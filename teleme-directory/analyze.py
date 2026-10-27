#!/usr/bin/env python3
"""Build CSV/JSON exports + stats from records.jsonl"""
import csv
import json
import os
import re
from collections import Counter

OUT = os.path.dirname(os.path.abspath(__file__))
def norm(raw):
    """Return (e164, quality). quality: ok | short | foreign | junk"""
    d = re.sub(r"[^\d+]", "", raw or "")
    plus = d.startswith("+")
    dg = re.sub(r"\D", "", d)
    if plus:
        e = "+" + dg
    elif dg.startswith("60"):
        e = "+" + dg
    elif dg.startswith("0"):
        e = "+6" + dg
    else:
        e = "+" + dg if dg else ""
    nat = dg[2:] if dg.startswith("60") else dg
    if not e:
        return "", "junk"
    if e.startswith("+60"):
        if len(nat) < 8:
            return e, "short"
        if len(nat) > 10:
            return e, "junk"
        return e, "ok"
    return e, "foreign"


recs = []
seen = set()
for line in open(os.path.join(OUT, "records.jsonl"), encoding="utf-8"):
    try:
        r = json.loads(line)
    except Exception:
        continue
    if r.get("slug") in seen or "error" in r:
        continue
    seen.add(r.get("slug"))
    for c in r.get("clinics", []):
        c["phone_e164"], c["quality"] = norm(c.get("phone", ""))
    r["phones"] = [c["phone_e164"] for c in r.get("clinics", [])
                   if c.get("quality") == "ok"]
    recs.append(r)

recs.sort(key=lambda r: r.get("name", ""))

# --- flat clinic-level CSV (one row per doctor-clinic pair) ---
flat_path = os.path.join(OUT, "teleme_clinic_contacts.csv")
with open(flat_path, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["doctor", "specialty", "clinic", "phone", "phone_e164",
                "address", "license_no", "languages", "profile_url"])
    for r in recs:
        for c in r.get("clinics", []):
            if c.get("quality") != "ok":
                continue
            w.writerow([r["name"], r["specialty"], c["clinic"], c["phone"],
                        c["phone_e164"], c["address"], r["license_no"],
                        r["languages"], r["url"]])

# --- unique phone CSV ---
phones = {}
for r in recs:
    for c in r.get("clinics", []):
        p = c.get("phone_e164")
        if not p or c.get("quality") != "ok":
            continue
        e = phones.setdefault(p, {"phone_e164": p, "phone_raw": c["phone"],
                                  "clinics": set(), "doctors": set(),
                                  "specialties": set()})
        if c["clinic"]:
            e["clinics"].add(c["clinic"])
        e["doctors"].add(r["name"])
        e["specialties"].add(r["specialty"])

uniq_path = os.path.join(OUT, "teleme_unique_phones.csv")
with open(uniq_path, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["phone_e164", "phone_raw", "clinic_count", "doctor_count",
                "clinics", "doctors", "specialties"])
    for p in sorted(phones):
        e = phones[p]
        w.writerow([p, e["phone_raw"], len(e["clinics"]), len(e["doctors"]),
                    " ; ".join(sorted(e["clinics"])),
                    " ; ".join(sorted(e["doctors"])),
                    " ; ".join(sorted(e["specialties"]))])

# --- stats ---
n = len(recs)
with_phone = sum(1 for r in recs if r.get("phones"))
allp = [p for r in recs for p in r.get("phones", [])]
kind = Counter("mobile" if re.match(r"\+601\d", p) else
               "landline" if re.match(r"\+60[3-9]", p) else "other" for p in allp)
q = Counter(c.get("quality") for r in recs for c in r.get("clinics", []))
NON_PHYS = {"Pharmacist", "Optician", "Optician / Optometrist", "Psychologist",
            "Dietician/Nutritionist", "Health Coach", "Nurse educator",
            "Psychotherapy & Hypnotherapy", "Physiotherapy, rehabilitation & sports therapy"}
phys = [r for r in recs if r.get("specialty") not in NON_PHYS]
spec = Counter(r["specialty"] for r in recs if r.get("specialty"))
lic = sum(1 for r in recs if r.get("license_no"))

stats = {
    "doctors_crawled": n,
    "doctors_with_phone": with_phone,
    "coverage_pct": round(100 * with_phone / n, 1) if n else 0,
    "doctor_clinic_rows": len(allp),
    "unique_phones": len(phones),
    "mobile_vs_landline": dict(kind),
    "doctors_with_license_no": lic,
    "phone_quality": dict(q),
    "non_physician_profiles": n - len(phys),
    "physician_profiles": len(phys),
    "physicians_with_phone": sum(1 for r in phys if r.get("phones")),
    "top_specialties": spec.most_common(12),
}
print(json.dumps(stats, indent=1, ensure_ascii=False))
json.dump(stats, open(os.path.join(OUT, "stats.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nwrote:", flat_path)
print("wrote:", uniq_path)
