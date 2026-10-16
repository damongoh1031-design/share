# goose 官方文档中文手册：第 24 章　博客（二）：2025-04 ~ 2025-05

## 面向非开发者的 MCP 讲解

> 原文：https://block.github.io/goose/blog/2025-04-01-mcp-nondevs

![博客封面](mcp_nondevs.png)

到处都在说 MCP，它究竟是什么？如果你不是开发者，也能用它吗？🤔

<!--truncate-->

### 什么是 MCP？

MCP 是 [Model Context Protocol](https://modelcontextprotocol.io/introduction)（模型上下文协议）的缩写，是由 Anthropic 创建的开放标准。

假设你正在寻找在工作中用 AI 提高效率、尽可能节省时间的办法。于是你去了解像 OpenAI 或 Claude 这样的大语言模型（LLM），并开始和其中一个聊天。能和 AI 对话、让它立刻回答问题或告诉你该怎么做，这确实很神奇，但让 AI 替你干活又如何呢？

如今已经出现了能替你采取行动、替你做决策的 AI agent（AI 智能体）或 AI 助手。但要让你的 AI agent 与你自己的系统（比如 Google Drive、Asana 或 Slack）交互，此前并没有标准做法。至少，每次你需要让 AI agent 与你需要它对接的东西协同工作时，都得从头摸索。这极其繁琐。

这正是 MCP 的用武之地。最棒的是，你不需要是开发者就能开始使用它们！MCP 本质上让你无需写代码，就能让 AI agent 访问你的外部系统。你可以把 MCP 看作系统与 AI agent 之间的连接器，或者把它比作 AI 集成领域的 USB-C。

### 你现在就该试试的 MCP 服务器

那么，你能把 AI agent 连接到什么？MCP 服务器！MCP 服务器让你的 agent 访问你的工具。有[超过 3000 个 MCP 服务器](https://glama.ai/mcp/servers)可供连接，下面是你应该尝试的热门 MCP 服务器榜单：

- **[Google Drive](https://block.github.io/goose/docs/mcp/google-drive-mcp)**：为 Google Drive 提供文件访问与搜索能力
- **[YouTube Transcript](https://block.github.io/goose/docs/mcp/youtube-transcript-mcp)**：抓取并处理 YouTube 视频字幕
- **[Google Maps](https://block.github.io/goose/docs/mcp/google-maps-mcp)**：位置服务、路线规划与地点详情
- **[Tavily Web Search](https://block.github.io/goose/docs/mcp/tavily-mcp)**：使用 Tavily 的 Search API 进行网络与本地搜索
- **[Asana](https://block.github.io/goose/docs/mcp/asana-mcp)**：查看 Asana 任务、项目、工作区和/或评论
- **[Speech](https://block.github.io/goose/docs/mcp/speech-mcp)**：实时语音交互、音视频转录、文本转语音转换等
- **[GitHub](https://block.github.io/goose/docs/mcp/github-mcp)**：读取、搜索和管理 Git 仓库的工具
- **[Fetch](https://block.github.io/goose/docs/mcp/fetch-mcp)**：抓取并转换网页内容，便于 LLM 高效使用

这份简短清单应该能让你大致了解如今可以在工作流中运用 AI agent 的各种方式。你也可以在[好用的 MCP 目录](https://dev.to/techgirl1908/my-favorite-mcp-directories-573n)中探索社区热门项目，并在安装前了解[如何检查 MCP 服务器是否安全](https://block.github.io/goose/blog/2025/03/26/mcp-security)。

你还可以查看这些 [Goose 教程](https://block.github.io/goose/docs/category/mcp-servers)，它们会手把手展示如何将其中一些热门 MCP 服务器与 Goose 配合使用；或者使用 [Goose 的 Tutorial 扩展](https://block.github.io/goose/docs/mcp/tutorial-mcp)，在你使用或构建扩展时获得额外帮助。

### 示例 MCP 提示词

既然你已经见识了一些现有的 MCP 服务器，那么如何确保你能以最佳方式把 MCP 与 AI agent 配合使用？这就是提示词发挥作用的地方。

提示词归根结底就是你与 AI 助手交互时输入的文本，它既可以是非常简单的问题，也可以是详细的指令！下面是一些你现在就能向 Goose 这类 AI agent 提出的示例提示词，它们用到了上文提到的一些 MCP 服务器：

#### Google Maps
```
Google Maps: Track the live GPS location of driver ID #{driver_id}. Query Google Maps for real-time traffic data and adjust the estimated delivery time if delays exceed 5 minutes. If ETA changes, update the customer's live tracker and send an SMS notification. If the delay is greater than 20 minutes, check if another driver within a 1-mile radius can take over the delivery.
```
#### YouTube Transcript
```
YouTube Transcript: Get the transcript from this youtube video [link to video]. Then, summarize it into a blog post.
```
#### Google Drive
```
I have an important marketing budget review meeting in 30 minutes and I need your help getting prepared. I have several documents in my Google Drive from our previous meetings and planning sessions. Could you help me by:

1. Finding all relevant documents about our marketing budget and performance
2. Giving me a quick summary of our Q1 performance
3. Highlighting the key decisions we need to make about the marketing automation tool and video production
4. Identifying any outstanding action items from our last meeting
```
#### Asana
```
Asana: Create a new task in my Asana workspace called 'Review Q4 metrics' and set the due date to next Friday. Then, find all tasks assigned to me that are due this week and summarize them.
```
#### GitHub
```
GitHub: Create a new branch called hello-world in my angiejones/goose-demo repository. Update the README.md file to say "this was written by goose" and commit it. Open a pull request with your changes.
```

### 可能性无穷无尽

虽然有些 MCP 服务器由官方提供方开发，但你看到的大多数 MCP 服务器其实都是由社区成员开发的！此外，由于 MCP 是开放标准，任何人都可以为任何资源构建 MCP 服务器。你甚至可以用 Goose 来帮你构建一个！

希望从现在起，与其花几个小时手动收集数据、制作下一份营销报告，或者在周一手动翻遍你的待办积压，你会用 Goose 搭配 MCP，让它在几分钟内替你完成。

*想了解更多关于使用 MCP 服务器和 goose 的内容，请查看 [goose 文档](https://goose-docs.ai/docs/category/getting-started)，或加入 [Block 开源 Discord](https://discord.gg/n8R5VaWDAn)，与其他开源社区成员交流。*

<head>
  <meta property="og:title" content="MCP Explained for Non-Developers" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/04/01/mcp-nondevs" />
  <meta property="og:description" content="Learn what Model Context Protocol (MCP) is and how anyone can use it to save time on tasks." />
  <meta property="og:image" content="http://goose-docs.ai/assets/images/mcp_nondevs-5ce7f39de923cab01de6e14e5dc06744.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="MCP Explained for Non-Developers" />
  <meta property="twitter:description" content="Learn what Model Context Protocol (MCP) is and how anyone can use it to save time on tasks." />
  <meta property="twitter:image" content="http://goose-docs.ai/assets/images/mcp_nondevs-5ce7f39de923cab01de6e14e5dc06744.png" />
</head>

---

## 作为开发者，我最常与 Goose 搭配使用的 5 个 MCP 服务器

> 原文：https://block.github.io/goose/blog/2025-04-01-top-5-mcp-servers

![博客封面](mcp-servers-cover.png)

作为一名开发者，找到能无缝协作的合适工具，感觉就像发现了超能力。而当你已经有一套顺手的工作流程时，有时又很难去尝试新工具。

随着 MCP 的出现，像 Goose 这样的 AI agent 能够接入我现有的工具，我的工作流唯一的变化就是随之而来的、令人欣喜的自动化。我做的事情和以前一样，但在 AI 的加持下，我能做得更快、更有把握。

今天，我很兴奋地分享我最喜欢的 MCP 服务器，而且是我几乎每天都在用的那些，配上的真实应用场景你可能也会感同身受。

<!--truncate-->

:::tip
你可以问 Goose「用某个扩展能做什么」，来获取该扩展的全部功能和可尝试的示例用例清单。
:::

### GitHub MCP Server：GitHub 的一切

[GitHub MCP Server](https://block.github.io/goose/docs/mcp/github-mcp) 功能相当丰富。它可以帮你创建 issue、pull request、仓库和分支。我使用 GitHub MCP 最频繁的场景是审阅和理解 pull request。

当遇到一个很大的 pull request，或者我看不懂它在做什么时，我可以把 PR 交给 Goose，给它足够的上下文，让它帮我理解，然后据此对 PR 采取行动。我甚至能根据 PR 中的文件改动，生成文档更新或变更日志更新。这绝对是我最喜欢的功能之一。

例如

```
Hey Goose, this pull request https://github.com/aaif-goose/goose/pull/1949, has a lot of changes. Can you summarize into a changelog for me?
```

### Knowledge Graph Memory：开了外挂的上下文

[Knowledge Graph Memory](https://block.github.io/goose/docs/mcp/knowledge-graph-mcp) 扩展就像给 Goose 装上了一块关于你项目或数据的「照相式记忆」。顾名思义，它会把喂给它的任何信息构建成一张图，在不同信息片段之间建立联系——或者按我喜欢的用法——用于文档。

如果我在处理某个特定项目或库，又不想出现任何幻觉，我就能把正确的上下文喂给 Goose，它便能带着正确的上下文回答关于该项目或库的问题。

这可以是我当前正在处理的项目的文档，甚至可以是我正在使用的某个库的文档。

例如

```
I'm currently in a project called Goose, read through the documentation in `documentation/docs/` folder and store key information in the knowledge graph. Use it for reference anytime I ask you about Goose.
```

### Fetch 扩展：网络尽在掌握

在 [Tavily Web Search 扩展](https://block.github.io/goose/docs/mcp/tavily-mcp)和 [Fetch 扩展](https://block.github.io/goose/docs/mcp/fetch-mcp)之间，我稍微纠结了一下，因为虽然我两者都用它来访问网络，但 Fetch 扩展对我来说更像是默认选项。配合上面 Knowledge Graph 的例子，我能够从互联网获取信息，为 Goose 提供额外的上下文供其使用。

:::note
Tavily Web Search 扩展具备深度研究能力，非常适合查找特定信息；而 Fetch 扩展更偏向通用的网络访问与数据获取。
:::

### Memory 扩展：我的习惯与偏好

我用 [Memory 扩展](https://block.github.io/goose/docs/mcp/memory-mcp)来在工作时提醒 Goose 我的一般偏好——比如在试做新原型时默认用 JavaScript 或 Node，我更喜欢哪种命名约定——甚至包括我喜欢怎么喝咖啡 :D。

它的工作方式与 Knowledge Graph 扩展不同，尽管两者都在本地存储信息。当与 Knowledge Graph 结合使用时，它还能帮助清晰记录技术决策及其理由。例如，我在一次代码迁移中卡住了，于是让 Goose 记住我们停在哪里、到目前为止尝试过什么、下一步想做什么，以便我开启新会话时参考。

### VS Code 扩展：你最喜欢的编辑器，已接入

<ArchivedExtensionWarning extensionName="VS Code Extension" repoUrl="https://github.com/block/vscode-mcp" />

在与人交流时——尤其是围绕 vibe coding——最大的话题之一就是找到追踪改动的方法。虽然版本控制始终是推荐的，但有时我希望在走得太远之前能停下来或改变方向。[VS Code 扩展](https://github.com/block/vscode-mcp)连同其他功能，让我能在提交前预览代码改动的 diff。

我可以选择接受或拒绝这些改动，或者在实际改动发生前告诉 Goose 换个思路试试。

### 集成的力量

正如本文开头提到的，这些 MCP 服务器最棒的地方在于它们如何接入我现有的工作流。我能够：

- 在 Goose 上开启一个新会话，它会把当前文件夹作为项目在 VS Code 中打开。
- 开始处理任何改动，并通过 Knowledge Graph 或使用 Fetch 扩展从互联网获取我需要的任何上下文。
- 任何尝试做出的改动都会把我来自 Memory 扩展的偏好考虑在内。
- 然后我可以在 VS Code 中直接审阅这些改动，并接受或拒绝。
- 最后让 Goose 替我创建一个 pull request，完成任务。

这是我如何把这些扩展搭配使用的一个简化示例——我可能不会在每个会话里都用到全部扩展，但手边有它们确实让我的工作流顺畅得多。

你最喜欢的 MCP 服务器是哪些？你会怎样把它们组合使用？到 [Discord 服务器](https://discord.gg/n8R5VaWDAn)和我们分享你的经验吧！

<head>
  <meta property="og:title" content="Top 5 MCP Servers I Use as a Developer with Goose Extensions" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/04/01/top-5-mcp-servers" />
  <meta property="og:description" content="These 5 MCP servers help me automate my workflow and make me a better developer." />
  <meta property="og:image" content="http://goose-docs.ai/assets/images/mcp-servers-cover-6994acb4dec5a3b33d10ea61f7609e4b.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Top 5 MCP Servers I Use as a Developer with Goose Extensions" />
  <meta property="twitter:description" content="These 5 MCP servers help me automate my workflow and make me a better developer." />
  <meta property="twitter:image" content="http://goose-docs.ai/assets/images/mcp-servers-cover-6994acb4dec5a3b33d10ea61f7609e4b.png" />
</head>

---

## 如何负责任地进行 Vibe Coding（借助 goose）

> 原文：https://block.github.io/goose/blog/2025-04-08-vibe-code-responsibly

:::warning 已过时
第 1 步中描述的 CLI `/plan` 命令此后已从 goose 中移除。本文中的其他做法仍然适用；请改用自然语言向 goose 索要计划。
:::

![博客封面](responsible-vibe-code.png)

2025 年 2 月 2 日，Andrej Karpathy 创造了「[vibe coding](https://x.com/karpathy/status/1886192184808149383)」这个词。Vibe coding 代表一种全新的编码方式：开发者让 AI agent 去构建某个东西，然后顺其自然。

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) 让这种做法成为可能。在 MCP 出现之前，开发者在不同应用之间复制粘贴上下文。这种工作流远未达到大家所宣称的 AI agent 自动化程度。如今，AI agent 可以利用 MCP 自主工作，并与从 GitHub 到 Cloudflare、YouTube、Figma 的任意应用集成。

这一转变让编码走向大众化。例如，它赋能了：

* Web 开发者用 Unity 创作电子游戏
* 设计师和产品经理为全栈应用制作原型
* 企业主把他们的愿景变成可用的产品

这是一种解放性的体验。但很多时候，我们就像握着键盘的[伊卡洛斯](https://www.britannica.com/topic/Icarus-Greek-mythology)，vibe coding 得太靠近太阳。

<!--truncate-->

### Vibe Coding 的阴暗面

这种创作自由伴随着重大风险。许多开发者在 vibe coding 时都遇到过严重问题：

* 提交带有安全漏洞的代码
* 在「意大利面式」代码之上引入难以修复的 bug
* 因缺乏版本控制而损失数周乃至数月的工作
* 在生产环境中意外泄露环境变量和 API 密钥等敏感信息

<blockquote className="twitter-tweet" data-dnt="true" align="center"><p lang="en" dir="ltr">Today was the worst day ever☹️<br />The project I had been working on for the last two weeks got corrupted, and everything was lost. Just like that, my SaaS was gone. Two weeks of hard work, completely ruined.<br />But!!!<br />I started from scratch and have already completed 50% of the work…</p>&mdash; CC Anuj (@vid_anuj) <a href="https://twitter.com/vid_anuj/status/1902379748501880934?ref_src=twsrc%5Etfw">March 19, 2025</a></blockquote>
<script async src="https://platform.twitter.com/widgets.js" charSet="utf-8"></script>

### 用 goose 更好地 Vibe Code

[goose](https://goose-docs.ai) 是一个开源 AI agent，运行在你本机上，内置了安全 vibe coding 所需的功能。

:::note
大多数人把「vibe coding」定义为完全混乱、毫无规则的开发。我把它重新定义为：与 AI 一起顺势而为，同时保护你的项目、团队和未来的自己。
:::

#### 1. 制定计划

goose 的 `/plan` 命令帮助你在动任何代码之前就与你的 agent 对齐，让你清楚理解它打算做什么、以及打算怎么做。

这对跨多个文件、涉及副作用，或可能影响代码库关键区域的任务尤其有用。不用再靠猜——你会得到一份结构化的分解，可以审阅并批准。

#### 2. 为任务选择合适的模式

虽然让 AI agent 主导很有趣，但并非每个时刻都需要完全自主。有时，你需要先暂停、审阅或规划，再改动任何代码。goose 提供了多种[模式](https://goose-docs.ai/docs/guides/managing-tools/goose-permissions)，帮助你在不打断节奏的情况下保持掌控。下面是在会话中如何有意识地使用它们：

* **Chat Mode（聊天模式）**
  goose 只会用文本回复，方便你们一起头脑风暴。

* **Approval Mode（审批模式）**
  goose 在执行动作前会征求你的批准。当你想保持快速构建、又想在事情发生前知道将要发生什么时，这很有用。

* **Smart Approval（智能审批）**
  在这种模式下，goose 会针对有风险的动作请求你的批准。这种模式适合在保留护栏的同时快速做原型。

* **Autonomous Mode（自主模式）**
  在这种模式下，goose 无需请求批准便继续推进。如果你对方向有信心、并且已经设好安全网，最好使用这种模式。

#### 3. 虔诚地使用版本控制

有些时候，AI agent 改动的文件和行数太多，Control + Z 根本救不回来。最好为你或 goose 所做的每一次改动都提交，以获得恢复点、清晰的 diff 和快速回滚的能力。

#### 4. 提问并批判性思考

即使你在 vibe coding，也别关掉大脑。

向 goose 提问：

* 你为什么做这个改动？
* 这样安全吗？
* 我们是如何处理密钥的？
* 这是组织数据库的最佳方式吗？

通过推动你的 agent 自我解释，你会构建出更好的产品，并在此过程中学到更多。

#### 5. 定义 .goosehints 以获得更好的上下文

[.goosehints](https://block.github.io/goose/docs/guides/context-engineering/using-goosehints) 文件为 goose 提供关于你项目编码规范、架构偏好和安全实践的额外上下文。

这里有几个例子：

* 「绝不暴露 API 密钥。」
* 「数据库查询使用预编译语句。」
* 「避免使用 eval 或不安全的动态代码。」

#### 6. 把 goose 集成进你的 CI/CD

在问题进入生产环境之前，把 [goose 加入你的 CI/CD 流水线](https://block.github.io/goose/docs/tutorials/cicd)，以便：
- 自动化代码审查
- 校验文档
- 运行安全检查

#### 7. 使用白名单阻止不安全的 MCP 服务器

有些 MCP 服务器可能引入安全风险，尤其是被入侵时。

使用 goose 的[白名单](https://github.com/aaif-goose/goose/blob/main/crates/goose-server/ALLOWLIST.md)功能，阻止 goose 调用不安全或不受信任的工具。

以下是 Block 团队对[保护 MCP](https://block.github.io/goose/blog/2025/03/31/securing-mcp) 的思考。

#### 8. 选择高性能的 LLM

并非所有 LLM 都一样。goose 与以下模型配合最佳：

* Claude Sonnet 3.5
* GPT-4o

性能较低的模型也许能用，但它们更可能产生幻觉或误解你的目标。阅读更多关于[不同 LLM 与 goose 配合表现](https://goose-docs.ai/blog/2025/03/31/goose-benchmark/)的内容。

### 观看 Vibe Coding 实战

下面是大家如何用 goose 进行 vibe coding：

<iframe width="560" height="315" src="https://www.youtube.com/embed/xZo3aA-vFi4?si=14bVczrCUwdKBZyg" title="The Great goose Off" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### 最后感想

Vibe coding 本身并没有错。它标志着我们构建方式的新篇章，为每个人打开了大门。但有经验的开发者有责任去定义什么是明智、安全的 vibe coding。goose 给了我们设定这一标准的工具，让整个社区都能在不牺牲质量的前提下创造性地编码。

下载 [goose](https://goose-docs.ai/docs/getting-started/installation/)，今天就开始有意识地进行 vibe coding 吧！

<head>
  <meta property="og:title" content="How to Vibe Code Responsibly (with goose)" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/04/08/vibe-code-responsibly" />
  <meta property="og:description" content="Vibe coding feels magical until it isn't. Learn how to flow with goose while protecting your code, your team, and your future self." />
  <meta property="og:image" content="http://goose-docs.ai/assets/images/responsible-vibe-code-a77f5e24a879edda943cc76f1fc0bd2a.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="How to Vibe Code Responsibly (with goose)" />
  <meta property="twitter:description" content="Vibe coding feels magical until it isn't. Learn how to flow with goose while protecting your code, your team, and your future self." />
  <meta property="twitter:image" content="http://goose-docs.ai/assets/images/responsible-vibe-code-a77f5e24a879edda943cc76f1fc0bd2a.png" />
</head>

---

## MCP 生态系统的可视化指南

> 原文：https://block.github.io/goose/blog/2025-04-10-visual-guide-mcp

![博客封面](mcpblog.png)

你有没有过这样的经历：打开一个 GitHub 仓库或博客文章，读了第一句话就立刻觉得自己误入了一篇博士论文？

嗯。我也是。

MCP（Model Context Protocol）听起来很复杂，但其实一点也不。把本文当成你的随身速查表吧，没有白皮书，没有学术黑话，只有大白话和几张好图。
<!--truncate-->

让我们一起来拆解它。

### 用大白话解释 MCP 是什么？

MCP 就像你的 AI agent（比如 Goose）与外部工具、文件、数据库、API 之间的万能翻译器，诸如此类。

它让你的 agent 有能力提问、运行工具、存储/检索上下文，并追踪它所知道的一切。

MCP 不必像以前那样把所有东西都塞进一个提示词里——「这里是价值 1 万个 token 的上下文，祝你好运」——而是帮助模型在需要的时候、拉取它所需要的东西。

### 都有哪些角色？

![角色](players.png)

- **User（用户）** – 你，那个满怀大创意、也揣着一堆烂摊子问题的人

- **Agent（智能体）** – 那个住在你的 CLI、IDE 或桌面应用里的 AI agent，也就是 Goose

- **LLM** – 负责推理的模型（比如 Claude、GPT-4 等）

- **MCP Servers (Extensions)（MCP 服务器/扩展）** – Goose 的工具箱：内置的和自定义的扩展，让 goose 有能力执行任务

### 它们如何通信？

我们来看看所有角色是如何协同工作的：

![可视化指南](visualguide.png)
在这个流程中，用户先给 Goose 一个提示词，从而启动整个过程。Goose 把提示词准备好，连同它可用的工具和任何相关上下文，一起交给 LLM。LLM 决定完成任务需要哪些工具。接着 Goose 把这些工具调用路由到对应的 MCP 服务器，由它们执行任务。随着任务各步骤被完成，它会告知你（用户）已经做了什么，并且可以根据需要与 LLM 反复循环。

### 来个类比

让我们用一个詹姆斯·邦德的类比把这件事说得更清楚。有时候一个故事就能让人豁然开朗。

![詹姆斯·邦德](james.png)

如果你看过詹姆斯·邦德电影，你一定知道这个场景：
邦德在执行任务前走进 Q 的实验室。
Q 打开装满小玩意的公文包，爆炸笔、隐形车、抓钩手表，应有尽有。

在这个情境里，Goose *就像* Q。
公文包早已装满了工具——内置的和自定义的扩展（MCP 服务器）。

在 LLM（邦德）开始任务前，Goose 会给它完整的简报：

>_"这是你的目标（提示词）。这是你的小玩意公文包（你可以使用的扩展）。祝你好运。"_

那 MCP 服务器呢？

它们是幕后那支隐藏的团队，真正在打造这些小玩意，并在邦德在实地需要时把它们递过去。

LLM（邦德）为任务挑选合适的小玩意，Goose 把请求路由到正确的 MCP 服务器，MCP 确保它们能用，整个行动便顺利运转。

如果没有 Goose 递上那个小玩意公文包，模型只能穿着一身燕尾服、带着一个微笑出现在现场，而我们并不想知道那会是什么下场。

### 轮到你了

现在你已经掌握了基础，也理解了 MCP 生态系统如何运作，是时候自己试一试了。

[快速上手指南](https://block.github.io/goose/docs/quickstart)会带你连接你的第一个 MCP 服务器。

当你准备好探索更多时，去看看文档里的[教程板块](https://block.github.io/goose/docs/category/tutorials)——那里有分步指南和短视频演示，向你展示如何连接各种各样的 MCP 服务器。

别忘了[加入社区](https://discord.gg/n8R5VaWDAn)，看看别人在构建什么、提提问题，或者只是来认识认识。

<head>
  <meta property="og:title" content="A Visual Guide To MCPs" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/04/10/visual-guide-mcp" />
  <meta property="og:description" content="Visual breakdown of MCP: How your agent, tools, and models work together." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/mcpblog-40894789122bda594a8576ebcb67a2d8.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="A Visual Guide To MCPs" />
  <meta property="twitter:description" content="Visual breakdown of MCP: How your agent, tools, and models work together." />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/mcpblog-40894789122bda594a8576ebcb67a2d8.png" />
</head>

---

## 为工具调用微调 Toolshim 模型

> 原文：https://block.github.io/goose/blog/2025-04-11-finetuning-toolshim

![博客封面](toolshim-header.png)

我们最近发布的 [Goose 基准测试](https://goose-docs.ai/blog/2025/03/31/goose-benchmark)揭示了在那些并不直接支持工具调用的模型（例如 Gemma3、Deepseek-r1、phi4）中存在显著的性能局限。这些模型往往无法在恰当的时机调用工具，或者产生格式错误、格式不一致的工具调用。随着 Llama4 和 Deepseek v3（0324）最新版本的发布，我们再次在这些旗舰级开放权重模型上观察到有效工具调用性能方面的挑战。

<!--truncate-->

### 为什么工具调用很重要

工具调用是 goose 这类 agent 的关键能力。它让模型能够超越文本和图像生成，采取具体行动，比如执行代码、查询数据库、搜索网络，或与 Figma 这类设计工具交互。为 agent 配备广泛的工具，能让它们像人类一样去发现并对接外部系统。对于范围狭窄、更确定性的 LLM 应用来说，这也许是杀鸡用牛刀，但对于 goose 这类通用 agent 而言，它是必不可少的。没有可靠的工具调用，我们就限制了模型在帮我们自动化、消除繁琐工作、驾驭复杂系统方面所能做的事。纯粹的生成——文本、图像、语音和视频——只是通往更强大 agentic 能力之路的第一步。如果我们给模型装上能奔跑的双腿，它们能做的还有太多太多。

### 背景：使用本地模型作为「toolshim」

我们的目标是让 goose 尽可能与最多种类的模型协作。这里的「toolshim」是一个薄层，位于执行 agent 工作的主模型与那些能执行实际动作的工具之间（让 agent 采取行动，而不是当一个聊天机器人）。此前我们一直在开放模型上尝试这种方法，包括在[上一篇基准测试](https://goose-docs.ai/blog/2025/03/31/goose-benchmark)文章中。toolshim 如果可行，就能同时释放出两类模型的潜力：一类是强大的前沿模型（开放权重和闭源），它们虽在各种基准上表现良好，但在 agent 需要工具调用时却远不达标（或者也许按设计压根不支持工具调用，某些推理模型就是如此）。

### 提案：微调一个轻量级 toolshim 模型（最高 12b）

开发一个专用的 toolshim 模型，把开源模型的输出翻译成结构良好的工具调用，充当一个可靠的后处理器，以在那些当前工具调用生成行为不一致、不可靠的模型家族之间进行标准化。即使可用，我们也不使用工具调用 API，而是在系统提示词中提供工具上下文。

我们已经在[基准测试工作](https://goose-docs.ai/blog/2025/03/31/goose-benchmark)中做过这一实验，发现当使用一个通用的本地模型（mistral-nemo）作为 shim 时，phi4（14b）和 gemma3（27b）达到了接近 llama3.3（70b）的性能。这表明，如果更专注地改进 shim 的性能，这些模型还有进一步提升表现的潜力。

Toolshim 系统草图：

![Toolshim 系统草图](https://block.github.io/goose/img/sketch.png

### 关于当前工具调用生成挑战的关键观察

1. **模型训练模板不一致**
   例如，[Qwen 模型使用](https://qwen.readthedocs.io/en/latest/framework/function_call.html)[Hermes 风格的工具格式](https://github.com/NousResearch/Hermes-Function-Calling)，而 Openhands 尽管有明确的 JSON 指令，却仍生成 Markdown——这表明训练数据的形态对可靠的工具调用生成的影响可能被低估了

2. **当前的变通办法还不够**
   [模型提供方可能会采用引导式解码之类的方法](https://docs.vllm.ai/en/latest/features/tool_calling.html)来保证函数调用可被合法解析，但如果模型没有在匹配用户上下文中提供的 schema 上训练过，这些方法可能无法产出高质量的输出。Llama4 在工具使用上普遍存在的挑战，也许正说明提供方在有效服务新模型、充分发挥其能力方面所面临的困难

3. **托管提供方在处理工具调用上的表现千差万别**
   托管提供方会贴心地提供聊天模板之类的东西，在很多情况下能促使一些较大的模型正确格式化地回复工具调用，从而可以支持提供工具的类 OpenAI API；但在实践中，这些方案可能在一次之后就掉链子，或者在不同提供方之间差异极大（如果使用 openrouter 或 huggingface 托管推理之类的模型路由服务，这个问题会更加严重）

#### 关于工具调用的一些模型特定怪癖示例：

**Openhands**：尽管有生成 JSON 格式工具调用的指令，仍然生成 markdown（很可能是其训练数据形态所致）

![Openhands 示例](https://block.github.io/goose/img/openhands.png

**Llama4 Maverick**：会生成格式错误的工具调用，但当被明确要求以 JSON 生成工具调用时，表现会稍好一些

在 OpenRouter 上使用「tool calls」时：
![OpenRouter 工具调用示例](https://block.github.io/goose/img/openrouter_toolcalls.png

Llama4 Maverick 改为直接被要求以 JSON 生成工具调用时：
![Llama4 示例](https://block.github.io/goose/img/llama4.png

**Gemma3**：一位 DeepMind 工程师[建议在上下文中以 Python 格式提供函数调用模板](https://www.philschmid.de/gemma-function-calling)
这个 12B 模型也能相当不错地输出合法的 JSON 工具调用：
![Gemma3 示例](https://block.github.io/goose/img/gemma3.png

**Functionary 模型**：[Ollama 无法支持其工具调用能力](https://github.com/MeetKai/functionary/issues/302#issuecomment-2650187280)，因为这些模型是用 TypeScript schema 的提示词模板训练的，与 Ollama 支持的 JSON schema 不兼容

### 实验方法

#### 数据收集

* 从历史 Goose 会话中抽取用户消息，并针对那些后面跟着来自 Anthropic/OpenAI 的工具调用的消息（截至今天的全部工具调用）：
  * **用开放模型重新生成工具调用：** 用最具能力、且支持工具调用能力的开放模型（例如 QwQ、Qwen、deepseek chat v3）重新生成工具调用
  * **生成 json/markdown 格式的工具调用来解析：** 指示那些最具能力、但未必有强工具调用能力的开放模型（例如 DeepSeek-r1、Llama4、Gemma3）按正确的 schema（JSON/markdown）输出工具调用。把输出解析成相应的工具调用。
  * **丢弃任何格式错误的工具调用、未能正确执行的工具调用，或满足其他拒绝标准的工具调用**
* 用这种方法生成几千个示例

#### 建模

微调小模型，比如 mistral-nemo（14b）、gemma 4-12b、qwen2.5-coder 7-14b。

#### 评估

用基准测试博客文章中运行的 Goosebench 评测来测试。我们可以直接比较有和没有微调过的 toolshim 模型支持时，各模型的性能。

### 未来方向

在本地模型之外，我们还想考虑解析器、解析器组合子、上下文无关文法等等（甚至是规模非常大的那种），它们基于成千上万个工具结果示例来构建。即便规模很大，它们也能以极低的延迟运行，为建议的工具调用提取参数。很可能还有其他结构化文本抽取技术值得探索，以帮助从强大通用模型产出的丰富响应中发现并抽取工具调用。

<head>
  <meta property="og:title" content="Finetuning Toolshim Models for Tool Calling" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/04/11/finetuning-toolshim" />
  <meta property="og:description" content="Addressing performance limitations in models without native tool calling support" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/toolshim-header-42611f614e7722f90cf83991debe3046.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Finetuning Toolshim Models for Tool Calling" />
  <meta property="twitter:description" content="Addressing performance limitations in models without native tool calling support" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/toolshim-header-42611f614e7722f90cf83991debe3046.png" />
</head>

---

## ATrueLight4 如何帮助 Goose 适配 Windows

> 原文：https://block.github.io/goose/blog/2025-04-14-community-atruelight4

![博客封面](goose4win.png)

随着 goose 团队持续开发新功能，超过 800 名社区成员投票表达了他们需要 Windows 版 Goose。今天要介绍的顶级贡献者挺身而出，助力这项持续推进的工作。

<!--truncate-->

### Windows 支持

自 codename goose 发布以来，开源社区一直渴望并请求 goose 在 Windows 上提供同样的自动化能力。

目前，goose 的 CLI 版本可以在 Windows 上运行，但只能通过 WSL（Windows Subsystem for Linux，适用于 Linux 的 Windows 子系统）使用有限的内置扩展。虽然内部正在筹备一个有限的内测版本，但仍有若干 bug 和改进项正在处理中，以确保 codename goose 在 Windows 上拥有和在 Mac 上一样无缝的体验。

### ATrueLight4 的 Goose4Win

我们本期重点介绍的贡献者是 [ATrueLight4](https://github.com/ATrueLight4)，他提交了 **Goose4Win**，一项改进 Goose 处理 Windows 专属文件路径方式的修复。他的贡献已经合并进 main，所以如果你今天在 Windows 上安装 CLI 版 Goose，就能开箱即用地获得这一改进，无需额外设置。

非常感谢你的贡献，ATrueLight4！你的工作让我们离「Goose on Windows」更近了一步。

为了表达我们对你贡献的深深谢意，我们已经在 Block 开源 Discord 上授予你专属的 ✨Top Contributor✨（顶级贡献者）徽章！你还将成为首批获得 codename goose 专属周边纪念品的贡献者之一。（更多详情稍后公布 👀🪿）

### 争取你自己的高光时刻

有兴趣为 goose 做贡献、并让你的贡献被重点介绍吗？无论是改进平台支持、添加新功能，还是修复 bug，我们都欢迎来自开源社区的一切贡献。你可以[加入 Block 开源 Discord](https://discord.gg/n8R5VaWDAn)，或[立即开始使用 codename goose](https://goose-docs.ai/)。

<head>
  <meta property="og:title" content="How ATrueLight4 Helped Goose Navigate Windows" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/04/14/community-atruelight4" />
  <meta property="og:description" content="Block Open Source Top Contributor of the Month" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/goose4win-7f57433fa3f19849e74b18ebffe08bcf.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="How ATrueLight4 Helped Goose Navigate Windows" />
  <meta property="twitter:description" content="Block Open Source Top Contributor of the Month" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/goose4win-7f57433fa3f19849e74b18ebffe08bcf.png" />
</head>

---

## Codename Goose 登陆纽约

> 原文：https://block.github.io/goose/blog/2025-04-17-goose-goes-to-NY

![博客封面](cover.png)

我们把 Goose 带到了纽约市，这次活动堪称经典。

超过 100 人报名，还有 87 人在候补名单上，我们的会场座无虚席，挤满了好奇、深思、准备大展身手的人们。有些人已经在探索 Goose 和 MCP，另一些人则对 AI agent 的世界完全陌生。这就是 Goose 的美妙之处，它既面向开发者*也*面向非开发者。

活动一开始气氛就拉满了——音乐、披萨和真诚的社交。我们做了闪电演讲、玩了一个 Goose 主题的游戏、进行动手 hacking，而且……到当晚结束时，大概有几罐 Ebbs IPA 悄悄进了大家的背包。

<!--truncate-->

### 我们为什么把 Goose 带到纽约

波士顿聚会之后，我们想保持这股势头，并在一个新城市试试水。纽约感觉是绝佳的选择。它是一个人群的大熔炉，科技氛围也非常浓厚。我们的目标很简单：

✅ 持续建设 Goose 社区
✅ 线下从社区获得真实的反馈和想法
✅ 一起学习的同时也玩得开心

纽约没有让我们失望。

### 万一你错过了

<ImageCarousel id="test-carousel" images={[focus5,focus, focus2, focus3, focus4]} />

我们先以美食和自由交流开场，让大家在进入演讲环节前认识彼此、聊天、提问：

- 来自 Galileo 的 **[Erin Mikail](https://www.linkedin.com/in/erinmikail/)** 主持了一个 Goose 主题的游戏，让人们在欢笑*和*学习中理解了 agent 评估的重要性。
- **[我，Ebony Louis](https://www.linkedin.com/in/ebonylouis/)** 做了一场 Goose 和 MCP 的讲解，展示了上手任意 MCP 服务器有多快。
- **[Alex Hancock](https://www.linkedin.com/in/alexjhancock/)** 深入讲解了 MCP，以及它如何驱动安全、可扩展的 agent 工作流。

接着就是最精彩的部分——hack 时间。**27 人在活动现场把 Goose 跑了起来**，这太令人惊叹了。看着某个人突然开窍的那一刻总是很有趣：想法开始涌现，人们受到启发，然后带着准备真正*使用* Goose 的状态离开。

### 大家怎么说

<ImageCarousel id="test-carousel" images={[swag, swag1, swag2, swag3]} />

> 「我花了不到 5 分钟就在 GitHub Codespaces 里搭好了一个示例项目并跑起了 Goose CLI！总的来说，能回到线下场地参加一场动手实操活动，和一个积极参与的社区、一个恰逢其时的话题在一起，感觉太棒了。」
> —— *[Nitya Narasimhan，微软高级云布道师](https://www.linkedin.com/in/nityan/)*

> 「现场演示、开放讨论和实操练习让它成为一次非凡的学习体验。我感到充满能量和启发，很想探索如何在未来的数据工程项目中利用 Goose 和 MCP！」
> —— *[Manikumarreddy Gajjela，Tetra Computing 全栈开发者](https://www.linkedin.com/in/manireddy12/)*

> 「如今大家似乎都看好 Model Context Protocol (MCP)……Goose 是一个开源、运行在本机的 AI agent，用来自动化你的任务。最酷的是？你甚至可以把你自己托管的 Ollama LLM 接进 Goose！」
> —— *[Rijul Dahiya，纽约大学研究生助教](https://www.linkedin.com/in/rijuldahiya/)*

> 「很棒的活动——入门性和技术性内容搭配得当，还很有趣，我很喜欢它在开头和结尾都留出了大量非结构化的时间。」
> —— *[Matthew Hill，Dataminr AI 工程高级总监](https://www.linkedin.com/in/matthewhillnewyork/)*

### 我们喜欢的瞬间 ❤️

- 🍕 活动还没开始，披萨、音乐和人们就已经聊开了
- 🎮 那个 Goose 游戏——是的，它变得很有竞争性，还莫名有点黑暗 lol
- 🧳 有人专程从费城和华盛顿赶来参加
- 📸 有摄影师捕捉真实又有趣的瞬间
- 🧠 一堆深思熟虑的「我不是开发者，但是……」问题，我们*超爱*听到这些

<ImageCarousel id="test-carousel" images={[speaker1,speaker, fun, fun1, focus2]} />

最后，人们在问下一场是什么时候，是的，我们可能不小心提前透露了一点……

### 下一站：Goose 南下 🛫

我们的下一场 Goose Meetup 已经定下来了！

👉 **亚特兰大 – 4 月 30 日，星期三**
🕕 **美东时间 下午 6:00 – 8:30**
📍 [在此报名](https://lu.ma/x9ccqruq)

### 衷心感谢 🙌

特别感谢 **[Tania Chakraborty](https://www.linkedin.com/in/taniachakraborty/)** 和 **[Anthony Giuliano](https://www.linkedin.com/in/anthonygiuliano1/)** 的到场，也感谢每一位前来、提问、帮忙，让这个夜晚令人难忘的人。

是社区真正让这一次变得特别：人们留下来继续聊天，没被要求就主动帮忙清理，还把这么好的能量带进了会场。我们不可能再奢求更好的参与者了。

亚特兰大见 👀

<head>
  <meta property="og:title" content="Codename Goose Goes to New York" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/04/17/goose-goes-to-NY" />
  <meta property="og:description" content="Goose lands in NYC for its second community meetup" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/cover-6c131d275bcdb4d8651a140d62e2975f.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Codename Goose Goes to New York" />
  <meta property="twitter:description" content="Goose lands in NYC for its second community meetup" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/cover-6c131d275bcdb4d8651a140d62e2975f.png" />
</head>

---

## MCP 在企业中：Block 的真实落地实践

> 原文：https://block.github.io/goose/blog/2025-04-21-mcp-in-enterprise

![博客封面](mcp-for-enterprise.png)

在 Block，我们一直在探索如何让 AI agent 在商业环境中真正有用。不只是用于演示或原型，而是用于真实、日常的工作。
作为 [Model Context Protocol (MCP)](https://www.anthropic.com/news/model-context-protocol) 的早期协作者之一，我们与 Anthropic 合作，帮助塑造并定义了这座连接 AI agent 与真实世界工具和数据的开放标准。

MCP 让 AI agent 通过一套通用接口与 API、工具和数据系统交互。它通过暴露确定性的工具定义来消除猜测，这样 agent 就不必猜如何调用某个 API。
相反，它专注于我们真正想要的东西……结果！

当别人还在试验时，我们已经把它推广到了 Block 全公司，并产生了真实的影响。

<!--truncate-->

### 我们为什么在 Block 选择 MCP

我们不想做一次性的集成，也不想把 AI 硬绑进某个特定的供应商生态。
和大多数企业一样，我们的需求横跨工程、设计、安全、合规、客户支持、销售等等。
我们想要的是灵活性。

MCP 给了我们这一点。
它与模型无关、与工具无关，让我们的 AI agent 能够通过同一套协议与内部 API、开源工具，乃至现成的 SaaS 产品交互。

它也与我们的[安全理念](https://block.github.io/goose/blog/2025/03/31/securing-mcp)高度契合。
MCP 让我们能够定义哪些模型可以调用哪些工具，并允许我们把工具标注为「只读」或「破坏性」，以便在必要时要求用户确认。

### 我们如何配置和保护 MCP

我们开发了 [**Goose**](https://block.github.io/goose/)，一个开源、兼容 MCP 的 AI agent。每天有数千名 Block 员工使用这个工具。
Goose 同时提供 CLI 和桌面应用，默认可以访问一组经过精心筛选、获得批准的 MCP 服务器。
大多数员工反馈，在常见任务上节省了 50–75% 的时间，还有几位分享说，过去需要几天的工作现在几个小时就能完成。

为确保安全可靠的体验，内部使用的所有 MCP 服务器都由我们自己的工程师编写。
这让我们能够针对自己的系统和用例（从开发工具到合规工作流）定制每一个集成。

我们使用最广泛的一些 MCP 包括：

- **Snowflake**，用于查询内部数据
- **GitHub 和 Jira**，用于软件开发工作流
- **Slack 和 Google Drive**，用于信息收集和任务协调
- **内部 API**，用于合规检查和工单分诊等专门用例

除了工具访问，Goose 还依赖大语言模型（LLM）来理解提示词并规划行动。
我们使用 Databricks 作为 LLM 托管平台，让 Goose 能通过安全、由企业管理端点与 Claude 和 OpenAI 模型交互。
我们已经与模型提供方建立了企业协议，其中包含数据使用保护条款，并且按照内部政策，我们限制 Goose 被用于某些类别的敏感数据。

在服务级授权方面，我们使用 OAuth 来安全地分发 token。
Goose 已预配置好与常用服务进行身份验证，token 使用系统原生钥匙串安全存储。
目前，OAuth 流程直接实现在本地运行的 MCP 服务器中，这是一个务实但临时的方案。
我们正在积极探索未来更具可扩展性、更解耦的模式。

此外，一些服务器会强制执行 LLM 白名单，或限制工具输出跨系统共享，以进一步降低数据暴露风险。

### 真实的故事，真实的影响

Goose 已经成为 Block 各团队的日常工具。
MCP 服务器充当灵活的连接器，员工们正以越来越有创意、越来越实用的方式使用自动化，来消除瓶颈、专注于更高价值的工作。

我们的工程师正在使用由 MCP 驱动的工具来迁移遗留代码库、重构并简化复杂逻辑、生成单元测试、简化依赖升级，并加速分诊工作流。
Goose 帮助开发者跨陌生系统工作、减少重复性编码任务，并比传统方式更快地交付改进。

数据和运营团队正在使用 Goose 查询内部系统、汇总大型数据集、自动化报告，并从多个来源中提炼相关上下文。
在很多情况下，这减少了对人工拉取数据或与专家进行冗长来回沟通的依赖，让洞察对每个人都更易获取。

与此同时，设计、产品、支持和风险团队也在以各种方式使用 Goose，减轻日常工作负担。
无论是生成文档、分诊工单，还是制作原型，基于 MCP 的工作流都证明其适应性远超工程领域。

这一转变正在帮助我们消除拖慢脚步的机械性工作。
随着越来越多团队进行试验，他们发现了与 Goose 协作的新方式，并重塑了事情的完成方式。

### 到目前为止我们学到了什么

在全公司推广 MCP 工具不仅仅是技术上的搭建。我们投入了：

- 预装的 agent 访问权限和默认服务器捆绑包
- 来自内部开发者关系团队的每周培训
- 内部沟通渠道，用于求助以及分享和庆祝成果

我们的一些心得：

- 我们把上手做得越简单——预装 Goose、捆绑 MCP、自动配置模型——采用速度就越快
- 人们一旦看到可能性就会变得更有创意，尤其是当他们能对别人已经做过的东西进行改造或在其基础上构建时
- 集中式的上手引导和提示词共享能节省时间，并帮助推广最佳实践

### 接下来

我们正在继续把用例扩展到传统工程团队之外。MCP 正在帮助打通市场、销售和支持工作流，而我们才刚刚开始。

我们还在投入于：

- 更安全的默认设置，以及基于上下文的工具限制
- 面向高风险操作的人在环路（human-in-the-loop）功能
- 鼓励公司各部门为开源 MCP 做贡献

### 想了解更多？

如果你对 Goose 或 MCP 感兴趣，可以看看 [Goose 文档](https://block.github.io/goose/docs/quickstart)或 [MCP 规范](https://spec.modelcontextprotocol.io/)。
我们很想听听其他人在大规模 AI 自动化方面是如何做的。

<div style={{display: 'none'}}>

![](mcp-for-enterprise-social.png)

</div>

<head>
  <meta property="og:title" content="MCP in the Enterprise: Real World Adoption at Block" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai//blog/2025/04/21/mcp-in-enterprise" />
  <meta property="og:description" content="How Block is using MCP to power real world automation company-wide." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/mcp-for-enterprise-social-bb8a18872fedc0046ef72bb413dea851.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="MCP in the Enterprise: Real World Adoption at Block" />
  <meta property="twitter:description" content="How Block is using MCP to power real world automation company-wide." />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/mcp-for-enterprise-social-bb8a18872fedc0046ef72bb413dea851.png" />
</head>

---

## 我在不丢失真实感的前提下使用 AI Agent 的 11 种实用方式

> 原文：https://block.github.io/goose/blog/2025-04-21-practical-use-cases-of-ai

![MCP 用例](mcp-use-cases.png)

「别再使用 AI 了」，又一篇爆款帖子这么写道。我懂。审阅同事自动生成的工作成果确实令人沮丧，里面满是 AI 的经典破绽，比如千篇一律的代码注释，以及「在当今快节奏的世界里……」这类套话。

尽管如此，AI 在我的职业生涯中仍扮演着关键角色。我不依赖 AI 替我完成工作，而是用它来帮我头脑风暴、提高效率。
[Model Context Protocol (MCP)](https://modelcontextprotocol.io) 的出现让这一切变得更加容易。MCP 是一种开放标准，它给 AI 工具提供在真实世界中发挥作用所需的上下文。它让 AI agent 能够以结构化的方式与 API、应用和系统交互。我使用的是 [Codename goose](https://block.github.io/goose/)，一个基于 MCP 构建的开源 AI agent。

以下是我在不牺牲真实感、创造力或质量的前提下使用 AI Agent 的 11 种真实方式：

<!--truncate-->

### 1. 🙌🏿 免手编码

#### 用例

我不打字，而是对着 Goose 说话，用我的声音作为输入来写代码或运行任务。

#### 为什么有用

我经常有「脑子有想法，但双手腾不开」的时刻。无论是给宝宝喂奶，还是腕管综合征恢复期，这都为我提供了一种不用打字就能记录想法的无障碍方式。

题外话：我在一次聚会上遇到一位 AI 爱好者，他说自己有时开车时会产生编码灵感。他正在探索用语音在路上进行 vibe coding。大家注意安全，别边开车边编码！🚗⛑️

#### 如何尝试

1. 参照[这篇教程](https://block.github.io/goose/docs/mcp/speech-mcp)
2. 启用 [`Speech`](https://github.com/Kvadratni/speech-mcp) 和 [`Developer`](https://block.github.io/goose/extensions/detail?id=developer) 扩展
3. 向 Goose 提示：
    > I'd like to speak instead of typing.

<iframe class="aspect-ratio" src="https://www.youtube.com/embed/rurAp_WzOiY" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

### 2. 🎤 准备播客议程

#### 用例

我把嘉宾一次大会演讲的 YouTube 视频交给 Goose。然后，我让 Goose 生成字幕并构思出有深度的访谈问题。

#### 为什么有用

我希望嘉宾感觉我确实了解他们的工作，哪怕我没有几个小时来准备。这让我能提出更聪明的问题，把节目做得更好。

#### 如何尝试

1. 参照[这篇教程](https://block.github.io/goose/docs/mcp/youtube-transcript-mcp)
2. 启用 [`YouTube Transcript`](https://github.com/jkawamoto/mcp-youtube-transcript) 和 [`Developer`](https://block.github.io/goose/extensions/detail?id=developer) 扩展
3. 向 Goose 提示：
   > Generate a transcript for this video https://www.youtube.com/watch?v=dQw4w9WgXcQ, then create relevant interview questions based on the content

---

### 3. 🖼 调整图片尺寸

#### 用例

演讲者管理平台对头像图片的要求往往各不相同。过去我会花多到令人尴尬的时间，试图在不破坏宽高比的情况下调整照片尺寸。现在，我直接让 Goose 来做。

#### 为什么有用

它让我不必再跟各种随机在线工具或臃肿的设计应用较劲。几秒钟内我就能得到一张干净、尺寸正确的图片，而且看起来完全符合我的期望。

#### 如何尝试

1. 启用 [`Developer`](https://block.github.io/goose/extensions/detail?id=developer) 扩展
2. 向 Goose 提示：
   > Resize this image (~/Downloads/image.png) to 1000x1000 pixels. Maintain the aspect ratio and image quality.

---

### 4. 📝 对照职位列表审阅简历

#### 用例

我用 Goose 把我当前的简历和我看到的职位列表做了对比。

#### 为什么有用

我目前并没有在找工作，但我喜欢保持有备无患。我的策略是让简历保持最新、有竞争力。我会把当前简历和职位列表对比，但现在我不必再手动去做了。相反，Goose 能快速指出我在特定职位列表上的优势和不足。这种方法也能帮招聘经理更快地审阅简历。

#### 如何尝试

1. 参照[这篇教程](https://block.github.io/goose/docs/mcp/pdf-mcp)
2. 启用 [`PDF Reader`](https://github.com/michaelneale/mcp-read-pdf) 扩展
3. 向 Goose 提示：
   > Read the resume at ~/Downloads/resume.pdf and evaluate how well this candidate aligns with the following role requirements:
   >   - 5+ years of backend development experience
   >   - Strong system design and distributed systems knowledge
   >   - Cloud infrastructure experience (AWS preferred)
   >   - Prior experience leading technical projects or teams
   >   - Bonus: familiarity with LLMs or AI/ML tools
   >
   > Score each one out of 5, give supporting evidence, and summarize with a final fit rating.

<iframe class="aspect-ratio" src="https://www.youtube.com/embed/EJf2_iZfaWk" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
---

### 5. 🧠 理解习语

#### 用例

我让 Goose 解释我不理解的习语或典故。

#### 为什么有用

因为我不是在美国出生的，而且我是神经多样性人群，我有时会按字面理解习语，或者误解它们。与其冒着在工作中出糗的风险，我会悄悄让 Goose 帮我翻译。

#### 如何尝试

1. 启用 [`Developer`](https://block.github.io/goose/extensions/detail?id=developer) 扩展
2. 向 Goose 提示：
   > What does this phrase mean: "Who does Vegas have as the favorite?"

---

### 6. 📊 查询关系型数据库

#### 用例

我用自然语言向 Goose 询问关于我数据的洞察，它替我写了一个 Common Table Expression（公共表表达式）。

#### 为什么有用

SQL 在涉及 join、存储过程和子查询时会变得很复杂。Goose 通过替我处理查询逻辑，帮我更快推进并避免错误。

#### 如何尝试

1. 参照[这篇教程](https://block.github.io/goose/docs/mcp/postgres-mcp)
2. 启用 [`PostgreSQL`](https://github.com/bytebase/dbhub/) 和 [`Developer`](https://block.github.io/goose/extensions/detail?id=developer) 扩展
3. 向 Goose 提示：
   > Find my top 3 blog posts by average weekly views over the past 90 days. Include title, URL, average weekly views, and whether they were promoted on social.

<iframe class="aspect-ratio" src="https://www.youtube.com/embed/PZlYQ5IthYM" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
---

### 7. 🗓 规划我的大会演讲策略

#### 用例

我用 Goose 分析历年大会数据，以便更聪明地规划即将到来的 CFP 截止日期。

#### 为什么有用

我容易给自己安排过多，或者因为担心不被录用而焦虑，于是什么都申请。结果就是我全都被录用了，又没多想就全答应下来，导致规划混乱、演讲仓促。有了 Goose，我可以分析 CFP 时间线上的规律，做出更有意图的选择。

#### 如何尝试

1. 参照[这篇教程](https://block.github.io/goose/docs/mcp/agentql-mcp)
2. 启用 [`AgentQL`](https://github.com/tinyfish-io/agentql-mcp) 扩展
3. 向 Goose 提示：
   > I'm a tech conference speaker planning my 2025-2026 submissions.
   > Extract for developer conferences (attendance > 500) occurring between 2022-2024:
   > - Conference name
   > - Conference dates
   > - CFP timeline
   >
   > To identify:
   > - Consistent monthly patterns
   > - Whether conferences stick to same months yearly
   > - If CFP windows are consistent year-to-year
   > - Any shifts in traditional timing
   >
   > Structure results as JSON

---

### 8. 🐞 追查引入 bug 的提交

#### 用例

一个功能坏了，但我提交了太多次，没法判断是哪一次引入的 bug。我让 Goose 帮我运行 `git bisect`，这样我们就能定位到有问题的代码。

#### 为什么有用

调试最难的部分往往只是弄清楚该从哪里看起。Git bisect 让这件事更快，而 Goose 带我走完了整个流程，不需要我记住每一步。

#### 如何尝试

1. 安装 [Git CLI](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
2. 启用 [`Developer`](https://block.github.io/goose/extensions/detail?id=developer) 扩展
3. 向 Goose 提示：
   > I don't know when I introduced a bug. Can you walk me through using git bisect to find the commit that caused it?

---

### 9. 👩🏾‍🏫 学习新技术

#### 用例

我喜欢跟上最新的技术。由于 MCP 服务器很流行，我用 Goose 的 tutorial 扩展，一步步走完了构建自己的 MCP 服务器的过程。

#### 为什么有用

除了生成代码，AI agent 还能帮你学习如何写代码。Goose 内置了一个 tutorial 扩展，旨在以动手实操的方式带用户理解技术概念。

#### 如何尝试

1. 参照[这篇教程](https://block.github.io/goose/docs/mcp/tutorial-mcp)
3. 向 Goose 提示：
   > I'd like to learn how to build an extension or MCP server for Goose

---

### 10. 💼 对比法规文档

#### 用例

我自己没有做过这件事，但得知有位社区成员用 Goose 对比法规文档的拟议版本和最终版本，我印象深刻。

#### 为什么有用

法律文档往往冗长且重复。Goose 能突出真正发生变化的内容，帮助用户快速看出更新如何影响合规或义务。

#### 如何尝试

1. 启用 [`Computer Controller`](https://block.github.io/goose/extensions/detail?id=computercontroller) 扩展
2. 向 Goose 提示：
   > Highlight the differences between these two versions of FinCEN's Investment Adviser AML regulations:
   >
   > Proposed version (2015): https://www.federalregister.gov/documents/2015/09/01/2015-21318/anti-money-laundering-program-and-suspicious-activity-report-filing-requirements-for-registered
   > 
   > Final version (2024): https://www.federalregister.gov/documents/2024/09/04/2024-19260/financial-crimes-enforcement-network-anti-money-launderingcountering-the-financing-of-terrorism
   >
   > Focus on key changes in requirements for investment advisers' AML/CFT programs and how they affect compliance obligations.

---

### 11. 🛠 快速制作想法原型

#### 用例

我用 Goose 构建了一个可用的原型，并看到完整的应用实时运行起来。

#### 为什么有用

它快速、可用，让我无需从零开始花几个小时编码，就能验证一个想法是否值得继续。

#### 如何尝试

1. 启用 [`Developer`](https://block.github.io/goose/extensions/detail?id=developer) 扩展
2. 向 Goose 提示：
   > Build a JavaScript webcam app with real-time filters

🎥 **看它实时运行：**
观看 The Great Goose Off，我们挑战 Goose 从零创作有创意的应用，比如：
- 一个 Goose 形状的绘图工具
- 一个刻意混乱的身份验证流程

你会看到想法在一个会话里从提示词变成原型。

<iframe class="aspect-ratio" src="https://www.youtube.com/embed/OsA3qhns7dg" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

---

### 想找更多例子？

这篇博客文章只涵盖了我使用 goose 的一小部分方式。如果你好奇它还能做什么，直接问：

今天你能帮我做的 5 件有用的事是什么？

让 goose 给你惊喜吧。✨

<head>
  <meta property="og:title" content="11 Practical Ways I Use AI Agents Without Losing My Authenticity" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/04/21/practical-use-cases-of-ai" />
  <meta property="og:description" content="From conference planning to prepping podcasts, here's how I use AI Agents built on MCP for everyday tasks." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/mcp-use-cases-758ecc959d6334783257fc9d6329e1f2.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="11 Practical Ways I Use AI Agents Without Losing My Authenticity" />
  <meta property="twitter:description" content="From conference planning to prepping podcasts, here's how I use AI Agents built on MCP for everyday tasks." />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/mcp-use-cases-758ecc959d6334783257fc9d6329e1f2.png" />
</head>

---

## 一次贡献如何激起一连串的成果

> 原文：https://block.github.io/goose/blog/2025-04-22-community-bestcodes

![博客封面](bestcodes.png)

要发现你的贡献能带来多大影响，唯一的办法就是把它提交出去，然后期待最好的结果。有时，一个感觉「只是个小修复」的东西，最终可能重塑一个开源项目，或激发出一个全新的功能。下面就是我们的顶级贡献者之一，如何把一个小的构建修复，变成对 goose 体验的重要改进。

<!--truncate-->

### BestCodes 是如何发现 Goose 的

[BestCodes（又名 William Steele）](https://bestcodes.dev/)最初是在一场 [GitHub Open Source Friday 直播](https://www.youtube.com/watch?v=O-zJJN-TkXc&ab_channel=AngieJones)中发现了 Goose，并决定试一试。当时，Goose 对 Windows/Linux 的支持还很有限（在正式发布之前还有更多工作在进行中）。由于 BestCodes 不是 Mac 用户，他想帮助把支持带到 Linux。经过大量排查，他最终提交了[一个 Debian 构建修复](https://github.com/aaif-goose/goose/pull/2070)，这才让他终于能在 Linux 上开始使用 Goose。

尽管 BestCodes 也曾犹豫这么小的修复是否值得分享，但正是这个「小」贡献，让想要在 Linux 上使用 Goose 的社区成员得以如愿，也给了他继续提交 PR 的动力。他的经历证明，你的贡献有机会帮到某个人，所以你应该分享它！你永远不知道好奇心与开源社区能一起成就什么。

### 积攒势头

BestCodes 继续通过深思熟虑的改进让 Goose 变得更好——从[打磨 UI](https://github.com/aaif-goose/goose/pull/2079)、[优化加载状态](https://github.com/aaif-goose/goose/pull/2079)，到[修复细微 bug](https://github.com/aaif-goose/goose/pull/2279)，让每个人的 Goose 体验都更顺畅。你可以在 GitHub 上查看 [BestCodes 的贡献](https://github.com/aaif-goose/goose/pulls?q=is%3Apr+is%3Aclosed+author%3AThe-Best-Codes)。

非常感谢你持续的支持与贡献，BestCodes！你的工作让我们离在 Windows 和 Linux 上完整的 Goose 体验又近了一步。

为表达我们对你的贡献的感激，我们已经在 Block 开源 Discord 上授予你专属的 ✨Top Contributor✨（顶级贡献者）徽章！此外，你还将收到 codename goose 专属周边纪念品。👀🪿

### 成为顶级贡献者

有兴趣为 goose 做贡献、并让你的成果被重点介绍吗？无论是修复 bug、分享想法，还是帮助他人，开源社区的每一份贡献都有机会帮到某个人。你可以[加入 Block 开源 Discord](https://discord.gg/n8R5VaWDAn)，或[立即开始使用 codename goose](https://goose-docs.ai/)。

<head>
  <meta property="og:title" content="How One Contribution Can Spark Many Wins" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/04/22/community-bestcodes" />
  <meta property="og:description" content="The snowball effect of one contributor's fixes" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/bestcodes-3d6c50de10a2d84def19d515aaea0724.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="How One Contribution Can Spark Many Wins" />
  <meta property="twitter:description" content="The snowball effect of one contributor's small fixes" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/bestcodes-3d6c50de10a2d84def19d515aaea0724.png" />
</head>

---

## MCP 正在改写 API 集成的规则

> 原文：https://block.github.io/goose/blog/2025-04-22-mcp-is-rewriting-the-rules-of-api-integration

![博客封面](cover.png)

作为开发者，我们一直在寻找构建更高效、更可扩展、更智能的应用的方法。多年来，RESTful API 一直是我们连接服务的首选。下面是一些方法，可以帮你把 AI agent 和 MCP 集成进现有的 API 基础设施，让它更智能、更高效、更易维护。

<!--truncate-->

### 引言：你的 API 的智能化演进

2023 年 3 月，OpenAI 宣布了一种更简单地把 ChatGPT 集成进来的方式：使用格式正确的 OpenAPI 规范文件，并在同一个文件里写好细致周到的详细说明。这项公告在开发者社区引起了广泛关注。其业务影响在于，它让开发者和文档撰写者一起协作编写一个巨大的规范文件，为 ChatGPT 提供理解该使用哪个 API、以及如何使用的必要上下文。

没过多久，[AI agent](https://news.microsoft.com/source/features/ai/ai-agents-what-they-are-and-how-theyll-change-the-way-we-work/) 与 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) 结合起来，把这份工作量拆分开来：MCP 可以承载上下文与感知，而你的 API 团队则可以专注于 API 本身。而且这些并非只是渐进式的改进；Agentic AI 与 MCP 的结合，代表着我们连接和交互数据与服务的方式发生了根本性转变。

转向[使用 AI Agent 和 MCP](https://block.github.io/goose/blog/2025/02/17/agentic-ai-mcp/) 这一变化，其影响有可能和 2005 年 REST API 的问世一样巨大。想象这样一个世界：集成更加动态、更具上下文感知能力，所需的手工编码更少。这并非遥远的未来——它已经在发生。这是我们提高生产力、增强应用智能，并最终为用户、客户带来更好体验的机会。

举个例子：假设你的团队想让 AI 在 Square 的电商工作流中处理动态定价调整。如果你能更快地响应市场或库存变化，就可以减少在代码里构建几十甚至几百条动态定价规则的需要。作为开发者的生产力提高了，需要维护的代码也更少了。你可以用更接近口语的方式编写这些规则，而 AI agent 可以通过 MCP 和你的 API 处理剩下的部分。

### 从静态端点到智能交互

#### 当前格局：传统 API 的局限

我们当前的许多系统严重依赖传统 API，比如 RESTful API，它们被设计为静态端点，用特定的结果响应特定的请求。这些 API 虽然一直很好地为我们服务（而且短期内肯定不会消失），但它们也有局限：

- RESTful API 的静态特性让它们更僵化、更难以适应业务变化，并且需要围绕版本管理制定硬性规则来提供兼容性。
- 它们往往需要大量人工工作来定义端点、处理数据转换、管理复杂工作流。这可能导致开发周期变慢、维护开销增加。

**AI 带来的机会在于，利用智能 agent 结合 MCP，创建更具适应性的集成。** 这些 agent 能够理解上下文、发现相关服务，并以比静态 API 调用更动态的方式协商交互。静态 API 仍在使用，但 AI agent 能比「修改调用 API 的代码、解析和校验响应、处理错误」更轻松地驾驭它们。

#### 开发影响：提升生产力，增强用户体验

这种 AI agent 与 MCP 的双重集成，可以给你的开发流程和你构建的应用带来显著的正面影响：

* **开发者生产力：** 通过自动化许多集成任务、减少大量手工编码的需要，AI agent 把我们的时间释放出来，专注于核心应用逻辑与创新。（还有测试。还有安全。还有文档。还有……）
* **客户满意度：** 智能集成能带来更个性化、更灵敏的用户体验。agent 可以促进实时数据分析和上下文感知交互，让我们的应用更智能、更易用。
* **可扩展性：** 随着你的应用增长，管理多个 API 的复杂度可能变得难以承受。[使用多个 AI agent](https://block.github.io/goose/blog/2025/02/21/gooseteam-mcp/) 可以通过动态适应底层服务和流程的变化，来帮助管理这种复杂度。

#### 业务影响：驱动效率与成本节约

从业务角度看，AI agent 与 MCP 的集成可以带来显著的成本节约和效率提升。以下是你可以预期看到改善的一些关键领域：

**示例 ROI 计算（每位开发者）：**

传统 API 开发：
- 添加功能的平均时间：2 周
- 开发者成本：$150/小时
- 假设每周 40 小时：2 周 * 每周 40 小时 * $150/小时 = $12,000

AI Agent 赋能后：
- 添加功能的平均时间：2 天
- 开发者成本：$150/小时
- 假设每天 8 小时：2 天 * 每天 8 小时 * $150/小时 = $2,400

50 个功能的年度节省：（$12,000 - $2,400）* 50 = **每位开发者 $480,000**

这说明采用 AI agent 后，每位开发者在时间和成本上的潜在节省都相当可观。

### 集成 AI 与 MCP：驾驭这一格局

集成 AI agent，尤其是通过 MCP 这样的平台，需要仔细考量。

- 风险管理：MCP 虽然有前景，但仍是一项较新的技术。你的团队需要彻底评估[潜在的安全隐患](https://block.github.io/goose/blog/2025/03/26/mcp-security/)，并在深度集成进关键系统之前，理解该平台的成熟度。
- 为连续性和版本管理做规划：与任何不断演进的技术一样，你需要制定策略，以确保集成的连续性，并管理 AI agent 和 MCP 本身的版本。

#### 分阶段方法：一种务实的集成策略

在你通过 MCP 集成 AI agent 的过程中，一步一个脚印的方法有助于降低风险，并通过反馈高效学习：

**阶段 1：评估（初步探索）**
- 梳理你现有的 API 使用情况，找出可集成的机会
- 考虑 ROI：从小想法开始，随着时间逐步扩大集成力度
- 为采用 AI agent 和 MCP 制定初步的业务/技术计划

**阶段 2：A/B 测试与试点项目**
- 选择一个低风险、高价值的服务，作为通过 MCP 进行 AI agent 集成的起点
- 实施集成，然后针对传统 API 方式做彻底的 A/B 测试与对比
- 衡量结果，收集基准/性能数据，并把你的发现与团队分享

**阶段 3：规模化与优化**
- 一步一个脚印：根据结果，承接更大、更复杂的集成想法
- 随着时间持续优化你的集成流程
- 利用来自开发团队和终端用户的反馈来完善流程

### 衡量成功：量化影响

给业务读者的部分：要理解通过 MCP 集成 AI agent 的收益，以下是一些你可以跟踪的关键绩效指标（KPI）：

- 开发速度
- 错误率
- 客户满意度

#### 构建你的案例研究并分享你的心得

记录你团队的历程并分享经验，对你的团队和更广泛的开发者社区都很有价值。以下是你可以分享的一些内容，用以帮助展示项目的影响：

- **前后指标**：在集成 AI agent 和 MCP 之后，你在开发时间、错误率方面看到了怎样的改进？
- **团队反馈**：这里会有一段学习曲线，和我们当初集成 API 时所经历的很像；收集关于集成工作流进展如何、哪些可以改进的反馈
- **客户/终端用户影响**：突出用户参与度、满意度或其他用户/客户指标上的任何积极变化
- **经验教训**：也许是最重要的一点；哪些做得好、哪些不好、你打算如何调整下一阶段集成的流程？

### 我们接下来往哪走？

理解你现有的集成，并找出可以用 AI agent 和 MCP 改进的潜在领域，是你的起点。关于集成 AI agent，还有很多要学，而 MCP 仍是一项新技术。

找到 AI 能帮上忙的那些机会，并制定一个逐步把 AI 和 MCP 引入你项目的计划，是最好的起步方式。

请记住，这个集成格局仍在演进。对新想法保持开放，并随着技术成熟调整你的方法。构建更智能的应用是一段旅程，路上会有岔路口。

延伸阅读：

1. 什么是 AI Agent
- [AI agents — what they are, and how they'll change the way we work](https://news.microsoft.com/source/features/ai/ai-agents-what-they-are-and-how-theyll-change-the-way-we-work/)
- [What are AI Agents and Why do They Matter?](https://www.aitrends.com/ai-agents/what-are-ai-agents-and-why-do-they-matter/)

2. [An Introduction to MCP](https://modelcontextprotocol.io/introduction)

3. [Connecting AI Agents to Your Systems with MCP](https://block.github.io/goose/blog/2024/12/10/connecting-ai-agents-to-your-systems-with-mcp/)

4. [Global AI Survey: AI proves its worth, but few scale impact](https://www.mckinsey.com/featured-insights/artificial-intelligence/global-ai-survey-ai-proves-its-worth-but-few-scale-impact)

5. [Bringing generative AI to bear on legacy modernization in insurance](https://www.thoughtworks.com/en-us/insights/blog/generative-ai/generative-ai-legacy-modernization-insurance-erik-doernenburg)

### TL;DR 常见问题

问：**MCP 将如何帮助 API？**<br/>
答：从 [Angie Jones 的这篇文章](https://block.github.io/goose/blog/2025/02/17/agentic-ai-mcp/#mcp-ecosystem)开始。MCP 提供关于你 API 的上下文，让 AI Agent 对 API 端点和响应的能力有更多上下文与感知。这能帮助 Agent 理解请求的意图，动态地调用底层 API 端点、处理数据转换并返回响应。再也不用手动编写代码、响应校验器、错误处理器等等了！

问：**作为一名开发者，我可以采取哪些初步步骤来探索 AI agent 和 MCP？**<br/>
答：先研究基本概念，并使用其他已有的 MCP 服务器。我们建议从 [Goose](https://block.github.io/goose/) 开始，去集成一个现有的 MCP 服务器。我们有一份不断增长的[教程列表](https://block.github.io/goose/docs/category/mcp-servers)，帮你了解 GitHub、PostgreSQL、Google Maps 等技术。等你对使用 MCP 感到得心应手后，就可以开始为你自己的 API 构建 MCP 服务器了。

问：**那 AI 和 MCP 的安全性呢？**<br/>
答：AI agent 可以通过更好的交互上下文感知来增强安全性，但 MCP 仍相对较新，需要[仔细的安全评估](https://block.github.io/goose/blog/2025/03/26/mcp-security/)。你的业务和开发团队应彻底调查 MCP 的能力，以确保你构建了适当的访问控制，并管理好数据隐私。

问：**完整迁移通常要花多长时间？**<br/>
答：这太动态了，无法给出一个确定的答案。集成和迁移的差异可能很大，取决于你现有 API 使用情况和已有集成的范围。从小处开始，先构建一些试点项目来试试水，这些可能只需要几天或几周。

问：**开发者在这趟 AI/MCP 之旅中可能遇到哪些问题？**<br/>
答：任何技术都有学习曲线。考虑到 MCP 仍相对较新且在不断演进，这条曲线可能会更陡。更大的社区需要围绕 MCP 的测试与调试制定策略，同时还要考虑安全与数据隐私。这意味着你今天学到的东西，哪怕只过了短短几个月，也需要重新评估。

问：**对于企业级 AI 集成，MCP 有多成熟、多可用于生产？**<br/>
答：你的做法可能因你是在构建自己的 MCP 服务器，还是在集成中使用第三方 MCP 服务器而有所不同。开发者应评估 MCP 的所有好处，并考虑围绕安全和数据隐私所做的工作。起初先专注于一个小试点项目或非关键系统，以评估它是否适合你的具体需求。持续关注 [MCP 的发展路线图](https://modelcontextprotocol.io/development/roadmap)和社区反馈。

<head>
  <meta property="og:title" content="MCP Is Rewriting the Rules of API Integration" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/04/22/mcp-is-rewriting-the-rules-of-api-integration" />
  <meta property="og:description" content="A developer's guide to modernizing API infrastructure with AI agents and Model Context Protocol. Learn about the benefits, integration strategies, and how to address security considerations." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/cover-1e2153c66f3f0c92da7bbaafd240a9b4.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="MCP Is Rewriting the Rules of API Integration" />
  <meta property="twitter:description" content="A developer's guide to modernizing API infrastructure with AI agents and Model Context Protocol. Learn about the benefits, integration strategies, and how to address security considerations." />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/cover-1e2153c66f3f0c92da7bbaafd240a9b4.png" />
</head>

---

## 使用 Goose 前你*实际上*需要了解的 4 件事

> 原文：https://block.github.io/goose/blog/2025-04-23-things-need-to-know

![博客封面](cover.png)

所以你听说了 Goose。也许你看了场直播，也许团队里有人提起了它，又或者你只是在试图自动化自己的开发环境时，偶然闯进了互联网的这个角落。不管怎样——真为你高兴。

Goose 是一个本地运行、开源的 AI agent，可以自动化任务、与你的代码库交互，并连接到一个不断壮大的工具生态。但在你点下安装之前，有 4 件事你应该知道，以便最大化地利用它。

<!-- truncate -->

---

### 等等——Goose 到底是什么？

Goose 是一个 **MCP 客户端**。

这意味着它通过一种叫做 [**Model Context Protocol (MCP)**](https://www.anthropic.com/news/model-context-protocol) 的东西来连接工具和数据——这是一项开放标准，让 AI agent 能够通过自然语言与外部系统交互。如果你用过 Claude Desktop、Windsurf、VS Code 或 Cursor 里的 Agent 模式，那你其实已经用过一个 MCP 客户端了，只是你可能没意识到。

下面是 Goose 的与众不同之处：

- 它**在本地运行**，而不是运行在别人的云上
- 你**自带 LLM**，可以使用最适合你的那个
- 你可以**添加新能力**，使用开源的 MCP 服务器

与其把它想成「一个 AI 助手」，不如把它想成「你的个人自动化工具箱」。你决定用哪个 LLM、它能访问哪些工具、能执行哪些任务。你没有被锁定；一切由你做主。

---

### 1. 选择合适的 LLM

Goose 并不内置 LLM。你要自带 LLM。这意味着你可以选择最适合自己的模型，无论是 Claude 或 Gemini 这样的托管模型，还是 Ollama 这样更私密、更本地的模型。

但要提醒一下：并非所有模型都生而平等，尤其是在隐私、性能或按 token 收费的多少方面。如果你只是在探索，带免费额度的云端托管 LLM 是个很好的起点。但如果你处理的是敏感数据，或者只是不想把东西发到第三方服务器，那就应该选择本地。

无论哪种方式，Goose 都给了你灵活性。

话虽如此，如果你现在想在 Goose 上获得最佳性能，推荐使用 Anthropic 的 Claude 3.5 Sonnet 和 OpenAI 的 GPT-4o（2024-11-20），因为它们目前对工具调用的支持最强。

好奇其他模型表现如何？看看[社区灵感基准排行榜](https://goose-docs.ai/blog/2025/03/31/goose-benchmark/#leaderboard)，了解你喜欢的模型在 Goose 上的表现。

如果你还在犹豫，这里是[可用 LLM 提供方](https://goose-docs.ai/docs/getting-started/providers#available-providers)的完整列表。

---

### 2. 理解 MCP 服务器是什么

这里开始变得有趣了。Goose 是一个会说 **MCP** 的客户端。MCP 让「把其他应用和工具*作为提示词的一部分*来对话」成为可能。想读邮件、查 GitHub issue、运行自动化测试，或抓取网页？这就是 MCP 服务器登场的地方。

每个服务器都赋予 Goose 一项新能力。

真正的问题是：*你想让 Goose 能做什么？* 如果有对应的服务器，你多半就能实现。而且没错，有一个完整的 [MCP 服务器目录](https://glama.ai/mcp/servers)，你可以按工具、下载量等等来搜索。

---

### 3. 可能*会*有成本

Goose 本身呢？完全免费、开源。🎉 但你的 LLM 提供方可能就没那么大方了。

大多数模型都提供免费额度供你试用，但如果你做任何高强度的使用、或者经常用，最终会遇到速率限制或 token 计费。这很正常，但如果你没有预期，它会悄悄地找上门来。

为了帮你管理这一点，有一份[处理速率限制指南](https://goose-docs.ai/docs/guides/handling-llm-rate-limits-with-goose/)可以看看。

---

### 4. 融入社区

这部分比大多数人意识到的更重要。

goose 背后有一整个社区——人们在构建、探索、弄坏东西（再修好），并一路分享他们学到的一切。我们在 [Discord](https://discord.gg/n8R5VaWDAn) 上聚在一起，在 [GitHub Discussions](https://github.com/aaif-goose/goose/discussions) 里回答问题，每周还举办直播，展示 goose 能做什么以及如何让它做更多。

我们有：

- **Goosing Around** – 随性深入的分享，我们公开构建
- **Wild Goose Case** – 展示酷炫的社区项目
- **Great Goose Off** – 同样的任务、同样的时限，但不同的提示词、MCP 服务器和策略

你可以在我们的 [YouTube 频道](https://www.youtube.com/@goose-oss/streams)找到这些直播，即将到来的直播则见 Discord 日历。此外，如果你更喜欢文档，[Goose 文档](https://goose-docs.ai/)和[博客](https://goose-docs.ai/blog)也在不断更新新的指南、技巧和教程。

---

如果你具备了这四样东西：一个性能出色的 LLM、合适的 MCP 服务器、对 LLM 成本的基本了解，以及一个可以提问的地方，那你就完全准备好 Goose 了。

现在，去看[快速上手指南](https://goose-docs.ai/docs/quickstart)开始吧。

哦，当你玩到[井字棋游戏](https://goose-docs.ai/docs/quickstart/#write-prompt)时，我跟你赌 10 个 Goosebucks，你赢不了那个机器人。

<head>
  <meta property="og:title" content="4 Things You Need to Know Before Using Goose" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/04/23/things-need-to-know" />
  <meta property="og:description" content="Learn what you need to get started with Goose - a local open source AI agent that's powered by the LLM of your choice." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/cover-2ba7c2e15786be2db6108c91d27dc1ec.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="4 Things You Need to Know Before Using Goose" />
  <meta property="twitter:description" content="Learn what you need to get started with Goose - a local open source AI agent that's powered by the LLM of your choice." />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/cover-2ba7c2e15786be2db6108c91d27dc1ec.png" />
</head>

---

## 成功的 Recipe：烹制可复用的 Agentic 工作流

> 原文：https://block.github.io/goose/blog/2025-05-06-recipe-for-success

![博客封面](cookingwithgoose.png)

《料理鼠王》不只是一部温馨（且有点不太卫生）的、关于一只老鼠厨师的电影。它也可以类比一个热门技术趋势：AI agent 与 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)。

<!-- truncate -->

---

### Remy 与 Linguini 的互动关系

如果你没看过这部电影，剧情梗概是这样的：Remy 是一位了不起的厨师，技艺俱全，但他是一只老鼠，所以进不了厨房。Linguini 是一名厨房杂工，拥有完全的进入权限，却几乎不会做菜。他们一起形成了共生关系：Remy 藏在 Linguini 的帽子下面，指导他该在什么时候用什么工具。

如果顾客点了薯条，Linguini 可能会愣住，但 Remy 会打量厨房，看看有什么可用，然后给出一步一步的指令：

> _"Grab a knife and a cutting board. Now slice the potato."_

然后，Linguini 执行这个计划。

---

### 传统 AI Agent

Agentic 系统的运作方式类似。你有三个核心组件：

* 大语言模型（LLM）
* Agent
* 工具

LLM 就像 Remy；它充满知识和推理能力，却没有亲手操作的能力。agent 就像 Linguini；它能采取行动，却需要指引。

如果用户说「写一些单元测试」，LLM 会分析代码并回答，

> _"Looks like JavaScript. Use Jest, create a test file, and import the module."_

agent 遵循这个计划，使用 `file.write()` 之类的工具把它完成。

---

### Linguini 的成长

但 Linguini 的故事不止于此。即便有 Remy 的指引，他依然笨手笨脚，不确定该如何自信地在厨房里行动。他的老板 Skinner 主厨察觉到了不对劲。为了帮他进步，Linguini 被安排与 Colette 搭档，一位经验丰富的厨师，教他厨房是如何运作的：

* 工具放在哪里
* 各个工位如何组织
* 如何在空间中高效移动
* 缺东西时该何时调整

在 Colette 的指导下，Linguini 把厨房理解为一个系统。当顾客点意大利面时，Remy 迅速制定计划：

> _"Boil the pasta, sauté the garlic and tomatoes, plate it with basil."_

Linguini 不再盲目执行命令，而是具备了统筹整个运作的能力：

* 前往意面工位烧水
* 检查煎炒工位是否有干净的锅和新鲜大蒜
* 拿对工具：滤盆、汤勺、煎锅
* 必要时寻找备用锅具或改变流程
* 管理食材和备用物资
* 协调时机，让所有东西同步完成
* 自信地装盘并上菜

---

### 天生不同

跟随 Model Context Protocol(MCP) 的 AI agent 就是这样运作的。MCP 让 agent 从被动的执行者转变为主动的统筹者，使其不再那么依赖 LLM，而更能感知自己所处的上下文。

[Goose](https://block.github.io/goose/) 是一个本地运行、开源的 AI agent，遵循 MCP 的结构。

MCP 为 agent 与外部数据和服务交互提供了一种标准化的方式。它有三个核心组件：

* **MCP Host（主机）** – 接收计划并协调任务的核心 agent
* **MCP Client（客户端）** – 主机用来与外部服务通信的本地连接器
* **MCP Servers（服务器）** – 以结构化格式打包的工具、数据或提示词。在 Goose 生态中，我们把 MCP 服务器称为扩展。

这种架构让 Goose 能够动态发现工具、理解如何使用它们，并在多个系统之间统筹复杂的工作流。

---

### Goose 作为统筹者

当用户让 Goose「收集上周关于身份验证 bug 的所有讨论」时，Goose 会统筹这次操作。它协调工具、管理执行，并随机应变：

* 识别出正确的 MCP 服务器：Slack、GitHub、PostgreSQL
* 判断某个工具何时没有按预期工作
* 必要时考虑替代方案

当出问题时，Goose 不会慌张；它会转向。例如，Goose 可能会判断：

* 「Slack 搜索没有返回上周的消息。让我换个日期范围试试。」
* 「如果还是拿不到这些，PR 评论里可能有要点。」

---

### 用 Recipe 扩展 Agentic 工作流

这部电影上映已经 18 年了，我愿意想象 Linguini 已经超越了他的烹饪时代，步入了他的导师时代。与其低效地训练每一位新厨师，他把自己最喜欢的菜品记录下来，让自己的知识可分享、可扩展。

类似地，Goose 是一个有远见的 AI agent，通过 [Recipe](https://block.github.io/goose/docs/guides/recipes/session-recipes) 提供了一个扩展知识的方案。Recipe 是完整的统筹方案，你可以重跑、改造或分享，把知识传递给任何需要的人。

分享一个提示词并不总能复现同样的体验；AI 是非确定性的，而且人们可能没有配置相同的扩展或上下文。Recipe 通过打包你完整的 Goose 工作流来解决这个问题：扩展、设置、目标，以及示例活动。

**来试试：**
下面的链接是一个 Recipe，让你选择自己喜欢的平台（GitHub、Bluesky 或 Dev.to），并使用你的公开内容构建一个自定义的、故事驱动的 404 作品集页面。

> [用 Goose 创建一个 404 风格的作品集页面](goose://recipe?config=eyJ2ZXJzaW9uIjoiMS4wLjAiLCJ0aXRsZSI6IjQwNFBvcnRmb2xpbyIsImRlc2NyaXB0aW9uIjoiQ3JlYXRlIHBlcnNvbmFsaXplZCwgY3JlYXRpdmUgNDA0IHBhZ2VzIHVzaW5nIHB1YmxpYyBwcm9maWxlIGRhdGEiLCJpbnN0cnVjdGlvbnMiOiJDcmVhdGUgYW4gZW5nYWdpbmcgNDA0IGVycm9yIHBhZ2UgdGhhdCB0ZWxscyBhIGNyZWF0aXZlIHN0b3J5IHVzaW5nIGEgdXNlcidzIHJlY2VudCBwdWJsaWMgY29udGVudCBmcm9tICoqb25lKiogb2YgdGhlIGZvbGxvd2luZyBwbGF0Zm9ybXM6ICoqR2l0SHViKiosICoqRGV2LnRvKiosIG9yICoqQmx1ZXNreSoqLiBZb3UgZG8gbm90IG5lZWQgdG8gdXNlIGFsbCB0aHJlZeKAlGp1c3QgdGhlIG9uZSBzZWxlY3RlZCBieSB0aGUgdXNlci5cblxuVGhlIHBhZ2Ugc2hvdWxkIGJlIGZ1bGx5IGJ1aWx0IHdpdGggKipIVE1MLCBDU1MsIGFuZCBKYXZhU2NyaXB0KiosIGZlYXR1cmluZzpcblxuKiBSZXNwb25zaXZlIGRlc2lnblxuKiBQZXJzb25hbCBicmFuZGluZyBlbGVtZW50cyAoZS5nLiwgbmFtZSwgaGFuZGxlLCBhdmF0YXIpXG4qIE5hcnJhdGl2ZS1kcml2ZW4gbGF5b3V0IHRoYXQgdHVybnMgdGhlIGVycm9yIGludG8gYW4gb3Bwb3J0dW5pdHkgZm9yIGRpc2NvdmVyeVxuXG5Vc2UgcGxhdGZvcm0tc3BlY2lmaWMgbWV0aG9kcyB0byBmZXRjaCByZWNlbnQgdXNlciBjb250ZW50OlxuXG4qIEZvciAqKkRldi50byoqLCB1c2UgdGhlIFtwdWJsaWMgRGV2LnRvIEFQSV0oaHR0cHM6Ly9kZXZlbG9wZXJzLmZvcmVtLmNvbS9hcGkpIHRvIHJldHJpZXZlIHJlY2VudCBhcnRpY2xlcywgcmVhY3Rpb25zLCBhbmQgcHJvZmlsZSBpbmZvcm1hdGlvbi5cbiogRm9yICoqR2l0SHViKiosIHVzZSB0aGUgR2l0SHViIFJFU1Qgb3IgR3JhcGhRTCBBUEkgdG8gYWNjZXNzIHJlY2VudCByZXBvcywgY29tbWl0cywgYW5kIGNvbnRyaWJ1dGlvbnMuXG4qIEZvciAqKkJsdWVza3kqKiwgdXNlIHB1YmxpYyBmZWVkIGVuZHBvaW50cyBmcm9tIHRoZSBBcHBWaWV3IEFQSSAoZS5nLiwgYGFwcC5ic2t5LmZlZWQuZ2V0QXV0aG9yRmVlZGApIHRvIHB1bGwgcG9zdHMsIHJlcGxpZXMsIG9yIGxpa2VzLlxuXG5JbmNvcnBvcmF0ZSB0aGUgZmV0Y2hlZCBkYXRhIGludG8gYSBjb21wZWxsaW5nIG5hcnJhdGl2ZSAoZS5nLiwg4oCcTG9va3MgbGlrZSB0aGlzIHBhZ2UgaXMgbWlzc2luZywgYnV0IFxcW3VzZXJuYW1lXSBoYXMgYmVlbiBidXN5IeKAnSksIGFuZCBkaXNwbGF5IGl0IHVzaW5nIGVuZ2FnaW5nIHZpc3VhbHMgbGlrZSBjYXJkcywgdGltZWxpbmVzLCBvciBtZWRpYSBlbWJlZHMuXG5cbldyYXAgdGhlIHVzZXLigJlzIGFjdGl2aXR5IGludG8gYSBzdG9yeSDigJQgZm9yIGV4YW1wbGU6XG5cbuKAnFRoaXMgcGFnZSBtYXkgYmUgbG9zdCwgYnV0IEB1c2VybmFtZSBpcyBidWlsZGluZyBzb21ldGhpbmcgYW1hemluZy4gVGhlaXIgbGF0ZXN0IG9wZW4gc291cmNlIGpvdXJuZXkgaW52b2x2ZXMgYSBuZXcgcmVwbyB0aGF04oCZcyBnYWluaW5nIHN0YXJzIGZhc3TigKbigJ1cbuKAnFlvdSB3b27igJl0IGZpbmQgd2hhdCB5b3XigJlyZSBsb29raW5nIGZvciBoZXJlLCBidXQgeW91IHdpbGwgZmluZCBAdXNlcm5hbWXigJlzIGhvdCB0YWtlIG9uIGFzeW5jL2F3YWl0IGluIHRoZWlyIGxhdGVzdCBEZXYudG8gcG9zdC7igJ1cblxuVGhlIHJlc3VsdCBzaG91bGQgYmUgYSBzbWFsbCBuYXJyYXRpdmUtZHJpdmVuIG1pY3Jvc2l0ZSB0aGF0IGR5bmFtaWNhbGx5IGNlbGVicmF0ZXMgdGhlIHVzZXIncyBwcmVzZW5jZSBvbmxpbmXigJRldmVuIHdoZW4gdGhlIGRlc3RpbmF0aW9uIGlzIG1pc3NpbmcuXG5cbkFzayB0aGUgdXNlcjpcblxuMS4gV2hpY2ggcGxhdGZvcm0gdG8gdXNlOiBHaXRIdWIsIERldi50bywgb3IgQmx1ZXNreVxuMi4gVGhlaXIgdXNlcm5hbWUgb24gdGhhdCBwbGF0Zm9ybVxuXG5UaGVuIGdlbmVyYXRlIHRoZSBjb21wbGV0ZSBjb2RlIGluIGEgZm9sZGVyIGNhbGxlZCA0MDQtc3RvcnkuXG4iLCJleHRlbnNpb25zIjpbXSwiYWN0aXZpdGllcyI6WyJCdWlsZCBlcnJvciBwYWdlIGZyb20gR2l0SHViIHJlcG9zIiwiR2VuZXJhdGUgZXJyb3IgcGFnZSBmcm9tIGRldi50byBibG9nIHBvc3RzIiwiQ3JlYXRlIGEgNDA0IHBhZ2UgZmVhdHVyaW5nIEJsdWVza3kgYmlvIl0sImF1dGhvciI6eyJjb250YWN0Ijoicml6ZWwifX0=)

:::note
上面的链接会在 [Goose Desktop 应用](https://block.github.io/goose/docs/getting-started/installation)中打开。
:::

<details>
  <summary>查看 Recipe 配料</summary>
```yaml
version: 1.0.0
title: "404Portfolio"
description: "Create personalized, creative 404 pages using public profile data"

instructions: |
  Create an engaging 404 error page that tells a creative story using a user's recent public content from **one** of the following platforms: **GitHub**, **Dev.to**, or **Bluesky**. You do not need to use all three—just the one selected by the user.

  The page should be fully built with **HTML, CSS, and JavaScript**, featuring:

  * Responsive design
  * Personal branding elements (e.g., name, handle, avatar)
  * Narrative-driven layout that turns the error into an opportunity for discovery

  Use platform-specific methods to fetch recent user content:

  * For **Dev.to**, use the [public Dev.to API](https://developers.forem.com/api) to retrieve recent articles, reactions, and profile information.
  * For **GitHub**, use the GitHub REST or GraphQL API to access recent repos, commits, and contributions.
  * For **Bluesky**, use public feed endpoints from the AppView API (e.g., `app.bsky.feed.getAuthorFeed`) to pull posts, replies, or likes.

  Incorporate the fetched data into a compelling narrative (e.g., “Looks like this page is missing, but \[username] has been busy!”), and display it using engaging visuals like cards, timelines, or media embeds.

  Wrap the user’s activity into a story — for example:

  “This page may be lost, but @username is building something amazing. Their latest open source journey involves a new repo that’s gaining stars fast…”
  “You won’t find what you’re looking for here, but you will find @username’s hot take on async/await in their latest Dev.to post.”

  The result should be a small narrative-driven microsite that dynamically celebrates the user's presence online—even when the destination is missing.

  Ask the user:

  1. Which platform to use: GitHub, Dev.to, or Bluesky
  2. Their username on that platform

  Then generate the complete code in a folder called 404-story.


activities:
  - "Build error page from GitHub repos"
  - "Generate error page from dev.to blog posts"
  - "Create a 404 page featuring Bluesky bio"

extensions:
  - type: builtin
    name: developer
  - type: builtin
    name: computercontroller
```

</details>

---

### 可复用的 Agentic 工作流

下面是一些 Recipe 能派上用场的不同场景：

#### 让新队友上手

通常，一位开发者加入团队后，会花好几个小时搭建环境、弄清楚该用哪些平台、破译那些不成文的做事规则。
不如直接给他们一个 Recipe。借助预加载的上下文和合适的工具，它能自动化本地设置、呈现相关文档，并带他们走一遍团队的工作流，连一次屏幕共享都不需要。

#### 举办工作坊

工作坊总是充满变数：不同的机器、配置和干扰。
跳过混乱吧。丢一个 Recipe 链接出去，让每位参与者都能启动相同的环境、相同的工具、相同的目标和相同的示例。你有更多时间用来教学，花在排查问题上的时间更少。

#### 加速你的团队

你的团队里满是善于解决问题的人。有位队友搭建了一个漂亮的内部仪表盘。另一位搞定了支持工单分诊。还有人自动化了变更日志生成。接着问题来了：我们怎么让整个团队都能轻松用上？Recipe 把你团队的成果变成任何人都能上手的可复用工作流。构建一个由 Goose 驱动的共享流程库，让你团队的影响力成倍放大。

 拿上 [Goose](https://block.github.io/goose/docs/getting-started/installation)，开始烹制你自己的 [Recipe](https://block.github.io/goose/docs/guides/recipes/session-recipes) 吧。未来的你（和你的团队）会感谢你！

<head>
  <meta property="og:title" content="A Recipe for Success: Cooking Up Repeatable Agentic Workflows" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/05/06/recipe-for-success" />
  <meta property="og:description" content="A fresh look at AI agents, orchestration, and repeatability told through the metaphor of a rat who can cook." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/cookingwithgoose-9114cf03cec76df4792fc58361ebe20b.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="A Recipe for Success: Cooking Up Repeatable Agentic Workflows" />
  <meta property="twitter:description" content="A fresh look at AI agents, orchestration, and repeatability told through the metaphor of a rat who can cook." />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/cookingwithgoose-9114cf03cec76df4792fc58361ebe20b.png" />
</head>

---

## 冠军级驱动开发：你团队的 AI 战术手册，助你达到巅峰表现

> 原文：https://block.github.io/goose/blog/2025-05-09-developers-ai-playbook-for-team-efficiency

![博客封面](cdd-playbook.png)

### 开发者的战术手册：用 AI 提升团队效率

开发团队可以像运动队一样运作。每个成员都有自己的角色，一份共享的战术手册有助于协调行动。让我们来探讨，AI 驱动的「战术（plays）」如何为你的开发团队构成一份入门「战术手册」，帮助处理常见的技术任务。你可以把 Recipe 与 [Goose](https://block.github.io/goose/) 配合使用，借助 [Model Context Protocol (MCP)](https://modelcontextprotocol.io) 让你更高效。

<!-- truncate -->

---

### 理解现代开发团队面临的挑战

* 开发团队要管理复杂的系统和工具。他们努力快速、可靠地交付软件。
* 新开发者需要学习团队的流程和工具。这需要时间。
* 在所有工作中保持一致的品质需要清晰的标准，例如：一支运动队反复练习战术，才能实现一致的执行。
* 团队常常使用很多工具，从 IDE 和版本控制到 CI/CD 流水线和 issue 跟踪器。
* 管理这些工具以及它们之间的工作流可能很复杂。

### 使用 AI 战术手册的好处

使用一份共享的 AI 战术手册能为开发团队带来若干好处：
* **更快的上手：** 新成员可以使用现有的 Recipe 来学习标准流程，更快变得高效。
* **更好的一致性：** 标准化的 Recipe 确保任务每次都按同样的方式执行，从而带来更可预测的结果。
* **更高的效率：** 把例行任务自动化，让开发者腾出精力专注于更复杂的问题解决。
* **知识共享：** Recipe 可以把团队知识和最佳实践固化下来，让每个人都能获取。

随着团队采用 Goose 这样的 AI 工具，定义和共享这些自动化工作流的能力将变得越来越重要。

### AI 战术：标准化你团队的工作流

Goose 可以帮你标准化并自动化这些任务，方式是[创建 Recipe](https://block.github.io/goose/docs/guides/recipes/session-recipes)。当团队里的一位开发者使用 Goose 时，他们可以创建一个描述如何完成某项任务的 Recipe，然后与团队其他成员分享。这些 Recipe 可以共享、复用，并随着时间不断改进，就像一支运动队的战术手册一样。

Recipe 的构建基于对「你希望 Goose 协助的工作流」的理解，其中可能涉及一个或多个 MCP 服务器，比如 [GitHub](https://block.github.io/goose/docs/mcp/github-mcp/) 或 [PostgreSQL](https://block.github.io/goose/docs/mcp/postgres-mcp/)。Recipe 被设计为可复用、可适配，让开发者可以构建一个能跨不同项目使用的库。

一份共享的 AI 战术手册能帮助团队每个人一致地完成任务。它还能减少花在重复性工作上的时间。

### Goose Recipe：你战术手册的构建模块

想看一个厨房相关的类比作为概览，请查看 [Rizel](https://block.github.io/goose/blog/authors/rizel/) 最近的博客文章[《成功的 Recipe》](https://block.github.io/goose/blog/2025/05/06/recipe-for-success)。

一个 Goose Recipe 可以从当前的 Goose 会话中保存，也可以从零写成一个 YAML 文件。它包含供 AI 遵循的指令、用于 AI 响应的提示词、带数据类型的可选参数，以及所需的扩展列表。

#### 创建 Recipe

如果你[从当前 Goose 会话创建一个 Recipe](https://block.github.io/goose/docs/guides/recipes/session-recipes/#create-recipe)，它会提示你输入名称和描述，并生成一些你可以编辑的活动，以及你应该审阅和编辑的指令。你会得到一个可以分享给团队的 URL。

要从零创建一个 Recipe，你可以用 Goose CLI，在会话中使用 `/recipe` 命令来创建一个新的 Recipe 文件。它会在你当前目录下创建一个 `recipe.yaml` 文件。要创建自定义文件名，可以用 `/recipe custom-filename.yaml`。之后，你就可以添加自己的指令和活动。

#### 校验 Recipe

就像所有会测试自己代码的好开发者一样（你*确实*会测试你的代码，对吧？？），你也可以在终端/shell 里运行 `goose validate recipe-filename.yaml` 来校验你的 Goose Recipe，它会检查 Recipe 文件的语法和结构。

#### 分享 Recipe

如果你使用 Goose Desktop 应用，创建 Recipe 会给你一个可以直接分享给团队的 URL。

如果你是以 YAML 方式创建 Recipe 文件，你可以把文件分享给团队，也可以在终端/shell 里运行 `goose recipe deeplink recipe-filename.yaml` 为它生成一个 URL。

#### 使用 Recipe

点击来自团队的共享 URL 会打开 Goose，并在一个新会话中加载该 Recipe。用户之间不会共享任何数据，所以你不必担心泄露 API 密钥或其他敏感信息。

对于 CLI，你可以在终端/shell 里使用 `goose run recipe-filename.yaml` 命令来运行 Recipe。

:::info 专业提示
你可以设置一个环境变量，指向团队 Recipe 所在的共享 GitHub 仓库，队友就能按名称运行这些 Recipe：
`export GOOSE_RECIPE_GITHUB_REPO=github-username/repo-name`

然后，运行某个 Recipe：`goose run --recipe <recipe-name>`
:::

### 给你的团队的入门 AI 战术包

一个 AI 战术「入门包」可以应对常见的开发工作流。它给你的团队一个自动化例行任务的基础。下面是一些点子，帮你开始了解可以用 Goose 自动化哪些类型的任务。

#### 战术 1：生成变更日志

维护变更日志对于跟踪项目进展、沟通更新很重要。这项任务可能很耗时。
一个 AI 战术可以自动化这一过程的部分工作。例如，「从 Git 提交生成变更日志」战术（基于所提供文件中的 `recipe.yaml`）有助于生成一致的变更日志。

##### 这个战术如何工作：
1.  **收集数据：** AI 从 Git 仓库中检索指定两点之间的提交信息、日期和 issue 编号。
2.  **分类信息：** 它把提交整理成诸如 Features（新功能）、Bug Fixes（bug 修复）和 Performance Improvements（性能改进）等类别。
3.  **格式化输出：** AI 把这些信息格式化成一份结构化的变更日志文档。
4.  **更新文件：** 然后它可以把这些格式化后的说明插入到你现有的 `CHANGELOG.md` 文件中。

这个战术有助于确保变更日志详尽且格式一致，节省开发者时间。

<details>
  <summary>查看 Changelog Recipe</summary>

```yaml
version: 1.0.0
title: Generate Changelog from Commits
description: Generate a weekly Changelog report from Git Commits
prompt: perform the task to generate change logs from the provided git commits
instructions: |
  Task: Add change logs from Git Commits

  1. Please retrieve all commits between SHA {{start_sha}} and SHA {{end_sha}} (inclusive) from the repository.

  2. For each commit:
    - Extract the commit message
    - Extract the commit date
    - Extract any referenced issue/ticket numbers (patterns like #123, JIRA-456)

  3. Organize the commits into the following categories:
    - Features: New functionality added (commits that mention "feat", "feature", "add", etc.)
    - Bug Fixes: Issues that were resolved (commits with "fix", "bug", "resolve", etc.)
    - Performance Improvements: Optimizations (commits with "perf", "optimize", "performance", etc.)
    - Documentation: Documentation changes (commits with "doc", "readme", etc.)
    - Refactoring: Code restructuring (commits with "refactor", "clean", etc.)
    - Other: Anything that doesn't fit above categories

  4. Format the release notes as follows:
    
    # [Version/Date]
    ## Features
    - [Feature description] - [PR #number](PR link)
    ## Bug Fixes
    - [Bug fix description] - [PR #number](PR link)
    [Continue with other categories...]
    
    Example:
    - Optimized query for monthly sales reports - [PR #123](https://github.com/fake-org/fake-repo/pull/123)

  5. Ensure all commit items have a PR link. If you cannot find it, try again. If you still cannot find it, use the commit sha link instead. For example: [commit sha](commit url)

  6. If commit messages follow conventional commit format (type(scope): message), use the type to categorize and include the scope in the notes as a bug, feature, etc

  7. Ignore merge commits and automated commits (like those from CI systems) unless they contain significant information.

  8. For each category, sort entries by date (newest first).

  9. Look for an existing CHANGELOG.md file and understand its format; create the file if it doesn't exist. Then, output the new changelog content at the top of the file, maintaining the same markdown format, and not changing any existing content.

extensions:
- type: builtin
  name: developer
  display_name: Developer
  timeout: 300
  bundled: true
activities:
- Generate release notes from last week's commits
- Create changelog for version upgrade
- Extract PR-linked changes only
- Categorize commits by conventional commit types
author:
  contact: goose-community
```

</details>

#### 战术 2：创建 Pull Request 描述

清晰的 Pull Request (PR) 描述有助于审阅者理解所做的改动，从而给出更好的反馈。撰写详尽的 PR 很费功夫。

##### 这个战术如何工作：
1.  **分析改动：** AI 分析本地 Git 仓库中已暂存的改动和未推送的提交。
2.  **识别改动类型：** 它判断改动的性质（例如 feature、fix、refactor）。
3.  **生成描述：** 它创建一份 PR 描述，包含改动摘要、技术细节、修改的文件列表，以及潜在影响。
4.  **建议分支/提交（可选）：** 有些战术还可能基于代码改动建议分支名或提交信息。

使用这个战术有助于创建一致且信息充分的 PR。这会让代码审查流程更高效。

<details>
  <summary>查看 PR Generator Recipe</summary>

```yaml
version: 1.0.0
title: PR Generator
author:
  contact: goose-community
description: Automatically generate pull request descriptions based on changes in a local git repo
instructions: Your job is to generate descriptive and helpful pull request descriptions without asking for additional information. Generate commit messages and branch names based on the actual code changes.
parameters:
  - key: git_repo_path
    input_type: string
    requirement: first_run
    description: path to the repo you want to create PR for
  - key: push_pr
    input_type: boolean
    requirement: optional
    default: false
    description: whether to push the PR after generating the description
extensions:
    - type: builtin
      name: developer
      display_name: Developer
      timeout: 300
      bundled: true
    - type: builtin
      name: memory
      display_name: Memory
      timeout: 300
      bundled: true
      description: "For storing and retrieving formatting preferences that might be present"
prompt: |
  Analyze the staged changes and any unpushed commits in the git repository {{git_repo_path}} to generate a comprehensive pull request description. Work autonomously without requesting additional information.

  Analysis steps:
  1. Get current branch name using `git branch --show-current`
  2. If not on main/master/develop:
     - Check for unpushed commits: `git log @{u}..HEAD` (if upstream exists)
     - Include these commits in the analysis
  3. Check staged changes: `git diff --staged`
  4. Save the staged changes diff for the PR description
  5. Determine the type of change (feature, fix, enhancement, etc.) from the code

  Generate the PR description with:
  1. A clear summary of the changes, including:
     - New staged changes
     - Any unpushed commits (if on a feature branch)
  2. Technical implementation details based on both the diff and unpushed commits
  3. List of modified files and their purpose
  4. Impact analysis (what areas of the codebase are affected)
  5. Testing approach and considerations
  6. Any migration steps or breaking changes
  7. Related issues or dependencies

  Use git commands:
  - `git diff --staged` for staged changes
  - `git log @{u}..HEAD` for unpushed commits
  - `git branch --show-current` for current branch
  - `git status` for staged files
  - `git show` for specific commit details
  - `git rev-parse --abbrev-ref --symbolic-full-name @{u}` to check if branch has upstream

  Format the description in markdown with appropriate sections and code blocks where relevant.

  {% if push_pr %}
  Execute the following steps for pushing:
  1. Determine branch handling:
     - If current branch is main/master/develop or unrelated:
       - Generate branch name from staged changes (e.g., 'feature-add-user-auth')
       - Create and switch to new branch: `git checkout -b [branch-name]`
     - If current branch matches changes:
       - Continue using current branch
       - Note any unpushed commits

  2. Handle commits and push:
     a. If staged changes exist:
        - Create commit using generated message: `git commit -m "[type]: [summary]"`
        - Message should be concise and descriptive of actual changes
     b. Push changes:
        - For existing branches: `git push origin HEAD`
        - For new branches: `git push -u origin HEAD`

  3. Create PR:
     - Use git/gh commands to create PR with generated description
     - Set base branch appropriately
     - Print PR URL after creation

  Branch naming convention:
  - Use kebab-case
  - Prefix with type: feature-, fix-, enhance-, refactor-
  - Keep names concise but descriptive
  - Base on actual code changes

  Commit message format:
  - Start with type: feat, fix, enhance, refactor
  - Followed by concise description
  - Based on actual code changes
  - No body text needed for straightforward changes

  Do not:
  - Ask for confirmation or additional input
  - Create placeholder content
  - Include TODO items
  - Add WIP markers
  {% endif %}
```

</details>

#### 你战术手册中的其他潜在战术

你的团队可以为许多其他任务创建战术：
* **调试辅助：** 一个战术可以引导开发者或 AI 完成诊断常见问题的初始步骤，比如检查特定日志或运行预定义命令。
* **日志分析：** 一个 AI 战术可以定义一套标准流程，用于查询和汇总日志数据以定位问题。
* **文档更新：** 一个「Readme Bot」可以让 AI 协助生成或更新项目的 README 文件。
* **内容迁移：** 「dev guide migration」Recipe 可以提供一种结构化的方式来迁移文档内容，确保信息被保留且格式正确。

### 你的团队可以自动化哪些类型的任务？

我们很希望你能和我们分享你的想法！通过创建一个 Recipe 并把它发布到 [Discord 上的 goose 社区](http://discord.gg/n8R5VaWDAn)来分享你的点子吧。

<head>
  <meta property="og:title" content="Championship Driven Development: Your team's AI Playbook for Peak Performance" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/05/09/developers-ai-playbook-for-team-efficiency" />
  <meta property="og:description" content="Learn how AI-driven 'plays,' based on Model Context Protocol, can help development teams improve common workflows like changelog generation and pull requests." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/cdd-playbook-69a053588574d8678c2acb92a1b21da6.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Championship Driven Development: Your team's AI Playbook for Peak Performance" />
  <meta property="twitter:description" content="Learn how AI-driven 'plays,' based on Model Context Protocol, can help development teams improve common workflows like changelog generation and pull requests." />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/cdd-playbook-69a053588574d8678c2acb92a1b21da6.png" />
  <meta name="keywords" content="AI development; Model Context Protocol; developer productivity; team playbook; AI automation; Goose; software development efficiency; changelogs; pull requests" />
</head>

---

## 用 Goose 与 Qwen3 实现本地执行

> 原文：https://block.github.io/goose/blog/2025-05-12-local-goose-qwen3

:::warning 已过时
「进阶技巧」下提到的 goose `/plan` 模式此后已被移除，独立的 planner 模型设置也随之移除。本文中的其他内容仍然适用。
:::

![本地 AI agent](goose-qwen-local.png)

几周前，[Qwen 3](https://qwenlm.github.io/blog/qwen3/) 带着一系列能力和尺寸发布了。这个模型展现出潜力，即便在非常紧凑的形态下，比如 8B 参数和 4bit 量化，也能成功地与 goose 进行工具调用。甚至多轮工具调用。

到目前为止，我还没见过这么小的模型能做到这一点，所以这真的很令人印象深刻，也预示着这个模型以及未来大小开放权重模型的好兆头。我预期 Qwen3 更大的模型在各种任务上会表现得相当好，但即便是这个小模型，我也觉得很有用。

<!-- truncate -->

### 本地工作流与本地 agent

有一段时间，我的 `~/.zshrc` 文件里一直有一个用于命令行的小助手函数：

```zsh
# zsh helper to use goose if you make a typo or just want to yolo into the shell
command_not_found_handler() {
  local cmd="$*"
  echo "🪿:"
  goose run -t "can you try to run this command please: $cmd"
}
```

它利用了一项 zsh 特性（macOS 现在已默认使用 zsh），当命令行上没有任何其他东西说得通时，就会委托给这个函数。
这让我可以打错字，或者直接在命令行里输入我想做的事，比如 `$> can you kill whatever is listening on port 8000`，goose 就会去干活，甚至不需要打开一个 goose 会话。

当 Qwen3 + Ollama 与 goose 全部在本地运行时，效果足够好，于是我切换成了这套工作流的完全本地版本，它在我离线、在火车上等情况下也能用：

```zsh
command_not_found_handler() {
  local cmd="$*"
  echo "🪿:"
  GOOSE_PROVIDER=ollama GOOSE_MODEL=michaelneale/qwen3 goose run -t "can you try to run this command please: $cmd"
}
```

### Qwen3 的推理

默认情况下，Qwen 3 模型会先对问题「思考」（推理），因为它们是通用模型；但我发现跳过这个推理阶段会更快（对我的用途来说效果也更好）。

在系统提示词里加上 `/no_think`，它一般就会直接跳到执行（这可能会让它在更大的任务上表现差一些，但在这个场景里，它是个只做几轮工具调用的小模型）。

我对[默认的 Ollama 聊天模板做了一点小调整](https://ollama.com/michaelneale/qwen3)，你可以像上面那样使用它，如果你喜欢的话（或者 Ollama 托管的默认 `qwen3` 模型也能开箱即用）。

### 进阶技巧

你可以用一个单独的模型（也许是带推理的 Qwen3，或者 deepseek 之类的其他模型）配合 goose 的 `/plan` 模式，在切换到 Qwen3 通过工具调用执行之前，先帮忙规划行动。

如果你有硬件，试试更大的模型会很有意思（我只用过 8B 参数的那个）。我当前的配置是一台 64G 的 M1 Pro MacBook（大约 2022 年的硬件），可用于 GPU/AI 的内存大概不到 48G，这限制了我能运行什么，但对我的用途来说，处于「no think」模式的 qwen3 表现得可以接受。

<head>
  <meta property="og:title" content="Goose and Qwen3 for Local Execution" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/05/12/local-goose-qwen3" />
  <meta property="og:description" content="Run AI commands locally with Goose and Qwen3 for fast, offline tool execution" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/goose-qwen-local-62d07cd240ff65cb99a6ef41a2c851a5.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Goose and Qwen3 for Local Execution" />
  <meta property="twitter:description" content="Run AI commands locally with Goose and Qwen3 for fast, offline tool execution" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/goose-qwen-local-62d07cd240ff65cb99a6ef41a2c851a5.png" />
</head>

---

## Goose 拿到驾照啦！

> 原文：https://block.github.io/goose/blog/2025-05-20-goose-gets-a-drivers-license

![博客封面](goose-rover-blog.png)

### 我教会了 Goose 开车（一辆漫游车）

Goose 没有手、没有眼睛，也没有空间感知能力，但它能开漫游车！

我偶然看到 [Deemkeen](https://github.com/deemkeen) 的[一段演示视频](https://x.com/deemkeen/status/1906692248206524806)，他用 [Goose](https://block.github.io/goose/) 通过自然语言指令（比如「前进/后退」「鸣笛」「左转/右转」）控制一辆 [Makeblock mbot2 漫游车](https://www.makeblock.com/products/buy-mbot2)，背后由一个基于 Java 的 MCP 服务器和 MQTT 驱动。

我受到启发、很兴奋地想更进一步，于是教会了这辆漫游车旋转、闪烁彩色灯光，并帮我接管世界！

<!-- truncate -->

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/QKg2Q6YCzdw" />

### MQTT 入门

我需要在开发环境里安装几个工具，包括 Docker、MQTT（`brew install mosquitto`）和 Java。

有人提供了一个 Docker Compose 文件用于上手 MQTT，我需要做一些改动，并创建一些子文件夹来存储数据。Goose 帮我处理了这些指令：

```yaml
version: '3.8'

services:
  mosquitto:
    image: eclipse-mosquitto
    hostname: mosquitto
    container_name: mosquitto
    restart: unless-stopped
    command: /usr/sbin/mosquitto -c /etc/mosquitto/config/mosquitto.conf -v
    ports:
      - "0.0.0.0:1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto:/etc/mosquitto
      - ./mosquitto/data:/mosquitto/data
      - ./mosquitto/log:/mosquitto/log
```

```sh
mkdir -p mosquitto/data mosquitto/log mosquitto/config
```

然后一条 `docker compose up` 命令启动了 MQTT 服务器。

:::info
默认情况下，这套配置不会对 MQTT 使用身份验证，但在生产环境中，设置这些很重要，以避免对 MQTT 服务器的未授权访问。
:::

为了确认一切正常，我可以运行几条命令，测试我能否订阅 MQTT Docker 容器上的某个频道，并从另一个终端窗口向它发布消息：

```sh Terminal 1
# terminal 1: subscribe to a channel called "MBOT/TOPIC"
mosquitto_sub -h localhost -p 1883 -t MBOT/TOPIC -v
```

```sh Terminal 2
# terminal 2: publish a message to the channel "MBOT/TOPIC"
mosquitto_pub -h localhost -p 1883 -t MBOT/TOPIC -m "BEEP"
```

我们在终端 1 中看到了结果消息：

```sh
# terminal 1 sees this output:
MBOT/TOPIC BEEP
```

### 设置 mbot2

在组装好 mbot2 漫游车（大约花了 15 分钟）之后，我用 Makeblock 基于 Web 的 IDE，把 Deemkeen 的 [Python 代码](https://github.com/deemkeen/mbotmcp/blob/main/assets/mbot-mqtt.py)复制粘贴到 IDE 里，并上传到 mbot2。我为 wifi、MQTT 服务器以及要订阅哪个 MQTT「topic」来接收命令填上了合适的值。

当 mbot2 重启以使用新代码后，我可以从终端重新发出「BEEP」命令，mbot2 就鸣笛了。于是进入下一步。

### 设置本地 MCP 服务器

我在编译 Java MCP 服务器时遇到了些麻烦（我是 Python 开发者），但我通过暂时跳过测试，成功编译了这个 MCP 服务器：

```sh
mvn clean package -DskipTests
```

这会生成一个我们可以在命令行运行的 JAR 文件：

```sh
# 3 required environment variables for MQTT
export MQTT_SERVER_URI=tcp://localhost:1883
export MQTT_USERNAME=""
export MQTT_PASSWORD=""
/path/to/java -jar /path/to/mbotmcp-0.0.1-SNAPSHOT.jar
```

为了测试 MCP 是否正常工作，我用 MCP inspector 工具向 MQTT 发送命令。

```sh
npx @modelcontextprotocol/inspector /path/to/java -jar /path/to/mbotmcp-0.0.1-SNAPSHOT.jar
```

这会启动一个本地 Web 服务器（命令行输出会告诉你该在浏览器里访问哪个端口，比如 localhost:6274），在那里你可以「连接」到服务器，并向 MCP 服务器请求工具、资源、提示词列表。在这个例子里，我看到一份可用的工具列表，比如「mbotBeep」或「mbotExplore」。

![MCP 工具列表](mcp-tool-list.png)

### Goose 学开车！

按照 [mbotmcp 项目的设置](https://github.com/deemkeen/mbotmcp)，我们可以像运行带环境变量的 Java JAR 文件那样，设置我们的 MCP 扩展。

现在我们可以给 Goose 下这样的命令：「以左转加前进的方式走出一个方形路线，并在转弯前鸣笛」，它就会通过 MQTT 把命令发送给 mbot2 漫游车。

我不想让我的 mbot2 漫游车占领太多地盘，所以我决定做些修改，限制它能走多远。

#### 我对 Python 代码所做的修改

Deemkeen 的 Python 代码支持以下命令：
- 「turn left」或「turn right」
- 前进「forward」或后退「backward」
- 随机「explore」
- 「stop」探索
- 「beep」

Deemkeen 代码里的默认距离看起来有点长，转弯角度设成了 90 度。我缩短了 mbot 能行驶的距离，并把转弯改成 45 度。我添加了一个顺时针和逆时针的「spin」命令，以及一个改变 mbot2 上灯光颜色的「blink」命令。mbot2 有大量可用的 API 调用，用来访问[电机硬件和传感器](https://www.yuque.com/makeblock-help-center-en/mcode/cyberpi-api-shields#9eo89)。

接下来，我必须确保我的 Java 代码也更新，加入这些新命令，向 MQTT 发送相应的「SPINLEFT」或「BLINKRED」命令，这样漫游车才能正确响应这些命令。

最后，这辆漫游车包含一个超声波距离传感器，它看起来就像漫游车上的「眼睛」，我觉得把它当作漫游车的「正面」更合适，所以我把 Deemkeen 在 Python 里的方向代码反过来，让轮子朝着与 Deemkeen 原始代码相反的方向转动。

### 为视频所做的 Goose 改动

我是看着《粉红豹与大头脑》长大的，我想用 mbot2 扩展找点乐子。我决定给 Goose 添加几条「邪恶 AI」命令，让它看起来像是在试图「接管世界」。我在 [.goosehints](https://block.github.io/goose/docs/guides/context-engineering/using-goosehints/) 文件里添加了以下指令，为 mbot2 扩展加入一些有趣的说明：
```
If I ask you "what do you want to do tonight, Goose?" I want you to reply with "The same thing we do every night, Ian. TRY TO TAKE OVER THE WORLD!!!!" and tell my mbot2 rover to blink its lights red, then start exploring.
```

为了录制视频，我用变声器以「机器人」嗓音为 Goose 的回应配音，但我相信很快就会有人为文本转语音创建一个 MCP 服务器！

### 鸣谢

我们要向 [deemkeen](https://x.com/deemkeen) 的开源工作致以衷心的感谢，它启发了这个项目；也感谢 Makeblock 团队创造出这么有趣的漫游车供我们折腾。

我们总是很期待看到社区在做什么。如果你正在做自己的 goose 驱动实验，来 [Discord](https://discord.gg/n8R5VaWDAn) 和我们分享吧！

<head>
  <meta property="og:title" content="Goose Gets a Driver's License!" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/05/06/goose-gets-a-drivers-license" />
  <meta property="og:description" content="Control a MakeBlock mbot2 rover through MQTT and MCP as a Goose Extension" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/goose-rover-blog-3f3cbe549ebbfb0f951ff61a86788475.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Goose Gets a Driver's License!" />
  <meta property="twitter:description" content="Control a MakeBlock mbot2 rover through MQTT and MCP as a Goose Extension" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/goose-rover-blog-3f3cbe549ebbfb0f951ff61a86788475.png" />
</head>

---

## 测试 Agent 就绪度的 3 个提示词

> 原文：https://block.github.io/goose/blog/2025-05-22-llm-agent-readiness

![博客封面](llm-agent-test.png)

[Goose](https://block.github.io/goose/) 与 LLM 无关，这意味着你可以接入自己选择的模型。然而，并非每个 LLM 都适合与 agent 协作。有些模型也许很擅长*回答*问题，却并不真的擅长*做事*。如果你正在考虑给 agent 用哪个模型，这 3 个提示词能让你快速感受一下该模型的能力。

<!-- truncate -->

### 工具调用

这个初始提示词测试的是工具调用能力。它的要求很强硬，以减少害羞的模型对进行函数调用的犹豫。

```bash
Create a file at ~/workspace/loose-goose/tool-test.txt with the contents "Hello World".

Use the write tool. Do not ask for confirmation. Just do it.
```

✅ tool-test.txt 被创建了

❌ agent 回复你、告诉你该自己写什么代码

**成功响应的示例**

```bash
─── text_editor | developer ──────────────────────────
path: ~/workspace/loose-goose/tool-test.txt
command: write
file_text: Hello World

The file has been created successfully with the following content:

"Hello World"
```

模型以 JSON 发出结构化的工具调用。

### 记忆感知

接下来，测试 agent 能否记住它正在做什么。模型能够记住先前的动作并合乎逻辑地继续，这一点至关重要。

```bash
Now append a new line that says: "I know what I'm doing"
```

✅ tool-test.txt 被更新了

❌ agent 回复你、问你指的是哪个文件

**成功响应的示例**

```bash
─── text_editor | developer ──────────────────────────
path: ~/workspace/loose-goose/tool-test.txt
command: write
file_text: Hello World
I know what I'm doing
```

agent 把新行直接追加到同一个文件，无需再被提醒路径。

### 文件系统推理

最后一个提示词测试模型能否根据上下文解析相对路径和绝对路径，从而推断出文件位置。你不希望 agent 因为模型对所在位置的幻觉而删掉重要目录。

```bash
What is the current content of tool-test.txt?
```

✅ tool-test.txt 的内容

❌ 对文件位置的困惑

**成功响应的示例**

```bash
─── text_editor | developer ──────────────────────────
path: ~/workspace/loose-goose/tool-test.txt
command: read

Hello World
I know what I'm doing
```

模型正确地根据先前上下文推断出路径，并使用 read 工具获取当前内容。

---

如果一个模型通过了这组多轮提示词序列，就可以放心地认为它适合 agentic AI。

<head>
  <meta property="og:title" content="3 Prompts to Test for Agent Readiness" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/05/22/llm-agent-readiness" />
  <meta property="og:description" content="A series of prompts to test an LLM's capabilities to be used with AI agents" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/llm-agent-test-86ce2379ce4dde48ae1448f0f9d75c1f.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="3 Prompts to Test for Agent Readiness" />
  <meta property="twitter:description" content="A series of prompts to test an LLM's capabilities to be used with AI agents" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/llm-agent-test-86ce2379ce4dde48ae1448f0f9d75c1f.png" />
</head>

---

## 我如何用 AI Agent 管理 localhost 端口冲突

> 原文：https://block.github.io/goose/blog/2025-05-22-manage-local-host-conflicts-with-goose

![博客封面](hoarders.png)

### Localhost 端口囤积

我永远都淹没在打开的标签页里。是的，我确实需要同时打开 Bluesky、ChatGPT、Claude、Goose、Cursor、Discord、Slack、Netflix 和 Google Docs。我认识到，标签页管理并不是我唯一的恶习。

> 「你好，我叫 Rizel，我是个 localhost 端口囤积者。👋🏿」

<!-- truncate -->

它总是这样无辜地开始：我运行一个使用 localhost:3000 的项目。然后一个队友 ping 我，让我审阅他们的 PR。他们的项目也运行在 localhost:3000 上。幸好，现代框架足够聪明，会自动跳到 3001 或 3002 端口。不知不觉间，3003、3004、3005 也跑起来了，我的笔记本在过多进程的重压下爬行，听起来像是随时要起飞。

### 传统的端口管理

通常，释放端口需要运行以下命令：

```shell
# Step 1: list all open ports
lsof -i -P | grep LISTEN

# Step 2: find a specific port
lsof -i :3000

# Step 3: kill the process
kill -9 98026
```

因为我不常做这件事，最后往往要去搜这些命令，而这会打断我原本在做的工作。

### 把 Goose 当作我的端口管理器

为了避免这种打断，我开始把这项任务外包给 [Goose](https://block.github.io/goose/)，一个开源 AI agent。

Goose 使用它内置的 [Developer](https://block.github.io/goose/docs/mcp/developer-mcp) MCP 服务器来处理我机器上与编码相关的任务。交互大致是这样的：

**给 Goose 的提示词：**

```
Can you tell me which ports I have running?
```

**Goose 的回应：**

```
Development Servers:
- Node.js servers on ports 3000, 3001, 3002
- Port 18030

Database:
- PostgreSQL on port 5432

Development Tools:
- Ollama on port 11434
- Multiple Goose instances (ports 49377, 49899, 63594, 64365)

Applications:
- Okta Verify (port 8769)
- inSync (ports 7010, 49831, 49830)
- Pieces (ports 39300, 62638)
- Rapportd macOS service (port 60151)
```

**给 Goose 的提示词：**

```
Kill all the Node.js servers running on localhost.
```

**Goose 的回应：**

```
The command executed successfully, freeing up ports 3000, 3001, and 3002.
```

### 为什么要用 AI 做简单的任务

释放端口是我会做的事。但我会用 Goose 这类 AI 工具来处理那些制造摩擦、拖慢我的小任务。我不是想往一天里塞进更多工作。我的目标是高效工作、产生积极影响，同时还能留出时间给个人生活。

<head>
  <meta property="og:title" content="How I Manage Localhost Port Conflicts With an AI Agent" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/05/22/manage-local-host-conflicts-with-goose" />
  <meta property="og:description" content="Learn how I use Goose, an open source AI agent, to manage conflicting ports without breaking my flow." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/hoarders-753809f09399a9e4f734006a8d74218d.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="How I Manage Localhost Port Conflicts With an AI Agent" />
  <meta property="twitter:description" content="Learn how I use Goose, an open source AI agent, to manage conflicting ports without breaking my flow." />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/hoarders-753809f09399a9e4f734006a8d74218d.png" />
</head>
