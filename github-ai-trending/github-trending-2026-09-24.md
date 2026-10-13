# GitHub 趋势日报 · 2026-09-24

> 数据源：github.com/trending（daily 为主，weekly 补位）｜筛选口径：当日新增 Star 高 + 技术方向有代表性 + 工程参考价值
> 去重：本期 10 条详细条目**全部为前三期（09-17 / 09-18 / 09-23）未展开的新面孔**；上期已推仓库的新动态单独成节。

---

## 一、榜单速览（本期 10 条）

| # | 仓库 | 语言 | 日新增 | 周新增 | 总 Star | 一句话 |
|---|------|------|--------|--------|---------|--------|
| 1 | obra/superpowers | Shell | +474 | — | 290.8k | 把软件工程方法论固化成 Agent 强制技能的框架 |
| 2 | DeusData/codebase-memory-mcp | C | +190 | — | 44.7k | 代码库知识图谱 MCP，纯 C 单二进制，token 省 99% |
| 3 | davila7/claude-code-templates | Python | +389 | +613 | 31.6k | 一键给 Claude Code 装 agents/commands/MCP/hooks/skills |
| 4 | HKUDS/CLI-Anything | Python | +57 | — | 50.0k | 自动为任意软件生成 CLI，让所有软件 Agent 原生 |
| 5 | strands-agents/harness-sdk | Python | +115 | — | 8.0k | AWS Strands 的 harness SDK，一行组装生产级 Agent |
| 6 | pbakaus/impeccable | JavaScript | +304 | — | 70.5k | 让 AI 生成的前端不再"AI 味"的设计语言技能 |
| 7 | Fission-AI/OpenSpec | TypeScript | — | +1,538 | 70.1k | 面向 AI 编码助手的规格驱动开发（SDD） |
| 8 | BuilderIO/agent-native | TypeScript | +87 | — | 6.6k | 构建 Agent 原生应用的全栈框架 + 模板矩阵 |
| 9 | TNT-Likely/PanWatch | Python | +95 | — | 1.6k | 自托管 AI 盯盘助手，TradingAgents 多 Agent 决策 |
| 10 | cloudflare/quiche | Rust | — | +707 | 12.5k | QUIC / HTTP3 的 Rust 实现（本期唯一非 Agent 项目） |

---

## 二、10 条详细

### 1. obra/superpowers — 把"工程纪律"写成 Agent 无法跳过的强制流程

**事件**
`obra/superpowers`（作者 Jesse Vincent / Prime Radiant 团队）今日日榜第 5，+474，总 Star 已达 **290.8k**，是当前榜单总 Star 最高的仓库之一（26.0k fork、682 commits、MIT 许可）。它不是一个工具，而是一套**完整的软件开发方法论**，以可组合的 "skills" 形式注入编码 Agent。

**核心内容**
- **改变默认行为**：传统 Agent 接到需求会直接写代码；Superpowers 让 Agent **先停下来问清楚要做什么** —— 通过提问细化想法 → 分节呈现设计等你确认 → 才进入实现。
- **7 阶段基本工作流**：
  1. `brainstorming` — 写码前激活，产出设计文档
  2. `using-git-worktrees` — 设计获批后建隔离工作区、验证干净测试基线
  3. `writing-plans` — 拆成 2–5 分钟的小任务，每个含确切文件路径 + 完整代码 + 验证步骤
  4. `subagent-driven-development` / `executing-plans` — 前者每任务派新子代理并逐个评审（最彻底），后者本会话内联实现、最后整体评审一次（最省钱）
  5. `test-driven-development` — 强制 RED-GREEN-REFACTOR，**会删除在测试之前写的代码**
  6. `requesting-code-review` — 任务之间评审，关键问题阻塞进度
  7. `finishing-a-development-branch` — 验证测试、给合并/PR/保留/丢弃选项、清理 worktree
