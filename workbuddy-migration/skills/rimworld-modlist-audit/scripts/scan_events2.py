# -*- coding: utf-8 -*-
"""扫模组源码：提取 IncidentDef 全字段 + StorytellerDef/IncidentCategoryDef/ScenPartDef/QuestScriptDef
+ Patches 目标 + C# 侧事件类（IncidentWorker / StorytellerComp / LordJob / QuestNode 等）。

用法: python scan_events2.py <modlist.xml> <map.json> <out.json>
  modlist.xml : ModsConfig.xml，取 <activeMods>
  map.json    : {packageId: "owner/repo"} 或 {packageId: {"repo": "...", "name": "..."}}
  out.json    : 每个 packageId 一条记录
"""
import io, json, re, sys, tarfile, urllib.request
import xml.etree.ElementTree as ET
from collections import Counter

MODLIST, MAPJSON, OUTJSON = sys.argv[1], sys.argv[2], sys.argv[3]
BRANCHES = ("master", "main")
UA = {"User-Agent": "Mozilla/5.0"}

# IncidentDef 全字段（原版 1.6 IncidentDef 的公开字段）
INC_FIELDS = ("category", "baseChance", "mtbDays", "minThreatPoints", "earliestDay",
              "minPopulation", "minRefireDays", "minDifficulty", "pointsScaleable",
              "hidden", "targetTags", "letterLabel", "letterText", "dialogText",
              "chanceFactor", "populationEffect", "targetsWholeMap", "workerClass",
              "tale", "diseaseIncident", "allowBeforeMinDays", "maxThreatPoints")

# C# 侧关心的基类
CS_KINDS = {
    "IncidentWorker": r"class\s+\w+\s*:\s*IncidentWorker",
    "StorytellerComp": r"class\s+\w+\s*:\s*StorytellerComp",
    "StorytellerCompProperties": r"class\s+\w+\s*:\s*StorytellerCompProperties",
    "QuestNode": r"class\s+\w+\s*:\s*QuestNode",
    "ScenPart": r"class\s+\w+\s*:\s*ScenPart",
    "GameCondition": r"class\s+\w+\s*:\s*GameCondition",
    "RaidStrategyWorker": r"class\s+\w+\s*:\s*RaidStrategyWorker",
    "LordJob": r"class\s+\w+\s*:\s*LordJob",
    "HarmonyPatch": r"\[HarmonyPatch",
    "forced": r"\.forced\s*=\s*true",
}


def strip_ns(t):
    return t.split("}")[-1] if "}" in t else t


def fetch(repo):
    for br in BRANCHES:
        url = "https://codeload.github.com/%s/tar.gz/refs/heads/%s" % (repo, br)
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=300) as r:
                data = r.read()
            if len(data) > 2000:
                return data, br
        except Exception:
            pass
    return None, None


def ver_segs(rel):
    return {s for s in rel.split("/") if re.match(r"^\d+\.\d+$", s)}


def collect(data):
    """返回 (xml_files, cs_files) —— xml_files: [(rel, text)]；cs_files: [(rel, text)]"""
    xmls, css = [], []
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        for m in tf.getmembers():
            if not m.isfile():
                continue
            low = m.name.lower()
            isxml = low.endswith(".xml")
            iscs = low.endswith(".cs")
            if not (isxml or iscs):
                continue
            parts = m.name.split("/")[1:]
            if not parts:
                continue
            rel = "/".join(parts)
            rl = "/" + rel.lower()
            if isxml:
                if "/defs/" not in rl and "/patches/" not in rl:
                    continue
            else:
                if "/source/" not in rl:
                    continue
            f = tf.extractfile(m)
            if f is None:
                continue
            try:
                txt = f.read().decode("utf-8", "replace")
            except Exception:
                continue
            (xmls if isxml else css).append((rel, txt))
    # 版本目录过滤：有 1.6 就只留 1.6（含无版本目录的文件）
    allv = set()
    for r, _ in xmls + css:
        allv |= ver_segs(r)
    if "1.6" in allv:
        keep = lambda r: (not ver_segs(r)) or ("1.6" in ver_segs(r))
        xmls = [(r, t) for r, t in xmls if keep(r)]
        css = [(r, t) for r, t in css if keep(r)]
        return xmls, css, "1.6"
    hi = None
    if allv:
        hi = max(sorted(allv), key=lambda v: tuple(int(x) for x in v.split(".")))
    return xmls, css, hi or "none"


def parse(text):
    try:
        return ET.fromstring(text.lstrip("\ufeff \t\r\n"))
    except ET.ParseError:
        return None


