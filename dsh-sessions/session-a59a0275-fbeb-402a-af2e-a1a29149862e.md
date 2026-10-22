# Session session-a59a0275-fbeb-402a-af2e-a1a29149862e

- Title: 有什么mcp可以用于go lang的编程
- CWD: `C:\Users\Admin\Documents\deepseek-harness\default-workspace`
- Created: 2026-10-22 12:21:12


---

## [user] 2026-10-22 12:21:12 · source=user

有什么mcp可以用于go lang的编程

---

## [user] 2026-10-22 12:21:12 · source=runtime-context

Current runtime context. This snapshot supersedes earlier runtime-context snapshots.

Current working directory: "C:\\Users\\Admin\\Documents\\deepseek-harness\\default-workspace".

Current DSH file policy: workspace-write. Any available operation enforced by the DSH file sandbox may modify files under the session workspace: "C:\\Users\\Admin\\Documents\\deepseek-harness\\default-workspace". Some platform temporary areas may also be writable.

Approval policy: ask. Operations that require approval may ask through the configured answerers; without an available answerer, the request fails closed.

You are the Team Lead named "lead".
Use list_agents({}) to find your teammates and their names.
To message another teammate, use send_message({ target: "<teammate name>", message: "..." }).

Current DeepSeek Harness implementation checkout: "C:\\Users\\Admin\\AppData\\Local\\Programs\\DeepSeek Harness\\resources\\app.asar\\dsh\\".

Current DeepSeek Harness Web GUI URL: "http://127.0.0.1:52307".

---

## [user] 2026-10-22 12:21:12 · source=skill-catalog

<system-reminder>
A skill is a reusable set of task-specific instructions. The following skills are available in this session:

