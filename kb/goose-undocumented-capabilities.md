---
id: goose-undocumented-capabilities
title: goose 源码有、官方文档未介绍的重要能力（33 项实证清单）
tags:
  - goose
  - source-code
  - documentation-gap
  - reverse-engineering
  - cli
  - environment-variables
  - cargo-features
created: 2026-10-16
updated: 2026-10-16
version: 1.0
status: stable
source: goose 源码 main 分支（2534 blob 快照 2026-10-16）+ 195 个关键源码文件逐行核对 + 官方文档库 311 个文件全文检索
confidence: 已核实
---

# goose 源码有、官方文档未介绍的重要能力

## 一句话结论

对 goose 源码（`aaif-goose/goose` main，2534 文件）与官方文档（311 个 `.md`/`.mdx`）做**逐项交叉核对**，发现 **33 项能力在源码中确实存在、官方文档完全未提及**：4 个内置斜杠命令（`/goal` `/grind` `/status` `/doctor`）、2 个隐藏 CLI 命令（`validate-extensions` `mcp-probe`）、1 个完整功能模块（实时语音 `live_voice`）、**17 个未公开的环境变量/配置键**、**7 个未公开的 Cargo feature**（含 CUDA/MLX/Vulkan GPU 加速）、2 项内部机制。

---

## 1. 汇总表

| # | 能力 | 类型 | 源码证据 | 文档命中 |
|---|---|---|---|---|
| 1 | **实时语音交互 `live_voice`** | 功能模块 | `crates/goose/src/live_voice/` 7 文件（service/interaction/transcript） | 0 |
| 2 | **`/goal`** 斜杠命令 | CLI | `agents/execute_commands.rs:43` | 0 |
| 3 | **`/grind`** 斜杠命令 | CLI | `agents/execute_commands.rs:47` | 0 |
| 4 | **`/status`** 斜杠命令 | CLI | `agents/execute_commands.rs:52` | 0 |
| 5 | **`/doctor`** 斜杠命令 | CLI | `agents/execute_commands.rs:39` | 0 |
| 6 | `goose validate-extensions` | CLI（隐藏） | `cli.rs:1199` `hide = true` | 0 |
| 7 | `goose mcp-probe` | CLI（隐藏） | `cli.rs:1209` `hide = true` | 0 |
| 8 | `GOOSE_MAX_ACTIVE_AGENTS` | 配置键 | `config/base.rs:1335` | 0 |
| 9 | `GOOSE_ADDITIONAL_CONFIG_FILES` | 配置键 | `config/base.rs:176` | 0 |
| 10 | `GOOSE_DEFAULT_EXTENSION_TIMEOUT` | 配置键 | `config/base.rs:1421` | 0 |
| 11 | `GOOSE_TOOL_PAIR_SUMMARIZATION` | 配置键 | `context_mgmt/mod.rs:46` | 0 |
| 12 | `GOOSE_SLASH_COMMANDS_ENABLED` | 配置键 | `execute_commands.rs:5` | 0 |
| 13 | `GOOSE_PROVIDER_SKIP_BACKOFF` | 配置键 | `agents/reply_parts.rs:385` | 0 |
| 14 | `GOOSE_OAUTH_AUTOMATIC_CALLBACK` | 配置键 | `oauth/mod.rs:90` | 0 |
| 15 | `GOOSE_SYSTEM_PROMPT_FILE_PATH` | 配置键 | `cli/session/builder.rs:630` | 0 |
| 16 | `GOOSE_LIVE_VOICE` / `GOOSE_LIVE_VOICE_ENABLED` | 配置键 | `live_voice/service.rs:22` | 0 |
| 17 | `GOOSE_TELEMETRY_OFF` | 配置键 | `cli/commands/configure.rs` | 0 |
| 18 | `GOOSE_MCP_OAUTH_CLIENT_ID` / `_CLIENT_SECRET` / `_CLIENT_METADATA_URL` | 配置键 | `cli.rs` | 0 |
| 19 | `GOOSE_CA_CERT_PATH` / `GOOSE_CLIENT_CERT_PATH` / `GOOSE_CLIENT_KEY_PATH` | 配置键 | `config/tls.rs` | 0 |
| 20 | `GOOSE_APP_TYPE` / `GOOSE_SCHEMA_CONTEXT` | 常量 | `goose_apps/app.rs:35` | 0 |
| 21 | `GOOSE_HINTS_FILENAME` | 常量 | `hints/load_hints.rs:10` | 0 |
| 22 | feature `cuda` | Cargo | `goose/Cargo.toml` | 0 |
| 23 | feature `mlx` | Cargo | `goose/Cargo.toml` | 0 |
| 24 | feature `vulkan` | Cargo | `goose/Cargo.toml` | 0 |
| 25 | feature `tree-sitter`（9 语言） | Cargo | `goose/Cargo.toml` | 0 |
| 26 | feature `platform-apps` | Cargo | `goose/Cargo.toml` | 0 |
| 27 | feature `acp-http` | Cargo | `goose/Cargo.toml` | 0 |
| 28 | feature `online-model-meta` | Cargo | `goose/Cargo.toml` | 0 |
| 29 | `execution` 模块（多并发会话） | 内部机制 | `execution/manager.rs` 26 KB | 0 |
| 30 | OTel W3C trace context（MCP SEP-414） | 内部机制 | `otel/trace_context.rs` | 0 |
| 31 | `GOOSE_NU_PREEXEC_INSTALLED` | 配置键 | `cli/commands/term.rs` | 0 |
| 32 | `GOOSE_ROAM_RELAY_TOKEN` | 配置键 | `cli/commands/roam.rs` | 0 |
| 33 | `GOOSE_RECIPE_GITHUB_REPO_CONFIG_KEY` / `GOOSE_RECIPE_PATH_ENV_VAR` / `GOOSE_SERVER_SECRET_KEY_ENV` / `GOOSE_MCP_CLIENT_VERSION` | 配置键 | `configure.rs` / `recipe/local_recipes.rs` / `cli.rs` / `agents/mcp_client.rs` | 0 |

