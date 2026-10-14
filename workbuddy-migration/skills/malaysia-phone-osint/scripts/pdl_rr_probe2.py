#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDL / RocketReach 第二轮：补「假 key」对照组 + 测试 key 线索挖掘。

方法论（本项目 4.2 节）：
  无 key  → 401  ⇒ 端点存在且强制鉴权
  假 key  → 401  ⇒ 端点不区分凭据有效性（只看有没有）
  假 key  → 401 带 "invalid api key" ⇒ 端点会校验凭据真实性
两者差异决定了「能不能用别人的 key」「有没有匿名口子」。
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


def probe(name, method, url, headers=None, **kw):
    """headers 显式收，内部合并 —— 修上一版 'multiple values for headers' bug"""
    try:
        r = requests.request(method, url, headers={**H, **(headers or {})},
                             timeout=30, verify=False, **kw)
        body = " ".join((r.text or "").split())[:300]
        print(f"[{r.status_code}] {name}")
        if body:
            print(f"        {body}")
        return r.status_code, body
    except Exception as e:
        print(f"[ERR ] {name}  -> {type(e).__name__}: {str(e)[:150]}")
        return None, str(e)


print("#" * 78)
print("# A. PDL —— 假 key 对照（关键组）")
print("#" * 78)
probe("PDL person/enrich 假 key", "GET",
      "https://api.peopledatalabs.com/v5/person/enrich?phone=60102261791",
      headers={"X-Api-Key": "FAKE_KEY_FOR_PROBE_12345"})
time.sleep(1)
probe("PDL person/enrich 空 key", "GET",
      "https://api.peopledatalabs.com/v5/person/enrich?phone=60102261791",
      headers={"X-Api-Key": ""})
time.sleep(1)
probe("PDL person/enrich 格式合法假 key", "GET",
      "https://api.peopledatalabs.com/v5/person/enrich?phone=60102261791",
      headers={"X-Api-Key": "a" * 40})

print()
print("#" * 78)
print("# B. RocketReach —— 假 key 对照 + test key 线索")
print("#" * 78)
time.sleep(1)
probe("RR person/lookup 假 key", "GET",
      "https://api.rocketreach.co/api/v2/person/lookup?phone=60102261791",
      headers={"Api-Key": "FAKE_KEY_FOR_PROBE_12345"})
time.sleep(1)
probe("RR person/lookup 空 key", "GET",
      "https://api.rocketreach.co/api/v2/person/lookup?phone=60102261791",
      headers={"Api-Key": ""})
time.sleep(1)
# RocketReach 报错里点名 "test API key" —— 试探常见文档用的 test key
for tk in ["test", "TEST_API_KEY", "test_api_key", "demo"]:
    probe(f"RR person/lookup test key='{tk}'", "GET",
          "https://api.rocketreach.co/api/v2/person/lookup?phone=60102261791",
          headers={"Api-Key": tk})
    time.sleep(1)

print()
print("#" * 78)
print("# C. 覆盖能力线索 —— 参数校验错误能否泄露 schema")
print("#" * 78)
time.sleep(1)
probe("PDL person/enrich 带假key+乱参数", "GET",
      "https://api.peopledatalabs.com/v5/person/enrich?foo=bar",
      headers={"X-Api-Key": "a" * 40})
time.sleep(1)
probe("RR person/lookup 带假key+乱参数", "GET",
      "https://api.rocketreach.co/api/v2/person/lookup?foo=bar",
      headers={"Api-Key": "a" * 40})
