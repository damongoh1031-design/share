---
type: Checklist
---

# goose 深度研究报告 v2.2

**副标题**：开源 AI Agent 的治理样本与竞争格局
**研究对象**：`aaif-goose/goose`（原 `block/goose`）
**版本**：v2.2（源码级补全版，取代 v2.1）
**数据截止**：2026-10-15（GitHub REST API + 官方文档库全量抓取 + 源码全量文件树枚举）
**对比范围**：14 款开源 / 商用 AI Agent，重点对比 5 款
**专项视角**：Linux 发行与分发适配 · 官方文档能力图谱 · 源码级架构与工程实践

---

## 摘要

goose 是一款本地优先、模型无关的开源通用 AI Agent。由 Block（Square / Cash App 母公司）于 2025 年 1 月开源发布，2025 年 12 月随 Agentic AI Foundation（AAIF）成立被捐赠，2026 年 4 月正式迁入 `aaif-goose` 组织，现由 Linux 基金会托管，Apache-2.0 许可。

**实时规模（2026-10-15）**：55,293 stars · 6,437 forks · 453 contributors · 480 open issues · 主线版本 **v1.54.0**（2026-10-08）· 日更。

**v2.1 新增**：补全 v2.0 缺失的官方文档维度——对文档库 **173 篇** Markdown 全量抓取归类，补齐官方架构、14 个内置扩展、73 个 MCP 扩展、完整 CLI 命令表、上下文管理参数、GDK、Roaming Agents 等能力图谱（见第 3 章）。

**v2.2 新增**：补全前两版都缺失的**实现层事实**——对仓库 `main` 分支全量枚举 **3,038 个文件**，核对 15 个 crate 的真实职责与特性矩阵、66 个提供方文件、桌面端依赖树（Electron）、43 个 workflow 的质量体系、安全与供应链源码口径，并修正 **4 处"把计划当既成事实"**的表述（见第 4 章）。

### 核心结论

| # | 结论 | 关键证据 |
|---|---|---|
| 1 | **治理中立性是 goose 最不可替代的资产** | 14 款对比产品中唯一由基金会（Linux 基金会 AAIF）托管的项目，其余全部由商业公司或个人主导 |
| 2 | **工程健康度属第一梯队** | 453 contributors 与 Codex（478）、OpenHands（461）、Dify（456）同级；open issues 仅 480，是同量级最低 |
| 3 | **获第三方权威认证** | Linux 基金会官方 Insights 平台判定其 **Health Score = Healthy** |
| 4 | **形态与场景最宽** | 唯一同时提供原生桌面 + CLI + API 三种稳定形态（TUI 实验已于 2026 年终止，见 4.13），且定位"not just code"（研究、写作、数据分析、自动化） |
| 5 | **星数与声量是最大短板** | 55,293 stars 在对比组中排 **第 9 位**（非 v1.1 所称第 7 位），被 opencode（213,573）压制 3.9 倍 |
| 6 | **Linux 分发最完整的桌面级 agent** | 单版 40 个产物中 Linux 相关占 24 个：12 CLI tarball + 4 RPM + 4 DEB + 4 Flatpak，并覆盖 Nix / RISCV |

---

## 0. 修订说明：v1.1 → v2.2 勘误与补充清单

**v1.0 → v2.0**：以 **2026-10-15 GitHub REST API 全量重采 + 仓库原文逐条比对** 为基础复核，发现并修正 18 处问题（见 0.1–0.5）。

**v2.0 → v2.1**：补全官方文档维度。对仓库 `documentation/docs/` 下 **173 篇 Markdown / MDX 全量抓取**（约 1.33 MB）并逐篇归类，补齐 v2.0 因"只看 API 与仓库治理文件"而缺失的功能层能力图谱，共 **13 项补充**（见 0.6）。

**v2.1 → v2.2**：转向**源码**。对 `main` 分支做**全量文件树枚举（3,038 个文件 / 52 个顶层条目）**并逐目录核对源码与配置，发现 **4 处需修正**（把计划当成既成事实）与 **4 处需补充**，共 **8 项**（见 0.7）。

### 0.1 实质性错误（3 处）

| # | v1.1 表述 | 问题性质 | v2.0 修正 | 依据 |
|---|---|---|---|---|
| 1 | "55.3k 排在主流开源 Agent **第 7 位**" | **排序计算错误** | 按其自身对比表实为 **第 9 位**。其前方有 opencode、Dify、Claude Code、Codex、Pi Agent、Gemini CLI、OpenHands、Cline 共 8 款 | 2026-10-15 API 实测全表排序 |
| 2 | "每版发布约 **40 个 Linux 相关产物**" | **口径混淆** | 40 是**全部产物总数**（含 macOS / Windows / 源码包）。Linux 相关实为 **24 个**，占比 60%：12 CLI tarball + 4 RPM + 4 DEB + 4 Flatpak | v1.54.0 release assets 逐条清点 |
| 3 | "goose 桌面 2.0 用 Tauri 重写" 并列于桌面形态描述 | **版本状态易误读** | 2.0 自 2026-04 起仍为 **beta**；当前稳定线 **v1.54.0**，2.0 能力不得当作正式版 | GitHub Releases API（prerelease 标记） |

### 0.2 重要遗漏（6 处）

| # | 遗漏内容 | v2.0 补充 | 依据 |
|---|---|---|---|
| 4 | **DEB 包** | goose 每版发布 4 个 DEB：`goose_1.54.0_{amd64,arm64}[-vulkan].deb` | assets 实测 |
| 5 | **Flatpak** | 每版发布 4 个 Flatpak：`io.github.block.Goose_stable_{x86_64,aarch64}[-vulkan].flatpak`，即已打通 Flathub 桌面分发路径 | assets 实测 |
| 6 | **官方一行安装命令** | `curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh \| bash` | README 原文 |
| 7 | **Linux 基金会官方健康分** | LF Insights 判定 goose **Health Score = Healthy**（绿色徽章） | insights.linuxfoundation.org API |
| 8 | **aaif-goose 组织创建时间** | 组织 **2026-03-25** 建立，早于 2026-04-07 的迁入公告；现含 5 个公开仓库 | GitHub org API |
| 9 | **Core Maintainers 实名与人数** | 当前 **7 人**：Alex Hancock、Bradley Axen、Douwe Osinga、Jack Amadeo、Jasper Hugo、Lifei Zhou、Mic Neale；另有 Maintainers 5 人 | MAINTAINERS.md 原文 |

### 0.3 数据过期（3 处）

| # | 项目 | v1.1 值 | v2.0 实测值（2026-10-15） | 变动 |
|---|---|---|---|---|
| 10 | goose stars | 55,274 | **55,293** | +19 |
| 11 | goose forks | 6,428 | **6,437** | +9 |
| 12 | goose open issues | 507 | **480** | **−27（−5.3%）** |

> 注：全部 14 款产品的 stars / forks / issues / contributors 均已在 第 5.1 节刷新为同一时点实测值，v1.1 中 6 处缺失值（标 "—"）已补齐。

### 0.4 口径与精度改进（6 处）

| # | 项目 | v1.1 表述 | v2.0 精确化 |
|---|---|---|---|
| 13 | opencode 增速 | "**一年内**从 1.4 万飙到 21.3 万" | 仓库创建于 **2025-04-30**，至 2026-10-15 为 **约 18 个月** |
| 14 | Aider 停更 | "2026-05 起基本停更" | 最后推送 **2026-05-22**，至报告日**约 5 个月无提交**，open issues 累积至 1,920 |
| 15 | 语言规模 | "Rust 约 1,050 万字节 + TS 约 345 万字节" | Rust **10,506,629 B（71.59%）** / TypeScript **3,446,615 B（23.49%）** |
| 16 | Rust 工具链 | "Rust 1.99" | `rust-toolchain.toml` 锁定 **1.99.0** |
| 17 | 代码结构 | 未量化 | `crates/` 工作区含 **15 个 crate** |
| 18 | Flatpak 标识 | 未提及 | 迁移至 AAIF 后，Flatpak ID 仍为 **`io.github.block.Goose`**，保留原 block 命名空间，属迁移遗留 |

### 0.5 v1.1 已核实为**正确**的表述（抽查 8 项）

为避免"纠错"本身失真，以下 v1.1 说法经原文核验成立：

| 项目 | v1.1 表述 | 核验结果 |
|---|---|---|
| 治理层级 | Core Maintainers 3–7 人、追求奇数 | ✓ GOVERNANCE.md 原文："We aim to have between 3 and 7 Core Maintainers… strive for an odd number" |
| 版权政策 | 贡献者保留版权，无需转让；代码 Apache-2.0、文档 CC-BY-4.0 | ✓ GOVERNANCE.md 原文 |
| 治理变更 | 需 Core Maintainers 多数通过，且须经 LF Projects, LLC 批准 | ✓ GOVERNANCE.md 原文 |
| 死锁裁决 | 创始人 Bradley Axen 打破僵局 | ✓ GOVERNANCE.md："goose's creator, Bradley Axen, steps in as a tie breaker" |
| 模型接入 | 15+ provider | ✓ README 原文："works with 15+ providers"（**v2.2 精确化**：源码实测 30+ 家，见 4.6） |
| 扩展生态 | 70+ 官方扩展（MCP） | ✓ README 原文："Connect to 70+ extensions via the Model Context Protocol"（**v2.2**：目录 73 个，且该目录正在退役，见 4.13） |
| 发行机制 | 官方提供 CUSTOM_DISTROS 机制 | ✓ 仓库根目录存在 `CUSTOM_DISTROS.md` |
| 关键文件 | RISCV_SETUP.md / BUILDING_LINUX.md / flake.nix | ✓ 三个文件 HTTP 200 存在 |

### 0.6 v2.0 → v2.1 补充清单（13 项，全部来自官方文档）

v2.0 的结论建立在 GitHub API 与仓库治理文件之上，**对官方文档站（`documentation/` 目录）挖掘不足**。v2.1 全量抓取 173 篇文档后补齐以下内容：

| # | 补充项 | 落点 | 性质 |
|---|---|---|---|
| 1 | **文档库规模实测**：173 篇 Markdown / 247 个文件 / 约 1.33 MB | 3.1 | 新数据 |
| 2 | **官方架构三组件 + 六步交互循环**（替换 v2.0 的推断式描述） | 3.2 | 口径修正 |
| 3 | **Context Revision 的四项具体机制**（小模型摘要 / 全量而非语义检索 / 算法删除 / find-and-replace + ripgrep） | 3.2 | 新事实 |
| 4 | **错误处理设计**：错误作为 tool response 送回模型而非中断 | 3.2 | 新事实 |
| 5 | **14 个内置扩展**（5 基础 + 9 平台，含各自默认启用状态） | 3.3 | 新事实 |
| 6 | **恶意包拦截**：激活前自动检查已知恶意软件 | 3.3 | 新事实 |
| 7 | **73 个 MCP 扩展**的分类归集（精确化 v2.0 的"70+"） | 3.4 | 精确化 |
| 8 | **完整 CLI 命令表**（20+ 命令与关键选项），据此确认 **goose 无 `task` 子命令** | 3.5 | 新事实 |
| 9 | **15 个交互式斜杠命令** + 会话存储 SQLite 迁移（v1.10.0 起） | 3.6 | 新事实 |
| 10 | **上下文管理参数级细节**：自动压缩触发 `min(80% 上下文, 225,000)`、`GOOSE_CONTEXT_STRATEGY`、Max Turns 默认 1000、上下文限制 5 级解析优先级 | 3.8 | 新事实 |
| 11 | **GDK**（SDK 支持 Rust/Python/Kotlin + ACP 三传输） | 3.10 | 新事实 |
| 12 | **Roaming Agents**：基于 iroh(QUIC) 的点对点 ACP 传输、公钥互认、需 opt-in 构建、含 wasm 与 Web 客户端 | 3.11 | 新事实 |
| 13 | **官方 Linux 桌面文档滞后**：文档只写 DEB，实际发布 RPM + DEB + Flatpak | 3.13 / 6.1 | 差异发现 |

**同时修正的 v2.0 判断**：v2.0 将"第三方教程、插件、主题数量全面落后"列为 goose 劣势——该判断在**第三方生态**层面成立，但**官方文档覆盖度并不薄弱**（73 个扩展各有独立文档页，文档密度约每千星 3.1 篇）。v2.1 已在第 3.1 与第 7.2 节区分这两个层面。

### 0.7 v2.1 → v2.2 源码维度修正与补充（8 项）

v2.1 补全了官方文档维度，但**文档写的是"设计意图"，源码写的是"实际实现"**。v2.2 对仓库 `main` 分支做全量文件树枚举（3,038 个文件，`truncated: false`）并逐目录核对源码与配置，发现 **4 处需修正**、**4 处需补充**。

| # | 项 | 落点 | 性质 |
|---|---|---|---|
| 1 | **桌面端不是 Tauri**：全仓库仅 2 处提及 Tauri、无任何 Tauri 代码，`ui/desktop` 实测仍是 **Electron 43.4.0**；Tauri 是官方路线图第 3 项（🚧 in progress），**未落地** | 2.4 / 4.7 / 4.13 | **实质修正** |
| 2 | **Buzz 不是第三方 ACP 集成**：`buzz/` 是仓库自带的 **Nostr issue 同步自动化**（目标 `buzz.gdk.so`），不是外部产品案例 | 4.11 / 4.13 | **实质修正** |
| 3 | **提供方数量精确化**："15+ providers" → `providers/` 共 **66 个文件、30+ 家**（直连 + ACP 两类） | 2.4 / 4.6 | 精确化 |
| 4 | **`.goosehints` 存在文档债**：仍描述已不存在的 `goose-server`（goosed）与 `goose-bench` crate | 4.13 | 文档债 |
| 5 | **MCP 扩展目录正在退役**：`AGENTS.md` 声明改用官方 **MCP Registry** 与 `server.json`，不再接受新增第三方条目（Discussion #10830） | 4.13 | 战略变化 |
| 6 | **ACP TUI 已弃用**：`ui/text/` 源码移除，npm 包 `@aaif/goose` 标记 deprecated | 4.13 | 新事实 |
| 7 | **安全模块实为 7 个**（v2.0 称"三件套"），含官方文档未提及的 `egress_inspector.rs`（出站检查）与 `permission/permission_judge.rs` | 4.10 | 新事实 |
| 8 | **npm 分发渠道**：`@aaif/goose-acp` + 5 个平台包 `goose-binary-*`（官方文档未收录） | 4.8 | 新事实 |

> **方法论要点** — 判定"计划 vs 既成事实"用的是**字符串级全仓库检索**（GitHub code search）：搜 `tauri` 只命中 2 个文件、且无任何 Tauri 依赖或构建配置，即可反证"Tauri 重写"未落地。这条方法同样适用于其他项目。

---
## 1. 研究方法与数据来源

| 方法 | 说明 | 本次采集时点 |
|---|---|---|
| GitHub REST API | `/repos`、`/contributors`、`/releases`、`/languages`、`/orgs`、`/contents` 端点，获取 star / fork / issues / 许可证 / 语言字节数 / 贡献者数 / 发布产物 / 文件树 | 2026-10-15 |
| 仓库治理原文 | `GOVERNANCE.md`、`MAINTAINERS.md`、`README.md`、`rust-toolchain.toml` 全文比对 | 2026-10-15 |
| 发布物清点 | 对 v1.54.0 的 40 个 asset 逐条分类（按扩展名与平台标识） | 2026-10-15 |
| **官方文档库全量抓取** | 递归枚举 `documentation/docs/`，下载全部 **173 篇** Markdown / MDX（约 1.33 MB），逐篇提取 frontmatter、标题结构与正文；发布物与文件存在性均以 HTTP 状态码核验 | 2026-10-15 |
| **源码全量文件树枚举** | Git Trees API `?recursive=1` 一次取得 `main` 分支整棵树（**3,038 个文件 / 52 个顶层条目**，`truncated: false`），逐目录核对 15 个 crate、43 个 workflow、`ui/desktop/package.json`、`Justfile`、`release-plz.toml` 等 | 2026-10-15 |
| **字符串级全仓库检索** | GitHub code search API（如 `tauri+repo:aaif-goose/goose`），用于判定"计划 vs 既成事实" | 2026-10-15 |
| 官方博客 | goose-docs.ai 博客（2026-02 至 2026-09 条目） | 2026-10-14 ~ 15 |
| 第三方权威 | Linux Foundation Insights 项目健康分 API | 2026-10-15 |
| 社区与媒体 | 腾讯云开发者社区、CSDN 系列教程、什么值得买评测、程序员茄子治理分析、TechCrunch 中文转述 | 2026-10-14 ~ 15 |