> **"文档命中 0"的判定口径**：在 `documentation/docs/**` 与 `documentation/blog/**` 全文（311 文件）中做字面检索，命中数为 0。排除仅出现在仓库内部文件（如 `MERGE_FIXES.md`）的情况。

---

## 2. 功能与命令缺口（最值得关注）

### 2.1 四个未公开的内置斜杠命令（`agents/execute_commands.rs`）

源码里内置命令表的原文（`static COMMANDS: &[CommandDef]`）：

| 命令 | 源码描述 | 为什么重要 |
|---|---|---|
| `/goal` | Set a goal the agent must satisfy before finishing, or clear with `/goal off` | **目标约束机制**：给 agent 设一个"完成前必须满足"的目标，让它自我校验后再结束。文档只讲了 Recipe 和 RPI，没讲这个更轻量的手段 |
| `/grind` | Set a goal the agent pursues relentlessly until max_turns, or clear with `/grind off` | **持续冲刺模式**：与 `/goal` 同源但语义更强——不达目标不罢休，直到 `max_turns`。是"长任务不中断"的原生开关 |
| `/status` | Show session status: model, provider, mode, and token usage | 会话内直接看 model / provider / 权限模式 / **token 用量**——比 `/compact` 或日志更直接 |
| `/doctor` | Check that your Goose setup is working | 环境自检；`goose doctor` 命令就是"开一个会话并执行 `/doctor`"（`commands/doctor.rs` 仅 15 行） |

其余 5 个内置命令（`/prompts` `/prompt` `/compact` `/clear` `/skills`）文档已覆盖。

**相关常量**：`COMPACT_TRIGGERS = ["/compact", "Please compact this conversation", "/summarize"]` —— 即"请压缩这段对话"和 `/summarize` 是 `/compact` 的**自然语言别名**，文档未提。

### 2.2 两个隐藏 CLI 命令

| 命令 | 源码 | 用途 |
|---|---|---|
| `goose validate-extensions <file>` | `cli.rs:1199`，`hide = true` | 校验 `bundled-extensions.json` 的格式 |
| `goose mcp-probe <extension> [--script PATH\|-]` | `cli.rs:1209`，`hide = true` | **不启动 LLM**，直接起一个 goose MCP 会话去探测 stdio MCP server（可喂 JSON 探测脚本）。调试自研 MCP server 时比拉满 goose 会话快得多 |

### 2.3 实时语音模块 `live_voice`（文档零提及）

- 路径：`crates/goose/src/live_voice/`（7 文件）
- 关键类型：`LiveVoiceService`、`WebRtcOffer`、`LiveVoiceInteractionCompletion`、`LiveVoiceTranscriptPublisher`
- 约束常量：`LIVE_VOICE_INPUT_MESSAGE_LIMIT = 128`、`LIVE_VOICE_INPUT_TOKEN_LIMIT = 8192`
- 开关：feature `live-voice`（**在 `goose-cli` 的 `default` 里，即默认编译进二进制**）+ 配置键 `GOOSE_LIVE_VOICE_ENABLED` / `GOOSE_LIVE_VOICE`
- 依赖：`goose-providers/live-websocket`

**注意**：文档里的 "voice dictation"（`guides/sessions/in-session-actions.md`）是**语音听写**（说完转文字），与 `live_voice` 的**实时语音交互**（WebRTC 双向）是两回事。听写有文档，实时语音没有。

---

## 3. 环境变量 / 配置键缺口（17 组）

