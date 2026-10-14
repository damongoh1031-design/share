# 知识库 / RAG / 召回 / 重排 —— MCP 选型指南

> **调研问题**：有什么适合做知识库的 MCP？能做 RAG、重排、召回等。
>
> **核验方式**：所有 GitHub 量化指标由主代理通过 GitHub REST API 于 **2026-10-14** 一手核验（143 个仓库直查 + 15 组关键词检索）；关键 MCP 的**实际能力**逐一抓取 raw README 核实，不采信二手转述。
>
> **配套文件**：`report.html`（可视化）、`data/github-verified.json` + `data/github-verified-2.json`（143 仓库核验）、`data/github-search.json`（15 组检索）、`data/verify_repos.py` 等 3 个可复跑脚本

---

## 〇 结论速览

### 先说三个最容易被误解的点

**① 绝大多数「向量库 MCP」只做召回，不做重排。**

这是本次调研最重要的发现。官方 Qdrant MCP（1,548★，这个领域星数最高）**只有 2 个工具**：`qdrant-store` 和 `qdrant-find`。没有重排、没有混合检索，embedding 只支持 fastembed 且默认 `all-MiniLM-L6-v2`。**它本质上是一个「语义记忆层」，不是一个 RAG 引擎。**

**② 想要「召回 + 重排」一体，只有很少几个 MCP 真正做到了。**

真正内置 cross-encoder 重排的 MCP，本轮只找到 **3 个**（见第二章）。其余要么只召回，要么把重排留给你的客户端或向量库自身配置。

**③ MCP 是「接缝」，不是「引擎」。**

RAG 的四个环节里，MCP 负责的是**把已有能力接到 Agent 上**，而不是替你实现能力。所以选型的第一问不是「哪个 MCP 最强」，而是「**我的检索后端是什么**」。

### 选型决策树

```
你的知识库后端是什么？
│
├─ 还没有，想要开箱即用 ──────────→ 【一体化 RAG MCP】
│                                    haiku.rag（628★，最推荐）
│                                    knowledge-rag（296★，纯本地）
│
├─ 已有向量库（Qdrant/Milvus/…）──→ 【向量库官方 MCP】+ 重排交给向量库自身配置
│                                    qdrant / milvus / weaviate / redis
│
├─ 已有 Elasticsearch / OpenSearch → 【ES MCP】⚠️ Elastic 官方版已废弃，用 OpenSearch 或 Agent Builder
│
├─ 已有云知识库（AWS/Azure） ─────→ 【云厂商 KB MCP】自带 rerank，最省事
│                                    awslabs/mcp（Bedrock KB Retrieval）
│
├─ 想要完整平台 + 自带 MCP ───────→ 【RAG 平台】Dify / RAGFlow / WeKnora
│
└─ 知识有强关系结构 ─────────────→ 【Graph RAG】Graphiti / cognee / neo4j MCP
```

### 分层推荐速查表

| 场景 | 首选 | 星数 | 召回 | 重排 |
|---|---|---|---|---|
| **开箱即用的本地 RAG** | `ggozad/haiku.rag` | 628★ | ✅ 混合（向量+全文） | ✅ 可选（cross-encoder/Jina/Cohere/vLLM） |
| **纯本地零云 RAG** | `lyonzin/knowledge-rag` | 296★ | ✅ 混合 | ✅ cross-encoder |
| **云知识库检索** | `awslabs/mcp` Bedrock KB | 9,777★ | ✅ | ✅ Bedrock rerank |
| **已有 Qdrant** | `qdrant/mcp-server-qdrant` | 1,548★ | ✅ 纯向量 | ❌ |
| **已有 Neo4j / 要图谱** | `neo4j-contrib/mcp-neo4j` | 988★ | ✅ 图谱 | ❌ |
| **完整平台** | `Tencent/WeKnora` | 33,881★ | ✅ | ✅（平台内） |
| **代码库知识库** | `DeusData/codebase-memory-mcp` | 46,547★ | ✅ | — |
| **上下文压缩（省 token）** | `headroomlabs-ai/headroom` | 75,305★ | — | — |

---

## 一 先搞清一件事：RAG 的环节，MCP 覆盖哪几个

### 1.1 一条完整 RAG 链路的 5 个环节

| 环节 | 做什么 | MCP 能覆盖吗 |
|---|---|---|
| **① 解析** | PDF/Word/图片 → 结构化文本 | ✅ 有专门的解析 MCP |
| **② 切分** | 文本 → chunks | ⚠️ 少见独立 MCP，多内嵌在平台里 |
| **③ 召回** | 向量/关键词/混合检索 | ✅ **这是 MCP 覆盖最充分的一环** |
| **④ 重排** | cross-encoder 精排 top-k | ⚠️ **稀缺**，只有少数 MCP 内置 |
| **⑤ 生成** | 喂给 LLM | ❌ 由 Agent 本体负责 |

**关键结论**：**③ 召回** 是 MCP 生态最成熟的环节（因为向量库厂商都在做官方 MCP）；**④ 重排** 是最稀缺的环节；**② 切分** 几乎没有独立 MCP。

### 1.2 MCP 是「接缝」，不是「引擎」

一个常见误解是「装个 MCP 就有 RAG 了」。实际上：

- **向量库 MCP**（Qdrant/Milvus/Weaviate）做的是「把你的查询转成对已有向量库的调用」
- **它不负责**：文档解析、切分策略、embedding 质量、重排、答案生成

所以选型顺序应该是：**先定检索后端 → 再选 MCP**，而不是反过来。

### 1.3 三类 MCP 的分工