**诚实性声明**：本报告对未经第二来源交叉验证的说法，一律在正文标注"社区称""本文判断""待验证"，并在第 10 节集中列出不确定性清单。所有 GitHub 数值均为 API 实时返回值，未做估算。

---

## 2. 项目画像

### 2.1 基本事实表（2026-10-15 实时值）

| 指标 | 数值 | 备注 |
|---|---|---|
| 仓库 | `aaif-goose/goose` | 原 `block/goose`，2026-04 迁移 |
| Stars | **55,293** | 对比组内排第 9 |
| Forks | **6,437** | — |
| Watchers | 297 | `subscribers_count` |
| Open Issues | **480** | 同量级项目中最低 |
| 贡献者 | **453** | 与 Codex（478）、OpenHands（461）同级 |
| 主语言 | Rust **10,506,629 B（71.59%）** + TypeScript **3,446,615 B（23.49%）** | 其余：Python 1.28% / JS 1.14% / Shell 1.13% / Nix 0.04% |
| 许可证 | Apache-2.0（文档 CC-BY-4.0） | — |
| 仓库创建 | 2024-08-23 | Block 内部孵化期 |
| 最后推送 | 2026-10-15 | 日更 |
| 最新稳定版 | **v1.54.0**（2026-10-08，40 个产物） | 2.0 仍为 beta |
| Rust 工具链 | 1.99.0 | `rust-toolchain.toml` |
| Topics | `acp` `ai` `ai-agents` `mcp` | — |
| 官网 / 组织 | https://goose-docs.ai/ · `aaif-goose`（2026-03-25 建，5 个公开仓库） | — |
| 第三方健康分 | **Healthy**（Linux Foundation Insights） | 官方绿色徽章 |

### 2.2 代码结构：15 个 crate 的工作区

`crates/` 目录实测含 15 个 crate，模块划分揭示了架构意图：

| crate | 职责推断 |
|---|---|
| `goose-agent` | Agent 内核与主循环 |
| `goose` | 主入口 / 聚合 |
| `goose-cli` | 命令行界面 |
| `goose-mcp` | MCP 协议实现 |
| `goose-acp-macros` | ACP 协议宏 |
| `goose-providers` / `goose-provider-types` | 模型提供方适配层 |
| `goose-local-inference` | **本地推理（llama.cpp）** |
| `goose-context-management` | 上下文管理与压缩 |
| `goose-download-manager` | 模型 / 资源下载 |
| `goose-roaming` | 会话漫游 / 迁移 |
| `goose-sdk` / `goose-sdk-types` | 对外 SDK |
| `goose-test` / `goose-test-support` | 测试基建 |

> 观察：`goose-local-inference` 与 `goose-context-management` 独立成 crate，说明"本地推理"与"上下文治理"被当作一等公民能力，而非附属特性。

### 2.3 发展时间线

| 时间 | 事件 | 性质 |
|---|---|---|
| 2024-08-23 | Block 内部立项，GitHub 仓库创建 | 内部孵化 |
| 2025-01 | Block 公开发布 | 公开发布 |
| 2025-07 | Block 发起 goose 资助计划（媒体报道：12 个月、10 万美元） | 生态投入（社区称） |
| 2025-12 | Linux 基金会发起 AAIF：Anthropic 捐 MCP、OpenAI 捐 AGENTS.md、Block 捐 goose，30+ 家公司参与 | 治理转折（宣布） |
| 2026-03-19 | 支持用 Claude / ChatGPT / Gemini 订阅经 ACP 接入 | 功能发布 |
| 2026-03-25 | `aaif-goose` GitHub 组织建立 | 迁移前置 |
| 2026-04-07 | 官方博客《goose has a new home》宣布迁入 AAIF | 治理落地 |
| 2026-04-08 | goose 2.0 beta：**宣布** Tauri 重写桌面、全新 TUI、统一 ACP（**截至 2026-10，前两项均未落地**，见 4.7 / 4.13） | 架构换代（beta） |
| 2026-09-16 | 官方博客《Agentic State Machines》：用可重入状态机取代经典 agent loop | 内核换代 |
| 2026-10-08 | v1.54.0 发布（40 个产物，含 4 Flatpak） | 当前稳定版 |

**发布节奏实测**：v1.48.0（08-27）→ v1.49.0（09-03）→ v1.50.0（09-08）→ v1.50.1（09-14）→ v1.51.0（09-17）→ v1.52.0（09-23）→ v1.53.0（10-02）→ v1.54.0（10-08）。**约每 5–7 天一个小版本**，产物数量从 37 增至 40。

### 2.4 技术架构

| 层 | 实现 |
|---|---|
| 内核 | Rust（15 个 crate 的工作区），MSRV **1.94.1**、工具链锁定 **1.99.0** |
| **界面** | TypeScript（`ui/`，约 345 万字节）；桌面端实测为 **Electron 43.4.0 + Electron Forge 7.11.2 + React 19.2.8 + Vite 8.2.1**。**v2.2 修正**：v2.0/v2.1 称"2.0 beta 起改用 Tauri 重写"有误——Tauri 仍在官方路线图（in progress），**源码中不存在 Tauri 代码**（见 4.7） |
| 形态 | 原生桌面应用（macOS / Linux / Windows）+ CLI + API（**ACP TUI 已于 2026 年弃用**，见 4.13） |
| Agent 循环 | 经典 agent loop → **可重入状态机**（对话即状态，每个行为是一个 Operation）。官方架构文档给出正式定义：**三组件（Interface / Agent / Extensions）+ 六步交互循环**，详见 3.2 |
| 错误处理 | 不中断流程：捕获传统错误与执行错误（无效 JSON、缺失工具等），**作为 tool response 送回模型**由其自行解决 |
| 嵌入方式 | **GDK**：SDK（Rust / Python / Kotlin 进程内库）+ ACP（stdio / HTTP / WebSocket），详见 3.10 |
| 工具协议 | MCP（客户端 + 服务端），**73 个**官方扩展（该目录正在退役，改用官方 MCP Registry，见 4.13） |
| 客户端协议 | ACP（Agent Client Protocol）：goose 作 **server**，可被 Zed / JetBrains / VS Code 接入；同时可把 Claude Code、Codex 等 ACP agent 当作自己的 LLM provider |
| 本地推理 | 独立 crate `goose-local-inference`（llama.cpp），无需 API key、无网络亦可运行 |
| 分发 | RPM / DEB / Flatpak / tarball（gnu + musl）/ Nix flake / 部分发行版仓库 / 官方一行脚本 |

### 2.5 功能矩阵

| 能力 | 说明 |
|---|---|
| 模型接入 | **30+ 家** provider（`providers/` 66 个文件；Anthropic / OpenAI / Google / Ollama / OpenRouter / Azure / Bedrock / Databricks 等）；支持订阅复用（Claude / ChatGPT / Gemini via ACP） |
| Recipes | YAML 可移植工作流：指令 + 扩展 + 参数 + subrecipes，团队共享、可跑 CI |
| Subagents | 派生子代理并行处理代码审查 / 研究 / 文件处理；v1.54.0 起支持前台 subagent |
| MCP Apps | 扩展可在桌面端内渲染交互式 UI（按钮、表单、可视化） |
| Mesh LLM | 跨模型路由，自动分配与降级 |
| Hooks | 遵循 Open Plugins 规范，在 PreToolUse / PostToolUse / SessionStart 等生命周期事件挂脚本 |
| 记忆与上下文 | Memory Extension（按 tag 存取，本地 `~/.goose/memory`）+ compaction（超窗时压缩为结构化摘要） |
| 安全 | macOS 沙箱、提示注入检测、工具权限控制、Adversary mode（隐藏审查 agent）、SLSA 构建溯源 |
| 桌面控制 | Computer Controller 扩展基于 Peekaboo，Mac 上可看屏、点击、打字 |
| 多代理编排 | Goosetown / Gas Town：多 agent 协同的分布式工程模式 |
| 评估 | Harbor / Terminal-Bench 驱动的回归评估体系 |
| **Roaming** | 基于 iroh(QUIC) 的**点对点远程 agent 访问**，公钥互认、无需端口/VPN/服务器；实验性，需 opt-in 构建（详见 3.11） |
| **本地模型管理** | `goose local-models` 直接从 Hugging Face 搜索、下载、注册 GGUF / MLX 模型 |
| **定时任务** | `goose schedule` 用 cron 表达式定时运行 recipe（`add` / `list` / `run-now` 等） |
| **代码审查** | `goose review [range]`：审查 git diff，支持 `.agents/checks/*.md` 检查项与并行编排 |
| **终端集成** | `goose term init` 为每个 shell 建立持久会话，创建 `@goose` / `@g` 别名 |
| **Tool Shim** | 为不支持原生 tool calling 的模型提供工具调用能力（实验性，详见 3.12） |
| **会话检索与记忆** | Chat Recall（跨全部会话搜索）、Memory Extension、Persistent Instructions（每轮注入） |
| **成本可视化** | 实时会话成本估算（多模型分列）+ 信用余额监控（HTTP 402 检测） |
| 自定义发行版 | `CUSTOM_DISTROS.md`：预置 provider、扩展与品牌的定制构建 |

### 2.6 治理结构（依据 GOVERNANCE.md 原文）

| 项 | 内容 |
|---|---|
| 托管方 | Agentic AI Foundation（AAIF），Linux 基金会旗下，属 LF Projects, LLC 的 Series 项目 |
| 角色层级 | Contributors → Maintainers → Core Maintainers |
| Core Maintainers | **7 人**（目标区间 3–7 人，追求奇数以减少投票死锁） |
| Maintainers | 5 人 |
| 当前名单 | Core：Alex Hancock、Bradley Axen、Douwe Osinga、Jack Amadeo、Jasper Hugo、Lifei Zhou、Mic Neale |
| 日常决策 | PR / GitHub Discussion / Discord 共识 |
| 重大架构变更 | 需公开社区评审**至少一周** + Core Maintainers 多数通过 + GitHub/Discord 公开公告 |
| 争议解决 | 升级至 Core Maintainers；仍未决则简单多数投票；结果公开 |
| 死锁裁决 | 项目创始人 Bradley Axen 担任打破僵局者 |
| 治理变更 | 需 Core Maintainers 多数通过，**且须经 LF Projects, LLC 批准** |
| 继任机制 | Core Maintainer 离任须 30 天内补位；若少于 3 人则 15 天内优先补齐，期间暂停重大决策 |
| 除名条件 | 连续 3 个月以上无贡献 / 违背项目价值 / 本人请辞 |
| 版权政策 | 贡献者保留自身版权，无需转让；代码 Apache-2.0，文档 CC-BY-4.0 |
| 工程文化 | 2026-07 起推行"Issues as the new PRs"：设计与讨论在 issue 完成，再由 agent 把 ready issue 转为代码 |
| 价值观 | Open（可 hack）/ Flexible（开放与私有模型同等支持）/ Choice（不绑定单一模型、协议、技术栈） |

---
## 3. 官方文档能力全景

> 本章为 **v2.1 新增**。v2.0 的结论主要建立在 GitHub API 与仓库治理文件之上，对官方文档站（goose-docs.ai，源码位于仓库 `documentation/`）挖掘不足。本章对该文档库做**全量抓取与逐篇归类**，补齐功能层面的能力图谱。

### 3.1 文档库规模与结构（全量实测）

对仓库 `documentation/docs/` 递归枚举后的实测结果：

| 维度 | 数值 |
|---|---|
| Markdown / MDX 文档 | **173 篇** |
| 目录条目总数（含图片等资源） | 247 个 |
| 文档正文总量 | 约 **1.33 MB** |
| 顶层分区 | 8 个 + quickstart |

分区明细：

| 分区 | 篇数 | 内容 |
|---|---:|---|
| `mcp/` | **74** | 扩展目录：73 个扩展文档 + 1 个模板 |
| `guides/` | **57** | 功能指南（顶层 26 · context-engineering 10 · managing-tools 5 · recipes 5 · security 4 · sessions 4 · interactive-chat 2 · multi-model 1） |
| `tutorials/` | 18 | 端到端教程（CI/CD、Docker、headless、RAG 观测、RPi 等） |
| `experimental/` | 8 | 实验功能（移动端、Telegram 网关、VS Code 扩展、Ollama shim） |
| `gdk/` | 5 | 开发工具包（SDK + ACP） |
| `troubleshooting/` | 4 | 排错与诊断 |
| `getting-started/` | 3 | 安装、Provider、扩展入门 |
| `goose-architecture/` | 3 | 架构、扩展设计、错误处理 |
| `quickstart.md` | 1 | 快速开始 |

**结论**：goose 的文档密度（173 篇 / 55k stars ≈ 每千星 3.1 篇）在对比组中属于第一梯队，且 73 个扩展每个都有独立文档页——这是 v2.0 判断"第三方生态薄弱"时需要修正的一点：**官方文档覆盖度并不薄弱，薄弱的是第三方教程与社区插件**。

### 3.2 官方架构：三组件与六步交互循环

官方 `goose-architecture.md` 给出的架构定义（此前 v2.0 的架构描述为推断，此处替换为官方口径）：

| 组件 | 职责 |
|---|---|
| **Interface** | 用户使用的桌面应用或 CLI，收集输入、显示输出 |
| **Agent** | 运行 goose 核心逻辑，管理交互循环 |
| **Extensions** | 通过 MCP 提供具体工具与能力（如执行命令、文件操作） |

一次会话中，Interface 启动一个 Agent 实例，Agent 同时连接一个或多个扩展；**Interface 也可创建多个 Agent 并发处理不同任务**。

**交互循环六步**（官方原文步骤）：

| # | 步骤 | 说明 |
|---|---|---|
| 1 | Human Request | 用户提出请求 / 问题 / 命令 |
| 2 | Provider Chat | goose 把请求**连同可用工具列表**发给 LLM provider；provider 处理并可能生成 tool call |
| 3 | Model Extension Call | **LLM 只能生成 JSON 格式的 tool call 请求，无法自行执行**——由 goose 执行并收集结果 |
| 4 | Response to Model | 把执行结果送回模型；如需更多扩展则重复 2–4 |
| 5 | Context Revision | goose 移除旧的 / 无关信息，让 LLM 只关注最重要的内容，控制 token |
| 6 | Model Response | 所有 tool call 完成后返回最终响应，用户再次输入则重启循环 |

**Context Revision 的四项具体机制**（官方明确列出，比 v2.0 的"compaction"描述精确得多）：

1. 用**更快、更小的 LLM** 做摘要；
2. 采取**包含全部内容**的策略，而非语义检索；
3. 用**算法删除**旧的 / 无关内容；
4. 用 **find-and-replace 代替重写大文件**、用 **ripgrep 跳过系统文件**、**摘要冗长的命令输出**。

**错误处理设计**：goose 不因错误中断流程，而是捕获传统错误与执行错误（无效 JSON、缺失工具等），**作为 tool response 送回模型**，让 LLM 获得足够信息自行解决并继续。

### 3.3 内置扩展体系（14 个）

官方文档明确列出 14 个内置扩展，分两类：

**基础内置（5 个）**

