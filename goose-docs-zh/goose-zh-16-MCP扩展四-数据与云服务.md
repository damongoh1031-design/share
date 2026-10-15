# goose 官方文档中文手册：第 16 章　MCP 扩展（四）：数据与云服务

## PostgreSQL 扩展

> 原文：https://block.github.io/goose/docs/mcp/postgres-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/PZlYQ5IthYM" />

服务器已归档

PostgreSQL MCP 服务器扩展让 goose 可以直接与你的 PostgreSQL 数据库交互，具备数据库操作、查询和 schema 管理能力。这让你能够通过自然语言交互轻松地操作数据库。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=-y&arg=@modelcontextprotocol/server-postgres&arg=Your%20PostgreSQL%20connection%20URL&id=postgres&name=PostgreSQL&description=PostgreSQL%20database%20integration)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **Command**
```sh
npx -y @modelcontextprotocol/server-postgres postgresql://localhost/mydb
```
  </TabItem>
</Tabs>
:::

### 自定义你的连接

值得注意的是，目前这个 MCP 服务器只允许连接到单个预定义数据库，且连接 URL 必须在命令中指定。这里我们用 `postgresql://localhost/mydb` 作为示例来访问本地数据库，但你可以根据自己的环境进行配置。

PostgreSQL 连接 URL 遵循以下格式：
```
postgresql://username:password@hostname:5432/database
```

其中：
- `username`：你的 PostgreSQL 用户
- `password`：你的 PostgreSQL 密码
- `hostname`：运行 PostgreSQL 的主机（例如 localhost、IP 地址或域名）
- `5432`：PostgreSQL 默认端口（如使用其他端口请修改）
- `database`：你的数据库名称

示例：
- 本地数据库：`postgresql://localhost/mydb`
- 带凭据的本地数据库：`postgresql://myuser:mypass@localhost/mydb`
- 远程数据库：`postgresql://user:pass@db.example.com:5432/production`

:::caution
切勿将带凭据的连接字符串提交到版本控制系统！请使用环境变量或安全的配置管理方式。
:::

### 配置

