#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DB3 · CallApp 号码反查（s.callapp.com/callapp-server/csrch）

独立实现，不依赖 cutypie2351/phone-number-lookup 仓库。
是 2026-10 之后 phone-number-lookup 里**唯一还能用**的库（DB1 已被封）。

用法:
    python callapp_lookup.py 60102261791
    python callapp_lookup.py 0102261791 0162281297 --json
    python callapp_lookup.py --file numbers.txt --delay 0.3
    python callapp_lookup.py --probe                 # 只探活
    python callapp_lookup.py 60102261791 --recheck   # 查两次验可复现

字段语义见 SKILL.md §4「DB3 CallApp」。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time

try:
    import requests
except ImportError:
    sys.exit("需要 requests：pip install requests")

try:
    import phonenumbers
except ImportError:
    phonenumbers = None

ENDPOINT = "https://s.callapp.com/callapp-server/csrch"

# 来自公开仓库 cutypie2351/phone-number-lookup 的示例凭据。
# ⚠️ tk/cvc 必需：缺失时服务端不报错，而是返回**别人的**记录（实测会串号）。
#    可用环境变量覆盖：CALLAPP_TK / CALLAPP_CVC / CALLAPP_MYP
DEFAULT_TK = os.environ.get("CALLAPP_TK", "0011243853")
DEFAULT_CVC = os.environ.get("CALLAPP_CVC", "2206")
DEFAULT_MYP = os.environ.get("CALLAPP_MYP", "gp.106898501948939491020")

HEADERS = {
    "Host": "s.callapp.com",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.124 Safari/537.36",
}

# 探活用号码（已确认有返回）
PROBE_NUMBER = "60162281297"

SOCIAL_FIELDS = [
    ("facebookID", "Facebook", "https://www.facebook.com/profile.php?id={}"),
    ("linkedinPubProfileUrl", "LinkedIn", "{}"),
    ("linkedinID", "LinkedIn(内码)", None),
    ("twitterScreenName", "Twitter/X", "https://twitter.com/{}"),
    ("instagramID", "Instagram", "https://www.instagram.com/"),
    ("googlePlusID", "Google+", None),
    ("foursquareID", "Foursquare", None),
]


def normalize(phone: str, default_region: str = "MY") -> str | None:
    """转成纯数字 E.164（无 + 号）。失败返回 None。"""
    raw = re.sub(r"[^\d+]", "", phone)
    if phonenumbers is not None:
        try:
            if raw.startswith("+"):
                num = phonenumbers.parse(raw, None)
            else:
                num = phonenumbers.parse(raw, default_region)
            if phonenumbers.is_possible_number(num):
                return str(num.country_code) + str(num.national_number)
        except Exception:
            pass
    # 兜底：手工归一化
    digits = re.sub(r"\D", "", phone)
    if not digits:
        return None
    if digits.startswith("0") and default_region.upper() == "MY":
        digits = "6" + digits
    elif len(digits) == 10 and digits.startswith("1") and default_region.upper() == "MY":
        digits = "60" + digits
    return digits


