---
id: cruise-research-methodology
title: 邮轮调研方法论 —— 六维评分模型 / 五路并行 / 可信度标注 / 黑名单
tags:
  - 邮轮
  - 方法论
  - 评分模型
  - 可信度
  - 单船深研
  - 内容农场
created: 2026-10-09
updated: 2026-10-13
version: 1.1
status: stable
source: 本次会话 8 轮邮轮调研沉淀（已在 ~/.workbuddy-ai/skills/world-cruise-research 固化为技能，本文件是工作区级摘要）
confidence: 已核实（经 15 艘船深研 + 1 次船队时效核查 + 1 次中文语言环境专项验证）
---

# 邮轮调研方法论

## 一句话结论（TL;DR）

**邮轮调研的可靠性不取决于查得多，而取决于三件事：用六维加权模型替代「感觉好」、用五路并行替代「一个人查」、用可信度标注替代「照抄二手资料」。**

> **权威源**：`~/.workbuddy-ai/skills/world-cruise-research/`（SKILL.md + references/{verified-facts,scoring-model,pitfalls}.md + assets/baseline-2026-10.csv + scripts/score.py）。本文件是工作区级摘要，**技能库为唯一权威**。

---

## 1. 六维加权评分模型

| # | 维度 | 权重 | 5 分的含义 | 关键判据 |
|---|---|---|---|---|
| ① | **WiFi / 流媒体** | **15%** | 环球航次免费赠无限 Premium，官方明确支持 streaming + 多设备 | ① 基础档能否流媒体 ② 目标航次有无免费升级 ③ 几台设备 ④ 是否 Starlink |
| ② | **舱房大小与性价比** | **20%** | 面积同级最大 **且** 每人每晚单价同级最低 | 面积口径（含阳台？）+ 是否套房 + 浴缸/衣橱 + **每人每晚** |
| ③ | **美食丰富度** | **20%** | 特色餐厅多、**全免费、无配额**、菜单轮换 | 餐厅**数量** + 免费范围 + **配额** + 近期口碑 |
| ④ | **船上节目** | **20%** | 每晚多场百老汇式驻船秀 + 顶级讲座 | 剧场座位数 + 制作秀数量与**频率** + 讲座规格 |
| ⑤ | **船上观景** | **15%** | 环绕甲板/全景观景厅 **且** 航线有 4+ 天命名风景巡航 | **硬件分 × 航线风景内容分** |
| ⑥ | **生活便利** | **10%** | 免费自助洗衣 + 酒水/小费已含 + 自由入座 + 无正装夜 + 无排队 | 洗衣 + 座次 + 着装 + 客流 + 航次礼包 |

### 第 ⑦ 条：停靠母国（前置过滤，不计权重）

**先过滤，再评分。** 若航次不停靠客户母国（对环球长航程而言，「母国停靠」意味着可中途上下船、探亲、处理事务），应先提示客户，而不是把它折成分数。

### 🚨 权重调整后冠军会变（必须主动给客户）

**同一个六维分数，换权重就会换冠军。** 例如 Coral Princess 观景 4.5 分是全场顶尖，但若把「节目」权重从 20% 降到 10%，Crystal Serenity 会反超。**必须给客户一张「若你把 X 排第一 → 结论是什么」的表。**

---

## 2. 五路并行调研法（单船深研标准流程）

| 路 | 负责范围 |
|---|---|
| **A** | 规格 / 舱房 / 设施 / 福利 |
| **B** | 餐饮 / 节目 / 票价 |
| **C** | 航线 / 海日 / 天气 / 停靠港 |
| **D** | 价格 / 口碑 / 公司财务 / 签证 |
| **E** | 船队时效核查 + 独特卖点三类拆分 |

每路 agent 的 prompt 必须：① 携带技能库已有基线 ② 明确要求「**核实 + 补漏 + 纠错**」而非「查一下」③ 直接点名内容农场黑名单。

### 标准流水线

```
① 建 {topic_slug}/ 目录
② 读技能库基线（verified-facts.md / scoring-model.md / baseline CSV）
③ AskUserQuestion 锁客户画像（国籍 / 关注维度 / 调研范围）
④ 5 路并行 agent（各自「核实 + 补漏 + 纠错」）
⑤ 交叉核实（任一路的结论必须能被另一路或官方源印证）
⑥ 撰写 22–24 章报告（开篇「关键修正」→ 速览 → 规格 → 卖点 → 价位 → 隐性成本 → 设施/舱房/福利 → 餐饮 → 节目 → 翻新史 → 航线 → 海日 → 风景巡航 → 天气 → 停靠港 → 运河风险 → 签证 → 口碑 → 公司稳定性 → 六维评分 → 数据冲突 → 行动建议 → 订舱前 5 件事）
⑦ md2html 渲染
⑧ 回改技能库（verified-facts / pitfalls / scoring-model / baseline CSV）
```

---

## 3. 独特卖点三类拆分（价值最高的是第三类）

| 类别 | 判定标准 | 例（Coral Princess） |
|---|---|---|
| ① **真首创** | 有**独立来源**用**现在时**证实「全球首艘 / 行业首个」 | EnviroEngine —— 邮轮业首个完全采用（*Maritime Reporter* 2003-02 原文） |
| ② **真差异化** | 非首创，但**确实与同级不同** | Princess 仅有的两艘可过巴拿马旧闸的船之一 |
| ③ **❌ 营销话术 / 被误传** | 二手资料广泛流传但**经核实为错/夸大/张冠李戴** | 「Princess 世界航程最长」（❌ 业界有 274 晚者）；「Coral 上有 Park19」（⚠️ 张冠李戴） |

> **第三类才是这份报告的核心价值** —— 客户自己查不到「哪个说法是错的」。

