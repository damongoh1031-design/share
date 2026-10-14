#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""连续跑 DB1 批次，直到被封 / 输入耗尽 / 达到批数上限。

每轮：导出快照(A:C) -> 跑一批(db1_batch.py) -> 回写 A 列 -> 回读校验 -> 间隔 -> 下一轮。

设计要点（都是踩过坑换来的）：
  1. 全程用「快照为底 + 只覆盖 found 行」写 A 列，写入前逐行 assert 目标格为空
     -> 不会抹掉区间里本来就有的名字。
  2. 标记列（C）**不写**，只用「写入前后逐行 diff」做校验；发现变化只告警不中止
     （该列可能被人工/另一条 CRM 流程并发修改，用「等于常数」校验会误判）。
  3. 跑批脚本的 stdout 全部重定向到日志文件，不污染调用方上下文。
  4. 文件锁：同一份表格同时只允许一个驱动进程；重复触发直接 exit 4。
  5. 每批结束写状态文件（含 next_start_row），供定时任务判断是否该续跑。

退出码：0 正常收口 / 2 开跑前被封 / 3 中途被封 / 4 已有实例在跑 / 5 校验失败 / 6 快照导出失败

用法：
  PY=C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe
  "$PY" db1_sheet_batch_driver.py \
      --spreadsheet-id <ID> --sheet "SHOPEE LIST 01" \
      --start-row 3124 --first-batch 11 --want 100 --max-batches 8 \
      --sleep-between 300
