#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
 supervise.py  v1.1.0  —— 全量采集的「自适应守护 + 监督报告」
================================================================================
 本脚本不修改 scrape_malaysiayp.py，只做四件事：
   1. 守护   反复推进全量采集，直到脚本自己报 rc=0（全站完成并验收通过）
   2. 调速   按「健康率」动态调整 --delay 与片间冷却，而不是拍脑袋固定值
   3. 报告   输出人类可读 + 机器可读（logs/status.json）的健康报告
   4. 收敛   rc=6（重试预算耗尽）时不再空转，落盘缺口报告并进入 6 小时复检节奏

 【为什么需要它】
 该站对「分页 URL」是概率性丢弃（HTTP 200 + 0 字节），不是 429/403。
 实测：连续以 2s 间隔请求时，丢弃率会从 0% 迅速恶化到 80%+；
 而每页只有 --page-attempts 次重试预算，硬扛会把页面「烧死」成永久缺口。
 所以必须：发现丢弃率升高 → 主动降速 + 长冷却，而不是继续硬跑。

 【三种模式】
   python supervise.py                 守护（默认）：一直跑到完成或致命错误
   python supervise.py --status        只读：打印当前进度与健康报告后退出
   python supervise.py --once          只推进一片，打印报告后退出

 【停止方式】
   创建空文件 logs/STOP  → 守护在下一轮开始前退出
   或删除 logs/RUNNING 并杀进程

 【产物】
   logs/status.json       机器可读状态（供计划任务/看板消费）
   logs/supervise.log     守护循环日志（每片一行摘要）
   logs/supervise-state.json  自适应状态（当前 delay / 冷却 / 历史）
   logs/GAP-REPORT.json   重试预算耗尽后的缺口清单（机器可读）
   logs/GAP-REPORT.md     同上，人类可读
   logs/EXHAUSTED.json    耗尽标记；存在且未过期时守护与切片都不再发起请求

 【退出码】
   0 完成并验收通过   1 致命（需人工介入）   2 参数错
   6 重试预算已耗尽（缺口已落盘，等待站点自愈或人工决策）   130 被中断
================================================================================
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import sqlite3
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))

# 计划任务用 pythonw.exe 启动本脚本（无控制台）。任何控制台子进程如果不带
# CREATE_NO_WINDOW，Windows 会给它新建一个控制台窗口，弹到用户桌面上。
# 本机默认终端是 Windows Terminal，弹出来就是可见的 WT 窗口（实测 1.7 秒以上）。
# 所有 spawn 一律带这个 flag —— 不要在前台干扰用户。
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0

DATA = os.path.join(HERE, "data")
LOGDIR = os.path.join(HERE, "logs")
OUT_REL = os.path.join("data", "malaysiayp_full.csv")
OUT = os.path.join(HERE, OUT_REL)
JOB = OUT + ".job.json"
DB = OUT + ".sqlite3"
LOCK = OUT + ".lock"
STATE = os.path.join(LOGDIR, "supervise-state.json")
STATUS = os.path.join(LOGDIR, "status.json")
SLOG = os.path.join(LOGDIR, "supervise.log")
STOP = os.path.join(LOGDIR, "STOP")
EXHAUSTED = os.path.join(LOGDIR, "EXHAUSTED.json")
GAPJSON = os.path.join(LOGDIR, "GAP-REPORT.json")
GAPMD = os.path.join(LOGDIR, "GAP-REPORT.md")

# 无人值守的健康信号（2026-10-14 加）。
# heartbeat.json 每片刷新一次：外部只读这一个文件就能判断「还活着吗 / 有进展吗」。
# ALERT.* 只在需要人类介入时才出现，出现即停止重试。
# 约定：外部巡检只看 ALERT.json 是否存在，存在才通知人；其余情况一律不打扰。
HEARTBEAT = os.path.join(LOGDIR, "heartbeat.json")
ALERTJSON = os.path.join(LOGDIR, "ALERT.json")
ALERTMD = os.path.join(LOGDIR, "ALERT.md")

# rc=6 表示「所有 pending 页的 attempts 都已到 --page-attempts 上限」。
# 该状态不会自愈，反复重跑只会拿到同一个 6，所以必须进入长复检节奏。
# 取 6 小时是为了覆盖站点 CDN 的 s-maxage=86400（坏响应最多缓存 24h），
# 一天 4 次复检足以在站点恢复后第一时间接上，且不产生垃圾日志。
EXHAUSTED_RECHECK = 6 * 3600.0

PYEXE = sys.executable
SCRAPER = os.path.join(HERE, "scrape_malaysiayp.py")

# 采集参数里「与断点库绑定、不可变」的部分：改这些必须重开任务
# page-attempts 取 30 是刻意的：实测该站会间歇性返回 200+0字节，
# 单页退避是 30s→60s→…→3600s 封顶，30 次约覆盖 26 小时的重试窗口，
# 足以跨过 CDN s-maxage=86400 的坏缓存，避免页面被误标 failed。
FROZEN = ["--all", "--out", OUT_REL, "--phone-scope", "all", "--page-attempts", "30"]
# 与断点库无关、可随时调整的部分
TUNABLE = dict(chunk_pages=25, chunk_pause=60, max_chunks=3, max_minutes=20)

# 常驻守护专用预算（2026-10-14）。
# 为什么比 TUNABLE 激进：TUNABLE 是为「计划任务每 20 分钟触发一次」设计的，
# 单片必须远小于触发间隔，否则下一次触发会被 MultipleInstances 拒绝。
# 常驻守护是唯一驱动者、没有刻度约束，可以让单片吃满预算，
# 省掉每 8 分钟一次的「Python 启动 + 打开 30MB SQLite + 重建索引」开销。
# 实测 health_ratio 长期 96%~100%（站点未压速），加大片长是安全的。
# 12 chunk x 40 页 = 480 页/片，配合 --delay 3s 约 24 分钟请求 + 9 分钟片间暂停。
DAEMON_TUNABLE = dict(chunk_pages=40, chunk_pause=45, max_chunks=12, max_minutes=50)

# 自适应调速边界（起始 8s 是实测值：10s 间隔下成功率 80%）
DELAY_MIN, DELAY_MAX = 3.0, 120.0
COOL_MIN, COOL_MAX = 60.0, 3600.0

