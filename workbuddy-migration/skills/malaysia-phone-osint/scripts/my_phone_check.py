#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
马来西亚电话号码反查工具（合法渠道）

用法:
    python my_phone_check.py 0102261791
    python my_phone_check.py 010-2261791 0123456789 +60123456789
    python my_phone_check.py 1234567890123 --bank
    python my_phone_check.py "ABC SDN BHD" --company

能力边界（重要）:
  - 本脚本只能给出: ①号段/运营商(离线推测) ②PDRM 诈骗举报库记录
  - 不能给出机主姓名。姓名只存在于电讯商实名库, 仅 PDRM/MCMC/法院可依法调取。
"""
import argparse
import json
import sys
import urllib.request

import phonenumbers
from phonenumbers import PhoneNumberFormat, PhoneNumberType, carrier, geocoder

# --- PDRM CCID Semak Mule 内部 JSON 接口 (前端 config.js + main.js 中可见) ---
MULE_URL = "https://semakmule.rmp.gov.my/api/mule/get_search_data.php"

CATEGORY = {
    "bank": ("bank", "bankAccount"),
    "phone": ("telefon", "telNo"),
    "company": ("namasyarikat", "companyName"),
}

TYPE_NAME = {
    PhoneNumberType.MOBILE: "mobile 手机",
    PhoneNumberType.FIXED_LINE: "fixed 固话",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "fixed/mobile",
    PhoneNumberType.TOLL_FREE: "toll-free",
    PhoneNumberType.PREMIUM_RATE: "premium rate",
    PhoneNumberType.VOIP: "VoIP",
    PhoneNumberType.PERSONAL_NUMBER: "personal number",
    PhoneNumberType.PAGER: "pager",
    PhoneNumberType.UAN: "UAN",
    PhoneNumberType.VOICEMAIL: "voicemail",
    PhoneNumberType.UNKNOWN: "unknown",
}


def offline_lookup(raw: str) -> dict:
    """离线号段解析: 号码类型 / 号段归属运营商 / 地区。不含机主信息。"""
    digits = raw.strip().replace(" ", "").replace("-", "")
    if digits.startswith("+"):
        candidate = digits
    elif digits.startswith("60"):
        candidate = "+" + digits
    elif digits.startswith("0"):
        candidate = "+60" + digits[1:]
    else:
        candidate = "+60" + digits

    try:
        num = phonenumbers.parse(candidate, None)
    except phonenumbers.NumberParseException as e:
        return {"ok": False, "error": f"无法解析: {e}"}

    if not phonenumbers.is_possible_number(num):
        return {"ok": False, "error": "号码长度不合法"}

    return {
        "ok": True,
        "e164": phonenumbers.format_number(num, PhoneNumberFormat.E164),
        "national": phonenumbers.format_number(num, PhoneNumberFormat.NATIONAL),
        "valid": phonenumbers.is_valid_number(num),
        "type": TYPE_NAME.get(phonenumbers.number_type(num), "unknown"),
        # 注意: 号段运营商 = 最初分配方, 携号转网(MNP)后可能已变更, 不可当结论用
        "prefix_carrier": carrier.name_for_number(num, "en") or "(未知)",
        "region": geocoder.description_for_number(num, "en") or "(未知)",
        "country_code": num.country_code,
    }


def semak_mule(kind: str, value: str, timeout: int = 25) -> dict:
    """查询 PDRM CCID Semak Mule 举报库。返回命中记录或空。"""
    cat, field = CATEGORY[kind]
    payload = json.dumps({"data": {"category": cat, field: value}}).encode()
    req = urllib.request.Request(
        MULE_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Origin": "https://semakmule.rmp.gov.my",
            "Referer": "https://semakmule.rmp.gov.my/",
            "User-Agent": "Mozilla/5.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8", "ignore"))
    except Exception as e:  # 网络/接口变动
        return {"ok": False, "error": str(e)}

    # table_data 才是结果; 响应里的 count 是"该关键词被查询次数"计数器, 不是命中数
    rows = body.get("table_data") or []
    header = body.get("table_header") or []
    return {
        "ok": True,
        "headers": header,
        "rows": rows,
        "reported": bool(rows),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="马来西亚号码/账号反查（合法渠道）")
    ap.add_argument("values", nargs="+", help="电话号码 / 银行账号 / 公司名")
    ap.add_argument(
        "--bank", action="store_true", help="按银行账号查询 Semak Mule"
    )
    ap.add_argument(
        "--company", action="store_true", help="按公司名查询 Semak Mule"
    )
    args = ap.parse_args()

    kind = "bank" if args.bank else "company" if args.company else "phone"

    for raw in args.values:
        print("=" * 62)
        print(f"输入: {raw}")
        if kind == "phone":
            info = offline_lookup(raw)
            print("\n[1] 离线号段解析 (libphonenumber)")
            if not info["ok"]:
                print("    ✗", info["error"])
                continue
            print(f"    E.164        : {info['e164']}")
            print(f"    本地格式     : {info['national']}")
            print(f"    号码类型     : {info['type']}")
            print(f"    号段运营商   : {info['prefix_carrier']}  (仅最初分配方, MNP 后可能已变)")
            print(f"    归属地       : {info['region']}")
            print(f"    号段有效     : {info['valid']}")
            # Semak Mule 存的是本地格式(0 开头、无连字符), 用 E.164 查会查不到
            query_value = "".join(c for c in info["national"] if c.isdigit())
        else:
            query_value = raw

        print("\n[2] PDRM CCID Semak Mule 举报库")
        res = semak_mule(kind, query_value)
        if not res["ok"]:
            print("    ✗ 查询失败:", res["error"])
        elif res["reported"]:
            print(f"    ⚠ 有 {len(res['rows'])} 条记录:")
            print("      " + " | ".join(res["headers"]))
            for row in res["rows"]:
                print("      " + " | ".join(str(c) for c in row))
        else:
            print("    ✓ 无记录（未在 PDRM 诈骗举报库中，≠ 安全）")

    print("=" * 62)
    print("提示: 机主姓名无法通过任何公开渠道获取。")
    print("      诈骗 -> 报警 PDRM / NSRC 997；骚扰诽谤 -> 律师向法院申请披露令。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
