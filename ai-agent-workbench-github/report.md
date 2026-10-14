# GitHub 上的 AI Agent 通用工作台全景调研

> **调研主题**：GitHub 上有多少种 AI Agent 通用工作台，各有什么特色
> **数据快照日期**：2026-10-14
> **覆盖范围**：6 大类 / 49 个代表性开源项目
> **数据来源**：GitHub REST API（`api.github.com/repos/{owner}/{repo}`）一手抓取 + 官方文档/媒体交叉验证
> **说明**：Star 数为 2026-10-14 快照值，会随时间变化；标注 `[不确定]` 的为未能一手核实的项。

---

## 一、结论速览

**「AI Agent 通用工作台」在 GitHub 上并非一类产品，而是 6 个层次分明的赛道。** 本次调研覆盖 49 个代表性项目，核心结论如下：

| # | 类别 | 一句话定位 | 项目数 | Star 中位数 | 代表项目 |
|---|---|---|---|---|---|
| A | **开发者框架 / Agent SDK** | 用代码编排 Agent，自由度最高 | 12 | ~2.8 万 | LangGraph、CrewAI、Google ADK |
| B | **可视化 / 低代码平台** | 拖拽编排、开箱即用、可自托管 | 10 | ~6.2 万 | n8n、Dify、Langflow、RAGFlow |
| C | **通用自主智能体** | 「你说它做」，能操作电脑/浏览器 | 11 | ~2.0 万 | **OpenClaw**、AutoGPT、OpenHands |
| D | **Agent-IDE / 编码工作台** | 以编码为唯一场景的 Agent 工作台 | 6 | ~3.2 万 | Cline、Aider、Continue |
| E | **基础设施 / 协议 / 运行时** | 决定工作台能力上限的底座 | 8 | ~2.6 万 | MCP、A2A、Browser Use、Mem0 |
| F | **知识库 / 研究型工作台** | 以调研与知识生产为核心 | 2 | ~3.0 万 | GPT-Researcher |

### 三个最关键的判断

1. **「通用工作台」的重心已经从「框架」转向「运行时 + 协议」。**
   2026 年最热的不是某个编排框架，而是 **OpenClaw**（39.2 万 Star，GitHub 历史星标第一）这种"本地优先的个人 Agent 运行时"，以及 **MCP**（工具连接标准）与 **A2A**（Agent 间协作标准）这类协议层。框架层反而在**收敛**——微软已把 AutoGen 与 Semantic Kernel 合并为统一的 Microsoft Agent Framework。

2. **可视化平台层已经跑出「四强格局」，但许可证是最大的坑。**
   n8n（20.7 万）、Dify（15.8 万）、Langflow（15.6 万）三家星标量级远超其他，加上字节的 Coze Studio（2.2 万）入局。但四家中**只有 Langflow 是纯 MIT**；n8n 是 Sustainable Use License（非 OSI 开源），Dify / FastGPT / Coze Studio 都是"基于 Apache 2.0 附加条件"的自定义许可。

3. **2026 年出现一波明显的"停运潮"，选型必须先看活跃度。**
   本次调研的 49 个项目中，**已有 5 个停止维护或归档**：Flowise（2026-08 归档）、Roo Code（2026-05 停运）、Void（已弃用）、Bytebot（2025-09 归档）、Devika（2025-09 后无提交）；Aider、bolt.diy 也进入停滞/维护模式。

---

## 二、分类地图：6 大类各自解决什么问题

### A 类｜开发者框架 / Agent SDK —— "用代码搭"

**解决什么问题**：需要精细控制流程、需要嵌入自有系统、需要生产级可观测性时，可视化平台不够用。

**共同特色**：
- 全部**模型无关**（都支持 OpenAI / Anthropic / Gemini / Ollama 等）
- 全部**原生支持 MCP**，多数同时支持 A2A
- 分化为四种编排范式：**图状态机**（LangGraph、Pydantic AI）、**角色扮演**（CrewAI）、**对话协商**（Microsoft Agent Framework 继承 AutoGen）、**工作流 + Agent 双范式**（Google ADK、Microsoft Agent Framework）

