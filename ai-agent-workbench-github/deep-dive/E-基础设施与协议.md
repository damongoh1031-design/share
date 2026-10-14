# E 类｜基础设施 / 运行时 / 协议（8 个）

> 这一类**不是"工作台"本身**，而是决定工作台能力上限的底座：连接、记忆、沙箱、观测。
> 2026 年协议层完成了标准化（MCP → Linux Foundation AAIF；A2A → Linux Foundation）。
> 数据快照：2026-10-14 · 标注 `[不确定]` 的为未能一手核实项

---

## 为什么这一类重要

如果你只看"工作台"，会漏掉一个关键事实：**2026 年 Agent 能力的跃迁几乎都发生在这一层**。

- 工作台能接多少外部工具？取决于 **MCP**
- 工作台之间怎么协作？取决于 **A2A**
- 工作台能安全执行代码吗？取决于 **E2B** 这类沙箱
- 工作台记得住你吗？取决于 **Mem0 / Letta** 这类记忆层
- 工作台能操作网页吗？取决于 **Browser Use**
- 工作台能调 1000+ 个 SaaS 吗？取决于 **Composio**
- 你能知道工作台为什么出错吗？取决于 **Langfuse**

**选型启示**：如果你在设计自己的 Agent 工作台，这一层是"买"而不是"造"的部分。

---

## 1. MCP（Model Context Protocol）

> **定位**：Agent 与外部工具之间的即插即用标准（"Agent 的 USB-C"）
> **仓库**：https://github.com/modelcontextprotocol/modelcontextprotocol · **Star**：9,448（规范仓库） · **License**：MIT（官方 SDK 与多数子仓库）；规范仓库 GitHub 识别为 Other · **语言**：TypeScript（规范）+ 多语言 SDK · **维护方**：原 Anthropic 主导，2025-12 捐给 Linux Foundation 旗下 **Agentic AI Foundation（AAIF）** · **状态**：✅ 高度活跃

### 它是什么

MCP 解决的是 Agent 生态里最基础的工程问题：**N×M 适配器爆炸**。

在没有标准之前，你想让 Agent 连接 GitHub、Slack、数据库、文件系统……每接一个系统就要写一套定制胶水代码；而 M 个 Agent 框架 × N 个外部系统 = M×N 个适配器。MCP 把这个矩阵**降维成 M+N**：外部系统实现一个 MCP Server，所有支持 MCP 的客户端都能用。

它的架构很直接：**Client-Server + JSON-RPC 2.0**，定义三大原语：
- **Tools**：可执行函数（如 `send_email`、`query_db`）
- **Resources**：可读取的上下文数据
- **Prompts**：提示词模板

2025 年 12 月，Anthropic 把 MCP 捐赠给 **Linux Foundation 旗下的 Agentic AI Foundation（AAIF）**，创始成员含 Anthropic、OpenAI、Block、Google、Microsoft 等 30+ 企业。**这标志着 MCP 从"Anthropic 的协议"变成了"行业的协议"**——也是 2026 年最重要的一次生态事件。

### 核心架构与编排范式

- **Client-Server 架构**：AI 应用作 Client，工具/数据源作 Server
- **JSON-RPC 2.0** 通信协议
- **三大原语**：Tools / Resources / Prompts
- **传输层双模**：本地 **stdio** 进程 + 远程 **Streamable HTTP**（含 SSE）
- **2026 年规范演进**：推进无状态化，便于水平扩展与企业网关部署
- **不负责多 Agent 编排**（该职责交给 A2A 等上层协议）

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | ⭐ **协议核心即工具调用**；Server 通过 `list_tools` / `call_tool` 暴露与执行工具 |
| **记忆机制** | 协议不内置记忆；官方参考实现提供 Memory Server 示例（基于知识图谱） |
| **MCP 支持** | 协议本身即 MCP（原生） |
| **沙箱/执行** | 无内置沙箱；代码执行类 Server（如 E2B）需自行提供隔离环境 |
| **人机协作** | 协议本身无审批原语，人工确认由宿主/Client 层实现（如 elicitation 请求用户补充输入） |
| **RAG** | 不内置 RAG；通过 Resources 原语向模型注入上下文数据 |

### 快速上手

MCP 的使用方式极其简单——**写一段 JSON 配置**即可，无需编码：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem",
               "/Users/username/Desktop", "/Users/username/Downloads"]
    }
  }
}
```

**配置文件位置**：
- macOS：`~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows：`%APPDATA%\Claude\claude_desktop_config.json`

改后**完全重启** Claude Desktop。
**前置要求**：客户端（如 Claude Desktop）+ **Node.js**（npx 运行 server）。
**上手难度**：★★☆☆☆ —— 只需写 JSON 配置，无需编码。

### 差异化特色

1. **Client-Server 架构 + 三大原语 Tools/Resources/Prompts**，统一了模型与外部世界的连接方式
2. **传输层同时支持本地 stdio 与远程 Streamable HTTP（含 SSE）**；2026 年规范演进推进无状态化，便于水平扩展与企业网关部署
3. **2025-12 捐赠至 Linux Foundation 旗下 AAIF**，OpenAI/Google/Microsoft 等共同支持，成为跨厂商事实标准
4. **生态规模庞大且高度分散**

### ⚠️ 生态规模的数据口径问题

关于"MCP 生态有多少 Server"，**不同来源差异极大，必须谨慎对待**：

| 口径 | 数量 | 时间 |
|---|---|---|
| 官方 Registry | 约 9,652 条 | 2026-05 |
| Glama 索引 | 66,701 | 2026-08 |
| GitHub `mcp-server` 话题仓库 | 15,926 | 2026-05 |
| 33 个注册表去重后 | 约 12,000+ | — |
| 媒体广泛报道 | "破 10 万 Server" | 2026-07 |

