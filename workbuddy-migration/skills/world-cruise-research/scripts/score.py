#!/usr/bin/env python3
"""环球邮轮六维加权评分计算器。

用法示例：
    # 单船快速计算
    python score.py --name "Seabourn Quest 2027" --scores "4.5,4.0,4.0,3.0,4.0,5.0"

    # 自定义权重（WiFi, 舱房, 美食, 节目, 观景, 便利）
    python score.py --name "X" --scores "5,5,5,5,5,5" --weights "30,20,20,15,10,5"

    # 批量：CSV 表头 name,wifi,cabin,dining,show,view,conv,home_stop
    python score.py --file ships.csv

    # 每人每晚单价
    python score.py --ppn 76199 --nights 180 --rate 4.09

home_stop 字段：yes / partial / no / unknown —— 用于「停靠母国」前置过滤。
"""

import argparse
import csv
import math
import sys

DIM_NAMES = ["WiFi", "舱房", "美食", "节目", "观景", "便利"]
DEFAULT_WEIGHTS = [15, 20, 20, 20, 15, 10]

HOME_STOP_LABEL = {
    "yes": "有停靠",
    "partial": "部分停靠",
    "no": "零停靠",
    "unknown": "未核实",
}


def parse_floats(text):
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def weighted_total(scores, weights):
    if len(scores) != 6:
        raise ValueError("需要恰好 6 个维度分数，收到 %d 个" % len(scores))
    if len(weights) != 6:
        raise ValueError("需要恰好 6 个权重，收到 %d 个" % len(weights))
    total_weight = sum(weights)
    if total_weight <= 0:
        raise ValueError("权重之和必须大于 0")
    raw = sum(s * w for s, w in zip(scores, weights)) / total_weight
    # 四舍五入（half-up），避免 Python 默认的 banker's rounding 把 4.125 变成 4.12
    return math.floor(raw * 100 + 0.5) / 100


def fmt_row(name, scores, weights, home_stop=None):
    total = weighted_total(scores, weights)
    dims = " | ".join("%s %.1f" % (n, s) for n, s in zip(DIM_NAMES, scores))
    stop = ""
    if home_stop:
        stop = " | 母国停靠: %s" % HOME_STOP_LABEL.get(home_stop, home_stop)
    return "%s | %s | 加权总分 %s%s" % (name, dims, total, stop)


def cmd_single(args):
    weights = parse_floats(args.weights) if args.weights else DEFAULT_WEIGHTS
    scores = parse_floats(args.scores)
    print(fmt_row(args.name or "未命名", scores, weights, args.home_stop))
    total = weighted_total(scores, weights)
    if args.home_stop == "no":
        print("\n!! 前置过滤未通过：该航线零停靠客户母国/邻国。")
        print("   按方法论第 7 条，应先出局，分数仅供参考。")
    return 0


def cmd_file(args):
    weights = parse_floats(args.weights) if args.weights else DEFAULT_WEIGHTS
    rows = []
    with open(args.file, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            name = (row.get("name") or "").strip()
            if not name:
                continue
            scores = [
                float(row["wifi"]),
                float(row["cabin"]),
                float(row["dining"]),
                float(row["show"]),
                float(row["view"]),
                float(row["conv"]),
            ]
            home_stop = (row.get("home_stop") or "unknown").strip().lower()
            rows.append((name, scores, home_stop))

    if not rows:
        print("CSV 中没有有效数据行。", file=sys.stderr)
        return 1

    ranked = sorted(rows, key=lambda r: weighted_total(r[1], weights), reverse=True)

    header = "%-42s %6s %6s %6s %6s %6s %6s   %7s  %s" % (
        "船 / 航线", "WiFi", "舱房", "美食", "节目", "观景", "便利", "总分", "母国停靠"
    )
    print(header)
    print("-" * len(header))

    rank = 0
    prev_total = None
    for idx, (name, scores, home_stop) in enumerate(ranked, start=1):
        total = weighted_total(scores, weights)
        if total != prev_total:
            rank = idx
            prev_total = total
        cells = " ".join("%6.1f" % s for s in scores)
        print("%-42s %s   %7.2f  %s" % (
            name[:42], cells, total, HOME_STOP_LABEL.get(home_stop, home_stop)
        ))
        if home_stop == "no":
            print("%-42s   ^^ 零停靠母国 —— 按前置过滤应先出局" % "")

    print("\n权重：%s（合计 %s）" % (weights, sum(weights)))
    print("提示：第一梯队内差距 <=0.03 视为无统计意义，需用「破平局表」而非分数决定。")
    return 0


def cmd_ppn(args):
    per_person = args.ppn / args.nights
    two_person = args.ppn * 2
    print("每人每晚：USD %.0f  ≈ MYR %.0f" % (per_person, per_person * args.rate))
    print("2 人合计（全程）：USD %s  ≈ MYR %s" % (
        f"{two_person:,.0f}", f"{two_person * args.rate:,.0f}"
    ))
    print("\n提醒：这是「名义单价」。比价前须扣掉票价已含的礼包")
    print("      （机票 / 酒店 / 专车 / 行李递送 / 船上消费金 / 洗衣 / 流媒体 WiFi）。")
    return 0


def main():
    parser = argparse.ArgumentParser(description="环球邮轮六维加权评分计算器")
    parser.add_argument("--name", default="未命名", help="船名 / 航线")
    parser.add_argument("--scores", help="6 个分数，逗号分隔：WiFi,舱房,美食,节目,观景,便利")
    parser.add_argument("--weights", help="6 个权重，逗号分隔（默认 15,20,20,20,15,10）")
    parser.add_argument("--file", help="CSV 文件，表头 name,wifi,cabin,dining,show,view,conv,home_stop")
    parser.add_argument("--home-stop", dest="home_stop",
                        choices=["yes", "partial", "no", "unknown"],
                        help="是否停靠客户母国/邻国")
    parser.add_argument("--ppn", type=float, help="每人起价（USD），用于算每人每晚")
    parser.add_argument("--nights", type=float, help="总晚数")
    parser.add_argument("--rate", type=float, default=4.09, help="USD->MYR 汇率，默认 4.09")
    args = parser.parse_args()

    if args.file:
        return cmd_file(args)
    if args.scores:
        # 修复（2026-10-07）：原逻辑先判 --ppn 并 return，导致
        # 「--scores + --ppn」同时给出时只打印价格、静默跳过评分。
        rc = cmd_single(args)
        if args.ppn:
            if not args.nights:
                parser.error("--ppn 需要同时提供 --nights")
            print()
            cmd_ppn(args)
        return rc
    if args.ppn:
        if not args.nights:
            parser.error("--ppn 需要同时提供 --nights")
        return cmd_ppn(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
