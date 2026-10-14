#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读关键 issue 正文 + 评论，找 20003 的 workaround"""
import time

import requests
import urllib3

urllib3.disable_warnings()
H = {"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github+json"}


def gh(path, **p):
    for i in range(3):
        try:
            r = requests.get(f"https://api.github.com{path}", headers=H,
                             params=p, timeout=30, verify=False)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 403:
                time.sleep(6)
                continue
            return None
        except Exception:
            time.sleep(3)
    return None


TARGETS = [
    ("sumithemmadi/truecallerjs", 165),
    ("sumithemmadi/truecallerjs", 162),
    ("sumithemmadi/truecallerpy", 30),
    ("sumithemmadi/truecallerpy", 42),
]

for repo, num in TARGETS:
    it = gh(f"/repos/{repo}/issues/{num}")
    if not it:
        print(f"\n### {repo}#{num} 读取失败")
        continue
    print("\n" + "=" * 78)
    print(f"### {repo}#{num}  [{it['state']}]  {it['title']}")
    print(f"    by {it['user']['login']}  {it['created_at'][:10]}  comments={it['comments']}")
    print("=" * 78)
    body = (it.get("body") or "").strip()
    print(body[:1200] if body else "(无正文)")

    cs = gh(f"/repos/{repo}/issues/{num}/comments")
    if cs:
        for c in cs[:6]:
            print(f"\n  --- 评论 by {c['user']['login']} {c['created_at'][:10]} ---")
            print("  " + (c.get("body") or "").strip()[:900].replace("\n", "\n  "))
    time.sleep(2)