> ⚠️ **媒体报道的"破 10 万 Server"与官方 Registry ~9,652 口径严重不符，疑为多目录聚合或夸大。** 建议采用官方 Registry 口径。

### 局限与风险

1. **生态质量参差**：arXiv 论文《Exposed by Design》对 414 个公网 Server 审计显示 **91.8% 未启用 OAuth**；BlueRock 对 7,000 个的扫描显示 **36.7% 远程 Server 存在潜在 SSRF 风险**；41.6% 已确认 Server 三天内离线
2. **工具过多易触发"工具幻觉"与上下文污染**，需动态工具路由 + 工具输出摘要（如用小模型压缩结果）
3. 规范/治理主体已迁移至 AAIF，生态分散在 servers 与多语言 SDK 等子仓库，**版本与兼容性管理成本较高**

### 生态与社区

生态由 **33+ 个注册表**构成（官方 Registry、Glama、PulseMCP、Smithery、MCP.so 等）；月 SDK 下载量约 **5 亿**（Tier1 口径，Anthropic 2026-07 公告）；组织生产环境采用率 **41%**（Stacklok 2026 调查）。
**知名采用方**：OpenAI、Google、Microsoft、Block、GitHub（官方 Go 实现 Server，29,000+ stars）、Salesforce（含 OAuth2.1 + 多租户 + 审计日志的企业级参考实现）、Stripe、Cloudflare、AWS（Bedrock AgentCore 贡献 Tasks 扩展）。

### 适合谁 / 典型场景

工作台/IDE/桌面客户端（Claude Desktop、Cursor、VS Code）统一接入 GitHub、Slack、Notion、数据库、文件系统等外部工具；企业部署统一 **MCP Gateway**，集中做鉴权、限流、日志审计与计费；把内部系统封装为 MCP Server，供多种 Agent 复用。

---

## 2. A2A（Agent2Agent）

> **定位**：Agent 间协作协议（"Agent 的 TCP/IP"）
> **仓库**：https://github.com/a2aproject/A2A · **Star**：26,141 · **License**：Apache-2.0 · **语言**：规范 + 多语言 SDK（Python/JS/Java/.NET/Go/Rust） · **维护方**：Google 发起（2025-04），已捐给 Linux Foundation · **状态**：✅ 高度活跃（v1.0 推进中）

### 它是什么

如果 MCP 解决的是"Agent 怎么连接工具"，那 A2A 解决的是"**Agent 之间怎么协作**"。

现实场景是：你的采购 Agent 需要向外部供应商的报价 Agent 询价。这两个 Agent 可能由不同公司开发、用不同框架实现、互不知道对方内部细节。A2A 让它们能**互相发现、委托任务、同步状态**——而且**不需要暴露内部实现**（"黑盒协作"）。

两个核心机制：
- **Agent Card**（`/.well-known/agent.json`）：Agent 的"能力名片"，声明技能、输入输出模态与鉴权方式——**类似 DNS**
- **Task 生命周期状态机**：`submitted → working → input-required → completed/failed` + **Artifact** 产物交付

生态层面，A2A 已纳入 **Linux Foundation**，且 **IBM 的竞争协议 ACP 已合并入 A2A**，推动生态统一。

### MCP 与 A2A 的分工（重要）

| | MCP | A2A |
|---|---|---|
| 解决的问题 | Agent ↔ **Tool** | Agent ↔ **Agent** |
| 比喻 | Agent 的 **USB-C** | Agent 的 **TCP/IP / HTTP** |
| 层次 | 微观执行层 | 宏观协作层 |
| 发起方 | Anthropic（2024-11） | Google（2025-04） |
| 治理 | Linux Foundation / AAIF | Linux Foundation |
| 关系 | **互补而非竞争** | |

两者共同构成 2026 年的"AI Agent 标准协议栈"：**上层 A2A、下层 MCP、底座 LLM & RAG**。

### 核心架构与编排范式

- **多 Agent 协作范式**：Agent Card 能力发现 + Task 生命周期状态机 + Artifact 产物交付
- **协议绑定灵活**：支持 JSON-RPC / gRPC / HTTP+JSON 多种绑定
- **流式与异步**：支持基于 SSE 的流式与异步长任务交付
- **黑盒协作**：调用方无需知道被调用方的内部实现

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 不直接定义工具调用；通过 Task/Skill 调用远端 Agent 的能力，工具/数据接入交由 MCP 完成 |
| **记忆机制** | 协议无内置记忆；任务上下文通过 Task 与 Artifact 在调用方与被调用方之间传递 |
| **MCP 支持** | 与 MCP 互补（社区有 a2a-mcp 桥接方案） |
| **沙箱/执行** | 无沙箱/执行环境能力 |
| **人机协作** | ✅ Task 状态机含 `input-required` 状态，支持在任务执行中请求人工/外部补充输入 |
| **RAG** | 无 RAG/知识库能力 |

### 快速上手

```bash
# 多语言 SDK
pip install a2a-sdk                     # Python
npm install @a2a-js/sdk                 # JS
go get github.com/a2aproject/a2a-go     # Go
# Java: Maven；.NET: dotnet add package A2A；Rust: cargo add a2a-lf
```

**形态示意**（具体 API 请参考官方 samples `github.com/a2aproject/a2a-samples`）：
```python
# 服务端：定义 AgentCard + AgentExecutor，挂载到 ASGI app
# 客户端：A2AClient 读取对方 AgentCard → 发送 task
```