:::info
注意，你需要在系统上安装 [Node.js](https://nodejs.org/) 才能运行此命令，因为它使用了 `npx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="postgres"
    extensionName="PostgreSQL"
    description="PostgreSQL database integration"
    command="npx"
    args={["-y", "@modelcontextprotocol/server-postgres", "Your PostgreSQL connection URL"]}
  />

  :::info
  请按以下格式输入你的 PostgreSQL 连接 URL：`postgresql://username:password@hostname:5432/database`
  :::

  </TabItem>
  <TabItem value="cli" label="goose CLI">
  1. 运行 `configure` 命令：
```sh
goose configure
```

  2. 选择添加 `Command-line Extension`
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
    │  PostgreSQL
    // highlight-end
    └ 
```

  4. 输入命令及你的数据库连接 URL
```sh
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension (Connect to a new extension) 
    │
    ◇  What would you like to call this extension?
    │  PostgreSQL
    │
    // highlight-start
    ◆  What command should be run?
    │  npx -y @modelcontextprotocol/server-postgres postgresql://localhost/mydb
    // highlight-end
    └ 
```  

  5. 设置超时时间（默认 300 秒通常已足够）
```sh
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension (Connect to a new extension) 
    │
    ◇  What would you like to call this extension?
    │  PostgreSQL
    │
    ◇  What command should be run?
    │  npx -y @modelcontextprotocol/server-postgres postgresql://localhost/mydb
    │
    // highlight-start
    ◆  Please set the timeout for this tool (in secs):
    │  300
    // highlight-end
    └ 
```

  6. 选择是否添加描述。如果你在这里选择「Yes」，系统会提示你为扩展输入一段描述。
```sh
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension (Connect to a new extension) 
    │
    ◇  What would you like to call this extension?
    │  PostgreSQL
    │
    ◇  What command should be run?
    │  npx -y @modelcontextprotocol/server-postgres postgresql://localhost/mydb
    │
    ◇  Please set the timeout for this tool (in secs):
    │  300
    │
    // highlight-start
    ◆  Would you like to add a description?
    │  No
    // highlight-end
    └ 
```

  7. 配置你的 PostgreSQL 连接 URL
```sh
    ┌   goose-configure 
    │
    ◇  What would you like to configure?
    │  Add Extension (Connect to a new extension) 
    │
    ◇  What would you like to call this extension?
    │  PostgreSQL
    │
    ◇  What command should be run?
    │  npx -y @modelcontextprotocol/server-postgres postgresql://localhost/mydb
    │     
    ◇  Please set the timeout for this tool (in secs):
    │  300
    │
    ◇  Would you like to add a description?
    │  No
    │    
    // highlight-start
    ◆  Would you like to add environment variables?
    │  No 
    // highlight-end
    └  Added PostgreSQL extension
```  

  </TabItem>
</Tabs>

### 示例用法

PostgreSQL 扩展让你能够查询和分析数据，或者获取表结构信息。该扩展仅支持*只读*操作，因此你可以用它来获取数据库信息，但不能修改数据库。

你只需用自然语言描述你想做什么，goose 就会借助合适的 SQL 命令和 PostgreSQL 功能帮你完成。

##### goose 提示词
```
Search my database for any students whose current GPA is higher than the average in their current grade level. Tell me their name, grade, and how much they exceed their grade’s average GPA, and the average GPA.
```

##### goose 输出
```
Based on the query results, here are the students who are performing above their grade level average:

Grade 11
  Emma Johnson
    GPA: 4.00
    Grade Average: 3.90
    Exceeds average by: 0.10 points

Grade 12
  John Smith
    GPA: 3.85
    Grade Average: 3.78
    Exceeds average by: 0.08 points

Both students are performing well above their respective grade level averages. Emma Johnson in Grade 11 shows the highest difference above the grade average, exceeding it by 0.10 points, while John Smith in Grade 12 exceeds his grade's average by 0.08 points.
```

---

## MongoDB 扩展

> 原文：https://block.github.io/goose/docs/mcp/mongodb-mcp

[MongoDB MCP 服务器](https://github.com/mongodb-js/mongodb-mcp-server)扩展让 goose 可以直接与你的 MongoDB 数据库交互，具备全面的数据库操作能力，包括查询、文档操作、集合管理和数据库管理。这让你能够通过自然语言交互轻松地操作 MongoDB 数据库。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=-y&arg=mongodb-mcp-server&arg=--connectionString&arg=mongodb://localhost:27017&id=mongodb&name=MongoDB&description=MongoDB%20database%20integration)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **Command**
```sh
npx -y mongodb-mcp-server --connectionString mongodb://localhost:27017
```
  </TabItem>
</Tabs>
:::

### 自定义你的连接

MongoDB MCP 服务器通过连接字符串连接到单个 MongoDB 数据库实例。连接字符串必须使用 `--connectionString` 标志指定。这里我们用 `mongodb://localhost:27017` 作为示例来访问本地 MongoDB 实例，但你可以根据自己的环境进行配置。

MongoDB 连接字符串遵循以下格式：
```
mongodb://username:password@hostname:27017/database
```

其中：
- `username`：你的 MongoDB 用户（本地开发时可省略）
- `password`：你的 MongoDB 密码（本地开发时可省略）
- `hostname`：运行 MongoDB 的主机（例如 localhost、IP 地址或域名）
- `27017`：MongoDB 默认端口（如使用其他端口请修改）
- `database`：你的数据库名称（可选，默认连接到默认数据库）

示例：
- 本地数据库：`mongodb://localhost:27017`
- 带凭据的本地数据库：`mongodb://myuser:mypass@localhost:27017/mydb`
- MongoDB Atlas：`mongodb+srv://user:pass@cluster.mongodb.net/database`

:::caution
切勿将带凭据的连接字符串提交到版本控制系统！请使用环境变量或安全的配置管理方式。对于 MongoDB Atlas，请确保你的 IP 地址已加入白名单，并使用强密码。
:::

### 配置

:::info
注意，你需要在系统上安装 [Node.js](https://nodejs.org/) 才能运行此命令，因为它使用了 `npx`。你还需要一个正在运行的 MongoDB 实例，或对 MongoDB Atlas 的访问权限。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="mongodb"
      extensionName="MongoDB"
      description="MongoDB database integration"
      command="npx"
      args={["-y", "mongodb-mcp-server", "--connectionString", "mongodb://localhost:27017"]}
    />
    
    :::info 配置你的连接字符串
    如有需要，请[更新该扩展](https://block.github.io/goose/docs/getting-started/using-extensions#updating-extension-properties)，使其与你的 [MongoDB 环境](#customizing-your-connection)匹配。例如，将 `command` 属性中的连接字符串改为 `mongodb://username:password@hostname:27017/database` 格式。
    :::

  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="MongoDB"
      description="MongoDB database integration"
      command="npx -y mongodb-mcp-server --connectionString mongodb://localhost:27017"
      commandNote={
        <>
          Replace <code>mongodb://localhost:27017</code> with the actual MongoDB connection string that matches your <a href="#customizing-your-connection">MongoDB environment</a>.
        </>
      }
    />
  </TabItem>
</Tabs>

### 可用操作

MongoDB 扩展通过自然语言交互提供全面的数据库管理能力。你可以执行多种操作，包括：

#### 查询操作
- 使用复杂过滤器和排序**查找文档**
- 使用 MongoDB 强大的聚合管道**聚合数据**
- 对集合中的文档**计数**，可选用过滤器

#### 文档管理
- **插入**单个或多个文档
- 按指定条件**更新**一个或多个文档
- **删除**特定文档或批量删除

#### 集合与数据库管理
- **创建索引**以优化查询性能
- **重命名集合**以更好地组织
- 不再需要时**删除集合**
- **删除整个数据库**（请谨慎使用！）

#### Schema 与分析
- **分析集合 schema**以了解文档结构
- **列出数据库和集合**以便探索
- **查看集合索引**及其配置
- **检查数据库统计信息**和集合存储大小

你只需用自然语言描述你想完成什么，goose 就会帮你安全高效地执行合适的 MongoDB 操作。

### 示例用法

##### goose 提示词
```
Update all users in the premium tier who haven't logged in for more than 90 days - set their status to 'inactive' and add a note about when this change was made.
```

##### goose 输出
```
I've successfully updated inactive premium users using updateMany:

db.users.updateMany(
  {
    subscriptionTier: "premium",
    lastLogin: { $lt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000) }
  },
  {
    $set: {
      status: "inactive",
      inactiveNote: "Auto-updated to inactive on 2025-05-25 due to 90+ days of inactivity",
      lastModified: new Date()
    }
  }
)

Operation Result:
{
  acknowledged: true,
  matchedCount: 23,
  modifiedCount: 23,
  upsertedId: null,
  upsertedCount: 0
}

Updated 23 premium tier users who hadn't logged in since February 24, 2025. Each document now has:
• status: "inactive"
• inactiveNote: explains the automatic status change
• lastModified: timestamp of this operation

Consider sending re-engagement emails to these users or reviewing their subscription status.
```

---

## Supabase 扩展

> 原文：https://block.github.io/goose/docs/mcp/supabase-mcp

本教程介绍如何将 [Supabase MCP 服务器](https://github.com/supabase-community/supabase-mcp)添加为 goose 扩展，以便与你的 Supabase 项目交互、管理表、查询数据、部署 Edge Functions，并直接与你的 Supabase 后端交互。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?type=streamable_http&url=https%3A%2F%2Fmcp.supabase.com%2Fmcp&id=supabase&name=Supabase&description=Connect%20your%20Supabase%20projects%20to%20AI%20assistants.%20Manage%20tables%2C%20query%20data%2C%20deploy%20Edge%20Functions%2C%20and%20interact%20with%20your%20Supabase%20backend%20directly%20from%20your%20MCP%20client.)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  使用 `goose configure` 添加 `Remote Extension (Streamable HTTP)` 类型的扩展，并填入：
  
  **Endpoint URL**
```
https://mcp.supabase.com/mcp
```
  </TabItem>
</Tabs>
:::

### 配置

#### Supabase 远程 MCP

Supabase MCP 服务器由 Supabase 托管，并提供基于 OAuth 的身份验证。当你连接时，会被重定向到 supabase.com 登录你的账户。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

    <GooseDesktopInstaller
      extensionId="supabase"
      extensionName="Supabase"
      description="Connect your Supabase projects to AI assistants. Manage tables, query data, deploy Edge Functions, and interact with your Supabase backend directly from your MCP client."
      type="http"
      url="https://mcp.supabase.com/mcp"
      envVars={[]}
    />

  </TabItem>
  <TabItem value="cli" label="goose CLI">

    <CLIExtensionInstructions
      name="Supabase"
      description="Connect your Supabase projects to AI assistants. Manage tables, query data, deploy Edge Functions, and interact with your Supabase backend directly from your MCP client."
      type="http"
      url="https://mcp.supabase.com/mcp"
      timeout={300}
      envVars={[]}
    />
    
  </TabItem>
</Tabs>

##### OAuth 流程

当你第一次通过 goose 连接到 Supabase MCP 服务器时，浏览器中会打开一个 OAuth 窗口。按照提示授权访问你的 Supabase 项目。

:::note 安全说明
Supabase MCP 服务器会授予对你数据库和项目管理能力的访问权限。在执行前务必审查 LLM 请求的操作，并确保你在合适的环境（开发、预发布、生产）中操作。
:::

### 示例用法

#### 示例 1：列出你的 Supabase 项目

获取你所有 Supabase 项目及其配置的概览。

##### goose 提示词

```
List all my Supabase projects
```

##### goose 输出

:::note 桌面版

```
Here are your Supabase projects:

1. my project (ID: abc123xyz789defg)
   - Region: US West 1
   - Created: October 30, 2025
   - Status: ACTIVE_HEALTHY
   - Database: PostgreSQL 17.6.1.031 (Engine v17)
   - Host: db.abc123xyz789defg.supabase.co

2. new project (ID: jkl456mno012pqrs)
   - Region: US West 1
   - Created: October 31, 2025
   - Status: INACTIVE
   - Database: PostgreSQL 17.6.1.032 (Engine v17)
   - Host: db.jkl456mno012pqrs.supabase.co

Would you like more detailed information about any specific project?
```

:::

#### 示例 2：查询数据库表

发现并查询你 Supabase 项目中的表。

##### goose 提示词

```
What tables exist in my project?
```

##### goose 输出

:::note 桌面版

```
Tables in my project (public schema):

1. users
   - RLS Enabled: Yes
   - Row count: 150
   - Columns: id (uuid), email (text), name (text), created_at (timestamptz), role (text)
   - Primary Key: id
   - Foreign Keys: Referenced by posts.user_id, profiles.user_id

2. posts
   - RLS Enabled: Yes
   - Row count: 342
   - Columns: id (uuid), user_id (uuid), title (text), content (text), created_at (timestamptz)
   - Primary Key: id
   - Foreign Keys: References users.id, referenced by comments.post_id

3. comments
   - RLS Enabled: Yes
   - Row count: 1089
   - Columns: id (uuid), post_id (uuid), user_id (uuid), content (text), created_at (timestamptz)
   - Primary Key: id
   - Foreign Keys: References posts.id, references users.id

4. profiles
   - RLS Enabled: Yes
   - Row count: 150
   - Columns: id (uuid), user_id (uuid), bio (text), avatar_url (text), updated_at (timestamptz)
   - Primary Key: id
   - Foreign Keys: References users.id

5. categories
   - RLS Enabled: No
   - Row count: 12
   - Columns: id (uuid), name (text), description (text), created_at (timestamptz)
   - Primary Key: id

Would you like to query data from any of these tables?
```

:::

#### 示例 3：部署 Edge Function

直接通过 goose 部署和管理 Supabase Edge Functions。

##### goose 提示词

```
Deploy a new Edge Function called 'hello-world' that returns a simple JSON response
```

##### goose 输出

:::note 桌面版

```
Edge Function deployed successfully!

Function Name: hello-world
Version: 1
Status: ACTIVE
Function ID: c4e03748-3e72-45e2-bdca-03f7e4800874
Project: my project (tabowbdrhvtlvzvfyinw)
Entrypoint: index.ts
JWT Verification: Enabled
Created: November 8, 2025

Function code:
~~~typescript
Deno.serve(async (req) => {
  return new Response(
    JSON.stringify({ message: "Hello World!" }),
    { headers: { "Content-Type": "application/json" } },
  )
})
~~~

Endpoint:
https://tabowbdrhvtlvzvfyinw.supabase.co/functions/v1/hello-world

You can test the function by sending a request to the endpoint above.
```

:::

### 其他资源

如需了解 Supabase MCP 服务器及其能力的更多信息，请访问：
- [Supabase MCP Server GitHub Repository](https://github.com/supabase-community/supabase-mcp)
- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Dashboard](https://supabase.com/dashboard)

---

## Neon 扩展

> 原文：https://block.github.io/goose/docs/mcp/neon-mcp

本教程介绍如何将 [Neon MCP 服务器](https://github.com/neondatabase/mcp-server-neon)添加为 goose 扩展，以便与你的 Neon Postgres 数据库交互，并管理你的项目、分支等。

Neon 提供两个版本的 MCP 服务器：

1. **远程 MCP 服务器**，由 Neon 托管，会把你重定向到 neon.com 登录你的 Neon 账户。
2. **本地 MCP 服务器**，你可以在自己的机器上使用 API key 运行，以连接特定的组织或你的个人账户。

:::warning 安全说明
Neon MCP 服务器会授予强大的数据库管理能力，且仅供本地开发使用——在执行前务必审查 LLM 请求的操作，并避免在生产环境中使用。
:::

### 配置

<Tabs groupId="remote-or-local">
  <TabItem value="remote" label="Neon Remote MCP" default>
  :::tip 快速安装
  <Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
    [启动安装器](goose://extension?type=streamable_http&url=https%3A%2F%2Fmcp.neon.tech%2Fmcp&id=neon&name=Neon&description=Manage%20Neon%20Postgres%20databases%2C%20projects%2C%20and%20branches)
    </TabItem>
    <TabItem value="cli" label="goose CLI">
    使用 `goose configure` 添加 `Remote Extension (Streamable HTTP)` 类型的扩展，并填入：

    **Endpoint URL**
```
https://mcp.neon.tech/mcp
```
    </TabItem>
  </Tabs>
  :::

  :::info OAUTH 流程
  浏览器中会打开一个 OAuth 窗口。按照提示授权访问你的 Neon 账户。
  :::

  <Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
      <GooseDesktopInstaller
        extensionId="neon"
        extensionName="Neon"
        description="Manage Neon Postgres databases, projects, and branches"
        type="http"
        url="https://mcp.neon.tech/mcp"
      />
    </TabItem>
    <TabItem value="cli" label="goose CLI">
      <CLIExtensionInstructions
        name="neon-mcp-remote"
        description="Manage Neon Postgres databases, projects, and branches"
        type="http"
        url="https://mcp.neon.tech/mcp"
        timeout={300}
      />
      </TabItem>
  </Tabs>

  </TabItem>

  <TabItem value="local" label="Neon Local MCP">
  :::tip 快速安装
  <Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
      [启动安装器](goose://extension?cmd=npx&arg=-y&arg=%40neondatabase%2Fmcp-server-neon&arg=start&arg=%3CYOUR_NEON_API_KEY%3E&id=neon&name=Neon&description=Manage%20your%20Neon%20Postgres%20databases%2C%20projects%2C%20and%20branches)
    </TabItem>
    <TabItem value="cli" label="goose CLI">
      **Command**
```sh
npx -y @neondatabase/mcp-server-neon start <YOUR_NEON_API_KEY>
```
      
      无需环境变量。
    </TabItem>
  </Tabs>
  :::

  :::info 前提条件

  - 系统上已安装 [Node.js](https://nodejs.org/)（v18.0.0 或更高版本）以运行此命令，因为它使用了 `npx`
  - 用于向你的 Neon 账户验证 Neon MCP 服务器的 Neon API key。你可以在 [Neon Console](https://console.neon.tech) 的 Profile 设置中创建一个。详细说明请参阅 [Neon 关于 API Keys 的文档](https://neon.com/docs/manage/api-keys#creating-api-keys)。
  :::

  <Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="neon"
      extensionName="Neon"
      description="Manage your Neon Postgres databases, projects, and branches"
      command="npx"
      args={["-y", "@neondatabase/mcp-server-neon", "start", "<YOUR_NEON_API_KEY>"]}
    />
    </TabItem>

    <TabItem value="cli" label="goose CLI">
      <CLIExtensionInstructions
        name="Neon MCP"
        description="Manage Neon Postgres databases, projects, and branches"
        command="npx -y @neondatabase/mcp-server-neon start <YOUR_NEON_API_KEY>"
        timeout={300}
      />
    </TabItem>
  </Tabs>

  </TabItem>
</Tabs>

关于所有安装和配置选项，请参阅[官方 Neon MCP 服务器文档](https://neon.com/docs/ai/neon-mcp-server)。

### 示例用法 1

获取你所有 Neon 数据库项目及其配置的概览。

#### goose 提示词

```
List my Neon projects
```

#### goose 输出

```
I'll help you list your Neon projects using the neon__list_projects tool. By default, it will show the first 10 projects.

Here are your Neon projects:

1. laravel-test (ID: mute-mountain-08595850)
- Region: AWS US East 2
- Created: July 23, 2025
- PostgreSQL: v17

2. rls-test (ID: noisy-hill-99207787)
- Region: AWS US East 2
- Created: July 20, 2025
- PostgreSQL: v17

3. neon-auth-test (ID: rapid-pond-81053507)
- Region: Azure East US 2
- Created: July 7, 2025
- PostgreSQL: v17

4. saas-starter-kit-nextjs (ID: misty-poetry-78149700)
- Region: AWS US West 2
- Created: June 23, 2025
- PostgreSQL: v17
- Note: Has logical replication enabled

5. neon-auth-mcp-oauth (ID: gentle-base-21700263)
- Region: AWS US West 2
- Created: June 4, 2025
- PostgreSQL: v17

All projects are running PostgreSQL 17 and have autoscaling configured between 1-2 compute units. Would you like more detailed information about any specific project?
```

### 示例用法 2

发现在特定项目中存在哪些表和 schema。

#### goose 提示词

```
What tables do I have in my neon-auth-mcp-oauth project?
```

#### goose 输出

```
In your neon-auth-mcp-oauth project, there is one table:

users_sync in the neon_auth schema
```

### 示例用法 3

对数据库表运行查询，以检索和分析你的数据。

#### goose 提示词

```
Count the rows in the users_sync table.
```

#### goose 输出

```
I'll count the rows in the neon_auth.users_sync table using a COUNT query.

Total Records: 1 row
Table Location: Schema neon_auth, Table users_sync
Project: neon-auth-mcp-oauth (Project ID: gentle-base-21700263)
Content: Contains one user record
```

---

## DataHub 扩展

> 原文：https://block.github.io/goose/docs/mcp/datahub-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/VXRvHIZ3Eww?start=1878" />

本教程介绍如何将 [DataHub MCP 服务器](https://github.com/acryldata/mcp-server-datahub)添加为 goose 扩展，以便在你的数据生态中实现 AI 驱动的数据发现、血缘探索和元数据查询。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=uvx&arg=mcp-server-datahub%40latest&id=datahub-mcp&name=DataHub&description=Data%20discovery%20and%20metadata%20platform%20integration&env=DATAHUB_GMS_URL%3DDataHub%20GMS%20URL%20(e.g.%2C%20https%3A%2F%2Fyour-instance.acryl.io%20or%20http%3A%2F%2Flocalhost%3A8080)&env=DATAHUB_GMS_TOKEN%3DDataHub%20Personal%20Access%20Token)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **Command**
```sh
uvx mcp-server-datahub@latest
```
  </TabItem>
</Tabs>
  **Environment Variables**
```
DATAHUB_GMS_URL: <your-datahub-url>
DATAHUB_GMS_TOKEN: <your-datahub-token>
```
:::

### 什么是 DataHub？

[DataHub](https://datahub.com/) 是一个开源元数据平台，为你的数据生态提供统一视图，对数据集、仪表盘、管道等进行编目，并附带丰富的元数据，包括归属、血缘、使用统计和数据质量信息。

DataHub MCP 服务器让 AI 代理能够：
- **查找可信数据**：使用自然语言搜索，并结合流行度、质量和血缘等信任信号
- **探索数据血缘**：在表和列级别理解上游和下游依赖
- **理解业务上下文**：通过术语表、域、数据产品和组织元数据
- **生成 SQL 查询**：借助文档、血缘和常见查询模式

了解更多：[DataHub MCP Server Guide](https://docs.datahub.com/docs/features/feature-guides/mcp) | [GitHub Repository](https://github.com/acryldata/mcp-server-datahub)

### 前提条件

在使用 DataHub MCP 服务器之前，请确保你已具备：

- **Python 3.10+** 和 **[uv](https://docs.astral.sh/uv/#installation)** 包管理器
- 一个 **DataHub 实例**：[DataHub Cloud](https://www.datahub.com) 或[自托管 DataHub](https://docs.datahub.com/docs/quickstart)
- 来自你 DataHub 实例的 **[Personal Access Token](https://docs.datahub.com/docs/authentication/personal-access-tokens)**

### 配置

:::info
注意，你需要在系统上安装 [uv](https://docs.astral.sh/uv/#installation) 才能运行此命令，因为它使用了 `uvx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

    <GooseDesktopInstaller
      extensionId="datahub-mcp"
      extensionName="DataHub"
      description="Data discovery and metadata platform integration"
      type="stdio"
      command="uvx"
      args={["mcp-server-datahub@latest"]}
      envVars={[
        { name: "DATAHUB_GMS_URL", label: "DataHub GMS URL (e.g., https://your-instance.acryl.io or http://localhost:8080)" },
        { name: "DATAHUB_GMS_TOKEN", label: "DataHub Personal Access Token" }
      ]}
      apiKeyLink="https://docs.datahub.com/docs/authentication/personal-access-tokens"
      apiKeyLinkText="DataHub Personal Access Token"
    />

  </TabItem>
  <TabItem value="cli" label="goose CLI">

    <CLIExtensionInstructions
      name="DataHub"
      description="Data discovery and metadata platform integration"
      type="stdio"
      command="uvx mcp-server-datahub@latest"
      timeout={300}
      envVars={[
        { key: "DATAHUB_GMS_URL", value: "https://your-instance.acryl.io" },
        { key: "DATAHUB_GMS_TOKEN", value: "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪" }
      ]}
      infoNote={
        <>
          Get your Personal Access Token from{" "}
          <a href="https://docs.datahub.com/docs/authentication/personal-access-tokens" target="_blank" rel="noopener noreferrer">
            DataHub documentation
          </a>. Use your DataHub GMS URL (e.g., https://your-instance.acryl.io for DataHub Cloud or http://localhost:8080 for local instances).
        </>
      }
    />

  </TabItem>
</Tabs>

### 示例用法

#### 查找可信数据

用自然语言描述你的需求，找到与你的项目相关的数据集。

##### goose 提示词

> _查找所有与客户交易相关、由 analytics 团队拥有的数据集_

##### goose 输出

:::note 桌面版

DataHub 扩展会在你的数据目录中搜索，并返回相关数据集及其元数据，包括：

- 数据集名称和描述
- 列名、类型、描述和标签
- 归属者
- 标签、属性和术语表条目
- 使用统计
- 数据质量状态

:::

#### 探索数据血缘

我想从 customer_orders 表中删除 "timestamp_seconds" 列。会有什么被破坏？

##### goose 提示词

> _向我展示 customer_orders 表的上游血缘_

##### goose 输出

:::note 桌面版

该扩展会遍历血缘图，并展示所有：

- 源表和数据集
- 转换管道
- ETL 任务和工作流
- 下游列

这些都会因删除该列而受到影响。

:::

#### 生成 SQL 查询

我如何计算去年在美国产生的订单数量？

##### goose 提示词

> _针对 customer_orders 数据集运行的最常见查询有哪些？_

##### goose 输出

:::note 桌面版

该扩展会检索 SQL 查询历史，展示：

- 频繁执行的查询
- 常见的 join 模式
- 过滤条件
- 聚合模式

此外还会返回列名、类型、描述和任何标签。这将使代理能够生成高质量的 SQL 来回答该问题。

:::

#### 理解数据质量与新鲜度

在使用数据集之前判断它是否可信。

##### goose 提示词

> _customer_orders 表是否新鲜，且没有数据质量问题？_

##### goose 输出

:::note 桌面版

该扩展会获取：

- 最新的数据质量断言和测试结果
- 新鲜度／陈旧度指标
- Schema 变更历史
- SLA 或 SLO 元数据
- 归属者提供的健康状态

从而使代理能够向用户发出警告，或确认数据可信度。

:::

### 能力

DataHub MCP 服务器提供以下工具：

**`search`**

使用结构化关键词搜索（/q 语法）搜索 DataHub，支持布尔逻辑、过滤器、分页，以及按使用指标进行可选排序。

**`get_lineage`**

检索任意实体（数据集、列、仪表盘等）的上游或下游血缘，支持过滤、血缘内查询、分页和跳数控制。

**`get_dataset_queries`**

获取引用某个数据集或列的真实 SQL 查询——无论是手写的还是系统生成的——以理解使用模式、join、过滤和聚合行为。

**`get_entities`**

按 URN 获取一个或多个实体的详细元数据；支持批量检索，以便高效检查搜索结果。

**`list_schema_fields`**

列出数据集的 schema 字段，支持关键词过滤和分页，当搜索结果截断了字段或探索大型 schema 时很有用。

**`get_lineage_paths_between`**

检索两个资产或列之间的确切血缘路径，包括中间的转换和 SQL 查询信息。

### 资源

- [DataHub MCP Server GitHub](https://github.com/acryldata/mcp-server-datahub)
- [DataHub Documentation](https://docs.datahub.com/docs/)
- [DataHub MCP Server Guide](https://docs.datahub.com/docs/features/feature-guides/mcp)
- [Demo Video](https://youtu.be/VXRvHIZ3Eww?t=1878)

### 故障排查

#### 连接问题

如果你在连接 DataHub 时遇到问题：

1. 确认你的 `DATAHUB_GMS_URL` 正确：
   - 对于 DataHub Cloud：`https://your-tenant.acryl.io`
   - 对于本地实例：`http://localhost:8080`
   - 对于本地部署：`https://datahub.your-company.com`

2. 确认你的 Personal Access Token 有效并具有适当的权限

3. 检查网络连通性和防火墙规则

#### 安装问题

如果找不到 `uvx`：

1. 确保已安装 `uv`：`curl -LsSf https://astral.sh/uv/install.sh | sh`
2. 重启你的终端或重新加载你的 shell 配置
3. 验证安装：`which uvx`

---

## OpenMetadata 扩展

> 原文：https://block.github.io/goose/docs/mcp/openmetadata-mcp

[OpenMetadata MCP 服务器](https://open-metadata.org/mcp)扩展让 goose 可以直接与你的 OpenMetadata 交互，支持对 OpenMetadata 资产、术语表和血缘的操作。这让你能够通过自然语言交互轻松地操作存储在 OpenMetadata 中的元数据。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=-y&arg=mcp-remote&arg=http%3A%2F%2Flocalhost%3A8585%2Fmcp&arg=--auth-server-url%3Dhttp%3A%2F%2Flocalhost%3A8585%2Fmcp&arg=--client-id%3Dopenmetadata&arg=--verbose&arg=--clean&arg=--header&arg=Authorization%3A%24%7BAUTH_HEADER%7D&id=openmetadata&name=OpenMetadata&description=Intelligent%20data%20management%20and%20automated%20data%20operations&env=AUTH_HEADER%3DBearer%20YOUR_OPENMETADATA_PAT)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **Command**
```sh
npx -y mcp-remote http://localhost:8585/mcp --auth-server-url=http://localhost:8585/mcp --client-id=openmetadata --verbose --clean --header Authorization:${AUTH_HEADER}
```
  </TabItem>
</Tabs>
:::

### 自定义你的连接

OpenMetadata MCP 服务器使用 OpenMetadata 内嵌的 MCP 服务器连接到 OpenMetadata 实例。这里我们用 `http://localhost:8585` 作为示例来访问本地 OpenMetadata 实例，但你可以根据自己的环境进行配置。这里的 AUTH_HEADER 是一个 [OpenMetadata Personal Access Token (PAT)](https://docs.open-metadata.org/latest/how-to-guides/mcp#adding-a-personal-access-token-to-your-mcp-client)。

### 配置

:::info
注意，你需要在系统上安装 [Node.js](https://nodejs.org/) 才能运行此命令，因为它使用了 `npx`。你还需要一个正在运行的 OpenMetadata 实例，或对 [OpenMetadata 沙箱](https://sandbox.open-metadata.org/)的访问权限。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="openmetadata"
      extensionName="OpenMetadata"
      description="Intelligent data management and automated data operations"
      command="npx"
      args={["-y", "mcp-remote", "http://localhost:8585/mcp", "--auth-server-url=http://localhost:8585/mcp", "--client-id=openmetadata", "--verbose", "--clean", "--header", "Authorization:${AUTH_HEADER}"]}
      envVars={[
        { name: "AUTH_HEADER", label: "Bearer YOUR_OPENMETADATA_PAT" }
      ]}
      apiKeyLink="https://docs.open-metadata.org/latest/how-to-guides/mcp#adding-a-personal-access-token-to-your-mcp-client"
      apiKeyLinkText="OpenMetadata Personal Access Token"
    />
    
    :::info 配置你的连接字符串
    如有需要，请[更新该扩展](https://block.github.io/goose/docs/getting-started/using-extensions#updating-extension-properties)，使其与你的 [OpenMetadata 环境](#customizing-your-connection)匹配。
    :::

  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="OpenMetadata"
      description="Intelligent data management and automated data operations"
      command="npx -y mcp-remote http://localhost:8585/mcp --auth-server-url=http://localhost:8585/mcp --client-id=openmetadata --verbose --clean --header Authorization:${AUTH_HEADER}"
      envVars={[
        { key: "AUTH_HEADER", value: "Bearer YOUR_OPENMETADATA_PAT" }
      ]}
      commandNote={
        <>
          Replace <code>http://localhost:8585/mcp</code> with the actual OpenMetadata instance URL that matches your <a href="#customizing-your-connection">OpenMetadata environment</a>.
        </>
      }
      infoNote={
        <>
          Obtain your <a href="https://docs.open-metadata.org/latest/how-to-guides/mcp#adding-a-personal-access-token-to-your-mcp-client" target="_blank" rel="noopener noreferrer">OpenMetadata Personal Access Token</a> and paste it in as the <code>Bearer</code> token.
        </>
      }
    />
  </TabItem>
</Tabs>

### 可用操作

OpenMetadata 扩展通过自然语言交互提供全面的元数据管理能力。你可以执行多种操作，包括：

#### OpenMetadata 操作
- **search_metadata** 在你的 OpenMetadata 目录中查找数据资产和业务术语。
- **get_entity_details** 使用实体的完全限定名检索某个特定实体的详细信息。
- **create_glossary** 创建一个新术语表，以组织业务术语和定义。
- **create_glossary_term** 在现有术语表内创建一个新术语，支持层级关系。
- **get_entity_lineage** 检索任意实体的上游和下游血缘信息，以理解数据依赖和影响分析。

你只需用自然语言描述你想完成什么，goose 就会帮你安全高效地执行合适的 OpenMetadata 操作。

### 示例用法

在这个示例中，goose 查看存储在 OpenMetadata 中一个名为 `customers` 的 Redshift 表的元数据，特别是它的血缘。如果血缘中没有显示有一个名为 `customerinfo` 的 Databricks 表被用于构建 `customers`，goose 会把它加上。

##### goose 提示词
```
which tables are used to create my customers table in redshift? if the databricks table customerinfo is not already, add it to the customers table lineage.
```

##### goose 输出
```
Based on my analysis, I found your Redshift customers table at `redshift prod.dev.dbt_jaffle.customers`. Here are the tables currently used to create it:

##### Current Upstream Tables for Redshift Customers Table
###### Direct Dependencies:
1. `redshift prod.dev.dbt_jaffle.stg_customers` (Staging Table for Customers)
2. `redshift prod.dev.dbt_jaffle.stg_payments`
3. `redshift prod.dev.dbt_jaffle.stg_orders`

######Indirect Dependencies (Raw Tables):
4. `redshift prod.dev.dbt_jaffle.raw_customers` → feeds into `stg_customers`
5. `redshift prod.dev.dbt_jaffle.raw_payments` → feeds into `stg_payments`
6. `redshift prod.dev.dbt_jaffle.raw_orders` → feeds into `stg_orders`

######Missing Databricks CustomerInfo Table
I found your Databricks `customerinfo` table at:

`DatabricksBanking.demo.mssqlbanking_customer.customerinfo`
This table is NOT currently connected to your Redshift customers table lineage.

I have successfully created the lineage between the Databricks customerinfo table and the Redshift customers table. Here's what I accomplished:
######Lineage Created Successfully
Source Table (Databricks):

Name: `customerinfo`
Full Name: `DatabricksBanking.demo.mssqlbanking_customer.customerinfo`
Platform: Databricks
Columns: customerid, firstname, lastname, dateofbirth, email, phonenumber, _fivetran_deleted, _fivetran_synced

Target Table (Redshift):

Name: `customers`
Full Name: `redshift prod.dev.dbt_jaffle.customers`
Platform: Redshift
Columns: customer_id, first_name, last_name, first_order, most_recent_order, number_of_orders, customer_lifetime_value

The lineage relationship now shows that the Databricks customerinfo table is an upstream source that feeds data to create the Redshift customers table. This relationship will be visible in OpenMetadata's lineage view, helping you track data flow and understand dependencies between your Databricks and Redshift systems.
You can now view this lineage in the OpenMetadata UI by navigating to either table and checking the "Lineage" tab to see the connection between these customer data assets.
```

---

## Cloudflare 扩展

> 原文：https://block.github.io/goose/docs/mcp/cloudflare-mcp

本教程介绍如何将 [Cloudflare 的 MCP 服务器](https://github.com/cloudflare/mcp-server-cloudflare)添加为 goose 扩展，以便使用自然语言管理你的 Cloudflare 基础设施、调试应用、分析流量等。

Cloudflare 为其平台的不同方面提供多个专用的 MCP 服务器，让你能够与 Workers、DNS、安全功能、分析和开发工具交互。

:::tip 快速安装

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=mcp-remote&arg=https%3A%2F%2Fobservability.mcp.cloudflare.com%2Fmcp&id=cloudflare-observability&name=Cloudflare%20Observability&description=Debug%20and%20get%20insight%20into%20your%20application%27s%20logs%20and%20analytics&env=CLOUDFLARE_API_TOKEN%3DCloudflare%20API%20Token)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **Command**
```sh
npx mcp-remote https://observability.mcp.cloudflare.com/mcp
```
  </TabItem>
</Tabs>
  **Environment Variable**
```
CLOUDFLARE_API_TOKEN: Your Cloudflare API token with appropriate permissions
```
:::

### 可用的 Cloudflare MCP 服务器

Cloudflare 为不同的使用场景提供多个专用的 MCP 服务器：

| 服务器 | 描述 | 使用场景 |
|--------|-------------|-----------|
| **Documentation** | 获取 Cloudflare 的最新参考信息 | API 参考、功能文档、故障排查指南 |
| **Workers Bindings** | 使用存储、AI 和计算原语构建 Workers 应用 | KV 存储、R2 存储桶、AI 模型、Durable Objects |
| **Workers Builds** | 获取洞察并管理你的 Cloudflare Workers 构建 | 部署状态、构建日志、版本管理 |
| **Observability** | 调试并洞察你应用的日志和分析 | 错误跟踪、性能监控、请求分析 |
| **Radar** | 全球互联网流量洞察、趋势、URL 扫描和实用工具 | 流量分析、威胁情报、URL 扫描 |
| **Container** | 启动沙箱开发环境 | 隔离测试、开发容器 |
| **Browser Rendering** | 抓取网页、转换为 markdown、截图 | 网页抓取、内容分析、视觉测试 |
| **Logpush** | 获取 Logpush 任务健康状态的快速摘要 | 日志管理、数据管道监控 |
| **AI Gateway** | 搜索日志、获取提示词和响应的详情 | AI 使用分析、提示词优化 |
| **AutoRAG** | 列出并搜索你 AutoRAG 上的文档 | 文档检索、知识库管理 |
| **Audit Logs** | 查询审计日志并生成报告以供审查 | 安全监控、合规报告 |
| **DNS Analytics** | 优化 DNS 性能并调试问题 | DNS 故障排查、性能优化 |
| **Digital Experience Monitoring** | 洞察你组织的关键应用 | 应用性能、用户体验监控 |
| **Cloudflare One CASB** | 识别 SaaS 应用的安全配置错误 | 安全态势、合规检查 |
| **GraphQL** | 使用 Cloudflare 的 GraphQL API 获取分析数据 | 自定义分析、数据可视化 |

### 前提条件

- 一个 [Cloudflare 账户](https://dash.cloudflare.com/sign-up)
- 具有适当权限的 [Cloudflare API Token](https://dash.cloudflare.com/profile/api-tokens)
- 已安装 Node.js（用于 `npx` 命令）

### 配置

#### 步骤 1：创建 API Token

1. 前往 [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens)
2. 点击 **"Create Token"**
3. 为特定权限选择 **"Custom token"**，或为完全访问选择 **"Global API Key"**
4. 根据你计划使用哪些 MCP 服务器来配置权限：
   - **Zone:Read** - 用于 DNS、分析和一般 zone 信息
   - **Zone:Edit** - 用于进行配置更改
   - **Account:Read** - 用于账户级资源
   - **Workers:Read/Edit** - 用于与 Workers 相关的服务器
   - **Logs:Read** - 用于可观测性和审计日志

#### 步骤 2：将 MCP 服务器添加到 goose

根据你的需求选择一个或多个服务器。以下是最常用的配置：

##### Observability 服务器（推荐用于调试）

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  1. [启动安装器](goose://extension?cmd=npx&arg=mcp-remote&arg=https%3A%2F%2Fobservability.mcp.cloudflare.com%2Fsse&id=cloudflare-observability&name=Cloudflare%20Observability&description=Debug%20and%20get%20insight%20into%20your%20application%27s%20logs%20and%20analytics&env=CLOUDFLARE_API_TOKEN%3DCloudflare%20API%20Token)
  2. 按 `Yes` 确认安装
  3. 输入你的 Cloudflare API Token
  4. 点击 `Save Configuration`
  5. 滚动到顶部，然后点击左上角的 `Exit`
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  1. 运行 `configure` 命令：
```sh
goose configure
```

  2. 选择添加 `Command-line Extension`
  3. 为你的扩展命名：`cloudflare-observability`
  4. 输入命令：`npx mcp-remote https://observability.mcp.cloudflare.com/mcp`
  5. 设置超时：`300` 秒
  6. 添加环境变量：
     - Name：`CLOUDFLARE_API_TOKEN`
     - Value：你的 Cloudflare API token

  </TabItem>
</Tabs>

##### Workers Bindings 服务器（用于 Workers 开发）

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=mcp-remote&arg=https%3A%2F%2Fbindings.mcp.cloudflare.com%2Fmcp&id=cloudflare-bindings&name=Cloudflare%20Workers%20Bindings&description=Build%20Workers%20applications%20with%20storage%2C%20AI%2C%20and%20compute%20primitives&env=CLOUDFLARE_API_TOKEN%3DCloudflare%20API%20Token)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  Command：`npx mcp-remote https://bindings.mcp.cloudflare.com/mcp`
  </TabItem>
</Tabs>

##### Radar 服务器（用于流量洞察）

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=mcp-remote&arg=https%3A%2F%2Fradar.mcp.cloudflare.com%2Fmcp&id=cloudflare-radar&name=Cloudflare%20Radar&description=Get%20global%20Internet%20traffic%20insights%2C%20trends%2C%20URL%20scans%2C%20and%20other%20utilities&env=CLOUDFLARE_API_TOKEN%3DCloudflare%20API%20Token)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  Command：`npx mcp-remote https://radar.mcp.cloudflare.com/mcp`
  </TabItem>
</Tabs>

### 示例用法

#### 调试应用问题

让我们用 Observability 服务器来调试某个 Workers 应用的性能问题：

##### goose 提示词
```
I'm seeing high error rates on my Workers application "my-api-worker". Can you help me:
1. Check the recent error logs
2. Identify the most common error types
3. Analyze the performance metrics
4. Suggest optimizations based on the data
```

##### 预期 goose 输出
```
I'll help you debug the issues with your "my-api-worker" application. Let me gather the observability data to identify the problems.

First, let me check the recent error logs for your worker:

[goose uses the observability MCP server to fetch error logs]

I found several issues with your worker:

**Error Analysis:**
- 45% of errors are 500 Internal Server Errors
- 30% are timeout errors (exceeded 30s CPU limit)
- 25% are memory limit exceeded errors

**Performance Metrics:**
- Average response time: 2.3s (up 150% from last week)
- CPU usage: 85% average (critical threshold)
- Memory usage: 92% average (near limit)

**Root Causes Identified:**
1. Database connection pooling issues causing timeouts
2. Memory leaks in JSON parsing for large payloads
3. Inefficient regex operations in request validation

**Recommended Optimizations:**
1. Implement connection pooling with proper cleanup
2. Stream large JSON payloads instead of loading into memory
3. Replace regex with more efficient string operations
4. Add caching for frequently accessed data

Would you like me to help implement any of these fixes?
```

#### 管理 Workers Bindings

使用 Workers Bindings 服务器来设置存储和 AI 能力：

##### goose 提示词
```
I need to set up a new Workers project with:
1. KV storage for caching
2. R2 bucket for file uploads
3. AI binding for text analysis
4. Durable Object for real-time features

Can you help me configure these bindings?
```

#### 使用 Radar 分析流量

使用 Radar 服务器进行安全和流量分析：

##### goose 提示词
```
Can you help me analyze the security posture of my domain example.com? I want to:
1. Check for any security threats or malicious traffic
2. Analyze global traffic patterns
3. Scan for vulnerabilities
4. Get recommendations for improving security
```

### 常见使用场景

#### 1. 应用调试
- **Observability Server**：监控错误、性能和用户体验
- **Logpush Server**：分析日志模式和数据管道健康状态
- **DNS Analytics**：调试 DNS 解析问题

#### 2. 开发与部署
- **Workers Bindings**：配置存储、AI 和计算资源
- **Workers Builds**：监控部署状态和构建健康状态
- **Container Server**：搭建隔离的开发环境

#### 3. 安全与合规
- **Audit Logs**：跟踪配置更改和访问模式
- **Cloudflare One CASB**：监控 SaaS 应用安全
- **Radar Server**：威胁情报和 URL 扫描

#### 4. 分析与洞察
- **GraphQL Server**：自定义分析和报告
- **Digital Experience Monitoring**：应用性能洞察
- **AI Gateway**：AI 使用分析和优化

#### 5. 内容与 Web 管理
- **Browser Rendering**：网页抓取和内容分析
- **AutoRAG**：文档管理和检索
- **Documentation Server**：API 参考和故障排查

### 最佳实践

#### 安全
- 使用具有最小必要权限的作用域 API token
- 定期轮换 API token
- 通过审计日志监控 API 使用情况
- 为异常活动设置告警

#### 性能
- 为不同操作使用合适的超时值
- 尽可能缓存频繁访问的数据
- 监控速率限制和使用配额
- 实现恰当的错误处理和重试

#### 开发工作流
- 从 Documentation 服务器开始，获取 API 参考
- 使用 Container 服务器进行隔离测试
- 开发过程中用 Observability 服务器监控
- 上线前用 Radar 服务器分析

### 故障排查

#### 常见问题

**身份验证错误：**
- 确认 API token 具有正确的权限
- 检查 token 是否已过期
- 确保 token 已正确设置到环境变量中

**速率限制：**
- 在 Cloudflare 仪表盘中监控 API 使用情况
- 为重试实现指数退避
- 考虑升级套餐以获得更高的限额

**连接问题：**
- 确认到 Cloudflare API 的网络连通性
- 检查防火墙设置
- 确保 DNS 解析正常

#### 获取帮助

如果你遇到问题：

1. 查阅 [Cloudflare MCP Server 仓库](https://github.com/cloudflare/mcp-server-cloudflare)中的文档
2. 阅读 [Cloudflare API 文档](https://developers.cloudflare.com/api/)
3. 加入我们的 [Discord 社区](https://discord.gg/n8R5VaWDAn)获取支持
4. 查看 [Cloudflare Community](https://community.cloudflare.com/)获取平台相关帮助

### 后续步骤

在 goose 中启用 Cloudflare MCP 服务器后，你可以：

- **监控和调试**你的应用，使用自然语言查询
- **管理基础设施**，通过对话式命令
- **分析安全和性能数据**，轻松自如
- **自动化工作流**，横跨 Cloudflare 整个平台

先试用 Observability 服务器来洞察你当前的应用，然后根据你的具体需求扩展到其他服务器。

---

## Vercel 扩展

> 原文：https://block.github.io/goose/docs/mcp/vercel-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/-Y-werFKtTw" />

本教程介绍如何将 [Vercel MCP 服务器](https://vercel.com/docs/mcp/vercel-mcp)添加为 goose 扩展，以便直接从 goose 管理你的 Vercel 项目和部署状态。

:::info
注意，你需要在系统上安装 [Node.js](https://nodejs.org/) 才能运行安装命令，这些命令使用 `npx`。
:::

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?url=https%3A%2F%2Fmcp.vercel.com&type=streamable_http&id=vercel&name=Vercel&description=Access%20deployments%2C%20manage%20projects%2C%20and%20more%20with%20Vercel%E2%80%99s%20official%20MCP%20server)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
```sh
npx mcp-remote https://mcp.vercel.com
```
  </TabItem>
</Tabs>
:::

### 配置

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="Vercel"
      extensionName="Vercel"
      description="Access Vercel deployments and manage projects"
      type="http"
      url="https://mcp.vercel.com"
    />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Vercel"
      description="Access Vercel deployments and manage projects"
      type="http"
      url="https://mcp.vercel.com"
      timeout={300}
    />
  </TabItem>
</Tabs>

### 示例用法

#### goose 提示词
```
Get a list of my Vercel projects via the Vercel MCP server, and build me a table showing when I last deployed the project and other details I should know about their status.
```

第一次使用 Vercel MCP 服务器时，系统会提示你通过 OAuth 向 Vercel 进行身份验证。

#### goose 输出
```
I'll help you get your Vercel projects and create a table with deployment details. Let me first get your teams to identify which team to use for listing projects.

> List Teams

> teamId: team_p3hPvXImXmdkbZ36FoqhoyYo


Now let me get the deployment information for each project to see the last deployment dates and status:

> projectId, teamId

> projectId, teamId

> projectId, teamId

Now let me get more details about each project to provide a comprehensive table:

> projectId, teamId

> projectId, teamId

> projectId, teamId

Based on the data from your Vercel projects, here's a comprehensive table showing your project status and deployment information:

Vercel Projects Overview
```
Project Name|Framework|Status|Last Deployment|Custom Domain|GitHub Repo|Notes
---|---|---|---|---|---|---
project1|Next.js|🟡 Building|Sep 8, 2025 (Today)|None|about-me|Currently building - newest project
project2|Next.js|✅ Ready|May 12, 2025|example.com|starter-blog|Notes for site 2
project3|Static|✅ Ready|Oct 25, 2024|None|sample.com|Notes for Site 3

```
Key Details & Status Summary

🟡 project1 (Currently Building)
Created: Today (Sep 8, 2025)
Status: Currently building (deployment in progress)
Last Commit: "first" (Sep 8, 2025)
Node Version: 22.x
Issue: This is your newest project and the deployment is still in progress

✅ project2 (Production Ready)
Created: Aug 21, 2024
Status: Production ready and live
Custom Domain: example.com (with www redirect)
Last Update: "grammar fix" (May 12, 2025)
Node Version: 20.x
Activity: Most active project with 12 deployments
Note: One failed deployment on Mar 12 but recovered successfully

✅ project3 (Production Ready)
Created: Oct 25, 2024
Status: Production ready
Last Update: "updated public to remove localhost" (Oct 25, 2024)
Node Version: 20.x
Activity: Single successful deployment

Recommendations
- Monitor the building project: Check on project1 as it's currently building
- Portfolio maintenance: Your project2 is well-maintained and actively used
- Domain setup: Consider adding a custom domain to your other projects if needed
- Node versions: You have mixed Node versions (20.x and 22.x) - consider standardizing
- All projects are connected to GitHub repositories and have automatic deployments configured.
```

---

## Netlify 扩展

> 原文：https://block.github.io/goose/docs/mcp/netlify-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/iSUNmxOf6gw" />

本教程介绍如何将 [Netlify MCP 服务器](https://github.com/netlify/netlify-mcp)添加为 goose 扩展，以构建、部署和管理 Netlify 站点。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=-y&arg=%40netlify%2Fmcp&id=netlify-mcp&name=Netlify&description=Build%2C%20deploy%2C%20and%20manage%20sites%20with%20Netlify%27s%20official%20MCP%20server.)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **Command**
```sh
npx -y @netlify/mcp
```
  </TabItem>
</Tabs>
:::

### 配置

确保你已登录 Netlify 账户：

```bash
netlify login
```

#### 添加 Netlify MCP 服务器

:::info
注意，你需要在系统上安装 [Node.js](https://nodejs.org/) 才能运行此命令，因为它使用了 `npx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="netlify-mcp"
    extensionName="Netlify"
    description="Build, deploy, and manage sites with Netlify's official MCP server."
    command="npx"
    args={["-y", "@netlify/mcp"]}
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Netlify"
      description="Build, deploy, and manage sites with Netlify's official MCP server"
      command="npx -y @netlify/mcp"
    />
  </TabItem>
</Tabs>

### 示例用法

在这个示例中，我将向你展示如何使用 goose 配合 Netlify 扩展来部署一个 Web 应用。

#### goose 提示词

> 你能通过我的 GitHub 仓库把我的应用部署到 Netlify 吗？

#### goose 输出

:::note CLI

<details>
    <summary>工具调用</summary>
    我会帮你从你的 GitHub 仓库把 tic-tac-toe 应用部署到 Netlify。让我先检查你的 Netlify 账户，然后设置部署。

    ─── netlify-user-services | netlify ──────────────────────────

    selectSchema: <br/>
        &nbsp;&nbsp;&nbsp;&nbsp;operation: get-user <br/>
        &nbsp;&nbsp;&nbsp;&nbsp;params:

    很好！我看到你已登录 Netlify，并已连接你的 GitHub 账户。现在让我创建一个新的 Netlify 站点，并从你的 GitHub 仓库部署你的 tic-tac-toe 应用。

    ─── netlify-project-services | netlify ──────────────────────────

    selectSchema:<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;operation: create-new-project<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;params:<br/>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name: tic-tac-toe-game

    让我换一个项目名称试试：

    ─── netlify-project-services | netlify ──────────────────────────

    selectSchema:<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;operation: create-new-project<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;params:<br/>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;name: janedoe-tic-tac-toe

    完美！我已经创建了一个名为 "janedoe-tic-tac-toe" 的新 Netlify 站点。现在我需要从 GitHub 仓库部署你的代码。让我部署该站点：

    ─── netlify-deploy-services | netlify ──────────────────────────

    selectSchema:<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;operation: deploy-site<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;params:<br/>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;deployDirectory: /Users/janedoe/Development/tic-tac-toe<br/>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;siteId: 1731e49e-1d0a-49a3-ad95-975b550f324a

    让我检查部署状态并获取你站点的实时 URL：

    ─── netlify-project-services | netlify ──────────────────────────

    selectSchema:<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;operation: get-project<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;params:<br/>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;siteId: 1731e49e-1d0a-49a3-ad95-975b550f324a
</details>
:::

🎉 **成功！你的 tic-tac-toe 游戏已部署到 Netlify！**

### 部署详情：

- **Live Site URL**：http://janedoe-tic-tac-toe.netlify.app
- **Netlify Project Dashboard**：https://app.netlify.com/projects/janedoe-tic-tac-toe
- **Site ID**：1731e49e-1d0a-49a3-ad95-975b550f324a

### 部署了什么：

✅ **HTML**：你的主游戏界面

✅ **CSS**：带现代动画和响应式设计的样式

✅ **JavaScript**：完整的游戏逻辑和交互

✅ **README**：项目文档

### 后续步骤：

1. **访问你的实时站点**：http://janedoe-tic-tac-toe.netlify.app
2. **测试游戏**：确保一切按预期运行
3. **分享给他人**：你的游戏现在已在 Web 上线！

### 未来更新：

由于你的代码是从本地目录部署的，如果你想做出更改：

1. 更新你的本地文件
2. 将更改推送到你的 GitHub 仓库
3. 你可以任选其一：
   - 使用相同的命令手动重新部署
   - 设置从 GitHub 的持续部署（这样你推送更改时会自动部署）

需要我帮你设置从 GitHub 仓库的持续部署，以便未来的更改自动部署吗？

你的 tic-tac-toe 游戏现已上线，可以开始玩了！🎮

---

## Cloudinary 资产管理扩展

> 原文：https://block.github.io/goose/docs/mcp/cloudinary-asset-management-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/4diEvoRFVrQ" />

本教程介绍如何将 [Cloudinary Asset Management MCP 服务器](https://github.com/cloudinary/asset-management-js)添加为 goose 扩展，以自动化复杂的图像处理工作流——这些工作流通常需要专业的设计软件或手动编辑。

:::tip 快速安装

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=-y&arg=--package&arg=@cloudinary/asset-management&arg=--&arg=mcp&arg=start&id=cloudinary-asset-management-mcp&name=Cloudinary%20Asset%20Management&description=Powerful%20media%20processing%20and%20transformation&env=CLOUDINARY_URL%3DCloudinary%20URL)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **Command**
```sh
npx -y --package @cloudinary/asset-management -- mcp start
```
  </TabItem>
</Tabs>
  **Environment Variable**
```
CLOUDINARY_URL: cloudinary://<your_api_key>:<your_api_secret>@<your_cloud_name>
```
:::

### 配置

:::info
注意，你需要在系统上安装 [Node.js](https://nodejs.org/) 才能运行此命令，因为它使用了 `npx`。你还需要一个 [Cloudinary 账户](https://cloudinary.com/users/register/free)。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="cloudinary-asset-management-mcp"
    extensionName="Cloudinary Asset Management"
    description="Powerful media processing and transformation"
    command="npx"
    args={["-y", "--package", "@cloudinary/asset-management", "--", "mcp", "start"]}
    envVars={[{ name: "CLOUDINARY_URL", label: "Cloudinary URL (cloudinary://api_key:api_secret@cloud_name)" }]}
    apiKeyLink="https://console.cloudinary.com/settings/api-keys"
    apiKeyLinkText="Cloudinary URL"
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Cloudinary"
      description="Powerful media processing and transformation"
      command="npx -y --package @cloudinary/asset-management -- mcp start"
      envVars={[
        { key: "CLOUDINARY_URL", value: "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪" }
      ]}
      infoNote={
        <>
          Obtain your <a href="https://console.cloudinary.com/settings/api-keys" target="_blank" rel="noopener noreferrer">Cloudinary URL</a> from your dashboard and paste it in. For example: <code>cloudinary://&lt;your_api_key&gt;:&lt;your_api_secret&gt;@&lt;your_cloud_name&gt;</code>
        </>
      }
    />
  </TabItem>
</Tabs>

### 示例用法

让我们用 Cloudinary 扩展来查找并转换带有高级视觉效果的产品图片。在这个示例中，我们将演示 goose 如何帮你：

1. 在你的媒体库中搜索特定的图片
2. 应用复杂的转换，包括背景移除
3. 添加精确定位的文字叠加

#### goose 提示词
```
1. find shoe images in my Cloudinary samples that have 'shoe' in the filename or public ID.
2. Let's transform the first result and only extract just the shoes
3. Add a white text overlay that says I love shoes. Make sure it's above the shoes
4. Add a background to the image. It should be black
```

#### goose 输出
```
I'll help you find shoe images in your Cloudinary samples and apply the transformations you've requested. Let me start by searching for images with 'shoe' in the filename or public ID.

─── list-images | cloudinaryassetmanagement ──────────────────────────
maxResults: 50
prefix: samples
type: upload

Perfect! I found the shoe images in your Cloudinary samples. I can see:

1. **`samples/shoe`** - A single shoe image (publicId: `samples/shoe`)
2. **`samples/ecommerce/shoes`** - A pair of shoes (publicId: `samples/ecommerce/shoes`)

Let me use the first result (`samples/shoe`) as requested and apply all the transformations you want:

1. Extract just the shoes (using background removal)
2. Add white text overlay "I love shoes" above the shoes
3. Add a black background

Here's the transformed image URL with all your requested modifications:

https://res.cloudinary.com/dd8qwbjtv/image/upload/e_background_removal/b_black/l_text:Arial_60:I%20love%20shoes,co_white,g_north,y_50/samples/shoe

Let me break down what each transformation does:

- `e_background_removal` - Removes the background and extracts just the shoe
- `b_black` - Adds a black background to replace the removed background
- `l_text:Arial_60:I%20love%20shoes,co_white,g_north,y_50` - Adds white text overlay:
  - `Arial_60` - Arial font, size 60
  - `I%20love%20shoes` - The text (URL encoded)
  - `co_white` - White color
  - `g_north` - Positioned at the top (north)
  - `y_50` - 50 pixels offset from the top

Here are the images we found with "shoe" in the filename/public ID:

1. **First result (used for transformation)**: `samples/shoe`
   - Original: https://res.cloudinary.com/dd8qwbjtv/image/upload/v1708364167/samples/shoe.jpg
   - **Transformed**: https://res.cloudinary.com/dd8qwbjtv/image/upload/e_background_removal/b_black/l_text:Arial_60:I%20love%20shoes,co_white,g_north,y_50/samples/shoe

2. **Second result**: `samples/ecommerce/shoes`
   - Original: https://res.cloudinary.com/dd8qwbjtv/image/upload/v1708364144/samples/ecommerce/shoes.png

The transformed image now has:
✅ Just the shoes extracted (background removed)
✅ White text "I love shoes" positioned above the shoes
✅ Black background applied

You can click on the transformed URL to see the final result!
```

---

## VMware AIops 扩展

> 原文：https://block.github.io/goose/docs/mcp/vmware-aiops-mcp

本教程介绍如何将 [vmware-aiops](https://github.com/zw008/VMware-AIops)添加为 goose 扩展，从而用自然语言管理 VMware vCenter 和 ESXi 基础设施。借助该扩展，goose 可以列出虚拟机、检查健康状况、开机／关机、从模板部署、在虚拟机内运行命令，并编排带自动回滚的多步骤操作。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    先安装 vmware-aiops：
```sh
uv tool install vmware-aiops
vmware-aiops mcp-config install --agent goose
```
  </TabItem>
  <TabItem value="cli" label="goose CLI">
```sh
uv tool install vmware-aiops
vmware-aiops mcp-config install --agent goose
```
  </TabItem>
</Tabs>
:::

### 配置

:::info 前提条件
你需要 [uv](https://docs.astral.sh/uv/) 和一个正在运行的 VMware vCenter Server 或 ESXi 主机。Guest Operations 功能要求客户机虚拟机内运行 VMware Tools。
:::

**步骤 1：安装并配置凭据**

```sh
uv tool install vmware-aiops

mkdir -p ~/.vmware-aiops
cat > ~/.vmware-aiops/config.yaml << 'EOF'
targets:
  my-vcenter:
    host: vcenter.example.com
    username: administrator@vsphere.local
    password_env: VMWARE_PASSWORD
    verify_ssl: false
EOF

echo "VMWARE_PASSWORD=your_password" > ~/.vmware-aiops/.env
chmod 600 ~/.vmware-aiops/.env
```

**步骤 2：验证连通性**

```sh
vmware-aiops doctor
```

**步骤 3：添加到 goose**

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="vmware-aiops"
      extensionName="VMware AIops"
      description="Natural language VMware vCenter/ESXi monitoring and operations"
      type="stdio"
      command="uvx"
      args={["--from", "vmware-aiops", "vmware-aiops-mcp"]}
      envVars={[
        { name: "VMWARE_AIOPS_CONFIG", label: "Path to config.yaml (e.g. /Users/you/.vmware-aiops/config.yaml)" }
      ]}
    />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="vmware-aiops"
      description="Natural language VMware vCenter/ESXi monitoring and operations"
      type="stdio"
      command="uvx --from vmware-aiops vmware-aiops-mcp"
      timeout={300}
      envVars={[
        { key: "VMWARE_AIOPS_CONFIG", value: "/Users/you/.vmware-aiops/config.yaml" }
      ]}
      infoNote={
        <>
          Set <code>VMWARE_AIOPS_CONFIG</code> to the absolute path of your config.yaml. See the <a href="https://github.com/zw008/VMware-AIops" target="_blank" rel="noopener noreferrer">vmware-aiops repository</a> for full setup instructions.
        </>
      }
    />
  </TabItem>
</Tabs>

### 示例用法

在这个示例中，我将用 goose 在我的 vCenter 环境中执行每日健康检查，并修复某个虚拟机上的磁盘空间问题——全程通过自然语言完成。

#### goose 提示词

```
Check the health of my vCenter environment. Show any active alarms and
powered-off VMs that haven't been used recently. If datastore usage is
above 85%, tell me which VMs are using the most space.
```

#### goose 输出

```
I'll start with a full health check of your vCenter environment.

--- get_alarms ---

Found 2 active alarms:
- esxi-03: CPU ready > 5% (Warning) — sustained for 2 hours
- datastore02: 87% capacity used (Critical) ← needs attention

--- list_virtual_machines (power_state=poweredOff) ---

4 powered-off VMs found:
- vm-test-old (last powered on: 21 days ago)
- vm-dev-unused (last powered on: 14 days ago)
- vm-staging-v1 (last powered on: 8 days ago)
- vm-backup-runner (last powered on: 3 days ago)

--- browse_datastore (datastore02) ---

Largest consumers on datastore02:
1. vm-db-prod: 320 GB (snapshots not cleaned up)
2. vm-web-cluster: 180 GB
3. vm-test-old: 95 GB (powered off)

Recommendation: Delete vm-test-old (powered off 21 days, 95 GB) to free
space immediately. Also, vm-db-prod has stale snapshots — consolidating
them would recover ~120 GB.

Shall I create a plan to remove vm-test-old and consolidate vm-db-prod snapshots?
```

```
Yes, go ahead.
```

```
--- vm_create_plan ---

Plan created:
Step 1: Power off check for vm-test-old (already off ✓)
Step 2: Delete vm-test-old
Step 3: Consolidate snapshots on vm-db-prod

⚠️  Step 2 is irreversible. Step 3 is safe (read-only snapshot merge).

--- vm_apply_plan ---

Step 1/3: Verified vm-test-old is powered off ✓
Step 2/3: Deleted vm-test-old — freed 95 GB ✓
Step 3/3: Consolidated vm-db-prod snapshots — freed 118 GB ✓

datastore02 is now at 64% capacity. All alarms should clear within 5 minutes.
```

---

## Linux MCP 服务器扩展

> 原文：https://block.github.io/goose/docs/mcp/linux-mcp-server-mcp

本教程介绍如何将 [Linux MCP 服务器](https://github.com/rhel-lightspeed/linux-mcp-server)添加为 goose 扩展，使 AI 助手能够运行、发现并排查 Linux 系统上的复杂问题。

:::tip 快速上手
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [安装 Linux MCP 服务器](https://rhel-lightspeed.github.io/linux-mcp-server/install/)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **Command**
```sh
# Using uv (recommended)
uvx linux-mcp-server
```
  </TabItem>
</Tabs>
:::

### 配置

:::info
注意，你需要在系统上安装 [uv](https://docs.astral.sh/uv/#installation) 才能运行此命令，因为它使用了 *uvx*。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

    <GooseDesktopInstaller
      extensionId="linux-mcp-server"
      extensionName="Linux MCP server"
      description="Tools for Linux system discovery and troubleshooting"
      type="stdio"
      command="uvx"
      args={["linux-mcp-server"]}
    />

 
  </TabItem>
  <TabItem value="cli" label="goose CLI">

    <CLIExtensionInstructions
      name="Linux MCP Server"
      description="Tools for Linux system discovery and troubleshooting"
      type="stdio"
      command="uvx linux-mcp-server"
      timeout={300}
    />
    
  </TabItem>
</Tabs>

### 示例用法

按照说明了解如何使用 Linux MCP 服务器进行系统诊断和故障排查。

#### goose 提示词

> _我的 wifi 连接不太稳定。请在系统日志中找到错误信息，并诊断问题以帮我修复。_

#### goose 输出

:::note 桌面版

🤖 LLM output 🤖
我会通过检查系统日志中与你的网络接口和无线连接相关的错误信息，帮你诊断 WiFi 连接问题。让我先收集系统信息并检查相关日志。

:::
