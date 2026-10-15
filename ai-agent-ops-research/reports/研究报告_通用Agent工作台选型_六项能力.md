---
type: Checklist
---

# 通用 Agent 工作台选型研究报告（Hermes Agent 之外）

**版本** v1.0 · **成稿日期** 2026-10-12 · **检索方式** GitHub REST API 直读仓库元数据（30 个候选）+ 官方文档原文逐条取证 · **判定口径** 六项硬需求 × 默认开/关状态

> 本报告回答一个具体问题：**除了 Hermes Agent，还有哪些通用 Agent 工作台能同时满足「周期任务 / 可执行 sudo 或 systemd / 可视化输出 / 知识库 / MCP + 网络搜索」这六项能力？**
> 全文按「先固化判据 → 再广度检索 → 再逐条取证 → 最后按场景给组合」的顺序组织。每一条能力断言都标注了证据等级与出处；凡是官方文档没有明确写的，一律标为「未发现」而不是「不支持」。

---

## 摘要

**一句话结论：六项能力里，前五项都有多个成熟候选；唯独「执行 sudo 或 systemd」没有任何一个通用工作台是原生自带且默认安全的——它必须靠「宿主 shell 直通」或「MCP 桥接」两条路之一来补，而 MCP 桥接是唯一可审计、可限权的方案。**

### 分层结论

| 需求 | 结论 | 最强候选 |
|---|---|---|
| 通用 Agent 工作台 | 成熟，星标 1.5 万～20 万区间有 10+ 个可用项 | Open WebUI、Agent Zero、n8n、LibreChat |
| 周期任务 | **最被低估的一项**：四个候选实现了生产级调度（RRULE / cron / 租约协调） | Open WebUI Computer、LibreChat、Agent Zero、n8n |
| 执行 sudo / systemd | **无原生方案**。三种替代路径，推荐 MCP 桥接 | `rhel-lightspeed/linux-mcp-server` + `openSUSE/systemd-mcp` |
| 可视化输出 | 普遍具备，但形态分三类：工件/画布/预览 | LibreChat Artifacts、Dify 画布、Open WebUI Computer 预览 |
| 知识库 | 分两派：RAG 派（向量检索）与内容平台派（文件/记忆） | Open WebUI（13 种向量库）、AnythingLLM、Onyx |
| MCP + 网络搜索 | MCP 已是标配；**传输类型是关键差异点** | LibreChat（4 种传输）、n8n（双向）、Agent Zero（含 A2A） |

### 三条推荐组合

1. **单人 / 单机 / 要真机 sudo** → `Open WebUI Computer (cptr)` 裸装 + `sudoers` 窄授权。唯一一个「在你自己机器上、有 RRULE 定时任务、有终端、有 MCP stdio」的开源方案。
2. **团队 / 多机 / 要审计**（推荐） → `Open WebUI` 作控制层 + `Open Terminal` 作动作层 + `rhel-lightspeed/linux-mcp-server` 作特权执行层。三层分离，权限落在 MCP 服务端而不是 Agent 手里。
3. **偏编排 / 已有大量脚本** → `n8n`。Schedule Trigger + Execute Command + SSH + 双向 MCP + 向量库节点，是唯一把「定时」和「特权执行」都做成可视化节点的。

> ⚠️ **最重要的一条反直觉**：Open WebUI 的 MCP 支持**只有 Streamable HTTP，没有 stdio**。这意味着所有本地 stdio MCP 服务器（包括本报告推荐的 `linux-mcp-server`）都需要一层桥接才能接进去。这条限制官方文档写得很明确，但绝大多数第三方横评都写错了。

---

## 第 1 章 需求固化：把六句口语翻译成可判定的判据

### 1.1 判定表

原始需求是六句口语。口语不可判定，必须先翻译成「抽象单位 + 判定口径 + 权重」。

| # | 口语需求 | 抽象单位 | 判定口径 | 权重 |
|---|---|---|---|---|
| R1 | 通用 agent 工作台 | 有 UI 的 Agent 运行时 | 是否具备 Web/桌面 UI + Agent 循环 + 工具调用；排除纯框架（LangChain/AutoGen）与纯 CLI（Goose CLI 形态） | 必须 |
| R2 | 有周期任务 | 调度器实现 | 调度表达式类型（cron / RRULE / 可视化频率）· 时区处理 · 无人值守时的审批策略 · 是否支持 Webhook 触发 | 必须 |
| R3 | 可以执行 sudo 或 systemd | 特权执行路径 | ① 能否作用于**目标宿主机**（而非容器/沙箱内）② 是否有作用域约束（白名单/策略）③ 默认开还是默认关 | **必须（最高权重）** |
| R4 | 有可视化输出 | 输出形态 | 图表 / 工件（Artifacts）/ 画布 / 实时预览 / 文件产物 五类中覆盖几类 | 高 |
| R5 | 有知识库 | 检索实现 | RAG（向量/混合检索）还是内容平台（文件 + 记忆 + 提示词）；是否可完全离线自托管 | 高 |
| R6 | MCP 和网络搜索 | 连接层 | MCP 传输类型（stdio / SSE / streamable-HTTP / websocket）· 是否双向（既能消费也能暴露）· 网络搜索是否内置 | 必须 |

### 1.2 R3 是全篇的分岔点：三条实现路径

这是整份报告最关键的澄清。「可以执行 sudo 或 systemd」在架构上有且只有三种落法，三者的安全性与可审计性差距巨大：

| 路径 | 机制 | 代表 | 安全性 | 可审计性 |
|---|---|---|---|---|
| **A. 宿主 shell 直通** | 工作台本身就跑在目标机上，Agent 拿到的 shell 就是宿主 shell | Open WebUI Computer（裸装）、Agent Zero + A0 CLI Connector、n8n Execute Command / SSH | 低（Agent 权限 = 你的权限） | 中（有运行日志，无策略层） |
| **B. MCP 桥接**（推荐） | 工作台保持非特权，由一个**专用 MCP 服务器**执行特权操作，策略写在服务端 | `rhel-lightspeed/linux-mcp-server`、`openSUSE/systemd-mcp` | **高**（命令白名单 + polkit/OAuth + 默认只读） | **高**（策略文件可版本化） |
| **C. SSH 外发** | 工作台通过 SSH 连到目标机执行 | n8n SSH 节点、任意 SSH MCP | 中（取决于密钥权限） | 中 |

> ⚠️ **路径 A 有一个几乎必然踩到的坑**：无人值守的定时任务里执行 `sudo`，如果该用户不是 `NOPASSWD`，sudo 会**阻塞在密码提示上直到任务超时**。这不是 bug，是 sudo 的设计。要么给窄范围的 `NOPASSWD` 白名单，要么走路径 B。

### 1.3 本报告不解决的问题

- 不评估各工作台的模型能力（同一模型下差异很小）。
- 不评估中文界面质量、许可证商业条款细节（只在关键处提示）。
- 不评估 SaaS 版本的定价（只给自托管能力）。

---

## 第 2 章 候选池与筛选

### 2.1 检索方法

用 GitHub REST API 直读 30 个候选仓库的元数据（`/repos/{owner}/{repo}`），字段含星标、fork、语言、许可证、创建/最后推送日期、是否归档。检索日期 **2026-10-12**。

### 2.2 原始元数据（按星标降序）

| 仓库 | ★ | Fork | 语言 | 许可证 | 创建 | 最后推送 | 归档 |
|---|---:|---:|---|---|---|---|---|
| `n8n-io/n8n` | 207,043 | 61,094 | TypeScript | NOASSERTION | 2019-06-22 | 2026-10-12 | 否 |
| `Significant-Gravitas/AutoGPT` | 187,525 | 45,947 | Python | NOASSERTION | 2023-03-16 | 2026-10-12 | 否 |
| `langgenius/dify` | 158,190 | 25,007 | TypeScript | NOASSERTION | 2023-04-12 | 2026-10-12 | 否 |
| `langflow-ai/langflow` | 155,524 | 10,231 | Python | MIT | 2023-02-08 | 2026-10-12 | 否 |
| `open-webui/open-webui` | 154,352 | 22,607 | Python | NOASSERTION | 2023-10-06 | 2026-10-11 | 否 |
| `infiniflow/ragflow` | 92,025 | 10,958 | Go | Apache-2.0 | 2023-12-12 | 2026-10-12 | 否 |
| `OpenHands/OpenHands` | 90,642 | 12,004 | TypeScript | MIT | 2024-03-13 | 2026-10-12 | 否 |
| `lobehub/lobehub` | 83,152 | 15,974 | TypeScript | NOASSERTION | 2023-05-21 | 2026-10-12 | 否 |
| `openinterpreter/openinterpreter` | 68,554 | 5,892 | Rust | Apache-2.0 | 2023-07-14 | 2026-10-11 | 否 |
| `Mintplex-Labs/anything-llm` | 66,956 | 7,472 | JavaScript | MIT | 2023-06-04 | 2026-10-09 | 否 |
| `microsoft/autogen` | 61,365 | 9,280 | Python | CC-BY-4.0 | 2023-08-18 | 2026-04-15 | 否 |
| `FlowiseAI/Flowise` | 55,494 | 25,056 | TypeScript | NOASSERTION | 2023-03-31 | 2026-08-13 | **是** |
| `aaif-goose/goose` | 55,174 | 6,408 | Rust | Apache-2.0 | 2024-08-23 | 2026-10-12 | 否 |
| `CherryHQ/cherry-studio` | 52,549 | 5,066 | TypeScript | AGPL-3.0 | 2024-05-24 | 2026-10-12 | 否 |
| `LibreChat-AI/LibreChat` | 45,550 | 9,361 | TypeScript | MIT | 2023-02-12 | 2026-10-12 | 否 |
| `khoj-ai/khoj` | 37,646 | 2,508 | Python | AGPL-3.0 | 2021-08-16 | 2026-08-02 | 否 |
| `reworkd/AgentGPT` | 36,284 | 9,223 | TypeScript | GPL-3.0 | 2023-04-07 | 2025-04-29 | **是** |
| `onyx-dot-app/onyx` | 32,409 | 4,544 | Python | NOASSERTION | 2023-04-27 | 2026-10-12 | 否 |
| `simstudioai/sim` | 29,807 | 3,849 | TypeScript | Apache-2.0 | 2025-01-05 | 2026-10-11 | 否 |
| `labring/FastGPT` | 29,799 | 7,326 | TypeScript | NOASSERTION | 2023-02-23 | 2026-10-12 | 否 |
| `letta-ai/letta` | 25,113 | 2,642 | — | Apache-2.0 | 2023-10-11 | 2026-09-10 | 否 |
| `activepieces/activepieces` | 25,012 | 4,324 | TypeScript | NOASSERTION | 2022-12-03 | 2026-10-12 | 否 |
| `coze-dev/coze-studio` | 21,699 | 3,127 | TypeScript | Apache-2.0 | 2025-06-26 | 2026-07-29 | 否 |
| `kortix-ai/suna` | 20,267 | 3,436 | TypeScript | NOASSERTION | 2024-10-05 | 2026-10-12 | 否 |
| `elizaOS/eliza` | 19,574 | 5,798 | TypeScript | MIT | 2024-07-09 | 2026-10-12 | 否 |
| `agent0ai/agent-zero` | 19,429 | 3,826 | Python | NOASSERTION | 2024-06-10 | 2026-10-11 | 否 |
| `windmill-labs/windmill` | 18,161 | 1,115 | Rust | NOASSERTION | 2022-05-05 | 2026-10-12 | 否 |
| `TransformerOptimus/SuperAGI` | 17,702 | 2,225 | Python | MIT | 2023-05-13 | 2025-01-22 | 否 |
| `bytebot-ai/bytebot` | 11,077 | 1,512 | TypeScript | Apache-2.0 | 2025-02-03 | 2025-09-12 | **是** |
| `agiresearch/AIOS` | 6,466 | 920 | Python | NOASSERTION | 2024-01-15 | 2026-07-20 | 否 |

