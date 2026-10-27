#!/usr/bin/env python3
"""Polite, non-bypass diagnostics for three public clinic directories.

This script performs bounded health checks only. It does NOT crawl whole
sites, solve challenges, rotate proxies, or disguise browser fingerprints.
Use only after obtaining site permission for bulk collection.
"""
from __future__ import annotations

import csv
import hashlib
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
URL_FILE = ROOT / "sitecheck_urls.txt"
OUT_CSV = ROOT / "sitecheck_results.csv"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
TIMEOUT = 20
DELAY = 1.0

CHALLENGE_MARKERS = (
    "one moment, please",
    "attention required! | cloudflare",
    "cf-challenge",
    "challenge-platform",
    "verify you are human",
    "just a moment",
)


def classify(status: int | None, content_type: str, body: bytes, error: str = "") -> str:
    text = body[:200_000].decode("utf-8", "replace").lower()
    if status in (401, 403, 429):
        return "blocked_http"
    if any(marker in text for marker in CHALLENGE_MARKERS):
        return "challenge_page"
    if status is not None and 500 <= status <= 599:
        return "server_error"
    if status is not None and status >= 400:
        return "http_error"
    if "xml" in content_type or text.lstrip().startswith("<?xml"):
        return "xml_ok"
    if "html" in content_type or "<html" in text[:5000]:
        return "html_ok"
    if status and 200 <= status < 300:
        return "ok"
    return "network_error"


def one(url: str) -> dict[str, str]:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    started = time.monotonic()
    status = None
    content_type = ""
    body = b""
    error = ""
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            status = response.status
            content_type = response.headers.get("Content-Type", "")
            body = response.read(1_000_000)
    except urllib.error.HTTPError as exc:
        status = exc.code
        content_type = exc.headers.get("Content-Type", "") if exc.headers else ""
        body = exc.read(1_000_000)
        error = str(exc)
    except Exception as exc:  # noqa: BLE001 - diagnostics need capture and continue
        error = f"{type(exc).__name__}: {exc}"
    elapsed = round(time.monotonic() - started, 3)
    text = body.decode("utf-8", "replace")
    title = ""
    match = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    if match:
        title = re.sub(r"\s+", " ", match.group(1)).strip()[:180]
    phone_count = len(re.findall(r"href\s*=\s*['\"]tel:", text, re.I))
    return {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "url": url,
        "status": str(status or ""),
        "content_type": content_type,
        "result_class": classify(status, content_type, body, error),
        "bytes_read": str(len(body)),
        "elapsed_seconds": str(elapsed),
        "title": title,
        "tel_link_count": str(phone_count),
        "body_sha256_prefix": hashlib.sha256(body).hexdigest()[:16] if body else "",
        "error": error[:300],
        "note": "A block/challenge is recorded and not bypassed.",
    }


def main() -> None:
    urls = [
        line.strip() for line in URL_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    fields = [
        "checked_at_utc", "url", "status", "content_type", "result_class",
        "bytes_read", "elapsed_seconds", "title", "tel_link_count",
        "body_sha256_prefix", "error", "note",
    ]
    rows = []
    for index, url in enumerate(urls):
        row = one(url)
        rows.append(row)
        print(f"{row['result_class']:16} {row['status']:3} {row['bytes_read']:>7} {url}", flush=True)
        if index + 1 < len(urls):
            time.sleep(DELAY)
    with OUT_CSV.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {OUT_CSV} ({len(rows)} bounded checks)")


if __name__ == "__main__":
    main()