| 类型 | 代表 | 你得到什么 | 你需要自己做什么 |
|---|---|---|---|
| **存储型** | qdrant / milvus / weaviate / redis MCP | 一个「语义记忆」接口 | 解析、切分、重排、答案 |
| **检索型** | haiku.rag / knowledge-rag | 完整的 RAG 能力 | 几乎不用，装完即用 |
| **平台型** | Dify / RAGFlow / WeKnora | 完整平台 + 自带 MCP Server | 部署平台 |

---

## 二 能同时做「召回 + 重排」的 MCP（最稀缺的一类）

本轮全量检索后，真正内置 cross-encoder 重排的 MCP 只有 **3 个**（外加 1 个云端方案）。这一章是全文最有价值的部分。

### 2.1 `ggozad/haiku.rag` — 最强本地 RAG MCP ⭐ 首推

| 项 | 值 |
|---|---|
| 星数 | **628★** |
| License | MIT |
| 最后推送 | 2026-10-13（活跃） |
| 技术栈 | LanceDB（嵌入式）+ Pydantic AI + Docling |
| Python | 3.12+ |

**README 原文能力清单（已核实）**：

> - **Ingest** PDFs, office documents, HTML, Markdown and images with Docling... The stored DoclingDocument keeps headings, tables, pictures and page provenance.
> - **Search** with **hybrid vector and full-text retrieval, optional reranking (cross-encoders, Jina, Cohere, Zero Entropy, vLLM, OpenRouter)**, section-aware context expansion, and image search with a multimodal embedder... Across several named databases at once.
> - **Answer** with the RAG capability: it searches, runs **sandboxed Python over the documents for counting and aggregation**, and **cites page numbers and headings**.
> - **Check** a citation by drawing its chunk on the page image.
> - **Integrate** through the Python API, native Pydantic AI capabilities, **an MCP server for Claude Code, Codex and Claude Desktop**, and a reference web app.
> - **Operate** with the `haiku-ingester` service (filesystem, HTTP, S3 and WebDAV sources, a SQLite or Postgres job queue with retries, a control plane and dashboard), tags and rollback, vacuum, and `haiku-rag doctor` health checks.

**为什么它是最优解**：

1. **召回层是混合的**（向量 + 全文），不是纯向量
2. **重排可插拔**：cross-encoder / Jina / Cohere / vLLM / OpenRouter 五选一，可以先用本地模型、后期换云服务
3. **引用可验证**：能把 chunk 画回 PDF 页面图上——这是 RAG 可信度的关键，绝大多数方案做不到
4. **默认零配置**：嵌入式 LanceDB + Ollama，不需要起服务器、不需要 API key
5. **有生产化组件**：`haiku-ingester` 带重试的任务队列 + 控制面板 + 健康检查

**上手**：

```bash
pip install haiku.rag
haiku-rag init
haiku-rag add-src paper.pdf
haiku-rag search "attention mechanism"
haiku-rag ask "What datasets were used for evaluation?"
```

**适合**：个人/团队自建知识库，要质量、要引用、要本地。

### 2.2 `lyonzin/knowledge-rag` — 纯本地零云方案

| 项 | 值 |
|---|---|
| 星数 | **296★** |
| License | MIT |
| 最后推送 | 2026-10-13（活跃） |
| 技术栈 | ChromaDB + FastEmbed |
| Python | 3.11+ |

**README 原文核心卖点（已核实）**：

> **Hybrid search · Cross-encoder reranking · 35 file formats · 100% local · Zero cloud · Enterprise-grade plumbing built-in.**
>
> `pip install knowledge-rag` → restart Claude Code → `search_knowledge("your query")`

**企业级配套设施**（README 明确列出）：bearer auth、Prometheus metrics、rate limiting、health probes、structured JSON logging、**zero-downtime reindex**。

**⚠️ 三条使用警告**：

1. **README 有大量 SEO 关键词堆砌**（HTML 注释里塞了 `local rag, mcp server, hybrid search, cross-encoder reranking, chromadb rag...`，还有 schema.org 结构化数据块）。这是营销驱动的仓库，**看到这类 README 要更谨慎地验证实际能力**。
2. **能力口径不一致**：仓库描述说「13 MCP tools, 20 format parsers」，README 说「35 file formats」。**两个数字对不上**，用前自己数一下。
3. **GPU 依赖**：badge 显示 NVIDIA CUDA。纯 CPU 环境的性能需自行验证。

**适合**：需要 air-gapped / GDPR 合规 / 完全不出网的场景。

### 2.3 `awslabs/mcp` — Bedrock KB Retrieval（云端首选）

| 项 | 值 |
|---|---|
| 星数 | **9,777★**（整个 AWS MCP 集合） |
| License | Apache-2.0 |
| 最后推送 | 2026-10-14（活跃） |

**README 原文能力（已核实）**，其中三项非常关键：

> **Agentic retrieval on managed knowledge bases**
> - Plan a multi-step retrieval strategy and synthesise a cited answer
> - **Search several knowledge bases in one call**
> - Optional condensed trace of the agent's planning and retrieval steps
>
> **Reach ACL-protected content**
> - Pass `user_id` to retrieve content from ACL-aware data sources (SharePoint, OneDrive, Confluence with per-document ACLs)
> - Results are filtered to what that user is authorised to see
>
> **Rerank results**
> - Improve relevance of retrieval results
> - **Use Amazon Bedrock reranking capabilities**

**三个别处没有的能力**：

1. **Agentic retrieval**：不是单次检索，而是「规划多步检索策略 → 综合出带引用的答案」，且**一次调用可跨多个知识库**
2. **ACL 感知**：传 `user_id` 就能拿到 SharePoint/OneDrive/Confluence 的权限内内容，结果按该用户权限过滤——**企业场景的刚需，开源方案普遍缺失**
3. **Bedrock 原生重排**

同时支持 `VECTOR` 和 `MANAGED` 两种知识库类型，自动识别。

**适合**：企业已在 AWS 上、有权限管控需求。