> ⚠️ **6 个仓库发生了改名/迁移**，直接用旧名请求会返回 `301 Moved Permanently`，必须跟随重定向：`frdel/agent-zero`→`agent0ai/agent-zero`、`danny-avila/LibreChat`→`LibreChat-AI/LibreChat`、`lobehub/lobe-chat`→`lobehub/lobehub`、`block/goose`→`aaif-goose/goose`、`All-Hands-AI/OpenHands`→`OpenHands/OpenHands`、`OpenInterpreter/open-interpreter`→`openinterpreter/openinterpreter`。这是一个实际踩到的坑——第一轮批量请求里这 6 个全部返回 `Moved Permanently` 而不是数据。

### 2.3 排除项与排除理由

| 仓库 | 排除理由 | 依据 |
|---|---|---|
| `FlowiseAI/Flowise` | **已归档**（`archived: true`），虽仍 5.5 万星 | API `archived` 字段 |
| `reworkd/AgentGPT` | 已归档，最后推送 2025-04-29 | 同上 |
| `bytebot-ai/bytebot` | 已归档，最后推送 2025-09-12 | 同上 |
| `TransformerOptimus/SuperAGI` | 最后推送 2025-01-22，停更约 21 个月 | 同上 |
| `microsoft/autogen` | 框架而非工作台；最后推送 2026-04-15，已滞后 6 个月 | 同上 |
| `infiniflow/ragflow` | RAG 引擎，无 Agent 工作台形态与调度器 | README |
| `langflow-ai/langflow` | 可视化 LLM 流程构建器，无「Agent 工作台 + 调度器」组合 | 定位判断 |
| `openinterpreter/openinterpreter` | 定位已收窄为「coding agent for open models」，无调度器 | README 原文 |
| `agiresearch/AIOS` | 研究型「AIOS」内核，非可直接用的工作台 | README |
| `CherryHQ/cherry-studio` | 桌面聊天客户端；有 MCP + 知识库 + 联网，但无调度器、无宿主 shell | 功能核对 |
| `Significant-Gravitas/AutoGPT` | 平台形态成立，但本轮未取得其调度器的一手文档，降为「未核实」 | 见第 8 章 |

### 2.4 入围 13 个候选

按「R1 工作台形态成立」+「未归档」+「近 90 天有推送」筛选：

**第一梯队（六项基本齐全）**：Open WebUI（+ Computer / Open Terminal）、Agent Zero、n8n、LibreChat、AnythingLLM、Dify、Suna/Kortix、OpenHands

**第二梯队（缺 1–2 项或有硬限制）**：Khoj、Onyx、Sim、LobeHub、Windmill、elizaOS、FastGPT、Coze Studio、Goose、Letta、Activepieces

---

## 第 3 章 六项能力总表

图例：**✅ 原生支持** · **⚠️ 有条件/需桥接** · **❌ 未发现** · 括注为「默认开 / 默认关」· 括号内字母为证据等级

| 候选 | ★ | R2 周期任务 | R3 sudo/systemd | R4 可视化 | R5 知识库 | R6 MCP | R6 网络搜索 |
|---|---:|---|---|---|---|---|---|
| **Open WebUI** | 154k | ✅ RRULE（默认开）(A) | ⚠️ 需 Computer 或 MCP (A) | ✅ 工件/图表/图像 (B) | ✅ 13 种向量库 (B) | ⚠️ **仅 Streamable HTTP**（默认关）(A) | ✅ 内置 (B) |
| ↳ **Open WebUI Computer** | — | ✅ RRULE + Webhook (A) | ✅ **宿主 shell（裸装）**(A) | ✅ 文件/终端/git/预览 (A) | ✅ Skills + Memory (A) | ✅ **stdio + HTTP + OpenAPI**（默认关）(A) | ✅ 内置 (A) |
| **Agent Zero** | 19.4k | ✅ 原生调度器 + crontab (A) | ⚠️ 容器内 root；宿主需 CLI 桥 (A) | ✅ Canvas + Linux 桌面 (B) | ✅ 项目级知识 + 记忆 (B) | ✅ MCP + A2A（默认关）(B) | ✅ 内置 (B) |
| **n8n** | 207k | ✅ Schedule Trigger（默认开）(A) | ⚠️ Execute Command（**2.0 起默认禁用**）/ SSH 节点 (A) | ✅ 画布 + 节点输出 (A) | ⚠️ 向量库节点，无内置 KB (A) | ✅ **双向** MCP（默认关）(A) | ⚠️ 需 HTTP/工具节点 (B) |
| **LibreChat** | 45.6k | ✅ Scheduled Chats（默认关，实验性）(A) | ❌ 沙箱非宿主；需 MCP (A) | ✅ Artifacts + 代码解释器 (B) | ✅ RAG API + Memory (B) | ✅ **4 种传输**（默认关）(A) | ✅ 内置 (B) |
| **AnythingLLM** | 67k | ✅ Scheduled Jobs（**仅单用户模式**）(A) | ⚠️ File System Agent + MCP (B) | ✅ 生成文件（图表/文档）(A) | ✅ 向量库 + 文档管道 (B) | ✅ stdio（默认关）(A) | ✅ 内置 (B) |
| **Dify** | 158k | ✅ Schedule Trigger（**每流程限 1 个**）(A) | ❌ 代码节点禁系统命令 (A) | ✅ 工作流画布 (B) | ✅ 知识库 (B) | ✅ 可发布为 MCP Server (B) | ✅ 工具节点 (B) |
| **Suna / Kortix** | 20.3k | ✅ cron + 签名 Webhook (B) | ⚠️ 云沙箱非宿主 (B) | ✅ 报告/Deck/代码 (B) | ✅ git 化公司记忆 + Skills (B) | ✅ MCP + OpenAPI + GraphQL (B) | ✅ 内置 (B) |
| **OpenHands** | 90.6k | ✅ Automations（调度 + Webhook）(B) | ⚠️ 沙箱运行时 (B) | ✅ Agent Canvas (B) | ⚠️ 依赖 MCP/工具 (C) | ✅ 支持 (B) | ⚠️ 未核实 (C) |
| **Khoj** | 37.6k | ✅ Automations（cron + 邮件投递）(A) | ❌ 无宿主 shell (A) | ⚠️ 图像/文档 (B) | ✅ 文档索引 + Agent (B) | ✅ 有 MCP 实现 (A) | ✅ 内置 (B) |
| **Onyx** | 32.4k | ❌ 未发现 (B) | ⚠️ 沙箱 (B) | ✅ Artifacts（文档/图形）(B) | ✅ **知识层本体** (B) | ✅ 双向（消费 + 自身为 MCP Server）(B) | ✅ 内置 (B) |
| **Sim** | 29.8k | ✅ 有 schedules 监控页 (B) | ⚠️ 桌面端终端 (B) | ✅ 知识/表格/桌面 (B) | ✅ 同步式知识库 (B) | ✅ 支持 (B) | ⚠️ 未核实 (C) |
| **LobeHub** | 83k | ⚠️ **云端执行，无 cron**（仅时/日/周）(B) | ❌ 无宿主 shell (B) | ✅ 生成式 UI (B) | ✅ 白盒记忆 (B) | ✅ 10000+ Skills / MCP 市场 (B) | ✅ 内置 (B) |
| **Windmill** | 18.2k | ✅ schedules + Webhook + Kafka 等 (A) | ✅ Bash/PowerShell/Ansible + nsjail（默认开）(A) | ✅ 自动生成 UI + 流程图 (B) | ⚠️ 资源/变量，非 RAG (B) | ✅ **双向**（可作 client）(A) | ⚠️ 需脚本实现 (C) |
| **elizaOS** | 19.6k | ✅ scheduled workflows (B) | ⚠️ 插件（shell 插件）(B) | ⚠️ App views (B) | ✅ memory/knowledge (B) | ✅ 插件化 MCP (B) | ✅ 插件 (B) |
| **Letta** | 25.1k | ✅ cron（`src/cron/` + CLI）(A) | ⚠️ 需 MCP 工具 (C) | ✅ ADE / 桌面 + Web (B) | ✅ 状态化记忆（核心卖点）(B) | ✅ 完整 MCP（含 OAuth）(A) | ⚠️ 需工具 (C) |
| **FastGPT** | 29.8k | ⚠️ 未核实 (C) | ❌ 无 (C) | ✅ 工作流画布 (B) | ✅ RAG 为核心 (B) | ✅ **双向 MCP** (B) | ⚠️ 未核实 (C) |
| **Coze Studio** | 21.7k | ❌ 未发现 (B) | ❌ 无 (B) | ✅ 可视化画布 (B) | ✅ 知识库 (B) | ⚠️ 插件机制 (B) | ⚠️ 插件 (B) |
| **Goose** | 55.2k | ❌ 未发现（无调度器）(B) | ✅ **本地 CLI 直通宿主**（默认开）(B) | ⚠️ 桌面 App (B) | ❌ 无内置 KB (B) | ✅ **70+ MCP 扩展**（默认开）(B) | ✅ 内置 (B) |

> ⚠️ **这张表里最容易误读的一格**：n8n 的 Execute Command 节点自 **n8n 2.0 起默认被禁用**（官方原文："the node is disabled by default from n8n 2.0"），且**仅在自托管版可用，n8n Cloud 上没有**。看到「n8n 能跑 shell」就下结论是错的。

---

## 第 4 章 逐候选取证

### 4.1 Open WebUI（+ Open WebUI Computer + Open Terminal）

**定位**：`open-webui/open-webui` 154,352★，Python，2023-10-06 创建，2026-10-11 最后推送。它是「模型无关的 AI 控制层」——聊天、知识库、用户权限、工具、提示词都在这一层。

**关键结构：Open WebUI 实际是三个产品，不是三个功能。** 官方文档《Computer, Open WebUI, or Open Terminal?》把三者并列：

| | Open WebUI | Open Terminal | Open WebUI Computer |
|---|---|---|---|
| 重心 | 对话与控制层 | 动作层 | **你自己的机器** |
| 环境 | 不适用 | 全新隔离（Docker）或宿主 | **真实宿主：现有文件、状态、工具、在跑的 agent** |
| 用户 | 一到多 | 跟随 Open WebUI | **一个受信任的所有者** |
| AI 必需 | 是 | 是 | 否（文件/终端/git 不用 AI 也能用） |

#### 4.1.1 周期任务（R2）— 两套独立实现，别搞混

**（a）Open WebUI 主产品的 Automations**（证据 A，官方文档）

- 按小时/日/周/月或**自定义 RRULE** 调度提示词。
- 每次运行创建一个真实聊天，走完整 chat completion 管线（模型默认值、工具、filter 都生效）。
- 管理员可用 `ENABLE_AUTOMATIONS` 环境变量或后台开关全局启停；禁用时 worker 停止、API 返回 **403**、侧栏入口隐藏。
- 权限门控：非管理员需 `Features > Automations` 权限（`USER_PERMISSIONS_FEATURES_AUTOMATIONS`）。
- **自动化是创建者私有的**：只有所有者能打开/编辑/运行/删除，"every other request, including one from an administrator, is answered as if the automation did not exist"。
- 可手动 `Run Now`、暂停/恢复、查看执行历史、把生成的聊天归档到指定文件夹。
- 可选：给运行配一个终端（"Give runs a terminal by configuring one on the model the automation uses"）——**这一句是 R3 的接口**。

