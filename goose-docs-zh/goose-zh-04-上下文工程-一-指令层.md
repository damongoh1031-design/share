# goose 官方文档中文手册：第 04 章　上下文工程（一）：指令层

## 上下文工程

> 原文：https://block.github.io/goose/docs/guides/context-engineering

<h1 className={styles.pageTitle}>上下文工程</h1>
<p className={styles.pageDescription}>
  上下文工程（Context engineering）关注的是构建背景知识、偏好与工作流，帮助 goose 更高效地工作。你不必反复重复指令，只需定义一次，就能教会 goose 你习惯的工作方式。
</p>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>📚 文档与指南</h2>
  <div className={styles.cardGrid}>
    <Card 
      title="使用 goosehints"
      description="使用 AGENTS.md、.goosehints 以及其他文件，提供 goose 会自动加载的项目上下文、偏好与指令。"
      link="/docs/guides/context-engineering/using-goosehints"
    />
    <Card 
      title="使用 Skill"
      description="创建可复用的指令集，其中包含工作流、脚本及其他资源，goose 可按需加载。"
      link="/docs/guides/context-engineering/using-skills"
    />
    <Card
      title="自定义 Agent"
      description="创建、编辑、导入和导出专用的 goose Agent，附带可复用的提示词以及可选元数据。"
      link="/docs/guides/context-engineering/custom-agents"
    />
    <Card 
      title="插件"
      description="安装、更新和管理扩展包，用 Skill、Hook 及其他可复用组件来扩展 goose。"
      link="/docs/guides/context-engineering/plugins"
    />
    <Card 
      title="Hook"
      description="在 goose 启动会话、提交提示词、调用工具、编辑文件或执行 shell 命令时运行脚本。"
      link="/docs/guides/context-engineering/hooks"
    />
    <Card 
      title="自定义斜杠命令"
      description="创建自定义快捷方式，用简单的斜杠命令在任意聊天会话中快速运行可复用指令。"
      link="/docs/guides/context-engineering/slash-commands"
    />
    <Card 
      title="提示词模板"
      description="自定义内置提示词，它们定义了 goose 如何响应、规划、压缩上下文以及创建 Recipe。"
      link="/docs/guides/context-engineering/prompt-templates"
    />
    <Card 
      title="子代理"
      description="把聚焦的任务委派给隔离的 goose 实例，这些实例可以顺序运行或并行运行。"
      link="/docs/guides/context-engineering/subagents"
    />
    <Card 
      title="持久指令"
      description="在每一轮向 goose 的工作记忆注入关键提醒。非常适合绝不能遗忘的安全护栏与行为规则。"
      link="/docs/guides/context-engineering/using-persistent-instructions"
    />
    <Card 
      title="Memory 扩展"
      description="教会 goose 可在跨会话中回忆的持久知识。保存命令、代码片段与偏好，以获得一致的协助。"
      link="/docs/mcp/memory-mcp"
    />
    <Card 
      title="研究 → 规划 → 实现模式"
      description="了解斜杠命令如何让你轻松把指令集成到交互式 RPI 工作流中。"
      link="/docs/tutorials/rpi"
    />
  </div>
</div>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>📝 精选博客文章</h2>
  <div className={styles.cardGrid}>
    <Card 
      title="我的 .goosehints 文件里有什么"
      description="深入探讨 .goosehints 与 Memory 扩展的对比，以及如何优化你的 goose 配置以获得更好的性能。"
      link="/blog/2025/06/05/whats-in-my-goosehints-file"
    />
    <Card 
      title="阻止你的 AI Agent 做出不想要的更改"
      description="教会你的 AI Agent 如何尽早、频繁地提交，这样你就能控制更改并安全回滚。"
      link="/blog/2025/12/10/stop-ai-agent-unwanted-changes"
    />
    <Card 
      title="AI 怀疑论者的上下文窗口指南"
      description="AI Agent 为什么会遗忘？了解上下文窗口、token 以及 goose 如何帮助你管理记忆与长对话。"
      link="/blog/2025/08/18/understanding-context-windows"
    />
    <Card
      title="Hook：在每一个 goose 事件上运行你自己的脚本"
      description="了解生命周期 Hook 如何让你用自己的脚本响应会话、提示词、工具、文件与 shell 事件。"
      link="/blog/2026/05/14/goose-hooks"
    />
  </div>
</div>

---

## 向 goose 提供提示

> 原文：https://block.github.io/goose/docs/guides/context-engineering/using-goosehints

