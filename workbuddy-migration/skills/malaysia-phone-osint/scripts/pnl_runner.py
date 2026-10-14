#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phone-number-lookup (cutypie2351) 隔离运行器

原脚本的问题：主流程里任何一个数据库报错都会被最外层 try/except 捕获并直接退出，
导致后面的 CallApp / Eyecon / Truecaller 根本不会执行。
本运行器逐个数据库单独调用并各自兜住异常，保证「能出结果的都出结果」。

用法:
    python pnl_runner.py 60102261791
    python pnl_runner.py 60102261791 --repo /tmp/osintrepos/phone-number-lookup
"""
import argparse
import importlib.util
import os
import sys
import traceback

TARGETS = [
    ("DataBase 1 · CallerID app (com.callblocker.whocalledme)", "callerid", "start_callerid_check"),
    ("DataBase 2 · Sync.ME", "syncme", "start_styncme"),
    ("DataBase 3 · CallApp", "callapp", "send_request"),
    ("DataBase 4a · Eyecon (picture)", "eyecon", "send_request_pic"),
    ("DataBase 4b · Eyecon (name)", "eyecon", "send_request_getname"),
    ("DataBase 5 · Truecaller", "truecaller", "send_request"),
]


def load_module(repo: str):
    path = os.path.join(repo, "lookup.py")
    if not os.path.exists(path):
        raise SystemExit(f"找不到 {path}")
    spec = importlib.util.spec_from_file_location("pnl_lookup", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pnl_lookup"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("phone", help="国际格式、不带 + 号，如 60102261791")
    ap.add_argument("--repo", default=os.environ.get("PNL_REPO", "."), help="phone-number-lookup 仓库目录")
    ap.add_argument("--more", action="store_true", help="打印完整 JSON")
    args = ap.parse_args()

    mod = load_module(args.repo)

    instances = {
        "callerid": mod.CallerID(),
        "syncme": mod.Sync_Me(),
        "callapp": mod.CallApp(),
        "eyecon": mod.Eyecon(),
        "truecaller": mod.Truecaller(),
    }

    for label, key, method in TARGETS:
        print("\n" + "=" * 68)
        print(f"### {label}")
        print("=" * 68)
        try:
            getattr(instances[key], method)(args.phone, args.more)
        except SystemExit:
            raise
        except Exception as e:
            print(f"  ✗ 该数据库调用失败: {type(e).__name__}: {e}")
            if os.environ.get("PNL_TRACE"):
                traceback.print_exc()

    print("\n" + "=" * 68)
    print("注意：以上名字/地点均来自众包来电识别 App 的用户通讯录，不是实名数据，")
    print("      可能过期、可能是别人的备注名、也可能被恶意标注。不可作为身份认定依据。")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    sys.exit(main())