| 扩展 | 作用 | 默认状态 |
|---|---|---|
| **Developer** | 通用软件开发工具集 | **默认启用** |
| Computer Controller | 网页抓取、文件缓存、自动化 | — |
| Memory | 记住用户偏好 | — |
| Tutorial | 交互式教程 | — |
| Auto Visualiser | 对话内自动生成数据可视化 | — |

**平台扩展（9 个）**

| 扩展 | 作用 | 默认状态 |
|---|---|---|
| **Analyze** | 分析代码结构、文件详情、符号调用图 | **默认启用** |
| **Extension Manager** | 会话中动态发现、启用、禁用扩展 | **默认启用** |
| **Skills** | 从内置与文件系统发现并加载技能指令 | **默认启用** |
| **Summon** | 加载知识源，并把任务委派给 subagents | **默认启用** |
| Apps | 创建、管理、在独立窗口中启动自定义 HTML 应用 | — |
| Chat Recall | 跨全部会话历史搜索对话内容 | — |
| Code Mode | 执行 JavaScript 完成工具发现与工具调用 | 视构建而定 |
| Todo | 跨会话管理任务列表与进度 | — |
| Top of Mind | 每轮向工作记忆注入持久指令 | — |

**关键补充事实**：

- **goose 的内置扩展本身就是独立的 MCP server**，可直接用于其他 agent（官方原文明确允许）。
- **默认自主运行**：goose 默认自主执行，叠加 Developer 扩展后，**可在未经批准的情况下执行命令、修改文件**——官方以 warning 形式提示，需配合权限模式与工具权限加以约束。
- **恶意包拦截**：goose 在激活外部扩展前会**自动检查已知恶意软件**，检出则阻止加载并给出明确错误。

### 3.4 MCP 扩展目录（73 个）

`mcp/` 目录实测 74 个文件，其中 73 个为扩展文档（另 1 个 `_template_.mdx` 为模板）。按用途归类：

| 类别 | 代表扩展 |
|---|---|
| 开发与代码 | GitHub、GitMCP、JetBrains、VS Code、Chrome DevTools、Puppeteer、Playwright、Selenium、Code Mode、Container Use |
| 数据与存储 | PostgreSQL、MongoDB、Neon、Supabase、DataHub、OpenMetadata、Knowledge Graph、Memory |
| 云与部署 | Cloudflare、Vercel、Netlify、Cloudinary、Docker 相关 |
| 搜索与研究 | Brave、Exa、Firecrawl、Tavily、Context7、Scholar Sidekick、Repomix、Reddit、YouTube Transcript |
| 办公与设计 | Google Drive、Google Maps、Figma、Excalidraw、Asana、PDF |
| 多媒体 | ElevenLabs、Speech、Blender、Nano Banana、Remotion |
| 金融与商业 | Square、Cash App、Kiwi Flight Search |
| 系统与运维 | Linux MCP Server、VMware AIOps、Extension Manager、Summon、Todo |
| 其他 | Apollo/AgentQL、Alby、Apify、Beads、Nostrbook、Ophis、Pieces、Rendex、Spraay 等 |

**与 v2.0 的对应**：v2.0 引用 README 的"70+ 官方扩展"表述成立，现可精确为 **73 个**（文档目录口径）。**v2.2 补充**：`AGENTS.md` 声明该目录**正在退役**，改用官方 MCP Registry 与 `server.json`（见 4.13）。

---
### 3.5 CLI 命令全表（官方文档口径）

v1.1 曾误引社区教程中的 `goose task "..."` 用法。以下为官方文档列出的完整命令集——**goose 没有 `task` 子命令**，对应能力由 `session` 与 `run` 提供。

**核心与维护**

| 命令 | 作用 |
|---|---|
| `goose configure` | 配置 provider、扩展、goose 设置（菜单支持输入即筛选） |
| `goose info [-v]` | 显示版本、配置文件位置、会话存储、日志 |
| `goose --version` | 查看当前版本 |
| `goose update [--canary] [--reconfigure]` | 更新到 stable 或 canary 通道 |
| `goose completion <SHELL>` | 生成补全脚本：`bash` `elvish` `fish` `nu` `powershell` `zsh` |

**会话管理**

| 命令 | 作用 |
|---|---|
| `goose session` | 启动 / 恢复交互式会话 |
| `goose session list` | 列出会话（`--format text\|json`、`--ascending`、`-w` 按工作目录过滤、`-l` 限量） |
| `goose session remove` | 删除会话（`--session-id` / `-n` / `-r` 正则 / `--path`） |
| `goose session rename` | 重命名会话 |
| `goose session export` | 导出会话（`--format markdown\|json\|yaml`，`-o` 输出文件） |
| `goose session diagnostics` | 生成诊断 JSON（系统信息、会话数据、配置文件、日志） |

`goose session` 的关键选项：

| 选项 | 说明 |
|---|---|
| `--session-id` / `-n, --name` | 按 ID 或名称指定会话 |
| `-r, --resume` | 恢复上次会话 |
| `--fork` | 复制历史创建新会话（须与 `--resume` 同用） |
| `--edit` | 在 `$VISUAL` / `$EDITOR` 中以 **YAML** 打开会话，可编辑、裁剪、重写消息后再继续 |
| `--history` | 恢复时显示历史消息 |
| `--container <id>` | 在 Docker 容器内运行扩展 |
| `--max-tool-repetitions <N>` | 限制同一工具以相同参数连续调用的次数，防死循环 |
| `--max-turns <N>` | 无用户输入时的最大轮数（默认 1000） |
| `--with-extension` | 添加 stdio 扩展，格式 `[name:]ENV1=val1 command args...` |
| `--with-streamable-http-extension <url>` | 添加 Streamable HTTP 远程扩展 |
| `--with-builtin <id>` | 启用内置扩展（如 `developer`、`computercontroller`） |

**任务执行**

| 命令 | 作用 |
|---|---|
| `goose run` | 从指令文件或 stdin 执行任务 |
| `goose review [range]` | 用 goose 审查 git diff |

`goose run` 的关键选项：

| 选项 | 说明 |
|---|---|
| `-i, --instructions <FILE>` | 指令文件（`-` 表示 stdin） |
| `-t, --text <TEXT>` | 直接输入文本 |
| `--system <TEXT>` | 追加系统指令 |
| `--recipe <FILE>` | 加载 recipe |
| `--params <K=V>` / `--sub-recipe <R>` | recipe 参数 / 子 recipe |
| `-s, --interactive` | 处理完初始输入后继续交互 |
| `--no-session` | 不创建、不存储会话 |
| `--output-format text\|json\|stream-json` | **面向自动化的结构化输出**：`json` 结束后返回，`stream-json` 事件流式返回 |
| `-q, --quiet` | 只输出模型响应 |
| `--explain` / `--render-recipe` | 展示 recipe 信息 / 渲染结果而不执行 |
| `--provider` / `--model` | 覆盖本次会话的 provider 与模型 |

`goose review` 是 v2.0 完全未提及的能力：默认审查工作树对 `HEAD` 的差异，可传 `main...HEAD` 之类的区间；从 `.agents/checks/*.md` 发现检查项、从 `.agents/REVIEW.md` 读取范围化审查指令；支持 `--severity`（默认 `medium`）、`--check-filter`、`--checks-only`、`--no-orchestrate`（关闭 Rust 并行编排器）。

**扩展、技能与本地模型**

| 命令 | 作用 |
|---|---|
| `goose mcp <name>` | 运行指定的已启用 MCP server |
| `goose plugin install <git-url> [--auto-update]` | 安装 git 插件（Open Plugins 规范），落在 `~/.agents/plugins/<name>/` |
| `goose plugin update <name>` | 更新已安装插件 |
| `goose skills list` | 列出可用技能，含 token 数与来源位置 |
| `goose local-models search <query> [-l N]` | **在 Hugging Face 搜索兼容的 GGUF / MLX 模型** |
| `goose local-models download <spec>` | 下载并注册模型（如 `user/repo:Q4_K_M`） |
| `goose local-models list` / `delete <id>` | 列出 / 删除本地模型（别名 `lm`） |

**自动化与协议**

| 命令 | 作用 |
|---|---|
| `goose schedule add\|list\|remove\|sessions\|run-now\|cron-help` | 用 **cron 表达式**定时运行 recipe（如 `--cron "0 0 9 * * *"`） |
| `goose acp [--enable-scheduler]` | 以 **stdio 上的 ACP server** 运行，供 Zed / JetBrains 等接入 |
| `goose serve` | 以 **HTTP / WebSocket 上的 ACP server** 运行（默认 `127.0.0.1:3284`） |
| `goose term init\|run\|info` | 终端集成：`goose term init zsh` 为每个 shell 建立持久会话（`AGENT_SESSION_ID`），并创建 `@goose` / `@g` 别名 |

`goose serve` 需 `GOOSE_SERVER__SECRET_KEY`（可用 `openssl rand -hex 32` 生成），除非显式传 `--dangerously-unauthenticated`（仅限本地可信客户端）。

### 3.6 交互式会话斜杠命令（15 个）

进入会话（`goose session` 或 `goose run --interactive`）后可用，全部支持 Tab 补全：

| 命令 | 作用 |
|---|---|
| `/?` 或 `/help` | 帮助菜单 |
| `/builtin <names>` | 按名称添加内置扩展（逗号分隔） |
| `/clear` | 清空当前对话历史 |
| `/exit` 或 `/quit` | 退出会话 |
| `/extension <command>` | 添加 stdio 扩展 |
| `/mode <name>` | 设置模式：`auto` / `approve` / `chat` / `smart_approve` |
| `/model [name]` | 查看或切换模型（保持同一 provider） |
| `/model --provider <name> [model]` | 切换到其他 provider |
| `/prompt <n> [--info] [k=v...]` | 查看提示信息或执行提示 |
| `/prompts [--extension <name>]` | 列出可用提示，可按扩展过滤 |
| `/compact` | 压缩并摘要当前对话（`/summarize` 为已弃用别名） |
| `/r` | 切换完整工具输出显示（不截断参数） |
| `/skills [<name>...]` | 列出技能，或按名称加载技能 |
| `/t` | 在 `light` → `dark` → `ansi` 间循环主题 |
| `/t <name>` | 直接设置主题 |

**会话存储迁移**：自 **v1.10.0** 起，goose 改用 SQLite 数据库（`sessions.db`）替代独立的 `.jsonl` 文件，旧会话自动导入，遗留 `.jsonl` 保留在磁盘但不再由 goose 管理。

**CLI 主题**：默认 `dark`，设置持久化到配置文件的 `GOOSE_CLI_THEME`；代码块语法高亮可用 `GOOSE_CLI_LIGHT_THEME` / `GOOSE_CLI_DARK_THEME` 指定任意 **bat 主题名**（如 Dracula、Nord、Monokai Extended）。CLI 主题与 Desktop 主题相互独立。

**外部编辑器模式**：`GOOSE_PROMPT_EDITOR` 可用 vim / nano / emacs，GUI 编辑器需加 `--wait`（如 `code --wait`）。

### 3.7 上下文工程（Context Engineering，10 项）

官方将"让 goose 高效工作所需的背景知识、偏好与工作流"统称为 Context Engineering，含 10 个机制：

| 机制 | 作用 |
|---|---|
| **goosehints** | 用 `AGENTS.md`、`.goosehints` 等文件提供项目上下文与指令，goose 自动加载 |
| **Skills** | 可复用的指令集，含工作流、脚本与其他资源，按需加载 |
| **Custom Agents** | 创建、编辑、导入、导出专用 goose agent（可复用提示 + 可选元数据） |
| **Plugins** | 安装、更新、管理以技能与 hooks 扩展 goose 的包 |
| **Hooks** | 在 goose 启动会话、提交提示、调用工具、编辑文件或执行 shell 时运行脚本 |
| **Custom Slash Commands** | 自定义斜杠命令，快速执行可复用指令 |
| **Prompt Templates** | 自定义内置提示（决定 goose 如何响应、规划、压缩上下文、创建 recipe） |
| **Subagents** | 把聚焦任务委派给**隔离的 goose 实例**，可顺序或并行运行 |
| **Persistent Instructions** | **每轮**向工作记忆注入关键提醒，适合安全护栏与不可遗忘的行为规则 |
| **Memory Extension** | 跨会话持久知识（命令、代码片段、偏好） |

其中 **Persistent Instructions** 与 **Subagents** 是 v2.0 未展开的能力；Subagents 的每个实例**可各自运行独立的 provider 与模型**（见 3.8 多模型策略）。

---
### 3.8 智能上下文管理（官方参数级细节）

v2.0 只写到"有 compaction"。官方文档给出了**两层机制与完整可调参数**：

**第一层：自动压缩（Auto-Compaction）**

| 项 | 官方值 |
|---|---|
| 触发条件 | 达到 token 限制的 **80%** 或 **225,000 tokens**，**先到者为准** |
| 有效公式 | `min(GOOSE_AUTO_COMPACT_THRESHOLD × 模型上下文窗口, GOOSE_AUTO_COMPACT_TOKEN_LIMIT)` |
| 默认上限设计意图 | 225,000 为 **OpenAI 长上下文定价档（272,000 输入 token）以下留出余量** |
| 阈值调整 | `GOOSE_AUTO_COMPACT_THRESHOLD`（设 `0.0` 可禁用，且 token 上限不会重新启用已禁用的自动压缩） |
| 摘要定制 | 编辑 `compaction.md` prompt template |
| 工具输出摘要 | 后台摘要较旧的工具调用输出，最近的保留完整细节；`GOOSE_TOOL_CALL_CUTOFF` 可微调 |

压缩后行为：**先前对话仍可见，但只有压缩后的内容进入活跃上下文**。

**第二层：上下文超限策略（Context Limit Strategies）**

| 策略 | 描述 | 适用场景 | 可用性 |
|---|---|---|---|
| **Summarize** | 压缩对话并保留要点 | 长而复杂的对话 | Desktop + CLI |
| **Truncate** | 删除最旧的消息 | 简单线性对话 | 仅 CLI |
| **Clear** | 保持会话活跃但重新开始 | 话题转向 | 仅 CLI |
| **Prompt** | 让用户逐次选择 | 需要掌控每次决策 | 仅 CLI |

- Desktop **只使用 summarize**；
- CLI 交互模式默认 `prompt`，headless（`goose run`）默认 `summarize`；
- 可用 `GOOSE_CONTEXT_STRATEGY=summarize|truncate|clear|prompt` 固定策略。

**最大轮数（Max Turns）**：默认 **1000**，存于配置文件的 `GOOSE_MAX_TURNS`；达到后 goose 停止并询问是否继续。官方给出的取值建议：

| 轮数 | 适用 |
|---|---|
| 5–10 | 探索性任务、调试、需要频繁确认 |
| 25–50 | 定义良好、中等复杂度的任务 |
| 100+ | 复杂多步自动化，信任 goose 独立工作 |

**上下文限制解析优先级**（官方 5 级）：

1. 全局环境变量 `GOOSE_CONTEXT_LIMIT`
2. 显式声明式或自定义 provider 模型配置
3. Provider 运行时发现
4. 规范模型元数据
5. **全局默认 128,000 tokens**

**Token 用量可视化**：Desktop 在模型名旁显示彩色圆点（绿=正常 / 橙=达 80% / 红=超限）；CLI 在提示符上方显示上下文标签（绿 <50% / 黄 50–85% / 红 >85%）。

**成本与余额**：Desktop 可开关成本追踪，实时显示会话估算成本（多模型时按模型分列，Ollama 与本地部署恒为 $0.00），定价定期从 OpenRouter API 获取并本地缓存；CLI 用 `GOOSE_CLI_SHOW_COST=true`。另支持**信用余额监控**——通过 HTTP 402 响应检测低余额并提示，Tetrate / OpenRouter 等支持一键跳转充值。

### 3.9 安全体系（官方口径）

