#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下载 issue 里的截图 + 读 truecallerjs#157（标题含 API Fixes）"""
import os
import time

import requests
import urllib3

urllib3.disable_warnings()
H = {"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github+json"}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetched")
os.makedirs(OUT, exist_ok=True)

print("=" * 78)
print("1) 读 truecallerjs#157 (Maintenance: ... API Fixes ...)")
print("=" * 78)
it = requests.get("https://api.github.com/repos/sumithemmadi/truecallerjs/issues/157",
                  headers=H, timeout=30, verify=False).json()
print(f"[{it.get('state')}] {it.get('title')}  by {it.get('user',{}).get('login')} {str(it.get('created_at'))[:10]}")
print("-" * 78)
print((it.get("body") or "(无正文)")[:3000])
cs = requests.get("https://api.github.com/repos/sumithemmadi/truecallerjs/issues/157/comments",
                  headers=H, timeout=30, verify=False).json()
for c in (cs or [])[:5]:
    print(f"\n--- 评论 {c['user']['login']} {c['created_at'][:10]} ---")
    print((c.get("body") or "")[:1200])
time.sleep(1)

print()
print("=" * 78)
print("2) 下载 truecallerpy#42 的两张截图")
print("=" * 78)
imgs = {
    "issue42_tests.png": "https://github.com/user-attachments/assets/6b43095e-a6f9-4347-a49c-86a2019c1d04",
    "issue42_postman.png": "https://github.com/user-attachments/assets/75c93e1c-6e4e-4cbf-a06e-d6a0c7e279c5",
}
for name, url in imgs.items():
    try:
        r = requests.get(url, headers=H, timeout=45, verify=False, allow_redirects=True)
        ct = r.headers.get("content-type", "")
        p = os.path.join(OUT, name)
        if r.status_code == 200 and "image" in ct:
            with open(p, "wb") as f:
                f.write(r.content)
            print(f"  ✅ {name}  {len(r.content)} bytes  ({ct})")
        else:
            print(f"  ❌ {name}  HTTP {r.status_code}  ct={ct}")
    except Exception as e:
        print(f"  ❌ {name}  {type(e).__name__}: {e}")
