# goose 官方文档中文手册：第 32 章　仓库治理文档

## AGENTS 指南

> 原文：https://github.com/aaif-goose/goose/blob/main/AGENTS.md

goose 是一个用 Rust 编写的 AI agent 框架，带有 CLI 与 Electron 桌面界面。

### 贡献工作流

对于打算提交上游 pull request 的工作，issue 是唯一事实来源。请在 [Goose Issues 看板](https://github.com/orgs/aaif-goose/projects/1)上跟踪 issue 状态。

- 在为某个 pull request 实现某个 issue 之前，先确认它已在看板上且状态为 **Ready**。
- 不要实现处于 **Inbox**、**Needs info** 或 **Accepted / design** 状态的 issue。应改为帮助推进该 issue 的讨论。
- 在修改代码之前，先阅读已达成一致的设计、约束、非目标与验证方案。
- 让实现保持在该 issue 已达成一致的范围内。
- 如果实现过程中暴露出实质性的设计变更，先回到 issue 再继续。
- 每个外部 pull request 都必须链接它所实现的 Ready issue，并说明验证方案是如何执行的。
- 新 issue 应按照 `.github/ISSUE_TEMPLATE/` 中匹配的模板来组织，并设置 issue 类型（例如 Bug、Feature）。`gh issue create` 不会自动应用模板。

由维护者指派的工作、紧急安全修复、发布自动化，以及本地或探索性改动，都不需要 Ready issue。

### MCP 服务器目录

goose 正在淘汰其项目专属的 MCP 服务器目录，转而采用[官方 MCP Registry](https://github.com/modelcontextprotocol/registry)及其 `server.json` 格式。

- 不要再向 `documentation/static/servers.json` 添加新的第三方服务器；这类贡献不再被接受。
- 应引导服务器作者改为发布到官方 MCP Registry。
- 在基于 registry 的发现与安装实现完成之前，把现有的 goose 目录视为遗留数据。
- 在支持迁移且处于已批准 issue 范围内时，允许对现有目录条目进行维护、迁移或移除。

有关该决策与迁移方向，参见 [Discussion #10830](https://github.com/aaif-goose/goose/discussions/10830)。

### GitHub 沟通

撰写 issue 与 pull request 评论时，要面向人，而不是写成详尽的工作日志。

- 开头先给结论或需要采取的行动。
- 评论保持简洁；不要重复帖子里已经存在的上下文。
- 使用短段落或项目符号，只在影响决策或评审时才包含实现细节。
- 宁可给出一个清晰的总结，也不要发多条增量评论。

### 环境搭建
```bash
source bin/activate-hermit
cargo build
```

### 命令

#### 构建
```bash
cargo build                   # debug
cargo build --release         # release  
just release-binary           # release binary
```

#### 测试
```bash
export GOOSE_DISABLE_KEYRING=1  # avoid system keyring prompts
cargo test                   # all tests
cargo test -p goose          # specific crate
cargo test --package goose --test mcp_integration_test
just record-mcp-tests        # record MCP
```

#### Lint/格式化
```bash
cargo fmt
cargo clippy --all-targets -- -D warnings
```

#### UI
```bash
just run-ui                  # start desktop
cd ui/desktop && pnpm run typecheck
cd ui/desktop && pnpm test   # test UI
```

### 目录结构
```
crates/       # Rust workspace members — see root Cargo.toml (`members = ["crates/*"]`)
ui/desktop/   # Electron app
ui/text/      # deprecated ACP TUI (see ui/text/README.md)
```

部分 workspace crate（包括构成 GDK 的那些）会发布到 crates.io 并暴露公共 API。GDK crate 的权威清单是 `release-plz.toml` 中 `release = true`、`version_group = "gdk"` 的包集合，它驱动 GDK 的发布；运行 `python3 crates/goose-sdk/scripts/gdk-release.py crates` 可将其打印出来。其他 crate（例如 `goose` 和 `goose-cli`）不提供稳定的公共 API；它们的 `pub` 项属于内部实现细节，可能随时变更。

### 开发循环
```bash
# 1. source bin/activate-hermit
# 2. Make changes
# 3. cargo fmt
```

#### 仅在用户要求你构建/测试你的改动时才运行以下命令：
```
# 1. cargo build
# 2. GOOSE_DISABLE_KEYRING=1 cargo test -p <crate>
# 3. cargo clippy --all-targets -- -D warnings
```

### 规则

- 测试：优先使用 tests/ 目录，例如 crates/goose/tests/
- 测试：新增功能时，更新 goose-self-test.yaml，重新构建，然后运行 `goose run --recipe goose-self-test.yaml` 进行验证
- 错误：使用 anyhow::Result
- 提供方：实现 Provider trait，参见 providers/base.rs
- MCP：扩展位于 crates/goose-mcp/
- UI 桌面版：使用 ACP SDK 类型或本地 `src/types/*` 类型。不要从 `ui/desktop/src/api` 导入生成的 OpenAPI 类型/客户端代码

### 代码质量

- 注释：写自解释的代码——优先用清晰的命名而非注释
- 注释：绝不添加只是复述代码行为的注释
- 注释：只在复杂算法、不易理解的业务逻辑，或需要说明「为什么」而非「是什么」时才写注释
- 简洁：不要给本不需要可选的东西加上可选性——编译器会强制执行
- 简洁：布尔值应默认为 false，而不是做成可选
- 错误：不要添加无助于提供有用信息的错误上下文（例如当错误本身已经表明失败时，还写 `.context("Failed to X")`）
- 简洁：避免过度防御性的代码——相信 Rust 的类型系统
- 日志：清理已有日志，除非用于错误或安全事件，否则不要新增

### 绝不

- 绝不：重建 `ui/desktop/src/api`，或在 `ui/desktop` 中添加 `@hey-api/openapi-ts`
- Cargo.toml：对于人工编写的依赖变更，使用 `cargo add` 而不是手动编辑依赖条目，除非有特定理由不这么做。
- Cargo.toml：自动化依赖升级 PR 不受此限；必须手动编辑时，保持 `Cargo.lock` 一致。
- 绝不：跳过 cargo fmt
- 绝不：不运行 clippy 就合并
- 绝不：为不言自明的操作（`// Initialize`、`// Return result`）、getter/setter、构造函数或标准 Rust 惯用法写注释
- 绝不：就地覆盖正在运行的二进制文件（例如用 `cp`/`fs.copyFileSync` 覆盖已有的可执行文件）——应先 unlink 或原子重命名目标文件，否则 macOS 会以「Code Signature Invalid」SIGKILL 正在运行的进程

### 入口点
- CLI：crates/goose-cli/src/main.rs
- UI：ui/desktop/src/main.ts
- Agent：crates/goose/src/agents/agent.rs

---

## 使用 Docker 构建并运行 goose

> 原文：https://github.com/aaif-goose/goose/blob/main/BUILDING_DOCKER.md

本指南介绍如何为生产使用、CI/CD 流水线以及本地开发构建 goose CLI 的 Docker 镜像。

### 快速开始

#### 使用预构建镜像

用 Docker 运行 goose 最简单的方式是从 GitHub Container Registry 拉取预构建镜像：

```bash
# Pull the latest image
docker pull ghcr.io/aaif-goose/goose:latest

# Run goose CLI
docker run --rm ghcr.io/aaif-goose/goose:latest --version

# Run with LLM configuration
docker run --rm \
  -e GOOSE_PROVIDER=openai \
  -e GOOSE_MODEL=gpt-4o \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  ghcr.io/aaif-goose/goose:latest run -t "Hello, world!"
```

### 从源码构建

#### 前置条件

- Docker 20.10 或更高版本
- Docker Buildx（用于多平台构建）
- Git

#### 构建镜像

1. 克隆仓库：
```bash
git clone https://github.com/aaif-goose/goose.git
cd goose
```

2. 构建 Docker 镜像：
```bash
docker build -t goose:local .
```

构建过程：
- 使用多阶段构建以最小化最终镜像体积
- 带优化编译（LTO、剥离符号、体积优化）
- 生成约 340MB 的镜像，其中包含 `goose` CLI 二进制文件

#### 构建选项

用于带调试符号的开发构建：
```bash
docker build --build-arg CARGO_PROFILE_RELEASE_STRIP=false -t goose:dev .
```

用于多平台构建：
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t goose:multi .
```

### 在 Docker 中运行 goose

#### CLI 模式

基本用法：
```bash
# Show help
docker run --rm goose:local --help

# Run a command
docker run --rm \
  -e GOOSE_PROVIDER=openai \
  -e GOOSE_MODEL=gpt-4o \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  goose:local run -t "Explain Docker containers"
```

挂载卷以访问文件：
```bash
docker run --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  -e GOOSE_PROVIDER=openai \
  -e GOOSE_MODEL=gpt-4o \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  goose:local run -t "Analyze the code in this directory"
```

使用 Databricks 的交互式会话模式：
```bash
docker run -it --rm \
  -e GOOSE_PROVIDER=databricks \
  -e GOOSE_MODEL=databricks-dbrx-instruct \
  -e DATABRICKS_HOST="$DATABRICKS_HOST" \
  -e DATABRICKS_TOKEN="$DATABRICKS_TOKEN" \
  goose:local session
```



#### Docker Compose

创建一个 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  goose:
    image: ghcr.io/aaif-goose/goose:latest
    environment:
      - GOOSE_PROVIDER=${GOOSE_PROVIDER:-openai}
      - GOOSE_MODEL=${GOOSE_MODEL:-gpt-4o}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./workspace:/workspace
      - goose-config:/home/goose/.config/goose
    working_dir: /workspace
    stdin_open: true
    tty: true

volumes:
  goose-config:
```

用以下命令运行：
```bash
docker-compose run --rm goose session
```

### 配置

#### 环境变量

该 Docker 镜像接受所有标准的 goose 环境变量：

- `GOOSE_PROVIDER`：LLM 提供方（openai、anthropic、google 等）
- `GOOSE_MODEL`：要使用的模型（gpt-4o、claude-sonnet-4 等）
- 提供方专属的 API key（OPENAI_API_KEY、ANTHROPIC_API_KEY 等）

#### 持久化配置

挂载配置目录以持久化设置：
```bash
docker run --rm \
  -v ~/.config/goose:/home/goose/.config/goose \
  goose:local configure
```

#### 安装额外工具

该镜像默认以非 root 用户运行。要安装额外的软件包：

```bash
# Run as root to install packages
docker run --rm \
  -u root \
  --entrypoint bash \
  goose:local \
  -c "apt-get update && apt-get install -y vim && goose --version"

# Or create a custom Dockerfile
FROM ghcr.io/aaif-goose/goose:latest
USER root
RUN apt-get update && apt-get install -y \
    vim \
    tmux \
    && rm -rf /var/lib/apt/lists/*
USER goose
```

### CI/CD 集成

#### GitHub Actions

```yaml
jobs:
  analyze:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/aaif-goose/goose:latest
      env:
        GOOSE_PROVIDER: openai
        GOOSE_MODEL: gpt-4o
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    steps:
      - uses: actions/checkout@v4
      - name: Run goose analysis
        run: |
          goose run -t "Review this codebase for security issues"
```

#### GitLab CI

```yaml
analyze:
  image: ghcr.io/aaif-goose/goose:latest
  variables:
    GOOSE_PROVIDER: openai
    GOOSE_MODEL: gpt-4o
  script:
    - goose run -t "Generate documentation for this project"
```

### 镜像详情

#### 体积与优化

- **基础镜像**：Debian Bookworm Slim（最小化的运行时依赖）
- **最终体积**：约 340MB
- **优化**：链接时优化（LTO）、二进制剥离、体积优化
- **包含的二进制文件**：`/usr/local/bin/goose`（32MB）

#### 安全性

- 以非 root 用户 `goose`（UID 1000）运行
- 只保留必要的运行时依赖，攻击面最小
- 通过自动化构建定期进行安全更新

#### 包含的工具

该镜像包含 goose 运行所需的必要工具：
- `git` —— 版本控制操作
- `curl` —— HTTP 请求
- `ca-certificates` —— SSL/TLS 支持
- 基本的 shell 工具

### 故障排查

#### 权限问题

如果挂载卷时遇到权限错误：
```bash
# Ensure the mounted directory is accessible
docker run --rm \
  -v $(pwd):/workspace \
  -u $(id -u):$(id -g) \
  goose:local run -t "List files"
```

#### API Key 问题

如果 API key 未被识别：
1. 确保环境变量已正确设置
2. 检查 shell 中引号的处理是否正确
3. 使用 `docker run --env-file .env` 传入多个环境变量

#### 网络问题

要从容器内访问本地服务：
```bash
# Use host network mode
docker run --rm --network host goose:local
```

### 进阶用法

#### 自定义 Entrypoint

覆盖默认 entrypoint 以便调试：
```bash
docker run --rm -it --entrypoint bash goose:local
```

#### 资源限制

设置内存与 CPU 限制：
```bash
docker run --rm \
  --memory="2g" \
  --cpus="2" \
  goose:local
```

#### 多阶段开发

用于支持热重载的开发：
```bash
# Mount source code
docker run --rm \
  -v $(pwd):/usr/src/goose \
  -w /usr/src/goose \
  rust:1.82-bookworm \
  cargo watch -x run
```

### 为生产环境构建

用于生产部署：

1. 使用具体的镜像标签而不是 `latest`
2. 使用密钥管理来存放 API key
3. 设置日志与监控
4. 配置资源限制与自动扩缩容

生产环境 Dockerfile 示例：
```dockerfile
FROM ghcr.io/aaif-goose/goose:v1.6.0
# Add any additional tools needed for your use case
USER root
RUN apt-get update && apt-get install -y your-tools && rm -rf /var/lib/apt/lists/*
USER goose
```

### 贡献

在贡献与 Docker 相关的改动时：

1. 在多个平台（amd64、arm64）上测试构建
2. 确认镜像体积保持合理
3. 更新本文档
4. 考虑对 CI/CD 的影响
5. 用各种 LLM 提供方进行测试

### 相关文档

- [goose in Docker 教程](https://github.com/aaif-goose/goose/blob/main/documentation/docs/tutorials/goose-in-docker.md) —— 分步教程
- [安装指南](https://goose-docs.ai/docs/getting-started/installation) —— 所有安装方式
- [配置指南](https://goose-docs.ai/docs/guides/config-files) —— 详细的配置选项

---

## 在 Linux 上构建 goose 桌面版

> 原文：https://github.com/aaif-goose/goose/blob/main/BUILDING_LINUX.md

本指南介绍如何在各种 Linux 发行版上从源码构建 goose 桌面版应用。

### 前置条件

#### 系统依赖

**Debian/Ubuntu：**
```bash
sudo apt update
sudo apt install -y dpkg fakeroot build-essential clang libxcb1-dev libxcb-util-dev protobuf-compiler libvulkan-dev libvulkan1 glslc
```

**Arch/Manjaro：**
```bash
sudo pacman -S --needed dpkg fakeroot base-devel vulkan-headers vulkan-icd-loader shaderc
```

**Fedora/RHEL/CentOS：**
```bash
sudo dnf install dpkg-dev fakeroot gcc gcc-c++ make libxcb-devel vulkan-headers vulkan-loader glslc
```

**openSUSE：**
```bash
sudo zypper install dpkg fakeroot gcc gcc-c++ make vulkan-headers vulkan-loader glslc
```

**Android / Termux：**

`download_cli.sh` 安装脚本会检测 Termux，并自动选择 musl 可移植构建（`GOOSE_LINUX_VARIANT=musl`）。安装方法：

```bash
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash
```

在 Termux 中从源码构建：

```bash
pkg install rust cmake protobuf clang build-essential
cargo build --release -p goose-cli --bin goose --no-default-features --features portable-default
```

> **注意：** musl/可移植构建会禁用 `local-inference`（V8）和 `system-keyring`（D-Bus SecretService），因为两者在 Android 上都不可用。

原始 PR：https://github.com/aaif-goose/goose/pull/3890

#### 开发工具

- **Rust**：通过 [rustup](https://rustup.rs/) 安装
- **Node.js**：22.9.0 或更高版本（使用 [nvm](https://github.com/nvm-sh/nvm) 管理版本）
- **pnpm**：10 或更高版本（通过 Hermit 管理，或全局安装）
- **just**：安装 Rust 后通过 `cargo install just` 安装。更多[信息](https://github.com/casey/just#packages)

### 构建流程

#### 1. 克隆并设置
```bash
git clone https://github.com/aaif-goose/goose.git
cd goose
```

#### 2. 构建

构建 Goose CLI：

```bash
cargo build --release -p goose-cli --bin goose
```

该命令应该会列出 workspace 中可用的包：

```bash
cargo test -p
```

#### 3. 准备桌面应用
```bash
cd ui/desktop
pnpm install

# Copy the goose binary to the expected location
mkdir -p src/bin
cp ../../target/release/goose src/bin/
```

#### 4. 构建应用

##### 选项 A：ZIP 发行包（推荐）
适用于所有 Linux 发行版：
```bash
pnpm run make --targets=@electron-forge/maker-zip
```

输出：`out/make/zip/linux/x64/goose-linux-x64-{version}.zip`

##### 选项 B：DEB 包
适用于 Debian/Ubuntu 系统：
```bash
pnpm run make --targets=@electron-forge/maker-deb
```

输出：`out/make/deb/x64/goose_{version}_amd64.deb`

##### 选项 C：两种格式都要
```bash
pnpm run make
```

#### 5. 运行应用

##### 从构建目录运行
```bash
./out/goose-linux-x64/goose
```

##### 安装 DEB 包（如果构建了的话）
```bash
sudo dpkg -i out/make/deb/x64/goose_*.deb
```

### 故障排查

#### 常见问题

##### 缺少系统依赖
如果你看到关于缺少 `dpkg`、`fakeroot`、Vulkan 头文件或 `glslc` 的错误：
```bash
# Install the missing packages for your distribution (see Prerequisites above)
```

##### GLib 警告
你可能会看到类似这样的警告：
```
GLib-GObject: instance has no handler with id
```
这些警告无害，不影响功能。要抑制它们，可以创建一个启动脚本：

```bash
#!/bin/bash
cd /path/to/goose/ui/desktop/out/goose-linux-x64
./goose 2>&1 | grep -v "GLib-GObject" | grep -v "browser_main_loop"
```

##### 找不到 Goose 二进制文件
如果你看到「Goose binary not found」，请确认你已经：
1. 构建了 Rust 二进制文件：`cargo build --release -p goose-cli --bin goose`
2. 把它复制到了正确位置：`cp ../../target/release/goose src/bin/`
3. 重新构建了应用：`pnpm run make`

#### 发行版专属说明

##### Arch/Manjaro
- RPM maker 默认被禁用，因为它与基于 Arch 的系统不兼容
- 使用 ZIP 发行方式以获得最大兼容性

##### Flatpak
Flatpak 构建通过 CI 支持。要在本地构建：
```bash
# Install flatpak and flatpak-builder
sudo apt install flatpak flatpak-builder

# Add Flathub remote
flatpak remote-add --if-not-exists --user flathub https://dl.flathub.org/repo/flathub.flatpakrepo

# Build with Electron Forge
pnpm run make --targets=@electron-forge/maker-flatpak
```

输出：`out/make/flatpak/x86_64/*.flatpak`

##### Snap
目前不支持构建 Snap 包，但未来可能会加入。

### 开发工作流

用于积极开发时：

1. **后端改动**：用 `cargo build --release -p goose-cli --bin goose` 重新构建并复制二进制文件
2. **前端改动**：开发期间使用 `pnpm run start` 进行热重载
3. **完整重建**：运行上面的完整构建流程

### 创建系统集成

#### 桌面入口
创建 `~/.local/share/applications/goose.desktop`：
```ini
[Desktop Entry]
Name=goose AI Agent
Comment=Local AI agent for development tasks
Exec=/path/to/goose/ui/desktop/out/goose-linux-x64/goose %U
Icon=/path/to/goose/ui/desktop/out/goose-linux-x64/resources/app.asar.unpacked/src/images/icon.png
Terminal=false
Type=Application
Categories=Development;Utility;
StartupNotify=true
MimeType=x-scheme-handler/goose
```

#### 全系统安装
要全系统安装：
```bash
sudo cp -r out/goose-linux-x64 /opt/goose
sudo ln -s /opt/goose/goose /usr/local/bin/goose-gui
```

### 贡献

在贡献影响 Linux 构建流程的改动时，请：

1. 尽可能在多个发行版上测试
2. 更新本文档
3. 如有需要，更新 `ui/desktop/README.md`
4. 考虑对自动化构建的 CI/CD 影响

---

## Claude 配置

> 原文：https://github.com/aaif-goose/goose/blob/main/CLAUDE.md

@AGENTS.md

---

## 行为准则

> 原文：https://github.com/aaif-goose/goose/blob/main/CODE_OF_CONDUCT.md

### Contributor Covenant 3.0 行为准则

### 我们的承诺

我们承诺让我们的社区对所有人都是欢迎、安全且公平的。

我们致力于营造一个尊重并促进所有个体尊严、权利与贡献的环境，无论其特征如何，包括种族、族裔、种姓、肤色、年龄、身体特征、神经多样性、残障、性别或社会性别、性别认同或表达、性取向、语言、哲学或宗教、民族或社会出身、社会经济地位、教育水平或其他身份。凡是本着善意并遵守本准则参与的人，都享有同样的参与特权。

### 鼓励的行为

在承认社会规范存在差异的同时，我们都努力达到社区对积极行为的期望。我们也理解，由于文化、背景或母语的不同，我们的言语和行为可能被解读得与我们的本意不同。

考虑到这些因素，我们同意以体贴的方式彼此相待，并以聚焦我们共同价值观的方式行事，包括：

1. 尊重**我们社区的目的**、我们的活动以及我们的聚会方式。
2. 与他人**友善而诚实地**互动。
3. 尊重**不同的观点**与经验。
4. 对自身的行为与贡献**承担责任**。
5. 优雅地给予和接受**建设性反馈**。
6. 承诺在伤害发生时**修复伤害**。
7. 以其他促进并维系**我们社区福祉**的方式行事。


### 受限制的行为

我们同意在我们的社区中限制以下行为。这些行为的实例、威胁与宣扬都违反本行为准则。

1. **骚扰。** 违反明确表达的界限，或在对方明确要求停止后仍进行不必要的个人关注。
2. **人身攻击。** 针对社区成员或群体发表侮辱性、贬低性或轻蔑的言论。
3. **刻板印象或歧视。** 基于不可改变的身份或特征来刻画任何人的性格或行为。
4. **性化。** 以在社区语境或目的下通常会被认为是不恰当亲密的方式行事。
5. **侵犯保密性**。未经许可分享或利用他人的个人或私密信息。
6. **危害。** 对任何个人或群体造成、鼓励或威胁暴力或其他伤害。
7. 以其他**威胁我们社区福祉**的方式行事。

#### 其他限制

1. **误导性身份。** 出于任何原因冒充他人，或假装成他人以逃避执法措施。
2. **未标明出处。** 未恰当标明你所贡献内容的来源。
3. **宣传材料**。以超出社区规范的方式分享营销或其他商业内容。
4. **不负责任的沟通。** 未能负责任地呈现包含、链接或描述任何其他受限制行为的内容。


### 报告问题

即使在社区成员尽力协作时，成员之间也可能出现紧张关系。并非每一次冲突都构成违反行为准则，而本行为准则强化了那些有助于避免冲突、减少伤害的鼓励行为与规范。

当事件确实发生时，及时报告很重要。要报告可能的违规行为，**请发送消息给 @goose-admin**

社区版主会认真对待违规报告，并尽一切努力及时响应。他们会调查所有违反行为准则的报告，审查消息、日志与录音，或访谈目击者与其他参与者。社区版主会在优先考虑安全与保密的同时，尽可能让调查与执法行动保持透明。为了尊重这些价值，执法行动会与相关方私下进行，但向整个社区沟通也可能是双方商定的解决方案的一部分。


### 处理与修复伤害

如果社区版主的调查认定本行为准则已被违反，可根据事件对相关个人及整个社区的影响，使用以下执法阶梯来确定如何最好地修复伤害。根据违规的严重程度，可以跳过阶梯中较低的层级。

1) 警告
   1) 事件：涉及单次事件或一系列事件的违规。
   2) 后果：由社区版主发出私下的书面警告。
   3) 修复：修复的示例包括私下书面道歉、承认责任，以及就期望寻求澄清。
2) 临时限制活动
   1) 事件：此前已导致警告的违规行为再次发生，或更严重违规行为的首次发生。
   2) 后果：一份私下书面警告，附带限时的冷静期，旨在强调情况的严重性，并让相关社区成员有时间消化该事件。冷静期可能仅限于特定沟通渠道或与特定社区成员的互动。
   3) 修复：修复的示例可能包括道歉、利用冷静期反思行为与影响，以及在冷静期结束后慎重考虑如何重新进入社区空间。
3) 暂时封禁
   1) 事件：社区版主已尝试用警告处理的一连串反复违规，或单次严重违规。
   2) 后果：一份私下书面警告，附带解除封禁的条件。一般而言，暂时封禁让被封禁者有时间反思自身行为与可能的纠正措施。
   3) 修复：修复的示例包括尊重封禁的精神、满足指定的解除条件，以及在封禁解除后慎重考虑如何重新融入社区。
