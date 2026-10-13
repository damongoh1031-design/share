#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""缺陷页「真伪」抽样复测。

目的：区分两种 0 字节响应
  A 型（短时限流）—— 静默数十秒后重测会恢复
  B 型（源站坏缓存）—— 静默后仍为 0 字节 / 截断

用法：
  python probe_recover.py [--n 30] [--gap 10]

只读，不写断点库。结果落 logs/probe-recover.json。
"""
import argparse
import json
import os
import random
import sqlite3
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "malaysiayp_full.csv.sqlite3")
OUT = os.path.join(HERE, "logs", "probe-recover.json")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
NORMAL_MIN = 34000          # 正常页 36510-37369，低于此值视为截断
CHUNK_EDGE = 32768          # 2**15，形态 B 的精确边界


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception:
        return -1, b""


def classify(n):
    if n == 0:
        return "0B"
    if n < NORMAL_MIN:
        return "截断"
    return "OK"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--gap", type=float, default=10.0)
    ap.add_argument("--seed", type=int, default=20261008)
    a = ap.parse_args()

    if not os.path.exists(DB):
        print("找不到断点库：" + DB)
        return 3

    con = sqlite3.connect(DB)
    rows = list(con.execute(
        "SELECT url, category, number, error FROM pages "
        "WHERE status='pending' AND error<>'' ORDER BY url"))
    if not rows:
        print("没有已报错页")
        return 0
    random.Random(a.seed).shuffle(rows)
    rows = rows[:a.n]

    print("抽样 %d / %d 个已报错页；间隔 %.0fs；预计 %.1f 分钟"
          % (len(rows), len(rows), a.gap, len(rows) * a.gap / 60.0))
    print("-" * 74)

    res = []
    for i, (url, cat, num, err) in enumerate(rows, 1):
        code, body = fetch(url)
        n = len(body)
        tag = classify(n)
        has_html = b"</html>" in body[-2000:] if n else False
        res.append({"url": url, "category": cat, "number": num,
                    "bytes": n, "http": code, "tag": tag,
                    "closed_html": has_html, "orig_error": (err or "")[:60]})
        print("[%2d/%2d] %-4s %7d  html_end=%-5s %s"
              % (i, len(rows), tag, n, has_html, url), flush=True)
        if i < len(rows):
            time.sleep(a.gap)

    ok = sum(1 for r in res if r["tag"] == "OK")
    short = sum(1 for r in res if r["tag"] == "截断")
    zero = sum(1 for r in res if r["tag"] == "0B")
    print("-" * 74)
    print("复测结果：OK=%d  截断=%d  0B=%d   恢复率=%.1f%%"
          % (ok, short, zero, 100.0 * ok / len(res)))
    print("→ 恢复率高 ⇒ 原报错多为 A 型限流误判，应降速重试而非延期")
    print("→ 恢复率低 ⇒ 确为 B 型源站缺陷，延期正确")
    try:
        json.dump({"sampled": len(res), "ok": ok, "short": short, "zero": zero,
                   "recover_pct": round(100.0 * ok / len(res), 2),
                   "gap_s": a.gap, "seed": a.seed, "results": res},
                  open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("明细已写入 " + OUT)
    except OSError as e:
        print("写结果失败：%s" % e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
