#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass 1b v2: multi-engine HTML search collector (DDG / Bing / Mojeek)."""
import json, urllib.request, urllib.parse, time, os, re, sys, random

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
OUT = os.path.dirname(os.path.abspath(__file__))
DEBUG = os.path.join(OUT, "dbg")
os.makedirs(DEBUG, exist_ok=True)


def fetch(url, ref=None):
    h = {"User-Agent": UA,
         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
         "Accept-Language": "en-US,en;q=0.9"}
    if ref:
        h["Referer"] = ref
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=35) as r:
        return r.read().decode("utf-8", "replace")


def clean(t):
    t = re.sub(r"<[^>]+>", "", t)
    for a, b in (("&amp;", "&"), ("&#x27;", "'"), ("&#39;", "'"), ("&quot;", '"'),
                 ("&lt;", "<"), ("&gt;", ">"), ("&#x2F;", "/"), ("&nbsp;", " ")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()


def parse_ddg(html):
    rows = []
    for m in re.finditer(r'class="result__a"\s+href="([^"]+)"[^>]*>(.*?)</a>', html, re.S):
        href = m.group(1)
        mm = re.search(r"uddg=([^&]+)", href)
        if mm:
            href = urllib.parse.unquote(mm.group(1))
        rows.append({"url": href, "title": clean(m.group(2))})
    for m in re.finditer(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.S):
        pass
    snips = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|div)>', html, re.S)
    for i, s in enumerate(snips):
        if i < len(rows):
            rows[i]["snippet"] = clean(s)[:700]
    return rows


def parse_bing(html):
    rows = []
    for m in re.finditer(r'<h2><a href="(http[^"]+)"[^>]*>(.*?)</a></h2>', html, re.S):
        rows.append({"url": m.group(1), "title": clean(m.group(2))})
    snips = re.findall(r'<p class="b_lineclamp[^"]*"[^>]*>(.*?)</p>', html, re.S)
    for i, s in enumerate(snips):
        if i < len(rows):
            rows[i]["snippet"] = clean(s)[:700]
    return rows


def parse_mojeek(html):
    rows = []
    for m in re.finditer(r'<a class="ob"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.S):
        rows.append({"url": m.group(1), "title": clean(m.group(2))})
    snips = re.findall(r'<p class="s">(.*?)</p>', html, re.S)
    for i, s in enumerate(snips):
        if i < len(rows):
            rows[i]["snippet"] = clean(s)[:700]
    return rows


ENGINES = [
    ("ddg", lambda q, off: "https://html.duckduckgo.com/html/?q=%s&s=%d" % (urllib.parse.quote(q), off), parse_ddg, 30),
    ("bing", lambda q, off: "https://www.bing.com/search?q=%s&count=30&first=%d" % (urllib.parse.quote(q), off + 1), parse_bing, 30),
    ("mojeek", lambda q, off: "https://www.mojeek.com/search?q=%s&s=%d" % (urllib.parse.quote(q), off), parse_mojeek, 10),
]

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
    ("reddit", "site:reddit.com/r/NixOS cline aider"),
    ("reddit", "site:reddit.com/r/NixOS nix flake ai"),
    ("reddit", "site:reddit.com/r/NixOS vibe coding"),
    ("reddit", "site:reddit.com/r/nix ai"),
    ("reddit", "site:reddit.com/r/nix llm"),
    ("reddit", "site:reddit.com/r/nix claude"),
    ("reddit", "site:reddit.com/r/nix agent"),
    ("reddit", "site:reddit.com/r/nix chatgpt"),
    ("reddit", "site:reddit.com nixos ai server"),
    ("x", "site:x.com nixos ai"),
    ("x", "site:x.com nixos llm"),
    ("x", "site:x.com nixos claude code"),
    ("x", "site:x.com nixos agent"),
    ("x", "site:twitter.com nixos ai llm"),
    ("x", "site:x.com nix flake ai"),
    ("discord", "site:discord.com nixos ai"),
    ("discord", "site:discord.com nixos llm agent"),
    ("discord", "site:discord.com/channels nixos ai"),
    ("forum", "nixos ai agent manage server"),
    ("forum", "nixos mcp model context protocol"),
    ("forum", "ai agent nixos rebuild rollback"),
    ("forum", "nixos llm configuration generator"),
    ("forum", "nixos claude code ssh experience"),
]

results = {}
if os.path.exists(os.path.join(OUT, "raw_search.json")):
    for r in json.load(open(os.path.join(OUT, "raw_search.json"), encoding="utf-8")):
        results[r["url"].split("?")[0].rstrip("/")] = r

qi = 0
for kind, q in QUERIES:
    qi += 1
    total_added = 0
    for ename, mk, parser, per in ENGINES:
        for off in (0, per, per * 2):
            try:
                html = fetch(mk(q, off))
            except Exception as e:
                print("  !! [%s] %s off=%d -> %s" % (ename, q[:40], off, str(e)[:60]), flush=True)
                break
            open(os.path.join(DEBUG, "%02d_%s_%d.html" % (qi, ename, off)), "w", encoding="utf-8").write(html)
            rows = parser(html)
            if not rows:
                break
            added = 0
            for r in rows:
                if not r["url"].startswith("http"):
                    continue
                key = r["url"].split("?")[0].rstrip("/")
                if not key or key in results:
                    continue
                r["kind_tag"] = kind
                r["query"] = q
                r["engine"] = ename
                r.setdefault("snippet", "")
                results[key] = r
                added += 1
            total_added += added
            if len(rows) < per // 2:
                break
            time.sleep(2.5 + random.random() * 1.5)
        time.sleep(2.0 + random.random() * 2.0)
    print("[%02d][%-7s] %-46s +%d (total %d)" % (qi, kind, q[:46], total_added, len(results)), flush=True)

with open(os.path.join(OUT, "raw_search.json"), "w", encoding="utf-8") as f:
    json.dump(list(results.values()), f, ensure_ascii=False, indent=1)
print("\n=== SEARCH TOTAL: %d ===" % len(results), flush=True)
print("done", flush=True)
