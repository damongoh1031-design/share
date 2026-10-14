#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A 列（DB1 反查结果）静态质量审查 —— 只读，不写表。

DB3 已被判定为完全随机，无法用于交叉验证，故改为对 A 列做**内部一致性审查**：
  1) 覆盖与分布：逐 500 行区间的命中率
  2) 名称频次：高频名（疑似公司/总机/营业厅）
  3) 形态异常：含数字、长度过短、全大写、含异常字符
  4) 书写系统分布：中文 / 拉丁 / 泰米尔 / 阿拉伯 —— 马来西亚通讯录应以此为主
  5) DB3 污染泄漏检测：把已知的 DB3 随机假名与 A 列比对

用法：
  "$PY" db1_colA_audit.py --sheet sheet_now.json --out report.md
"""
import argparse
import collections
import json
import re
import unicodedata

# 2026-10-08 实测抓到的 DB3 随机假名样本（用于泄漏检测）
DB3_FAKE = {
    "Nidia Layton", "Leiah Bevan", "Frida Holmberg", "Lashone Marsden",
    "Terresa Garnes", "Aidee Bever", "Williams May", "Steffon Domingue",
    "Jewel Grigsby", "Madai Pair", "Hadiya Lehner", "Daiana Lacasse",
    "Mitch Blodgett", "Sabrea Baynes", "Delray Guglielmo", "Torris Clinton",
    "Cristoval Moen", "Jamesmichael Beebe", "Sherice Bannon",
    "Odie Mikkelsen", "Pearl Bednar", "Keo Maney", "Maryam Thrush",
    "Judge Sensenig",
}


def script_of(s):
    """粗略判定书写系统。"""
    cjk = sum(1 for c in s if "\u4e00" <= c <= "\u9fff")
    tamil = sum(1 for c in s if "\u0b80" <= c <= "\u0bff")
    arab = sum(1 for c in s if "\u0600" <= c <= "\u06ff")
    latin = sum(1 for c in s if c.isascii() and c.isalpha())
    n = max(len(s.strip()), 1)
    if cjk / n > 0.3:
        return "中文"
    if tamil / n > 0.3:
        return "泰米尔"
    if arab / n > 0.3:
        return "阿拉伯"
    if latin / n > 0.5:
        return "拉丁"
    return "其它"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True)
    ap.add_argument("--block", type=int, default=500)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    rows = json.load(open(args.sheet, encoding="utf-8"))
    total = len(rows)
    a_vals, b_vals = [], []
    for i, r in enumerate(rows):
        a = (r[0] or "").strip() if len(r) > 0 else ""
        b = (r[1] or "").strip() if len(r) > 1 else ""
        a_vals.append(a)
        b_vals.append(b)

    filled = [(i + 1, a) for i, a in enumerate(a_vals) if a]
    b_nonempty = sum(1 for b in b_vals if b)
    L = []
    P = L.append

    P("# A 列（DB1 反查结果）静态质量审查")
    P("")
    P(f"- 表总行数：**{total}**")
    P(f"- B 列非空：**{b_nonempty}**")
    P(f"- A 列非空：**{len(filled)}**")
    P(f"- 已填 A / B 非空 = **{len(filled)/max(b_nonempty,1)*100:.1f}%**")
    P("")

    # ---- 1) 分块命中率 ----
    P(f"## 1. 分块覆盖（每 {args.block} 行）")
    P("")
    P("| 行区间 | B 非空 | A 非空 | 命中率 |")
    P("|---|---|---|---|")
    for s in range(0, total, args.block):
        e = min(s + args.block, total)
        nb = sum(1 for b in b_vals[s:e] if b)
        na = sum(1 for a in a_vals[s:e] if a)
        if nb == 0 and na == 0:
            continue
        P(f"| {s+1}–{e} | {nb} | {na} | {na/max(nb,1)*100:.0f}% |")
    P("")

    # ---- 2) 名称频次 ----
    cnt = collections.Counter(a for _, a in filled)
    P(f"## 2. 高频名（Top {args.top}，共 {len(cnt)} 个不同名）")
    P("")
    P("| 次数 | 名字 |")
    P("|---|---|")
    for nm, c in cnt.most_common(args.top):
        P(f"| {c} | {nm} |")
    P("")
    dup = [(n, c) for n, c in cnt.items() if c >= 3]
    P(f"- 出现 ≥3 次的名字：**{len(dup)}** 个，占已填 **{sum(c for _, c in dup)}** 行")
    P(f"- 唯一名占比：**{len(cnt)/max(len(filled),1)*100:.1f}%**")
    P("")

    # ---- 3) 形态异常 ----
    P("## 3. 形态异常")
    P("")
    has_digit = [(r, a) for r, a in filled if re.search(r"\d", a)]
    too_short = [(r, a) for r, a in filled if len(a.strip()) <= 2]
    all_caps = [(r, a) for r, a in filled
                if len(a) > 3 and a == a.upper() and re.search(r"[A-Z]", a)]
    odd_char = [(r, a) for r, a in filled
                if re.search(r"[^\w\s\u4e00-\u9fff.\-'/&()@+]", a)]
    P(f"| 类型 | 行数 | 示例 |")
    P("|---|---|---|")
    P(f"| 含数字 | {len(has_digit)} | {[a for _, a in has_digit[:5]]} |")
    P(f"| 长度 ≤2 | {len(too_short)} | {[a for _, a in too_short[:5]]} |")
    P(f"| 全大写 | {len(all_caps)} | {[a for _, a in all_caps[:5]]} |")
    P(f"| 含异常字符 | {len(odd_char)} | {[a for _, a in odd_char[:5]]} |")
    P("")

    # ---- 4) 书写系统 ----
    sc = collections.Counter(script_of(a) for _, a in filled)
    P("## 4. 书写系统分布")
    P("")
    P("| 书写系统 | 行数 | 占比 |")
    P("|---|---|---|")
    for k, v in sc.most_common():
        P(f"| {k} | {v} | {v/max(len(filled),1)*100:.1f}% |")
    P("")

    # ---- 5) DB3 污染泄漏 ----
    leak = [(r, a) for r, a in filled if a in DB3_FAKE]
    P("## 5. DB3 污染泄漏检测")
    P("")
    P(f"用 {len(DB3_FAKE)} 个已知 DB3 随机假名与 A 列逐一比对：")
    P("")
    P(f"- 命中：**{len(leak)}** 行" + (f" → {leak}" if leak else " → **无泄漏** ✅"))
    P("")

    # ---- 6) 重复占用 ----
    P("## 6. 同名多行（Top 10）")
    P("")
    P("| 名字 | 行号（前 12 个） |")
    P("|---|---|")
    byname = collections.defaultdict(list)
    for r, a in filled:
        byname[a].append(r)
    for nm, c in cnt.most_common(10):
        P(f"| {nm} | {byname[nm][:12]} |")
    P("")

    txt = "\n".join(L)
    print(txt)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(txt)
        print(f"\n[written] {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