4) 永久封禁
   1) 事件：阶梯上其他步骤都未能解决的一连串反复违反行为准则的行为，或严重到社区版主认定无法在让此人为成员的情况下保持社区安全的违规。
   2) 后果：移除对所有社区空间、工具与沟通渠道的访问权限。一般而言，永久封禁应极少使用，应有充分的理由支撑，并且只有在通过其他补救措施仍未能改变行为时才应诉诸。
   3) 修复：在这种严重程度下不存在可能的修复。

该执法阶梯旨在作为指引。它不限制社区管理者本着我们社区最佳利益行使自己的酌情权与判断力。


### 适用范围

本行为准则适用于所有社区空间，也适用于个人在公共或其他空间中正式代表社区时。代表我们社区的示例包括使用官方电子邮件地址、通过官方社交媒体账号发帖，或在线上或线下活动中担任指定代表。


### 归属

本行为准则改编自 Contributor Covenant 3.0 版，永久可访问于 [https://www.contributor-covenant.org/version/3/0/](https://www.contributor-covenant.org/version/3/0/)。

Contributor Covenant 由 Organization for Ethical Source 管理，并以 CC BY-SA 4.0 授权。要查看该许可证的副本，请访问 [https://creativecommons.org/licenses/by-sa/4.0/](https://creativecommons.org/licenses/by-sa/4.0/)

有关 Contributor Covenant 常见问题的解答，请参见 [https://www.contributor-covenant.org/faq](https://www.contributor-covenant.org/faq) 上的 FAQ。译文见 [https://www.contributor-covenant.org/translations](https://www.contributor-covenant.org/translations)。更多执法与社区指引资源见 [https://www.contributor-covenant.org/resources](https://www.contributor-covenant.org/resources)。该执法阶梯的灵感来自 [Mozilla 行为准则团队](https://github.com/mozilla/inclusion)的工作。
---

## 贡献指南

> 原文：https://github.com/aaif-goose/goose/blob/main/CONTRIBUTING.md

goose 是开源的，而代码只是贡献的一种方式。报告问题、复现问题、分享领域知识、参与塑造设计、实现解决方案，以及验证结果，都是有价值的工作。

我们在公开的 [Goose Issues 看板](https://github.com/orgs/aaif-goose/projects/1)上组织这些工作。从最初的报告到设计、实现与验证，issue 是贡献的主要记录。

> [!TIP]
> 除了代码，也看看[其他贡献方式](#other-ways-to-contribute)

---

### Issue 工作流

每个未关闭的 issue 都在 [Goose Issues 看板](https://github.com/orgs/aaif-goose/projects/1)上跟踪：

- **Inbox**：该 issue 正在等待分类。
- **Needs info**：在 issue 能够推进之前还需要更多信息。
- **Accepted / design**：我们想要解决这个问题，正在梳理设计、约束与验证方案。
- **Ready**：预期方案已确定，可以开始实现。
- **In progress**：实现正在进行中。
- **Verification**：实现已就绪，等待人工确认它确实可用。
- **Done**：结果已经过验证，issue 已关闭。

我们不打算推进的 issue 会附带说明被关闭。我们不使用拒绝标签。

功能请求应当描述一个具有广泛用途的问题，而不只是偏好的实现方式。增加功能很容易；维护它们却是长期成本，因此我们可能会拒绝那些增加了复杂度但没有足够普遍收益的功能。

Discord 与 GitHub Discussions 仍然适合非正式交流，但影响实现的决策应记录在 issue 中。

### 如何贡献

如果你发现 bug 或想要新功能，[开一个 issue](https://github.com/aaif-goose/goose/issues/new/choose)。一个好的 issue 会说明问题是什么、影响谁、以及为什么重要。对于 bug，请尽可能包含清晰的复现步骤与诊断报告。
请自己撰写 issue。你的 agent 可以做调研并帮你探索，但你应当理解这个 issue。你可以
提出一个解决方向，但不要给出详细的解决方案，尤其是代码。

最好的贡献位置是 **Accepted / design** 与 **Ready** 之间的讨论。工程就在这里发生：把一个值得解决的问题转化为 agent 可以实现的具体方案。通过带来上下文与领域知识、挑战假设、比较不同方案、识别约束与权衡，并就结果将如何验证达成一致，来参与 issue 讨论。

在任何阶段做出实质贡献的人都可以被认定为共同作者。贡献的单位是把问题带到已验证的解决方案，而不是写出补丁。

### LLM 提供方集成

如果你运营一个使用 OpenAI、Anthropic 或 Ollama 兼容 API 的 LLM 服务，支持 goose 用户的最佳方式通常是发布一个 goose 自定义提供方 JSON 文件，并附上你自己的文档。用户可以下载该文件到本地的 `custom_providers` 目录并选择该提供方，而无需等待 goose 发版。

有关 JSON 格式与安装位置，参见[自定义提供方配置](https://github.com/aaif-goose/goose/blob/main/documentation/docs/getting-started/providers.md#configure-custom-provider)。请包含清晰的设置说明，涵盖凭据、支持的模型、流式支持，以及你的服务所需的任何自定义请求头。不要在 JSON 文件中包含真实的 API key、token、租户密钥或其他凭据。

为自定义 LLM 提供方开的 issue 只会偶尔作为例外被接受。支持 goose 用户的最佳方式是提供一个有文档的提供方配置，让用户自行安装。

### 从 Issue 到 Pull Request

在 issue 于 Goose Issues 看板上达到 **Ready** 之前，不要开始实现或开 pull request。

每个外部 pull request 都必须：

- 链接它所实现的 Ready issue；
- 保持在 issue 中已达成一致的设计与范围内；
- 说明该 issue 的验证方案是如何执行的；并且
- 把实质性的设计变更带回 issue 讨论。

没有实现 Ready issue 的 pull request 会被关闭。自动化依赖与发布 pull request、紧急安全修复，以及核心团队明确指派的工作除外。

不要接连快速地开很多 pull request。按优先级顺序提交，等它们落地后再开新的。

### AI 代码评审

我们使用 codex 作为 AI 代码评审员。AI 代码评审已经发展了很久，而且大多数情况下能指出真实的问题。因此我们期望你处理所有这些问题，要么修复代码，要么加一行说明为什么这不是问题或不值得修复。

如果不是这样，我们可能会关闭该 PR 和/或回复一个指向本节的链接。一旦你处理了这些评论，随时可以重新打开。

### 负责任地使用 AI 的快速提示

没有必要告诉我们你在工作中使用了 AI。你正在为一个 agent 做贡献，如果你没用才奇怪。
我们的总体想法是，你可以随意使用 AI，但在机器人革命到来之前，你要对最终代码负责。在提交
PR 供评审之前，确保你自己已经审阅过它。我们会关闭任何明显跳过这一步的 vibe coding 提交。

只要你坚持这一原则，你可以使用任何 agent 和任何方法论。当然，我们希望你喜欢 goose 并使用它。
有一件事需要留意，就是 LLM 的急躁。它们喜欢讨好别人，而且很着急。

   * **先思考**。Agent 倾向于直接跳到写代码。先根据你自己对代码的理解说明你想要的架构，以
      避免这种行为，或者让 agent 先探索代码并提出方案。如果第一个实现看起来不太对，就直接
      重来，用你学到的东西下次做得更好。
   * **发现偷懒**。LLM 会让自己的工作变简单。它们会写毫无价值的测试，把类型放宽并设为可选
      以免编译器抱怨，捕获异常后只是记录日志而不处理错误，并且不论是否合适都照抄本地模式。
      要顶回去！
   * **发现不确定性**。尽管这些机器人会宣称「我现在清楚地看到了问题」，它们往往并没有。如果
      你看到 agent 在胡乱挣扎，就点破它。另一个明显的迹象是，agent 开始列举它用多少种方式修
      复了问题，或者开始写过度防御性的代码。
   * **发现臃肿**。Agent 喜欢插入冗余的注释，或者更糟——评论当前的改动而不是最终的代码。它们
      会创建一大堆实际上什么都没测的测试，即使测了，测的也是实现而不是意图。它们还喜欢什么都
      记日志，以防万一。

### 前置条件

goose 在 GUI 的 electron 应用之外还包含 Rust 二进制文件。

我们使用 [Hermit][hermit] 管理开发依赖（Rust、Node、pnpm、just 等）。
进入项目时激活 Hermit：

```bash
source bin/activate-hermit
```

或者添加 [shell hook 自动激活](https://cashapp.github.io/hermit/usage/shell/#shell-hooks)，让 Hermit 在你 `cd` 进入项目时自动激活（推荐）。

我们在 `justfile` 中用 [just][just] 为常用命令提供了快捷方式。

#### 适用于 Linux 的 Windows 子系统

对于 WSL 用户，你可能需要安装 `build-essential` 和 `libxcb`，否则可能会遇到 `cc` 链接错误（cc 代表 C Compiler）。
运行以下命令来安装：

```
sudo apt update                   # Refreshes package list (no installs yet)
sudo apt install build-essential  # build-essential is a package that installs all core tools
sudo apt install libxcb1-dev      # libxcb1-dev is the development package for the X C Binding (XCB) library on Linux
```

### 开发环境搭建

#### Rust

先编译 goose 并试用一下。
由于 goose 需要 Hermit 来管理依赖，让我们先激活 hermit。

```
cd goose
source ./bin/activate-hermit
cargo build
```

完成后，就可以使用各二进制文件的 debug 构建了，包括 goose CLI：

```
./target/debug/goose --help
```

首次设置时，运行 configure 命令：

```
./target/debug/goose configure
```

一旦与某个 LLM 提供方的连接可用，就启动一个会话：

```
./target/debug/goose session
```

这些相同的命令可以用 `cargo run -p goose-cli` 重新编译并立即运行，以便迭代。
在修改 Rust 代码时，在 CLI 上测试它们，或运行检查、测试与 linter：

```
cargo check  # verify changes compile
cargo test   # run tests with changes
cargo fmt    # format code
cargo clippy --all-targets -- -D warnings # run the linter
```

#### Node

要运行应用：

```
just run-ui
```

该命令会构建 Rust 的 release 构建（等价于 `cargo build -r`）并启动 Electron 进程。
应用会打开一个窗口并显示首次设置。完成设置后，goose 就可以使用了。

在 `ui/desktop` 中进行 GUI 改动。

##### 故障排查：`just run-ui` 出现空白屏幕

如果应用打开后是空白窗口（日志显示 `Cannot read properties of null (reading 'useRef')`），说明你的 `node_modules` 已过期，加载了两份 React。删除它并重新安装：

```
rm -rf ui/desktop/node_modules
cd ui && pnpm install
```

参见 #8757。

#### 调试

要调试外部 ACP 后端，可以从 IDE 中运行它。配置取决于 IDE。要运行的命令是：

```
export GOOSE_SERVER__SECRET_KEY=test
cargo run --package goose-cli --bin goose -- serve --platform desktop --enable-scheduler --host 127.0.0.1 --port 3000
```

`debug-ui` recipe 默认连接到 `http://127.0.0.1:3000`。如果
后端使用了另一个端口，在启动 UI 时设置 `GOOSE_PORT`，或者把
`GOOSE_EXTERNAL_BACKEND_URL` 设置为后端的 HTTP 基础 URL。

后端运行起来后，启动一个 UI 并将其连接到后端，运行：

```
just debug-ui
```

UI 会连接到在 IDE 中启动的后端，从而让你在与 UI 交互的同时使用断点
并单步调试后端代码。

### 创建 fork

要 fork 该仓库：

1. 访问 https://github.com/aaif-goose/goose 并点击「Fork」（右上角）。
2. 这会在你的 GitHub 账号下创建 https://github.com/<your-username>/goose。
3. 克隆你的 fork（不是主仓库）：

```
git clone https://github.com/<your-username>/goose.git
cd goose
```

4. 把主仓库添加为 upstream：

```
git remote add upstream https://github.com/aaif-goose/goose.git
```

5. 在你的 fork 中为你的改动创建一个分支：

```
git checkout -b my-feature-branch
```

6. 将你的 fork 与主仓库同步：

```
git fetch upstream

# Merge them into your local branch (e.g., 'main' or 'my-feature-branch')
git checkout main
git merge upstream/main
```

7. 推送到你的 fork。由于你是该 fork 的所有者，你有权限推送到这里。

```
git push origin my-feature-branch
```

8. 从你 fork 上的分支向 aaif-goose/goose 的 main 分支开一个 Pull Request。

### 保持你的 Fork 最新

为确保你的贡献能顺利集成，让你的 fork 与主
仓库保持同步很重要。这有助于避免冲突，也让我们能更快地合并你的 pull request。以下是如何同步你的 fork：

#### 将你的 Fork 与主仓库同步

1. **把主仓库添加为 Remote**（如果已经设置过就跳过）：

   ```bash
   git remote add upstream https://github.com/aaif-goose/goose.git
   ```

2. **从主仓库拉取最新改动**：

   ```bash
   git fetch upstream
   ```

3. **检出你的开发分支**：

   ```bash
   git checkout your-branch-name
   ```

4. **把主分支的改动合并进你的分支**：

   ```bash
   git merge upstream/main
   ```

   解决出现的任何冲突并提交改动。

5. **把合并后的改动推送到你的 Fork**：

   ```bash
   git push origin your-branch-name
   ```

这个过程会帮你让分支与主仓库中持续发生的改动保持一致，在需要合并时最大限度减少集成问题！

#### 提交 Pull Request 之前

在你提交 pull request 之前，请确保你的 fork 已按上述方式同步。这项检查能确保你的改动与主仓库中的最新内容兼容，并让评审流程更顺畅。

如果你在这个过程中遇到任何问题或有任何疑问，请通过[开一个 issue][issues]联系我们，我们很乐意帮忙。

### 环境变量

作为开发者，你可能想更频繁地改动提供方设置或类似配置来测试效果。
你可以使用环境变量在不重做配置的情况下即时改变设置。

> [!TIP]
> 目前我们仍在更新部分 CLI 配置，以确保这一点得到
> 遵循。

你可以通过 `GOOSE_PROVIDER` 环境变量改变 goose 指向的提供方。如果你此前设置时已经在该提供方的钥匙串中存有凭据，它应该会被复用。对于自动化之类的场景，或想在不做正式设置的情况下测试，你也可以为该提供方设置相关的环境变量。例如 `ANTHROPIC_API_KEY`、`OPENAI_API_KEY`，或 `DATABRICKS_HOST`。有关所需密钥的更多信息，请参阅提供方详情。

#### 隔离测试环境

在测试改动或运行多个 goose 配置时，使用 `GOOSE_PATH_ROOT` 隔离你的数据：

```bash
# Test with a clean environment
export GOOSE_PATH_ROOT="/tmp/goose-test"
./target/debug/goose session

# Or for a single command
GOOSE_PATH_ROOT="/tmp/goose-dev" cargo run -p goose-cli -- session
```

这会在指定路径下创建隔离的 `config/`、`data/` 和 `state/` 目录，防止你的测试会话影响你主要的 goose 安装。更多细节参见[环境变量指南](https://github.com/aaif-goose/goose/blob/main/documentation/docs/guides/environment-variables.md#development--testing)。

### 使用[本地托管的 Langfuse](https://langfuse.com/docs/deployment/self-host)在 goose 中启用 trace

- [按文档启动一个本地 Langfuse](https://langfuse.com/self-hosting/docker-compose)。创建一个组织与项目，并创建 API 凭据。
- 设置环境变量，让 goose 能连接到 langfuse 服务器：

```
export LANGFUSE_INIT_PROJECT_PUBLIC_KEY=publickey-local
export LANGFUSE_INIT_PROJECT_SECRET_KEY=secretkey-local
```

然后你可以在 http://localhost:3000 查看你的 trace

### 约定式提交

本项目在 PR 标题上遵循[约定式提交（Conventional Commits）](https://www.conventionalcommits.org/en/v1.0.0/)规范。约定式提交让项目历史更易理解，也便于围绕版本管理与变更日志生成做自动化。

[issues]: https://github.com/aaif-goose/goose/issues
[hermit]: https://cashapp.github.io/hermit/
[just]: https://github.com/casey/just?tab=readme-ov-file#installation

### 其他贡献方式

成为开源贡献者、为 goose 做贡献的方式有很多。我们乐意在这条路上帮助你！以下是一些入门建议。如果你有任何疑问或需要帮助，欢迎在 [Discord](https://discord.gg/n8R5VaWDAn) 上联系我们。

- **在 GitHub 上加星：** 如果你认同我们的项目并觉得它有价值，考虑在 GitHub 上给我们的 goose 加星！🌟
- **提问：** 你的问题不仅帮助我们改进，也让社区受益。如果你有疑问，尽管在 [Discord](https://discord.gg/n8R5VaWDAn) 上提出。
- **给出反馈：** 有想要的功能，或在使用 goose 时遇到问题，[点此开一个 issue](https://github.com/aaif-goose/goose/issues/new/choose)、[发起一个讨论](https://github.com/aaif-goose/goose/discussions)，或在 Discord 上告诉我们。
- **参与社区活动：** 我们每月在 Discord 上举办各种社区活动与直播，从工作坊到头脑风暴会都有。你可以订阅我们的[活动日历](https://calget.com/c/t7jszrie)，或在[社交媒体](https://linktr.ee/goose_oss)上关注我们以保持联系。
- **改进文档：** 好的文档是任何项目成功的关键。你可以帮助改进我们现有文档的质量，或添加新页面。
- **帮助其他成员：** 看到另一位社区成员卡住了？或者有贡献者被一个你知道答案的问题挡住了？回复社区帖子，或为他人做代码评审来帮忙。
- **展示你的作品：** 最近在做某个项目或写了篇博客？在我们的 [#share-your-work](https://discord.com/channels/1287729918100246654/1287729920797179958) 频道与社区分享。
- **表达赞赏：** 有某个你喜爱的项目，或有某个社区/工作人员特别有帮助？欢迎在我们的 [#general](https://discord.com/channels/1287729918100246654/1287729920797179957) 频道向他们表达赞赏。
- **传播出去：** 通过分享 goose 的项目、网站、YouTube 和/或 Twitter/X，帮助我们触达更多人。

---

## goose 技术治理与监管

> 原文：https://github.com/aaif-goose/goose/blob/main/GOVERNANCE.md

了解 goose 的治理结构以及如何参与

goose 遵循一种轻量的技术治理模型，旨在支持快速迭代的同时保持社区参与。本文档概述项目如何组织以及决策如何做出。

### 核心价值观
goose 的治理以三项基本价值为指导：

* **开放**：goose 是开源的，但我们不止于代码可用。我们在公开环境下规划与构建。我们的路线图以及 goose recipe、扩展与提示词都是可编辑、可分享的。我们的目标是让 goose 成为最可被改造（hackable）的 agent。
* **灵活**：我们偏好开放模型——但我们不限制自己。goose 同样支持远程部署的前沿模型以及本地私有模型，无论是开放的还是专有的。
* **选择**：我们不受任何单一模型、协议或技术栈的束缚。goose 为选择与开放标准而生，适应你作为创造者的工具、工作流与身份。

### 角色

#### 贡献者

社区中任何通过 issue、pull request 或讨论为 goose 做贡献的人。各种形式的社区贡献，从代码与 bug 报告到功能请求与讨论参与，都有助于确保 goose 朝着服务真实用户需求的方向演进，并与人们实际使用项目的方式保持一致。

#### 维护者

维护者是受信任的社区成员，负责 goose 的关键组件。他们评审 pull request、引导贡献者，并确保其领域内的技术与社区健康。

##### 职责

* 推动其组件领域内的持续改进。
* 评审贡献并维持质量。
* 培育社区参与。
* 在需要时，向核心维护者提出战略性或架构性的决策。

维护者拥有在仓库上创建分支的写入权限，但没有完整的管理权限。

#### 核心维护者

核心维护者对 goose 有广泛的技术理解，并负责项目的整体方向、技术一致性与长期愿景。

##### 职责

* 设定 goose 的整体技术方向与愿景
* 定义并维护 goose 的技术方向与原则。
* 解决由维护者上报的争议。
* 任命与罢免维护者。
* 确保创新与稳定之间的平衡。
* 以开放社区的最佳利益为准则监管 goose。

核心维护者在所有仓库上都拥有管理员权限，但为了透明，他们使用标准的贡献工作流（例如 pull request）。

### 决策流程

#### 日常决策

* 大多数技术与流程决策通过 pull request、GitHub 讨论或 Discord 中的共识做出。
* 当有明确收益时，核心维护者可以快速批准并合并改动。
* 重大的架构性改动应在实现前先在 GitHub issue 或 discussion 中讨论。
* 当出现争议或决策具有项目级影响时，核心维护者可以介入。

#### 争议解决

* 如果维护者无法达成共识，该事项会上报给核心维护者。
* 核心维护者以通过讨论达成共识为目标。
* 如果在合理讨论后仍未解决，核心维护者可以举行简单多数投票来解决该问题。
* 所有争议解决结果都应在 GitHub 与 Discord 上公开宣布。

该流程在实现及时决策的同时确保公平与透明。

#### 僵局

如果上述流程中出现决策僵局，goose 的创造者 Bradley Axen 会作为打破僵局者介入，以解除僵局并推动进展。

#### 重大变更

重大的架构或方向性变更应：

1. 作为 GitHub issue 或 discussion 提出。
2. 经过至少一周的开放社区评审。
3. 获得多数核心维护者的批准。
4. 在 GitHub 与 Discord 上公开宣布。

### 维护者的选拔与罢免

#### 原则

* 成员资格基于功绩，与个人贡献挂钩，而非雇主归属。
* 没有任期限制，但不活跃可能导致转为荣誉（emeritus）身份。
* 所有任命与罢免都以透明方式进行。

#### 维护者提名流程

1. 由任何现任维护者或核心维护者提名，依据：
   * 持续、高质量的贡献。
   * 在评审与讨论中的建设性参与。
   * 与项目价值观的一致性。
2. 在所有核心维护者之间讨论。
3. 多数投票通过。
4. 在 GitHub 与 Discord 上公开宣布。

#### 核心维护者的任命

我们的目标是在任何时候都保持 3 到 7 名核心维护者。我们力求核心维护者人数为奇数，以尽量减少投票僵局的可能性，但候选人的技术卓越程度优先于严格遵循人数。

1. 由任何现任核心维护者提名，依据：
   * 成为维护者所需的一切条件
   * 展现出的领导力与判断力。
   * 对项目价值观的长期承诺
2. 在所有核心维护者之间讨论。
3. 多数投票通过。
4. 在 GitHub 与 Discord 上公开宣布。

#### 罢免

维护者或核心维护者可能在以下情况下被罢免：

* 连续 3 个月以上无贡献的长期不活跃。
* 与项目价值观相悖的行为。
* 本人主动请求。

罢免决定需要核心维护者的多数投票，并且必须公开记录。可以附带理由向核心维护者提出申诉。

#### 继任规划

如果某位核心维护者因任何原因离开：

* 其余核心维护者应在 30 天内任命一名替代者。
* 如果核心维护者人数降至三人以下，任命新核心维护者就成为优先事项，且必须在 15 天内完成任命。在任命新的核心维护者之前，不会做出任何重大决策。
* 如果没有愿意担任核心维护者的合格开发者，其余核心维护者应改为制定并采纳一项招募与培养新核心维护者的计划。
* 在任命替代者之前，其余核心维护者继续承担治理职责

### 沟通

#### 渠道

* **GitHub**：issue、pull request 与文档的权威归属地。
* **Discord**：用于实时协作与非正式讨论。

#### 透明度

* 所有技术决策与治理讨论都应公开进行。
* 会议记录与关键决策在 GitHub 上公开发布。
* 路线图与优先级在 GitHub 上公开讨论并发布。
* 所有治理相关的提案与改动都必须通过 pull request 记录。

### 工作实践

#### 代码评审

##### 遵循我们的工作方式

* 仔细评审 AI 生成的工作：检查冗余注释、价值很低甚至为负的测试、过时的模式，以及重复的代码。
* 评审要分清优先级：别人在等，但也要花时间理解改动。
* 避免「挑人评审」：向熟悉所修改代码的人寻求评审。
* 充分测试：对于较大的功能，手动与自动化 E2E 测试至关重要；UI 改动请附上截图或视频。

##### 贡献

* 先讨论：对于新功能或架构性改动，先开 issue 或 discussion。
* 让 PR 保持聚焦：更小、更聚焦的改动更容易评审与合并。
* 写有意义的测试：测试应防范真实的 bug，而不只是提高覆盖率。
* 参与社区：所有维护者都应活跃于 Discord 与 GitHub，并对其他贡献者保持响应。

##### 发布流程

* 定期发布，并清晰记录交付的功能。
* 在需要时，快速的 bug 修复或安全问题的解决会被 cherry-pick 到补丁发布中。
* 所有发布在公布前都由多位核心维护者或维护者测试。

### 治理变更

该治理模型可能随着 goose 的成长而演进。对本文件的任何修改提案都必须：

1. 通过 GitHub issue 附带理由提出。
2. 经过至少一周的开放社区讨论。
3. 获得多数核心维护者的批准。
4. 向社区清晰沟通变更。
5. 通过对 goose 主仓库中 GOVERNANCE.md 文件的 pull request 实施。

### 现任成员

核心维护者与维护者列在 goose 主仓库的 [MAINTAINERS.md](https://github.com/aaif-goose/goose/blob/main/MAINTAINERS.md) 文件中，并酌情标注其专业领域。

### 小结

#### goose 的治理优先考虑

* **速度**：以最少的流程支持快速试验
* **开放**：透明的决策与社区参与
* **自主**：赋能用户与贡献者去塑造 goose
* **质量**：深思熟虑的评审，同时避免官僚作风

我们相信这种平衡能让 goose 保持创新，同时围绕创造最可被改造、最由用户掌控的 agent 这一共同目标，构建一个强大且投入的社区。

### 一般项目政策

goose 由 Block 创立，现由 AAIF（Agentic AI Foundation）监管，已确立为 Series of LF Projects, LLC 的一个项目。适用于 goose 以及 goose 项目参与者的政策，包括商标使用指南，位于 [https://lfprojects.org/policies/](https://lfprojects.org/policies/)。按本治理文件条款批准的治理变更也必须获得 LF Projects, LLC 的批准。

goose 参与者承认，所有新贡献中的版权将作为独立的著作由版权持有者保留，且任何贡献者或版权持有者都不需要向项目转让版权。
除下文所述外，对项目的所有代码与规范贡献都必须使用位于（「项目许可证」）处的 Apache License, Version 2.0 进行。

所有出站的代码与规范都将在项目许可证下提供。核心维护者可以例外地批准对入站或出站贡献使用替代的开放许可证。
所有文档（规范除外）都将在 Creative Commons Attribution 4.0 International 许可证下提供，地址为：https://creativecommons.org/licenses/by/4.0。
---

## goose 自定义发行版

> 原文：https://github.com/aaif-goose/goose/blob/main/CUSTOM_DISTROS.md

> **提示：** 这有时被称为「white labelling」——为你的组织创建一个品牌化或定制化的开源项目版本。

本指南介绍如何创建针对你组织需求量身定制的 goose 自定义发行版——无论是预配置的模型、自定义工具、品牌化界面，还是全新的用户体验。

### 概览

goose 的架构为可扩展性而设计。组织可以创建「重混（remixed）」版本，这些版本能够：

- **预配置 AI 提供方**：随附特定模型（本地或云端）与 API 凭据
- **捆绑自定义工具**：包含用于内部数据源的专有扩展
- **定制体验**：修改品牌、UI 与默认行为
- **面向特定人群**：为开发者、法务团队、设计师等创建专门版本

### 架构一览

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interfaces                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  CLI        │  │  Desktop    │  │  Your Custom UI         │  │
│  │  (goose-cli)│  │  (Electron) │  │  (web, mobile, etc.)    │  │
│  └──────┬──────┘  └──────┬──────┘  └────────────┬────────────┘  │
└─────────┼────────────────┼──────────────────────┼───────────────┘
          │                │                      │
          ▼                ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    goose serve (ACP)                            │
│         ACP HTTP/WebSocket server for custom clients            │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Core (goose crate)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Providers  │  │  Extensions │  │  Config & Recipes       │  │
│  │  (AI models)│  │  (MCP tools)│  │  (behavior & defaults)  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 关键定制点

| 你想要什么 | 到哪里找 | 复杂度 |
|---------------|---------------|------------|
| 预配置模型/提供方 | `config.yaml`、`init-config.yaml`、环境变量 | 低 |
| 添加自定义 AI 提供方 | `crates/goose/src/providers/declarative/` | 低 |
| 捆绑自定义 MCP 扩展 | `config.yaml` 的 extensions 段、`ui/desktop/src/built-in-extensions.json`、`ui/desktop/src/components/settings/extensions/bundled-extensions.json` | 中 |
| 修改系统提示词 | `crates/goose/src/prompts/` | 低 |
| 定制桌面版品牌 | `ui/desktop/`（图标、名称、颜色） | 中 |
| 构建新 UI（web、mobile） | 通过 ACP 与 `goose serve` 集成 | 高 |
| 创建引导式工作流 | Recipe（基于 YAML 的任务定义） | 低 |
| 构建复杂的多步工作流 | 带子 Recipe 与子代理的 Recipe | 中 |

### 快速开始

#### 1. Fork 并克隆

```bash
git clone https://github.com/YOUR_ORG/goose.git
cd goose
```

#### 2. 选择你的定制策略

- **仅配置**：修改配置文件与环境变量（不改代码）
- **基于扩展**：为你的工具添加自定义 MCP 服务器（对核心改动最小）
- **深度定制**：修改核心行为、UI，或添加新的提供方

#### 3. 构建并分发

平台专属的构建说明参见 [BUILDING_LINUX.md](https://github.com/aaif-goose/goose/blob/main/BUILDING_LINUX.md) 与 [ui/desktop/README.md](https://github.com/aaif-goose/goose/blob/main/ui/desktop/README.md)。

### 重要注意事项

#### 许可证

goose 以 Apache License 2.0（ASL v2）授权。自定义发行版必须：
- 包含原始许可证与版权声明
- 清楚标明所做的任何修改
- 不得以暗示获得官方认可的方式使用「Goose」商标

关于 ASL v2 合规的详细指引，参见 [Apache License FAQ](https://www.apache.org/foundation/license-faq.html)。

#### 回馈上游

虽然你可以自由维护私有 fork，但把改进贡献回上游对所有人都有益——包括你的发行版。严重分叉的私有 fork 维护成本高昂，并且会错过安全更新与新功能。考虑把通用改进贡献回上游，只把组织专属的定制保持为私有。

#### 遥测

goose 包含可选的遥测（通过 PostHog），以帮助改进项目。对于自定义发行版，你可以：
- **禁用遥测**：设置 `GOOSE_DISABLE_TELEMETRY=1`
- **使用你自己的实例**：修改 `crates/goose/src/posthog.rs` 以指向你的 PostHog 实例

#### 保持最新

要从上游改进中获益：
1. 定期将你的 fork 与主仓库同步
2. 尽可能让定制保持隔离（配置文件、独立的扩展仓库）
3. 用 recipe 做工作流定制，而不是改动代码
4. 订阅发布公告以了解破坏性变更

---

### 附录：自定义发行版场景

### A. 预配置本地模型的发行版

**目标**：发布预配置为使用本地 Ollama 模型的 goose，无需任何 API key。

#### 步骤

1. **在你的发行版根目录创建一个 init-config.yaml**：

```yaml
# init-config.yaml - Applied on first run if no config exists
GOOSE_PROVIDER: ollama
GOOSE_MODEL: qwen3-coder:latest
```

2. **在你的启动脚本或打包中设置环境默认值**：

```bash
export GOOSE_PROVIDER=ollama
export GOOSE_MODEL=qwen3-coder:latest
export OLLAMA_HOST=http://localhost:11434  # Or your hosted instance
```

3. **可选：在 UI 中隐藏提供方选择**，通过修改 `ui/desktop/src/` 中的组件实现。

#### 技术细节

- 提供方配置：`crates/goose/src/config/base.rs`
- Ollama 提供方实现：`crates/goose/src/providers/ollama.rs`
- 配置优先级：环境变量 → config.yaml → 默认值

---

### B. 带托管 API Key 的企业发行版

**目标**：在企业内部发行预先配置好前沿模型 API key 的 goose。

#### 步骤

1. **使用 goose 的密钥管理安全存储 API key**：

```yaml
# config.yaml (distributed with your package)
GOOSE_PROVIDER: anthropic
GOOSE_MODEL: claude-sonnet-4-20250514
```

2. **在安装时或通过你的 MDM/配置管理注入密钥**：

```bash
# Secrets are stored in system keyring or ~/.config/goose/secrets.yaml
# if GOOSE_DISABLE_KEYRING=1
goose configure set-secret ANTHROPIC_API_KEY "your-corporate-key"
```

3. **（可选）锁定提供方变更**，通过修改设置 UI 或使用一个强制该提供方的 recipe 实现。

#### 技术细节

- 密钥存储：`crates/goose/src/config/base.rs`（SecretStorage 枚举）
- 钥匙串集成：默认使用系统钥匙串，可回退到基于文件的存储
- 配置文件位置：`~/.config/goose/config.yaml`

---

### C. 面向内部数据源的自定义工具

**目标**：添加连接到你的数据湖、内部 API 或专有系统的 MCP 扩展。

#### 步骤

1. **按照 [MCP 规范](https://modelcontextprotocol.io/)创建你的 MCP 服务器**：

```python
# Example: internal_data_mcp.py
from mcp.server import Server
from mcp.types import Tool

server = Server("internal-data")

@server.tool()
async def query_data_lake(query: str) -> str:
    """Query the corporate data lake."""
    # Your implementation here
    return results
```

2. **作为内置扩展捆绑**，添加到以下任一处：
   - `ui/desktop/src/built-in-extensions.json`（在扩展 UI 中呈现的核心内置扩展）
   - `ui/desktop/src/components/settings/extensions/bundled-extensions.json`（设置中捆绑的扩展目录）

示例：

```json
{
  "id": "internal-data",
  "name": "Internal Data Lake",
  "description": "Query corporate data sources",
  "enabled": true,
  "type": "stdio",
  "cmd": "python",
  "args": ["/path/to/internal_data_mcp.py"],
  "env_keys": ["INTERNAL_DATA_API_KEY"],
  "timeout": 300
}
```

3. **或者作为一个启用该扩展的 recipe 分发**：

```yaml
# data-analyst.yaml
title: Data Analyst Assistant
description: goose configured for data analysis
instructions: |
  You have access to the corporate data lake. Help users query and analyze data.
extensions:
  - type: stdio
    name: internal-data
    cmd: python
    args: ["/opt/corp-goose/internal_data_mcp.py"]
    description: Corporate data lake access
```

#### 技术细节

- 扩展类型：`crates/goose/src/agents/extension.rs`（ExtensionConfig 枚举）
- 内置 MCP 服务器：`crates/goose-mcp/`
- 扩展加载：`crates/goose/src/agents/extension_manager.rs`

---

### D. 自定义品牌与 UI

**目标**：用你组织的形象重塑桌面应用。

#### 步骤

1. **替换 `ui/desktop/src/images/` 中的视觉资源**：
   - `icon.png`、`icon.ico`、`icon.icns` —— 应用图标
   - 按需更新启动画面与 logo

2. **修改 `ui/desktop/forge.config.ts` 中的应用元数据**：

```typescript
// forge.config.ts
module.exports = {
  packagerConfig: {
    name: 'YourCompany AI Assistant',
    executableName: 'yourcompany-ai',
    icon: 'src/images/your-icon',
    // ...
  },
  // ...
};
```

3. **更新系统提示词**以体现你的品牌，位于 `crates/goose/src/prompts/system.md`：

```markdown
You are an AI assistant called [YourName], created by [YourCompany].
...
```

4. **定制 UI 组件**，位于 `ui/desktop/src/`（React/TypeScript）：
   - CSS/Tailwind 配置中的配色方案
   - 组件文案与标签
   - 功能可见性

5. **重塑品牌时对齐打包与更新器名称**：
   - 更新 `ui/desktop/package.json` 中的静态品牌元数据（`productName`、description）以及 Linux 桌面模板（`ui/desktop/forge.deb.desktop`、`ui/desktop/forge.rpm.desktop`）

   - 一致地设置构建/发布环境变量：
     - `GITHUB_OWNER` 与 `GITHUB_REPO`，用于发布者与更新器仓库查找
     - `GOOSE_BUNDLE_NAME`，用于 bundle/调试脚本与更新器资源命名（默认为 `Goose`）

示例：

```bash
export GITHUB_OWNER="your-org"
export GITHUB_REPO="your-goose-fork"
export GOOSE_BUNDLE_NAME="InsightStream-goose"
```

6. **发布前使用这份品牌一致性检查清单**：
   - 应用元数据（`forge.config.ts`、`package.json`、`index.html`）使用你的发行版名称
   - 发布产物名称与更新器查找名称保持一致
   - 桌面启动器（Linux `.desktop` 模板）指向打包产出的同一个可执行文件名

#### 技术细节

- Electron 配置：`ui/desktop/forge.config.ts`
- UI 入口点：`ui/desktop/src/renderer.tsx`
- 系统提示词：`crates/goose/src/prompts/`

---

### E. 构建新界面（Web、移动端等）

**目标**：在利用 goose 后端的同时创建一个全新的前端。

goose 提供两种 ACP 传输方式用于构建自定义客户端：

#### 选项 1：ACP HTTP/WebSocket（`goose serve`）

对于进程分离的集成，例如 web 应用、桌面外壳与其他客户端，使用 `goose serve`：

```bash
# Start the server
GOOSE_SERVER__SECRET_KEY='a-long-random-secret' goose serve

# ACP endpoint available at http://localhost:3284/acp
```

HTTP 客户端使用 `X-Secret-Key` 请求头进行认证。浏览器 WebSocket 客户端把同一个密钥作为 `?token=` 查询参数使用，因为浏览器的 WebSocket API 无法设置自定义请求头：

```text
ws://localhost:3284/acp?token=a-long-random-secret
```

对于从非回环（non-loopback）源提供的浏览器客户端，用 `--allowed-origin` 传入确切的 UI 源。当你传入 `--allowed-origin` 时，它会替换默认的回环源白名单，所以要包含客户端需要的每一个源。

关于 ACP 协议与客户端流程，参见[把 goose 用作 ACP agent](https://github.com/aaif-goose/goose/blob/main/documentation/docs/gdk/acp/index.md)。

#### 选项 2：基于 stdio 的 Agent Client Protocol（ACP）

对于更丰富的本地集成（IDE 与嵌入式 agent），将 goose 作为基于 stdio 的 ACP agent 运行。

ACP 提供：
- **双向通信**：Agent 可以请求权限、流式推送更新，并接收取消
- **丰富的工具调用处理**：每次工具调用的详细状态更新、位置与内容
- **会话管理**：创建、加载并恢复带完整对话历史的会话
- **MCP 服务器集成**：动态向会话中添加 MCP 服务器

**将 goose 作为 ACP agent 启动**：

```bash
# Run goose as an ACP server on stdio
goose acp --with-builtin developer,memory

# Or programmatically
cargo run -p goose-cli -- acp --with-builtin developer
```

**关键 ACP 方法**：

| 方法 | 说明 |
|--------|-------------|
| `initialize` | 建立连接并交换能力 |
| `session/new` | 创建一个带可选 MCP 服务器的新会话 |
| `session/load` | 按 ID 恢复已有会话 |
| `session/prompt` | 发送提示词并接收流式响应 |
| `session/cancel` | 取消进行中的提示词 |

**示例：Python ACP 客户端**（完整示例参见 `test_acp_client.py`）：

```python
import subprocess
import json

class AcpClient:
    def __init__(self):
        self.process = subprocess.Popen(
            ['goose', 'acp', '--with-builtin', 'developer'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
    
    def send_request(self, method, params=None):
        request = {"jsonrpc": "2.0", "method": method, "id": 1}
        if params:
            request["params"] = params
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        return json.loads(self.process.stdout.readline())

# Initialize and create session
client = AcpClient()
client.send_request("initialize", {"protocolVersion": "2025-01-01"})
session = client.send_request("session/new", {"cwd": "/path/to/project"})

# Send a prompt (responses stream as notifications)
client.send_request("session/prompt", {
    "sessionId": session["result"]["sessionId"],
    "prompt": [{"type": "text", "text": "List files in this directory"}]
})
```

**ACP 通知**（由 agent 发送给客户端）：
- 带 `agentMessageChunk` 的 `session/notification` —— 流式文本响应
- 带 `toolCall` 的 `session/notification` —— 工具调用已开始
- 带 `toolCallUpdate` 的 `session/notification` —— 工具状态/结果更新
- `requestPermission` —— Agent 就敏感操作请求用户确认

完整的 ACP 规范参见 [Agent Client Protocol 文档](https://github.com/anthropics/anthropic-cookbook/tree/main/misc/agent_client_protocol)。

#### 技术细节

**ACP**：
- ACP 服务器实现：`crates/goose/src/acp/server.rs`
- CLI 集成：`crates/goose-cli/src/cli.rs`（Command::Acp）
- 协议库：`agent-client-protocol` crate（ACP 的 Rust 实现）
- 测试客户端示例：`test_acp_client.py`

---

### F. 面向特定人群的发行版（法务、设计等）

**目标**：为特定专业人群创建一个量身定制的 goose 版本。

#### 步骤

1. **创建一个定义体验的专用 recipe**：

```yaml
# legal-assistant.yaml
title: Legal Research Assistant
description: AI assistant for legal professionals

instructions: |
  You are a legal research assistant. You help lawyers and paralegals with:
  - Case law research
  - Document review and summarization
  - Contract analysis
  - Legal writing assistance
  
  Always cite sources. Flag when you're uncertain. Never provide actual legal advice.

extensions:
  - type: builtin
    name: developer
    description: File and document tools
  - type: stdio
    name: legal-database
    cmd: python
    args: ["/opt/legal-goose/legal_db_mcp.py"]
    description: Legal database search

activities:
  - "Research case law on..."
  - "Summarize this contract..."
  - "Find precedents for..."

settings:
  goose_provider: anthropic
  goose_model: claude-sonnet-4-20250514
```

2. **定制 UI**，只显示相关的功能，并使用符合该领域的语言。

3. **捆绑领域专属扩展**，用于专门的数据源（法律数据库、设计工具等）。

#### 技术细节

- Recipe 格式：`crates/goose/src/recipe/mod.rs`
- Recipe 加载：`crates/goose/src/recipe/local_recipes.rs`
- 活动建议：在 UI 中作为快速开始提示词显示

---

### G. 添加自定义 AI 提供方

**目标**：添加对新的 AI 提供方或你的自托管模型端点的支持。

#### 选项 1：声明式提供方（无需代码）

在 `~/.config/goose/custom_providers/` 中创建一个 JSON 文件，或捆绑在你的发行版中：

```json
{
  "name": "my_provider",
  "engine": "openai",
  "display_name": "My Custom Provider",
  "description": "Our internal LLM endpoint",
  "api_key_env": "MY_PROVIDER_API_KEY",
  "base_url": "https://llm.internal.company.com/v1/chat/completions",
  "models": [
    {
      "name": "company-llm-v1",
      "context_limit": 32768
    }
  ],
  "supports_streaming": true,
  "requires_auth": true
}
```

支持的引擎：`openai`、`anthropic`、`ollama`

#### 选项 2：自定义提供方（代码）

对于具有独特 API 的提供方，实现 Provider trait：

1. 在 `crates/goose/src/providers/` 中创建一个新文件
2. 实现 `base.rs` 中的 `Provider` trait
3. 在 `crates/goose/src/providers/factory.rs` 中注册

#### 技术细节

- 声明式提供方：`crates/goose/src/config/declarative_providers.rs`
- Provider trait：`crates/goose/src/providers/base.rs`
- 提供方注册：`crates/goose/src/providers/factory.rs`
- 提供方示例：`crates/goose/src/providers/declarative/*.json`

---

### H. 用 Recipe 预配置工作流

**目标**：创建标准化、可重复的工作流，让用户以最少的设置即可运行。

Recipe 是定义完整 goose 体验的 YAML 文件——把指令、扩展、参数与提示词捆绑在一起。它们非常适合自定义发行版，因为无需改动代码，并且可以作为简单的文件分发。

#### 基本 Recipe 结构

```yaml
version: 1.0.0
title: Daily Standup Report Generator
description: Generates standup reports from GitHub activity

# Parameters users can customize at runtime
parameters:
  - key: github_repo
    input_type: string
    requirement: required
    description: "GitHub repository (e.g., 'owner/repo')"
  
  - key: time_period
    input_type: select
    requirement: optional
    default: "24h"
    options: ["24h", "48h", "week"]
    description: "Time period to analyze"

# System instructions for the AI
instructions: |
  You are a standup report generator. Fetch PR and issue data from GitHub,
  analyze activity, and generate a formatted report.
  
  Always save reports to ./standup/standup-{date}.md

# Extensions this recipe needs
extensions:
  - type: builtin
    name: developer
    description: File operations
  - type: stdio
    name: github
    cmd: uvx
    args: ["github-mcp-server"]
    description: GitHub API access

# Quick-start suggestions shown in UI
activities:
  - "Generate today's standup report"
  - "Summarize this week's PRs"

# Initial prompt with parameter substitution
prompt: |
  Generate a standup report for {{ github_repo }} covering the last {{ time_period }}.
```

#### Recipe 参数类型

| 类型 | 说明 | 使用场景 |
|------|-------------|----------|
| `string` | 自由文本输入 | 名称、路径、查询 |
| `number` | 数值输入 | 计数、上限 |
| `boolean` | 真/假开关 | 功能开关 |
| `date` | 日期选择器 | 基于时间的筛选 |
| `file` | 文件路径（导入内容） | 文档处理 |
| `select` | 从选项中下拉选择 | 预定义的选项 |

#### 分发 Recipe

1. **随你的发行版捆绑**在已知位置
2. **通过 URL 分享**——用户可以从 URL 导入 recipe
3. **创建 recipe 库**——一个面向不同使用场景的 recipe 目录

#### 技术细节

- Recipe schema：`crates/goose/src/recipe/mod.rs`
- 参数处理：`crates/goose/src/recipe/template_recipe.rs`
- Recipe 校验：`crates/goose/src/recipe/validate_recipe.rs`

---

### I. 带子 Recipe 与子代理的复杂工作流

**目标**：构建编排多个专门任务的高级多步工作流。

对于复杂工作流，goose 支持两种强大的组合机制：

1. **子 Recipe**：可按名称调用的预定义 recipe 模板
2. **子代理**：为处理特定任务而派生的独立 AI agent

#### 子 Recipe：预定义的任务模板

子 Recipe 让你定义可复用的工作流组件，供主 recipe 调用：

```yaml
version: 1.0.0
title: Implementation Planner
description: Creates detailed implementation plans with research

instructions: |
  Create implementation plans through research and iteration.
  Use sub-recipes to delegate specialized research tasks.

# Define available sub-recipes
sub_recipes:
  - name: "find_files"
    path: "./subrecipes/codebase-locator.yaml"
    description: "Locate relevant files in the codebase"
  
  - name: "analyze_code"
    path: "./subrecipes/code-analyzer.yaml"
    description: "Analyze code structure and patterns"
  
  - name: "find_patterns"
    path: "./subrecipes/pattern-finder.yaml"
    # Pre-fill some parameters
    values:
      search_depth: "3"
      include_tests: "true"

extensions:
  - type: builtin
    name: developer

prompt: |
  Create an implementation plan for the requested feature.
  
  Use the available sub-recipes to research the codebase:
  - find_files: Locate relevant source files
  - analyze_code: Understand current implementation  
  - find_patterns: Find similar features to model after
```

定义了 `sub_recipes` 的 recipe 会自动获得 Summon 扩展。AI 可以通过 Summon 的 `delegate` 工具调用子 Recipe：

```
delegate(source: "find_files", parameters: {"search_term": "authentication"})
```

#### 子代理：动态任务委派

子代理是拥有自己上下文的独立 AI 实例。它们适用于：

- **并行执行**：多个任务同时运行
- **上下文隔离**：防止上下文窗口溢出
- **专门任务**：每个任务使用不同的模型/设置

##### 临时子代理

用自定义指令即时创建子代理：

```yaml
prompt: |
  To complete this task:
  
  1. Spawn a subagent to analyze the frontend code:
     delegate(instructions: "Analyze all React components in src/components/ and list their props and state management patterns")
  
  2. Spawn another subagent for the backend:
     delegate(instructions: "Document all API endpoints in src/api/ including their request/response schemas")
  
  3. Synthesize findings from both subagents into a unified report.
```

##### 多个子代理

在一条回复中发起多个 `delegate` 调用；每个调用在完成时返回其子代理的结果：

```yaml
prompt: |
  Run these analyses:
  
  delegate(instructions: "Count lines of code by language")
  delegate(instructions: "Find all TODO comments")
  delegate(instructions: "List external dependencies")
  
  Then combine the results into a codebase health report.
```

##### 子代理设置覆盖

为每个子代理定制模型、提供方或行为：

```yaml
prompt: |
  Use a faster model for simple tasks:
  
  delegate(
    instructions: "List all files modified in the last week",
    model: "gpt-4o-mini",
    max_turns: 3
  )
  
  Use the full model for complex analysis:
  
  delegate(
    instructions: "Review this code for security vulnerabilities",
    model: "claude-sonnet-4-20250514",
    temperature: 0.1
  )
```

##### 扩展作用域

限制子代理可以访问哪些扩展：

```yaml
prompt: |
  Create a sandboxed subagent with only file reading capabilities:
  
  delegate(
    instructions: "Analyze the README files in this project",
    extensions: ["developer"]  # Only developer extension, no network access
  )
```

#### 示例：多阶段代码评审工作流

```yaml
version: 1.0.0
title: Comprehensive Code Review
description: Multi-stage code review with parallel analysis

sub_recipes:
  - name: "security_scan"
    path: "./subrecipes/security-scanner.yaml"
    sequential_when_repeated: true  # Don't run multiple security scans in parallel
  
  - name: "style_check"
    path: "./subrecipes/style-checker.yaml"
  
  - name: "test_coverage"
    path: "./subrecipes/coverage-analyzer.yaml"

parameters:
  - key: pr_number
    input_type: number
    requirement: required
    description: "Pull request number to review"
  
  - key: review_depth
    input_type: select
    requirement: optional
    default: "standard"
    options: ["quick", "standard", "thorough"]

instructions: |
  Perform a comprehensive code review using specialized sub-recipes.
  
  ## Review Process
  
  ### Phase 1: Parallel Analysis
  Run these checks simultaneously:
  - style_check: Code style and formatting
  - test_coverage: Test coverage analysis
  
  ### Phase 2: Security Review
  After initial checks pass, run security_scan (sequential to avoid conflicts).
  
  ### Phase 3: Synthesis
  Combine all findings into a unified review report with:
  - Critical issues (must fix)
  - Suggestions (should consider)
  - Positive observations (good practices found)

extensions:
  - type: builtin
    name: developer
  - type: stdio
    name: github
    cmd: uvx
    args: ["github-mcp-server"]

prompt: |
  Review PR #{{ pr_number }} with {{ review_depth }} depth.
  
  {% if review_depth == "quick" %}
  Focus only on critical issues and security concerns.
  {% elif review_depth == "thorough" %}
  Perform exhaustive analysis including performance review.
  {% endif %}
  
  Start by fetching the PR details, then orchestrate the review phases.
```

#### 复杂工作流的最佳实践

1. **对可复用组件使用子 Recipe** —— 定义一次，在多个 recipe 中使用
2. **并行化独立任务** —— 一条消息中的多个子代理调用会并发运行
3. **使用 `sequential_when_repeated: true`** —— 用于不应并行运行的任务（例如数据库迁移）
4. **恰当地限定扩展作用域** —— 只给子代理它们需要的工具
5. **优雅地处理失败** —— 设计工作流时让它在某个子代理失败时仍能继续

#### 技术细节

- 子代理工具：`crates/goose/src/agents/subagent_tool.rs`
- 子代理执行：`crates/goose/src/agents/subagent_handler.rs`
- Recipe 的 sub_recipes 字段：`crates/goose/src/recipe/mod.rs`（SubRecipe 结构体）
- 模板渲染：`crates/goose/src/recipe/template_recipe.rs`

---

## 国际化（i18n）——Goose 桌面版 UI

> 原文：https://github.com/aaif-goose/goose/blob/main/I18N.md

本文档介绍 Goose 桌面版 UI（`ui/desktop/`）的 i18n 基础设施。

### 概览

该 i18n 系统基于 [react-intl](https://formatjs.io/docs/react-intl/)（FormatJS 套件的一部分）构建。它对翻译使用 **ICU MessageFormat** 标准，完整支持复数、性别/选择、数字/日期格式化，以及嵌套消息——全部由 CLDR 规则约束。

**关键设计决策：**

- 英文字符串以 `defaultMessage` 值的形式存在于源码中——代码与目录之间没有重复。
- `@formatjs/cli` 工具会自动从源码中提取消息到翻译目录。
- 日期、时间与数字格式化使用与文本翻译相同的 locale（通过 `IntlProvider` 实现单一事实来源）。
- 无需修改构建流水线——react-intl 是一个纯运行时库。

### 标记待翻译的字符串

#### 在 React 组件中

```tsx
import { defineMessages, useIntl } from 'react-intl';

const messages = defineMessages({
  greeting: {
    id: 'myComponent.greeting',
    defaultMessage: 'Hello, {name}!',
  },
  itemCount: {
    id: 'myComponent.itemCount',
    defaultMessage: '{count, plural, one {# item} other {# items}}',
  },
});

function MyComponent({ name, count }: { name: string; count: number }) {
  const intl = useIntl();
  return (
    <div>
      <h1>{intl.formatMessage(messages.greeting, { name })}</h1>
      <p>{intl.formatMessage(messages.itemCount, { count })}</p>
    </div>
  );
}
```

#### 消息 ID 约定

使用点分隔的层级化 ID，以反映组件所在位置：

```
settings.appearance.title
sessions.delete.confirmMessage
launcher.placeholder
searchBar.caseSensitive
```

#### ICU MessageFormat 语法

| 功能 | 语法 | 示例 |
|---|---|---|
| 插值 | `{variable}` | `Hello, {name}!` |
| 复数 | `{var, plural, one {…} other {…}}` | `{count, plural, one {# file} other {# files}}` |
| 选择 | `{var, select, male {…} female {…} other {…}}` | `{gender, select, male {He} female {She} other {They}}` |
| 数字 | `{var, number}` | `{price, number, ::currency/USD}` |
| 日期 | `{var, date, medium}` | `{when, date, long}` |

plural/selectordinal 内的 `#` 符号会被替换为格式化后的数字。

完整语法细节参见 [ICU MessageFormat 规范](https://unicode-org.github.io/icu/userguide/format_parse/messages/)。

### 提取消息

在添加或修改 `defineMessages` 调用后，重新生成英文目录：

```bash
cd ui/desktop
pnpm i18n:extract
```

这会扫描所有 `src/**/*.{ts,tsx}` 文件，并把权威的英文目录写入 `src/i18n/messages/en.json`。请提交该文件——它作为翻译者的参考。

#### 保持 en.json 同步（自动化检查）

`lint:check` 脚本包含 `i18n:check`，它会重新运行提取并验证输出与已提交的内容一致：

```bash
pnpm i18n:check
```

它作为 `pnpm lint:check`（因而是 CI）的一部分运行。如果开发者修改了源码中的某个 `defaultMessage` 却忘记运行 `pnpm i18n:extract`，该检查会失败，并给出一个 diff，精确显示哪里已过期。

要把消息编译成优化后的 AST 格式（可选，用于生产环境性能）：

```bash
pnpm i18n:compile
```

编译后的文件会输出到 `src/i18n/compiled/`（已被 gitignore）。

### Locale 检测

locale 在启动时按以下顺序解析：

1. **桌面语言设置** —— 在 Settings 中选择的，除非设置为 System Default
2. **`GOOSE_LOCALE`** —— 当桌面设置为
   System Default 时，来自环境/应用配置的显式覆盖
3. **`navigator.language`** —— 浏览器/操作系统 locale
4. **`"en"`** —— 回退默认值

解析出的 locale 同时用于文本翻译与所有 Intl 格式化（日期、数字、
相对时间）。修改桌面语言设置会重新加载渲染进程，以便仅在启动时读取 locale 的
辅助函数能获取到新值。

### 日期与数字格式化

#### 在 React 组件内部

使用 `useIntl()` hook 中的 `intl.formatDate()`、`intl.formatNumber()`、`intl.formatRelativeTime()`。它们会自动使用与文本翻译相同的 locale：

```tsx
const intl = useIntl();
intl.formatDate(new Date(), { month: 'long', day: 'numeric' });
intl.formatNumber(1234.5, { style: 'currency', currency: 'USD' });
```

#### 在 React 上下文之外

对于无法访问 React 树的工具函数（例如 `timeUtils.ts`），直接导入解析出的 locale：

```ts
import { currentLocale } from '../i18n';
new Intl.DateTimeFormat(currentLocale, { ... }).format(date);
```

这能确保日期/数字格式化使用与 UI 其余部分相同的 locale。

### 添加新语言

1. 把 `src/i18n/messages/en.json` 复制成一个新文件，例如 `src/i18n/messages/ja.json`。
2. 翻译 `defaultMessage` 值。保持 ICU 语法完整（例如 `{count, plural, ...}`）。
3. 把 locale 代码添加到 `src/i18n/index.ts` 中的 `SUPPORTED_LOCALES`。
4. 把该 locale 添加到 `src/components/settings/app/AppSettingsSection.tsx` 中的语言选择器。
5. 可选：运行 `pnpm i18n:compile` 进行预编译。

不需要其他代码改动——`loadMessages()` 会在运行时动态导入正确的目录。

### 测试

#### 用 IntlProvider 包裹测试渲染

任何使用 `useIntl()` 的组件都必须在 `IntlProvider` 内部渲染。使用测试辅助函数：

```tsx
import { IntlTestWrapper } from '../i18n/test-utils';

render(<MyComponent />, { wrapper: IntlTestWrapper });
```

#### i18n 专属测试

locale 检测与消息加载的单元测试位于 `src/i18n/i18n.test.ts`。用以下命令运行它们：

```bash
cd ui/desktop
pnpm test:run -- src/i18n/i18n.test.ts
```

### 架构小结

```
src/i18n/
├── index.ts          # Locale detection, loadMessages(), re-exports
├── messages/
│   └── en.json       # Extracted English catalog (committed)
├── compiled/         # Compiled catalogs (gitignored)
├── test-utils.tsx    # IntlTestWrapper for tests
└── i18n.test.ts      # Unit tests

src/renderer.tsx      # IntlProvider wraps the entire app tree
```
---

## 维护者

> 原文：https://github.com/aaif-goose/goose/blob/main/MAINTAINERS.md

### 核心维护者

* [Alex Hancock (@alexhancock)](https://github.com/alexhancock)
* [Bradley Axen (@baxen)](https://github.com/baxen)
* [Douwe Osinga (@DOsinga)](https://github.com/DOsinga)
* [Jack Amadeo (@jamadeo)](https://github.com/jamadeo)
* [Jasper Hugo (@jh-block)](https://github.com/jh-block)
* [Lifei Zhou (@lifeizhou-ap)](https://github.com/lifeizhou-ap)
* [Mic Neale (@michaelneale)](https://github.com/michaelneale)


### 维护者

* [Abhijay Jain (@Abhijay007)](https://github.com/Abhijay007)
* [Adrian Cole (@codefromthecrypt)](https://github.com/codefromthecrypt)
* [Angie Jones (@angiejones)](https://github.com/angiejones)
* [Rizèl Scarlett (@blackgirlbytes)](https://github.com/blackgirlbytes)
* [@The-Best-Codes](https://github.com/The-Best-Codes)

---

## unroll-agent-loop 的合并修复

> 原文：https://github.com/aaif-goose/goose/blob/main/MERGE_FIXES.md

### 针对 `unroll-agent-loop` 的合并修复

用于修复与 `origin/main` 合并所丢失内容的临时工作笔记。在该分支合并前
请删除此文件。

**状态：第 1–3 节已完成。** `cargo test -p goose` 只剩下 4 个 `jsonwebtoken`
库失败和 6 个依赖网络的 `tests/providers.rs` 失败，两者都是环境性的。
`cargo test -p goose-cli` 全绿。在 `state_machine/**` 之外，相对
`origin/main` 的 diff 从 50 个文件 / +1688 / -1237 变为 50 个文件 / +1657 / **-620**；每一处
残留的删除都在下面的有意删除清单中。第 4 和第 5 节仍然未完成。

工作过程中出现了两个问题，它们并非合并损伤：

- `cargo build -p goose-cli` 在这个分支上根本无法编译。`ActionRequiredData`
  新增了一个 `ToolConfirmationResponse` 变体，但 `session/export.rs` 从未获得对应的
  分支，而且该 crate 不在 `cargo test -p goose` 的覆盖范围内。已在此处修复，同时
  补上了缺失的 `MessageContent::Error` 分支。
- `tests/schedule_tool_security.rs::parse_errors_do_not_reflect_recipe_contents` 正在
  失败。抽取 `ScheduleTool` 时，把按扩展名解析的检查替换成了
  `validate_recipe_template_from_content`，它的错误是原始的 serde 消息——这会把
  recipe 文件内容原样引回给调用方。现在解析失败会重新得到那条通用消息；
  语义检查（缺少提示词、重试配置错误）仍然报告各自的措辞，这是
  `recipe_scheduling_lifecycle` 所依赖的。
- 平台扩展的提示词快照曾被重新生成而缺少 `code-mode`
  特性，因此丢掉了 `code_execution` 段，只在
  `cargo test -p goose` 下匹配。已用 workspace 的特性集重新生成：现在它与
  main 的差异仅在于 `## scheduler` 段。再次改动该快照前，请先运行 workspace 形式的命令。
- scheduler 扩展会向每个系统提示词贡献一个裸的 `## scheduler` 标题。
  它从未调用 `.with_instructions(...)`（其他所有平台扩展都会调用），并且在
  `default_enabled: true` 的情况下，即使宿主没有 scheduler 服务它也会注册，而此时它
  也不宣传任何工具。`client_factory` 现在返回 `Option<Box<dyn McpClientTrait>>`，
  这样宿主无法提供的扩展会主动拒绝而不是空注册，
  且 `SchedulerClient::new` 在没有 scheduler 时返回 `None`。`schedule_tool` 因此
  不再是一个 `Option`，从而移除了 `call_tool` 中的「Scheduler not available」死路。

### 发生了什么

`57f1b3f20`（以及更早的合并）通过整体保留分支版本的
`agent.rs` 与 `reply_parts.rs` 来解决冲突，然后手工把上游的部分内容移植回来。
两个方向的工作都有丢失：

- 上游的 #10716（稳定的 agent 事件消息身份）从未进入该分支
- 分支自己在 ACP 与 markdown 导出中的 `MessageContent::Error` 渲染
  被后续一次站在 main 一侧的合并覆盖了

因此有九个测试失败：7 个在 `crates/goose/tests/agent.rs`，2 个在
`crates/goose/tests/compaction.rs`。（库中的 4 个 `jsonwebtoken` 失败以及
`tests/providers.rs` 中的 6 个失败是环境性的——没有出站网络——不是我们的问题。）

只修补可见症状会让我们对其余部分只能猜测，所以这两个大文件
会从 `origin/main` 重建，并在其上重新应用状态机集成。

### 1. 从 `origin/main` 重建 —— 已完成

#### `crates/goose/src/agents/agent.rs`

恢复 main 的版本，然后只重新应用：

- `create_state_machine` 与 `reply_with_state_machine`
- `state_machine::enabled()` 的分派 —— 把它放在 `reply_impl` 里，**而不是** `reply`，这样
  状态机路径会继承 main 的 `ensure_message_event_id` 边界。这也是
  状态机发出的事件缺失 id 的修复；ops 不会一致地赋予它们 id，
  `Emitter::emit` 也不会。
- 在 `stop_hook_denial_context_message`、`stop_hook_denial_notification`、
  `stop_hook_block_cap_warning`、`stop_hook_block_cap`、`emit_stop_hook`、
  `emit_stop_hook_blocking`、`has_pending_steers`、`drain_pending_steers`、`goal`、`grind`、
  `stop_hook_block_cap_override` 上加上 `pub(crate)`
- 用 `steer_queues: Mutex<HashMap<String, SteerQueue>>` 取代 `pending_steers`，外加
  `steer_queue()` 访问器 —— `SteerOperation` 共享那个 `Arc<Mutex<VecDeque<Message>>>`
- 传给 `ExtensionManager::new` 的 `scheduler` 参数
- 移除 `PLATFORM_MANAGE_SCHEDULE_TOOL_NAME` 的分派与工具注册（由
  scheduler 平台扩展取代它 —— 见第 5 节）
- `tool_stream` / `ToolStreamItem` / `ToolStream` 现在位于 `tool_execution.rs`
- 在 `RetryResult::Retried` 之后清除 `final_output_tool.final_output` 的逻辑从
  `RetryManager` 移出，放到了调用方
- `dispatch_tool_call` 返回 `ErrorData` 而不是 `anyhow` + downcast
- `MAX_TURNS_MESSAGE` 从 `ops_maxturns` 导入，而不是再写一份字符串副本

当前 diff 中其他所有内容都是回归或无关改动。具体而言**不要**带过来：

- 移除 `ensure_message_event_id`、`push_message_with_id`、
  `persist_message_with_id`、`persist_and_push_message_with_id`
- `attach_turn_usage` 丢掉它的 `preferred_message_id` 参数
- 移除拆分工具请求消息的 response-id 载体逻辑
- `stop_hook_context` 丢掉 `.with_working_dir(...)`（见第 2 节）
- 在 `/goal` `/grind` 调用点内联 `command_starts_turn`（见第 2 节）

#### `crates/goose/src/agents/reply_parts.rs`

恢复 main 的版本，然后只重新应用 `ops_llm` 所调用的那部分抽取：

- `prepare_inference_tools`
- `prepare_tools_for_provider`
- `stream_response_from_provider` 作为一个自由函数

有两处偏离被丢弃而不是重新应用，因为遗留路径之外没有任何东西
需要它们：`prompt_manager.load_subdirectory_hints(working_dir)`（状态机通过
`build_system_prompt` 调用它）以及用
`with_extension_and_tool_counts(extension_count, tools.len())` 取代 main 的 `tool_count`。
`apply_tool_annotations` 也留在 main 放置它的位置——
`ops_llm` 自己会应用注解，所以把它移进 `list_tools` 从来就不是必要的。

`update_session_metrics` 逐字回到 main 的签名
（`post_compaction_context_tokens: Option<i32>`），它的三个调用方重新传入
`Some(compaction.retained_context_tokens)`。`bool` 版本会从摘要调用的输出 token 推导新的
基线，这会忽略所有被保留的内容——
那两个 `tests/compaction.rs` 失败正是关于这一点。

保留 main 的四个测试：`prepare_toolshim_tools_applies_writable_annotations`、
`normal_provider_stream_groups_only_contiguous_mergeable_chunks`、
`toolshim_provider_stream_assigns_missing_message_id`、
`toolshim_provider_stream_preserves_provider_message_id`。它们所覆盖的行为仍然
有效；只是测试被删除了。

#### `crates/goose-cli/src/session/output.rs`

恢复 main 的版本（它在两条渲染路径中都有 #10493 的 `is_user_visible` 守卫与
`user_visible_content()` 投影），然后只重新加上 `MessageContent::Error` 分支与
`ActionRequiredData::ToolConfirmationResponse` 分支。

#### `crates/goose/tests/agent.rs`、`crates/goose/tests/compaction.rs`、`crates/goose/src/agents/execute_commands.rs`

恢复被删除的上游测试以及 `command_starts_turn` 辅助函数（连同它的测试）。
`execute_commands.rs` 除此之外保留其分支改动：`is_known_slash_command`、
持久化 recipe 的 `resolve_command`、`Conversation::last`。

### 2. 直接回退 —— 已完成

- `stop_hook_context` 重新获得 `.with_working_dir(...)`。它曾是最后一个调用方，所以
  `HookContext::working_dir` 目前对*每一个* hook 事件都序列化为 `null`，而不只是
  Stop。Hook 插件会读取该字段。
- `crates/goose/src/providers/oauth.rs` —— `test_token_cache` 的重写与本分支无关。
  回退它。
- 从非状态机测试中删除的注释（例如
  `tests/compaction.rs::assert_conversation_compacted` 中的受众说明）重新加回来。

### 3. 重新落地被后续合并丢弃的分支工作 —— 已完成

- `crates/goose/src/acp/server.rs` —— `MessageContent::Error` 作为 agent 消息块，以及
  `Error(CreditsExhausted)` 经由 `prompt_error_from_message_content` 路由，以便
  桌面支付流程仍然触发。目前该函数只匹配 `SystemNotification`，
  所以状态机下的提供方错误在桌面上是不可见的。
- `crates/goose-cli/src/session/export.rs` —— `MessageContent::Error` 分支。它目前会
  落到 `WARNING: Message content type could not be rendered to Markdown`。

两者都在 `1729c902b` 中添加，之后被覆盖。

### 4. 简化 —— 仍未完成

- `OperationResult::NotApplicable(Emitter)` 把 emitter 穿回结果中，
  这迫使在 `machine.rs` 中使用 `Option<Emitter>` + `take()`，并为
  一个类型层面的不变量加入运行时 `anyhow!("step did not return the event emitter")`。`Emitter`
  是 `Clone`，而且 ops 本来就会在内部克隆它，所以它什么也保证不了。改为传 `&Emitter`
  并把枚举改为 `NotApplicable | Applied(StepResult)`。
- `state_machine::usage::estimate_context` 是
  `context_mgmt::count_retained_context_tokens` 的一份拷贝。一旦 `retained_context_tokens` 再次被消费，
  两条路径就可以共享同一个函数。
- 仓库根目录的 `phase1_basic_tools.md` 与 `test_results.tsv` 是自测产物。
  删除它们。

### 5. Scheduler 工具重命名 —— 已接受

把 scheduler 转换为平台扩展后，面向模型的工具从
`platform__manage_schedule` 重命名为 `scheduler__manage_schedule`。`PermissionManager` 按工具名
存储权限，因此该工具所有已保存的「always allow」都会丢失，命名旧工具的 recipe 或
hook 匹配器也会停止匹配。按现状接受——不做迁移。

### 其他待办

`cargo clippy --workspace --all-targets -- -D warnings` 有 8 个错误，全部位于
`state_machine/**` 且都早于本次修复：`dummy_api.rs` 中的 UTF-8 字符串索引、
`InferenceRunner::new` 与四个 `dummy_api` 辅助函数上的 `too_many_arguments`，以及
`StateEffect::SetRecipe` 上的 `large_enum_variant`。在解决这些问题之前，该分支
无法通过 lint 门禁合并。

### 验证

每个文件之后：

```bash
cargo test -p goose --test agent --test compaction
cargo test -p goose --lib agents::state_machine
```

三者全绿就是重建已恢复合并所丢失内容的证据。然后：

```bash
cargo fmt
cargo clippy --all-targets -- -D warnings
cargo test -p goose --no-fail-fast
```

预期 4 个 `jsonwebtoken` 库失败与 6 个依赖网络的 `tests/providers.rs`
失败仍然存在；其他都不应失败。

---

## goose（README）

> 原文：https://github.com/aaif-goose/goose/blob/main/README.md

<div align="center">

### goose

_你原生的开源 AI agent —— 桌面应用、CLI 与 API —— 面向代码、工作流，以及其间的一切_

<p align="center">
  <a href="https://opensource.org/licenses/Apache-2.0"
    ><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg"></a>
  <a href="https://discord.gg/n8R5VaWDAn"
    ><img src="https://img.shields.io/discord/1287729918100246654?logo=discord&logoColor=white&label=Join+Us&color=blueviolet" alt="Discord"></a>
  <a href="https://github.com/aaif-goose/goose/actions/workflows/ci.yml"
     ><img src="https://img.shields.io/github/actions/workflow/status/aaif-goose/goose/ci.yml?branch=main" alt="CI"></a>
  <a href="https://insights.linuxfoundation.org/project/goose"><img src="https://insights.linuxfoundation.org/api/badge/health-score?project=goose"></a>
  <a href="https://repology.org/project/goose-cli/versions"><img src="https://repology.org/badge/tiny-repos/goose-cli.svg" alt="Packaging status"></a>
</p>

<a href="https://trendshift.io/repositories/25298?utm_source=repository-badge&amp;utm_medium=badge&amp;utm_campaign=badge-repository-25298" target="_blank" rel="noopener noreferrer"><img src="https://trendshift.io/api/badge/repositories/25298" alt="aaif-goose%2Fgoose | Trendshift" width="250" height="55"/></a>

</div>


goose 是一个运行在你机器上的通用 AI agent。不只是用于代码——你可以用它做研究、写作、自动化、数据分析，或任何你需要完成的事。

一个面向 macOS、Linux 与 Windows 的原生桌面应用。一套用于终端工作流的完整 CLI。一个可以嵌入任何地方的 API。用 Rust 构建，兼顾性能与可移植性。

goose 支持 15 个以上的提供方——Anthropic、OpenAI、Google、Ollama、OpenRouter、Azure、Bedrock 等等。使用 API key，或通过 [ACP](https://goose-docs.ai/docs/guides/acp-providers) 使用你现有的 Claude、ChatGPT 或 Gemini 订阅。通过 [Model Context Protocol](https://modelcontextprotocol.io/) 开放标准连接到 70 个以上的扩展。

goose 是 Linux 基金会旗下[Agentic AI Foundation（AAIF）](https://aaif.io/)的一部分。

### 开始使用

**[下载桌面应用](https://goose-docs.ai/docs/getting-started/installation)**，支持 macOS、Linux 与 Windows。

或者安装 CLI：

```bash
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash
```

### 快速链接
- [快速上手](https://goose-docs.ai/docs/quickstart)
- [安装](https://goose-docs.ai/docs/getting-started/installation)
- [教程](https://goose-docs.ai/docs/category/tutorials)
- [文档](https://goose-docs.ai/docs/category/getting-started)
- [治理](https://github.com/aaif-goose/goose/blob/main/GOVERNANCE.md)
- [自定义发行版](https://github.com/aaif-goose/goose/blob/main/CUSTOM_DISTROS.md) —— 用预配置的提供方、扩展与品牌打造你自己的 goose 发行版

#### 需要帮助？
- [诊断与报告](https://goose-docs.ai/docs/troubleshooting/diagnostics-and-reporting)
- [已知问题](https://goose-docs.ai/docs/troubleshooting/known-issues)

### 一点 goose 幽默 🪿

> 为什么开发者选择 goose 作为他们的 AI agent？
> 
> 因为它总能帮他们「迁移（migrate）」代码到生产环境！🚀

### 和我们一起 goose 一下
- [Discord](https://discord.gg/n8R5VaWDAn)
- [YouTube](https://www.youtube.com/@goose-oss)
- [LinkedIn](https://www.linkedin.com/company/goose-oss)
- [Twitter/X](https://x.com/goose_oss)

---

## 发布流程

> 原文：https://github.com/aaif-goose/goose/blob/main/RELEASE.md

### 制作发布

你通常会创建两种发布类型之一：常规功能发布（次版本号提升，如 1.20）或修 bug 的补丁发布（补丁版本号提升，如 1.20.1）。

goose 使用 GitHub actions 自动化发布流程。实际的发布由 tag 触发。

### 次版本发布

这些通常每周做一次。该流程有两个自动化阶段：

1. **版本提升 PR** —— 一个[action](https://github.com/aaif-goose/goose/actions/workflows/minor-release.yaml)每周二运行（也可手动触发），它会创建一个 PR 来提升 `main` 上的版本。评审并合并该 PR。

2. **发布分支 + PR** —— 当版本提升 PR 合并后，自动化会从 `main` 创建一个 `release/<version>` 分支，并开一个带 QA 清单的发布 PR。

从那里开始：
- 如果可以，在本地测试（`just run-ui`）
- 如有需要，把最后的修复 cherry-pick 到发布分支
- 下载并测试发布 PR 中的 .zip
- 准备好后，按照发布 PR 上的说明打 tag 并发布

要触发发布，找到[对应的 PR](https://github.com/aaif-goose/goose/pulls?q=is%3Apr+%22chore%28release%29%22+author%3Aapp%2Fgithub-actions+)，并按照 PR 描述中的说明操作。

### 补丁版本发布

当次版本被打了 tag 后，自动化会立即创建下一个补丁发布分支（例如从 `release/1.25.0` 创建 `release/1.25.1`），版本已经提升，发布 PR 也已打开。把修复 cherry-pick 到该分支，准备好后打 tag。

要触发发布，找到[对应的 PR](https://github.com/aaif-goose/goose/pulls?q=is%3Apr+%22chore%28release%29%22+%22%28patch%29%22+author%3Aapp%2Fgithub-actions+)，并按照 PR 描述中的说明操作。

### 高层发布流程：

```
minor-release (cron/manual)
  │
  ▼
version-bump PR → main (merge this)
  │
  ▼ (on merge)
release/<V> branch created from main
release PR opened (for QA, cherry-picks, testing)
  │
  ▼ (when ready)
git tag v<V> origin/release/<V> && git push origin v<V>
  │
  ├─► release PR auto-closed (no merge needed)
  ├─► release.yml builds & publishes
  └─► patch release/<V+1> branch + PR auto-created
        │
        ▼ (cherry-pick fixes, then when ready)
        git tag v<V+1> origin/release/<V+1> && git push origin v<V+1>
```

---

## goose 发布人工测试清单

> 原文：https://github.com/aaif-goose/goose/blob/main/RELEASE_CHECKLIST.md

### goose 发布人工测试清单

从本 PR 下载发布构建。一旦某个构建就绪，actions bot 会在本 PR 上发布一条评论，
说明如何下载与签名。

### 使用以下脚本创建风险评估与测试计划：
```
./workflow_recipes/release_risk_check/run.sh {{VERSION}}
```

它会在 `/tmp/release_report_final.md` 中生成一份分析报告，并对高风险的 pr 改动执行必要的测试。

### 运行 goose 自测 recipe

goose run --recipe goose-self-test.yaml

### 让 goose 产出一份测试计划

打开候选发布的桌面应用，让 goose 通过指向本 PR 来产出一份测试计划。使用类似这样的提示词

> Look at the notes in PR <release PR> and the report at `/tmp/release_report_final.md` and investigate potential risks in this release. After familiarizing yourself with the scope of each change, produce a suggested test plan that I should follow before publishing the release.

goose 会产出一份计划。按照该计划完成测试。

---

## 为 RISC-V 构建 goose

> 原文：https://github.com/aaif-goose/goose/blob/main/RISCV_SETUP.md

### 为 RISC-V 构建 goose（riscv64gc-unknown-linux-gnu）

本文档介绍如何为 RISC-V 64 位系统构建带完整 V8/code-mode 支持的 goose-cli。

> [!WARNING]
> 这是一个实验性的、由社区贡献的构建流程。RISC-V 并未
> 得到 goose 项目的官方支持。

### 前置条件

- Rust 1.96.1+（无需升级工具链）
- RISC-V 交叉编译工具链：`gcc-riscv64-linux-gnu`
- 目标：`rustup target add riscv64gc-unknown-linux-gnu`

#### 链接器配置

在 RISC-V 硬件**上**构建不需要任何额外配置——会自动使用
原生链接器。

**交叉编译**（例如从 x86_64）需要交叉链接器，否则
rustc 会调用宿主 `cc` 并导致链接失败。要么导出：

```bash
export CARGO_TARGET_RISCV64GC_UNKNOWN_LINUX_GNU_LINKER=riscv64-linux-gnu-gcc
```

要么添加到 `.cargo/config.toml`（或 `~/.cargo/config.toml`）：

```toml
[target.riscv64gc-unknown-linux-gnu]
linker = "riscv64-linux-gnu-gcc"
```

如果你的发行版以不同的名称提供交叉 gcc，请相应调整二进制文件名。

### 概览

V8 152.2.0 是第一个带有预构建 RISC-V 二进制的版本。然而：
- 当前的 goose 通过 deno_core 0.381.1 使用 v8 145.0.0（不支持 RISC-V）
- 升级需要为 V8 152 的 API 变更给 deno_core 与 serde_v8 打补丁
- 这些补丁侵入性强，如果通过 Cargo.toml patch 应用会影响所有平台

### 设置步骤

#### 1. 克隆 rusty_v8 v152.2.0

在仓库根目录运行：

```bash
git init vendor/rusty_v8
git -C vendor/rusty_v8 remote add origin https://github.com/denoland/rusty_v8.git
git -C vendor/rusty_v8 fetch --depth 1 origin 2768994f664e8a6e3aba27503606c58339136e2a
git -C vendor/rusty_v8 checkout --detach FETCH_HEAD
rm -rf vendor/rusty_v8/.git
```

这会提供带 RISC-V 支持的 v8 152.2.0。Cargo 会自动下载预构建的二进制。

#### 2. Vendor deno_core 0.381.1

在仓库根目录运行：

```bash
wget -P vendor https://static.crates.io/crates/deno_core/deno_core-0.381.1.crate
echo "77660b04f5368bcd69a42e0fdd6343e325eb781ec7d79bbf49ff2548ae4f17b6  vendor/deno_core-0.381.1.crate" | sha256sum --check
tar -C vendor -xzf vendor/deno_core-0.381.1.crate
mv vendor/deno_core-0.381.1 vendor/deno_core
rm vendor/deno_core-0.381.1.crate
```

#### 3. Vendor serde_v8 0.290.0

在仓库根目录运行：

```bash
wget -P vendor https://static.crates.io/crates/serde_v8/serde_v8-0.290.0.crate
echo "21a52aca5a5661aea9c2ccf8c2f985f2381266d7aab03a0d02beadb4ae1190ea  vendor/serde_v8-0.290.0.crate" | sha256sum --check
tar -C vendor -xzf vendor/serde_v8-0.290.0.crate
mv vendor/serde_v8-0.290.0 vendor/serde_v8
rm vendor/serde_v8-0.290.0.crate
```

#### 4. 应用补丁

##### vendor/v8 —— 把它从 workspace 中移除

克隆下来的 `vendor/rusty_v8` 本身就是 `152.2.0` 版本的 `v8` crate，所以根
`[patch.crates-io]` 条目直接指向它（见第 6 步）。已提交的
`vendor/v8` 垫片不被编辑，但它必须离开 workspace：
它会引入 `v8-goose`，后者声明了 `links = "rusty_v8"`，而一旦该
补丁解析到 denoland 的 `v8` 152（同样是 `links = "rusty_v8"`），一个同时包含两者的 workspace
就会以「more than one crate with links=rusty_v8」失败。从 `members` 中移除
`vendor/v8` 并把它加到 `exclude`（见第 6 步）。

##### vendor/deno_core/Cargo.toml

更新 v8 与 ICU-data 依赖：

```toml
[dependencies.v8]
version = "152.2.0"  # was 145.0.0
default-features = false

[dependencies.deno_core_icudata]
version = "0.78.0"  # was 0.77.0; V8 152 needs the ICU 78 data blob
optional = true
```

##### vendor/serde_v8/Cargo.toml

更新 v8 依赖：

```toml
[dependencies.v8]
version = "152.2.0"  # was 145.0.0
default-features = false
```

#### 5. 对 vendor/deno_core 的源码补丁

这些补丁让 deno_core 0.381.1 适配 V8 152 的 API 变更。

##### 用 `unsafe {}` 包裹 `v8::Global::open()` 调用

V8 152 把 `Global::open()` 标记为 unsafe。受影响的文件：
- `error.rs`（2 处）
- `modules/map.rs`（9 处）
- `runtime/jsrealm.rs`（1 处）
- `runtime/jsruntime.rs`（3 处）
- `ops_builtin_v8.rs`（1 处）

示例：
```rust
// Before:
let cb = callback.open(scope);

// After:
let cb = unsafe { callback.open(scope) };
```

##### 在 `runtime/bindings.rs` 中禁用 fast-call 路径

Fast-call API 会在 RISC-V 上创建快照时导致 SIGILL：

```rust
// Replace lines ~600-605:
let template = builder.build(scope);
// (Remove the if/else with fast_function)
```

##### 在 `ops_builtin.rs` 中更新 `WasmStreaming`

```rust
// Before:
pub struct WasmStreamingResource(pub(crate) RefCell<v8::WasmStreaming>);

// After:
pub struct WasmStreamingResource(pub(crate) RefCell<v8::WasmStreaming<false>>);
```

##### 在 `runtime/setup.rs` 中更新 ICU 数据

初始化函数名与数据 blob 必须匹配（见上面
`deno_core_icudata` 的版本提升）—— `set_common_data_78` 会拒绝 ICU 77
的 blob，导致 V8 初始化失败。

```rust
// Line ~19:
v8::icu::set_common_data_78(deno_core_icudata::ICU_DATA).unwrap();
// was: set_common_data_77

// Line ~24 - remove this line:
" --no-validate-asm",  // Remove - V8 13+ doesn't support this flag
```

#### 6. 更新根 Cargo.toml

添加 workspace 排除与补丁：

```toml
[workspace]
members = ["crates/*"]  # drop "vendor/v8" (see step 4)
exclude = ["vendor/v8", "vendor/rusty_v8"]
resolver = "2"

# Relax ICU pins (temporal 0.2.6 handles this):
icu_calendar = { version = ">=2.1", default-features = false }
icu_locale = { version = ">=2.1", default-features = false }

[patch.crates-io]
deno_core = { path = "vendor/deno_core" }
serde_v8 = { path = "vendor/serde_v8" }
v8 = { path = "vendor/rusty_v8" }  # was vendor/v8; rusty_v8 is the v8 crate
# ... existing patches
```

#### 7. 更新 crates/goose/Cargo.toml

放宽 ICU 版本约束：

```toml
icu_calendar = { version = ">=2.1", default-features = false }
icu_locale = { version = ">=2.1", default-features = false }
```

#### 8. RISC-V 更新命令处理（已在仓库中）

`crates/goose-cli/src/commands/update.rs` 已经处理了 RISC-V：

- `asset_name()` 包含了 riscv64gc-gnu 资源名，以便该函数
  在 RISC-V 上能编译（否则每个分支都被 cfg 禁用，函数体会
  求值为 `()` 而不是 `&'static str`）。
- `update()` 在 riscv64 上会提前报错退出并给出清晰的错误，因为该平台
  尚未发布发布产物：

```rust
#[cfg(all(target_arch = "riscv64", not(feature = "disable-update")))]
{
    bail!("Self-update is not supported on riscv64: no release artifacts are published for this platform.");
}
```

一旦 RISC-V 资源被加入发布流水线，就移除该提前退出块，并从主分支中
去掉 `not(target_arch = "riscv64")`。

由于该提前退出使模块的其余部分在 riscv64 上被 cfg 禁用，
该文件还带有一个模块级的 allow，以便 `clippy -D warnings` 在 RISC-V 构建中
保持干净（在其他目标上不生效）：

```rust
#![cfg_attr(target_arch = "riscv64", allow(dead_code, unused_imports, unused_variables))]
```

#### 9. 更新依赖

只更新本次设置所改动的依赖，而不是整个 lockfile：

```bash
cargo update deno_core_icudata icu_calendar icu_locale temporal_rs
```

预期的改动：
- v8：145.0.0 → 152.2.0（本地，通过补丁）
- deno_core_icudata：0.77.0 → 0.78.0
- temporal_rs：0.1.2 → 0.2.6
- icu_calendar：2.1.1 → 2.3.0

#### 10. 构建

```bash
cargo build --release --target riscv64gc-unknown-linux-gnu -p goose-cli --bin goose
```

输出：`target/riscv64gc-unknown-linux-gnu/release/goose`

### 完整补丁脚本

自动化设置参见 `scripts/setup-riscv.sh`。

### 已知问题

- Fast-call 优化被禁用（RISC-V 创建快照时 SIGILL）
- 使用 vendored deno_core 时，补丁会影响所有平台
- 会向仓库添加约 2.6MB 的 vendor 依赖

### 替代方案：条件编译

对于生产 PR，考虑：
1. 把 deno_core/serde_v8 补丁保留在单独的 git 分支中
2. 记录手动设置步骤
3. 只提交最小改动（update.rs、CI workflow）
4. 让用户在本地为 RISC-V 构建应用补丁

### 验证

```bash
# Check architecture
file target/riscv64gc-unknown-linux-gnu/release/goose
# Output: ELF 64-bit LSB pie executable, UCB RISC-V

# Test execution (on RISC-V hardware)
./target/riscv64gc-unknown-linux-gnu/release/goose --version
./target/riscv64gc-unknown-linux-gnu/release/goose doctor
```

---

## 安全

> 原文：https://github.com/aaif-goose/goose/blob/main/SECURITY.md

> [!CAUTION]
> goose 是一个开发者 agent，可以访问各种系统，并代表用户在其本地机器上执行操作。请注意，由于开发者 agent 有能力在你的计算机上运行代码并采取行动，与基于聊天的 LLM 交互相比，它们带来了独特的风险。虽然大多数基础模型都包含针对提示词注入的基线防护，但在使用 goose 与互联网或其他不受信任的数据源交互时，仍然存在固有风险。为将这些风险降到最低，请考虑采取以下预防措施：
>
> - 使用一个专用虚拟机或容器（Docker/Kubernetes），并限制其特权能力。这将最大限度降低本地系统被攻击或关键系统资源被意外访问的风险。
> - 始终审查 goose 生成的代码与测试是否准确。
> - 避免向 goose 提供敏感或机密信息，以防信息泄露。
> - 对于可能导致重大变更的任何系统与操作，始终要求人工确认。
> - 如果可能，把复杂的 goose 指令拆解为更小、隔离的操作。这降低了某条错误命令一次性影响系统多个部分的风险，也让异常行为更容易被检测到。
> - 只把你已审查过的 MCP 扩展连接到 goose
>
> 在某些情况下，goose 可能会遵循内容中嵌入的命令，即使这些命令与交给 goose 的任务相冲突。我们建议采取上述预防措施来限制提示词注入带来的风险。通过这些步骤，你可以降低与开发者 agent 相关的潜在安全风险，更好地保护你的系统与用户。
>
> AAIF（Agentic AI Foundation）认可我们的开源社区所做的重要贡献。保障 goose 及其用户安全的一部分，就是确保我们找出并修复开源项目中发现的任何安全问题。如果你发现安全漏洞，我们鼓励你通过仓库的 Security 标签页 -> Report a vulnerability 私下报告。
>
> 更多信息请参见[私下报告安全漏洞](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability#privately-reporting-a-security-vulnerability)。如需协助或升级处理，请联系 [AAIF 开源治理委员会](mailto:open-source-governance@block.xyz)
