#!/usr/bin/env python3
"""Final curated close-pair listing with area names."""
import json, math, re

def hav(a, b):
    R = 6371000.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0],a[1],b[0],b[1]])
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(h))

stores = json.load(open("stores_geocoded.json", encoding="utf-8"))
pairs = []
for i in range(len(stores)):
    for j in range(i+1, len(stores)):
        a, b = stores[i], stores[j]
        d = hav((a["lat"],a["lon"]), (b["lat"],b["lon"]))
        if d <= 500 and a["brand"] != b["brand"]:
            pairs.append((d, a, b))
pairs.sort(key=lambda x: x[0])

def short(s):
    n = s["name"].strip()
    area = s.get("area","")
    parts = [p.strip() for p in area.split("|") if p.strip()]
    return n, area, parts

for d, a, b in pairs:
    na, aa, pa = short(a); nb, ab, pb = short(b)
    # same-mall heuristic: same postcode & same road & same suburb
    same = (pa and pb and pa[-1]==pb[-1] and len(pa)>2 and len(pb)>2 and pa[-2]==pb[-2] and pa[0]==pb[0])
    print(f"{d:5.0f}m | {a['brand']:15s} {na[:34]:34s} [{aa.split(' | ')[0][:28] if aa else ''}] {a['addr'][:40]:40s} ({a['lat']:.4f},{a['lon']:.4f})")
    print(f"       {b['brand']:15s} {nb[:34]:34s} [{ab.split(' | ')[0][:28] if ab else ''}] {b['addr'][:40]:40s} ({b['lat']:.4f},{b['lon']:.4f})  SAME_COMPLEX={same}")
print(f"TOTAL <=500m: {len(pairs)}")
