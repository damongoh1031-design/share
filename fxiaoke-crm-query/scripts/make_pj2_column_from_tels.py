#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
由「纯号码列表 + 全量重查结果」生成某区间的 C 列 2D JSON。

适用场景：源表只有号码列（无 A 列姓名 / 无结果列），
        重查结果 s*_levels.csv 的列结构为：
            号码,记录数,级别列表,PJ2名称,PJ1名称,其他级别名称,全部名称

判定口径：仅当该号码有 PJ2（第 4 列非空）才写 'X'，否则留空。

行序对齐：tels 的第 i 行 == Sheet 第 (start + i) 行。
        （tels 是按 Sheet 行序抽取的，无表头）

用法：
  python make_pj2_column_from_tels.py \
      --tels  s10001_tels.txt \
      --levels s10001_levels.csv \
      --out   s10001_c.json
"""
import argparse, csv, json, sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tels', required=True, help='纯号码列表（每行一个，按 Sheet 行序）')
    ap.add_argument('--levels', required=True, help='全量重查结果 CSV')
    ap.add_argument('--out', required=True, help='输出 2D JSON')
    args = ap.parse_args()

    # 1. 读号码列表（保持行序）
    tels = [l.strip() for l in open(args.tels, encoding='utf-8') if l.strip()]

    # 2. 读重查结果 → {号码: PJ2名称}
    pj2 = {}
    lev_rows = 0
    for row in csv.reader(open(args.levels, encoding='utf-8-sig')):
        if not row or row[0] == '号码':
            continue
        lev_rows += 1
        tel = row[0].strip()
        name = row[3].strip() if len(row) > 3 else ''
        if name:
            pj2[tel] = name

    # 3. 行序校验（强断言：不一致直接失败，不静默继续）
    if len(tels) != lev_rows:
        print(f'❌ 行数不匹配: tels {len(tels)} vs levels {lev_rows}', file=sys.stderr)
        sys.exit(1)

    # 4. 逐行判定
    out = []
    hits = 0
    for tel in tels:
        if pj2.get(tel):
            out.append(['X'])
            hits += 1
        else:
            out.append([''])

    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False)

    print(f'号码行数   : {len(tels)}')
    print(f'重查记录   : {lev_rows}')
    print(f'有 PJ2 号码: {len(pj2)}')
    print(f'写 X 行数  : {hits}')
    print(f'留空       : {len(out) - hits}')
    print(f'输出       : {args.out}')


if __name__ == '__main__':
    main()
