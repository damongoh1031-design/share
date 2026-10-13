---
id: nixos-operations-guide
title: NixOS 运维指南（26.05）——配置路线、游戏、非 Nix 二进制、查询工具链、LLM 辅助
tags: [nixos, nix, flakes, home-manager, gaming, steam, appimage, nix-ld, llm-ops, mcp, rolling-release, nixpkgs-unstable, nixhub, flakehub, noogle, search-nixos, devbox, systemd-user-service, linger, hermes-agent, openclaw]
created: 2026-10-12
updated: 2026-10-12
version: 1.5
status: stable
source: 本次会话（官方手册 + nixpkgs nixos-26.05 源码逐条比对 + 官方 Wiki + 官方论坛 + 五个生态查询站 API 实测 + 第二轮源码级复核 + 第三轮 agent 服务化交叉引用 + 第四轮 nixos-26.05/nixos-unstable 双分支逐包版本实测）
confidence: 已核实
---

## TL;DR

1. NixOS 的一切都源于「**没有 FHS**」：所有官方二进制跑不起来，都是因为 ELF 里硬编码的 `/lib64/ld-linux-x86-64.so.2` 不存在。
2. 三条配置路线**不是三选一，是三个阶段**：`configuration.nix` 单体 → flakes → home-manager。
3. 游戏玩家的铁律：**固定单一 nixpkgs**。NVIDIA 驱动 = 内核模块 + 用户态库的配对，混用 nixpkgs 必然黑屏。
4. 跑非 Nix 程序只需记一张表：AppImage→`appimage-run`，复杂二进制→`buildFHSEnv`，CLI 缺 .so→`nix-ld`。
5. NixOS 是 LLM 辅助运维最理想的发行版：声明式 + 强类型选项 + `dry-build` 闸门 + generation 回滚，四重保险。
6. 「稳定基座 + 滚动组件」：**能滚叶子，不能滚根**。flake 做不到「不锁」，但能做到「自动换锁」。**动手前先量** —— 实测 26.05 的 `linuxPackages_latest` 已是 7.2.9，与 unstable 逐字相同，**内核跨源毫无意义**。
7. **查得准 > 猜得对**：五个生态查询站（search.nixos.org / NixHub / FlakeHub / Noogle / Devbox）提供「地面真值」；LLM 幻觉在 NixOS 上的代价是系统起不来。

---

## 1. 三个核心概念

| 概念 | 是什么 | 运维意义 |
|---|---|---|
| derivation | 构建配方，产物进 `/nix/store/<32字符哈希>-<名字>` | 同输入必得同路径 = 可复现 |
| 不可变性 | store 只读、内容寻址 | 旧 closure 在被 GC 前始终可寻址 |
| generation | 每次 switch 追加一条，注册在 `/nix/var/nix/profiles/system` | 回滚 = 原子切符号链接，不是重装 |

**关键事实**：NixOS 无 `/usr/lib`、无 `/lib64/ld-linux-x86-64.so.2`。ELF 把动态链接器路径硬编码在文件头 → 报 `No such file or directory`（文件明明在）。Nix 用 `patchelf` 改写 interpreter/RPATH 解决。

---

## 2. nixos-rebuild 子命令语义（易混）

| 子命令 | 构建 | 立即激活 | 进启动菜单 |
|---|---|---|---|
| `switch` | ✅ | ✅ | ✅ |
| `boot` | ✅ | ❌ | ✅ |
| `test` | ✅ | ✅ | ❌ |
| `build` | ✅ | ❌ | ❌ |
| `dry-build` | ✅(求值) | ❌ | ❌ |
| `build-vm` | ✅ | — | 生成 QEMU 镜像 |

`test` = 新手最安全的实验方式（重启即撤销）。`dry-build` = LLM 改配置后的验证闸门。

---

## 3. 三条配置路线

| 维度 | configuration.nix | +Flakes | +Home Manager |
|---|---|---|---|
| 难度 | ★☆☆ | ★★★ | ★★☆ |
| 可复现 | 中（channel 漂移） | 高（flake.lock） | 高 |
| 管 dotfiles | ✗ | ✗ | ✓ |
| 多机复用 | 弱 | 强 | 强 |

**推荐分阶段**：默认配置 → 把 `/etc/nixos` 进 git → 迁 flakes → 叠加 HM。

### 必须记住的三条