# 判定阈值（按「一片内的成功率」）
RATIO_EXCELLENT = 0.95
RATIO_OK = 0.85
RATIO_BAD = 0.60


# ------------------------------------------------------------------ 基础设施
def now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def log(msg: str, echo: bool = True) -> None:
    line = "[%s] %s" % (now(), msg)
    os.makedirs(LOGDIR, exist_ok=True)
    with open(SLOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    if echo:
        print(line, flush=True)


def load_state() -> dict:
    if os.path.exists(STATE):
        try:
            with open(STATE, encoding="utf-8") as fh:
                st = json.load(fh)
            st.setdefault("history", [])
            return st
        except Exception:
            pass
    return {"delay": 8.0, "jitter": 2.0, "cooldown": 60.0, "history": []}


def save_state(st: dict) -> None:
    st["updated"] = now()
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


# ------------------------------------------------------------------ 只读探针
def read_job() -> dict:
    if not os.path.exists(JOB):
        return {}
    try:
        with open(JOB, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def read_db() -> dict:
    """只读打开断点库；采集中可能瞬时忙，失败就返回空。"""
    out: dict = {}
    if not os.path.exists(DB):
        return out
    try:
        db = sqlite3.connect("file:%s?mode=ro" % DB.replace("\\", "/"), uri=True, timeout=5)
        try:
            out["attempts_hist"] = dict(
                db.execute("SELECT attempts,count(*) FROM pages GROUP BY attempts").fetchall())
            out["status_hist"] = dict(
                db.execute("SELECT status,count(*) FROM pages GROUP BY status").fetchall())
            cutoff = time.time() - 600
            out["done_10min"] = db.execute(
                "SELECT count(*) FROM pages WHERE status='done' AND updated>?", (cutoff,)).fetchone()[0]
            out["last_updated"] = db.execute(
                "SELECT max(updated) FROM pages").fetchone()[0]
            out["errored"] = db.execute(
                "SELECT count(*) FROM pages WHERE error<>''").fetchone()[0]
            out["zero_err"] = db.execute(
                "SELECT count(*) FROM pages WHERE error LIKE '%响应过短(0B)%'").fetchone()[0]
            out["error_by_cat"] = [
                [r[0], r[1], r[2]] for r in db.execute(
                    "SELECT category, count(*), sum(error LIKE '%响应过短(0B)%') "
                    "FROM pages WHERE error<>'' GROUP BY category "
                    "ORDER BY count(*) DESC LIMIT 8")]
            out["cooldown_until"] = None
            row = db.execute("SELECT value FROM job_meta WHERE key='cooldown_until'").fetchone()
            if row:
                out["cooldown_until"] = json.loads(row[0])
        finally:
            db.close()
    except Exception as exc:
        out["db_error"] = str(exc)
    return out


def process_alive() -> dict:
    """读互斥锁里的 pid，判断采集进程是否还在跑。"""
    info: dict = {"pids": [], "alive": False}
    try:
        with open(LOCK, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        # Windows 上采集脚本用 msvcrt.locking 独占锁住这个文件，正在跑的时候
        # 我们根本读不出来（Device or resource busy）。此时「读不到」恰好等于
        # 「有人在跑」，不能当成没在跑。
        if os.path.exists(LOCK):
            info["alive"] = True
            info["reason"] = "lock-busy"
        return info
    for line in text.splitlines():
        if line.startswith("pid="):
            try:
                info["pids"].append(int(line.split("=", 1)[1].split()[0]))
            except Exception:
                pass
    if info["pids"]:
        try:
            res = subprocess.run(["tasklist", "/FO", "CSV", "/NH"],
                                 capture_output=True, text=True, encoding="gbk", errors="replace",
                                 creationflags=CREATE_NO_WINDOW)
            running: dict = {}
            for row in res.stdout.splitlines():
                parts = [p.strip('"') for p in row.split('","')]
                if len(parts) >= 2 and parts[1].isdigit():
                    running[int(parts[1])] = parts[0].lower()
            # 只认最后一条 pid（最近的持锁者），并要求它确实是 python 进程，
            # 避免 pid 被回收后误判「采集还在跑」而让守护永远不启动。
            last = info["pids"][-1]
            info["alive"] = last in running and running[last].startswith("python")
            info["checked_pid"] = last
        except Exception:
            pass
    return info


def deferred_state() -> dict:
    """只读：待处理页里有多少被延期（not_before 在未来），最近一批什么时候回来。

    用途有二：
      1. 报告里区分「真正还没抓」和「已判定缺陷、正在延期」；
      2. 守护在「可抓页为 0、只剩延期页」时直接长睡，而不是启动一个注定
         只会撞到 not_before 而在预算耗尽后返回 rc=9 的空片。
    """
    out: dict = {"ready": 0, "deferred": 0, "next_at": None}
    if not os.path.exists(DB):
        return out
    try:
        db = sqlite3.connect("file:%s?mode=ro" % DB.replace("\\", "/"),
                             uri=True, timeout=5)
        try:
            now = time.time()
            out["ready"] = db.execute(
                "SELECT count(*) FROM pages WHERE status='pending' AND attempts<30 "
                "AND not_before<=?", (now,)).fetchone()[0]
            out["deferred"] = db.execute(
                "SELECT count(*) FROM pages WHERE status='pending' AND attempts<30 "
                "AND not_before>?", (now,)).fetchone()[0]
            out["next_at"] = db.execute(
                "SELECT min(not_before) FROM pages WHERE status='pending' AND attempts<30 "
                "AND not_before>?", (now,)).fetchone()[0]
        finally:
            db.close()
    except Exception as exc:
        out["error"] = str(exc)
    return out


def last_chunk_log() -> dict:
    """从最近一份 run-*.log 统计限流/失败/封禁指纹。"""
    try:
        files = [f for f in os.listdir(LOGDIR) if f.startswith("run-") and f.endswith(".log")]
    except OSError:
        return {}
    if not files:
        return {}
    files.sort(key=lambda f: os.path.getmtime(os.path.join(LOGDIR, f)), reverse=True)
    path = os.path.join(LOGDIR, files[0])
    c = collections.Counter()
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                classify(line, c)
    except OSError:
        return {}
    c["file"] = files[0]
    c["mtime"] = os.path.getmtime(path)
    finalize(c)
    return dict(c)


def classify(line: str, c: collections.Counter) -> None:
    """把一行日志归类。关键区分：
      zero = 200 + 0 字节 —— 实测与具体 URL 一一对应、可复现，属「站点缺陷」，
             不是速率信号，因此不参与调速，只统计为覆盖率损失；
      hard = 连接错误 / 502 / 超时 / HTTP 错误 —— 这才是「该降速」的信号；
      soft = 非 0 字节的截断响应（如 32768B）—— 介于两者之间，按 hard 的一半权重看待。
    """
    if "[全量段" in line:
        c["attempts"] += 1
    if "全量失败" in line:
        c["failed"] += 1
        if "响应过短(0B)" in line:
            c["zero"] += 1
        elif "响应过短" in line:
            c["truncated"] += 1
        else:
            c["hard"] += 1
    if "疑似软限流" in line:
        c["soft"] += 1
    if "被封禁" in line or "验证页" in line or "拦截指纹" in line:
        c["blocked"] += 1


def finalize(c: collections.Counter) -> None:
    attempts = c.get("attempts", 0)
    if not attempts:
        c["success_ratio"] = None
        c["health_ratio"] = None
        return
    c["success_ratio"] = round(1 - c.get("failed", 0) / attempts, 3)
    # 只有 hard 与 truncated 才说明「我们请求得太快 / 站点在压我们」
    pressure = c.get("hard", 0) + 0.5 * c.get("truncated", 0)
    c["health_ratio"] = round(max(0.0, 1 - pressure / attempts), 3)
    c["zero_ratio"] = round(c.get("zero", 0) / attempts, 3)


# ------------------------------------------------------- 收敛：缺口报告与耗尽标记
def read_exhausted() -> dict:
    """返回仍未过期的耗尽标记；无标记或已过期则返回 {}。"""
    if not os.path.exists(EXHAUSTED):
        return {}
    try:
        with open(EXHAUSTED, encoding="utf-8") as fh:
            info = json.load(fh)
        if (time.time() - float(info.get("at", 0))) < EXHAUSTED_RECHECK:
            return info
    except Exception:
        pass
    return {}


def write_exhausted(info: dict) -> None:
    info = dict(info)
    info["at"] = time.time()
    info["recheck_sec"] = EXHAUSTED_RECHECK
    info["next_recheck"] = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(info["at"] + EXHAUSTED_RECHECK))
    tmp = EXHAUSTED + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(info, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, EXHAUSTED)


def write_gap_report(rep: dict) -> dict:
    """重试预算耗尽时，把「永久取不到」的页面清单落盘，供人工决策。

    只读断点库，不写任何采集数据。
    """
    rows: list = []
    if os.path.exists(DB):
        try:
            db = sqlite3.connect("file:%s?mode=ro" % DB.replace("\\", "/"),
                                 uri=True, timeout=5)
            try:
                rows = [dict(zip(("category", "number", "attempts", "error", "status"), r))
                        for r in db.execute(
                            "SELECT category,number,attempts,error,status FROM pages "
                            "WHERE status!='done' ORDER BY category,number")]
            finally:
                db.close()
        except Exception as exc:
            rows = [{"category": "(读取失败)", "number": 0, "attempts": 0,
                     "error": str(exc), "status": "?"}]

    # 正常耗尽时，所有非 done 页都应该是 status='failed'（预算烧完）。
    # 若这里出现 attempts 很低的 pending 页，说明是被别的路径打断的，报告里要能看出来。
    spent = [r for r in rows if r["status"] == "failed"]
    untried = [r for r in rows if r["status"] != "failed"]

    by_cat: dict = {}
    for r in rows:
        e = by_cat.setdefault(r["category"], {"pages": 0, "zero": 0, "other": 0, "max_attempts": 0})
        e["pages"] += 1
        e["max_attempts"] = max(e["max_attempts"], int(r["attempts"] or 0))
        if "响应过短(0B)" in (r["error"] or ""):
            e["zero"] += 1
        else:
            e["other"] += 1

    payload = {
        "generated_at": now(),
        "reason": "所有待处理页的 attempts 已达 --page-attempts 上限，脚本退出码 6",
        "pages_done": rep.get("pages_done"),
        "pages_expected": rep.get("pages_expected"),
        "gap_pages": len(rows),
        "gap_budget_spent": len(spent),
        "gap_not_yet_attempted": len(untried),
        "entities_stored": rep.get("entities_stored"),
        "rows_exported": rep.get("rows_exported"),
        "parts": rep.get("parts"),
        "by_category": [
            {"category": k, "pages": v["pages"], "zero_byte": v["zero"],
             "other_error": v["other"], "max_attempts": v["max_attempts"]}
            for k, v in sorted(by_cat.items(), key=lambda kv: -kv[1]["pages"])],
        "pages": rows,
    }
    tmp = GAPJSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, GAPJSON)

    total_zero = sum(v["zero"] for v in by_cat.values())
    lines = [
        "# malaysiayp 全量采集 · 残余缺口报告",
        "",
        "- 生成时间：%s" % payload["generated_at"],
        "- 触发原因：%s" % payload["reason"],
        "- 已完成 / 预期页数：%s / %s" % (payload["pages_done"], payload["pages_expected"]),
        "- 缺口页数：**%s**（其中 HTTP 200 + 0 字节 %s 页）" % (len(rows), total_zero),
        "- 缺口构成：重试预算已烧完 `%s` 页；尚未尝试 `%s` 页"
        % (len(spent), len(untried)),
        "- 已交付：入库实体 %s，导出行 %s，CSV 分片 %s"
        % (payload["entities_stored"], payload["rows_exported"], payload["parts"]),
        "",
        "> 正常情况下「尚未尝试」应为 0。若不为 0，说明这一轮是被别的原因打断的，"
        "不是真的耗尽，应直接重跑而不是看本报告。",
        "",
        "## 按分类汇总",
        "",
        "| 分类 | 缺口页 | 200+0字节 | 其他错误 | 最高尝试次数 |",
        "|---|---|---|---|---|",
    ]
    for k, v in sorted(by_cat.items(), key=lambda kv: -kv[1]["pages"]):
        lines.append("| %s | %s | %s | %s | %s |"
                     % (k, v["pages"], v["zero"], v["other"], v["max_attempts"]))
    lines += [
        "",
        "## 处置建议",
        "",
        "1. 这些页对同一 URL 的返回是**确定性**的（多次请求结果一致），不是限流，"
        "降速/换 UA/加 Referer 均无效，已在 TROUBLESHOOTING.md「三·F」记录实测证据。",
        "2. 若是 CDN 缓存了坏响应，`s-maxage=86400` 表示 24 小时后可能自愈；"
        "守护每 6 小时自动复检一次，无需人工干预。",
        "3. 若 24 小时后仍不恢复，属源站缺陷，只能：① 接受当前交付形态"
        "（全量 CSV + 本缺口清单）；② 缩小目标范围；③ 更换出口 IP；"
        "④ 与站点方确认配额与授权。",
        "4. 不要把 `--page-attempts` 再往上调——单页退避已封顶 3600s，"
        "30 次覆盖约 26 小时重试窗口，继续加只会拉长空转时间。",
        "",
        "完整逐页清单见 `logs/GAP-REPORT.json`。",
    ]
    tmp = GAPMD + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    os.replace(tmp, GAPMD)
    return payload


def settle_exhausted(rep: dict, who: str) -> dict:
    """rc=6 的统一处置：落盘缺口报告 + 写耗尽标记 + 记日志。"""
    payload = write_gap_report(rep)
    write_exhausted({"gap_pages": payload["gap_pages"],
                     "pages_done": payload["pages_done"],
                     "pages_expected": payload["pages_expected"]})
    log("%s：重试预算已耗尽，缺口 %s 页已落盘（logs/GAP-REPORT.md / .json）"
        % (who, payload["gap_pages"]))
    log("下次复检：%s（%d 小时后再试，站点坏缓存可能已过期）"
        % (time.strftime("%Y-%m-%d %H:%M:%S",
                         time.localtime(time.time() + EXHAUSTED_RECHECK)),
           int(EXHAUSTED_RECHECK // 3600)))
    return payload


# ------------------------------------------------------------------ 报告
def build_report(state: dict) -> dict:
    job = read_job()
    db = read_db()
    cov = job.get("page_coverage", {}) or {}
    states = cov.get("page_states", {}) or {}
    csvq = job.get("csv_quality", {}) or {}
    att = job.get("attempts", {}) or {}
    done = states.get("done", 0)
    expected = cov.get("expected_pages", 0)
    pending = states.get("pending", 0)
    failed = states.get("failed", 0)

    rate = (db.get("done_10min", 0) / 10.0) if db.get("done_10min") else 0.0
    remain = max(0, expected - done)
    eta_h = (remain / rate / 60.0) if rate > 0 else None

    chunk = last_chunk_log()
    live = process_alive()
    dfr = deferred_state()

    risk = 0
    for a, n in (db.get("attempts_hist") or {}).items():
        if int(a) >= 12:
            risk += n

    # 有效进度：把「已判定缺陷、正在延期」的页从分母里摘出去，
    # 否则进度条会被一批永远抓不到的页永久压住，看不出真实推进。
    deferred = dfr.get("deferred", 0)
    effective_expected = max(0, expected - deferred)

    return {
        "generated_at": now(),
        "completion": job.get("completion", False),
        "phase": job.get("phase", ""),
        "exit_code": job.get("exit_code", None),
        "pages_done": done,
        "pages_expected": expected,
        "pages_pending": pending,
        "pages_failed": failed,
        "pages_done_last_10min": db.get("done_10min", 0),
        "pages_per_min": round(rate, 2),
        "eta_hours": round(eta_h, 1) if eta_h is not None else None,
        "categories": cov.get("categories", 0),
        "categories_index_pending": cov.get("index_failed_or_pending", 0),
        "category_page_gaps": cov.get("category_page_gaps", 0),
        "header_total_mismatches": cov.get("header_total_mismatches", 0),
        "entities_stored": csvq.get("stored_entities", 0),
        "rows_exported": csvq.get("scope_rows", 0),
        "parts": csvq.get("parts", 0),
        "attempts_total": att.get("total", 0),
        "attempts_failed_or_interrupted": att.get("failed_or_interrupted", 0),
        "attempts_hist": db.get("attempts_hist", {}),
        "pages_near_retry_limit": risk,
        "errored_pages": db.get("errored", 0),
        "zero_error_pages": db.get("zero_err", 0),
        "error_by_category": db.get("error_by_cat", []),
        "last_page_update": db.get("last_updated"),
        "last_chunk": chunk,
        "crawler_alive": live.get("alive", False),
        "adaptive_delay": state.get("delay"),
        "adaptive_cooldown": state.get("cooldown"),
        "exhausted": read_exhausted(),
        "deferred_pages": deferred,
        "deferred_next_at": dfr.get("next_at"),
        "ready_pages": dfr.get("ready", 0),
        "effective_expected": effective_expected,
        "effective_pct": (round(100.0 * done / effective_expected, 2)
                          if effective_expected else None),
        "db_error": db.get("db_error", ""),
    }


def print_report(rep: dict) -> None:
    def row(k, v):
        print("  %-26s %s" % (k, v))

    print("=" * 68)
    print(" malaysiayp 全量采集 · 监督报告   %s" % rep["generated_at"])
    print("=" * 68)
    print("[进度]")
    row("已完成 / 预期页数", "%s / %s  (%.2f%%)" % (
        rep["pages_done"], rep["pages_expected"],
        (100.0 * rep["pages_done"] / rep["pages_expected"]) if rep["pages_expected"] else 0))
    if rep.get("deferred_pages"):
        row("有效进度（剔除延期页）", "%s / %s  (%.2f%%)" % (
            rep["pages_done"], rep["effective_expected"], rep.get("effective_pct") or 0))
    row("待处理 / 已失败", "%s / %s" % (rep["pages_pending"], rep["pages_failed"]))
    if rep.get("deferred_pages"):
        row("其中已延期(缺陷页)", "%s 页，最近一批 %s 回来" % (
            rep["deferred_pages"],
            time.strftime("%H:%M", time.localtime(rep["deferred_next_at"]))
            if rep.get("deferred_next_at") else "?"))
        row("当前可抓取页数", rep.get("ready_pages", 0))
    row("分类 已索引/待索引", "%s / %s" % (rep["categories"],
                                          rep["categories_index_pending"]))
    row("页缺口 / 页数不一致", "%s / %s" % (rep["category_page_gaps"],
                                            rep["header_total_mismatches"]))
    row("速率 / ETA", "%s 页/分  ·  %s" % (
        rep["pages_per_min"],
        ("%.1f 小时" % rep["eta_hours"]) if rep["eta_hours"] is not None else "未知"))
    print("[产出]")
    row("入库实体 / 导出行", "%s / %s" % (rep["entities_stored"], rep["rows_exported"]))
    row("CSV 分片数", rep["parts"])
    print("[限流与错误]")
    lc = rep["last_chunk"] or {}
    row("最近一片", "%s" % lc.get("file", "(无)"))
    row("  页尝试 / 失败", "%s / %s" % (lc.get("attempts", 0), lc.get("failed", 0)))
    row("  URL缺陷(200+0B)", "%s  (%.0f%%)" % (
        lc.get("zero", 0), 100 * (lc.get("zero_ratio") or 0)))
    row("  截断 / 硬错误", "%s / %s" % (lc.get("truncated", 0), lc.get("hard", 0)))
    row("  总成功率 / 健康率", "%s / %s" % (lc.get("success_ratio", "n/a"),
                                            lc.get("health_ratio", "n/a")))
    row("  封禁指纹", lc.get("blocked", 0))
    row("自适应 --delay", rep["adaptive_delay"])
    row("自适应片间冷却", rep["adaptive_cooldown"])
    print("[重试预算与缺陷分布]")
    row("attempts 分布", json.dumps(rep["attempts_hist"], ensure_ascii=False))
    row("接近上限(>=12)的页", rep["pages_near_retry_limit"])
    row("带错误信息的页", rep["errored_pages"])
    row("其中 200+0字节(站点缺陷)", rep["zero_error_pages"])
    for cat, n, z in (rep.get("error_by_category") or [])[:5]:
        row("  " + str(cat)[:24], "%s 页报错（其中 %s 页 0 字节）" % (n, z))
    print("[运行状态]")
    row("job phase / exit_code", "%s / %s" % (rep["phase"], rep["exit_code"]))
    row("completion", rep["completion"])
    row("采集进程存活", rep["crawler_alive"])
    lu = rep["last_page_update"]
    row("最后一页落盘时间",
        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(lu)) if lu else "无")
    if rep["last_page_update"]:
        idle = time.time() - rep["last_page_update"]
        row("空闲时长", "%.1f 分钟" % (idle / 60.0))
    if rep.get("db_error"):
        row("DB 只读异常", rep["db_error"])
    ex = rep.get("exhausted") or {}
    if ex:
        print("[终止态]")
        row("重试预算", "已耗尽（rc=6），缺口 %s 页" % ex.get("gap_pages"))
        row("下次复检", ex.get("next_recheck"))
        row("缺口报告", "logs/GAP-REPORT.md")
    print("=" * 68)


# ------------------------------------------------------------------ 采集一片
def run_chunk(state: dict, budget_minutes: int | None = None,
              daemon: bool = False) -> tuple[int, dict]:
    t = DAEMON_TUNABLE if daemon else TUNABLE
    args = [PYEXE, SCRAPER] + FROZEN + [
        "--chunk-pages", str(t["chunk_pages"]),
        "--chunk-pause", str(t["chunk_pause"]),
        "--max-chunks", str(t["max_chunks"]),
        "--max-minutes", str(budget_minutes or t["max_minutes"]),
        "--delay", "%.1f" % state["delay"],
        "--jitter", "%.1f" % state["jitter"],
    ]
    log("启动采集片: delay=%s jitter=%s chunk_pages=%s max_chunks=%s max_minutes=%s"
        % (state["delay"], state["jitter"], t["chunk_pages"], t["max_chunks"],
           budget_minutes or t["max_minutes"]))
    counters = collections.Counter()
    proc = subprocess.Popen(args, cwd=HERE, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True,
                            encoding="utf-8", errors="replace", bufsize=1,
                            creationflags=CREATE_NO_WINDOW)

    # 2026-10-14 事故复盘：原先是主线程 `for line in proc.stdout`。
    # Windows 上若采集脚本派生的子进程继承了 stdout 管道句柄，管道永不关闭，
    # 这个 for 循环就永远不返回 —— 表现是「日志已打印 rc=9、采集早结束，
    # 但 supervise 进程不退出」，它继续持有互斥锁，把之后所有切片全部挡在门外
    # （实测停摆 15 分钟无人推进）。改为后台线程读管道 + 主线程带 deadline 等待：
    # 采集进程一退出就正常收尾，真卡住也有硬超时兜底。
    def _reader() -> None:
        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                line = line.rstrip()
                if not line:
                    continue
                classify(line, counters)
                print("    " + line, flush=True)
        except Exception:
            pass

    th = threading.Thread(target=_reader, daemon=True)
    th.start()

    budget = float(budget_minutes or t["max_minutes"])
    # 给串行的收尾（SQLite checkpoint / 索引维护）留 10 分钟余量
    deadline = time.time() + budget * 60.0 + 600.0
    # 单片最长 50 分钟，只在片尾写心跳的话外部要等近一小时才看得到进展。
    # 这里在等待期间每 60 秒补一次心跳，监控粒度从「一片」降到「一分钟」。
    last_hb = 0.0
    try:
        while True:
            if proc.poll() is not None and not th.is_alive():
                break
            if time.time() - last_hb >= 60.0:
                last_hb = time.time()
                try:
                    write_heartbeat(build_report(state), note="采集中")
                except Exception:
                    pass  # 采集脚本正持有 DB 写锁，读不到就下一轮再试
            if time.time() > deadline:
                log("采集进程超过硬超时（%.0f 分钟 + 10 分钟余量）仍未退出，强制结束"
                    % budget)
                proc.kill()
                break
            time.sleep(1.0)
    except KeyboardInterrupt:
        proc.terminate()
        raise
    th.join(timeout=15.0)
    rc = proc.wait()
    finalize(counters)
    return rc, dict(counters)


# ------------------------------------------------------------------ 自适应调速
def adapt(state: dict, counters: dict, rc: int) -> str:
    """按 health_ratio 调速，而不是按 success_ratio。

    原因：实测「200 + 0 字节」与具体 URL 一一对应、可复现（换 Referer / 加缓存穿透参数 /
    换 Accept-Encoding 都无效），属站点缺陷。若按 success_ratio 调速，遇到缺陷密集的
    分类就会误判为「被限流」，把整站拖慢却毫无收益。只有连接错误 / 502 / 超时 /
    截断响应才说明我们请求得太快。
    """
    ratio = counters.get("health_ratio")
    note = []
    if ratio is None:
        # 没有发出任何请求（例如被锁挡住），只做小睡
        state["cooldown"] = max(COOL_MIN, min(COOL_MAX, state["cooldown"]))
        note.append("本片未发出请求（可能被互斥锁挡住），冷却 %.0fs" % state["cooldown"])
        return "; ".join(note)

    if ratio >= RATIO_EXCELLENT:
        old = state["delay"]
        state["delay"] = max(DELAY_MIN, round(state["delay"] * 0.85, 1))
        state["cooldown"] = COOL_MIN
        note.append("健康率 %.0f%% 优秀，delay %.1f→%.1f，冷却 %ds" % (
            ratio * 100, old, state["delay"], int(state["cooldown"])))
    elif ratio >= RATIO_OK:
        state["cooldown"] = COOL_MIN
        note.append("健康率 %.0f%% 正常，保持 delay=%.1f，冷却 %ds" % (
            ratio * 100, state["delay"], int(state["cooldown"])))
    elif ratio >= RATIO_BAD:
        old = state["delay"]
        state["delay"] = min(DELAY_MAX, round(state["delay"] * 1.5, 1))
        state["cooldown"] = min(COOL_MAX, max(120.0, state["cooldown"] * 1.5))
        note.append("健康率 %.0f%% 偏低，delay %.1f→%.1f，冷却 %.0fs" % (
            ratio * 100, old, state["delay"], state["cooldown"]))
    else:
        old = state["delay"]
        state["delay"] = min(DELAY_MAX, round(state["delay"] * 2.0, 1))
        state["cooldown"] = min(COOL_MAX, max(300.0, state["cooldown"] * 3.0))
        note.append("健康率 %.0f%% 很差（疑似被站点压速），delay %.1f→%.1f，长冷却 %.0fs" % (
            ratio * 100, old, state["delay"], state["cooldown"]))

    zr = counters.get("zero_ratio")
    if zr:
        note.append("URL 缺陷率(200+0字节) %.0f%%（站点侧，不可通过降速解决）" % (zr * 100))

    state.setdefault("history", []).append(
        {"at": now(), "rc": rc, "attempts": counters.get("attempts", 0),
         "zero": counters.get("zero", 0), "hard": counters.get("hard", 0),
         "truncated": counters.get("truncated", 0), "health_ratio": ratio,
         "zero_ratio": zr, "delay": state["delay"], "cooldown": state["cooldown"]})
    state["history"] = state["history"][-200:]
    return "; ".join(note)


FATAL_CODES = {2: "参数错误", 3: "环境/DB/磁盘错误", 4: "被站点封禁或验证页",
               5: "站点结构变更", 7: "输出保护触发"}

# 各类致命码的处置建议，写进 ALERT.md，让人打开就知道该干什么
FATAL_ADVICE = {
    2: "参数与断点库不一致。多半是有人手改了命令行参数。核对 FROZEN 常量与 "
       "data/malaysiayp_full.csv.job.json 的 config 是否一致。",
    3: "环境 / DB / 磁盘错误。先看 logs/run-*.log 末尾，再确认磁盘剩余空间与 "
       "data/malaysiayp_full.csv.sqlite3 是否可写。",
    4: "被站点封禁或落到验证页。停一段时间再试；必要时换出口 IP 或降低 --delay。",
    5: "站点结构变更，解析器匹配不上了。需要改 scrape_malaysiayp.py 的选择器。",
    7: "输出保护触发：命令行参数与断点库里冻结的配置不一致。"
       "必须带上 --page-attempts 30 等 FROZEN 参数。",
    6: "重试预算耗尽（不是限流）。等 CDN 坏缓存过期后会自动复检，见 logs/GAP-REPORT.md。",
    1: "连续多次异常退出，守护主动放弃重试。看 logs/supervise.log 末尾几片的 rc。",
}


def write_heartbeat(rep: dict, note: str = "") -> None:
    """每片刷新一次。外部巡检只读这一个文件即可判断健康度。"""
    # build_report 返回的是扁平字段（pages_done / entities_stored ...），
    # 不是 job.json 的嵌套结构，别按嵌套去取，否则全是 None。
    hb = {
        "ts": now(),
        "epoch": time.time(),
        "alive": True,
        "phase": rep.get("phase"),
        "exit_code": rep.get("exit_code"),
        "completion": rep.get("completion"),
        "pages_done": rep.get("pages_done"),
        "pages_pending": rep.get("pages_pending"),
        "expected_pages": rep.get("pages_expected"),
        "effective_pct": rep.get("effective_pct"),
        "pages_per_min": rep.get("pages_per_min"),
        "eta_hours": rep.get("eta_hours"),
        "entities": rep.get("entities_stored"),
        "crawler_alive": rep.get("crawler_alive"),
        "last_page_update": rep.get("last_page_update"),
        "idle_minutes": (round((time.time() - rep["last_page_update"]) / 60.0, 1)
                         if rep.get("last_page_update") else None),
        "note": note,
    }
    try:
        with open(HEARTBEAT, "w", encoding="utf-8") as fh:
            json.dump(hb, fh, ensure_ascii=False, indent=1)
    except OSError:
        pass


def raise_alert(kind: str, rc: int, detail: str, rep: dict) -> None:
    """需要人类介入时调用：落盘 ALERT.json / ALERT.md，然后停止重试。

    约定：外部（WorkBuddy 巡检 / 人）只需判断 ALERT.json 是否存在。
    存在 = 停下来找人；不存在 = 一切正常，别打扰。
    """
    payload = {
        "ts": now(),
        "epoch": time.time(),
        "needs_human": True,
        "kind": kind,
        "rc": rc,
        "detail": detail,
        "advice": FATAL_ADVICE.get(rc, "见 TROUBLESHOOTING.md 第 4 节"),
        "progress": {
            "pages_done": rep.get("pages_done"),
            "pages_pending": rep.get("pages_pending"),
            "entities": rep.get("entities_stored"),
        },
        "logs": {
            "supervise": "logs/supervise.log",
            "last_run": "logs/run-*.log",
        },
        "resume_hint": "修好后删掉 logs/ALERT.json 与 logs/STOP，再启动守护即可续跑",
    }
    try:
        with open(ALERTJSON, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        with open(ALERTMD, "w", encoding="utf-8") as fh:
            fh.write("# 采集守护告警：需要人工介入\n\n")
            fh.write("- 时间：%s\n" % payload["ts"])
            fh.write("- 类型：%s（退出码 %s）\n" % (kind, rc))
            fh.write("- 详情：%s\n\n" % detail)
            fh.write("## 处置建议\n\n%s\n\n" % payload["advice"])
            fh.write("## 当前进度\n\n")
            fh.write("- 已完成页：%s / 待采页：%s\n" % (
                rep.get("pages_done"), rep.get("pages_pending")))
            fh.write("- 已存实体：%s\n\n" % rep.get("entities_stored"))
            fh.write("## 排查入口\n\n")
            fh.write("- `logs/supervise.log`（末尾几片的 rc 与自适应调速记录）\n")
            fh.write("- `logs/run-*.log`（最近一次采集脚本的完整输出）\n")
            fh.write("- `TROUBLESHOOTING.md` 第 4 节（退出码对照表）\n\n")
            fh.write("## 恢复\n\n")
            fh.write("修好后删除 `logs/ALERT.json` 和 `logs/STOP`，重新启动守护；"
                     "断点在 SQLite 里，会自动续跑。\n")
    except OSError:
        pass
    log("!!! 需要人工介入：%s rc=%s —— 已写入 logs/ALERT.json" % (kind, rc))


# ------------------------------------------------------------------ 主流程
def cmd_status() -> int:
    state = load_state()
    rep = build_report(state)
    print_report(rep)
    os.makedirs(LOGDIR, exist_ok=True)
    with open(STATUS, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1)
    return 0


def cmd_once(budget_minutes: float | None = None) -> int:
    state = load_state()
    # 已经耗尽且还在复检窗口内：不 spawn 采集脚本。
    # 否则计划任务每 20 分钟就会生成一个 994 字节的空 run-*.log（纯垃圾）。
    ex = read_exhausted()
    if ex:
        log("重试预算已耗尽，跳过本片；下次复检 %s（缺口 %s 页，见 logs/GAP-REPORT.md）"
            % (ex.get("next_recheck"), ex.get("gap_pages")))
        print_report(build_report(state))
        return 6
    rc, counters = run_chunk(state, budget_minutes)
    note = adapt(state, counters, rc)
    save_state(state)
    log("本片 rc=%d %s | %s" % (rc, json.dumps(counters, ensure_ascii=False), note))
    rep = build_report(state)
    if rc == 6:
        settle_exhausted(rep, "切片")
    print_report(rep)
    return 0 if rc in (0, 9) else rc


def transient_robots_failure(rc: int) -> bool:
    """Only retry explicitly classified robots transport failures, never storage errors."""
    if rc != 3:
        return False
    try:
        with open(JOB, encoding="utf-8") as fh:
            job = json.load(fh)
        return (job.get("phase") == "environment_error"
                and job.get("exit_code") == 3
                and "[transient-network]" in job.get("last_error", ""))
    except (OSError, ValueError, TypeError):
        return False


def cmd_daemon() -> int:
    state = load_state()
    log("守护启动：delay=%s cooldown=%s 预算=%s" % (
        state["delay"], state["cooldown"], DAEMON_TUNABLE))
    abnormal = 0
    network_failures = 0
    # 启动即留心跳：看门狗靠它判断守护是否活着，否则首次拉起后要等满一整片
    write_heartbeat(build_report(state), note="守护启动")
    while True:
        if os.path.exists(STOP):
            log("检测到 logs/STOP，守护退出")
            write_heartbeat(build_report(state), note="守护已按 STOP 停止")
            return 0

        # 先探测再启动：计划任务的切片实例可能在跑。若不先探测就 spawn，
        # 采集脚本会因互斥锁立刻返回 8，但每次都会生成一个空的 run-*.log，
        # 一天能刷出上千个垃圾日志文件。
        live = process_alive()
        if live.get("alive"):
            log("检测到已有采集进程在跑（pid=%s），等待 120s 不启动新片" % live.get("pids"))
            slept = 0.0
            while slept < 120.0:
                time.sleep(min(5.0, 120.0 - slept))
                slept += 5.0
                if os.path.exists(STOP):
                    log("等待期间检测到 logs/STOP，守护退出")
                    return 0
            continue

        # 「可抓页为 0、只剩延期页」时不要启动采集片：
        # 采集脚本会立刻撞到 not_before 而空等到预算耗尽返回 rc=9，
        # 白白起一个进程、写一份空 run 日志。直接长睡到最近一批回来。
        ds = deferred_state()
        if ds.get("ready", 0) == 0 and ds.get("deferred", 0) > 0:
            until = ds.get("next_at") or (time.time() + 3600.0)
            wait_s = max(60.0, until - time.time())
            log("可抓取页为 0，%d 页缺陷页处于延期状态；休眠 %.0f 分钟至 %s"
                % (ds["deferred"], wait_s / 60.0,
                   time.strftime("%H:%M:%S", time.localtime(until))))
            slept = 0.0
            while slept < wait_s:
                time.sleep(min(30.0, wait_s - slept))
                slept += 30.0
                if os.path.exists(STOP):
                    log("延期等待期间检测到 logs/STOP，守护退出")
                    return 0
            continue

        rep = build_report(state)
        if rep["completion"]:
            log("job.json 报告完成，执行离线验收")
            # 必须带上与断点库一致的冻结参数，否则验收会因配置不匹配而拒绝
            vrc = subprocess.call([PYEXE, SCRAPER, "--full-verify"] + FROZEN, cwd=HERE,
                                  creationflags=CREATE_NO_WINDOW)
            log("--full-verify rc=%d" % vrc)
            if vrc == 0:
                log("全站采集与验收通过，守护收工")
                print_report(build_report(state))
                write_heartbeat(build_report(state),
                                note="全站采集完成并通过离线验收")
                return 0
            log("验收未通过，回到采集循环补缺口")

        rc, counters = run_chunk(state, daemon=True)
        rep = build_report(state)

        if transient_robots_failure(rc):
            network_failures += 1
            if network_failures <= 3:
                delay = 60 * (2 ** (network_failures - 1))
                log("robots 临时网络失败，第 %d/3 次恢复等待 %ds；不抓取、不清其他告警"
                    % (network_failures, delay))
                for _ in range(delay // 5):
                    if os.path.exists(STOP):
                        return 0
                    write_heartbeat(rep, note="临时网络错误退避，等待重新检查 robots")
                    time.sleep(5)
                continue
            log("临时网络恢复预算耗尽，转人工告警")
        else:
            network_failures = 0

        if rc in FATAL_CODES:
            log("致命退出码 %d（%s），停止重试，需人工介入" % (rc, FATAL_CODES[rc]))
            print_report(rep)
            raise_alert(FATAL_CODES[rc], rc,
                        "采集脚本以退出码 %d 结束：%s" % (rc, FATAL_CODES[rc]), rep)
            write_heartbeat(rep, note="已停止：%s" % FATAL_CODES[rc])
            return 1

        note = adapt(state, counters, rc)
        save_state(state)
        log("本片 rc=%d %s | %s" % (rc, json.dumps(counters, ensure_ascii=False), note))
        write_heartbeat(build_report(state), note=note)

        # rc 不属于「正常推进」集合（0 完成 / 9 时间片到 / 6 预算耗尽）就计一次异常。
        # 连续 8 次说明问题不会自愈，停下来找人，别无限空转。
        if rc in (0, 9, 6):
            abnormal = 0
        else:
            abnormal += 1
            if abnormal >= 8:
                rep2 = build_report(state)
                raise_alert("连续异常退出", rc,
                            "连续 %d 片以非预期退出码 %d 结束，守护停止重试" % (abnormal, rc),
                            rep2)
                write_heartbeat(rep2, note="已停止：连续异常退出")
                return 1

        # rc=6：所有待处理页的重试预算都烧完了。这不是限流，重跑只会立刻再拿一个 6。
        # 落盘缺口报告后进入 6 小时复检节奏，让站点坏缓存有机会过期。
        if rc == 6:
            settle_exhausted(build_report(state), "守护")
            write_heartbeat(build_report(state),
                            note="重试预算耗尽，进入 6 小时复检（非限流，无需介入）")
            if os.path.exists(STOP):
                log("检测到 logs/STOP，守护退出")
                return 0
            slept = 0.0
            while slept < EXHAUSTED_RECHECK:
                time.sleep(min(30.0, EXHAUSTED_RECHECK - slept))
                slept += 30.0
                if os.path.exists(STOP):
                    log("复检等待期间检测到 logs/STOP，守护退出")
                    return 0
            log("复检窗口到期，清除耗尽标记后重试")
            try:
                os.remove(EXHAUSTED)
            except OSError:
                pass
            continue

        if os.path.exists(STOP):
            log("检测到 logs/STOP，守护退出")
            return 0

        cool = state["cooldown"]
        log("冷却 %.0f 秒后继续" % cool)
        slept = 0.0
        while slept < cool:
            time.sleep(min(5.0, cool - slept))
            slept += 5.0
            if os.path.exists(STOP):
                log("冷却期间检测到 logs/STOP，守护退出")
                return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="全量采集的自适应守护与监督报告（不修改采集脚本）")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--status", action="store_true", help="只读：打印监督报告后退出")
    g.add_argument("--once", action="store_true", help="只推进一片，报告后退出")
    g.add_argument("--probe", action="store_true", help="同 --status（兼容别名）")
    p.add_argument("--budget-minutes", type=float, default=None,
                   help="单片时间预算（分钟）；配合 --once 用，"
                        "计划任务必须让它小于触发间隔，否则下一次触发会被 "
                        "MultipleInstances=IgnoreNew 拒绝（LastTaskResult 0x800710E0）")
    p.add_argument("--reset-state", action="store_true", help="重置自适应状态后退出")
    return p


def _ensure_stdio() -> None:
    """pythonw.exe（无控制台子系统）下 sys.stdout / sys.stderr 是 None，
    任何 print() 都会抛 AttributeError，log() 第一步就会炸。

    计划任务故意用 pythonw 是为了不弹控制台窗口，所以这里把输出重定向到
    logs/slice-stdio.log，既保留现场又不产生窗口。
    """
    if sys.stdout is not None and sys.stderr is not None:
        return
    os.makedirs(LOGDIR, exist_ok=True)
    try:
        fh = open(os.path.join(LOGDIR, "slice-stdio.log"), "a",
                  encoding="utf-8", buffering=1)
    except OSError:
        fh = open(os.devnull, "w", encoding="utf-8")
    if sys.stdout is None:
        sys.stdout = fh
    if sys.stderr is None:
        sys.stderr = fh


def main(argv=None) -> int:
    _ensure_stdio()
    args = build_parser().parse_args(argv)
    os.makedirs(LOGDIR, exist_ok=True)
    if args.reset_state:
        if os.path.exists(STATE):
            os.remove(STATE)
        print("自适应状态已重置")
        return 0
    if args.status or args.probe:
        return cmd_status()
    if args.once:
        return cmd_once(args.budget_minutes)
    try:
        return cmd_daemon()
    except KeyboardInterrupt:
        log("收到中断信号，守护退出（断点在 SQLite，重跑自动续跑）")
        return 130


if __name__ == "__main__":
    sys.exit(main())
