# B 类｜可视化 / 低代码 Agent 平台（10 个）

> 这一类是"拖拽搭"的平台：开箱即用、可自托管，面向业务人员与团队。
> 数据快照：2026-10-14 · 标注 `[不确定]` 的为未能一手核实项

---

## 1. n8n

> **定位**：通用自动化工作流平台，近两年成长为 AI Agent 编排的热门选择
> **仓库**：https://github.com/n8n-io/n8n · **Star**：207,314 · **License**：Sustainable Use License（非 OSI 开源） · **语言**：TypeScript · **维护方**：n8n GmbH（德国柏林，创始人 Jan Oberhauser） · **状态**：✅ 极活跃（2.43.4，2026-10-12）

### 它是什么

n8n 最初是**通用工作流自动化工具**（对标 Zapier / Make），核心能力是"把 400+ 个 SaaS 系统连起来"。近两年它长出了 AI Agent 能力——通过内置的 AI Agent 节点（底层由 LangChain 驱动）和工具节点，把 LLM 编排直接接进了它原本强大的集成网络。

这个出身决定了它的独特价值：**其他平台是"AI 平台加集成"，n8n 是"集成平台加 AI"**。当你的 Agent 需要真的去操作 CRM、发邮件、写数据库、调内部 API 时，n8n 的集成深度是其他可视化平台难以匹敌的。

它的另一个特点是**可视化 + 代码混合**：画布上拖节点，需要时随时插入 JS/Python 代码节点。

### 核心架构与编排范式

- **工作流 DAG 为主** + AI Agent 节点
- **AI Agent 节点**：由 LangChain 驱动，可挂载工具节点
- **子工作流**：通过 Execute Workflow 节点实现复用与多 Agent 组合
- **触发器体系**：Webhook、定时、表单、事件触发等

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | ⭐ **400+ 集成节点** + 自定义 HTTP/代码节点 + AI 工具节点，可直接编排真实业务系统 |
| **记忆机制** | AI 节点支持会话记忆（memory） |
| **MCP 支持** | ⭐ **原生双向**：既作 MCP 客户端（MCP Client Tool 节点调用外部 MCP Server），又可暴露自身为 MCP Server |
| **沙箱/执行** | 代码节点执行 JS/Python，运行于自托管自身环境（隔离取决于部署） |
| **人机协作** | ✅ 支持（Wait 节点、表单/审批触发等人机协作机制） |
| **RAG** | 通过内置 Vector Store 节点实现 RAG |

### 快速上手

```bash
# Docker（官方推荐）
docker run -it --rm --name n8n -p 5678:5678 \
  -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n

# 或 npm（需 Node.js 20/22）
npx n8n
```

**首次使用**：访问 `http://localhost:5678` → 创建 Owner 账号 → 新建 Workflow → 拖拽节点连线 → Execute Workflow 测试。
**最低资源**：内存约 2 GB 起；生产建议配反向代理 + 外部 Postgres。
**上手难度**：★★★☆☆ —— 单命令即可跑起来，但节点/凭证/表达式体系较陡。

### 差异化特色

1. **400+ 集成 + 通用自动化基因**：AI Agent 可直接编排真实业务系统（CRM/邮件/数据库等）
2. **同时作为 MCP 客户端与服务端**，实现双向 AI 互操作
3. **可视化画布 + 自定义代码混合编程**，灵活度高
4. 社区规模极大（约 6.1 万 forks），文档多语言（**含中文**）

### 局限与风险

1. ⚠️ **非 OSI 开源许可**（Sustainable Use License），禁止作为 SaaS 竞品转售，商用需注意条款
2. 学习曲线较陡；RBAC/SSO 等企业功能需付费版
3. AI Agent 能力相对 Dify/Langflow 等专用平台更偏通用自动化，深度较浅

### 适合谁 / 典型场景

业务流程/IT 自动化与定时任务；AI Agent 接入企业系统完成跨应用任务；事件触发的数据处理与集成流水线。

---

## 2. Dify

> **定位**：开源 LLM 应用与 Agent 工作流平台，LLMOps 一体化
> **仓库**：https://github.com/langgenius/dify · **Star**：158,414 · **License**：Dify Open Source License（基于 Apache 2.0 附加条件） · **语言**：TypeScript + Python · **维护方**：LangGenius（中国） · **状态**：✅ 极活跃

### 它是什么

Dify 是国产开源 LLM 应用平台的标杆，定位是 **"LLMOps 全家桶"**——把 Prompt 编排、RAG 知识库、Agent、工作流、可观测性、标注反馈闭环全部做进一个产品。

它的核心设计是**双工作流范式**：`Chatflow`（面向对话场景）和 `Workflow`（面向自动化任务）分开建模。这个区分很实用，因为对话流需要考虑多轮上下文与变量，而自动化流更接近传统 DAG 编排。

