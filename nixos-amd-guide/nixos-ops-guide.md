---
type: Checklist
---

# NixOS 运维指南（26.05 版）

### 面向初学者与游戏玩家 · 每个设置都解释「为什么」· 全部结论附出处

| 项 | 值 |
|---|---|
| 适用版本 | NixOS 26.05「Yarara」 |
| 26.05 发布日期 | 2026-05-30 |
| 26.05 安全支持截止 | 2026-12-31 |
| 下一版本 | NixOS 26.11「Zokor」（2026 年 11 月底） |
| 文档核实日期 | 2026-10-12（含第二轮源码级复核 + 第四轮 `nixos-26.05`/`nixos-unstable` 双分支逐包实测） |
| 文档版本 | 1.4 |
| 出处基准 | 官方手册 / nixpkgs `nixos-26.05` 分支源码 / 官方 Wiki / 官方 Discourse / 生态站 API 实测 |

**证据分级说明**（全文遵守）：

- `[官方]` = nixos.org 手册、nix.dev、nix-community 官方文档、官方 API 文档
- `[官方选项]` = 官方手册/选项数据库中的选项定义页
- `[官方论坛]` = 官方 Discourse 论坛帖（一手社区讨论，非官方结论）
- `[Wiki]` = wiki.nixos.org / nixos.wiki 社区 Wiki
- `[仓库]` = 项目自身 GitHub README / issue / 源码
- `[社区]` / `[社区实证]` = 第三方社区讨论、博客、实测报告
- `[媒体]` = 新闻报道（如 LWN）
- `[核实]` / `[核实·源码]` / `[核实·Wiki]` = 本文撰写时 **curl 实测** 或**逐条比对源码/Wiki** 确认
- `[未核实]` / `[未找到]` = 无法从一手来源确认，已明确标注

---

## 目录

