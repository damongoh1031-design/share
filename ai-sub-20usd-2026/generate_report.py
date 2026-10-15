# -*- coding: utf-8 -*-
"""读取 results/ 下全部调研 JSON，生成带目录与横向对比的 Markdown 报告。"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(BASE, "results")
OUT = os.path.join(BASE, "report.md")

ITEM_ORDER = [
    "OpenAI_ChatGPT_Plus.json",
    "Anthropic_Claude_Pro.json",
    "Google_Gemini_AI_Pro.json",
    "Grok_8usd_Tier.json",
    "Microsoft_Copilot_Pro.json",
    "Perplexity_Pro.json",
]

FIELD_LABELS = {
    "pricing": "价格与档位",
    "benefits": "福利权益",
    "limits": "额度限制",
    "top_models": "可用的最高模型",
    "third_party_clients": "第三方客户端 / 订阅通道支持",
    "builtin_tools": "内置工具与智能体",
    "model_intelligence": "模型智力（基准成绩）",
    "hallucination": "幻觉率对比",
    "context_hit": "长上下文命中",
    "world_knowledge": "世界知识",
    "writing": "文字与写作能力",
    "verdict": "总结定位",
}

FIELD_ORDER = ["pricing", "benefits", "limits", "top_models",
               "third_party_clients", "builtin_tools", "model_intelligence",
               "hallucination", "context_hit", "world_knowledge",
               "writing", "verdict"]

REPORT_HEADER = """# 20美元档 AI 订阅深度横评：ChatGPT Plus / Claude Pro / Gemini AI Pro / Grok $8 档

> 调研日期：2026年10月15日（v2 修订版：纠正“Sora 仍在订”错误、补充 Hermes Agent 对 Codex 订阅的支持、新增幻觉率与长上下文命中对比）｜ 数据来源：各官方定价页与帮助中心、Artificial Analysis、LMArena 周榜、IT之家、智源社区/新智元、知乎、什么值得买、CSDN、腾讯云等。价格与权益变动极快，请以官网实时信息为准。

## 执行摘要（TL;DR）

1. **ChatGPT Plus（$20）是大多数人的默认首选**：模型矩阵最全（聊天 GPT-6 Sol，Work/Codex 还能限用 GPT-6 Astra），Codex 编程、深度研究、Work 智能体全线覆盖，无广告。注意：**Sora 视频生成已于 2026-04-26 关停**（API 于 2026-09-24 停止），已购额度可转用于 Codex。
2. **Claude Pro（$20）是“最高智能 + 最低幻觉倾向 + 最强文字”的偏科生**：Claude Opus 5.5 是 2026年10月 Artificial Analysis 智能指数第一名（58），中文文学写作被公认为最细腻；但网页/编程额度偏紧（Opus 约45条/5小时，Claude Code 每周40–80小时 Sonnet）。
3. **Gemini AI Pro（$19.99）买的是生态、低幻觉与长上下文**：100万 tokens 上下文、Gemini 4 Argon、Deep Think、2TB 存储、Veo 视频、独门福利——**Antigravity 编程 IDE 里可以直接调用 Claude Opus 5.5**。**幻觉率仅15%（AA 口径，45分以上模型中最低）**、GraphWalks 长上下文命中 84.2% 第一。
4. **Grok 的“8美金”档已升级为捆绑订阅**：2026-10-13 起 $8/月的 X Subscription Plus = Grok（基础档）+ X Premium + **Grok API 额度** + Cursor。**第三方生态开放度四家第一**：xAI 官方支持 Hermes Agent（OAuth 直连、100万上下文）。最新旗舰 Grok 4.7 需 $30 档，顶级 Heavy 模型在 $300 档。Grok 独特价值是实时 X 数据，弱项是文字打磨与幻觉数据缺位。
5. **第三方客户端（Hermes Agent / OpenClaw）真相（v2 纠正）**：**Hermes Agent v0.14 的 `hermes proxy` 确实能把 ChatGPT（Codex OAuth 设备登录）、Claude Pro、SuperGrok 订阅一行命令转成本地 OpenAI 兼容 API 端点**，驱动 Aider、Codex CLI 等。但 Anthropic 反制锋利：有 Claude Max 用户因目录残留 hermes.md 被倒扣 $200.98 API 账单——可用但有风险。
6. 补充对照：**Copilot Pro（$20）**需叠加 M365 授权（实际 $30–40/月），只推荐 Office 重度用户；**Perplexity Pro（$20）**是带引用检索与研究专家（600次 Pro Search + 20次 Deep Research/月），适合做第二订阅而非主力助手。

