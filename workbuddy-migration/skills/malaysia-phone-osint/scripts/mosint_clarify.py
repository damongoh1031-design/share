#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""澄清两处：① BNM 到底能不能过 WAF（跑 3 次看稳定性）② SSPI 返回的文本是默认文案还是查询结果"""
import re
import time

import requests
import urllib3

urllib3.disable_warnings()

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")

print("=" * 78)
print("① BNM 稳定性（同一简单 header，跑 3 次）")
print("=" * 78)
for i in range(3):
    try:
        r = requests.get("https://www.bnm.gov.my/financial-consumer-alert-list",
                         headers={"User-Agent": UA, "Accept": "*/*"},
                         timeout=30, verify=False)
        body = r.text
        is_waf = ("Just a moment" in body) or ("cf-chl" in body.lower()) or \
                 ("Enable JavaScript and cookies" in body)
        # 找警示名单关键词
        kw_hits = len(re.findall(r"(?i)alert list|senarai|financial consumer", body))
        print(f"  第 {i+1} 次: HTTP {r.status_code}  len={len(body)}  "
              f"WAF页={'是' if is_waf else '否'}  名单关键词={kw_hits}")
    except Exception as e:
        print(f"  第 {i+1} 次: ERR {type(e).__name__}: {str(e)[:90]}")
    time.sleep(2)

print()
print("=" * 78)
print("② SSPI 返回文本 —— 是页面默认文案还是真实查询结果？")
print("=" * 78)
try:
    r = requests.get("https://sspi.imi.gov.my/sspi/index.php?page=sspi/bm",
                     headers={"User-Agent": UA, "Accept": "*/*"},
                     timeout=30, verify=False)
    print(f"HTTP {r.status_code}  len={len(r.text)}")
    body = re.sub(r"<script.*?</script>", "", r.text, flags=re.S)
    body = re.sub(r"<style.*?</style>", "", body, flags=re.S)
    txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)).strip()
    print(f"\n正文前 500 字:\n  {txt[:500]}")
    print("\n关键判定:")
    for kw, note in [
        ("Tiada halangan", "『无禁止』——注意这可能是页面**默认/示例**文案"),
        ("captcha", "有验证码"),
        ("No. Kad Pengenalan", "有身份证输入框"),
        ("sah pada tarikh dan masa", "『仅查询当时有效』免责声明"),
    ]:
        print(f"  {'✔' if kw.lower() in txt.lower() else '✘'} {kw:<28} {note}")
except Exception as e:
    print(f"ERR {type(e).__name__}: {str(e)[:110]}")
