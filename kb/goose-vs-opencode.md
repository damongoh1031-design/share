---
id: goose-vs-opencode
title: goose vs opencode 全面对比（2026-10-16 数据）
tags:
  - goose
  - opencode
  - ai-agent
  - comparison
  - benchmark
  - capability-mapping
created: 2026-10-16
updated: 2026-10-16
version: 1.0
status: stable
source: GitHub API（2026-10-16）+ goose 源码 2534 blob + opencode v1.19.2 6634 blob + 两侧官方文档全文
confidence: 已核实
---

# goose vs opencode 全面对比

## 一句话结论

两者都是开源 coding agent，但**路线完全不同**：opencode 是 **TypeScript 生态的「广度派」**（213,953★ / MIT / 18 语言官方文档 / 34 个 npm 包 / 7 个内置 agent / 13 个内置工具），goose 是 **Rust 生态的「深度派」**（55,293★ / 15 个 crate / 173 页英文文档 / 14 个内置扩展 / MCP 协议深度整合）。**选 opencode 要生态广度与本地化，选 goose 要 Rust 性能与企业级扩展控制。**

---

## 1. 基本面对照（2026-10-16，GitHub API 实测）

| 项 | goose | opencode | 差 |
|---|---|---|---|
| 仓库 | `aaif-goose/goose` | `anomalyco/opencode` | — |
| Stars | **55,293** | **213,953** | 3.87× |
| Forks | ~2,900 | **28,720** | 9.9× |
| Open issues | 480 | **4,316** | 9.0× |
| License | Apache-2.0 | **MIT** | MIT 更宽松 |
| 主语言 | **Rust（71.6%）** | **TypeScript（81.4%）** | — |
| 创建时间 | 2025-01-28 | **2025-04-30** | goose 早 3 个月 |
| 最近推送 | 2026-10-16 | 2026-10-16 | 都活跃 |
| 仓库体积 | ~52 MB | **576 MB** | 11× |
| 文件数（blob） | 2,534 | **6,634**（v1.19.2） | 2.6× |
| 默认分支 | `main` | `dev`（2.0 开发线） | — |
| 当前稳定版 | v1.54.0 | **v1.19.2**（2026-10-16） | 双版本轨 |
| Discussions | 无 | 无 | — |

> opencode 有 **OpenCode 1 / OpenCode 2 双线**：`dev` 分支是 v2（未发布，含 `gui-extensions` 等新包），`v1.19.x` 是稳定线。两者**不能共存安装**（同名 `opencode` 命令）。

---

## 2. 架构对照

| 维度 | goose | opencode |
|---|---|---|
| 语言栈 | Rust 15 crate + TS 23.5%（Electron 桌面） | **TypeScript 32 包**（monorepo） |
| 核心包 | `goose`(447 文件) / `goose-providers`(87) / `goose-cli`(53) / `goose-mcp`(43) | `core`(781) / `ai`(690) / `ui`(1651) / `app`(835) / `web`(649) / `tui`(509) / `desktop`(356) / `cli`(204) |
| 桌面端 | Electron 43 + Forge + React 19 + Vite 8 | **`packages/desktop`**（TS 原生） |
| TUI | `ui/text`（已弃用 npm 包）/ `goose term`（nushell） | **`packages/tui`**（509 文件，原生 TS） |
| Web | 无独立 web app | **`packages/web`**（文档站 + web UI，Astro） |
| SDK | GDK：Rust / Python / Kotlin（UniFFI） | **`@opencode/sdk` + `sdk-next`**（npm，TS） |
| 协议 | MCP + **ACP**（Agent Client Protocol，48 文件）+ Roaming（iroh P2P） | **ACP**（原生，19 文件）+ `acp` CLI 命令 |
| 特色模块 | `goose-context-management` / `goose-local-inference` / `goose-roaming` | `codemode` / `plugin-browser` / `merman` / `http-recorder` / `simulation` / `containers` |

**结论**：opencode 前端资产重（ui/app/web/tui/desktop 5 个包占 4,006 文件），goose 后端资产重（核心 crate 447 文件）。

---

## 3. 文档覆盖对照（本次全量核查）

| 项 | goose | opencode |
|---|---|---|
| 英文文档页 | **173 页**（`documentation/docs/`） | **36 页**（`packages/web/src/content/docs/`） |
| 官方中文 | **无**（`locales: ["en"]`，无 i18n） | **有 zh-cn + zh-tw** |
| 文档语言 | 1（仅英文） | **18 种**（ar/bs/da/de/es/fr/it/ja/ko/nb/pl/pt-br/ru/th/tr/zh-cn/zh-tw + en） |
| 多语言合计 | — | **614 页** |
| 文档站 | Docusaurus | **Astro + Starlight** |
| 文档正文总量 | 1,351,256 B | 36 页（单页更深，如 cli.mdx 27,504 B） |
| 术语表 | 无官方 | **`.opencode/glossary/` 18 语言**（翻译用） |
| 自举文档 | 无 | `.opencode/` 45 文件（agent 2 / command 8 / skills 8 / tool 2 / themes / plugins） |