goose 的配置键既能写进 `config.yaml`，也能用同名环境变量覆盖（`config_value!` 宏）。以下键文档未列。

| 键 | 源码位置 | 作用 | 备注 |
|---|---|---|---|
| `GOOSE_MAX_ACTIVE_AGENTS` | `config/base.rs:1335` | 同时活跃的 agent 数量上限 | 并发会话治理的关键旋钮 |
| `GOOSE_ADDITIONAL_CONFIG_FILES` | `config/base.rs:176` | 追加配置文件列表（按 `env::split_paths` 解析，即系统 PATH 分隔符） | 多环境配置叠加 |
| `GOOSE_DEFAULT_EXTENSION_TIMEOUT` | `config/base.rs:1421` | 扩展默认超时（`u64`） | 慢 MCP server 必备 |
| `GOOSE_TOOL_PAIR_SUMMARIZATION` | `context_mgmt/mod.rs:46` | 对「工具调用+结果」成对做摘要，**默认 false** | 上下文压缩的另一种策略 |
| `GOOSE_SLASH_COMMANDS_ENABLED` | `execute_commands.rs:5` | 斜杠命令总开关，**默认 true** | 收紧交互面时用 |
| `GOOSE_PROVIDER_SKIP_BACKOFF` | `agents/reply_parts.rs:385` | 首个 item 前失败重试时跳过退避等待 | 调试 provider 时提速 |
| `GOOSE_OAUTH_AUTOMATIC_CALLBACK` | `oauth/mod.rs:90` | 启用 OAuth 自动回调（无该环境变量则直接返回 None） | 无头/容器环境 |
| `GOOSE_SYSTEM_PROMPT_FILE_PATH` | `cli/session/builder.rs:630` | 用文件内容**覆盖系统提示词**（比 prompts 目录更硬） | 强定制 |
| `GOOSE_LIVE_VOICE` / `GOOSE_LIVE_VOICE_ENABLED` | `live_voice/service.rs:22` | 实时语音开关 | 见 2.3 |
| `GOOSE_TELEMETRY_OFF` | `cli/commands/configure.rs` | 关闭遥测 | 合规场景 |
| `GOOSE_MCP_OAUTH_CLIENT_ID` / `_CLIENT_SECRET` / `_CLIENT_METADATA_URL` | `cli.rs` | MCP server 的 OAuth 客户端凭据 | 远程 MCP 鉴权 |
| `GOOSE_CA_CERT_PATH` / `GOOSE_CLIENT_CERT_PATH` / `GOOSE_CLIENT_KEY_PATH` | `config/tls.rs` | **企业 mTLS 客户端证书三件套** | 文档 0 命中，企业部署必用 |
| `GOOSE_APP_TYPE` / `GOOSE_SCHEMA_CONTEXT` | `goose_apps/app.rs:35` | GooseApp 的 schema 标识（`application/x-goose-prd`、`urn:goose.ai:schema`） | MCP App 生态 |
| `GOOSE_HINTS_FILENAME` | `hints/load_hints.rs:10` | 提示文件名常量（`.goosehints`）；同文件还有 `AGENTS_MD_FILENAME = "AGENTS.md"` | 说明 **`AGENTS.md` 与 `.goosehints` 同级被识别** |
| `GOOSE_NU_PREEXEC_INSTALLED` | `cli/commands/term.rs` | `goose term` 的 nushell preexec 安装标记 | `goose term` 内部 |
| `GOOSE_ROAM_RELAY_TOKEN` | `cli/commands/roam.rs` | Roaming 中继令牌 | iroh P2P |
| `GOOSE_RECIPE_GITHUB_REPO_CONFIG_KEY` / `GOOSE_RECIPE_PATH_ENV_VAR` / `GOOSE_SERVER_SECRET_KEY_ENV` / `GOOSE_MCP_CLIENT_VERSION` | `configure.rs` / `recipe/local_recipes.rs` / `cli.rs` / `agents/mcp_client.rs` | Recipe 仓库来源、Recipe 搜索路径、server 密钥、MCP 客户端版本 | 分散的配置点 |

---

## 4. Cargo feature 缺口（7 个）

`crates/goose/Cargo.toml` 的 `[features]` 共 20 个；`crates/goose-cli/Cargo.toml` 共 24 个。**`goose-cli` 的 `default` 已启用 16 个**：

```
code-mode, tree-sitter, local-inference, aws-providers, telemetry, otel,
rustls-tls, live-voice, system-keyring, update, bundled-mcp, scheduler,
platform-apps, chat-recall, acp-http, online-model-meta
```

文档未提及的 feature：