Dify 的另一个杀手锏是**可插拔性**：模型供应商、工具、向量库都可以替换，并对外提供 Backend-as-a-Service API，方便把 AI 能力嵌进已有业务系统。UI 与文档全中文，是国内团队上手成本最低的选择之一。

### 核心架构与编排范式

- **工作流 DAG**：含 LLM / 代码 / 条件分支 / 循环等节点
- **Agent 节点**：支持 ReAct / Function Calling 两种模式
- **工作流嵌套**：通过子工作流实现多 Agent 组合（非原生多 Agent 协商）
- **双范式**：Chatflow（对话流）与 Workflow（自动化流）

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置大量工具 + 自定义 API 工具 + 工作流即工具 + 代码执行节点（Python/Node.js）；可挂载 MCP 工具 |
| **记忆机制** | 会话变量 + 对话记忆（短期）；长期记忆依赖知识库检索实现 |
| **MCP 支持** | ✅ 原生支持（MCP 客户端/服务端，1.6+ 版本引入） |
| **沙箱/执行** | 代码执行节点在受限沙箱中运行 Python/Node.js |
| **人机协作** | 较弱：支持单步调试/运行日志回放与对话式人工介入 |
| **RAG** | ✅ 内置 RAG 管道与知识库，支持多数据源导入、分段、多向量库（可插拔） |

### 快速上手

```bash
git clone --branch "$(curl -s https://api.github.com/repos/langgenius/dify/releases/latest | jq -r .tag_name)" \
  https://github.com/langgenius/dify.git
cd dify/docker
cp .env.example .env
docker compose up -d          # 需 Docker Compose >= 2.24.0
docker compose ps             # 验证容器状态
```

**首次使用**：访问 `http://localhost/install` 初始化管理员 → 登录 `http://localhost` → 「设置 → 模型供应商」填 API Key → 创建应用 → 上传知识库文档。
**最低资源**（官方明确）：**CPU ≥ 2 Core，RAM ≥ 4 GiB**；启动约 7 个核心服务 + 8 个依赖组件（weaviate、postgres、redis、nginx、sandbox 等）。无需 GPU。
**上手难度**：★★★☆☆ —— 一条 `docker compose up -d` 即可，但组件多、首次需配置模型供应商与向量库。

### 差异化特色

1. **LLMOps 全家桶**：Prompt 编排、RAG、Agent、可观测性、标注反馈闭环一体，覆盖应用全生命周期
2. **双工作流范式**：Chatflow（对话流）与 Workflow（自动化流）分离
3. **模型/工具/向量库高度可插拔**，并提供 Backend-as-a-Service API
4. **中文体验极佳**：官方中文文档、全中文 UI、中文社区庞大

### 局限与风险

1. **开源版与企业版边界**：SSO/RBAC/多租户等企业特性仅企业版提供
2. **自定义许可禁止将 Dify 直接作为云服务转售**，商用需注意条款
3. 复杂多 Agent 协作与精细条件逻辑不如代码框架（如 LangGraph）灵活

### 适合谁 / 典型场景

企业私有知识库问答与智能客服；多模型 LLM 应用/Agent 快速搭建与运营；将 AI 能力通过 API 嵌入现有业务系统。

---

## 3. Langflow

> **定位**：基于 LangChain 的可视化拖拽式 Agent 构建工具
> **仓库**：https://github.com/langflow-ai/langflow · **Star**：155,643 · **License**：**MIT** · **语言**：Python · **维护方**：Langflow 团队（2024 年被 DataStax 收购，现由 IBM/DataStax 支持） · **状态**：✅ 极活跃（v1.12.6，2026-10-13）

### 它是什么

Langflow 把 LangChain 的**组件生态可视化**了：每个节点就是一个 LangChain 组件，你在 React Flow 画布上连线，就完成了一次编排。因为 LangChain 的组件库极其庞大，Langflow 的**节点数量与集成广度在同类工具里领先**。

它最大的商业优势是 **License 最宽松（纯 MIT）**——在本次调研的 B 类十强里，它是唯一一个不带任何附加商业条款的。对于需要二次开发、或者对许可合规敏感的企业，这一点往往比功能差异更关键。

它基于 React Flow 的画布支持把流程**即时导出为可调用 API 或嵌入组件（Embedded Chat）**，从原型到上线的路径很短。

### 核心架构与编排范式

- **工作流 DAG**：节点即 LangChain 组件
- **多 Agent**：支持 multiagent 模式
- **Playground**：画布内直接测试对话
- **API / 嵌入导出**：流程可发布为 API 或 iframe 组件

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 组件即工具，支持自定义 Python 组件、工具调用与代码执行 |
| **记忆机制** | 提供会话记忆组件 |
| **MCP 支持** | ✅ 支持（提供 MCP 组件 / 可暴露为 MCP Server） |
| **沙箱/执行** | 支持代码执行组件（Python），可在流程内运行自定义代码 |
| **人机协作** | [不确定] |
| **RAG** | ✅ 内置 RAG 与向量库组件，支持多种向量数据库 |