## 一、横向对比总表（2026-10-15）

| 维度 | ChatGPT Plus $20 | Claude Pro $20 | Gemini AI Pro $19.99 | Grok $8 档 |
|---|---|---|---|---|
| 档位体系 | Free/Go $8/Plus $20/Pro $100/Pro $200 | Free/Pro $20/Max $100/Max $200 | 免费/AI Plus $4.99/AI Pro $19.99/AI Ultra $99.99–199.99 | X Subscription Plus $8/Premium $30/Super $100/Ultra $200；SuperGrok $30/Heavy $300 |
| 聊天最高模型 | GPT-6 Sol（中/高） | Claude Opus 5.5 | Gemini 4 Argon + Deep Think | Grok 基础档（最新4.7需$30档） |
| 顶级模型获取 | GPT-6 Pro(Astra) 锁 $100+；Plus 仅 Work/Codex 限用 | Opus 5.5 即当前全球智能第一 | Argon 第一梯队（AA 53） | Heavy 模型锁 $300 |
| 消息额度 | 滚动窗口，Sol 约10–100条/5h（社区观测） | Opus 约45条/5h；Sonnet 更高；独立配额池 | 算力计量：5h窗口+周上限，Pro=免费4倍 | 限额提升但非顶级；官方未固定公布 |
| 深度研究 | 有月度限制（账户内查询） | Research 功能可用 | Deep Research（耗算力高） | DeepSearch（$30档近无感） |
| 视频生成 | **无（Sora 2026-04-26 已关停）** | 无 | Veo 3/Flow 积分制（$25起充） | Imagine（SuperGrok 20倍、720p/30s） |
| 编程工具 | Codex + Work 智能体 | Claude Code（周40–80h Sonnet） | Antigravity（含 Claude 5.5！） | Grok Build + 捆绑 Cursor |
| 上下文 | 150万（5.6系）/Astra 输出128K | 200K 级 | 100万 | 128K（SuperGrok）；Hermes 接入 4.3 可达100万 |
| 幻觉率（AA） | GPT-6 Astra 51%（GPT系85–92%口径见正文） | Opus 4.7 36%（最低幻觉倾向） | **Argon 15%（≥45分模型中最低）** | 无权威数据 |
| 长上下文命中 | Astra 71.8%（GraphWalks） | 约65%（MRCR 迭代回退） | **84.2%（GraphWalks 第一）** | MRCR 数据缺失 |
| 捆绑权益 | 无广告、Projects、GPTs | Projects、Artifacts、MCP 连接器 | 2TB 存储、NotebookLM Plus、Workspace | X Premium 社交 + Grok API + Cursor |
| 第三方客户端 | △ Hermes proxy 可转（Codex OAuth，有风险） | △ Hermes proxy 可转，但有倒扣$200.98账单风控 | ✗（CLI 免费登录已关） | ✓ xAI 官方支持 Hermes + 自带 API |
| 广告 | 无 | 无 | 无 | $8 档基础 X 权益（去广告看档位） |

## 二、可用模型的最高智力对比（2026年10月）

| 模型（所属订阅可用的最高档） | Artificial Analysis 智能指数 | LMArena / 其他 | 备注 |
|---|---|---|---|
| Claude Opus 5.5（Claude Pro $20） | **58（第一）** | 周榜前四占其三位，opus-5.5-high ELO 1507 | 智能体榜 Opus 5.5 Max 72% 登顶 |
| Claude Sonnet 5.5（Claude/Google Antigravity） | 56 | — | 价格约旗舰60%，速度+30% |
| Meta Muse Wonder Full | 56 | — | 非订阅对照 |
| GPT-6 Astra（ChatGPT $100+/Google Antigravity） | 53 | — | GPT-6 Pro 底座 |
| Gemini 4 Argon（Gemini AI Pro $19.99） | 53 | 独立综合榜约第4 | DeepSWE v1.1 77.9% 第一；Vals Index 68.90% 登顶 |
| Grok 4.3（历史口径） | 53 | — | 2026-05 数据 |
| Grok 4.7（Grok $30 档） | 46（第二梯队第一） | 编码智能体指数 56 | DeepSWE 71.0%；实测有“跑分强落地翻车”样本 |

