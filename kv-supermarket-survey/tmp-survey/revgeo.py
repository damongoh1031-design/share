#!/usr/bin/env python3
"""Reverse-geocode candidate stores (Nominatim, cached, 1.1s apart) to recover suburb/mall names."""
import json, time, urllib.request, urllib.parse, os, re, sys

CACHE = "revgeo_cache.json"
cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}

def rev(lat, lon):
    key = f"{lat:.5f},{lon:.5f}"
    if key in cache: return cache[key]
    q = urllib.parse.urlencode({"lat": lat, "lon": lon, "format": "jsonv2",
                                "zoom": 18, "addressdetails": 1, "accept-language": "en,ms"})
    req = urllib.request.Request(f"https://nominatim.openstreetmap.org/reverse?{q}",
                                 headers={"User-Agent": "KV-supermarket-survey/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode())
        a = d.get("address", {})
        parts = [a.get("neighbourhood") or a.get("suburb") or a.get("quarter") or "",
                 a.get("road",""), a.get("postcode",""), a.get("city") or a.get("town") or a.get("state") or ""]
        out = " | ".join(p for p in parts if p)
    except Exception as e:
        out = f"ERR:{e}"
    cache[key] = out
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    time.sleep(1.1)
    return out

stores = json.load(open("stores.json", encoding="utf-8"))
# candidates: any store in a cross-brand pair <=500 m
def hav(a, b):
    import math
    R = 6371000.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0],a[1],b[0],b[1]])
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(h))

need = set()
for i in range(len(stores)):
    for j in range(i+1, len(stores)):
        if stores[i]["brand"] != stores[j]["brand"]:
            d = hav((stores[i]["lat"],stores[i]["lon"]), (stores[j]["lat"],stores[j]["lon"]))
            if d <= 500:
                need.add(i); need.add(j)
print(f"stores to geocode: {len(need)}", file=sys.stderr)
for i in sorted(need):
    s = stores[i]
    s["area"] = rev(s["lat"], s["lon"])
    print(f"{i:3d} {s['brand']:15s} {s['name'][:40]:40s} -> {s['area']}", file=sys.stderr)
json.dump(stores, open("stores_geocoded.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("done", file=sys.stderr)
