#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓 github.com/truecaller/flutter-sdk 的实际 Dart API 代码 + 官方文档站"""
import json
import os
import time

import requests
import urllib3

urllib3.disable_warnings()

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetched")
os.makedirs(OUT, exist_ok=True)

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def get(url, tries=3):
    for i in range(tries):
        try:
            r = requests.get(url, timeout=30, verify=False, headers=H)
            return r
        except Exception as e:
            if i == tries - 1:
                print(f"  !! {url} -> {e}")
                return None
            time.sleep(2 * (i + 1))
    return None


def save(name, text):
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"  saved {name} ({len(text)} chars)")
    return p


print("=" * 70)
print("1) 列出 flutter-sdk 仓库根目录 + lib/ + example/lib/")
print("=" * 70)
for path in ("", "lib", "example", "example/lib", "android/app/src/main", "example/android/app/src/main"):
    url = f"https://api.github.com/repos/truecaller/flutter-sdk/contents/{path}"
    r = get(url)
    if r is None or r.status_code != 200:
        print(f"  [{path or '/'}] HTTP {r.status_code if r else 'ERR'}")
        continue
    try:
        items = r.json()
    except Exception:
        print(f"  [{path or '/'}] 非 JSON")
        continue
    print(f"  [{path or '/'}]")
    for it in items:
        print(f"     {it['type']:<5} {it['size']:>7}  {it['name']}")

print()
print("=" * 70)
print("2) 抓关键源码文件")
print("=" * 70)
targets = [
    ("lib/truecaller_sdk.dart", "truecaller_flutter-sdk__lib__truecaller_sdk.dart"),
    ("lib/truecaller_sdk_method_channel.dart", "truecaller_flutter-sdk__lib__method_channel.dart"),
    ("example/lib/main.dart", "truecaller_flutter-sdk__example__main.dart"),
    ("example/lib/screens/login_screen.dart", "truecaller_flutter-sdk__example__login_screen.dart"),
    ("CHANGELOG.md", "truecaller_flutter-sdk__CHANGELOG.md"),
]
for path, name in targets:
    for br in ("main", "master"):
        url = f"https://raw.githubusercontent.com/truecaller/flutter-sdk/{br}/{path}"
        r = get(url)
        if r is not None and r.status_code == 200 and len(r.text) > 50:
            save(name, r.text)
            break
    else:
        print(f"  miss {path}")

print()
print("=" * 70)
print("3) 抓官方文档站（多路径试探）")
print("=" * 70)
docs = [
    ("https://docs.truecaller.com/truecaller-sdk/android/oauth-sdk-3.0/introduction", "docs__oauth_sdk_intro.html"),
    ("https://docs.truecaller.com/truecaller-sdk/android/oauth-sdk-3.0/getting-started", "docs__oauth_sdk_start.html"),
    ("https://developer.truecaller.com/", "docs__dev_home.html"),
    ("https://sdk-console-noneu.truecaller.com/", "docs__sdk_console.html"),
    ("https://docs.truecaller.com/", "docs__docs_home.html"),
]
for url, name in docs:
    r = get(url)
    if r is None:
        continue
    print(f"  HTTP {r.status_code}  len={len(r.text)}  {url}")
    if r.status_code == 200 and len(r.text) > 200:
        save(name, r.text)

print("\ndone")