**结论**：**goose 文档深度胜出（173 页 vs 36 页，4.8×），opencode 本地化广度胜出（18 语言 vs 1）**。对中文用户，opencode 是唯一有官方中文的。

---

## 4. 能力面对照

| 维度 | goose | opencode | 备注 |
|---|---|---|---|
| **内置工具** | 14 个 MCP 扩展（Developer/Apps/Code Mode/Memory/Todo/Knowledge Graph/Fetch/PDF…） | **13 个内置工具**（bash/edit/write/read/grep/glob/lsp/apply_patch/skill/todowrite/webfetch/websearch/question） | 模型不同：goose 走 MCP，opencode 内置 |
| **内置 agent** | 无独立 agent 概念，靠 Recipe/subagent | **7 个内置 agent**：build / plan / general / **explore** / **scout** / **compaction** / **title** / **summary** | opencode 把常见角色固化为 agent |
| **扩展机制** | MCP server + Plugin（`plugins/` 容器） | **Plugin（npm 包）+ MCP server + 自定义工具（TS 函数）** | opencode 扩展面更宽 |
| **自定义工具** | 需写 MCP server | **直接 TS 函数**（`tool/` 目录，见 `.opencode/tool/*.ts`） | opencode 门槛低 |
| **Skills** | `~/.agents/skills/<name>/SKILL.md`（无 GUI） | `.opencode/skills/*/SKILL.md`（**8 个内置**） | 两者格式相同 |
| **Hooks** | **11 个事件**（SessionStart/SessionEnd/Stop/UserPromptSubmit/PreToolUse/PreToolUseResult/PostToolUse/PostToolUseFailure/BeforeReadFile/AfterFileEdit/BeforeShellExecution/AfterShellExecution），仅 PreToolUse + Stop 可阻断 | 文档未见独立 hooks 概念（用 plugin 实现） | **goose 独有** |
| **斜杠命令** | 15+（含 `/compact` `/model` `/mode` `/extension`…） | **`.opencode/command/*.md`**（8 个内置：ai-deps/changelog/commit/issues/learn/rmslop/spellcheck/translate） | 都支持 Markdown 定义 |
| **Recipe / 工作流** | **Recipe YAML**（完整字段参考 + 子 Recipe + 并行 + 站点 Recipe 库 67 个） | 无独立 Recipe 概念（靠 agent + command 组合） | **goose 独有** |
| **权限模型** | 4 种模式（auto/approve/smart_approve/chat）+ 三级工具权限 + `allowlist` | **`permission` 字段**（allow/deny/ask + 通配符 + task permissions） | opencode 更细粒度 |
| **多模型** | 30+ provider（直连 + ACP），subagent 各自 provider+model | provider 配置 + 每 agent 独立 model/temperature/top_p | opencode 采样参数更全 |
| **上下文管理** | Context Revision 四项机制 + `min(80%, 225000)` + `GOOSE_CONTEXT_STRATEGY` | **`compaction` agent**（专职压缩）+ `experimental` 段 | opencode 用 agent 化 |
| **RAG / 知识库** | **无向量 RAG**（替代：Memory/Knowledge Graph/Chat Recall/Repomix/Context7/Analyze） | **`references` 配置**（按仓库/路径挂外部知识，如 `effect-smol`） | 思路不同 |
| **渲染** | md/html/pdf(读)/图表（Auto Visualiser 8 类） | `latex` / `merman`（Mermaid）包 | opencode 有 LaTeX |
| **CLI 子命令** | **21 顶层**（含 session/recipe/schedule/gateway/review/term/roam/doctor…） | v1.19.2 **4 顶层**（api/debug/service/serve）+ 文档列 20+ | goose CLI 面更广 |
| **配置 schema** | 14 个 `config_value!` 键（宏） | **独立 `@opencode/schema` 包**（21 个子 schema + `$schema` 校验 + 对外发布） | opencode 更工程化 |
| **环境变量** | 79 个（含 33 未文档化） | 文档列 12 个 `OPENCODE_*` | goose 更多 |
| **企业特性** | `adversary mode` / 提示注入检测 / `allowlist` / mTLS（`GOOSE_CA_CERT_PATH` 等） | `enterprise` 配置段 + `policies` 文档页 | 两者都有 |

---

## 5. 未文档化能力对照（同方法源码考古）

| | goose | opencode v1.19.2 |
|---|---|---|
| 源码文件 | 195 个（3.67 MB） | 193 个（749 KB） |
| 发现「源码有、文档无」 | **33 项** | 本次未做同等深度考古（仅确认 schema 与 CLI 均完备文档化） |
| 代表 | `/goal` `/grind` `/status` `/doctor`、`live_voice`、17 组配置键、`cuda/mlx/vulkan` | 待补 |

> opencode 的 `@opencode/schema` 包**本身就是配置的权威清单**（Effect Schema + `$schema` 发布），文档与源码一致性高于 goose（后者靠 `config_value!` 宏，无 schema 输出）。

---

## 6. 社区与生态

