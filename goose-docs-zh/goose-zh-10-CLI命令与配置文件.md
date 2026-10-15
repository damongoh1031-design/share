# goose 官方文档中文手册：第 10 章　CLI 命令与配置文件

## CLI 命令

> 原文：https://block.github.io/goose/docs/guides/goose-cli-commands

goose 提供命令行界面（CLI），其中的命令可用于管理会话、配置和扩展。本指南涵盖主要的 CLI 命令与交互式会话功能。

### 标志命名约定

goose CLI 遵循一致的标志命名模式，使命令直观且可预测：

- **`--session-id`**：用于会话标识符（例如 `20251108_1`）
- **`--schedule-id`**：用于计划任务标识符（例如 `daily-report`）
- **`-n, --name`**：用于人类可读的名称
- **`--path`**：用于文件路径（旧版支持）
- **`-o, --output`**：用于输出文件路径
- **`-r, --resume` 或 `-r, --regex`**：依上下文而定（会话用 resume，过滤器用 regex）
- **`-v, --verbose`**：用于详细输出
- **`-l, --limit`**：用于限制结果数量
- **`-f, --format`**：用于指定输出格式
- **`-w, --working_dir`**：用于工作目录过滤

#### 核心命令

##### help

显示帮助菜单。

**用法：**
```bash
goose --help
```

---

##### configure

配置 goose 设置 —— 提供方、扩展等。

**用法：**
```bash
goose configure
```

:::tip 输入以过滤
在 `goose configure` 的菜单中选择时，直接开始输入即可实时过滤选项。这对提供方、扩展和工具列表都有效。
:::

---

##### info [options]

显示 goose 信息，包括版本、配置文件位置、会话存储和日志。

**选项：**
- **`-v, --verbose`**：显示详细的配置设置，包括环境变量和已启用的扩展

**用法：**
```bash
goose info
```

---

##### version

查看你当前安装的 goose 版本。

**用法：**
```bash
goose --version
```

---

##### update [options]

将 goose CLI 更新到较新版本。

**选项：**
- **`--canary, -c`**：更新到 canary（开发）版本而非稳定版本
- **`--reconfigure, -r`**：在更新过程中强制 goose 重置配置设置

**用法：**
```bash
# Update to latest stable version
goose update

# Update to latest canary version
goose update --canary

# Update and reconfigure settings
goose update --reconfigure
```

---

##### completion

生成针对特定 shell 的脚本，以启用 goose 命令、子命令和选项的 Tab 补全。脚本会打印到 stdout，因此你需要将其重定向到适合你的 shell 的位置，然后重新加载或 source 你的 shell 配置。

安装后，你可以：

- 按 Tab 查看可用的命令和子命令
- 自动补全命令名和标志
- 无需查看 `--help` 即可发现选项

**参数：**
- **`<SHELL>`**：要为其生成补全的 shell。支持的 shell：`bash`、`elvish`、`fish`、`nu`、`powershell`、`zsh`

**用法：**
```bash
# Generate completion script for your shell (outputs to stdout)
goose completion bash
goose completion zsh
goose completion fish
goose completion nu
```

**按 shell 安装：**

<Tabs groupId="shells">
<TabItem value="zsh" label="Zsh" default>

将这一行添加到你的 `~/.zshrc`：

```bash
eval "$(goose completion zsh)"
```

然后重新加载你的 shell：
```bash
source ~/.zshrc
```

</TabItem>
<TabItem value="bash" label="Bash">

将这一行添加到你的 `~/.bashrc` 或 `~/.bash_profile`：

```bash
eval "$(goose completion bash)"
```

然后重新加载你的 shell：
```bash
source ~/.bashrc
```

</TabItem>
<TabItem value="fish" label="Fish">

```bash
goose completion fish > ~/.config/fish/completions/goose.fish
```

然后重启终端或运行 `exec fish`。

</TabItem>
<TabItem value="nu" label="Nushell">

```nu
let autoload_dir = ($nu.user-autoload-dirs | first)
mkdir $autoload_dir
goose completion nu | save --force ($autoload_dir | path join "goose.nu")
```

然后重启 Nushell 或运行：
```nu
source (($nu.user-autoload-dirs | first) | path join "goose.nu")
```

</TabItem>
<TabItem value="powershell" label="PowerShell">

将这一行添加到你的 PowerShell 配置文件：

```powershell
goose completion powershell | Out-String | Invoke-Expression
```

然后重新加载你的配置文件：
```powershell
. $PROFILE
```

</TabItem>
</Tabs>

:::tip 测试
安装并重新加载 shell 后，输入 `goose ` 并按 Tab 查看可用命令，或输入 `goose session --` 并按 Tab 查看可用选项，以测试补全。
:::

---

#### 会话管理

:::info 会话存储迁移
从 1.10.0 版本开始，goose 使用 SQLite 数据库（`sessions.db`）而非单独的 `.jsonl` 文件。
你现有的会话会自动导入数据库。旧版 `.jsonl` 文件仍保留在磁盘上，但不再由 goose 管理。
:::

##### session [options]

启动或恢复交互式聊天会话。

