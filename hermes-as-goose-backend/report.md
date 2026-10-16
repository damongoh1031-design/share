# Hermes Agent 作为 goose 的后端运行时 / 模型：可行路径与双方配置

> 调研日期：2026-10-16 ｜ 方法：本机源码取证（Hermes 完整源码 + goose 上游源码）+ 双方官方文档交叉验证
> 本机环境：Windows 11；Hermes Agent 已安装（`C:\Users\Admin\AppData\Local\hermes\`）；goose 未安装

---

## 结论速览

**「Hermes 作为 goose 的后端」不是一个功能，而是四条不同路径**。goose 的源码里用 `RUNS_OWN_TOOL_LOOP` 这个常量把「模型」和「运行时」严格区分开，所以必须先选定你要哪一种。

| # | 路径 | 传输协议 | 谁跑工具循环 | 双方原生支持？ |
|---|------|---------|-------------|--------------|
| A | **Hermes 当模型**：`hermes proxy` → goose 自定义 provider | OpenAI Chat Completions | **goose**（用 goose 的扩展） | ✅ 双方文档都覆盖 |
| B | **Hermes 当智能体后端**：Hermes API server → goose 自定义 provider | OpenAI Chat Completions | **Hermes**（用 Hermes 的工具） | ✅ 双方文档都覆盖 |
| C | **Hermes 当运行时**：`hermes acp` ← goose ACP provider | ACP over stdio | **Hermes**（goose 扩展可透传） | ❌ **goose 侧不支持任意 ACP agent**（唯一缺口） |
| D | **Hermes 当 MCP 扩展**：`hermes mcp serve` → goose extension | MCP over stdio | goose 跑，Hermes 作为工具被调用 | ✅ 双方原生支持 |

**一句话答案**：
- 想要「用 Hermes 的订阅/模型，但保留 goose 的扩展和会话管理」→ **走 A**，`hermes proxy start` 即可，十分钟能跑通。
- 想要「让 Hermes 真正作为 goose 的执行后端（含 Hermes 的记忆/技能/工具）」→ **走 B**，Hermes 的 API server 就是一个 OpenAI 兼容的「智能体即模型」端点。
- 想要 goose 官方 ACP provider 那种「goose 把扩展当 MCP server 透传给后端 agent」的**运行时委托**语义 → **goose 目前做不到**，因为它的 ACP provider 是 5 个写死的 adapter（C 路径，见下文变通办法）。

---

## 0. 先厘清两个词：「模型」vs「运行时」

goose 源码里这个区分是硬编码的，不是文案差异：

`crates/goose/src/providers/base.rs` 的 `ProviderDef` trait 有两个常量：

```rust
impl ProviderDef for ClaudeAcpProvider {
    type Provider = AcpProvider;
    const SESSION_BOUND: bool = true;
    const RUNS_OWN_TOOL_LOOP: bool = true;   // ← 后端 agent 自己跑工具循环
}
```

对比声明式 custom provider（`provider_registry.rs::register_with_name_impl`）里：

```rust
session_bound: false,
runs_own_tool_loop: false,   // ← goose 自己跑工具循环
```

所以：
- **「模型」** = goose 自己跑 agent loop，把工具 schema 发给模型，模型只返回 tool_call。
- **「运行时」** = 后端（此处是 Hermes）自己跑完整 loop，goose 退化成一个会话前端；goose 会把它的扩展当作 **MCP server** 通过 `session/new` 传给后端 agent。

---

## 1. 路径 A：Hermes 当 goose 的**模型**（推荐先做这个）

### 原理
Hermes 自带 `hermes proxy` —— 一个"订阅代理"：

> Run a local HTTP server that forwards OpenAI-compatible requests to an OAuth-authenticated provider (e.g. Nous Portal). External apps can point at the proxy with any bearer token; the proxy attaches your real credentials.
> — `hermes proxy --help`（本机实测）

Hermes 文档把它定位为"给外部 app 用你的订阅当 LLM 端点"，全文不涉及 agent loop，是纯凭证透传（`website/docs/user-guide/features/subscription-proxy.md`）。

### Hermes 侧配置

```powershell
# 1) 一次性登录（Nous Portal 或 xAI）
hermes portal

# 2) 起代理（默认 127.0.0.1:8645）
hermes proxy start
#   Listening on:  http://127.0.0.1:8645/v1
#   Use any bearer token in the client — the proxy attaches your real credential.

