---
id: general-agent-workbench-alternatives
title: 通用 Agent 工作台选型（Hermes Agent 之外）— 六项能力 × 19 候选
tags:
  - agent-workbench
  - scheduled-tasks
  - mcp
  - sudo-systemd
  - knowledge-base
  - open-webui
  - librechat
  - n8n
created: 2026-10-12
updated: 2026-10-12
version: 1
status: stable
source: 本次会话 · GitHub REST API 直读 30 个仓库元数据 + 官方文档原文逐条取证（检索日 2026-10-12）
confidence: 已核实
---

# 通用 Agent 工作台选型（Hermes Agent 之外）

## TL;DR

六项需求里，前五项都有成熟候选；**唯独「执行 sudo 或 systemd」没有任何通用工作台原生自带且默认安全**——必须靠「宿主 shell 直通」或「MCP 桥接」二选一，而 MCP 桥接是唯一可审计、可限权的方案。

三条推荐组合：

1. **单人/单机/要真机 sudo** → `Open WebUI Computer (cptr)` 裸装 + sudoers 窄白名单（唯一一个「真机 + RRULE 定时 + 终端 + stdio MCP」的开源方案）
2. **团队/多机/要审计**（推荐） → `Open WebUI` 控制层 + `Open Terminal` 动作层 + `rhel-lightspeed/linux-mcp-server` 特权层
3. **偏编排/已有大量脚本** → `n8n`（Schedule Trigger + Execute Command + SSH + 双向 MCP 都在同一张画布上）

---

## 1. 需求 → 判据固化表

口语需求不可判定，必须先翻译。六项硬需求的判据：

| # | 口语需求 | 抽象单位 | 判定口径 | 权重 |
|---|---|---|---|---|
| R1 | 通用 agent 工作台 | 有 UI 的 Agent 运行时 | Web/桌面 UI + Agent 循环 + 工具调用；排除纯框架与纯 CLI | 必须 |
| R2 | 有周期任务 | 调度器实现 | cron/RRULE/可视化频率 · 时区 · 无人值守审批策略 · Webhook 触发 | 必须 |
| R3 | 可执行 sudo 或 systemd | 特权执行路径 | ① 能否作用于**目标宿主机**（非容器/沙箱）② 是否有作用域约束 ③ 默认开还是默认关 | **必须（最高权重）** |
| R4 | 有可视化输出 | 输出形态 | 图表/工件/画布/实时预览/文件产物 五类覆盖几类 | 高 |
| R5 | 有知识库 | 检索实现 | RAG（向量/混合）还是内容平台；能否完全离线自托管 | 高 |
| R6 | MCP 和网络搜索 | 连接层 | MCP 传输类型 · 是否双向 · 搜索是否内置 | 必须 |

### 1.1 R3 的三条实现路径（全篇分岔点）

| 路径 | 机制 | 代表 | 安全性 | 可审计性 |
|---|---|---|---|---|
| **A. 宿主 shell 直通** | 工作台跑在目标机上，Agent 拿到的 shell 就是宿主 shell | Open WebUI Computer（裸装）、Agent Zero + A0 CLI Connector、n8n Execute Command/SSH、Goose、Windmill | 低 | 中 |
| **B. MCP 桥接**（推荐） | 工作台保持非特权，专用 MCP 服务器执行特权操作，策略写在服务端 | `rhel-lightspeed/linux-mcp-server`、`openSUSE/systemd-mcp` | **高** | **高** |
| **C. SSH 外发** | 工作台经 SSH 连目标机执行 | n8n SSH 节点、任意 SSH MCP | 中 | 中 |

---

## 2. 候选池元数据（2026-10-12 直读 GitHub API）

