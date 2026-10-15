# goose 官方文档中文手册：第 09 章　提供方进阶与多模型

## 多模型配置

> 原文：https://block.github.io/goose/docs/guides/multi-model

<h1 className={styles.pageTitle}>多模型配置</h1>
<p className={styles.pageDescription}>
  goose 支持在单个会话内使用不同模型的多种方式，让你可以针对成本、性能和任务专门化进行优化。策略涵盖从手动或按轮次选择模型，到动态的、上下文感知的切换。
</p>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>📚 文档与指南</h2>
  <div className={styles.cardGrid}>
    <Card 
      title="会话中途切换模型"
      description="使用 /model 命令在不丢失会话的情况下切换模型，既可以保持同一提供方，也可以切换到另一个提供方。"
      link="https://block.github.io/goose/docs/guides/goose-cli-commands#slash-commands"
    />
    <Card 
      title="子代理"
      description="把聚焦的任务委派给相互隔离的 goose 实例，每个实例都能运行自己的提供方和模型。"
      link="https://block.github.io/goose/docs/guides/context-engineering/subagents"
    />
    <Card 
      title="上下文工程"
      description="塑造 goose 在会话期间保留在上下文中的内容，包括压缩和持久化指令。"
      link="https://block.github.io/goose/docs/guides/context-engineering"
    />
  </div>
</div>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>📝 精选博客文章</h2>
  <div className={styles.cardGrid}>
    <Card
      title="把 LLM 当作工具箱里的工具：通往更智能 AI Agent 的多模型方法"
      description="LLM 是专门化的工具，多模型方法能打造更智能、更高效的 AI Agent。"
      link="https://block.github.io/goose/blog/2025/06/16/multi-model-in-goose"
    />
    <Card
      title="AI 怀疑论者的上下文窗口指南"
      description="了解在长时间运行的会话中管理上下文窗口和 token 用量的实用方法。"
      link="https://block.github.io/goose/blog/2025/08/18/understanding-context-windows"
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
      src: 'https://www.youtube.com/embed/ZyhUTsChFUw',
      title: 'goose\'s Multi-Model Setup',
      description: 'Learn practical multi-model workflows in goose',
      duration: '5:01'
    }
  ]}
/>
</div>

---

## ACP 提供方

> 原文：https://block.github.io/goose/docs/guides/acp-providers