**前置要求**：无特殊依赖；按语言选择 SDK。
**上手难度**：★★★☆☆ —— 协议概念（Agent Card、task 生命周期）+ SDK 学习曲线。
**中文支持**：README 提供多语言入口（含**简体中文/繁體中文**的翻译链接）。

### 差异化特色

1. **Agent Card（`/.well-known/agent.json`）能力发现机制**，声明技能、输入输出模态与鉴权方式，类似 DNS
2. **标准化 Task 生命周期状态机 + Artifact 产物交付**，实现跨组织"黑盒协作"
3. **支持 JSON-RPC / gRPC / HTTP+JSON 多种协议绑定**，并支持 SSE 流式与异步长任务
4. **已纳入 Linux Foundation**；IBM 的竞争协议 ACP 已合并入 A2A

### 局限与风险

1. **生态与采用度明显小于 MCP**（26k Star vs MCP 生态数千至数万 Server），落地案例仍以 Google 及云厂商为主
2. **v1.0 GA 精确时间说法不一**（一说 2026-03 规范里程碑，一说 2026-07 正式 GA），需以官方发布为准
3. 跨组织调用面临网络不确定性：超时、重试、指数退避、全局 Task Timeout，以及信任/鉴权（OAuth2）复杂度较高

### 生态与社区

由 Google 主导并联合多家云厂商；`a2aproject` 组织提供 a2a-python / a2a-js / a2a-java / a2a-dotnet 等多语言 SDK；与 DeepLearning.AI 合办课程。
**知名采用方**：Google（发起方）、Microsoft、IBM（合并 ACP 入 A2A）、Salesforce、SAP 及多家云厂商。可对接 Google ADK、LangGraph、BeeAI 等框架。

### 适合谁 / 典型场景

跨组织 Agent 协作（采购 Agent 通过 A2A 调用外部供应商报价 Agent）；异构多 Agent 互通（让基于 LangChain 与 AutoGen 等不同框架开发的 Agent 互相通信）；企业内多 Agent 能力目录与任务编排。

---

## 3. Browser Use

> **定位**：让 Agent 像人一样操作浏览器的最流行开源库
> **仓库**：https://github.com/browser-use/browser-use · **Star**：117,914 · **License**：MIT · **语言**：Python · **维护方**：Browser Use 公司（美国，YC W25） · **状态**：✅ 高度活跃（2.x，0.13.11 / 2026-10-07）

### 它是什么

Browser Use 是 E 类里 Star 最高的项目（117,914），它解决的是"**Agent 怎么操作网页**"。

它代表的是**"DOM + Vision 混合感知"路线**——与 UI-TARS 的"纯视觉坐标点击"路线相对：
- 底层经 **Playwright → CDP** 驱动 Chromium
- 解析**结构化 DOM / 可访问性树**，辅以视觉信息
- 采用**语义定位器**：2.0 版本把动作抽象从 `click(xpath=...)` 升级为 `click('search button')`，显著提升跨页面改版的鲁棒性

这个路线的优势是**精确、便宜、可解释、失败可诊断**；局限是**只能操作网页**（无法操作桌面应用或无 DOM 的 canvas）。

业界正在收敛："**有结构用结构，无结构用像素**"——UI-TARS 的 Agent TARS 已推出 GUI+DOM 混合模式，Browser Use 类项目也把截图贴在 DOM 旁。

### 核心架构与编排范式

- **单 Agent 循环**：任务规划 → 感知页面（DOM + Vision）→ LLM 推理 → 执行动作 → 观察结果 → 循环
- **内置自我纠正/重试机制**：检测到错误时可重试或调整策略
- **可作为 MCP Server** 暴露给其他 Agent 调用
- **云托管**：提供托管的浏览器与优化模型

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 提供高层动作抽象（click/type/scroll/提取等）；可作为 MCP 工具暴露；支持扩展自定义动作 |
| **记忆机制** | 支持短期会话上下文与可配置的 Agent 记忆（历史步骤/状态） |
| **MCP 支持** | ✅ 支持（可作为 MCP Server 被其他 Agent 调用） |
| **沙箱/执行** | 浏览器级隔离：本地启动独立 Chromium 实例（经 Playwright/CDP 控制），云版提供托管沙箱 |
| **人机协作** | 支持敏感操作确认与人工接管/干预 |
| **RAG** | 无内置 RAG；但具备网页内容提取能力可对接外部检索 |

### 快速上手

```bash
pip install browser-use
playwright install chromium
```

```python
from browser_use import Agent
from langchain_openai import ChatOpenAI
import asyncio

async def main():
    agent = Agent(task="Find the top HN story", llm=ChatOpenAI(model="gpt-4o"))
    await agent.run()

asyncio.run(main())
```

> ⚠️ 安装命令与示例为通用形态，本次未直接核实官方页面。

**前置要求**：Python 3.11+；LLM API Key（OpenAI/Anthropic/Gemini 等）。
**上手难度**：★★☆☆☆ —— pip 安装 + 少量代码即可跑通。

### 差异化特色

1. **DOM + Vision 混合感知路线**：解析结构化 DOM/可访问性信息并辅以视觉，非纯视觉坐标点击
2. **2.0 动作抽象升级**：从 `click(xpath=...)` 改为**语义定位** `click('search button')`，提升跨页面改版鲁棒性
3. **内置自我纠正机制**，检测到错误时可重试或调整策略
4. **提供自研 ChatBrowserUse 优化模型与云托管服务**，降低对通用大模型的依赖

### 局限与风险

