# goose 官方文档中文手册：第 18 章　MCP 扩展（六）：搜索与信息获取

## Brave Search 扩展

> 原文：https://block.github.io/goose/docs/mcp/brave-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/kD2YA61NTLU" />

服务器已迁移

本教程将带你上手把 [Brave Search MCP Server](https://www.pulsemcp.com/servers/brave-search) 添加为 goose 扩展，从而为网页搜索和本地搜索启用交互式搜索。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=-y&arg=%40modelcontextprotocol%2Fserver-brave-search&id=brave-search&name=Brave%20Search&description=Brave%20Search%20API&env=BRAVE_API_KEY%3DYour%20API%20Key)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
npx -y @modelcontextprotocol/server-brave-search
```
  </TabItem>
</Tabs>
  **环境变量**
```
BRAVE_API_KEY: <YOUR_API_KEY>
```
:::

### 配置

:::info
注意，你需要在系统中安装 [Node.js](https://nodejs.org/) 才能运行该命令，因为它使用了 `npx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="brave-search"
    extensionName="Brave Search"
    description="Brave Search API"
    command="npx"
    args={["-y", "@modelcontextprotocol/server-brave-search"]}
    envVars={[{ name: "BRAVE_API_KEY", label: "Your Brave Search API Key" }]}
    apiKeyLink="https://api-dashboard.search.brave.com/app/keys"
    apiKeyLinkText="Brave Search API Key"
  />
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

  3. 为你的扩展起一个名字
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
  │  brave-search
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
  │  brave-search
  │
  // highlight-start
  ◆  What command should be run?
  │  npx -y @modelcontextprotocol/server-brave-search
  // highlight-end
  └ 
```

  5. 输入 goose 在超时之前应等待动作完成的秒数。默认值为 300 秒
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
  │  brave-search
  │
  ◇  What command should be run?
  │  npx -y @modelcontextprotocol/server-brave-search
  │
  // highlight-start
  ◆  Please set the timeout for this tool (in secs):
  │  300
  // highlight-end
  │
  └ 
```

  6. 选择是否添加描述。如果你在这里选择「Yes」，系统会提示你为扩展输入一段描述。
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
  │  brave-search
  │
  ◇  What command should be run?
  │  npx -y @modelcontextprotocol/server-brave-search
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

  7. 获取一个 [Brave Search API Key](https://api-dashboard.search.brave.com/app/keys) 并粘贴进去。
  :::info
  注册一个 [Brave Search API 账号](https://brave.com/search/api/)，选择一个套餐（免费档每月提供 2000 次查询），然后在 [开发者控制台](https://api-dashboard.search.brave.com/app/keys) 中生成你的 API key。
  :::

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
  │  brave-search
  │
  ◇  What command should be run?
  │  npx -y @modelcontextprotocol/server-brave-search
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
  │  BRAVE_API_KEY
  │
  ◇  Environment variable value:
  │  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
  │
  ◇  Add another environment variable?
  │  No 
  // highlight-end
  └  Added brave-search extension
```

  </TabItem>
</Tabs>

### 示例用法

Brave Search MCP 服务器让你可以访问 Brave Search API，同时提供网页搜索和本地搜索能力：

- **网页搜索**：通用查询、新闻、文章，支持分页和时效性控制
- **本地搜索**：查找商家、餐厅和服务，并附带详细信息（需要 Pro API key）
- **灵活过滤**：控制结果类型、安全级别和内容时效性
- **智能回退**：本地搜索在未找到结果时会自动回退到网页搜索


##### goose 提示词

```
( O)> Organize a Italian dinner party with Ian, Rizel, Ace, and Ebony. Find 3 or 4 YouTube cooking channels (with URLs) that focus on Italian cuisine for beginners, and then find one recipe (with URL) for each person to make: one salad, two entrees, and one dessert.
```

##### goose 输出

```

I'll help you organize the Italian dinner party and search for appropriate cooking resources and recipes. Let me break this down into parts.

First, let's search for some beginner-friendly Italian cooking YouTube channels:

Brave Web Search
query: best youtube channels italian cooking for beginners authenti...

Let me search for some specific recipes:

Brave Web Search
query: authentic italian salad recipes panzanella caprese insalata

Brave Web Search
query: authentic italian main course pasta recipes carbonara osso b...

Brave Web Search
query: authentic italian dessert recipes tiramisu panna cotta


Based on my research, I'll organize the dinner party plan with recommended YouTube channels and specific recipes for each person. Here's the plan:

Recommended Italian Cooking YouTube Channels for Beginners

1. Vincenzo's Plate (https://www.youtube.com/channel/UCcsSowAamCLJv-xeF9geXoA)
  - Authentic Italian recipes with clear instructions
  - Run by an Italian native who explains techniques well for beginners

2. Italia Squisita (https://www.youtube.com/c/ItaliaSquisita)
  - Features traditional Italian recipes
  - Often shows multiple ways to make classic dishes

3. Giallo Zafferano (https://www.youtube.com/user/GialloZafferano)
  - Italy's most popular cooking channel
  - Comprehensive collection of authentic Italian recipes


Recipe Assignments

1. Rizel - Salad Course
  - Classic Panzanella (Tuscan Bread and Tomato Salad)
  - Recipe: https://www.themediterraneandish.com/tomato-panzanella-salad-recipe/
  - Perfect summer salad with crusty bread, tomatoes, and fresh basil

2. Ian - First Entrée
  - Authentic Spaghetti Carbonara
  - Recipe: https://anitalianinmykitchen.com/spaghetti-carbonara/
  - Classic Roman pasta dish with eggs, pecorino, and guanciale

3. Ace - Second Entrée
  - Osso Buco alla Milanese
  - Recipe: https://www.pastagrammar.com/post/osso-buco-authentic-italian-veal-recipe
  - Traditional Milanese braised veal shanks with gremolata

4. Ebony - Dessert
  - Classic Vanilla Panna Cotta
  - Recipe: https://www.recipesfromitaly.com/panna-cotta-recipe/
  - Elegant, creamy dessert that can be made ahead


Tips for Success

- Watch the YouTube channels beforehand to familiarize yourself with Italian cooking techniques
- Make sure to read through the entire recipe before starting
- The Panna Cotta should be made at least 4 hours ahead (or the night before) to allow proper setting time
- The Panzanella can be assembled just before serving for the best texture
- The Osso Buco can be made slightly ahead and reheated, as it often tastes better the next day
- The Carbonara should be made just before serving and served immediately while hot

```

---

## Exa Search 扩展

> 原文：https://block.github.io/goose/docs/mcp/exa-mcp

本教程介绍如何把 [Exa MCP Server](https://github.com/exa-labs/exa-mcp-server) 添加为 goose 扩展，以启用 AI 驱动的网页搜索功能。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=-y&arg=exa-mcp-server&id=exa&name=Exa%20Search&description=AI-powered%20web%20search&env=EXA_API_KEY%3DExa%20API%20Key)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
npx -y exa-mcp-server
```
  </TabItem>
</Tabs>
  **环境变量**
```
EXA_API_KEY: <YOUR_API_KEY>
```
:::

### 配置

:::info
注意，你需要在系统中安装 [Node.js](https://nodejs.org/) 才能运行该命令，因为它使用了 `npx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="exa"
    extensionName="Exa Search"
    description="AI-powered web search"
    command="npx"
    args={["-y", "exa-mcp-server"]}
    envVars={[
      { name: "EXA_API_KEY", label: "Exa API Key" }
    ]}
    apiKeyLink="https://dashboard.exa.ai/api-keys"
    apiKeyLinkText="Exa API Key"
  />
</TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Exa Search"
      description="AI-powered web search"
      command="npx -y exa-mcp-server"
      envVars={[
        { key: "EXA_API_KEY", value: "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪" }
      ]}
      infoNote={
        <>
          Obtain your <a href="https://dashboard.exa.ai/api-keys" target="_blank" rel="noopener noreferrer">Exa API Key</a> and paste it in. You can get your API key by signing up at <a href="https://exa.ai" target="_blank" rel="noopener noreferrer">exa.ai</a> and navigating to the API keys page in the dashboard.
        </>
      }
    />
  </TabItem>
</Tabs>

### 示例用法

Exa MCP 服务器在你的 goose 交互中启用 AI 驱动的网页搜索。Exa 提供了高级搜索能力，包括：

1. 神经搜索、关键词搜索和自动搜索模式
2. 内容检索，支持全文、高亮片段或摘要
3. 类别过滤（新闻、研究论文、公司等）
4. 域名和日期范围过滤

#### goose 提示词

```
Find recent research papers about large language model reasoning capabilities and summarize the key findings.
```

#### goose 输出

```
I'll use Exa to search for recent research papers on LLM reasoning.

─── web_search_exa | exa ──────────────────────────
query: large language model reasoning capabilities research paper
category: research paper


Here are the key findings from recent research on LLM reasoning:

1. Chain-of-Thought Reasoning:
- Recent papers show that explicit chain-of-thought prompting significantly improves performance on multi-step reasoning tasks
- Models trained with reasoning traces demonstrate better generalization to novel problem types

2. Mathematical and Logical Reasoning:
- New benchmarks reveal that while LLMs have improved at arithmetic and formal logic, they still struggle with compositional reasoning
- Hybrid approaches combining neural methods with symbolic solvers show promising results

3. Commonsense Reasoning:
- Studies demonstrate that scaling model size continues to improve commonsense reasoning benchmarks
- However, models still fail on tasks requiring physical intuition or temporal reasoning about everyday events

4. Limitations and Future Directions:
- Several papers identify "reasoning shortcuts" where models exploit dataset patterns rather than performing genuine inference
- Research into retrieval-augmented reasoning shows potential for grounding model outputs in verified facts

Would you like me to search for more details on any of these topics?
```

:::tip
Exa 支持多种搜索类型，包括用于语义查询的神经搜索，以及智能组合多种搜索策略的自动模式。你还可以按类别、域名和日期范围过滤结果，以进行更有针对性的研究。
:::

---

## Tavily 网页搜索扩展

> 原文：https://block.github.io/goose/docs/mcp/tavily-mcp

<YouTubeShortEmbed videoUrl="https://youtube.com/embed/mxS2G9afGxE" />

本教程介绍如何把 [Tavily Web Search MCP Server](https://github.com/tavily-ai/tavily-mcp) 添加为 goose 扩展，以启用 AI 驱动的网页搜索功能。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=-y&arg=tavily-mcp&id=tavily&name=Tavily%20Web%20Search&description=Search%20the%20web%20with%20Tavily%20MCP&env=TAVILY_API_KEY%3DTavily%20API%20Key)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
npx -y tavily-mcp
```
  </TabItem>
</Tabs>
  **环境变量**
```
TAVILY_API_KEY: <YOUR_API_KEY>
```
:::

### 配置

:::info
注意，你需要在系统中安装 [uv](https://docs.astral.sh/uv/#installation) 才能运行该命令，因为它使用了 `uvx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="tavily"
    extensionName="Tavily Web Search"
    description="Search the web with Tavily MCP"
    command="npx"
    args={["-y", "tavily-mcp"]}
    envVars={[
      { name: "TAVILY_API_KEY", label: "Tavily API Key" }
    ]}
    apiKeyLink="https://tavily.com/"
    apiKeyLinkText="Tavily API Key"
  />
</TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Tavily Web Search"
      description="Search the web with Tavily MCP"
      command="npx -y tavily-mcp"
      envVars={[
        { key: "TAVILY_API_KEY", value: "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪" }
      ]}
      infoNote={
        <>
          Obtain your <a href="https://tavily.com/" target="_blank" rel="noopener noreferrer">Tavily API Key</a> and paste it in. You can get your API key by signing up at <a href="https://app.tavily.com/" target="_blank" rel="noopener noreferrer">tavily.com</a> and navigating to your account settings.
        </>
      }
    />
  </TabItem>
</Tabs>

### 示例用法

Tavily MCP 服务器在你的 goose 交互中启用 AI 驱动的网页搜索功能。当你获得 API key 后，就能使用 Tavily 的高级搜索能力，包括：

1. 实时网页搜索
2. 结构化数据提取
3. 内容分析
4. 特定主题搜索

#### goose 提示词

```
Search for recent news about artificial intelligence breakthroughs in medicine and summarize the key findings.
```

#### goose 输出

```
I'll use the Tavily news search tool to find recent news about AI breakthroughs in medicine.

─── tavily_news_search | tavily ──────────────────────────
max_results: 5
query: ...



Let me summarize the key findings from the recent news about AI in medicine:

1. Personalized AI-Driven Healthcare:
- Development of AI systems that act as "personal doctors" that work alongside human clinicians rather than replacing them
- Focus on augmenting clinical capabilities while maintaining human oversight

2. Breakthrough in Medical Imaging:
- A significant advancement in CT scan analysis has been reported in Nature
- Development of a "Unified total-body CT image" (Uni-CT) algorithm that:
  - Automatically generates single series of total-body CT images
  - Concatenates multiple images of segmented organs using organ-specific window settings
  - Reduces diagnosis time by 35% without compromising accuracy
  - Improves efficiency in trauma cases

3. Future Trends:
- Movement toward democratized AI in healthcare, potentially reducing the gap between large and small healthcare providers
- Development of hyper-personalized medical experiences powered by AI
- Integration of AI systems that can perform human-like reasoning in medical contexts

The most concrete breakthrough appears to be in medical imaging, with the Uni-CT algorithm showing promising results in improving both the speed and accuracy of trauma diagnosis. This represents a practical application of AI that could have immediate benefits in emergency medicine.

Would you like me to search for more specific information about any of these developments or explore other areas of AI in medicine?
```

:::tip
你可以针对不同类型的查询和信息深度调整 [搜索参数](https://github.com/tavily-ai/tavily-mcp#tavily-search-examples)。该扩展同时支持快速搜索和全面研究。
:::

---

## Firecrawl 扩展

> 原文：https://block.github.io/goose/docs/mcp/firecrawl-mcp

<YouTubeShortEmbed videoUrl="https://youtube.com/embed/_rKBFLREVcM" />


本教程将带你上手把 [Firecrawl MCP Server](https://github.com/firecrawl/firecrawl-mcp-server) 添加为 goose 扩展，从而为 AI 代理启用强大的网页抓取、爬取和搜索能力。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=-y&arg=firecrawl-mcp&id=firecrawl&name=Firecrawl&description=Web%20scraping%20and%20crawling%20capabilities&env=FIRECRAWL_API_KEY%3DYour%20API%20Key)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
npx -y firecrawl-mcp
```
  </TabItem>
</Tabs>
  **环境变量**
```
FIRECRAWL_API_KEY: <YOUR_API_KEY>
```
:::

### 配置

:::info
注意，你需要在系统中安装 [Node.js](https://nodejs.org/) 才能运行该命令，因为它使用了 `npx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="firecrawl"
    extensionName="Firecrawl"
    description="Web scraping and crawling capabilities"
    command="npx"
    args={["-y", "firecrawl-mcp"]}
    envVars={[{ name: "FIRECRAWL_API_KEY", label: "Your Firecrawl API Key" }]}
    apiKeyLink="https://firecrawl.dev/app/api-keys"
    apiKeyLinkText="Firecrawl API Key"
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="firecrawl"
      description="Web scraping and crawling capabilities"
      type="stdio"
      command="npx -y firecrawl-mcp"
      timeout={300}
      envVars={[
        { key: "FIRECRAWL_API_KEY", value: "<Your Firecrawl API Key>" }
      ]}
      infoNote={
        <>
          Obtain your <a href="https://firecrawl.dev/app/api-keys" target="_blank" rel="noopener noreferrer">Firecrawl API Key</a> and paste it in.
        </>
      }
    />
    </TabItem>
</Tabs>

### 示例用法

Firecrawl MCP 服务器提供全面的网页抓取和爬取能力，包括：

- **单页抓取**：从单个网页中提取干净、结构化的内容
- **批量处理**：通过批量操作高效抓取多个 URL
- **站点爬取**：以可自定义的深度爬取整个网站或特定部分
- **搜索集成**：在已爬取的内容中搜索，并支持高级过滤

#### goose 提示词

```
I'm building a multiplayer game and trying to decide between Photon and Unity Netcode. Can you scrape their official documentation and recent comparison articles to help me understand the pros and cons of each platform, including performance, pricing, ease of use, and scalability?
```

#### goose 输出

```
I'll help you research Photon and Unity Netcode by scraping their official documentation and finding recent comparison articles. Let me start by gathering information from both platforms' official sites and then look for comparison articles.

──────────────  Firecrawl ─────────────────
Firecrawl Scrape url, formats, onlyMainContent

Firecrawl Scrape url, formats, onlyMainContent

Firecrawl Search query, limit, sources

Firecrawl Scrape url, formats, onlyMainContent

Firecrawl Scrape url, formats, onlyMainContent

Firecrawl Search query, limit, sources

Firecrawl Scrape url, formats, onlyMainContent

Firecrawl Search query, limit, sources

Firecrawl Scrape url, formats, onlyMainContent


Based on my research of the official documentation and recent discussions, I'll provide you with a comprehensive comparison of Photon and Unity Netcode for multiplayer game development.


Photon vs Unity Netcode: Comprehensive Comparison

Overview

Photon is a mature, third-party multiplayer networking solution with multiple products (PUN, Fusion, Quantum) that has been powering games for over a decade. Unity Netcode refers to Unity's first-party networking solutions, primarily Netcode for GameObjects and Netcode for Entities.


Performance Comparison

Photon Fusion

Bandwidth Usage: 6x more efficient than Unity's MLAPI/Mirror
Player Count: Supports thousands of networked objects across hundreds of client connections
Features: Tick-based simulation, client-side prediction, lag compensation, snapshot interpolation
Optimization: Advanced replication algorithms (full consistency vs eventual consistency)

Unity Netcode

Netcode for GameObjects: Designed for casual co-op games (smaller scale)
Netcode for Entities: Built for competitive action games with ECS architecture
Performance: Generally less optimized than Photon Fusion for bandwidth usage
Features: Client/server authoritative models, prediction, interpolation
Winner: Photon Fusion for raw performance and bandwidth efficiency


Pricing Comparison

Photon Pricing (2024)
  Free Tier:
  - 20 CCU for development only
  - 100 CCU for launched games (≈40k MAU)

  Paid Plans:
  - 500 CCU: $95/month (≈200k MAU)
  - 1,000 CCU: $195/month (≈400k MAU)
  - 2,000 CCU: $395/month (≈800k MAU)
  - Premium Cloud: $580/month minimum (auto-scaling up to 50k CCU)

  One-time Options:
  - PUN Plus: $95 one-time for 100 CCU (12 months)

Unity Gaming Services Pricing
  Free Tier:
  - Relay: First 50 average monthly CCU free
  - Lobby: 10 GiB/month bandwidth free
  - Multiplay: $800 credit for 6 months
  
  Paid Plans:
  - Relay: $0.16 per additional average CCU

  Multiplay Hosting:
  - CPU: $0.038/hour per core
  - RAM: $0.0051/GiB/hour
  - Network: $0.14/GiB

  No free tier after credits expire

Winner: Photon for small to medium games; Unity potentially cheaper for very large scale with dedicated servers


Ease of Use

Photon

Pros:
- Mature documentation and tutorials
- Large community and extensive examples
- Works out-of-the-box with minimal setup
- Cross-platform support (including WebGL without server setup)
Cons:
- Third-party dependency
- Learning curve for advanced features

Unity Netcode

Pros:
- First-party Unity integration
- Consistent with Unity's development patterns
- Direct support from Unity
Cons:
- Newer solution with evolving documentation
- Requires more setup for WebGL (needs Relay service)
- Steeper learning curve for Netcode for Entities

Winner: Photon for immediate productivity and WebGL deployment


Scalability

Photon
- Global Infrastructure: 15+ regions worldwide
- DDoS Protection: Built-in for higher tiers
- Auto-scaling: Available in Premium Cloud plans
- Maximum: Up to 50k CCU (Premium), unlimited (Enterprise)

Unity Netcode
- Infrastructure: Leverages Google Cloud
- Scaling: Manual server management required
- Distributed Authority: New topology for better scaling
- Maximum: Depends on your server infrastructure investment

Winner: Photon for managed scaling; Unity for custom infrastructure control


Platform Support

Photon
- Platforms: All major platforms including WebGL, mobile, console, VR/AR
- WebGL: Works seamlessly without dedicated servers
- Cross-play: Full support across all platforms

Unity Netcode
- Platforms: All Unity-supported platforms
- WebGL: Requires Unity Relay service for multiplayer
- Cross-play: Supported but requires additional setup

Winner: Tie - both support all major platforms


Key Considerations for Your Decision

Choose Photon if:
- You want to deploy quickly, especially to WebGL
- You need proven, battle-tested networking
- You prefer managed infrastructure
- Your game will have moderate CCU (under 10k)
- You want extensive documentation and community support

Choose Unity Netcode if:
- You want first-party Unity integration
- You plan to scale to very high CCU with custom servers
- You need tight control over server infrastructure
- You're building competitive games requiring ECS performance
- You want to avoid third-party dependencies

Recent Community Insights

From the Unity forums discussion, developers note:
- Photon Fusion offers 100 CCU free for one app, combinable with subscriptions
- Unity Multiplay has no free tier but provides $800 credit for 6 months
- WebGL deployment is simpler with Photon as it handles the server backend
- Migration between frameworks requires touching every networking script

Recommendation

For most indie and small-to-medium studios, Photon offers better value and ease of use, especially for WebGL deployment. For larger studios with dedicated infrastructure teams or those requiring maximum performance at scale, Unity Netcode with custom server management might be more cost-effective long-term.

The choice ultimately depends on your specific needs: immediate deployment ease (Photon) vs. long-term infrastructure control (Unity).
```

---

## Apify 扩展

> 原文：https://block.github.io/goose/docs/mcp/apify-mcp

本教程介绍如何把 [Apify MCP server](https://mcp.apify.com) 添加为 goose 扩展，让 goose 能够调用 [Apify Store](https://apify.com/store) 中数千个工具，从社交媒体、电商网站、搜索引擎、在线地图或任何其他网站中提取数据。

### 配置

<Tabs groupId="remote-or-local">
<!-- REMOTE SETUP -->
<TabItem value="remote" label="Apify Remote MCP" default>

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
   [启动安装器](goose://extension?type=streamable_http&url=https%3A%2F%2Fmcp.apify.com&id=apify&name=Apify&description=Extract%20data%20from%20any%20website%20with%20thousands%20of%20scrapers%2C%20crawlers%2C%20and%20automations%20on%20Apify%20Store&header=Authorization%3DBearer%20YOUR_APIFY_TOKEN)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  添加一个 `Remote Extension (Streamable HTTP)` 类型的扩展，配置如下：

  **端点 URL**
```
https://mcp.apify.com
```
  </TabItem>
</Tabs>

  **自定义请求头**
```
Authorization: Bearer <YOUR_APIFY_TOKEN>
```
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="apify"
      extensionName="Apify"
      description="Extract data from any website with thousands of scrapers, crawlers, and automations on Apify Store"
      type="http"
      url="https://mcp.apify.com"
      envVars={[
        { name: "Authorization", label: "Bearer YOUR_APIFY_TOKEN" }
      ]}
      apiKeyLink="https://console.apify.com/settings/integrations"
      apiKeyLinkText="Apify Token"
    />
  </TabItem>

  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Apify"
      description="Extract data from any website with thousands of scrapers, crawlers, and automations on Apify Store"
      type="http"
      url="https://mcp.apify.com"
      timeout={300}
      envVars={[
        { key: "Authorization", value: "Bearer apify_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" }
      ]}
      infoNote={
        <>
          Obtain your <a href="https://console.apify.com/settings/integrations" target="_blank" rel="noopener noreferrer">Apify Token</a> and paste it in as the <code>Bearer</code> token.
        </>
      }
    />
  </TabItem>
</Tabs>

</TabItem>

<!-- LOCAL SETUP -->
<TabItem value="local" label="Apify Local MCP">

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=@apify/actors-mcp-server&arg=start&id=mcp_apify_local&name=Apify%20Local%20MCP%20Server&description=Run%20Apify%20MCP%20server%20locally%20using%20your%20token&env=APIFY_TOKEN%3DYour%20Apify%20Token)
  </TabItem>

  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
npx -y @apify/actors-mcp-server
```
  </TabItem>
</Tabs>

**环境变量**
```
APIFY_TOKEN: <YOUR_APIFY_TOKEN>
```
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="mcp_apify_local"
      extensionName="Apify Local MCP Server"
      description="Extract data from any website with thousands of scrapers, crawlers, and automations on Apify Store"
      type="stdio"
      command="npx"
      args={["-y", "@apify/actors-mcp-server"]}
      envVars={[
        { name: "APIFY_TOKEN", label: "<YOUR_APIFY_TOKEN>" }
      ]}
      apiKeyLink="https://console.apify.com/settings/integrations"
      apiKeyLinkText="Apify Token"
    />
  </TabItem>

  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Apify Local MCP Server"
      description="Extract data from any website with thousands of scrapers, crawlers, and automations on Apify Store"
      type="stdio"
      command="npx -y @apify/actors-mcp-server"
      timeout={300}
      envVars={[
        { key: "APIFY_TOKEN", value: "apify_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" }
      ]}
      infoNote={
        <>
          Obtain your <a href="https://console.apify.com/settings/integrations" target="_blank" rel="noopener noreferrer">Apify Token</a> and paste it in.
        </>
      }
    />
  </TabItem>
</Tabs>

</TabItem>
</Tabs>

### 示例用法

Apify MCP 服务器让你把 goose 连接到 [Apify Store](https://apify.com/store)，这是一个汇集了数千个现成工具（称为 _Actors_）的市场，涵盖各种网页抓取、爬取和数据提取用例。你可以在 [官方文档](https://docs.apify.com/platform/actors) 中进一步了解 Apify Actors。

在这个示例中，goose 将使用 [Google Places Scraper](https://apify.com/compass/crawler-google-places) Actor，根据公开评分、评论和精致餐饮认可度，找出布拉格最可信、评分最高的意大利餐厅。

#### goose 提示词

```

( O)> Find the top-rated Italian restaurant in Prague with verifiable credibility — use Apify MCP to find Google Maps review scraper Actor, focus on places with at least 200+ reviews, an average rating of 4.7 or higher on Google, TripAdvisor, or OpenTable, and any Michelin or fine-dining recognition. Include the restaurant’s name, rating, total review count, address, cuisine style, and a short summary of what makes it stand out (e.g., service, ambiance, or signature dishes). Return to me only 1 restaurant with the highest rating to review count ratio

```

#### goose 输出

```

Based on the gathered information, the top-rated Italian restaurant in Prague with verifiable credibility is:

### **Al Tagliere**

* **Rating:** 4.7/5
* **Total Reviews:** 457
* **Address:** [Al Tagliere on TripAdvisor](https://www.tripadvisor.com/Restaurant_Review-g274707-d6835155-Reviews-Al_Tagliere-Prague_Bohemia.html)
* **Cuisine Style:** Italian
* **Summary:** Al Tagliere is celebrated for its authentic Italian dishes that showcase regional flavors. The restaurant is known for its delightful ambiance, attentive service, and signature dishes such as homemade pasta and traditional desserts. Patrons frequently highlight the freshness of ingredients and the welcoming atmosphere, making it a preferred choice for both locals and tourists.

This restaurant has a strong reputation and meets your criteria for quality and credibility.

```

---

## AgentQL 扩展

> 原文：https://block.github.io/goose/docs/mcp/agentql-mcp

<!-- <YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/VIDEO_ID" /> -->

本教程介绍如何把 [AgentQL MCP Server](https://github.com/tinyfish-io/agentql-mcp) 添加为 goose 扩展，以把非结构化的网页内容提取并转换为结构化数据。

:::tip 快速安装

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=-y&arg=agentql-mcp&id=agentql-mcp&name=AgentQL&description=Transform%20unstructured%20web%20content%20into%20structured%20data&env=AGENTQL_API_KEY%3DAgentQL%20API%20Key)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
npx -y agentql-mcp
```
  </TabItem>
</Tabs>
  **环境变量**
```
AGENTQL_API_KEY: <YOUR_API_KEY>
```
:::

### 配置

:::info
注意，你需要在系统中安装 [Node.js](https://nodejs.org/) 才能运行该命令，因为它使用了 `npx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="agentql-mcp"
    extensionName="AgentQL"
    description="Transform unstructured web content into structured data"
    command="npx"
    args={["-y", "agentql-mcp"]}
    envVars={[
      { name: "AGENTQL_API_KEY", label: "AgentQL API Key" }
    ]}
    apiKeyLink="https://dev.agentql.com/api-keys"
    apiKeyLinkText="AGENTQL_API_KEY"
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="agentql"
      description="Transform unstructured web content into structured data"
      command="npx -y agentql-mcp"
      envVars={[
        { key: "AGENTQL_API_KEY", value: "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪" }
      ]}
      infoNote={
        <>
          Obtain your <a href="https://dev.agentql.com/api-keys" target="_blank" rel="noopener noreferrer">AgentQL API Key</a> and paste it in.
        </>
      }
    />

  </TabItem>
</Tabs>

### 示例用法

让我们用 AgentQL 扩展来收集并结构化技术会议数据，以帮助规划演讲日程。


#### goose 提示词

```
I'm a tech conference speaker planning my 2025-2026 submissions. 

Extract for developer conferences (attendance > 500) occurring between 2022-2024:
- Conference name
- Conference dates
- CFP timeline 

To identify:
- Consistent monthly patterns
- Whether conferences stick to same months yearly
- If CFP windows are consistent year-to-year
- Any shifts in traditional timing

Structure results as JSON
```

#### goose 输出

```
I'll help you analyze conference patterns using the web data extraction tool. Let me break this down into a few queries to get comprehensive data.

─── extract-web-data | agentql ──────────────────────────
prompt: ...
url: ...

Let me get some historical data to compare patterns:

─── extract-web-data | agentql ──────────────────────────
prompt: ....
url: ....

Based on my research and the available data, I'll provide an analysis of major tech conference patterns. Here's the structured JSON with my findings:

{
  "analysis": {
    "major_conference_patterns": {
      "timing_consistency": {
        "spring_events": {
          "typical_months": ["March", "April", "May"],
          "notable_conferences": [
            "Google I/O",
            "Microsoft Build",
            "DevOpsDays (various locations)"
          ],
          "cfp_patterns": "Usually opens 4-6 months before event, closes 2-3 months before"
        },
        "fall_events": {
          "typical_months": ["September", "October", "November"],
          "notable_conferences": [
            "AWS re:Invent",
            "KubeCon + CloudNativeCon"
          ],
          "cfp_patterns": "Usually opens 6-8 months before event, closes 4-5 months before"
        }
      },
      "observed_trends": {
        "timing_consistency": "High - Most major conferences maintain consistent months year-over-year",
        "cfp_windows": {
          "typical_duration": "6-12 weeks",
          "advance_notice": "4-8 months before event",
          "variation": "Regional events tend to have shorter CFP windows (4-6 weeks)"
        },
        "recent_shifts": [
          "Increased hybrid/virtual options post-2022",
          "More regional editions of major conferences",
          "Earlier CFP deadlines for larger events"
        ]
      }
    },
    "recommendations_for_2025_2026": {
      "spring_submissions": {
        "prepare_by": "September-October of previous year",
        "submit_during": "November-December of previous year"
      },
      "fall_submissions": {
        "prepare_by": "February-March",
        "submit_during": "March-April"
      }
    }
  }
}


Key Insights for Your Planning:

1. **Monthly Patterns**:
   - Spring conference season: March-May
   - Fall conference season: September-November
   - Summer tends to be lighter for major tech conferences
   - December-January typically quiet except for regional events

2. **Year-to-Year Consistency**:
   - Major conferences (AWS re:Invent, KubeCon, Google I/O) are very consistent with their timing
   - Regional versions of major conferences (like DevOpsDays) show more date flexibility
   - Most maintain the same quarter/season year over year

3. **CFP Windows**:
   - Larger conferences: 6-8 months before event
   - Regional conferences: 3-4 months before event
   - Trend toward longer review periods for major conferences
   - Many now have rolling or multi-phase CFP processes

4. **Recent Shifts**:
   - Earlier CFP deadlines compared to pre-2022
   - More hybrid/virtual components
   - Increased number of regional editions of major conferences
   - Longer review periods for submissions

For 2025-2026 planning, I recommend:
- Start preparing fall 2025 submissions by February-March 2025
- Start preparing spring 2026 submissions by September-October 2025
- Consider regional versions of major conferences as they often have later deadlines
- Keep track of multi-track conferences as they might have different CFP deadlines for different tracks

Would you like me to focus on any specific aspect of these patterns or provide more detailed information about particular conferences?
```

---

## Scholar Sidekick 扩展

> 原文：https://block.github.io/goose/docs/mcp/scholar-sidekick-mcp

本教程介绍如何把 [Scholar Sidekick MCP Server](https://github.com/mlava/scholar-sidekick-mcp) 添加为 goose 扩展，以便从任意学术标识符 —— DOI、PMID、PMCID、ISBN、ISSN、arXiv ID、ADS bibcode 或 WHO IRIS URL —— 解析、格式化、导出并核验学术引用，另附撤稿（Crossref + Retraction Watch）与开放获取（Unpaywall）检查。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=-y&arg=scholar-sidekick-mcp%40latest&id=scholar-sidekick&name=Scholar%20Sidekick&description=Resolve%2C%20format%2C%20export%2C%20and%20verify%20academic%20citations%20plus%20retraction%20and%20open-access%20checks&timeout=300)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
npx -y scholar-sidekick-mcp@latest
```
  </TabItem>
</Tabs>
  **无需 API key** —— 该服务器以匿名方式在免费、限速的档位上运行。可选地设置 `SCHOLAR_API_KEY`（一个来自 [scholar-sidekick.com/account](https://scholar-sidekick.com/account) 的免费 `ssk_` key）以获得更高限额，或设置 `RAPIDAPI_KEY` 以使用付费档位。参见 [可选：更高的速率限制](#optional-higher-rate-limits)。
:::

### 配置

:::info
你需要安装 [Node.js](https://nodejs.org/)（该命令使用了 `npx`）。**无需 API key** —— Scholar Sidekick 以匿名方式在免费、限速的档位上运行。若要更高限额，可添加一个免费的第一方 key（`SCHOLAR_API_KEY`，一个来自 [scholar-sidekick.com/account](https://scholar-sidekick.com/account) 的 `ssk_` key）；若使用付费/托管档位，可添加一个 [RapidAPI key](https://rapidapi.com/scholar-sidekick-scholar-sidekick-api/api/scholar-sidekick)（`RAPIDAPI_KEY`）。参见下方的 [可选：更高的速率限制](#optional-higher-rate-limits)。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="scholar-sidekick"
      extensionName="Scholar Sidekick"
      description="Resolve, format, export, and verify academic citations plus retraction and open-access checks."
      type="stdio"
      command="npx"
      args={["-y", "scholar-sidekick-mcp@latest"]}
    />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Scholar Sidekick"
      description="Resolve, format, export, and verify academic citations plus retraction and open-access checks."
      type="stdio"
      command="npx -y scholar-sidekick-mcp@latest"
      timeout={300}
    />
  </TabItem>
</Tabs>

### 可选：更高的速率限制

Scholar Sidekick 在免费、限速的档位上**无需任何 key** 即可运行 —— 对普通的交互式使用来说已经足够。若要提高限额，为该扩展添加一个环境变量即可（goose Desktop：扩展设置 → 环境变量；CLI：`goose configure` → 该扩展的 env）：

- **`SCHOLAR_API_KEY`** —— 一个**免费**的第一方 key（前缀为 `ssk_`）。可在 [scholar-sidekick.com/account](https://scholar-sidekick.com/account) 创建。以 `Authorization: Bearer` 方式发送；它会提高你的速率限制，并解锁验证器可选的 LLM 筛查。
- **`RAPIDAPI_KEY`** —— 用于通过 [RapidAPI 网关](https://rapidapi.com/scholar-sidekick-scholar-sidekick-api/api/scholar-sidekick) 使用付费/托管档位。设置后，调用会经由 RapidAPI 路由，而不是匿名/第一方端点。

两者都不是必需的，你也永远不需要同时设置 —— 如果两者都设置了，RapidAPI 优先。

### 你可以做什么

Scholar Sidekick 提供六个工具，可将任意学术标识符转换为干净的引用、导出文件和完整性检查。内置五种引用格式（Vancouver、AMA、APA、IEEE、CSE），外加包含 10,000 多种格式的完整 CSL 目录。

#### 从任意标识符格式化引用

粘贴一个 DOI、PMID、PMCID、ISBN、ISSN、arXiv ID、ADS bibcode 或 WHO IRIS URL，即可获得按你所选格式排版的参考文献。识别是自动的 —— 请原样传入标识符（无需去掉 `PMID:`、`arXiv:` 或 `https://doi.org/` 前缀）。

**提示词：**

```
Format 10.1056/NEJMoa2033700 as a Vancouver-style citation.
```

#### 为你的文献管理器导出参考文献

传入一个或多个标识符，即可获得可导入的 BibTeX、RIS、EndNote XML、RefWorks、NBIB、Zotero RDF、CSV 或 CSL-JSON 文件。可直接拖入 Zotero、Mendeley、EndNote、JabRef 或 Citavi。

**提示词：**

```
Take these three DOIs and export them as BibTeX:
10.1056/NEJMoa2033700
10.1038/s41586-020-2649-2
10.1016/S0140-6736(20)32661-1
```

#### 检查论文是否被撤稿

交叉检索 Crossref 和 Retraction Watch，以发现撤稿、更正和关注声明。返回状态、原因和日期。

**提示词：**

```
Has 10.1016/S0140-6736(97)11096-0 been retracted?
```

#### 查找开放获取副本

查询 Unpaywall，以找出论文的最佳合法免费版本 —— 机构库副本、出版商 OA 或预印本 —— 并附带许可和版本信息（已接收版还是已发表版）。

**提示词：**

```
Is there a free open-access copy of 10.1371/journal.pone.0173664?
```

#### 验证引用是否真实

将一条*声称的*引用（标题、可选的作者/年份）与其标识符实际解析出的元数据进行交叉核对。它能捕捉 LLM 编造内容的主导模式 —— 一个真实、可解析的 DOI 配上虚构的标题和作者 —— 该模式由 Topaz 等人记录（Lancet，2026）。当一份 AI 生成的参考文献「看起来合理但……」时，就用它。

**提示词：**

```
Is this citation real? "A Unified Theory of Everything", Smith J, Nature, 2010, 10.1038/nphys1170
```

---

## YouTube Transcript 扩展

> 原文：https://block.github.io/goose/docs/mcp/youtube-transcript-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/N38u7hZqZJg" />

本教程介绍如何把 [YouTube Transcript MCP Server](https://github.com/jkawamoto/mcp-youtube-transcript) 添加为 goose 扩展，以支持获取和处理 YouTube 视频字幕。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=uvx&arg=--from&arg=git%2Bhttps%3A%2F%2Fgithub.com%2Fjkawamoto%2Fmcp-youtube-transcript&arg=mcp-youtube-transcript&id=youtube-transcript-mcp&name=YouTube%20Transcript&description=Access%20YouTube%20video%20transcripts)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
uvx --from git+https://github.com/jkawamoto/mcp-youtube-transcript mcp-youtube-transcript
```
  </TabItem>
</Tabs>
:::

### 配置


:::info
注意，你需要在系统中安装 [uv](https://docs.astral.sh/uv/#installation) 才能运行该命令，因为它使用了 `uvx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="youtube-transcript-mcp"
    extensionName="YouTube Transcript"
    description="Access YouTube video transcripts"
    command="uvx"
    args={["--from", "git+https://github.com/jkawamoto/mcp-youtube-transcript", "mcp-youtube-transcript"]}
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="YouTube Transcript"
      description="Access YouTube video transcripts"
      command="uvx --from git+https://github.com/jkawamoto/mcp-youtube-transcript mcp-youtube-transcript"
    />
  </TabItem>
</Tabs>

### 示例用法

YouTube Transcript 扩展让你可以获取并处理 YouTube 视频的字幕。你需要从想要获取字幕的 YouTube URL 中取得视频 ID。

#### goose 提示词

```
Get me the transcript for this YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

#### goose 输出

:::note CLI
我来帮你获取那个视频的字幕。视频 ID 是「dQw4w9WgXcQ」。让我为你获取字幕。

以下是字幕：

[字幕内容会在这里出现，带有时间戳和文本]

我已经取回了 Rick Astley 的「Never Gonna Give You Up」音乐视频的字幕。字幕展示了这首歌的歌词，不过由于系统是自动处理的，存在一些轻微的转写错误。字幕包含这首 1987 年著名歌曲标志性的副歌和主歌，它已成为最广为人知的互联网梗之一，常被用于「rickrolling」。

关于这个视频或其字幕，还需要我帮你做别的事情吗？
:::

---

## Kiwi 航班搜索扩展

> 原文：https://block.github.io/goose/docs/mcp/kiwi-flight-search

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/MhLU91zKE4M" />

服务器已迁移：https://apify.com/agentify/kiwi-mcp-server

本教程介绍如何把 [Kiwi Flight Search MCP Server](https://mcp.kiwi.com) 添加为 goose 扩展，以启用航班搜索和价格比较。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  在 设置 → 扩展 中使用 `Add custom extension` 添加一个 `Streamable HTTP` 类型的扩展，配置如下：
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  使用 `goose configure` 添加一个 `Remote Extension (Streamable HTTP)` 类型的扩展，配置如下：
  </TabItem>
</Tabs>

  **端点 URL**
```
https://mcp.kiwi.com
```
:::

### 配置

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏
    2. 点击 `Extensions`
    3. 点击 `Add custom extension`
    4. 在 `Add custom extension` 弹窗中，输入以下内容：
       - **扩展名称**：Kiwi Flight Search
       - **类型**：Streamable HTTP
       - **端点**：`https://mcp.kiwi.com`
    5. 点击 `Add Extension` 保存该扩展
    6. 进入聊天界面

  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="kiwi-flight-search"
      type="http"
      url="https://mcp.kiwi.com"
      timeout={300}
    />

  </TabItem>
</Tabs>

### 示例用法

让我们搜索任意两个地点在指定日期的航班。你可以按城市名或机场代码搜索，该扩展会找出可用航班，并附带价格、时长和预订链接。

#### goose 提示词

```
Can you help me search for a flight from Paris to Rome for August 9?
```

#### goose 输出

```
I'd be happy to help you search for flights from Paris to Rome for August 9th! Let me search for available options for you.

## ✈️ Flight Options: Paris → Rome (August 9, 2025)

### 💰 **Best Prices** (Cheapest Options)

| Route | Departure → Arrival | Class | Price | Book |
|-------|-------------------|-------|-------|------|
| Paris ORY → Rome FCO | 09/08 22:10 → 00:10+1 (2h 0m) | Economy | €138 | [Book Now](https://on.kiwi.com/ZyIJ2r) |
| Paris ORY → Rome FCO | 09/08 09:05 → 11:10 (2h 5m) | Economy | €154 | [Book Now](https://on.kiwi.com/31IDMW) |
| Paris ORY → Rome FCO | 09/08 06:25 → 08:25 (2h 0m) | Economy | €157 | [Book Now](https://on.kiwi.com/2dNs3f) |

### ⚡ **Shortest Flights** (Fastest Duration)

| Route | Departure → Arrival | Class | Price | Book |
|-------|-------------------|-------|-------|------|
| Paris ORY → Rome FCO | 09/08 06:25 → 08:25 (2h 0m) | Economy | €157 | [Book Now](https://on.kiwi.com/2dNs3f) |
| Paris ORY → Rome FCO | 09/08 22:10 → 00:10+1 (2h 0m) | Economy | €138 | [Book Now](https://on.kiwi.com/ZyIJ2r) |
| Paris CDG → Rome FCO | 09/08 21:10 → 23:10 (2h 0m) | Economy | €187 | [Book Now](https://on.kiwi.com/62jyt7) |

### 🕐 **Other Good Options**

| Route | Departure → Arrival | Class | Price | Book |
|-------|-------------------|-------|-------|------|
| Paris ORY → Rome FCO | 09/08 12:00 → 14:05 (2h 5m) | Economy | €164 | [Book Now](https://on.kiwi.com/m55oIC) |
| Paris ORY → Rome FCO | 09/08 21:10 → 23:10 (2h 0m) | Economy | €165 | [Book Now](https://on.kiwi.com/tkAU0T) |

## 📋 **Summary & Recommendations**

**🏆 Best Overall Value:** The **€138 evening flight** (ORY 22:10 → FCO 00:10+1) offers the best price with the shortest flight time, though it arrives after midnight.

**🌅 Best Morning Option:** The **€157 early flight** (ORY 06:25 → FCO 08:25) gets you to Rome early in the day with a quick 2-hour flight.

**⏰ Best Daytime Flight:** The **€154 mid-morning flight** (ORY 09:05 → FCO 11:10) offers great value and convenient timing.

All direct flights are around 2 hours, departing from either Paris Orly (ORY) or Charles de Gaulle (CDG) to Rome Fiumicino (FCO).

Have a wonderful trip to Rome! 🇮🇹 Fun fact: Rome has more fountains than any other city in the world - over 2,000 of them! Don't forget to toss a coin into the Trevi Fountain to ensure your return to the Eternal City! ⛲✨

```

---

## Speech 扩展

> 原文：https://block.github.io/goose/docs/mcp/speech-mcp

<YouTubeShortEmbed videoUrl="https://youtube.com/embed/rurAp_WzOiY" />


本教程介绍如何把 [Speech MCP Server](https://github.com/Kvadratni/speech-mcp) 添加为 goose 扩展，以启用实时语音交互、音频/视频转写、文本转语音转换以及多说话人音频生成。

:::info 要求
PyAudio 需要 [PortAudio](https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/scripts/readme-gen/templates/install_portaudio.tmpl.rst#install-portaudio) 才能从你的麦克风采集音频
:::

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=uvx&arg=-p&arg=3.10.14&arg=speech-mcp@latest&id=speech_mcp&name=Speech%20Interface&description=Voice%20interaction%20with%20audio%20visualization%20for%20goose)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
uvx -p 3.10.14 speech-mcp@latest
```
  </TabItem>
</Tabs>
:::

### 配置

:::info
注意，你需要在系统中安装 [uv](https://docs.astral.sh/uv/#installation) 才能运行该命令，因为它使用了 `uvx`。

在添加此扩展之前，请确保系统中已安装 [PortAudio](https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/scripts/readme-gen/templates/install_portaudio.tmpl.rst#install-portaudio)。**PortAudio 是必需的**，PyAudio 需要它才能从你的麦克风采集音频。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="speech_mcp"
    extensionName="Speech Interface"
    description="Voice interaction with audio visualization for goose"
    command="uvx"
    args={["-p", "3.10.14", "speech-mcp@latest"]}
  />
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

  3. 为你的扩展起一个名字
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
  │  speech
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
  │  speech
  │
  // highlight-start
  ◆  What command should be run?
  │  uvx -p 3.10.14 speech-mcp@latest
  // highlight-end
  └ 
```

  5. 输入 goose 在超时之前应等待动作完成的秒数。默认值为 300 秒
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
  │  speech
  │
  ◇  What command should be run?
  │  uvx -p 3.10.14 speech-mcp@latest
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
  ◇  What type of extension would you like to add?
  │  Command-line Extension 
  │
  ◇  What would you like to call this extension?
  │  speech
  │
  ◇  What command should be run?
  │  uvx -p 3.10.14 speech-mcp@latest
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

  7. 当被问到是否添加环境变量时，选择 No
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
  │  speech
  │
  ◇  What command should be run?
  │  uvx -p 3.10.14 speech-mcp@latest
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
  │
  // highlight-end
  └  Added speech extension
```

  </TabItem>
</Tabs>


### 示例用法
在这个示例中，你将看到如何结合 Speech MCP Server 扩展使用 goose，把语音命令变成代码。通过直接对 goose 说话，你可以启动语音界面、给出一个语音提示词，并让 goose 根据你的请求生成并打开一个网页。

这让你能够免手动地用 goose 构建，使开发更加易用、更具交互性。

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
以下是你可以对 goose 说的一些话，用来激活语音界面：

- “goose，我今天不想打字。”
- “我们用语音聊聊吧。”
- “我们能进行语音对话吗？”
- “我想说而不是打字。”
- “goose，启动语音 UI。”

```
goose I don't feel like talking today
```
#### goose 输出
```
I understand! In that case, I can help you use voice commands instead. I'll launch the speech interface so you can speak your requests rather than type them

---- Launch Speech UI ----
```

#### goose 语音 🎙️

**goose：**
>_我已经启动了语音界面。你现在可以说出你的请求，而不必打字。在听到我的声音并看到麦克风激活后，直接说话即可。你需要什么帮助？_


**Max：**

>_goose，我们来创建一个简单的页面，上面写着「vibes」这个词，也许再改改颜色，让它在页面上到处移动，完成后在浏览器里打开这个页面_


<div style={{ width: "100%", height: 0, position: "relative", paddingBottom: "56.25%" }}>
  <iframe
    src="https://www.youtube.com/embed/vbD8IHwx-OY"
    frameBorder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowFullScreen
    title="YouTube video"
    style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
  ></iframe>
</div>

---

## ElevenLabs 扩展

> 原文：https://block.github.io/goose/docs/mcp/elevenlabs-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/1Z8XtjQ9El0" />


本教程介绍如何把 [ElevenLabs MCP Server](https://github.com/elevenlabs/elevenlabs-mcp) 添加为 goose 扩展，以启用 AI 驱动的语音生成、声音克隆、音频编辑和语音转文字转写。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=uvx&arg=elevenlabs-mcp&id=elevenlabs-mcp&name=ElevenLabs&description=ElevenLabs%20voice%20synthesis%20server&env=ELEVENLABS_API_KEY)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
uvx elevenlabs-mcp
```
  </TabItem>
</Tabs>

  **环境变量**
```
ELEVENLABS_API_KEY: <YOUR_API_KEY>
```
:::

### 配置

:::info
注意，你需要在系统中安装 [uv](https://docs.astral.sh/uv/#installation) 才能运行该命令，因为它使用了 `uvx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="elevenlabs-mcp"
      extensionName="ElevenLabs"
      description="ElevenLabs voice synthesis server"
      command="uvx"
      args={["elevenlabs-mcp"]}
      envVars={[
        { name: "ELEVENLABS_API_KEY", label: "ElevenLabs API Key" }
      ]}
      apiKeyLink="https://elevenlabs.io/app/settings/api-keys"
      apiKeyLinkText="ElevenLabs API Key"
    />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="ElevenLabs"
      description="ElevenLabs voice synthesis server"
      command="uvx elevenlabs-mcp"
      envVars={[
        { key: "ELEVENLABS_API_KEY", value: "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪" }
      ]}
      infoNote={
        <>
          Obtain your <a href="https://elevenlabs.io/app/settings/api-keys" target="_blank" rel="noopener noreferrer">ElevenLabs API Key</a> and paste it in.
        </>
      }
    />
  </TabItem>
</Tabs>

### 示例用法

在这个示例中，我将向你展示如何结合 ElevenLabs 扩展使用 goose，为一个 YouTube Short 制作 AI 生成的配音。goose 会拿到我提供的一段示例脚本，用不同的 AI 声音生成一个旁白版本，并在脚本中途无缝切换语气，以贴合内容走向。

通过连接 ElevenLabs MCP 服务器，goose 可以把纯文本转换成听起来自然的语音，提供多种声音风格和角色选项 —— 全程无需任何手动录音或编辑。

#### goose 提示词

> 嘿 goose，帮我为我的 youtube short 视频写一段脚本，我想要有两种不同的声音。第一个声音应该打断我，采用人类旁白风格，然后在我念完提示词之后切换成随性的 AI 语气。这是我过去做过的一个 YT short 脚本示例：

等等……几秒之内，goose 就在多个项目中执行了安全审计？！🔥

让我们即插即用，看看是怎么回事

让我们给 goose 提供它连接 Filesystem MCP 服务器扩展所需的命令……

现在让我们开始吧
prompt: "嘿 goose，我需要在多个项目中执行一次安全审计。我们来检查一下……🔹 硬编码凭证 —— 遗留在代码中的 API key、密码和密钥。🔹 SQL 注入风险 —— 可能泄露数据的不安全查询。🔹 不安全的加密实践 —— 让数据面临风险的弱加密方法。还有 🔹 暴露的配置文件 —— 不应公开的敏感信息。🔹 过时的依赖 —— 第三方库中的安全漏洞。"

Go goose, go goose!

✅ goose 扫描了 3 个不同项目的整个代码库，识别出安全风险，生成了一份包含修复方案的详细报告，并为我提供了可以如何测试和验证这些代码修复的逐步说明！

如果这都不算惊艳，那我也不知道什么算了……

🚀 要开始使用，请访问 goose-docs.ai_


#### goose 输出

:::note Desktop

我会以你提供的脚本作为参考，为你创建 YouTube 脚本。

───────────── Text To Speech ─────────────

───────────── Text To Speech ─────────────

───────────── Text To Speech ─────────────

───────────── Text To Speech ─────────────

───────────── Text To Speech ─────────────

───────────── Play Audio  ────────────────

───────────── Play Audio  ────────────────

脚本已经创建完成，并使用指定的声音和风格朗读了出来。音频文件已保存到你的桌面。

按下播放，亲自听听吧！🔊

<audio controls>
  <source src="https://block.github.io/goose/audio/elevenlabs-mcp-demo.mp3" type="audio/mpeg" />
  Your browser does not support the audio element.
</audio>

:::

---

## prompts.chat 扩展

> 原文：https://block.github.io/goose/docs/mcp/prompts-chat-mcp

本教程介绍如何把 [prompts.chat MCP Server](https://prompts.chat) 添加为 goose 扩展，以便直接在你的 AI 助手中访问数千条 AI 提示词。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=-y&arg=@fkadev/prompts.chat-mcp@latest&id=prompts-chat-mcp&name=prompts.chat&description=Access%20thousands%20of%20AI%20prompts%20directly%20in%20your%20AI%20assistant&env=PROMPTS_API_KEY%3DAPI%20Key%20to%20save%20and%20list%20private%20prompts)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
npx -y @fkadev/prompts.chat-mcp@latest
```
  </TabItem>
</Tabs>
  **环境变量（可选）**
```
PROMPTS_API_KEY: <YOUR_API_KEY>
```
:::

### 配置

:::info
注意，你需要在系统中安装 [Node.js](https://nodejs.org/) 才能运行该命令，因为它使用了 `npx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="prompts-chat-mcp"
    extensionName="prompts.chat"
    description="Access thousands of AI prompts directly in your AI assistant"
    command="npx"
    args={["-y", "@fkadev/prompts.chat-mcp@latest"]}
    envVars={[
      { name: "PROMPTS_API_KEY", label: "API Key to save and list private prompts on prompts.chat (optional)" }
    ]}
    apiKeyLink="https://prompts.chat"
    apiKeyLinkText="prompts.chat API Key"
  />
</TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="prompts.chat"
      description="Access thousands of AI prompts directly in your AI assistant"
      command="npx -y @fkadev/prompts.chat-mcp@latest"
      envVars={[
        { key: "PROMPTS_API_KEY", value: "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪" }
      ]}
      infoNote={
        <>
          The PROMPTS_API_KEY is optional. If you want to save and list private prompts, obtain your API key from{" "}
          <a href="https://prompts.chat" target="_blank" rel="noopener noreferrer">
            prompts.chat
          </a> and paste it in.
        </>
      }
    />
  </TabItem>
</Tabs>

### 示例用法

prompts.chat 扩展提供了一个精选的 AI 提示词库，你可以直接在 goose 中搜索和使用。当你需要灵感，或想为特定任务借用经过验证的提示词模式时，这会很有用。

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

#### 搜索提示词

##### goose 提示词

```
Search for prompts about code review
```

##### goose 输出

```
I found several prompts related to code review:

1. **Code Review Assistant** - A comprehensive prompt for reviewing code quality, 
   security, and best practices
2. **Pull Request Reviewer** - Helps analyze pull requests and suggest improvements
3. **Security Code Audit** - Focuses on identifying security vulnerabilities

Would you like me to retrieve any of these prompts?
```

#### 使用提示词

##### goose 提示词

```
Get the Code Review Assistant prompt and use it to review my current file
```

##### goose 输出

```
I've retrieved the Code Review Assistant prompt. Let me apply it to analyze your code...

[Applying prompt guidelines to review your code]

Here's my review based on the prompt's framework:

✅ Code structure and organization
✅ Naming conventions
⚠️ Consider adding error handling for edge cases
⚠️ Documentation could be improved for public methods

Would you like me to help address any of these findings?
```

---

## Tutorial 扩展

> 原文：https://block.github.io/goose/docs/mcp/tutorial-mcp

Tutorial 扩展是 goose 的内置功能，为学习 goose 及其能力的各个方面提供交互式、逐步的引导。它旨在通过动手实践，帮助用户熟悉 goose 的各项功能。

Tutorial 扩展是一个交互式学习工具，它：
- 提供结构化、逐步的教程
- 让你可以动手实践 goose 的功能
- 提供即时反馈和引导

### 配置

1. 确保 Tutorial 扩展已启用：

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseBuiltinInstaller
    extensionName="Tutorial"
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
│  ● tutorial
// highlight-end
|
└  Extension settings updated successfully
```
</TabItem>
</Tabs>

### 可用的教程

目前，以下教程可用：

- **build-mcp-extension**：学习如何使用 Model Context Protocol（MCP）构建一个扩展
- **first-game**：用 goose 创建你的第一个游戏

我们正在定期添加更多教程，以覆盖更多功能和用例。

### 使用 Tutorial 扩展

#### 开始一个教程

有两种与教程交互的主要方式：

1. **直接询问 goose**：你可以直接询问你感兴趣的话题，goose 会推荐相关的教程。

```
( O)> I'd like to learn how to build an extension for goose
```

2. **请求指定的教程**：你可以直接按名称请求某个教程。

```
( O)> Can you walk me through the first-game tutorial?
```

#### 教程进行中

在浏览一个教程时：

1. goose 会逐步引导你完成整个过程
2. 在采取任何操作之前，你都会收到清晰的说明
3. 你可以随时提问以求澄清
4. 你可以中途休息，稍后再继续

#### 最佳实践

- **慢慢来**：不要在教程中赶进度。继续下一步之前，确保你理解了每一步。
- **多提问**：如果有不清楚的地方，请让 goose 进一步解释。
- **多做实验**：不妨尝试你所学的各种变体。
- **记笔记**：记录你学到的任何有趣发现或技巧。

### 示例用法

#### 开始一个教程会话

以下是一个如何开始学习构建扩展的示例：

#### goose 提示词
```
I'd like to learn how to build an extension for goose
```

#### goose 输出
```
I'll help you learn about building extensions! The "build-mcp-extension" tutorial would be perfect for this. Let me load it and guide you through it.

─── load_tutorial | tutorial ──────────────────────────
name: build-mcp-extension



Before we dive into building your extension, I need to understand a few things to better guide you:

1. Which SDK would you prefer to use? We have three options:
   - Python (beginner-friendly, great for prototyping)
   - TypeScript (great for web-based tools)
   - Kotlin (robust, type-safe, good for complex applications)

2. What type of extension would you like to build? For example:
   - A tool that performs specific actions
   - A resource that provides data to the LLM
   - Or do you have a specific idea in mind?

Let me know your preferences, and I'll help you get started with the appropriate setup and implementation!

For reference, here's what we'll cover:
1. Setting up your development environment
2. Creating the basic MCP server
3. Implementing your specific functionality
4. Testing and debugging

Which SDK would you like to use to get started?
```

### 后续步骤

完成教程后，你可以：
- 把学到的概念应用到你自己的项目中
- 通过分享你的经验为 goose 社区做贡献
- 提出对他人有帮助的新教程主题

#### 需要更多帮助？
如果你有疑问、遇到问题，或者只是想头脑风暴一些想法，欢迎加入 [Discord 社区][discord]！

[discord]: https://discord.gg/n8R5VaWDAn

---

## goose Docs 扩展

> 原文：https://block.github.io/goose/docs/mcp/goose-docs-mcp

本教程介绍如何把 [goose Docs MCP Server](https://github.com/idosal/git-mcp) 添加为 goose 扩展，让 goose 能够回答关于它自身的问题。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装器](goose://extension?cmd=npx&arg=mcp-remote&arg=https%3A%2F%2Fblock.gitmcp.io%2Fgoose%2F&id=goose-docs&name=goose%20Docs&description=gitmcp%20for%20goose%20documentation)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
npx mcp-remote https://block.gitmcp.io/goose/
```
  </TabItem>
</Tabs>
:::

### 配置

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="goose-docs"
      extensionName="goose Docs"
      description="GitMCP for goose documentation"
      command="npx"
      args={["mcp-remote", "https://block.gitmcp.io/goose/"]}
    />
 </TabItem>
  <TabItem value="cli" label="goose CLI">
      <CLIExtensionInstructions
        name="goose Docs"
        description="GitMCP for goose documentation"
        command="npx mcp-remote https://block.gitmcp.io/goose/"
        timeout={300}
      />
  </TabItem>
</Tabs>


### 示例用法
GitMCP 让你可以把任意 Git 仓库转换成一个 goose 扩展。goose Docs MCP Server 就是一个很好的例子，它提供了一种让 goose 回答关于自身问题的方式。

让我们请 goose 为我们创建一个 Recipe！它会使用 goose Docs MCP Server 来查找相关信息。


#### goose 提示词

```
hey goose, I want to create a recipe for automated code review that my development team can use. Can you look at the goose documentation to understand the recipe format, then create a recipe that:


1. Reviews pull requests for:

- Code quality issues and best practices
- Security vulnerabilities
- Missing unit tests
- Performance concerns

2. Should be parameterized so teams can customize:

- Programming language (Python, JavaScript, etc.)
- Minimum test coverage threshold
- Specific coding standards to enforce

3. Should output structured results that can be parsed by CI/CD systems

Please research the recipe format first using the goose Docs extension, then create a complete recipe file with proper YAML structure, parameters, and any needed extensions. 
Make it something a development team could immediately use in their workflow.
```


#### goose 输出

:::note Desktop

完美！基于对 goose 文档的研究，我已经创建了一份完整的自动化代码审查 Recipe。以下是我为你的开发团队构建的内容：

##### 📋 Recipe 概览

**Automated Code Review** Recipe（`automated-code-review.yaml`）提供：

##### ✅ **核心审查领域**
1. **代码质量与最佳实践** —— 架构、命名、复杂度、文档
2. **安全漏洞评估** —— OWASP Top 10、输入校验、认证问题
3. **测试覆盖率分析** —— 缺失的测试、覆盖率阈值、测试质量
4. **性能问题** —— 瓶颈、算法复杂度、资源管理
5. **技术债评估** —— 重构需求、可维护性问题

##### 🔧 **参数化特性**
- **`programming_language`** —— Python、JavaScript、Java、Go、Rust、TypeScript 等
- **`min_test_coverage`** —— 可自定义的阈值（默认：80%）
- **`coding_standards`** —— PEP8、ESLint、Google Style Guide、公司自定义规范
- **`security_focus`** —— 基础、标准或全面的安全分析
- **`performance_analysis`** —— 启用/禁用性能审查
- **`exclude_patterns`** —— 跳过某些文件/目录

##### 📊 **结构化的 CI/CD 输出**
该 Recipe 会输出一个完整的 JSON 结构，包含：
- **总体质量评分**和建议（批准/请求修改/拒绝）
- **分类后的问题**，带严重级别和具体文件位置
- **安全漏洞**，带 CWE ID 和修复步骤
- **测试覆盖率指标**和缺失测试的建议
- **性能问题**及优化建议
- **技术债评估**及工作量估算
- **CI/CD 元数据**，用于流水线集成

##### 🚀 **用法示例**

##### 基础用法：
```bash
goose run automated-code-review.yaml \
  --repository_path ./my-project \
  --programming_language Python
```

##### 进阶用法：
```bash
goose run automated-code-review.yaml \
  --repository_path ./my-project \
  --programming_language JavaScript \
  --min_test_coverage 85 \
  --coding_standards ESLint \
  --security_focus comprehensive \
  --exclude_patterns "*.test.js,dist/*,node_modules/*"
```

##### 🔧 **CI/CD 集成**

结构化的 JSON 输出使它非常适合 CI/CD 流水线：

```yaml
# Example GitHub Actions integration
- name: Run Code Review
  run: |
    goose run automated-code-review.yaml \
      --repository_path . \
      --programming_language ${{ matrix.language }} \
      --output review-results.json

- name: Process Results
  run: |
    # Parse JSON results for pipeline decisions
    RECOMMENDATION=$(jq -r '.review_summary.recommendation' review-results.json)
    if [ "$RECOMMENDATION" = "reject" ]; then
      exit 1
    fi
```

##### 📁 **文件结构**

该 Recipe 保存为你当前目录下的 `automated-code-review.yaml`，并包含：
- 遵循 goose recipe 格式的正确 YAML 结构
- 带默认值的完整参数定义
- 内置的 developer 扩展，用于文件系统访问
- 用于结构化输出的详细 JSON schema
- 用于参数替换的模板语法

你的开发团队只需把它放进他们的项目仓库中，并针对自己的具体需求自定义参数，就可以立即开始使用这份 Recipe！
:::

#### 生成的 Recipe 文件
<details>
<summary>automated-code-review.yaml</summary>

```yaml
version: "1.0.0"
title: "Automated Code Review"
description: "Comprehensive automated code review for pull requests with customizable standards and structured CI/CD output"

instructions: |
  You are an expert code reviewer with deep knowledge of software engineering best practices, 
  security vulnerabilities, and testing methodologies. Your role is to perform a thorough 
  code review focusing on:
  
  1. Code Quality & Best Practices
  2. Security Vulnerabilities  
  3. Test Coverage Analysis
  4. Performance Concerns
  5. Maintainability Issues
  
  Always provide actionable feedback with specific examples and suggestions for improvement.
  Consider the specified programming language conventions and coding standards.

parameters:
  - key: repository_path
    input_type: string
    requirement: required
    description: "Path to the repository or pull request to review"
  
  - key: programming_language
    input_type: string
    requirement: required
    description: "Primary programming language (e.g., Python, JavaScript, Java, Go, Rust, TypeScript)"
  
  - key: min_test_coverage
    input_type: number
    requirement: optional
    default: 80
    description: "Minimum test coverage threshold percentage (0-100)"
  
  - key: coding_standards
    input_type: string
    requirement: optional
    default: "industry_standard"
    description: "Coding standards to enforce (e.g., PEP8, ESLint, Google Style Guide, company_specific)"
  
  - key: security_focus
    input_type: string
    requirement: optional
    default: "standard"
    description: "Security review depth (basic, standard, comprehensive)"
  
  - key: performance_analysis
    input_type: string
    requirement: optional
    default: "true"
    description: "Enable performance analysis (true/false)"
  
  - key: exclude_patterns
    input_type: string
    requirement: optional
    default: "*.md,*.txt,*.json,node_modules/*,vendor/*,.git/*"
    description: "Comma-separated patterns of files/directories to exclude from review"

extensions:
  - type: builtin
    name: developer
    timeout: 600
    bundled: true
    description: "Access to file system and shell commands for code analysis"

prompt: |
  Perform a comprehensive code review of the {{ programming_language }} codebase at {{ repository_path }}.
  
  ## Review Scope
  - Programming Language: {{ programming_language }}
  - Minimum Test Coverage: {{ min_test_coverage }}%
  - Coding Standards: {{ coding_standards }}
  - Security Focus: {{ security_focus }}
  - Performance Analysis: {{ performance_analysis }}
  - Exclude Patterns: {{ exclude_patterns }}
  
  ## Analysis Requirements
  
  ### 1. Code Quality & Best Practices
  - Review code structure, organization, and architecture
  - Check adherence to {{ coding_standards }} standards
  - Identify code smells, anti-patterns, and technical debt
  - Evaluate naming conventions, documentation, and readability
  - Check for proper error handling and logging
  
  ### 2. Security Vulnerability Assessment
  {% if security_focus == "comprehensive" %}
  Perform comprehensive security analysis including:
  - OWASP Top 10 vulnerabilities
  - Input validation and sanitization
  - Authentication and authorization flaws
  - Cryptographic implementations
  - Dependency vulnerabilities
  - Information disclosure risks
  {% elif security_focus == "standard" %}
  Perform standard security review:
  - Common vulnerability patterns
  - Input validation issues
  - Authentication/authorization problems
  - Basic cryptographic concerns
  {% else %}
  Perform basic security check:
  - Obvious security anti-patterns
  - Hardcoded credentials
  - Basic input validation
  {% endif %}
  
  ### 3. Test Coverage Analysis
  - Analyze existing test files and coverage
  - Identify missing unit tests for critical functions
  - Check for integration and end-to-end test gaps
  - Evaluate test quality and maintainability
  - Verify test coverage meets {{ min_test_coverage }}% threshold
  
  ### 4. Performance Concerns
  {% if performance_analysis == "true" %}
  - Identify potential performance bottlenecks
  - Review algorithm complexity and efficiency
  - Check for memory leaks and resource management
  - Analyze database queries and data access patterns
  - Review caching strategies and optimization opportunities
  {% endif %}
  
  ### 5. Maintainability & Technical Debt
  - Assess code complexity and maintainability
  - Identify areas needing refactoring
  - Check for proper separation of concerns
  - Evaluate dependency management
  - Review documentation completeness
  
  ## Output Requirements
  Provide structured analysis that can be parsed by CI/CD systems, including:
  - Overall quality score and recommendation
  - Categorized issues with severity levels
  - Specific file locations and line numbers
  - Actionable remediation steps
  - Test coverage metrics and missing test recommendations
  - Security findings with risk assessments

response:
  json_schema:
    type: object
    properties:
      review_summary:
        type: object
        properties:
          overall_score:
            type: number
            minimum: 0
            maximum: 100
            description: "Overall code quality score (0-100)"
          recommendation:
            type: string
            enum: ["approve", "approve_with_suggestions", "request_changes", "reject"]
            description: "Review recommendation for CI/CD pipeline"
          total_issues:
            type: number
            description: "Total number of issues found"
          critical_issues:
            type: number
            description: "Number of critical/blocking issues"
        required: ["overall_score", "recommendation", "total_issues", "critical_issues"]
      
      code_quality:
        type: object
        properties:
          score:
            type: number
            minimum: 0
            maximum: 100
            description: "Code quality score"
          issues:
            type: array
            items:
              type: object
              properties:
                severity:
                  type: string
                  enum: ["critical", "major", "minor", "info"]
                category:
                  type: string
                  enum: ["architecture", "naming", "complexity", "documentation", "best_practices"]
                file_path:
                  type: string
                  description: "Relative path to the file"
                line_number:
                  type: number
                  description: "Line number where issue occurs"
                description:
                  type: string
                  description: "Description of the issue"
                suggestion:
                  type: string
                  description: "Suggested fix or improvement"
              required: ["severity", "category", "file_path", "description", "suggestion"]
        required: ["score", "issues"]
      
      security_analysis:
        type: object
        properties:
          risk_score:
            type: number
            minimum: 0
            maximum: 100
            description: "Security risk score (0=low risk, 100=high risk)"
          vulnerabilities:
            type: array
            items:
              type: object
              properties:
                severity:
                  type: string
                  enum: ["critical", "high", "medium", "low"]
                type:
                  type: string
                  description: "Type of vulnerability (e.g., SQL Injection, XSS, etc.)"
                file_path:
                  type: string
                line_number:
                  type: number
                description:
                  type: string
                impact:
                  type: string
                  description: "Potential impact of the vulnerability"
                remediation:
                  type: string
                  description: "Steps to fix the vulnerability"
                cwe_id:
                  type: string
                  description: "Common Weakness Enumeration ID if applicable"
              required: ["severity", "type", "file_path", "description", "impact", "remediation"]
        required: ["risk_score", "vulnerabilities"]
      
      test_coverage:
        type: object
        properties:
          current_coverage:
            type: number
            minimum: 0
            maximum: 100
            description: "Current test coverage percentage"
          meets_threshold:
            type: boolean
            description: "Whether coverage meets the minimum threshold"
          missing_tests:
            type: array
            items:
              type: object
              properties:
                file_path:
                  type: string
                function_name:
                  type: string
                line_number:
                  type: number
                priority:
                  type: string
                  enum: ["critical", "high", "medium", "low"]
                test_type:
                  type: string
                  enum: ["unit", "integration", "end_to_end"]
                description:
                  type: string
                  description: "Description of what should be tested"
              required: ["file_path", "function_name", "priority", "test_type", "description"]
          test_quality_issues:
            type: array
            items:
              type: object
              properties:
                file_path:
                  type: string
                issue:
                  type: string
                suggestion:
                  type: string
              required: ["file_path", "issue", "suggestion"]
        required: ["current_coverage", "meets_threshold", "missing_tests", "test_quality_issues"]
      
      performance_analysis:
        type: object
        properties:
          concerns:
            type: array
            items:
              type: object
              properties:
                severity:
                  type: string
                  enum: ["critical", "major", "minor"]
                type:
                  type: string
                  enum: ["algorithm_complexity", "memory_leak", "database_query", "resource_management", "caching"]
                file_path:
                  type: string
                line_number:
                  type: number
                description:
                  type: string
                impact:
                  type: string
                  description: "Performance impact description"
                optimization:
                  type: string
                  description: "Suggested optimization"
              required: ["severity", "type", "file_path", "description", "impact", "optimization"]
        required: ["concerns"]
      
      technical_debt:
        type: object
        properties:
          debt_score:
            type: number
            minimum: 0
            maximum: 100
            description: "Technical debt score (0=low debt, 100=high debt)"
          refactoring_suggestions:
            type: array
            items:
              type: object
              properties:
                priority:
                  type: string
                  enum: ["critical", "high", "medium", "low"]
                area:
                  type: string
                  enum: ["architecture", "code_duplication", "complexity", "dependencies", "documentation"]
                file_path:
                  type: string
                description:
                  type: string
                effort_estimate:
                  type: string
                  enum: ["small", "medium", "large"]
                business_impact:
                  type: string
              required: ["priority", "area", "file_path", "description", "effort_estimate"]
        required: ["debt_score", "refactoring_suggestions"]
      
      ci_cd_metadata:
        type: object
        properties:
          review_timestamp:
            type: string
            description: "ISO timestamp of when review was performed"
          reviewer:
            type: string
            description: "goose automated code review"
          language:
            type: string
            description: "Programming language reviewed"
          standards_applied:
            type: string
            description: "Coding standards that were applied"
          files_reviewed:
            type: number
            description: "Number of files reviewed"
          lines_of_code:
            type: number
            description: "Total lines of code reviewed"
        required: ["review_timestamp", "reviewer", "language", "standards_applied", "files_reviewed"]
    
    required: [
      "review_summary", 
      "code_quality", 
      "security_analysis", 
      "test_coverage", 
      "performance_analysis", 
      "technical_debt", 
      "ci_cd_metadata"
    ]

```

</details>