- `system.stateVersion` / `home.stateVersion` = **首次安装版本，永不随手改**。官方原文：*"Most users should never change this value after the initial install, for any reason, even if you've upgraded your system."*
- flakes **至今仍是 experimental**（Nix 2.34.x，RFC 49 已关闭无时间表）。
- flake 的文件**必须 `git add` 后才可见**（未跟踪文件被忽略）——新手第一大坑。

---

## 4. 稳定基座 + 滚动组件（混合版本策略）

### 动手前先量：跨源到底能拿到什么（2026-10-12 实测）

**不要凭「unstable 一定更新」的直觉动手。** 在 `nixos-26.05` 与 `nixos-unstable` 两分支上逐包比对：`[核实·源码]`

| 组件 | 26.05 | nixos-unstable | 跨源值不值 |
|---|---|---|---|
| **内核 `linuxPackages_latest`** | **7.2.9** | **7.2.9** | ❌ 完全一致，跨源毫无意义 |
| 内核 `linuxPackages`（默认） | 6.18.55（LTS） | 6.18.55（LTS） | ❌ 完全一致 |
| **Mesa** | **26.1.8** | **26.2.4** | ✅ 值得 |
| **proton-ge-bin** | **GE-Proton11-1** | **GE-Proton11-7** | ✅ 值得 |
| **gamescope** | **3.16.23** | **3.16.31** | ✅ 值得 |
| **mangohud** | **1.91.6** | **1.91.6** | ❌ 完全一致 |

> **这条实测推翻了本文 v1.4 的一条结论。** 原表把「内核」整行判为「❌ 不要跨源」，理由是「NVIDIA / ZFS / VirtualBox 模块必须与内核同源」。**那个理由只对「有树外内核模块」的人成立**，且掩盖了更简单的事实：**26.05 的 `linuxPackages_latest` 已经是 7.2.9，与 unstable 逐字相同。**
>
> 源码依据：两分支 `pkgs/top-level/linux-kernels.nix` 的 `packageAliases` 都是 `linux_default = packages.linux_6_18; linux_latest = packages.linux_7_2;`（26.05 `:739-743` vs unstable `:667-671`），且两边的 `pkgs/os-specific/linux/kernel/kernels-org.json` 里 `7.2 → 7.2.9`、`6.18 → 6.18.55` **逐字相同**。**stable 分支会定期把内核 rebase 到最新补丁。**

**出处（可自行复验）**：`pkgs/os-specific/linux/kernel/kernels-org.json`、`pkgs/development/libraries/mesa/common.nix`、`pkgs/by-name/{pr/proton-ge-bin,ma/mangohud,ga/gamescope}/package.nix`。两分支 raw 路径只差分支名。

### 能滚什么、不能滚什么

| 组件 | 能跨 nixpkgs 滚 | 理由 |
|---|---|---|
| 浏览器（Firefox / Chromium） | ✅ | 纯用户态叶子包；且 stable 分支本身也收浏览器安全更新 |
| Mesa | ⚠️ 官方支持但有实测翻车 | `hardware.graphics.package`（25.05 起），**32/64 位必须一起换**。实测有版本差（26.1.8→26.2.4），故值得 |
| 游戏组件（mangohud / gamescope / proton-ge-bin） | ✅ 但先看上面那张表 | 不进内核、不参与引导。实测 proton-ge-bin / gamescope 有差，**mangohud 无差** |
| **内核（linux）** | ⚠️ **看平台，且通常没必要** | **有树外模块**（NVIDIA / ZFS / VirtualBox）→ ❌ 绝对不要；**纯 AMD/Intel** → 技术可行，**但 26.05 已是最新内核，跨源拿不到东西** |
| NVIDIA 闭源驱动 | ❌ | 内核模块 + 用户态库强配对 |
| 系统模块（systemd / glibc / 引导） | ❌ | 由 `nixosSystem` 决定 |

**原则**：能滚「叶子」，不能滚「根」。
**真正的风险不是「版本新」，而是「同一个包同时被两份 nixpkgs 定义」。**

**跨源换内核真正的失败模式**：不是内核本身，而是**模块树**。`boot.extraModulePackages` 类型为 `listOf types.package`，NixOS 把它拼进模块树（`nixos/modules/system/boot/kernel.nix:197-202`、`:394`）：
```nix
system.modulesTree = [ (lib.getOutput "modules" kernel) ] ++ config.boot.extraModulePackages;
```
只要有模块往这里塞「来自稳定 nixpkgs」的包而内核来自 unstable，模块树里就会出现「为 6.18 编译的 .ko」与「7.2 内核」并存。