| feature | 含义 | 为什么重要 |
|---|---|---|
| **`cuda`** | `local-inference` + `candle-core/cuda` | **NVIDIA GPU 加速本地推理** |
| **`mlx`** | `local-inference` + `goose-providers/mlx` | **Apple Silicon GPU 加速**（Mac 用户首选） |
| **`vulkan`** | `local-inference` + `goose-providers/vulkan` | **跨平台 GPU 加速**（AMD/Intel） |
| **`tree-sitter`** | 9 个语言文法：go / java / javascript / kotlin-ng / python / ruby / rust / swift / typescript | 代码结构感知（AST 级分析）的基础；**在 default 里** |
| `platform-apps` | `goose_apps` 模块（MCP App 抓取/缓存/CSP/权限） | MCP App 生态；在 default 里 |
| `acp-http` | `agent-client-protocol-http` | ACP over HTTP/WebSocket；在 default 里 |
| `online-model-meta` | 在线拉取模型元数据 | 模型列表与能力信息 |

**另有两个构建预设值得记**：
- `portable-default`：精简构建（**不含** `local-inference` / `system-keyring` / `update` / `bundled-mcp`）—— 无 GPU、无钥匙串、无自更新的可移植版本
- `disable-update`（goose-cli）：**编译期禁用 `goose update` 命令**

---

## 5. 内部机制缺口（2 项）

| 项 | 证据 | 说明 |
|---|---|---|
| `execution` 模块 | `crates/goose/src/execution/mod.rs`：`//! Unified execution management for Goose agents` + `manager.rs` 26 KB + `ActiveRunRegistry` | **统一执行管理**：会话隔离，支持多个并发会话各自持有独立的 agent / extensions / provider。这是"多会话并发"的底层设施，文档只在会话管理层面描述现象 |
| OTel W3C trace context | `crates/goose/src/otel/trace_context.rs`：`//! W3C trace context carried in ACP and MCP _meta (MCP SEP-414 keys)` | 链路追踪上下文通过 ACP / MCP 的 `_meta` 字段透传，遵循 **MCP SEP-414**。做分布式可观测时是关键协议细节 |

---

## 6. 核查方法（可复用）

```bash
# 1) 拿全仓库文件树（含 size），一次调用
GET https://api.github.com/repos/aaif-goose/goose/git/trees/main?recursive=1

# 2) 按模块定位「文档会写但没写」的区域：看 src 下的一级子目录清单
#    crates/goose/src/ = agents(97) providers(66) acp(48) config(23) session(19)
#                        + live_voice(7) dictation(6) plugins(6) slash_commands(6)
#                        + gateway(5) goose_apps(5) execution(3) otel(3) oauth(3)
#                        + scheduler(3) hints(3) checks(1) context_mgmt(1) hooks(1)

# 3) 抓关键文件（本方法用了 195 个 / 3.67 MB），逐项提取：
#    - 内置斜杠命令：agents/execute_commands.rs 的 static COMMANDS
#    - CLI 子命令：cli.rs 的 enum Command / enum *Command（含 hide = true）
#    - 配置键：config/base.rs 的 config_value!(KEY, Type) 宏调用
#    - feature：各 Cargo.toml 的 [features] 段 + default 列表

# 4) 与文档做字面检索对比（documentation/docs/** + documentation/blog/**）

# 本仓库脚本：_verify/scan_src.py → fetch_src_key.py → gap_src_docs.py → gap_cli.py → gap_final.py
```

**关键判据**：`config_value!(KEY, Type)` 宏是配置键的权威清单；`enum Command` 里带 `hide = true` 的是**故意隐藏**的命令；`[features] default = [...]` 说明该能力**默认已编译进二进制**（所以"没文档但能用"）。

---

## 7. 未核实项

| 项 | 说明 |
|---|---|
| `/goal` / `/grind` 的实际行为细节 | 只读到命令描述与调用点，未逐行追踪 `max_turns` 交互、目标校验失败时的重试语义 |
| `live_voice` 的可用入口 | 源码有完整模块且默认编译，但**未确认 Desktop / CLI 是否有 UI 入口**，可能只在特定构建/实验开关下可达 |
| `GOOSE_MAX_ACTIVE_AGENTS` 默认值 | 声明为 `config_value!(GOOSE_MAX_ACTIVE_AGENTS, usize)`，未找到默认常量，实际默认值待确认 |
| GPU feature 的实测效果 | `cuda` / `mlx` / `vulkan` 只验证了 feature 依赖声明，未实测推理速度 |
| `platform-apps` 与 `MCP Apps` 文档的关系 | 文档有 MCP Apps 页（标注 experimental），但未提 `platform-apps` feature 名，两者是否同一能力未确认 |

---

## 修订记录

- **1.0**（2026-10-16）：首次沉淀。基于源码 2534 文件快照 + 195 个关键文件逐行核对 + 311 个文档文件全文检索，产出 33 项「源码有、文档无」实证清单。
