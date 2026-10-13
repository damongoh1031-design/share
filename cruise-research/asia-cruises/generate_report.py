# -*- coding: utf-8 -*-
"""将 results/*.json + notes/*.md 汇总为 report.md（亚洲中日韩长程邮轮）。"""
import json
import re
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parent
FIELDS = BASE / "fields.yaml"
RESULTS = BASE / "results"
NOTES = BASE / "notes"
REPORT = BASE / "report.md"

# 按档位分组的展示顺序
GROUPS = [
    ("短线 3–6 晚", [
        ("中国母港日韩短线", "china_homeport_short.json"),
        ("日本国内与离岛航线", "japan_domestic_islands.json"),
        ("韩国航线与韩国母港", "korea_homeport.json"),
        ("香港与台湾出发亚洲航线", "hongkong_taiwan.json"),
    ]),
    ("中长线 7–15 晚", [
        ("中日韩中长线", "china_japan_korea_mid.json"),
        ("环日本深度长线", "japan_circumnavigation.json"),
    ]),
    ("长线 16–29 晚", [
        ("东南亚长线", "southeast_asia_long.json"),
        ("亚洲探险邮轮长线", "asia_expedition.json"),
    ]),
    ("超长线 30 晚+", [
        ("亚洲区域大环线", "asia_grand_circle.json"),
        ("环球航线亚洲段", "world_cruise_asia_segment.json"),
        ("亚洲跨洋长线", "asia_transoceanic.json"),
    ]),
]

SUMMARY_FIELDS = ["典型天数与晚数", "人均每晚单价"]

CORE_FINDINGS = """## 一、核心发现

### 1. 中国母港 2026 年是「净缩量 + 结构升级」的一年

2025 年中国母港共 8 艘邮轮、约 **25,386 床位**；2026 年下半年**净减 3 艘、约 3,930 床位**——鼓浪屿号（30 年船龄触发政策红线，转手西班牙 Corazul）、招商维京伊敦号（2026-08 转营地中海）、蓝梦之歌号（转手俄罗斯远东）。外资仅剩 **MSC 地中海邮轮与皇家加勒比**留守，运力向少数十几万吨大船集中；国产邮轮（爱达三船）成为北方与华南主力。

### 2. 韩国端 2026 出现政策收紧，日韩格局反转

**韩国 C-3-2 团体旅游签证将不再适用于邮轮行程**（韩国移民局通告）。釜山、仁川、丽水自由行须改办个人签证（约 260 元、5–14 个工作日），**济州岛仍维持 30 天免签**。日本「船舶观光上陆许可」政策未变。结果是 2026 年下半年呈现**「日本线回归、韩国线承压」**的格局。

### 3. MSC 荣耀号重返上海，首创「上海—釜山」双母港

2026-01-27 MSC 荣耀号（MSC Bellissima，5,686 床位）回归上海，当日搭载近 4,000 名国际游客抵沪，并于同日载客前往济州与釜山。这是中国母港首次出现**双母港运营模式**——通过引入韩国入境客源，对冲中国出境需求疲软。

### 4. 日本邮轮免签有三个硬约束，容易踩坑

「船舶观光上陆许可」只适用于：①乘**法务大臣指定邮轮**；②**当日返船**；③**限指定港**（那霸、福冈、长崎、熊本、鹿儿岛、佐世保、小樽、函馆等）。**在日本登船/离船，或跨夜停靠，该许可即失效**，须持常规签证。另：护照上若已贴有效日本签证，免签自动失效。

### 5. 日本国内船队正在换代

「にっぽん丸」已于 **2026-05-10 引退**（服役 35 年），后继船 **MITSUI OCEAN SAKURA**（32,477 GT / 458 人）于 2026 年 9 月投入，从横滨、神户、名古屋出发，主打濑户内海与离岛。

### 6. 价格分档清晰，性价比洼地在两端

| 档位 | 每人每晚（参考） |
|---|---|
| 中国母港日韩短线（4–6 晚） | **300–650 元**（约 $42–90） |
| 东南亚线（3–17 晚） | 400–1,100 元 |
| 亚洲 30+ 晚长线 | 700–1,500 元 |
| 中日韩中长线（7–15 晚） | 800–1,800 元 |
| 亚洲奢华探险线 | **3,000–8,500 元** |

**最划算**：中国母港日韩短线（门槛最低）+ 公主/荷美 30+ 晚长线（约 746 元/晚，长途成本被摊薄）。
**溢价最高**：奢华探险线（3,000–8,500 元/晚）。
**比价提醒**：大众线报价**普遍不含小费（$16.5–21/人·晚）与岸上游（$45 起/项）**，必须用同人数、同舱型、同权益的结算总价比较，不要只看「每人起」。

### 7. 亚洲长线的真正入口是东南亚，不是日韩

中日韩受制于航线短、政策波动大；而**新加坡往返 14 晚内舱约 94–145 美元/人·晚**，且新马泰对中国护照互免签（新加坡 30 天、马来西亚 30 天、泰国 60 天），是亚洲长线入门首选。
"""


def demote(text):
    """把 notes 里的 # 标题降一级，便于嵌入报告。"""
    out = []
    for line in text.splitlines():
        if line.startswith("## "):
            out.append("#" + line)
        elif line.startswith("# "):
            out.append("#" + line)
        else:
            out.append(line)
    return "\n".join(out)