1. [NixOS 的心智模型：三个概念解释一切](#一)
2. [三条配置路线：configuration.nix / flakes / home-manager](#二)
3. [从零装机：默认配置逐段解释](#三)
4. [游戏玩家专章](#四)
5. [NixOS 没有的软件怎么跑（AppImage / 官方二进制 / node / npm）](#五)
6. [稳定基座 + 滚动组件（混合版本策略）](#六)
7. [长期运维与跨版本升级](#七)
8. [Nix 生态查询工具链（search.nixos.org / NixHub / FlakeHub / Noogle / Devbox）](#八)
9. [LLM 辅助管理 NixOS](#九)
10. [附录：命令速查 + 出处汇总](#十)

---

<a id="一"></a>
## 一、NixOS 的心智模型：三个概念解释一切

初学者 90% 的困惑来自没搞清这三个概念。搞清之后，后面所有「为什么跑不起来」「为什么能回滚」都是自然推论。

### 1.1 derivation（构建配方）

**是什么**：derivation 是一份「构建配方」，描述「用什么输入、跑什么命令、产出什么路径」。执行后产物被放进 `/nix/store`。

**为什么重要**：产物路径由输入（名字、构建脚本、全部依赖）的哈希决定，所以**同样的输入必然得到同样的路径**。这就是「可复现」的物理基础。

store path 格式为 `/nix/store/<32 字符哈希>-<名字>`，例如 `/nix/store/1a2b...-firefox-142.0`。官方明确说这个哈希「应当被当作不透明标识符」，不要试图解读它。

> 出处：[nix.dev · Store Path](https://nix.dev/manual/nix/stable/store/store-path.html) `[官方]`

### 1.2 不可变性与「没有 /usr/lib」——解释后面所有报错

**关键事实**：NixOS **不遵循 FHS（Filesystem Hierarchy Standard）**。

- 没有 `/usr/lib`
- 没有 `/lib64/ld-linux-x86-64.so.2`
- 没有 `/bin/bash` 之外的常规动态链接器路径

**为什么**：Linux 的 ELF 可执行文件把「动态链接器（interpreter）的路径」**硬编码在文件头里**。普通发行版的二进制写着 `/lib64/ld-linux-x86-64.so.2`，NixOS 没这个文件 → 运行时报一个极具误导性的错误：

```
bash: ./some-binary: No such file or directory
```

文件明明存在，却报「找不到文件」。这不是文件缺失，是**它依赖的链接器缺失**。

**Nix 的解法**：打包时用 `patchelf` 改写 ELF 的 interpreter 和 RPATH，指向 `/nix/store` 里的 glibc。

> 出处：[NixOS Wiki · Packaging/Binaries](https://wiki.nixos.org/wiki/Packaging/Binaries) `[Wiki]`；[github.com/NixOS/patchelf](https://github.com/NixOS/patchelf) `[仓库]`

**这个事实直接决定了第五章的全部内容**：任何「官方下载的二进制」都需要某种方式补上 FHS 环境。

### 1.3 generation（代）——回滚能力的来源

每次 `nixos-rebuild switch` 都会：

1. 构建新的系统 closure（一整棵依赖树）
2. 在 `/nix/var/nix/profiles/system` 下追加一个新 generation
3. 往 bootloader 菜单里加一条启动项

**为什么回滚可靠**：`/nix/store` 里的内容不可变且内容寻址，旧 generation 指向的路径在被 GC 之前**始终存在且内容不变**。所以回滚是「原子切换一个符号链接」，不是「重新安装旧版本」。

传统发行版升级会**就地覆盖** `/usr` 下的文件，覆盖后旧版本就没了 → 回滚不可靠。这是 NixOS 最核心的运维红利。

> 出处：[NixOS Wiki · nixos-rebuild](https://wiki.nixos.org/wiki/Nixos-rebuild) `[Wiki]`

**实践**：

```bash
# 列出系统所有 generation
sudo nix-env --list-generations --profile /nix/var/nix/profiles/system
# 新命令等价写法（26.05 可用）
sudo nixos-rebuild list-generations

# 回滚到上一个 generation 并立即生效
sudo nixos-rebuild switch --rollback
```

### 1.4 nixos-rebuild 的七个子命令（语义差异，必须分清）

| 子命令 | 构建 | 立即激活 | 进 bootloader 菜单 | 典型用途 |
|---|---|---|---|---|
| `switch` | ✅ | ✅ | ✅ | 日常改配置 |
| `boot` | ✅ | ❌ | ✅ | 改内核/驱动，重启才生效 |
| `test` | ✅ | ✅ | ❌ | **临时试，重启即失效** |
| `build` | ✅ | ❌ | ❌ | 只验证能否构建成功 |
| `dry-build` | ✅(仅求值+计划) | ❌ | ❌ | **LLM 改配置后的验证闸门** |
| `dry-activate` | ✅ | ❌ | ❌ | 预览「激活会做哪些动作」 |
| `build-vm` | ✅ | — | — | 生成 QEMU 虚拟机，真跑一遍 |

> 出处：[NixOS Wiki · nixos-rebuild](https://wiki.nixos.org/wiki/Nixos-rebuild) `[Wiki]`；[NixOS Manual · Changing the Configuration](https://nixos.org/manual/nixos/stable/#sec-changing-config) `[官方]`

**为什么 `test` 很重要**：它激活新配置但不写进 bootloader。如果你把显示驱动配错了导致进不去图形界面，**重启就能回来**。这是新手上路阶段最安全的子命令。

---

<a id="二"></a>
## 二、三条配置路线：configuration.nix / flakes / home-manager

### 2.1 路线 A：configuration.nix 单体（默认，新手起点）

**文件位置**：`/etc/nixos/configuration.nix`，与自动生成的 `/etc/nixos/hardware-configuration.nix` 并列。

**它是什么**：一个 Nix 函数，接收 `config`/`pkgs`/`lib` 等参数，返回一个**属性集（attribute set）**，描述整台机器的期望状态。

```nix
{ config, pkgs, lib, ... }:
{
  imports = [ ./hardware-configuration.nix ];   # 把机器相关配置合并进来

  boot.loader.systemd-boot.enable = true;       # 用 systemd-boot 引导
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "mypc";
  networking.networkmanager.enable = true;      # 用 NetworkManager 管网络

  users.users.me = {
    isNormalUser = true;
    extraGroups = [ "wheel" "networkmanager" "video" ];  # wheel=sudo 权限
  };

  environment.systemPackages = with pkgs; [ vim git firefox ];

  system.stateVersion = "26.05";                # 见下方解释
}
```

**`system.stateVersion` 到底是什么**（最常见的误解）：

它**不是**当前系统版本，**不是**升级时要改的字段。它记录的是「**你首次安装时**的版本」，作用是让某些有状态数据（数据库格式、目录布局）**保持当时的默认行为**，不被新版本的默认值悄悄改掉。

官方原文：*"Most users should never change this value after the initial install, for any reason, even if you've upgraded your system."*

**为什么绝对不能随手改**：改它相当于告诉系统「请按新版本的默认值来初始化这些有状态数据」→ 可能触发数据格式迁移 → 可能损坏你的数据库、邮件目录等。

**什么时候才该改**：① 全新安装；② 某次 release notes 明确要求你改，并且你已手动完成迁移。

> 出处：[NixOS Wiki · When do I update stateVersion](https://wiki.nixos.org/wiki/FAQ/When_do_I_update_stateVersion) `[Wiki]`；[MyNixOS · system.stateVersion](https://mynixos.com/nixpkgs/option/system.stateVersion) `[官方选项]`

**两个文件的分工**：

| 文件 | 谁生成 | 管什么 | 能不能手改 |
|---|---|---|---|
| `hardware-configuration.nix` | `nixos-generate-config` 自动生成 | `fileSystems`、`swapDevices`、`boot.initrd.*`、内核模块 | 可以，但改动后建议重跑生成器对比 |
| `configuration.nix` | 安装器生成，你手写 | 其它全部系统策略 | 是主战场 |

> 出处：[NixOS Manual · Installation](https://nixos.org/manual/nixos/stable/#sec-installation) `[官方]`；[NixOS Wiki · nixos-generate-config](https://wiki.nixos.org/wiki/Nixos-generate-config) `[Wiki]`

**命令式 vs 声明式的边界**（这是「为什么我的包不生效」的根源）：

```bash
nix-shell -p ffmpeg        # 临时环境，退出即消失
nix run nixpkgs#hello      # 直接跑，不安装
nix profile install nixpkgs#ripgrep   # 装进用户 profile（命令式！）
nix-env -iA nixpkgs.htop   # 老式命令式安装（不推荐）
```

**为什么这些不该用**：它们**不写进 configuration.nix**，因此：

- 不参与系统 generation → **不会随系统回滚**
- 不体现在配置里 → 换机器/重装后消失
- 与声明式安装的同名包可能冲突 → 出现「我明明在配置里删了它，怎么还能用」

> 出处：[nix.dev · nix-shell](https://nix.dev/manual/nix/stable/command-ref/nix-shell.html) `[官方]`；[nix.dev · nix-env](https://nix.dev/manual/nix/stable/command-ref/nix-env.html) `[官方]`

**适用人群**：完全新手、单机、先跑起来再说。**理由**：零额外概念，官方安装器直接给你这套，出错一句 `nixos-rebuild switch --rollback` 就回来。

---

### 2.2 路线 B：Flakes（进阶，多机 / 想要锁版本）

**flake.nix 的 schema**：

```nix
{
  description = "My NixOS config";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    home-manager = {
      url = "github:nix-community/home-manager/release-26.05";
      inputs.nixpkgs.follows = "nixpkgs";   # 关键：让 HM 复用同一份 nixpkgs
    };
  };

  outputs = { self, nixpkgs, home-manager, ... }@inputs: {
    nixosConfigurations.mypc = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      specialArgs = { inherit inputs; };    # 把 inputs 传给所有模块
      modules = [
        ./configuration.nix
        ./hardware-configuration.nix
        home-manager.nixosModules.home-manager
      ];
    };
  };
}
```

**`flake.lock` 的作用**：首次运行任何 `nix` 命令时自动生成，**把每个 input 锁定到确切的 commit**。这保证「今天能构建的配置，半年后还能构建出完全一样的系统」。

**`nixos-26.05` vs `nixos-unstable`**：

| 分支 | 更新节奏 | 风险 | 用途 |
|---|---|---|---|
| `nixos-26.05` | 只回移 bug/安全修复 | 低 | 生产、日常主力机 |
| `nixos-unstable` | 滚动，每天变 | 高（可能破坏） | 想要新内核/新驱动、愿意承担风险 |

> 出处：[NixOS Wiki · Flakes](https://wiki.nixos.org/wiki/Flakes) `[Wiki]`

**使用**：

```bash
# flakes 目前仍是实验特性，必须先开
# /etc/nixos/configuration.nix 里加：
#   nix.settings.experimental-features = [ "nix-command" "flakes" ];

sudo nixos-rebuild switch --flake .#mypc     # 注意 # 后面是 hostname
nix flake update                             # 更新全部 input
nix flake update nixpkgs                     # 只更新 nixpkgs
```

**flakes 转正了吗？** 没有。截至 Nix 2.34.x 仍标注为 experimental。nix.dev 原文称其为 *"experimental extension format with outstanding issues"*，RFC 49 已关闭且**没有给出转正时间表**。

> 出处：[nix.dev · Flakes](https://nix.dev/concepts/flakes.html) `[官方]`；[Discourse · Why are flakes still experimental](https://discourse.nixos.org/t/why-are-flakes-still-experimental/29317) `[官方论坛]`

**优点**：lock 锁死版本、pure 求值、对 CI 二进制缓存友好、多机复现简单。
**代价**：学习曲线；**文件必须 `git add` 后才对 flake 可见**（未跟踪文件会被忽略，这是新手最常踩的坑）；传递依赖可能被锁旧。

---

### 2.3 路线 C：Home Manager（管用户环境与 dotfiles）

**它解决什么问题**：`configuration.nix` 管的是**系统**（root 视角）。但你的 `.bashrc`、`.gitconfig`、neovim 配置、用户级服务属于**用户**。Home Manager 把这些也变成声明式的。

**两种集成方式**：

**方式一：NixOS module（推荐给 NixOS 用户）**

```nix
{
  imports = [ home-manager.nixosModules.home-manager ];

  home-manager.useGlobalPkgs = true;      # 复用系统 nixpkgs，避免两份 nixpkgs 求值
  home-manager.useUserPackages = true;    # 用 users.users.<name>.packages 装包

  home-manager.users.me = { pkgs, ... }: {
    home.stateVersion = "26.05";          # 必需字段
    home.packages = [ pkgs.ripgrep pkgs.fd ];

    programs.git = {
      enable = true;
      userName = "me";
      userEmail = "me@example.com";
    };
    programs.bash.enable = true;
    programs.mangohud = {                 # 注意：MangoHud 只有 HM 模块，见第四章
      enable = true;
      enableSessionWide = true;
    };
  };
}
```

**方式二：standalone（独立，可跨发行版）**

```bash
nix run home-manager/release-26.05 -- init --switch
home-manager switch --flake .#me@mypc
```

> 出处：[Home Manager · NixOS module](https://nix-community.github.io/home-manager/installation/nixos.html) `[官方]`；[Home Manager · Standalone + Flakes](https://nix-community.github.io/home-manager/nix-flakes/standalone.html) `[官方]`

**`home.stateVersion`**：与 `system.stateVersion` **完全独立**，各管各的。同样是「首次生成时的版本，不要随便改」。

**典型管理对象**：

| 类别 | 例子 |
|---|---|
| 程序模块 | `programs.git`、`programs.firefox`、`programs.mangohud`、`programs.starship` |
| dotfiles | `home.file."/home/me/.foo".text = "..."` |
| 用户级包 | `home.packages = [ ... ]` |
| 用户级服务 | `systemd.user.services.*`、`services.syncthing` |

**三个「装包位置」的选择准则**：

| 位置 | 作用域 | 何时用 |
|---|---|---|
| `environment.systemPackages` | 全系统所有用户 | 系统服务、驱动工具、登录前就需要的程序 |
| `users.users.<name>.packages` | 单用户，走系统 nixpkgs | 简单场景，不想引入 HM |
| `home.packages`（HM） | 单用户，可跨发行版、能管 dotfiles | 用户应用与用户配置 |

> 出处：[NixOS Manual · User Management](https://nixos.org/manual/nixos/stable/#sec-user-management) `[官方]`

**版本对齐**：HM 用 `release-26.05` 分支跟随 NixOS 26.05。**务必保持同版本**，否则会出现两份 nixpkgs 导致库版本冲突。

---

### 2.4 三条路线对比与推荐

| 维度 | configuration.nix 单体 | + Flakes | + Home Manager |
|---|---|---|---|
| 适用人群 | 新手、单机 | 进阶、多机、CI | 想精细管用户环境 |
| 可复现性 | 中（跟随 channel 漂移） | 高（lock 锁死） | 高（可复用系统 pkgs） |
| 上手难度 | ★☆☆ | ★★★ | ★★☆ |
| 回滚粒度 | 整机 generation | 整机 generation | 整机 + 用户级 generation |
| 多机复用 | 弱（靠手动拷文件） | 强 | 强 |
| 管 dotfiles | ✗ | ✗ | ✓ 核心能力 |
| 额外概念负担 | 无 | flake/lock/pure eval | HM 选项体系 |

**推荐路径（分阶段，别一步到位）**：

1. **第 1 周**：只用默认 `configuration.nix`。目标：能装机、能改包、能回滚。用 `nixos-rebuild test` 做实验。
2. **第 2–4 周**：把 `/etc/nixos` 变成 git 仓库（先不上 flake）。目标：每次改动有 commit，出问题能 `git diff`。
3. **熟练后**：迁移到 flakes。**理由**：lock 文件让「半年后还能复现」成立，且 `inputs` 机制让引入 nix-gaming 等第三方源变得干净。
4. **最后**：叠加 Home Manager 管 dotfiles。**理由**：dotfiles 是用户级关注点，放系统配置里语义错位；HM 的 `programs.*` 模块已替你写好大量最佳实践配置。

**游戏玩家推荐路径**：**必须走声明式（configuration.nix 或 flake），且固定单一 nixpkgs**。

**理由（这条很硬）**：NVIDIA 闭源驱动 = 内核模块 + 用户态库的**配对**。内核模块由 `boot.kernelPackages` 决定，用户态库由 nixpkgs 决定。如果这两者来自不同的 nixpkgs 实例，就会出现「驱动版本与内核模块对不上」→ 开机黑屏或 `nvidia: module not found`。命令式装包（`nix-env -i`）最容易造成这种分裂。

> 出处：[NixOS Wiki · Nvidia](https://wiki.nixos.org/wiki/Nvidia) `[Wiki]`；[nixpkgs issue #445092](https://github.com/NixOS/nixpkgs/issues/445092) `[仓库]`

---

<a id="三"></a>
## 三、从零装机：默认配置逐段解释

### 3.1 安装流程（图形安装器）

1. 下载 ISO：`https://nixos.org/download` → 选 **Graphical ISO**（带图形安装器，对新手最友好）
2. 写入 U 盘（`dd` 或 Rufus / balenaEtcher），UEFI 启动
3. 安装器里选语言、键盘、分区、用户、桌面环境（GNOME / KDE Plasma 任选）
4. 重启后，配置文件已在 `/etc/nixos/`

> 出处：[NixOS Manual · Installation](https://nixos.org/manual/nixos/stable/#sec-installation) `[官方]`

### 3.2 逐段解释安装器生成的配置

```nix
# /etc/nixos/configuration.nix
{ config, pkgs, ... }:
{
  imports = [ ./hardware-configuration.nix ];
  # ↑ 把自动探测到的分区/内核模块合并进来。删了它机器可能起不来。

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
  # ↑ UEFI 机器用 systemd-boot。canTouchEfiVariables 允许安装器写 EFI 变量，
  #   没有它新内核不会出现在启动菜单里。

  networking.hostName = "nixos";
  networking.networkmanager.enable = true;
  # ↑ 用 NetworkManager 而非 systemd-networkd：桌面场景下 Wi-Fi/图形管理更方便。

  time.timeZone = "Asia/Shanghai";
  i18n.defaultLocale = "en_US.UTF-8";
  i18n.extraLocaleSettings = {
    LC_TIME = "zh_CN.UTF-8";
    LC_MONETARY = "zh_CN.UTF-8";
  };
  # ↑ 保留英文 locale 作为默认：避免某些程序把中文 locale 用出乱码；
  #   只覆盖时间/货币格式，得到中文显示但英文排序。

  services.xserver.enable = true;
  services.xserver.xkb.layout = "us";
  # ↑ 键盘布局。中文用户常改 "us" + 输入法，比 "cn" 布局更顺手。

  users.users.nixos = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];     # wheel 组 = 可用 sudo
    initialPassword = "changeme";  # 首次登录后立刻 passwd 改掉
  };

  system.stateVersion = "26.05";
  # ↑ 首次安装版本。此后无论升级到哪个版本都不要改。
}
```

**中文环境与输入法**（新手最常问）：

```nix
# 中文字体：不装会看到方块
fonts.packages = with pkgs; [
  noto-fonts
  noto-fonts-cjk-sans
  noto-fonts-cjk-serif
  noto-fonts-color-emoji
  wqy_zenhei
];
fonts.fontconfig.defaultFonts = {
  serif = [ "Noto Serif CJK SC" ];
  sansSerif = [ "Noto Sans CJK SC" ];
  monospace = [ "Noto Sans Mono CJK SC" ];
};

# 输入法：Fcitx5 + 中文引擎
i18n.inputMethod = {
  enable = true;
  type = "fcitx5";
  fcitx5.addons = with pkgs; [ fcitx5-chinese-addons fcitx5-rime ];
};
# 环境变量让 GTK/Qt 程序认输入法
environment.sessionVariables = {
  GTK_IM_MODULE = "fcitx";
  QT_IM_MODULE  = "fcitx";
  XMODIFIERS    = "@im=fcitx";
};
```

> 出处：[NixOS Wiki · Fcitx5](https://wiki.nixos.org/wiki/Fcitx5) `[Wiki]`；[NixOS Wiki · Fonts](https://wiki.nixos.org/wiki/Fonts) `[Wiki]`

### 3.3 必备基础设置

```nix
# 允许非自由软件（NVIDIA 驱动、Steam、部分字体等必须开）
nixpkgs.config.allowUnfree = true;

# 开启 flakes（第三章起会用到）
nix.settings.experimental-features = [ "nix-command" "flakes" ];

# 自动 GC：防止 /nix/store 无限膨胀
nix.gc = {
  automatic = true;
  dates = "weekly";
  options = "--delete-older-than 30d";   # 保留 30 天内的回滚点
  persistent = true;                      # 错过时间点就补跑
  randomizedDelaySec = "30m";             # 避免所有机器同时跑
};
nix.settings.auto-optimise-store = true;  # 增量硬链接去重，省磁盘

# 限制启动菜单里的 generation 数量
boot.loader.systemd-boot.configurationLimit = 10;

# 命令找不到时提示「哪个包提供它」
programs.command-not-found.enable = true;

# 自动升级（可选，新手建议先关，手动升级更有掌控感）
# system.autoUpgrade.enable = false;
```

> 出处：[NixOS Manual · Cleaning the Nix Store](https://nixos.org/manual/nixos/stable/#sec-nix-gc) `[官方]`；[MyNixOS · nix.gc.*](https://mynixos.com/nixpkgs/option/nix.gc.automatic) `[官方选项]`

**为什么 `--delete-older-than 30d` 而不是 `-d`**：`-d` 会删掉**全部**旧 generation，等于摧毁你的回滚点。保留 30 天是「磁盘 vs 保险」的合理折中。

---

<a id="四"></a>
## 四、游戏玩家专章

> 本章所有选项均在 nixpkgs `nixos-26.05` 分支源码中逐条比对确认。

### 4.1 显卡驱动

#### NVIDIA 专有驱动

```nix
nixpkgs.config.allowUnfree = true;   # 必须：NVIDIA 驱动是 unfree

hardware.graphics = {
  enable = true;        # 图形栈总开关（26.05 中 hardware.opengl 只是它的别名）
  enable32Bit = true;   # 32 位驱动：Steam/Wine 跑 32 位游戏必需
};

hardware.nvidia = {
  modesetting.enable = true;      # 生成 nvidia-drm.modeset=1，Wayland 与防撕裂必需
  open = true;                    # Turing(20系)+ 使用开源内核模块；驱动 ≥560 必须显式设
  powerManagement.enable = true;  # 笔记本：休眠时保存显存
  nvidiaSettings = true;          # 安装 nvidia-settings 图形工具
};

services.xserver.videoDrivers = [ "nvidia" ];  # 声明使用 NVIDIA 驱动
```

**每个选项的理由**：

| 选项 | 为什么这么设 |
|---|---|
| `allowUnfree = true` | NVIDIA 驱动 license 是 unfree，不开会直接构建失败 |
| `hardware.graphics.enable` | 26.05 里 `hardware.opengl` 已重命名为 `hardware.graphics`（重命名发生在 **24.11**），旧名保留为别名 |
| `enable32Bit` | Steam 里大量游戏和 Wine 前缀是 32 位的，缺 32 位驱动会启动失败 |
| `modesetting.enable` | 等价于内核参数 `nvidia-drm.modeset=1`。≥535 驱动默认 true。缺它 Wayland 无法启动、X11 有撕裂 |
| `open = true` | 驱动 ≥560 时有 assertion **强制**你显式设置此项，不设会报错 |
| `powerManagement.enable` | 笔记本挂起/恢复时保存显存到磁盘，避免恢复后花屏 |
| `services.xserver.videoDrivers` | 决定 X server 加载哪个驱动模块 |

> 出处：`nixos/modules/hardware/video/nvidia.nix` `[核实·源码]`；`nixos/modules/hardware/graphics.nix`（含 `hardware.opengl` → `hardware.graphics` 的 `mkRenamedOptionModule`）`[核实·源码]`；[NixOS Wiki · Nvidia](https://wiki.nixos.org/wiki/Nvidia) `[Wiki]`

**⚠️ 为什么换驱动/内核必须重启，不能只 `switch`**：

内核模块由**当前正在运行的内核**加载。`nixos-rebuild switch` 只切换用户态 generation，运行中的内核不会变。所以：

```bash
sudo nixos-rebuild boot    # 而不是 switch
sudo reboot
```

**AMD / Intel（开源驱动，省心得多）**：

```nix
hardware.graphics = {
  enable = true;
  enable32Bit = true;
  extraPackages = with pkgs; [
    # AMD 可选：amdvlk（Vulkan 备选实现）
    # Intel 可选：intel-media-driver / vpl-gpu-rt
  ];
};
```

AMD 用内核自带的 `amdgpu` + Mesa，无需 `allowUnfree`，无版本配对问题。**新装机若可选，AMD 显卡在 Linux 上的运维成本显著低于 NVIDIA。**

> 出处：[NixOS Wiki · Graphics](https://wiki.nixos.org/wiki/Graphics) `[Wiki]`

### 4.2 Steam / Proton

```nix
programs.steam = {
  enable = true;                        # 隐式启用 hardware.steam-hardware
  remotePlay.openFirewall = true;       # 打开 Remote Play 所需端口
  gamescopeSession.enable = true;       # 提供 gamescope 会话（掌机/全屏体验）
  extraCompatPackages = with pkgs; [ proton-ge-bin ];  # 声明式安装 GE-Proton
};
```

**Proton 为什么能在 NixOS 上跑非 Nix 游戏**：Steam 的 **Steam Runtime** 本身就是一个 **FHS 容器**。它提供游戏所需的 `/usr`、`/lib` 层级，游戏在里面看到的是「正常 Linux」。所以 Steam 游戏基本不受 NixOS 无 FHS 的影响。

`pkgs.steam-run` 就是这个 FHS 环境的独立入口，可以拿来跑别的二进制（见第五章）。

> 出处：`nixos/modules/programs/steam.nix` `[核实·源码]`；[NixOS Wiki · Steam](https://wiki.nixos.org/wiki/Steam) `[Wiki]`

**反作弊**：EAC / BattlEye 是否可用**逐游戏而定**，取决于开发者是否开启 Proton 支持。查 https://areweanticheatyet.com/ `[仓库]`

### 4.3 性能与监控工具

```nix
programs.gamemode.enable = true;     # 游戏启动时自动提频/调 nice

programs.gamescope = {
  enable = true;
  capSysNice = true;                 # 允许 gamescope 自行 renice
};

# ⚠️ MangoHud：NixOS 没有 programs.mangohud 模块！
#    那是 Home Manager 的选项。NixOS 层面这样用：
environment.systemPackages = with pkgs; [ mangohud ];
# 然后 Steam 启动项填：mangohud %command%
# 或者全局：environment.sessionVariables.MANGOHUD = "1";
```

**⚠️ 这是本节最容易踩的坑**：网上大量教程写 `programs.mangohud.enable = true;` 放在 `configuration.nix` 里 —— **在 NixOS 里这会导致 eval 失败**，因为该选项只存在于 Home Manager。

> 出处：[MyNixOS · programs.mangohud](https://mynixos.com/options/programs.mangohud)（链接全部指向 home-manager）`[核实]`；[Home Manager · programs.mangohud](https://nix-community.github.io/home-manager/options/home-manager/programs/mangohud.html) `[官方]`

**AMD 用户**：`programs.corectrl.enable = true;`（模块只有 `enable` + `package` 两个选项）`[核实·源码: nixos/modules/hardware/corectrl.nix]`

> ⚠️ **超频选项已迁移**：`programs.corectrl.gpuOverclock.enable` / `.ppfeaturemask` 在 26.05 **已重命名为 `hardware.amdgpu.overdrive.enable` / `.ppfeaturemask`**（`corectrl.nix:18-25` 的两条 `mkRenamedOptionModule`）。老教程里的旧名会报错。
> 开 `programs.corectrl.enable` 会同时建 `corectrl` 用户组 + 写一条 polkit 规则，**你还需要把自己加进该组**（`users.users.<name>.extraGroups = [ "corectrl" ]`）才能免密启动。

**sched-ext 调度器**（26.05 已内置）：

```nix
services.scx = {
  enable = true;
  scheduler = "scx_rustland";   # 默认值
  # package = pkgs.scx.full;    # 默认
};
```

> 出处：`nixos/modules/services/scheduling/scx.nix` `[核实·源码]`

### 4.4 其它启动器（包名均在 26.05）

| 启动器 | 包名 | 用途 |
|---|---|---|
| Lutris | `lutris` | 通用 Wine/模拟器游戏管理 |
| Heroic | `heroic` | Epic / GOG / Amazon 游戏 |
| Bottles | `bottles` | 可视化 Wine 前缀管理 |
| Prism Launcher | `prismlauncher` | Minecraft 多实例 |
| RetroArch | `retroarch` | 模拟器前端 |

> 出处：nixpkgs `pkgs/by-name/*`、`all-packages.nix` `[核实·源码]`

### 4.5 nix-gaming（第三方 flake，可选进阶）

提供 nixpkgs 里没有的游戏/工具：`wine-tkg`、`wine-cachyos`、`osu-stable`、`rocket-league`、`star-citizen`、`northstar-proton` 等，以及两个实用模块：

- `pipewireLowLatency` — 低延迟音频（`services.pipewire.lowLatency.*`）
- `platformOptimizations` — `programs.steam.platformOptimizations.enable`

```nix
inputs.nix-gaming.url = "github:fufexan/nix-gaming";
# 缓存（不配会从源码编译，极慢）
nix.settings.substituters = [ "https://nix-gaming.cachix.org" ];
nix.settings.trusted-public-keys = [
  "nix-gaming.cachix.org-1:nbjlureqMbRAxR1gJ/f3hxemL9svRfzI17kGPMBzKAc="
];
```

**风险**：需要信任第三方 binary cache（理论上可注入内容）；部分包是 unfree；与 nixpkgs 版本可能漂移。**只在你明确需要某个包时引入。**

> 出处：[github.com/fufexan/nix-gaming](https://github.com/fufexan/nix-gaming) `[仓库]`

### 4.6 系统调优

```nix
# vm.max_map_count：26.05 默认已是 1048576，一般无需手动设置
# （老教程里的 262144 是过时值）
boot.kernel.sysctl."vm.max_map_count" = 1048576;

powerManagement.cpuFreqGovernor = "performance";   # 台式机可设；笔记本会耗电

services.thermald.enable = true;    # Intel 散热守护

# 内核选择
boot.kernelPackages = pkgs.linuxPackages_latest;   # 新硬件/新驱动
# boot.kernelPackages = pkgs.linuxPackages_zen;    # 低延迟优化
```

> 出处：`nixos/modules/config/sysctl.nix`（`"vm.max_map_count" = lib.mkDefault 1048576;`）`[核实·源码]`；`nixos/modules/tasks/cpu-freq.nix` `[核实·源码]`

**⚠️ `cpuFreqGovernor` 与 `services.tlp` / `power-profiles-daemon` 可能冲突**，三者别同时开。

**关于把 Steam 库放在 NTFS 分区**：社区普遍报告权限与符号链接问题，建议用 ext4/btrfs。**`[未核实]`** —— 未找到权威一手出处，仅作提示。

### 4.7 完整可复制片段（NVIDIA 独显 + Steam 全家桶）

```nix
{ config, pkgs, ... }:
{
  nixpkgs.config.allowUnfree = true;   # NVIDIA + Steam 都需要

  hardware.graphics = {
    enable = true;                     # 图形栈（26.05 用 graphics，opengl 已弃用为别名）
    enable32Bit = true;                # 32 位：Steam/Wine 必需
  };

  hardware.nvidia = {
    modesetting.enable = true;         # = nvidia-drm.modeset=1
    open = true;                       # Turing+ 开源内核模块，驱动 ≥560 强制显式设
    powerManagement.enable = true;     # 笔记本休眠存显存
    nvidiaSettings = true;
  };
  services.xserver.videoDrivers = [ "nvidia" ];

  programs.steam = {
    enable = true;
    remotePlay.openFirewall = true;
    gamescopeSession.enable = true;
    extraCompatPackages = with pkgs; [ proton-ge-bin ];
  };

  programs.gamemode.enable = true;
  programs.gamescope = { enable = true; capSysNice = true; };

  environment.systemPackages = with pkgs; [
    mangohud          # NixOS 无 programs.mangohud，用包 + Steam 启动项 `mangohud %command%`
    protonup-qt       # 手动管理多版本 Proton
    gamescope
  ];

  boot.kernelPackages = pkgs.linuxPackages_latest;
}
```

**首次应用**：`sudo nixos-rebuild boot && sudo reboot`（驱动变更必须重启）。

---

<a id="五"></a>
## 五、NixOS 没有的软件怎么跑

### 5.1 决策树

```
要运行的程序在 nixpkgs 里吗？
├─ 有 → nix shell nixpkgs#xxx  或写进 environment.systemPackages
└─ 没有
   ├─ 是 .AppImage？
   │   ├─ 偶尔用 → nix-shell -p appimage-run → appimage-run foo.AppImage
   │   └─ 常用   → programs.appimage = { enable = true; binfmt = true; };
   ├─ 是官方 tar.gz / 专有二进制，依赖复杂（图形、CUDA、一堆 .so）？
   │   └─ buildFHSEnv 建沙箱（或直接用 pkgs.steam-run）
   ├─ 是 CLI 工具，只缺 libc 和几个 .so（node/npm/python 官方二进制）？
   │   └─ programs.nix-ld.enable = true;  ← 一劳永逸的兜底
   └─ 长期使用、有源码？
       └─ 写 derivation（buildNpmPackage / python3.withPackages / mkDerivation）
```

### 5.2 方案 A：buildFHSEnv（FHS 沙箱）

**现状**：函数现名 `pkgs.buildFHSEnv`（内部是 `buildFHSEnvBubblewrap`）。**旧名 `buildFHSUserEnv` 在当前 nixpkgs 中已不存在**（`all-packages.nix` 与 `aliases.nix` 中均无）。看到老教程用旧名，直接换成新名。

```nix
# shell.nix —— 给官方 tar.gz 二进制建沙箱，nix-shell 进入
{ pkgs ? import <nixpkgs> {} }:
let
  base = pkgs.appimageTools.defaultFhsEnvArgs;   # 复用 AppImage 的默认库集合
in
(pkgs.buildFHSEnv (base // {
  name = "my-fhs-env";
  targetPkgs = pkgs: (base.targetPkgs pkgs) ++ (with pkgs; [
    pkg-config
    ncurses
    zlib
    # 你的程序需要什么就加什么
  ]);
  multiPkgs = pkgs: (with pkgs; [ glibc ]);   # 32 位库放这里
  runScript = "bash";
  profile = ''
    export MY_ENV=1
  '';
})).env
```

```bash
nix-shell ./shell.nix
# 进入后可以直接跑 ./your-binary
```

**`targetPkgs` vs `multiPkgs`**：前者是主架构（64 位）的包，后者是 32 位库。

> 出处：[Nixpkgs Manual · FHS Environments](https://nixos.org/manual/nixpkgs/stable/#sec-fhs-environments) `[官方]`

### 5.3 方案 B：AppImage

**临时用法**：

```bash
nix-shell -p appimage-run
appimage-run ~/Downloads/SomeApp.AppImage
```

**让 AppImage 能直接双击运行**（注册到内核 binfmt_misc）：

```nix
programs.appimage = {
  enable = true;    # 提供 appimage-run 包装脚本
  binfmt = true;    # 让内核用 appimage-run 作为 .AppImage 的解释器
};
```

**缺库时覆盖**：

```nix
programs.appimage.package = pkgs.appimage-run.override {
  extraPkgs = pkgs: [ pkgs.icu pkgs.libxcrypt-legacy pkgs.python312 ];
};
```

**AppImage 常见失败原因**：

| 症状 | 原因 | 修法 |
|---|---|---|
| 挂载失败 | 缺 FUSE | `programs.appimage.enable` 已带 fuse；或手动解包 |
| 缺 .so | 依赖不在默认库集合 | `extraPkgs` 补 |
| 沙箱受限 | bubblewrap 在容器/受限内核下失败 | `./foo.AppImage --appimage-extract` 解包后跑 `squashfs-root/AppRun` |
| 找不到字体/图标 | 非 Nix 程序看不到系统字体 | 见 NixOS Wiki「Fixes for non-Nix applications」 |

> 出处：[NixOS Wiki · Appimage](https://wiki.nixos.org/wiki/Appimage) `[核实·Wiki]`；[MyNixOS · programs.appimage](https://mynixos.com/options/programs.appimage) `[核实]`

### 5.4 方案 C：nix-ld（★ 最推荐的兜底方案）

**它做什么**：`programs.nix-ld` 把系统的动态链接器设为 `nix-ld`，并导出 `NIX_LD` / `NIX_LD_LIBRARY_PATH` 环境变量。这样**任何写着标准 FHS 链接器路径的 ELF 二进制**都能被正确加载。

```nix
programs.nix-ld = {
  enable = true;
  libraries = with pkgs; [
    # 默认只有 zlib/zstd/curl/openssl/systemd 等少数几个，缺什么补什么
    stdenv.cc.cc.lib   # 提供 libstdc++
    zlib
    zlib-ng
    openssl
    curl
    libxkbcommon
    libglvnd
    # 报 "cannot open shared object file: libXXX.so" 时，把提供它的包加进来
  ];
};
```

**为什么它能解决 node/npm/python 官方二进制**：这些官方二进制只依赖 libc + 少量通用 .so。nix-ld 把链接器和库路径都补上了，它们就能直接跑。

**关键注意**：nix-ld **不提供** FHS 目录结构，只提供链接器。所以它对「依赖大量图形库的复杂程序」不够用 —— 那种场景要用 buildFHSEnv。

> 出处：[NixOS Wiki · Nix-ld](https://wiki.nixos.org/wiki/Nix-ld) `[Wiki]`；[github.com/nix-community/nix-ld](https://github.com/nix-community/nix-ld) `[仓库]`；`nixos/modules/programs/nix-ld.nix` `[核实·源码]`

### 5.5 方案 D：steam-run

`pkgs.steam-run` 是 `steam.run`，一个预置了大量图形/音频/游戏库的 buildFHSEnv。适合依赖复杂的现成二进制：

```bash
steam-run ./some-complex-binary
steam-run npx cypress open      # 例如带预编译二进制的 npm 工具
```

> 出处：`pkgs/top-level/all-packages.nix`（`steam-run = steam.run;`）`[核实·源码]`

### 5.6 决策表

| 场景 | 选择 | 理由 |
|---|---|---|
| 长期用、有源码 | 写 derivation | 完全融入 Nix 生态，可缓存可回滚 |
| 现成 tar.gz、专有二进制、依赖复杂 | `buildFHSEnv` / `steam-run` | 提供完整 FHS 目录与库 |
| CLI 工具、只缺 libc 和几个 .so | `nix-ld` | 一劳永逸，无需为每个程序建环境 |
| `.AppImage` | `appimage-run` / `programs.appimage` | 专为该格式设计 |
| 临时试跑 | `nix-shell -p` + `steam-run` | 用完即弃，不污染系统 |

### 5.7 node / npm 生态

**现状（重要变更）**：

- `nixpkgs.nodePackages` **已整体移除**（报错原文：*"nodePackages has been removed because it was unmaintainable"*）
- `pkgs.nodejs_22` 等版本化包可用；`pkgs.nodejs` 当前指向 LTS 别名
- `pkgs.pnpm`、`pkgs.bun`、`pkgs.corepack` 均可用

**为什么 `npm install -g` 在 NixOS 上必然失败**：

```
npm ERR! code EACCES
npm ERR! errno -13
npm ERR! syscall mkdir
npm ERR! path /nix/store/xxxxx-nodejs-22.x/lib/node_modules/xxx
```

因为 `/nix/store` 是**只读的**（这正是不可变性的代价与保障）。npm 试图往 store 里写 → 权限拒绝。

**正确做法一：改 npm 全局前缀到用户目录（推荐）**

```bash
npm config set prefix ~/.npm-global
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
npm install -g @openai/codex
```

**正确做法二：nix-ld 兜底**（官方二进制形式的 CLI 用这个）

**正确做法三：FHS 沙箱**（依赖复杂的用这个）

```bash
steam-run npm install -g some-package
```

**npx 的坑**：部分包（如 Cypress）会在 npx 时下载预编译二进制 → 仍然受无 FHS 影响 → 用 `steam-run npx ...` 兜底。

> 出处：[nixos.wiki · Node](https://nixos.wiki/wiki/Node) `[Wiki]`；[Discourse #76753](https://discourse.nixos.org/t/76753) `[官方论坛]`

### 5.8 Python 生态

```nix
# 方式一：把依赖固化进解释器（推荐用于脚本/服务）
python3.withPackages (ps: [ ps.requests ps.numpy ps.pillow ])

# 方式二：用 uv / poetry（推荐用于开发）
environment.systemPackages = with pkgs; [ uv poetry ];
```

**为什么 venv 在 NixOS 上常出问题**：`python3 -m venv` 生成的解释器仍指向 `/nix/store` 里那个只读解释器，`pip install` 会尝试写入 → 失败或污染。

**边界**：`nix-shell -p python3` 里只能 `pip install --user` 或建 venv，**不能改 store**。

> 出处：[NixOS Wiki · Python](https://wiki.nixos.org/wiki/Python) `[Wiki]`

### 5.9 案例：Hermes Agent

**核实结果**：Hermes Agent 是 **Nous Research** 出品的开源 AI Agent 框架（MIT），**主要走 Python 分发**，不是 npm 包。官方给出的安装方式包括一键脚本、pip、Docker、SSH、Daytona、Modal。

**一键脚本做了什么**：用 `uv` 获取 Python 环境，装 `hermes-agent`，然后 `hermes pm install` 拉取运行依赖（**包括 Node 运行时和 Chromium 等浏览器二进制**）。这一步是 NixOS 上的关键难点 —— 它会下载官方预编译二进制。

**NixOS 上的推荐方案**：

```nix
# configuration.nix
programs.nix-ld = {
  enable = true;
  libraries = with pkgs; [
    stdenv.cc.cc.lib zlib openssl curl
    libxkbcommon libglvnd
    # Chromium 运行还需要一批图形库，缺啥补啥（看报错里的 .so 名字）
    nss nspr atk at-spi2-atk cups dbus expat libdrm
    mesa libgbm alsa-lib pango cairo
  ];
};

environment.systemPackages = with pkgs; [
  uv          # 官方脚本依赖 uv 取 Python
  python3
  nodejs_22   # 让 hermes 优先用 Nix 的 node，而非自己下载
];
```

```bash
# 推荐：不用官方一键脚本（它会往系统里下二进制），改用 uv 建独立环境
uv tool install hermes-agent
hermes --version

# 如果 hermes pm install 仍然要下 Node/Chromium：
#   优先让它复用系统 node（设 PATH 或 HERMES_NODE_PATH 之类的变量）
#   实在不行，用 steam-run 包一层：
#   steam-run hermes pm install
```

**为什么这样做**：

1. 用 `uv tool install` 而非一键脚本 → 装进用户目录，不污染系统，且版本可回滚
2. 开 nix-ld → 让 hermes 下载的预编译二进制能跑起来
3. 先装 `nodejs_22` → 尽量让 hermes 复用 Nix 的 node，避免它自己下载一份（自己下的那份没有 Nix 的补丁，更容易出问题）

> 出处：[Hermes Agent 安装文档](https://hermes-ai.net/zh/docs/installation/) `[仓库]`；[github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) `[仓库]`
> ⚠️ `[未核实]`：`hermes pm install` 是否支持指定外部 node 路径，未在公开文档中找到明确说明。上面第 3 点建议属**推断**，请以实测为准。

### 5.10 案例：OpenAI Codex CLI

**核实结果**：npm 分发为主，包名 `@openai/codex`。官方另提供 `curl -fsSL https://chatgpt.com/codex/install.sh | sh`（Rust 原生二进制）与 Homebrew。

**NixOS 上两条路线**：

**路线一：npm（推荐）**

```nix
# configuration.nix —— 让 npm 全局安装落在用户目录
environment.systemPackages = with pkgs; [ nodejs_22 ];
```

```bash
npm config set prefix ~/.npm-global
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
npm install -g @openai/codex
codex --version
```

**为什么可行**：npm 全局前缀改到 `~/.npm-global` 后，不再尝试写 `/nix/store`，权限问题消失。

**路线二：官方 install.sh（Rust 二进制）**

```nix
programs.nix-ld = {
  enable = true;
  libraries = with pkgs; [ stdenv.cc.cc.lib zlib openssl curl libxkbcommon ];
};
```

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
# 二进制装到 ~/.codex 或类似路径，靠 nix-ld 提供链接器
```

**为什么不推荐把 install.sh 装的东西再打包成 derivation**：它是个会自我更新的安装器，打包成 derivation 会与自动更新冲突。用 nix-ld 兜底更务实。

> 出处：[github.com/openai/codex](https://github.com/openai/codex)（README 安装段）`[仓库]`

---

<a id="六"></a>
## 六、稳定基座 + 滚动组件（混合版本策略）

> 本章回答一个具体问题：**系统底座留在 26.05 稳定版，但浏览器、Mesa、内核、游戏组件想跟着滚动更新，怎么做？**

### 6.0 先做一件事：量出「跨源到底能拿到什么」

**不要凭「unstable 一定更新」这个直觉动手。先量。** 我在 `nixos-26.05` 与 `nixos-unstable` 两个分支上逐包比对了版本（2026-10-12 实测）：`[核实·源码]`

| 组件 | 26.05（stable） | nixos-unstable | 跨源值不值 |
|---|---|---|---|
| **内核 `linuxPackages_latest`** | **7.2.9** | **7.2.9** | ❌ **完全一致，跨源毫无意义** |
| 内核 `linuxPackages`（默认） | 6.18.55（LTS） | 6.18.55（LTS） | ❌ 完全一致 |
| **Mesa** | **26.1.8** | **26.2.4** | ✅ **值得**（小版本差一个代际） |
| **proton-ge-bin** | **GE-Proton11-1** | **GE-Proton11-7** | ✅ **值得** |
| **gamescope** | **3.16.23** | **3.16.31** | ✅ 值得 |
| **mangohud** | **1.91.6** | **1.91.6** | ❌ 完全一致 |

**出处（可自行复验）**：`pkgs/os-specific/linux/kernel/kernels-org.json`（内核版本表）、`pkgs/development/libraries/mesa/common.nix`（Mesa 版本）、`pkgs/by-name/{pr/proton-ge-bin,ma/mangohud,ga/gamescope}/package.nix`。两个分支的 raw 路径只差分支名。

> [!IMPORTANT]
> **这张表推翻了本章原稿的一条结论。** 原稿把「内核」列为「❌ 不要跨 nixpkgs 滚」，理由是「NVIDIA / ZFS / VirtualBox 的模块必须与内核同源」。**那个理由只对「有树外内核模块」的人成立**，而且它掩盖了一个更简单的事实：
>
> **在 26.05 上你根本不需要跨源拿内核 —— stable 的 `linuxPackages_latest` 已经是 7.2.9，和 unstable 逐字相同。**
>
> 两个分支的 `packageAliases` 都是 `linux_default = packages.linux_6_18; linux_latest = packages.linux_7_2;`（`pkgs/top-level/linux-kernels.nix:739-743` vs unstable 同文件 `:667-671`），而 `kernels-org.json` 里 `7.2` 的 `version` 两边都是 `7.2.9`。**stable 分支会定期把内核 rebase 到最新补丁。**

### 6.1 分清：哪些组件能滚，哪些不能

**核心判据不是「新不新」，而是「它跟谁配对」。**

| 组件 | 类型 | 能否跨 nixpkgs 滚 | 理由 |
|---|---|---|---|
| 浏览器（Firefox / Chromium） | 纯用户态叶子包 | ✅ 可以 | 只依赖用户态库；且 stable 分支本身也在收浏览器安全更新 |
| Mesa | 用户态图形库 | ⚠️ 官方支持，但有实测翻车 | 有官方选项 `hardware.graphics.package`（25.05 起），社区实测出现版本错配。**且实测确实有版本差（26.1.8 → 26.2.4）** |
| 游戏组件（proton-ge-bin / mangohud / gamescope） | 纯用户态 | ✅ 可以（**先看 §6.0 表决定值不值**） | 不进内核，不参与引导。实测 proton-ge-bin 与 gamescope 有差，mangohud 无差 |
| **内核（linux）** | 与内核模块配对 | ⚠️ **看平台，而且通常没必要** | **有树外模块**（NVIDIA / ZFS / VirtualBox）→ ❌ **绝对不要**跨源；**纯 AMD/Intel**（无树外模块）→ 技术上可行，**但 26.05 已经是最新内核，跨源拿不到任何东西**（§6.0 表 + §6.4 ③） |
| NVIDIA 闭源驱动 | 内核模块 + 用户态库配对 | ❌ 不要 | 驱动与内核模块版本强绑定 |
| 系统模块（systemd / glibc / 引导） | 系统基座 | ❌ 不要 | 由 `nixosSystem` 决定，跨版本会破坏激活流程 |

**一句话原则**：**可以滚「叶子」，不能滚「根」。** 叶子包出问题最多是那个程序跑不起来；根出问题是最小系统起不来。

**关键洞察（最反直觉的一条）**：混合版本真正的风险不是「版本太新」，而是「**同一个包同时被两个 nixpkgs 定义**」。

社区实测案例：有人在 NixOS stable 上用 `hardware.graphics.package = unstable.mesa;` 换成滚动 Mesa（2026-05），结果是：

> Firefox 报告的是**新的** Mesa 版本号，但报告**没有硬件加速**；Steam 报告的还是**旧的**稳定版 Mesa 版本号；GNOME 桌面环境的风扇一直转。

出处：[Discourse · Mesa unstable on nixos-stable in 2026?](https://discourse.nixos.org/t/mesa-unstable-on-nixos-stable-in-2026/77618) `[官方论坛]`

同一个系统里两个程序看到两个不同的 Mesa —— 这正是「同一个包被两份定义」的典型症状。

### 6.2 只用 `configuration.nix` 做到吗？——能，有三条路

**先直接回答：能。`configuration.nix` 里就能拿到 unstable 的包，不需要 flake。** 三条路，锁定程度递增。

#### 路 A：加一条 unstable channel（最简单，但完全不锁）

```bash
sudo nix-channel --add https://nixos.org/channels/nixos-unstable nixos-unstable
sudo nix-channel --update
```

```nix
# configuration.nix
let
  unstable = import <nixos-unstable> { config.allowUnfree = true; };
in
{
  environment.systemPackages = [
    unstable.proton-ge-bin    # 游戏组件跟着 unstable 滚
  ];

  hardware.graphics.package   = unstable.mesa;                  # Mesa（有风险，见 §6.4）
  hardware.graphics.package32 = unstable.pkgsi686Linux.mesa;    # 32 位必须一起换
}
```

**上面那两行 Mesa 就是 §6.1 翻车案例的原始配置。**

#### 路 B：`builtins.fetchTarball`（不用 channel、不用 flake，仍然只改 `configuration.nix`）

**这是原稿漏掉的一条路** —— 不需要 `nix-channel`，也不需要 flake，纯 `configuration.nix`：

```nix
# configuration.nix —— 一个文件搞定，不碰 channel，不建 flake
{ config, pkgs, lib, ... }:
let
  # ① 拉一份 unstable 的 nixpkgs 源码树
  unstableSrc = builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz";
    # sha256 = "...";   # ← 建议加：不加的话每次求值都可能重新下载，且不可复现
  };

  # ② 导入它，并继承你的 allowUnfree 等设置
  unstable = import unstableSrc {
    inherit (pkgs.stdenv.hostPlatform) system;
    inherit (config.nixpkgs) config;
  };
in
{
  # ③ Mesa
  hardware.graphics.package   = unstable.mesa;
  hardware.graphics.package32 = unstable.pkgsi686Linux.mesa;

  # ④ 游戏组件
  environment.systemPackages = [
    unstable.proton-ge-bin
    unstable.gamescope
  ];
}
```

**取 hash 的办法**（不加 hash 会有一个警告，且不可复现）：

```bash
nix-prefetch-url --unpack https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz
```

> [!WARNING]
> **`nixos-unstable.tar.gz` 是一个「移动目标」。** 它指向 unstable 分支的**当前** HEAD，所以不加 `sha256` 时每次求值都可能拉到不同内容 —— 这等于「用 fetchTarball 实现了 channel 的不锁行为」。**要可复现就必须钉死**：
>
> ```nix
> url = "https://github.com/NixOS/nixpkgs/archive/<完整 commit>.tar.gz";
> sha256 = "...";
> ```
>
> **这条路的价值**：它是「不想引入 flake、又想要比 channel 更可控」的折中。**代价是你要自己管理那个 commit 字符串** —— 这其实就是手工版的 `flake.lock`。

#### 路 C：`builtins.fetchGit` + 钉死 `rev`（纯 `configuration.nix` 的「准锁定」写法）

```nix
# configuration.nix
{ config, pkgs, ... }:
let
  unstable = import (builtins.fetchGit {
    url = "https://github.com/NixOS/nixpkgs";
    ref = "refs/heads/nixos-unstable";
    rev = "0000000000000000000000000000000000000000";   # ← 钉死一个 commit
  }) {
    inherit (pkgs.stdenv.hostPlatform) system;
    inherit (config.nixpkgs) config;
  };
in
{
  hardware.graphics.package   = unstable.mesa;
  hardware.graphics.package32 = unstable.pkgsi686Linux.mesa;
}
```

`fetchGit` 带 `rev` 时 Nix 会校验取到的 commit 与 `rev` 一致，**这就是「手工锁」**。升级 = 手动改 `rev` 那一行。

#### 三条路的对照

| 路 | 需要 channel？ | 需要 flake？ | 锁版本？ | 能单独回滚包？ | 适合 |
|---|---|---|---|---|---|
| **A** channel + `import <nixos-unstable>` | ✅ 要 | ❌ 不要 | ❌ **完全不锁** | ❌ | 临时救急装一个包 |
| **B** `fetchTarball` | ❌ 不要 | ❌ 不要 | ⚠️ 加 `sha256` 才锁 | ❌ | 不想碰 channel / flake，能接受手工管 hash |
| **C** `fetchGit` + `rev` | ❌ 不要 | ❌ 不要 | ✅ **锁**（手工钉 rev） | ❌ | 想要锁定但坚决不引入 flake |
| **D** flake（§6.3） | ❌ 不要 | ✅ 要 | ✅ **锁**（`flake.lock`） | ❌ | **长期做滚动组件（推荐）** |

> [!NOTE]
> **「能单独回滚某个包」这一列全是 ❌ —— 这是混合版本策略的固有局限。** 无论哪条路，回滚的粒度都是**整次 rebuild**（`nixos-rebuild --rollback` 或 `home-manager` 的 generation），不是「只把 mesa 退回去」。想要单包回滚，只能手工改回那一行引用。
>
> 唯一例外是**把滚动包放在 Home Manager 层**（§6.4 ⑥）—— 那时回滚粒度是 HM 的 generation，虽然仍不是单包，但至少不影响系统能启动。

**结论**：A 能用但只适合救急；B/C 是「不想用 flake」时的正解；**要长期做滚动组件，走 D（flake）**。

### 6.3 路 D：flake（推荐）

flake 让你**同时持有两份 nixpkgs**，并显式声明哪份负责什么。

```nix
# flake.nix
{
  description = "NixOS 稳定基座 + 滚动组件";

  inputs = {
    # ① 基座：稳定版。整个系统由它构建
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

    # ② 滚动源：只用来取叶子包
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";

    home-manager = {
      url = "github:nix-community/home-manager/release-26.05";
      inputs.nixpkgs.follows = "nixpkgs";   # HM 跟稳定基座，不跟滚动源
    };
  };

  outputs = { self, nixpkgs, nixpkgs-unstable, home-manager, ... }@inputs:
  {
    nixosConfigurations.mypc = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      specialArgs = { inherit inputs; };
      modules = [
        ./configuration.nix
        ./hardware-configuration.nix
        home-manager.nixosModules.home-manager
      ];
    };
  };
}
```

**接线方式：两种，只用第一种。**

**✅ 方式 A：`_module.args`（推荐）**

```nix
# configuration.nix
{ config, pkgs, inputs, lib, ... }:
let
  system = pkgs.stdenv.hostPlatform.system;
  unstable = import inputs.nixpkgs-unstable {
    inherit system;
    inherit (config.nixpkgs) config;   # 继承 allowUnfree 等设置
  };
in
{
  _module.args.pkgsUnstable = unstable;   # 之后任何模块都能用 pkgsUnstable

  environment.systemPackages = [
    unstable.firefox
  ];
}
```

**为什么推荐**：只为需要的包求值 unstable，eval 开销小。

**❌ 方式 B：overlay 把 unstable 塞进 `pkgs`**

```nix
# 不推荐
nixpkgs.overlays = [
  (final: _: {
    unstable = import inputs.nixpkgs-unstable {
      inherit (final.stdenv.hostPlatform) system;
      inherit (final) config;
    };
  })
];
```

**为什么不推荐**：官方论坛原话 —— 「我个人反对这个 overlay 方案，因为为此用 overlay 完全没必要，而且很可能拖慢 eval。」

出处：[Discourse · Mixing stable and unstable packages on flake-based NixOS system](https://discourse.nixos.org/t/mixing-stable-and-unstable-packages-on-flake-based-nixos-system/50351) `[官方论坛]`

**三条硬限制（必须知道）**

1. **同一个包不能装两个版本。** `environment.systemPackages` 里同时出现 `pkgs.vim` 和 `unstable.vim` 不成立。
2. **系统只能由一份 nixpkgs 构建。** 上面的 `nixosSystem` 用的是稳定版；unstable 只是「额外的包来源」，不能用来构建系统。
3. **unstable 的 unfree 包需要单独放行。** flake 的 pure 求值会挡住 `allowUnfree`，需要 `inherit (config.nixpkgs) config`，或改用 `nixpkgs-unfree`。

出处：同上；[LibrePhoenix · Using Both Stable and Unstable Packages on NixOS](https://librephoenix.com/2024-02-10-using-both-stable-and-unstable-packages-on-nixos-at-the-same-time) `[社区实证]`（原文自我定位：「这是个 hacky 方案，应作为最后手段」）

### 6.4 逐个组件的正确做法

**① 浏览器**

先问一句：**真的需要吗？** nixpkgs 的 Chromium 包维护文档明确写着 —— 所有更新「全部被视为安全关键，应尽快移植到 stable 通道」。

出处：[nixpkgs · chromium README](https://github.com/NixOS/nixpkgs/tree/master/pkgs/applications/networking/browsers/chromium) `[仓库]`

**所以**：stable 分支的 Firefox / Chromium 本身就在持续收版本更新。先跑 `nix search nixpkgs firefox` 看版本，再决定要不要滚。

真要滚，用 `programs.firefox.package` 指向 unstable：

```nix
programs.firefox.package = unstable.firefox;
```

**为什么用这个选项而不是 overlay 整个 `firefox`**：`programs.firefox.*` 模块会把 `package` 包进它自己生成的 wrapper（配置、扩展、策略），换 `package` 是最小侵入。

出处：[NixOS Wiki · Firefox](https://wiki.nixos.org/wiki/Firefox) `[Wiki]`

**② Mesa**

**官方支持这条路径**（25.05 起）：

```nix
hardware.graphics.package   = unstable.mesa;
hardware.graphics.package32 = unstable.pkgsi686Linux.mesa;   # 32 位必须一起换
```

**两个选项在 26.05 中确实存在**：`hardware.graphics.package`（「提供默认驱动集的包」）与 `hardware.graphics.package32`（「提供 32 位驱动集的包」）。

出处：[MyNixOS · hardware.graphics](https://mynixos.com/options/hardware.graphics) `[官方选项]`；[NixOS Wiki · Mesa](https://wiki.nixos.org/wiki/Mesa) `[Wiki]`；NixOS 25.05 release notes `[官方]`

**但注意**：§6.1 的翻车案例用的就是这个官方选项，仍然出问题。**「官方支持」≠「一定不炸」。**

**NVIDIA 用户补充**：NVIDIA 走自己的 `nvidia` 驱动，不用 Mesa 的 `nouveau`，所以换 Mesa 一般不影响 NVIDIA 渲染；但会影响 Vulkan 层和 XWayland。**换完必须重启，不要只 `switch`。**

**③ 内核**

**先说结论：在 26.05 上，换内核完全不需要 unstable。** 正确做法是在**同一个 nixpkgs 内**选更新的内核分支：

```nix
# ✅ 推荐：同一个 stable nixpkgs 里的更新内核
boot.kernelPackages = pkgs.linuxPackages_latest;   # 26.05 上 = 7.2.9（与 unstable 逐字相同）
# 或
boot.kernelPackages = pkgs.linuxPackages_zen;      # 低延迟，仍在 stable 内
```

**为什么「不需要」**（§6.0 表的展开）：两个分支的内核别名指向同一个内核分支，且补丁版本号相同。

```nix
# nixos-26.05  pkgs/top-level/linux-kernels.nix:739-743
packageAliases = {
  linux_default = packages.linux_6_18;
  linux_latest  = packages.linux_7_2;      # ← 26.05 与 unstable 都是这一行
};

# 两边的 pkgs/os-specific/linux/kernel/kernels-org.json 里：
#   "7.2"  -> { version = "7.2.9";  lts = false; }
#   "6.18" -> { version = "6.18.55"; lts = true;  }
```

`pkgs/top-level/all-packages.nix:8224,8227` 把这两个别名暴露为 `pkgs.linuxPackages` / `pkgs.linuxPackages_latest`。**所以 `pkgs.linuxPackages_latest` 在 26.05 上就是 7.2.9。**

**那什么时候才真的不能跨源？—— 看你的机器有没有「树外内核模块」。**

| 你的情况 | 能否 `boot.kernelPackages = unstable.linuxPackages` | 原因 |
|---|---|---|
| **纯 AMD / Intel**（amdgpu / i915 在主线内核里） | ⚠️ 技术可行，**但拿不到任何东西** | 没有树外模块 → 不存在版本配对问题；**但 26.05 已经是 7.2.9，跨源等于白做** |
| **NVIDIA 闭源驱动** | ❌ **绝对不要** | `hardware.nvidia` 从**同一个 nixpkgs** 取 `nvidia.ko`。跨源 → 模块与内核不匹配 → 开机加载失败 → 可能进不去图形界面 |
| **ZFS**（`boot.zfs.enable`） | ❌ **绝对不要** | `zfs.ko` 必须与内核**精确**配对，跨源必炸 |
| **VirtualBox**（`virtualisation.virtualbox.host.enable`） | ❌ **绝对不要** | `vboxdrv` 同上 |

**技术上的风险点在哪**（即使你没有 NVIDIA/ZFS/VBox 也该知道）：

`boot.extraModulePackages` 的类型是 `listOf types.package`，而 NixOS 会把它拼进模块树（`nixos/modules/system/boot/kernel.nix:197-202`、`:394`）：

```nix
system.modulesTree = [ (lib.getOutput "modules" kernel) ] ++ config.boot.extraModulePackages;
```

**所以只要有任何模块往 `boot.extraModulePackages` 里塞一个「来自稳定 nixpkgs」的包，而内核来自 unstable，模块树里就会出现「为 6.18 编译的 .ko」和「7.2 的内核」并存。** 这是跨源换内核真正的失败模式 —— 不是内核本身，而是模块树。

**对 AMD 用户的实务建议**：

```nix
# 不要写这个 —— 它只会多拉一整份 nixpkgs，换来的内核版本一模一样
# boot.kernelPackages = unstable.linuxPackages_latest;   # ❌ 无意义

# 要更新的内核，这样写就够了：
boot.kernelPackages = pkgs.linuxPackages_latest;         # ✅ 7.2.9，来自你已有的 stable
```

**如果你确实需要比 7.2 更新的内核**（例如 7.3 出来了而 26.05 还没 rebase）：那才轮到跨源，且必须**先用 `nixos-rebuild build-vm` 验证、再 `nixos-rebuild boot` + 重启**，不要用 `switch`。

**④ NVIDIA 驱动**

```nix
hardware.nvidia.package = unstable.linuxPackages.nvidiaPackages.stable;
```

**同样必须连同 `boot.kernelPackages` 一起换**，否则模块与内核不匹配。**新手建议不动。**

**⑤ 游戏组件**

这三个是纯用户态，可以安全滚：

```nix
environment.systemPackages = [
  unstable.mangohud
  unstable.gamescope
  unstable.proton-ge-bin
];
```

**注意 `gamescope` 依赖 Mesa/Vulkan**：滚了 gamescope 但没滚 Mesa，可能出现 Vulkan 层版本不匹配。**要么一起滚，要么都不滚。**

**⑥ 把滚动包放在 Home Manager 层（风险最低的落地方式）**

```nix
# home-manager 里
home.packages = [
  inputs.nixpkgs-unstable.legacyPackages.${pkgs.system}.firefox
];
```

**为什么这样更好**：滚动包只影响你的用户环境，**不进系统 generation 的构建路径**。系统基座完全不受影响；出问题最多是那个程序打不开。

**这是「稳定基座 + 滚动组件」推荐的默认做法。**

### 6.5 flake 会锁版本吗？能自动换锁吗？

**先纠正一个前提**：

> **flake 做不到「不锁」。锁（`flake.lock`）是它的设计目的，是「可复现」的物理基础。**

但可以做到：**让锁自动刷新，全程无需人工介入**。你要的不是「不锁」，而是「自动换锁」。

| 路线 | 是否锁版本 | 能否全自动 | 可复现性 |
|---|---|---|---|
| channel + `nixos-rebuild switch --upgrade` | **不锁** | ✅ 全自动 | 低（无法复现历史状态） |
| flake（手动 `nix flake update`） | 锁 | ❌ | 高 |
| flake + 自动换锁 | 锁（但自动刷新） | ✅ 全自动 | 高 |

**所以：如果你真的想「不锁」，channel 路线才是你要的。代价是不可复现 —— 你无法回答「我三个月前那台机器是什么状态」。**

**四个自动化层次（按复杂度递增）**

**层次 1：官方 Wiki 的单配置方案**

```nix
system.autoUpgrade = {
  enable = true;
  flake = "/path/to/flake";
  flags = [
    "--print-build-logs"
    "--commit-lock-file"    # 自动提交更新后的 flake.lock
  ];
  dates = "02:00";
  randomizedDelaySec = "45min";
};
```

出处：[NixOS Wiki · Automatic system upgrades](https://wiki.nixos.org/wiki/Automatic_system_upgrades) `[Wiki]`

**⚠️ 历史陷阱**：该页面以前推荐 `flags = [ "--update-input" "nixpkgs" ]`，但 `--update-input` **已被废弃**（Nix 会警告 `'--update-input' is a deprecated alias for 'flake update' and will be removed in a future version`）。相关讨论见 [nixpkgs issue #349734](https://github.com/NixOS/nixpkgs/issues/349734) `[仓库]`，其中提议新增 `--update-all-inputs` 与模块选项 `updateFlakeInputs`。**按老教程配置会导致自动升级静默失败。**

**层次 2：两段式（社区实测，更可靠）**

社区实测结论：**必须先更新 lock 文件，再升级系统 —— 这就是 flake 的工作方式**，是两个独立操作。

```nix
{ pkgs, ... }:
{
  # ① 每天先刷新 flake.lock
  systemd.services.flake-update = {
    description = "Update flake inputs";
    unitConfig = {
      StartLimitIntervalSec = 300;
      StartLimitBurst = 5;
    };
    serviceConfig = {
      ExecStartPre = "${pkgs.networkmanager}/bin/nm-online";   # 等网络就绪
      ExecStart = "${pkgs.nix}/bin/nix flake update --flake /path/to/flake";
      Restart = "on-failure";
      RestartSec = "30";
      Type = "oneshot";
      User = "youruser";        # 用拥有该仓库的用户跑，避开 git 所有权问题
    };
    path = [ pkgs.nix pkgs.git pkgs.host pkgs.networkmanager ];
  };

  systemd.timers.flake-update = {
    wantedBy = [ "timers.target" ];
    timerConfig = {
      OnCalendar = "daily";
      Persistent = true;         # 错过时间点（关机）就补跑
    };
  };

  # ② 系统升级必须等 lock 刷新完
  systemd.services.nixos-upgrade = {
    after    = [ "flake-update.service" ];
    requires = [ "flake-update.service" ];
  };

  # ③ 系统自动升级
  system.autoUpgrade = {
    enable = true;
    flake = "path:///path/to/flake";
    flags = [ "--print-build-logs" ];
    dates = "02:00";
    randomizedDelaySec = "45min";
    allowReboot = false;         # 建议先关自动重启，留人工确认
  };
}
```

出处：[Discourse · How to automatically update flakes](https://discourse.nixos.org/t/how-to-automatically-update-flakes/72426) `[官方论坛]`（原帖作者实测多日确认该配置有效）

**关键点**：`nixos-upgrade.service` 用 `after` + `requires` 依赖 `flake-update.service`。**顺序错了就会出现「刷新了锁但没生效」或「升级用了旧锁」。**

**层次 3：CI 侧自动化（GitHub Actions）**

如果配置在 GitHub 仓库里，用 `DeterminateSystems/update-flake-lock` 定时提 PR：

```yaml
name: update-flake-lock
on:
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * 0'    # 每周日
jobs:
  lockfile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: DeterminateSystems/nix-installer-action@main
      - uses: DeterminateSystems/update-flake-lock@main
        with:
          pr-title: "Update flake.lock"
          pr-labels: [ dependencies, automated ]
```

**为什么这条最有价值**：**它在「应用」之前插入了一道审查**。lock 更新变成 PR → CI 跑 `nixos-rebuild dry-build` → 通过才合并 → 机器再拉取。

出处：[github.com/DeterminateSystems/update-flake-lock](https://github.com/DeterminateSystems/update-flake-lock) `[仓库]`

**层次 4：让 agent 接管（见 §6.7）**

**自动化必须配的三个护栏**

| 护栏 | 配置 | 为什么 |
|---|---|---|
| GC | `nix.gc.automatic = true;` + `--delete-older-than 30d` | 自动升级会快速堆积 generation，不清理会撑爆 `/boot` 和 `/` |
| 启动项上限 | `boot.loader.systemd-boot.configurationLimit = 10;` | `/boot` 分区很小，启动项太多会写不进去 |
| 不自动重启 | `system.autoUpgrade.allowReboot = false;` | 自动重启可能在你正在用电脑时发生 |

**另外两个必须处理的坑**（官方 Wiki 明确列出）：

```nix
# 坑 1：flake 仓库目录不属于 root，而 nixos-upgrade 以 root 运行
#   /root/.gitconfig 里加：
#   [safe]
#     directory = /path/to/flake

# 坑 2：root 没配 git 身份，提交 lock 文件时报 "unable to auto-detect email address"
systemd.services.nixos-upgrade.environment = {
  GIT_AUTHOR_NAME     = "NixOS Auto-upgrade";
  GIT_AUTHOR_EMAIL    = "root@mypc";
  GIT_COMMITTER_NAME  = "NixOS Auto-upgrade";
  GIT_COMMITTER_EMAIL = "root@mypc";
};
```

出处：[NixOS Wiki · Automatic system upgrades（Troubleshooting）](https://wiki.nixos.org/wiki/Automatic_system_upgrades) `[Wiki]`

### 6.6 有多少步骤？—— 四种口径的步骤清单

**先给结论，再拆解**：

| 口径 | 用什么 | 首次搭建 | 日常升级 | 每次要手工查版本？ | 可复现 |
|---|---|---|---|---|---|
| **A** channel | 只改 `configuration.nix` | **3 步** | **2 步** | ❌ channel 自动 | ❌ |
| **B** `fetchTarball` | 只改 `configuration.nix` | **3 步** | **2 步** | ✅ 每次手工查 hash | ⚠️ 钉了 hash 才可复现 |
| **C** `fetchGit` + `rev` | 只改 `configuration.nix` | **3 步** | **2 步** | ✅ 每次手工查 rev | ✅ |
| **D** flake + 手动换锁 | `flake.nix` + `configuration.nix` | **6 步** | **2 步** | ❌ | ✅ |
| **E** flake + 自动换锁 | 同上 + systemd timer | **8 步** | **0 步** | ❌ | ✅ |

> [!IMPORTANT]
> **「首次搭建」和「日常升级」必须分开算 —— 这是最容易被误解的一点。**
>
> flake 的「6 步」是**一次性**成本（写 `flake.nix`、`git init`、第一次 rebuild 生成 `flake.lock`）。搭完之后，每天升级只有 2 步；配了自动换锁就是 0 步。
>
> **所以「flake 是不是比 channel 麻烦」的正确答案是：一次性多花 3 步，换回「日常可复现 + 只滚一个组件」。**

#### 口径 A：channel（只用 `configuration.nix`）—— 首次 3 步

```bash
# ① 加 unstable channel 并拉取
sudo nix-channel --add https://nixos.org/channels/nixos-unstable nixos-unstable
sudo nix-channel --update
```

② 改 `configuration.nix`：加 `let` 块 + 引用（见 §6.2 路 A）

```bash
# ③ 应用
sudo nixos-rebuild switch
```

**日常升级 = 2 步**：

```bash
sudo nix-channel --update     # ① 刷新 channel
sudo nixos-rebuild switch     # ② 重建
```

**⚠️ 这条路没有「只滚一个组件」的能力** —— `nix-channel --update` 把整个 unstable 拉新，凡是写了 `unstable.*` 的地方全动。这就是 §6.2 表里「锁版本 ❌」的实际含义。

#### 口径 B / C：`fetchTarball` / `fetchGit`（只用 `configuration.nix`）—— 首次 3 步

```bash
# ① 取 hash（B 路）或 rev（C 路）
nix-prefetch-url --unpack https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz
# 或
git ls-remote https://github.com/NixOS/nixpkgs refs/heads/nixos-unstable
```

② 改 `configuration.nix`：写 `let` 块 + 引用（见 §6.2 路 B / 路 C）

```bash
# ③ 应用
sudo nixos-rebuild switch
```

**日常升级 = 2 步**：

```bash
# ① 手工改 configuration.nix 里那一行 hash / rev
# ② 重建
sudo nixos-rebuild switch
```

> [!NOTE]
> **这条路线的隐藏成本就在第 ① 步：手工去查新的 hash/rev 并改文件。**
>
> flake 并没有让「升级」这件事本身变简单 —— 它只是把这一步**自动化**了（`nix flake update` 替你改 `flake.lock`）。**理解了这一点，你就理解了 flake 的真实价值：它是「自动化的手工锁」。**

#### 口径 D：flake + 手动换锁 —— 首次 6 步

```bash
# ① 进入 flake 目录（惯例 /etc/nixos）
cd /etc/nixos
```

② 写 `flake.nix`（双 input：`nixpkgs` = `nixos-26.05`，`nixpkgs-unstable` = `nixos-unstable`）—— 见 §6.3

③ 写 `configuration.nix` 的 `let` 块 + 4 行引用 —— 见 §6.3

④ （可选）加 `_module.args.pkgsUnstable = unstable;`，方便 Home Manager 层复用同一个 unstable —— 见 §6.3

```bash
# ⑤ 纳入 git（flake 要求文件在 git 仓库里，否则会警告「Git tree is dirty」）
sudo git init && sudo git add flake.nix configuration.nix
```

```bash
# ⑥ 第一次 rebuild —— 这一步才会生成 flake.lock
sudo nixos-rebuild switch --flake /etc/nixos#mypc
```

**日常升级 = 2 步**：

```bash
nix flake update nixpkgs-unstable                      # ① 只换 unstable 这一个 input 的锁
sudo nixos-rebuild switch --flake /etc/nixos#mypc      # ② 重建
```

> [!TIP]
> **`nix flake update nixpkgs-unstable` 只动一个 input 的锁，基座 `nixpkgs` 的锁完全不变。**
>
> 这就是「稳定基座」在 flake 里的**物理保证** —— 不是靠你记得别改，而是靠 `flake.lock` 里那个 input 的 hash 没动。**channel 路线做不到这一点。**

#### 口径 E：flake + 自动换锁 —— 首次 8 步，日常 0 步

在口径 D 的 6 步之后加：

⑦ 加 `systemd.services.flake-update` + `systemd.timers.flake-update`（§6.5 层次 2 的完整配置）

⑧ 加三个护栏：`system.autoUpgrade`、`nix.gc.automatic`、`boot.loader.systemd-boot.configurationLimit`（§6.5）

之后日常升级 = **0 步**（定时器自动跑）。**但建议保留最后一步人工确认**（见 §6.7 的风险分级）—— 自动换锁 ≠ 自动应用，把 `switch` 那一步留给人。

#### 三种口径共用的一件事：内核不要跨源

**呼应 §6.0 与 §6.4 ③**：无论你走哪条路，**都不要写 `unstable.linuxPackages_latest`**。纯 AMD/Intel 用户直接：

```nix
boot.kernelPackages = pkgs.linuxPackages_latest;   # 26.05 上 = 7.2.9，与 unstable 逐字相同
```

这一行属于**基座 nixpkgs**（`pkgs` 不是 `unstable`），跟着基座走。NVIDIA / ZFS / VirtualBox 用户同理，而且**必须**用基座的 —— 因为树外内核模块只能与同源内核配对。

### 6.7 让 agent 接管整个闭环

**可以，而且这是 NixOS 相对其他发行版最有优势的场景。** 因为「验证」这一步在 NixOS 上是**零成本的**：

```bash
nixos-rebuild dry-build    # 不产生副作用，只验证配置是否成立
```

传统发行版里让 LLM 改系统配置是危险的，因为你无法在不承担风险的情况下验证。NixOS 有 `dry-build` 和 `build-vm`，等于给了 LLM 一个**沙盒试衣间**。

**推荐的 agent 闭环架构**

```
① 触发：systemd timer（每日/每周）
        ↓
② 采集状态（喂给 agent 的「地面真值」）
   nixos-rebuild list-generations
   nix eval --json .#nixosConfigurations.mypc.config
   nix flake metadata
   df -h /nix ; 当前 firefox / mesa / 内核版本
        ↓
③ agent 决策：是否需要动？动什么？
   · 只是刷新 lock   → nix flake update
   · 需要加包/改配置 → 生成 diff
   · 无变化          → 直接退出，不产生任何改动
        ↓
④ 硬闸门（不可跳过）
   nixos-rebuild dry-build --flake .#mypc
   失败 → 丢弃改动 + git checkout . + 退出码 1
        ↓
⑤ 风险分级
   只动叶子包        → 直接 switch
   动了内核/驱动/boot → 必须 build-vm 或人工确认
        ↓
⑥ 应用 + 记录
   git commit（留痕，可 bisect）
   nixos-rebuild switch --flake .#mypc
        ↓
⑦ 健康检查
   systemctl is-system-running
   systemctl --failed
   失败 → nixos-rebuild switch --rollback
```

**给 agent 的 prompt 模板（每日巡检）**

```text
你是 NixOS 26.05 运维 agent。当前系统是「稳定基座 + 滚动叶子包」策略。

目标：
- 基座 nixpkgs 固定在 nixos-26.05，不要改
- 只允许更新 nixpkgs-unstable 这个 input
- 只允许改动 environment.systemPackages 里来自 unstable 的叶子包

严格禁止（无论任何理由）：
- 修改 system.stateVersion / home.stateVersion
- 修改 boot.loader.* / boot.kernelParams / fileSystems
- 修改 boot.kernelPackages 或 hardware.nvidia.*
- 执行 nix-collect-garbage -d
- 引入任何新的第三方 flake

工作流程（必须按顺序，任一步失败立即停止并报告）：
1. 运行 nix flake metadata 与 nixos-rebuild list-generations，报告当前状态
2. 运行 nix flake update nixpkgs-unstable
3. 运行 nixos-rebuild dry-build --flake .#mypc
4. dry-build 失败 → git checkout . && 报告失败原因，结束
5. dry-build 成功 → 报告将要发生的版本变化（哪些包从什么版本到什么版本）
6. 输出建议，等待人工确认后再执行 switch

不要自行执行 switch。不要自行执行 reboot。
```

**为什么第 6 步要停下来等人工确认**：自动升级 + 无验证 = 无人值守炸机。**「能自动」不等于「应该全自动」。** 合理的分工是：agent 负责「发现、验证、准备」，人负责「最后按一下」。

**进阶：只把低风险部分全自动**

```text
风险分级：
· 全自动（无需确认）：nix flake update nixpkgs-unstable + dry-build + switch
  —— 仅当 diff 只涉及 environment.systemPackages 里的叶子包时
· 需要确认：任何涉及 hardware.* / programs.steam / boot.* 的改动
· 禁止自动：stateVersion / bootloader / 分区 / 跨大版本（26.05 → 26.11）
```

**封装成 skill 的目录结构**

```text
nixos-rolling-ops/
├── SKILL.md                      # 策略声明 + 硬约束 + 风险分级表
├── scripts/
│   ├── collect-state.sh          # 采集当前状态，输出 JSON 喂给 LLM
│   ├── gate.sh                   # dry-build 闸门，失败即退出码 1
│   ├── risk-classify.sh          # 解析 git diff，判断风险等级
│   ├── apply.sh                  # git commit + switch
│   └── healthcheck.sh            # 检查 failed units，失败则 rollback
├── prompts/
│   ├── daily-check.md            # 每日巡检模板
│   ├── component-bump.md         # 单组件升级模板
│   └── explain-diff.md           # 解释版本变化
└── checklists/
    └── rolling-safety.md         # 「能滚 / 不能滚」判据表
```

### 6.8 社区案例汇总

| 来源 | 做法 | 结果 | 教训 |
|---|---|---|---|
| [Discourse 2026-05](https://discourse.nixos.org/t/mesa-unstable-on-nixos-stable-in-2026/77618) | stable 上用 `hardware.graphics.package = unstable.mesa` | ❌ Firefox 无硬件加速、Steam 仍用旧 Mesa、GNOME 风扇狂转 | 官方选项 ≠ 不炸；Mesa 要 32/64 位一起换 |
| [Discourse 2024-08](https://discourse.nixos.org/t/mixing-stable-and-unstable-packages-on-flake-based-nixos-system/50351) | 双 nixpkgs input + `_module.args.pkgsUnstable` | ✅ 可行 | 原帖编者按：「**我强烈建议不要在同一系统上混用 stable 与 unstable。这是不受支持的**」 |
| [Discourse 2026-05](https://discourse.nixos.org/t/installing-both-stable-and-unstable-packages-in-a-flake/77652) | 双 input 装包 | ⚠️ 有限制 | unstable 的 unfree 包需单独处理（`nixpkgs-unfree`） |
| [LibrePhoenix 2024-02](https://librephoenix.com/2024-02-10-using-both-stable-and-unstable-packages-on-nixos-at-the-same-time) | `specialArgs` 传 `pkgs-unstable` | ✅ 可行 | 作者自述：「这是个 hacky 方案，应作为最后手段」；**同一包不能装两个版本** |
| [Discourse 2025-11](https://discourse.nixos.org/t/how-to-automatically-update-flakes/72426) | `flake-update.service` + `nixos-upgrade.service` 依赖 | ✅ 实测有效 | 「必须先更新 lock，再升级 —— 这就是 flake 的工作方式」 |
| [nixpkgs #349734](https://github.com/NixOS/nixpkgs/issues/349734) | 老方案用 `--update-input nixpkgs` | ⚠️ 已废弃 | 社区 Wiki 旧写法会导致自动升级静默失败 |
| [update-flake-lock](https://github.com/DeterminateSystems/update-flake-lock) | GitHub Action 定时提 PR | ✅ | CI 侧自动化，**在应用前插入审查环节** |
| [NixOS Wiki · Automatic upgrades](https://wiki.nixos.org/wiki/Automatic_system_upgrades) | `system.autoUpgrade` + `flake` + `--commit-lock-file` | ✅ 官方推荐 | 需处理 git 所有权与身份两个坑 |

**综合这些案例，最稳的落点是**：

1. **系统基座**：`nixos-26.05`，不滚
2. **内核 / NVIDIA 驱动**：不滚（用同一 nixpkgs 的 `linuxPackages_latest`）
3. **Mesa**：谨慎滚，32/64 位一起；NVIDIA 用户影响小
4. **浏览器 / 游戏组件**：放 Home Manager 层滚，缩小爆炸半径
5. **自动化**：`flake-update.service` + `system.autoUpgrade`，或 GitHub Action 提 PR
6. **agent**：负责「采集 → 验证 → 准备」，人负责「按下开关」

### 6.9 一句话决策

> **基座不动、叶子放 Home Manager、内核驱动永不跨源、锁自动换但最后一步留给人。**

---

<a id="七"></a>
## 七、长期运维与跨版本升级

### 7.1 generation 管理与回滚

```bash
# 查看系统 generation 列表
sudo nixos-rebuild list-generations
sudo nix-env --list-generations --profile /nix/var/nix/profiles/system

# 回滚
sudo nixos-rebuild switch --rollback

# 在 bootloader 菜单里选旧 generation 启动（图形界面挂掉时的救命手段）
```

**为什么比传统发行版可靠**：见 §1.3。旧 generation 的 closure 在被 GC 前完整存在。

### 7.2 磁盘占用与清理

**`/nix/store` 膨胀的常见原因**：

1. 每次 rebuild 产生一棵新的完整 closure
2. 旧 generation 从未清理
3. 同时订阅多个 channel / 多个 nixpkgs 版本
4. dev shell 与临时 `nix-shell` 缓存

**工具**：

```bash
# 查看 store 占用
du -sh /nix/store

# 硬链接去重（相同文件只存一份，节省大量空间）
sudo nix-store --optimise
# 或新命令
sudo nix store optimise

# 交互式查看依赖树，定位占用大户
nix-tree /run/current-system      # 需先 nix shell nixpkgs#nix-tree

# 校验 store 完整性
sudo nix-store --verify --check-contents

# GC：保留最近 30 天
sudo nix-collect-garbage --delete-older-than 30d
# ⚠️ -d 会删掉全部旧 generation，等于摧毁回滚点，谨慎使用
sudo nix-collect-garbage -d
```

**为什么 `auto-optimise-store` 值得开**：它在新路径加入 store 时增量地做硬链接去重，避免事后全量 `optimise` 的巨大开销。

> 出处：[nix.dev · nix-store optimise](https://nix.dev/manual/nix/stable/command-ref/nix-store/optimise) `[官方]`；[github.com/utdemir/nix-tree](https://github.com/utdemir/nix-tree) `[仓库]`

### 7.3 跨版本升级：26.05 → 26.11

**路线一：channel（非 flake 配置）**

```bash
# 查看当前订阅
nix-channel --list | grep nixos

# 切到 26.11（末尾的 nixos 是 channel 名，不能省）
sudo nix-channel --add https://nixos.org/channels/nixos-26.11 nixos
sudo nixos-rebuild switch --upgrade
```

**⚠️ 官方警告**：新版 NixOS 可能附带新版本 Nix，会**升级 Nix 数据库 schema**，此操作**不可轻易回退**。

**路线二：flake**

```nix
# flake.nix
inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.11";
```

```bash
nix flake update nixpkgs
sudo nixos-rebuild switch --flake .#mypc
```

**自动升级**（可选）：`system.autoUpgrade.enable = true;` + `system.autoUpgrade.allowReboot`。

> 出处：[NixOS Manual · Upgrading](https://nixos.org/manual/nixos/stable/#sec-upgrading) `[官方]`

### 7.4 stateVersion 在升级时怎么处理

**结论：什么都不做。**

跨版本升级**不需要**改 `system.stateVersion`，也不需要改 `home.stateVersion`。它们只记录「首次生成的版本」，作用是让有状态数据的默认值保持稳定。

**唯一该改的情况**：某次 release notes 明确要求，且你已手动完成数据迁移。

> 出处：[NixOS Wiki · FAQ/When do I update stateVersion](https://wiki.nixos.org/wiki/FAQ/When_do_I_update_stateVersion) `[Wiki]`

### 7.5 升级前检查清单（照做即可）

```bash
# 1. 先看 breaking changes
#    https://nixos.org/manual/nixos/stable/release-notes  → 找 "Backward Incompatibilities"
#    或 GitHub: nixos/doc/manual/release-notes/rl-2611.section.md

# 2. 磁盘空间够不够（升级需要额外几十 GB 临时空间）
df -h /nix

# 3. 确认旧 generation 还在（回滚点）
sudo nixos-rebuild list-generations

# 4. 求值 + 构建闸门（不激活）
sudo nixos-rebuild dry-build --flake .#mypc

# 5. 在虚拟机里真跑一遍（最有价值的验证）
sudo nixos-rebuild build-vm --flake .#mypc
./result/bin/run-mypc-vm

# 6. 校验 store 完整性
sudo nix-store --verify --check-contents

# 7. 正式升级
sudo nixos-rebuild switch --flake .#mypc
```

**为什么第 5 步最有价值**：`build-vm` 生成一个可以直接启动的 QEMU 虚拟机，用的是你即将部署的**完全相同**的系统 closure。它能在不冒风险的前提下暴露「驱动不兼容」「服务起不来」这类问题。

> 出处：[NixOS Wiki · nixos-rebuild](https://wiki.nixos.org/wiki/Nixos-rebuild) `[Wiki]`

**26.11 值得注意的变化**（升级前必读）：
- 新安装的默认 PostgreSQL 版本为 v18（`system.stateVersion >= 26.11` 时生效）
- 引入了 `system.rebuild.enableNg` —— 新的 `nixos-rebuild` 实现，可用它替代旧版

> 出处：[NixOS Manual · unstable release notes](https://nixos.org/manual/nixos/unstable/release-notes) `[官方]`；[nixpkgs rl-2611.section.md](https://github.com/NixOS/nixpkgs/blob/master/nixos/doc/manual/release-notes/rl-2611.section.md) `[仓库]`

### 7.6 稳定性策略

**stable + unstable 混用的风险**：两个 nixpkgs 意味着依赖图跨两个世界，容易出现 ABI 不匹配、库版本冲突，且构建量翻倍。

**正确做法：用 overlay 只把单个包固定到 unstable**

```nix
{ inputs, pkgs, ... }:
{
  nixpkgs.overlays = [
    (final: prev: {
      # 只把 neovim 换成 unstable 版本，其余全部保持 stable
      neovim = inputs.nixpkgs-unstable.legacyPackages.${pkgs.system}.neovim;
    })
  ];
}
```

**为什么这比「整个系统切 unstable」安全**：影响面被限制在一个包内，其余几百个包的版本配对关系不变。

**stateVersion 相互独立**：`system.stateVersion`（NixOS）与 `home.stateVersion`（Home Manager）各管各的，改一个不影响另一个。

> 出处：[MyNixOS · home.stateVersion](https://mynixos.com/home-manager/option/home.stateVersion) `[官方选项]`

### 7.7 备份策略

**该备份什么**：

| 对象 | 为什么 |
|---|---|
| `/etc/nixos/` 或你的 flake 仓库 | 配置即代码。有它就能在任何机器上重建整个系统 |
| `/home` 里的**数据**（文档、存档、照片） | 配置可重建，数据不可重建 |
| 密钥（`/etc/ssh/ssh_host_*`、GPG、密码管理器数据库） | 不可重新生成 |

**不该依赖备份的**：`/nix/store` 本身。它可以从配置完全重建。

```nix
# 把 configuration.nix 拷进 store 供系统引用（便于事后追溯）
system.copySystemConfiguration = true;
```

**为什么配置必须进 git**：

1. 每次改动有 commit → 出问题能 `git diff` 找出改了什么
2. 可以多机共享同一份配置
3. `git bisect` 可以定位「哪次改动引入了问题」
4. 换机器时 `git clone` + `nixos-rebuild` 就恢复了

> 出处：[NixOS Manual · Configuration](https://nixos.org/manual/nixos/stable/) `[官方]`；[NixOS Wiki · nixos-generate-config](https://wiki.nixos.org/wiki/Nixos-generate-config) `[Wiki]`

---

---

<a id="八"></a>
## 八、Nix 生态查询工具链

> NixOS 的痛点从来不是「装不上」，而是**找不到**：包在不在、选项叫什么、这个版本对应哪个 commit、这个 lib 函数怎么用。
> 下面这五个站点各解决一块。**它们同时也是喂给 LLM 的「地面真值」来源。**

### 8.1 五个工具的分工

| 工具 | 回答什么问题 | 运营方 | 有公开 API | 免费 |
|---|---|---|---|---|
| **search.nixos.org** | 包 / **选项** / 三方 flake 的**当前**状态 | NixOS 官方 | ⚠️ 后端是 ES，凭据非官方公开 | ✅ |
| **NixHub.io** | **历史版本**：某包某版本对应哪个 nixpkgs commit | Jetify | ✅ v2 REST | ✅（限流） |
| **FlakeHub** | flake 的 semver 发布与分发 | Determinate Systems | ✅ 部分 | ⚠️ Cache 需付费 |
| **Noogle** | `lib` / `builtins` / `pkgs` 里的**函数**文档 | nix-community | ✅ 全量 JSON | ✅ |
| **Jetify / Devbox** | 用 Nix 做开发环境，**不写 Nix 语言** | Jetify | — | ✅ |

**一句话记法**：

- 要查**选项** → search.nixos.org（唯一权威）
- 要查**旧版本** → NixHub
- 要**分发 flake** → FlakeHub
- 要写**函数** → Noogle
- 要**避开 Nix 语言** → Devbox

---

### 8.2 search.nixos.org —— 官方搜索（选项搜索是它的核心价值）

**地址**：https://search.nixos.org

**三个标签页**：

| Tab | 搜什么 |
|---|---|
| Packages | nixpkgs 里的包 |
| **Options** | **NixOS 模块选项**（还有子分类：Official / Community(Home Manager) / External(Darwin) / Experimental） |
| Flakes | 三方 flake 及其提供的包/选项 |

> 出处：https://search.nixos.org/ `[官方]`

**Packages 的筛选器**：Channel、Package sets、Licenses、Maintainers、Teams、Platforms，外加排序（Best Match / 字母升序 / 降序）。

**⚠️ 没有 broken / insecure 筛选器** —— 社区有专门抱怨帖：
https://discourse.nixos.org/t/nixos-package-search-does-not-show-when-a-package-is-broken/78488 `[社区]`

**数据来源与更新频率**：

- 后端是 **Elasticsearch**（由 bonsai.io 赞助），前端 Elm
- 导入由 GitHub Actions 定时任务驱动，cron 为 `0 */2 * * *` —— **每 2 小时**重建一次索引
- 索引别名形如 `latest-{gen}-nixos-{channel}`，包/选项索引名为 `nixos-{gen}-{channel}-{commit}`
- 覆盖 unstable、26.05、25.11 及历史若干代（旧代保留一段时间后裁剪）

> 出处：https://github.com/NixOS/nixos-search `[官方]`（README 与 `.github/workflows/import-to-elasticsearch.yml`）

**深链接有效**（可直接分享/写进文档）：

```
https://search.nixos.org/packages?channel=unstable&show=firefox
https://search.nixos.org/options?channel=unstable&show=programs.steam.enable
```

**⚠️ 关于后端 API**：`search.nixos.org/backend/<索引别名>/_search` 确实是可用的 Elasticsearch 端点，但**需要 HTTP Basic 认证**，而凭据**从未由 NixOS 官方公开**（第三方项目 `mcp-nixos` 源码中有硬编码值）。

> **建议：不要自己抓这个端点。** 用 `mcp-nixos`（它已封装好）或直接用网页。把它当**非官方契约**，随时可能变。

**为什么选项搜索比包搜索重要**：

NixOS 是声明式配置，**用户实际写的是 option，不是 package**。而选项文档分散在成百上千个模块里，`man configuration.nix` 浏览效率极低。选项搜索能按名称/描述直达某个模块的**默认值、类型、示例和源码位置** —— 这是包搜索无法替代的。

> 出处：https://wiki.nixos.org/wiki/NixOS_search `[Wiki]`

**和 `nix search` 的区别**：

| | `nix search nixpkgs <name>` | search.nixos.org |
|---|---|---|
| 搜什么 | 可求值的 installable | 预建索引（包 + 选项 + 三方 flake） |
| 搜选项 | ❌ | ✅ |
| 需要本地有 nixpkgs | ✅（flake input 已锁） | ❌ |
| 依赖网络 | 首次要拉 | 要 |
| 输出 | 属性路径 + 版本 + description | 可筛选、可深链接 |

> 出处：https://nix.dev/manual/nix/latest/command-ref/new-cli/nix3-search `[官方]`

---

### 8.3 NixHub.io —— 查历史版本（本节最有实用价值）

**它解决什么问题**：nixpkgs 是滚动的，**查不到「某包在某个月是什么版本」**。NixHub 把每个包的历次版本映射到包含它的 nixpkgs commit。

- 主页：https://www.nixhub.io
- 运营方：**Jetify**（Devbox 的同一家）
- 规模：官方 API 文档称「**1 million package versions for over 100,000 Nix packages**」；主页称 40 万+ 版本
- 免费：个人使用免费，有速率限制

> 出处：https://www.jetify.com/docs/nixhub `[官方]`

**网页用法**：`https://www.nixhub.io/packages/<包名>`，例如 `https://www.nixhub.io/packages/firefox`

#### 公开 API（实测可用）

官方文档只给相对路径（`/v2/search`、`/v2/pkg`、`/v2/resolve`），**实际主机是 `https://search.devbox.sh`**。

> 出处：https://www.jetify.com/docs/nixhub `[官方]`；主机名为本文实测得出

```bash
# 按名字搜包
curl "https://search.devbox.sh/v2/search?q=firefox"

# 取某包的全部历史版本（含每版对应的 nixpkgs commit）
curl "https://search.devbox.sh/v2/pkg?name=firefox"

# 名字 + 版本 → 解析出 commit 与属性路径（这就是「固定版本」的关键）
curl "https://search.devbox.sh/v2/resolve?name=firefox&version=latest"
```

**实测返回（2026-10-12 真实抓取）**：

```json
{
  "name": "firefox",
  "version": "154.0.1",
  "summary": "Web browser built from Firefox source tree",
  "systems": {
    "x86_64-linux": {
      "flake_installable": {
        "ref": { "type": "github", "owner": "NixOS", "repo": "nixpkgs",
                 "rev": "c27cdad491a991b11ed731760aa2ef8db0cb0410" },
        "attr_path": "firefox"
      },
      "outputs": [{ "name": "out",
        "path": "/nix/store/...-firefox-154.0.1" }]
    }
  }
}
```

**版本匹配规则**：`latest` / 前缀（`1.21` → `1.21.13`）/ 精确版本。

**限流**：每个 IP 初始 1000 次配额，每请求 −1，每分钟回补 5 次；配额耗尽返回 `429`。

#### 固定某个包到指定版本（工作流）

**第 1 步**：用 API 拿到目标版本的 commit

```bash
curl -s "https://search.devbox.sh/v2/resolve?name=firefox&version=154" \
  | grep -o '"rev":"[a-f0-9]*"'
```

**第 2 步**：用这个 commit 引用 nixpkgs

```bash
# 命令行临时验证
nix shell github:NixOS/nixpkgs/<commit>#firefox
```

```nix
# configuration.nix —— 只把这一个包固定到旧版 nixpkgs
{ config, pkgs, lib, ... }:
let
  pinned = builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/<commit>.tar.gz";
    # sha256 = "...";   # 生产环境必须加 hash，否则每次 eval 都可能重新下载
  };
  pkgsPinned = import pinned {
    inherit (pkgs.stdenv.hostPlatform) system;
    inherit (config.nixpkgs) config;
  };
in
{
  programs.firefox.package = pkgsPinned.firefox;
}
```

**⚠️ 为什么用 `programs.firefox.package` 而不是覆盖 `pkgs.firefox`**：前者是模块化替换，只影响 Firefox；后者会牵动依赖树。

**⚠️ 实测观察（重要）**：本文核实（2026-10-12）时，`hello` 和 `firefox` 的 `latest` 都解析到**同一个 commit `c27cdad…`**，其 `date` 字段为 **2026-08-27**。

**这提示 NixHub 的索引可能并非实时同步**（滞后数周）。**用它做版本决策前，务必核对返回的 `date` / `last_updated` 字段，并与 search.nixos.org 交叉验证。**

**另一种「固定版本」的思路（推荐给长期使用）**：不用 NixHub，而是把整个 nixpkgs 固定到某个 commit —— 这就是 flake 的 `flake.lock` 在做的事。NixHub 适合**「只回退一个包」**的场景。

---

### 8.4 FlakeHub —— flake 的语义化版本与分发

**它解决什么问题**：Nix 本身**没有 SemVer 概念**，flake 难以发现、难以复用、更新粒度粗。

官方一句话原文：
> *"FlakeHub is a platform for publishing and discovering Nix flakes built by Determinate Systems."*

> 出处：https://docs.determinate.systems/flakehub/ `[官方]`

#### 核心创新：给 flake 加 SemVer

> *"Nix by itself has no built-in concept of semantic versioning (SemVer). FlakeHub enables you to use a subset of SemVer with your Nix flakes."*

URL 结构：`https://flakehub.com/f/:org/:project/:version-req`

| 写法 | 含义 |
|---|---|
| `*` | 最高已发布版本 |
| `1.*` | 主版本为 1 的任意版本 |
| `1.2.*` | 主次版本为 1.2 |
| `=3.2.1` | 精确锁定 |
| `0.1.1` | 至少 0.1.1，但不会升到 0.2.0 |

官方称其求解器行为「像 Cargo 的版本求解器」。

> 出处：https://docs.determinate.systems/flakehub/concepts/urls/ 与 `/concepts/semver/` `[官方]`

**nixpkgs 在 FlakeHub 上的版本映射**：

| FlakeHub 版本 | 对应 nixpkgs |
|---|---|
| `0` / `*` | 最新稳定 |
| `0.2605` | `nixos-26.05` 分支最新 |
| `0.1` | unstable |

```nix
# 等价写法对照
inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
inputs.nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.2605";   # 同一个东西
```

**完整可用示例**：

```nix
{
  inputs = {
    # 通配：始终取最高已发布版本
    fh.url = "https://flakehub.com/f/DeterminateSystems/fh/*";
    # 精确版本
    agenix.url = "https://flakehub.com/f/ryantm/agenix/=0.13.0";
    # 主版本范围
    nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.2605";
  };
  outputs = { nixpkgs, fh, ... } @ inputs: { };
}
```

> 出处：https://docs.determinate.systems/flakehub/ `[官方]`

#### `fh` CLI

```bash
# 安装（官方方式：从 FlakeHub 拉取，本地构建）
nix shell "https://flakehub.com/f/DeterminateSystems/fh/*"
```

**常用子命令**：`fh add`（加 input）、`fh init`（生成 flake.nix）、`fh search`、`fh list flakes|orgs|releases|versions`、`fh apply`（从 Cache 部署 NixOS/Home Manager/nix-darwin）、`fh resolve`、`fh fetch`、`fh convert`、`fh eject`、`fh login`。

**⚠️ 发布不是 `fh publish`** —— 是 GitHub Action `DeterminateSystems/flakehub-push`。

> 出处：https://docs.determinate.systems/flakehub/cli/ `[官方]`

#### FlakeHub Cache（付费）

官方原文：**"FlakeHub Cache is available only on paid plans."**

| | `cache.nixos.org` | FlakeHub Cache |
|---|---|---|
| 覆盖 | 整个 store | per-flake / per-repo 细粒度 |
| 认证 | 无 | JWT |
| 谁可推送 | 任何人 | 仅 trusted builders（GitHub Actions / GitLab CI / Semaphore / Buildkite） |
| 价格 | 免费 | Individual $7/月；Team $20/用户/月 |

**Free 层只含公开 flake，不含 Cache。**

> 出处：https://docs.determinate.systems/flakehub/cache/ 与 https://flakehub.com/pricing `[官方]`

#### Determinate Nix

官方原文：
> *"Determinate Nix is Determinate Systems' validated and secure downstream distribution of NixOS/nix designed for enterprise use cases."*

即**上游 Nix 的下游发行版**。**它默认启用 flakes**，不需要写 `experimental-features`：

> *"By default, it installs Determinate Nix, which enables flakes"*

> 出处：https://docs.determinate.systems/determinate-nix/ 与 https://github.com/DeterminateSystems/nix-installer `[官方]`

#### API（部分有官方文档）

```bash
# 某 flake 的全部发布（官方文档记载）
curl -H "Accept: application/json" "https://api.flakehub.com/f/NixOS/nixpkgs/releases"

# 匹配版本约束的最新版本（官方文档记载）
curl -H "Accept: application/json" "https://api.flakehub.com/version/NixOS/nixpkgs/0.1"

# 按名字搜索（官方文档未记载，实测可用；建议带 User-Agent）
curl -H "Accept: application/json" -H "User-Agent: my-client/1.0" \
  "https://api.flakehub.com/search?q=home-manager"
```

> 出处：https://docs.determinate.systems/flakehub/discovery/ `[官方]`（前两个端点）

#### ⚠️ 争议（用之前必须知道）

FlakeHub 发布时（2023-08-22）在 NixOS Discourse 上有明确批评，有成员认为 DetSys「不推动 flakes 稳定化，反而在其上做产品」，并批评其版本方案是「第三方的、中心化的、专有的，且似乎无意上游化」。

> 出处：https://discourse.nixos.org/t/introducing-flakehub/32044 `[社区]`

**更广的治理背景**：2024-04 的 Nix 社区公开信与 NixOS Foundation 领导层危机，Nix 作者兼 DetSys 联合创始人 Eelco Dolstra 涉其中（后辞去基金会董事）。

> 出处：https://lwn.net/Articles/970824/ `[媒体]`

**技术上的具体权衡**：FlakeHub 上的 nixpkgs 实际由 **DetSys 的镜像仓库**提供（实测 API 返回的 `repo_url` 指向 `DeterminateSystems/flakehub-mirror`）。这意味着你多了一个中间层。

| | 用 `github:NixOS/nixpkgs/nixos-26.05` | 用 `flakehub.com/f/NixOS/nixpkgs/0.2605` |
|---|---|---|
| 权威性 | 上游官方 | 经 DetSys 镜像 |
| 免费缓存 | `cache.nixos.org` | Cache 需付费 |
| 版本表达 | 分支名（无 semver） | **SemVer 约束** |
| `nix flake update` 行为 | 拉到分支最新 | **只在允许范围内升级** |
| 停服风险 | 无 | 有（官方另设 "Service availability" 页） |

**建议**：**日常用上游 GitHub 源**。只有当你确实需要「SemVer 约束 + 团队分发 + 细粒度缓存权限」时才引入 FlakeHub。

---

### 8.5 Noogle —— Nix 函数搜索引擎

**它解决什么问题**：写配置时想「有没有一个把 list 转成 attrs 的函数」，但你不知道它叫什么。

- 地址：https://noogle.dev
- 仓库：https://github.com/nix-community/noogle（MIT，maintainer `@hsjobeki`）
- **索引范围**：`builtins`、`lib`、**以及 `pkgs`** 里的函数

> 出处：https://wiki.nixos.org/wiki/Noogle `[Wiki]`

**返回什么**（以 `lib.mkIf` 为例）：**类型签名、文档注释、源码位置（文件/行/列）、别名、示例**。

**最有用的两个功能**：

1. **按类型签名过滤** —— 搜「从 list 到 attrset 的函数」：
   `https://noogle.dev/q?term=map&from=list&to=list&limit=20`
2. **别名检测** —— 自动告诉你 `lib.mkIf` 同时也是 `lib.modules.mkIf`

**单函数页**：`https://noogle.dev/f/lib/mkIf/`

#### API

**⚠️ 你记忆中的 `noogle.dev/api/v1/search?query=...` 不存在** —— 实测返回 **404**。

**真实存在的公开端点**是全量数据下载：

```bash
# 全量数据集（约 4.4 MB JSON，实测 2145 条记录）
curl -s https://noogle.dev/api/v1/data -o noogle-data.json
```

返回结构：

```json
{ "data": [ { "meta": { "title": "lib.mkIf", "path": ["lib","mkIf"], "aliases": [...] },
              "content": { ... } }, ... ] }
```

**这意味着你可以把 Noogle 的全量索引下载到本地，喂给 LLM 或做本地检索 —— 无需联网、无需认证。**

> 出处：https://wiki.nixos.org/wiki/Noogle `[Wiki]`；端点由本文实测确认

**更新频率**：每天针对 nix master（builtins）与 nixpkgs（lib/pkgs）更新，变更次日生效。

**相比直接读 nixpkgs 源码的优势**：① 模糊搜索 + 类型签名过滤；② 自动检测别名；③ 直接给源码位置；④ 渲染好的文档注释；⑤ 全量 JSON 可离线使用。

---

### 8.6 Jetify / Devbox —— 不写 Nix 语言用 Nix

**先澄清归属**：**NixHub 是 Jetify 做的**。Jetify 是一家公司，旗下产品：

| 产品 | 是什么 |
|---|---|
| **Testpilot** | **AI QA / 端到端测试 agent —— 现在是 Jetify 的旗舰** |
| **Devbox** | 隔离开发环境 CLI（Apache-2.0） |
| **NixHub** | 包版本注册表 + API |
| **Jetify Cloud** | Jetify Cache（私有 Nix 缓存）、Jetify Secrets |

> 出处：https://www.jetify.com/docs `[官方]`

**Devbox 的定位**（官方原文）：
> *"an approachable, intuitive interface for creating development environments with the Nix Package Manager, **without the Nix language**"*

即**在 Nix 之上的封装**。它内部就是 Nix（README 原文 *"internally powered by nix"*）。

**在 NixOS 上安装**（官方文档专门列了 NixOS 选项）：

```bash
nix profile install nixpkgs#devbox
# 或要最新版
nix profile install github:jetify-com/devbox/latest
```

**⚠️ 已知限制（官方明示）**：走 nixpkgs 安装时「新版本 Devbox 需要先在 nixpkgs 里更新才可用」—— **版本会滞后**。要最新/预发布需用 flake 源。

> 出处：https://www.jetify.com/docs/devbox/installing-devbox/ `[官方]`

**固定版本的用法**（Devbox 的杀手功能）：

```bash
devbox add python@3.10          # 自动解析并写入 devbox.lock
```

对应 `devbox.json`：`"packages": ["python@3.10"]`

#### ⚠️ 两个必须澄清的误解

1. **`devbox generate` 不是 AI 功能。** 它生成 devcontainer / Dockerfile / direnv / readme 脚手架。
   > 出处：https://www.jetify.com/docs/devbox/cli-reference/devbox-generate `[官方]`
2. **Jetify 没有官方的 Devbox MCP server。** 搜到的 `devbox-mcp-server` 是 **Microsoft Dev Box**（Azure 产品），**与 Jetify Devbox 完全无关**。
   > 出处：https://github.com/microsoft/devbox-mcp-server `[仓库]`

**Jetify 的 AI 集中在 Testpilot，不在 Devbox。** 网上「Devbox 有 AI/MCP 集成」的说法未获官方证实。

---

### 8.7 串起来：一个真实工作流

**场景**：我要在 NixOS 上把 Firefox 固定到某个旧版本，并且**绝不编造选项名**。

```bash
# ① 查选项的准确名字、类型、默认值 —— search.nixos.org（唯一权威）
#    https://search.nixos.org/options?channel=unstable&show=programs.firefox.package

# ② 查历史版本 → 拿到 commit —— NixHub
curl -s "https://search.devbox.sh/v2/resolve?name=firefox&version=154" | grep -o '"rev":"[a-f0-9]*"'

# ③ 查 lib 函数（如果你要写条件判断）—— Noogle
#    https://noogle.dev/q?term=mkIf

# ④ 写进 configuration.nix（见 §8.3 的代码块）

# ⑤ 验证闸门 —— 这一步不可跳过
sudo nixos-rebuild dry-build
```

**第 ⑤ 步是关键**：前四步都在「查」，只有这一步在「验」。**Nix 的强类型选项系统会让错误的选项名在 eval 阶段立刻失败** —— 这就是为什么「查准」比「猜对」重要得多。

---

### 8.8 这些工具和 LLM 的关系

**`mcp-nixos` 已经把这五个数据源里的四个聚合了。** 它的数据源覆盖：

nixpkgs 包 · **NixOS 选项** · **Home Manager 选项** · nix-darwin · Nixvim · NVF · **FlakeHub** · **Noogle** · NixOS Wiki · nix.dev · **NixHub**

> 出处：https://github.com/utensils/mcp-nixos `[仓库]`

**这意味着两条路径**：

| 路径 | 适合 | 代价 |
|---|---|---|
| 人工查这五个站点 | 你在写配置、需要理解 | 慢，但你能学到东西 |
| 让 agent 通过 `mcp-nixos` 查 | 批量、重复、你不关心细节 | 需要装 MCP server |

**给 LLM 加这些工具的价值（一句话）**：**LLM 幻觉在 NixOS 上的代价是「系统起不来」，而这些工具提供的是可验证的地面真值。** 两者是互补的，不是替代的。

**Noogle 的特殊价值**：它的**全量 JSON 可下载**（`/api/v1/data`，约 4.4 MB，2145 条）。你可以把它塞进本地向量库或直接放进 context，**让 LLM 离线查 Nix 函数** —— 这是五个工具里唯一能做到「完全离线」的。

---

### 8.9 坑与反直觉

| 坑 | 事实 |
|---|---|
| `noogle.dev/api/v1/search` | **不存在**（实测 404）。真实端点是 `/api/v1/data`（全量） |
| NixHub API 主机名 | 官方文档**只给相对路径**，实际主机是 `https://search.devbox.sh`（本文实测） |
| NixHub 索引实时性 | 实测 `latest` 解析到 2026-08-27 的 commit，**可能滞后数周**，用前核对 `date` 字段 |
| search.nixos.org 后端 API | 存在但**需要 Basic Auth，凭据从未官方公开**。别自己抓，用 `mcp-nixos` |
| search.nixos.org 筛 broken | **没有这个筛选器**（社区有抱怨帖） |
| FlakeHub 上的 nixpkgs | 实际由 **DetSys 镜像**提供（`DeterminateSystems/flakehub-mirror`），不是直连上游 |
| FlakeHub 发布 flake | **不是 `fh publish`**，是 GitHub Action `flakehub-push` |
| `devbox generate` | **不是 AI 功能**，是脚手架生成器 |
| Devbox 的 MCP | **Jetify 没有官方 Devbox MCP**；`devbox-mcp-server` 是 Microsoft Azure 的东西 |
| Jetify 的旗舰 | 现在是 **Testpilot**（AI 测试 agent），不是 Devbox |
| `nix search` 能不能搜选项 | **不能**。要搜选项只能用 search.nixos.org |
| FlakeHub Cache 免费吗 | **不免费**。Free 层只含公开 flake，不含 Cache |

<a id="九"></a>
## 九、LLM 辅助管理 NixOS

### 9.1 为什么 NixOS 特别适合 LLM 辅助

| 特性 | 对 LLM 的意义 |
|---|---|
| 配置是**声明式文本** | LLM 可以生成、阅读、diff，而不是教你在 GUI 里点哪里 |
| 有**单一事实来源** | LLM 读一个文件就能了解整机状态 |
| 有**强类型选项系统** | 错误选项名会被 eval 立刻拒绝 —— 幻觉有明确边界 |
| 有**dry-build 闸门** | 可以在不产生任何副作用的前提下验证 LLM 的输出 |
| 有**generation 回滚** | 即使闸门漏了，也能一键回到上一个可用状态 |

**这四点组合起来，让 NixOS 成为「LLM 辅助运维」最理想的发行版之一** —— 因为 LLM 最怕的「悄悄改坏系统、无法验证、无法回滚」在 NixOS 上全部不成立。

### 9.2 MCP 生态（2026-10-12 核实）

| 名称 | 仓库 | 状态 | 能做什么 |
|---|---|---|---|
| **mcp-nixos** | [github.com/utensils/mcp-nixos](https://github.com/utensils/mcp-nixos) | **活跃**（约 853★，最后 push 2026-09-05，MIT） | 只暴露 2 个工具：`nix`（search / info / stats / browse / cache / flake-inputs / store）与 `nix_versions`。数据源覆盖 nixpkgs 包、**NixOS 选项**、**Home Manager 选项**、nix-darwin、Nixvim、NVF、FlakeHub、Noogle、NixOS Wiki、nix.dev、NixHub。**无需本机装 Nix**，且已进 nixpkgs（`pkgs.mcp-nixos`） |
| TheCowboyAI/nixmcp | github.com/TheCowboyAI/nixmcp | `[未核实]` | GitHub 页面多次取回为空，描述与 mcp-nixos 逐字一致，疑似镜像/复制，**无法证实为独立维护项目，不建议使用** |
| mynixos.com 官方 API/MCP | — | `[未找到]` | 仅有网站与选项页，未见公开 API 或 MCP server |
| 通用 filesystem / shell MCP | — | 存在 | 非 NixOS 专用，但可让 LLM 读写 `/etc/nixos` |

> 出处：[github.com/utensils/mcp-nixos](https://github.com/utensils/mcp-nixos) `[仓库]`；[mcp-nixos.io](https://mcp-nixos.io/) `[仓库]`

**mcp-nixos 对 NixOS 运维的价值**：它把「这个选项叫什么、在哪个模块、默认值是什么」这件事变成可查询的事实，**直接压制 LLM 编造选项名这个最大风险源**。

### 9.3 给 LLM 喂上下文的标准姿势

**核心工具**：

```bash
# 1. 查询某个选项的定义、类型、默认值
nixos-option services.xserver.videoDrivers
#    25.05 起重写为「bash 脚本调用的 Nix 表达式」，26.05 仍可用

# 2. 查阅完整选项手册
man configuration.nix
nixos-help

# 3. 查询包
nix search nixpkgs <name>
#    或网页版 https://search.nixos.org

# 4. 导出当前系统的完整生效配置（给 LLM 的「地面真值」）
nix eval --json .#nixosConfigurations.mypc.config > current-config.json

# 5. 命令找不到时定位提供者
#    programs.command-not-found.enable = true;  ← NixOS 默认开启
nix-locate --top-level bin/htop      # 需 nix-index
```

**`nix-index` 是 command-not-found 的加强版**：预先索引整个 nixpkgs，能按文件路径反查包。

```nix
programs.command-not-found.enable = true;   # 基础版，NixOS 默认已开
# 加强版：nix-index + 预生成数据库
# https://github.com/nix-community/nix-index
# https://github.com/nix-community/nix-index-database （每日更新）
```

> 出处：[github.com/nix-community/nix-index](https://github.com/nix-community/nix-index) `[仓库]`；[NixOS Manual · unstable release notes（nixos-option 重写）](https://nixos.org/manual/nixos/unstable/release-notes) `[官方]`

**⚠️ 上面这些是「本机侧」的查询手段；「外部数据源」见 [第八章](#八)。**

第八章讲的五个站点（search.nixos.org / NixHub / FlakeHub / Noogle / Devbox）是**喂给 LLM 的地面真值**的主要来源。其中：

- **要查选项** → 用 search.nixos.org（`nixos-option` 只能查**已安装**系统里的选项，查不到「还没启用的模块」）
- **要查历史版本** → NixHub（`nix search` 只能查当前锁定的 nixpkgs）
- **要查 lib 函数** → Noogle（本地 `man` 完全没有）
- **`mcp-nixos` 把其中四个聚合成了 MCP tool** —— 这是给 agent 用的最短路径（见 §9.2 与 §8.8）

### 9.4 安全护栏流程（必须遵守）

```
┌─────────────────────────────────────────────────────────┐
│  LLM 生成配置改动                                        │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│  ① 人工审阅 diff（不接受「直接改完就 switch」）           │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│  ② nixos-rebuild dry-build --flake .#host               │
│     ← 求值 + 构建闸门。选项名错/类型错，这里就会失败      │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│  ③ 涉及内核/驱动/bootloader/分区？                       │
│     是 → build-vm 里真跑一遍，或先 nixos-rebuild boot    │
│     否 → 继续                                            │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│  ④ nixos-rebuild switch                                  │
└────────────────────┬────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│  ⑤ 出问题 → nixos-rebuild switch --rollback（秒级回退）  │
└─────────────────────────────────────────────────────────┘
```

**为什么 dry-build 是关键的验证闸门**：Nix 的选项系统是强类型的。LLM 编造一个不存在的选项（例如把 `programs.mangohud` 写进 NixOS 配置），**eval 阶段就会报错并指出具体路径**。这意味着幻觉不会「悄悄生效」，而是被立刻拦下。

**为什么必须人工确认**：LLM 幻觉在 NixOS 上的代价不是「程序报错」而是「系统起不来」。以下四类改动必须人工确认：

1. `boot.kernelParams` — 写错可能无法引导
2. `boot.loader.*` — 写错可能丢失启动项
3. `fileSystems` — 写错可能挂载失败、无法进入系统
4. `system.stateVersion` — 写错可能损坏有状态数据

> `[核实]` 上述四类均为 NixOS 引导链路关键项，出错代价高于普通包配置

### 9.5 可复用的 Prompt 模板

**模板 1：读配置给 diff**

```text
你是 NixOS 26.05 专家。下面是我的 configuration.nix。

要求：
1. 只输出 unified diff，不要输出完整文件。
2. 禁止使用任何你无法确认在 NixOS 26.05 中存在的选项名。
3. 每个新增选项后加一行注释，说明它的作用和来源（模块路径或官方手册章节）。
4. 如果需要引用第三方 flake，单独列一节说明引入方式和风险。

我的配置：
<粘贴 configuration.nix>
```

**模板 2：生成 flake + home-manager 骨架**

```text
生成一份最小可用的 NixOS flake 骨架，要求：
- inputs: nixpkgs 固定到 nixos-26.05；home-manager 固定到 release-26.05，且 follows nixpkgs
- outputs 含 nixosConfigurations.<hostname>
- 内含 home-manager.nixosModules.home-manager，并设 useGlobalPkgs = true
- 机器为 x86_64-linux，主机名 mypc，用户名 me
- 每个 input 后注释说明为什么锁定这个分支
```

**模板 3：解释报错**

```text
这是 nixos-rebuild 的报错。请按以下结构回答：
1. 报错涉及的选项路径 / derivation
2. 错误类型（eval 错误 / 构建错误 / 激活错误）
3. 根因（一句话）
4. 最小修复方案（给出可直接粘贴的 diff）
5. 明确标注你不确定的部分

报错：
<粘贴报错>
```

**模板 4：升级前审查**

```text
我要从 NixOS 26.05 升级到 26.11。请：
1. 列出 26.11 release notes 中与本配置相关的 breaking changes
2. 指出我的配置里哪些选项可能被重命名或移除
3. 给出升级前的检查清单
4. 如果某个选项被移除，给出对应的新写法
注意：只引用你能给出出处的信息，不确定的标「需人工核实」。

我的配置：
<粘贴 configuration.nix>
```

### 9.6 把 NixOS 运维封装成 skill

如果把上面这套流程封装成一个 agent skill，建议的目录结构：

```text
nixos-ops-skill/
├── SKILL.md                    # 触发条件、边界、护栏说明
├── scripts/
│   ├── preflight.sh            # dry-build + build-vm + store 校验 + 磁盘检查
│   ├── upgrade.sh              # channel / flake 升级封装（含备份）
│   ├── gc.sh                   # 保留 N 天的 GC，绝不使用 -d
│   ├── rollback.sh             # 回滚 + 确认 generation 存在
│   └── export-options.sh       # nix eval --json 导出当前配置给 LLM
├── checklists/
│   ├── upgrade.md              # 升级前 / 中 / 后清单
│   ├── rollback.md             # 回滚步骤（含图形界面挂掉时用 bootloader 的情况）
│   └── new-hardware.md         # 换显卡 / 换硬盘时的检查项
├── prompts/
│   ├── diff-config.md          # 模板 1
│   ├── gen-skeleton.md         # 模板 2
│   ├── explain-error.md        # 模板 3
│   └── upgrade-review.md       # 模板 4
└── references/
    └── options-index.md        # 常用选项速查（来自 mcp-nixos 查询结果）
```

**SKILL.md 里应该写明的硬约束**：

- 任何配置改动必须先 `dry-build`
- 涉及 `boot.*` / `fileSystems` / `stateVersion` 必须停下来要求人工确认
- 绝不执行 `nix-collect-garbage -d`
- 所有生成的选项名必须能给出出处

### 9.7 风险清单

| 风险 | 后果 | 缓解 |
|---|---|---|
| LLM 编造不存在的选项名 | eval 失败，rebuild 中断 | `dry-build` 闸门 + mcp-nixos 查询 |
| LLM 直接改 `/etc/nixos` 并 switch | 可能激活失败、系统起不来 | 人工审 diff，用 `nixos-rebuild test` 先试 |
| LLM 建议改 `stateVersion` | 可能损坏有状态数据 | 硬规则：**永不**由 LLM 决定改这个 |
| LLM 建议改 `boot.kernelParams` | 可能无法引导 | 必须 `build-vm` 验证 |
| LLM 建议引入不明第三方 flake | 供应链风险 | 人工审查仓库维护状态与 cachix key |
| LLM 建议 `nix-collect-garbage -d` | 摧毁全部回滚点 | 硬规则：只允许 `--delete-older-than Nd` |

---

<a id="十"></a>
## 十、附录

### 10.1 命令速查表

```bash
# ── 配置与重建 ─────────────────────────────────────────
sudo nixos-rebuild switch              # 构建 + 激活 + 设为默认启动项
sudo nixos-rebuild test                # 构建 + 激活，不进启动菜单（可重启撤销）
sudo nixos-rebuild boot                # 构建 + 设为默认启动项，重启生效
sudo nixos-rebuild dry-build           # 只验证能否构建
sudo nixos-rebuild build-vm            # 生成可启动的测试虚拟机
sudo nixos-rebuild switch --rollback   # 回滚到上一个 generation
sudo nixos-rebuild list-generations    # 列出所有 generation

# flake 路线在后面加 --flake .#<hostname>

# ── 查询 ───────────────────────────────────────────────
nixos-option <选项路径>                 # 查选项定义
man configuration.nix                  # 选项手册
nix search nixpkgs <名字>               # 搜包
nix-locate --top-level bin/<程序>       # 按文件反查包

# ── 临时使用（不污染系统）───────────────────────────────
nix shell nixpkgs#<包>                  # 进入带该包的临时 shell
nix run nixpkgs#<程序>                  # 直接运行
nix-shell -p <包>                       # 老式临时环境

# ── 清理 ───────────────────────────────────────────────
sudo nix-collect-garbage --delete-older-than 30d   # 推荐
sudo nix-collect-garbage -d                        # ⚠️ 删除全部旧 generation
sudo nix store optimise                            # 硬链接去重
sudo nix-store --verify --check-contents           # 校验完整性
df -h /nix                                         # 看磁盘

# ── flake ─────────────────────────────────────────────
nix flake update                       # 更新全部 input
nix flake update nixpkgs               # 只更新指定 input
nix flake metadata                     # 查看当前锁定的版本

# ── 稳定基座 + 滚动组件（第六章）───────────────────────
nix flake update nixpkgs-unstable          # 只滚滚动源，基座不动
nixos-rebuild dry-build --flake .#mypc     # 闸门：验证配置成立再应用
nixos-rebuild boot --flake .#mypc          # 动内核/驱动时用 boot，不用 switch
sudo systemctl start nixos-upgrade         # 手动触发一次自动升级
systemctl status nixos-upgrade.timer       # 看自动升级定时器
journalctl -u nixos-upgrade.service        # 看自动升级日志
sudo systemctl start flake-update          # 手动刷新 flake.lock

# ── 升级 ───────────────────────────────────────────────
sudo nix-channel --add https://nixos.org/channels/nixos-26.11 nixos
sudo nixos-rebuild switch --upgrade

# ── 非 Nix 程序 ────────────────────────────────────────
appimage-run ./foo.AppImage            # 跑 AppImage
steam-run ./some-binary                # FHS 沙箱跑二进制
nix-shell ./shell.nix                  # 进入自定义 FHS 环境
npm config set prefix ~/.npm-global    # npm 全局安装改到用户目录
```

### 10.2 出处汇总

**官方文档**

| 主题 | URL |
|---|---|
| NixOS 手册（总） | https://nixos.org/manual/nixos/stable/ |
| 安装 | https://nixos.org/manual/nixos/stable/#sec-installation |
| 改配置 | https://nixos.org/manual/nixos/stable/#sec-changing-config |
| 升级 | https://nixos.org/manual/nixos/stable/#sec-upgrading |
| GC | https://nixos.org/manual/nixos/stable/#sec-nix-gc |
| 用户管理 | https://nixos.org/manual/nixos/stable/#sec-user-management |
| Release notes | https://nixos.org/manual/nixos/stable/release-notes.html |
| Unstable release notes | https://nixos.org/manual/nixos/unstable/release-notes |
| FHS 环境（nixpkgs 手册） | https://nixos.org/manual/nixpkgs/stable/#sec-fhs-environments |
| AppImage 打包 | https://nixos.org/manual/nixpkgs/stable/#sec-pkgs-appimageTools |
| Nix store path | https://nix.dev/manual/nix/stable/store/store-path.html |
| Flakes 概念 | https://nix.dev/concepts/flakes.html |
| nix-shell | https://nix.dev/manual/nix/stable/command-ref/nix-shell.html |
| nix-store optimise | https://nix.dev/manual/nix/stable/command-ref/nix-store/optimise |
| Home Manager（NixOS module） | https://nix-community.github.io/home-manager/installation/nixos.html |
| Home Manager（standalone + flakes） | https://nix-community.github.io/home-manager/nix-flakes/standalone.html |
| Home Manager · programs.mangohud | https://nix-community.github.io/home-manager/options/home-manager/programs/mangohud.html |

**Wiki**

| 主题 | URL |
|---|---|
| nixos-rebuild | https://wiki.nixos.org/wiki/Nixos-rebuild |
| stateVersion FAQ | https://wiki.nixos.org/wiki/FAQ/When_do_I_update_stateVersion |
| Flakes | https://wiki.nixos.org/wiki/Flakes |
| Nvidia | https://wiki.nixos.org/wiki/Nvidia |
| Steam | https://wiki.nixos.org/wiki/Steam |
| Appimage | https://wiki.nixos.org/wiki/Appimage |
| Nix-ld | https://wiki.nixos.org/wiki/Nix-ld |
| Packaging/Binaries | https://wiki.nixos.org/wiki/Packaging/Binaries |
| Python | https://wiki.nixos.org/wiki/Python |
| Node（旧 wiki） | https://nixos.wiki/wiki/Node |
| Graphics | https://wiki.nixos.org/wiki/Graphics |
| nixos-generate-config | https://wiki.nixos.org/wiki/Nixos-generate-config |
| Fcitx5 | https://wiki.nixos.org/wiki/Fcitx5 |
| Fonts | https://wiki.nixos.org/wiki/Fonts |
| 自动系统升级（含 flake 路线） | https://wiki.nixos.org/wiki/Automatic_system_upgrades |
| 更新 NixOS（channel / flake 对照） | https://wiki.nixos.org/wiki/Updating_NixOS |
| Mesa（`hardware.graphics.package`） | https://wiki.nixos.org/wiki/Mesa |
| Firefox（`programs.firefox.package`） | https://wiki.nixos.org/wiki/Firefox |
| Overlays | https://wiki.nixos.org/wiki/Overlays |

**源码（nixpkgs `nixos-26.05` 分支）**

| 模块 | 路径 |
|---|---|
| NVIDIA 驱动 | `nixos/modules/hardware/video/nvidia.nix` |
| 图形栈（opengl→graphics 重命名） | `nixos/modules/hardware/graphics.nix` |
| Steam | `nixos/modules/programs/steam.nix` |
| gamemode | `nixos/modules/programs/gamemode.nix` |
| gamescope | `nixos/modules/programs/gamescope.nix` |
| corectrl | `nixos/modules/hardware/corectrl.nix` |
| scx 调度器 | `nixos/modules/services/scheduling/scx.nix` |
| sysctl 默认值 | `nixos/modules/config/sysctl.nix` |
| nix-ld | `nixos/modules/programs/nix-ld.nix` |
| CPU 调频 | `nixos/modules/tasks/cpu-freq.nix` |
| 26.11 release notes | `nixos/doc/manual/release-notes/rl-2611.section.md` |

前缀：`https://github.com/NixOS/nixpkgs/blob/nixos-26.05/`

**第三方仓库与工具**

| 项目 | URL |
|---|---|
| nix-gaming | https://github.com/fufexan/nix-gaming |
| mcp-nixos | https://github.com/utensils/mcp-nixos |
| nix-index | https://github.com/nix-community/nix-index |
| nix-index-database | https://github.com/nix-community/nix-index-database |
| nix-tree | https://github.com/utdemir/nix-tree |
| nix-ld | https://github.com/nix-community/nix-ld |
| patchelf | https://github.com/NixOS/patchelf |
| Hermes Agent | https://github.com/NousResearch/hermes-agent |
| OpenAI Codex CLI | https://github.com/openai/codex |
| Are We Anti-Cheat Yet | https://areweanticheatyet.com/ |
| MyNixOS（选项查询） | https://mynixos.com/ |

**Nix 生态查询工具（第八章出处）**

| 主题 | URL |
|---|---|
| search.nixos.org | https://search.nixos.org/ |
| nixos-search 源码（ES 导入工作流、cron） | https://github.com/NixOS/nixos-search |
| 无 broken/insecure 筛选（社区抱怨） | https://discourse.nixos.org/t/nixos-package-search-does-not-show-when-a-package-is-broken/78488 |
| NixOS search（Wiki） | https://wiki.nixos.org/wiki/NixOS_search |
| `nix search` 手册 | https://nix.dev/manual/nix/latest/command-ref/new-cli/nix3-search |
| NixHub.io | https://www.nixhub.io |
| NixHub API 文档（相对路径） | https://www.jetify.com/docs/nixhub |
| NixHub API 实测主机 | https://search.devbox.sh |
| FlakeHub 文档 | https://docs.determinate.systems/flakehub/ |
| FlakeHub URL 语义 | https://docs.determinate.systems/flakehub/concepts/urls/ |
| FlakeHub SemVer | https://docs.determinate.systems/flakehub/concepts/semver/ |
| FlakeHub CLI | https://docs.determinate.systems/flakehub/cli/ |
| FlakeHub Cache（付费） | https://docs.determinate.systems/flakehub/cache/ |
| FlakeHub 定价 | https://flakehub.com/pricing |
| FlakeHub discovery API | https://docs.determinate.systems/flakehub/discovery/ |
| Determinate Nix | https://docs.determinate.systems/determinate-nix/ |
| nix-installer（默认启用 flakes） | https://github.com/DeterminateSystems/nix-installer |
| FlakeHub 发布时的社区批评 | https://discourse.nixos.org/t/introducing-flakehub/32044 |
| Nix 治理危机（LWN） | https://lwn.net/Articles/970824/ |
| Noogle | https://noogle.dev |
| Noogle 仓库 | https://github.com/nix-community/noogle |
| Noogle（Wiki） | https://wiki.nixos.org/wiki/Noogle |
| Noogle 全量数据端点（实测） | https://noogle.dev/api/v1/data |
| Jetify 产品文档 | https://www.jetify.com/docs |
| Devbox 安装（含 NixOS） | https://www.jetify.com/docs/devbox/installing-devbox/ |
| `devbox generate`（非 AI） | https://www.jetify.com/docs/devbox/cli-reference/devbox-generate |
| Microsoft Dev Box MCP（易混淆） | https://github.com/microsoft/devbox-mcp-server |

**社区案例与讨论（第六章论据）**

| 主题 | URL |
|---|---|
| Mesa unstable on nixos-stable（2026-05，实测翻车） | https://discourse.nixos.org/t/mesa-unstable-on-nixos-stable-in-2026/77618 |
| Mixing stable and unstable packages（2024-08） | https://discourse.nixos.org/t/mixing-stable-and-unstable-packages-on-flake-based-nixos-system/50351 |
| Installing both stable and unstable packages（2026-05） | https://discourse.nixos.org/t/installing-both-stable-and-unstable-packages-in-a-flake/77652 |
| How to automatically update flakes（2025-11，实测有效） | https://discourse.nixos.org/t/how-to-automatically-update-flakes/72426 |
| nixpkgs #349734（`--update-input` 废弃） | https://github.com/NixOS/nixpkgs/issues/349734 |
| LibrePhoenix · 同时用 stable + unstable 教程 | https://librephoenix.com/2024-02-10-using-both-stable-and-unstable-packages-on-nixos-at-the-same-time |
| update-flake-lock（GitHub Action） | https://github.com/DeterminateSystems/update-flake-lock |
| chromium 维护说明（浏览器更新移植到 stable） | https://github.com/NixOS/nixpkgs/tree/master/pkgs/applications/networking/browsers/chromium |
| nixos-rebuild-ng（Python 重写版） | https://github.com/NixOS/nixos-rebuild-ng |

**版本与日程**

| 主题 | URL |
|---|---|
| NixOS 26.05 发布公告 | https://discourse.nixos.org/t/nixos-26-05-released/77930 |
| 26.11 发布日程 | https://github.com/NixOS/nixpkgs/issues/567567 |
| 26.11 发布周期讨论 | https://discourse.nixos.org/t/let-s-have-a-great-26-11-release-cycle/80323 |

### 10.3 未核实 / 存疑项

| 项 | 说明 |
|---|---|
| `hermes pm install` 是否支持指定外部 node 路径 | 公开文档未说明，§5.9 第 3 点为**推断** |
| Steam 库放 NTFS 分区的具体风险 | 社区经验一致，但**未找到权威一手出处** |
| TheCowboyAI/nixmcp 是否为独立维护项目 | GitHub 页面无法取回，描述与 mcp-nixos 逐字相同，**不建议使用** |
| mynixos.com 是否有官方 API / MCP | **未找到**公开接口 |
| `programs.mangohud` 在 NixOS 系统层是否存在 | **不存在**（已核实为 Home Manager 专属选项） |
| `buildFHSUserEnv` 旧名 | **已在当前 nixpkgs 中移除**（已核实） |
| `nixpkgs.nodePackages` | **已整体移除**（已核实） |
| 各启动器包的 license 是否为 unfree | 未逐包核实；取决于运行时组件 |
| `nixos-rebuild-ng` 在 26.05 中是否为默认实现 | **来源冲突**：NixOS Wiki 称「25.11 起为默认」，但 nixpkgs unstable release notes 称「可通过 `system.rebuild.enableNg` 启用」。**以 `man nixos-rebuild` 实测为准**；`system.rebuild.enableNg` 选项在 MyNixOS 上未能检索到 |
| `nixos-rebuild --commit-lock-file` 的确切语义 | 官方 Wiki 的自动升级配置使用了它，但**是否同时隐含刷新 lock** 未能从一手源码确认。社区普遍采用「先 `nix flake update` 再 rebuild」的两段式（§6.5 层次 2），更可靠 |
| Mesa 从 unstable 换到 stable 后**是否必然**出问题 | 单个社区案例（§6.1）报告了失败；无法推断普遍性。**属个案，非结论** |
| `hardware.nvidia.package` 跨 nixpkgs 取 unstable 的可行性 | 原理上需要与 `boot.kernelPackages` 同步更换，**未找到成功案例佐证**，仅作原理说明 |
| `noogle.dev/api/v1/search` 端点 | **不存在**（实测 404）。真实公开端点是 `/api/v1/data`（全量 JSON）。文档/教程中出现的 search 端点均为误传 |
| NixHub API 主机名 | 官方文档**只给相对路径**，未记载主机名。`https://search.devbox.sh` 为**本文 curl 实测**所得，非文档明示 |
| NixHub 索引实时性 | 实测（2026-10-12）`hello` / `firefox` 的 `latest` 均解析到 commit `c27cdad…`（`date` = 2026-08-27），**疑似滞后数周**。用它做版本决策前务必核对 `date` 字段并交叉验证 |
| search.nixos.org 后端 ES 凭据 | 端点可用但**需 HTTP Basic 认证**，凭据**从未由官方公开**（仅见于第三方源码）。视为**非官方契约**，随时可能失效 |
| FlakeHub 上的 nixpkgs 来源 | 实测 API 返回的 `repo_url` 指向 `DeterminateSystems/flakehub-mirror`，即**经 DetSys 镜像**而非直连上游。镜像可用性未获官方 SLA 承诺 |
| Jetify 是否有官方 Devbox MCP server | **未找到官方证据**。网上出现的 `devbox-mcp-server` 实为 **Microsoft Dev Box**（Azure），与 Jetify 无关 |
| `api.flakehub.com/search` 端点 | 官方 discovery 文档未记载，**本文实测可用**（需带 `User-Agent`）。属非文档化接口 |

---

*文档版本 1.4 · 生成于 2026-10-12 · 基准 NixOS 26.05「Yarara」*
*NixOS 迭代较快，使用前请对照官方 release notes 核对选项名。*