### 快速上手

```bash
pip install langflow
langflow run            # 默认启动 Web UI
# 或一次性： uvx langflow run
# Docker： docker run -p 7860:7860 langflowai/langflow:latest
```

**首次使用**：访问 `http://localhost:7860` → 从左侧组件库拖入 LLM/Embedding/Vector Store 节点 → 填 API Key → 连成 Flow → Playground 测试 → 通过 API 端点发布。
**最低资源**：轻量，Python 3.10+ 环境，内存约 2 GB 起。
**上手难度**：★★☆☆☆ —— pip 安装即用，可视化拖拽最直观，属最低门槛之一。

### 差异化特色

1. **深度绑定 LangChain 组件生态**，可用节点数量与集成广度在同类工具中领先
2. **基于 React Flow 的画布**，任一流程可即时导出为可调用 API 或嵌入组件
3. **MIT 许可（最宽松）**，商用限制少——这是 B 类十强中唯一的纯 MIT
4. 支持通过 MCP 与外部 AI 助手互操作

### 局限与风险

1. LangChain 概念多，非技术用户学习曲线较陡
2. 复杂/大规模流程的生产部署仍需额外工程化工作
3. 第三方组件质量参差，版本兼容问题较多；**无官方中文文档**

### 适合谁 / 典型场景

RAG 应用与聊天机器人快速原型；多 Agent 可视化工作流搭建；将 LangChain 能力可视化封装为 API 服务。

---

## 4. RAGFlow

> **定位**：以"深度文档理解"为核心差异化的开源 RAG 引擎 + Agent 平台
> **仓库**：https://github.com/infiniflow/ragflow · **Star**：92,178 · **License**：Apache-2.0 · **语言**：Go（后端主语言）+ Python + TypeScript · **维护方**：InfiniFlow 英飞流（中国·上海） · **状态**：✅ 极度活跃

### 它是什么

RAGFlow 把**"文档解析"当成一等公民**——这是它与所有其他 RAG 平台的根本区别。

大多数 RAG 系统的瓶颈不在检索，而在**解析**：一份扫描版合同 PDF，如果解析出来是乱的，后面的向量化、检索、生成全都建立在错误的基础上。RAGFlow 的 **DeepDoc 引擎**专门解决这个问题：内置 OCR、**版面分析（Layout Recognition）**（识别文本/标题/表格/图/公式/页眉页脚等版面区域）与**表格结构识别（TSR）**，把扫描件与复杂版式 PDF 还原为**带坐标的结构化内容**。

在此之上还有**模板化分块（chunk template）**：按 General / 论文 / 手册 / 简历 / 表格 / 书籍 / 法律 / PPT 等文档类型选择不同的分块策略，显著提升召回质量。回答时支持**可点击溯源到原文切片**。

这是国产项目，中文文档与中文社区完善，国内可用性好。

### 核心架构与编排范式

- **可视化工作流 DAG**：节点式 Agent 编排
- **Agent 内多轮工具调用**
- **检索即上下文**：为 Agent 提供可溯源的引用
- **GraphRAG / 知识图谱**：支持图谱增强检索

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 支持 function calling；内置/可配置工具节点（网页搜索、代码执行等） |
| **记忆机制** | 会话级短期记忆（多轮对话上下文） |
| **MCP 支持** | ✅ 支持（较新版本引入） |
| **沙箱/执行** | 提供代码执行组件（sandbox），隔离以容器为主 |
| **人机协作** | 工作流支持人工介入节点/输入节点 |
| **RAG** | ⭐⭐ **核心卖点**：多格式解析、模板化分块、向量+关键词混合检索、可配 rerank |

### 快速上手

```bash
# 1) 先提高 Elasticsearch 所需的内核参数
sudo sysctl -w vm.max_map_count=262144      # 需 >= 262144
# 2) 克隆并启动
git clone https://github.com/infiniflow/ragflow.git
cd ragflow/docker
docker compose -f docker-compose.yml up -d
docker logs -f ragflow-cpu                  # 查看初始化
curl -f http://localhost/api/v1/system/healthz   # 健康检查
```

**首次使用**：打开 `http://<机器IP>` 登录 → 「Model providers」填 LLM/Embedding API Key → 设默认模型 → 创建 dataset 并上传文件解析 → 创建 Chat 助手绑定 dataset。
**最低资源**（官方明确）：**推荐起步 4 CPU 核、16 GB RAM、50 GB 空闲磁盘**。需 Docker ≥ 24.0.0、Compose ≥ v2.26.1。DeepDoc 用 CPU 推理；本地 LLM 建议 GPU。
**上手难度**：★★★★☆ —— 资源门槛高（16 GB 内存起步）、需调内核参数、必须配置模型与向量/ES 引擎。