### 纯 `configuration.nix` 能做到吗？—— 能，有三条路

| 路 | 需要 channel？ | 需要 flake？ | 锁版本？ | 适合 |
|---|---|---|---|---|
| **A** channel + `import <nixos-unstable>` | ✅ | ❌ | ❌ **完全不锁** | 临时救急装一个包 |
| **B** `builtins.fetchTarball` | ❌ | ❌ | ⚠️ 加 `sha256` 才锁 | 不碰 channel/flake，能接受手工管 hash |
| **C** `builtins.fetchGit` + 钉 `rev` | ❌ | ❌ | ✅ **手工锁** | 想要锁定但坚决不引入 flake |
| **D** flake | ❌ | ✅ | ✅ **锁**（`flake.lock`） | **长期做滚动组件（推荐）** |

```nix
# 路 B：只用 configuration.nix，不碰 channel、不建 flake
{ config, pkgs, lib, ... }:
let
  unstableSrc = builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz";
    # sha256 = "...";   # 建议加：不加则每次求值可能重下，且不可复现
  };
  unstable = import unstableSrc {
    inherit (pkgs.stdenv.hostPlatform) system;
    inherit (config.nixpkgs) config;
  };
in {
  hardware.graphics.package   = unstable.mesa;
  hardware.graphics.package32 = unstable.pkgsi686Linux.mesa;
  environment.systemPackages = [ unstable.proton-ge-bin unstable.gamescope ];
}
```

> **路 C 用 `builtins.fetchGit { url; ref = "refs/heads/nixos-unstable"; rev = "<commit>"; }`** —— 带 `rev` 时 Nix 会校验取到的 commit 与 `rev` 一致，**这就是「手工锁」**，等价于手工版的 `flake.lock`。
>
> **⚠️ `nixos-unstable.tar.gz` 是移动目标** —— 不加 `sha256` 时等于「用 fetchTarball 实现了 channel 的不锁行为」。取 hash：`nix-prefetch-url --unpack <url>`。

### 各路线做法对照（flake 内）

| 做法 | 写法 | 评价 |
|---|---|---|
| flake + `_module.args` | 双 input + `_module.args.pkgsUnstable = unstable;` | ✅ 推荐，只为需要的包求值，eval 开销小 |
| flake + overlay | `nixpkgs.overlays` 里塞 `unstable` | ❌ 官方论坛原话：「完全没必要，很可能拖慢 eval」 |

**三条硬限制**：① 同一个包不能装两个版本；② 系统只能由一份 nixpkgs 构建（unstable 只是额外包来源）；③ unstable 的 unfree 包需 `inherit (config.nixpkgs) config` 放行。

**回滚粒度的固有局限**：无论哪条路，「单独回滚某一个包」都做不到 —— 粒度是整次 rebuild。唯一例外是把滚动包放 Home Manager 层（回滚粒度 = HM generation，至少不影响系统能启动）。

### 有多少步骤？—— 首次 vs 日常必须分开算

| 口径 | 用什么 | 首次搭建 | 日常升级 | 每次手工查版本？ | 可复现 |
|---|---|---|---|---|---|
| **A** channel | 只改 `configuration.nix` | 3 步 | 2 步 | ❌ | ❌ |
| **B** `fetchTarball` | 只改 `configuration.nix` | 3 步 | 2 步 | ✅ 查 hash | ⚠️ 钉 hash 才可复现 |
| **C** `fetchGit` + `rev` | 只改 `configuration.nix` | 3 步 | 2 步 | ✅ 查 rev | ✅ |
| **D** flake + 手动换锁 | `flake.nix` + `configuration.nix` | **6 步** | 2 步 | ❌ | ✅ |
| **E** flake + 自动换锁 | 同上 + systemd timer | **8 步** | **0 步** | ❌ | ✅ |

- **口径 D 的 6 步**：① `cd /etc/nixos` ② 写 `flake.nix`（双 input）③ 写 `configuration.nix` 的 `let` + 引用 ④（可选）`_module.args.pkgsUnstable` ⑤ `git init && git add` ⑥ 首次 `nixos-rebuild switch --flake .#mypc`（此步才生成 `flake.lock`）
- **日常 2 步**：`nix flake update nixpkgs-unstable` → `nixos-rebuild switch --flake .#mypc`。**只换一个 input 的锁，基座 `nixpkgs` 的锁不变** —— 这是「稳定基座」的物理保证。
- **口径 E 加 2 步**：⑦ `flake-update.service` + `.timer` ⑧ `system.autoUpgrade` + `nix.gc` + `configurationLimit`
- **flake 的「6 步」是一次性成本**；它没让「升级」本身变简单，只是把「手工查 hash/rev」自动化了（`nix flake update` 替你改 `flake.lock`）。**flake = 自动化的手工锁。**

