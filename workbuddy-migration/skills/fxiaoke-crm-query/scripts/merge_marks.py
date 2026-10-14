"""
把 CRM 查询结果回写到 CSV 的指定列（默认 C 列），并保证输出文件与原文件**字节级对齐**。

用法：
    python merge_marks.py --src "原文件.csv" --result "查询结果.csv" --out "输出.csv" \
        --start-row 457 --col 3 --mark X

参数说明：
    --src        原始 CSV（不修改）
    --result     fx_phone_query.mjs 的输出 CSV（列：输入号码,查询号码,匹配数,客户名称,客户编号）
    --out        输出 CSV（默认在 src 同目录加 _filled 后缀）
    --start-row  从第几行开始处理（1-based，含），默认 1
    --col        要写标记的列号（1-based），默认 3
    --mark       命中时写入的标记，默认 "X"
    --phone-col  号码所在列号（1-based），默认 2

判定规则：结果里「匹配数」列 != "无数据" → 视为命中。
输出对齐：BOM / 换行符(CRLF|LF) / 末行是否带换行，全部按原文件原样保留，只改目标列。
（注意：用 encoding="utf-8-sig" 写出会凭空加 BOM，这是必须避免的坑。）
"""
import argparse
import csv
import io
import os
import sys


def read_raw(path):
    """返回 (文本, 是否有BOM, 换行符, 末尾是否有换行)"""
    raw = open(path, "rb").read()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    body = raw[3:] if has_bom else raw
    text = body.decode("utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    ends_nl = text.endswith(nl)
    return text, has_bom, nl, ends_nl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--result", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--start-row", type=int, default=1)
    ap.add_argument("--col", type=int, default=3)
    ap.add_argument("--mark", default="X")
    ap.add_argument("--phone-col", type=int, default=2)
    args = ap.parse_args()

    out = args.out or os.path.splitext(args.src)[0] + "_filled.csv"
    mark_i = args.col - 1
    tel_i = args.phone_col - 1

    # 1) 读查询结果：输入号码 -> 是否命中
    found = {}
    with open(args.result, encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f):
            if len(row) < 3 or row[0] in ("输入号码", ""):
                continue
            found[row[0].strip()] = (row[2] != "无数据")

    # 2) 读原文件（字节级探测格式）
    src_text, has_bom, nl, ends_nl = read_raw(args.src)
    rows = [r for r in csv.reader(io.StringIO(src_text)) if r]

    marked = notfound = skipped = 0
    for i, row in enumerate(rows, start=1):
        if i < args.start_row or len(row) <= max(mark_i, tel_i):
            continue
        tel = row[tel_i].strip()
        if not tel:
            skipped += 1
            continue
        if tel in found:
            if found[tel]:
                row[mark_i] = args.mark
                marked += 1
            else:
                notfound += 1
        else:
            skipped += 1

    # 3) 按原文件格式写出
    buf = io.StringIO()
    csv.writer(buf, lineterminator=nl).writerows(rows)
    out_text = buf.getvalue()
    if not ends_nl and out_text.endswith(nl):
        out_text = out_text[: -len(nl)]
    data = out_text.encode("utf-8")
    if has_bom:
        data = b"\xef\xbb\xbf" + data
    with open(out, "wb") as f:
        f.write(data)

    # 4) 校验：字节差应恰好 = 新增标记数
    orig_bytes = os.path.getsize(args.src)
    new_bytes = os.path.getsize(out)
    delta = new_bytes - orig_bytes
    expect = marked * len(args.mark.encode("utf-8"))
    print(f"处理行数: {len(rows)}")
    print(f"标记 {args.mark}: {marked}")
    print(f"无数据: {notfound}")
    print(f"未匹配到结果: {skipped}")
    print(f"BOM: {'有' if has_bom else '无'} | 换行: {nl!r} | 末尾换行: {ends_nl}")
    print(f"字节: {orig_bytes} -> {new_bytes} (差 {delta}，期望 {expect})")
    print(f"输出: {out}")
    if delta != expect:
        print("⚠️ 字节差与标记数不符，请检查！", file=sys.stderr)
        return 1
    print("✅ 字节级校验通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
