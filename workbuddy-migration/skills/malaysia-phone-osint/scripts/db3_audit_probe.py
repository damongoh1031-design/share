#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DB3 (CallApp) 可用性诊断 —— 只读，不写表。

目的：判定 DB3 能否用于「补充/审查」DB1 已写入 A 列的名字。
判据三条：
  1) 幂等性：同一号码连查 N 次是否返回同一名字（唯一可靠判据）
  2) 与 DB1 真名的一致率：抽 A 列已有名字的行，看 DB3 是否命中同名
  3) 形态学：返回名是否为美式姓名（污染特征）

用法：
  PY=.../osint/Scripts/python.exe
  "$PY" db3_audit_probe.py --sheet <sheet_now.json> --n 6 --repeat 3
"""
import argparse
import collections
import json
import random
import re
import time

import requests
import urllib3

urllib3.disable_warnings()

URL = ("https://s.callapp.com/callapp-server/csrch"
       "?cpn=%2B{phone}&myp=gp.106898501948939491020&ibs=0&cid=0")
HEADERS = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/91.0.4472.124 Safari/537.36")}


def intl(msisdn):
    d = re.sub(r"\D", "", str(msisdn or ""))
    if not d:
        return ""
    if d.startswith("60"):
        return d
    if d.startswith("0"):
        return "60" + d[1:]
    return "60" + d


def ask(phone):
    try:
        r = requests.get(URL.format(phone=phone), headers=HEADERS,
                         timeout=25, verify=False)
        if r.status_code != 200:
            return f"HTTP{r.status_code}"
        try:
            return (r.json() or {}).get("name", "") or "<empty>"
        except ValueError:
            return "<badjson>"
    except requests.RequestException as exc:
        return f"ERR:{type(exc).__name__}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True)
    ap.add_argument("--n", type=int, default=6, help="A 列已有名字的抽样数")
    ap.add_argument("--n-empty", type=int, default=2, help="A 列为空的抽样数")
    ap.add_argument("--repeat", type=int, default=3)
    ap.add_argument("--gap", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=20261008)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    rows = json.load(open(args.sheet, encoding="utf-8"))
    has, empty = [], []
    for i, r in enumerate(rows):
        a = (r[0] or "").strip() if len(r) > 0 else ""
        b = (r[1] or "").strip() if len(r) > 1 else ""
        if not b:
            continue
        (has if a else empty).append((i + 1, a, b))

    random.seed(args.seed)
    sample_has = random.sample(has, min(args.n, len(has)))
    sample_empty = random.sample(empty, min(args.n_empty, len(empty)))

    print(f"表内：A 列已有名字 {len(has)} 行 / A 列空 {len(empty)} 行")
    print(f"抽样：{len(sample_has)} 行（有名字）+ {len(sample_empty)} 行（无名字），"
          f"每行连查 {args.repeat} 次\n")

    recs = []
    for tag, group in (("HAS-DB1", sample_has), ("NO-DB1", sample_empty)):
        for row_no, a_name, phone in group:
            p = intl(phone)
            got = []
            for k in range(args.repeat):
                got.append(ask(p))
                if k < args.repeat - 1:
                    time.sleep(args.gap)
            usable = [g for g in got if not g.startswith(
                ("HTTP", "ERR:", "<empty>", "<badjson>"))]
            uniq = sorted(set(usable))
            stable = len(uniq) == 1
            match = bool(a_name) and a_name in uniq
            recs.append({"tag": tag, "row": row_no, "phone": phone,
                         "db1": a_name, "got": got, "uniq": uniq,
                         "stable": stable, "match_db1": match})
            print(f"[{tag}] 行{row_no} {phone}  DB1={a_name!r}")
            print(f"    DB3 -> {got}")
            print(f"    -> {'STABLE' if stable else f'RANDOM({len(uniq)}名)'}"
                  f"{'  同名✓' if match else ''}")

    print("\n========== 结论 ==========")
    st = [r for r in recs if r["stable"]]
    mt = [r for r in recs if r["match_db1"]]
    print(f"稳定（幂等）号码：{len(st)}/{len(recs)}")
    print(f"与 DB1 同名：{len(mt)}/{len([r for r in recs if r['db1']])}")
    if not st:
        print("→ DB3 当前输出**完全随机**，零信息量：既不能补充，也不能用于审查。")
    if args.out:
        json.dump(recs, open(args.out, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