# 3) 可选：确认上游就绪
hermes proxy status
hermes proxy providers      # 目前只有 nous / xai 两个 upstream adapter
```

模型名用 Nous 侧的，如 `Hermes-4-70B` / `Hermes-4.3-36B` / `Hermes-4-405B`。
代理只放行 `/v1/chat/completions`、`/v1/completions`、`/v1/embeddings`、`/v1/models`，其余 404。
**无自身认证**：任何 bearer 都接受；`--host 0.0.0.0` 会让整个局域网白嫖你的订阅。

### goose 侧配置

两种写法，二选一（别混用）：

**写法 1：直接用内置 OpenAI provider（最快）**

```powershell
$env:GOOSE_PROVIDER = "openai"
$env:OPENAI_HOST = "http://127.0.0.1:8645"     # 只到 root，不带路径
$env:OPENAI_API_KEY = "sk-unused"              # 任意非空值，代理会忽略并换成真凭证
$env:GOOSE_MODEL = "Hermes-4-70B"
goose session
```
`OPENAI_BASE_PATH` 默认就是 `v1/chat/completions`，不用改。

**写法 2：建一个自定义 provider（可命名、可多端点切换）**

goose 的声明式 custom provider 是**每个 provider 一个 JSON 文件**，位置由源码确认：

```
<goose config_dir>/custom_providers/<id>.json
→ Windows: %APPDATA%\Block\goose\config\custom_providers\hermes_proxy.json
```
（`crates/goose/src/config/declarative_providers.rs::custom_providers_dir()`）

```json
{
  "name": "custom_hermes_portal",
  "engine": "openai",
  "display_name": "Hermes Portal (proxy)",
  "base_url": "http://127.0.0.1:8645/v1/chat/completions",
  "models": [{ "name": "Hermes-4-70B", "context_limit": 128000 }],
  "requires_auth": true,
  "api_key_env": "HERMES_PROXY_KEY"
}
```

`engine` 只支持 `openai` / `anthropic` / `ollama` 三种。**API key 不能写在 config.yaml 里**（goose 会忽略并报 `No api key passed in`），要用 `goose configure` 走 keychain，或用显式环境变量。

图形界面路线：goose Desktop → Settings → Models → Configure providers → **Add Custom Provider** → Provider Type 选 `OpenAI Compatible`，API URL 填 `http://127.0.0.1:8645/v1/chat/completions`。

### 这条路径的取舍
- ✅ goose 的全部扩展（70+ MCP）、会话、recipe、subagent 全部照常工作。
- ✅ 不需要任何 API key / 按 token 付费，走你的订阅额度。
- ❌ Hermes 的记忆、技能、工具**完全用不上**——它在这里只是一块"模型"。
- ❌ 速率限制是整个代理共享一份订阅额度，不池化、不并发扩容。

---

## 2. 路径 B：Hermes 当 goose 的**智能体后端**（API server）

### 原理
Hermes 有一个容易被忽略的独立能力：**API server**，把 agent 本身暴露成 OpenAI 兼容端点。

> The API server exposes hermes-agent as an OpenAI-compatible HTTP endpoint. Any frontend that speaks the OpenAI format — Open WebUI, LobeChat, LibreChat … — can connect to hermes-agent and use it as a backend. **Your agent handles requests with its full toolset (terminal, file operations, web search, memory, skills) and returns the final response.**
> — `website/docs/user-guide/features/api-server.md`

对比表（同一份文档里 Hermes 自己给的划分）：

| | API server | Subscription proxy |
|---|---|---|
| 它提供什么 | **你的 agent**（完整工具集、记忆、技能） | 裸模型推理 |
| 用途 | "把 Hermes 当聊天后端" | "把订阅给别的 app 用" |
| Tool calls | **是——agent 自己跑工具** | 否——纯透传 |

这正是用户问的"**运行时**"形态：Hermes 是后端那个干活的人。

### Hermes 侧配置

```powershell
# 1) 写入 ~/.hermes/.env（本机为 C:\Users\Admin\AppData\Local\hermes\.env）
API_SERVER_ENABLED=true
API_SERVER_KEY=<自己设一个长随机串>

# 2) 启动（API server 挂在 gateway 上）
hermes gateway
#   [API Server] API server listening on http://127.0.0.1:8642

# 3) 自测
curl http://localhost:8642/v1/chat/completions `
  -H "Authorization: Bearer <key>" -H "Content-Type: application/json" `
  -d '{"model":"hermes-agent","messages":[{"role":"user","content":"Hello!"}]}'
```

关键端点：
- `POST /v1/chat/completions`（有状态化套件，含 `X-Hermes-Session-Id` 续会话）
- `POST /v1/responses`（Responses API，`previous_response_id` 服务端存历史）
- `GET /v1/models`（把 agent 本身列为模型，名字 = profile 名，默认 `hermes-agent`）
- `GET /v1/capabilities`（机器可读能力清单，含 `reasoning_streaming: true`）
- 流式里会额外发 `event: hermes.tool.progress`，可被严格 OpenAI 客户端用 `tool_progress_events: false` 关掉

模型名默认就是 `hermes-agent`（多 profile 时是 profile 名，如 `alice`）。
`/v1/chat/completions` 的裸 `model` 值**默认为被忽略**（除非开 `gateway.platforms.api_server.direct_model_requests: true`），明确带 `provider` 字段才会生效——goose 只会发裸 `model`，所以要么保持默认走 Hermes 全局默认模型，要么打开这个开关。

### goose 侧配置

```json
{
  "name": "custom_hermes_agent",
  "engine": "openai",
  "display_name": "Hermes Agent",
  "base_url": "http://127.0.0.1:8642/v1/chat/completions",
  "models": [{ "name": "hermes-agent", "context_limit": 200000 }],
  "requires_auth": true,
  "api_key_env": "HERMES_API_SERVER_KEY"
}
```
`HERMES_API_SERVER_KEY` 的值 = 你上面设的 `API_SERVER_KEY`。

### 这条路径的取舍
- ✅ Hermes 完整能力（终端、文件、记忆、技能、subagent）都在后端生效，goose 变成"好看的前端 + 会话/recipe 编排"。
- ✅ 一次配置，Open WebUI / LobeChat 等同源客户端可共用同一端口。
- ⚠️ **`/v1/chat/completions` 是"agent 即模型"**：goose 会把它的扩展工具 schema 一起发过去，而 Hermes 的 API server 文档中没有"执行调用方传入的 tools"的承诺——**goose 的扩展在这条路径上实际不会被执行**，工具全由 Hermes 侧自己的工具集完成。
- ⚠️ 双重人格风险：goose 的系统提示会把 goose 的规则叠加到 Hermes 的核心 system prompt 之上（文档明说 layering），两边都以为自己是主控。给 goose 的 system prompt 建议保持极简。
- ⚠️ 安全：`API_SERVER_KEY` 是必需的（文档有单独 warning 块），因为它等于把带 `terminal` 的 agent 暴露出去。

