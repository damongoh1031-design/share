---
id: chatgpt-work-mode
title: ChatGPT Work 模式（vs Chat）差异、设置、强化、Skills/MCP、Agent Loop
tags:
  - chatgpt
  - chatgpt-work
  - agent
  - codex
  - mcp
  - skills
  - ai-agent
  - openai
created: 2026-10-16
updated: 2026-10-16
version: 1.0.0
status: draft
source: 本次会话调研（OpenAI 官方帮助中心 / OpenAI Learn / 百度百科 / 一线实测文章）
confidence: 社区实证
---

# ChatGPT Work 模式

## TL;DR

**Chat 给答案（文本），Work 交成品（文件）。** Work 是 Agent 模式：拆解 → 调工具 → 校验 → 迭代 → 交付，可后台跑、可定时、可审批。Skills/MCP 有套餐门槛（Business/Enterprise 为主），Work 自身主推 plugins（60+ 连接器）。Loop 是 Work 与 Chat 的本质区别。

---

## 1. 事实基线（截至 2026-10-16）

| 项 | 值 |
|---|---|
| 发布 | 2026-07-10（与 GPT-5.6 同步） |
| 定位 | 办公智能体，"delegate real work to ChatGPT" |
| 模型演进 | GPT-5.6(Sol/Terra/Luna) → GPT-6 Astra(09-03) → GPT-6 Sol/Luna(09-23)；**10-14 GPT-5.5 退出 Work** |
| 底层 | Codex 执行框架，去掉编程界面 |
| 交付物 | 文档 / 表格 / 幻灯片 / 报告 / 网页应用 |
| 特色 | Computer Use（内置浏览器操作电脑）、Cloud Browser |

### Chat / Work / Codex

| 模式 | 用途 | 读什么 | 交付 |
|---|---|---|---|
| Chat | 问答、讨论、探索 | 当前对话 + 你给的材料 | 文本 |
| Work | 跨应用知识工作 | 邮件、文档、聊天、日历、业务系统 | 成品文件 |
| Codex | 软件开发 | 代码仓库、测试、Git | diff / PR |

## 2. 差异要点

| 维度 | Chat | Work |
|---|---|---|
| 交互 | 线性问答 | 状态机（拆解→执行→校验→交付） |
| 输入 | 问题/指令 | 目标 |
| 工具循环 | 无 | 有 |
| 上下文 | 回合独立 | 跨步骤保持并迭代 |
| 耗时 | 秒级 | 分钟~小时级 |
| 可追溯 | 弱 | 强（每步轨迹 + 来源） |
| 人工介入 | 无 | 改方向 / 答问 / 审批 |

**额度**：Chat 独立限额；**Work 与 Codex、ChatGPT for Excel、Workspace Agents 共享"智能体用量"池**。按 Token 计费。Plus 5 小时滚动限制 2026-08-26 恢复。

## 3. 设置 / 入口

| 端 | 情况 |
|---|---|
| 桌面端 | 顶部切换器 Chat/Work/Codex；能力最强（本地文件 + 内置浏览器 + Computer Use）。旧桌面端改名 ChatGPT Classic |
| 网页端 | Work 独立入口，可跑云端沙箱 |
| 手机端 | 有 Work；Codex 需 Remote 标签查看桌面任务 |

- 可用性：官方口径全档可用（差别在额度）；实测称桌面端已扩展至所有套餐，网页/手机端 Free/Go 不含 Work。
- 排查：App 版本 → 登录账号 → 是否企业 Workspace（管理员限制）→ 逐步开放。
- **本地 vs 云端**：本地可读写本机文件，关机停；云端关机续跑，读不到本地文件。开启 **Local computer access with Work Cloud** 可跨设备续跑。
- **云端与本地 Work 对话不互通**（Chat 对话互通）。

## 4. 强化清单

1. 提示词五要素：**目标结果 / 材料来源 / 约束 / 什么算好 / 何时停下等审批**。写清 "只用这些来源""发送前停下"。
2. 心法：给 Work 的**所有权**越大越有用——不要一次一个问题，让它对整件事负责。
3. 挂 plugins：左侧 **Customize → Plugins**；提示词用 `@插件名` 指定取数工具。
4. 模型：Astra（高难度/精致成品）→ Sol（复杂但更省）→ Luna（简单/快）。Free/Go 仅 Terra。
5. 推理强度：`max`（更深）；`ultra`（**并行 4 个子智能体**，Work 中仅 Pro/Enterprise）。
6. 资料库：Pro 100GB，可挂 Google Drive；当"任务工作区"，**不是唯一存储**。
7. 翻车三场景：任务模糊、来源不清、成果未人工终审。