**（b）Open WebUI Computer 的 Scheduled tasks**（证据 A，官方文档）

- 调度表达式是**标准 iCalendar RRULE**，官方给出的示例：

```
Every day at 09:00     RRULE:FREQ=DAILY;BYHOUR=9;BYMINUTE=0
Every Monday           RRULE:FREQ=WEEKLY;BYDAY=MO
Every hour             RRULE:FREQ=HOURLY;INTERVAL=1
Once, then never again RRULE:FREQ=DAILY;COUNT=1
```

- 可让 Agent 用工具自己建任务（"The agent has a tool for this; approve the tool call and the task exists"）。
- 每次运行产生：① 所选工作区里的一个真实聊天（侧栏可见，含完整任务活动）；② 任务上的一条运行历史（成功/失败 + 错误文本）。
- **Webhook 触发**：任务可生成含密钥 token 的 Webhook URL，外部 POST 即可立即运行；带 JSON body 时提示词可用 `{{webhook_payload}}` 占位符接住 CI 失败载荷。
- 通知：可加通知目标，提示词里写「仅在失败时通知我」，Agent 自行决定是否调用 notify 工具。

> ⚠️ **无人值守 = 全量审批放行**。官方原文：*"Scheduled runs execute with full tool approval: nobody is there to click Allow."* 同一份文档的审批页也写：*"Unattended paths (the gateway API, messaging bots, and scheduled tasks) always run in full approval."* 定时任务必须配一个你完全放心的工作区。

#### 4.1.2 执行 sudo / systemd（R3）

Open WebUI Computer 的定位文档写得极其直白（证据 A）：

> *"a signed-in user has the same power as someone at the keyboard within the boundary you chose, meaning **full filesystem and shell access on a bare install**, or exactly the folders you mounted if you run it in Docker."*

即：
- **裸装** → Agent 的 `run_command` 就是你自己的 shell，能 `systemctl`、能 `sudo`（前提见下）。
- **Docker 装** → 只能看到挂载进去的目录，`systemctl` 没有意义（容器内没有你的 systemd）。

安装方式（证据 A）：

```bash
pip install cptr
cptr run
# 或
uvx cptr@latest run
```

Docker 方式（官方文档原文）：

```bash
docker run --rm -it \
  -p 8000:8000 \
  -v cptr-data:/data \
  -v "$PWD:/workspace" \
  -w /workspace \
  ghcr.io/open-webui/computer:latest
```

> ⚠️ **sudo 在无人值守任务里的真实行为**：Agent 以启动 `cptr` 的那个用户身份执行命令。如果该用户执行 `sudo` 需要密码，定时任务会**卡在密码提示直到超时**。可行的修法是给一个极窄的 `NOPASSWD` 白名单，例如只放 `systemctl restart nginx`、`systemctl status *`，而不是 `ALL`。更稳的做法是走 MCP 桥接（第 5 章）。

#### 4.1.3 可视化输出（R4）

- **Open WebUI 主产品**：代码执行（浏览器内 Python 或经 Open Terminal）、图像生成（GPT-Image / Gemini / ComfyUI）、多模型并排对比、Artifacts、Mermaid 图。（证据 B）
- **Computer**：全功能文件编辑器、终端、**git 面板（状态/差异/暂存/提交/分支）**、网站实时预览、"generated artifacts"、手机端同一工作区视图。（证据 A）

#### 4.1.4 知识库（R5）

Open WebUI 主产品（证据 B，官方功能页）：

- **13 种向量数据库**，其中 ChromaDB 与 PGVector 官方维护，另含 Qdrant、Milvus、Elasticsearch 等。
- **混合检索**：BM25 + 向量 + cross-encoder 重排。
- **8 种抽取引擎**：Tika、Docling、Azure、Mistral OCR、Datalab Marker、MinerU、PaddleOCR、自定义 loader。
- **Agentic retrieval**：模型自主检索并阅读文档。
- **Full context mode**：整篇注入，不分块。
- **Notes**：可挂到任意聊天做全保真上下文注入。

Computer 侧的知识层（证据 A）：Skills（`SKILL.md`，遵循 **agentskills.io 规范**）、Memory（按用户，可查看/编辑/删除）、系统提示词解析链、自动加载 `MEMORY.md` / `AGENTS.md` / `AGENT.md` / `CLAUDE.md`（上限 32KB）。技能发现路径：工作区 `.cptr/skills`、`.agents/skills`、`.claude/skills`、`.codex/skills`；全局 `~/.cptr/skills`、`~/.agents/skills`——**已有 Claude Code / Codex 的技能会被自动识别，无需复制**。

> ⚠️ **知识库不互通**。官方原文：*"Knowledge bases, prompts, and users don't transfer between the two"*（指 Open WebUI 与 Computer 之间）。两者要分别配置。

#### 4.1.5 MCP 与网络搜索（R6）

**主产品的 MCP（证据 A，官方文档）——这是全表最容易被写错的一条**：

- 原生支持 MCP，**从 v0.6.31 起**。
- **只支持 Streamable HTTP**。官方原文：*"Open WebUI's own MCP support is Streamable HTTP only."*
- **MCP 服务器仅管理员可添加**：*"MCP servers can only be added by administrators, under Settings > Admin > Integrations. Regular users cannot register their own, by design."*
- 官方解释了为什么这么严：MCP 是**有状态、能力丰富**的（sampling、elicitation、持久会话、**通过 stdio 传输的任意宿主命令执行**），它跑在 Open WebUI 的信任边界内、带着连接用户的完整权限——*"a malicious or compromised MCP server could execute code and read or exfiltrate data with that user's access"*。
- 认证选项：None / Bearer / OAuth / **OAuth 2.1（DCR）** / **OAuth 2.1（Static）**，含 RFC 8707 resource parameter 与 OAuth scopes 配置。
- 配置陷阱（官方明示）：类型必须选 `MCP (Streamable HTTP)`，**不是 `OpenAPI`**；把 `mcpServers` JSON 填进 OpenAPI 连接会导致 UI 崩溃或无限加载。
- **必须设 `WEBUI_SECRET_KEY`**，否则 OAuth 连接的 MCP 工具每次重启都要求重新认证（`Error decrypting tokens`）。

> ⚠️ **因此：任何本地 stdio MCP 服务器（含 `linux-mcp-server`、`systemd-mcp`）都无法直接接入 Open WebUI 主产品**，需要一层 HTTP 桥。反之 **Computer 原生支持 stdio MCP**（见下），这是一个关键的选型分水岭。

**Computer 的 MCP（证据 A，官方文档）**：

| 类型 | 配置 | 运行方式 |
|---|---|---|
| OpenAPI | Spec URL + path（默认 `openapi.json`） | Computer 调 HTTP API，每个带 `operationId` 的操作变成一个工具 |
| MCP (remote) | Server URL | Streamable-HTTP 传输到远程 MCP 服务器 |
| **MCP (stdio)** | command、args、env、cwd | **Computer 本地启动进程、保活、崩了自动重启** |

- 需要可选依赖组：`pip install 'cptr[mcp]'`（Docker 镜像已含）。
- 工具在模型侧显示为 `<server_id>_<tool_name>`。
- 支持 Bearer key 与自定义 header；stdio 服务器的凭据走进程 env。
- 保存前有 `Verify` 按钮，会连接并列出发现的工具。

> ⚠️ 官方安全提示原文：*"A stdio MCP server is a real process running on the Computer host under the same account as Computer itself... Only connect servers you trust with your workspace context."*

**网络搜索**：主产品与 Computer 均内置（Computer 侧还含浏览器操作：导航、点击、填表、截图）。（证据 B / A）

#### 4.1.6 其他要点

- **Open Terminal** 是独立项目，需要 Open WebUI Enterprise 许可才能在生产使用；代码在 `github.com/open-webui/terminals`。（证据 B）
- 许可证字段是 `NOASSERTION`（非标准 SPDX 标识），商业使用前需自行读许可原文。
- 部署：Docker/K8s/Helm/pip；无状态架构 + Redis 协调可横向扩展；支持 S3/GCS/Azure Blob 与 OpenTelemetry。（证据 B）

---

### 4.2 Agent Zero

**定位**：`agent0ai/agent-zero` 19,429★（原 `frdel/agent-zero`），Python，2024-06-10 创建，2026-10-11 最后推送。自我定位是 *"an open agent framework for work that needs more than chat: a Dockerized Linux desktop, a browser with DOM annotation, live document cowork, projects, skills, plugins, and a bridge back to your host machine."*

#### 4.2.1 周期任务（R2）— 有原生调度器，这是它被严重低估的地方

证据等级 **A**：直接读源码树得到的调度器文件清单：

```
helpers/task_scheduler.py
api/scheduler_task_create.py    api/scheduler_task_run.py
api/scheduler_tasks_list.py     api/scheduler_task_update.py
api/scheduler_task_delete.py    api/scheduler_tick.py
api/self_update_schedule.py
```

以及 UI 侧 `plugins/_sidebar_folders/extensions/webui/sidebar-tasks-list-view`。

从 `helpers/task_scheduler.py.dox.md`（官方随源码维护的文档）读到的数据模型：

| 类 | 关键方法 | 含义 |
|---|---|---|
| `TaskSchedule` | `to_crontab() -> str` | 调度表达式可序列化为 **crontab** |
| `ScheduledTask` | `create(name, system_prompt, prompt, schedule, attachments, context_id, timezone, project_name, project_color)` | **带时区**的周期任务 |
| `PlannedTask` | `create(..., plan: TaskPlan)` | 按计划时间点列表执行（`TaskPlan.add_todo/set_in_progress/set_done/get_next_launch_time`） |
| `AdHocTask` | `create(name, system_prompt, prompt, token, ...)` | 一次性/临时任务 |
| `BaseTask` | `check_schedule(frequency_seconds)`、`get_next_run()`、`on_run/on_finish/on_error` | 调度检查与生命周期钩子 |

也就是说，**Agent Zero 的周期任务是核心功能，不是插件**。README 里「Scheduled operations: run recurring checks and monitoring tasks with project-scoped context and credentials」与之一致。

#### 4.2.2 执行 sudo / systemd（R3）— 注意容器的语义陷阱

- Agent Zero **默认跑在 Docker 里**：`docker run -p 80:80 -v a0_usr:/a0/usr agent0ai/agent-zero`。（证据 B）
- README 描述：*"The agent can use real GUI software, terminals, files, and desktop apps inside the Canvas."*——这里的 terminal 是**容器内的** Linux 桌面终端。（证据 B）
- 宿主访问的官方通道是 **A0 CLI Connector**：*"It connects to a running Agent Zero instance and gives that instance a terminal-native bridge to your host machine - so the same agent (with all its memory, projects, and skills) can also work on real files outside the Docker container."*（证据 B）

> ⚠️ **容器内是 root，但这不等于宿主 sudo**。容器里的 root 只在容器命名空间内有效；它能碰到的只有挂载进去的卷。要操作宿主机的 systemd，必须走 A0 CLI Connector 或挂载宿主路径——而挂载宿主路径又等于把宿主的文件暴露给 Agent。

#### 4.2.3 可视化输出（R4）

- Canvas 内的完整 Linux 桌面（可用真实 GUI 软件，README 举例：开 Blender 建模、跳进终端窗口、管理文件、跑无 API 的 GUI 工具）。
- 浏览器带 **DOM 注解**：人可以在页面上标注意见，Agent 把视觉评论转成可执行的修复。
- 浏览器历史保留关键步骤截图，旧对话仍能看到 Agent 当时看到的内容。
- 支持 Chrome 扩展；也可通过 A0 CLI Connector 驱动**你自己机器上的** Chrome/Edge/Brave/Opera/Vivaldi/Chromium。
（以上证据 B）

