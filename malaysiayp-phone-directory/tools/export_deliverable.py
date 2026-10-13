#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""malaysiayp 交付物导出器。

从断点库 data/malaysiayp_full.csv.sqlite3 导出可直接使用的成品 CSV。
特性：
  * 只读断点库（不写、不锁、不改任何状态）
  * 不触网
  * `no` 列全局连续（1..N），跨批次稳定重排
  * 公式注入防护：以 = + - @ 开头的字段加前导撇号（与采集脚本一致）
  * UTF-8 BOM + CRLF，Excel 双击即正常
  * 产出 meta.json（行数 / 字节数 / SHA256 / 覆盖度）

用法：
  python export_deliverable.py                 # 导出到 data/deliverable/
  python export_deliverable.py --out-dir DIR
  python export_deliverable.py --quiet
"""
import argparse
import csv
import hashlib
import json
import os
import sqlite3
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "malaysiayp_full.csv.sqlite3")
JOB = os.path.join(HERE, "data", "malaysiayp_full.csv.job.json")
DEF_OUT = os.path.join(HERE, "data", "deliverable")

CSV_COLS = ["no", "company", "phone", "display",
            "category", "address", "detail_url", "source_page"]
EXT_COLS = CSV_COLS + ["raw_phone", "phone_status", "entry_id"]
DANGEROUS = "=+-@"

# 与采集脚本 _full_filter('mobile') 完全一致
MOBILE_WHERE = ("(phone GLOB '01[0-9]*' AND length(phone)=10) "
                "OR (phone GLOB '011[0-9]*' AND length(phone)=11)")
ORDER = "ORDER BY category, company, id"


def protect(value):
    """公式注入防护：前导撇号，与 scrape_malaysiayp.py::_full_csv_row 一致。"""
    if value and value.lstrip().startswith(tuple(DANGEROUS)):
        return "'" + value
    return value


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path, cols, rows):
    """rows: 可迭代的 dict（键为 cols 子集）"""
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        n = 0
        for r in rows:
            w.writerow({c: protect(r.get(c) or "") for c in cols})
            n += 1
    return n


def build_rows(con, where=None, extended=False):
    sql = ("SELECT id, company, phone, display, category, address, "
           "detail_url, source_page, raw_phone, phone_status FROM entries")
    if where:
        sql += " WHERE " + where
    sql += " " + ORDER
    for i, r in enumerate(con.execute(sql), 1):
        d = {
            "no": str(i),
            "company": r[1] or "",
            "phone": r[2] or "",
            "display": r[3] or "",
            "category": r[4] or "",
            "address": r[5] or "",
            "detail_url": r[6] or "",
            "source_page": r[7] or "",
        }
        if extended:
            d["raw_phone"] = r[8] or ""
            d["phone_status"] = r[9] or ""
            d["entry_id"] = str(r[0])
        yield d


def coverage(con, job):
    q = con.execute
    done = q("SELECT count(*) FROM pages WHERE status='done'").fetchone()[0]
    pending = q("SELECT count(*) FROM pages WHERE status='pending'").fetchone()[0]
    total_queued = done + pending
    cats_total = q("SELECT count(*) FROM categories").fetchone()[0]
    cats_idx = q("SELECT count(*) FROM categories WHERE index_state='done'").fetchone()[0]
    # 已索引分类的页数总和（真实值）
    idx_pages = q("SELECT coalesce(sum(pages),0) FROM categories "
                  "WHERE index_state='done'").fetchone()[0]
    # 未索引分类的页数未知，用已索引分类外推。三档估计，避免单点误导：
    #   低 = 每分类 1 页（下界，等于 categories.pages 默认值）
    #   中 = 剔除前 2 大分类后的均值（避免被巨型分类拉高）
    #   高 = 全量均值（若未索引分类里也藏着巨型分类）
    top2 = q("SELECT coalesce(sum(pages),0) FROM (SELECT pages FROM categories "
             "WHERE index_state='done' ORDER BY pages DESC LIMIT 2)").fetchone()[0]
    rest_n = max(cats_idx - 2, 1)
    mid_avg = max((idx_pages - top2) / rest_n, 1.0)
    high_avg = max(idx_pages / max(cats_idx, 1), 1.0)
    missing = max(cats_total - cats_idx, 0)
    est_low = idx_pages + missing * 1.0
    est_mid = idx_pages + missing * mid_avg
    est_high = idx_pages + missing * max(mid_avg * 2.0, high_avg * 0.25)
    est_total = est_mid
    err = q("SELECT count(*) FROM pages WHERE status='pending' AND error<>''").fetchone()[0]
    zero = q("SELECT count(*) FROM pages WHERE error LIKE '%0B%'").fetchone()[0]
    ent = q("SELECT count(*) FROM entries").fetchone()[0]
    return {
        "pages_done": done,
        "pages_pending": pending,
        "pages_queued_known": total_queued,
        "pct_of_queued": round(100.0 * done / total_queued, 2) if total_queued else 0.0,
        "categories_total": cats_total,
        "categories_indexed": cats_idx,
        "categories_not_indexed": cats_total - cats_idx,
        "pages_from_indexed_categories": idx_pages,
        "estimated_total_pages_low": int(round(est_low)),
        "estimated_total_pages_mid": int(round(est_mid)),
        "estimated_total_pages_high": int(round(est_high)),
        "estimated_total_pages": int(round(est_mid)),
        "estimated_true_pct": round(100.0 * done / est_mid, 2) if est_mid else 0.0,
        "estimated_true_pct_range": [
            round(100.0 * done / est_high, 2) if est_high else 0.0,
            round(100.0 * done / est_low, 2) if est_low else 0.0],
        "errored_pages": err,
        "zero_byte_pages": zero,
        "entities_stored": ent,
        "note": ("pages_queued_known 只含已索引分类；未索引分类（%d 个）尚未展开，"
                 "真实总页数落在 %d–%d 之间（中值 %d），"
                 "故 pages_queued_known 会显著低估总量。"
                 % (missing, est_low, est_high, est_mid)),
    }


README_TMPL = """# malaysiayp 电话号码目录 · 交付物