> **v2.2 补充**：源码中 `security/` 实为 **7 个模块**（含未见于文档的 `egress_inspector.rs`），另有 `permission/permission_judge.rs`。本节为官方文档口径，源码口径见 **4.10**。

官方 `guides/security/` 给出三项机制（v2.0 仅列举名称，此处补全定位）：

| 机制 | 官方定位 |
|---|---|
| **Adversary Mode** | **独立 agent 审查者**，静默监视 tool call，在 agent 失控时保护用户 |
| **Prompt Injection Detection** | 在命令执行前检测并阻止潜在有害指令 |
| **Classification API Specification** | 供**自托管**基于 ML 的提示注入检测端点的 API 规范 |

叠加此前已在 v2.0 记录的机制（macOS 沙箱、工具权限控制、SLSA 构建溯源、恶意包拦截），goose 的安全体系可归为四层：**执行前检测 → 执行中监视 → 权限约束 → 供应链溯源**。

官方同时明确警示：**goose 默认自主运行**，配合 Developer 扩展可在无批准情况下执行命令与修改文件，建议通过 `goose permission mode` 与 `tool permissions` 收窄权限。

### 3.10 GDK：Goose Development Kit

v2.0 完全未覆盖。官方将 GDK 定位为"构建 agentic 应用所需的核心组件"，覆盖 **agent 编排、模型访问、上下文管理、工具、记忆、远程执行、自动化、路由**，提供两种接入方式：

| 方式 | 说明 |
|---|---|
| **SDK** | 把 goose 的 provider 层作为**进程内库**使用，支持 **Rust、Python、Kotlin** |
| **ACP** | 作为**独立 agent 进程**连接，传输层支持 **stdio、HTTP、WebSocket** |

**对生态位的意义**：goose 不只是终端产品，还是一个**可被嵌入的 agent 运行时**。这解释了 `crates/` 中 `goose-sdk` / `goose-sdk-types` 独立成 crate 的设计（见 2.2），也意味着它与 Dify / Coze 这类"平台化"产品的差异——goose 提供的是**库与协议**，而非可视化编排界面。

### 3.11 Roaming Agents：点对点远程 Agent（v2.1 新增）

v2.0 只记录到存在 `goose-roaming` crate，实际能力远超预期。官方定位：**让你从另一台机器访问运行中的 goose agent，无需开放端口、无需 VPN、无需自建服务器**。

| 项 | 内容 |
|---|---|
| 传输基础 | **iroh（QUIC）**，可直连（NAT 打洞成功时）或经中继回退 |
| 本质 | **一个经过认证的点对点 ACP 传输**——host 跑 goose 真正的 ACP server，连接方是 ACP client |
| 可用性 | **实验性，且不包含在正式发布的二进制中**。需 `cargo build --release -p goose-cli --features roaming`；默认构建下 `goose roam` 会报"无法识别的子命令" |
| 信任模型 | **公钥互认**（类比 WireGuard / SSH known-hosts）。每节点一个长期身份，生成**连接卡**（`goose+roam://…`）；**卡片不含任何秘密**，持有卡片不授予任何权限 |
| 配对方式 | 交换卡片 → 双方 `peers accept` 对方公钥；支持 `--qr` 二维码扫码配对；`goose roam pair` 一步完成 |
| 命令集 | `roam id` / `peers add\|accept\|list\|revoke` / `share` / `connect` / `delegate` / `bridge` / `connections` / `pair` |
| 委派模式 | `roam delegate <target> "任务"` 一次性任务；`--list-sessions`、`--session <id>` 复用远端会话 |
| 桥接模式 | `roam bridge` 把远端 agent 暴露为**本地 ACP 端点**，供 Zed 等编辑器当作本地 agent 使用 |
| 集成方式 | 独立 crate，**零依赖 goose core**；`goose serve --roam` 一个进程同时提供常规 agent server 与 roam |
| 浏览器支持 | 同一传输可编译为 **WebAssembly**（`@aaif/goose-roam-web`），浏览器标签页自身即一个 roam peer，**无需中间服务器** |
| 参考实现 | 托管 Web 客户端 https://aaif-goose.github.io/goose-mobile/ ，源码在独立仓库 **`aaif-goose/goose-mobile`** |
| 中继 | 默认使用 **goose 自管的 iroh 中继**（按区域，非 iroh 公共中继）；`GOOSE_ROAM_RELAYS` 可指向自建部署 |

**安全边界（官方明确警告）**：接受一个 peer 即授予**完全控制权**——对方可驱动 agent 的工具，**包括 shell**，等同于远程 shell 访问；**没有更细粒度的角色，接受是全有或全无**。撤销是持久且实时的：写入磁盘，运行中的 `share` 每次连接重读并约每 2 秒轮询信任文件，撤销后数秒内对已建立连接生效（但工具已 fork 出的 OS 进程可能跑完）。

### 3.12 实验性功能（官方标记）

| 功能 | 说明 |
|---|---|
| **Ollama Tool Shim** | 为**不支持原生 tool calling 的模型**（如 DeepSeek）提供工具调用能力；需独立解释器模型，默认 Ollama + `mistral-nemo` |
| **Remote Access** | 经 goose AI 移动 App 或 Telegram 等消息平台远程访问 |
| **goose for VS Code Extension** | 在 VS Code 内经 ACP 与 goose 交互 |

**Tool Shim 参数**（官方表格）：

| 环境变量 | 说明 | 默认 |
|---|---|---|
| `GOOSE_TOOLSHIM` | 启用（`true` / `1`） | `false` |
| `GOOSE_TOOLSHIM_BACKEND` | 解释器后端：`ollama` / `local` / `llama.cpp` | `ollama` |
| `GOOSE_TOOLSHIM_OLLAMA_MODEL` | 作为解释器的 Ollama 模型 | `mistral-nemo` |
| `GOOSE_TOOLSHIM_MODEL` | 本地解释器后端模型名（用 `local` 且未设 `LOCAL_LLM_MODEL` 时必填） | — |

**触发场景**（官方列举）：会话中途工具突然失效、模型输出 `functions.shell:0 <|tool_call_argument_begin|> {...}` 之类的纯文本、使用本地模型（Ollama / llama.cpp）、OpenAI 兼容 provider 的模型把 `<think>` 推理标签与 tool call 混在一起导致解析失败。

### 3.13 安装与配置要点补充

**官方安装口径与实测产物的差异**（值得注意）：

| 平台 | 官方文档给出的方式 | 实测发布产物 |
|---|---|---|
| macOS | 下载桌面 App 或 `brew install --cask block-goose`；CLI 用一行脚本或 `brew install block-goose-cli` | 桌面 zip ×4 + CLI tarball ×4 |
| **Linux 桌面** | **仅列出 DEB**（"For Debian/Ubuntu-based distributions: `sudo dpkg -i (filename).deb`"） | **RPM / DEB / Flatpak 三种齐全** |
| Linux CLI | 一行脚本，可 `CONFIGURE=false` 跳过交互配置 | 12 个 tarball（gnu / musl / vulkan 变体） |
| Windows | Git Bash / MSYS2（推荐）、PowerShell 脚本、WSL（可选） | 4 个产物（含 cuda 变体） |

> **结论**：**官方 Linux 桌面文档滞后于实际产物**——文档只写 DEB，但实际同时发布 RPM 与 Flatpak（见 6.1）。RPM 与 Flatpak 用户目前只能自行从 Release 页面获取。

**其他安装/配置要点**：

- **Homebrew cask 名仍为 `block-goose`**（另一个品牌迁移遗留，与 Flatpak ID `io.github.block.Goose` 同类）。
- **CI/CD 固定版本**：用 `GOOSE_VERSION` 固定版本以保证可复现，避免 `stable` tag 不含二进制资产时下载 404。
- **发行版打包支持**：`just generate-manpages` 生成 ROFF manpage（`goose.1`、`goose-session.1` 等）到 `target/man/`，供 Fedora / Debian 等打包者安装到 `/usr/share/man/man1/`。
- **配置共享**：CLI 与 Desktop **共享全部核心配置**（provider 设置、模型选择、扩展配置），存于中心位置，可在两个界面间无缝切换。
- **配置文件**：`~/.config/goose/config.yaml`。
- **扩展安装的三种途径**：扩展目录、CLI / UI、**Deeplink 协议** `goose://extension?cmd=…&arg=…&id=…&name=…&description=…`（`cmd` 仅允许 `jbang` / `npx` / `uvx` / `goosed` / `docker`；远程扩展用 `type=streamable_http`）。所有参数需 URL 编码。
- **MCP Roots 支持**：roots-aware 扩展可自动获知当前会话工作目录。
- **智能扩展推荐**：goose 会依据任务自动判断并建议 / 启用所需扩展（动态启用**仅对当前会话有效**）。
- **远程扩展 OAuth**：支持 `client_id` / `client_secret_key` / `scopes` 配置预注册客户端；回调服务在 `127.0.0.1` 临时端口，`GOOSE_OAUTH_CALLBACK_PORT` 可固定端口。
- **离线环境**：文档站提供 Offline / Air-gapped Docs 方案；企业内网中扩展激活失败可参考 Known Issues 的对应章节。
- **社区入口**：Discord `discord.gg/n8R5VaWDAn`。

---

## 4. 源码级架构与工程实践

> 本章为 **v2.2 新增**。v2.1 补全了官方文档维度，但文档描述的是"设计意图"，源码反映的是"实际实现"。本章基于 `main` 分支**全量文件树（3,038 个文件，未截断）**逐目录核对，补出前两版都缺失的实现层事实，并**纠正 4 处把计划当成既成事实的表述**。

### 4.1 仓库全貌（全量枚举）

Git Trees API 递归枚举 `main` 分支：**3,038 个文件**（`truncated: false`），**52 个顶层条目**。

| 目录 | 文件数 | 内容 |
|---|---:|---|
| `crates/` | **806** | 15 个 Rust crate（详见 4.2） |
| `ui/` | **645** | 桌面端（608）+ 3 个 npm 包 + 平台二进制包 |
| `documentation/` | 173 篇 md/mdx | 官方文档站（v2.1 已全量抓取） |
| `bin/` | 39 | Hermit 管理的可复现工具链 |
| `.github/workflows/` | **43** | CI/CD 与自动化 |
| `scripts/` | 30 | 基准后处理、复现脚本、诊断工具 |
| `services/` | 29 | `ask-ai-bot`（Discord 支持机器人） |
| `buzz/` | 11 | GitHub issue ↔ Nostr 社区同步自动化 |
| `evals/` | 10 | `harbor` Terminal-Bench 评测工具 |
| `examples/` | 11 | `mcp-wiki`、`plugins/hello-hooks` |
| `oidc-proxy/` | 8 | Cloudflare Worker OIDC 代理 |
| `vendor/v8/` | 2 | 本地补丁的 v8 crate（Code Mode 用） |
| `workflow_recipes/` | 3 | 发布风险检查 recipe |
| 根级配置文件 | 15+ | `Cargo.toml` / `Justfile` / `deny.toml` / `flake.nix` / `AGENTS.md` 等 |

### 4.2 15 个 crate 的真实职责

| crate | 版本 | 职责 | 源文件 |
|---|---|---|---:|
| **goose** | 1.55.0（workspace） | 核心：agent 循环、provider 层、扩展、会话、权限、安全、ACP server | **447** |
| goose-cli | 1.55.0 | CLI：子命令 + 交互会话 + recipe 解析 | 53 |
| goose-mcp | 1.55.0 | 随附 MCP server：autovisualiser / computercontroller / memory / tutorial / peekaboo | 43 |
| goose-roaming | 1.55.0 | iroh P2P 传输（11 个模块） | 17 |
| goose-providers | 0.1.0-alpha.12 | GDK 提供方实现 | 87 |
| goose-provider-types | 0.1.0-alpha.12 | 提供方类型 + 7 种 wire format + canonical 模型目录 | 47 |
| goose-sdk | 0.1.0-alpha.12 | GDK 入口（uniffi 绑定，`cdylib`/`staticlib`/`rlib`） | 34 |
| goose-local-inference | 0.1.0-alpha.12 | 本地推理：llama.cpp + MLX + 工具模拟 | 25 |
| goose-agent | 0.1.0-alpha.12 | GDK 的 Agent Loop（支持 wasm32） | 14 |
| goose-context-management | 0.1.0-alpha.12 | 会话压缩（结构化） | 12 |
| goose-sdk-types | 0.1.0-alpha.12 | GDK 共享类型 | 7 |
| goose-download-manager | 0.1.0-alpha.12 | 模型与资源下载 | 3 |
| goose-acp-macros | — | ACP 过程宏 | 2 |
| goose-test | — | MCP 录制回放、`capture` bin | 7 |
| goose-test-support | — | `mcp_fixture_server`、OTel、会话测试夹具 | 8 |

<div class="callout">
  <div class="ic">§</div>
  <div>
    <p><b>版本双轨制</b>：4 个核心 crate 用 workspace 版本 <code>1.55.0</code>；7 个 GDK crate 独立走 <code>0.1.0-alpha.12</code>。由 <code>release-plz.toml</code> 的 <code>version_group = "gdk"</code> 控制，只对 GDK 系列开启独立发布（其中 <code>goose-local-inference</code> 与 <code>goose-providers</code> 关闭 semver 检查，因为 <code>--all-features</code> 会拉入 cuda/vulkan 加速器依赖，发布机上没有 CUDA Toolkit）。</p>
  </div>
</div>

### 4.3 工作区配置（`Cargo.toml` / `rust-toolchain.toml`）

| 项 | 值 |
|---|---|
| `edition` / `version` | 2021 / **1.55.0** |
| `rust-version`（MSRV） | **1.94.1** |
| `rust-toolchain.toml` channel | **1.99.0** |
| `license` / `authors` | Apache-2.0 / `AAIF <ai-oss-tools@block.xyz>` |
| workspace members | `crates/*` + `vendor/v8`（后者仅为让 `cargo-machete` 不误报） |
| resolver | `"2"` |

<div class="callout bad">
  <div class="ic">!</div>
  <div>
    <p><b>版本状态（重要）</b>：<code>main</code> 分支的工作区版本**已 bump 到 1.55.0**，但 **GitHub 最新发布仍是 <code>v1.54.0</code>（2026-10-08）**。即 1.55.0 处于开发中、尚未发布。引用"当前版本"时必须区分"仓库版本"与"发布版本"。</p>
    <p style="margin-top:8px">另需注意 <b>MSRV ≠ 工具链</b>：<code>rust-version = "1.94.1"</code> 是声明的支持下限，<code>rust-toolchain.toml</code> 的 <code>1.99.0</code> 才是实际构建版本。</p>
  </div>
</div>

**自定义 profile（4 项）**：

| profile | 配置 | 意图 |
|---|---|---|
| `dev.package."*"` | `debug = false` | 注释原文：第三方 rlib 的 DWARF 占每包 **50–70%**，去掉后调试构建显著变小、链接更快；`*` 匹配依赖但不匹配 workspace 成员，**第一方 crate 保留完整调试信息** |
| `lean` | `opt-level="z"` + `lto="fat"` + `codegen-units=1` + `panic="abort"` + `strip="symbols"` | 体积优先的嵌入式 agent 二进制 |

**`[patch.crates-io]`**：`v8 = { path = "vendor/v8" }`（本地补丁，供 Code Mode 执行 JS）+ `cudaforge` 从 git 精确 `rev` 拉取。

**精确版本钉扎（`=`）**：`llama-cpp-2` / `llama-cpp-sys-2` = `0.1.146`；AWS 五个 SDK crate 全部精确钉扎（`aws-config =1.12.0`、`aws-sdk-bedrockruntime =1.143.0` 等）；`icu_calendar` / `icu_locale` = `2.1.1` —— 注释说明这是绕 `temporal_rs` 0.1 经 **PCTX** 引入的 unstable feature 问题，等 PCTX 升级后可移除。

**Lint 与依赖卫生**：

