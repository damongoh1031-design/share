# -*- coding: utf-8 -*-
"""两份 RimWorld ModsConfig.xml 差异对比 + 名称解析。

用法：
  python diff_modlists.py <A.xml> <B.xml>

输出：
  1. 规模/版本/DLC 画像
  2. 仅 A / 仅 B 的条目（带模组名，来自 RimSort 社区库）
  3. 两侧各自的「汉化包空转」检测（汉化在，本体不在）
"""
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict

A = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Admin\Downloads\ce0906.xml"
B = sys.argv[2] if len(sys.argv) > 2 else r"C:\Users\Admin\Downloads\Medieval.xml"
DB = os.path.join(os.environ.get("TEMP", "/tmp"), "steamDB.json")
DB_URL = "https://raw.githubusercontent.com/RimSort/Steam-Workshop-Database/main/steamDB.json"

# 汉化包 packageId 的常见前缀/特征（用于空转检测）
TRANS_PREFIX = ("zh.", "rwzh.", "chinesepack", "cc.chinese", "shavius.", "momanacha.",
                "qulee.", "suiyu.", "soulwolf.", "lemontea.", "maiya.", "openclaw.",
                "jueying.", "shouer.", "diyshanliu.", "holarula.", "azrazalea.",
                "gousheng.", "wlk.", "laiguai.", "xxfq007.", "qa.")
TRANS_SUFFIX = (".zh", ".zht", ".zh.hc", ".chs", ".chinese", ".zhmiz", ".mizzh",
                ".zhtc", ".zhpatch", ".expansioncn", ".chinese")


def ensure_db():
    if os.path.exists(DB) and os.path.getsize(DB) > 10_000_000:
        return
    print("[*] 下载 RimSort 社区工坊数据库 ...", file=sys.stderr)
    urllib.request.urlretrieve(DB_URL, DB)


def is_translation(pid):
    p = pid.lower()
    return p.startswith(TRANS_PREFIX) or p.endswith(TRANS_SUFFIX)


def main():
    ensure_db()
    d = json.load(open(DB, encoding="utf-8"))["database"]
    by_pid = defaultdict(list)
    for wid, e in d.items():
        if not isinstance(e, dict):
            continue
        pid = e.get("packageId") or e.get("packageid")
        if pid:
            by_pid[str(pid).lower()].append((str(wid), e))

    def pick(pid):
        lst = by_pid.get(pid.lower())
        if not lst:
            return None
        for wid, e in lst:
            if "1.6" in (e.get("gameVersions") or []):
                return e
        return lst[0][1]

    def name(pid):
        e = pick(pid)
        return (e.get("name") if e else None) or "--未收录--"

    def load(p):
        raw = open(p, encoding="utf-8").read()
        r = ET.fromstring(raw)
        mods = [x.text.strip() for x in r.find("activeMods").findall("li")]
        exp = [x.text.strip() for x in r.find("knownExpansions").findall("li")]
        ver = (r.findtext("version") or "?").strip()
        return mods, exp, ver

    a, ea, va = load(A)
    b, eb, vb = load(B)
    sa, sb = set(a), set(b)

    print("=" * 78)
    print("画像")
    print("=" * 78)
    print("  A %-40s 版本 %-20s %d mods / %d DLC" % (os.path.basename(A), va, len(a), len(ea)))
    print("  B %-40s 版本 %-20s %d mods / %d DLC" % (os.path.basename(B), vb, len(b), len(eb)))
    print("  DLC 是否一致:", "是" if sorted(ea) == sorted(eb) else "否  A=%s B=%s" % (ea, eb))
    print("  交集 %d / 仅A %d / 仅B %d" % (len(sa & sb), len(sa - sb), len(sb - sa)))

    only_a = [m for m in a if m not in sb]
    only_b = [m for m in b if m not in sa]
    for tag, lst in (("仅 A 有", only_a), ("仅 B 有", only_b)):
        print()
        print("=" * 78)
        print("%s（%d 个）" % (tag, len(lst)))
        print("=" * 78)
        for m in lst:
            mark = "  [汉化]" if is_translation(m) else ""
            print("  %-52s %s%s" % (m, name(m), mark))

    # 汉化空转：汉化在，但同名"本体"在对面清单里
    print()
    print("=" * 78)
    print("汉化包空转检测（汉化在 B，但其疑似本体只在 A）")
    print("=" * 78)
    hit = 0
    for m in b:
        if not is_translation(m):
            continue
        # 去掉汉化前后缀，做前缀匹配找本体
        stem = re.sub(r"\.(zh|zht|chs|chinese|zhmiz|mizzh|zhtc|zh\.hc|zhpatch)$", "", m.lower())
        stem = re.sub(r"^(zh|rwzh|chinesepack|cc\.chinese|shavius|qulee|suiyu|soulwolf|lemontea|momanacha|wlk|laiguai|xxfq007)\.", "", stem)
        cands = [x for x in only_a if x.lower() == stem or stem.endswith("." + x.lower()) or x.lower().endswith("." + stem)]
        if cands:
            hit += 1
            print("  !! %s  ->  疑似本体 %s（%s）" % (m, cands[0], name(cands[0])))
    if not hit:
        print("  （未发现）")
    print()
    print("  ⚠️ 启发式结果，需人工确认：部分「汉化」包实为「本体+汉化」合并包。")


if __name__ == "__main__":
    main()
