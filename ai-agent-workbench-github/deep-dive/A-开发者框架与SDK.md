# A 类｜开发者框架与 Agent SDK（12 个）

> 这一类是"用代码搭 Agent"的底座。自由度最高，也最需要工程能力。
> 数据快照：2026-10-14 · 标注 `[不确定]` 的为未能一手核实项

---

## 1. LangGraph

> **定位**：图状态机式低层 Agent 编排框架，工业界事实标准之一
> **仓库**：https://github.com/langchain-ai/langgraph · **Star**：43,238 · **License**：MIT · **语言**：Python / TypeScript · **维护方**：LangChain, Inc.（美国） · **状态**：✅ 高度活跃

### 它是什么

LangGraph 是 LangChain 团队在 2024 年推出的**低层 Agent 编排框架**，解决的是 LangChain "链式（Chain）"抽象表达能力不足的问题——线性链无法表达循环、分支、并行和人工介入，而这恰恰是真实 Agent 流程的常态。

它的核心洞察是：**把 Agent 流程建模成一张图（Graph）**，而不是一条链。节点（Node）是执行单元，边（Edge）是流转关系，条件边（Conditional Edge）负责分支判断，循环则由边指回上游节点自然表达。这个抽象直接对标了工作流引擎里的状态机范式，因此对复杂业务流程的表达能力远强于线性链。

到 2026 年，LangGraph 已发布 1.0 正式版（2025-10），成为"要精细控制流程"时的默认选择。

### 核心架构与编排范式

- **图状态机**：`StateGraph` 定义状态结构，`add_node` 注册节点，`add_edge` / `add_conditional_edges` 定义流转
- **共享状态 + Reducer**：所有节点读写同一份 State，通过 reducer 函数决定并发写入时的合并策略（如消息追加）
- **持久化执行（Durable Execution）**：基于 checkpoint 机制，同一 `thread_id` 可从任意断点恢复；这是它区别于多数框架的关键能力
- **多 Agent 预置模式**：内置 supervisor（主管分派）、swarm（对等移交）、层级委派（hierarchical）三种多 Agent 拓扑
- **子图（Subgraph）**：图可以嵌套图，便于把复杂流程拆成可复用模块

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置 `ToolNode` 执行工具调用；可直接复用 LangChain 生态的数百种工具；支持自定义函数与结构化工具 |
| **记忆机制** | 短期：thread 内图状态；长期：`BaseStore` 跨 thread 持久化，可接向量检索记忆 |
| **MCP 支持** | ✅ 支持，通过 `langchain-mcp-adapters` 把 MCP Server 的工具适配成 LangChain 工具 |
| **沙箱/执行** | 框架本身不内置沙箱，需自行接入 E2B、本地 subprocess 等 |
| **人机协作** | ✅ 原生支持。`interrupt()` 可在任意节点暂停，人工审批/编辑后 `resume`，配合 checkpoint 实现 |
| **RAG** | 不自带完整 RAG 平台，但可经 LangChain 集成任意向量库与检索器 |

### 快速上手

```bash
pip install -U langgraph
pip install "langgraph-cli[inmem]"   # 本地开发用 CLI
```

```python
from langgraph.graph import StateGraph, MessagesState, START, END

def mock_llm(state: MessagesState):
    return {"messages": [{"role": "ai", "content": "hello world"}]}

graph = StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)
graph = graph.compile()

graph.invoke({"messages": [{"role": "user", "content": "hi!"}]})
```

**开发调试**：`langgraph dev` 启动本地服务与可视化调试界面。
**前置要求**：Python 3.9+（新版多要求 3.10+）；LLM 供应商 API Key；LangSmith 追踪可选（`LANGSMITH_TRACING=true`）。
**上手难度**：★★★☆☆ —— 图/状态/checkpoint 概念较多，但文档极全、示例丰富。

### 差异化特色

1. **图状态机范式**：用节点/边/条件边显式表达分支、循环与并行，比线性链更适合复杂可控流程
2. **持久化执行**：checkpoint 驱动的暂停/恢复与故障恢复，长流程不必从头重跑
3. **原生 human-in-the-loop**：`interrupt()` + 状态检查点，天然支持审批流与步骤回放
4. **内置多种多 Agent 编排模式**，并配套 LangGraph Platform 提供生产部署与可观测性

### 局限与风险

1. **学习曲线陡峭**：图、状态、reducer、checkpoint 等概念多，抽象层厚
2. **商业化依赖**：部署、持久化后端、可视化等高级能力依赖 LangChain 的付费平台（LangGraph Platform / LangSmith）
3. **API 迭代频繁**，社区对迁移成本有一定抱怨

### 适合谁 / 典型场景

需要长时间运行、可恢复的生产级 Agent（客服、研究、审批流）；多 Agent 协作与复杂工作流编排；需人工审批介入的合规/风控自动化。

### 生态与社区

LangChain 生态（集成、文档、模板）最丰富，社区规模大，中文教程较多。官方文档以英文为主。

---

## 2. CrewAI

> **定位**：角色扮演式多 Agent 协作框架，上手最快的框架之一
> **仓库**：https://github.com/crewAIInc/crewAI · **Star**：59,675 · **License**：MIT · **语言**：Python · **维护方**：CrewAI, Inc.（美国，创始人 João Moura） · **状态**：✅ 高度活跃（v1.15.28）

### 它是什么

CrewAI 用一套**"团队隐喻"**把多 Agent 协作变得直观：`Agent`（角色，有 role/goal/backstory）、`Task`（任务）、`Crew`（团队）、`Process`（协作方式）。你不再需要画图或写状态机，只需要描述"我需要一个研究员、一个写手、一个审核员，按顺序干活"，框架就会驱动它们协作。

这个抽象让它成为**上手门槛最低的多 Agent 框架**：几行代码就能跑起一个多角色协作流程。官方还提供了 CLI 脚手架（`crewai create crew`）一键生成项目结构。

2025 年后 CrewAI 引入 **Flows**——事件驱动的流程编排层，用于需要精确控制、检查点与人工反馈的场景，与 Crews（自主协作）形成"双模式"。

