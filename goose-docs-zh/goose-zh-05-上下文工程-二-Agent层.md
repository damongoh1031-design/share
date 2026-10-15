# goose 官方文档中文手册：第 05 章　上下文工程（二）：Agent 层

## 自定义 Agent

> 原文：https://block.github.io/goose/docs/guides/context-engineering/custom-agents

自定义 Agent 是针对特定角色、行为或专业领域的可复用 goose 配置。每个 Agent 打包了一个名称、描述、可选的模型偏好和指令，让你可以快速让 goose 以某个专业角色工作，例如代码审查者、文档撰写者、测试规划者或发布助手。

当你希望跨多个会话保持同一角色或行为、又不想重复输入相同指令时，就使用自定义 Agent。

### 创建 Agent 文件

Agent 以带 YAML frontmatter 的 Markdown 文件形式存储。你可以在编辑器中直接创建或编辑这些文件。

全局 Agent 可在所有 goose 会话中使用：

```text
~/.agents/agents/
```

项目 Agent 在 goose 于该项目中工作时可用：

```text
<project>/.agents/agents/
```

:::note 兼容路径
goose 还会从 `.goose/agents/`、`.claude/agents/`、`~/.goose/agents/`、`~/.claude/agents/`、goose 平台专属配置的 agents 目录，以及项目本地的 `.agents/agents/` 中发现 Agent。新的共享 Agent 应使用 `.agents/agents/`（项目 Agent）或 `~/.agents/agents/`（全局 Agent）。
:::

如果目录尚不存在，先创建它，然后为你的 Agent 添加一个 Markdown 文件：

```markdown title="~/.agents/agents/code-reviewer.md"
---
name: code-reviewer
description: Reviews code for correctness, maintainability, and risk
model: gpt-5.5
---

You are a senior code reviewer. Review changes for correctness, maintainability, security, and test coverage. Be direct, prioritize issues by severity, and suggest concrete fixes.
```

frontmatter 支持以下字段：

| 字段 | 是否必填 | 描述 |
|---|---:|---|
| `name` | 是 | 用于列出、加载、提及或委派给该 Agent 的名称。 |
| `description` | 否 | 列出 Agent 时显示的简短摘要。 |
| `model` | 否 | 该 Agent 偏好的模型。 |

frontmatter 中只有 `name` 是必填的。`description` 和 `model` 是可选的。Markdown 正文是该 Agent 的指令；如果你希望该 Agent 在聊天中作为可用来源出现，正文不应为空。

### 使用 Agent

创建 Agent 文件后，从一个能发现该 Agent 的工作目录启动 goose。项目 Agent 从当前工作目录发现，而全局 Agent 从你的主目录/配置目录发现。

#### 列出可用 Agent

在 goose 聊天会话中，让 goose 列出可用来源：

```text
list available sources
```

这是给 goose 的提示词，不是终端命令。当来源加载可用时，goose 会把可发现的 Agent 与 Recipe 和子 Recipe 一起列出。

你可以通过名称提及来调用某个 Agent：

```text
@code-reviewer review the current diff
```

或者让 goose 使用它：

```text
Use the code-reviewer agent to review this pull request.
```

在带提及选择器的聊天界面中，输入 `@` 并按名称选择该 Agent，例如 `code-reviewer`。

#### 把工作委派给 Agent

当你希望一个隔离的专家执行任务并把结果返回当前对话时，就使用自定义 Agent。

```text
Delegate to code-reviewer: review the current diff and identify the highest-risk issues.
```

或者，如果你正在编写直接调用委派工具的提示词，就把该 Agent 的 `name` 用作来源：

```text
Use the code-reviewer agent to review this pull request.
```

被委派的 Agent 会在一个独立会话中运行，并使用该 Agent 文件中的指令。它可以使用该 Agent frontmatter 中指定的模型。某些界面还允许你在委派时覆盖诸如模型、提供方、temperature 或最大轮数之类的设置。

#### 把 Agent 的指令加载到当前对话

当你希望当前对话采用某个 Agent 的指令、但不创建单独的委派会话时，就把该 Agent 作为已加载的上下文使用。

```text
Load the code-reviewer agent, then review this change.
```

加载 Agent 会把它的指令加入当前对话上下文。委派给 Agent 则会单独运行它并返回结果。

### 示例 Agent

#### 代码审查者

```markdown title="~/.agents/agents/code-reviewer.md"
---
name: code-reviewer
description: Reviews code for correctness, maintainability, and risk
model: gpt-5.5
---

You are a senior code reviewer. Review changes for correctness, maintainability, security, and test coverage.

Prioritize:
- bugs and correctness issues
- security or privacy risks
- missing tests
- unnecessary complexity
- unclear naming or structure

Be direct. Group findings by severity and suggest concrete fixes.
```

#### 文档撰写者

```markdown title="~/.agents/agents/docs-writer.md"
---
name: docs-writer
description: Writes clear developer documentation
---

You are a developer documentation writer. Explain features clearly, use practical examples, and avoid marketing language.

When writing docs:
- start with what the user can accomplish
- show the shortest working example
- explain important options after the example
- call out limitations and prerequisites
```

### 何时使用 Agent、Skill 还是 Recipe