导出时间：{ts}
数据源：`data/malaysiayp_full.csv.sqlite3`（采集脚本 v{ver}）

## 一、文件清单

| 文件 | 行数 | 说明 |
|---|---:|---|
| `malaysiayp_all.csv` | {all_rows} | **主交付**。全部有效记录，含座机与手机 |
| `malaysiayp_mobile.csv` | {mob_rows} | 仅马来西亚手机号（`01X-XXXXXXX` / `011-XXXXXXXX`） |
| `malaysiayp_all_extended.csv` | {ext_rows} | 11 列诊断版，含 `raw_phone` / `phone_status` / `entry_id` |
| `malaysiayp_quarantine.csv` | {qua_rows} | 号码无效或缺失的记录，供人工排查 |
| `meta.json` | — | 行数 / 字节数 / SHA256 / 覆盖度 |

## 二、列定义

| 列 | 说明 |
|---|---|
| `no` | 全局连续序号（1..N），按 `category, company, id` 排序后重编 |
| `company` | 商家名称 |
| `phone` | 归一化号码（纯数字，无分隔符）。手机号 10 或 11 位，座机 8–9 位 |
| `display` | 站点原始展示格式（含空格/连字符），便于人工核对 |
| `category` | 来源分类 slug |
| `address` | 地址（可能为空） |
| `detail_url` | 商家详情页 |
| `source_page` | 抓取该记录的分类列表页 |

## 三、覆盖度（重要）

| 指标 | 值 |
|---|---:|
| 已完成页 / 已入队页 | {done} / {queued}（{pct_q}%） |
| 分类总数 | {cats} |
| 已索引分类 | {cats_idx} |
| 未索引分类 | {cats_miss} |
| 估计真实总页数 | {est_low} – {est_high}（中值 {est_pages}） |
| **估计真实覆盖率** | **≈ {est_pct}%** |

> 当前为**阶段快照**，不是终版。采集仍在进行，覆盖率会持续上升。
> 未索引分类尚未展开页数，因此 `pages_queued_known` 会低估总量。

## 四、数据质量

- 号码校验：`_FULL_PHONE_ALL` 正则（`0\\d{{7,10}}` / `1[38]00\\d{{6,8}}`）全量校验，不合格入 `quarantine`
- 去重：DB 层 `UNIQUE(detail_url, phone)`，同公司多号码保留多行
- 公式注入防护：以 `= + - @` 开头的字段加前导撇号（Excel/Sheets 不会执行）
- 编码：UTF-8 **带 BOM**，CRLF 换行，Excel 双击即正常显示中文
- 完整性：每行均含 `company` / `category` / `detail_url` / `source_page`