| 仓库 | ★ | Fork | 语言 | 许可证 | 创建 | 最后推送 | 归档 |
|---|---:|---:|---|---|---|---|---|
| `n8n-io/n8n` | 207,043 | 61,094 | TypeScript | NOASSERTION | 2019-06-22 | 2026-10-12 | 否 |
| `Significant-Gravitas/AutoGPT` | 187,525 | 45,947 | Python | NOASSERTION | 2023-03-16 | 2026-10-12 | 否 |
| `langgenius/dify` | 158,190 | 25,007 | TypeScript | NOASSERTION | 2023-04-12 | 2026-10-12 | 否 |
| `open-webui/open-webui` | 154,352 | 22,607 | Python | NOASSERTION | 2023-10-06 | 2026-10-11 | 否 |
| `OpenHands/OpenHands` | 90,642 | 12,004 | TypeScript | MIT | 2024-03-13 | 2026-10-12 | 否 |
| `lobehub/lobehub` | 83,152 | 15,974 | TypeScript | NOASSERTION | 2023-05-21 | 2026-10-12 | 否 |
| `Mintplex-Labs/anything-llm` | 66,956 | 7,472 | JavaScript | MIT | 2023-06-04 | 2026-10-09 | 否 |
| `aaif-goose/goose` | 55,174 | 6,408 | Rust | Apache-2.0 | 2024-08-23 | 2026-10-12 | 否 |
| `LibreChat-AI/LibreChat` | 45,550 | 9,361 | TypeScript | MIT | 2023-02-12 | 2026-10-12 | 否 |
| `khoj-ai/khoj` | 37,646 | 2,508 | Python | AGPL-3.0 | 2021-08-16 | 2026-08-02 | 否 |
| `onyx-dot-app/onyx` | 32,409 | 4,544 | Python | NOASSERTION | 2023-04-27 | 2026-10-12 | 否 |
| `simstudioai/sim` | 29,807 | 3,849 | TypeScript | Apache-2.0 | 2025-01-05 | 2026-10-11 | 否 |
| `labring/FastGPT` | 29,799 | 7,326 | TypeScript | NOASSERTION | 2023-02-23 | 2026-10-12 | 否 |
| `letta-ai/letta` | 25,113 | 2,642 | — | Apache-2.0 | 2023-10-11 | 2026-09-10 | 否 |
| `coze-dev/coze-studio` | 21,699 | 3,127 | TypeScript | Apache-2.0 | 2025-06-26 | 2026-07-29 | 否 |
| `kortix-ai/suna` | 20,267 | 3,436 | TypeScript | NOASSERTION | 2024-10-05 | 2026-10-12 | 否 |
| `elizaOS/eliza` | 19,574 | 5,798 | TypeScript | MIT | 2024-07-09 | 2026-10-12 | 否 |
| `agent0ai/agent-zero` | 19,429 | 3,826 | Python | NOASSERTION | 2024-06-10 | 2026-10-11 | 否 |
| `windmill-labs/windmill` | 18,161 | 1,115 | Rust | NOASSERTION | 2022-05-05 | 2026-10-12 | 否 |

### 2.1 归档/停更排除项

| 仓库 | 理由 |
|---|---|
| `FlowiseAI/Flowise` | **已归档**（`archived: true`），尽管仍有 55,494★ |
| `reworkd/AgentGPT` | 已归档，最后推送 2025-04-29 |
| `bytebot-ai/bytebot` | 已归档，最后推送 2025-09-12 |
| `TransformerOptimus/SuperAGI` | 停更约 21 个月（2025-01-22） |
| `microsoft/autogen` | 框架非工作台；停更 6 个月（2026-04-15） |
| `infiniflow/ragflow` | RAG 引擎，无工作台形态与调度器 |
| `openinterpreter/openinterpreter` | 定位收窄为 coding agent，无调度器 |
| `agiresearch/AIOS` | 研究型内核，非可用工作台 |

### 2.2 改名仓库（旧路径返回 301，必须 `curl -L`）

```
frdel/agent-zero          → agent0ai/agent-zero
danny-avila/LibreChat     → LibreChat-AI/LibreChat
lobehub/lobe-chat         → lobehub/lobehub
block/goose               → aaif-goose/goose
All-Hands-AI/OpenHands    → OpenHands/OpenHands
OpenInterpreter/open-interpreter → openinterpreter/openinterpreter
```

---

## 3. 六项能力总表

图例：✅ 原生 · ⚠️ 有条件/需桥接 · ❌ 未发现 · 括注默认开/关 · 括号字母为证据等级

