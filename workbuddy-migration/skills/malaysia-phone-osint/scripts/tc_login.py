#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第 1 步：向指定号码发送 Truecaller 登录 OTP。
⚠️ 有副作用：会真实发送短信。由用户明确授权执行。
"""
import asyncio
import json
import os
import sys

# 沙箱网络：Python 的 TLS 校验常失败 -> 全局给 httpx 兜底 verify=False
import httpx
_OrigAsyncClient = httpx.AsyncClient


class _PatchedAsyncClient(_OrigAsyncClient):
    def __init__(self, *a, **kw):
        kw.setdefault("verify", False)
        super().__init__(*a, **kw)


httpx.AsyncClient = _PatchedAsyncClient

from truecallerpy import login  # noqa: E402

PHONE = "+60102261791"
HERE = os.path.dirname(os.path.abspath(__file__))
SECRETS = os.path.join(HERE, ".secrets")
os.makedirs(SECRETS, exist_ok=True)
STATE = os.path.join(SECRETS, "tc_login_state.json")


async def main():
    print(f"向 {PHONE} 请求登录 OTP ...")
    resp = await login(PHONE)
    print(json.dumps(resp, ensure_ascii=False, indent=2))

    if isinstance(resp, dict) and isinstance(resp.get("data"), dict):
        d = resp["data"]
        if d.get("requestId"):
            with open(STATE, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            print(f"\n✅ requestId 已保存 -> {STATE}")
            print(f"   method    = {d.get('method')}")
            print(f"   tokenTtl  = {d.get('tokenTtl')} 秒")
            print(f"   domain    = {d.get('domain')}")
            print("\n请查看手机短信，把 6 位 OTP 告诉我。")
            return 0
        print("\n⚠️ 响应里没有 requestId，OTP 未发出。")
        return 1

    print("\n⚠️ 响应结构异常，未保存。")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
