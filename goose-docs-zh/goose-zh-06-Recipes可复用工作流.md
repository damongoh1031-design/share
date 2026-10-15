# goose 官方文档中文手册：第 06 章　Recipes 可复用工作流

## Recipes 可复用工作流

> 原文：https://block.github.io/goose/docs/guides/recipes/index

<h1 className={styles.pageTitle}>Recipes 可复用工作流</h1>
<p className={styles.pageDescription}>
  Recipe 是可复用的工作流，它们将扩展、提示词和设置打包在一起。你可以与团队分享经过验证的工作流，并持续复现成功的结果。
</p>

<div className="video-container margin-bottom--lg">
  <iframe
    width="100%"
    height="400"
    src="https://www.youtube.com/embed/8rTliYrQ6Iw"
    title="使用 Recipes 创建可复用的 AI Agent"
    frameBorder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowFullScreen
  ></iframe>
</div>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>📚 文档与指南</h2>
  <div className={styles.cardGrid}>
    <Card
      title="可复用 Recipe"
      description="将 goose 会话设置（包括工具、目标和说明）作为可复用的 Recipe 分享，让其他人只需单击一次即可启动。"
      link="https://block.github.io/goose/docs/guides/recipes/session-recipes"
    />
    <Card
      title="Recipe 参考指南"
      description="通过 CLI 在 goose 中创建和自定义 Recipe 的完整技术参考。"
      link="https://block.github.io/goose/docs/guides/recipes/recipe-reference"
    />
    <Card
      title="自定义斜杠命令"
      description="创建自定义快捷方式，以便在任意聊天会话中通过简单的斜杠命令快速运行 Recipe。"
      link="https://block.github.io/goose/docs/guides/context-engineering/slash-commands"
    />
    <Card
      title="goose Recipes 教程"
      description="学习如何使用提示词、参数、MCP 服务器等创建和使用 goose Recipe。"
      link="https://block.github.io/goose/docs/tutorials/recipes-tutorial"
    />
    <Card
      title="子 Recipe"
      description="了解 Recipe 如何使用子 Recipe 执行特定任务。"
      link="https://block.github.io/goose/docs/guides/recipes/subrecipes"
    />
    <Card
      title="保存 Recipe"
      description="了解如何保存、整理和查找 goose Recipe，以便轻松访问和重复使用。"
      link="https://block.github.io/goose/docs/guides/recipes/storing-recipes"
    />
    <Card
      title="并行运行子 Recipe 教程"
      description="学习如何同时运行多个子 Recipe 实例。"
      link="https://block.github.io/goose/docs/tutorials/subrecipes-in-parallel"
    />
  </div>
</div>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>🛠️ Recipe 示例集</h2>
  <div className={styles.cardGrid}>
    <Card
      title="Recipe 示例集"
      description="浏览我们收集的开箱即用 Recipe。查找并改编适用于常见开发场景的 Recipe。"
      link="https://block.github.io/goose/recipes"
    />
  </div>
</div>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>📝 精选博客文章</h2>
  <div className={styles.cardGrid}>
    <Card
      title="以锦标赛为驱动的开发"
      description="通过 Recipes 加速开发团队的工作流。"
      link="https://block.github.io/goose/blog/2025/05/09/developers-ai-playbook-for-team-efficiency"
    />
    <Card
      title="成功的秘诀"
      description="借助 Recipes 扩展智能体工作流的价值。"
      link="https://block.github.io/goose/blog/2025/05/06/recipe-for-success"
    />
  </div>
</div>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>🎥 更多视频</h2>

<VideoCarousel
  id="more-videos"
  videos={[
    {
      type: 'iframe',
      src: 'https://youtube.com/embed/1szmJSKInnU',
      title: 'goose 中 Recipes/子 Recipes 的高级技巧',
      description: '在 goose 中使用 Recipes 和子 Recipes 的高级技巧',
      duration: '10:07'
    },
    {
      type: 'iframe',
      src: 'https://youtube.com/embed/gvg7DomaJuA',
      title: '无头 goose：安排并行子代理 Recipe',
      description: '安排一个同时运行两个子代理的 Recipe',
      duration: '5:50'
    }
  ]}
/>
</div>

---

## Recipe 参考指南

> 原文：https://block.github.io/goose/docs/guides/recipes/recipe-reference

Recipe 是可复用的 goose 配置，其中打包了说明和设置，便于轻松分享设置并由其他人启动。

### Recipe 文件格式

Recipe 可以定义在以下文件中：
- `.yaml`（推荐）和 `.yml` 文件
- `.json` 文件

:::info
goose CLI 不支持`.yml`文件。
:::