| 候选 | ★ | R2 周期任务 | R3 sudo/systemd | R4 可视化 | R5 知识库 | R6 MCP | R6 搜索 |
|---|---:|---|---|---|---|---|---|
| **Open WebUI** | 154k | ✅ RRULE（默认开）(A) | ⚠️ 需 Computer 或 MCP (A) | ✅ 工件/图表/图像 (B) | ✅ 13 种向量库 (B) | ⚠️ **仅 Streamable HTTP**（默认关）(A) | ✅ 内置 (B) |
| ↳ **Open WebUI Computer** | — | ✅ RRULE + Webhook (A) | ✅ **宿主 shell（裸装）**(A) | ✅ 文件/终端/git/预览 (A) | ✅ Skills + Memory (A) | ✅ **stdio + HTTP + OpenAPI**（默认关）(A) | ✅ 内置 (A) |
| **Agent Zero** | 19.4k | ✅ 原生调度器 + crontab (A) | ⚠️ 容器内 root；宿主需 CLI 桥 (A) | ✅ Canvas + Linux 桌面 (B) | ✅ 项目级知识 + 记忆 (B) | ✅ MCP + A2A（默认关）(B) | ✅ 内置 (B) |
| **n8n** | 207k | ✅ Schedule Trigger（默认开）(A) | ⚠️ Execute Command（**2.0 起默认禁用**）/ SSH 节点 (A) | ✅ 画布 + 节点输出 (A) | ⚠️ 向量库节点，无内置 KB (A) | ✅ **双向** MCP（默认关）(A) | ⚠️ 需 HTTP 节点 (B) |
| **LibreChat** | 45.6k | ✅ Scheduled Chats（默认关，实验性）(A) | ❌ 沙箱非宿主；需 MCP (A) | ✅ Artifacts + 代码解释器 (B) | ✅ RAG API + Memory (B) | ✅ **4 种传输**（默认关）(A) | ✅ 内置 (B) |
| **AnythingLLM** | 67k | ✅ Scheduled Jobs（**仅单用户模式**）(A) | ⚠️ File System Agent + MCP (B) | ✅ 生成文件（图表/文档）(A) | ✅ 向量库 + 文档管道 (B) | ✅ stdio（默认关）(A) | ✅ 内置 (B) |
| **Dify** | 158k | ✅ Schedule Trigger（**每流程限 1 个**）(A) | ❌ 代码节点禁系统命令 (A) | ✅ 工作流画布 (B) | ✅ 知识库 (B) | ✅ 可发布为 MCP Server (B) | ✅ 工具节点 (B) |
| **Suna / Kortix** | 20.3k | ✅ cron + 签名 Webhook (B) | ⚠️ 云沙箱非宿主 (B) | ✅ 报告/Deck/代码 (B) | ✅ git 化公司记忆 + Skills (B) | ✅ MCP + OpenAPI + GraphQL (B) | ✅ 内置 (B) |
| **OpenHands** | 90.6k | ✅ Automations（调度 + Webhook）(B) | ⚠️ 沙箱运行时 (B) | ✅ Agent Canvas (B) | ⚠️ 依赖 MCP/工具 (C) | ✅ 支持 (B) | ⚠️ 未核实 (C) |
| **Khoj** | 37.6k | ✅ Automations（cron + 邮件投递）(A) | ❌ 无宿主 shell (A) | ⚠️ 图像/文档 (B) | ✅ 文档索引 + Agent (B) | ✅ 有 MCP 实现 (A) | ✅ 内置 (B) |
| **Onyx** | 32.4k | ❌ 未发现 (B) | ⚠️ 沙箱 (B) | ✅ Artifacts (B) | ✅ **知识层本体** (B) | ✅ 双向（消费 + 自身为 MCP Server）(B) | ✅ 内置 (B) |
| **Sim** | 29.8k | ✅ 有 schedules 监控页 (B) | ⚠️ 桌面端终端 (B) | ✅ 知识/表格/桌面 (B) | ✅ 同步式知识库 (B) | ✅ 支持 (B) | ⚠️ 未核实 (C) |
| **LobeHub** | 83k | ⚠️ **云端执行，无 cron**（仅时/日/周）(B) | ❌ 无宿主 shell (B) | ✅ 生成式 UI (B) | ✅ 白盒记忆 (B) | ✅ 10000+ Skills / MCP 市场 (B) | ✅ 内置 (B) |
| **Windmill** | 18.2k | ✅ schedules + Webhook + Kafka (A) | ✅ Bash/PowerShell/Ansible + nsjail（默认开）(A) | ✅ 自动生成 UI + 流程图 (B) | ⚠️ 资源/变量，非 RAG (B) | ✅ **双向**（可作 client）(A) | ⚠️ 需脚本 (C) |
| **elizaOS** | 19.6k | ✅ scheduled workflows (B) | ⚠️ 插件（shell 插件）(B) | ⚠️ App views (B) | ✅ memory/knowledge (B) | ✅ 插件化 MCP (B) | ✅ 插件 (B) |
| **Letta** | 25.1k | ✅ cron（`src/cron/` + CLI）(A) | ⚠️ 需 MCP 工具 (C) | ✅ ADE / 桌面 + Web (B) | ✅ 状态化记忆（核心卖点）(B) | ✅ 完整 MCP（含 OAuth）(A) | ⚠️ 需工具 (C) |
| **FastGPT** | 29.8k | ⚠️ 未核实 (C) | ❌ 无 (C) | ✅ 工作流画布 (B) | ✅ RAG 为核心 (B) | ✅ **双向 MCP** (B) | ⚠️ 未核实 (C) |
| **Coze Studio** | 21.7k | ❌ 未发现 (B) | ❌ 无 (B) | ✅ 可视化画布 (B) | ✅ 知识库 (B) | ⚠️ 插件机制 (B) | ⚠️ 插件 (B) |
| **Goose** | 55.2k | ❌ 未发现（无调度器）(B) | ✅ **本地 CLI 直通宿主**（默认开）(B) | ⚠️ 桌面 App (B) | ❌ 无内置 KB (B) | ✅ **70+ MCP 扩展**（默认开）(B) | ✅ 内置 (B) |