### 差异化特色

1. **DeepDoc 文档解析引擎**：OCR + 版面分析 + 表格结构识别，把扫描件还原为带坐标的结构化内容——这是它相对一般 RAG 框架的核心壁垒
2. **模板化分块**：按文档类型选择分块策略，显著提升召回质量
3. **RAG 与 Agent 融合**：回答可点击溯源到原文切片
4. **工程化完整**：可视化知识库管理、GraphRAG/知识图谱、多向量库后端

### 局限与风险

1. **资源占用高**，Docker 部署对内存/GPU 有一定要求，首次部署与调优有学习曲线
2. 文档解析质量高度依赖 DeepDoc 模型，对极端版式仍可能出现表格/公式错位，需人工校验
3. 版本迭代快，API/界面变动较频繁；部分能力（MCP、GraphRAG）成熟度待验证

### 适合谁 / 典型场景

合同/招投标/财报等长文档、扫描件的企业级知识问答与要素抽取；把复杂版式 PDF（含表格、双栏、公式）建成可检索知识库并做带引用问答；基于知识库的客服/内部助手。

---

## 5. AnythingLLM

> **定位**："一体化、本地优先"的私有化知识库与 Agent 应用
> **仓库**：https://github.com/Mintplex-Labs/anything-llm · **Star**：67,040 · **License**：**MIT** · **语言**：JavaScript（Node.js 全栈） · **维护方**：Mintplex Labs（美国） · **状态**：✅ 极活跃

### 它是什么

AnythingLLM 走的是一条与 Dify 完全相反的路线：**"桌面端 + 一键部署 + 本地优先"**。

它内置了 `llama.cpp`，可以直接跑本地模型，内置本地嵌入模型与向量库（LanceDB），**不需要任何外部依赖**就能获得一个完整的知识库+Agent。这意味着真正的**离线可用**——文档与向量完全留在本机。对个人用户、小团队、以及数据不能出内网的场景，这是最省心的选择。

它的核心组织单位是 **Workspace（工作区）**：每个工作区有独立的文档与向量空间，轻量地管理多个主题知识库。License 是 MIT，商用限制最少。

### 核心架构与编排范式

- **单 Agent + Agent 技能（工具）+ Agent Flows（可视化流程）**
- **Workspace 隔离模型**：每个工作区独立文档与向量空间
- **多形态**：桌面 App / 自托管 Docker / 云托管
- **多端入口**：桌面 + 浏览器 + 移动端

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | Agent 技能/工具（含网页抓取、文档操作、代码等）、自定义工具，并支持 MCP |
| **记忆机制** | 工作区（Workspace）级记忆 + 长期记忆（@agent 记忆），可跨会话保留 |
| **MCP 支持** | ✅ 原生支持（可作为 MCP 客户端接入外部工具） |
| **沙箱/执行** | ⚠️ Agent 可在桌面端执行代码并访问本地文件系统（本地优先带来便利，但隔离性弱于容器沙箱） |
| **人机协作** | 有限：Agent 流程中可查看/干预步骤，但缺少企业级审批流 |
| **RAG** | ✅ 内置：按工作区投喂文档/网页，支持多种向量数据库（内置 LanceDB，可选 Pinecone/Chroma 等） |

### 快速上手

```bash
docker run -d -p 3001:3001 --name anythingllm \
  -v $PWD/anythingllm:/app/server/storage \
  -e STORAGE_DIR="/app/server/storage" \
  mintplexlabs/anythingllm
```

**首次使用**：访问 `http://localhost:3001` → 选择 LLM 与 Embedder（可用内置本地模型或填 API Key）→ 新建 Workspace → 上传文档并 Embed → 聊天提问。
**最低资源**：轻量，内存约 2 GB 起，无需 GPU（用云 LLM 时）；有 Mac/Win/Linux 桌面版一键安装。
**上手难度**：★★☆☆☆ —— 提供桌面安装包 + 单容器部署，开箱即用程度高。

### 差异化特色

1. **"桌面端 + 一键部署"路线**：单机安装即可获得完整知识库+Agent，**内置本地 LLM 与嵌入模型，真正离线可用**——与 Dify 的"自托管 Docker + 企业级多应用编排"定位形成差异
2. **Workspace 隔离模型**：轻量管理多主题知识库
3. **隐私优先/数据自持**：文档与向量可完全留在本机
4. **MIT 许可**，商用限制最少，易于二次开发

### 局限与风险

1. 复杂多应用编排与权限体系弱于 Dify 等企业级平台，大规模多租户场景能力有限
2. ⚠️ **桌面端 Agent 可直接访问本地文件系统，沙箱隔离较弱**，存在安全/权限风险
3. 部分高级功能（云同步、企业特性）与商业版绑定

