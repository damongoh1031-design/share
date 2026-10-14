# -*- coding: utf-8 -*-
"""ScamGuards 批量提交 v2 — 自适配额轮询。
每次提交前先 OPTIONS 读 X-Ratelimit-Remaining，为 0 则睡到 Reset。
"""
import json, time, urllib.request, urllib.error, sys, datetime

H = {"Content-Type": "application/json", "Origin": "https://scamguards.app",
     "Referer": "https://scamguards.app/submit",
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
REPORTER_HASH = "rh_93d6c053edc546c29cb3bbaf794412ef"

NUMBERS = [
    ("016-259 1088", "0162591088"), ("018-310 9929", "0183109929"),
    ("011-186 74391", "01118674391"), ("016-278 8069", "0162788069"),
    ("018-357 5535", "0183575535"), ("017-491 6139", "0174916139"),
    ("016-216 6952", "0162166952"), ("016-258 0790", "0162580790"),
    ("011-261 13318", "01126113318"), ("016-258 0348", "0162580348"),
]

def quota():
    """返回 (remaining, reset_ts)。"""
    req = urllib.request.Request("https://scamguards.app/api/submit", method="OPTIONS")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            print(f"  OPTIONS {r.status}", file=sys.stderr)
    except urllib.error.HTTPError as e:
        r = e
    rem = int(r.headers.get("X-Ratelimit-Remaining", "0"))
    rst = int(r.headers.get("X-Ratelimit-Reset", "0")) / 1000
    return rem, rst

def submit(local, digits):
    desc = (f"Suspected scam caller using Malaysian mobile number {local} "
            f"(E.164 +60{digits[1:]}). Part of a coordinated cluster of eleven Malaysian "
            "mobile numbers operating the same charity-impersonation scam. The caller "
            "impersonated a charitable organisation and pressured the recipient to make an "
            "immediate donation, while refusing to provide verifiable charity registration "
            "details or official authorisation documentation. No money was transferred; no "
            "OTP, banking details, card information or identity documents were disclosed; "
            "no APK was installed and no links were clicked. Reported strictly for public "
            "awareness and fraud prevention. This is a suspected, not confirmed, scam.")
    body = json.dumps({"scamType": "other", "platform": "Phone Call", "country": "MY",
                       "description": desc, "amountLost": 0,
                       "reporterHash": REPORTER_HASH,
                       "dataPoints": [{"type": "phone", "value": local}]}).encode()
    req = urllib.request.Request("https://scamguards.app/api/submit",
                                 data=body, headers=H, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return -1, str(e)

idxs = [int(x) for x in sys.argv[1].split(",")]
for i in idxs:
    local, digits = NUMBERS[i]
    for attempt in range(1, 6):
        rem, rst = quota()
        wait = rst - time.time()
        if rem <= 0 and wait > 0:
            secs = int(wait) + 5
            print(f"[{datetime.datetime.now():%H:%M:%S}] #{i+1} {local}: quota={rem}, "
                  f"sleeping {secs}s until {datetime.datetime.fromtimestamp(rst):%H:%M:%S}")
            time.sleep(secs)
            continue
        code, resp = submit(local, digits)
        ts = f"{datetime.datetime.now():%H:%M:%S}"
        print(f"[{ts}] #{i+1} {local} attempt{attempt} -> HTTP {code} {resp[:220]}")
        if code == 200:
            break
        if code == 500:
            print(f"  → 500 服务端故障，等 70s 重试")
            time.sleep(70)
        elif code == 429:
            continue
        else:
            time.sleep(70)
    time.sleep(70)
print("DONE_ALL")