### 核心架构与编排范式

- **角色扮演 + 多 Agent 协作**：Agent / Task / Crew / Process 四要素建模
- **Process 两种模式**：`sequential`（顺序执行）/ `hierarchical`（层级，由 manager agent 委派任务）
- **Flows（事件驱动）**：用 `@start` / `@listen` 装饰器定义事件流，支持状态管理与检查点重放
- **Crews + Flows 组合**：Crews 负责"自主协作"，Flows 负责"精确控制"，可嵌套使用

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置大量工具（搜索、爬虫、文件、数据库、代码执行等）；`@tool` 装饰器自定义；有 CrewAI Tools 市场 |
| **记忆机制** | ✅ 内置短期/长期/实体记忆，支持跨会话持久（可配向量存储） |
| **MCP 支持** | ✅ 支持 MCP（工具调用）与 A2A（Agent 间协作/发现） |
| **沙箱/执行** | 不内置强隔离沙箱；可执行代码但需自行用 Docker/E2B 隔离 |
| **人机协作** | Flows 支持人工反馈与审批；任务可设 `human_input`；支持检查点重放/分支 |
| **RAG** | ✅ 内置 RAG 工具（`RagTool`、PDF/网页知识源） |

### 快速上手

```bash
pip install crewai
pip install 'crewai[tools]'
crewai create crew my_project   # 脚手架一键生成
crewai install && crewai run
```

```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Researcher",
    goal="Find info about {topic}",
    backstory="You are a seasoned researcher.",
    verbose=True,
)
task = Task(description="Research {topic}", expected_output="A markdown report", agent=researcher)
crew = Crew(agents=[researcher], tasks=[task], verbose=True)
result = crew.kickoff(inputs={"topic": "AI agents"})
print(result)
```

**前置要求**：Python 环境 + CrewAI CLI；LLM API Key；示例中搜索工具需 `SERPER_API_KEY`。
**上手难度**：★★☆☆☆ —— 抽象直观、脚手架一键生成，最易上手之一。

### 差异化特色

1. **角色扮演范式**：用 Agent/Task/Crew/Process 的团队隐喻建模，代码量少、可读性强
2. **Crews + Flows 双模式**：自主协作与精确控制两种风格可混用
3. **原生支持 MCP 与 A2A**，并内置记忆与 RAG 工具
4. **配套 CrewAI Studio（可视化）与 Enterprise 平台**，官方认证课程规模大

### 局限与风险

1. 高自由度多 Agent 协作带来不确定性与较高的 token 消耗
2. 相比 LangGraph 的低层控制力弱，复杂分支/状态管理受限
3. 部分高级/企业能力需付费平台（CrewAI Enterprise）

### 适合谁 / 典型场景

快速搭建内容生成、市场调研、数据分析等多角色协作流程；企业自动化（客服、报告生成、线索处理）；需要事件驱动精确控制的工作流（Flows）。

### 生态与社区

社区活跃，官方称有 10 万+ 开发者通过其认证课程。文档以英文为主，中文社区与教程较多。

---

## 3. Microsoft Agent Framework

> **定位**：微软把 AutoGen 与 Semantic Kernel 合并后的统一企业级 Agent 框架
> **仓库**：https://github.com/microsoft/agent-framework · **Star**：14,120 · **License**：MIT · **语言**：Python / .NET · **维护方**：Microsoft（美国） · **状态**：✅ 高度活跃（1.0 GA 2026-04）

### 它是什么

这是 2026 年框架层最重要的一次"整合"。微软此前并行维护两个 Agent 项目：**AutoGen**（学术味浓的对话式多 Agent 研究框架）和 **Semantic Kernel**（企业级插件/流程框架，.NET 生态根基）。两者累计超过 7.5 万 Star，但定位重叠、用户困惑。

2026 年 4 月，微软把二者合并为 **Microsoft Agent Framework 并发布 1.0 GA**，同时提供 Python 与 .NET 两套 API 对齐的实现。动机很明确：把"对话式多 Agent 研究"与"企业级插件/流程"收敛成单一生产级底座，并深度对接 Azure AI Foundry。

对于 .NET 技术栈的企业，这是目前最正统的选择——其他主流框架几乎都是 Python 或 TypeScript 优先。

### 核心架构与编排范式

- **工作流（Workflow）+ Agent 双范式**：既可做类型安全的工作流编排，也可做开放式多 Agent 协作
- **多 Agent 模式**：顺序、并发、交接（handoff）、群聊（group chat）
- **继承关系**：保留 AutoGen 的对话协商能力 + Semantic Kernel 的插件/流程能力
- **DevUI**：配套交互式开发界面，用于测试与调试 Agent

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 函数工具/插件；支持 OpenAPI、Code Interpreter、托管工具；可复用 Semantic Kernel 插件与 AutoGen 工具 |
| **记忆机制** | 会话线程（thread）状态 + 记忆组件；长期记忆可对接向量存储 / Azure AI Search |
| **MCP 支持** | ✅ 原生支持 MCP（工具）与 A2A（Agent 间协作） |
| **沙箱/执行** | 框架不内置沙箱，代码执行需借助 Azure / 容器等外部环境 |
| **人机协作** | 工作流支持人工审批/中断（request-response）与检查点恢复 |
| **RAG** | 不内置完整 RAG 平台，可经 Semantic Kernel 连接器对接向量库与 Azure AI Search |

### 快速上手

```bash
# Python
pip install agent-framework
# .NET
dotnet add package Microsoft.Agents.AI
```

```python
import asyncio
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

async def main():
    agent = Agent(
        client=FoundryChatClient(credential=AzureCliCredential()),
        name="HaikuAgent",
        instructions="You are an upbeat assistant that writes beautifully.",
    )
    print(await agent.run("Write a haiku about Microsoft Agent Framework."))

if __name__ == "__main__":
    asyncio.run(main())
```