### 2.4 Azure AI Search 的 MCP 端点

Azure AI Search 每个知识库暴露**原生 MCP 端点**，检索请求里设 `"resultsProcessing": "rerank"` 即启用重排序管道。这是**平台内建 MCP**（不需要单独装服务器），跟前面几个的形态不同。

**⚠️ 注意**：`Azure/azure-mcp`（1,225★）**已归档**（最后推送 2026-02-06）。Azure 的 MCP 能力现在走 AI Search 原生端点，不要去找那个归档仓库。

### 2.5 三个一体化方案横向对比

| | **haiku.rag** | **knowledge-rag** | **Bedrock KB Retrieval** |
|---|---|---|---|
| 星数 | 628★ | 296★ | 9,777★（集合） |
| 部署 | 本地 | 本地 | AWS 云 |
| 向量库 | LanceDB（嵌入） | ChromaDB | Bedrock KB |
| **召回** | ✅ 混合（向量+全文） | ✅ 混合 | ✅ |
| **重排** | ✅ 5 种可插拔 | ✅ cross-encoder | ✅ Bedrock rerank |
| **引用** | ✅ 页码+标题，可回画页面图 | — | ✅ |
| 多库查询 | ✅ 同时跨多个命名库 | — | ✅ 一次调用跨多库 |
| 权限控制 | — | bearer auth | ✅ ACL 感知 |
| 增量/重试 | ✅ ingester 服务 | ✅ 零停机重建索引 | 由 AWS 托管 |
| 解析器 | Docling | 35 格式 | Bedrock 托管 |
| 答案生成 | ✅ + 沙箱 Python 聚合 | ❌ 只检索 | ✅ agentic |

**选择建议**：个人/团队自建 → **haiku.rag**；纯离线合规 → knowledge-rag；企业云上 → Bedrock KB Retrieval。

---

## 三 向量库 / 检索后端 MCP（召回层）

这是 MCP 生态里数量最多的一类，但**能力边界差异极大**。下表「重排」列是重点。

| MCP | 星数 | License | 最后推送 | 召回能力 | 重排 | 备注 |
|---|---|---|---|---|---|---|
| **qdrant/mcp-server-qdrant** | **1,548★** | Apache-2.0 | 2026-09-04 | 纯向量 | ❌ | **仅 2 个工具**，fastembed only |
| **neo4j-contrib/mcp-neo4j** | 988★ | MIT | 2026-09-09 | 图谱 | ❌ | Labs 项目，4 个子服务 |
| **elastic/mcp-server-elasticsearch** | 718★ | Apache-2.0 | 2026-10-12 | 全文+向量 | ⚠️ | **官方已标记 deprecated** |
| **redis/mcp-redis** | 634★ | MIT | 2026-10-13 | 向量+KV | ❌ | 官方 |
| **chroma-core/chroma-mcp** | 599★ | Apache-2.0 | 2025-09-17 | 向量 | ❌ | ⚠️ **停更 13 个月** |
| **zilliztech/mcp-server-milvus** | 244★ | Apache-2.0 | 2026-08-11 | 向量+混合 | ❌ | 官方，Milvus 本体支持混合 |
| **weaviate/mcp-server-weaviate** | 162★ | — | 2026-05-26 | 向量+混合 | ❌ | 官方 |
| **pinecone-io/pinecone-mcp** | 72★ | Apache-2.0 | 2026-09-29 | 向量 | ❌ | 官方 |
| **opensearch-project/opensearch-mcp-server-py** | 155★ | Apache-2.0 | 2026-10-08 | 全文+向量 | ⚠️ | ES 的开源替代 |
| **crystaldba/postgres-mcp** | **3,396★** | MIT | 2026-08-17 | SQL+pgvector | ❌ | 星数最高的数据库 MCP 之一 |
| **FalkorDB/FalkorDB-MCPServer** | 41★ | MIT | 2026-10-13 | 图谱+向量 | ❌ | |

### 3.1 三个必须知道的发现

**① Qdrant 官方 MCP 比想象的弱得多**

已抓 README 核实，它的全部工具只有两个：

```
qdrant-store  → 存信息
qdrant-find   → 检索信息
```

配置项只有 `QDRANT_URL` / `QDRANT_LOCAL_PATH` / `COLLECTION_NAME` / `EMBEDDING_PROVIDER`（**目前只支持 fastembed**）/ `EMBEDDING_MODEL`（默认 `sentence-transformers/all-MiniLM-L6-v2`）/ `QDRANT_SEARCH_LIMIT`（默认 10）/ `QDRANT_READ_ONLY`。

README 自述定位是「**acts as a semantic memory layer**」（语义记忆层）——**不是 RAG 引擎**。但它有 1,548★，是这个领域星数最高的。**高星 ≠ 功能全。**

**② Elastic 官方 MCP 已废弃**

README 顶部原文：

> [!CAUTION]
> **This MCP server is deprecated** and will only receive critical security updates going forward. It has been superseded by the **Elastic Agent Builder MCP endpoint**, which is available in Elastic 9.2.0+ and Elasticsearch Serverless projects.

另外它提示 **SSE 传输已废弃**，改用 streamable-HTTP。用 ES 做知识库的人要改路线。

**③ Neo4j 有两套，别装错**

`neo4j-contrib/mcp-neo4j`（988★）是 **Neo4j Labs** 项目，README 明确说「**we don't provide any SLAs or guarantees around backwards compatibility**」，并指向 `github.com/neo4j/mcp` 为官方产品版。它包含 4 个子服务：

- `mcp-neo4j-cypher` — 自然语言转 Cypher
- `mcp-neo4j-memory` — **知识图谱记忆**（跨会话/客户端持久化实体与关系）
- `mcp-neo4j-cloud-aura-api` — Aura 云实例管理
- `mcp-neo4j-data-modeling` — 图数据建模与可视化

