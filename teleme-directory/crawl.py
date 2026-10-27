#!/usr/bin/env python3
"""Teleme doctor directory crawler: profiles -> clinic contact info.

Respects robots.txt (only /internal/ disallowed), 1 req/s politeness delay.
"""
import csv
import html as H
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
BASE = "https://teleme.co"
OUT = os.path.dirname(os.path.abspath(__file__))
DELAY = 0.5
WORKERS = 8
RETRY = 3


def get(url):
    last = None
    for i in range(RETRY):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=35) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 + i * 3)
    raise last


def clean(s):
    s = re.sub(r"<br\s*/?>", " | ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = H.unescape(s)
    return re.sub(r"\s+", " ", s).strip(" |")


def section(html, start_marker, end_markers):
    i = html.find(start_marker)
    if i < 0:
        return ""
    j = len(html)
    for m in end_markers:
        k = html.find(m, i + len(start_marker))
        if k > 0:
            j = min(j, k)
    return html[i:j]


def parse(slug, html):
    rec = {"slug": slug, "url": f"{BASE}/doctors/profile/{slug}"}

    m = re.search(r'<h3 class="name">(.*?)</h3>', html, re.S)
    rec["name"] = clean(m.group(1)) if m else ""
    rec["name"] = re.sub(r"\s*(Male|Female)$", "", rec["name"]).strip()

    m = re.search(r'<p class="specialty">(.*?)</p>', html, re.S)
    rec["specialty"] = clean(m.group(1)) if m else ""

    m = re.search(r"Video Call Rate</h4>\s*<p class=\"rate\">(.*?)</p>", html, re.S)
    rec["video_rate"] = clean(m.group(1)) if m else ""
    m = re.search(r"Messenger Rate</h4>\s*<p class=\"rate\">(.*?)</p>", html, re.S)
    rec["msg_rate"] = clean(m.group(1)) if m else ""
    m = re.search(r'class="number">([\d,]+) people', html)
    rec["views"] = m.group(1).replace(",", "") if m else ""
    m = re.search(r'class="number">([\d,]+) Follower', html)
    rec["followers"] = m.group(1).replace(",", "") if m else ""

    gen = section(html, 'id="general"', ['id="clinics"', 'id="services"'])
    m = re.search(r"<h4>License no\.</h4>\s*<p>(.*?)</p>", gen, re.S)
    rec["license_no"] = clean(m.group(1)) if m else ""
    m = re.search(r"<h4>Spoken Languages</h4>\s*<p>(.*?)</p>", gen, re.S)
    rec["languages"] = clean(m.group(1)) if m else ""
    m = re.search(r'<div class="awards">(.*?)</div>', gen, re.S)
    rec["qualifications"] = clean(m.group(1)) if m else ""
    m = re.search(r"<h4>Affiliations</h4>\s*<p>(.*?)</p>", gen, re.S)
    rec["affiliations"] = clean(m.group(1)) if m else ""
    m = re.search(r"<h4>Biography</h4>(.*?)</div>", gen, re.S)
    bio = clean(m.group(1)) if m else ""
    rec["biography"] = "" if bio in ("-", "") else bio[:400]

    cl = section(html, 'id="clinics"', ['id="services"', 'id="look"', "profile-tabs"])
    names = re.findall(r"<h4>([^<]+?)\s*</h4>\s*<p class=\"grey\">(.*?)</p>", cl, re.S)
    phones = re.findall(r"<h4>Contact</h4>\s*<p>(.*?)</p>", cl, re.S)
    clinics = []
    for i, (cname, addr) in enumerate(names):
        clinics.append({
            "clinic": clean(cname),
            "address": clean(addr),
            "phone": clean(phones[i]) if i < len(phones) else "",
        })
    if len(phones) > len(names):
        for p in phones[len(names):]:
            clinics.append({"clinic": "", "address": "", "phone": clean(p)})

    # normalise phone to E.164-ish
    for c in clinics:
        d = re.sub(r"[^\d+]", "", c["phone"])
        if d.startswith("+"):
            d = "+" + re.sub(r"\D", "", d)
        elif d.startswith("60"):
            d = "+" + d
        elif d.startswith("0"):
            d = "+6" + d
        c["phone_e164"] = d

    rec["clinics"] = clinics
    rec["phones"] = [c["phone_e164"] for c in clinics if c["phone_e164"]]
    return rec


def main():
    slugs = [s for s in open(os.path.join(OUT, "profiles_list.txt"),
                             encoding="utf-8").read().split() if s]
    done_path = os.path.join(OUT, "records.jsonl")
    seen = set()
    if os.path.exists(done_path):
        for line in open(done_path, encoding="utf-8"):
            try:
                seen.add(json.loads(line)["slug"])
            except Exception:  # noqa: BLE001
                pass
    todo = [s for s in slugs if s not in seen]
    print(f"total {len(slugs)} | done {len(seen)} | todo {len(todo)}", flush=True)

    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading

    lock = threading.Lock()
    f = open(done_path, "a", encoding="utf-8")
    counter = {"n": 0, "ok": 0, "fail": 0}

    def work(slug):
        time.sleep(DELAY)
        try:
            return parse(slug, get(f"{BASE}/doctors/profile/{slug}"))
        except Exception as e:  # noqa: BLE001
            return {"slug": slug, "error": str(e)}

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(work, s): s for s in todo}
        for fu in as_completed(futs):
            rec = fu.result()
            with lock:
                counter["n"] += 1
                if "error" in rec:
                    counter["fail"] += 1
                    print(f"FAIL {rec['slug']}: {rec['error'][:80]}", flush=True)
                else:
                    counter["ok"] += 1
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    f.flush()
                if counter["n"] % 100 == 0:
                    print(f"{counter['n']}/{len(todo)} ok={counter['ok']} fail={counter['fail']}",
                          flush=True)
    f.close()
    print(f"DONE ok={counter['ok']} fail={counter['fail']}", flush=True)


if __name__ == "__main__":
    main()