def lookup(number: str, timeout: int = 20) -> dict:
    """查询单个号码。

    返回 {'ok':bool, 'raw':dict|None, 'error':str|None, 'blocked':bool, 'xcode':str|None}
    ⚠️ 限流信号：HTTP 513 + 响应头 X_C_CODE: -4 + 空 body（2026-10-05 实测）。
       与「未命中」（HTTP 200 空 body）必须区分开。
    🚨 降级信号：HTTP 200 + X_C_CODE: 1 = 服务端走匿名路径，返回**与号码无关的随机记录**。
       本函数直接判为失败（ok=False, degraded=True），绝不外泄假数据。
    """
    # ---- 前置护栏：凭据不完整时服务端不报错，而是返回随机记录 ----
    if not DEFAULT_TK or not DEFAULT_CVC:
        return {"ok": False, "raw": None, "blocked": False, "degraded": True, "xcode": None,
                "error": "凭据不完整(tk/cvc 为空)：服务端会返回与号码无关的随机记录，已拒绝发起请求。"
                         "请设置 CALLAPP_TK / CALLAPP_CVC 环境变量"}

    params = {
        "cpn": f"+{number}",
        "myp": DEFAULT_MYP,
        "ibs": "0",
        "cid": "0",
        "tk": DEFAULT_TK,
        "cvc": DEFAULT_CVC,
    }
    try:
        r = requests.get(ENDPOINT, params=params, headers=HEADERS, timeout=timeout)
    except Exception as e:
        return {"ok": False, "raw": None, "error": f"{type(e).__name__}: {e}",
                "blocked": False, "xcode": None}

    xc = (r.headers.get("X_C_CODE") or "").strip()

    # 限流 / 拒绝（HTTP 511/512/513/525，状态在 X_C_CODE）
    if r.status_code in (511, 512, 513, 525) or xc.startswith("-"):
        meaning = {"-2": "缺必填参数(cpn)", "-3": "身份无效(myp/tk)",
                   "-4": "配额/速率用尽"}.get(xc, "未知")
        return {"ok": False, "raw": None, "blocked": True, "xcode": xc,
                "error": f"blocked (HTTP {r.status_code} / X_C_CODE {xc or 'n/a'} {meaning})"}
    if r.status_code != 200:
        return {"ok": False, "raw": None, "blocked": False, "xcode": xc,
                "error": f"HTTP {r.status_code}"}

    # 🚨 匿名降级路径：返回的是随机记录，直接丢弃
    if xc == "1":
        return {"ok": False, "raw": None, "blocked": False, "degraded": True, "xcode": xc,
                "error": "degraded (HTTP 200 / X_C_CODE 1)：走匿名路径，返回的是与号码无关的随机记录，已丢弃"}

    body = (r.text or "").strip()
    if not body:
        # 空响应 = 未命中 / 参数被拒（cpn 空）
        return {"ok": True, "raw": {}, "error": None, "blocked": False,
                "empty": True, "xcode": xc}
    try:
        data = json.loads(body)
    except Exception:
        return {"ok": False, "raw": None, "error": f"非 JSON: {body[:120]}",
                "blocked": False, "xcode": xc}
    if not isinstance(data, dict):
        return {"ok": False, "raw": None, "error": f"非预期结构: {body[:120]}",
                "blocked": False, "xcode": xc}
    return {"ok": True, "raw": data, "error": None, "blocked": False, "xcode": xc}


def fmt_social(raw: dict) -> list[str]:
    out = []
    for key, label, tmpl in SOCIAL_FIELDS:
        v = raw.get(key)
        if isinstance(v, dict) and v.get("id"):
            sid = v["id"]
            link = tmpl.format(sid) if tmpl else None
            sure = "sure" if v.get("sure") else "unsure"
            out.append(f"{label}: {sid}" + (f"  → {link}" if link else "") + f"  [{sure}]")
    return out


def render(number: str, res: dict, indent: str = "  ") -> str:
    if not res["ok"]:
        return f"{indent}✗ 请求失败: {res['error']}"
    raw = res["raw"]
    if not raw:
        return f"{indent}(空响应：该号码未命中，或 tk/cvc 被拒)"

    lines = []
    name = raw.get("name")
    if name:
        lines.append(f"{indent}name        : {name}")
    if "priority" in raw:
        lines.append(f"{indent}priority    : {raw['priority']}   (热度/收录度，不是置信度)")
    if "spamScore" in raw:
        lines.append(f"{indent}spamScore   : {raw['spamScore']}   (语义未确认，勿当结论)")
    if raw.get("type") is not None:
        lines.append(f"{indent}type        : {raw['type']}")
    if raw.get("description"):
        lines.append(f"{indent}description : {raw['description']}")
    if raw.get("photoUrl"):
        lines.append(f"{indent}photoUrl    : {raw['photoUrl']}")
    if raw.get("avgRating") is not None:
        lines.append(f"{indent}avgRating   : {raw['avgRating']}")

    for w in raw.get("websites") or []:
        if isinstance(w, dict) and w.get("websiteUrl"):
            lines.append(f"{indent}website     : {w['websiteUrl']}")
    for a in raw.get("addresses") or []:
        if isinstance(a, dict) and a.get("street"):
            lines.append(f"{indent}address     : {a['street']}")
    for c in raw.get("categories") or []:
        if isinstance(c, dict) and c.get("name"):
            lines.append(f"{indent}category    : {c['name']}")
    for rv in raw.get("reviews") or []:
        if isinstance(rv, dict):
            txt = rv.get("text") or rv.get("reviewText") or ""
            if txt:
                lines.append(f"{indent}review      : {txt[:120]}")

    if raw.get("lat") is not None and raw.get("lng") is not None:
        lines.append(f"{indent}coords      : {raw['lat']}, {raw['lng']}")
    if raw.get("url"):
        lines.append(f"{indent}maps        : {raw['url']}")

    for s in fmt_social(raw):
        lines.append(f"{indent}{s}")

    oh = raw.get("openingHours")
    if isinstance(oh, dict) and oh:
        lines.append(f"{indent}openingHours: 有（{len(oh)} 天）")

    known = {
        "name", "priority", "spamScore", "type", "description", "photoUrl", "avgRating",
        "websites", "addresses", "categories", "reviews", "lat", "lng", "url",
        "openingHours", "googlePlacesId", "huaweiPlacesId",
    } | {k for k, _, _ in SOCIAL_FIELDS}
    extra = [k for k in raw if k not in known]
    if extra:
        lines.append(f"{indent}其他字段    : {', '.join(extra)}")

    if not lines:
        lines.append(f"{indent}(返回了 JSON 但无可读字段: {list(raw)[:8]})")
    return "\n".join(lines)


