# -*- coding: utf-8 -*-
"""packageId -> 工坊ID：工坊中文包池 token 级匹配（含停用词表 + 汉化包优先级）"""
import json, io, re, html
from difflib import SequenceMatcher

COLL = r"C:\SteamCMDData\pool-zh.json"
MISS = r"C:\SteamCMDData\rmk-miss.txt"

coll = json.load(io.open(COLL, encoding="utf-8"))
miss = [l.strip() for l in io.open(MISS, encoding="utf-8") if l.strip()]

ZH_MARK = re.compile(r"(zh[-_ ]?pack|_zh\b|\bzh\b|汉化包|汉化补丁|汉化|中文汉化|简&?繁中文|简繁中文|中文翻譯|中文翻译|中文化|中文|chinese|translation|汉化整合版|补丁)", re.I)
CJK = re.compile(u"[\u4e00-\u9fff]")
PREFIX = re.compile(r"^(zh|rwzh|chinesepack|chinesetranslation|cn|chs|zhongwen|vanillaexpanded|vanillaquestsexpanded)[.\-_]", re.I)
SUFFIX = re.compile(r"[.\-_](zh|zht|zhtc|chs|cn|zhpatch|zhpack|hc|xt|93|chinese)([.\-_].*)?$", re.I)
PID_ZH = re.compile(r"^(zh|rwzh|chinesepack|chinesetranslation|cn|chs)[.\-_]|[.\-_](zh|zht|zhtc|chs|zhpatch|zhpack)$", re.I)
STOP = set("""rimworld framework core expanded vanilla faction factions translation chinese patch mod pack
continued series zh zht zhtc chinese cn chs patch pack medieval overhaul""".split())


def norm(s):
    s = html.unescape(s)
    s = re.sub(u"【[^】]*】", "", s)
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]", "", s.lower())


def toks(s):
    return [t for t in re.split(r"[^a-z0-9\u4e00-\u9fff]+", html.unescape(s).lower()) if t]


titles = []
for wid, t in coll.items():
    t2 = re.sub(u"【[^】]*】", "", html.unescape(t))
    base = ZH_MARK.split(t2)[0]
    base = re.sub(r"[\s\-_&]+$", "", base).strip()
    nbase = norm(base)
    tk = [x for x in toks(base) if len(x) >= 6 and x not in STOP]
    is_zht = bool(ZH_MARK.search(t2)) or bool(CJK.search(t2))
    if nbase:
        titles.append((wid, t, base, nbase, tk, is_zht))


def body_parts(pid):
    b = pid
    for _ in range(3):
        nb = PREFIX.sub("", b)
        if nb == b:
            break
        b = nb
    for _ in range(3):
        nb = SUFFIX.sub("", b)
        if nb == b:
            break
        b = nb
    return [p for p in re.split(r"[.\-_]", b) if p]


def score_one(pid, nbase, tk):
    parts = body_parts(pid)
    npkg = norm("".join(parts))
    npkg2 = norm("".join(parts[1:])) if len(parts) > 1 else ""
    ptk = [p for p in parts if len(p) >= 6 and p not in STOP]
    if npkg and npkg == nbase:
        return (100, "全等")
    if npkg2 and npkg2 == nbase:
        return (98, "去作者段全等")
    if ptk and any(p == x for p in ptk for x in tk):
        m = [p for p in ptk for x in tk if p == x]
        return (90 + min(len(m), 3), "token全等:" + m[0])
    m_tk = sorted([x for x in tk if x in npkg], key=len)
    if m_tk:
        return (80 + min(len(m_tk), 4) * 2, "标题token∈包名:" + m_tk[-1])
    m_ptk = sorted([p for p in ptk if p in nbase], key=len)
    if m_ptk:
        return (78 + min(len(m_ptk), 4) * 2, "包名token∈标题:" + m_ptk[-1])
    r = SequenceMatcher(None, npkg, nbase).ratio() if npkg and nbase else 0
    if r >= 0.62:
        return (68, "相似度%.2f" % r)
    return None


rows = []
for pid in miss:
    if pid.lower().startswith("ludeon.rimworld"):
        rows.append((pid, None, [], "官方本体/DLC"))
        continue
    hits = []
    for wid, t, base, nbase, tk, is_zht in titles:
        r = score_one(pid, nbase, tk)
        if r:
            sc = r[0]
            if PID_ZH.search(pid) and is_zht:
                sc += 12
            hits.append((sc, r[1], wid, t, nbase))
    # 同分时优先「标题更短」（更接近精确命中，避免 Hospital 被 Hospital Extended 抢走）
    hits.sort(key=lambda x: (-x[0], len(x[4])))
    hits = [h[:4] for h in hits]
    rows.append((pid, hits[0] if hits else None, hits[1:4], ""))

hi = [r for r in rows if r[1] and r[1][0] >= 88]
md = [r for r in rows if r[1] and 78 <= r[1][0] < 88]
lo = [r for r in rows if r[1] and r[1][0] < 78]
no = [r for r in rows if not r[1]]
print("未解析 %d -> 高 %d / 中 %d / 低 %d / 无 %d" % (len(miss), len(hi), len(md), len(lo), len(no)))
print("--- rwzh / zh. 抽样 ---")
for pid, top, alts, _ in rows:
    if (pid.startswith("rwzh.") or pid.startswith("zh.")) and top:
        print("%-44s %3d %-20s -> %-12s %s" % (pid, top[0], top[1], top[2], top[3]))

json.dump([{"pid": p,
            "top": ({"score": t[0], "why": t[1], "wid": t[2], "title": t[3]} if t else None),
            "alts": [{"score": a[0], "why": a[1], "wid": a[2], "title": a[3]} for a in alts],
            "note": n}
           for p, t, alts, n in rows],
          io.open(r"C:\SteamCMDData\zh-match5.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
