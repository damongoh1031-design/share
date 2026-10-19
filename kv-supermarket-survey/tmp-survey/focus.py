#!/usr/bin/env python3
"""Focus on major supermarket brands (drop convenience 99 Speedmart), dedupe, list close pairs."""
import json, math, re, sys
from collections import defaultdict

BRANDS = {
    "AEON":        r"\bAEON\b(?!\s*BIG)",
    "AEON BIG":    r"AEON\s*BIG",
    "Lotus's":     r"\bLOTUS|Lotus'?s|\bTESCO\b",
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
    "Checkers":    r"CHECKERS",
    "HeroMarket":  r"HERO ?MARKET",
    "Mercato":     r"MERCAT",
    "Cold Storage": r"COLD\s*STORAGE",
    "Isetan":      r"ISETAN",
}
EXCLUDE_99 = True

def brand_of(name):
    u = name.upper()
    if EXCLUDE_99 and re.search(r"99\s*SPEED ?MART", name, re.IGNORECASE):
        return []
    if re.search(r"AEON\s*BIG", name, re.IGNORECASE):
        return ["AEON BIG"]
    hits = [b for b, pat in BRANDS.items() if re.search(pat, name, re.IGNORECASE)]
    return hits

def hav(a, b):
    R = 6371000.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(h))

def clean(s): return re.sub(r"\s+"," ",(s or "")).strip()

data = json.load(open("overpass_raw.json", encoding="utf-8"))
stores = []
for el in data.get("elements", []):
    t = el.get("tags", {})
    lat = el.get("lat", el.get("center", {}).get("lat"))
    lon = el.get("lon", el.get("center", {}).get("lon"))
    if lat is None or lon is None: continue
    name = clean(t.get("name","")) or clean(t.get("brand",""))
    if not name: continue
    b = brand_of(name)
    if not b: continue
    stores.append({
        "name": name, "brand": "/".join(b), "shop": t.get("shop",""),
        "lat": lat, "lon": lon,
        "addr": clean(" ".join(filter(None,[
            t.get("addr:housenumber",""), t.get("addr:street",""),
            t.get("addr:city",""), t.get("addr:postcode","")]))),
    })

# dedupe same brand within 40 m (mall vs supermarket duplicate markers)
kept = []
for s in sorted(stores, key=lambda x: (x["brand"], x["name"])):
    dup = False
    for k in kept:
        if k["brand"].split("/")[0] == s["brand"].split("/")[0] and hav((k["lat"],k["lon"]),(s["lat"],s["lon"])) <= 40:
            # keep the more informative one (more tags / longer name)
            if len(s["name"]) > len(k["name"]) or (s["addr"] and not k["addr"]):
                k.update({"name": s["name"], "addr": s["addr"] or k["addr"],
                          "lat": (k["lat"]+s["lat"])/2, "lon": (k["lon"]+s["lon"])/2,
                          "merged": (k.get("merged",1)+1)})
            else:
                k["merged"] = k.get("merged",1)+1
            dup = True; break
    if not dup:
        kept.append(s)

print(f"brand stores after dedupe: {len(kept)}", file=sys.stderr)
byc = defaultdict(int)
for k in kept: byc[k["brand"]] += 1
for b,c in sorted(byc.items(), key=lambda x:-x[1]): print(f"  {b}: {c}", file=sys.stderr)

json.dump(kept, open("stores.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

# candidate pairs: different brand, <=600 m ; also same-brand <=600 m (flag)
pairs = []
for i in range(len(kept)):
    for j in range(i+1, len(kept)):
        a,b = kept[i], kept[j]
        d = hav((a["lat"],a["lon"]),(b["lat"],b["lon"]))
        if d <= 700:
            pairs.append((d,a,b))
pairs.sort(key=lambda x:x[0])

diffsame = [(d,a,b) for d,a,b in pairs if a["brand"] != b["brand"]]
same = [(d,a,b) for d,a,b in pairs if a["brand"] == b["brand"]]
print(f"cross-brand pairs <=700m: {len(diffsame)}; same-brand: {len(same)}", file=sys.stderr)

def line(tag, d,a,b):
    return (f"{d:6.0f} m | {a['brand']:15s} {a['name'][:32]:32s} {a['addr'][:36]:36s} @({a['lat']:.4f},{a['lon']:.4f}) || "
            f"{b['brand']:15s} {b['name'][:32]:32s} {b['addr'][:36]:36s} @({b['lat']:.4f},{b['lon']:.4f})")

with open("cross_pairs.txt","w",encoding="utf-8") as f:
    for d,a,b in diffsame: f.write(line("x",d,a,b)+"\n")
with open("same_pairs.txt","w",encoding="utf-8") as f:
    for d,a,b in same: f.write(line("s",d,a,b)+"\n")

print("\n=== CROSS-BRAND PAIRS (top 100) ===")
for d,a,b in diffsame[:100]: print(line("x",d,a,b))
print("\n=== SAME-BRAND PAIRS (<=700m) ===")
for d,a,b in same: print(line("s",d,a,b))