**⚠️ 内核提醒**：不要写 `unstable.linuxPackages_latest`。纯 AMD/Intel 直接 `boot.kernelPackages = pkgs.linuxPackages_latest;`（26.05 上 = 7.2.9）—— 这一行属于基座 `pkgs`，跟着基座走。NVIDIA / ZFS / VirtualBox 用户同理，且**必须**用基座的。

### flake 会锁版本吗？

**做不到「不锁」—— 锁（`flake.lock`）是可复现的物理基础。但可以做到「自动换锁、无需人工」。**

| 路线 | 锁版本 | 全自动 | 可复现 |
|---|---|---|---|
| channel + `nixos-rebuild switch --upgrade` | **不锁** | ✅ | 低 |
| flake 手动 `nix flake update` | 锁 | ❌ | 高 |
| flake + 自动换锁 | 锁（自动刷新） | ✅ | 高 |

**四个自动化层次**

1. `system.autoUpgrade` + `flake` + `flags = [ "--commit-lock-file" ]`（官方 Wiki）
2. **两段式**：`flake-update.service` 跑 `nix flake update`，`nixos-upgrade.service` 用 `after` + `requires` 依赖它 —— 社区实测有效，更可靠
3. GitHub Action `DeterminateSystems/update-flake-lock` 定时提 PR —— **在应用前插入审查环节**
4. agent 接管（见下）

**坑**：

- `--update-input` **已废弃**（nixpkgs #349734）→ 老教程会导致自动升级**静默失败**
- flake 仓库不属 root → `/root/.gitconfig` 加 `[safe] directory = /path/to/flake`
- root 无 git 身份 → 需设 `GIT_AUTHOR_NAME` / `GIT_AUTHOR_EMAIL` / `GIT_COMMITTER_*`
- 必须同时配 `nix.gc` + `boot.loader.systemd-boot.configurationLimit`，否则 `/boot` 撑爆

### agent 闭环

```
timer → 采集状态 → agent 决策 → dry-build 闸门 → 风险分级
      → git commit + switch → 健康检查 → 失败则 rollback
```

**为什么 NixOS 特别适合**：`nixos-rebuild dry-build` 是零成本验证闸门，等于给 LLM 一个沙盒试衣间。

**硬规则**：禁止 agent 改 `stateVersion` / bootloader / 分区 / 内核驱动；`switch` 前必须人工确认。

### 社区案例

| 案例 | 结果 |
|---|---|
| Mesa unstable on stable（2026-05） | ❌ Firefox 无硬件加速、Steam 仍报旧 Mesa、GNOME 风扇狂转 |
| Mixing stable+unstable（2024-08） | 可行，但原帖编者按：「**强烈建议不要混用，这是不受支持的**」 |
| LibrePhoenix 教程（2024-02） | 可行，作者自称「hacky 方案，最后手段」；同一包不能装两版 |
| 自动更新 flakes（2025-11） | ✅ 两段式实测有效 |

**最稳落点**：基座不动 · 叶子放 Home Manager · 内核驱动永不跨源 · 锁自动换但最后一步留给人。

## 5. 游戏玩家要点

```nix
nixpkgs.config.allowUnfree = true;          # NVIDIA/Steam 必需
hardware.graphics = { enable = true; enable32Bit = true; };
hardware.nvidia = {
  modesetting.enable = true;   # = nvidia-drm.modeset=1
  open = true;                 # Turing+；驱动 ≥560 有 assertion 强制显式设
  powerManagement.enable = true;
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
environment.systemPackages = with pkgs; [ mangohud ];  # 见下方坑
```

### 坑与反直觉

