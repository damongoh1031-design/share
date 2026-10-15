# goose 官方文档中文手册：第 03 章　扩展与工具管理

## 使用扩展

> 原文：https://block.github.io/goose/docs/getting-started/using-extensions

扩展是一种附加组件，它提供了一种扩展 goose 功能的方式，通过与你工作流中已在使用的应用程序和工具建立连接来实现。这些扩展可用于添加新功能、访问数据和资源，或与其他系统集成。

扩展基于 [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol)，因此你可以将 goose 连接到广泛的能力生态。

goose 会在激活前自动检查外部扩展是否存在已知恶意软件。如果检测到恶意包，该[扩展将被阻止](https://block.github.io/goose/docs/troubleshooting/known-issues#malicious-package-detected)，并给出清晰的错误信息。

:::tip 教程
查看[分步教程](https://block.github.io/goose/docs/category/mcp-servers)，了解如何添加和使用各种 goose 扩展
:::

### 内置扩展
goose 包含若干内置扩展，开箱即可使用：

- [Developer](https://block.github.io/goose/docs/mcp/developer-mcp)：提供一组对软件开发有用的通用开发工具。Developer 扩展**默认启用**。
- [Computer Controller](https://block.github.io/goose/docs/mcp/computer-controller-mcp)：提供用于网页抓取、文件缓存和自动化的通用计算机控制工具。
- [Memory](https://block.github.io/goose/docs/mcp/memory-mcp)：教会 goose 在你使用它时记住你的偏好。
- [Tutorial](https://block.github.io/goose/docs/mcp/tutorial-mcp)：提供用于学习 goose 的交互式教程。
- [Auto Visualiser](https://block.github.io/goose/docs/mcp/autovisualiser-mcp)：在对话中自动生成图形化数据可视化。

:::warning 访问控制
goose 默认自主运行。结合 Developer 扩展的工具，这意味着 goose 可以在未经你批准的情况下执行命令和修改文件。如果你希望对这一行为有更多控制，可以配置 [goose 权限模式](https://block.github.io/goose/docs/guides/managing-tools/goose-permissions)和[工具权限](https://block.github.io/goose/docs/guides/managing-tools/tool-permissions)。简要概述请参见[配置访问控制](https://block.github.io/goose/docs/mcp/developer-mcp#configuring-access-controls)。
:::

#### 内置平台扩展

平台扩展是内置扩展，提供诸如代码分析、对话搜索、任务跟踪和扩展管理等全局功能。它们可以按需开启或关闭。

- [Analyze](https://block.github.io/goose/docs/guides/codebase-analysis)：分析代码结构、文件详情和符号调用图（默认启用）
- [Apps](https://block.github.io/goose/docs/mcp/apps-mcp)：在独立窗口中创建、管理和启动自定义 HTML 应用
- [Chat Recall](https://block.github.io/goose/docs/mcp/chatrecall-mcp)：搜索你所有会话历史中的对话内容
- [Code Mode](https://block.github.io/goose/docs/mcp/code-mode-mcp)：在包含于当前构建中时，执行 JavaScript 代码以进行工具发现和工具调用
- [Extension Manager](https://block.github.io/goose/docs/mcp/extension-manager-mcp)：在会话期间动态发现、启用和禁用扩展（默认启用）
- [Skills](https://block.github.io/goose/docs/guides/context-engineering/using-skills)：从内置 Skill 和文件系统 Skill 中发现并加载 Skill 指令（默认启用）
- [Summon](https://block.github.io/goose/docs/mcp/summon-mcp)：加载知识源并将任务委派给子代理（默认启用）
- [Todo](https://block.github.io/goose/docs/mcp/todo-mcp)：管理任务列表并跨会话跟踪进度
- [Top of Mind](https://block.github.io/goose/docs/mcp/tom-mcp)：在每一轮向 goose 的工作记忆注入持久指令

#### 切换内置扩展

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏。
  2. 点击侧边栏上的 `Extensions` 按钮。
  3. 在 `Extensions` 下，你可以开启或关闭内置扩展。
  </TabItem>

  <TabItem value="cli" label="goose CLI">
    
    如果你知道想要添加的扩展的确切名称，请运行：

    ```sh
    goose mcp {name}
    ```

    要浏览可用的扩展：

    1. 运行以下命令：
        ```sh
        goose configure
        ```
    2. 从菜单中选择 `Add Extension`。使用上下键高亮你的选择，然后按 `Enter`。
    3. 选择 `Built-In Extension`。
    4. 选择要启用的扩展。
    5. 为该扩展提供一个超时时间（以秒为单位）。
    6. 按 `Enter`。

    **示例：添加内置扩展**

    ```
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension 
    │
    ◇  What type of extension would you like to add?
    │  Built-in Extension 
    │
    ◇  Which built-in extension would you like to enable?
    │  Auto Visualiser
    │        
    ◇  Please set the timeout for this tool (in secs):
    │  300
    │ 
    └  Enabled Auto Visualiser extension    
    ```
  </TabItem>
</Tabs>


:::info
goose 的内置扩展本身就是 MCP 服务器。如果你想将 goose 自带的 MCP 服务器用于任何其他 agent，你可以随意这样做。
:::

### 发现扩展

goose 提供了一个可安装和使用的扩展[中心目录][extensions-directory]。

你也可以将任何其他 [MCP Server](#mcp-servers) 添加为 goose 扩展，即使它未在我们的目录中列出。


### 添加扩展

扩展可以直接通过[扩展目录][extensions-directory]、CLI 或 UI 安装。

:::warning 气隙环境
如果你处于企业环境或气隙环境中，且扩展无法激活，请参阅[气隙/离线环境](https://block.github.io/goose/docs/troubleshooting/known-issues#airgappedoffline-environment-issues)了解变通方法。
:::

#### MCP 服务器

你可以将任何 MCP 服务器安装为 goose 扩展。

许多 MCP 服务器在了解你的活动工作区时能更好地工作。goose 支持 [MCP Roots](https://block.github.io/goose/docs/guides/mcp-roots)，它让具备 roots 感知能力的扩展自动看到你当前会话的工作目录。

:::tip MCP 服务器目录
在 **[MCP Server Directory](https://www.pulsemcp.com/servers)** 中查看可用的服务器。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
 
  1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏。
  2. 点击侧边栏上的 `Extensions` 按钮。
  3. 在 `Extensions` 下，点击 `Add custom extension`。
  4. 在 `Add custom extension` 模态框中，输入必要的详细信息
     - 如果要添加环境变量，请点击变量右侧的 `Add` 按钮
     - `Timeout` 字段让你设置 goose 应等待来自该扩展的工具调用完成的时间
  5. 点击 `Add` 按钮
  
  #### 添加 [Knowledge Graph Memory MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/memory) 的示例：
    * **Type**：`Standard IO`
    * **ID**：`kgm-mcp`（_设置为你想要的任何值_）
    * **Name**：`Knowledge Graph Memory`（_设置为你想要的任何值_）
    * **Description**：`maps and stores complex relationships between concepts`（_设置为你想要的任何值_）
    * **Command**：`npx -y @modelcontextprotocol/server-memory`
  </TabItem>

  <TabItem value="cli" label="goose CLI">
  
  1. 运行以下命令：

    ```sh
    goose configure
    ```

  2. 从菜单中选择 `Add Extension`。

  3. 选择你想添加的扩展类型：
      - `Built-In Extension`：使用 goose 预装的扩展。
      - `Command-Line Extension`：添加一个本地命令或脚本作为扩展运行。
      - `Remote Extension (Streamable HTTP)`：通过 Streamable HTTP 连接到远程系统

  4. 根据你选择的扩展类型，按照提示操作。

  #### 添加 [Knowledge Graph Memory MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/memory) 的示例：

<Tabs groupId="extensions">
   <TabItem value="node" label="Node">
  ```
 ┌   goose-configure 
 │
 ◇  What would you like to configure?
 │  Add Extension 
 │
 ◇  What type of extension would you like to add?
 │  Command-line Extension 
 │
 ◇  What would you like to call this extension?
 │  Knowledge Graph Memory
 │
 ◇  What command should be run?
 │  npx -y @modelcontextprotocol/server-memory
 │
 ◇  Please set the timeout for this tool (in secs):
 │  300
 │
 ◆  Would you like to add environment variables?
 │  No 
 │
 └  Added Knowledge Graph Memory extension
 ```

   </TabItem>
   <TabItem value="python" label="Python">

  ```
 ┌   goose-configure
 │
 ◇  What would you like to configure?
 │  Add Extension
 │
 ◇  What type of extension would you like to add?
 │  Command-line Extension
 │
 ◇  What would you like to call this extension?
 │  Wikipedia Reader
 │
 ◇  What command should be run?
 │  uvx mcp-wiki
 │
 ◇  Please set the timeout for this tool (in secs):
 │  300
 │
 ◆  Would you like to add environment variables?
 │  No
 │
 └  Added Wikipedia Reader extension
 ```

   </TabItem>
   <TabItem value="java" label="Java">

注意：Java 和 Kotlin 扩展仅在 Linux 和 macOS 上受支持

  ```
 ┌   goose-configure
 │
 ◇  What would you like to configure?
 │  Add Extension
 │
 ◇  What type of extension would you like to add?
 │  Command-line Extension
 │
 ◇  What would you like to call this extension?
 │  Spring Data Explorer
 │
 ◇  What command should be run?
 │  jbang -Dspring.profiles.active=dev org.example:spring-data-mcp:1.0.0
 │
 ◇  Please set the timeout for this tool (in secs):
 │  300
 │
 ◆  Would you like to add environment variables?
 │  Yes
 │
 ◇  Environment variable name:
 │  SPRING_DATASOURCE_URL
 │
 ◇  Environment variable value:
 │  jdbc:postgresql://localhost:5432/mydb
 │
 ◇  Add another environment variable?
 │  No
 │
 └  Added Spring Data Explorer extension
 ```

   </TabItem>
  </Tabs>

  </TabItem>
</Tabs>


#### 深链接

扩展可以使用 goose 的深链接协议安装。URL 格式因扩展类型而异：

<Tabs groupId="interface">
  <TabItem value="stdio" label="StandardIO" default>
```
goose://extension?cmd=<command>&arg=<argument>&id=<id>&name=<name>&description=<description>
```

必需参数：
- `cmd`：要运行的基础命令，为 `jbang`、`npx`、`uvx`、`goosed` 或 `docker` 之一
- `arg`：（仅 cmd）命令参数（可重复以提供多个参数：`&arg=...&arg=...`）
- `timeout`：等待扩展响应的最长时间（以秒为单位）
- `id`：扩展的唯一标识符
- `name`：扩展的显示名称
- `description`：扩展功能的简要描述

像 `npx -y @modelcontextprotocol/server-github` 这样的命令将表示为：

```
goose://extension?cmd=npx&arg=-y&arg=%40modelcontextprotocol/server-github&timeout=<timeout>&id=<id>&name=<name>&description=<description>
```

请注意，`npx` 命令的每个参数在深链接中都作为单独的 `arg` 参数传递。
  </TabItem>
  <TabItem value="streamable_http" label="Streamable HTTP">
```
goose://extension?url=<remote-streamable-http-url>&type=streamable_http&id=<id>&name=<n>&description=<description>
```

参数：
- `url`：远程 Streamable HTTP 服务器的 URL
- `type`：必须设置为 `streamable_http` 以指定协议类型
- `timeout`：等待扩展响应的最长时间（以秒为单位）
- `id`：扩展的唯一标识符
- `name`：扩展的显示名称
- `description`：扩展功能的简要描述

例如，像 `https://example.com/streamable` 这样的 URL 的深链接在进行 URL 编码后会像这样：

```
goose://extension?url=https%3A%2F%2Fexample.com%2Fstreamable&type=streamable_http&timeout=<timeout>&id=<id>&name=<n>&description=<description>
```

  </TabItem>
</Tabs>

:::note
深链接中的所有参数都必须进行 URL 编码。例如，空格应替换为 `%20`，`@` 应替换为 `%40`。
:::


#### 配置条目
对于高级用户，你也可以直接编辑配置文件（`~/.config/goose/config.yaml`）来添加、移除或更新扩展：

```yaml
extensions:
  github:
    name: GitHub
    cmd: npx
    args: [-y @modelcontextprotocol/server-github]
    enabled: true
    envs: { "GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_TOKEN>" }
    type: stdio
    timeout: 300
```

##### 使用预注册 OAuth 客户端的远程扩展

需要 OAuth 的远程（`streamable_http`）扩展通常会自动获取客户端 ID，方式是使用 Client ID Metadata Documents 或 Dynamic Client Registration。有些授权服务器两者都不支持，而是要求使用一个带外注册的客户端。对于这些服务器，请在扩展上设置 `client_id` —— 对于机密客户端，还要设置 `client_secret_key`：

```yaml
extensions:
  remote-example:
    name: Remote Example
    type: streamable_http
    uri: https://example.com/mcp
    client_id: <YOUR_REGISTERED_CLIENT_ID>
    client_secret_key: REMOTE_EXAMPLE_OAUTH_SECRET
    scopes:
      - example.readonly
    enabled: true
    timeout: 300
```

- `client_id`：在服务器的授权服务器上注册的 OAuth 客户端 ID。设置后，它的优先级高于 Client ID Metadata Documents 和 Dynamic Client Registration。支持 `$VAR`/`${VAR}` 替换。
- `client_secret_key`：持有客户端密钥的环境变量/密钥键的名称，从 `envs`/`env_keys` 或 goose 的密钥存储中解析（`goose configure` > extension secrets）。密钥值本身永远不会写入配置文件。对于仅使用 PKCE 进行认证的公共客户端，请省略此项。
- `scopes`：要请求的 OAuth scope。省略时，scope 会从服务器公布的元数据中选择，这可能比扩展所需的更宽泛。

OAuth 回调在 `127.0.0.1` 上以临时端口提供；如果授权服务器只允许使用固定端口且预先注册的重定向 URI，请设置 `GOOSE_OAUTH_CALLBACK_PORT`。

### 启用/禁用扩展

你可以随时启用或禁用已安装的扩展，既可以作为新会话的默认设置，也可以更改你在当前会话中使用的扩展。

#### 为新会话设置默认扩展

对默认扩展所做的更改会应用于将来的会话。对这些设置的更新不会影响任何当前活动的会话。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

  1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏。
  2. 点击侧边栏上的 `Extensions` 按钮。
  3. 使用扩展旁边的切换开关来启用或禁用它。

  </TabItem>

  <TabItem value="cli" label="goose CLI">

  1. 运行以下命令打开 goose 的配置：
      ```sh
      goose configure
      ```
  2. 从菜单中选择 `Toggle Extensions`。
  3. 将列出已安装的扩展列表。
  4. 按 `space bar` 切换该扩展。实心表示已启用。

  **示例：**

  ```
  ┌   goose-configure 
  │
  ◇  What would you like to configure?
  │  Toggle Extensions 
  │
  ◆  enable extensions: (use "space" to toggle and "enter" to submit)
  │  ◼ developer 
  │  ◻ fetch 
  └   
  ```
  </TabItem>
</Tabs>

#### 在会话中途更改扩展

在会话期间所做的更改会保留你当前的对话，而无需重新开始。会话中途的更改仅应用于当前聊天会话，不会更改你为新会话设置的默认扩展。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

  1. 点击应用底部的 <Puzzle className="inline" size={16} /> 按钮。
  2. 使用扩展旁边的切换开关来启用或禁用它。

  </TabItem>

  <TabItem value="cli" label="goose CLI">

  在交互式会话中使用斜杠命令添加扩展：

  **添加 stdio 扩展：**
  ```bash
  /extension npx -y @modelcontextprotocol/server-memory
  ```

  **添加内置扩展：**
  ```bash
  /builtin developer
  ```
  </TabItem>
</Tabs>

### 自动启用的扩展

goose 中的 Smart Extension Recommendation（智能扩展推荐）系统会根据你的任务和需求自动识别并建议相关的扩展。本节说明如何有效地使用此功能，并理解其能力和局限。

当你请求一个任务时，goose 会检查其已启用的扩展及其工具，以确定能否完成该请求。如果不能，它会按需建议或启用额外的扩展。你也可以按名称请求特定的扩展。


:::warning
任何动态启用的扩展都仅在当前会话中启用。若要在会话之间保持扩展启用，请参阅[启用/禁用扩展](#enablingdisabling-extensions)。
:::

#### 自动检测

goose 会根据你的任务需求自动检测何时需要某个扩展。下面是一个 goose 在对话期间识别并启用所需扩展的示例：

<Tabs groupId="interface">
<TabItem value="ui" label="goose Desktop" default>

#### goose 提示词
```plaintext
Find all orders with pending status from our production database
```

#### goose 输出

```plaintext
I'll help you search for available extensions that might help us interact with PostgreSQL databases.

🔍 Search Available Extensions
└─ Output ▼

 I see there's a PostgreSQL extension available. Let me enable it so we can query your database.

🔧 Manage Extensions
└─ action           enable
   extension_name   postgresql

The extension 'postgresql' has been installed successfully

Great! Now I can help you query the database...
```

</TabItem>
<TabItem value="cli" label="goose CLI">

#### goose 提示词
```plaintext
Find all orders with pending status from our production database
```

#### goose 输出

```sh
I apologize, but I notice that I don't currently have access to your database. Let me search if there are any database-related extensions available.
─── search_available_extensions | platform ──────────────────────────

I see that there is a "postgresql" extension available. Let me enable it so I can help you query your database.
─── enable_extension | platform ──────────────────────────
extension_name: postgresql


■  goose would like to enable the following extension, do you approve?
// highlight-start
| ● Yes, for this session 
// highlight-end
| ○ No
```

</TabItem>
</Tabs>

#### 直接请求

goose 会响应针对扩展的显式请求，允许用户手动启用他们所需的特定工具。下面是一个 goose 处理启用扩展的直接请求的示例：

<Tabs groupId="interface">
<TabItem value="ui" label="goose Desktop" default>

#### goose 提示词

```plaintext
Use PostgreSQL extension
```

#### goose 输出

```plaintext
I'll help enable the PostgreSQL extension for you.

🔧 Manage Extensions
└─ action           enable
   extension_name   postgresql

The extension 'postgresql' has been installed successfully

The PostgreSQL extension is now ready to use. What would you like to do with it?
```

</TabItem>
<TabItem value="cli" label="goose CLI">

#### goose 提示词

```sh
Use the PostgreSQL extension
```

#### goose 输出

```sh
I'll help enable the PostgreSQL extension for you.
─── enable_extension | platform ──────────────────────────
extension_name: postgresql


■  goose would like to enable the following extension, do you approve?
// highlight-start
| ● Yes, for this session 
// highlight-end
| ○ No
```

</TabItem>
</Tabs>

### 更新扩展属性

goose 依赖扩展属性来确定如何处理某个扩展。如果你想更改扩展的显示设置和行为，例如名称、超时时间或环境变量，可以编辑这些属性。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

  1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏。
  2. 点击侧边栏上的 `Extensions` 按钮。
  3. 在 `Extensions` 下，点击你想要编辑的扩展上的 <Settings className="inline" size={16} /> 按钮。
  4. 在出现的对话框中，按需编辑该扩展的属性。
  5. 点击 `Save Changes`。

  </TabItem>

  <TabItem value="cli" label="Config file">
  
  1. 导航到 goose [配置文件](https://block.github.io/goose/docs/guides/config-files)。例如，在 macOS 上导航到 `~/.config/goose/config.yaml`。
  2. 按需编辑扩展属性并保存你的更改。

  </TabItem>
</Tabs>

### 移除扩展

你可以移除已安装的扩展。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

  1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏。
  2. 点击侧边栏上的 `Extensions` 按钮。
  3. 在 `Extensions` 下，点击你想要移除的扩展上的 <Settings className="inline" size={16} /> 按钮。
  4. 在出现的对话框中，点击 `Remove Extension`。

  </TabItem>

  <TabItem value="cli" label="Config file">
  :::info
  要移除扩展，你必须先[禁用它](#enablingdisabling-extensions)。
  :::

    1. 运行以下命令打开 goose 的配置：
    ```sh
    goose configure
    ```
    2. 从菜单中选择 `Remove`。将列出已禁用的扩展。
    3. 用方向键向下移动到你想移除的扩展。
    4. 按 `space bar` 选择该扩展。实心表示已选中。
    ```
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Remove Extension 
    │
    ◆  Select extensions to remove (note: you can only remove disabled extensions - use "space" to toggle and "enter" to submit)
    │  ◼ fetch 
    └  
    ```
    5. 按 Enter 保存
  </TabItem>
</Tabs>


### 使用扩展启动会话

你可以直接从 CLI 用特定的扩展启动一个量身定制的 goose 会话。

:::info 注意事项
* 该扩展不会被安装。它仅在当前会话中启用。
* 如果你已经启用了这些扩展，则无需这样做。
:::

#### 内置扩展

要在启动会话时启用一个内置扩展，请运行以下命令：

```bash
goose session --with-builtin "{extension_id}"
```

例如，要启用 Developer 和 Computer Controller 扩展并启动一个会话，你可以运行：

```bash
goose session --with-builtin "developer,computercontroller"
```

或者：

```bash
goose session --with-builtin developer --with-builtin computercontroller
```


#### 外部扩展

要在启动会话时启用一个扩展，请运行以下命令：

```bash
goose session --with-extension "{extension command}" --with-extension "{another extension command}"
```

例如，要用 [Fetch 扩展](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch)启动一个会话，你可以运行：

```bash
goose session --with-extension "uvx mcp-server-fetch"
```


##### 环境变量

有些扩展需要环境变量。你可以在命令中包含这些变量：

```bash
goose session --with-extension "VAR=value command arg1 arg2"
```

例如，要用 [GitHub 扩展](https://github.com/github/github-mcp-server)启动一个会话，你可以运行：

```bash
goose session --with-extension "GITHUB_PERSONAL_ACCESS_TOKEN=<YOUR_TOKEN> npx -y @modelcontextprotocol/server-github"
```

:::info
请注意，你需要在系统上安装 [Node.js](https://nodejs.org/) 才能运行此命令，因为它使用了 `npx`。
:::


#### 通过 Streamable HTTP 使用远程扩展

要在启动会话时通过 Streamable HTTP 启用一个远程扩展，请运行以下命令：

```bash
goose session --with-streamable-http-extension "{extension URL}" --with-streamable-http-extension "{another extension URL}"
```

例如，要用一个 Streamable HTTP 扩展启动一个会话，你可以运行：

```bash
goose session --with-streamable-http-extension "https://example.com/streamable"
```

#### 容器中的扩展

goose 可以使用 `--container` 标志在 Docker 容器内运行扩展，以支持 devcontainer 工作流。详情请参阅[在 Docker 容器中运行扩展](https://block.github.io/goose/docs/tutorials/goose-in-docker#running-extensions-in-docker-containers)。

### 开发扩展

goose 扩展是用 MCP 实现的，MCP 是一种标准协议，允许 AI 模型和 agent 安全地连接本地或远程资源。了解如何构建你自己的[作为 MCP 服务器的扩展](https://modelcontextprotocol.io/quickstart/server)。

**教程：**
- [构建自定义扩展](https://block.github.io/goose/docs/tutorials/custom-extensions) - 创建一个基于 Python 的 MCP 扩展
- [构建 MCP 应用](https://block.github.io/goose/docs/tutorials/building-mcp-apps) - 创建交互式 UI 应用

[extensions-directory]: https://block.github.io/goose/extensions

---

## 管理工具

> 原文：https://block.github.io/goose/docs/guides/managing-tools

<h1 className={styles.pageTitle}>管理工具</h1>
<p className={styles.pageDescription}>
  工具是<a href="https://block.github.io/goose/docs/getting-started/using-extensions">扩展</a>中的特定功能，它们赋予 goose 各种能力。学习如何控制并定制这些工具为你工作的方式。
</p>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>📚 文档与指南</h2>
  <div className={styles.cardGrid}>
    <Card 
      title="goose 权限"
      description="选择 goose 在使用工具、编辑文件和在会话中采取行动时拥有多少自主权。"
      link="https://block.github.io/goose/docs/guides/managing-tools/goose-permissions"
    />
    <Card 
      title="工具权限"
      description="配置细粒度权限，以控制 goose 可以使用哪些工具以及何时使用，确保自动化安全可控。"
      link="https://block.github.io/goose/docs/guides/managing-tools/tool-permissions"
    />
    <Card 
      title="调整工具输出"
      description="定制工具交互的显示方式，从详细的冗长输出到简洁明了的摘要。"
      link="https://block.github.io/goose/docs/guides/managing-tools/adjust-tool-output"
    />
    <Card 
      title="Code Mode"
      description="一种按需发现并调用 MCP 工具的编程式方法。"
      link="https://block.github.io/goose/docs/guides/managing-tools/code-mode"
    />
    <Card 
      title="Ollama Tool Shim"
      description="使用一个实验性的本地解释器模型设置，为不原生支持工具调用的模型启用工具调用。"
      link="https://block.github.io/goose/docs/experimental/ollama"
    />
  </div>
</div>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>📝 精选博客文章</h2>
  <div className={styles.cardGrid}>
    <Card
      title="Agentic AI 与 MCP 生态"
      description="关于 AI agent、工具调用，以及工具如何与 LLM 协同以实现强大自动化的 101 入门介绍。"
      link="https://block.github.io/goose/blog/2025/02/17/agentic-ai-mcp"
    />
    <Card
      title="MCP 生态可视化指南"
      description="MCP 的可视化解析：你的 AI agent、工具和模型如何协同工作，并用图表和类比进行讲解。"
      link="https://block.github.io/goose/blog/2025/04/10/visual-guide-mcp"
    />
    <Card
      title="为工具调用微调 Toolshim 模型"
      description="深入探讨使用开源模型进行工具调用所面临的挑战，以及 toolshim 解决方案背后的研究。"
      link="https://block.github.io/goose/blog/2025/04/11/finetuning-toolshim"
    />

  </div>
</div>

---

## 管理工具权限

> 原文：https://block.github.io/goose/docs/guides/managing-tools/tool-permissions

工具权限提供了对 goose 如何在扩展中使用不同工具的细粒度控制。本指南将帮助你理解并有效地配置这些权限。

### 理解工具与扩展

在深入了解权限之前，我们先澄清关键组成部分：

- **扩展**是为 goose 添加功能的包（例如 Developer、Google Drive 等）
- **工具**是每个扩展内 goose 可以使用的特定功能

例如，Developer 扩展包含多个工具，例如：

- 用于文件编辑的文本编辑器工具
- 用于运行命令的 shell 工具
- 用于截取屏幕的屏幕捕获工具

:::warning 性能优化
goose 在所有扩展合计启用的工具少于 25 个时表现最佳。考虑只启用你当前任务所需的扩展。
:::

### 权限级别

工具权限与 [goose 权限模式](https://block.github.io/goose/docs/guides/managing-tools/goose-permissions)协同工作。模式设定默认行为，而工具权限让你可以覆盖特定工具的行为。

每个工具可以设置为三种权限级别之一：

| 权限级别 | 说明 | 最适用于 | 示例 |
|-----------------|-------------|-----------|----------|
| **始终允许** | 工具无需批准即可运行 | 安全的只读操作 | • 读取文件<br></br>• 列出目录<br></br>• 检索信息 |
| **执行前询问** | 需要确认 | 改变状态的操作 | • 写入/编辑文件<br></br>• 系统命令<br></br>• 创建资源 |
| **从不允许** | 工具不能被使用 | 敏感操作 | • 访问凭据<br></br>• 系统关键文件<br></br>• 删除资源 |

### 配置工具权限

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    在使用 `Manual` 或 `Smart` 批准模式时，你可以为已启用的扩展配置细粒度的工具权限。这些规则可以从模式切换器或 `Settings` 页面访问。

    <Tabs>
      <TabItem value="toggle" label="Mode Toggle" default>
        1. 点击应用底部的 <Tornado className="inline" size={16} /> 按钮
        2. 点击你所选的 `Manual` 或 `Smart` 模式旁边的 <Settings className="inline" size={16} /> 按钮
        3. 点击你想为其配置工具的扩展
        4. 使用每个工具旁边的下拉菜单来设置其权限级别
        5. 点击 `Save Changes`
      </TabItem>
      <TabItem value="settings" label="Settings Page" default>
        1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏
        2. 点击侧边栏上的 `Settings` 按钮
        3. 点击 `Chat`
        4. 在 `Mode` 下，点击你所选的 `Manual` 或 `Smart` 模式旁边的 <Settings className="inline" size={16} /> 按钮
        5. 点击你想为其配置工具的扩展
        6. 使用每个工具旁边的下拉菜单来设置其权限级别
        7. 点击 `Save Changes`
      </TabItem>
    </Tabs>
  
  </TabItem>
  <TabItem value="cli" label="goose CLI">

    1. 运行配置命令：
    ```sh
    goose configure
    ```

    2. 从菜单中选择 `goose settings`
    ```sh
    ┌ goose-configure
    │
    ◆ What would you like to configure?
    | ○ Configure Providers
    | ○ Add Extension
    | ○ Toggle Extensions
    | ○ Remove Extension
    // highlight-start
    | ● goose settings
    // highlight-end
    └
    ```

    3. 选择 `Tool Permission`
    ```sh
    ┌   goose-configure
    │
    ◇  What would you like to configure?
    │  goose settings
    │
    ◆  What setting would you like to configure?
    │  ○ goose mode
    // highlight-start
    │  ● Tool Permission
    // highlight-end
    |  ○ Tool Output
    └
    ```

    4. 选择一个扩展并为其工具配置权限：
    ```sh
    ┌   goose-configure
    │
    ◇  What setting would you like to configure?
    │  Tool Permission 
    │
    ◇  Choose an extension to configure tools
    │  developer 
    │
    ◇  Choose a tool to update permission
    │  read_image 
    │
    ◆  Set permission level for tool read_image, current permission level: Not Set
    │  ○ Always Allow 
     // highlight-start
    │  ● Ask Before (Prompt before executing this tool)
    // highlight-end
    │  ○ Never Allow 
    └
    ```
  </TabItem>
</Tabs>

### 权限管理的好处

:::tip
随着任务的变化，审视并更新你的工具权限。你可以在会话期间随时修改权限。
:::

配置工具权限有几个理由：

1. **性能优化**
   - 将启用的工具总数保持在 25 个以下以获得最佳性能
   - 禁用当前任务不需要的工具
   - 减少上下文窗口占用并提高响应质量
   - 防止工具决策瘫痪

2. **安全控制**
   - 限制对敏感操作的访问
   - 防止意外的文件修改
   - 控制系统资源使用

3. **任务聚焦**
   - 只启用当前任务所需的工具
   - 帮助 goose 做出更好的工具选择
   - 减少响应中的噪音

### 权限配置示例

#### 基于任务的配置

根据你当前的任务配置权限：

```
Development Task:
✓ File reading → Always Allow
✓ Code editing → Ask Before
✓ Test running → Always Allow
✗ System commands → Ask Before

Documentation Task:
✓ File reading → Always Allow
✓ Markdown editing → Always Allow
✗ Code editing → Never Allow
✗ System commands → Never Allow
```

---

## goose 权限模式

> 原文：https://block.github.io/goose/docs/guides/managing-tools/goose-permissions

goose 的权限决定了它在修改文件、使用扩展和执行自动化操作时拥有多少自主权。通过选择一种权限模式，你可以完全控制 goose 与你的开发环境交互的方式。

<details>
  <summary>权限模式视频演示</summary>
  <iframe
  class="aspect-ratio"
  src="https://www.youtube.com/embed/bMVFFnPS_Uk"
  title="goose Permission Modes Explained"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
  ></iframe>
</details>

### 权限模式

| 模式 | 说明 | 最适用于 |
|------|-------------|----------|
| **完全自主** | goose 可以**无需批准**地修改文件、使用扩展和删除文件 | 希望**完全自动化**并将其无缝集成到工作流中的用户 |
| **手动批准** | goose 在使用任何工具或扩展之前都会**请求确认**（支持细粒度的[工具权限](https://block.github.io/goose/docs/guides/managing-tools/tool-permissions)） | 希望**审查并批准**每一次更改和工具使用的用户 |
| **智能批准** | goose 采用基于风险的方法，**自动批准低风险操作**并**将其他操作标记**以待批准（支持细粒度的[工具权限](https://block.github.io/goose/docs/guides/managing-tools/tool-permissions)） | 希望根据操作影响在**自主与监督之间取得平衡**的用户 |
| **仅聊天** | goose **只进行聊天**，不使用扩展也不修改文件 | 偏好**对话式 AI 体验**来进行分析、写作和推理任务而不需要自动化的用户 |

:::warning
默认应用 `Autonomous Mode`（自主模式）。
:::

### 配置 goose 模式

配置方法如下：

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

    每个会话都有自己的权限模式。使用 Settings 为新会话选择默认模式。当你更改此默认值时，现有会话会保留其当前模式。

    1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏。
    2. 点击侧边栏上的 `Settings` 按钮。
    3. 点击 `Chat`。
    4. 在 `Default Mode` 下，选择你想要模式。
  </TabItem>
  <TabItem value="cli" label="goose CLI">

    <Tabs groupId="method">
      <TabItem value="session" label="In Session" default>
        要在会话中途更改模式，请使用 `/mode` 命令。

        * 自主：`/mode auto`
        * 智能批准：`/mode smart_approve`
        * 批准：`/mode approve`
        * 聊天：`/mode chat`     
      </TabItem>
      <TabItem value="settings" label="From Settings">
        1. 运行以下命令：

        ```sh
        goose configure
        ```

        2. 从菜单中选择 `goose settings` 并按 Enter。

        ```sh
        ┌ goose-configure
        │
        ◆ What would you like to configure?
        | ○ Configure Providers
        | ○ Add Extension
        | ○ Toggle Extensions
        | ○ Remove Extension
        // highlight-start
        | ● goose settings (Set the goose mode, Tool Output, Tool Permissions, Experiment, goose recipe github repo and more)
        // highlight-end
        └
        ```

        3. 从菜单中选择 `goose mode` 并按 Enter。

        ```sh
        ┌   goose-configure
        │
        ◇  What would you like to configure?
        │  goose settings 
        │
        ◆  What setting would you like to configure?
        // highlight-start
        │  ● goose mode (Configure goose mode)
        // highlight-end
        │  ○ Router Tool Selection Strategy 
        │  ○ Tool Permission 
        │  ○ Tool Output 
        │  ○ Max Turns 
        │  ○ Toggle Experiment 
        │  ○ goose recipe github repo 
        │  ○ Scheduler Type 
        └
        ```

        4.  选择你想要配置的 goose 模式。

        ```sh
        ┌   goose-configure
        │
        ◇  What would you like to configure?
        │  goose settings
        │
        ◇  What setting would you like to configure?
        │  goose mode
        │
        ◆  Which goose mode would you like to configure?
        // highlight-start
        │  ● Auto Mode (Full file modification, extension usage, edit, create and delete files freely)
        // highlight-end
        |  ○ Approve Mode
        |  ○ Smart Approve Mode    
        |  ○ Chat Mode
        |
        └  Set to Auto Mode - full file modification enabled
        ```     
      </TabItem>
    </Tabs>
  </TabItem>
</Tabs>

  :::info
  在手动和智能批准模式下，你会在工具调用期间于会话窗口中看到 "Allow" 和 "Deny" 按钮。
  goose 只会对它认定为"写"工具的工具请求权限，例如任何"文本编辑器写入"、"文本编辑器编辑"、"bash - rm, cp, mv"命令。

  读/写批准会尽最大努力对读工具或写工具进行分类。这由你的 LLM 提供方来解释。
  :::

### CLI 提供方权限集成

当使用像 Claude Code 这样的 [CLI 提供方](https://block.github.io/goose/docs/guides/cli-providers)时，goose 会与该提供方的原生权限系统集成。在批准模式下，来自 Claude Code 的权限请求会经由 goose 的确认界面路由，为你提供统一的体验。

例如，在批准模式下使用 Claude Code 时：
- Claude Code 检测敏感操作（文件写入、shell 命令、工具调用）
- 权限提示出现在 goose 的界面中（CLI 或 Desktop）
- 你的允许/拒绝决定被发送回 Claude Code
- Claude Code 根据你的响应继续执行或作出调整

此集成使用与官方 Claude Agent SDK 相同的机制，确保兼容性和一致的行为。

有关设置详情，请参阅 [CLI 提供方 - Claude Code 配置](https://block.github.io/goose/docs/guides/cli-providers#claude-code-configuration)。

---

## 调整工具输出详细程度

> 原文：https://block.github.io/goose/docs/guides/managing-tools/adjust-tool-output

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
Response Styles（响应样式）定制工具交互在 goose Desktop 聊天窗口中的显示方式。

要更改此设置：
1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏。
2. 点击侧边栏上的 `Settings` 按钮。
3. 点击 `Chat`。
4. 在 `Response Styles` 下，选择 `Detailed` 或 `Concise`。

- **简洁**（默认）
    - 工具调用默认折叠
    - 只显示 goose 使用了哪个工具
    - 最适合关注结果而非技术细节的用户

- **详细**
    - 工具调用默认展开
    - 显示工具调用及其响应的细节
    - 最适合调试或了解 goose 如何工作

此设置只影响对话中工具调用的默认状态。无论你选择哪种样式，你都可以随时手动展开或折叠任何工具调用。

</TabItem>
  <TabItem value="cli" label="goose CLI">
在使用 goose CLI 时，你可以控制工具输出的详细程度。

要调整工具输出，请运行：

```sh
goose configure
```

然后选择 `Adjust Tool Output`

```sh
┌   goose-configure 
│
◆  What would you like to configure?
│  ○ Configure Providers 
│  ○ Add Extension 
│  ○ Toggle Extensions 
│  ○ Remove Extension
// highlight-next-line
│  ● Adjust Tool Output (Show more or less tool output)
└  
```

接下来，选择一种可用的模式：

```sh
┌   goose-configure 
│
◇  What would you like to configure?
│  Adjust Tool Output 
│
// highlight-start
◆  Which tool output would you like to show?
│  ○ High Importance 
│  ○ Medium Importance 
│  ○ All 
// highlight-end
└  
```

- **High Importance（高重要性）**
    - 只显示最重要的工具输出
    - 最精简的输出级别

- **Medium Importance（中重要性）**
    - 显示中和高重要性的输出
    - 例如：文件写入操作的结果

- **All（全部）**
    - 显示所有工具输出
    - 例如：shell 命令的输出
    - 最详细的级别

#### 切换参数截断

在活动会话期间，使用 `/r` 斜杠命令来切换工具参数是被截断还是完整显示：

```sh
Context: ●○○○○○○○○○ 5% (9695/200000 tokens)
( O)> /r
✓ Full tool output enabled - tool parameters will no longer be truncated
```

当你需要查看完整的文件路径、URL 或命令参数时，这很有用。再次输入 `/r` 即可恢复为截断输出。
 </TabItem>
</Tabs>

---

## Code Mode

> 原文：https://block.github.io/goose/docs/guides/managing-tools/code-mode

Code Mode 是一种以编程方式与 MCP 工具交互的方法，而不是直接调用它们。Code Mode 在处理许多已启用的扩展时特别有用，因为它有助于更高效地管理上下文窗口占用。

:::info
此功能需要启用内置的 [Code Mode 扩展](https://block.github.io/goose/docs/mcp/code-mode-mcp)。
:::

Code Mode 控制工具如何被发现和调用：

- 来自已启用扩展的工具按需被发现，并在需要时加载到上下文中
- 多个工具调用在一次执行中批处理
- 中间结果被串联起来（一个工具的输出作为下一个工具的输入）

### Code Mode 如何工作

[Code Mode 扩展](https://block.github.io/goose/docs/mcp/code-mode-mcp)是一个 MCP 服务器，它使用 MCP 协议暴露三个基础元工具。当 Code Mode 被启用时，goose 会切换到 Code Mode。对于每个请求，LLM 会编写 JavaScript 代码，由 goose 使用 [pctx (Port of Context)](https://portofcontext.com/)（[GitHub](https://github.com/portofcontext/pctx)）——一个基于 Deno 的自定义运行时——来执行，以便：

- 从你已启用的扩展中发现可用的工具（如有需要）
- 了解如何操作当前任务所需的工具
- 以编程方式调用这些工具以完成任务

#### 传统方式 vs. Code Mode 工具调用

传统的 MCP 工具调用和 Code Mode 是实现同一目标的两种不同方法：让 goose 能够访问工具。

| 方面 | 传统方式 | Code Mode |
|--------|------------------|-----------|
| **工具发现** | 来自已启用扩展的所有工具，例如：<br/>• `developer.shell`<br/>• `developer.text_editor`<br/>• `github.list_issues`<br/>• `github.get_pull_request`<br/>• `slack.send_message`<br/>• ... *可能还有更多* | Code Mode 扩展的元工具：<br/>• `list_functions`<br/>• `get_function_details`<br/>• `execute_typescript`<br/><br/>LLM 使用这些工具按需发现来自其他已启用扩展的工具 |
| **工具调用** | • 顺序工具调用<br/>• 每次结果在下一次调用前发送给 LLM | • 可能需要工具发现调用<br/>• 多个工具调用在一次执行中批处理<br/>• 中间结果被串联并在本地处理 |
| **上下文窗口** | 每次 LLM 调用都包含来自已启用扩展的所有工具定义 | 每次 LLM 调用都包含这 3 个元工具定义，以及会话中先前发现的任何工具定义 |
| **最适用于** | • 1-3 个已启用的扩展<br/>• 使用 1-2 个工具的简单任务 | • 5 个以上扩展<br/>• 定义明确的多步工作流 |

:::info 仅文本结果
Code Mode 只支持来自工具结果的文本内容。图像、二进制数据和其他内容类型会被忽略。
:::

### 其他资源

<ContentCardCarousel
  items={[
    {
      type: 'blog',
      title: 'Code Mode for MCP',
      description: 'Learn about the code execution approach to MCP tool calling.',
      thumbnailUrl: gooseCodeMode,
      linkUrl: '/blog/2025/12/15/code-mode-mcp',
      date: '2025-12-15',
      duration: '5 min read'
    },
    {
      type: 'blog',
      title: 'Code Mode Doesn\'t Replace MCP',
      description: 'Understanding how Code Mode and MCP work together.',
      thumbnailUrl: notMcpReplacement,
      linkUrl: '/blog/2025/12/21/code-mode-doesnt-replace-mcp',
      date: '2025-12-21',
      duration: '8 min read'
    }
  ]}
/>

---

## Tool Shim

> 原文：https://block.github.io/goose/docs/guides/tool-shim

:::warning 实验性功能
工具 shim 是一个实验性功能。配置选项和行为在将来的版本中可能会变化。
:::

有些语言模型不原生支持工具/函数调用，或者会间歇性地将工具调用作为纯文本输出，而不是结构化的 API 响应。工具 shim 会检测这些基于文本的工具调用格式，并将它们转换为 goose 可以执行的正确工具调用。

### 何时启用

在以下情况启用工具 shim：

- 工具在会话中途停止工作 —— 模型调用了工具，但 goose 没有执行它
- 模型输出像 `functions.shell:0 <|tool_call_argument_begin|> {...}` 这样的纯文本，而不是使用工具 API
- 你正在使用不支持原生工具调用的本地模型（Ollama、llama.cpp）
- 你的 OpenAI 兼容提供方路由到的模型将推理标签（`<think>`）与工具调用混在一起，导致解析失败

大多数本地托管的模型，以及一些未针对结构化工具调用进行微调的云模型，都需要这个 shim。

### 工作原理

shim 会拦截模型响应，并将任何基于文本的工具调用格式转换为 goose 可以执行的结构化工具调用。它需要一个单独的**解释器模型** —— 默认情况下，goose 使用 Ollama 作为解释器。解释器模型独立于你用于主对话的任何提供方。

### 配置

#### 启用 shim

```bash
export GOOSE_TOOLSHIM=true
```

#### Ollama 后端（默认）

必须安装并运行 Ollama。默认的解释器模型是 `mistral-nemo`。

```bash
# Pull the default interpreter model
ollama pull mistral-nemo

# Optional: use a different interpreter model
export GOOSE_TOOLSHIM_OLLAMA_MODEL=llama3.2
```

#### 本地后端（llama.cpp / 内置推理）

如果你使用内置本地推理后端运行 goose，你可以用它作为解释器，而不是单独的 Ollama 实例。模型名称是必需的 —— 请设置 `GOOSE_TOOLSHIM_MODEL` 或 `LOCAL_LLM_MODEL` 配置键，否则 goose 会在启动时报错：

```bash
export GOOSE_TOOLSHIM_BACKEND=local
export GOOSE_TOOLSHIM_MODEL=my-model-name
```

`GOOSE_TOOLSHIM_BACKEND` 的有效值：`ollama`（默认）、`local`、`llama.cpp`。

### 用法示例

<Tabs>
  <TabItem value="ollama-primary" label="Ollama as primary provider" default>

  ```bash
  GOOSE_TOOLSHIM=true goose session
  ```

  使用 `mistral-nemo` 作为解释器。如有需要，用 `GOOSE_TOOLSHIM_OLLAMA_MODEL` 覆盖。

  </TabItem>
  <TabItem value="custom-provider" label="Custom OpenAI-compatible provider">

  ```bash
  GOOSE_TOOLSHIM=true \
  GOOSE_TOOLSHIM_OLLAMA_MODEL=llama3.2 \
  goose session
  ```

  你的主提供方可以是任何东西（Bedrock、自定义路由器等）。无论你在与哪个提供方对话，shim 都在本地使用 Ollama 作为解释器。

  </TabItem>
  <TabItem value="local-backend" label="Built-in local inference">

  ```bash
  GOOSE_TOOLSHIM=true \
  GOOSE_TOOLSHIM_BACKEND=local \
  GOOSE_TOOLSHIM_MODEL=my-model-name \
  goose session
  ```

  使用 goose 内置的 llama.cpp 后端作为解释器。`GOOSE_TOOLSHIM_MODEL`（或配置中的 `LOCAL_LLM_MODEL`）是必需的 —— 如果两者都未设置，启动会失败。

  </TabItem>
</Tabs>

### 环境变量参考

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `GOOSE_TOOLSHIM` | 启用工具 shim（`true` 或 `1`） | `false` |
| `GOOSE_TOOLSHIM_BACKEND` | 解释器后端：`ollama`、`local` 或 `llama.cpp` | `ollama` |
| `GOOSE_TOOLSHIM_OLLAMA_MODEL` | 用作解释器的 Ollama 模型 | `mistral-nemo` |
| `GOOSE_TOOLSHIM_MODEL` | 本地解释器后端的模型名称（如果使用 `local` 后端且未设置 `LOCAL_LLM_MODEL` 配置，则必需） | — |

### 故障排查

**工具在会话中途突然停止工作**

模型可能已从原生工具调用切换为基于文本的格式。启用 `GOOSE_TOOLSHIM=true` 并重启。

**shim 已启用但工具仍然不执行**

检查你的解释器后端是否可达：
- Ollama：运行 `ollama list` 以确认它正在运行并且解释器模型已拉取。
- 本地：确认本地推理已配置且已设置模型。

**解释器调用很慢**

切换到更小、更快的 Ollama 模型：
```bash
export GOOSE_TOOLSHIM_OLLAMA_MODEL=qwen2.5:3b
```

**模型在工具调用之前输出推理（`<think>` 标签）**

有些推理模型会将思考标签与工具调用混在一起，导致解析失败。shim 会自动处理这种情况 —— 启用它，推理内容就会从最终消息中剥离。
