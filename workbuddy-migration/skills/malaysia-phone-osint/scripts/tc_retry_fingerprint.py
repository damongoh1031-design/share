#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 20003 的根因：是「伪造指纹过时」还是「服务端彻底封堵」。

设计：对同一号码，换不同版本的客户端指纹重试。
- 20003 已证明「不会真发短信」-> 重试成本低
- 一旦某组返回 method/tokenTtl（说明真发了）立即停止，避免重复发短信
"""
import json
import random
import string
import sys
import time

import httpx
import urllib3
from phonenumbers import parse as parse_pn
from phonenumbers.phonenumberutil import region_code_for_country_code

urllib3.disable_warnings()

sys.path.insert(0, r"C:\Users\Admin\.workbuddy-ai\binaries\python\envs\osint\Lib\site-packages")
from truecallerpy.data.phones_list import get_random_device  # noqa: E402

PHONE = "+60102261791"
URL = "https://account-asia-south1.truecaller.com/v2/sendOnboardingOtp"
SECRET = "lvc22mp3l1sfv6ujg83rd17btt"

pn = parse_pn(PHONE, None)
CC = str(region_code_for_country_code(pn.country_code))
DIAL = pn.country_code
NAT = str(pn.national_number)
print(f"号码解析: dialingCode={DIAL} countryCode={CC} national={NAT}\n")


def rnd(n):
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))


def build(major, minor, build_v, os_ver):
    dev = get_random_device()
    return {
        "countryCode": CC,
        "dialingCode": DIAL,
        "installationDetails": {
            "app": {"buildVersion": build_v, "majorVersion": major,
                    "minorVersion": minor, "store": "GOOGLE_PLAY"},
            "device": {"deviceId": rnd(16), "language": "en",
                       "manufacturer": dev["manufacturer"], "model": dev["model"],
                       "osName": "Android", "osVersion": os_ver,
                       "mobileServices": ["GMS"]},
            "language": "en",
        },
        "phoneNumber": NAT,
        "region": "region-2",
        "sequenceNo": 2,
    }


# (标签, major, minor, build, os_ver, ua)
CASES = [
    ("A 基线（库现值）",  11, 7,  5,  "10", "Truecaller/11.75.5 (Android;10)"),
    ("B 14.43.8",        14, 43, 8,  "13", "Truecaller/14.43.8 (Android;13)"),
    ("C 15.3.10",        15, 3,  10, "14", "Truecaller/15.3.10 (Android;14)"),
    ("D 14.43.8+无UA伪装", 14, 43, 8, "13", "okhttp/4.9.2"),
]

for label, maj, mnr, bv, osv, ua in CASES:
    body = build(maj, mnr, bv, osv)
    hdr = {"content-type": "application/json; charset=UTF-8",
           "accept-encoding": "gzip", "user-agent": ua, "clientsecret": SECRET}
    print("=" * 78)
    print(f"### {label}   (UA={ua})")
    print("=" * 78)
    try:
        r = httpx.post(URL, json=body, headers=hdr, timeout=30, verify=False)
        print(f"HTTP {r.status_code}")
        try:
            d = r.json()
            print(json.dumps(d, ensure_ascii=False, indent=2))
            # 关键判定：拿到 method / tokenTtl 才是真的发出了
            if d.get("method") or d.get("tokenTtl"):
                print("\n>>> ✅ 这组成功发出了 OTP！停止后续测试。")
                with open(".secrets/tc_login_state.json", "w", encoding="utf-8") as f:
                    json.dump(d, f, ensure_ascii=False, indent=2)
                print("    requestId 已保存，请查收短信。")
                break
            print(f"\n>>> ❌ 仍是 status={d.get('status')} / {d.get('message')} —— OTP 未发出")
        except Exception:
            print(r.text[:400])
    except Exception as e:
        print(f"ERR {type(e).__name__}: {e}")
    time.sleep(3)

print("\n--- 实验结束 ---")
