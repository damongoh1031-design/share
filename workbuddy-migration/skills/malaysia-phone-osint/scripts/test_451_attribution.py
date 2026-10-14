#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【关键更正实验】钉死 451 的归因。

之前的结论「451 是端点级地域策略」可能是错的：
  - 本轮新测：search5-noneu + 假 Bearer -> 401（端点可达！）
  - 历史测：  search5-noneu + 硬编码真 token -> 451

必须隔离 4 个变量，找出 451 到底由什么触发：
  ① 端点 (eu / noneu)
  ② token (无 / 假 / 硬编码 TC_KEY)
  ③ URL 参数集（历史用的「完整参数」 vs 本轮「精简参数」）
  ④ User-Agent
"""
import json
import time

import requests
import urllib3

urllib3.disable_warnings()

TC_KEY = "a1i1V--ua298eldF0hb0rL520GjDz7bzVAdt63J2nzZBnWlEKNCJUeln_7kWj4Ir"
UA_TC = "Truecaller/9.00.3 (Android;10)"
UA_TC_JS = "Truecaller/11.75.5 (Android;10)"

Q = "60197527397"
CC = "MY"

# 历史脚本 test_apis2.py 用的「完整参数」
PARAMS_FULL = (f"q={Q}&countryCode={CC}&type=4"
               f"&locAddr=&placement=SEARCHRESULTS,HISTORY,DETAILS&adId=&encoding=json")
# 本轮 test_oauth_endpoints.py 用的「精简参数」
PARAMS_MIN = f"q={Q}&countryCode={CC}&type=4&encoding=json"


def call(host, params, auth, ua):
    url = f"https://{host}/v2/search?{params}"
    h = {"User-Agent": ua, "content-type": "application/json; charset=UTF-8",
         "accept-encoding": "gzip"}
    if auth:
        h["Authorization"] = f"Bearer {auth}"
    try:
        r = requests.get(url, headers=h, timeout=25, verify=False)
        body = " ".join((r.text or "").split())[:170]
        return r.status_code, body
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:100]}"


CASES = [
    # ① 无 token，两种参数集
    ("noneu / 无token / 完整参数", "search5-noneu.truecaller.com", PARAMS_FULL, None, UA_TC),
    ("noneu / 无token / 精简参数", "search5-noneu.truecaller.com", PARAMS_MIN, None, UA_TC),
    # ② 假 token
    ("noneu / 假token / 完整参数", "search5-noneu.truecaller.com", PARAMS_FULL, "FAKE_TOKEN", UA_TC),
    ("noneu / 假token / 精简参数", "search5-noneu.truecaller.com", PARAMS_MIN, "FAKE_TOKEN", UA_TC),
    # ③ 硬编码 TC_KEY —— 完整参数（复现历史 451）
    ("noneu / TC_KEY / 完整参数", "search5-noneu.truecaller.com", PARAMS_FULL, TC_KEY, UA_TC),
    # ④ 硬编码 TC_KEY —— 精简参数（隔离参数集变量）
    ("noneu / TC_KEY / 精简参数", "search5-noneu.truecaller.com", PARAMS_MIN, TC_KEY, UA_TC),
    # ⑤ 同一 token 换 UA
    ("noneu / TC_KEY / 完整参数 / UA=11.75", "search5-noneu.truecaller.com", PARAMS_FULL, TC_KEY, UA_TC_JS),
    # ⑥ 对照：EU 端点同条件
    ("eu    / TC_KEY / 完整参数", "search5-eu.truecaller.com", PARAMS_FULL, TC_KEY, UA_TC),
    ("eu    / TC_KEY / 精简参数", "search5-eu.truecaller.com", PARAMS_MIN, TC_KEY, UA_TC),
    ("eu    / 假token / 完整参数", "search5-eu.truecaller.com", PARAMS_FULL, "FAKE_TOKEN", UA_TC),
]

rows = []
print(f"{'用例':<38} {'HTTP':<6} 响应")
print("-" * 100)
for name, host, params, auth, ua in CASES:
    code, body = call(host, params, auth, ua)
    print(f"{name:<38} {str(code):<6} {body}")
    rows.append({"case": name, "host": host, "params": "full" if params == PARAMS_FULL else "min",
                 "auth": "none" if auth is None else ("fake" if auth == "FAKE_TOKEN" else "TC_KEY"),
                 "ua": ua, "http": code, "body": body})
    time.sleep(0.9)

print()
print("=" * 100)
print("归因矩阵（只看 noneu 端点，锁定触发条件）")
print("=" * 100)
print(f"{'参数集':<8} {'token':<8} {'HTTP':<6} 说明")
for r in rows:
    if "noneu" not in r["case"]:
        continue
    tag = ""
    if r["http"] == 451:
        tag = "  <== 451"
    elif r["http"] == 401:
        tag = "  (token 无效)"
    elif r["http"] == 400:
        tag = "  (缺鉴权头)"
    elif r["http"] == 429:
        tag = "  (限流)"
    elif r["http"] == 200:
        tag = "  <== 200 可用!"
    print(f"{r['params']:<8} {r['auth']:<8} {str(r['http']):<6}{tag}")

with open("api_probe_451attrib.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
print("\n已写入 api_probe_451attrib.json")