1. **Token 消耗较高**：DOM 树体量大，长任务上下文成本显著
2. 复杂/强动态或强反爬页面稳定性有限，需重试与人工兜底
3. 依赖浏览器运行环境，云版有额外成本；作为 Python 库对非开发者有使用门槛

### 生态与社区

13,059 forks、480 watchers（2026-10-14）。发布说明显示新增 **Browser Use toolsets for Claude**（`browser_use.integrations.toolsets_for_claude`，需 Anthropic SDK 支持 `anthropic.tools.browser`）；支持 **MCP**（含安全开关）；支持多 provider（OpenAI/Anthropic/Gemini/Mistral/DeepSeek/Bedrock/OpenRouter 等）。
被众多 Agent 框架与工作台作为网页操作组件集成（如 OpenManus 默认集成）。

### 适合谁 / 典型场景

Web 数据采集与表单自动填写（批量提交、抓取）；UI 自动化测试（作为 Playwright 的 AI 上层封装）；电商比价、预订、报销填报等网页任务自动化。

---

## 4. Mem0

> **定位**：通用 Agent 记忆层（drop-in memory infrastructure），可插入任意 Agent 框架
> **仓库**：https://github.com/mem0ai/mem0 · **Star**：67,149 · **License**：Apache-2.0 · **语言**：Python · **维护方**：Mem0（美国，YC S24） · **状态**：✅ 非常活跃（Node SDK ts-v3.3.1 / 2026-09-25）

### 它是什么

Mem0 是"**记忆中间件**"路线的代表：它不做 Agent 编排，只做记忆——你可以把它**插入任何 Agent 框架**（LangChain、CrewAI、自研 Agent）给它加上跨会话长期记忆。

它的写入流程是：**上下文查重 → LLM 抽取事实 → 去重与 embedding → 实体抽取与链接**，分别落到三个库：SQL（事实与元数据）、向量库（embedding）、实体库。

检索时用**多信号并行混合检索**：语义向量 + BM25 关键词 + 实体匹配 + 时间感知排序。

这个路线与 Letta 的"OS 式分层记忆"形成对比——Mem0 是"**无状态的事实抽取层**"，Letta 是"**有状态 Agent 的运行环境**"。两者互补：想要轻量给现有应用加记忆 → Mem0；想要完整的有状态 Agent 运行时 → Letta。

### ⚠️ 三个必须知道的问题

**① 基准数字可信度存疑**
官方论文（arXiv:2504.19413）声称在 LOCOMO 上相对 OpenAI Memory 提升 26%、p95 延迟降低 91%、token 成本节省超 90%。但官方自己声明：高分"**仅适用于托管平台（含开源 SDK 不具备的专有优化）**"——**开源版跑不出宣传分数**。且 Zep、Hindsight、Honcho 三方公开质疑 LOCOMO 的可比性，**无独立第三方复现验证**。

**② 中文场景硬伤**
BM25 关键词搜索与实体抽取**硬编码为英文**（issue #4884）——中文用户需特别注意。

**③ v3 的副作用**
v3 改为单遍 ADD-only 管线（取消 UPDATE/DELETE），简化了写入并提升吞吐，但在 **batch embedding 部分失败时会静默丢记忆**（issue #5245）；Graph Memory 已从开源版移至托管平台。

### 核心架构与编排范式

- **自身不做编排**，是记忆中间件；可嵌入 LangChain、CrewAI 等各类 Agent 框架与自研 Agent
- **三库架构**：SQL（事实+元数据）/ 向量库（embedding）/ 实体库
- **混合检索**：语义向量 + BM25 + 实体匹配 + 时间感知排序

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 对外提供记忆读写接口（add / search / get / update），可作为"记忆工具"接入 Agent 的工具列表 |
| **记忆机制** | ⭐ **核心产品**：上下文查重 → LLM 抽取事实 → 去重与 embedding → 实体抽取与链接 |
| **MCP 支持** | ✅ 支持（提供 Mem0 的 MCP Server，便于在 MCP 客户端中调用记忆能力） |
| **沙箱/执行** | 无 |
| **人机协作** | 弱：支持对记忆条目进行查看/增删改，但无审批或步骤回放式的人机协作机制 |
| **RAG** | ✅ 内置多信号并行混合检索 |

### 快速上手

```bash
# 库
pip install mem0ai
# 增强混合检索（需下载 spacy 模型）
pip install mem0ai[nlp] && python -m spacy download en_core_web_sm
npm install mem0ai

# 自托管
cd server && make bootstrap
# 或
cd server && docker compose up -d      # localhost:3000

# 云平台：app.mem0.ai 注册获取 key
# CLI
npm install -g @mem0/cli    # 或 pip install mem0-cli
mem0 init --agent --agent-caller claude-code
```

```python
from mem0 import Memory
memory = Memory()  # 默认 gpt-5-mini + text-embedding-3-small
relevant = memory.search(query="What does the user prefer?", filters={"user_id": "alice"}, top_k=3)
memory.add([{"role": "user", "content": "I prefer dark mode"}], user_id="alice")
```

**前置要求**：需 LLM（默认 OpenAI `gpt-5-mini`）+ Embedding（默认 `text-embedding-3-small`），故需 **OpenAI API Key**（或改用其他 LLM/Embedder）。
**上手难度**：★★☆☆☆ —— 两三行即可 add/search。

### 差异化特色

1. **事实抽取 + 混合检索路线**（语义向量 + BM25 + 实体匹配 + 时间感知），是"事实抽取派"代表方案
2. **v3 改为单遍 ADD-only 管线**，简化写入并提升吞吐（但副作用见上文）
3. **产品形态齐全**：开源库 / 自托管 / 云三档并存，可无缝替换
4. 官方论文声称 LOCOMO 相对 OpenAI Memory 提升 26%、p95 延迟降低 91%

