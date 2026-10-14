#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓 MalaysianOSINT 的 Readme + src 结构 + 端点定义 + 测公开 demo"""
import json
import re
import time

import requests
import urllib3

urllib3.disable_warnings()
H = {"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github+json"}
RAW = {"User-Agent": "Mozilla/5.0"}
REPO = "ctkqiang/MalaysianOSINT"


def gh(path, **p):
    for i in range(3):
        try:
            r = requests.get(f"https://api.github.com{path}", headers=H, params=p,
                             timeout=30, verify=False)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 403:
                time.sleep(5)
                continue
            return None
        except Exception:
            time.sleep(2)
    return None


def raw(path, br="main"):
    r = requests.get(f"https://raw.githubusercontent.com/{REPO}/{br}/{path}",
                     headers=RAW, timeout=30, verify=False)
    return r.text if r.status_code == 200 else None


print("=" * 78)
print("1) Readme.md")
print("=" * 78)
t = raw("Readme.md")
if t:
    # 去掉徽章行，保留正文
    body = "\n".join(l for l in t.splitlines() if not l.strip().startswith("[!["))
    print(body[:5500])
else:
    print("  未取到")

print()
print("=" * 78)
print("2) src/ 与 include/ 目录")
print("=" * 78)
for d in ("src", "include", "public"):
    items = gh(f"/repos/{REPO}/contents/{d}")
    print(f"\n[{d}/]")
    for it in (items or []):
        print(f"   {it['type']:<5} {it['size']:>8}  {it['name']}")

print()
print("=" * 78)
print("3) 从源码里提取所有外部端点")
print("=" * 78)
srcs = ["my_osint.c"]
for d in ("src",):
    items = gh(f"/repos/{REPO}/contents/{d}") or []
    srcs += [f"{d}/{it['name']}" for it in items if it["name"].endswith((".c", ".h"))]

seen = set()
for s in srcs:
    t = raw(s)
    if not t:
        continue
    urls = set(re.findall(r'https?://[a-zA-Z0-9\.\-/_%\?=&:]+', t))
    urls = {u.rstrip('"\\,;') for u in urls if "truecaller" not in u.lower()}
    if urls:
        print(f"\n--- {s} ({len(t)} chars) ---")
        for u in sorted(urls):
            if u not in seen:
                seen.add(u)
                print(f"   {u}")

print()
print("=" * 78)
print("4) 公开 demo 是否活着")
print("=" * 78)
for name, url in [
    ("demo 页面", "https://www.ctkqiang.xin/MalaysianOSINT/public/myosint.html"),
    ("站点根", "https://www.ctkqiang.xin/"),
]:
    try:
        r = requests.get(url, headers=RAW, timeout=25, verify=False, allow_redirects=True)
        print(f"[{r.status_code}] {name}  final={r.url}  len={len(r.text)}")
    except Exception as e:
        print(f"[ERR ] {name} -> {type(e).__name__}: {str(e)[:110]}")
