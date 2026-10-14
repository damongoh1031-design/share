# F 类｜知识库 / 研究型工作台（2 个）

> 以调研与知识生产为核心的专用工作台——是"通用工作台"在垂直场景的收敛形态。
> 数据快照：2026-10-14 · 标注 `[不确定]` 的为未能一手核实项

---

## 为什么单独列这一类

深度研究（Deep Research）是 2025-2026 年最热门的 Agent 应用场景之一。它跟 B 类知识库平台的区别在于：**B 类是"你喂数据它回答"，F 类是"你给问题它自己去查"**。

F 类的核心能力是：**自主规划子问题 → 并行检索多个来源 → 归纳 → 生成带引用的报告**。这本质上是一个多 Agent 协作流程，因此这一类项目也是观察"多 Agent 编排范式"的好样本——下面两个项目恰好代表了两条不同的技术路线。

---

## 1. GPT-Researcher

> **定位**：自主深度研究 Agent，给定主题自动检索、抓取、归纳并生成带引用的研究报告
> **仓库**：https://github.com/assafelovic/gpt-researcher · **Star**：30,084 · **License**：Apache-2.0 · **语言**：Python · **维护方**：Assaf Elovic（个人发起）+ 活跃社区 · **状态**：✅ 非常活跃（v3.7.0，2026-09-26）

### 它是什么

GPT-Researcher 是 F 类里**产品化最成熟**的项目，也是"规划器-执行器（planner-executor）"范式的代表。

它的工作流程是：**先规划**——把研究主题拆解成若干子问题；**再并行执行**——多个研究 Agent 同时检索、抓取、归纳各自负责的子问题；**最后汇总**——合成一份带引用来源的报告。这个"多 Agent 并行研究"架构显著优于单 Agent 的线性检索，因为并行能覆盖更多来源、减少串行等待。

它的另一个优势是**检索器插件化**：内置 **20+ 检索器**（Tavily、Serper、Bing、Google、DuckDuckGo、arXiv、PubMed、Semantic Scholar、OpenAlex 等），覆盖通用搜索与学术检索。可以通过 `gpt_researcher.retrievers` 入口把搜索提供方打包为独立插件。

**v3.7.0 有一个重要变化**：引入基于"有用性"的上下文过滤（**Jev**，来自 typesafe.ai）——不再按向量相似度筛选抓取内容，而是按"对回答的有用性"筛选。官方称在 28 个研究任务的内部基准上"达到或超过 embeddings"，且**不再强制需要嵌入模型**（无 key 时回退 BM25 关键词排序）。

> ⚠️ **升级注意**：v3.7.0 起要求 **Python 3.12+**，且默认上下文过滤行为变化（默认改为关键词排序，需显式设置 `CONTEXT_FILTER=embeddings` 才保留旧行为）。

### 核心架构与编排范式

- **「规划器-执行器」（planner-executor）范式** + **多 Agent 并行**（基于 LangGraph / deepagents）
- **先规划子问题，再并行研究，最后汇总**
- **报告对话（Report Chat）**：可对已生成报告追问
- **自托管前端**：WebSocket 流式输出

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | ⭐ **20+ 检索器**（Tavily/Serper/Bing/Google/DuckDuckGo/arXiv/PubMed/Semantic Scholar/OpenAlex 等）、网页爬虫、文件检索，并支持 MCP 工具 |
| **记忆机制** | 研究过程内的上下文累积；v3.7.0 引入基于"有用性"的上下文过滤（Jev） |
| **MCP 支持** | ✅ 支持（MCPRetriever，v3.7.0 中修复了 MCP 依赖版本约束） |
| **沙箱/执行** | 支持执行代码（用于本地文件研究与数据处理），隔离以本地/容器为主 |
| **人机协作** | 报告对话（Report Chat）支持对已生成报告追问，属交互式而非审批式中断 |
| **RAG** | ✅ 支持对本地/私有文档做研究（本地文档 RAG）与检索；v3.7.0 后向量检索变为可选 |

### 快速上手

