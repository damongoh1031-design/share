#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
只读连通性探测：验证 Truecaller 官方 OAuth 端点在本机是否可达。
严格只做「无凭据 / 假凭据」探测 —— 不发送任何真实手机号，不触发真实 OTP。
"""
import json
import time

import requests
import urllib3

urllib3.disable_warnings()
H = {"User-Agent": "Truecaller/11.75.5 (Android;10)", "Accept": "application/json"}


def probe(name, method, url, headers=None, **kw):
    t0 = time.time()
    hh = {**H, **(headers or {})}
    try:
        r = requests.request(method, url, timeout=25, verify=False, headers=hh, **kw)
        dt = int((time.time() - t0) * 1000)
        body = (r.text or "").strip().replace("\n", " ")[:260]
        print(f"[{r.status_code}] {name}  ({dt}ms)")
        print(f"        {url}")
        if body:
            print(f"        body: {body}")
        return r.status_code, body
    except Exception as e:
        print(f"[ERR ] {name}  -> {type(e).__name__}: {str(e)[:120]}")
        return None, str(e)


print("=" * 78)
print("A. 官方 OAuth 端点（flutter-sdk 用的域名）")
print("=" * 78)
# 无 token 访问 userinfo：期望 401 => 端点活着且要鉴权
probe("userinfo 无 token", "GET", "https://oauth-account-noneu.truecaller.com/v1/userinfo")
# 假 token
probe("userinfo 假 Bearer", "GET", "https://oauth-account-noneu.truecaller.com/v1/userinfo",
      headers={**H, "Authorization": "Bearer FAKE_TOKEN_FOR_PROBE"})
# token 端点，假 client_id + 假 code
probe("token 假 client_id", "POST", "https://oauth-account-noneu.truecaller.com/v1/token",
      data={"grant_type": "authorization_code",
            "client_id": "0000000000_probe_probe_probe_probe_probe",
            "code": "PROBE_FAKE_CODE",
            "code_verifier": "PROBE_FAKE_VERIFIER"},
      headers={**H, "Content-Type": "application/x-www-form-urlencoded"})
# token 端点，用 example 里那个 demo client_id
probe("token example 的 demo client_id", "POST",
      "https://oauth-account-noneu.truecaller.com/v1/token",
      data={"grant_type": "authorization_code",
            "client_id": "1si1lk7rbbo_mtg29mw5yczekv2ripbbnwnaozhpz6o",
            "code": "PROBE_FAKE_CODE",
            "code_verifier": "PROBE_FAKE_VERIFIER"},
      headers={**H, "Content-Type": "application/x-www-form-urlencoded"})

print()
print("=" * 78)
print("B. 对照：search5 两个端点（用假 Bearer，不消耗真实额度）")
print("=" * 78)
for host in ("search5-eu", "search5-noneu"):
    probe(f"{host} 假 Bearer", "GET",
          f"https://{host}.truecaller.com/v2/search",
          params={"q": "60123456789", "countryCode": "MY", "type": "4",
                  "encoding": "json", "installationId": "probe"},
          headers={**H, "Authorization": "Bearer PROBE_FAKE_TOKEN"})

print()
print("=" * 78)
print("C. 对照：search5 无任何鉴权头（区分端点策略 vs token 失效）")
print("=" * 78)
for host in ("search5-eu", "search5-noneu"):
    probe(f"{host} 无 token", "GET",
          f"https://{host}.truecaller.com/v2/search",
          params={"q": "60123456789", "countryCode": "MY", "type": "4", "encoding": "json"})

print()
print("=" * 78)
print("D. account-asia-south1（truecallerjs 的 OTP 端点）—— 仅探测，不发真实号码")
print("=" * 78)
# 故意发空 body：期望 4xx 参数错误 => 端点活着。不会触发任何真实 OTP 发送。
probe("sendOnboardingOtp 空 body", "POST",
      "https://account-asia-south1.truecaller.com/v2/sendOnboardingOtp",
      json={}, headers={**H, "Content-Type": "application/json; charset=UTF-8",
                        "clientsecret": "lvc22mp3l1sfv6ujg83rd17btt"})
probe("verifyOnboardingOtp 空 body", "POST",
      "https://account-asia-south1.truecaller.com/v1/verifyOnboardingOtp",
      json={}, headers={**H, "Content-Type": "application/json; charset=UTF-8",
                        "clientsecret": "lvc22mp3l1sfv6ujg83rd17btt"})

print("\ndone")
