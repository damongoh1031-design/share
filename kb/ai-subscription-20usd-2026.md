---
id: ai-subscription-20usd-2026
title: "20美元档 AI 订阅横评：2026-10 纠错与复核事实库"
tags: [ai-subscription, chatgpt-plus, claude-pro, gemini, grok, sora, hermes-agent]
created: 2026-10-15
updated: 2026-10-15
version: 3
status: stable
source: "本次会话实测（重新联网检索：智源社区/新智元、IT之家、DoNews、知乎、什么值得买、CSDN、百家号、百度百科）"
confidence: "已核实"
---

## 一句话结论

初版横评报告两处硬伤已修：**Sora 已于 2026-04-26 关停（API 2026-09-24 关闭）**；**Hermes Agent v0.14 的 `hermes proxy` 可把 ChatGPT/Claude/SuperGrok 订阅转成本地 OpenAI 兼容 API（ChatGPT 侧走 Codex OAuth 设备登录），Codex CLI、Aider 等均可驱动**——低价订阅喂第三方客户端并非只有 Grok 一条路。其余价格/档位事实（ChatGPT Go $8、Opus 5.5、Gemini 10-09 新政、X Subscription Plus $8、Perplexity Pro）均于 2026-10-15 二次核实通过。

## 关键事实（均 2026-10-15 复核）

| 事实 | 内容 | 口径/日期 | 信源 |
|---|---|---|---|
| Sora 关停 | 2026-03-24 OpenAI 宣布关停；04-26 App/网页端下线；09-24 API 彻底关闭 | 累计烧掉约 54 亿美元；连带迪士尼 10 亿美元合作告吹 | 知乎、腾讯云社区、百家号（The Information） |
| Sora 后续 | 2026-10-13 The Information：OpenAI 正谈判把 Sora 交给梦工厂联合创始人 Katzenberg 等接手的初创公司 | 以专业影视工具形式卖回电影圈 | 百家号 |
| Hermes proxy | v0.14（2026-05）一行命令将 ChatGPT Pro / Claude Pro / SuperGrok 订阅变成本地 OpenAI 兼容 API 端点，推理穿透 OAuth 走订阅额度 | 官方/社区示例驱动 Codex CLI、Aider | 智源社区（新智元）、知乎专栏 |
| ChatGPT 侧通道 | 经 **Codex OAuth 设备登录**（需在 ChatGPT 网页设置开启"设备登录"开关） | 端点为标准 OpenAI 兼容格式，支持自定义 base_url 的客户端（Cline、opencode 等）理论上均可接入 | 同上 |
| Grok 侧官方背书 | SuperGrok OAuth → Grok 4.3 全栈（文本/语音/图像/视频/转录），上下文拉满 100 万 token，默认跨请求 prompt 缓存；官方接入指南 x.ai/news/grok-hermes | OpenClaw 5.18 亦修复 Grok OAuth PKCE（373k star） | 智源社区 |
| Anthropic 反制 | 一名 Claude Max $200 用户仅因目录残留 hermes.md 触发第三方调用风控，被倒扣 $200.98 API 账单 | "宁可错杀"式风控 | 智源社区 |
| ChatGPT 档位 | Free $0 / Go $8（2026-01-16/17 全球推出，部分地区含广告）/ Plus $20 / Pro $100·$200 / Business $30 每人 | Pro $100 为 2026-04 新增 | CSDN、什么值得买、百度百科 |
| Claude 模型 | Opus 5.5（2026-09-22 发布）AA 智能指数 **58 居全球第一**；Sonnet 5.5 56（210 tok/s）；Haiku 5.5（10-07 解禁）AA 43、382.8 tok/s | Meta Muse Wonder Full 56 落后 Opus 5.5 两分 | CSDN、百家号、百度百科 |
| Gemini 10-09 新政 | 免费版仅 Flash-Lite；AI Plus $4.99 失去 Pro；**AI Pro $19.99 首次获 Deep Think**（原 Ultra 独占） | 2026-10-09 生效 | 百家号、CSDN、什么值得买 |
| Gemini 4 Argon | 2026-09-30 发布，输出上限 100 万 token（一说 1.1M），初期仅 Fairwind 安全伙伴，后扩大开放 | 长上下文 GraphWalks 84.2% | 百家号、百度百科 |
| X Subscription | SpaceXSI 于 2026-10-13 推出：Plus $8 / Premium $30 / Super $100 / Ultra $200 | Plus 含 Grok Chat/Voice/Imagine/X Premium/Build + **Grok API 使用权限** + Cursor | IT之家、DoNews、IT时代网 |
| Perplexity Pro | $20/月 = 600 次 Pro Search + 20 次 Deep Research；Max $200 含 Computer 智能体 | 教育 Pro $10 | 百家号 |

## 可复用操作

```bash
# 报告再生成（results/*.json 为唯一事实源，改 JSON 后必须重跑，否则 report.md/html 是旧版）
cd ai-sub-20usd-2026
python generate_report.py && python generate_html.py

# Hermes Agent 安装（订阅转 API 前提）
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
pip install hermes-agent          # PyPI 直接装

# Hermes 选模型/登录（Grok 示例）
hermes model                      # 选 xAI Grok OAuth（SuperGrok 订阅）
hermes --tui                      # 浏览器 OAuth 登录后开聊
```

ChatGPT 侧替代路径：在 ChatGPT 网页设置开启"设备登录" → Codex OAuth 设备登录 → `hermes proxy` 暴露本地 OpenAI 兼容端点 → Codex CLI / Aider 指向 `http://127.0.0.1:<port>`。

## 坑与反直觉

1. **报告与数据源不同步**：本项目 `results/*.json` 与 `generate_report.py` 已是 v2，但 `report.md`/`report.html` 停在新智元报道前的 v1——生成式流水线里"改了 JSON 忘了重跑"是静默错误，交付前必须 `grep` 关键词自检（Sora、Hermes、$8）。
2. **"唯一能喂第三方的只有 Grok"是错的**：Hermes proxy 让 ChatGPT/Claude 订阅也能转 API，正确表述是"Grok 是唯一官方背书、低风险的通道；ChatGPT/Claude 能用但属灰色、有封号与倒扣账单风险"。
3. **X Subscription 档位数信源不一**：IT时代网称"三档"，DoNews 称四档（8/30/100/200）；SmartHey/新浪称 Super/Ultra 定价未正式公布。引用时注明信源与日期。
4. **AA 智能指数已并入"非幻觉率"**（2026-08），GPT 系因幻觉率高得分被压低；跨厂商比分须区分旧/新口径。
5. **MRCR"大海捞针"高分多为固定针位**，第三方复核认为与真实文档检索差距大，长上下文结论勿只凭 MRCR。
6. **模型命名漂移**：2026-10 中旬新信源已出现 "GPT-6.1 Sol"（与 Muse Wonder 52 持平），而报告写作口径为 GPT-6 Sol/GPT-6 Astra，下次复核需确认 OpenAI 现行命名。

## 未核实 / 存疑

- X Subscription Super $100 / Ultra $200 的官方最终定价（部分信源称未正式公布）。
- "已购 Sora 额度可转用于 Codex"（单一信源，未见官方公告）。
- ChatGPT 网页"设备登录"开关的确切菜单位置与 Plus 档是否全量开放（智源社区示例以 Pro 为主）。
- "GPT-6 Sol" vs "GPT-6.1 Sol" 哪个是 2026-10 现行名称。
- Gemini 4 Argon 输出上限 100 万 vs 1.1M 的口径差异。
