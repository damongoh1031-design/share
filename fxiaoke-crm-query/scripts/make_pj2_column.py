#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_pj2_column.py — 把「全量重查的 PJ2 判定结果」转成可写回 Sheet 的 2D JSON。

输入:
  --base   原始查询结果 CSV（s1210_result.csv），列序: 输入号码,查询号码,匹配数,客户名称,客户编号
           其行序 == Sheet 的数据行序（第 14 行起）
  --levels 全量重查结果 CSV（s1210_levels.csv），列序: 号码,记录数,级别列表,PJ2名称,PJ1名称,其他级别名称,全部名称
  --start  起始行号（1-based，Sheet 里的行号），默认 14
  --end    结束行号（含），默认 1665
输出:
  --out    2D JSON 数组，形如 [["X"],[""],...]，长度 == end-start+1
"""
import csv, json, argparse, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True)
    ap.add_argument('--levels', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--start', type=int, default=14)
    ap.add_argument('--end', type=int, default=1665)
    args = ap.parse_args()

    # 1. 读基表：拿到行序 + 每行归一化后的查询号码
    base = []
    with open(args.base, 'r', encoding='utf-8-sig', newline='') as f:
        for row in csv.reader(f):
            if not row:
                continue
            if row[0] == '输入号码':
                continue
            base.append(row)
    print(f'基表数据行: {len(base)}')

    # 2. 读全量重查：号码 -> 是否有 PJ2
    pj2 = {}      # 查询号码 -> PJ2 名称（非空表示命中）
    with open(args.levels, 'r', encoding='utf-8-sig', newline='') as f:
        r = csv.DictReader(f)
        for row in r:
            tel = (row.get('号码') or '').strip()
            if not tel:
                continue
            pj2[tel] = (row.get('PJ2名称') or '').strip()
    print(f'重查记录: {len(pj2)}  其中含PJ2: {sum(1 for v in pj2.values() if v)}')

    # 3. 逐行判定
    #    关键：基表第 1 行 == Sheet 第 1 行（无表头），所以 Sheet 第 start 行 == base[start-1]
    #    输出长度必须 == end-start+1，且逐行对应 Sheet[start..end]
    n = args.end - args.start + 1
    lo = args.start - 1          # 0-based 起始索引
    hi = args.end                # 0-based 结束索引（不含）
    if len(base) != args.end:
        print(f'⚠️  基表行数 {len(base)} != Sheet 末行 {args.end}（预期基表覆盖 1..{args.end}）', file=sys.stderr)
    out = []
    hits = 0
    for idx in range(lo, min(hi, len(base))):
        tel = (base[idx][1] if len(base[idx]) > 1 else '').strip()
        if tel and pj2.get(tel):
            out.append(['X']); hits += 1
        else:
            out.append([''])
    # 补齐（基表不足时）
    while len(out) < n:
        out.append([''])

    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False)

    print(f'基表行序==Sheet行号，取值 base[{lo}:{hi}] → 写回 Sheet!C{args.start}:C{args.end}')
    print(f'输出行数     : {len(out)}  (应为 {n})')
    print(f'PJ2 命中写 X : {hits}')
    print(f'留空         : {len(out) - hits}')
    print(f'输出: {args.out}')

if __name__ == '__main__':
    main()
