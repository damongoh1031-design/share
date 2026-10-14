#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CallerID（DataBase 1 / aunumber.com）批量准确率验证器

phone-number-lookup 的 DB1 接口：
    POST https://app.aunumber.com/api/v1/sea.php
    响应经三层编码（位移 → 逐字符 chr → base64），解密后是 JSON：
    name / avater / belong_area / address / report_count / old_tel_number / type_label

原脚本 start_callerid_check() 只 print 不 return，且 --more 分支会打印完整 JSON。
本脚本捕获其 stdout 并解析出 JSON，批量跑号码，与已知答案做三级对比：
    ① 全串精确匹配
    ② 子串包含
    ③ token 级模糊匹配（编辑距离 ≤ 1）—— 用于识别 "Dato Dr Ricky" vs "Dato Ricky Lim" 这类部分命中

用法：
    python verify_callerid.py --repo <phone-number-lookup 目录> --recheck \
        "0123355873|roland leong" "0122071768|dato ricky lim"
"""
import argparse
import contextlib
import importlib.util
import io
import json
import os
import re
import sys


def load_repo(repo: str):
    path = os.path.join(repo, "lookup.py")
    if not os.path.exists(path):
        raise SystemExit(f"找不到 {path}")
    spec = importlib.util.spec_from_file_location("pnl_lookup", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pnl_lookup"] = mod
    spec.loader.exec_module(mod)
    return mod


def local_to_intl(raw: str) -> str:
    """本地 0123355873 → 国际 60123355873"""
    d = re.sub(r"\D", "", raw)
    if d.startswith("60"):
        return d
    if d.startswith("0"):
        return "60" + d[1:]
    return "60" + d


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def tokens(s: str):
    return [t for t in re.split(r"[^A-Za-z0-9]+", (s or "").lower()) if t]


# 称谓/头衔词：不参与姓名比对。
# Truecaller 常带前缀（`MR ENG JING HAO`），DB1 常不带（`Eng Jing Hao`），
# 不剥离会把"实质全中"误判成"缺一个 token"。
# ⚠️ 不要往里加 `tan`（也是姓"陈"）、`lim`、`ng` 这类**同时是姓氏**的词。
TITLES = {
    "mr", "mrs", "ms", "miss", "dr", "dato", "datin", "puan", "encik", "cik",
    "hj", "hajjah", "haji", "sri",
}


def strip_titles(ts):
    """剥掉称谓词；若剥完为空（名字本身就是称谓）则原样返回。"""
    out = [t for t in ts if t not in TITLES]
    return out or ts


def lev(a: str, b: str) -> int:
    """Levenshtein 距离"""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def fuzzy_eq(a: str, b: str) -> bool:
    """token 近似相等：允许编辑距离 ≤1（≥3 字母），或短 token 的前缀一致。

    放宽到 3 字母是必要的：华语姓名的罗马化拼写常有变体
    （Loh/Low、Tan/Tang、Lim/Lim），3 字母姓氏漏判会严重低估命中率。
    """
    if a == b:
        return True
    if min(len(a), len(b)) >= 3 and lev(a, b) <= 1:
        return True
    return False


def pinyin_of_cjk(s: str):
    """把字符串里的中文字符转拼音。返回 (拼接串, 逐字列表)。

    DB1 库里存中文备注（如 `智辉`），而 Truecaller 存罗马拼音（`CHEE HUI`）。
    跨语言匹配必须过拼音，否则会把实质命中判为不匹配。
    """
    chars = re.findall(r"[\u4e00-\u9fff]", s or "")
    if not chars:
        return "", []
    try:
        from pypinyin import lazy_pinyin
    except ImportError:
        return "", []
    per = lazy_pinyin(chars)
    return "".join(per), list(per)


def extract_json(text: str):
    marker = "DataBase 1 Information:"
    m = text.find(marker)
    if m < 0:
        return None
    rest = text[m + len(marker):]
    i = rest.find("{")
    if i < 0:
        return None
    try:
        obj, _ = json.JSONDecoder().raw_decode(rest[i:])
        return obj
    except Exception:
        return None


def query(mod, intl: str):
    cid = mod.CallerID()
    buf = io.StringIO()
    err = None
    try:
        with contextlib.redirect_stdout(buf):
            cid.start_callerid_check(intl, True)
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
    return extract_json(buf.getvalue()), err


def analyze(got: str, expect: str) -> dict:
    raw_got = (got or "").strip()
    n_got, n_exp = norm(got), norm(expect)
    tg, te = strip_titles(tokens(got)), strip_titles(tokens(expect))
    py_full, py_chars = pinyin_of_cjk(got)
    hits, py_hits = [], []
    for t in te:
        if any(fuzzy_eq(t, g) for g in tg):
            hits.append(t)
        elif py_full and (t in py_full or any(fuzzy_eq(t, c) for c in py_chars)):
            hits.append(t)
            py_hits.append(t)
    return {
        "exact": bool(n_got) and n_got == n_exp,
        "substring": bool(n_got) and bool(n_exp) and (n_got in n_exp or n_exp in n_got),
        "token_hits": hits,
        "token_ratio": round(len(hits) / len(te), 3) if te else 0.0,
        # has_data 必须看原始串：norm() 会抹掉中文，`智辉` 的 norm 是空串，会被误判为"无数据"
        "has_data": bool(raw_got),
        "cjk": "".join(re.findall(r"[\u4e00-\u9fff]", raw_got)),
        "pinyin": py_full,
        "pinyin_hits": py_hits,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="CallerID DB1 批量准确率验证")
    ap.add_argument("pairs", nargs="+", help="本地号码|已知名字")
    ap.add_argument("--repo", default=os.environ.get("PNL_REPO", "."))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--recheck", action="store_true", help="每个号码查两次，验证可复现性")
    args = ap.parse_args()

    mod = load_repo(args.repo)
    rows = []
    for p in args.pairs:
        raw, _, expect = p.partition("|")
        raw, expect = raw.strip(), expect.strip()
        intl = local_to_intl(raw)
        obj, err = query(mod, intl)
        got = (obj or {}).get("name", "") if obj else ""
        a = analyze(got, expect)
        row = {
            "local": raw, "intl": intl, "expect": expect, "got": got,
            "area": (obj or {}).get("belong_area", ""),
            "type_label": (obj or {}).get("type_label", ""),
            "report_count": (obj or {}).get("report_count", ""),
            "address": (obj or {}).get("address", ""),
            "old_tel": (obj or {}).get("old_tel_number", ""),
            "error": err, "decoded_ok": obj is not None,
            **a,
        }
        if args.recheck:
            obj2, _ = query(mod, intl)
            row["got2"] = (obj2 or {}).get("name", "") if obj2 else ""
            row["reproducible"] = (row["got2"] == got)
        rows.append(row)

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0

    print("=" * 108)
    print("CallerID (DataBase 1 / aunumber.com) 准确率验证")
    print("=" * 108)
    print(f"{'号码':<12}{'库返回 name':<24}{'已知名字':<22}{'全串':<5}{'子串':<5}{'token命中':<22}举报")
    print("-" * 108)
    for r in rows:
        th = ",".join(r["token_hits"]) or "-"
        if r.get("pinyin_hits"):
            th += " +拼音"
        print(f"{r['local']:<12}{r['got'][:23]:<24}{r['expect'][:21]:<22}"
              f"{'Y' if r['exact'] else '-':<5}{'Y' if r['substring'] else '-':<5}{th[:21]:<22}{r['report_count']}")
    print("-" * 108)
    n = len(rows)
    cjk_rows = [r for r in rows if r.get("cjk")]
    if cjk_rows:
        print("含中文备注: " + ", ".join(f"{r['local']}→{r['cjk']}(拼音 {r['pinyin']})" for r in cjk_rows))
    print(f"有返回 {sum(1 for r in rows if r['has_data'])}/{n}   "
          f"全串精确 {sum(1 for r in rows if r['exact'])}/{n}   "
          f"子串包含 {sum(1 for r in rows if r['substring'])}/{n}   "
          f"token 命中 ≥1 个 {sum(1 for r in rows if r['token_hits'])}/{n}   "
          f"token 全中 {sum(1 for r in rows if r['token_ratio'] == 1.0)}/{n}")
    if args.recheck:
        print(f"重查可复现 {sum(1 for r in rows if r.get('reproducible'))}/{n}")
        for r in rows:
            if not r.get("reproducible"):
                print(f"  ~ {r['local']}: 第一次 {r['got']!r} / 第二次 {r.get('got2')!r}")
    for r in rows:
        if r["error"]:
            print(f"  ! {r['local']} 出错: {r['error']}")
        elif not r["decoded_ok"]:
            print(f"  ! {r['local']} 接口未解密出 JSON")
    return 0


if __name__ == "__main__":
    sys.exit(main())
