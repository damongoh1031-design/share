#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CallApp → Google Sheet 批量回填器（「号码列 → 名字列」）

对应 SKILL.md §11 的批量作业，但数据源换成 **DB3 CallApp**（DB1 已封）。

设计要点（都是踩过的坑）：
  * 开跑前探活（probe）；探活失败直接 exit 2，零批量请求
  * **增量落盘** JSONL，杀进程不丢结果
  * `--resume` 从 JSONL 断点续跑
  * 只写「A 列为空 且 C 列 ≠ X」的行；**A 列已有名字的行原样保留**
  * 回写数组以导出快照为底，只覆盖 found 行 → 绝不会清空原有名字
  * 写入前逐行 assert 目标格原本为空

用法:
    PY="C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
    "$PY" callapp_sheet_batch.py --sheet sheet_abc.json --rows 500 --out r1.json
    "$PY" callapp_sheet_batch.py --sheet sheet_abc.json --rows 500 --out r1.json --resume
    "$PY" callapp_sheet_batch.py --probe

退出码: 0 正常 / 2 探活失败 / 3 中途熔断 / 5 校验失败
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from callapp_lookup import lookup, normalize  # noqa: E402

SKIP_C_VALUES = {"X"}          # C 列这些值 → 跳过
MAX_CONSEC_EMPTY = 40          # 连续空响应熔断（空=未命中，正常；连续过多说明接口异常）
MAX_CONSEC_BLOCK = 3           # 连续限流熔断（HTTP 513 / X_C_CODE -4）


def cell(row, i):
    return (row[i] if i < len(row) and row[i] is not None else "").strip()


def load_snapshot(path):
    d = json.load(open(path, encoding="utf-8"))
    rows = []
    for idx, r in enumerate(d):
        rows.append({
            "rownum": idx + 1,
            "A": cell(r, 0),
            "B": cell(r, 1),
            "C": cell(r, 2),
        })
    return rows


def build_targets(rows, start_row=1):
    """A 空 且 C∉SKIP 且 B 非空 且 行号>=start_row"""
    out = []
    for r in rows:
        if r["rownum"] < start_row:
            continue
        if not r["B"]:
            continue
        if r["A"]:
            continue                      # 已有名字 → 保留，不动
        if r["C"].upper() in SKIP_C_VALUES:
            continue                      # C=X → 跳过
        out.append(r)
    return out


