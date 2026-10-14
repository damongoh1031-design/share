#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用原项目的【正确请求格式】重测 Semak Mule。

从源码读出（my_osint.c:289-294 + pdrm.c:78,103-106）：
  POST https://semakmule.rmp.gov.my/api/mule/get_search_data.php
  Header: Content-Type: application/json
          Origin: https://semakmule.rmp.gov.my
          Referer: https://semakmule.rmp.gov.my/
          apikey: j3j389#nklala2          <-- 关键，我上次漏了
  Body:   {"data":{"category":"telefon","bankAccount":"<q>","telNo":"<q>",
                   "companyName":"","captcha":""}}
"""
import json
import time

import requests
import urllib3

urllib3.disable_warnings()

URL = "https://semakmule.rmp.gov.my/api/mule/get_search_data.php"
APIKEY = "j3j389#nklala2"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 QQBrowser/19.5.5.207")

H = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": "https://semakmule.rmp.gov.my",
    "Referer": "https://semakmule.rmp.gov.my/",
    "User-Agent": UA,
    "apikey": APIKEY,
    "sec-ch-ua": '"Chromium";v="123", "Not:A-Brand";v="8"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}


def query(q, category="telefon"):
    body = {"data": {"category": category, "bankAccount": q, "telNo": q,
                     "companyName": "", "captcha": ""}}
    try:
        r = requests.post(URL, json=body, headers=H, timeout=35, verify=False)
        return r.status_code, r.json()
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:110]}"


print("#" * 78)
print("# Semak Mule 重测（用原项目的正确 apikey + body 结构）")
print("#" * 78)

CASES = [
    ("电话（示例号）", "0123456789", "telefon"),
    ("电话（国际格式）", "60123456789", "telefon"),
    ("电话（本地 10 位）", "0123456789", "telefon"),
    ("银行账户", "1234567890123", "akaun"),
    ("银行账户(telefon 类)", "1234567890123", "telefon"),
]

for label, q, cat in CASES:
    code, d = query(q, cat)
    print(f"\n{'='*78}\n### {label}   q={q}  category={cat}")
    print(f"{'='*78}")
    if isinstance(d, dict):
        print(f"HTTP {code}")
        print(json.dumps(d, ensure_ascii=False, indent=2)[:900])
    else:
        print(f"HTTP {code}  {d}")
    time.sleep(1.5)

print()
print("#" * 78)
print("# 对照：不带 apikey（验证 apikey 是否必需）")
print("#" * 78)
H2 = {k: v for k, v in H.items() if k != "apikey"}
body = {"data": {"category": "telefon", "bankAccount": "0123456789",
                 "telNo": "0123456789", "companyName": "", "captcha": ""}}
try:
    r = requests.post(URL, json=body, headers=H2, timeout=35, verify=False)
    print(f"HTTP {r.status_code}")
    print(json.dumps(r.json(), ensure_ascii=False, indent=2)[:600])
except Exception as e:
    print(f"ERR {type(e).__name__}: {str(e)[:110]}")