### 3.2 一个重要提醒：混合检索与重排可能在「库本体」里

MCP 只是一个薄壳。**Milvus、Weaviate、Qdrant 本体都支持混合检索**，只是官方 MCP 没把这些参数暴露出来。

已核验本体星数：

| 向量库 | 星数 | 本体是否支持混合检索 |
|---|---|---|
| `milvus-io/milvus` | 46,381★ | ✅ 支持 sparse + dense |
| `qdrant/qdrant` | 35,070★ | ✅ topics 含 `hybrid-search` |
| `weaviate/weaviate` | 16,880★ | ✅ topics 含 `hybrid-search` |
| `chroma-core/chroma` | 29,494★ | ⚠️ 有限 |
| `pgvector/pgvector` | 23,355★ | ❌（需自己配 BM25） |
| `infiniflow/infinity` | 4,741★ | ✅ 自述 dense+sparse+tensor+全文 |
| `lancedb/lancedb` | 11,669★ | ✅ |

**所以如果你要混合检索 + 重排，有两条路**：

1. **换成一体的 RAG MCP**（haiku.rag），它已经把混合检索和重排都接好了
2. **自建薄封装**：直接用向量库 SDK 调混合检索 + 重排，再包一层 MCP。**如果官方 MCP 不暴露你要的参数，别硬用它**

---

## 四 RAG 平台型（自带 MCP Server，最省事）

如果你愿意跑一个平台，这类方案能一次解决解析 + 切分 + 召回 + 重排 + 生成，并且**自己就暴露 MCP Server** 给别的 Agent 用。

| 平台 | 星数 | License | 最后推送 | 亮点 |
|---|---|---|---|---|
| **langgenius/dify** | **158,418★** | — | 2026-10-14 | 最流行；RAG 流水线 + Agent 工作流 + 模型/工具生态 |
| **open-webui/open-webui** | **155,610★** | — | 2026-10-14 | 内建 RAG，最易部署 |
| **infiniflow/ragflow** | **92,181★** | Apache-2.0 | 2026-10-14 | 深度文档理解见长，切片/召回可调 |
| **Mintplex-Labs/anything-llm** | 67,041★ | MIT | 2026-10-14 | 本地优先，桌面版友好 |
| **zylon-ai/private-gpt** | 57,575★ | Apache-2.0 | 2026-10-14 | 自述含 RAG + skills + tools + **MCP** + text-to-sql |
| **HKUDS/LightRAG** | 40,127★ | MIT | 2026-10-12 | 轻量 Graph RAG，成本低 |
| **chatchat-space/Langchain-Chatchat** | 38,681★ | Apache-2.0 | 2025-11-10 | ⚠️ **停更 11 个月** |
| **Tencent/WeKnora** | **33,881★** | — | 2026-10-14 | **腾讯官方**，见下方详解 |
| **Cinnamon/kotaemon** | 25,802★ | Apache-2.0 | 2026-07-14 | 开源文档问答 UI |
| **netease-youdao/QAnything** | 14,199★ | AGPL-3.0 | 2026-09-23 | 网易有道 |
| **dataelement/bisheng** | 12,049★ | Apache-2.0 | 2026-10-14 | 企业级 LLM 应用平台 |
| **xerrors/Yuxi** | 7,388★ | MIT | 2026-10-10 | **中文**，多租户，统一 RAG + 知识图谱 + MCP/Skills |

### 4.1 `Tencent/WeKnora` — 中文场景最值得看的

已抓 README 核实，能力密度很高：

- **三种模式共用同一知识库**：RAG 查资料 / Agent 做多步任务 / Wiki 组织知识
- **数据源自动同步**：飞书 wiki、飞书云盘、Confluence、GitLab、腾讯 IMA、Notion、语雀、钉钉文档、Seafile、RSS
- **格式**：PDF、Word、图片、Excel、XMind 等 10+，Office 文件由 anydoc 进程内解析
- **内建 MCP Server**：供 Cursor、Claude 等 AI 工具接入
- **检索 chunk 可编辑、可 diff、可回滚**——这个特性很少见，直接解决「切分错了怎么办」
- **跨会话长期记忆**：保存用户档案、偏好、已确认事实
- **渠道**：企业微信、飞书、Slack、Telegram 问答；可嵌入外部网站
- **29 个内置模型厂商**；LLM / 向量库 / 存储后端全部可替换
- **权限**：多工作区 RBAC（4 种角色）+ 每资源所有权 + 每工作区审计日志
- **可观测**：Langfuse 追踪 agent 步骤、token 用量、流水线
- **部署**：Docker Compose / K8s，可本地或私有云，数据不出环境
- 知识图谱走 `neo4j` profile

**适合**：中文企业，需要飞书/钉钉/企业微信打通 + 权限管控 + 私有部署。

### 4.2 云厂商 MCP 工具箱（不只是知识库）

| 项目 | 星数 | License | 最后推送 | 说明 |
|---|---|---|---|---|
| **googleapis/mcp-toolbox** | **16,657★** | Apache-2.0 | 2026-10-14 | 数据库 MCP 工具箱：BigQuery/ClickHouse/Elasticsearch/Firestore 等 |
| **awslabs/mcp** | 9,777★ | Apache-2.0 | 2026-10-14 | 含 Bedrock KB Retrieval（见 2.3） |
| **cloudflare/mcp-server-cloudflare** | 4,378★ | Apache-2.0 | 2026-10-09 | 含 Vectorize/AI Gateway |
| **Azure/azure-mcp** | 1,225★ | MIT | 2026-02-06 | ⚠️ **已归档**，Azure 改走 AI Search 原生 MCP 端点 |

---

## 五 知识图谱 / Graph RAG（关系型知识）

