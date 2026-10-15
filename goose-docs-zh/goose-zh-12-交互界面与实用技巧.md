# goose 官方文档中文手册：第 12 章　交互界面与实用技巧

## 基于 MCP Apps 的丰富交互式聊天

> 原文：https://block.github.io/goose/docs/guides/interactive-chat

<p className={styles.pageDescription}>
  goose Desktop 支持通过扩展把纯文本回复转变为图形化、可交互的体验。无需再逐条阅读列表和描述，你可以直接在对话中点击、浏览并与 UI 组件交互。
</p>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>📚 文档与指南</h2>
  <div className={styles.cardGrid}>
    <Card
      title="构建 MCP Apps"
      description="逐步教程：创建可在 goose Desktop 中渲染的交互式 UI 应用程序。"
      link="https://block.github.io/goose/docs/tutorials/building-mcp-apps"
    />
    <Card
      title="使用 MCP Apps"
      description="启动独立应用，并直接在 goose Desktop 对话中渲染交互式 UI。"
      link="https://block.github.io/goose/docs/guides/interactive-chat/mcp-ui"
    />
    <Card
      title="Auto Visualiser 扩展"
      description="在 goose 中自动生成交互式数据可视化。"
      link="https://block.github.io/goose/docs/mcp/autovisualiser-mcp"
    />
  </div>
</div>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>🎥 视频</h2>

  <VideoCarousel
    id="mcp-apps-videos"
    videos={[
      {
        type: "iframe",
        src: "https://youtube.com/embed/QcojQ3Fwqsw",
        title: "什么是 MCP Apps？",
        description:
          "MCP Apps 是什么，以及它们如何在 goose 中渲染交互式 UI",
        duration: "1:53",
      },
    ]}
  />
</div>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>📝 精选博客文章</h2>
  <div className={styles.cardGrid}>
    <Card
      title="从 MCP-UI 到 MCP Apps：交互式 Agent UI 的演进"
      description="一份面向 MCP Apps 的实用迁移指南：4 个关键变化、哪些地方会失效，以及为什么这次转变很重要。"
      link="https://block.github.io/goose/blog/2026/01/22/mcp-ui-to-mcp-apps"
    />
    <Card
      title="goose 落地 MCP Apps"
      description="goose 提前支持 MCP Apps 规范草案，与交互式 UI 的新兴标准保持一致。"
      link="https://block.github.io/goose/blog/2026/01/06/mcp-apps"
    />
  </div>
</div>

---

## 使用 MCP Apps

> 原文：https://block.github.io/goose/docs/guides/interactive-chat/mcp-ui

用 MCP Apps 构建的扩展让 goose Desktop 能够提供交互式且引人入胜的用户体验。无需阅读文本回复并输入提示词，你可以与图形化、可点击的 UI 进行交互。

