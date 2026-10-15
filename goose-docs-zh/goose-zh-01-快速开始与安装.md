# goose 官方文档中文手册：第 01 章　快速开始与安装

## 快速开始：goose 五分钟入门

> 原文：https://block.github.io/goose/docs/quickstart

goose 是一个可扩展的开源 AI 代理，它通过自动化编码任务来增强你的软件开发。

本快速教程将引导你完成：

- ✅ 安装 goose
- ✅ 配置你的 LLM
- ✅ 构建一个小应用
- ✅ 添加一个 MCP 服务器

让我们开始吧 🚀

### 安装 goose

<Tabs>
  <TabItem value="mac" label="macOS" default>
    选择安装 goose 的桌面版和/或 CLI 版本：

    <Tabs groupId="interface">
      <TabItem value="ui" label="goose Desktop" default>
        <MacDesktopInstallButtons/>
        <div style={{ marginTop: '1rem' }}>
          1. 解压下载的 zip 文件。
          2. 运行可执行文件以启动 goose 桌面版应用程序。
        </div>
      </TabItem>
      <TabItem value="cli" label="goose CLI">
        运行以下命令安装 goose：

```sh
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash
```
      </TabItem>
    </Tabs>
  </TabItem>

  <TabItem value="linux" label="Linux">
    选择安装 goose 的桌面版和/或 CLI 版本：

    <Tabs groupId="interface">
      <TabItem value="ui" label="goose Desktop" default>
        <LinuxDesktopInstallButtons/>
        <div style={{ marginTop: '1rem' }}>
          **适用于基于 Debian/Ubuntu 的发行版：**
          1. 下载 DEB 文件
          2. 在终端中导航到该文件保存的目录
          3. 运行 `sudo dpkg -i (filename).deb`
          4. 从应用菜单启动 goose

        </div>
      </TabItem>
      <TabItem value="cli" label="goose CLI">
        运行以下命令在 Linux 上安装 goose CLI：

```sh
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash
```
      </TabItem>
    </Tabs>
  </TabItem>

  <TabItem value="windows" label="Windows">
    选择安装 goose 的桌面版和/或 CLI 版本：

    <Tabs groupId="interface">
      <TabItem value="ui" label="goose Desktop" default>
        <WindowsDesktopInstallButtons/>
        <div style={{ marginTop: '1rem' }}>
          1. 解压下载的 zip 文件。
          2. 运行可执行文件以启动 goose 桌面版应用程序。
        </div>
      </TabItem>
      <TabItem value="cli" label="goose CLI">

        在 **Git Bash**、**MSYS2** 或 **PowerShell** 中运行以下命令，以在 Windows 上原生安装 goose CLI：

