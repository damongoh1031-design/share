# 教程 · 路径 B：把 Hermes Agent 的 API server 接成 goose 的后端

> 编写日期：2026-10-16
> 取证方式：**Hermes 本机源码（`C:\Users\Admin\AppData\Local\hermes\hermes-agent\`）+ 官方文档 + goose 上游源码（`aaif-goose/goose@main`）**
> 标注约定：**【源码】**= 我在源码里读到实现；**【文档】**= 官方文档原文；**⚠️ 未实测**= 本机 goose 未安装，无法端到端验证
>
> 本教程只讲路径 B。其余三条路径（A proxy / C ACP / D MCP）见 `report.md`。

---

## 0. 先读这 90 秒：三个硬约束

写这份教程时最重要的一件事，是把"承诺"和"实际会发生什么"分开。下面三条是**配之前就该知道**的，否则你会配完才发现不是想要的：

| # | 约束 | 依据 |
|---|---|---|
| 1 | **goose 的扩展工具在这条路径上不会被使用。** Hermes 用自己的工具集（terminal / file / web / memory / skills）干活，goose 发来的 `tools` 数组被静默忽略 | **【源码】** `gateway/platforms/api_server_openai_routes.py` 里 `tools` / `tool_choice` **只出现在 `fingerprint_keys=[...]`**（幂等指纹）中，从不用于构建 toolset。搜索 `".get(\"tools\")"` / `'["tools"]'` 在全部 `api_server*.py` 里**零命中** |
| 2 | **两套记忆不合并。** goose 自己的 `memory` 扩展与 Hermes 的 `MEMORY.md` 是两个独立存储 | **【文档】** §System Prompt Handling：前端 system prompt 是"layered on top"，但记忆不互通 |
| 3 | **必须常驻一个 `hermes gateway` 进程**，且 **`API_SERVER_KEY` 必须 ≥16 字符且非占位符**，否则 adapter 直接拒绝启动 | **【源码】** `gateway/config_env.py::_api_server()` + `api_server.py::_api_key_passes_startup_guard()` → `has_usable_secret(key, min_length=16)` |

**什么时候该走 B**：你要一个**已经会自己记事、自己攒技能**的 agent，愿意让 Hermes 当"执行者"，goose 当"前端 + 会话/recipe 编排"。
**什么时候不该走 B**：你离不开 goose 的 70+ 扩展工具、或要求 goose 的 loop 说了算 → 走**路径 A**（`report.md` §1）。

---

## 1. 原理：为什么用 OpenAI 协议就能换后端

```
┌──────────────────┐   HTTP POST /v1/chat/completions   ┌────────────────────────┐
│ goose CLI/Desktop│ ─────────────────────────────────► │ Hermes API server      │
│ （前端/编排）     │   Authorization: Bearer <key>      │ （gateway 的一个       │
│                  │   X-Hermes-Session-Id: <会话>       │   platform adapter）   │
│                  │ ◄───────────────────────────────── │                        │
└──────────────────┘   最终文本（+ 工具进度 SSE）        └───────────┬────────────┘
                                                                    │ 自己跑 agent loop
                                                                    ▼
                                                        ┌────────────────────────┐
                                                        │ Hermes AIAgent         │
                                                        │ ├ terminal / file / web│
                                                        │ ├ memory（MEMORY.md）  │
                                                        │ ├ skills / skill_manage│
                                                        │ └ subagent / cron ...  │
                                                        └────────────────────────┘
```

关键点：Hermes 把「**agent 本身**」伪装成一个 OpenAI **模型**。所以任何会说 OpenAI 协议的客户端都能接——goose 只是其中之一。

**【文档】** Hermes 自己给的划分（`api-server.md`）：

| | API server | Subscription proxy（路径 A） |
|---|---|---|
| 提供什么 | **你的 agent**（完整工具集、记忆、技能） | 裸模型推理 |
| Tool calls | **是——agent 自己跑工具** | 否——纯透传 |

**推论**：这条路径上，"工具循环"的所有权从 goose 转移到了 Hermes。这也正是它唯一能让你白拿 Hermes 记忆/技能/知识的方式——因为那些能力全在 agent 层（见 `report.md` §9）。

---

## 2. 前置检查

### 2.1 让 Hermes 更新收敛（不然后面所有命令都会被依赖安装打断）

```powershell
hermes update          # 或 hermes pm install
hermes doctor
```

**本机现状**：Hermes 处于 `source-update` 中途，每次都打印 `install out of sync (npm: not installed or outdated; ripgrep: not installed or outdated)`。⚠️ 这是本次调研中唯一挡住端到端实测的因素。

### 2.2 确认 API server 的密钥强度规则

**【源码】** `hermes_cli/auth.py::has_usable_secret(value, min_length=16)`：

```python
cleaned = value.strip()
return (len(cleaned) >= min_length
        and cleaned.lower() not in _PLACEHOLDER_SECRET_VALUES     # "changeme","example","dummy","none",...
        and not _is_placeholder_shape(cleaned))                   # "your_..._here"、"sk-xxxx"、全 x
