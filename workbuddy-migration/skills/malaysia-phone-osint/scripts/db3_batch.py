#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DB3 CallApp 批量查名字 —— 面向「表格一列号码 → 填另一列」。

██████████████████████████████████████████████████████████████████████████████
🔴🔴🔴  当前不可用 —— 运行前必读  🔴🔴🔴

  2026-10-06 实测：DB3 对马来西亚号码已 **100% 返回随机假名**。
  同一号码连查 10 次返回 8 个不同名字、零重复
  （`Maryam Thrush` / `Judge Sensenig` / …，全首字母大写的美式姓名）。
  HTTP 仍是 200，形态完全正常 —— **肉眼与常规校验都发现不了**。

  污染未恢复。2026-10-08 终审补上决定性证据：**连明显无效的号码
  （60100000000 / 60111111111 / 60999999999）也照样返回名字**（5/5）
  ⇒ DB3 是无条件编造，连「有无这条记录」都不含信息。
  **已永久排除，不要再探活、不要写入。** 详见 references/DB3-CallApp-限流与污染实测.md 第 10 节。

  污染的触发点疑似是一轮 300 次压力测试（10:05–10:10），
  之后即降级。与请求速率无关（每 10 秒 1 次也照样随机）。

  ⚠️ 本脚本**默认拒绝运行**。要真跑必须显式加 `--i-know-db3-is-polluted`，
     并且**必须先**通过幂等性门禁：
         "$PY" check_idempotent.py --source db3 --repeat 5 --gate   # 必须 exit 0

  完整测验记录见 references/DB3-CallApp-限流与污染实测.md
██████████████████████████████████████████████████████████████████████████████

与 db1_batch.py 同构的控制流，端点：
  https://s.callapp.com/callapp-server/csrch?cpn=%2B<国际号>&myp=...&ibs=0&cid=0
  ⚠️ **不要加 tk / cvc** —— `tk=0011243853` 已失效，带上必返回 HTTP 513 / `X_C_CODE:-4`。
     原仓库 phone-number-lookup 的 CallApp 类写死了这两个值，所以直接跑原版永远 513。

