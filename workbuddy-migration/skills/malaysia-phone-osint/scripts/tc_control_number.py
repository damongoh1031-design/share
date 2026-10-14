#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对照实验：20003 是「号码问题」还是「服务端统一拦截自动化请求」？

选号原则 —— 零副作用：
  ① 马来西亚固话 +60312345678  -> 固话不可能收短信
  ② 无效手机前缀 +601999999999 -> 199 不是有效马来西亚手机前缀
  ③ 用户号码   +60102261791    -> 对照组（已证明不会真发）
三个都走同一份请求体，看响应是否一致。
"""
import json
import random
import string

import httpx
import urllib3
from phonenumbers import parse as parse_pn
from phonenumbers.phonenumberutil import region_code_for_country_code

urllib3.disable_warnings()

import sys
sys.path.insert(0, r"C:\Users\Admin\.workbuddy-ai\binaries\python\envs\osint\Lib\site-packages")
from truecallerpy.data.phones_list import get_random_device  # noqa: E402

URL = "https://account-asia-south1.truecaller.com/v2/sendOnboardingOtp"
SECRET = "lvc22mp3l1sfv6ujg83rd17btt"
UA = "Truecaller/11.75.5 (Android;10)"


def rnd(n):
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))


def call(phone):
    pn = parse_pn(phone, None)
    if not pn.country_code or not pn.national_number:
        return None, f"phonenumbers 无法解析 {phone}"
    dev = get_random_device()
    body = {
        "countryCode": str(region_code_for_country_code(pn.country_code)),
        "dialingCode": pn.country_code,
        "installationDetails": {
            "app": {"buildVersion": 5, "majorVersion": 11,
                    "minorVersion": 7, "store": "GOOGLE_PLAY"},
            "device": {"deviceId": rnd(16), "language": "en",
                       "manufacturer": dev["manufacturer"], "model": dev["model"],
                       "osName": "Android", "osVersion": "10", "mobileServices": ["GMS"]},
            "language": "en",
        },
        "phoneNumber": str(pn.national_number),
        "region": "region-2",
        "sequenceNo": 2,
    }
    hdr = {"content-type": "application/json; charset=UTF-8",
           "accept-encoding": "gzip", "user-agent": UA, "clientsecret": SECRET}
    r = httpx.post(URL, json=body, headers=hdr, timeout=30, verify=False)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text[:300]


CASES = [
    ("① 马来西亚固话（不可能收短信）", "+60312345678"),
    ("② 无效手机前缀 199", "+601999999999"),
    ("③ 用户号码（对照）", "+60102261791"),
]

print(f"{'用例':<34} {'HTTP':<6} status / message / method / tokenTtl")
print("-" * 96)
for label, phone in CASES:
    code, d = call(phone)
    if isinstance(d, dict):
        print(f"{label:<34} {str(code):<6} status={d.get('status')} | {d.get('message')} | "
              f"method={d.get('method')} | tokenTtl={d.get('tokenTtl')}")
    else:
        print(f"{label:<34} {str(code):<6} {d}")

print("""
判读：
  · 三个用例响应完全一致（都 20003、都无 method/tokenTtl）
      -> 服务端在「选定发送渠道」前就统一拒绝，与号码无关
      -> 是自动化请求被整体封堵（很可能加了设备证明 / Play Integrity 校验）
  · 若无效号码返回不同错误码（如 invalid number）
      -> 服务端仍在做号码校验，20003 可能与号码或账号状态有关
""")