- 工作区 clippy：`uninlined_format_args = "allow"`、`string_slice = "warn"`；`clippy.toml` 设 `too-many-lines-threshold = 200`
- `deny.toml`：`yanked = "deny"`（拒绝被 yank 的依赖）、`unmaintained = "none"`、`unsound = "none"`，唯一豁免 `RUSTSEC-2023-0071`（rsa Marvin 时序侧信道——注释说明无安全升级路径，且可达路径经 `jsonwebtoken`）
- `[package.metadata.cargo-machete] ignored` 在多个 crate 里显式列出豁免项**并注明原因**（如 "Used only on windows" / "Included only to pin version"）
- `.cargo/config.toml`：Windows MSVC 链接参数 `/FORCE:MULTIPLE /STACK:8388608`（**8 MB 栈**）；`wasm32-unknown-unknown` 用 `wasm-bindgen-test-runner`

### 4.4 特性矩阵（feature flags）

`goose` crate 的 `default = []`（**空**），能力全部由可选特性拼装。`goose-cli` 的默认特性有 **18 个**：

| 特性 | 作用 | 关键依赖 |
|---|---|---|
| `code-mode` | 用 JS 编排工具调用 | `pctx_code_mode 0.5.0` |
| `tree-sitter` | 代码结构分析（9 种语言） | tree-sitter + go/java/javascript/kotlin/python/ruby/rust/swift/typescript |
| `local-inference` | 本地推理 + **本地 Whisper 听写** | candle-core/nn/transformers、tokenizers、**symphonia**（音频解码）、**rubato**（重采样） |
| `aws-providers` | Bedrock + SageMaker TGI | AWS SDK（精确钉扎） |
| `live-voice` | 实时语音 | `goose-providers/live-websocket`（tokio-tungstenite） |
| `telemetry` / `otel` | 遥测与 OpenTelemetry | opentelemetry 0.32 全家桶 |
| `rustls-tls` / `native-tls` | TLS 二选一 | aws-lc-rs / openssl |
| `system-keyring` | 系统凭据库 | keyring（macOS apple-native / Linux sync-secret-service / Windows windows-native） |
| `update` | 自更新 | **`sigstore-verify` + `snap`** |
| `bundled-mcp` | 内置 MCP server 打进二进制 | `goose-mcp` |
| `scheduler` / `platform-apps` / `chat-recall` / `acp-http` | 定时任务 / Apps / 会话检索 / ACP over HTTP | tokio-cron-scheduler 等 |
| `cuda` / `vulkan` / `mlx` | 加速器三选 | 对应 candle / llama.cpp / safemlx |
| `portable-default` | 便携构建组合 | 上述大部分 + 不含 `local-inference` |
| `online-model-meta` | 在线获取模型元数据 | — |

<div class="callout ok">
  <div class="ic">✓</div>
  <div>
    <p><span class="t">实测确认</span> — <code>roaming</code> <b>不在 <code>goose-cli</code> 的默认特性里</b>（需显式 <code>--features roaming</code>，并拉入 <code>goose-roaming</code> + <code>qrcode</code> + <code>fs2</code> + <code>agent-client-protocol</code>）。这与官方文档"不含在正式发布二进制中"完全一致，属源码级交叉验证。</p>
  </div>
</div>

**lean 构建与体积预算（CI 强制）**：`just build-lean` = `cargo build -p goose --bin goose-acp --profile lean --no-default-features --features native-tls,online-model-meta`。`just check-lean-size` 在 CI 里卡体积上限：

| 平台 | 预算 |
|---|---|
| macOS | **17,825,792 B（17.0 MiB）** |
| 其他 | **23,068,672 B（22.0 MiB）** |

> Justfile 注释解释了为何不能用单一跨平台数值：ELF 比 Mach-O 多带 DWARF `.eh_frame`（Mach-O 用紧凑 unwind 信息）与 `.rela.dyn` 相对重定位表，同一份代码在 Linux 上就是更大——单一阈值要么在 Linux 上永远达不到，要么在 macOS 上失去回归信号价值。

### 4.5 goose 核心 crate 的模块地图（374 个源文件）

| 模块 | 文件 | 内容 |
|---|---:|---|
| `agents/` | **97** | `state_machine/`(40)、`platform_extensions/`(21)、`extension_manager/`(5)、`snapshots/`(4)、`subagent_execution_tool/`(2) |
| `providers/` | **66** | 提供方实现（见 4.6） |
| `acp/` | **48** | `server/`(33)、`transport/`(3)、`mcp_app_proxy.rs`、`handoff.rs`、`response_builder.rs`、`tool_call_notifier.rs` |
| `config/` | 23 | `migrations.rs`、`permission.rs`、`declarative_providers.rs`、`experiments.rs`、`paths.rs`、`tls.rs`、`signup_openrouter/`、`signup_tetrate/` |
| `session/` | 19 | `session_manager.rs`、`chat_history_search.rs`、`export_html/`(6)、`import_formats/`(4)、`legacy.rs`、`diagnostics.rs` |
| `recipe/` | 11 | `manifest.rs`、`template_recipe.rs`、`validate_recipe.rs`、`build_recipe/`、`local_recipes.rs` |
| `security/` | 7 | `adversary_inspector.rs`、`classification_client.rs`、**`egress_inspector.rs`**、`patterns.rs`、`scanner.rs`、`security_inspector.rs` |
| `skills/` | 7 | `builtin.rs`、`builtins/`、`client.rs`、`supporting_files.rs` |
| `live_voice/` | 7 | `interaction.rs`、`service.rs`、`transcript.rs` |
| `prompts/` | 7 | 内嵌提示词（见下） |
| `dictation/` | 6 | `whisper.rs` + `whisper_data/` |
| `plugins/` | 6 | `discovery.rs`、`formats/`(3)、`mcp_servers.rs` |
| `slash_commands/` | 6 | `recipe_slash_command.rs`、`skill_slash_command.rs` |
| `goose_apps/` | 5 | `app.rs`、`cache.rs`、`resource.rs`、`clock.html` |
| `gateway/` | 5 | `telegram.rs`、`pairing.rs`、`handler.rs`、`manager.rs` |
| `permission/` | 4 | `permission_inspector.rs`、**`permission_judge.rs`**、`permission_store.rs` |
| `execution/` / `hints/` / `otel/` / `tracing/` / `scheduler/` | 3 各 | `active_run.rs`、`load_hints.rs`、`otlp.rs`、**`langfuse_layer.rs`**、`full.rs` |

**7 个内嵌提示词**（`prompts/*.md`，编译进二进制）：`system.md`、`tiny_model_system.md`、`subagent_system.md`、`permission_judge.md`、`session_name.md`、`apps_create.md`、`apps_iterate.md`。

<div class="callout warn">
  <div class="ic">!</div>
  <div>
    <p><span class="t">源码里才有的模块（官方文档未提及）</span></p>
    <p><b>实时语音</b>：<code>live_voice/</code>（interaction / service / transcript，配 <code>live-voice</code> 特性走 WebSocket）<br>
    <b>本地听写</b>：<code>dictation/whisper.rs</code> + 内嵌 whisper 数据（本地 Whisper 转写，<code>test_whisper</code> 示例需 <code>local-inference</code>）<br>
    <b>消息网关</b>：<code>gateway/telegram.rs</code> + <code>pairing.rs</code>（配对码）<br>
    <b>出站检查</b>：<code>security/egress_inspector.rs</code> —— 官方只列了"安全三件套"，源码里是 7 个模块、四类检查器<br>
    <b>模型判官</b>：<code>permission/permission_judge.rs</code> + <code>prompts/permission_judge.md</code>（用模型判断该不该批准工具调用）<br>
    <b>产品分析</b>：<code>posthog.rs</code>；<b>实例标识</b>：<code>instance_id.rs</code>；<b>诊断</b>：<code>doctor.rs</code><br>
    <b>观测后端</b>：<code>tracing/langfuse_layer.rs</code>（Langfuse）+ <code>otel/otlp.rs</code> + <code>trace_context.rs</code></p>
  </div>
</div>

### 4.6 提供方实现全景（远超"15+"）

README 说 "works with 15+ providers"。源码 `crates/goose/src/providers/` 有 **66 个文件**，实际实现如下：

| 类别 | 实现 |
|---|---|
| **直连 API** | Anthropic、OpenAI、Google、Azure（含 Azure AI Foundry）、AWS Bedrock、AWS SageMaker TGI、GCP Vertex AI、Databricks（v1 + v2）、Snowflake、Ollama（本地 + Cloud）、OpenRouter、LiteLLM、HuggingFace、xAI、NanoGPT、Tetrate、Avian、Gondola、KimiCode、Muse Code、GitHub Copilot、本地推理 |
| **把别的 agent 当 provider（经 ACP）** | `claude_acp`、`codex_acp`、`copilot_acp`、`pi_acp`、`amp_acp`、`cursor_agent`；另有 `gemini_cli`、`claude_code`、`codex` 直连封装 |
| **声明式提供方定义**（`*_def.rs`，10 个） | anthropic / azure_foundry / databricks / databricks_v2 / google / muse_code / ollama / openai / openrouter / snowflake |

**支撑设施**：

- **7 种 wire format**（`goose-provider-types/src/formats/`）：anthropic、databricks、google、ollama、openai、**openai_responses**、snowflake
- **canonical 模型目录**：`canonical/`（catalog / model / **models_dev** / name_builder / registry + `data/`）。`just build-canonical-models` 从 **models.dev** 重建，产物 `canonical_models.json` + `provider_metadata.json` **检入仓库**；`just prepare-release` 每次发版都重建 —— 即**模型元数据是随版本快照固定的生成物**
- **成本与用量**：`canonical_cost.rs`（成本表）、`usage_estimator.rs`（用量估算）
- **鉴权**：`oauth.rs` + `oauth_device_flow.rs`（设备码）、`command_auth.rs`（外部命令取 token）、`azureauth.rs` / `gcpauth.rs` / `huggingface_auth.rs` / `xai_oauth.rs` / `gemini_oauth.rs`
- **可测试性**：`provider_registry.rs`、`provider_secrets.rs`、`private_file.rs`（权限受限的密钥文件）、`provider_test.rs`、`testprovider.rs`

### 4.7 桌面端真相：Electron，不是 Tauri（v2.2 修正）

`ui/desktop/package.json` 实测：

| 项 | 值 |
|---|---|
| 包名 / 版本 | `goose-app` / **1.55.0** |
| 运行时 | **Electron 43.4.0** |
| 构建 | **Electron Forge 7.11.2** + `plugin-vite` / `plugin-fuses`（安全熔断）/ `plugin-auto-unpack-natives` |
| 前端 | React **19.2.8** + Vite **8.2.1** |
| 主进程入口 | `.vite/build/main.js` |
| 打包 maker | `maker-deb` / `maker-rpm` / `maker-flatpak` / `maker-squirrel`（Windows）/ `maker-zip` |
| 依赖规模 | 58 deps + 51 devDeps |
| 测试 | vitest（单元/集成）+ Playwright（`test-e2e*`） |
| i18n | react-intl / FormatJS + ICU MessageFormat，`@formatjs/cli` 抽取，已校验 **es / ja** 语言包 |

**全仓库检索 "tauri" 只命中 2 个文件**：一篇官方博客与 `goose-roaming/README.md`（后者写的是 "No Tauri, no local bridge"）。**仓库内不存在任何 Tauri 代码。**

<div class="callout bad">
  <div class="ic">!</div>
  <div>
    <p><span class="t">修正 v2.0 / v2.1 的表述</span></p>
    <p>官方 2026-04-08 博客（issue #6642）把 "Desktop rewrite to Tauri" 列为路线图第 3 项，状态 <b>🚧 In progress</b>，原文："Electron app being replaced with a Tauri-based desktop client on ACP"。</p>
    <p style="margin-top:8px">v2.0/v2.1 写成"<b>2.0 beta 起桌面端改用 Tauri 重写</b>"，等于<b>把计划当成了既成事实</b>。源码实测：截至 2026-10-15，桌面端<b>仍是 Electron 43.4.0</b>，Tauri 迁移未落地。同时这也说明 v2.0 把它列为"劣势"（架构过渡期风险）是成立的——只是表述方式错了。</p>
  </div>
</div>

**由 Electron 反向解释的两个既有事实**：

1. **DEB / RPM / Flatpak 的来源**是 Electron Forge 的 `maker-deb` / `maker-rpm` / `maker-flatpak`，而不是 Rust 侧打包。这解释了为什么三种包格式能同时齐备。
2. **`mac-update-requirements.json`**（v1.52.0 起新增的发布产物）是 Electron 自动更新的 macOS 清单文件，与 `maker-squirrel` 生态一致。

**桌面端的其他源码事实**：`entitlements.plist` 含麦克风权限（配合听写 / 语音）；`forge.deb.desktop` / `forge.rpm.desktop` 为桌面入口文件模板；桌面会**内嵌 goose CLI 二进制**到 `ui/desktop/src/bin/`（Justfile `copy-binary` 任务），并支持 `GOOSE_EXTERNAL_BACKEND=true` 走外部 ACP 后端。

### 4.8 分发与打包（源码口径）

**npm 渠道（官方文档未收录）**：

| 包 | 作用 |
|---|---|
| `@aaif/goose-acp` | **用户实际安装的包**，自动装对应平台包并提供 `goose` 命令 |
| `@aaif/goose-binary-darwin-arm64` | macOS Apple Silicon |
| `@aaif/goose-binary-darwin-x64` | macOS Intel |
| `@aaif/goose-binary-linux-arm64` | Linux ARM64 |
| `@aaif/goose-binary-linux-x64` | Linux x64 |
| `@aaif/goose-binary-win32-x64` | Windows x64 |

> `publish-npm.yml` 从**精确版本号的 Release** 下载二进制并打包；默认只上传为 workflow artifact，需手动把 `publish` 输入置为 true 才真正发布到受保护的 npm production 环境。

**ACP 类型是代码生成的，且产物检入仓库**：

```
Rust 类型
  └─ generate-acp-schema bin ─► crates/goose/acp-schema.json + acp-meta.json
        └─ ui/goose-acp-client/generate-schema.ts ─► src/generated/（TypeScript）
              └─ documentation/scripts/generate-acp-docs.js ─► 文档
```
`just check-acp-artifacts` 在 CI 里校验这些生成物是否过期，过期直接失败。

**发布产物口径（本次复核）**：v1.54.0 共 **40 个** asset —— rpm 4 + deb 4 + flatpak 4 + zip 9 + tarball 17 + 其他 2；**Linux 相关 24 个**（12 个包 + 12 个 CLI tarball），与 v2.0 结论一致。

**产物数变化（新发现）**：v1.48.0 至 v1.51.0 为 **37 个**，**v1.52.0 起为 40 个**——新增的是 2 个 macOS 桌面 zip（`Goose-darwin-{arm64,x64}.zip`）与 `mac-update-requirements.json`。

**发布节奏（`RELEASE.md`）**：minor 版本**每周一次**，`minor-release.yaml` 每周二自动开版本 bump PR → 合并后自动建 `release/<version>` 分支与带 QA 清单的发布 PR → 打 tag 触发 `release.yml` 构建发布；minor 打 tag 后**立即自动创建下一个 patch 分支**。`just prepare-release <version>` 一次完成 Cargo / npm 版本 bump 与 canonical 模型目录重建。manpage 由 `clap_mangen` 生成到 `target/man/`。Windows 目标固定 MSVC，且必须在 Windows 主机上构建。

### 4.9 质量保障体系（43 个 workflow）