## 5. Skills / MCP

| 能力 | 范围 | 备注 |
|---|---|---|
| Skills | 官方：Business / Enterprise / Healthcare / Edu | 4 种创建方式；默认含 skill-creator；上传先扫描（可用/需检查/已封锁） |
| MCP 完整版（含写入） | Business / Enterprise / Edu，**仅网页版** | 无需开发者模式，Plugins → Add custom MCP server |
| MCP | Pro 仅只读/抓取 | 本地服务器需 Secure MCP Tunnel |
| Work 自身连接 | plugins（60+） | Slack/Gmail/Drive/SharePoint/Teams/Outlook/Salesforce… |

## 6. Agent Loop

```
目标 → 拆解 → 计划 → 调工具/插件 → 执行 →（失败/不合规→回退修正）→ 交付 + 轨迹
```
- 可暂停待批准；云端后台续跑；Computer Use 后台操作应用。
- **定时任务**：一次性/周期/事件触发/监控。
  - 事件触发**在 Work 模式运行**，响应 Gmail/Slack/GitHub；Free/Go/FedRAMP 不支持。
  - 活动任务上限：Free/Go 3、Plus 5、Business/Edu 10、Pro/Enterprise 15。
  - 频率：付费最高每小时 1 次；事件触发合计 ≤30 次/小时、≤720 次/天。
  - 桌面 App 不能创建/编辑触发条件 → 用网页版。

## 可复用操作

**打开 Work**
1. 更新桌面 App（菜单 > 检查更新）→ 2. 顶部模式切换器选 **Work** → 3. composer 选 local / cloud

**挂插件**
`Customize → Plugins → 安装` → 提示词写 `@Slack 拉取 #product 本周消息并归类`

**装 Skills（网页版）**
`侧边栏 → 插件 → 技能页签 → 建立 → 从电脑上传 / 通过对话建立 / 编辑器建立`；调用：`@skills`
（沙箱内路径：`/root/.codex/skills/remote-skills`）

**接自定义 MCP**
`Plugins → + → Add custom MCP server → 填 HTTPS 端点 / Tunnel → 选认证 → 勾选风险确认 → Create as a plugin`

**建定时任务**
`已安排 → 新建`，或对话直接说 "包裹送达后通知我"；事件触发需 `设置 > 应用` 先连 Gmail/Slack/GitHub（Slack 频道内加 `@ChatGPT`）

**Work 提示词模板**
```
目标：<要交付什么、给谁>
材料：<附件/@来源，只允许用哪些>
约束：<格式/篇幅/口径/边界>
什么算好：<结构、必须包含、必须剔除>
停止条件：<先给草稿审阅 / 发送前停下>
```

## 坑与反直觉

1. **Work 不比 Chat 聪明**，只是更长更多步。概念解释用 Work 反而更慢。
2. **额度不通用**：Chat 用爆不影响 Work；但 Work 跑大任务会挤占 Codex。
3. **云端 ≠ 本地**：Work 对话跨端不同步（官方 at launch 限制）。
4. **MCP 变更不自动更新**，用冻结快照，需管理员 Refresh 重发布。
5. **官方 MCP 文档从未提 "Work mode"** —— MCP 在 Work 下的可用性无官方确认。
6. **技能上传有风险**，扫描 ≠ 安全背书，外部来源需自行审查。
7. 定时任务**不支持语音聊天和 GPT**；不活跃会自动暂停。

## 未核实 / 存疑

1. Skills 是否对**个人付费档**开放（官方只列企业档，实测称网页 Work 可 `@skills`）。
2. MCP 应用在 **Work 模式**下是否可用（无官方说明）。
3. Free/Go 在**桌面端**能否用 Work（来源互相矛盾）。
4. 单次任务的 credits 消耗无官方统一口径。
5. 部分中文来源为 AI 生成内容，仅采信可交叉验证部分。
