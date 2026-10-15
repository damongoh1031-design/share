# goose 官方文档中文手册：第 22 章　排错与实验特性

## 排错

> 原文：https://block.github.io/goose/docs/troubleshooting

需要帮助时获取支持、上报缺陷、请求新功能，并找到常见问题的解决方案。goose 提供内置诊断能力以及直达支持渠道的链接。

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>🛠️ 获取帮助</h2>
  <div className={styles.cardGrid}>
    <Card 
      title="诊断与上报"
      description="使用内置诊断、上报缺陷并请求新功能。包含生成排错数据的分步指南。"
      link="https://block.github.io/goose/docs/troubleshooting/diagnostics-and-reporting"
    />
    <Card
      title="调试桌面版启动失败"
      description="找到桌面版启动诊断日志，理解其中的关键字段，并在 goose 在后端就绪前失败时附上正确的产物。"
      link="https://block.github.io/goose/docs/troubleshooting/desktop-startup-debugging"
    />
    <Card 
      title="已知问题"
      description="涵盖常见问题、错误消息和平台特定问题的综合排错指南，附带分步解决方案。"
      link="https://block.github.io/goose/docs/troubleshooting/known-issues"
    />
    <Card 
      title="日志"
      description="了解如何访问和解读 goose 会话日志与系统日志，用于调试和排错。"
      link="https://block.github.io/goose/docs/guides/logs"
    />
  </div>
</div>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>💬 社区支持</h2>
  <div className={styles.cardGrid}>
    <Card 
      title="Discord 社区"
      description="加入我们活跃的 Discord 服务器，实时获取 goose 用户和维护者提供的帮助、讨论与社区支持。"
      link="https://discord.gg/n8R5VaWDAn"
    />
    <Card 
      title="GitHub Issues"
      description="浏览已有 issue、参与讨论，或在我们 GitHub 仓库中创建新的缺陷报告和功能请求。"
      link="https://github.com/aaif-goose/goose/issues"
    />
  </div>
</div>

---

## 已知问题

> 原文：https://block.github.io/goose/docs/troubleshooting/known-issues

goose 和任何系统一样，偶尔会遇到问题。本指南为常见问题提供解决方案。