---

## 3. 路径 C：Hermes 当 goose 的**运行时**（ACP）—— 唯一不支持的一环

这是用户问题里"运行时"最字面的答案，也是唯一卡住的地方。**结论：goose 目前不能把任意 ACP agent 注册成 provider。**

### 现状取证

**Hermes 侧完全就绪**，它有一个标准 ACP server：

```powershell
hermes acp          # 等价 hermes-acp / python -m acp_adapter
hermes acp --check  # 依赖自检
hermes acp --version
```
- 日志走 stderr，stdout 留给 ACP JSON-RPC。
- 暴露 `SessionModelState`（模型选择器，条目 id 形如 `provider:model`，如 `openrouter:z-ai/glm-5.1`）与 edit-approval 的 `SessionModeState`。
- 会话可持久化、可 resume/fork（`website/docs/user-guide/features/acp.md`）。
- Hermes 文档已经把"被别的 ACP host 拉起"当成一级场景，并列了 **Buzz / VS Code / Zed / JetBrains** 的接入方式，还专门定义了 host 侧该注入的环境变量 `HERMES_ACP_SKIP_CONFIGURED_MCP=1`（让 host 自己通过 `session/new` 传 MCP，跳过 Hermes 的全局 MCP 启动）。

**goose 侧是封闭集合**（`crates/goose/src/providers/inventory/registrations.rs` 逐一登记）：

| goose provider id | binary 名（写死在源码） | `model_config_option_id` | `session_mode_id` |
|---|---|---|---|
| `claude-acp` | `claude-agent-acp` | `Some("model")` | 有（bypassPermissions/default/acceptEdits/plan） |
| `codex-acp` | `codex-acp` | 动态模型发现 | 有 |
| `amp-acp` | `amp-acp` | **None** | 有（bypass/default） |
| `pi-acp` | `pi-acp` | `Some("model")` | **None** |
| `copilot-acp` | `copilot`（args `--acp`） | `Some("model")` | 有 |

goose 官方文档的 ACP provider 一节也只列了这 5 个（含 Copilot）。而"自定义 provider"这条用户可配置的口子，`ProviderEngine` 只有 `OpenAI` / `Anthropic` / `Ollama` 三种（`declarative_providers.rs`）——**没有 ACP 引擎**，且注册时强制 `runs_own_tool_loop: false`。

### 三种变通办法

**(C1) PATH 影子二进制（最快，但属未验证 hack）**

goose 解析 ACP adapter 用的是 `SearchPaths::builder().with_npm().resolve(<写死的名字>)`（`acp_tooling.rs`），**没有环境变量可以覆盖命令**（已确认 `claude_acp.rs`/`codex_acp.rs`/`copilot_acp.rs` 里没有 `*_COMMAND` 式的 override）。

同时，goose 在 ACP `initialize` 时**只读 `agent_capabilities`（close / load_session / mcp_capabilities），完全不校验 agent 名字或版本**（`crates/goose/src/acp/provider.rs` 的 initialize 处理块，1544 行起）。所以理论上：**做一个叫 `pi-acp` 的可执行文件，它去 exec `hermes acp`，goose 就会把 Hermes 当 pi 用。**

Windows 做法示意（放到 PATH 里靠前的位置）：

```cmd
:: %USERPROFILE%\.goose-acp-shim\pi-acp.cmd
@echo off
set HERMES_ACP_SKIP_CONFIGURED_MCP=1
"C:\Users\Admin\AppData\Local\hermes\bin\hermes.exe" acp %*
```
```powershell
$env:PATH = "$env:USERPROFILE\.goose-acp-shim;$env:PATH"
$env:GOOSE_PROVIDER = "pi-acp"
$env:GOOSE_MODE = "auto"
goose session
```

为什么首选 `pi-acp` 而不是 `claude-acp`：`pi_acp.rs` 的 `session_mode_id: None`，goose 不会去 `session/set_mode` 推一个 Hermes 不认识的 mode；而 `claude-acp`/`amp-acp` 都会推 mode（Hermes 的 mode 是它自己的 edit-approval 策略集合，不匹配就可能是会话创建失败）。代价是 `pi-acp` 会 `set_config_option(id="model")`，而 Hermes 的 `set_config_option` 实现直接 `return SetSessionConfigOptionResponse(config_options=[])`（`acp_adapter/server.py:1074`）——**模型选择很可能不生效**，会退回 Hermes 自己的默认模型。

> ⚠️ **C1 全程未实测**。本机没有安装 goose，无法端到端验证。上机前请先 `hermes acp --check` 通过，再用 `goose session` 的最小 prompt 试探，并观察 Hermes 侧 `~/.hermes/logs/` 与 goose 的 ACP 日志。失败点最可能是 session 创建阶段的 mode 校验或模型 config option 往返。

**(C2) 自建 goose 发行版 / 打补丁（工程上最干净）**