**前置要求**：Python 3.10+；需 `az login` 或 API Key；支持 Microsoft Foundry / Azure OpenAI / OpenAI / GitHub Copilot SDK。
**上手难度**：★★★☆☆ —— API 双语言一致、示例完整，但依赖 Azure 身份与资源，首次配置略重。

### 差异化特色

1. **统一底座**：合并 AutoGen（对话式多 Agent）与 Semantic Kernel（企业插件/流程），终结微软内部的双轨局面
2. **跨语言一致性**：Python 与 .NET API 对齐，契合 .NET 企业技术栈——这是它相对其他框架的独特价值
3. **工作流 + Agent 双范式**，兼顾可控性与自主性
4. **企业就绪**：与 Azure AI Foundry、OpenTelemetry 可观测性集成

### 局限与风险

1. 相对年轻（2025 年建仓），生态与第三方集成不如 LangChain/CrewAI 成熟
2. 两套旧框架合并带来迁移成本与概念过渡期
3. 部分最佳实践与文档仍在完善，社区规模较小；**无官方中文文档**

### 适合谁 / 典型场景

企业 .NET/Python 应用内嵌 Agent 能力（Azure 技术栈）；多 Agent 协作与工作流自动化（交接、群聊、A2A）；从 Semantic Kernel / AutoGen 迁移的存量项目。

---

## 4. OpenAI Agents SDK

> **定位**：OpenAI 官方轻量级多 Agent 工作流 SDK，配套 AgentKit 生态
> **仓库**：https://github.com/openai/openai-agents-python · **Star**：30,023 · **License**：MIT · **语言**：Python / JS · **维护方**：OpenAI（美国） · **状态**：✅ 高度活跃（v0.23.1，2026-10-02）

### 它是什么

OpenAI Agents SDK 由 2024 年底的实验性项目 **Swarm** 演进而来，2025 年 3 月正式发布。它的设计哲学是**极简**：核心抽象只有四个——`Agent`（智能体）、`Handoff`（交接）、`Guardrail`（护栏）、`Session`（会话）。

这个极简设计让它在所有主流框架里**上手最快**（难度 ★☆☆☆☆）：定义一个 Agent、调用 `Runner.run()`，就跑起来了。代价是它原生绑定 OpenAI 平台——但换来的是与 Responses API、托管工具（Web Search / File Search / Computer Use / Code Interpreter）的深度协同。

配套的 **AgentKit**（2025-10 发布）把能力补齐到平台级：可视化 Agent Builder 画布、ChatKit 聊天组件、Connector Registry、Evals 评测。

### 核心架构与编排范式

- **多 Agent 编排**：以 Agent + handoffs（交接）+ guardrails + sessions 为核心
- **agents-as-tools**：可把一个 Agent 当工具给另一个 Agent 调用
- **LLM 决定的路由**：由模型自行决定何时交接给哪个 Agent
- **AgentKit**：可视化画布搭建，可导出 SDK 代码（设计态与代码态互通）

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置 Web Search、File Search、Computer Use、Code Interpreter、Hosted MCP；支持自定义 function tools 与结构化输出 |
| **记忆机制** | `sessions` 会话记忆，可自动管理对话历史；长期记忆需自行实现 |
| **MCP 支持** | ✅ 原生支持（含托管 MCP 工具与本地 MCP Server） |
| **沙箱/执行** | Computer Use / Code Interpreter 在 OpenAI 托管的隔离环境中执行 |
| **人机协作** | 支持工具调用审批（guardrails 与需人工确认的工具）、中断与恢复 |
| **RAG** | 内置 File Search 工具（托管向量检索） |

### 快速上手

```bash
pip install openai-agents
```

```python
import asyncio
from agents import Agent, Runner

agent = Agent(
    name="History Tutor",
    instructions="You answer history questions clearly and concisely.",
)

async def main():
    result = await Runner.run(agent, "When did the Roman Empire fall?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

**前置要求**：`OPENAI_API_KEY`；Python 3.9+。
**上手难度**：★☆☆☆☆ —— 极简 API，最适合快速起步。

### 差异化特色

1. **官方轻量**：核心抽象仅 4 个，代码简洁、易调试
2. **与 OpenAI 平台深度协同**：原生调用 Responses API 与 Hosted Tools
3. **AgentKit 生态**：Agent Builder（可视化画布，可导出 SDK 代码）、ChatKit、Connector Registry、Evals
4. **原生 handoff 多 Agent 交接与 guardrails 安全护栏**

### 局限与风险

1. 对 OpenAI 平台绑定较强，跨厂商模型支持不如模型无关框架
2. 部分能力（Hosted Tools、AgentKit）依赖 OpenAI 云服务与计费
3. 相对较新，复杂状态/持久化能力不如 LangGraph 等成熟框架

### 适合谁 / 典型场景

基于 OpenAI 模型快速构建客服/研究/销售等 Agent；多 Agent 交接与路由（handoffs）；用 Agent Builder 可视化搭建并导出代码的企业工作流。

### 生态与社区

OpenAI 官方维护，增长快。文档英文为主，社区示例丰富。**无官方中文文档**。

---

## 5. Claude Agent SDK

> **定位**：Anthropic 官方 Agent SDK，源自 Claude Code
> **仓库**：https://github.com/anthropics/claude-agent-sdk-python · **Star**：8,273 · **License**：MIT · **语言**：Python / TypeScript · **维护方**：Anthropic（美国） · **状态**：✅ 活跃

### 它是什么

Claude Agent SDK 的前身是 **Claude Code SDK**，2025 年 9-10 月随 Claude Sonnet 4.5 发布后更名。它的独特之处在于：**它不是从零设计的框架，而是把 Claude Code 这个成熟产品的能力暴露成 SDK**。

也就是说，你拿到的不是一套"抽象概念"，而是一个已经在真实编码场景里跑了很久的 Agent 运行时——内置文件读写、Bash 命令执行、网页抓取等工具，自带上下文压缩（compaction）机制、权限系统、hooks、子代理（subagents）与 Skills。

这让它成为"要在自有应用里嵌入类 Claude Code 能力"时最直接的路径。

### 核心架构与编排范式

- **单主 Agent 循环 + 子代理委派**：以层级委派实现多 Agent
- **扩展机制**：hooks（生命周期钩子）、commands（自定义命令）、skills（技能包）
- **权限系统**：permission modes 控制工具调用审批
- **上下文管理**：自动 compaction 应对长会话

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置文件读写、Bash 命令执行、网页抓取/搜索；支持自定义工具与 hooks |
| **记忆机制** | 上下文管理与 compaction；`CLAUDE.md` 提供项目级长期上下文；跨会话持久记忆需自行实现 |
| **MCP 支持** | ✅ 原生支持 MCP（作为工具来源） |
| **沙箱/执行** | 可执行代码、操作文件系统（Bash、文件工具）；支持沙箱/权限隔离配置 |
| **人机协作** | 完善的权限系统、工具调用审批与 hooks，可中断/接管 |
| **RAG** | 不内置完整 RAG；可通过 MCP 工具或外部检索接入 |

### 快速上手

```bash
pip install claude-agent-sdk
```

```python
import anyio
from claude_agent_sdk import query