当知识之间有强关系结构（人物、组织、事件、代码依赖），纯向量召回会失效——它找得到「相似」，找不到「关联」。这类场景需要 Graph RAG。

### 5.1 知识图谱框架（非 MCP，但常作为后端）

| 项目 | 星数 | License | 最后推送 | 说明 |
|---|---|---|---|---|
| **HKUDS/LightRAG** | 40,127★ | MIT | 2026-10-12 | 轻量 Graph RAG，成本远低于微软方案 |
| **microsoft/graphrag** | 36,332★ | MIT | 2026-10-12 | 微软官方，体系完整但重 |
| **topoteretes/cognee** | **32,243★** | Apache-2.0 | 2026-10-14 | 记忆 + 知识图谱一体化 |
| **getzep/graphiti** | **31,730★** | Apache-2.0 | 2026-10-14 | 实时知识图谱，企业级，带时间维度 |
| **vitali87/code-graph-rag** | 5,253★ | MIT | 2026-10-14 | 代码库知识图谱 |
| **FlowElement-xinliuyuansu/m_flow** | 4,511★ | Apache-2.0 | 2026-09-01 | 类脑认知记忆引擎 |

### 5.2 带 MCP 的知识图谱方案

| MCP / 项目 | 星数 | 最后推送 | 形态 |
|---|---|---|---|
| **Graphify-Labs/graphify** | **126,279★** | 2026-10-13 | 把代码库+文档+SQL schema+PDF 变成可查询知识图谱，提供 `/graphify` skill |
| **DeusData/codebase-memory-mcp** | **46,547★** | 2026-10-14 | 代码库索引进持久知识图谱，158 种语言，亚毫秒级 |
| **forloopcodes/contextplus** | 1,983★ | 2026-07-13 | RAG + Tree-sitter AST + 谱聚类，含 `search_memory_graph` / `retrieve_with_traversal`（带衰减评分） |
| **iwe-org/iwe** | 1,771★ | 2026-10-08 | Markdown 知识图谱，CLI + MCP 记忆 |
| **neo4j-contrib/mcp-neo4j** | 988★ | 2026-09-09 | `mcp-neo4j-memory` 子服务 |
| **shaneholloman/mcp-knowledge-graph** | 886★ | 2026-05-29 | 本地知识图谱持久记忆 |
| **GreatScottyMac/context-portal** | 767★ | 2026-01-27 | 项目级知识图谱记忆库 |
| **doobidoo/mcp-memory-service** | 2,013★ | 2026-10-14 | 知识图谱 + 自主整合 |

**⚠️ 星数异常提示**：`Graphify-Labs/graphify` 的 **126,279★** 和 `DeusData/codebase-memory-mcp` 的 **46,547★** 都经 API 复核确认，但**建仓时间很短、增长曲线陡峭**。这类高星新仓建议实际试用后再决定，不要只看星数。

### 5.3 Graph RAG vs 向量 RAG 怎么选

| | 向量 RAG | Graph RAG |
|---|---|---|
| 擅长 | 「意思相近」的检索 | 「相互关联」的推理 |
| 典型问法 | "文档里怎么说 X？" | "X 和 Y 是什么关系？谁影响了谁？" |
| 成本 | 低 | 高（要建图 + LLM 抽取实体关系） |
| 增量更新 | 容易 | 难 |
| 建议 | **先做向量，不够再上图** | 知识本身有强关系结构时直接用 |

---

## 六 记忆层（与知识库的边界）

**「记忆」和「知识库」不是一回事**，但经常被混在一起：

- **知识库**：你主动放进去的文档，可检索、可引用
- **记忆**：Agent 在对话中自动沉淀的事实/偏好，用于跨会话连续性

两者可以共用一个向量库，但**用途和写入策略完全不同**。选型时别把它们混成一个需求。

| 项目 | 星数 | License | 最后推送 | 说明 |
|---|---|---|---|---|
| **mem0ai/mem0** | **67,153★** | Apache-2.0 | 2026-10-12 | 最流行的 Agent 记忆层 |
| **MemTensor/MemOS** | 11,854★ | Apache-2.0 | 2026-10-10 | 自述 hybrid-retrieval，省 35.24% token，支持 DSH/Hermes |
| **getzep/zep** | 4,959★ | Apache-2.0 | 2026-10-14 | Graphiti 的商业版底座 |
| **basicmachines-co/basic-memory** | 4,167★ | AGPL-3.0 | 2026-10-12 | Markdown 本地记忆，**与 Obsidian 天然兼容** |
| **memodb-io/memobase** | 2,932★ | Apache-2.0 | 2026-01-11 | 基于用户档案的长期记忆 |
| **microsoft/kernel-memory** | 2,231★ | MIT | 2026-06-08 | 微软研究项目（**注意：是 research project**） |
| **doobidoo/mcp-memory-service** | 2,013★ | Apache-2.0 | 2026-10-14 | 知识图谱 + 自主整合 |
| **okf-memory/okf-agent-memory** | 777★ | MIT | 2026-10-12 | Git-native，BM25 亚 300µs |
| **0xK3vin/MegaMemory** | 724★ | MIT | 2026-05-03 | 项目知识图谱 + 语义搜索 |
| **jaredrhod/ai-memory-vault** | 700★ | CC-BY-SA-4.0 | 2026-08-31 | 把 Obsidian vault 变成 AI 工作记忆 |
| **Lyellr88/marm-memory** | 420★ | Apache-2.0 | 2026-10-12 | 本地优先，融合会话历史+代码索引 |

**官方参考实现**：`modelcontextprotocol/servers` 里的 **Knowledge Graph Memory** 是最常被引用的官方记忆实现（注意：官方活跃参考服务器现在只剩 7 个：Filesystem / Memory / Sequential Thinking / Time / Fetch / Git / Everything）。

---

## 七 文档解析与切分（RAG 的前置，决定上限）