---

## 4. 可信度标注体系

| 标记 | 含义 |
|---|---|
| ✅ | 官方 / 多源已核实 |
| ⚠️ | 单一来源 / 存疑 |
| ❌ | 已证实为错误 |
| 🚨 | 高风险提示 / 重大冲突 |

**数据冲突处理原则**：**双方并列，不擅自取舍。** 把两个数字、两个来源、两个日期都写出来，让客户看到分歧本身。

---

## 5. 🚨 低质内容农场黑名单（不可作为唯一依据）

`cruisezoom`、`nauticalflock`、`cruisebooking`、`360Cruising`、`cruiseprodigy`、`travelvient`、`ticketing-info`、`specrizy`、`guidebookbali`、`cruises.to`、`oceaniacruisesale`、`cruiseping`、`cruiselobster`、`cruiselookup`

→ **一律标 ⚠️ 且不可作为唯一依据。** 每路 agent 的 prompt 里应**直接点名这份黑名单**。

---

## 6. 「公司风险」vs「品牌风险」分离原则

| | 定义 | 判据 | 例 |
|---|---|---|---|
| **公司风险** | 母公司偿付能力 | 信用评级 / 杠杆 / 到期债结构 | Crystal：S&P **B+**（投机级），破产重生品牌，旧债权人清偿 ≈30% |
| **品牌风险** | 船舶长期可用性 | 船龄 > 20 年 + 同公司有大额新船订单 + 该船未来部署未公布 + 同集团近期有跨品牌转移先例 | Coral Princess：2003 年造，Princess 订 3 艘 Voyager 级新船，**2028 年 5 月后部署未公布** |

**对客户的表述**：不要说「这船可能会被卖掉」（无依据的猜测），而要说「**同集团历史上确实做过跨品牌转移，该船未来部署未公布** —— 建议订舱时确认退改条款」。

⚠️ **论坛传闻不是信号，官方部署空缺才是信号**（Coral 2025-05「被出售」传闻已证伪）。

---

## 可复用操作

### 评分脚本

```bash
C:/Users/Admin/.workbuddy-ai/skills/world-cruise-research/scripts/score.py \
  --scores "4.0,3.5,4.5,4.0,4.5,4.5" --name "Crystal Serenity 2027 (139n WC)"
```

### 渲染 HTML（⚠️ 必须用装了 markdown 的 venv）

```bash
# ❌ 托管 python 3.13.12 未装 markdown
"C:/Users/Admin/.workbuddy-ai/binaries/python/envs/default/Scripts/python.exe" \
  md2html.py "报告.md" "报告.html"
```

### 校验 HTML 锚点

```python
import re, io
h = io.open('report.html', encoding='utf-8').read()
ids = set(re.findall(r'id="([^"]+)"', h))
bad = [x for x in set(re.findall(r'href="#([^"]+)"', h)) if x not in ids]
print(len(ids), len(bad))   # 期望 bad = 0
```

### 奢华邮轮「全含」的 8 项打勾清单

**船上餐饮 / 酒水 / 小费 / WiFi / 岸上游 / 机票 / 接送 / 洗衣** —— 官方没明说 included 的一律按「不含」处理。

---

## 坑与反直觉（跨船通则）

1. 🚨 **「两个 agent 给出一致数字」≠ 正确** —— 它们可能读的是**同一批滞后页面**。
2. 🚨 **价格类事实必须问三件事**：① 公告日期 ② 生效日期 ③ 我关心的航次出发日在生效日之前还是之后。
3. 🚨 **优先找「公告型来源」**（Cruise Hive / Cruise Critic News / Seatrade / 船公司致旅行社函），而不是「展示型来源」（官网产品页、代理站）。
4. 🚨 **官方数据也会错** —— Coral 官方 Fact Sheet 的客舱数（1,545）与载客量数学矛盾，实际约 1,000 间。
5. 🚨 **「World Cruise」不保证绕地球一圈** —— Crystal Serenity 2027 与 Seabourn Quest 2027 都不走巴拿马/苏伊士。**先查运河清单再下结论。**
6. 🚨 **同一航次官方可能有双口径晚数**（139 vs 140）—— 先假设「行程改版」而非「笔误」。
7. 🚨 **「全含」不含岸上游与机票** —— 行业最大误解。
8. ⚠️ **第三方舱房数不可信** —— 用「客数 ÷ 2」反推更可靠。
9. ⚠️ **品牌的旗舰卖点可能被安到姊妹船上** —— 核实要落到**具体船**。
10. ⚠️ **本技能库自身也会滞后** —— `verified-facts.md` 的价格条目**每 3 个月必须重查**，引用前先看核实日期。

---

## 未核实 / 存疑

| 项目 | 状态 |
|---|---|
| 六维权重的「客观正确性」 | ⚠️ 权重是**客户画像驱动**的主观设定，不是行业标准；已内置「权重调整表」应对 |
| 各维度的 5 分锚点在不同船级间是否可比 | ⚠️ 部分船级差异大（内河 vs 海轮），基线仅含海轮长航程 |
| 黑名单是否穷尽 | ⚠️ 为经验清单，会持续增补 |

---

## 交付物位置

- 权威源：`~/.workbuddy-ai/skills/world-cruise-research/`
- 已深研 15 艘船基线：`~/.workbuddy-ai/skills/world-cruise-research/assets/baseline-2026-10.csv`
- 坑清单（64 条）：`~/.workbuddy-ai/skills/world-cruise-research/references/pitfalls.md`
- 相关 KB：[coral-princess-2027-world-cruise.md](./coral-princess-2027-world-cruise.md)｜[crystal-serenity-2027-world-cruise.md](./crystal-serenity-2027-world-cruise.md)