async def main():
    async for message in query(prompt="What is 2 + 2?"):
        print(message)

anyio.run(main)
```

更复杂的交互用 `ClaudeSDKClient`（双向、支持自定义工具与 hooks）。
**前置要求**：Python 3.10+；**Claude Code CLI 已随包自动捆绑**（无需单独安装）；需 Anthropic 凭据。
**上手难度**：★★★☆☆ —— 少量 API 即可跑，但需理解 Claude Code 的工具集与权限模式。

### 差异化特色

1. **源自 Claude Code 的成熟 Agent 运行时**：开箱具备文件、Bash、搜索等工具与上下文管理
2. **原生支持子代理（subagents）与 Skills**，便于层级委派与能力复用
3. **完善的权限与 hooks 机制**，支持人机协作与安全管控
4. **原生 MCP 支持**

### 局限与风险

1. 与 Claude 模型 / Anthropic 生态绑定较强
2. 依赖 Claude Code 运行时，部署形态与跨厂商灵活性有限
3. 相对年轻，Star 数与生态小于其他主流框架；**无官方中文文档**

### 适合谁 / 典型场景

在自有应用中嵌入类 Claude Code 的编码/自动化 Agent；构建需操作文件系统与命令行的自主任务 Agent；通过子代理与 Skills 扩展的企业级 Agent。

---

## 6. Google ADK（Agent Development Kit）

> **定位**：Google 开源的代码优先 Agent 开发工具包，与 Gemini/Vertex AI 深度绑定
> **仓库**：https://github.com/google/adk-python · **Star**：21,826 · **License**：Apache-2.0 · **语言**：Python / Go / Java / TypeScript / Kotlin · **维护方**：Google（美国） · **状态**：✅ 高度活跃（2.0 已发布）

### 它是什么

Google ADK 于 2025 年 4 月首发，是 Google 在 Agent 框架层的正式回应。它的核心主张是 **"Agent + Workflow 双范式"**：LLM Agent 负责需要判断的决策，Workflow 负责确定性的编排——顺序、并行、循环、路由、重试、状态管理全部内置，不必自己写调度代码。

这是 ADK 相对 LangGraph 的差异化：LangGraph 给你图的**原语**，你自己画；ADK 2.0 给你**成品组件**，直接组合。对不想要"从零设计状态机"的团队更友好。

另一个显著优势是**多语言**：Python / Java / Go / TypeScript / Kotlin 五套实现，API 保持一致。这在需要跨栈团队协作的企业里很实用。

### 核心架构与编排范式

- **Agent + Workflow 双范式**：LLM Agent 决策，Workflow 编排
- **预置工作流 Agent**：`SequentialAgent` / `ParallelAgent` / `LoopAgent` 等
- **层级多 Agent**：sub-agents 结构
- **A2A 原生集成**：跨 Agent 协作
- **`adk web`**：开发用可视化调试界面

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置 Google Search、代码执行、Vertex AI 工具、函数工具；支持自定义工具与第三方库工具 |
| **记忆机制** | Session/State 管理会话状态；支持长期记忆（Memory）与可插拔存储后端 |
| **MCP 支持** | ✅ 原生支持 MCP（工具）+ A2A（协议） |
| **沙箱/执行** | 提供代码执行工具（可对接 Vertex AI 代码执行/沙箱环境） |
| **人机协作** | 工作流支持人工审批/中断与恢复，状态可持久化 |
| **RAG** | ✅ 内置 RAG 能力，可对接 Vertex AI Search / 向量库 |

### 快速上手

```bash
pip install google-adk
adk create my_agent
adk run my_agent        # CLI 运行
adk web --port 8000     # Web 调试 UI（仅开发用）
```

```python
from google.adk.agents.llm_agent import Agent

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

