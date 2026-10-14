#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSPI 区分度终测：精确取 <span id="lblStatuscode"> 的内容（不再用宽泛正则）。
对照：合法格式 IC vs 非法输入 —— 若结果不同，说明接口真的在查。
"""
import re
import time

import requests
import urllib3

urllib3.disable_warnings()
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
URL = "https://sspi.imi.gov.my/sspi/index.php?page=sspi/bm"


def check(ic):
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "*/*"})
    s.get(URL, timeout=30, verify=False)
    r = s.post(URL, data={"txtIcNo": ic, "btnSemak": "Semak"},
               headers={"Content-Type": "application/x-www-form-urlencoded"},
               timeout=35, verify=False)
    html = r.text
    # ★ 精确取 lblStatuscode（结果区）
    m = re.search(r'id="lblStatuscode"[^>]*>(.*?)</span>', html, re.S | re.I)
    result = ""
    if m:
        result = re.sub(r"<[^>]+>", " ", m.group(1))
        result = re.sub(r"\s+", " ", result).strip()
    # 另一处提示区
    m2 = re.search(r'id="lblStatus"[^>]*>(.*?)</span>', html, re.S | re.I)
    hint = ""
    if m2:
        hint = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m2.group(1))).strip()
    return r.status_code, result, hint, len(html)


CASES = [
    ("合法格式 A", "900101011234"),
    ("合法格式 B", "850505055555"),
    ("全 0", "000000000000"),
    ("太短", "123"),
    ("含字母", "90010101123A"),
    ("空值", ""),
]

print(f"{'用例':<12} {'HTTP':<6} {'lblStatuscode（结果区）':<52} 提示区")
print("-" * 118)
results = []
for label, ic in CASES:
    try:
        code, res, hint, ln = check(ic)
        results.append(res)
        print(f"{label:<12} {str(code):<6} {res[:50]:<52} {hint[:40]}")
    except Exception as e:
        results.append("ERR")
        print(f"{label:<12} ERR    {type(e).__name__}: {str(e)[:60]}")
    time.sleep(3)

print()
print("=" * 118)
uniq = set(results)
if len(uniq) == 1:
    print(f"⚠️ 全部相同 → {uniq.pop()!r}")
    print("   判定：接口无区分度（对任何输入都返回同一结果），不能作为有效查询依据")
else:
    print(f"✅ 结果随输入变化（{len(uniq)} 种）→ 接口**有区分度，真的在查**：")
    for u in uniq:
        print(f"     · {u!r}")
