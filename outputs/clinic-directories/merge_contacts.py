#!/usr/bin/env python3
"""Merge the three clinic-directory captures into one deduplicated contact table.

Inputs
  seekclinic_contacts.csv           109 unique phones, Seek Clinic listing pages
  aestheticclinic_profiles.jsonl    AestheticClinic.my profile records
  tressless_verified.csv            Tressless MY records read page-by-page

Outputs
  combined_contacts.csv         one row per unique phone (primary deliverable)
  combined_contacts_detail.csv  one row per source record (audit trail)
  combined_conflicts.csv        same clinic, different phone across sources
  combined_build_report.txt     counts, corrections applied, coverage notes
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHECKED_AT = "2026-10-27"


def norm_phone(raw: str) -> tuple[str, str]:
    """Return (e164, note). Handles MY formats: +60 10-368 1400, 03-3395 1393, 60123..."""
    s = (raw or "").strip()
    if not s:
        return "", "empty"
    digits = re.sub(r"[^\d+]", "", s)
    plus = digits.startswith("+")
    d = digits.lstrip("+")
    if d.startswith("60"):
        e164 = "+" + d
    elif d.startswith("0"):
        e164 = "+6" + d
    elif d.startswith("1") and len(d) in (9, 10):
        e164 = "+60" + d
    elif d.startswith("6"):
        e164 = "+" + d
    else:
        return "", f"unrecognized:{s}"
    body = e164[3:]
    if not re.fullmatch(r"\d{8,10}", body):
        return "", f"bad_length:{e164}"
    if not (body.startswith("1") or body.startswith("3") or body.startswith("4")
            or body.startswith("5") or body.startswith("6") or body.startswith("7")
            or body.startswith("8") or body.startswith("9") or body.startswith("0")):
        return "", f"bad_prefix:{e164}"
    note = ""
    if plus and re.search(r"[\s\-()]", s):
        note = "normalized_from_spaced_format"
    return e164, note


def key_name(name: str) -> str:
    """Loose match key. Keep the brand words, drop only legal suffixes and punctuation."""
    n = (name or "").lower()
    n = re.sub(r"\b(sdn\.? ?bhd\.?|bhd\.?|enterprise|plt)\b", " ", n)
    n = re.sub(r"[^a-z0-9]+", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n if len(n) >= 6 else ""


records = []  # dicts with source_site, source_url, name, phone, address, state, extra

# --- Seek Clinic (read the raw TSV, not the CSV: the CSV can be re-saved by a
# spreadsheet and silently turn +601123200821 into 6.01123E+11) ---
seek_path = ROOT / "seekclinic_raw.tsv"
if seek_path.exists():
    for line in seek_path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, phone_raw, address, url, page = line.split("|")
        records.append({
            "source_site": "seekclinic.my",
            "source_url": url,
            "name": name,
            "phone_raw": phone_raw,
            "address": address,
            "state": "",
            "extra": f"listing_page={page}",
            "person": "",
        })

# --- Seek Clinic, additional categories (medical-clinic pages 1-24, then 25-100) ---
for med_name in ("seekclinic_medical_raw.tsv", "seekclinic_medical2_raw.tsv",
                 "seekclinic_medical3_raw.tsv", "seekclinic_medical4_raw.tsv",
                 "seekclinic_medical5_raw.tsv"):
    seek_med = ROOT / med_name
    if not seek_med.exists():
        continue
    for line in seek_med.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) != 5:
            print(f"WARN: skipping malformed line in {med_name}: {line[:80]}")
            continue
        name, phone_raw, address, url, page = parts
        records.append({
            "source_site": "seekclinic.my",
            "source_url": url,
            "name": name,
            "phone_raw": phone_raw,
            "address": address,
            "state": "",
            "extra": f"category=medical-clinic; listing_page={page}",
            "person": "",
            "record_type": "seekclinic.my:medical-clinic",
        })

# --- AestheticClinic ---
ac_path = ROOT / "aestheticclinic_profiles.jsonl"
ac_rows = 0
if ac_path.exists():
    for line in ac_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        p = json.loads(line)
        ac_rows += 1
        if p.get("error") or not p.get("phones"):
            continue
        for ph in p["phones"]:
            records.append({
                "source_site": "aestheticclinic.my",
                "source_url": p["url"],
                "name": p.get("name", ""),
                "phone_raw": ph,
                "address": p.get("address", ""),
                "state": "",
                "extra": f"completeness={p.get('completeness','')}; premises={p.get('registered_premises','')}",
                "person": p.get("matched_doctor", ""),
            })

# --- Tressless ---
tr_path = ROOT / "tressless_verified.csv"
tr_rows = 0
if tr_path.exists():
    for r in csv.DictReader(tr_path.open(encoding="utf-8-sig")):
        tr_rows += 1
        records.append({
            "source_site": "tressless.com",
            "source_url": r["source_url"],
            "name": r["name"],
            "phone_raw": r["phone"],
            "address": r.get("city", ""),
            "state": "",
            "extra": r.get("note", ""),
            "person": r.get("doctors", ""),
        })

# --- normalize + corrections ---
corrections = Counter()
for rec in records:
    e164, note = norm_phone(rec["phone_raw"])
    rec["phone"] = e164
    if note.startswith("normalized"):
        corrections["phone_format_normalized"] += 1
    elif note.startswith("unrecognized") or note.startswith("bad_"):
        corrections["phone_rejected:" + note.split(":")[0]] += 1
    rec["name_key"] = key_name(rec["name"])

valid = [r for r in records if r["phone"]]
dropped = [r for r in records if not r["phone"]]

# --- per-phone aggregation ---
by_phone: dict[str, dict] = {}
for r in valid:
    p = r["phone"]
    agg = by_phone.setdefault(p, {
        "phone": p,
        "names": [],
        "sources": set(),
        "source_urls": [],
        "addresses": [],
        "states": set(),
        "people": set(),
        "record_count": 0,
        "extra": [],
    })
    if r["name"] and r["name"] not in agg["names"]:
        agg["names"].append(r["name"])
    agg["sources"].add(r["source_site"])
    if r["source_url"] not in agg["source_urls"]:
        agg["source_urls"].append(r["source_url"])
    if r["address"] and r["address"] not in agg["addresses"]:
        agg["addresses"].append(r["address"])
    if r["state"]:
        agg["states"].add(r["state"])
    if r["person"]:
        agg["people"].add(r["person"].split(" — ")[0])
    if r["extra"]:
        agg["extra"].append(r["extra"])
    agg["record_count"] += 1

# --- data-quality guard: detect spreadsheet scientific-notation damage ---
sci_damaged = 0
repaired_csv = ROOT / "seekclinic_contacts.csv"
if repaired_csv.exists():
    for r in csv.DictReader(repaired_csv.open(encoding="utf-8-sig")):
        if "E+" in (r.get("phone_raw") or ""):
            sci_damaged += 1

# --- cross-source conflict detection: same clinic name key, different phone ---
name_to_phones = defaultdict(set)
for r in valid:
    if r["name_key"]:
        name_to_phones[r["name_key"]].add(r["phone"])
conflicts = {k: v for k, v in name_to_phones.items() if len(v) > 1}

# --- brand-number detection: one phone used by >=3 distinct clinics ---
phone_to_keys = defaultdict(set)
for r in valid:
    if r["name_key"]:
        phone_to_keys[r["phone"]].add(r["name_key"])
brand_phones = {p for p, keys in phone_to_keys.items() if len(keys) >= 3}

# --- clinic-level view: one row per clinic, prefer a direct branch line over a brand number ---
clinic_rows = {}
for r in valid:
    k = r["name_key"]
    if not k:
        continue
    c = clinic_rows.setdefault(k, {"name": r["name"], "phones": set(), "sources": set(),
                                   "addresses": set(), "urls": set(), "people": set()})
    c["phones"].add(r["phone"])
    c["sources"].add(r["source_site"])
    if r["address"]:
        c["addresses"].add(r["address"])
    c["urls"].add(r["source_url"])
    if r["person"]:
        c["people"].add(r["person"].split(" — ")[0])

clinic_out = []
for k, c in sorted(clinic_rows.items(), key=lambda kv: kv[1]["name"].lower()):
    direct = sorted(p for p in c["phones"] if p not in brand_phones)
    brand = sorted(p for p in c["phones"] if p in brand_phones)
    clinic_out.append({
        "clinic_key": k,
        "clinic_name": c["name"],
        "primary_phone": (direct or brand or [""])[0],
        "primary_phone_role": "branch_direct" if direct else ("brand_shared" if brand else ""),
        "all_phones": "; ".join(sorted(c["phones"])),
        "brand_phones": "; ".join(brand),
        "person_names": "; ".join(sorted(c["people"])),
        "sources": "; ".join(sorted(c["sources"])),
        "address": sorted(c["addresses"])[0] if c["addresses"] else "",
        "source_urls": " || ".join(sorted(c["urls"])),
        "cross_source_confirmed": "yes" if len(c["sources"]) > 1 else "no",
        "checked_at": CHECKED_AT,
    })

with (ROOT / "combined_clinics.csv").open("w", newline="", encoding="utf-8-sig") as fh:
    fields = ["clinic_key", "clinic_name", "primary_phone", "primary_phone_role",
              "all_phones", "brand_phones", "person_names", "sources", "address",
              "source_urls", "cross_source_confirmed", "checked_at"]
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    w.writerows(clinic_out)

OUT_FIELDS = [
    "phone", "primary_name", "other_names", "person_names", "state", "addresses",
    "sources", "source_urls", "record_count", "shared_across_clinics",
    "cross_source_confirmed", "checked_at", "notes",
]

out_rows = []
for p, a in sorted(by_phone.items(), key=lambda kv: kv[1]["names"][0].lower() if kv[1]["names"] else ""):
    multi = len(a["names"]) > 1
    out_rows.append({
        "phone": p,
        "primary_name": a["names"][0] if a["names"] else "",
        "other_names": "; ".join(a["names"][1:]),
        "person_names": "; ".join(sorted(a["people"])),
        "state": "; ".join(sorted(a["states"])),
        "addresses": " || ".join(a["addresses"]),
        "sources": "; ".join(sorted(a["sources"])),
        "source_urls": " || ".join(a["source_urls"]),
        "record_count": a["record_count"],
        "shared_across_clinics": "yes" if multi else "no",
        "cross_source_confirmed": "yes" if len(a["sources"]) > 1 else "no",
        "checked_at": CHECKED_AT,
        "notes": " | ".join(dict.fromkeys(a["extra"]))[:400],
    })
    if p in brand_phones:
        out_rows[-1]["notes"] = ("brand_shared_number; " + out_rows[-1]["notes"])[:400]

with (ROOT / "combined_contacts.csv").open("w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=OUT_FIELDS)
    w.writeheader()
    w.writerows(out_rows)

DETAIL_FIELDS = ["source_site", "name", "phone", "phone_raw", "person_names",
                 "state", "address", "source_url", "notes", "checked_at"]
with (ROOT / "combined_contacts_detail.csv").open("w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=DETAIL_FIELDS)
    w.writeheader()
    for r in sorted(valid, key=lambda x: (x["source_site"], x["name"].lower())):
        w.writerow({
            "source_site": r["source_site"],
            "name": r["name"],
            "phone": r["phone"],
            "phone_raw": r["phone_raw"],
            "person_names": r["person"],
            "state": r["state"],
            "address": r["address"],
            "source_url": r["source_url"],
            "notes": r["extra"],
            "checked_at": CHECKED_AT,
        })

with (ROOT / "combined_conflicts.csv").open("w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["name_key", "phones", "sources"])
    for k, phones in sorted(conflicts.items()):
        srcs = sorted({r["source_site"] for r in valid if r["name_key"] == k})
        w.writerow([k, "; ".join(sorted(phones)), "; ".join(srcs)])

per_source = Counter(r["source_site"] for r in valid)
lines = [
    "Combined clinic contact build report",
    f"checked_at                    : {CHECKED_AT}",
    f"raw source records            : {len(records)}",
    f"  seekclinic.my               : {per_source.get('seekclinic.my', 0)}",
    f"  aestheticclinic.my          : {per_source.get('aestheticclinic.my', 0)}",
    f"  tressless.com               : {per_source.get('tressless.com', 0)}",
    f"records rejected (bad phone)  : {len(dropped)}",
    f"unique phone numbers          : {len(by_phone)}",
    f"unique clinics                : {len(clinic_out)}",
    f"brand-shared numbers (>=3 use): {len(brand_phones)}",
    f"multi-source confirmed phones : {sum(1 for r in out_rows if r['cross_source_confirmed'] == 'yes')}",
    f"multi-source confirmed clinics: {sum(1 for c in clinic_out if c['cross_source_confirmed'] == 'yes')}",
    f"phones shared by >1 clinic    : {sum(1 for r in out_rows if r['shared_across_clinics'] == 'yes')}",
    f"clinics listed with >1 number : {len(conflicts)}",
    "",
    "aestheticclinic profiles read : " + str(ac_rows),
    "tressless records read        : " + str(tr_rows),
    f"csv sci-notation rows repaired: {sci_damaged}",
    "",
    "corrections applied:",
]
for k, v in corrections.most_common():
    lines.append(f"  {k:<34} {v}")
(ROOT / "combined_build_report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
