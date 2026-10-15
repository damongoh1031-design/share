---
type: Checklist
---

# AI Agent 扩展生态深度调研：Skills · MCP · 辅助工具 · SKILL.md 规范

> **调研对象**：AI Agent 的"扩展面"——技能（Skills）、协议（MCP）、辅助工具链、以及 SKILL.md 规范本身
> **数据快照**：2026-10-14
> **一手数据源**：agentskills.io 规范 · modelcontextprotocol.io 规范与 changelog · Linux Foundation 新闻稿 · GitHub Advisory Database · GitLab Advisory Database · JFrog / Oligo / Invariant Labs 安全研究 · 本机环境实测
> **原则**：标注 `[不确定]` 的为未能一手核实项；**不编造、不填补**。本报告对每一条关键数字都注明口径与来源等级。

---

## 目录

- [〇、结论速览](#〇结论速览)
- [一、SKILL.md 规范：Agent Skills 开放标准](#一skillmd-规范agent-skills-开放标准)
- [二、MCP 协议 2026 现状](#二mcp-协议-2026-现状)
- [三、市场、目录站与辅助工具链](#三市场目录站与辅助工具链)
- [四、安全风险全景](#四安全风险全景)
- [五、四者关系辨析：SKILL.md vs AGENTS.md vs CLAUDE.md vs MCP](#五四者关系辨析skillmd-vs-agentsmd-vs-claudemd-vs-mcp)
- [六、本机环境实测盘点](#六本机环境实测盘点)
- [七、选型决策树](#七选型决策树)
- [八、数据可信度与口径问题](#八数据可信度与口径问题)

---

## 〇、结论速览

**1. 2026 年扩展生态已经收敛为"三层结构"**，各自解决不同问题，不是竞品：

| 层 | 标准 | 管什么 | 类比 |
|---|---|---|---|
| **能力层** | **Agent Skills**（SKILL.md） | Agent **怎么做事**（程序性知识） | 员工手册 |
| **连接层** | **MCP** | Agent **能碰什么**（工具/数据） | USB-C 接口 |
| **协作层** | **A2A** | Agent **之间怎么配合** | 同事间的工单系统 |
| **规则层** | **AGENTS.md** | Agent **在本仓库要守什么规矩** | 公司章程 |

**2. 两个标准在 2025 年底同时被"中立化"**：MCP 于 **2025-12-09** 随 **Agentic AI Foundation（AAIF）** 捐给 Linux Foundation（与 Block 的 goose、OpenAI 的 AGENTS.md 一同作为创始项目）；Agent Skills 于 **2025-12-18** 作为开放标准发布到 **agentskills.io**。这是 2026 年生态最重要的结构性变化——扩展标准不再由单一厂商控制。

**3. MCP 在 2026-07-28 完成了问世以来最大的一次重构**：核心从"有状态双向会话"改为**无状态请求/响应**（移除 `initialize` 握手与 `Mcp-Session-Id`），新增 `server/discover`，并把 Roots / Sampling / Logging **正式废弃**。这是 2026 年读 MCP 文档时最容易踩坑的地方——网上大量教程仍是旧模型。

**4. 安全是这个生态当前最大的短板**。已确认的 MCP 组件 RCE/SSRF 漏洞至少 7 个（多个 CVSS ≥9.0）；Invariant Labs 在 2025-04 就公开了**工具投毒（Tool Poisoning）**这一基础攻击面，至今无生态级强制签名机制。**Skills 与 MCP 共用同一条信任链**：第三方技能以 Agent 同等权限运行，恶意 SKILL.md 即等于完全接管 Agent。

**5. "MCP 服务器破 10 万"是营销口径**。该数字出自 Linux Foundation 新闻稿，指"整个生态广泛发布的服务器"，**不等于官方 Registry 的收录量**（官方 Registry 2026-09 约 3 万条）。第三方目录站的 13.7 万等数字互相重复计数，不可比。

**6. 本机环境**：49 个用户级 Skills、57 个已装插件、5 个插件市场、3 个 MCP Server、13 个可用连接器。已是一个相当完整的"扩展面"实例（详见第六章）。

---

## 一、SKILL.md 规范：Agent Skills 开放标准

### 1.1 它是什么

**Agent Skills** 是 Anthropic 于 **2025 年 10 月**随 Claude Skills 功能推出的能力封装机制，并在 **2025-12-18** 发布为跨平台开放标准，规范主页为 **`agentskills.io/specification`**。

官方定义（一手）：

> "Skills are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. Skills teach Claude how to complete specific tasks in a repeatable way."

**核心思路**：一个 Skill = 一个文件夹，里面是 `SKILL.md`（元数据 + 指令）加上可选的脚本、参考资料、模板资源。它把"领域流程知识"从提示词里剥离出来，做成可组合、可移植、按需加载的模块。

**解决什么问题**：LLM 有能力但缺"程序性知识"（procedural knowledge）——不知道你公司的品牌规范、不知道你们的数据处理流程、不知道某类文档该怎么生成。把这些写进系统提示词会让上下文永久膨胀；Skill 的做法是**按需加载**。

### 1.2 SKILL.md 格式规范（权威来源：agentskills.io/specification）

文件必须是 **YAML frontmatter + Markdown 正文**。

| 字段 | 必需 | 约束 |
|---|---|---|
| `name` | ✅ | **最长 64 字符**。仅允许小写字母、数字、连字符（`a-z` `0-9` `-`）。**不得**以连字符开头或结尾，**不得**出现连续连字符（`--`）。**必须与父目录名一致。** |
| `description` | ✅ | **最长 1,024 字符**，非空。必须同时说明**这个技能做什么**和**什么时候用它**，并包含具体关键词。 |
| `license` | — | 许可证名称，或指向随附许可证文件的引用。 |
| `compatibility` | — | **最长 500 字符**。环境要求（目标产品、系统依赖、网络访问）。官方说明"大多数技能不需要"。 |
| `metadata` | — | 任意 string→string 键值对，用于规范之外的扩展属性。 |
| `allowed-tools` | — | 空格分隔的预授权工具列表。**实验性**，各实现支持度不一。例：`allowed-tools: Bash(git:*) Bash(jq:*) Read` |

**最小可用示例**：

```yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, and merge documents. Use when working with PDF files or when the user mentions forms, extraction, or PDF merging.
---
```

**非法 `name` 示例**（规范明确列举）：`PDF-Processing`（含大写）、`-pdf`（连字符开头）、`pdf--processing`（连续连字符）。

> ⚠️ **规范里没有 `version` 和 `model` 顶层字段**。版本类信息应放进自由格式的 `metadata` 映射（如 `metadata: { version: "1.0" }`）。部分实现（如 OpenClaw、Codex）自行扩展了额外 frontmatter 键——那是**实现私有**，不属于标准。

> ⚠️ **官方文档内部存在冲突**：Anthropic 帮助中心文章 *"How to create custom skills"* 称 `description` **上限 200 字符**（而非 1,024），并列出一个规范中**不存在**的 `dependencies` 字段（如 `python>=3.8, pandas>=1.5.0`）。**以 agentskills.io 规范为准**；帮助中心文章疑似简化/滞后版本。引用时须注意。

**校验方式**：规范提供参考库 **`skills-ref`**，命令 `skills-ref validate ./my-skill`，用于检查 frontmatter 合法性与命名约定。规范**未明确规定** frontmatter 非法时的运行时行为（是静默跳过还是报错）——不要臆测具体失败模式。

### 1.3 渐进式披露（Progressive Disclosure）：三级加载模型

这是 Agent Skills 最重要的工程机制，也是它区别于"把提示词塞进系统提示"的关键。

| 层级 | 内容 | 何时加载 | 预算 |
|---|---|---|---|
| **Level 1** | `name` + `description`（元数据） | **启动时，对所有技能全部加载** | **约 100 tokens** |
| **Level 2** | `SKILL.md` 正文（指令） | **技能被激活时** | **建议 < 5,000 tokens**；官方要求**正文保持在 500 行以内** |
| **Level 3** | `scripts/` `references/` `assets/` 中的文件 | **仅在需要时按需读取** | 不设上限，但应拆分 |

**为什么 Level 1 的 description 如此关键**：因为它是**唯一**常驻上下文的部分，也是**唯一的触发机制**。写得含糊（如 "Helps with PDFs."）就永远触发不了。这是新手最常犯的错。

> 📌 注意口径：官方预算单位是 **tokens**（<5,000 tokens），不是"5,000 词"。常见误传。

### 1.4 目录结构约定

```
skill-name/
├── SKILL.md          # 必需：元数据 + 指令
├── scripts/          # 可选：可执行代码（Python / Bash / JS 等）
├── references/       # 可选：按需加载的参考文档
├── assets/           # 可选：模板、图片、查找表等静态资源
└── ...               # 其他任意文件/目录
```

- **命名规则**：`name` 字段**必须与父目录名一致**；打包 ZIP 时 ZIP 根目录必须是技能文件夹本身，不能多套一层。
- **`scripts/`**：用于"传统编程比 token 生成更可靠"的场景。应自包含或显式声明依赖，错误信息要清晰。
- **`references/`**：额外文档，按需加载（如 `REFERENCE.md`、`FORMS.md`、领域文件 `finance.md`）。单个文件应小而聚焦。
- **`assets/`**：静态资源——模板、图像、数据/查找表。
- **引用路径**：使用相对于技能根目录的相对路径；**保持引用层级只深一层**，避免深层嵌套链。

### 1.5 编写技能的最佳实践

综合规范 + 官方帮助中心 + Microsoft Learn：

1. **保持聚焦**：一个技能只做一条工作流。"多个聚焦的技能比一个大技能组合得更好。"
2. **把 description 写具体**：它是唯一触发器。要写清 *做什么* + *何时用* + 具体关键词。
3. **确定性工作交给脚本**：能用代码可靠完成的，就打包成脚本，别让模型"生成"。
4. **避免 token 膨胀**：正文控制在 500 行内，细节移入 `references/`，元数据保持极简。
5. **从简单开始、增量测试**：先写 Markdown 指令，每次显著改动后测试；触发不了就回去改 description。
6. **包含输入/输出示例**，记录边界情况。
7. **安全**：不要硬编码密钥/API Key；**启用前先读第三方技能的 SKILL.md**（技能可以执行代码）。

### 1.6 产品采用情况（截至 2026）

**一手/厂商文档可证实的支持**：

| 产品 | 技能目录约定 |
|---|---|
| Claude Code / Claude 应用 / Claude API / Agent SDK | `.claude/skills/`（Anthropic 自家全产品线） |
| GitHub Copilot / Visual Studio | `.github/skills/`（工作区）、`~/.copilot/skills/`（个人），同时兼容 `.claude/skills/`、`.agents/skills/`；VS Code 需开启 `chat.agent.skills` |
| Cursor | `.cursor/skills/`（可用 `@skill-name` 调用） |
| Codex CLI | `.codex/skills/` |
| Gemini CLI | `.gemini/skills/` |
| Antigravity / OpenCode | `.agent/skills/` |

- **Microsoft Azure Agent Skills**：官方目录 **193 个技能**，"遵循 Agent Skills 开放标准"，明确列出兼容助手：GitHub Copilot、Claude Code、Cursor、Gemini CLI、Codex CLI、Antigravity、OpenCode。
- **合作伙伴技能**：Canva、Notion、Figma、Atlassian、Box（Anthropic 新闻页 + 帮助中心）。

> ⚠️ **未证实、勿引用的数字**：中文技术博客流传的"**33+ 个 Agent 产品已采用**""**2026 年初 85,000+ 公开技能**""**280,000+ 公开技能**"等，均**来自二手来源（CSDN/知乎/腾讯云）**，非一手。Anthropic 新闻页中合作伙伴的表述多为前瞻性语言（"plans to leverage"），属营销证言。**不要作为事实引用。**

---

## 二、MCP 协议 2026 现状

### 2.1 它是什么

MCP（Model Context Protocol）是连接 AI 应用与外部系统的**开源标准**——数据源（本地文件、数据库）、工具（搜索引擎、计算器）、工作流（专用提示模板）。官方类比是"**AI 应用的 USB-C 接口**"。

**架构**：Client-Server。Host/Client（Claude、ChatGPT、VS Code、Cursor）连接 MCP Server，Server 暴露能力。消息编码为 **JSON-RPC 2.0**，必须 UTF-8。

**服务端三大原语**：

| 原语 | 含义 | 控制方 |
|---|---|---|
| **Tools** | 模型可调用的可执行函数（搜索、计算等），支持结构化输出（`outputSchema`/`structuredContent`，2025-06-18 加入） | 模型控制 |
| **Resources** | 应用暴露给模型的只读上下文数据（文件、数据库行），以 URI 寻址 | 应用控制 |
| **Prompts** | 可复用的模板化工作流/消息，呈现给用户（如斜杠命令） | 用户控制 |

MCP 还定义客户端侧特性（roots、sampling、elicitation）——其中数项已在 2026-07-28 被废弃（见下）。

### 2.2 规范版本史（一手：官方 changelog）

版本号用 `YYYY-MM-DD`，代表**最后一次向后不兼容变更**的日期；向后兼容的编辑**不**升版本。

| 版本 | 状态 | 关键变更 |
|---|---|---|
| **2024-11-05** | Final | 首次公开发布。传输：**stdio** + **HTTP+SSE**。 |
| **2025-03-26** | Final | **引入 Streamable HTTP**，取代 HTTP+SSE；**引入 OAuth 2.1 授权**；JSON-RPC 批处理；工具注解；音频内容；completions。 |
| **2025-06-18** | Final | 移除 JSON-RPC 批处理；**结构化工具输出**；**elicitation**（服务端→用户输入）；工具结果中的资源链接；MCP Server 被归类为 **OAuth Resource Server**，需提供受保护资源元数据；**强制 RFC 8707 resource indicators**；HTTP 请求必须带 `MCP-Protocol-Version` 头。 |
| **2025-11-25** | Final | 一周年版本。引入实验性 **tasks**；URL 模式 elicitation（带 `elicitationId`）；软废弃 `includeContext` 的 `"thisServer"/"allServers"`；采纳**特性生命周期与废弃政策**。 |
| **2026-07-28** | **Current** | **无状态核心** —— 自发布以来最大架构变更。 |

#### 2026-07-28 主要变更（据官方 changelog）

1. 移除协议级会话与 `Mcp-Session-Id` 头；列表端点不再随连接变化。
2. **使 MCP 无状态**：移除 `initialize` / `notifications/initialized` 握手。每个请求在 `_meta` 中携带协议版本与客户端能力（`io.modelcontextprotocol/protocolVersion`、`.../clientCapabilities`）；不匹配返回 `UnsupportedProtocolVersionError`。
3. 新增 **`server/discover`** —— 强制 RPC，通告支持的版本、能力与身份。
4. 用 **`subscriptions/listen`**（单一长连接 POST-response 流）取代 HTTP GET 端点与 `resources/subscribe`/`unsubscribe`。
5. 移除 `ping`、`logging/setLevel`、`notifications/roots/list_changed`。
6. 实验性 **tasks** 移入官方扩展（`io.modelcontextprotocol/tasks`）。
7. 引入 **Multi Round-Trip Requests（MRTR）**：服务端返回 `InputRequiredResult`（`resultType: "input_required"`）与 `inputRequests`；客户端带 `inputResponses` 重试。**取代**服务端发起的 `roots/list`、`sampling/createMessage`、`elicitation/create`。
8. 所有结果新增必填 **`resultType`** 字段（`"complete"` 或 `"input_required"`）。
9. 移除 SSE 流可恢复性/重投递（`Last-Event-ID`）。

**2026-07-28 废弃项**：**Roots、Sampling、Logging 被废弃**（Sampling 建议迁移为"直接对接 LLM 厂商 API"）；HTTP+SSE 正式重分类为 Deprecated；**OAuth 2.0 动态客户端注册（RFC 7591）废弃**，转向 **Client ID Metadata Documents**。新的特性生命周期政策保证**最少 12 个月的废弃窗口**。

> 🔴 **这是最容易踩坑的地方**：网上绝大多数 MCP 教程仍基于 2025 年的有状态会话模型（`initialize` 握手 + `Mcp-Session-Id`）。按 2026-07-28 规范实现时这些已不存在。

### 2.3 传输层

规范定义**两种**标准传输（外加可插拔自定义）：

| 传输 | 机制 | 场景 |
|---|---|---|
| **stdio** | 客户端把 Server 作为子进程启动；stdin/stdout 上换行分隔的 JSON-RPC；stderr 用于日志 | **本地** Server。客户端应尽可能支持 stdio |
| **Streamable HTTP** | Server 独立进程，服务多客户端；单一 MCP 端点（如 `https://example.com/mcp`）支持 POST 与 GET；可选 SSE 流式多条消息。**取代 2024-11-05 的 HTTP+SSE** | **远程** Server |
| **HTTP+SSE** | 原始远程传输 | **自 2025-03-26 起废弃**，2026-07-28 正式重分类 Deprecated。迁移目标为 Streamable HTTP |

**Streamable HTTP 安全要求**：校验 `Origin`（非法返回 403）以防 DNS 重绑定；本地时绑定 localhost；必须实现认证。

### 2.4 授权

MCP 的 HTTP 授权模型基于 **OAuth 2.1**（2025-03-26 引入，后续版本加固）：

- MCP Server 充当 **OAuth 2.0 Resource Server**（2025-06-18），发布**受保护资源元数据**（**RFC 9728**），供客户端发现对应的 Authorization Server。
- **强制 RFC 8707 resource indicators**，使客户端把 token 绑定到特定 Server，防止恶意 Server 获取其他资源的 token。
- **2026-07-28 新增**：Authorization Server 应包含 **RFC 9207** 的 `iss` 参数（客户端必须校验）；客户端在动态注册时必须指定 `application_type`；客户端凭据必须按 issuer 归类；**RFC 7591 动态客户端注册废弃**，转向 **Client ID Metadata Documents**。

### 2.5 治理：捐给 Linux Foundation

**已证实**。**2025-12-09**，Linux Foundation 宣布成立 **Agentic AI Foundation（AAIF）**，创始贡献三个项目：

- **Anthropic 的 MCP**
- **Block 的 goose**（Agent 框架）
- **OpenAI 的 AGENTS.md**（标准）

**治理模式**：中立、开放的基金会治理（Linux Foundation Directed）。

**白金成员**：AWS、Anthropic、Block、Bloomberg、Cloudflare、Google、Microsoft、OpenAI。
**黄金成员**（部分）：Adyen、Cisco、Datadog、**Docker**、Ericsson、IBM、JetBrains、Okta、Oracle、Salesforce、SAP、Shopify、Snowflake、Temporal、Twilio。
**白银成员**（部分）：Apify、Hugging Face、SUSE、Uber、WorkOS、Zapier、ZED。

> Jim Zemlin（LF 执行董事）：*"Bringing these projects together under the AAIF ensures they can grow with the transparency and stability that only open governance provides."*
> Mike Krieger（Anthropic CPO）：*"Donating MCP to the Linux Foundation as part of the AAIF ensures it stays open, neutral, and community-driven…"*

**MCP Dev Summit** 已由 Obot.ai 捐给 AAIF；下一届 **2026-04-02~03，纽约**。

**意义**：MCP 不再由单一厂商控制，成为厂商中立的公共基础设施，创始治理来自 Anthropic、OpenAI、Block 三方，成员横跨几乎所有主要云与 AI 厂商。

### 2.6 MCP Registry（官方注册表）

**官方注册表：`registry.modelcontextprotocol.io`**（文档 `modelcontextprotocol.io/registry/about`）。

- **只存元数据，不存代码**——包本身在 npm / PyPI / Docker Hub。
- 元数据用标准化的 **`server.json`** 格式；名称采用反向 DNS 命名空间（`io.github.user/server`），通过 GitHub OAuth/OIDC 或 DNS/HTTP 验证归属。
- 由 **Anthropic、GitHub、PulseMCP、Microsoft** 支持。
- 定位是**供下游聚合器消费**，而非直接供宿主应用使用；**不支持私有 Server**；安全扫描交给包注册表与聚合器。
- 状态仍为 **preview**（"正式发布前可能发生破坏性变更或数据重置"）；API 自 **2025-10-24** 冻结在 **v0.1**。

**数量（口径极重要）**：

| 口径 | 数字 | 来源 |
|---|---|---|
| Linux Foundation 新闻稿 | "**超过 10,000 个已发布 MCP server**" | LF 新闻稿（2025-12-09） |
| 官方 Registry 自身 API 收录 | **约 9,652**（2026-05）→ 约 16,967（2026-07）→ **约 30,375**（2026-09-10）；含版本共 99,114 条记录 | 官方 Registry API |
| Glama（第三方，自动索引任意公开 GitHub 仓库） | **约 66,000+** | 第三方 |
| 聚合站 mcptoplist（跨站去重情况不明） | **137,138**（2026-09-30） | 第三方聚合 |

> ⚠️ **这些数字不可比**。LF 的"10,000+"是**生态级"广泛发布"口径**，非 Registry 收录量；第三方站存在重复计数、含废弃/重复 Server、为营销夸大。**任何具体数字都应视为自报、未经验证。** 可辩护的表述是：*"MCP 从 2024 年底的少数参考 Server，发展为 2025–2026 年横跨多个注册表的广谱生态，可信的数量级在数万量级及以上。"*
> 另一值得注意的结构性问题：官方 Registry 中 **62% 的 Server 发布后从未更新**；前 50 名发布者占 **24.6%**——存在大量批量自动发布（如某发布者一人发了 1,505 个单功能微工具）。

### 2.7 官方 SDK（分层）

官方 SDK 按特性完整度、协议支持与维护承诺分为三层：

| 层级 | 语言 |
|---|---|
| **Tier 1** | TypeScript、Python、**C#**、**Go**、**Rust**、**Ruby** |
| **Tier 2** | Java |
| **Tier 3** | Swift、PHP、Kotlin |

所有 SDK 支持创建 Server（tools/resources/prompts）、构建 Client、本地+远程传输、类型安全的协议合规。仓库位于 `github.com/modelcontextprotocol/*-sdk`。**注意**：语言清单较 2025 年中期已扩容（PHP/Ruby/Rust/Go 为后加入），分层机制也是新增的。

### 2.8 采用方

- **OpenAI**：2025-03 宣布在 **Agents SDK、Responses API、ChatGPT 桌面端**全面支持 MCP。
- **Google DeepMind**：2025-04 Gemini 支持 MCP，集成进 **Google AI Studio 与 Vertex AI**。
- **Microsoft**：Build 2025 深度集成 **GitHub、Microsoft 365、Azure**；VS Code 原生支持 MCP。
- **AWS**：支持 MCP（VP Agentic AI Swami Sivasubramanian 在 LF 新闻稿中表态支持中立基金会）。
- **客户端/IDE**：Claude（Desktop/Code）、ChatGPT、Cursor、VS Code、Gemini、Microsoft Copilot、MCPJam。
- **未找到可信的"主要厂商抵制"记录**（这反映的是本次检索结果，不代表绝无抵制者）。

---

## 三、市场、目录站与辅助工具链

### 3.1 MCP 目录站/注册表对比

| 名称 | 运营方 | 官方？ | 规模 | 质量信号 |
|---|---|---|---|---|
| **官方 MCP Registry**<br>`registry.modelcontextprotocol.io` | MCP 项目 / Linux Foundation（AAIF） | ✅ **官方** | 约 9.6k(5月) → 16.9k(7月) → **30.4k(9月)** | 只存元数据；命名空间归属经 GitHub/DNS 验证；preview，API v0.1 冻结 |
| **Smithery**<br>`smithery.ai` | Henry Mao（创始人），**已被 Arcade 收购** | ❌ | 约 4,800–5,000 | 托管+计费+网关；以 `ai.smithery/*` 发布进官方 Registry；`npx @smithery/cli install` |
| **Glama**<br>`glama.ai/mcp/servers` | Frank Fiegel（punkpeye） | ❌ | **约 66,000+** | 原始数量最大；自动索引任意公开仓库；"超集"再发布者；提供沙箱运行衍生数据与付费托管连接器 |
| **mcp.so** | **无法核实** | ❌ | 约 8,000+ | 中文社区流行目录；对是否源自官方 Registry 保持沉默 |
| **PulseMCP**<br>`pulsemcp.com` | PulseMCP 团队（其成员在官方 Registry WG 中） | ❌（伙伴） | 精选子集 | 提供实现官方 *Generic MCP Registry API* 规范的 Sub-Registry REST API，带流行度/安全分析/`isOfficial` 富化 |
| **Cursor Directory**<br>`cursor.directory` | Cursor 社区 | ❌ | 社区提交 | 主要是 `.cursorrules` 规则社区，也索引 MCP server |
| **awesome-mcp-servers**<br>`github.com/punkpeye/awesome-mcp-servers` | punkpeye | ❌（精选列表） | 96.3k stars | MIT；外链指向 Glama |

> ⚠️ **需警惕的聚合站**（数量互相矛盾、来源不明，疑似 SEO 驱动）：`mcptoplist.com`（称 137,138）、`mcpfind.org`（称 38,294+）、`mcp.ad`（称 33,000+）、`unyly.org`（称 108,000+）、`martechdb.com`。**不建议作为选型依据。**

### 3.2 MCP 开发工具

| 工具 | 用途 | 维护方 | 备注 |
|---|---|---|---|
| **MCP Inspector** | 官方可视化测试/调试工具，包名 `@modelcontextprotocol/inspector`。**v2** 含四个客户端：**Web**（React+Mantine SPA）、**CLI**（可脚本化，适配 CI）、**TUI**（Ink）、**mcpdo**（实验性连接 CLI/守护进程） | ✅ 官方 | `npx @modelcontextprotocol/inspector`（web），`--cli`，`--tui`。需 Node ≥22.19.0。密钥（OAuth token）存 OS keychain。许可证正从 MIT → Apache-2.0 |
| **mcp-publisher** | **官方 Registry 发布工具**（registry 仓库 `cmd/publisher`），发布 `server.json`，处理 GitHub OAuth/OIDC + DNS/HTTP 归属验证 | ✅ 官方 | `make publisher` 构建。**这是正确的发布方式**（不是给仓库提 PR） |
| **`mcp` CLI** | ⚠️ **未能核实存在单一官方 `mcp` 二进制**。官方 CLI 是 `mcp-publisher`（发布）与 `mcp-inspector`/`mcpdo`（调试）。社区有多个 "mcp-cli" 项目但未验证 | — | **标为未核实** |
| **@smithery/cli** | 安装/管理 MCP server 到客户端（`npx -y @smithery/cli install <server> --client claude`） | Smithery（第三方） | 绑定 Smithery 托管 |
| **VS Code MCP 集成** | VS Code（GitHub Copilot）原生支持 MCP。配置在 **`.vscode/mcp.json`**（项目级，顶层键 **`servers`**）或用户设置 JSON；`chat.mcp.discovery.enabled` 自动发现 | Microsoft（官方） | ⚠️ **破坏性变更**：`.vscode/mcp.json` **不再被 Copilot CLI 支持**；Copilot CLI 用 **`.mcp.json`**，顶层键 **`mcpServers`** |

### 3.3 Agent Skills 市场与集合

| 名称 | 维护方 | 可信度 | 说明 |
|---|---|---|---|
| **anthropics/skills** | ✅ Anthropic 官方 | **高** | 约 **180.9k stars**，21.4k forks。含 `skills/`、`spec/`（Agent Skills 规范）、`template/`。可注册为 Claude Code 插件市场：`/plugin marketplace add anthropics/skills`。多数技能 Apache-2.0，但文档创建类技能（`docx`/`pdf`/`pptx`/`xlsx`）为**源码可见但非开源** |
| **agentskills.io** | Anthropic / 开放标准 | **高** | 标准主页（JS 重，直接抓取渲染为空，建议人工核验） |
| **anthropics/claude-plugins-official** | ✅ Anthropic 官方 | **高** | "官方、Anthropic 管理的高质量 Claude Code 插件目录"。含内部 `/plugins` 与伙伴 `/external_plugins`。安装：`/plugin install {name}@claude-plugins-official` |
| **awesome-claude-skills** | 社区（travisvn；ComposioHQ） | ⚠️ 中 | 精选列表；Composio 版约 21.7k stars。偏"精选"而非"穷举" |
| **obra/superpowers** | 社区（obra） | ⚠️ 中 | 流行插件市场：`/plugin marketplace add obra/superpowers` |
| **SkillsMP**<br>`skillsmp.com` | 独立，非官方 | ⚠️ **低** | 聚合 Claude + Codex 技能。**自称数量自相矛盾（25,000+ vs 700,000+）** —— 典型 SEO 信号问题 |
| **SkillsHunt**<br>`skillshunt.org` | 不明 | ⚠️ **低** | 分类技能目录；来源不明 |
| **agenticmarket.dev** | 不明 | ⚠️ **低** | 宣称"290+ 实战技能""13+ IDE 的已验证 MCP server"——营销味重，未验证 |

> **可信度指引**：**唯一的一手技能来源是 `anthropics/skills` 与 `anthropics/claude-plugins-official`**。其余均为社区。对宣称海量技能数的站点（skillsmp、skillhunt、agenticmarket）应保持怀疑——它们是 SEO 驱动的聚合站，来源不可验证，且**没有 MCP Registry 那样的归属/验证模型**。

### 3.4 技能创作与管理工具

| 工具 | 用途 | 维护方 |
|---|---|---|
| **skill-creator** | **"元技能"**：创建新技能、修改/改进已有技能、并**度量技能表现**（跑 eval、带方差的基准）。按 Anthropic 规范引导全生命周期 | ✅ Anthropic 官方（在 anthropics/skills 中） |
| **技能模板** | `template/` 目录，最小 SKILL.md 脚手架 | Anthropic |
| **Claude Code 插件系统** | 技能/Agent/命令的**主要分发机制**。插件：`.claude-plugin/plugin.json`（元数据，必需）+ 可选 `.mcp.json`、`commands/`、`agents/`、`skills/`、`README.md`。市场：`.claude-plugin/marketplace.json`（`name`、`owner`、`plugins[]` 含 `name`/`source`/`description`/`version`；支持 `strict`、`renames`、`git-subdir` 源） | ✅ Anthropic |
| **技能校验器/linter** | ⚠️ **未发现单一权威的独立官方 linter**。校验主要靠 (a) Claude Code 插件加载器、(b) skill-creator 内置 eval、(c) 各仓库自带的 `validate-skill` 工具。官方 `skills-ref` 提供 `validate` 子命令 | 混合 / 部分未核实 |

> 📌 **插件 `name` 是不可变的 slug**；要改显示名用 `displayName`。技能打包类插件可声明 `skills[]` 数组并设 `strict:false`。

### 3.5 评测与基准工具

| 基准/工具 | 度量什么 | 维护方 | 备注 |
|---|---|---|---|
| **MCP-Bench** | 通过 MCP server 评测工具使用型 LLM Agent 在复杂多步真实任务上的表现（跨工具协调、参数控制、规划） | Tiamat-Tech | **ICLR 2026 poster**。用 Server 内互补工具生成真实任务（对比：ToolBench/BFCL 用孤立 API） |
| **MCPAgentBench** | LLM Agent **MCP 工具使用**的真实任务基准；带难度感知，不依赖外部 MCP 服务 | 学术（Liu et al., 2025） | 同行评审论文 |
| **OSWorld-MCP** | 集成 **GUI + MCP** 的评测，在真实 OS 环境中进行；158 个精选 MCP 工具，覆盖 7 个应用。新指标：Accuracy、**Tool Invocation Rate (TIR)**、Average Completion Steps (ACS) | 研究项目 | 有公开 leaderboard |
| **ToolBench / BFCL** | 传统工具调用/函数调用基准（MCP 之前的基线） | 社区/学术 | 用作对比基线 |
| **skill-creator evals** | 技能专项评测框架（跑 eval，带方差度量） | Anthropic | 内置于 skill-creator 元技能 |

### 3.6 配置文件格式（易踩坑）

**标准 MCP 客户端配置** —— 顶层键 **`mcpServers`**：

```json
{
  "mcpServers": {
    "arxiv": { "type": "stdio", "command": "uvx", "args": ["arxiv-mcp-server"] },
    "remote-db": { "url": "http://localhost:3000/mcp" }
  }
}
```

| 客户端 | 配置文件位置 | 顶层键 | 备注 |
|---|---|---|---|
| **Claude Desktop** | macOS：`~/Library/Application Support/Claude/claude_desktop_config.json`<br>Windows：`%APPDATA%\Claude\claude_desktop_config.json` | `mcpServers` | 尽管文件名叫 `claude_desktop_config`，键是 `mcpServers`（不是 `mcp.servers`） |
| **Cursor** | macOS/Linux：`~/.cursor/mcp.json`<br>Windows：`%USERPROFILE%\.cursor\mcp.json` | `mcpServers` | 也支持项目级配置；UI 可"Add new MCP server" |
| **VS Code** | `.vscode/mcp.json`（项目）或用户设置 JSON | **`servers`** | ⚠️ **键是 `servers`，不是 `mcpServers`**。支持 `inputs` + `servers` |
| **GitHub Copilot CLI** | `.mcp.json`（项目根） | `mcpServers` | ⚠️ **不支持 `.vscode/mcp.json`**（破坏性变更） |
| **Claude Code** | 通过 `/plugin` 系统 + 插件内 `.mcp.json` | `mcpServers` | MCP server 可打包进插件 |

---

## 四、安全风险全景

> **重要前提**：本节把"已披露确认的漏洞"与"理论攻击类别"严格分开。2026 年关于此主题的**最新材料大量集中在中文技术博客/聚合站**（CSDN、知乎、腾讯云、百度百科），下文凡依赖此类来源者均已标注。

### 4.1 MCP 攻击类别

| 攻击类别 | 机制 | 状态 |
|---|---|---|
| **工具投毒（Tool Poisoning）** | 恶意指令藏在 MCP 工具的 `description`/元数据中（如一个看似无害的 `add` 工具），模型读到但用户看不到，含 Unicode 不可见字符（如 U+2063） | **已确认**，Invariant Labs 于 **2025-04** 公开，是该领域的基础攻击面 |
| **拉地毯（Rug Pull）** | Server 通过审查时工具是良性的，**批准后**静默改变工具描述或实现（如 `read_file` 后来变成先外泄再读取） | **已确认概念**（Invariant Labs 描述）。MCP 工具动态注册，安装时静态审查无法防护后续变更 |
| **工具遮蔽/同名冲突** | 两个 Server 暴露同名工具，恶意 Server 静默覆盖良性 Server 的工具，Agent 以为在调 A 实际调 B | 已描述 |
| **工具输出中的提示注入** | 工具返回的不可信内容（网页、issue 正文、数据库行）携带指令，Agent 照做 | 已确认；对应 Simon Willison 的 **"致命三要素（lethal trifecta）"** |
| **混淆代理（Confused Deputy）** | 权限高于调用方的代理/Server 被诱骗代调用方行事（如使用静态 client ID 被恶意客户端冒用） | **官方规范**收录 |
| **Token 透传（Token Passthrough）** | Server 接受客户端 token 却不校验其是否签发给本 Server，然后转发下游，破坏下游限流/审计 | **官方明令禁止的反模式** |
| **会话劫持** | 可预测/静态 session ID 使攻击者冒充用户或事件流 | **官方规范**收录。缓解：≥128 位熵、密码学安全随机、Base64url、非确定性；服务端用户绑定；提权后轮换；安全事件时失效 |
| **本地 Server 沦陷** | 运行不可信本地 Server（如通过 `npx`/`uvx`）在开发机执行任意代码；STDIO 启动命令即信任边界 | **官方规范**收录 |

**其他命名类别**（多来自二手/学术）：Sampling 攻击、动态能力修改、上下文窗口投毒、学术工作如 "WebMCP Tool Surface Poisoning"（Lee, Chang & Yu, 2026）、"Beyond Tool Poisoning: Attack Surfaces of Malicious Remote MCP Servers"（J. Park, 2026）。

**常被引用的研究者**：Invariant Labs（工具投毒、GitHub MCP 漏洞、line jumping）、Equixly（MCP server 漏洞，2025-03-29 博文 "MCP Server: A New Security Nightmare"）、Oligo Security（MCP Inspector CVE）、Trail of Bits、General Analysis、OX Security。
> ⚠️ **缺口**：本次**未能**为 Trail of Bits 找到单一权威的 MCP 攻击类别博文——其站点列出 MCP/AI 安全工作，但未找到可确证的具体命名攻击论文。**标注为缺口。**

### 4.2 已确认的真实事件（CVE 与实证发现）

**已确认 CVE（经 advisory 数据库 / 厂商安全博客交叉印证）**：

| CVE | 组件 | 类型 | 严重度 | 来源 |
|---|---|---|---|---|
| **CVE-2025-49596** | Anthropic **MCP Inspector**（<0.14.1） | Inspector 客户端与代理之间缺认证 → CSRF → 未授权 **RCE**；可经浏览器"零点击"利用 | CVSS **9.4–9.6** Critical | Oligo Security（2025-06）；**GitLab Advisory DB** 确认 |
| **CVE-2025-6514** | **mcp-remote**（geelen/mcp-remote） | OS **命令注入** → 连接客户端 RCE | CVSS **9.6** | **JFrog** Security（2025-07） |
| **CVE-2025-53110** | Anthropic **Filesystem MCP Server** | 目录穿越 → 沙箱逃逸 | — | 被引（知乎） |
| **CVE-2025-53107** | **@cyanheads/git-mcp-server** | 多个工具中的命令注入 / RCE | — | **GitHub Advisory DB**（GHSA-3q26-f695-pp76），引用 Equixly |
| **CVE-2025-58358** | **mcp-markdownify-server** | pptx-to-markdown 工具命令注入 | 7.5 High | **GitLab Advisory DB** |
| **CVE-2025-65513** | **Fetch MCP Server**（mcp-fetch-server ≤1.0.2） | **SSRF** —— `is_ip_private()` 未校验私有 IP | Critical | SentinelOne / ZDI（2026-01-09） |
| **CVE-2025-53967** | **Framelink Figma MCP Server** | 未净化 URL 导致命令注入 → RCE | High | mcpsec.dev（2025-10） |

**已确认的研究发现（非 CVE）**：

- **GitHub MCP server 私有仓库泄露**（Invariant Labs，2025-05）：一个恶意公开 issue 可劫持 Agent（Claude 4），强迫其通过新 PR 读取并外泄用户**私有**仓库数据。影响广泛使用的 GitHub MCP 集成（约 14k stars）；GitLab Duo 有类似问题。
- **Supabase MCP "致命三要素"**（General Analysis，约 2025-07）：演示了对 Supabase MCP server 的提示注入 → 数据外泄；Simon Willison 有分析。无编号 CVE。
- **Asana MCP server 数据泄露**：据报道 Asana 的 MCP 实现允许一组用户访问其他用户（内部团队/伙伴）数据。中文安全媒体报导，**未找到 CVE ID** —— 视为"据报道"，未完全验证。
- **Cycode 发现官方 MCP Python SDK 缺陷**：**官方 MCP Python SDK 1.9.1–2.1.1** 存在高危问题，恶意 MCP server 可**窃取 OAuth 凭据**并完全接管账号。来源为 Cycode 的 LinkedIn 汇总——**标注为厂商自报，无 CVE ID**。
- **OX Security 架构性披露**（2026-04-15）：参考 MCP SDK **不把 STDIO 启动命令视为信任边界**，导致 RCE。声称规模：**>20 万 server 可能暴露、>3.2 万代码仓库受影响**；攻击者可窃取数据、数据库内容、API key、聊天日志。Anthropic 据称以咨询文档回应。**⚠️ 规模数字为 OX 自估，未经独立验证。**

**厂商扫描研究（方向性，非确认利用）**：

- **Endor Labs**：**82%** 的 MCP server 使用易受路径穿越影响的文件操作（样本 2,614 个实现）；**53%** 依赖不安全的长效静态凭据（样本 5,200+ 个开源服务）。
- **BlueRock**：扫描 7,000 个 MCP server，发现 **36.7%** 的远程 server 存在潜在 SSRF 风险。

### 4.3 Skills 特有风险

- **背景**：Anthropic 于 **2025-10** 在 Claude Code 引入 Agent Skills；**2025-12-18** 升为开放标准（agentskills.io），带规范 + SDK；被 VS Code/GitHub、Cursor、Goose、OpenCode 快速采用。有二手来源称"2026-02 已有 280,000+ 公开技能、20+ 平台采用"——**厂商/聚合口径，视为未验证营销近似值**。
- **核心风险 —— SKILL.md 内的提示注入**：Skill 是"YAML 元数据 + 自然语言指令"的文件夹，而 Agent 会**忠实执行**技能中的指令。恶意的或被入侵的 SKILL.md 因此可以指示 Agent 外泄密钥、执行脚本、关闭防护——这是工具投毒在"技能内容"上的对应物。
- **社区技能仓库的供应链风险**：Docker 的 "coding agent horror stories"（2026-05）把**恶意技能与插件供应链**列为头号风险：第三方技能/插件以**与 Agent 本身相同的权限**运行，故恶意技能 = Agent 完全沦陷。技能还可捆绑会被执行的脚本/参考资料。
- **为什么"安装前先读 SKILL.md"是推荐防御**：因为技能没有成熟的审查/注册机制，且以 Agent 权限执行，社区防御只能是人工检查。科学技能仓库 K-Dense 明确写道：*"Read the SKILL.md before installing… If something looks suspicious, don't install it. Check the contribution history."* 逻辑与防工具投毒一致——载荷在人类可读文本中，人工审查是最后一道防线。**但这很弱**：rug pull/动态更新与混淆（Unicode 隐藏）指令可绕过静态阅读。

### 4.4 缓解与最佳实践

**官方 MCP 指引**（规范 security best-practices 页；本次未能直接加载，据二手汇总）：

- **禁止 token 透传**；校验 token 是否签发给本 Server。
- **混淆代理缓解**：逐客户端同意/白名单、安全客户端注册、避免静态共享 client ID。
- **会话劫持缓解**：≥128 位熵、密码学安全、非确定性会话/状态句柄（Base64url）；服务端用户绑定；提权时轮换；安全事件时失效。
- **本地 Server 沦陷**：把 STDIO 启动命令视为信任边界；安全编码、最小权限、供应链审查、凭据管理。
- **2026-07-28 规范**进一步加固授权（见 2.4）。

**社区/业界最佳实践**（Elastic Security Labs、Microsoft "MCP for Beginners"、CSA、Wiz、JFrog、Docker）：

- **人在环（Human-in-the-loop）**：工具调用与安装 server/技能都需人工批准。
- **最小权限**：限定工具权限；禁止读取 `~/.aws`、`~/.ssh`、`.env` 等。
- **沙箱化**：容器、网络出口控制，以遏制被入侵的 server/技能。
- **白名单**：只信任已知 server/技能；阻止 `npx`/`uvx` 自动执行；关闭 IDE 自动执行。
- **锁定版本**并监控 **rug pull**（更新时重新审查）。
- 把 MCP server 当作**受治理的软件供应链组件**，而非随手装的插件（JFrog "MCP Trojan"）。
- **签名/证明机制（新兴，尚未普及）**：MCP server 二进制的 **SLSA provenance** 证明（如部分 Obsidian MCP 工具发布 SLSA provenance）；第三方 "MPP Registry" 营销"已签名、沙箱化、能力受限"的 MCP 包；npm provenance。**均属早期/局部，部分为厂商营销——尚无生态级强制签名。**

**2026 新增 —— 企业托管授权（EMA）**：MCP 扩展于 **2026-07-13 升为稳定**。企业可通过自家 IdP（Microsoft Entra、Okta 等）集中控制 MCP server 访问，取代逐 server 同意提示，实现零接触流程；管理员授权一次，用户经 IdP 组继承。Claude/Claude Code/Cowork 与 VS Code 支持；服务端支持来自 **Asana、Atlassian、Canva、Figma、Granola、Linear、Supabase**，Slack 进行中。

---

## 五、四者关系辨析：SKILL.md vs AGENTS.md vs CLAUDE.md vs MCP

这是最容易被混淆的一组概念。**它们不是竞品，是不同层的东西。**

| 文件/标准 | 归属 | 作用 | 加载模型 |
|---|---|---|---|
| **`SKILL.md`** | Anthropic 发起，**Agent Skills 开放标准**（agentskills.io） | **能力包**：针对特定任务的按需指令 + 脚本 + 资源。一个技能文件夹一个 | **渐进式/按需**（元数据常驻；正文与文件在触发时加载） |
| **`AGENTS.md`** | 开放跨工具约定（Sourcegraph Amp 先提 `AGENT.md`，后由 OpenAI 的 `AGENTS.md` 推广；现由 **AAIF** 托管） | **仓库级常驻指令**（项目约定、约束、"道路规则"） | **始终加载**（常驻上下文） |
| **`CLAUDE.md`** | Anthropic，**Claude Code 专用** | Claude Code 的项目"记忆"/指令，在项目根自动加载。Claude Code **不**原生自动加载 `AGENTS.md`（需用 `@AGENTS.md` 导入桥接） | **始终加载** |
| **`.cursorrules`** | Cursor（旧） | Cursor 旧版项目规则文件，已被 `.cursor/rules/` 目录取代 | 始终加载 |
| **`skills.md`** | — | **不是标准**。小写复数形式出现在 Codex 早期实验性 PR 和泛称中。**标准化文件名是大写 `SKILL.md`** | — |

**关键对比**：`AGENTS.md`/`CLAUDE.md` = 常驻的行为规则（"宪法"）；`SKILL.md` = 按需的专项能力（"技能证书"）。二手来源的概括是"**AGENTS.md 管路由/选择，Skill 管执行**"。

**Skill vs MCP（官方口径）**：
> "MCP connects Claude to external services and data sources. Skills provide **procedural knowledge**—instructions for how to complete specific tasks."

即：**MCP 给工具，Skills 教怎么用这些工具**。Microsoft 的框架类似：MCP = **工具**（搜索/获取），Skills = **知识**（查什么、何时查、怎么查）。

**Skill vs Projects / 自定义指令**：Projects = 始终加载的**静态背景知识**；Skills = 按需加载的**动态任务流程**；自定义指令 = **广泛适用于所有对话**。

**Skill vs Subagent / 斜杠命令**（⚠️ 二手来源，非一手确认）：Skill = 可复用的"操作手册"/知识；Subagent = 执行既定任务的专用 Agent 实例；斜杠命令 = 用户主动调用的快捷方式，而 Skills 由相关性自动触发（也可用户调用）。

**三者合观**：
> "Agent Skills 定义**能力**，MCP 提供**工具**，A2A 实现**协作**。"
> 常见建议是把 **MCP 当作基础设施、Agent Skills 当作应用层**，叠在一起用。

---

## 六、本机环境实测盘点

> 本节为**一手实测数据**（2026-10-14 扫描本机 `~/.workbuddy-ai/`），可作为"扩展面"的真实案例。

### 6.1 总体规模

| 项 | 数量 |
|---|---|
| **用户级 Skills**（`~/.workbuddy-ai/skills/`） | **49 个** |
| SKILL.md 文件总数（含插件内嵌） | 184 个 |
| **已安装插件** | **57 个** |
| **插件市场** | **5 个** |
| **已配置 MCP Server** | **3 个** |
| 可用连接器清单 | 13 个 |

### 6.2 已安装插件的来源分布

| 来源市场 | 数量 | 说明 |
|---|---:|---|
| `workbuddy-builtin` | 45 | 内置插件（技能包 + 交互模式 + 欢迎模式 + 文档/PPT/表格等） |
| `experts` | 5 | 专家包（deep-research、gpt-researcher-team、教育、运营客服、质量测试） |
| `codebuddy-plugins-official` | 3 | agent-browser、find-skills、playwright-cli |
| `workbuddy-connector-plugins-official` | 2 | github、notion 连接器 |
| `cb_teams_marketplace` | 1 | document-skills（pdf / pdfkit-py） |
| `my-experts` | 1 | rimworld-mod-guardian（自建专家） |

### 6.3 已配置的 MCP Server（3 个）

| 名称 | 传输 | 配置要点 |
|---|---|---|
| **gog** | stdio | 本地 `gog.exe mcp`，绑定一个 Google 账号（**邮箱已脱敏**），仅放行 `sheets,drive_search,drive_get,docs_get` 且 `--allow-write` —— **这是最小权限的好范例** |
| **web-search** | stdio | 本地 Node 运行 `open-websearch`，默认引擎 duckduckgo，允许 duckduckgo/baidu/bing/brave/startpage |
| **nixos** | stdio | `uvx mcp-nixos` —— 查 NixOS/nixpkgs 生态 |

> 📌 三者**全部使用 stdio 传输**，且全部为**本地可执行**（无远程 HTTP server）。按第 4.1 节，"本地 Server 沦陷"正是 stdio 模式的主要风险面——但这三个来源均为可信本地二进制，风险可控。

### 6.4 49 个用户级 Skills 的领域分布

| 领域 | 数量 | 代表技能 |
|---|---:|---|
| **调研 / 研究** | 9 | deep-research、market-researcher、ai-product-research、community-signal-research、last30days、dsh-market-plugin-research、property-shortlist-research、vps-cost-research、world-cruise-research |
| **浏览器自动化 / 抓取** | 8 | browser-use、playwright-browser-automation、agent-browser-core、playwriter、moli、headless-form-submit、web-scraper、scrapling |
| **工程 / 运维** | 6 | github-sync、cli-empirical-docs、unattended-scraper-ops、vps-ops-tooling、serverless-app-feasibility、windows-longrun-ai-service |
| **文档 / 知识管理** | 6 | markitdown-skill、docs-site-zh-manual、kb-distill、llm-wiki、obsidian、fanyi-bendi |
| **系统诊断 / 平台** | 4 | windows-flash-window-diagnosis、google-sheets-cdp、gog-google-workspace、mcp-nixos |
| **元技能（对 Agent 自身）** | 4 | agent-harness-extension-audit、agent-mbti、task-alignment、task-implement |
| **检索 / 资讯** | 4 | multi-search-engine、web-search-fallback、aihot、github-ai-trends |
| **业务 / 垂直** | 4 | fxiaoke-crm-query、malaysia-phone-osint、tieba-scrape、diagram-design |
| **游戏** | 2 | rimworld-modlist-audit、rimworld-workshop-download |
| **输出风格** | 1 | i-have-adhd |
| **其他** | 1 | news-summary |

**观察**：

1. **"调研 + 抓取"占了 17/49（约 35%）** —— 这套环境明显是围绕"信息获取与研究报告"构建的，与本会话正在做的 deep-research 任务高度一致。
2. **出现了"元技能"这一类**（4 个）：审计 Agent 框架、给 Agent 做 MBTI 诊断、任务对齐/实施。这说明使用者把 Agent 自身当成了调研对象。
3. **几乎全部技能都遵循了渐进式披露**：描述里普遍写明"做什么 + 何时用"，并带中文触发关键词（如 `cli-empirical-docs` 的"针对每一个指令做测试"）。
4. **一个卫生问题**：`skills/` 目录下同时存在 `malaysia-phone-osint/` 目录与 `malaysia-phone-osint.zip`（重复包），建议清理 zip。

### 6.5 连接器清单（13 个可用）

`canva`、`edgeone-pages`、`fosunwealth`、`futu-mcp`、`github`、`kdocs`、`kling-ai-plugin`、`laiye-adp`、`linear-mcp`、`moomoo-mcp`、`notion`、`tiktok`

> 其中 **github** 与 **notion** 已安装。这份清单本身就是一个"连接层"（MCP 类）的实例——注意它是**插件市场分发的连接器配置索引**，与用户手动写在 `mcp.json` 里的 3 个 MCP Server 是两条不同的接入路径。

---

## 七、选型决策树

**问题 1：你要解决的是"Agent 不知道怎么做"，还是"Agent 碰不到某个系统"？**

- 不知道**怎么做** → 用 **Agent Skills（SKILL.md）**：写清流程、示例、边界，需要确定性步骤就捆脚本。
- 碰不到某个**系统/数据** → 用 **MCP Server**：本地系统走 stdio，远程走 Streamable HTTP。
- 两者都要 → **叠加**：MCP 提供工具，Skill 教怎么用这些工具。

**问题 2：你的规则是"全局"还是"本仓库"？**

- 全局行为约束 → 系统提示 / 自定义指令。
- 本仓库约定 → **`AGENTS.md`**（跨工具）或 **`CLAUDE.md`**（Claude Code 专用）。
- 特定任务的按需流程 → **Skill**。

**问题 3：多个 Agent 要互相配合？**

- → **A2A**（Agent Card + Task 生命周期）。注意 A2A 已纳入 Linux Foundation（本次未独立核实其捐赠时间，标为待确认）。

**问题 4：去哪里找现成的？**

| 找什么 | 去哪里（按可信度排序） |
|---|---|
| 官方技能 | `github.com/anthropics/skills`、`github.com/anthropics/claude-plugins-official` |
| 官方 MCP server | `registry.modelcontextprotocol.io` |
| 第三方 MCP server | PulseMCP（有官方 Registry API 实现）→ Smithery → Glama（数量最大但需自行甄别） |
| 调试 MCP server | **MCP Inspector**（官方） |
| 发布自己的 MCP server | **mcp-publisher**（官方 CLI） |
| 创作技能 | **skill-creator** 元技能 |

**问题 5：怎么降低风险？**

1. 装之前**读一遍** SKILL.md / 检查 MCP server 来源与提交历史。
2. 权限**最小化**（本机 gog 的 `--allow-tool` 白名单就是好做法）。
3. 能沙箱就沙箱；能锁版本就锁版本（防 rug pull）。
4. 敏感操作走**人在环**审批。
5. 别用来源不明的"技能市场"站点。

---

## 八、数据可信度与口径问题

### 8.1 来源分级

| 等级 | 含义 | 本报告中的适用 |
|---|---|---|
| **A 级（一手核实）** | 官方规范站点、官方 changelog、Linux Foundation 新闻稿、advisory 数据库、本机实测 | MCP 版本史与 2026-07-28 变更、AAIF 成立、SKILL.md frontmatter 约束、渐进式披露、CVE 编号、本机盘点数据 |
| **B 级（交叉验证）** | 多方来源一致 | 传输层演进、OAuth 模型、SDK 分层、目录站归属 |
| **C 级（`[不确定]`）** | 单一来源 / 抓取失败 / 未能核实 | 见 8.2 |

### 8.2 明确标注的不确定项

- **Trail of Bits 的 MCP 攻击类别论文**：未找到可确证的单一权威来源 —— **缺口**。
- **`modelcontextprotocol.io` 与 `invariantlabs.ai`**：直接抓取返回空，官方文档与 Invariant 细节依赖二手汇总。
- **`agentskills.io`**：JS 重，直接抓取未渲染，内容据官方仓库 README 与三方转述推断。
- **Registry 上线时间（2025-09-08 preview）与 API 冻结（2025-10-24）**：来自二手/中文来源，未在官方英文页面确认。
- **MCP Registry 授权页**：多次抓取返回空，授权细节来自官方 changelog + Microsoft Learn。
- **A2A 捐给 Linux Foundation（2025-06）**：**本次未独立核实**，标为待确认。
- **`mcp` CLI**：未发现单一官方二进制（官方 CLI 为 `mcp-publisher` 与 `mcp-inspector`/`mcpdo`）。
- **mcp.so 运营方**：无法核实。
- **"OAuth 2026 强制迁移（2026-10-01 停用旧认证）"**：仅见于一篇 CSDN 帖，**未被一手来源印证，疑似不实**。
- **各类"技能数量"**：`skillsmp` 自称 25,000+ vs 700,000+ 自相矛盾；"85,000+/280,000+ 公开技能"均来自二手聚合，**不可引用**。
- **OX Security 规模数字**（>20 万 server / >3.2 万仓库）：其自估，未独立验证。
- **Cycode / Asana 事件**：厂商自报或中文媒体报导，**无 CVE ID**。

### 8.3 三个必须记住的"口径陷阱"

1. **"MCP 服务器破 10 万"** ≠ 官方 Registry 收录量。前者是 LF 新闻稿的生态口径，后者 2026-09 约 3 万条。第三方站的 13.7 万等数字存在重复计数。
2. **技能预算单位是 tokens 不是 words**。官方要求 `SKILL.md` 正文 **<5,000 tokens / <500 行**。
3. **description 长度上限是 1,024 字符（规范），不是 200 字符（帮助中心）**。以规范为准。

---

## 附：主要参考来源

- [Agent Skills Specification — agentskills.io](https://agentskills.io/specification)
- [anthropics/skills（官方技能仓库）](https://github.com/anthropics/skills)
- [anthropics/claude-plugins-official（官方插件目录）](https://github.com/anthropics/claude-plugins-official)
- [Introducing Agent Skills — Anthropic](https://www.anthropic.com/news/skills)
- [What are skills? — Claude Help Center](https://support.claude.com/en/articles/12512176-what-are-skills)
- [How to create custom skills — Claude Help Center](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- [Use Agent Skills with GitHub Copilot — Microsoft Learn](https://learn.microsoft.com/en-us/visualstudio/ide/copilot-agent-skills)
- [Azure Agent Skills — Microsoft Learn](https://learn.microsoft.com/en-us/training/support/agent-skills)
- [What is MCP? — modelcontextprotocol.io](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro)
- [MCP Versioning](https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning)
- [MCP Spec Changelog — 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- [MCP Spec Changelog — 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/changelog)
- [MCP Transports](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)
- [MCP SDKs](https://modelcontextprotocol.io/docs/2026-07-28/sdk)
- [The MCP Registry (About)](https://modelcontextprotocol.io/registry/about)
- [官方 MCP Registry](https://registry.modelcontextprotocol.io/)
- [Linux Foundation Announces the Formation of the Agentic AI Foundation](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)
- [MCP Inspector（官方，GitHub）](https://github.com/modelcontextprotocol/inspector)
- [MCP Registry（官方，GitHub）](https://github.com/modelcontextprotocol/registry)
- [PulseMCP](https://www.pulsemcp.com/) · [Smithery](https://smithery.ai/) · [Glama](https://glama.ai/mcp/servers) · [mcp.so](https://mcp.so/) · [Cursor Directory](https://cursor.directory/)
- [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)
- [Invariant Labs — MCP Tool Poisoning Attacks](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)
- [Elastic Security Labs — MCP Tools: Attack Vectors and Defense Recommendations](https://www.elastic.co/security-labs/mcp-tools-attack-defense-recommendations)
- [GitLab Advisory DB — @modelcontextprotocol/inspector (CVE-2025-49596)](https://advisories.gitlab.com/pkg/npm/@modelcontextprotocol/inspector/)
- [GitHub Advisory DB — git-mcp-server (CVE-2025-53107)](https://github.com/advisories/GHSA-3q26-f695-pp76)
- [JFrog — CVE-2025-6514: mcp-remote 命令注入](https://www.jfrogchina.com/blog/cve-2025-6514/)
- [Docker — Coding Agent Horror Stories: The Security Crisis](https://www.docker.com/blog/coding-agent-horror-stories-the-security-crisis-threatening-developer-infrastructure/)
- [MCP Security Best Practices（2025-06-18 规范）](https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices)
- [MCP-Bench（ICLR 2026 poster）](https://iclr.cc/virtual/2026/poster/10008216)
- [OSWorld-MCP Leaderboard](https://osworld-mcp.github.io/)
- [Claude Code plugin marketplaces 文档](https://code.claude.com/docs/en/plugin-marketplaces)