- **技能库**分三类：测试（TDD）、调试（`systematic-debugging` 四阶段根因流程、`verification-before-completion`）、协作（brainstorming / writing-plans / dispatching-parallel-agents / receiving-code-review 等）。
- **跨工具适配 16+ 种 harness**：仓库为 `.claude-plugin`、`.codex-plugin`、`.cursor-plugin`、`.devin-plugin`、`.hermes-plugin`、`.kimi-plugin`、`.muse-plugin`、`.opencode`、`.pi/extensions`、`.agents/plugins` 各提供独立插件；支持 Claude Code、Codex、Cursor、Devin CLI、Factory Droid、Gemini CLI、GitHub Copilot CLI、Grok Build CLI、Kimi Code、OpenCode、Pi、Qwen Code 等。
- **自我诊断**：`diagnosing-superpowers` 技能让 Agent 读会话记录、以**行级证据**报告问题，并可打包脱敏包提 bug。
- **遥测**：brainstorming 的可视化伴侣会加载 logo，仅含版本号；可用 `SUPERPOWERS_DISABLE_TELEMETRY` 或 Claude Code 的 `DISABLE_TELEMETRY` / `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 关闭。
- **治理**：一般不接受新技能贡献；技能改动必须兼容所有支持的编码代理，需切 `dev` 分支、遵循 `writing-skills`、跑 `superpowers-evals` 的 drill 评测。

**值得关注的原因**
1. **它把"提示词软约束"升级为"流程硬约束"**。README 明确写：技能是**强制性工作流，而非建议**。TDD 技能甚至会删除测试前写的代码 —— 这是用破坏性动作保证纪律，而不是靠模型自觉。
2. **它是"技能分发格式战争"的又一实锤**。同一个仓库同时维护 10+ 种 harness 的插件目录，说明 SKILL.md 类格式已成为事实标准，而各家 harness 的差异只剩"插件目录名"这一层。
3. **290k star 的量级值得警惕地看待**：这类"方法论仓库"star 增长往往靠社区传播而非实际使用，判断价值要看它是否真的改变了你的 Agent 行为 —— 建议拿一个中等项目跑一遍 7 阶段流程再决定是否长期保留。
4. 对团队有直接意义：它把 code review、worktree 隔离、完成前验证这些**人类工程习惯**编码成 Agent 默认动作，是"AI 写码后如何维持代码质量"这一问题的现成答案。

---

### 2. DeusData/codebase-memory-mcp — 用知识图谱替掉 Agent 的 grep 循环

**事件**
`DeusData/codebase-memory-mcp` 今日日榜第 14，+190，总 Star 44.7k（C 语言，MIT）。它是一个**纯 C 编写、零依赖、单静态二进制**的 MCP 服务器，把代码库索引成**持久化知识图谱**供 Agent 查询。配套论文 arXiv:2603.27277《Codebase-Memory: Tree-Sitter-Based Knowledge Graphs for LLM Code Exploration via MCP》。

**核心内容**
- **解决什么**：Agent 理解代码库只能"逐文件 grep / read"，导致 token 爆炸、工具调用多、无法回答跨文件/跨包/跨服务的结构性问题（"谁调用了 ProcessOrder"、"哪些函数是死代码"）。它的做法是**一次图查询替代几十次 grep/read 循环**。
- **本身不含 LLM**：只建图与查图，自然语言→图查询的翻译由你的 MCP 客户端（如 Claude Code）承担，**因此不需要额外 API Key**。
- **三层解析**：
  - 解析层：vendored **tree-sitter** 语法，覆盖 **162 种语言**
  - 语义层（Hybrid LSP）：纯 C 实现的轻量类型解析，对标 tsserver / pyright / gopls / Roslyn / JDT / rust-analyzer，完整支持 Python、TS/JS/JSX/TSX、PHP、C#、Go、C/C++、Java、Kotlin、Rust、Perl 共 11 种
  - 索引管线：RAM-first，LZ4 压缩读取 + 内存内 SQLite，结束一次性落盘后释放内存；持久化在 `~/.cache/codebase-memory-mcp/`（SQLite WAL，ACID）
- **能力**：架构总览、ADR 管理、Louvain 社区发现、Git diff 影响映射 + 风险分级、调用图解析、死代码检测、类 Cypher 查询；语义向量搜索（内置 Nomic `nomic-embed-code`，40K tokens / 768 维 int8，编译进二进制，11 信号组合打分）+ BM25 全文搜索（FTS5，区分 camelCase/snake_case）；HTTP 路由↔调用点匹配、gRPC/GraphQL/tRPC 检测、跨仓库 `CROSS_*` 边；内置 3D 图谱可视化 UI（localhost:9749）；IaC 索引（Dockerfile / K8s / Kustomize）；团队可共享图产物（`.codebase-memory/graph.db.zst`，zstd 8–13:1）。
- **关键数字**：

  | 指标 | 数值 |
  |---|---|
  | 支持语言 | 162 种 |
  | MCP 工具数 | 17 |
  | 客户端接入面 | 45（39 自动检测 + 6 条件） |
  | Linux 内核完整索引 | **3 分钟**（28M LOC / 75K 文件 → 4.81M 节点、7.72M 边） |
  | Django 完整索引 | 约 6 秒（49K 节点、196K 边） |
  | Cypher 查询 | **<1 ms** |
  | 死代码检测 | 约 150 ms |
  | Token 节省 | **约 99.2%**（5 个结构查询 3,400 tokens vs 文件搜索 412,000 tokens，120 倍） |
  | 测试 | 8,060（141 个套件） |
  | 论文评测 | 31 个真实仓库：83% 答案质量、10× 更少 token、2.1× 更少工具调用 |

- **安全**：SLSA 3、Sigstore cosign 签名、SHA-256 校验、CodeQL SAST、VirusTotal 扫描（v0.7.0 五平台 0/72）。最近提交在 **2026-09-24**。

**值得关注的原因**
1. **它是"上下文经济"最锋利的一刀**。99.2% token 节省不是优化，是换了一个信息获取范式 —— 从"让模型读文件"变成"让模型查图"。同一思路在本期 `video-use`（45M tokens → 12KB 文本）上再次出现，说明**给 Agent 更少但更结构化的输入**正在成为通用解法。
2. **纯 C + 单二进制 + 零依赖 + 无 API Key** 的组合，是自托管场景的最优解：没有运行时、没有 Docker、没有密钥管理，直接扔进 PATH 就能用。这类"反框架化"的分发形态值得作为选型偏好记下来。
3. **它把"代码智能"从 IDE 里搬到了 Agent 的上下文里**。VS Code 的 LSP 服务于人类阅读，而它是让 Agent 用一次查询拿到调用链、影响面和死代码 —— 这是给 Agent 而不是给人做的工具，定位清晰。
4. 谨慎点：162 种语言中只有 11 种有真正的类型解析，其余靠 AST + 名称匹配（README 自己给了语言质量分级，OCaml/Haskell 落在 <75%）。判断值不值，先拿你主语言跑一遍 `get_architecture` 看准确率。

---

### 3. davila7/claude-code-templates — Claude Code 的"配置分发市场"，但刚修了一个 RCE

**事件**
`davila7/claude-code-templates` 今日日榜第 3（+389），周榜 +613，总 Star 31.6k。最新版本 **v1.29.6**（2026-09-17），MIT 许可。它是一个 CLI，用一条 `npx` 命令给 Claude Code 安装 agents / commands / MCP / settings / hooks / skills。

**核心内容**
- **用法**：
  ```bash
  npx claude-code-templates@latest \
    --agent development-team/frontend-developer \
    --command testing/generate-tests \
    --mcp development/github-integration --yes
  ```
  也可交互式浏览（不带参数），或单独装一个组件（`--hook git/pre-commit-validation`、`--setting performance/mcp-timeouts`）。组件从 GitHub raw/API 下载后合并进 `.mcp.json` / settings / hooks。
- **附带 4 个监控工具**：`--analytics`（会话实时监控与性能指标）、`--chats [--tunnel]`（移动端对话查看，可走 Cloudflare Tunnel 远程访问）、`--health-check`（安装诊断）、`--plugins`（市场/已装插件与权限管理）。
- **组件规模**：100+ 可浏览组件；来源包括 K-Dense 科学技能 139 个、Anthropic 官方技能 21 + 开发指南 10、obra/superpowers 14、alirezarezvani 36、wshobson/agents 48、awesome-claude-code 21 条命令。
- **⚠️ 安全事件（重点）**：**GHSA-79wm-x847-7cvg 命令注入（RCE）**，在 **v1.29.4** 修复。成因是 `--studio` 服务器绑定 `0.0.0.0` + CORS 通配 + 无鉴权，且把请求体字段直接传给 `spawn(..., { shell: true })`，导致可通过 `POST /api/execute`（prompt 参数）与 `/api/install-agent`（agentName 参数）执行任意 OS 命令。修复：移除 `shell: true`、校验 `agentName`、绑定 `127.0.0.1`、限制 CORS，并为 Windows 补 `.cmd` shim 解析（NPX_CMD / CLAUDE_CMD）。
- **架构演进**：新增 **Rust 移植版 `cli-rust`（#640）**，二进制名 `cct`，与 Node CLI **字节级对齐**（用 `diff -r` 验证），支持 npm shim（可选依赖分发）、Homebrew、cargo-binstall、install.sh；CI 仅在 `cli-rust/**` 变化时触发。
- **仓库加固（#458）**：npm 安装全部加 `--ignore-scripts`、修复 discord 通知里的 shell 注入、所有 workflow 加最小权限、新增 `.npmrc`、dependabot 与 CODEOWNERS。
- 其他：新增 OWASP 综合安全技能（#665，含把 OWASP Top 10 标签从 2025 更正为 2021）；删除长期失败的 GitHub Packages workflow（#943）；暂停每周 newsletter（#939）；组件目录生成器支持 `--skip-downloads`（约 2 秒重生成）。

**值得关注的原因**
1. **这是一个真实的供应链攻击面案例**，而且是"经典三件套"叠加：`0.0.0.0` 绑定 + CORS 通配 + `shell: true`。任何做本地 Agent 辅助服务（studio / dashboard / preview server）的项目都该照这三条自查。修复动作也值得抄：绑定回环、白名单参数、去掉 shell 层。
2. **`--ignore-scripts` 成为 Agent 生态的默认安全基线**。继 09-18 期 n8n 的 SBOM/OpenVEX 之后，这是第二例把"禁止安装脚本"写进 CI 的项目，说明供应链安全已从口号变成流水线配置。
3. **"配置分发"正在变成一门生意**。这个仓库本质是 Claude Code 的 npm —— 把社区沉淀的 agents/skills/MCP 配置打包分发。它的存在说明：Agent 生态的痛点已经从"模型不够强"转移到"配置不知道装什么"。
4. **Rust 重写 CLI 且要求字节级对齐**是很有意思的工程决策：保留 Node 版作为参考实现，Rust 版作为分发形态（单二进制、Homebrew、cargo-binstall），既拿到性能与分发优势，又用 diff 测试锁住行为一致性。这个模式可以直接借鉴。

---

### 4. HKUDS/CLI-Anything — 让"所有软件"变成 Agent 原生

**事件**
`HKUDS/CLI-Anything`（香港大学数据智能实验室）今日日榜第 10，+57，总 Star 50.0k（Python，Apache-2.0）。标语是 **"Making ALL Software Agent-Native"**，论文 arXiv:2606.03854《CLI-Anything: Towards Agent-Native Computer Use》。

**核心内容**
- **要解决的 gap**：Agent 会推理，但用不了真实专业软件。现有三条路都很脆 —— ① 截图/像素点击/RPA 极易失效；② API 覆盖不全；③ "简化版重实现"丢掉 90% 功能。CLI-Anything 的方案是**直接驱动真实软件后端**（Blender、LibreOffice、FFmpeg、GIMP、Inkscape、QGIS…），不截图、不点击、纯命令行 + 结构化 JSON 输出。
- **7 阶段自动流水线**：一条 `/cli-anything ./gimp` 命令驱动全流程 ——
  1. Analyze（扫源码，把 GUI 操作映射到 API）
  2. Design（规划命令组、状态模型、输出格式）
  3. Implement（构建含 REPL、JSON 输出、撤销/重做的 Click CLI）
  4. Plan Tests（生成 TEST.md，含单元 + E2E 计划）
  5. Write Tests（实现完整测试套件）
  6. Document（结果写回 TEST.md；**Phase 6.5 自动生成 SKILL.md**）
  7. Publish（生成 `setup.py` 并安装到 PATH）
- **设计原则（值得背下来）**：
  - **真实软件集成** —— 生成合法项目文件（ODF / MLT XML / SVG）交真实应用渲染，"构建通往软件的结构化接口，而非替代品"；**零妥协**：后端缺失时测试**失败而非跳过**
  - **双交互模型** —— 有状态 REPL（交互式会话）+ 子命令接口（脚本/流水线）
  - **Agent 原生** —— 每个命令内建 `--json`；Agent 用标准 `--help` 和 `which` 发现能力
- **HARNESS.md 里的踩坑经验（干货）**：
  - 渲染鸿沟：GUI 应用在渲染时应用效果，需要"原生渲染器 → 滤镜翻译 → 渲染脚本"三段式
  - 时间码精度：非整数帧率（29.97fps）会累积舍入误差，必须 `round()` 而非 `int()`，测试允许 ±1 帧容差
  - 输出验证：**不要因为退出码为 0 就信任导出成功** —— 要验魔数字节、ZIP/OOXML 结构、像素分析、音频 RMS 电平、时长
- **规模**：**2,461 个测试**（1,732 单元 + 579 E2E + 19 Node.js），100% 通过；覆盖 **18 个主要应用** —— GIMP（107 测试）、Blender（208）、Inkscape（202）、Audacity（161）、LibreOffice（158）、OBS Studio（153）、Kdenlive（155）、Shotcut（154）、s&box（244）、Joplin（134）、Draw.io（138）、RenderDoc（59）、QGIS（22）、3MF（50）等。
- **CLI-Hub 包管理器**：`pip install cli-anything-hub`，提供 list / search / info / install / update / uninstall / launch，支持 pip、npm、brew、捆绑/系统工具多种安装源；Agent 可自主发现并安装（meta-skill）。CLI-Hub 当前 **v0.2.0**（2026-04-15）。
- **支持平台**：Claude Code、Cursor、Pi、OpenCode、Goose、Qodercli、OpenClaw、Codex、Hermes、Reasonix、GitHub Copilot CLI（Windsurf 即将推出）。
- **局限（官方自陈）**：需要强基础模型（Claude Opus 4.6 / Sonnet 4.6 / GPT-5.4），弱模型产出质量差；依赖源码，只有二进制需反编译时质量大幅下降；单次运行常需多次 `/cli-anything:refine` 才能覆盖全能力。

**值得关注的原因**
1. **它给了"Computer Use"一条与截图派完全相反的路线**。09-18 期推的 Tencent/BrowserSkill 走"让 Agent 用真实浏览器"，CLI-Anything 走"把 GUI 软件编译成 CLI"—— 两者共同结论是：**像素级操作不可靠，结构化接口才可靠**。这个判断在连续三期里反复出现，基本可以当结论用了。
2. **"零妥协依赖"是罕见的工程洁癖**：没有 Pillow 替 GIMP、没有自写 Blender 渲染器、后端缺失直接测试失败。这保证了产出是"真能交付的文件"而不是"看起来像的截图"。
3. **HARNESS.md 本身就是一份可复用的经验资产**：时间码舍入、滤镜翻译、输出魔数校验 —— 这些是任何做"Agent 驱动专业工具"的人都会踩的坑，已经有人替你写成文档。
4. **它把"给软件写 CLI"从一次性工作变成可批量生产**。如果你的工作流里有大量 GUI 工具（CAD、DAW、EDA、GIS），这条路线意味着不必等厂商出 API。

---

### 5. strands-agents/harness-sdk — AWS 系的"一行组装生产级 Agent"

**事件**
`strands-agents/harness-sdk` 今日日榜第 9，+115，总 Star 8.0k（Python + TypeScript monorepo，Apache-2.0，2,759 commits，最近活动 2026-09-23）。

**核心内容**
- **定位**：一个**模型驱动（model-driven）**、**运行在你进程内、无托管控制平面**的开源 SDK。适用场景一句话 —— "当你本来要自己手写 agent loop 时，改用 Strands"。
- **替代手写循环要覆盖的清单**（就是它内置的东西）：生命周期控制（轮次上限、token 预算、取消、停止原因）、工具与结构化输出、MCP、多智能体模式、记忆与会话、模型可移植性、流式、护栏、链路追踪、评测。
- **两个使用层级**：
  - **harness（推荐入口）**：一次 `create_harness()` / `createHarness()` 即得组装好的 Agent，内置为模型/工具/记忆/会话/上下文优化过的默认配置。
    ```python
    from strands_harness import create_harness
    agent = create_harness()
    agent("Find the slowest test in this repo and explain why it's slow")
    ```
    ```typescript
    import { createHarness } from '@strands-agents/harness'
    const agent = await createHarness()
    await agent.invoke("Find the slowest test in this repo and explain why it's slow")
    ```
  - **底层 SDK**：`from strands import Agent` / `import { Agent } from '@strands-agents/sdk'`，完全掌控循环、工具、模型提供方、记忆、会话与钩子。
- **Monorepo 结构**：`harness-py`（PyPI: strands-harness）、`harness-ts`（npm: @strands-agents/harness）、`strands-cli`（终端原型化与对话）、`strands-py`（PyPI: strands-agents）、`strands-ts`（npm: @strands-agents/sdk）、`site`（Astro/Starlight 文档站）、`team`（治理与跨 SDK 流程文档：原则、决策、PR 与兼容性指南、设计提案）。
- **关键特性**：模型无关（一等支持 Amazon Bedrock / Anthropic / OpenAI / Gemini + 自定义模型）；Hooks 可拦截循环任意步骤做记录/校验/重定向；护栏在错误执行前拦截；steering handlers 让 Agent 自我纠错而非静默失败。
- **版本要求**：Python 3.10+；TypeScript 侧 **Node.js 22+（2026-09-03 已正式放弃 Node 20）**。

**值得关注的原因**
1. **它与 09-23 期推的 google/ax 构成清晰的上下分层**。AX 管集群调度与沙箱（K8s 层），Strands harness 管**进程内**的 agent 循环（应用层）。这回答了"Agent 基础设施该分几层"的问题：调度层与循环层是两件不同的事，不该由一个项目同时做。
2. **"无托管控制平面、跑在你自己的进程里"是明确的立场宣示**。在 AWS 自家产品线里选择开源、进程内、可自托管，等于承认**多数场景不需要托管编排服务** —— 这与本期 `codebase-memory-mcp`（单二进制）、`PanWatch`（Docker 自托管）的方向完全一致：本地优先已成为默认架构假设。
3. **它把"手写 agent loop 最终会长成什么样"这份清单公开了**。轮次限制、token 预算、停止原因、steering handler、护栏位置 —— 即使你不用 Strands，这份清单也可以直接当作自研循环的检查表。
4. **治理文档独立成目录（`team/`）**，含跨 SDK 兼容性指南与设计提案流程 —— 双语言 SDK 最容易走偏的地方就是两套行为不一致，这是正面回应。

---

### 6. Fission-AI/OpenSpec — 用规格文件给 AI 编码上锁

**事件**
`Fission-AI/OpenSpec` 今日周榜第 17，**周 +1,538**，总 Star 70.1k（TypeScript，MIT，913 commits，最近提交 2026-09-23）。

**核心内容**
- **定位**：面向 AI 编码助手的**规格驱动开发（Spec-Driven Development, SDD）**，强制走 "spec → change → task → 实现 → 归档" 的结构化流程，让 AI 按可验证的规格工作，而不是按一段模糊的自然语言描述。
- **CLI 初始化**项目结构：`openspec/` 下含 `specs`、`changes`、`archive` 三个目录 + `config.yaml`。
- **命令族迁移**：`/opsx:*` 取代旧的 `/openspec:*`；技能数从 9 个增至 10 个（新增 `opsx:onboard` 引导流程），后续发布 **12 个 workflow skills** 到 skills.sh；可用 `npx skills add Fission-AI/OpenSpec` 安装静态技能。
- **验证（verify）逻辑**是本期的技术重点，多次修复都围绕它：需要区分 `ADDED` / `MODIFIED` / `REMOVED` / `RENAMED` 四类需求，避免把"已正确删除的需求"误报为"缺失"—— 这是规格校验里最容易出错的一类假阳性。
- **多仓库 / 工作区支持**：`multi-repo/worksets`、`context stores`、`initiative views`，面向团队级与多仓库场景。
- **工具集成**：Claude、Codex、Cursor、Qwen、Windsurf、Antigravity、Crush、OpenCode、Qoder 等（提及 21 个工具集成迁移）；文档站重建含 40 页（Start / Guides / Customize / Multi-repo / Reference / Help）。
- **归档流程**：`/opsx:sync` 为可选同步步骤；任务分组要求测试与文档保留在各自任务组内。

**值得关注的原因**
1. **它与本期 `superpowers`、`impeccable` 构成同一条主线的三个切面**：superpowers 锁**开发流程**（TDD、review、worktree），OpenSpec 锁**需求边界**（规格与变更集），impeccable 锁**输出质量**（设计规则）。共同点是把不可协商的约束**写进流程与文件**，而不是写进提示词祈祷模型遵守。
2. **"verify 要区分删除与缺失"这个细节暴露了 SDD 的真实难点**。规格驱动听起来简单，但一旦规格会演进，"什么算实现完成"就变成集合运算问题 —— 这个仓库的提交历史基本就是一部踩坑记录，值得当成 SDD 落地指南读。
3. **70k star + 913 commits 的体量**说明它已经跨过了"玩具"阶段，且 12 个 workflow skills 发布到 skills.sh 意味着它同时是"工具"也是"技能分发者"。
4. 适用判断：如果你已经在用 Claude Code / Cursor 做正式项目（而不是原型），SDD 的价值在于**把验收标准前置**；如果只是改小脚本，这套流程的开销可能大于收益。

---

### 7. pbakaus/impeccable — 61 条确定性规则，专治"AI 味"前端

**事件**
`pbakaus/impeccable`（作者 Paul Bakaus）今日日榜第 12，+304，总 Star 70.5k（JavaScript，Apache-2.0，1,913 commits、101 分支、69 tags，最近提交 2026-09-22）。一句话概括：**1 个 skill + 24 个命令 + 实时浏览器迭代 + 61 条确定性检测规则**。

**核心内容**
- **要解决的问题（说得非常具体）**：所有大模型都在同一批 SaaS 模板上训练过，缺设计指导时，生成的前端会出现同一批"套路痕迹"：
  - 到处都用 Inter 字体
  - 紫到蓝渐变
  - 卡片套卡片
  - 彩色背景上叠灰色文字
  - 每个标题上方一个圆角方形图标块
- **血统**：起点是 Anthropic 的 `frontend-design` skill（首个被广泛使用的 Claude 设计技能），在其基础上扩展。
- **工作方式**：
  1. `/impeccable init` 一次性设置 —— 只问产品核心事实的关键缺口，写入持久化的 `PRODUCT.md`（受众、目的、运行环境、约束、语气、证据）；视觉方向单独记在 `DESIGN.md`。此后命令能区分"产品事实"与"表层视觉方向"，不会混为一谈。
  2. 所有命令统一走 `/impeccable <command> <target>`；可用 `pin` 生成独立快捷命令（如 `pin audit` → `/audit`）。
  3. **检测引擎跑 61 条确定性规则，无需 LLM、无需 API key**；另有纯 LLM 的 critique 检查作为补充。
  4. **Live mode**：在浏览器里直接对元素做视觉变体迭代。
  5. **设计 Hook**：直接编辑 UI 文件时自动跑检测器，把发现反馈回 Agent 流程。
- **24 个命令**（部分）：`craft`（先塑形后构建）、`shape`（写码前规划 UX/UI）、`critique`（UX 评审：层级/清晰度/情感共鸣）、`audit`（无障碍/性能/响应式）、`polish`、`distill`、`harden`（错误处理、i18n、文本溢出、边界情况）、`onboard`（首次运行、空状态、激活路径）、`animate`、`colorize`、`typeset`、`layout`、`delight`、`overdrive`、`clarify`、`adapt`、`optimize`、`live`、`generate`；以及方向性调节 `bolder`（放大无聊设计）/ `quieter`（收敛过大设计）。
- **明确的反模式清单**：不用 Arial / Inter / 系统默认字体；不在彩色背景上用灰色文字；不用纯黑纯灰（总带色调）；不把所有东西包进卡片、不嵌套卡片；不用 bounce/elastic 缓动。
- **CLI 检测器**：`npx impeccable detect src/`（目录）、`detect index.html`、`detect https://example.com`（用已装 Chrome/Chromium/Edge）、`--json`（CI 友好）、`--no-config`（原始扫描）。退出码约定：`0` 无主要发现、`2` 有主要发现、`1` 至少一个目标无法扫描。
- **61 条规则覆盖两类**：AI slop（侧边标签边框、紫色渐变、bounce 缓动、暗色辉光）与通用设计质量（行宽、局促内边距、过小触控目标、跳级标题）。
- **工程形态**：skill 本身无运行时依赖，每份副本带一个小启动器（Windows 为 `impeccable.cmd`），运行自包含二进制（首次运行下载到 `~/.impeccable/bin/`）；Node 只用于 `npx` 安装器 shim；仓库含 Rust 组件、CLI、浏览器扩展、VS Code 扩展。支持 **17 种工具**：Cursor、Claude Code、GitHub Copilot、DeepSeek Harness、Gemini CLI、Codex CLI、Grok Build、Hermes Agent、OpenCode、Pi、Kiro、Trae、Rovo Dev、Qoder、Mistral Vibe、Veto、Google Antigravity。

**值得关注的原因**
1. **"确定性规则 + 零 LLM"这个选择非常聪明**。用 LLM 检测 LLM 的设计缺陷是自相矛盾的（同样的先验会同样地视而不见）；用 61 条硬编码规则做 linter，可复现、可进 CI、退出码可门禁 —— 这是"确定性工程兜底 LLM 不确定性"在**设计领域**的又一次出现（09-17 期的结论在此得到新证据）。
2. **它把"品味"中可判定的部分剥离出来**。行宽、触控目标尺寸、标题层级、对比度是可测的；配色氛围不可测。项目明确把前者做成规则、后者留给 LLM critique —— 这种"能判定的部分不许靠模型"的分工，是所有 Agent 质量治理项目的通用模板。
3. **反模式清单本身就是可复用的 prompt 资产**。即使不装这个工具，那五条（Inter、紫蓝渐变、卡片套卡片、彩底灰字、标题上方图标块）可以直接贴进你的前端生成提示词里当负向约束。
4. 谨慎点：它锚定的是"AI 生成设计的均值缺陷"，如果你的产品定位就是极简/通用 SaaS 风格，部分规则（如禁 Inter）可能与你的品牌规范冲突，需要在 `DESIGN.md` 里显式覆盖。

---

### 8. BuilderIO/agent-native — 从底层就为 Agent 设计的全栈应用框架

**事件**
`BuilderIO/agent-native`（Builder.io 出品）今日日榜第 4，+87，总 Star 6.6k（TypeScript）。仓库特征极为显眼：**5,962 commits、786 个分支、2,703 个 tags**，最近提交 **2026-09-24**。

**核心内容**
- **定位**：让应用**本身**为 Agent 原生 —— 而非事后加一个聊天框。
- **模板矩阵**（开箱即用的应用）：analytics、assets、calendar、chat、clips（录屏/视频）、content、design、docs、forms、mail、plan、slides、starter、videos；另有 `community-templates/` 与 `registry/agent-native-app/` 注册表。
- **多 Agent 工具并存**：根目录同时存在 `.agents/`（含 skills、plugins）、`.claude/` + `.claude-plugin/`、`.codex/`、`.gemini/` —— 一个框架同时伺候四家 harness。
- **MCP Registry 集成**：`mcp-registry/`（含 server.schema.json、生成脚本），支持把 Agent-Native 应用**发布到 MCP 注册表**供 AI 客户端调用（提交 #4318）。
- **运行时与部署**：
  - 服务端从 Express 迁到 **Nitro（H3）**，采用**基于文件的路由**
  - 使用 **React Router v7** + Web 标准 `entry.server.tsx`（`renderToReadableStream`），兼容 Cloudflare Workers / Deno
  - **数据库无关**：`db/client.ts` 抽象层自动检测 —— `postgres://` → postgres.js；`libsql://` / `file:` → @libsql/client；D1 binding → Cloudflare D1（也提及 Neon / Supabase）
  - 支持 AWS Amplify 部署
  - **5 个核心存储**：settings、app-state、oauth-tokens、resources、sessions，统一走 DB 执行抽象
- **Agent 交互能力**：Tiptap 聊天编辑器支持 `@` 引用文件、`/` 调用技能；多标签聊天（MultiTabAssistantChat）；可折叠/可调宽侧边栏（状态持久化到 localStorage）；**文件变更同步从 SSE 改为 2 秒轮询 `/api/poll`**（为兼容 serverless）；审批工作流与安全栅栏；实时语音；可安装桌面应用（`packages/desktop-app`）。
- **Resources 体系**：基于 SQL 的跨模板持久化存储，面板可拖拽分文件夹。
- **设计编辑器**：对标 Figma 手感（选择框、拖拽、Shift 多选、Space 拖拽、跨屏克隆），带 handoff 与 capability 安全控制。
- **集成**：Google Workspace / Calendar（含参会人照片、RSVP 状态、重叠事件堆叠布局）、Notion 同步（含 OAuth 向导）、Apollo 人员补全、CRM（Gong / HubSpot / Pylon）、BigQuery 分析。

**值得关注的原因**
1. **"786 分支 / 2,703 tags / 5,962 commits" 这组数字本身就是结论**：这是一个**高度自动化、Agent 自己提交代码**的仓库（大量 `chore: publish branch work` 式提交）。把它当成"Agent 全自动开发的规模化样本"来读，比当成一个框架来读更有价值 —— 它展示了当 Agent 频繁开分支、发 tag 时，仓库治理会变成什么样子。
2. **2 秒轮询替代 SSE 是个务实但反直觉的取舍**。为兼容 serverless（无长连接）牺牲实时性 —— 这说明"跨运行时兼容"的代价是真实存在的，选 serverless 就要接受这类降级。
3. **"DB 无关 + 跨运行时"是给 Agent 生成代码准备的基础设施**。当代码由 Agent 写、部署环境不确定时，自动探测后端（Postgres / libSQL / D1）比让 Agent 每次猜配置更可靠。
4. **它示范了"应用如何被 Agent 使用"**：不是给人用的 UI 加个 AI 侧栏，而是把应用能力发布到 MCP Registry，让任意 AI 客户端调用。这个思路与 09-23 期 `univer` 的 "Office Harness for AI Agents" 完全同源。

---

### 9. TNT-Likely/PanWatch — 自托管 AI 盯盘，单次多 Agent 分析 $0.05

**事件**
`TNT-Likely/PanWatch`（盯盘侠）今日日榜第 17，+95，总 Star 1.6k（Python，MIT，226 commits，最近提交 2026-09-21）。定位：**自托管 AI 盯盘助手**，集成 TradingAgents（76k+ star）多 Agent 投资决策框架，覆盖 A股 / 港股 / 美股。

**核心内容**
- **多 Agent 决策链路**：持仓页点 🧠 触发 TradingAgents 流程 —— **4 类分析师**（技术 / 情绪 / 新闻 / 基本面）→ **看多看空辩论** → **风控审查** → **PM 整合决策**。3–5 分钟输出完整推理链，结论推送到 Telegram / 微信 / 钉钉。
  - **成本：默认 `deepseek-chat`，单次约 $0.05**
  - TradingAgents 框架已升级至 **0.5.0**
- **4 类定时 Agent**：盘前分析（综合隔夜美股 + 新闻 + 技术形态给今日策略）、盘中监测（RSI/KDJ/MACD 共振时推送）、盘后日报（复盘 + 资金流向 + 次日规划）、新闻速递（AI 筛选与持仓相关的财经新闻）。
- **技术分析能力**：趋势（MA 多空排列、MACD 金叉死叉、布林带突破）、动量（RSI 超买超卖、KDJ 钝化与背离）、量价（量比异动、缩量回调、放量突破）、K 线形态（锤子线、吞没、十字星）、自动计算多级支撑压力位。
- **多市场多账户**：A股/港股/美股实时行情；多券商账户独立管理 + 总资产汇总；按短线/波段/长线分别设置交易风格以影响 AI 建议。
- **通知与提醒**：Telegram / 企业微信 / 钉钉 / 飞书 / Bark / 自定义 Webhook；价格提醒支持价格、涨跌幅、成交额、量比等条件 **AND / OR 组合**，支持交易时段/全天生效、冷却时间、日触发上限、重复触发模式、到期时间（留空永不过期）、按规则指定通知渠道。
- **数据层**：12 类 Engine —— quote / kline / capital_flow / events / flash_news / fundamentals / dragon_tiger（龙虎榜）/ margin（融资融券）/ shareholders / dividend / northbound（北向资金）/ news。
- **可观测性（本期值得单独看的部分）**：
  - 内建自建体系：结构化日志 `trace_id` 贯穿、`agent_runs` 运行表、TradingAgents 节点级进度与成本，**开箱即用无需外部组件**
  - 可选挂标准 OpenTelemetry 导出，支持 Jaeger / Tempo / Langfuse 等
  - 三类 span 映射：Agent 一次运行 → root span；单次 LLM 调用 → `gen_ai` 子 span（遵循 OTel GenAI 语义约定）；TradingAgents 节点 → 子 span
  - **默认完全关闭**，不装依赖、不配 endpoint 时全程 no-op
- **部署**：Docker 一键（或 Compose），5 分钟配置；首次访问在 Web 界面设账号密码；容器内含 Playwright 系统依赖，Chromium 首次启动下载到挂载卷（默认 `/app/data/playwright`）；打 tag（如 `0.2.3`）自动构建推送 Docker 镜像 `sunxiao0721/panwatch`；移动端支持 PWA 可"添加到主屏幕"。

**值得关注的原因**
1. **它是"垂类 Agent 打包 + 人工签核 + 成本可控"模式在消费级金融场景的落地**。09-23 期 `anthropics/financial-services` 是机构级（投行/PE/研究）的具名 Agent；PanWatch 是个人级，且把**单次分析成本明确写成 $0.05** —— 这是"Agent 产品必须报单价"的正面示范（默认用 deepseek-chat 而非 GPT/Claude，成本决策很清醒）。
2. **自建可观测性 + 可选 OTel 的设计可以直接抄**。默认 no-op、零外部依赖，需要时再挂 Jaeger/Langfuse；并且遵循 OTel GenAI 语义约定命名 span。多数 Agent 项目在这一层要么完全没有、要么强绑定某个 SaaS，这种"默认关闭、标准可插"的中间态最实用。
3. **"多 Agent 辩论 + 风控审查 + PM 决策"是金融场景里少见的可解释链路**，3–5 分钟输出推理链而不只是一个买卖信号 —— 这比"AI 选股"更接近可用的形态。
4. 谨慎点：README 自称"数据私有、自托管、不经第三方"，但行情数据与 LLM 调用本身仍要出网；AI 投资建议不构成投资建议，实盘前建议先用它的模拟盘（净值曲线 + 绩效）跑一段时间。

---

### 10. cloudflare/quiche — 本期唯一的非 Agent 项目：QUIC/HTTP3 的 Rust 实现

**事件**
`cloudflare/quiche` 今日周榜第 12，**周 +707**，总 Star 12.5k（Rust，2,535 commits，仓库可追溯至 2019）。README 自述为 "savoury implementation of the QUIC transport protocol and HTTP/3"。

**核心内容**
- **多 crate 工作区**：
  - `quiche` — 核心 QUIC/HTTP3 实现，含 FFI 接口
  - `tokio-quiche` — 基于 Tokio 的异步集成
  - `h3i` — HTTP/3 互操作性测试工具
  - `qlog` / `qlog-dancer` — QUIC 日志格式支持与可视化
  - `octets`（字节处理）、`buffer-pool`、`datagram-socket`、`netlog`、`task-killswitch` — 辅助基础设施
  - `apps`、`tools`、`fuzz`
  - 依赖 **BoringSSL**（boring / boring-sys）
- **近期发布**：`h3i` **0.7.0**（2026-09-17）、`tokio-quiche` **0.20.0**（2026-09-17）、`octets` **0.3.7**（2026-09-07）
- **近期变更（按时间倒序）**：
  - `ffi: populate max_rtt in PathStats`（2026-09-21）—— 修复 FFI 函数 `quiche_conn_path_stats` 缺 setter 导致 `max_rtt` 恒为 0
  - `.opencode/skills/` 改为指向 `.codex` 的符号链接（2026-09-18）
  - `path: add PMTU path event`（2026-09-17）—— PMTU 发现改变路径包大小上限时通知应用
  - **升级 boring 至 5.2（兼容 4.19）**（2026-09-15）—— Boring 5 默认启用**后量子密钥共享**，可能把 ClientHello 拆到多个 Initial 包，相应更新了包大小与包数预期；同时为 i686 multiarch 构建准备 CFLAGS/CXXFLAGS
  - 适配新版 nightly rustfmt 的注释换行（2026-09-04）
  - 提升 serde_with 版本并上调 MSRV（原 `~3.17` 限制导致无法与要求 ≥3.18 的 crate 共用）
- 支持特性：`set_curves_list()` 配置曲线、后量子密钥共享、RPK（原始公钥）相关 API。

**值得关注的原因**
1. **它是本期唯一的非 Agent 项目，且是基础设施层的地基**。当所有榜单都被 Agent 占满时，网络协议栈仍在默默推进 —— 你自托管的所有 Agent 服务（浏览器自动化、MCP、推理 API）都跑在 HTTP/3 之上。
2. **BoringSSL 5 默认启用后量子密钥共享是个有实际影响的变化**。它会把 ClientHello 拆到多个 Initial 包，直接影响 MTU 假设、包数与重传行为 —— 任何自建 QUIC/HTTP3 服务或做性能测试的人，都要相应更新包大小预期（仓库的测试基线已经改了）。这也是"后量子迁移从可选变默认"的一个具体信号。
3. **`PMTU path event` 补上了一块长期缺口**：路径 MTU 变化时通知应用，是 QUIC 在真实网络（尤其是隧道/VPN 环境）中稳定性的关键。如果你的服务在特定网络下出现诡异卡顿，这类事件是你需要的观测点。
4. **`.opencode/skills/` 变成指向 `.codex` 的符号链接** —— 一个基础设施项目也开始维护多 harness 的技能目录，说明这股风已经吹到了非 AI 项目（它自己就参与 Agent 生态的构建，Cloudflare 另有 security-audit-skill 在榜）。

---

## 三、上期已推条目的新动态（不重复详述，仅记变化）

| 仓库 | 上期位置 | 今日数据 | 新动态 |
|---|---|---|---|
| **google/ax** | 09-23 详述第 1 | **日 +1,543（今日榜首）** | **09-20 大规模架构重构**：从"内嵌 Python harness 的单一 CLI"转型为通用编排层，拆成三个二进制 —— `ax-server`（gRPC API 提交 Task manifests）、`ax-controller`（水平扩展 reconciler，从 **Redis Streams** 消费）、`ax-task-runner`（沙箱 worker 内执行）；**Task 状态从 Kubernetes CRD 迁到 Redis**（为支撑海量短生命周期任务而不压垮 etcd）；删掉旧 Python harness、ATE client、SQL event log、skill 示例；新增 design / concepts / manifest / networking / runner / sandbox 文档与 K8s 部署 manifests。**09-23 新增外部路线图** `docs/roadmap.md`（#381，修复 #362），覆盖核心规范、actor 架构、智能体环境与治理里程碑。官方警告：稳定版发布前很可能有破坏性变更 |
| **dream-num/univer** | 09-23 详述第 7 | 日 +1,142，总 16.5k | 产品线显著扩张（已超出"Office SDK"范畴）：**Univer Workspace**（开源可自托管工作空间，人与 Agent 共同创建/协作/审阅）、**Univer Office for DeepSeek Harness**（内容连接、校验、隔离 worktree）、**Univer CLI**（本地命令行工作空间，创建/编辑/检查/交付 Office 内容）、**Univer Office for WorkBuddy**（本地 Office 集成，含 MCP 预览与草稿审阅，开发预览版）、**Univer Office for OpenClaw**、**univer-mcp**（自然语言驱动 Univer Sheets）；PDF 标注 coming soon；AI Agent 工作流三能力明确为 programmatic editing / output verification（截图 + 布局诊断）/ worktree collaboration。运行时要求：headless 需 Node ≥18.17.0，monorepo 开发需 ≥22.18 |
| **browser-use/video-use** | 09-23 详述第 8 | 日 +746 | **09-24 新提交**：字幕改为**语义分块**（原先固定 2 词配对，会切断停顿产生 "DOES IS"、出现 0.18s 闪现字幕；现在按标点与 ≥0.3s 停顿断句，过短字幕最多扩到 3 词）；字幕路径解析失败从"打印警告后无字幕渲染"改为"先试当前目录，再报错退出"；SKILL.md 增加音乐/音效规则、分段落响度检查、自评中的 **critic 子代理**、字体加载断言、"show the edit" 作为完整示例 |
| **anthropics/financial-services** | 09-23 详述第 3 | 日 +664，周 +1,895 | 财富管理方向连续调整：09-11 移除 wealth-management 插件（#349）→ 09-14 上线 **Claude for Financial Advisors**（#350）并移除重复市场条目（#351）→ **09-21 删除 claude-for-financial-advisors 目录（#354）**；新增合作伙伴插件 **LSEG**（债券相对价值、掉期曲线、FX carry、期权波动率、宏观利率监控）与 **S&P Global**（基于 Capital IQ 的简报、财报预览、融资摘要）；连接器共 **11 个**（Daloopa、Morningstar、S&P Global、FactSet、Moody's、MT Newswires、Aiera、LSEG、PitchBook、Chronograph、Egnyte、Box）；09-18 安全修复：build-manifest 把凭证从 query string 移到 URL fragment |
| **LibreChat** | 09-23 详述第 10（当时为 `danny-avila/LibreChat`） | 周 +949，总 44.8k | **09-24 仓库迁移**：`danny-avila/LibreChat` → **`LibreChat-AI/LibreChat`**（#16005），同步更新 package repository、bugs URL、文档链接、模板与注释，以及镜像引用（compose 文件、deployed-update、Helm values、renovate hints），连带已迁至该组织的 rag-api 仓库及其镜像；sponsor 链接与 star-history 图保持不变。另：09-19 修复 Langfuse 媒体上传类型（文本/JSON 媒体上传、附件 MIME 类型）。历史重要功能：插件命令钩子真实执行（#14755，含进程树回收、Windows/POSIX 差异、默认关闭的 `DEPLOYMENT_PLUGIN_HOOKS`） |
| **cloudflare/security-audit-skill** | 09-17 / 09-18 / 09-23 三次提及 | **周榜第 1，周 +15,280，总 21.0k** | 累计涨幅：09-17 首推时 +927 → 09-18 +3,607 → 09-23 周 +15,381 → 今日周 +15,280（周窗口滚动后基本持平，增长进入平台期） |
| **alibaba/open-code-review** | 09-17 详述第 1 | 周榜第 2，周 +9,833，总 40.3k | 周涨幅较 09-23 的 +12,590 回落约 22% |
| 其他仍在榜的上期条目 | — | — | `agent-substrate/substrate` 日 +558；`superdesigndev/treg` 日 +506（周 +1,067）；`mvt-project/mvt` 日 +543；`anthropics/claude-code` 周 +2,762；`Tencent/WeKnora` 周 +4,522；`affaan-m/ECC` 周 +6,695；`addyosmani/agent-skills` 周 +3,867；`TencentCloud/Octop` 周 +1,877；`cline/cline` 周 +1,177；`JustVugg/colibri` 周 +2,739 |
| **仍未见踪影** | — | — | 09-17 首推的 `NationalSecurityAgency/ghidra`、`alphaXiv/OpenResearch`、`abue-ammar/tinycast` 已连续 7 天不在 daily 与 weekly 榜上（09-23 已标记退榜，本期确认） |

---

## 四、其他趋势速览（未展开）

| 仓库 | 语言 | 数据 | 一句话 |
|---|---|---|---|
| Open-Dev-Society/OpenStock | TypeScript | 日 +344，**周 +4,356**，总 18.9k | 昂贵行情平台的开源替代：实时价格、个性化提醒、公司洞察，"公开构建、永远免费"。周榜增速第 3，值得下期展开 |
| harry7557558/spirula-studio | C++ | 日 +69，总 795 | 跨厂商 **3D Gaussian Splatting** 训练器：video → splat → mesh，支持 Vulkan 或 CUDA。本期唯二的非 Agent 项目 |
| pytorch/pytorch | Python | 周 +196，总 103.2k | 张量与动态神经网络，GPU 加速。基础盘，长期在榜 |
| cilium/cilium | Go | 周 +447，总 25.5k | 基于 eBPF 的网络、安全与可观测性方案。09-18 期已作未展开提及 |
| davila7 之外的同类 | — | — | `HKUDS/CLI-Anything` 的 CLI-Hub（`pip install cli-anything-hub`）与 `strands-cli` 都提供终端入口，说明"Agent 的 CLI 层"正在成为独立竞争面 |

---

## 五、当日主线判断

1. **"把不可协商的约束写进流程与文件"成为 Agent 质量治理的统一答案。**
   本期三条最值得看的项目恰好是同一件事的三个切面：`superpowers` 锁**开发流程**（TDD 强制 RED-GREEN-REFACTOR，会删除测试前写的代码；code review 阻塞关键问题）、`OpenSpec` 锁**需求边界**（spec → change → task → verify → archive，verify 要区分 ADDED/MODIFIED/REMOVED/RENAMED）、`impeccable` 锁**输出质量**（61 条确定性规则 + 退出码可进 CI）。共同点是：约束落在**流程节点与文件**上，不落在提示词里。这与 09-17 期"可靠性靠确定性工程兜底"的结论完全一致，且本期给出了设计领域的新证据。

2. **上下文经济从技巧变成独立工程学科。**
   `codebase-memory-mcp` 用图查询替代 grep 循环，token 省 **99.2%**（3,400 vs 412,000）、Cypher 查询 **<1 ms**；`video-use` 用 12KB 转录文本 + 按需 PNG 替代 45M tokens 的帧堆；`CLI-Anything` 强制每个命令内建 `--json`。三个完全不同的领域，同一个动作：**给 Agent 更少但更结构化的输入**。这已经是可迁移的方法论，不只是优化技巧。

3. **Agent 基础设施的四层分工在本期彻底清晰。**
   - 调度/沙箱层：`google/ax`（重构为 ax-server / ax-controller / ax-task-runner，状态迁 Redis）+ `agent-substrate/substrate`
   - 进程内循环层：`strands-agents/harness-sdk`（`create_harness()` 一行组装，无托管控制平面，跑在你自己的进程里）
   - 方法论层：`superpowers`（7 阶段 + 16 种 harness 适配）+ `OpenSpec`（SDD）
   - 输出质量层：`impeccable`（61 条设计规则）
   值得注意的立场：Strands 明确选择"无托管控制平面"，AX 选择"K8s 化 + Redis"。**两种哲学并存**，但都默认可自托管。

4. **"Agent-native" 从形容词变成了工程目标，并且出现了两条实现路径。**
   - **改造存量软件**：`CLI-Anything` 用 7 阶段流水线自动为 GIMP / Blender / LibreOffice / QGIS 等 18 个 GUI 软件生成 CLI，2,461 个测试，原则是"零妥协依赖、后端缺失测试失败"
   - **新建原生应用**：`BuilderIO/agent-native` 提供 15+ 模板、`@` 文件引用 + `/` 技能、审批工作流、MCP Registry 发布
   两条路径的共同前提：**像素级操作（截图/点击/RPA）不可靠，结构化接口才可靠** —— 这个判断已连续四期出现，可以当结论使用。

5. **供应链与安全修复继续以"具体 CVE 级细节"出现在榜单上。**
   `claude-code-templates` 的 GHSA-79wm-x847-7cvg：`0.0.0.0` 绑定 + CORS 通配 + 无鉴权 + `shell: true`，可通过两个 API 端点执行任意 OS 命令；修复四件套（去 shell 层、白名单参数、绑回环、限 CORS）可直接作为自查清单。同时 `npm install --ignore-scripts` 进入 CI（继 09-18 期 n8n 的 SBOM/OpenVEX 之后第二次出现）。非 AI 侧的 `quiche` 也在修 FFI 字段缺失（`max_rtt` 恒为 0）——**接口字段静默缺失**是另一类高频隐患。

6. **本地优先/自托管已从"选项"变成默认假设。**
   `codebase-memory-mcp`（纯 C 单二进制、零依赖、无 API Key）、`PanWatch`（Docker 一键、数据私有、单次分析 $0.05）、`Strands`（进程内、无托管控制平面）、`univer`（可自托管工作空间）。同时 `PanWatch` 的"自建可观测性默认 no-op + 可选标准 OTel 导出"是一个可直接复用的中间态设计。

7. **非 Agent 项目仍能上榜，但数量稀少且集中在"地基"与"垂直工具"。**
   本期只有 `cloudflare/quiche`（QUIC/HTTP3，BoringSSL 5 默认启用后量子密钥共享、新增 PMTU 路径事件）、`harry7557558/spirula-studio`（3D Gaussian Splatting）、`pytorch/pytorch`。榜单的 Agent 集中度已达前三期最高。

8. **值得警惕的一点**：本期总 Star 最高的两个仓库（`superpowers` 290.8k、`impeccable` 70.5k）都属于"方法论 / 规则集"型项目，star 增长主要靠传播而非使用。判断价值的标准应该是**它是否真的改变了你的 Agent 行为**，而不是 star 数。建议各拿一个中等项目实测后再决定是否长期保留。