**RAG 效果的上限在解析和切分，不在向量库。** 这一环做不好，后面再强的重排也救不回来。

### 7.1 文档解析

| 项目 | 星数 | License | 最后推送 | 说明 |
|---|---|---|---|---|
| **microsoft/markitdown** | **190,127★** | MIT | 2026-10-04 | 文档转 Markdown 的事实标准（注意：是**库**，MCP 只是捆绑） |
| **unclecode/crawl4ai** | **85,497★** | Apache-2.0 | 2026-10-14 | 网页爬取 → LLM 友好 Markdown |
| **opendatalab/MinerU** | **81,713★** | — | 2026-10-14 | PDF 深度解析，中文/公式/表格强 |
| **docling-project/docling** | **68,859★** | MIT | 2026-10-14 | IBM 出品，保留标题/表格/图片/页码溯源 |
| **datalab-to/marker** | 40,431★ | Apache-2.0 | 2026-10-02 | PDF → Markdown，质量高 |
| **datalab-to/surya** | 21,493★ | Apache-2.0 | 2026-09-11 | OCR + 版面分析 |
| **Unstructured-IO/unstructured** | 15,564★ | Apache-2.0 | 2026-10-14 | 老牌，格式覆盖最广 |
| **firecrawl/firecrawl** | **191,341★** | AGPL-3.0 | 2026-10-13 | 网页抓取 → 结构化 |
| **pymupdf/pymupdf4llm** | 2,262★ | AGPL-3.0 | 2026-10-13 | 轻量 PDF → Markdown |
| **opendatalab/MinerU-Document-Explorer** | 641★ | MIT | 2026-04-26 | **Agent 原生知识引擎，带 MCP 工具**：文档索引、wiki 组织、快速检索、深读 |

### 7.2 切分

| 项目 | 星数 | License | 最后推送 | 说明 |
|---|---|---|---|---|
| **feyninc/chonkie** | **4,790★** | MIT | 2026-10-03 | 最流行的 RAG 切分库 |

**⚠️ 注意**：`chonkie` 的仓库已迁移到 `feyninc/chonkie`（`chonkie-ai/chonkie` 返回 404）。**独立做切分的 MCP 基本没有**——切分要么内嵌在平台里，要么你自己在管线里做。

---

## 八 重排 / Embedding 服务（把重排变成可调用的服务）

如果不想用一体化 MCP，也可以把重排单独做成服务，再用 MCP 包一层。

| 项目 | 星数 | License | 最后推送 | 说明 |
|---|---|---|---|---|
| **ollama/ollama** | 183,101★ | MIT | 2026-10-14 | 本地跑 embedding 模型最省事 |
| **vllm-project/vllm** | 93,751★ | Apache-2.0 | 2026-10-14 | 高吞吐推理，可跑 embedding/reranker |
| **huggingface/sentence-transformers** | 19,171★ | Apache-2.0 | 2026-10-13 | 自述 "Embeddings, Retrieval, and **Reranking**" |
| **FlagOpen/FlagEmbedding** | 12,243★ | MIT | 2026-08-24 | **BGE 系列**，中文场景首选重排模型 |
| **huggingface/text-embeddings-inference** | 5,076★ | Apache-2.0 | 2026-10-13 | 官方 embedding 推理服务 |
| **mixedbread-ai/mgrep** | 4,419★ | Apache-2.0 | 2026-04-25 | 语义 grep（代码/图片/PDF） |
| **michaelfeil/infinity** | 2,958★ | MIT | 2026-10-14 | **高吞吐 serving 引擎，同时支持 text-embeddings 和 reranking** |
| **AnswerDotAI/rerankers** | 1,641★ | Apache-2.0 | 2025-12-20 | ⚠️ **停更 10 个月**，轻量重排库 |
| **Scisaga/qwen3-retrieval-server** | 7★ | — | 2026-08-18 | 自托管 Qwen3，Embedding + Reranker + MCP + Web 控制台 |

**推荐组合**：
- **中文重排** → FlagEmbedding（BGE-reranker 系列）
- **生产 serving** → infinity 或 TEI
- **本地快速起步** → Ollama

**⚠️ BGE 的 GitHub 仓库提示**：`BAAI/bge-reranker-v2-m3` 是**模型名不是仓库**（返回 404）。模型权重在 HuggingFace，代码在 `FlagOpen/FlagEmbedding`。

---

## 九 四套可直接抄的组合方案

### 方案 A：个人本地知识库（最省心）

```
文档 → Docling/MinerU 解析 → haiku.rag（LanceDB + 混合检索 + cross-encoder 重排 + 页码引用）
      → MCP Server → Claude Code / Codex / Claude Desktop
```

- 装：`pip install haiku.rag` + Ollama
- 优点：全本地、零 API key、引用可验证
- 适合：个人文档、论文、笔记

### 方案 B：团队知识库（要权限 + 多数据源）

```
飞书/Notion/Confluence/GitLab → WeKnora（自动同步 + 解析 + 切分 + 检索 + 重排）
      → 内建 MCP Server → 各类 AI 工具
```

- 优点：数据源打通、RBAC 权限、审计日志、chunk 可回滚
- 适合：中文企业、需要 IM 渠道（企业微信/飞书/钉钉）

### 方案 C：已有向量库（改动最小）

```
已有 Qdrant/Milvus/Weaviate → 官方 MCP（仅召回）
      + 重排放在向量库自身配置或客户端管线里
```

- 优点：不动现有架构
- **注意**：官方 MCP 通常不暴露混合检索/重排参数，**如果不够用，考虑自建薄封装而不是硬用**

### 方案 D：企业云上（要 ACL）

```
SharePoint/OneDrive/Confluence（带 ACL） → AWS Bedrock KB
      → awslabs/mcp bedrock-kb-retrieval（rerank + agentic retrieval + user_id 权限过滤）
```