| 坑 | 事实 |
|---|---|
| `programs.mangohud` | **NixOS 无此模块**，只在 Home Manager 里。写进 `configuration.nix` 会 eval 失败。NixOS 层用 `pkgs.mangohud` + Steam 启动项 `mangohud %command%` |
| `hardware.opengl` | **24.11 已重命名为 `hardware.graphics`**，旧名仅为别名 |
| 换驱动只 `switch` | **无效**。内核模块由运行中的内核加载，必须 `nixos-rebuild boot` + 重启 |
| `vm.max_map_count` | 26.05 默认已是 **1048576**，老教程的 262144 是过时值 |
| `services.scx` | 26.05 **存在**（`scheduler` 默认 `scx_rustland`） |
| NTFS 放 Steam 库 | ✅ **已找到权威一手出处**：Valve 官方 Proton Wiki 明确标注 **NOT RECOMMENDED**（此前标「未找到」已解决）→ https://github.com/ValveSoftware/Proton/wiki/Using-a-NTFS-disk-with-Linux-and-Windows |
| `programs.corectrl` 超频选项 | `gpuOverclock.enable` / `.ppfeaturemask` **已重命名为 `hardware.amdgpu.overdrive.*`**（`corectrl.nix:18-25`）；模块本身只有 `enable` + `package`，开 enable 会建 `corectrl` 组，**还需手动加组** |
| `programs.nix-ld.libraries` | 不是「默认空」—— 模块强制注入 **14 个基础库**（`nix-ld.nix:47-64`）；因 `listOf` 是**拼接**语义，用户写法是**追加**。GUI 应用才需要补 `libGL` / `libxkbcommon` / `gtk3` |

---

## 6. 跑非 Nix 程序：决策表

| 场景 | 方案 |
|---|---|
| 长期用、有源码 | 写 derivation |
| tar.gz / 专有二进制、依赖复杂 | `pkgs.buildFHSEnv`（旧名 `buildFHSUserEnv` **已移除**）或 `pkgs.steam-run` |
| CLI 只缺 libc + 几个 .so | `programs.nix-ld.enable = true`（**推荐兜底**） |
| `.AppImage` | `programs.appimage = { enable = true; binfmt = true; };` 或 `appimage-run` |
| 临时试 | `nix-shell -p` + `steam-run` |

```nix
programs.nix-ld = {
  enable = true;
  libraries = with pkgs; [ stdenv.cc.cc.lib zlib openssl curl libxkbcommon ];
};
```

**nix-ld 只补链接器，不提供 FHS 目录** → 图形依赖复杂的不够用，那种要 buildFHSEnv。

### node / npm

- `nixpkgs.nodePackages` **已整体移除**（"unmaintainable"）
- `npm install -g` 必然失败（`/nix/store` 只读，EACCES）
- 正解：`npm config set prefix ~/.npm-global` + PATH

### 案例

| 程序 | 分发方式 | NixOS 方案 |
|---|---|---|
| Hermes Agent | **Python**（Nous Research，非 npm） | `uv tool install hermes-agent` + `programs.nix-ld`（它的 `hermes pm install` 会下 Node/Chromium 二进制） |
| OpenAI Codex CLI | npm `@openai/codex` | `npm config set prefix ~/.npm-global` 后 `npm install -g` |
| Codex（install.sh 路线） | Rust 原生二进制 | `programs.nix-ld` 兜底 |

---

## 7. 长期运维

```nix
nix.gc = { automatic = true; dates = "weekly";
           options = "--delete-older-than 30d"; persistent = true; };
nix.settings.auto-optimise-store = true;
boot.loader.systemd-boot.configurationLimit = 10;
```

- **GC 用 `--delete-older-than 30d`，不要 `-d`**（`-d` 摧毁全部回滚点）
- 升级 26.05 → 26.11：改 channel/flake input → `nixos-rebuild switch --upgrade` / `--flake .#host`
- 升级**不需要改 stateVersion**
- 升级前清单：读 release notes breaking changes → `df -h /nix` → `dry-build` → `build-vm` → `nix-store --verify`
- 单包上 unstable 用 **overlay**，不要整机切 unstable

---

## 8. Nix 生态查询工具链（五个站点的分工）

| 工具 | 回答什么 | 运营方 | API |
|---|---|---|---|
| **search.nixos.org** | 包 / **选项** / 三方 flake 的**当前**状态 | NixOS 官方 | ⚠️ ES 后端，凭据非官方公开 |
| **NixHub.io** | **历史版本** → 对应哪个 nixpkgs commit | Jetify | ✅ v2 REST |
| **FlakeHub** | flake 的 **SemVer** 发布与分发 | Determinate Systems | ✅ 部分 |
| **Noogle** | `lib` / `builtins` / `pkgs` 的**函数**文档 | nix-community | ✅ 全量 JSON |
| **Jetify / Devbox** | 用 Nix 做开发环境，**不写 Nix 语言** | Jetify | — |