def fmt(v):
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip()
        if not v or "[不确定]" in v:
            return None
        return v
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, list):
        parts = []
        for it in v:
            if isinstance(it, dict):
                p = "；".join(f"{k}: {fmt(x)}" for k, x in it.items() if fmt(x))
                if p:
                    parts.append(p)
            else:
                p = fmt(it)
                if p:
                    parts.append(p)
        return "、".join(parts) or None
    if isinstance(v, dict):
        parts = [f"{k}: {fmt(x)}" for k, x in v.items() if fmt(x)]
        return "；".join(parts) or None
    return str(v)


def slug(text):
    s = re.sub(r"[^\w\s\u4e00-\u9fff-]", "", text.lower().strip())
    return re.sub(r"\s+", "-", s)


def truncate(text, limit=40):
    if not text:
        return "—"
    text = text.replace("|", "/")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def main():
    fields = yaml.safe_load(FIELDS.read_text(encoding="utf-8"))
    cats = fields["field_categories"]
    known = {f["name"] for c in cats for f in c["fields"]}

    data = {}
    for _, pairs in GROUPS:
        for name, fn in pairs:
            p = RESULTS / fn
            if p.exists():
                data[name] = json.loads(p.read_text(encoding="utf-8"))

    lines = []
    A = lines.append
    A("# 亚洲（中日韩）长程邮轮深度调研报告")
    A("")
    A("> 调研日期：2026-10-06 ｜ 覆盖 11 条航线 + 3 个专题 ｜ 口径：全谱系（4 晚短线 → 60 晚大环线）｜ 数据时效：近 12 个月 + 已公布的 2026–2028 船期")
    A("")
    A("本报告以**中日韩为核心**、覆盖亚洲全谱系邮轮产品，从**航线与船期、运营公司与船、价格与性价比、签证与政策**四个维度逐一建档，并附中国母港部署、签证政策、价格体系三个专题。")
    A("")
    A(CORE_FINDINGS)
    A("")

    # ---- 专题 ----
    topic_map = [
        ("二、专题一：中国母港 2026–2027 邮轮部署全清单", "china_homeport_deployment.md"),
        ("三、专题二：亚洲邮轮签证与政策总览", "asia_visa_policy.md"),
        ("四、专题三：亚洲邮轮价格体系与性价比对比", "asia_price_benchmark.md"),
    ]
    for title, fn in topic_map:
        p = NOTES / fn
        if p.exists():
            A(f"## {title}")
            A("")
            A(demote(p.read_text(encoding="utf-8")).strip())
            A("")

    # ---- 目录 ----
    A("## 五、航线总目录")
    A("")
    A("| # | 档位 | 航线 | " + " | ".join(SUMMARY_FIELDS) + " |")
    A("|---|------|------|" + "|".join(["------"] * len(SUMMARY_FIELDS)) + "|")
    idx = 0
    for group, pairs in GROUPS:
        for name, _ in pairs:
            if name not in data:
                continue
            idx += 1
            d = data[name]
            anchor = slug(f"{idx}. {name}")
            cells = [truncate(fmt(d.get(f))) for f in SUMMARY_FIELDS]
            A(f"| {idx} | {group} | [{name}](#{anchor}) | " + " | ".join(cells) + " |")
    A("")

    # ---- 详录 ----
    A("## 六、航线详录")
    A("")
    idx = 0
    for group, pairs in GROUPS:
        A(f"### 【{group}】")
        A("")
        for name, _ in pairs:
            if name not in data:
                continue
            idx += 1
            d = data[name]
            A(f"#### {idx}. {name}")
            A("")
            unc = set(d.get("uncertain") or [])
            for cat in cats:
                rows = []
                for f in cat["fields"]:
                    fn2 = f["name"]
                    if fn2 in unc:
                        continue
                    v = fmt(d.get(fn2))
                    if v:
                        rows.append((fn2, v))
                if not rows:
                    continue
                A(f"**{cat['category']}**")
                A("")
                for fn2, v in rows:
                    A(f"- **{fn2}**：{v}")
                A("")
            extra = [k for k in d if k not in known and k not in ("uncertain", "_source_file")]
            if extra:
                A("**其他信息**")
                A("")
                for k in extra:
                    v = fmt(d.get(k))
                    if v:
                        A(f"- **{k}**：{v}")
                A("")
            A("---")
            A("")

    # ---- 附录 ----
    A("## 七、附录")
    A("")
    A("### 不确定字段清单")
    A("")
    unc_rows = []
    for _, pairs in GROUPS:
        for name, _ in pairs:
            if name in data and (data[name].get("uncertain") or []):
                unc_rows.append(f"- **{name}**：{'、'.join(data[name]['uncertain'])}")
    A("\n".join(unc_rows) if unc_rows else "无。")
    A("")
    A("### 字段定义")
    A("")
    A("| 分类 | 字段 | 说明 | 详细度 |")
    A("|------|------|------|--------|")
    for cat in cats:
        for f in cat["fields"]:
            A(f"| {cat['category']} | {f['name']} | {f['description']} | {f['detail_level']} |")
    A("")
    A("### 说明")
    A("")
    A("- 价格为「每人起」，随航期、房型、供需浮动；币种与舱位类型已标注。")
    A("- 标注 `[不确定]` 的字段已在正文跳过，字段名列入上方清单。")
    A("- 数据来源涵盖邮轮公司官网、携程/同程邮轮、星美亚、去游轮、Cruise Critic、CruiseMapper、日本国土交通省、韩国移民局、中国驻釜山总领事馆等。")
    A("- 签证政策均有生效日期，请以官方最新公告为准；本报告区分「已生效」「拟议中」「已过期」。")
    A("")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"已生成 {REPORT}  航线数: {len(data)}")


if __name__ == "__main__":
    main()