```bash
pip install -U gpt-researcher      # PyPI 包版本 0.16.0
# 或源码 + Docker：
git clone https://github.com/assafelovic/gpt-researcher.git
cd gpt-researcher
# 配置 .env（OPENAI_API_KEY / TAVILY_API_KEY 等）后
docker compose up -d
```

**首次使用**：在 `.env` 填入 `OPENAI_API_KEY`（及搜索 API Key，如 Tavily/Serper）→ 启动服务 → 打开前端 `http://localhost:3000`（后端 API `http://localhost:8000`）→ 输入研究问题 → 等待多智能体生成带引用的研究报告。
**最低资源**：轻量，内存约 2 GB 起；**需 Python 3.12+**；无需 GPU。
**上手难度**：★★☆☆☆ —— pip 安装 + 填 Key 即可用，代码调用也很简单。

### 差异化特色

1. **多 Agent 并行研究架构**：规划器拆解子问题、多个研究 Agent 并行检索写作，最后汇总成报告，显著优于单 Agent 线性检索
2. **v3.7.0 的 Jev 上下文过滤**：按"对回答的有用性"而非向量相似度筛选抓取内容，且不再强制需要嵌入模型
3. **检索器插件化**：20+ 检索器覆盖通用搜索与学术检索
4. **工程化成熟**：自托管前端、WebSocket 流式、自托管前端资源（不再依赖第三方 CDN）

### 局限与风险

1. **Token 与 API 成本较高**（多 Agent 并行检索 + 长上下文），大规模使用成本需评估
2. 报告质量高度依赖所选模型与检索源质量，存在幻觉/来源偏差风险
3. **v3.7.0 起要求 Python 3.12+**，且默认上下文过滤行为变化（默认改为关键词排序），升级需注意兼容性

### 关于评测成绩的诚实说明

GPT-Researcher 的 v3.7.0 只公布了**自建的 28 任务内部基准**，**未在官方 GAIA / DeepResearch Bench 类榜单公布成绩**。引用时需谨慎——这不是第三方独立评测。

### 生态与社区

watchers 176、forks 4,113、open issues 仅 34（维护响应积极）；有官方文档站 docs.gptr.dev，含多语言 README；中文支持一般。

### 适合谁 / 典型场景

自动生成行业/竞品/技术调研报告（带引用来源）；作为 SDK 嵌入自有产品，做定制化深度研究流程；对本地/私有文档与公开网页做混合研究。

---

## 2. Open Deep Research（Hugging Face）

> **定位**：对 OpenAI Deep Research 的开源复现，偏参考实现/示例
> **仓库**：https://github.com/huggingface/smolagents/tree/main/examples/open_deep_research · **Star**：N/A（随 smolagents 仓库） · **License**：Apache-2.0（随 smolagents） · **语言**：Python · **维护方**：Hugging Face（美国/法国） · **状态**：⚠️ 独立仓库 2026-10-14 返回 404，现作为 smolagents 示例分发

### 它是什么

这是 Hugging Face 对 OpenAI Deep Research 的开源复现。它跟 GPT-Researcher 是**两条不同的技术路线**：

- **GPT-Researcher**：规划器-执行器 + 多 Agent 并行，**JSON 工具调用**
- **Open Deep Research**：核心范式是 smolagents 的 **CodeAgent「用代码写动作」**——Agent 直接生成 Python 代码来执行动作，而不是输出 JSON 工具调用

在 GAIA 提交中，它采用 **manager agent + 子 agent 的层级结构**：一个管理 Agent 负责编排，子 Agent 负责具体研究。

它公开了一个很实用的工程技巧：**把 PDF/xls 转为 png 截图喂入模型**（数据增强），因为视觉模型读截图往往比读原始文件更稳。

> ⚠️ **重要提示**：本次调研中 `huggingface/open_deep_research` 独立仓库在 2026-10-14 **返回 404**（疑似已归档/迁移/改名），当前实现位于 `huggingface/smolagents/tree/main/examples/open_deep_research`。它**不是产品化的交付物**，而是偏参考实现。

### 核心架构与编排范式