```

**【源码】** 启动守卫 `api_server.py::_api_key_passes_startup_guard()` 的三条报错，可直接用来对号入座：

| 报错 | 含义 |
|---|---|
| `Refusing to start: API_SERVER_KEY is required for the API server, including loopback-only binds on 127.0.0.1` | 完全没设 key |
| `Refusing to start: API_SERVER_KEY is a placeholder or too short (<16 chars). ... a guessable key is remote code execution.` | 太短或像占位符 |
| `Refusing to start: API_SERVER_KEY strength could not be verified (...). Repair the installation` | fail-closed：连检查都做不到时也不启动 |

> ⚠️ **一处文档与代码的不一致（实测发现）**：`api-server.md` 的 `config.yaml` 示例写的是 `key: your-secret-key`，但该串**只有 15 个字符**，按上面的守卫会被拒绝启动。请勿照抄该示例。**同文档的 `.env` 示例 `change-me-local-dev`（18 字符）是能通过的**，但生产环境请用随机串。

### 2.3 检查端口与残留锁

```powershell
# 8642 是否已被占用
Get-NetTCPConnection -LocalPort 8642 -ErrorAction SilentlyContinue |
  Select-Object LocalAddress, LocalPort, State, OwningProcess

# 是否有其它 hermes gateway / serve 在跑
Get-Process -Name python, hermes -ErrorAction SilentlyContinue |
  Select-Object Id, ProcessName, StartTime
```

**本机现状**：存在一份 `hermes serve` 留下的锁文件

```
C:\Users\Admin\.local\state\hermes\gateway-locks\host-serve.json
{ "role": "serve", "pid": 8056, "host": "127.0.0.1", "port": 54706,
  "profiles": ["default"], "updatedAt": "2026-10-01T08:32:59Z" }