#### 4.2.4 知识库（R5）

- **Projects** 隔离工作区、指令、记忆、密钥、知识、仓库、模型预设——*"Keep files, instructions, secrets, memories, repositories, and model-preset choices isolated per project."*
- 记忆系统可替换后端（替代记忆后端、智能整合策略、向量召回插件）。
（证据 B）

#### 4.2.5 MCP 与网络搜索（R6）

- 支持 **插件、MCP、A2A、自定义工具、自定义提示词、项目级配置**。（证据 B）
- 官方插件索引 `agent0ai/a0-plugins` 是**社区维护的索引仓库**，每个插件一个目录、一个 `index.yaml` 指向插件自己的仓库。（证据 A）
- 我拉取了完整插件名清单（**200+ 个**），与本需求相关的包括：
  `agent0-terminal`、`docker_terminal`、`rg`（ripgrep）、`command_palette`、`commands`、`stop_process`、`seq_logs`、`sentrysearch`、`file_browser_ssh`、`file_browser_s3`、`file_browser_smb`、`file_browser_ftps`、`file_browser_webdav`、`tailscale_manager`、`human_in_the_loop`、`human_approval_gate`、`guard_system`、`mcp2cli`、`mcp_agent_access`、`a0_agent_skills`、`skill_creator`、`skill_slash_commands`、`skills_finder`、`skill_synthesizer`、`knowledge_upload`、`obsidian`、`notebooklm`、`open_notebook`、`memex`、`graph_memory`、`memory_hardening`、`tree_ring_memory`、`qmd_memory`、`autosave_memory`、`context_engine`、`autoresearch`、`autonomous_growth_engine`、`deep` 类研究插件、`slack`/`discord`/`telegram`/`whatsapp_automation`/`signal`/`matrix_chat` 等消息通道。（证据 A）
- **网络搜索**：内置；另有 `a0_fauxplexica`（Perplexica 风格搜索）、`sentrysearch`、`qmd_search` 等搜索类插件。（证据 B）

> ⚠️ 插件索引里**没有**名为 scheduler/cron 的插件——因为调度器在核心（4.2.1），不在插件层。不要因为「插件市场里搜不到定时插件」就判断 Agent Zero 不能定时。

---

### 4.3 n8n

**定位**：`n8n-io/n8n` 207,043★，TypeScript，2019-06-22 创建，2026-10-12 最后推送。它是全表星标最高的候选，也是最接近「Linux 运维自动化」本行的候选——但它不是 Agent 工作台，是**带 AI 节点的自动化平台**。这个区别很重要。

#### 4.3.1 周期任务（R2）— 证据 A，官方文档

**Schedule Trigger 节点**，官方原文：*"Use the Schedule Trigger node to run workflows at fixed intervals and times. This works in a similar way to the Cron software utility in Unix-like systems."*

- 触发间隔单位：秒 / 分 / 时 / 日 / 周 / 月 / **Custom (Cron)**。
- 可加**多条 Trigger Rules**，一个节点跑多个不同排期。
- 时区：优先用 workflow 时区，否则用实例时区；**自托管默认 `America/New_York`**，n8n Cloud 注册时尝试探测所有者时区，回退 GMT。
- 必须**保存并发布**工作流，Schedule 才会生效。

> ⚠️ 自托管默认时区是 `America/New_York`，不是 UTC 也不是本地。做运维排期（比如「每天凌晨 3 点清理日志」）时必须显式设时区，否则会错 12 小时左右。这是一个非常容易踩的坑。

#### 4.3.2 执行 sudo / systemd（R3）— 证据 A，官方文档

**Execute Command 节点**：

> *"The Execute Command node runs shell commands on the host machine that runs n8n."*

- **安全警告（官方原文）**：*"The Execute Command node can introduce significant security risks in environments that operate with untrusted users. Because of this, the node is **disabled by default from n8n 2.0**."*
- **可用范围**：自托管全部版本可用；**n8n Cloud 上没有这个节点**。
- 执行 shell：宿主默认 shell（Windows 是 `cmd`，macOS 是 `zsh`）。
- **Docker 部署时命令在 n8n 容器内执行，不在 Docker 宿主上**。
- queue 模式下命令在生产环境跑在正在执行任务的 worker 上；手动执行跑在主实例上，除非设 `OFFLOAD_MANUAL_EXECUTIONS_TO_WORKERS=true`。
- 多命令：用 `&&` 连接，或每行一条。

**SSH 节点**：核心节点里存在（`n8n-nodes-base.ssh`），可用于对远程主机执行操作——这是 n8n 做多机运维的正式路径。（证据 B）

> ⚠️ 要恢复 Execute Command，需要在**部署层**显式把节点从禁用列表里移除（官方指向 `block-specific-nodes` 配置页）。这不是界面开关。

#### 4.3.3 可视化输出（R4）

工作流画布 + 每个节点的执行数据面板 + AI Agent 节点的中间步骤可视化。（证据 A/B）

#### 4.3.4 知识库（R5）— 这是 n8n 的短板

n8n 提供**向量库节点**而非知识库产品。官方文档索引中可见的向量库节点包括：PGVector、Milvus、MongoDB Atlas、Oracle Database、Azure AI Search、Simple (In-Memory) 等。（证据 A）

也就是说：n8n 能做 RAG **管线**，但不提供「上传文档→自动切分→检索」的**开箱知识库**。要知识库得自己拼。判为 ⚠️。

#### 4.3.5 MCP 与网络搜索（R6）— 双向且完整，证据 A

从 n8n 官方文档索引 `llms.txt`（287,299 字节）中检索到的 MCP 相关页面：

| 页面 | 作用 |
|---|---|
| **MCP Server Trigger** | **n8n 作为 MCP 服务器**，把 n8n 工具与工作流暴露给 MCP 客户端；支持 SSE 与 streamable HTTP |
| **MCP Client** | n8n 作为 MCP 客户端消费外部 MCP 服务器 |
| **MCP Client Tool** | 在 AI Agent 里把 MCP 服务器当工具用 |
| **MCP servers（registry）** | 一键连接 MCP 注册表服务器 |
| **MCP credentials** | MCP 服务器认证 |
| **Connect to n8n MCP server** | 让 Claude Desktop / Claude Code / Codex / Gemini CLI / Cursor / VS Code / Windsurf / Lovable / Google ADK 等客户端连接 n8n |
| **MCP server tools reference** | n8n MCP 服务器暴露的全部工具（工作流管理、工作流构建器、Agent 管理、数据表） |

官方对 MCP Server Trigger 的描述：*"The MCP Server Trigger node acts as an entry point into n8n for MCP clients. It operates by exposing a URL that MCP clients can interact with to access n8n tools."* 并且可以挂 **Custom n8n Workflow Tool** 把整条工作流暴露成 MCP 工具。

**网络搜索**：无专用内置搜索节点，需用 HTTP Request 节点或社区节点实现。判为 ⚠️。

#### 4.3.6 n8n 的定位警告

n8n 的强项是**固定流程的自动化**。Suna 的对比文档给了一句很准确的判据（证据 B）：

> *"n8n（workflow automation）：The job is a fixed flowchart: the same steps, in the same order, every time."*

如果你的运维任务有固定的步骤序列（巡检→收集→判断→通知），n8n 是最佳；如果需要开放式推理（「看看系统为什么慢」），n8n 的 AI Agent 节点能做但不如 Agent 原生工作台自然。

---

### 4.4 LibreChat

**定位**：`LibreChat-AI/LibreChat` 45,550★（原 `danny-avila/LibreChat`），TypeScript，**MIT**，2023-02-12 创建，2026-10-12 最后推送。自我定位：*"Enhanced ChatGPT Clone: Features Agents, MCP, Skills, DeepSeek, Anthropic, AWS, OpenAI, Responses API, Azure, Groq, o1, GPT-5, Mistral, OpenRouter, Ve..."*

#### 4.4.1 周期任务（R2）— Scheduled Chats，实现质量全表最高

证据等级 **A**，官方文档完整可读。这是一个**生产级设计**，不是玩具：

配置（`librechat.yaml`）：

```yaml
interface:
  schedules:
    use: true
    create: true
    maxPerUser: 10          # 0 = 禁止创建
    minIntervalMinutes: 60  # 最短允许间隔
    autoDisableAfterFailures: 5
    fireConcurrency: 5
    requireProject: false
    # projectId: '000000000000000000000000'
```

能力：

- 节奏类型：**Hourly / Daily / Weekdays / Weekly / Custom（五字段 cron）**。Custom 支持 `0 9,17 * * 1-5` 这类表达式；**拒绝秒字段与年字段**，拒绝超过 256 字符、或没有未来发生时间的表达式。
- **IANA 时区**，每条排期独立存储；改时区会重算下次发生时间并按部署最短间隔重新校验。
- **夏令时处理**：不存在的本地时间前移到第一个有效时刻；重复的本地时间只跑一次；跨春季前移的间隔校验按真实时长计算。
- 每次发生**开一个新对话**，用指定的已保存 Agent。
- 运行中若暂停等待 Ask User 或工具审批，状态变为 **Needs approval**，可打开对话完成决策。
- **防重叠**：LibreChat 阻止同一排期的重叠发生；有活跃运行或余额不足时可能跳过某次发生。
- **MCP 预检**：消耗生成额度前，会检查该排期 Agent 及其可运行 Subagent 图所需的每一个 MCP 工具；缺工具/服务器不可用/权限被撤销/目录不完整/需要交互的认证流程都会**阻止运行**，并指明哪个 Agent 需要修复。
- **多副本部署**：用 MongoDB 租约 + 幂等触发投递 + 防重叠来协调持久发生；多副本必须同时启用 `USE_REDIS_STREAMS=true`，否则排期写入**fail closed**。单进程无 Redis 的部署可显式 `SCHEDULES_SINGLE_PROCESS=true`。
- **全局急停**：`SCHEDULES_DISABLED=true` 阻止自动发生与 Run now，但不删定义。
- 权限：`SCHEDULES: USE` 控制能否列出/查看；`SCHEDULES: CREATE` 额外门控创建/编辑/启停/运行/删除；运行时还会重新检查 Agent 功能权限与查看权限。
- 排期失败会自动禁用（连续失败达 `autoDisableAfterFailures`，或 Agent 被删、配置失效、访问被撤销、余额不足、必需项目缺失等）。

> ⚠️ 官方明示：*"Scheduled Chats are in an early experimentation phase. Their behavior, configuration, and..."*（该句在文档中被截断）。功能设计很完整，但官方自己标为实验性，**升级前要读变更日志**。

#### 4.4.2 执行 sudo / systemd（R3）— 沙箱，不是宿主

LibreChat 的 Code Interpreter **不碰宿主机**：

- 由 `ClickHouse/code-interpreter` 驱动（Apache 2.0），是一个**沙箱化代码执行服务**，需自托管后把 LibreChat 指过去。
- 支持语言：Python、Node.js（JS/TS）、Go、C/C++、Java、PHP、Rust、Fortran、Rscript。
- **沙箱没有通用网络访问**。工具调用经 Code Interpreter Tool Call Server 代理；LibreChat 把实时调用方能力投影与其可信注册表取交集，因此只有该 Agent 已注册的活跃 programmatic 工具能被调用，请求**无法自我扩权**。
- **Programmatic Tool Calling**：让 Agent 把选定的 MCP 工具经 Code Interpreter 沙箱编排——沙箱代码可以调用注册的工具桩、用循环与条件、处理中间结果。
- **Background execution**：Agent 可派发长时间运行的**代码或 shell 工作**然后继续对话；需在 Agents endpoint capabilities 里加 `run_in_background`，并在 Agent 上开 Code Interpreter。
- **Stateful Code Sessions**：可部署独立的有状态 Code Interpreter 路由。