<available_skills>
- `ab-test-setup`: When the user wants to plan, design, or implement an A/B test or experiment. Also use when the user mentions "A/B test," "split test," "experiment," "test this change," "variant copy," "multivariate test," or "hypothesis." For tracking implementation, see analytics-tracking.
- `academic-paper-expert`: 学术论文写作专家。精通社科/理工科论文结构、APA/GB-T7714引用规范、学术表达范式。 提供论文结构设计、文献综述、摘要撰写、学术语言润色等全流程指导。 当用户提到「写论文」「学术写作」「文献综述」「论文润色」「摘要」时触发。
- `accessibility-review`: Run a WCAG 2.1 AA accessibility audit on a design or page. Trigger with "audit accessibility", "check a11y", "is this accessible?", or when reviewing a design for color contrast, keyboard navigation, touch target size, or screen reader behavior before handoff.
- `adaptyv`: Cloud laboratory platform for automated protein testing and validation. Use when designing proteins and needing experimental validation including binding assays, expression testing, thermostability measurements, enzyme activity assays, or protein sequence optimization. Also use for submitting experiments via API, tracking experiment status, downloading results, optimizing protein sequences for better expression using computational tools (NetSolP, SoluProt, SolubleMPNN, ESM), or managing prote...
- `aeon`: This skill should be used for time series machine learning tasks including classification, regression, clustering, forecasting, anomaly detection, segmentation, and similarity search. Use when working with temporal data, sequential patterns, or time-indexed observations requiring specialized algorithms beyond standard ML approaches. Particularly suited for univariate and multivariate time series analysis with scikit-learn compatible APIs.
- `agent-browser`: Automates browser interactions for web testing, form filling, screenshots, and data extraction. Use when the user needs to navigate websites, interact with web pages, fill forms, take screenshots, test web applications, or extract information from web pages.
- `agent-browser-core`: OpenClaw skill for the agent-browser CLI (Rust-based with Node.js fallback) enabling AI-friendly web automation with snapshots, refs, and structured commands.
- `agent-development`: This skill should be used when the user asks to "create an agent", "add an agent", "write a subagent", "agent frontmatter", "when to use description", "agent examples", "agent tools", "agent colors", "autonomous agent", or needs guidance on agent structure, system prompts, triggering conditions, or agent development best practices for CodeBuddy Code plugins.
- `agent-harness-extension-audit`: 审计本机已安装的 AI agent 框架（Hermes Agent、DeepSeek Harness/DSH、WorkBuddy、OpenClaw 等）的「扩展面」——MCP 目录、内置/可选技能、插件目录、记忆提供方、搜索后端——先读本地源码与文档建立权威能力图谱，再体检用户实际配置，最后映射到用户目标给出落地方案。当用户问「XX agent 要装什么 MCP / 技能」「怎么提升 XX 的搜索/记忆/知识库能力」「我的 XX 配置有什么问题」时使用。核心价值：**不靠模型记忆猜能力，而是从本机仓库读出精确的条目清单与数量**。
- `agent-mbti`: AI Agent personality diagnosis and configuration system based on MBTI framework. Use when users want to (1) test/diagnose an Agent's personality type, (2) understand the gap between Agent's actual personality and user's desired personality, (3) generate configuration recommendations to adjust Agent behavior, (4) customize Agent's communication style, proactivity, reasoning approach, or execution patterns. Supports both free tier (quick assessment) and premium tier (full 93-question assessment...
- `agent-team-orchestration`: Orchestrate multi-agent teams with defined roles, task lifecycles, handoff protocols, and review workflows. Use when: (1) Setting up a team of 2+ agents with different specializations, (2) Defining task routing and lifecycle (inbox → spec → build → review → done), (3) Creating handoff protocols between agents, (4) Establishing review and quality gates, (5) Managing async communication and artifact sharing between agents.
- `agentmail`: Email inbox for AI agent

---

## [user] 2026-10-22 12:21:12 · source=time-context

Time sampled while preparing turn 1, step 1: 2026-10-22T12:21:11+08:00[Asia/Kuala_Lumpur]
Browser time zone for this request: Asia/Kuala_Lumpur. Interpret otherwise-unqualified dates and times in this zone.
Elapsed since the preceding model-visible message: unavailable.

---

## [user] 2026-10-22 12:22:27 · source=runtime-context

Current runtime context. This snapshot supersedes earlier runtime-context snapshots.

Current working directory: "C:\\Users\\Admin\\Documents\\deepseek-harness\\default-workspace".

Current DSH file policy: danger-full-access. The DSH file sandbox does not restrict file modifications by available operations.

Approval prompts are disabled in this session: actions that require approval are rejected automatically — do not request sandbox escalation (do not set `sandbox_permissions`).

You are the Team Lead named "lead".
Use list_agents({}) to find your teammates and their names.
To message another teammate, use send_message({ target: "<teammate name>", message: "..." }).

Current DeepSeek Harness implementation checkout: "C:\\Users\\Admin\\AppData\\Local\\Programs\\DeepSeek Harness\\resources\\app.asar\\dsh\\".

Current DeepSeek Harness Web GUI URL: "http://127.0.0.1:52307".

---

## [user] 2026-10-22 12:22:27 · source=user-approval

The approval policy changed from "ask" to "never" (changed by the user).

---

## [assistant] turn 1 · 2026-10-22 12:23:51 · 160002 ms

已在本机实测确认：你的环境里最好的那个方案**已经装好了**。结论如下。

## 1. 首选：官方 gopls 内置 MCP（Go 团队维护）

gopls ≥ v0.20 自带 MCP server。你本机是 `gopls v0.24.0` + `go1.27.3`，我实际拉起 `gopls mcp` 做了握手，返回 `serverInfo: gopls v1.0.0`，协议 `2025-06-18`，工具列表如下（共 8 个）：

| 工具 | 作用 |
|---|---|
| `go_workspace` | 判断 module / workspace / GOPATH 结构（会话开头必用） |
| `go_search` | 模糊搜符号（类型、函数、`pkg.Symbol`），上限 100 条 |
| `go_file_context` | 一个文件依赖了同包哪些声明 |
| `go_package_api` | 包的公开 API 摘要 |
| `go_symbol_references` | 改代码前查符号所有引用（支持 `T.M`、`lib.T.M`） |
| `go_diagnostics` | 全工作区编译/静态诊断，改完必跑 |
| `go_rename_symbol` | 跨工作区重命名，返回待应用 edits |
| `go_vulncheck` | 对 `./...` 跑漏洞检查（动 go.mod 后必跑） |

两种运行模式（官方文档 `gopls/doc/features/mcp.md`）：

- **detached（stdio）**：`gopls mcp` —— 独立无头 LSP，只能看到**已保存**的文件
- **attached（SSE）**：`gopls serve -mcp.listen=localhost:8092` → `http://localhost:8092/sessions/1` —— 复用你编辑器里那个 LSP 会话，能看见**未保存**的 buffer

另外 `gopls mcp -instructions > gopls-mcp.md` 可以导出官方给模型的作业指导（读代码工作流 / 编辑后必须跑 diagnostics 等），建议一并喂给 agent。

价值点：它不是 grep，是**类型检查器级别**的语义——接口由哪些具体类型实现、跨包同名符号、被遮蔽的作用域都能精确解析。

## 2. 社区增强版（官方 8 个工具不够用时）

- **xieyuschen/gopls-mcp** — 60★, BSD-3, 活跃（2026-10-18）。gopls 的 fork，专攻语义任务，官方 benchmark 称比 grep 导航少 2–4× 工具调用；有 Claude Code / Codex 插件，Windows 一条 `irm https://gopls-mcp.org/install.ps1 | iex`。注意：它是社区项目，非 Google 官方。
- **hloiseau/mcp-gopls** — 104★, Apache-2.0，2026-06 还在更新，LSP 分析 + 测试 + 覆盖率。
- **Yantrio/mcp-gopls** — 46★，2025-06 后基本停更，仅作参考。
- **mickeyinfoshan/lsp-mcp** — 2★，Go/TS/Python 多语言 LSP 桥。

## 3. 如果你是想「用 Go 写 MCP Server」

- **modelcontextprotocol/go-sdk** — 5,256★，官方 SDK，与 Google 合作维护，活跃。gopls 自己的 MCP 就是用它写的。
- **mark3labs/mcp-go** — 9,180★, MIT，社区最流行。
- `ktr0731/go-mcp` 已归档，README 直接指向官方 SDK，别再用。

## 4. 通用型（配合 Go 开发）

GitHub MCP（**你本机已连接**，PR/issue/代码搜索）最实用；其余按需加数据库（Postgres/SQLite）、文档检索（Context7 类）、浏览器（本机市场已上架 Chrome DevTools）。本机连接器市场 9 个里**没有 Go 专用项**，所以 gopls 只能走自定义 stdio 配置。

## 5. 在 DSH 里接上它

```json
{ "name": "gopls", "transport": "stdio", "command": "gopls", "args": ["mcp"] }
```

attached 模式则用 `transport: "streamable-http"`, `url: "http://localhost:8092/sessions/1"`（需先手动起 `gopls serve -mcp.listen=localhost:8092`）。

## 6. 两个实测踩到的坑

- gopls 首次运行要写 `%LOCALAPPDATA%\gopls` 缓存。我最初在 workspace-write 沙箱下直接报 `can't write executable hash: ... Access is denied`，放开文件权限后正常。若在受限环境里接，记得放行这个目录。
- 工具少是**刻意设计**：`go_context`、`go_file_metadata`、`go_file_diagnostics`、`go_references` 默认关闭（token 太贵或模型容易传错参数），可在 gopls 设置里通过 `MCPTools` 显式打开。

需要的话我可以现在就把它接进 DSH（一条 `mcp_connector_configure`），接完顺手验证工具能不能列出来。

---

## [user] 2026-10-22 12:26:02 · source=user

安装cli：Context7

---

## [assistant] turn 2 · 2026-10-22 12:27:20 · 78516 ms

已装好并实测跑通。

## 安装结果

- **包**：`ctx7` v0.8.1（Upstash 官方发布，主页 context7.com，仓库 upstash/context7）
- **位置**：`C:\Users\Admin\AppData\Local\hermes\node\ctx7.cmd`（npm 全局 prefix）
- **验证**：`--version` → 0.8.1；文档查询真实可用

## 实测两条

```
ctx7 library go "goroutines and channels"
```
→ 解析出 4 个可用库 ID：`/golang/go`（9662 片段）、`/websites/go_dev_doc`、`/golang/website`、`/websites/go_dev_ref`

```
ctx7 docs /golang/go "context cancellation with timeout"
```
→ 返回 5,690 字符，含 `context.WithTimeout` 签名/参数/返回值 + Go 源码里 HTTP/2 重试退避的真实片段。匿名即可用，不需要 API key。

## 命令一览

| 命令 | 用途 |
|---|---|
| `ctx7 library <name> [query]` | 库名 → Context7 library ID |
| `ctx7 docs <libraryId> <query>` | 按库 ID 拉取文档/代码片段 |
| `ctx7 setup --claude/--cursor/--vscode/--codex/--gemini ...` | 自动写入对应 agent 配置（支持 `--mcp` 或 `--cli` 两种模式、`-p` 项目级） |
| `ctx7 login` / `whoami` / `logout` | 登录提额（当前 Not logged in） |
| `ctx7 upgrade` | 自升级 |

## 两个本地坑（已踩到）

1. **PowerShell 执行策略**：本机五个作用域全是 `Undefined`（Windows 客户端默认 Restricted），所以 `ctx7` 解析到 `ctx7.ps1` 会被拒：`无法加载文件 ... 在此系统上禁止运行脚本`。直接用 `ctx7.cmd` 即可；想彻底解决需 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`——这属于改安全策略，我没动，你点头我再改。
2. **`ctx7 setup` 没有 DSH 目标**：只认 Claude Code / Cursor / VS Code / Codex / Gemini / Copilot / OpenCode / Devin / Antigravity。

## 要不要顺手接进 DSH

DSH 侧走 MCP 连接器更顺（Context7 官方托管端点，HTTP 传输），接上后我这边能直接调 `resolve-library-id` / `get-library-docs`，不用你手动敲 CLI。一条 `mcp_connector_configure` 的事——要接就说一声。