请参阅[可复用 Recipe](https://block.github.io/goose/docs/guides/recipes/session-recipes)，了解如何创建、使用和管理 Recipe。

### Recipe 位置

Recipe 可以从以下位置加载：

1. 本地文件系统：
   - 当前目录
   - [`GOOSE_RECIPE_PATH`](https://block.github.io/goose/docs/guides/environment-variables#recipe-configuration)环境变量指定的目录

2. GitHub 仓库：
   - 使用[`GOOSE_RECIPE_GITHUB_REPO`](https://block.github.io/goose/docs/guides/environment-variables#recipe-configuration)配置键进行配置
   - 需要安装并完成身份验证的 GitHub CLI（`gh`）

### Recipe 核心架构

Recipe 遵循以下架构结构：

| 字段 | 类型 | 必需 | 描述 |
|-------|------|----------|-------------|
| `description` | String | ✅ | 对 Recipe 功能的详细描述 |
| `instructions` | String | ✅* | 可包含参数替换的模板说明 |
| `prompt` | String | ✅* | 可包含参数替换的模板提示词。在[无头](https://block.github.io/goose/docs/tutorials/headless-goose)（非交互）模式下为必需项。 |
| `title` | String | ✅ | 描述 Recipe 的简短标题 |
| [`activities`](#activities) | Array | - | 示例提示词列表，可包含参数替换。活动会在 goose Desktop 中以可点击气泡的形式显示。 |
| [`extensions`](#extensions) | Array | - | 扩展配置列表 |
| [`parameters`](#parameters) | Array | - | 动态 Recipe 的参数定义列表 |
| [`response`](#response) | Object | - | 自动化工作流的结构化输出架构 |
| [`retry`](#retry) | Object | - | 自动重试逻辑配置，并可验证是否成功 |
| [`settings`](#settings) | Object | - | 模型提供方、模型名称和其他设置的配置 |
| [`sub_recipes`](#subrecipes) | Array | - | 子 Recipe 列表 |
| `version` | String | - | Recipe 格式版本；省略时默认为"1.0.0" |

*必须至少提供`instructions`或`prompt`其中之一。

### 字段规范

#### Activities

`activities`字段定义可选消息和可点击的活动气泡（按钮），当 Recipe 在 goose Desktop 中打开时显示。

:::info 仅桌面版
Activities 是仅限 Desktop 的功能。通过 CLI 或作为计划任务运行包含 activities 的 Recipe 时，`activities`字段会被忽略，不会影响 Recipe 执行。
:::

##### 活动类型

Activities 可以通过两种方式定义：

1. **消息活动**：在活动气泡上方的信息框中显示 Markdown 格式的活动文本。例如：

```
activities:
  - "message: **Welcome!** Here's what I can help with:\n\n• 📊 Data analysis\n• 🔍 Code review\n• 📝 Documentation\n\nSelect an option below to begin."
```

只添加一个带`message:`前缀的活动。其他带`message:`前缀的活动会成为普通的可点击气泡（并显示字面文本`message:`）。

2. **按钮活动**：显示在活动气泡中的文本，单击后会将活动文本作为提示词发送。

##### 参数替换

Activities 支持[参数替换](#parameters)，因此你可以创建动态的个性化活动气泡。用户在**Recipe Parameters**对话框中提供参数值后，这些值会替换进活动文本，然后再显示气泡。

##### 配置示例

<Tabs groupId="format">
<TabItem value="yaml" label="YAML" default>
```yaml
version: "1.0.0"
title: "Code Review Assistant"
description: "Review code with customizable focus areas"
parameters:
  - key: language
    input_type: string
    requirement: required
    description: "Programming language to review"
  - key: focus
    input_type: string
    requirement: optional
    default: "best practices"
    description: "Review focus area"

activities:
  - "message: Click an option below to start reviewing {{ language }} code with a focus on {{ focus }}."
  - "Review the current file for {{ focus }}"
  - "Suggest improvements for {{ language }} code quality"
  - "Check for security vulnerabilities"
  - "Generate unit tests"
```
</TabItem>
<TabItem value="json" label="JSON">
```json
{
  "version": "1.0.0",
  "title": "Code Review Assistant",
  "description": "Review code with customizable focus areas",
  "parameters": [
    {
      "key": "language",
      "input_type": "string",
      "requirement": "required",
      "description": "Programming language to review"
    },
    {
      "key": "focus",
      "input_type": "string",
      "requirement": "optional",
      "default": "best practices",
      "description": "Review focus area"
    }
  ],
  "activities": [
    "message: Click an option below to start reviewing {{ language }} code with a focus on {{ focus }}.",
    "Review the current file for {{ focus }}",
    "Suggest improvements for {{ language }} code quality",
    "Check for security vulnerabilities",
    "Generate unit tests"
  ]
}
```
</TabItem>
</Tabs>

在此示例中：
- 消息活动会显示替换了参数值的说明，例如："Click an option below to start reviewing rust code with a focus on best practices."
- 前两个活动气泡使用参数替换，例如："Review the current file for best practices"
- 最后两个活动气泡是静态提示词，无论参数是什么都可以使用

#### Extensions

`extensions`字段允许你指定 Recipe 正常运行所需的模型上下文协议（MCP）服务器和其他扩展。`extensions`数组中的每个扩展都遵循以下架构：

##### Extension 架构

| 字段 | 类型 | 描述 |
|-------|------|-------------|
| `type` | String | 扩展类型（例如"stdio"） |
| `name` | String | 扩展的唯一名称 |
| `cmd` | String | 运行扩展的命令 |
| `args` | Array | 命令参数列表 |
| `env_keys` | Array | （可选）扩展所需的环境变量名称 |
| `timeout` | Number | 超时时间（秒） |
| `bundled` | Boolean | （可选）扩展是否与 goose 捆绑提供 |
| `description` | String | 扩展功能的描述 |
| `available_tools` | Array | 扩展中可用的工具名称列表。未指定时，所有工具均可用。 |

##### Extension 类型

- **`stdio`**：带有命令和参数的标准 I/O 客户端
- **`builtin`**：goose 捆绑 MCP 服务器的一部分内置扩展
- **`platform`**：在 Agent 进程中运行的平台扩展
- **`streamable_http`**：使用 URI 端点的可流式 HTTP 客户端

:::note Summon Extension 与子代理
`delegate`和`load`工具由`summon`平台扩展提供。当 Recipe 指定显式的`extensions`区块时，只有列出的扩展可用；像`summon`这样的默认平台扩展不会自动包含在内。如果 Recipe 需要子代理委派，请将`summon`添加到扩展列表中：

```yaml
extensions:
  - type: platform
    name: summon
```

定义了[`sub_recipes`](https://block.github.io/goose/docs/guides/recipes/subrecipes)的 Recipe 会自动注入`summon`，无需显式列出。
:::

##### Extension 配置示例

<Tabs groupId="format">
<TabItem value="yaml" label="YAML" default>

```yaml
extensions:
  - type: stdio
    name: codesearch
    cmd: uvx
    args:
      - mcp_codesearch@latest
    timeout: 300
    bundled: true
    description: "Query https://codesearch.sqprod.co/ directly from goose"

  - type: stdio
    name: presidio
    timeout: 300
    cmd: uvx
    args:
      - 'mcp_presidio@latest'
    available_tools:
      - query_logs

  - type: stdio
    name: github-mcp
    cmd: github-mcp-server
    args: []
    env_keys:
      - GITHUB_PERSONAL_ACCESS_TOKEN
    timeout: 60
    description: "GitHub MCP extension for repository operations"

```

</TabItem>
<TabItem value="json" label="JSON">

```json
{
  "extensions": [
    {
      "type": "stdio",
      "name": "codesearch",
      "cmd": "uvx",
      "args": ["mcp_codesearch@latest"],
      "timeout": 300,
      "bundled": true,
      "description": "Query https://codesearch.sqprod.co/ directly from goose"
    },
    {
      "type": "stdio",
      "name": "presidio",
      "timeout": 300,
      "cmd": "uvx",
      "args": ["mcp_presidio@latest"],
      "available_tools": ["query_logs"]
    },
    {
      "type": "stdio",
      "name": "github-mcp",
      "cmd": "github-mcp-server",
      "args": [],
      "env_keys": ["GITHUB_PERSONAL_ACCESS_TOKEN"],
      "timeout": 60,
      "description": "GitHub MCP extension for repository operations"
    }
  ]
}
```

</TabItem>
</Tabs>

##### Extension 环境变量

Extensions 可以通过`env_keys`声明所需环境变量的名称。goose 在扩展启动时解析这些值，优先使用环境变量，然后使用 goose 密钥存储（系统密钥环；禁用密钥环时使用`secrets.yaml`）。

加载 Recipe 时不会提示你补充缺失值。启动 Recipe 前请先配置这些值；如果必需值不可用，扩展会报告初始化错误。

:::info
`env_keys`可以包含 API 密钥等机密，也可以包含 API 端点等非机密配置。
:::

#### Parameters

`parameters`字段允许你创建动态、可复用的 Recipe，以便针对不同上下文进行自定义。参数定义了占位符，用户在运行 Recipe 时填写这些值，从而让 Recipe 更灵活、更具适应性。

参数替换使用 Jinja 风格的模板语法和`{{ parameter_name }}`占位符。`parameters`数组中的每个参数都遵循以下架构：

##### Parameter 架构

| 字段 | 类型 | 必需 | 描述 |
|-------|------|----------|-------------|
| `key` | String | ✅ | 参数的唯一标识符 |
| `input_type` | String | ✅ | 输入类型：`"string"`（默认）、`"number"`、`"boolean"`、`"date"`、`"file"`或`"select"` |
| `requirement` | String | ✅ | 以下其中一项："required"、"optional"或"user_prompt" |
| `description` | String | ✅ | 参数的易读描述 |
| `default` | String | - | 可选参数的默认值 |
| `options` | Array | - | 可用选项列表（`select`输入类型必需） |

##### Parameter 要求

- `required`：使用 Recipe 时必须提供该参数
- `optional`：如果指定了默认值，则可以省略
- `user_prompt`：如果未提供输入，将以交互方式提示用户输入

`required`和`optional`参数最适合用于在 goose Desktop 中打开的 Recipe。如果没有为`user_prompt`参数提供值，则不会替换该参数，它可能会以字面量`{{ parameter_name }}`文本出现在 Recipe 输出中。

##### 输入类型

- `string`：默认类型。参数值在模板替换时按原样使用
- `number`：数值。Desktop UI 会提供数字输入验证
- `boolean`：True/false 值。Desktop UI 会显示包含"True"/"False"选项的下拉列表
- `date`：日期值。目前会渲染为文本输入框
- `file`：参数值应为文件路径。goose 会读取文件内容，并将实际内容（而非路径）替换到模板中
- `select`：从预定义选项中下拉选择。需要`options`字段

**示例：**

```yaml
parameters:
  - key: max_files
    input_type: number
    requirement: optional
    default: "10"
    description: "Maximum files to process"

  - key: output_format
    input_type: select
    requirement: required
    description: "Choose output format"
    options:
      - json
      - markdown
      - csv

  - key: enable_debug
    input_type: boolean
    requirement: optional
    default: "false"
    description: "Enable debug mode"

  - key: source_code
    input_type: file
    requirement: required
    description: "Path to the source code file to analyze"

prompt: "Process {{ max_files }} files in {{ output_format }} format. Debug: {{ enable_debug }}. Code:\n\n{{ source_code }}"
```

:::important
- 可选参数必须指定默认值
- 必需参数不能设置默认值
- 无论`file`参数属于哪种必需类型，都不能设置默认值，以防意外导入敏感文件
- `select`参数必须提供包含可用选项的`options`字段
- 参数键必须与`instructions`、`prompt`或`activities`中使用的模板变量匹配
:::

##### Desktop 中的参数替换

在 goose Desktop 中打开包含参数的 Recipe 时，用户会看到**Recipe Parameters**对话框，可以：
- 为必需参数提供值
- 修改或接受可选参数的默认值
- 为`user_prompt`参数输入值

提交参数值后，这些值会在 Recipe 启动前替换`instructions`、`prompt`和`activities`字段中的内容。

#### Response

`response`字段可以强制 Recipe 输出最终的结构化 JSON。指定`json_schema`后，goose 将：

1. **验证输出**：使用基本的 JSON Schema 验证来检查输出 JSON 是否符合你的 JSON Schema
2. **输出最终结构化内容**：确保 Agent 的最终输出是符合你 JSON 结构的响应

此功能专为**非交互式自动化**设计，以确保输出一致且可解析。通过 goose CLI 或 goose Desktop 运行时，Recipe 都可以生成结构化输出。请参阅[自动化工作流的用例与构想](https://block.github.io/goose/docs/guides/recipes/session-recipes#structured-output-for-automation)。

##### Response 架构

| 字段 | 类型 | 必需 | 描述 |
|-------|------|----------|-------------|
| `json_schema` | Object | ✅ | 用于输出验证的[JSON Schema](https://json-schema.org/) |

##### 基本结构

```yaml
response:
  json_schema:
    type: object
    properties:
      # Define your fields here, with their type and description
    required:
      # List required field names
```

##### 简单示例

```yaml
version: "1.0.0"
title: "Task Summary"
description: "Summarize completed tasks"
prompt: "Summarize the tasks you completed"
response:
  json_schema:
    type: object
    properties:
      summary:
        type: string
        description: "Brief summary of work done"
      tasks_completed:
        type: number
        description: "Number of tasks finished"
      next_steps:
        type: array
        items:
          type: string
        description: "Recommended next actions"
    required:
      - summary
      - tasks_completed
```

#### Retry

`retry`字段允许 Recipe 在未达到成功标准时自动重试执行。对于可能需要多次尝试才能实现目标的 Recipe，或用于实现自动验证与恢复工作流时，这项功能非常有用。

##### Retry 架构

| 字段 | 类型 | 必需 | 描述 |
|-------|------|----------|-------------|
| `max_retries` | Number | ✅ | 最大重试次数 |
| `checks` | Array | ✅ | 成功检查配置列表 |
| `timeout_seconds` | Number | - | 成功检查命令的超时时间（默认：300 秒） |
| `on_failure_timeout_seconds` | Number | - | `on_failure`命令的超时时间（默认：600 秒） |
| `on_failure` | String | - | 重试失败时运行的 Shell 命令 |

##### 成功检查配置

`checks`数组中的每个成功检查都遵循以下架构：

| 字段 | 类型 | 必需 | 描述 |
|-------|------|----------|-------------|
| `type` | String | ✅ | 检查类型——目前仅支持"shell" |
| `command` | String | ✅ | 执行验证的 Shell 命令（成功时必须以代码 0 退出） |

##### Retry 逻辑的工作方式

1. **Recipe 执行**：Recipe 使用提供的说明正常运行
2. **成功验证**：执行完成后，按顺序执行所有成功检查
3. **重试判定**：如果任何成功检查失败且仍有重试机会：
   - 执行`on_failure`命令（如果已配置）
   - 将 Agent 的消息历史重置为初始状态
   - 增加重试计数器并重新开始执行
4. **完成**：满足以下任一条件时停止处理：
   - 所有成功检查均通过（成功）
   - 已达到最大重试次数（失败）

##### 基本 Retry 示例

```yaml
version: "1.0.0"
title: "Counter Increment Task"
description: "Increment a counter until it reaches target value"
prompt: "Increment the counter value in /tmp/counter.txt by 1."

retry:
  max_retries: 5
  timeout_seconds: 10
  checks:
    - type: shell
      command: "test $(cat /tmp/counter.txt 2>/dev/null || echo 0) -ge 3"
  on_failure: "echo 'Counter is at:' $(cat /tmp/counter.txt 2>/dev/null || echo 0) '(need 3 to succeed)'"
```

##### 高级 Retry 示例

```yaml
version: "1.0.0"
title: "Service Health Check"
description: "Start service and verify it's running properly"
prompt: "Start the web service and verify it responds to health checks"

retry:
  max_retries: 3
  timeout_seconds: 30
  on_failure_timeout_seconds: 60
  checks:
    - type: shell
      command: "curl -f http://localhost:8080/health"
    - type: shell
      command: "pgrep -f 'web-service' > /dev/null"
  on_failure: "systemctl stop web-service || killall web-service"
```

##### 环境变量

你可以使用环境变量全局配置重试行为：

- `GOOSE_RECIPE_RETRY_TIMEOUT_SECONDS`：成功检查命令的全局超时时间
- `GOOSE_RECIPE_ON_FAILURE_TIMEOUT_SECONDS`：`on_failure`命令的全局超时时间

Recipe 专属的超时配置会覆盖这些环境变量。

#### Settings

`settings`字段允许你为 Recipe 配置 AI 模型和提供方设置。运行 Recipe 时，这些设置会覆盖默认配置。

##### Settings 架构

| 字段 | 类型 | 必需 | 描述 |
|-------|------|----------|-------------|
| `goose_provider` | String | - | 要使用的 AI 提供方（例如"anthropic"、"openai"） |
| `goose_model` | String | - | 要使用的具体模型名称 |
| `temperature` | Number | - | 模型温度设置（通常为 0.0-1.0） |
| `max_turns` | Number | - | 此 Recipe 创建的子代理任务的最大轮数 |

##### 了解 max_turns

`max_turns`设置用于控制 Agent 在停止前可以执行多少轮迭代。在 Recipe 的 settings 中设置时，它会应用于该 Recipe 的执行过程及其创建的任何子代理或子 Recipe（除非它们指定了自己的值）。

**配置优先级（从高到低）：**
1. 子代理工具调用覆盖值
2. Recipe 的`settings.max_turns`
3. `GOOSE_SUBAGENT_MAX_TURNS`环境变量
4. 默认值（主 Recipe 为 1000，子代理为 25）

**常见用例：**限制自动化工作流的执行时间、防止子代理失控、控制计划任务中的资源使用。

对于子代理，`settings`中的`goose_provider`和`goose_model`优先于`GOOSE_SUBAGENT_PROVIDER`和`GOOSE_SUBAGENT_MODEL`环境变量。

##### Settings 配置示例

```yaml
settings:
  goose_provider: "anthropic"
  goose_model: "claude-sonnet-4-20250514"
  temperature: 0.7
  max_turns: 50
```

```yaml
settings:
  goose_provider: "openai"
  goose_model: "gpt-4o"
  temperature: 0.3
```

:::note
Recipe 中指定的 Settings 会在该 Recipe 执行时覆盖 goose 的默认配置。如果未指定任何 Settings，goose 将使用你配置的默认值。
:::

#### Subrecipes

`sub_recipes`字段指定主 Recipe 调用来执行特定任务的[子 Recipe](https://block.github.io/goose/docs/guides/recipes/subrecipes)。`sub_recipes`数组中的每个子 Recipe 都遵循以下架构：

##### Subrecipe 架构

| 字段 | 类型 | 必需 | 描述 |
|-------|------|----------|-------------|
| `name` | String | ✅ | 子 Recipe 的唯一标识符 |
| `path` | String | ✅ | 子 Recipe 文件的相对路径或绝对路径 |
| `values` | Object | - | 传递给子 Recipe 的预配置参数值 |
| `sequential_when_repeated` | Boolean | - | 强制按顺序执行多个子 Recipe 实例。详情请参阅[并行运行子 Recipe](https://block.github.io/goose/docs/tutorials/subrecipes-in-parallel)。 |
| `description` | String | - | 子 Recipe 的可选描述 |

##### 子 Recipe 配置示例

```yaml
sub_recipes:
  - name: "security_scan"
    path: "./subrecipes/security-analysis.yaml"
    values:  # in key-value format: {parameter_name}: {parameter_value}
      scan_level: "comprehensive"
      include_dependencies: "true"

  - name: "quality_check"
    path: "./subrecipes/quality-analysis.yaml"
    description: "Performs code quality analysis"
```

### Desktop 元数据字段

从 goose Desktop 保存的 Recipe 会包含额外的元数据字段。Desktop 应用会使用这些字段进行整理和管理，但 CLI 操作会忽略它们。

| 字段 | 类型 | 必需 | 描述 |
|-------|------|----------|-------------|
| `recipe` | Object | ✅ | 包含所有 Recipe 字段（`title`、`description`、`instructions`等） |
| `name` | String | ✅ | 在 Recipe Library 中显示的名称 |
| `isGlobal` | Boolean | ✅ | Recipe 是全局可用还是仅在本地项目中可用 |
| `lastModified` | String | ✅ | Recipe 上次修改时间的 ISO 时间戳 |
| `isArchived` | Boolean | ✅ | Recipe 是否在 Desktop 界面中归档 |

<details>
<summary>CLI 与 Desktop 格式示例</summary>

**CLI 格式**

<Tabs groupId="format">
<TabItem value="yaml" label="YAML" default>

```yaml
version: "1.0.0"
title: "Code Review Assistant"
description: "Automated code review with best practices"
instructions: "You are a code reviewer..."
prompt: "Review the code in this repository"
extensions: []
```

</TabItem>
<TabItem value="json" label="JSON">

```json
{
  "version": "1.0.0",
  "title": "Code Review Assistant",
  "description": "Automated code review with best practices",
  "instructions": "You are a code reviewer...",
  "prompt": "Review the code in this repository",
  "extensions": []
}
```

</TabItem>
</Tabs>

**Desktop 格式**

<Tabs groupId="format">
<TabItem value="yaml" label="YAML" default>

```yaml
name: "Code Review Assistant"
recipe:
  version: "1.0.0"
  title: "Code Review Assistant"
  description: "Automated code review with best practices"
  instructions: "You are a code reviewer..."
  prompt: "Review the code in this repository"
  extensions: []
isGlobal: true
lastModified: 2025-07-02T03:46:46.778Z
isArchived: false
```

</TabItem>
<TabItem value="json" label="JSON">

```json
{
  "name": "Code Review Assistant",
  "recipe": {
    "version": "1.0.0",
    "title": "Code Review Assistant",
    "description": "Automated code review with best practices",
    "instructions": "You are a code reviewer...",
    "prompt": "Review the code in this repository",
    "extensions": []
  },
  "isGlobal": true,
  "lastModified": "2025-07-02T03:46:46.778Z",
  "isArchived": false
}
```

</TabItem>
</Tabs>

</details>

### 模板支持

Recipe 在`instructions`、`prompt`和`activities`字段中支持 Jinja 风格的模板语法，用于参数替换：

```yaml
instructions: "Follow these steps with {{ parameter_name }}"
prompt: "Your task is to {{ action }}"
activities:
  - "Process {{ parameter_name }} with {{ action }}"
```

高级模板功能包括：
- [转义模板变量](#escaping-template-variables)，以输出字面内容
- 使用`{% extends "parent.yaml" %}`进行[模板继承](#template-inheritance)
- 可定义和覆盖的区块：

```yaml
{% block content %}
Default content
{% endblock %}
```

- [`indent()`模板筛选器](#indent-filter-for-multi-line-values)

#### 转义模板变量

如果要在 Recipe 中包含字面量模板语法（如`{{ variable }}`）而不进行参数替换，请用单引号将其括起来：

```yaml
prompt: |
  This will be substituted: {{ actual_parameter }}
  This will appear literally: {{'{{example_variable}}'}}
```

**示例：**生成配置文件模板

```yaml
version: "1.0.0"
title: "Generate Config Template"
description: "Generate a template with placeholder values"
parameters:
  - key: app_name
    input_type: string
    requirement: required
    description: "Application name"

prompt: |
  Create a config.yaml file for {{ app_name }} with these placeholder variables:
  - {{'{{API_KEY}}'}} for the API key
  - {{'{{DATABASE_URL}}'}} for the database connection
  - {{'{{PORT}}'}} for the server port
```

#### 模板继承

使用`{% extends "parent.yaml" %}`进行模板继承：

**父 Recipe（`parent.yaml`）：**

```yaml
version: "1.0.0"
title: "Parent Recipe"
description: "Base recipe template"
prompt: |
  {% block prompt %}
  Default prompt text
  {% endblock %}
```

**子 Recipe：**

```yaml
{% extends "parent.yaml" %}
{% block prompt %}
Modified prompt text
{% endblock %}
```

#### 用于多行值的 indent() 筛选器

使用`indent()`筛选器，确保多行参数值具有正确缩进并能解析为有效的 JSON 或 YAML 格式。以下示例使用`{{ raw_data | indent(2) }}`，在向子 Recipe 传递数据时指定缩进两个空格：

```yaml
sub_recipes:
  - name: "analyze"
    path: "./analyze.yaml"
    values:
      content: |
        {{ raw_data | indent(2) }}
```

#### 内置参数

内置模板参数会自动受支持，无需在`parameters`数组中定义。

| 参数 | 描述 |
|-----------|-------------|
| `recipe_dir` | 自动设为包含 Recipe 文件的目录。你可以用它引用配套文件，例如：`{{ recipe_dir }}/style-guide.md` |

### 验证规则

加载 Recipe 时会执行[`validate_recipe.rs`](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/recipe/validate_recipe.rs)中的验证规则；[`goose recipe validate`](https://block.github.io/goose/docs/guides/goose-cli-commands#recipe)子命令也会使用这些规则：

#### Recipe 级验证

- `validate_prompt_or_instructions`——必须提供`instructions`或`prompt`其中至少一项
- `validate_json_schema`——如果指定了`response.json_schema`，则 JSON 响应架构必须有效

#### 参数验证

- `validate_parameters_in_template`——所有模板变量必须有对应的参数定义，且所有已定义参数都必须使用（不能存在未使用的参数）
- `validate_optional_parameters`——可选参数必须设置默认值
- `validate_optional_parameters`——文件参数不能设置默认值，以防导入敏感文件

:::info
基本字段要求（必需字段、类型、字符限制）记录在[Recipe 核心架构](#core-recipe-schema)表中。
:::

### 完整 Recipe 示例

<Tabs groupId="format">
<TabItem value="yaml" label="YAML" default>

```yaml
version: "1.0.0"
title: "Example Recipe"
description: "A sample recipe demonstrating the format"
instructions: "Process {{ file_count }} files using {{ required_param }} and output in {{ output_format }} format. Configuration: {{ config_file }}"
prompt: "Start processing with the provided parameters"
parameters:
  - key: required_param
    input_type: string
    requirement: required
    description: "A required text parameter"

  - key: file_count
    input_type: number
    requirement: optional
    default: 10
    description: "Maximum number of files to process"

  - key: output_format
    input_type: select
    requirement: required
    description: "Choose the output format"
    options:
      - json
      - markdown
      - csv

  - key: config_file
    input_type: file
    requirement: required
    description: "Path to configuration file"

extensions:
  - type: stdio
    name: codesearch
    cmd: uvx
    args:
      - mcp_codesearch@latest
    timeout: 300
    bundled: true
    description: "Query codesearch directly from goose"

settings:
  goose_provider: "anthropic"
  goose_model: "claude-sonnet-4-20250514"
  temperature: 0.7
  max_turns: 100

retry:
  max_retries: 3
  timeout_seconds: 30
  checks:
    - type: shell
      command: "echo 'Task validation check passed'"
  on_failure: "echo 'Retry attempt failed, cleaning up...'"

response:
  json_schema:
    type: object
    properties:
      result:
        type: string
        description: "The main result of the task"
      details:
        type: array
        items:
          type: string
        description: "Additional details of steps taken"
    required:
      - result
      - details
```

</TabItem>
<TabItem value="json" label="JSON">

```json
{
  "version": "1.0.0",
  "title": "Example Recipe",
  "description": "A sample recipe demonstrating the format",
  "instructions": "Process {{ file_count }} files using {{ required_param }} and output in {{ output_format }} format. Configuration: {{ config_file }}",
  "prompt": "Start processing with the provided parameters",
  "parameters": [
    {
      "key": "required_param",
      "input_type": "string",
      "requirement": "required",
      "description": "A required text parameter"
    },
    {
      "key": "file_count",
      "input_type": "number",
      "requirement": "optional",
      "default": "10",
      "description": "Maximum number of files to process"
    },
    {
      "key": "output_format",
      "input_type": "select",
      "requirement": "required",
      "description": "Choose the output format",
      "options": ["json", "markdown", "csv"]
    },
    {
      "key": "config_file",
      "input_type": "file",
      "requirement": "required",
      "description": "Path to configuration file"
    }
  ],
  "extensions": [
    {
      "type": "stdio",
      "name": "codesearch",
      "cmd": "uvx",
      "args": ["mcp_codesearch@latest"],
      "timeout": 300,
      "bundled": true,
      "description": "Query codesearch directly from goose"
    }
  ],
  "settings": {
    "goose_provider": "anthropic",
    "goose_model": "claude-sonnet-4-20250514",
    "temperature": 0.7,
    "max_turns": 100
  },
  "retry": {
    "max_retries": 3,
    "timeout_seconds": 30,
    "checks": [
      {
        "type": "shell",
        "command": "echo 'Task validation check passed'"
      }
    ],
    "on_failure": "echo 'Retry attempt failed, cleaning up...'"
  },
  "response": {
    "json_schema": {
      "type": "object",
      "properties": {
        "result": {
          "type": "string",
          "description": "The main result of the task"
        },
        "details": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "Additional details of steps taken"
        }
      },
      "required": ["result", "details"]
    }
  }
}
```

</TabItem>
</Tabs>

### 错误处理

需要留意的常见错误：

- 缺少必需参数
- 可选参数未设置默认值
- 模板变量没有参数定义
- YAML/JSON 语法无效
- 缺少必需字段
- 扩展配置无效
- Retry 配置无效（缺少必需字段、Shell 命令无效）

出现这些情况时，goose 会提供实用的错误消息，指出需要修复的内容。

#### Retry 专属错误

- **成功检查无效**：无法执行或存在语法错误的 Shell 命令
- **超时错误**：成功检查命令或`on_failure`命令超过其超时限制
- **超过最大重试次数**：所有重试均已用尽但仍未成功
- **缺少必需的 Retry 字段**：未指定`max_retries`或`checks`

### 了解更多

查看[Recipes](https://block.github.io/goose/docs/guides/recipes)指南，获取更多文档、工具和资源，帮助你熟练掌握 goose Recipe。

---

## 可复用 Recipe

> 原文：https://block.github.io/goose/docs/guides/recipes/session-recipes

Recipe 会将工具、目标和说明打包为可复用的工作流，其他人（或未来的你）只需单击一次即可启动。

### 创建 Recipe

<Tabs groupId="interface">
<TabItem value="ui" label="goose Desktop" default>

1. 单击左上角的<PanelLeft className="inline" size={16} />按钮，打开侧边栏
2. 单击侧边栏中的`Recipes`
3. 单击`Create Recipe`
4. 在打开的对话框中，根据需要填写 Recipe 字段：
   <RecipeFields />
5. 完成后，你可以：
   - 复制 Recipe 链接，与其他人分享
   - 单击`Save Recipe`，将 Recipe 保存到 Recipe Library
   - 单击`Save & Run Recipe`，保存 Recipe 并立即在新会话中运行

</TabItem>
<TabItem value="cli" label="goose CLI">
在编辑器中按照下方的 Recipe 结构创建 JSON 或 YAML 文件。

<details>
<summary>Recipe 文件结构</summary>

```yaml
# Required fields
version: 1.0.0
title: $title
description: $description
instructions: $instructions    # Define the model's behavior

# Optional fields
prompt: $prompt                # Initial message to start with
extensions:                    # Tools the recipe needs
- $extensions
activities:                    # Example prompts to display in the Desktop app
- $activities
settings:                      # Additional settings
  goose_provider: $provider    # Provider to use for this recipe
  goose_model: $model          # Specific model to use for this recipe
  temperature: $temperature    # Model temperature setting for this recipe (0.0 to 1.0)
retry:                         # Automated retry logic with success validation
  max_retries: $max_retries    # Maximum number of retry attempts
  checks:                      # Success validation checks
  - type: shell
    command: $validation_command
  on_failure: $cleanup_command # Optional cleanup command on failure
```

</details>

有关所有 Recipe 字段的详细说明和配置示例，请参阅[Recipe 参考指南](https://block.github.io/goose/docs/guides/recipes/recipe-reference)。

:::tip 验证 Recipe
你应该[验证 Recipe](#validate-recipe)，以确认 Recipe 完整且格式正确。
:::

#### 可选参数

你可以向 Recipe 添加参数，这样用户运行 Recipe 时就需要填写相应数据。参数可以添加到 Recipe 的任何部分（instructions、prompt、activities 等）。

使用参数的方法：
1. 在 Recipe 内容中使用`{{ variable_name }}`语法添加模板变量
2. 在 YAML 文件的`parameters`区块中定义每个参数

<details>
<summary>带参数的 Recipe 示例</summary>

```yaml
version: 1.0.0
title: "{{ project_name }} Code Review" # Wrap the value in quotes if it starts with template syntax to avoid YAML parsing errors
description: Automated code review for {{ project_name }} with {{ language }} focus
instructions: You are a code reviewer specialized in {{ language }} development.
prompt: |
   Apply the following standards:
   - Complexity threshold: {{ complexity_threshold }}
   - Required test coverage: {{ test_coverage }}%
   - Style guide: {{ style_guide }}
activities:
- "Review {{ language }} code for complexity"
- "Check test coverage against {{ test_coverage }}% requirement"
- "Verify {{ style_guide }} compliance"
settings:
  goose_provider: "anthropic"
  goose_model: "claude-3-7-sonnet-latest"
  temperature: 0.7
parameters:
- key: project_name
  input_type: string
  requirement: required # could be required, optional or user_prompt
  description: name of the project
- key: language
  input_type: string
  requirement: required
  description: language of the code
- key: complexity_threshold
  input_type: number
  requirement: optional
  default: 20 # default is required for optional parameters
  description: a threshold that defines the maximum allowed complexity
- key: test_coverage
  input_type: number
  requirement: optional
  default: 80
  description: the minimum test coverage threshold in percentage
- key: style_guide
  input_type: string
  description: style guide name
  requirement: user_prompt
  # If style_guide param value is not specified in the command, user will be prompted to provide a value, even in non-interactive mode
```

</details>

有关 Recipe 字段的更多信息，请参阅[Recipe 参考指南](https://block.github.io/goose/docs/guides/recipes/recipe-reference)。

</TabItem>
</Tabs>

### 编辑 Recipe
<Tabs groupId="interface">
<TabItem value="ui" label="goose Desktop" default>

1. 单击左上角的<PanelLeft className="inline" size={16} />按钮，打开侧边栏
2. 单击侧边栏中的`Recipes`
3. 找到要编辑的 Recipe，并单击<SquarePen className="inline" size={16} />按钮
4. 在出现的对话框中，编辑以下任意内容：
   <RecipeFields />
5. 完成后，你可以：
   - 复制 Recipe 链接，与其他人分享
   - 单击`Save Recipe`，保存更改
   - 单击`Save & Run Recipe`，保存 Recipe 并立即在新会话中运行

:::tip 编辑正在使用的 Recipe
在会话中使用 Recipe 时也可以打开编辑对话框：只需单击应用底部的<ChefHat className="inline" size={16} />按钮。发送第一条消息后，该按钮就会显示。
:::

</TabItem>

<TabItem value="cli" label="goose CLI">
创建 Recipe 文件后，可以使用你喜欢的文本编辑器打开文件并修改任意字段的值。

</TabItem>
</Tabs>

### 使用 Recipe

<Tabs groupId="interface">
<TabItem value="ui" label="goose Desktop" default>

1. 通过直接链接或手动输入 URL 打开 Recipe，也可以从 Recipe Library 打开：

   **直接链接：**

       1. 单击他人分享给你的 Recipe 链接

   **手动输入 URL：**

       1. 将 Recipe 链接粘贴到浏览器地址栏
       2. 按`Enter`，然后单击`Open Goose.app`提示

   **Recipe Library：**

       1. 单击左上角的<PanelLeft className="inline" size={16} />按钮，打开侧边栏
       2. 单击侧边栏中的`Recipes`
       3. 在 Recipe Library 中找到你的 Recipe
       4. 单击要打开的 Recipe 旁边的`Use`

   **斜杠命令：**

       1. 在任意 goose 聊天会话中输入一个[自定义斜杠命令](https://block.github.io/goose/docs/guides/context-engineering/slash-commands)

2. 首次运行 Recipe 时，会显示警告对话框，其中包含 Recipe 的标题、描述和说明，供你查看。如果你信任 Recipe 内容，请单击`Trust and Execute`继续。除非 Recipe 发生更改，否则不会再次提示同一个 Recipe。

3. 如果 Recipe 包含参数，请在`Recipe Parameters`对话框中输入值，然后单击`Start Recipe`。

   参数是 Recipe 中使用的动态值：

   - **必需参数**以红色星号（*）标记
   - **可选参数**会显示可更改的默认值

4. Recipe 会自动提交，goose 随即开始执行。如果 Recipe 包含[prompt](#core-components)，它会作为第一条消息发送。如果没有，你可以单击活动气泡或发送提示词以开始。

:::info 隐私与隔离
- 每个人都有自己的私密会话
- 用户之间不会共享数据
- 你的会话不会影响原始 Recipe 创建者的会话
:::
</TabItem>

<TabItem value="cli" label="goose CLI">

使用 goose CLI 运行 Recipe 可能涉及以下任务：
- [配置 Recipe 位置](#configure-recipe-location)
- [运行 Recipe](#run-a-recipe)
- [安排 Recipe](#schedule-recipe)

#### 配置 Recipe 位置

Recipe 可以存储在本地设备或 GitHub 仓库中。使用`goose configure`命令或[配置文件](https://block.github.io/goose/docs/guides/config-files#global-settings)配置 Recipe 仓库。

:::tip 仓库结构
- 每个 Recipe 都应放在自己的目录中
- 目录名与命令中使用的 Recipe 名称一致
- Recipe 文件可以是 recipe.yaml 或 recipe.json
:::

<Tabs>
<TabItem value="configure" label="使用 goose configure" default>

运行 configure 命令：

```sh
goose configure
```

你会看到以下提示：

```sh
┌  goose-configure
│
◆  What would you like to configure?
│  ○ Configure Providers
│  ○ Add Extension
│  ○ Toggle Extensions
│  ○ Remove Extension
// highlight-start
│  ● goose settings (Set the goose mode, Tool Output, Tool Permissions, Experiment, goose recipe github repo and more)
// highlight-end
│
◇  What would you like to configure?
│  goose settings
│
◆  What setting would you like to configure?
│  ○ goose mode
│  ○ Tool Permission
│  ○ Tool Output
│  ○ Toggle Experiment
// highlight-start
│  ● goose recipe github repo (goose will pull recipes from this repo if not found locally.)
// highlight-end
└
┌  goose-configure
│
◇  What would you like to configure?
│  goose settings
│
◇  What setting would you like to configure?
│  goose recipe github repo
│
◆  Enter your goose recipe GitHub repo (owner/repo): eg: my_org/goose-recipes
// highlight-start
│  squareup/goose-recipes (default)
// highlight-end
└
```

</TabItem>

<TabItem value="config" label="使用配置文件">

在配置文件中添加：

```yaml title="~/.config/goose/config.yaml"
GOOSE_RECIPE_GITHUB_REPO: "owner/repo"
```

</TabItem>
</Tabs>

#### 运行 Recipe

<Tabs groupId="interface">
<TabItem value="local" label="本地 Recipe" default>

**基本用法**——运行一次后退出（更多信息请参阅[运行选项](https://block.github.io/goose/docs/guides/goose-cli-commands#run-options)和[Recipe 命令](https://block.github.io/goose/docs/guides/goose-cli-commands#recipe)）：

```sh
# Using recipe file in current directory or [`GOOSE_RECIPE_PATH`](https://block.github.io/goose/docs/guides/environment-variables#recipe-configuration) directories
goose run --recipe recipe.yaml

# Using full path
goose run --recipe ./recipes/my-recipe.yaml
```

**预览 Recipe**——使用[`explain`](https://block.github.io/goose/docs/guides/goose-cli-commands#run-options)命令在运行前查看详细信息：

**交互模式**——启动交互式会话：

```sh
goose run --recipe recipe.yaml --interactive
```

交互模式会提示你输入必需值：

```sh
◆ Enter value for required parameter 'language':
│ Python
│
◆ Enter value for required parameter 'style_guide':
│ PEP8
```

**使用参数**——运行 Recipe 时提供参数值。详细示例和选项请参阅[`run`命令文档](https://block.github.io/goose/docs/guides/goose-cli-commands#run-options)。

基本示例：

```sh
goose run --recipe recipe.yaml --params language=Python
```

**斜杠命令**——在任意 goose 聊天会话中输入一个[自定义斜杠命令](https://block.github.io/goose/docs/guides/context-engineering/slash-commands)

</TabItem>

<TabItem value="github" label="GitHub Recipe">

配置好 GitHub 仓库后，你可以按名称运行 Recipe：

**基本用法**——使用与你已配置仓库中目录同名的 Recipe，从仓库运行 Recipe（更多信息请参阅[运行选项](https://block.github.io/goose/docs/guides/goose-cli-commands#run-options)和[Recipe 命令](https://block.github.io/goose/docs/guides/goose-cli-commands#recipe)）：

```sh
goose run --recipe recipe-name
```

例如，如果你的仓库结构如下：

```
my-repo/
├── code-review/
│   └── recipe.yaml
└── setup-project/
    └── recipe.yaml
```

要运行代码审查 Recipe，可以使用以下命令：

```sh
goose run --recipe code-review
```

**预览 Recipe**——使用[`explain`](https://block.github.io/goose/docs/guides/goose-cli-commands#run-options)命令在运行前查看详细信息：

**交互模式**——使用参数提示：

```sh
goose run --recipe code-review --interactive
```

交互模式会提示你输入必需值：

```sh
◆ Enter value for required parameter 'project_name':
│ MyProject
│
◆ Enter value for required parameter 'language':
│ Python
```

**使用参数**——运行 Recipe 时提供参数值。详细示例和选项请参阅[`run`命令文档](https://block.github.io/goose/docs/guides/goose-cli-commands#run-options)。

</TabItem>
</Tabs>
:::info 隐私与隔离
- 每个人都有自己的私密会话
- 用户之间不会共享数据
- 你的会话不会影响原始 Recipe 创建者的会话
:::

</TabItem>
</Tabs>

### 验证 Recipe

<Tabs groupId="interface">
<TabItem value="ui" label="goose Desktop" default>
Recipe 验证只能通过 CLI 执行。
</TabItem>
<TabItem value="cli" label="goose CLI">
验证 Recipe 文件，确保配置正确。验证会检查：
- 是否提供了所有必需字段
- 参数格式是否正确
- 引用的扩展是否存在且有效
- YAML/JSON 语法是否正确

```sh
goose recipe validate recipe.yaml
```

:::info
如果要验证刚创建的 Recipe，需要先[退出会话](https://block.github.io/goose/docs/guides/sessions/session-management#exit-session)，然后再运行[`validate`子命令](https://block.github.io/goose/docs/guides/goose-cli-commands#recipe)。
:::

Recipe 验证可用于：
- 排查无法按预期工作的 Recipe
- 手动编辑后验证 Recipe
- 在 CI/CD 流水线中进行自动化测试

</TabItem>
</Tabs>

### 分享 Recipe
使用 Recipe 链接或 Recipe 文件与 goose 用户分享你的 Recipe。

:::info 隐私与隔离
每位接收者使用你分享的 Recipe 时，都会拥有自己的私密会话。用户之间不会共享数据，你的原始会话和 Recipe 均不受影响。
:::

#### 通过 Recipe 链接分享
你可以通过 Recipe 链接与 Desktop 用户分享 Recipe。

<Tabs groupId="interface">
<TabItem value="ui" label="goose Desktop" default>
从 Recipe Library 复制深层链接并分享给其他人：
1. 单击左上角的<PanelLeft className="inline" size={16} />按钮，打开侧边栏
2. 单击侧边栏中的`Recipes`
3. 找到要分享的 Recipe，单击<Link className="inline" size={16} />按钮复制链接

</TabItem>
<TabItem value="cli" label="goose CLI">
从 Recipe 文件生成深层链接并分享给其他人：

```sh
goose recipe deeplink <FILE>
```

你也可以提供参数值，预先填写`Recipe Parameters`对话框：

```sh
goose recipe deeplink <FILE> --param key1=value1 --param key2=value2
```
</TabItem>
</Tabs>

有人单击此链接时，会在 goose Desktop 中打开你的 Recipe 配置。他们也可以使用 Recipe 链接[导入 Recipe](https://block.github.io/goose/docs/guides/recipes/storing-recipes#importing-recipes)，供日后使用。

#### 通过 Recipe 文件分享
你可以直接发送 Recipe 文件，与 Desktop 或 CLI 用户分享 Recipe。

<Tabs groupId="interface">
<TabItem value="ui" label="goose Desktop">

在 goose Desktop 中，你可以导出 Recipe 文件或复制 Recipe 内容并分享给其他人。

1. 单击左上角的<PanelLeft className="inline" size={16} />按钮，打开侧边栏
2. 单击侧边栏中的`Recipes`
3. 找到要分享的 Recipe，单击<Share2 className="inline" size={16} />按钮
4. 选择分享方式：
   - 要将 Recipe 下载为`.yaml`文件：选择`Export to File`，选择下载位置，然后单击`Save`
   - 要将 Recipe 的 YAML 内容复制到剪贴板：选择`Copy YAML`

其他 Desktop 用户可以将 Recipe[导入](https://block.github.io/goose/docs/guides/recipes/storing-recipes#importing-recipes)到 Recipe Library。

</TabItem>
<TabItem value="cli" label="goose CLI">

导出或复制 Recipe 内容只能通过 Desktop 完成，但你可以直接复制本地 Recipe 文件。

CLI 用户可以使用`goose run --recipe <FILE>`运行共享的 Recipe 文件，也可以使用`goose recipe open <FILE>`直接在 goose Desktop 中打开。详情请参阅[CLI 命令指南](https://block.github.io/goose/docs/guides/goose-cli-commands#recipe)。

</TabItem>
</Tabs>

### 安排 Recipe
<Tabs groupId="interface">
<TabItem value="ui" label="goose Desktop" default>

按计划运行 goose Recipe，实现自动化。创建计划时，你需要配置：
- **名称**：计划的描述性名称
- **来源**：要运行的 Recipe
- **执行模式**：Recipe 在后台运行（不显示窗口，保存结果），还是在前台运行（如果 goose Desktop 正在运行则打开窗口，否则在后台运行）
- **频率和时间**：运行 Recipe 的时间（例如每 20 分钟运行一次，或每周五上午 10 点运行）。你选择的频率和时间会转换为 goose 使用的[cron 表达式](https://en.wikipedia.org/wiki/Cron#Cron_expression)。

**从 Recipe Library 创建计划：**

1. 单击左上角的<PanelLeft className="inline" size={16} />按钮，打开侧边栏
2. 单击侧边栏中的`Recipes`
3. 找到要安排计划的 Recipe，单击<Clock className="inline" size={16} />按钮
4. 单击`Create Schedule`
5. 在出现的对话框中配置计划。对于**来源**，系统已提供你的 Recipe 链接。
6. 单击`Create Schedule`

**从 Scheduler 视图创建计划：**

1. 单击左上角的<PanelLeft className="inline" size={16} />按钮，打开侧边栏
2. 单击`Scheduler`
3. 单击`Create Schedule`
4. 在出现的对话框中配置计划。对于**来源**，选择`.yaml`或`.yml`文件，或者提供一个[Recipe 链接](#share-recipe)。
5. 单击`Create Schedule`

**管理已安排的 Recipe**

你安排的 Recipe 会列在`Scheduler`页面中。
单击某个计划可以查看详细信息、了解上次运行时间，并对已安排的 Recipe 执行以下操作：
- `Run Schedule Now`：手动触发 Recipe
- `Edit Schedule`：更改计划频率
- `Pause Schedule`：停止自动运行 Recipe

在`Schedule Details`页面底部，你可以查看已安排的 Recipe 创建的会话列表，并打开或恢复每个会话。

</TabItem>
<TabItem value="cli" label="goose CLI">
使用[cron 表达式](https://en.wikipedia.org/wiki/Cron#Cron_expression)安排 goose Recipe 的运行，实现自动化。

```bash
# Add a new scheduled recipe which runs every day at 9 AM
goose schedule add --schedule-id daily-report --cron "0 0 9 * * *" --recipe-source ./recipes/daily-report.yaml
```
你可以使用 5、6 或 7 位的 cron 表达式，实现完整的计划精度，格式为"seconds minutes hours day-of-month month day-of-week year"。

详细示例和选项请参阅[`schedule`命令文档](https://block.github.io/goose/docs/guides/goose-cli-commands.md#schedule)。
</TabItem>
</Tabs>

### 核心组件

Recipe 需要以下核心组件：

- **Instructions**：定义 Agent 的行为和能力
  - 作为 Agent 的使命声明
  - 让 Agent 能够随时处理相关任务
  - 未提供 prompt 时必需

- **Prompt**（可选）：自动启动对话
  - 如果没有 prompt，Agent 会等待用户输入
  - 适用于具体、即时的任务
  - 未提供 instructions 时必需

- **Activities**：以可点击气泡形式显示的示例任务
  - 帮助用户了解 Recipe 的功能
  - 让用户更容易开始使用

### 高级功能

#### 自动重试逻辑

Recipe 可以包含重试逻辑，在满足成功标准前自动多次尝试完成任务。以下场景尤其适用：

- **自动化工作流**：需要确保任务成功完成
- **开发任务**：例如可能需要多次尝试才能通过的测试
- **系统操作**：需要验证和清理

**基本重试配置：**

```yaml
retry:
  max_retries: 3
  checks:
    - type: shell
      command: "test -f output.txt"  # Check if output file exists
  on_failure: "rm -f temp_files*"   # Cleanup on failure
```

**工作方式：**
1. Recipe 使用提供的说明正常执行
2. 执行完成后，成功检查会验证结果
3. 如果验证失败且仍有重试机会：
   - 运行可选清理命令
   - 将 Agent 状态重置为初始状态
   - 重新开始执行 Recipe
4. 持续处理，直至成功或达到最大重试次数

完整的重试配置选项和示例请参阅[Recipe 参考指南](https://block.github.io/goose/docs/guides/recipes/recipe-reference#retry)。

#### 用于自动化的结构化输出

Recipe 可以强制生成[结构化 JSON 输出](https://block.github.io/goose/docs/guides/recipes/recipe-reference#response)，非常适合需要可靠解析和处理 Agent 响应的自动化工作流。主要优势包括：

- **可靠解析**：为脚本、自动化和 CI/CD 流水线提供一致的 JSON 格式
- **内置验证**：确保输出符合你的要求
- **轻松提取**：最终输出显示为单行，便于解析

结构化输出尤其适用于：
- **开发工作流**：代码分析报告、包含通过/失败计数的测试结果，以及包含部署就绪状态的构建状态
- **数据处理**：包含计数和验证状态的结果，以及带结构化发现的内容分析
- **文档生成**：便于后续处理的一致元数据和结构化项目报告

**结构化输出配置示例：**

```yaml
response:
  json_schema:
    type: object
    properties:
      build_status:
        type: string
        enum: ["success", "failed", "warning"]
        description: "Overall build result"
      tests_passed:
        type: number
        description: "Number of tests that passed"
      tests_failed:
        type: number
        description: "Number of tests that failed"
      artifacts:
        type: array
        items:
          type: string
        description: "Generated build artifacts"
      deployment_ready:
        type: boolean
        description: "Whether the build is ready for deployment"
    required:
      - build_status
      - tests_passed
      - tests_failed
      - deployment_ready
```

**工作方式：**
1. Recipe 使用提供的说明正常运行
2. goose 调用`final_output`工具，输出符合你架构的 JSON
3. 根据 JSON Schema 验证输出
4. 如果验证失败，goose 会收到错误详情并必须修正输出
5. 最终通过验证的 JSON 会显示为输出的最后一行，便于提取

**自动化用法示例：**

```bash
# Run recipe and extract JSON output
goose run --recipe analysis.yaml --params project_path=./src > output.log
RESULT=$(tail -n 1 output.log)
echo "Analysis Status: $(echo $RESULT | jq -r '.build_status')"
echo "Issues Found: $(echo $RESULT | jq -r '.tests_failed')"
```

:::info
在 goose CLI 和 goose Desktop 中运行的 Recipe 均支持结构化输出。不过，创建和编辑`json_schema`配置必须在 Recipe 文件中手动完成。
:::

### 包含的内容

Recipe 包含：

- AI 说明（目标/用途）
- 建议活动（供用户单击的示例）
- 已启用的扩展及其配置
- 项目文件夹或文件上下文
- 初始设置（但不包含完整对话历史）
- 运行 Recipe 时使用的模型和提供方（可选）
- 重试逻辑和成功验证配置（如果已配置）

为保护你的隐私和系统完整性，goose 不会纳入：

- 全局和本地记忆
- API 密钥和个人凭据
- 系统级 goose 设置

这意味着，如果 Recipe 依赖这些内容，其他人可能需要提供自己的凭据或记忆上下文。

### 了解更多
查看[Recipes](https://block.github.io/goose/docs/guides/recipes)指南，获取更多文档、工具和资源，帮助你熟练掌握 goose Recipe。

---

## 保存 Recipe

> 原文：https://block.github.io/goose/docs/guides/recipes/storing-recipes

本指南介绍如何存储、整理和查找 goose Recipe，以便之后再次访问。

:::info Desktop UI 与 CLI
- **goose Desktop** 提供可视化的 Recipe Library，用于浏览和管理已保存的 Recipe
- **goose CLI** 将 Recipe 保存为文件，你可以通过文件路径或环境变量查找
:::

### 了解 Recipe 存储

保存 Recipe 前，了解可存储的位置以及存储位置对可用范围的影响非常重要。

#### Recipe 存储位置

| 类型 | 位置 | 可用范围 | 适用场景 |
|------|----------|-------------|----------|
| **全局** | `~/.config/goose/recipes/` | 所有项目和会话 | 个人工作流、通用 Recipe |
| **本地** | `YOUR_WORKING_DIRECTORY/.goose/recipes/` | 仅在该项目中工作时可用 | 项目专属工作流、团队 Recipe |

**选择全局存储的情况：**
- 你希望 Recipe 在所有项目中都可用
- 这是个人工作流或通用 Recipe
- 你是该 Recipe 的主要使用者

**选择本地存储的情况：**
- Recipe 专用于某个项目
- 你正在与团队协作，希望共享 Recipe
- Recipe 依赖项目专属文件或配置

### 存储 Recipe

<Tabs groupId="interface">
<TabItem value="desktop" label="goose Desktop" default>

**保存新 Recipe：**

1. 从侧边栏打开`Recipes`，然后单击`Create Recipe`
2. 完成 Recipe Editor 中的内容，然后单击`Save Recipe`，将其保存到 Recipe Library

**保存修改后的 Recipe：**

如果你已在使用一个 Recipe，并希望保存修改后的版本：
1. 单击应用底部的<ChefHat className="inline" size={16}/>按钮；发送第一条消息后该按钮会显示
2. 根据需要编辑 instructions、prompt 或其他字段
3. 单击`Save Recipe`

:::info
如果你修改 Recipe 并使用新名称保存，系统会生成新的 Recipe 和新的链接。你仍然可以从 Recipe Library 或使用原始链接运行原始 Recipe。如果编辑 Recipe 时没有更改名称，Recipe Library 中的版本会更新，但你仍然可以通过链接运行原始 Recipe。
:::

</TabItem>
<TabItem value="cli" label="goose CLI">

使用你喜欢的编辑器创建 Recipe 文件。将项目专属 Recipe 存储在`.goose/recipes/`中，将全局 Recipe 存储在`~/.config/goose/recipes/`中。CLI 可以运行 YAML 或 JSON 格式的 Recipe。

</TabItem>
</Tabs>

#### 导入 Recipe

<Tabs groupId="interface">
<TabItem value="desktop" label="goose Desktop">
通过深层链接或 Recipe 文件导入 Recipe：

1. 单击左上角的<PanelLeft className="inline" size={16} />按钮，打开侧边栏
2. 单击侧边栏中的`Recipes`
3. 单击`Import Recipe`
4. 选择导入方式：
   - 通过链接导入：在`Recipe Deeplink`下粘贴[Recipe 链接](https://block.github.io/goose/docs/guides/recipes/session-recipes#share-via-recipe-link)
   - 通过文件导入：在`Recipe File`下单击`Choose File`，选择 Recipe 文件，然后单击`Open`
5. 单击`Import Recipe`，将 Recipe 的副本保存到 Recipe Library

:::warning Recipe 文件格式
goose Desktop 接受`.yaml`、`.yml`和`.json`文件，但**CLI 仅支持`.yaml`和`.json`**。如需在两个界面中都兼容，请避免使用`.yml`扩展名。

所有 Recipe 格式遵循相同的[架构结构](https://block.github.io/goose/docs/guides/recipes/recipe-reference#core-recipe-schema)。
:::

</TabItem>
<TabItem value="cli" label="goose CLI">
导入 Recipe 只能在 goose Desktop 中进行。
</TabItem>
</Tabs>

### 查找可用 Recipe

<Tabs groupId="interface">
<TabItem value="desktop" label="goose Desktop" default>

**访问 Recipe Library：**
1. 单击左上角的<PanelLeft className="inline" size={16} />按钮，打开侧边栏
2. 单击`Recipes`，查看 Recipe Library
3. 浏览可用的 Recipe，其中会显示：
   - Recipe 标题和描述
   - 上次修改日期
   - Recipe 是全局存储还是本地存储

:::info Desktop 与 CLI 的 Recipe 发现方式
Desktop 的 Recipe Library 会显示你明确保存或导入的所有 Recipe。它不像 CLI 那样自动发现文件系统中的 Recipe 文件。
:::

</TabItem>
<TabItem value="cli" label="goose CLI">

使用`goose recipe list`命令，从多个来源查找所有可用 Recipe：

**基本用法**

```bash
# List all available recipes
goose recipe list

# Show detailed information including titles and full paths
goose recipe list --verbose

# Output in JSON format for automation
goose recipe list --format json
```

**Recipe 发现过程**

goose 按以下顺序搜索 Recipe：

1. **当前目录**：`.`（查找`*.yaml`和`*.json`文件）
2. **自定义路径**：[`GOOSE_RECIPE_PATH`](https://block.github.io/goose/docs/guides/environment-variables#recipe-configuration)环境变量指定的目录
3. **全局 Recipe 库**：`~/.config/goose/recipes/`（或操作系统上的对应位置）
4. **本地项目 Recipe**：`./.goose/recipes/`
5. **GitHub 仓库**：配置了[`GOOSE_RECIPE_GITHUB_REPO`](https://block.github.io/goose/docs/guides/environment-variables#recipe-configuration)环境变量时

**输出示例**

*默认文本格式：*

```bash
$ goose recipe list
Available recipes:
goose-self-test - A comprehensive meta-testing recipe - local: ./goose-self-test.yaml
hello-world - A sample recipe demonstrating basic usage - local: ~/.config/goose/recipes/hello-world.yaml
job-finder - Find software engineering positions - local: ~/.config/goose/recipes/job-finder.yaml
```

*详细模式：*

```bash
$ goose recipe list --verbose
Available recipes:
  goose-self-test - A comprehensive meta-testing recipe - local: ./goose-self-test.yaml
    Title: goose Self-Testing Integration Suite
    Path: ./goose-self-test.yaml
  hello-world - A sample recipe demonstrating basic usage - local: ~/.config/goose/recipes/hello-world.yaml
    Title: Hello World Recipe
    Path: /Users/username/.config/goose/recipes/hello-world.yaml
```

*用于自动化的 JSON 格式：*

```json
[
  {
    "name": "goose-self-test",
    "source": "Local",
    "path": "./goose-self-test.yaml",
    "title": "goose Self-Testing Integration Suite",
    "description": "A comprehensive meta-testing recipe"
  },
  {
    "name": "hello-world",
    "source": "GitHub",
    "path": "recipes/hello-world.yaml",
    "title": "Hello World Recipe",
    "description": "A sample recipe demonstrating basic usage"
  }
]
```

**配置 Recipe 来源**

添加自定义 Recipe 目录：

```bash
export GOOSE_RECIPE_PATH="/path/to/my/recipes:/path/to/team/recipes"
goose recipe list
```

配置 GitHub Recipe 仓库：

```bash
export GOOSE_RECIPE_GITHUB_REPO="myorg/goose-recipes"
goose recipe list
```

如需了解更多配置选项，请参阅[环境变量指南](https://block.github.io/goose/docs/guides/environment-variables#recipe-configuration)。

**手动浏览目录（高级）**

如果需要手动浏览 Recipe 目录：

```bash
# List recipes in default global location
ls ~/.config/goose/recipes/

# List recipes in current project
ls .goose/recipes/

# Search for all recipe files
find . -name "*.yaml" -path "*/recipes/*" -o -name "*.json" -path "*/recipes/*"
```

:::tip
推荐使用`goose recipe list`命令查找 Recipe，因为它会自动搜索所有已配置的来源，并提供一致的格式。
:::

</TabItem>
</Tabs>

### 使用已保存的 Recipe

<Tabs groupId="interface">
<TabItem value="desktop" label="goose Desktop" default>

1. 单击左上角的<PanelLeft className="inline" size={16} />按钮，打开侧边栏
2. 单击`Recipes`
3. 在 Recipe Library 中找到你的 Recipe
4. 选择以下一种方式：
   - 单击`Use`，立即运行
   - 单击`Preview`先查看 Recipe 详情，然后单击**Load Recipe**运行

</TabItem>
<TabItem value="cli" label="goose CLI">

找到 Recipe 文件后，[运行 Recipe](https://block.github.io/goose/docs/guides/recipes/session-recipes#run-a-recipe)或[在 goose Desktop 中打开](https://block.github.io/goose/docs/guides/goose-cli-commands#recipe)。

:::tip 格式兼容性
CLI 无需转换即可运行从 goose Desktop 保存的 Recipe。无论通过 CLI 创建还是通过 Desktop 保存，Recipe 均可与所有 Recipe 命令配合使用。
:::

</TabItem>
</Tabs>

---

## 用于特定任务的子 Recipe

> 原文：https://block.github.io/goose/docs/guides/recipes/subrecipes

子 Recipe 是被另一个 Recipe 调用、用于执行特定任务的 Recipe。它们支持：
- **多步骤工作流**——将复杂任务拆分为多个阶段，每个阶段使用专门的能力
- **可复用组件**——创建可在各种工作流中使用的常见任务

:::warning 实验性功能
子 Recipe 是一项仍在积极开发中的实验性功能。其行为和配置可能会在未来版本中发生变化。
:::

### 子 Recipe 的工作方式

“主 Recipe”在`sub_recipes`字段中注册自己的子 Recipe，其中包含以下字段：

- `name`：子 Recipe 的唯一标识符，用于生成工具名称
- `path`：子 Recipe 文件的路径（相对路径或绝对路径）
- `values`：（可选）始终传递给子 Recipe 的预配置参数值

运行主 Recipe 时，goose 会为每个子 Recipe 生成一个工具，该工具：
- 接受子 Recipe 定义的参数
- 在具有独立上下文的单独会话中执行子 Recipe
- 将输出返回给主 Recipe

子 Recipe 会话彼此隔离——它们不会与主 Recipe 或其他子 Recipe 共享对话历史、记忆或状态。此外，子 Recipe 不能再定义自己的子 Recipe（不允许嵌套）。

:::note
定义了`sub_recipes`的 Recipe 会自动注入`summon`平台扩展，因此无需在`extensions`中列出就可以使用`delegate`工具。
:::

#### 参数处理

子 Recipe 接收的参数可以使用`{{ parameter_name }}`语法放入提示词和说明中。子 Recipe 通过两种方式接收参数：

1. **预设值**：在`values`字段中定义的固定参数值会自动提供，运行时不能覆盖
2. **基于上下文的参数**：AI Agent 可以从对话上下文中提取参数值，包括之前子 Recipe 的结果

预设值优先于基于上下文的参数。如果对话上下文和`values`字段提供了相同参数，则使用`values`中的值。

:::tip
将多行参数值传递给子 Recipe 时，请使用`indent()`筛选器保持 YAML 格式有效，例如：`{{ content | indent(2) }}`。详情请参阅[模板支持](https://block.github.io/goose/docs/guides/recipes/recipe-reference#template-support)。
:::

### 示例

#### 顺序处理

此代码审查流水线示例展示了一个主 Recipe 如何使用两个子 Recipe 执行全面的代码审查：

**用法：**

```bash
goose run --recipe code-review-pipeline.yaml --params repository_path=/path/to/repo
```

**主 Recipe：**

```yaml
# code-review-pipeline.yaml
version: "1.0.0"
title: "Code Review Pipeline"
description: "Automated code review using subrecipes"
instructions: |
  Perform a code review using the available subrecipe tools.
  Run security analysis first, then code quality analysis.

parameters:
  - key: repository_path
    input_type: string
    requirement: required
    description: "Path to the repository to review"

sub_recipes:
  - name: "security_scan"
    path: "./subrecipes/security-analysis.yaml"
    values:
      scan_level: "comprehensive"

  - name: "quality_check"
    path: "./subrecipes/quality-analysis.yaml"

extensions:
  - type: builtin
    name: developer
    timeout: 300
    bundled: true

prompt: |
  Review the code at {{ repository_path }} using the subrecipe tools.
  Run security scan first, then quality analysis.
```

**子 Recipe：**

<details>
<summary>security_scan</summary>

```yaml
# subrecipes/security-analysis.yaml
version: "1.0.0"
title: "Security Scanner"
description: "Analyze code for security vulnerabilities"
instructions: |
  You are a security expert. Analyze the provided code for security issues.
  Focus on common vulnerabilities like SQL injection, XSS, and authentication flaws.

parameters:
  - key: repository_path
    input_type: string
    requirement: required
    description: "Path to the code to analyze"

  - key: scan_level
    input_type: string
    requirement: optional
    default: "standard"
    description: "Depth of security scan (basic, standard, comprehensive)"

extensions:
  - type: builtin
    name: developer
    timeout: 300
    bundled: true

prompt: |
  Perform a {{ scan_level }} security analysis on the code at {{ repository_path }}.
  Report any security vulnerabilities found with severity levels and recommendations.
```
</details>

<details>
<summary>quality_check</summary>

```yaml
# subrecipes/quality-analysis.yaml
version: "1.0.0"
title: "Code Quality Analyzer"
description: "Analyze code quality and best practices"
instructions: |
  You are a code quality expert. Review code for maintainability,
  readability, and adherence to best practices.

parameters:
  - key: repository_path
    input_type: string
    requirement: required
    description: "Path to the code to analyze"

extensions:
  - type: builtin
    name: developer
    timeout: 300
    bundled: true

prompt: |
  Analyze the code quality at {{ repository_path }}.
  Check for code smells, complexity issues, and suggest improvements.
```
</details>

:::tip
如果子 Recipe 彼此独立，可[并行运行子 Recipe](https://block.github.io/goose/docs/tutorials/subrecipes-in-parallel)，同时执行多个子 Recipe，从而加快运行速度。
:::

#### 条件处理

此智能项目分析器示例展示了如何根据分析结果，通过条件逻辑选择不同的子 Recipe：

**用法：**

```bash
goose run --recipe smart-analyzer.yaml --params repository_path=/path/to/project
```

**主 Recipe：**

```yaml
# smart-analyzer.yaml
version: "1.0.0"
title: "Smart Project Analyzer"
description: "Analyze project and choose appropriate processing based on type"
instructions: |
  First examine the repository to determine the project type (web app, CLI tool, library, etc.).
  Based on what you find:
  - If it's a web application, use the web_security_audit subrecipe
  - If it's a CLI tool or library, use the api_documentation subrecipe
  Only run one subrecipe based on your analysis.

parameters:
  - key: repository_path
    input_type: string
    requirement: required
    description: "Path to the repository to analyze"

sub_recipes:
  - name: "web_security_audit"
    path: "./subrecipes/web-security.yaml"
    values:
      check_cors: "true"
      check_csrf: "true"

  - name: "api_documentation"
    path: "./subrecipes/api-docs.yaml"
    values:
      format: "markdown"

extensions:
  - type: builtin
    name: developer
    timeout: 300
    bundled: true

prompt: |
  Analyze the project at {{ repository_path }} and determine its type.
  Then run the appropriate subrecipe tool based on your findings.
```

**子 Recipe：**

<details>
<summary>web_security_audit</summary>

```yaml
# subrecipes/web-security.yaml
version: "1.0.0"
title: "Web Security Auditor"
description: "Security audit for web applications"
instructions: |
  You are a web security specialist. Audit web applications for
  security vulnerabilities specific to web technologies.

parameters:
  - key: repository_path
    input_type: string
    requirement: required
    description: "Path to the web application code"

  - key: check_cors
    input_type: string
    requirement: optional
    default: "false"
    description: "Whether to check CORS configuration"

  - key: check_csrf
    input_type: string
    requirement: optional
    default: "false"
    description: "Whether to check CSRF protection"

extensions:
  - type: builtin
    name: developer
    timeout: 300
    bundled: true

prompt: |
  Perform a web security audit on {{ repository_path }}.
  {% if check_cors == "true" %}Check CORS configuration for security issues.{% endif %}
  {% if check_csrf == "true" %}Verify CSRF protection is properly implemented.{% endif %}
  Focus on web-specific vulnerabilities like XSS, authentication flaws, and session management.
```
</details>

<details>
<summary>api_documentation</summary>

```yaml
# subrecipes/api-docs.yaml
version: "1.0.0"
title: "API Documentation Generator"
description: "Generate documentation for APIs and libraries"
instructions: |
  You are a technical writer specializing in API documentation.
  Create comprehensive documentation for code libraries and APIs.

parameters:
  - key: repository_path
    input_type: string
    requirement: required
    description: "Path to the code to document"

  - key: format
    input_type: string
    requirement: optional
    default: "markdown"
    description: "Output format for documentation (markdown, html, rst)"

extensions:
  - type: builtin
    name: developer
    timeout: 300
    bundled: true

prompt: |
  Generate {{ format }} documentation for the code at {{ repository_path }}.
  Include API endpoints, function signatures, usage examples, and installation instructions.
  Focus on making it easy for developers to understand and use this code.
```
</details>

#### 基于上下文的参数传递

此旅行规划器示例展示了子 Recipe 如何从对话上下文中接收参数，其中包括之前子 Recipe 的结果：

**用法：**

```bash
goose run --recipe travel-planner.yaml
```

**主 Recipe：**

```yaml
# travel-planner.yaml
version: "1.0.0"
title: "Travel Activity Planner"
description: "Get weather data and suggest appropriate activities"
instructions: |
  Plan activities by first getting weather data, then suggesting activities based on conditions.

prompt: |
  Plan activities for Sydney by first getting weather data, then suggesting activities based on the weather conditions we receive.

sub_recipes:
  - name: weather_data
    path: "./subrecipes/weather-data.yaml"
    # No values - location parameter comes from prompt context

  - name: activity_suggestions
    path: "./subrecipes/activity-suggestions.yaml"
    # weather_conditions parameter comes from conversation context

extensions:
  - type: builtin
    name: developer
    timeout: 300
    bundled: true
```

**子 Recipe：**

<details>
<summary>weather_data</summary>

```yaml
# subrecipes/weather-data.yaml
version: "1.0.0"
title: "Weather Data Collector"
description: "Fetch current weather conditions for a location"
instructions: |
  You are a weather data specialist. Gather current weather information
  including temperature, conditions, and seasonal context.

parameters:
  - key: location
    input_type: string
    requirement: required
    description: "City or location to get weather data for"

extensions:
  - type: stdio
    name: weather
    cmd: uvx
    args:
      - mcp_weather@latest
    timeout: 300
    description: "Weather data for trip planning"
  - type: builtin
    name: developer
    timeout: 300
    bundled: true

prompt: |
  Get the current weather conditions for {{ location }}.
  Include temperature, weather conditions (sunny, rainy, etc.),
  and any relevant seasonal information.
```
</details>

<details>
<summary>activity_suggestions</summary>

```yaml
# subrecipes/activity-suggestions.yaml
version: "1.0.0"
title: "Activity Recommender"
description: "Suggest activities based on weather conditions"
instructions: |
  You are a travel expert. Recommend appropriate activities and attractions
  based on current weather conditions.

parameters:
  - key: weather_conditions
    input_type: string
    requirement: required
    description: "Current weather conditions to base recommendations on"

extensions:
  - type: builtin
    name: developer
    timeout: 300
    bundled: true

prompt: |
  Based on these weather conditions: {{ weather_conditions }},
  suggest appropriate activities, attractions, and travel tips.
  Include both indoor and outdoor options as relevant.
```
</details>

在此示例中：
- `weather_data`子 Recipe 从提示词上下文中获取地点（AI 从自然语言提示词中提取"Sydney"）
- `activity_suggestions`子 Recipe 从对话上下文中获取天气状况（AI 使用第一个子 Recipe 的天气结果）

### 最佳实践
- **单一职责**：每个子 Recipe 都应有一个明确用途
- **清晰的参数**：使用有描述性的名称和说明
- **预设固定值**：对不会更改的参数使用`values`
- **独立测试**：组合之前先单独验证子 Recipe 能否正常工作

:::tip 控制子 Recipe 执行
每个子 Recipe 都可以指定自己的`settings.max_turns`值，以控制执行限制。如果未指定，子 Recipe 会继承父 Recipe 的`max_turns`设置。详情请参阅[Recipe Settings](https://block.github.io/goose/docs/guides/recipes/recipe-reference#settings)。

```yaml
# subrecipes/quick-scan.yaml
version: "1.0.0"
title: "Quick Security Scan"
settings:
  max_turns: 10  # Limit this subrecipe to 10 turns
instructions: "Perform a quick security scan"
prompt: "Scan for common vulnerabilities"
```
:::

### 了解更多

查看[Recipes](https://block.github.io/goose/docs/guides/recipes)指南，获取更多文档、工具和资源，帮助你熟练掌握 goose Recipe。