### 局限与风险

见上文"三个必须知道的问题"——基准可信度、中文硬编码、v3 静默丢记忆。

### 生态与社区

67,149 stars、7.9k forks、255 watchers；生态广泛（多语言 SDK、框架集成）。
**集成情况**：LangGraph、CrewAI 等；提供 Agent Skills（Claude Code、Cursor、Windsurf 等）。

### 适合谁 / 典型场景

为客服/助手类应用注入跨会话用户偏好与历史事实记忆；在既有 Agent/RAG 系统中加装可插拔的长期记忆层；个性化推荐与用户画像的持久化记忆管理。

---

## 5. Letta（原 MemGPT）

> **定位**：面向开发者的"有状态 Agent 运行时 / 记忆操作系统"
> **仓库**：https://github.com/letta-ai/letta · **Star**：25,125 · **License**：Apache-2.0 · **语言**：Python · **维护方**：Letta（源自 UC Berkeley MemGPT 论文团队，美国） · **状态**：✅ 活跃维护

### 它是什么

Letta 的前身是 **MemGPT**——那篇著名论文提出了一个类比：**把 LLM 当 CPU、把上下文窗口当内存、把外部存储当磁盘**。Agent 像一个操作系统一样，自主管理"什么留在内存里、什么写回磁盘"。

这个"OS 式分层记忆"是 Letta 的核心差异化：

- **core memory（核心记忆）**：常驻上下文，按 block 组织（典型为 persona 与 human 两个 block）。**关键特性：Agent 会随对话自我改写这些 block**——这就是"跨会话身份连续性"的来源
- **archival memory（归档记忆）**：向量库长期记忆，按需检索
- **recall memory（回溯记忆）**：对话历史回溯

它还有一个很有意思的机制：**sleep-time compute**——在非交互时（"睡眠"时）后台自主整理记忆、提炼图谱、合并相似上下文。把"重活"下沉到异步巩固，而不是占用对话时的算力。

它提供 **ADE（Agent Development Environment）** 可视化界面，让你能**查看和直接编辑 Agent 的记忆块**——这对调试有状态 Agent 非常重要。

> ⚠️ **2026 年重要变化**：原 `letta-ai/letta` 仓库的 V1 API server 已归档（`archive` 分支），活跃源码迁至 **`letta-ai/letta-code`**，主入口变为 `npm install -g @letta-ai/letta-code` → `letta`。

### 核心架构与编排范式

- **单 Agent 循环**为核心，强调 Agent 自主调度自身记忆
- **sleep-time compute**：睡眠时后台整理记忆
- **记忆更新由 Agent 自主调用内部工具完成**（如 `core_memory_append` / `core_memory_replace` / `archival_memory_insert` / `archival_memory_search`）
- **ADE 可视化**：查看/编辑记忆块

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置记忆管理工具（`core_memory_append` / `core_memory_replace` / `archival_memory_insert` / `archival_memory_search` / `conversation_search`）；支持自定义工具与代码执行 |
| **记忆机制** | ⭐⭐ **核心差异化：分层记忆（OS 式）**——core / archival / recall 三层 + sleep-time compute |
| **MCP 支持** | ✅ 支持（可将外部 MCP 工具接入 Agent） |
| **沙箱/执行** | 支持工具调用与代码执行（可运行自定义工具），具体隔离机制需查文档 |
| **人机协作** | ✅ ADE 可视化界面允许人查看与直接编辑 Agent 的记忆块，实现人工干预/接管 |
| **RAG** | 通过 archival memory 的向量检索实现长期记忆召回；非通用 RAG 知识库平台 |

### 快速上手

```bash
npm install -g @letta-ai/letta-code
letta          # 启动终端 UI
letta server   # 启动 App Server
```

**其他形态**：桌面 App（macOS/Windows/Linux）、`chat.letta.com`、Slack/Telegram/Discord 渠道、**Letta Agent SDK**（TS）、Letta Cloud。
**前置要求**：Node.js；模型 provider API Key。
**上手难度**：★★★☆☆ —— 安装简单，但"有状态记忆 Agent"概念需学习。

### 差异化特色

1. **OS 式分层记忆**：LLM 视为 CPU、上下文窗口视为内存、archival memory 视为磁盘，Agent 自主决定写入/调取
2. **core memory 可自我编辑**：Agent 判断信息重要性后主动调用内部工具改写 human/persona block，实现**跨会话身份连续性**
3. **sleep-time compute**：非交互时后台自主整理记忆、提炼图谱、合并相似上下文，把重活下沉到异步巩固
4. **ADE（Agent Development Environment）**提供记忆的可视化查看与编辑，便于调试有状态 Agent

### 局限与风险

1. **较重**：是完整 Agent 运行时而非轻量库，只想要"记住用户偏好"轻功能时引入成本偏高
2. 记忆管理逻辑复杂、学习曲线较陡，需自行设计记忆策略
3. 长期记忆的向量检索与 sleep-time compute 会带来额外 token 与算力消耗

### 适合谁 / 典型场景

长期陪伴型 / 私人助理型 Agent（跨会话记住用户身份、偏好、项目上下文）；需要人格连续性与关系记忆的客服/助理机器人；企业构建有状态、可自我改进的自主 Agent 运行时。

---

## 6. E2B

