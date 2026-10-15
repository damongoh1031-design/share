# goose 官方文档中文手册：第 19 章　教程（一）：扩展与集成实战

## 构建自定义扩展

> 原文：https://block.github.io/goose/docs/tutorials/custom-extensions

goose 允许你通过创建自己的自定义扩展来扩展其功能，这些扩展以 MCP 服务器形式构建。由于 goose 遵循 [Model Context Protocol (MCP)][mcp-docs]，这些扩展与 goose 兼容。MCP 是一个开放协议，它标准化了应用程序向 LLM 提供上下文的方式。它提供了一种一致的方式将 LLM 连接到各种数据源和工具，使其成为以结构化、可互操作的方式扩展功能的理想选择。

在本指南中，我们使用 [Python SDK for MCP][mcp-python] 构建一个 MCP 服务器。我们将演示如何创建一个读取 Wikipedia 文章并将其转换为 Markdown 的 MCP 服务器，并将其作为扩展集成到 goose 中。你可以按照类似的流程为 goose 开发自己的自定义扩展。

你可以在 [MCP servers 仓库][mcp-servers]中查看其他示例服务器。MCP SDK 也适用于其他常见语言，例如 [TypeScript][mcp-typescript] 和 [Kotlin][mcp-kotlin]。

:::info
goose 支持 [Model Context Protocol](https://modelcontextprotocol.io/) 中的 Tools、Resources 和 Prompts。关于支持的协议版本和客户端能力，请参阅 [`mcp_client.rs`](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/agents/mcp_client.rs)。
:::

---

### 前置条件

在开始之前，请确保你的系统上安装了以下内容：

- **Python 3.13 或更高版本** - MCP 服务器所必需
- **[uv](https://docs.astral.sh/uv/)** - 本教程使用的 Python 包管理器
- **Node.js 和 npm** - 仅当你想在[第 4 步](#step-4-test-your-mcp-server)中使用 MCP Inspector 开发工具时才需要。

---

### 第 1 步：初始化你的项目

第一步是使用 [uv][uv-docs] 创建一个新项目。我们将项目命名为 `mcp-wiki`。

在终端中运行以下命令，为你的 MCP 服务器搭建基本结构：

```bash
uv init --lib mcp-wiki
cd mcp-wiki

mkdir -p src/mcp_wiki
touch src/mcp_wiki/server.py
touch src/mcp_wiki/__main__.py
```

你的项目目录结构应如下所示：

```plaintext
.
├── README.md
├── pyproject.toml
└── src
    └── mcp_wiki
        ├── __init__.py   # Primary CLI entry point
        ├── __main__.py   # To enable running as a Python module
        ├── py.typed      # Indicates the package supports type hints
        └── server.py     # Your MCP server code (tool, resources, prompts)
```

---

### 第 2 步：编写你的 MCP 服务器代码

在这一步中，我们将实现 MCP 服务器的核心功能。以下是关键组件的分解：

1. **`server.py`**：该文件包含主 MCP 服务器代码。在此示例中，我们定义了一个用于读取 Wikipedia 文章的工具。你可以在此处添加自己的自定义工具、资源和提示词。
2. **`__init__.py`**：这是你的 MCP 服务器的主 CLI 入口点。
3. **`__main__.py`**：该文件允许你的 MCP 服务器作为 Python 模块执行。

以下是 Wikipedia MCP 服务器的示例实现：

#### `server.py`

```python
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from html2text import html2text
from urllib.parse import urlparse

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS

mcp = FastMCP("wiki")

@mcp.tool()
def read_wikipedia_article(url: str) -> str:
    """
    Fetch a Wikipedia article at the provided URL, parse its main content,
    convert it to Markdown, and return the resulting text.

    Usage:
        read_wikipedia_article("https://en.wikipedia.org/wiki/Python_(programming_language)")
    """
    try:
        # Validate input
        if not url.startswith("http"):
            raise ValueError("URL must start with http or https.")

        # SSRF protection: only allow Wikipedia domains
        parsed = urlparse(url)
        hostname = parsed.netloc.lower()

        # Allow wikipedia.org or *.wikipedia.org subdomains only
        if hostname != 'wikipedia.org' and not hostname.endswith('.wikipedia.org'):
            raise ValueError(f"Only Wikipedia URLs are allowed. Got: {parsed.netloc}")

        # Add User-Agent header to avoid 403 from Wikipedia
        headers = {
            'User-Agent': 'MCP-Wiki/1.0 (Educational purposes; Python requests)'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Failed to retrieve the article. HTTP status code: {response.status_code}"
                )
            )

        soup = BeautifulSoup(response.text, "html.parser")
        content_div = soup.find("div", {"id": "mw-content-text"})
        if not content_div:
            raise McpError(
                ErrorData(
                    code=INVALID_PARAMS,
                    message="Could not find the main content on the provided Wikipedia URL."
                )
            )

        # Convert to Markdown
        markdown_text = html2text(str(content_div))
        return markdown_text

    except ValueError as e:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e))) from e
    except RequestException as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Request error: {str(e)}")) from e
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Unexpected error: {str(e)}")) from e
```

#### `__init__.py`

```python
import argparse
from .server import mcp

def main():
    """MCP Wiki: Read Wikipedia articles and convert them to Markdown."""
    parser = argparse.ArgumentParser(
        description="Gives you the ability to read Wikipedia articles and convert them to Markdown."
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()
```

#### `__main__.py`

```python
from mcp_wiki import main

main()
```

---

### 第 3 步：定义项目配置

使用 `pyproject.toml` 配置你的项目。此配置定义了 CLI 脚本，以便 `mcp-wiki` 命令可作为二进制文件使用。以下是示例配置：

```toml
[project]
name = "mcp-wiki"
version = "0.1.0"
description = "MCP Server for Wikipedia"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "beautifulsoup4>=4.14.0",
    "html2text>=2025.4.15",
    "mcp[cli]>=1.25.0",
    "requests>=2.32.3",
]

[project.scripts]
mcp-wiki = "mcp_wiki:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

### 第 4 步：测试你的 MCP 服务器

验证你的 MCP 服务器在 MCP Inspector（一个基于浏览器的开发工具）或服务器 CLI 中是否正在运行。

<Tabs>
  <TabItem value="ui" label="在 MCP Inspector 中" default>
:::info
MCP Inspector 需要你的计算机上安装 Node.js 和 npm。
:::

1. 设置项目环境：

   ```bash
   uv sync
   ```

2. 激活你的虚拟环境：

   ```bash
   source .venv/bin/activate
   ```

3. 以开发模式运行你的服务器：

   ```bash
   mcp dev src/mcp_wiki/server.py
   ```

   MCP Inspector 应会自动在你的浏览器中打开。首次运行时，系统会提示你安装 `@modelcontextprotocol/inspector`。

4. 测试工具：
   1. 点击 `Connect` 初始化你的 MCP 服务器
   2. 在 `Tools` 选项卡上，点击 `List Tools`，然后点击 `read_wikipedia_article` 工具
   3. 在 URL 中输入 `https://en.wikipedia.org/wiki/Bangladesh`，然后点击 `Run Tool`

[![MCP Inspector UI](https://block.github.io/goose/assets/guides/custom-extension-mcp-inspector.png)](https://block.github.io/goose/assets/guides/custom-extension-mcp-inspector.png)

  </TabItem>
  <TabItem value="cli" label="在 CLI 中">
1. 设置项目环境：

```bash
uv sync
```

2. 激活你的虚拟环境：

   ```bash
   source .venv/bin/activate
   ```

3. 在本地安装你的项目：

   ```bash
   uv pip install .
   ```

4. 验证 CLI：

   ```bash
   mcp-wiki --help
   ```

   你应该会看到类似以下的输出：

   ```plaintext
   ❯ mcp-wiki --help
   usage: mcp-wiki [-h]

   Gives you the ability to read Wikipedia articles and convert them to Markdown.

   options:
     -h, --help  show this help message and exit
   ```

  </TabItem>
</Tabs>

---

### 第 5 步：与 goose 集成

要将你的 MCP 服务器作为扩展添加到 goose：

1. 构建扩展二进制文件：

   ```bash
   uv pip install .
   ```

2. 打开 goose Desktop，点击左上角的 <PanelLeft className="inline" size={16} /> 按钮以打开侧边栏
3. 在侧边栏中点击 `Extensions`
4. 将 `Type` 设置为 `STDIO`
5. 为你的扩展提供一个名称和描述
6. 在 `Command` 字段中，提供可执行文件的绝对路径：

   ```plaintext
   uv run /full/path/to/mcp-wiki/.venv/bin/mcp-wiki
   ```

   例如：

   ```plaintext
   uv run /Users/smohammed/Development/mcp/mcp-wiki/.venv/bin/mcp-wiki
   ```

:::tip 修改后重新构建二进制文件
要与 goose 集成后查看你对 MCP 服务器代码所做的任何更改，请重新运行 `uv pip install .`，然后重启 goose Desktop。
:::

出于本指南的目的，我们将运行本地版本。或者，你也可以将包发布到 PyPI。发布后，即可使用 `uvx` 直接运行服务器。例如：

```
uvx mcp-wiki
```

---

### 第 6 步：在 goose 中使用你的扩展

集成完成后，你就可以开始在 goose 中使用你的扩展了。打开 goose 聊天界面，按需调用你的工具。

你可以通过询问 goose「what tools do you have?」来验证 goose 是否已获取你自定义扩展中的工具。

![goose Chat - Ask about tools](https://block.github.io/goose/assets/guides/custom-extension-tools.png)

然后，你可以尝试提出需要使用你所添加扩展的问题。

![goose Chat - Use custom extension](https://block.github.io/goose/assets/guides/custom-extension-chat.png)

🎉 **恭喜！** 你已成功构建并将自定义 MCP 服务器与 goose 集成。

---

### MCP Apps：交互式扩展

**[MCP Apps](https://block.github.io/goose/docs/tutorials/building-mcp-apps)** 支持丰富的交互式用户界面，而不仅仅是纯文本响应。

**主要优势：**

- 从你的 MCP 服务器工具返回交互式 UI 组件
- 组件在 goose Desktop 中的隔离沙箱内安全渲染
- 实时用户交互会触发对你服务器的回调

**用例：** 交互式表单、数据可视化、预订界面、配置向导

**了解更多：** [构建 MCP Apps 教程](https://block.github.io/goose/docs/tutorials/building-mcp-apps)

[mcp-docs]: https://modelcontextprotocol.io/
[mcp-python]: https://github.com/modelcontextprotocol/python-sdk
[mcp-typescript]: https://github.com/modelcontextprotocol/typescript-sdk
[mcp-kotlin]: https://github.com/modelcontextprotocol/kotlin-sdk
[mcp-servers]: https://github.com/modelcontextprotocol/servers
[uv-docs]: https://docs.astral.sh/uv/getting-started/

---

## 构建 MCP 应用

> 原文：https://block.github.io/goose/docs/tutorials/building-mcp-apps

MCP Apps 让 MCP 服务器能够返回直接在 goose 聊天界面内渲染的交互式 UI，而不仅仅是文本响应。这允许用户通过交互表达意图，对于需要输入、迭代或视觉反馈的工作流非常有用。

:::warning 实验性
goose 中的 MCP Apps 支持是实验性的，基于一份草案规范。该实现非常基础，可能会发生变化，且尚不支持高级能力或持久化应用窗口。
:::

在本教程中，你将使用 JavaScript 和 Node.js 构建一个 MCP App。该应用包含一个交互式计数器，与宿主主题保持同步，并向聊天发送消息，展示用户意图如何从 UI 流向 agent。

:::info 前置条件
- 已安装 Node.js 18+
- 已安装 goose Desktop 1.19.1+
:::

---

### 第 1 步：初始化你的项目

创建一个新目录并初始化一个 Node.js 项目：

```bash
mkdir mcp-app-demo
cd mcp-app-demo
npm init -y
```

安装 MCP SDK：

```bash
npm install @modelcontextprotocol/sdk
```

通过添加 `"type": "module"` 更新你的 `package.json` 以使用 ES 模块：

```json5
{
  "name": "mcp-app-demo",
  "version": "1.0.0",
  // highlight-next-line
  "type": "module",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0"
  }
}
```

---

### 第 2 步：创建 MCP 服务器

创建 `server.js` - 这是加载并提供你的 HTML 的 MCP 服务器：

<details>
<summary>server.js</summary>

```javascript
#!/usr/bin/env node

import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// Load HTML from file
const __dirname = dirname(fileURLToPath(import.meta.url));
const APP_HTML = readFileSync(join(__dirname, "index.html"), "utf-8");

// Create the MCP server
const server = new Server(
  {
    name: "mcp-app-demo",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "show_demo_app",
        description: "Shows an interactive demo MCP App UI in the chat",
        inputSchema: {
          type: "object",
          properties: {},
          required: [],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name } = request.params;

  if (name === "show_demo_app") {
    return {
      content: [
        {
          type: "text",
          text: "The demo app is now displayed!",
        },
      ],
      // This metadata tells goose to render the MCP App
      _meta: {
        ui: {
          resourceUri: "ui://mcp-app-demo/main",
        },
      },
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

// List available resources
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: "ui://mcp-app-demo/main",
        name: "MCP App Demo",
        description: "An interactive demo",
        mimeType: "text/html;profile=mcp-app",
      },
    ],
  };
});

// Read resource content - returns the HTML
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  if (uri === "ui://mcp-app-demo/main") {
    return {
      contents: [
        {
          uri: "ui://mcp-app-demo/main",
          mimeType: "text/html;profile=mcp-app",
          text: APP_HTML,
          _meta: {
            ui: {
              csp: {
                connectDomains: [],
                resourceDomains: [],
                frameDomains: [],
                baseUriDomains: [],
              },
              prefersBorder: true,
            },
          },
        },
      ],
    };
  }

  throw new Error(`Resource not found: ${uri}`);
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP App Demo server running on stdio");
}

main().catch(console.error);
```

</details>

---

### 第 3 步：创建应用 HTML

创建 `index.html` - 这是你的交互式 UI：

<details>
<summary>index.html</summary>

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MCP App Demo</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      padding: 20px;
      min-height: 100vh;
      transition: background-color 0.3s, color 0.3s;
    }
    
    body.light { background: #f5f5f7; color: #1d1d1f; }
    body.dark { background: #1d1d1f; color: #f5f5f7; }
    
    .container {
      max-width: 500px;
      margin: 0 auto;
      padding: 24px;
      border-radius: 16px;
    }
    
    body.light .container { background: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    body.dark .container { background: #2d2d2f; box-shadow: 0 1px 3px rgba(0,0,0,0.3); }
    
    h1 { font-size: 24px; margin-bottom: 8px; }
    .subtitle { opacity: 0.7; margin-bottom: 20px; font-size: 14px; }
    
    .counter-section {
      text-align: center;
      padding: 24px;
      border-radius: 12px;
      margin-bottom: 20px;
    }
    
    body.light .counter-section { background: #f5f5f7; }
    body.dark .counter-section { background: #1d1d1f; }
    
    .counter-value { font-size: 64px; font-weight: bold; color: #0071e3; }
    .counter-label { font-size: 14px; opacity: 0.6; margin-top: 4px; }
    
    .button-row { display: flex; gap: 12px; justify-content: center; margin-top: 16px; }
    
    button {
      padding: 12px 24px;
      font-size: 18px;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
      color: white;
      transition: opacity 0.2s;
    }
    
    button:hover { opacity: 0.85; }
    button:active { opacity: 0.7; }
    
    .btn-increment { background: #0071e3; }
    .btn-decrement { background: #ff3b30; }
    .btn-reset { background: #86868b; }
    .btn-send { background: #34c759; }
    
    .message-section { margin-top: 20px; }
    .message-section h3 { font-size: 16px; margin-bottom: 12px; }
    .message-input { display: flex; gap: 8px; }
    
    input[type="text"] {
      flex: 1;
      padding: 12px 16px;
      border-radius: 8px;
      border: 2px solid transparent;
      font-size: 14px;
      transition: border-color 0.2s;
    }
    
    body.light input { background: #f5f5f7; color: #1d1d1f; }
    body.dark input { background: #1d1d1f; color: #f5f5f7; }
    input:focus { outline: none; border-color: #0071e3; }
    
    .status {
      margin-top: 16px;
      padding: 12px;
      border-radius: 8px;
      font-size: 13px;
      display: none;
    }
    
    .status.show { display: block; }
    .status.success { background: rgba(52, 199, 89, 0.15); color: #34c759; }
    .status.error { background: rgba(255, 59, 48, 0.15); color: #ff3b30; }
    
    .info-section {
      margin-top: 20px;
      padding: 16px;
      border-radius: 8px;
      font-size: 12px;
      opacity: 0.8;
    }
    
    body.light .info-section { background: #f5f5f7; }
    body.dark .info-section { background: #1d1d1f; }
    
    .info-section code {
      background: rgba(0, 113, 227, 0.1);
      padding: 2px 6px;
      border-radius: 4px;
      font-family: 'SF Mono', Monaco, monospace;
    }
  </style>
</head>
<body class="light">
  <div class="container">
    <h1>🎮 MCP App Demo</h1>
    <p class="subtitle">An interactive UI running inside goose</p>
    
    <div class="counter-section">
      <div class="counter-value" id="counter">0</div>
      <div class="counter-label">Counter Value</div>
      <div class="button-row">
        <button class="btn-decrement" onclick="updateCounter(-1)">−</button>
        <button class="btn-reset" onclick="resetCounter()">Reset</button>
        <button class="btn-increment" onclick="updateCounter(1)">+</button>
      </div>
    </div>
    
    <div class="message-section">
      <h3>💬 Send a message to goose</h3>
      <div class="message-input">
        <input type="text" id="messageInput" placeholder="Type a message..." />
        <button class="btn-send" onclick="sendMessage()">Send</button>
      </div>
      <div class="status" id="status"></div>
    </div>
    
    <div class="info-section">
      <strong>How this works:</strong><br><br>
      This UI is served as an MCP resource with the <code>ui://</code> scheme. 
      It communicates with goose via JSON-RPC messages through the sandbox bridge.
      <br><br>
      • Counter uses local state<br>
      • "Send" calls <code>ui/message</code> to append text to chat<br>
      • Theme syncs with goose's theme setting
    </div>
  </div>

  <script>
    class McpAppClient {
      constructor() {
        this.pendingRequests = new Map();
        this.requestId = 0;
        this.initialized = false;
        this.hostContext = null;
        
        window.addEventListener('message', (e) => this.handleMessage(e));
        this.initialize();
      }
      
      async initialize() {
        try {
          const result = await this.request('ui/initialize', {});
          this.hostContext = result.hostContext;
          this.initialized = true;
          
          if (this.hostContext?.theme) {
            this.applyTheme(this.hostContext.theme);
          }
          
          this.notify('ui/notifications/initialized', {});
          this.reportSize();
        } catch (error) {
          console.error('Failed to initialize MCP App:', error);
        }
      }
      
      handleMessage(event) {
        const data = event.data;
        if (!data || typeof data !== 'object') return;
        
        if ('id' in data && this.pendingRequests.has(data.id)) {
          const { resolve, reject } = this.pendingRequests.get(data.id);
          this.pendingRequests.delete(data.id);
          data.error ? reject(new Error(data.error.message)) : resolve(data.result);
          return;
        }
        
        if (data.method === 'ui/notifications/host-context-changed') {
          if (data.params?.theme) {
            this.applyTheme(data.params.theme);
          }
        }
      }
      
      request(method, params) {
        return new Promise((resolve, reject) => {
          const id = ++this.requestId;
          this.pendingRequests.set(id, { resolve, reject });
          window.parent.postMessage({ jsonrpc: '2.0', id, method, params }, '*');
          
          setTimeout(() => {
            if (this.pendingRequests.has(id)) {
              this.pendingRequests.delete(id);
              reject(new Error('Request timed out'));
            }
          }, 30000);
        });
      }
      
      notify(method, params) {
        window.parent.postMessage({ jsonrpc: '2.0', method, params }, '*');
      }
      
      applyTheme(theme) {
        document.body.className = theme;
      }
      
      reportSize() {
        this.notify('ui/notifications/size-changed', { height: document.body.scrollHeight });
      }
      
      async sendMessageToChat(text) {
        return this.request('ui/message', { content: { type: 'text', text } });
      }
    }
    
    const mcpApp = new McpAppClient();
    
    let counter = 0;
    
    function updateCounter(delta) {
      counter += delta;
      document.getElementById('counter').textContent = counter;
      mcpApp.reportSize();
    }
    
    function resetCounter() {
      counter = 0;
      document.getElementById('counter').textContent = counter;
      mcpApp.reportSize();
    }
    
    async function sendMessage() {
      const input = document.getElementById('messageInput');
      const message = input.value.trim();
      
      if (!message) {
        showStatus('Please enter a message', 'error');
        return;
      }
      
      try {
        await mcpApp.sendMessageToChat(message);
        showStatus('Message sent to chat!', 'success');
        input.value = '';
      } catch (error) {
        showStatus('Failed to send: ' + error.message, 'error');
      }
    }
    
    function showStatus(message, type) {
      const status = document.getElementById('status');
      status.textContent = message;
      status.className = 'status show ' + type;
      setTimeout(() => { status.className = 'status'; }, 3000);
    }
    
    document.getElementById('messageInput').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendMessage();
    });
  </script>
</body>
</html>
```

</details>

---

### 第 4 步：添加到 goose Desktop

1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮以打开侧边栏
2. 点击 `Extensions`
3. 点击 `Add custom extension`
4. 填写详细信息：
   - **Type**：`Standard IO`
   - **ID**：`mcp-app-demo`
   - **Name**：`MCP App Demo`
   - **Command**：`node /full/path/to/mcp-app-demo/server.js`
5. 点击 `Add`

有关更多选项，请参阅[添加扩展](https://block.github.io/goose/docs/getting-started/using-extensions#adding-extensions)。

---

### 第 5 步：测试你的应用

1. 重启 goose 以加载新扩展
2. 向 goose 提示：「Show me the demo app」
3. goose 将调用 `show_demo_app` 工具
4. 你的交互式应用将在聊天中渲染！

尝试：
- 点击计数器按钮
- 输入一条消息并点击「Send」
- 在浅色/深色模式之间切换 goose

---

### 工作原理

```
┌──────────────────────────────────────┐
│           Your MCP App               │  HTML/JS in sandboxed iframe
└──────────────────┬───────────────────┘
                   │ postMessage
┌──────────────────▼───────────────────┐
│          goose Desktop               │  Renders UI, routes messages
└──────────────────┬───────────────────┘
                   │ MCP Protocol
┌──────────────────▼───────────────────┐
│          Your MCP Server             │  Serves HTML via resources
└──────────────────────────────────────┘
```

你的服务器返回一个 `ui://` 资源 URI，goose 获取 HTML 并在 iframe 中渲染它。该应用通过 `postMessage` 进行回传通信——请求主题信息、向聊天发送消息或调整自身大小。

MCP Apps 在具有严格 Content Security Policy 限制的沙箱 iframe 中运行。

#### 内容安全策略配置

默认情况下，应用只能从自己的源加载资源。如果你的应用需要与外部域交互——例如从 CDN 加载资源、发起 API 调用或嵌入地图——你可以通过资源 `_meta.ui` 部分中的 `csp` 对象配置允许哪些域。

```javascript
_meta: {
  ui: {
    csp: {
      connectDomains: [],      // Domains for fetch/XHR requests
      resourceDomains: [],     // Domains for scripts, styles, images, fonts, media
      frameDomains: [],        // Origins allowed for nested iframes
      baseUriDomains: [],      // Additional allowed base URIs
    },
  },
}
```

| 选项 | CSP 指令 | 用途 | 默认值 |
|--------|---------------|---------|---------|
| `connectDomains` | `connect-src` | 你的应用可以发起网络请求的域 | 仅同源 |
| `resourceDomains` | `script-src`、`style-src`、`img-src`、`font-src`、`media-src` | 加载外部资源的域 | 仅同源 |
| `frameDomains` | `frame-src` | 允许用于嵌套 `<iframe>` 元素的源 | `'none'`（无 iframe） |
| `baseUriDomains` | `base-uri` | 允许用于 `<base>` 元素的额外域 | 仅 `'self'` |

<details>
<summary>示例</summary>

**嵌入地图：**

```javascript
csp: {
  frameDomains: ['https://www.openstreetmap.org'],
  resourceDomains: ['https://tile.openstreetmap.org'],
}
```

**从 CDN 加载资源：**

```javascript
csp: {
  resourceDomains: ['https://cdn.jsdelivr.net', 'https://unpkg.com'],
  connectDomains: ['https://api.example.com'],
}
```

</details>

:::warning 安全考量
只添加你信任的域。你添加的每个域都会扩展你的应用可以加载或嵌入的外部内容范围。保持列表最小化并具体化，以降低安全风险。
:::

#### 请求浏览器权限

MCP Apps 可以使用 Permission Policy 请求特定的浏览器权限。这对于需要访问摄像头、麦克风或位置服务等设备能力的应用非常有用。这些只是请求——宿主可能不会授予它们，应用应使用特性检测来处理权限不可用的情况。

要为你的 MCP App 声明权限，请在资源的 `_meta.ui` 部分中包含 `permissions` 对象：

```javascript
_meta: {
  ui: {
    permissions: {
      camera: true,           // Request camera access
      microphone: true,       // Request microphone access
      geolocation: true,      // Request geolocation access
      clipboardWrite: true,   // Request clipboard write access
    },
  },
}
```

| 权限 | Permission Policy 特性 | 用例 |
|------------|---------------------------|----------|
| `camera` | `camera` | 视频捕获、二维码扫描 |
| `microphone` | `microphone` | 音频录制、语音输入 |
| `geolocation` | `geolocation` | 位置感知应用、地图 |
| `clipboardWrite` | `clipboard-write` | 复制到剪贴板功能 |

所有权限默认均为 `false`。只请求你的应用实际需要的权限。

<details>
<summary>示例：视频录制应用</summary>

```javascript
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  if (uri === "ui://my-video-app/recorder") {
    return {
      contents: [
        {
          uri: "ui://my-video-app/recorder",
          mimeType: "text/html;profile=mcp-app",
          text: VIDEO_RECORDER_HTML,
          _meta: {
            ui: {
              permissions: {
                camera: true,
                microphone: true,
              },
            },
          },
        },
      ],
    };
  }
});
```

</details>

:::info 需要用户同意
即使 MCP App 请求了权限，浏览器在授予访问权之前仍会提示用户征求同意。用户可以随时拒绝权限请求。
:::

有关安全性和完整协议的详细信息，请参阅 [MCP Apps Specification](https://github.com/modelcontextprotocol/ext-apps)。

---

## 使用 Playwright CLI Skill 进行智能体测试

> 原文：https://block.github.io/goose/docs/tutorials/playwright-skill

<iframe
  class="aspect-ratio"
  src="https://www.youtube.com/embed/_MpbmD_unnU?si=dpHvuLVkbONN_0Hk"
  title="Agentic testing with Playwright CLI skill tutorial video"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
  referrerPolicy="strict-origin-when-cross-origin"
  allowFullScreen
></iframe>

借助 [Playwright CLI](https://github.com/microsoft/playwright-cli)，goose 可以浏览网站、点击按钮、填写表单，并将这些交互转化为 Playwright 测试，全部通过自然语言完成。与每次请求都向 LLM 发送完整页面结构的 Playwright MCP 不同，Playwright CLI 在本地存储无障碍树。这意味着更快的响应、更低的成本，以及大页面也不会出现问题。

### 为什么作为 Skill？

LLM 可能没有在 Playwright 的 CLI 上训练过，因此当要求 agent 使用它时，它可能会幻觉出命令和参数，导致错误和 token 浪费。[Playwright CLI Skill](https://github.com/microsoft/playwright-cli/blob/main/skills/playwright-cli/SKILL.md) 教会 goose 如何使用该 CLI 以及何时调用特定命令。

### 前置条件

- [Node.js](https://nodejs.org/) 18 或更高版本
- 全局安装 Playwright CLI：
  ```bash
  npm install -g @playwright/cli@latest
  ```
- （可选）如果你想运行生成的测试，需要安装 [Playwright](https://playwright.dev/)（`npm init playwright@latest`）

### 配置

#### 安装 Skill

1. 从命令行，在你的项目目录中安装 Playwright Skill：

```bash
npx skills add https://github.com/microsoft/playwright-cli --skill playwright-cli
```

2. 当被问及是否安装 skills 包时，输入 `y`

3. 当被问及安装到哪个 agent 时，选择 `goose`

4. 选择 `Global` 作用域以便在任何项目中都能使用该 Skill，或选择 `Local` 仅在当前工作目录内可用

5. 选择 `Symlink` 以获得一份你所有 agent 都能引用的副本

6. 你将收到安装确认，选择 `Yes` 继续

#### 启用 Summon 扩展
在 goose 中，启用 [Summon 扩展](https://block.github.io/goose/docs/mcp/summon-mcp)以在会话中加载 Agent Skills。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseBuiltinInstaller
    extensionName="Summon"
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
  |
  └  Extension settings updated successfully
  ```
  </TabItem>
</Tabs>


### 生成带视频和 Trace 的测试

给 goose 一个描述你想测试内容的提示词：

```
Using the Playwright CLI skill, open goose-docs.ai, click on the Docs menu, click on Context Engineering, 
then click on Using Skills and generate a test with video and traces
```

#### 工作原理

每个 `playwright-cli` 命令都会自动输出相应的 Playwright 代码。例如，这个命令：

```bash
playwright-cli click e11
```

执行以下 Playwright 代码：

```ts
await page.getByRole('link', { name: 'Docs' }).click();
```

#### goose 做了什么

1. 打开浏览器：`playwright-cli open goose-docs.ai`
2. 开始录制：`playwright-cli video-start` 和 `playwright-cli tracing-start`
3. 拍摄快照以查找元素：`playwright-cli snapshot`
4. 执行点击：`playwright-cli click <ref>`
5. 停止录制：`playwright-cli video-stop` 和 `playwright-cli tracing-stop`
6. 将生成的代码组装成一个测试文件

#### 生成的文件

| 文件 | 说明 |
|------|-------------|
| `tests/using-skills-navigation.spec.ts` | 你的 Playwright 测试 |
| `.playwright-cli/video-*.webm` | 会话的视频录制 |
| `.playwright-cli/traces/*.trace` | 用于调试的 Trace 文件 |

#### 生成的测试代码

生成的测试可能类似如下：

```typescript
import { test, expect } from '@playwright/test';

test('navigate to Using Skills guide via docs menu', async ({ page }) => {
  await page.goto('https://goose-docs.ai');
  await expect(page).toHaveTitle(/goose/);
  
  // Click on Docs in the navigation
  await page.getByRole('link', { name: 'Docs' }).click();
  
  // Expand Context Engineering category
  await page.getByRole('button', { name: 'Expand sidebar category \'Context Engineering\'' }).click();
  
  // Click on Using Skills
  await page.getByRole('link', { name: 'Using Skills' }).click();
  
  // Verify navigation
  await expect(page).toHaveURL(/using-skills/);
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Using Skills');
});
```

#### 运行测试

goose 甚至可以为你运行测试以确保它按预期工作。如果 Playwright 已经设置好，只需让它运行测试即可。如果没有，goose 可以为你安装 Playwright，然后运行测试。

### 查看视频

要查看发生了什么的视频，向 goose 提示：

```
Show me the video
```

goose 将使用 CLI 打开录制的视频，这样你就能确切看到会话期间发生了什么。

### 查看 Trace

要调试或回顾发生了什么，向 goose 提示：

```
Open the trace
```

Trace 查看器会显示：
- 所有操作的时间线
- 每个操作前后的截图
- 控制台日志和错误
- 网络请求
- 使用的元素定位器

### 多会话的可视化仪表盘

当你让 goose 同时运行多个浏览器任务时，可能很难跟踪正在发生的事情。可视化仪表盘为你提供所有活动浏览器会话的鸟瞰视图，让你实时观察进度，或在需要时介入并接管控制。

```
Show playwright dashboard
```

在这里你可以看到 goose 控制的每个浏览器的实时预览。点击进入任意会话以全尺寸观看，或者在 goose 需要帮助时自己接管鼠标和键盘。完成后按 `Escape`，goose 会从你离开的地方继续。

### 完整能力

想知道 Playwright Skill 还能做什么？问 goose：

```
What else can you do with the Playwright skill?
```

| 类别 | 能力 |
|----------|-------------|
| **浏览器控制** | open、goto、click、fill、close |
| **捕获与调试** | screenshot、snapshot、video、trace |
| **标签页管理** | 打开、切换、关闭标签页 |
| **存储与认证** | 保存/恢复 cookies、处理登录状态 |
| **网络** | 模拟 API、拦截请求 |
| **输入** | 输入文本、按键、鼠标操作 |

#### 示例用例

- ✅ 用自然语言测试 Web 应用
- ✅ 自动填写表单
- ✅ 从网站抓取数据
- ✅ 使用视频录制调试问题
- ✅ 测试认证流程
- ✅ 为文档录制演示
- ✅ 为隔离测试模拟 API

### 结论

上手 Playwright CLI agent Skill 很简单，并可直接通过自然语言提示词开启强大的浏览器自动化能力。无论你是生成测试、用视频和 Trace 调试，还是自动化复杂交互，Playwright CLI agent Skill 都提供了一种 token 高效的方式来借助 goose 发挥 Playwright 的全部威力。

### 资源

- [Summon 扩展文档](https://block.github.io/goose/docs/mcp/summon-mcp)
- [使用 Skills 指南](https://block.github.io/goose/docs/guides/context-engineering/using-skills) - 了解如何创建和使用 goose 的 skills
- [Playwright CLI GitHub](https://github.com/microsoft/playwright-cli)

---

## Spraay x402 扩展

> 原文：https://block.github.io/goose/docs/tutorials/spraay-mcp

本教程介绍如何将 [Spraay x402 MCP Server](https://github.com/plagtech/spraay-x402-mcp) 添加为 goose 扩展，用于在 Base 上进行批量加密货币支付、链上数据查询和 AI 模型访问。

借助 Spraay 扩展，goose 可以在**单笔交易中向最多 200 个接收者**发送 ETH 和 ERC-20 代币、查询实时代币价格、检查钱包余额、解析 ENS 名称、获取兑换报价，并与 200 多个 AI 模型聊天——所有这些都通过 [x402 协议](https://x402.org)按次付费。

### 支持的工具

Spraay x402 MCP Server 提供以下工具：

| 工具 | 成本 | 说明 |
|------|------|-------------|
| `spraay_chat` | $0.005 | 通过 200 多个模型（GPT-4、Claude、Llama、Gemini）进行 AI 聊天 |
| `spraay_models` | $0.001 | 列出可用的 AI 模型及其定价 |
| `spraay_batch_execute` | $0.01 | 向多个接收者批量支付 USDC |
| `spraay_batch_estimate` | $0.001 | 估算批量支付的 gas |
| `spraay_swap_quote` | $0.002 | Base 上 Uniswap V3 的兑换报价 |
| `spraay_tokens` | $0.001 | 列出 Base 上支持的代币 |
| `spraay_prices` | $0.002 | 实时链上代币价格（Uniswap V3） |
| `spraay_balances` | $0.002 | 任意地址的 ETH + ERC-20 余额 |
| `spraay_resolve` | $0.001 | 将 ENS 名称和 Basenames 解析为地址 |

:::info
AI agent 通过 x402 协议按请求支付 USDC。无需 API 密钥或账户——只需一个在 Base 上持有 USDC 的钱包。
:::

### 设置

#### 前置条件

- 已安装 Git 和 Node.js
- 一个在 Base 上持有 USDC 的钱包私钥（用于 x402 微支付）

#### 安装 MCP 服务器

```bash
git clone https://github.com/plagtech/spraay-x402-mcp.git
cd spraay-x402-mcp
npm install
npm run build
```

#### 配置

<Tabs>
<TabItem value="ui" label="goose Desktop">

1. 点击侧边栏中的 **Extensions** 图标
2. 点击 **Add custom extension**
3. 选择 **Command-line Extension**
4. 填写以下内容：
   - **Name**：`spraay`
   - **Command**：`node /absolute/path/to/spraay-x402-mcp/dist/index.js`
   - **Timeout**：`300`
5. 添加环境变量：
   - **Name**：`EVM_PRIVATE_KEY`
   - **Value**：你的钱包私钥（在 Base 上持有 USDC）

</TabItem>
<TabItem value="cli" label="goose CLI">

```
goose configure
```

选择 **Add Extension** → **Command-line Extension** 并配置：

```
┌   goose-configure
│
│   ◇  What would you like to call this extension?
│   spraay
│
│   ◇  What command should be run?
│   node /absolute/path/to/spraay-x402-mcp/dist/index.js
│
│   ◇  Please set the timeout for this tool (in secs):
│   300
│
│   ◇  Would you like to add environment variables?
│   Yes
│
│   ◇  Environment variable name:
│   EVM_PRIVATE_KEY
│
│   ◇  Environment variable value:
│   ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
│
│   └  Added spraay extension
```

</TabItem>
</Tabs>

### 使用示例

#### 查询代币价格

```
What's the current price of ETH on Base?
```

goose 将使用 `spraay_prices` 工具从 Uniswap V3 获取实时链上价格。

#### 查询钱包余额

```
Check the USDC balance of vitalik.eth
```

goose 将使用 `spraay_resolve` 解析 ENS 名称，然后使用 `spraay_balances` 获取余额。

#### 获取兑换报价

```
Get me a swap quote for 100 USDC to WETH on Base
```

goose 将使用 `spraay_swap_quote` 从 Uniswap V3 获取实时报价。

#### 批量发送 USDC

```
Send 10 USDC each to these wallets:
0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18
0x53d284357ec70cE289D6D64134DfAc8E511c8a3D
0xFBb1b73C4f0BDa4f67dcA266ce6Ef42f520fBB98
```

goose 将使用 `spraay_batch_execute` 在单笔交易中处理所有支付。

#### 与 AI 模型聊天

```
Using spraay, ask GPT-4 to explain what x402 is
```

goose 将使用 `spraay_chat` 从 200 多个可用的 AI 模型中查询。

### 工作原理

1. 你询问 goose → goose 调用 Spraay 工具（例如 `spraay_prices`）
2. MCP 服务器向 `gateway.spraay.app` 发送请求
3. 网关返回 HTTP 402 + 支付要求
4. x402 客户端自动在 Base 上签名 USDC 支付
5. 网关验证支付并返回数据

每次调用花费 $0.001–$0.01 的 USDC。无需 API 密钥，无需账户。

### 资源

- [Spraay App](https://spraay.app) — 多链批量支付（10 条链）
- [Spraay x402 Gateway](https://gateway.spraay.app) — AI agent 支付网关
- [GitHub](https://github.com/plagtech/spraay-x402-mcp) — MCP 服务器源代码
- [x402 协议](https://x402.org) — 支付标准
- [BaseScan 上的智能合约](https://basescan.org/address/0x1646452F98E36A3c9Cfc3eDD8868221E207B5eEC)

---

## 在 Docker 中运行 goose

> 原文：https://block.github.io/goose/docs/tutorials/goose-in-docker

本指南涵盖两种与 Docker 相关的场景：
1. **在 Docker 内运行 goose** - 在容器中构建并运行 goose 进程本身
2. **在 Docker 中运行扩展** - 在宿主机上运行 goose，但在容器内执行扩展

### 在 Docker 内运行 goose

你可以在 Docker 容器中从源文件构建 goose。这种方法不仅通过创建隔离环境提供安全优势，还增强了可移植性和一致性。例如，如果你需要在不常使用的平台（如 Ubuntu）上排查错误，可以使用 Docker 轻松调试。

首先，你需要修改 [`Dockerfile` 和 `docker-compose.yml` 文件](https://github.com/aaif-goose/goose/tree/main/documentation/docs/docker)以满足你的需求。你可能考虑的一些更改包括：

- **必需：** 在 `docker-compose.yml` 文件中将你的 API 密钥、provider 和 model 设置为环境变量，因为 keyring 设置在 Docker 中的 Ubuntu 上无法工作。此示例使用 Google Gemini。

- **可选：** 在 `Dockerfile` 中将基础镜像更改为其他 Linux 发行版。此示例使用 Ubuntu，但你可以切换到其他发行版，例如 CentOS、Fedora 或 Alpine。

- **可选：** 在 `docker-compose.yml` 文件中挂载你的个人 goose 设置和 hints 文件。这允许你在 Docker 容器内使用你的个人设置和 hints 文件。

:::tip 自动化替代方案
关于在容器中运行 goose 的自动化方法，请参阅 [Container-Use MCP 扩展](https://block.github.io/goose/docs/mcp/container-use-mcp)，它通过对话为你创建和管理容器。
:::

设置凭据后，你可以使用以下命令构建 Docker 镜像：

```bash
docker-compose -f documentation/docs/docker/docker-compose.yml build
```

接下来，使用以下命令运行容器并连接到它：

```bash
docker-compose -f documentation/docs/docker/docker-compose.yml run --rm goose-cli
```

在容器内，运行以下命令来配置 goose：

```bash
goose configure
```

当提示将 API 密钥保存到 keyring 时，选择 `No`，因为你已经将 API 密钥作为环境变量传递了。

再次配置 goose，这一次，你可以[添加任何你需要的扩展](https://block.github.io/goose/docs/getting-started/using-extensions)。

之后，你可以启动一个会话：

```bash
goose session
```

现在你应该能够连接到你已启用所配置扩展的 goose 了。

### 在 Docker 容器中运行扩展

`--container` 标志允许你在 Docker 容器内运行 goose 扩展。

#### 用法

```bash
goose session --container <container-id-or-name>
```

在 `config.yaml` 中配置的扩展将自动在指定容器内运行。使用 `docker ps` 查找你的容器 ID 或名称。

#### 要求

- 扩展必须存在于容器中，并且可通过你的扩展配置中使用的相同路径访问
- 要运行内置扩展，goose CLI 必须[安装](https://block.github.io/goose/docs/getting-started/installation)在容器内

#### 示例

```bash
# Start an interactive session with extensions from config.yaml
goose session --container my-dev-container

# Start a non-interactive session with instructions
goose run --container my-dev-container --text "your instructions here"

# Specify an extension to run in the container
goose session --container 4c76a1beed85 --with-extension "uvx mcp-server-fetch"

# Workaround: Use full path if container can't find the command
goose session --container 4c76a1beed85 --with-extension "/root/.local/bin/uvx mcp-server-fetch"
```

---

## 隔离开发环境

> 原文：https://block.github.io/goose/docs/tutorials/isolated-development-environments

本指南向你展示如何使用 **[Container Use MCP](https://github.com/dagger/container-use)** 与 goose 一起搭建隔离开发环境。通过这种设置，你的开发工作将同时隔离到 git 分支和容器中，让你可以自由实验而不影响你的主系统状态。
Container Use MCP 提供了强大的隔离开发方式，对 agent 非常友好（构建于 Docker、写时复制文件系统等工具之上）。

### 概述

**[Container Use MCP](https://github.com/dagger/container-use)** 服务器提供与 goose 无缝集成的容器化开发环境。这让你能够：

- 在隔离到 git 分支的更改上工作
- 在容器中运行代码而不影响你的本地机器
- 在需要时轻松重置并重新开始
- 在不同项目和实验之间保持清晰的隔离
- 并行处理多项事务

:::info 已经在使用 Devcontainers？
如果你在 Docker 容器内开发（例如 VS Code Remote-Containers），请参阅如何[在你现有的容器中运行扩展](https://block.github.io/goose/docs/tutorials/goose-in-docker#running-extensions-in-docker-containers)。
:::

### 前置条件

- 在你的系统上安装并运行 Docker（[Podman](https://docs.dagger.io/ci/integrations/podman)、[NerdCtl](https://docs.dagger.io/ci/integrations/nerdctl/) 或 [Container](https://docs.dagger.io/ci/integrations/apple-container/)）
- 安装并配置 Git
- 安装并配置 goose

### 设置

有关安装和配置说明，请参阅 [Container Use 扩展](https://block.github.io/goose/docs/mcp/container-use-mcp)教程。

### 用法

在 goose 中启用该扩展后，你可以：

#### 开始隔离开发

只需在与 goose 的对话中提到你想在隔离环境中工作：

```
"I want to experiment with adding a new feature, but I want to do it in an isolated environment so I don't affect my main codebase."
```

goose 将自动：
1. 为你的工作创建一个新的 git 分支
2. 搭建一个容器化环境
3. 确保所有更改都与你的宿主系统隔离

#### 处理实验

```
"Let me try a completely different approach to this algorithm. Can you set up an isolated environment where I can experiment?"
```

#### 学习新技术

```
"I want to try out this new framework, but I don't want to install all its dependencies on my main system."
```

### 优势

- **安全**：实验时无需担心破坏你的主开发环境
- **可复现性**：在不同机器和团队成员之间保持一致的环境
- **隔离**：多个项目可以同时运行而不冲突
- **易于清理**：完成后删除容器和分支
- **版本控制**：所有更改都跟踪在隔离的 git 分支中
- **回滚能力**：轻松丢弃失败的实验

### 常见工作流

#### 功能开发

1. 与 goose 开始一段关于新功能的对话
2. 请求隔离开发环境
3. goose 创建分支和容器
4. 开发和测试该功能
5. 如果成功，合并分支；如果不成功，丢弃它

#### 依赖探索

1. 让 goose 探索一个新的库或工具
2. 在带有该依赖的隔离容器中工作
3. 测试兼容性和功能
4. 决定是否集成到主项目

#### 重构

1. 为大规模重构请求隔离环境
2. 在容器和分支的安全环境中进行更改
3. 在合并前彻底测试
4. 如果出现问题可轻松回滚

### 故障排除

#### 常见问题

**Docker 未运行：**
- 确保 Docker Desktop 已安装并正在运行
- 检查 Docker 守护进程状态：`docker info`

**权限问题：**
- 确保你的用户有运行 Docker 命令的权限
- 在 Linux 上，将用户添加到 docker 组：`sudo usermod -aG docker $USER`

**Git 问题：**
- 确保 Git 已正确配置用户名和邮箱
- 检查你在开始隔离工作时是否位于 Git 仓库中

#### 获取帮助

如果你遇到问题：

1. 查看 **[Container Use GitHub 仓库](https://github.com/dagger/container-use)** 的文档
2. 验证所有前置条件已安装并正常工作
3. 加入我们的 [Discord 社区](https://discord.gg/n8R5VaWDAn)寻求支持

### 下一步

在 goose 中启用 container-use 后，你就可以自信地开发了。试着开启一段关于你一直犹豫要不要实验的项目的对话，让 goose 为你的探索搭建一个安全、隔离的环境。

记住：有了隔离环境，就不存在失败的实验——只有不影响你主代码库的学习机会。

---

## CI/CD 环境

> 原文：https://block.github.io/goose/docs/tutorials/cicd

goose 不仅在本地机器上有用，它还可以简化 CI/CD 环境中的任务。通过将 goose 集成到你的流水线中，你可以自动化诸如以下的任务：

- 代码审查
- 文档检查
- 构建和部署工作流
- 基础设施和环境管理
- 回滚和恢复流程
- 智能测试执行

本指南将引导你在 CI/CD 流水线中设置 goose，重点介绍使用 GitHub Actions 进行代码审查。

### 在 GitHub Actions 中使用 goose
你可以直接在 GitHub Actions 中运行 goose。按照以下步骤设置你的工作流。

:::info TLDR
<details>
   <summary>复制 GitHub Workflow</summary>
   
   ```yaml title="goose.yml"


name: goose

on:
   pull_request:
      types: [opened, synchronize, reopened, labeled]

permissions:
   contents: write
   pull-requests: write
   issues: write

env:
   PROVIDER_API_KEY: ${{ secrets.REPLACE_WITH_PROVIDER_API_KEY }}
   PR_NUMBER: ${{ github.event.pull_request.number }}
   GH_TOKEN: ${{ github.token }}

jobs:
   goose-comment:
      name: goose Comment
      runs-on: ubuntu-latest
      steps:
         - name: Check out repository
           uses: actions/checkout@v4
           with:
              fetch-depth: 0

         - name: Gather PR information
           run: |
              {
              echo "# Files Changed"
              gh pr view $PR_NUMBER --json files \
                 -q '.files[] | "* " + .path + " (" + (.additions|tostring) + " additions, " + (.deletions|tostring) + " deletions)"'
              echo ""
              echo "# Changes Summary"
              gh pr diff $PR_NUMBER
              } > changes.txt

         - name: Install goose CLI
           run: |
              mkdir -p /home/runner/.local/bin
              curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh \
                | GOOSE_VERSION=REPLACE_WITH_VERSION CONFIGURE=false GOOSE_BIN_DIR=/home/runner/.local/bin bash
              echo "/home/runner/.local/bin" >> $GITHUB_PATH

         - name: Configure goose
           run: |
              mkdir -p ~/.config/goose
              cat <<EOF > ~/.config/goose/config.yaml
              GOOSE_PROVIDER: REPLACE_WITH_PROVIDER
              GOOSE_MODEL: REPLACE_WITH_MODEL
              keyring: false
              EOF

         - name: Create instructions for goose
           run: |
              cat <<EOF > instructions.txt
              Create a summary of the changes provided. Don't provide any session or logging details.
              The summary for each file should be brief and structured as:
              <filename/path (wrapped in backticks)>
                 - dot points of changes
              You don't need any extensions, don't mention extensions at all.
              The changes to summarise are:
              $(cat changes.txt)
              EOF

         - name: Test
           run: cat instructions.txt

         - name: Run goose and filter output
           run: |
              goose run --instructions instructions.txt | \
              # Remove ANSI color codes
              sed -E 's/\x1B\[[0-9;]*[mK]//g' | \
              # Remove session/logging lines
              grep -v "logging to /home/runner/.config/goose/sessions/" | \
              grep -v "^starting session" | \
              grep -v "^Closing session" | \
              # Trim trailing whitespace
              sed 's/[[:space:]]*$//' \
              > pr_comment.txt

         - name: Post comment to PR
           run: |
              cat -A pr_comment.txt
              gh pr comment $PR_NUMBER --body-file pr_comment.txt

   ```
</details>

:::

#### 1. 创建工作流文件

在你的仓库中创建一个新文件 `.github/workflows/goose.yml`。它将包含你的 GitHub Actions 工作流。

#### 2. 定义工作流触发器和权限

配置该 action，使其：

- 在拉取请求被打开、更新、重新打开或标记时触发工作流
- 授予 goose 与仓库交互所需的权限
- 为你选择的 LLM provider 配置环境变量

```yaml
name: goose

on:
    pull_request:
        types: [opened, synchronize, reopened, labeled]

permissions:
    contents: write
    pull-requests: write
    issues: write

env:
   PROVIDER_API_KEY: ${{ secrets.REPLACE_WITH_PROVIDER_API_KEY }}
   PR_NUMBER: ${{ github.event.pull_request.number }}
```


#### 3. 安装并配置 goose

要在你的工作流中安装并设置 goose，请添加以下步骤：

```yaml
steps:
    - name: Install goose CLI
      run: |
          mkdir -p /home/runner/.local/bin
          curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh \
            | GOOSE_VERSION=REPLACE_WITH_VERSION CONFIGURE=false GOOSE_BIN_DIR=/home/runner/.local/bin bash
          echo "/home/runner/.local/bin" >> $GITHUB_PATH

    - name: Configure goose
      run: |
          mkdir -p ~/.config/goose
          cat <<EOF > ~/.config/goose/config.yaml
          GOOSE_PROVIDER: REPLACE_WITH_PROVIDER
          GOOSE_MODEL: REPLACE_WITH_MODEL
          keyring: false
          EOF
```

##### 在 CI/CD 中固定 goose 版本

在 CI/CD 中，我们建议使用 `GOOSE_VERSION` 固定特定的 goose 版本，以实现可复现的运行。这还能避免在下载 goose CLI 二进制资产时，如果 `stable` 发布标签不包含它们而出现 404 错误。

CI 相关的安装器选项：
- `GOOSE_VERSION`：将安装固定到的版本（同时支持 `1.21.1` 和 `v1.21.1` 两种格式）
- `GOOSE_BIN_DIR`：安装目录（确保该目录在 `PATH` 上）
- `CONFIGURE=false`：跳过交互式 `goose configure` 流程

:::info 替换项
将 `REPLACE_WITH_VERSION`、`REPLACE_WITH_PROVIDER` 和 `REPLACE_WITH_MODEL` 替换为你想要固定的 goose 版本以及你的 LLM provider/model 名称。添加任何其他必要的配置。
:::

#### 4. 收集 PR 更改并准备指令

此步骤提取拉取请求详情并将其格式化为 goose 的结构化指令。

```yaml
    - name: Create instructions for goose
      run: |
          cat <<EOF > instructions.txt
          Create a summary of the changes provided. Don't provide any session or logging details.
          The summary for each file should be brief and structured as:
            <filename/path (wrapped in backticks)>
              - dot points of changes
          You don't need any extensions, don't mention extensions at all.
          The changes to summarise are:
          $(cat changes.txt)
          EOF
```

#### 5. 运行 goose 并清理输出

现在，使用格式化后的指令运行 goose，并通过移除 ANSI 颜色代码和不必要的日志消息来清理输出。

```yaml
    - name: Run goose and filter output
      run: |
          goose run --instructions instructions.txt | \
            # Remove ANSI color codes
            sed -E 's/\x1B\[[0-9;]*[mK]//g' | \
            # Remove session/logging lines
            grep -v "logging to /home/runner/.config/goose/sessions/" | \
            grep -v "^starting session" | \
            grep -v "^Closing session" | \
            # Trim trailing whitespace
            sed 's/[[:space:]]*$//' \
            > pr_comment.txt
```

#### 6. 将评论发布到 PR

最后，将 goose 的输出作为评论发布到拉取请求上：

```yaml
    - name: Post comment to PR
      run: |
          cat -A pr_comment.txt
          gh pr comment $PR_NUMBER --body-file pr_comment.txt
```

通过这个工作流，goose 将在拉取请求上运行，分析更改，并将摘要作为评论发布到 PR 上。

这只是可能性中的一个示例。你可以自由修改你的 GitHub Action 以满足你的需求。

---

### 并行运行多个 goose 实例

goose 支持运行多个具有隔离状态的并发会话，这使得在你的 CI/CD 流水线中安全地运行并行作业成为可能。每个 goose 实例都维护自己的对话历史、agent 上下文和扩展配置，互不干扰。

这支持诸如跨不同环境的矩阵构建或同时处理多个组件等用例。

---

### 安全考量

在 CI/CD 环境中运行 goose 时，请牢记以下安全实践：

1. **密钥管理**
      - 将你的敏感凭据（如 API 密钥）存储为 GitHub Secrets。
      - 永远不要在日志或 PR 评论中暴露这些凭据。

2. **最小权限原则**
      - 在你的工作流中只授予必要的权限，并定期审计它们。

3. **输入验证**
      - 确保传递给 goose 的任何输入都经过清理和验证，以防止意外行为。

---

## 使用无头模式自动化

> 原文：https://block.github.io/goose/docs/tutorials/headless-goose

*在 CI/CD 流水线、服务器和批处理场景中运行 AI 驱动的工程工作流*

无需人工干预即可自动化复杂工程任务的能力已经非常强大，但让我们用 AI 将它提升到下一个层次。goose 的「无头」模式使开发者能够在服务器环境、CI/CD 流水线和批处理场景中充分发挥 AI 自动化的全部威力，而在这些场景中交互式会话根本不可行。

### 什么是无头模式？

无头模式是 goose 的非交互式执行环境，专为无法（或不希望）人工干预的自动化场景而设计。

与交互式桌面应用或 CLI 会话不同，无头模式处理指令并自动退出，非常适合集成到现有的开发工作流中。

可以把它想象成与 AI 助手进行对话，与带着明确指令派它去执行一项支线任务并信任它自主完成任务之间的区别。

### 交互式 vs. 无头：理解差异

| 特性 | 交互模式 | 无头模式 |
|---------|------------------|---------------|
| **用户输入** | 提示用户做出决定和澄清 | 使用默认行为和预配置的设置 |
| **上下文管理** | 达到限制时提示用户选择策略 | 自动总结对话 |
| **会话持久性** | 维护持续的对话状态 | 执行任务并干净退出 |
| **错误处理** | 用户可以介入并提供指导 | 基于配置的自动化错误响应 |
| **工具权限** | 可以提示批准高风险操作 | 使用配置的默认值或安全失败 |
| **执行流程** | 来回对话风格 | 单次执行并输出完整结果 |

### 带命令示例的真实用例

#### 1. 服务器环境和云部署

非常适合无头服务器、容器化环境和无法使用 GUI 的云部署。

```bash
# Automated server maintenance
goose run --with-builtin developer -t "Check system logs for errors in the last 24 hours, identify performance bottlenecks, and generate a maintenance report"

# Container optimization
goose run --no-session -t "Analyze the Dockerfile, optimize for smaller image size, and update the build process documentation"

# Cloud resource audit
goose run -t "Review our AWS infrastructure configuration, identify cost optimization opportunities, and create a migration plan for underutilized resources"
```

#### 2. CI/CD 流水线集成

将 AI 驱动的分析和修复无缝集成到你的持续集成工作流中。

```bash
# In your .github/workflows/ci.yml
- name: AI-Powered Code Review
  run: |
    goose run --with-builtin developer \
      -t "Analyze the code changes in this PR, check for security vulnerabilities, performance issues, and suggest improvements. Generate a detailed review report."

# Test failure analysis
goose run --debug -t "Examine the failing test suite, identify the root cause of failures, implement fixes, and ensure all tests pass"

# Automated documentation updates
goose run -t "Review code changes and update the README.md and API documentation to reflect new features and modifications"
```

#### 3. 批处理和批量操作

处理跨多个文件、仓库或系统的大规模操作。

```bash
# Bulk code modernization
goose run --with-builtin developer \
  -t "Upgrade all Python files in the src/ directory from Python 3.8 to 3.11 syntax, update dependencies, and ensure compatibility"

# Multi-repository maintenance
for repo in repo1 repo2 repo3; do
  cd $repo
  goose run --no-session -t "Update all dependencies to latest stable versions, run tests, and create a PR if changes are needed"
  cd ..
done

# Database migration automation
goose run -t "Analyze the current database schema, generate migration scripts for the new requirements, and create rollback procedures"
```

#### 4. 计划任务执行

与 cron 作业或任务调度器结合，实现定期自动化维护。

```bash
# Daily security scan (add to crontab)
0 2 * * * /usr/local/bin/goose run --no-session -t "Run comprehensive security audit, check for vulnerabilities, and email report to security team"

# Weekly dependency updates
0 9 * * 1 /usr/local/bin/goose run -t "Check for outdated dependencies, create update PRs for non-breaking changes, and schedule review for major updates"
```

### 无头模式成功的最佳实践

那么我们如何设置这一切呢？

让我们谈谈成功的无头自动化的基础：

#### 1. **编写清晰明了的指令**

你的指令是成功工具使用的蓝图。你的提示词想法需要具体、详细且明确。如果有疑问，可以尝试一些[氛围提示词来帮助你入门](https://www.youtube.com/watch?v=IjXmT0W4f2Q)。

```bash
# Good: Specific and actionable
goose run -t "Analyze the test failures in the latest CI run, identify the root cause, and create a fix with appropriate unit tests"

# Better: Even more detailed
goose run -t "Review the failed tests in tests/integration/, identify why the authentication middleware is failing, implement a fix that maintains backward compatibility, and add regression tests"
```

#### 2. **预配置你的环境**
设置你的环境变量，以避免一些重复的运行时决策。

```bash
export GOOSE_CONTEXT_STRATEGY=summarize
export GOOSE_MAX_TURNS=50
export GOOSE_MODE=auto
export GOOSE_DISABLE_SESSION_NAMING=true
```

`CONTEXT_STRATEGY` 和 `MAX_TURNS` 设置有助于管理对话限制，而 `GOOSE_MODE` 设置为 `auto` 则允许非交互式执行。`GOOSE_DISABLE_SESSION_NAMING` 避免了用于生成会话名称的额外后台模型调用，并保留默认的「CLI Session」名称。

#### 3. **实现健壮的错误处理**

始终检查退出码，并在自动化脚本中优雅地处理失败：

```bash
#!/bin/bash
if ! goose run --no-session -t "Run security audit and fix critical issues"; then
    echo "goose automation failed - manual intervention required"
    exit 1
fi
```

#### 4. **选择合适的会话策略**
对于一次性任务使用 `--no-session`，以避免弄乱你的会话历史，但对于可能需要稍后调试（或首次尝试时）的复杂、多步骤工作流，则应保留会话。


### 无头模式下的 Recipe 执行

[Recipe](https://block.github.io/goose/docs/guides/recipes/) 是 goose 定义可复用、参数化工作流的强大方式。在无头模式下，Recipe 变得更有价值，因为它们支持复杂的自动化场景。

#### 无头模式下的 Recipe 要求

要让 Recipe 在无头模式下工作，它**必须**包含一个 `prompt` 字段。此提示词作为启动自动化执行的初始指令：

```yaml
# automation-recipe.yaml
title: "Automated Code Quality Check"
name: "Automated Code Quality Check"
description: "Comprehensive code quality analysis and improvement"
author:
  name: "DevOps Team"
  email: "devops@company.com"

# Required for headless mode
prompt: "Perform a comprehensive code quality analysis including linting, security scanning, test coverage analysis, and generate an improvement plan"

instructions: |
  You are an expert code quality engineer. Your task is to:
  1. Run static analysis tools (eslint, pylint, etc.)
  2. Perform security vulnerability scanning
  3. Analyze test coverage and identify gaps
  4. Check for code duplication and complexity issues
  5. Generate a prioritized improvement plan
  6. Create actionable tickets for the development team

parameters:
  - key: target_directory
    input_type: string
    requirement: required
    description: "Directory to analyze"
    default: "./src"
  - key: output_format
    input_type: string
    requirement: required
    description: "Report format (markdown, json, html)"
    default: "markdown"

extensions:
  - type: builtin
    name: developer
    display_name: Developer
    timeout: 300
    bundled: true
```

#### 在无头模式下执行 Recipe

```bash
# Basic recipe execution
goose run --recipe automation-recipe.yaml

# With custom parameters
goose run --recipe automation-recipe.yaml \
  --params target_directory=./backend \
  --params output_format=json

# Complex workflow with multiple recipes
goose run --recipe main-workflow.yaml \
  --sub-recipe security-audit.yaml \
  --sub-recipe performance-analysis.yaml \
  --params environment=production
```

### 理解局限性

虽然无头模式非常强大，但理解它的约束很重要，这样你才能为你的自动化想法设定适当的期望。

#### 1. 无用户交互能力

**这意味着什么**：goose 在执行期间无法请求澄清、批准或额外输入。如果它不确定该做什么，提示词结果通常会向你展示一个类似「How should I proceed?」的问题。

**影响**：如果指令含糊不清或出现意外情况，goose 将基于可用上下文做出最佳判断，这可能并不总是符合你的意图。

**缓解措施**：提供极其详细的指令，尤其是在遇到问题时该怎么做，并首先在**非生产**环境中彻底测试你的自动化。

```bash
# Problematic: Too vague
goose run -t "Fix the issues"

# Better: Specific and actionable
goose run -t "Fix the TypeScript compilation errors in src/components/, ensure all imports are correct, and update any deprecated API calls to use the latest syntax"
```

#### 2. Recipe 提示词要求

**这意味着什么**：无头模式中使用的任何 Recipe 都必须包含一个 `prompt` 字段，否则执行将失败并报错。

**影响**：现有的交互式 Recipe 可能需要修改才能在自动化场景中使用。

**缓解措施**：始终在你的 Recipe 中包含有意义的提示词，即使它们主要是为交互式使用而设计的。

#### 3. 工具权限依赖

**这意味着什么**：goose 无法提示获取使用潜在高风险工具或操作的权限。

**影响**：需要批准的操作将使用默认权限或失败，可能阻塞自动化工作流。

**缓解措施**：使用环境变量预配置工具权限：

```bash
export GOOSE_MODE=auto  # Automatically approve safe operations
# or configure specific tool permissions in your config
```

#### 4. 上下文决策自动化

**这意味着什么**：当达到对话上下文限制时，goose 会在没有用户输入的情况下自动应用配置的策略。

**影响**：如果总结不完美，重要上下文可能会丢失，或者如果上下文清除过于激进，执行可能会被中断。

**缓解措施**：配置适当的上下文策略并监控 token 使用情况：

```bash
export GOOSE_CONTEXT_STRATEGY=summarize  # Usually the best choice for automation
export GOOSE_MAX_TURNS=100  # Prevent runaway execution
```

#### 5. 错误恢复局限性

**这意味着什么**：本可从人类洞察中受益的复杂错误场景无法以交互方式解决。

**影响**：自动化可能在人通过对话就能轻松解决的边缘情况下失败。

**缓解措施**：在你的调用脚本中实现全面的错误处理，并准备后备流程：

```bash
#!/bin/bash
if ! goose run --recipe complex-deployment.yaml; then
    # Fallback to simpler approach or alert human operators
    echo "Complex deployment failed, initiating rollback procedure"
    goose run --recipe rollback.yaml
fi
```

### 配置和环境设置

#### 必要的环境变量

```bash
# Context management
export GOOSE_CONTEXT_STRATEGY=summarize
export GOOSE_MAX_TURNS=50

# Tool behavior
export GOOSE_MODE=auto

# Model configuration
export GOOSE_PROVIDER=openai
export GOOSE_MODEL=gpt-4o

# Output control
export GOOSE_CLI_MIN_PRIORITY=0.2  # Reduce verbose output
```

#### 高级配置

```bash
# Security and permissions
export GOOSE_ALLOWLIST=https://company.com/allowed-extensions.json
```

### 自动化开发的未来

goose 的无头模式不仅仅是一个功能——它是向由 AI 驱动的真正自动化开发工作流的一次转变。我们可以消除日常任务中的人工干预，让团队专注于高价值的工作，而由 AI 处理那些拖慢我们的重复性、耗时的操作。

无论你是想简化 CI/CD 流水线、自动化服务器维护，还是处理跨多个仓库的批量操作，goose 的无头模式都为构建复杂、可靠的自动化工作流提供了基础。

**今天就开始你的自动化之旅：**

1. **安装 goose** 并配置你的环境变量
2. **创建你的第一个 Recipe**，包含清晰的提示词和详细的指令
3. **在安全环境中测试**，然后再部署到生产环境
4. **与你现有的工作流集成**，看着你的生产力飙升

在我们的 [Discord 社区](https://discord.gg/n8R5VaWDAn)与我们联系，分享你的无头模式成功故事、提出问题，并与其他想要突破 AI 自动化边界的开发者合作。
