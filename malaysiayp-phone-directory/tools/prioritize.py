#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""队列优先级重排（只动 not_before，可回滚）。

背景
----
断点库默认按 `ORDER BY not_before, category, number` 选页。字母序会把采集
一头扎进 `agricultural` / `apparel-*` 这类巨型分类的深层页，而 **1185 个
分类的首页（page/1）还没抓过**。首页价值最高：
  * 每页 ~20 条新记录
  * 读出该分类的真实页数（`categories.pages`），把总量估计从猜测变成事实

本工具用 SQL 直接改 `not_before` 实现优先级，**不改脚本、不改状态字段**：
  A. 未索引分类的首页  → not_before = EPOCH_TOP（排到最前）
  B. 已确认缺陷页      → not_before = now + DEFER（推到最后）

安全性
------
* 只 UPDATE `not_before`，不动 status/attempts/error/rows
* 条件带 `not_before` 边界，二次执行不会重复推后（幂等）
* 每次运行前自动备份受影响行的原值到 logs/prioritize-backup-*.json
* `--rollback` 可完整还原

用法
----
  python prioritize.py                # 干跑，只报告
  python prioritize.py --apply        # 执行
  python prioritize.py --rollback     # 还原最近一次
  python prioritize.py --rollback logs/prioritize-backup-xxx.json
"""
import argparse
import json
import os
import sqlite3
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "malaysiayp_full.csv.sqlite3")
LOGDIR = os.path.join(HERE, "logs")
EPOCH_TOP = -1000.0             # 负数，抢占队首（默认 not_before 为 0）
DEFER = 6 * 3600.0              # 缺陷页推后 6 小时
PAGE_ATTEMPTS = 30


def connect():
    con = sqlite3.connect(DB, timeout=30)
    con.execute("PRAGMA busy_timeout=30000")
    return con


def snapshot(con, ids):
    if not ids:
        return []
    marks = ",".join("?" * len(ids))
    return [{"url": u, "not_before": nb} for u, nb in con.execute(
        "SELECT url, not_before FROM pages WHERE url IN (%s)" % marks, ids)]


def plan(con):
    now = time.time()
    head = list(con.execute(
        "SELECT url, not_before FROM pages "
        "WHERE status='pending' AND number=1 AND attempts<? AND error='' "
        "  AND category IN (SELECT name FROM categories WHERE index_state<>'done')",
        (PAGE_ATTEMPTS,)))
    # 注：error='' 排除「已确认缺陷首页」（B 型坏缓存首页）。这类页已带 error，
    # 由 defer_defects.py 按 attempts 阶梯延期复检，不再每轮强制拉回队首空耗预算。
    # 若其缓存恢复、抓取成功 → index_state 变 'done' → 自然退出本查询。
    head = [(u, nb) for u, nb in head if nb > EPOCH_TOP]
    defect = list(con.execute(
        "SELECT url, not_before FROM pages "
        "WHERE status='pending' AND error<>'' AND not_before<=?",
        (now,)))
    return head, defect, now


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--rollback", nargs="?", const="__latest__", default=None)
    a = ap.parse_args()

    if not os.path.exists(DB):
        print("找不到断点库：" + DB)
        return 3
    os.makedirs(LOGDIR, exist_ok=True)
    con = connect()

    if a.rollback is not None:
        path = a.rollback
        if path == "__latest__":
            cands = sorted(f for f in os.listdir(LOGDIR)
                           if f.startswith("prioritize-backup-"))
            if not cands:
                print("没有可回滚的备份")
                return 0
            path = os.path.join(LOGDIR, cands[-1])
        data = json.load(open(path, encoding="utf-8"))
        n = 0
        with con:
            for r in data.get("rows", []):
                con.execute("UPDATE pages SET not_before=? WHERE url=?",
                            (r["not_before"], r["url"]))
                n += 1
        print("已回滚 %d 行（来自 %s）" % (n, os.path.basename(path)))
        return 0

    head, defect, now = plan(con)
    print("=" * 68)
    print(" 队列优先级重排（%s）" % time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 68)
    print("  A. 未索引分类首页（提前）      %5d 页" % len(head))
    print("  B. 已确认缺陷页（推后 6h）     %5d 页" % len(defect))
    if not a.apply:
        print("\n  [干跑] 加 --apply 才执行。")
        return 0

    rows = snapshot(con, [u for u, _ in head] + [u for u, _ in defect])
    stamp = time.strftime("%Y%m%d-%H%M%S")
    bpath = os.path.join(LOGDIR, "prioritize-backup-%s.json" % stamp)
    json.dump({"stamp": stamp, "head": len(head), "defect": len(defect),
               "rows": rows},
              open(bpath, "w", encoding="utf-8"), ensure_ascii=False)

    with con:
        for u, _ in head:
            con.execute("UPDATE pages SET not_before=? WHERE url=?",
                        (EPOCH_TOP, u))
        cutoff = now + DEFER
        for u, _ in defect:
            con.execute("UPDATE pages SET not_before=? WHERE url=?",
                        (cutoff, u))
    print("\n  ✅ 已应用：%d 页提到最前，%d 页推后 6 小时" % (len(head), len(defect)))
    print("     备份 → %s" % os.path.basename(bpath))
    print("     回滚 → python prioritize.py --rollback")
    return 0


if __name__ == "__main__":
    sys.exit(main())