root_agent = Agent(
    model='gemini-flash-latest',
    name='root_agent',
    description="Tells the current time in a specified city.",
    instruction="You are a helpful assistant that tells the current time in cities.",
    tools=[get_current_time],
)
```

**前置要求**：Python 3.10+；`GOOGLE_API_KEY`（从 Google AI Studio 获取）。
**上手难度**：★★☆☆☆ —— `adk create` 一键脚手架 + `adk web` 可视化调试。

### 差异化特色

1. **Agent + Workflow 双范式**：ADK 2.0 内置工作流、路由、循环、重试、并行与状态管理，减少自研调度代码
2. **五语言一致 API**：Python / Java / Go / TypeScript / Kotlin
3. **与 Google 生态深度绑定**：Gemini、Vertex AI、Google Search、A2A 协议原生集成
4. **内置评估（eval）与部署到 Vertex AI Agent Engine 的路径**

### 局限与风险

1. 最佳体验偏向 Google/Gemini 生态，跨厂商模型需额外适配
2. 多语言 API 与文档成熟度不一，部分特性以 Python 为先
3. ADK 2.0 相对新，迁移与最佳实践仍在沉淀；**无官方中文文档**

### 适合谁 / 典型场景

基于 Gemini/Vertex AI 构建企业级 Agent 与多 Agent 系统；需要工作流编排（分支/循环/并行）的复杂 Agent 应用；跨 Agent 协作（A2A）与工具集成的 Google Cloud 场景。

---

## 7. LlamaIndex

> **定位**：以数据/RAG 为中心的 Agent 框架
> **仓库**：https://github.com/run-llama/llama_index · **Star**：50,433 · **License**：MIT · **语言**：Python · **维护方**：LlamaIndex Inc.（美国） · **状态**：✅ 活跃（开源框架更新放缓）

### 它是什么

LlamaIndex 的出发点与 LangGraph/CrewAI 不同：**它解决的是"如何把私有、复杂、异构的数据变成 LLM 可用的上下文"**。在这个基础上，它长出了完整的 RAG 工具链（数据连接器 → 索引 → 检索 → 重排 → 查询引擎），再往上才扩展到 Agent 与 Workflows。

所以它的能力重心在**数据层**：`LlamaHub` 提供 300+ 数据连接器（API、PDF、SQL、Notion 等），覆盖从数据接入到检索问答的全链路。当你需要处理"企业里散落在各处的文档和数据"时，它是集成成本最低的选择。

需要留意的信号是：公司战略重心已转向商业平台 **LlamaParse / LlamaCloud**（企业级文档解析），官方 README 自述开源框架的更新频率下降。

### 核心架构与编排范式

- **事件驱动 Workflows**：支持流式事件、分支、中断，适合复杂文档 Agent 工作流
- **单 Agent 循环 + 多 Agent 协作**
- **QueryEngine → Agent 的跃迁路径**：从固定"检索-生成"到自主决策
- **FunctionAgent**：基于函数工具的 Agent 抽象

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置工具与 `FunctionTool`；支持 QueryEngine-as-Tool；支持 CodeInterpreterTool |
| **记忆机制** | 短期会话记忆 + 长期向量记忆（memory 模块与 chat store 持久化） |
| **MCP 支持** | ✅ 支持（提供 MCP 工具集成包） |
| **沙箱/执行** | 无独立沙箱，代码执行通过工具实现 |
| **人机协作** | ✅ 支持（Workflows 支持事件中断与人工输入） |
| **RAG** | ⭐ **核心强项**：LlamaHub 300+ 连接器、索引、检索、rerank、查询引擎 |

### 快速上手

```bash
pip install llama-index
```

```python
import asyncio
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI

def multiply(a: float, b: float) -> float:
    """Useful for multiplying two numbers."""
    return a * b

agent = FunctionAgent(
    tools=[multiply],
    llm=OpenAI(model="gpt-4o-mini"),
    system_prompt="You are a helpful assistant that can multiply two numbers.",
)

async def main():
    response = await agent.run("What is 1234 * 4567?")
    print(str(response))

if __name__ == "__main__":
    asyncio.run(main())
```

**前置要求**：`OPENAI_API_KEY`（默认 OpenAI，可换 OpenAILike 或本地模型）；Python 3.9+。
**上手难度**：★★★☆☆ —— Agent 示例简单，但生态庞大（RAG/索引/向量库集成）概念多。

### 差异化特色

1. **以数据为中心**：LlamaHub 300+ 数据连接器，从数据接入到检索问答全链路覆盖
2. **事件驱动 Workflows 编排引擎**，支持流式、分支与中断
3. **从 QueryEngine 到 Agent 的完整能力跃迁路径**
4. **与 LlamaParse/LlamaCloud 企业级文档解析深度集成**（130+ 文档格式、agentic OCR）

### 局限与风险

1. **公司战略重心转向商业平台 LlamaParse，开源框架更新放缓**（README 明确提示）
2. 集成包数量庞大导致依赖与版本管理复杂
3. 抽象层较多，深度定制学习曲线偏高

### 适合谁 / 典型场景

企业私有数据的 RAG 问答与知识库；复杂文档解析与结构化抽取（结合 LlamaParse）；多 Agent 文档处理工作流（解析→索引→抽取→问答）。

### 生态与社区

社区成熟（Discord、Reddit），贡献者众多；**有官方中文文档站**（docs.llamaindex.org.cn）。

---

## 8. smolagents

> **定位**：HuggingFace 出品的极简 Code-Agent 框架，核心理念"代码即动作"
> **仓库**：https://github.com/huggingface/smolagents · **Star**：27,944 · **License**：Apache-2.0 · **语言**：Python · **维护方**：Hugging Face（美国/法国） · **状态**：✅ 活跃（v1.26.0，2026-05-29）

### 它是什么

smolagents 的核心主张是一句反直觉的话：**"Agent 不应该输出 JSON 工具调用，而应该直接写 Python 代码"**。

传统 tool-calling 的流程是：模型输出结构化 JSON → 框架解析 → 调用工具 → 把结果序列化回上下文。smolagents 认为这个"序列化-反序列化"过程浪费 token 且限制表达力——模型完全可以直接写 `result = search("x") + calc(y)` 这样的代码，一次调用完成多个工具的组合与数据处理。

这个范式叫 **Code-as-Action（代码即动作）**。它的优势是省 token、表达力强（可以做循环、条件、变量复用）；代价是**安全风险显著上升**，必须依赖沙箱隔离。

另一个卖点是**极简**：核心实现约 1000 行代码，依赖轻量、易读易改，是"想读懂 Agent 框架内部怎么工作"的最佳教材。

### 核心架构与编排范式

- **CodeAgent**：Agent 直接生成 Python 代码调用工具（核心）
- **ToolCallingAgent**：也提供传统 JSON 工具调用模式作为备选
- **managed agents**：多 Agent 层级协作（Agent 互相调用）
- **CLI**：`smolagent`（通用多步 CodeAgent）、`webagent`（网页浏览 Agent）

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | `Tool` 装饰器自定义工具、`ToolCollection`、Hub 工具共享；**原生支持代码执行** |
| **记忆机制** | 短期会话记忆（agent 步骤与消息历史），无内置长期记忆 |
| **MCP 支持** | ✅ 支持（MCP 客户端，`ToolCollection.from_mcp`） |
| **沙箱/执行** | ⭐ **多后端可选**：E2B / Docker / Modal / WebAssembly（Pyodide）；内置 `LocalPythonExecutor` **不是安全边界** |
| **人机协作** | ✅ 支持（Agent 可请求人工输入，提供步骤回调） |
| **RAG** | 非内置；可通过自定义工具/检索实现 |

### 快速上手

```bash
pip install "smolagents[toolkit]"
```

```python
from smolagents import CodeAgent, WebSearchTool, InferenceClientModel

