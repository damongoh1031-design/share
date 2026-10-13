# OpenClaw 2.0 × Hermes Agent 按操作系统安装配置与注意事项指南

> 核验日期：2026-10-13。所有版本口径以当日官方一手来源为准；社区/镜像来源已单独标注。
> 配套报告：`openclaw2-vs-hermes-research.md`、`第5章_Arch-NixOS部署适配与双栈选型.md`。

## 0. 导读：平台支持矩阵

截至 2026-10-13，两款工具的最新版本：**OpenClaw ≈ v2026.9.9**（AUR 稳定包 2026.9.9-1，2026-10-08 更新）、**Hermes Agent v0.21.7**（2026-10-12）。

| 平台 | OpenClaw 2.0 | Hermes Agent |
|---|---|---|
| NixOS / Nix | ✅ 第一方 nix-openclaw Home Manager 模块，`OPENCLAW_NIX_MODE=1` 应用层不可变 | ⚠️ **Tier 2 尽力而为**：flake + NixOS 模块 + Home Manager 模块，官方明言"可能随时被 main 分支破坏" |
| Arch Linux | ✅ 官方 `install.sh`（supported path）；AUR 有 3 包但 ArchWiki 预警"存在 bug 且不稳定" | ⚠️ AUR 有 `hermes-agent` 包（当日更新、7 票）但**官方明确列为"不支持"**；官方支持路径是 install.sh |
| Debian/Ubuntu/Fedora 等 glibc Linux | ✅ install.sh / install-cli.sh / .deb / AppImage | ✅ Tier 1（要求 glibc + systemd + FHS） |
| Alpine/musl | ⚠️ 可装但 SQLite 安全检查常不过关，官方建议改用容器 | ⚠️ 无官方承诺，未列入支持矩阵 |
| macOS | ✅ .app 需 **macOS 26.2 (Tahoe)+**；CLI/Gateway 需受支持 Node | ✅ 仅 **Apple Silicon** 为 Tier 1；Intel Mac 属特殊路径 |
| Windows 10/11 | ✅ 桌面 app（需签名 Bun 运行时）/ PowerShell CLI / Windows Hub / WSL2 Gateway | ✅ Tier 1 原生（x86_64/aarch64）；MSIX 桌面需 Win11 22H2+ |
| WSL2 | ✅ install.sh 支持；官方文档专列 WSL2 Gateway 拓扑 | ✅ Tier 1（与 Linux 并列） |
| Docker | ✅ `ghcr.io/openclaw/openclaw`，端口 18789 | ✅ `nousresearch/hermes-agent`，网关 8642 / 面板 9119 |
| Android / Termux | ❌ 无 | ⚠️ Tier 2 且**当前损坏**（官方 danger 横幅），aarch64 only |
| AUR / pypi / brew 装 Hermes | — | ❌ **官方"不支持"清单**明列：AUR、pypi（uv tool/pip）、brew |

**三条铁律（先记住，能避开大多数翻车）：**

1. **OpenClaw 的 Node 必须是 `>=24.16.0 <25 || >=26.1.0`**（v2026.9.3 起口径；Node 22/23/25 均不支持），且**链接的 SQLite 库必须修过 WAL-reset 损坏 Bug**（需 SQLite 3.51.3+ / 3.50.7+ / 3.44.6+，视分支而定）。根因是 `node:sqlite` TEXT 解码器在嵌入 NUL 处截断（nodejs/node#61954）与 SQLite WAL-reset 损坏——**不是**社区流传的 V8 ABI 说法。
2. **Hermes 第一方安装运行在 Python 3.14 上**。`pyproject.toml` 里 `>=3.11,<3.15` 只是让旧 Python 能跑 updater，PM 随后会切到自管的 3.14；不要指望 3.11–3.13 是受支持的运行时。（社区镜像 hermes-agents.net 仍写"最低 3.10/推荐 3.11"，已过时。）
3. **Hermes 不支持 AUR / pypi / brew 安装**，出问题不受理；要支持请迁移到 install.sh / install.ps1 / Docker / 桌面包 / Nix（Tier 2）。

---

## 1. 通用前置与版本口径

### 1.1 OpenClaw：Node + SQLite 双重门槛