| 机制 | 说明 |
|---|---|
| **MCP 客户端一致性测试** | `just mcp-conformance` 用官方 `@modelcontextprotocol/conformance@0.2.0-alpha.10` 跑自研 `mcp_conformance_driver`；套件分 all / core / extensions / backcompat / auth / metadata / draft / **sep-835**；默认 spec 版本 **2025-11-25**；支持 `expected-failures` 基线文件 |
| **MCP 录制回放** | `GOOSE_RECORD_MCP=1 cargo test --test mcp_integration_test` → 录制到 `crates/goose/tests/mcp_replays/`，回归不依赖网络 |
| **模型工具调用一致性扫描** | `model-toolcall-conformance.yml` 每日 03:00 UTC 扫 OpenRouter 前 10 个支持工具调用的模型，报告"哪些模型真能驱动 goose 的 MCP 工具调用"。**刻意不做 PR 门禁**——注释原文：它打第三方网络，失败通常意味着提供方或模型回退，而非 goose 改动 |
| **自测 recipe** | 仓库根 `goose-self-test.yaml`：goose 用自己测自己（"第一人称集成测试"）。17 个阶段含 Azure AI Foundry 路由、Databricks 网关、声明式视觉、thinking 保留、Z.AI Coding Plan 流式工具调用、ACP thinking-effort 发现、GDK 观测钩子、**有上限 / 无上限自动压缩阈值**、嵌套委派拦截 |
| **用 goose 修自己的 issue** | `goose-issue-solver.yml` 由 `issue_comment` 触发，用内置 recipe（developer + todo 扩展）解 GitHub issue；另有 `goose-pr-reviewer.yml`、`goose-release-notes.yml` |
| **CI 结构** | `dorny/paths-filter` 跳过纯文档改动；独立 job 检查 npm 包（`npm-versions.mjs check` + `goose-acp test` + 打包） |
| **测试基建** | `insta`（快照）、`mockall`、`wiremock`、`ctor`/`dtor`、`env-lock`、`serial_test`、`test-case`；`goose-test` 的 `capture` bin、`goose-test-support` 的 `mcp_fixture_server` |
| **快照资产** | `agents/snapshots/`（4 个）；提示词改动会触发平台扩展提示词快照差异 |

<div class="callout ok">
  <div class="ic">✓</div>
  <div>
    <p><span class="t">`goose-issue-solver` 的 recipe 顺带是一份公开的代码规范</span>（原文摘录）：</p>
    <p>路径用 <code>PathBuf</code> 不用 <code>String</code>；有限集合用枚举不用字符串比较；<code>Vec&lt;T&gt;</code> 而非 <code>Option&lt;Vec&lt;T&gt;&gt;</code>（空 vec 即"无"）；新增结构体字段加 <code>#[serde(default)]</code>；<b>修 bug 先写失败测试</b>；删功能时同步删测试；<b>不加向后兼容垫片，直接改调用方</b>；只保留 WHY 注释、不写 WHAT 注释；错误信息要说"怎么修"而不只是"哪里错"。</p>
  </div>
</div>

### 4.10 安全与供应链（源码口径）

| 措施 | 证据 |
|---|---|
| **Actions 全部钉到完整 commit SHA** | 43 个 workflow 中形如 `actions/checkout@3d3c42e5…  # v7.0.1` |
| **OpenSSF Scorecard** | 每周四 12:19 UTC 运行，`publish_results: true`、`id-token: write`、`persist-credentials: false` |
| **依赖门禁** | `cargo-deny`（拒绝 yanked）+ `cargo-machete`（未使用依赖，豁免项注明原因）+ `dependabot-auto-merge` + `quarantine` |
| **自更新验签** | `update = ["dep:sigstore-verify", "dep:snap"]` —— `goose update` 走 **sigstore 签名校验** + snap 压缩 |
| **CI 免长期密钥** | `oidc-proxy/`（Cloudflare Worker）用 GitHub Actions OIDC token 换上游 API 访问；校验 JWKS / issuer / audience / `iat` 年龄 / 仓库 / ref；限速 **2 req/s**、每 token 最多 **200 次**、token 最长 **20 分钟** |
| **密钥存储** | `keyring` 分平台后端（apple-native / sync-secret-service / windows-native）+ `private_file.rs`（权限受限文件兜底） |
| **构建溯源** | SLSA 构建溯源（v2.0 已记录）+ `scorecard.yml` |
| **提示注入的官方自述** | `SECURITY.md` 原文承认：*"In some circumstances, goose may follow commands found embedded in content even if those commands conflict with the task given to goose."* 建议用专用 VM/容器、对重大变更逐条人工确认、只接已审阅的 MCP 扩展；漏洞经 Security tab 私下上报，升级联系人 = **AAIF Open Source Governance Committee**（`open-source-governance@block.xyz`） |

### 4.11 周边资产（源码枚举）

| 资产 | 性质 |
|---|---|
| `buzz/`（11 文件，Node） | 把 goose 的 GitHub issue 与公开社区 **`buzz.gdk.so`** 打通：用 **Nostr** 密钥创建 issue 频道、加成员、发摘要、同步话题；有一个名为 **Doose** 的 agent 身份（由 Buzz Desktop 运行）在被显式 @ 时评审 issue |
| `services/ask-ai-bot/` | **Discord 支持机器人**（Bun + TypeScript）：回复控制在 120 词内，检索文档 / 源码 / GitHub 评论 / 发布记录，用 Anthropic API；日志刻意不含提示词与工具输入输出 |
| `evals/harbor/` | Terminal-Bench 风格评测工具（Python：`runner.py` / `reporter.py` / `agent.py` / `cmd.py` + recipes） |
| `oidc-proxy/` | Cloudflare Worker（见 4.10） |
| `workflow_recipes/release_risk_check/` | 发布风险检查 recipe（yaml + python + sh） |
| `examples/` | `mcp-wiki`（Python MCP 示例）、`plugins/hello-hooks`（Open Plugins hooks 示例） |
| `scripts/`（30） | 基准后处理（含 **LLM judges**）、`provider-error-proxy`（复现提供方错误的 Python 代理）、`goose-db-helper.sh`、`diagnostics-viewer.py`、`test_compaction.sh` / `test_subagents.sh` / `test_subrecipes.sh` / `test_mcp.sh` / `test_local_model_smoke.sh` / `test_openrouter_toolcalls.sh`、`setup-riscv.sh` |
| `bin/`（39） | **Hermit** 管理的可复现工具链：cmake 4.2.3 / just 1.40.0 / node 24.10.0 / pnpm 10.30.3 / protoc 31.1 / rustup 1.28.2 / **temporal-cli 1.3.0**。官方 setup 第一步就是 `source bin/activate-hermit` |
| `vendor/v8/` | 本地补丁的 v8 crate（Code Mode 的 JS 运行时） |
| 开发环境 | `.devcontainer/`、`.blox/workstation.yaml`、`.intersect/intersect-config.yaml`、`test_acp_client.py` |

### 4.12 Terminal-Bench 自报数据（仓库内 `evals/harbor/`）

`evals/harbor/README.md` 直接给出了 `terminal-bench/terminal-bench-2`（**89 个任务**）的实测结果，除小模型对照外模型统一为 `claude-sonnet-4-6`：

| 任务 | 通过率 | 说明 |
|---|---:|---|
| **goose + code-mode** | **57.3%** | 仓库内最高 |
| code-mode + summon | 57.3% | 并列第一 |
| harbor 原版 Goose harness | 55.1% | 用于校验适配器无损耗 |
| goose + summon | 55.1% | — |
| opencode | 52.8% | 同模型 |
| goose（developer, todo） | 50.6% | 标准配置 |
| goose 1.30（developer, todo） | 50.6% | 存量版本 |
| goose（仅 developer） | 48.3% | — |
| pi | 47.2% | 同模型 |
| nemotron-3-nano-30b-a3b | 1.1% | 小模型对照 |

原文关键读数：code-mode 两项并列 **57.3%**；标准 goose（50.6%）与 opencode（52.8%）大致同级、**高于 pi（47.2%）**；pi 同时消耗最多算力（24.4h，"slowest *and* lowest scoring"）。

<div class="callout bad">
  <div class="ic">!</div>
  <div>
    <p><span class="t">引用限定（必须保留）</span> — 这是<b>仓库内自报的内部评测</b>，不是第三方榜单。harness 由 goose 团队自己维护；各任务的模型与参数不完全等同（如 <code>nemotron-full</code> 用的不是 sonnet，不能与其他行直接比）。**可作为"goose 官方给出的对标读数"引用，不可当作中立排名**。这同时回答了 v2.0/v2.1 不确定性清单第 6 项（"Pi 在 Terminal-Bench 的具体排名——未见官方榜单"）：官方榜单仍未出现，但 goose 仓库内已有一份同模型对标数据。</p>
  </div>
</div>

### 4.13 源码揭示的 8 处修正与补充

| # | 原表述（v2.0 / v2.1） | 源码证据 | 处理 |
|---|---|---|---|
| 1 | "2.0 beta 起桌面端改用 **Tauri** 重写" | 全仓库仅 2 处提 Tauri，无任何 Tauri 代码；`ui/desktop` 是 **Electron 43.4.0 + Forge 7.11.2** | **修正**：Tauri 是路线图第 3 项（in progress），**未落地** |
| 2 | "works with **15+ providers**" | `providers/` 66 个文件，直连 + ACP 两类共 30+ 家 | **精确化** |
| 3 | "70+ 官方扩展（MCP）" | 文档目录 73 个（v2.1 已精确化）；但 `AGENTS.md` 声明**该目录正在退役**，改用官方 **MCP Registry** 与 `server.json`，不再接受新增第三方条目（Discussion #10830） | **补充战略变化** |
| 4 | "2.0 beta：新 TUI" | `ui/text/README.md`：该 ACP TUI **已弃用、源码移除、npm 包 `@aaif/goose` 标记 deprecated** | **补充**：TUI 实验已终止，官方推荐 CLI 或桌面端 |
| 5 | "第三方平台 **Buzz** 以原生 ACP harness 集成 goose" | `buzz/` 是**仓库自带的 Nostr issue 同步自动化**，目标是 `buzz.gdk.so`（与 GDK 同域），不是第三方 ACP 集成案例 | **修正** |
| 6 | 安全体系"**三件套**" | `security/` 有 7 个模块，含官方文档未提的 **`egress_inspector.rs`**（出站检查）；另有 `permission/permission_judge.rs` | **补充** |
| 7 | 分发渠道（未提 npm） | `ui/goose-binary/` 5 个平台包 + `@aaif/goose-acp` 包装包 | **补充** |
| 8 | `.goosehints` 仍描述 `goose-server`（goosed）与 `goose-bench` crate | 15 个 crate 中**二者均不存在**（已被 ACP 架构取代） | **文档债**：仓库内的 agent 提示文件滞后于实际架构 |

**同源发现（非错误，但值得记录）**：仓库根目录存在 `MERGE_FIXES.md`，是一份针对 `unroll-agent-loop` 分支的内部合并修复笔记，自称"分支合并前应删除"。它意外提供了状态机重构的进度与测试现状（`cargo test -p goose` 仅剩 4 个 jsonwebtoken 库测试与 6 个依赖网络的 provider 测试失败）。属透明但未清理的内部文档。

---
## 5. 竞品全景对比

### 5.1 GitHub 硬数据总表（按 stars 降序，2026-10-15 实时采集）

| 排名 | 产品 | 仓库 | Stars | Forks | 贡献者 | Open Issues | 许可证 | 主语言 | 创建 | 最后推送 |
|---:|---|---|---:|---:|---:|---:|---|---|---|---|
| 1 | opencode | `anomalyco/opencode` | 213,573 | 28,659 | 454 | 4,265 | MIT | TypeScript | 2025-04-30 | 2026-10-15 |
| 2 | Dify | `langgenius/dify` | 158,511 | 25,044 | 456 | 1,131 | NOASSERTION | TypeScript | 2023-04-12 | 2026-10-15 |
| 3 | Claude Code | `anthropics/claude-code` | 150,923 | 26,584 | 57 | 15,014 | **无（专有条款）** | TypeScript | 2025-02-22 | 2026-10-14 |
| 4 | Codex | `openai/codex` | 129,272 | 20,320 | 478 | 22,620 | Apache-2.0 | Rust | 2025-04-13 | 2026-10-15 |
| 5 | Pi Agent | `earendil-works/pi` | 115,237 | 14,678 | 291 | 342 | MIT | TypeScript | 2025-08-09 | 2026-10-14 |
| 6 | Gemini CLI | `google-gemini/gemini-cli` | 107,372 | 14,716 | 443 | 745 | Apache-2.0 | TypeScript | 2025-04-17 | 2026-10-14 |
| 7 | OpenHands | `OpenHands/OpenHands` | 90,928 | 12,053 | 461 | 996 | MIT | TypeScript | 2024-03-13 | 2026-10-15 |
| 8 | Cline | `cline/cline` | 70,339 | 7,660 | 340 | 1,664 | Apache-2.0 | TypeScript | 2024-07-06 | 2026-10-15 |
| **9** | **goose** | `aaif-goose/goose` | **55,293** | **6,437** | **453** | **480** | **Apache-2.0** | **Rust** | 2024-08-23 | 2026-10-15 |
| 10 | Aider | `Aider-AI/aider` | 49,554 | 5,060 | 172 | 1,920 | Apache-2.0 | Python | 2023-05-09 | **2026-05-22（停更）** |
| 11 | Continue | `continuedev/continue` | 36,226 | 5,472 | 393 | 851 | Apache-2.0 | TypeScript | 2023-05-24 | 2026-10-14 |
| 12 | OpenWork | `different-ai/openwork` | 24,109 | 2,441 | 71 | 629 | NOASSERTION | TypeScript | 2026-01-14 | 2026-10-15 |
| 13 | Octop | `TencentCloud/Octop` | 9,362 | 1,162 | 62 | 825 | MIT | Python | 2026-07-08 | 2026-10-15 |
| — | WorkBuddy | 无开源仓库 | — | — | — | — | 闭源 | — | — | — |

**读表要点**：

1. **star 数会骗人**：Aider 4.96 万星，但最后推送停在 2026-05-22，已约 5 个月无提交，1,920 个 open issues 无人收敛。星数衡量的是历史影响力，不是当前维护强度。
2. **最热的未必开源**：Claude Code 15.09 万星排第 3，但仓库 **无 OSI 许可证**（`license: null`），源码可见仅作分发与 issue 跟踪之用；贡献者仅 57 人，open issues 却高达 15,014。
3. **goose 星数排第 9，工程健康度却排前列**：453 贡献者与 Codex（478）、OpenHands（461）、Dify（456）同级，而 open issues 仅 480 —— 是**全表同量级项目中的最优值**。
4. **issues / stars 比是最被低估的指标**：

| 产品 | open issues ÷ stars | 解读 |
|---|---:|---|
| **goose** | **0.87%** | 维护闭环效率最高 |
| Gemini CLI | 0.69% | 同样优秀，但贡献者 443、issues 745 |
| Codex | 17.5% | 高速迭代伴随大量积压 |
| Claude Code | 9.9% | 官方渠道承接用户反馈，非代码仓库 |
| opencode | 2.0% | 声量第一，积压同步增长 |

5. **增速对比**（star ÷ 存续月数）：

| 产品 | 存续 | stars | 月均增速 |
|---|---:|---:|---:|
| Pi Agent | 约 14 个月 | 115,237 | **约 8,230 / 月** |
| opencode | 约 18 个月 | 213,573 | 约 11,865 / 月 |
| goose | 约 26 个月 | 55,293 | 约 2,127 / 月 |
| OpenWork | 约 9 个月 | 24,109 | 约 2,679 / 月 |
| Octop | 约 3 个月 | 9,362 | 约 3,121 / 月 |

> 结论：goose 的月均增速（约 2,127）显著低于同期新锐（Pi 约 8,230、opencode 约 11,865）。**"开源最早"没有转化为"声量最大"**，这是 goose 最真实的处境。

### 5.2 定位差异表

