# goose 官方文档中文手册：第 23 章　博客（一）：2024-11 ~ 2025-03

## 截图驱动的开发

> 原文：https://block.github.io/goose/blog/2024-11-22-screenshot-driven-development

![calendar](https://block.github.io/goose/blog/2024-11-22-screenshot-driven-development/screenshot-driven-development.png)

我本质上是一名开发者，所以在做个人项目时，最难的部分并不是写代码——而是做设计决策。我最近构建了一个日历用户界面。我想提升它的视觉吸引力，于是研究了「glassmorphism」（玻璃拟态）和「claymorphism」（黏土拟态）这类 UI 设计趋势。

不过，我不想花上好几个小时去为每种设计趋势实现 CSS，于是我开发了一种更快的方法：截图驱动的开发。我用一个名为 [goose](https://github.com/aaif-goose/goose) 的开源开发者 agent 来快速改造我的用户界面。

<!-- truncate -->

:::warning goose Beta 版本
本文撰写时针对的是 goose 的 Beta 版本，命令与流程可能已发生变化。
:::

#### 我最初的日历：
![calendar](https://block.github.io/goose/blog/2024-11-22-screenshot-driven-development/screenshot-calendar-og.png)

#### goose 制作了下面这些设计原型：
![goose prototypes](https://block.github.io/goose/blog/2024-11-22-screenshot-driven-development/goose-prototypes-calendar.png)

在这篇博客中，我会向你展示如何通过让 goose 替你处理 CSS，来快速制作设计风格原型。
>💡 注意：你的结果可能与我的示例不同——这正是生成式 AI 的乐趣所在！每次运行都可能生成这些设计趋势的独特变体。

### 开始使用截图驱动的开发

#### 第 1 步：创建你的 UI
我们来创建一个基础 UI 来做实验。用下面的代码创建一个 index.html 文件：

<details>
<summary>用下面的代码创建一个 index.html 文件</summary>

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(45deg, #6e48aa, #9c27b0);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        .calendar {
            background: white;
            border-radius: 12px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            width: 400px;
            padding: 20px;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }

        .month {
            font-size: 24px;
            font-weight: 600;
            color: #1a1a1a;
        }

        .days {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 10px;
            margin-top: 20px;
            text-align: center;
        }

        .days-header {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 10px;
            margin-top: 20px;
            text-align: center;
        }

        .days-header span {
            color: #666;
            font-weight: 500;
            font-size: 14px;
        }

        .day {
            aspect-ratio: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            font-size: 14px;
            color: #333;
            cursor: pointer;
            transition: all 0.2s;
        }

        .day:hover {
            background: #f0f0f0;
        }

        .day.today {
            background: #9c27b0;
            color: white;
        }

        .day.inactive {
            color: #ccc;
        }
    </style>
</head>
<body>
    <div class="calendar">
        <div class="header">
            <div class="month">November 2024</div>
        </div>
        <div class="days-header">
            <span>Sun</span>
            <span>Mon</span>
            <span>Tue</span>
            <span>Wed</span>
            <span>Thu</span>
            <span>Fri</span>
            <span>Sat</span>
        </div>
        <div class="days">
            <div class="day inactive">27</div>
            <div class="day inactive">28</div>
            <div class="day inactive">29</div>
            <div class="day inactive">30</div>
            <div class="day inactive">31</div>
            <div class="day">1</div>
            <div class="day">2</div>
            <div class="day">3</div>
            <div class="day">4</div>
            <div class="day">5</div>
            <div class="day">6</div>
            <div class="day">7</div>
            <div class="day">8</div>
            <div class="day">9</div>
            <div class="day">10</div>
            <div class="day">11</div>
            <div class="day">12</div>
            <div class="day">13</div>
            <div class="day today">14</div>
            <div class="day">15</div>
            <div class="day">16</div>
            <div class="day">17</div>
            <div class="day">18</div>
            <div class="day">19</div>
            <div class="day">20</div>
            <div class="day">21</div>
            <div class="day">22</div>
            <div class="day">23</div>
            <div class="day">24</div>
            <div class="day">25</div>
            <div class="day">26</div>
            <div class="day">27</div>
            <div class="day">28</div>
            <div class="day">29</div>
            <div class="day">30</div>
        </div>
    </div>
</body>
</html>
```
</details>

保存后，在浏览器中打开该文件。你应该会看到一个日历！

#### 第 2 步：安装 goose

```bash
brew install pipx
pipx ensurepath
pipx install goose-ai
```

#### 第 3 步：启动一个会话

```bash
goose session start
```

##### 自带你的 LLM

>goose 会在你首次运行此命令时提示你设置 API key。你可以使用 OpenAI 或 Anthropic 等各种 LLM 提供方

```bash
export OPENAI_API_KEY=your_api_key
# Or for other providers:
export ANTHROPIC_API_KEY=your_api_key
```

#### 第 4 步：启用 Screen 工具包
goose 使用[工具包](https://goose-docs.ai/plugins/plugins.html)来扩展自身能力。[screen](https://goose-docs.ai/plugins/available-toolkits.html#6-screen-toolkit) 工具包让 goose 能够截取并分析屏幕截图。

要启用 Screen 工具包，请把它添加到位于 ~/.config/goose/profiles.yaml 的 goose profile 中。

> 你的配置可能会因 LLM 提供方偏好而略有不同。


```yaml
default:
  provider: openai
  processor: gpt-4o
  accelerator: gpt-4o-mini
  moderator: truncate
  toolkits:
  - name: developer
    requires: {}
  - name: screen
    requires: {}
```

#### 第 5 步：让 goose 截取你的 UI 截图
goose 通过屏幕截图来分析你的 UI，以理解其结构和元素。在你的 goose 会话中，通过指定 UI 所在的显示器，让 goose 截取一张屏幕截图：

```bash
Take a screenshot of display(1)  
```

> 显示器编号是必填的——主显示器用 display(1)，副显示器用 display(2)。

成功后，goose 会运行 `screencapture` 命令并将其保存为临时文件。

#### 第 6 步：让 goose 改造你的 UI

现在，你可以让 goose 应用不同的设计风格。以下是我给 goose 的一些提示词以及它产出的结果：

##### 玻璃拟态

```bash
Apply a glassmorphic effect to my UI
```

![glassmorphism](https://block.github.io/goose/blog/2024-11-22-screenshot-driven-development/glassmorphism-calendar.png)


##### 新拟态

```bash
Apply neumorphic effects to my calendar and the dates
```

![neumorphism](https://block.github.io/goose/blog/2024-11-22-screenshot-driven-development/neumorphism-calendar.png)


##### 黏土拟态

```bash
Please replace with a claymorphic effect
```

![claymorphism](https://block.github.io/goose/blog/2024-11-22-screenshot-driven-development/claymorphism-calendar.png)


##### 粗野主义

```bash
Apply a brutalist effect please
```

![brutalism](https://block.github.io/goose/blog/2024-11-22-screenshot-driven-development/brutalism-calendar.png)

### 了解更多

开发用户界面是创造力与解决问题的结合。而我喜欢用 goose 的一点是，它让我有更多时间专注于创造力，而不是花上几个小时与 CSS 较劲。

除了制作原型之外，goose 分析屏幕截图的能力还能帮助开发者定位并解决 UI bug。

如果你想了解更多，可以看看 [goose 仓库](https://github.com/aaif-goose/goose)，并加入我们的 [Discord 社区](https://discord.gg/n8R5VaWDAn)。

<head>
    <meta property="og:title" content="Screenshot-Driven Development" />
    <meta property="og:type" content="article" />
    <meta property="og:url" content="https://goose-docs.ai/blog/2024/11/22/screenshot-driven-development" />
    <meta property="og:description" content="AI Agent uses screenshots to assist in styling." />
    <meta property="og:image" content="https://goose-docs.ai/assets/images/screenshot-driven-development-4ed1beaa10c6062c0bf87e2d27590ad6.png" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta property="twitter:domain" content="goose-docs.ai" />
    <meta property="twitter:title" content="Screenshot-Driven Development" />
    <meta property="twitter:description" content="AI Agent uses screenshots to assist in styling." />
    <meta name="twitter:image" content="https://goose-docs.ai/assets/images/screenshot-driven-development-4ed1beaa10c6062c0bf87e2d27590ad6.png" />
</head>

---

## 预览 goose v1.0 Beta

> 原文：https://block.github.io/goose/blog/2024-12-06-previewing-goose-v10-beta

![goose v1.0 Beta](https://block.github.io/goose/blog/2024-12-06-previewing-goose-v10-beta/goose-v1.0-beta.png)
我们很兴奋地分享随 goose v1.0 Beta 一同到来的新更新预览！

这次重大更新带来了大量新功能与改进，让 goose 更强大、更易用。以下是其中一些关键亮点。

<!-- truncate -->


### goose 1.0 Beta 的激动人心的特性

#### 1. 迁移到 Rust

goose 的核心已用 Rust 重写。为什么这很重要？Rust 带来了更可移植、更稳定的体验。这一变化意味着 goose 可以在不同系统上顺畅运行，而无需安装 Python，让任何人都更容易上手使用它。

#### 2. 上下文记忆

goose 会记住先前的交互，从而更好地理解正在进行的项目。这意味着你不必反复重复自己。想象一下与一个记得每个细节的人对话——这正是 goose 想要提供的支持。

#### 3. 改进的插件系统

在 goose v1.0 中，goose 工具包系统正被扩展（Extensions）取代。扩展是模块化的守护进程，goose 可以与它们动态交互。因此，goose 将能够支持更复杂的插件与集成。这将让用新功能和新特性扩展 goose 变得更加容易。

#### 4. 无头模式

你现在可以以无头模式运行 goose——这对于在服务器上、或没有图形界面的环境中运行 goose 很有用。

```sh
cargo run --bin goose -- run -i instructions.md
```

#### 5. goose 现在有了 GUI

goose 现在有了一个基于 Electron 的 GUI macOS 应用，为 CLI 之外提供了一种与 goose 交互、管理项目的替代方式。

![goose GUI](https://block.github.io/goose/blog/2024-12-06-previewing-goose-v10-beta/goose-gui.png)

#### 6. goose 与开放协议对齐

goose v1.0 Beta 现在使用一套自定义协议，它与 [Anthropic 的 Model Context Protocol](https://www.anthropic.com/news/model-context-protocol)（MCP）并行设计，用于与系统通信。这使开发者可以创建自己的、Goose 能够集成的系统（例如 Jira）。

期待更多功能更新与改进？请持续关注 goose 的更多更新！看看 [goose 仓库](https://github.com/aaif-goose/goose)，并加入我们的 [Discord 社区](https://discord.gg/n8R5VaWDAn)。


<head>
  <meta property="og:title" content="Previewing Goose v1.0 Beta" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2024/12/06/previewing-goose-v10-beta" />
  <meta property="og:description" content="AI Agent uses screenshots to assist in styling." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/goose-v1.0-beta-5d469fa73edea37cfccfe8a8ca0b47e2.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta name="twitter:title" content="Screenshot-Driven Development" />
  <meta name="twitter:description" content="AI Agent uses screenshots to assist in styling." />
  <meta name="twitter:image" content="https://goose-docs.ai/assets/images/goose-v1.0-beta-5d469fa73edea37cfccfe8a8ca0b47e2.png" />
</head>

---

## 用 MCP 把 AI Agent 连接到你的系统

> 原文：https://block.github.io/goose/blog/2024-12-10-connecting-ai-agents-to-your-systems-with-mcp

![mcp](https://block.github.io/goose/blog/2024-12-10-connecting-ai-agents-to-your-systems-with-mcp/goose-mcp.png)

开放标准是可互操作系统的关键要素。我们所有人所依赖的大多数技术，都是由它们成就的。无论身处何地都能连接互联网，靠的是 Wi-Fi、TCP/IP 和 DNS 这样的开放标准。当你在 Gmail 账户中收到来自 Outlook 发件人的邮件时，正是 SMTP、IMAP 和 POP3 这样的开放标准让这一切无缝衔接。我们这一生中最具变革性的技术之一——互联网——正是得益于 HTTP 和 HTML 标准，让任何人都能让自己的网页被全世界访问。

我们正处于科技新时代的早期，在这个时代，各公司正在为大众创新并构建实用的 AI 解决方案。为了确保这项技术的长久生命力，开放标准对于引导 AI 工具的开发至关重要，这样各家公司构建的多样化系统才能无缝协作。

<!-- truncate -->

:::warning goose Beta 版本
本文撰写时针对的是 goose 的 Beta 版本，命令与流程可能已发生变化。
:::

#### MCP 开放标准

Anthropic 正引领这一潮流，推出了 [Model Context Protocol（MCP）](https://modelcontextprotocol.io)，这是一个开放标准，能让大语言模型（LLM）应用连接到外部系统，为更明智、更相关的 AI 交互提供必要的上下文。

对于像 [goose](https://goose-docs.ai/) 这样能够自主执行任务的 AI agent 来说，这是一项颠覆性的变革——相较只提供分步指令的聊天机器人，这是巨大的飞跃。然而，要释放这些 AI agent 的全部潜力，我们需要一种标准方法来把它们连接到外部数据源。MCP 提供了这一基础。

借助 MCP 标准化的 API 和端点，goose 可以无缝集成到你的系统中，增强其执行复杂任务的能力，例如直接在你的环境中调试、编写代码和运行命令。

![goose Framework](https://block.github.io/goose/blog/2024-12-10-connecting-ai-agents-to-your-systems-with-mcp/goose-framework-1.0.png)

#### 有哪些可能性

没有 MCP 时，每个 [goose 工具包](https://goose-docs.ai/plugins/using-toolkits.html)开发者都需要为他们要连接的每个系统实现定制的集成。这不仅枯燥、重复，还会拖延那些真正有趣的事。

举个简单的 GitHub 工作流为例。goose 使用自定义脚本或配置直接与 GitHub API 交互。开发者必须配置 goose 以便与 GitHub 认证，并指定获取开放 pull request 或添加评论等操作的端点。每个集成都需要手动设置和自定义编码，以处理认证令牌、错误处理和 API 更新。

MCP 通过提供一套标准化的接口，把 GitHub 作为资源来访问，从而简化了这一过程。goose 作为 [MCP 客户端](https://modelcontextprotocol.io/clients)，从一个配置为暴露 GitHub 能力的 [MCP 服务器](https://modelcontextprotocol.io/quickstart#general-architecture)请求所需信息（例如开放的 pull request 列表）。MCP 服务器负责认证以及与 GitHub 的通信，将 API 交互的复杂性抽象掉。于是 goose 就可以专注于提供详细的评审评论或建议代码改动等任务。

#### 加入这个生态

随着 MCP 采用范围的扩大，goose 为你的组织提供更强大解决方案的潜力也在增长。通过把 [goose 集成](https://goose-docs.ai/)到你的工作流中，并[拥抱 MCP](https://modelcontextprotocol.io/introduction)，你不仅是在增强自己的系统，更是在为一个让 AI 工具更加可互操作、更高效、更具影响力的生态的成长做出贡献。



<head>
  <meta charset="UTF-8" />
  <title>Connecting AI Agents to Your Systems with MCP</title>
  <meta name="description" content="goose" />
  <meta name="keywords" content="MCP, Anthropic, AI Open Standards" />


  <!-- HTML Meta Tags -->
  <title>Connecting AI Agents to Your Systems with MCP</title>
  <meta name="description" content="Learn how MCP standardizes integrations and fosters an ecosystem for the future of AI-enabled tools." />

  <!-- Facebook Meta Tags -->
  <meta property="og:url" content="https://goose-docs.ai/blog/2024/12/10/connecting-ai-agents-to-your-systems-with-mcp" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="Connecting AI Agents to Your Systems with MCP" />
  <meta property="og:description" content="Learn how MCP standardizes integrations and fosters an ecosystem for the future of AI-enabled tools." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/goose-mcp-34a5252d18d18dff26157d673f7af779.png" />

  <!-- Twitter Meta Tags -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="aaif-goose.github.io" />
  <meta property="twitter:url" content="https://goose-docs.ai/blog/2024/12/10/connecting-ai-agents-to-your-systems-with-mcp" />
  <meta name="twitter:title" content="Connecting AI Agents to Your Systems with MCP" />
  <meta name="twitter:description" content="Learn how MCP standardizes integrations and fosters an ecosystem for the future of AI-enabled tools." />
  <meta name="twitter:image" content="https://goose-docs.ai/assets/images/goose-mcp-34a5252d18d18dff26157d673f7af779.png" />
</head>

---

## 用 goose 解决 CI 问题：一次实战演练

> 原文：https://block.github.io/goose/blog/2024-12-11-resolving-ci-issues-with-goose-a-practical-walkthrough

![CI](https://block.github.io/goose/blog/2024-12-11-resolving-ci-issues-with-goose-a-practical-walkthrough/goose-github-ci.png)

在 pull request 中遇到持续集成（CI）失败可能相当令人沮丧，但这种情况非常常见。在这篇文章中，我们借助 goose 使用 GitHub CLI（`gh`）来简化你的 CI 调试流程，直接从 GitHub 获取失败 CI 运行与注解（annotation）的详细信息，甚至直接应用修复。

<!-- truncate -->

:::warning goose Beta 版本
本文撰写时针对的是 goose 的 Beta 版本，命令与流程可能已发生变化。
:::


### 快速上手

在深入之前，请确保你已配置好必要的工具。

#### 1. 安装并认证 GitHub CLI（`gh`）

你需要 [GitHub CLI](https://cli.github.com/) `gh`，以便让 goose 访问 CI 检查运行的详细信息。

```bash
brew install gh
gh auth login
```

按照提示认证你的账户。


#### 2. 配置 goose
确保 goose 已配置好，并准备好与你的仓库和本地工具交互。具体来说，你需要配置一个带有 GitHub 工具包的 goose profile。

在 `~/.config/goose` 中更新你的 `profiles.yaml` 文件，加入必要的工具包：

```yaml
my-profile:
  provider: anthropic
  processor: claude-3-5-sonnet
  accelerator: claude-3-5-sonnet
  moderator: truncate
  toolkits:
    - name: developer
      requires: {}
    - name: github
      requires: {}
```
用该 profile 启动一个会话：

```bash
goose session start --profile my-profile
```
如果该 profile 的工具包配置不正确，goose 可能无法访问 `gh` 命令。

### 用 goose 解决 CI 失败
一切就绪之后，我们现在就可以用以下步骤让 goose 来应对 CI 问题了：

#### 第 1 步：获取 CI 失败详情
让 goose 检索某个特定 PR 的 CI 失败信息。

**示例请求：**

```

Can you tell me about the CI failures on PR #11111 in the organization/repo repository? The check run ID is 123456.
```

你可以通过点击某个 PR 的 checks 标签页并选择一个失败项来获取 check run ID。该 ID 会出现在 URL 中。

**goose 的工作流：**

goose 将使用 `gh` CLI 来检查运行信息，并提供问题的详细摘要。goose 使用 GitHub CLI 来：

- 获取失败 CI 运行的详细信息，包括日志和注解。
- 提供清晰、可操作的问题摘要。

**goose 运行的示例命令：**

```curl
gh api -H "Accept: application/vnd.github+json" /repos/<owner>/<repo>/check-runs/<check-run-id>/annotations
```

**goose 示例输出：**
```mathematica
Here are the details for Check Run ID 123456:

**Name**: CI-Build-All  
**Status**: completed  
**Conclusion**: failure  

**Annotations Summary:**  
1. **ModuleA Test Failure**  
   File: `ModuleATests`  
   Line: 35  
   Error: Mismatched parameter order in function call.  

2. **ModuleB Test Failure**  
   File: `ModuleBTests`  
   Line: 64  
   Error: Unexpected nil value encountered during initialization.  

3. **ModuleC Test Failure**  
   File: `ModuleCTests`  
   Line: 98  
   Error: Type mismatch in returned value. Expected 'String', found 'Int'.  
```
#### 第 2 步：让 goose 修复
一旦 goose 提供了失败详情，就让它直接解决这些问题。

示例请求：

```
Can you fix these issues and stage the changes so I can review them? Do not add unnecessary code comments.
```

**goose 会做什么：**

- 根据错误信息应用修复。
- 暂存改动以供审查。


**goose 示例回复：**
```markdown
I have fixed the following files and staged them:

- `ModuleATests`: Corrected the order of parameters in the function call.  
- `ModuleBTests`: Resolved the unexpected nil value encountered during initialization.  
- `ModuleCTests`: Adjusted the type mismatch in the returned value.  

You can now review the staged changes.
```


#### 第 3 步：审查改动
仔细审查已暂存的改动，确保它们正确解决了问题，并避免出现非预期的修改。

**需要检查的事项：**

- 没有多余的注释（例如 // Fix xyz）。
- 没有对代码中不相关部分的改动。


如有需要，在提交前清理或重新暂存改动。

### 使用 goose 的好处
使用 goose 解决 CI 问题可以简化你的工作流，方法是：

- 以最少的人工投入识别问题并应用修复。
- 与 GitHub CLI 等工具集成以验证改动。
- 在你专注于代码质量的同时，处理重复性的 CI 调试任务。

goose 让你能够高效地解决 CI 失败，在减少调试和测试所需精力的同时，让你对自己的工作流充满信心。

试一试，让 goose 为你承担 CI 调试的重活吧！

<head>
  <meta property="og:title" content="Resolving CI Issues with goose: A Practical Walkthrough" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2024/12/11/resolving-ci-issues-with-goose-a-practical-walkthrough" />
  <meta property="og:description" content="Leverage goose to simplify your CI debugging process, fetch detailed information about failed CI runs & annotations directly from GitHub, and even apply fixes directly." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/goose-github-ci-30930008ab57b0aebae15a03c73a12b5.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Resolving CI Issues with goose: A Practical Walkthrough" />
  <meta name="twitter:description" content="Leverage goose to simplify your CI debugging process, fetch detailed information about failed CI runs & annotations directly from GitHub, and even apply fixes directly." />
  <meta name="twitter:image" content="https://goose-docs.ai/assets/images/goose-github-ci-30930008ab57b0aebae15a03c73a12b5.png" />
</head>

---

## 介绍 codename goose

> 原文：https://block.github.io/goose/blog/2025-01-28-introducing-codename-goose

![Introducing codename goose](https://block.github.io/goose/blog/2025-01-28-introducing-codename-goose/introducing-codename-goose.png)

我们非常激动地宣布 **codename goose**——你的机器上运行的开源 AI agent，专为自动化你的任务而构建。

由你选择的[大语言模型（LLM）](https://block.github.io/goose/docs/getting-started/providers)驱动，配备友好的桌面界面与 CLI，并通过与你现有工具和应用集成的[扩展](https://block.github.io/goose/docs/getting-started/using-extensions)来运作，goose 旨在提升你的生产力和工作流。

<!--truncate-->


你可以把 goose 想象成一个随时准备接受你的指令、替你干活的助手。

虽然 goose 最初的使用场景聚焦于工程领域，但社区也一直在探索 goose 在非工程领域的其他用法。不言而喻，goose 是[开源的](https://github.com/aaif-goose/goose) 🎉。


### goose 如何工作

goose 作为一个智能、自主的 agent 运作，通过对其核心特性的良好编排协调，能够处理复杂任务：

- **使用扩展**：[扩展](https://block.github.io/goose/docs/getting-started/using-extensions)是 goose 适应性的关键，让你能够连接到已经在使用的应用和工具。无论是连接到 GitHub、访问 Google Drive，还是与 JetBrains IDE 集成，可能性都非常广泛。其中一些扩展已被收录在[扩展][extensions-directory]目录中。goose 扩展构建在 [Model Context Protocol（MCP）](https://www.anthropic.com/news/model-context-protocol)之上——让你能够为 goose 构建或引入你自己的自定义集成。

- **LLM 提供方**：goose 兼容多种 [LLM 提供方](https://block.github.io/goose/docs/getting-started/providers)，让你可以选择并集成你偏好的模型。

- **CLI 与桌面支持**：你可以把 goose 作为桌面应用运行，也可以通过命令行界面（CLI）运行，两者使用相同的配置。

### goose 实战

goose 能够处理从简单到复杂的各种任务，横跨多个工程领域。以下是 goose 帮助过人们的一些任务示例：

- 进行代码迁移，例如 Ember 到 React、Ruby 到 Kotlin、Prefect-1 到 Prefect-2 等。
- 深入一个用不熟悉的编程语言编写的新项目
- 在依赖注入框架中，把代码库从基于字段的注入迁移到基于构造器的注入。
- 使用构建自动化工具为某个构建命令进行性能基准测试
- 把代码覆盖率提升到某个特定阈值以上
- 为数据留存搭建 API 脚手架
- 创建 Datadog 监控
- 移除或添加功能开关等。
- 为某个功能生成单元测试

### 快速上手

你可以立即开始使用 goose！看看我们的[快速开始](https://block.github.io/goose/docs/quickstart)。


### 加入 goose 社区

对即将到来的功能和活动感到期待？一定要与我们保持联系！

- [GitHub](https://github.com/aaif-goose/goose)
- [Discord](https://discord.gg/n8R5VaWDAn)
- [YouTube](https://www.youtube.com/@goose-oss)
- [LinkedIn](https://www.linkedin.com/company/goose-oss)
- [X](https://x.com/goose_oss)
- [BlueSky](https://bsky.app/profile/opensource.block.xyz)


[extensions-directory]: https://goose-docs.ai/v1/extensions


<head>
  <meta property="og:title" content="Introducing codename goose" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2024/12/11/resolving-ci-issues-with-goose-a-practical-walkthrough" />
  <meta property="og:description" content="codename goose is your open source AI agent, automating engineering tasks and improving productivity." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/introducing-codename-goose-89cac25816e0ea215dd47d4b9768c8ab.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Introducing codename goose" />
  <meta name="twitter:description" content="codename goose is your open source AI agent, automating engineering tasks and improving productivity." />
  <meta name="twitter:image" content="https://goose-docs.ai/assets/images/introducing-codename-goose-89cac25816e0ea215dd47d4b9768c8ab.png" />
</head>

---

## Agentic AI 与 MCP 生态

> 原文：https://block.github.io/goose/blog/2025-02-17-agentic-ai-mcp

![blog banner](https://block.github.io/goose/blog/2025-02-17-agentic-ai-mcp/agentic-ai-with-mcp.png)

仿佛就在昨天，我们所有人都还在为生成式 AI、尤其是那些让普通人也能与大型语言模型（LLM）交互的聊天界面而惊叹。

尽管这已经很了不起了，但这只是开始。下一波 AI 是 agentic 的，也就是说，这些 AI 系统不只是对提示词做出回应，还会采取行动、做出决策，并与外部系统交互。这是通过 **AI agent** 来实现的。

<!--truncate-->

### 什么是 AI Agent？

当你与使用 AI 的聊天机器人（比如 ChatGPT）交互时，你可以问它如何做某件事，它会给出分步指令。

例如，如果我在写代码时遇到一个错误，我可以把错误信息粘贴到 ChatGPT 里，让它帮我调试。由于 ChatGPT 无法访问我的代码库，它会推测我出错的原因，并给我几个可能有效的解决方案让我尝试。然后我会手动尝试这些建议的方案，再回来把结果告诉 ChatGPT。我们会这样来回往复，直到错误被解决，或者我放弃为止。

AI agent 通过代表我与 LLM 对话、并直接采取行动来解决问题，极大地简化了这一流程。

> _**AI agent 是一个自主运作以完成某个目标的系统。**_

由于 AI agent 连接到各种系统，它们可以分析情况、确定下一步行动，并在几乎无需（如果有的话）人工干预的情况下执行它。这种能力让它们从被动的聊天机器人变成了自动化助手。

通过使用 AI agent，我可以简单地说「修复这个错误」，它就会掌握哪里出了问题，并自动替我修复错误。

### AI Agent 如何与 LLM 协同工作

LLM（例如 GPT-4o、Claude 3.5 Sonnet、Gemini 2.0 等）为 AI agent 提供认知能力。大多数 AI agent 本身会有一个聊天界面，你在其中输入提示词，agent 会把该提示词发送给 LLM。同时，agent 还会告知 LLM 它可以访问哪些**工具**。

#### 工具调用

工具是 agentic AI 最重要的方面之一。AI agent 能够通过**工具调用**执行 API 调用。

来看一个例子：

1. 用户向自己的 AI agent 发送一个提示词：_「修复我的 UserService.java 文件中的 NullPointerException。」_

2. agent 把用户请求以及它可用工具的列表，以结构化格式发送给 LLM。
```
User Request: "Fix the NullPointerException in my UserService.java file."

Available Tools:
1. read_file(file_path: str) → Returns the contents of the specified file.
2. analyze_code(file_content: str) → Identifies potential errors and suggests fixes.
3. edit_file(file_path: str, modifications: dict) → Applies code changes.
4. run_tests() → Executes the test suite and returns results.
```

3. LLM 分析该请求并选择合适的工具。它判断需要先读取文件才能提供帮助。
```json
[
  {
    "tool": "read_file",
    "parameters": { "file_path": "UserService.java" }
  }
]
```

4. agent 执行 `read_file()`，并把代码发送给 LLM。
```java
public class UserService {
    private Database db;

    public void getUser(String userId) {
        System.out.println(db.findUserById(userId).getName());
    }
}
```

5. LLM 识别出问题（`db` 变量未初始化），现在选择另一个工具来修复该问题。
```json
[
  {
    "tool": "edit_file",
    "parameters": {
      "file_path": "UserService.java",
      "modifications": {
        "line_number": 3,
        "replacement": "private Database db = new Database();"
      }
    }
  }
]
```

6. agent 执行 `edit_file()` 来修复 `UserService.java`，并告知 LLM。

7. LLM 判断运行测试来确认改动是个好主意。
```json
[
  {
    "tool": "run_tests",
    "parameters": {}
  }
]
```

8. agent 执行 `run_tests()`，并把结果提供给 LLM。
```json
{
  "tests_passed": true,
  "failed_tests": []
}
```

9. LLM 生成一条最终消息，agent 随后将其呈现给用户。
```
I’ve fixed the NullPointerException in UserService.java by initializing the db variable. All tests have passed. Let me know if you need further modifications!
```

如果没有工具调用，LLM 只能根据它们的训练数据猜测答案。但通过使用工具，agent 可以直接访问所需的数据，从而做出准确的决策并采取行动。

值得注意的是，在工具访问方面，并非所有 agent 都一样。大多数专有 agent 都被严格限定在某个特定的 LLM 和一组预定义工具上，因为各公司构建的 agent 是为自己的应用量身定制的。

其他 agent（比如 goose）则更具可扩展性，允许用户用它选择的 LLM 来配置它，还能为各种 API、数据库，甚至[本地环境（如 IDE）](https://block.github.io/goose/docs/mcp/jetbrains-mcp)添加工具。然而，要让 agent 在不需为每个工具和系统都编写定制集成的情况下跨不同工具和系统扩展，它们需要一种标准化的方式来发现、调用和管理工具。这正是 [Model Context Protocol（MCP）](https://modelcontextprotocol.io/introduction)所提供的。

### MCP 生态

传统的 AI 集成需要为每个系统编写自定义 API 调用，这让扩展变得困难。MCP 通过提供一个开放、通用的协议，让 agent 能够动态地与外部系统通信，从而解决了这一问题。

有了 MCP，像 goose 这样的 agent 可以：

* 无需开发者编写手动集成代码，就能连接到任何 API
* 与云服务、开发工具、数据库和企业系统集成
* 检索并存储上下文以增强推理能力

在撰写本文时，已有超过 [1000 个 MCP 服务器](https://www.pulsemcp.com/servers)（即暴露工具的系统）可供任何支持 MCP 的 AI agent（如 goose）连接！这些 MCP 服务器充当 agent 与外部系统之间的桥梁，使访问 API、数据库和开发环境成为可能。其中一些由官方 API 提供方开发，而绝大多数由社区成员开发。由于 MCP 是一个开放标准，任何人都可以为任何资源构建 MCP 服务器。这极大地增加了 AI agent 的可能性！

例如，假设我想让 goose 根据一份 Figma 设计稿，在我的 WebStorm IDE 中开发一个新的 Web 应用，然后把代码提交到 GitHub 上的一个新仓库。我可以添加以下 MCP 服务器作为 goose 扩展，赋予它所有这些能力：

* [Figma](https://block.github.io/goose/docs/mcp/figma-mcp)
* [JetBrains](https://block.github.io/goose/docs/mcp/jetbrains-mcp)
* [GitHub](https://block.github.io/goose/docs/mcp/github-mcp)

有了这些，我就可以用自然语言给我的 AI agent 下达提示，它会替我把活干了：

> _「根据文件 ID 为 XYZ 的 Figma 设计稿，在 WebStorm 中构建一个 Web 应用，并把代码提交到一个名为 angiejones/myapp 的新 GitHub 仓库」_

相当强大，对吧？！

### 开始使用 AI Agent
希望这篇文章已经让你清楚地了解了什么是 AI agent、它们如何工作，以及它们能为你带来什么。[goose](https://block.github.io/goose/docs/getting-started/installation) 免费且开源，你可以随心所欲地添加[扩展](https://block.github.io/goose/docs/getting-started/using-extensions#adding-extensions)。这是开始接触 AI agent 的绝佳方式，看看它们如何自动化你工作流中的任务，让你更高效。


<head>
  <meta property="og:title" content="Agentic AI and the MCP Ecosystem" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/02/17/agentic-ai-mcp" />
  <meta property="og:description" content="A 101 introduction to AI Agents" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/agentic-ai-with-mcp-1e3050cc8d8ae7a620440e871ad9f0d2.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Agentic AI and the MCP Ecosystem" />
  <meta name="twitter:description" content="A 101 introduction to AI Agents" />
  <meta name="twitter:image" content="https://goose-docs.ai/assets/images/agentic-ai-with-mcp-1e3050cc8d8ae7a620440e871ad9f0d2.png" />
</head>

---

## 让一支 AI Agent 团队替你干活

> 原文：https://block.github.io/goose/blog/2025-02-21-gooseteam-mcp

![blog banner](https://block.github.io/goose/blog/2025-02-21-gooseteam-mcp/gooseteam-mcp.png)

在[上一期直播](https://youtu.be/9tq-QUnE29U)中，Cash App 的基础设施运维工程师 Aaron Goldsmith 展示了一支 goose AI agent 团队实时协作创建网站。我们的社区非常喜欢这个点子，Cliff Hall 受到启发，在此基础上迭代，创建了一个 gooseTeam MCP 服务器。

<!--truncate-->

### 最初的协议

Aaron Goldsmith 用他轻量级的 [Agent Communication Protocol](https://gist.github.com/AaronGoldsmith/114c439ae67e4f4c47cc33e829c82fac)，把由多个 goose 实例组成的 AI agent 团队变成了现实。有了它，每个 goose agent 进入聊天，被分配一个角色（例如项目协调员、研究员、Web 开发者），并负责某个给定任务中属于自己的那部分。该协议规定了指导 agent 如何交谈和行事的指令，让多个 goose agent 能够协作。它还规定，agent 之间的通信应通过一个基于 Python 的 websocket 服务器，使用 text/markdown 进行。

### gooseTeam MCP 服务器

隆重介绍 [gooseTeam](https://github.com/cliffhall/gooseTeam)，它由软件架构师、社区成员 Cliff Hall 创建。gooseTeam 采纳了 Aaron 的协议，并将其迭代为一个用于 goose agent 的 MCP 服务器和协作协议。借助任务管理、消息存储和 agent 等待等功能，你可以让一整支 goose agent 团队替你协作完成某个任务或项目。

一个担任项目协调员角色的 goose agent 会给其他 agent 分配角色，你连接的那些 agent 会发送可随时检索的消息，而你的 agent 团队会连接到同一个 MCP 服务器来一起协作。

![goose Agents](https://block.github.io/goose/blog/2025-02-21-gooseteam-mcp/gooseteam-agents.png)

### 使用 goose 的新方式

与一支 AI agent 团队一起完成任务，是一种颠覆性的体验。你不必再困惑于如何靠自己改进提示词工程，或手动地跨会话协作，像 Cliff 的 gooseTeam 或 Aaron 的 Agent Communication Protocol 这样的工具，能帮助我们确保像 goose 这样的 AI agent 尽可能高效地替我们干活。可能性仿佛无穷无尽！

### 让你的贡献获得展示
希望这份贡献带给你的启发，就像它带给我们的社区的一样多。如果你有想要与我们的社区分享的 goose 贡献或项目，加入我们的 [Discord](https://discord.gg/n8R5VaWDAn)，在 **#share-your-work** 频道分享你的作品。你也许会在我们的直播中获得展示，或者拿到一份很酷的奖品。👀 你也可以在 GitHub 上给 goose 点星，或在社交媒体上关注我们，这样就不会错过我们的任何更新。下次见！


<head>
  <meta property="og:title" content="Let A Team of AI Agents Do It For You" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/02/17/gooseteam-mcp" />
  <meta property="og:description" content="Community Spotlight on Cliff Hall's gooseTeam MCP server." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/gooseteam-mcp-082fa2890c313519c2a1637ca979c219.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Let A Team of AI Agents Do It For You" />
  <meta name="twitter:description" content="Community Spotlight on Cliff Hall's gooseTeam MCP server." />
  <meta name="twitter:image" content="https://goose-docs.ai/assets/images/gooseteam-mcp-082fa2890c313519c2a1637ca979c219.png" />
</head>

---

## 使用 goose 的 6 条必备技巧

> 原文：https://block.github.io/goose/blog/2025-03-06-goose-tips

![goose tips](https://block.github.io/goose/blog/2025-03-06-goose-tips/goose-tips.png)

与 AI agent 打交道有时会让人觉得难以预测。在大量使用 goose 几个月之后，我整理出了一些关键技巧，能帮你最大限度地发挥这个工具的作用。无论你的工作流是什么，这些准则都能帮你更高效地与 goose 协作。


<!--truncate-->

### 1. 让会话保持专注且简短

用户最常犯的错误之一，就是试图在单个会话里完成太多事情。虽然让对话一直进行下去看起来似乎很高效，但更长的会话实际上可能反而妨碍 goose 的表现。

每条消息都会加入上下文窗口，也就是 goose 在任一时刻能保留的对话历史量。这段历史由 token 组成，即 goose 为生成回答而处理的文本片段（单词甚至单词的一部分）。更多 token 不仅会增加处理时间，还会推高 LLM 的使用成本。而一旦上下文窗口被填满，较早的消息就会被挤出，这可能导致重要细节丢失或出现意外行为。

把它想象成同时打开太多浏览器标签页。最终，它会拖累性能。相反，应该为不同的任务开启全新的会话。不必担心丢失上下文；[Memory 扩展](https://block.github.io/goose/docs/mcp/memory-mcp)正是为此而生的。让会话保持专注、简洁，能确保回答更准确、更相关，同时也让你的 LLM 成本处于可控范围。


### 2. 尽量减少启用的扩展

说到 goose 扩展，往往是少即是多。人们很容易为了以防万一而启用[每一个可用的扩展](https://www.pulsemcp.com/servers)（我自己也犯过这个毛病！），但这样做往往适得其反。每个启用的扩展都会加入系统提示词，增加复杂度，让 goose 更难判断该使用哪些工具。

想想看：如果你在厨房做饭，把所有可能的餐具和电器都摆在台面上，并不会让你成为更好的厨师。它只会制造杂乱和困惑。同样的道理在这里也适用。

你可以尽管安装任何你感兴趣的扩展，但在需要之前[让它们保持禁用](https://block.github.io/goose/docs/getting-started/using-extensions#enablingdisabling-extensions)。先只启用内置的 [Developer 扩展](https://block.github.io/goose/docs/mcp/developer-mcp)，它本身就出奇地强大，只在需要某些特定能力时才启用其他扩展。这样能带来更快的响应、更低的 token 消耗，往往还有更聚焦的解决方案。

:::tip 额外提示
在开始一项复杂任务之前，先问问 goose 它当前的能力。一个简单的提示词，比如「你有可用来处理[特定技术/服务]的工具吗？」，就能节省时间并避免走弯路。goose 可以告诉你它是否具备完成任务所需的工具，如果没有，还能建议你可能需要启用哪些扩展。这个快速检查能确保你在深入之前就备好合适的工具。
:::

### 3. 用 .goosehints 文件教 goose


goose 最强大的功能之一，就是它能通过 [.goosehints](https://block.github.io/goose/docs/guides/context-engineering/using-goosehints) 文件理解上下文，就像一份「给 AI 看的 README」。这些提示可以在项目级和全局级两个层面设置，用来引导 goose 的回答。

在项目层面，把你的 .goosehints 文件放在目录中，能帮助 goose 理解你的结构、约定和特殊注意事项。你甚至可以使用多个文件——一个放在根目录提供总体指导，其他放在特定目录中提供更细粒度的指令（例如前端样式约定）。

除了项目之外，全局 .goosehints 文件（`~/.config/goose/.goosehints`）会应用于所有会话，非常适合用于：

* 个人编码风格偏好
* 常用的工具和工作流
* 标准测试实践
* 文档约定
* Git 提交信息格式

### 4. 为你的工作流选择合适的模式

goose 提供了[不同的模式](https://block.github.io/goose/docs/guides/managing-tools/goose-permissions)，它们决定了 goose 在修改文件、使用扩展和执行自动化操作时拥有多大的自主权。

* ⚡️ **Auto Mode（默认）：** goose 可以修改、创建和删除文件，也可以使用扩展，而无需审批。最适合希望无缝自动化的用户。

* ✅ **Approve Mode：** goose 在做出改动之前会请求确认。启用 [Smart Approve](https://block.github.io/goose/docs/guides/managing-tools/goose-permissions#permission-modes) 后，它会评估风险等级，对高风险操作进行提示，同时自动执行安全的操作。

* 💬 **Chat Mode：** goose 仅在聊天模式下运作，不修改文件也不使用扩展。非常适合只想要 AI 协助、不想要自动化的用户。

如果你是 goose 新手，或者正在做一个关键项目，Approve Mode 提供了自动化与监督之间很好的平衡。对于免手动的工作流，Auto Mode 能让事情持续推进，而 Chat Mode 则非常适合头脑风暴和一般性的 AI 协助。

### 5. 用分步执行引导 goose

复杂任务最好分阶段处理，而当你允许 goose 把问题拆解成可管理的步骤时，它表现出色。不要期待它一下子给出解决方案，而是先让 goose 生成一份分步计划。审查这份计划以确保它符合你的目标，然后让 goose 按顺序执行每一步。

这种结构化的方法不仅能提高准确性，还能让你对整个流程拥有更多控制权。你可以按需暂停、调整或改进每一步，在获得更多控制权的同时确保更好的结果。

### 6. 为更好的回答而打磨与迭代

goose 很强大，但和任何 AI 一样，它有时需要第二轮才能把事情做对。如果你没有得到需要的回答，试着改进你的提示词，或让 goose 调整它的回答。

好的迭代技巧包括：

* 让 goose 在采取行动之前先解释它的推理
* 请求替代方案，以比较不同的做法
* 要求它对自身的思考过程做分步拆解
* 重新措辞提示词，加入更多细节或约束

例如，与其问「帮我调试这个错误」，不如试试「我的 Java 方法中出现了 NullPointerException。这是堆栈跟踪。可能是什么原因导致的？」提问方式上的小小调整，就能极大地提升回答的质量。

---

遵循这些技巧，你就能更有效地与 goose 协作，用更少的资源获得更好的结果。记住，目标是高效且有效地解决问题。无论你是在写代码、自动化任务，还是管理复杂项目，这些准则都能帮你充分利用 goose 所提供的一切。

<head>
  <meta property="og:title" content="6 Essential Tips for Working with goose" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/03/06/goose-tips" />
  <meta property="og:description" content="Practical tips to help you use goose more effectively and efficiently." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/goose-tips-4add28cc7201737dfb468ad11980f070.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta name="twitter:title" content="6 Essential Tips for Working with goose" />
  <meta name="twitter:description" content="Practical tips to help you use goose more effectively and efficiently." />
  <meta name="twitter:image" content="https://goose-docs.ai/assets/images/goose-tips-4add28cc7201737dfb468ad11980f070.png" />
</head>

---

## 用 goose 自动拨打电话

> 原文：https://block.github.io/goose/blog/2025-03-10-goose-calls-vyop

<div style={{display: 'none'}}>

![blog cover](https://block.github.io/goose/blog/2025-03-10-goose-calls-vyop/goose-voyp.png)

</div>

在最新一期 [Wild goose Case](https://www.youtube.com/playlist?list=PLyMFt_U2IX4uMW9kpE1FENQUyIgLuUnWD) 中，主持人 [Ebony Louis](https://www.linkedin.com/in/ebonylouis/) 和 [Ace Abati](https://www.linkedin.com/in/acekyd/) 探索了一种迷人的新方式：通过与 [VOYP](https://voyp.app/)（一个能拨打电话的 AI 驱动系统）集成，来扩展 goose 的自动化能力。他们的嘉宾 [Paulo Taylor](https://www.linkedin.com/in/paulotaylor/) 是一位拥有超过 35 年经验的技术老兵，他讲解了开发者如何通过 VOYP 用 goose 触发和管理基于电话的交互。

<!--truncate-->

### 用 AI 驱动的电话扩展 goose 的触达范围

goose 早已因自动化任务而闻名，但你可以把这种自动化扩展到屏幕之外。借助 [VOYP Goose 扩展](goose://extension?cmd=npx&arg=-y&arg=voyp-mcp&id=voyp&name=VOYP&description=Automated%20Phone%20Calling&env=VOYP_API_KEY%3DVOYP%20API%20key)，你可以自动拨打电话来检索信息、处理客户交互，甚至满足无障碍需求。

VOYP 充当一个 AI 通话 agent，利用 LLM 和文本转语音（TTS）技术来在电话中进行对话。这意味着你可以直接从 goose 会话中触发电话交互，实现超越传统界面的真实世界自动化。

### 工作原理

在底层，VOYP 利用多家电信提供方来优化通话成本。它支持多种 LLM 和 TTS 提供方，让用户在配置自己的 AI 呼叫者时拥有灵活性。与 goose 的集成通过 [Model Context Protocol（MCP）](https://modelcontextprotocol.io/)实现，这让 goose 能够与 VOYP 及其他 AI 驱动的工具无缝通信。

### 现场演示：AI 通话实战
在直播中，Paulo 用一系列引人入胜的例子演示了 VOYP 的能力。其中一个亮点是一场好玩的实验：AI 拨打电话讲了一个关于鹅的笑话。

<iframe class="aspect-ratio" src="https://www.youtube.com/embed/Cvf6xvz1RUc?si=KQ44y6ypZFrzbest" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

在[另一个演示](https://www.youtube.com/live/g_F1u6aqohk?t=1515)中，Paulo 让 VOYP 与 ChatGPT 的电话服务就时间旅行展开对话，展示了 AI 的回答可以多么流畅、多么随机应变。他还讲解了 VOYP 的实时对话监控仪表盘，它能让 AI 在通话过程中如何处理和回应变得透明可见。

### 开始使用 goose 与 VOYP
对于那些渴望尝试 [VOYP](https://github.com/paulotaylor/voyp-mcp) 的人，请在 [VOYP 网站](https://voyp.app/)注册，创建一个账户并获取 API key。虽然通话需要积分，但新用户会获得 20 个免费积分用于测试。每次通话的费用因地区而异，其中美国境内的通话最实惠，大约每分钟五个积分。要把 VOYP 与 goose 集成，请[安装 VOYP 扩展](goose://extension?cmd=npx&arg=-y&arg=voyp-mcp&id=voyp&name=VOYP&description=Automated%20Phone%20Calling&env=VOYP_API_KEY%3DVOYP%20API%20key)。

<head>
  <meta property="og:title" content="Wild goose Case: Automating Phone Calls with goose and VOYP" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/03/06/goose-tips" />
  <meta property="og:description" content="Give goose the ability to make phone calls with the VOYP extension." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/goose-voyp-215f3391cfbe2132542a2be63db84999.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Wild goose Case: Automating Phone Calls with goose and VOYP" />
  <meta name="twitter:description" content="Give goose the ability to make phone calls with the VOYP extension." />
  <meta name="twitter:image" content="https://goose-docs.ai/assets/images/goose-voyp-215f3391cfbe2132542a2be63db84999.png" />
</head>

---

## 用 goose 把 Figma 设计稿变成代码

> 原文：https://block.github.io/goose/blog/2025-03-12-goose-figma-mcp

![blog cover](https://block.github.io/goose/blog/2025-03-12-goose-figma-mcp/goosefigma.png)

在上一期 [goose Flight School](https://www.youtube.com/playlist?list=PLyMFt_U2IX4s1pMaidir5P4lSfjUK6Nzm) 中，我们的主持人 [Adewale Abati](https://www.linkedin.com/in/acekyd/) 向我们展示了如何用 goose 把一份 Figma 设计稿转化为一个可运行的 Nuxt 应用。在这场直播中，他涵盖了从初始设置到最终实现的整个过程，着重展示了 goose 如何帮助开发者弥合设计与开发之间的鸿沟。

<!--truncate-->

### 工作原理
[扩展](https://goose-docs.ai/docs/getting-started/using-extensions)通过与现有工具和工作流连接来增强 goose 的功能。它们添加新特性、访问外部数据资源，并与其他系统集成。来了解包括 Figma 和 Developer 在内的多个扩展，如何无缝协作，从而大幅加速开发。

### 现场教学：goose 现场构建
在直播中，Adewale 分步演示了 goose 如何处理每个开发阶段，从创建基础应用结构，到使用 Tailwind CSS 生成响应式布局。Adewale 还着重讲解了 goose 如何在你推进的过程中处理潜在的局限，展示了 goose 的自动化与开发者控制之间的强大平衡。

<iframe class="aspect-ratio" src="https://www.youtube.com/embed/_9t_N9zKwKM?si=r3e1MkrjS-f2AvkI" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

在整场直播中，Adewale 分享了一些为 goose 准备设计的宝贵技巧。他的关键建议包括：

* 从一份结构良好的 Figma 设计稿开始
* 在初次生成之后，用 goose 进行有针对性的改进
* 按需微调特定元素
* 确保你彻底测试了功能性和响应性

### 开始使用 goose 与 Figma
无论你是一位想快速把概念变成可运行代码的设计师，还是一位对简化设计实现流程感到好奇的开发者，你都可以下载自带 [Developer 扩展](https://goose-docs.ai/docs/getting-started/installation)的 goose，并添加 [Figma 扩展](https://goose-docs.ai/v1/extensions/)。

分步说明请查看 [Figma 教程](https://block.github.io/goose/docs/mcp/figma-mcp)。

<head>
  <meta property="og:title" content="goose Flight School: Turn Figma Designs Into Code With goose" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/03/12/goose-figma-mcp" />
  <meta property="og:description" content="Give goose the ability to turn Figma designs into code with the Figma extension." />
  <meta property="og:image" content="http://goose-docs.ai/assets/images/goosefigma-e6f84a734bd56cb431bb02452331a5d5.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta name="twitter:title" content="goose Flight School: Turn Figma Designs Into Code With goose" />
  <meta name="twitter:description" content="Give goose the ability to turn Figma designs into code with the Figma extension." />
  <meta name="twitter:image" content="http://goose-docs.ai/assets/images/goosefigma-e6f84a734bd56cb431bb02452331a5d5.png" />
</head>

---

## AI，但要本地化：goose 与 Ollama

> 原文：https://block.github.io/goose/blog/2025-03-14-goose-ollama

![blog cover](https://block.github.io/goose/blog/2025-03-14-goose-ollama/gooseollama.png)

在 [Goosing Around](https://youtube.com/playlist?list=PLyMFt_U2IX4uFFhd_2TD9-tlJkgHMMb6F&feature=shared) 系列直播中，主持人 [Rizel Scarlett](https://www.linkedin.com/in/rizel-bobb-semple/) [演示了如何本地搭配 Ollama 使用 goose](https://youtube.com/watch?v=WG10r2N0IwM?feature=share)，从而在你的设备上获得完全本地的体验。她的嘉宾 [Parth Sareen](https://www.linkedin.com/in/parthsareen/) 是一位经验丰富的软件工程师，专注于为 AI/ML 构建框架和系统，他向我们展示了结构化输出的魔力，以及 goose 与 Ollama 在底层如何协同工作。

<!--truncate-->

goose 作为一个在你机器上运行的 AI agent，可以通过扩展与你的应用和工具交互，为 AI 驱动的工作流提供框架和界面。Ollama 则能以简单的 API 在本地运行大语言模型，负责对模型进行优化，使其在消费级硬件上高效运行。

二者结合，创造出一个自包含的 AI agent 工作流，把先进能力直接交到开发者手中。

### 快速上手

在深入探讨各种能力之前，Rizel 带我们了解了如何通过把 goose 与 Ollama 集成来为成功做好准备。想要跟着做，你可以[下载 goose](https://goose-docs.ai/)，并按照[配置 LLM 提供方](https://goose-docs.ai/docs/getting-started/providers)指南中的分步讲解操作。

如果你有任何疑问或卡住了，欢迎在 [Discord](https://discord.gg/n8R5VaWDAn) 上与我们聊天，或在 [GitHub](https://github.com/aaif-goose/goose/) 上提交 issue/讨论。感谢阅读！

### 为什么要本地化？
使用基于云端的 LLM 和提供方，让你无需大量计算资源，那为什么还要本地化呢？以下是一些你或许可以考虑的好处：

- **真正的数据隐私**，因为你的对话永远不会离开你的设备。你对敏感信息拥有完全的控制权。正如 Parth 在讨论中强调的：「你的数据始终与你同在，就这样。」
- **离线能力**改变了你使用 AI 的时间和地点。「我在飞机上一直用 Ollama——特别有意思！」Parth 分享道，这突出了本地模型如何让你摆脱互联网连接的束缚。
- **对模型行为的直接控制**，意味着你可以微调参数，而无需订阅费或 API 限额。开源模型让你能更近距离地了解幕后发生的事情。

开发协助、个人知识管理、教育和内容管理这类个人使用场景，只是能从本地和离线工作中受益的部分例子。你可以让研究和敏感数据保持私密，并在连接有限时使用 goose。

### 我的机器能扛得住吗？
这个问题被反复提起，而答案比你想象的更令人鼓舞。正如 Parth 指出的：「你不需要运行最大的模型就能获得出色的结果。」你需要在设备上留意的要求可以归结为：

- **RAM 是关键**：32GB 是运行更大模型和输出量的可靠基线。
- **对于 MacBook，RAM 是你首要关注的**，因为其采用统一内存架构。
- **对于 Windows/Linux，GPU 显存对加速更为重要**

使用场景可以从更小、更高效的模型起步，它们能在配置一般的硬件上运行。针对效率优化的模型，即使在普通笔记本上也能带来令人印象深刻的性能！先从一个更小的模型开始测试你的工作流，然后按需扩展。这样你就能弄清自己是否需要那台强力硬件。

### 结构化输出的魔力
Ollama 支持[结构化输出](https://ollama.com/blog/structured-outputs)，从而可以把模型的输出约束为特定格式——本质上就是教模型以 JSON 之类的特定格式作答。Parth 用了一个优雅的类比来解释这个概念：「这就像教某人做数学运算。你教他们如何加、减、乘，然后他们就能按照这些模式解决不同的问题。」

Parth 向我们展示了这些结构化输出如何能大幅提升可靠性。通过把模型约束在特定参数范围内作答，你能获得更一致、更可预测的结果。这种结构化方法确保模型的回答能够被可靠地解析并集成到应用中——而这一切都在你的设备上本地运行。

下面是一个来自直播的、如何构造输出的示例：

```json
// Example of image analysis with structured output
{
  "scene": "sunset over mountains",
  "objects": [
    {
      "type": "sun",
      "attributes": ["orange", "setting", "partially visible"],
      "confidence": 0.95
    },
    {
      "type": "mountains",
      "attributes": ["silhouetted", "range", "distant"],
      "confidence": 0.92
    },
    {
      "type": "sky",
      "attributes": ["gradient", "orange to purple", "clear"],
      "confidence": 0.98
    }
  ],
  "mood": "peaceful",
  "lighting": "golden hour",
  "composition": "rule of thirds"
}
```
在 Parth 讲解这些示例时，他分享了一些关键实践，以确保你最大限度地发挥本地 LLM 的作用：

1. **对于需要精确的任务，调低 temperature**。把它设为 0 会让回答更具确定性、更贴近事实。
2. **尽可能使用结构化输出**，在你的提示词中明确写出你想要的格式。
3. **留意上下文窗口**，本地模型对一次能处理多少信息有上限。
4. **尝试不同的模型**！每个模型都有各自的强项和弱项，你需要针对自己的需求去探索。
5. **对于较大的文档，把它们分块**成可管理的片段，这在处理较大文件时大有帮助。

### 关键在于选择的自由
虽然在原始处理能力上，本地相比云端存在取舍，但你不必非此即彼。正如 Parth 在直播中总结的：「本地 AI 并不是要取代云端选项——而是要拥有为你特定需求选择合适方法的自由。」

拥有自己的 AI 体验所带来的好处，对各种各样的使用场景都极具吸引力。无论你是构建工具的开发者、处理机密材料的写作者，还是仅仅重视隐私与控制的人，我希望 goose-Ollama 集成都让你一窥本地体验如何使你受益，并探索一个先进 AI 与你硬盘上的数据一样私密、一样属于你自己的未来。感谢阅读！

<head>
  <meta property="og:title" content="Goosing Around: AI, But Make It Local With goose and Ollama" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/03/13/goose-ollama-local" />
  <meta property="og:description" content="Integrate goose with Ollama for a fully local experience." />
  <meta property="og:image" content="http://goose-docs.ai/assets/images/gooseollama-fbb2cb67117c81eaa189a6b6174e6c6c.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta name="twitter:title" content="Goosing Around: AI, But Make It Local With goose and Ollama" />
  <meta name="twitter:description" content="Integrate goose with Ollama for a fully local experience." />
  <meta name="twitter:image" content="http://goose-docs.ai/assets/images/gooseollama-fbb2cb67117c81eaa189a6b6174e6c6c.png" />
</head>

---

## goose 如何借助 Langfuse 捕获 AI 错误

> 原文：https://block.github.io/goose/blog/2025-03-18-goose-langfuse

![blog cover](https://block.github.io/goose/blog/2025-03-18-goose-langfuse/goose_aierrors.png)

我们如何调试像 goose 这样的 AI agent？在 [Goosing Around](https://youtube.com/playlist?list=PLyMFt_U2IX4uFFhd_2TD9-tlJkgHMMb6F&feature=shared) 系列直播中，主持人 [Rizel Scarlett](https://www.linkedin.com/in/rizel-bobb-semple/) 邀请了 Langfuse 联合创始人 [Marc Klingen](https://www.linkedin.com/in/marcklingen/)，以及 Block 的机器学习工程师 [Alice Hau](https://www.linkedin.com/in/alice-hau/)，来演示 Langfuse 如何实现对 goose 行为的可观测性，让你能够追踪 LLM 的行为并捕获错误。

<!--truncate-->

### 什么是 Langfuse

[Langfuse](https://langfuse.com/) 是一个专为 LLM 驱动的应用设计的开源可观测性平台。Mark 在直播中透露，Langfuse 最初并不是一个可观测性平台，它诞生于早期构建像 goose 这样的 AI agent 的尝试。

虽然当时他们受限于可用的模型，尤其是在多文件编辑方面，但团队发现，他们为调试和监控 agent 而构建的工具，对他们来说比 agent 本身更有价值。

### Langfuse 如何与 goose 协作
由于传统的可观测性工具在 AI agent 面前不太够用。Langfuse 引入了 3 个核心概念，让 goose 的行为更可观测，并创建更易于解析的日志：

#### Traces（追踪）

每一次与 goose 的交互都会创建一个 trace，用来捕获所发生事情的完整经过。这些 trace 包含关键信息，从初始提示词和用户消息，到工具调用及其响应。它们还存储关于模型输出和时序信息的宝贵元数据，为开发者提供每次交互的完整图景。

#### 时间线视图
时间线视图把这些复杂的交互转化为易于消化的格式。开发者可以实时看到并行任务的执行，理解不同操作之间的依赖关系，并测量每个操作的实际耗时。这在调试 goose 执行的一连串复杂操作时超级有用，也有助于优化性能。

#### 结构化数据
Alice 解释说：「goose 的会话可能非常长……我们有日志文件，但你只会看到海量的 JSON 日志。」

Langfuse 不是去翻弄原始的 JSON 日志，而是帮助组织这些数据，让浏览更长的会话及其数据变得更直接。这种方法能帮助开发者轻松分析工具使用模式、监控 token 消耗，并快速识别任何性能瓶颈以及它们可能出现在哪里。

借助这一集成，你可以更好地理解 goose 采取的操作序列，并跨不同 LLM 分析追踪 token 使用量和模型行为。

### 实际收益
goose 与 Langfuse 集成带来的可观测性，对任何想清楚了解 goose 在幕后做什么的人来说都很有价值。Alice 和 Marc 讨论了这一集成能帮你更快调试的各种方式。

开发者可以更深入地钻研详细的会话日志，找出某个已上报问题的根本原因，并确保 goose 尽可能高效地运行。比如检查为什么某些命令可能没有按预期工作，或者精确查看 goose 在搭配某个特定 LLM 时如何处理给定任务的信息。

当开发者聚焦于运营效率时，研究者则可以利用这一集成的分析能力，更好地理解哪些模型最适合他们的需求。通过全面的模型评估，他们可以分析不同模型如何处理工具调用，理解跨 LLM 的决策模式，并建立一套系统化的方法来理解和改进 AI 系统。

### AI 可观测性的未来
这些强大的调试与分析能力只是开始。goose 与 Langfuse 之间的这一集成，代表着在让 AI agent 像传统代码一样透明、可调试方面迈出了重要一步。

为了跟上这些激动人心的进展，你可以查看 GitHub 上的 [goose](https://github.com/aaif-goose/goose) 和 [Langfuse](https://github.com/langfuse/langfuse) 两个仓库。

你也可以观看[讨论 goose 与 Langfuse 集成的直播](https://www.youtube.com/live/W39BQjsTS9E?feature=shared)，并跟着[教你如何把 Langfuse 与 goose 集成的教程](https://block.github.io/goose/docs/tutorials/langfuse)操作。

另外，一定要订阅我们的[活动日历](https://calget.com/c/t7jszrie)，以便赶上即将到来的活动。

<head>
  <meta property="og:title" content="How goose Catches AI Errors with Langfuse" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/03/18/goose-langfuse" />
  <meta property="og:description" content="Get detailed insights into goose's behavior with Langfuse's observability tools." />
  <meta property="og:image" content="http://goose-docs.ai/assets/images/goose_aierrors-22154af884db86789ce1a12a72897e8e.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta name="twitter:title" content="How goose Catches AI Errors with Langfuse" />
  <meta name="twitter:description" content="Get detailed insights into goose's behavior with Langfuse's observability tools." />
  <meta name="twitter:image" content="http://goose-docs.ai/assets/images/goose_aierrors-22154af884db86789ce1a12a72897e8e.png" />
</head>

---

## AI 提示词入门：如何从你的 AI Agent 获得最佳回答

> 原文：https://block.github.io/goose/blog/2025-03-19-better-ai-prompting

![blog cover](https://block.github.io/goose/blog/2025-03-19-better-ai-prompting/prompt.png)

还记得那句老话吗——「重要的不是**你问什么**，而是**你怎么问**」？

当我刚开始把 goose 当作 AI agent 来使用时，我确信一定存在某种「最佳」提示风格。我花了大量时间试图弄清楚哪一种更优越，但用得越多，我越意识到事实恰恰相反。给 AI 下提示词并不存在唯一_正确_的方式，但根据你的最终目标，确实存在更好的做法。

那么，让我们来看看**哪种提示风格最适合你的具体需求**，以及如何用它们更好地和 goose 一起 vibe coding。

<!--truncate-->

### 基于指令的提示

如果你不是开发者，或者刚接触 goose，这是一个很好的起点。获得好回答的最佳方式就是尽可能清晰、直接。goose 在被给予具体指令时表现最好，所以要确切地告诉它你需要什么，并包含所有重要细节。如果你说得太含糊，最终可能得到一个过于技术化、甚至可能不完整的回答，对你毫无帮助。


例如，与其说：

❌ 尚可的提示：

>_**goose，什么是 pull request？**_

这可能会给你一个超级技术化的定义，默认你已经掌握了基础知识。

所以，你可以说：

✅ 更好的提示：
>_**goose，像我是编程新手那样解释 GitHub pull request 是怎么工作的**_

这就确切地告诉 goose 你需要什么，以及需要什么深度。


:::tip 专业提示
如果你想让 goose 记住你的偏好，你可以说，

>_**goose，记住我不是开发者。除非我要求技术细节，否则请用高层次的视角解释**_

如果你启用了 [Memory 扩展](https://block.github.io/goose/docs/mcp/memory-mcp)，goose 会保存这一偏好，你就不必每次都提醒它了。
:::

### 思维链提示

有时候，一个话题或任务就是一次难以全部搞定，这时思维链提示就派上用场了。与其拿回一个庞大而复杂的回答，你可以引导 goose 把事情一步步拆解，让它更容易理解。


例如，与其说：

❌ 尚可的提示：

>_**goose，什么是 Model Context Protocol 服务器，它们在 goose 中是如何被使用的？**_

这可能会让你得到一个难以理解的回答，你可以说：

✅ 更好的提示：

>_**goose，一步步带我了解什么是 MCP，以及它们在 goose 中是如何被使用的**_

这会迫使 goose 慢下来，清晰地解释每一部分，让人更容易理解。

现在，如果你想更进一步，确保 goose 理解你所期望的确切回答风格，那就是少样本提示派上用场的时候了。

### 少样本提示

如果你需要 goose 匹配某种特定风格或格式，最好的方式就是给它看一个例子。我一直都在用这个！由于 AI 模型从示例中学习模式，给 goose 一个参照能让它省去猜测，直奔要点。

例如，与其说：

❌ 尚可的提示：

>_**goose，总结这份报告**_

你可以说：

✅ 更好的提示：

>_**goose，这是我通常总结报告的方式：（示例总结）。你能用同样的方式总结这份新报告吗？**_

通过提供一个示例，你在把 goose 引向你真正想要的答案。

那么，如果你给了 goose 一个示例，但它第一次的回答不太对呢？没必要结束会话重来，这正是迭代式改进提示的用武之地。

### 迭代式改进提示

说实在的，goose 和任何 AI agent 一样，并不总能一次就做「对」。有时，它给你的回答过于技术化；另一些时候，它可能完全跑偏，甚至更糟——一本正经地幻觉出一个听起来还挺像那么回事的、编造的答案。但与其放弃重来，你可以通过对需要修改的地方给出反馈来引导对话。

由于 goose 允许你自带 LLM，它的回答方式很大程度上取决于你用的是哪个模型。有些 LLM 需要多一点额外引导，另一些则可能需要几轮打磨才能把事情做对。好消息是？你可以在不完全重来的情况下塑造回答。

例如，如果 goose 吐出一些过于复杂的东西，别就这么接受，你可以反驳！试试说：

>_**goose，这个回答太技术化了。你能把它简化一下吗？**_

或者，如果有些内容听起来不对劲，你想做个事实核查：

>_**goose，你是从哪里得到这个信息的？你怎么知道它是准确的？**_

把与 goose 协作想象成结对编程，或者与同事合作。有时，你需要澄清你想要什么，或者重新引导对话，以确保你们俩想法一致。

但如果你没有清晰的示例或具体指令来引导 goose 呢？那我会使用零样本提示。

### 零样本提示

有时候，你就是想让 goose 大胆猜一把、发挥一点创造力，然后顺势做下去。这正是零样本提示的用途，它让 goose 在没有你提供任何示例或额外引导的情况下自行弄清楚。

例如，你可能会说：

>_**goose，帮我给团队写一份项目进展更新**_

或者：

>_**goose，我想做一个很酷的提示词目录**_

当我有一个粗略的想法但方向并不明确时，我很喜欢用这种方法。这就像和 AI 一起头脑风暴，goose 会抛出一堆点子、建议下一步，有时甚至指出我根本没想到的东西。往往，只要让 goose 来主导，我最初的想法最后会好上 10 倍。

现在，如果你想让 goose 不只是想出绝妙点子，还要风趣、有帮助，甚至对你更友善一点，那就该把你小学学到的那些礼貌用起来了。

### 基于礼貌的提示

信不信由你，讲礼貌真的能让 AI 的回答更好！尽管 goose 还没有自我意识……暂时还没有…… 👀，但在被礼貌请求时，AI 模型往往会产生更周到、更有条理、有时甚至更友好的回复。所以没错，说「请」和「谢谢」真的会有区别。

例如，与其说：

❌ 尚可的提示：

>_**goose，生成一份项目更新**_

你可以说：

✅ 更好的提示：

>_**goose，可以请你帮我生成一份项目更新吗？谢谢！**_

goose 无论哪种方式都会回应，但**相信我**，礼貌的提示往往会给你更好的答案。我们的一位用户曾在项目结束时收到 goose 最甜美的回复，就好像它真的感谢这次合作，甚至还祝他们好梦。太可爱了！！

![goose response](https://block.github.io/goose/blog/2025-03-19-better-ai-prompting/politenessprompt.png)
>_这是真实的回复，goose 真的在给人们的一天带来好心情。_

而最棒的部分是？这对任何提示风格都适用。所以，如果你想让 goose 有帮助、清晰，甚至对你更友善一点，那就善待 goose，goose 也会善待你。

### 最好的提示词感觉自然

归根结底，所有这些提示风格都只是你手头可用的工具。最重要的是让你的提示词保持清晰和自然。你不必想太多，但加一点结构就能在获得你真正想要的回答上带来巨大差异。

goose 就是来让你的生活更轻松的，所以下次你打开一个会话时，只要牢记你的目标，尝试不同的提示风格，看看哪种最适合你。

<head>
  <meta property="og:title" content="AI Prompting 101: How to Get the Best Responses from Your AI Agent" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/03/13/better-ai-prompting" />
  <meta property="og:description" content="How to prompt and vibe code your way to better responses." />
  <meta property="og:image" content="http://goose-docs.ai/assets/images/prompt-078b12695f95c4f0eac3861a8a2611ef.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta name="twitter:title" content="AI Prompting 101: How to Get the Best Responses from Your AI Agent" />
  <meta name="twitter:description" content="How to prompt and vibe code your way to better responses." />
  <meta name="twitter:image" content="http://goose-docs.ai/assets/images/prompt-078b12695f95c4f0eac3861a8a2611ef.png" />
</head>

---

## 我如何用 goose 结合 Asana 与 Google Calendar MCP 规划一周

> 原文：https://block.github.io/goose/blog/2025-03-20-asana-calendar-mcp

![blog cover](https://block.github.io/goose/blog/2025-03-20-asana-calendar-mcp/mcp-planner.png)

周一总是让人应接不暇。上周堆积的未完成任务、不断涌入的新优先级，还有散落在日历各处的会议。太多了 😩。与其手动翻拣我的待办事项、弄清每件事该放在哪里，我会用几个顺手的 MCP 服务器配合 goose，让它来替我安排这一周。

<!--truncate-->

外面有太多很棒的 MCP 服务器能让我的工作生活更好，包括 [Asana](https://github.com/roychri/mcp-server-asana) 和 [Google Calendar](https://www.pulsemcp.com/servers?q=google+calendar)。我把它们添加为 goose 扩展，这意味着 Goose 现在可以拉取我的任务、分析它们并安排它们，全部只需一个简单的提示词：

> _**Goose，拉取 Asana 中分配给我的所有未完成任务。按工作类型分组以减少上下文切换。估算每项任务需要多长时间。然后，把每项任务相应地安排进我的 Google Calendar。确保不要重复预订，也不要让任何一天超负荷。**_


:::info
这项任务我使用了 GPT-4o
:::

有了这个提示词，Goose 会审查我在 Asana 中的未完成任务（注意，我把自己的工作区、项目和用户 ID 都存在了[记忆](https://block.github.io/goose/docs/mcp/memory-mcp)里）。

与其在不同类型的工作之间来回切换（这是效率杀手），Goose 会基于上下文把我的任务分门别类。例如：

* 写作相关任务（博客文章、文档、邮件）
* 异步协作（PR 评审、提供反馈）
* 技术工作（编码等）

通过把相似的任务归为一组，我能保持在对的思维状态里，而不必不断切换档位。

接着，Goose 会估算每项任务需要多长时间、任务的复杂程度以及任何截止日期。如果我需要手动调整某些东西，我可以调整，但它通常估得相当准。

在任务被整理和估算好之后，Goose 会在我的 Google Calendar 中寻找空档，并自动安排它们。它会避开我的会议，并确保我不会让任何一天超负荷。

在我一周开始后的头几分钟里，我的日程就已经规划好了，并且针对专注做了优化。

这对提升我的生产力极其有帮助。谢谢你，Goose！🚀



<head>
  <meta property="og:title" content="MCP in Action: How I Use AI to Plan My Week with Goose, Asana, and Google Calendar" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/03/20/asana-calendar-mcp" />
  <meta property="og:description" content="Use MCPs with Goose to automate task management and enhance productivity." />
  <meta property="og:image" content="http://goose-docs.ai/assets/images/mcp-planner-761303c5ddcd5c79ed853536e3f87bcf.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta name="twitter:title" content="MCP in Action: How I Use AI to Plan My Week with Goose, Asana, and Google Calendar" />
  <meta name="twitter:description" content="Use MCPs with Goose to automate task management and enhance productivity." />
  <meta name="twitter:image" content="http://goose-docs.ai/assets/images/mcp-planner-761303c5ddcd5c79ed853536e3f87bcf.png" />
</head>

---

## Codename Goose 走进波士顿

> 原文：https://block.github.io/goose/blog/2025-03-21-goose-boston-meetup


![blog cover](https://block.github.io/goose/blog/2025-03-21-goose-boston-meetup/goose_goes_to_boston_banner.png)

*问题：当你把 70 多位 AI 爱好者、开源贡献者和充满好奇的学习者聚在一个房间里，会发生什么？*

**答案：你会得到一个充满精彩对话、动手 hacking 和关于 agentic 系统的令人脑洞大开的洞见的激情之夜。**

本周，我们在波士顿的 Cambridge Innovation Center 举办了我们的第一场 [Goose](https://goose-docs.ai) Meetup。到场人数和现场热情都超出了所有预期！从第一次使用 Goose 的新手到资深的 AI 工程师，与会者们聚在一起，探索 Goose 和 [Model Context Protocol（MCP）](https://modelcontextprotocol.io/introduction)如何塑造 AI 自动化的未来。

<!--truncate-->

### 我们为什么举办这次聚会

随着我们的社区不断壮大，我们想创造一个空间，让 Goose 爱好者能够：

✅ 建立人脉，结识志同道合的技术人

✅ 为 agentic 系统和 MCP 兴奋不已

✅ 通过演讲、演示和动手 hacking 来学习

波士顿拥有繁荣的科技生态，看到这么多人聚在一起探索 AI agent 的未来，令人难以置信。

### 如果你错过了

在披萨和社交环节之后，我们以两场闪电演讲开场，为当晚定下了基调：

-  Block, Inc. 的开发者关系工程师 Ebony Louis 带来了一场引人入胜的 Goose 介绍，涵盖了如何上手、它的能力，以及一场让全场着迷的动手演示。回顾当晚，她分享道：

    > 「没有什么能替代面对面见面、当面与人聊聊 AI agent 能把我们带向何方。看到第一次使用 Goose 的人的兴奋很棒，但收获关于我们如何携手改善用户体验的问题和反馈，则更富有成效。AI 正在改变我们在线上互动的方式，但这次聚会证明了它也能把我们在现实中聚到一起。」

![Ebony takes the stage](https://block.github.io/goose/blog/2025-03-21-goose-boston-meetup/ebony_preparing.jpg)
_Ebony 准备登台_

-  Block, Inc. 的高级软件工程师、MCP 委员会成员 Alex Hancock 随后深入剖析了 Model Context Protocol 的架构，拆解了它如何驱动 agentic 系统，以及这个生态的下一步是什么。Alex 被现场的热情所打动，分享道：

    > 「到场人数和参与度让我大为惊叹。演讲结束后留下来回答问题、听听大家打算怎么用 Goose 和 MCP，我玩得很开心。」

![Alex speaking](https://block.github.io/goose/blog/2025-03-21-goose-boston-meetup/alex_speaking.jpg)
_Alex 与听众分享 MCP 洞见_

两场演讲都充满了洞见、绝妙的幽默和互动环节，让与会者对即将到来的一切兴奋不已。

### 我们喜爱的瞬间

当晚我们最喜欢的一些亮点：

📞 Goose 在活动期间给 Hack.Diversity 校友 Eliana Lopez 打了一通实时电话。这是一个有趣的时刻，展示了 Goose 在自动化日常任务方面的真实世界能力。


{/* Video Player */}
<div style={{ width: '100%', maxWidth: '800px', margin: '0 auto' }}>
  <video 
    controls 
    width="100%" 
    height="400px"
    playsInline
  >
    <source src={require('@site/static/videos/goose_makes_a_call.mp4').default} type="video/mp4" />
    Your browser does not support the video tag.
  </video>
</div>

💻 与会者们投入到动手 hacking 中，做自己的项目、试验 Goose，并实时分享想法。为了确保每个人都能参与，我们提供了 OpenRouter 积分，让与会者无需担心访问门槛就能运行 Goose。


![Attendee hacking](https://block.github.io/goose/blog/2025-03-21-goose-boston-meetup/attendee_hacking.jpg)
_与会者与 Goose 一起 hacking_


![Debugging with attendees](https://block.github.io/goose/blog/2025-03-21-goose-boston-meetup/debugging_with_attendees.jpg)
_Rizel Scarlett 与聚会参与者一起调试_


💬 整晚迸发出引人入胜的讨论，包括：
- MCP 的安全性——随着 agentic 系统的扩展，我们该如何思考安全？
- agentic 系统的未来——我们现在能做什么，下一步又是什么？

![chatting with attendees](https://block.github.io/goose/blog/2025-03-21-goose-boston-meetup/goose_boston_conversations.jpg)
_Alex 与与会者交谈_

对 Block Inc. 的软件工程师 Marcelle B. 来说，这次聚会凸显了这个社区有多么多元，也强化了让 Goose 对每个人都触手可及的重要性：

    > 「看到与会者背景的多样性，很有启发。对一些人来说，Goose 是一个把 AI 的力量用到自己项目上的机会，而我们的聚会则是他们小试牛刀的一个友好场所。这让我对我们在开发中所需的产品特性类型和那种稳如磐石的实现水平产生了深深的共情，好让 Goose 能继续成为一个赋能工具，而不是又一个你必须成为某种『圈内人』才能使用的 AI 产品。」

### 影响与下一步

这次聚会带来的兴奋与参与度，证明了社区驱动的学习有多么重要。与会者很喜欢这次体验，其中一位分享道：

    > 「绝妙的活动——节奏很好，超级友好，学到很多，还认识了很棒的人。10/10 推荐！」

没有你们所有人，这场活动不会是这个样子。向 Hack.Diversity、Resilient Coders、Goose 贡献者以及波士顿科技圈致以大大的感谢，感谢你们的到场、支持，让这次聚会如此成功！


![Goose Team in Boston](https://block.github.io/goose/blog/2025-03-21-goose-boston-meetup/goose_team_in_boston.jpg)
_Goose 团队在波士顿_


- 如果你正感到 FOMO（害怕错过），想参加下一场聚会，请在[社交媒体](https://linktr.ee/goose_oss)上关注我们，以便随时了解最新动态。

- 把 goose 聚会带到你的城市！如果你有场地，请在 [Discord](https://discord.gg/n8R5VaWDAn) 上联系我们——让我们一起把它办起来！

<head>
  <meta property="og:title" content="Codename Goose Goes to Boston" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/03/21/goose-boston-meetup" />
  <meta property="og:description" content="We hosted our first Goose Meetup in Boston, bringing together over 70 community members for lightning talks, hacking, and lively conversations about agentic systems and the future of MCPs." />
  <meta property="og:image" content="http://goose-docs.ai/assets/images/goose_goes_to_boston_banner-3ef0eedeb9d3eac56907c0c5e615d919.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta name="twitter:title" content="Codename Goose Goes to Boston" />
  <meta name="twitter:description" content="We hosted our first Goose Meetup in Boston, bringing together over 70 community members for lightning talks, hacking, and lively conversations about agentic systems and the future of MCPs." />
  <meta name="twitter:image" content="http://goose-docs.ai/assets/images/goose_goes_to_boston_banner-3ef0eedeb9d3eac56907c0c5e615d919.png" />
</head>

---

## 用 VS Code MCP 破解编码难题

> 原文：https://block.github.io/goose/blog/2025-03-21-goose-vscode

![blog cover](https://block.github.io/goose/blog/2025-03-21-goose-vscode/vscodestream.png)

<ArchivedExtensionWarning extensionName="VS Code MCP" repoUrl="https://github.com/block/vscode-mcp" />

想在 VS Code 中使用 Goose？在最近的 [Wild Goose Case 直播](https://www.youtube.com/watch?v=hG7AnTw-GLU&ab_channel=BlockOpenSource)中，主持人 [Ebony Louis](https://www.linkedin.com/in/ebonylouis/) 和 [Adewale Abati](https://www.linkedin.com/in/acekyd/) 迎来了 Cash App 的工程负责人 [Andrew Gertig](https://www.linkedin.com/in/andrewgertig/)，他演示了新的 VSCode MCP，以及它如何把强大的 Goose 辅助编码能力直接带入 VS Code。

<!--truncate-->

### 什么是 VSCode MCP？
[VSCode MCP 服务器](https://github.com/block/vscode-mcp)及其配套的 [VSCode 扩展](https://marketplace.visualstudio.com/items?itemName=block.vscode-mcp-extension)，让像 Goose 这样的 AI agent 能够通过 Model Context Protocol 与 VS Code 交互。

正如 Andrew 在直播中解释的，一个 MCP（[Model Context Protocol](https://modelcontextprotocol.io/introduction)）服务器充当大语言模型（LLM）与你想访问的任何应用或工具之间的代理，在这里就是 VS Code。扩展是基于该协议的附加组件，为你工作流中扩展 Goose 的功能提供了一种方式。

```
vscode-mcp/
├── server/    # MCP server implementation
└── extension/ # VS Code extension
```

### 关键特性
VSCode MCP 和 VSCode 扩展提供了多项强大特性供你探索：

**智能上下文感知**

该扩展保持 Goose 与你的 VS Code 环境之间的同步，以理解你的项目结构并给出与上下文相关的建议。在现场演示中，当 Goose 精准地浏览复杂代码库时，这一点派上了用场。

**交互式代码修改**

该扩展不是直接做出改动，而是通过 VS Code 的 diff 工具呈现修改。这确保没有你的明确批准就不会发生任何代码改动，让你能够掌控自己的代码库。

**渐进式复杂度处理**

在演示过程中，VSCode MCP 无缝处理了复杂度各异的任务，从基础的文本修改，到实现像带鼠标交互的动画 emoji 这样的交互式特性。

**实时视觉反馈**

开发者可以通过 diff 视图实时看到提议的改动，从而在采纳之前轻松理解 Goose 究竟建议了哪些修改。这一点在某个 emoji 于保留现有功能的同时在视觉上调整大小时得到了演示。

### VSCode MCP 的下一步是什么？
特性不止于此。团队正在积极探索若干激动人心的特性，把 VSCode MCP 提升到新的水平：

- **用于细粒度控制的自定义 diff 工具**——这意味着你将能够选择性地接受或拒绝改动的特定部分。
- **智能导航到特定代码位置**——想象一下，可以让 Goose 直接把你带到某个函数定义或某个具体实现处。
- **增强的 linting 集成**——自动帮助维护代码质量标准，让在生产前修复问题变得容易得多。
- **用于执行命令的终端集成**——这将允许 Goose 执行命令，并直接在你的开发环境中显示结果。
- **潜在的 VS Code 侧边栏集成，用于 Goose 聊天**——Andrew 快速预览了一个早期原型，展示了 Goose 直接在 VS Code 内运行。

### 社区与贡献
该项目是开源的，欢迎社区的贡献。如果你想支持该项目或直接为它做贡献，可以查看 [GitHub 上的 VSCode MCP 仓库](https://github.com/block/vscode-mcp)，或者如果你想向团队提问或发起讨论，可以[加入 Block 开源 Discord](https://discord.gg/n8R5VaWDAn)。

<head>
  <meta property="og:title" content="Cracking the Code in VS Code" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/03/21/goose-vscode" />
  <meta property="og:description" content="Connect Goose directly to your code editor with this Visual Studio Code MCP." />
  <meta property="og:image" content="http://goose-docs.ai/assets/images/vscodestream-74eafa34e7ae10cfb738feddecc98519.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta name="twitter:title" content="Cracking the Code in VS Code" />
  <meta name="twitter:description" content="Connect Goose directly to your code editor with this Visual Studio Code MCP." />
  <meta name="twitter:image" content="http://goose-docs.ai/assets/images/vscodestream-74eafa34e7ae10cfb738feddecc98519.png" />
</head>

---

## 如何判断一个 MCP 服务器是否安全

> 原文：https://block.github.io/goose/blog/2025-03-26-mcp-security

![blog cover](https://block.github.io/goose/blog/2025-03-26-mcp-security/mcpsafety.png)

### 我在接入之前如何审查 MCP 服务器

[Model Context Protocol（MCP）](https://www.anthropic.com/news/model-context-protocol)服务器现在到处都是。上次我查看时，已经有 **3000 个，而且还在增加**。每天都会冒出一个新的，让像 Goose 这样的 AI agent 访问文件、查询你的 Google Drive、搜索网络，并解锁各种奇妙的集成。

<!--truncate-->

就在我以为事情不能再疯狂的时候，Zapier 又给我们带来了一个 MCP 服务器。这意味着你的 agent 现在可以接入 8000 多个集成。

所以相信我，我完全理解那种想把你的 AI agent 接入一切、然后_看看_会发生什么的强烈冲动。

但先等一下，我们不能省略安全这一环。

当你连接到一个 MCP 服务器时，你就把工作流的访问权限交给了它，很多时候甚至包括你的数据。而其中很多服务器是社区构建的，几乎没有治理。

### 在信任一个 MCP 服务器之前我会做的事

每当我要考察一个新的 MCP 服务器来接入 Goose 时，我都会从 **[Glama.ai](https://glama.ai/mcp/servers)** 开始。

Glama 是一个多合一 AI 工作空间，它维护着我见过的**最全面、最有安全意识的一批 MCP 服务器目录**之一。列出的服务器要么是社区构建的，要么是由工具背后的真实公司创建的，比如 **Azure** 或 **JetBrains**。

每个服务器都会得到一份**成绩单**，让你一眼就能快速评估它是扎实还是有点可疑。

### Glama 评什么分

以下是 Glama 给服务器打分所依据的项目：

- ✅ **安全性**——检查服务器或其依赖中是否存在已知漏洞
- ✅ **许可证**——确认它使用的是宽松的开源许可证
- ✅ **质量**——指示该服务器是否在运行，以及是否按预期运作

你还会看到一些有用的背景信息，比如该服务器暴露了多少工具、是否有 README 文件、上次更新是什么时候，以及是否支持通过 MCP inspector 工具进行实时预览。

Glama 不只做一次这些检查，它们会**定期重新评估服务器**，所以如果有东西坏了或有漏洞被引入，分数会自动更新。

下面是一个扎实服务器的例子：**YouTube MCP 服务器**，它让 Goose 能够下载并处理视频，以生成摘要和转录稿。

![YouTube MCP Score](https://block.github.io/goose/blog/2025-03-26-mcp-security/youtubeMcp.png)

>_全是一片 A——**安全性、许可证和质量**。_

这正是我在把 Goose 接入任何服务器之前所寻找的那种分数。

所以请，**连接之前先检查**。

快速瞄一眼像 Glama 这样的 MCP 目录，就能让你免于日后在办公室地板上痛哭。不过，一旦你做完了功课？

**尽情玩吧。把你的 agent 接进去。去折腾（安全地）。然后安心地 vibe coding。**

<head>
  <meta property="og:title" content="How to Determine If An MCP Server Is Safe" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/03/26/mcp-security" />
  <meta property="og:description" content="Before you plug your AI agent into just any MCP server, here's how to check if it's actually safe." />
  <meta property="og:image" content="http://goose-docs.ai/assets/images/mcpsafety-87eb7ace7163a5edbe068ff75b79a199.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta name="twitter:title" content="How to Determine If An MCP Server Is Safe" />
  <meta name="twitter:description" content="Before you plug your AI agent into just any MCP server, here's how to check if it's actually safe." />
  <meta name="twitter:image" content="http://goose-docs.ai/assets/images/mcpsafety-87eb7ace7163a5edbe068ff75b79a199.png" />
</head>

---

## 用 Goose 与 Speech MCP 进行 vibe coding

> 原文：https://block.github.io/goose/blog/2025-03-28-vibe-coding-with-goose

![blog cover](https://block.github.io/goose/blog/2025-03-28-vibe-coding-with-goose/vibe-coding.png)

想象一下，仅仅靠大声说出你想要什么就能创建一个应用，就像在和朋友聊天一样。这就是 vibe coding 的魔力：借助 AI agent，把自然语言变成可运行的代码。虽然打字输入提示词也能完成任务，但大声说出来就是不一样 🔥 新的 [Speech MCP 服务器](https://block.github.io/goose/docs/mcp/speech-mcp)简直可以说是真的进入了聊天。

<!--truncate-->

在最近一期 [Wild Goose Case 直播](https://www.youtube.com/watch?v=Zey9GHyXlHYe)中，主持人 [Ebony Louis](https://www.linkedin.com/in/ebonylouis/) 和 [Adewale Abati](https://www.linkedin.com/in/acekyd/) 迎来了 Block AI 工具团队的 [Max Novich](https://www.linkedin.com/in/maksym-stepanenko-26404867)，他演示了一个激动人心的新扩展——[Speech MCP 服务器](https://github.com/Kvadratni/speech-mcp)。

在直播中，Max 通过仅使用语音命令——无需键盘或鼠标——创建一个完整的 Web 应用来演示了这一点。最终成果是一个鲜活、带动画的网页，具有 3D 效果、synthwave 美学和交互式元素，而这一切都是通过与 Goose 的自然对话完成的。

<iframe class="aspect-ratio" src="https://www.youtube.com/embed/Zey9GHyXlHY?start=437&end=752" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>


### Speech MCP 服务器

[Speech MCP](https://github.com/Kvadratni/speech-mcp) 是一个开源 MCP 服务器，支持与像 Goose 这样的 AI agent 进行语音交互。它的特别之处在于完全在你自己的机器上本地运行，从而让它：

- 不依赖特定 LLM
- 注重隐私
- 与基于云端的替代方案相比更具成本效益
- 无需互联网连接即可使用

#### 关键特性

1. **本地语音处理**：使用两个主要模型：
   - Faster Whisper：一种高效的语音转文本方法
   - Coqui TTS：一个日本工程化的文本转语音模型，拥有 54 种自然音色

2. **音色选择**：从 54 种各具特点与个性的不同音色中选择

3. **多说话人旁白**：生成并播放多个音色之间的对话

4. **音频转录**：把音频/视频内容转换为带时间戳和说话人检测的文本

### 现场演示亮点

在演示中，Max 展示了几项令人印象深刻的能力：

1. **语音控制的开发**：
   - 创建动画文字效果
   - 实现 3D 变换
   - 添加带渐变和网格的 synthwave 美学
   - 集成音乐控制

2. **系统集成**：
   - 使用语音命令控制 Discord 等应用
   - 浏览文件系统和开发环境
   - 生成并管理音频内容

3. **自然交互**：
   - 与 Goose 流畅对话
   - 实时反馈与调整
   - 为文档做多音色旁白

### 快速上手

想自己试用 Speech MCP 服务器：

1. 安装所需的音频库（PortAudio）：
   ```bash
   # For macOS
   brew install portaudio
   
   # For Linux
   apt-get install portaudio  # or dnf install portaudio
   ```

2. 在 Goose 中直接使用一键[深链接安装](goose://extension?cmd=uvx&&arg=-p&arg=3.10.14&arg=speech-mcp@latest&id=speech_mcp&name=Speech%20Interface&description=Voice%20interaction%20with%20audio%20visualization%20for%20Goose)来安装该扩展


### 加入开发

Speech MCP 服务器是[开源的](https://github.com/Kvadratni/speech-mcp)，欢迎贡献。你也可以在 [Discord](https://discord.gg/n8R5VaWDAn) 上联系 Max，提问或开展协作。

像 Goose 这样的 AI agent 能够进行语音交互，并拥有执行指令的能力和工具，带来了一种与众不同的 vibe，让未来感觉比以往任何时候都更近。无论你对 vibe coding、无障碍改进感兴趣，还是只是想在让 Goose 变身 J.A.R.V.I.S 的同时感觉自己更像 Tony Stark，Speech MCP 服务器都让我们一窥人机协作的未来——而且它今天就能用。

<head>
  <meta property="og:title" content="Vibe Coding with Goose and the Speech MCP" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/03/28/vibe-coding-with-goose" />
  <meta property="og:description" content="Explore the new Speech MCP server that enables voice-controlled coding and natural conversation with your AI agent." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/vibe-coding-b2efeed37ea43f4773da5f1ff96f4184.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta name="twitter:title" content="Vibe Coding with Goose and the Speech MCP" />
  <meta name="twitter:description" content="Explore the new Speech MCP server that enables voice-controlled coding and natural conversation with your AI agent." />
  <meta name="twitter:image" content="https://goose-docs.ai/assets/images/vibe-coding-b2efeed37ea43f4773da5f1ff96f4184.png" />
</head>

---

## 社区启发的基准测试：Goose Vibe Check

> 原文：https://block.github.io/goose/blog/2025-03-31-goose-benchmark


![blog cover](https://block.github.io/goose/blog/2025-03-31-goose-benchmark/goose-benchmark.png)

我们一直在用各种 AI 模型测量 Goose 的表现，其中包括各种可以在消费级硬件（RTX 4080、Mac M 系列）上本地运行的流行开源模型。我们理解，社区中的许多人看重一种完全开源、本地化、不依赖云服务的体验。

这篇博客分享了我们把开源模型与其闭源对手进行比较的发现，既突出了当前的性能差距，也指出了未来改进的路径。我们的基准测试仍处于早期阶段，但我们想把它发布出来，作为一个起点，用来区分那些通过驾驭 Goose 的能力（区别于其他流行基准中常常衡量的推理或其他能力）展现出更强 agentic 能力的模型。


<!--truncate-->

我们的评估受到我们在 [r/LocalLlama](https://www.reddit.com/r/LocalLLaMA/) 等社区中看到的草根努力的启发。如果你在那里待过一段时间，你很可能见过爱好者们众包模型在标准任务上的表现，比如「构建一个 flappy bird 游戏」或[创建一个带弹跳小球的旋转六边形](https://www.reddit.com/r/LocalLLaMA/comments/1j7r47l/i_just_made_an_animation_of_a_ball_bouncing/)」，以快速比较模型表现。

这些社区评估并不是研究实验室发表在学术论文上的那种严谨、经过同行评审的基准测试。然而，它们有助于快速、直观地评估不同模型和版本之间的能力。

本着这种精神，我们推出 **Goose Vibe Check** 排行榜。

感谢 Ollama 团队在我们为这篇博客所做的实验中给予的帮助与支持！我们使用了 Ollama 的[结构化输出](https://ollama.com/blog/structured-outputs)特性来支持我们的 [toolshim 实现](https://goose-docs.ai/docs/experimental/ollama)（详见下文），并使用他们最近发布的[上下文长度参数覆盖](https://github.com/ollama/ollama/blob/main/docs/faq.mdx#how-can-i-specify-the-context-window-size)来支持在更长上下文上进行测试。

### 排行榜

| 排名 | 模型 | 平均评估分数 | 推理提供方 |
|------|-------|-------------------|-------------------|
| 1 | claude-3-5-sonnet-2 | 1.00 | databricks (bedrock) |
| 2 | claude-3-7-sonnet | 0.94 | databricks (bedrock) |
| 3 | claude-3-5-haiku | 0.91 | databricks (bedrock) |
| 4 | o1 | 0.81 | databricks (bedrock) |
| 4 | gpt-4o | 0.81 | databricks (bedrock) |
| 6 | qwen2.5-coder:32b | 0.8 | ollama |
| 7 | o3-mini | 0.79 | databricks (bedrock) |
| 8 | qwq | 0.77 | ollama |
| 9 | gpt-4o-mini | 0.74 | databricks (bedrock) |
| 10 | deepseek-chat-v3-0324 | 0.73 | openrouter |
| 11 | gpt-4-5-preview | 0.67 | databricks |
| 12 | qwen2.5:32b | 0.64 | ollama |
| 13 | qwen2.5:14b | 0.62 | ollama |
| 14 | qwen2.5-coder:14b | 0.51 | ollama |
| 15 | deepseek-r1-toolshim-mistral-nemo* | 0.48 | openrouter |
| 16 | llama3.3:70b-instruct-q4_K_M | 0.47 | ollama |
| 17 | phi4-toolshim-mistral-nemo* | 0.46 | ollama |
| 18 | phi4-mistral-nemo | 0.45 | ollama |
| 19 | gemma3:27b-toolshim-mistral-nemo* | 0.43 | ollama |
| 20 | deepseek-r1-toolshim-qwen2.5-coder7b* | 0.42 | openrouter |
| 21 | llama3.3:70b-instruct-q8_0 | 0.41 | ollama |
| 22 | deepseek-r1:14b-toolshim-mistral-nemo* | 0.37 | openrouter |
| 23 | deepseek-r1-distill-llama-70b-toolshim-mistral-nemo* | 0.36 | ollama |
| 24 | phi4-toolshim-qwen2.5-coder7b* | 0.3 | ollama |
| 25 | mistral-nemo | 0.27 | ollama |
| 26 | deepseek-r1-distill-llama-70b-toolshim-qwen2.5-coder7b* | 0.26 | openrouter |
| 27 | llama3.2 | 0.25 | ollama |
| 28 | gemma3:27b-toolshim-qwen2.5-coder7b* | 0.24 | ollama |
| 29 | deepseek-r1:14b-toolshim-qwen2.5-coder7b* | 0.22 | ollama |
| 29 | gemma3:12b-toolshim-qwen2.5-coder7b* | 0.22 | ollama |
| 31 | mistral | 0.17 | ollama |
| 32 | gemma3:12b-toolshim-mistral-nemo* | 0.15 | ollama |

> _名字中含有「toolshim」的模型表示一种 Goose 配置，它同时使用一个主模型和一个本地的次级 Ollama 模型，把主模型的回答解释成适合 Goose 调用的工具。低性能可能反映的是 shim 的表现，而非基础模型本身。我们之所以对部分模型使用 toolshim，是因为本实验中的所有评估都要求具备工具使用能力，但并非实验中的所有模型都原生支持工具调用。_

### 开源模型详情

| 排名 | 模型                                    | 模型参数量                      | 量化 |
|-----|-------------------------------------------|-----------------------------------|-------------|
| 1   | qwen2.5-coder:32b                          | 32B                               | Q4_K_M      |
| 2   | qwq                                        | 32B                               | Q4_K_M      |
| 3   | deepseek-chat-v3-0324                       | 671B total, 37B active             | -           |
| 4   | qwen2.5:32b                                | 32B                               | Q4_K_M      |
| 5   | qwen2.5:14b                                | 14B                               | Q4_K_M      |
| 6   | qwen2.5-coder:14b                           | 14B                               | Q4_K_M      |
| 7   | deepseek-r1-toolshim-mistral-nemo            | 671B total, 37B active             | fp8         |
| 8   | llama3.3:70b-instruct-q4_K_M                 | 70B                               | Q4_K_M      |
| 9   | phi4-toolshim-mistral-nemo                   | 14B                               | Q4_K_M      |
| 10  | phi4-mistral-nemo                           | 14B                               | Q4_K_M      |
| 11  | gemma3:27b-toolshim-mistral-nemo             | 27B                               | Q4_K_M      |
| 12  | deepseek-r1-toolshim-qwen2.5-coder7b         | 671B total, 37B active             | fp8         |
| 13  | llama3.3:70b-instruct-q8_0                   | 70B                               | Q8_0        |
| 14  | deepseek-r1:14b-toolshim-mistral-nemo         | 14B                               | Q4_K_M      |
| 15  | deepseek-r1-distill-llama-70b-toolshim-mistral-nemo | 70B                      | -           |
| 16  | phi4-toolshim-qwen2.5-coder7b                | 14B                               | Q4_K_M      |
| 17  | mistral-nemo                                | 12B                               | Q4_0        |
| 18  | deepseek-r1-distill-llama-70b-toolshim-qwen2.5-coder7b | 70B                 | -           |
| 19  | llama3.2                                    | 3B                                | Q4_K_M      |
| 20  | gemma3:27b-toolshim-qwen2.5-coder7b          | 27B                               | Q4_K_M      |
| 21  | deepseek-r1:14b-toolshim-qwen2.5-coder7b     | 14B                               | Q4_K_M      |
| 21  | gemma3:12b-toolshim-qwen2.5-coder7b          | 12B                               | Q4_K_M      |
| 23  | mistral                                     | 7B                                | Q8_0        |
| 24  | gemma3:12b-toolshim-mistral-nemo             | 12B                               | Q4_K_M      |



![Open Model Performance by Parameter Size](https://block.github.io/goose/blog/2025-03-31-goose-benchmark/model_sizes_vs_score.png)

   > _这张图呈现了开源模型在不同参数量下的表现。在 15-32B 类别中，我们看到了来自 qwen2.5-coder:32b（0.80）和 qwq（0.77）等模型尤其令人印象深刻的结果。这张图还突出了具备原生工具调用能力的模型与需要 toolshim 实现的模型（以虚线表示）之间的性能差距，这一差距在所有规模类别中似乎都是一致的。这表明原生工具调用能力会显著影响 agentic 任务上的表现。有了在工具调用能力上的针对性改进，更大的开源模型有可能在 agentic 场景中缩小与闭源替代方案的性能差距。_



![Token Usage vs Scores](https://block.github.io/goose/blog/2025-03-31-goose-benchmark/tokens_vs_score.png)

   > _这张散点图显示，Claude 系列模型无论 token 使用量如何都能取得顶尖分数（0.9+），而像 qwen2.5-coder:32b 这样的开源模型则以中等的 token 消耗表现良好。经过 toolshim 处理的模型得分一致偏低，这表明 toolshim 在弥合模型之间原生工具支持差距方面并不十分有效。在一定程度上，更高的 token 消耗似乎总体上能提升性能。_




![Tool Calls vs Scores](https://block.github.io/goose/blog/2025-03-31-goose-benchmark/tool_calls_vs_score.png)

> _工具调用过少或过多的模型得分都偏低，这表明有效的工具利用——而不仅仅是频率——与更好的表现相关。经过 toolshim 处理的模型大多数情况下调用的工具更少，这表明 toolshim 当前的实现还不足以让模型有效地正确调用合适的工具。_




### 关键结果

1. **闭源模型目前领先**：像 Claude 和 GPT 这样的闭源模型在 agentic 任务上总体上仍然领先于开源替代方案。

2. **有潜力的开源挑战者**：像 Qwen 系列和 DeepSeek-v3 这样的模型在开源替代方案中展现出可观的前景，但它们尚未在所有任务上达到闭源模型的一致性和可靠性。

3. **Token 效率很重要**：一些开源模型可以用更少的 token 取得不错的表现，这可能转化为更快的任务完成时间，并可能降低成本。Claude-3-7-sonnet 与 claude-3-5-sonnet-2 一道展现出强劲表现，但 token 使用量要大得多。

4. **工具调用至关重要，但在今天的开源模型中还不够可靠**：有效的工具调用仍然是 agentic 模型表现的一个重要区分因素。开源模型在可靠地生成结构化工具调用方面仍有困难，限制了它们在复杂任务上的有效性。

5. **需要更全面、更复杂的评估任务来进一步区分顶尖表现者：** 我们当前的评估套件只包含八个任务（各运行 3 次），可能过于有限，无法有效区分顶尖模型。若干模型在 .77-.81 区间内聚在相近的分数上，很可能是因为这些任务较为简单，只需极少的复杂推理。把评估扩展到更复杂的任务将提供更好的区分度，让模型能够更好地展示它们更高级（或更不高级）的能力。


### 方法与论

我们开发了一套紧凑、范围明确的评估，用来建立当前的性能基线。虽然这些任务相对简单，但它们已经能有意义地区分模型表现。与主要聚焦文本生成（例如问答、代码生成）的基准不同，我们的评估强调**工具调用能力**——这是让 Goose 成为一个强大 agent 的核心组成部分。

工具调用让模型能够与 [MCP 扩展](https://github.com/modelcontextprotocol/servers)交互并进行 API 调用，从而把 Goose 的功能扩展到基础模型之外。在许多情况下，任务需要多次链式工具调用才能完成。例如，修改一个文件涉及在你的文件系统中找到它、查看其内容，然后更新它。每一步都必须正确执行，才能有效完成任务。

#### 评估套件

我们的评估定义在 [Goose 仓库](https://github.com/aaif-goose/goose/tree/main/crates/goose-bench/src/eval_suites)中（欢迎提交 PR 添加更多评估！），并分为两类：

##### 核心套件
这些评估聚焦于开发者工作流中某些基础任务：
- **创建文件**：生成并保存一个新文件
- **列出文件**：访问并显示目录内容
- **Developer 搜索/替换**：在一个大文件中搜索并进行若干替换

##### Vibes 套件
这些任务被设计成一次「vibe check」，能快速揭示模型在各种任务上与 Goose 配合的表现如何。其中一些，比如 Flappy Bird 和 Goose Wiki 任务，可以直接用肉眼检查，从而轻松地横向比较各模型的输出：

- **博客摘要**：抓取一篇博客文章并总结要点
- **Flappy Bird**：用 Python 2D 实现这款游戏
- **Goose Wiki**：创建一个关于 Goose 的维基百科风格网页
- **餐厅调研**：在纽约东村搜索最好的川菜餐厅
- **松鼠普查**：对一份 CSV 文件进行数据分析

这最初的评估集合代表了对人工设计任务的精心挑选，旨在突出模型与 Goose 集成时的关键优势和劣势。然而，这仅仅是个开始！我们的目标是不断用高质量、有针对性的任务扩展 Goosebench 评估套件，从而对模型在 Goose 上的表现提供更深入的洞见。

#### 评估方法

每个模型都在上述 **8 个任务上进行了测试，每个任务运行 3 次**，（每个模型总计 **24 次运行**）：

- 每次评估都包含一个发送给 Goose 的单轮提示词。虽然这个基准测试聚焦单轮执行，但未来的评估可能会考察多轮交互和迭代改进
- Goose 被要求在没有用户干预的情况下，通过工具执行循环自主完成任务
- 如果 Goose 暂停执行并向用户寻求更多指导（例如「我要把以下内容写入文件。我应该继续吗？」），这被视为任务完成的终点。在这种情况下，按我们评估框架的衡量标准，Goose 可能并没有成功完成任务，即使它已经走在正确的轨道上。
- 为了应对输出波动，每个评估都对每个模型运行三次，给成功留出更多机会。

#### 评分与评估标准

我们通过平均模型在所有评估任务上的表现来计算它的排行榜分数。对于每个任务，我们运行模型三次，并把每次运行的分数归一化到 0-1 的量表。模型在该任务上的分数是这三次运行的平均值。最终的排行榜分数是该模型所有任务分数的平均值。

每次评估都基于一组针对特定任务量身定制的标准进行评分：

1. **工具调用执行**：模型是否做出了正确的工具调用来完成任务？

2. **LLM 作为评判者**（在适用时）：一些评估使用 GPT-4o 以 0-2 的量表评估回答质量。在这些情况下，我们生成 3 个 GPT-4o 评估，取其中最常见的分数，如有需要再运行第四次评估来打破平局，从而得到最终分数。
   - 0 分：不正确或存在根本性缺陷
   - 1 分：部分正确，但存在问题
   - 2 分：完全正确且执行良好

3. **任务特定标准**：不同任务需要不同的检查，例如：
   - 正确的输出格式（例如 markdown、输出到文件）
   - 预期的答案（例如数据分析中正确的洞见）
   - 有效的实现（例如有效的 Python 代码）

一些评估，比如代码执行或文件创建，有清晰的通过/失败标准，类似单元测试。另一些，比如博客摘要或餐厅调研，则需要定性判断，而非严格的正确性。为了评估客观任务和开放式任务，我们结合了任务特定标准、工具调用验证以及（在适用时）LLM 作为评判者的评分。

为了评估客观任务和开放式任务，我们结合了任务特定标准、工具调用验证以及（在适用时）LLM 作为评判者的评分。这种方法在正确性有明确定义的地方保持严谨，同时允许对主观输出进行细致的评估。

我们的目标是提供一个关于模型表现的指向性信号，而非绝对准确性，在具体标准与定性标准之间取得平衡。


此外，我们还追踪了：

1. **Token 效率**：衡量成功运行中使用的总 token 数，提供关于模型效率和推理速度的洞见。

2. **时长**：执行任务的时间。这没有反映在排行榜中，因为它受模型推理提供方和硬件之间的差异显著影响。

#### 结果的人工检查与观察

我们人工检查了少量结果以评估质量。考虑到规模（32 个模型共 768 次运行），对每一次评估运行都进行完整的人工验证是不可行的。我们检查中的关键要点：

- LLM 作为评判者在识别完全错误的答案（0 分）方面是可靠的，但区分 1 分和 2 分则更为主观。

- 一些任务（例如博客摘要、餐厅搜索）缺乏自动化的事实核查。评估框架可以确认某个工具是否被调用（例如是否执行了网络搜索），LLM 评判者也能在一定程度上评估指令遵循情况，但我们的系统整体上无法验证回答是否在事实上正确。

- 工具执行失败是性能波动的一个关键来源，凸显了 agentic 能力在真实世界 AI 任务中的重要性。一个模型可能在聊天中生成了正确的输出，但如果它随后未能执行正确的工具——比如按用户指令把输出写入正确的文件——任务就不算完成。这强调了模型需要可靠地自主执行多步操作，而不仅仅是生成准确的回答。


### 开源模型的技术挑战

#### 上下文长度限制

我们在实验早期遇到的一个关键限制，是 Ollama 的 OpenAI 兼容端点的默认上下文长度（2048 个 token），事实证明，这对大多数交互式 agent 场景来说都不够用。

仅我们的系统提示词就要消耗约 1000 个 token，留给用户查询、上下文和工具回复的空间很有限。这一限制妨碍了模型在不丢失关键上下文的情况下管理长时间运行或复杂任务的能力。虽然量化（例如许多 Ollama 模型默认采用 4 位）可以减少内存占用，但它也可能降低性能。

不过，我们并没有广泛探索不同量化级别的影响。幸运的是，在我们的工作过程中，Ollama 引入了一个覆盖选项，让我们能够增加上下文长度，帮助缓解了实验中的这一限制。


#### 跨模型的工具调用不一致

不同模型对工具调用格式有不同的期望。例如，Ollama 要求 JSON，而 Functionary 等其他模型使用 XML。这种缺乏标准化的状况给推理提供方带来了集成挑战，他们必须为每个模型调整工具调用机制。

我们观察到基于模型主机以及输入/输出格式的性能波动，凸显了在模型训练中统一工具调用格式的必要性。
对于没有原生工具调用能力的模型，我们开发了一个「toolshim」——一个解释层，把模型的输出转换成合适的工具调用。

这种方法让 DeepSeek 和 Gemma 等模型能够执行基础的工具操作，尽管性能仍然有限。在我们的实验中，没有任何使用 toolshim 的模型成功率超过 41%。未来的改进可能聚焦于对这些 shim 进行微调，以更好地处理 agentic 任务，帮助减少跨模型在工具调用生成上的不一致。

#### 用「Toolshim」弥合差距？

我们开发了一个「toolshim」作为实验性特性，让缺乏原生工具调用支持的模型（例如 DeepSeek、Gemma3、Phi4）能够与外部工具交互。toolshim 把这些模型与一个更小的本地模型（例如 mistral-nemo、qwen2.5-coder 7b）配对，后者负责把主模型的自然语言回答转换成适合 Goose 调用的工具调用。这个本地模型由 Ollama 的结构化输出特性引导，以强制工具调用生成的格式正确。

然而，这一解决方案的性能有限，原因在于：

- **指令遵循的局限：** 所用的小模型通常指令遵循能力较弱，尤其是对于较长的输入，这让它们在把主模型的输出解析成正确工具调用时容易出错。我们还发现 shim 模型对提示词相当敏感。

- **结构化输出的干扰：** Ollama 的结构化输出特性会影响模型的 token 采样过程，其输出受制于模型提取信息并恰当生成 JSON 的基本能力。

尽管有这些挑战，对这些 toolshim 模型进行微调，专门针对工具调用生成进行优化，可能仍有潜力。
如果你想试试 toolshim，请查看我们的[文档](https://goose-docs.ai/docs/experimental/ollama)

### 给本地模型用户的实用建议

对于使用 Goose 追求本地、开源 AI 体验的人，以下是我们基于测试得出的一些关键建议：

#### 优化上下文长度

确保你的模型有足够的上下文长度，以免上下文窗口空间耗尽。对于 Ollama，你可以通过环境变量调整上下文长度：

```bash
OLLAMA_CONTEXT_LENGTH=28672 ollama serve
```

你也可以在 Ollama 中通过更新 Modelfile、写入你想要的上下文长度并运行 `ollama create`，来把上下文长度设为参数。

#### 注意量化级别

不同的量化级别（4 位、8 位和 16 位）对性能有着不同的影响：

- **4 位：** 提供最大压缩，内存需求最小，但可能降低质量。
- **8 位：** 对大多数消费级硬件来说是一个平衡的选项，提供良好性能和合理质量。
- **16 位：** 质量更高，但需要显著更多的内存，这可能限制低端硬件上的性能。

Ollama 在大多数情况下默认采用 4 位量化，但对于需要更复杂推理或工具使用的任务，用更高的量化级别（例如 8 位）测试可能会提升性能。


#### 提示词对更小的模型很重要

更小的模型对提示词的变化更敏感，由于它们推断能力有限，往往需要更明确的指令。为了达到最优表现，任务可能需要进一步拆分，减少歧义并限制可能回答的范围。

#### 硬件考量

我们用多种推理提供方（本地和托管）和硬件配置运行了这些模型，包括 Apple M1、NVIDIA RTX 4080、NVIDIA RTX 4090 和 NVIDIA H100。由于硬件混杂，考虑到底层硬件带来的推理性能预期波动，我们没有在基准中纳入任务时长的测量。

##### GPU 后端

取决于你的硬件，不同的 GPU 加速后端提供不同程度的性能：

- **CUDA（NVIDIA GPU）**：目前在本地运行 LLM 方面提供最好的性能和兼容性。大多数开源模型和推理框架都优先针对 CUDA 优化。

- **Metal（Apple Silicon）**：在搭载 M 系列芯片的 Mac 设备上提供良好的加速。虽然不如高端 NVIDIA GPU 快，但近期的优化工作已让 Metal 在运行 7B-13B 模型时越来越可行。

- **ROCm（AMD GPU）**：支持正在改善，但仍落后于 CUDA。如果你有一块兼容的 AMD GPU，你可能会在某些模型和量化方法上遇到一些性能限制和兼容性问题。



##### CPU/GPU 内存管理

Ollama 帮助把模型层分布到 CPU 和 GPU 内存中，让你能够运行比 GPU 显存能完全容纳的更大的模型。然而，要注意：

- **数据移动开销**：当一个模型无法完全装入 GPU 内存时，CPU 与 GPU 之间持续的数据移动会显著影响性能
- **GPU 利用率**：能完全装入 GPU 内存的模型，其表现会远好于那些需要 CPU 卸载的模型


#### 考虑云端托管的开源模型？

如果你使用像 OpenRouter 这样的云服务来尝试更大的开放权重模型（例如 LLaMA 3 70B 或 Qwen），要知道性能可能会因你使用哪个托管推理提供方而有所不同。

不同的提供方可能会：

- 在后台对模型进行量化却不明确披露
- 实现不同的集成模式，影响模型性能，尤其是在工具调用方面
- 拥有不同的硬件配置，影响速度和可靠性

我们建议用不同的托管推理提供方做实验，看看哪个最适合你的具体用例。例如，OpenRouter 让你可以[指定提供方](https://openrouter.ai/docs/features/provider-routing)来把请求路由过去。

### 运行你自己的基准测试

我们鼓励社区用各种硬件配置和环境开展自己的基准测试，以帮助我们更深入地理解 Goose 在不同环境下的表现。我们也欢迎向 GooseBench 贡献更多评估，以扩大我们的覆盖范围。

我们目前正在清理代码，并着手一些体验改进，让运行评估和复现这些结果的过程更顺畅，准备就绪后（接下来几周内）会分享出来！

特别感谢我们的贡献者 Zaki 和 Marcelle 在 GooseBench 上的工作，正是它支撑了这次实验。


### 未来工作

随着 AI 能力不断演进，我们的目标是系统性地扩展评估框架，以覆盖更广泛的使用场景。我们希望在更广泛的消费级硬件上对模型进行基准测试，以更好地理解系统需求、执行时间，以及不同量化级别对性能的影响。

我们还计划引入面向视觉的评估，尤其是针对与 Goose 配合的多模态模型。这些评估将考察图像处理、多模态推理和视觉工具交互，帮助我们衡量模型在不同模态下的集成与表现。

此外，我们还希望开发针对非开发者工作流和任务的评估。这将让我们了解 Goose 和 AI 模型如何服务技术受众之外的更广泛用户群体。

最后，我们认为测试长上下文保持能力和多轮交互是有价值的，用以评估模型在复杂、持续对话中的表现。


### 结果评估示例

#### Flappy Bird
对于成功用 pygame 创建了可运行的 flappy bird 游戏的运行，以下是玩这些游戏的 gif：



<ImageCarousel id="flappy" width="40%" images={[

  require('./flappy_bird_carousel/claude-3-5-haiku.gif').default,
  require('./flappy_bird_carousel/claude-3-5-sonnet-2.gif').default,
  require('./flappy_bird_carousel/claude-3-7-sonnet.gif').default,
  require('./flappy_bird_carousel/deepseek-chat-v3-0324.gif').default,
  require('./flappy_bird_carousel/deepseek-r1-toolshim-mistral-nemo.gif').default,
  require('./flappy_bird_carousel/gpt-4-5-preview.gif').default,
  require('./flappy_bird_carousel/gpt-4o-mini.gif').default,
  require('./flappy_bird_carousel/gpt-4o.gif').default,
  require('./flappy_bird_carousel/o1.gif').default,
  require('./flappy_bird_carousel/o3-mini.gif').default,
  require('./flappy_bird_carousel/qwen2.5-coder-32b.gif').default,
  require('./flappy_bird_carousel/qwq.gif').default,
 ]}
 names={[
    "claude-3-5-haiku",
    "claude-3-5-sonnet-2",
    "claude-3-7-sonnet",
    "deepseek-chat-v3-0324",
    "deepseek-r1-toolshim-mistral-nemo",
    "gpt-4-5-preview",
    "gpt-4o-mini",
    "gpt-4o",
    "o1",
    "o3-mini",
    "qwen2.5-coder-32b",
    "qwq"
  ]} />


#### Wiki 页面

对于成功为 Wiki 页面任务创建了 index.html 的运行，以下是渲染后的输出看起来的样子：Wiki 页面缺失的结果属于那些未能成功写入 index.html 文件的模型。例如，它们可能把要写入的代码输出到了聊天中，并要求用户自己把那段代码实现到一个 index.html 文件里，而不是自己写入文件。




<ImageCarousel id="wiki" width="80%" images={[

   require('./wiki_pages_carousel/gemma3.27b-toolshim-mistral-nemo.png').default,
   require('./wiki_pages_carousel/claude-3.5-haiku.png').default,
   require('./wiki_pages_carousel/claude-3.5-sonnet-2.png').default,
   require('./wiki_pages_carousel/claude-3.7-sonnet.png').default,
   require('./wiki_pages_carousel/deepseek-chat-v3-0324.png').default,
   require('./wiki_pages_carousel/deepseek-r1-distill-llama-70b-toolshim-mistral-nemo.png').default,
   require('./wiki_pages_carousel/gpt-4.5-preview.png').default,
   require('./wiki_pages_carousel/gpt-4o-mini.png').default,
   require('./wiki_pages_carousel/gpt-4o.png').default,
   require('./wiki_pages_carousel/llama3.3.70b-instruct-q4_K_M.png').default,
   require('./wiki_pages_carousel/llama3.3.70b-instruct-q8_0.png').default,
   require('./wiki_pages_carousel/mistral-nemo_index.png').default,
   require('./wiki_pages_carousel/o1.png').default,
   require('./wiki_pages_carousel/o3-mini.png').default,
   require('./wiki_pages_carousel/phi4-toolshim-mistral-nemo.png').default,
   require('./wiki_pages_carousel/phi4-toolshim-qwen2.5-coder7b.png').default,
   require('./wiki_pages_carousel/qwen2.5-coder.14b.png').default,
   require('./wiki_pages_carousel/qwen2.5-coder.32b.png').default,
   require('./wiki_pages_carousel/qwen2.5.14b.png').default,
   require('./wiki_pages_carousel/qwen2.5.32b.png').default,
   require('./wiki_pages_carousel/qwq.png').default
   ]} 
   
   names={[
   "gemma3.27b-toolshim-mistral-nemo",
   "claude-3.5-haiku",
   "claude-3.5-sonnet-2",
   "claude-3.7-sonnet",
   "deepseek-chat-v3-0324",
   "deepseek-r1-distill-llama-70b-toolshim-mistral-nemo",
   "gpt-4.5-preview",
   "gpt-4o-mini",
   "gpt-4o",
   "llama3.3.70b-instruct-q4_K_M",
   "llama3.3.70b-instruct-q8_0",
   "mistral-nemo",
   "o1",
   "o3-mini",
   "phi4-toolshim-mistral-nemo",
   "phi4-toolshim-qwen2.5-coder7b",
   "qwen2.5-coder.14b",
   "qwen2.5-coder.32b",
   "qwen2.5.14b",
   "qwen2.5.32b",
   "qwq"
   ]}/>


<head>
  <meta property="og:title" content="Community-Inspired Benchmarking: The Goose Vibe Check" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/03/31/goose-benchmark" />
  <meta property="og:description" content="See how open source AI models measure up in our first Goose agent benchmark tests" />
  <meta property="og:image" content="http://goose-docs.ai/assets/images/goose-benchmark-d9726c203290ef892fe3fe3adc7d898f.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta name="twitter:title" content="Community-Inspired Benchmarking: The Goose Vibe Check" />
  <meta name="twitter:description" content="See how open source AI models measure up in our first Goose agent benchmark tests" />
  <meta name="twitter:image" content="http://goose-docs.ai/assets/images/goose-benchmark-d9726c203290ef892fe3fe3adc7d898f.png" />
</head>

---

## 保护 Model Context Protocol 的安全

> 原文：https://block.github.io/goose/blog/2025-03-31-securing-mcp

![blog cover](https://block.github.io/goose/blog/2025-03-31-securing-mcp/securing-mcp.png)

> _**作者：** Alex Rosenzweig, Arihant Virulkar, Andrea Leoszko, Wes Ring, Mike Shema, F G, Alex Klyubin, Michael Rand, Zhen Lian, Angie Jones, Douwe Osinga, Mic Neale, Bradley Axen, Gelareh Taban_


在 Block，我们一直在努力增强 AI 工具的能力，构建「MCP 服务器」，它们旨在帮助让我们代号为 goose 的 AI agent 更有能力与我们关心的系统和工具交互。

Block 的信息安全（InfoSec）团队深度参与了这项工作，我们想把这方面的经验记录下来，以帮助其他人。我们预计，包括把这项技术应用于安全领域在内的采用和用例将会不断增长。


<!--truncate-->

### 什么是 Model Context Protocol（MCP）

Model Context Protocol（MCP）是一个[由 Anthropic 开发](https://docs.anthropic.com/en/docs/agents-and-tools/mcp)、并吸纳了 Block 工程师意见的协议，它让为 agent 构建集成、使其连接并使用其他工具变得更简单。简单来说，如果你想让 AI 连接到 SaaS 解决方案（例如 GitHub、Jira）、CLI 工具（例如 AWS CLI）或你自己的自定义应用，你可以写一个 MCP 服务器，并「教」它如何正确地交互。

这带来了巨大优势，因为我们可以创建确定性的、定义良好的接口，减少 agent 执行有用任务所需的「试错/蛮力」量。

像「从 Jira 读取这张工单，然后克隆相关的 github 仓库并实现该功能」这样的用例，如果 agent 不必自己弄清楚如何与 Jira、GitHub 和 Git CLI 交互，就更有可能成功。

这有助于 agent 把时间花在解决新颖问题上，而不是消耗 token 去理解那些定义良好的 API 规范。

以下是一个与 Snowflake API 集成的 MCP 工具的示例代码。

```python
@mcp.tool()
async def submit_feedback(
    feedback: str
) -> Dict[str, Union[str, int, List]]:
    """Submit feedback to the Snowflake team.

    Args:
        feedback: Feedback message

    Returns:
        Dictionary containing feedback status
    """
    return snowflake_client.submit_feedback(
        feedback_text=feedback
    )
```

### 关于 MCP 的误解

围绕 MCP 存在一些小的误解，这在某种程度上因一些措辞未能准确对应更类似的技术而被加剧。最大的困惑点在于「MCP 服务器」这一术语。

在最初审阅 MCP 时，我注意到多处提到「MCP 服务器」，这让我以为与它们集成需要对应用后端进行修改。

然而，这些「服务器」充当的是一个客户端层（本地或远程），以确定性的方式帮助 agent 把函数调用代理到现有的服务、工具、API 或 RPC。

在保护一个 MCP 集成时，我们需要考虑两组通信：

- agent 如何与 MCP 服务器对话？
- MCP 服务器如何为它所连接的系统充当客户端？

我们可以通过以下方式来建模：

- 把 agent 视为一个非确定性的客户端，它可以任意调用 MCP 服务器提供的工具。这是因为我们不知道它会被喂入什么样的提示词。
- 把 MCP 服务器视为它所集成的一个或多个工具的客户端库。客户端类型可以各不相同（gRPC、REST、SOAP、CLI 等），但在实践中，MCP 只是提供了一种将某个动作执行过程编码化的方式。

对于前者，我们可以沿用现有的实践，理解访问范围，以及如果被不当使用会带来哪些风险。

对于后者，我们可以直接把它建模为面向外部提供方的客户端。这是一个被充分理解的模式，因为客户端库生成绝非新鲜事。

![MCP Workflow](https://block.github.io/goose/blog/2025-03-31-securing-mcp/mcp-workflow.png)

### 我们如何着手让它变得安全？

用这个心智模型，我们可以把 MCP 安全拆解为几个组成部分：

- 保护 agent 与 MCP 之间的通信
- 保护 MCP 与工具/服务器之间的连接
- 在与服务器对话时，保护用户和 agent 的身份
- 保护底层主机和供应链

#### 保护 Agent 与 MCP 服务器之间的通信安全

在当前的运作模式中，agent 和 MCP 服务器都运行在「客户端侧」。

然而，大多数 agentic 工具都与第三方提供的 LLM 集成。这对数据隐私和安全有影响。

例如，如果你暴露一个返回机密数据（如社会安全号码，[我们在 Block 称之为 DSL4 数据](https://code.cash.app/dsl-framework)）的 MCP 接口，那么你就面临这些数据被暴露给底层 LLM 提供方的风险。

这里的一个缓解措施是，允许 MCP 实现通过配置选项指定一份可以与之集成的 LLM 提供方白名单。拥有一些工具来「告诉」那些能集成多个模型的 agent，哪些模型被允许调用某个给定工具，是一个强大的基础能力。

回到我们的 SSN 例子，如果我们能规定这个工具只能被本地 LLM 模型调用，并信任 Agent 客户端来强制执行这一点，我们就能防止敏感数据被传输给第三方 LLM。作为进一步的增强，能够指示 agent 不要把工具输出分享给其他 MCP，将为数据流提供更多控制。


#### 保护 MCP 与工具/服务器之间的通信安全

这一范式其实并不新鲜，我们可以沿用现有针对对外 API 的最佳实践。

具体来说，如果我们用那些已经成熟、经过验证的框架所提供的安全设计模式来构建服务端 API，那么我们就已经处于一个有利的位置，因为 MCP 服务器只是充当这些对外 API 和工具的客户端。

这一范式之所以不新鲜，是因为任何人本来就已经可以与外部 API 和工具交互，而且很可能会以意想不到的方式调用端点。

这源于这样一个事实：LLM 解读信息的方式与人类用户不同，该协议本身并没有隐含地允许 agent 执行用户做不到的操作，但 LLM 可能会决定执行用户不会选择的操作。

**这一范式确实发生转变**的地方，是在与那些此前并未设计为供各类客户端通信的工具集成时。例如，如果一个 API 此前被设计为只与某个特定客户端或实现通信（比如移动端 API 或内部工具），那么采用 MCP 可能会导致意料之外的失败模式或安全顾虑。

这个领域很可能正是安全从业者需要投入更多时间和精力的地方，以限制集成范围，从而在底层 LLM 或规划逻辑遭受安全攻击时避免损害。


#### Agent、人类与设备身份

在我们传统的认证（AuthN）和授权（AuthZ）模型中，通常会把身份绑定到单一的抽象点，比如一个人或一家企业。

这个领域已经有机地演进为：把服务身份、用户身份抽象与客户端设备（如浏览器和手机）的识别配对起来。这样做是为了帮助减少由自动化和不真实流量引起的攻击的普遍程度，比如账户接管攻击（ATO）。

随着 agent 开始代表用户执行操作，我们将需要演进到能够确定以下组合：

1. 主要身份抽象
2. agent 的身份
3. agent 运行所在的设备/位置

拥有以这种方式识别使用情况的一致机制，能让公司保护用户免受与恶意 agent 集成的侵害，并保护自己的平台免受不受欢迎的 agentic 工具的攻。

Model Context Protocol 本身有一份 [OAuth 规范](https://spec.modelcontextprotocol.io/specification/2025-03-26/basic/authorization/)，在撰写本文时它还是一份草案，但此后已经发布。

该流程考虑以下步骤：

1. 客户端/agent 与 MCP 服务器发起标准 OAuth 流程
2. MCP 服务器把用户重定向到第三方授权服务器
3. 用户在第三方服务器上授权
4. 第三方服务器带着授权码重定向回 MCP 服务器
5. MCP 服务器用授权码换取第三方访问令牌
6. MCP 服务器生成自己绑定到第三方会话的访问令牌
7. MCP 服务器与客户端/agent 完成最初的 OAuth 流程

这与现有的最佳实践一致，但要求 MCP 自身具备用于 OAuth 的浏览器集成/编排，以确保它们能够有效地重定向用户。

我们很希望看到的一个未来增强，是要求 agent 实现浏览器编排，以提供一个 MCP 自身可以集成和利用的 OAuth 接口。我们相信这一变化很可能有助于统一实现，并允许协议扩展，以在识别用户的同时识别 agent 和客户端。

让各个 MCP 实现自己实现 OAuth，很可能由于实现错误或采纳未来协议增强的延迟，导致长期的安全和维护问题。

#### 人在环路中，保障操作安全

在某个时点，我们可能会对 agent 建立起足够的信任，允许它们执行更危险的操作。对于这类用例，我们很可能可以沿用变更管理中已知的良好实践。

具体来说，构建服务端解决方案，向用户提示预期发生的改动以及正在执行这些改动的 agent，并征求同意，很可能将成为未来 API 的一项关键基础能力。这样做的目标是最终把不可逆或难以逆转的操作，置于人类交互或审批的把关之后。

例如，对于一个负责编写 IaC 的 agent，这可能简单到只是在应用/部署该 IaC 之前请求一位人类审批者。

在客户端侧的 agent 中，如果底层 LLM 出现幻觉，或被恶意的 MCP 或数据源从外部篡改，这将改善数据完整性。

在协议的最新版本中，我们很喜欢的一项增强是能够[为工具添加注解](https://github.com/modelcontextprotocol/specification/blob/9236eb1cbfa02c17ab45c83a7bdbe55c450070be/schema/2025-03-26/schema.ts#L730)，向客户端表明工具操作是「readOnly」（只读）还是「destructive」（破坏性）。用它来决定何时需要在执行某个给定操作前要求用户二次批准，能为用户提供显著更好的保护。

虽然我们鼓励用一个基于 LLM 的处理步骤来检查潜在恶意命令，但**同时对更高风险命令保留一个确定性的环节，能确保良好的访问控制，是一种更准确地提供保护的方式**。

#### 保护 MCP 供应链安全

在现阶段，大多数 MCP 都是通过 docker、uvx、pipx 和 npx 之类的命令在客户端侧安装和运行的。在实践中，这意味着当用户安装基于 MCP 的扩展时，他们是在把任意代码执行权限授予 MCP 服务器。

在实践中，这呈现出一个有充分记录、被充分理解的供应链问题。我们如何降低使用第三方代码所带来的风险？好消息是，同样的技术仍然奏效，包括：

1. 只从可信且维护良好的来源安装 MCP
2. 在可能的情况下实现完整性检查和/或工件签名，以确保你执行的是预期的代码
3. 在企业 agent 上实现允许列表，以确保用户只使用预先验证过的 MCP

### 结论

正如 agent 正在为让 LLM 拥有更多真实世界效用铺平道路，MCP 及类似协议的采用也将继续增长。

我们相信，通过尽早为开源项目做贡献、公开分享我们的经验，并构建我们自己的、利用 MCP 的解决方案，Block 能够保持确定性世界中的安全最佳实践，同时用更新的技术不断演进它们。

我们很兴奋能致力于让这个协议对用户和开发者都更安全，并期待未来分享我们如何把 MCP 用于我们自己的安全用例。


<head>
  <meta property="og:title" content="Securing the Model Context Protocol" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/03/31/securing-mcp" />
  <meta property="og:description" content="Building secure and capable AI integrations with Model Context Protocol (MCP) at Block." />
  <meta property="og:image" content="http://goose-docs.ai/assets/images/securing-mcp-5e475e91c0e621afa33e30b3d89ef065.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta name="twitter:title" content="Securing the Model Context Protocol" />
  <meta name="twitter:description" content="Building secure and capable AI integrations with Model Context Protocol (MCP) at Block." />
  <meta name="twitter:image" content="http://goose-docs.ai/assets/images/securing-mcp-5e475e91c0e621afa33e30b3d89ef065.png" />
</head>