```

它占的是 **54706**（不是 8642），不会直接撞端口；但如果 pid 8056 已不存在，这是一份**陈旧的锁**，建议在排查 gateway 启动异常时先确认它的进程是否还活着。⚠️ 未实测该锁对 `hermes gateway` 启动的实际影响。

### 2.4 确认 Hermes 自己有可用的 provider

API server 只是"把 agent 暴露出去"，agent 自己得有模型可用：

```powershell
hermes setup --portal      # 【文档】一次性：300+ 模型 + web/image/TTS/browser 的 Tool Gateway
```

---

## 3. Hermes 侧配置

### 3.1 生成一个合格的密钥

```powershell
# PowerShell（Windows，无需 openssl）
$bytes = New-Object byte[] 32
[System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
$key = -join ($bytes | ForEach-Object { $_.ToString('x2') })
$key                      # 64 个十六进制字符
```

```bash
# bash / WSL
openssl rand -hex 32
```

### 3.2 写法一：写入 `.env`（推荐）

**【文档】** 加到 `~/.hermes/.env`；本机路径 = `C:\Users\Admin\AppData\Local\hermes\.env`

```env
API_SERVER_ENABLED=true
API_SERVER_KEY=<把上面生成的 64 位串贴进来>
# 可选：只有浏览器需要直连 Hermes 时才设
# API_SERVER_CORS_ORIGINS=http://localhost:3000
```

**本机现状**：`.env` 现有键全是浏览器/终端/视觉调试开关（`BROWSER_*`、`TERMINAL_*`、`VISION_TOOLS_DEBUG` 等），**没有任何 `API_SERVER_*`** —— 所以这一步是本教程唯一必须新增的配置。

### 3.3 写法二：写进 `config.yaml`

**【源码】** `gateway/api_server` 配置支持 `enabled / port / host / key / cors_origins / model_name / max_concurrent_runs / history_tool_output_max_chars`，且接受三种嵌套位置：`gateway.api_server:`、`gateway.platforms.api_server:`、`platforms.api_server:`。

**本机现状**：`config.yaml` 第 1321 行**已经有这个块**，但只有两个调优项、没有 `enabled` 和 `key`：

```yaml
gateway:
  ...
  api_server:                      # ← 第 1321 行，已存在
    max_concurrent_runs: 10
    history_tool_output_max_chars: 0
```

要改用配置方式，补两行即可：

```yaml
gateway:
  api_server:
    enabled: true
    key: <64 位随机串>            # 注意 ≥16 字符
    max_concurrent_runs: 10
    history_tool_output_max_chars: 0
```

### 3.4 启用机制：其实是"密钥存在即启用"

这是一个文档没点明、但源码很明确的细节：

**【源码】** `gateway/config_env.py::_api_server()`：

```python
key = getenv("API_SERVER_KEY")
if not _has_usable_api_server_key(key):
    return                                    # 没合格密钥 = 直接不注册这个 platform
extra = _enable_from_env(config, Platform.API_SERVER, pop_marker=True, warn=False).extra
extra["key"] = key
```

也就是说：
- **`API_SERVER_KEY` 合格 ⇒ 平台就被启用**；`API_SERVER_ENABLED=true` 在源码里是 `pop_marker=True` 的"标记"，会被消费掉。
- 走 `config.yaml` 时，连接性检查是 `_PLATFORM_CONNECTED_CHECKERS[Platform.API_SERVER] = _has_usable_api_server_key(cfg.extra.get("key"))` → **同样只看 key 是否合格**。
- **环境变量优先于 `config.yaml`**（【文档】明写）。

### 3.5 本机特别提醒：`multiplex_profiles: true`

**本机现状**：`config.yaml` 第 1301 行 `multiplex_profiles: true`（且 `auto_multiplex_migration: true`）。

**【文档】** 这会让共享 listener 用 `/p/<profile>/` 前缀服务每个 profile，并且**认证绑定到被路由的 profile**：

| URL | 用哪个密钥 |
|---|---|
| `http://127.0.0.1:8642/v1/...` | **默认 profile 的** `API_SERVER_KEY` |
| `http://127.0.0.1:8642/p/default/v1/...` | 同上 |
| `http://127.0.0.1:8642/p/alice/v1/...` | **必须**用 `~/.hermes/profiles/alice/.env` 里的 `API_SERVER_KEY`；用默认 profile 的 key 会 **401** |

> ⚠️ 本机目前只有 `default` profile（锁文件的 `profiles: ["default"]`），所以 goose 直接用**无前缀** URL 即可。若以后建了 profile 并想让 goose 走它，必须为该 profile 单独设 key。

### 3.6 可选开关

| 开关 | 默认 | 什么时候要动它 |
|---|---|---|
| `direct_model_requests` | **false** | goose 只会发**裸 `model`**。裸 model 默认被忽略（落到 Hermes 全局默认模型）；想让 goose 指定的模型名生效，就开这个，或改用带 `provider` 字段的请求。**【文档】+【源码】** `api_server.py:1237` |
| `tool_progress_events` | **true** | 保持 true 时，Chat Completions 的 SSE 会额外发 `event: hermes.tool.progress`（Hermes 自定义命名事件）。**goose 的流解析器若被命名事件卡住**，把它设为 `false`。**【文档】+【源码】** `api_server.py:1242` |
| `max_concurrent_runs` | **10** | 超限返回 **429** `Too many concurrent runs (max N)`。本机已是 10；`0` = 不限 |
| `history_tool_output_max_chars` | **0**（逐字存） | 只影响 `/v1/responses` 的 `previous_response_id` 存储体积 |
| `cors_origins` | 无 | 仅浏览器直连需要。goose 是**服务端到服务端**，**不需要** |

配置写法（`config.yaml` 的同一个块里）：

```yaml
gateway:
  api_server:
    enabled: true
    key: <64 位随机串>
    direct_model_requests: true      # 让 goose 发的裸 model 生效
    tool_progress_events: true       # 若 goose 流解析报错再改 false
    max_concurrent_runs: 10
```

### 3.7 启动并自测

```powershell
hermes gateway
# 期望看到：
# [API Server] API server listening on http://127.0.0.1:8642
```

**三条自测（PowerShell 原生，不依赖 curl）**：

```powershell
$key = "<你的密钥>"
$h   = @{ Authorization = "Bearer $key" }

# ① 存活探针（无需认证）
Invoke-RestMethod http://127.0.0.1:8642/health
# → {"status":"ok"}     ；/v1/health 同样可用

# ② 模型名发现（goose 建 provider 时要用这个名字）
Invoke-RestMethod http://127.0.0.1:8642/v1/models -Headers $h
# → 默认 profile 下模型名就是 hermes-agent

# ③ 能力清单（机器可读，用于确认这个版本支持什么）
Invoke-RestMethod http://127.0.0.1:8642/v1/capabilities -Headers $h
```

**【源码】** `/v1/capabilities` 里会明确 advertisement 出两个我们后面要用的头名（`api_server.py:59-79`）：

```json
{
  "session_continuity_header": "X-Hermes-Session-Id",
  "session_key_header": "X-Hermes-Session-Key",
  "features": { "chat_completions": true, "responses_api": true, "run_events_sse": true,
                "reasoning_streaming": true, "skills_api": true, "memory_write_api": false }
}
```

**一次真实的对话（含工具调用观察）**：

```powershell
$body = @{
  model    = "hermes-agent"
  messages = @(@{ role = "user"; content = "用你的终端工具列出当前目录的前 5 个文件，然后告诉我一共几个" })
} | ConvertTo-Json -Depth 6

Invoke-RestMethod -Uri "http://127.0.0.1:8642/v1/chat/completions" -Method Post `
  -Headers $h -ContentType "application/json" -Body $body
```

> **这里就是第 0 节的约束 1 的现场演示**：Hermes 会**真的去执行 `ls`**（用它自己的 terminal 工具），然后把结果作为最终文本返回。返回体里**不会**有 `tool_calls` 等着 goose 去执行。

**想要 curl 风格（注意 Windows 上 `curl` 是 `Invoke-WebRequest` 的别名，必须写 `curl.exe`）**：

```cmd
curl.exe -N http://127.0.0.1:8642/v1/chat/completions ^
  -H "Authorization: Bearer %API_SERVER_KEY%" ^
  -H "Content-Type: application/json" ^
  -H "X-Hermes-Session-Id: goose-smoke-test" ^
  -d "{\"model\":\"hermes-agent\",\"stream\":true,\"messages\":[{\"role\":\"user\",\"content\":\"说一句你好\"}]}"
```
`-N` 关掉缓冲以看清 SSE。**【文档】** 长工具调用期间每 10 秒会发一行 `: keepalive` 注释，标准 SSE 客户端会忽略它。

---

## 4. goose 侧配置

### 4.1 文件位置

**【源码】** `crates/goose/src/config/declarative_providers.rs`：

```rust
pub fn custom_providers_dir() -> std::path::PathBuf {
    Paths::config_dir().join("custom_providers")
}
```

**【文档】** goose 配置根目录：Linux/macOS `~/.config/goose/`，**Windows `%APPDATA%\Block\goose\config\`**。

所以本机上 provider 文件放在：

```
%APPDATA%\Block\goose\config\custom_providers\hermes_api_server.json
```

### 4.2 完整 provider 文件

```json
{
  "name": "hermes_api_server",
  "engine": "openai",
  "display_name": "Hermes Agent (API server)",
  "description": "Hermes agent 作为 OpenAI 兼容后端；工具循环由 Hermes 执行",
  "api_key_env": "HERMES_API_SERVER_KEY",
  "base_url": "http://127.0.0.1:8642/v1/chat/completions",
  "models": [
    { "name": "hermes-agent", "context_limit": 200000 }
  ],
  "requires_auth": true,
  "supports_streaming": true,
  "headers": {
    "X-Hermes-Session-Key": "agent:main:goose:default"
  },
  "session_id_header_override": "X-Hermes-Session-Id"
}
```

**字段来源**：**【源码】** `DeclarativeProviderConfig`（`declarative_providers.rs:218-243`）包含 `name / engine / display_name / description / api_key_env / base_url / models / headers / session_id_header_override / timeout_seconds / supports_streaming / requires_auth / catalog_provider_id / base_path / env_vars / auth / dynamic_models / toolshim / preserves_thinking / emit_clear_thinking / setup`。`engine` 只接受 **`openai` / `anthropic` / `ollama`** 三种。

### 4.3 两个字段值得单独讲（本节的新发现）

**(1) `session_id_header_override` —— 让 goose 自动下发 `X-Hermes-Session-Id`**

这是本次调研翻 goose 源码时找到的、文档里没有明说的可用字段。**【源码】** `crates/goose/src/session_context.rs`：

```rust
pub const SESSION_ID_HEADER: &str = "agent-session-id";     // goose 的默认会话头名

pub(crate) fn session_id_request_builder_with_header_override(
    header_name_override: Option<&str>,
) -> Result<RequestBuilderDecorator, InvalidHeaderName> {
    let header_name = match header_name_override {
        Some(h) => HeaderName::from_bytes(h.as_bytes())?,
        None    => HeaderName::from_static(SESSION_ID_HEADER),
    };
    ...
    if let Some(session_id) = current_session_id() {
        request.headers_mut().insert(session_header, HeaderValue::from_str(&session_id)?);
    }
```

而 `openai_def.rs::from_custom_config()`（**自定义 provider 走的就是这条路**）把它接了进去：

```rust
pub fn from_custom_config(config: DeclarativeProviderConfig, tls_config: ...) -> Result<OpenAiProvider> {
    let request_builder = session_id_request_builder_with_header_override(
        config.session_id_header_override.as_deref(),
    )?;
    ...
}
```

**结论**：写上 `"session_id_header_override": "X-Hermes-Session-Id"` 之后，goose 会把**它自己的当前会话 ID** 作为 `X-Hermes-Session-Id` 发出去——**不用任何 hack，会话连续性直接对齐**。

- 若**不**写这个字段，goose 发的是 `agent-session-id`，而 Hermes 只认 `X-Hermes-Session-Id` → **每轮都是新会话**，`session_search` 与外部 memory provider 的 recall 不会累积。
- ⚠️ **未实测**：header 只在 `current_session_id()` 返回 `Some` 时插入。goose 在 `goose session` / Desktop 下应该有会话上下文，但 `goose run` 一次性调用的行为我没能确认（本机没装 goose）。
- 注：内置 `openai` provider 走的是**不带 override** 的 `session_id_request_builder()`，头名固定 `agent-session-id`，所以**只有自定义 provider 路线能改头名**。

**(2) `headers` —— 静态头，用来钉 `X-Hermes-Session-Key`**

**【源码】** `headers: Option<HashMap<String, String>>` 是 `DeclarativeProviderConfig` 的一等字段。
**【文档】** goose 官方说明：*"Custom providers must use OpenAI, Anthropic, or Ollama compatible API formats. They can include custom headers for additional authentication, API keys, tokens, or tenant identifiers."*

`X-Hermes-Session-Key` 是给**外部记忆 provider（Honcho 等）**用的**稳定作用域**，它**不随 `/new` 轮换**（就是它存在的理由）。**【文档】** 规则：**≤256 字符，禁止 `\r` / `\n` / `\x00`**，值会在响应里回显。

> **两者的区别（别混）**：
> - `X-Hermes-Session-Id` = **transcript 级**，跟着会话走，`/new` 就换 → 由 goose 自动填（靠 `session_id_header_override`）
> - `X-Hermes-Session-Key` = **记忆作用域级**，长期稳定 → 由你手写在 `headers` 里

### 4.4 密钥怎么给两个位置（源码级答案）

**【源码】** `crates/goose/src/providers/custom_provider_config.rs`：

```rust
fn resolve_key(&self, key: &str) -> Result<String, Self::Error> {
    self.config.get_secret(key)
}
```

**【源码】** 而 `Config::get_secret` 的顺序是（`crates/goose/src/config/base.rs:920`）：

```rust
pub fn get_secret<T>(&self, key: &str) -> Result<T, ConfigError> {
    // First check environment variables (convert to uppercase)
    let env_key = key.to_uppercase();
    if let Ok(val) = env::var(&env_key) { ... return Ok(...); }
    // Then check keyring
    let values = self.all_secrets()?;
    ...
}
```

**所以两种都能用，任选一种**：

| 方式 | 做法 |
|---|---|
| **A. 环境变量**（最省事） | 让 `HERMES_API_SERVER_KEY` 这个环境变量存在（值 = Hermes 的 `API_SERVER_KEY`）。注意 key 名会被**转成大写**再查，所以 JSON 里写 `"api_key_env": "HERMES_API_SERVER_KEY"` 正好对齐 |
| **B. goose 密钥存储** | 用 `goose configure` / Desktop 建 provider 时填入 key，goose 会把它存进 keyring，并以 `<PROVIDER_ID大写>_API_KEY` 为名（**【源码】** `generate_api_key_name()` = `format!("{}_API_KEY", id.to_uppercase())`）。若手工建 JSON，需保证 `api_key_env` 与存储名一致 |

> `goose configure` 建出来的 provider 通常 `api_key_env` 会是 `HERMES_API_SERVER_API_KEY`（id 来自 display_name 规范化）。**为了可预期，建议手写 JSON**，把 `api_key_env` 固定成 `HERMES_API_SERVER_KEY`，再用环境变量提供值。

### 4.5 已知限制：Desktop 不能填 headers

**【文档】** goose 官方原文：

> *"Currently, custom headers can't be defined in goose Desktop. As a workaround, edit the provider configuration file after creation."*
> *"Currently, custom headers can only be defined for OpenAI compatible providers in the CLI."*

**操作流程因此是**：
1. 用 Desktop 或 `goose configure` 建一个 OpenAI 兼容的自定义 provider（这样密钥会正确进 keyring）；
2. 找到 `%APPDATA%\Block\goose\config\custom_providers\<id>.json`；
3. 手改 JSON，补上 `headers` 与 `session_id_header_override`；
4. 重启 goose。

> ⚠️ **未实测**：`custom_providers/*.json` 是启动时 `load_custom_providers(&dir)` 读取的，手工修改后是否需要重启、Desktop/Goose2 是否有热加载行为，我没能验证（`report.md` 未验证项 #7）。

### 4.6 另一种写法：直接用内置 `openai` provider

不想建 provider 文件时，也可以用内置 OpenAI provider + 环境变量：

```powershell
$env:GOOSE_PROVIDER = "openai"
$env:OPENAI_HOST    = "http://127.0.0.1:8642"     # 【文档】只到 root，不带路径
$env:OPENAI_BASE_PATH = "v1/chat/completions"     # 【文档】默认就是这个值
$env:OPENAI_API_KEY = "<Hermes 的 API_SERVER_KEY>"
$env:GOOSE_MODEL    = "hermes-agent"
```

**这条路的两个代价**：
- **头名不可改** → 发的是 `agent-session-id`，Hermes 不认，会话连续性丢失。
- 会话密钥只能靠 `OPENAI_CUSTOM_HEADERS` 补：**【文档】** `OPENAI_CUSTOM_HEADERS="X-Header-A=abc,X-Header-B=def"`（逗号分隔 `KEY=VALUE`）。

**【源码】** 这条路的实现细节（`openai_def.rs:96-104`）：`OPENAI_CUSTOM_HEADERS` 与 `OPENAI_API_KEY` 是**一起**从 `config.get_secrets("OPENAI_API_KEY", &["OPENAI_CUSTOM_HEADERS"])` 取的，而 `get_secrets` 的规则是 *"If primary is in env, use env for all keys"* —— 也就是说 **`OPENAI_API_KEY` 走环境变量时，`OPENAI_CUSTOM_HEADERS` 也必须走环境变量**，不能一个在 env、一个在 keyring。

**结论**：长期用、且在意会话连续性 → 用 §4.2 的**自定义 provider**路线（能改头名）。临时验证 → 这条够用。

---

## 5. 验证清单

按顺序做完 6 步，一步不过就别往下走。

| # | 做什么 | 命令 | 期望 |
|---|---|---|---|
| 1 | 进程活着 | `Invoke-RestMethod http://127.0.0.1:8642/health` | `{"status":"ok"}` |
| 2 | 认证生效｜**不带 key** | `Invoke-RestMethod http://127.0.0.1:8642/v1/models` | **401** `Invalid gateway API key (API_SERVER_KEY)` |
| 3 | 模型名 | `Invoke-RestMethod .../v1/models -Headers $h` | 模型名 = `hermes-agent`（或 profile 名） |
| 4 | **Hermes 会自己用工具** | §3.7 的对话请求（问它列文件） | 返回自然语言结果，**无 `tool_calls`**；Hermes 日志里能看到 terminal 工具执行 |
| 5 | **会话连续性** | 同 `X-Hermes-Session-Id` 连发两轮，第二轮问"我上一句问了什么" | 记得住；换一个 session id 再问则记不住 |
| 6 | **记忆生效** | goose 里吩咐一句"记住：我的项目根目录是 D:\proj" → 退出 → 重开会话再问 | 能答出来（写进 `~/.hermes/memories/MEMORY.md`） |

第 6 步落地后，去确认文件真的变了：

```powershell
Get-Content "C:\Users\Admin\AppData\Local\hermes\memories\MEMORY.md"
```

**本机现状**：`C:\Users\Admin\AppData\Local\hermes\memories\` 目前是**空的** —— 说明这套还没被写过。第一次写入成功就是你看到的第一个"自进化"证据。

---

## 6. 让 Hermes 的「自进化」真的生效

路径 B 之所以被选为"要用 Hermes 记忆/技能"的答案，就是因为它是唯一让自进化三件套（nudge + background review + curator）全活的模式（论证见 `report.md` §10）。下面是**落到本机 config.yaml 的具体动作**。

### 6.1 必须检查：`write_approval` 保持 false —— 头号杀手

**【文档】** `memory.md` 原文：

> With `write_approval: true`, **writes outside the interactive CLI are held for review and never reach the file** until approved.

而 **API server 会话正是 "outside the interactive CLI"**，两个审批入口（`/memory approve all`、`/skills approve`）都在 CLI/messaging 上 —— **goose 侧看不见也批不了 → 自进化静默失效**。

**本机现状**：`config.yaml` 里 **没有** `write_approval` 键 → 取默认值 **false** ✅ 不需要改，但**别去打开它**：

```yaml
memory:
  write_approval: false      # 本机未设置 = 默认 false
skills:
  write_approval: false      # 本机未设置 = 默认 false
```

### 6.2 钉住会话（即 §4.3 的两个头）

没有 `X-Hermes-Session-Id` 时，nudge 计数器（`_turns_since_memory` / `_iters_since_skill`）挂在 **per-session 的 agent 实例**上，每轮新 session 会让计数器从 0 开始，**永远到不了 `nudge_interval`**。
⚠️ 这是**逻辑外推，未实测**（`report.md` §10.3(2)）。

### 6.3 成本刹车：`auxiliary.background_review`

它是 **post-turn fork**，goose 是高频调用方，每问一句都可能多跑一次复盘。

**本机现状**：`config.yaml` 里 `auxiliary:` 整段是**注释掉的** → 取默认 `background_review.enabled: true`。要封顶成本，取消注释并加两行：

```yaml
auxiliary:
  background_review:
    enabled: true
    max_input_tokens: 48000                          # 单次复盘**累计**重放输入上限（≤0 = 不限）
    provider: openrouter                             # 路由到便宜模型，官方称省 3–5×
    model: google/gemini-3-flash-preview
```

**【文档】** 不设 `max_input_tokens` 时，预算按复盘模型的上下文窗口算：**窗口的 75%，上限 600,000 token**（小模型也会被约束，如 65,536 的模型得到 49,152）。

**【文档】** 路由到**不同**模型时会自动改用对话 digest（近轮逐字 + 老轮摘要），官方称 capture 质量基本不变；**同模型**复盘永远继承父对话的 reasoning effort，`reasoning_effort` 会被忽略并打印一次性警告。

### 6.4 别把工具关掉

确认这两处**不是** false，且 `agent.disabled_toolsets` 里**没有** `memory` / `skills`：

**本机现状**：`memory.memory_enabled: true` ✅、`memory.user_profile_enabled: true` ✅、`memory.nudge_interval: 10` ✅、`skills.creation_nudge_interval: 15` ✅。

### 6.5 curator（维护循环）

**本机现状**：`config.yaml` 里**没有** `curator:` 块 → 取默认（enabled、`interval_hours: 168`、`min_idle_hours: 2`、`consolidate: false`）。

**【文档】** 触发点是 *"On CLI session start, during **gateway housekeeping**, and on the Desktop/`hermes serve` maintenance timer"* —— 因为你为了跑 B 必须常驻 `hermes gateway`，**这个触发点天然满足**。这正是 C 路径做不到的地方。

---

## 7. 排错表

| 症状 | 根因 | 处置 |
|---|---|---|
| `Refusing to start: API_SERVER_KEY is a placeholder or too short (<16 chars)` | 密钥 <16 字符或形如占位符 | 用 §3.1 生成 64 位随机串。**注意别抄文档里那个 15 字符的 `your-secret-key`** |
| `Refusing to start: API_SERVER_KEY is required ... including loopback-only binds` | 完全没设 | 设 `API_SERVER_KEY`（【源码】`_api_server()` 的判定就是"合格 key 存在才注册平台"） |
| `Refusing to start: API_SERVER_KEY strength could not be verified` | fail-closed：安装损坏导致检查都跑不了 | 回 §2.1 修安装 |
| `401 {"type":"gateway_auth_error","message":"Invalid gateway API key (API_SERVER_KEY)"}` | key 不匹配；**或**你用了 `/p/<profile>/` 前缀但拿的是默认 profile 的 key | 见 §3.5；named profile 必须用它自己 `.env` 里的 key |
| `429 Too many concurrent runs (max N)` | 并发上限（默认 10） | 客户端退避重试，或调大 `gateway.api_server.max_concurrent_runs` |
| goose 指定的模型名不生效 | 【文档】**裸 `model` 默认被忽略**（除非带 `provider` 字段） | 开 `direct_model_requests: true` |
| goose 流式解析报错 / 卡住 | SSE 里混了 Hermes 自定义命名事件 `event: hermes.tool.progress` | 设 `gateway.api_server.tool_progress_events: false`（只影响 Chat Completions，内容分片不受影响） |
| goose 里"工具不生效" | 这是**设计如此**，不是 bug | 见第 0 节约束 1。要用 goose 的扩展 → 路径 A |
| 客户端读流时莫名超时 | 长工具调用期间只有 `: keepalive` 注释行 | 标准 SSE 客户端会忽略；自定义解析器必须**跳过以 `:` 开头的行** |
| 记忆不累积 | 没发 `X-Hermes-Session-Id` | 见 §4.3(1)：加 `session_id_header_override` |
| 记忆**写了但不落盘** | `write_approval: true` | 见 §6.1 |
| goose 报 `No api key passed in` | 把 key 写进了 goose 的 `config.yaml`（**会被忽略**） | 用环境变量或 keyring，见 §4.4 |

---

## 8. 回滚

| 对象 | 怎么退 |
|---|---|
| Hermes 侧 | 删掉 `.env` 里的 `API_SERVER_ENABLED` / `API_SERVER_KEY`（或把 `config.yaml` 的 `gateway.api_server.enabled` 改 false），重启 `hermes gateway` |
| goose 侧 | 删 `%APPDATA%\Block\goose\config\custom_providers\hermes_api_server.json`，重启 goose |
| 环境变量 | 去掉 `HERMES_API_SERVER_KEY` / `OPENAI_*` 那几个 |
| 影响面 | **两侧都不动应用安装目录**，升级不会冲掉；Hermes 的 `config.yaml` 有既有内容，改前建议先备份一份 |

---

## 9. 证据与未验证项

**本节新增/强化的源码级结论（`report.md` 未验证项 #2/#3 在此结清）**

| 结论 | 证据 |
|---|---|
| goose 发来的 `tools` **被忽略** | 全 `api_server*.py` 中 `.get("tools")` / `["tools"]` 零命中；`tools`/`tool_choice` 仅出现在 `fingerprint_keys` |
| 平台启用的实际判定 = **合格 key 存在** | `config_env.py::_api_server()` + `_PLATFORM_CONNECTED_CHECKERS[Platform.API_SERVER]` |
| 密钥强度 = `has_usable_secret(min_length=16)` + 反占位符 | `hermes_cli/auth.py` + `api_server.py::_api_key_passes_startup_guard()` |
| goose 可自定义会话头名 | `session_context.rs::session_id_request_builder_with_header_override` + `openai_def.rs::from_custom_config` |
| goose 密钥解析**先查环境变量**再查 keyring | `config/base.rs::get_secret` |
| `OPENAI_CUSTOM_HEADERS` 与 `OPENAI_API_KEY` 必须同在 env 或同在 keyring | `config/base.rs::get_secrets` 的 `use_env` 规则 |
| goose **容忍**响应里的未知字段（非流式安全） | `crates/goose-provider-types/src/formats/openai.rs`（5999 行）中 `deny_unknown_fields` **零命中** |

**仍未实测（请勿当结论用）**

1. **整条链路从未端到端跑通**：本机未安装 goose，且 Hermes 处于 `source-update` 中途。
2. goose 的 `session_id_header_override` 在 `goose run`（一次性调用）下 `current_session_id()` 是否为 `Some`。
3. 手改 `custom_providers/*.json` 是否需要重启、Desktop 有无热加载。
4. goose 的**流式**解析器面对 `hermes.tool.progress` 命名事件的实际表现（非流式路径已确认安全：响应类型无 `deny_unknown_fields`；流式命名事件仍属未验证，本文只给了 `tool_progress_events: false` 这个开关）。
5. `base_url` 写完整路径 `.../v1/chat/completions` 与拆成 `base_url`(root) + `base_path` 两种写法的实际差异（**【源码】** `base_url` 会被解析成 host+path 且存在 `from_base_url` 分支，但我没跑通 404 反例）。
6. `host-serve.json` 那份陈旧锁对 `hermes gateway` 启动有无影响。
7. nudge 计数器是否真因每轮新 session 归零（`report.md` §10.3(2) 的逻辑外推）。

---

## 10. 一页速查

```powershell
# ── 前置 ────────────────────────────────────────────────
hermes update; hermes doctor; hermes setup --portal

# ── Hermes 侧：生成密钥并写入 .env ──────────────────────
$bytes = New-Object byte[] 32
[System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
$key = -join ($bytes | ForEach-Object { $_.ToString('x2') })
Add-Content "C:\Users\Admin\AppData\Local\hermes\.env" "`nAPI_SERVER_ENABLED=true`nAPI_SERVER_KEY=$key"

# ── 启动 ────────────────────────────────────────────────
hermes gateway            # 期望：[API Server] listening on http://127.0.0.1:8642

# ── 自测（另开一个终端）─────────────────────────────────
$h = @{ Authorization = "Bearer $key" }
Invoke-RestMethod http://127.0.0.1:8642/health
Invoke-RestMethod http://127.0.0.1:8642/v1/models -Headers $h

# ── goose 侧：写 provider 文件 ──────────────────────────
#   %APPDATA%\Block\goose\config\custom_providers\hermes_api_server.json
#   → 内容见本文 §4.2（关键：session_id_header_override = "X-Hermes-Session-Id"）
$env:HERMES_API_SERVER_KEY = $key        # 供 api_key_env 解析

# ── 起 goose ────────────────────────────────────────────
goose session            # 选择 Hermes Agent (API server) / model = hermes-agent
```

**四条最容易被忘的**：
1. key ≥16 字符、非占位符；
2. `session_id_header_override` 不写 → 会话连续性丢失；
3. `write_approval` 必须是 false，否则记忆"写了但不落盘"；
4. goose 的扩展在这条路径上**不会被执行**——那是设计，不是故障。
