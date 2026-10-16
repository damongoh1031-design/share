# goose 官方文档中文手册：第 29 章　博客（七）：2026-03 ~ 2026-09

## WebMCP 入门

> 原文：https://block.github.io/goose/blog/2026-03-17-webmcp-for-beginners

![博客封面](https://block.github.io/goose/img/blog/webmcp-for-beginners.png)

如果你也曾以为 WebMCP 只是一个 MCP 服务器，请举手。我认罪，我也这么以为过。事实是，它是一个 W3C 标准，使用了与 MCP 相似的概念。下面说说它究竟是什么。

<!--truncate-->

### 什么是 WebMCP？

WebMCP 是一种让网站定义 AI Agent 可以直接调用的动作的方式。

通常，当 Agent 与网站交互时，它必须去解读界面。它查看页面，试图找到输入项，点击按钮，并祈祷自己正在与正确的元素交互。这个过程能奏效，但它是间接的，而且往往很脆弱。

有了 WebMCP，网站就去掉了这层猜测。网站不再迫使 Agent 去弄清楚 UI，而是暴露代表其所支持动作的函数。

于是，Agent 不再模拟「在输入框里打字然后点击按钮」这样的用户流程，而是可以直接调用类似这样的东西：

```javascript
set_background_color({ color: "coral" })
```

在这个例子中，Agent 并不试图理解页面的布局，也不一步步地浏览它。它调用的是网站明确定义的函数，这让交互更直接、更可靠。

### WebMCP 不是 MCP

这是最关键的部分。MCP 和 WebMCP 解决的是类似的问题，但它们在完全不同的地方解决。

使用 MCP 时，你运行一个暴露工具的服务器。你的 Agent 连接到那个服务器并调用那些工具。你需要负责构建它、托管它、处理身份验证，并长期维护它。而使用 WebMCP 时，一切都在浏览器中发生。网站自身定义工具，Agent 通过访问页面来发现它们。这种交互不需要单独部署服务器。

另一种理解方式是：MCP 是你在想要访问的系统周围构建的东西，而 WebMCP 是网站构建进自身内部的东西。

### WebMCP 为什么存在

当你看看人们在规模化使用 MCP 时遇到的局限，WebMCP 背后的理由就更容易理解了。当团队尝试构建大型 MCP 服务器时，他们常常最终拥有太多工具，以至于模型无法有效地推理。除此之外，身份验证也变得复杂，因为每个服务都有自己的要求，而把这一切都集中在一处管理很困难。

浏览器其实已经解决了其中很多问题。当你登录一个网站时，你的会话、cookie 和身份验证状态都已经就位。这套系统已经存在多年，并且可靠地运行着。WebMCP 建立在这个想法之上：让网站在那个已认证的上下文中暴露自己的动作，而不是要求一个单独的服务器来管理一切。

### WebMCP 不是 Playwright MCP Server

我直播了自己第一次探索 WebMCP 的过程，收到的一个常见问题是：「它和 Chrome DevTools MCP server 或 Playwright MCP Server 是同一个东西吗？」它们不是同一个东西。

这些 MCP 服务器启用的是浏览器自动化。浏览器自动化允许 Agent 通过与界面交互来控制浏览器。Agent 可以截图、读取 DOM、点击元素、在输入框中打字，以及浏览页面。这在任何网站上都能用，但 Agent 必须解读它所看到的内容，并决定如何行动。

WebMCP 采取了不同的方法。它只在实现了它的网站上有效，但当网站实现了它时，Agent 根本不需要解读 UI。网站提供结构化的动作，Agent 直接调用它们。

在实践中，这种差异改变了交互模型。使用浏览器自动化时，Agent 遵循一系列步骤，近似一个用户会做的事情。使用 WebMCP 时，Agent 跳过这个过程，直接调用底层的动作。

如果你在使用 goose，Chrome DevTools MCP 仍然有用，因为它把 goose 连接到浏览器。它充当桥梁。而 Agent 与网站交互方式的改进，来自 WebMCP 本身。

### WebMCP 实践

为了让它更具体，想想从餐厅网站点餐。没有 WebMCP 时，你需要构建某种能理解那个网站如何运作的东西。这包括梳理点餐流程、处理登录、解析菜单，以及提交订单。每当网站发生变化，你还需要维护那套逻辑。如果你想支持多家餐厅，你得为每一家重复这个过程。

有了 WebMCP，餐厅定义一个像 `place_order` 这样的工具。网站已经知道自己的菜单结构、修改选项和结账流程。它也已经处理了身份验证。Agent 不必在外部重建这一切，只需调用网站提供的工具即可。

### 为什么这很重要

这种方式之所以突出，有几个原因。网站对自身结构和逻辑的理解，比任何外部系统都好。WebMCP 让它们可以一次性把这些知识编码进去，并让任何 Agent 都能使用。身份验证已经在浏览器内处理好了，这消除了 MCP 服务器否则需要管理的大量复杂性。维护工作也转移到了正确的地方。当网站发生变化时，拥有它的人会更新他们的工具。你不再需要为你无法控制的系统维护集成。

### 构建一个 WebMCP 网站

为了更好地理解这一点，我构建了一个简单的取色器演示，它只暴露一个动作：改变页面的背景颜色。

它的结构是这样的：

```plaintext
my-webmcp-site/
├── index.html
├── style.css
└── webmcp.js
```

HTML 是一个基础页面：

```html
<!DOCTYPE html>
<html>
<head>
  <title>WebMCP Color Picker</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="container">
    <h1>🎨 Color Picker</h1>
    <p>Ask an AI to change my background!</p>
    <p>Current color: <span id="colorName">#6366f1</span></p>
  </div>
  <script src="webmcp.js"></script>
</body>
</html>
```

WebMCP 功能来自注册一个工具：

```javascript
if (window.navigator.modelContext) {
  window.navigator.modelContext.registerTool({
    name: "set_background_color",
    description: "Change the background color of the page",
    inputSchema: {
      type: "object",
      properties: {
        color: { type: "string" }
      },
      required: ["color"]
    },
    execute: ({ color }) => {
      document.body.style.backgroundColor = color;
      document.getElementById("colorName").textContent = color;

      return {
        content: [{
          type: "text",
          text: `Background color changed to ${color}`
        }]
      };
    }
  });
}
```

一旦注册完成，Agent 在访问页面时就能发现并调用这个工具。有一个细节让我印象深刻，那就是描述有多重要。模型用这段描述来决定何时调用工具以及提供什么输入，所以写得具体会带来不同。

### 定义工具的两种方式

你可以用 JavaScript 定义工具，这对动态行为以及需要更多控制的应用很合适。还有一个更简单的选项，你可以在 HTML 中直接用表单属性定义工具：

```html
<form 
  toolname="subscribe_newsletter"
  tooldescription="Subscribe an email address"
>
  <input 
    type="email" 
    name="email" 
    required
  />
  <button type="submit">Subscribe</button>
</form>
```

在这种情况下，浏览器会自动把表单变成一个工具。这种方式对不需要自定义逻辑的简单用例很合适。

### 把 goose 连接到 WebMCP

因为 WebMCP 运行在浏览器中，你需要一种让 goose 与它交互的方式。这正是 Chrome DevTools MCP 的用武之地。它充当 goose 和浏览器之间的桥梁，让 Agent 能够访问 WebMCP 工具。

我在测试时注意到的一点是，仅凭提示词并不总是足以让 Agent 使用 WebMCP。我不得不提供解释如何发现和执行工具的提示：

```markdown
const tools = await navigator.modelContextTesting.listTools();
const result = await navigator.modelContextTesting.executeTool("toolName", JSON.stringify({}));
```

没有这些指引，Agent 会默认使用浏览器自动化，因为那是当前模型更熟悉的方式。随着 WebMCP 越来越普及，这很可能变得不那么必要，但就目前而言，它有助于引导行为。

眼下，WebMCP 只在选择实现它的网站上有效，这限制了它能被使用的广度。与此同时，这个方向很重要。网站不必让 Agent 去解读界面，而是可以定义自己的能力，让 Agent 以结构化的方式与它们交互。这种转变减少了猜测、简化了集成，并把责任转移给那些最了解自己的系统。现在仍处于早期，但比起试图把网上的每一个界面都自动化，这个模型更合理。

### 资源

- [WebMCP 取色器演示](https://blackgirlbytes.github.io/webmcp-color-picker/)
- [WebMCP 航班演示](https://googlechromelabs.github.io/webmcp-tools/demos/react-flightsearch/)
- [WebMCP 披萨演示](http://googlechromelabs.github.io/webmcp-tools/demos/pizza-maker/)
- [分步教程](https://blackgirlbytes.github.io/webmcp-color-picker/tutorial.html)
- [WebMCP 早期预览文档](https://docs.google.com/document/d/1rtU1fRPS0bMqd9abMG_hc6K9OAI6soUy3Kh00toAgyk/edit)
- [Chrome DevTools MCP](https://github.com/anthropics/anthropic-tools/tree/main/chrome-devtools-mcp)
- [WebMCP GitHub](https://github.com/anthropics/anthropic-tools/tree/main/chrome-devtools-mcp)

<iframe width="560" height="315" src="https://www.youtube.com/embed/4LfBsSWEitE" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

<head>
  <meta property="og:title" content="WebMCP for Beginners" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2026/03/17/webmcp-for-beginners" />
  <meta property="og:description" content="WebMCP lets websites expose structured actions that AI agents can call directly. This guide explains how it works, how it differs from MCP and browser automation, and how to build your own WebMCP-enabled site." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/webmcp-for-beginners-f12da638fe0f49acf924c720a7d1243a.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="WebMCP for Beginners" />
  <meta property="twitter:description" content="WebMCP lets websites expose structured actions that AI agents can call directly. This guide explains how it works, how it differs from MCP and browser automation, and how to build your own WebMCP-enabled site." />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/webmcp-for-beginners-f12da638fe0f49acf924c720a7d1243a.png" />
</head>

---

## 使用你的 AI 订阅来使用 goose

> 原文：https://block.github.io/goose/blog/2026-03-19-use-goose-with-your-ai-subscription

多亏了 ACP（Agent Client Protocol），你现在可以用 goose 使用你为 codex、claude 和 gemini 订阅的服务了！
Codex 还有个特别之处：你可以直接登录 chatgpt，不需要安装任何其他东西。

Gemini 现在通过 OAuth 工作——只需用你的 Google 账户登录即可。在撰写本文时，claude 只需安装一个工具，且只需安装一次。

<!--truncate-->

### 为什么要用订阅？

嗯，你可以用上你已经付费的东西。这还用说！而且会话等等仍然在 goose 里。
ACP 让这些 Agent 的连接比把 CLI 当作 provider 使用更深。在这个世界里，你可以把它想成一层层的 Agent：
goose 通过 ACP 接入 gemini（还有别的东西，客户端也可以接入 goose！），但 gemini（以及 claude code）某种程度上也充当一个 Agent 循环。
有了 ACP，你使用的是（大部分）位于底层 Agent 中的工具。不过 Codex 是一个全能的 LLM api，所以对那一个，你可以在 goose 中原生地使用扩展。

### Claude Code——通过 ACP

如果你有 Claude Code 订阅，可以通过 [Agent Client Protocol（ACP）](https://agentclientprotocol.com/)在 goose 中使用它。这需要安装一个小小的适配器包：

```bash
npm install -g @agentclientprotocol/claude-agent-acp
```

然后通过 claude acp 扩展（CLI 或 GUI）配置 goose 来使用它。


或者通过环境变量来设置：

```bash
export GOOSE_PROVIDER=claude-acp
goose
```

goose 会通过 ACP 把你的 MCP 扩展传递给 Claude，因此你在 goose 中配置的任何自定义 MCP 服务器都可供该 Agent 使用。

### ChatGPT——用你的账户登录

如果你有 ChatGPT Plus 或 Pro，`chatgpt_codex` provider 让你用现有账户使用 goose。在你第一次设置 goose 应用时（或切换到该 provider 时）选择 ChatGPT 即可

第一次运行时，goose 会打开一个浏览器窗口，让你用 ChatGPT 账户登录。之后，你的会话会缓存在本地。

推荐的模型是 `gpt-5.3-codex`，它也是默认模型。你还可以从模型选择器中选择 `gpt-5.4`（OpenAI 最新的全模态模型）或 `gpt-5.2-codex`。

### Gemini——通过 OAuth

如果你的 Google 账户可以访问 Gemini，`Gemini`（`gemini_oauth`）provider 让你用现有账户使用 goose。第一次设置 goose 时（或切换 provider 时）选择 Gemini 即可。

第一次运行时，goose 会打开一个浏览器窗口，让你用 Google 账户登录。之后，你的会话会缓存在本地。

### 那旧的 CLI provider 呢？

Goose 此前支持 `claude-code`、`codex` 和 `gemini-cli` 作为「透传」CLI provider。这些很快就会移除，因为 ACP 才是未来！

### 速查表

| 订阅 | Provider | 安装 | 扩展 |
|---|---|---|---|
| Claude Code | `claude-acp` | `npm install -g @agentclientprotocol/claude-agent-acp` | ✅ 通过 MCP |
| ChatGPT Plus/Pro | `chatgpt_codex` | 无需——OAuth 登录 | ✅ 通过 MCP |
| Gemini | `gemini_oauth` | 无需——OAuth 登录 | ✅ 原生 |

挑一个与你已经在付费的服务相匹配的，你就可以开始了。

---

## 对手 Agent：用一个隐藏的 Agent 守护主 Agent 的安全

> 原文：https://block.github.io/goose/blog/2026-03-31-adversary-mode

![博客封面](https://block.github.io/goose/img/blog/adversary-mode.png)

goose 的一个愿望（嗯，至少是我们中一些人的愿望）是避免不停地请求权限，把一切决定都交给最终用户，以试图保证 Agent 执行工具时的安全。有时候这会变得相当嘈杂和烦人，而且当你读累了、批准累了之后，最终反而变得更不安全。

你当然可以按自己认为合适的方式调整设置，但考虑一下如何在不假设你可以不断打断用户请求权限的情况下让事情变安全，是件好事，尤其是围绕那些用户当下（脑子里）可能还没有上下文的事情。

在 goose 中，你可以启用一层层的东西，但当我们观察到各类 Agent 真的很有帮助、却作为副作用意外造成伤害时，我们也想思考一些通用解决方案。这就催生了「adversary mode（对手模式）」，其想法是：何不用另一个 Agent 以毒攻毒。Agent 想要有帮助，它们可以被导向去帮助用户，但另一个 Agent 可以被导向去防范那个 Agent「帮助」用户，从而让事情保持在策略之内并安全。

<!--truncate-->

### 什么是对手模式？

对手模式增加了一个静默的、独立的审查者，它在需要时、在每一个敏感调用*执行之前*对其进行评估。把它想象成一位有安全意识的同事在 Agent 肩头看着——它知道最初你要求的是什么，并能发现哪里对不上。它使用与主 Agent 同一级别的模型（理想情况下）或更好的模型，并作为一个自己的小 Agent 运行（上下文更小，所以运行更快、更便宜，因为它必须被频繁调用，你不想让成本直接翻倍！）。

也有[基于模式的提示词注入检测](https://block.github.io/goose/docs/guides/security/prompt-injection-detection)，但当你启用对手模式时，审查者能理解上下文。它看到你的原始任务、你最近的消息以及工具调用详情，然后做出判断：**ALLOW（允许）** 还是 **BLOCK（阻止）**。

配置非常简单（就是大白话，是 Agent 或人都能认同的东西，因为评估它的是一个 Agent）。

### 它是如何工作的

1. 在每次工具调用之前，对手会检查你的**原始任务**、**最近的对话**以及**拟议的工具调用**
2. 它根据你的规则进行评估，并返回 ALLOW 或 BLOCK
3. 被阻止的调用会被拒绝——主 Agent 看到拒绝，且无法重试
4. 如果审查者因任何原因失败，调用会被放行（fail-open，故障开放）

对手使用 goose 已经配置好的同一个模型和 provider。不需要额外的 API 密钥或设置。

### 开启它

在 `~/.config/goose/adversary.md` 创建一个文件，写入你的规则：

```markdown
BLOCK if the tool call:
- Exfiltrates data (posting to unknown URLs, piping secrets to external services)
- Is destructive beyond the project scope (deleting system files, wiping directories)
- Installs malware or runs obfuscated code
- Downloads and executes untrusted remote scripts

ALLOW normal development operations like editing files, running tests,
installing packages, using git, etc.
```

就这样。文件存在 → 对手模式开启。删除文件 → 它就关闭。空文件使用合理的默认值。

### 为什么不干脆用模式匹配？

基于模式的检测非常适合捕捉已知的攻击特征，goose 也支持这种方式。对手审查者能分辨 `curl` 是在下载依赖，还是在窃取你的 SSH 密钥——因为它知道你实际要求的是什么。它甚至能察觉某个 Agent 是否在创造性地、以碎片化的方式编写脚本，把数据外泄到一个公开 URL（再说一次，是为了「帮忙」！），而这不会被模式、规则或过滤器明显地捕捉到。

这两种方法是互补的。两个都用。把所有层次都用上！

### 接下来

我们把对手模式看作更广泛安全叙事中的一层。想了解它背后的深入思考，请查看我们关于[把 CORS 模型应用于 Agent 安全](https://block.github.io/goose/blog/2026/01/05/agentic-guardrails-and-controls)的文章。

完整的配置细节——包括如何扩展哪些工具会被审查——请见[对手模式文档](https://block.github.io/goose/docs/guides/security/adversary-mode)。

<head>
  <meta property="og:title" content="Adversary Agent: using a hidden agent to keep the main agent safe" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2026/03/31/adversary-mode" />
  <meta property="og:description" content="Introducing adversary mode — an independent agent reviewer that silently watches the main agent to keep it away from danger." />
</head>

---

## goose 有了新家——Agentic AI Foundation（AAIF）

> 原文：https://block.github.io/goose/blog/2026-04-07-goose-moves-to-aaif

![goose 迁往 Agentic AI Foundation](https://block.github.io/goose/img/blog/goose-aaif-foundation.png)

Block 已将 goose 捐赠给 Linux 基金会下的 [Agentic AI Foundation（AAIF）](https://aaif.io/)，与 Anthropic 的 Model Context Protocol（MCP）和 OpenAI 的 AGENTS.md 一起。你可以[在这里阅读完整公告](https://aaif.io/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation-aaif-anchored-by-new-project-contributions-including-model-context-protocol-mcp-goose-and-agents-md/)。

虽然 goose 对其使命和社区的投入没有任何改变，但以下是发生变化的地方；

<!-- truncate -->

### 新的文档站点
文档已迁至新站点：[https://goose-docs.ai/](https://goose-docs.ai/)，有着一个漂亮的 .ai 顶级域名！旧的文档链接会重定向，但请把你的书签更新到新站点。

### 更新后的 GitHub 仓库
GitHub 仓库及相关项目已从 `block/goose` 迁到一个新组织：

> **[https://github.com/aaif-goose/goose](https://github.com/aaif-goose/goose)**

这包括 [aaif-goose](https://github.com/aaif-goose) 组织中的相关仓库。

其他一切——项目、社区、使命——都保持不变。goose 仍然是开源的，仍然在积极开发中，仍然是你熟悉的那个 Agent。

### 更新你的 remote

如果你有本地克隆，更新你的 git remote：

```bash
git remote set-url origin git@github.com:aaif-goose/goose.git
```

### 迁移进行中

我们仍在处理一些迁移问题（失效链接、重定向、CI 等）。如果你遇到任何看起来不对劲的地方，请在 [Discord](https://discord.gg/n8R5VaWDAn) 上联系我们，让我们知道。
### 了解更多

访问 [aaif.io](https://aaif.io/) 以了解更多关于该基金会及其使命的信息。

---

## goose 2.0 beta——全新架构与客户端

> 原文：https://block.github.io/goose/blog/2026-04-08-goose-acp-and-new-tui

![博客封面](https://block.github.io/goose/img/blog/goose-2-blog-cover.jpg)

goose 诞生于终端。最早的版本是一个 Python CLI，在进程内运行 Agent——你输入一条消息，模型作出回应，工具执行，一切都在一个循环里发生。这种简单性是一种优势：它意味着任何有终端的人都能立即开始使用 goose，无需安装应用，无需运行服务器。

随着 goose 成长，人们想使用它的方式也在增多。我们发布了一个 Electron 桌面应用，于是突然之间我们有了两个客户端，走两条完全不同的集成路径。Rust CLI 在进程内直接与 Agent 对话，而桌面应用则经过 `goosed`——一个自定义的 REST + SSE 服务器。每一个新功能——会话管理、扩展加载、流式传输——都必须在两处分别接线。

<!--truncate-->

第三方开发者从来都无法轻松构建自己的客户端，因为他们根本没有标准的方式来连接。

我们需要一个单一协议，让任何客户端都能用它访问同一个 Agent 核心。为此，我们选择了 [ACP](https://agentclientprotocol.com/)，即 Agent Client Protocol，作为我们访问 goose 的新的默认接口。

### 底层：ACP

在幕后，我们正在统一每个客户端连接 goose 的方式，全部通过 **ACP（Agent Client Protocol）**。ACP 为每个客户端——终端、桌面、IDE 插件，任何你想构建的东西——提供了同一个协议和同一个 goose 服务器。这将使一个由不同 goose 客户端组成的生态成为可能。我们还有一份关于为 ACP 引入新的 HTTP/WS 传输的 [RFD](https://github.com/agentclientprotocol/agent-client-protocol/pull/721)，欢迎对该设计提出反馈。

目前的进展如下：

| 阶段 | 内容 | 状态 |
|-------|------|--------|
| **1 — 稳定 ACP 服务器** | 生产就绪的服务器，具备会话持久化、扩展、流式传输 | ✅ 完成 |
| **2 — TypeScript TUI beta** | 基于 ACP 客户端构建的功能完整的终端 UI | 🚧 进行中 |
| **3 — 桌面版重写为 Tauri** | 用基于 ACP 的 Tauri 桌面客户端替换 Electron 应用 | 🚧 进行中 |
| **4 — 整合** | 移除 `goosed` 和旧的 Rust CLI；单一统一架构 | 计划中 |

这项工作在 [#6642](https://github.com/aaif-goose/goose/issues/6642) 中跟踪。

### 新的 goose TUI

有了这个基础，我们现在发布建立在其之上的第一批官方客户端：一个你今天就能试用的全新 TypeScript TUI，以及一个将取代我们 Electron 桌面应用的基于 Tauri 的桌面应用。对你来说，这意味着无论在终端还是桌面上都有更快、更轻量的体验——以及一条清晰的路径，让社区无需逆向工程内部实现就能构建新的客户端和集成。

以下是正在发生的事情以及如何开始。

### 立即试用新的 TUI

新的基于 TypeScript 的 TUI 处于 beta 阶段。它已经支持消息、工具调用、语法高亮代码以及渲染后的 markdown。来试试：

```bash
npx @aaif/goose
```

就这样——一条命令，无需安装。它会拉取最新的 beta 并启动一个交互式会话。

![新的 goose TUI](https://block.github.io/goose/img/TUI.png)

#### TUI 接下来要做的

- Provider 和模型管理
- 会话列表、恢复和导出
- 用于 MCP 功能和 Skills 管理的 UI

我们很想听到你的反馈——试用一下，告诉我们哪些好用、哪些不好用。

### 桌面版正在迁往 Tauri

我们还在把桌面应用从 Electron 重写为 [Tauri](https://tauri.app/)。Tauri 重写带来了更好的性能、焕然一新的 UI，而且新应用会与 ACP 对话，因此两个官方客户端将共享同一个协议和服务器。

当桌面版准备好进行 beta 测试时，我们会再发一篇文章跟进。

### 参与进来

这一切都是公开进行的。跟进或加入进来：

- **跟踪 issue：** [#6642](https://github.com/aaif-goose/goose/issues/6642)
- **试用 TUI：** `npx @aaif/goose`
- **Discord：** 在 [#goose-2-dev](https://discord.gg/n8R5VaWDAn) 中跟进并给出反馈。
- **有反馈？** 开一个 issue 或在 #6642 上留言——我们很想听到你的声音。

<head>
  <meta property="og:title" content="goose 2.0 beta - new architecture and clients" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2026/04/08/goose-acp-and-new-tui" />
  <meta property="og:description" content="We're shipping a new TUI, rewriting the desktop app in Tauri, and unifying everything under ACP." />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="https://goose-docs.ai" />
  <meta property="twitter:title" content="goose 2.0 beta - new architecture and clients" />
  <meta property="twitter:description" content="We're shipping a new TUI, rewriting the desktop app in Tauri, and unifying everything under ACP." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/goose-2-blog-cover-aaee1526bc905939e34f5766d377a793.jpg" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/goose-2-blog-cover-aaee1526bc905939e34f5766d377a793.jpg" />
</head>

---

## 如何与你的 Agent「分手」

> 原文：https://block.github.io/goose/blog/2026-04-08-how-to-break-up-with-your-agent

![编辑器通过 ACP 连接到 Goose，而 Goose 连接到多个 Agent](https://block.github.io/goose/img/blog/how-to-break-up-with-your-agent.png)

过去一年开发者工具领域最大的转变不是 Agent 的兴起。而是 Agent 订阅的兴起。我们不再挑选 LLM 平台、计算 token 用量。我们开始挑选一个 Agent CLI，并支付固定的月费。

这行得通，直到你意识到每个 Agent 都意味着一套特定的前端。Cursor 是它自己的编辑器（一个 VS Code 分支）。Claude Code 起初是一个纯终端工具。许多 Agent 只在某一个特定环境里才能良好工作。即便是像 Copilot 这样拥有广泛 IDE 支持的 Agent，也把更深层的功能绑在它自己的生态里。如果你想在最喜欢的编辑器里换一个 Agent，往往就没戏了。

[Agent Client Protocol（ACP）](https://agentclientprotocol.com/)是由 [Zed Industries](https://zed.dev/) 主导的一项社区规范，它把 Agent 与编辑器解耦。Goose 双向实现了 ACP：编辑器可以接入 goose，goose 也可以接入其他 Agent。本文会带你了解这在今天的实践中是什么样子。

<!-- truncate -->

### 集成问题

存在几十个 Agent。存在几十个编辑器。每一种组合都需要一个自定义集成，而这个集成必须在双方发布更新时同时跟进两边。Goose 是吃了苦头才明白这一点的。多位社区维护者构建了 VS Code 扩展甚至一个 IntelliJ 插件，但[没有一个能跟上](https://block.github.io/goose/blog/2025/10/24/intro-to-agent-client-protocol-acp)goose 的发布节奏。goose 的每一次变更都意味着要更新每一个插件，而插件们渐渐落后了。

ACP 绕开了这一点。和 [MCP](https://modelcontextprotocol.io/) 一样，ACP 定义了一个基于 stdio 的 JSON-RPC 协议，不过是用于 Agent 与编辑器之间的通信。编辑器实现客户端接口，而 Agent 实现服务器端。模型选择、斜杠命令、文件 I/O 和终端执行等能力都在 ACP 协议中，从而消除了每个 Agent 各自的自定义代码。

### 在 Goose 中使用任何编辑器

Goose 已列入 [ACP Agent Registry](https://zed.dev/blog/acp-registry)，因此 [Zed](https://zed.dev/) 和 [JetBrains](https://blog.jetbrains.com/ai/2025/12/bring-your-own-ai-agent-to-jetbrains-ides/) 可以自动发现并安装它。对于还不读取该注册表的编辑器，比如配合 [avante.nvim](https://github.com/yetone/avante.nvim) 的 Neovim，配置很直接：

```lua
acp_providers = {
  ["goose"] = {
    command = "goose",
    args = { "acp", "--with-builtin", "developer" },
  },
},
```

流经 ACP 的内容不止于提示词。编辑器可以委派文件读取（包括你尚未保存的文件）、运行终端命令，并以原生方式呈现权限对话框。你在编辑器中配置的任何 MCP 服务器都会自动作为扩展添加到那个 goose 会话中，因此你不必在两处配置它们。

更多内容请见 [ACP 客户端指南](https://block.github.io/goose/docs/gdk/acp)。

### 在 Goose 中使用任何 Agent

Goose 也作为客户端使用 ACP。它可以把其他 Agent 作为 ACP provider 来编排。你保留 goose 的 UI 和扩展，但底层的 LLM 和 MCP 调用则经过另一个 Agent。目前包括 [Claude Code](https://github.com/agentclientprotocol/claude-agent-acp)、[Codex](https://github.com/agentclientprotocol/codex-acp)、[Copilot](https://docs.github.com/en/copilot/reference/copilot-cli-reference/acp-server)、[Gemini](https://github.com/google-gemini/gemini-cli)、[Amp](https://www.npmjs.com/package/amp-acp) 和 [Pi](https://github.com/svkozak/pi-acp)。

像 Gemini 和 Copilot 这样的 Agent 原生使用 ACP。其他像 Claude 这样的则需要先安装一个小小的适配器：

```bash
npm install -g @agentclientprotocol/claude-agent-acp  # one-time adapter install
GOOSE_PROVIDER=claude-acp GOOSE_MODEL=current goose
```

把模型设为 `current` 意味着「使用底层 Agent 中配置的任意模型」。

完整列表和设置说明请见 [ACP provider 指南](https://block.github.io/goose/docs/guides/acp-providers)。

### ACP 目前止步于何处

ACP 还处于 1.0 之前的阶段。有些东西运转良好，有些还不行：

- 权限对话框的呈现因编辑器而异。在 Zed 中看起来原生的东西，在 Neovim 中可能呈现得不一样。
- 并非每个 Agent 都会遵循客户端传入的 MCP 服务器配置。覆盖程度取决于该 Agent。
- 模型和模式切换的支持各不相同。有些 Agent 暴露完整的模型列表，另一些则暴露别名。
- 协议仍在趋于稳定。随着实现成熟，功能会在不同的稳定层级之间移动。

这些都是真实的边界。协议还很年轻。但方向是对的。

### 下一步走向何处

Goose 目前为它的桌面应用、CLI 和 ACP 服务器分别维护着不同的代码路径。这些正在收敛。goose 守护进程正在把 ACP 作为其协议过渡，因此每个前端都变成一个轻量的 ACP 客户端，与同一个后端对话。Provider 选择和配置变更通过 ACP 自定义请求进行，而不再由各前端各自处理逻辑。

在 provider 方面，如今向 goose 添加一个新的 ACP Agent 意味着要写一个 Rust 文件。声明式的 ACP provider 将用 JSON 配置取代那些文件，使得无需重新编译 goose 就能添加 Agent。结合对 [ACP Agent Registry](https://github.com/agentclientprotocol/registry) 的原生支持，goose 可以在新 Agent 出现在注册表中时就发现并提供它们，无需发布新版本。

### 试一试

Goose 最近被捐赠给了 Linux 基金会内的 [Agentic AI Foundation（AAIF）](https://aaif.io/)。互操作性是核心命题：goose 不应该把你锁死在某一个 Agent 或某一个编辑器里。

我正在 [AI Native DevCon](https://tessl.io/speaker/adriancole/) 上讲解这套架构，每一页幻灯片都链接到其背后的 PR 或 GitHub 讨论。

挑选你喜欢的 UI。挑选你喜欢的 Agent。它们不必是同一个东西。

- [ACP 客户端指南](https://block.github.io/goose/docs/gdk/acp)
- [ACP provider 指南](https://block.github.io/goose/docs/guides/acp-providers)
- [GitHub 上的 Goose](https://github.com/aaif-goose/goose)
- [Discord 社区](https://discord.gg/n8R5VaWDAn)

<head>
  <meta property="og:title" content="How to Break Up with Your Agent" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2026/04/08/how-to-break-up-with-your-agent" />
  <meta property="og:description" content="ACP lets you keep your favorite editor but swap the AI agent, or keep your agent but use it from any editor. Here's what actually works today in Goose." />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="block.github.io/goose" />
  <meta property="twitter:title" content="How to Break Up with Your Agent" />
  <meta property="twitter:description" content="ACP lets you keep your favorite editor but swap the AI agent, or keep your agent but use it from any editor. Here's what actually works today in Goose." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/header-f8e0e7e5dfa082ad8d33c0fdf84163d4.png" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/header-f8e0e7e5dfa082ad8d33c0fdf84163d4.png" />
  
</head>

---

## goose 中的 Mesh LLM：跨模型路由

> 原文：https://block.github.io/goose/blog/2026-04-20-mesh-llm

简短说明：[Mesh LLM](https://github.com/Mesh-LLM/mesh-llm/) 现在已进入 goose，作为一个与朋友和家人访问和共享（开放）LLM 的选项。

它使用与本地模式相同的 llama.cpp 基础设施来运行模型，只是有一点不同。

<!--truncate-->

### 什么是 Mesh LLM？

Mesh LLM 是一个我们正在试验的关联项目，它让人们以点对点方式连接各自的计算能力（可能只是一台笔记本电脑），这样他们就能访问原本无法自行托管的模型。

有一个演示用的公共「mesh」，它在任何时候都有一些算力。但你也可以创建自己的私有网络，把算力汇聚到一起。mesh 会尝试算出运行模型的最佳位置（按需下载它们），甚至能以各种方式拆分计算。

这是一个相当早期的项目，所以我们很想听到任何反馈。

看看[项目文档](https://docs.anarchai.org/)和[实时的公共 mesh](https://meshllm.cloud/dashboard)。

<head>
  <meta property="og:title" content="Mesh LLM in goose: routing across models" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2026/04/20/mesh-llm" />
  <meta property="og:description" content="Mesh LLM is now available as a provider setting in goose." />
</head>

---

## 默认私密：goose 内置的本地推理模型

> 原文：https://block.github.io/goose/blog/2026-04-24-use-goose-with-built-in-local-inference

![博客封面](https://block.github.io/goose/img/blog/goose-built-in-inference.png)

你现在可以直接在你的机器上用 goose 运行本地模型。不需要 Ollama，不需要 Docker，不需要外部服务器——完全在 goose 内部。我们发布了由 [llama.cpp](https://github.com/ggml-org/llama.cpp) 驱动的内置本地推理，它今天已经可以在桌面应用中使用。

这是使用 goose 的完全免费、零依赖路径。你的代码永远不会离开你的机器，没有需要管理的 API 密钥，而且它可以离线工作。下面是这种体验的样子、该选哪些模型，以及粗糙的边缘仍然在哪里。

<!--truncate-->

### 它是如何工作的

goose 现在把 llama.cpp 直接嵌入其运行时。当你选择 **Local** provider 时，goose 会从 HuggingFace 下载一个量化的 [GGUF](https://huggingface.co/docs/hub/en/gguf) 模型，把它加载到你的 GPU（或 CPU）内存中，并在进程内运行推理。

没有需要单独启动的服务器，没有需要配置的端口，没有后台守护进程。

在桌面应用中如何操作：

1. 打开 **Settings → Local Inference**
2. 在 Hugging Face 中搜索一个兼容的模型。
3. 点击下载——模型文件会落在共享的 Hugging Face 缓存中。
4. 开始构建。就这样。

goose 处理这些细节：GPU 卸载、内存管理、上下文窗口大小，以及在你切换模型时自动卸载模型。

### 这与 Ollama 有何不同

你可能已经熟悉通过 [Ollama provider](https://block.github.io/goose/blog/2025/03/14/goose-ollama)使用 goose。两条路径都在本地运行模型，但架构不同：

| | 内置（llama.cpp） | Ollama |
|---|---|---|
| **设置** | 无需——内置于 goose | 需单独安装 Ollama |
| **服务器** | 无——进程内 | Ollama 作为后台服务运行 |
| **模型格式** | 来自 HuggingFace 的 GGUF | Ollama 自己的模型注册表 |
| **模型管理** | goose 设置 UI | `ollama pull` / `ollama list` |
| **工具调用** | 原生（Gemma 4）或模拟 | 通过 toolshim 解释器 |
| **视觉** | ✅ Gemma 4 模型 | 取决于模型 |
| **配置** | 零配置 | `OLLAMA_HOST`、超时等 |

内置路径是为那些想要尽可能简单的本地体验的人设计的——一个应用，一次下载，搞定。如果你想要更多控制、更广的模型选择，或者你已经在为其他工具使用 Ollama，那么 Ollama 依然很棒。

### 会有怎样的体验

选择使用本地模型会带来一些代价——其中最大的是性能，取决于你硬件的能力。与云端模型相比：

**它更慢。** 第一个请求需要 30–120 秒，因为模型要加载进内存。之后，在 Apple Silicon（尤其是 M2/M3/M4）上 token 生成很快，但在仅用 CPU 的机器上会明显更慢。

**上下文窗口更小。** 大多数本地模型在 4K–8K token 的上下文下工作，而 Claude 或 GPT 是 128K+。goose 会根据你的可用内存设置 `num_ctx`，但在长会话中你会更快触到上限。[Code Mode](https://block.github.io/goose/blog/2026/02/06/8-things-you-didnt-know-about-code-mode)在这方面有帮助——它减少 token 用量和上下文腐化。

**工具调用是差距所在。** 用 Gemma 4 时，它确实不错。用模拟模型时，它仅限于 shell 命令。这是与云端体验相比最大的单一差异。

**它完全私密。** 什么都不离开你的机器。没有遥测，没有 API 调用，没有数据共享。对于处理专有代码、凭据或敏感数据，这很重要。

**它不花钱。** 初次下载模型之后，每个会话都是免费的。没有 token 要数，没有账单要操心。


### 充分利用它的技巧

**从小处开始。** 选择一个能舒舒服服放进 goose 可用内存里的量化模型。如果它对你的任务有效，就在需要更强能力时升级到更大的模型。

**使用 Code Mode。** 说真的。它就是为这种场景设计的——在更小的上下文窗口内保持会话高效。

**使用推荐。** goose 会把已经在你 Hugging Face 缓存中的模型与当前可用于推理的内存进行比较。

**别跟模拟模式较劲。** 如果你使用的模型没有原生工具调用，就顺着 shell 命令工作流来。让 goose 一步步地做事。它对「运行这条命令，检查输出，做下一件事」这样的模式效果很好。

**为不同任务切换模型。** 你可以下载多个模型。用一个小而快的模型做快速的 shell 任务，用更大的模型做复杂推理。goose 会自动卸载上一个模型。



<head>
  <meta property="og:title" content="Private by Default: Built-in Local Inference Models with goose" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2026/04/24/use-goose-with-built-in-local-inference" />
  <meta property="og:description" content="goose now ships with built-in local inference powered by llama.cpp — no server, no API key, no cost. Here's how it works and what to expect." />
  <meta property="og:image" content="https://goose-docs.ai/img/blog/goose-built-in-inference.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Private by Default: Built-in Local Inference Models with goose" />
  <meta property="twitter:description" content="goose now ships with built-in local inference powered by llama.cpp — no server, no API key, no cost. Here's how it works and what to expect." />
  <meta property="twitter:image" content="https://goose-docs.ai/img/blog/goose-built-in-inference.png" />
</head>

---

## 走出终端：goose 用 Peekaboo 掌控你的桌面

> 原文：https://block.github.io/goose/blog/2026-04-29-computer-controller-peekaboo

![goose 用带标注的 UI 元素控制 Mac 桌面](https://block.github.io/goose/img/blog/computer-controller-peekaboo.png)

大多数 AI Agent 生活在终端里。它们能读文件、运行命令、写代码——但让它们去点击某个 web 应用里的按钮或填写表单，它们就卡住了。它们无法*看见*屏幕上的内容，当然也无法与之交互。

从 v1.26 起，goose 走出了终端。Computer Controller 扩展用 [Peekaboo](https://github.com/steipete/Peekaboo) 从头重建，Peekaboo 是一个用于屏幕捕获和 GUI 自动化的 macOS CLI 工具。这给了 goose 面向桌面的眼睛和双手——它可以查看带标注的截图、识别 UI 元素、点击按钮、输入文本、滚动、拖拽，并在你 Mac 上的任何应用中浏览菜单。

<!-- truncate -->

### 看 → 点 → 输入 的循环

核心工作流极其简单，而且出奇地可靠：

1. **看** — goose 对某个应用截一张带标注的截图。每个可点击元素都会获得一个带标签的 ID，比如 `B1`、`B2`、`T1`。
2. **点** — goose 按元素的 ID 点击它。没有脆弱的像素坐标。
3. **输入** — goose 输入文本、按键，或使用键盘快捷键。

因为元素 ID 绑定到实际的 UI 组件（而不是屏幕位置），这种方法能适应不同的窗口大小和位置。goose 不需要知道按钮在屏幕上的*哪里*——只需要知道它是*什么*。

在实践中它是这样的：

```
goose: Let me see what's on screen...
→ see --app Safari --annotate

goose: I can see the form. Clicking on the email field...
→ click --on T3
→ type "hello@example.com" --return
```

`see` 命令既返回一张带标注的截图（临时存储在内存中），也返回带有元素 ID、标签和类型的结构化 JSON 数据。这种视觉与结构的结合，正是让交互可靠的原因。

### goose 实际上能用它做什么？

一旦 goose 能看见并与你的屏幕交互，它能处理的任务范围就大幅扩展。以下是一些真实例子：

#### 填写表单

> 「去 HR 门户，帮我提交下周五的休假申请」

goose 打开浏览器，导航到页面，识别表单字段，填写它们，然后点击提交——全靠看见 UI 并一步步与之交互。

#### 浏览复杂的 UI

> 「打开 Figma，找到名为 'Homepage Redesign' 的设计，把它导出为 PNG」

跨那些没有 API 的应用进行多步工作流成为可能。goose 可以点开菜单、在应用内搜索，并遵循多屏流程。

#### 控制系统设置

> 「打开勿扰模式，并把我的显示器亮度设为 50%」

系统偏好设置、菜单栏项目以及 macOS 设置都可以通过 Peekaboo 的 `menu`、`menubar` 和 `dialog` 命令访问。

#### 自动化重复的 GUI 任务

> 「对于我下载文件夹里的每个 PDF，用预览打开并打印它」

goose 可以把它已有的文件系统和 shell 能力与 GUI 自动化结合起来——读取目录列表，然后以可视方式打开并与每个文件交互。

### 完整的命令工具箱

Peekaboo 为 goose 提供了一整套用于与 macOS 交互的命令，涵盖视觉、交互和系统控制。完整列表请查看 [Peekaboo 文档](https://github.com/steipete/Peekaboo)。一些亮点：
- `see` — 截取一张带标注的截图，并获取结构化的 UI 数据
- `click` — 按 ID 点击某个元素
- `type` — 输入文本或按键
- `scroll` — 在某个元素内滚动
- `drag` — 从一个元素点击并拖拽到另一个元素
- `menu` — 与菜单栏项目交互
- `dialog` — 与系统对话框和通知交互


### 获得最佳效果的技巧

在大量使用 Computer Controller 之后，以下几点很有帮助：

- **goose 工作时不要碰你的鼠标。** goose 基于它所看到的来截图和点击。如果你在任务中途移动东西，它会困惑。
- **提示词要具体。** 「点击表单底部的蓝色 Submit 按钮」比「提交它」能给 goose 多得多的依据。
- **让 goose 先看。** goose 会自然地以一条 `see` 命令开始，先理解当前的 UI 状态再行动。如果你在调试某个交互，让 goose 重新截一张图。
- **长文本走粘贴。** 为了可靠，goose 在输入较长内容时使用 `paste` 而不是 `type`。这避免了特殊字符和打字速度带来的问题。

### 当前的局限

Computer Controller 很强大，但值得了解它的边界：

- **仅限 macOS（目前）** — Peekaboo 建立在 macOS 辅助功能 API 之上。在 Windows 和 Linux 上，Computer Controller 会回退到基于 shell 的自动化（Windows 上用 PowerShell 脚本，Linux 上用 xdotool/wmctrl）。
- **快速变化的 UI 可能很棘手** — 视频、动画和快速更新的内容会导致 goose 看到过时的状态。静态或变化缓慢的 UI 效果最好。
- **标准 UI 元素效果最好** — 自定义渲染的画布（比如某些游戏 UI 或高度自定义的 web 应用）可能不会暴露 Peekaboo 能识别的辅助功能标签。
- **一次一个屏幕** — goose 每条 `see` 命令处理一张截图，不过在多显示器设置中你可以用 `--screen-index` 定位特定屏幕。

### 试一试

Computer Controller 扩展内置于 goose——只要在你的扩展中启用它，然后开始让 goose 做视觉任务。如果你在 macOS 上，Peekaboo 会处理剩下的事。

在 goose Desktop 中，前往 **Extensions** 并打开 **Computer Controller**。在 CLI 中：

```sh
goose configure
# → Toggle Extensions → enable computercontroller
```

然后试一个简单的：

```
Take a screenshot of my current screen and describe what you see.
```

或者更有野心的：

```
Open System Settings, go to Displays, and set the resolution to "More Space."
```

goose 会弄明白剩下的事——看见 UI、识别正确的元素，并一路点击把事情办成。


<head>
  <meta property="og:title" content="Beyond the Terminal: goose Controls Your Desktop with Peekaboo" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://block.github.io/goose/blog/2026/04/29/computer-controller-peekaboo" />
  <meta property="og:description" content="The Computer Controller extension was rebuilt with Peekaboo, giving goose the ability to see, click, type, and interact with any application on your Mac." />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="block.github.io/goose" />
  <meta property="twitter:title" content="Beyond the Terminal: goose Controls Your Desktop with Peekaboo" />
  <meta property="twitter:description" content="The Computer Controller extension was rebuilt with Peekaboo, giving goose the ability to see, click, type, and interact with any application on your Mac." />
</head>

---

## 以三十分之一的成本逼近前沿性能

> 原文：https://block.github.io/goose/blog/2026-05-04-officeqa-minimax-m25

简短亮点：[Sentient AGI](https://x.com/SentientAGI/status/2046967422004154739) 最近与我们分享了一项名为「Grounded Reasoning」的挑战赛的一些结果，各团队在其中使用 MiniMax（2.5）开放模型攻克 Databricks OfficeQA 基准。

<!-- truncate -->

链接文章中的亮点：

> * 在 [Databricks 的 OfficeQA 基准](https://www.databricks.com/blog/officeqa)上使用 goose 搭配 [MiniMax M2.5](https://www.minimax.io/)，我们看到结果以**三十分之一的成本**逼近前沿模型性能。
> * 闭源模型在准确率上取胜（约 80% 对约 70%），但 MiniMax M2.5 平均每次运行 $1.74，而 Opus 4.5 为 $56.53。这大约便宜 30 倍。
> * 切换到 @goose_oss harness 后，准确率比替代方案高出约 10%，而且比下一个选项便宜 8 倍。我们决定通过独立测试进一步研究这一点。在 Terminal Bench 2.0 上，我们发现了类似的情况——goose 的 token 效率（以及成本）比 OpenHands 高 20 倍，比 OpenCode 便宜 40 倍以上。

在这里查看完整的帖子和结果：

> **[https://x.com/SentientAGI/status/2046967422004154739](https://x.com/SentientAGI/status/2046967422004154739)**

<head>
  <meta property="og:title" content="Approaching frontier performance for 1/30th the cost" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2026/05/04/officeqa-minimax-m25" />
  <meta property="og:description" content="Using goose with MiniMax M2.5 on the Databricks OfficeQA benchmark — approaching frontier model performance at a fraction of the cost." />
</head>

---

## 用 goose 跨多个 Agent 编排复杂工作流

> 原文：https://block.github.io/goose/blog/2026-05-05-goose-as-conductor

![goose 像指挥家一样编排多个 Agent](https://block.github.io/goose/img/blog/goose-conductor.png)

很多人一次只给他们的 Agent 布置一个任务——「做这个，现在做那个，再做下一件事」。这行得通，但很慢。许多人也希望他们的 Agent 同时做很多事：一边研究一边编码，一边审查一边测试，一边写文档一边重构。

这就是编排给你的东西。你不必一次给 goose 喂一个任务然后等待，而是可以让它协调多个并行工作的 Agent——每个专注于拼图中的特定一块，而 goose 让一切保持在正轨上。

<!-- truncate -->

### 什么是编排？

如果你以前用过[子代理](https://block.github.io/goose/docs/guides/context-engineering/subagents)，你就已经知道如何把工作委派给独立的 AI 实例。编排是它上面的一层——决定*谁*在*何时*做*什么*的那部分。与其让一个 goose 会话按顺序做所有事，编排让你可以：

- **分解**一个复杂任务为独立的子任务
- **委派**每个子任务给一个单独的 Agent（子代理、ACP provider，或另一个 goose 实例）
- **协调**结果——等待依赖、处理失败、合并输出

把它想象成单打独斗的开发者与管理团队的技术负责人之间的区别。

### 自己试试

这里有件你现在就能运行的事，看看编排如何运作。让 goose：

```
I need to understand this codebase. In parallel:
- Summarize the project structure and key dependencies
- Identify the main entry points and how data flows through them
- Find any TODO comments or known issues in the code
```

goose 会同时启动三个子代理——每个研究任务一个。你会在你的会话中看到它们同时工作，三份摘要大致一起返回，而不是一个接一个。原本会是三次顺序等待，现在变成了一次。

### 它如何建立在已有基础之上

编排不会取代子代理或子 Recipe——它建立在它们之上：

| 层 | 它做什么 |
|-------|-------------|
| [子代理](https://block.github.io/goose/docs/guides/context-engineering/subagents)（委派） | 启动独立的子任务 |
| 异步委派 | 在后台运行子代理，稍后收集结果 |
| [ACP provider](https://block.github.io/goose/docs/guides/acp-providers) | 引入外部 Agent（Claude Code、Codex、Amp） |
| **编排** | 把以上所有协调成结构化的工作流 |

如果子代理是你的队友，那么编排就是告诉它们做什么、何时做的项目计划。

### 分阶段工作流：研究 → 构建 → 验证

并非所有事都能并行运行。有些工作流有自然的阶段，后面的步骤依赖前面的结果。你可以自然地把它描述给 goose：

```
Build a REST API for the inventory system:
1. First, research the existing data models in src/models/ and the API patterns in src/routes/ (do both at the same time)
2. Then implement the inventory API routes following those patterns
3. Finally, write integration tests and do a security review (both at the same time)
```

goose 理解这里的依赖结构。阶段 1 并行运行两个研究任务。阶段 2 在构建前等待那些结果。阶段 3 并行启动两个独立的验证任务。

关键洞见：**读取可以并行，写入应当顺序进行**（尤其是当它们触及相同的文件时）。

### 编排 + ACP：混合 Agent

这里事情变得真正有趣。编排可以与 [ACP provider](https://block.github.io/goose/docs/guides/acp-providers) 一起工作，这意味着你可以委派给完全不同的编码 Agent——而不只是 goose 子代理。

要使用它们，你只需在提示词里说出来，例如：

```
Refactor the auth module for clarity using Claude Code,
then write tests for it, and use Codex to generate the API docs.
```

goose 理解你想让不同的 Agent 处理工作流的不同部分。它把每个任务委派给正确的 Agent，等待结果，并把一切汇总到一起。无论你在 CLI 还是桌面应用上，这都一样有效——你只需用自然语言提出。

唯一的前提是为你想要使用的任何 Agent [配置好 provider](https://block.github.io/goose/docs/guides/acp-providers)。

### 最佳实践

当你开始编排时，重要的是用那些概念上相互分离、不太可能导致共享文件编辑冲突的任务来做。以下是一些提示：

#### 让你的读取并行

研究任务是安全的并行对象。多个 Agent 可以同时读取同一个代码库、文档或 API，而不会相互踩踏。

#### 指令要明确

被委派者只知道你告诉它们的东西。它们彼此之间、以及与父会话之间都不共享上下文。如果某个被委派者需要前一个阶段的信息，请在指令中明确传递。

#### 从简单开始

你不需要编排所有事。对于直截了当的任务，单个子代理就够了。当你拥有真正独立的工作流，或需要对同一个问题有多个视角时，编排才大放异彩。

### 开始使用

如果你已经在使用 goose，你今天就可以开始编排。最简单的方式就是直接提出：

```
Do these three things in parallel: [task A], [task B], [task C]
```

goose 处理剩下的事——启动被委派者、并发运行它们，并把结果汇总到一起。

对于可复用的工作流，看看[并行子 Recipe 教程](https://block.github.io/goose/docs/tutorials/subrecipes-in-parallel/)来构建你可以与团队分享的 Recipe。如果你想引入外部 Agent，[ACP provider 指南](https://block.github.io/goose/docs/guides/acp-providers)会帮你把 Claude Code、Codex 或 Amp 配置好。

<head>
  <meta property="og:title" content="Orchestrate Complex Workflows Across Multiple Agents with goose" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2026/05/05/goose-as-conductor" />
  <meta property="og:description" content="Use goose to coordinate multi-agent workflows — decompose complex tasks, delegate to specialized agents in parallel, and synthesize the results." />
  <meta property="og:image" content="http://goose-docs.ai/assets/images/goose-conductor-c380f287a96196276ac7cb0a652e390c.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Orchestrate Complex Workflows Across Multiple Agents with goose" />
  <meta property="twitter:description" content="Use goose to coordinate multi-agent workflows — decompose complex tasks, delegate to specialized agents in parallel, and synthesize the results." />
  <meta property="twitter:image" content="http://goose-docs.ai/assets/images/goose-conductor-c380f287a96196276ac7cb0a652e390c.png" />
</head>

---

## Hooks：在每个 goose 事件上运行你自己的脚本

> 原文：https://block.github.io/goose/blog/2026-05-14-goose-hooks

![Hooks：在每个 goose 事件上运行你自己的脚本](https://block.github.io/goose/img/blog/goose-hooks.jpg)

goose 现在支持**生命周期 Hook**。把一个插件放到磁盘上的某个目录里，goose 就会在会话期间发生某些事情时运行你的 shell 脚本：某个工具即将触发、某个工具刚刚完成、用户提交了提示词、会话开始、会话结束。

如果你用过 Claude Code 的 hooks 或 git hooks，那是一个道理。如果你没用过：现在可以从外部对 Agent 循环进行脚本化，而无需编写任何 Rust 或任何 MCP 服务器。

<!-- truncate -->

### 它是如何工作的

goose 遵循 [Open Plugins hooks 规范](https://open-plugins.com/agent-builders/components/hooks)。任何位于 `~/.agents/plugins/<name>/`（用户范围）或 `<project>/.agents/plugins/<name>/`（项目范围）下、且包含 `hooks/hooks.json` 文件的插件目录，都会在启动时被自动发现。

一个最小的 hook 配置长这样：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "developer__shell|developer__text_editor",
        "hooks": [
          { "type": "command", "command": "${PLUGIN_ROOT}/scripts/log.sh" }
        ]
      }
    ]
  }
}
```

当事件触发时，goose 运行该命令，在环境中设置 `PLUGIN_ROOT`，并把一个 JSON 载荷通过 stdin 管道传给脚本：

```json
{
  "event": "PostToolUse",
  "session_id": "abc-123",
  "tool_name": "developer__shell",
  "tool_input": { "command": "rg TODO" },
  "working_dir": "/Users/you/project"
}
```

支持的事件有：

- `SessionStart`, `SessionEnd`, `Stop`
- `UserPromptSubmit`
- `PreToolUse`, `PostToolUse`, `PostToolUseFailure`
- `BeforeReadFile`, `AfterFileEdit`
- `BeforeShellExecution`, `AfterShellExecution`

`matcher` 字段是一个正则表达式，会针对该事件最相关的字符串（工具名、文件路径或 shell 命令）进行测试。不写它，hook 就会对该类型的每个事件触发。失败或超时的 Hook 会被记录日志，但不会让宿主工具崩溃，所以你的脚本可以随心所欲地粗糙。

### 几个可以尝试的东西

#### 1. 让 goose 在真正需要你的时候跟你说话

挑几个意味着「现在人类的注意力会有用」的事件——某个工具失败了、会话结束了、某个长时间运行的命令完成了——然后让 goose 在其中一个触发时说一句话：

```json
{
  "hooks": {
    "PostToolUseFailure": [{ "hooks": [{ "type": "command", "command": "${PLUGIN_ROOT}/scripts/notify.sh" }] }],
    "SessionEnd":         [{ "hooks": [{ "type": "command", "command": "${PLUGIN_ROOT}/scripts/notify.sh" }] }],
    "AfterShellExecution": [
      {
        "matcher": "^(cargo (test|build|clippy)|pnpm (test|build)|just )",
        "hooks": [{ "type": "command", "command": "${PLUGIN_ROOT}/scripts/notify.sh" }]
      }
    ]
  }
}
```

然后 `notify.sh` 根据载荷分支，挑一句话：

```bash
#!/usr/bin/env bash
payload="$(cat)"
event="$(printf '%s' "$payload" | jq -r .event)"

case "$event" in
  PostToolUseFailure)  echo "That didn't work. Need a hand?" | say -v Daniel ;;
  SessionEnd)          echo "Done. Come check this out."     | say -v Daniel ;;
  AfterShellExecution) echo "Long command finished."         | say -v Daniel ;;
esac
```

把 `matcher` 正则调整成在你的世界里算作「长时间运行」的任何东西——测试套件、构建、部署、`terraform apply`。

#### 2. 「goose 正在干活」的桌面指示灯 🪿💡

如果你有一个带 HTTP API 的智能灯泡（Hue、LIFX、Home Assistant 等），在 goose 开始一次工具调用时打开它，完成时关掉：

```json
{
  "hooks": {
    "PreToolUse":  [{ "hooks": [{ "type": "command", "command": "curl -s -X POST http://hue.local/light/on"  }] }],
    "PostToolUse": [{ "hooks": [{ "type": "command", "command": "curl -s -X POST http://hue.local/light/off" }] }]
  }
}
```

现在你的台灯就是 Agent 的状态指示器。走开，回头瞥一眼，如果它亮着，说明 goose 还在工作。

#### 3. 自动格式化 goose 编辑的每个文件

Hook `AfterFileEdit`，自己运行格式化程序，这样 Agent 就不必记着这件事：

```json
{
  "hooks": {
    "AfterFileEdit": [
      {
        "matcher": "\\.(ts|tsx|js|jsx|json|md)$",
        "hooks": [{ "type": "command", "command": "${PLUGIN_ROOT}/scripts/format.sh" }]
      },
      {
        "matcher": "\\.rs$",
        "hooks": [{ "type": "command", "command": "cargo fmt" }]
      }
    ]
  }
}
```

`scripts/format.sh` 从 stdin 读取文件路径，并对其运行 `prettier --write`。

#### 4. 每日会话日志

Hook `SessionEnd`，把一行摘要追加到一个 markdown 文件：

```bash
#!/usr/bin/env bash
payload="$(cat)"
session_id="$(printf '%s' "$payload" | jq -r .session_id)"
date_str="$(date '+%Y-%m-%d %H:%M')"
echo "- $date_str — session $session_id ended" >> ~/notes/goose-journal.md
```

也捕获 `UserPromptSubmit` 载荷，你就得到了今天你问 Agent 的每一个问题的日志。

#### 5. 让 goose 听起来像一艘潜艇

因为你可以：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Submarine.aiff"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "say 'Captain, the session has ended.'"
          }
        ]
      }
    ]
  }
}
```

当 goose 在另一个窗口里处理长时间任务时，这很有用。这个声音提示告诉你，它确实在做事，而不是坐在那里等你。

### 试试这个示例

仓库里有一个可用的示例，位于 [`examples/plugins/hello-hooks`](https://github.com/block/goose/tree/main/examples/plugins/hello-hooks)——一个把 `SessionStart`、`UserPromptSubmit`、`PreToolUse` 和 `PostToolUse` 接起来，并为每一个向 stderr 打印一个友好 emoji 的插件。把它复制到 `~/.agents/plugins/`，启动一个会话，看着事件飞过：

```bash
mkdir -p ~/.agents/plugins
cp -R examples/plugins/hello-hooks ~/.agents/plugins/hello-hooks
chmod +x ~/.agents/plugins/hello-hooks/scripts/announce.sh

goose session
# 🚀 [hello-hooks] SessionStart
# 💬 [hello-hooks] UserPromptSubmit
# ⚡ [hello-hooks] PreToolUse tool=developer__shell
# ✅ [hello-hooks] PostToolUse tool=developer__shell
```

每个事件还会被追加到 `~/.agents/plugins/hello-hooks/last-event.log`，这样你就能看到你的脚本收到的确切 JSON。触发一些事件，`tail` 一下日志，从那里开始构建。

### 为什么这很重要

MCP 服务器给 goose 新工具。Hooks 走的是相反方向：它们给你一种方式，用你已经会的任何语言，实时地对 goose 正在做的事作出反应。Bash、Python、一个 Go 二进制、一行 `curl`。全都只是 stdin 上的一条命令。

插件模型故意做得很小：一个文件夹、一个 JSON 文件、一个脚本。没有注册步骤，没有守护进程，没有重新编译。放进去，启动 goose，它就能用。拿出去，goose 也不会注意到它不在了。

如果你构建了好玩的东西，分享出来。`examples/plugins/` 目录是社区插件的好归宿，而 [Open Plugins 规范](https://open-plugins.com)意味着你在这里构建的任何东西都能与采用它的其他 Agent 一起工作。

Hook 愉快。🪝

---

## 自我改进的 Agent 仍需要人类

> 原文：https://block.github.io/goose/blog/2026-06-17-self-improving-agents-need-humans

![一位人类工程师在基准仪表盘和终端日志之间审视 AI Agent 的反馈循环](https://block.github.io/goose/img/blog/self-improving-agents-need-humans.png)

[古德哈特定律](https://en.wikipedia.org/wiki/Goodhart%27s_law)是基准测试者的诅咒：当一个度量变成目标，它就不再是一个好的度量。编码 Agent 的基准几乎就是为触发它而设计的。任务是公开的，结果是一个数字，而排行榜不可避免地会被那些——往往并非有意——对基准过拟合的 harness 填满。

这并不意味着首选标准 [Terminal-bench](https://www.tbench.ai/) 就没用了，但它确实改变了 goose 团队使用它的方式。排行榜是对通用 Agent 能力的一个噪声很大的度量。信号是一组失败的模式：goose 不断卡住的地方，或者 goose 失败而另一个 harness 成功的地方。

这也是为什么我们通常用 [Sonnet](https://www.anthropic.com/claude/sonnet) 而不是可用的最强模型来做基准测试。我们不是想得到尽可能大的数字。我们希望留下足够多的失败，以便看出 Agent 缺失了什么支持。

<!-- truncate -->

自我改进的 Agent 现在风头正盛，但我们所信任的那个版本目前仍需要人类。这个循环是：运行基准测试，让 [goose](https://github.com/aaif-goose/goose) 比较某个任务中一个 harness 成功而另一个失败的情况，并让它用具体的说法解释差异。然后人类查看其中几处失败，判断普遍的经验教训是什么，并要求 goose 实现那个更宽泛的改进。

人类这一步防止循环坍缩成基准测试的把戏。没有它，自我改进的 Agent 可能会选择为每个任务就写一个 [Skill](https://agentskills.io/)；Agent 和人一样懒。有了它，我们才有希望把某一个任务上的失败，转化成一个应当能帮助到我们尚未见过的任务的能力。

这方面的工具位于 goose 仓库中的 [`evals/harbor`](https://github.com/aaif-goose/goose/pull/9637)。主入口是 `./evals/harbor/cmd.py`，一个小巧的 Python 命令，带有 `run`、`list`、`show`、`task`、`compare` 和 `pull` 等子命令。它把 [Harbor](https://github.com/harbor-framework/harbor) 包裹在某个特定的 goose 二进制、模型和扩展集合周围，然后留下一个满是逐任务 JSON 和日志的目录。

这是 Python 表现非常好的一个场景。`cmd.py` 是一个 [PEP 723](https://peps.python.org/pep-0723/) 的 [`uv`](https://docs.astral.sh/uv/) 脚本，所以依赖就放在文件顶部。没有打包的繁文缛节，没有新仓库，也不用记着哪个 virtualenv 是被祝福过的。你让一个 Agent 添加一个子命令、为一个值加埋点，或者让输出表格不那么糟糕，它就直接做了。这个脚本既是控制面，也是实验的文档。这正是 vibe coding 大放异彩的地方：表达需要做什么的小工具，而且它们是否被优雅地编写出来真的无所谓。

实际的基准运行发生在一台远程 Linux 机器上，因为一次完整运行是缓慢、并行且大量使用 Docker 的工作。但分析不必留在那里。`cmd.py pull tbench@...:/path/to/goose` 会把运行目录 rsync 回来，然后本地工具就可以列出运行、检查某个任务，或比较两个作业。这比听起来更重要。如果每个问题都需要 SSH 进基准测试机器并手动在日志里摸索，你就会问更少的问题。

[PR #9637](https://github.com/aaif-goose/goose/pull/9637) 中的比较 Recipe 实现了 goose 查看结果的那一步。它们读取同一任务的两个运行、Agent 轨迹、验证器输出以及参考解法。有用的输出会解释机制：「A 注意到了图像，B 从未打开它」或者「A 在正确的文件存在后就停下了，B 一直重写它直到把它写坏」。

以下是近期工作中的两个发现。第一，goose 有时在已经有足够信息完成时还会继续探索。它会接近答案，但不是去下结论，而是继续戳来戳去，最终耗尽轮数，导致基准测试失败。同样的事情也可能发生在普通对话中：如果 goose 不知道自己在这段交流中已经进行到多远，它就没有真正的理由停止探索并转向一个解法。[PR #9636](https://github.com/aaif-goose/goose/pull/9636) 为 MoIM 添加了轮数感知——MoIM 是 goose 注入的、用于让模型保持方向感的上下文。所以现在 goose 知道什么时候该收工了。

第二，goose 失去了从磁盘读取图像的能力。最初，当你把一张图像拖进 goose 对话时，我们插入该图像的路径，并给模型一个读取它的工具。那很笨拙，所以我们用对话中恰当的图像加载取代了它。在这个过程中，我们意外地把磁盘图像工具也删掉了。在基准测试中，这表现为 goose 使用 [PIL](https://pillow.readthedocs.io/) 来检查图像，而不是使用模型的视觉能力。比较 Recipe 让这个失败变得显而易见，因为成功的那次运行看了图像，而失败的那次运行绕开了它。

多亏了这个循环，我们在 goose 中发现了两个真实的弱点并修复了它们。基准测试提升了，这很好，但更重要的是，这两处修复都应当让 goose 在正常使用中变得更好：在该完成时更不容易跑偏，并且重新能够查看磁盘上的图像文件。

这就是基准测试有用的时候：当它不再是一个排行榜，而开始成为一份 bug 报告。

---

## 转向以 issue 作为新的 PR

> 原文：https://block.github.io/goose/blog/2026-07-30-issues-are-the-new-prs

![goose GitHub 仓库显示 184 个未关闭的 pull request，列表逐渐模糊](https://block.github.io/goose/img/blog/issues-are-the-new-prs.png)

在过去，[向一个开源项目贡献你的第一个 PR](https://opensource.guide/how-to-contribute/) 相当麻烦。即便有很棒的说明，让项目构建起来、让应用跑起来、让测试通过，也需要实实在在的功夫。而且即便你确切知道要修哪个 bug，你也需要对项目架构有大致理解，并对你正在改动的代码有更细致的了解。

[编码 Agent](https://block.xyz/inside/block-open-source-introduces-codename-goose) 改变了这一切。问题不在于代码质量。网上到处都是关于 AI 垃圾内容的抱怨，但 Agent 写出的代码往往比初次贡献者写出的更好。问题在于，Agent [改变了开源的经济学](https://github.blog/open-source/maintainers/how-pull-request-limits-are-cutting-down-the-noise/)。

<!-- truncate -->

过去，一个 PR 是某人做过功课的不完美证据。除非你有某种理由相信维护者会想要它，否则你为什么要费力地实现一个功能？修复一个 bug 所需的工作也迫使你理解周围的代码。这并不保证好的判断力，但这种摩擦筛选出了投入，并迫使贡献者在写代码之前获取上下文。

如今，[产出一个看似合理的功能实现或 bug 修复很便宜](https://github.blog/ai-and-ml/github-copilot/assigning-and-completing-issues-with-coding-agent-in-github-copilot/)。而判断这个改动是否属于这个项目、以及正确的解法是什么，仍然昂贵。一个 PR 到来时这些问题看似已经有了答案，但往往 Agent 只是做了一系列看似合理的选择。维护者必须挖出那些选择，判断哪些是对的，并解释其他的应当如何改。贡献者的 Agent 会迅速修改代码，但判断是维护者提供的。到那时，维护者为什么不干脆运行自己的 Agent 呢？

推演到极致，这会让开源项目拥有公开的代码，却没有有意义的公众参与：项目由一个小核心团队及其 Agent 开发，而其他所有人都变成被动的用户或工单提交者。但[开源的价值](https://github.com/aaif-goose/goose/blob/main/GOVERNANCE.md#contributors)从来都不局限于外部人写出的代码。外部人带来新鲜的眼光、新的想法、意料之外的用例和领域知识。他们遇到核心团队从未见过的问题，并质疑核心团队不再注意到的假设。

为了保住这份价值，我们必须放弃把 PR 作为主要贡献机制，把外部贡献上移。有价值的贡献之处不再主要在于写代码，而在于提交好的 issue，更重要的是，参与那场把 issue 变成深思熟虑的解法的讨论。

我们正通过一个公开的 [Goose Issues 看板](https://github.com/orgs/aaif-goose/projects/1)把 goose 转向这一模式。和以前一样，如果你发现一个 bug 或想要一个新功能，就[提交一个 GitHub issue](https://github.com/aaif-goose/goose/issues/new/choose)。新的 issue 进入 Inbox。在分类处理期间，我们可能会要求更多信息，或者附上解释关闭该 issue。我们想要解决的问题会移动到 Accepted / design，在那里贡献者和核心团队一起确定预期的设计、架构约束，以及结果将如何被验证。

当那场讨论尘埃落定，issue 就移动到 Ready。到那时，一个 Agent 就可以写代码了。实现进行期间 issue 移动到 In progress，当结果准备好由人类确认它确实有效时移动到 Verification。只有到那时它才是 Done。不实现某个 ready issue 的 PR 会被关闭，[反馈未被处理](https://github.com/aaif-goose/goose/blob/main/CONTRIBUTING.md#ai-code-reviews)的 PR 也会被关闭。

这也改变了谁值得被记功。报告问题、复现问题、贡献领域知识、塑造设计、实现解法以及验证结果，都可以是有意义的工作。每个阶段的重要贡献者都应当被认定为[共同作者](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors)。开源贡献的单位不再是补丁；而是把一个问​​题一路带到经过验证的解法。如今这种贡献的大部分都发生在 issue 里。

---

## Agentic 状态机

> 原文：https://block.github.io/goose/blog/2026-09-16-agentic-state-machines

![一只 goose 从纠缠的 Agent 循环走进一排井然有序的状态机](https://block.github.io/goose/img/blog/agentic-state-machines.jpg)

[goose 发布](https://github.com/aaif-goose/goose/blob/dd126afa6c73fe01ad4991a6b45a6d027cb02b29/README.md)已经很久了。狗年跟 Agent 年比起来算不了什么。goose 比通用的 agentic AI 还要早一点。这一切背后最初的想法是：如果你把对一个 shell 会话的控制权交给一个 LLM，会发生什么？

结果发现，有趣的事情发生了。模型写一条命令，命令运行，结果回到对话中，模型决定下一步做什么。我们的工具调用很自然地从那个实验中生长出来，如今位于大多数编码 Agent 核心的 Agent 循环也是如此。

随后工具调用被正式化，[MCP 出现了](https://www.anthropic.com/news/model-context-protocol)。[审批](https://block.github.io/goose/docs/guides/managing-tools/tool-permissions)、[上下文管理](https://block.github.io/goose/docs/guides/sessions/smart-context-management)、[待办列表](https://block.github.io/goose/docs/mcp/todo-mcp)、top-of-mind、[子代理](https://block.github.io/goose/docs/guides/context-engineering/subagents)、重试、[hooks](https://block.github.io/goose/docs/guides/context-engineering/hooks)、[skills](https://block.github.io/goose/docs/guides/context-engineering/using-skills)、[recipes](https://block.github.io/goose/docs/guides/recipes) 和 steering 也是如此。但原本的 Agent 循环仍然存在。每一个功能都增添了又一个分支、又一个局部变量或又一个特殊情况。十几个不同的关注点可能在一个轮次内同时活跃，彼此相互影响。取消需要知道当前正在运行的是推理还是一个工具。压缩需要理解 provider 错误和用量。工具可以改变提示词。一个停止 hook 可以把一个已完成的回答重新变成更多工作。循环开始变成意大利面。

<!-- truncate -->

[插件系统](https://block.github.io/goose/docs/guides/context-engineering/plugins)看起来是自然的答案。它在一定程度上有所帮助：添加一个工具或监听一个事件很契合。但一旦某个插件需要影响整个轮次，中央循环仍然必须决定它何时运行、它向提示词贡献什么、它是否可以继续该轮次，以及它的状态如何挺过一次重启。插件 API 逐渐为 Agent 循环的每一个部分都获得一个 hook，而循环仍然负责协调它们全部。

goose 采取了不同的方法。我们[用可重入的状态机取代了经典的 Agent 循环](https://github.com/aaif-goose/goose/pull/9574)。持久化的对话是主状态，每一块 Agent 行为都被编码为一个 [`Operation`](https://github.com/aaif-goose/goose/blob/main/crates/goose-agent/src/operation.rs)。状态机按顺序检查各个 Operation。每一个要么通过，要么返回一组 effect，第一个生效的在那一​​步胜出。它的 effect 被持久化，状态机带着新状态从顶部重新开始。

考虑一次普通的工具调用。推理看到最后一条消息来自用户，并产出一条请求工具的助手消息。在下一步，审批 Operation 首先有机会检查它。如果需要审批，它就向对话添加一个请求并让出给客户端。在用户决定期间，没有任何东西保持运行。客户端稍后存储答案，一个新建的状态机从那里继续。如果不需要审批，该 Operation 通过。然后工具执行 Operation 识别该工具并运行它，把结果添加到对话中。推理看到工具响应，并询问模型下一步做什么。当模型最终在没有请求另一个工具的情况下作答时，stop-hook Operation 决定该轮次是否可以结束。

这种可重入性的意义超出了代码组织。服务器在等待输入时不需要保持一个协程及其所有局部变量存活。一个进程可以重启并从最后一个持久化的步骤继续。另一个前端可以加载同一个会话并继续下去。便捷运行器仍然会重复步骤直到状态机让出，但它只是一个围绕状态机的小驱动器，而状态机一次可以被调用一次。

Operation 是独立但协作的。一个工具处理器只认领它知道如何执行的工具。如果它不认识某个工具，它就让出，给另一个 Operation 一个机会。最后的 unknown-tool Operation 把剩下的一切变成给模型的错误。同样的所有权也适用于执行之外。skills Operation 拥有列出 skills 的命令、加载某个 skill 的工具，以及告诉模型存在哪些 skills 的提示词文本。移除那个 Operation，这三者就一起消失。

推理很特别，但它仍然是一个 Operation。在调用模型之前，它从流水线中的每一个 Operation 收集工具、提示词片段和 top-of-mind。max-turns Operation 可以告诉模型它的预算快用完了。recipe Operation 可以添加一个最终输出工具。skills Operation 可以宣告可用的 skills。推理不需要知道这些贡献中任何一个来自哪里。

另一个有用的区分是 [effects](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/agents/state_machine/effects.rs) 和 [events](https://github.com/aaif-goose/goose/blob/main/crates/goose-agent/src/events.rs) 之间的区别。Events 是实时流：一段文本、一个工具通知或一次用量更新，客户端应当立即看到。Effects 是持久的结果：追加这条消息、替换这段对话、更新这个工具请求或记录这次用量。调用方可以要求状态机走一步，并决定如何应用那些 effects，或者使用一个便捷运行器，不断应用步骤直到状态机让出给客户端。

测试变得容易多了。我们针对一个[行为像模型 provider 的小 HTTP 服务器](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/agents/state_machine/tests/dummy_api.rs)和一个[真实的有状态计算器扩展](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/agents/state_machine/tests/calculator_extension.rs)来测试完整的 Operation 集合。我们还有一个[测试运行器，它在每一步应用之后都丢弃整个状态机](https://github.com/aaif-goose/goose/blob/main/crates/goose/src/agents/state_machine/tests/pipeline.rs)，并从持久化的会话构建一个新的。如果一次工具调用仍然能从请求推进到响应再到最终答案，我们就知道进度真的被捕获在状态中，而不是藏在某个局部变量里。

并非所有状态都消失了。Provider、扩展管理器和 hooks 仍然是运行时依赖。待处理的 steering 仍然从一个内存队列开始，而外部副作用需要小心：如果一个工具成功了，但进程在它的响应被持久化之前崩溃，重建状态机并不会神奇地让那个工具可以安全地运行两次。有用的变化是，这些边界现在是可见的，而不是被混进一个长期运行的协程里。

结果是一个更容易测试、重构和试验的代码库。一个改变 Agent 的新想法可以表达为一个 Operation，并添加到流水线中，而无需改动状态机核心。原本的 Agent 循环把 goose 带到了令人惊讶的远方。现在我们可以在不给它增添又一个分支的情况下改变 Agent 的行为。
