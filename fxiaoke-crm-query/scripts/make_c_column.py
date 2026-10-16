# -*- coding: utf-8 -*-
"""
make_c_column.py — 把 CRM 查询结果转成 Google Sheets 某一列的 2D JSON 数组。

输入：fx_phone_query.mjs 输出的 result CSV（列：输入号码,查询号码,匹配数,客户名称,客户编号）
输出：JSON 2D 数组 [["X"],[""],...]，供 `gog sheets update <id> <range> --values-json @file` 使用

用法：
    python make_c_column.py --result "result.csv" --out "col.json" --rows 1209 --mark X

参数说明：
    --result   fx_phone_query.mjs 的输出 CSV（必需）
    --out      输出 JSON 文件（必需）
    --rows     期望数据行数；给出后若实际行数不符则拒绝写出（防止查询未跑完误写），默认不校验
    --mark     命中时写入的标记，默认 "X"

判定规则：结果里「匹配数」列 ∉ {"", 无数据, ERROR, SKIP} → 视为命中（异常值不计为命中，比 merge_marks 更严格）。
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
    ap.add_argument("--mark", default="X")
    args = ap.parse_args()

    rows = []
    with open(args.result, encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.reader(f)):
            if i == 0 and row and row[0] in ("输入号码", ""):
                continue                      # 跳过表头
            if len(row) < 3:
                rows.append([""])
                continue
            hit = row[2] not in NOT_HIT
            rows.append([args.mark if hit else ""])

    hits = sum(1 for r in rows if r[0] == args.mark)
    print("结果行数: %d" % len(rows))
    print("命中(%s): %d" % (args.mark, hits))
    print("未命中 : %d" % (len(rows) - hits))

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