:::info MCP Apps 是官方规范
[MCP Apps](https://block.github.io/goose/docs/tutorials/building-mcp-apps) 是面向交互式 UI 的官方 MCP 规范。新的交互式扩展请使用 MCP Apps。
:::

:::warning 实验性功能
本主题描述的功能属于实验性功能，正在积极开发中。其行为和支持情况可能会在未来的版本中发生变化。
:::

MCP Apps 通过官方 [MCP Apps 规范](https://github.com/modelcontextprotocol/ext-apps)为 goose 带来交互式界面。取决于具体扩展，应用可以在独立的沙箱窗口中启动，也可以嵌入到你的聊天窗口中。

#### 在独立窗口中启动应用

某些 MCP Apps 可以在它们自己的窗口中启动，让你无需向 goose 发送消息就能直接进入界面。

1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏
2. 在侧边栏中点击 `Apps`
3. 浏览你可用的 MCP Apps
4. 点击 `Launch` 在新窗口中启动一个应用

:::info Apps 扩展
要在侧边栏中看到 `Apps` 页面，必须先在 `Extensions` 页面中启用 [Apps 扩展](https://block.github.io/goose/docs/mcp/apps-mcp)。你也可以用它创建自定义的独立应用。
:::

`Apps` 页面会显示你使用 Apps 扩展创建的自定义 HTML 应用、导入的 HTML 应用，以及来自已启用 MCP Apps 扩展的应用。应用界面允许你点击按钮、填写表单或使用其他控件。应用可以通过 MCP 调用工具并读取资源（前提是已通过 CORS 启用），但无法与 goose 通信（例如通过聊天）。

##### 导入 HTML 应用

导入由 Apps 扩展创建并分享给你的应用。

1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏
2. 在侧边栏中点击 `Apps`
3. 点击 `Import App`，在文件系统中浏览到该应用的 `.html` 文件，然后点击 `Open`

#### 在聊天窗口中使用应用

当 goose 调用某个返回 UI 的工具时，某些 MCP Apps 会直接在你的对话中渲染。交互式界面会内联出现在聊天中，让你无需离开对话流程即可进行选择、填写表单或触发操作。

如有需要，你只需询问 goose 该 UI 能否在聊天窗口中加载。

<div style={{ width: '100%', maxWidth: '800px', margin: '0 auto' }}>
  <video 
    controls 
    playsInline
    style={{ 
      width: '100%', 
      aspectRatio: '2876/2160',
      borderRadius: '8px'
    }}
  >
    <source src={require('@site/static/videos/plan-trip-demo.mp4').default} type="video/mp4" />
    你的浏览器不支持 video 标签。
  </video>
</div>

### 面向扩展开发者

为你自己的扩展添加交互能力：

- [构建 MCP Apps](https://block.github.io/goose/docs/tutorials/building-mcp-apps) - 分步教程（推荐）
- [MCP Apps SDK 与规范](https://modelcontextprotocol.github.io/ext-apps/api/)
- [MCP Apps SDK 指南](https://mcpui.dev/guide/introduction)

---

## 自定义侧边栏

> 原文：https://block.github.io/goose/docs/guides/desktop-navigation

:::info 仅桌面版
侧边栏自定义仅在 goose Desktop 中可用。
:::

侧边栏是你在 goose Desktop 中在页面之间导航的方式：Home、Chat、Recipes、Apps、Scheduler、Extensions 和 Settings。你可以自定义它的外观、位置和行为，以贴合你的工作方式。

要访问这些设置：

1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏
2. 在侧边栏中点击 `Settings`
3. 点击 `App` 标签页
4. 滚动到 **Navigation** 部分

### 样式

选择侧边栏如何显示其项目。

| 样式 | 说明 |
|-------|-------------|
| **Tile**（默认） | 带标签的大图标，以网格排列。适合快速进行视觉扫描。 |
| **List** | 紧凑的单列列表。占用空间更少，一次显示更多项目。 |

:::note
在较小窗口（宽度小于 700px）中使用 List 样式时，侧边栏会自动折叠为仅图标。
:::

### 位置

把侧边栏移动到窗口的任意边缘。

| 位置 | 说明 |
|----------|-------------|
| **Left**（默认） | 窗口左侧的垂直侧边栏 |
| **Right** | 窗口右侧的垂直侧边栏 |
| **Top** | 沿窗口顶部的水平栏 |
| **Bottom** | 沿窗口底部的水平栏 |

### 模式

控制侧边栏打开时你的内容会发生什么。

| 模式 | 说明 |
|------|-------------|
| **Push**（默认） | 侧边栏占用空间，你的内容移动以腾出位置。侧边栏在你工作时保持可见。 |
| **Overlay** | 侧边栏浮在你的内容之上，不移动任何内容。点击外部或进行导航即可将其关闭。 |

:::note
在 Overlay 模式下，Style 和 Position 设置不可用。侧边栏始终以全屏瓦片式覆盖层的形式出现。
:::

### 自定义项目

你可以在导航设置的 **Customize Items** 部分中重新排序和隐藏侧边栏中的项目。

- **拖动项目** 以重新排序
- 点击 **眼睛图标** 以显示或隐藏单个项目

点击 `Reset to defaults` 以恢复原始顺序和可见性。

### 切换侧边栏

无需打开 Settings 即可显示或隐藏侧边栏：

- **菜单栏：** 转到 **View → Toggle Navigation**
- **键盘快捷键：** 快捷键显示在菜单项旁边，可在 `Settings` > `Keyboard` 中自定义

侧边栏的打开/关闭状态会跨会话被记住。

---

## 终端集成

> 原文：https://block.github.io/goose/docs/guides/terminal-integration

对话直接在 shell 提示符中进行。无需切换到单独的 REPL 会话，留在终端里，需要时调用 goose 即可。

### 设置

<Tabs groupId="shells">
<TabItem value="zsh" label="zsh" default>

添加到 `~/.zshrc`：
```bash
eval "$(goose term init zsh)"
```

</TabItem>
<TabItem value="bash" label="bash">

添加到 `~/.bashrc`：
```bash
eval "$(goose term init bash)"
```

</TabItem>
<TabItem value="fish" label="fish">

添加到 `~/.config/fish/config.fish`：
```fish
goose term init fish | source
```

</TabItem>
<TabItem value="nu" label="Nushell">

添加到 `~/.config/nushell/config.nu`：
```nu
let goose_term_init = ($nu.cache-dir | path join "goose-term-init.nu")
^goose term init nu | save --force $goose_term_init
source $goose_term_init
```

</TabItem>
<TabItem value="powershell" label="PowerShell">

添加到 `$PROFILE`：
```powershell
Invoke-Expression (goose term init powershell)
```

</TabItem>
</Tabs>

重启终端或 source 配置文件，就完成了！

### 用法

只需输入 `@goose`（或简写 `@g`），后面跟上你的问题：

```bash
npm install express
    npm ERR! code EACCES
    npm ERR! permission denied

@goose "how do I fix this error?"
```

goose 会自动看到你自上次提问以来运行过的命令，因此你无需解释自己一直在做什么。如果你的提示词包含 `?`、`*` 或 `'` 等特殊字符，请用引号把它括起来：

```bash
@goose "what's in this directory?"
@g "analyze the error: 'permission denied'"
```

### 命名会话

默认情况下，每个终端都有自己的 goose 会话，该会话会一直持续到你关闭它为止。命名会话让你可以跨终端重启继续对话，并在多个窗口之间共享上下文。

<Tabs groupId="shells">
<TabItem value="zsh" label="zsh" default>

```bash
eval "$(goose term init zsh --name my-project)"
```

</TabItem>
<TabItem value="bash" label="bash">

```bash
eval "$(goose term init bash --name my-project)"
```

</TabItem>
<TabItem value="fish" label="fish">

```fish
goose term init fish --name my-project | source
```

</TabItem>
<TabItem value="nu" label="Nushell">

```nu
let goose_term_init = ($nu.cache-dir | path join "goose-term-init.nu")
^goose term init nu --name my-project | save --force $goose_term_init
source $goose_term_init
```

</TabItem>
<TabItem value="powershell" label="PowerShell">

```powershell
Invoke-Expression (goose term init powershell --name my-project)
```

</TabItem>
</Tabs>

命名会话会持久化在 goose 的数据库中，因此它们随时可用，即使重启电脑后也一样。稍后重新打开并运行相同的命令即可继续：

```bash
# Start debugging
eval "$(goose term init zsh --name auth-bug)"
@goose help me debug this login timeout

# Close terminal, come back later
eval "$(goose term init zsh --name auth-bug)"
@goose "what was the solution we discussed?"
# Continues the same conversation with context
```

### 默认处理器

如果你的 shell 无法解析某条命令，而你想让 goose 来应答，请使用 `--default`。

<Tabs groupId="default-shells">
<TabItem value="zsh" label="zsh" default>

```bash
eval "$(goose term init zsh --default)"
```

</TabItem>
<TabItem value="bash" label="bash">

```bash
eval "$(goose term init bash --default)"
```

</TabItem>
<TabItem value="nu" label="Nushell">

```nu
let goose_term_init = ($nu.cache-dir | path join "goose-term-init.nu")
^goose term init nu --default | save --force $goose_term_init
source $goose_term_init
```

</TabItem>
</Tabs>

### 在提示符中显示上下文状态

把 `goose term info` 添加到你的提示符中，即可在终端 goose 会话期间看到你已使用了多少上下文以及当前激活的是哪个模型。

<Tabs groupId="shells">
<TabItem value="zsh" label="zsh" default>

```bash
PROMPT='$(goose term info) %~ $ '
```

</TabItem>
<TabItem value="bash" label="bash">

```bash
PS1='$(goose term info) \w $ '
```

</TabItem>
<TabItem value="fish" label="fish">

```fish
function fish_prompt
    goose term info
    echo -n ' '(prompt_pwd)' $ '
end
```

</TabItem>
<TabItem value="nu" label="Nushell">

```nu
$env.PROMPT_COMMAND = {|| $"(goose term info) (pwd)> " }
```

</TabItem>
<TabItem value="powershell" label="PowerShell">

```powershell
function prompt {
    $gooseInfo = & goose term info
    "$gooseInfo $(Get-Location) PS> "
}
```

</TabItem>
</Tabs>

你的终端提示符现在会显示活动 goose 会话的上下文使用量和模型名称（为便于阅读而缩短）。例如：

```bash
●●○○○ sonnet ~/projects $
```

### goose 命令的 Shell 补全

`@goose` 会基于你的命令历史提供上下文感知的协助。要启用 goose CLI 命令（如 `goose session`、`goose run` 等）的 Tab 补全，请参阅 [shell 补全文档](https://block.github.io/goose/docs/guides/goose-cli-commands#completion)。

### 故障排除

**goose 看不到最近的命令：**
如果你运行了命令，但 goose 说看不到任何最近的活动，请检查终端集成是否已正确[在你的 shell 配置中设置](#setup)。
你也可以检查当前终端中 goose 会话的 id：
```bash
# Check if session ID exists
echo $AGENT_SESSION_ID
# Should show something like: 20251209_151730
```
```nu
# Nushell
$env.AGENT_SESSION_ID
# Should show something like: 20251209_151730
```
要在多个终端窗口之间共享上下文，请改用[命名会话](#named-sessions)。

**会话变得太满**（提示符显示 `●●●●●`）：
如果 goose 的响应变慢或触及上下文上限，请在终端中启动一个新的 goose 会话。新的 goose 会话会看到你的命令历史，但看不到上一个会话的对话历史。
```bash
# Start a new goose session in the same shell
eval "$(goose term init zsh)"
```
```nu
# Nushell
let goose_term_init = ($nu.cache-dir | path join "goose-term-init.nu")
^goose term init nu | save --force $goose_term_init
source $goose_term_init
```

---

## 文件访问与管理

> 原文：https://block.github.io/goose/docs/guides/file-management

作为一个自主 Agent，goose 被设计为按照指定指令执行任务。这通常涉及处理本地文件——既包括找到要处理的正确文件，也包括安全地修改它们。

本指南介绍如何在 goose 中高效地访问和引用文件。它还包含安全文件操作的基本最佳实践，例如监控更改并在必要时回退它们，以维护代码库的完整性。

### 文件访问

#### goose Desktop 中的快速文件搜索

goose Desktop 包含一个模糊文件搜索功能，让你可以轻松地在聊天界面中引用文件，而无需手动浏览文件系统对话框。该功能帮助你快速找到文件并把它们加入发给 goose 的消息中。

1. 在聊天输入框中输入 `@` 打开文件搜索框
2. 继续输入，使用不区分大小写的模糊匹配来筛选文件（例如 `@readme`、`@config.js`、`@src/main`）

   浏览结果：
   - 使用方向键（↑/↓）在搜索结果中移动
   - 点击或按 `Enter` 把选中的文件路径插入到你的消息中
   
3. 就这样！准备好后，把你的消息发送给 goose

:::info
要关闭搜索框而不选择文件，请按 `Esc` 或点击聊天输入框。
:::

**智能功能：**
- **模糊匹配**：智能匹配部分文本，并优先匹配词边界处的命中
- **高亮结果**：在搜索结果中高亮显示匹配到的字符
- **性能优化**：最多扫描 5 层目录深度，并带有智能过滤
- **自动过滤**：自动排除常见目录，如 `.git`、`node_modules`、`__pycache__`、`target`、`dist` 和 `build`
- **隐藏文件夹支持**：包含重要的配置目录，如 `.github`、`.vscode`、`.idea`、`.config`，以及其他 CI/CD 文件夹（`.circleci`、`.gitlab`、`.azure`、`.jenkins`）
- **跨平台**：从用户目录开始搜索（macOS 上为 `/Users`，Windows 上为 `C:\Users`，Linux 上为 `/home`）
- **视觉指示**：用清晰的图标区分文件和目录

### 文件管理最佳实践

#### 版本控制

始终使用像 Git 这样的版本控制系统来跟踪代码库的更改。这可以防止意外覆盖，并让你轻松回退到之前的状态。确保在对代码库运行 goose 之前先提交更改。使用分支把实验性更改与主代码库分开。

#### 验证与测试

在 goose 修改任何文件之前和之后，都要实施验证和测试步骤。运行你的单元测试来验证 goose 所做的更改。使用预发布环境来确保更改能与整个系统良好集成。

#### 变更审查

手动审查或使用自动化代码审查来确保生成代码或更改的质量。集成 diff 工具之类的工具来可视化 goose 所做的更改。与团队成员或 CI/CD 流水线一起实施审查流程。

#### 代码库组织

把你的代码库组织成定义良好的模块或子目录，以便高效管理它们。使用模块化方法隔离 goose 需要访问的部分代码。你也可以提供你希望 goose 处理的特定目录或文件路径。

---

## 代码库分析

> 原文：https://block.github.io/goose/docs/guides/codebase-analysis

Analyze 平台扩展提供了一个 `analyze` 工具，帮助你理解代码结构、跟踪符号使用情况，并探索整个代码库中的调用图。它默认启用，并支持[多种编程语言](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/agents/platform_extensions/analyze/languages.rs)的文件类型。

<details>
<summary>分析示例：跨文件跟踪一个函数</summary>

**提示词：**

"Show me the call graph for the authenticate function"

**输出：**

:::info 桌面版
我将分析 `authenticate` 函数在你的代码库中是如何被使用的。

根据我的分析，以下是 `authenticate` 函数在你的代码库中的使用方式：

##### 函数定义
`authenticate` 函数定义在 `auth.py` 的第 15 行。它接收 username 和 password 参数，并处理用户身份验证。

##### 传入调用（调用 authenticate 的函数）
- `api.py:25` 中的 **login_handler()** - 处理登录请求的 API 端点
- `admin.py:102` 中的 **admin_login()** - 面向管理员用户的特殊身份验证流程
- `tests/test_auth.py:45` 中的 **test_auth()** - 身份验证的测试用例

##### 传出调用（authenticate 调用的函数）
- `db.py:102` 中的 **validate_credentials()** - 对照数据库检查凭据
- `logger.py:45` 中的 **log_attempt()** - 记录身份验证尝试
- `security.py:78` 中的 **check_rate_limit()** - 防止暴力破解攻击

这表明 `authenticate` 是你身份验证流程中的一个核心函数，被多个入口点调用，并依赖数据库验证、日志记录和安全检查。
:::

</details>

### 分析模式

`analyze` 工具有三种运行模式——Structure、Semantic 和 Focus——取决于你是在分析目录、文件还是符号。通过自然语言或直接命令并配合[参数](#common-parameters)来调用它。

#### 理解项目结构

通过分析一个目录来获得代码库的结构概览——理解项目组织方式、识别大文件，并查看代码库指标。

**自然语言：**
- "Can you analyze the structure of my src/ directory?"
- "Give me an overview of this project's code structure"
- "What's the main entry point of this Python project?"

**直接命令：**
```bash
# Get overview with default depth (3 levels)
analyze path="src/"

# Get overview limited to 2 subdirectory levels
analyze path="." max_depth=2
```

#### 检查单个文件

获取单个文件的语义细节——查看它的函数、类和导入，以理解结构并找到具体的实现。

**自然语言：**
- "main.py 里有哪些函数？"
- "展示 src/utils.py 的结构"

**直接命令：**
```bash
# Get file details
analyze path="main.py"

# Analyze specific file
analyze path="src/utils.py"
```

#### 跨文件跟踪一个符号

聚焦于某个特定的函数、类或方法，查看它在哪里定义以及如何跨文件被调用——这对重构和调试很有用。

**自然语言：**
- "追踪 authenticate 函数的依赖关系"
- "展示 UserClass 的调用图"

**直接命令：**
```bash
# Track function usage
analyze path="src/" focus="authenticate"

# Track with deeper call chains
analyze path="." focus="UserClass" follow_depth=3
```

### 常用参数

| 参数 | 默认值 | 说明 |
|-----------|---------|-------------|
| `path` | None（必填） | 要分析的文件或目录的绝对路径或相对路径 |
| `focus` | None | 要跟踪的符号名称。对于跨文件跟踪，`path` 必须是目录。 |
| `follow_depth` | 2 | 从聚焦符号开始追踪多少步（0=定义位置，1=直接调用者/被调用者，2=它们的调用者/被调用者，以此类推）。与 `focus` 参数一起使用。 |
| `max_depth` | 3 | 当 `path` 是目录时要分析的子目录层数（0=不限制） |
| `force` | false | 接收完整的分析结果（否则，当结果超过 50,000 个字符时只显示一条警告消息） |

### 最佳实践

#### 处理大量输出

如果分析结果超过 50,000 个字符，工具会返回一条警告消息而不是分析结果。管理大量输出的选项：

- **使用 `force=true`** 绕过警告并查看完整输出（可能会消耗大量对话上下文）
- **缩小范围**，只分析某个特定的子目录或文件
- **降低深度**，对目录使用 `max_depth=1` 或 `max_depth=2`
- **委托给[子代理](https://block.github.io/goose/docs/guides/context-engineering/subagents)**进行分析和总结，而不填满你的对话历史，例如："使用一个子代理分析整个 src/ 目录并总结主要组件"

#### 性能提示

- 先从小范围（特定文件或子目录）开始，再分析整个项目
- 使用 `max_depth=1` 或 `max_depth=2` 来限制目录遍历深度
- 使用 `.gitignore` 文件把不必要的文件排除在分析之外，例如 `node_modules/` 和构建产物

---

## MCP Elicitation

> 原文：https://block.github.io/goose/docs/guides/mcp-elicitation

MCP Elicitation 让 goose 在扩展需要特定信息时暂停并向你询问。goose 不再猜测或假设，而是呈现一个表单，请求继续下去所需的确切信息。

该功能在 goose 中自动启用。当支持 elicitation 的扩展需要你提供信息时，会话中会出现一个表单。

:::info
[MCP Elicitation](https://modelcontextprotocol.io/specification/draft/client/elicitation) 是 Model Context Protocol 中的一项功能。goose 支持 form 模式请求。
:::

### MCP Elicitation 如何工作

当扩展需要信息时，goose 会暂停并呈现一个表单供你填写。你可以提交你的响应，也可以取消该请求。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

    聊天中会内联出现一个表单，包含：
    - 请求数据的字段
    - 用星号（*）标记的必填字段
    - 你可以接受或更改的默认值
    - 用于发送响应的 **Submit** 按钮

    提交后，你会看到一条确认消息。

  </TabItem>
  <TabItem value="cli" label="goose CLI">

    终端中会出现一个提示，包含：
    - 解释需要什么信息的消息（青色显示）
    - 带描述的字段名（黄色显示）
    - 用红色星号（*）标记的必填字段
    - 用方括号显示的默认值，例如 `[default]`

    为每个字段输入你的响应，然后按 Enter。对于是/否问题，你会看到一个交互式切换开关。

    要取消请求，请按 `Ctrl+C`。

  </TabItem>
</Tabs>

:::info 超时
Elicitation 请求会在 5 分钟后超时。如果你没有及时响应，请求会被取消，goose 将在没有该信息的情况下继续。
:::

### 面向扩展开发者

想为你自己的扩展添加 elicitation 吗？请参阅 [MCP Elicitation 规范](https://modelcontextprotocol.io/specification/draft/client/elicitation)，了解 MCP 服务器如何向用户请求结构化输入。

---

## MCP Roots

> 原文：https://block.github.io/goose/docs/guides/mcp-roots

MCP Roots 让 goose 把会话工作目录共享给支持 roots 的 MCP 扩展。

这有助于扩展理解应把哪个文件夹用作当前会话的活动工作区。

:::info
[MCP Roots](https://modelcontextprotocol.io/specification/2025-06-18/client/roots) 是 Model Context Protocol 中的一项功能。goose 会自动为支持 roots 的 MCP 扩展启用它。
:::

### MCP Roots 如何工作

当 goose 连接到某个 MCP 扩展时，它会在 MCP 初始化期间声明支持 roots。

支持 roots 的扩展随后可以：

- 向 goose 请求当前的 root 列表
- 把该 root 视为活动工作区边界
- 在会话期间 root 发生变化时做出反应

在 goose 中，root 列表目前只包含一个条目：

- 你当前的会话工作目录

如果你更改会话工作目录，goose 会更新 root 并自动通知已连接的扩展。

### 使用 MCP Roots

goose 中没有单独的 "Roots" 设置界面。MCP Roots 跟随你已为该会话使用的工作目录。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

  在 goose Desktop 中，当前工作目录显示在聊天窗口的底部。

  1. 点击目录显示区域以选择另一个文件夹
  2. goose 更新会话工作目录
  3. 已连接的、支持 roots 的扩展会自动收到更新后的 root

  要更改目录：

  1. 如有需要，点击 <PanelLeft className="inline" size={16} /> 按钮并打开一个会话
  2. 使用显示在聊天窗口底部的目录控件
  3. 选择你希望 goose 和你的扩展在其中工作的文件夹

  </TabItem>
  <TabItem value="cli" label="goose CLI">

  在 goose CLI 中，会话 root 跟随你启动 goose 时所在的目录。

  - 从你希望在其中工作的项目文件夹启动 goose
  - 恢复会话时，goose 可能会提示你切换回该会话最初的工作目录

  这意味着支持 roots 的扩展看到的 workspace 目录与 goose 在 CLI 中已使用的目录相同。

  </TabItem>
</Tabs>

### 扩展用它做什么

MCP Roots 对需要处理本地文件或理解你的项目结构的扩展很有用。

没有 roots 时，扩展可能需要猜测你指的是哪个文件夹，或依赖自定义配置。有了 roots，goose 可以告诉扩展当前会话范围内是哪个目录。

例如，扩展可以使用 roots 来：

- 发现活动的项目目录
- 把文件操作限定在你当前的工作区范围内
- 避免猜测你指的是哪个仓库或文件夹
- 在你切换到另一个项目时更新其行为

### 当前限制

goose 目前每个会话只暴露一个 root，而不是多文件夹工作区。对大多数工作流而言，这与 goose 已有的工作方式完全吻合：一次只有一个活动的项目目录。

如果你想让某个扩展在另一个位置工作，请先更改会话工作目录。

### 面向扩展开发者

如果你正在为 goose 构建 MCP 扩展，对 roots 的支持让你的扩展能够以标准方式发现活动工作区目录，而不必依赖自定义配置。

关于协议细节，请参阅 [MCP Roots 规范](https://modelcontextprotocol.io/specification/2025-06-18/client/roots)。

---

## goose 快速技巧

> 原文：https://block.github.io/goose/docs/guides/tips

#### goose 为你工作
goose 是一个 AI Agent，这意味着你可以让 goose 为你执行任务，例如打开应用、运行 shell 命令、自动化工作流、编写代码、浏览网页等等。

#### 用自然语言向 goose 提问
你不需要花哨的语言或特殊语法来向 goose 提问。像和朋友说话一样和 goose 交流即可。你甚至可以使用俚语，或者说「请」和「谢谢」；goose 都能理解。

#### 把 goose 的能力扩展到任何应用
goose 的能力是可扩展的。作为一个 [MCP](https://modelcontextprotocol.io/) 客户端，goose 可以通过[扩展](https://block.github.io/goose/extensions)连接到你的应用和服务，从而在整个工作流中发挥作用。

#### 选择 goose 拥有多少控制权
你可以自定义 goose 需要多少[监督](https://block.github.io/goose/docs/guides/managing-tools/goose-permissions)。在完全自主、操作前需要批准，或仅聊天而不执行任何操作之间进行选择。

#### 选择合适的 LLM
你与 goose 的体验取决于你[选择的 LLM](https://block.github.io/goose/blog/2025/03/31/goose-benchmark)，因为 LLM 负责所有规划，而 goose 负责执行。在选择 LLM 时，考虑其工具支持、具体能力以及相关成本。

#### 保持会话简短
LLM 有上下文窗口，也就是它们能保留多少对话历史的限制。一旦超出，它们可能会忘记对话中较早的部分。监控你的 token 使用量，并在需要时[开启新会话](https://block.github.io/goose/docs/guides/sessions/session-management)。

#### 使用快速启动器更快开始会话
按 `Cmd+Option+Shift+G`（macOS）或 `Ctrl+Alt+Shift+G`（Windows/Linux），发送一个提示词即可立即开始新会话。

#### 关闭不必要的扩展或工具
启用太多扩展会降低性能。只启用必要的[扩展和工具](https://block.github.io/goose/docs/guides/managing-tools/tool-permissions)，以提高工具选择的准确性、节省上下文窗口空间，并保持在提供方的工具限制之内。

:::tip 扩展较多时使用 Code Mode
考虑启用 [Code Mode](https://block.github.io/goose/docs/guides/managing-tools/code-mode)，这是一种按需发现工具的替代工具调用方式。
:::

#### 让 goose 了解你的偏好
通过使用 [`.goosehints` 或其他上下文文件](https://block.github.io/goose/docs/guides/context-engineering/using-goosehints)或 [skills](https://block.github.io/goose/docs/guides/context-engineering/using-skills)来保存永久的项目偏好，并使用 [Memory 扩展](https://block.github.io/goose/docs/mcp/memory-mcp)来保存你希望 goose 之后动态回忆的内容，从而帮助 goose 记住你喜欢的工作方式。两者都能帮助节省宝贵的上下文窗口空间，同时让你的偏好保持可用。

#### 保护敏感文件
在你不希望 goose 更改的文件附近工作时，使用[权限模式](https://block.github.io/goose/docs/guides/managing-tools/goose-permissions)和[工具权限](https://block.github.io/goose/docs/guides/managing-tools/tool-permissions)。

#### 版本控制
尽早且频繁地提交你的代码更改。这让你可以回滚任何意外的更改。

#### 控制 goose 可以使用哪些扩展
管理员可以使用[白名单](https://block.github.io/goose/docs/guides/allowlist)把 goose 限制为仅使用已批准的扩展。这有助于防止来自未知 MCP 服务器的有风险安装。

#### 设置起始模板
为你想要分享或以后再次运行的工作流创建一个可复用的 [recipe](https://block.github.io/goose/docs/guides/recipes/session-recipes)。

#### 拥抱实验心态
你不需要第一次就做对。对提示词和工具进行迭代是工作流的一部分。

#### 自定义侧边栏
goose Desktop 让你可以[自定义侧边栏](https://block.github.io/goose/docs/guides/desktop-navigation)，以贴合你喜欢的工作方式。调整它的位置、外观以及哪些项目可见。

#### 保持 goose 更新
定期[更新](https://block.github.io/goose/docs/guides/updating-goose) goose，以获得最新功能、缺陷修复和性能改进。

#### 让 Recipe 可安全重复运行
编写 [recipes](https://block.github.io/goose/docs/guides/recipes/session-recipes)时，先检查当前状态再执行操作，这样它们可以多次运行而不引起任何错误或重复。

#### 为 Recipe 添加日志
在你的 recipes 中为每个主要步骤加入信息丰富的日志消息，以便在出错时更容易进行调试和排查。

---

## 自定义发行版

> 原文：https://block.github.io/goose/docs/guides/custom-distributions

goose 被设计为可以 fork 和自定义。你可以创建自己的 goose「发行版」，为你的组织或受众预配置特定的提供方、捆绑的扩展、自定义品牌以及定制的工作流。

### 你可以自定义的内容

| 你想要做的 | 复杂度 |
|---------------|------------|
| 预配置一个模型/提供方 | 低 |
| 添加自定义 AI 提供方（声明式 JSON，无需代码） | 低 |
| 捆绑自定义 MCP 扩展 | 中 |
| 修改系统提示词 | 低 |
| 自定义桌面品牌（图标、名称、颜色） | 中 |
| 通过 ACP 构建新的 UI | 高 |
| 用 recipes 创建引导式工作流 | 低 |

### 快速上手

完整指南位于仓库根目录，因为构建自定义发行版需要你在代码层面工作：

👉 **[CUSTOM_DISTROS.md](https://github.com/aaif-goose/goose/blob/main/CUSTOM_DISTROS.md)**

它涵盖：

- **架构概览** —— goose 的各层（UI → server → core）如何组合在一起
- **仅配置式自定义** —— 环境变量、`config.yaml`、`init-config.yaml`
- **扩展捆绑** —— 把 MCP 服务器添加为内置扩展或通过 recipes 添加
- **自定义品牌** —— 替换图标、应用名称、系统提示词
- **构建新界面** —— 通过 Agent Client Protocol（ACP）与 `goose serve` 或 `goose acp` 集成
- **自定义 AI 提供方** —— 声明式 JSON 提供方或实现 Provider trait
- **Recipes 与子代理** —— 分发预配置的工作流
- **许可与贡献指南** —— 保持符合 Apache 2.0

### 快速示例：随 goose 一起分发本地模型

最简单的自定义发行版只需设置环境默认值：

```bash
export GOOSE_PROVIDER=ollama
export GOOSE_MODEL=qwen3-coder:latest
```

或者创建一个在首次运行时应用的 `init-config.yaml`：

```yaml
GOOSE_PROVIDER: ollama
GOOSE_MODEL: qwen3-coder:latest
```

更多场景请参阅[完整指南](https://github.com/aaif-goose/goose/blob/main/CUSTOM_DISTROS.md)，包括企业 API 密钥分发、面向特定受众的构建以及自定义 UI。
