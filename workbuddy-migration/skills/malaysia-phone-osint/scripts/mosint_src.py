#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓 src/pdrm.c 等源文件，看原项目真实的请求参数名"""
import os
import re
import time

import requests
import urllib3

urllib3.disable_warnings()
H = {"User-Agent": "Mozilla/5.0"}
REPO = "ctkqiang/MalaysianOSINT"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetched")
os.makedirs(OUT, exist_ok=True)


def raw(path):
    for br in ("main", "master"):
        for i in range(2):
            try:
                r = requests.get(f"https://raw.githubusercontent.com/{REPO}/{br}/{path}",
                                 headers=H, timeout=30, verify=False)
                if r.status_code == 200:
                    return r.text
            except Exception:
                time.sleep(2)
    return None


for f in ("pdrm.c", "sspi.c", "sprm.c", "ecourt.c", "bnm.c", "company.c", "ssm.c", "rmp_wanted.c"):
    t = raw(f"src/{f}")
    if not t:
        print(f"  miss src/{f}")
        continue
    with open(os.path.join(OUT, f"mosint__{f}"), "w", encoding="utf-8") as fh:
        fh.write(t)
    print(f"  saved src/{f}  ({len(t)} chars)")

print()
print("=" * 78)
print("pdrm.c 里的 POST body 构造")
print("=" * 78)
t = raw("src/pdrm.c") or ""
# 找 postfields / json 构造 / 参数名
for pat, tag in [
    (r'POSTFIELDS[^\n]*', "POSTFIELDS"),
    (r'"[a-z_]+"\s*:\s*"[^"]*"', "JSON 键值"),
    (r'curl_easy_setopt[^\n]*CURLOPT_URL[^\n]*', "URL"),
    (r'Content-Type[^\n]*', "Content-Type"),
    (r'snprintf\([^;]*body[^;]*;', "body 构造"),
]:
    for m in re.finditer(pat, t, re.I):
        print(f"  [{tag}] {m.group(0).strip()[:170]}")

print()
print("=" * 78)
print("全部源码里出现的「请求体参数名」候选")
print("=" * 78)
allkeys = set()
for f in ("pdrm.c", "sspi.c", "sprm.c", "ecourt.c", "bnm.c", "ssm.c"):
    tt = raw(f"src/{f}")
    if not tt:
        continue
    for m in re.finditer(r'"([a-zA-Z_]{2,20})"\s*[,:]\s*', tt):
        allkeys.add(m.group(1))
print("  ", sorted(k for k in allkeys if k.lower() not in
                   {"true", "false", "null", "utf-8", "application/json",
                    "content-type", "get", "post", "user-agent"}))
