# goose 官方文档中文手册：第 13 章　MCP 扩展（一）：核心内置

## {Extension Name} 扩展

> 原文：https://block.github.io/goose/docs/mcp/_template_

<!-- 你可以使用 Recipe Cookbook 中的 "Add MCP Server" Recipe 来创建一份教程草稿 -->

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/VIDEO_ID" />


本教程介绍如何将 [{Extension Name} MCP Server](https://block.github.io/goose/) 添加为 goose 扩展，以启用 ________________。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序]({goose_url})
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
  ```sh
  {command}
  ```
  </TabItem>
</Tabs>
  **环境变量**
  ```
  {env_var}: <ENV_VALUE>
  ```
:::

### 配置

:::info
注意，你需要在系统中安装 [Node.js](https://nodejs.org/) 才能运行此命令，因为它使用了 `npx`。
:::

:::info
注意，你需要在系统中安装 [uv](https://docs.astral.sh/uv/#installation) 才能运行此命令，因为它使用了 `uvx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

    <!-- 适用于内置扩展 -->
    <GooseBuiltinInstaller
      extensionName="{Extension Name}"
      description="{Extension description}"
      extensionId="{extension_id}"
    />

    <!-- 适用于外部 STDIO MCP 服务器（npx、uvx、git 等） -->
    <GooseDesktopInstaller
      extensionId="{extension_id}"
      extensionName="{Extension Name}"
      description="{Extension description}"
      type="stdio"
      command="npx"
      args={["-y", "@package/name"]}
      envVars={[
        { name: "API_KEY", label: "Description or placeholder value" }
      ]}
      apiKeyLink="https://example.com/api-keys"
      apiKeyLinkText="Service Access Token"
    />

    <!-- 适用于 HTTP MCP 服务器 -->
    <GooseDesktopInstaller
      extensionId="{extension_id}"
      extensionName="{Extension Name}"
      description="{Extension description}"
      type="http"
      url="https://example-server.com/mcp"
      envVars={[                                    // also used for http request headers
        { name: "SOME_KEY", label: "Description or placeholder value" }
      ]}
      apiKeyLink="https://example.com/api-keys"
      apiKeyLinkText="Service Access Token"
    />

  </TabItem>
  <TabItem value="cli" label="goose CLI">

    <!-- 适用于外部 STDIO MCP 服务器（npx、uvx、git 等） -->
    <CLIExtensionInstructions
      name="{Extension Name}"
      description="{Extension description}"
      type="stdio"
      command="{full command with args}"
      timeout={300}
      envVars={[
        { key: "API_KEY", value: "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪" }
      ]}
      infoNote={
        <>
          Get your API key from 
          <a href="https://example.com/api-keys" target="_blank" rel="noopener noreferrer">
            example.com
          </a> and paste it in.
        </>
      }
    />

    <!-- 适用于 HTTP MCP 服务器 -->
    <CLIExtensionInstructions
      name="{Extension Name}"
      description="{Extension description}"
      type="http"
      url="https://example-server.com/mcp"
      timeout={300}
      envVars={[                                    // also used for http request headers
        { key: "API_KEY", value: "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪" }
      ]}
      infoNote={
        <>
          Get your API key from{" "}
          <a href="https://example.com/api-keys" target="_blank" rel="noopener noreferrer">
            example.com
          </a>.
        </>
      }
    />
    
  </TabItem>
</Tabs>

### 使用示例

{描述任何环境搭建、访问控制，以及你想要完成的目标。}

#### goose 提示词

> _exact prompt_


#### goose 输出

:::note 桌面版

{exact output}

:::

---

## Developer 扩展

> 原文：https://block.github.io/goose/docs/mcp/developer-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/on_p-LeIrak" />

Developer 扩展允许 goose 自动化以开发者为中心的任务，例如文件编辑、shell 命令执行和项目搭建。它还提供了用于[代码库分析](https://block.github.io/goose/docs/guides/codebase-analysis)的工具。

本教程将介绍如何启用和使用 Developer MCP Server，它是一个 goose 内置扩展。


### 配置

:::info
goose 安装时，Developer 扩展默认已经启用。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseBuiltinInstaller
    extensionName="Developer"
    description="Automate developer-centric tasks like file editing and shell commands"
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">

  1. 运行 `configure` 命令：
  ```sh
  goose configure
  ```

  2. 选择 `Toggle Extensions`
  ```sh
  ┌   goose-configure 
  │
  ◇  What would you like to configure?
  │  Toggle Extensions 
  │
  ◆  Enable extensions: (use "space" to toggle and "enter" to submit)
  // highlight-start    
  │  ● developer
  // highlight-end  
  └  Extension settings updated successfully
  ```
  </TabItem>
</Tabs>

### 使用示例

在此示例中，我将让 goose 自动化地搭建我的 JavaScript 开发环境，其中包含 Express、Mongoose、Nodemon、Dotenv，并初始化 Git。


<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
   1. 在 goose Desktop 中打开一个新的会话
  </TabItem>
  <TabItem value="cli" label="goose CLI">

  1. 打开一个终端并启动一个新的 goose 会话：

  ```sh
  goose session
  ```

  </TabItem>
</Tabs>

#### goose 提示词
```
set up a new JavaScript project with Express, Mongoose, Nodemon, and Dotenv? Fetch the latest package versions, generate a README with those versions, and initialize Git
```

1 分钟后，goose 就搭建好了我的整个开发环境！🎉

#### goose 输出

```md
I'll help you set up a new JavaScript project with those dependencies. I'll break this down into steps:

1. First, let's create a new directory and initialize the project
2. Then install the dependencies
3. Create a detailed README
4. Initialize git
5. Create some starter files
6. Let's begin:

[... shell commands, files created ...]

Great! I've set up a complete Express project with MongoDB and Dotenv integrations:

1. Created a new project directory and initialized npm
2. Installed Express, Mongoose, and dotenv dependencies
3. set up the basic project structure with directories for:
    - config/
    - models/
    - routes/ 
    - controllers/
4. Created essential files:
    - index.js (main server file)
    - .env (environment variables)
    - .ignore (with common node.js ignores)
5. Added a basic user model with basic name and email fields
6. Created a user controller with two methods:
    - getUsers (GET all users)
    - createUser (POST new user)
7. Added user routes under `/api/routes`
8. Updated package.json with start scripts
9. Created a comprehensive README.md with:
    - Installation scripts
    - Project structure
    - Available scripts
    - Environment variables 
    - Latest package versions

The project structure is:

my-express-app/
├── config/         # Configuration files
├── models/        # MongoDB models
│   └── User.js    # User model
├── routes/        # API routes
│   └── userRoutes.js
├── controllers/   # Route controllers
│   └── userController.js
├── .env           # Environment variables
├── .gitignore     # Git ignore file
├── index.js       # Entry point
└── package.json   # Project dependencies and scripts

To start developing you can:

1. Run `npm install` to install dependencies
2. start the server with `npm run dev` 

The API will be available at:
    - `http://localhost:3000/api/users` (GET to get all users)
    - `http://localhost:3000/api/users` (POST to create a new user)

To test out the API you can use tools like postman or curl, for example, to create a new user:

curl x POST http://localhost:3000/api/users \
-H "Content-Type: application/json" \
-d '{"name": "Ebony Louis" , "email": "ebony@example.com"}'

Would you like me to add any additional features or make other improvements to the setup?
```

### 在 Shell 命令中使用环境变量

由 `shell` 工具执行的 shell 命令会继承运行中的 goose 进程的环境。这通常包括：
- 系统变量，如 `PATH`、`HOME` 和 `USER`
- 启动 goose 的进程中存在的环境变量（例如，当你从 shell 启动 goose 时，你的终端环境）
- goose 注入的会话专属变量，例如用于[会话隔离工作流](https://block.github.io/goose/docs/guides/environment-variables#using-session-ids-in-workflows)的 `AGENT_SESSION_ID`

这使得依赖环境配置的工作流成为可能，例如需要认证的 CLI 操作和构建流程。

:::info
goose Desktop 或基于启动器的方式启动时，可能使用不同的环境，并且可能不会加载你的 shell 启动文件。
:::

:::warning 敏感信息
环境变量可能包含敏感值，例如 API 密钥和令牌（例如 `GITHUB_TOKEN`、`AWS_ACCESS_KEY_ID`）。
:::

### 配置访问控制

默认情况下，goose 可以以你的用户权限运行系统命令，并**无需你的审批**即可编辑任何可访问的文件。这是因为 goose 默认以 Autonomous（自主）权限模式运行，并且可以访问 Developer 扩展的 shell 和文件编辑工具。虽然这种配置能让 goose 快速且独立地工作，但也存在出现意外结果的可能。了解可用的访问控制功能，可以帮助你把 goose 配置成符合你舒适度和具体需求的样子。

:::tip
请参阅下方的[快速设置示例](#quick-setup-example)，了解一些更精细控制 goose 行为的方法。
:::

#### Developer 扩展工具

Developer 扩展提供以下工具：

| 工具 | 描述 | 使用场景 | 风险等级 |
|------|-------------|-----------|------------|
| `shell` | 执行 shell 命令 | 运行测试、安装包、git 操作 | ⚠️ 高<br />可以以你的用户权限运行任何系统命令 |
| `write` | 创建或覆盖文件 | 创建文件、更新生成的资源、写入配置 | ⚠️ 高<br />可以修改任何可访问的文件 |
| `edit` | 替换文件中的精确文本 | 代码重构、定向编辑、删除匹配的文本 | ⚠️ 高<br />可以修改任何可访问的文件 |
| `tree` | 列出目录树并统计行数 | 在读取文件前了解项目结构 | ✅ 低<br />只读文件列表 |
| `read_image` | 读取本地或远程图像以供模型检查 | 检查截图、图表和视觉资源 | ✅ 低<br />只读图像访问 |

要进行代码结构分析，请使用单独的 [Analyze 平台扩展](https://block.github.io/goose/docs/guides/codebase-analysis)。

#### 访问控制功能

你可以叠加多个控制项，以匹配你的风险承受能力和工作流：

- **[goose 权限模式](https://block.github.io/goose/docs/guides/managing-tools/goose-permissions)**控制 goose 何时请求审批：

  | 模式 | 描述 | 使用场景 |
  |------|-------------|-----------|
  | 自主<br />CLI: `auto` | 无需审批 | 适合在安全环境中使用的经验丰富的用户 |
  | 手动审批<br />CLI: `approve` | 审查每一个操作 | 推荐用于敏感工作，或当你想要最大控制权时 |
  | 智能审批<br />CLI: `smart_approve` | 由 AI 决定哪些需要审查 | 平衡的方案 |
  | 仅聊天<br />CLI: `chat` | 禁用所有工具 | 用于最高安全性，以及不支持工具调用的模型 |

- **[工具权限](https://block.github.io/goose/docs/guides/managing-tools/tool-permissions)**让你在手动审批或智能审批模式下，为单个扩展工具设置 `Always allow`、`Ask before` 和 `Never allow` 权限

:::tip 在会话中切换模式
你可以在会话过程中切换 goose 权限模式，而无需重启：
- **CLI**：使用 `/mode` 命令（例如 `/mode approve`）
- **Desktop**：使用底部菜单中的 <Tornado className="inline" size={16} /> 模式选择按钮
:::

##### 快速设置示例

在处理敏感系统、探索不熟悉的代码库、使用不受信任的模型，或者只是倾向于在执行前先审查操作时，你可能希望对 goose 的操作有更多控制。

下面是一个启用监督的示例配置：

1. **将[权限模式](https://block.github.io/goose/docs/guides/managing-tools/goose-permissions)**设置为智能审批或手动审批：
   ```yaml
   # ~/.config/goose/config.yaml
   GOOSE_MODE: smart_approve  # or approve
   ```

2. **根据你的需求配置[工具权限](https://block.github.io/goose/docs/guides/managing-tools/tool-permissions)**

随着你对 goose 行为的适应程度提高，你可以调整这些设置以减少摩擦，同时为你的环境保留适当的安全保障。

:::info
另请参阅[安全指南](https://block.github.io/goose/docs/guides/security/)，了解如何安全地使用 goose。
:::

### 其他资源

<ContentCardCarousel
  items={[
    {
      type: 'topic',
      title: 'Codebase Analysis',
      description: 'Understand codebases with semantic analysis and call graphs',
      linkUrl: '/docs/guides/codebase-analysis'
    }
  ]}
/>

---

## 扩展管理器

> 原文：https://block.github.io/goose/docs/mcp/extension-manager-mcp

你并不总是需要手动管理扩展。扩展管理器扩展让 goose 能够在活动会话期间动态地发现、启用和禁用扩展。根据你交给它的任务，goose 会识别出何时需要某个特定扩展，在需要时启用它，并在未使用的扩展占用你的上下文窗口时建议禁用它们。

你只需描述你的任务，goose 就会自动处理扩展管理。

### 配置

<PlatformExtensionNote/>

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseBuiltinInstaller
    extensionName="Extension Manager"
    description="Dynamically discover, enable, and disable extensions during sessions"
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">

  1. 运行 `configure` 命令：
  ```sh
  goose configure
  ```

  2. 选择 `Toggle Extensions`
  ```sh
  ┌   goose-configure 
  │
  ◇  What would you like to configure?
  │  Toggle Extensions 
  │
  ◆  Enable extensions: (use "space" to toggle and "enter" to submit)
  // highlight-start    
  │  ● extensionmanager
  // highlight-end  
  └  Extension settings updated successfully
  ```
  </TabItem>
</Tabs>

### 为什么要使用扩展管理器？

goose 可以配合许多扩展工作，但一次启用太多扩展会：
- 用过多的工具选择压垮 LLM
- 降低工具选择的质量
- 拖慢响应速度
- 超出建议的上限（5 个扩展或 50 个工具）

扩展管理器通过让 goose 能够以下操作来解决这个问题：
- **发现**有哪些可用扩展
- 仅在特定任务需要时**启用**扩展
- 在扩展不再需要时**禁用**它们

这会带来更聚焦、更高效的体验，让 goose 在需要时恰好能访问到它所需的工具。

:::tip 建议的上限
为获得最佳性能，请将活动扩展控制在 **5 个或更少**，工具总数控制在 **50 个或更少**。扩展管理器会通过仅在需要时启用特定任务的扩展，帮助你保持在这些上限之内。
:::

### 可用工具

扩展管理器提供以下工具：

| 工具 | 描述 | 使用场景 |
|------|-------------|----------|
| `search_available_extensions` | 发现可以被启用或禁用的扩展 | 为任务找到合适的扩展 |
| `manage_extensions` | 按名称启用或禁用某个扩展 | 动态加载/卸载扩展 |
| `list_resources` | 列出扩展中的资源（如果支持） | 发现可用的数据源 |
| `read_resource` | 读取特定资源的内容（如果支持） | 访问扩展提供的数据 |

:::tip
资源工具（`list_resources` 和 `read_resource`）仅在至少有一个已启用的扩展支持资源时才可用。
:::

### 使用示例

让我们在需要时启用一个扩展。在此示例中，我们将启用 GitHub 扩展来处理仓库。

#### goose 提示词

```
List all my GitHub repositories
```

#### goose 输出

:::note 桌面版

```
I'll enable the GitHub extension for you so we can work with repositories.

MANAGE_EXTENSIONS
action: enable
extension_name: github

✅ The extension 'github' has been installed successfully

The GitHub extension is now active.

I'll list your GitHub repositories using the GitHub extension.

LIST_REPOSITORIES

Here are your repositories:

...

Would you like to work with any of these repositories?
```

:::

---

## Apps 扩展

> 原文：https://block.github.io/goose/docs/mcp/apps-mcp

Apps 扩展让你能够通过聊天创建、管理和启动简单的自定义应用。此功能非常适合：
- 快速实用工具，例如计算器和转换器
- 数据可视化，例如图表和仪表盘
- 简单的游戏和交互式小组件

自定义应用是单文件 HTML 应用，包含 JavaScript、CSS 和 HTML（无外部依赖或 npm 包）。它们以 [MCP App 资源](https://block.github.io/goose/docs/guides/interactive-chat/mcp-ui)的形式暴露，运行在独立的沙箱窗口中，你可以从 `Apps` 页面启动它们，或在聊天中向 goose 提出请求来启动。

你可以通过聊天创建、修改和删除应用，而无需直接编辑文件。在幕后，Apps 扩展会将每个应用以 HTML 文件的形式存储在：

- **macOS/Linux：** `~/.local/share/goose/apps/`
- **Windows：** `%APPDATA%\Block\goose\data\apps\`

### 配置

<PlatformExtensionNote/>

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseBuiltinInstaller
    extensionName="Apps"
    description="Create and manage custom goose apps through chat. Apps are HTML/CSS/JavaScript and run in sandboxed windows."
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">

  1. 运行 `configure` 命令：
  ```sh
  goose configure
  ```

  2. 选择 `Toggle Extensions`
  ```sh
  ┌   goose-configure 
  │
  ◇  What would you like to configure?
  │  Toggle Extensions 
  │
  ◆  Enable extensions: (use "space" to toggle and "enter" to submit)
  // highlight-start    
  │  ● apps
  // highlight-end  
  └  Extension settings updated successfully
  ```
  </TabItem>
</Tabs>

### 使用示例

让我们让 goose 创建一个实用工具应用。

:::info LLM
此示例使用了 Anthropic 的 Claude Sonnet 4.5。
:::

#### goose 提示词

> _Create a JSON formatter app_

#### goose 输出

:::note 桌面版
I'll create a JSON formatter app for you. This will be a useful tool for formatting, validating, and beautifying JSON data.

Perfect! I've created a JSON formatter app called "json-beautifier" that should have opened in a new window. 

The app includes:

✅ **Input & Output Areas**: Split view with input on the left and formatted output on the right  
✅ **Format Button**: Prettifies JSON with proper indentation  
✅ **Minify Button**: Compresses JSON to a single line  
✅ **Validate Button**: Checks JSON validity and shows errors  
✅ **Copy Button**: Copies the formatted JSON to clipboard  
✅ **Clear Button**: Resets everything  
✅ **Syntax Highlighting**: Color-coded keys, strings, numbers, and booleans  
✅ **Indentation Options**: Choose between 2 or 4 spaces  
✅ **Error Display**: Clear error messages in red  
✅ **Character/Line Count**: Shows statistics about your JSON  
✅ **Dark Theme**: Modern, easy-on-the-eyes design

You can paste JSON into the left panel and use the buttons to format, minify, validate, or copy it. The app should be ready to use right away!
:::

#### 结果

下面是这个 JSON 格式化应用的样子：

[![JSON 格式化应用](https://block.github.io/goose/img/apps-extension-results.png)](https://block.github.io/goose/img/apps-extension-results.png)

我的应用第一个版本外观和功能都很不错，但你完全可以让 goose 继续添加功能、更改样式等等！

---

## Auto Visualiser 扩展

> 原文：https://block.github.io/goose/docs/mcp/autovisualiser-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/txh6DlzPwNo" />

Auto Visualiser 扩展让 goose 能够直接在你的对话中自动生成交互式数据可视化。这个内置扩展使用 MCP Apps 在 goose Desktop 中内联渲染图表、图形、地图和示意图。

本指南将介绍如何启用和使用 Auto Visualiser MCP Server。

### 配置


<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseBuiltinInstaller
    extensionName="Auto Visualiser"
    description="Automatically generate interactive data visualizations"
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">

  1. 运行 `configure` 命令：
  ```sh
  goose configure
  ```

  2. 选择 `Toggle Extensions`
  ```sh
  ┌   goose-configure 
  │
  ◇  What would you like you configure?
  │  Toggle Extensions 
  │
  ◆  Enable extensions: (use "space" to toggle and "enter" to submit)
  // highlight-start    
  │  ● autovisualiser
  // highlight-end  
  └  Extension settings updated successfully
  ```
  </TabItem>
</Tabs>


:::info
Auto Visualiser 现在使用 [MCP Apps](https://block.github.io/goose/docs/tutorials/building-mcp-apps)，这意味着可视化可以内联渲染在聊天中，并在 goose Desktop 中展开为全屏或画中画模式。
:::

### 可视化类型

Auto Visualiser 会自动检测数据何时适合可视化，并选择最合适的图表或示意图类型。它会将这些可视化渲染为 goose Desktop 内的交互式 MCP App。

| 图表类型 | 描述 | 提示词隐含以下内容时被检测 |
|------------|-------------|------------------------------|
| **桑基图（Sankey Diagrams）** | 展示关系与数量的流向数据可视化 | 流向或流程数据<br />（工作流、漏斗、流程数据集） |
| **雷达图（Radar Charts）** | 多维数据对比（蜘蛛图） | 多维对比<br />（性能指标、功能对比） |
| **圆环图/饼图（Donut/Pie Charts）** | 分类数据可视化，支持多个图表 | 分类占比<br />（百分比细分、类别分布） |
| **矩形树图（Treemap Visualizations）** | 用成比例面积表示层级数据 | 层级数据<br />（嵌套类别、组织结构） |
| **弦图（Chord Diagrams）** | 实体之间的关系与流向可视化 | 关系矩阵<br />（网络连接、交叉引用） |
| **交互式地图（Interactive Maps）** | 使用 Leaflet 展示带位置标记的地理数据可视化 | 地理信息<br />（位置数据、坐标、地址） |
| **Mermaid 示意图（Mermaid Diagrams）** | 使用 Mermaid 语法绘制流程图、时序图、甘特图及其他示意图类型 | 示意图创建<br />（流程图、时序图、架构图） |
| **折线图/柱状图/散点图（Line/Bar/Scatter Charts）** | 用于数据分析的传统图表类型 | 时间序列数据<br />（历史数据、随时间变化的趋势） |

#### 示例可视化

<ImageCarousel id="flappy" width="40%" images={[

  require('/blog/2025-08-27-autovisualiser-with-mcp-ui/sankey.png').default,
  require('/blog/2025-08-27-autovisualiser-with-mcp-ui/treemap.png').default,
 ]}
 names={[
    "Sankey",
    "Treemap"
  ]} />

#### 功能特性

- **自动检测**：goose 会智能地为你的数据选择最佳可视化类型
- **交互式组件**：所有可视化都是交互式的，支持悬停效果、缩放和钻取能力
- **MCP Apps 渲染**：可视化作为 MCP App 直接在 goose Desktop 中渲染
- **多种显示模式**：可视化可以内联显示，并展开为全屏或画中画模式
- **多图表支持**：可以在单个响应中渲染多个可视化
- **可自定义样式**：支持自定义颜色、标签和格式化选项
- **导出能力**：可视化可以保存为 HTML 文件以便分享

### 工作原理

当 goose 判断你的数据应当被可视化时，Auto Visualiser 扩展会为所选图表类型返回一个 MCP App。随后 goose Desktop 会在对话中直接渲染该应用。

根据可视化的不同，你可以：

- 在聊天中内联查看它
- 将其展开为全屏以获得更大的工作区
- 在你继续对话的同时，将其移入画中画模式


### 使用示例

在此示例中，我将让 goose 分析一些销售数据，并使用 Auto Visualiser 扩展自动将其可视化。


#### goose 提示词
```
I have quarterly sales data for different product categories. Can you help me understand:
1. The hierarchical breakdown of revenue across our nested product categories
2. How our performance metrics compare across all four quarters  
3. The customer flow through our sales funnel process

Here's the data:
- Electronics: Q1: $150k, Q2: $180k, Q3: $220k, Q4: $195k
- Clothing: Q1: $120k, Q2: $140k, Q3: $160k, Q4: $175k  
- Home & Garden: Q1: $80k, Q2: $95k, Q3: $110k, Q4: $125k
```

#### goose 输出

:::note 桌面版

I'll help you analyze your quarterly sales data with three different visualizations to address each of your questions. Let me create these visualizations for you.

First, let's visualize the hierarchical breakdown of your revenue across product categories:

![](https://block.github.io/goose/img/autovisualiser-treemap.png)

![](https://block.github.io/goose/img/autovisualiser-radar.png)

![](https://block.github.io/goose/img/autovisualiser-sankey.png)


I've created three comprehensive visualizations to help you understand your quarterly sales data from different perspectives:

##### 1. Hierarchical Revenue Breakdown (Treemap)
The **treemap visualization** shows your revenue hierarchy with proportional areas representing the relative size of each category and quarter. Key insights:
- **Electronics** is your largest revenue generator ($745k total)
- **Clothing** follows as second largest ($595k total) 
- **Home & Garden** is smallest but growing ($410k total)
- You can see how each quarter contributes within each category

##### 2. Performance Metrics Comparison (Radar Chart)
The **radar chart** displays how all three product categories performed across the four quarters, making it easy to compare:
- **Electronics** shows strong Q3 performance ($220k) with slight Q4 decline
- **Clothing** demonstrates consistent growth throughout the year
- **Home & Garden** shows steady upward trajectory across all quarters
- All categories show their strongest performance in Q3-Q4

##### 3. Sales Funnel Flow (Sankey Diagram)
The **Sankey diagram** represents customer flow through your sales process, with flow thickness proportional to revenue:
- Shows how market opportunities flow into prospects for each category
- Demonstrates the conversion from prospects to actual sales
- **Electronics** has the thickest flow (highest revenue conversion)
- **Home & Garden** has the thinnest but represents growth opportunity

##### Key Business Insights:
- **Total Revenue**: $1.75M across all categories
- **Growth Pattern**: All categories show positive growth trends
- **Category Performance**: Electronics (42.6%), Clothing (34%), Home & Garden (23.4%)
- **Seasonal Trends**: Q3 appears to be your strongest quarter overall

Would you like me to create additional visualizations or dive deeper into any specific aspect of your sales data?
:::



### 故障排查

- **可视化未出现**：确保 Auto Visualiser 扩展已启用，并且你的数据符合预期的格式。

- **可视化打开了但内联显示不理想**：在 goose Desktop 中尝试全屏模式以获得更多空间。

- **数据格式错误**：检查你的数据结构是否匹配该可视化类型所要求的 schema。扩展会提供详细的错误信息来引导你。

- **大数据集的性能问题**：对于非常大的数据集，请考虑在可视化前对数据进行聚合或抽样。

---

## Code Mode 扩展

> 原文：https://block.github.io/goose/docs/mcp/code-mode-mcp

Code Mode 扩展启用了 [Code Mode](https://block.github.io/goose/docs/guides/managing-tools/code-mode)，这是一种与 MCP 工具交互的编程式方法。

Code Mode 扩展是一个 MCP 服务器，它暴露三个元工具。当 Code Mode 启用时，LLM 会编写 JavaScript 代码，goose 使用一个名为 [Port of Context](https://github.com/AdrianCole/pctx) 的基于 Deno 的运行时来执行这些代码，以发现工具、了解它们的接口并以编程方式调用它们。

当启用了多个扩展，以及执行包含多次工具调用的工作流时，这有助于更高效地管理上下文窗口的使用。

### 配置

<PlatformExtensionNote defaultEnabled={false} />

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseBuiltinInstaller
    extensionName="Code Mode"
    description="Execute JavaScript code to interact with MCP tools efficiently"
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">

  1. 运行 `configure` 命令：
  ```sh
  goose configure
  ```

  2. 选择 `Toggle Extensions`
  ```sh
  ┌   goose-configure 
  │
  ◇  What would you like to configure?
  │  Toggle Extensions 
  │
  ◆  Enable extensions: (use "space" to toggle and "enter" to submit)
  // highlight-start    
  │  ● code_execution
  // highlight-end  
  └  Extension settings updated successfully
  ```
  </TabItem>
</Tabs>

### 使用示例

在此示例中，我们将让 goose 编译一份需要多次工具调用的报告。

#### goose 提示词

```
Create a LOG.md file with the current git branch, last 3 commits, and the version from package.json
```

#### goose 输出

:::note 桌面版
I'll help you create a LOG.md file with the git branch, last 3 commits, and version from package.json. Let me gather all this information in one operation.

`Execute Code code: import { shell, text_editor } from "developer" ...`

Let me check the package.json path first:

`Execute Code code: import { shell, text_editor } from "developer" ...`

Perfect! I've created the **LOG.md** file with:

- ✅ **Current git branch**
- ✅ **Last 3 commits** (with hash, message, author, and relative time)
- ✅ **Version** from ui/desktop/package.json

The file has been saved to the root directory as `LOG.md`.
:::

---

## Summon 扩展

> 原文：https://block.github.io/goose/docs/mcp/summon-mcp

Summon 扩展让你能够将可复用的任务源加载到 goose 的上下文中，并将工作委派给[子代理](https://block.github.io/goose/docs/guides/context-engineering/subagents)。

你可以加载不同类型的源：
- [**Recipe**](https://block.github.io/goose/docs/guides/recipes) - 带有提示词和参数的自动化任务定义
- **Agent** - 存储在 agent 目录中的可复用 agent 定义
- **子 Recipe** - 当前 Recipe 中可用的 Recipe 本地任务

当你希望 goose 复用某个任务定义、把工作交给另一个 agent，或并行运行只读研究时，这很有用。Skill 由单独的 [Skills 平台扩展](https://block.github.io/goose/docs/guides/context-engineering/using-skills)加载。

:::info
此扩展在 v1.25.0+ 中可用。
:::

### 配置

<PlatformExtensionNote/>

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseBuiltinInstaller
    extensionName="Summon"
    description="Load sources and delegate tasks to subagents"
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">

  1. 运行 `configure` 命令：
  ```sh
  goose configure
  ```

  2. 选择 `Toggle Extensions`
  ```sh
  ┌   goose-configure 
  │
  ◇  What would you like to configure?
  │  Toggle Extensions 
  │
  ◆  Enable extensions: (use "space" to toggle and "enter" to submit)
  // highlight-start    
  │  ● summon
  // highlight-end  
  └  Extension settings updated successfully
  ```
  </TabItem>
</Tabs>

### 使用示例

在此示例中，我们将创建一个可复用的 Recipe，并使用 Summon 将其委派给一个子代理。

#### 创建一个 Recipe

```yaml title=".agents/recipes/release-notes.yaml"
title: Release Notes
description: Draft release notes from recent git changes
instructions: |
  Review the recent git history and changed files.
  Write concise release notes with:
  - user-facing changes
  - fixes
  - migration notes, if any
prompt: Draft release notes for the current branch.
```

#### goose 提示词

```
Use summon to delegate the release-notes recipe for this branch.
```

#### goose 输出

```
─── delegate | summon ───────────────────────────────────────
source: release-notes

The release-notes subagent reviewed the branch and drafted release notes:

## User-facing changes
- Added support for configuring project-specific extensions.
- Improved error messages when extension startup fails.

## Fixes
- Fixed stale extension state after disabling an extension.
```

### 常用的 Summon 命令

用自然语言让 goose 使用 Summon，或者直接调用这些工具：

```text
load()
load(source: "release-notes")
delegate(source: "release-notes")
delegate(instructions: "Review these docs and report stale links")
```

不带参数调用 `load()` 会列出可用的源。`delegate` 会等待子代理完成并返回其结果。

---

## Skills 扩展

> 原文：https://block.github.io/goose/docs/mcp/skills-mcp

:::caution 已废弃
此扩展已被废弃，仅在 v1.16.0 - v1.24.0 中可用。对于 v1.25.0+，请参阅 [Summon 扩展](https://block.github.io/goose/docs/mcp/summon-mcp)。
:::

Skills 扩展加载 *Skill* &mdash; 即可复用的指令集合，用来教会 goose 如何执行特定任务或遵循特定工作流。

goose 会在启动时自动发现 Skill，并在它们与你的请求相关时使用它们。goose 会从项目目录下的 `.agents/skills/` 以及全局的 `~/.agents/skills/` 加载 Skill，使 Skill 可以跨不同的 AI 编码 agent 移植。要了解如何创建 Skill 以及 goose 如何使用它们，请参阅[使用 Skill](https://block.github.io/goose/docs/guides/context-engineering/using-skills)。

### 配置

<PlatformExtensionNote/>

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseBuiltinInstaller
    extensionName="Skills"
    description="Load and use skills from the .agents/skills directory"
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">

  1. 运行 `configure` 命令：
  ```sh
  goose configure
  ```

  2. 选择 `Toggle Extensions`
  ```sh
  ┌   goose-configure 
  │
  ◇  What would you like to configure?
  │  Toggle Extensions 
  │
  ◆  Enable extensions: (use "space" to toggle and "enter" to submit)
  // highlight-start    
  │  ● skills
  // highlight-end  
  └  Extension settings updated successfully
  ```
  </TabItem>
</Tabs>

### 使用示例

假设你有一个 Skill，goose 在启动时会从 `~/.agents/skills/deploy/SKILL.md` 中发现它：

```markdown
---
name: production-deploy
description: Safe deployment procedure for production environment
---

# Production Deployment

## Pre-deployment Checklist
1. Ensure all tests pass
2. Check staging environment is stable
3. Notify #deployments channel

## Deployment Steps
1. Create release branch from main
2. Run `npm run build:prod`
3. Deploy to staging first, then production
4. Monitor error rates for 30 minutes
```

#### goose 提示词

```
Deploy the current branch to production
```

#### goose 输出

:::note 桌面版
I'll help you deploy the current branch to production. Let me first load the production deployment skill to follow the safe deployment procedure.

I can see you're on the **`my-feature-branch`** branch with some untracked files. Before proceeding with production deployment, I need to follow the safe deployment procedure.

##### ⚠️ Pre-deployment Confirmation Required

According to the production deployment skill, I need to complete the following checklist:

**Pre-deployment Checklist**
1. **Ensure all tests pass** - Have tests been run?
2. **Check staging environment is stable** - Has this been deployed to staging first?
3. **Notify #deployments channel** - Should I notify the team?

**Deployment Steps (once confirmed)**
1. Create release branch from main
2. Run `npm run build:prod`
3. Deploy to staging first, then production
4. Monitor error rates for 30 minutes

---

**Before I proceed, please confirm:**

1. ✅ Have all tests passed for the `my-feature-branch` branch?
2. ✅ Has this been tested on staging?
3. ✅ Should I notify the #deployments channel?
4. ✅ Are you sure you want to deploy the `my-feature-branch` branch (not `main`) to production?

Please confirm these items and I'll proceed with the deployment.
:::

---

## Todo 扩展

> 原文：https://block.github.io/goose/docs/mcp/todo-mcp

Todo 扩展通过将复杂工作拆解为一系列步骤，并在完成每一步时持续向你更新进度，帮助 goose 保持有条理。

Todo 扩展默认未启用。一旦启用，goose 就可以为多步骤任务记下一份简短计划，并在计划变化时更新它。这些笔记会在每一轮展示给 goose，并且能在上下文压缩后依然保留，但 goose 不会被要求勾选条目或重新核实已完成的工作。

:::tip
你随时可以让 goose「显示当前的 todo 列表」，以查看正在跟踪的内容。
:::

本教程将介绍如何启用和使用 Todo 扩展。

### 配置

<PlatformExtensionNote defaultEnabled={false}/>

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseBuiltinInstaller
    extensionName="Todo"
    description="Manage complex tasks with structured checklists and progress tracking"
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">

  1. 运行 `configure` 命令：
  ```sh
  goose configure
  ```

  2. 选择 `Toggle Extensions`
  ```sh
  ┌   goose-configure 
  │
  ◇  What would you like to configure?
  │  Toggle Extensions 
  │
  ◆  Enable extensions: (use "space" to toggle and "enter" to submit)
  // highlight-start    
  │  ● todo
  // highlight-end  
  └  Extension settings updated successfully
  ```
  </TabItem>
</Tabs>

### 使用示例

在此示例中，我将让 goose 帮我修复文档文件中的格式不一致问题。这演示了在处理系统性改进时，Todo 扩展如何帮助 goose 保持有条理。

#### goose 提示词

```
I need to update our documentation to fix formatting inconsistencies between two tutorial files. There are several sections that don't match the expected pattern. Can you help me systematically work through these issues and track our progress?
```

#### goose 输出

```md
I'll help you fix the documentation inconsistencies systematically. Let me break this down into organized tasks and track our progress.

## Fix Documentation Tutorial Inconsistencies

### Missing Components (vs Reference Pattern)
- [x] Add video embed at the top
- [x] Add LLM info box in Example Usage section  
- [x] Remove extra sections not in reference pattern

### Configuration Section Issues
- [x] Change terminology to match reference format
- [x] Fix CLI configuration section format
  - [x] Show exact command flow
  - [x] Include proper menu output with syntax highlighting
  - [x] Remove vague instructions

### Introduction/Description Issues
- [x] Simplify intro paragraph to match reference style
- [x] Fix tutorial description line to match pattern
- [x] Fix capitalization consistency throughout

### Example Structure Issues
- [x] Simplify example to match reference format
  - [x] Use clear "Prompt" and "Output" sections
  - [x] Add timing information
  - [x] Show actual response in proper code blocks
- [x] Use focused, achievable example
- [x] Show clear before/after states

### Formatting Consistency
- [x] Ensure code blocks use proper syntax highlighting
- [x] Match tone and structure of reference
- [x] Use consistent terminology throughout
- [x] Fix capitalization issues

## Documentation Update Complete! ✅

All tutorial inconsistencies have been resolved:

✅ **Structure aligned** - Matches reference pattern exactly
✅ **Components added** - Video embed, info boxes, proper tabs  
✅ **Terminology fixed** - Consistent language throughout
✅ **Example updated** - Simple, focused, with clear timing
✅ **CLI instructions** - Exact command flow with highlighting
✅ **Formatting consistent** - Proper code blocks and syntax

The documentation now follows a consistent pattern and provides a clear, organized experience for users.
```

---

## Memory 扩展

> 原文：https://block.github.io/goose/docs/mcp/memory-mcp

<YouTubeShortEmbed videoUrl="https://youtube.com/embed/BZ0yrSLXQwk" />

Memory 扩展让 goose 成为一个知识渊博的助手，它允许你教给它个性化的关键信息（例如命令、代码片段、偏好和配置），供它日后回忆并应用。无论是项目专属（本地）知识还是通用（全局）知识，goose 都会学习并记住对你最重要的内容。

本教程介绍如何启用和使用 Memory MCP Server，它是一个 goose 内置扩展。

### 配置

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseBuiltinInstaller
    extensionName="Memory"
    description="Store and recall personalized information for consistent assistance"
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">

 
  1. 运行 `configure` 命令：
  ```sh
  goose configure
  ```

  2. 选择 `Toggle Extensions`
  ```sh
  ┌   goose-configure 
  │
  ◇  What would you like to configure?
  │  Toggle Extensions 
  │
  ◆  Enable extensions: (use "space" to toggle and "enter" to submit)
  // highlight-start    
  │  ● memory
  // highlight-end
  |
  └  Extension settings updated successfully
  ```
  </TabItem>
</Tabs>

### 存储位置

记忆会以文件形式存储在磁盘上的两个位置之一：

| 范围 | 路径 | 何时使用 |
|-------|------|-------------|
| 本地（项目） | 工作目录下的 `.goose/memory/` | 项目专属的偏好和配置 |
| 全局（用户） | `~/.config/goose/memory/` | 适用于所有项目的偏好 |

goose 会在会话开始时加载所有已保存的记忆，并将它们包含在发送给 LLM 的每一条提示词中。

### 工具参考

| 工具 | 作用 |
|------|-------------|
| `remember_memory(category, data, tags, is_global)` | 存储信息，附带类别、可选标签和范围（本地/全局） |
| `retrieve_memories(category, is_global)` | 按类别检索记忆。使用 `"*"` 检索全部。 |
| `remove_memory_category(category, is_global)` | 移除某个类别中的所有记忆。使用 `"*"` 清空全部。 |
| `remove_specific_memory(category, memory_content, is_global)` | 通过在类别内匹配内容来移除单条记忆 |

### 为什么要使用 Memory？

有了 Memory 扩展，你不仅仅是在存储静态笔记，你是在教 goose 如何更好地协助你。想象一下告诉 goose：

> _learn everything about MCP servers and save it to memory._

之后，你可以问：
> _utilizing our MCP server knowledge help me build an MCP server._ 

只要你指示 goose 记住，它就会回忆你保存的一切。这使得在使用 goose 时更容易获得一致的结果。

对于篇幅较长或内容详细的指令，请将它们存储在文件中，并指示 goose 引用这些文件：

> _Remember that if I ask for help writing JavaScript, I want you to refer to "/path/to/javascript_notes.txt" and follow the instructions in that file._


### 触发词及使用时机
goose 还能识别某些触发词，它们标志着何时存储、检索或移除记忆。

| **触发词**   | **何时使用** |
|---------------------|----------------|
| remember            | 存储有用信息以备后用 |
| forget           | 移除一条已存储的记忆 |
| memory           | 通用的记忆相关操作 |
| save             | 保存一条命令、配置或偏好 |
| remove memory    | 删除特定的已存储数据 |
| clear memory     | 清空所有已存储的记忆 |
| search memory    | 查找先前存储的数据 |
| find memory      | 定位特定的已保存信息 |

### 使用示例

在此示例中，我将向你展示如何通过教 goose 了解你项目的 API 标准，把它变成一个知识渊博的开发助手。有了 Memory 扩展，goose 可以存储结构化信息，并在需要时回忆它们，帮助你在工作中保持一致。

这意味着你不再需要重复自己。goose 会记住你项目的要求，并自动将它们应用到新任务中。

:::tip  
如果你经常处理 API 标准或其他结构化知识，当 goose 检测到你工作流中的某种模式时，它可能会自动建议将其保存到记忆中。  
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
   1. 在 goose Desktop 中打开一个新的会话
  </TabItem>
  <TabItem value="cli" label="goose CLI">

  1. 打开一个终端并启动一个新的 goose 会话：

  ```sh
  goose session
  ```

  </TabItem>
</Tabs>

#### 第 1 步：教 goose 了解你的 API 标准
    ##### goose 提示词 #1
    ```
    goose, learn our API development standards:

    - All endpoints must use TypeScript interfaces
    - Error responses follow RFC 7807 Problem Details spec
    - Rate limiting headers are required
    - Authentication uses JWT in Authorization header
    - All endpoints need OpenAPI documentation

    Remember this so you can help me follow these practices.
    ```

    ##### goose 输出

    ```
    I've learned your API standards. I'll help enforce these requirements when working on API endpoints.

    Storing in:
        - Category: development_standards
        - Tags: #api #typescript #security #documentation
        - Scope: global (these are general standards)

    I can now help with:
        - API endpoint implementation
        - Error handling patterns
        - Authentication flows
        - Documentation requirements
    ```
#### 第 2 步：使用已存储的知识创建一个新的 API 端点
    ##### goose 提示词 # 2

    ```
    Help me create a new endpoint for user preferences
    ```
    ##### goose 输出
    ```
    I see you need a new endpoint. Based on our API development standards that I have stored in memory, I'll ensure it meets all our requirements.

    [.. Checking stored API standards ...]

    I've included all our required elements:
    
    ✅ TypeScript interfaces
    ✅ RFC 7807 error response format
    ✅ Rate limiting
    ✅ JWT auth header
    ✅ OpenAPI documentation

    Here's your compliant endpoint:

    interface UserPreferences {
        userId: string;
        theme: 'light' | 'dark';
        notifications: boolean;
        timezone: string;
    }

    interface ErrorResponse { 
        type: string;
        title: string;
        status: number;
        detail: string;
        instance: string;
    }

    @Route('/api/users/:userId/preferences')
    class UserPreferencesController {
        @Get()
        @RateLimit(100)  // Adding required rate limiting
        @OpenAPI({ ... }) // Including mandatory OpenAPI docs
        async getUserPreferences(
            @Header('Authorization') token: string,  // JWT auth as per our standard
            @Param('userId') userId: string
        ): Promise<UserPreferences | ErrorResponse> {
            // Implementation following our error handling pattern
        }
    }

    Would you like me to implement the full endpoint logic?
    ```

---

## Chat Recall 扩展

> 原文：https://block.github.io/goose/docs/mcp/chatrecall-mcp

Chat Recall 扩展通过在你的会话历史中进行搜索，帮助 goose 记住过往的对话。当你需要先前工作的上下文时，goose 可以搜索相关的对话，或加载特定会话的摘要。

当你引用过往工作，或提出需要历史上下文的问题时，goose 会自动使用 Chat Recall。

### 配置

<PlatformExtensionNote defaultEnabled={false} />

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseBuiltinInstaller
    extensionName="Chatrecall"
    description="Search conversation history across all your sessions"
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">

  1. 运行 `configure` 命令：
  ```sh
  goose configure
  ```

  2. 选择 `Toggle Extensions`
  ```sh
  ┌   goose-configure 
  │
  ◇  What would you like to configure?
  │  Toggle Extensions 
  │
  ◆  Enable extensions: (use "space" to toggle and "enter" to submit)
  // highlight-start    
  │  ● chatrecall
  // highlight-end  
  └  Extension settings updated successfully
  ```
  </TabItem>
</Tabs>

### 使用示例

Chat Recall 可以使用关键词搜索所有会话。结果会按会话分组，并按时间由近到远排序，还可以按日期过滤。或者，你可以提供[会话 ID](https://block.github.io/goose/docs/guides/goose-cli-commands#session-list-options)来加载特定会话的摘要。

让我们让 goose 查找关于某个主题的近期对话：

#### goose 提示词

```
What did we discuss about database migrations last week?
```

#### goose 输出

:::note 桌面版
I found discussions about database migrations in your recent sessions. Here's what we covered:

**Database Migration Discussions - Last Week**

##### Session: Fix migration scripts (Nov 26, 2024)
**Working Dir:** /projects/myapp

We debugged a production database migration that was failing with a "column already exists" error. The key points were:

- The migration was trying to add a column that already existed in some environments
- We added conditional logic to check if the column exists before adding it
- Tested the fix locally and committed the changes

##### Session: Database schema updates (Nov 27, 2024)
**Working Dir:** /projects/myapp

We discussed adding email verification functionality:

- Planned to add a new `email_verified` column to the users table
- Discussed whether to make it nullable or default to false
- Created the migration script for the new column

Both sessions were focused on safely updating the database schema in production. Would you like me to load the full details from either of these sessions?
:::

:::info
由于对话历史存储方式的变更，来自 v1.14.0 之前 goose 版本的已压缩会话可能无法被搜索到。
:::

---

## 知识图谱记忆扩展

> 原文：https://block.github.io/goose/docs/mcp/knowledge-graph-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/PF6hpDaI9Mc" />


本教程介绍如何将 [Knowledge Graph Memory MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/memory) 添加为 goose 扩展。这使 goose 能够分析关系、检测模式，并更深入地理解你的数据。知识图谱建立在 [memory 扩展](https://block.github.io/goose/docs/mcp/memory-mcp)之上，通过映射概念之间的复杂关系，并在 goose 会话之间提供持久记忆。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?cmd=npx&arg=-y&arg=%40modelcontextprotocol%2Fserver-memory&id=knowledge_graph_memory&name=Knowledge%20Graph%20Memory&description=Graph-based%20memory%20system%20for%20persistent%20knowledge%20storage)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
  ```sh
  npx -y @modelcontextprotocol/server-memory
  ```
  </TabItem>
</Tabs>
:::

### 配置

:::info
注意，你需要在系统中安装 [Node.js](https://nodejs.org/) 才能运行此命令，因为它使用了 `npx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="knowledge_graph_memory"
    extensionName="Knowledge Graph Memory"
    description="Graph-based memory system for persistent knowledge storage"
    command="npx"
    args={["-y", "@modelcontextprotocol/server-memory"]}
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Knowledge Graph Memory"
      description="Graph-based memory system for persistent knowledge storage"
      command="npx -y @modelcontextprotocol/server-memory"
    />
  </TabItem>
</Tabs>

### 使用示例

在此示例中，我将向你展示 goose 如何通过使用相互连接的知识模式来检测和分析漏洞，从而成为一个智能的安全审查员。goose 将能够理解安全问题、它们的影响和缓解措施之间的关系。

这意味着 goose 不仅仅是发现问题——它理解漏洞如何与真实世界的影响相关联，并能够建议全面的解决方案。

#### 第 1 步：教 goose 了解安全模式

##### goose 提示词 #1

```text
goose, learn these security vulnerability patterns and their relationships:

1. SQL Injection relates to:

   - Unvalidated database inputs
   - Data theft risks
   - Parameterized query solutions

2. XSS Vulnerabilities connect to:

   - Unescaped user output
   - Session hijacking risks
   - Content sanitization fixes

3. Authentication Weaknesses link to:

   - Session management
   - Account compromise
   - JWT-based solutions
```

##### goose 输出

```text
I'll store this security knowledge in the Knowledge Graph Memory with proper entities and relationships

[.... Create Entities .....]

Now, let's create the relationships between these security concepts:

[.... Create Relations .....]

Let me verify what's been stored:

[... Read Graph ...]

I've now stored your security knowledge in the graph with:

1. Vulnerability Entities:

   - SQL Injection (with observations about unvalidated inputs and data theft)
   - XSS Vulnerabilities (with observations about unescaped output and session risks)
   - Authentication Weaknesses (with observations about session management)

2. Solution Entities:

   - Parameterized Queries
   - Content Sanitization
   - JWT Authentication

3. Connected Relationships:

   - Vulnerabilities -> their potential impacts
   - Solutions -> the vulnerabilities they mitigate

The knowledge is now structured in a way that I can:

   - Trace vulnerability impact chains
   - Identify appropriate solutions for each vulnerability
   - Understand how different security issues are related
```

#### 第 2 步：使用相互连接的知识进行代码审查

##### goose 提示词 #2

Review this API endpoint for security issues:

```js
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
    const query = `SELECT * FROM users WHERE username = '${username}'`;
    db.query(query, (err, result) => {
        if (err) throw err;
        if (result.length > 0) {
            res.cookie('user', username);
            res.json({ success: true });
        }
    });
});
```

##### goose 输出

```text
I'll analyze this code using our connected knowledge graph to trace security vulnerabilities and their implications:

[.... Search Nodes ... Open Nodes ...]

Based on our knowledge graph analysis, I've found multiple critical security issues:

1. SQL Injection Vulnerability:
   - Issue: Using string concatenation in query WHERE username = '${username}'
   - Impact Chain: SQL Injection -> Data Theft
   - Risk Level: Critical
   - Solution (from parameterized_queries): Use parameterized queries instead

2. Authentication Weakness:
   - Issue: Using basic cookie-based session res.cookie('user', username)
   - Impact Chain: Auth Weakness -> Account Compromise
   - Risk Level: High
   - Solution (from jwt_auth): Implement JWT with proper expiration
```

Here's the secure implementation based on our stored patterns:

```js
app.post('/api/login', async (req, res) => {
    try {
        if (!req.body.username || !req.body.password) {
            return res.status(400).json({
                success: false,
                error: 'Username and password required'
            });
        }

        const query = 'SELECT * FROM users WHERE username = ?';
        const result = await db.query(query, [req.body.username]);

        if (!result.length) {
            return res.status(401).json({
                success: false,
                error: 'Invalid credentials'
            });
        }

        const token = jwt.sign(
            { userId: result[0].id },
            process.env.JWT_SECRET,
            { expiresIn: '1h' }
        );

        res.json({
            success: true,
            token: token
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Internal server error'
        });
    }
});
```

```text
The fixes address the vulnerability chains our knowledge graph identified:

1. SQL Injection -> Data Theft: Mitigated by parameterized queries
2. Auth Weakness -> Account Compromise: Mitigated by JWT implementation

Additional security improvements based on connected patterns:

- Added input validation
- Proper error handling
- No exposure of internal errors
- Token-based instead of cookie-based auth
- Expiration time on authentication

Would you like me to:

1. Explain any of these security relationships in more detail?
2. Show how to implement additional security patterns?
3. Analyze another endpoint?
```

---

## Fetch 扩展

> 原文：https://block.github.io/goose/docs/mcp/fetch-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/_WMm4kDYMog" />

:::warning 已知限制
Fetch 扩展[无法与](https://github.com/aaif-goose/goose/issues/1184) Google 模型（例如 gemini-2.0-flash）配合使用，因为此扩展在其 JSON schema 中使用了 `format: uri`，而 Google 不支持它。
:::

本教程介绍如何将 [Fetch MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) 添加为 goose 扩展，以从网络中检索和处理内容。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?cmd=uvx&arg=mcp-server-fetch&id=fetch&name=Fetch&description=Web%20content%20fetching%20and%20processing%20capabilities)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
  ```sh
  uvx mcp-server-fetch
  ```
  </TabItem>
</Tabs>
:::

### 配置

:::info
注意，你需要在系统中安装 [uv](https://docs.astral.sh/uv/#installation) 才能运行此命令，因为它使用了 `uvx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="fetch"
    extensionName="Fetch"
    description="Web content fetching and processing capabilities"
    command="uvx"
    args={["mcp-server-fetch"]}
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Fetch"
      description="Web content fetching and processing capabilities"
      command="uvx mcp-server-fetch"
    />
  </TabItem>
</Tabs>

### 使用示例

让我们使用 Fetch 扩展从 [Official Joke API](https://official-joke-api.appspot.com/random_joke) 获取随机的编程笑话。

:::info
虽然这个 API 不需要 API 密钥，但许多 API 都需要。如果你需要提供 API 密钥，可以将其设置为环境变量，并把变量名告诉 goose。例如：_"get tomorrow's weather for New Orleans from the weatherapi. Don't use the key directly but instead use a script that gets the value from the env var WEATHER_API_KEY"_
:::

#### goose 提示词
```
make a web page that tells jokes for programmers. The page should ask the user the setup of the joke, allow them to guess the punchline and then tell them if they are right or wrong. Include a button that allows them to request another joke. you can fetch the jokes from the official joke api
```

#### goose 输出

```
I'll help you create a web page that uses the Official Joke API to display programming jokes. I'll break this down into steps:

First, let's verify the API endpoint and see what kind of data we get
Then create an HTML file with the necessary structure
Add JavaScript to handle the interactions

Let me check the API first:


FETCH
url: https://official-joke-api.appspot.com/jokes/programming/random

Output
Content type application/json; charset=utf-8 cannot be simplified to markdown, but here is the raw content:
Contents of https://official-joke-api.appspot.com/jokes/programming/random:
[{"type":"programming","setup":"A SQL query walks into a bar, walks up to two tables and asks...","punchline":"'Can I join you?'","id":23}]

Perfect! Now I'll create an HTML file with the necessary structure and JavaScript code:

TEXT_EDITOR
command: write
file_text:
<!DOCTYPE html> <html lang="en"> <head> <meta charset="U...
path:
programmer_jokes.html

Output
programmer_jokes.html


[... contents of programmer_jokes.html ...]

I've created a complete web page that:

Fetches random programming jokes from the Official Joke API
Shows the setup of the joke
Provides an input field for users to guess the punchline
Shows whether they got it right or wrong
Displays the actual punchline after they guess
Includes a button to get another joke

The page also includes:
Clean, modern styling
Error handling for API failures
Responsive design that works on both desktop and mobile
Visual feedback for correct/incorrect answers
Disabled input after guessing to prevent multiple attempts
You can open the file programmer_jokes.html in your web browser to try it out. Would you like me to help you test it or make any adjustments to the design or functionality?
```

#### 结果

![goose 构建的网站](https://block.github.io/goose/assets/guides/programmer-jokes-fetch-mcp.png)

<details>
<summary>源代码</summary>

```html title="programmer_jokes.html"

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Programmer Jokes</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
        }
        .container {
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .setup {
            font-size: 1.2em;
            margin-bottom: 20px;
        }
        .guess-container {
            margin-bottom: 20px;
        }
        #guessInput {
            padding: 10px;
            width: 300px;
            margin-right: 10px;
        }
        button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .result {
            margin-top: 20px;
            font-weight: bold;
        }
        .correct {
            color: green;
        }
        .incorrect {
            color: red;
        }
        #punchline {
            display: none;
            margin-top: 20px;
            font-style: italic;
        }
    </style>
</head>
<body>
    <h1>Programmer Jokes</h1>
    <div class="container">
        <div id="setup" class="setup">Loading joke...</div>
        <div class="guess-container">
            <input type="text" id="guessInput" placeholder="Guess the punchline...">
            <button onclick="checkGuess()">Submit Guess</button>
        </div>
        <div id="result" class="result"></div>
        <div id="punchline"></div>
        <button onclick="getNewJoke()" style="margin-top: 20px;">Get Another Joke</button>
    </div>

    <script>
        let currentJoke = null;

        async function getNewJoke() {
            try {
                const response = await fetch('https://official-joke-api.appspot.com/jokes/programming/random');
                const jokes = await response.json();
                currentJoke = jokes[0];
                
                document.getElementById('setup').textContent = currentJoke.setup;
                document.getElementById('guessInput').value = '';
                document.getElementById('result').textContent = '';
                document.getElementById('punchline').style.display = 'none';
                document.getElementById('guessInput').disabled = false;
            } catch (error) {
                document.getElementById('setup').textContent = 'Error loading joke. Please try again.';
            }
        }

        function checkGuess() {
            const guess = document.getElementById('guessInput').value.trim().toLowerCase();
            const punchline = currentJoke.punchline.toLowerCase();
            const resultElement = document.getElementById('result');
            const punchlineElement = document.getElementById('punchline');

            if (guess === punchline) {
                resultElement.textContent = 'Correct! You got it! 🎉';
                resultElement.className = 'result correct';
            } else {
                resultElement.textContent = 'Not quite! Here\'s the punchline:';
                resultElement.className = 'result incorrect';
            }

            punchlineElement.textContent = currentJoke.punchline;
            punchlineElement.style.display = 'block';
            document.getElementById('guessInput').disabled = true;
        }

        // Load first joke when page loads
        getNewJoke();
    </script>
</body>
</html>
```

</details>

---

## PDF Reader 扩展

> 原文：https://block.github.io/goose/docs/mcp/pdf-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/EJf2_iZfaWk" />

本教程介绍如何将 [PDF Reader MCP Server](https://github.com/michaelneale/mcp-read-pdf) 添加为 goose 扩展，使 goose 能够读取受保护和未受保护的 PDF 并从中提取文本。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?cmd=uvx&arg=mcp-read-pdf&id=pdf_read&name=PDF%20Reader&description=Read%20large%20and%20complex%20PDF%20documents)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
  ```sh
  uvx mcp-read-pdf
  ```
  </TabItem>
</Tabs>
:::

### 配置

:::info
注意，你需要在系统中安装 [uv](https://docs.astral.sh/uv/#installation) 才能运行此命令，因为它使用了 `uvx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="pdf_read"
    extensionName="PDF Reader"
    description="Read large and complex PDF documents"
    command="uvx"
    args={["mcp-read-pdf"]}
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="PDF Reader"
      description="Read large and complex PDF documents"
      command="uvx mcp-read-pdf"
    />
  </TabItem>
</Tabs>

### 使用示例

此示例展示了如何使用 PDF Reader 扩展来分析一份求职者的简历，以评估特定属性。借助 PDF Reader 扩展，goose 可以读取特定页面或整份文档，也可以从大型复杂的 PDF 中提取文本。

#### goose 提示词

```
Read the resume at ~/Downloads/resume.pdf and evaluate how well this candidate aligns with the following role requirements:

  - 5+ years of backend development experience
  - Strong system design and distributed systems knowledge
  - Cloud infrastructure experience (AWS preferred)
  - Prior experience leading technical projects or teams
  - Bonus: familiarity with LLMs or AI/ML tools

Give a score out of 5 for each requirement, supporting evidence, and a summary at the end with pros, cons, and a decision: Strong Fit / Moderate Fit / Weak Fit.
```

#### goose 输出

:::note CLI

I'll help analyze the resume against those requirements. Let me read the PDF first.

─── read_pdf | pdf ──────────────────

file_path: ~/Downloads/resume.pdf

I'll now evaluate the candidate against each requirement based on the resume content:

**1. Backend Development Experience (5+ years)**

**Score: 5/5**

- 7+ years of experience as a Software Engineer at various companies
- Extensive backend development work with Java, Python, and Go
- Built and maintained multiple backend services and APIs
- Deep experience with microservices architecture and RESTful APIs

**2. System Design and Distributed Systems Knowledge**

**Score: 4.5/5**

- Designed and implemented distributed caching systems
- Experience with high-throughput message queuing systems
- Implemented service mesh architecture for microservices
- Strong understanding of scalability and reliability patterns
- Worked on systems processing millions of daily transactions

**3. Cloud Infrastructure Experience (AWS preferred)**

**Score: 4/5**

- Significant AWS experience including:
  - EC2, ECS, and Lambda
  - S3 and DynamoDB
  - CloudWatch and CloudFormation
- Experience with infrastructure as code
- Kubernetes deployment and management
- CI/CD pipeline implementation in cloud environments

**4. Prior Experience Leading Technical Projects or Teams**

**Score: 4.5/5**

- Led a team of 5 engineers in developing a new payment processing system
- Mentored junior developers and conducted technical interviews
- Managed multiple critical projects from inception to delivery
- Successfully coordinated cross-functional teams
- Demonstrated technical leadership in architecture decisions

**5. Bonus: Familiarity with LLMs or AI/ML Tools**

**Score: 3.5/5**

- Recent experience implementing ML model deployment pipelines
- Worked with natural language processing systems
- Basic understanding of ML concepts and frameworks
- Some exposure to LLM integration, though not extensive

**Summary**

**Pros:**

- Exceeds the required years of backend development experience
- Strong technical depth across multiple domains
- Proven leadership and project management capabilities
- Comprehensive cloud infrastructure experience
- Good foundation in modern AI/ML technologies

**Cons:**

- While experienced with AWS, some newer cloud services experience could be beneficial
- AI/ML experience is good but not deeply specialized in LLMs
- Could benefit from more experience with specific cloud-native patterns

**Decision: Strong Fit**

The candidate demonstrates exceptional strength in core requirements, particularly in backend development and system design. Their leadership experience and cloud infrastructure knowledge are very solid. While their AI/ML experience isn't extensive, it's sufficient for the role where it's listed as a bonus qualification. The breadth and depth of their technical experience, combined with demonstrated leadership capabilities, make them a strong fit for the position.

Their overall profile suggests they would be able to make immediate contributions while having the capacity to grow into any areas where they might need additional expertise. The strong foundation in distributed systems and proven track record of leading teams makes them particularly valuable for a technical leadership role.

**Overall Scores Summary:**

1. Backend Development: 5/5
2. System Design: 4.5/5
3. Cloud Infrastructure: 4/5
4. Leadership Experience: 4.5/5
5. AI/ML (Bonus): 3.5/5

**Total Score: 21.5/25** (not including bonus)

:::