**一句话记法**：查选项→search.nixos.org；查旧版本→NixHub；分发 flake→FlakeHub；写函数→Noogle；避开 Nix 语言→Devbox。

### 关键端点（实测）

```bash
# NixHub：官方文档只给相对路径，实际主机是 search.devbox.sh
curl "https://search.devbox.sh/v2/resolve?name=firefox&version=latest"
curl "https://search.devbox.sh/v2/pkg?name=firefox"

# Noogle：全量数据（约 4.4 MB / 2145 条）—— 唯一可完全离线的数据源
curl -s https://noogle.dev/api/v1/data -o noogle-data.json

# FlakeHub
curl -H "Accept: application/json" "https://api.flakehub.com/f/NixOS/nixpkgs/releases"
```

### 为什么「选项搜索」是核心

NixOS 是声明式配置，**用户写的是 option，不是 package**。选项散落在上千个模块里，`man configuration.nix` 效率极低。search.nixos.org 的 Options 页能直达某模块的默认值 / 类型 / 示例 / 源码位置 —— `nix search` **做不到**。

### 固定单个包到指定版本

```nix
# configuration.nix —— 只把这一个包固定到旧版 nixpkgs
{ config, pkgs, ... }:
let
  pinned = builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/<commit>.tar.gz";
    # sha256 = "...";   # 生产必须加 hash
  };
  pkgsPinned = import pinned {
    inherit (pkgs.stdenv.hostPlatform) system;
    inherit (config.nixpkgs) config;
  };
in { programs.firefox.package = pkgsPinned.firefox; }
```

用 `programs.firefox.package`（模块化替换）**而非**覆盖 `pkgs.firefox`（牵动依赖树）。

### 与 LLM 的关系

`mcp-nixos` 已聚合其中四个数据源（NixHub / FlakeHub / Noogle / 选项库）→ 给 agent 的最短路径。Noogle 的全量 JSON 是唯一能「完全离线」喂给 LLM 的。

### 坑与反直觉

| 坑 | 事实 |
|---|---|
| `noogle.dev/api/v1/search` | **不存在**（404）。真实端点是 `/api/v1/data`（全量） |
| NixHub API 主机名 | 文档只给相对路径，实际是 `https://search.devbox.sh`（实测） |
| NixHub 索引实时性 | 实测 `latest` 解析到 2026-08-27 的 commit，**可能滞后数周**，用前核对 `date` |
| search.nixos.org 后端 API | 需 Basic Auth，**凭据从未官方公开**。别自己抓，用 `mcp-nixos` |
| search.nixos.org 筛 broken | **没有这个筛选器** |
| FlakeHub 上的 nixpkgs | 实际由 **DetSys 镜像**提供，不是直连上游 |
| FlakeHub 发布 flake | **不是 `fh publish`**，是 Action `flakehub-push` |
| `devbox generate` | **不是 AI 功能**，是脚手架生成器 |
| Devbox 的 MCP | **Jetify 无官方 MCP**；`devbox-mcp-server` 是 Microsoft Azure 的 |
| FlakeHub Cache | **不免费**（Free 层只含公开 flake） |

### 争议提示

FlakeHub 发布时（2023-08-22）在 NixOS Discourse 有明确批评（「第三方的、中心化的、专有的」）；更广背景是 2024-04 Nix 社区治理危机。**日常用上游 GitHub 源即可**，仅在需要 SemVer 约束 + 团队分发时才引入。

---

## 9. LLM 辅助管理

### MCP 生态（2026-10-12 核实）

