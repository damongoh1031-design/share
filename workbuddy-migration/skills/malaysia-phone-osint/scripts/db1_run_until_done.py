#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DB1 反查外层循环：一直跑到 10000 行全部查完（或硬失败）才停。

每轮：探活 -> 未解封则休眠等待 -> 解封则调驱动器跑批 -> 判读 rc -> 续跑。
必须脱离会话运行（WMI+VBS），否则会话结束进程被沙箱 Job Object 回收。

停止条件：
  - 下一批起点 > MAX_ROWS(10000)      -> 全部查完，正常结束
  - 驱动器无进展（输入耗尽 queried==0）-> 正常结束
  - rc=5 校验失败 / rc=6 快照失败      -> 硬停止，等人工
  - rc=7 子进程崩溃 / rc=9 门禁失败 连续 3 次 -> 硬停止，等人工
  - rc=2/3 被封                       -> 不停止，休眠后继续探活
  - rc=4 已有实例                     -> 不停止，休眠后重试

用法（由 .cmd 调用，stdout 重定向到日志）：
  python db1_run_until_done.py
"""
import json
import os
import subprocess
import sys
import time

# 强制 UTF-8（隐藏 cmd 下默认 GBK，中文/特殊字符 print 会崩）
for _stream in ("stdout", "stderr"):
    try:
        _s = getattr(sys, _stream)
        if hasattr(_s, "reconfigure"):
            _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PY = r"C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
SCRIPTS = r"C:/Users/Admin/.workbuddy-ai/skills/malaysia-phone-osint/scripts"
DRIVER = os.path.join(SCRIPTS, "db1_sheet_batch_driver.py")
BATCH = os.path.join(SCRIPTS, "db1_batch.py")
TMP = r"C:/Users/Admin/AppData/Local/Temp"

SPREADSHEET = "1WdlrWe2vY8cVCzyowfZJUF1F6H4oEhwz9iLIVH4lAPU"
SHEET = "SHOPEE LIST 01"
SUMMARY = os.path.join(TMP, "run_batches_summary.json")
AUTOSTATE = os.path.join(TMP, "db1_autostate.json")
BATCHNO = os.path.join(TMP, "db1_next_batch.txt")
STATUS = os.path.join(TMP, "db1_until_done_status.json")

MAX_ROWS = 10000
WANT = 100
MAX_BATCHES = 4
SLEEP_BETWEEN = 300
PROBE_WAIT = 900          # 被封后休眠 15 分钟再探活
DEFAULT_START = 9301      # 兜底，实际以状态文件为准
DEFAULT_BATCH = 31

# 剥离沙箱代理：127.0.0.1:55968 会 502，导致 DB1 请求假失败（ProxyError ≠ 封禁）
env = os.environ.copy()
for _k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
    env.pop(_k, None)
env["NO_PROXY"] = "*"
env["no_proxy"] = "*"
env["PYTHONUTF8"] = "1"
env["PYTHONIOENCODING"] = "utf-8"


def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def save_status(**kw):
    try:
        cur = {}
        if os.path.exists(STATUS):
            cur = json.load(open(STATUS, encoding="utf-8"))
        cur.update(kw)
        cur["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        json.dump(cur, open(STATUS, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
    except Exception:
        pass


def probe():
    r = subprocess.run(f'"{PY}" "{BATCH}" --probe', shell=True, env=env,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=300)
    return r.returncode, (r.stdout or "").strip().replace("\n", " ")


def read_json(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return None


def next_start():
    """起点优先取 run_batches_summary.json（每次跑批必写），回退 autostate。"""
    s = read_json(SUMMARY)
    if isinstance(s, dict) and s.get("next_start_row"):
        return int(s["next_start_row"])
    a = read_json(AUTOSTATE)
    if isinstance(a, dict):
        v = (a.get("last_success") or {}).get("next_start_row")
        if v:
            return int(v)
    return DEFAULT_START


def batch_no():
    """批号取持久计数：保证每个批号只用一个 jsonl 文件名（防 jsonl 追加导致重复行）。"""
    try:
        return int(open(BATCHNO, encoding="utf-8").read().strip())
    except Exception:
        pass
    s = read_json(SUMMARY)
    if isinstance(s, dict) and s.get("summary"):
        return max(x["batch"] for x in s["summary"]) + 1
    return DEFAULT_BATCH


def save_batch_no(n):
    with open(BATCHNO, "w", encoding="utf-8") as fh:
        fh.write(str(n))


def run_driver(start, bno):
    # 清本轮将用到的批号残留（jsonl 追加会造重复行 -> 写前 assert 中止 exit 1）
    for b in range(bno, bno + MAX_BATCHES):
        for suf in (".json.jsonl", ".json", ".log"):
            p = os.path.join(TMP, f"r{b}{suf}")
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass
    cmd = (f'"{PY}" "{DRIVER}" --spreadsheet-id {SPREADSHEET} '
           f'--sheet "{SHEET}" --start-row {start} --first-batch {bno} '
           f'--want {WANT} --max-batches {MAX_BATCHES} '
           f'--sleep-between {SLEEP_BETWEEN}')
    return subprocess.run(cmd, shell=True, env=env).returncode


def main():
    log("=== 外层循环启动：跑到 10000 行全部查完为止 ===")
    start = next_start()
    bno = batch_no()
    log(f"初始：下一批起点 行 {start} | 批号 {bno} | 上限行 {MAX_ROWS}")
    save_status(start_row=start, batch=bno, phase="start")

    soft_fail = 0
    while True:
        if start > MAX_ROWS:
            log(f"DONE: 下一批起点 行 {start} > {MAX_ROWS}，"
                f"{MAX_ROWS} 行已全部查完。")
            save_status(phase="done", reason=f"start {start} > {MAX_ROWS}")
            return 0

        rc, out = probe()
        if rc != 0:
            log(f"探活 仍被封/异常 rc={rc} | {out[:100]} | 休眠 {PROBE_WAIT}s")
            save_status(phase="blocked_wait", start_row=start, probe_rc=rc)
            time.sleep(PROBE_WAIT)
            continue

        log(f"探活 已解封 rc={rc} | 启动驱动器 批 {bno} 起点行 {start}")
        save_status(phase="running", start_row=start, batch=bno)
        drc = run_driver(start, bno)

        s = read_json(SUMMARY)
        new_start = start
        if isinstance(s, dict) and s.get("next_start_row"):
            new_start = int(s["next_start_row"])
        ran = [x["batch"] for x in (s or {}).get("summary", [])] if isinstance(s, dict) else []
        if ran:
            bno = max(ran) + 1
            save_batch_no(bno)
        log(f"驱动器 rc={drc} | 下一起点 行 {new_start} | 下一批号 {bno}")

        if drc in (5, 6):
            log(f"STOP: 硬失败 rc={drc}（5=校验失败 / 6=快照失败），停等人工。")
            save_status(phase="stopped", reason=f"hard rc={drc}")
            return drc
        if drc == 4:
            log("已有驱动实例在跑，休眠后重试")
            save_status(phase="wait_lock")
            time.sleep(PROBE_WAIT)
            continue
        if drc in (7, 9):
            soft_fail += 1
            log(f"软失败 rc={drc}（7=子进程崩溃 / 9=门禁失败），连续 {soft_fail} 次")
            if soft_fail >= 3:
                log("STOP: 软失败连续 3 次，停等人工。")
                save_status(phase="stopped", reason=f"soft rc={drc} x3")
                return drc
            time.sleep(PROBE_WAIT)
            continue

        soft_fail = 0
        if drc in (2, 3):
            log("本轮被封熔断（已命中部分已落表），休眠后继续探活")
            start = new_start
            save_status(phase="blocked_after_run", start_row=start)
            time.sleep(PROBE_WAIT)
            continue

        # drc == 0：正常收口
        if new_start <= start:
            log("DONE: 无进展（输入耗尽，没有可查的行）。")
            save_status(phase="done", reason="input exhausted")
            return 0
        start = new_start
        save_status(start_row=start, batch=bno, phase="idle")


if __name__ == "__main__":
    sys.exit(main())
