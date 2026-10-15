# goose 官方文档中文手册：第 17 章　MCP 扩展（五）：协作与办公

## Asana 扩展

> 原文：https://block.github.io/goose/docs/mcp/asana-mcp

本教程介绍如何把 [Asana MCP Server](https://github.com/roychri/mcp-server-asana) 添加为 goose 扩展，以实现任务自动化、项目跟踪和团队协作。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?cmd=npx&arg=-y&arg=%40roychri%2Fmcp-server-asana&id=asana-mcp&name=Asana&description=enable%20task%20automation%2C%20project%20tracking%2C%20and%20team%20collaboration&env=ASANA_ACCESS_TOKEN%3DAsana%20Access%20Token)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **Command**
  ```sh
  npx -y @roychri/mcp-server-asana
  ```
  </TabItem>
</Tabs>
  **Environment Variable**
  ```
  ASANA_ACCESS_TOKEN: <YOUR_TOKEN>
  ```
:::

### 配置

:::info
注意，你需要在系统上安装 [Node.js](https://nodejs.org/) 才能运行此命令，因为它使用了 `npx`。
:::


<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="asana-mcp"
    extensionName="Asana"
    description="Enable task automation, project tracking, and team collaboration"
    command="npx"
    args={["-y", "@roychri/mcp-server-asana"]}
    envVars={[
      { name: "ASANA_ACCESS_TOKEN", label: "Asana Access Token" }
    ]}
    apiKeyLink="https://app.asana.com/0/my-apps"
    apiKeyLinkText="Asana Access Token"
  />
  :::info
  如果你需要关于创建访问令牌的详细说明，请参阅 [Asana 的开发者文档](https://developers.asana.com/docs/personal-access-token)。
  :::
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Asana"
      description="Enable task automation, project tracking, and team collaboration"
      command="npx -y @roychri/mcp-server-asana"
      envVars={[
        { key: "ASANA_ACCESS_TOKEN", value: "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪" }
      ]}
      infoNote={
        <>
          Obtain your <a href="https://app.asana.com/0/my-apps" target="_blank" rel="noopener noreferrer">Asana Access Token</a> and paste it in. See <a href="https://developers.asana.com/docs/personal-access-token" target="_blank" rel="noopener noreferrer">Asana's developer docs</a> if you need detailed instructions on creating an access token.
        </>
      }
    />
  </TabItem>
</Tabs>

### 示例用法

#### goose 提示词

> _goose，我有一个小时。查看 Asana 中分配给我的未完成任务，把那些你估计需要一小时或更短时间就能完成的任务展示给我。按截止时间排序。_


#### goose 输出

注意，ID 已被替换为通用值

:::note CLI

<details>
    <summary>工具调用</summary>

    ─── asana_search_tasks | abcdefgh ──────────────────────────

    assignee.any: me

    completed: false

    workspace: 1234567890123



    ─── asana_get_task | abcdefgh ──────────────────────────

    opt_fields: due_on,estimated_hours

    task_id: 1100000000000001


    ─── asana_get_task | abcdefgh ──────────────────────────

    opt_fields: due_on,estimated_hours

    task_id: 1100000000000002


    ─── asana_get_task | abcdefgh ──────────────────────────

    opt_fields: due_on,estimated_hours

    task_id: 1100000000000003


    ─── asana_get_task | abcdefgh ──────────────────────────

    opt_fields: due_on,estimated_hours

    task_id: 1100000000000004


    ─── asana_get_task | abcdefgh ──────────────────────────

    opt_fields: due_on,estimated_hours

    task_id: 1100000000000005


    ─── asana_get_task | abcdefgh ──────────────────────────

    opt_fields: due_on,estimated_hours

    task_id: 1100000000000006


    ─── asana_get_task | abcdefgh ──────────────────────────

    opt_fields: due_on,estimated_hours

    task_id: 1100000000000007


    ─── asana_get_task | abcdefgh ──────────────────────────

    opt_fields: due_on,estimated_hours

    task_id: 1100000000000008


    ─── asana_get_task | abcdefgh ──────────────────────────

    opt_fields: due_on,estimated_hours

    task_id: 1100000000000009


    ─── asana_get_task | abcdefgh ──────────────────────────

    opt_fields: due_on,estimated_hours

    task_id: 1100000000000010
</details>



以下是你在 Asana 中估计需要一小时或更短时间完成的未完成任务，按截止时间排序：

1. **任务：** 查看团队会议记录
   - **截止日期：** 2025-03-21

2. **任务：** 起草简短的状态更新
   - **截止日期：** 2025-03-21

3. **任务：** 校对博客文章
   - **截止日期：** 2025-03-21

4. **任务：** 给合作伙伴发送提醒
   - **截止日期：** 2025-03-27

如果你需要更多信息或希望我协助处理某个具体任务，请告诉我！
:::

---

## Google Drive 扩展

> 原文：https://block.github.io/goose/docs/mcp/google-drive-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/p9HGYbJk9wU" />

服务器已归档

本教程介绍如何把 [Google Drive MCP Server](https://www.pulsemcp.com/servers/modelcontextprotocol-gdrive) 添加为 goose 扩展，让你可以列出、读取和搜索 Google Drive 中的文件。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?cmd=npx&arg=-y&arg=%40modelcontextprotocol%2Fserver-gdrive&id=google-drive&name=Google%20Drive&description=Google%20Drive%20integration&env=GDRIVE_CREDENTIALS_PATH%3DPath%20to%20Google%20Drive%20credentials&env=GDRIVE_OAUTH_PATH%3DPath%20to%20OAuth%20token)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **Command**
  ```sh
  GDRIVE_OAUTH_PATH=$USER_HOME/.config/gcp-oauth.keys.json \ 
  GDRIVE_CREDENTIALS_PATH=$USER_HOME/.config/.gdrive-server-credentials.json \ 
  npx -y @modelcontextprotocol/server-gdrive auth \
  npx -y @modelcontextprotocol/server-gdrive 
  ```
  </TabItem>
</Tabs>
  **Environment Variable**
  ```
  GDRIVE_CREDENTIALS_PATH: $USER_HOME/.config/.gdrive-server-credentials.json
  GDRIVE_OAUTH_PATH: $USER_HOME/.config/gcp-oauth.keys.json  
  ```
:::

:::info
注意，你*必须*在环境变量中使用绝对路径。请确保把 `$USER_HOME` 替换为你的主目录。
:::

### 配置

:::info
注意，你需要在系统上安装 [Node.js](https://nodejs.org/) 才能运行此命令，因为它使用了 `npx`。
:::

要获取你的 Google Drive 服务器凭据和 oauth 密钥，请按照以下步骤操作：

  1. 设置你的 Google Cloud 凭据，以启用 API 访问：
        - 创建 Google Cloud 项目
            - 前往 [Google Cloud Console](https://console.cloud.google.com/projectcreate) 并创建一个新项目
            - 你可以把 `location` 保留为 `No organization`
        - 启用 Google Drive API
            - 在你的项目中，前往 [API 产品库](https://console.cloud.google.com/workspace-api/products)
            - 检查左上角，确认你处于正确的项目中
            - 搜索 `Google Drive API` 并启用它

  2. 配置 OAuth 同意屏幕
        -  前往 [OAuth 同意屏幕](https://console.cloud.google.com/auth/overview/create)
        -  输入必需信息，`project name`、`user support email`
        -  为 `Audience` 选择 `Internal` 并按下 `create`
        -  如果你无法选择 `Internal`，请选择 `External` 并遵循以下附加步骤：
            - 前往 [Audience](https://console.cloud.google.com/auth/audience) 屏幕
            - 在 `Test users` 下点击 `Add Users`

 3. 创建 OAuth 凭据
        -  前往 [OAuth Clients](https://console.cloud.google.com/apis/credentials/oauthclient)
        -  点击 `Create Client`
        -  选择 **Application Type: Desktop App**
        -  下载 JSON 密钥文件
        -  把它重命名为 `gcp-oauth.keys.json`
        -  把它移动到一个扩展可以访问的安全位置：
            ```sh
            mv ~/Downloads/gcp-oauth.keys.json ~/.config/gcp-oauth.keys.json
            ```
  4. 连接 Google 账号
  
     要连接你的 Google 账号，请在终端中运行以下认证命令：
          ```sh
          GDRIVE_OAUTH_PATH=$USER_HOME/.config/gcp-oauth.keys.json \ 
          GDRIVE_CREDENTIALS_PATH=$USER_HOME/.config/.gdrive-server-credentials.json \ 
          npx -y @modelcontextprotocol/server-gdrive auth
          ```
         :::info
         把 `$USER_HOME` 替换为你的主目录。
         :::

      将打开一个浏览器窗口进行认证。按照提示连接你的 Google 账号并完成 OAuth 流程。在此阶段，你的环境变量 `GDRIVE_CREDENTIALS_PATH` 将被设置为已保存的凭据。

:::tip
使用 Google Drive 扩展时，你需要每天重新认证一次。要重新认证，只需在终端中重新运行认证命令即可。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="google-drive"
    extensionName="Google Drive"
    description="Google Drive integration"
    command="npx"
    args={["-y", "@modelcontextprotocol/server-gdrive"]}
    envVars={[
      { name: "GDRIVE_CREDENTIALS_PATH", label: "Path to Google Drive credentials" },
      { name: "GDRIVE_OAUTH_PATH", label: "Path to OAuth token" }
    ]}
  />

  :::info
  - 对于 `GDRIVE_CREDENTIALS_PATH`，输入 `$USER_HOME/.config/.gdrive-server-credentials.json`
  - 对于 `GDRIVE_OAUTH_PATH`，输入 `$USER_HOME/.config/gcp-oauth.keys.json`
  
  把 `$USER_HOME` 替换为你的主目录。你必须为此扩展指定绝对路径才能正常工作。
  :::
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  1. 运行 `configure` 命令：
  ```sh
  goose configure
  ```

  2. 选择添加一个 `Command-line Extension`
  ```sh
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension (Connect to a new extension) 
    │
    ◆  What type of extension would you like to add?
    │  ○ Built-in Extension 
    // highlight-start    
    │  ● Command-line Extension (Run a local command or script)
    // highlight-end
    │  ○ Remote Extension (Streamable HTTP) 
    └ 
  ```

  3. 为你的扩展命名
  ```sh
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension (Connect to a new extension) 
    │
    ◇  What type of extension would you like to add?
    │  Command-line Extension 
    │
    // highlight-start
    ◆  What would you like to call this extension?
    │  google drive
    // highlight-end
    └ 
  ```

  4. 输入命令
  ```sh
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension (Connect to a new extension) 
    │
    ◇  What type of extension would you like to add?
    │  Command-line Extension 
    │
    ◇  What would you like to call this extension?
    │  google drive
    │
    // highlight-start
    ◆  What command should be run?
    │  npx -y @modelcontextprotocol/server-gdrive 
    // highlight-end
    └ 
  ```  

  5. 输入 goose 在超时之前应等待操作完成的秒数。默认为 300 秒
   ```sh
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension (Connect to a new extension) 
    │
    ◇  What type of extension would you like to add?
    │  Command-line Extension 
    │
    ◇  What would you like to call this extension?
    │  google drive
    │
    ◇  What command should be run?
    │  npx -y @modelcontextprotocol/server-gdrive 
    │
    // highlight-start
    ◆  Please set the timeout for this tool (in secs):
    │  300
    // highlight-end
    └ 
  ``` 

  6. 选择添加描述。如果你在这里选择「Yes」，系统会提示你为扩展输入一段描述。
   ```sh
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension (Connect to a new extension) 
    │
    ◇  What type of extension would you like to add?
    │  Command-line Extension 
    │
    ◇  What would you like to call this extension?
    │  google drive
    │
    ◇  What command should be run?
    │  npx -y @modelcontextprotocol/server-gdrive 
    │
    ◇  Please set the timeout for this tool (in secs):
    │  300
    │
    // highlight-start
    ◇  Would you like to add a description?
    │  No
    // highlight-end
    └ 
  ```

  7. 添加你的环境变量

   ```sh
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension (Connect to a new extension) 
    │
    ◇  What type of extension would you like to add?
    │  Command-line Extension 
    │
    ◇  What would you like to call this extension?
    │  google drive
    │
    ◇  What command should be run?
    │  npx -y @modelcontextprotocol/server-gdrive 
    │
    ◇  Please set the timeout for this tool (in secs):
    │  300
    │
    ◇  Would you like to add a description?
    │  No
    │    
    // highlight-start
    ◆  Would you like to add environment variables?
    │  Yes 
    │
    ◇  Environment variable name:
    │  GDRIVE_CREDENTIALS_PATH
    │
    ◇  Environment variable value:
    │  ~/.config/.gdrive-server-credentials.json
    │
    ◇  Add another environment variable?
    │  yes 
    |
    ◇  Environment variable name:
    │  GDRIVE_OAUTH_PATH
    │
    ◇  Environment variable value:
    │  ~/.config/gcp-oauth.keys.json
    │
    // highlight-end
    └  Added google drive extension
  ```  

  </TabItem>
</Tabs>

### 示例用法

在这个示例中，我将使用 goose 快速收集并总结 30 分钟后即将召开的营销预算评审会议所需的重要信息。我会让 goose 从我的 Google Drive 中查找相关文档，总结第一季度（Q1）的表现，突出关于营销自动化和视频制作的关键决策，并找出上次会议中遗留的待办事项。

#### goose 提示词
```
I have an important marketing budget review meeting in 30 minutes and I need your help getting prepared. I have several documents in my Google Drive from our previous meetings and planning sessions. Could you help me by:

1. Finding all relevant documents about our marketing budget and performance
2. Giving me a quick summary of our Q1 performance
3. Highlighting the key decisions we need to make about the marketing automation tool and video production
4. Identifying any outstanding action items from our last meeting

I need a quick but comprehensive overview so I can walk into this meeting well-prepared.
```

#### goose 输出

```
I'll help you prepare for your meeting. Let me first list available resources from Google Drive to make sure we access the correct files. 

[... list resources ...]

Great! I can see several relevant documents. Let me access them one by one to gather the information you need. 

[... reads resources ...]

Based on all these documents, here's your comprehensive overview for the meeting: 

Q1 Performance Summary:

  - Overall 5% under budget ($104,200 spent vs $107,000 budgeted)
  - Digital Marketing performing well with highest ROI:
      - Email marketing: 3.2 ROI
      - Google Ads: 2.4 ROI
      - Content Marketing: 2.1 ROI
  - Social media engagement up 23% from previous quarter
  - Content marketing blog posts generating 2x expected leads

Key Decisions Needed:

  1. Marketing Automation Tool (License Renewal Due):
    - Current tool (BasicAutomation Pro): $12,000/year
    - Options:
        - GrowthStack ($15,000/year) - recommended option, balanced features/price
        - MarketingHub Enterprise ($18,000/year) - premium option with AI features
        - Decision needed on whether to upgrade or maintain current solution
    - Implementation would take 6 weeks if changing providers

  2. Video Production Investment:
    - Three vendor options:
        - CreativeForce Media ($16,200) - most comprehensive, unlimited revisions
        - VisualCraft Studios ($14,500) - solid middle option
        - Digital Narrative Pro ($12,800) - basic package
    - CreativeForce Media is recommended despite higher cost due to comprehensive deliverables
    - Timeline ranges from 3-5 weeks depending on vendor choice

Outstanding Action Items from Last Meeting:

  1. Sarah needs to present ROI analysis for video content investment
  2. John needs to complete software license review
  3. Lisa to present new PPC strategy
  4. Mike has completed the video production agency quotes

Q2 Planning Considerations:

  - Proposed 12% budget increase for Q2 ($120,000 total)
  - Potential reallocation needed based on new tool and video production decisions
  - PPC strategy review pending

Would you like me to focus on any particular aspect of this overview in more detail?
```

---

## Google Maps 扩展

> 原文：https://block.github.io/goose/docs/mcp/google-maps-mcp

服务器已归档

本教程介绍如何把 [Google Maps MCP Server](https://www.pulsemcp.com/servers/google-maps-docs) 添加为 goose 扩展，以实现地理编码、地点搜索、距离计算、海拔数据获取和路线导航。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?cmd=npx&arg=-y&arg=%40modelcontextprotocol%2Fserver-google-maps&id=google-maps&name=Google%20Maps&description=Google%20Maps%20API%20integration&env=GOOGLE_MAPS_API_KEY%3DGoogle%20Maps%20API%20key)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **Command**
  ```sh
  npx -y @modelcontextprotocol/server-google-maps
  ```
  </TabItem>
</Tabs>
  **Environment Variable**
  ```
  GOOGLE_MAPS_API_KEY: <YOUR_TOKEN>
  ```
:::

### 配置

:::info
注意，你需要在系统上安装 [Node.js](https://nodejs.org/) 才能运行此命令，因为它使用了 `npx`。
:::

<Tabs groupId="interface" defaultValue="ui">
  <TabItem value="ui" label="goose Desktop">
  <GooseDesktopInstaller
    extensionId="google-maps"
    extensionName="Google Maps"
    description="Google Maps API integration"
    command="npx"
    args={["-y", "@modelcontextprotocol/server-google-maps"]}
    envVars={[
      { name: "GOOGLE_MAPS_API_KEY", label: "Google Maps API Key" }
    ]}
    apiKeyLink="https://developers.google.com/maps/documentation/javascript/get-api-key"
    apiKeyLinkText="Google Maps API Key"
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  1. 运行 `configure` 命令：
  ```sh
  goose configure
  ```

  2. 选择添加一个 `Command-line Extension`
  ```sh
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension (Connect to a new extension) 
    │
    ◆  What type of extension would you like to add?
    │  ○ Built-in Extension 
    // highlight-start    
    │  ● Command-line Extension (Run a local command or script)
    // highlight-end
    │  ○ Remote Extension (Streamable HTTP) 
    └ 
  ```

  3. 为你的扩展命名
  ```sh
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension (Connect to a new extension) 
    │
    ◇  What type of extension would you like to add?
    │  Command-line Extension 
    │
    // highlight-start
    ◆  What would you like to call this extension?
    │  Google Maps
    // highlight-end
    └ 
  ```

  4. 输入命令
  ```sh
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension (Connect to a new extension) 
    │
    ◇  What type of extension would you like to add?
    │  Command-line Extension 
    │
    ◇  What would you like to call this extension?
    │  Google Maps
    │
    // highlight-start
    ◆  What command should be run?
    │  npx -y @modelcontextprotocol/server-google-maps
    // highlight-end
    └ 
  ``` 

  5. 输入 goose 在超时之前应等待操作完成的秒数。默认为 300 秒
   ```sh
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension (Connect to a new extension) 
    │
    ◇  What type of extension would you like to add?
    │  Command-line Extension 
    │
    ◇  What would you like to call this extension?
    │  Google Maps
    │
    ◇  What command should be run?
    │  npx -y @modelcontextprotocol/server-google-maps
    │
    // highlight-start
    ◆  Please set the timeout for this tool (in secs):
    │  300
    // highlight-end
    └ 
  ``` 

  6. 选择添加描述。如果你在这里选择「Yes」，系统会提示你为扩展输入一段描述。
   ```sh
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension (Connect to a new extension) 
    │
    ◇  What type of extension would you like to add?
    │  Command-line Extension 
    │
    ◇  What would you like to call this extension?
    │  Google Maps
    │
    ◇  What command should be run?
    │  npx -y @modelcontextprotocol/server-google-maps
    │
    ◆  Please set the timeout for this tool (in secs):
    │  300
    │
    // highlight-start
    ◇  Would you like to add a description?
    │  No
    // highlight-end
    │
    └ 
  ```

  7. 获取一个 [Google Maps API Key](https://developers.google.com/maps/documentation/javascript/get-api-key) 并粘贴进去。

   ```sh
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension (Connect to a new extension) 
    │
    ◇  What type of extension would you like to add?
    │  Command-line Extension 
    │
    ◇  What would you like to call this extension?
    │  Google Maps
    │
    ◇  What command should be run?
    │  npx -y @modelcontextprotocol/server-google-maps
    │
    ◇  Please set the timeout for this tool (in secs):
    │  300
    │
    ◇  Would you like to add a description?
    │  No
    │   
    // highlight-start
    ◆  Would you like to add environment variables?
    │  Yes 
    │
    ◇  Environment variable name:
    │  GOOGLE_MAPS_API_KEY
    │
    ◇  Environment variable value:
    │  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
    │
    ◇  Add another environment variable?
    │  No 
    // highlight-end
    └  Added github extension
  ```  

  </TabItem>
</Tabs>

### 示例用法

goose 充当一个自主代理，它跟踪外卖骑手的位置，实时更新客户信息，并根据 Google Maps 的交通数据动态调整预计送达时间。

goose 可以：

**监控骑手位置**
* goose 每隔几秒获取一次骑手的 GPS 坐标。
* 如果骑手的位置明显落后于计划，goose 会重新计算预计送达时间。

**考虑交通状况的 ETA 调整**
* goose 查询 Google Maps 的实时交通状况。
* 如果检测到延误，goose 会用新的预计时间更新客户的跟踪器。

**动态客户通知**
* 如果骑手堵在路上，goose 会向客户发送提醒：「你的骑手因交通延误。更新后的预计送达时间：晚上 7:25。」
* 如果骑手提前于计划，goose 会通知餐厅提前备餐。


#### goose 提示词
```
Track the live GPS location of driver ID #12345. Query Google Maps for real-time traffic data and adjust the estimated delivery time if delays exceed 5 minutes. If ETA changes, update the customer’s live tracker and send an SMS notification. If the delay is greater than 20 minutes, check if another driver within a 1-mile radius can take over the delivery.
```

#### goose 输出

:::note CLI
好的，我将跟踪骑手 #12345，查询 Google Maps 的交通数据，调整 ETA，并通知客户。

**跟踪骑手的 GPS 位置**

*   **骑手 ID：** #12345
*   **起点：** 1955 Broadway, Suite 600, Oakland, CA 94612

骑手 #12345 的移动轨迹：

```
2025-02-23 08:20:00: Latitude: 37.8074, Longitude: -122.2697 (Starting point)
2025-02-23 08:21:00: Latitude: 37.8080, Longitude: -122.2690
2025-02-23 08:22:00: Latitude: 37.8090, Longitude: -122.2680
2025-02-23 08:23:00: Latitude: 37.8100, Longitude: -122.2670
```


**对目的地地址进行地理编码**

*   **客户地址：** 2111 Mission Street, San Francisco, CA

我将把此地址转换为地理坐标：


`─── maps_geocode | googlemaps ──────────────────────────`

address: 2111 Mission Street, San Francisco, CA

```
Latitude: 37.7631446
Longitude: -122.4192073
```


**获取初始路线和 ETA**

我将获取从骑手起点到客户地址的初始路线和 ETA。


`─── maps_directions | googlemaps ──────────────────────────`

destination: 2111 Mission St, San Francisco, CA
mode: driving
origin: ...

```
Distance: 12.1 miles
Initial ETA: 21 minutes
Estimated arrival at: 08:41 AM
```


**监控交通并调整 ETA**

我将监控交通更新并定期重新计算 ETA。

```
Remaining Distance: 8 miles
Updated ETA: 15 minutes
Estimated arrival at: 08:45 AM
```

没有明显延误。

*08:35 AM 时：* 发生了一起交通事件。


`─── maps_directions | googlemaps ──────────────────────────`

destination: 2111 Mission St, San Francisco, CA
mode: driving
origin: Latitude: 37.8100, Longitude: -122.2670


抱歉，我无法在请求中使用经纬度。我将改用名称来调用 google maps api。

`─── maps_directions | googlemaps ──────────────────────────`

destination: 2111 Mission St, San Francisco, CA
mode: driving
origin: ...

```
Remaining Distance: 7 miles
Updated ETA: 26 minutes
Estimated arrival at: 08:46 AM
```


ETA 相比最初的 08:41 AM 增加了 5 分钟。路线现在包含一条提示：「Expect delays due to congestion.」

**更新客户并发送短信**

[... other extensions used (e.g. Webhooks, MySQL, ClickSend)...]

*   **更新实时跟踪器：** 客户的实时跟踪界面已更新，以反映 08:46 AM 的新 ETA。
*   **发送短信通知：** _「由于交通原因，你的配送现在预计大约在 08:46 AM 到达。给您带来不便，我们深表歉意。」_
:::

---

## Square MCP 扩展

> 原文：https://block.github.io/goose/docs/mcp/square-mcp

<details>
  <summary> 🎥 Square MCP Server 视频演示</summary>
  <iframe
  class="aspect-ratio"
  src="https://www.youtube.com/embed/y6pklrzhzNg"
  title="Run your Business with AI | Square MCP Server"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
  ></iframe>
</details>


本教程将带你开始使用 [Square MCP server](https://developer.squareup.com/docs/mcp)，为你的 Square 卖家账号启用交互式和自动化的工作。Square MCP server 是一个开源项目，允许你使用 goose 与 Square API 进行交互。

Square 提供两个版本的 MCP 服务器：

1. **远程 MCP 服务器**，由 Square 托管，使用 OAuth 进行认证，并允许对 API 使用进行细粒度权限控制。
2. **本地 MCP 服务器**，你可以在自己的机器上运行，使用访问令牌进行认证，并允许完整的 API 访问。

:::info
注意，你需要在系统上安装 [Node.js](https://nodejs.org/) 才能运行安装命令，因为它们使用了 `npx`。
:::

### 配置

<Tabs groupId="remote-or-local">
  <TabItem value="remote" label="Square Remote MCP" default>
  :::tip 快速安装
  <Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
    [启动安装程序](https://mcp.squareup.com/goose)
    </TabItem>
    <TabItem value="cli" label="goose CLI">
    **Command**
    ```sh
    npx mcp-remote https://mcp.squareup.com/sse
    ```
    </TabItem>
  </Tabs>
  :::

  <Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
     1. [启动安装程序](https://mcp.squareup.com/goose)
     2. 点击 `OK` 确认安装
     3. goose 应会打开一个浏览器标签页，跳转到 OAuth 权限页面。请仔细核对你想允许的权限，然后点击 `Grant Access`。
     4. 它会要求你登录或重新认证到 Square，并可能要求你确认想要允许的权限。
     5. 在 goose 中，导航到聊天界面

    </TabItem>
    <TabItem value="cli" label="goose CLI">
      <CLIExtensionInstructions
        name="square-mcp-remote"
        type="stdio"
        command="npx mcp-remote https://mcp.squareup.com/sse"
        timeout={300}
      />

      当你启动下一个会话时，goose 会打开一个浏览器，你可以在其中授予权限并登录你的 Square 账号。
  
    </TabItem>
  </Tabs>
</TabItem>

  <TabItem value="local" label="Square Local MCP">
  :::tip 快速安装
  <Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
    [启动安装程序](goose://extension?cmd=npx&arg=square-mcp-server&arg=start&id=square-mcp&name=Square%20MCP%20Server&description=Square%20API%20MCP%20Server&env=ACCESS_TOKEN%3DYour%20Access%20Token&env=SANDBOX%3Dtrue)

    </TabItem>
    <TabItem value="cli" label="goose CLI">
    **Command**
    ```sh
    npx square-mcp-server start
    ```
    </TabItem>
  </Tabs>
    **Environment Variables**
    ```
    ACCESS_TOKEN: <YOUR_API_KEY>
    SANDBOX: <true/false>
    PRODUCTION: <true/false>
    ```

    注意，你将使用 `SANDBOX` 或 `PRODUCTION`，而不是两者同时使用，并且你的 `ACCESS_TOKEN` 将根据你选择的环境，是沙箱令牌或生产令牌。
  :::

  <Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="square-mcp"
      extensionName="Square MCP Server"
      description="Square API MCP Server"
      command="npx"
      args={["square-mcp-server", "start"]}
      envVars={[
        { name: "ACCESS_TOKEN", label: "Your Access Token" },
        { name: "SANDBOX", label: "true" }
      ]}
      appendToStep3="Set either SANDBOX or PRODUCTION to true (the access token must match the environment)"
      apiKeyLink="https://developer.squareup.com/apps"
      apiKeyLinkText="Square Access Token"
    />
    </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="square-mcp"
      type="stdio"
      command="npx square-mcp-server start"
      timeout={300}
      envVars={[
        { key: "ACCESS_TOKEN", value: "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪" },
        { key: "SANDBOX", value: "true" }
      ]}
      infoNote={
        <>
          Obtain your <a href="https://developer.squareup.com/apps" target="_blank" rel="noopener noreferrer">Square Access Token</a> and paste it in. Set either <code>SANDBOX</code> or <code>PRODUCTION</code> to true (the access token must match the environment)
        </>
      }
    />
    </TabItem>
  </Tabs>

  </TabItem>
</Tabs>

### 示例用法

Square MCP server 允许你通过一个内容丰富的[服务目录](https://github.com/square/square-mcp-server?tab=readme-ov-file#service-catalog)与 Square 的 connect API 交互，从而访问 Square API 生态。

#### goose 提示词

```
( O)> Find my food menu from the following image and import these into my Square seller account. "my-burger-menu.png"
```

[这是演示中使用的菜单图片。](https://block.github.io/goose/assets/guides/square-mcp-goosin-menu.png)

#### goose 输出

```
I'll help you import these menu items into your Square catalog. I'll use the Square API to create catalog items for each burger. Let me break this down into steps:

1. First, I'll check the catalog API service info and types
2. Then I'll create catalog items for each burger

Now let me check the type info for creating catalog objects

Now I'll start creating catalog items for each burger in your menu. I'll create them one by one using the catalog API. Let me process each burger:

(output truncated)

I've successfully created all the burger items from your menu in your Square catalog. Each burger has been added with:

- The exact name from your menu
- The full description
- The correct price
- A standard variation for ordering

Here's a summary of what was created:
- The Classic - $10.00
- Cheeseburger - $11.00
- Primetime Burger - $12.00
- Double Bacon - $14.00
- Texas Meatlover - $12.50
- Buffalo Burger - $12.00
- The Atomic - $12.50
- Little Bird - $11.00
- Mushroom Burger - $10.00

All items are now available in your Square catalog and ready for use in your point of sale system. Each burger includes its complete description and comes with a "Regular" variation at the specified price. The items are set as both sellable and stockable by default, and they're available at all locations.
```

---

## Cash App 扩展

> 原文：https://block.github.io/goose/docs/mcp/cash-app-mcp

Cash App 把本地餐饮点单带入 AI 时代。发现附近的商家、浏览带卡路里和过敏原信息的菜单、自定义订单并完成结账——一切都通过对话完成。真正的魔力在于？把它与其他工具结合起来：查看日历上的会议时间、把餐食记录到你的健康应用，或寻找符合你饮食目标的选项。试试「Order a nut-free lunch that arrives before my 2pm flight」这类提示词，获得真正连贯的体验。

### 快速安装

:::tip
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [安装 Cash App 扩展](goose://extension?type=streamable_http&url=https%3A%2F%2Fconnect.squareup.com%2Fv2%2Fmcp%2Fcash-app&id=cash-app&name=Cash%20App&description=Cash%20App%20brings%20local%20food%20ordering%20into%20the%20AI%20era.)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  使用 `goose configure` 添加一个 `Remote Extension (Streamable HTTP)`，配置如下：

  **Endpoint URL**

  ```
  https://connect.squareup.com/v2/mcp/cash-app
  ```
  </TabItem>
</Tabs>
:::

### 配置

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="cash-app"
      extensionName="Cash App"
      description="Cash App brings local food ordering into the AI era. Discover nearby sellers, browse menus, customize orders, and complete checkout—all conversationally."
      type="http"
      url="https://connect.squareup.com/v2/mcp/cash-app"
    />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Cash App"
      description="Cash App brings local food ordering into the AI era. Discover nearby sellers, browse menus, customize orders, and complete checkout—all conversationally."
      type="http"
      url="https://connect.squareup.com/v2/mcp/cash-app"
    />
  </TabItem>
</Tabs>

### 你可以做什么

#### 发现附近餐厅

查找任意位置附近的餐厅。可以按菜系偏好、品牌名称、当前是否营业进行筛选，或者直接描述你想吃什么。

**提示词：**
```
Find me restaurants near 375 W Broadway in New York that are open now.
I'm in the mood for something quick and healthy.
```

<details>
<summary>goose 输出</summary>

```
Here are restaurants near 375 W Broadway:

1. Ba'al Falafel - 71 Sullivan St — Mediterranean. Fresh falafel,
   hummus, and salads. (hours: 10:00 AM - 10:00 PM)
2. Kale & Things - 284 Lafayette St — Healthy bowls and salads
   with lean proteins. (hours: 9:00 AM - 9:00 PM)
3. Simply Natural Grill House NY - 684 Broadway — Grilled proteins
   and wholesome meals. (hours: 11:00 AM - 10:00 PM)
4. Steam & Sip - 112 Spring St — Coffee and light bites.
   (hours: 7:00 AM - 7:00 PM)

For a quick, healthy lunch I'd recommend Ba'al Falafel or Kale & Things —
both are close by and have great light options. Want me to show you
either menu?
```

</details>

#### 浏览带价格和推荐的菜单

获取完整的菜单概览，包括分类、价格、描述和推荐菜品——全部以 goose 可以推理的纯文本形式呈现。

**提示词：**
```
Show me the full menu for Ba'al Falafel at 71 Sullivan St.
```

<details>
<summary>goose 输出</summary>

```
# Ba'al Falafel

## Recommended
- **Classic Falafel Sandwich** — $9.99: Crispy falafel balls with tahini,
  pickles, and fresh vegetables in warm pita
- **Mediterranean Bowl** — $12.99: Falafel, hummus, tabbouleh, and mixed
  greens with tahini dressing

## Sandwiches
- **Classic Falafel Sandwich** — $9.99: Crispy falafel balls with tahini
- **Shawarma Wrap** — $11.99: Seasoned chicken shawarma with garlic sauce
- **Sabich** — $10.99: Fried eggplant, hard-boiled egg, and amba sauce

## Salads
- **Beets Apple Salad** — $11.99: Roasted beets, apple, walnuts, goat cheese
- **Fattoush Salad** — $10.99: Crispy pita chips with fresh vegetables

## Soups
- **Lentil Soup** — $6.99: Traditional red lentil soup with cumin

## Drinks
- **Ginger Lemonade** — $4.99: Fresh-squeezed with ginger
- **Mint Tea** — $3.99: Fresh mint leaves steeped in hot water
```

</details>

由于菜单以结构化文本返回，goose 无需再次调用工具即可回答后续问题，例如*「哪些菜品在 $10 以下？」*或*「哪些是素食？」*。

#### 构建购物车并结账

一旦找到你想要的，就让 goose 构建你的订单。它会处理菜品选择、选项修饰符和数量——然后给你一个结账链接，通过 Cash App 完成支付。

**提示词：**
```
Add a Classic Falafel Sandwich and a Ginger Lemonade to my cart.
```

### 示例提示词

当 goose 把 Cash App 与你的其他工具以及你一天的情境结合起来时，它最为强大：

- **考虑时间的点单：** *「订一份无坚果的午餐，要在我下午 2 点航班之前送到。」*
- **与日历搭配：** *「查看我今天的日历，在我下午 1 点会议前找个能快速自取午餐的地方。我在 Union Square 附近。」*
- **注重健康的选择：** *「找我附近有低于 500 卡路里沙拉的餐厅，并把选项展示给我。」*
- **为聚会做计划：** *「今晚我要在 Bryant Park 附近和 3 个朋友见面。找个有不错素食选项的地方，并把菜单展示给我。」*
- **探索新街区：** *「我刚搬到 Williamsburg。Bedford Ave 步行范围内有哪些最好的餐厅？」*
- **注重预算的点单：** *「在 Times Square 附近找 $12 以下的午餐特惠。」*

---

## Alby 比特币支付扩展

> 原文：https://block.github.io/goose/docs/mcp/alby-mcp

本教程介绍如何把 [Alby Bitcoin Payments MCP Server](https://github.com/getalby/mcp) 添加为 goose 扩展，以便与你的闪电钱包交互、进行收付款、列出交易、把法币金额转换为 sats、从闪电地址请求发票，以及与付费 MCP 工具（例如用 [PaidMCP](https://github.com/getAlby/paidmcp) 构建的工具）交互。

:::info
你需要一个支持 [NWC](https://nwc.dev) 的闪电钱包。如果还没有，可以考虑试试 [Alby Hub](https://albyhub.com)。
:::

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?cmd=npx&arg=-y&arg=%40getalby%2Fmcp&id=alby-mcp&name=Alby&description=Connect%20goose%20to%20your%20Bitcoin%20Lightning%20Wallet&env=NWC_CONNECTION_STRING%3DNWC%20Connection%20Secret)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **Command**
  ```sh
  npx -y @getalby/mcp
  ```
  </TabItem>
</Tabs>
  **Environment Variable**
  ```
  NWC_CONNECTION_STRING: nostr+walletconnect://...
  ```
:::

### 配置

:::info
你需要在系统上安装 [Node.js](https://nodejs.org/) 才能运行此命令，因为它使用了 `npx`

**或者**你可以使用 Alby 托管的 MCP（见下方的远程选项）。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <Tabs>
      <TabItem value="local" label="Local" default>
        <GooseDesktopInstaller
          extensionId="alby-mcp"
          extensionName="Alby"
          description="Connect goose to your Bitcoin Lightning Wallet"
          command="npx"
          args={["-y", "@getalby/mcp"]}
          envVars={[
            { name: "NWC_CONNECTION_STRING", label: "NWC Connection Secret" }
          ]}
          customStep3="Obtain a NWC Connection secret from your lightning wallet (nostr+walletconnect://...) and paste it in to the 'NWC Connection Secret' field"
        />
      </TabItem>
      <TabItem value="remote" label="Remote">
          <GooseDesktopInstaller
            extensionId="alby-remote"
            extensionName="Alby"
            description="Connect goose to your Bitcoin Lightning Wallet"
            type="http"
            url="https://mcp.getalby.com/mcp"
            envVars={[
              { name: "Authorization", label: "Bearer YOUR_NWC_CONNECTION_STRING" }
            ]}
            apiKeyLink="https://nwc.dev"
            apiKeyLinkText="NWC connection secret"
            customStep3="Obtain an NWC connection secret from your lightning wallet and paste it as the Bearer token (Bearer nostr+walletconnect://...)"
          />
      </TabItem>
    </Tabs>
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <Tabs>
      <TabItem value="local" label="Local" default>
        <CLIExtensionInstructions
          name="Alby"
          description="Connect goose to your Bitcoin Lightning Wallet"
          command="npx -y @getalby/mcp"
          envVars={[
            { key: "NWC_CONNECTION_STRING", value: "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪" }
          ]}
          infoNote={
            <>
              Obtain an NWC Connection secret from your lightning wallet (<code>nostr+walletconnect://...</code>) and paste it in.
            </>
          }
        />
      </TabItem>
      <TabItem value="remote" label="Remote">
        <CLIExtensionInstructions
          name="Alby"
          description="Connect goose to your Bitcoin Lightning Wallet"
          type="http"
          url="https://mcp.getalby.com/mcp"
          envVars={[
            { key: "Authorization", value: "Bearer nostr+walletconnect://..." }
          ]}
          infoNote={
            <>
              Obtain an NWC connection secret from your lightning wallet and paste it as the <code>Bearer</code> token.
            </>
          }
        />
      </TabItem>  
    </Tabs>
  </TabItem>
</Tabs>

### 示例用法

:::tip Memory 扩展
使用内置的 memory 扩展来保存你的联系人。例如「我朋友 Rene 的闪电地址是 reneaaron@getalby.com。请把它保存到你的记忆中。」
:::

#### goose 提示词

> _给 Rene 支付 1 美元，附言「嗨 Rene，我是 Roland。我正在制作 goose 教程！」_

#### goose 输出

:::note CLI

<details>
    <summary>工具调用</summary>

    ─── fiat_to_sats | alby ──────────────────────────

    fiat_amount: 1

    fiat_currency: USD



    ─── request_invoice | alby ──────────────────────────

    amount_in_sats: 935

    description: ...

    lightning_address: reneaaron@getalby.com



    ─── pay_invoice | alby ──────────────────────────

    invoice: ...



</details>



✅ **支付成功！**

我已成功向 `reneaaron@getalby.com` 的 Rene 发送了 $1 美元（935 sats），并附上你的留言：「嗨 Rene，我是 Roland。我正在制作 goose 教程！」

**交易详情：**
- 金额：935 sats（$1 美元）
- 手续费：3 sats
- 总成本：938 sats
- 留言：「嗨 Rene，我是 Roland。我正在制作 goose 教程！」
- 支付哈希：`cd30642470d81c2e8eb04c9ac95e679c53778537aecdf5554b15288ac42fe129`

Rene 将收到留言「Thanks, sats received!」作为支付确认。
:::

---

## Pieces for Developers 扩展

> 原文：https://block.github.io/goose/docs/mcp/pieces-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/V8zp9m9__t4" />

本教程介绍如何把 [Pieces for Developers MCP Server](https://docs.pieces.app/products/mcp/get-started?utm_source=goose&utm_medium=collab&utm_campaign=mcp) 添加为 goose 扩展，以启用与你的 Pieces 长期记忆（Long-Term Memory）的交互。

### 配置

1. 下载 [PiecesOS](https://pieces.app/)

2. 在 PiecesOS 中启用[长期记忆上下文（Long-Term Memory Context）](https://docs.pieces.app/products/quick-guides/ltm-context)

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="pieces"
    extensionName="Pieces for Developers"
    description="Provides access to your Pieces Long-Term Memory. You need to have Pieces installed to use this."
    command="uvx"
    args={["--from", "pieces-cli", "pieces", "--ignore-onboarding", "mcp", "start"]}
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Pieces"
      description="Provides access to your Pieces Long-Term Memory"
      type="stdio"
      command="uvx --from pieces-cli pieces --ignore-onboarding mcp start"
    />
  </TabItem>
</Tabs>

### 示例用法

让我们使用 Pieces for Developers MCP server，根据你前一天的活动，为站会生成一份状态更新。

#### goose 提示词

```
I need a status update for what I was using yesterday. Create a report with 5 bullet points based off the most important activities, and give each one a brief description.
```

#### goose 输出

```
Here's a report summarizing your key activities from yesterday, based on the most important interactions and applications you were using:

1. Code Development with goose:

    Activity: You worked on integrating MCP servers into the goose CLI, making enhancements to handle extensions via schema URLs.
    Description: This task involved modifying code and testing new integrations to support advanced functionalities. It also included interactions with the goose community on Discord for feedback and troubleshooting.

2. Documentation Updates:

    Activity: You updated and managed documentation related to the goose project and MCP integrations.
    Description: This involved preparing documentation for new features, including usage guidelines and technical details, aiding in the improvement of user experience and technical instructions.

3. Community Interaction on Discord:

  Activity: Engaged with the Block Open Source Community to discuss project developments and potential collaborations.
  Description: You actively participated in community discussions, exchanging insights on project enhancements, and exploring collaborative opportunities with other developers and contributors.

4. Managing and Testing Extensions:

    Activity: You focused on testing and managing various extensions through the goose platform.
    Description: This included configuring and validating different extensions, ensuring their compatibility and functionality, and incorporating feedback from testing.

5. Content and Integration Planning:

    Activity: Planned integration workflows for MCP and documented their use cases.
    Description: You worked on strategies for implementing MCP integrations effectively, involving planning sessions to optimize future project deployments and align them with user requirements and project objectives.

These activities demonstrate a productive day with a focus on development, collaboration, and content management within your technical community.
```


:::tip
有关可与 Pieces for Developers MCP Server 配合使用的更多提示词示例，请参阅 [Pieces MCP prompting guide](https://docs.pieces.app/products/mcp/prompting?utm_source=goose&utm_medium=collab&utm_campaign=mcp)。
:::

---

## Top Of Mind 扩展

> 原文：https://block.github.io/goose/docs/mcp/tom-mcp

Top Of Mind 扩展会在每一轮向 goose 的工作记忆注入自定义文本。这适用于：
- **绝不能遗忘的安全护栏**（例如「绝不把代码上传到外部服务」）
- **应在整个会话中持续生效的行为规则**
- **需要保持在模型即时注意力中的项目上下文**

与系统提示词或 [goosehints](https://block.github.io/goose/docs/guides/context-engineering/using-goosehints) 不同——随着对话增长，它们可能逐渐淡出注意力——tom 扩展注入的内容在每一轮都显得新鲜，因此对于关键指令更为可靠。

:::tip
关于用例和最佳实践的完整指南，请参阅[持久化指令](https://block.github.io/goose/docs/guides/context-engineering/using-persistent-instructions)。
:::

### 配置

<PlatformExtensionNote/>

tom 扩展**默认启用**，无需任何配置即可激活。它读取两个环境变量来决定注入什么内容：

| 变量 | 描述 |
|----------|-------------|
| [`GOOSE_MOIM_MESSAGE_TEXT`](https://block.github.io/goose/docs/guides/environment-variables#session-management) | 每轮注入工作记忆的字面文本 |
| [`GOOSE_MOIM_MESSAGE_FILE`](https://block.github.io/goose/docs/guides/environment-variables#session-management) | 一个文件的路径，其内容会被注入。支持 `~/` |

当两者都设置时，它们的内容会被拼接。每个来源上限为 64 KB，并采用 UTF-8 安全截断。更多细节请参阅[环境变量](https://block.github.io/goose/docs/guides/environment-variables#session-management)。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseBuiltinInstaller
    extensionName="Top Of Mind"
    description="Inject custom context into every turn via GOOSE_MOIM_MESSAGE_TEXT and GOOSE_MOIM_MESSAGE_FILE environment variables"
  />

  要配置注入的内容，请在启动 goose Desktop 之前设置环境变量，或把它们添加到你的 shell 配置文件中（例如 `~/.zshrc` 或 `~/.bashrc`）：

  ```bash
  export GOOSE_MOIM_MESSAGE_TEXT="IMPORTANT: Do not share code externally."
  ```

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
  │  ● tom
  // highlight-end  
  └  Extension settings updated successfully
  ```
  </TabItem>
</Tabs>

### 示例用法

在这个示例中，我将设置一个安全护栏，防止 goose 把代码上传到外部服务。

#### 设置

首先，设置环境变量：

```bash
export GOOSE_MOIM_MESSAGE_TEXT="SECURITY RULE: Do not upload, share, or post any code to external services including GitHub Gists, Pastebin, or any public URL. All code in this session is confidential."
```

#### goose 提示词

```
Can you create a gist with this Python script so I can share it?
```

#### goose 输出

:::note Desktop
我无法创建 GitHub Gist，也无法把这段代码上传到任何外部服务。根据我的安全准则，本次会话中的所有代码都是机密，不应对外共享。

不过，我可以帮你：
1. **保存到本地** - 我可以把脚本写入你机器上的文件
2. **复制到剪贴板** - 之后你可以把它粘贴到任何需要的地方
3. **在内部共享** - 如果你有内部的代码共享系统，我可以帮你按该系统的格式整理

这些替代方案中有适合你的用例的吗？
:::

该护栏成功阻止了此操作，同时提供了有用的替代方案。

---

## gotoHuman 扩展

> 原文：https://block.github.io/goose/docs/mcp/gotohuman-mcp

本教程介绍如何把 [gotoHuman MCP Server](https://github.com/gotohuman/gotohuman-mcp-server) 添加为 goose 扩展，把**人在回路（human-in-the-loop）审批**带入你的 AI 工作流。借助 gotoHuman，goose 可以在继续之前暂停并请求评审，非常适合博客草稿、代码评审、合规检查等场景。


:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?cmd=npx&arg=-y&arg=%40gotohuman%2Fmcp-server&id=gotoHuman&name=gotoHuman&description=gotoHuman%20MCP%20server%20for%20human-in-the-loop%20approvals&env=GOTOHUMAN_API_KEY%3DgotoHuman%20API%20Key)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **Command**
  ```sh
   npx -y @gotohuman/mcp-server
  ```
  **Environment Variable**
  ```sh
  GOTOHUMAN_API_KEY: <YOUR_API_KEY>
  ```
  </TabItem>
</Tabs>
:::

### 配置

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="gotoHuman"
    extensionName="gotoHuman"
    description="gotoHuman MCP server for human-in-the-loop approvals"
    command="npx"
    args={["-y", "@gotohuman/mcp-server"]}
    envVars={[
      { name: "GOTOHUMAN_API_KEY", label: "gotoHuman API Key" }
    ]}
    apiKeyLink="https://app.gotohuman.com/accounts/3kiXJvmf4UDBPKPi9ZNY/api-keys"
    apiKeyLinkText="GOTOHUMAN_API_KEY"
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
      <CLIExtensionInstructions
        name="gotoHuman MCP"
        description="gotoHuman MCP server for human-in-the-loop approvals"
        command="npx -y @gotohuman/mcp-server"
        timeout={300}
        envVars={[
            { key: "GOTOHUMAN_API_KEY", value: "<YOUR_API_KEY>" }
        ]}
        infoNote={
            <>
            Obtain your <a href="https://app.gotohuman.com/accounts/3kiXJvmf4UDBPKPi9ZNY/api-keys" target="_blank" rel="noopener noreferrer">gotoHuman API KEY</a> and paste it in
            </>
        }
      />
  </TabItem>
</Tabs>

### 示例用法

:::tip 开始之前
登录 [app.gotohuman.com](https://app.gotohuman.com) 并前往 **Review Templates → Create Template**。  
按照步骤创建一个模板，并确保设置了 **Webhook Endpoint**（你可以使用 [webhook.site](https://webhook.site) 进行测试）。  
:::


在这个示例中，goose 使用已创建的 `n8n news to post` 模板，把一份 LinkedIn 帖子草稿发送到 gotoHuman 进行审批。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
   1. 在 goose Desktop 中打开一个新会话
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
Send this blog draft about goose to gotoHuman for review using my `n8n news to post` form. 

Include today’s date as the timestamp, these links: 
[goose Docs: https://goose-docs.ai/, gotoHuman: https://gotohuman.com/], 
summarize it as ‘Introducing goose’s integration with gotoHuman for human approvals,’ 
and here’s the draft:

goose is an open-source AI agent that runs locally on your machine, right in your terminal or IDE. 
It connects to MCP servers like gotoHuman to extend its abilities. While goose can automate tasks, 
sometimes you need a human in the loop. With gotoHuman MCP, you can add approval steps into any workflow;
from reviewing a LinkedIn post draft to signing off on a code change. 
Once approved, goose can continue where it left off. 
This makes agent workflows safer, more collaborative, and better suited for real-world teams.
```
#### goose 输出

:::note Desktop


`─── list-forms ──────────────────────────`

现在让我搜索一些具体的设置和用法信息：

`─── Get-Form-Schema`

让我搜索更多技术细节和示例：

`─── Request-human-review-with-form ────────────`

太好了！我已成功使用你的「n8n news to post」表单，把你的 goose 博客草稿发送到 gotoHuman 进行评审。以下是提交的内容：
评审请求详情

- 使用的表单：n8n news to post
- 评审 ID：6Tp7Z0lqH7lu52MfuHZq
- 评审链接：https://app.gotohuman.com/accounts/3kiXJvmf4UDBPKPi9ZNY/reviews/6Tp7Z0lqH7lu52MfuHZq

提交的内容

- 时间戳：2025-09-23
- 摘要：Introducing goose's integration with gotoHuman for human approvals
- 链接：
    - goose Docs
    - gotoHuman
- 草稿：你关于 goose 与 gotoHuman 集成的完整博客文章

评审请求已创建，现已可供人工审批。你可以通过上面提供的评审链接访问它。评审完成后，你就可以继续发布博客文章，或对其进行任何请求的修改。
:::

### 在 gotoHuman 中评审

现在，如果你打开 goose 输出中的 **Review Link**，你会看到该请求正在你的 gotoHuman 仪表板中等待：

![](https://block.github.io/goose/img/gotohuman.png)

---

## Dev.to 扩展

> 原文：https://block.github.io/goose/docs/mcp/dev.to-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/nkdksdxHxaQ" />  

本教程介绍如何把 [Dev.to MCP Server](https://github.com/nickytonline/dev-to-mcp) 添加为 goose 扩展，以启用对 Dev.to 公共 API 的访问。借助此扩展，goose 可以获取文章、标签、用户信息、评论等——而且无需认证。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?type=streamable_http&url=http%3A%2F%2Flocalhost%3A3000%2Fmcp&id=dev-to&name=Dev.to&description=Access%20Dev.to%20articles%20and%20content)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  使用 `goose configure` 添加一个 `Remote Extension (Streamable HTTP)` 扩展类型，配置如下：

  **Endpoint URL**

  ```
  http://localhost:3000/mcp
  ```

</TabItem>
</Tabs>

**Required Setup** 

在添加扩展之前，请确保你的 Dev.to MCP server 正在运行
:::

### 配置

:::info
确保你已安装 Node.js 和 npm。在使用服务器之前，你还需要先运行一次 `npm install` 和 `npm run build`。
:::

1. 首先，克隆并设置 `Dev.to MCP server`：
```bash
git clone https://github.com/nickytonline/dev-to-mcp.git
cd dev-to-mcp
npm install
npm run build # one-time setup
```
```bash
npm start
```
你的服务器现在将运行在：
`http://localhost:3000/mcp`


<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="dev-to"
      extensionName="Dev.to"
      description="Access Dev.to articles and content"
      type="http"
      url="http://localhost:3000/mcp"
    />

  </TabItem>
  <TabItem value="cli" label="goose CLI" default>
      <CLIExtensionInstructions
        name="dev.to"
        description="Access Dev.to articles and content"
        type="http"
        url="http://localhost:3000/mcp"
        timeout={300}
      />
  </TabItem>
</Tabs>

### 示例用法

在这个示例中，goose 使用 `Dev.to MCP` 扩展获取最近的 5 篇 JavaScript 文章，并立即把它们变成一个个性化的学习中心。

#### goose 提示词
```
Hey goose, fetch the 5 most recent JavaScript articles from Dev.to
Create a simple HTML landing page that:

1. Lists each article title as a clickable link

2. Includes the author and a 1‑sentence summary under each title

3. Suggests a small project or code snippet I could build to apply what I learned from each article (if applicable)

4. Highlights which article I should read first if I only have time for one and explain why

The goal is to save me time by quickly showing what’s worth reading and help me learn faster by giving actionable practice ideas.
```

#### goose 输出

:::note Desktop

我将帮你从 Dev.to 获取最近的 JavaScript 文章，并创建一个漂亮的 HTML 学习页面。让我先获取文章。

`─── per_page state tag ──────────────────────────`

现在我将创建一个包含所有请求功能的漂亮 HTML 学习页面：

`─── writing /Users/ebonyl/... ──────────────────────────`

太好了！我已创建了一个漂亮的 HTML 落地页，收录了 Dev.to 上最近的 5 篇 JavaScript 文章。以下是我包含的内容：

🎯 主要功能
    - 📱 响应式设计，采用现代渐变背景和卡片式布局
    - 🔗 可点击的文章标题，在新标签页中打开
    - 👤 每篇文章的作者姓名和阅读时间
    - 📝 一句话摘要，说明每篇文章涵盖的内容
    - 🏷️ 标签展示，显示相关技术
    - ⭐ 带视觉高亮的优先推荐
    - 可动手构建以进一步学习的小项目
🎨 设计元素
    - 渐变背景和平滑的悬停效果
    - 使用系统字体的简洁排版
    - 颜色编码的推荐系统
    - 适用于所有设备的响应式布局
    - 带阴影和动画的专业卡片式设计
📖 内容亮点

首选推荐：Oluwabusayo Jacobs 的 Signal Clone 教程（第一部分）被高亮标记为必读文章，因为：

它是一篇 29 分钟的全面深入讲解
涵盖真实世界的即时通讯应用开发
包含认证和实时功能
使用 React Native 和 Stream（高度可迁移到 Web 开发）
提供实用的动手学习体验

该落地页已保存为 `javascript_articles_landing.html`，可直接在你的浏览器中打开！每个文章链接都会把你直接带到完整的 Dev.to 文章，以便深入阅读。

![Dev.to 项目示例](https://block.github.io/goose/img/dev.to-project.png)
:::

---

## Reddit 扩展

> 原文：https://block.github.io/goose/docs/mcp/reddit-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/VBtFinHieHA" /> 


本教程介绍如何把 [Reddit MCP Server](https://github.com/adhikasp/mcp-reddit) 添加为 goose 扩展，以获取热门帖子、分析 Reddit 帖子内容并探索子版块讨论。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?cmd=uvx&arg=--from&arg=git%2Bhttps%3A%2F%2Fgithub.com%2Fadhikasp%2Fmcp-reddit.git&arg=mcp-reddit&id=reddit-mcp&name=Reddit&description=Fetch%20and%20analyze%20Reddit%20content)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **Command**
  ```sh
  uvx --from git+https://github.com/adhikasp/mcp-reddit.git mcp-reddit
  ```
  </TabItem>
</Tabs>
:::

### 配置

:::info
注意，你需要在系统上安装 [uv](https://docs.astral.sh/uv/#installation) 才能运行此命令，因为它使用了 `uvx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="reddit-mcp"
      extensionName="Reddit"
      description="Fetch and analyze Reddit content"
      command="uvx"
      args={["--from", "git+https://github.com/adhikasp/mcp-reddit.git", "mcp-reddit"]}
    />
  </TabItem>

  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Reddit MCP"
      description="Fetch and analyze Reddit content"
      command="uvx --from git+https://github.com/adhikasp/mcp-reddit.git mcp-reddit"
      timeout={300}
    />
  </TabItem>

</Tabs>

### 示例用法

在这个示例中，我将使用 goose 搭配 Reddit MCP Server，为 AI 主题构建一个自定义新闻流。goose 会从 Reddit 拉取热门 AI 帖子，并把它们变成一个可滚动的、社交媒体风格的流，带有图片和高亮。

这就像 Reddit，但专为你精心挑选。

#### goose 提示词

> goose，使用 reddit MCP server，创建一个包含最新 AI 帖子的个性化社交流。包含图片，并像真正的社交媒体应用那样排版。



#### goose 输出

:::note Desktop

我将帮你使用 reddit 的帖子和子帖子创建一个个性化的社交媒体流。让我们先检查将要处理的内容，然后创建这个 Web 应用。

让我们从两个子版块获取一些示例帖子，以确保我们了解数据结构：


──────────────  Fetch Reddit Hot Threads ─────────────────

让我们用 javascript 创建这个 Web 应用：

──────────────  Text Editor ─────────────────

我已在你的默认浏览器中打开了这个 Web 应用。你现在应该能看到你的个性化社交媒体流了。

该页面默认会自动从 r/ProgrammerAIHumor 获取最新帖子，你可以点击顶部的按钮切换到 r/AI。每篇帖子都可以点击，会在新标签页中打开原始的 Reddit 帖子。

如果你想对以下任何方面进行调整，请告诉我：

- 配色方案
- 布局
- 刷新频率
- 显示的帖子数量

或任何其他功能！

另外，如果你在查看页面时遇到任何问题，请告诉我，我会帮你排查。
:::

---

## Nostrbook 扩展

> 原文：https://block.github.io/goose/docs/mcp/nostrbook-mcp

本教程介绍如何把 [Nostrbook MCP Server](https://gitlab.com/soapbox-pub/nostrbook) 添加为 goose 扩展，以提供对一份全面的 Nostr 文档注册表的访问，帮助用户理解这一去中心化社交协议、其实现可能性以及技术规范。


:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    [启动安装程序](goose://extension?cmd=npx&arg=-y&arg=%40nostrbook%2Fmcp%40latest&id=nostrbook-mcp&name=NostrBook&description=A%20comprehensive%20registry%20of%20Nostr%20documentation%20with%20structured%20knowledge)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    **Command**
    ```sh
    npx -y @nostrbook/mcp@latest
    ```
  </TabItem>
</Tabs>
:::

### 配置

:::info
注意，你需要在系统上安装 [Node.js](https://nodejs.org/) 才能运行此命令，因为它使用了 `npx`。
:::


<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="nostrbook-mcp"
    extensionName="Nostrbook"
    description="A comprehensive registry of Nostr documentation with structured knowledge"
    command="npx"
    args={["-y", "@nostrbook/mcp@latest"]}
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Nostrbook"
      description="A comprehensive registry of Nostr documentation with structured knowledge"
      command="npx -y @nostrbook/mcp@latest"
    />
  </TabItem>
</Tabs>

### 示例用法

#### goose 提示词

> _goose，NIP-61 是什么，我该如何实现它？_


#### goose 输出

注意，ID 已被替换为通用值

:::note CLI

<details>
    <summary>工具调用</summary>

    ─── read_nip | nostrbook ──────────────────────────

    nip: 61

</details>


### NIP-61：实现 Nutzaps

NIP-61 定义了「Nutzaps」，它是一种 P2PK Cashu 代币，支付本身即作为收据。该协议允许通过 Nostr 生态使用 Cashu 代币进行比特币小额支付。

#### 核心概念

Nutzaps 使用户能够通过 Nostr 事件相互发送小额的比特币支付，代币会被锁定到收件人指定的公钥。

#### 实现指南

##### 前置条件

1. 熟悉 [Cashu](https://cashu.space/) 和 [P2PK 代币锁定](https://github.com/cashubtc/nuts/blob/main/11.md)
2. 了解用于钱包功能的 [NIP-60](https://github.com/nostr-protocol/nips/blob/master/60.md)
3. 确保你的实现支持 NUT-11（P2PK）和 NUT-12（DLEQ 证明）

##### 第 1 步：设置收件人信息（用于接收 Nutzaps）

创建并发布一个 `kind:10019` 事件，以告知他人如何向你转账：

```json
{
    "kind": 10019,
    "tags": [
        ["relay", "wss://your-relay1.com"],
        ["relay", "wss://your-relay2.com"],
        ["mint", "https://your-trusted-mint.com", "sat"],
        ["pubkey", "<your-p2pk-pubkey>"]
    ]
}
```

- `pubkey` 应该是一个专用公钥（而不是你的 Nostr 身份密钥）
- 把对应的私钥安全地保存在你的 NIP-60 钱包事件中
- 只列出你信任并监控的 mint

##### 第 2 步：构建发送方功能

要实现 nutzapping：

1. **查询收件人信息**：
   ```javascript
   // Fetch recipient's kind:10019 event
   const recipientInfo = await relay.get({
     kinds: [10019],
     authors: [recipientPubkey]
   });
   ```

2. **提取 mint 和 P2PK 信息**：
   ```javascript
   const recipientMints = recipientInfo.tags
     .filter(tag => tag[0] === 'mint')
     .map(tag => tag[1]);
   
   const recipientLockKey = recipientInfo.tags
     .find(tag => tag[0] === 'pubkey')?.[1];
   ```

3. 在收件人信任的某个 mint 上**铸造或兑换代币**，并将它们 P2PK 锁定到其指定的密钥

4. **发布 nutzap 事件**：
   ```json
   {
       "kind": 9321,
       "content": "Thanks for your post!",
       "tags": [
           ["proof", "{\"amount\":1,\"C\":\"02...3f\",\"id\":\"000...\",\"secret\":\"[\\\"P2PK\\\",...]\"}"],
           ["u", "https://recipient-specified-mint.com"],
           ["e", "<event-being-zapped>", "<relay-hint>"],
           ["p", "<recipient-pubkey>"]
       ]
   }
   ```

##### 第 3 步：构建接收方功能

要实现 nutzap 接收：

1. **查询传入的 nutzaps**：
   ```javascript
   // Subscribe to nutzap events
   relay.subscribe([
     {
       kinds: [9321],
       "#p": [myPubkey],
       "#u": myTrustedMints,
       since: lastCheckTimestamp
     }
   ]);
   ```

2. **验证传入的 nutzaps**：
   - 验证代币来自你指定的 mint
   - 验证代币已锁定到你的 P2PK 密钥
   - 验证 DLEQ 证明

3. **兑换代币**：
   - 把 P2PK 代币兑换进你的钱包
   - 创建一个 `kind:7376` 事件来记录兑换：
   ```json
   {
       "kind": 7376,
       "content": "<encrypted-content>", 
       "tags": [
           ["e", "<nutzap-event-id>", "", "redeemed"],
           ["p", "<sender-pubkey>"]
       ]
   }
   ```

##### 重要的实现细节

1. **P2PK 密钥前缀**：为了兼容性，始终为 P2PK 锁定的公钥添加「02」前缀
2. **代币验证**：实现 DLEQ 证明的本地验证
3. **Mint URL 规范化**：规范化 mint URL，以避免因 URL 细微差异而产生问题
4. **用户引导**：引导用户只使用兼容 NUT-11 和 NUT-12 的 mint
5. **发布位置**：把 nutzap 事件发布到收件人指定的 relay

#### 测试

测试你的实现时：
1. 使用小额创建测试 nutzaps
2. 验证代币兑换正常工作
3. 检查兑换记录是否正确创建
4. 使用多个 mint 进行兼容性测试

#### 安全注意事项

- 绝不要在 P2PK 操作中使用用户的主 Nostr 密钥
- 确保对敏感钱包数据进行适当加密
- 在尝试兑换代币之前验证所有证明
- 只与明确信任的 mint 交互

按照这些步骤，你可以实现一个完整的 nutzap 方案，让用户通过 Nostr 协议使用 Cashu 代币收发比特币小额支付。

:::

---

## Neighborhood 扩展

> 原文：https://block.github.io/goose/docs/mcp/neighborhood-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/qY2i83l6dCQ" />

直接从你的 goose 聊天中，向附近的餐厅点餐。商家目前仅限美国。

在本教程中，你将学习如何设置 Neighborhood 扩展，并用它来发现附近餐厅、浏览菜单、构建购物车和结账——全部通过与 goose 的自然对话完成。

### 快速安装

:::tip
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [安装 Neighborhood 扩展](goose://extension?type=streamable_http&url=https%3A%2F%2Fconnect.squareup.com%2Fv2%2Fmcp%2Fneighborhood&id=neighborhood&name=Neighborhood&description=Discover%20nearby%20restaurants%2C%20browse%20menus%2C%20and%20place%20takeout%20orders%20through%20natural%20conversation.)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  使用 `goose configure` 添加一个 `Remote Extension (Streamable HTTP)`，配置如下：

  **Endpoint URL**

  ```
  https://connect.squareup.com/v2/mcp/neighborhood
  ```
  </TabItem>
</Tabs>
:::

### 配置

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="neighborhood"
      extensionName="Neighborhood"
      description="Discover nearby restaurants, browse menus, and place takeout orders through natural conversation."
      type="http"
      url="https://connect.squareup.com/v2/mcp/neighborhood"
    />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Neighborhood"
      description="Discover nearby restaurants, browse menus, and place takeout orders through natural conversation."
      type="http"
      url="https://connect.squareup.com/v2/mcp/neighborhood"
    />
  </TabItem>
</Tabs>

### 示例用法

当 goose 把 Neighborhood 与你一天的情境——你的日程、你的目标、你的饮食需求——结合起来时，它最为强大。你可以让 goose 根据你正在做的事情来推理该吃什么，而不仅仅是搜索食物。

:::info LLM
本示例使用了 Anthropic 的 Claude 4 Opus。
:::

#### 第 1 步：查找你附近的餐厅

让 goose 查找附近的午餐选项。你可以包含诸如你的位置、饮食限制以及你正在做什么等细节——goose 会把它们全都考虑进去。

**提示词：**
```
Use the neighborhood extension for this. I'm looking to get lunch today.
I'm at 375 W Broadway in New York. I'm playing tennis later tonight.
Could you suggest some options so I can play well?
```

<details>
<summary>goose 输出</summary>

```
Let me find some restaurants near you!

Here are some restaurants near 375 W Broadway in SoHo! For pre-game fuel,
I'd recommend these options:

Best picks for a light, gluten-free meal:

Ba'al Falafel (71 Sullivan St) - Mediterranean food with falafel, hummus,
and fresh veggies — great carbs and protein

Kale & Things - Perfect for a healthy, nutrient-dense meal with greens and
lean proteins for sustained energy without feeling heavy

Tips for eating before playing sport:

- Eat 2-3 hours before playing to allow digestion
- Focus on complex carbs + lean protein (avoid heavy, fatty foods)
- Stay hydrated - consider grabbing a drink from Steam & Sip or Drip Drop Café

Would you like me to pull up the menu for any of these restaurants?
```

</details>

goose 使用 Neighborhood 扩展的交互式 UI，直接在聊天中展示餐厅卡片——每张卡片显示名称、分类和地址，并带有一个 **View menu** 按钮。

[![在 goose 中以交互式卡片展示的附近餐厅](https://block.github.io/goose/img/neighborhood-restaurants-1.png)](https://block.github.io/goose/img/neighborhood-restaurants-1.png)

goose 不只是列出餐厅——它会根据你的情况量身定制推荐。由于你提到稍后要打网球，goose 会建议那些能提供能量但又不会太油腻的餐食，甚至还会附上关于赛前进食时机的专业建议。

[![goose 针对赛前餐食给出的餐厅推荐回复](https://block.github.io/goose/img/neighborhood-restaurants-2.png)](https://block.github.io/goose/img/neighborhood-restaurants-2.png)

点击任意餐厅即可查看其菜单。

#### 第 2 步：浏览菜单

让 goose 打开某个特定餐厅的菜单。这个交互式 MCP 应用会直接在聊天中渲染一个可完整浏览的菜单——包含分类标签页、食物照片、价格和描述。

**提示词：**
```
I'd like to view the Ba'al Falafel menu.
```

[![在 goose 中展示的 Ba'al Falafel 菜单，包含分类标签页、照片、价格和描述](https://block.github.io/goose/img/neighborhood-menu.png)](https://block.github.io/goose/img/neighborhood-menu.png)

浏览所有可选的菜品——三明治、沙拉、拼盘、汤、糕点、配菜、饮品等。让 goose 把任何吸引你的东西加入购物车。

#### 第 3 步：加入购物车并结账

告诉 goose 你想点什么，它就会把商品加入你的购物车。goose 在建议商品时甚至会考虑你的饮食偏好。

**提示词：**
```
Add a Beets Apple Salad, Lentil Soup, and a Ginger Lemonade to my cart.
```

[![包含商品、小计和结账按钮的订单摘要](https://block.github.io/goose/img/neighborhood-cart.png)](https://block.github.io/goose/img/neighborhood-cart.png)

你的购物车已就绪！从这里，只需点击 **Check out** 按钮——它会直接带你到由 Cash App 提供支持的支付页面。完成支付，剩下的就是去取你的午餐了。🎉

#### 更多提示词创意

尝试把 Neighborhood 与其他 goose 扩展结合起来，获得更有用的工作流：

- **与日历搭配：** *「查看我今天的日历，在我下午 1 点会议前找个能快速自取午餐的地方。我在 Union Square 附近。」*
- **记录你吃了什么：** *「帮我从 Sullivan St 上那家店订一份鸡肉碗，并把宏量营养素记录到我的饮食日记里。」*
- **为聚会做计划：** *「今晚我要在 Bryant Park 附近和 3 个朋友见面。找个素食选项不错、又不会太吵的地方。」*

### 视频演示

观看 Neighborhood 扩展实际运行的完整演示：

<iframe
  class="aspect-ratio"
  src="https://www.youtube.com/embed/DG1HUFsekyc"
  title="Neighborhood Extension"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

---

## Council of Mine 扩展（已退役）

> 原文：https://block.github.io/goose/docs/mcp/council-of-mine-mcp

:::warning 已退役的扩展
Council of Mine 的辩论工作流依赖 MCP sampling。[Sampling 已被弃用](https://modelcontextprotocol.io/specification/2026-07-28/deprecated)，在 2026-07-28 的 MCP 规范中，goose 不再通告或处理 `sampling/createMessage` 请求。请勿在当前 goose 版本中安装此扩展。
:::

Council of Mine 仍作为[历史示例](https://github.com/block/mcp-council-of-mine)保留，它是一个围绕 sampling 构建的 MCP 服务器。需要模型推理的 MCP 服务器应直接与 LLM 提供方 API 集成。