```bash
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash
```

        在[安装指南](https://block.github.io/goose/docs/getting-started/installation)中了解前提条件。

        :::info PATH 警告与密钥环
        如果安装后看到 PATH 警告，你需要在运行 `goose configure` 之前将 goose 添加到 PATH。详细步骤请参阅 [Windows CLI 安装说明](https://block.github.io/goose/docs/getting-started/installation)。

        如果在配置过程中出现提示，请选择不存储到密钥环。如果遇到密钥环错误，请参阅 [Windows 设置说明](https://block.github.io/goose/docs/getting-started/installation#set-llm-provider)以获取更多信息。
        :::

      </TabItem>
    </Tabs>
  </TabItem>
</Tabs>

### 配置提供方

goose 可与[受支持的 LLM 提供方](https://block.github.io/goose/docs/getting-started/providers)配合使用，这些提供方为 goose 提供理解你的请求所需的 AI 智能。首次使用时，系统会提示你配置首选的提供方。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  在欢迎界面上，你有以下选项：

  <OnboardingProviderSetup />

  对于本快速入门，请选择 **Agent Router by Tetrate**。Tetrate 提供对多个 AI 模型的访问，并内置速率限制和自动故障转移。有关其他提供方的更多信息，请参阅[配置 LLM 提供方](https://block.github.io/goose/docs/getting-started/providers)。

  goose 会打开浏览器，让你使用 Tetrate 进行身份验证；如果你还没有账户，也可以创建一个新账户。当你返回 goose 桌面版应用后，即可开始你的第一个会话。

  :::info 免费额度优惠
  当你首次通过 goose 自动使用 Tetrate 进行身份验证时，将获得 $10 免费额度。此优惠对新老 Tetrate 用户均可用。
  :::

  </TabItem>
  <TabItem value="cli" label="goose CLI">
  1. 在你的终端中，运行以下命令：

```sh
goose configure
```

  2. 从菜单中选择 `Configure Providers` 并按 Enter。

```
   ┌   goose-configure 
   │
   ◆  What would you like to configure?
   │  ● Configure Providers (Change provider or update credentials)
   │  ○ Add Extension 
   │  ○ Toggle Extensions 
   │  ○ Remove Extension 
   │  ○ goose settings 
   └  
```
   3. 选择一个模型提供方。对于本快速入门，请选择 `Tetrate Agent Router Service` 并按 Enter。Tetrate 提供对多个 AI 模型的访问，并内置速率限制和自动故障转移。有关其他提供方的信息，请参阅[配置 LLM 提供方](https://block.github.io/goose/docs/getting-started/providers)。

```
   ┌   goose-configure 
   │
   ◇  What would you like to configure?
   │  Configure Providers 
   │
   ◆  Which model provider should we use?
   │  ○ Amazon Bedrock 
   │  ○ Amazon SageMaker TGI 
   │  ○ Anthropic 
   │  ○ Azure OpenAI 
   │  ○ ChatGPT Codex 
   │  ○ Claude Code CLI 
   │  ○ ...
   |  ● Tetrate Agent Router Service (Enterprise router for AI models)
   │  ○ ...
   └  
```
    :::info 免费额度优惠
    当你首次通过 goose 自动使用 Tetrate 进行身份验证时，将获得 $10 免费额度。此优惠对新老 Tetrate 用户均可用。
    :::

   4. 在出现提示时输入你的 API 密钥（以及任何其他配置详情）。

```
   ┌   goose-configure 
   │
   ◇  What would you like to configure?
   │  Configure Providers 
   │
   ◇  Which model provider should we use?
   │  Tetrate Agent Router Service 
   │
   ◆  Provider Tetrate Agent Router Service requires TETRATE_API_KEY, please enter a value
   │  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
   └  
```
    :::tip GitHub Copilot 身份验证
    GitHub Copilot 不使用 API 密钥。相反，在配置过程中会生成一个身份验证码。要生成该代码，请选择 `GitHub Copilot` 作为你的提供方。验证码会被复制到你的剪贴板，并打开一个浏览器窗口，你可以在其中粘贴它以完成身份验证。

    更多详情，请参阅 [GitHub Copilot 身份验证](https://block.github.io/goose/docs/getting-started/providers#github-copilot-authentication)。
    :::

   5. 选择或搜索你想使用的模型。

```
   │
   ◇  Model fetch complete
   │
   ◆  Select a model:
   │  ○ Search all models...
   │  ○ gemini-2.5-pro
   │  ○ gemini-2.0-flash
   |  ○ gemini-2.0-flash-lite
   │  ● gpt-5 (Recommended)
   |  ○ gpt-5-mini
   |  ○ gpt-5-nano
   |  ○ gpt-4.1
   │
   ◓  Checking your configuration...
   └  Configuration saved successfully
```
  </TabItem>
</Tabs>

### 开始会话

会话是你与 goose 之间单一、连续的对话。让我们开始一个会话。

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
        选择 LLM 提供方后，点击侧边栏中的 `Home` 按钮。

        将你的问题、任务或指令直接输入到输入框中，goose 会立即开始工作。
    </TabItem>
    <TabItem value="cli" label="goose CLI">
        1. 创建一个空目录（例如 `goose-demo`），并从终端导航到该目录。
        2. 要开始一个新会话，请运行：

```sh
goose session
```

    </TabItem>
</Tabs>

### 编写提示词

在提示词中，你可以像与开发者交谈一样输入指令，与 goose 进行交互。

让我们让 goose 做一个井字棋游戏！

```
create an interactive browser-based tic-tac-toe game in javascript where a player competes against a bot
```

goose 会制定一个计划，然后立即着手实现它。完成后，你的目录中应包含一个 JavaScript 文件以及一个用于游玩的 HTML 页面。

### 启用扩展

虽然你可以手动导航到工作目录并在浏览器中打开 HTML 文件，但如果 goose 能替你完成这件事不是更好吗？让我们通过启用 [`Computer Controller` 扩展](https://block.github.io/goose/docs/mcp/computer-controller-mcp)来赋予 goose 打开 Web 浏览器的能力。

<Tabs groupId="interface">

    <TabItem value="ui" label="goose Desktop" default>
        1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮以打开侧边栏。
        2. 点击侧边栏菜单中的 `Extensions`。
        3. 切换 `Computer Controller` 扩展以启用它。此扩展支持网页抓取、文件缓存和自动化。
        4. 返回你的会话以继续。
        5. 现在 goose 已具备浏览器能力，让我们让它在一个浏览器中启动你的游戏：
    </TabItem>
    <TabItem value="cli" label="goose CLI">
        1. 输入 `Ctrl+C` 结束当前会话，以便返回到终端的命令提示符。
        2. 运行配置命令

```sh
goose configure
```

        3. 选择 `Add Extension` > `Built-in Extension` > `Computer Controller`，并将超时设置为 300s。此扩展支持网页抓取、文件缓存和自动化。

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
        │  Computer Controller
        │
        ◇  Please set the timeout for this tool (in secs):
        │  300
        │
        └  Enabled computercontroller extension
```
        4. 现在 goose 已具备浏览器能力，让我们恢复你上次的会话：

```sh
 goose session -r
```

        5. 让 goose 在浏览器中启动你的游戏：
    </TabItem>
</Tabs>

```
open the tic-tac-toe game in a browser
```

去玩你的游戏吧，我知道你想玩 😂……祝你好运！

### 后续步骤

恭喜，你已成功使用 goose 开发了一个 Web 应用！🎉

以下是一些后续步骤的想法：
* 继续与 goose 进行会话，改进你的游戏（样式、功能等）。
* 浏览其他可用的[扩展](https://block.github.io/goose/extensions)并安装更多，以进一步增强 goose 的功能。
* 为 goose 提供一组[提示](https://block.github.io/goose/docs/guides/context-engineering/using-goosehints)，以便在你的会话中使用。
* 如果你不希望 goose 自主工作，了解如何设置[访问控制](https://block.github.io/goose/docs/mcp/developer-mcp#configuring-access-controls)。

---

## 安装 goose

> 原文：https://block.github.io/goose/docs/getting-started/installation

<Tabs>
  <TabItem value="mac" label="macOS" default>
    选择安装 goose 的桌面版和/或 CLI 版本：

    <Tabs groupId="interface">
      <TabItem value="ui" label="goose Desktop" default>
        直接从浏览器或使用 [Homebrew](https://brew.sh/) 安装 goose 桌面版。

        <h3 style={{ marginTop: '1rem' }}>选项 1：通过下载安装</h3>
        <MacDesktopInstallButtons/>

        <div style={{ marginTop: '1rem' }}>
          1. 解压下载的 zip 文件。
          2. 运行可执行文件以启动 goose 桌面版应用程序。

          :::tip 更新 goose
          最好定期[更新 goose](https://block.github.io/goose/docs/guides/updating-goose)。
          :::
        </div>
        <h3>选项 2：通过 Homebrew 安装</h3>
        Homebrew 下载的是[同一个应用](https://github.com/Homebrew/homebrew-cask/blob/master/Casks/b/block-goose.rb)，但还能负责更新。

```bash
brew install --cask block-goose
```
        ---
        <div style={{ marginTop: '1rem' }}>
          :::info 权限
          如果你使用的是 Apple Mac M3，并且 goose 桌面版应用在启动时不显示窗口，请检查并更新以下内容：

          确保 `~/.config` 目录具有读写权限。

          goose 需要此访问权限来创建日志目录和文件。授予权限后，应用应能正确加载。有关具体操作步骤，请参阅[已知问题指南](https://block.github.io/goose/docs/troubleshooting/known-issues#macos-permission-issues)。
          :::
        </div>
      </TabItem>
      <TabItem value="cli" label="goose CLI">
        直接从浏览器或使用 [Homebrew](https://brew.sh/) 安装 goose。

        <h3 style={{ marginTop: '1rem' }}>选项 1：通过下载脚本安装</h3>
        运行以下命令在 macOS 上安装最新版本的 goose：

```sh
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash
```
        此脚本将获取最新版本的 goose 并在你的系统上进行设置。

        如果你希望在不进行交互式配置的情况下安装，请禁用 `CONFIGURE`：

```sh
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | CONFIGURE=false bash
```

        :::tip 更新 goose
        最好保持 goose 更新。要更新 goose，请运行：

```sh
goose update
```
        :::

        <h3>选项 2：通过 Homebrew 安装</h3>
        Homebrew 下载的是[预编译的 CLI 工具](https://github.com/Homebrew/homebrew-core/blob/master/Formula/b/block-goose-cli.rb)，并且能负责更新。

```bash
brew install block-goose-cli
```
      </TabItem>
    </Tabs>
  </TabItem>

  <TabItem value="linux" label="Linux">
    选择安装 goose 的桌面版和/或 CLI 版本：

    <Tabs groupId="interface">
      <TabItem value="ui" label="goose Desktop" default>
        直接从浏览器安装 goose 桌面版。

        <h3 style={{ marginTop: '1rem' }}>通过下载安装</h3>
        <LinuxDesktopInstallButtons/>

        <div style={{ marginTop: '1rem' }}>
          **适用于基于 Debian/Ubuntu 的发行版：**
          1. 下载 DEB 文件
          2. 在终端中导航到该文件保存的目录
          3. 运行 `sudo dpkg -i (filename).deb`
          4. 从应用菜单启动 goose

          :::tip 更新 goose
          最好定期[更新 goose](https://block.github.io/goose/docs/guides/updating-goose)。
          :::
        </div>
      </TabItem>
      <TabItem value="cli" label="goose CLI">
        运行以下命令在 Linux 上安装 goose CLI：

```sh
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash
```
        此脚本将获取最新版本的 goose 并在你的系统上进行设置。

        如果你希望在不进行交互式配置的情况下安装，请禁用 `CONFIGURE`：

```sh
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | CONFIGURE=false bash
```

        :::tip 更新 goose
        最好保持 goose 更新。要更新 goose，请运行：

```sh
goose update
```
        :::
      </TabItem>
    </Tabs>
  </TabItem>

  <TabItem value="windows" label="Windows">
    选择安装 goose 的桌面版和/或 CLI 版本：

    <Tabs groupId="interface">
      <TabItem value="ui" label="goose Desktop" default>
        直接从浏览器安装 goose 桌面版。

        <h3 style={{ marginTop: '1rem' }}>通过下载安装</h3>
        <WindowsDesktopInstallButtons/>

        <div style={{ marginTop: '1rem' }}>
          1. 解压下载的 zip 文件。
          2. 运行可执行文件以启动 goose 桌面版应用程序。

          :::tip 更新 goose
          最好定期[更新 goose](https://block.github.io/goose/docs/guides/updating-goose)。
          :::
        </div>
      </TabItem>
      <TabItem value="cli" label="goose CLI">
        要在 Windows 上原生安装 goose，你需要以下环境之一：
        - **Git Bash**（推荐）：随 [Git for Windows](https://git-scm.com/download/win) 一起提供
        - **MSYS2**：可从 [msys2.org](https://www.msys2.org/) 获取
        - **PowerShell**：在 Windows 10/11 上默认可用

        **Git Bash / MSYS2：标准**

```bash
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash
```

        要在不进行交互式配置的情况下安装，请禁用 `CONFIGURE`：

```bash
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | CONFIGURE=false bash
```

        **PowerShell 安装：标准**
        将 PowerShell 安装脚本下载到你的当前目录。

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/aaif-goose/goose/main/download_cli.ps1" -OutFile "download_cli.ps1";
```
        然后运行该脚本以安装 goose：

```powershell
.\download_cli.ps1
```

        :::info Windows PATH 设置
        如果你看到 goose 不在你的 PATH 中的警告，你需要将 goose 添加到你的 PATH：

        <details>
          <summary>对于 Git Bash/MSYS2</summary>

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```
        </details>

        <details>
          <summary>对于 PowerShell</summary>

```powershell
# Add to your PowerShell profile
$profilePath = $PROFILE
if (!(Test-Path $profilePath)) { New-Item -Path $profilePath -ItemType File -Force }
Add-Content -Path $profilePath -Value '$env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"'
# Reload profile or restart PowerShell
. $PROFILE
```
        </details>

        更新 PATH 后，你可以在任意目录中运行 `goose` 命令。
        :::

        <details>
        <summary>通过适用于 Linux 的 Windows 子系统（WSL）安装</summary>

          我们建议在 Windows 上原生运行 goose CLI，但如果你更喜欢类似 Linux 的环境，也可以使用 WSL。

          1. 以管理员身份打开 [PowerShell](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-windows) 并安装 WSL 和默认的 Ubuntu 发行版：

```bash
wsl --install
```

          2. 如果出现提示，请重启计算机以完成 WSL 安装。重启后，或者如果 WSL 已安装，通过运行以下命令启动你的 Ubuntu shell：

```bash
wsl -d Ubuntu
```

          3. 运行 goose 安装脚本：

```bash
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash
```
          :::tip
            如果你在下载时遇到任何问题，可能需要安装 `bzip2` 来解压下载的文件：

```bash
sudo apt update && sudo apt install bzip2 -y
```
          :::

          如果你希望在不进行交互式配置的情况下安装，请禁用 `CONFIGURE`：

```sh
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | CONFIGURE=false bash
```

          如有需要，将 goose 添加到你的路径：

```
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo 'export OPENAI_API_KEY=your_api_key' >> ~/.bashrc
source ~/.bashrc
```

        </details>
      </TabItem>
    </Tabs>
  </TabItem>
</Tabs>

### 设置 LLM 提供方

goose 可与[受支持的 LLM 提供方][providers]配合使用，这些提供方为 goose 提供理解你的请求所需的 AI 智能。首次使用时，系统会提示你配置首选的提供方。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    首次打开 goose 时，在欢迎界面上选择如何配置提供方：
    <OnboardingProviderSetup />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    CLI 会自动进入配置模式，你可以在其中选择如何配置提供方：

    - **OpenRouter 登录** - 使用 OpenRouter 登录以自动配置模型
    - **Tetrate Agent Router Service 登录** - 使用 Tetrate Agent Router Service 登录以自动配置模型
    - **手动配置** - 选择一个提供方并手动输入凭据

    配置流程示例：

```
    ┌   goose-configure
    │
    ◇ How would you like to set up your provider?
    │ Tetrate Agent Router Service Login
    │
    Opening browser for Tetrate Agent Router Service authentication...
    [goose opens the browser and prints details]

    Authentication complete!

    Configuring Tetrate Agent Router Service...
    ✓ Tetrate Agent Router Service configuration complete
    ✓ Models configured successfully

    Testing configuration...
    ✓ Configuration test passed!
    ✓ Developer extension enabled!
    └ Tetrate Agent Router Service setup complete! You can now use goose.
```

  :::info Windows 用户
  如果你选择手动配置提供方，在配置过程中出现提示时，请选择不存储到密钥环。如果在设置 API 密钥时遇到密钥环错误，你可以改为手动设置环境变量：

```bash
export OPENAI_API_KEY={your_api_key}
```

  然后再次运行 `goose configure`。goose 会检测到该环境变量并显示：

```
  ● OPENAI_API_KEY is set via environment variable
```

  要使 API 密钥在会话之间持久保存，请将它们添加到你的 shell 配置文件中：

```bash
echo 'export OPENAI_API_KEY=your_api_key' >> ~/.bashrc
source ~/.bashrc
```
  :::
  </TabItem>
</Tabs>

:::tip
<ModelSelectionTip />
:::

:::info 免费额度优惠
当你首次通过 goose 自动使用 Tetrate 进行身份验证时，将获得 $10 免费额度。此优惠对新老 Tetrate 用户均可用。
:::

### 更新提供方

你可以随时更改 LLM 提供方和/或模型，或更新 API 密钥。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮以打开侧边栏。
    2. 点击侧边栏上的 `Settings` 按钮。
    3. 点击 `Models` 标签页。
    4. 选择更新你的提供方、切换模型，或点击 `Reset Provider and Model` 以清除你的设置并返回欢迎界面。有关这些[配置选项](https://block.github.io/goose/docs/getting-started/providers#configure-provider-and-model)的详细信息，请参阅相关文档。
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    1. 运行以下命令：

```sh
goose configure
```

    2. 从菜单中选择 `Configure Providers`。
    3. 按照提示选择你的 LLM 提供方，并输入或更新你的 API 密钥。

    **示例：**

    要在配置过程中选择一个选项，请使用上下箭头高亮你的选择，然后按 Enter。

```
    ┌   goose-configure
    │
    ◇ What would you like to configure?
    │ Configure Providers
    │
    ◇ Which model provider should we use?
    │ Google Gemini
    │
    ◇ Provider Google Gemini requires GOOGLE_API_KEY, please enter a value
    │▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
    │
    ◇ Enter a model from that provider:
    │ gemini-2.0-flash-exp
    │
    ◇  Hello there! You're all set to use me, so please ask away!
    │
    └  Configuration saved successfully
```
  </TabItem>
</Tabs>

<RateLimits />

### 运行 goose

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
        在 goose 桌面版中开始会话非常简单。选择提供方后，你会看到会话界面已准备好使用。

        将你的问题、任务或指令直接输入到输入框中，goose 会立即开始工作。
    </TabItem>
    <TabItem value="cli" label="goose CLI">
        在终端中，导航到你希望作为起点的目录并运行：

```sh
goose session
```
    </TabItem>
</Tabs>

### 共享配置设置

goose CLI 和桌面版 UI 共享所有核心配置，包括 LLM 提供方设置、模型选择和扩展配置。当你在任一界面中安装或配置扩展时，设置会存储在一个中心位置，使桌面版应用和 CLI 都能使用。这便于你在保持设置一致的同时在界面之间切换。有关更多信息，请访问[配置文件][config-files]指南。

:::info
虽然核心配置在界面之间共享，但扩展在存储身份验证凭据方面具有灵活性。有些扩展可能使用共享配置文件，而其他扩展则实现自己的存储方式。
:::

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
        通过以下方式导航到共享配置：
        1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮以打开侧边栏。
        2. 点击侧边栏上的 `Settings` 按钮。
    </TabItem>
    <TabItem value="cli" label="goose CLI">
        使用以下命令管理共享配置：

```sh
goose configure
```
    </TabItem>
</Tabs>

### 在 CI/CD 中固定 goose 版本

在 CI/CD（以及其他自动化的非交互式环境）中，使用 `GOOSE_VERSION` 固定特定版本，以使安装可复现，并在 `stable` 发布标签不包含 goose CLI 二进制资源时，避免下载时出现 404。

有关完整示例和用法详情，请参阅 [CI/CD 环境](https://block.github.io/goose/docs/tutorials/cicd)。

### 为 Linux 发行版生成 manpage

如果你正在为某个 Linux 发行版打包 goose 或创建自定义构建，你可以从 CLI 命令定义生成 Unix manpage：

```bash
just generate-manpages
```

这会在 `target/man/` 中创建 ROFF 格式的 manpage（例如 `goose.1`、`goose-session.1`），可以安装到 `/usr/share/man/man1/`，以通过 `man` 命令提供离线文档。

生成 manpage 需要 goose 源代码仓库，面向的是为 Fedora、Debian 及其他 Linux 发行版准备软件包的发行版打包者。有关实现细节，请参阅 [generate_manpages.rs 源码](https://github.com/aaif-goose/goose/blob/main/crates/goose-cli/src/bin/generate_manpages.rs)。

### 附加资源

你也可以配置扩展来扩展 goose 的功能，包括添加新的扩展或开启和关闭它们。有关详细说明，请访问[使用扩展指南][using-extensions]。

[using-extensions]: https://block.github.io/goose/docs/getting-started/using-extensions
[providers]: https://block.github.io/goose/docs/getting-started/providers
[handling-rate-limits]: https://block.github.io/goose/docs/guides/handling-llm-rate-limits-with-goose
[mcp]: https://www.anthropic.com/news/model-context-protocol
[config-files]: https://block.github.io/goose/docs/guides/config-files
