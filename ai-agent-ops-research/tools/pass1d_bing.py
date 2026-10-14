#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass 1d: Bing HTML search collector (robust b_algo parser) + Startpage fallback."""
import json, urllib.request, urllib.parse, time, os, re, random

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
OUT = os.path.dirname(os.path.abspath(__file__))


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.bing.com/",
    })
    with urllib.request.urlopen(req, timeout=35) as r:
        return r.read().decode("utf-8", "replace")


def clean(t):
    t = re.sub(r"<[^>]+>", "", t)
    for a, b in (("&amp;", "&"), ("&#x27;", "'"), ("&#39;", "'"), ("&quot;", '"'),
                 ("&lt;", "<"), ("&gt;", ">"), ("&nbsp;", " "), ("&raquo;", ")")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()


def parse_bing(html):
    """Split on b_algo blocks, extract first <h2> anchor + first paragraph."""
    rows = []
    blocks = re.split(r'class="b_algo"', html)[1:]
    for b in blocks:
        m = re.search(r"<h2[^>]*>\s*<a[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", b, re.S)
        if not m:
            continue
        url = m.group(1)
        if not url.startswith("http"):
            continue
        title = clean(m.group(2))
        sm = re.search(r"<p[^>]*>(.*?)</p>", b, re.S)
        snip = clean(sm.group(1))[:700] if sm else ""
        rows.append({"url": url, "title": title, "snippet": snip})
    return rows


QUERIES = [
    ("reddit", "site:reddit.com/r/NixOS ai"),
    ("reddit", "site:reddit.com/r/NixOS ai agent"),
    ("reddit", "site:reddit.com/r/NixOS llm"),
    ("reddit", "site:reddit.com/r/NixOS claude"),
    ("reddit", "site:reddit.com/r/NixOS chatgpt"),
    ("reddit", "site:reddit.com/r/NixOS codex"),
    ("reddit", "site:reddit.com/r/NixOS copilot"),
    ("reddit", "site:reddit.com/r/NixOS mcp"),
    ("reddit", "site:reddit.com/r/NixOS cursor"),
    ("reddit", "site:reddit.com/r/NixOS cline"),
    ("reddit", "site:reddit.com/r/NixOS aider"),
    ("reddit", "site:reddit.com/r/NixOS nix flake ai"),
    ("reddit", "site:reddit.com/r/NixOS vibe coding"),
    ("reddit", "site:reddit.com/r/NixOS ai configuration"),
    ("reddit", "site:reddit.com/r/NixOS nixos-rebuild"),
    ("reddit", "site:reddit.com/r/nix ai"),
    ("reddit", "site:reddit.com/r/nix llm"),
    ("reddit", "site:reddit.com/r/nix claude"),
    ("reddit", "site:reddit.com/r/nix agent"),
    ("reddit", "site:reddit.com/r/nix chatgpt"),
    ("reddit", "site:reddit.com/r/nix flake"),
    ("reddit", "site:reddit.com nixos ai server agent"),
    ("reddit", "site:reddit.com nix ai packaging nixpkgs"),
    ("x", "site:x.com nixos ai"),
    ("x", "site:x.com nixos llm"),
    ("x", "site:x.com nixos claude"),
    ("x", "site:x.com nixos agent"),
    ("x", "site:twitter.com nixos ai"),
    ("x", "site:x.com nix flake"),
    ("discord", "site:discord.com nixos ai"),
    ("discord", "site:discord.com nixos llm"),
    ("discord", "site:discord.com/channels nixos ai"),
    ("forum", "nixos ai agent manage server experience"),
    ("forum", "nixos mcp model context protocol"),
    ("forum", "nixos claude code ssh experience"),
    ("forum", "nixos ai rebuild rollback generation"),
]

results = {}
srch = os.path.join(OUT, "raw_search.json")
if os.path.exists(srch):
    for r in json.load(open(srch, encoding="utf-8")):
        results[r["url"].split("?")[0].rstrip("/")] = r

for i, (kind, q) in enumerate(QUERIES):
    added = 0
    for first in (1, 11, 21, 31, 41, 51):
        url = "https://www.bing.com/search?q=%s&count=10&first=%d" % (urllib.parse.quote(q), first)
        try:
            html = fetch(url)
        except Exception as e:
            print("  !! %s first=%d -> %s" % (q[:40], first, str(e)[:50]), flush=True)
            break
        rows = parse_bing(html)
        if not rows:
            break
        a = 0
        for r in rows:
            key = r["url"].split("?")[0].rstrip("/")
            if not key or key in results:
                continue
            r["kind_tag"] = kind
            r["query"] = q
            r["engine"] = "bing"
            results[key] = r
            a += 1
        added += a
        if a == 0:
            break
        time.sleep(2.0 + random.random() * 1.5)
    print("[%02d][%-7s] %-46s +%d (total %d)" % (i + 1, kind, q[:46], added, len(results)), flush=True)
    time.sleep(1.5 + random.random() * 1.5)

json.dump(list(results.values()), open(srch, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n=== SEARCH TOTAL: %d ===" % len(results), flush=True)
print("done", flush=True)
