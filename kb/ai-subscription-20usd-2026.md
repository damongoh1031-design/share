---
id: ai-subscription-20usd-2026
title: "20美元档 AI 订阅横评：v4 法律场景导向复核事实库（2026-10-15）"
tags: [ai-subscription, chatgpt-plus, claude-pro, gemini, grok, perplexity, legal-ai]
created: 2026-10-15
updated: 2026-10-15
version: 4
status: stable
source: "本次会话实测（41+ 次定向检索：OpenAI/微软官方帮助页、智源社区/新智元、IT之家、DoNews、虎嗅、什么值得买、百家号、搜狐、helicsnews、CSDN、知乎、澎湃、律协指引）"
confidence: "已核实"
---

## 一句话结论

v4 重写版完成：旧版四类错误已纠正（Sora 已关停、Copilot Pro 已停售、第三方不止 Grok、"Claude 幻觉最低"被推翻），报告重组为法律场景导向结构。法律用途选型结论：**长文档/低幻觉首选 Gemini AI Pro $19.99（Argon 幻觉率 15%、GraphWalks 84.2%、输入输出均 100 万 token）；文书精度选 Claude Pro（Opus 5.5 智能 58 第一，但最高推理幻觉率 59%，必须逐条核验）；律师对 AI 输出承担最终责任**。

## 一、2026-10-15 复核事实表（关键结论）

| 事实 | 内容 | 信源/日期 |
|---|---|---|
| Copilot Pro 停售 | 微软官方：不再开放新购，现有订阅支持至 2026-08-01；替代 Microsoft 365 Premium $19.99/月 | 微软官方支持页；什么值得买 2026-07-02 |
| Sora 关停 | 2026-03-24 宣布，04-26 App/网页下线，09-24 API 关闭；烧掉约 54 亿美元 | 知乎、腾讯云、百家号 2026-10 |
| Hermes proxy | v0.14（2026-05）把 ChatGPT（Codex OAuth 设备登录）/Claude Pro/SuperGrok 订阅转本地 OpenAI 兼容 API，驱动 Codex CLI、Aider；任何 OpenAI 兼容客户端理论可接 | 智源社区/新智元 2026-05-20 |
| Hermes 风险 | Claude Max $200 用户因目录残留 hermes.md 被倒扣 $200.98 API 账单 | 同上 |
| Opus 5.5 幻觉率 | AA-Omniscience 最高推理档 **59%**（旧版"Claude 幻觉最低"基于 Opus 4.7 36% 是 4 月口径，已推翻）；Argon 15% 最低、Astra 45–51%、Fable 5.1 73% | helicsnews 2026-10-11、搜狐 2026-10-14 |
| 智能指数 AA | Opus 5.5 = **58 第一**；Sonnet 5.5 56；Astra/Argon/Fable 5.1 均 53；GPT-6.1 Sol 52 | CSDN 2026-10-11、百家号 2026-10-01、知乎 2026-10-12 |
| Gemini 10-09 新政 | 免费仅 Flash-Lite；AI Plus $4.99 失去 Pro；AI Pro $19.99 得 Deep Think；算力计费 5h+周限+Effort 滑块 | 百家号/什么值得买 2026-10 |
| Argon 开放 | 09-30 发布；10-14 登陆 Gemini 应用面向 AI Pro/Ultra；输入输出均 100 万 token；API $2/$10 促销至 11-30 | 百家号 2026-10-14、新浪 2026-10-14 |
| Antigravity 送 Claude | AI Pro/Ultra 用户可用 Claude Opus 5.5/Sonnet 5.5（官方确认）；旧第三方模型（GPT-OSS 120B、Claude 4.6）11-02 下架 | 百家号 2026-10-04 |
| OpenAI 新档位 | Pro 500 $500/月（DevDay 09-29）：Astra Ultrafast + GPT-6.1 Sol Ultrafast，速度最高 8 倍；Pro 200 重开但 10-30 起新订阅额度减半 | OpenAI 帮助中心、百度百科 |
| GPT-6.1 Sol | 2026-09-29 上线 Work/Codex（API 名 gpt-6.1-sol），多任务接近 Astra | OpenAI 帮助中心、百度百科 |
| X Subscription | 2026-10-13 上线：Plus $8（含 Grok API 权限+Cursor）/Premium $30/Super $100/Ultra $200；档位总数信源不一（3/4/5 档）【疑】 | IT之家、DoNews、虎嗅、aibase |
| ChatGPT 数据开关 | 帮助中心提供"关闭将新聊天用于模型训练" | OpenAI 帮助中心数据管理 |
| Claude 数据条款 | 消费版（含 Pro/Claude Code）须选训练授权，弹窗默认为开；同意=保留 5 年，拒绝=30 天；商业/API 不受影响 | 澎湃/新智元 2025-09-01 |
| 律师 AI 执业指引 | 深圳律协八章三十五条（2026-09-02，含数据保密、跨境传输、输出核验）；全国律协常顾指引（2026-08-04）；宁夏指引（2026-03-22：私有化、脱敏、严禁直接采信、留痕） | 深圳律协、全国律协、宁夏律协 |
| AI 幻觉司法责任 | 全国首例 AI 幻觉侵权案终审：使用者承担全部过错责任；2024 年杨某案：AI 虚假案例提交法院被训诫 | 百家号 2026-09-01、微信公号 2026-10-15 |

