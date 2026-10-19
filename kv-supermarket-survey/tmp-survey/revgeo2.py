#!/usr/bin/env python3
"""Reverse with full display_name for stores in pairs <=400m."""
import json, time, urllib.request, urllib.parse, os, math, sys

CACHE = "revgeo_cache.json"
cache = json.load(open(CACHE, encoding="utf-8"))

def hav(a, b):
    R = 6371000.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0],a[1],b[0],b[1]])
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(h))

stores = json.load(open("stores_geocoded.json", encoding="utf-8"))
need = []
for i in range(len(stores)):
    for j in range(i+1, len(stores)):
        if stores[i]["brand"] != stores[j]["brand"]:
            d = hav((stores[i]["lat"],stores[i]["lon"]), (stores[j]["lat"],stores[j]["lon"]))
            if d <= 400 and i not in need:
                need.append(i)
            if d <= 400 and j not in need:
                need.append(j)

def rev(lat, lon):
    key = f"full:{lat:.5f},{lon:.5f}"
    if key in cache: return cache[key]
    q = urllib.parse.urlencode({"lat": lat, "lon": lon, "format": "jsonv2",
                                "zoom": 20, "addressdetails": 1, "accept-language": "en,ms"})
    req = urllib.request.Request(f"https://nominatim.openstreetmap.org/reverse?{q}",
                                 headers={"User-Agent": "KV-supermarket-survey/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode())
    out = {"display": d.get("display_name",""), "addr": d.get("address",{})}
    cache[key] = out
    json.dump(cache, open(CACHE,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    time.sleep(1.05)
    return out

for i in sorted(need):
    s = stores[i]
    key = f"full:{s['lat']:.5f},{s['lon']:.5f}"
    if key not in cache:
        rev(s["lat"], s["lon"])
    full = cache[key]
    print(f"--- {i} {s['brand']} | {s['name']} | OSMaddr: {s['addr'][:60]}")
    print(f"    DISPLAY: {full['display'][:180]}")
json.dump(stores, open("stores_geocoded.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