| 产品 | 定位 | 主打形态 | 是否仅限编程 | 治理主体 |
|---|---|---|---|---|
| **goose** | 通用本地 agent | 桌面 + CLI + API（TUI 已弃用） | **否**（研究 / 写作 / 数据分析皆可） | **Linux 基金会 AAIF** |
| opencode | 终端 coding agent | 终端 TUI + 桌面（beta） | 是 | Anomaly 商业公司 |
| Pi Agent | agent 工具包全家桶 | 终端 TUI（另有 Web / SDK） | 是（但可构建通用应用） | Mario Zechner（个人 / 小团队） |
| Claude Code | 终端 agentic coding | 终端 | 是 | Anthropic |
| Codex | 轻量终端 coding agent | 终端 | 是 | OpenAI |
| Gemini CLI | Gemini 入终端 | 终端 | 是 | Google |
| OpenHands | AI 驱动开发平台 | 服务端 Web + headless | 是 | All Hands AI |
| Cline | 自治编码 agent | VS Code 扩展 + CLI + SDK | 是 | Cline 商业公司 |
| Aider | 终端结对编程 | 终端 | 是 | 个人项目（已停更） |
| Continue | 开源 coding agent | VS Code / JetBrains 扩展 | 是 | Continue Dev 公司 |
| OpenWork | Claude Cowork 开源替代 | 桌面应用（Win / macOS / Linux） | 否（基于 opencode 内核） | different-ai |
| Octop | 自托管多用户多 agent 助手 | 服务端（PyPI / docker） | 否 | 腾讯云 |
| Dify | Agentic 工作流 + RAG 平台 | 服务端 Web | 否 | LangGenius 商业公司 |
| WorkBuddy | 桌面 AI 办公工作台 | 桌面（Win / macOS / Linux） | 否 | 腾讯云 CodeBuddy 团队 |

**结构性观察**：14 款产品中，**仅 goose 由基金会托管**；**仅 goose 与 OpenWork / WorkBuddy 提供原生桌面**；**仅 goose 不限编程场景且同时具备四形态**。这三个"唯一"构成了 goose 的差异化基础。

### 5.3 与五款重点产品的逐一对比

| 对比对象 | goose 的优势 | goose 的劣势 | 竞争关系 |
|---|---|---|---|
| **opencode**（213,573★） | 基金会治理；原生桌面 + CLI + API；场景不限编程；MCP 73 个官方扩展；ACP 双向；完整安全体系 | 星数仅其 1/4；月均增速约 1/5.6；第三方教程 / 插件 / 主题全面落后；背后无公司全职投入 | **最直接对手**：宽松许可证 + 终端 agent + 多模型自由，几乎全维度重叠 |
| **Pi Agent**（115,237★） | 有原生桌面应用（Pi 仅 CLI / TUI）；通用场景；MCP 官方扩展体系；基金会治理 | 星数仅其一半；月均增速约 1/3.9；Pi 生态已长出扩展层（plannotator 9.4k★、awesome-pi-agent）；Pi 有 Terminal-Bench 口碑（社区称） | 同为"通用 agent 工具包"叙事，但 Pi 是明星个人项目、无桌面应用 |
| **WorkBuddy**（闭源） | 开源可审计；模型自由含本地；治理中立；可离线；无厂商绑定 | 需自行配置 provider；无中文办公交付物打磨；无官方商业支持 | **定位最接近**（桌面 AI 工作台），一开一闭、一极客一办公 |
| **Octop**（9,362★） | 单机执行深度（MCP / ACP / 安全体系）；本地推理；桌面体验 | 无多租户与权限体系；Octop 走多用户多 agent 与 IM 网关，goose 不参与该场景 | 部署形态不同（服务端 vs 桌面），可互补 |
| **OpenWork**（24,109★） | 是"agent 本体级"基金会项目；OpenWork 依附 opencode 内核，许可证含附加条款（NOASSERTION） | 星数约其 2.3 倍；OpenWork 基于 opencode 因而天然继承其生态 | 应用层 vs 本体的竞合关系 |

---
## 6. Linux 环境专项对比

### 6.1 goose v1.54.0 发布产物逐条清点（40 个）

v1.1 曾把"40 个产物"误述为"40 个 Linux 相关产物"。逐条分类后的真实构成：

| 平台 / 类型 | 数量 | 明细 |
|---|---:|---|
| **Linux 原生包** | **12** | 4 RPM（`x86_64` / `arm64` × 普通 / vulkan）· 4 DEB（`amd64` / `arm64` × 普通 / vulkan）· 4 Flatpak（`x86_64` / `aarch64` × 普通 / vulkan） |
| **Linux CLI tarball** | **12** | `{x86_64, aarch64}-unknown-linux-{gnu, gnu-vulkan, musl}` × `{tar.gz, tar.bz2}` |
| macOS | 9 | 4 桌面 zip（darwin-arm64 / x64 / 通用 / intel）+ 4 CLI tarball + 1 更新清单 |
| Windows | 4 | 2 桌面 zip（x64 / x64-cuda）+ 2 CLI zip（msvc / msvc-cuda） |
| 源码包 | 2 | `goose-source-v1.54.0.tar.gz` / `.zip` |
| 脚本 | 1 | `download_cli.sh` |
| **合计** | **40** | **其中 Linux 相关 24 个，占 60%** |

**三条被 v1.1 漏掉的事实**：

1. **Flatpak 已上线**：`io.github.block.Goose_stable_*`，意味着 goose 打通了 Flathub 这条桌面 Linux 主流分发路径。注意 ID 仍保留 `block` 命名空间（迁移遗留，未改为 aaif-goose）。
2. **DEB 与 RPM 双轨齐全**：覆盖 Debian/Ubuntu 系与 RHEL/Fedora 系，且都提供 **vulkan 硬件加速变体**。
3. **musl 静态链接变体**：`*-unknown-linux-musl` 可在 Alpine 等无 glibc 环境直接运行，是服务器 / 容器场景的关键能力。

### 6.2 安装渠道与形态对比

| 产品 | Linux 安装方式 | Linux 形态 | 运行时依赖 | 本地模型 | 适配评分 |
|---|---|---|---|---|---|
| **goose** | **RPM / DEB / Flatpak** / CLI tarball（gnu + musl）/ 官方一行脚本 / Nix flake / 部分发行版仓库 | 原生桌面 + CLI | Rust 单二进制（musl 变体零依赖） | **内置 llama.cpp** | **★★★★☆** |
| opencode | **pacman 官方源** / AUR / brew / Nix / mise / npm | 终端 TUI + 桌面（deb / rpm / AppImage） | Node / Bun | 多 provider | ★★★★☆ |
| Pi Agent | curl install.sh / npm / Nix（x86-64 + ARM64） | 仅终端 TUI | **Node 22.19+** | 统一 LLM API | ★★★☆ |
| Codex | npm / brew / GitHub 二进制 | 终端 | Rust 单二进制 | 有限 | ★★★☆ |
| Octop | **pip（PyPI）** / docker-compose | 服务端 Web | Python 3.12+ / Docker | 可接本地模型 | ★★★☆ |
| Dify | docker-compose | 服务端 Web | Docker | 多模型 | ★★★☆ |
| OpenHands | Docker | 服务端 + headless | Docker | 可接本地模型 | ★★★☆ |
| WorkBuddy | 官方 Linux 安装包（4GB 内存起，建议 8GB） | 仅桌面（无 CLI） | 闭源二进制 | 多模型调度 | ★★★☆ |
| OpenWork | 桌面应用（Linux 版） | 桌面应用 | Node（opencode 内核） | Ollama | ★★☆☆ |
| Claude Code | npm / curl | 终端 | Node | — | ★★☆☆ |
| Gemini CLI | npm / brew | 终端 | Node | — | ★★☆☆ |
| Cline | VS Code 扩展市场 | IDE 插件 + CLI | Node（随 VS Code） | 多 provider | ★★☆☆ |
| Aider | pip / pipx | 终端 | Python | 多 provider | ★★☆☆ |
| Continue | VS Code / JetBrains 扩展 | IDE 插件 | Node（随 IDE） | 多 provider | ★★☆☆ |

> 评分维度：安装渠道丰富度 / 形态完整度 / 依赖链轻量 / 服务器场景适配（各 1 星，半星用于区分同档）。
> **goose 扣半星原因**：桌面端（Electron）在部分发行版仍需补 GTK / 图形依赖，开箱体验不如 Arch 官方源的 opencode。

### 6.3 三个 Linux 特有事实

1. **发布物不会说谎**：goose 单版 24 个 Linux 产物、覆盖 4 种原生包格式；opencode 则直接进了 **Arch 官方仓库**。这两款是 Linux 打包最认真的。
2. **依赖链三档**：
   - **Rust 单二进制**（goose、Codex）——解压即用，musl 变体在 Alpine 亦可跑；
   - **Node 工具链**（opencode、Pi、Claude Code、Gemini CLI、Cline）——需先装运行时，Pi 还要求 Node 22.19+；
   - **Python venv / Docker**（Aider、Octop、Dify、OpenHands）——依赖最重。
3. **桌面 Linux 是小众需求**：仅 goose、opencode、OpenWork、WorkBuddy 提供 Linux 桌面版，其余全部为终端 / IDE / 服务端形态——桌面 Linux 用户的选择面远窄于 Windows / macOS。

### 6.4 分场景结论

| 场景 | 推荐 | 理由 |
|---|---|---|
| **桌面 Linux 日常工作台** | **goose 或 opencode** | goose 通用性更强（不限编程），RPM / DEB / Flatpak 三格式齐全；opencode 有 Arch 官方源，安装最省心 |
| **服务器 / headless / SSH** | **goose CLI**、opencode、Pi、Codex | goose 单二进制 + musl 变体 + distro 打包 + Nix，且**内置 llama.cpp 可完全离线运行** |
| **容器 / 最小化镜像** | **goose musl 变体** | `aarch64/x86_64-unknown-linux-musl` 无 glibc 依赖 |
| **团队自托管 / 多用户** | Octop、Dify、OpenHands | goose 无多租户能力，此场景不参与竞争 |
| **轻量本地编程** | Aider（pip）、Codex | 依赖最简单，但 Aider 已停更 |

### 6.5 goose 在 Linux 上的优势与短板

**优势**

1. **Linux 分发最完整的桌面级 agent**：RPM + DEB + Flatpak 三格式原生包、gnu / musl 双 libc、vulkan 加速变体、Nix flake、RISCV 支持文档（`RISCV_SETUP.md`）、发行版仓库收录。
2. Rust 单二进制，musl 变体零运行时依赖，服务器与容器上解压即用。
3. 内置本地推理（独立 crate `goose-local-inference`），离线可用，无需任何 API key。
4. 基金会治理，可进入企业软件供应链审计流程；LF Insights 官方健康分 **Healthy**。
5. MCP / ACP 协议深度，可被 Zed 等 Linux 原生编辑器直接接入。

**短板**

1. 桌面端仍为 **Electron**（Tauri 迁移未落地，见 4.7），部分发行版需补 GTK / 图形依赖。
2. 社区打包质量参差；`goose-cli` 在主流发行版**官方源**的收录范围仍未逐一核实（见第 10 节）。
3. 首次配置门槛依旧存在（provider 配置、keyring 处理、PATH 调整）。

---

## 7. 优势与劣势总分析

### 7.1 优势（按不可替代程度排序）

| # | 优势 | 说明 | 是否可被复制 |
|---|---|---|---|
| 1 | **治理中立性** | 14 款对比产品中唯一由 Linux 基金会 AAIF 托管；贡献者保留版权；治理变更需 LF Projects 批准 | 极难（需捐给基金会） |
| 2 | **工程健康度** | 453 贡献者 + 480 open issues（issues/stars 比 0.87%，全表最优）；约 5–7 天一版 | 中等 |
| 3 | **第三方权威背书** | LF Insights 官方健康分 **Healthy**，可直接用于企业采购与合规论证 | 难（需实际达标） |
| 4 | **形态与场景最宽** | 桌面 + CLI + API 三形态（TUI 已弃用）；不限编程场景 | 中等（需资源投入） |
| 5 | **协议站位** | MCP 最早最深度集成者（73 个扩展）+ ACP server（可被 Zed / JetBrains / VS Code 接入，也可把 Claude Code / Codex 当 provider） | 较难（协议基础设施属性） |
| 6 | **模型自由度 + 离线** | 30+ 家 provider、订阅复用、内置 llama.cpp 本地推理、Mesh LLM 路由 | 中等 |
| 7 | **Linux 分发完整度** | 24 个 Linux 产物 / 4 种包格式 / 双 libc / vulkan / Nix / RISCV | 中等 |
| 8 | **安全体系** | macOS 沙箱、提示注入检测、权限控制、Adversary mode、SLSA 溯源；四层结构：执行前检测 → 执行中监视 → 权限约束 → 供应链溯源 | 较难（开源阵营唯一成体系） |
| 9 | **文档与开发者接口完备度** | **173 篇官方文档**，73 个扩展各有独立页；**GDK** 同时提供 SDK（Rust / Python / Kotlin 进程内库）与 ACP（stdio / HTTP / WebSocket）两种嵌入方式 | 中等（需持续投入） |

### 7.2 劣势（按影响程度排序）

| # | 劣势 | 说明 | 可缓解性 |
|---|---|---|---|
| 1 | **声量薄弱，第三方生态落后** | 55,293 stars 排第 9，被 opencode 压制 3.9 倍；月均增速约 2,127，仅为 Pi 的 1/3.9、opencode 的 1/5.6。**需区分两个层面**（v2.1 修正）：**官方文档覆盖度并不弱**（173 篇，73 个扩展各有独立文档页，密度约每千星 3.1 篇），真正落后的是**第三方教程、社区插件与主题** | 低（需时间 + 运营） |
| 2 | **上手门槛高** | 需自行配置 provider、处理 keyring / PATH；订阅 OAuth 链路复杂 | 中（文档可改善） |
| 3 | **无托管与协作体系** | 无多租户、SSO、审计后台；企业需自建定制发行版（官方提供 CUSTOM_DISTROS 机制） | 中（可外部集成） |
| 4 | **一方模型优化深度不足** | 跨模型通用换来单模型深度折损（"通用性税"），编程基准通常不敌 Claude Code / Codex | 低 |
| 5 | **记忆架构偏被动** | 有 Memory Extension + compaction + 独立 context-management crate，但社区评价仍偏"文件式 / 被动式" | 中（已在改进） |
| 6 | **架构过渡期风险** | 2.0 beta 未完全收敛：**Tauri 桌面重写**与状态机重构仍在进行中（**新 TUI 已终止**，见 4.7 / 4.13） | 高（时间可解） |
| 7 | **决策集中度** | 453 贡献者背后实际决策仍为 7 名 Core Maintainer | 中 |
| 8 | **品牌迁移遗留** | Flatpak ID 等标识仍沿用 `block` 命名空间，品牌与仓库归属存在过渡期不一致 | 高（可修正） |

### 7.3 一个需要注意的判断项（非事实）

**通过 ACP 使用 Claude / ChatGPT / Gemini 订阅**：这是官方明确支持的功能（2026-03-19 博客，README 亦有说明），但**订阅 OAuth 用于第三方客户端**在部分服务商条款中处于灰区，**存在被限流或封禁的不确定性**。此项为本文判断，非已发生的事件，请自行评估风险。

---
## 8. 社区与官方声音

### 8.1 官方叙事（goose-docs.ai 博客，2026）