:::tip 遇到了此处未列出的问题需要帮助？
我们的 [Discord 社区](https://discord.gg/n8R5VaWDAn)随时提供帮助！如需最快的支持，建议生成一份[诊断报告](https://block.github.io/goose/docs/troubleshooting/diagnostics-and-reporting) —— 它能帮助我们快速了解你的环境。
:::

### goose 会编辑文件
goose 会在其工作流中编辑文件，这是正常行为。为避免丢失个人改动，请使用版本控制暂存你的个人修改。在审查之前，让 goose 的编辑保持未暂存状态。建议为 goose 的编辑单独提交，以便在需要时轻松回滚。

---

### 中断 goose
如果 goose 正朝着错误的方向前进或卡住了，你可以[中断它](https://block.github.io/goose/docs/guides/sessions/in-session-actions#interrupt-task)以纠正其行为或补充信息。

---

### 陷入循环或无响应
在极少数情况下，goose 可能在长时间会话中进入「死亡螺旋」或变得无响应。这通常通过结束当前会话并开启一个新会话来解决。

1. 按住 `Ctrl+C` 取消
2. 开启新会话：
  ```sh
  goose session
  ```
:::tip
对于特别庞大或复杂的任务，可考虑拆分成更小的会话。
:::

---

### 防止长时间运行的命令

如果你使用 goose CLI 并从事 Web 开发项目，可能会遇到让 goose 无限挂起的命令。像 `npm run dev`、`python -m http.server` 或 `webpack serve` 这类命令会启动永不自行退出的开发服务器。

你可以通过定制 shell 来让 goose 运行时以不同方式处理这些命令，从而避免此类问题。关于使用 `GOOSE_TERMINAL` 环境变量的详情，参见[定制 Shell 行为](https://block.github.io/goose/docs/guides/environment-variables#customizing-shell-behavior)。

---

### 上下文长度超限错误

当提供给 goose 的输入超过所使用 LLM 的最大 token 限制时，就会出现此错误。要解决它，可尝试把输入拆分成更小的部分。你也可以使用 [`.goosehints`][goosehints] 为 goose 提供详细上下文，并在 goose Desktop 中使用[消息队列](https://block.github.io/goose/docs/guides/sessions/in-session-actions#queue-messages)。

---

### 使用 Ollama 提供方

Ollama 提供本地 LLM，这意味着在尝试将此后端提供方与 goose 配合使用之前，你必须先[下载 Ollama 并运行模型](https://block.github.io/goose/docs/getting-started/providers#local-llms)。如果你没有下载模型，就会遇到以下错误：

> ExecutionError("error sending request for url (http://localhost:11434/v1/chat/completions)")

另需注意，DeepSeek 模型不支持工具调用，因此要使用这类模型之一，必须[禁用所有 goose 扩展](https://block.github.io/goose/docs/getting-started/using-extensions#enablingdisabling-extensions)。遗憾的是，若不使用工具，使用 DeepSeek 时 goose 能自主完成的事情不多。不过，Ollama 的其他模型（如 `qwen2.5`）确实支持工具调用，可与 goose 扩展一起使用。

---

### 处理速率限制错误
goose 在与 LLM 提供方交互时可能遇到 `429 error`（超出速率限制）。推荐方案是使用提供内置速率限制的提供方。更多信息参见[处理 LLM 速率限制][handling-rate-limits]。

---

### Hermit 错误

如果在应用中安装扩展时看到 "hermit:fatal" 之类的错误，你可能需要重置 hermit 缓存。我们使用
hermit 的一个副本以确保 npx 和 uvx 始终可用。如果你已经用过旧版本的 hermit，可能
需要清理缓存 —— 在 Mac 上该缓存位于

```
sudo rm -rf ~/Library/Caches/hermit
```

---

### API 错误

当用户的 LLM API token 出现问题时（例如额度用尽或配置错误），可能会遇到如下错误：

```sh
Traceback (most recent call last):
  File "/Users/admin/.local/pipx/venvs/goose-ai/lib/python3.13/site-packages/exchange/providers/utils.py",
line 30, in raise_for_status
    response.raise_for_status()
    ~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "/Users/admin/.local/pipx/venvs/goose-ai/lib/python3.13/site-packages/httpx/_models.py",
line 829, in raise_for_status
    raise HTTPStatusError(message, request=request, response=self)
httpx.HTTPStatusError: Client error '404 Not Found' for url
'https://api.openai.com/v1/chat/completions'

...
```
此错误通常在 LLM API 额度耗尽或你的 API key 无效时发生。要解决此问题：

1. 检查你的 API 额度：
    - 登录你的 LLM 提供方控制台
    - 确认你有足够的额度。如不足，请充值
2. 验证 API Key：
    - 运行以下命令重新配置你的 API key：
    ```sh
    goose configure
    ```
有关更新 LLM 提供方的详细步骤，参见[安装][installation]指南。

---

### GitHub Copilot 提供方配置

如果你在将 GitHub Copilot 配置为提供方时遇到错误，可针对常见场景尝试以下变通方案。

#### 容器与密钥环问题

goose 会尝试使用系统密钥环（通常通过 DBus 上的 Secret Service）来安全存储你的 GitHub Copilot token。在容器化或无头环境中，DBus 和/或桌面密钥环服务可能不可用（某些环境会因基于 X11 的 DBus 自动启动错误而失败），因此密钥环访问可能失败。

如果你在 Docker 容器或不支持密钥环的 Linux 环境中运行 goose，goose 可能会自动回退到[基于文件的密钥存储](#keyring-cannot-be-accessed-automatic-fallback)。

如果你仍然收到如下认证/密钥环错误，说明 goose 无法自动回退。当 goose 未将该密钥环故障识别为访问问题，或该错误与密钥环访问无关时，就可能发生这种情况。
```
Failed to save token: Failed to access keyring: <error message>
```

要解决此问题（或主动强制使用基于文件的密钥存储），把 `GOOSE_DISABLE_KEYRING` 设为任意值。下面这个示例仅在运行 `goose configure` 时设置它：

```bash
GOOSE_DISABLE_KEYRING=1 goose configure
```

如果你不想把密钥存进 `secrets.yaml`，可以改为通过环境变量来设置 token。

关于密钥环替代方案的更多细节，参见[钥匙串/密钥环错误](#keychainkeyring-errors)。

---

### 新 Recipe 警告

首次在 goose Desktop 中运行某个 recipe 时，你会看到一个 `New Recipe Warning` 对话框，供你查看该 recipe 的标题、描述和指令。如果你信任该 recipe，点击 `Trust and Execute` 继续。除非该 recipe 发生变化，否则你不会再被提示。

此警告有助于防止无意中执行可能有危害的 recipe 代码。

---

### 卸载 goose 或移除缓存数据

在重新安装之前，你可能需要卸载 goose 或清除已有数据。goose 会依据操作系统将数据存储在不同位置。密钥（如 API key）默认存储在系统钥匙串/密钥环中（在使用基于文件的密钥存储时则存于 `secrets.yaml`）。

#### macOS

**数据位置**

- **日志与配置**：`~/.config/goose`
- **应用数据**：`~/Library/Application Support/Goose`
- **密钥**：macOS 钥匙串（凭据名为 "goose"）。

#### 移除步骤

1. 停止所有正在运行的 goose 副本（CLI 或 GUI）

  - 可通过「活动监视器」确认已全部停止

2. 打开「钥匙串访问」，删除名为 "goose" 的凭据，其中包含 goose 存储的所有密钥
3. 移除数据目录：

```
rm -rf ~/.config/goose
rm -rf ~/Library/Application\ Support/goose
```
4. 从「应用程序」文件夹中删除 "goose" 应用（如果使用 goose Desktop）。

#### Linux
**数据位置**

- **数据/会话**：`~/.local/share/goose/`
- **日志**：`~/.local/state/goose/`
- **配置**：`~/.config/goose/`
- **密钥**：系统密钥环（如果可用）

#### 移除步骤

- 停止所有正在运行的 goose 副本（CLI 或 GUI）
- 从系统密钥环中清除密钥（如适用）
- 移除数据目录：

```
rm -rf ~/.local/share/goose/
rm -rf ~/.local/state/goose/
rm -rf ~/.config/goose/
```
#### Windows

**数据位置**
- **配置与数据**：`%APPDATA%\Block\goose\`
- **本地应用数据**：`%LOCALAPPDATA%\Block\goose\`
- **密钥**：Windows 凭据管理器

#### 移除步骤

1. 停止所有正在运行的 goose 副本（CLI 或 GUI）

  - 通过任务管理器确认所有实例已关闭

2. 打开 Windows 凭据管理器，删除与 "goose" 相关的凭据
3. 移除数据目录：
```
rmdir /s /q "%APPDATA%\Block\goose"
rmdir /s /q "%LOCALAPPDATA%\Block\goose"
```
4. 从「设置 > 应用」中卸载 goose Desktop 应用（如适用）

> 完成此清理后，如果你想尝试全新安装 goose，现在就可以从常规安装说明开始。
---

### 钥匙串/密钥环错误

goose 默认尝试使用系统密钥环（macOS 上为钥匙串）来存储密钥。在无法访问密钥环（或不支持密钥环）的环境中，你可能会看到如下错误：

```bash
Error Failed to access secure storage (keyring): Platform secure storage failure: DBus error: The name org.freedesktop.secrets was not provided by any .service files
Please check your system keychain and run 'goose configure' again.
If your system is unable to use the keyring, please try setting secret key(s) via environment variables.
```

在某些情况下，goose 可能会自动回退到基于文件的密钥存储。参见[无法访问密钥环（自动回退）](#keyring-cannot-be-accessed-automatic-fallback)。

如果你仍然收到密钥环错误，请使用以下选项之一：

- **设置提供方专属环境变量**，可在[支持的 LLM 提供方][configure-llm-provider]中找到。
  - 仅在当前会话期间有效：`export GOOGLE_API_KEY=$YOUR_KEY_HERE`
  - 跨新 shell 持久生效：把它加入你的 `~/.bashrc` 或 `~/.zshrc`（或等价文件）

    然后在提示是否把该值保存到密钥环时选择 `No` 选项。

  ```bash
  $ goose configure

  Welcome to goose! Let's get you set up with a provider.
    you can rerun this command later to update your configuration

  ┌   goose-configure
  │
  ◇  Which model provider should we use?
  │  Google Gemini
  │
  ◇  GOOGLE_API_KEY is set via environment variable
  │
  ◇  Would you like to save this value to your keyring?
  │  No
  │
  ◇  Enter a model from that provider:
  │  gemini-2.0-flash-exp
  ```

- **如果需要禁用密钥环**，把 `GOOSE_DISABLE_KEYRING` 设为任意值，强制使用基于文件的密钥存储。实际值无关紧要，只取决于该变量是否被设置。

  下面这个示例仅在运行 `goose configure` 时设置它：

  ```bash
  GOOSE_DISABLE_KEYRING=1 goose configure
  ```

当密钥环被禁用（或无法访问且 goose 回退到基于文件的密钥存储）时，密钥存储于此：

- macOS/Linux：`~/.config/goose/secrets.yaml`
- Windows：`%APPDATA%\Block\goose\config\secrets.yaml`

详情参见[配置文件](https://block.github.io/goose/docs/guides/config-files)。

---

### 无法访问密钥环（自动回退）

goose 默认使用系统密钥环（macOS 上为钥匙串）来存储密钥。如果无法访问密钥环，goose 可能会回退到基于文件的密钥存储。

在这种情况下，你可能会在日志中看到如下警告：

```text
Keyring unavailable. Using file storage for secrets.
```

自动回退仅适用于当前 goose 进程。当你开启新会话时，goose 会再次尝试使用密钥环。

如果你需要强制使用基于文件的密钥存储（例如在容器或无头环境中），把 `GOOSE_DISABLE_KEYRING` 设为任意值：

```bash
GOOSE_DISABLE_KEYRING=1 goose configure
```

关于 `secrets.yaml` 的细节，参见[配置文件](https://block.github.io/goose/docs/guides/config-files)。

### 包运行器

许多外部扩展都需要一个包运行器。例如，如果你遇到这样的错误：

```
Failed to start extension `{extension name}`: Could not run extension command (`{extension command}`): No such file or directory (os error 2)
Please check extension configuration for {extension name}.
```

……这表示该扩展可能尚未安装，你需要包运行器才能安装它。

一个例子是 GitHub 扩展，其命令为 `npx -y @modelcontextprotocol/server-github`。你需要在系统上安装 [Node.js](https://nodejs.org/) 才能运行该命令，因为它使用了 `npx`。

---

### Node.js 扩展在 Windows 上无法激活

如果你在 Windows 上尝试激活基于 Node.js 的扩展时遇到错误 `Node.js installer script not found`，这很可能是 goose 在预期的系统路径中找不到 Node.js。

#### 症状：
- Node.js 已安装且可正常工作（用 `node -v` 和 `npm -v` 验证过）
- 其他扩展（如基于 Python 的扩展）工作正常
- 错误仅在激活 Node.js 扩展时出现

#### 解决方案：
此问题通常发生在 Node.js 安装于非标准位置时。goose 期望在 `C:\Program Files\nodejs\` 找到 Node.js，但它可能安装在别处（例如 `D:\Program Files\nodejs\`）。

1. **检查你的 Node.js 安装路径：**
   ```powershell
   where.exe node
   ```

2. **如果 Node.js 不在 `C:\Program Files\nodejs\`，创建一个符号链接：**
   - 以管理员身份打开 PowerShell
   - 创建一个符号链接，把 goose 重定向到你实际的 Node.js 安装位置：
   ```powershell
   mklink /D "C:\Program Files\nodejs" "D:\Program Files\nodejs"
   ```
   （把 `D:\Program Files\nodejs` 替换为你实际的 Node.js 安装路径）

3. **重启 goose** 并再次尝试激活该扩展。

这会创建一个符号链接，使 goose 能在预期位置找到 Node.js，同时保持你实际的安装不受影响。

---

### 检测到恶意包 

如果你在尝试使用某个扩展时看到关于 "blocked malicious package"（已阻止的恶意包）的错误，说明该扩展被阻止了，因为其使用的某个包中检测到了恶意软件。错误消息会包含该包的详细信息，例如：

```
Blocked malicious package: package-name@1.0.0 (npm). OSV MAL advisories: MAL-2024-1234
```

解决步骤：
1. **寻找替代方案**：在[扩展目录][extensions-directory]或 [PulseMCP](https://www.pulsemcp.com/servers) 中寻找类似的扩展
2. **可选的验证**：核实被阻止扩展的来源，或包名/发布者
3. **上报误报**：如果你认为这是误判，请[提交 issue](https://github.com/aaif-goose/goose/issues)

此安全检查仅适用于使用 PyPI（`uvx`）或 NPM（`npx`）的本地执行外部扩展。该检查使用 OSV 数据库的实时数据；如果安全服务不可用，扩展仍会正常安装。

最佳实践是：只从可信的官方来源安装扩展。

---

### macOS 权限问题

如果 goose Desktop 应用启动时不显示窗口，可能是文件与文件夹权限导致的。这通常是因为 goose 需要对 `~/.config` 目录的读写权限，以创建其日志目录和文件。
同样，如果工具在使用过程中无法创建文件或目录，也可能是同一个权限问题造成的。

#### 如何检查并修复权限：

1. 打开「终端」。
2. 运行以下命令查看 ~/.config 的当前权限：
  ```sh
  ls -ld ~/.config
  ```
**示例输出：**
  ```sh
  drwx------  7 yourusername  staff  224 Jan 15 12:00 /Users/yourusername/.config
  ```
`rwx` 表示你的用户拥有读（r）、写（w）和执行（x）权限。如果你的用户没有 `rwx`，请按以下步骤操作。

#### 如何授予读写权限：

1. 要添加正确的权限，请运行以下命令：
    ```sh
    chmod u+rw ~/.config
    ```
    如果 ~/.config 目录不存在，请先创建它再分配权限：
      ```sh
      mkdir -p ~/.config
      chmod u+rw ~/.config
      ```
2. 验证更改：
    ```sh
    ls -ld ~/.config
    ```

如果在修复权限后仍然遇到问题，可尝试以超级用户（管理员）权限启动 goose：
```sh
sudo /Applications/Goose.app/Contents/MacOS/Goose
```

:::note
以 sudo 运行 goose 可能会创建由 root 拥有的文件，从而导致更多权限问题。请将此作为排错步骤，而非常久性修复。
:::

#### 在「系统设置」中更新权限（macOS）
1. 前往 `System Settings` -> `Privacy & Security` -> `Files & Folders`
2. 授予 goose 访问权限

---

### WSL 上 Ollama 提供方的连接错误

如果在 goose 中将 Ollama 设置为提供方时遇到如下错误：
    ```
    Execution error: error sending request for url (http://localhost:11434/v1/chat/completions)
    ```
这很可能意味着本地主机地址无法从 WSL 访问。
1. 检查服务是否正在运行：
    ```
    curl http://localhost:11434/api/tags
    ```
    如果你收到 `failed to connect` 错误，可能是 WSL 对 localhost 使用了不同的 IP。在这种情况下，运行以下命令找到 WSL 的正确 IP 地址：
    ```
    ip route show | grep -i default | awk '{ print $3 }'
    ```
2. 拿到 IP 地址后，在你的 goose 配置中用它替代 localhost。例如：
    ```
    http://172.24.80.1:11434
    ```
    
如果你仍然遇到 `failed to connect` 错误，且使用的是 Windows 11 22H2 或更高版本，可以尝试使用 WSL 的[镜像网络](https://learn.microsoft.com/en-us/windows/wsl/networking#mirrored-mode-networking)设置 

---

### 企业代理或防火墙问题

如果你位于企业代理或防火墙之后，且 goose 无法连接到你的 LLM 提供方，你可能会看到如下错误：

```
error sending request for url (https://api.openai.com/...)
failed to connect to api.openai.com
```

goose 通过标准环境变量和系统代理设置支持 HTTP/HTTPS 代理配置。两者都配置时，环境变量优先。

**解决方案：**

1. **配置[代理环境变量](https://block.github.io/goose/docs/guides/environment-variables#network-configuration)：**
   ```bash
   export HTTPS_PROXY="http://proxy.company.com:8080"
   export NO_PROXY="localhost,127.0.0.1,.internal"
   ```

2. **或使用系统代理设置：**
   - **macOS**：系统设置 → 网络 → [选择连接] → 详细信息 → 代理
   - **Windows**：设置 → 网络和 Internet → 代理

3. 配置代理设置后**重启 goose**

如果仍然遇到连接问题，请核实：
- 你的代理 URL 和端口是否正确
- 如需认证，你是否有认证凭据（格式：`http://username:password@proxy:port`）
- 你的代理是否允许到 LLM 提供方域名的 HTTPS 连接

---

### 隔离/离线环境问题

如果你在隔离、离线或企业受限的环境中工作，可能会遇到 MCP 服务器扩展无法激活或无法下载其运行时依赖的问题。

#### 症状：
- 扩展激活失败，并报出关于缺少运行时环境的错误消息
- 错误包含 "hermit:fatal" 或互联网下载失败
- 扩展在个人机器上可用，但在企业/受限网络中失败
- 错误消息类似：`Failed to start extension: Could not run extension command`

#### 解决方案：
goose Desktop 使用 **"shims"**（打包的 `npx` 和 `uvx` 版本），它们会通过 Hermit 自动下载运行时环境。在受限网络中，这些下载会失败。

**变通方案 - 使用自定义命令名：**

1. **在系统上创建包运行器的替代命名版本：**
   ```bash
   # For uvx (Python packages)
   ln -s /usr/local/bin/uvx /usr/local/bin/runuv
   
   # For npx (Node.js packages)  
   ln -s /usr/local/bin/npx /usr/local/bin/runnpx
   ```

2. **更新你的 MCP 服务器配置以使用自定义名称：**
   
   不要用：
   ```yaml
   extensions:
     example:
       cmd: uvx
       args: [mcp-server-example]
   ```
   
   改用：
   ```yaml
   extensions:
     example:
       cmd: runuv  # This bypasses goose's shims
       args: [mcp-server-example]
   ```

3. **为什么这样可行：** goose 只会把已知的命令名（`npx`、`uvx`、`jbang` 等）替换为其打包的 shims。自定义名称会原样传递给系统中真正的可执行文件。

4. **需要更多改动**：在企业代理环境或隔离环境中，如果上述方法无效，建议你根据自身网络限制（例如 TLS 证书限制、[代理配置](https://block.github.io/goose/docs/guides/environment-variables#network-configuration)、无法下载所需内容等），自定义并打包 goose Desktop，使其附带在该网络约束下可用的 shims/配置。

#### 文档访问：
`goose-doc-guide` Skill 默认从 `https://goose-docs.ai` 读取 goose 文档，该地址在离线时不可用。要让 goose 改从本地文档副本读取，参见[离线/隔离环境文档](https://block.github.io/goose/docs/guides/offline-docs)。

---

### 需要更多帮助？ 

仍然遇到问题？我们随时提供帮助！加入我们的 [Discord 社区][discord]，goose 团队和社区成员乐于提供协助。

:::tip
如果你能在提问时附上一份[诊断报告](https://block.github.io/goose/docs/troubleshooting/diagnostics-and-reporting#diagnostics-system)，它有助于我们了解你的环境并提供更有针对性的解决方案。
:::

[handling-rate-limits]: https://block.github.io/goose/docs/guides/handling-llm-rate-limits-with-goose
[installation]: https://block.github.io/goose/docs/getting-started/installation
[discord]: https://discord.gg/n8R5VaWDAn
[goosehints]: https://block.github.io/goose/docs/guides/context-engineering/using-goosehints
[configure-llm-provider]: https://block.github.io/goose/docs/getting-started/providers
[extensions-directory]: https://block.github.io/goose/extensions

---

## 诊断与上报

> 原文：https://block.github.io/goose/docs/troubleshooting/diagnostics-and-reporting

goose 提供多项内置功能，帮助你获取支持、上报问题并请求新功能。本指南涵盖诊断系统、缺陷上报和功能请求工具。

| 功能 | 用途 | 位置 | 输出 |
|---------|---------|----------|---------|
| **诊断** | 生成排错数据 | 聊天输入工具栏 | 包含系统信息、日志和会话数据的 JSON 报告 |
| **上报缺陷** | 提交缺陷报告 | 聊天输入工具栏 或 设置 → 应用 → 帮助与反馈 | 打开 GitHub issue 模板 |
| **请求功能** | 建议新功能 | 设置 → 应用 → 帮助与反馈 | 打开 GitHub issue 模板 |

### 诊断系统

诊断功能会生成一份全面的排错 JSON 报告，包含系统信息、会话数据、配置文件以及最近的日志。这对调试问题或获取技术支持非常有价值。

#### 生成诊断

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    1. 在活跃的聊天会话中，找到底部工具栏里的 <Bug className="inline" size={16} /> 图标
    2. 点击诊断按钮
    3. 在弹窗中查看关于将要收集哪些数据的说明
    4. 点击 `Download` 生成并保存诊断报告
    5. JSON 文件将保存为 `diagnostics_{session_id}.json`

    你可以使用 `scripts/diagnostics-viewer.py` 来查看下载的诊断报告；默认它会查找 `~/Downloads`。

    :::tip
    诊断按钮仅在你有活跃会话时可用，因为它需要会话 ID 才能生成诊断包。
    :::
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    使用会话诊断命令生成排错包。完整细节和所有可用选项，参见 [CLI 命令指南](https://block.github.io/goose/docs/guides/goose-cli-commands#session-diagnostics-options)。

    ```sh
    # Generate diagnostics for a specific session
    goose session diagnostics --session-id <session_id>

    # Interactive selection (prompts you to choose a session)
    goose session diagnostics

    # Save to a custom location
    goose session diagnostics --session-id <session_id> --output /path/to/diagnostics.json
    ```

    要找到你的会话 ID，先列出可用会话：

    ```sh
    goose session list
    ```

    示例输出：
    ```
    Available sessions:
    abc123def - My coding session - 2024-01-15 14:30:22
    xyz789ghi - Documentation work - 2024-01-15 10:15:45
    ```
  </TabItem>
</Tabs>

### 使用诊断数据

诊断 JSON 文件包含多个结构化分区：

```json
{
  "system": {},
  "session": {},
  "config": {},
  "logs": {},
  "prompts": [],
  "schedule": {},
  "errors": []
}
```

**何时生成诊断：**
- 遇到崩溃或异常行为
- 收到看不懂的错误消息
- 性能问题或响应缓慢
- 在向上报缺陷前生成，以便附上技术细节

**诊断中包含哪些内容：**
- **系统信息**：应用版本、操作系统、架构和时间戳
- **会话数据**：你当前的对话消息和历史
- **配置文件**：你的[配置文件](https://block.github.io/goose/docs/guides/config-files)（如果存在）
- **日志文件**：用于调试的最近应用日志

:::warning 隐私声明
诊断包包含你的会话消息和系统信息。如果你的会话包含敏感数据（API key、个人信息、专有代码），请先审查内容再公开分享。
:::

### 缺陷报告

缺陷报告功能会打开一个结构化的 GitHub issue 模板，帮助你提供有效上报缺陷所需的全部信息。

#### 创建缺陷报告

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    1. 在活跃的聊天会话中，找到底部工具栏里的 <Bug className="inline" size={16} /> 图标
    2. 点击诊断按钮
    3. 点击 `File Bug on GitHub`
    4. 这会在浏览器中打开 GitHub，并预填缺陷报告模板
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    CLI 用户可直接前往 GitHub 仓库：

    ```
    https://github.com/aaif-goose/goose/issues/new?template=bug_report.md
    ```
  </TabItem>
</Tabs>

### 功能请求

功能请求系统帮助你为 goose 建议改进和新功能。

#### 提交功能请求

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏
    2. 在侧边栏中点击 `Settings`
    3. 点击 `App` 标签页
    4. 向下滚动到 `Help & feedback` 区域
    5. 点击 `Request a Feature`
    6. 这会在浏览器中打开 GitHub，并预填功能请求模板
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    直接前往 GitHub 仓库：

    ```
    https://github.com/aaif-goose/goose/issues/new?template=feature_request.md
    ```
  </TabItem>
</Tabs>

### 使用「Ask goose」进行错误恢复

当 goose Desktop 中发生某些类型的错误时（例如扩展激活失败），你会在错误通知中看到一个 `Ask goose` 按钮。此功能让你借助 goose 的帮助快速排查问题：

1. 错误发生时，错误通知中会出现一个 `Ask goose` 按钮
2. 点击该按钮，将错误详情作为聊天提示词发送给 goose
3. goose 会给出诊断建议和可能的解决方案

### 其他调试

对于诊断无法解决的问题：

- **[会话与系统日志](https://block.github.io/goose/docs/guides/logs)**：查看详细日志以调试单个会话
- **[遥测导出](https://block.github.io/goose/docs/guides/environment-variables#observability)**：配置遥测以进行性能分析和生产监控

---

## 调试桌面版启动失败

> 原文：https://block.github.io/goose/docs/troubleshooting/desktop-startup-debugging

当 goose Desktop 在后端就绪之前就失败时，常规服务器日志可能为空或不完整。在这种情况下，最有用的产物是桌面应用写入的启动诊断 JSON。

### 找到启动诊断日志

goose Desktop 每次启动尝试都会写入一个启动诊断文件。

典型位置：

- macOS：`~/Library/Application Support/Goose/logs/startup/`
- Windows：`%APPDATA%\Goose\logs\startup\`
- Linux：`~/.config/Goose/logs/startup/`

文件命名类似：

```text
goosed-startup-2026-04-21T01-24-03.149Z-23416.json
```

如果存在多个文件，使用最新的那个。

### 需要分享什么

上报桌面版启动失败时，请分享：

- 最新的 `goosed-startup-*.json`
- 你的 goose 版本
- 你的操作系统及版本

对于 Windows 原生崩溃，如果可用，还请附上 `goosed.exe` 的 Windows 崩溃报告。

Windows 崩溃报告的常见位置：

- 事件查看器：`Windows Logs` → `Application`
- 可靠性监视器：`View technical details`
- 磁盘上的 WER 文件：
  - `%LOCALAPPDATA%\Microsoft\Windows\WER\ReportArchive\`
  - `%LOCALAPPDATA%\Microsoft\Windows\WER\ReportQueue\`

寻找与 `goosed.exe` 相关的 `Report.wer`。

如果你要提交 GitHub issue 或寻求支持，以下通常就够了：

- 最新的 `goosed-startup-*.json`
- 你的 goose 版本
- 你的操作系统及版本
- 在 Windows 上，如果 Windows 生成了 `goosed.exe` 的 `Report.wer`，也一并附上

### 启动日志包含什么

多数情况下，分享最新的启动日志就足够了。

如果你想快速做一次高层级解读，重点关注这些字段：

- `childExitCode` 或 `childExitSignal`
  显示后端进程是否在启动期间退出。
- `certFingerprintSeen`
  显示后端是否到达 TLS 启动阶段。
- `healthCheckSucceeded`
  显示桌面应用是否曾观察到后端就绪。
- `stderrTail`
  显示从后端捕获的最近启动输出，可用时包含主要启动阶段标记。
- `events`
  显示主要启动步骤的顺序，如进程生成、健康检查和子进程退出。

### 相关诊断

对于 goose 启动之后的会话内或应用内问题，请使用 [诊断与上报](https://block.github.io/goose/docs/troubleshooting/diagnostics-and-reporting)中描述的常规诊断包。

---

## 实验特性

> 原文：https://block.github.io/goose/docs/experimental

goose 是一个不断被改进和扩展的开源项目。这些实验特性和项目仍处于开发中，可能尚未完全稳定或未准备好用于生产环境，但它们展示了 AI 自动化未来种种令人兴奋的可能性。

:::note
实验特性列表可能会随 goose 的开发进展而变化。一些特性可能会升级为稳定特性，另一些则可能被修改或移除。随着具体实验特性可用，本节会持续更新。
:::

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>🧪 实验特性</h2>
  <div className={styles.cardGrid}>
    <Card 
      title="Ollama Tool Shim"
      description="使用实验性的本地解释器模型方案，为不原生支持工具调用的语言模型（如 DeepSeek）启用工具调用能力。"
      link="https://block.github.io/goose/docs/experimental/ollama"
    />
    <Card 
      title="远程访问"
      description="通过 goose AI 移动应用或 Telegram 等消息平台远程访问 goose。"
      link="https://block.github.io/goose/docs/experimental/remote-access"
    />
    <Card 
      title="goose for VS Code 扩展"
      description="通过 ACP 直接在 VS Code 中与 goose 交互。"
      link="https://block.github.io/goose/docs/experimental/vs-code-extension"
    />
  </div>
</div>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>📝 精选博客文章</h2>
  <div className={styles.cardGrid}>
    <Card 
      title="为工具调用微调 Toolshim 模型"
      description="通过专门的 toolshim 模型开发，解决不原生支持工具调用的模型的性能局限。"
      link="https://block.github.io/goose/blog/2025/04/11/finetuning-toolshim"
    />
    <Card 
      title="AI，但用 goose 和 Ollama 让它本地化"
      description="了解如何将 goose 与 Ollama 集成，获得完全本地的 AI 体验，包括结构化输出和工具调用能力。"
      link="https://block.github.io/goose/blog/2025/03/14/goose-ollama"
    />
    <Card 
      title="社区启发的基准测试：goose Vibe Check"
      description="在我们首批 goose 智能体基准测试中看看开源 AI 模型表现如何，包含 toolshim 性能分析。"
      link="https://block.github.io/goose/blog/2025/03/31/goose-benchmark"
    />
  </div>
</div>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>💬 反馈与支持</h2>
  <div className={styles.cardGrid}>
    <Card 
      title="GitHub Issues"
      description="上报缺陷、请求功能，或为实验特性的开发做贡献。"
      link="https://github.com/aaif-goose/goose/issues"
    />
    <Card 
      title="Discord 社区"
      description="加入我们的社区，讨论实验特性、分享反馈并与其他用户交流。"
      link="https://discord.gg/n8R5VaWDAn"
    />
  </div>
</div>

---

## goose Mobile

> 原文：https://block.github.io/goose/docs/experimental/goose-mobile

:::info 已归档
goose Mobile 已归档。此前的 iOS 移动隧道方案在当前 goose Desktop 构建中也已退役。
:::

goose Mobile 是一个受 goose 应用启发的实验性 Android 项目。它作为你手机上的开放智能体，自动化多步任务、响应通知，甚至替换你的主屏幕以实现最高效率。

:::danger 实验性
goose Mobile 需要深度访问你的设备。请自行承担风险 —— 最好在备用手机或模拟器上使用。
:::

<div style={{textAlign: 'center'}}>
  <img src="https://github.com/user-attachments/assets/af9d7d83-54f4-4ace-ad66-9e19f86c8fb9" alt="goose Mobile 截图" />
</div>

### 它能做什么
- **自动化：** 使用你已安装的应用编排任务。
- **通知处理：** 根据你的规则响应传入的通知。
- **可扩展性：** 利用来自其他应用的扩展，无缝执行后台任务。

### 安装
- **预构建 APK：** 通过 [Firebase 分发链接](https://appdistribution.firebase.google.com/pub/i/3f111ea732d5f7f6)快速安装。
- **从源码构建：** 开发者说明见 [goose Mobile 仓库](https://github.com/aaif-goose/goose-mobile)。

### 扩展 goose Mobile
goose Mobile 支持 **mobile MCP** 系统，它让你无需离开上下文即可使用其他应用的工具 —— 例如，通过天气扩展获取天气数据。  

示例代码和设置说明见仓库 [README](https://github.com/aaif-goose/goose-mobile)。

### 贡献
我们欢迎贡献！详情参见[贡献指南](https://github.com/aaif-goose/goose-mobile/blob/main/CONTRIBUTING.md)。

---

更多场景、说明和开发环境搭建，请访问 [goose Mobile 仓库](https://github.com/aaif-goose/goose-mobile)。

---

## 通过安全隧道进行移动端访问

> 原文：https://block.github.io/goose/docs/experimental/mobile-access

<Redirect to="/docs/experimental/remote-access/mobile-access" />

---

## Ollama Tool Shim

> 原文：https://block.github.io/goose/docs/experimental/ollama

:::warning 实验特性
Ollama tool shim 是实验特性。其行为与配置可能在未来的版本中变化。
:::

Ollama tool shim 为不原生支持工具调用的模型启用工具调用。完整的设置说明、配置选项和排错，参见 **[Tool Shim 指南](https://block.github.io/goose/docs/guides/tool-shim)**。

##### 快速开始

1. 安装并启动 [Ollama](https://ollama.com/download)
2. 拉取默认解释器模型：
   ```bash
   ollama pull mistral-nemo
   ```
3. 启用 shim 启动 goose：
   ```bash
   GOOSE_TOOLSHIM=true goose session
   ```

---

## goose for VS Code 扩展

> 原文：https://block.github.io/goose/docs/experimental/vs-code-extension

[goose for VS Code 扩展](https://marketplace.visualstudio.com/items?itemName=block.vscode-goose)让你直接在 VS Code 中与 goose 交互。

:::warning 实验特性
goose for VS Code 正在积极开发中。其行为与配置可能在未来的版本中变化。
:::

该扩展使用 [Agent Client Protocol (ACP)](https://block.github.io/goose/docs/gdk/acp) 与 goose 通信。

### 安装扩展

:::info 前置条件
- [VS Code](https://code.visualstudio.com/) 1.95.0 或更高版本
- [goose CLI](https://block.github.io/goose/docs/getting-started/installation)
:::

1. 前往 [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=block.vscode-goose)
2. 点击 `Install`
3. 在弹出窗口中点击 `Open Visual Studio Code`
4. 在 Visual Studio Code 中点击 `Install`
5. 点击活动栏中的 <IconGoose className="inline" size={16} /> 图标打开侧边面板，开始与 goose 聊天

### 与 goose 共享上下文

有两种方式为 goose 提供上下文。

#### 发送选中的代码

1. 在编辑器中选中你想讨论的代码
2. 将选区发送给 goose：
   - macOS：`Cmd+Shift+G`
   - Windows/Linux：`Ctrl+Shift+G`
   - 右键并选择 `Send to goose`

选中的代码会以上下文 chip 的形式出现在聊天输入框上方。

#### 通过 @ 提及附加文件

1. 在聊天输入框中输入 `@` 并开始输入文件名
2. 选择文件：
   - 用方向键（↑/↓）选择文件并按 `Enter`
   - 用鼠标选择文件

附加的文件会以上下文 chip 的形式出现在聊天输入框上方。

### 用法示例

goose for VS Code 扩展直接连接到你的编辑器，让你用 AI 管理文件、项目和工作流。它包含以下功能：

- 带流式响应的交互式聊天界面
- 访问 goose 的 AI 能力与已启用的扩展
- 带历史回放的会话管理
- 聊天界面中的上下文共享和可视化上下文 chip
- 用于复制代码片段/响应以便分享的剪贴板工具

#### goose 提示词

```
Update the contributing guide at /goose/CONTRIBUTING.md with instructions on how to start docusaurus dev server
```

#### goose 输出

```

I'll help you update the CONTRIBUTING.md file with instructions for starting the Docusaurus dev server. First, let me check the current content of the file.

─── developer__text_editor | view ──────────────────────────

I'll now update the CONTRIBUTING.md file to include instructions for starting the Docusaurus dev server. I'll add this information in a new section under the Node section.

─── developer__text_editor | str_replace ──────────────────────────

I've successfully updated the CONTRIBUTING.md file to include instructions for starting the Docusaurus dev server. I added a new "Documentation" section right after the Node section, which provides clear step-by-step instructions for:

Navigating to the docs directory
Installing dependencies
Starting the development server
I also included helpful information about the hot-reloading feature and the local server URL. The formatting is consistent with the rest of the document, using proper markdown syntax for code blocks and headers.

Is there anything else you'd like me to add or modify in the contributing guide?

```

---

## 远程访问

> 原文：https://block.github.io/goose/docs/experimental/remote-access

使用受支持的消息平台，从任何地方访问 goose。这些功能让你在离开电脑时也能与 goose 交互。

<div className={styles.cardGrid}>
  <Card 
    title="Telegram 网关"
    description="通过 Telegram 从任何设备与 goose 聊天。"
    link="https://block.github.io/goose/docs/experimental/remote-access/telegram-gateway"
  />
</div>

---

## 通过安全隧道进行移动端访问

> 原文：https://block.github.io/goose/docs/experimental/remote-access/mobile-access

通过安全隧道的移动端访问在当前 goose Desktop 构建中已不再可用。

此前的设置流程依赖一个桌面版设置面板，它会启动隧道并显示移动端连接二维码。该面板以及 `/tunnel/start` 和 `/tunnel/stop` API 已被移除，因此无法再从 Desktop 配置新的移动应用连接。

---

## Telegram 网关

> 原文：https://block.github.io/goose/docs/experimental/remote-access/telegram-gateway

Telegram 网关让你通过 Telegram 与 goose 交互，从而在任何装有 Telegram 的设备上实现远程访问。

:::warning 实验特性
网关功能是实验性的，正在积极开发中。其行为与配置可能在未来的版本中变化。
:::

### 工作原理

网关通过一个安全的配对流程把你的 Telegram 账号连接到 goose。配对完成后，你可以向一个 Telegram 机器人发送消息，机器人会把消息转发给 goose，并在 Telegram 中收到格式化后的回复。

**关键细节：**
- 使用你自行创建和配置的 Telegram 机器人
- 通过一次性验证码进行安全配对
- 支持带代码块和 markdown 的格式化回复
- 维护一个持久会话，会为长对话自动压缩
- 在任何装有 Telegram 的设备上均可使用

### 前置条件

在设置 Telegram 网关之前：

1. [配置 goose](https://block.github.io/goose/docs/getting-started/providers)，设置好提供方和模型。
2. 打开 Telegram 并搜索 [@BotFather](https://t.me/BotFather)。
3. 发送 `/newbot` 并按提示创建你的机器人。
4. 复制 BotFather 提供的 **bot token**（形如 `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）。

:::tip
妥善保管你的 bot token。任何拿到该 token 的人都能控制你的机器人。
:::

### 设置

使用 goose CLI 启动网关并配对你的 Telegram 账号。

#### 启动网关

在一个终端中，导出你的 bot token 并启动网关：

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
goose gateway start telegram --bot-token "$TELEGRAM_BOT_TOKEN"
```

让这条命令保持运行。你的电脑必须保持唤醒并在线，机器人才能响应。

#### 配对 Telegram 账号

在第二个终端中生成配对码：

```bash
goose gateway pair telegram
```

在 Telegram 中打开你的机器人，并在五分钟内把六位配对码发送给它。配对完成后机器人会确认，随后你就可以通过 Telegram 与 goose 聊天。

要停止网关，在运行它的终端中按 <kbd>Ctrl</kbd>+<kbd>C</kbd>。

### 你能做什么

配对完成后，你可以：
- 向 goose 发送消息并接收回复
- 获取带语法高亮的格式化代码块
- 跨多个会话继续对话
- 访问你已配置的 goose 扩展

### 排错

#### 机器人不响应
- 确认 bot token 正确。
- 检查 `goose gateway start` 命令是否仍在运行。
- 确保你的电脑处于唤醒并在线状态。

#### 配对码无效
- 配对码五分钟后过期。重新生成一个再试。
- 确认你把配对码发送给了正确的机器人。

#### 消息格式不正确
- 网关会把 goose 的 markdown 转换为 Telegram 兼容的格式。
- 某些复杂格式可能会为了 Telegram 兼容性而被简化。

### 其他资源

- [Telegram Bot API 文档](https://core.telegram.org/bots)
- [网关 PR #7199](https://github.com/aaif-goose/goose/pull/7199)