def load_done(jsonl):
    done = {}
    if os.path.exists(jsonl):
        with open(jsonl, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    done[rec["rownum"]] = rec
                except Exception:
                    continue
    return done


def main() -> int:
    ap = argparse.ArgumentParser(description="CallApp → Sheet 批量回填")
    ap.add_argument("--sheet", help="A/B/C 列快照 JSON（gog sheets get 导出）")
    ap.add_argument("--out", help="结果 JSON 路径")
    ap.add_argument("--start-row", type=int, default=1)
    ap.add_argument("--rows", type=int, default=500, help="本次最多扫描多少个「可查行」")
    ap.add_argument("--want", type=int, default=0, help="最多收集多少个命中（0=不限）")
    ap.add_argument("--delay", type=float, default=0.35)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--emit-colA", action="store_true",
                    help="同时生成回写数组 <out>.colA.json（默认开启）")
    args = ap.parse_args()

    # ---- 探活 ----
    probe_num = normalize("0162281297")
    pr = lookup(probe_num)
    probe_name = (pr.get("raw") or {}).get("name")
    if pr.get("blocked"):
        print(f"[probe] BLOCKED -> {pr['error']}  （限流中，等一会再试）")
        return 2
    if pr.get("degraded"):
        print(f"[probe] DEGRADED -> {pr['error']}  （凭据不完整，会返回假数据，拒绝开跑）")
        return 2
    if not (pr["ok"] and probe_name):
        print(f"[probe] FAIL -> {pr.get('error') or '空响应'}")
        return 2
    print(f"[probe] OK  {probe_num} -> {probe_name!r}")
    if args.probe:
        return 0

    if not args.sheet or not args.out:
        ap.error("--sheet 与 --out 必填")

    rows = load_snapshot(args.sheet)
    targets = build_targets(rows, args.start_row)
    print(f"[sheet] 总行 {len(rows)}  |  A 非空 {sum(1 for r in rows if r['A'])}"
          f"  |  C=X {sum(1 for r in rows if r['C'].upper() in SKIP_C_VALUES)}"
          f"  |  可查行 {len(targets)}")

    jsonl = args.out + "l"          # r1.json -> r1.jsonl
    done = load_done(jsonl) if args.resume else {}
    if args.resume and done:
        print(f"[resume] 已有 {len(done)} 条结果，跳过这些行")

    todo = [t for t in targets if t["rownum"] not in done][: args.rows]
    print(f"[run] 本次计划查询 {len(todo)} 行（行 {todo[0]['rownum']}–{todo[-1]['rownum']}）"
          if todo else "[run] 无待查行")
    if not todo:
        return 0

    found = sum(1 for v in done.values() if v.get("name"))
    miss = sum(1 for v in done.values() if v.get("status") == "miss")
    err = sum(1 for v in done.values() if v.get("status") == "error")
    blocked = sum(1 for v in done.values() if v.get("status") == "blocked")
    consec_block = 0
    t0 = time.time()
    aborted = False

    with open(jsonl, "a", encoding="utf-8") as jf:
        for i, t in enumerate(todo, 1):
            num = normalize(t["B"])
            r = lookup(num)
            name = (r.get("raw") or {}).get("name") if r["ok"] else None

            if r.get("blocked"):
                status, consec_block, consec_empty = "blocked", consec_block + 1, 0
                blocked += 1
            elif r.get("degraded"):
                # 🚨 匿名降级路径：返回的是随机记录，绝不能当 found 写进表
                status, consec_block, consec_empty = "degraded", 0, 0
                err += 1
            elif not r["ok"]:
                status, consec_block, consec_empty = "error", 0, 0
                err += 1
            elif not name:
                status, consec_block, consec_empty = "miss", 0, consec_empty + 1
                miss += 1
            else:
                status, consec_block, consec_empty = "found", 0, 0
                found += 1

            rec = {"rownum": t["rownum"], "phone": t["B"], "norm": num,
                   "name": name, "status": status,
                   "priority": (r.get("raw") or {}).get("priority"),
                   "err": r.get("error")}
            jf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            jf.flush()
            os.fsync(jf.fileno())

            if i % 25 == 0 or i == len(todo):
                el = time.time() - t0
                rate = i / el if el else 0
                print(f"  [{i}/{len(todo)}] found={found} miss={miss} "
                      f"blocked={blocked} err={err} "
                      f"({rate:.2f} 行/秒, 已用 {el/60:.1f} 分)")

            if args.want and found >= args.want:
                print(f"[stop] 已达 --want {args.want}")
                break
            if consec_block >= MAX_CONSEC_BLOCK:
                print(f"[abort] 连续 {consec_block} 次限流（HTTP 513 / X_C_CODE -4），熔断")
                aborted = True
                break
            if consec_empty >= MAX_CONSEC_EMPTY:
                print(f"[abort] 连续 {consec_empty} 次空响应，疑似接口异常，熔断")
                aborted = True
                break
            time.sleep(args.delay)

    # ---- 汇总 ----
    allrec = load_done(jsonl)
    summary = {
        "queried": len(allrec),
        "found": sum(1 for v in allrec.values() if v.get("name")),
        "miss": sum(1 for v in allrec.values() if v.get("status") == "miss"),
        "blocked": sum(1 for v in allrec.values() if v.get("status") == "blocked"),
        "degraded": sum(1 for v in allrec.values() if v.get("status") == "degraded"),
        "error": sum(1 for v in allrec.values() if v.get("status") == "error"),
        "hits": {str(k): v["name"] for k, v in sorted(allrec.items())
                 if v.get("name")},
    }
    json.dump(summary, open(args.out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"[out] {args.out}  查询 {summary['queried']} / 命中 {summary['found']} "
          f"/ 空 {summary['miss']} / 限流 {summary['blocked']} "
          f"/ 降级 {summary['degraded']} / 错 {summary['error']}")

    # ---- 回写数组：以快照为底，只覆盖 found 行 ----
    colA = [r["A"] for r in rows]
    written = 0
    for rownum, v in allrec.items():
        if not v.get("name"):
            continue
        idx = rownum - 1
        if idx < 0 or idx >= len(colA):
            continue
        # 逐行 assert：目标格原本必须为空（防止覆盖人工填写的名字）
        assert colA[idx] == "", f"行 {rownum} 的 A 列非空({colA[idx]!r})，拒绝覆盖"
        colA[idx] = v["name"]
        written += 1
    colA_path = args.out + ".colA.json"
    json.dump(colA, open(colA_path, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"[writeback] {colA_path}  共 {len(colA)} 行，本次填入 {written} 个名字")

    # ---- 校验：非空数 = 原非空 + 本次填入 ----
    orig_nonempty = sum(1 for r in rows if r["A"])
    new_nonempty = sum(1 for c in colA if c.strip())
    expect = orig_nonempty + written
    if new_nonempty != expect:
        print(f"[verify] ❌ 非空数 {new_nonempty} != 预期 {expect}")
        return 5
    print(f"[verify] ✅ A 列非空 {orig_nonempty} -> {new_nonempty} (+{written})")

    if aborted:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