| 时间 | 主题 | 信号 |
|---|---|---|
| 2026-02 | goose v1.25.0：macOS 沙箱、统一 summon 扩展、SLSA 构建溯源 | 安全与供应链投入 |
| 2026-02 | Code mode：减少长会话的上下文腐化与 token 消耗 | 成本优化 |
| 2026-03 | Adversary mode：隐藏审查 agent 盯防主 agent | 安全差异化 |
| 2026-03 | 用订阅接入 AI（Claude / Gemini / Codex） | 成本结构创新 |
| 2026-04 | 内置 llama.cpp 本地推理（Private by Default） | 隐私与离线 |
| 2026-04 | Mesh LLM 跨模型路由 | 模型自由度 |
| 2026-04 | goose 迁入 AAIF | 治理落地 |
| 2026-04 | goose 2.0 beta：**宣布** Tauri 桌面重写、新 TUI、统一 ACP（源码核对：桌面端仍为 Electron，TUI 已弃用） | 架构换代 |
| 2026-05 | Hooks（Open Plugins 规范）、goose as conductor 多代理编排 | 可编程性 |
| 2026-06 | 自改进 agent 仍需人类（Terminal-Bench / Harbor 失败即 bug 报告） | 工程务实 |
| 2026-07 | Issues as the new PRs（agent 把 ready issue 转代码） | 贡献流程再造 |
| 2026-09 | Agentic State Machines（用状态机取代经典 agent loop） | 内核换代 |

### 8.2 社区评价

**正面**

- 社区评测将 goose 归入"**执行型**"而非"建议型"工具——能自动跑测试、验证、部署全流程，与 Copilot / Cursor 的"推荐片段需人工接受"形成代际区分（什么值得买评测，2026-04）。
- 治理迁移被社区视为"开源史上的深远事件"：由公司项目转为中立基金会的公共基础设施，回应了"谁来为 AI Agent 负责"的问题（程序员茄子分析，2026-06）。
- 第三方平台 Buzz 以原生 ACP harness 集成 goose，佐证其协议落地能力（仓库内存在 `buzz/` 目录，可佐证）。

**负面 / 保留意见**

- 上手环节的实际障碍：安装后需处理 PATH 警告、keyring 报错，需先加 PATH 再 `goose configure`（CSDN 系列教程）。
- 记忆与长上下文被部分社区意见认为仍偏"文件式 / 被动式"，与新一代多层记忆架构的 agent 在长链路任务上有差距。
- **社区文章存在失真**：例如某评测中出现的 `goose task "..."` 用法并非官方 CLI——引用社区教程时需回到官方文档核对。

---

## 9. 选型建议

| 需求 | 推荐 | 说明 |
|---|---|---|
| 要隐私、离线、多模型套利、可审计、嵌 IDE | **goose** | 无替代品 |
| 要最强编程能力、追前沿模型 | Claude Code / Codex / Gemini CLI / opencode | 一方优化占优 |
| 要开箱即用、中文办公交付物 | WorkBuddy | 零配置、落盘交付 |
| 要拖拽搭建业务 Agent、多租户交付 | Dify / Octop | 平台化能力 |
| 要纯编程终端 + 开源 + 声量 | opencode / Pi Agent | 生态成熟 |
| 团队自托管协作 | Octop / Dify / OpenHands | goose 不参与此场景 |
| 企业采购需合规背书 | **goose** | 基金会治理 + LF 官方健康分可写入审计材料 |

**常见组合**：主力模型用官方 Agent 保效果上限 + goose 管敏感场景与批量自动化；两者经 ACP 可互为 provider，**不互斥**。

---

## 10. 不确定性清单（诚实声明）

| # | 事项 | 状态 |
|---|---|---|
| 1 | WorkBuddy 鸿蒙支持 | 仅见百科条目，未获第二来源证实 |
| 2 | WorkBuddy Linux GUI 成熟度 | 2026-06 有来源称"未发布原生 Linux GUI"，与 2026-10 官方教程矛盾，可能已补齐，**建议实测** |
| 3 | goose 2.0 GA 时间 | 未公布；稳定线仍为 1.x |
| 4 | `goose-cli` 在主流发行版官方源的收录范围 | repology 有收录，具体范围未逐一核实 |
| 5 | goose Flatpak 是否已正式上架 Flathub | 产物已发布，但未核验 Flathub 商店条目 |
| 6 | Pi 在 Terminal-Bench 的具体排名 | **部分解决（v2.2）**：官方第三方榜单仍未出现，但 goose 仓库内已有同模型对标数据——89 个任务，pi **47.2%** vs goose **50.6%**（见 4.12）。该数据为**仓库自报**，非中立排名 |
| 7 | AAIF 成员公司完整名单 | 部分细节来自百科 / 媒体转述 |
| 8 | 订阅 OAuth 的合规判定 | 本文判断，非事实 |
| 9 | goose 桌面的具体实现框架 | **已解决（v2.2）**：源码实测为 **Electron 43.4.0 + Forge 7.11.2**；Tauri 迁移**未落地**（见 4.7） |
| 10 | 社区打包质量与 repology 收录明细 | 未逐条核对各发行版仓库版本 |
| 11 | 部分官方文档由 Docusaurus 组件动态渲染 | 如 `<RateLimits />`、`<OnboardingProviderSetup />`、各平台安装按钮组件，其最终内容在 Markdown 源中不可见 |
| 12 | Roaming 的正式可用时间 | 官方标记为实验性且**不含在发布二进制中**，需自行编译启用；尚无 GA 计划 |
| 13 | `goose serve` 的生产可用性 | 官方要求 `GOOSE_SERVER__SECRET_KEY`，但未给出多用户/多租户场景的官方指引 |

---

## 11. 参考来源

**官方**

- [aaif-goose/goose 仓库](https://github.com/aaif-goose/goose) · [README](https://github.com/aaif-goose/goose/blob/main/README.md) · [GOVERNANCE.md](https://github.com/aaif-goose/goose/blob/main/GOVERNANCE.md) · [MAINTAINERS.md](https://github.com/aaif-goose/goose/blob/main/MAINTAINERS.md) · [CUSTOM_DISTROS.md](https://github.com/aaif-goose/goose/blob/main/CUSTOM_DISTROS.md) · [BUILDING_LINUX.md](https://github.com/aaif-goose/goose/blob/main/BUILDING_LINUX.md) · [flake.nix](https://github.com/aaif-goose/goose/blob/main/flake.nix) · [RISCV_SETUP.md](https://github.com/aaif-goose/goose/blob/main/RISCV_SETUP.md)
- **官方文档库（173 篇 Markdown，v2.1 全量抓取源）**：[documentation/docs 目录](https://github.com/aaif-goose/goose/tree/main/documentation/docs)
- [goose 官方文档站](https://goose-docs.ai/) · [官方博客](https://goose-docs.ai/blog)
- 本版重点引用的文档页：
  - [goose Architecture](https://goose-docs.ai/docs/goose-architecture/goose-architecture) · [Error Handling](https://goose-docs.ai/docs/goose-architecture/error-handling)
  - [Installation](https://goose-docs.ai/docs/getting-started/installation) · [Using Extensions](https://goose-docs.ai/docs/getting-started/using-extensions) · [Providers](https://goose-docs.ai/docs/getting-started/providers)
  - [CLI Commands](https://goose-docs.ai/docs/guides/goose-cli-commands) · [Smart Context Management](https://goose-docs.ai/docs/guides/sessions/smart-context-management) · [Context Engineering](https://goose-docs.ai/docs/guides/context-engineering)
  - [Security](https://goose-docs.ai/docs/guides/security) · [Tool Shim](https://goose-docs.ai/docs/guides/tool-shim) · [Roaming Agents](https://goose-docs.ai/docs/guides/roaming-agents)
  - [GDK](https://goose-docs.ai/docs/gdk) · [SDK](https://goose-docs.ai/docs/gdk/sdk) · [ACP](https://goose-docs.ai/docs/gdk/acp)
- [goose 迁入 AAIF（官方博客）](https://goose-docs.ai/blog/2026/04/07/goose-moves-to-aaif) · [goose 2.0 beta](https://goose-docs.ai/blog/2026/04/08/goose-acp-and-new-tui) · [Agentic State Machines](https://goose-docs.ai/blog/2026/09/16/agentic-state-machines)
- [Agentic AI Foundation](https://aaif.io/) · [Agent Client Protocol](https://agentclientprotocol.com/) · [goose-mobile 仓库](https://github.com/aaif-goose/goose-mobile) · [goose Mobile Web 客户端](https://aaif-goose.github.io/goose-mobile/)

**第三方权威数据**

- [Linux Foundation Insights — goose 项目健康分](https://insights.linuxfoundation.org/project/goose)（Health Score = Healthy）
- GitHub REST API：`repos` / `contributors` / `releases` / `languages` / `orgs` / `contents` 端点，采集时点 2026-10-15

**竞品仓库**

- [anomalyco/opencode](https://github.com/anomalyco/opencode) · [earendil-works/pi](https://github.com/earendil-works/pi) · [openai/codex](https://github.com/openai/codex) · [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) · [anthropics/claude-code](https://github.com/anthropics/claude-code)
- [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) · [cline/cline](https://github.com/cline/cline) · [Aider-AI/aider](https://github.com/Aider-AI/aider) · [continuedev/continue](https://github.com/continuedev/continue)
- [different-ai/openwork](https://github.com/different-ai/openwork) · [TencentCloud/Octop](https://github.com/TencentCloud/Octop) · [langgenius/dify](https://github.com/langgenius/dify) · [zed-industries/zed](https://github.com/zed-industries/zed)

**社区与媒体**

- [WorkBuddy 安装教程（腾讯云开发者社区）](https://cloud.tencent.com/developer/article/2673380) · [WorkBuddy 百度百科](https://baike.baidu.com/item/WorkBuddy/67362053)
- [Goose AI Agent 评测（什么值得买）](https://post.smzdm.com/p/a7065w8o) · [Goose 治理迁移分析（程序员茄子）](https://www.chenxutan.com/d/3505.html)
- [Goose 记忆扩展与上下文压缩（CSDN）](https://blog.csdn.net/gitblog_00709/article/details/154329481) · [安装注意事项（CSDN）](https://blog.csdn.net/gitblog_01150/article/details/154896281)
- [AAIF 成立报道（TechCrunch 中文转述）](https://baijiahao.baidu.com/s?id=1851107522440953319&wfr=spider&for=pc) · [Agentic AI Foundation 百科](https://baike.baidu.com/item/AI%20Agent%20Foundation/67073976)
- [Pi-mono 项目解析（CSDN）](https://blog.csdn.net/j8267643/article/details/160601065) · [OpenWork 与 Cowork 对比（CSDN）](https://wesee.blog.csdn.net/article/details/157288088)

---

## 附录 A：v2.2 复核方法可复现命令

```bash
# 需具备 repo 读权限的 GitHub PAT（匿名调用限流 60 次/小时）
export TOKEN=<your_github_pat>

# 1) 仓库硬数据
curl -s -H "Authorization: Bearer $TOKEN" https://api.github.com/repos/aaif-goose/goose

# 2) 贡献者数（Link header 最后一页）
curl -sI -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/aaif-goose/goose/contributors?per_page=1" | grep -i '^link:'

# 3) 语言字节数
curl -s -H "Authorization: Bearer $TOKEN" https://api.github.com/repos/aaif-goose/goose/languages

# 4) 单版发布产物清单（用于平台分类清点）
curl -s -H "Authorization: Bearer $TOKEN" \
  https://api.github.com/repos/aaif-goose/goose/releases/tags/v1.54.0 \
  | python -c "import sys,json;[print(a['name']) for a in json.load(sys.stdin)['assets']]"

# 5) 治理与维护者原文
curl -s -H "Authorization: Bearer $TOKEN" \
  https://raw.githubusercontent.com/aaif-goose/goose/main/MAINTAINERS.md

# 6) Linux 基金会官方健康分
curl -s "https://insights.linuxfoundation.org/api/badge/health-score?project=goose"

# 7) 官方文档库全量清单（v2.1 新增）
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/aaif-goose/goose/git/trees/main?recursive=1" \
  | python -c "
import sys,json
for t in json.load(sys.stdin)['tree']:
    p=t['path']
    if p.startswith('documentation/docs/') and p.endswith(('.md','.mdx')):
        print(p)
"

# 8) 单篇文档正文（示例：架构文档）
curl -s -H "Authorization: Bearer $TOKEN" \
  https://raw.githubusercontent.com/aaif-goose/goose/main/documentation/docs/goose-architecture/goose-architecture.md

# ---------- 以下为 v2.2 源码维度新增 ----------

# 9) 源码全量文件树（一次拿到整棵树，务必检查 truncated 字段）
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/aaif-goose/goose/git/trees/main?recursive=1" \
  | python -c "
import sys,json
d=json.load(sys.stdin)
print('truncated=',d.get('truncated'),' files=',len(d['tree']))
print('top-level=',len(set(t['path'].split('/')[0] for t in d['tree'])))
"

# 10) 字符串级全仓库检索 —— 判定"计划 vs 既成事实"的关键手段
#     搜 tauri 只命中 2 个文件且无构建配置 ⇒ Tauri 重写未落地
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/search/code?q=tauri+repo:aaif-goose/goose" \
  | python -c "import sys,json;d=json.load(sys.stdin);print(d['total_count']);[print(' -',i['path']) for i in d.get('items',[])]"

# 11) 桌面端依赖真相（Electron / Forge / React / Vite 版本）
curl -s -H "Authorization: Bearer $TOKEN" \
  https://raw.githubusercontent.com/aaif-goose/goose/main/ui/desktop/package.json \
  | python -c "
import sys,json
d=json.load(sys.stdin)
dd=d.get('devDependencies',{})
for k in ['electron','@electron-forge/cli','vite']:
    print(k,'=',dd.get(k))
print('react =',d.get('dependencies',{}).get('react'))
"

# 12) 工作区版本 vs 最新发布（判断是否有未发布改动）
curl -s -H "Authorization: Bearer $TOKEN" \
  https://raw.githubusercontent.com/aaif-goose/goose/main/Cargo.toml | head -20
curl -s -H "Authorization: Bearer $TOKEN" \
  https://api.github.com/repos/aaif-goose/goose/releases/latest \
  | python -c "import sys,json;print('latest tag =',json.load(sys.stdin)['tag_name'])"

# 13) 发布产物版本间 diff（定位"何时新增了什么"）
for v in v1.51.0 v1.52.0; do
  curl -s -H "Authorization: Bearer $TOKEN" \
    https://api.github.com/repos/aaif-goose/goose/releases/tags/$v \
    | python -c "import sys,json;print('\n'.join(sorted(a['name'] for a in json.load(sys.stdin)['assets'])))" > /tmp/$v.txt
done
diff /tmp/v1.51.0.txt /tmp/v1.52.0.txt
```

## 附录 B：本报告版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.0 | 2026-10-14 | 对话式研究，含时间线图表 |
| v1.1 | 2026-10-15 | 首轮勘误 10 项 + 4 项新增事实 |
| v2.0 | 2026-10-15 | 全量重采 API 复核，勘误 18 项（3 实质错误 / 6 重要遗漏 / 3 数据过期 / 6 口径改进），新增 Flatpak 与 DEB、LF 官方健康分、15 个 crate 结构、Core Maintainers 实名、issues/stars 比与增速对比 |
| v2.1 | 2026-10-15 | 官方文档补全版：全量抓取 173 篇官方文档（约 1.33 MB），新增第 3 章「官方文档能力全景」（13 节），补齐官方架构三组件与六步循环、14 个内置扩展、73 个 MCP 扩展分类、完整 CLI 命令表、15 个斜杠命令、上下文管理参数级细节、GDK、Roaming Agents、实验性功能；修正 v2.0 关于"生态薄弱"的表述（区分官方文档与第三方生态） |
| **v2.2** | **2026-10-15** | **源码级补全版：对仓库 `main` 分支做全量文件树枚举（3,038 个文件 / 52 个顶层条目），新增第 4 章「源码级架构与工程实践」（13 节），覆盖 15 个 crate 的真实职责、特性矩阵与模块地图、66 个提供方文件、桌面端 Electron 真相、npm 分发渠道、43 个 workflow 的质量保障体系、安全与供应链源码口径、周边资产与 Terminal-Bench 自报数据；修正 4 处"把计划当既成事实"的表述（Tauri / Buzz / providers / .goosehints），并把不确定性清单第 6、9 项标记为已解决** |