- **单 Agent 与多 Agent 层级两种模式**
- **核心范式**：smolagents **CodeAgent**（用代码写动作）
- **GAIA 提交**：manager agent + 子 agent 层级结构
- **数据增强**：PDF/xls 转 png 截图喂入

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置 GoogleSearchTool（SerpApi/Serper）、网页访问/文本检查器、文件加载器（支持读取本地文件与 PDF） |
| **记忆机制** | 无独立长期记忆（研究过程式上下文） |
| **MCP 支持** | [不确定]（未见明确 MCP 支持说明） |
| **沙箱/执行** | CodeAgent 以代码写动作，可配合 E2B 等远程沙箱或本地执行 |
| **人机协作** | 无（端到端自动研究） |
| **RAG** | 通过文件加载器读取本地文档/PDF 参与研究；非通用知识库产品 |

### 快速上手

```bash
git clone https://github.com/huggingface/smolagents.git
cd smolagents/examples/open_deep_research
pip install -r requirements.txt
python run.py          # 启动 Gradio Web UI
```

**首次使用**：设置环境变量（`HF_TOKEN` 或所选模型 API Key）→ 运行 `python run.py` → 浏览器打开 Gradio 界面（默认 `http://localhost:7860`）→ 输入研究问题 → 查看 Agent 生成的带来源报告。
**最低资源**：轻量，内存约 2 GB 起；无需 GPU（调用云模型/HF Inference）。
**上手难度**：★★★☆☆ —— 属代码示例，需自行准备 Python 环境与 API Key，无官方一键部署包。

### 差异化特色

1. **以「用代码写动作」为核心范式**（smolagents CodeAgent），相比 JSON 工具调用更灵活，是其区别于 GPT-Researcher 的关键编排差异
2. **官方公布 GAIA 验证集达到 55% pass@1**，对比 OpenAI 原版 Deep Research 的 67%
3. **多 Agent 层级结构**（manager + 子 agent）用于 GAIA 提交
4. **公开可复现的数据增强方法**（把 PDF/xls 转为 png 截图喂入）

### 局限与风险

1. **偏参考实现/示例，非产品化**：无 GUI、无知识库管理，工程化程度低于 GPT-Researcher
2. 依赖付费搜索 API（SerpApi/Serper）与模型 API（默认 o1 需 tier-3 权限），运行成本与门槛较高
3. **独立仓库状态不明**（2026-10-14 返回 404），版本与维护情况难以核实

### 关于评测成绩的诚实说明

官方公布的 **GAIA 验证集 55% pass@1** 与"OpenAI 原版 67%"**均来自官方 README/blog，非第三方独立榜单**。引用时需注明来源。

### 适合谁 / 典型场景

复现/研究 OpenAI Deep Research 的 agent 架构与基准表现；作为 smolagents 的学习示例，快速搭建带网页检索与文件读取的研究 Agent；在 GAIA 类通用助手基准上做实验与对照。

---

## F 类横向对比

| | GPT-Researcher | Open Deep Research |
|---|---|---|
| Star | 30,084 | 随 smolagents（约 2.8 万） |
| 编排范式 | 规划器-执行器 + 多 Agent 并行 | CodeAgent「用代码写动作」+ 层级 |
| 动作形式 | JSON 工具调用 | **Python 代码** |
| 检索器 | ⭐ 20+ 插件化检索器 | GoogleSearchTool（SerpApi/Serper） |
| MCP | ✅ 支持 | [不确定] |
| 产品化程度 | ⭐ 高（自托管前端 + WebSocket 流式） | 低（参考实现/示例） |
| 评测成绩 | 自建 28 任务内部基准 | GAIA 55% pass@1（官方口径） |
| 上手 | ★★☆ | ★★★ |
| 定位 | 生产可用的深度研究工具 | 学习/复现参考 |

### 选型建议

- **要真正用来做调研、要产品化** → **GPT-Researcher**
- **要学习 Deep Research 的架构、或在 GAIA 类基准上做实验** → **Open Deep Research**
- 两者都是"通用工作台"在垂直场景的收敛：**把多 Agent 编排 + 检索 + 报告生成打包成一个开箱即用的工具**。如果你的需求是通用任务而非研究，应该回到 C 类（通用自主智能体）。
