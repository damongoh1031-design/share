#!/usr/bin/env python3
"""Parse Overpass dump -> Klang Valley supermarket inventory + pairwise proximity."""
import json, math, re, sys
from collections import defaultdict

RAW = "overpass_raw.json"

# brand whitelist: display name -> regex aliases (case-insensitive)
BRANDS = {
    "AEON":        r"\bAEON\b",
    "AEON BIG":    r"AEON\s*BIG|Aeon\s*Big",
    "Lotus's":     r"\bLOTUS|Lotus'?s|新麦森|\bTESCO\b",
    "Giant":       r"\bGIANT\b",
    "Econsave":    r"\bECONSAVE\b",
    "Mydin":       r"\bMYDIN\b",
    "Jaya Grocer": r"JAYA\s*GROCER",
    "Village Grocer": r"VILLAGE\s*GROCER",
    "LuLu":        r"\bLULU\b",
    "NSK":         r"\bNSK\b",
    "TF Value-Mart": r"TF\s*VALUE",
    "Billion":     r"\bBILLION\b",
    "The Store":   r"\bTHE\s*STORE\b",
    "99 Speedmart": r"99\s*SPEED ?MART",
    "Checkers":    r"CHECKERS",
    "Mercató":     r"MERCAT",
    "HeroMarket":  r"HERO ?MARKET",
    "Sogo":        r"\bSOGO\b",
    "Cold Storage": r"COLD\s*STORAGE",
    "Jason's":     r"JASON'?S",
    "Isetan":      r"ISETAN",
    "Mitsui":      r"MITSUI",
    "Kedai Rakyat": r"KEDAI\s*RAKYAT",
    "YaPEIM":      r"YAPEIM",
}

def hav(a, b):
    R = 6371000.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(h))

def clean(s):
    return re.sub(r"\s+", " ", (s or "")).strip()

data = json.load(open(RAW, encoding="utf-8"))
rows = []
for el in data.get("elements", []):
    t = el.get("tags", {})
    lat = el.get("lat", el.get("center", {}).get("lat"))
    lon = el.get("lon", el.get("center", {}).get("lon"))
    if lat is None or lon is None:
        continue
    name = clean(t.get("name", "")) or clean(t.get("brand", ""))
    if not name:
        continue
    rows.append({
        "osm_type": el["type"], "osm_id": el["id"],
        "name": name, "shop": t.get("shop", ""),
        "lat": lat, "lon": lon,
        "addr": clean(" ".join(filter(None, [
            t.get("addr:housenumber",""), t.get("addr:street",""),
            t.get("addr:city",""), t.get("addr:postcode","")]))),
    })

def brand_of(name):
    u = name.upper()
    hits = []
    for b, pat in BRANDS.items():
        if re.search(pat, name, re.IGNORECASE):
            hits.append(b)
    if "AEON" in u and "BIG" in u:
        hits = ["AEON BIG"]
    return hits

matched = []
for r in rows:
    b = brand_of(r["name"])
    if b:
        r["brand"] = "/".join(b)
        matched.append(r)

print(f"total OSM shop elements with name: {len(rows)}; brand-matched: {len(matched)}", file=sys.stderr)
bystore = defaultdict(list)
for r in matched:
    bystore[r["brand"]].append(r)
for b in sorted(bystore, key=lambda k: -len(bystore[k])):
    print(f"  {b}: {len(bystore[b])}", file=sys.stderr)

json.dump(matched, open("brand_matched.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# pairwise proximity on brand-matched stores only
pairs = []
for i in range(len(matched)):
    for j in range(i+1, len(matched)):
        a, b = matched[i], matched[j]
        d = hav((a["lat"],a["lon"]), (b["lat"],b["lon"]))
        if d <= 600:
            pairs.append((d, a, b))
pairs.sort(key=lambda x: x[0])

with open("pairs.tsv", "w", encoding="utf-8") as f:
    f.write("dist_m\tbrandA\tnameA\taddrA\tlatA\tlonA\tbrandB\tnameB\taddrB\tlatB\tlonB\n")
    for d, a, b in pairs:
        f.write(f"{d:.0f}\t{a['brand']}\t{a['name']}\t{a['addr']}\t{a['lat']:.5f}\t{a['lon']:.5f}\t"
                f"{b['brand']}\t{b['name']}\t{b['addr']}\t{b['lat']:.5f}\t{b['lon']:.5f}\n")

print(f"pairs <=600m: {len(pairs)}", file=sys.stderr)
print("=== TOP PAIRS ===")
for d, a, b in pairs[:80]:
    print(f"{d:6.0f} m | {a['brand']:14s} {a['name'][:38]:38s} {a['addr'][:30]:30s} || {b['brand']:14s} {b['name'][:38]:38s} {b['addr'][:30]}")