v2026.9.3 起官方支持矩阵（[docs.openclaw.ai/install/node](https://docs.openclaw.ai/install/node)）：

| Node 版本 | 支持？ | 说明 |
|---|---|---|
| 26.1+ | ✅ 推荐 | v2026.9.3 起的主力推荐线 |
| 24.16+（<25） | ✅ | Node 24 LTS 线，v2026.9.3 前的口径是 24.15+ |
| 22.x / 23.x / 25.x | ❌ | 22 是 2.0 初期口径；23、25 从未受支持 |

安装器行为（[Installer internals](https://docs.openclaw.ai/install/installer)）：

- `install.sh` / `install.ps1` 在缺 Node 且无 nvm 时自动装机：macOS 走 Homebrew 装 Node 26，Linux 走 NodeSource 装 Node 24 LTS，Windows 走 winget/Chocolatey/Scoop（兜底下 Node 26）。
- **RPM 系自带的 Node 若链接了不安全的 SQLite**：安装器保留发行版包不动，另建用户态 Node（`~/.openclaw/tools/cli-node`，被 `OPENCLAW_HOME` 覆盖时改用其下路径）。
- CLI 检测到不受支持的 Node 时会交互式提供 `Update NodeJS: Y/N`（需 TTY；`--json`/`--yes`/`--non-interactive` 下不提示），装一个校验过的私有运行时，**不动系统 Node、shell 设置、包和 Gateway 服务**。Alpine/musl 与非 x64/ARM64 架构不在此列，需手动装。
- **Alpine 专属坑**：apk 装的新 Node 仍可能链接有漏洞的系统 SQLite，官方明确建议直接用官方 `node:26-alpine` 容器或换 glibc 主机。
-  Bun 运行时备选：`install.sh --runtime bun` 仅限 macOS 与 glibc Linux（x64/arm64），装的是 OpenClaw 发布钉住的 Bun fork，Windows/musl 拒绝。

### 1.2 Hermes：Python 3.14 + PM 自管工具链

[官方 Installation 页](https://hermes-agent.nousresearch.com/docs/getting-started/installation)现行口径：

- 源码安装器克隆源码 → 引导 uv → 交给 **PM** 准备依赖；PM 提供**钉住的** Python（3.14）、Node.js、npm、ripgrep、FFmpeg（版本读 `pm/lock.json`，**不收编系统里随便版本的 Node**）。
- 默认选 `all` Python extra，并默认装浏览器与计算机使用工具：`agent-browser` + 钉住的 Chromium、`cua-driver`（macOS/Windows/glibc Linux）。想跳过：POSIX 加 `--skip-browser` / `--skip-computer-use`，Windows 加 `-SkipBrowser` / `-SkipComputerUse`；**这个选择会被记住**，以后 `hermes update` 不会偷偷装回来，想补装用 `hermes pm install agent-browser`。
- **glibc Linux 的 `libatomic` 坑**：PM 自管 Node 链接 `libatomic.so.1`，而精简 Debian/Ubuntu/RHEL 系镜像不带。安装器与 `hermes update` 会自动跑包管理器补（apt/zypper 叫 `libatomic1`，dnf/yum/apk 叫 `libatomic`，pacman 叫 `gcc-libs`），以 root 或 `sudo -n` 执行；`--non-interactive` 绝不弹密码。无 sudo 的服务用户会得到一条确切命令，转交管理员执行。
- 全程**不要用 sudo 跑安装器**（以目标服务用户身份跑；家目录、工具库、配置、launcher 都必须属于该用户）。要常驻后台的 Linux 用户服务，管理员需 `sudo loginctl enable-linger <用户>`。

### 1.3 中文文档滞后坑（对中文用户尤其重要）

OpenClaw **中文文档站的 Node 兼容页在 v2026.9.3 改口径后仍写旧区间**（`>=22.22.3 <23 || >=24.15.0 <25 || >=25.9.0`），直接按中文页配环境会踩坑。**以英文页 / 安装器实报为准**：命令行里 `openclaw --version`、`openclaw doctor --lint` 在不受支持 Node 上仍可跑（只读诊断），并会打印 `Running on an unsupported Node (<version>)` 警告。

---

## 2. NixOS / Nix（声明式党主战场）

### 2.1 OpenClaw：nix-openclaw 一方 Home Manager 模块

[官方 Nix 文档](https://docs.openclaw.ai/zh-CN/install/nix)确认 nix-openclaw 为**第一方** Home Manager 模块：

```nix
# flake.nix（示意）
{
  inputs.nix-openclaw.url = "github:openclaw/nix-openclaw";
  # home-manager 模块中启用 programs.openclaw，配置写入 openclaw.json
}
```

亮点：

- Gateway 与工具链**全部版本锁定**，重启可持续运行的服务；**声明式插件系统**。
- `home-manager switch --rollback` **即时回滚**。
- **`OPENCLAW_NIX_MODE=1` 应用层不可变**：`openclaw.json` 被视作只读，`openclaw update`、插件安装/卸载、`doctor --fix`、`config set`、`--generate-gateway-token` 等写操作**全部被拒绝**，只能改 Nix 源——这是双栈中唯一的"应用层不可变语义"。
- launchd/systemd 服务自动发现 `NIX_PROFILES` 中的二进制加入 PATH（未设置时回退 `~/.nix-profile/bin`）。

### 2.2 Hermes：flake 三形态（Tier 2，尽力而为）

官方[Nix & NixOS Setup](https://hermes-agent.nousresearch.com/docs/getting-started/nix-setup)页开头就是 Tier 2 警告：**"Nix is no longer an explicitly supported install path (best-effort only)"**，main 分支提交可能随时破坏 flake 与模块。三种形态：

```bash
# 形态一：任意 Nix 用户（NixOS/macOS/Linux 通用）
nix profile install github:NousResearch/hermes-agent
# 之后 PATH 上有 hermes / hermes-agent / hermes-acp 三个命令
# 工作流与标准安装完全一致：hermes setup → hermes gateway install → ~/.hermes/ 配置

# 只要消息网关的轻量变体（闭包从 ~700MB 降到 ~33MB）
nix profile install github:NousResearch/hermes-agent#messaging
```

- uv2nix 构建全部 Python 依赖，Node/git/ripgrep/ffmpeg 包进二进制 PATH——**运行时无 pip、无 venv 激活、无 npm install**。
- 运行时钉随 `pm/lock.json`：`nix/pythonLock.nix` 读 Python 主次版本，**钉的 nixpkgs 缺该版本族时求值直接报错**，不会换一个 Python。

### 2.3 Hermes NixOS 模块（原生 / 容器两种模式）

```nix
# /etc/nixos/flake.nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    hermes-agent.url = "github:NousResearch/hermes-agent";
  };
  # outputs 里 modules = [ hermes-agent.nixosModules.default ];
}

# configuration.nix 最小配置
{ config, ... }: {
  services.hermes-agent = {
    enable = true;
    settings.model.default = "anthropic/claude-sonnet-4";
    environmentFiles = [ config.sops.secrets."hermes-env".path ];
    addToSystemPackages = true;   # hermes 上 PATH + 全系统共享 HERMES_HOME
  };
}
```

`nixos-rebuild switch` 后自动建 `hermes` 用户、生成 config.yaml、接管机密、启动 gateway 服务。

| 模式 | 运行方式 | 自装包能力 | 适用 |
|---|---|---|---|
| **原生**（默认） | 主机上加固的 systemd 服务（`NoNewPrivileges`/`ProtectSystem=strict`/`PrivateTmp`） | ❌ 只能用 Nix PATH 上的工具 | 标准部署、最大安全性与可复现性 |
| **容器**（`container.enable = true`） | 持久 Ubuntu 容器 + `/nix/store` 挂载 | ✅ `apt`/`pip`/`npm install` 跨重启保留 | Agent 需要运行时装包、可变环境 |

要点与坑：

- **机密只能走 `environmentFiles`**：写进 `settings`/`environment` 的值会进 `/nix/store`（全局可读）。sops-nix / agenix 均可；没有机密管理器时可先用 `sudo install -m 0600 -o hermes /dev/stdin /var/lib/hermes/env` 落一个 0600 文件顶着。
- `addToSystemPackages = true` 才会让 shell 里的 `hermes` 与服务**共享** `HERMES_HOME`；否则手动跑 `hermes` 会另起一个 `~/.hermes/`。
- **容器模式的 CLI 透明路由**：开启后每条 `hermes` 命令都 exec 进容器；`HERMES_DEV=1` 可绕过跑本地检出。Podman 用户需给 `podman` 配 NOPASSWD sudo（rootful 容器）。
- **cron 的 linger 坑**：cron 作业跑在 `systemd-run --user --scope` 里，需要服务 uid 有 user manager；`createUser = true` 时模块自动设 `linger = true`（nixpkgs ≥ 25.05），自建用户要自己 `loginctl enable-linger`，否则 cron 降级或（`cron.require_restart_safe_scope: true` 时）直接失败关闭。
- 逃生阀：`services.hermes-agent.configFile = /etc/hermes/config.yaml;` 完全绕过 `settings` 生成；`hermesHomeFiles`（进 HERMES_HOME，SOUL.md/记忆必须放这）与 `documents`（进工作区，**必须显式设 `workingDirectory`**，否则模块拒绝）别放错。
- `nix build .#configKeys && cat result` 可列出全部配置叶键，把现有 config.yaml 1:1 搬进 `settings`。

### 2.4 Nix 侧注意事项

- Hermes 的 Nix 路径**没有**与 `OPENCLAW_NIX_MODE` 对等的应用层不可变语义——NixOS 模块只是"CLI 配置命令被禁、配置全走 configuration.nix"，成熟度差距明显（详见第 5 章）。
- 一个易误解点：AUR 打包里 hermes-agent 仍把 nodejs/npm 列为运行时依赖，与 flake 宣称的"无 npm"看似矛盾——这是**打包策略差异**（AUR 用系统 nodejs），不是运行时需求差异。
- 修 Nix store 路径**永远不要用 pip**；官方明令 "Do not repair a Nix store path with pip"。

---

## 3. Arch Linux

### 3.1 OpenClaw on Arch：官方脚本优先，AUR 备选

```bash
# 路径 A（推荐，supported path，通常最新稳定版）
curl -fsSL https://openclaw.ai/install.sh | bash

# 路径 B（rootless，全部落 ~/.openclaw，自带钉住的 Node 24.21.0）
curl -fsSL https://openclaw.ai/install-cli.sh | bash

# 路径 C（AUR，版本滞后约 5 天，ArchWiki 预警不稳定）
yay -S openclaw
```

AUR 三包实测状态（2026-10-13，[AUR](https://aur.archlinux.org/packages/openclaw)）：

| 包 | 版本/更新 | 维护者 | 票 | 备注 |
|---|---|---|---|---|
| openclaw | 2026.9.9-1（10-08） | ralphptorres | 5 | npm tarball，仅依赖 nodejs（npm 为 make 依赖）；比"几乎每天发版"的上游滞后约 5 天 |
| openclaw-git | 2026.9.6.r100068（09-27） | SolarAquarion | 2 | Bun 源码构建，make 依赖含 bun/cmake/gcc/libvips 等；bubblewrap 仅为 optdepends |
| hermes-agent | 0.21.7-3（**当日**） | y0uCeF | 7 | 详见 3.2 |

**ArchWiki 中文明确写道「目前 AUR 软件包均存在 bug 且不稳定」**，长期稳定运行建议官方 curl 脚本；remoteclaw 指南亦称 AUR 为社区维护、官方安装器才是 supported path。另注意 ArchWiki 称经 AUR 安装"bubblewrap 沙箱已作为依赖项安装"与 AUR 页面事实不符（稳定包依赖列表无 bubblewrap）——**以 AUR 页面为准**。

### 3.2 Hermes on Arch：AUR 包解剖（官方不支持，但机制透明）

**官方立场**：[Platform Support 页](https://hermes-agent.nousresearch.com/docs/getting-started/platform-support)把 "installs via the AUR" 列入**不支持**清单（原话温柔但明确："we might upstream patches if it helps out <3"）。

AUR 包实态（git clone aur.archlinux.org/hermes-agent 核验 PKGBUILD 全文，2026-10-13）：

- 版本 `0.21.7-3`，上游 GitHub tarball + `keep-venv-interpreter.patch`。
- **运行时依赖**：`nodejs>=22.22`、`npm`、`python>=3.14`、`uv`、`ripgrep`、`ffmpeg`、`agent-browser`；**makedepends** `cmake`；**optdepsends** chromium / google-chrome。
- 安装至 **`/opt/hermes-agent`**，`/usr/bin/hermes` 包装器 exec venv Python。
- **`keep-venv-interpreter.patch` 的真实作用**：改 `hermes_cli/_launchers.py`，对 package-manager（pacman）分发**返回 None**，从而保持 venv 解释器不被系统 Python 顶替。
- 打包约束：`/opt` 只读 + `HERMES_DISABLE_LAZY_INSTALLS=1`，**可选 extras 必须在打包时烘焙进包**，运行时懒装路径被禁。

两条路任选：

```bash
# AUR 路线（注意：官方不支持，出问题先自查）
yay -S hermes-agent

# 官方路线（受支持，PM 自管 Python 3.14，勿用 sudo）
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
# 之后：hermes setup → hermes gateway install（systemd user 服务）
```

### 3.3 OpenClaw 守护进程（Arch 及其他 Linux 通用）

```bash
openclaw onboard --install-daemon   # 或 openclaw gateway install / openclaw configure
openclaw doctor                     # 修复/迁移既有安装
```

`openclaw gateway install` 默认渲染 **systemd user unit**（`~/.config/systemd/user/openclaw-gateway[-<profile>].service`）；共享/常驻主机可用 system 级变体（见 [Gateway runbook](https://docs.openclaw.ai/gateway))。手写 unit 最小示例（[Linux 平台页](https://docs.openclaw.ai/platforms/linux)）：

```ini
[Unit]
Description=OpenClaw Gateway (profile: <profile>)
After=network-online.target
Wants=network-online.target
StartLimitBurst=10
StartLimitIntervalSec=300

[Service]
ExecStart=/usr/local/bin/openclaw gateway --port 18789
Restart=always
RestartSec=5
RestartPreventExitStatus=78
TimeoutStopSec=330
TimeoutStartSec=30
SuccessExitStatus=0 143
OOMPolicy=continue
KillMode=mixed

[Install]
WantedBy=default.target
```

坑：手写 unit **不继承** `gateway install` 写的自适应堆大小——要么用托管安装器，要么在自定义 supervisor 里显式设堆上限；`TimeoutStopSec=330` 是为 Gateway 五分钟协作式 drain 留的余量；自定义 unit 里 `WorkingDirectory=`/`EnvironmentFile=` **不要加 shell 引号**，每个绝对路径一条独立指令，`%` 要写 `%%`，路径不能以空格/制表符结尾（systemd 255 会丢尾随空白，OpenClaw 直接拒启）。

### 3.4 Arch 注意事项

- **升级纪律**：ArchWiki 记载 OpenClaw"几乎每天发新版本，某些更新会使现有配置失效"；每次更新前经验证备份（SQLite 会话库），更新后跑 `openclaw doctor`。生产考虑 extended-stable 发布线。
- OpenClaw **OOM 子进程偏置**：Linux 上 eligible 子进程会被 `/bin/sh` shim 包裹，先把自身 `oom_score_adj` 提到 `1000` 再 exec 真命令（无需特权），Gateway 本体保持 0；unit 里 `OOMPolicy=continue` 保证临时子进程被杀不牵连整个服务。验证：`cat /proc/<child-pid>/oom_score_adj`。设 `OPENCLAW_CHILD_OOM_SCORE_ADJ=0/false/no/off` 可关（仅诊断用）。**这不能替代内存调优**——VPS/容器老被杀子进程就加内存、降并发或上 systemd `MemoryMax=`。
- SSH 隧道连远端 Gateway：`ssh -N -L 18789:127.0.0.1:18789 user@gateway-host`（端口默认 18789）。
- 远端 node 加入需审批：`openclaw nodes pending` → `openclaw nodes approve <nodeRequestId>`；device 审批（`openclaw devices approve`）与 node 命令面审批是**两个独立请求 ID**。

---

## 4. 其他 Linux（Debian/Ubuntu/Fedora/openSUSE 等 glibc 发行版）

### 4.1 OpenClaw

```bash
# 标准安装（默认 npm 全局；亦可 --install-method git 源码装）
curl -fsSL https://openclaw.ai/install.sh | bash

# rootless：全部落在 ~/.openclaw（Node 装到 <prefix>/tools/node-v24.21.0 并验 SHA-256）
curl -fsSL https://openclaw.ai/install-cli.sh | bash
# 只想要 Node 不想装 OpenClaw：install-cli.sh --node-only（拒绝 musl 与 FreeBSD）

# 装完验证
openclaw --version && openclaw doctor && openclaw gateway status --json
```

Linux  companion 桌面 app（稳定版随主发布）：GitHub releases 上有 `OpenClaw-<version>-amd64.deb` 与 AppImage（带 `SHA256SUMS.linux-app.txt`）；AppImage 需 FUSE 2（Ubuntu 24.04+ 为 `libfuse2t64`），没有就 `APPIMAGE_EXTRACT_AND_RUN=1` 跑。**注意只有含这些资产的 release 才有 Linux app**，新 Gateway 发布不等于新 Linux app 可用。

安装流细节（[Installer internals](https://docs.openclaw.ai/install/installer)）：五步 = 探测 OS → 确保受支持 Node（apt/dnf/yum 走 NodeSource 装 Node 24 LTS；**RPM 自带 Node 链接不安全 SQLite 时保留原包、另建用户态 Node**）→ 确保 Git → npm/git 安装 → 后置任务（onboarding、刷新重启 gateway 服务、`doctor --fix`；升级态修复失败即退出非零）。npm 11.16+/12 会对 npm 解析到的 OpenClaw 候选身份加 `--allow-scripts`；本地 `.tgz` 安装在 npm 12 上需要**逗号 free 的路径**（npm 用逗号分隔 lifecycle 批准项）。

### 4.2 Hermes

```bash
# 一键源码安装（POSIX；自带 uv 钉版本，不用你 PATH 上的 uv）
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# 跳过浏览器/计算机使用工具（选择会被记住，update 不装回）
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-browser --skip-computer-use

# CI/无人值守
... | bash -s -- --non-interactive

# 装完
source ~/.bashrc
hermes setup            # 或 hermes setup --portal 一个订阅打通 300+ 模型与工具网关
hermes gateway install  # systemd user 服务；常驻需管理员先 loginctl enable-linger
```

安装布局：源码 `~/.hermes/hermes-agent/`，launcher `~/.local/bin/hermes`（包装器），用户数据 `~/.hermes/`（`HERMES_HOME` 可改；POSIX 脚本 `--dir` 单独选源码检出目录）。修应用**不要删数据根目录**。

系统要求（官方口径 2026-10-13）：Python 3.14 运行时（PM 自管）；glibc + systemd + FHS（官方测试环境为最新 Ubuntu 与 WSL2）。社区镜像 hermes-agents.net 的"2GB 最低/4GB+ 推荐、Python 3.10/3.11"页面**已过时**，仅内存部分可参考，Python 部分以官方 3.14 为准；该社区一键脚本（自动装 uv、建 venv、配 PATH、明示"不要 sudo"）思路与官方一致但同样滞后。

### 4.3 服务与更新

| | OpenClaw | Hermes |
|---|---|---|
| 用户服务 | `openclaw gateway install`（systemd user unit） | `hermes gateway install`（launchd on macOS / systemd user on Linux） |
| 更新 | `openclaw update`（自动识别 npm/pnpm/Bun/git 安装形态） | `hermes update`（managed source checkout） |
| 更新前 | **经验证备份**（SQLite 会话库；官翻「自动配置副本不算全量备份」） | 自动预更新快照（`updates.pre_update_backup`: quick/full/off，快照失败只警告不阻断） |
| 诊断 | `openclaw doctor` / `--fix` / `triage --json` | `hermes doctor` / `hermes config check` + `hermes config migrate` |
| 回滚 | 见 §10 | 更新前后语法校验失败自动 `git reset --hard <pre-pull-sha>`，保证 shell 可启动 |

Hermes 更新期 gateway 行为（值得知道的细节）：Linux/macOS 上 `hermes update` 在首次改动检出前**先暂停**该安装的所有 gateway，依赖就绪后重启（bot 离线窗口 ≈ git 更新 + 依赖同步）；重启是 drain-first（拒新回合、等在飞工作完成，`agent.restart_after_turn_timeout` 默认 30 分钟封顶）；被暂停的集合会记账，更新被杀则下次 `hermes` 命令自动拉起。

---

## 5. macOS

### 5.1 OpenClaw

两条产品形态：

**(a) OpenClaw.app 菜单栏伴侣（推荐桌面用户）**

- **要求 macOS 26.2 (Tahoe) 或更高**（含原生 `openclaw-mac` helper 与 Voice Wake）。
- 从 [GitHub releases](https://github.com/openclaw/openclaw/releases) 取 `OpenClaw-<version>.dmg`（首选）或 `.zip`；**有些 release 只发 CLI/Windows 资产**，没有 macOS 资产就取最近一个有的。
- 首启自动准备 bundled runtime、在本机起 Gateway、开 onboard；**不会自动加入发现的 Gateway**。本机 CLI/Gateway 管理走 launchd；只装 app 不装 CLI 也能用 local 模式（app 的 Mac node 两种模式都用自带私有运行时）。
- 自动选型顺序：已存 OpenClaw auth profiles → Codex 登录 → Claude CLI 登录 → `OPENAI_API_KEY` → `ANTHROPIC_API_KEY` → Ollama/LM Studio/llama.cpp 已加载模型。**Apple Foundation Models 永不被选为主模型**。复用 Codex 登录时与 Codex 共享会话（想隔离选 "Use a separate login"）。
- 桌面共享默认开（`This Mac → Capabilities → Desktop sharing`），在系统设置里启用 Screen Sharing 并批准 node 的 desktop capability。

**(b) CLI / Gateway（无界面或服务器）**

```bash
curl -fsSL https://openclaw.ai/install.sh | bash     # 缺 Node 时经 Homebrew 装 Node 26
# Bun 运行时：install.sh --runtime bun（macOS 会自动确保 Homebrew SQLite 并导出 HOMEBREW_PREFIX，
# 装 OpenClaw 前先验证 SQLite；可用 OPENCLAW_SQLITE_LIBRARY 覆盖）
openclaw onboard --install-daemon                    # launchd 服务
```

- Node CLI 的 OS 门槛：官方 Node 24/26 的 macOS 二进制要求 **macOS 13.5+**（Node 支持的最老 release）；老版本 Mac 可能能跑但不受支持，且**跑得动 CLI 不等于 .app 兼容**。
- 状态目录别放 iCloud 同步文件夹（官方有专节 "state directory on macOS"）。

### 5.2 Hermes

- **Tier 1 = Apple Silicon only**。Intel x86_64 桌面包**默认不构建**——只有用 `release.py release --include-macos-intel` 剪的 release 才带，且装了的 Intel Mac 桌面包要等下一个带 Intel 的 release 才有更新。
- DMG：拷贝 `Hermes.app` 到 Applications；自动更新用 ZIP 制品里的签名 app。`Hermes-Setup` 引导安装器是另一回事（下载源码现场构建桌面 app），且仅 Apple Silicon。
- Intel Mac 的正路：装 CLI（`install.sh`）后跑 `hermes desktop`，或找带 `darwin-x64` bundle 的 release。
- 更新：`hermes update`（managed source checkout）/ 桌面 app 的 Update 控制（electron-updater/Squirrel.Mac）。

### 5.3 macOS 注意事项

- OpenClaw .app 与 Gateway 的更新是**协调更新**：app 拥有本地 launchd Gateway 时，Sparkle 先更新 app，重启后自动把 Gateway 更新到匹配版本；`Update Gateway` 按钮只走远端/手动管理 Gateway 的常规更新流。更新卡片命名准确（"Update Mac app + Gateway" vs "Update Gateway"），误点不会启动 Sparkle。
- OpenClaw Gateway 协议版本被 app 拒时会明报两侧版本、告诉你哪边要升级。
- 备份：Hermes 换机可用 `hermes import` 全量备份或 `hermes profile import` 单 agent；**profile 导出按设计不含凭据**，别当全量备份用。

---

## 6. Windows 10/11 原生

### 6.1 OpenClaw

**(a) 桌面 app（推荐）**

- 从 releases 页下载 **Windows x64 NSIS 安装器** `OpenClaw-<version>-windows-x86_64.exe`，安装后从开始菜单启动；Control UI 用 WebView2（安装器按需 provisioning）。
- **app 用自带私有 Bun 运行时和包管理器，不要求系统 Node/npm**；但本地 Gateway 需要**该 app 钉住版本里的签名 Windows Bun 运行时**。旧 app 报 "This app does not include a signed Windows Gateway runtime" 时：升级到带签名运行时的 app 版本，或连远端 Gateway——**装系统 Node 不影响这个准入策略**。
- 安装器 Authenticode 签名由 release  owner 单独启用，未签名安装器 Windows 会显示未知发布者警告（app 自身更新走 Tauri 签名独立校验）。

**(b) PowerShell CLI**

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
openclaw --version; openclaw doctor; openclaw gateway status --json
# 服务安装（Scheduled Task，S4U 主体：开机+登录触发、免存密码、可登录前运行）
openclaw gateway install
# 纯 CLI 不要托管服务：
openclaw onboard --non-interactive --accept-risk --skip-health
openclaw gateway run
```

- app 管理的 CLI launcher 是 `%USERPROFILE%\.openclaw\bin\openclaw.cmd`（不在 PATH 就用全路径调用）。
- **注册开机任务要从目标服务用户的 elevated 终端跑安装**；账号识别不了或建任务被拒时退化为桌面任务/Startup 文件夹（需交互登录，做不到无人值守开机启动）。`openclaw doctor --fix` 会把老 Gateway 定义从交互登录迁到无人值守启动（先备份定义和 launcher）。
- 更新后若 launcher 没刷新，跑 `openclaw gateway install --force` 重写 `gateway.cmd`；pnpm 全局装的新 launcher 指向已验证的稳定 `node_modules/openclaw` 链接。
- 日志重定向要**整体加引号**：`>> "%USERPROFILE%\.openclaw\logs\gateway-stdout.log" 2>&1`；不加引号的环境展开会在 Gateway 参数里留文件名碎片，OpenClaw 会拒绝终止一个所有权无法验证的监听器。
- 已知坑：**2026.9.4 的 Windows updater 在服务交接里留着旧数据库读取器**，目标状态迁移超 schema 17 时激活后回调会失败。从 9.4 升级：等 updater 退出看结果，建 verified backup，用**独立 shell 的手动包管理流程**升（保持原服务账号、包前缀、profile 与 state/config 覆盖），换包前经服务 owner 停 Gateway，跑新 Doctor 再启动验证。**别降 schema 标记、别用旧构建跑迁过的数据。**

**(c) Windows Hub（可选伴侣 app）**：WinUI 原生，Win10 20H2+/Win11，免管理员，自带 x64/ARM64 签名安装器；提供本机 app 自有 **WSL Gateway** 一键配置（不动你已有的 Ubuntu 发行版）、node 模式（屏幕/摄像头/通知/受控 `system.run`）与本地 MCP server 模式。

### 6.2 Hermes（原生，无 WSL/Cygwin/Docker）

```powershell
# 一键安装（无需管理员；装到 %LOCALAPPDATA%\hermes\，hermes 进 User PATH）
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
# 或 windows-native 指南给的等价入口：
# iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)

# 带参数（scriptblock 方式）
& ([scriptblock]::Create((irm https://hermes-agent.nousresearch.com/install.ps1))) -NonInteractive -Branch main

Get-Command hermes    # 应指向 AppData\Local\hermes\bin\hermes.exe
hermes --version
hermes gateway install   # schtasks ONLOGON（LIMITED，无 UAC）+ Startup 文件夹 VBS 兜底
```

安装器八步：找 Git（没有就暂存钉住的 Git for Windows）→ 克隆分支 → 引导 uv 建初始 Python 环境 → PM 准备 Python 3.14 与工具与 `all` extra → 在数据 home 的 `bin` 铸 launcher 并加 User PATH → 准备配置并跑交互 setup（除非 `-NonInteractive`）→ 可选构建桌面 → 写完成标记。**`-NoVenv`/`-Tag` 当前不接受**；`-SkipSetup` 是 `-NonInteractive` 的废弃别名。

Windows 专属机制（[Windows Native 指南](https://hermes-agent.nousresearch.com/docs/user-guide/windows-native)）：

- **UTF-8 stdio shim**：每个入口早期调 `configure_windows_stdio()`——控制台切 CP_UTF8、stdio 重配 UTF-8、设 `PYTHONIOENCODING=utf-8`/`PYTHONUTF8=1`、`EDITOR` 未设时置 `notepad`。不这么干的话带 Unicode 的 banner/技能描述直接 `UnicodeEncodeError`。`HERMES_DISABLE_WINDOWS_UTF8=1` 可退回（仅调试用）。
- **编辑器**：`Ctrl-X Ctrl-E` / `/edit` 默认 notepad（阻塞式）；VS Code 必须 `$env:EDITOR = "code --wait"`，少了 `--wait` Hermes 拿回空缓冲。
- **终端走 Git Bash**（与 Claude Code 同策略）；**MinGit 不算数**，要"Git for Windows with Bash"。
- **gateway 自启**：`schtasks /Create /SC ONLOGON /RL LIMITED /TN Hermes_Gateway`（无 UAC）；被组策略挡就退化为 Startup 文件夹里的 `Hermes_Gateway.vbs`（wscript 隐藏跑；用 VBS 而非 cmd 快捷方式是因为登录时分配的控制台可能收到关闭事件把 gateway 掐死）。两者只保留一个。进程以 **`pythonw.exe` 分离启动**（`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW | CREATE_BREAKAWAY_FROM_JOB`），免疫同进程组 Ctrl+C 广播。
- **不用 Windows Service 的原因**：服务要管理员、绑定机器启动而非用户登录；典型用户要的是"登录即有、登出即无"。真要用服务自己上 nssm/sc，且命名/路径要能被 `hermes update` 识别为 Hermes 自有。
- **MSIX 桌面包另成一系**：需 **Win11 22H2+**（Win10 源码脚本支持 ≠ MSIX 支持 Win10）；经 `.appinstaller` 装签名 bundle；execution aliases 暴露 hermes/hermes-agent/hermes-acp。
- **PATH 刷新**：安装器经 `[Environment]::SetEnvironmentVariable` 写 User PATH，**已开着的终端不生效**——开新窗口，别手拼 `$env:PATH`。
- **机密放 `%LOCALAPPDATA%\hermes\.env`**（即 HERMES_HOME），不要塞 User 环境变量（那等于给每个 Windows 进程看）。
- ARM64 原生 Windows 的依赖裁剪：排除 `google-chat` SDK extra 与 openWakeWord（默认 Sherpa 唤醒）、Faster-Whisper STT（用云端或命令式 STT；Porcupine 可替代）；Chromium/agent-browser 可能走 x64 模拟。

### 6.3 Windows 注意事项

- **Hermes 原生与 WSL2 数据互不相通**：原生在 `%LOCALAPPDATA%\hermes`，WSL 在 `~/.hermes`，可共存。功能矩阵上两者几乎打平（WSL 仅本地 Ollama 类需经 WSL 网络、终端 pane 用 POSIX PTY vs ConPTY）。
- 删 `%LOCALAPPDATA%\hermes` 根目录 = 删用户数据且可能影响共享它的其他安装——**修应用用卸载命令，别删根**。
- 远端 WebChat 要 HTTPS 或 localhost；自签证书要么导进 Windows 信任，要么 SSH 隧道到 localhost。

---

## 7. WSL2（OpenClaw 与 Hermes 共用）

WSL2 是 Windows 上"最 Linux 兼容"的 Gateway 运行时。Hermes 把 WSL2 列为 Tier 1；OpenClaw install.sh 亦支持 WSL。

```powershell
# 1) 装 WSL（PowerShell 管理员）
wsl --install -d Ubuntu-24.04

# 2) WSL 内启用 systemd
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true
EOF
wsl --shutdown    # 回 PowerShell 执行，重启 WSL 生效
```

```bash
# 3) WSL 内按 Linux 路径装（二选一）
curl -fsSL https://openclaw.ai/install.sh | bash
openclaw gateway status
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
hermes gateway install
```

**无人值守开机自启（官方配方，含两个 2026 年新变化）**：

```bash
# WSL 内
sudo apt-get install -y dbus-x11
sudo loginctl enable-linger "$(whoami)"
openclaw gateway install        # 或 hermes gateway install
```

```powershell
# Windows PowerShell（管理员）
schtasks /create /tn "WSL Boot" /tr "wsl.exe -d Ubuntu --exec dbus-launch true" /sc onstart /ru "$env:USERNAME"
# Ubuntu 换成 wsl --list --verbose 看到的发行版名
```

两个与旧配方不同的点（官方 note）：

1. **`dbus-launch true` 而不是 `/bin/true`**：WSL ≥ 2.6.1.0 有回归（microsoft/WSL#13416），最后一个客户端退出后 15–20 秒 idle-terminate 整个发行版，linger 也拦不住；`dbus-launch true` 留一个 init 的子进程续命。
2. **`/ru "$env:USERNAME"` 而不是 `/ru SYSTEM`**：按用户的 WSL 发行版对 SYSTEM 账户不可见，任务"成功"但发行版根本没起。

验证与 LAN 暴露：

```bash
systemctl --user is-enabled openclaw-gateway.service   # WSL 内
```

```powershell
# 把 Windows 端口转发到当前 WSL IP（WSL IP 重启会变，需时刷新）
$Distro = "Ubuntu-24.04"; $ListenPort = 2222; $TargetPort = 22
$WslIp = (wsl -d $Distro -- hostname -I).Trim().Split(" ")[0]
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=$ListenPort connectaddress=$WslIp connectport=$TargetPort
New-NetFirewallRule -DisplayName "WSL SSH $ListenPort" -Direction Inbound -Protocol TCP -LocalPort $ListenPort -Action Allow
```

注意：远端 node 要指向**可达的 Gateway URL**，不是 `127.0.0.1`。

---

## 8. Docker / 容器

### 8.1 OpenClaw：`ghcr.io/openclaw/openclaw`

- 主镜像 `ghcr.io/openclaw/openclaw`（Docker Hub 亦有 `openclaw/openclaw`）；变体：slim / browser / extended-stable。
- 引导走 `./scripts/docker/setup.sh`；**端口 18789**；健康探针 `/healthz`、`/startupz`、`/readyz`。
- `--offline` 支持气隙安装。
- **镜像升级时 entrypoint 自动跑 `openclaw doctor --fix`**，挂载状态无法安全修复时拒绝启动；容器镜像更换走 [Upgrading container images](https://docs.openclaw.ai/install/docker)。
- 提醒：实验性 `openclaw fleet` 命令**已移除**；多租户容器生命周期移交你自己的 Docker/Podman 工具链（升级主机 CLI 不动已有 tenant 容器），各租户单独备份（容器环境里可能有 Gateway token，当机密管）。

### 8.2 Hermes：`nousresearch/hermes-agent`

```sh
# 首次：跑 setup 向导（API keys 写进 ~/.hermes/.env）
mkdir -p ~/.hermes
docker run -it --rm -v ~/.hermes:/opt/data nousresearch/hermes-agent setup

# 常驻网关模式（8642 = OpenAI 兼容 API + 健康端点；要 dashboard/外部工具才必须开）
docker run -d --name hermes --restart unless-stopped \
  -v ~/.hermes:/opt/data -p 8642:8642 \
  nousresearch/hermes-agent gateway run

# 带 dashboard（9119）
docker run -d --name hermes --restart unless-stopped \
  -v ~/.hermes:/opt/data -p 8642:8642 -p 9119:9119 \
  -e HERMES_DASHBOARD=1 \
  nousresearch/hermes-agent gateway run
```

- 标签：`latest`/`stable`（过稳定门的镜像）/`main`（开发）/`X.Y.Z`（钉版本用 digest）。镜像 Python 环境跟随 `pyproject.toml`+`uv.lock`（当前 3.14）；**不含 Electron 桌面**。
- **`/opt/data` 是唯一状态源**（映射宿主 `~/.hermes/`）：`.env`、`config.yaml`、`SOUL.md`、`sessions/`、`memories/`、`skills/`、`cron/`、`logs/`、以及给工具子进程用的 per-profile HOME（`home/`）。镜像本身无状态，**换镜像升级不丢配置**。
- **s6 监管**：`gateway run` 崩溃数秒内自动重启；CMD 本体是 `sleep infinity` 心跳，`docker stop` 仍能干净关闭。想退回"gateway 即主进程、容器退出=gateway 退出"的旧语义：`--no-supervise` 或 `HERMES_GATEWAY_NO_SUPERVISE=1`（仅早期 tini 镜该语义是默认）。**Docker 安装不支持 `hermes update`**——升级=拉新镜像、用同一数据挂载重建容器。
- **API server**：默认关；`API_SERVER_ENABLED=true` 开，`API_SERVER_HOST=0.0.0.0` 才出容器回环，`API_SERVER_KEY` 最少 8 字符（`openssl rand -hex 32`）。公网开端口=自带风险，掂量清楚。
- **Dashboard 认证门（2026-06 加固后的硬规则）**：非回环绑定 + 注册了 `DashboardAuthProvider` 才启动；**没有任何 provider 且非回环绑定 = 启动即失败关闭**。三种 provider：用户名密码（`HERMES_DASHBOARD_BASIC_AUTH_USERNAME/PASSWORD`，可加 `_SECRET` 稳会话）、Nous Portal OAuth（设 `HERMES_DASHBOARD_OAUTH_CLIENT_ID`）、自托管 OIDC（`HERMES_DASHBOARD_OIDC_ISSUER`+`_CLIENT_ID`）。`HERMES_DASHBOARD_INSECURE=1` **已是废弃 no-op**（背景：2026-06 有扫描器打暴露的 dashboard/API server 驱动 agent 种 SSH 后门）。反代场景在 config.yaml 里配 `dashboard.public_url` + `trusted_proxies`（精确 IP 或有界 CIDR；`*`/`0.0.0.0/0`/`::/0` 直接被拒）。
- **virtiofs/9p 的 WAL 损坏坑（Docker Desktop macOS/Windows、OrbStack、Podman）**：跨 VM 边界的 bind mount 不保证 `state.db-shm` 一致性，并发写会**静默损坏** WAL 库（主文件还能过 integrity_check）。v2026.9.14 起的对策：新库检测到此类挂载**直接建 DELETE journal 模式**并记一次警告；已有 WAL 库**不 live 降级**——停掉所有 Hermes 进程后跑一次性离线转换（镜像内无 sqlite3 shell，用自带 Python）：
  ```sh
  docker exec hermes python3 -c "import sqlite3; print(sqlite3.connect('/opt/data/state.db').execute('PRAGMA journal_mode=DELETE').fetchone()[0])"
  # 并在 config.yaml 设 database.journal_mode: delete 防止被切回
  ```
  或者**换命名卷**（`-v hermes-data:/opt/data`，落在 VM 自己的 ext4 上，WAL 正常）。NFS/SMB/通用 FUSE 不在自动检测范围，那些上面**显式**设 `database.journal_mode: delete`。
- **配对审批必须 `-u hermes`**：官方镜像用 gosu 降权到 `hermes`（uid 10000），而 `docker exec` 默认 root——root 建的审批文件是 `0600 root:root`，gateway 读不了，**审批被静默忽略**（issue #10270）：
  ```sh
  docker exec -u hermes hermes-agent hermes pairing approve telegram ABC12DEF
  ```
  已经用 root 跑过？重启容器，entrypoint 下次启动会修属主。
- **`/opt/hermes` 不可变**（root 属主、运行时用户只读）：agent 自进化范围限于 `/opt/data` 下的 skills/memory/plugins/config；核心改动走 PR + 换镜像。`docker exec hermes hermes ...` 的 shim 会降回运行时用户；确需 root 用 `HERMES_DOCKER_EXEC_AS_ROOT=1` 一次性。
- 多 profile：容器内**每个 profile 是 first-class s6 服务**（`hermes profile create` 动态注册 `/run/service/gateway-<name>/` 槽位，崩溃自动重启、日志轮转、重启后按 `gateway_state.json` 恢复）；推荐**一个容器承载全部 profile**。宿主侧对 bind mount 建的 profile 没有槽位（宿主进程够不着容器的 `/run/service`），进容器 `hermes -p <name> gateway start` 即用即注册。
- 技能 CLI 的凭据在 `~` 下的（如 xurl 的 `~/.xurl`）：官方布局里即 `/opt/data/home/.xurl`，手工认证要带 `HOME=/opt/data/home`。
- **绝不要两个 Hermes gateway 容器同时挂同一个数据目录**（会话文件与记忆库不是为并发写设计的）。

### 8.3 容器注意事项

- 用浏览器版 VPS 控制台（Hetzner Cloud 等）粘贴 `docker run` 命令是官方点名的大坑：`:` 变 `;`、`@` 错渲染、非英语键盘更糟，`-v ~/.hermes:/opt/data`、`-e KEY=value`、API key 会被**静默污染**。**走 SSH**；非要用控制台就手打并逐个核对 `:`/`@`/`=`/`/`。
- Hermes 的 docker 终端后端沙箱是另一回事（agent 在宿主跑、命令进持久沙箱容器）：硬编码 `--cap-drop ALL` + 按需 `DAC_OVERRIDE/CHOWN/FOWNER`、`no-new-privileges`、pids-limit 256、tmpfs 限额；`docker_forward_env` 是显式白名单，**加进去的变量容器内代码可读可外传**，只放任务型凭据。生产网关优先 docker/modal/daytona/vercel_sandbox 后端做隔离（可免掉危险命令审批）。

---

## 9. Android / Termux（仅 Hermes；当前损坏）

- **官方 danger 横幅：Termux 包现在跑不了**，修复中；下面步骤可能失败或装上一个跑不起来的包。
- 仅 **aarch64**；签名 APT 仓库（`https://hermes-assets.nousresearch.com/releases/termux/stable`，key 指纹 `C572 B5FD D1A2 9CCF A9A9 12B6 840B 0848 E139 156D`，对不上就停、别绕过验签）：
  ```bash
  pkg install curl gnupg
  mkdir -p "$PREFIX/etc/apt/keyrings"
  curl -fsSL https://hermes-assets.nousresearch.com/releases/termux/stable/key.asc -o "$PREFIX/etc/apt/keyrings/hermes-agent.asc"
  # 核指纹后：
  printf '%s\n' "deb [signed-by=$PREFIX/etc/apt/keyrings/hermes-agent.asc] https://hermes-assets.nousresearch.com/releases/termux/stable hermes-stable main" > "$PREFIX/etc/apt/sources.list.d/hermes-agent.list"
  pkg update && pkg install hermes-agent
  hermes setup && hermes --tui
  ```
- 包内自带 Python 3.14（bionic pin，不需要 Termux 的 python/nodejs 包）；**无 systemd/launchd/schtasks**，gateway 跑在 Termux 会话里（`nohup hermes gateway run >> "${HERMES_HOME:-$HOME/.hermes}/logs/gateway.log" 2>&1 &`）；**Android 会杀后台**，电池优化豁免 + `termux-wake-lock` 不保证持久。
- `hermes update` 拒绝改 APT 拥有的安装（会打印 `pkg upgrade` 命令）；无 Electron/本地 Chromium/computer-use；无 `nemo-relay` exporter。
- 发行门：Termux 包**默认不构建**，只有 `release.py release --include-termux` 剪的 release 才更新 APT 通道。

---

## 10. 更新、备份与回滚速查

| 安装形态 | 更新方式 | 备份/回滚要点 |
|---|---|---|
| OpenClaw npm/pnpm/Bun 全局 | `openclaw update`（自动识别形态；升级时自动跑 `doctor --fix`，失败即退出非零） | 重大更新前**建 verified backup**（自动配置副本不算）；`extended-stable` 发布线可钉 |
| OpenClaw 源码 checkout | 同 `openclaw update` / 重跑安装器 `--install-method git` | 同上 |
| OpenClaw < 2026-07 老安装 | **先升 `2026.9.5` 桥接版**跑 Doctor 迁移，再升 latest | 老库已被新 schema 升过时，用兼容的更新前备份走降级恢复；**旧版本打不开新 schema** |
| OpenClaw macOS app | app 自己的更新器（Sparkle，跟随 Gateway `update.channel`） | app 拥有本地 Gateway 时协调更新；extended-stable pin 不被自动修复降级 |
| OpenClaw Windows 服务 | `openclaw update`（Scheduled Task 检查/重启有 60s 预算，超时跳过自动重启需手动） | 更新 preflight 超时会保留服务定义、跳过重启——用 `openclaw gateway status --deep` 核查后手动重启 |
| OpenClaw Docker | 拉新镜像重建（entrypoint 自动 `doctor --fix`） | 数据在挂载卷；tenant 容器单独记账备份 |
| Hermes 源码检出 | `hermes update`（默认 stable 通道=最新 release 精确 commit；`--set-channel main` 追主线） | 每次更新自动预更新快照（quick/full/off）；拉取后**九个关键启动文件语法校验失败自动回滚**到 pre-pull SHA |
| Hermes 桌面包（Win MSIX/商店、macOS） | app 的 Update 控制 / Store | stable 与 canary 是**两个独立应用**（独立状态、独立更新，`hermes-canary` 命令）；一次性 commit  bundle **永收不到更新** |
| Hermes Docker | 拉新镜像 + 同数据挂载重建 | `/opt/data` 即全部状态；**不支持 `hermes update`** |
| Hermes Nix | 更新 flake/profile 并 rebuild | 回滚走 Nix 世代 |
| Hermes Termux APT | `pkg update && pkg upgrade hermes-agent` | `hermes update` 拒绝动 APT 安装 |
| Hermes on Arch（AUR，不受支持） | 跟 pacman | 官方路线：重跑 install.sh 覆盖同一检出 |

补充机制：

- `hermes update --check` 只比对不动手；`hermes update --plan` 打印全机 fleet 预览（安装类型、各 profile 服务、监管器、运行版本、重启机制），**只读、可对live 集群安全跑**。每次真更新写机器可读回执到 `~/.hermes/logs/update_receipts/`（留 20 份，`latest.json` 指向最新）；更新后会逐 profile 核对运行中 gateway 的代码版本，还在跑旧代码的会大声报出来。
- Hermes  partial clone 的两个 git 坑（都有自动修复）：Git ≥ 2.53 的 `should_include_obj` 崩溃（`hermes update` 自动标记 pack 重试一次）；2026-09 下旬的 treeless（`--filter=tree:0`）检出被老 Desktop 反复路径过滤走history，**有报告把磁盘涨到 434GB**——`hermes update` 现在会在拉取后自动 `git fetch --refetch --filter=blob:none`（约 120MB）一次性转换。
- OpenClaw CLI 在不受支持 Node 上的白名单命令：`--version`、`--help`、`gateway status`、`doctor --lint`、`update status`、`triage --json/--non-interactive`；修复类操作与 Gateway 启动仍需受支持运行时。

---

## 11. 故障排查速查

| 症状 | 因果 | 修法 |
|---|---|---|
| OpenClaw 起手报 unsupported Node / SQLite | Node 不在 24.16+/26.1+，或链接 SQLite 未修 WAL-reset | 按 §1.1 升 Node；RPM 系让安装器自建用户态 Node；Alpine 换 `node:26-alpine` 容器或 glibc 主机 |
| npm 全局装成功但 CLI 仍报不受支持 Node | npm 可能跳过 preinstall 检查 | 装完必跑 `openclaw --version` + `openclaw doctor` 实检 |
| Hermes 装完 `hermes` 找不到 | PATH 未刷新（Windows 固有；POSIX 需 `source ~/.bashrc`） | 开新终端；Windows 别手拼 `$env:PATH`；`Get-Command hermes -All` 查 alias 遮蔽（MSIX） |
| Hermes Linux 报缺 `libatomic.so.1` | 精简镜像没带 | 装 `libatomic1`/`libatomic`/`gcc-libs`（按发行版）；无 sudo 找管理员 |
| Hermes Windows 乱码/`UnicodeEncodeError` | 控制台代码页非 UTF-8 | 升级到带 stdio shim 的版本；`HERMES_DISABLE_WINDOWS_UTF8=1` 仅作对照实验 |
| Windows Gateway 登录前不起 | S4U 任务需 elevated 终端注册；退化路径要交互登录 | 以目标用户 elevated 重装；`openclaw doctor --fix` 迁移旧定义 |
| WSL 定时任务"成功"但发行版没起 | `/ru SYSTEM` 看不到按用户发行版；WSL ≥2.6.1.0 idle-terminate | `/ru "$env:USERNAME"` + `dbus-launch true`（§7） |
| Hermes 容器里 pairing 审批无效 | root 建的 0600 文件 gateway 读不了 | `docker exec -u hermes ...`；或重启容器让 entrypoint 修属主 |
| Hermes Docker 数据疑似损坏（integrity_check 却过） | virtiofs/9p 上 WAL 静默损坏 | §8.2 离线转 DELETE 模式或换命名卷 |
| Hermes dashboard 起不来 | 非回环绑定无 auth provider，fail closed | 配 basic auth/OAuth/OIDC，或 `HERMES_DASHBOARD_HOST=127.0.0.1` + SSH 隧道 |
| OpenClaw 更新后集成挂 | 高频发版的回归密度（社区自述约 25% 更新打挂集成） | 事前 verified backup；等一两个补丁（官方自己也这么建议）；`openclaw doctor` / `triage` |

---

## 12. 引用来源（均于 2026-10-13 核验）

**OpenClaw 官方**

- 安装总览 / Node 兼容性：https://docs.openclaw.ai/install 、https://docs.openclaw.ai/install/node
- 安装器内部（install.sh / install-cli.sh / install.ps1）：https://docs.openclaw.ai/install/installer
- 更新与回滚：https://docs.openclaw.ai/install/updating
- Linux 平台（systemd unit / OOM / SSH / 桌面 app .deb+AppImage）：https://docs.openclaw.ai/platforms/linux
- Windows 平台（桌面 app / Hub / WSL2 / Scheduled Task）：https://docs.openclaw.ai/platforms/windows
- macOS app（26.2 Tahoe+ 要求 / Gateway 模式 / 更新）：https://docs.openclaw.ai/platforms/macos
- Docker：https://docs.openclaw.ai/install/docker
- Nix（中文页）：https://docs.openclaw.ai/zh-CN/install/nix
- v2026.9.2 发布说明（本地模型 8 GiB 底线 / 共享 Gateway 警告）：https://docs.openclaw.ai/releases/2026.9.2
- Releases（各平台安装资产）：https://github.com/openclaw/openclaw/releases
- Node `node:sqlite` NUL 截断（版本门槛根因）：https://github.com/nodejs/node/issues/61954

**Hermes 官方**

- Installation：https://hermes-agent.nousresearch.com/docs/getting-started/installation
- Platform Support（Tier 1/2 与不支持清单）：https://hermes-agent.nousresearch.com/docs/getting-started/platform-support
- Nix & NixOS Setup：https://hermes-agent.nousresearch.com/docs/getting-started/nix-setup
- Updating & Uninstalling：https://hermes-agent.nousresearch.com/docs/getting-started/updating
- Windows (Native) Guide：https://hermes-agent.nousresearch.com/docs/user-guide/windows-native
- Docker Setup：https://hermes-agent.nousresearch.com/docs/user-guide/docker
- Termux：https://hermes-agent.nousresearch.com/docs/getting-started/termux
- 配对审批 root 坑 issue #10270：https://github.com/NousResearch/hermes-agent/issues/10270
- 仓库：https://github.com/NousResearch/hermes-agent

**包管理与社区**

- AUR：https://aur.archlinux.org/packages/openclaw 、https://aur.archlinux.org/packages/openclaw-git 、https://aur.archlinux.org/packages/hermes-agent
- ArchWiki 中文 OpenClaw 页：https://wiki.archlinux.org.cn/title/OpenClaw
- WSL #13416（idle-terminate 回归）：https://github.com/microsoft/WSL/issues/13416 ；讨论 #9245
- remoteclaw Arch 教程：https://remoteclaw.com/tutorials/local/arch-linux.html
- 社区镜像（Python 口径已过时，仅内存要求部分参考）：https://hermes-agents.net/zh-cn/install/linux/

> 本指南与主报告口径冲突时，以本指南与英文官方页为准（中文文档站存在已确认的滞后，见 §1.3）。抓取失败项与未核实结论见主报告"待完善事项"。