---

## 4. 关键实现细节（按候选）

### 4.1 Open WebUI 家族

**它是三个产品，不是三个功能**（官方文档《Computer, Open WebUI, or Open Terminal?》并列）：

| | Open WebUI | Open Terminal | Open WebUI Computer |
|---|---|---|---|
| 重心 | 对话与控制层 | 动作层 | **你自己的机器** |
| 环境 | 不适用 | 全新隔离（Docker）或宿主 | **真实宿主** |
| 用户 | 一到多 | 跟随 Open WebUI | **一个受信任的所有者** |
| AI 必需 | 是 | 是 | 否 |

**周期任务有两套**：

- 主产品 **Automations**：RRULE；`ENABLE_AUTOMATIONS` 环境变量全局启停（禁用时 API 返 403）；权限 `Features > Automations`（`USER_PERMISSIONS_FEATURES_AUTOMATIONS`）；**创建者私有**，连管理员都看不到别人的自动化；可 `Run Now` / 暂停 / 历史 / 归档到文件夹；可给运行配终端。
- Computer **Scheduled tasks**：标准 iCalendar RRULE；Webhook 触发（含密钥 token + `{{webhook_payload}}`）；每次运行产生一个真实聊天 + 一条运行历史；通知工具（"仅在失败时通知我"）。

**MCP 传输能力相反**（本报告最重要的单条发现）：

| 产品 | 传输 | 说明 |
|---|---|---|
| Open WebUI 主产品 | **仅 Streamable HTTP** | 官方原文：*"Open WebUI's own MCP support is Streamable HTTP only."* 从 v0.6.31 起。**MCP 服务器仅管理员可添加**。类型必须选 `MCP (Streamable HTTP)`，不是 `OpenAPI` |
| Open WebUI Computer | **stdio + remote Streamable-HTTP + OpenAPI** | stdio 由 Computer 本地起进程、保活、崩溃重启；需 `pip install 'cptr[mcp]'` |

认证选项（主产品）：None / Bearer / OAuth / **OAuth 2.1 (DCR)** / **OAuth 2.1 (Static)**，含 RFC 8707 resource parameter。

知识层：主产品 13 种向量库（ChromaDB + PGVector 官方维护）、BM25+向量混合 + cross-encoder 重排、8 种抽取引擎（Tika/Docling/Azure/Mistral OCR/Datalab Marker/MinerU/PaddleOCR/自定义）、Agentic retrieval、Full context mode、Notes。Computer 侧是 Skills（`SKILL.md`，遵循 **agentskills.io 规范**）+ Memory + 自动加载 `MEMORY.md`/`AGENTS.md`/`AGENT.md`/`CLAUDE.md`（32KB 上限），技能发现路径含 `.claude/skills`、`.codex/skills`（**已有 Claude Code/Codex 技能自动识别**）。

### 4.2 Agent Zero

**周期任务在核心不在插件**（证据 A，源码树）：

```
helpers/task_scheduler.py
api/scheduler_task_create.py / scheduler_task_run.py / scheduler_tasks_list.py
api/scheduler_task_update.py / scheduler_task_delete.py / scheduler_tick.py
```

`TaskSchedule.to_crontab()` 可序列化为 crontab；三类任务：`ScheduledTask`（周期，带时区）、`PlannedTask`（按 `TaskPlan` 时间点列表）、`AdHocTask`（一次性）。

**插件索引 `agent0ai/a0-plugins` 有 200+ 插件**，与本需求相关的：`agent0-terminal`、`docker_terminal`、`rg`、`command_palette`、`stop_process`、`seq_logs`、`file_browser_ssh/s3/smb/ftps/webdav`、`tailscale_manager`、`human_in_the_loop`、`human_approval_gate`、`guard_system`、`mcp2cli`、`mcp_agent_access`、`skill_creator`、`knowledge_upload`、`obsidian`、`memex`、`graph_memory`、`tree_ring_memory`、`context_engine`、`autoresearch`。