`.goosehints` 是一个文本文件，用于提供关于你的项目的额外上下文，并改善与 goose 的沟通。使用 `.goosehints` 可以确保 goose 更好地理解你的需求，从而更高效地执行任务。

<details>
  <summary>goose 提示视频演示</summary>
  <iframe
  class="aspect-ratio"
  src="https://www.youtube.com/embed/kWXJC5p0608"
  title="goose Hints"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
  ></iframe>
</details>

当你发现自己反复输入提示词，或多次提供同类指令时，就是考虑添加 `.goosehints` 文件的好时机。它也是提供大量上下文的绝佳方式，这些上下文放在文件里可能更合适。

本指南将带你一步步创建并使用 `.goosehints` 文件，用自定义指令与上下文来简化你的工作流。

:::info 需要 Developer 扩展
要使用提示文件，你需要[启用](https://block.github.io/goose/docs/getting-started/using-extensions) `Developer` 扩展。
:::

### 创建你的提示文件

goose 支持两种类型的提示文件：
- **全局提示文件** - 这些提示会应用于你与 goose 的所有会话，无论当前目录是什么。全局提示存储在 `~/.config/goose/.goosehints`。
- **本地提示文件** - 这些提示仅在特定目录或目录层级中工作时才会生效。

你可以同时使用全局提示与本地提示。当两者都存在时，goose 会同时考虑你的全局偏好与项目特定需求。如果本地提示文件中的指令与你的全局偏好冲突，goose 会优先采用本地提示。

:::tip 自定义上下文文件
你可以通过 [`CONTEXT_FILE_NAMES` 环境变量](#custom-context-files)在 goose 中使用其他 Agent 规则文件。
:::

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>

    ##### 全局提示文件
    1. 在 `~/.config/goose` 中创建 `.goosehints` 文件

    ##### 本地提示文件

    1. 点击应用底部的目录路径，打开你想在其中创建文件的目录
    2. 点击左上角的汉堡菜单按钮 <Menu className="inline" size={16} /> 打开侧边栏
    3. 在侧边栏中点击 `Settings`
    4. 点击 `Chat`
    5. 向下滚动到 `Project Hints (.goosehints)` 区域，点击 `Configure`
    6. 在文本区域输入你的本地提示
    7. 点击 `Save`
    8. 重启会话，让 goose 读取更新后的 `.goosehints`

    如果给定目录中已存在 `.goosehints` 文件，你可以编辑已有的提示。

    </TabItem>
    <TabItem value="manual" label="手动">
    
    - **全局提示文件** - 在 `~/.config/goose` 中创建 `.goosehints` 文件。
    - **本地提示文件** - 在项目根目录和/或层级中的任意目录创建 `.goosehints` 文件。

    </TabItem>
</Tabs>

`.goosehints` 文件可以包含与你的项目相关的任何指令或上下文细节。

### 设置提示

`.goosehints` 文件支持自然语言。使用 goose 容易理解并遵循的直接语言，编写清晰、具体的指令。包含关于你的项目与工作流偏好的相关上下文，并把最重要的准则放在前面。

goose 会在会话开始时加载提示。当它访问嵌套目录中的文件时，也会加载这些目录的提示文件。goose 会把提示加入每个请求的系统提示词中。由于 `.goosehints` 内容会消耗 token，保持简洁可以降低成本并提升性能。

#### 全局 `.goosehints` 文件示例

```
Always use TypeScript for new Next.js projects.

@coding-standards.md  # Contains our coding standards
docs/contributing.md  # Contains our pull request process

Follow the [Google Style Guide](https://google.github.io/styleguide/pyguide.html) for Python code.

Run unit tests before committing any changes.

Prefer functional programming patterns where applicable.
```

#### 本地 `.goosehints` 文件示例

```
This is a simple example JavaScript web application that uses the Express.js framework. View [Express documentation](https://expressjs.com/) for extended guidance.

Go through the @README.md for information on how to build and test it as needed.

Make sure to confirm all changes with me before applying.

Run tests with `npm run test` ideally after each change.
```

这些示例展示了引用其他文件的两种方式：
- **`@` 语法**：自动把文件内容包含进 goose 的即时上下文
- **普通引用**：把 goose 指向需要时再查看的文件（适用于可选或非常大的文件）

#### 嵌套的 `.goosehints` 文件

goose 在 git 仓库中支持分层的本地提示。会话开始时，goose 会从你的工作目录一直向上加载到仓库根目录的已配置上下文文件。当 goose 读取或修改嵌套子目录中的文件时，它还能自动发现并加载这些目录中的额外提示文件。

这在 monorepo 或代码库不同部分有不同约定的大型项目中尤其有用。

默认情况下，goose 会在每一层查找 `AGENTS.md` 与 `.goosehints`。如果你在使用[自定义上下文文件](#custom-context-files)，goose 也会对这些文件名应用相同的嵌套加载行为。

作为最佳实践，每一层的 `.goosehints` 只应包含与该范围相关的提示：
- **根层级**：包含项目级标准、构建流程与通用准则
- **模块/功能层级**：添加该代码库区域的特定要求
- **目录层级**：包含非常具体的上下文，如本地测试流程或组件模式

**示例项目结构：**
```sh
my-project/
├── .git/
├── .goosehints              # Project-wide hints
├── frontend/
│   ├── .goosehints          # Frontend-specific hints
│   └── components/
│       ├── .goosehints      # Component-specific hints
│       └── Button.tsx
└── backend/
    ├── .goosehints          # Backend-specific hints
    └── api/
        └── routes.py
```

如果你在 `my-project/` 中启动 goose，根层级提示会立即加载。之后，当 goose 访问 `frontend/components/` 下的文件时，它会加载该路径的嵌套提示，并按以下顺序合并：
1. <details>
     <summary>`my-project/.goosehints` (项目根目录)</summary>

```
This is a React + TypeScript project using Vite.

@README.md                    # Project overview and setup instructions
@docs/development-setup.md    # Development environment configuration

Always run tests before committing: `npm test`
Use conventional commits for all changes.
```

   </details>
2. <details>
     <summary>`frontend/.goosehints`</summary>

```
This frontend uses React 18 with TypeScript and Tailwind CSS.

@package.json                      # Dependencies and scripts
@docs/frontend-architecture.md     # Frontend structure and patterns

## Development Standards
- Use functional components with hooks (no class components)
- Implement proper TypeScript interfaces for all props
- Follow the component structure: /components/ComponentName/index.tsx
- Use Tailwind classes instead of custom CSS when possible

## Testing Requirements  
- Write unit tests for all components using React Testing Library
- Test files should be co-located: ComponentName.test.tsx
- Run `npm run test:frontend` before committing changes

## State Management
- Use React Query for server state
- Use Zustand for client state management
- Avoid prop drilling - lift state appropriately

Always confirm UI changes with design team before implementation.
```

   </details>
3. <details>
     <summary>`frontend/components/.goosehints` (当前目录)</summary>

```
Components in this directory use our design system.

@docs/component-api.md    # Component interface standards and examples

All components must:
- Export a default component
- Include TypeScript props interface
- Have corresponding .test.tsx file
- Follow naming convention: PascalCase
```

   </details>

:::note
某个目录的嵌套提示加载后，会在本次会话剩余时间内保持生效。如果你更新了提示文件并希望 goose 可靠地读取新内容，请重启会话。
:::

### 常见用例
以下是人们使用提示为 goose 提供额外上下文的一些方式：

- **决策**：指定 goose 是应自主做出更改，还是先与你确认操作。

- **验证例程**：提供 goose 应执行的测试用例或验证方法，确保更改符合项目规范。

- **反馈循环**：加入让 goose 获得反馈并迭代改进其建议的步骤。

- **指向更详细的文档**：指出 `README.md`、`docs/setup-guide.md` 等重要文件，让 goose 查阅以获得详细说明。

- **用 @ 提及来组织**：对于经常需要的文档，使用 `@filename.md` 或 `@relative/path/testing.md`，自动把文件内容包含进当前上下文，而不仅仅是引用它。这能确保 goose 立即访问到重要信息。
对于核心文档（如 API schema 或编码标准），用 @ 提及来提供即时上下文；而对于可选或非常大的文件，使用普通引用（不带 `@`）。

与提示词一样，这并不是塑造 `.goosehints` 文件的详尽清单。你可以按需包含任意多的上下文。

### 最佳实践

- **保持文件更新**：定期更新 `.goosehints` 文件，以反映项目协议或优先级的任何变化。
- **保持简洁**：确保内容直截了当、切中要点，让 goose 能快速解析并据此行动。
- **从小处着手**：先创建一小批清晰、具体的提示，再根据你的需求逐步扩展。这样更容易理解 goose 如何解读和应用你的指令。
- **引用其他文件**：把 goose 指向 /docs/style.md 或 /scripts/validation.js 等相关文件，以减少重复并让指令保持轻量。

### 自定义上下文文件

默认情况下，goose 会先查找 `AGENTS.md`，再查找 `.goosehints` 文件；但你可以使用 `CONTEXT_FILE_NAMES` 环境变量配置不同的文件名或多个上下文文件。这适用于：

- **工具兼容性**：沿用其他 AI 工具的约定（例如 `CLAUDE.md`）
- **组织管理**：把经常使用的规则拆分到多个自动加载的文件中
- **项目约定**：使用你项目既有工具链中的上下文文件（`.cursorrules`）

它的工作方式如下：
1. goose 会在全局位置（`~/.config/goose/`）与本地项目位置查找每个已配置的文件名
2. 会话开始时，goose 会从你的工作目录层级加载匹配的文件
3. 会话期间，当 goose 访问嵌套子目录时，它可以加载额外的匹配文件
4. 所有找到的文件都会被加载并合并到上下文中

#### 配置

把 `CONTEXT_FILE_NAMES` 环境变量设置为文件名的 JSON 数组。默认值为 `["AGENTS.md", ".goosehints"]`。

```bash
# Single custom file
export CONTEXT_FILE_NAMES='["AGENTS.md"]'

# Project toolchain files
export CONTEXT_FILE_NAMES='[".cursorrules", "AGENTS.md"]'

# Multiple files
export CONTEXT_FILE_NAMES='["CLAUDE.md", ".goosehints", "project_rules.txt"]'
```

---

## 持久指令

> 原文：https://block.github.io/goose/docs/guides/context-engineering/using-persistent-instructions

持久指令让你在每一轮都把文本注入 goose 的工作记忆。与 [`.goosehints`](https://block.github.io/goose/docs/guides/context-engineering/using-goosehints) 不同（后者在会话开始时加载，并可能在 goose 发现嵌套提示文件后扩展），持久指令会在每次交互时重新读取并注入最新内容。这使得它们非常适合那些必须始终强制执行、无论对话如何演变的行为护栏。

### 工作原理

goose 有一个名为 MOIM（Model-Observed Internal Memory，模型可观测内部记忆）的组件，它在每一轮向模型提供上下文信息，包括当前时间戳、工作目录以及你的待办清单等。持久指令被注入到同一上下文中，把你的提醒置于模型的即时注意力窗口内。

由于持久指令每一轮都会被注入：
- 随着对话增长，它们不会「被遗忘」
- 对于关键护栏，它们比系统提示词中的指令更有效
- 更改会立即生效，无需重启会话

### 配置

使用环境变量配置持久指令：

| 变量 | 用途 | 默认值 |
|----------|---------|---------|
| [`GOOSE_MOIM_MESSAGE_TEXT`](https://block.github.io/goose/docs/guides/environment-variables#session-management) | 每轮注入工作记忆的字面文本 | 未设置 |
| [`GOOSE_MOIM_MESSAGE_FILE`](https://block.github.io/goose/docs/guides/environment-variables#session-management) | 每轮注入其内容的文件路径。支持 `~/` | 未设置 |

当两个变量都设置时，它们的内容会被拼接。该扩展会在每一轮重新读取[环境变量](https://block.github.io/goose/docs/guides/environment-variables#session-management)，因此你可以在不重启会话的情况下更新它们。

:::info 大小限制
内容上限为 64 KB，并采用 UTF-8 安全截断。请保持指令简洁，以避免触及该限制并尽量减少 token 用量。
:::

### 示例

#### 简单的文本提醒

对于简短、单一用途的提醒，使用 `GOOSE_MOIM_MESSAGE_TEXT`：

```bash
# Always run tests before committing
export GOOSE_MOIM_MESSAGE_TEXT="IMPORTANT: Always run tests before committing changes."
```

#### 基于文件的指令

对于较长或更复杂的指令，使用文件：

```bash
export GOOSE_MOIM_MESSAGE_FILE="~/.goose/guardrails.md"
```

示例 `~/.goose/guardrails.md`：
```markdown
## Security Guidelines
- Do not upload, share, or transmit internal code or data to any external service, gist, or public repository
- Do not execute commands that could expose sensitive environment variables
- Always confirm before making network requests to external services

## Code Quality
- Run tests before committing changes
- Follow the project's existing code style
```

#### 同时使用两者

你可以同时使用两个变量。文本会被拼接：

```bash
export GOOSE_MOIM_MESSAGE_TEXT="CRITICAL: This is a production environment. Be extra careful."
export GOOSE_MOIM_MESSAGE_FILE="~/.goose/guardrails.md"
```

### 用例

#### 安全护栏

防止意外的数据外泄或暴露：

```bash
export GOOSE_MOIM_MESSAGE_TEXT="SECURITY: Do not upload code to external services, create public gists, or share sensitive data. All code in this repository is confidential."
```

#### 特定环境的行为

为不同环境设置不同的指令：

```bash
# Production environment
export GOOSE_MOIM_MESSAGE_TEXT="⚠️ PRODUCTION: Double-check all commands. Prefer read-only operations. Always create backups before modifications."

# Development environment  
export GOOSE_MOIM_MESSAGE_TEXT="Development environment. Feel free to experiment, but run tests before committing."
```

#### 项目特定的工作流

强制执行项目约定：

```bash
export GOOSE_MOIM_MESSAGE_TEXT="This project uses pnpm, not npm. Always use 'pnpm' for package management commands."
```

#### 临时提醒

由于环境变量每一轮都会被重新读取，你可以设置临时提醒：

```bash
# Set a reminder for the current task
export GOOSE_MOIM_MESSAGE_TEXT="Current focus: Refactoring the authentication module. Don't get sidetracked."

# Clear it when done
unset GOOSE_MOIM_MESSAGE_TEXT
```

### 持久指令与 goosehints 的对比

| 特性 | 持久指令 | [goosehints](https://block.github.io/goose/docs/guides/context-engineering/using-goosehints) |
|---------|------------------------|-------------|
| 加载时机 | 每一轮 | 会话开始时，以及会话期间发现的嵌套上下文文件 |
| 是否会被遗忘 | 否 | 会，随着上下文被填满 |
| 最适合 | 关键护栏、安全规则 | 项目上下文、编码标准 |
| Token 成本 | 每轮 | 开始时一次 |
| 更新所需 | 无需重启 | 重启会话 |

**在以下情况使用持久指令：**
- 该指令至关重要，绝不能被忽视
- 你需要无法被绕过的安全护栏
- 你想在会话中途更改行为而无需重启

**在以下情况使用 goosehints：**
- 提供项目上下文与背景信息
- 设置编码标准与偏好
- 该信息有帮助但并非关键

你可以将两者一起使用：goosehints 用于项目上下文，持久指令用于关键护栏。

### 最佳实践

1. **保持简洁**：持久指令每一轮都会被注入，因此文本越长，每次交互消耗的 token 就越多。

2. **要具体**：像「小心一点」这样含糊的指令，不如「提交前始终运行 `npm test`」这样具体的指令有效。

3. **区分优先级**：把最重要的指令放在最前面，以防被截断。

4. **用文件承载复杂规则**：如果你有多条准则，把它们组织到一个文件中，而不是全部塞进 `GOOSE_MOIM_MESSAGE_TEXT`。

5. **测试你的护栏**：设置好持久指令后，通过让 goose 做一件本应被阻止的事情，来测试它是否遵守这些指令。

---

## Agent Skill

> 原文：https://block.github.io/goose/docs/guides/context-engineering/using-skills

Skill 是可复用的指令与资源集合，用来教会 goose 如何执行特定任务。一个 Skill 可以简单到一份清单，也可以复杂到包含领域专业知识的详细工作流，还可以包含脚本或模板等辅助文件。示例用例包括部署流程、代码审查清单和 API 集成指南。

:::info
此功能使用内置的 Skills 平台扩展，该扩展默认启用。
:::

会话开始时，goose 会把发现的 Skill 名称与描述加入其指令。在会话期间，goose 会在以下情况下加载某个 Skill 的完整指令：
- 你的请求明确匹配某个 Skill 的用途
- 你明确要求使用某个 Skill，例如：
  - 「使用 code-review Skill 来审查这个 PR」
  - 「按照 new-service Skill 来搭建 auth 服务」
  - 「应用 deployment Skill」

你也可以询问 goose 有哪些 Skill 可用，运行 `goose skills list`，或使用 CLI 的 `/skills` 命令列出可用 Skill 并按名称加载一个或多个：

```bash
/skills code-review edge-case-finder
```

:::info Claude 兼容性
goose Skill 与 Claude Desktop 以及其他[支持 Agent Skill 的代理](https://agentskills.io/home#adoption)兼容。
:::

### 内置 Skill

goose 内置了一个 Skill，无需任何安装即可始终使用：

| Skill | 描述 |
|-------|-------------|
| `web-search` | 使用 DuckDuckGo（无需 API key）、Tavily 或 SearXNG 搜索网页，并提取页面内容。 |

对于浏览器自动化——导航页面、点击、填写表单和截取屏幕截图——请安装由上游维护的 browser-use Skill：

```bash
browser-use skill install
```

这样你就能获得来自 browser-use 项目的完整、最新的 Skill，包括远程浏览器支持、AX 树元素选择策略和录制工具。

### Skill 位置

Skill 可以存储在全局、按项目存储，或存储在已安装的插件中：

1. `~/.agents/skills/` — 全局 Skill，在所有会话中可用
2. `.agents/skills/` — 项目级 Skill，作用域为当前项目
3. `~/.agents/plugins/<plugin-name>/` — 由已安装的[插件](https://block.github.io/goose/docs/guides/context-engineering/plugins)提供的 Skill

在具名子目录中放置一个 `SKILL.md` 文件。例如，一个名为
`code-review` 的全局 Skill 位于 `~/.agents/skills/code-review/SKILL.md`。

> **向后兼容：** goose 也会从 `.goose/skills/`、
> `.claude/skills/`、`~/.claude/skills/` 以及平台特定的配置目录中发现 Skill，
> 但推荐的标准是 `agents/skills/`。

### 创建 Skill

当你有一个涉及多个步骤、专门知识或辅助文件的可重复工作流时，就创建一个 Skill。

#### Skill 文件结构

每个 Skill 都位于自己的目录中，其中包含一个 `SKILL.md` 文件：

```
~/.agents/skills/
└── code-review/
    └── SKILL.md
```

`SKILL.md` 文件需要包含带 `name` 与 `description` 的 YAML frontmatter，其后是 Skill 内容：

```markdown
---
name: code-review
description: Comprehensive code review checklist for pull requests
---

# Code Review Checklist

When reviewing code, check each of these areas:

## Functionality
- [ ] Code does what the PR description claims
- [ ] Edge cases are handled
- [ ] Error handling is appropriate

## Code Quality
- [ ] Follows project style guide
- [ ] No hardcoded values that should be configurable
- [ ] Functions are focused and well-named

## Testing
- [ ] New functionality has tests
- [ ] Tests are meaningful, not just for coverage
- [ ] Existing tests still pass

## Security
- [ ] No credentials or secrets in code
- [ ] User input is validated
- [ ] SQL queries are parameterized
```

### 来自插件的 Skill

Skill 也可以来自已安装的[插件](https://block.github.io/goose/docs/guides/context-engineering/plugins)。插件提供的 Skill 会在会话启动时被发现，并像其他 Skill 一样工作。对于 Open Plugin，Skill 名称会以插件名为命名空间，例如 `my-plugin:review`。在显式加载插件提供的 Skill 时，请使用该完整名称。

### 辅助文件

Skill 可以包含脚本、模板或配置文件等辅助文件。把它们放在 Skill 目录中：

```
~/.agents/skills/
└── api-setup/
    ├── SKILL.md
    ├── setup.sh
    └── templates/
        └── config.template.json
```

当 goose 加载该 Skill 时，它会看到这些辅助文件，并可以使用 [Developer 扩展](https://block.github.io/goose/docs/mcp/developer-mcp)的文件工具访问它们。

<details>
<summary>带辅助文件的 Skill 示例</summary>

**SKILL.md:**
```markdown
---
name: api-setup
description: Set up API integration with configuration and helper scripts
---

# API Setup

This skill helps you set up a new API integration with our standard configuration.

## Steps

1. Run `setup.sh <api-name>` to create the integration directory
2. Copy `templates/config.template.json` to your integration directory
3. Update the config with your API credentials
4. Test the connection

## Configuration

The config template includes:
- `api_key`: Your API key (get from the provider's dashboard)
- `endpoint`: API endpoint URL
- `timeout`: Request timeout in seconds (default: 30)

## Verification

After setup, verify:
- [ ] Config file is valid JSON
- [ ] API key is set and not a placeholder
- [ ] Test connection succeeds
```

**setup.sh:**
```bash
#!/bin/bash
API_NAME=$1
mkdir -p "integrations/$API_NAME"
cp templates/config.template.json "integrations/$API_NAME/config.json"
echo "Created integration directory for $API_NAME"
echo "Edit integrations/$API_NAME/config.json with your credentials"
```

**templates/config.template.json:**
```json
{
  "api_key": "YOUR_API_KEY_HERE",
  "endpoint": "https://api.example.com/v1",
  "timeout": 30,
  "retry_attempts": 3
}
```

</details>

### 常见用例示例

<details>
<summary>部署工作流</summary>

```markdown
---
name: production-deploy
description: Safe deployment procedure for production environment
---

# Production Deployment

## Pre-deployment
1. Ensure all tests pass
2. Get approval from at least 2 reviewers
3. Notify #deployments channel

## Deploy
1. Create release branch from main
2. Run `npm run build:prod`
3. Deploy to staging, verify, then production
4. Monitor error rates for 30 minutes

## Rollback
If error rate exceeds 1%:
1. Revert to previous deployment
2. Notify #incidents channel
3. Create incident report
```

</details>

<details>
<summary>测试策略</summary>

```markdown
---
name: testing-strategy
description: Guidelines for writing effective tests in this project
---

# Testing Guidelines

## Unit Tests
- Test one thing per test
- Use descriptive test names: `test_user_creation_fails_with_invalid_email`
- Mock external dependencies

## Integration Tests
- Test API endpoints with realistic data
- Verify database state changes
- Clean up test data after each test

## Running Tests
- `npm test` — Run all tests
- `npm test:unit` — Unit tests only
- `npm test:integration` — Integration tests (requires database)
```

</details>

<details>
<summary>API 集成指南</summary>

````markdown
---
name: square-integration
description: How to integrate with our Square account
---

# Square Integration

## Authentication
- Test key: Use `SQUARE_TEST_KEY` from `.env.test`
- Production key: In 1Password under "Square Production"

## Common Operations

### Create a customer
```javascript
const customer = await squareup.customers.create({
  email: user.email,
  metadata: { userId: user.id }
});
```

### Handle webhooks
Always verify webhook signatures. See `src/webhooks/square.js` for our handler pattern.

## Error Handling
- `card_declined`: Show user-friendly message, suggest different payment method
- `rate_limit`: Implement exponential backoff
- `invalid_request`: Log full error, likely a bug in our code
````

</details>

:::tip 其他支持复用的 goose 功能
- [.goosehints](https://block.github.io/goose/docs/guides/context-engineering/using-goosehints)：最适合通用偏好、项目上下文以及像「始终使用 TypeScript」这样的重复指令
- [recipes](https://block.github.io/goose/docs/guides/recipes/session-recipes)：可分享的配置，把指令、提示词与设置打包在一起
:::

### 最佳实践

- **保持 Skill 聚焦** — 每个工作流或领域一个 Skill。如果某个 Skill 变得很长，考虑拆分它。
- **为清晰而写** — Skill 是给 goose 的指令。使用清晰、直接的语言与编号步骤。
- **包含验证步骤** — 帮助 goose 确认工作流已成功完成。

### 附加资源

<ContentCardCarousel
  items={[
    {
      type: 'blog',
      title: 'Did Skills Kill MCP?',
      description: 'An overview of Agent Skills vs MCP',
      thumbnailUrl: skillsvsmcp,
      linkUrl: '/blog/2025/12/22/agent-skills-vs-mcp',
      date: '2025-12-22',
      duration: '4 min read'
    }
  ]}
/>

---

## 自定义提示词模板

> 原文：https://block.github.io/goose/docs/guides/context-engineering/prompt-templates

goose 内置了提示词模板，用于在不同情境下引导其行为。你可以编辑这些模板，自定义 goose 如何响应、如何创建计划、在压缩期间决定保存什么，等等。

### 工作原理

goose 的默认提示词模板定义在代码库中，并内嵌于应用里。你可以在本地配置目录中创建自定义版本（直接创建或通过 goose Desktop）来覆盖任何默认模板。

当你自定义模板时：

- 你的自定义内容会在 goose 更新后保留
- 代码库中默认模板的更改不会影响你自定义的模板
- 你可以随时重置为默认模板
- 更改会在新会话中生效

你的更改可以是重大更新，也可以是细微调整，例如：
- 编辑 `system.md`，通过添加一条「Reply in Dutch」指令让 goose 用荷兰语回复
- 编辑 `compaction.md`，通过添加一条「Preserve every file path and command that was run.」指令，在总结时保留更多细节

关于修改模板变量的重要信息，请参阅[模板变量语法](#template-variable-syntax)。

:::info 相关配置
其他 goose 设置与功能也可能影响行为或提供上下文，例如[配置文件](https://block.github.io/goose/docs/guides/config-files)、[.goosehints](https://block.github.io/goose/docs/guides/context-engineering/using-goosehints) 和 [Skill](https://block.github.io/goose/docs/guides/context-engineering/using-skills)。
:::

### 管理提示词模板

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  
  goose Desktop 用户可以在 `Settings` 页面管理模板。

  **自定义模板：**

  1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏
  2. 在侧边栏中点击 `Settings`
  3. 点击 `Prompts` 标签页
  4. 点击你想更改的模板旁的 `Edit`
  5. 在编辑器中做出更改。你可以随时点击 `Restore Default` 从默认模板重新开始。
  6. 点击 `Save` 应用你的自定义

  已自定义的提示词模板会显示 `Customized` 徽章。

  **将模板重置为默认值：**

  1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏
  2. 在侧边栏中点击 `Settings`
  3. 点击 `Prompts` 标签页
  4. 点击你想重置的模板旁的 `Edit`
  5. 点击 `Reset to Default` 删除你的本地模板文件

  或者点击标签页顶部的 `Reset All`，删除你所有的本地模板文件。

  </TabItem>
  <TabItem value="cli" label="goose CLI">

  goose CLI 用户可以直接在文件系统中编辑模板文件。

  自定义模板存储在：

  - **macOS/Linux：** `~/.config/goose/prompts/`
  - **Windows：** `%APPDATA%\Block\goose\config\prompts\`

  **自定义模板：**

  1. 如果 `prompts` 目录不存在，则创建它
  2. 从上表中复制模板文件名（例如 `system.md`）
  3. 在你的 prompts 目录中创建同名文件
  4. 添加你的自定义内容并保存更改。我们建议你先查看或复制默认模板（链接在上面的[表格](#available-prompt-templates)中）。

  **将模板重置为默认值：**

  1. 从你的 `prompts` 目录中删除该模板文件

  </TabItem>
</Tabs>

#### 可用的提示词模板

以下默认模板均可自定义。

| 模板 | 描述 | 适用范围 |
|----------|-------------|------------|
| [system.md](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/prompts/system.md) | 定义 goose 角色、能力与响应格式的通用系统提示词 | Desktop 和 CLI |
| [apps_create.md](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/prompts/apps_create.md) | 用于生成新的独立应用的提示词（开发中） | 仅 Desktop |
| [apps_iterate.md](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/prompts/apps_iterate.md) | 用于更新现有独立应用的提示词（开发中） | 仅 Desktop |
| [compaction.md](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/prompts/compaction.md) | 达到上下文限制时用于总结对话历史的提示词 | Desktop 和 CLI |
| [permission_judge.md](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/prompts/permission_judge.md) | 用于分析工具操作以进行只读检测的提示词 | Desktop 和 CLI |
| [subagent_system.md](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/prompts/subagent_system.md) | 为处理特定任务而派生的子代理所使用的系统提示词 | Desktop 和 CLI |
| [tiny_model_system.md](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/prompts/tiny_model_system.md) | 使用 shell 命令模拟的小型本地模型所使用的系统提示词 | CLI |
| [session_name.md](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/prompts/session_name.md) | 用于根据对话历史生成简短会话名称的提示词 | Desktop 和 CLI |

可自定义的模板在 [`prompt_template.rs`](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/prompt_template.rs) 中的 `TEMPLATE_REGISTRY` 数组里列出。

#### 模板变量语法

模板使用 [Jinja2](https://jinja.palletsprojects.com/) 语法处理动态内容：

- `{{ variable }}` - 插入一个值（例如 `{{ extensions }}` 会列出已启用的扩展）
- `{% if condition %}...{% endif %}` - 条件区块
- `{% for item in list %}...{% endfor %}` - 遍历项目

查看默认模板（从上面的[表格](#available-prompt-templates)链接过去）以找到常用变量，例如 `{{ extensions }}` 和 `{{ hints }}`。

##### 转义模板变量

如果你需要在模板中包含不经替换的字面变量语法，请用单引号把它括起来：

```markdown
This will substitute: {{ variable }}
This will appear literally: {{'{{variable}}'}}
```

:::warning
修改模板变量时要小心，错误的更改可能破坏功能。请在新会话中测试你的更改，确保它们按预期工作。
:::

### 附加资源

<ContentCardCarousel
  items={[
    {
      type: 'blog',
      title: 'AI Prompting 101: How to Get the Best Responses from Your AI Agent',
      description: 'Learn different prompting styles—from instruction-based to chain-of-thought—and discover which approach works best for your needs.',
      thumbnailUrl: promptBanner,
      linkUrl: '/blog/2025/03/19/better-ai-prompting',
      date: '2025-03-19',
      duration: '8 min read'
    }
  ]}
/>
