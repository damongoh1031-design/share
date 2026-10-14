#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass 1: collect NixOS x AI usage posts from Discourse, HN, GitHub."""
import json, urllib.request, urllib.parse, time, sys, os, re

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
OUT = os.path.dirname(os.path.abspath(__file__))
stats = {}

def get(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            last = e
            time.sleep(3 + i * 3)
    print("  !! FAIL %s -> %s" % (url[:110], last), flush=True)
    return None

def strip_html(s):
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"&quot;", '"', s)
    s = re.sub(r"&#39;", "'", s)
    s = re.sub(r"&amp;", "&", s)
    s = re.sub(r"&lt;", "<", s)
    s = re.sub(r"&gt;", ">", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

# ---------------- Discourse ----------------
DISCOURSE_KW = [
    "llm", "claude", "codex", "chatgpt", "copilot", "gemini", "aider",
    "cline", "cursor", "mcp", "ai agent", "ai assistant", "gpt",
    "deepseek", "ollama", "opencode", "windsurf", "continue dev",
    "vibe coding", "ai nix", "llm nix", "claude code",
]
disco = {}
for kw in DISCOURSE_KW:
    n = 0
    for page in (1, 2, 3):
        url = "https://discourse.nixos.org/search.json?q=%s&page=%d" % (
            urllib.parse.quote(kw), page)
        d = get(url)
        if not d:
            break
        posts = d.get("posts") or []
        if not posts:
            break
        for p in posts:
            pid = p.get("id")
            if pid is None or pid in disco:
                continue
            disco[pid] = {
                "source": "discourse.nixos.org",
                "kind": "post",
                "id": pid,
                "topic_id": p.get("topic_id"),
                "topic_title": p.get("title") or "",
                "topic_slug": p.get("topic_slug"),
                "post_number": p.get("post_number"),
                "author": p.get("username"),
                "created_at": p.get("created_at"),
                "likes": p.get("like_count") or 0,
                "posts_count": p.get("posts_count") or 0,
                "blurb": strip_html(p.get("blurb"))[:900],
                "url": "https://discourse.nixos.org/t/%s/%s/%s" % (
                    p.get("topic_slug"), p.get("topic_id"), p.get("post_number") or 1),
                "matched_kw": kw,
            }
            n += 1
        if len(posts) < 50:
            break
        time.sleep(1.2)
    stats["disco:" + kw] = n
    print("discourse %-14s +%d (total %d)" % (kw, n, len(disco)), flush=True)
    time.sleep(1.0)

# ---------------- Hacker News ----------------
HN_Q = [
    "nixos ai", "nix llm", "nixos agent", "nixos claude", "nix gpt",
    "nixos chatgpt", "nixos copilot", "nix flake ai", "nixos ai coding",
    "nixos llm", "nix ai agent", "nixify ai", "nixos mcp",
]
hn = {}
for q in HN_Q:
    n = 0
    for endpoint in ("search", "search_by_date"):
        url = "https://hn.algolia.com/api/v1/%s?query=%s&hitsPerPage=100" % (
            endpoint, urllib.parse.quote(q))
        d = get(url)
        if not d:
            continue
        for h in d.get("hits") or []:
            oid = h.get("objectID")
            if oid is None or oid in hn:
                continue
            text = strip_html(h.get("story_text") or h.get("comment_text") or "")
            hn[oid] = {
                "source": "news.ycombinator.com",
                "kind": "story" if h.get("_tags") and "story" in h["_tags"] else "comment",
                "id": oid,
                "title": strip_html(h.get("title") or "") or "(comment)",
                "author": h.get("author"),
                "created_at": h.get("created_at"),
                "points": h.get("points") or 0,
                "num_comments": h.get("num_comments") or 0,
                "url": "https://news.ycombinator.com/item?id=%s" % oid,
                "story_url": h.get("url"),
                "text": text[:1200],
                "matched_q": q,
            }
            n += 1
        time.sleep(0.8)
    stats["hn:" + q] = n
    print("hn %-18s +%d (total %d)" % (q, n, len(hn)), flush=True)

# ---------------- GitHub issues / discussions ----------------
GH_Q = [
    "nixos ai agent", "nixos llm", "nix copilot",
]
gh = {}
for q in GH_Q:
    n = 0
    for sort in ("", "&sort=updated"):
        url = "https://api.github.com/search/issues?q=%s&per_page=100%s" % (
            urllib.parse.quote(q), sort)
        d = get(url)
        if not d:
            continue
        for it in d.get("items") or []:
            iid = it.get("id")
            if iid is None or iid in gh:
                continue
            gh[iid] = {
                "source": "github.com",
                "kind": it.get("pull_request") and "pr" or (it.get("html_url", "").find("/discussions/") > 0 and "discussion" or "issue"),
                "id": iid,
                "title": it.get("title") or "",
                "author": (it.get("user") or {}).get("login"),
                "created_at": it.get("created_at"),
                "updated_at": it.get("updated_at"),
                "state": it.get("state"),
                "comments": it.get("comments") or 0,
                "repo": (it.get("repository_url") or "").replace("https://api.github.com/repos/", ""),
                "body": strip_html(it.get("body"))[:700],
                "url": it.get("html_url"),
                "matched_q": q,
            }
            n += 1
        time.sleep(6.5)
    stats["gh:" + q] = n
    print("github %-16s +%d (total %d)" % (q, n, len(gh)), flush=True)

# ---------------- save ----------------
with open(os.path.join(OUT, "raw_discourse.json"), "w", encoding="utf-8") as f:
    json.dump(list(disco.values()), f, ensure_ascii=False, indent=1)
with open(os.path.join(OUT, "raw_hn.json"), "w", encoding="utf-8") as f:
    json.dump(list(hn.values()), f, ensure_ascii=False, indent=1)
with open(os.path.join(OUT, "raw_github.json"), "w", encoding="utf-8") as f:
    json.dump(list(gh.values()), f, ensure_ascii=False, indent=1)

print("\n=== TOTALS ===", flush=True)
print("discourse: %d" % len(disco), flush=True)
print("hn:        %d" % len(hn), flush=True)
print("github:    %d" % len(gh), flush=True)
print("SUM:       %d" % (len(disco) + len(hn) + len(gh)), flush=True)
print("done", flush=True)
