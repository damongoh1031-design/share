#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DB1 CallerID（aunumber.com）批量查名字 —— 带限流自愈的版本。

相比 v1 的改动（针对 2026-10-02 的 `{"status": -5}` 应用层封禁故障）：
  1. **开跑前先探活**：先单发 1 个已知回归号。被封就直接退出（exit 2），不浪费配额。
  2. **增量落盘**：每条结果立刻 append 到 JSONL，进程被杀也不丢数据。
  3. **`-5` 识别与熔断**：`-5` 不算「没数据」，算「被封」；连续 N 次即中止（exit 3）。
  4. **断点续跑**：`--resume` 读已有 JSONL，跳过已处理行。
  5. 任何退出路径都会把 JSONL 汇总成最终 `--out` JSON。

退出码：0=正常结束 / 2=开跑前探活发现被封 / 3=跑的过程中被封熔断

用法：
    PY="C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
    "$PY" db1_batch.py --probe                                  # 只探活
    "$PY" db1_batch.py --sheet sheetAB.json --startrow 1177 --want 100 --out r5.json
    "$PY" db1_batch.py --sheet sheetAB.json --startrow 1177 --want 100 --out r5.json --resume
"""
import argparse
import contextlib
import importlib.util
import io
import json
import os
import re
import sys
import time

# ---- 强制 stdout/stderr UTF-8 ----
# 2026-10-13 血泪：隐藏 cmd（无控制台）下 stdout 默认 GBK，命中名含非 GBK 字符（如 £ U+00A3、
# 中文、emoji）时 print 抛 UnicodeEncodeError -> 整个 db1_batch 崩溃 -> 不生成 --out JSON ->
# 驱动器 json.load 失败 exit 1。此处在启动时无条件重配为 utf-8，errors="replace" 兜底。
for _stream in ("stdout", "stderr"):
    try:
        _s = getattr(sys, _stream)
        if hasattr(_s, "reconfigure"):
            _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

REPO = os.environ.get(
    "PNL_REPO", r"C:/Users/Admin/AppData/Local/Temp/osintrepos/phone-number-lookup"
)
# 已知回归号：历史上稳定返回 "Prof Lee"。用它做探活基准。
PROBE_NUMBER = "60162281297"


def load_repo(repo):
    path = os.path.join(repo, "lookup.py")
    if not os.path.exists(path):
        raise SystemExit(f"找不到 {path}（用 --repo 或 PNL_REPO 指定 phone-number-lookup 目录）")
    spec = importlib.util.spec_from_file_location("pnl_lookup", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pnl_lookup"] = mod
    spec.loader.exec_module(mod)
    return mod


def local_to_intl(raw):
    d = re.sub(r"\D", "", raw or "")
    if d.startswith("60"):
        return d
    if d.startswith("0"):
        return "60" + d[1:]
    return "60" + d


def extract_json(text):
    marker = "DataBase 1 Information:"
    m = text.find(marker)
    if m < 0:
        return None
    rest = text[m + len(marker):]
    i = rest.find("{")
    if i < 0:
        return None
    try:
        obj, _ = json.JSONDecoder().raw_decode(rest[i:])
        return obj
    except Exception:
        return None


def is_blocked(obj):
    """应用层封禁标志：{"status": -5}（也可能有别的负 status）。"""
    if not isinstance(obj, dict):
        return False
    st = obj.get("status")
    try:
        return st is not None and int(st) < 0
    except (TypeError, ValueError):
        return False


def query(mod, intl, tries=2):
    """查一次。返回 (kind, payload)，kind = 'ok' | 'blocked' | 'error'。"""
    last = "no-json"
    for k in range(tries):
        cid = mod.CallerID()
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                cid.start_callerid_check(intl, True)
            obj = extract_json(buf.getvalue())
            if obj is None:
                last = "no-json"
            elif is_blocked(obj):
                return "blocked", obj          # 被封不重试，立刻上报
            else:
                return "ok", obj
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
        time.sleep(1.0 * (k + 1))
    return "error", last


def do_probe(mod, number=PROBE_NUMBER):
    kind, payload = query(mod, number, tries=1)
    if kind == "ok":
        print(f"[probe] OK  {number} -> {json.dumps(payload, ensure_ascii=False)[:120]}")
        return 0
    if kind == "blocked":
        print(f"[probe] BLOCKED  {number} -> {json.dumps(payload, ensure_ascii=False)}")
        return 2
    print(f"[probe] ERROR  {number} -> {payload}")
    return 2


def load_jsonl(path):
    recs = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    recs.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return recs


def consolidate(jsonl_path, out_path, meta):
    recs = load_jsonl(jsonl_path)
    found = [r for r in recs if r["kind"] == "found"]
    misses = [r for r in recs if r["kind"] == "miss"]
    blocked = [r for r in recs if r["kind"] == "blocked"]
    errors = [r for r in recs if r["kind"] == "error"]
    out = {
        "found": found, "misses": misses, "blocked": blocked, "errors": errors,
        "queried": len(recs), "startrow": meta["startrow"],
        "last_row": recs[-1]["row"] if recs else meta["startrow"] - 1,
        "note": meta.get("note", ""),
    }
    json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return out


def main():
    ap = argparse.ArgumentParser(description="DB1 CallerID 批量查名字（带限流熔断）")
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--in", dest="infile", help="纯号码文件，每行一个")
    ap.add_argument("--sheet", help="gog 导出的 [[A,B],...] JSON；A 非空的行自动跳过")
    ap.add_argument("--out", default="db1_results.json")
    ap.add_argument("--jsonl", help="增量落盘文件（默认 <out>.jsonl）")
    ap.add_argument("--want", type=int, default=50, help="找到多少个名字后停（0=不限）")
    ap.add_argument("--startrow", type=int, default=1, help="从第几行开始（1-based）")
    ap.add_argument("--maxrows", type=int, default=100000)
    ap.add_argument("--delay", type=float, default=0.4)
    ap.add_argument("--max-block", type=int, default=5,
                    help="连续多少次 -5 就熔断中止（默认 5）")
    ap.add_argument("--probe", action="store_true", help="只做一次探活后退出")
    ap.add_argument("--probe-number", default=PROBE_NUMBER)
    ap.add_argument("--no-probe", action="store_true", help="跳过开跑前的探活")
    ap.add_argument("--resume", action="store_true", help="跳过 JSONL 里已处理过的行")
    args = ap.parse_args()

    jsonl_path = args.jsonl or (args.out + ".jsonl")
    mod = load_repo(args.repo)

    if args.probe:
        return do_probe(mod, args.probe_number)

    # ---- 开跑前探活：被封就别浪费配额 ----
    if not args.no_probe:
        rc = do_probe(mod, args.probe_number)
        if rc != 0:
            print("[abort] 开跑前探活失败，未发起任何批量查询。")
            consolidate(jsonl_path, args.out, {"startrow": args.startrow,
                                               "note": "aborted at pre-run probe"})
            return rc

    # ---- 组装待查列表 ----
    done = set()
    if args.resume:
        done = {r["row"] for r in load_jsonl(jsonl_path)}
        print(f"[resume] 已有 {len(done)} 条记录，将跳过这些行")

    items = []
    if args.sheet:
        rows = json.load(open(args.sheet, encoding="utf-8"))
        for idx, r in enumerate(rows[: args.maxrows], 1):
            if idx < args.startrow or idx in done:
                continue
            a = (r[0] or "").strip() if len(r) > 0 else ""
            b = (r[1] or "").strip() if len(r) > 1 else ""
            if a or not b:
                continue
            items.append((idx, b))
    elif args.infile:
        for idx, line in enumerate(open(args.infile, encoding="utf-8"), 1):
            if idx < args.startrow or idx in done:
                continue
            p = line.strip().split("\t")[-1].strip()
            if p:
                items.append((idx, p))
    else:
        raise SystemExit("必须给 --sheet 或 --in")

    # ---- 主循环 ----
    jl = open(jsonl_path, "a", encoding="utf-8")
    n_found = sum(1 for r in load_jsonl(jsonl_path) if r["kind"] == "found")
    consec_block = 0
    status = "completed: input exhausted"
    for row, phone in items:
        kind, payload = query(mod, local_to_intl(phone))

        if kind == "blocked":
            consec_block += 1
            jl.write(json.dumps({"row": row, "phone": phone, "kind": "blocked",
                                 "payload": payload}, ensure_ascii=False) + "\n")
            jl.flush()
            print(f"row{row} {phone} BLOCKED {payload}", flush=True)
            if consec_block >= args.max_block:
                status = f"aborted: {consec_block} consecutive blocked"
                print(f"\n[abort] 连续 {consec_block} 次被封，中止。已落盘 {jsonl_path}")
                break
            time.sleep(args.delay)
            continue

        consec_block = 0

        if kind == "error":
            jl.write(json.dumps({"row": row, "phone": phone, "kind": "error",
                                 "err": payload}, ensure_ascii=False) + "\n")
            jl.flush()
            print(f"row{row} {phone} ERROR {payload}", flush=True)
        else:
            name = (payload.get("name") or "").strip()
            if name:
                jl.write(json.dumps({
                    "row": row, "phone": phone, "kind": "found", "name": name,
                    "area": payload.get("belong_area", ""),
                    "type_label": payload.get("type_label", ""),
                    "report_count": payload.get("report_count", ""),
                }, ensure_ascii=False) + "\n")
                jl.flush()
                n_found += 1
                print(f"row{row} {phone} -> {name}", flush=True)
            else:
                jl.write(json.dumps({"row": row, "phone": phone, "kind": "miss"},
                                    ensure_ascii=False) + "\n")
                jl.flush()
                print(f"row{row} {phone} -> (empty)", flush=True)

        time.sleep(args.delay)
        if args.want and n_found >= args.want:
            status = "completed: reached --want"
            break

    jl.close()
    out = consolidate(jsonl_path, args.out, {"startrow": args.startrow, "note": status})
    print(f"\n== startrow {args.startrow} | {status}")
    print(f"== queried {out['queried']} | found {len(out['found'])} | miss {len(out['misses'])} "
          f"| blocked {len(out['blocked'])} | err {len(out['errors'])} | last_row {out['last_row']}")
    denom = len(out["found"]) + len(out["misses"])
    if denom:
        print(f"== 覆盖率 {len(out['found'])}/{denom} = {len(out['found'])/denom:.0%}")
    print(f"== 结果 -> {args.out}  (增量日志 {jsonl_path})")
    return 3 if status.startswith("aborted") else 0


if __name__ == "__main__":
    sys.exit(main())
