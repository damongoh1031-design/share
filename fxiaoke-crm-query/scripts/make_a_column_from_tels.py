#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
由「纯号码列表 + 全量重查结果」生成某区间的 A 列（名字列）2D JSON。

适用场景：源表只有号码列，要把 CRM 返回的**客户名称**写入名字列。
重查结果 s*_levels.csv 的列结构：
    0 号码 | 1 记录数 | 2 级别列表 | 3 PJ2名称 | 4 PJ1名称 | 5 其他级别名称 | 6 全部名称

判定口径由 --col 与 --only-if-empty 组合决定：
  --col N           取第 N 列的值作为写入内容
  --only-if-empty M 仅当第 M 列为空时才写（不传则不过滤）

例：把「无 PJ2 有 PJ1」的号码的 PJ1 名称写进名字列
  --col 4 --only-if-empty 3
     → 取 PJ1名称（第4列），但仅当 PJ2名称（第3列）为空时

行序对齐：tels 的第 i 行 == Sheet 第 (start + i) 行。

用法：
  python make_a_column_from_tels.py \
      --tels  s10001_tels.txt \
      --levels s10001_levels.csv \
      --out   s10001_a.json \
      --col 4 --only-if-empty 3
"""
import argparse, csv, json, sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tels', required=True, help='纯号码列表（每行一个，按 Sheet 行序）')
    ap.add_argument('--levels', required=True, help='全量重查结果 CSV')
    ap.add_argument('--out', required=True, help='输出 2D JSON')
    ap.add_argument('--col', type=int, required=True, help='取哪一列作为写入内容（0-based）')
    ap.add_argument('--only-if-empty', type=int, default=None,
                    help='仅当该列为空时才写（0-based，可选）')
    args = ap.parse_args()

    # 1. 读号码列表（保持行序）
    tels = [l.strip() for l in open(args.tels, encoding='utf-8') if l.strip()]

    # 2. 读重查结果 → {号码: 该行}
    lev = {}
    lev_rows = 0
    for row in csv.reader(open(args.levels, encoding='utf-8-sig')):
        if not row or row[0] == '号码':
            continue
        lev_rows += 1
        lev[row[0].strip()] = row

    # 3. 行序校验（强断言）
    if len(tels) != lev_rows:
        print(f'❌ 行数不匹配: tels {len(tels)} vs levels {lev_rows}', file=sys.stderr)
        sys.exit(1)

    # 4. 逐行判定
    out = []
    hits = 0
    for tel in tels:
        r = lev.get(tel)
        val = ''
        if r is not None:
            if args.only_if_empty is not None:
                guard = r[args.only_if_empty].strip() if len(r) > args.only_if_empty else ''
                if guard:
                    val = ''
                else:
                    val = r[args.col].strip() if len(r) > args.col else ''
            else:
                val = r[args.col].strip() if len(r) > args.col else ''
        out.append([val])
        if val:
            hits += 1

    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False)

    print(f'号码行数   : {len(tels)}')
    print(f'重查记录   : {lev_rows}')
    print(f'取列       : {args.col}' + (f'（仅当第 {args.only_if_empty} 列为空）'
                                       if args.only_if_empty is not None else ''))
    print(f'写入名字行 : {hits}')
    print(f'留空       : {len(out) - hits}')
    print(f'输出       : {args.out}')


if __name__ == '__main__':
    main()