| 名称 | 状态 | 说明 |
|---|---|---|
| [mcp-nixos](https://github.com/utensils/mcp-nixos) | **活跃**（~853★，push 2026-09-05） | 覆盖 nixpkgs 包 / NixOS 选项 / Home Manager 选项 / FlakeHub / Noogle / Wiki。已进 nixpkgs（`pkgs.mcp-nixos`）。**无需本机装 Nix** |
| TheCowboyAI/nixmcp | `[未核实]` | 描述与 mcp-nixos 逐字相同，疑似镜像，**不建议用** |
| mynixos.com API/MCP | `[未找到]` | — |

### 安全护栏（硬性）

```
LLM 生成 → 人工审 diff → dry-build → (涉及 boot/驱动? build-vm) → switch → 出问题 rollback
```

**必须人工确认的四类**：`boot.kernelParams`、`boot.loader.*`、`fileSystems`、`system.stateVersion`。

**为什么 dry-build 是关键**：Nix 选项系统强类型，幻觉选项名会在 eval 阶段被立刻拒绝，不会悄悄生效。

### 给 LLM 喂上下文

```bash
nixos-option <path>                                   # 查选项定义
nix eval --json .#nixosConfigurations.host.config      # 导出全量生效配置
nix search nixpkgs <name>
nix-locate --top-level bin/<prog>                      # 需 nix-index
```

## 10. 交叉引用：把 agent 装成服务（2026-10-12 第三轮新增）

本文**不包含**具体 agent 软件的服务化方案。如果你要把 **Hermes Agent / OpenClaw** 装成 NixOS 上的常驻服务，见姊妹交付物 `nixos-amd-guide.md` 的**第十九～二十二章**，以及 `kb/nixos-amd-teaching-guide.md` 第 12 节。

**三条与本文直接相关的结论（摘要）**：

| 结论 | 为什么和「运维」有关 |
|---|---|
| **用户级 systemd 服务默认只在你登录期间存在** | 必须 `loginctl enable-linger <user>`（或 NixOS 的 `users.users.<n>.linger = true`）才能开机自启。**Home Manager 自己设不了 linger** —— 它是账户属性 |
| **无 linger 时 Hermes 的 cron 会静默 fail closed** | cron job 走 `systemd-run --user --scope`，没有 user manager 就**一个都不跑且不报错**。自查：`loginctl show-user hermes \| grep Linger` |
| **NixOS 系统模块的配置在 root 手里** | Hermes 的 state dir 是 `0750 hermes:hermes`（连 `ls` 都 permission denied）；OpenClaw 的 `configPath` **有硬断言必须 `/etc/` 下**。**要"agent 能在对话里改配置"，只有 `nix profile install` + 官方 CLI 那条路** |

**另一条与本文「混合版本策略」（第 4 节）直接相关**：Hermes 的 flake **没有二进制缓存**，每次 bump nixpkgs 要本地编译约 **666 个 derivation**（GitHub issue `#130870`）。这会让"频繁 `nix flake update`"这个习惯在 agent 场景下变成小时级操作 —— **第 4 节的混合版本策略需要按这个成本重新权衡**。

---

## 可复用操作

```bash
# 安全实验
sudo nixos-rebuild test
# 验证闸门
sudo nixos-rebuild dry-build --flake .#host
# 虚拟机试跑
sudo nixos-rebuild build-vm --flake .#host
# 回滚
sudo nixos-rebuild switch --rollback
# 保 30 天的 GC
sudo nix-collect-garbage --delete-older-than 30d
# npm 全局安装改到用户目录
npm config set prefix ~/.npm-global
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc

# 稳定基座 + 滚动组件
nix flake update nixpkgs-unstable          # 只滚滚动源，基座不动
nixos-rebuild dry-build --flake .#mypc     # 闸门：验证成立再应用
nixos-rebuild boot --flake .#mypc          # 动内核/驱动用 boot，不用 switch
sudo systemctl start nixos-upgrade         # 手动触发一次自动升级
journalctl -u nixos-upgrade.service        # 看自动升级日志
```

## 未核实 / 存疑

| 项 | 状态 |
|---|---|
| `hermes pm install` 是否支持指定外部 node 路径 | 公开文档未说明，属**推断** |
| Steam 库放 NTFS 的风险 | 社区经验一致，**无权威一手出处** |
| TheCowboyAI/nixmcp 独立性 | **无法证实** |
| mynixos.com 官方 API/MCP | **未找到** |
| 各启动器包 license 是否 unfree | 未逐包核实 |
| `nixos-rebuild-ng` 在 26.05 是否为默认实现 | **来源冲突**（Wiki 称 25.11 起默认 vs release notes 称需 `system.rebuild.enableNg`），以 `man nixos-rebuild` 实测为准 |
| `nixos-rebuild --commit-lock-file` 是否隐含刷新 lock | **未能从一手源码确认**；社区两段式更可靠 |
| Mesa 从 unstable 换到 stable 是否**必然**出问题 | **个案，非结论** |
| 26.05 的 `linuxPackages_latest` 是否**长期**等于 unstable | **本轮（2026-10-12）实测逐字相同**，但属快照；两个分支各自 rebase，**下次动手前应重新比对 `kernels-org.json`** |
| 纯 AMD/Intel 跨源取 unstable 内核 | 技术上无模块配对问题，但**无收益**（版本相同），故**无实测案例** |
| `hardware.nvidia.package` 跨源取 unstable | 原理上需与 `boot.kernelPackages` 同步，**无成功案例佐证** |
| `noogle.dev/api/v1/search` 端点 | **不存在**（实测 404）。真实端点是 `/api/v1/data` |
| NixHub API 主机名 | 官方文档**未记载**；`search.devbox.sh` 为实测所得 |
| NixHub 索引实时性 | 实测疑似**滞后数周**（`latest` → 2026-08-27 commit），用前核对 `date` |
| search.nixos.org ES 凭据 | **从未官方公开**，属非官方契约 |
| FlakeHub 上的 nixpkgs 来源 | 实测经 `DeterminateSystems/flakehub-mirror`，**非直连上游** |
| Jetify 官方 Devbox MCP | **未找到官方证据** |

## 出处（主要）

- NixOS 手册：https://nixos.org/manual/nixos/stable/ （#sec-installation / #sec-changing-config / #sec-upgrading / #sec-nix-gc / #sec-user-management）
- nixpkgs 手册 FHS：https://nixos.org/manual/nixpkgs/stable/#sec-fhs-environments
- nix.dev：store path / flakes / nix-shell / nix-store optimise
- Wiki：Nixos-rebuild / FAQ-When_do_I_update_stateVersion / Flakes / Nvidia / Steam / Appimage / Nix-ld / Packaging-Binaries / Python
- 源码（`github.com/NixOS/nixpkgs/blob/nixos-26.05/`）：`hardware/video/nvidia.nix`、`hardware/graphics.nix`、`programs/steam.nix`、`programs/gamemode.nix`、`programs/gamescope.nix`、`services/scheduling/scx.nix`、`config/sysctl.nix`、`programs/nix-ld.nix`
- **双分支版本比对（第四轮新增）**：`pkgs/os-specific/linux/kernel/kernels-org.json`（内核版本表）、`pkgs/top-level/linux-kernels.nix`（`packageAliases`）、`pkgs/top-level/all-packages.nix`（`linuxPackages*` 暴露点）、`pkgs/development/libraries/mesa/common.nix`、`pkgs/by-name/{pr/proton-ge-bin,ma/mangohud,ga/gamescope}/package.nix`、`nixos/modules/system/boot/kernel.nix`（`extraModulePackages` → `modulesTree`）。**两分支 raw 路径只差分支名**
- Home Manager：https://nix-community.github.io/home-manager/
- nix-gaming：https://github.com/fufexan/nix-gaming
- 自动系统升级（含 flake 路线）：https://wiki.nixos.org/wiki/Automatic_system_upgrades
- Mesa（`hardware.graphics.package`）：https://wiki.nixos.org/wiki/Mesa
- Mesa unstable on stable 实测案例：https://discourse.nixos.org/t/mesa-unstable-on-nixos-stable-in-2026/77618
- 混用 stable + unstable 讨论：https://discourse.nixos.org/t/mixing-stable-and-unstable-packages-on-flake-based-nixos-system/50351
- 自动更新 flakes 实测：https://discourse.nixos.org/t/how-to-automatically-update-flakes/72426
- `--update-input` 废弃：https://github.com/NixOS/nixpkgs/issues/349734
- update-flake-lock：https://github.com/DeterminateSystems/update-flake-lock

**生态查询工具（第八章）**

- search.nixos.org：https://search.nixos.org/ · 源码/ES 导入工作流：https://github.com/NixOS/nixos-search
- NixHub：https://www.nixhub.io · API 文档：https://www.jetify.com/docs/nixhub · 实测主机：https://search.devbox.sh
- FlakeHub：https://docs.determinate.systems/flakehub/ · 定价：https://flakehub.com/pricing · 批评帖：https://discourse.nixos.org/t/introducing-flakehub/32044 · 治理危机（LWN）：https://lwn.net/Articles/970824/
- Noogle：https://noogle.dev · 仓库：https://github.com/nix-community/noogle · 全量端点：https://noogle.dev/api/v1/data
- Jetify/Devbox：https://www.jetify.com/docs · 安装：https://www.jetify.com/docs/devbox/installing-devbox/ · 易混淆的 Microsoft Dev Box MCP：https://github.com/microsoft/devbox-mcp-server

完整逐条出处见交付物 `nixos-ops-guide.md` 第 10.2 节。
