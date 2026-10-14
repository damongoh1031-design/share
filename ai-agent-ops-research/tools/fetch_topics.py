#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch full Discourse topic JSON for given topic IDs; extract posts."""
import json, urllib.request, time, os, re, sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
OUT = os.path.dirname(os.path.abspath(__file__))

def strip(s):
    if not s:
        return ""
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"</p>", "\n\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    for a, b in (("&quot;", '"'), ("&#39;", "'"), ("&amp;", "&"), ("&lt;", "<"),
                 ("&gt;", ">"), ("&nbsp;", " "), ("&mdash;", "-"), ("&hellip;", "...")):
        s = s.replace(a, b)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def get_topic(tid):
    url = "https://discourse.nixos.org/t/%d.json" % tid
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

ids = [int(x) for x in sys.argv[1:]]
out = []
for tid in ids:
    try:
        d = get_topic(tid)
    except Exception as e:
        print("!! %d -> %s" % (tid, e), flush=True)
        continue
    posts = []
    for p in d.get("post_stream", {}).get("posts", []):
        posts.append({
            "post_number": p.get("post_number"),
            "username": p.get("username"),
            "created_at": p.get("created_at"),
            "like_count": p.get("like_count") or 0,
            "cooked": strip(p.get("cooked"))[:4000],
        })
    rec = {
        "source": "discourse.nixos.org",
        "kind": "topic",
        "topic_id": tid,
        "title": d.get("title"),
        "slug": d.get("slug"),
        "created_at": d.get("created_at"),
        "posts_count": d.get("posts_count"),
        "views": d.get("views"),
        "like_count": d.get("like_count") or 0,
        "category_id": d.get("category_id"),
        "tags": d.get("tags") or [],
        "url": "https://discourse.nixos.org/t/%s/%d" % (d.get("slug"), tid),
        "posts": posts,
    }
    out.append(rec)
    print("OK %-6d posts=%-3d likes=%-3d %s" % (tid, rec["posts_count"], rec["like_count"], (rec["title"] or "")[:70]), flush=True)
    time.sleep(1.5)

fn = os.path.join(OUT, "topics_full.json")
existing = []
if os.path.exists(fn):
    existing = json.load(open(fn, encoding="utf-8"))
have = {r["topic_id"] for r in existing}
existing.extend([r for r in out if r["topic_id"] not in have])
json.dump(existing, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved %d topics total" % len(existing), flush=True)