model = InferenceClientModel()
agent = CodeAgent(tools=[WebSearchTool()], model=model, stream_outputs=True)

agent.run("How many seconds would it take for a leopard at full speed to run through Pont des Arts?")
```

**CLI**：`smolagent`（交互向导）、`webagent`（网页浏览）。
**前置要求**：Python 3.10+；HF token 或改用 LiteLLM/OpenAI/Azure/Bedrock 等；**代码执行强烈建议配 E2B/Docker 沙箱**。
**上手难度**：★★☆☆☆ —— 核心约千行、抽象极少，几行即可跑；但代码执行需注意安全。

### 差异化特色

1. **"代码即动作"范式**：省去 JSON 工具调用的中间序列化，理论上更省 Token 且表达力更强
2. **极简核心实现**（千行代码量级），依赖轻量、易读易改
3. **多沙箱执行后端可选**（E2B/Docker/Modal/WASM），兼顾安全与灵活性
4. **工具可在 Hugging Face Hub 上分享与加载**（`Tool.from_hub`）

### 局限与风险

1. **"代码即动作"带来安全风险，必须依赖沙箱隔离**
2. 集成与生态规模相对小于 LangChain 等老牌框架
3. 复杂生产级编排能力弱于 LangGraph 等图编排框架

### 适合谁 / 典型场景

代码型 Agent 与研究原型实验；数学计算、数据分析类任务；教学演示与快速概念验证。

### 生态与社区

依托 Hugging Face 生态，社区活跃；**提供多语言（含中文）官方文档**。

---

## 9. Pydantic AI

> **定位**：以类型安全与 Pydantic 校验为核心的 Python Agent 框架
> **仓库**：https://github.com/pydantic/pydantic-ai · **Star**：约 16,900 · **License**：MIT · **语言**：Python · **维护方**：Pydantic Services Inc.（英国，创始人 Samuel Colvin） · **状态**：✅ 活跃（2.x）

### 它是什么

Pydantic AI 的定位类比是 **"Agent 框架里的 FastAPI"**。它要解决的问题是：LLM 的输出不可控、难测试、难做类型校验——而这正是传统软件工程最不能接受的部分。

它的解法是把 Agent 的**输出、依赖、工具接口全部纳入 Pydantic 类型系统**：模型输出必须符合你定义的 Pydantic 模型，工具函数的签名与 docstring 自动生成 schema，依赖通过类型化的依赖注入传入。这样你在 IDE 里能获得完整的类型提示与静态检查，测试时也能直接断言结构化对象。

对 Python 后端团队来说，这是"把 LLM 应用当正经软件工程做"的最自然选择。配套的 `pydantic-graph` 还提供类型化图状态机，补上了复杂工作流编排能力。

### 核心架构与编排范式

- **类型化单 Agent 循环**：以 Pydantic 模型约束输入输出
- **多 Agent**：委托 / handoff
- **pydantic-graph**：类型化图状态机，支持复杂可控工作流
- **依赖注入**：类似 FastAPI 的 `RunContext` 机制

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 类型化工具（由函数签名与 docstring 自动生成 schema）+ 依赖注入；支持 CodeExecutionTool |
| **记忆机制** | 消息历史（短期）；长期可通过消息处理器与外部持久化实现 |
| **MCP 支持** | ✅ 支持（原生 MCP 客户端） |
| **沙箱/执行** | 无内置沙箱；代码执行依赖外部工具/环境 |
| **人机协作** | ✅ 支持（工具审批、延迟工具、Human-in-the-loop 机制） |
| **RAG** | 非强内置；可结合 embeddings 与检索组件实现 |

### 快速上手

```bash
pip install pydantic-ai
```

```python
from pydantic_ai import Agent

agent = Agent(
    'openai:gpt-4o',   # 也可用 'google-gla:gemini-1.5-flash' 等
    system_prompt='Be concise, reply with one sentence.',
)

