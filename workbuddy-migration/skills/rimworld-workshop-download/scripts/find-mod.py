# -*- coding: utf-8 -*-
"""按关键词定位 mod 目录与源码。

用法:
    python find-mod.py <关键词>            # 模糊搜索工坊ID/packageId/名称
    python find-mod.py --src <关键词>      # 只看带 C# 源码的
    python find-mod.py --list              # 列出全部（简表）

示例:
    python find-mod.py ratkin
    python find-mod.py --src medieval
    python find-mod.py vanillaexpanded.vfesecurity
"""
import os, sys, io, json, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
IDX = r"C:\SteamCMDData\source-index.json"
rows = json.load(open(IDX, encoding="utf-8"))
# 列: 0工坊ID 1名称 2packageId 3命中pid 4源码目录 5cs数 6dll 7dll数 8版本 9大小MB

args = sys.argv[1:]
only_src = "--src" in args
args = [a for a in args if a != "--src"]

if "--list" in args or not args:
    print("%-12s %-42s %-6s %s" % ("工坊ID", "名称", "cs数", "packageId"))
    for r in rows:
        print("%-12s %-42s %-6s %s" % (r[0], r[1][:40], r[5] or "-", r[2][:60]))
    sys.exit(0)

kw = " ".join(args).lower()
hits = []
for r in rows:
    blob = " ".join(str(x) for x in r[:5]).lower()
    if kw in blob or all(w in blob for w in kw.split()):
        if only_src and not r[4]:
            continue
        hits.append(r)

if not hits:
    print("未找到匹配:", kw)
    sys.exit(1)

print("命中 %d 个:\n" % len(hits))
for r in hits:
    print("─" * 70)
    print("  工坊ID   :", r[0])
    print("  名称     :", r[1])
    print("  packageId:", r[2])
    print("  支持版本 :", r[8] or "(未标注)")
    print("  大小     :", r[9], "MB")
    print("  mod 目录 :", os.path.join(
        r"C:\SteamCMDData\steam\steamapps\workshop\content\294100", r[0]))
    if r[4]:
        print("  ★ 源码   :", r[4], "(%s 个 .cs)" % r[5])
    else:
        print("  ★ 源码   : 无（mod 未附带 C# 源码）")
    if r[6]:
        print("  程序集   :", r[6], "(%s 个 dll)" % r[7])