结论：**R3 必须走 MCP**。判为 ❌（沙箱非宿主）。（证据 A）

#### 4.4.3 可视化输出（R4）

- **Artifacts（Generative UI）**
- **Code Interpreter**（图表/文件产物）
- 文档导航可见的还有：Conversation Pull Requests、Agent Plugins、Subagents、Agents API (Beta)。
（证据 B）

#### 4.4.4 知识库（R5）

- **RAG API（Chat with Files）**——独立的 RAG 服务。
- **User Memory**（用户记忆）
- **Message Search**（消息检索）
- **Skills**：可复用的 `SKILL.md` 指令，Agent 可手动、自动或每轮调用。
（证据 B）

#### 4.4.5 MCP 与网络搜索（R6）— 传输类型全表最全，证据 A

| 传输类型 | 说明 |
|---|---|
| `stdio` | **必须在 `librechat.yaml` 配置**；管理员配置 API 会拒绝进程型条目；数据库或按主体的覆盖无法替换/移除已有的进程型服务器 |
| `websocket` | — |
| `streamable-http` | — |
| `sse` | — |

- 配置字段：`type`、`command`、`args`、`url`、`env`、`stderr`（`pipe`/`ignore`/`inherit`/文件描述符，默认 `inherit`）。
- 可通过 `smithery.ai` 找并安装 MCP 服务器到 `librechat.yaml`；也可在 UI 的 MCP Settings 面板创建（面板创建的服务器**不需要重启**，改 yaml 需要重启）。
- **OAuth 2.0/2.1**：支持 Client Discovery（自动注册）与显式配置；回调 URL 形如 `${DOMAIN_SERVER}/api/mcp/<server-name>/oauth/callback`。
- 用户信息占位符：MCP 服务器可通过 URL/header 里的占位符访问用户信息（SSE 与 Streamable HTTP）；`{{LIBRECHAT_OPENID_*}}`、`{{LIBRECHAT_GRAPH_*}}`、`{{LIBRECHAT_BODY_*}}`；`LIBRECHAT_BODY_*` 是请求作用域的，只在该次运行内复用。
- 运维细节：Streamable HTTP 重连时可能短暂返回 **HTTP 409**（服务器仍持有旧会话的 SSE 流），LibreChat 视为瞬态并自动重建；响应类型按解析后的 Content-Type 媒体类型分类，而非子串匹配。
- 取消传播：前台 Agent 工具调用按 Stop 时，对 Streamable HTTP 服务器发送 `notifications/cancelled`（**服务器必须遵守该通知**才会真正停止）。

**网络搜索**：内置。（证据 B）

---

### 4.5 AnythingLLM

**定位**：`Mintplex-Labs/anything-llm` 66,956★，JavaScript，**MIT**，2023-06-04 创建，2026-10-09 最后推送。定位是「一体化私有 ChatGPT」。

#### 4.5.1 周期任务（R2）— Scheduled Jobs，但有硬限制

证据等级 **A**，官方文档完整。

- 版本要求：**v1.13.0 及以上**。
- **硬限制（官方原文）**：*"It is also only available in single-user mode — self-hosted instances running in multi-user mode will not see the Scheduled Jobs settings page."*
- 机制：*"Scheduled Jobs let you run an AI agent on a recurring schedule — unattended, with access to your agent tools, and with every result saved for you to review later."*
- 任务四要素：**name、prompt、schedule、allowed tools**。可随时启用/禁用。
- 调度：**cron 表达式**，可用可视化构建器或直接输入。
- 每次运行（Run）有状态（`queued`/`running`/`completed`/`failed`/`timed out`）、开始时间、时长，以及完整结果（Agent 的思考、工具调用、最终回复）。
- **工具范围**：任务可用的工具是「agent skills、plugins、flows、MCP servers」的子集。
- **生成的文件**（图表、文档、导出）随运行保存并可下载。
- 自动创建 **Scheduled Jobs 工作区**存放结果，支撑「Continue in Thread」按钮。
- **推送通知**：任务完成时可发浏览器通知。
- **对话式创建**：启用 `Create Scheduled Jobs` agent skill 后可直接说「@agent every weekday at 9am, summarize my inbox and email me a digest」，Agent 会建好任务并给出可点击的卡片。**该技能同样是单用户模式限定。**

> ⚠️ 单用户模式限定意味着：**AnythingLLM 的 Scheduled Jobs 无法用于多用户团队部署**。这是它掉出第一梯队的主因。

#### 4.5.2 执行 sudo / systemd（R3）

- 内置技能清单里有 **File System Agent**（文件系统 Agent），另有 Web Browsing、Web Scraper、Document Generation、SQL Agent、Gmail Agent、Google Calendar Agent、Outlook Agent。（证据 B）
- MCP 兼容（见下），因此可挂特权 MCP 服务器。
- 未发现官方文档描述「宿主 shell / 系统命令」能力。判为 ⚠️（需 MCP）。（证据 B）

#### 4.5.3 可视化输出（R4）

- 生成的文件（**图表**、文档、导出）随运行保存，可下载。（证据 A）
- 拖拽上传、来源引用、浏览器扩展、会议助手、桌面助手。（证据 B）

#### 4.5.4 知识库（R5）

- 内置 Agent、多用户、**向量数据库**、**文档管道**，开箱即用。
- 支持的向量库包括 PGVector 等（README 有完整清单）。
（证据 B）

#### 4.5.5 MCP 与网络搜索（R6）

- **MCP 兼容**，配置文件是 `mcpServers` JSON，使用 **stdio** 形态（`command` + `args`）。（证据 A）

```json
{
  "mcpServers": {
    "face-generator": {
      "command": "npx",
      "args": ["@dasheck0/face-generator"],
      "anythingllm": { "autoStart": false }
    },
    "mcp-youtube": { "command": "mcp-youtube", "args": [] }
  }
}
```

- `autoStart: false` 可让某个 MCP 服务器不随其他服务器自动启动（用于资源紧张或按需启动）。
- **网络搜索**：内置（Web Browsing / Web Scraper 技能）。（证据 B）

> ⚠️ AnythingLLM 的 MCP 是 **stdio**，而 Open WebUI 主产品只支持 **Streamable HTTP**——两者对同一批本地 MCP 服务器的适配方向相反。

---

### 4.6 Dify

**定位**：`langgenius/dify` 158,190★，TypeScript，2023-04-12 创建，2026-10-12 最后推送。LLM 应用开发平台，工作流画布为核心。

#### 4.6.1 周期任务（R2）— Schedule Trigger

证据等级 **A**，官方文档完整。

- **仅 Workflow 应用可用**；**每个工作流最多一个 schedule trigger**。
- 触发方式：默认可视化选择器，或 **cron 表达式**。配置后能看到**接下来 5 次**执行时间。
- cron 为**五字段**（分 时 日 月 周），支持 `*`、`,`、`-`、`/`、`L`、`?`，以及 `@yearly`/`@monthly`/`@weekly`/`@daily`/`@hourly`。
- **当「日」与「周」字段同时指定时，匹配任一即触发**（官方示例：`1 2 3 4 4` 会在 4 月 3 日**以及** 4 月的每个周四触发）。
- 触发不产生输出变量，但会更新系统变量 `sys.timestamp`。
- 自托管文档路径同样存在（`/self-host/use-dify/nodes/trigger/schedule-trigger`），说明非云版也可用。
- 测试：「Run this step」立即忽略排期执行；「Test Run」等待下次排期时间。

> ⚠️ 「每个工作流最多一个 schedule trigger」是个真实的架构约束——想在一个流程里做「每天 3 点」+「每小时」两种排期，必须拆成两个工作流。

#### 4.6.2 执行 sudo / systemd（R3）— 明确不可能

证据等级 **A**，官方原文：

> *"Code executes in a strict sandbox that prevents file system access, network requests, and system commands."*

- Code 节点执行 Python 或 JavaScript，跑在**独立容器**里，与宿主和其他服务隔离。
- Python 可用标准库（`json`、`math`、`datetime`、`re`）；可导入 numpy、pandas、requests 等**预装在沙箱里的**依赖。
- 网络：默认出站调用走 SSRF 代理；`SANDBOX_ENABLE_NETWORK=false` 可完全禁网。
- 可调：`SANDBOX_*`（worker 超时、网络、端口）、`CODE_*`（输出限额）。
- 输出按 API 容器上的限额校验。

结论：**Dify 的代码节点在设计上就排除了系统命令**。R3 必须靠 MCP 工具或外部服务。判为 ❌。（证据 A）

#### 4.6.3 可视化输出（R4）

工作流画布（拖拽节点构建数据流与任务处理）。（证据 B）

#### 4.6.4 知识库（R5）

- 一等公民：知识库是核心资源类型之一，有独立的管理界面与检索配置。
- 支持 RAG 全链路（切分、索引、检索、重排）。
（证据 B）

#### 4.6.5 MCP 与网络搜索（R6）

- **可把 Dify 应用发布为 MCP Server**（文档路径 `/self-host/use-dify/publish/publish-mcp`），并可对接 Claude Desktop、Cursor 等客户端。（证据 B）
- 插件机制 + 工具节点生态。（证据 B）
- 网络搜索：通过工具节点实现。（证据 B）

---

### 4.7 Suna / Kortix

**定位**：`kortix-ai/suna` 20,267★，TypeScript，2024-10-05 创建，2026-10-12 最后推送。自我定位已明确对标 *"an open-source, self-hosted alternative to Claude Cowork or ChatGPT Work"*。

#### 4.7.1 周期任务（R2）— cron + 签名 Webhook

证据等级 **B**（README 原文）：

- *"A trigger starts a session on a cron schedule or a signed webhook, with nobody present."*
- README 给出配置示例：

```yaml
type: cron
cron: '0 0 9 * * 1-5'
```

- 触发层能力表：*"**Triggers** | Cron and signed webhooks that spawn sessions automatically — every morning, or the instant something happens."*

#### 4.7.2 执行 sudo / systemd（R3）— 云沙箱，不是你的机器

- *"The agents work on real **cloud computers** — an isolated sandbox per session, on its own branch"*
- *"Every **session** gets its own **cloud computer** — a disposable, isolated Linux sandbox"*
- *"Run thousands of sandboxes in parallel on the same config, each fully isolated"*

所以 sudo/systemd 作用的是**会话沙箱**，不是你的宿主机。要碰你的机器得靠 connector / MCP。（证据 B）

#### 4.7.3 可视化输出（R4）

*"Agents run on real cloud computers and return finished work: **decks, reports, code and replies**."*（证据 B）

#### 4.7.4 知识库（R5）

*"One repo is the company: agents, skills, memory, connectors and triggers are files, versioned and diffable."*
*"**Memory** | A living company brain — plain files today, a system that compounds what it learns over time."*
（证据 B）

这是「知识库 = git 仓库里的纯文件」这一派，与 RAG 派不同：可 diff、可 code review、可回滚。

#### 4.7.5 MCP 与网络搜索（R6）

- *"The agent reaches 3,000+ apps through one scoped token, plus **MCP, OpenAPI, GraphQL and raw HTTP**."*
- *"**Connectors** | 3,000+ apps in a click — plus MCP, OpenAPI, GraphQL and raw HTTP. Credentials are brokered server-side through one scoped token and never enter the machine."*
（证据 B）

凭据由服务端代理、不进沙箱——这是本报告见到的较好的凭据隔离设计。

#### 4.7.6 部署

