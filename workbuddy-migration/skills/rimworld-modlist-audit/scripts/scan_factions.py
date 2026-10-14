# -*- coding: utf-8 -*-
"""
scan_factions.py — 派系专项扫描器

对每个「派系模组」仓库下载 tarball（不走 GitHub API，避免 60/h 配额），
只抽取 Defs/ 与 Patches/ 下的 XML，输出：

  1. factions      : 每个 FactionDef 的**完整原始 XML 块**（含全部字段）
  2. incidents     : IncidentDef（defName/category/workerClass + 是否引用本模组派系）
  3. quests        : QuestScriptDef defName
  4. scenparts     : ScenPartDef / GameConditionDef
  5. code          : 所有 .cs 文件名（用于判断独特机制）
  6. patches       : PatchOperation 目标（Patch 了哪些 FactionDef）
  7. comps         : FactionDef 里出现的 Comp / 自定义 compClass

用法：
  python scan_factions.py <repos.txt> <out.json> [--jobs N]

repos.txt 每行:  <packageId> <owner/repo>
"""
import io, json, os, re, sys, tarfile, urllib.request, zipfile
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "Mozilla/5.0"}
TARBALL = "https://codeload.github.com/{repo}/tar.gz/refs/heads/{br}"


def fetch(repo):
    """返回 (branch, bytes) 或 (None, None)。先 master 再 main。"""
    for br in ("master", "main"):
        try:
            req = urllib.request.Request(TARBALL.format(repo=repo, br=br), headers=UA)
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
            if len(data) > 2000:
                return br, data
        except Exception:
            continue
    return None, None


def version_segments(rel):
    return {s for s in rel.split("/") if re.match(r"^\d+\.\d+$", s)}


def iter_members(data):
    """yield (relpath, bytes) for XML/C# files"""
    try:
        tf = tarfile.open(fileobj=io.BytesIO(data), mode="r:gz")
    except Exception:
        return
    root = None
    for m in tf.getmembers():
        if root is None and "/" in m.name:
            root = m.name.split("/")[0]
        if not m.isfile():
            continue
        rel = m.name.split("/", 1)[1] if "/" in m.name else m.name
        yield rel, m


def pick_version(files, want="1.6"):
    """files: list of (rel, bytes).
    优先保留 want 版本目录 + 无版本目录的文件；
    若仓库没有 want 版本（源码滞后），退化为**最高可用版本**，避免把 1.2/1.3/1.4 全混进来重复计数。"""
    allvers = set()
    for rel, _ in files:
        allvers |= version_segments(rel)
    if not allvers:
        return files, None
    if want in allvers:
        chosen = want
    else:
        def key(v):
            try:
                return tuple(int(x) for x in v.split("."))
            except Exception:
                return (0, 0)
        chosen = max(sorted(allvers), key=key)
    out = []
    for rel, b in files:
        vs = version_segments(rel)
        if (not vs) or (chosen in vs):
            out.append((rel, b))
    return out, chosen


