#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""判定 DB3 是否「无条件编造名字」——决定性测试。

若连明显无效的号码（如 60100000000）也返回名字，说明 DB3 的「有/无数据」
本身零信息量，连当「存在性信号」都不能用。
"""
import json
import re
import sys
import time

import requests
import urllib3

urllib3.disable_warnings()

URL = ("https://s.callapp.com/callapp-server/csrch"
       "?cpn=%2B{phone}&myp=gp.106898501948939491020&ibs=0&cid=0")
H = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36")}

TESTS = [
    ("60100000000", "明显无效（全 0 段）"),
    ("60111111111", "明显无效（全 1）"),
    ("60999999999", "明显无效（全 9）"),
    ("60123456789", "疑似无效"),
    ("60162281297", "真实号（DB1='Prof Lee'）"),
]


def ask(p):
    try:
        r = requests.get(URL.format(phone=p), headers=H, timeout=25, verify=False)
        if r.status_code != 200:
            return f"HTTP{r.status_code}"
        try:
            return (r.json() or {}).get("name", "") or "<empty>"
        except ValueError:
            return "<badjson>"
    except requests.RequestException as exc:
        return f"ERR:{type(exc).__name__}"


named = 0
for p, note in TESTS:
    got = [ask(p) for _ in range(2)]
    time.sleep(1.2)
    ok = [g for g in got if not g.startswith(("HTTP", "ERR:", "<empty>", "<badjson>"))]
    if ok:
        named += 1
    print(f"{p}  ({note})")
    print(f"    -> {got}")

print(f"\n返回了名字的号码：{named}/{len(TESTS)}")
print("→ 若无效号码也返回名字，DB3 的『有数据』不含任何信息。" if named else "→ DB3 对无效号码不返回名字。")
