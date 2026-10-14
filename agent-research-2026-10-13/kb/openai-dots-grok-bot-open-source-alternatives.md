---
id: openai-dots-grok-bot-open-source-alternatives
title: OpenAI Dots / Grok Bot 开源替代项目盘点（2026-10-13）
tags: [opendots, dots, grok-bot, 开源替代, 自托管, ai-agent]
created: 2026-10-13
updated: 2026-10-13
version: 1.2.0
status: stable
source: 本会话实测（GitHub API + README 直取）
confidence: 已核实
---

# TL;DR

「常开 AI 队友」类产品（OpenAI Dots、Grok Bot）共有 6 个主要开源替代，star 与协议均于 2026-10-13 核实。首选 **Anil-matcha/open-dots**（5.7k★，MIT）；要 Electron 桌面端选 **milind-soni/OpenMausBot**（4.6k★）；要手机 App 选 **elie222/rakazo**（3.8k★）。

# 项目清单

| 项目 | Star | 协议 | 形态 | 备注 |
|---|---|---|---|---|
| Anil-matcha/open-dots | 5,735 | MIT | 自托管工作区 | local-first，动作网关+审批+浏览器运行时；oliverv 的 fork 为 0★ |
| CopilotKit/OpenDots | 5,082 | MIT | 模板（Web+Mobile） | 每个 Dot 一台"电脑"，对话依赖 CopilotKit Intelligence（可 Docker 本地评估） |
| milind-soni/OpenMausBot | 4,641 | Apache-2.0 | Electron 桌面（mac/Win/Ubuntu） | 每 bot 跑本地 Claude/Codex；原名 OpenGrokBot |
| elie222/rakazo | 3,822 | Apache-2.0 | Web/Electron/iOS/Android | BYO 模型与电脑提供方，beta |
| thinkwee/OpenDot | 5 | MIT | 自托管团队 | 每 agent 有邮箱别名+电话+自己的电脑，极早期 |
| defog-ai/opendot | 0 | 未核实 | Slack/终端 | 本机容器执行+内置 MCP+定时；模型动作需 OpenDot 代为执行 |

# 背景

OpenAI 于 2026-09-29 DevDay 发布 Dots（ChatGPT 内常开 agent）；同类有 Meta Muse、Manus Cue、Instinct、OpenClaw、Hermes Agent、Claude Cowork。开源替代潮集中在 2026-09-30 至 10-02 爆发。

# 坑

- CopilotKit/OpenDots 是"模板不是成品"；对话能力绑定 CopilotKit Intelligence（自托管需授权）。
- Anil-matcha/open-dots 作者自述"early prototype, not feature-equivalent"。
- defog-ai/opendot 会给 agent shell+联网权限，官方 SECURITY.md 警告先读再用。
- 多家名字撞车（open-dots / OpenDot / OpenDots / opendot 四个不同项目），检索时注意作者名。

# 与 OpenClaw / Hermes Agent 的差异（2026-10-13 补充）

- **OpenClaw**（github.com/openclaw/openclaw，391,819★，MIT）：同一品类（常驻消息助手）的产品级真身。20+ 渠道（WhatsApp/iMessage/Telegram/Discord/Slack/Teams）+ macOS/iOS/Android/Windows/Linux 全平台原生 App，单 Gateway 笔记本/团队同配置；状态/记忆/凭据全在本地硬件；Claude/Codex/本地模型是可拔插 harness 插件（它是调度层，不替代编程 agent）。
- **Hermes Agent**（github.com/NousResearch/Hermes-Agent，253,208★，MIT）：独有 GEPA 自进化循环（DSPy+GEPA）——技能从经验自动生成并在使用中迭代、跨会话建用户模型；可跑 $5 VPS/GPU 集群/serverless，Telegram 聊天 + 云 VM 干活；任意模型。
- dot 类仅存差异化：拟人「联系人」多 agent + 每 Dot 一台云电脑 + 聊天流审批卡。其余指标（渠道、平台、成熟度）被 OpenClaw 全面碾压；「学习循环」被 Hermes 独占。

# dot 类 vs 普通 agent 工作台（2026-10-13 分析）

一句话：dot 类是「常驻同事」，普通工作台是「按需工具」。普通工作台做不到的 5 点：

1. 持久身份+消息渠道：每 Dot 有电话/邮箱别名/Slack 入口，可主动外呼；工作台无号码无邮箱，进不了聊天 App。
2. 24/7 常驻+主动推送：定时任务后台自跑，只汇报变化（defog/opendot 实测）；工作台基本 pull 模式。
3. 每 agent 一台持久「电脑」：云沙箱+浏览器+持久登录态，跨会话续用；工作台沙箱跟会话绑定，关窗即销毁。
4. 手机端审批治理：审批卡片弹在聊天流，通勤可批；thinkwee 还有独立「第二双眼」复核。工作台 diff 审查锁在桌面 IDE。
5. 人格化多 agent：多 Dot 各有人设/角色/权限，SuperDot 跨 Dot 编排；工作台是单 agent 多会话。

代价：开源替代全为 alpha/原型；编程硬任务远不如 OpenHands/Cline；CopilotKit OpenDots 对话能力绑定托管服务；Dots 原版 4000+ 插件生态开源版够不着。
