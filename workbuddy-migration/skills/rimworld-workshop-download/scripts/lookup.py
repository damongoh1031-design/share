# -*- coding: utf-8 -*-
import json, io, sys, re
d = json.load(io.open(r"C:/SteamCMDData/pool-zh.json", encoding="utf-8"))
for kw in sys.argv[1:]:
    kws = [x for x in re.split(r"[,|]", kw) if x.strip()]
    pat = re.compile("|".join(re.escape(x) for x in kws), re.I)
    print("### %s" % kw)
    n = 0
    for wid, t in d.items():
        if pat.search(t):
            print("   %-12s %s" % (wid, t)); n += 1
            if n >= 8: break
    if n == 0: print("   (无)")