def probe() -> int:
    n = normalize(PROBE_NUMBER)
    res = lookup(n)
    if res["ok"] and res["raw"] and res["raw"].get("name"):
        print(f"[probe] OK  {PROBE_NUMBER} -> name={res['raw']['name']!r} "
              f"priority={res['raw'].get('priority')} xcode={res.get('xcode')}")
        return 0
    print(f"[probe] FAIL {PROBE_NUMBER} -> {res.get('error') or '空响应'} "
          f"(xcode={res.get('xcode')})")
    return 2


def main() -> int:
    ap = argparse.ArgumentParser(description="DB3 CallApp 号码反查")
    ap.add_argument("numbers", nargs="*", help="号码，本地格式(0102261791)或 E.164(+60102261791)")
    ap.add_argument("--file", help="号码文件，一行一个")
    ap.add_argument("--json", action="store_true", help="输出原始 JSON")
    ap.add_argument("--recheck", action="store_true", help="每个号码查两次，验证可复现")
    ap.add_argument("--delay", type=float, default=0.3, help="请求间隔秒（默认 0.3）")
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--region", default="MY", help="本地格式的默认国家（默认 MY）")
    ap.add_argument("--probe", action="store_true", help="只探活，不查号码")
    args = ap.parse_args()

    if args.probe:
        return probe()

    raw_list = list(args.numbers)
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            raw_list += [ln.strip() for ln in f if ln.strip()]
    if not raw_list:
        ap.error("至少给一个号码，或用 --file")

    results = {}
    for i, p in enumerate(raw_list):
        num = normalize(p, args.region)
        print("=" * 68)
        print(f"号码: {p}   归一化: +{num}" if num else f"号码: {p}   ✗ 无法归一化")
        print("=" * 68)
        if not num:
            results[p] = {"ok": False, "error": "normalize_failed"}
            continue

        res = lookup(num, args.timeout)
        if args.json:
            print(json.dumps(res["raw"] if res["ok"] else res, ensure_ascii=False, indent=2))
        else:
            print(render(num, res))

        if args.recheck:
            time.sleep(args.delay)
            res2 = lookup(num, args.timeout)
            same = (res.get("raw") == res2.get("raw"))
            print(f"  ── 复现性: {'一致 ✅' if same else '不一致 ❌'}")
            if not same:
                print(render(num, res2, indent="     [2nd] "))
        results[p] = res
        if i < len(raw_list) - 1:
            time.sleep(args.delay)

    print()
    print("=" * 68)
    print("注意：以上名字/地址/社交账号来自 CallApp 的用户通讯录众包库，不是实名数据。")
    print("      可能过期、可能是别人的备注名、也可能被恶意标注（实测存在恶搞与串号记录）。")
    print("      不可作为身份认定依据。实名只能走报警(PDRM/NSRC 997)或法院披露令。")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    sys.exit(main())
