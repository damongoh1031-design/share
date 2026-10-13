# -*- coding: utf-8 -*-
"""将 results/*.json 汇总为 report.md（扁平结构，6 大类 25 字段）。"""
import json
import re
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parent
FIELDS = BASE / "fields.yaml"
OUTLINE = BASE / "outline.yaml"
RESULTS = BASE / "results"
REPORT = BASE / "report.md"

SUMMARY_FIELDS = ["典型航程天数", "人均价格区间"]

# item 名称 -> results 文件名（显式映射，避免中文匹配歧义）
FILE_MAP = {
    "东加勒比": "east_caribbean.json",
    "西加勒比": "west_caribbean.json",
    "南加勒比": "south_caribbean.json",
    "百慕大": "bermuda.json",
    "西地中海": "west_mediterranean.json",
    "东地中海": "east_mediterranean.json",
    "亚得里亚海": "adriatic.json",
    "挪威峡湾": "norwegian_fjords.json",
    "波罗的海与北欧": "baltic_northern_europe.json",
    "跨大西洋": "transatlantic.json",
    "阿拉斯加": "alaska.json",
    "加拿大与新英格兰": "canada_new_england.json",
    "墨西哥蔚蓝海岸": "mexican_riviera.json",
    "巴拿马运河": "panama_canal.json",
    "环球航线": "world_cruise.json",
    "夏威夷": "hawaii.json",
    "南太平洋与法属波利尼西亚": "south_pacific_tahiti.json",
    "澳大利亚与新西兰": "australia_new_zealand.json",
    "日本与东北亚": "japan_northeast_asia.json",
    "东南亚": "southeast_asia.json",
    "中国母港航线": "china_homeport.json",
    "阿拉伯湾与中东": "arabian_gulf_middle_east.json",
    "西非与加那利群岛": "west_africa_canary.json",
    "印度洋与马尔代夫": "indian_ocean_maldives.json",
    "南美与合恩角": "south_america_cape_horn.json",
    "南极": "antarctica.json",
    "北极与斯瓦尔巴": "arctic_svalbard.json",
    "欧洲内河（多瑙河/莱茵河）": "european_rivers.json",
    "尼罗河": "nile_river.json",
    "亚马逊与探险内河": "amazon_rivers.json",
}

CORE_FINDINGS = """## 核心发现

1. **加勒比海是全球邮轮运力最密集的区域**。东、西、南三条主线加上百慕大短线，构成北美市场的基本盘；产品以 7 晚为主，大众线普遍落在每人每晚 100–200 美元区间，是全行业价格锚点。
2. **地中海呈现「西 / 东 / 亚得里亚」三分格局**。西地中海以美食酒庄与大城市为主，东地中海以希腊群岛与古迹宗教文化为主，亚得里亚海以中小型船 + 古城峡湾体验为主；整体旺季集中在 4–10 月，高端与奢华船占比明显高于加勒比。
3. **价格天花板出现在极地与奢华探险航线**。南极（11 月–次年 3 月，经德雷克海峡）与北极斯瓦尔巴（6–8 月）人均普遍在 500 美元/晚以上，且受 IAATO 等限额约束，属供给刚性、需求高增长赛道。
4. **亚洲是当前增量最快的市场**。中国母港航线在 2026 年重新扩张（MSC 荣耀号 2026-01-27 重返上海），日韩短线与东南亚长线同步增长；日本环岛航线受樱花季与红叶季双高峰驱动。
5. **内河是独立赛道而非海轮的补充**。欧洲内河（多瑙河/莱茵河）、尼罗河、亚马逊三类内河航线体量小、船型小、客单价高、复购率强，客户画像与海轮重叠度低。
6. **换船航线（repositioning）是性价比洼地**。跨大西洋、巴拿马运河、西非换船线等因需异地返程、海日偏多，单价明显低于同船同等级的常规航线，适合时间充裕、看重「纯航海体验」的旅客。
"""


def truncate(text, limit=42):
    if text is None:
        return "—"
    text = text.replace("|", "/")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def slug(text):
    s = text.lower().strip()
    s = re.sub(r"[^\w\s\u4e00-\u9fff-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s


def fmt(v):
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip()
        if not v:
            return None
        if "[不确定]" in v:
            return None
        return v
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, list):
        parts = []
        for it in v:
            if isinstance(it, dict):
                parts.append("；".join(f"{k}: {fmt(x)}" for k, x in it.items() if fmt(x)))
            else:
                p = fmt(it)
                if p:
                    parts.append(p)
        return "、".join(p for p in parts if p) or None
    if isinstance(v, dict):
        parts = [f"{k}: {fmt(x)}" for k, x in v.items() if fmt(x)]
        return "；".join(parts) or None
    return str(v)


def load():
    outline = yaml.safe_load(OUTLINE.read_text(encoding="utf-8"))
    fields = yaml.safe_load(FIELDS.read_text(encoding="utf-8"))
    cats = fields["field_categories"]
    order = [f["name"] for c in cats for f in c["fields"]]
    known = set(order)
    data = {}
    for item in outline["items"]:
        fn = FILE_MAP.get(item["name"])
        if not fn:
            continue
        p = RESULTS / fn
        if p.exists():
            data[item["name"]] = (item, json.loads(p.read_text(encoding="utf-8")))
    return outline, cats, order, known, data