goose 有官方机制 [Custom Distributions](https://goose-docs.ai/docs/guides/custom-distributions)：编译期预置 provider、扩展与品牌。照 `claude_acp.rs` 抄一个 `hermes_acp.rs`（`type Provider = AcpProvider`、`RUNS_OWN_TOOL_LOOP = true`、binary 用 `hermes`、args `["acp"]`、`env` 注入 `HERMES_ACP_SKIP_CONFIGURED_MCP=1`、`model_config_option_id: None`、`session_mode_id: None`），在 `registrations.rs` 里登记即可。这是一次性投入，之后 `GOOSE_PROVIDER=hermes-acp` 就是一等公民。

**(C3) 推上游**

ACP 是开放协议且 [有 registry](https://github.com/agentclientprotocol/registry)，Hermes 已是合规 ACP agent。给出上面那个 provider 描述，提 issue/PR 是合理诉求，成本最低。

### 补充：不要走错方向
- goose **自己**也能当 ACP server（`goose acp` / `goose serve` → `/acp`），那是"编辑器驱动 goose"，方向相反，不是本题所需。
- goose 的 Roaming（`goose roam bridge`）是 **goose↔goose** 的 p2p ACP 传输，也不能用来接 Hermes。
- 顺带一提，对称能力是存在的：**Hermes 自己也能把 ACP agent 当 provider**（`hermes --provider copilot-acp`，走 `HERMES_COPILOT_ACP_COMMAND`/`HERMES_COPILOT_ACP_ARGS` 两个**可覆盖**的变量）。也就是说 Hermes 侧对"ACP agent 当后端"的支持比 goose 更开放——goose 反而不行。

---

## 4. 路径 D：Hermes 当 goose 的 MCP 扩展

Hermes 明确提供 MCP server 模式，把"对话"暴露给其他 agent：

```powershell
hermes mcp serve    # Run Hermes as an MCP server (expose conversations to other agents)
```

goose 侧走标准 stdio 扩展（`config.yaml`）：

```yaml
extensions:
  hermes:
    type: stdio
    name: hermes
    enabled: true
    cmd: "C:\\Users\\Admin\\AppData\\Local\\hermes\\bin\\hermes.exe"
    args: ["mcp", "serve"]
    envs: { HERMES_ACCEPT_HOOKS: "1" }
    timeout: 600
```

适用场景：**把 Hermes 当 goose 的一个"外包同事"**——goose 保留主控权和自己的扩展，需要时把一个任务甩给 Hermes。注意这与 A/B/C 是不同维度的东西：它是"工具调用"，不是"换后端"。

---

## 5. 本机现状核查（实测记录）

| 项 | 结果 | 证据 |
|---|---|---|
| Hermes 是否安装 | ✅ 已装 | `C:\Users\Admin\AppData\Local\hermes\bin\hermes.exe`；`Get-Command hermes` 命中 |
| Hermes 版本来源 | 源码检出 + 打包运行时 | `AppData\Local\hermes\hermes-agent\`（含 `cli.py`、`acp_adapter/`、`gateway/`、`providers/`、`optional-mcps/`、`website/docs/`） |
| Hermes 当前状态 | ⚠️ **正在自我更新**，`npm`/`ripgrep` 报 out of sync，`hermes proxy status` 因触发依赖安装而超时 | 每次调用都打印 `install out of sync … run hermes pm install`；`hermes proxy status` 120s 超时在 "Installing Python dependencies"。**先跑 `hermes update` / `hermes pm install` 让更新收敛，再动上面任何配置。** |
| ACP 能力 | ✅ 命令已注册 | `hermes acp --help` 正常输出（含 `--check`/`--setup`/`--setup-browser`） |
| proxy 能力 | ✅ 命令已注册，默认 `127.0.0.1:8645`，upstream 只有 `nous` / `xai` | `hermes proxy --help`、`hermes proxy providers` |
| API server | ⚙️ 配置块存在但未启用 | `config.yaml` 有 `gateway.platforms.api_server.{max_concurrent_runs:10, history_tool_output_max_chars:0}`；`.env` 的键名列表里**没有** `API_SERVER_ENABLED` / `API_SERVER_KEY` |
| 已有的 Hermes 网关清单 | 存在 host-serve 网关锁与 token | `C:\Users\Admin\.local\state\hermes\gateway-locks\host-serve.json`（`role: serve`, `port: 54706`, `profiles: ["default"]`） |
| goose 是否安装 | ❌ 未安装 | `Get-Command goose` 无结果 |
| Hermes 是否有内置 goose 集成 | ❌ 无 | 全仓库 grep `goose` 仅命中 13 处，全部是"从 block/goose 借鉴的代码注释/schema 归一化移植/Buzz 测试里的假 profile 名"，**没有 goose 适配层** |

---

## 6. 证据清单

**goose 侧（上游源码 + 官方文档）**
- `crates/goose/src/providers/inventory/registrations.rs` — 5 个 ACP provider 的登记与 `acp_inventory(provider_id, command, …)`
- `crates/goose/src/providers/acp_tooling.rs` — `resolve_acp_command()` 只按二进制名在 PATH/npm 里找，无环境变量覆盖
- `crates/goose/src/providers/{claude,codex,amp,pi,copilot}_acp.rs` — 每个 provider 的 binary 名、args、mode mapping、`model_config_option_id`
- `crates/goose/src/acp/provider.rs` — `initialize` 只取 `agent_capabilities`，不校验 agent 身份；`apply_model_if_changed` 只走 `set_config_option`
- `crates/goose/src/config/declarative_providers.rs` — `custom_providers_dir()` = `<config>/custom_providers/`；`ProviderEngine` 三值；声明式 provider 恒为 `runs_own_tool_loop: false`
- `crates/goose/src/providers/base.rs` — `RUNS_OWN_TOOL_LOOP` / `SESSION_BOUND` 常量
- https://goose-docs.ai/docs/guides/acp-providers — 只售 4 个（+Copilot）ACP provider
- https://goose-docs.ai/docs/getting-started/providers — Custom Provider 的 JSON 形状、`OPENAI_HOST`/`OPENAI_BASE_PATH`、engine 仅 OpenAI/Anthropic/Ollama
- https://goose-docs.ai/docs/guides/config-files — 配置文件路径、stdio 扩展形状、API key 不入 config.yaml
- https://goose-docs.ai/docs/gdk/acp — 仅讲"goose 作为 ACP agent"，无自定义 ACP provider 的口子
- https://goose-docs.ai/docs/guides/roaming-agents — goose↔goose p2p ACP，与本题无关

**Hermes 侧（本机源码 `C:\Users\Admin\AppData\Local\hermes\hermes-agent\`）**
- `website/docs/user-guide/features/subscription-proxy.md` — 路径 A 全文（含"proxy 只做凭证透传、不跑 agent loop"的自我定位）
- `website/docs/user-guide/features/api-server.md` — 路径 B 全文（含 API server vs proxy 对比表、`hermes-agent` 模型名、`API_SERVER_*` 变量）
- `website/docs/user-guide/features/acp.md` — 路径 C 的 Hermes 侧（含 host integration 段与 `HERMES_ACP_SKIP_CONFIGURED_MCP`）
- `website/docs/reference/cli-commands.md` — `hermes acp` / `hermes proxy` / `hermes mcp` 的定位
- `acp_adapter/server.py` — `_session_modes()`、`_build_model_state()`、`set_config_option()`（返回空 config_options）
- `acp_adapter/model_catalog.py` — ACP 模型选择器的 `provider:model` 编码
- `website/docs/reference/environment-variables.md` — `HERMES_COPILOT_ACP_COMMAND`（Hermes 侧 ACP provider 是可覆盖的，与 goose 不同）
- 实测 CLI 输出：`hermes --help`、`hermes acp --help`、`hermes proxy --help`、`hermes proxy providers`、`hermes mcp --help`、`hermes mcp serve --help`

---

## 7. 未验证项（务必当作假设）

1. **C1 影子二进制方案从未实测**（本机无 goose）。不确定点：goose 发起 `session/new` 时会话创建是否被 Hermes 的 mode/model 校验拒绝；`set_config_option` 收到未知 `config_id` 是静默还是报错。
2. **路径 B 下 goose 的扩展是否被忽略**：Hermes 文档没有承诺"执行调用方传入的 tools"，我按文档推断为忽略，但**未做端到端请求抓包验证**。goose 可能对返回体里没有 `tool_calls` 的行为有额外处理分支。
3. **路径 B 的流式兼容**：Hermes 会插入自定义 SSE 事件 `hermes.tool.progress`；goose 的 OpenAI 流解析器遇到命名事件是否健壮未验证（Hermes 侧有 `tool_progress_events: false` 开关可关）。
4. **路径 A 与工具调用**：`hermes proxy` 是逐字节透传，模型是否稳定返回 OpenAI 格式 tool_call 取决于 Nous 侧模型，本机 proxy 未启动成功（更新中），**未实测**。
5. **goose 的 `custom_providers/*.json` 手写是否被热加载**：源码里 `load_custom_providers(&dir)` 是启动时读；文档说"直接改配置文件通常需要重启 goose"，未实测 Desktop/Goose2 的刷新行为。
6. **Hermes 更新收敛**：本机 Hermes 处于 `source-update` 中途状态，我未能启动 proxy 或 API server 做真实验证——上述所有命令均来自 `--help`/源码/文档，**非运行时实测**。

---

## 8. 建议的落地顺序

```powershell
# 前置：先把 Hermes 更新收敛，否则一切命令都会被依赖安装打断
hermes update          # 或 hermes pm install
hermes doctor
hermes acp --check     # 路径 C 依赖这步

# 第 1 步（10 分钟，必成）：路径 A，先用上订阅
hermes portal
hermes proxy start     # 保持前台运行；生产环境用 Wine/服务包装
# 另开终端：
$env:GOOSE_PROVIDER="openai"; $env:OPENAI_HOST="http://127.0.0.1:8645"
$env:OPENAI_API_KEY="sk-unused"; $env:GOOSE_MODEL="Hermes-4-70B"
goose session

# 第 2 步（30 分钟，高价值）：路径 B，让 Hermes 真正当后端
#   设 API_SERVER_ENABLED=true / API_SERVER_KEY=...  →  hermes gateway
#   在 goose 建 custom provider 指向 http://127.0.0.1:8642/v1/chat/completions
#   模型名 hermes-agent

# 第 3 步（想清楚再动）：路径 C
#   先花 10 分钟试 C1 影子二进制（pi-acp → hermes acp），
#   不行就评估 C2 自建发行版 / C3 推上游。
```

**最终判断**：用户问的"runtime"如果指**执行引擎**，官方可达答案是**路径 B（API server）**，「Hermes 作为 goose 的运行时」这句话在 goose 侧没有原生入口；如果指**模型**，答案是**路径 A（proxy）**，十分钟能用。真正的"A 与 C 之间的那种 ACP 运行时委托"，需要 goose 侧补一个 `hermes-acp` provider 才能真正成立。

---

# 追加调研：goose 没有知识库时，哪条路径能用到 Hermes 的知识能力？

## 9.1 先纠正前提：Hermes 没有「知识库」这个产品

Hermes 的 `website/docs/user-guide/features/` 目录下**不存在 knowledge-base 或 rag 页面**（目录清单已逐项读取：memory.md / memory-providers.md / skills.md / context-files.md / context-references.md / tool-search.md …，没有 KB 页）。它的知识资产是四类彼此独立的东西，**全部位于 agent 层，不在模型层**：

| # | 资产 | 机制 | 规模/上限 | 关键性质 |
|---|------|------|----------|---------|
| 1 | **内建持久记忆** | `~/.hermes/memories/MEMORY.md` + `USER.md`，由 `memory` 工具增改，**会话开始时整块注入 system prompt** | 2,200 / 1,375 字符（~1300 token） | **冷冻快照**：session start 注入后不再变；不自动压缩，写满报错 |
| 2 | **`session_search`** | 对 `state.db` 做全文检索（FTS），捞历史会话 | 全部历史 | 文档明说"需要 session 边界才会触发" |
| 3 | **7 个外部记忆 provider** | `honcho` / `openviking` / `mem0` / `hindsight` / `holographic` / `retaindb` / `byterover` / `supermemory`，同一时间只能启用一个，**additive**（内建记忆照常工作） | 取决于 provider | 提供语义检索（如 `honcho_search`）、跨会话 representation/card、镜像内建记忆写入 |
| 4 | **技能体系** | `skills.md` 里的 **knowledge-base skill**（一整套书/论文/文档语料压成一个 skill，按需加载）；bundled `llm-wiki`（自述为 "RAG alternative"、可复利的 markdown 知识库）；optional 技能里的 RAG 工具 `qmd` / `siyuan` / `chroma` / `qdrant` / `pinecone` | 无硬上限 | 按相关性加载，不占 2,200 字符预算 |

**关键推论**：既然知识能力全在 agent 层，那么"哪种 goose 集成模式能用上"就等于"哪种模式让 **Hermes 的 agent 真的跑起来**"。

## 9.2 逐路径判定

| 路径 | 能否用到 Hermes 的知识能力 | 依据 |
|------|--------------------------|------|
| **A. proxy** | ❌ **完全用不到** | proxy 文档自述："No transformation. No logging of request bodies. **No agent loop.** The proxy is a credential-attaching pass-through."；对比表里 Tool calls 一栏写 "No — passthrough only"。没有 agent → 没有 memory 注入、没有 session_search、没有技能 |
| **B. API server** | ✅ **能，且是唯一"开箱自动生效"的路径** | 官方定位就是 "Your agent handles requests with its **full toolset** (terminal, file operations, web search, **memory, skills**)"。Hermes 侧完整 agent 每轮都在跑，它的 KB 资产在其内部被自然使用 |
| **C. ACP** | ✅ 能（与 B 等价，副作用不同） | `acp.md` 明确列出 ACP toolset 含 "**memory, todo, session search**"、"**skills**"。差别只在 goose 是否要透传扩展（B 不透传，C 透传） |
| **D. mcp serve** | ❌ **用不到** | 源码 `mcp_serve.py` 首行自述："Hermes MCP Server — expose **messaging conversations** as MCP tools"。工具集是 `conversations_list` / `messages_read` / `send_message` 这类**消息桥**，**不暴露任何知识检索工具** |

**所以答案是 B（或 C）**，A 和 D 直接出局。

## 9.3 走 B 时，必须补的三个配置，否则"知识"会打折

这是本问题最容易被忽略的部分——**Hermes 的记忆体系是围绕"会话边界"设计的**，goose 若每次都用新会话发请求，会丢掉一半能力。

**(1) MEMORY.md / USER.md 会自动生效，但有"一轮延迟"**
注入发生在 session start，且是 frozen snapshot。含义：
- 好处：goose 每轮都开新 session 的话，反而总能拿到**最新**的 MEMORY.md；
- 坏处：**同一会话内** Hermes 新写入的记忆，本轮和后续轮都看不到（要等下一个 session）。

**(2) 跨会话语义 recall + session_search 依赖会话连续性 → 必须下发会话头**

api-server 文档原文：
> the memory provider is initialised once per session and kept across requests, so a **continued session** (`X-Hermes-Session-Id`, `previous_response_id`, or a declared `X-Hermes-Session-Key` conversation) receives the recall the provider prepared after the previous turn.

goose 侧下发自相定义 header 的两个位置：
- 自定义 provider JSON 的 `headers` 字段（`DeclarativeProviderConfig.headers`，Desktop 建 provider 时不可填，需建完再手改 JSON）；
- 或内置 OpenAI provider 的 `OPENAI_CUSTOM_HEADERS`，格式 `HEADER_A=VALUE_A,HEADER_B=VALUE_B`。

建议至少钉住 transcript 级标识：
```
X-Hermes-Session-Id: goose-<稳定的会话名>
```
需要给外部 memory provider 一个**不随 `/new` 轮换**的稳定作用域时，再加 `X-Hermes-Session-Key: agent:main:goose:<用户或项目>`（规则：≤256 字符，禁 `\r`/`\n`/`\x00`）。

**(3) 别指望"一次配置全自动"**
外部 memory provider 需要先在 Hermes 侧启用并登录（`hermes memory setup`），且**一次只能激活一个**。`memories/` 目录本机当前是空的，说明这套东西还没初始化——B 路径要真正"有知识"，前置动作是：`hermes memory setup` → 选 provider → 灌入/沉淀内容。

## 9.4 反面思考：如果目标只是"让 goose 有知识库"，别绕 Hermes

这是本次调研里最有价值的副产品。Hermes 的知识资产**没有对外查询 API**（除 provider 自带 SDK 外），绕道 B/C 本质上是"整台 Hermes 替我回答"，代价是 goose 自己的扩展/loop 全部让位。更干净的做法是**给 goose 直接挂一个 KB 类 MCP 扩展**：

- **`qmd`** —— Hermes 自己就是把它当 MCP server 用的：`qmd mcp`（stdio，持久）或 `qmd mcp --http --daemon`，工具集 `mcp_qmd_search/vsearch/deep_search/get/status`，混合 BM25+向量本地检索，MIT 许可（`@tobilu/qmd`）。**这是纯第三方工具，goose 可以直接挂同一个，完全不经 Hermes。**
- 其他同类可选：Mem0 / Chroma / Qdrant / SiYuan（Hermes 的 optional skills 里也都在用同一批基础设施）。
- 补充事实：goose 其实**有一个内建的 `memory` 扩展**（config-files 文档示例里 `memory: {type: builtin, bundled: true}`），但那是简单记忆，不是可检索知识库——所以"goose 没有知识库"这个判断基本成立，只是要区分"记忆"和"知识库"。

**选型建议**
- 只要"我的 goose 能查我的知识" → **直接给 goose 挂 qmd MCP**（或 mem0），别碰 Hermes。
- 要"用 Hermes 已经沉淀好的记忆/技能/语料" → **走 B**，并配好 §9.3 的会话头。
- 既要 Hermes 的知识、又要 goose 的扩展被真正使用 → **路径 C**（但需先解决 goose 侧没有 `hermes-acp` provider 的问题，见第 3 节）。

## 9.5 本节新增的未验证项

1. **路径 B 下 `X-Hermes-Session-Id` 是否能通过 goose 的 `headers`/`OPENAI_CUSTOM_HEADERS` 成功落到请求上**：字段在源码里存在（`DeclarativeProviderConfig.headers`、`OPENAI_CUSTOM_HEADERS`），但**未做端到端抓包**。
2. **Hermes API server 对调用方传入 `tools` 的处理**（上一篇的未验证项 2）在"知识库"场景下更关键：如果 goose 发来的 tools 被忽略，goose 的扩展在本路径等于摆设；这一条仍未验证。
3. **`qmd` 挂到 goose 是否可用**：qmd 的 MCP 契约来自 Hermes 的 optional skill 文档（第三方项目文档），**未在本机安装验证**。
4. **goose 内建 memory 扩展的实际能力边界**（是否支持向量检索、容量多少）：来自 config-files 文档的示例片段，**未读源码、未实测**。

---

# 追加调研二：要让 goose 用上 Hermes 的**记忆/技能自进化**，选哪个模式？

## 10.1 先拆开"Hermes 的自进化"到底由哪三部分组成

文档里这是一个被明确命名的机制，不是模糊能力。它由**三个部件**组成，缺一个都会退化成"能读写但没有进化"：

| 部件 | 作用 | 触发点（文档原文） | 配置 |
|------|------|------------------|------|
| **① Nudge（方向性提醒）** | 计数器到了就提醒模型"该复盘记忆了 / 该沉淀技能了" | **agent loop 内**：memory 计数器在 pre-loop 计算、响应后触发；skill 计数器在 loop 结束后计算 | `memory.nudge_interval`、`skills.creation_nudge_interval` |
| **② Background review fork（真正的写入者）** | spawn 一个后台 `AIAgent` fork 重放对话，去写 MEMORY.md / `skill_manage` 建技能；**不打断主对话**，与主对话共享 prompt cache | **automatic post-turn fork**（每轮之后） | `auxiliary.background_review.{enabled,provider,model,max_input_tokens}`；默认 `enabled: true` |
| **③ Curator（维护循环）** | 给"agent 自己造出来的技能"做生命周期管理：usage 追踪、`active → stale(14d) → archived(30d)`、LLM 合并去重 | **"On CLI session start, during gateway housekeeping, and on the Desktop/`hermes serve` maintenance timer"**（curator.md 第 19 行，逐字） | `curator.{enabled:true, interval_hours:168, min_idle_hours:2, consolidate:false}` |

来源：`website/docs/user-guide/features/memory.md`（§Running the review on a cheaper model / §Disabling automatic reviews）、`website/docs/user-guide/features/curator.md`、`website/docs/user-guide/features/codex-app-server-runtime.md`（§Self-improvement loop 里给出计数器语义）。

值得强调 curator 的存在理由（curator.md 原文）：技能是"self-improvement loop"自动写进 `~/.hermes/skills/` 的，"Without maintenance, you end up with dozens of narrow near-duplicates that pollute the catalog and waste tokens."

## 10.2 逐模式判定：**只有 B 三项全活**

| 模式 | ① Nudge | ② Review fork | ③ Curator | 结论 |
|------|--------|--------------|----------|------|
| **A. proxy** | ❌ | ❌ | ❌ | 无 agent loop，自进化三件套**全灭** |
| **B. API server** | ✅ loop 内 | ✅ post-turn | ✅ **API server 就挂在 `hermes gateway` 上，gateway housekeeping 就是它的触发点** | **✅ 三项全活——唯一自洽的模式** |
| **C. ACP** | ✅ loop 内 | ✅ post-turn | ❌ **ACP adapter 进程不在 curator 的触发清单里**（清单只有 CLI session start / gateway housekeeping / serve 维护定时器） | ⚠️ 能读写、能提醒，但**技能只增不减**，会长出大量近重复技能 |
| **D. mcp serve** | 视目标会话而定 | 视目标会话而定 | 若同时常驻 gateway 则 ✅ | ⚠️ 它是消息桥，不是"把 Hermes 当后端" |

**结论：选 B（API server）。**

理由不是"B 也能用"，而是 **B 是唯一让自进化形成闭环的模式**：
- ①② 需要"Hermes 的 agent loop 真的在跑" → A 出局，B/C 满足；
- ③ 需要"一个常驻的 gateway / serve / CLI 进程做 housekeeping" → **只有 B 天然满足**，因为 API server 本身就是 gateway 的一个 platform（`gateway.platforms.api_server`），你为了跑 B 必须常驻 `hermes gateway`；而 C 的 ACP adapter 是**按需 stdio 子进程**，进程结束即消失，没有维护定时器。

换句话说：**走 C 你会得到"记忆和技能会增长，但永不清理"的半套自进化**；要补齐就得额外再常驻一个 `hermes serve` 或 gateway —— 那还不如直接走 B。

## 10.3 走 B 时，四个必须检查的开关（这是最容易踩的坑）

**(1) `write_approval` 必须保持 `false` —— 这是头号杀手**

两个开关的默认值都是 `false`（自由写入），但如果你（或某次 setup）打开了它：

```yaml
memory:
  write_approval: false    # true = stage every write for review
skills:
  write_approval: false    # true = 同上
```

memory.md 写得非常直接：
> With `write_approval: true`, **writes outside the interactive CLI are held for review and never reach the file** until approved — run `/memory pending` and `/memory approve all`.

而 **API server 会话正是 "outside the interactive CLI"**。一旦为 true：
- 记忆写入被暂存，**永不落盘**；
- 技能写入被 stage 到 `~/.hermes/pending/skills/`；
- 而两个审批入口（`/memory approve all`、`/skills pending|diff|approve|reject`）分别在 CLI 与 messaging 平台上——**goose 侧根本看不见、也无从批准**。

结果就是"自进化静默失效"：goose 那边一切正常，Hermes 这边什么都没学到。**这是本问题最值得先检查的一项。**

**(2) 钉住 `X-Hermes-Session-Id`（否则 nudge 可能永不触发）**

① 的计数器是 `_turns_since_memory` / `_iters_since_skill` 这类**挂在 agent 实例上的状态**；而 API server 的 agent 缓存是 per-session（`agent.agent_cache.idle_ttl_secs` 默认 1 小时）。goose 若不发 `X-Hermes-Session-Id`，每个请求都是新 session → 新 agent 实例 → **计数器从 0 开始，永远到不了 `nudge_interval`** → ① 不触发，自进化退化成"只有 ② 在没有方向性提醒的情况下盲写"。

> ⚠️ 这一条是我从"计数器在 loop 内 + agent 缓存 per-session"两条文档事实推出的**逻辑外推，未实测**。请按未验证项对待，最简单验证法：跑几轮后看 `~/.hermes/memories/MEMORY.md` 是否有新条目、日志里是否有 nudge/review 记录。

goose 侧下发位置同上篇 §9.3：custom provider JSON 的 `headers` 或 `OPENAI_CUSTOM_HEADERS`。

**(3) 盯住 ② 的 token 成本**

② 是 **post-turn** fork：goose 每提一个问题，Hermes 都可能额外跑一次"复盘"。goose 是高频调用方，这个成本会放大。三个刹车：

```yaml
auxiliary:
  background_review:
    enabled: true
    max_input_tokens: 48000        # 单次复盘重放输入的总上限，封顶成本
    provider: openrouter           # 路由到便宜模型，官方称可省 3–5×
    model: google/gemini-3-flash-preview
```
注意：路由到**不同**模型时会自动改用对话 digest（近轮逐字 + 老轮摘要），官方称"memory capture was identical and skill capture near-identical"；而**同模型**复盘永远继承父对话的 reasoning effort，`reasoning_effort` 键被忽略并打印一次性警告。

**(4) 别把工具关掉**

`memory.memory_enabled: false`、`user_profile_enabled: false`，或把 `memory`/`skills` 放进 `agent.disabled_toolsets`，都会直接从 schema 里摘掉工具 —— 模型连"能保存"都不知道，自进化归零。

## 10.4 一个必须接受的副作用

走 B 时，**goose 自己的 `memory` 扩展和 Hermes 的记忆是两套独立存储，不会合并**。goose 侧的记忆留在 goose 的 store 里，Hermes 侧的在 `~/.hermes/memories/MEMORY.md` + 外部 provider。你得到的不是"goose 有了 Hermes 的记忆"，而是"**goose 把活派给了一个会自己记事的同事，这个同事越用越熟练**"。如果需求是前者（goose 本体要有记忆/知识），请回到 §9.4：给 goose 直接挂 mem0 / qmd 这类 MCP 扩展。

## 10.5 本节新增的未验证项

1. **nudge 计数器是否真的因每轮新 session 而归零**（§10.3(2)）—— 逻辑外推，未实测。
2. **`write_approval: true` 下 API server 写入的确切命运**（是落盘但不通知，还是完全不落盘）—— 文档措辞是 "never reach the file"，我按字面理解，未实测 staged 目录。
3. **curator 是否会被 ACP adapter 的进程间接触发**：文档触发清单不含 ACP，但"gateway housekeeping"是否会被 ACP 的会话创建间接满足，**未验证**（我的判断是不会，因为 ACP 不经过 gateway）。
4. **goose 侧 `headers` 是否能成功注入每轮请求**：仍未抓包验证（承接 §9.5 第 1 条）。