**2026 年格局变化**：
- 微软把 AutoGen + Semantic Kernel（累计 7.5 万 Star）合并为 **Microsoft Agent Framework**，2026-04 发布 1.0 GA
- **Google ADK 2.0** 主打 "Agent + Workflow" 双范式，把路由/循环/重试/并行/状态管理全部内置
- 三家原生 SDK 成型：**OpenAI Agents SDK**（+ AgentKit）、**Claude Agent SDK**（源自 Claude Code）、**Google ADK**

**选型提示**：
| 你的需求 | 推荐 |
|---|---|
| 复杂可控流程、需要断点续跑 | LangGraph |
| 快速搭多角色协作 | CrewAI |
| .NET 企业栈 | Microsoft Agent Framework |
| TypeScript 全栈 | Mastra |
| 强类型 / 可测试 | Pydantic AI |
| 数据/RAG 为中心 | LlamaIndex、Haystack |

---

### B 类｜可视化 / 低代码平台 —— "拖拽搭"

**解决什么问题**：非工程背景的团队成员（运营、产品、业务）也要能自己搭 AI 应用。

**共同特色**：
- **工作流 DAG 是绝对主流**——没有一个是原生"多 Agent 协商"架构，多 Agent 都是通过"Agent 节点 + 子工作流"组合实现
- 全部支持 MCP，全部可 Docker 自托管
- 普遍内置 RAG / 知识库、Prompt 编排、可观测性

**分层定位**：

| 项目 | 定位差异 | 许可风险 |
|---|---|---|
| **n8n** | 通用自动化长出 AI，400+ 集成可直接编排真实业务系统 | ⚠️ 非 OSI 开源，禁止 SaaS 转售 |
| **Dify** | LLMOps 全家桶，Chatflow + Workflow 双范式 | ⚠️ 自定义许可，禁止云服务转售 |
| **Langflow** | 可视化 LangChain，节点生态最广 | ✅ MIT，最宽松 |
| **RAGFlow** | 深度文档理解（DeepDoc：OCR + 版面分析 + 表格识别） | ✅ Apache-2.0 |
| **AnythingLLM** | 桌面端 + 一键部署 + 本地优先，可完全离线 | ✅ MIT |
| **FastGPT / Bisheng** | 国产化 / 信创友好，中文文档完善 | ⚠️ FastGPT 自定义 / ✅ Bisheng Apache-2.0 |
| **Coze Studio** | 字节扣子开源版，复用 SaaS 插件生态 | ✅ Apache-2.0 |
| **Flowise** | Node/TS 技术栈 | ⚠️ **已归档停更** |

**关键提醒**：`n8n / Dify / FastGPT` 的许可证都**不是**标准开源协议。商用前必须确认条款——尤其是"不得将其作为云服务对外转售"这类限制。

---

### C 类｜通用自主智能体 —— "你说它做"（本次调研重点）

**解决什么问题**：不想设计流程，直接说"帮我把下载目录里上周的截图按日期归档"，它就真的去读目录、建文件夹、移动文件。

**这是 2026 年最热、也是风险最高的一类。**

#### C 类内部其实分成两条路线

**路线一：本地个人 Agent（以 OpenClaw 为代表）**
- 核心卖点：**本地数据主权 + 消息渠道入口 + 技能生态**
- 架构范式：**Gateway 网关为中心的消息总线**（约 26 个 IM 平台桥接收敛到单个长驻 Node.js 进程）+ Agent 核心 + 技能库 + 心跳定时任务 + 本地双模记忆
- 典型项目：OpenClaw（39.2 万 Star）
- ⚠️ **代价是没有沙箱**——默认拿系统级权限，这也是它安全争议的根源

**路线二：任务型通用智能体（Manus 的开源平替们）**
- 核心卖点：多步骤任务自动化的能力上限
- 典型项目：OpenHands（9.1 万）、Open Interpreter（6.9 万）、OpenManus（5.9 万）、Suna/Kortix（2.0 万）、OWL（2.0 万）
- 能力标杆：OpenHands 的 SWE-bench Verified 约 53%+；OWL 的 GAIA 从 58.18 提升到 69.09