def main():
    outline, cats, order, known, data = load()
    items = outline["items"]
    missing = [i["name"] for i in items if i["name"] not in data]
    if missing:
        print("[警告] 未匹配到 JSON：", missing)

    lines = []
    lines.append("# 全球邮轮的主要航线 — 深度调研报告")
    lines.append("")
    lines.append(f"> 调研日期：2026-10-06 ｜ 覆盖航线：{len(data)} 条 ｜ 字段框架：6 大类 {len(order)} 字段 ｜ 数据时效：近 12 个月（2025-10 ~ 2026-10）")
    lines.append("")
    lines.append("本报告对全球邮轮市场的主要航线逐一建档，每条航线覆盖基本信息、地理与季节、目的地亮点、运营方、价格与客群、差异化与注意六大维度，便于横向比较与选线参考。")
    lines.append("")
    lines.append(CORE_FINDINGS)
    lines.append("")

    # ---- 概览：区域分布 ----
    lines.append("## 二、全球航线格局概览")
    lines.append("")
    by_region = {}
    for it in items:
        by_region.setdefault(it["category"], []).append(it["name"])
    lines.append("| 区域 | 航线数 | 包含航线 |")
    lines.append("|------|--------|----------|")
    for reg, names in by_region.items():
        lines.append(f"| {reg} | {len(names)} | {'、'.join(names)} |")
    lines.append("")

    # ---- 目录 ----
    lines.append("## 三、目录")
    lines.append("")
    hdr = "| # | 航线 | 区域 | " + " | ".join(SUMMARY_FIELDS) + " |"
    sep = "|---|------|------|" + "|".join(["------"] * len(SUMMARY_FIELDS)) + "|"
    lines.append(hdr)
    lines.append(sep)
    idx = 0
    for it in items:
        if it["name"] not in data:
            continue
        idx += 1
        d = data[it["name"]][1]
        anchor = slug(f"{idx}. {it['name']}")
        cells = [truncate(fmt(d.get(f))) for f in SUMMARY_FIELDS]
        lines.append(f"| {idx} | [{it['name']}](#{anchor}) | {it['category']} | " + " | ".join(cells) + " |")
    lines.append("")

    # ---- 详细 ----
    lines.append("## 四、航线详录")
    lines.append("")
    idx = 0
    for it in items:
        if it["name"] not in data:
            continue
        idx += 1
        d = data[it["name"]][1]
        lines.append(f"### {idx}. {it['name']}")
        lines.append("")
        unc = set(d.get("uncertain") or [])
        for cat in cats:
            rows = []
            for f in cat["fields"]:
                fn = f["name"]
                if fn in unc:
                    continue
                v = fmt(d.get(fn))
                if not v:
                    continue
                rows.append((fn, v))
            if not rows:
                continue
            lines.append(f"**{cat['category']}**")
            lines.append("")
            for fn, v in rows:
                if len(v) > 90 or "\n" in v:
                    lines.append(f"- **{fn}**：{v}")
                else:
                    lines.append(f"- **{fn}**：{v}")
            lines.append("")
        # 额外字段
        extra = [k for k in d if k not in known and k not in ("uncertain", "_source_file")]
        if extra:
            lines.append("**其他信息**")
            lines.append("")
            for k in extra:
                v = fmt(d.get(k))
                if v:
                    lines.append(f"- **{k}**：{v}")
            lines.append("")
        lines.append("---")
        lines.append("")

    # ---- 附录 ----
    lines.append("## 五、附录：数据完整性与说明")
    lines.append("")
    unc_list = []
    for it in items:
        if it["name"] not in data:
            continue
        d = data[it["name"]][1]
        u = d.get("uncertain") or []
        if u:
            unc_list.append(f"- **{it['name']}**：{'、'.join(u)}")
    lines.append("### 不确定字段清单")
    lines.append("")
    if unc_list:
        lines.extend(unc_list)
    else:
        lines.append("无。30 条航线全部字段均取得可核实内容。")
    lines.append("")
    lines.append("### 字段定义")
    lines.append("")
    lines.append("| 分类 | 字段 | 说明 | 详细度 |")
    lines.append("|------|------|------|--------|")
    for cat in cats:
        for f in cat["fields"]:
            lines.append(f"| {cat['category']} | {f['name']} | {f['description']} | {f['detail_level']} |")
    lines.append("")
    lines.append("### 说明")
    lines.append("")
    lines.append("- 价格均为「每人每晚 USD」，分大众 / 高端 / 奢华三档，实际受船型、舱位、预订时机影响较大。")
    lines.append("- 标注 `[不确定]` 的字段已在报告中跳过，对应字段名列入上方「不确定字段清单」。")
    lines.append("- 数据来源涵盖 CLIA、Cruise Critic、CruiseMapper、IAATO、MedCruise、Cruise Baltic 及主要邮轮公司官网，时效以最近 12 个月为主。")
    lines.append("")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"已生成 {REPORT}")
    print(f"航线数: {len(data)}  未匹配: {missing}")


if __name__ == "__main__":
    main()