> **定位**：Agent 专用云端沙箱执行环境
> **仓库**：https://github.com/e2b-dev/E2B · **Star**：14,339 · **License**：Apache-2.0 · **语言**：Python SDK（沙箱核心含 Go/Rust 组件） · **维护方**：E2B 公司 · **状态**：✅ 高度活跃（@e2b/code-interpreter-python 2.11.0 / 2026-10-13）

### 它是什么

E2B 解决的是 Agent 安全里最硬的一个问题：**Agent 要执行代码，但代码不能碰到你的真实系统**。

它的答案是**硬件级隔离**：基于 **AWS Firecracker microVM**（不是普通 Docker 容器）。microVM 提供的是**虚拟机级别**的隔离，逃逸防护远强于容器——这对"防止 prompt 注入导致的恶意代码逃逸"至关重要。

它的另外两个特点是：
- **极快启动（亚秒级）**，且支持**快照/恢复（pause/resume）**——适合长任务与有状态会话
- **一套环境内同时提供代码执行、文件系统、浏览器、完整 Linux 桌面（VM）**

开源 core 支持自托管/on-prem 部署，满足企业数据不出域与合规需求。它也被 Thoughtworks 技术雷达收录。

> **实际应用**：社区里"给 OpenClaw 戴上安全锁"的方案，正是基于 E2B 的硬件级隔离。

### 核心架构与编排范式

- **无编排能力**：定位为执行底座，不负责 Agent 逻辑或工作流编排，由上层 Agent/框架调用
- **沙箱生命周期**：创建 → 执行 → 快照/恢复 → 销毁
- **多能力容器**：代码执行 + 文件系统 + 浏览器 + 桌面

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 向 Agent 提供 code interpreter、文件系统、浏览器、桌面等"真实世界工具"能力 |
| **记忆机制** | 无 Agent 记忆机制；沙箱文件系统在会话生命周期内持久，并支持快照/恢复以延续状态 |
| **MCP 支持** | ✅ 提供 MCP 集成（可作为沙箱执行能力暴露给支持 MCP 的 Agent） |
| **沙箱/执行** | ⭐⭐ **核心能力**：基于 AWS Firecracker microVM 的硬件级隔离（非普通容器），亚秒级启动，支持代码执行、文件系统读写、浏览器与完整 Linux 桌面，支持 pause/resume 快照 |
| **人机协作** | 无审批/人工接管机制（安全依赖隔离而非审批） |
| **RAG** | 无 RAG/知识库能力 |

### 快速上手

```bash
# JS/TS
npm i @e2b/code-interpreter dotenv
# Python
pip install e2b-code-interpreter
```

```bash
# .env
E2B_API_KEY=e2b_***
```

```ts
import 'dotenv/config'
import { Sandbox } from '@e2b/code-interpreter'

const sbx = await Sandbox.create()
const execution = await sbx.runCode('print("hello world")')
console.log(execution.logs)
console.log(await sbx.files.list('/'))
```

运行：`npx tsx ./index.ts`
**前置要求**：E2B 账号 + **API Key**（新账号送 $100 额度）。**注意**：2.56.0 起要求 **Python ≥ 3.11**。
**上手难度**：★★☆☆☆ —— 几行代码启动沙箱执行代码。

### 差异化特色

1. **基于 Firecracker microVM 的硬件级安全隔离**，相比传统 Docker 容器提供更强的逃逸防护
2. **极快启动（亚秒级）并支持快照/恢复（pause/resume）**，适合长任务与有状态会话
3. **一套环境内同时提供代码执行、文件系统、浏览器、桌面（VM）**
4. **开源 core 支持自托管/on-prem 部署**，满足企业数据不出域与合规需求

### 局限与风险

1. **自托管部署与运维复杂度高**（Firecracker/基础设施编排），中小团队门槛较大
2. 云托管版按用量计费，大规模长任务成本可能较高
3. 需要额外配置网络访问与凭证，且**隔离越强、环境初始化与调试成本越高**

### 生态与社区

1,110 forks、85 watchers（2026-10-14）；被 Thoughtworks 技术雷达收录；在 MCP 生态中被列为 Code Execution 品类代表 Server。

### 适合谁 / 典型场景

AI 数据分析师 / Code Interpreter：让 Agent 执行 AI 生成的 Python/JS 代码并返回结果；代码执行安全隔离：防止 prompt 注入或恶意代码逃逸到宿主环境；长时运行的有状态 Agent 沙箱（可快照恢复、复用环境）。

---

## 7. Composio

> **定位**：Agent 工具集成与认证平台，把 Agent 的"意图"转为"行动"
> **仓库**：https://github.com/ComposioHQ/composio · **Star**：30,541 · **License**：MIT · **语言**：TypeScript · **维护方**：Composio（美国） · **状态**：✅ 非常活跃

### 它是什么

Composio 解决的是 MCP 之外的另一半问题：**工具的认证（OAuth）与多租户隔离**。

MCP 让 Agent 能"连上"工具，但真实的 SaaS 工具需要 OAuth 授权，而且每个终端用户都要有自己的凭证——这部分工程非常繁琐。Composio 把它托管了：**1600+ 应用的工具集成 + per-user 的认证托管**（OAuth/API key/token 按用户隔离并自动刷新）。

三个关键技术：
- **Tool Router**：按意图在运行时解析工具、按需"just in time"暴露并收窄作用域，降低上下文噪音
- **per-user 隔离的 MCP 会话**：为每个用户创建带独立工具/认证/沙箱配置的 MCP 会话
- **Triggers**：订阅任意 toolkit 的事件并直接路由给 Agent

**Composio 与 MCP 是互补而非竞争**：它既是 MCP Server（把会话以托管 MCP 端点暴露给 Cursor 等客户端），也能接入任意 MCP Server 作为工具来源。