result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
```

> ⚠️ 上述示例为通用形态，本次调研未能抓取到官方 Quickstart 页面原文，请以官方文档为准。

**前置要求**：`OPENAI_API_KEY`（或对应供应商 Key）；Python 3.9+。
**上手难度**：★★☆☆☆ —— 类型安全、API 简洁。

### 差异化特色

1. **以 Pydantic 类型校验为核心**——输出、依赖、工具接口均类型安全，兼容静态类型检查
2. **类 FastAPI 的开发者体验**：依赖注入 + 与 Pydantic Logfire 可观测性深度集成
3. **pydantic-graph 提供类型化图状态机**，支持可控的复杂工作流编排
4. **同一 Agent 可跨 Web 前端、终端、语音、后台队列、GitHub Actions 等运行**

### 局限与风险

1. 生态相对较新，第三方集成数量少于 LangChain
2. 偏重类型与后端工程，对非工程背景用户学习曲线较陡
3. 复杂多 Agent 编排能力相对有限；**无官方中文文档**

### 适合谁 / 典型场景

需要强类型与结构化校验输出的 LLM 应用；生产级 LLM 后端服务（API/队列）；需要可测试、可观测的 Agent 工作流。

### 生态与社区

由 Pydantic 官方维护，社区活跃；**有中文文档镜像站**（ai.pydantic.org.cn）。

---

## 10. Agno（原 Phidata）

> **定位**：主打高性能、无依赖的多模态 Agent 运行时
> **仓库**：https://github.com/agno-agi/agno · **Star**：约 34,000 · **License**：Apache-2.0 · **语言**：Python · **维护方**：Agno（美国，创始人 Ashpreet Bedi） · **状态**：✅ 非常活跃（v3.x）

### 它是什么

Agno（2024 年由 Phidata 更名而来）的差异化主张是**性能与轻量**：纯 Python 实现、无依赖、刻意回避"图/链"这类重型抽象，宣称 Agent 的实例化与运行速度远超 LangGraph（官方曾宣传"快 5000 倍"——**这是营销口径，未经独立验证，需谨慎看待**）。

它的三层抽象是：`Agent`（单智能体）、`Team`（多 Agent 协作，支持路由/协作/协调三种模式）、`Workflow`（DAG 流程）。在此之上提供 **AgentOS**——一个运行时层，为 Agent 平台提供 REST API、控制台 UI、监控与部署能力，可 Docker 自托管。

所以 Agno 实际上是"SDK + 平台"的组合：SDK 层做 Agent，AgentOS 层做产品化。

### 核心架构与编排范式

- **三层抽象**：Agent / Team（三模式）/ Workflow（DAG）
- **刻意回避图/链范式**：追求简洁直观
- **AgentOS**：运行时层，含 REST API、控制台、MCP endpoint（含 OAuth）
- **外部 Agent 生命周期**：可持久化 / 恢复 / 取消 / 回放

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置丰富工具包（ReasoningTools、搜索、代码执行等）；自定义工具简洁 |
| **记忆机制** | ✅ 内置会话记忆 + 长期记忆 + 知识库（基于向量库的动态少样本学习），可持久化到数据库 |
| **MCP 支持** | ✅ 支持（AgentOS MCP endpoint，含 OAuth 认证） |
| **沙箱/执行** | 支持代码执行（通过工具，可集成沙箱环境） |
| **人机协作** | ✅ 支持（工具审批；外部 Agent 可持久化/恢复/取消/回放） |
| **RAG** | ✅ 内置 Agentic RAG 与 Knowledge 体系 |

### 快速上手

```bash
pip install agno
```

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(model=OpenAIChat(id="gpt-4o"), markdown=True)
agent.print_response("What is the capital of France?", stream=True)
```

> ⚠️ 示例为通用形态，本次未从官方 Quickstart 页面核实。

**生产形态**：官方推荐用 AgentOS 模板仓库（agentos-railway / agentos-docker / agentos-aws）一键起平台。
**前置要求**：Python + 供应商 API Key；AgentOS 生产模式需 **Postgres**（存 sessions/memory/knowledge/traces）。
**上手难度**：★★★☆☆ —— SDK 层简洁，但官方主推的 AgentOS 平台形态起步略重。

### 差异化特色

1. **高性能主张**：无依赖/纯 Python 架构（宣传数字未获独立验证）
2. **AgentOS 运行时层**：为 Agent 平台提供 API、控制台、监控与部署能力
3. **多模态 + 多 Agent**：Team 提供路由/协作/协调三种协作模式
4. **内置记忆与知识库**，支持会话与 Agent 状态持久化

### 局限与风险

1. **性能宣传数字（如 5000x）缺乏独立验证，营销色彩较重**
2. 版本迭代极快（v2.x→v3.x），API 变动频繁，升级成本高
3. 部分高级能力（监控、部署）绑定 AgentOS；**无官方中文文档**

### 适合谁 / 典型场景

生产级多 Agent 平台搭建；多模态 Agent 应用；需要会话/知识持久化的客服与智能助手。

---

## 11. Mastra

> **定位**：TypeScript 原生 Agent 框架，TS 阵营代表
> **仓库**：https://github.com/mastra-ai/mastra · **Star**：约 24,972 · **License**：Apache-2.0 + 企业许可（`ee/` 目录） · **语言**：TypeScript · **维护方**：Mastra AI（美国，YC W25） · **状态**：✅ 活跃

### 它是什么

在本次调研的 12 个框架里，**Mastra 是唯一的 TypeScript 原生框架**（其余基本是 Python，Microsoft Agent Framework 是 Python/.NET）。这个定位本身就是它的价值：Node / Next.js 全栈团队不必为了做 Agent 而引入 Python 服务。

它走"一体化"路线：Agent + Workflow（基于 XState 的状态机引擎）+ 记忆 + RAG + 可观测性全部内置，并提供本地 **Mastra Playground** 调试 UI 与 **Mastra Cloud** 一键部署。`npm create mastra@latest` 一条命令生成项目骨架。

需要留意的是：核心框架是 Apache-2.0，但部分功能位于 `ee/` 目录，采用**企业许可**——并非完全开源。

### 核心架构与编排范式

- **Agent + Workflow**：工作流引擎基于 **XState**（成熟的状态机库），支持挂起/恢复
- **多 Agent 网络**：Agent 之间可互相调用
- **原生 MCP 双向**：既是 MCP 客户端，也可把自身 Agent/工具暴露为 MCP Server
- **Studio / Playground**：本地可视化调试

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置工具、基于 Zod schema 定义工具、支持工具执行与结果流式 |
| **记忆机制** | ✅ 内置记忆系统（对话历史、工作记忆、语义记忆），可持久化到存储 |
| **MCP 支持** | ✅ 原生（`@mastra/mcp` 同时提供客户端与服务端） |
| **沙箱/执行** | 无内置强沙箱；可执行工具函数 |
| **人机协作** | ✅ 支持（工作流挂起/恢复，human-in-the-loop） |
| **RAG** | ✅ 内置（文档处理、分块、向量存储、检索） |

### 快速上手

```bash
npm create mastra@latest
# 加入已有项目：
npm install @mastra/core
mastra dev        # 启动 Studio
```

```ts
import { Agent } from '@mastra/core/agent';
import { openai } from '@ai-sdk/openai';

export const myAgent = new Agent({
  name: 'myAgent',
  instructions: 'You are a helpful assistant.',
  model: openai('gpt-4o'),
});
```

> ⚠️ 示例为通用形态，本次未从官方 Quickstart 页面核实具体 API。

**前置要求**：Node.js 20+（TypeScript 生态）；供应商 API Key。
**上手难度**：★★★☆☆ —— 脚手架开箱即用、Studio 可视化好，但需熟悉 TypeScript 生态。

