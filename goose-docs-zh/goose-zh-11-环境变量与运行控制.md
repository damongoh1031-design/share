# goose 官方文档中文手册：第 11 章　环境变量与运行控制

## 环境变量

> 原文：https://block.github.io/goose/docs/guides/environment-variables

goose 支持多种环境变量，让你可以自定义其行为。本指南按功能分组，提供了可用环境变量的完整列表。

### 模型配置

这些变量控制[语言模型](https://block.github.io/goose/docs/getting-started/providers)及其行为。

#### 基础提供方配置

这些是开始使用 goose 所需的最低限度变量。

| 变量 | 用途 | 取值 | 默认值 |
|----------|---------|---------|---------|
| `GOOSE_PROVIDER` | 指定要使用的 LLM 提供方 | [查看可用提供方](https://block.github.io/goose/docs/getting-started/providers#available-providers) | 无（必须[配置](https://block.github.io/goose/docs/getting-started/providers#configure-provider-and-model)） |
| `GOOSE_MODEL` | 指定从该提供方使用哪个模型 | 模型名称（例如 "gpt-4"、"claude-sonnet-4-20250514"） | 无（必须[配置](https://block.github.io/goose/docs/getting-started/providers#configure-provider-and-model)） |
| `GOOSE_TEMPERATURE` | 设置模型响应的 [temperature](https://medium.com/@kelseyywang/a-comprehensive-guide-to-llm-temperature-%EF%B8%8F-363a40bbc91f) | 0.0 到 1.0 之间的浮点数 | 模型特定的默认值 |
| `GOOSE_MAX_TOKENS` | 设置每次模型响应的最大 token 数（更长的响应会被截断） | 正整数（例如 4096、8192） | 模型特定的默认值 |
| `GOOSE_CACHE_TTL` | 设置 Anthropic 提示缓存的 TTL。`1h` 会让缓存前缀在空闲间隙（例如会话中途离开）保持存活，但缓存写入按 2 倍输入计费而非 1.25 倍，因此只有真正会空闲的会话才划算。无头运行（`goose run`、子代理、定时 Recipe）始终使用 `5m` | `5m`、`1h` | `5m` |

**示例**

```bash
# Basic model configuration
export GOOSE_PROVIDER="anthropic"
export GOOSE_MODEL="claude-sonnet-4-5-20250929"
export GOOSE_TEMPERATURE=0.7

# Set a lower limit for shorter interactions
export GOOSE_MAX_TOKENS=4096

# Set a higher limit for tasks requiring longer output (e.g. code generation)
export GOOSE_MAX_TOKENS=16000
```

#### 高级提供方配置

当你使用自定义端点、企业部署或特定提供方实现时，需要用到这些变量。

| 变量 | 用途 | 取值 | 默认值 |
|----------|---------|---------|---------|
| `GOOSE_PROVIDER__TYPE` | 提供方的具体类型/实现 | [查看可用提供方](https://block.github.io/goose/docs/getting-started/providers#available-providers) | 从 GOOSE_PROVIDER 推导 |
| `GOOSE_PROVIDER__HOST` | 提供方的自定义 API 端点 | URL（例如 "https://api.openai.com"） | 提供方特定的默认值 |
| `GOOSE_PROVIDER__API_KEY` | 提供方的认证密钥 | API 密钥字符串 | 无 |
| `GEMINI3_THINKING_LEVEL` | 全局设置 Gemini 3 模型的[思考级别](https://block.github.io/goose/docs/getting-started/providers#gemini-3-thinking-levels) | `low`、`high` | `low` |

**示例**

```bash
# Advanced provider configuration
export GOOSE_PROVIDER__TYPE="anthropic"
export GOOSE_PROVIDER__HOST="https://api.anthropic.com"
export GOOSE_PROVIDER__API_KEY="your-api-key-here"
```

#### Claude 思考配置

这些变量控制 Claude 的推理行为。在 Anthropic 和 Databricks 提供方上受支持。

| 变量 | 用途 | 取值 | 默认值 |
|----------|---------|---------|---------|
| `CLAUDE_THINKING_TYPE` | 控制 Claude 的推理模式 | `adaptive`、`enabled`、`disabled` | Claude 4.6+ 模型为 `adaptive`，否则为 `disabled` |

**示例**

```bash
# Claude 4.6 adaptive thinking
export GOOSE_PROVIDER=anthropic
export GOOSE_MODEL=claude-sonnet-4-6
export CLAUDE_THINKING_TYPE=adaptive

# Explicit extended thinking with the default budget
export CLAUDE_THINKING_TYPE=enabled

# Explicit extended thinking with a larger budget for complex tasks
export CLAUDE_THINKING_TYPE=enabled

# Disable Claude thinking entirely
export CLAUDE_THINKING_TYPE=disabled
```

:::tip 查看思考输出
要在 **CLI** 中查看 Claude 的思考输出，你还需要设置 `GOOSE_CLI_SHOW_THINKING=1`。在 **goose Desktop** 中，思考输出会自动显示在可折叠的 "Show reasoning" 开关中。
:::

#### 提供方重试

LLM 提供方的可配置重试参数。

##### AWS Bedrock

| 变量 | 用途 | 默认值 |
|---------------------|-------------|---------|
| `BEDROCK_MAX_RETRIES` | 放弃前的最大重试次数 | 6 |
| `BEDROCK_INITIAL_RETRY_INTERVAL_MS` | 首次重试前等待的时长（毫秒） | 2000 |
| `BEDROCK_BACKOFF_MULTIPLIER` | 每次尝试后重试间隔增长的倍数 | 2（每次翻倍） |
| `BEDROCK_MAX_RETRY_INTERVAL_MS` | 重试间隔的上限（毫秒） |  120000 |

**示例**

```bash
export BEDROCK_MAX_RETRIES=10                    # 10 retry attempts
export BEDROCK_INITIAL_RETRY_INTERVAL_MS=1000    # start with 1 second before first retry
export BEDROCK_BACKOFF_MULTIPLIER=3              # each retry waits 3x longer than the previous
export BEDROCK_MAX_RETRY_INTERVAL_MS=300000      # cap the maximum retry delay at 5 min
```

##### Databricks

| 变量 | 用途 | 默认值 |
|---------------------|-------------|---------|
| `DATABRICKS_MAX_RETRIES` | 放弃前的最大重试次数 | 3 |
| `DATABRICKS_INITIAL_RETRY_INTERVAL_MS` | 首次重试前等待的时长（毫秒） | 1000 |
| `DATABRICKS_BACKOFF_MULTIPLIER` | 每次尝试后重试间隔增长的倍数 | 2（每次翻倍） |
| `DATABRICKS_MAX_RETRY_INTERVAL_MS` | 重试间隔的上限（毫秒） |  30000 |

**示例**

```bash
export DATABRICKS_MAX_RETRIES=5                      # 5 retry attempts
export DATABRICKS_INITIAL_RETRY_INTERVAL_MS=500      # start with 0.5 second before first retry
export DATABRICKS_BACKOFF_MULTIPLIER=2               # each retry waits 2x longer than the previous
export DATABRICKS_MAX_RETRY_INTERVAL_MS=60000        # cap the maximum retry delay at 1 min
```


### 会话管理

这些变量控制 goose 如何管理对话会话和上下文。

| 变量 | 用途 | 取值 | 默认值 |
|----------|---------|---------|---------|
| `GOOSE_MAX_TURNS` | 在无用户输入的情况下允许的[最大轮数](https://block.github.io/goose/docs/guides/sessions/smart-context-management#maximum-turns) | 整数（例如 10、50、100） | 1000 |
| `GOOSE_GATEWAY_MAX_TURNS` | 网关会话（例如 Telegram）的最大轮数。仅对网关流量覆盖 `GOOSE_MAX_TURNS`，这样聊天平台可以保持比 CLI/桌面会话更严格的上限。 | 整数（例如 5、10、25） | 回退到 `GOOSE_MAX_TURNS`，再回退到 5 |
| `GOOSE_SUBAGENT_MAX_TURNS` | 设置[子代理](https://block.github.io/goose/docs/guides/context-engineering/subagents)在超时前允许完成的最大轮数。可被 Recipe 或子代理工具调用中的 [`settings.max_turns`](https://block.github.io/goose/docs/guides/recipes/recipe-reference#settings) 覆盖。 | 整数（例如 25） | 25 |
| `CONTEXT_FILE_NAMES` | 为[提示/上下文文件](https://block.github.io/goose/docs/guides/context-engineering/using-goosehints#custom-context-files)指定自定义文件名 | 字符串的 JSON 数组（例如 `["CLAUDE.md", ".goosehints"]`） | `[".goosehints", "AGENTS.md"]` |
| `GOOSE_DISABLE_SESSION_NAMING` | 禁用 AI 自动生成会话名称；避免后台模型调用，并保留默认的 "CLI Session"（goose CLI）或 "New Chat"（goose Desktop） | "1"、"true"（不区分大小写）以启用 | false |
| `GOOSE_PROMPT_EDITOR` | 用于撰写提示词、替代 CLI 输入的[外部编辑器](https://block.github.io/goose/docs/guides/goose-cli-commands#external-editor-mode) | 编辑器命令（例如 "vim"、"code --wait"） | 未设置（使用 CLI 输入） |
| `GOOSE_CLI_THEME` | CLI 响应 markdown 的[主题](https://block.github.io/goose/docs/guides/goose-cli-commands#themes) | "light"、"dark"、"ansi" | "ansi" |
| `GOOSE_CLI_LIGHT_THEME` | 浅色模式下用于语法高亮的自定义 [bat 主题](https://github.com/sharkdp/bat#adding-new-themes) | bat 主题名（例如 "Solarized (light)"、"OneHalfLight"） | "GitHub" |
| `GOOSE_CLI_DARK_THEME` | 深色模式下用于语法高亮的自定义 [bat 主题](https://github.com/sharkdp/bat#adding-new-themes) | bat 主题名（例如 "Dracula"、"Nord"） | "zenburn" |
| `GOOSE_CLI_NEWLINE_KEY` | 自定义[在 CLI 输入中插入换行](https://block.github.io/goose/docs/guides/goose-cli-commands#keyboard-shortcuts)的键盘快捷键 | 单个字符（例如 "n"、"m"） | "j"（Ctrl+J） |
| `GOOSE_CLI_BELL` | 在交互式轮次结束或需要工具审批时响铃终端 | "true"、"false" | false |
| `GOOSE_CLI_SHOW_THINKING` | 在 CLI 响应中显示模型的推理/思考输出。某些模型（例如 DeepSeek-R1、Kimi、Gemini）会暴露其内部推理过程——该变量使其在 CLI 中可见。 | 设置为任意值即启用 | 禁用 |
| `GOOSE_RANDOM_THINKING_MESSAGES` | 控制是否在处理期间显示有趣的随机消息 | "true"、"false" | "true" |
| `GOOSE_CLI_SHOW_COST` | 切换 CLI 输出中模型成本估算的显示 | "1"、"true"（不区分大小写）以启用 | false |
| `GOOSE_MAX_CODE_BLOCK_LINES` | CLI 输出中代码块被截断前的行数阈值。完整内容会保存到临时文件。 | 正整数 | 50 |
| `GOOSE_TRUNCATED_SHOW_LINES` | 代码块被截断时，在 "... (N more lines)" 消息之前显示的行数 | 正整数 | 20 |
| `GOOSE_NO_CODE_TRUNCATION` | 完全禁用代码块截断——所有代码块都完整显示 | "1"、"true"（不区分大小写）以启用 | false |
| `GOOSE_AUTO_COMPACT_THRESHOLD` | 设置 goose [自动压缩你的会话](https://block.github.io/goose/docs/guides/sessions/smart-context-management#automatic-compaction)的百分比阈值。 | 0.0 到 1.0 之间的浮点数（0.0 表示禁用） | 0.8 |
| `GOOSE_AUTO_COMPACT_TOKEN_LIMIT` | 自动压缩的绝对触发值；在自动压缩启用时，此值与百分比阈值中较早触发者生效。控制压缩何时开始，而非保证的最大请求大小。 | 正整数 | 225000 |
| `GOOSE_TOOL_CALL_CUTOFF` | 在摘要化较早的工具输出之前保持完整细节的工具调用数量，以帮助维持高效的上下文使用 | 整数（例如 5、10、20） | 根据模型上下文限制和自动压缩阈值计算得出 |
| `GOOSE_MOIM_MESSAGE_TEXT` | 每轮向 goose 的[工作记忆](https://block.github.io/goose/docs/guides/context-engineering/using-persistent-instructions)注入持久文本。适用于行为护栏或持久提醒。 | 任意文本字符串 | 未设置 |
| `GOOSE_MOIM_MESSAGE_FILE` | 一个文件的路径，其内容每轮被注入 goose 的[工作记忆](https://block.github.io/goose/docs/guides/context-engineering/using-persistent-instructions)。支持 `~/`。每个文件最大 64 KB。 | 文件路径 | 未设置 |

对于子代理，Recipe 的 [`settings.goose_provider` 和 `settings.goose_model`](https://block.github.io/goose/docs/guides/recipes/recipe-reference#settings) 优先于 `GOOSE_SUBAGENT_PROVIDER` 和 `GOOSE_SUBAGENT_MODEL` 环境变量。

**示例**

```bash
# Set a low limit for step-by-step control
export GOOSE_MAX_TURNS=5

# Set a moderate limit for controlled automation
export GOOSE_MAX_TURNS=25

# Set a reasonable limit for production
export GOOSE_MAX_TURNS=100

# Raise the per-gateway cap without changing CLI/desktop limits
# (applies to Telegram and other gateway sessions only)
export GOOSE_GATEWAY_MAX_TURNS=15

# Customize the default subagent turn limit
# Note: This can be overridden per-recipe or per-subagent using the max_turns setting
export GOOSE_SUBAGENT_MAX_TURNS=50

# Use multiple context files
export CONTEXT_FILE_NAMES='["CLAUDE.md", ".goosehints", ".cursorrules", "project_rules.txt"]'

# Disable automatic AI-generated session naming (useful for CI/headless runs)
export GOOSE_DISABLE_SESSION_NAMING=true

# Use vim for composing prompts
export GOOSE_PROMPT_EDITOR=vim

# Set the ANSI theme for the session
export GOOSE_CLI_THEME=ansi

# Customize syntax highlighting themes (uses bat themes)
export GOOSE_CLI_LIGHT_THEME="Solarized (light)"
export GOOSE_CLI_DARK_THEME="Dracula"

# Use Ctrl+N instead of Ctrl+J for newline
export GOOSE_CLI_NEWLINE_KEY=n

# Disable random thinking messages for less distraction
export GOOSE_RANDOM_THINKING_MESSAGES=false

# Show reasoning/thinking output from models that support it (e.g., DeepSeek-R1, Kimi, Gemini)
export GOOSE_CLI_SHOW_THINKING=1

# Enable model cost display in CLI
export GOOSE_CLI_SHOW_COST=true

# Show code blocks up to 100 lines before truncating
export GOOSE_MAX_CODE_BLOCK_LINES=100

# Disable code block truncation entirely (show all lines inline)
export GOOSE_NO_CODE_TRUNCATION=true

# Automatically compact sessions when 60% of available tokens are used
export GOOSE_AUTO_COMPACT_THRESHOLD=0.6

# Keep more tool calls in full detail (useful for debugging or verbose workflows)
export GOOSE_TOOL_CALL_CUTOFF=20

# Inject a persistent reminder into goose's working memory every turn
export GOOSE_MOIM_MESSAGE_TEXT="IMPORTANT: Always run tests before committing changes."

# Load persistent instructions from a file (supports ~/)
export GOOSE_MOIM_MESSAGE_FILE="~/.goose/guardrails.md"
```

#### 模型上下文限制覆盖

这些变量允许你覆盖模型的默认上下文窗口大小（token 限制）。当你使用 [LiteLLM 代理](https://docs.litellm.ai/docs/providers/litellm_proxy)或与 goose 预定义模型模式不匹配的自定义模型时，这尤其有用。

| 变量 | 用途 | 取值 | 默认值 |
|----------|---------|---------|---------|
| `GOOSE_CONTEXT_LIMIT` | 覆盖主模型的上下文限制 | 整数（token 数） | 模型特定默认值或 128,000 |
| `GOOSE_INPUT_LIMIT` | 覆盖 ollama 请求的输入提示限制（映射到 `num_ctx`） | 整数（token 数） | 未设置；Ollama 使用其模型默认值 |

**示例**

```bash
# Set context limit for main model (useful for LiteLLM proxies)
export GOOSE_CONTEXT_LIMIT=200000
# Override ollama input prompt limit
export GOOSE_INPUT_LIMIT=32000
```

更多细节和示例，请参阅[模型上下文限制覆盖](https://block.github.io/goose/docs/guides/sessions/smart-context-management#model-context-limit-overrides)。

### 工具配置

这些变量控制 goose 如何处理[工具执行](https://block.github.io/goose/docs/guides/managing-tools/goose-permissions)和[工具管理](https://block.github.io/goose/docs/guides/managing-tools/)。

| 变量 | 用途 | 取值 | 默认值 |
|----------|---------|---------|---------|
| `GOOSE_MODE` | 控制 goose 如何处理工具执行 | "auto"、"approve"、"chat"、"smart_approve" | "auto" |
| `GOOSE_TOOLSHIM` | 为输出基于文本的工具调用的模型启用[工具垫片](https://block.github.io/goose/docs/guides/tool-shim) | "1"、"true"（不区分大小写）以启用 | false |
| `GOOSE_TOOLSHIM_BACKEND` | 工具垫片的解释器后端 | "ollama"（默认）、"local"、"llama.cpp" | "ollama" |
| `GOOSE_TOOLSHIM_OLLAMA_MODEL` | 用作[工具垫片](https://block.github.io/goose/docs/guides/tool-shim)解释器的 Ollama 模型 | 模型名称（例如 llama3.2、mistral-nemo） | "mistral-nemo" |
| `GOOSE_TOOLSHIM_MODEL` | 本地工具垫片解释器后端的模型 | 模型名称 | 使用 `LOCAL_LLM_MODEL` 配置 |
| `GOOSE_CLI_MIN_PRIORITY` | 控制[工具输出](https://block.github.io/goose/docs/guides/managing-tools/adjust-tool-output)的详细程度 | 0.0 到 1.0 之间的浮点数 | 0.0 |
| `GOOSE_DEBUG` | 启用调试模式，显示完整工具参数而不截断。也可在会话中使用 `/r` [斜杠命令](https://block.github.io/goose/docs/guides/goose-cli-commands#slash-commands)切换 | "1"、"true"（不区分大小写）以启用 | false |
| `GOOSE_SHOW_FULL_OUTPUT` | 在 CLI 输出中显示完整工具参数，而不是将其截断到终端宽度 | true/false | false |
| `GOOSE_SEARCH_PATHS` | 为扩展命令向 PATH 前置额外目录 | 路径的 JSON 数组（例如 `["/usr/local/bin", "~/custom/bin"]`） | 内置搜索路径，后跟系统 PATH |
| `GOOSE_MAX_TOOL_RESPONSE_SIZE` | 单个工具响应在写入临时文件、而不内联到对话之前的最大字符数 | 正整数（例如 100000、200000） | 200000 |
| `GOOSE_SHELL` | 覆盖 Developer 扩展 shell 命令所使用的 shell | shell 可执行文件路径或名称（例如 `/bin/zsh`、`pwsh`、`C:\cygwin64\bin\bash.exe`） | Unix：若在 PATH 中找到则用 `bash`，否则 `sh`。Windows：`cmd` |

**示例**

```bash
# Enable tool interpretation
export GOOSE_TOOLSHIM=true
export GOOSE_TOOLSHIM_OLLAMA_MODEL=llama3.2
export GOOSE_MODE="auto"
export GOOSE_CLI_MIN_PRIORITY=0.2  # Show only medium and high importance output
export GOOSE_SHOW_FULL_OUTPUT=true  # Show full tool parameters in CLI output

# Add custom tool directories for extensions
export GOOSE_SEARCH_PATHS='["/usr/local/bin", "~/custom/tools", "/opt/homebrew/bin"]'

# These custom paths are checked before built-in fallback paths such as
# ~/.local/bin, /usr/local/bin on Unix, Homebrew/MacPorts paths on macOS,
# and finally the inherited system PATH.

# Lower the tool response size limit for smaller-context models
export GOOSE_MAX_TOOL_RESPONSE_SIZE=100000

# Use zsh for Developer extension shell commands
export GOOSE_SHELL=/bin/zsh
```

```bat
REM Windows: use a POSIX-like shell instead of cmd.exe
set GOOSE_SHELL=C:\cygwin64\bin\bash.exe
```

:::note
你只需把 `GOOSE_SHELL` 设置为某个 shell 可执行文件路径或名称。goose 会根据 shell 自动注入命令行标志，因此你无需自行添加：

- **PowerShell**（`pwsh`、`powershell`）→ `-NoProfile -NonInteractive -Command`
- **cmd** → `/C`
- **POSIX shell**（在 Windows 上通过 Cygwin/MSYS2 运行的 bash、zsh 等）→ `-c`
- 在 Unix 上，默认 shell（`bash`，回退到 `sh`）以 `<shell> -c` 的方式调用
:::

### 安全与隐私

这些变量控制安全功能、凭据存储和匿名使用数据收集。

| 变量 | 用途 | 取值 | 默认值 |
|----------|---------|---------|---------|
| `GOOSE_ALLOWLIST` | 控制哪些扩展可以被加载 | [允许的扩展](https://block.github.io/goose/docs/guides/allowlist)列表的 URL | 未设置 |
| `GOOSE_DISABLE_KEYRING` | 禁用用于密钥存储的系统密钥环 | 设置为任意值（例如 "1"、"true"、"yes"）以禁用。实际值无关紧要，只取决于该变量是否被设置。 | 未设置（密钥环启用） |
| `SECURITY_PROMPT_ENABLED` | 启用[提示注入检测](https://block.github.io/goose/docs/guides/security/prompt-injection-detection)以识别可能有害的命令 | true/false | false |
| `SECURITY_PROMPT_THRESHOLD` | 提示注入检测的敏感度阈值（越高越严格） | 0.01 到 1.0 之间的浮点数 | 0.8 |
| `SECURITY_PROMPT_CLASSIFIER_ENABLED` | 启用基于 ML 的提示注入检测以进行高级威胁识别 | true/false | false |
| `SECURITY_PROMPT_CLASSIFIER_ENDPOINT` | 基于 ML 的提示注入检测的分类端点 URL | URL（例如 "https://api.example.com/classify"） | 未设置 |
| `SECURITY_PROMPT_CLASSIFIER_TOKEN` | `SECURITY_PROMPT_CLASSIFIER_ENDPOINT` 的认证令牌 | 字符串 | 未设置 |
| `GOOSE_TELEMETRY_ENABLED` | 启用或禁用[匿名使用数据收集](https://block.github.io/goose/docs/guides/usage-data) | true/false | false |

**示例**

```bash
# Enable prompt injection detection with default threshold
export SECURITY_PROMPT_ENABLED=true

# Enable with custom threshold (stricter)
export SECURITY_PROMPT_ENABLED=true
export SECURITY_PROMPT_THRESHOLD=0.9

# Enable ML-based detection with external endpoint
export SECURITY_PROMPT_ENABLED=true
export SECURITY_PROMPT_CLASSIFIER_ENABLED=true
export SECURITY_PROMPT_CLASSIFIER_ENDPOINT="https://your-endpoint.com/classify"
export SECURITY_PROMPT_CLASSIFIER_TOKEN="your-auth-token"

# Control anonymous usage data collection
export GOOSE_TELEMETRY_ENABLED=false  # Disable telemetry
export GOOSE_TELEMETRY_ENABLED=true   # Enable telemetry
```

:::tip
当密钥环被禁用（或无法访问、goose [回退到基于文件的存储](https://block.github.io/goose/docs/troubleshooting/known-issues#keyring-cannot-be-accessed-automatic-fallback)）时，密钥存储在以下位置：

* macOS/Linux：`~/.config/goose/secrets.yaml`
* Windows：`%APPDATA%\Block\goose\config\secrets.yaml`
:::

### 网络配置

这些变量配置 goose 的网络代理设置。

#### OAuth 回调端口

默认情况下，goose 会在随机端口上启动一个临时本地服务器来接收 OAuth 回调。要求精确匹配 `redirect_uri`（并禁止通配符端口）的企业身份提供方会拒绝该回调。设置此变量以改用固定端口。

| 变量 | 用途 | 取值 | 默认值 |
|----------|---------|---------|---------|
| `GOOSE_OAUTH_CALLBACK_PORT` | 本地 OAuth 回调服务器的固定端口 | 端口号（例如 8080、9999） | 随机（由操作系统分配） |

**示例**

```bash
# Use a fixed port so your IdP's redirect_uri whitelist can match exactly
export GOOSE_OAUTH_CALLBACK_PORT=8080
```

然后，在你的身份提供方中注册相应的重定向 URI：
- 对于 MCP 服务器 OAuth：`http://127.0.0.1:8080/oauth_callback`
- 对于 Databricks OAuth：`http://localhost:8080`

#### HTTP 代理

goose 支持标准的 HTTP 代理环境变量，供处于企业防火墙或代理服务器之后的用户使用。

| 变量 | 用途 | 取值 | 默认值 |
|----------|---------|---------|---------|
| `HTTP_PROXY` | HTTP 连接的代理 URL | URL（例如 `http://proxy.company.com:8080`） | 无 |
| `HTTPS_PROXY` | HTTPS 连接的代理 URL（两者都设置时优先于 `HTTP_PROXY`） | URL（例如 `http://proxy.company.com:8080`） | 无 |
| `NO_PROXY` | 绕过代理的主机 | 逗号分隔的列表（例如 `localhost,127.0.0.1,.internal.com`） | 无 |

**示例**

```bash
# Configure proxy for all connections
export HTTPS_PROXY="http://proxy.company.com:8080"
export NO_PROXY="localhost,127.0.0.1,.internal,.local,10.0.0.0/8"

# Or with authentication
export HTTPS_PROXY="http://username:password@proxy.company.com:8080"
export NO_PROXY="localhost,127.0.0.1,.internal"
```

或者，也可以通过操作系统的网络设置来配置代理。如果你遇到连接问题，请参阅[企业代理或防火墙问题](https://block.github.io/goose/docs/troubleshooting/known-issues#corporate-proxy-or-firewall-issues)了解排查步骤。

### 可观测性

除了 goose 内置的[日志系统](https://block.github.io/goose/docs/guides/logs)之外，你还可以将遥测导出到外部可观测性平台，以实现高级监控、性能分析和生产洞察。

#### 可观测性配置

配置 goose 将遥测导出到任何兼容 [OpenTelemetry](https://opentelemetry.io/docs/) 的平台。

要启用导出，请设置一个收集器端点：

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
```

你可以使用 `OTEL_{SIGNAL}_EXPORTER` 独立控制每种信号（traces、metrics、logs）：

| 变量模式 | 用途 | 取值 |
|---|---|---|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | 基础 OTLP 端点（会附加 `/v1/traces` 等） | URL |
| `OTEL_EXPORTER_OTLP_{SIGNAL}_ENDPOINT` | 为特定信号覆盖端点 | URL |
| `OTEL_{SIGNAL}_EXPORTER` | 每种信号的导出器类型 | `otlp`、`console`、`none` |
| `OTEL_SDK_DISABLED` | 禁用所有 OTel 导出 | `true` |
| `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` | 在导出的 traces 中包含模型消息以及工具参数/结果 | `true`、`false`（默认） |

还支持其他变量，例如 `OTEL_SERVICE_NAME`、`OTEL_RESOURCE_ATTRIBUTES`
和 `OTEL_EXPORTER_OTLP_TIMEOUT`。
完整列表请参阅 [OTel 环境变量规范][otel-env]。

**示例：**
```bash
# Export everything to a local collector
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"

# Export only traces, disable metrics and logs
export OTEL_TRACES_EXPORTER="otlp"
export OTEL_METRICS_EXPORTER="none"
export OTEL_LOGS_EXPORTER="none"
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"

# Debug traces to console (no collector needed)
export OTEL_TRACES_EXPORTER="console"

# Sample 10% of traces (reduce volume in production)
export OTEL_TRACES_SAMPLER="parentbased_traceidratio"
export OTEL_TRACES_SAMPLER_ARG="0.1"
```

[otel-env]: https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/

#### Langfuse 集成

这些变量配置[用于可观测性的 Langfuse 集成](https://block.github.io/goose/docs/tutorials/langfuse)。

| 变量 | 用途 | 取值 | 默认值 |
|----------|---------|---------|---------|
| `LANGFUSE_PUBLIC_KEY` | Langfuse 集成的公钥 | 字符串 | 无 |
| `LANGFUSE_SECRET_KEY` | Langfuse 集成的密钥 | 字符串 | 无 |
| `LANGFUSE_URL` | Langfuse 服务的自定义 URL | URL 字符串 | 默认 Langfuse URL |
| `LANGFUSE_INIT_PROJECT_PUBLIC_KEY` | Langfuse 的备用公钥 | 字符串 | 无 |
| `LANGFUSE_INIT_PROJECT_SECRET_KEY` | Langfuse 的备用密钥 | 字符串 | 无 |

### goose ACP 服务器

这些变量配置 `goose serve` ACP 服务器进程。它们是等效 `goose serve` 标志的替代方式，最常用于[运行远程 goose 服务器](https://block.github.io/goose/docs/guides/remote-goose-server)并将 goose Desktop 连接到它。

| 变量 | 用途 | 取值 | 默认值 |
|----------|---------|---------|---------|
| `GOOSE_TLS` | 等效于 `goose serve --tls`。推荐用于远程服务器。 | `true`、`false` | `false` |
| `GOOSE_TLS_CERT_PATH` | 等效于 `goose serve --tls-cert-path`。必须与 `GOOSE_TLS_KEY_PATH` 一起使用；设置它会启用 TLS。 | 文件路径 | 无 |
| `GOOSE_TLS_KEY_PATH` | 等效于 `goose serve --tls-key-path`。必须与 `GOOSE_TLS_CERT_PATH` 一起使用；设置它会启用 TLS。 | 文件路径 | 无 |
| `GOOSE_SERVER__SECRET_KEY` | 除非使用 `--dangerously-unauthenticated`，否则 ACP 端点所需的共享密钥。 | 密钥字符串 | 必需 |

**示例**

```bash
# Start a goose ACP server reachable on the local network over TLS
GOOSE_SERVER__SECRET_KEY='a-long-random-secret' \
goose serve --platform desktop --enable-scheduler --host 0.0.0.0 --port 3000 --tls
```

当启用 TLS 时，`goose serve` 会在启动时打印一行 `GOOSED_CERT_FINGERPRINT=...`。goose Desktop 可以使用此指纹来固定服务器证书。完整设置请参阅[运行远程 goose 服务器](https://block.github.io/goose/docs/guides/remote-goose-server)。

### Recipe 配置

这些变量控制 Recipe 的发现和管理。

| 变量 | 用途 | 取值 | 默认值 |
|----------|---------|---------|---------|
| `GOOSE_RECIPE_PATH` | 用于搜索 Recipe 的额外目录 | Unix 上以冒号分隔、Windows 上以分号分隔的路径 | 无 |
| `GOOSE_RECIPE_GITHUB_REPO` | 用于搜索 Recipe 的 GitHub 仓库 | 格式："owner/repo"（例如 "aaif-goose/goose-recipes"） | 无 |
| `GOOSE_RECIPE_RETRY_TIMEOUT_SECONDS` | Recipe 成功检查命令的全局超时 | 整数（秒） | Recipe 特定的默认值 |
| `GOOSE_RECIPE_ON_FAILURE_TIMEOUT_SECONDS` | Recipe on_failure 命令的全局超时 | 整数（秒） | Recipe 特定的默认值 |

**示例**

```bash
# Add custom recipe directories
export GOOSE_RECIPE_PATH="/path/to/my/recipes:/path/to/team/recipes"

# Configure GitHub recipe repository
export GOOSE_RECIPE_GITHUB_REPO="myorg/goose-recipes"

# Set global recipe timeouts
export GOOSE_RECIPE_RETRY_TIMEOUT_SECONDS=300
export GOOSE_RECIPE_ON_FAILURE_TIMEOUT_SECONDS=60
```

### 文档配置

此变量控制 `goose-doc-guide` Skill 从何处读取 goose 文档。

| 变量 | 用途 | 取值 | 默认值 |
|----------|---------|---------|---------|
| `GOOSE_DOCS_ROOT` | `goose-doc-guide` Skill 的文档根目录，用于[离线/气隙环境文档](https://block.github.io/goose/docs/guides/offline-docs) | 包含 `goose-docs-map.md` 和 `docs/` 的本地路径或 HTTP(S) URL | `https://goose-docs.ai` |

### 开发与测试

这些变量主要用于 goose 自身的开发、测试和调试。

| 变量 | 用途 | 取值 | 默认值 |
|----------|---------|---------|---------|
| `GOOSE_PATH_ROOT` | 覆盖所有 goose 数据、配置和状态文件的根目录 | 目录的绝对路径 | 平台特定的默认值 |

**默认位置：**
- macOS：`~/Library/Application Support/Block/goose/`
- Linux：`~/.local/share/goose/`
- Windows：`%APPDATA%\Block\goose\`

设置后，goose 会在指定路径下创建 `config/`、`data/` 和 `state/` 子目录。适用于隔离测试环境、运行多种配置或 CI/CD 流水线。

**示例**

```bash
# Temporary test environment
export GOOSE_PATH_ROOT="/tmp/goose-test"

# Isolated environment for a single command
GOOSE_PATH_ROOT="/tmp/goose-isolated" goose run --recipe my-recipe.yaml

# CI/CD usage
GOOSE_PATH_ROOT="$(mktemp -d)" goose run --recipe integration-test.yaml

# Use with developer tools
GOOSE_PATH_ROOT="/tmp/goose-test" ./scripts/goose-db-helper.sh status
```

### 由 goose 控制的变量

这些变量由 goose 在执行命令期间自动设置。

| 变量 | 用途 | 取值 | 默认值 |
|----------|---------|---------|---------|
| `GOOSE_TERMINAL` | 表示某条命令正由 goose 执行，启用[自定义 shell 行为](#customizing-shell-behavior) | 设置时为 "1" | 未设置 |
| `AGENT` | 用于跨工具兼容的通用 agent 标识符，使工具和脚本能够检测自己是否正由 goose 运行 | 设置时为 "goose" | 未设置 |
| `AGENT_SESSION_ID` | 当前会话 ID，用于[会话隔离的工作流](#using-session-ids-in-workflows)，自动可供 STDIO 扩展和 Developer 扩展的 shell 命令使用 | 会话 ID 字符串（例如 `20260217_5`） | 未设置（仅在扩展/shell 上下文中设置） |

#### 自定义 Shell 行为

有时你希望 goose 使用与平常终端用法不同的命令，或具有不同的 shell 行为。常见用例包括：
- 跳过昂贵的 shell 初始化（例如语法高亮、自定义提示符）
- 阻止会让 agent 挂起的交互式命令（例如 `git commit`）
- 重定向到对 agent 友好的工具（例如用 `rg` 代替 `find`）
- 构建能检测 AI agent 执行的跨 agent 工具和脚本
- 与 MCP 服务器和 LLM 网关集成

在使用 goose CLI 时这最有用，因为 shell 命令会直接在你的终端环境中执行。

**工作原理：**

goose 提供了 `GOOSE_TERMINAL` 和 `AGENT` 变量，你可以用它们检测 goose 是否为执行 agent。

1. 当 goose 运行命令时：
   - `GOOSE_TERMINAL` 自动设置为 "1"
   - `AGENT` 自动设置为 "goose"
2. 你的 shell 配置可以检测到这一点并改变行为，同时保持你平常的终端用法不变

**示例：**

```bash
# In ~/.zshenv (for zsh users) or ~/.bashrc (for bash users)

# Block git commit when run by goose
if [[ -n "$GOOSE_TERMINAL" ]]; then
  git() {
    if [[ "$1" == "commit" ]]; then
      echo "❌ BLOCKED: git commit is not allowed when run by goose"
      return 1
    fi
    command git "$@"
  }
fi
```

```bash
# Guide goose toward better tool choices
if [[ -n "$GOOSE_TERMINAL" ]]; then
  alias find="echo 'Use rg instead: rg --files | rg <pattern> for filenames, or rg <pattern> for content search'"
fi
```

```bash
# Detect AI agent execution using standard naming convention
if [[ -n "$AGENT" ]]; then
  echo "Running under AI agent: $AGENT"
  # Apply agent-specific behavior if needed
  if [[ "$AGENT" == "goose" ]]; then
    echo "Detected goose - applying goose-specific settings"
  fi
fi
```

#### 在工作流中使用会话 ID

STDIO 扩展（通过标准输入/输出通信的本地扩展）和 Developer 扩展的 shell 命令会自动收到 `AGENT_SESSION_ID` 环境变量。这使你能够创建会话隔离的工作流，并更轻松地：
- 使用会话隔离的交接路径在多个工具调用之间协调工作
- 按会话隔离工作树或临时文件
- 调试产物与会话历史之间的关联

以下示例展示了 Recipe 如何使用会话 ID 在步骤之间交接信息：

```bash
# Create session-specific handoff directory
mkdir -p ~/Desktop/${AGENT_SESSION_ID}/handoff
echo "Results from step 1" > ~/Desktop/${AGENT_SESSION_ID}/handoff/output.txt

# Later steps in the recipe can read from the same location
cat ~/Desktop/${AGENT_SESSION_ID}/handoff/output.txt
```

### 环境变量透传

Developer 扩展的 `shell` 工具会继承你会话中的环境变量。这使得依赖环境配置的工作流成为可能，例如已认证的 CLI 操作和构建过程。

详情请参阅 [Shell 命令中的环境变量](https://block.github.io/goose/docs/mcp/developer-mcp#environment-variables-in-shell-commands)。

### 企业环境

在企业环境中部署 goose 时，管理员可能需要控制行为和基础设施，或在各团队之间强制执行一致的设置。以下环境变量较为常用：

**网络与基础设施** - 控制 goose 如何连接到外部服务和内部基础设施：
- [网络配置](#network-configuration) - 代理配置和网络设置
- [高级提供方配置](#advanced-provider-configuration) - 指向内部 LLM 端点（例如 Databricks、自定义部署）
- [模型上下文限制覆盖](#model-context-limit-overrides) - 为 LiteLLM 代理和自定义模型配置上下文限制

**安全与隐私** - 控制安全和隐私功能：
- [安全与隐私](#security-and-privacy) - 管理扩展加载、密钥存储和使用数据收集等安全与隐私设置

**合规与监控** - 跟踪使用情况并导出遥测以供审计：

- [可观测性](#observability) - 将遥测导出到监控平台（OTLP、Langfuse）

### 注意事项

- 环境变量优先于配置文件。
- 对于安全敏感的变量（例如 API 密钥），考虑使用系统密钥环而非环境变量。
- 某些变量可能需要重启 goose 才能生效。

---

## goose 日志系统

> 原文：https://block.github.io/goose/docs/guides/logs

goose 使用统一的存储系统来保存对话和交互。所有对话和交互（CLI 和 Desktop）都**本地**存储在以下位置：

| **类型**            | **类 Unix（macOS、Linux）**              | **Windows**                              |
|---------------------|----------------------------------------|---------------------------------------------|
| **命令历史** | `~/.config/goose/history.txt`          | `%APPDATA%\Block\goose\data\history.txt`    |
| **会话记录** | `~/.local/share/goose/sessions/sessions.db` | `%APPDATA%\Block\goose\data\sessions\sessions.db` |
| **系统日志**     | `~/.local/state/goose/logs/`           | `%APPDATA%\Block\goose\data\logs\`          |

:::info 隐私
goose 是一个本地应用程序，所有 goose 日志文件都存储在本地。这些日志绝不会发送到外部服务器或第三方，确保所有 goose 数据保持私密并处于你的控制之下。
请注意，goose 代表你使用的 LLM 和工具可能有它们自己的日志和隐私考量。
:::

### 命令历史

goose 跨聊天会话持久保存命令历史，让 goose 能够回忆先前的命令。

命令历史日志存储在：
* 类 Unix：` ~/.config/goose/history.txt`
* Windows：`%APPDATA%\Block\goose\data\history.txt`

### 会话记录

goose 维护会话记录，用于跟踪每个会话的对话历史和交互。
会话存储在 SQLite 数据库中，位置为：
- **类 Unix**：`~/.local/share/goose/sessions/sessions.db`
- **Windows**：`%APPDATA%\Block\goose\data\sessions\sessions.db`

:::info 会话存储迁移
在 1.10.0 版本之前，goose 将会话记录存储在 `~/.local/share/goose/sessions/` 下的各个 `.jsonl` 文件中。
当你升级到 v1.10.0 或更高版本时，现有会话会自动导入到数据库中。旧版 `.jsonl` 文件仍保留在磁盘上，但不再由 goose 管理。
:::

此数据库包含所有已保存的会话数据，包括：
- 会话元数据（ID、名称、工作目录、时间戳）
- 对话消息（用户命令、助手响应、角色信息）
- 工具调用和结果（ID、参数、响应、成功/失败状态）
- Token 使用统计
- 扩展数据和配置

会话 ID 采用 `YYYYMMDD_<COUNT>` 格式命名，例如：`20250310_2`。goose CLI 会在每个会话开始时输出会话 ID。要获取会话 ID，请使用 [`goose session list` 命令](https://block.github.io/goose/docs/guides/goose-cli-commands#session-list-options)查看所有可用会话。

有关搜索会话的详细信息，另请参阅[会话管理](https://block.github.io/goose/docs/guides/sessions/session-management)。

### 系统日志

goose 为其各个组件存储日志。CLI 和服务器日志会自动整理到按日期划分的目录中，并在两周后清理，以防止磁盘占用过多。

当[提示注入检测](https://block.github.io/goose/docs/guides/security/prompt-injection-detection)启用时，CLI 和服务器日志还会包含：
* 带有唯一 ID 的安全发现（格式：`SEC-{uuid}`）
* 与发现 ID 相关联的用户决策（允许/拒绝）

:::info
扩展可以选择性地记录日志到 `~/.local/state/goose/logs/` 下的子目录。具体的子目录结构由每个扩展的实现决定。
:::

#### 桌面应用程序日志

桌面应用程序维护自己的日志：
* macOS：`~/Library/Application Support/Goose/logs/main.log`
* Windows：`%APPDATA%\Block\goose\logs\main.log`

桌面应用程序按照平台惯例保存其自身的运行日志和状态数据，但对于实际的对话和交互，它使用标准的 goose [会话记录](#session-records)。这意味着无论你使用哪个界面与 goose 交互，你的对话历史都是一致的。

#### CLI 日志

CLI 日志存储在：
* 类 Unix：`~/.local/state/goose/logs/cli/`
* Windows：`%APPDATA%\Block\goose\data\logs\cli\`

日志被整理到按日期划分的子目录中（例如 `cli/2025-11-13/`），超过两周的子目录会被自动删除。

CLI 会话日志包含：
* 工具调用和响应
* 命令执行细节
* 会话标识符
* 时间戳

CLI 日志还会捕获与扩展相关的活动，包括：
* 工具初始化
* 工具能力和 schema
* 扩展特定的操作
* 命令执行结果
* 错误消息和调试信息
* 扩展配置状态
* 扩展特定的协议信息

#### 服务器日志

服务器日志存储在：
* 类 Unix：`~/.local/state/goose/logs/server/`
* Windows：`%APPDATA%\Block\goose\data\logs\server\`

日志被整理到按日期划分的子目录中（例如 `server/2025-11-13/`），超过两周的子目录会被自动删除。

服务器日志包含关于 goose 守护进程（`goosed`）的信息，它是一个在你的计算机上运行的本地服务器进程。该服务器组件管理 CLI、扩展和 LLM 之间的通信。

服务器日志包括：
* 服务器初始化细节
* JSON-RPC 通信日志
* 服务器能力
* 协议版本信息
* 客户端-服务器交互
* 扩展加载和初始化
* 工具定义和 schema
* 扩展指令和能力
* 调试级传输信息
* 系统能力和配置
* 操作系统信息
* 工作目录信息
* 传输层通信细节
* 消息解析和处理信息
* 请求/响应周期
* 错误状态和处理
* 扩展初始化序列

#### LLM 请求日志

LLM 请求日志捕获发送给语言模型提供方的原始请求和响应数据：
* 类 Unix：`~/.local/state/goose/logs/llm_request.*.jsonl`
* Windows：`%APPDATA%\Block\goose\data\logs\llm_request.*.jsonl`

这些日志使用编号轮换系统，保留最近 10 个已完成的请求（`llm_request.0.jsonl` 到 `llm_request.9.jsonl`）。每个日志包含模型配置、输入负载、响应数据和 token 使用信息。

---

## 设置 LLM 速率限制

> 原文：https://block.github.io/goose/docs/guides/handling-llm-rate-limits-with-goose

速率限制是指在特定时间范围内限制用户或应用程序可以向 LLM API 发送的请求数量的过程。LLM 提供方实施速率限制的目的是管理资源和防止滥用。

由于 goose 在实现你的任务时工作得非常快，你可能需要管理提供方施加的速率限制。如果你频繁触达速率限制，考虑升级你的 LLM 方案以访问更高层级的限制，或[配置一个提供方](https://block.github.io/goose/docs/getting-started/providers#configure-provider-and-model)，它内置了速率限制：

:::info
goose 支持对这两个提供方进行自动设置，会引导你完成 OAuth 账户创建和安全的 API 密钥生成。
:::

- **Tetrate Agent Router**：面向 AI 模型的统一 API 网关，包括 Claude、Gemini、GPT、开放权重模型等。这是开发者通往企业级路由、内置速率限制和自动故障转移的最短路径。

  在 [router.tetrate.ai](https://router.tetrate.ai/dashboard) 管理你的账户。

- **OpenRouter**：为 LLM 提供统一接口，让你可以自动选择并在不同提供方之间切换——全部在单一计费方案下。使用 OpenRouter，你可以使用免费模型，或为付费模型购买额度。

  在 [openrouter.ai](https://openrouter.ai) 管理你的账户。

当 goose 通过其中一个提供方发送你的请求时，该提供方会在必要时自动切换模型，以避免因速率限制而中断。

---

## 更新 goose

> 原文：https://block.github.io/goose/docs/guides/updating-goose

goose CLI 和桌面应用程序正处于活跃且持续的开发中。要获取最新功能和修复，你应该定期使用以下说明更新你的 goose 客户端。

<Tabs>
  <TabItem value="mac" label="macOS" default>
    <Tabs groupId="interface">
      <TabItem value="ui" label="goose Desktop" default>
        将 goose 更新到最新的稳定版本。

        <DesktopAutoUpdateSteps />

        **手动下载并安装更新：**
        1. <MacDesktopInstallButtons/>
        2. 解压下载的 zip 文件
        3. 将解压出的 `Goose.app` 文件拖到 `Applications` 文件夹以覆盖当前版本
        4. 启动 goose Desktop

      </TabItem>
      <TabItem value="cli" label="goose CLI">
        你可以通过运行以下命令来更新 goose：

        ```sh
        goose update
        ```

        其他[选项](https://block.github.io/goose/docs/guides/goose-cli-commands#update-options)：

        ```sh
        # Update to latest canary (development) version
        goose update --canary

        # Update and reconfigure settings
        goose update --reconfigure
        ```

        或者你可以再次运行[安装](https://block.github.io/goose/docs/getting-started/installation)脚本：

        ```sh
        curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | CONFIGURE=false bash
        ```

        要检查你当前的 goose 版本，请使用以下命令：

        ```sh
        goose --version
        ```
      </TabItem>
    </Tabs>
  </TabItem>

  <TabItem value="linux" label="Linux">
    <Tabs groupId="interface">
      <TabItem value="ui" label="goose Desktop" default>
        将 goose 更新到最新的稳定版本。

        <DesktopAutoUpdateSteps />

        **手动下载并安装更新：**
        1. <LinuxDesktopInstallButtons/>

        #### 对于基于 Debian/Ubuntu 的发行版
        2. 在终端中，导航到下载的 DEB 文件
        3. 运行 `sudo dpkg -i (filename).deb`
        4. 从应用程序菜单启动 goose
      </TabItem>
      <TabItem value="cli" label="goose CLI">
        你可以通过运行以下命令来更新 goose：

        ```sh
        goose update
        ```

        其他[选项](https://block.github.io/goose/docs/guides/goose-cli-commands#update-options)：

        ```sh
        # Update to latest canary (development) version
        goose update --canary

        # Update and reconfigure settings
        goose update --reconfigure
        ```

        或者你可以再次运行[安装](https://block.github.io/goose/docs/getting-started/installation)脚本：

        ```sh
        curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | CONFIGURE=false bash
        ```

        要检查你当前的 goose 版本，请使用以下命令：

        ```sh
        goose --version
        ```
      </TabItem>
    </Tabs>
  </TabItem>

  <TabItem value="windows" label="Windows">
    <Tabs groupId="interface">
      <TabItem value="ui" label="goose Desktop" default>
        将 goose 更新到最新的稳定版本。

        <DesktopAutoUpdateSteps />

        **手动下载并安装更新：**
        1. <WindowsDesktopInstallButtons/>
        2. 解压下载的 zip 文件
        3. 运行可执行文件以启动 goose Desktop 应用
      </TabItem>
      <TabItem value="cli" label="goose CLI">
        你可以通过运行以下命令来更新 goose：

        ```sh
        goose update
        ```

        其他[选项](https://block.github.io/goose/docs/guides/goose-cli-commands#update-options)：

        ```sh
        # Update to latest canary (development) version
        goose update --canary

        # Update and reconfigure settings
        goose update --reconfigure
        ```

        或者在 **Git Bash**、**MSYS2** 或 **PowerShell** 中再次运行[安装](https://block.github.io/goose/docs/getting-started/installation)脚本，以在 Windows 上原生更新 goose CLI：

        ```bash
        curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | CONFIGURE=false bash
        ```

        要检查你当前的 goose 版本，请使用以下命令：

        ```sh
        goose --version
        ```

        <details>
        <summary>通过 Windows Subsystem for Linux（WSL）更新</summary>

        要更新你的 WSL 安装，请使用 `goose update` 或通过 WSL 再次运行安装脚本：

        ```sh
        curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | CONFIGURE=false bash
        ```

       </details>
      </TabItem>
    </Tabs>
  </TabItem>
</Tabs>

:::info 在 CI/CD 中更新
如果你在 CI 或其他非交互式环境中运行 goose，请使用 `GOOSE_VERSION` 固定特定版本以实现可复现的安装。完整示例和使用细节请参阅 [CI/CD 环境](https://block.github.io/goose/docs/tutorials/cicd)。
:::

---

## 离线/气隙环境文档

> 原文：https://block.github.io/goose/docs/guides/offline-docs

`goose-doc-guide` Skill 在回答 goose 特定问题之前会读取官方 goose 文档。默认情况下，它从 `https://goose-docs.ai` 读取。在离线或气隙环境中，请通过设置 `GOOSE_DOCS_ROOT` 让 goose 改用**本地副本**。

- 如果设置了 `GOOSE_DOCS_ROOT`（在 `config.yaml` 中或环境中），goose 会将其用作文档根目录——可以是本地文件系统路径或 HTTP(S) URL。
- 如果未设置，goose 会回退到 `https://goose-docs.ai`。

当根目录是本地路径时，goose 使用其文件工具读取文档；不需要网络访问。

### 文档布局

文档根目录包含一个文档映射和一个 `docs/` 目录树：

```
<docs-root>/
├── goose-docs-map.md
└── docs/
    ├── getting-started/...
    └── guides/...
```

`goose-docs-map.md` 是 Skill 首先搜索的索引；它读取的每个页面都由其中列出的路径引用。

### 构建本地文档根目录

从 goose 检出构建文档，并使用与你的 goose 二进制相同的版本，以便文档与运行时匹配。标准文档构建已经生成 goose 所需的一切——一个 `goose-docs-map.md` 索引和一个由 markdown 文件组成的 `docs/` 目录树——因此不需要自定义工具：

```bash
git checkout v1.41.0   # match your goose binary version
cd documentation
npm run build
```

这会将文档根目录写入 `documentation/build/`，其中包含：

```
build/
├── goose-docs-map.md
└── docs/
    ├── getting-started/...
    └── guides/...
```

`npm run build` 需要 registry 访问，因此请在联网环境中运行它。然后将生成的 `build/` 目录复制到你的气隙目标位置（例如 `/opt/goose-docs`），并将 `GOOSE_DOCS_ROOT` 指向它。

### 配置 goose

在 `config.yaml` 中设置 `GOOSE_DOCS_ROOT`：

```yaml
GOOSE_DOCS_ROOT: "/opt/goose-docs"
```

或通过环境变量：

```bash
export GOOSE_DOCS_ROOT=/opt/goose-docs
```

对于托管分发，将文档目录树烘焙到你的镜像中，并在随附的 `config.yaml` 或启动器环境中设置 `GOOSE_DOCS_ROOT`。

### 注意事项

- goose 回答中的文档链接始终渲染为规范的 `https://goose-docs.ai/...` URL，即使是从本地读取。
- 自定义 HTTP(S) 镜像同样可行：将 `GOOSE_DOCS_ROOT` 设置为其根 URL。
- 关于离线的 MCP 扩展运行时问题，请参阅[气隙/离线环境问题](https://block.github.io/goose/docs/troubleshooting/known-issues#airgappedoffline-environment-issues)。