#### 沙箱隔离方案对比（安全边界由弱到强）

| 项目 | 隔离方案 | 风险等级 |
|---|---|---|
| **OpenClaw** | ❌ 无沙箱，默认系统级权限 | 🔴 极高 |
| **OpenManus / OWL** | ⚠️ 本地直接执行，需自行加固 | 🟠 高 |
| **OpenHands** | ✅ Docker 容器沙箱 | 🟡 中 |
| **Agent Zero** | ✅ Docker 容器（Kali Linux 环境） | 🟡 中 |
| **Bytebot** | ✅ Docker 容器 + NoVNC 可视化接管 | 🟡 中（但已停更） |
| **Suna / Kortix** | ✅✅ 每会话独立 microVM + 独立 git 分支 + 审批门 | 🟢 低 |

#### ⚠️ 必须知道的安全风险（OpenClaw）

- 工信部于 **2026-03-12 发布安全预警**；国家互联网应急中心列举密钥泄露、重要信息误删、**功能插件（Skills）投毒**、隐私泄露等风险
- **提示词注入**：网页/邮件中的隐藏恶意指令可诱导其泄露密钥或执行高危操作
- **ClawJacked 远程控制漏洞**：诱导用户访问恶意网页即可远程控制本地 Agent
- **权限失控**：默认系统级权限，可能误删文件/生产数据，造成不可逆损失

> **建议**：若要使用 OpenClaw 类本地 Agent，务必跑在独立虚拟机/容器中，用 E2B 等硬件级隔离方案"戴安全锁"，并严格审查第三方 Skills。

---

### D 类｜Agent-IDE / 编码工作台 —— "以编码为唯一场景"

**解决什么问题**：软件工程是 Agent 落地最成熟的场景，因此单独长出一类专用工作台。

**与 C 类的边界**：D 类的工具集（文件读写、终端、git、代码检索）与上下文全部围绕软件工程，交付物是代码变更；C 类虽然也能写代码，但目标是"操作电脑完成任意任务"。

**2026 年这一类的关键词是"洗牌"**：

| 项目 | 状态 | 特色 |
|---|---|---|
| **Cline** | ✅ 高度活跃 | Plan/Act 两阶段 + Checkpoint 快照回滚；IDE/CLI/SDK 三形态 |
| **Continue** | ✅ 活跃 | 补全 + 聊天 + Agent 三位一体；强私有化/自托管 |
| **Aider** | ⚠️ 2026-05 后无提交 | **git 原生**（每次修改自动 commit）+ **仓库地图 repo map**（tree-sitter 提取符号） |
| **bolt.diy** | ⚠️ 维护模式 | 浏览器内 WebContainers 全栈运行；22+ 模型可选 |
| **Roo Code** | ❌ 2026-05 停运 | 多模式（Code/Architect/Ask/Debug）系统 |
| **Void** | ❌ 已弃用 | Cursor 的开源替代路线 |

---

### E 类｜基础设施 / 协议 / 运行时 —— "决定上限的底座"

**这一层不是工作台，但工作台的每一次能力跃迁都由它驱动。**

| 子层 | 项目 | Star | 为工作台提供什么 |
|---|---|---|---|
| **连接协议** | MCP | 9,448（规范仓库） | Agent ↔ 工具 的即插即用标准（"Agent 的 USB-C"） |
| | A2A | 26,141 | Agent ↔ Agent 的跨组织协作标准（"Agent 的 TCP/IP"） |
| **网页操作** | Browser Use | 117,914 | DOM + Vision 混合感知的浏览器操作层 |
| **沙箱执行** | E2B | 14,339 | Firecracker microVM 硬件级隔离 |
| **记忆** | Mem0 | 67,149 | 事实抽取 + 混合检索的通用记忆层 |
| | Letta（原 MemGPT） | 25,125 | OS 式分层记忆的有状态 Agent 运行时 |
| **工具集成** | Composio | 30,541 | 1600+ 应用的工具集成与托管认证 |
| **可观测性** | Langfuse | 35,800 | LLM/Agent 追踪、评测、成本监控 |

#### 2026 年协议层两大变化