宿主访问靠 **A0 CLI Connector**：*"a terminal-native bridge to your host machine"*。

### 4.3 n8n

- **Schedule Trigger**：秒/分/时/日/周/月/**Custom (Cron)**；可加多条 Trigger Rules；**自托管默认时区 `America/New_York`**；必须保存并发布。
- **Execute Command**：*"runs shell commands on the host machine that runs n8n"*；**自 2.0 起默认禁用**；仅自托管可用（Cloud 没有）；Docker 部署时命令跑在容器内；需改部署配置恢复。
- **SSH 节点**：核心节点，多机运维的正式路径。
- **MCP 双向**：MCP Server Trigger（n8n 作服务器，支持 SSE + streamable HTTP）+ MCP Client + MCP Client Tool + MCP registry + MCP credentials。
- **知识库是短板**：只有向量库节点（PGVector/Milvus/MongoDB Atlas/Oracle/Azure AI Search/Simple），无开箱 KB。
- 定位：*"The job is a fixed flowchart: the same steps, in the same order, every time."*

### 4.4 LibreChat（调度实现质量最高）

`librechat.yaml` 配置：

```yaml
interface:
  schedules:
    use: true
    create: true
    maxPerUser: 10          # 0 = 禁止创建
    minIntervalMinutes: 60
    autoDisableAfterFailures: 5
    fireConcurrency: 5
    requireProject: false
```

- 节奏：Hourly / Daily / Weekdays / Weekly / **Custom 五字段 cron**；**拒绝秒与年字段**，拒绝 >256 字符或无未来发生时间的表达式。
- **IANA 时区**逐条存储；夏令时：不存在的本地时间前移、重复的只跑一次、跨春季前移按真实时长校验间隔。
- **MCP 预检**：消耗额度前检查排期 Agent 及 Subagent 图所需的每个 MCP 工具；缺工具/服务器不可用/权限撤销/目录不完整/需交互认证 → **阻止运行**并指明需修复的 Agent。
- **多副本**：MongoDB 租约 + 幂等投递 + 防重叠；多副本必须 `USE_REDIS_STREAMS=true`，否则写入 **fail closed**；单进程可 `SCHEDULES_SINGLE_PROCESS=true`；全局急停 `SCHEDULES_DISABLED=true`。
- 权限：`SCHEDULES: USE` / `SCHEDULES: CREATE`；运行时重检 Agent 功能权限与查看权限。
- 官方标注 **early experimentation phase**。

**MCP 四种传输全支持**：`stdio`（**必须在 `librechat.yaml` 配**，管理员配置 API 拒绝进程型条目）/ `websocket` / `streamable-http` / `sse`。OAuth 2.0/2.1 + Client Discovery。占位符 `{{LIBRECHAT_OPENID_*}}` / `{{LIBRECHAT_GRAPH_*}}` / `{{LIBRECHAT_BODY_*}}`（请求作用域）。

**Code Interpreter 是沙箱非宿主**：ClickHouse/code-interpreter 驱动；Python/Node/Go/C/C++/Java/PHP/Rust/Fortran/R；**无通用网络访问**；Programmatic Tool Calling；Background execution（含 shell 调用）；Stateful Code Sessions。

### 4.5 AnythingLLM

- Scheduled Jobs **v1.13.0+**，**仅单用户模式**（多用户自托管看不到设置页）。
- cron 表达式，可视化构建器或直接输入；任务四要素 name/prompt/schedule/allowed tools。
- 工具范围 = agent skills / plugins / flows / **MCP servers** 的子集。
- 生成文件（图表/文档/导出）随运行保存；自动建 Scheduled Jobs 工作区；推送通知；对话式创建（`Create Scheduled Jobs` skill，同样单用户限定）。
- **MCP 是 stdio**：`mcpServers` JSON，`command` + `args` + `env`，`autoStart: false` 可按需启动。

### 4.6 Dify

- **Schedule Trigger**：仅 Workflow 应用；**每工作流限 1 个**；可视化或五字段 cron（支持 `L`/`?`/`@daily` 等）；显示接下来 5 次执行时间。
- **cron 语义陷阱**：日与周字段同时指定时是**「或」**——`1 2 3 4 4` 会在 4 月 3 日**和**每个周四触发。
- **Code 节点**：官方原文 *"Code executes in a strict sandbox that prevents file system access, network requests, and system commands."* 独立容器；预装 numpy/pandas/requests；默认出站走 SSRF 代理，`SANDBOX_ENABLE_NETWORK=false` 可禁网。
- 可把 Dify 应用**发布为 MCP Server**。

### 4.7 Suna / Kortix

```yaml
type: cron
cron: '0 0 9 * * 1-5'
```

- cron + **签名 Webhook**；"A trigger starts a session on a cron schedule or a signed webhook, with nobody present."
- 每个 session 一台**云沙箱**（非你的机器）；可并行上千个。
- Connector：3,000+ 应用经一个 scoped token + MCP + OpenAPI + GraphQL + raw HTTP；**凭据服务端代理，不进机器**。
- 知识库 = git 仓库里的纯文件（agents/skills/memory/connectors/triggers 全可 diff、可 review）。
- `kortix self-host start` 一个 Docker Compose 栈；自托管免费，托管云 $40/seat/月。

### 4.8 Windmill

- 触发方式最全：**schedules / webhooks / HTTP routes / Kafka / WebSockets / emails**。
- 语言：Python、TypeScript、Go、**Bash**、SQL、GraphQL、**PowerShell**、Rust、**Ansible**。
- 沙箱：**nsjail**（文件系统/资源隔离）+ **PID namespace 隔离（默认开启）**。
- **MCP 双向**：作服务器暴露 scripts/flows（含 **Schedules 的 CRUD**）；官方原文 *"Windmill can also be the client rather than the server: an AI session chat calls the tools of the external MCP servers you connect to it"*。
- 定位是脚本平台，不是 Agent 工作台。

### 4.9 Letta

- 主仓库已迁至 `letta-ai/letta-code`。
- **周期任务 ✅（源码 A）**：`src/backend/api/schedules.ts`、`src/cron/`（`cron-file.ts`、`index.ts`）、CLI `cron`/`cron-task-ref`/`cron-scope`。
- **MCP ✅ 完整（源码 A）**：`src/backend/api/mcp-servers.ts`、`unified-mcp.ts`、`src/cli/commands/mcp.ts`、`src/cli/subcommands/mcp-connect.ts`、`browser-device-mcp-oauth.ts`（浏览器设备码 OAuth）。
- 核心卖点是状态化记忆。

---

## 5. 可复用操作

### 5.1 批量取候选元数据（先查配额）

```bash
curl -s "https://api.github.com/rate_limit"          # 未认证：core 60/小时，search 10/分钟
curl -sL "https://api.github.com/repos/agent0ai/agent-zero" \
  | python -c "import sys,json;d=json.load(sys.stdin);print(d['full_name'],d['stargazers_count'],d['pushed_at'],d['archived'])"
```

> 必须用 `-L`：本次实测 6 个仓库已改名返回 301。

### 5.2 查源码树里的调度器/MCP（比读 README 可靠）

```bash
# Agent Zero 原生调度器
curl -sL "https://api.github.com/repos/agent0ai/agent-zero/git/trees/main?recursive=1" \
  | grep -oE '"path": "[^"]+"' | grep -Ei 'sched|cron|timer|task'

# Letta 的 cron 与 MCP
curl -sL "https://api.github.com/repos/letta-ai/letta-code/git/trees/main?recursive=1" \
  | grep -oE '"path": "[^"]+"' | grep -Ei 'sched|cron|mcp'

# Khoj 的 MCP 实现
curl -sL "https://api.github.com/repos/khoj-ai/khoj/git/trees/master?recursive=1" \
  | grep -oE '"path": "[^"]*mcp[^"]*"'
```

### 5.3 用官方文档索引代替逐页抓（效率提升最大的一招）

```bash
curl -sL "https://docs.n8n.io/llms.txt"        | grep -iE 'mcp|ssh|vector store'   # 287 KB 全站索引
curl -sL "https://www.windmill.dev/llms.txt"   | grep -iE 'mcp|schedul'
curl -sL "https://docs.openwebui.com/sitemap.xml" | grep -oE '<loc>[^<]+</loc>' | grep -Ei 'schedul|mcp'
```

### 5.4 场景 A：Open WebUI Computer 裸装 + 窄授权 sudoers

```bash
pip install cptr && cptr run          # 浏览器打开日志里的 http://localhost:8000/?token=...

sudo tee /etc/sudoers.d/cptr-agent >/dev/null <<'EOF'
cptr-agent ALL=(root) NOPASSWD: /usr/bin/systemctl restart nginx
cptr-agent ALL=(root) NOPASSWD: /usr/bin/systemctl status nginx
cptr-agent ALL=(root) NOPASSWD: /usr/bin/journalctl -u nginx -n 100
EOF
sudo visudo -c -f /etc/sudoers.d/cptr-agent     # 必须先校验语法

pip install 'cptr[mcp]'               # 需要 stdio MCP 时
# Settings → Admin → Tool Servers → 加 MCP (stdio)，填 command/args/env/cwd
```

### 5.5 场景 B：Open WebUI + linux-mcp-server

```bash
uv tool install linux-mcp-server
export LINUX_MCP_ALLOWED_LOG_PATHS=/var/log/nginx,/var/log/syslog   # 不设则什么都读不到
export LINUX_MCP_VERIFY_HOST_KEYS=True
# 不要开 LINUX_MCP_TRANSPORT=http —— 该传输没有认证

export WEBUI_SECRET_KEY="$(openssl rand -hex 32)"   # 不设则 OAuth MCP 每次重启都要重认证
docker run -d -p 3000:8080 -e WEBUI_SECRET_KEY -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
# 主产品 MCP 只能加 Streamable HTTP → 需要一层 stdio→HTTP 桥
```

### 5.6 决策速查

```
需要 Agent 操作 systemd/sudo
├─ 目标机就是工作台所在机？
│   ├─ 是 → 单用户？
│   │        ├─ 是 → 路径 A（Open WebUI Computer 裸装）+ sudoers 窄白名单
│   │        └─ 否 → 路径 B（MCP）
│   └─ 否 → 多台机？ → 路径 C（n8n SSH 节点）或 路径 B + SSH 策略
└─ 只读还是写？
    ├─ 只读 → systemd-mcp 默认 --allow-write=false，零配置即安全
    └─ 写 → linux-mcp-server 的 auth_policy.yaml + 最小 action
```

---

## 6. 坑与反直觉

1. **Open WebUI 的 MCP 只有 Streamable HTTP，没有 stdio**。反之 **Computer 原生支持 stdio**——同一家两个产品，传输能力相反。
2. **Open WebUI 的 MCP 服务器只能管理员添加**：*"Regular users cannot register their own, by design."*
3. **把 `mcpServers` JSON 填进 OpenAPI 类型的连接会让 UI 崩溃或无限加载**。类型必须选 `MCP (Streamable HTTP)`。
4. **不设 `WEBUI_SECRET_KEY`，OAuth 连接的 MCP 工具每次容器重启都要重新认证**（`Error decrypting tokens`）。
5. **Open WebUI 主产品和 Computer 的知识库不互通**：*"Knowledge bases, prompts, and users don't transfer between the two."*
6. **Open WebUI 有两套定时任务**（主产品 Automations / Computer Scheduled tasks），配置位置不同。
7. **无人值守 = 全量审批放行**：*"Scheduled runs execute with full tool approval: nobody is there to click Allow."*
8. **AnythingLLM 的 Scheduled Jobs 只在单用户模式可见**，多用户自托管看不到设置页。
9. **LobeHub 的定时任务在云端执行且不支持 cron**（仅时/日/周；Fixed interval 最短 10 分钟或 1 小时）。
10. **n8n 的 Execute Command 自 2.0 起默认禁用**，且 Cloud 版没有这个节点。
11. **n8n 自托管默认时区是 `America/New_York`**，不是 UTC 也不是本地。
12. **Dify 的代码节点在设计上就禁止系统命令**；且每工作流最多一个 schedule trigger。
13. **Dify 的 cron 在日与周同时指定时是「或」不是「与」**。
14. **LibreChat 的 Code Interpreter 是沙箱不是宿主**，且沙箱没有通用网络访问。
15. **LibreChat 的 stdio MCP 必须在 `librechat.yaml` 配**，管理员配置 API 拒绝进程型条目。
16. **Agent Zero 容器内是 root，但不等于宿主 sudo**。
17. **Agent Zero 的插件市场里搜不到「定时」插件，因为调度器在核心**。
18. **Suna 的沙箱是云电脑，不是你的机器**。
19. **Windmill 的 MCP 是双向的**（服务器 + 客户端），含对 Schedules 的 CRUD。
20. **Goose 有 70+ MCP 扩展但没有调度器**。MCP 最强 ≠ 六项齐全。
21. **OpenHands 主仓库 9 万星，但调度能力在只有 37 星的 `OpenHands/automation` 里**。
22. **6 个候选仓库改过名**，旧路径返回 301。
23. **`sudo` 在无人值守任务里会阻塞在密码提示**。不是 bug，是 sudo 的设计。
24. **sudoers 里的 `*` 能匹配空格**，`systemctl status *` 实际允许任意参数。
25. **`LINUX_MCP_TRANSPORT=http` 没有认证**，官方警告不要用于生产或不可信网络。
26. **`linux-mcp-server` 的 Gatekeeper 模型评分表在官方文档里仍是 `??`**，不要当唯一防线。
27. **Flowise 虽 5.5 万星但已归档**；AgentGPT、bytebot 同样已归档。星标高 ≠ 活着。
28. **GitHub API 未认证配额是 60/小时（core）+ 10/分钟（search）**。本次实测 3 次 search 调用即触发 `API rate limit exceeded`。
29. **Windmill 与 n8n 都不是 Agent 工作台**：前者是脚本平台，后者是带 AI 节点的自动化平台。
30. **「工作台」与「知识库」是两件事**：Onyx 的知识层是本体但无调度器；n8n 有调度器但知识库要自己拼。

---

## 7. sudo 与 systemd 的正确取舍：优先 polkit

如果目标是「让 Agent 能重启服务」，**不要给 sudo，给 polkit 规则**。

| 维度 | sudo + NOPASSWD | polkit |
|---|---|---|
| 授权粒度 | 命令 + 参数（通配/正则） | **D-Bus 方法级**（如 `org.freedesktop.systemd1.manage-units`） |
| 无人值守 | 必须 NOPASSWD | 规则里按 subject 区分，可 `yes` 可 `auth_admin_keep` |
| 绕过面 | 拿到该用户即可执行该命令 | 只能触发被授权的 D-Bus 调用 |
| 审计 | sudo 日志（可关） | journal 内可见调用方与主体 |
| 与 MCP 契合 | 需拼命令 | `openSUSE/systemd-mcp` 已这么实现 |

---

## 8. 未核实 / 存疑

| 项 | 状态 | 原因 |
|---|---|---|
| `Significant-Gravitas/AutoGPT` 的调度器 | 未核实 | 平台形态成立（187k★），未取得其 trigger 体系官方文档 |
| OpenHands 的 MCP 细节与网络搜索 | 未核实 | README 仅提及支持 |
| Sim 的 MCP 传输类型与网络搜索 | 未核实 | `docs.sim.ai` 返回空内容，仅有 README 佐证 |
| FastGPT 的周期任务 | 未核实 | README 未提及调度 |
| Letta 的宿主 shell 能力 | 未核实 | 仅有 MCP 通道，未找到直连宿主文档 |
| elizaOS 的六项逐条核验 | 部分 | 仅 README 级佐证 |
| Coze Studio 的插件/MCP 细节 | 部分 | 未取得 MCP 传输文档 |
| Activepieces 的六项能力 | 未核实 | 本轮仅取元数据（25,012★，2026-10-12 推送） |
| 各候选的许可证商业条款 | 未核实 | 多个仓库 `license.spdx_id` 为 `NOASSERTION` |

### 方法论边界

1. **星标不能代表子能力成熟度**：OpenHands 90k★ 主仓库 vs 37★ 的 automation 子仓库；n8n 207k★ 但 Execute Command 默认禁用。
2. **「未发现」≠「不支持」**：表中所有 ❌ 均为「在官方 README/文档/源码树中未找到」。
3. **未做端到端实测**：所有断言来自官方文档原文、README 原文或源码树文件名，未实际部署任一工作台执行 `sudo systemctl`。
4. **未覆盖 SaaS/闭源方案**（Claude Cowork、ChatGPT Work、Coze 云版、LobeHub 云版）。
5. **未覆盖中文社区生态**。

---

## 9. 与前序结论的衔接

本条目是《AI Agent Linux 运维全发行版深度研究报告》的横向补充：

- 前序报告解决「用 Hermes Agent 管 Linux 需要什么 MCP/Skills/知识库方案」。
- 本条目解决「除 Hermes Agent 外还有哪些工作台可用」。
- **两份的执行层结论一致**：`rhel-lightspeed/linux-mcp-server`（317★，Apache-2.0，`CommandSpec` 硬编码元组 + 具名占位符，不做 shell 插值）+ `openSUSE/systemd-mcp`（10★，MIT，直调 systemd C API，polkit/OAuth，`--allow-write` 默认 false）是厂商级特权执行层。任何工作台都应通过 MCP 挂载它们，而不是给 Agent 一个 sudo shell。