- 优点：ACL 感知、多库一次调用、Bedrock 原生重排
- 适合：已有 AWS、有权限管控要求

---

## 十 陷阱清单（全部实测）

### 10.1 已废弃 / 已归档

| 项目 | 星数 | 状态 | 影响 |
|---|---|---|---|
| **elastic/mcp-server-elasticsearch** | 718★ | ⚠️ **官方 deprecated** | 改用 Elastic Agent Builder MCP 端点（9.2.0+） |
| **Azure/azure-mcp** | 1,225★ | ✅ **已归档**（2026-02-06） | Azure 改走 AI Search 原生 MCP 端点 |
| **weaviate/Verba** | 7,697★ | ✅ **已归档** | Weaviate 的 RAG 演示应用停更 |
| **timescale/pgai** | 5,798★ | ✅ **已归档**（2026-05-27） | pgvector 生态的 AI 扩展 |

### 10.2 高星但停更

| 项目 | 星数 | 停更 | 最后推送 |
|---|---|---|---|
| **kwanLeeFrmVi/mcp-rag-server** | 36★ | **18 个月** | 2025-04-18 |
| **chroma-core/chroma-mcp** | 599★ | **13 个月** | 2025-09-17 |
| **chatchat-space/Langchain-Chatchat** | 38,681★ | **11 个月** | 2025-11-10 |
| **AnswerDotAI/rerankers** | 1,641★ | 10 个月 | 2025-12-20 |
| **vibrantlabsai/ragas** | 16,019★ | 8 个月 | 2026-02-24 |
| **microsoft/kernel-memory** | 2,231★ | 4 个月 | 2026-06-08 |
| **weaviate/mcp-server-weaviate** | 162★ | 5 个月 | 2026-05-26 |

### 10.3 仓库改名（照抄旧 URL 会 404）

| 旧名 | 新名 |
|---|---|
| `explodinggradients/ragas` | **`vibrantlabsai/ragas`** |
| `chonkie-ai/chonkie` | **`feyninc/chonkie`** |
| `VikParuchuri/marker` | `datalab-to/marker` |
| `VikParuchuri/surya` | `datalab-to/surya` |
| `pymupdf/RAG` | `pymupdf/pymupdf4llm` |
| `run-llama/llama_parse` | `run-llama/llama_cloud_services` |
| `UKPLab/sentence-transformers` | `huggingface/sentence-transformers` |
| `THUDM/ChatGLM3` | `zai-org/ChatGLM3` |
| `mendableai/firecrawl-mcp-server` | `firecrawl/firecrawl-mcp-server` |

### 10.4 「库本体」被误当「MCP」

| 仓库 | 星数 | 真相 |
|---|---|---|
| `microsoft/markitdown` | 190,127★ | **文档转换库**，MCP 只是捆绑功能 |
| `firecrawl/firecrawl` | 191,341★ | **抓取服务本体**；MCP 是 `firecrawl-mcp-server`（7,598★） |
| `qdrant/qdrant` | 35,070★ | **向量库本体**；MCP 是 `mcp-server-qdrant`（1,548★） |
| `milvus-io/milvus` | 46,381★ | **向量库本体**；MCP 是 `mcp-server-milvus`（244★） |
| `HKUDS/LightRAG` | 40,127★ | **RAG 框架本体**；`olafgeibig/knowledge-mcp` 才是用它做的 MCP |

### 10.5 星数参考性的三个警告

1. **官方 MCP 星数普遍远低于库本体**：Milvus 本体 46,381★ vs 它的 MCP 244★。**别用本体的星数评估 MCP。**
2. **向量库 MCP 的星数不能反映功能完整度**：Qdrant MCP 1,548★ 但只有 2 个工具、无重排；haiku.rag 628★ 却有完整混合检索+重排+引用。
3. **高星新仓要谨慎**：`Graphify-Labs/graphify` 126,279★、`DeusData/codebase-memory-mcp` 46,547★ 均经 API 复核，但建仓短、增速陡，**建议试用后再采用**。

### 10.6 口径提醒

- **`BAAI/bge-reranker-v2-m3` 不是 GitHub 仓库**（404），是 HuggingFace 模型名；代码在 `FlagOpen/FlagEmbedding`（12,243★）
- **`xlang-ai/ModelScope` 返回 404**，ModelScope 的代码托管在别处
- **`smithery-ai/reference-servers` 返回 404**，Smithery 的参考服务器已迁移

---

## 十一 数据可信度与核验

### 11.1 来源分级

| 级别 | 来源 | 可信度 |
|---|---|---|
| **A 级** | GitHub REST API 一手直查（143 仓库）+ **关键 MCP 的 raw README 逐一核实能力声明** | **高** |
| **B 级** | 官方 README 原文引用（haiku.rag / knowledge-rag / Qdrant MCP / Bedrock KB / WeKnora / contextplus 等） | 高 |
| **C 级** | 检索聚合（15 组关键词，用于发现） | 中 |

### 11.2 本轮特别说明

**本轮的核验重点从「星数」转向了「能力」。** 上一轮发现子代理的 star 数普遍不准，本轮进一步发现：**光核验星数还不够，必须核实「它到底能做什么」**。

因此对每个候选 MCP 都做了 raw README 抓取，例如：
- 确认 Qdrant 官方 MCP **只有 2 个工具、无重排**（而非传闻中的"向量检索全能"）
- 确认 Elastic 官方 MCP **已 deprecated**（README 顶部 CAUTION 块）
- 确认 `knowledge-rag` 的**能力口径自相矛盾**（13 tools/20 parsers vs 35 formats）
- 确认 `neo4j-contrib/mcp-neo4j` 是 **Labs 非官方产品版**

### 11.3 明确未核实 / 存疑项