1. **MCP 完成标准化治理**：2025-12 由 Anthropic 捐赠给 **Linux Foundation 旗下的 Agentic AI Foundation（AAIF）**，OpenAI / Google / Microsoft / Block 等 30+ 企业为创始成员。
   > ⚠️ **数据口径提醒**：媒体广泛报道的"MCP 生态破 10 万 Server"存在夸大——官方 Registry 约 9,652 条（2026-05），Glama 索引 66,701（2026-08），33 个注册表去重后约 12,000+。建议采用官方 Registry 口径。

2. **A2A 纳入 Linux Foundation**：IBM 的竞争协议 ACP 已合并入 A2A，生态走向统一。MCP 与 A2A 是**互补而非竞争**关系——下层 MCP 管连接工具，上层 A2A 管 Agent 间协作。

#### 记忆层的技术路线之争

- **Letta 派（OS 式）**：把 LLM 当 CPU、上下文当内存、向量库当磁盘，Agent 自主决定写入/调取；core memory 可自我编辑，还有 sleep-time compute 在空闲时后台整理记忆
- **Mem0 派（事实抽取）**：无状态中间件，写入流程为"查重 → LLM 抽取事实 → 去重 embedding → 实体链接"，检索时语义向量 + BM25 + 实体匹配混合
  > ⚠️ Mem0 官方论文声称 LOCOMO 相对 OpenAI Memory 提升 26%，但官方声明高分"仅反映托管平台（含开源 SDK 不具备的专有优化）"，且 Zep / Hindsight / Honcho 三方公开质疑 LOCOMO 可比性，**无独立第三方复现验证**。另有中文场景硬伤：BM25 与实体抽取硬编码英文。

---

### F 类｜知识库 / 研究型工作台

**解决什么问题**：把"调研"这一高频场景做到极致，是通用工作台在垂直方向的收敛形态。

- **GPT-Researcher**（3.0 万 Star）：规划器-执行器 + 多 Agent 并行研究；20+ 检索器插件；v3.7.0 的 Jev 上下文过滤按"有用性"而非向量相似度筛选
- **Open Deep Research**（HuggingFace）：OpenAI Deep Research 的开源复现，GAIA 验证集 55% pass@1（原版 67%）；核心范式是 smolagents 的"用代码写动作"。⚠️ 独立仓库已 404，现作为 smolagents 示例分发

---

## 三、横向对比：关键维度速查

### 3.1 Star 排行（2026-10-14）

```
OpenClaw          ████████████████████████████████████████ 391,937
n8n               █████████████████████ 207,314
AutoGPT           ███████████████████ 187,566
Dify              ████████████████ 158,414
Langflow          ████████████████ 155,643
Browser Use       ████████████ 117,914
RAGFlow           █████████ 92,178
OpenHands         █████████ 90,847
Cline             ███████ 70,289
Open Interpreter  ███████ 68,574
Mem0              ███████ 67,149
AnythingLLM       ███████ 67,040
CrewAI            ██████ 59,675
OpenManus         ██████ 58,635
Flowise           ██████ 55,500
LlamaIndex        █████ 50,433
Aider             █████ 49,539
LangGraph         ████ 43,238
Khoj              ████ 37,679
Continue          ████ 36,218
Langfuse          ████ 35,800
Agno              ████ 34,000
Composio          ███ 30,541
GPT-Researcher    ███ 30,084
OpenAI Agents SDK ███ 30,023
FastGPT           ███ 29,817
Void              ███ 28,759
smolagents        ███ 27,944
A2A               ███ 26,141
Letta             ███ 25,125
Mastra            ███ 24,972
Haystack          ███ 24,800
Roo Code          ███ 24,281
Google ADK        ██ 21,826
Coze Studio       ██ 21,709
Suna/Kortix       ██ 20,273
OWL               ██ 20,151
bolt.diy          ██ ~20,000
Devika            ██ 19,553
Agent Zero        ██ 19,458
Pydantic AI       ██ 16,900
E2B               █ 14,339
Microsoft AF      █ 14,120
Bisheng           █ 12,047
UI-TARS           █ 11,596
Bytebot           █ 11,075
MCP (spec)        █ 9,448
Claude Agent SDK  █ 8,273
```

