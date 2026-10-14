#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓 ctkqiang/MalaysianOSINT 仓库现状：元数据 + 文件树 + README"""
import time

import requests
import urllib3

urllib3.disable_warnings()
H = {"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github+json"}
API = "https://api.github.com"


def gh(path, **p):
    for i in range(3):
        try:
            r = requests.get(f"{API}{path}", headers=H, params=p, timeout=30, verify=False)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 403:
                time.sleep(5)
                continue
            print(f"  HTTP {r.status_code} {path}: {r.text[:120]}")
            return None
        except Exception as e:
            if i == 2:
                print(f"  ERR {path}: {e}")
                return None
            time.sleep(2)


REPO = "ctkqiang/MalaysianOSINT"

print("=" * 78)
print("1) 仓库元数据")
print("=" * 78)
info = gh(f"/repos/{REPO}")
if info:
    for k in ("full_name", "description", "language", "stargazers_count", "forks_count",
              "open_issues_count", "created_at", "pushed_at", "updated_at", "license",
              "archived", "default_branch", "topics", "homepage"):
        v = info.get(k)
        if isinstance(v, dict):
            v = v.get("spdx_id") or v.get("name")
        print(f"  {k:<20} {v}")
else:
    print("  取不到仓库信息")
    raise SystemExit(1)

print()
print("=" * 78)
print("2) 最近提交（判断是否还在维护）")
print("=" * 78)
cs = gh(f"/repos/{REPO}/commits", per_page=8)
for c in (cs or []):
    print(f"  {c['commit']['author']['date'][:10]}  {c['commit']['message'].splitlines()[0][:72]}")

print()
print("=" * 78)
print("3) 文件树（根目录）")
print("=" * 78)
items = gh(f"/repos/{REPO}/contents/")
for it in (items or []):
    print(f"  {it['type']:<5} {it['size']:>8}  {it['name']}")

print()
print("=" * 78)
print("4) README")
print("=" * 78)
for br in (info.get("default_branch", "main"), "main", "master"):
    r = requests.get(f"https://raw.githubusercontent.com/{REPO}/{br}/README.md",
                     headers=H, timeout=30, verify=False)
    if r.status_code == 200 and len(r.text) > 100:
        print(r.text[:7000])
        break
else:
    print("  README 未取到")
