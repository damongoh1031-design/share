#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""确认替代路径：Truecaller Web 版是否可用（PR#157 提到的 installationId 来源）"""
import requests
import urllib3

urllib3.disable_warnings()
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
     "Accept": "text/html,application/xhtml+xml"}

TARGETS = [
    ("web.truecaller.com", "https://web.truecaller.com/"),
    ("web.truecaller.com/home", "https://web.truecaller.com/home"),
    ("www.truecaller.com", "https://www.truecaller.com/"),
]

for name, url in TARGETS:
    try:
        r = requests.get(url, headers=H, timeout=30, verify=False, allow_redirects=True)
        loc = r.headers.get("location", "")
        title = ""
        low = r.text.lower()
        for k in ("<title>",):
            if k in low:
                i = low.index(k)
                title = r.text[i + 7:i + 120].split("<")[0].strip()
        print(f"[{r.status_code}] {name}")
        print(f"      final_url = {r.url}")
        if loc:
            print(f"      location  = {loc}")
        if title:
            print(f"      title     = {title}")
        print(f"      len       = {len(r.text)}")
        # 探测是否是登录页 / SPA
        for kw in ("login", "signin", "sign-in", "otp", "phone"):
            if kw in low:
                print(f"      contains  : {kw}")
                break
    except Exception as e:
        print(f"[ERR ] {name} -> {type(e).__name__}: {str(e)[:100]}")
    print()
