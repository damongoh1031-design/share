#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探测 People Data Labs / RocketReach 的 API 端点可用性。
只做「无 key / 假 key」探测 —— 判断端点是否存在、是否强制鉴权。
不进行任何真实人员查询。
"""
import json
import time

import requests
import urllib3

urllib3.disable_warnings()
H = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"),
     "Accept": "application/json, text/plain, */*",
     "Accept-Language": "en-US,en;q=0.9"}


def probe(name, method, url, **kw):
    try:
        r = requests.request(method, url, headers=H, timeout=30, verify=False, **kw)
        body = " ".join((r.text or "").split())[:240]
        print(f"[{r.status_code}] {name}")
        print(f"        {url}")
        if body:
            print(f"        {body}")
        return r.status_code, body
    except Exception as e:
        print(f"[ERR ] {name}  -> {type(e).__name__}: {str(e)[:130]}")
        return None, str(e)


print("#" * 78)
print("# People Data Labs")
print("#" * 78)
probe("person/enrich 无 key", "GET",
      "https://api.peopledatalabs.com/v5/person/enrich?phone=60102261791")
time.sleep(1)
probe("person/enrich 假 key", "GET",
      "https://api.peopledatalabs.com/v5/person/enrich?phone=60102261791",
      headers={**H, "X-Api-Key": "FAKE_KEY_FOR_PROBE"})
time.sleep(1)
probe("person/identify 无 key", "GET",
      "https://api.peopledatalabs.com/v5/person/identify?phone=60102261791")
time.sleep(1)
probe("person/search 无 key", "POST", "https://api.peopledatalabs.com/v5/person/search",
      json={"sql": "SELECT * FROM person WHERE phone='60102261791'"})
time.sleep(1)
probe("company/enrich 无 key", "GET",
      "https://api.peopledatalabs.com/v5/company/enrich?website=maybank.com")
time.sleep(1)
probe("根路径", "GET", "https://api.peopledatalabs.com/")

print()
print("#" * 78)
print("# RocketReach")
print("#" * 78)
time.sleep(1)
probe("person/lookup 无 key", "GET",
      "https://api.rocketreach.co/api/v2/person/lookup?phone=60102261791")
time.sleep(1)
probe("person/lookup 假 key", "GET",
      "https://api.rocketreach.co/api/v2/person/lookup?phone=60102261791",
      headers={**H, "Api-Key": "FAKE_KEY_FOR_PROBE"})
time.sleep(1)
probe("person/search 无 key", "POST", "https://api.rocketreach.co/api/v2/person/search",
      json={"query": {"phone": ["60102261791"]}})
time.sleep(1)
probe("company/lookup 无 key", "GET",
      "https://api.rocketreach.co/api/v2/company/lookup?domain=maybank.com")
time.sleep(1)
probe("account 端点（查额度）", "GET", "https://api.rocketreach.co/api/v2/account")
time.sleep(1)
probe("根路径", "GET", "https://api.rocketreach.co/")