### 核心架构与编排范式

- **自身不做 Agent 编排**，提供工具/认证/触发层
- **Tool Router**：按意图解析并路由工具
- **三层粒度过滤**：Toolkit → 单 Tool → 行为标签
- **Triggers**：事件订阅与路由

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | ⭐ **1600+ 应用/工具包**（GitHub 描述称 1000+ toolkits，官方文档首页称 1,600+ apps）；智能工具搜索按意图在运行时解析；支持触发订阅 |
| **记忆机制** | 提供会话级 context management（per-user session、上下文管理）；长期记忆需搭配 Mem0/Letta 等 |
| **MCP 支持** | ✅ **原生双向**：既是 MCP Server，也能接入外部 MCP Server（含 remote-mcp-server）；未列出的应用只要有 MCP server 即可免费接入 |
| **沙箱/执行** | ✅ 有：提供预接用户已连接账户与 1600+ 工具的沙箱工作台，可安全运行任意代码 |
| **人机协作** | 体现在认证授权流程：OAuth/API key/token 按终端用户隔离并自动刷新，需用户授权；无步骤审批式 HITL |
| **RAG** | 弱，非知识库/检索产品 |

### 快速上手

```bash
# TypeScript
npm install @composio/core @composio/openai-agents @openai/agents
# Python
pip install composio composio-openai-agents openai-agents
# CLI
curl -fsSL https://composio.dev/install | sh
composio login
```

```python
from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider
from agents import Agent, Runner

composio = Composio(provider=OpenAIAgentsProvider())
session = composio.create(user_id="user_123")
agent = Agent(name="Assistant", instructions="Use Composio tools.", tools=session.tools())
print(Runner.run_sync(starting_agent=agent, input="Summarize my emails from today").final_output)
```

也支持 `composio.create(..., mcp=True)` 暴露托管 MCP 端点给 Claude/Cursor。
**前置要求**：`COMPOSIO_API_KEY`（dashboard 获取）；TS 需 **Node 22+**，Python 需 **Python 3.10+**。
**上手难度**：★★☆☆☆ —— SDK 初始化 + session 即可调用。

### 差异化特色

1. **1600+ 应用的工具集成 + 托管认证**（OAuth/API key/token 按 per-user 作用域隔离并自动刷新），省去自建认证的工程
2. **per-user 隔离的 MCP 会话**：为每个用户创建带独立工具/认证/沙箱配置的 MCP 会话，支持会话复用
3. **Tool Router 按意图解析工具**、按需"just in time"暴露并收窄作用域，降低上下文噪音
4. **Triggers 事件订阅**：订阅任意 toolkit 的事件并直接路由到 Agent

### 局限与风险

1. **强依赖云托管**：认证与工具执行主要走 Composio 云，自托管能力边界有限，存在数据/凭证集中风险
2. **工具数量口径不一致**（GitHub 描述 1000+ toolkits vs 文档 1600+ apps），实际可用工具质量与深度参差
3. 作为工具/认证中间层会引入额外网络跳数与延迟，且**非记忆/编排能力**

### 生态与社区

30,541 stars、4.8k forks、78 watchers；文档英文为主（docs.composio.dev）。
**官方 provider 适配**：OpenAI、OpenAI Agents、Anthropic、Claude Agent SDK、Vercel AI SDK、Google GenAI/ADK、LangChain、LangGraph、LlamaIndex、Mastra、Cloudflare Workers、CrewAI、AutoGen 等（TS + Python 双栈）。

### 适合谁 / 典型场景

给自研 Agent 快速接入 Gmail、Slack、GitHub、Notion 等第三方 SaaS 工具与认证；在自有 SaaS 产品内嵌 Agent 工具能力（多租户、按用户隔离认证）；作为 MCP 工具层接入 Cursor、Claude Code、Codex 等现有 Agent 客户端。

---

## 8. Langfuse

> **定位**：开源的 LLM/Agent 可观测性与评测平台
> **仓库**：https://github.com/langfuse/langfuse · **Star**：35,800 · **License**：MIT（核心）+ 企业版双轨（`ee/` 目录商业许可） · **语言**：TypeScript · **维护方**：Langfuse GmbH（德国柏林）；**2026-01 被 ClickHouse 收购** · **状态**：✅ 非常活跃（v4.58.0 / 2026-10-13）

### 它是什么

Langfuse 回答的是运维层面的问题：**我的 Agent 到底在干什么？为什么这次回答不对？花了多少钱？延迟多少？**

它提供追踪（trace）、评测（eval）、提示管理、成本/延迟监控的一体化能力。核心架构上有两个技术亮点：

**① 原生支持 OpenTelemetry / OTLP**
你可以用标准 OTel SDK 采集链路后直接发送给 Langfuse，不绑定特定框架。这在与已有的可观测体系（如 Datadog、Grafana）共存时很重要。

**② ClickHouse OLAP 后端 + 队列化 trace 摄取**
写入路径是：先写 S3 → Redis 排队 → Worker 再入 ClickHouse。这个设计支撑高吞吐与大规模分析——官方称每月处理 **900 亿+ observations**。

它的自托管只依赖开源组件（Postgres + ClickHouse + Redis + S3），数据主权可控，且与 Langfuse Cloud 共用同一代码库。

> ⚠️ **许可注意**：核心为 MIT Expat，但 `ee/`、`web/src/ee/`、`worker/src/ee/` 目录**单独采用商业许可**，部分功能需 license key。LICENSE 版权方为 **ClickHouse, Inc.**（Langfuse 于 2026-01 被 ClickHouse 收购）。

### 核心架构与编排范式