## 五、使用注意

1. **合规**：数据来源为公开商业目录，含个人数据（公司名+手机号），受马来西亚 PDPA 2010 约束。
   仅限目录检索 / 研究用途；**禁止群发、推销、骚扰、转售**。
2. **手机号列可能为空**：`malaysiayp_all.csv` 保留号码缺失的记录（`phone` 为空），
   需要纯号码清单请用 `malaysiayp_mobile.csv`。
3. **重跑**：数据更新后重新执行 `python export_deliverable.py` 即可覆盖产出。

## 六、更新方式

```bash
# 查看采集进度
python supervise.py --status

# 重新导出最新交付物
python export_deliverable.py
```
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=DEF_OUT)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    say = (lambda *x: None) if a.quiet else print

    if not os.path.exists(DB):
        say("找不到断点库：" + DB)
        return 3
    out = a.out_dir
    os.makedirs(out, exist_ok=True)

    con = sqlite3.connect("file:%s?mode=ro" % DB.replace("\\", "/"), uri=True)
    job = {}
    if os.path.exists(JOB):
        try:
            job = json.load(open(JOB, encoding="utf-8"))
        except (OSError, ValueError):
            job = {}
    ver = ((job.get("script") or {}).get("version")) or "?"

    files = []
    say("导出到 " + out)
    specs = [
        ("malaysiayp_all.csv", CSV_COLS, None, False),
        ("malaysiayp_mobile.csv", CSV_COLS, MOBILE_WHERE, False),
        ("malaysiayp_all_extended.csv", EXT_COLS, None, True),
        ("malaysiayp_quarantine.csv", EXT_COLS,
         "phone_status IN ('invalid','missing')", True),
    ]
    for name, cols, where, ext in specs:
        path = os.path.join(out, name)
        n = write_csv(path, cols, build_rows(con, where, ext))
        size = os.path.getsize(path)
        files.append({"name": name, "rows": n, "bytes": size,
                      "sha256": sha256_of(path)})
        say("  %-28s %6d 行  %9d 字节" % (name, n, size))

    cov = coverage(con, job)
    con.close()

    meta = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "generated_epoch": int(time.time()),
        "source_db": DB,
        "source_db_mtime": time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.localtime(os.path.getmtime(DB))),
        "script_version": ver,
        "columns": CSV_COLS,
        "extended_columns": EXT_COLS,
        "mobile_rule": MOBILE_WHERE,
        "formula_protection": "leading apostrophe for values starting with " + DANGEROUS,
        "encoding": "utf-8-sig (BOM)",
        "newline": "CRLF",
        "files": files,
        "coverage": cov,
        "compliance": ("公开商业目录；含个人数据（公司名+手机号），受马来西亚 PDPA 2010 "
                       "约束；仅限目录检索/研究，禁止群发、推销、骚扰、转售。"),
    }
    mpath = os.path.join(out, "meta.json")
    json.dump(meta, open(mpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    by = {f["name"]: f["rows"] for f in files}
    rpath = os.path.join(out, "README.md")
    open(rpath, "w", encoding="utf-8").write(README_TMPL.format(
        ts=meta["generated_at"], ver=ver,
        all_rows=by.get("malaysiayp_all.csv", 0),
        mob_rows=by.get("malaysiayp_mobile.csv", 0),
        ext_rows=by.get("malaysiayp_all_extended.csv", 0),
        qua_rows=by.get("malaysiayp_quarantine.csv", 0),
        done=cov["pages_done"], queued=cov["pages_queued_known"],
        pct_q=cov["pct_of_queued"], cats=cov["categories_total"],
        cats_idx=cov["categories_indexed"],
        cats_miss=cov["categories_not_indexed"],
        est_pages=cov["estimated_total_pages"],
        est_low=cov["estimated_total_pages_low"],
        est_high=cov["estimated_total_pages_high"],
        est_pct=cov["estimated_true_pct"],
    ))
    say("  %-28s （覆盖度 %s%% / 估计真实 %s%%）"
        % ("meta.json + README.md", cov["pct_of_queued"], cov["estimated_true_pct"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