### 差异化特色

1. **TypeScript 原生、端到端类型安全**，与 Node/Next.js 无缝集成——这是它在框架层的独特生态位
2. **一体化能力**：Agent + 工作流引擎（XState）+ 记忆 + RAG + 可观测性，开箱即用
3. **原生 MCP 客户端与服务端**，可将自身 Agent/工具通过 MCP 暴露
4. **本地 Playground 调试 + Mastra Cloud 一键部署**

### 局限与风险

1. **仅限 TS/JS 生态**，Python 团队无法直接复用
2. 部分功能位于 `ee/` 目录，采用企业许可，**并非完全开源**
3. 项目较新（YC W25），大规模生产案例仍在积累；**无官方中文文档**

### 适合谁 / 典型场景

TypeScript/Node 后端 AI 应用；全栈 AI 产品（如 Next.js 应用）；需要工作流编排 + RAG + 记忆的产品级 Agent。

---

## 12. Haystack

> **定位**：生产级 LLM/Agent 编排框架，强调"显式控制"的模块化 Pipeline
> **仓库**：https://github.com/deepset-ai/haystack · **Star**：约 24,800 · **License**：Apache-2.0 · **语言**：Python · **维护方**：deepset（德国柏林） · **状态**：✅ 活跃（2.x）

### 它是什么

Haystack 来自德国公司 deepset，根源是**检索（retrieval）研究**，因此它的 RAG / 语义搜索能力非常扎实。它的设计哲学是**"显式控制"**：用可插拔的组件（Component）组装成 Pipeline（DAG），每一环都清晰可见、可替换、可观测。

这跟 LangGraph 的"给原语自己画图"、CrewAI 的"给隐喻自己组队"都不同——Haystack 更像是**给你一套标准零件和装配线**，适合对可观测性、可维护性要求高的生产环境（尤其是企业文档问答、语义搜索、信息抽取）。

配套的 **Hayhooks** 可把 Pipeline 暴露为 REST / MCP 服务；企业侧有 deepset AI Platform，并与 NVIDIA Enterprise AI Factory 合作。

### 核心架构与编排范式

- **模块化 Pipeline（DAG）**：组件可插拔组合
- **Agent 工作流**：支持多 Agent
- **显式控制**：Pipeline 支持中断与断点（Breakpoints）
- **Hayhooks**：对外暴露 REST / MCP

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 组件化工具（Tool 组件）+ 自定义工具；支持函数调用 |
| **记忆机制** | 短期会话（ChatMessage 历史）+ 可扩展长期记忆（存储组件） |
| **MCP 支持** | ✅ 支持（MCPTool 等） |
| **沙箱/执行** | 无内置沙箱；可执行工具函数 |
| **人机协作** | ✅ 支持（Pipeline 支持中断与断点） |
| **RAG** | ⭐ **核心强项**：完整 RAG pipeline（检索、rerank、reader、generator） |

### 快速上手

```bash
pip install haystack-ai
```

```python
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

generator = OpenAIChatGenerator(model="gpt-4o-mini")
response = generator.run(messages=[ChatMessage.from_user("What is RAG?")])
print(response["replies"][0].text)
```

> ⚠️ 示例为通用形态，本次官方 Quickstart 页面返回 404，请以官方文档为准。

**前置要求**：Python；供应商 API Key；无需强制数据库。
**上手难度**：★★★☆☆ —— 面向生产的 RAG/Pipeline 抽象严谨，需理解 Component/Pipeline 模型。

### 差异化特色

1. **组件化模块设计，Pipeline 显式可控**，适合生产环境与可观测性要求高的场景
2. **深厚的检索/RAG 能力**（源自 deepset 早期检索研究），检索-重排-生成链路完整
3. **企业级支持**：deepset AI Platform，并与 NVIDIA Enterprise AI Factory 合作
4. **统一支持 Agent、RAG、多模态、语义搜索与对话系统**

### 局限与风险

1. **从 Haystack 1.x 到 2.x API 大改**，历史项目迁移成本高
2. 组件抽象较重，简单场景上手相对繁琐
3. Agent 编排灵活度相对 LangGraph 等图编排框架略低

### 适合谁 / 典型场景

企业级 RAG 与语义搜索；文档问答与信息抽取（含智能文档处理 IDP）；生产级对话系统与检索增强应用。

---

## A 类横向速查

| 项目 | Star | License | 语言 | 编排范式 | 上手 | 一句话 |
|---|---|---|---|---|---|---|
| CrewAI | 59,675 | MIT | Python | 角色扮演多 Agent | ★★☆ | 上手最快 |
| LlamaIndex | 50,433 | MIT | Python | 事件驱动 Workflow | ★★★ | RAG 最强 |
| LangGraph | 43,238 | MIT | Py/TS | 图状态机 | ★★★ | 控制力最强 |
| Agno | ~34,000 | Apache-2.0 | Python | Agent/Team/Workflow | ★★★ | 性能主张激进 |
| OpenAI Agents SDK | 30,023 | MIT | Py/JS | handoff 交接 | ★☆☆ | 最简 |
| smolagents | 27,944 | Apache-2.0 | Python | 代码即动作 | ★★☆ | 极简教材 |
| Mastra | ~24,972 | Apache-2.0+EE | TS | Agent + XState | ★★★ | 唯一 TS 原生 |
| Haystack | ~24,800 | Apache-2.0 | Python | 模块化 Pipeline | ★★★ | 生产级 RAG |
| Google ADK | 21,826 | Apache-2.0 | 5 语言 | Agent + Workflow | ★★☆ | 多语言 |
| Pydantic AI | ~16,900 | MIT | Python | 类型化 Agent | ★★☆ | 类型安全 |
| Microsoft AF | 14,120 | MIT | Py/.NET | 工作流 + 多 Agent | ★★★ | .NET 首选 |
| Claude Agent SDK | 8,273 | MIT | Py/TS | 主 Agent + 子代理 | ★★★ | 复用 Claude Code |
