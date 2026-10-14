#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用「表里已知的真名」作 ground truth，验证某个数据源是否返回真实资料。

背景：DB3 CallApp 在 2026-10-06 之后对同一号码**每次返回不同假名**，
但 HTTP 200、字段结构合法、覆盖率还更高 —— 靠状态码/覆盖率**完全发现不了**。
唯一可靠的判据是幂等性；再叠加「与已知真名是否一致」可进一步提高置信度。

判据（两条都要过）：
  1. 幂等性 —— 同一号码连查 N 次必须同名
  2. 一致性 —— 返回的名字应与快照里的已知名相同

用法：
  PY=C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe
  "$PY" source_verify.py --snapshot sheetAB.json --source db3 --n 10 --repeat 3

  # 只验证幂等（快照里没有已知名时）
  "$PY" source_verify.py --source db1 --phone 60162281297 --repeat 3

退出码：0 通过 / 9 不通过（含无数据）/ 1 参数错误
"""
import argparse
import importlib.util
import json
import os
import random
import re
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load_idem():
    """复用 check_idempotent.py 里的 ask_db3 / ask_db1（单一事实源）。"""
    p = os.path.join(_HERE, "check_idempotent.py")
    spec = importlib.util.spec_from_file_location("_idem", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def norm(s):
    """归一化：小写、只留字母数字与中文，用于宽松比较。"""
    s = (s or "").lower()
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["db1", "db3"], required=True,
                    help="要验证的数据源")
    ap.add_argument("--snapshot", default="",
                    help="快照 JSON（A1:B<N> 二维数组），提供后启用「一致性」判据")
    ap.add_argument("--phone", default="",
                    help="只验证单个号码时用（与 --snapshot 二选一）")
    ap.add_argument("--n", type=int, default=10, help="抽样号码数")
    ap.add_argument("--repeat", type=int, default=3, help="每号查询次数")
    ap.add_argument("--gap", type=float, default=1.2, help="请求间隔秒")
    ap.add_argument("--seed", type=int, default=20261007, help="抽样随机种子")
    ap.add_argument("--out", default="", help="明细输出 JSON 路径")
    args = ap.parse_args()

    idem = _load_idem()
    ask = idem.SOURCES[args.source]
    to_intl = idem.intl

    # ---------- 组装样本 ----------
    if args.snapshot:
        rows = json.load(open(args.snapshot, encoding="utf-8"))
        named = [(i + 1, (r[1] or "").strip(), (r[0] or "").strip())
                 for i, r in enumerate(rows)
                 if len(r) > 1 and (r[0] or "").strip() and (r[1] or "").strip()]
        print(f"快照里「已知真名」的行：{len(named)} 个")
        if not named:
            print("快照里没有已知真名，无法做一致性判据。")
            return 1
        random.seed(args.seed)
        seg = len(named) / args.n
        sample = [random.choice(named[int(k * seg):int((k + 1) * seg)])
                  for k in range(args.n)]
        print(f"分层抽样 {args.n} 个（覆盖全表），每号查 {args.repeat} 次\n")
    elif args.phone:
        sample = [(0, args.phone, "")]
        print(f"单号码验证：{args.phone}，查 {args.repeat} 次\n")
    else:
        print("必须提供 --snapshot 或 --phone")
        return 1

    # ---------- 逐号查询 ----------
    hdr = f"{'行':>5} {'号码':<13} {'已知真名':<24} {'返回结果':<48} 判定"
    print(hdr)
    print("-" * len(hdr))

    results = []
    n_stable = n_match = n_nodata = 0
    for row, phone, known in sample:
        got = []
        for k in range(args.repeat):
            got.append(ask(to_intl(phone)))
            if k < args.repeat - 1:
                time.sleep(args.gap)

        bad_prefix = ("HTTP", "ERR:", "BLOCKED:", "<empty>", "<badjson>")
        usable = [g for g in got if g and not g.startswith(bad_prefix)]
        uniq = sorted(set(usable))
        stable = len(uniq) == 1 and len(usable) == args.repeat
        match = bool(uniq) and bool(known) and norm(uniq[0]) == norm(known)

        n_stable += stable
        n_match += match
        n_nodata += (not usable)

        if not usable:
            verdict = "NO-DATA"
        elif not stable:
            verdict = f"❌ 随机({len(uniq)}种)"
        elif known and match:
            verdict = "✅ 一致"
        elif known:
            verdict = "⚠️ 稳定但不同"
        else:
            verdict = "✅ 幂等"

        shown = got[0] if len(set(got)) == 1 else " | ".join(got)
        print(f"{row:>5} {phone:<13} {known:<24} {shown[:48]:<48} {verdict}")
        results.append({"row": row, "phone": phone, "known": known,
                        "got": got, "unique": uniq,
                        "stable": stable, "match": match})

    # ---------- 判定 ----------
    n = len(sample)
    print("\n" + "=" * 60)
    print(f"幂等（{args.repeat} 次同名）：{n_stable}/{n}")
    if args.snapshot:
        print(f"与已知真名一致    ：{n_match}/{n}")
    print(f"无数据            ：{n_nodata}/{n}")

    ok = (n_stable == n)
    if args.snapshot:
        ok = ok and (n_match == n)

    if ok:
        print("\n结论：该源幂等" + ("且与已知真名一致" if args.snapshot else "")
              + " —— 可用于批量写入。")
        rc = 0
    elif n_stable == 0 and n_nodata == 0:
        print("\n结论：每次返回不同名字 —— **源已污染/降级，禁止写入任何数据**。")
        rc = 9
    elif n_nodata == n:
        print("\n结论：全部无数据 —— 无法判断（可能被限流或号码本身无记录）。")
        rc = 9
    else:
        print("\n结论：混合状态 —— 不可用于批量写入，需扩大样本人工复核。")
        rc = 9

    if args.out:
        json.dump(results, open(args.out, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print(f"明细 -> {args.out}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
