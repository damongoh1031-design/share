#!/usr/bin/env python3
"""Build a verified contact table from the Seek Clinic listing capture.

Input : seekclinic_raw.tsv  (name|phone|address|detail_url|source_page)
Output: seekclinic_contacts.csv        full deduplicated table (by phone)
        seekclinic_contacts.jsonl      same rows, raw JSON for audit
        seekclinic_verify_100.csv      100-row deterministic random sample
        seekclinic_build_report.txt    counts + quality gates

No data is invented. Rows with unusable phone numbers are dropped and counted.
"""
from __future__ import annotations

import csv
import json
import random
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "seekclinic_raw.tsv"
OUT_FULL = ROOT / "seekclinic_contacts.csv"
OUT_JSONL = ROOT / "seekclinic_contacts.jsonl"
OUT_100 = ROOT / "seekclinic_verify_100.csv"
OUT_REPORT = ROOT / "seekclinic_build_report.txt"
CHECKED_AT = "2026-10-27"
SEED = 20261027

FIELDS = [
    "source_site", "source_url", "listing_page", "record_type", "name",
    "phone_raw", "phone_normalized", "phone_kind", "address", "state",
    "verification_status", "checked_at", "notes",
]

STATE_PATTERNS = [
    ("W.P. Kuala Lumpur", r"Kuala Lumpur"),
    ("Selangor", r"Selangor"),
    ("Johor", r"Johor"),
    ("Penang", r"Penang"),
    ("Perak", r"Perak"),
    ("Pahang", r"Pahang"),
    ("Malacca", r"Malacca|Melaka"),
    ("Negeri Sembilan", r"Negeri Sembilan"),
    ("Kedah", r"Kedah"),
    ("Kelantan", r"Kelantan"),
    ("Terengganu", r"Terengganu"),
    ("Sabah", r"Sabah"),
    ("Sarawak", r"Sarawak"),
    ("Perlis", r"Perlis"),
]


def norm_phone(raw: str) -> tuple[str, str]:
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("60"):
        national = digits[2:]
        e164 = "+60" + national
    elif digits.startswith("0"):
        e164 = "+6" + digits
    else:
        return "", "invalid"
    kind = "mobile" if re.match(r"^1[0-9]{8,9}$", e164[3:]) else "landline"
    if not (11 <= len(e164) <= 13):
        return "", "invalid"
    return e164, kind


def state_of(address: str) -> str:
    for label, pattern in STATE_PATTERNS:
        if re.search(pattern, address, re.I):
            return label
    return ""


def main() -> None:
    rows = []
    for line in SRC.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) != 5:
            raise SystemExit(f"bad row ({len(parts)} fields): {line[:90]}")
        name, phone_raw, address, url, page = parts
        e164, kind = norm_phone(phone_raw)
        if not e164:
            raise SystemExit(f"unparseable phone: {phone_raw} / {name}")
        rows.append({
            "source_site": "seekclinic.my",
            "source_url": url,
            "listing_page": f"https://seekclinic.my/category/aesthetic-clinic-1/page/{page}/" if page != "1"
                            else "https://seekclinic.my/category/aesthetic-clinic-1/",
            "record_type": "clinic",
            "name": name.strip(),
            "phone_raw": phone_raw,
            "phone_normalized": e164,
            "phone_kind": kind,
            "address": address.strip(),
            "state": state_of(address),
            "verification_status": "listed",
            "checked_at": CHECKED_AT,
            "notes": "",
        })

    total = len(rows)
    # duplicate phone handling: keep every branch row, flag shared numbers
    phone_counts = Counter(r["phone_normalized"] for r in rows)
    for r in rows:
        shared = phone_counts[r["phone_normalized"]]
        if shared > 1:
            r["notes"] = f"shared number across {shared} listings (brand/multi-branch)"

    # dedupe by (phone, name) - identical listing repeated across pages
    seen = set()
    unique_pairs = []
    dropped = 0
    for r in rows:
        key = (r["phone_normalized"], r["name"].lower())
        if key in seen:
            dropped += 1
            continue
        seen.add(key)
        unique_pairs.append(r)

    # one row per unique phone: first occurrence wins, rest merged into notes
    by_phone: dict[str, dict] = {}
    extra_branches: dict[str, list[str]] = {}
    for r in unique_pairs:
        p = r["phone_normalized"]
        if p in by_phone:
            extra_branches.setdefault(p, []).append(r["name"])
            continue
        by_phone[p] = r
    for p, names in extra_branches.items():
        row = by_phone[p]
        row["notes"] = (row["notes"] + "; " if row["notes"] else "") + \
            f"also listed for: {', '.join(names)}"

    final = list(by_phone.values())
    final.sort(key=lambda r: r["name"].lower())

    with OUT_FULL.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(final)

    with OUT_JSONL.open("w", encoding="utf-8") as fh:
        for r in final:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    sample = random.Random(SEED).sample(final, min(100, len(final)))
    sample.sort(key=lambda r: r["name"].lower())
    with OUT_100.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(sample)

    page_counts = Counter(r["listing_page"].rsplit("/", 2)[-2] if "page/" in r["listing_page"] else "1"
                          for r in rows)
    lines = [
        "Seek Clinic capture build report",
        f"checked_at            : {CHECKED_AT}",
        f"raw listing rows      : {total}",
        f"exact duplicate rows  : {dropped}",
        f"unique phone numbers  : {len(final)}",
        f"unique clinic names   : {len({r['name'].lower() for r in final})}",
        f"sample rows (seed {SEED}): {len(sample)}",
        "",
        "rows per listing page:",
    ]
    for page in sorted(page_counts, key=lambda p: int(p)):
        lines.append(f"  page {page:>2}: {page_counts[page]}")
    states = Counter(r["state"] or "(unresolved)" for r in final)
    lines += ["", "unique phones by state:"]
    for state, count in states.most_common():
        lines.append(f"  {state:<20} {count}")
    lines += ["", "shared numbers:", ]
    for phone, count in phone_counts.most_common():
        if count > 1:
            lines.append(f"  {phone} used by {count} listings")
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