- `kortix self-host start` —— 一个 Docker Compose 栈；自托管免费。
- 托管云 $40/seat/月 + 用量。
- 可跑在 Kortix Cloud、你的 VPC、或你自己的内网。
（证据 B）

---

### 4.8 OpenHands

**定位**：`OpenHands/OpenHands` 90,642★（原 `All-Hands-AI/OpenHands`），TypeScript，**MIT**，2024-03-13 创建，2026-10-12 最后推送。自我定位已从「AI-Driven Development」演进。

#### 4.8.1 周期任务（R2）

证据等级 **B**，README 原文表格：

> *"| **Create automations** | Create automations and workflows that integrate with Slack, GitHub, Linear, and more. Run on a schedule or in response to webhook events |"*

以及：

> *"The Agent Server is often paired with an **Automation Server**, which lets you set up agents that run on a schedule or in response to events."*

配套仓库 `OpenHands/automation`（**37★**，Python，2026-03-13 创建，2026-10-12 最后推送，未归档），README 描述：*"Automation definitions, scheduling, webhooks, run history, and dispatching."*

> ⚠️ 注意配套仓库只有 **37★**、49 fork、2026-03 才创建。调度能力存在，但生态成熟度远低于主仓库。这是「主仓库 9 万星 ≠ 调度功能成熟」的典型案例。

#### 4.8.2 执行 sudo / systemd（R3）

OpenHands 的 Agent 跑在沙箱运行时里。README 未描述宿主特权执行。判为 ⚠️。（证据 B）

#### 4.8.3 其余

- 可视化：**Agent Canvas** + 预建自动化。（证据 B）
- 知识库：README 未描述内置知识库，依赖 MCP/工具。判为 ⚠️。（证据 C）
- MCP：支持。（证据 B）
- 网络搜索：未核实。（证据 C）

---

### 4.9 第二梯队速览

#### Khoj（37,646★，AGPL-3.0）

- **周期任务 ✅（证据 A）**：Automations 页面调度重复任务，**用本地时区**，结果**以邮件投递**；自托管需配 Resend 与 Authentication 才能发信。定位举例：自定义 newsletter、新闻摘要、事件提醒。
- **MCP ✅（证据 A）**：源码里存在 `src/khoj/processor/tools/mcp.py` 与数据库迁移 `src/khoj/database/migrations/0096_mcpserver.py`——说明 MCP 服务器是**持久化实体**，有数据模型。
- **知识库 ✅**：*"Create agents with custom knowledge, persona, chat model and tools to take on any role."*（证据 B）
- **R3 ❌**：无宿主 shell。邮件投递是它的动作出口，不是命令执行。

#### Onyx（32,409★）

- **知识库 ✅（本体）**：*"the knowledge/context layer for your team and AI agents"*，连接 50+ 应用索引知识，自称比 MCP 检索「更可靠、更低延迟、更低成本」。*"Instead of an agent coordinating and iteratively searching dozens of MCP and burning many thousands of tokens, Onyx fetches the context across its internal representation instantly."*
- **MCP ✅ 双向**：既能 *"Let Onyx agents take actions in external applications"*，也能 *"**MCP server** - Point Claude Code, Open Code, Codex, or any MCP client at Onyx."*
- **可视化 ✅**：Artifacts（生成文档、图形与其他可下载工件）+ Secure Sandbox。
- **网络搜索 ✅**：内置。
- **周期任务 ❌**：README 未提及任何调度能力。这是它落选第一梯队的原因。
- 技术栈：向量 + 关键词索引；后台容器跑任务队列与 worker 同步连接器；Redis + MinIO。Lite 模式 <1GB 内存但不能索引文档。社区版 MIT。（证据 B）

#### Sim（29,807★，Apache-2.0）

- *"Ingest files, knowledge bases, and structured table data"*、*"Monitor runs, logs, **schedules**, and workflow activity"*、*"Knowledge — your agents' memory"*。
- 有 **Desktop** 形态（Mac，含浏览器与终端）。
- 环境变量里有 `CRON_SECRET`，说明有定时基础设施。
- 本地 AI 走 Ollama，需要 12GB+ 内存。（证据 B）

#### LobeHub（83,152★）

- **周期任务 ⚠️（有硬限制，证据 B）**：定时任务文档明确 —— **在云端执行**；支持 **Daily / Weekly / Hourly**，**不支持 Monthly 或自定义 cron**；「Fixed interval」最短 10 分钟或 1 小时。
- 路径：任务详情 → Automation → Scheduled。
- *"10,000+ Skills"*、MCP Market、白盒记忆（structured, editable）、Docker/Vercel 自托管。
- **R3 ❌**：无宿主 shell。
- 仓库描述里的 "hiring, scheduling, and reporting on your entire AI team" 指的是**云端**的调度与汇报，不要理解为可以在你本机跑 cron。

#### Windmill（18,161★）

- **周期任务 ✅（证据 A）**：*"Scripts and flows can be triggered by **schedules**, webhooks, HTTP routes, Kafka, WebSockets, emails, and more."*
- **R3 ✅ 且是本表最完整的（证据 A/B）**：支持 **Python、TypeScript、Go、Bash、SQL、GraphQL、PowerShell、Rust、Ansible**；沙箱用 **nsjail** 做文件系统/资源隔离，**PID namespace 隔离默认开启**。
- **MCP ✅ 双向（证据 A）**：Windmill 可作 MCP 服务器（暴露 scripts/flows，含对 **Schedules** 的 CRUD）；官方原文 *"Windmill can also be the client rather than the server: an AI session chat calls the tools of the external MCP servers you connect to it"*。
- **知识库 ⚠️**：Resources / Variables 机制，非 RAG 知识库。
- 定位差异：Windmill 是**脚本平台**（*"Scripts are turned into sharable UIs automatically"*），不是 Agent 工作台。要 Agent 循环得用它的 AI sessions。

#### elizaOS（19,574★，MIT）

- README 提到 *"scheduled workflows, coding-agent orchestration, and installable app views"*、*"chat, voice, memory, knowledge, and document workflows"*、插件契约。
- 生态偏 Web3/社交代理，但架构上具备六项要素。（证据 B）

#### Letta（25,113★，Apache-2.0）

- 主仓库已迁至 `letta-ai/letta-code`（*"the agent harness, interactive terminal UI, App Server, channels, and the runtime used by the desktop and web apps"*）。
- **周期任务 ✅（证据 A）**：源码含 `src/backend/api/schedules.ts`、`src/cron/`（`cron-file.ts`、`index.ts`）、CLI 子命令 `cron`、`cron-task-ref`、`cron-scope`。
- **MCP ✅ 完整（证据 A）**：`src/backend/api/mcp-servers.ts`、`unified-mcp.ts`、`src/cli/commands/mcp.ts`、`src/cli/subcommands/mcp-connect.ts`，还有 `browser-device-mcp-oauth.ts`（浏览器设备码 OAuth）。
- 核心卖点是**状态化记忆**（memory that can learn and improve over time）。（证据 B）

#### FastGPT（29,799★）

- README roadmap 勾选了 **双向 MCP**。
- RAG 为核心；有工作流画布。
- 周期任务未核实。（证据 B/C）

#### Coze Studio（21,699★，Apache-2.0）

- 来自「Coze 开发平台」的开源核心引擎，一站式可视化 AI Agent 开发工具。
- 有 prompt、RAG、插件、工作流、知识库、数据库、记忆。
- **周期任务 ❌**：README 未提及调度。（证据 B）
- 最后推送 2026-07-29，落后主流行约 2.5 个月。

#### Goose（55,174★，Apache-2.0）

- *"an open source, extensible AI agent that goes beyond code suggestions - install, execute, edit, and test with any LLM"*
- **MCP ✅ 最强（证据 B）**：*"Connect to **70+ extensions** via the Model Context Protocol open standard."*
- 形态：macOS/Linux/Windows 原生桌面 App + CLI + API；Rust。
- **R3 ✅**：本地 CLI 形态直接跑在宿主上。
- **周期任务 ❌**：README 未发现调度器。这是它落选的原因——**它是最强的 MCP 宿主，但没有定时能力**。

---

## 第 5 章 「sudo 或 systemd」专项

这是六项需求里唯一没有开箱答案的一项。本章给出完整解法。

### 5.1 为什么没有工作台原生做这件事

三个原因，都是设计选择而非疏漏：

1. **容器化默认**。现代工作台默认 Docker 部署，容器内没有宿主的 systemd，`sudo` 也没有意义（进程通常已是 root）。
2. **多租户**。一旦工作台支持多用户（Open WebUI、LibreChat、AnythingLLM 都是），把宿主 shell 开放给任意用户等于把机器交出去。Open WebUI 甚至因此**禁止普通用户添加 MCP 服务器**。
3. **审计需求**。`sudo bash -c "..."` 不可审计；`systemctl restart nginx` 可审计。工作台层面很难做这个区分，MCP 服务端可以。

### 5.2 三条路径的实操

#### 路径 A：宿主 shell 直通

适用：单机、单用户、你自己就是唯一操作者。

| 工作台 | 配置要点 | 官方依据 |
|---|---|---|
| Open WebUI Computer | **裸装**（`pip install cptr && cptr run`），不用 Docker。Agent 的 `run_command` 即宿主 shell | *"full filesystem and shell access on a bare install"* |
| n8n | 恢复 Execute Command 节点（2.0 起默认禁用），或直接用 SSH 节点连目标机 | *"runs shell commands on the host machine that runs n8n"* |
| Agent Zero | 用 A0 CLI Connector 建立到宿主的终端桥 | *"a terminal-native bridge to your host machine"* |
| Goose | 本地 CLI 直接跑 | README |
| Windmill | Bash / PowerShell / Ansible 脚本 | README |

> ⚠️ **必须处理的 sudo 密码问题**。无人值守任务里 `sudo` 需要密码时会**阻塞到超时**。最小授权写法（不要用 `ALL`）：

```
# /etc/sudoers.d/cptr-agent   —— 只放开必要命令，且限定参数
cptr-agent ALL=(root) NOPASSWD: /usr/bin/systemctl restart nginx
cptr-agent ALL=(root) NOPASSWD: /usr/bin/systemctl status *, /usr/bin/journalctl -u nginx *
```

配套要点：
- `NOPASSWD` 条目里的命令**必须写绝对路径**。
- 通配符 `*` 在 sudoers 里能匹配空格，`systemctl status *` 实际等价于允许任意参数——要更严就得用固定参数或包一层白名单脚本。
- 用 `visudo -c -f /etc/sudoers.d/cptr-agent` 校验语法再生效。

#### 路径 B：MCP 桥接（推荐）

工作台保持非特权，特权操作交给专用 MCP 服务器。这份报告的前序调研（`研究报告_AI_Agent_Linux运维_全发行版.md`）已经找到了两个厂商级实现：

| 项目 | ★ | 语言 | 许可证 | 关键机制 |
|---|---:|---|---|---|
| **`rhel-lightspeed/linux-mcp-server`** | **317** | Python | Apache-2.0 | `CommandSpec` 硬编码元组 + 具名占位符（`{service_name}`），**不做 shell 插值**；`MappingProxyType` 冻结；端口工具 `ss`→`netstat` 自动回退；`auth_policy.py` 的 `PolicyRule(host, tools, claims, action)`，`action ∈ {deny, ssh_key, ssh_default, local}`；默认**失败即关闭** |
| **`openSUSE/systemd-mcp`** | 10 | Go | MIT | 直调 systemd C API（不拼 shell）；stdio 走 polkit、HTTP 走 OAuth2；**`--allow-write` 默认 false** |

选 `linux-mcp-server` 的三个理由：