| 项 | goose | opencode |
|---|---|---|
| 生态仓库 | `awesome-opencode` 10,607★ 等（opencode 侧） | **`awesome-opencode` 10,607★** / `opencode.nvim` 3,888★ / `oh-my-opencode-slim` 9,567★ |
| 认证插件 | 无（原生 provider） | `opencode-gemini-auth` 1,767★ / `opencode-openai-codex-auth` 2,214★ |
| 自举使用 | 无公开配置 | **`.opencode/` 45 文件**（用自己开发自己） |
| 基金会 | **LF Insights 健康分 = Healthy**（Linux 基金会背书） | 无（个人/公司项目） |
| 治理 | GOVERNANCE.md + 7 位 Core Maintainer | 无公开治理文件 |

---

## 7. 选型建议

| 你的需求 | 推荐 |
|---|---|
| 中文文档 / 多语言团队 | **opencode**（唯一有官方中文） |
| Rust / 性能 / 单二进制 | **goose** |
| 企业级权限、审计、提示注入防护 | **goose**（adversary mode + allowlist + mTLS） |
| 扩展生态（MCP 已达 73 个） | **goose** |
| 写自定义工具要快（TS 函数） | **opencode** |
| 需要 LaTeX / Mermaid 渲染 | **opencode** |
| 需要工作流编排（Recipe + 子 Recipe） | **goose**（opencode 无此概念） |
| 需要 Hooks 生命周期控制 | **goose**（11 事件） |
| 前端/桌面/Web 三端一致 | **opencode**（web + desktop + TUI 同栈） |
| Python/Kotlin SDK | **goose**（GDK 三语言） |
| TypeScript SDK | **opencode**（npm） |

---

## 8. 可复用操作

```bash
# 采集任意仓库基本面 + 文件树
GET https://api.github.com/repos/<owner>/<repo>
GET https://api.github.com/repos/<owner>/<repo>/git/trees/<branch>?recursive=1

# opencode 分支（注意 main 404，用 2.0/dev 或具体 tag）
GET https://api.github.com/repos/anomalyco/opencode/git/trees/v1.19.2?recursive=1

# 本仓核对脚本
_verify/fetch_opencode.py          # 元数据 + 树
_verify/fetch_opencode_files.py    # dev 线文件
_verify/fetch_oc_v1192.py          # v1.19.2 文件
_verify/oc_subcmd.py               # CLI 子命令提取
_verify/oc_docs.py                 # 文档结构统计
```

---

## 9. 坑与反直觉

| # | 坑 | 说明 |
|---|---|---|
| 1 | **opencode 的 `main` 分支不存在（404）** | 主开发分支叫 `dev`，另有 `2.0` 分支；稳定线是 `v1.19.x` tag。按 `main` 抓会失败 |
| 2 | **opencode 有双版本且不能共存** | OpenCode 1 与 2 共用 `opencode` 命令名。`dev`/`2.0` 分支含 `gui-extensions` 等 v1 没有的包，**对比时必须锁定 tag** |
| 3 | **opencode 文档统计易重复** | `packages/web/src/content/docs/` 下按语言分目录（`zh-cn/` 等），同名页 18 份。按文件名去重会得到 578（错），按路径层级判断才是 36 |
| 4 | **opencode 用 `effect/cli` 而非 clap** | 命令定义是 `Spec.make("name", {...})`，正则提取子命令要按缩进分层级，不能按 `#[command]` 找 |
| 5 | **opencode v1.19.2 的 commands.ts 只有 4 个顶层子命令** | 其余命令（agent/auth/mcp/run/session…）在 `cli.mdx` 文档里但不在 `commands.ts`——**文档比源码列得多**（与 goose 相反，goose 是源码 21 个、文档 24 小节） |
| 6 | **stars 与代码质量无关** | opencode 213,953★ vs goose 55,293★，但 goose 有 LF 健康分背书 + 7 位 core maintainer 治理文件，opencode 无公开治理文档 |
| 7 | **体积 11× 不等于功能 11×** | opencode 576 MB 里 4,006 文件是前端（ui/app/web/tui/desktop），核心逻辑 `core` 781 文件 |

---

## 10. 未核实项

| 项 | 说明 |
|---|---|
| opencode 未文档化能力 | 未做与 goose 同等深度的源码考古（33 项级别），仅确认 schema/CLI 文档化完整 |
| opencode 贡献者精确数 | GitHub contributors API 首页即满 100（分页上限），未翻页取总数 |
| opencode 的 4,316 open issues 质量分布 | 未分析 issue 构成（feature request / bug / support） |
| goose 4,320 vs opencode 28,720 forks 的活跃度 | 仅取数未分析 fork 活跃度 |
| opencode Hooks 是否存在 | 文档未见，但 plugin 体系可能提供等价能力，未逐行核实 plugin 源码 |
| goose 的 Web UI | goose 无独立 web app，但 `goose serve` 提供 ACP over HTTP；未核实是否有配套前端 |

---

## 修订记录

- **1.0**（2026-10-16）：首次对比。基于 GitHub API + 两侧源码树（goose 2534 blob / opencode v1.19.2 6634 blob）+ 两侧官方文档全文，覆盖 9 个维度。
