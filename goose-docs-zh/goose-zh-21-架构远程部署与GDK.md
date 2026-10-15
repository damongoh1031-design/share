# goose 官方文档中文手册：第 21 章　架构、远程部署与 GDK

## goose 架构

> 原文：https://block.github.io/goose/docs/goose-architecture/goose-architecture

goose 是一个开源 AI Agent，它构建在大语言模型（LLM）的基本交互框架之上，而该框架主要充当基于文本的对话界面：它处理文本输入并生成文本输出。这种「文本进、文本出」的方式通过工具集成得到增强，使 AI Agent 能够完成任务——goose 由此诞生。

### goose 组件
goose 通过三个主要组件运作：**界面（interface）**、**代理（agent）**以及**所连接的[扩展](https://block.github.io/goose/docs/getting-started/using-extensions)**。

* **界面（Interface）**：这是你用来运行 goose 的桌面应用或 CLI。它收集你的输入并向你展示输出。

* **代理（Agent）**：代理运行 goose 的核心逻辑，管理交互循环。

* **扩展（Extensions）**：扩展是提供特定工具和能力供代理使用的组件。这些工具让 goose 能够执行诸如运行命令、管理文件等操作。

在一次典型的会话中，界面会启动一个代理实例，该实例随后同时连接到一个或多个扩展。界面还可以创建多个代理以并发处理不同任务。扩展和交互循环是 goose 功能的重要组成部分。接下来的章节将解释 goose 如何连接扩展以及如何处理用户请求。

### 与扩展的互操作性
[模型上下文协议（MCP）](https://modelcontextprotocol.io/)是一项开放标准，允许数据源与 AI Agent 之间实现互操作。goose 利用 MCP 连接到 [MCP 系统/服务器](https://github.com/modelcontextprotocol/servers?tab=readme-ov-file#model-context-protocol-servers)。在 goose 中，这些系统/服务器被称为扩展。

扩展通过工具向 goose 暴露其功能。工具是让扩展执行特定操作的函数，例如运行命令或执行文件操作。例如，Google Drive 扩展包含一个用于搜索文档的工具。正是该工具赋予了 goose 执行该操作的能力。

goose 自带一组[内置扩展](https://block.github.io/goose/docs/getting-started/using-extensions#built-in-extensions)，每一个都旨在增强你的交互体验。其中包括用于开发、网页抓取、自动化、记忆等用途的工具。goose 还支持[连接到外部扩展](https://block.github.io/goose/docs/getting-started/using-extensions#adding-extensions)或[创建自定义扩展](https://block.github.io/goose/docs/tutorials/custom-extensions)作为 MCP 服务器。

要了解更多关于扩展和工具的设计与实现，请参阅[扩展设计指南](https://block.github.io/goose/docs/goose-architecture/extensions-design#tools)。

### Agent Client Protocol (ACP)

goose 以两种方式支持 [Agent Client Protocol (ACP)](https://agentclientprotocol.com/)：

#### goose 作为 ACP 服务器

`goose acp` 以 stdio 方式将 goose 启动为 ACP 服务器，让 JetBrains 和 Zed 等编辑器能够直接连接到它。参见[在 ACP 客户端中使用 goose](https://block.github.io/goose/docs/gdk/acp)。

#### ACP Agent 作为提供方

goose 可以将任务委派给外部 ACP Agent（如 Claude Code 或 Codex）作为[提供方](https://block.github.io/goose/docs/guides/acp-providers)。ACP Agent 在内部处理工具执行。goose 将已配置的扩展作为 MCP 服务器传递过去。

### 交互循环
![交互循环](https://block.github.io/goose/assets/guides/interactive-loop.png)

让我们仔细看看上图所示的交互循环。

1. **人类请求（Human Request）**：流程始于你、也终于你。一旦你向 goose 提出请求、问题、命令或待解决的问题，流程便开始了。

2. **提供方对话（Provider Chat）**：goose 将你的请求以及一份可用工具列表发送给你所连接的 [LLM 提供方](https://block.github.io/goose/docs/getting-started/providers)。提供方处理该请求，必要时会在其响应中创建一次工具调用。

3. **模型扩展调用（Model Extension Call）**：LLM 能够创建工具调用请求，但无法执行它，这时 goose 便介入了。goose 接收以 JSON 格式化的工具调用，运行它，并收集结果。

4. **向模型返回响应（Response to Model）**：执行工具调用后，goose 将结果发送回模型。如果需要更多扩展，这些步骤将重复进行。

5. **上下文修订（Context Revision）**：goose 会移除任何陈旧或无关的信息，确保 LLM 只专注于最重要的信息。这有助于 token 管理。

6. **模型响应（Model Response）**：一旦所有工具调用完成，LLM 会向你发回最终响应，并在你回复后重新开始循环。

### goose 中的错误处理

与让错误中断流程不同，goose 会捕获并处理传统错误以及执行错误。诸如无效 JSON、缺失工具等错误会作为工具响应发送回模型，为 LLM 提供解决错误并继续所需的信息。

关于 goose 如何处理错误的更多细节，请参阅 [goose 中的错误处理](https://block.github.io/goose/docs/goose-architecture/error-handling)指南。

### 上下文修订：token 管理

虽然 goose 免费且开源，但 LLM token 的使用通常会产生成本。一切都在竞争 token 用量，包括消息、工具请求、资源、文件内容、指令等。这正是内容修订（Content Revision）发挥作用之处，帮助降低部分成本。为此采取了以下几项措施：
* goose 使用更快、更小的 LLM 进行摘要
* goose 包含全部内容，而非进行语义搜索
* goose 使用算法删除陈旧或无关的内容
* goose 会使用查找替换而非重写大文件，使用 ripgrep 跳过系统文件，并对冗长的命令输出进行摘要

---

## 扩展设计

> 原文：https://block.github.io/goose/docs/goose-architecture/extensions-design

本文档描述 goose 中[扩展框架](https://block.github.io/goose/docs/getting-started/using-extensions)的设计与实现，该框架使 AI Agent 能够通过统一的、基于工具的接口与不同的扩展进行交互。

### 核心概念

#### 扩展（Extension）
扩展代表任何可以由 AI Agent 操作（operated）的组件。扩展通过工具暴露其能力并维护自身状态。核心接口由 `Extension` trait 定义：

```rust
#[async_trait]
pub trait Extension: Send + Sync {
    fn name(&self) -> &str;
    fn description(&self) -> &str;
    fn instructions(&self) -> &str;
    fn tools(&self) -> &[Tool];
    async fn status(&self) -> AnyhowResult<HashMap<String, Value>>;
    async fn call_tool(&self, tool_name: &str, parameters: HashMap<String, Value>) -> ToolResult<Value>;
}
```

#### 工具（Tools）
工具是扩展向代理暴露功能的主要方式。每个工具都有：
- 一个名称
- 一个描述
- 一组参数
- 一个执行该工具功能的实现

工具必须接收一个 Value 并返回 `AgentResult<Value>`（它还必须是异步的）。这正是它与代理的工具调用框架兼容的原因。

```rust
async fn echo(&self, params: Value) -> AgentResult<Value>
```

### 架构

#### 组件概览

1. **扩展 Trait**：所有扩展都必须实现的核心接口
2. **错误处理**：用于工具执行的专用错误类型
3. **过程宏（Proc Macros）**：简化工具定义与注册 [*尚未实现*]

#### 错误处理

系统使用两种主要的错误类型：
- `ErrorData`：与工具执行相关的特定错误
- `anyhow::Error`：用于扩展状态及其他操作的通用错误

这种拆分使得工具执行能够获得精确的错误处理，同时为一般扩展操作保持灵活性。

### 最佳实践

#### 工具设计

1. **清晰的名称**：为工具使用清晰、面向动作的名称（例如用 "create_user" 而非 "user"）
2. **描述性的参数**：每个参数都应有清晰的描述
3. **错误处理**：尽可能返回具体的错误，这些错误会成为「提示词」
4. **状态管理**：对状态修改保持明确

#### 扩展实现

1. **状态封装**：保持扩展状态私有且受控
2. **错误传播**：在工具执行中使用 `?` 运算符配合 `ErrorData`
3. **状态清晰**：提供清晰、结构化的状态信息
4. **文档**：为所有工具及其效果编写文档

#### 示例实现

下面是一个简单扩展的完整示例：

```rust
use goose_macros::tool;

struct FileSystem {
    registry: ToolRegistry,
    root_path: PathBuf,
}

impl FileSystem {
    #[tool(
        name = "read_file",
        description = "Read contents of a file"
    )]
    async fn read_file(&self, path: String) -> ToolResult<Value> {
        let full_path = self.root_path.join(path);
        let content = tokio::fs::read_to_string(full_path)
            .await
            .map_err(|e| ErrorData {
                code: ErrorCode::INTERNAL_ERROR,
                message: Cow::from(e.to_string(),
                data: None,
            }))?;
            
        Ok(json!({ "content": content }))
    }
}

#[async_trait]
impl Extension for FileSystem {
    // ... implement trait methods ...
}
```

### 测试

扩展应在多个层面进行测试：
1. 针对单个工具的单元测试
2. 针对扩展行为的集成测试
3. 针对工具不变量的属性测试

示例测试：
```rust
#[tokio::test]
async fn test_echo_tool() {
    let extension = TestExtension::new();
    let result = extension.call_tool(
        "echo",
        hashmap!{ "message" => json!("hello") }
    ).await;
    
    assert_eq!(result.unwrap(), json!({ "response": "hello" }));
}
```

---

## 错误处理

> 原文：https://block.github.io/goose/docs/goose-architecture/error-handling

错误处理是 goose 中驱动性能的关键部分。LLM 中的非确定性可能以许多方式引入错误，而它又能从中恢复。在一次典型的 goose 会话中，出现若干代理错误是意料之中的，模型可以直接看到并纠正它们，甚至可能完全在幕后完成。

### 传统错误

当代理运行期间，网络、基础模型的可用性等可能出现间歇性问题。这些会作为错误在代理 API 中抛出给调用方，由调用方决定如何处理。我们通常用 [anyhow::Error][anyhow-error] 来处理它们。

### 代理错误

有若干类型的错误，此时一切都在正常工作，但模型自身的生成过程却以某种方式导致了错误。比如生成未知的工具名、错误的参数，或一个格式良好但导致工具自身出错的工具调用。所有这些都可以呈现给 LLM，让它尝试恢复。

错误消息在某种意义上是提示性的——它们向 LLM 提供关于如何着手恢复的指示。我们用 [thiserror::Error][this-error] 来处理它们，并精心维护一个集合。

为覆盖所有这些情况，`ToolUse` 和 `ToolResult` 通常都作为 `Result<T, AgentError>` 的一部分通过 API 传递。`ToolUse` 中的错误会立即变成 `ToolResult` 中的错误并回传给 LLM。一个有效的 `ToolUse` 仍可能最终产生一个出错的 `ToolResult`，它同样会被回传给 LLM。

随后，各提供方负责将代理错误转换为符合各种 API 规范的有效消息。

[anyhow-error]: https://docs.rs/anyhow/latest/anyhow/
[this-error]: https://docs.rs/thiserror/latest/thiserror/

---

## 运行远程 goose 服务器

> 原文：https://block.github.io/goose/docs/guides/remote-goose-server

goose Desktop 通常会在同一台机器的后台运行它自己的 `goose serve` ACP 服务器进程。你也可以单独运行 `goose serve`——例如，在远程 VM 或网络中的另一台机器上——并让 goose Desktop 指向它。

当你希望 goose 在拥有更多算力、稳定 IP 或共享访问权限的某处运行时，同时又想从本地的 Desktop UI 驱动它，这非常有用。

本指南涵盖：

1. [在远程机器上启动 `goose serve` 服务器](#1-start-the-goose-serve-server)
2. [验证它是否可达](#2-verify-the-server-is-up)
3. [定位证书指纹](#3-find-the-certificate-fingerprint)
4. [配置 goose Desktop 连接到它](#4-configure-goose-desktop)
5. [在 macOS 上将 `goose serve` 作为后台服务运行](#running-goose-serve-as-a-background-service-macos)
6. [故障排查](#troubleshooting)

:::warning 为远程服务器使用 TLS
goose Desktop 同时接受 HTTP 和 HTTPS 外部后端 URL，但在网络上连接时强烈建议使用 TLS。证书指纹固定（pinning）需要 HTTPS。
:::

### 初始设置

#### 1. 启动 `goose serve` 服务器

在远程机器上，使用主机、端口、TLS 和共享密钥启动 `goose serve`：

```bash
GOOSE_SERVER__SECRET_KEY='YOUR_SECRET' \
goose serve --platform desktop --enable-scheduler --host 0.0.0.0 --port 3000 --tls
```

如果你使用的是 macOS 应用捆绑的二进制文件，命令路径为 `/Applications/Goose.app/Contents/Resources/bin/goose`。

| 设置 | 用途 |
|---------|---------|
| `--host` | 要绑定的接口。使用 `0.0.0.0` 以接受来自其他机器的连接。绑定到 `localhost` 或 `127.0.0.1` 将只接受本地连接。 |
| `--port` | 要监听的 TCP 端口。 |
| `--tls` / `GOOSE_TLS=true` | 启用 TLS。强烈建议用于远程服务器，且证书指纹固定需要它。 |
| `GOOSE_SERVER__SECRET_KEY` | 共享密钥。客户端必须将其发送到 ACP 端点。请像对待密码一样对待它。 |

:::tip
为 `GOOSE_SERVER__SECRET_KEY` 选取一个长随机值并将其存储在密码管理器中——稍后会将同样的值填入 goose Desktop。
:::

#### 2. 验证服务器已启动

首先，确认 `goose serve` 确实在你期望的端口上监听：

```bash
lsof -nP -iTCP:3000 -sTCP:LISTEN
```

然后从服务器自身测试服务器。`-k` 标志告诉 `curl` 接受 `goose serve` 生成的自签名 TLS 证书：

```bash
# Connectivity only
curl -i https://127.0.0.1:3000/status -k

# ACP endpoint auth check. A 401 means the secret was rejected.
curl -i https://127.0.0.1:3000/acp -k \
  -H 'X-Secret-Key: YOUR_SECRET'
```

成功的 `/status` 响应确认 TLS 已启动。当密钥正确时，`/acp` 检查不应返回 `401`。

如果你打算从另一台机器访问该服务器，也请从那里使用服务器的主机名或 VPN 地址进行测试——而不是 `127.0.0.1`。

#### 3. 可选：查找证书指纹

当 `goose serve` 以 TLS 运行时，它会生成或加载一个 TLS 证书。goose Desktop 可以通过 SHA-256 指纹固定该证书。如果你将指纹字段留空，goose Desktop 会使用首次使用信任（trust-on-first-use），并固定它为此外端看到的第一个证书。

启用 TLS 时，`goose serve` 会在启动时记录指纹。它看起来像：

```text
GOOSED_CERT_FINGERPRINT=AA:BB:CC:DD:EE:FF:...
```

要捕获它，可以：

- 交互式运行 `goose serve` 并从终端输出中读取，或
- 跟踪你作为服务运行时重定向到的日志文件（参见[将 `goose serve` 作为后台服务运行](#running-goose-serve-as-a-background-service-macos)）：

```bash
grep GOOSED_CERT_FINGERPRINT ~/Library/Logs/GooseExternal/goose-serve.out.log
```

如果你想在 goose Desktop 中固定某个特定证书，请记下该指纹。

:::note
每当 `goose serve` 重新生成其证书时（例如，如果你删除了证书文件），指纹都会改变。如果 goose Desktop 在服务器重启后突然拒绝连接，请重新检查指纹。
:::

#### 4. 配置 goose Desktop

在客户端机器上，打开 goose Desktop 并导航到 **Settings → goose Server**：

| 设置 | 值 |
|---------|-------|
| **Use external server** | 已启用 |
| **URL** | `https://your-server-host:3000`（使用客户端可访问的主机名或 IP——例如 VPN/tailnet 地址） |
| **Secret Key** | 你用于 `GOOSE_SERVER__SECRET_KEY` 的同一个值 |
| **Certificate Fingerprint** | 可选。使用服务器日志中的 `GOOSED_CERT_FINGERPRINT` 值来固定特定的 TLS 证书。 |

保存后，goose Desktop 会将所有后端请求路由到远程 `goose serve` 进程。如果连接失败，参见[故障排查](#troubleshooting)。

### 将 `goose serve` 作为后台服务运行（macOS）

在终端会话中运行 `goose serve` 对于测试来说没问题，但日常使用中你很可能希望将它作为后台服务管理，以便它在登录时启动并在失败时重启。在 macOS 上，这通过 `launchd` 完成。

下面的示例使用 goose Desktop 捆绑的 CLI 二进制文件。如果你单独安装了 CLI，请将 `/Applications/Goose.app/Contents/Resources/bin/goose` 替换为 `which goose` 返回的绝对路径。

由于密钥存储在 XML 中，请使用十六进制值，例如 `openssl rand -hex 32` 的输出，或者对该值中的 XML 特殊字符进行转义。

在 `~/Library/LaunchAgents/com.goose.serve.external.plist` 创建一个 LaunchAgent plist：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.goose.serve.external</string>

    <key>ProgramArguments</key>
    <array>
      <string>/Applications/Goose.app/Contents/Resources/bin/goose</string>
      <string>serve</string>
      <string>--platform</string>
      <string>desktop</string>
      <string>--enable-scheduler</string>
      <string>--host</string>
      <string>0.0.0.0</string>
      <string>--port</string>
      <string>3000</string>
      <string>--tls</string>
    </array>

    <key>EnvironmentVariables</key>
    <dict>
      <key>GOOSE_SERVER__SECRET_KEY</key><string>YOUR_SECRET</string>
    </dict>

    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>

    <key>StandardOutPath</key>
    <string>/Users/YOUR_USERNAME/Library/Logs/GooseExternal/goose-serve.out.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/YOUR_USERNAME/Library/Logs/GooseExternal/goose-serve.err.log</string>
  </dict>
</plist>
```

将 `YOUR_SECRET` 和 `YOUR_USERNAME` 替换为适当的值。然后创建日志目录并限制对该 plist 的访问（其中包含密钥）：

```bash
mkdir -p ~/Library/Logs/GooseExternal
chmod 600 ~/Library/LaunchAgents/com.goose.serve.external.plist
```

加载并启动服务：

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.goose.serve.external.plist
```

稍后重启服务：

```bash
launchctl kickstart -k gui/$(id -u)/com.goose.serve.external
```

停止并卸载服务：

```bash
launchctl bootout gui/$(id -u)/com.goose.serve.external
```

要移除服务配置，请在卸载后删除该 plist。

### 故障排查

#### 服务器只接受本地连接

如果 `curl` 从服务器上可用，但客户端机器超时或收到「连接被拒绝」，请检查 `goose serve` 绑定到哪个接口。如果 `--host` 是 `localhost` 或 `127.0.0.1`，则只接受环回连接。

设置 `--host 0.0.0.0` 以接受所有接口上的连接，然后重启 `goose serve`。你可以用以下命令验证：

```bash
lsof -nP -iTCP:3000 -sTCP:LISTEN
```

输出应将地址显示为 `*:3000` 或特定的外部 IP，而不是 `127.0.0.1:3000`。

#### 未启用 TLS

在服务器的启动日志中：

- 如果你看到 `listening on http://...`，则 TLS **未**启用。goose Desktop 仍可通过 HTTP 连接，但不建议对远程服务器这样做。请使用 `--tls` 或 `GOOSE_TLS=true` 启动并重启 `goose serve`。
- 如果你看到 `listening on https://...`，则 TLS 已启用，一切就绪。

启动日志还包含 `GOOSED_CERT_FINGERPRINT=...` 行，你可以用它来在 goose Desktop 中进行证书固定。在服务器的 stdout（或日志文件，如果运行在 `launchd` 下）中搜索 `GOOSED_CERT_FINGERPRINT` 即可找到它。

#### 客户端无法认证（401 / Unauthorized）

来自服务器的 `401`，或 goose Desktop 指示密钥被拒绝的错误，几乎总是意味着服务器上的 `GOOSE_SERVER__SECRET_KEY` 与 goose Desktop 设置中的 **Secret Key** 不匹配。

要端到端地检查密钥而无需涉及 goose Desktop，请使用你在客户端上配置的确切值，运行[第 2 步](#2-verify-the-server-is-up)中经过认证的 `curl`。对于这个 `GET /acp` 探测，`406` 响应意味着认证通过，但请求未包含 ACP 流所需的 SSE 头。`401` 或 `403` 意味着服务器上的密钥与你发送的不同。

如果你在服务器上轮换了密钥，也必须更新 goose Desktop 设置中的密钥——它们不会自动同步。

#### 证书指纹不匹配

如果 goose Desktop 因证书或指纹错误而拒绝连接，最常见的原因有：

- 服务器重新生成了其证书（例如，删除证书文件后）。查看最新的启动日志以获取当前的 `GOOSED_CERT_FINGERPRINT`，并更新 goose Desktop。
- 你在复制指纹时带了多余空白，或粘贴了错误的值。

### 相关

- [环境变量](https://block.github.io/goose/docs/guides/environment-variables) — 所有 `GOOSE_*` 变量的完整参考
- [配置文件](https://block.github.io/goose/docs/guides/config-files) — 持久化的客户端配置

---

## VMware Tanzu Platform

> 原文：https://block.github.io/goose/docs/guides/tanzu-ai-services

[VMware Tanzu Platform](https://techdocs.broadcom.com/us/en/vmware-tanzu/platform/ai-services/10-3/ai/index.html) 通过 AI Services 提供企业托管的 LLM 访问。goose 作为兼容 OpenAI 的提供方连接到 VMware Tanzu Platform，支持**单模型**和**多模型**服务计划，默认启用流式传输。

### 前提条件

- 已安装并配置 GenAI tile 的 VMware Tanzu Platform (TAS) foundation
- 可访问某个 CF org/space，且市场（marketplace）中提供 `genai` 服务
- 已安装并认证的 CF CLI（`cf`）（`cf login`）
- goose v1.28.0 或更高版本

### 第 1 步：检查可用计划

首先，验证你的市场中提供 `genai` 服务并查看可用计划：

```sh
cf marketplace -e genai
```

你将看到类似如下的输出：

```
broker: genai-service
   plan                                description                                            free or paid
   tanzu-Qwen3-Coder-30B-A3B-vllm-v1  Access to: Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8.    free
   tanzu-gpt-oss-120b-vllm-v1          Access to: openai/gpt-oss-120b.                        free
   tanzu-all-models                    Access to: Qwen3.5-122B, Qwen3-Coder-30B, gpt-oss...   free
```

每个计划对应不同的模型或模型集合。**单模型计划**提供对一个模型的访问。**多模型计划**（例如 `tanzu-all-models`）提供对单个端点背后多个模型的访问。

### 第 2 步：创建服务实例

#### 选项 A：单模型计划

使用单模型计划创建服务实例：

```sh
cf create-service genai tanzu-Qwen3-Coder-30B-A3B-vllm-v1 my-qwen-coder --wait
```

#### 选项 B：多模型计划

使用多模型计划创建服务实例：

```sh
cf create-service genai tanzu-all-models my-all-models --wait
```

验证实例已创建：

```sh
cf services
```

### 第 3 步：创建服务密钥

创建服务密钥以生成 API 凭据：

```sh
cf create-service-key my-qwen-coder my-goose-key --wait
```

然后获取凭据：

```sh
cf service-key my-qwen-coder my-goose-key
```

#### 单模型计划输出

对于单模型计划，输出在顶层包含模型元数据：

```json
{
  "credentials": {
    "api_base": "https://genai-proxy.sys.example.com/tanzu-my-model-abc1234/openai",
    "api_key": "eyJhbGciOi...",
    "endpoint": {
      "api_base": "https://genai-proxy.sys.example.com/tanzu-my-model-abc1234",
      "api_key": "eyJhbGciOi...",
      "config_url": "https://genai-proxy.sys.example.com/tanzu-my-model-abc1234/config/v1/endpoint",
      "name": "tanzu-my-model-abc1234"
    },
    "model_capabilities": ["chat", "tools"],
    "model_name": "Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8",
    "wire_format": "openai"
  }
}
```

#### 多模型计划输出

对于多模型计划，输出只包含 endpoint 对象：

```json
{
  "credentials": {
    "endpoint": {
      "api_base": "https://genai-proxy.sys.example.com/tanzu-all-models-abc1234",
      "api_key": "eyJhbGciOi...",
      "config_url": "https://genai-proxy.sys.example.com/tanzu-all-models-abc1234/config/v1/endpoint",
      "name": "tanzu-all-models-abc1234"
    }
  }
}
```

### 第 4 步：确定你的端点和 API 密钥

从服务密钥输出中，你需要 **`credentials.endpoint`** 对象中的两个值：

| 值 | JSON 路径 | 示例 |
|-------|-----------|---------|
| **Endpoint URL** | `credentials.endpoint.api_base` | `https://genai-proxy.sys.example.com/tanzu-my-model-abc1234` |
| **API Key** | `credentials.endpoint.api_key` | `eyJhbGciOi...`（JWT token） |

:::warning 使用 `credentials.endpoint.api_base`，而不是 `credentials.api_base`
单模型计划包含一个顶层 `credentials.api_base` 字段，它带有 `/openai` 后缀。**不要使用这个值。** 始终使用 `credentials.endpoint.api_base`（不带 `/openai`），因为 goose 会自动追加正确的路径。

使用错误的值会产生像 `.../openai/openai/v1/chat/completions` 这样的双路径 URL。
:::

### 第 5 步：配置 goose

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

  1. 打开 goose Desktop
  2. 点击侧边栏按钮，然后点击 **Settings** > **Models** > **Configure providers**
  3. 在提供方列表中找到 **VMware Tanzu Platform** 并点击 **Configure**
  4. 输入你的值：
     - **TANZU_AI_ENDPOINT**：粘贴 `credentials.endpoint.api_base` URL
     - **TANZU_AI_API_KEY**：粘贴 `credentials.endpoint.api_key` JWT token
  5. 点击 **Submit**
  6. 从动态获取的列表中选择一个模型

  </TabItem>
  <TabItem value="cli" label="goose CLI">

  #### 选项 1：使用 `goose configure`

  ```sh
  goose configure
  ```

  1. 选择 **Configure Providers**
  2. 从列表中选择 **VMware Tanzu Platform**
  3. 在提示时输入你的 `TANZU_AI_ENDPOINT`
  4. 在提示时输入你的 `TANZU_AI_API_KEY`
  5. 从获取的列表中选择一个模型

  #### 选项 2：使用环境变量

  在启动 goose 之前设置以下环境变量：

  ```sh
  export TANZU_AI_ENDPOINT="https://genai-proxy.sys.example.com/tanzu-my-model-abc1234"
  export TANZU_AI_API_KEY="eyJhbGciOi..."
  ```

  然后启动 goose：

  ```sh
  goose session
  ```

  :::tip
  将这些 export 添加到你的 shell 配置文件（`~/.bashrc`、`~/.zshrc` 等）中，以便跨会话持久保留。
  :::

  </TabItem>
</Tabs>

### 第 6 步：选择模型

goose 会从你的 Tanzu 端点动态获取可用模型。配置提供方后：

- **单模型计划**：将列出唯一可用的模型（例如 `Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8`）
- **多模型计划**：将列出该计划上的所有模型，你可以在它们之间切换

要稍后更改模型，可在 Desktop 中使用 **Settings** > **Models** > **Switch models**，或在 CLI 中运行 `goose configure`。

:::note
仅用于嵌入（embedding-only）的模型（例如 `nomic-ai/nomic-embed-text-v2-moe`）会出现在模型列表中，但不能用作聊天模型。
:::

### 故障排查

#### 「Could not contact provider」/ 模型端点返回 401 Unauthorized

这意味着 API 密钥没有被正确发送。常见原因：

1. **未设置环境变量**：如果使用 goose Desktop，shell 中的环境变量可能不会被继承。请改用 Settings UI 配置提供方。
2. **`api_base` 错误**：确保你使用了 `credentials.endpoint.api_base`（不带 `/openai`），而不是 `credentials.api_base`。
3. **API 密钥过期**：Tanzu API 密钥是会过期的 JWT token。使用 `cf create-service-key` 生成新的服务密钥。

#### 手动验证你的端点

你可以用 curl 测试连通性：

```sh
# Test model discovery
curl -H "Authorization: Bearer $TANZU_AI_API_KEY" \
  "$TANZU_AI_ENDPOINT/openai/v1/models"

# Test chat completions
curl -X POST "$TANZU_AI_ENDPOINT/openai/v1/chat/completions" \
  -H "Authorization: Bearer $TANZU_AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"YOUR_MODEL_NAME","messages":[{"role":"user","content":"hello"}]}'
```

#### 流式传输

流式传输默认启用。如果你的端点不支持流式传输，你可以在提供方配置 UI 中取消勾选 **Streaming** 复选框来禁用它，或将 `TANZU_AI_STREAMING` 环境变量设置为 `false`。

#### 找不到模型

如果你选择的模型返回错误，请验证你计划上可用的模型：

```sh
curl -H "Authorization: Bearer $TANZU_AI_API_KEY" \
  "$TANZU_AI_ENDPOINT/openai/v1/models"
```

确保模型名称完全匹配（包括前缀，例如 `Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8`）。

#### 清理

要移除服务实例及其密钥：

```sh
cf delete-service-key my-qwen-coder my-goose-key -f
cf delete-service my-qwen-coder -f
```

---

## VMware Tanzu Platform - CLI 测试指南

> 原文：https://block.github.io/goose/docs/guides/tanzu-cli-testing-guide

### 前提条件

- 从 `feat/tanzu-ai-provider` 分支构建的 goose CLI
- 一个 Tanzu AI Services 端点和 API 密钥（单模型或多模型计划）

### 定位 CLI 二进制文件

**macOS：**
```bash
# If built from source:
export GOOSE_CLI=~/claude/goose-fork/target/release/goose

# Verify:
$GOOSE_CLI --version
```

**Linux：**
```bash
# If installed via .deb:
export GOOSE_CLI=/usr/bin/goose

# If built from source:
export GOOSE_CLI=~/goose-fork/target/release/goose

# Verify:
$GOOSE_CLI --version
```

### 测试 1：配置 VMware Tanzu Platform 提供方

```bash
goose configure
```

1. 选择 **Configure Providers**
2. 滚动到 / 搜索 **VMware Tanzu Platform**
3. 当提示输入 **TANZU_AI_ENDPOINT** 时，输入你的端点 URL：
   - 单模型：`https://genai-proxy.sys.example.com/tanzu-my-model-abc1234`
   - 多模型：`https://genai-proxy.sys.example.com/tanzu-all-models-abc1234`
4. 当提示输入 **TANZU_AI_API_KEY** 时，粘贴你服务密钥中的 JWT token
5. 从动态获取的列表中选择一个模型

**预期：** 模型从端点获取并显示以供选择。

### 测试 2：启动会话（单模型计划）

```bash
export TANZU_AI_ENDPOINT="https://genai-proxy.sys.tas-tdc.kuhn-labs.com/tanzu-Qwen3-Coder-30B-A3B-vllm-v1-f3b0d18"
export TANZU_AI_API_KEY="<your-jwt-token>"

goose session
```

输入一个简单的提示词：
```
> What is 2 + 2?
```

**预期：** 模型以答案回应。如果启用了流式传输，token 会逐步出现。

### 测试 3：启动会话（多模型计划）

```bash
export TANZU_AI_ENDPOINT="https://genai-proxy.sys.tas-tdc.kuhn-labs.com/tanzu-all-models-a8a9e22"
export TANZU_AI_API_KEY="<your-jwt-token>"

goose session
```

**预期：** 会话以 `goose configure` 期间所选的那个模型启动。

### 测试 4：验证流式传输

在启用流式传输的情况下（`supports_streaming: true`），响应应逐 token 出现，而不是一次性全部出现。

```
> Write a short poem about clouds
```

**预期：** 文本逐步流式传入，而不是在延迟后一次性全部出现。

### 测试 5：验证动态模型获取

```bash
goose configure
```

选择 **Configure Providers** > **VMware Tanzu Platform**。

**单模型计划的预期：** 出现一个模型（例如 `Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8`）
**多模型计划的预期：** 出现多个模型（例如 `Qwen3.5-122B`、`Qwen3-Coder-30B`、`gpt-oss-120b`）

### 测试 6：验证错误消息

#### 缺少 API 密钥
```bash
unset TANZU_AI_API_KEY
goose session
```
**预期：** 清晰的错误消息："Required API key TANZU_AI_API_KEY is not set."

#### 缺少端点
```bash
unset TANZU_AI_ENDPOINT
goose session
```
**预期：** 关于 TANZU_AI_ENDPOINT 未设置的清晰错误消息。

#### 错误的端点
```bash
export TANZU_AI_ENDPOINT="https://genai-proxy.sys.example.com/nonexistent"
export TANZU_AI_API_KEY="invalid-key"
goose session
```
**预期：** 连接或认证错误，而不是崩溃。

### 测试 7：在计划之间切换

1. 使用多模型端点进行配置，选择一个模型，启动会话，验证其可用
2. 再次运行 `goose configure`
3. 将 TANZU_AI_ENDPOINT 更改为单模型端点
4. 选择该单一模型
5. 启动新会话，验证其可用

**预期：** 两种计划都能正常工作，无需重启 goose。

### 快速 Curl 验证

在使用 goose 测试之前，你可以直接验证端点：

```bash
# Test models endpoint
curl -s -H "Authorization: Bearer $TANZU_AI_API_KEY" \
  "$TANZU_AI_ENDPOINT/openai/v1/models" | python3 -m json.tool

# Test chat completions
curl -s -X POST "$TANZU_AI_ENDPOINT/openai/v1/chat/completions" \
  -H "Authorization: Bearer $TANZU_AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8","messages":[{"role":"user","content":"hello"}],"max_tokens":10}'

# Test streaming
curl -s -N -X POST "$TANZU_AI_ENDPOINT/openai/v1/chat/completions" \
  -H "Authorization: Bearer $TANZU_AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8","messages":[{"role":"user","content":"hello"}],"max_tokens":10,"stream":true}'
```

---

## GDK 概览

> 原文：https://block.github.io/goose/docs/gdk

goose 开发套件（GDK）提供开发人员构建智能体应用所需的核心组件，包括代理编排、模型访问、上下文管理、工具、记忆、远程执行、自动化以及路由。有两种使用方式：

- [SDK](https://block.github.io/goose/docs/gdk/sdk) — 从 Rust、Python 或 Kotlin 以进程内库的形式使用 goose 的提供方层。
- [ACP](https://block.github.io/goose/docs/gdk/acp) — 通过 stdio、HTTP 或 WebSocket 将 goose 作为单独的代理进程连接。

---

## 将 goose 用作 ACP Agent

> 原文：https://block.github.io/goose/docs/gdk/acp

使用 [Agent Client Protocol (ACP)](https://agentclientprotocol.com/) 构建客户端，连接到 goose 的代理运行时、工具、扩展以及已配置的模型。这些客户端可以是代码编辑器、桌面、Web 或移动应用、自动化服务，或其他自定义集成。

关于 goose 在标准 ACP 方法之外提供的其他方法，参见 [goose ACP 参考](https://block.github.io/goose/docs/gdk/acp/reference)。

### 安装

根据你的 ACP 客户端运行 goose 的方式选择一种安装方法。

#### 安装 goose CLI

安装 [goose CLI](https://block.github.io/goose/docs/getting-started/installation)，以配置客户端启动 `goose acp`，或自行运行 `goose serve`。

#### 从 ACP Registry 安装

受支持的 ACP 客户端可以通过 [ACP Registry 中的 goose 条目](https://agentclientprotocol.com/get-started/registry#goose)为你安装和管理 goose。这不需要单独安装 goose CLI。

### 运行代理

#### 通过 stdio 连接

配置你的 ACP 客户端，使用以下命令将 goose 作为子进程启动：

```bash
goose acp
```

客户端通过 stdin 和 stdout 与 goose 通信，并在连接的整个生命周期内管理该进程。

#### 通过 HTTP 或 WebSocket 连接

当你的 ACP 客户端通过 HTTP 或 WebSocket 连接时，运行 `goose serve`：

```bash
GOOSE_SERVER__SECRET_KEY='a-long-random-secret' goose serve
```

`GOOSE_SERVER__SECRET_KEY` 设置你的客户端用于认证的密钥。当你直接运行 `goose serve` 时，它监听 `127.0.0.1:3284` 并在 `/acp` 暴露 ACP 端点。要使用不同的地址，传入 `--host` 和 `--port`。

##### 认证

HTTP 客户端使用 `X-Secret-Key` 头进行认证。WebSocket 客户端可以使用相同的头，但基于浏览器的 WebSocket 客户端必须在 `?token=` 查询参数中传递密钥。未携带正确密钥的请求会收到 `401 Unauthorized` 响应。

:::warning 仅用于本地开发
传入 `--dangerously-unauthenticated` 会在不进行认证的情况下启动 `goose serve`。仅当服务器与不受信任的流量隔离时才使用它。
:::

##### 浏览器源（Browser origins）

大多数客户端无需配置源。从非环回源提供服务的基于浏览器的客户端，在启动 goose 时必须允许该源。要同时允许本地开发客户端和已部署的 Web 客户端，请指定两个源：

```bash
GOOSE_SERVER__SECRET_KEY='a-long-random-secret' goose serve \
  --allowed-origin 'http://localhost:5173' \
  --allowed-origin 'https://app.example'
```

指定任何 `--allowed-origin` 值都会替换默认的环回源，因此请包含你的客户端需要的每一个源，包括用于开发的 localhost 源。源必须完全匹配，包括 scheme 和 port。

关于远程部署、TLS 和证书设置，参见[运行远程 goose 服务器](https://block.github.io/goose/docs/guides/remote-goose-server)。
运行 `goose serve --help` 获取完整的选项列表。

### ACP 客户端示例

#### 通过 stdio 的客户端

浏览[官方 ACP 客户端目录](https://agentclientprotocol.com/get-started/clients)，寻找可以运行本地 ACP Agent 的客户端。关于安装和配置 goose 作为 stdio Agent 的完整示例，参见 [Zed 设置示例](https://block.github.io/goose/docs/gdk/acp/zed)。

#### 通过 WebSocket 的 goose Desktop

[goose Desktop](https://github.com/aaif-goose/goose/tree/main/ui/desktop) 是一个使用 WebSocket 的 ACP 客户端。它在某个可用的环回端口上本地启动 `goose serve`，并通过 WebSocket 连接到其 `/acp` 端点。

---

## 在 Zed 中设置 goose

> 原文：https://block.github.io/goose/docs/gdk/acp/zed

Zed 可以将 goose 作为 ACP Agent 运行。从 ACP Registry 安装 goose 以获得最简单的设置，或手动配置以使用你自己的 goose 二进制文件和环境变量覆盖。

### 从 ACP Registry 安装 goose

Zed 内置支持 ACP Registry，因此它可以为你下载并运行 goose，无需手动配置。

1. 打开 Zed
2. 打开 Agent Settings
3. 点击 `Add Agent`，然后选择 `Install from Registry`
4. 选择 `goose`

从 Registry 安装的 goose 运行相同的 `goose acp` 服务器，并读取你现有的 goose 配置，因此你的提供方、模型和扩展都会延续过来。Zed 会为你保持已安装版本为最新。

### 手动配置 goose

如果你想运行自己的 goose 二进制文件（例如本地开发构建），或传入环境变量覆盖，请使用自定义代理。

#### 前提条件

确保你已同时安装 Zed 和 goose CLI：

- **Zed**：从 [zed.dev](https://zed.dev/) 下载
- **goose CLI**：遵循[安装指南](https://block.github.io/goose/docs/getting-started/installation)

验证 goose 已安装：

```bash
goose --version
```

#### 将 goose 添加到你的 Zed 设置

1. 打开 Zed
2. 打开 Agent Settings，点击 `Add Agent`，然后选择 `Add Custom Agent`。Zed 会搭建一个 `agent_servers` 条目并打开你的设置文件
3. 编辑该条目使其运行 goose：

```json
{
  "agent_servers": {
    "goose": {
      "type": "custom",
      "command": "goose",
      "args": ["acp"]
    }
  }
}
```

现在你可以直接在 Zed 中与 goose 交互。ACP 会话使用你 goose 配置中启用的扩展，因此它们的工具在 Zed 中也可用。

### 覆盖提供方和模型

默认情况下，goose 使用你的[配置文件](https://block.github.io/goose/docs/guides/config-files)中定义的提供方和模型。使用 `GOOSE_PROVIDER` 和 `GOOSE_MODEL` 环境变量为特定的代理配置覆盖它们。

这个示例配置了两个具有不同模型设置的 goose 代理：

```json
{
  "agent_servers": {
    "goose": {
      "type": "custom",
      "command": "goose",
      "args": ["acp"]
    },
    "goose (GPT-4o)": {
      "type": "custom",
      "command": "goose",
      "args": ["acp"],
      "env": {
        "GOOSE_PROVIDER": "openai",
        "GOOSE_MODEL": "gpt-4o"
      }
    }
  }
}
```

### 将 Zed MCP 服务器与 goose 一起使用

Zed 的 `context_servers` 配置中的 MCP 服务器会自动对 goose 可用。这让原生 Zed 功能和 goose Agent 可以使用相同的 MCP 服务器。

```json
{
  "context_servers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/allowed/dir"
      ]
    }
  },
  "agent_servers": {
    "goose": {
      "type": "custom",
      "command": "goose",
      "args": ["acp"]
    }
  }
}
```

当 `context_servers` 中的所有 MCP 服务器使用 stdio（基于命令）或 HTTP 传输时，它们都对 goose 可用。goose 不支持使用已弃用的 SSE 传输的服务器。

如果 `context_servers` 中的某个服务器与某个 goose 扩展同名，goose 会使用它自己的[配置](https://block.github.io/goose/docs/guides/config-files)。

---

## SDK

> 原文：https://block.github.io/goose/docs/gdk/sdk

SDK 将其提供方层作为进程内库暴露，以便你可以从自己的应用中调用模型、流式传输补全并压缩对话。

一个 Rust crate `goose-sdk` 是每种语言绑定的来源。Python 和 Kotlin 使用 [UniFFI](https://github.com/mozilla/uniffi-rs)从它生成，因此三种语言共享相同的类型、行为和版本号。

参见 [API 参考](https://block.github.io/goose/docs/gdk/sdk/api-reference)，了解你所用语言的完整接口。

:::info Alpha
SDK 处于 alpha 阶段。接口可能在不同 `0.x` 版本之间发生变化。升级时请固定一个确切的版本，并查看 API 参考的版本选择器。
:::

### 你可以做什么

- 为 OpenAI、Anthropic、Groq、Databricks 或任何在 JSON 中定义的[声明式提供方](#declarative-providers)构造提供方
- 逐块流式传输补全，包括工具调用和推理输出
- 请求单次非流式补全
- 将长对话压缩为摘要，使其能够越过模型的上下文窗口继续
- 将提供方请求日志捕获为 JSONL

### 安装

<!-- prettier-ignore-start -->

#### Rust

```bash
cargo add goose-sdk --features uniffi
```

`uniffi` feature 启用此处记录的进程内提供方 API。

#### Python

```bash
pip install goose-sdk
```

该包以 `goose-sdk` 安装并以 `goose` 导入。wheel 中捆绑了原生库，因此无需构建其他内容。需要 Python 3.9+。

```python
import goose
```

#### Kotlin / JVM

```kotlin
dependencies {
    implementation("io.github.aaif-goose:gdk:<version>")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")
}
```

该 artifact 版本与 Rust crate 版本一致。类位于 `io.github.aaif_goose` 包中。该 jar 捆绑了适用于 macOS（arm64、x86-64）、Linux（arm64、x86-64）和 Windows（x86-64）的原生库。

在 JDK 24+ 上，添加 `--enable-native-access=ALL-UNNAMED`，因为 GDK 通过 JNA 加载其原生库。

<!-- prettier-ignore-end -->

### 快速开始

每个示例都会构建一个提供方、发送一条消息并打印流式响应。

#### Python

```python
import asyncio
from goose import (
    MessageContent,
    MessageRole,
    ProviderMessage,
    ProviderModelConfig,
    StreamChunk,
    openai_default_model,
    openai_provider,
)


async def main() -> None:
    provider = openai_provider(api_key="...")
    model = ProviderModelConfig(model_name=openai_default_model())
    messages = [
        ProviderMessage(
            role=MessageRole.USER,
            content=[MessageContent.Text(text="What is the capital of France?")],
        )
    ]

    stream = await provider.stream(model, "You are a geography expert.", messages, [])
    while chunk := await stream.next_chunk():
        if isinstance(chunk, StreamChunk.TextChunk):
            print(chunk.text, end="")


asyncio.run(main())
```

#### Kotlin

```kotlin
import io.github.aaif_goose.MessageContent
import io.github.aaif_goose.MessageRole
import io.github.aaif_goose.ProviderMessage
import io.github.aaif_goose.ProviderModelConfig
import io.github.aaif_goose.StreamChunk
import io.github.aaif_goose.streamFlow
import io.github.aaif_goose.providers.openai.defaultModel
import io.github.aaif_goose.providers.openai.provider as openAiProvider
import kotlinx.coroutines.runBlocking

fun main() = runBlocking {
    val provider = openAiProvider(System.getenv("OPENAI_API_KEY"))
    val model = ProviderModelConfig(modelName = defaultModel())
    val messages = listOf(
        ProviderMessage(
            role = MessageRole.USER,
            content = listOf(MessageContent.Text(text = "What is the capital of France?")),
        ),
    )

    provider.streamFlow(model, "You are a geography expert.", messages)
        .collect { chunk ->
            if (chunk is StreamChunk.TextChunk) print(chunk.text)
        }
}
```

#### Rust

```rust
use goose_sdk::bindings::{
    openai_default_model, openai_provider, MessageContent, MessageRole, ProviderMessage,
    ProviderModelConfig, StreamChunk,
};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let provider = openai_provider(std::env::var("OPENAI_API_KEY")?)?;
    let model = ProviderModelConfig {
        model_name: openai_default_model(),
        ..Default::default()
    };
    let messages = vec![ProviderMessage {
        role: MessageRole::User,
        content: vec![MessageContent::Text {
            text: "What is the capital of France?".to_string(),
        }],
    }];

    let stream = provider
        .stream(model, "You are a geography expert.".to_string(), messages, vec![])
        .await?;

    while let Some(chunk) = stream.next_chunk().await? {
        if let StreamChunk::TextChunk { text } = chunk {
            print!("{text}");
        }
    }
    Ok(())
}
```

### Kotlin 惯用法

Kotlin 包在生成的绑定之上添加了一些便利：

| Kotlin API | 等价的生成调用 |
| --- | --- |
| `provider.streamFlow(model, system, messages, tools)` | `stream(...)` 加一个 `nextChunk()` 循环，作为 `Flow<StreamChunk>` |
| `providers.openai.provider(apiKey)` | `openaiProvider(apiKey)` |
| `providers.openai.defaultModel()` | `openaiDefaultModel()` |
| `providers.anthropic.provider(apiKey, baseUrl, betaHeaders)` | `anthropicProvider(...)` |
| `providers.groq.provider(apiKey)` | `groqProvider(apiKey)` |
| `providers.databricks.provider(host, token)` | `databricksProvider(host, token)` |

`tools` 在 Kotlin 辅助函数中默认是一个空列表，挂起函数映射到 Kotlin 协程。错误以 `GooseException` 子类的形式出现。

### 声明式提供方

任何使用兼容 OpenAI 或 Anthropic API 的提供方都可以在 JSON 中定义，并无需新的 Rust 代码即可加载：

```python
provider = goose.declarative_provider_from_json(open("deepseek.json").read())
```

JSON 中的环境变量占位符（如 `${DEEPSEEK_API_KEY}`）会在构造提供方时被解析。

### 流式模型

`stream()` 返回一个 `ProviderStream`。反复调用 `next_chunk()` 直到它返回 `None` 以消费响应：

| Chunk | 含义 |
| --- | --- |
| `TextChunk` | 助手文本 |
| `ToolChunk` | 一次带有 JSON 参数和提供方工具调用 `index` 的工具调用请求 |
| `ThinkingChunk` / `RedactedThinkingChunk` | 推理输出 |
| `EndChunk` | 流结束，携带最终的 token `Usage` |
| `ErrorChunk` | 流中途失败，携带一个 `GooseStreamError` |

在流开始之前抛出的错误会作为 `GooseError`（Kotlin 中为 `GooseException`）抛出。流中途发生的错误则以 `ErrorChunk` 的形式到达。

---

## SDK 参考

> 原文：https://block.github.io/goose/docs/gdk/sdk/api-reference

完整的 SDK 接口。使用切换开关来切换语言和 SDK 版本——名称和类型按照每种语言自身的约定显示。

刚接触 SDK？请从 [SDK 概览](https://block.github.io/goose/docs/gdk/sdk)开始，了解安装和可运行的示例。

<GdkApiReference />