### 适合谁 / 典型场景

个人/小团队私有知识库问答（个人电脑本地运行，数据不出本机）；企业内部文档助手（自托管 Docker，接入公司模型 API）；快速搭建带工具调用的本地 Agent。

---

## 6. FastGPT

> **定位**：国产知识库问答 + 可视化工作流编排平台
> **仓库**：https://github.com/labring/FastGPT · **Star**：29,817 · **License**：FastGPT 开源许可证（基于 Apache 2.0 附加条件） · **语言**：TypeScript（Next.js） · **维护方**：Labring 环界云（中国） · **状态**：✅ 活跃（v4.17.2，2026-10-09）

### 它是什么

FastGPT 是国产开源 RAG 平台的另一代表，与 Dify 相比它**更聚焦知识库问答**：数据导入、清洗、切分、混合检索与重排的流水线做得更完整，并在此基础上提供可视化 Flow 工作流与 Agent 编排。

它的生态依托 **Sealos**（环界云自家的云操作系统），因此云托管与私有化部署都很顺。中文文档完善、国内社区活跃，是"要做一个中文企业知识库问答"时的常见选择。

需要留意的是许可证：它基于 Apache 2.0 但附加了规模限制——**超出一定规模商用需授权**。

### 核心架构与编排范式

- **工作流 DAG（Flow）** + Agent（工具调用/任务规划）
- **知识库为中心**：导入 → 清洗 → 切分 → 索引 → 检索 → 重排
- **应用形态**：对话应用 / 工作流应用

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 工作流工具 + 插件 + 代码执行 |
| **记忆机制** | 会话记忆 + 知识库长期检索 |
| **MCP 支持** | ✅ 支持 |
| **沙箱/执行** | 支持代码节点执行 |
| **人机协作** | [不确定] |
| **RAG** | ⭐ **核心强项**：内置知识库、数据导入/清洗/切分、混合检索与重排 |

### 快速上手

```bash
git clone https://github.com/labring/FastGPT.git
cd FastGPT/deploy          # 官方部署目录（含 docker-compose.yml）
docker compose up -d
```

**首次使用**：访问 `http://localhost:3000` → 登录（默认管理员，首次应改密码）→ 在「账号/模型」配置模型渠道（one-api）→ 创建知识库并上传文档、选索引模型 → 创建应用绑定知识库。
**最低资源**：中等，建议内存 4 GB 起（含 one-api、向量库 pgvector/Milvus、MongoDB）。
**上手难度**：★★★☆☆ —— 一条 compose 起服务，但模型渠道与向量库配置步骤较多。

### 差异化特色

1. **知识库/RAG 能力突出**：完整的数据导入、切分、混合检索与重排流水线
2. **可视化 Flow 工作流 + Agent 编排一体化**，开箱即用
3. **国产化适配好**：中文文档、私有化部署、与 Sealos 云操作系统生态集成
4. 社区版 + 商业版（FastGPT Pro）双轨

### 局限与风险

1. **自定义许可对大规模商用有限制**（超出规模需商业授权）
2. 生态/插件规模小于 Dify/n8n
3. 复杂 Agent 逻辑表达能力相对有限

### 适合谁 / 典型场景

企业私有知识库问答与智能客服；基于文档的 RAG 应用快速搭建；私有化部署的国产 AI 应用。

---

## 7. Bisheng（毕昇）

> **定位**：面向企业的国产开源 LLM 应用开发平台（LLMOps）
> **仓库**：https://github.com/dataelement/bisheng · **Star**：12,047 · **License**：Apache-2.0 · **语言**：Python · **维护方**：DataElement 数据元素（中国·北京） · **状态**：✅ 活跃（v2.6.0-fix2，2026-08-11）

### 它是什么

在本次调研的 B 类十个平台里，**Bisheng 的企业级功能最全**。它不只是"工作流 + 知识库"，而是原生集成了：模型管理、评测（Evaluation）、**SFT 微调**、数据集管理、可观测性、企业级系统管理——相当于把一整套 LLMOps 流程装进一个平台。

这决定了它的定位：**不是给个人快速试用的，而是给企业做长期 AI 平台建设的**。代价是部署与运维较重、组件多、资源要求高。

它对国产化/信创场景支持最好：中文优先、支持国产大模型与本地化部署、适配国内合规与私有化要求。文档解析与 OCR 能力也针对中文复杂文档（合同、招投标、报告）做了强化。

### 核心架构与编排范式