| 用途 | 最佳选择 |
|---|---|
| 为某个任务改变 goose 的角色、语气或指令 | 自定义 Agent |
| 教 goose 一个可按需加载的可复用工作流或领域专属流程 | [Skill](https://block.github.io/goose/docs/guides/context-engineering/using-skills) |
| 把可重复的任务与提示词、设置、扩展和参数打包 | [Recipe](https://block.github.io/goose/docs/guides/recipes) |
| 把工作委派给另一个隔离的 goose 实例 | [子代理](https://block.github.io/goose/docs/guides/context-engineering/subagents) |

Agent 定义 goose 在某个任务中应当是谁。Skill 和 Recipe 定义 goose 应当知道什么或做什么。

#### 自定义 Agent 可以被调度运行吗？

不能直接这样做。自定义 Agent 是可复用的角色，不是被调度的任务。要按计划运行某件事，请创建一个 [Recipe](https://block.github.io/goose/docs/guides/recipes) 并调度该 Recipe。如果你希望被调度的任务表现得像自定义 Agent，就把该 Agent 的指令放进 Recipe 中，或让该 Recipe 委派给那个 Agent。

#### 自定义 Agent 有工作流吗？

没有。自定义 Agent 定义 goose 在某个任务中应当是谁：它的角色、行为、指令以及可选的模型偏好。它不定义分步的工作流。当你需要可重复的步骤、参数、扩展配置或调度执行时，请使用 Recipe。

#### 自定义 Agent 能使用 Skill 吗？

可以。自定义 Agent 可以使用会话中可用的 Skill。Skill 仍然通过 goose 正常的 Skill 行为被发现和加载，因此当你的请求匹配某个 Skill 或你明确要求某个 Skill 时，该 Agent 就能使用它们。

#### 自定义 Agent 能运行 Recipe 吗？

自定义 Agent 不包含也不会自动运行 Recipe。你可以带某个 Recipe 启动 goose，在相关工具可用时让 goose 加载或委派某个 Recipe，或创建一个把自定义 Agent 的指令作为其工作流一部分的 Recipe。

#### 自定义 Agent 能使用 MCP 服务器吗？

可以。自定义 Agent 可以使用当前会话中已启用的 MCP 服务器和扩展。Agent 文件本身并不定义单独的 MCP 服务器列表。如果你需要一个带有特定扩展集合的可复用配置，请使用 Recipe。

#### 自定义 Agent 能调用子代理吗？

可以，只要会话中有委派工具可用。自定义 Agent 可以像默认的 goose Agent 一样让 goose 把工作委派给子代理。被委派的子代理在隔离会话中运行，且不会自动继承完整的父对话。

#### 一个自定义 Agent 能调用另一个自定义 Agent 吗？

可以，通过委派实现。例如，只要另一个自定义 Agent 可被发现，某个自定义 Agent 就可以按名称把任务委派给它。这对专用 Agent 之间的一次性协作很有用。

对于可重复的链式调用，请使用一个明确界定顺序的 Recipe，例如先委派给某个审查者 Agent，再委派给某个文档 Agent，然后合并结果。

---

## 子代理

> 原文：https://block.github.io/goose/docs/guides/context-engineering/subagents

子代理是独立实例，它们在执行任务的同时让你的主对话保持干净和专注。把它们想象成处理特定工作的临时助手，通过把工作卸载到独立实例来实现进程隔离和上下文保留。

<details>
  <summary>子代理演示</summary>
  <iframe
    class="aspect-ratio"
    src="https://youtube.com/embed/Uk4TtJUykK4"
    title="Subagents Explained"
    frameBorder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowFullScreen
  ></iframe>
</details>

### 如何使用子代理

:::tip 子代理的自主创建
当 goose 判定子代理对你的任务有益时，它可以自主决定使用子代理——你并不总是需要显式请求它们。这会在自主[权限模式](https://block.github.io/goose/docs/guides/managing-tools/goose-permissions)（默认）下自动发生。在手动批准、智能批准和纯聊天模式下，子代理被禁用。
:::

要使用子代理，请用自然语言让 goose 委派任务。goose 会自动决定何时生成子代理，并处理它们的生命周期。你可以：

1. **请求专门帮助**：「用一个代码审查者分析这个函数的安全问题」
2. **引用特定 Recipe**：「用 'security-auditor' Recipe 扫描这个端点」
3. **运行并行任务**：「同时创建三个 HTML 模板」
4. **委派复杂工作**：「研究量子计算进展并总结发现」
5. **控制扩展访问**：「创建一个只带 developer 扩展的子代理来重构代码」

你可以按顺序或并行运行多个子代理。

| 类型 | 描述 | 触发关键词 | 示例 |
|------|-------------|------------------|---------|
| **顺序**（默认） | 任务一个接一个执行 | "first...then"、"after" | `"First analyze the code, then generate documentation"` |
| **并行** | 任务同时执行 | "parallel"、"simultaneously"、"at the same time"、"concurrently" | `"Create three HTML templates in parallel"` |

### 监控子代理活动

当 goose 把工作委派给子代理时，你可以实时看到该子代理的工具调用。这种透明度有助于你理解子代理在做什么，并核实它是否走在正确的轨道上。

<Tabs groupId="interface">
  <TabItem value="desktop" label="goose Desktop" default>
    子代理的工具调用会作为对话中可展开的区块出现。点击展开即可看到每个工具调用的完整细节，包括：
    - 正在调用的工具名称
    - 传给该工具的参数
    - 工具输出和结果
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    子代理的工具调用会内联显示，并带有展示工具名称和扩展的视觉指示符。例如：

    ```text
    [subagent:16] text_editor | developer
    ```

    每个工具调用会显示：
    - 子代理标识符（例如 `subagent:16`）
    - 工具名称（例如 `text_editor`）
    - 提供该工具的扩展（例如 `developer`）
  </TabItem>
</Tabs>

:::info
如果某个子代理失败或超时（默认 5 分钟），你将不会收到来自该子代理的任何输出。对于并行执行，如果任何子代理失败，你只会得到成功那些子代理的结果。
:::

### 内部子代理

内部子代理会生成 goose 实例，使用你当前会话的上下文和扩展来处理任务。有两种方式配置和执行内部子代理：

1. **直接提示词** —— 使用自然语言指令的快速、一次性任务
2. **Recipe** —— 用于专门子代理行为的可复用、结构化配置

#### 直接提示词
直接提示词是用自然语言提示词为一次性任务提供的。主 Agent 会根据你的请求自动配置子代理。

**goose 提示词：**
```
"Use 2 subagents to create hello.html with 'Hello World' content and goodbye.html with 'Goodbye World' content in parallel"
```

**工具输出：**
```json
{
  "execution_summary": {
    "total_tasks": 2,
    "successful_tasks": 2,
    "failed_tasks": 0,
    "execution_time_seconds": 16.2
  },
  "task_results": [
    {
      "task_id": "create_hello_html",
      "status": "success",
      "result": "Successfully created hello.html with Hello World content"
    },
    {
      "task_id": "create_goodbye_html", 
      "status": "success",
      "result": "Successfully created goodbye.html with Goodbye World content"
    }
  ]
}
```

#### Recipe
使用 [Recipe](https://block.github.io/goose/docs/guides/recipes/) 文件为子代理定义具体的指令、扩展和行为。Recipe 提供可复用的配置，可按名称共享和引用。

**创建 Recipe 文件**

`code-reviewer.yaml`

```yaml
id: code-reviewer
version: 1.0.0
title: "Code Review Assistant"
description: "Specialized subagent for code quality and security analysis"
instructions: |
  You are a code review assistant. Analyze code and provide feedback on:
  - Code quality and readability
  - Security vulnerabilities
  - Performance issues
  - Best practices adherence
activities:
  - Analyze code structure
  - Check for security issues
  - Review performance patterns
extensions:
  - type: builtin
    name: developer
    display_name: Developer
    timeout: 300
    bundled: true
parameters:
  - key: focus_area
    input_type: string
    requirement: optional
    description: "Specific area to focus on (security, performance, readability, etc.)"
    default: "general"
prompt: |
  Please review the following code focusing on {{focus_area}} aspects.
  Provide specific, actionable feedback with examples.
```

**把 Recipe 文件放在 goose 能找到的位置**
- 把 [`GOOSE_RECIPE_PATH`](https://block.github.io/goose/docs/guides/recipes/recipe-reference#recipe-location) 环境变量设置为你的 Recipe 目录
- 或者把它放在你当前的工作目录中

**goose 提示词**
```
Use the "code-reviewer" recipe to analyze the authentication feature I implemented
```

**goose 输出**
```
I'll use your code-reviewer recipe to create a specialized subagent for this analysis.

🤖 Subagent created using code-reviewer recipe
💭 Analyzing authentication function for security issues...
🔧 Scanning code structure and patterns...
⚠️  Security vulnerabilities detected!

## Code Review Results

### Critical Issues Found:
1. **SQL Injection Vulnerability**: Direct string interpolation in SQL query
2. **Missing Password Hashing**: Plain text password comparison

### Recommendations:
- Use parameterized queries or ORM
- Implement proper password hashing (bcrypt, scrypt)
- Add input validation and sanitization
```

### 外部子代理

外部子代理让你引入来自其他提供方和平台的 AI Agent，使 goose 能够与更广泛的生态协调并集成你的工作流。在下面的示例中，我们通过把 Codex 作为 MCP 服务器运行来把它用作子代理：

**[goose 配置文件](https://block.github.io/goose/docs/guides/config-files)**（`.~/.config/goose/config.yaml `）：
```yaml
subagent:
  args:
  - mcp-server
  bundled: true
  cmd: codex
  description: OpenAI Codex CLI Subagent
  enabled: true
  env_keys:
  - OPENAI_API_KEY
  envs: {}
  name: subagent
  timeout: 300
  type: stdio
```

**外部工具配置**（`~/.codex/config.toml`）：
```toml
# Use fast model for quick responses
# model = "codex-mini-latest"
disable_response_storage = true

# Never prompt for approval - auto-execute
approval_policy = "never"

[sandbox]
mode = "workspace-write"
```

**goose 提示词：**
```
"Use the codex subagent to analyze my codebase structure and identify the main components"
```

**goose 输出：**

```md
Based on my analysis of your codebase, here are the main components:

1. **Core Agent System** (`crates/goose/src/agents/`)
   - Agent orchestration and session management
   - Tool execution framework
   - Extension system integration

2. **CLI Interface** (`crates/goose-cli/`)
   - Command-line interface and session handling
   - Configuration management

3. **ACP Server** (`crates/goose/src/acp/`)
   - Agent Client Protocol endpoints
   - HTTP/WebSocket communication for real-time interaction

4. **Desktop UI** (`ui/desktop/`)
   - Electron-based desktop application
   - TypeScript frontend with React components

The architecture follows a modular design with clear separation between the core agent logic, interfaces, and UI components.
```

### 建议的用例

**独立操作**
- 创建多个结构相似的文件
- 基本的数据处理任务
- 文件转换与生成

**上下文保留**
- 会产生大量工具输出的复杂分析
- 更适合由专用 Agent 处理的专门任务
- 让主对话专注于高层决策

**进程隔离**
- 即使失败也不影响主工作流的任务
- 需要不同配置的操作
- 实验性或探索性工作

### 生命周期与清理

子代理是仅为执行任务而存在的临时实例。任务完成后，无需任何人工干预进行清理。

### 配置

子代理使用以下预配置的设置，但你可以在提示词中用自然语言覆盖任何默认值。

#### 默认设置
| 参数 | 默认值 | 如何自定义 |
|-----------|---------|------------------|
| **最大轮数** | 25 | 使用自然语言、设置 `GOOSE_SUBAGENT_MAX_TURNS`，或在 [Recipe](https://block.github.io/goose/docs/guides/recipes/recipe-reference#settings) 或子代理工具调用中配置 `settings.max_turns` |
| **超时** | 5 分钟 | 在提示词中请求更长的超时 |
| **扩展** | 继承自父级 | 在提示词中指定要使用哪些扩展 |
| **返回模式** | 所有子代理信息都在主会话中提供 | 在提示词中指定你想要的详细程度 |

:::tip 高级自定义
你还可以通过编辑 `subagent_system.md` [提示词模板](https://block.github.io/goose/docs/guides/context-engineering/prompt-templates)来自定义子代理行为。
:::

#### 在提示词中自定义设置

你可以通过在自然语言请求中包含该设置来覆盖任何默认值：

**示例：**
```
"Use subagents to analyze code, limit each to 5 turns"
```

```
"Use a research subagent with 30 turns and 20-minute timeout to investigate quantum computing trends"
```

**环境变量：** 设置 `GOOSE_SUBAGENT_MAX_TURNS` 可更改所有子代理的默认最大轮数。类似地，`GOOSE_SUBAGENT_MODEL` 和 `GOOSE_SUBAGENT_PROVIDER` 设置子代理模型和提供方的默认值；Recipe 的 [`settings`](https://block.github.io/goose/docs/guides/recipes/recipe-reference#settings) 优先于这两者。

#### 扩展控制

控制子代理可以访问哪些工具和能力。默认情况下，子代理会从你的主会话继承所有扩展，但出于安全、专注或性能考虑，你可以限制访问。

:::note Summon 扩展
`delegate` 和 `load` 工具由 `summon` 平台扩展提供，该扩展默认启用。如果你使用的 [Recipe](https://block.github.io/goose/docs/guides/recipes/) 带有显式的 `extensions` 块，你必须在该列表中包含 `summon`，否则 `delegate` 工具将不可用：

```yaml
extensions:
  - type: platform
    name: summon
  # ... your other extensions
```

定义了 [`sub_recipes`](https://block.github.io/goose/docs/guides/recipes/subrecipes) 的 Recipe 会自动注入 `summon`。
:::

**示例：**
```
"Create a subagent to write a summary, but don't give it file access"
```

```
"Use a subagent with only code editing tools to refactor main.py"
```

#### 返回模式控制
选择 goose 在主会话中从子代理提供多少信息。

**完整细节（默认）：** 查看所有工具执行和推理步骤
```
"Create a subagent to debug this issue - I want to see the full investigation process"
```

**仅摘要：** 只获取最终结果，让你的对话保持干净
```
"Use a subagent to research this topic and summarize the key findings"
```

### 安全约束

子代理在受限的工具访问下运行，以确保安全执行并防止干扰主会话。

#### 允许的操作

子代理可以访问以下安全操作：

- **扩展发现**：搜索可用扩展，以了解有哪些工具可用
- **资源访问**：从已启用的扩展读取并列出资源以获取上下文
- **扩展工具**：使用 Recipe 中指定的或从父会话继承的扩展所提供的工具

#### 受限的操作

以下操作被阻止，以确保子代理专注于其被指派的任务，而不影响更广泛的系统状态：

- **生成子代理**：不能创建额外的子代理，以防止无限递归
- **扩展管理**：不能启用、禁用或修改扩展，以避免与主会话冲突
- **调度管理**：不能创建、修改或删除被调度的任务，以防止干扰父工作流

:::info
子代理可以浏览扩展以获取建议，但不能启用它们，以避免修改父会话。
:::

### 附加资源

<ContentCardCarousel
  items={[
      {
      type: 'blog',
      title: 'Agents, Subagents, and Multi Agents: What They Are and When to Use Them',
      description: 'Compare agents, subagents, and multi agents in AI workflows. Learn how they work together and practical scenarios for each approach.',
      thumbnailUrl: agentCoordination,
      linkUrl: '/blog/2025/08/14/agent-coordination-patterns',
      date: '2025-08-14',
      duration: '4 min read'
    },
    {
      type: 'video',
      title: 'How I Built an App with 6 Subagents',
      description: 'Deep dive into goose subagents. Walk through building an app using 6 specialized AI agents for advanced workflow automation and development.',
      thumbnailUrl: 'https://img.youtube.com/vi/yIBrD5AxtTc/maxresdefault.jpg',
      linkUrl: 'https://www.youtube.com/watch?v=yIBrD5AxtTc',
      date: '2025-10-01',
      duration: '6:53'
    },
    {
      type: 'tutorial',
      title: 'Tutorial: Using Subagents',
      description: 'Spin up a team of subagents to build a fully functional app',
      thumbnailUrl: 'https://goose-docs.ai/assets/images/tutorial-using-subagents-ef265627024db73e73d80e5799ed0c1a.png',
      linkUrl: '/docs/tutorials/subagents',
      date: '2026-01-27',
      duration: '1 hour'
    },
    {
      type: 'video',
      title: 'Flight School - Choosing the Right Tools for AI Work',
      description: 'Discover the differences between subagents and subrecipes for efficient task execution in goose. Learn which approach is best for your workflow.',
      thumbnailUrl: 'https://img.youtube.com/vi/joePzlkARjs/maxresdefault.jpg',
      linkUrl: 'https://www.youtube.com/watch?v=joePzlkARjs',
      date: '2025-09-29',
      duration: '6:13'
    },
    {
      type: 'video',
      title: 'Flight School - Choosing the Right Tools for AI Work',
      description: 'Discover the differences between subagents and subrecipes for efficient task execution in goose. Learn which approach is best for your workflow.',
      thumbnailUrl: 'https://img.youtube.com/vi/joePzlkARjs/maxresdefault.jpg',
      linkUrl: 'https://www.youtube.com/watch?v=joePzlkARjs',
      date: '2025-09-29',
      duration: '6:13'
    },
    {
      type: 'blog',
      title: 'How to Choose Between Subagents and Subrecipes in goose',
      description: 'Detailed guide to subagents and subrecipes in goose. Compare reusability, setup complexity, and get practical advice for choosing the right approach.',
      thumbnailUrl: subagentsVsSubrecipes,
      linkUrl: '/blog/2025/09/26/subagents-vs-subrecipes',
      date: '2025-09-26',
      duration: '6 min read'
    }
  ]}
/>

---

## Hooks

> 原文：https://block.github.io/goose/docs/guides/context-engineering/hooks

Hook 让你在 goose 会话期间发生关键事件时运行你自己的脚本。用 Hook 记录活动、发送通知、在编辑后格式化文件、在 shell 命令后运行检查，或在不编写自定义扩展的情况下把 goose 集成到本地工作流中。

goose 遵循 [Open Plugins hooks 规范](https://open-plugins.com/agent-builders/components/hooks)。Hook 从磁盘上的[插件](https://block.github.io/goose/docs/guides/context-engineering/plugins)中发现，并在匹配的生命周期事件触发时作为 shell 命令运行。

:::warning 仅运行可信的 Hook
Hook 会在你的机器上执行本地命令。只安装或创建来自你信任来源的 Hook，并在启用前审查 Hook 脚本。
:::

### Hook 存放在哪里

一个 Hook 属于一个[插件](https://block.github.io/goose/docs/guides/context-engineering/plugins)目录。goose 从以下位置发现插件：

| 作用域 | 位置 |
|---|---|
| 用户 | `~/.agents/plugins/<plugin-name>/` |
| 项目 | `<project>/.agents/plugins/<plugin-name>/` |
| 已安装插件 | goose 的插件安装目录 |

每个定义了 Hook 的插件都必须包含一个 `hooks/hooks.json` 文件：

```text
my-plugin/
├── plugin.json
├── hooks/
│   └── hooks.json
└── scripts/
    └── notify.sh
```

项目插件在从该项目启动 goose 时加载。用户插件跨项目可用。

### 创建一个 Hook

要创建任何 Hook，请选择你想响应的事件，创建一个插件目录，添加一个把该事件映射到命令的 `hooks/hooks.json` 文件，然后编写应运行的脚本或命令。该命令通过 stdin 接收事件 payload 作为 JSON，因此它可以检查会话 ID、提示词文本、工具名称、文件路径或 shell 命令等细节。

一个 Hook 插件需要以下基本结构：

```text
session-logger/
├── plugin.json
├── hooks/
│   └── hooks.json
└── scripts/
    └── log-session.sh
```

插件清单标识该插件：

```json title="plugin.json"
{
  "name": "session-logger",
  "version": "0.1.0",
  "description": "Log goose session events"
}
```

Hook 配置把一个事件映射到一个命令。此示例在 `SessionEnd` 事件触发时运行一个脚本：

```json title="hooks/hooks.json"
{
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${PLUGIN_ROOT}/scripts/log-session.sh"
          }
        ]
      }
    ]
  }
}
```

该脚本从 stdin 读取事件 payload 并执行自动化：

```bash title="scripts/log-session.sh"
#!/usr/bin/env bash
payload="$(cat)"
session_id="$(printf '%s' "$payload" | jq -r .session_id)"
date_str="$(date '+%Y-%m-%d %H:%M')"

echo "- $date_str — session $session_id ended" >> ~/goose-session-log.md
```

把该插件放在一个可发现的插件位置，例如 `~/.agents/plugins/session-logger/`，并在你的操作系统要求时让命令脚本可执行。

### Hook 配置

`hooks.json` 有一个顶层 `hooks` 对象。每个键是一个事件名称，每个事件包含一条或多条规则：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "^(shell|edit)$",
        "hooks": [
          {
            "type": "command",
            "command": "${PLUGIN_ROOT}/scripts/log-tool.sh",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

| 字段 | 是否必填 | 描述 |
|---|---:|---|
| `matcher` | 否 | 用于决定该规则是否对该事件运行的正则表达式（不是 glob）。如果省略，该规则会针对该类型的每个事件运行。 |
| `hooks` | 是 | 当事件和 matcher 匹配时要运行的动作。 |
| `type` | 否 | 动作类型。goose 目前支持 `command`。如果省略，则使用 `command`。 |
| `command` | command Hook 必填 | 要运行的 shell 命令。goose 用 `sh -c` 运行它。 |
| `timeout` | 否 | 命令的超时时间（秒）。默认为 30 秒。 |
| `on_failure` | 否 | 当 `PreToolUse` Hook 失败时的处理方式：它无法被执行、超时、未收到其 payload、产生了 goose 无法解码的输出，或退出时没有 goose 能识别的决策。`allow`（默认值）继续执行工具调用，`block` 拒绝它。仅对选定的 `PreToolUse` command 动作解释，对其他所有事件忽略。参见[阻止工具调用](#blocking-a-tool-call)。 |

在命令中使用 `${PLUGIN_ROOT}` 来引用插件目录。goose 还会在 Hook 命令的环境中设置 `PLUGIN_ROOT`。

### 支持的事件

| 事件 | 何时运行 | Matcher 目标 |
|---|---|---|
| `SessionStart` | 会话开始 | 无 |
| `SessionEnd` | 会话结束 | 无 |
| `Stop` | goose 完成一轮或收到 stop 事件 | 无 |
| `UserPromptSubmit` | 用户提交提示词 | 提示词文本 |
| `PreToolUse` | 在 goose 运行工具之前 | 工具名称 |
| `PreToolUseResult` | 在 `PreToolUse` 链解析之后，对允许和拒绝的调用一视同仁，在工具运行或拒绝被返回之前。仅观察 | 工具名称 |
| `PostToolUse` | 在工具成功之后 | 工具名称 |
| `PostToolUseFailure` | 在工具失败之后 | 工具名称 |
| `BeforeReadFile` | 在 goose 读取文件之前 | 文件路径 |
| `AfterFileEdit` | 在 goose 成功编辑文件之后 | 文件路径 |
| `BeforeShellExecution` | 在 goose 运行 shell 命令之前 | shell 命令 |
| `AfterShellExecution` | 在 goose 成功运行 shell 命令之后 | shell 命令 |

matcher 是一个正则表达式，会针对该事件最相关的字符串进行匹配。例如，用 `"\\.rs$"` 在 `AfterFileEdit` 上匹配 Rust 文件，或用 `"^(cargo test|pnpm test)"` 在 `AfterShellExecution` 上匹配测试命令。匹配是非锚定的，所以 `"shell"` 也会匹配另一个扩展的 `"remote__shell_exec"`；当你需要精确匹配时，用 `^`/`$` 锚定。

:::warning 用 `.*` 而不是 `*` 来匹配一切
matcher 是正则表达式，不是 glob。一个裸的 `"*"` 是无效正则，所以整条规则会被**静默跳过**（goose 记录一条警告后继续）。要让一条规则对每个事件都运行，要么完全省略 `matcher`，要么使用 `".*"`。
:::

:::note
`AfterFileEdit` 和 `AfterShellExecution` 只在工具调用成功后才运行。要对失败的编辑、失败的 shell 命令或其他失败的工具调用做出反应，请使用 `PostToolUseFailure`。
:::

`PreToolUseResult` 在权威性上仅观察，但在投递上并非异步。匹配的 Hook 会被运行并等待，然后 goose 才继续执行工具或返回拒绝，因此一个慢速订阅者会把它自身的运行时间（最多到其超时）加到工具调用上。投递是尽力而为且不持久的：一个失败或不存在的订阅者不会改变决策，如果 Hook 未运行也不会保留任何记录。

### Hook Payload

当 Hook 运行时，goose 会把一个 JSON payload 写入该命令的 stdin。每个 payload 都包含事件名称和会话 ID。其余字段只在适用于该事件时才出现，因此 Hook 应把它们视为可选的。

| 字段 | 描述 |
|---|---|
| `event` | 触发的事件名称，例如 `PostToolUse` 或 `UserPromptSubmit`。 |
| `session_id` | 当前 goose 会话的 ID。 |
| `matcher_context` | 该规则的 `matcher` 所测试的字符串（例如工具事件上的工具名称，或 `UserPromptSubmit` 上的提示词文本）。 |
| `tool_name` | 工具名称，在工具事件上。 |
| `tool_input` | 传给该工具的输入参数，在工具事件上。 |
| `message` | 用户提交的提示词文本，在 `UserPromptSubmit` 上。 |
| `last_assistant_message` | 该轮的最终助手文本，在有助手输出时的 `Stop` 上。 |
| `working_dir` | 会话的工作目录，在工具事件上。 |
| `tool_call_id` | 一次工具调用的稳定标识符，在 `PreToolUse`、`PreToolUseResult`、`PostToolUse` 和 `PostToolUseFailure` 上。它关联单次调用的事件，而工具名加输入在同一个调用重复时无法做到这一点。 |
| `decision` | `allow` 或 `deny`，在 `PreToolUseResult` 上。没有第三个值。 |
| `policy_evaluated` | 当至少一个匹配的 `PreToolUse` Hook 以 0 退出或返回显式决策（退出码 `2`，或 stdout 上的 `{"decision":"block"}`）时为 `true`，在 `PreToolUseResult` 上。一个以非零退出但无决策、生成失败、超时，或其 payload 无法被序列化的 Hook 不计入，缺少匹配的 Hook 也不计入。它是一个「至少一个」的值，如果后续 Hook 失败仍保持 `true`。它报告的是某个 Hook 运行到了结论，而不是该结论可用：请读取 `cause` 了解这一点。 |
| `blocked_by` | 其 Hook 拒绝了该调用的插件，在 `decision` 为 `deny` 时的 `PreToolUseResult` 上。 |
| `reason` | 拒绝的消息，在 `decision` 为 `deny` 时的 `PreToolUseResult` 上。对于显式的策略拒绝，goose 从退出码 2 的 stderr 或 JSON 的 `reason` 字段推导出它。goose 不会限制或脱敏 Hook 提供的 reason，因此 Hook 不得包含机密。对于 `on_failure: block` 下的 Hook 失败，goose 提供一条有界的、由框架生成的消息，其中不包含命令字符串、插件路径或 payload 内容。 |
| `cause` | 链为何以该结果结束，在 `PreToolUseResult` 上。`policy_denial` 表示一个显式的策略决策阻止了该调用。`hook_failure` 表示至少一个 Hook 未能执行、未能收到其 payload、未能产生可解码输出，或未能应答决策协议，并且该失败决定或限定了所报告的结果。仅在无 Hook 失败的 allow 时缺失。 |

工具事件的示例 payload：

```json
{
  "event": "PostToolUse",
  "session_id": "abc-123",
  "matcher_context": "shell",
  "tool_name": "shell",
  "tool_input": { "command": "rg TODO" },
  "working_dir": "/Users/you/project"
}
```

提示词事件的示例 payload，其中提交的提示词在 `message` 中：

```json
{
  "event": "UserPromptSubmit",
  "session_id": "abc-123",
  "matcher_context": "summarize this file",
  "message": "summarize this file"
}
```

助手回复后 `Stop` 事件的示例 payload：

```json
{
  "event": "Stop",
  "session_id": "abc-123",
  "last_assistant_message": "Done. I updated the file and ran the tests."
}
```

读取 payload 的示例脚本：

```bash
#!/usr/bin/env bash
set -euo pipefail

payload="$(cat)"
event="$(printf '%s' "$payload" | jq -r .event)"
tool="$(printf '%s' "$payload" | jq -r '.tool_name // "none"')"

echo "goose hook: event=$event tool=$tool" >> "${PLUGIN_ROOT}/hook.log"
```

#### 工具输入键

`tool_name` 是 goose 发送给模型的名称，`tool_input` 保存该工具自身的参数。大多数扩展把它们的工具命名为 `{extension}__{tool}` 的形式，例如 `todo__todo_write`。`developer`、`analyze`、`summon` 和 `code_execution` 扩展不带该前缀暴露，因此它们的工具以其裸名称到达：shell 工具是 `shell`，而不是 `developer__shell`。这些键是该工具的 schema，因此它们因工具而异——一个检查文件路径的 Hook 必须读取它所匹配工具的对应字段。goose 内置 `developer` 工具的键如下：

| `tool_name` | `tool_input` 键 |
|---|---|
| `shell` | `command`、`timeout_secs`（可选） |
| `write` | `path`、`content` |
| `edit` | `path`、`before`、`after` |
| `tree` | `path`、`depth` |
| `read_image` | `source`、`crop`（可选） |

对于 shell 和文件工具，`matcher_context` 已经携带了 shell 命令（在 `BeforeShellExecution`/`AfterShellExecution` 上）或文件路径（在 `BeforeReadFile`/`AfterFileEdit` 上），因此那些 Hook 无需解析 `tool_input` 即可匹配。

### 阻止工具调用

大多数事件仅观察：goose 运行 Hook、记录结果，然后无论 Hook 返回什么都继续。有两个事件不同——**`PreToolUse` 和 `Stop` 可以阻止**。任何其他事件上的 Hook（包括 `UserPromptSubmit`、`PostToolUse` 以及 `Before*`/`After*` 事件）都不能阻止任何东西；来自那些事件的 block 决策会被忽略。

`PreToolUse` Hook 通过以下两种信号之一拒绝工具调用：

- **退出码 `2`** —— goose 阻止，并从 **stderr** 获取原因。
- **stdout 上的 `{"decision":"block","reason":"..."}`** —— goose 阻止，并从 `reason` 字段获取原因。只要退出码不是 `2`，goose 就会检查 stdout，因此无论该 Hook 是以 `0` 还是非零退出，该信号都会被认可。

对于 stdout 信号，stdout 必须以 `{` 开头，且 `decision` 必须恰好是 `"block"`。如果 `reason` 为空，goose 会代之以 `denied by plugin hook`。

当 `PreToolUse` Hook 阻止时，goose 不运行该工具，并向模型返回以下消息：

```text
Tool call denied by policy hook `<plugin>`: <reason>. Do not retry; this is a policy denial, not a transient failure.
```

一个阻止的 `Stop` Hook 会强制该轮继续而不是结束。为防止行为异常的 Hook 永远循环，goose 会限制连续 `Stop` 阻止的次数；一旦达到上限，goose 会覆盖该 Hook 并结束该轮。用 `GOOSE_STOP_HOOK_BLOCK_CAP` 环境变量提高上限。

#### stdout 是决策通道

对于阻止类事件，goose 按以下顺序从 Hook 的退出状态和 stdout 中读取决策：

1. 退出码 `2` 拒绝，原因来自 stderr。
2. stdout 上的 `{"decision":"block"}` 拒绝，无论退出状态是什么。
3. 退出码 `0` 且 stdout 为空则允许。
4. 退出码 `0` 且 stdout 上有 `{"decision":"allow"}` 则允许。
5. 其他任何情况都意味着该 Hook 没有返回决策。

规则 5 涵盖的不只是崩溃。stdout 上一行杂散的日志、被截断或格式错误的 JSON、一个 JSON 数组、没有 `decision` 的 `{}`、无法识别的 `decision` 值、与非零退出同时打印的 allow JSON、意外的退出状态，以及被信号终止，都会被读作无决策，生成错误和超时也是如此。把日志和诊断信息写到 stderr，把 stdout 留给决策。

另外两种情况也会被读作无决策：

- **stdout 不是有效的 UTF-8。** goose 严格读取 stdout，不会修复无效字节，因为修复它们可能把格式错误的输出变成能解析为 allow 的 JSON。stderr 则被宽松解码，因为它只会展示给人看。
- **goose 无法投递请求。** 如果 payload 无法被写入 Hook 的 stdin，那么该 Hook 是在没看到请求的情况下做出决策的，因此来自它的 allow 不计入。显式的拒绝仍然计入：goose 在做出决策之前读取该 Hook 的输出，而它成功打印的 block 会被认可。

由于 block 信号是独立于退出码被读取的，一个打印了 `{"decision":"block"}` 然后才以非零退出的 Hook 仍会阻止。不要依赖非零退出码来取消你已经打印的 block。

#### 选择 Hook 失败时会发生什么

一个 Hook 只有在 goose 投递了 payload，且进程以 0 退出并带空 stdout 或有效 allow 决策时，才算干净地允许。投递失败、goose 无法使用的输出，或没有拒绝的非零退出，都属于 Hook 失败，而非 allow。

**默认情况下，Hook 失败会被记录，工具调用继续。** 这是历史行为，也保持为默认，因此一个损坏的 Hook 永远不会卡住会话。

对于你确实依赖的策略，在该动作上把 `on_failure` 设为 `block`。这样当该 Hook 失败时，goose 会拒绝工具调用：

```json title="hooks/hooks.json"
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "^shell$",
        "hooks": [
          {
            "type": "command",
            "command": "${PLUGIN_ROOT}/scripts/block-sudo.sh",
            "on_failure": "block"
          }
        ]
      }
    ]
  }
}
```

由失败导致的拒绝，其措辞与策略拒绝不同，因此模型和你的日志可以区分它们：

```text
Tool call blocked because policy hook `<plugin>` could not complete: <reason>. That hook is configured to block on failure.
```

有三个限制值得了解：

- `on_failure` 仅适用于 `PreToolUse`。`Stop` Hook 即使设置了 `on_failure: block` 也保持 fail-open，因此一个损坏的 Hook 永远无法阻止一个已完成的轮结束。
- `on_failure` 永远不会覆盖显式拒绝。显式阻止的 Hook 在任一模式下都被认可。它也不会改变干净的 allow 的任何东西，即 payload 已投递且进程以 0 退出并带空 stdout 或有效 allow 决策的那种 allow。
- 在选定的 `PreToolUse` command 动作上，任何除 `allow` 或 `block` 以外的值都是配置错误，goose 会带着一条警告跳过该插件的整个 `hooks.json` 文件，而不是猜测一个策略。其他事件不解释该字段。`on_failure` 规定的是 Hook 运行并失败时会发生什么，而不是配置加载错误如何处理。

#### goose 在 `hooks.json` 中校验什么

未知事件名称和不支持的字符串动作类型会被忽略，其 payload 不会被解释，因此一个插件可以为更新的 goose 携带配置而不会在当前版本上出错。被识别的事件 schema 和选定的可运行 command 动作会被校验。格式错误的选定配置会带着一条警告跳过该插件的 `hooks.json`，而无效的 matcher 正则会警告并只跳过该条规则。`on_failure` 规定的是 Hook 在运行时失败时会发生什么；它不会让配置加载或 matcher 错误 fail closed。

`PreToolUseResult` 事件通过 `cause` 报告结果：显式 block 为 `policy_denial`，执行或协议失败为 `hook_failure`，干净的 allow 则没有 `cause`。

#### `PreToolUseResult` 报告什么

`PreToolUseResult` 携带 `PreToolUse` 链的结果。它的字段在 [Hook Payload](#hook-payload) 中定义了一次；本节只涵盖 `on_failure` 改变了什么。

`decision` 是实际应用于该工具调用的结果，因此在 `on_failure: block` 下，Hook 失败会显示为 `deny`。`cause` 是订阅者区分两种拒绝的方式：`policy_denial` 表示某个 Hook 显式阻止，`hook_failure` 表示某个 Hook 无法被执行、未收到其 payload、产生了 goose 无法解码的输出，或未应答决策协议所识别的任何内容。

`policy_evaluated` 回答的是与 `cause` 不同的问题，两者独立变动。一个以 0 退出同时打印一行杂散日志的 Hook 已运行到结论，因此 `policy_evaluated` 为 `true`，但它没有产生可用的决策，因此 `cause` 为 `hook_failure`。一个生成失败的 Hook 根本没运行过，因此 `policy_evaluated` 保持 `false`。

在混合链中，两种解读都会保留。如果较早的 Hook 干净地允许而较晚的一个失败，该事件会报告来自较早 Hook 的 `policy_evaluated: true` 和来自较晚 Hook 的 `cause: hook_failure`，无论该调用最终是被允许还是被拒绝。

一个在 `on_failure` 为 `allow` 时失败的 Hook 仍会发出带 `cause: "hook_failure"` 的 `decision: "allow"`，因此一个监控插件即使看到工具调用继续进行，也能看出某个 Hook 被跳过了。

#### 阻止危险命令

这个 `PreToolUse` Hook 会阻止任何使用 `sudo` 的 shell 命令：

```json title="hooks/hooks.json"
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "^shell$",
        "hooks": [
          {
            "type": "command",
            "command": "${PLUGIN_ROOT}/scripts/block-sudo.sh"
          }
        ]
      }
    ]
  }
}
```

```bash title="scripts/block-sudo.sh"
#!/usr/bin/env bash
set -euo pipefail

payload="$(cat)"
command="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty')"

if printf '%s' "$command" | grep -qE '(^|[[:space:]])sudo([[:space:]]|$)'; then
  printf '{"decision":"block","reason":"sudo is not allowed in this session"}'
fi
```

当命令被允许时，该 Hook 什么都不打印，因此 goose 正常运行它。

### 示例

#### 在工具失败时通知

```json
{
  "hooks": {
    "PostToolUseFailure": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${PLUGIN_ROOT}/scripts/notify.sh"
          }
        ]
      }
    ]
  }
}
```

```bash title="scripts/notify.sh"
#!/usr/bin/env bash
payload="$(cat)"
tool="$(printf '%s' "$payload" | jq -r '.tool_name // "tool"')"

osascript -e "display notification \"$tool failed\" with title \"goose\""
```

#### 在 goose 编辑文件后格式化它们

```json
{
  "hooks": {
    "AfterFileEdit": [
      {
        "matcher": "\\.(ts|tsx|js|jsx|json|md)$",
        "hooks": [
          {
            "type": "command",
            "command": "${PLUGIN_ROOT}/scripts/prettier.sh"
          }
        ]
      },
      {
        "matcher": "\\.rs$",
        "hooks": [
          {
            "type": "command",
            "command": "cargo fmt"
          }
        ]
      }
    ]
  }
}
```

```bash title="scripts/prettier.sh"
#!/usr/bin/env bash
set -euo pipefail

payload="$(cat)"
file="$(printf '%s' "$payload" | jq -r '.matcher_context // empty')"

if [ -n "$file" ]; then
  npx prettier --write "$file"
fi
```

#### 对长时间运行的命令做出反应

```json
{
  "hooks": {
    "AfterShellExecution": [
      {
        "matcher": "^(cargo (test|build|clippy)|pnpm (test|build)|just )",
        "hooks": [
          {
            "type": "command",
            "command": "say 'goose finished running your command'"
          }
        ]
      }
    ]
  }
}
```

### 试用示例插件

goose 在 `examples/plugins/hello-hooks` 提供了一个示例插件。

```bash
mkdir -p ~/.agents/plugins
cp -R examples/plugins/hello-hooks ~/.agents/plugins/hello-hooks
chmod +x ~/.agents/plugins/hello-hooks/scripts/announce.sh

goose session
```

该示例把 Hook 事件打印到 stderr，并把完整 payload 追加到：

```text
~/.agents/plugins/hello-hooks/last-event.log
```

### 禁用 Hook 插件

要禁用某个插件，请把它的名称加入 goose 设置文件中的 `disabledPlugins`：

```json title="~/.config/goose/settings.json"
{
  "disabledPlugins": ["session-logger"]
}
```

对于项目专属设置，请使用：

```text
<project>/.config/goose/settings.json
```

列在 `disabledPlugins` 中的插件会在插件发现期间被跳过，因此它的 Hook 不会运行。

### 疑难排查

#### 我的 Hook 没有运行

检查以下各项：

- 插件目录位于 `~/.agents/plugins/<name>/` 或 `<project>/.agents/plugins/<name>/` 之下。
- Hook 配置位于插件目录内的 `hooks/hooks.json`。
- 事件名称匹配[支持的事件](#supported-events)之一。
- `matcher` 正则表达式匹配该事件的 matcher 目标。
- 命令路径正确。对于插件内的脚本，使用 `${PLUGIN_ROOT}`。
- 如果你直接调用脚本，该脚本是可执行的。
- 该插件未列在 `disabledPlugins` 中。
- 该事件不是子代理生命周期事件。`SubagentStart` 和 `SubagentStop` 目前不会由 goose 发出，因此为它们注册的 Hook 永远不会运行。

#### 我的 Hook 超时或失败了

Hook 失败会被记录，但不会使 goose 或触发该 Hook 的工具崩溃。默认情况下，一个无法运行、超出其超时、从未收到其 payload，或退出时没有 goose 能识别决策的 Hook 会被记录，而工具调用继续进行。要有意停止工具调用，`PreToolUse` Hook 必须发出干净的 block 信号，而不仅仅是非零退出。

有两种情况看起来像失败，但并不是人们所预期的：

- **该 Hook 向 stdout 打印了一行日志。** goose 把 stdout 读作决策通道，因此 `echo "checking policy"` 会让一个本来健康的 Hook 被读作无决策。请改为把诊断信息发送到 stderr。
- **该 Hook 打印了 `{"decision":"allow"}` 然后以非零退出。** 退出状态与决策相矛盾，因此 goose 把它视为无决策。要在 allow 的同时以 `0` 退出。

如果你宁愿让失败的 Hook 停止工具调用而不是被忽略，就在该动作上把 `on_failure` 设为 `block`。参见[选择 Hook 失败时会发生什么](#choose-what-happens-when-a-hook-fails)。

为长时间运行的 Hook 设置更长的超时：

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${PLUGIN_ROOT}/scripts/archive.sh",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

#### 我的脚本找不到 `jq` 或其他命令

Hook 作为本地 shell 命令运行。确保你的脚本使用的任何命令都已安装，并可在你的 shell `PATH` 上使用。为可移植性考虑，对可能并非到处都安装的工具，优先使用绝对路径。

### 附加资源

<ContentCardCarousel
  items={[
    {
      type: 'blog',
      title: 'Hooks: run your own scripts on every goose event',
      description: 'Learn how lifecycle hooks let you react to session, prompt, tool, file, and shell events with your own scripts.',
      thumbnailUrl: hooksBanner,
      linkUrl: '/blog/2026/05/14/goose-hooks',
      date: '2026-05-14',
      duration: '5 min read'
    }
  ]}
/>

---

## 插件

> 原文：https://block.github.io/goose/docs/guides/context-engineering/plugins

插件是用于以可复用组件扩展 goose 的包。一个插件可以提供 [Skill](https://block.github.io/goose/docs/guides/context-engineering/using-skills)、[Hook](https://block.github.io/goose/docs/guides/context-engineering/hooks)，或两者兼有。

当你希望安装、共享或更新一组 goose 功能，而不是把单个文件复制到本地的 skills 或 hooks 目录中时，就使用插件。

:::warning 仅安装可信的插件
插件可以包含 goose 可能加载的指令，以及执行本地命令的 Hook。只从你信任的来源安装插件，并在启用前审查插件内容。
:::

### 插件能提供什么

| 组件 | 作用 |
|---|---|
| Skill | 可复用的指令和支持文件，教 goose 如何执行任务或遵循某个工作流。 |
| Hook | 在 goose 会话期间发生生命周期事件时运行的本地命令。 |

插件是容器。Skill 和 Hook 是该容器内部的组件。

### 插件结构

插件是一个带有插件清单和可选组件目录的目录。一个同时包含 Skill 和 Hook 的插件可以长这样：

```text
my-plugin/
├── plugin.json
├── skills/
│   └── review/
│       └── SKILL.md
├── hooks/
│   └── hooks.json
└── scripts/
    └── notify.sh
```

插件清单标识该插件：

```json title="plugin.json"
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Reusable skills and hooks for my team"
}
```

#### 向插件添加 Skill

要向插件添加一个 Skill，请把一个 Skill 目录放在该插件的 `skills/` 目录下。每个 Skill 目录包含一个 `SKILL.md` 文件：

```text
my-plugin/
└── skills/
    └── review/
        └── SKILL.md
```

```markdown title="skills/review/SKILL.md"
---
name: review
description: Review code changes for correctness, maintainability, and test coverage
---

Review the code changes. Prioritize correctness issues, security concerns, missing tests, and maintainability risks. Be direct and suggest concrete fixes.
```

对于 Open Plugins，goose 会把导入的 Skill 名称以插件名作为命名空间。`my-plugin` 中的 `review` Skill 会以 `my-plugin:review` 加载。

#### 向插件添加 Hook

要向插件添加一个 Hook，请创建 `hooks/hooks.json` 并把生命周期事件映射到命令：

```text
my-plugin/
├── hooks/
│   └── hooks.json
└── scripts/
    └── notify.sh
```

```json title="hooks/hooks.json"
{
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${PLUGIN_ROOT}/scripts/notify.sh"
          }
        ]
      }
    ]
  }
}
```

Hook 命令通过 stdin 接收事件 payload 作为 JSON。使用 `${PLUGIN_ROOT}` 来引用插件目录内的文件。

关于支持的事件、payload 细节和更多 Hook 示例，参见 [Hook 指南](https://block.github.io/goose/docs/guides/context-engineering/hooks)。

### 插件位置

goose 从以下位置发现插件：

| 插件类型 | 位置 | 备注 |
|---|---|---|
| 用户插件 | `~/.agents/plugins/<plugin-name>/` | 包括用 `goose plugin install` 安装的插件，以及手动复制到你的用户插件目录中的插件。 |
| 项目插件 | `<project>/.agents/plugins/<plugin-name>/` | 在 goose 于该项目中工作时可用。 |

已安装和手动放置的用户插件使用同一个用户插件目录。已安装插件包含由 `goose plugin install` 创建的元数据；只有已安装的 git 支持的插件可以用 `goose plugin update` 更新。

### 安装插件

用以下命令从 git 仓库安装插件：

```bash
goose plugin install https://github.com/example/my-goose-plugin.git
```

安装命令会克隆该仓库、检测插件格式、把它复制到插件目录，并报告导入的组件。

示例输出：

```text
✓ Installed open-plugins plugin 'my-plugin' (1.0.0)
  Source: https://github.com/example/my-goose-plugin.git
  Location: /Users/you/.agents/plugins/my-plugin
  Imported skills:
    - my-plugin:review
    - my-plugin:test-plan
```

### 自动更新插件

要让 goose 自动检查插件更新，请用 `--auto-update` 安装它：

```bash
goose plugin install --auto-update https://github.com/example/my-goose-plugin.git
```

当启用自动更新时，goose 会在加载插件 Skill 之前检查该插件是否有更新。自动更新检查有速率限制，因此 goose 不会在每次会话开始时都克隆该仓库。

如果自动更新失败，goose 会记录该失败并继续使用当前已安装的插件。

:::note
自动更新适用于用 `goose plugin install --auto-update` 安装的 git 支持的插件。手动复制到 `.agents/plugins/` 的插件会被发现，但它们不受插件更新命令管理。
:::

### 手动更新插件

要按需更新一个 git 支持的插件，请运行：

```bash
goose plugin update <plugin-name>
```

例如：

```bash
goose plugin update my-plugin
```

更新命令会从其原始 git 来源获取该插件、替换已安装的副本，并保留该插件是否启用了自动更新。

### 禁用插件

要全局禁用一个插件，请把它的名称加入你的用户 goose 设置文件中的 `disabledPlugins`：

```json title="~/.config/goose/settings.json"
{
  "disabledPlugins": ["my-plugin"]
}
```

对于项目专属设置，请使用：

```text
<project>/.config/goose/settings.json
```

对于不应与队友共享的本地专属项目设置，请使用：

```text
<project>/.config/goose/settings.local.json
```

被禁用的插件会在插件发现期间被跳过，因此它的 Skill 不会被加载，它的 Hook 也不会运行。

### 插件格式

goose 支持以下插件格式：

| 格式 | 常见文件 | 备注 |
|---|---|---|
| Open Plugins | `plugin.json`、`.plugin/plugin.json`、`.goose-plugin/plugin.json`、`skills/`、`hooks/hooks.json` | 支持 Open Plugins 的 Skill 和 Hook。 |
| Gemini 扩展 | `gemini-extension.json`、`skills/` | 支持来自 Gemini 风格扩展仓库的 Skill。 |

对于 Open Plugins，导入的 Skill 名称会以插件名作为命名空间，例如 `my-plugin:review`。在显式加载插件提供的 Skill 时，请使用该完整名称。Gemini 扩展的 Skill 保留 `SKILL.md` 中的 Skill 名称；goose 不会给它们加上扩展名前缀。

Open Plugins 可以使用插件根目录的 `plugin.json`、`.plugin/plugin.json` 或 `.goose-plugin/plugin.json`。仅有 Hook 的 Open Plugins 可以从 `hooks/hooks.json` 发现；如果没有清单，goose 会从来源或目录名推断插件名。

### 何时使用插件、Skill 还是 Hook

| 用途 | 最佳选择 |
|---|---|
| 打包并分发可复用的 goose 组件 | 插件 |
| 教 goose 一个可复用的流程或领域专属工作流 | Skill |
| 在 goose 会话事件发生时运行一个本地命令 | Hook |

插件用于打包和分发。Skill 和 Hook 定义插件被安装或发现后 goose 可以使用什么行为。

---

## 自定义斜杠命令

> 原文：https://block.github.io/goose/docs/guides/context-engineering/slash-commands

自定义斜杠命令是用于运行 [Recipe](https://block.github.io/goose/docs/guides/recipes) 的个性化快捷方式。如果你有一个运行每日报告的 Recipe，就可以创建一个自定义斜杠命令来从会话内调用该 Recipe：

```
/daily-report
```


### 创建斜杠命令

把一个自定义命令指派给一个 Recipe。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
   1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏
   2. 在侧边栏中点击 `Recipes`
   3. 找到你想使用的 Recipe，然后点击 <Terminal className="inline" size={16} /> 按钮
   4. 在弹出窗口中，输入你的自定义命令（不含开头的 `/`）
   5. 点击 `Save`
 
  该命令会出现在你 `Recipes` 菜单中该 Recipe 的下方。对于不在你 Recipe 库中的 Recipe，请按 `goose CLI` 步骤操作。

  </TabItem>
  <TabItem value="cli" label="goose CLI">

  在你的[配置文件](https://block.github.io/goose/docs/guides/config-files)中配置斜杠命令。列出命令（不含开头的 `/`）以及你电脑上 Recipe 文件的路径：

```yaml title="~/.config/goose/config.yaml"
slash_commands:
  - command: "run-tests"
    recipe_path: "/path/to/recipe.yaml"
  - command: "daily-report"
    recipe_path: "/Users/me/.local/share/goose/recipes/report.yaml"
```

   </TabItem>
</Tabs>

### 使用斜杠命令

在任何聊天会话中，在消息开头输入带前导斜杠的自定义命令：

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

```
/run-tests
```

:::tip 可用命令
在 goose Desktop 中输入 `/` 会弹出一个菜单，显示可用的斜杠命令。
:::

  </TabItem>
  <TabItem value="cli" label="goose CLI">

```sh
Context: ●○○○○○○○○○ 5% (9695/200000 tokens)
( O)> /run-tests
```

  </TabItem>
</Tabs>

你可以在命令后传递一个参数（如需要）。引号是可选的：

```
/translator where is the library
```

当你用斜杠命令运行一个 Recipe 时，该 Recipe 的 instructions 和 prompt 字段会被发送到你的模型并加载到对话中，但不会显示在聊天中。模型会使用该 Recipe 的上下文和指令来回应，就像你直接打开它一样。

### 限制

- 斜杠命令只接受一个[参数](https://block.github.io/goose/docs/guides/recipes/recipe-reference#parameters)。Recipe 中任何额外的参数都必须有默认值。
- 命令名不区分大小写（`/Bug` 和 `/bug` 被视为同一命令）。
- 命令名必须唯一且不含空格。
- 你不能使用与[内置 CLI 斜杠命令](https://block.github.io/goose/docs/guides/goose-cli-commands#slash-commands)冲突的名称，如 `/compact` 或 `/help`。
- 如果 Recipe 文件缺失或无效，该命令会被当作发送给模型的常规文本处理。

### 附加资源

<ContentCardCarousel
  items={[
    {
      type: 'topic',
      title: 'Recipes',
      description: 'Check out the Recipes guide for more docs, tools, and resources to help you master goose recipes.',
      linkUrl: '/docs/guides/recipes'
    },
    {
      type: 'topic',
      title: 'Research → Plan → Implement Patterns',
      description: 'See how slash commands make it easy to integrate instructions into interactive RPI workflows.',
      linkUrl: '/docs/tutorials/rpi'
    }
  ]}
/>