> 编程专项：Terminal-Bench 2.1 GPT-5.6 Sol 88.8%（Ultra 91.9%）> Claude Mythos 5 88.0%；Terminal-Bench 4.0 Opus 5.5 66.4% > Argon 57.4%；FrontierSWE v2 GPT-6 Astra 65.5% > Argon 55.0%。**结论：ChatGPT 系擅长端到端编程，Claude 系综合智能与智能体任务更强，Gemini 长上下文与低幻觉无敌，Grok 编码智能体进步快但仍差一档。**

## 二·补、幻觉率对比（越低越好）

| 模型 | AA-Omniscience 幻觉率 | 其他口径 |
|---|---|---|
| Gemini 4 Argon | **15%（≥45分模型中最低）** | 工具幻觉率 0.18%（LMArena 智能体周榜头部最低，2026-10-12） |
| Claude Opus 4.7 | 36% | Claude 系“非幻觉率”历来大幅领先 GPT 系 |
| GPT-6 Astra | 51% | GPT-5.5 高达 86%，GPT 全系 85–92% |
| Grok 4.7 | 无权威数据 [不确定] | 实时 X 数据可降低事实幻觉，引用规范性弱 |

学术引用实测（2026-06，50篇论文）：Perplexity Pro 幻觉率4%（96%引用真实）> Gemini Pro 16% > **ChatGPT Plus 24%（仅76%真实）**。
注意：AA-Omniscience 奖励“宁可拒答也不乱答”，对回答倾向积极的模型天然不严；引用类幻觉更贴近日常使用体感。

## 二·补2、长上下文命中对比（越高越好）

| 模型 | GraphWalks 256K–1M | MRCR v2 @1M（大海捞针） | 备注 |
|---|---|---|---|
| Gemini 4 Argon | **84.2%** | 前代3.0 Pro @28k 77.0%，1M衰减 | 100万统一输入输出 token |
| GPT-6 Astra | 71.8% | GPT-5.5 约74.x（5.4仅36.6%） | 5.6系标称150万上下文 |
| Claude Opus 5.5 | 约65% | Opus 4.6 78.3% → 4.7 32.2%（迭代回退） | 优势在理解/改写而非纯检索 |
| Grok 4.7 | 缺权威数据 [不确定] | 缺 | Hermes 接入 4.3 可达100万 token |

> 行业警示：MRCR“大海捞针”类测试被第三方复核批评——多数高分是在固定文档位置下取得，与真实“从文档堆里找答案”差距不小。长上下文请以实际文档测试为准。

## 三、世界知识对比

- **时效性之王：Grok**——实时 X 平台数据，追热点/舆情/突发新闻无对手。
- **带引用之王：Perplexity Pro**——每论断编号引用可验证；引用错误率两极（CJR 基准免费37%/Pro 45% 最差，但学术引用实测仅4%），且无跨会话 AI 记忆。
- **Gemini**——100万上下文 + 联网搜索，长文档/代码库知识工作最强，幻觉率与引用真实性（84%）均优于 ChatGPT（76%）。
- **ChatGPT / Claude**——联网搜索均支持；世界知识问答与引用真实性非其最强项。
- 各家知识截止时间均未获得官方逐项数据，[不确定]，建议以联网搜索 + Deep Research 实际体验为准。

## 四、文字与写作能力对比

| 场景 | 第一 | 第二 | 第三 |
|---|---|---|---|
| 中文文学/细腻文笔 | **Claude**（“文科生AI”，AI味最淡，心理描写与对话出色） | GPT-5.6 | Gemini |
| 英文学术/格式规范 | **GPT-5.6**（45.0分，APA 执行最准） | Claude 4.8 | Gemini 3.5 |
| 中文学术写作 | **GPT-5.6**（8.8） | Claude 4.8（8.5） | Gemini 3.5（8.2，中英差距最大） |
| 摘要与结论质量 | **Claude**（9.1，能准确提炼全文核心） | GPT-5.6 | Gemini |
| 信息型/数据型写作 | Grok（实时数据支撑） | GPT | Claude |

## 五、第三方客户端可用性（Hermes Agent / OpenClaw 专题，v2 修订）