- **可视化工作流 DAG**（拖拽式流程编排）
- **Agent**：ReAct 类自主循环，可作为工作流节点
- **模型管理**：统一接入闭源与开源模型
- **BiSheng Flow / Linsight**：工作流搭建与数据分析

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置工具节点（检索、代码、HTTP、OCR 等），支持自定义工具与代码节点 |
| **记忆机制** | 会话级短期记忆；平台侧含对话历史管理 |
| **MCP 支持** | ✅ 较新版本支持 MCP 接入 |
| **沙箱/执行** | 提供代码节点/代码执行能力，隔离以容器为主 |
| **人机协作** | 工作流支持人工节点/审批与输入，流程可中断查看 |
| **RAG** | ✅ 内置知识库：文档解析（含 OCR）、向量化、检索问答 |

### 快速上手

```bash
git clone https://github.com/dataelement/bisheng.git
cd bisheng/docker
docker compose up -d
```

**首次使用**：访问 `http://localhost:3001` → 默认管理员登录 → 配置模型（LLM/Embedding）→ 创建知识库上传文档 → 进入「工作流/BiSheng Flow」搭建应用。
**最低资源**：**较重**，建议内存 16 GB 起（若含本地模型/向量检索组件），磁盘数十 GB；本地大模型需 GPU。
**上手难度**：★★★★☆ —— 组件多、资源要求高、企业级配置复杂。

### 差异化特色

1. **企业级功能最全的一档**：除工作流与 RAG 外，原生集成模型管理、评测、SFT 微调、数据集管理、可观测性与企业级系统管理
2. **国产化/信创友好**：中文优先、支持国产大模型与本地化部署
3. **强大的文档解析与 OCR 能力**（面向合同、招投标、报告等中文复杂文档）
4. 存在 3.0-beta 分支，持续演进

### 局限与风险

1. **部署与运维较重**，组件多、资源要求高，非技术用户上手门槛高于 Dify 等轻量平台
2. 社区规模与生态（插件/模板市场、第三方教程）小于 Dify/RAGFlow，英文资料较少
3. 部分高级能力（SFT、评测）面向企业版/专业场景，开源版与商业版能力存在差异

### 适合谁 / 典型场景

企业合同/招投标/风控文档的智能审核与要素抽取；面向业务部门的可视化工作流应用搭建；企业私有化知识库问答 + 模型微调/评测的一体化 LLMOps。

---

## 8. Khoj

> **定位**："个人 AI 第二大脑"，把本地/在线文档与联网检索统一为可问答、可自动化的个人助手
> **仓库**：https://github.com/khoj-ai/khoj · **Star**：37,679 · **License**：AGPL-3.0 · **语言**：Python · **维护方**：Khoj AI（美国） · **状态**：⚠️ 中等活跃（2.0 仍 beta，近期提交放缓）

### 它是什么

Khoj 的定位在 B 类里最独特：**它不是"搭应用的平台"，而是"个人知识助手"**。

它深度绑定个人知识工作者的工作流：可以索引本地文档（含 **Obsidian**、Markdown）、PDF 与在线内容，做语义搜索与问答；提供桌面端、移动端、浏览器插件、以及 **Obsidian / Emacs 插件**；还能接入 WhatsApp 等入口。更特别的是它有**定时自动化（Scheduled Automations）**——可以设定时执行研究/总结任务，比如每天早上汇总资讯。

对"用 Obsidian 管理笔记"的人来说，Khoj 是最贴合的工具。

需要留意两个风险：**AGPL-3.0** 对闭源商用与二次分发限制较强；**2.0 版本从 2026 年初起一直处于 beta**（最新 2.0.0-beta.28，2026-03-26），且近期提交频率低于同类头部项目。

### 核心架构与编排范式

- **单 Agent + 自定义 Agent + 定时自动化 + 深度研究模式**
- **多端入口**：桌面 / 移动 / 浏览器插件 / 编辑器插件
- **内容源接入**：本地文档、Obsidian、GitHub、PDF、在线内容

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置工具（联网搜索、代码执行、图像生成、文档检索等），可组合到自定义 Agent |
| **记忆机制** | 长期记忆（可开关，默认开启），用于个性化与跨会话上下文 |
| **MCP 支持** | [不确定] |
| **沙箱/执行** | 提供代码执行工具，能力有限，隔离程度以官方文档为准 |
| **人机协作** | 有限（对话式交互为主，自动化任务可查看结果） |
| **RAG** | ✅ 内置：可索引本地文档（含 Obsidian/Markdown）、PDF 与在线内容，做语义检索问答 |

### 快速上手

```bash
git clone https://github.com/khoj-ai/khoj.git
cd khoj
docker compose up -d
# 也支持 pip install khoj 或桌面/浏览器扩展
```

**首次使用**：访问 `http://localhost:42110` → 配置对话模型（云 API 或本地）→ 在设置中添加内容源（文档、Obsidian、GitHub 等）→ 在聊天框提问或使用搜索/Agent 模式。
**最低资源**：轻到中等，内存约 2–4 GB 起；GPU 可选。
**上手难度**：★★★☆☆ —— 有 compose 与桌面版，但功能面广（搜索+Agent+插件），配置项偏多。