1. **命令是硬编码元组，不是字符串拼接**。`CommandSpec` 用 `{service_name}` 这类具名占位符，从根上消除 shell 注入——这正是 CISA 归纳的那类漏洞（*"auth logic trusting a reconstructed path, a suffix match, or a fallback object instead of doing a hard check"*）的反面。
2. **策略可版本化**。`auth_policy.py` 读 YAML，规则是 `PolicyRule(host, tools, claims, action)`，工具模式支持 `*` / `-<tool>` / `@<group>` / `-@<group>`，还有 pydantic 语义校验器。这份 YAML 能进 git、能 code review。
3. **默认失败即关闭**。`LINUX_MCP_ALLOWED_LOG_PATHS` 未设时 `read_log_file` **什么都读不到**；SSH 只认密钥 + `LINUX_MCP_VERIFY_HOST_KEYS=True`。

> ⚠️ **两个必须知道的坑**：
> 1. `LINUX_MCP_TRANSPORT=http` **没有认证**。官方警告原文：*"should not be used in production or on untrusted networks."* 要用 HTTP 传输必须自己加一层反代 + 认证。
> 2. `LINUX_MCP_TOOLSET=run_script|both` 会打开「受保护命令执行」。它的三道护栏是 Gatekeeper LLM + 人工介入 + OS 沙箱（官方自称 *"rudimentary"*），硬编码策略是 **"No new repositories may be added"**、**"nothing may be downloaded from the internet"**（除预配置仓库）。**Gatekeeper 模型的评分表在官方文档里仍是 `??`（未公布）**——不要把它当唯一防线。

#### 路径 C：SSH 外发

- n8n **SSH 节点**（核心节点）→ 对多台目标机执行。
- 任意 SSH MCP 服务器 → 挂到支持 MCP 的工作台上。
- 优点：工作台与目标机解耦，一台工作台管 N 台机。
- 缺点：密钥权限往往过宽；建议在目标机侧配 `command=` 限制（`authorized_keys` 的 forced command）或用 `restrict` 选项。

### 5.3 sudo 与 systemd 的正确取舍：优先 polkit

如果目标是「让 Agent 能重启服务」，**不要给 sudo，给 polkit 规则**。理由：

| 维度 | sudo + NOPASSWD | polkit |
|---|---|---|
| 授权粒度 | 命令 + 参数（正则/通配） | **D-Bus 方法级**（如 `org.freedesktop.systemd1.manage-units`） |
| 是否需要密码 | NOPASSWD 才能无人值守 | 规则里 `auth_admin_keep` 或 `yes`，可按 subject 区分 |
| 绕过面 | 拿到该用户即可执行该命令 | 只能触发被授权的 D-Bus 调用 |
| 审计 | sudo 日志（可关） | journal 里可见调用方与主体 |
| 与 MCP 的契合 | 需拼命令 | `systemd-mcp` 已经这么做了 |

`openSUSE/systemd-mcp` 走的就是 polkit（stdio 传输），这是它在架构上比「给 Agent 一个 sudo shell」更正确的地方。

### 5.4 一张决策图

```
需要 Agent 操作 systemd/sudo
├─ 目标机就是工作台所在机？
│   ├─ 是 → 单用户？
│   │        ├─ 是 → 路径 A（Open WebUI Computer 裸装）+ sudoers 窄白名单
│   │        └─ 否 → 路径 B（MCP）
│   └─ 否 → 多台机？
│            ├─ 是 → 路径 C（n8n SSH 节点）或 路径 B + SSH 策略
│            └─ 否 → 路径 B（MCP，推荐）
└─ 需要写操作还是只读？
    ├─ 只读 → systemd-mcp 默认 --allow-write=false，零配置即安全
    └─ 写 → linux-mcp-server 的 auth_policy.yaml + 最小 action
```

---

## 第 6 章 推荐组合（按场景）

### 场景 A：单人 / 单机 / 要真机 sudo

**组合**：`Open WebUI Computer (cptr)` 裸装 + sudoers 窄白名单 + 可选接 `Open WebUI` 作前端。

```
pip install cptr
cptr run
# 浏览器打开输出的链接，建账号，打开工作目录
```

为什么选它：
- 唯一一个「跑在你真机上 + 有 RRULE 定时任务 + 有终端 + 有 stdio MCP + 有 git 面板」的开源方案。
- AI 可选：不配模型也能用文件/终端/git。
- 可加 Codex / Claude Code / Cursor / Grok / OpenCode / Cline / Pi 作原生后端，复用你已有的订阅。
- 可从手机访问，配合 Tailscale 保持私网。

代价：
- 官方明说 *"One trusted owner"*——**不要多人共用**。
- 无审计层，权限 = 你的权限。
- 许可证字段是 NOASSERTION，商用前读原文。

### 场景 B：团队 / 多机 / 要审计（推荐）

**组合**：`Open WebUI`（控制层）+ `Open Terminal`（动作层，需企业许可）+ `rhel-lightspeed/linux-mcp-server`（特权层）+ 任意 HTTP 桥（把 stdio MCP 转成 Streamable HTTP）。

三层职责：

| 层 | 组件 | 职责 |
|---|---|---|
| 控制层 | Open WebUI | 用户、权限、模型选择、提示词、知识库、Automations |
| 动作层 | Open Terminal / Terminals | 隔离工作区、文件、shell、包管理、预览；Terminals 做多用户编排与生命周期 |
| 特权层 | linux-mcp-server | 命令白名单、SSH 策略、日志路径白名单、默认失败即关闭 |

> ⚠️ **必须补的一环**：Open WebUI 主产品的 MCP **只支持 Streamable HTTP**，而 `linux-mcp-server` 默认是 stdio。你需要一层桥把 stdio 转成 HTTP。已知的桥包括 `mcpo`（MCP-to-OpenAPI 代理）一类工具；也可以用 Open Terminal 或 Computer 作为 stdio 宿主，再让 Open WebUI 通过 `cptr/<workspace>` 把 Computer 工作区当模型调用。

为什么选它：**权限落在 MCP 服务端，不在 Agent 手里**。这是六项需求里唯一能同时满足「可用」与「可审计」的组合。

### 场景 C：偏编排 / 已有大量脚本

**组合**：`n8n` + SSH 节点 + MCP Client 节点。

为什么选它：
- Schedule Trigger + Execute Command + SSH 都在同一张画布上，排期与执行的关系一眼可见。
- 双向 MCP：既能消费外部 MCP 服务器，也能把自己暴露给 Claude Code / Codex / Cursor。
- 207k 星、7 年历史、生态最厚。

代价：
- Execute Command **2.0 起默认禁用**，要改部署配置。
- 无内置知识库（只有向量库节点）。
- 自托管默认时区是 `America/New_York`，排期必须显式设时区。
- 定位是「固定流程图」，开放式推理不擅长。

### 场景 D：已有大量 MCP，要一个聊天工作台

**组合**：`LibreChat`。

为什么选它：
- **MCP 传输类型最全**：stdio / websocket / streamable-http / sse，四种全支持。
- Scheduled Chats 的工程质量最高：MongoDB 租约、幂等投递、防重叠、MCP 预检、夏令时处理、多副本协调、全局急停。
- MIT 许可证。
- RAG API + Artifacts + Code Interpreter（9 种语言）+ Skills + Subagents。

代价：
- Scheduled Chats 官方标为**实验性**。
- Code Interpreter 是沙箱，R3 仍需 MCP。
- 多副本必须配 Redis + `USE_REDIS_STREAMS=true`，否则排期写入 fail closed。

### 场景 E：要 Docker 隔离的自主 Agent

**组合**：`Agent Zero`（+ A0 CLI Connector 按需开宿主访问）。

为什么选它：
- 核心自带调度器（crontab 序列化 + 时区 + PlannedTask/AdHocTask 三种任务形态）。
- 200+ 插件索引，覆盖终端、SSH/S3/SMB/WebDAV 文件浏览、ripgrep、日志、Tailscale、人机审批门。
- Canvas 内是真 Linux 桌面，可跑 GUI 软件。
- 浏览器带 DOM 注解，能把视觉评论转成修复。

代价：
- 默认在 Docker 内，宿主 sudo 要额外开桥。
- 插件索引里没有调度插件，容易误判为「不能定时」（其实在核心）。

---

## 第 7 章 坑与反直觉

1. **Open WebUI 的 MCP 只有 Streamable HTTP，没有 stdio**。官方原文：*"Open WebUI's own MCP support is Streamable HTTP only."* 所有本地 stdio MCP 服务器都要桥接。反之 **Computer 原生支持 stdio**——同一家两个产品，MCP 传输能力相反。

2. **Open WebUI 的 MCP 服务器只能管理员添加**。*"Regular users cannot register their own, by design."* 非管理员的替代路径是管理员加一次 + 用 Access Control 按用户/组限权。

3. **把 `mcpServers` JSON 填进 OpenAPI 类型的连接会让 UI 崩溃或无限加载**。类型必须选 `MCP (Streamable HTTP)`。

4. **不设 `WEBUI_SECRET_KEY`，OAuth 连接的 MCP 工具每次容器重启都要重新认证**（`Error decrypting tokens`）。

5. **Open WebUI 主产品和 Computer 的知识库不互通**。*"Knowledge bases, prompts, and users don't transfer between the two."*

6. **Open WebUI 有两套定时任务**：主产品的 **Automations**（RRULE、`ENABLE_AUTOMATIONS`、按用户私有）与 Computer 的 **Scheduled tasks**（RRULE + Webhook + `{{webhook_payload}}`）。它们不是同一套，配置位置也不同。

7. **无人值守 = 全量审批放行**。Open WebUI 原文：*"Scheduled runs execute with full tool approval: nobody is there to click Allow."* 定时任务的工作区边界必须先想清楚。

8. **AnythingLLM 的 Scheduled Jobs 只在单用户模式可见**。多用户自托管实例**看不到这个设置页**。

9. **LobeHub 的定时任务在云端执行，且不支持 cron**。仅 Daily / Weekly / Hourly；「Fixed interval」最短 10 分钟或 1 小时。仓库描述里的 "scheduling" 指的是云端调度。

10. **n8n 的 Execute Command 自 2.0 起默认禁用**，且 Cloud 版没有这个节点。看到「n8n 能跑 shell」直接下结论是错的。

11. **n8n 自托管默认时区是 `America/New_York`**，不是 UTC 也不是本地。

12. **Dify 的代码节点在设计上就禁止系统命令**：*"prevents file system access, network requests, and system commands."* 且**每个工作流最多一个 schedule trigger**。

13. **Dify 的 cron 在「日」与「周」同时指定时是「或」不是「与」**。`1 2 3 4 4` 会在 4 月 3 日**和**每个周四触发。

14. **LibreChat 的 Code Interpreter 是沙箱不是宿主**，且沙箱**没有通用网络访问**。

15. **LibreChat 的 stdio MCP 必须在 `librechat.yaml` 里配**；管理员配置 API 会拒绝进程型条目，数据库覆盖也无法替换已有的进程型服务器。

16. **Agent Zero 容器内是 root，但不等于宿主 sudo**。容器 root 只在容器命名空间内有效。

17. **Agent Zero 的插件市场里搜不到「定时」插件，因为调度器在核心**（`helpers/task_scheduler.py`）。

18. **Suna 的沙箱是云电脑，不是你的机器**。sudo 作用在会话沙箱上。

19. **Windmill 的 MCP 是双向的**：既能作服务器暴露 scripts/flows（含 Schedules 的 CRUD），也能作客户端让 AI session 调用外部 MCP。

20. **Goose 有 70+ MCP 扩展但没有调度器**。MCP 最强 ≠ 六项齐全。