退出码：0 正常 / 3 连续失败熔断 / 8 未通过污染警示确认
"""
import argparse
import json
import os
import random
import re
import sys
import time

import requests
import urllib3

urllib3.disable_warnings()

URL = ("https://s.callapp.com/callapp-server/csrch"
       "?cpn=%2B{phone}&myp=gp.106898501948939491020&ibs=0&cid=0")
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"),
    "Host": "s.callapp.com",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
}

# 只重试「服务端抖动」，不重试「确无数据」（525/空体/非JSON）
RETRY_BACKOFF = (1.5, 4.0, 9.0)


def intl(msisdn):
    """本地格式 → 国际格式（去掉前导 0，加 60）。"""
    d = re.sub(r"\D", "", str(msisdn or ""))
    if not d:
        return ""
    if d.startswith("60"):
        return d
    if d.startswith("0"):
        return "60" + d[1:]
    return "60" + d


def query(phone, session, retries=3):
    """返回 (kind, payload)。kind = 'ok' | 'empty' | 'error'"""
    last = None
    for attempt in range(retries + 1):
        try:
            r = session.get(URL.format(phone=phone), headers=HEADERS,
                            timeout=25, verify=False)
            if r.status_code == 200:
                try:
                    obj = r.json()
                except ValueError:
                    last = "bad-json"
                else:
                    name = (obj or {}).get("name", "") or ""
                    if name.strip():
                        return "ok", obj
                    return "empty", None          # 200 + 无 name = 真无数据，不重试
            last = f"HTTP {r.status_code}"          # 含 525
        except requests.RequestException as exc:
            last = f"{type(exc).__name__}"
        if attempt < retries:
            time.sleep(RETRY_BACKOFF[min(attempt, len(RETRY_BACKOFF) - 1)]
                       + random.uniform(0, 0.6))
    return "error", last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True, help="gog 导出的 A/B 二列 JSON")
    ap.add_argument("--startrow", type=int, default=1)
    ap.add_argument("--want", type=int, default=100, help="凑满 N 个命中就停（不是查询上限）")
    ap.add_argument("--out", required=True)
    ap.add_argument("--maxrows", type=int, default=0, help="0=不限")
    ap.add_argument("--delay", type=float, default=0.2, help="每次请求后的基础休眠秒数")
    ap.add_argument("--max-fail", type=int, default=40,
                    help="连续这么多次重试后仍失败就熔断（DB3 无封禁，阈值放宽）")
    ap.add_argument("--resume", action="store_true", help="跳过 JSONL 里已处理过的行")
    ap.add_argument("--probe", action="store_true", help="只探活一次")
    ap.add_argument("--probe-number", default="60162281297")
    ap.add_argument("--i-know-db3-is-polluted", action="store_true",
                    help="确认已知 DB3 返回随机假名，仍要运行（危险）")
    args = ap.parse_args()

    if not args.i_know_db3_is_polluted:
        print(__doc__)
        print("！！ 拒绝运行：DB3 当前返回随机假名，回写会污染整列。")
        print("！！ 若已用 check_idempotent.py --source db3 确认恢复稳定，")
        print("！！ 再加 --i-know-db3-is-polluted 重跑。")
        return 8

    session = requests.Session()

    if args.probe:
        kind, payload = query(args.probe_number, session)
        print(f"[probe] {kind.upper()}  {args.probe_number} -> "
              f"{json.dumps(payload, ensure_ascii=False) if payload else '(none)'}")
        return 0 if kind == "ok" else 1

    rows = json.load(open(args.sheet, encoding="utf-8"))
    jsonl = args.out + ".jsonl"
    done = set()
    if args.resume and os.path.exists(jsonl):
        for line in open(jsonl, encoding="utf-8"):
            try:
                done.add(json.loads(line)["row"])
            except (ValueError, KeyError):
                pass
        print(f"[resume] 已处理 {len(done)} 行", flush=True)

    # 先把模板落盘，异常退出也有文件
    json.dump({"found": [], "queried": 0, "last_row": args.startrow - 1,
               "blocked": [], "errors": []}, open(args.out, "w", encoding="utf-8"))

    fh = open(jsonl, "a", encoding="utf-8")
    found, block, errs = [], [], []
    q = hits = miss = 0
    consec_fail = 0
    last_row = args.startrow - 1
    t0 = time.time()
    stop_reason = "exhausted"

    for idx in range(args.startrow - 1, len(rows)):
        row_no = idx + 1
        if args.maxrows and row_no > args.startrow - 1 + args.maxrows:
            stop_reason = "maxrows"
            break
        if hits >= args.want:
            stop_reason = "want-reached"
            break
        if row_no in done:
            continue

        r = rows[idx]
        a = (r[0] or "").strip() if len(r) > 0 else ""
        b = (r[1] or "").strip() if len(r) > 1 else ""
        last_row = row_no
        if a or not b:                       # A 列已有名字 / B 列空 → 跳过
            continue

        p = intl(b)
        if not p:
            continue

        kind, payload = query(p, session)
        q += 1
        rec = {"row": row_no, "phone": b, "kind": kind}

        if kind == "ok":
            nm = payload.get("name", "")
            found.append({"row": row_no, "phone": b, "name": nm,
                          "priority": payload.get("priority"),
                          "extra": {k: v for k, v in payload.items()
                                    if k not in ("name", "priority")} or None})
            hits += 1
            consec_fail = 0
            rec["name"] = nm
        elif kind == "empty":
            miss += 1
            consec_fail = 0
        else:
            errs.append({"row": row_no, "phone": b, "why": payload})
            consec_fail += 1
            if consec_fail >= args.max_fail:
                stop_reason = "circuit-breaker"
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh.flush()
                break

        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        fh.flush()

        if q % 25 == 0:
            el = time.time() - t0
            print(f"  行{row_no} | 查{q} 命中{hits} ({hits/q*100:.0f}%) "
                  f"miss{miss} err{len(errs)} | {el/60:.1f}m "
                  f"| {q/el:.2f} 个/秒", flush=True)

        if args.delay:
            time.sleep(args.delay + random.uniform(0, args.delay))

    fh.close()
    dt = time.time() - t0
    json.dump({"found": found, "queried": q, "last_row": last_row,
               "blocked": block, "errors": errs,
               "stats": {"hits": hits, "miss": miss, "errors": len(errs),
                         "seconds": round(dt, 1),
                         "rate_per_sec": round(q / dt, 2) if dt else 0,
                         "stop": stop_reason}},
              open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"\n完成：扫到行 {last_row} | 查 {q} | 命中 {hits} ({hits/max(q,1)*100:.0f}%) "
          f"| miss {miss} | err {len(errs)} | {dt/60:.1f}m | 停止原因 {stop_reason}")
    return 3 if stop_reason == "circuit-breaker" else 0


if __name__ == "__main__":
    sys.exit(main())