**基本选项：**
- **`--session-id <session_id>`**：通过 ID 指定会话（例如 '20251108_1'）
- **`-n, --name <name>`**：为会话指定一个名称
- **`--path <path>`**：通过文件路径指定会话的旧版参数
- **`-r, --resume`**：恢复之前的会话
- **`--edit`**：以 YAML 形式在你的编辑器（`$VISUAL` / `$EDITOR` / `vi`）中打开会话的对话。编辑、修剪或重写消息，然后保存并关闭，以编辑后的对话继续会话。必须与 `--resume` 一起使用。可与 `--fork` 组合，从编辑结果创建新会话。
- **`--fork`**：创建一个复制了历史记录的新会话副本。必须与 `--resume` 一起使用。提供 `--name` 或 `--session-id` 以 fork 特定会话。否则，fork 最近的会话。
- **`--history`**：恢复会话时显示之前的消息
- **`--container <container_id>`**：在 [Docker 容器](https://block.github.io/goose/docs/tutorials/goose-in-docker#running-extensions-in-docker-containers)内运行扩展。
- **`--debug`**：启用调试模式，以输出完整的工具响应、详细的参数值和完整文件路径
- **`--max-tool-repetitions <NUMBER>`**：设置同一工具以相同参数连续调用的最大次数。有助于防止无限循环。
- **`--max-turns <NUMBER>`**：设置无用户输入时允许的最大轮数（默认：1000）

**扩展选项：**
- **`--with-extension <command>`**：添加 stdio 扩展。格式：`[name:]ENV1=val1 command args...`。若不提供可选的 `name:`，扩展将以命令命名 —— 对于任何通过启动器（`npx`、`python -m ...`、`uvx`）启动的扩展，这个命令是启动器而非服务器本身。该名称会作为服务器暴露的每个工具的前缀（`npx__search`），而由同一启动器启动的扩展否则会发生冲突，因此 goose 会用它们的完整命令行来命名冲突的扩展。显式指定名称以控制它：`--with-extension "memory:npx -y @modelcontextprotocol/server-memory"` 会暴露 `memory__search`。
- **`--with-streamable-http-extension <url>`**：通过 Streamable HTTP 添加远程扩展
- **`--with-builtin <id>`**：启用内置扩展（例如 'developer'、'computercontroller'）

**用法：**
```bash
# Start a basic session
goose session -n my-project

# Resume a previous session
goose session --resume -n my-project
goose session --resume --session-id 20251108_2
goose session --resume --path ./session.json    # exported session
goose session --resume --path ./session.jsonl   # legacy session storage

# Fork a specific session by name
goose session --resume --fork --name my-project

# Fork the most recent session and show message history
goose session --resume --fork --history

# Edit a session's conversation in your editor
goose session --resume --session-id 20251108_2 --edit

# Edit and fork — create a new session from the edited conversation
goose session --resume --session-id 20251108_2 --fork --edit --history

# Start with extensions
goose session --with-extension "npx -y @modelcontextprotocol/server-memory"

# Name an extension explicitly (tools become memory__*, not npx__*)
goose session --with-extension "memory:npx -y @modelcontextprotocol/server-memory"
goose session --with-builtin developer
goose session --with-streamable-http-extension "http://localhost:8080/mcp"

# Advanced: Mix multiple extension types
goose session \
  --with-extension "echo hello" \
  --with-streamable-http-extension "http://localhost:8080/mcp" \
  --with-builtin "developer"

# Control session behavior
goose session -n my-session --debug --max-turns 25
```

---

##### session list [options]

列出所有已保存的会话。

**选项：**
- **`-f, --format <format>`**：指定输出格式（`text` 或 `json`）。默认为 `text`
- **`--ascending`**：按日期升序排列会话（最旧的在前）
- **`-w, --working_dir <path>`**：按工作目录过滤会话
- **`-l, --limit <number>`**：限制结果数量

**用法：**
```bash
# List all sessions in text format (default)
goose session list

# List sessions in JSON format
goose session list --format json

# Sort sessions by date in ascending order
goose session list --ascending

# Filter sessions by working directory
goose session list -w ~/projects/myapp

# List only the 10 most recent sessions
goose session list --limit 10
```

---

##### session remove [options]

删除一个或多个已保存的会话。

**选项：**
- **`--session-id <session_id>`**：通过会话 ID 删除特定会话
- **`-n, --name <name>`**：通过名称删除特定会话
- **`-r, --regex <pattern>`**：删除匹配正则模式的会话
- **`--path <path>`**：通过文件路径删除特定会话（旧版）

**用法：**
```bash
# Interactive removal (prompts you to choose sessions)
goose session remove

# Remove a specific session by ID
goose session remove --session-id 20251108_3

# Remove a specific session by name
goose session remove -n my-project

# Remove all sessions starting with "project-"
goose session remove -r "project-.*"

# Remove all sessions containing "migration"
goose session remove -r ".*migration.*"
```

:::caution
会话删除是永久性的，无法撤销。goose 会显示将要删除哪些会话，并在删除前请求确认。
:::

---

##### session rename [options]

重命名已保存的会话。如果未提供会话 ID，goose 会提示你交互式地选择一个会话。

**选项：**
- **`--session-id <session_id>`**：通过会话 ID 重命名特定会话（例如 `20251108_3`）
- **`-n, --new-name <name>`**：会话的新名称（必填）

**用法：**
```bash
# Rename a specific session by ID
goose session rename --session-id 20251108_3 --new-name my-project

# Interactive selection (prompts you to choose a session)
goose session rename --new-name my-project
```

---

##### session export [options]

以不同格式导出会话，用于备份、共享、迁移或文档目的。

**选项：**
- **`--session-id <session_id>`**：通过 ID 导出特定会话
- **`-n, --name <name>`**：通过名称导出特定会话
- **`--path <path>`**：通过文件路径导出特定会话（旧版）
- **`-o, --output <file>`**：将导出内容保存到文件（默认：stdout）
- **`--format <format>`**：输出格式：`markdown`、`json`、`yaml`。默认为 `markdown`

**导出格式：**
- **`json`**：完整的会话备份，保留所有数据，包括对话历史、元数据和设置
- **`yaml`**：以 YAML 格式的完整会话备份
- **`markdown`**：默认格式，创建格式良好、可读的对话版本，用于文档和共享

**用法：**
```bash
# Interactive export
goose session export

# Export specific session as JSON for backup
goose session export -n my-session --format json -o session-backup.json

# Export specific session as readable markdown
goose session export -n my-session -o session.md

# Export to stdout in different formats
goose session export --session-id 20251108_4 --format json
goose session export -n my-session --format yaml

# Export session by path (legacy)
goose session export --path ./my-session.jsonl -o exported.md
```

---

##### session diagnostics [options]

生成一份全面的诊断 JSON 报告，用于排查特定会话的问题。

**选项：**
- **`--session-id <session_id>`**：通过 ID 为特定会话生成诊断
- **`-n, --name <name>`**：通过名称为特定会话生成诊断
- **`--path <path>`**：通过文件路径为特定会话生成诊断（旧版）
- **`-o, --output <file>`**：将诊断报告保存到特定文件路径（默认：`diagnostics_{session_id}.json`）

**包含内容：**
- **系统信息**：应用版本、操作系统、架构和时间戳
- **会话数据**：指定会话的完整对话消息和历史记录
- **配置文件**：你的[配置文件](https://block.github.io/goose/docs/guides/config-files)（如果存在）
- **日志文件**：用于调试的近期应用日志

**用法：**
```bash
# Generate diagnostics for a specific session by ID
goose session diagnostics --session-id 20251108_5

# Generate diagnostics for a session by name
goose session diagnostics -n my-project-session

# Save diagnostics to a custom location
goose session diagnostics --session-id 20251108_5 -o /path/to/my-diagnostics.json

# Interactive selection (prompts you to choose a session)
goose session diagnostics
```

:::warning 隐私提示
诊断报告包含你的会话消息和系统信息。如果你的会话包含敏感数据（API 密钥、个人信息、专有代码），在公开分享前请检查内容。
:::

:::tip
在报告 bug 之前生成诊断，以提供有助于更快解决问题的技术细节。该 JSON 文件可以附加到 GitHub issue 或与支持团队共享。
:::

---

#### 任务执行

##### run [options]

从指令文件或 stdin 执行命令。查看[完整指南](https://block.github.io/goose/docs/guides/running-tasks)了解更多信息。

**输入选项：**
- **`-i, --instructions <FILE>`**：包含命令的指令文件的路径。使用 `-` 表示 stdin
- **`-t, --text <TEXT>`**：直接提供给 goose 的输入文本
- **`--system <TEXT>`**：提供额外的系统指令以自定义该 Agent 的行为
- **`--recipe <RECIPE_FILE_NAME> <OPTIONS>`**：在当前会话中加载自定义 Recipe
- **`--params <KEY=VALUE>`**：传递给 Recipe 文件的键值参数。可多次指定
- **`--sub-recipe <RECIPE>`**：指定与主 Recipe 一起包含的子 Recipe。可多次指定

**会话选项：**
- **`-s, --interactive`**：处理完初始输入后以交互模式继续
- **`-n, --name <name>`**：此次运行会话的名称（例如 `daily-tasks`）
- **`-r, --resume`**：从之前的运行恢复
- **`--path <PATH>`**：此次运行会话的路径（例如 `./playground.jsonl`）。用于旧版基于文件的会话存储。
- **`--container <container_id>`**：在 [Docker 容器内](https://block.github.io/goose/docs/tutorials/goose-in-docker#running-extensions-in-docker-containers)运行扩展。
- **`--no-session`**：运行 goose 命令而不创建或存储会话文件

**扩展选项：**
- **`--with-extension <COMMAND>`**：添加 stdio 扩展（可多次使用）
- **`--with-streamable-http-extension <URL>`**：通过 Streamable HTTP 添加远程扩展（可多次使用）
- **`--with-builtin <name>`**：按名称添加内置扩展（例如 'developer' 或多个：'developer,github'）

**控制选项：**
- **`--debug`**：输出完整的工具响应、详细的参数值和完整文件路径
- **`--max-tool-repetitions <NUMBER>`**：同一工具以相同参数连续调用的最大次数。有助于防止无限循环
- **`--max-turns <NUMBER>`**：无用户输入时允许的最大轮数（默认：1000）
- **`--explain`**：显示 Recipe 的标题、描述和参数
- **`--render-recipe`**：打印渲染后的 Recipe 而非运行它
- **`-q, --quiet`**：静默模式。抑制非响应输出，仅将模型响应打印到 stdout
- **`--output-format <FORMAT>`**：输出格式（`text`、`json` 或 `stream-json`）。默认为 `text`。用于自动化和脚本时使用 JSON 结构化输出：`json` 在完成后给出结果，`stream-json` 在事件发生时给出事件
- **`--provider`**：指定此次会话使用的提供方（覆盖环境变量）
- **`--model`**：指定此次会话使用的模型（覆盖环境变量）

**用法：**
```bash
# Run from instruction file
goose run --instructions plan.md

# Load a recipe with a prompt that goose executes and then exits  
goose run --recipe recipe.yaml

# Load a recipe and stay in an interactive session
goose run --recipe recipe.yaml --interactive

# Load a recipe in debug mode
goose run --recipe recipe.yaml --debug

# Show recipe details
goose run --recipe recipe.yaml --explain

# Run a recipe with parameters
goose run --recipe recipe.yaml --params environment=production --params region=us-west-2

# Run instructions from a file without session storage
goose run --no-session -i instructions.txt

# Run with a specified provider and model
goose run --provider anthropic --model claude-4-sonnet -t "initial prompt"

# Run with limited turns before prompting user
goose run --recipe recipe.yaml --max-turns 10
```

---

##### review [options] [range]

使用 goose 审查当前的 git diff。默认情况下，`goose review` 将工作树与 `HEAD` 进行比较；传入诸如 `main...HEAD` 的范围以审查特定的 diff。

`goose review` 可以从 `.agents/checks/*.md` 发现审查检查项，并从 `.agents/REVIEW.md` 发现作用域内的审查指令。

**选项：**
- **`--prompt <FILE>`**：使用自定义的基础审查提示词
- **`--model <MODEL>`**：为主审查 Agent 以及未声明自身模型的检查项设置默认模型
- **`--provider <PROVIDER>`**：为主审查 Agent 设置提供方
- **`--override-model <MODEL>`**：强制每个发现的检查项使用此模型
- **`--turn-limit <N>`**：为编排的审查子进程和检查项设置默认轮数限制
- **`--dry-run`**：打印组装好的审查提示词和发现的检查项，而不运行审查
- **`-q, --quiet`**：抑制底层 Agent 的非结果输出
- **`--no-orchestrate`**：禁用默认的 Rust 驱动的并行编排器，改用单提示词路径。声明了 `tools` 的检查项会被拒绝，因为此路径无法强制执行按检查项的工具白名单。
- **`-i, --instructions <TEXT>`**：添加自由形式的审查指令
- **`-f, --files <FILE>...`**：将审查限制在特定文件
- **`-c, --check-filter <NAME>...`**：仅运行名称匹配的检查项
- **`-s, --check-scope <DIR>`**：在特定目录中搜索 `.agents/checks/*.md`
- **`--checks-only`**：跳过主正确性检查，仅运行检查子代理
- **`--summary-only`**：仅打印 diff 摘要
- **`--severity <LEVEL>`**：显示的最低严重级别。默认为 `medium`；使用 `low` 显示每一条发现

**用法：**
```bash
# Review the working tree against HEAD
goose review

# Review a branch range
goose review main...HEAD

# Add review intent
goose review --instructions "This is a refactor; flag behavior changes"

# Review only selected files
goose review --files crates/goose/src/agents/agent.rs documentation/docs/guides/goose-cli-commands.md

# Preview the assembled prompt and discovered checks
goose review --dry-run

# Run only named checks
goose review --check-filter security performance --checks-only
```

---

##### recipe

用于验证 Recipe 文件、管理 Recipe 共享、列出可用 Recipe，以及在 goose 桌面版中打开 Recipe。

**命令：**
- **`deeplink <RECIPE_NAME>`**：为 Recipe 文件生成可共享的链接
  - **`-p, --param <KEY=VALUE>`**：预填 Recipe 参数（可多次指定）
- **`list [OPTIONS]`**：列出本地目录和已配置的 GitHub 仓库中所有可用的 Recipe
  - **`--format <FORMAT>`**：输出格式（`text` 或 `json`）。默认为 `text`
  - **`-v, --verbose`**：显示详细信息，包括 Recipe 标题和完整文件路径
- **`open <RECIPE_NAME>`**：在 goose 桌面版中直接打开 Recipe 文件
  - **`-p, --param <KEY=VALUE>`**：预填 Recipe 参数（可多次指定）
- **`validate <RECIPE_NAME>`**：验证 Recipe 文件

**用法：**
```bash
# Generate a shareable link
goose recipe deeplink my-recipe.yaml

# Generate a deeplink and provide parameter values
goose recipe deeplink my-recipe.yaml -p environment=production -p region=us-west-2

# List all available recipes
goose recipe list

# List recipes with detailed information
goose recipe list --verbose

# List recipes in JSON format for automation
goose recipe list --format json

# Open a recipe in goose desktop
goose recipe open my-recipe.yaml

# Open a recipe by name
goose recipe open my-recipe

# Open a recipe and provide parameter value
goose recipe open my-recipe --param name=myproject

# Validate a recipe file
goose recipe validate my-recipe.yaml

# Get help about recipe commands
goose recipe help
```

---

##### plugin

安装和更新基于 git 的插件，这些插件提供 Skill 或其他 Open Plugins 组件。

**命令：**
- **`install [OPTIONS] <URL>`**：从 git 仓库 URL 安装插件
  - **`--auto-update`**：在加载插件 Skill 之前自动检查更新
- **`update <NAME>`**：按名称更新已安装的基于 git 的插件

**用法：**
```bash
# Install a plugin from a git repository
goose plugin install https://github.com/example/my-goose-plugin.git

# Install a plugin and enable automatic update checks
goose plugin install --auto-update https://github.com/example/my-goose-plugin.git

# Update an installed plugin manually
goose plugin update my-plugin
```

已安装的插件存储在 `~/.agents/plugins/<plugin-name>/` 下。有关插件提供的 Skill、Hook 和更新行为的更多信息，请参阅[插件指南](https://block.github.io/goose/docs/guides/context-engineering/plugins)。

---

##### skills

列出 goose Agent 可用的 Skill。

**命令：**
- **`list`**：列出已安装和可发现的 Skill，包括 token 数量和来源位置

**用法：**
```bash
goose skills list
```

---

##### local-models

搜索、下载、列出和删除本地推理模型。

:::info
此命令在包含本地推理支持的 goose 构建中可用。
:::

**命令：**
- **`search <QUERY>`**：在 Hugging Face 中搜索兼容的 GGUF 和 MLX 模型
  - **`-l, --limit <NUMBER>`**：显示的最大结果数。默认为 `10`
- **`download <SPEC>`**：从搜索结果下载并注册模型，例如 `user/repo:Q4_K_M`
- **`list`**：列出已下载的本地模型
- **`delete <ID>`**：删除已下载的本地模型

**别名：** `lm`

**用法：**
```bash
# Search for local models
goose local-models search qwen --limit 5

# Download a model from a search result
goose local-models download 'user/repo:Q4_K_M'

# List downloaded models
goose local-models list

# Delete a downloaded model
goose local-models delete user/repo:Q4_K_M
```

---

##### schedule

通过按[计划](https://block.github.io/goose/docs/guides/recipes/session-recipes.md#schedule-recipe)运行 Recipe 来实现自动化。

**命令：**
- `add <OPTIONS>`：创建一个新的计划任务。将 Recipe 的当前版本复制到 `~/.local/share/goose/scheduled_recipes`
- `list`：查看所有计划任务
- `remove`：删除一个计划任务
- `sessions`：列出由计划 Recipe 创建的会话
- `run-now`：立即运行一个计划 Recipe
- `cron-help`：显示 cron 表达式示例和帮助

**选项：**
- `--schedule-id <NAME>`：计划任务的唯一 ID（例如 `daily-report`）
- `--cron "* * * * * *"`：使用 [cron 表达式](https://en.wikipedia.org/wiki/Cron#Cron_expression)指定任务应在何时运行
- `--recipe-source <PATH>`：Recipe YAML 文件的路径
- `-l, --limit <NUMBER>`：使用 `sessions` 命令时显示的最大会话数

**用法：**
```bash
goose schedule <COMMAND>

# Add a new scheduled recipe which runs every day at 9 AM
goose schedule add --schedule-id daily-report --cron "0 0 9 * * *" --recipe-source ./recipes/daily-report.yaml

# List all scheduled jobs
goose schedule list

# List the 10 most recent goose sessions created by a scheduled job
goose schedule sessions --schedule-id daily-report -l 10

# Run a recipe immediately
goose schedule run-now --schedule-id daily-report

# Remove a scheduled job
goose schedule remove --schedule-id daily-report
```

---

##### mcp

运行由 `<name>` 指定的已启用 MCP 服务器（例如 `'Google Drive'`）。

**用法：**
```bash
goose mcp <name>
```

---

##### acp

通过 stdio 将 goose 作为 Agent Client Protocol（ACP）Agent 服务器运行。这使 goose 能够与 Zed 等兼容 ACP 的客户端配合工作。

ACP 是一项新兴的协议规范，它标准化了 AI Agent 与客户端应用之间的通信，使客户端更容易集成各种 AI Agent。

**选项：**
- **`--enable-scheduler`**：启用计划 Recipe 执行。默认禁用。

**用法：**
```bash
goose acp
```

:::info
此命令由兼容 ACP 的客户端自动调用，通常不由用户直接运行。客户端管理 `goose acp` 进程的生命周期。详情请参阅[在 ACP 客户端中使用 goose](https://block.github.io/goose/docs/gdk/acp)。
:::

:::warning 无人值守环境
goose 默认使用系统钥匙串。在 macOS 上，读取凭据可能会显示 Keychain 授权提示。如果你的 ACP 客户端在无人可响应的情况下运行 goose，钥匙串访问可能会无限期阻塞。

为该进程禁用钥匙串访问，并通过环境变量提供提供方凭据：

```bash
GOOSE_DISABLE_KEYRING=1 OPENAI_API_KEY='...' goose acp
```
:::

---

##### serve [options]

通过 HTTP 和 WebSocket 将 goose 作为 Agent Client Protocol（ACP）服务器启动。

**选项：**
- **`--host <HOST>`**：要绑定的主机。默认为 `127.0.0.1`
- **`--port <PORT>`**：要监听的端口。默认为 `3284`
- **`--with-builtin <NAME>`**：按名称启用内置扩展。可多次传入或以逗号分隔列表传入。省略时默认为 `developer`。
- **`--dangerously-unauthenticated`**：在无 ACP 认证的情况下运行。仅用于本地受信任的客户端。
- **`--enable-scheduler`**：启用计划 Recipe 执行。默认禁用。

**用法：**
```bash
# Set a secret before starting the server
export GOOSE_SERVER__SECRET_KEY=$(openssl rand -hex 32)

# Start the ACP server on localhost:3284
goose serve

# Bind to a different host and port
goose serve --host 0.0.0.0 --port 3284

# Start with specific built-in extensions
goose serve --with-builtin developer,memory
```

:::warning
除非传入 `--dangerously-unauthenticated`，否则 `goose serve` 需要 `GOOSE_SERVER__SECRET_KEY`。仅在本地受信任的客户端中使用 `--dangerously-unauthenticated`。
:::

---

#### 终端集成

##### term

设置并使用终端集成的会话。终端集成通过 `AGENT_SESSION_ID` 为每个 shell 提供一个持久的 goose 会话，并可创建 `@goose` 和 `@g` 别名。

**命令：**
- **`init <SHELL>`** - 打印用于 `bash`、`zsh`、`fish`、`nu` 或 `powershell` 的 shell 集成脚本
- **`run <PROMPT...>`** - 向终端集成的会话发送提示词
- **`info`** - 打印用于 shell 提示符集成的精简会话信息

**选项：**
- **`-n, --name <NAME>`** - 运行 `init` 时设置终端会话名称
- **`--default`** - 请求 goose 处理受支持 shell 中的未知命令

**用法：**
```bash
# Set up zsh integration
eval "$(goose term init zsh)"

# Set up zsh integration and ask goose about unknown commands
eval "$(goose term init zsh --default)"

# Set up nushell integration
let init = ($nu.cache-dir | path join "goose-term-init.nu")
goose term init nu | save --force $init
source $init

# Send a prompt to the current terminal session
goose term run why did the last command fail

# Print session info for prompt integration
goose term info
```

---

##### @goose / @g

直接从 shell 提示符向 goose 提问，上下文会包含命令历史。当你设置[终端集成](https://block.github.io/goose/docs/guides/terminal-integration.md)时，这些别名由 `goose term init` 创建。

**示例：**
```bash
# Ask questions with command history context
@goose create a python script to process these files
@goose create a PR description summarizing these changes
@g how do I fix these permission denied errors?
```

---

### 交互式会话功能

#### 斜杠命令

进入交互式会话后（通过 `goose session` 或 `goose run --interactive`），你可以使用这些斜杠命令。所有命令都支持 Tab 补全。按 `/ + <Tab>` 循环浏览可用命令。

**可用命令：**
- **`/?` 或 `/help`** - 显示帮助菜单
- **`/builtin <names>`** - 按名称添加内置扩展（逗号分隔）
- **`/clear`** - 清除当前聊天历史
- **`/exit` 或 `/quit`** - 退出会话
- **`/extension <command>`** - 添加 stdio 扩展（格式：ENV1=val1 command args...）
- **`/mode <name>`** - 设置要使用的 goose 模式（'auto'、'approve'、'chat'、'smart_approve'）
- **`/model [name]`** - 显示当前模型，或在保持同一提供方的情况下为此会话切换模型
- **`/model --provider <name> [model]`** - 切换到不同的提供方，可选择指定模型
- **`/prompt <n> [--info] [key=value...]`** - 获取提示词信息或执行提示词
- **`/prompts [--extension <name>]`** - 列出所有可用提示词，可选择按扩展过滤
- **`/compact`** - 压缩并总结当前对话，在保留关键信息的同时减少上下文长度
- **`/r`** - 切换完整工具输出显示（显示完整工具参数而不截断）
- **`/skills [<name>...]`** - 列出可用 Skill，或按名称加载一个或多个 Skill
- **`/t`** - 在 `light`、`dark` 和 `ansi` 主题之间切换。[更多信息](#themes)。
- **`/t <name>`** - 直接设置主题（light、dark、ansi）

**示例：**
```bash
# List all prompts from the developer extension
/prompts --extension developer

# Switch to chat mode
/mode chat

# Add a builtin extension during the session
/builtin developer

# Clear the current conversation history
/clear
```

你也可以在 goose 桌面版或 CLI 中创建[用于运行 Recipe 的自定义斜杠命令](https://block.github.io/goose/docs/guides/context-engineering/slash-commands)。

---

#### 主题

`/t` 命令控制 goose CLI 响应中 markdown 内容的语法高亮主题。它会影响响应输出中用于标题、代码块、粗体/斜体文本及其他 markdown 元素的样式。

**命令：**
- `/t` - 循环切换主题：`light` → `dark` → `ansi` → `light`
- `/t light` - 设置 `light` 主题（柔和的浅色）
- `/t dark` - 设置 `dark` 主题（柔和的深色）
- `/t ansi` - 设置 `ansi` 主题（视觉上最鲜明、颜色更亮的选项）

**配置：**
- 默认主题为 `dark`
- 主题设置以 `GOOSE_CLI_THEME` 保存到[配置文件](https://block.github.io/goose/docs/guides/config-files)，并在会话之间持久保留
- 保存的配置可通过 `GOOSE_CLI_THEME` [环境变量](https://block.github.io/goose/docs/guides/environment-variables#session-management)为此会话覆盖

**自定义语法高亮：**

你可以通过设置以下内容来自定义用于代码块的底层语法高亮主题：
- `GOOSE_CLI_LIGHT_THEME` - 浅色模式下使用的主题（默认："GitHub"）
- `GOOSE_CLI_DARK_THEME` - 深色模式下使用的主题（默认："zenburn"）

这些接受任何 [bat 主题名称](https://github.com/sharkdp/bat#adding-new-themes)。常用选项包括 "Dracula"、"Nord"、"Solarized (light)"、"Solarized (dark)"、"OneHalfDark" 和 "Monokai Extended"。运行 `bat --list-themes` 查看所有可用主题。

:::info
语法高亮样式仅影响字体，不影响整体终端界面。`light` 和 `dark` 主题在字体颜色和字重上有细微差别。

goose CLI 主题独立于 goose 桌面版主题。
:::

**示例：**
```bash
# Set ANSI theme for the session via environment variable
export GOOSE_CLI_THEME=ansi
goose session --name use-custom-theme

# Toggle theme during a session
/t

# Set the light theme during a session
/t light
```

---

### 导航与控制

#### 键盘快捷键

**会话控制：**
- **`Ctrl+C`** - 如果已输入文本则清除当前行，如果正在处理则中断当前请求，如果行为空则退出会话
- **`Ctrl+J`** - 添加换行。可通过[配置文件](https://block.github.io/goose/docs/guides/config-files)中的 `GOOSE_CLI_NEWLINE_KEY`（例如 `GOOSE_CLI_NEWLINE_KEY: n`）或作为[环境变量](https://block.github.io/goose/docs/guides/environment-variables#session-management)自定义该字符。避免使用 "c" 以及像 "r"、"w"、"z" 这样的常见终端快捷键。

**导航：**
- **`Cmd+Up/Down arrows`** - 浏览命令历史
- **`Ctrl+R`** - 交互式命令历史搜索（反向搜索）。[更多信息](#command-history-search)。

---

#### 外部编辑器模式

为了编写更长的提示词或处理复杂的代码片段，你可以配置 goose 使用你偏好的文本编辑器，而不是 CLI 输入。这会在整个会话中取代标准 CLI 输入和键盘快捷键。

**工作原理：**
1. goose 使用模板文件打开你配置的编辑器
2. 在 `# Your prompt:` 标题之后输入你的提示词（下方显示对话历史作为上下文）
3. 保存文件并关闭/退出编辑器，将你的提示词发送给 goose
4. goose 处理你的提示词，并将响应添加到对话历史后重新打开编辑器
5. 对对话中的每条消息重复步骤 2-4

你可以使用任何接受文件路径参数的编辑器，例如 vim、nano、emacs 和 VS Code。

**配置：**

<Tabs>
  <TabItem value="envvar" label="环境变量" default>

  仅适用于当前会话。

```bash
# For terminal editors like vim or nano
export GOOSE_PROMPT_EDITOR=vim

# Or for GUI editors like VS Code (use --wait flag)
export GOOSE_PROMPT_EDITOR="code --wait"
```

  </TabItem>
  <TabItem value="config" label="配置文件">

  在所有会话之间持久保留，除非被环境变量覆盖。

  1. 打开 goose [配置文件](https://block.github.io/goose/docs/guides/config-files)。例如，在 macOS 上打开 `~/.config/goose/config.yaml`。
  2. 添加 `GOOSE_PROMPT_EDITOR` 并将其设置为你偏好的编辑器：

```yaml
# For terminal editors like vim or nano
GOOSE_PROMPT_EDITOR: vim

# Or for GUI editors like VS Code (use --wait flag)
GOOSE_PROMPT_EDITOR: code --wait
```

  </TabItem>
</Tabs>

**使用 GUI 编辑器：**

GUI 编辑器需要 `--wait` 或等效标志，以确保 goose 在你完成编辑后再继续。没有此标志时，编辑器会打开，但 goose 会立即继续，就好像你已经完成一样。像 vim 和 nano 这样的终端编辑器不需要此标志。

---

#### 命令历史搜索

`Ctrl+R` 快捷键通过你存储的 CLI [命令历史](https://block.github.io/goose/docs/guides/logs#command-history)提供交互式搜索。此功能让你可以轻松查找并复用最近的命令，而无需重新输入。当你输入搜索词时，goose 会在历史中向后搜索匹配项。

**工作原理：**
1. 在你的 goose CLI 会话中按 `Ctrl+R`
2. 输入搜索词
3. 使用以下方式浏览结果：
   - `Ctrl+R` 向后循环浏览更早的匹配项
   - `Ctrl+S` 向前循环浏览更新的匹配项
4. 按 `Return`（或 `Enter`）运行找到的命令，或按 `Esc` 取消

例如，无需重新输入这条长命令：

```
analyze the performance issues in the sales database queries and suggest optimizations
```

使用 `"sales database"` 或 `"optimization"` 搜索词来找到并重新运行它。

**搜索提示：**
- **使用独特的词效果最好**：选择独特的词或短语以帮助过滤结果
- **支持部分匹配和多个词**：你可以搜索诸如 `"gith"` 和 `"run the unit test"` 这样的短语

---

## 配置文件

> 原文：https://block.github.io/goose/docs/guides/config-files

### 配置概览

goose 使用 YAML [配置文件](#configuration-files)来管理设置和扩展。主配置文件位于：

* macOS/Linux：`~/.config/goose/config.yaml`
* Windows：`%APPDATA%\Block\goose\config\config.yaml`

配置文件允许你设置默认行为、配置语言模型、设置工具权限以及管理扩展。虽然许多设置也可以使用[环境变量](https://block.github.io/goose/docs/guides/environment-variables)设置，但配置文件提供了一种持久的方式来维护你的偏好。

### 配置文件

- **config.yaml** - 提供方、模型、扩展和常规设置
- **permission.yaml** - 通过 `goose configure` 配置的工具权限级别
- **secrets.yaml** - API 密钥和机密（当 goose 使用[基于文件的机密存储](#security-considerations)时）
- **permissions/tool_permissions.json** - 运行时权限决策（自动管理）
- **prompts/** - 自定义[提示词模板](https://block.github.io/goose/docs/guides/context-engineering/prompt-templates)

除了直接编辑配置文件外，许多设置也可以从 goose 桌面版和 goose CLI 管理：

- **goose Desktop**：从 `Settings` 页面和底部工具栏
- **goose CLI**：运行 `goose configure` 命令

### 提供方配置

提供方设置存储在 `active_provider` 和 `providers` 键中：

```yaml
active_provider: anthropic
providers:
  anthropic:
    enabled: true
    model: claude-sonnet-4-5-20250929
    configured: true
```

`GOOSE_PROVIDER` 和 `GOOSE_MODEL` 仍作为环境变量受支持，并会为该进程覆盖配置文件。使用扁平 `GOOSE_PROVIDER` 和 `GOOSE_MODEL` 键的旧配置文件会被读取以保持兼容，并在 goose 更新提供方设置时迁移。

### 全局设置

以下设置可以在 config.yaml 文件的根级别进行配置：

| 设置 | 用途 | 取值 | 默认值 | 是否必填 |
|---------|---------|---------|---------|-----------|
| `GOOSE_TEMPERATURE` | 模型响应的随机性 | 0.0 到 1.0 之间的浮点数 | 依模型而定 | 否 |
| `GOOSE_MAX_TOKENS` | 每次模型响应的最大 token 数（截断更长的响应） | 正整数 | 依模型而定 | 否 |
| `GOOSE_CACHE_TTL` | Anthropic 提示词缓存 TTL；`1h` 以更高的缓存写入速率在空闲间隔期间保持缓存前缀存活。无头运行始终使用 `5m` | "5m", "1h" | "5m" | 否 |
| `GOOSE_MODE` | [工具执行行为](https://block.github.io/goose/docs/guides/managing-tools/goose-permissions) | "auto", "approve", "chat", "smart_approve" | "auto" | 否 |
| `GOOSE_MAX_TURNS` | 无用户输入时允许的[最大轮数](https://block.github.io/goose/docs/guides/sessions/smart-context-management#maximum-turns) | 整数（例如 10、50、100） | 1000 | 否 |
| `GOOSE_TOOLSHIM` | 启用工具解释 | true/false | false | 否 |
| `GOOSE_TOOLSHIM_OLLAMA_MODEL` | 用于工具解释的模型 | 模型名称（例如 "llama3.2"） | 系统默认 | 否 |
| `GOOSE_INPUT_LIMIT` | 覆盖 Ollama 的输入 token 限制（映射到 `num_ctx`） | 正整数 | 模型默认 | 否 |
| `GOOSE_CLI_MIN_PRIORITY` | 工具输出详细程度 | 0.0 到 1.0 之间的浮点数 | 0.0 | 否 |
| `GOOSE_CLI_THEME` | CLI 响应 markdown 的[主题](https://block.github.io/goose/docs/guides/goose-cli-commands#themes) | "light", "dark", "ansi" | "ansi" | 否 |
| `GOOSE_CLI_LIGHT_THEME` | 浅色模式的自定义语法高亮主题 | [bat 主题名称](https://github.com/sharkdp/bat#adding-new-themes) | "GitHub" | 否 |
| `GOOSE_CLI_DARK_THEME` | 深色模式的自定义语法高亮主题 | [bat 主题名称](https://github.com/sharkdp/bat#adding-new-themes) | "zenburn" | 否 |
| `GOOSE_CLI_SHOW_COST` | 在 CLI 中显示 token 使用的估算成本 | true/false | false | 否 |
| `GOOSE_CLI_BELL` | 当交互轮次结束或需要工具审批时响终端铃 | true/false | false | 否 |
| `GOOSE_ALLOWLIST` | 允许的扩展的 URL | 有效 URL | 无 | 否 |
| `GOOSE_DOCS_ROOT` | `goose-doc-guide` 使用的文档根目录（例如用于离线/气隙环境的文档） | 包含 `goose-docs-map.md` 和 `docs/` 的本地路径或 HTTP(S) URL | `https://goose-docs.ai` | 否 |
| `GOOSE_RECIPE_GITHUB_REPO` | 用于 Recipe 的 GitHub 仓库 | 格式："org/repo" | 无 | 否 |
| `GOOSE_AUTO_COMPACT_THRESHOLD` | 设置 goose [自动压缩你的会话](https://block.github.io/goose/docs/guides/sessions/smart-context-management#automatic-compaction)的百分比阈值。 | 0.0 到 1.0 之间的浮点数（为 0.0 时禁用）| 0.8 | 否 |
| `GOOSE_AUTO_COMPACT_TOKEN_LIMIT` | 绝对自动压缩触发条件；在启用自动压缩时，此项与百分比阈值中较早触发者生效。它控制压缩何时开始，而非保证的最大请求大小。 | 正整数 | 225000 | 否 |
| `SECURITY_PROMPT_ENABLED` | 启用[提示词注入检测](https://block.github.io/goose/docs/guides/security/prompt-injection-detection)以识别潜在有害的命令 | true/false | false | 否 |
| `SECURITY_PROMPT_THRESHOLD` | 提示词注入检测的敏感度阈值（越高越严格） | 0.01 到 1.0 之间的浮点数 | 0.8 | 否 |
| `SECURITY_PROMPT_CLASSIFIER_ENABLED` | 启用基于机器学习的提示词注入检测，以实现高级威胁识别 | true/false | false | 否 |
| `SECURITY_PROMPT_CLASSIFIER_ENDPOINT` | 用于基于机器学习的提示词注入检测的分类端点 URL | URL（例如 "https://api.example.com/classify"） | 无 | 否 |
| `SECURITY_PROMPT_CLASSIFIER_TOKEN` | 用于 `SECURITY_PROMPT_CLASSIFIER_ENDPOINT` 的认证令牌 | 字符串 | 无 | 否 |
| `GOOSE_TELEMETRY_ENABLED` | 启用[匿名使用数据](https://block.github.io/goose/docs/guides/usage-data)收集 | true/false | false | 否 |

配置文件 config.yaml 中还可能支持额外的[环境变量](https://block.github.io/goose/docs/guides/environment-variables)。

### 示例配置

以下是一个 config.yaml 文件的基本示例：

```yaml
# Model Configuration
active_provider: anthropic
providers:
  anthropic:
    enabled: true
    model: claude-sonnet-4-5-20250929
    configured: true
GOOSE_TEMPERATURE: 0.7

# Tool Configuration
GOOSE_MODE: "smart_approve"
GOOSE_TOOLSHIM: true
GOOSE_CLI_MIN_PRIORITY: 0.2

# Recipe Configuration
GOOSE_RECIPE_GITHUB_REPO: "aaif-goose/goose-recipes"

# Documentation Configuration
GOOSE_DOCS_ROOT: "/path/to/goose-docs"

# Search Path Configuration
GOOSE_SEARCH_PATHS:
  - "/usr/local/bin"
  - "~/custom/tools"
  - "/opt/homebrew/bin"

# Security Configuration
SECURITY_PROMPT_ENABLED: true

# Extensions Configuration
extensions:
  developer:
    bundled: true
    enabled: true
    name: developer
    timeout: 300
    type: builtin
  
  memory:
    bundled: true
    enabled: true
    name: memory
    timeout: 300
    type: builtin
```

### 扩展配置

扩展在 `extensions` 键下配置。每个扩展可以有以下设置：

```yaml
extensions:
  extension_name:
    bundled: true/false       # Whether it's included with goose
    display_name: "Name"      # Human-readable name (optional)
    enabled: true/false       # Whether the extension is active
    name: "extension_name"    # Internal name
    timeout: 300              # Operation timeout in seconds
    type: "builtin"           # Extension type
    available_tools: []       # Filter to specific tools (empty = all)
```

支持的扩展类型有 `builtin`、`platform`、`stdio` 和 `streamable_http`。不支持 SSE；请将旧的 SSE 配置迁移到 `streamable_http`。

常见的扩展形态：

```yaml
extensions:
  developer:
    type: builtin
    name: developer
    enabled: true
    bundled: true
    timeout: 300

  computercontroller:
    type: platform
    name: computercontroller
    display_name: Computer Controller
    enabled: true
    bundled: true

  filesystem:
    type: stdio
    name: filesystem
    enabled: true
    cmd: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    env_keys: []
    envs: {}
    timeout: 300

  remote-tools:
    type: streamable_http
    name: remote-tools
    enabled: true
    uri: "https://example.com/mcp"
    headers: {}
    env_keys: []
    envs: {}
    timeout: 300
```

#### 工具过滤

使用 `available_tools` 字段限制从扩展加载哪些工具。列出你想要的工具名称 —— 只有这些工具对 goose 可用。将其留空（默认值）则加载所有工具。在你只需要扩展能力子集的会话中，这有助于减少 token 开销。

### 搜索路径配置

扩展可能需要执行外部命令或工具。Goose 从任何 `GOOSE_SEARCH_PATHS` 条目、内置回退路径，然后是你的系统 PATH 构建命令搜索路径。你可以在配置文件中添加额外的搜索目录：

```yaml
GOOSE_SEARCH_PATHS:
  - "/usr/local/bin"
  - "~/custom/tools"
  - "/opt/homebrew/bin"
```

在运行扩展命令时，这些路径会在内置回退路径和系统 PATH 之前被检查，确保无需修改你的全局 PATH 即可找到你的自定义工具。

### 可观测性配置

配置 goose 将遥测导出到 [OpenTelemetry](https://opentelemetry.io/docs/) 兼容的平台。环境变量会覆盖这些设置，并支持诸如按信号配置之类的附加选项。详情请参阅[环境变量指南](https://block.github.io/goose/docs/guides/environment-variables#observability-configuration)。

| 设置 | 用途 | 取值 | 默认值 |
|---------|---------|--------|---------|
| `otel_exporter_otlp_endpoint` | OTLP 端点 URL | URL（例如 `http://localhost:4318`） | 无 |
| `otel_exporter_otlp_timeout` | 导出超时（毫秒） | 整数（毫秒） | 10000 |

```yaml
otel_exporter_otlp_endpoint: "http://localhost:4318"
otel_exporter_otlp_timeout: 20000
```

### Recipe 命令配置

你可以选择设置[自定义斜杠命令](https://block.github.io/goose/docs/guides/context-engineering/slash-commands)来运行你创建的 Recipe。列出命令（不含前导 `/`）以及 Recipe 的路径：

```yaml
slash_commands:
  - command: "run-tests"
    recipe_path: "/path/to/recipe.yaml"
  - command: "daily-standup"
    recipe_path: "/Users/me/.local/share/goose/recipes/standup.yaml"
```

### 配置优先级

设置按以下优先级顺序应用：

1. 环境变量（最高优先级）
2. 配置文件设置
3. 默认值（最低优先级）

### 安全注意事项

:::warning 提供方 API 密钥不要放在 `config.yaml` 中
goose 不会从 `config.yaml` 读取提供方 API 密钥。放在那里的密钥会被忽略，通常会表现为认证失败，例如 `No api key passed in`。请将密钥存储在系统钥匙串中（通过 `goose configure`），或者——在使用基于文件的机密存储时——存储在 `secrets.yaml` 中。它也可以通过提供方的环境变量（例如 `OPENAI_API_KEY`）提供，其优先级高于已存储的机密。
:::

- 避免在配置文件中存储敏感信息（API 密钥、令牌）
- 使用系统钥匙串（macOS 上为 keychain）存储机密。在可用时，这是推荐选项。
- 如果 goose 使用基于文件的机密存储，机密存储在单独的 `secrets.yaml` 文件中（以纯文本形式）。这可能发生在以下情况：

  - 你的环境不提供桌面钥匙串服务（例如：无头服务器、CI/CD、容器）
  - 你显式禁用了钥匙串（通过 [GOOSE_DISABLE_KEYRING](https://block.github.io/goose/docs/guides/environment-variables#security-and-privacy)）
  - goose 无法访问钥匙串并回退到基于文件的机密存储

  有关排查钥匙串失败和自动回退行为的更多信息，请参阅[已知问题](https://block.github.io/goose/docs/troubleshooting/known-issues#keyring-cannot-be-accessed-automatic-fallback)。

### 更新配置

直接编辑配置文件通常需要重启 goose 才能对现有会话生效。通过 Settings 进行的 Goose2 提供方凭据/配置保存使用 ACP/core 来更新存储并刷新提供方清单，而无需重启应用，但当前活跃的聊天会话会继续使用它们启动时所用的提供方实例。你可以使用以下方式验证当前配置：

```bash
goose info -v
```

这将显示所有生效的设置及其当前值。

### 另请参阅

- **[多模型配置](https://block.github.io/goose/docs/guides/multi-model/)** - 关于多种模型选择策略
- **[环境变量](https://block.github.io/goose/docs/guides/environment-variables)** - 关于环境变量配置
- **[使用扩展](https://block.github.io/goose/docs/getting-started/using-extensions.md)** - 关于扩展配置的更多详情