def scan(xmls, css):
    inc = {}           # Name/defName -> dict
    inc_order = []
    cats, st_comps, st_defs = {}, [], []
    scenparts, quests, conds = [], [], []
    patch_targets = []          # Patches 里被改的 xpath / 内联 defName
    patch_incident = []
    counts = Counter()

    for rel, txt in xmls:
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
                    rec = {"defName": d.findtext("defName"), "parent": d.get("ParentName"),
                           "abstract": d.get("Abstract") == "True", "src": rel}
                    for f in INC_FIELDS:
                        v = d.findtext(f)
                        if v is not None:
                            rec[f] = v.strip()
                    inc[key] = rec
                    inc_order.append(key)
                elif dt == "IncidentCategoryDef":
                    n = d.findtext("defName")
                    if n:
                        cats[n] = {"needsParmsPoints": d.findtext("needsParmsPoints"),
                                   "src": rel}
                elif dt == "StorytellerDef":
                    sd = d.findtext("defName") or d.get("Name") or "?"
                    st_defs.append(sd)
                    for comp in d.iter():
                        ct = strip_ns(comp.tag)
                        if ct not in ("li", "compClass"):
                            continue
                        cls = comp.get("Class") or comp.findtext("Class")
                        if not cls:
                            continue
                        if "StorytellerComp" not in cls:
                            continue
                        item = {"storyteller": sd, "class": cls}
                        for f in ("category", "incident", "mtbDays", "onDays", "minDays",
                                  "maxDays", "repeatDays", "pointsFactor", "minThreatPoints"):
                            v = comp.findtext(f)
                            if v is not None:
                                item[f] = v.strip()
                        st_comps.append(item)
                elif dt == "ScenPartDef":
                    n, cls = d.findtext("defName"), (d.findtext("scenPartClass") or "")
                    if n:
                        scenparts.append({"defName": n, "class": cls, "src": rel})
                elif dt == "QuestScriptDef":
                    n = d.findtext("defName")
                    if n:
                        quests.append(n)
                elif dt == "GameConditionDef":
                    n = d.findtext("defName")
                    if n:
                        conds.append(n)
        elif tag == "Patch":
            for op in root.iter():
                ot = strip_ns(op.tag)
                if ot.startswith("PatchOperation") or ot == "Operation":
                    xp = op.findtext("xpath")
                    if xp:
                        patch_targets.append(xp.strip()[:180])
                if ot == "IncidentDef":
                    n = op.findtext("defName")
                    if n:
                        patch_incident.append(n)

    # category 继承
    def eff(d, key, seen=None):
        seen = seen or set()
        if d.get(key):
            return d[key]
        p = d.get("parent")
        if p and p in inc and p not in seen:
            seen.add(p)
            return eff(inc[p], key, seen)
        return None

    real, seen_dn = [], set()
    for k in inc_order:
        d = inc[k]
        if not d.get("defName") or d.get("abstract") or d["defName"] in seen_dn:
            continue
        seen_dn.add(d["defName"])
        out = {"defName": d["defName"], "src": d["src"]}
        for f in INC_FIELDS:
            v = d.get(f) or eff(d, f)
            if v is not None:
                out[f] = v
        real.append(out)

    # C# 侧
    cs_hits = Counter()
    cs_classes = {}
    for rel, txt in css:
        for kind, pat in CS_KINDS.items():
            n = len(re.findall(pat, txt))
            if n:
                cs_hits[kind] += n
                cs_classes.setdefault(kind, []).append(rel)
    return real, st_defs, st_comps, cats, scenparts, sorted(set(quests)), sorted(set(conds)), \
        sorted(set(patch_targets)), sorted(set(patch_incident)), dict(counts), dict(cs_hits), cs_classes


def active_mods(path):
    root = ET.parse(path).getroot()
    node = root.find("activeMods")
    src = node if node is not None else root
    return [e.text.strip() for e in src.iter("li") if e.text and e.text.strip()]


def main():
    pids = active_mods(MODLIST)
    raw = json.load(open(MAPJSON, encoding="utf-8"))
    m = {}
    for k, v in raw.items():
        m[k.lower()] = v["repo"] if isinstance(v, dict) else v
    out = []
    todo = [(p, m[p.lower()]) for p in pids if p.lower() in m]
    print("modlist=%d  mapped=%d" % (len(pids), len(todo)), flush=True)
    for pid, repo in todo:
        data, br = fetch(repo)
        if data is None:
            out.append({"packageId": pid, "repo": repo, "status": "FETCH_FAIL"})
            print("  !! %-45s %s" % (pid, repo), flush=True)
            continue
        xmls, css, used = collect(data)
        try:
            (inc, stdefs, stc, cats, sp, q, gc, pt, pi, cnt, csh, csc) = scan(xmls, css)
        except Exception as e:
            out.append({"packageId": pid, "repo": repo, "status": "SCAN_ERR", "err": str(e)[:200]})
            print("  EE %-45s %s" % (pid, str(e)[:60]), flush=True)
            del data
            continue
        out.append({"packageId": pid, "repo": repo, "status": "OK", "branch": br,
                    "version_used": used, "def_counts": cnt, "incidents": inc,
                    "storyteller_defs": stdefs, "storyteller_comps": stc,
                    "incident_categories": cats, "scenparts": sp, "quests": q,
                    "gameconditions": gc, "patch_targets": pt, "patch_incident_defs": pi,
                    "cs_hits": csh, "cs_files": {k: v[:6] for k, v in csc.items()}})
        print("  %-45s inc=%-3d stComp=%-2d cat=%-2d scen=%-2d quest=%-3d cs=%s"
              % (pid, len(inc), len(stc), len(cats), len(sp), len(q),
                 ",".join("%s%d" % (a[:9], b) for a, b in sorted(csh.items()))[:70]), flush=True)
        del data
    json.dump(out, open(OUTJSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("written", OUTJSON, len(out))


if __name__ == "__main__":
    main()
