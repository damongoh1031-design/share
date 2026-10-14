#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass 1b: collect Reddit / X / Discord / forum posts via DuckDuckGo HTML search."""
import json, urllib.request, urllib.parse, time, os, re, sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
OUT = os.path.dirname(os.path.abspath(__file__))

QUERIES = [
    # --- Reddit r/NixOS ---
    ("reddit", "site:reddit.com/r/NixOS ai"),
    ("reddit", "site:reddit.com/r/NixOS ai agent"),
    ("reddit", "site:reddit.com/r/NixOS llm"),
    ("reddit", "site:reddit.com/r/NixOS claude"),
    ("reddit", "site:reddit.com/r/NixOS chatgpt"),
    ("reddit", "site:reddit.com/r/NixOS codex"),
    ("reddit", "site:reddit.com/r/NixOS copilot"),
    ("reddit", "site:reddit.com/r/NixOS mcp"),
    ("reddit", "site:reddit.com/r/NixOS cursor ai"),
    ("reddit", "site:reddit.com/r/NixOS cline"),
    ("reddit", "site:reddit.com/r/NixOS aider"),
    ("reddit", "site:reddit.com/r/NixOS nix flake ai"),
    ("reddit", "site:reddit.com/r/NixOS ai generated configuration"),
    ("reddit", "site:reddit.com/r/NixOS vibe coding"),
    # --- Reddit r/nix ---
    ("reddit", "site:reddit.com/r/nix ai"),
    ("reddit", "site:reddit.com/r/nix llm"),
    ("reddit", "site:reddit.com/r/nix claude"),
    ("reddit", "site:reddit.com/r/nix gpt"),
    ("reddit", "site:reddit.com/r/nix agent"),
    # --- Reddit other ---
    ("reddit", "site:reddit.com nixos ai server management"),
    ("reddit", "site:reddit.com nix ai packaging"),
    # --- X / Twitter ---
    ("x", "site:x.com nixos ai"),
    ("x", "site:x.com nixos llm"),
    ("x", "site:x.com nixos claude"),
    ("x", "site:x.com nixos agent"),
    ("x", "site:twitter.com nixos ai"),
    ("x", "site:x.com nix flake ai"),
    # --- Discord ---
    ("discord", "site:discord.com nixos ai"),
    ("discord", "site:discord.com nixos llm"),
    ("discord", "site:discord.com nix ai agent"),
    ("discord", "site:discord.com nixos claude"),
    # --- Forums / blogs / misc ---
    ("forum", "nixos ai agent manage server discourse"),
    ("forum", "nixos llm configuration generator"),
    ("forum", "nixos mcp model context protocol"),
    ("forum", "ai agent nixos rebuild rollback"),
]


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def parse_ddg(html):
    out = []
    # split into result blocks
    for m in re.finditer(r'<a rel="nofollow" class="result__a" href="([^"]+)">(.*?)</a>', html, re.S):
        href, title = m.group(1), m.group(2)
        mm = re.search(r"uddg=([^&]+)", href)
        if mm:
            href = urllib.parse.unquote(mm.group(1))
        title = re.sub(r"<[^>]+>", "", title)
        title = title.replace("&amp;", "&").replace("&#x27;", "'").replace("&quot;", '"')
        title = re.sub(r"\s+", " ", title).strip()
        out.append({"url": href, "title": title, "snippet": ""})
    # snippets appear as result__snippet anchors right after
    snips = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.S)
    for i, s in enumerate(snips):
        if i < len(out):
            s = re.sub(r"<[^>]+>", "", s)
            s = s.replace("&amp;", "&").replace("&#x27;", "'").replace("&quot;", '"')
            out[i]["snippet"] = re.sub(r"\s+", " ", s).strip()[:700]
    return out


results = {}
per_source = {}
for kind, q in QUERIES:
    got = 0
    for offset in (0, 30, 60):
        url = "https://html.duckduckgo.com/html/?q=%s&s=%d" % (urllib.parse.quote(q), offset)
        try:
            html = fetch(url)
        except Exception as e:
            print("  !! %s off=%d -> %s" % (q, offset, e), flush=True)
            break
        rows = parse_ddg(html)
        if not rows:
            break
        for r in rows:
            key = r["url"].split("?")[0].rstrip("/")
            if not key or key in results:
                continue
            r["kind_tag"] = kind
            r["query"] = q
            results[key] = r
            got += 1
        if len(rows) < 10:
            break
        time.sleep(2.0)
    per_source["%s | %s" % (kind, q)] = got
    print("[%-7s] %-52s +%d (total %d)" % (kind, q[:52], got, len(results)), flush=True)
    time.sleep(1.5)

with open(os.path.join(OUT, "raw_search.json"), "w", encoding="utf-8") as f:
    json.dump(list(results.values()), f, ensure_ascii=False, indent=1)

print("\n=== DDG TOTAL: %d ===" % len(results), flush=True)
print("done", flush=True)
