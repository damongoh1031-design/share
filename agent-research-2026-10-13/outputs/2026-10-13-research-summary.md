# 2026-10-13 调研总结（Agent 工作台 / Dots 类常驻助手）

> 数据核实日期均为 2026-10-13；star 为当日 GitHub 实时值。详细分析见 `agent-workbench-survey.html` 与 `kb/` 下三份知识库文档。

## TL;DR

1. 「类 WorkBuddy Agent 工作台」共收录 **51 个**开源工具，全能型首选 **Agent Zero**（Docker 内 XFCE 桌面+bash+定时+MCP）；桌面形态首选 **Cherry Studio / AnythingLLM / DeepChat**。
2. OpenAI Dots / Grok Bot 的开源替代共 6 个（撞名严重），首选 **Anil-matcha/open-dots**（5,735★ MIT）；其独有形态是「多人格联系人 + 每 agent 一台电脑 + 聊天流审批」。
3. 同一品类的产品级真身是 **OpenClaw**（391,819★ MIT，20+ 渠道+全平台 App）与 **Hermes Agent**（253,208★ MIT，GEPA 自进化循环）——dot 类原型在渠道/成熟度上被全面碾压，Hermes 独占「学习循环」维度。

## 研究线一：类 WorkBuddy Agent 工作台（51 个，报告见 HTML）

| 类别 | 代表 | Star | 一句话 |
|---|---|---|---|
| 全能型 | Agent Zero | 19,444 | Docker 内 XFCE+bash+子代理+定时+MCP 全占 |
| 自主开发平台 | OpenHands | 90,754 | 开源「AI 开发者」标杆 |
| 桌面工作台 | Cherry Studio | 52,579 | MCP+300 助手市场，Tauri 跨平台 |
| 桌面+RAG | AnythingLLM | 66,990 | 桌面/Docker 双形态 |
| CLI Agent | Gemini CLI | 107,301 | MCP+无头，可进 CI |
| Computer Use | Agent-S / Cua / browser-use | 12,593 / 29,519 / 117,763 | OS 级 GUI / 跨 OS 虚拟机 / 浏览器级 |
| 自动化平台 | n8n | 207,150 | fair-code，MCP 双向，Execute Command |

排除清单（按用户要求）：goose、aionui、openwork、opencode desktop、octop、openwebui desktop、codex、claude desktop。已剔除闭源 IDE（Cursor/Windsurf/Trae/Kiro）与 legacy 归档项目。**Roo Code 与 Flowise 仓库已归档**，选型需注意。

## 研究线二：Dots / Grok Bot 开源替代（6 个）

| 项目 | Star | 协议 | 形态 |
|---|---|---|---|
| Anil-matcha/open-dots | 5,735 | MIT | 自托管工作区（原型） |
| CopilotKit/OpenDots | 5,082 | MIT | 模板，每 Dot 一台电脑 |
| OpenMausBot | 4,641 | Apache-2.0 | Electron 桌面（含 Ubuntu） |
| rakazo | 3,822 | Apache-2.0 | Web/桌面/iOS/Android |
| thinkwee/OpenDot | 5 | MIT | 每 agent 有邮箱别名+电话 |
| defog-ai/opendot | 0 | 未核实 | Slack/终端+容器+MCP+定时 |

## 研究线三：与 OpenClaw / Hermes Agent 的差异

- **OpenClaw**（391,819★）：渠道常驻助手的产品级真身——20+ 聊天渠道+全平台原生 App，单 Gateway，Claude/Codex 是可拔插 harness 插件（调度层而非编程 agent 替代品）。
- **Hermes Agent**（253,208★）：GEPA 自进化（技能从经验生成并迭代、跨会话用户模型），可跑 $5 VPS/serverless。
- **dot 类唯一幸存差异化**：拟人多 agent + 每 agent 一台持久电脑 + 手机端聊天内审批。

## 产物清单

- `agent-workbench-survey.html` — 51 工具四分类评测表（正式交付物）
- `2026-10-13-research-summary.md` — 本文件
- `kb/workbuddy-write-tool-large-content-failure.md` — Write 工具大 content 被丢弃的排障（分块写入修复）
- `kb/openai-dots-grok-bot-open-source-alternatives.md` — Dots 类替代盘点 + 三方对比（v1.2.0）

## 可信度说明

star/协议/归档状态经 GitHub API 与仓库页面直取；能力矩阵中标注 △/— 的为调研推断，落地前以官网复核为准。Witsy 的 star 三次抓取失败，原报告中记「—」。