### 差异化特色

1. **"第二大脑"定位独特**：深度绑定 Obsidian/Emacs 等笔记工具与 WhatsApp 等入口
2. **多端 + 离线**：桌面/移动/浏览器插件多入口，支持本地模型离线运行
3. **内置自动化**：可定时执行研究/总结任务（Scheduled Automations）
4. 提供 Khoj Cloud 商业托管

### 局限与风险

1. ⚠️ **AGPL-3.0 许可**对闭源商用/二次分发有较强限制
2. ⚠️ **2.0 仍处于 beta**（beta.28），稳定性与 API 变动风险较高
3. 近期提交频率低于同类头部项目（最近提交 2026-08），长期演进节奏需关注

### 适合谁 / 典型场景

个人笔记/文档（Obsidian、PDF、Markdown）的语义搜索与问答；个人知识库 + 联网检索的日常研究助理；定时自动化（如每日资讯汇总）。

---

## 9. Flowise

> **定位**：拖拽式 LLM 应用/Agent 编排平台（Node/TypeScript 技术栈）
> **仓库**：https://github.com/FlowiseAI/Flowise · **Star**：55,500 · **License**：Apache-2.0（附商业使用附加条款） · **语言**：TypeScript · **维护方**：FlowiseAI（2025-08 被美国 Workday 收购） · **状态**：❌ **已归档停更（2026-08-13）**

### 它是什么

Flowise 曾是"Node 版 Langflow"——用 TypeScript 重写了一套拖拽式 LLM 应用编排平台，`npx flowise start` 一条命令就能跑起来，对前端/JS 开发者非常友好。它提供 Chatflow / Agentflow / 工具链多类画布，企业版有 RBAC 与多工作区。

**但它的开源版本已经停止维护了。** 2025 年 8 月 FlowiseAI 被 Workday 收购，2026 年 8 月 13 日 GitHub 仓库正式归档（`archived=true`）。这意味着不再有新功能、不再有安全修复。

> **选型结论：新项目不建议采用 Flowise 开源版。** 若你已经在用，应评估迁移到 Langflow（MIT，活跃）或 Dify。企业客户可关注 Workday 后续的商业化路线。

### 核心架构与编排范式

- **工作流 DAG** + 多 Agent（Multi-Agent / Supervisor 模式）
- **多类画布**：Chatflow / Agentflow / 工具链
- **内嵌 API / iframe 发布**

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置工具/自定义工具 + 代码执行节点 |
| **记忆机制** | 会话记忆与向量记忆 |
| **MCP 支持** | ✅ 支持（提供 MCP 工具节点） |
| **沙箱/执行** | 支持代码节点执行 |
| **人机协作** | 有限 [不确定] |
| **RAG** | ✅ 内置 RAG 与向量库集成 |

### 快速上手

```bash
npx flowise start
# 或 npm install -g flowise && flowise start
# Docker： docker run -d -p 3000:3000 flowiseai/flowise
```

**访问地址**：`http://localhost:3000`。**最低资源**：轻量，内存约 2 GB 起。
**上手难度**：★★☆☆☆ —— npx 一条命令即用，拖拽式体验友好。
**最后版本**：`flowise@3.1.4`（2026-07-29）

### 差异化特色

1. **Node/TypeScript 技术栈**，npm 安装即用，前端/JS 开发者上手友好
2. 提供 Chatflow / Agentflow / 工具链多类画布，拖拽即可编排
3. 企业版（Flowise Enterprise）提供 RBAC、多工作区等能力

### 局限与风险

1. ⚠️ **开源仓库已于 2026-08-13 归档，收购后停止活跃维护，长期可持续性存疑**
2. RBAC/多工作区等企业特性需付费企业版
3. 大规模工作流性能与长期维护风险较高

---

## 10. Coze Studio（扣子开源版）

> **定位**：字节跳动扣子（Coze）的开源版，全栈式 AI Agent 开发平台
> **仓库**：https://github.com/coze-dev/coze-studio · **Star**：21,709 · **License**：Apache-2.0（附商标/使用附加条款） · **语言**：TypeScript（前端）+ Go（后端） · **维护方**：字节跳动 ByteDance（中国） · **状态**：⚠️ 2025-06 开源，近期节奏放缓（最后提交 2026-07-29）

### 它是什么

Coze Studio 是字节跳动在 2025 年 6 月把**扣子（Coze）平台开源**的产物。扣子本身是国内最流行的 Agent 搭建平台之一，开源版让企业可以在自有基础设施上跑一套"类 Coze"平台。

它的技术选型很"企业级"：后端 **Go 微服务 + DDD 领域驱动设计**，前端 React + TypeScript。性能与可扩展性导向明确，但也意味着**二次开发门槛较高**——想改业务逻辑得先理解微服务拆分与 DDD 分层。

