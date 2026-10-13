#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
电话黄页收集器 —— 号码 -> 身份 -> 来源渠道，一行一条，追加进 data/records.csv

复用 malaysia-phone-osint 技能里的采集脚本：
    A 层 my_phone_check.py   （号段解析 + PDRM Semak Mule）
    D 层 crowd_lookup.py     （busuk.my + junk-call）
    D 层 callapp_lookup.py   （CallApp 众包备注，当前唯一稳定可用众包库）

用法:
    python collector.py 0123956969
    python collector.py 0123956969 0162281297 --json
    python collector.py --file numbers.txt

合规: 只做公开数据源的只读单点查询。众包返回的是通讯录备注，不是实名。
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "records.csv")
SKILL = r"C:/Users/Admin/.workbuddy-ai/skills/malaysia-phone-osint/scripts"
PY = r"C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"

HEADER = ["number", "name", "entity", "source", "layer", "reliability", "date", "note"]


def run(script, *args, timeout=90):
    """跑技能脚本，返回 (ok, stdout)。脚本不存在或超时都算失败，不抛异常。"""
    path = os.path.join(SKILL, script)
    if not os.path.exists(path):
        return False, f"[skip] {script} not found"
    try:
        r = subprocess.run(
            [PY, path, *args],
            capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace",
        )
        return r.returncode == 0, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return False, f"[timeout] {script}"
    except Exception as exc:                       # noqa: BLE001
        return False, f"[error] {script}: {exc}"


def local(fmt):
    """+60123956969 / 60123956969 / 012-395 6969 -> 0123956969（Semak Mule 只认本地格式）"""
    d = re.sub(r"\D", "", fmt or "")
    if d.startswith("60"):
        d = "0" + d[2:]
    return d


def collect(number):
    """对一个号码跑 A/C/D 三层，返回记录列表。"""
    rows = []
    loc = local(number)

    # ---- A 层 + C 层 ----
    ok, out = run("my_phone_check.py", loc)
    if ok:
        def grab(label):
            m = re.search(re.escape(label) + r"\s*:\s*(.+)", out)
            return m.group(1).strip() if m else ""
        rows.append({
            "number": number,
            "name": "(号段/举报核对)",
            "entity": f"{grab('号码类型')} / {grab('号段运营商')} / Semak Mule: {grab('归属地') or '见下'}",
            "source": "libphonenumber + PDRM Semak Mule",
            "layer": "A",
            "reliability": "高",
            "date": "auto",
            "note": "号段运营商不穿透 MNP；无记录 ≠ 安全",
        })
        mule = "有记录" if ("无记录" not in out and "Semak" in out) else "无记录"
        rows[-1]["entity"] = f"{grab('号码类型')} / {grab('号段运营商')} / Semak Mule: {mule}"
    else:
        rows.append({"number": number, "name": "(A/C 层失败)", "entity": out[:120],
                     "source": "my_phone_check.py", "layer": "A", "reliability": "低",
                     "date": "auto", "note": "脚本不可用"})

    # ---- D 层: 众包 ----
    ok, out = run("crowd_lookup.py", loc)
    if ok:
        risk = ""
        m = re.search(r"风险等级\s*:\s*(.+)", out)
        if m:
            risk = m.group(1).strip()
        rows.append({
            "number": number, "name": "(busuk.my)", "entity": risk or "无社区报告",
            "source": "busuk.my", "layer": "D", "reliability": "低", "date": "auto",
            "note": "页面按需生成；无数据 ≠ 有人提过",
        })

    # ---- D 层: CallApp ----
    ok, out = run("callapp_lookup.py", loc, "--json")
    if ok:
        try:
            blob = json.loads(out[out.index("{"):out.rindex("}") + 1])
        except Exception:                          # noqa: BLE001
            blob = {}
        if blob.get("blocked"):
            rows.append({"number": number, "name": "(CallApp 限流)", "entity": "X_C_CODE -4",
                         "source": "CallApp", "layer": "D", "reliability": "不可用",
                         "date": "auto", "note": "约 100 次/窗口，冷却 ≥1 小时"})
        else:
            nm = (blob.get("raw") or {}).get("name") or "(空)"
            rows.append({"number": number, "name": nm,
                         "entity": "CallApp 通讯录备注（非实名）",
                         "source": "CallApp", "layer": "D", "reliability": "低",
                         "date": "auto", "note": "只做验证假设用，不可当实名"})

    return rows


def append(rows):
    new = not os.path.exists(OUT)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "a", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        if new:
            w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("numbers", nargs="*")
    ap.add_argument("--file", help="每行一个号码的文件")
    ap.add_argument("--json", action="store_true", help="只输出 JSON")
    a = ap.parse_args()

    nums = list(a.numbers)
    if a.file and os.path.exists(a.file):
        with open(a.file, encoding="utf-8") as fh:
            nums += [ln.strip() for ln in fh if ln.strip()]

    if not nums:
        ap.error("请给出至少一个号码，或用 --file")

    all_rows = []
    for n in nums:
        rows = collect(n)
        all_rows += rows
        if not a.json:
            print(f"\n===== {n} =====")
            for r in rows:
                print(f"  [{r['layer']}/{r['reliability']}] {r['name']}  <- {r['source']}")
                print(f"      {r['entity']}")

    append(all_rows)

    if a.json:
        print(json.dumps(all_rows, ensure_ascii=False, indent=2))
    else:
        print(f"\n已追加 {len(all_rows)} 条 -> {OUT}")


if __name__ == "__main__":
    main()
