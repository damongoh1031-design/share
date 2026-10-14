# -*- coding: utf-8 -*-
"""聚合 scanA_all.json / scanB_all.json -> 对比数据 agg.json"""
import json, sys
from collections import Counter, defaultdict

A = json.load(open(sys.argv[1], encoding="utf-8"))
B = json.load(open(sys.argv[2], encoding="utf-8"))
OUT = sys.argv[3]
VAN_WORKERS = set(json.load(open("vanilla_workers.json", encoding="utf-8")))
VAN_CORE = json.load(open("vanilla_core.json", encoding="utf-8"))
VAN_CATS = set(VAN_CORE["categories"]) | {"AllyAssistance", "RaidBeacon", "WorldQuest"}


def short(cls):
    return cls.split(".")[-1] if cls else ""


def is_custom_worker(w):
    if not w:
        return None
    return short(w) not in VAN_WORKERS


def is_custom_cat(c):
    if not c:
        return None
    return c not in VAN_CATS


def load(rows):
    inc = {}
    by_pid = defaultdict(list)
    st_defs, st_comps, cats = [], [], {}
    scen, quests, gc, patch = [], [], [], []
    cs = Counter()
    ok, fail = [], []
    for r in rows:
        if r.get("status") != "OK":
            fail.append((r["packageId"], r.get("repo"), r.get("status")))
            continue
        ok.append((r["packageId"], r["repo"], r.get("version_used")))
        for e in r.get("incidents", []):
            dn = e["defName"]
            if dn in inc:
                continue
            e2 = dict(e)
            e2["pid"] = r["packageId"]
            e2["repo"] = r["repo"]
            e2["customWorker"] = is_custom_worker(e.get("workerClass"))
            e2["customCat"] = is_custom_cat(e.get("category"))
            inc[dn] = e2
            by_pid[r["packageId"]].append(dn)
        for s in r.get("storyteller_defs", []):
            st_defs.append((r["packageId"], s))
        for c in r.get("storyteller_comps", []):
            c2 = dict(c)
            c2["pid"] = r["packageId"]
            st_comps.append(c2)
        for k in (r.get("incident_categories") or {}):
            cats.setdefault(k, []).append(r["packageId"])
        for s in r.get("scenparts", []):
            scen.append((r["packageId"], s["defName"], s["class"]))
        for q in r.get("quests", []):
            quests.append((r["packageId"], q))
        for g in r.get("gameconditions", []):
            gc.append((r["packageId"], g))
        for p in r.get("patch_incident_defs", []):
            patch.append((r["packageId"], p))
        for k, v in (r.get("cs_hits") or {}).items():
            cs[k] += v
    return dict(inc=inc, by_pid=by_pid, st_defs=st_defs, st_comps=st_comps, cats=cats,
                scen=scen, quests=quests, gc=gc, patch=patch, cs=cs, ok=ok, fail=fail)


def summarize(D, label):
    inc = D["inc"]
    cat = Counter((e.get("category") or "(未声明)") for e in inc.values())
    zero = sorted(d for d, e in inc.items()
                  if (e.get("baseChance") or "").strip() in ("0", "0.0", ".0", "0.00"))
    custom_w = {d: e["workerClass"] for d, e in inc.items() if e.get("customWorker") is True}
    van_w = {d: e["workerClass"] for d, e in inc.items() if e.get("customWorker") is False}
    now = [d for d, e in inc.items() if not e.get("workerClass")]
    custom_c = {d: e["category"] for d, e in inc.items() if e.get("customCat") is True}
    hidden = [d for d, e in inc.items() if (e.get("hidden") or "").lower() == "true"]
    print("=" * 78)
    print(label)
    print("  已核实仓库 %d（失败 %d）" % (len(D["ok"]), len(D["fail"])))
    print("  非原版事件 defName 去重 %d" % len(inc))
    print("  分类: %s" % dict(cat.most_common()))
    print("  baseChance=0 : %d" % len(zero))
    print("  自定义 workerClass : %d / 复用原版 worker : %d / 未声明 : %d"
          % (len(custom_w), len(van_w), len(now)))
    print("  复用原版 worker 的明细: %s" % sorted(van_w))
    print("  自定义 category : %s" % sorted(set(custom_c.values())))
    print("  hidden=true : %d" % len(hidden))
    print("  模组新增 StorytellerDef: %s" % sorted(set(s for _, s in D["st_defs"])))
    print("  模组新增 IncidentCategoryDef: %s" % sorted(D["cats"]))
    print("  StorytellerComp 条目 %d / ScenPart %d / QuestScript %d / GameCondition %d"
          % (len(D["st_comps"]), len(D["scen"]), len(D["quests"]), len(D["gc"])))
    print("  C#: %s" % dict(D["cs"].most_common()))
    print("  按模组: %s" % dict(sorted(((k, len(v)) for k, v in D["by_pid"].items()),
                                      key=lambda x: -x[1])[:22]))
    return dict(inc=inc, cat=cat, zero=zero, custom_w=custom_w, van_w=van_w, now=now,
                custom_c=custom_c, hidden=hidden)


da, db = load(A), load(B)
sa = summarize(da, "A · ce0906.xml")
sb = summarize(db, "B · Medieval.xml")

ia, ib = set(sa["inc"]), set(sb["inc"])
both, onlyA, onlyB = ia & ib, ia - ib, ib - ia
print("=" * 78)
print("A 独有 %d / B 独有 %d / 共有 %d" % (len(onlyA), len(onlyB), len(both)))

# 按来源模组列事件
def by_mod(inc):
    m = defaultdict(list)
    for d, e in inc.items():
        m[e["pid"]].append(d)
    return {k: sorted(v) for k, v in sorted(m.items(), key=lambda x: -len(x[1]))}


out = {}
for tag, D, S in (("A", da, sa), ("B", db, sb)):
    out[tag] = {
        "covered": [{"pid": p, "repo": r, "version": v} for p, r, v in D["ok"]],
        "fail": D["fail"],
        "incidentCount": len(S["inc"]),
        "incidents": S["inc"],
        "categories": dict(S["cat"]),
        "zeroChance": S["zero"],
        "customWorker": S["custom_w"],
        "vanillaWorker": S["van_w"],
        "noWorker": S["now"],
        "customCategory": S["custom_c"],
        "hidden": S["hidden"],
        "storyteller_defs": sorted(set(s for _, s in D["st_defs"])),
        "storyteller_comps": D["st_comps"],
        "incident_categories": sorted(D["cats"]),
        "scenparts": D["scen"],
        "quests": D["quests"],
        "gameconditions": D["gc"],
        "cs_hits": dict(D["cs"]),
        "by_mod": by_mod(S["inc"]),
    }
out["onlyA"] = sorted(onlyA)
out["onlyB"] = sorted(onlyB)
out["both"] = sorted(both)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("written", OUT)