- **Hermes 与 OpenClaw**是两款开源、可 Docker 自托管的 AI 智能体框架（NAS 即可部署，OpenClaw 已 37万+ star）：OpenClaw 主打网关/技能/本地记忆的“连接与控制”；Hermes 主打安全、配额记忆与 SOP 技能复用、Cron+沙箱无人值守，现已上 PyPI（`pip install hermes-agent`）。
- **重大纠正：Hermes Agent v0.14（2026-05）的 `hermes proxy` 可以把订阅“变”成 API**——本地拉起 HTTP 端口暴露 OpenAI 兼容 API，实际请求穿透 OAuth 授权走订阅额度：
  - **ChatGPT 订阅 → Codex**：经 Codex OAuth 设备登录（需在 ChatGPT 网页设置开启“设备登录”开关），$20 Plus 即可驱动 Codex CLI / Aider（用户指出的正确事实，初版报告遗漏）；
  - **Claude Pro 订阅**：同样可转本地 API 驱动 Aider / Claude Code；
  - **SuperGrok 订阅**：xAI 官方背书——Hermes OAuth 直连 Grok 4.3 全栈（文本/语音/图像/视频/转录），100万上下文 + 跨请求 prompt 缓存，官网有接入指南（x.ai/news/grok-hermes）；OpenClaw 5.18 也修复了 Grok OAuth PKCE 认证。
- **风险红线**：Anthropic 2026-04-04 起明令订阅额度不得被 OpenClaw 等第三方工具消耗；一名 Claude Max $200 用户仅因目录残留 hermes.md 文件触发风控，被倒扣 $200.98 API 账单。Hermes proxy 对 ChatGPT/Claude 属于“能用但随时可能被封/被计费”的灰色通道；**唯一低风险的是 xAI 官方支持的 Grok 通道与 $8 档自带的 Grok API 额度**。
- 各家官方 API 均可单独按量付费（OpenAI/Anthropic/Google/xAI），第三方客户端的正规姿势是自备 API key。

## 六、购买建议（按人群）

| 人群 | 推荐 | 理由 |
|---|---|---|
| 大多数个人用户 | **ChatGPT Plus $20** | 全能、生态最大、无短板（视频已无 Sora，需视频请用 Gemini/Grok） |
| 文字工作者/深度思考 | **Claude Pro $20** | 智能第一、幻觉倾向最低、中文文笔第一 |
| Google 生态/长文档/洁癖党 | **Gemini AI Pro $19.99** | 1M 上下文 + 幻觉率15% + Antigravity 送 Claude 旗舰 |
| 预算优先/爱折腾智能体 | **Grok $8 捆绑档** | 唯一含 API 且官方支持 Hermes 的低价订阅；要旗舰加钱到 $30 |
| 研究者/事实核查 | + **Perplexity Pro $20**（第二订阅） | 带引用检索独一档 |
| Office 重度办公 | Copilot Pro（仅在已有 M365 时考虑） | 与主力订阅重叠，勿叠加 |

---

"""

UNCERTAIN_NOTE = ""


def esc(s):
    return str(s)


def fmt_value(v, indent=0):
    if isinstance(v, list):
        if all(isinstance(x, (str, int, float)) for x in v):
            txt = "、".join(str(x) for x in v)
        else:
            txt = "\n" + "\n".join(
                "- " + "；".join(f"{k}: {vv}" for k, vv in d.items())
                for d in v)
        return txt
    if isinstance(v, dict):
        return "\n" + "\n".join(f"- **{k}**：{vv}" for k, vv in v.items())
    return str(v)


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main():
    items = []
    for fn in ITEM_ORDER:
        with open(os.path.join(RESULTS, fn), encoding="utf-8") as f:
            items.append(json.load(f))

    lines = [REPORT_HEADER]
    # 目录
    lines.append("## 目录\n")
    for i, it in enumerate(items, 1):
        name = it.get("name", fn)
        verdict = str(it.get("verdict", ""))
        short = verdict.split("；")[0].split("。")[0]
        lines.append(f"{i}. [{name}](#{slug(name)}) — {short}")
    lines.append("\n---\n")

    # 详情
    for i, it in enumerate(items, 1):
        name = it.get("name", f"Item {i}")
        lines.append(f"\n## {i}. {name}\n")
        uncertain = set(it.get("uncertain", []))
        skipped = []
        for key in FIELD_ORDER:
            if key not in it or key in uncertain:
                if key in it:
                    skipped.append(FIELD_LABELS.get(key, key))
                continue
            val = it[key]
            if val is None or str(val).strip() == "":
                continue
            if "[不确定]" in str(val):
                skipped.append(FIELD_LABELS.get(key, key))
                continue
            label = FIELD_LABELS.get(key, key)
            lines.append(f"### {label}\n")
            lines.append(f"{fmt_value(val)}\n")
        if skipped:
            lines.append(f"> 数据缺口（证据不足，未收录）：{'、'.join(skipped)}。\n")
        lines.append("")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("written:", OUT)


if __name__ == "__main__":
    main()