goose 支持把 [Agent Client Protocol (ACP)](https://agentclientprotocol.com/) agent 作为提供方使用。ACP 是与编码 agent 通信的标准协议，实现该协议的 agent 有一个不断增长的[注册表](https://github.com/agentclientprotocol/registry)。

ACP 提供方会把 goose 的[扩展](https://block.github.io/goose/docs/getting-started/using-extensions)作为 MCP 服务器传递给 agent，因此 agent 可以直接调用你的扩展。

:::tip 使用你现有的订阅
ACP 提供方让你可以把 goose 与你现有的 Claude Code 或 ChatGPT Plus/Pro 订阅配合使用 —— 没有按 token 计费的 API 成本。对于已弃用的 [CLI 提供方](https://block.github.io/goose/docs/guides/cli-providers)，它们是推荐的替代方案。
:::

:::warning 限制
- **不支持会话 fork 或恢复**：你可以启动新会话，但尚不支持 `goose session resume` 和 `goose session fork`。
- **ACP 会话 ID 与 goose 会话 ID 不同**：遥测字段在两者之间可能无法对应。
:::

### 可用的 ACP 提供方

#### Amp ACP

封装了 [amp-acp](https://www.npmjs.com/package/amp-acp)，这是面向 [Amp](https://ampcode.com) 的 ACP 适配器。使用你现有的 Amp 订阅。

**要求：**
- Node.js 和 npm
- 已安装 Amp CLI（`curl -fsSL https://ampcode.com/install.sh | bash`）
- 已安装 ACP 适配器（`npm install -g amp-acp`）
- 已用你的 Amp 账号完成认证（`amp` CLI 可正常工作）

#### Claude ACP

封装了 [claude-agent-acp](https://github.com/agentclientprotocol/claude-agent-acp)，这是面向 Anthropic 的 Claude Code 的 ACP 适配器。使用与已弃用的 `claude-code` CLI 提供方相同的 Claude 订阅。

**要求：**
- Node.js 和 npm
- 有效的 Claude Code 订阅
- 已用你的 Anthropic 账号完成认证（`claude` CLI 可正常工作）

#### Codex ACP

通过 [codex-acp](https://github.com/agentclientprotocol/codex-acp) 适配器，将 goose 与 ChatGPT Plus/Pro 或 OpenAI API 额度配合使用。

**要求：**
- Node.js 和 npm
- 有效的 ChatGPT Plus/Pro 订阅或 OpenAI API 额度
- 已用你的 OpenAI 账号完成认证（`codex` CLI 可正常工作）

#### Pi ACP

封装了 `pi-acp`，这是面向 Pi 的 ACP 适配器。使用你现有的 Pi 安装。

**要求：**
- 已安装 Pi CLI
- 已安装 ACP 适配器（`pi-acp` 二进制可用）
- 已用你的 Pi 账号完成认证（`pi` CLI 可正常工作）

### 设置步骤

#### Amp ACP

1. **安装 Amp CLI**

   ```bash
   curl -fsSL https://ampcode.com/install.sh | bash
   ```

2. **安装 ACP 适配器**

   ```bash
   npm install -g amp-acp
   ```

3. **使用 Amp 进行认证**

   运行 `amp` 并按提示完成认证。

4. **配置 goose**

   设置提供方环境变量：
   ```bash
   export GOOSE_PROVIDER=amp-acp
   ```

   或者通过 goose CLI 使用 `goose configure` 进行配置。

#### Claude ACP

1. **安装 ACP 适配器**

   ```bash
   npm install -g @agentclientprotocol/claude-agent-acp
   ```

2. **使用 Claude 进行认证**

   确保你的 Claude CLI 已认证且可正常工作

3. **配置 goose**

   设置提供方环境变量：
   ```bash
   export GOOSE_PROVIDER=claude-acp
   ```

   或者通过 goose CLI 使用 `goose configure` 进行配置：

   ```bash
   ┌   goose-configure
   │
   ◇  What would you like to configure?
   │  Configure Providers
   │
   ◇  Which model provider should we use?
   │  Claude Code
   │
   ◇  Model fetch complete
   │
   ◇  Enter a model from that provider:
   │  default
   ```

#### Codex ACP

1. **检查已安装的包**

   ```bash
   codex-acp --version
   ```

   输出应以 `@agentclientprotocol/codex-acp` 开头。如果是，则继续认证步骤。

2. **仅在需要时安装或替换**

   如果 `--version` 被拒绝，请移除 `@agentclientprotocol/codex-acp`：

   ```bash
   npm uninstall -g @agentclientprotocol/codex-acp
   ```

   如果 `codex-acp` 缺失或已被移除，请安装 `@agentclientprotocol/codex-acp`：

   ```bash
   npm install -g @agentclientprotocol/codex-acp
   ```

3. **使用 OpenAI 进行认证**

   运行 `codex` 并按提示完成认证。可以复用兼容的现有 Codex 登录。

4. **配置 goose**

   设置提供方，并使用 `current` 让 Codex 选择其默认模型：
   ```bash
   export GOOSE_PROVIDER=codex-acp
   export GOOSE_MODEL=current
   ```

   或者通过 goose CLI 使用 `goose configure` 进行配置：

   ```bash
   ┌   goose-configure
   │
   ◇  What would you like to configure?
   │  Configure Providers
   │
   ◇  Which model provider should we use?
   │  Codex CLI
   │
   ◇  Model fetch complete
   │
   ◇  Enter a model from that provider:
   │  current
   ```

替换 npm 包不会改变 `~/.codex`，也不需要重建你的 goose 配置。goose 不会自动替换该包。

#### Pi ACP

1. **安装 Pi CLI 和 ACP 适配器**

   按照项目的安装说明安装 `pi` CLI 和 `pi-acp` ACP 适配器。

2. **使用 Pi 进行认证**

   运行 `pi` 并按提示完成认证。

3. **配置 goose**

   设置提供方环境变量：
   ```bash
   export GOOSE_PROVIDER=pi-acp
   ```

   或者通过 goose CLI 使用 `goose configure` 进行配置。

### 用法示例

#### 基本用法

```bash
goose session
```

#### 与扩展一起使用

通过 `--with-extension` 或 `--with-streamable-http-extension` 配置的扩展会被传递给 ACP agent：

```bash
GOOSE_PROVIDER=claude-acp goose run \
  --with-extension 'npx -y @modelcontextprotocol/server-everything' \
  -t 'Use the echo tool to say hello'
```

```bash
GOOSE_PROVIDER=codex-acp goose run \
  --with-streamable-http-extension 'https://mcp.kiwi.com' \
  -t 'Search for flights from BKI to SYD tomorrow'
```

### 配置选项

#### Amp ACP 配置

| 环境变量 | 描述 | 默认值 |
|----------------------|-------------------|-----------|
| `GOOSE_PROVIDER`     | 设置为 `amp-acp`  | 无      |
| `GOOSE_MODEL`        | 要使用的模型      | `current` |
| `GOOSE_MODE`         | 权限模式          | `auto`    |

#### Claude ACP 配置

| 环境变量 | 描述 | 默认值 |
|----------------------|---------------------|-----------|
| `GOOSE_PROVIDER`     | 设置为 `claude-acp` | 无      |
| `GOOSE_MODEL`        | 要使用的模型        | `default` |
| `GOOSE_MODE`         | 权限模式            | `auto`    |

**已知模型：**
- `default`（opus）
- `sonnet`
- `haiku`

**权限模式（`GOOSE_MODE`）：**

| 模式            | 会话模式            | 行为                                              |
|-----------------|---------------------|-------------------------------------------------------|
| `auto`          | `bypassPermissions` | 跳过所有权限检查                           |
| `smart-approve` | `acceptEdits`       | 自动接受文件编辑，对高风险操作进行提示 |
| `approve`       | `default`           | 对所有需要权限的操作进行提示        |
| `chat`          | `plan`              | 仅规划，不执行工具                      |

关于会话模式的细节，请参阅 [claude-agent-acp](https://github.com/agentclientprotocol/claude-agent-acp)。

#### Codex ACP 配置

| 环境变量 | 描述 | 默认值 |
|----------------------|--------------------|-----------|
| `GOOSE_PROVIDER`     | 设置为 `codex-acp` | 无      |
| `GOOSE_MODEL`        | 要使用的模型       | `current` |
| `GOOSE_MODE`         | 权限模式           | `auto`    |

Codex ACP 会动态上报其可用模型。保留 `current` 以使用 Codex 的默认模型，或显式选择一个已发现的模型。

**权限模式（`GOOSE_MODE`）：**

| goose 模式      | Codex ACP 模式      |
|-----------------|---------------------|
| `auto`          | `agent-full-access` |
| `smart-approve` | `agent`             |
| `approve`       | `read-only`         |
| `chat`          | `read-only`         |

关于会话模式的细节，请参阅 [codex-acp](https://github.com/agentclientprotocol/codex-acp)。

#### Pi ACP 配置

| 环境变量 | 描述 | 默认值 |
|----------------------|------------------|-----------|
| `GOOSE_PROVIDER`     | 设置为 `pi-acp`  | 无      |
| `GOOSE_MODEL`        | 要使用的模型     | `current` |
| `GOOSE_MODE`         | 权限模式         | `auto`    |

### 错误处理

ACP 提供方依赖外部二进制文件，因此请确保：

- ACP agent 二进制已安装并在你的 PATH 中（`amp-acp`、`claude-agent-acp`、`codex-acp`、`pi-acp` 或 `copilot`）
- 底层 CLI 工具已认证且可正常工作
- 订阅额度未被超出
- 已安装 Node.js 和 npm（针对 npm 分发的适配器）

如果 goose 找不到该二进制文件，会话启动会失败并报错。运行 `which <binary>` 来验证安装。

---

## CLI 提供方

> 原文：https://block.github.io/goose/docs/guides/cli-providers

:::warning 已弃用 —— 请使用 ACP 提供方
Claude Code（`claude-code`）、Codex（`codex`）、Gemini CLI（`gemini-cli`）和 Gemini OAuth（`gemini_oauth`）提供方均已弃用。对于 Claude 和 Codex，请改用 [ACP 提供方](https://block.github.io/goose/docs/guides/acp-providers)（`claude-acp`、`codex-acp`）。对于 Gemini，请使用带 Gemini API key 的 [Google 提供方](https://block.github.io/goose/docs/getting-started/providers#google-gemini)或 [Vertex AI](https://cloud.google.com/vertex-ai)。已弃用的提供方仅为向后兼容而保留可用。
:::

goose 可以利用透传（pass-through）提供方，与 Anthropic、OpenAI、Cursor 和 Google 的现有 CLI 工具集成。这些提供方让你可以通过 goose 的界面使用现有的 Claude Code、Codex、Cursor Agent 和 Google Gemini CLI 订阅，为这些工具增添会话管理、持久化和工作流集成能力。Gemini OAuth 提供方已被弃用，因为 Google 不再支持某些账号类型底层的 Code Assist 登录流程。请参阅 Google 的[公告](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)和[弃用通知](https://developers.google.com/gemini-code-assist/docs/deprecations/code-assist-individuals)。

:::warning 限制
这些提供方并不完全支持所有 goose 功能，可能有平台或能力上的限制，出现问题有时还需要高级调试。它们在此纯粹作为便利而提供。
:::

### 为什么要使用 CLI 提供方？

如果你符合以下情况，CLI 提供方会很有用：

- 已经拥有 Claude Code、Codex、Cursor 或 Google Gemini CLI 订阅，想通过 goose 使用它而不是按 token 付费
- 需要会话持久化来保存、恢复和导出对话历史
- 想使用 goose recipe 和定时任务来创建可重复的工作流
- 更喜欢在不同 AI 提供方之间使用统一的命令
- 想在任务中[一起使用多个模型](https://block.github.io/goose/docs/guides/multi-model)

#### 优势

##### 会话管理
- **持久化对话**：跨重启保存和恢复会话
- **导出能力**：导出对话历史和产出物
- **会话组织**：管理多个对话线程

##### 工作流集成
- **Recipe 兼容性**：在自动化的 goose recipe 中使用 CLI 提供方
- **调度支持**：纳入定时任务和工作流
- **混合配置**：与子代理和模型专属工作流组合使用

##### 界面一致性
- **统一命令**：在所有提供方上使用相同的 `goose session` 界面
- **一致的配置**：通过 goose 的配置系统管理所有提供方

:::warning 扩展
CLI 提供方**不会**让你访问 goose 的扩展生态（MCP 服务器、第三方集成等）。它们使用自己内置的工具以避免冲突。如果你需要 goose 的扩展，请改用标准的 [API 提供方](https://block.github.io/goose/docs/getting-started/providers#available-providers)。
:::


### 可用的 CLI 提供方

#### Claude Code

Claude Code 提供方与 Anthropic 的 [Claude CLI 工具](https://claude.ai/cli)集成，让你可以通过现有的 Claude Code 订阅使用 Claude 模型。

**功能特性：**
- 使用 Claude 的最新模型
- 200,000 token 的上下文上限
- 自动从系统提示词中过滤掉 goose 扩展（因为 Claude Code 有自己的工具生态）
- 流式 JSON（NDJSON）协议，用于持久化的多轮会话

**要求：**
- 已安装并配置 Claude CLI 工具
- 有效的 Claude Code 订阅
- CLI 工具已用你的 Anthropic 账号认证

#### OpenAI Codex

Codex 提供方与 OpenAI 的 [Codex CLI 工具](https://developers.openai.com/codex/cli)集成，让你可以通过现有的 ChatGPT Plus/Pro 订阅或 API 额度使用 OpenAI 模型。

**功能特性：**
- 使用 OpenAI 的 GPT-5 系列模型（gpt-5.2-codex、gpt-5.2、gpt-5.1-codex-max、gpt-5.1-codex-mini）
- 可配置的推理投入级别（`low`、`medium`、`high`、`xhigh`；`none` 仅在非 codex 模型如 `gpt-5.2` 上受支持）
- 可选的 skills 支持以增强能力
- JSON 输出解析以获得结构化响应
- 自动从系统提示词中过滤掉 goose 扩展

**要求：**
- 已安装 Codex CLI 工具（`npm i -g @openai/codex` 或 `brew install --cask codex`）
- 有效的 ChatGPT Plus/Pro 订阅或 OpenAI API 额度
- CLI 工具已用你的 OpenAI 账号认证
- 默认情况下，Codex 要求从 git 仓库中运行。设置 `CODEX_SKIP_GIT_CHECK=true` 可绕过此要求

#### Cursor Agent

Cursor 提供方与 Cursor 的 [CLI agent](https://docs.cursor.com/en/cli/installation)集成，通过你现有的订阅提供访问能力。

**功能特性：**

- 与 Cursor Agent CLI 编码任务集成。
- 非常适合与代码相关的工作流和文件交互。

**要求：**

- 已安装并配置 cursor-agent 工具。
- CLI 工具已认证。

#### Gemini CLI

Gemini CLI 提供方与 Google 的 [Gemini CLI 工具](https://ai.google.dev/gemini-api/docs)集成，通过你的 Google AI 订阅提供对 Gemini 模型的访问能力。

**功能特性：**
- 1,000,000 token 的上下文上限

**要求：**
- 已安装并配置 Gemini CLI 工具
- CLI 工具已用你的 Google 账号认证

### 设置步骤

#### Claude Code

1. **安装 Claude CLI 工具**
   
   按照 [Claude Code 的安装说明](https://docs.anthropic.com/en/docs/claude-code/overview)安装并配置 Claude CLI 工具。

2. **使用 Claude 进行认证**
   
   确保你的 Claude CLI 已认证且可正常工作

3. **配置 goose**
   
   设置提供方环境变量：
   ```bash
   export GOOSE_PROVIDER=claude-code
   ```
   
   或者通过 goose CLI 使用 `goose configure` 进行配置：

   ```bash
   ┌   goose-configure 
   │
   ◇  What would you like to configure?
   │  Configure Providers 
   │
   ◇  Which model provider should we use?
   │  Claude Code 
   │
   ◇  Model fetch complete
   │
   ◇  Enter a model from that provider:
   │  default
   ```
#### OpenAI Codex

1. **安装 Codex CLI 工具**

   使用 npm 或 Homebrew 安装 Codex CLI：
   ```bash
   npm i -g @openai/codex
   # or
   brew install --cask codex
   ```

2. **使用 OpenAI 进行认证**

   运行 `codex` 并按提示完成认证。你可以使用你的 ChatGPT 账号或 API key。

3. **配置 goose**

   设置提供方环境变量：
   ```bash
   export GOOSE_PROVIDER=codex
   ```

   或者通过 goose CLI 使用 `goose configure` 进行配置：

   ```bash
   ┌   goose-configure
   │
   ◇  What would you like to configure?
   │  Configure Providers
   │
   ◇  Which model provider should we use?
   │  OpenAI Codex CLI
   │
   ◇  Model fetch complete
   │
   ◇  Enter a model from that provider:
   │  gpt-5.2-codex
   ```

#### Cursor Agent

1. **安装 Cursor agent 工具**

   按照 [Cursor Agent 的安装说明](https://docs.cursor.com/en/cli/installation)安装并配置 cursor agent 工具。

2. **使用 Cursor 进行认证**

   确保你的 Cursor Agent 已认证且可正常工作

3. **配置 goose**

   设置提供方环境变量：

   ```bash
   export GOOSE_PROVIDER=cursor-agent
   ```

   或者通过 goose CLI 使用 `goose configure` 进行配置：

   ```bash
   ┌   goose-configure
   │
   ◇  What would you like to configure?
   │  Configure Providers
   │
   ◇  Which model provider should we use?
   │  Cursor Agent
   │
   ◇  Model fetch complete
   │
   ◇  Enter a model from that provider:
   │  default
   ```

#### Gemini CLI

1. **安装 Gemini CLI 工具**
   
   按照 [Gemini CLI 的安装说明](https://blog.google/technology/developers/introducing-gemini-cli-open-source-ai-agent/)安装并配置 Gemini CLI 工具。

2. **使用 Google 进行认证**
   
   确保你的 Gemini CLI 已认证且可正常工作。

3. **配置 goose**
   
   设置提供方环境变量：
   ```bash
   export GOOSE_PROVIDER=gemini-cli
   ```
   
   或者通过 goose CLI 使用 `goose configure` 进行配置：

   ```bash
   ┌   goose-configure 
   │
   ◇  What would you like to configure?
   │  Configure Providers 
   │
   ◇  Which model provider should we use?
   │  Gemini CLI 
   │
   ◇  Model fetch complete
   │
   ◇  Enter a model from that provider:
   │  default
   ```

### 用法示例

#### 基本用法

配置完成后，你可以像使用其他提供方一样，用这些提供方启动一个 goose 会话：

```bash
goose session
```

### 配置选项

#### Claude Code 配置

| 环境变量 | 描述 | 默认值 |
|---------------------|-------------|---------|
| `GOOSE_PROVIDER` | 设置为 `claude-code` 以使用此提供方 | 无 |
| `GOOSE_MODEL` | 要使用的模型（只有 `sonnet` 或 `opus` 会传递给 CLI） | `claude-sonnet-4-20250514` |
| `CLAUDE_CODE_COMMAND` | Claude CLI 命令的路径 | `claude` |

**已知模型：**

以下模型会被识别，并通过 `--model` 标志传递给 Claude CLI。如果 `GOOSE_MODEL` 被设置为不在此列表中的值，则不会传递模型标志，Claude Code 将使用其默认值：

- `default`（opus）
- `sonnet`
- `haiku`

**权限模式（`GOOSE_MODE`）：**

| 模式 | Claude Code 标志 | 行为 |
|------|------------------|----------|
| `auto` | `--dangerously-skip-permissions` | 绕过所有权限提示 |
| `smart-approve` | `--permission-prompt-tool stdio` | 通过控制协议路由权限检查（按需提示） |
| `approve` | `--permission-prompt-tool stdio` | 通过控制协议路由权限检查（按需提示） |
| `chat` | （无） | Claude Code 的默认行为 |

:::tip Approve 模式集成
在 Claude Code 中使用 `approve` 或 `smart_approve` 模式时，goose 会把 Claude Code 的权限提示路由到 goose 的确认界面。这意味着：

- **敏感操作**（文件写入、shell 命令等）会在 goose 中触发批准提示
- **你在 goose CLI 或 Desktop 界面中直接**审查并批准/拒绝
- **被拒绝的操作**会被回传给 Claude Code，它会相应地调整

这在整个 goose 的所有提供方上提供了一致的权限体验，同时利用了 Claude Code 内置的安全检查。

使用 approve 模式的示例：
```bash
GOOSE_PROVIDER=claude-code GOOSE_MODE=approve goose session
```
:::

#### Cursor Agent 配置

| 环境变量 | 描述 | 默认值 |
|---------------------|-------------|---------|
| `GOOSE_PROVIDER` | 设置为 `cursor-agent` 以使用此提供方 | 无 |
| `CURSOR_AGENT_COMMAND` | Cursor Agent 命令的路径 | `cursor-agent` |

#### OpenAI Codex 配置

| 环境变量 | 描述 | 默认值 |
|---------------------|-------------|---------|
| `GOOSE_PROVIDER` | 设置为 `codex` 以使用此提供方 | 无 |
| `GOOSE_MODEL` | 要使用的模型（只有已知模型会传递给 CLI） | `gpt-5.2-codex` |
| `CODEX_COMMAND` | Codex CLI 命令的路径 | `codex` |
| `CODEX_REASONING_EFFORT` | 推理投入级别：`low`、`medium`、`high` 或 `xhigh`（`none` 仅在非 codex 模型如 `gpt-5.2` 上受支持） | `high` |
| `CODEX_ENABLE_SKILLS` | 启用 Codex skills：`true` 或 `false` | `true` |
| `CODEX_SKIP_GIT_CHECK` | 跳过 git 仓库要求：`true` 或 `false` | `false` |

**已知模型：**

以下模型会被识别，并通过 `-m` 标志传递给 Codex CLI。如果 `GOOSE_MODEL` 被设置为不在此列表中的值，则不会传递模型标志，Codex 将使用其默认值：

- `gpt-5.2-codex`（400K 上下文，自动压缩）
- `gpt-5.2`（400K 上下文，自动压缩）
- `gpt-5.1-codex-max`（256K 上下文）
- `gpt-5.1-codex-mini`（256K 上下文）

:::note 旧版模型
这些是 Codex CLI v0.77.0 支持的默认模型。要访问更旧或旧版模型，你可以直接运行 `codex -m <model_name>`，或在 Codex 的 `config.toml` 中配置它们。详情请参阅 [Codex CLI 文档](https://developers.openai.com/codex/cli)。
:::

**权限模式（`GOOSE_MODE`）：**

| 模式 | Codex 标志 | 行为 |
|------|------------|----------|
| `auto` | `--yolo` | 绕过所有批准和沙箱限制 |
| `smart-approve` | `--full-auto` | 工作区写入沙箱，仅在失败时批准 |
| `approve` | （无） | 交互式批准（Codex 默认行为） |
| `chat` | `--sandbox read-only` | 只读沙箱模式 |

#### Gemini CLI 配置

| 环境变量 | 描述 | 默认值 |
|---------------------|-------------|---------|
| `GOOSE_PROVIDER` | 设置为 `gemini-cli` 以使用此提供方 | 无 |
| `GEMINI_CLI_COMMAND` | Gemini CLI 命令的路径 | `gemini` |

### 工作原理

#### 系统提示词过滤

CLI 提供方会自动从系统提示词中过滤掉 goose 的扩展信息，因为这些 CLI 工具有自己的工具生态。这可以防止冲突，并确保与底层 CLI 工具的干净交互。

#### 消息转换

- **Claude Code**：将 goose 消息转换为带角色前缀（Human:/Assistant:）的文本内容块，与 Codex 和 Gemini CLI 类似
- **Codex**：将消息转换为带角色前缀（Human:/Assistant:）的简单文本提示词，与 Gemini CLI 类似
- **Cursor Agent**：将 goose 消息转换为 Cursor 的 JSON 消息格式，妥善处理工具调用和响应
- **Gemini CLI**：将消息转换为带角色前缀（Human:/Assistant:）的简单文本提示词

#### 响应处理

- **Claude Code**：解析流式 JSON 响应以提取文本内容和用量信息
- **Codex**：解析换行分隔的 JSON 事件以提取文本内容和用量信息
- **Cursor Agent**：解析 JSON 响应以提取文本内容和用量信息
- **Gemini CLI**：处理来自 CLI 工具的纯文本响应

### 错误处理

CLI 提供方依赖外部工具，因此请确保：

- CLI 工具已正确安装并在你的 PATH 中
- 认证保持有效
- 订阅额度未被超出
- 对于 Codex：你位于 git 仓库中，或设置 `CODEX_SKIP_GIT_CHECK=true`


---

CLI 提供方提供了一种通过 goose 界面使用现有 AI 工具订阅的方式，增添了会话管理和工作流集成能力。对于拥有现有 CLI 订阅、希望获得统一会话管理和 recipe 集成的用户来说，它们尤其有价值。

---

## Azure AI Foundry

> 原文：https://block.github.io/goose/docs/guides/azure-foundry-provider

`azure_foundry` 提供方将 goose 连接到 Azure AI Foundry 部署。它支持两种端点类型：

| 端点 | 推理面 |
|---|---|
| Foundry 项目：`https://<resource>.services.ai.azure.com/api/projects/<project>` | 部署发现加上发布方感知路由 |
| Foundry 资源：`https://<resource>.services.ai.azure.com` | OpenAI 模型经由 Responses，Claude 经由 Anthropic Messages，伙伴模型经由 Chat Completions |
| MaaS/无服务器：`https://<deployment>.<region>.models.ai.azure.com` | 对绑定到该端点的模型使用 Chat Completions |

对于项目端点，goose 使用 `GET /deployments` 发现部署。部署名称可以自定义；goose 使用返回的 `modelPublisher` 来选择协议，并使用 `modelName` 来解析模型元数据，例如上下文窗口。

资源端点不暴露项目部署发现。goose 按家族路由可识别的模型或部署名称：`gpt-5*` 和受支持的 o 系列模型使用 Responses，`claude-*` 使用 Anthropic Messages，其他名称使用 Chat Completions。当别名无法标识其底层模型家族时，请使用项目端点。

### 配置

| 变量 | 必需 | 描述 |
|---|---:|---|
| `AZURE_FOUNDRY_ENDPOINT` | 是 | 完整的 Foundry 项目或 MaaS 端点 |
| `AZURE_FOUNDRY_API_KEY` | 否 | API key；省略它则使用 Azure CLI 凭据 |
| `AZURE_FOUNDRY_MODEL` | 仅 MaaS | 绑定到所配置 MaaS 端点的模型 |
| `AZURE_FOUNDRY_AD_TOKEN` | 否 | 预先获取的 Microsoft Entra 访问令牌；优先于 API key |
| `AZURE_FOUNDRY_API_VERSION` | 否 | 部署发现 API 版本；项目端点默认为 `v1` |

运行 `goose configure`，选择 **Configure Providers**，然后选择 **Azure AI Foundry**。你也可以在启动 goose 之前设置这些变量：

```sh
export AZURE_FOUNDRY_ENDPOINT="https://my-resource.services.ai.azure.com/api/projects/my-project"
export AZURE_FOUNDRY_API_KEY="<key>"
goose session
```

对于 MaaS 端点：

```sh
export AZURE_FOUNDRY_ENDPOINT="https://my-deployment.eastus.models.ai.azure.com"
export AZURE_FOUNDRY_API_KEY="<key>"
export AZURE_FOUNDRY_MODEL="<model-bound-to-this-endpoint>"
goose session
```

MaaS 端点暴露单个已部署的模型。对于这些端点，`AZURE_FOUNDRY_MODEL` 是必需的。

### 认证

认证按以下顺序选择：

1. `AZURE_FOUNDRY_AD_TOKEN`
2. `AZURE_FOUNDRY_API_KEY`
3. Azure CLI 凭据

当既未配置令牌也未配置 key 时，请在启动 goose 之前使用 Azure CLI 登录：

```sh
az login
```

项目和资源端点会为 `https://ai.azure.com` 请求令牌。MaaS 端点会为 `https://ml.azure.com` 请求令牌。

### 协议路由

对于项目端点，goose 使用 Azure 返回的元数据路由每个部署：

- 发布方 `OpenAI` 且模型与 Responses 兼容（`gpt-5*` 和受支持的 o 系列）→ `/openai/v1/responses`
- 发布方 `Anthropic` → `/anthropic/v1/messages`
- 较旧的 OpenAI 模型和所有其他发布方 → `/openai/v1/chat/completions`

如果部署发现暂时不可用，则可识别的、与 Responses 兼容的 OpenAI 名称和 `claude-*` 名称会使用其原生面。其他名称使用 Chat Completions。

资源端点使用相同的推理面，但没有部署发现：可识别的模型家族名称会选择原生协议。这允许自定义 Agent 的 `model:` 声明直接选择诸如 `gpt-5.6-sol` 之类的部署，而无需通过规范模型解析重写名称。

MaaS 端点始终使用 `/v1/chat/completions` 以及由 `AZURE_FOUNDRY_MODEL` 配置的模型。

### 模型元数据与定价

deployments API 提供部署名称以及底层的 `modelName`、`modelVersion` 和 `modelPublisher`。goose 使用底层模型名称在其内置的模型目录中查找上下文窗口。显式的 `GOOSE_CONTEXT_LIMIT` 或会话覆盖仍然优先。

Azure 的定价取决于区域、SKU、优惠、部署类型和合同。deployments API 不提供可靠的按 token 价格，因此此提供方不会为发现的部署附加价格。

### 故障排查

#### 401 或 403

- 确保该 key 属于所配置的端点。
- 对于 Entra 认证，请再次运行 `az login`，并确认你的身份有权访问该 Foundry 项目。
- 不要将项目端点的 key 用于 MaaS 端点，反之亦然。

#### 未列出任何部署

- 确认端点包含 `/api/projects/<project>`。
- 确认该项目包含模型部署。
- 如果你的项目使用非默认的部署 API 版本，请设置 `AZURE_FOUNDRY_API_VERSION`。

#### 自定义部署名称的协议错误

刷新提供方的模型列表，以便 goose 能够获取 `modelPublisher`。没有部署元数据时，路由只能使用可识别的模型名称前缀。

---

## 漫游 Agent

> 原文：https://block.github.io/goose/docs/guides/roaming-agents

漫游 Agent 让你可以通过点对点连接从另一台机器访问正在运行的 goose agent —— 无需开放端口、无需 VPN、无需托管服务器。它构建在 [iroh](https://iroh.computer)（QUIC）之上，因此两台机器可以直接连接，或经由中继连接，通常无需任何防火墙更改。

:::warning 需要选择性构建
漫游是一项可选的实验性功能，**不包含在已发布的 goose 二进制文件中**。本指南中的每条命令都需要从源代码构建、并启用 `roaming` 特性的 goose：

```bash
cargo build --release -p goose-cli --features roaming
```

在默认构建上，`goose roam` 会报告无法识别的子命令。
:::

漫游被设计为**可嵌入的**：其传输层是一个独立的 Rust crate（`goose-roaming`），不依赖 goose 的 agent 内部实现；CLI 将其暴露为 `goose roam` 命令；并且有面向浏览器应用的 wasm 绑定。如果你在 goose 之上构建 —— 或者只是想要一个经过认证的 p2p ACP 传输层 —— 你可以直接使用这些相同的组件。Web 客户端（在接近文末处介绍）是一个完全构建在此公开接口之上的**参考客户端**。

你可以用它从另一台设备驱动你笔记本电脑上的 agent，把一次性任务交给远程 agent，把远程 agent 暴露给任何本地 ACP 客户端（比如编辑器），或者把 p2p agent 访问接入你自己的应用。

### 核心思想：漫游是一种 ACP 传输

漫游只做一件事：它提供一个**经过认证的点对点 [ACP](https://block.github.io/goose/docs/gdk/acp) 传输层**。主机运行 goose 真正的 ACP 服务器；连接的一方是 ACP 客户端。仅此而已。

因此，一切感觉「像会话」的东西，都只是碰巧运行在漫游连接之上的普通 ACP —— 而不是某种定制的漫游功能：

| 你想…… | 它只是 ACP…… | 命令 |
|--------------|----------------|---------|
| 列出远程的会话 | `session/list` | `roam delegate <target> --list-sessions` |
| 继续某个特定会话 | `session/load` | `roam delegate <target> --session <id> "…"` |
| 运行一个全新的一次性任务 | `session/new` + `session/prompt` | `roam delegate <target> "…"` |
| 从真实的 UI 驱动远程 agent | 完整的 ACP 面 | `roam bridge` → Zed 或其他 ACP 编辑器 |
| 快速交互式查看 | 内置 REPL | `roam connect` |

因为该连接承载了完整的 ACP 面，连接方可以枚举、创建和恢复主机的会话，而无需任何漫游专属协议。更高级的行为（已保存的对等方）位于传输层*之上*，并在下文描述。

:::note
漫游是一项可选的实验性功能。当 goose 使用 `roaming` 特性构建时（`cargo build -p goose-cli --features roaming`），它便可用。
:::

### 工作原理：卡片与相互接受

信任是一种**相互的、公钥的关系** —— 类似 WireGuard 或 SSH 的 known-hosts，并且刻意是基础设施层面的。每个节点有一个长期身份，并生成一张**连接卡片**：一个可分享的字符串，包含其公钥以及如何到达它（中继 URL）。*卡片中的任何内容都不是秘密* —— 拥有卡片并不授予任何访问权限。

要让对等方能够到达你，你们各自需要：

1. **交换卡片**（`goose roam id` 会打印你的卡片；通过任意渠道发送它）。
2. **接受对方的 key**（`goose roam peers accept …`）。

由于卡片只是一个字符串，它可以以任何方便的方式传递 —— 包括作为二维码：`goose roam id --qr` 和 `goose roam share --qr` 也会在终端中将卡片渲染为二维码，你可以用手机摄像头扫描（或直接用下文所述的 Web 客户端的摄像头扫描），而不必复制粘贴。

只有当**主机已接受拨号方的 key** 时，连接才会成功。传输层（iroh QUIC-TLS）证明每一方都持有其卡片中身份的私钥，因此没有人能冒充某个 key，而泄露的卡片也无法让任何人进入。不存在凭持有即授予访问权限的 bearer token。

```
┌────────────┐    swap cards     ┌────────────┐
│  Machine A │ ◀───────────────▶ │  Machine B │
│            │  each accepts the │            │
│  roam share│  other's key      │ roam connect│
│  (agent)   │ ◀═══ ACP over ══▶ │ /delegate/ │
└────────────┘   iroh + relay    │  bridge    │
                                 └────────────┘
```

每个连接客户端都获得其**自己的** agent，并通过完整的 ACP 面驱动其**自己的**会话。（对同一个实时会话进行同时多观察者的「共同驱动」是未来可能的功能，不属于此 ACP 传输模型的一部分。）

### 使用 CLI

#### 快速开始

假设机器 B 想要驱动机器 A 的 agent。两台机器都运行 `goose roam id`，并把各自打印出的卡片发送给对方。然后：

**在机器 A（主机）上：** 添加 B 的卡片并接受其 key。

```bash
goose roam peers add 'goose+roam://…B…' laptop-b
goose roam peers accept laptop-b          # grants control by default
goose roam share                          # serve to accepted peers
```

`share` 会持续运行，并也会打印 A 的卡片。agent 在启动 `share` 时所在的目录中运行（可用 `--cwd <dir>` 覆盖）；连接方自己的目录始终被忽略。

**在机器 B（客户端）上：** 添加 A 的卡片并连接。

```bash
goose roam peers add 'goose+roam://…A…' laptop-a
goose roam connect laptop-a
```

你会得到一个交互式提示符，用来驱动机器 A 上的 agent。输入一条消息并按回车；用 `/quit` 或 Ctrl-D 退出。

`connect` 是一个极简的内置聊天循环 —— 便于快速做健全性检查。对于实际工作，更推荐 `bridge`（从完整的 ACP 客户端驱动远程 agent）或 `delegate`（可脚本化的一次性任务）。

对于常见的「配对新设备」场景，还有一个一步到位的辅助命令：`goose roam pair` 会把本节点的卡片显示为二维码，从 stdin 读取设备的卡片，并一次性保存并接受它（相当于 `peers add` + `peers accept`）。

:::tip
请通过带外方式比对 `roam id` / `peers accept` 显示的简短**指纹**（例如朗读出来），以确保你接受的是你想要的 key。
:::

#### 一次性委派

要发送单个任务并取回答案 —— 没有交互式会话：

```bash
goose roam delegate 'goose+roam://…' "Summarize the last 5 commits in this repo."
```

远程 agent 用它自己的工具运行该任务，并打印其最终响应。`delegate` 是一个轻量的 ACP 客户端，因此它也能与远程现有的会话协作 —— 底层全是普通 ACP：

```bash
# List the remote agent's sessions (session/list)
goose roam delegate 'goose+roam://…' --list-sessions

# Continue a specific session instead of starting fresh (session/load)
goose roam delegate 'goose+roam://…' --session <SESSION_ID> "Now fix the first failure."
```

#### 桥接到任何 ACP 客户端

`connect` 和 `delegate` 内嵌了 goose 自己的 ACP 客户端。`bridge` 做的恰恰相反：它把远程 agent 暴露为一个**本地 ACP 端点**，因此任何 ACP 客户端 —— Zed 或其他编辑器 —— 都能像它运行在本地一样驱动它。它本身不运行任何 UI，也不运行任何 agent；它在本地客户端和远程 agent 之间透明地代理 ACP 字节。

通过 stdio 桥接（默认 —— 适用于把 goose 作为子进程启动的客户端）：

```bash
goose roam bridge 'goose+roam://…'
```

将你的 ACP 客户端配置为运行 `goose roam bridge '<card>'` 作为其 agent 命令。它会在进程的 stdin/stdout 上讲 ACP，每个请求都会被转发给远程 agent。

或者通过本地 TCP 端口桥接，适用于连接到某个地址的客户端：

```bash
goose roam bridge laptop --listen 127.0.0.1:8900 --allow-remote-clients
```

这会在该地址上接受单个 ACP 连接，并将其代理到远程 agent。已保存的对等方名称在这里同样适用。之所以需要显式选择启用，是因为 TCP 监听器不对其客户端进行认证：即使在环回地址上，另一个本地用户或进程也能连接并获取远程 agent 的 ACP 访问权限。仅在你能控制谁能连接到该监听器的可信主机上使用 TCP 桥接。

由于默认的 `share` 提供完整的 ACP 面，桥接的客户端能获得一切 —— 它可以列出、创建和加载主机的会话，而不仅仅是一个预先选定的会话。

:::note
一个 bridge 服务一个客户端连接。远程主机仍然运行该 agent，施加其自己的工作目录，并对连接进行授权。
:::

### 把漫游嵌入你自己的应用

上述一切都是构建在 **`goose-roaming` crate**（`crates/goose-roaming`）之上的，你可以直接使用它。该 crate 刻意做到**对 goose 核心零依赖** —— 它对 agent 或会话一无所知，只知道身份、信任和经过认证的字节流 —— 因此你可以把它嵌入任何 Rust 应用，无论是否配合 goose。

使用方接触到的接口：

- **`RoamingIdentity`** —— 一个持久化的 ed25519 节点密钥，其公钥部分*就是* iroh 端点 id（`RoamingIdentity::generate()` 用于临时身份，`default_key_path` 用于 goose 使用的磁盘身份）。
- **`RoamingConfig`** —— 一个节点的构建器：`RoamingConfig::new(identity)` 加上诸如 `.with_relay(RelaySettings::…)` 和 `.with_bind_addr(addr)` 之类的链式方法。默认使用 iroh 的公共中继和一个**空的白名单**（不接受任何人），因此安全默认值已内置。
- **`RoamingNode`** —— 节点本身。`RoamingNode::bind(config)` 绑定端点；`node.share(server)` 把 agent 托管给已接受的对等方；`node.connect(&card, label)` / `node.connect_with_addr(addr, label)` 拨号一个远程并返回一个 `RoamingClientStream`（使用 `.into_futures_io()` 获得普通的异步读/写两半）；`node.card()` 生成可分享的卡片。
- **`AcpStreamServer`** —— 你的主机侧实现以接入「agent」的 trait。它有两个方法 —— `serve_stream`（在一个已接受对等方的已授权流上驱动你的协议）和 `agent_id`（在握手 ack 中发送的显示 id）—— 这就是整个集成接缝。goose-cli 的 `FullAcpBridge` 通过把流交给 goose 真正的 ACP `serve` 来实现它；你的应用可以服务任何东西。
- **`TrustBook`** —— 已接受对等方 key 的相互白名单，具有持久化存储和故障关闭（fail-closed）的重载。`node.trust()` 给你一个句柄，用于在运行时接受或吊销 key。
- **`ConnectionCard`** —— 非秘密的身份 + 可达性字符串（`goose+roam://…`），具有 `encode()` / 解析以及用于带外验证的简短 `fingerprint()`。

一个最小的端到端示例（摘自 `crates/goose-roaming/examples/echo_roundtrip.rs`，它在单个进程内运行两端 —— `cargo run -p goose-roaming --example echo_roundtrip`）：

```rust
use std::sync::Arc;
use goose_roaming::{
    AcpStreamServer, EndpointId, RoamingConfig, RoamingIdentity, RoamingNode,
};

// Your "agent": anything that can serve an authorized byte stream.
struct EchoServer;

impl AcpStreamServer for EchoServer {
    fn serve_stream(
        &self,
        _client: EndpointId,
        recv: Box<dyn futures::io::AsyncRead + Send + Unpin>,
        send: Box<dyn futures::io::AsyncWrite + Send + Unpin>,
    ) -> futures::future::BoxFuture<'static, anyhow::Result<()>> {
        Box::pin(async move { /* echo recv back on send … */ Ok(()) })
    }
    fn agent_id(&self) -> String { "echo-agent".to_string() }
}

async fn demo() -> anyhow::Result<()> {
    // Host: bind a node and share the agent to accepted peers.
    let host = RoamingNode::bind(RoamingConfig::new(RoamingIdentity::generate())).await?;
    host.share(Arc::new(EchoServer)).await?;
    println!("share this card: {}", host.card().encode()?);

    // Client: a separate node dials the host's card.
    let client = RoamingNode::bind(RoamingConfig::new(RoamingIdentity::generate())).await?;

    // Trust step: the HOST must accept the client's key, or the dial is refused.
    host.trust().lock().await.accept(&client.endpoint_id());

    let stream = client.connect(&host.card(), Some("example".into())).await?;
    let (send, recv, _conn) = stream.into_futures_io();
    // … speak your protocol (ACP, or anything) over send/recv …
    Ok(())
}
```

给集成者的几点说明：

- **要暴露一个完整的 goose 后端**，你不必自己实现 `AcpStreamServer`：`goose serve --roam` 在单个进程内运行 goose 的常规 agent 服务器*并*通过 roam 暴露它。它以无头方式工作，把其卡片写入 `<data-dir>/roam/serve.json`，并在启动时打印它。
- **对于浏览器应用**，同一传输层可编译为 WebAssembly。wasm 绑定（`@aaif/goose-roam-web`，由 [goose-mobile 仓库](https://github.com/aaif-goose/goose-mobile/tree/main/mobile-web)中的 `goose-roaming-web` crate 构建）向 JavaScript 暴露一个 `RoamClient` —— 生成身份、打印你的卡片、拨号主机的卡片，并在浏览器标签页内驱动 ACP，中间没有任何服务器。下面的 Web 客户端就是构建在这些绑定之上的。
- 该 crate 的 [README](https://github.com/aaif-goose/goose/tree/main/crates/goose-roaming) 更深入地涵盖了设计决策（为什么由主机控制工作目录、为什么信任是全有或全无的，等等）。

### Web 客户端：一个参考浏览器客户端

托管在 [aaif-goose.github.io/goose-mobile](https://aaif-goose.github.io/goose-mobile/) 的 Web 客户端是一个**构建在上述组件之上的参考客户端**：传输层使用 `@aaif/goose-roam-web` wasm 绑定，ACP 协议层使用 goose 的 `ui/sdk` `GooseClient`。浏览器标签页本身就是一个 roam 对等方：编译为 WebAssembly 的 iroh 在标签页内运行，并通过相同的中继、以相同的相互 key 信任进行连接 —— 中间没有服务器，也没有任何流量经过该站点的 origin。它所能做的一切，你自己的应用都能用相同的绑定做到。

配对的工作方式与其他任何对等方完全相同。标签页生成自己的身份并显示其卡片；你在主机上接受它一次：

```bash
goose roam peers accept 'goose+roam://…tab…' phone
```

要把主机的卡片弄进浏览器，请粘贴它 —— 或运行 `goose roam share --qr` 并用 Web 客户端的摄像头扫描二维码。

连接后，标签页可以列出并打开主机的会话、启动新会话、流式接收响应、引导正在运行的轮次，并按项目对会话分组。你可以同时连接多个主机；它们的会话会出现在一个合并的列表中。

源代码位于 [goose-mobile 仓库](https://github.com/aaif-goose/goose-mobile/tree/main/mobile-web)（`mobile-web/`）—— 如果你想自己托管它，那里的 README 有构建细节（它构建为一个静态站点）。

### 已保存的对等方

把对等方的卡片保存在一个昵称下，这样你就不必每次都粘贴卡片。已保存的卡片只是一个通讯录条目 —— 它**不会**让该对等方连接到*你*（为此请使用 `peers accept`）：

```bash
goose roam peers add 'goose+roam://…' laptop   # save to the address book
goose roam connect laptop
goose roam delegate laptop "run the tests and report failures"

goose roam peers list      # show saved peers + which keys you accept
goose roam connections     # show observed connections
goose roam id              # print this node's connection card
```

### 控制谁可以连接

访问权限**仅**通过接受对等方的公钥来授予 —— 不存在凭持有即生效的 bearer token。你可以通过已保存的名称或内联卡片来接受一个对等方：

```bash
goose roam peers accept laptop                    # accept a saved peer
goose roam peers accept 'goose+roam://…'          # accept an inline card (also saves it)
goose roam peers accept 'goose+roam://…' laptop   # accept + save under a nickname in one go

goose roam peers list                             # see who is accepted
goose roam peers revoke laptop                    # stop accepting (name, card, or raw id)
```

已接受的对等方获得 goose 的**完整 ACP 面** —— 它可以在这台机器上驱动自己的会话（new/list/load/prompt），这实际上等同于远程 shell 访问。不存在更细粒度的角色：接受是全有或全无的。

接受是**持久的**且**实时的**：它存储在磁盘上，而运行中的 `share` 会在每次连接时重新读取它，*并且*轮询信任文件（大约每两秒一次），以便对已经打开的连接强制执行它。因此，即使面对一个实时对等方，吊销也能在数秒内生效 —— share 会强制关闭它的任何已打开连接。两端都无需重启。

由于信任以对等方的公钥为键，且传输层以密码学方式认证该 key，卡片可以通过任何渠道分享 —— 它不是秘密，泄露的卡片也无法让任何人进入。

:::warning
接受一个对等方会授予**完全控制权** —— 该对等方可以运行 agent 的工具，包括其 shell。只接受你信任的机器和人，并通过带外方式验证指纹。
:::

### 让 agent 能触达其他 agent

启用漫游特性后，goose 自身可以委派给其他 agent。你让它这么做，它就能通过其 shell 运行 `goose roam delegate <peer> "<task>"` —— 例如，「把这个委派给我的工作笔记本电脑，并总结它的发现。」它会发送一个自包含的任务，并转达响应。

由于已保存的对等方只是一个通讯录，agent 可以发现它有哪些可用的远程（`goose roam peers list`），并把工作路由到正确的那一个 —— 例如在拥有工具链的机器上运行构建，然后带回结果。每次委派都是一个响应有界的自包含任务，因此这可以组合成多机器工作流，而无需任何共享状态。

### 说明与限制

- 当 NAT 打洞成功时，对等方直接连接，否则回退到中继。默认情况下，漫游使用一组由 goose 管理的 iroh 中继（每个区域一个 —— 不是 iroh 的共享公共中继）；可通过 `GOOSE_ROAM_RELAYS` 配置键或环境变量覆盖它们，以指向你自己的部署。
- `connect`、`delegate` 和 `bridge` 都接受已保存的对等方名称或原始的 `goose+roam://…` 卡片。请记住，对等方也必须已接受你的 key。
- 发送给**在 share 进程中**有运行在途的会话的消息，会成为对该运行的引导。运行在主机上*另一个*进程中的循环（另一个 CLI，或未启用 roam 的主机）无法被远程引导 —— Web 客户端会检测到这一点，并在发送前发出警告。
- 吊销一个对等方会在数秒内强制关闭其连接，并在其下一步丢弃任何在途轮次；无法开始新工作。一个狭窄的残余情况：某个工具已经启动的操作系统进程（比如一条长 shell 命令）可能会运行至完成 —— 吊销会停止该 agent，但不会停止它已经 fork 出的进程。
- 在 macOS 上，如果某个会话在连接时仍显得挂起，请设置 `GOOSE_DISABLE_KEYRING=1` 以完全跳过钥匙串。