> Star 数不等于质量，但能反映社区关注度。注意：**已停更项目的 Star 是历史存量**（Flowise 5.5 万、Roo Code 2.4 万、Void 2.9 万），不代表可维护性。

### 3.2 许可证风险矩阵

| 风险 | 许可证 | 项目 |
|---|---|---|
| 🟢 **最宽松** | MIT | LangGraph、CrewAI、OpenAI Agents SDK、Claude Agent SDK、LlamaIndex、Pydantic AI、Langflow、AnythingLLM、OpenClaw、AutoGPT(Classic)、OpenHands、OpenManus、Devika、Browser Use、Composio、Langfuse(核心)、Bytebot、bolt.diy |
| 🟢 **宽松** | Apache-2.0 | Google ADK、smolagents、Agno、Haystack、RAGFlow、Bisheng、Coze Studio、UI-TARS、Open Interpreter、Cline、Continue、Aider、Void、Roo Code、A2A、Letta、E2B、GPT-Researcher、MCP(SDK) |
| 🟡 **注意** | 附加商业条款 / 双轨 | Dify、FastGPT、Flowise、Mastra、n8n（Sustainable Use）、Langfuse(ee/)、AutoGPT(Platform: Polyform Shield)、MCP(规范仓库) |
| 🔴 **限制强** | AGPL-3.0 / 自定义不明 | Khoj（AGPL）、OWL（协议文件缺失）、Suna（NOASSERTION）、Agent Zero（自定义） |

### 3.3 活跃度红绿灯（选型第一道关）

| 状态 | 项目 |
|---|---|
| ✅ **高度活跃**（2026-10 仍有提交） | OpenClaw、n8n、Dify、Langflow、RAGFlow、AnythingLLM、Cline、Continue、AutoGPT、OpenHands、Browser Use、Mem0、Langfuse、Composio、A2A、MCP、E2B、Letta、CrewAI、LangGraph、Google ADK、Microsoft AF、Suna、Agent Zero、OWL、OpenManus、GPT-Researcher、Bisheng、FastGPT、Coze Studio、Open Interpreter、Haystack、Mastra、Pydantic AI、Agno、smolagents |
| ⚠️ **放缓 / 维护模式** | Khoj、LlamaIndex（开源侧）、UI-TARS（模型侧）、Aider、bolt.diy |
| ❌ **停运 / 归档** | **Flowise**（2026-08-13 归档）、**Roo Code**（2026-05-15 停运）、**Void**（已弃用）、**Bytebot**（2025-09-12 归档）、**Devika**（2025-09-25 后无提交） |

---

## 四、2026 年五大趋势

1. **从"框架"到"运行时"**：竞争重心从"怎么编排"转向"跑在哪里、记得住什么、连得上什么"。OpenClaw 的 Gateway 架构、Suna 的每会话沙箱、Letta 的记忆操作系统，都是运行时层的创新。

2. **协议层完成标准化**：MCP（Anthropic → AAIF）+ A2A（Google → Linux Foundation）构成"下层连接工具、上层连接 Agent"的双层标准栈。**任何不支持 MCP 的工作台在 2026 年都算生态落后**。

3. **沙箱隔离成为分水岭**：从 OpenClaw 的"裸奔"到 E2B 的 Firecracker microVM 硬件级隔离，安全边界正在成为通用工作台的核心竞争力，也是监管关注焦点。

4. **记忆成为下一个差异化战场**：Letta 的 OS 式分层记忆 vs Mem0 的事实抽取中间件，两条路线尚未分出胜负，但基准数字的"罗生门"（厂商自报 vs 第三方质疑）说明这个领域还不够成熟。

5. **IDE 插件赛道洗牌**：Roo Code 停运、Void 弃用、Aider 停滞，而云端 Agent（Roomote 等）兴起——说明"VS Code 插件"这一形态可能正在被"云端沙箱 Agent"取代。

---

## 五、选型决策树