def scan_repo(pkg, repo):
    br, data = fetch(repo)
    res = {"packageId": pkg, "repo": repo, "status": "FAIL", "branch": None,
           "factions": [], "incidents": [], "quests": [], "scenparts": [],
           "gameconditions": [], "code": [], "patch_targets": [],
           "faction_comps": [], "files_xml": 0, "version_used": None}
    if not data:
        return res
    res["branch"] = br
    xmls, csharp = [], []
    tf = tarfile.open(fileobj=io.BytesIO(data), mode="r:gz")
    for m in tf.getmembers():
        if not m.isfile():
            continue
        rel = m.name.split("/", 1)[1] if "/" in m.name else m.name
        low = rel.lower()
        if low.endswith(".cs"):
            csharp.append(rel)
        elif low.endswith(".xml") and ("/defs/" in "/" + low or "/patches/" in "/" + low
                                       or low.startswith("defs/") or low.startswith("patches/")):
            try:
                xmls.append((rel, tf.extractfile(m).read()))
            except Exception:
                pass
    xmls, chosen = pick_version(xmls)
    res["files_xml"] = len(xmls)
    res["version_used"] = chosen
    res["code"] = sorted(set(os.path.basename(c) for c in csharp))

    def txt(b):
        return b.decode("utf-8", "ignore")

    def blocks(t, tag):
        """返回 <tag>...</tag> 的原始块列表（非贪婪，支持嵌套一层）"""
        out = []
        for m in re.finditer(r"<%s\b[^>]*>(.*?)</%s>" % (tag, tag), t, re.S):
            out.append(m.group(0))
        return out

    seen = set()
    for rel, b in xmls:
        t = txt(b)
        # 1) FactionDef 完整块
        for blk in blocks(t, "FactionDef"):
            dn = re.search(r"<defName>([^<]+)</defName>", blk)
            key = dn.group(1) if dn else blk[:80]
            if key in seen:
                continue
            seen.add(key)
            res["factions"].append({"defName": key, "src": rel, "xml": blk})
            for cm in re.finditer(r"<li\s+Class=\"([^\"]+)\"", blk):
                res["faction_comps"].append({"faction": key, "comp": cm.group(1)})
        # 2) IncidentDef
        for blk in blocks(t, "IncidentDef"):
            dn = re.search(r"<defName>([^<]+)</defName>", blk)
            cat = re.search(r"<category>([^<]+)</category>", blk)
            wc = re.search(r"<workerClass>([^<]+)</workerClass>", blk)
            bc = re.search(r"<baseChance>([^<]+)</baseChance>", blk)
            res["incidents"].append({
                "defName": dn.group(1) if dn else "?", "src": rel,
                "category": cat.group(1) if cat else None,
                "workerClass": wc.group(1) if wc else None,
                "baseChance": bc.group(1) if bc else None,
            })
        # 3) QuestScriptDef
        for blk in blocks(t, "QuestScriptDef"):
            dn = re.search(r"<defName>([^<]+)</defName>", blk)
            if dn:
                res["quests"].append({"defName": dn.group(1), "src": rel})
        # 4) ScenPartDef / GameConditionDef
        for blk in blocks(t, "ScenPartDef"):
            dn = re.search(r"<defName>([^<]+)</defName>", blk)
            if dn:
                res["scenparts"].append({"defName": dn.group(1), "src": rel})
        for blk in blocks(t, "GameConditionDef"):
            dn = re.search(r"<defName>([^<]+)</defName>", blk)
            if dn:
                res["gameconditions"].append({"defName": dn.group(1), "src": rel})
        # 5) Patch 目标
        for m in re.finditer(r"<xpath>([^<]*FactionDef[^<]*)</xpath>", t):
            res["patch_targets"].append({"xpath": m.group(1).strip(), "src": rel})
        for m in re.finditer(r"<match\s+name=\"defName\"[^>]*>([^<]+)</match>", t):
            res["patch_targets"].append({"match_defName": m.group(1), "src": rel})

    # 去重
    for k in ("quests", "scenparts", "gameconditions"):
        seen2 = set()
        out = []
        for x in res[k]:
            if x["defName"] in seen2:
                continue
            seen2.add(x["defName"])
            out.append(x)
        res[k] = out
    res["status"] = "OK"
    return res


def main():
    src, outp = sys.argv[1], sys.argv[2]
    jobs = 6
    if "--jobs" in sys.argv:
        jobs = int(sys.argv[sys.argv.index("--jobs") + 1])
    pairs = []
    for line in open(src, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            pairs.append((parts[0], parts[1]))
    out = []
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        for r in ex.map(lambda p: scan_repo(*p), pairs):
            out.append(r)
            print(f"[{r['status']}] {r['packageId']:42s} factions={len(r['factions']):2d} "
                  f"inc={len(r['incidents']):3d} q={len(r['quests']):3d} cs={len(r['code']):3d}",
                  flush=True)
    json.dump(out, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("WROTE", outp)


if __name__ == "__main__":
    main()
