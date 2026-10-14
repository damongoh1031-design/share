#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓 flutter-sdk 的 lib/src/* 与 example 的 OAuth/OTP 相关页面"""
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
            return requests.get(url, timeout=30, verify=False, headers=H)
        except Exception as e:
            if i == tries - 1:
                print(f"  !! {url} -> {e}")
                return None
            time.sleep(2)


def save(name, text):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(text)
    print(f"  saved {name} ({len(text)} chars)")


print("== lib/src/ 目录 ==")
r = get("https://api.github.com/repos/truecaller/flutter-sdk/contents/lib/src")
if r and r.status_code == 200:
    for it in r.json():
        print(f"   {it['type']:<5} {it['size']:>7}  {it['name']}")

print("\n== example/lib/customization/ 目录 ==")
r = get("https://api.github.com/repos/truecaller/flutter-sdk/contents/example/lib/customization")
if r and r.status_code == 200:
    for it in r.json():
        print(f"   {it['type']:<5} {it['size']:>7}  {it['name']}")

print("\n== 抓文件 ==")
targets = [
    ("lib/src/truecaller.dart", "tc__truecaller.dart"),
    ("lib/src/scope_options.dart", "tc__scope_options.dart"),
    ("lib/src/truecaller_callback.dart", "tc__truecaller_callback.dart"),
    ("example/lib/non_tc_screen.dart", "tc__non_tc_screen.dart"),
    ("example/lib/customization/oauth_result_screen.dart", "tc__oauth_result_screen.dart"),
    ("example/lib/customization/config_options.dart", "tc__config_options.dart"),
    ("example/android/app/src/main/AndroidManifest.xml", "tc__AndroidManifest.xml"),
    ("pubspec.yaml", "tc__pubspec.yaml"),
]
for path, name in targets:
    for br in ("main", "master"):
        r = get(f"https://raw.githubusercontent.com/truecaller/flutter-sdk/{br}/{path}")
        if r is not None and r.status_code == 200 and len(r.text) > 30:
            save(name, r.text)
            break
    else:
        print(f"  miss {path}")
print("\ndone")
