#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""排查 20003：查两个仓库的 issue + 最后提交时间 + 库里的伪造版本号"""
import json
import time

import requests
import urllib3

urllib3.disable_warnings()
H = {"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github+json"}
API = "https://api.github.com"


def gh(path, **params):
    for i in range(3):
        try:
            r = requests.get(f"{API}{path}", headers=H, params=params,
                             timeout=30, verify=False)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 403:
                time.sleep(5)
                continue
            print(f"   HTTP {r.status_code} {path} :: {r.text[:150]}")
            return None
        except Exception as e:
            if i == 2:
                print(f"   ERR {path} :: {e}")
                return None
            time.sleep(3)


print("=" * 78)
print("1) 两个仓库的最后提交时间（判断是否还在维护）")
print("=" * 78)
for repo in ("sumithemmadi/truecallerpy", "sumithemmadi/truecallerjs"):
    cs = gh(f"/repos/{repo}/commits", per_page=5)
    info = gh(f"/repos/{repo}")
    if info:
        print(f"\n{repo}")
        print(f"   ★ {info.get('stargazers_count')}  | 最后推送 {info.get('pushed_at','')[:10]}"
              f"  | open issues {info.get('open_issues_count')}")
    if cs:
        for c in cs[:5]:
            d = c["commit"]["author"]["date"][:10]
            m = c["commit"]["message"].splitlines()[0][:70]
            print(f"   {d}  {m}")

print()
print("=" * 78)
print("2) 搜 20003 / Verification failed 相关 issue")
print("=" * 78)
for repo in ("sumithemmadi/truecallerpy", "sumithemmadi/truecallerjs"):
    for q in ("20003", "Verification failed", "sendOnboardingOtp", "not working"):
        d = gh("/search/issues", q=f'repo:{repo} {q}')
        if not d:
            continue
        n = d.get("total_count", 0)
        print(f"\n[{repo}] '{q}' -> {n} 条")
        for it in (d.get("items") or [])[:6]:
            print(f"   #{it['number']} [{it['state']}] {it['title'][:95]}")
        time.sleep(2)

print()
print("=" * 78)
print("3) 库里伪造的客户端指纹 vs 当前真实版本")
print("=" * 78)
print("""
库（truecallerpy v1.0.3 / truecallerjs）伪造:
   user-agent  : Truecaller/11.75.5 (Android;10)
   app         : buildVersion=5, majorVersion=11, minorVersion=7, store=GOOGLE_PLAY
   device.os   : Android 10
Google Play 实测当前版本: 14.x / 15.x  (抓到 14.43.8 / 15.3.10)
→ 伪造指纹落后 3-4 个大版本
""")