1. **`lyonzin/knowledge-rag` 的实际质量**：README 有大量 SEO 关键词堆砌（HTML 注释 + schema.org 块），属营销驱动仓库；且能力口径不一致（13 tools/20 parsers vs 35 formats）。**建议实测后再用于生产。**
2. **`lyonzin/knowledge-rag` 的 CPU 性能**：badge 显示 NVIDIA CUDA，纯 CPU 表现未验证。
3. **`Graphify-Labs/graphify`（126,279★）与 `DeusData/codebase-memory-mcp`（46,547★）**：星数经 API 复核为真，但建仓时间短、增长陡峭，实际质量未验证。
4. **Azure AI Search MCP 端点的具体参数**：仅从微软文档确认有 `resultsProcessing: rerank`，未实测。
5. **各向量库官方 MCP 是否支持传混合检索参数**：本轮只确认了 Qdrant（不支持）。Milvus/Weaviate 官方 MCP 的参数面未逐一核实。
6. **`headroomlabs-ai/headroom`（75,305★）**：自述压缩 RAG chunks 省 token，星数高但属新品类，未验证压缩后对召回质量的影响。

### 11.4 核验数据速览（节选）

**一体化 RAG MCP**

| 仓库 | 星数 | License | 最后推送 |
|---|---|---|---|
| `ggozad/haiku.rag` | 628★ | MIT | 2026-10-13 |
| `lyonzin/knowledge-rag` | 296★ | MIT | 2026-10-13 |
| `benmaster82/Kwipu` | 609★ | MIT | 2026-09-07 |
| `mathomhaus/guild` | 301★ | Apache-2.0 | 2026-10-13 |
| `olafgeibig/knowledge-mcp` | 59★ | MIT | 2026-02-13 |
| `Scisaga/qwen3-retrieval-server` | 7★ | — | 2026-08-18 |

**向量库 / 检索后端 MCP**

| 仓库 | 星数 | 最后推送 |
|---|---|---|
| `qdrant/mcp-server-qdrant` | 1,548★ | 2026-09-04 |
| `neo4j-contrib/mcp-neo4j` | 988★ | 2026-09-09 |
| `elastic/mcp-server-elasticsearch` | 718★ | 2026-10-12 ⚠️deprecated |
| `redis/mcp-redis` | 634★ | 2026-10-13 |
| `chroma-core/chroma-mcp` | 599★ | 2025-09-17 ⚠️停更 |
| `zilliztech/mcp-server-milvus` | 244★ | 2026-08-11 |
| `weaviate/mcp-server-weaviate` | 162★ | 2026-05-26 |
| `opensearch-project/opensearch-mcp-server-py` | 155★ | 2026-10-08 |
| `pinecone-io/pinecone-mcp` | 72★ | 2026-09-29 |
| `crystaldba/postgres-mcp` | 3,396★ | 2026-08-17 |

**平台 / 框架（本体星数）**

| 仓库 | 星数 | 最后推送 |
|---|---|---|
| `langgenius/dify` | 158,418★ | 2026-10-14 |
| `open-webui/open-webui` | 155,610★ | 2026-10-14 |
| `infiniflow/ragflow` | 92,181★ | 2026-10-14 |
| `Mintplex-Labs/anything-llm` | 67,041★ | 2026-10-14 |
| `zylon-ai/private-gpt` | 57,575★ | 2026-10-14 |
| `HKUDS/LightRAG` | 40,127★ | 2026-10-12 |
| `chatchat-space/Langchain-Chatchat` | 38,681★ | 2025-11-10 ⚠️停更 |
| `Tencent/WeKnora` | 33,881★ | 2026-10-14 |
| `microsoft/graphrag` | 36,332★ | 2026-10-12 |
| `topoteretes/cognee` | 32,243★ | 2026-10-14 |
| `getzep/graphiti` | 31,730★ | 2026-10-14 |
| `run-llama/llama_index` | 52,488★ | 2026-10-14 |
| `deepset-ai/haystack` | 26,737★ | 2026-10-14 |
| `xerrors/Yuxi` | 7,388★ | 2026-10-10 |

**解析 / 记忆 / 重排**

| 仓库 | 星数 | 最后推送 |
|---|---|---|
| `microsoft/markitdown` | 190,127★ | 2026-10-04 |
| `firecrawl/firecrawl` | 191,341★ | 2026-10-13 |
| `unclecode/crawl4ai` | 85,497★ | 2026-10-14 |
| `opendatalab/MinerU` | 81,713★ | 2026-10-14 |
| `docling-project/docling` | 68,859★ | 2026-10-14 |
| `mem0ai/mem0` | 67,153★ | 2026-10-12 |
| `headroomlabs-ai/headroom` | 75,305★ | 2026-10-13 |
| `datalab-to/marker` | 40,431★ | 2026-10-02 |
| `huggingface/sentence-transformers` | 19,171★ | 2026-10-13 |
| `vibrantlabsai/ragas` | 16,019★ | 2026-02-24 ⚠️停更 |
| `Unstructured-IO/unstructured` | 15,564★ | 2026-10-14 |
| `FlagOpen/FlagEmbedding` | 12,243★ | 2026-08-24 |
| `lancedb/lancedb` | 11,669★ | 2026-10-14 |
| `huggingface/text-embeddings-inference` | 5,076★ | 2026-10-13 |
| `feyninc/chonkie` | 4,790★ | 2026-10-03 |
| `michaelfeil/infinity` | 2,958★ | 2026-10-14 |
| `AnswerDotAI/rerankers` | 1,641★ | 2025-12-20 ⚠️停更 |

---

*报告生成：2026-10-14 ｜ 数据核验：GitHub REST API 直查 143 仓库 + 关键 MCP 能力 raw README 逐一核实 ｜ 本机环境：Windows 11*