- **自身不做 Agent 编排**，是可观测性/评测层
- 可追踪 LangChain、LangGraph、LlamaIndex 等编排框架
- **100+ 集成框架与提供商接入**（OpenAI、LangChain、LiteLLM、OpenTelemetry 等）

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 非工具集成产品，但可追踪并可视化 Agent 的工具调用链（嵌套 trace 展示 LLM 调用、检索、嵌入、Agent 操作） |
| **记忆机制** | 无（非记忆系统，不做跨会话持久记忆） |
| **MCP 支持** | ✅ 支持（提供 Langfuse MCP Server，用于访问可观测性数据） |
| **沙箱/执行** | 无 |
| **人机协作** | ✅ 有：支持人工标注/评分（human annotation）、人工审核与评测集管理，用于质量把关 |
| **RAG** | 可追踪 RAG 的检索与嵌入环节（观测而非提供检索能力） |

### 快速上手

```bash
pip install langfuse        # Python
npm install langfuse        # JS
```

```python
import os
from langfuse import observe, get_client

os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-..."
os.environ["LANGFUSE_SECRET_KEY"] = "sk-..."
os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"

@observe()
def my_llm_call(q): ...
```

> ⚠️ 安装命令与 v4 具体导入路径未从官方页面核实。

**前置要求**：`LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST`；可用云版或自托管。
**上手难度**：★★☆☆☆ —— 装饰器即可打点。

### 差异化特色

1. **原生支持 OpenTelemetry/OTLP**：可用 OTel SDK 采集链路后直接发送给 Langfuse，自身 SDK 亦与 OTel 兼容
2. **ClickHouse OLAP 后端 + 队列化 trace 摄取**（先写 S3、Redis 排队、Worker 再入 ClickHouse），支撑高吞吐与大规模分析
3. **开源可自托管、数据主权可控**（仅依赖 Postgres + ClickHouse + Redis + S3），与 Langfuse Cloud 同一代码库
4. **集成评测能力**：LLM-as-a-Judge、代码评测器、提示管理与 A/B 实验

### 局限与风险

1. **非记忆/编排产品**：只做观测与评测，需与其他框架（LangGraph 等）搭配使用
2. **自托管架构较重**：需维护 Postgres + ClickHouse + Redis/Valkey + S3 多个组件
3. 部分企业级功能（组织创建者、实例管理 API、UI 定制等）位于 `ee/` 目录，需商业 license key

### 生态与社区

35,800 stars、4.0k forks、114 watchers；官方称每月处理 900 亿+ observations、Docker 镜像拉取 3800 万+ 次。
**知名采用方**：官网宣称被 **Fortune 50 中的 21 家**采用，公开提及 Twilio、Khan Academy 等（企业名单需以官网为准）。

### 适合谁 / 典型场景

LLM/Agent 应用的追踪、调试与延迟/成本监控；基于评测集与 LLM-as-a-Judge 做模型/提示词效果评估与回归测试；企业自托管构建数据主权可控的 LLM 可观测平台。

---

## E 类横向速查

| 项目 | Star | License | 层次 | 为工作台提供什么 | 上手 |
|---|---|---|---|---|---|
| **Browser Use** | 117,914 | MIT | 执行 | 网页操作（DOM+Vision） | ★★☆ |
| **Mem0** | 67,149 | Apache-2.0 | 记忆 | 事实抽取型长期记忆中间件 | ★★☆ |
| **Langfuse** | 35,800 | MIT + EE | 观测 | 追踪、评测、成本监控 | ★★☆ |
| **Composio** | 30,541 | MIT | 工具 | 1600+ 应用集成 + 托管认证 | ★★☆ |
| **A2A** | 26,141 | Apache-2.0 | 协议 | Agent ↔ Agent 协作 | ★★★ |
| **Letta** | 25,125 | Apache-2.0 | 记忆 | OS 式分层记忆运行时 | ★★★ |
| **E2B** | 14,339 | Apache-2.0 | 沙箱 | Firecracker microVM 硬件级隔离 | ★★☆ |
| **MCP** | 9,448 | MIT | 协议 | Agent ↔ Tool 连接标准 | ★★☆ |

### 2026 年协议层两大变化

1. **MCP 完成标准化治理**：2025-12 由 Anthropic 捐赠给 **Linux Foundation 旗下的 Agentic AI Foundation（AAIF）**，OpenAI / Google / Microsoft / Block 等 30+ 企业为创始成员。
   > ⚠️ **数据口径提醒**：媒体广泛报道的"MCP 生态破 10 万 Server"存在夸大——官方 Registry 约 9,652 条（2026-05），33 个注册表去重后约 12,000+。建议采用官方 Registry 口径。

2. **A2A 纳入 Linux Foundation**：IBM 的竞争协议 ACP 已合并入 A2A，生态走向统一。

### 记忆层的技术路线之争

| | Letta（OS 式） | Mem0（事实抽取） |
|---|---|---|
| 定位 | 有状态 Agent 运行时 | 无状态记忆中间件 |
| 记忆模型 | core / archival / recall 三层 | 事实 + 向量 + 实体三库 |
| 关键机制 | core memory 自我编辑、sleep-time compute | 上下文查重 → 抽取 → 去重 → 链接 |
| 检索 | archival 向量检索 | 语义 + BM25 + 实体 + 时间感知 |
| 基准 | — | 官方自报 LOCOMO 92.5（**争议**） |
| 适合 | 要完整运行时 | 只给现有应用加记忆 |

两条路线尚未分出胜负。基准数字的"罗生门"（厂商自报 vs 第三方质疑）说明这个领域还不够成熟。
