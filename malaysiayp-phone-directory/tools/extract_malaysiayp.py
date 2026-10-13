#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
extract_malaysiayp.py —— malaysiayp.com 页面【解析器】

    ★ 这不是爬虫。它不发起任何网络请求。
    只读取你已经【合法取得】的本地 HTML 文件，抽取「公司名 / 地址 / 电话」，
    按 tel: 数字去重、过滤 01X 手机号、输出 CSV。

用法:
    python extract_malaysiayp.py page1.html page2.html -o out.csv
    python extract_malaysiayp.py saved_pages/*.html -o out.csv --dry-run
    python extract_malaysiayp.py page.html -o out.csv --include-landline

--------------------------------------------------------------------------
开工前请确认（四项缺一不可，脚本会强制打印）：

  1. 授权 —— malaysiayp.com 的 robots.txt 已【明确 Disallow】
     GPTBot / ClaudeBot / Google-Extended / Applebot-Extended /
     meta-externalagent / CCBot。全量采集前必须取得站点书面授权或走官方接口。
  2. PDPA —— 聚合「公司名 + 手机号」即构成个人数据处理，须有合法性基础，
     并限定用途（仅目录检索/研究，不得群发、推销、骚扰或转售）。
  3. 限速 —— 并发 1、间隔 >= 2s、真实可联系 UA、遵守 Retry-After。
  4. 最小必要 —— 只取业务必需字段，设上限与熔断，产出后抽样核验。
--------------------------------------------------------------------------

选择器（一条记录 = 一个 li.row-item）:
    company : li.row-item > .row-main > span.row-name > a[href^="/item/"]
    address : li.row-item > .row-main > span.row-meta
    phone   : li.row-item > a.row-phone[href^="tel:"]      <- 用 href 里的数字
    去重键  : tel: 后的纯数字
"""
import argparse
import csv
import glob
import html
import os
import re
import sys

ROW = re.compile(
    r'<li class="row-item">'
    r'[\s\S]*?<a href="(/item/[^"]+)"[^>]*>([^<]+)</a>'
    r'[\s\S]*?<span class="row-meta">([^<]*)</span>'
    r'[\s\S]*?<a[^>]*class="row-phone"[^>]*href="tel:(\d+)"[^>]*>([^<]*)</a>',
    re.I,
)

MOBILE = re.compile(r"01\d{7,8}")          # 马来西亚手机：01X + 7~8 位
LANDLINE = re.compile(r"0[3-9]\d{7,8}")    # 座机

BANNER = """
======================================================================
 合规前置条件（缺一不可）
 1) 授权：该站 robots.txt 已明确 Disallow ClaudeBot / GPTBot 等 AI 爬虫，
    全量采集须先取得站点书面授权或走官方接口。
 2) PDPA 2010(2024)：聚合「公司名+手机号」= 个人数据处理，须有合法性基础，
    并限定用途（仅目录检索/研究；禁止群发 / 推销 / 骚扰 / 转售）。
 3) 限速：并发 1、间隔 >= 2s、真实可联系 UA、遵守 Retry-After。
 4) 最小必要：只取业务必需字段，设上限与熔断，产出后抽样核验。
======================================================================
"""


def parse_file(path, include_landline=False):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        h = fh.read()
    out = []
    for m in ROW.finditer(h):
        link, name, addr, tel, disp = m.groups()
        name = html.unescape(name).strip()
        addr = html.unescape(addr).strip()
        is_mob = bool(MOBILE.fullmatch(tel))
        if not is_mob and not (include_landline and LANDLINE.fullmatch(tel)):
            continue
        out.append({
            "company": name,
            "phone": tel,
            "display": disp.strip(),
            "type": "mobile" if is_mob else "landline",
            "address": addr,
            "detail_url": "https://malaysiayp.com" + link,
            "source_file": os.path.basename(path),
        })
    return out


def main():
    ap = argparse.ArgumentParser(description="malaysiayp.com 页面解析器（不联网）")
    ap.add_argument("files", nargs="+", help="本地 HTML 文件（支持通配符）")
    ap.add_argument("-o", "--out", default="malaysiayp_extract.csv")
    ap.add_argument("--dry-run", action="store_true", help="只统计，不写文件")
    ap.add_argument("--include-landline", action="store_true", help="连同座机一起导出")
    a = ap.parse_args()

    print(BANNER)

    paths = []
    for f in a.files:
        paths.extend(glob.glob(f) if any(c in f for c in "*?[") else [f])
    paths = [p for p in paths if os.path.isfile(p)]
    if not paths:
        sys.exit("没有找到任何输入文件")

    rows, seen = [], set()
    dup = 0
    for p in paths:
        for r in parse_file(p, a.include_landline):
            if r["phone"] in seen:
                dup += 1
                continue
            seen.add(r["phone"])
            rows.append(r)

    mob = sum(1 for r in rows if r["type"] == "mobile")
    lan = len(rows) - mob
    print(f"输入文件      : {len(paths)}")
    print(f"唯一记录      : {len(rows)}  （手机 {mob} / 座机 {lan}；去重丢弃 {dup}）")
    if rows:
        print(f"示例          : {rows[0]['company']} | {rows[0]['display']} | {rows[0]['address'][:40]}")

    if a.dry_run:
        print("\n[dry-run] 未写文件。")
        return

    with open(a.out, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "company", "phone", "display", "type", "address", "detail_url", "source_file"])
        w.writeheader()
        w.writerows(rows)
    print(f"\n已写入 {len(rows)} 行 -> {a.out}")
    print("提醒：导出后请抽样核验，并保留 detail_url 作为来源留痕。")


if __name__ == "__main__":
    main()
