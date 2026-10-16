# -*- coding: utf-8 -*-
"""
make_a_column.py — 把 CRM 查询结果里的「客户名称」转成 Google Sheets 某一列的 2D JSON。

与 make_c_column.py 的区别：那个写命中标记（如 X），这个写客户名称本身。

输入：fx_phone_query.mjs 输出的 result CSV（列：输入号码,查询号码,匹配数,客户名称,客户编号）
输出：JSON 2D 数组 [["B  IRENE 2"],[""],...]，供 `gog sheets update <id> <range> --values-json=@file` 使用

用法：
    python make_a_column.py --result "result.csv" --out "a_column.json" --rows 10000

参数：
    --result   fx_phone_query.mjs 的输出 CSV（必需）
    --out      输出 JSON 文件（必需）
    --rows     期望数据行数；给出后若实际行数不符则拒绝写出（防止查询未跑完误写）
    --col      客户名称所在列（0-based），默认 3
    --keep-blank-mark  命中但客户名为空时，写占位符（默认写空串）
"""
import argparse
import csv
import json
import sys

NOT_HIT = ("", "无数据", "ERROR", "SKIP")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--result", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rows", type=int, default=None)
    ap.add_argument("--col", type=int, default=3)
    args = ap.parse_args()

    rows = []
    with open(args.result, encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.reader(f)):
            if i == 0 and row and row[0] in ("输入号码", ""):
                continue                                   # 跳过表头
            cnt = row[2] if len(row) > 2 else ""
            if cnt in NOT_HIT:                             # 未命中 → 留空
                rows.append([""])
                continue
            name = row[args.col].strip() if len(row) > args.col else ""
            rows.append([name])

    named = sum(1 for r in rows if r[0])
    print("结果行数: %d" % len(rows))
    print("有名字  : %d" % named)

    if args.rows is not None and len(rows) != args.rows:
        print("⚠️ 行数不符：期望 %d，实际 %d —— 查询可能未跑完，先别写入！"
              % (args.rows, len(rows)), file=sys.stderr)
        return 1

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False)
    print("已写出: %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