它的独特优势是**复用扣子 SaaS 插件生态**：通过 MCP 协议可以调用扣子 SaaS 版的大量插件，工具丰富度起点很高。此外，Agent、工作流、插件、知识库、Prompt 在同一个平台内闭环。

需要留意的信号：版本号仍在 **0.5.1**（2026-02-05），最后提交为 2026-07-29，近期节奏放缓；官方部署以 Docker 一站式为主，大规模扩展（K8s/多租户）能力受限。

### 核心架构与编排范式

- **工作流 DAG** + 单 Agent / 多 Agent 模式
- **插件体系**：通过 MCP 调用扣子 SaaS 插件
- **全栈闭环**：Agent、工作流、插件、知识库、Prompt 同一平台

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 插件生态（含通过 MCP 调用 Coze SaaS 插件）、工作流工具、知识库、代码节点 |
| **记忆机制** | 会话变量 + 对话记忆（短期） |
| **MCP 支持** | 通过插件/MCP 客户端方式支持 |
| **沙箱/执行** | 含代码节点执行能力 |
| **人机协作** | [不确定] |
| **RAG** | ✅ 内置知识库与 RAG 检索 |

### 快速上手

```bash
git clone https://github.com/coze-dev/coze-studio.git
cd coze-studio
docker compose up -d          # 官方一键部署
```

**首次使用**：访问 `http://localhost:8888` → 注册/登录 → 「模型管理」配置 LLM → 创建智能体或工作流 → 编排节点并试运行/发布为 API。
**最低资源**（官方 README 建议）：**约 2 Core CPU + 4 GB RAM 起步**；含 MySQL、Redis、Elasticsearch、MinIO 等组件。
**上手难度**：★★★☆☆ —— 一键 compose 起服务，但组件多、需配置模型与存储，功能面大。

### 差异化特色

1. **全栈开源**：后端 Go（微服务架构 + DDD），前端 React + TypeScript，性能与可扩展性导向
2. **复用扣子 SaaS 插件生态**（通过 MCP 协议调用 SaaS 版插件），扩展工具丰富
3. **低代码一体化**：Agent、工作流、插件、知识库、Prompt 在同一可视化平台内闭环
4. 官方中英文文档齐全（含 README.zh_CN）

### 局限与风险

1. 官方部署方案以 Docker 一键部署为主，大规模扩展（K8s/多租户）能力受限
2. **近期提交放缓**（最后提交 2026-07-29），生态/文档成熟度不及 Dify，开源版与 SaaS 版存在功能差距
3. **二次开发门槛较高**（Go 微服务 + DDD 架构）

### 适合谁 / 典型场景

企业搭建内部"类 Coze"自有 Agent 平台；低代码快速开发与调试 Agent/工作流；接入国内模型（豆包）的 AI 应用。

---

## B 类横向速查

| 项目 | Star | License | 语言 | 默认端口 | 最低资源 | 上手 | 状态 |
|---|---|---|---|---|---|---|---|
| n8n | 207,314 | ⚠️ Sustainable Use | TypeScript | 5678 | ~2 GB RAM | ★★★ | ✅ |
| Dify | 158,414 | ⚠️ 自定义 | TS + Python | 80 | 2C / 4 GB | ★★★ | ✅ |
| Langflow | 155,643 | ✅ **MIT** | Python | 7860 | ~2 GB RAM | ★★☆ | ✅ |
| RAGFlow | 92,178 | ✅ Apache-2.0 | Go + Python | 80 | 4C / 16 GB / 50 GB | ★★★★ | ✅ |
| AnythingLLM | 67,040 | ✅ **MIT** | JavaScript | 3001 | ~2 GB RAM | ★★☆ | ✅ |
| Flowise | 55,500 | ⚠️ Apache-2.0+条款 | TypeScript | 3000 | ~2 GB RAM | ★★☆ | ❌ **已归档** |
| Khoj | 37,679 | 🔴 AGPL-3.0 | Python | 42110 | ~2–4 GB RAM | ★★★ | ⚠️ beta |
| FastGPT | 29,817 | ⚠️ 自定义 | TypeScript | 3000 | ~4 GB RAM | ★★★ | ✅ |
| Coze Studio | 21,709 | ✅ Apache-2.0 | TS + Go | 8888 | 2C / 4 GB | ★★★ | ⚠️ 放缓 |
| Bisheng | 12,047 | ✅ Apache-2.0 | Python | 3001 | ~16 GB RAM | ★★★★ | ✅ |

> **许可证速记**：纯 MIT 只有 **Langflow** 与 **AnythingLLM** 两家。n8n 非 OSI 开源，Dify / FastGPT / Flowise 均为"Apache 2.0 + 附加条件"，Khoj 为 AGPL-3.0。
