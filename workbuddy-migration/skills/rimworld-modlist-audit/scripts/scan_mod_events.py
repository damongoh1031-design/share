# -*- coding: utf-8 -*-
"""按 packageId→GitHub 仓库，扫描模组源码里新增的 Def（重点：事件 IncidentDef）。

用法:
  python scan_mod_events.py <repos.txt> <out.json>
  repos.txt 每行: <packageId> <owner/repo>     （# 开头为注释）

输出 out.json: 每个仓库一条记录，含
  def_counts            各 Def 类型的数量
  incidents             新增 IncidentDef（defName / category（已按 ParentName 继承）/ workerClass）
  storyteller_bindings  该 mod 的 StorytellerDef 里绑定了哪些 category / incident
  quests / scenparts / gameconditions / patch_incident_targets

为什么不用 GitHub API：
  匿名 API 配额只有 60 次/小时，扫几十个仓库立刻耗尽。
  改用 codeload.github.com 的 tarball（不受该配额限制），tar 流式只抽 Defs/ 与 Patches/。

两个必须处理的坑（否则统计会错）：
  1. ParentName 继承 —— 子 Def 常常不写 category，靠抽象父 Def 继承。
     不递归会把原版疾病类事件误判成"无 category"。
  2. 版本目录 + 重复 defName —— 仓库里常有 1.4/1.5/1.6 并列目录，
     同一个 defName 出现多次。必须只保留 1.6（或仓库无版本目录时全保留）并按 defName 去重。
     实测：RWoM 不做这两步会把 10 个事件虚报成 48 个。
"""
import io
import json
import re
import sys
import tarfile
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

REPOS = sys.argv[1]
OUTJSON = sys.argv[2]
BRANCHES = ("master", "main")
UA = {"User-Agent": "Mozilla/5.0"}

# 关心细节的 Def 类型；其余只计数
DETAIL_TYPES = ("IncidentDef", "StorytellerDef", "QuestScriptDef", "ScenPartDef",
                "GameConditionDef", "IncidentCategoryDef")


def strip_ns(t):
    return t.split("}")[-1] if "}" in t else t


def fetch(repo):
    for br in BRANCHES:
        url = "https://codeload.github.com/%s/tar.gz/refs/heads/%s" % (repo, br)
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
            if len(data) > 2000:
                return data, br
        except Exception:
            pass
    return None, None


def version_segments(rel):
    return {s for s in rel.split("/") if re.match(r"^\d+\.\d+$", s)}


def extract_xml(data):
    raw = []
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        for m in tf.getmembers():
            if not m.isfile() or not m.name.lower().endswith(".xml"):
                continue
            parts = m.name.split("/")[1:]      # 去掉顶层 repo-branch 目录
            if not parts:
                continue
            rel = "/".join(parts)
            low = "/" + rel.lower()
            if "/defs/" not in low and "/patches/" not in low:
                continue
            f = tf.extractfile(m)
            if f is None:
                continue
            try:
                raw.append((rel, f.read().decode("utf-8", "replace")))
            except Exception:
                pass
    allvers = set()
    for r, _ in raw:
        allvers |= version_segments(r)
    if "1.6" in allvers:
        raw = [(r, t) for r, t in raw
               if (not version_segments(r)) or ("1.6" in version_segments(r))]
    return raw


def parse(text):
    try:
        return ET.fromstring(text.lstrip("\ufeff \t\r\n"))
    except ET.ParseError:
        return None


def scan(files):
    inc, inc_order = {}, []
    st_bind, quests, scenparts, conds, patch_inc = [], [], [], [], []
    counts = Counter()

    for rel, txt in files:
        root = parse(txt)
        if root is None:
            continue
        tag = strip_ns(root.tag)
        if tag == "Defs":
            for d in root:
                dt = strip_ns(d.tag)
                counts[dt] += 1
                if dt == "IncidentDef":
                    key = d.get("Name") or d.findtext("defName")
                    if not key:
                        continue
                    inc[key] = {"defName": d.findtext("defName"), "cat": d.findtext("category"),
                                "worker": d.findtext("workerClass"), "parent": d.get("ParentName"),
                                "abstract": (d.get("Abstract") == "True"), "src": rel}
                    inc_order.append(key)
                elif dt == "StorytellerDef":
                    sd = d.findtext("defName") or d.get("Name") or "?"
                    for li in d.iter():
                        if strip_ns(li.tag) != "li":
                            continue
                        if li.findtext("category"):
                            st_bind.append((sd, "category", li.findtext("category")))
                        if li.findtext("incident"):
                            st_bind.append((sd, "incident", li.findtext("incident")))
                elif dt == "QuestScriptDef":
                    q = d.findtext("defName")
                    if q:
                        quests.append(q)
                elif dt == "ScenPartDef":
                    sp, cls = d.findtext("defName"), (d.findtext("scenPartClass") or "")
                    if sp and ("Incident" in cls or "Incident" in sp):
                        scenparts.append((sp, cls))
                elif dt == "GameConditionDef":
                    g = d.findtext("defName")
                    if g:
                        conds.append(g)
        elif tag == "Patch":
            # 注意：PatchOperationAdd 的 xpath 目标是字符串，这里只能抓到内联写法的 defName
            for el in root.iter():
                if strip_ns(el.tag) == "IncidentDef":
                    nm = el.findtext("defName")
                    if nm:
                        patch_inc.append(nm)

    def eff_cat(d, seen=None):
        seen = seen or set()
        if d.get("cat"):
            return d["cat"]
        p = d.get("parent")
        if p and p in inc and p not in seen:
            seen.add(p)
            return eff_cat(inc[p], seen)
        return None

    real, seen_dn = [], set()
    for k in inc_order:
        d = inc[k]
        if not d.get("defName") or d.get("abstract") or d["defName"] in seen_dn:
            continue
        seen_dn.add(d["defName"])
        real.append({"defName": d["defName"], "category": eff_cat(d),
                     "workerClass": d["worker"], "src": d["src"]})
    return (real, st_bind, sorted(set(quests)), scenparts,
            sorted(set(conds)), sorted(set(patch_inc)), dict(counts))


def main():
    out = []
    for line in open(REPOS, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        pid, repo = line.split()[0], line.split()[1]
        print("[*]", pid, repo, flush=True)
        data, br = fetch(repo)
        if data is None:
            out.append({"packageId": pid, "repo": repo, "status": "FETCH_FAIL"})
            print("    !! fail", flush=True)
            continue
        real, st, q, sp, gc, pt, cnt = scan(extract_xml(data))
        out.append({"packageId": pid, "repo": repo, "status": "OK", "branch": br,
                    "def_counts": cnt, "incidents": real, "storyteller_bindings": st,
                    "quests": q, "scenparts": sp, "gameconditions": gc,
                    "patch_incident_targets": pt})
        print("    incidents=%d storyteller_binds=%d quests=%d" % (len(real), len(st), len(q)), flush=True)
        del data
    json.dump(out, open(OUTJSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("written", OUTJSON)


if __name__ == "__main__":
    main()