```
你的需求是什么？
│
├─ 要嵌入自有系统、需要精细控制流程
│   └─ → A 类：LangGraph（复杂流程）/ CrewAI（快速协作）/ Mastra（TS 栈）
│
├─ 团队里有非工程师，要可视化搭
│   ├─ 要宽松许可 → Langflow（MIT）/ Bisheng（Apache-2.0）
│   ├─ 要编排真实业务系统 → n8n（注意许可）
│   ├─ 要 LLMOps 全家桶 → Dify（注意许可）
│   └─ 要处理复杂扫描件/表格文档 → RAGFlow
│
├─ 想让它直接操作我的电脑/浏览器
│   ├─ 个人使用、要数据留在本地 → OpenClaw（⚠️ 必须加沙箱隔离！）
│   ├─ 要企业级治理与审计 → Suna/Kortix
│   ├─ 要 Docker 隔离 → Agent Zero / OpenHands
│   └─ 要网页自动化 → Browser Use
│
├─ 主要是写代码
│   ├─ VS Code 内 → Cline
│   ├─ 要企业私有化 → Continue
│   ├─ 终端党、重视 git 可追溯 → Aider
│   └─ 浏览器内生成全栈应用 → bolt.diy
│
├─ 要给它加"记忆"
│   ├─ 只是给现有应用加记忆 → Mem0（⚠️ 中文场景需注意）
│   └─ 要完整的"有状态 Agent 运行时" → Letta
│
└─ 要做深度调研
    └─ → GPT-Researcher
```

---

## 六、数据可信度说明

本次调研对每条数据都做了来源标注，需特别注意以下**未完全核实项**：

| 项目 | 未核实内容 |
|---|---|
| 各项目 Star 数 | 除使用 GitHub API 一手抓取的之外，部分为量级估算（已在 JSON 中标注） |
| MCP 生态规模 | "破 10 万 Server"与官方 Registry ~9,652 口径严重不符，疑为多目录聚合夸大 |
| A2A v1.0 GA 日期 | 2026-03 与 2026-07 两种说法并存 |
| Mem0 基准成绩 | 官方自报 LOCOMO 92.5，但声明仅适用于托管平台；Zep/Hindsight/Honcho 公开质疑，无第三方复现 |
| Agno 性能宣传 | "快 5000 倍"未经独立验证，营销口径 |
| OpenHands SWE-bench | ~53% 来自二手来源，具体模型/版本需以官方为准 |
| OWL 许可证 | GitHub 未检测到标准协议文件，商用合规性存疑 |
| Suna / Agent Zero 许可证 | GitHub 识别为 NOASSERTION，具体条款未一手确认 |
| Open Deep Research | 独立仓库 2026-10-14 返回 404，现作为 smolagents 示例分发 |
| notable_users | 多数项目的"知名使用方"来自第三方博客/发布会报道，未经官方逐一确认 |

**方法论**：所有 Star / License / 语言 / 提交时间优先通过 `api.github.com/repos/{owner}/{repo}` 一手抓取；项目定位、架构、社区评价通过官方 README/文档与多方来源交叉验证；对存在冲突的信息，在报告中明确标注而非选择性呈现。

---

## 附录：完整项目清单（49 个）

**A 开发者框架/SDK（12）**：LangGraph、Microsoft Agent Framework、CrewAI、OpenAI Agents SDK、Claude Agent SDK、Google ADK、LlamaIndex、smolagents、Pydantic AI、Agno、Mastra、Haystack

**B 可视化/低代码平台（10）**：n8n、Dify、Langflow、RAGFlow、AnythingLLM、FastGPT、Khoj、Bisheng、Flowise、Coze Studio

**C 通用自主智能体（11）**：OpenClaw、AutoGPT、OpenHands、Open Interpreter、OpenManus、Suna(Kortix)、OWL、Agent Zero、Devika、UI-TARS、Bytebot

**D Agent-IDE/编码工作台（6）**：Cline、Aider、Continue、Void、Roo Code、bolt.diy

**E 基础设施/协议/运行时（8）**：Browser Use、Mem0、Langfuse、Composio、A2A、Letta、E2B、MCP

**F 知识库/研究型工作台（2）**：GPT-Researcher、Open Deep Research