"""
import argparse
import ctypes
import json
import os
import subprocess
import sys
import time

# ---- 强制 stdout/stderr UTF-8（隐藏 cmd 下默认 GBK，中文 print 会崩）----
# 2026-10-13：同类问题已导致 db1_batch 崩溃，此处一并加固。
for _stream in ("stdout", "stderr"):
    try:
        _s = getattr(sys, _stream)
        if hasattr(_s, "reconfigure"):
            _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

GOG = r"C:/Users/Admin/.workbuddy-ai/bin/gog/gog.exe"
PY = r"C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
BATCH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db1_batch.py")
TMP = r"C:/Users/Admin/AppData/Local/Temp"

# GetExitCodeProcess 的 STILL_ACTIVE
_STILL_ACTIVE = 259


def sh(cmd, timeout=900):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True,
                          timeout=timeout, encoding="utf-8", errors="replace")


def gog_json(cmd, tries=3, timeout=900, need_json=True):
    """跑 gog，返回 (ok, data_or_text)。

    必须重试：gog 偶发返回空 stdout（exit 0 但无输出），
    2026-10-06 实测导致回读校验 json.loads 崩溃、整个驱动器中断。
    """
    last = None
    for k in range(tries):
        r = sh(cmd, timeout=timeout)
        txt = (r.stdout or "").strip()
        if r.returncode == 0 and txt:
            if not need_json:
                return True, txt
            try:
                return True, json.loads(txt)
            except json.JSONDecodeError as exc:
                last = f"JSONDecodeError: {exc} | 头80字={txt[:80]!r}"
                print(f"  [gog] 第{k+1}次返回非 JSON，重试…", flush=True)
        else:
            last = (f"rc={r.returncode} stdout={txt[:80]!r} "
                    f"stderr={(r.stderr or '')[:120]!r}")
            print(f"  [gog] 第{k+1}次失败，重试… {last}", flush=True)
        time.sleep(2 * (k + 1))
    return False, last


def pid_alive(pid):
    """Windows 原生存活检测。

    不用 tasklist：本机沙箱里 MSYS 会把 /FI 参数转成路径导致输出为空，
    会造成「误判为已死」→ 两个驱动同时写同一列。也不用 os.kill(pid, 0)——
    Windows 上它等价于 TerminateProcess，会真的杀掉对方进程。
    """
    if pid <= 0:
        return False
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    h = k32.OpenProcess(0x1000, False, pid)          # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return False
    try:
        code = ctypes.c_ulong()
        if not k32.GetExitCodeProcess(h, ctypes.byref(code)):
            return False
        return code.value == _STILL_ACTIVE
    finally:
        k32.CloseHandle(h)


def cell(row, i):
    return (row[i] or "").strip() if len(row) > i else ""


class Lock:
    """极简 PID 锁，防止定时任务与手动跑批撞车（同表并发写 = 数据风险）。"""

    def __init__(self, path):
        self.path = path
        self.held = False

    def acquire(self):
        if os.path.exists(self.path):
            try:
                old = int(open(self.path, encoding="utf-8").read().strip() or 0)
            except (ValueError, OSError):
                old = 0
            if old and old != os.getpid() and pid_alive(old):
                return False
            print(f"[lock] 陈旧锁文件（PID {old} 已不在），覆盖", flush=True)
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write(str(os.getpid()))
        self.held = True
        return True

    def release(self):
        if self.held:
            try:
                os.remove(self.path)
            except OSError:
                pass
            self.held = False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spreadsheet-id", required=True)
    ap.add_argument("--sheet", default="SHOPEE LIST 01")
    ap.add_argument("--col-a", default="A", help="名字列（写入目标）")
    ap.add_argument("--col-b", default="B", help="号码列（查询源）")
    ap.add_argument("--col-marker", default="C", help="外部标记列（只读，绝不写入）")
    ap.add_argument("--start-row", type=int, required=True)
    ap.add_argument("--first-batch", type=int, default=1)
    ap.add_argument("--want", type=int, default=100, help="每批目标命中数（不是查询上限）")
    ap.add_argument("--max-batches", type=int, default=8)
    ap.add_argument("--max-rows", type=int, default=10000)
    ap.add_argument("--sleep-between", type=int, default=0,
                    help="批间休眠秒数。滚动窗口限速场景建议 300（5 分钟）")
    ap.add_argument("--workdir", default=TMP)
    ap.add_argument("--state-file", default=os.path.join(TMP, "db1_autostate.json"))
    ap.add_argument("--lock-file", default=os.path.join(TMP, "db1_driver.lock"))
    ap.add_argument("--no-lock", action="store_true")
    ap.add_argument("--skip-idempotent", action="store_true",
                    help="跳过幂等性门禁（不建议；见 SKILL.md §12）")
    ap.add_argument("--resume", action="store_true",
                    help="透传给 db1_batch：读已有 JSONL 跳过已处理行（中断后续跑用）")
    args = ap.parse_args()

    # ---------- 0) 幂等性门禁：防止数据源静默返回随机假名 ----------
    if not args.skip_idempotent:
        ck = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "check_idempotent.py")
        r = sh(f'"{PY}" "{ck}" --source db1 --phone 60162281297 --repeat 3 --gate')
        print(r.stdout.strip(), flush=True)
        if r.returncode != 0:
            print("STOP: 幂等性门禁未通过（数据源可能返回随机假名），中止。"
                  "确要认真跑可加 --skip-idempotent。", flush=True)
            return 9

    lock = Lock(args.lock_file)
    if not args.no_lock and not lock.acquire():
        print(f"已有驱动实例在跑（{args.lock_file}），本次退出。", flush=True)
        return 4

    wd = args.workdir
    sheet_range = f"'{args.sheet}'"
    ca, cb, cm = args.col_a, args.col_b, args.col_marker
    start_row, batch = args.start_row, args.first_batch
    summary = []
    rc_final = 0

    try:
        for _ in range(args.max_batches):
            snap = f"{wd}/sheetAB{batch}.json"
            out = f"{wd}/r{batch}.json"
            log = f"{wd}/r{batch}.log"
            colf = f"{wd}/colA{batch}.json"

            # ---------- 1) 快照（含标记列，用于 diff） ----------
            ok, rows = gog_json(
                f'"{GOG}" sheets get {args.spreadsheet_id} '
                f'"{sheet_range}!{ca}1:{cm}{args.max_rows}" -j '
                f'--results-only --render FORMATTED_VALUE')
            if ok:
                json.dump(rows, open(snap, "w", encoding="utf-8"),
                          ensure_ascii=False)
            try:
                if not ok:
                    raise ValueError(f"gog 取数失败：{rows}")
                if not isinstance(rows, list) or not rows:
                    raise ValueError("空表")
            except Exception as exc:                       # noqa: BLE001
                print(f"\nSTOP: 快照导出失败（{exc}）", flush=True)
                rc_final = 6
                break
            mi = ord(cm) - ord("A")
            a_before = sum(1 for x in rows if cell(x, 0))
            c_before = {i + 1: cell(x, mi) for i, x in enumerate(rows)}
            print(f"\n===== 批 {batch} | 起点行 {start_row} | "
                  f"A 列非空 {a_before} | {cm} 列非空 "
                  f"{sum(1 for v in c_before.values() if v)} =====", flush=True)

            # ---------- 2) 跑批（stdout -> 日志） ----------
            t0 = time.time()
            rc = subprocess.run(
                f'"{PY}" "{BATCH}" --sheet "{snap}" --startrow {start_row} '
                f'--want {args.want} --out "{out}"'
                + (" --resume" if args.resume else "")
                + f' > "{log}" 2>&1',
                shell=True).returncode
            dt = time.time() - t0

            if not os.path.exists(out):
                # db1_batch 未产出汇总 JSON = 子进程中途崩溃（曾因 stdout 编码崩溃）。
                # 不清除 JSONL，保留现场供 --resume 续跑；打印子日志尾部说明原因。
                print(f"\nSTOP: db1_batch 未生成 {out}（子进程异常退出，rc={rc}）。"
                      f"见 {log} 尾部。中止本批。", flush=True)
                try:
                    tail = open(log, encoding="utf-8", errors="replace").read()[-600:]
                    print(f"  --- {log} 尾部 ---\n{tail}", flush=True)
                except Exception:
                    pass
                rc_final = 7
                break
            d = json.load(open(out, encoding="utf-8"))
            found, last = d["found"], d["last_row"]
            print(f"  跑批 rc={rc} 耗时 {dt/60:.1f}m | queried={d['queried']} "
                  f"found={len(found)} blocked={len(d['blocked'])} "
                  f"err={len(d['errors'])} last_row={last}", flush=True)

            entry = {"batch": batch, "start": start_row, "last": last,
                     "queried": d["queried"], "found": len(found),
                     "blocked": len(d["blocked"]), "errors": len(d["errors"]),
                     "minutes": round(dt / 60, 1), "rc": rc}

            # ---------- 3) 回写 A 列 ----------
            if found:
                vals = [[cell(rows[i - 1], 0)] for i in range(start_row, last + 1)]
                keep = [i for i in range(start_row, last + 1)
                        if vals[i - start_row][0]]
                for f in found:
                    i = f["row"] - start_row
                    assert vals[i][0] == "", \
                        f"目标格非空 row={f['row']} {vals[i]!r}"
                    vals[i][0] = f["name"]
                json.dump(vals, open(colf, "w", encoding="utf-8"),
                          ensure_ascii=False)
                ok, info = gog_json(f'"{GOG}" sheets update {args.spreadsheet_id} '
                                    f'"{sheet_range}!{ca}{start_row}:{ca}{last}" '
                                    f'--values-json @{colf} --input RAW -j')
                if not ok:
                    print(f"  !!! 写入失败（已重试）：{info}\n"
                          f"      → 数据未落表，回写数组留在 {colf}，可手工重放。停止。",
                          flush=True)
                    rc_final = 5
                    break
                print(f"  写入 {ca}{start_row}:{ca}{last} found={len(found)} "
                      f"preserved={keep} "
                      f"{json.dumps(info, ensure_ascii=False)[:90]}", flush=True)

                # ---------- 4) 回读校验 ----------
                ok, v = gog_json(
                    f'"{GOG}" sheets get {args.spreadsheet_id} '
                    f'"{sheet_range}!{ca}1:{cm}{args.max_rows}" -j '
                    f'--results-only --render FORMATTED_VALUE')
                if not ok:
                    print(f"  !!! 回读失败（已重试）：{v}\n"
                          f"      → 写入可能已生效但无法校验。停止以免重复扫。",
                          flush=True)
                    rc_final = 5
                    break
                a_after = sum(1 for x in v if cell(x, 0))
                matched = sum(1 for f in found
                              if cell(v[f["row"] - 1], 0) == f["name"])
                kept_ok = all(cell(v[i - 1], 0) for i in keep)
                c_after = {i + 1: cell(x, mi) for i, x in enumerate(v)}
                c_added = [r for r, val in c_after.items()
                           if val and val != c_before.get(r, "")]
                c_removed = [r for r, val in c_before.items()
                             if val and val != c_after.get(r, "")]
                print(f"  校验 matched={matched}/{len(found)} "
                      f"preserved_ok={kept_ok} A={a_before}->{a_after} "
                      f"{cm}列 新增{c_added} 移除{c_removed}", flush=True)

                entry.update({"a_total": a_after, "preserved": keep,
                              "marker_added": c_added,
                              "marker_removed": c_removed})
                bad = False
                if matched != len(found):
                    print("  !!! matched 不一致，停止", flush=True)
                    bad = True
                if not kept_ok:
                    print("  !!! preserved 行丢失，停止", flush=True)
                    bad = True
                if a_after != a_before + len(found):
                    print(f"  !!! A 列总数不符（期望 {a_before + len(found)}，"
                          f"实际 {a_after}），停止", flush=True)
                    bad = True
                if c_added or c_removed:
                    print(f"  !!! {cm} 列被外部改动（新增 {c_added} / 移除 "
                          f"{c_removed}）—— 该列由另一条流程/人工维护，我们未写入。"
                          f"仅告警，继续。", flush=True)
                if bad:
                    summary.append(entry)
                    rc_final = 5
                    break
                summary.append(entry)          # 成功路径也必须记账，
                start_row = last + 1           # 否则汇总/状态文件全是 0（2026-10-06 修）
            else:
                entry["note"] = "no found"
                summary.append(entry)
                if last >= start_row:
                    start_row = last + 1

            # ---------- 5) 终止判断 ----------
            # 兜底记账：正常路径已在上面 append(entry)，此处只在未记账时补记，
            # 否则封禁/异常分支会把同一批重复计入（2026-10-08 修：批 23 曾被记两次）。
            if not (summary and summary[-1] is entry):
                summary.append(entry)
            if rc == 2:
                print("\nSTOP: 开跑前探活即被封（exit 2），未发起批量查询。", flush=True)
                rc_final = 2
                break
            if rc == 3:
                print("\nSTOP: 中途被封熔断（exit 3），已命中部分已落表。", flush=True)
                rc_final = 3
                break
            if rc != 0:
                print(f"\nSTOP: 退出码 {rc}（非封禁的异常）。", flush=True)
                rc_final = rc
                break
            if d["queried"] == 0:
                print("\nSTOP: 没有可查的行（输入耗尽）。", flush=True)
                break

            if args.sleep_between and batch - args.first_batch < args.max_batches - 1:
                print(f"  [rate] 批间休眠 {args.sleep_between}s（滚动窗口限速）",
                      flush=True)
                time.sleep(args.sleep_between)
            batch += 1
    finally:
        lock.release()

    json.dump({"summary": summary, "next_start_row": start_row},
              open(os.path.join(wd, "run_batches_summary.json"), "w",
                   encoding="utf-8"), ensure_ascii=False, indent=2)

    # 状态文件：供定时任务判断「上次跑到哪、是否该续跑」
    tq = sum(s["queried"] for s in summary)
    tf = sum(s["found"] for s in summary)
    if tf:
        json.dump({"last_success": {
            "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "start_row": summary[0]["start"], "scanned_to_row": start_row - 1,
            "queried": tq, "hits": tf, "next_start_row": start_row,
            "a_nonempty": summary[-1].get("a_total"),
            "marker_nonempty": None,
        }}, open(args.state_file, "w", encoding="utf-8"),
            ensure_ascii=False, indent=2)

    print("\n========== 汇总 ==========")
    for s in summary:
        print(f"批 {s['batch']}: 行{s['start']}-{s['last']} 查{s['queried']} "
              f"命中{s['found']} blocked={s['blocked']} {s['minutes']}m "
              f"rc={s['rc']}")
    print(f"合计: 查 {tq} 命中 {tf} | 下一批起点 行 {start_row} | rc={rc_final}")
    print("DONE")
    return rc_final


if __name__ == "__main__":
    sys.exit(main())