21. **OpenHands 主仓库 9 万星，但它的调度能力在只有 37 星的 `OpenHands/automation` 里**。主仓库星标不能代表子能力成熟度。

22. **6 个候选仓库改过名**，旧路径返回 301。批量检索必须跟随重定向。

23. **`sudo` 在无人值守任务里会阻塞在密码提示**。不是 bug，是 sudo 的设计。要么窄 `NOPASSWD`，要么走 MCP。

24. **sudoers 里的 `*` 能匹配空格**，`systemctl status *` 实际允许任意参数。要更严必须固定参数或包一层白名单脚本。

25. **`LINUX_MCP_TRANSPORT=http` 没有认证**，官方警告不要用于生产或不可信网络。

26. **`linux-mcp-server` 的 Gatekeeper 模型评分表在官方文档里仍是 `??`**，不要把它当唯一防线。

27. **Flowise 虽 5.5 万星但已归档**；AgentGPT、bytebot 同样已归档。星标高不等于活着。

28. **`github.com/api` 未认证配额是 60 次/小时（core）+ 10 次/分钟（search）**。批量检索 30 个仓库刚好够，但搜索接口很快就打满——本次实测中 3 次 search 调用即触发 `API rate limit exceeded`。检索前先用 `/rate_limit` 确认配额。

29. **Windmill 不是 Agent 工作台，是脚本平台**；要 Agent 循环得用它的 AI sessions。同样，n8n 不是 Agent 工作台，是带 AI 节点的自动化平台。

30. **「工作台」与「知识库」是两件事**。Onyx 的知识层是本体但它没有调度器；n8n 有调度器但知识库要自己拼。六项齐全的候选比想象中少。

---

## 第 8 章 未核实与覆盖边界

### 8.1 本轮未取得一手证据的项

| 项 | 状态 | 原因 |
|---|---|---|
| `Significant-Gravitas/AutoGPT` 的调度器 | 未核实 | 平台形态成立（187k★），但本轮未取得其 trigger 体系的官方文档 |
| OpenHands 的 MCP 细节与网络搜索 | 未核实 | README 仅提及支持，未取得传输类型与配置文档 |
| Sim 的 MCP 传输类型与网络搜索 | 未核实 | `docs.sim.ai` 返回空内容，仅有 README 佐证 |
| FastGPT 的周期任务 | 未核实 | README 未提及调度 |
| Letta 的宿主 shell 能力 | 未核实 | 仅有 MCP 通道，未找到直连宿主的文档 |
| elizaOS 的六项逐条核验 | 部分 | 仅 README 级别佐证，未逐项读官方文档 |
| Coze Studio 的插件/MCP 细节 | 部分 | README 提及插件机制，未取得 MCP 传输文档 |
| Activepieces 的六项能力 | 未核实 | 本轮仅取元数据（25,012★，2026-10-12 推送），未取证 |
| 各候选的许可证商业条款 | 未核实 | 多个仓库 `license.spdx_id` 为 `NOASSERTION`，需读许可原文 |

### 8.2 明确的方法论边界

1. **星标不能代表子能力成熟度**。本次实证：OpenHands 90k★ 主仓库 vs 37★ 的 automation 子仓库；n8n 207k★ 但 Execute Command 默认禁用。
2. **「未发现」不等于「不支持」**。表中所有 ❌ 均为「在官方 README/文档/源码树中未找到」，不等于该能力不存在于社区插件或未文档化的路径中。
3. **本次未做端到端实测**。所有能力断言均来自官方文档原文、README 原文或源码树文件名，未实际部署任一工作台执行 `sudo systemctl` 验证。
4. **未覆盖 SaaS/闭源方案**（Claude Cowork、ChatGPT Work、Coze 云版、LobeHub 云版等），用户需求是「工作台」且前序调研以自托管为主。
5. **未覆盖中文社区生态**（如国内厂商的 Agent 平台）。

### 8.3 与前序报告的关系

本报告是前序《AI Agent Linux 运维全发行版深度研究报告》的**横向补充**：前序报告解决「用 Hermes Agent 管 Linux 需要什么 MCP/Skills/知识库方案」，本报告解决「除 Hermes Agent 外还有哪些工作台可用」。两份报告的**执行层结论一致**：`rhel-lightspeed/linux-mcp-server`（317★）+ `openSUSE/systemd-mcp`（10★）是厂商级的特权执行层，任何工作台都应通过 MCP 挂载它们，而不是给 Agent 一个 sudo shell。

---

## 附录 A 证据分级说明

| 等级 | 含义 | 本报告的典型来源 |
|---|---|---|
| **A** | 官方文档原文 / 源码树直读，可复现 | Open WebUI MCP 文档原文；Agent Zero 的 `helpers/task_scheduler.py` 类清单；LibreChat Scheduled Chats 配置项；n8n `llms.txt` 索引 |
| **B** | 项目 README 原文 / 官方功能页 | Suna 的 cron 配置示例；Windmill 的触发方式列表；Onyx 的能力清单 |
| **C** | 项目自述但未独立复现，或仅有间接证据 | OpenHands 的 automations 表格；elizaOS 的能力描述 |
| **D** | 本报告推断 | 路径 A 的 sudo 阻塞分析；polkit 与 sudo 的对比 |

## 附录 B 可复现命令

### B.1 批量取候选元数据

```bash
# 先确认配额（未认证：core 60/小时，search 10/分钟）
curl -s "https://api.github.com/rate_limit"

# 取单个仓库元数据（注意 -L 跟随 301，本次实测 6 个仓库已改名）
curl -sL "https://api.github.com/repos/agent0ai/agent-zero" \
  | python -c "import sys,json;d=json.load(sys.stdin);print(d['full_name'],d['stargazers_count'],d['pushed_at'],d['archived'])"
```

### B.2 查源码树里的调度器

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

### B.3 取官方文档索引（比逐页抓更高效）

```bash
# n8n 文档索引（287 KB，可 grep MCP / SSH / vector store）
curl -sL "https://docs.n8n.io/llms.txt" | grep -iE 'mcp|ssh|vector store'

# Windmill 文档索引
curl -sL "https://www.windmill.dev/llms.txt" | grep -iE 'mcp|schedul'

# Open WebUI 文档 sitemap
curl -sL "https://docs.openwebui.com/sitemap.xml" | grep -oE '<loc>[^<]+</loc>' | grep -Ei 'schedul|mcp|automation'
```

### B.4 场景 A 的最小可行部署

```bash
# 1. 装 Open WebUI Computer（裸装，获得宿主 shell）
pip install cptr && cptr run
# 浏览器打开日志里输出的 http://localhost:8000/?token=...，建账号，打开工作目录

# 2. 窄授权 sudoers（不要用 ALL）
sudo tee /etc/sudoers.d/cptr-agent >/dev/null <<'EOF'
cptr-agent ALL=(root) NOPASSWD: /usr/bin/systemctl restart nginx
cptr-agent ALL=(root) NOPASSWD: /usr/bin/systemctl status nginx
cptr-agent ALL=(root) NOPASSWD: /usr/bin/journalctl -u nginx -n 100
EOF
sudo visudo -c -f /etc/sudoers.d/cptr-agent   # 必须先校验语法

# 3. 需要 stdio MCP 时补依赖
pip install 'cptr[mcp]'

# 4. 在 Settings → Admin → Tool Servers 加 MCP (stdio)，填 command/args/env/cwd
```

### B.5 场景 B 的最小可行部署

```bash
# 特权层：linux-mcp-server（stdio 默认）
uv tool install linux-mcp-server

# 关键：不设 ALLOWED_LOG_PATHS 时 read_log_file 什么都读不到（失败即关闭）
export LINUX_MCP_ALLOWED_LOG_PATHS=/var/log/nginx,/var/log/syslog
export LINUX_MCP_VERIFY_HOST_KEYS=True
# 不要开 LINUX_MCP_TRANSPORT=http —— 该传输没有认证

# 控制层：Open WebUI（MCP 只能加 Streamable HTTP）
# 注意必须设 WEBUI_SECRET_KEY，否则 OAuth MCP 每次重启都要重认证
export WEBUI_SECRET_KEY="$(openssl rand -hex 32)"
docker run -d -p 3000:8080 -e WEBUI_SECRET_KEY -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
# 然后在 Settings → Admin → Integrations 里以 MCP (Streamable HTTP) 类型添加桥接后的地址
```

## 附录 C 参考链接

### C.1 工作台官方文档

| 项目 | 文档入口 |
|---|---|
| Open WebUI | https://docs.openwebui.com/features/ |
| Open WebUI MCP | https://docs.openwebui.com/features/extensibility/mcp/ |
| Open WebUI Automations | https://docs.openwebui.com/features/chat-conversations/chat-features/automations |
| Open WebUI Computer | https://docs.openwebui.com/ecosystem/computer/ |
| Computer 定时任务 | https://docs.openwebui.com/ecosystem/computer/automate/scheduled-tasks |
| Computer MCP | https://docs.openwebui.com/ecosystem/computer/automate/tool-servers |
| Computer 技能与记忆 | https://docs.openwebui.com/ecosystem/computer/ai/skills-and-memory |
| Computer 审批 | https://docs.openwebui.com/ecosystem/computer/ai/approvals-and-plan-mode |
| Open Terminal | https://docs.openwebui.com/ecosystem/open-terminal/ |
| Agent Zero | https://github.com/agent0ai/agent-zero |
| Agent Zero 插件索引 | https://github.com/agent0ai/a0-plugins |
| n8n Schedule Trigger | https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.scheduletrigger/ |
| n8n Execute Command | https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/ |
| n8n MCP Server Trigger | https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/ |
| n8n 文档索引 | https://docs.n8n.io/llms.txt |
| LibreChat MCP | https://www.librechat.ai/docs/features/mcp |
| LibreChat Scheduled Chats | https://www.librechat.ai/docs/features/scheduled_chats |
| LibreChat Code Interpreter | https://www.librechat.ai/docs/features/code_interpreter |
| LibreChat MCP 配置 | https://www.librechat.ai/docs/configuration/librechat_yaml/object_structure/mcp_servers |
| AnythingLLM Scheduled Jobs | https://docs.anythingllm.com/scheduled-jobs/overview |
| AnythingLLM MCP | https://docs.anythingllm.com/mcp-compatibility/overview |
| Dify Schedule Trigger | https://docs.dify.ai/en/self-host/use-dify/nodes/trigger/schedule-trigger |
| Dify Code 节点 | https://docs.dify.ai/en/self-host/use-dify/nodes/code |
| Dify 发布为 MCP | https://docs.dify.ai/en/self-host/use-dify/publish/publish-mcp |
| Khoj Automations | https://docs.khoj.dev/features/automations/ |
| LobeHub 定时任务 | https://lobehub.com/docs/usage/agent/scheduled-task |
| Windmill MCP | https://www.windmill.dev/docs/core_concepts/mcp |
| Windmill 文档索引 | https://www.windmill.dev/llms.txt |
| OpenHands Automations | https://docs.openhands.dev/openhands/usage/agent-canvas/prebuilt-automations |
| OpenHands Automation Server | https://github.com/OpenHands/automation |

### C.2 前序报告（特权执行层）

| 项目 | 位置 |
|---|---|
| 全发行版研究报告（MD） | `研究报告_AI_Agent_Linux运维_全发行版.md` |
| 全发行版研究报告（HTML） | `研究报告_AI_Agent_Linux运维_全发行版.html` |
| 知识库条目 | `kb/hermes-openclaw-linux-ops-agent-stack.md` |

---

*报告完 · v1.0 · 2026-10-12 · 六项能力 × 19 个候选 × 官方文档逐条取证 · 证据分级见附录 A · 未核实项见第 8 章*