## 二、法律场景选型结论

| 场景 | 首选 | 理由 |
|---|---|---|
| 长合同/卷宗/法条汇编 | Gemini AI Pro | 100 万 token + GraphWalks 84.2% + 幻觉 15% |
| 法律文书起草 | Claude Pro | 智能第一、文笔第一；严守核验 SOP |
| 类案检索 | Perplexity Pro（第二订阅） | 唯一编号引用可回源（学术口径 4% 幻觉） |
| 合规/舆情监测 | Grok $8（第二订阅） | 实时 X 数据 + 自带 API 额度 |
| 保密材料 | 都不用 | 境外服务=数据出境；优先私有化部署 |

引用核验 SOP：AI 输出仅作初稿 → 案号回裁判文书网、法条回国家法律法规数据库 → 链接逐条点开 → 全程留痕（脱敏输入、模型版本、修改痕迹）→ 第二人复核。

## 三、可复用操作

```bash
# 报告再生成（HTML 由 report.md 生成，改完 md 必须重跑）
cd ai-sub-20usd-2026 && python generate_html.py
```

## 四、坑与反直觉

1. **"Claude 幻觉最低"已过期**：Opus 4.7（2026-04）36% → Opus 5.5（2026-10）最高推理 59%。引用旧结论选型会被打脸。
2. **Copilot Pro 停售仍被广泛误传**：以微软官方支持页为准，替代 M365 Premium $19.99。
3. **"窗口大≠命中准"**：GraphWalks 检索命中与窗口大小是两回事；MRCR 高分多为固定针位，与真实文档堆检索差距大。
4. **生成式流水线"改 JSON 忘重跑"会静默留旧版**：本仓库 v1→v2 就犯过；交付前 grep 关键词自检（Sora/Hermes/停售）。
5. **AA-Omniscience 奖励"说不知道"**：低幻觉率部分来自模型更爱拒答；法律场景这是优点，但通用问答场景可能显得"答不上来"。
6. **Grok 档位与分数信源混乱**：3/4/5 档说法并存；Grok 4.6 有信源称 AA 61 而 4.7 旧口径 46，未解。
7. **Anthropic 训练授权弹窗默认"开"**：注销/换机重登后要复查设置。

## 五、未核实 / 存疑

- X Subscription 档位总数与 Super/Ultra 最终官宣价。
- $8 Grok 档具体模型版本与 API 额度数量。
- Claude 引用真实性 2026 同口径实测；ChatGPT 各消费档数据保留期。
- Argon 输出上限 100 万 vs 1.1M；"已购 Sora 额度可转 Codex"单一信源。
- 各产品中国区可用性与支付方式。
