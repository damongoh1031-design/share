#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""幂等性抽检门禁 —— **任何批量写名字列之前必须先跑这个。**

背景（2026-10-06 血泪）：
  DB3 CallApp 在 10:00 还返回真实的马来西亚/华人姓名（覆盖率 80%、名字稳定可复现），
  被一轮 300 次压力测试打过后，**降级为返回随机假名** —— HTTP 仍是 200，
  名字形态正常（`Maryam Thrush` / `Judge Sensenig`），但**每次查询都不同**。
  如果不做幂等性检查就回写，会把几千个假名灌进表格，且肉眼几乎无法发现。

判据（唯一可靠）：
  **同一号码连查 N 次，返回的名字必须完全一致。**
  不一致 ⇒ 该数据源当前输出随机垃圾，必须立即停止一切批量写入。

用法：
  PY=C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe
  "$PY" check_idempotent.py --source db3 --phone 60162281297 --repeat 5
  "$PY" check_idempotent.py --source db1 --phone 60162281297 --repeat 3 --gate

  --gate 模式下：不稳定 → exit 9（供驱动器调用，非 0 即中止跑批）

退出码：0 稳定可用 / 9 不稳定（数据源已被污染）/ 8 全部请求失败
"""
import argparse
import collections
import json
import re
import sys
import time

import requests
import urllib3

urllib3.disable_warnings()

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# ---- DB3 CallApp ----
# ⚠️ 不要加 tk 参数：tk=0011243853 已失效，带上会返回 X_C_CODE:-4 / HTTP 513，
#    不带 tk 才是有效调用（但内容自 2026-10-06 起已污染，见模块 docstring）。
DB3_URL = ("https://s.callapp.com/callapp-server/csrch"
           "?cpn=%2B{phone}&myp=gp.106898501948939491020&ibs=0&cid=0")
DB3_HEADERS = {"User-Agent": UA}

# ---- DB1 aunumber ----
PROBE_NUMBER = "60162281297"


def intl(msisdn):
    d = re.sub(r"\D", "", str(msisdn or ""))
    if not d:
        return ""
    if d.startswith("60"):
        return d
    if d.startswith("0"):
        return "60" + d[1:]
    return "60" + d


def ask_db3(phone):
    try:
        r = requests.get(DB3_URL.format(phone=phone), headers=DB3_HEADERS,
                         timeout=25, verify=False)
        if r.status_code != 200:
            return f"HTTP{r.status_code}"
        try:
            return (r.json() or {}).get("name", "") or "<empty>"
        except ValueError:
            return "<badjson>"
    except requests.RequestException as exc:
        return f"ERR:{type(exc).__name__}"


def ask_db1(phone):
    """复用 skill 里的 db1_batch 查询逻辑（只读、不写任何东西）。

    注意 db1_batch 里叫 local_to_intl（不是 intl），且要传 (mod, 国际号)。
    """
    import importlib.util
    import os
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db1_batch.py")
    spec = importlib.util.spec_from_file_location("_db1", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    pnl = mod.load_repo(mod.REPO)
    kind, payload = mod.query(pnl, mod.local_to_intl(phone), tries=1)
    if kind == "ok":
        return (payload or {}).get("name", "") or "<empty>"
    if kind == "blocked":
        return f"BLOCKED:{json.dumps(payload, ensure_ascii=False)}"
    return f"{kind}:{payload}"


SOURCES = {"db3": ask_db3, "db1": ask_db1}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=sorted(SOURCES), required=True)
    ap.add_argument("--phone", default=PROBE_NUMBER)
    ap.add_argument("--repeat", type=int, default=5)
    ap.add_argument("--gap", type=float, default=1.0)
    ap.add_argument("--gate", action="store_true",
                    help="不稳定时 exit 9，供驱动器当门禁用")
    ap.add_argument("--extra", default="",
                    help="额外对照号码，逗号分隔（建议带 1-2 个已知真实的）")
    args = ap.parse_args()

    ask = SOURCES[args.source]
    phone = intl(args.phone)
    targets = [phone] + [intl(x) for x in args.extra.split(",") if x.strip()]

    all_ok = True
    for t in targets:
        got = []
        for i in range(args.repeat):
            got.append(ask(t))
            if i < args.repeat - 1:
                time.sleep(args.gap)
        usable = [g for g in got
                  if g and not g.startswith(("HTTP", "ERR:", "BLOCKED:", "<empty>", "<badjson>"))]
        uniq = sorted(set(usable))
        if not usable:
            verdict, ok = "NO-DATA (undecidable)", False
        elif len(uniq) == 1:
            verdict, ok = f"STABLE  -> {uniq[0]!r}", True
        else:
            verdict, ok = f"RANDOM ({len(uniq)} distinct names!)", False
        all_ok = all_ok and ok
        print(f"[{args.source}] {t}: {got}")
        print(f"    -> {verdict}")

    print()
    if all_ok:
        # 纯 ASCII 输出：避免 GBK 代码页下 UnicodeEncodeError 导致非零退出
        # （2026-10-13 实测：✅ 在 cmd.exe GBK 环境 flush 时崩溃，驱动器误判门禁失败 exit 9）
        print(f"[OK] {args.source} idempotency PASS - safe to batch")
        return 0
    print(f"[FAIL] {args.source} idempotency FAILED - DO NOT write name column")
    print("   Same phone returned different names => source emits random junk.")
    return 9 if args.gate else 9


if __name__ == "__main__":
    sys.exit(main())
