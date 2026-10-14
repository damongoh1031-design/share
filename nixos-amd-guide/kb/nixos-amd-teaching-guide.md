---
id: nixos-amd-teaching-guide
title: NixOS 26.05 教学指南（AMD 平台 · 中文用户 · Vibe Coding）——25 章配置实录
tags: [nixos, amd-gpu, amdgpu, realtek, r8169, fcitx5, gnome, kde-plasma, flatpak, steam, gamescope, scx, sched-ext, linux-zen, cachyos, ananicy-cpp, ananicy-rules-cachyos, bore, zram, thp, ksm, kyber, vibe-coding, hermes-agent, openclaw, codex, mcp, searxng, nix-ld, devshell, apparmor, fhs, china-mirror, flake, nixpkgs-unstable, overlay, home-manager, nix-openclaw, systemd-user-service, linger, bazzite, ujust, rpm-ostree, nh, distrobox, waydroid, lanzaboote, inputplumber, powerstation, bazaar, atomic-update, aeon, microos, transactional-update, pkgsUnstable, useGlobalPkgs, pkgsPath, stable-base-rolling-apps, buildFHSEnv, buildFHSEnvBubblewrap, autoPatchelfHook, patchelf, nix-alien, nix-index, appimage, binfmt, ldso, xorg-deprecation, libx11, glibc-mismatch, steam-run]
created: 2026-10-12
updated: 2026-10-12
version: 1.8
status: stable
source: 本次会话（nixpkgs nixos-26.05 源码逐条比对 + torvalds/linux 源码 + CachyOS-Settings/ananicy-rules/zen-kernel 上游源码 + NixOS Wiki 官方页 + 多路并行子代理调研 + 本人 curl 实测 + **第二轮全量源码复核** + **第三轮：Hermes/OpenClaw 的 Nix 生态调研（官方 flake 源码 + 官方文档 + GitHub issue + NixOS Discourse）** + **第四轮：nixos-26.05/nixos-unstable 双分支逐包版本实测** + **第五轮：Bazzite 官方文档 + nixos-26.05 源码逐条核实（Bazzite 使用模式映射）** + **第六轮：LWN 一手技术分析 + Aeon 官网 + Home Manager 官方 FAQ（unstable.md）+ HM/NixOS 源码核实（Aeon 模式映射）** + **第七轮：nixpkgs 模块源码逐文件核实（nix-ld.nix / ldso.nix / build-fhsenv-* / appimage.nix / aliases.nix / rl-2605.section.md）+ nix-ld 与 nix-alien 官方 README（二进位包与依赖问题）**）
confidence: 已核实
---

## TL;DR

1. **AMD 是 Linux 桌面最省心的选择**：驱动在主线内核，不需 `allowUnfree`，**升级内核不会炸显卡**（NVIDIA 的核心痛点不存在）。
2. **但 `hardware.graphics.enable` 默认是 `false`，且 GNOME/KDE 都不会自动开** —— 必须手写。全仓库**只有 3 处**会替你开：`programs.steam`（硬赋值）、`hardware.amdgpu.opencl.enable`、`hardware.amdgpu.zluda.enable`（后两者 `mkDefault`）。
3. **不要写 `services.xserver.videoDrivers = [ "amdgpu" ]`** —— 默认的 `modesetting` 才是现代 AMD 的推荐值。
4. **`amd_pstate=active` 是冗余的** —— 26.05 内核默认就是 active 模式。
5. **fcitx5 的 `i18n.inputMethod.enabled` 已弃用** → 改用 `enable = true` + `type = "fcitx5"`。
6. **agent 以普通用户跑**：用户级 systemd + `NoNewPrivileges` + MCP（读）+ skills（流程），**「应用变更」永远留给人**。
7. **游戏性能的正确优先级**：Proton 选对 + mesa 够新 + 内存够 ≫ 换内核 ≫ 换调度器 ≫ I/O 调度器。
8. **`elevator=` 内核参数已是死参数**（内核自己只打印警告）—— 设 I/O 调度器只能用 udev/sysfs。
9. **NixOS 没有 SELinux 模块**（`selinux` 在 module-list.nix 匹配数为 0）；有 AppArmor。
10. **NixOS 已经在 sysctl 里设好了 `vm.max_map_count=1048576`** —— 抄 SteamOS 的调优值是多余的。

---

## 1. AMD 硬件：10 个已核实的关键点

| # | 结论 | 依据 |
|---|---|---|
| 1 | `hardware.graphics.enable` **默认 false**，GNOME/KDE 模块**都不设**它 | `hardware/graphics.nix:54`（`default = false`）；`services/desktop-managers/{gnome,plasma6}.nix` grep 命中 **0** |
| 2 | **只有 3 处会替你开**：`programs.steam`（**硬赋值**）、`hardware.amdgpu.opencl.enable`、`hardware.amdgpu.zluda.enable`（后两者 `mkDefault`） | `programs/steam.nix:205-210`（`hardware.graphics = { enable = true; enable32Bit = true; }`，位于 `mkIf cfg.enable` 下）→ **在别处写 `false` 会直接 option conflict 报错**；`services/hardware/amdgpu.nix:62-76` |
| 3 | `services.xserver.videoDrivers` 默认 `["modesetting" "fbdev"]` | `services/x11/xserver.nix:457-462` |
| 4 | **现代 AMD 不要写 `"amdgpu"`** —— 那是旧 xf86 DDX，会劣化 | 同上 + Wiki |
| 5 | `hardware.amdgpu.*` 全部 **7 个**选项：`initrd.enable` / `legacySupport.enable` / `overdrive.enable` / `overdrive.ppfeaturemask` / `opencl.enable` / `zluda.enable` / `zluda.package` | `services/hardware/amdgpu.nix:12-45` |
| 6 | `overdrive.ppfeaturemask` 默认 `"0xfffd7fff"` | 同上:28-39 |
| 7 | **没有** `amdgpu.dcdebugmask` / `gpu_recovery` 模块选项 | 同上（需手写 kernelParams） |
| 8 | VA-API **不需要额外包**，Mesa 自带 radeonsi | nixpkgs `doc/manual/gpu-accel.chapter.md` |
| 9 | `services.lact` 有 3 个选项（`enable`/`package`/`settings`），描述**明确建议**同时开 `hardware.amdgpu.overdrive.enable`；`settings` 非空时 `/etc/lact/config.yaml` 变符号链接 → **GUI 无法再改配置** | `services/hardware/lact.nix:16-22,29-52` |
| 10 | 26.05 默认内核 **6.18**（`packageAliases.linux_default = packages.linux_6_18`） | `pkgs/top-level/linux-kernels.nix:740` |

**其他已核实**

- `hardware.cpu.amd.updateMicrocode` **默认 false**（`hardware/cpu/amd-microcode.nix:15-16`）→ 建议开（Zenbleed/Sinkclose 等微码修复）
- `services.thermald` 是 **Intel 专用**，AMD 上无意义
- TLP 与 `power-profiles-daemon` **互斥**（有断言）；GNOME/Plasma6 自动 `mkDefault true` 开 ppd（`gnome.nix:332`、`plasma6.nix:272`）
- `services.ollama.package` 默认是 **CPU 版**，必须改 `pkgs.ollama-rocm` 才用 GPU；`acceleration` 选项**已移除**（`ollama.nix:38-39` 的 `mkRemovedOptionModule`）。4 个变体在 `all-packages.nix:424-427` 生成：`ollama-cpu` / `ollama-rocm` / `ollama-cuda` / `ollama-vulkan`（Vulkan 版可作 ROCm 跑不动时的后备）
- CoreCtrl 超频选项已从 `programs.corectrl.gpuOverclock.*` **迁移到** `hardware.amdgpu.overdrive.*`（`corectrl.nix:18-25`）；`programs.corectrl` 只有 `enable` + `package`，开 enable 会建 `corectrl` 组 + polkit 规则，**还需手动加组**
- `AMD_VULKAN_ICD=RADV` 用于强制走 RADV（AMDVLK 正在停止维护，默认不装）

## 2. Realtek 网卡：先别急着换驱动

| 结论 | 说明 |
|---|---|
| `r8169`（内核自带）**已覆盖** RTL8111/8168/8411/8125/8126 | 绝大多数情况够用 |
| 厂商驱动在 nixpkgs 里**存在** | `pkgs/os-specific/linux/r8168`、`.../r8125`（均已核实 200） |
| ⚠️ RTL8125 对应的是 **`r8125`**，**不是 `r8168`** | 常见混淆 |
| 换法 | `boot.extraModulePackages = [ config.boot.kernelPackages.r8125 ]` + `boot.blacklistedKernelModules = [ "r8169" ]` |
| **代价** | 树外模块，内核升级要重编；**编译失败 = 没网** |
| **`r8169.aspm=0` 参数不存在** | 2025-03 提案被内核拒绝；全局关 ASPM 用 `pcie_aspm=off`（影响所有 PCIe） |
| `hardware.enableRedistributableFirmware` **有线网卡也需要** | 提供 `rtl_nic/*.fw` |
| 网卡名是 `enp4s0` 这类，**不是 `eth0`** | 可预测网卡名 |

## 3. 中文环境：三个已弃用/易错项

| 项 | 正确做法 |
|---|---|
| `i18n.inputMethod.enabled` | **已弃用** → `i18n.inputMethod.enable = true;` + `i18n.inputMethod.type = "fcitx5";` |
| fcitx5 安装方式 | **绝不能**用 `environment.systemPackages`（破坏 addon 检测），只用 `i18n.inputMethod.fcitx5.addons` |
| emoji 字体包名 | **`noto-fonts-color-emoji`**（`noto-fonts-emoji` 不存在） |
| `GTK_IM_MODULE` | Wayland 下**不要设** —— `waylandFrontend = true` 的**作用就是**不设它 |
| `QT_IM_MODULE` | KDE 下**不要设** |
| `--enable-wayland-ime` | **是 Chromium 的 flag，不是 fcitx5 的** |
| `i18n.supportedLocales` | 已隐藏/弃用，**不用设** |
| `fonts.fonts` | 已重命名 → **`fonts.packages`** |
| 字体优先级 | **拉丁字体在前、中文在后**（反了英文会难看） |
| 国内镜像 | USTC / TUNA；**不需要改 `trusted-public-keys`**（镜像用官方签名） |
| `nix.binaryCaches` | 仅 ≤21.11 存在，26.05 用会**构建失败** → 用 `nix.settings.substituters` |

## 4. GNOME / KDE / Flatpak / Steam：已核实的坑

| 坑 | 事实 |
|---|---|
| `services.displayManager.gdm.wayland` | **26.05 已删除**（GNOME 50 强制 Wayland），写了构建失败 |
| `programs.gnome-extensions` | **不存在** → 用「`pkgs.gnomeExtensions.<x>` + dconf `enabled-extensions = [ extensionUuid ]`」两步 |
| Nix 装的 GNOME 扩展 | **默认不激活**，必须 dconf 显式列出 |
| GNOME 分数缩放 | **无 NixOS 选项**，只能 gsettings |
| `qt.platformTheme = "gnome"` | 26.05 深色模式**是坏的** |
| `services.flatpak.enable` | 有**硬断言**：必须同时 `xdg.portal.enable = true`，否则构建失败 |
| **`services.flatpak.remotes`** | **在 nixpkgs 26.05 不存在！** 属第三方 `nix-flatpak` 模块。nixpkgs 只有 `enable` / `package` |
| NTFS 放 Steam 库 | **Valve 官方 Proton Wiki 明确「NOT RECOMMENDED」** —— 终于有权威一手出处 |
| `programs.mangohud` | **NixOS 无此模块**（只在 Home Manager）→ 用 `pkgs.mangohud` + Steam 启动项 / `steam.override { extraEnv }` |
| Steam 32 位 | `programs.steam.enable` **自动**开 `hardware.graphics.enable32Bit` |
| Steam 中文字体 | 用 **`programs.steam.fontPackages`** —— Steam 在独立 FHS 里，**看不到** `fonts.packages` |
| `programs.gamescope` | **存在**（很多资料说只有包没有模块，那是旧信息） |

## 5. Agent 管理系统的四层权限模型

| 方案 | 权限 | 安全性 | 配置难度 |
|---|---|---|---|
| **1. 只写配置，人工执行** | 只能改文件 | ⭐⭐⭐⭐⭐ | ★ 最低 |
| 2. 受限 sudoers（只放 `dry-build` 包装脚本） | 白名单命令 | ⭐⭐⭐ | ★★ |
| 3. polkit | 按动作授权 | ⭐⭐ | ★★★ |
| 4. 用户级 systemd | 只能管自己服务 | ⭐⭐⭐⭐ | ★★ |

**核心原则**：**agent 以普通用户运行，通过 MCP 获得「读」，通过 skills 获得「流程」，通过受限 sudo 获得「验证」，但「应用变更」永远留给人。**

**「架构上不给它能力」的具体手段**（systemd 单元字段）：

```ini
NoNewPrivileges = true      # 禁止 setuid 提权（最重要）
ProtectSystem = "strict"    # /usr /boot /etc 只读
ProtectHome = "read-only"
PrivateTmp = true
ReadWritePaths = [ ... ]    # 白名单
```

**用户级服务必备**：`users.users.<name>.linger = true;`（否则注销后服务被停）—— 已核实存在于 `config/users-groups.nix:455`。

**skills 格式**：Hermes 与 OpenClaw **共用 `SKILL.md`**（一份 skill 两边用）；Codex 用 **`AGENTS.md`**（格式不同）。

## 6. 游戏性能（第十四章）：优先级 + 已核实事实

### 6.1 优先级（收益排序）

| 优先级 | 手段 | 收益 | 位置 |
|---|---|---|---|
| 🥇 P0 | **Proton 版本选对** | 巨大（10–50% 或能跑/不能跑） | `programs.steam.extraCompatPackages = [ pkgs.proton-ge-bin ]` |
| 🥇 P0 | **mesa 版本够新** | 大 | 跟随 nixpkgs |
| 🥈 P1 | `hardware.graphics.enable32Bit` | 巨大（32 位游戏必需） | Steam 会自动开，但别依赖 |
| 🥈 P1 | **内存 / zram** | 大（卡顿主因） | `zramSwap.enable = true` |
| 🥉 P2 | 换 `linux_zen` | 中 | 见 6.2 |
| 🥉 P2 | `scx` 调度器 | 中（**负载相关**） | 见 6.3 |
| P3 | GameMode / gamescope | 小到中 | `programs.gamemode` / `programs.gamescope` |
| P4 | I/O 调度器 / sysctl | 小 | 见 6.4 |

### 6.2 内核变体：nixpkgs 26.05 的真实情况

| 属性 | 状态 | 版本 |
|---|---|---|
| `linuxPackages`（默认） | ✅ | **6.18** |
| `linuxPackages_latest` | ✅ | **7.2.9**（与 `nixos-unstable` 逐字相同，见 §13） |
| `linuxPackages_zen` | ✅ | **7.2.9-zen1** |
| `linuxPackages_xanmod` | ✅ | **6.18.55-xanmod1**（`variant="lts"`）⚠️ 反直觉 |
| `linuxPackages_xanmod_stable` / `_latest` | ✅ | **7.2.9-xanmod1**（都是 `variant="main"`） |
| `linux_lqx` / `linux_libre` / `linux_hardened` / `linux-rt` | ❌ **全部已删除**（`throw`） | — |
| `linux_cachyos` | ❌ **nixpkgs 从未收录** | — |

**编译期配置差异（源码级）**

| 配置 | 默认 6.18 | `linux_zen` | `linux_xanmod` |
|---|---|---|---|
| 抢占 | `PREEMPT=no` + **`PREEMPT_LAZY=yes`** | **`PREEMPT=yes`** | 6.13+ `PREEMPT_LAZY=yes` |
| HZ | 未设（内核默认 250） | **1000** | 250 |
| I/O 调度器 | `MQ_IOSCHED_DEADLINE/KYBER=yes`、`IOSCHED_BFQ=module` | **`IOSCHED_BFQ=yes`**（内建） | 同默认 |
| CPU governor | `SCHEDUTIL` | 继承 | **`GOV_PERFORMANCE`** |
| sched_ext | **`SCHED_CLASS_EXT=yes`**（≥6.12）→ **默认内核就能跑 scx** | 继承 | 继承 |
| **ntsync** | ❌ **未启用** | ✅ **`NTSYNC=yes`** | ❌ |
| FUTEX2 | 未设 | ✅ `FUTEX`/`FUTEX_PI` | 未设 |

出处：`common-config.nix:126,262-265,1417-1419,1430`、`zen-kernels.nix`、`xanmod-kernels.nix`

### 6.3 `services.scx`（sched-ext）—— 26.05 原生支持

| 项 | 值 |
|---|---|
| 模块路径 | `nixos/modules/services/scheduling/scx.nix` |
| 选项 | `enable` / `package`（默认 `pkgs.scx.full`）/ `scheduler`（enum，默认 **`"scx_rustland"`**）/ `extraArgs` |
| **硬断言** | **内核 ≥ 6.12**，否则求值期报错 |
| 服务条件 | `ConditionPathIsDirectory = "/sys/kernel/sched_ext"`（内核不支持时**静默跳过**） |
| 重启策略 | `Restart=on-failure`，`startLimitIntervalSec=30` / `startLimitBurst=2` |
| 临时换调度器 | `systemctl set-environment SCX_SCHEDULER_OVERRIDE=<name>` → `restart scx` |
| 调度器总数 | **26 个**（18 Rust + 8 C 示例） |
| **Valve 关联** | **`scx_lavd` 由 Igalia 受 Valve 委托开发**，动机是 Steam Deck 游戏负载 |
| ⚠️ 冲突 | **`services.system76-scheduler` 与 scx 互斥**（scx 替换了 CFS，后者的 CFS 调优全部失效） |

> `scx_nest` 是 **C 示例**（教学用），不是 Rust 调度器 —— 很多中文文章列错了。

### 6.4 三个「流传很广但错误」的性能建议

| 错误建议 | 事实 | 出处 |
|---|---|---|
| `boot.kernelParams = [ "elevator=bfq" ]` | **内核已明确废弃** —— `elevator_setup()` 只剩 `pr_warn("Kernel parameter elevator= does not have any effect anymore. Please use sysfs to set IO scheduler for individual devices.")` | `torvalds/linux block/elevator.c:893-898` |
| 调 `vm.max_map_count` | **NixOS 默认已是 `1048576`**（`mkDefault`）—— 比常见教程值还高 | `config/sysctl.nix:114` |
| 调 `fs.inotify.max_user_watches` | **NixOS 默认已是 `524288`**（传统默认 8192） | `config/sysctl.nix:119-120` |

**I/O 调度器的正确设置法**：`services.udev.extraRules`（→ `/etc/udev/rules.d/99-local.rules`）

```nix
services.udev.extraRules = ''
  ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/rotational}=="1", ATTR{queue/scheduler}="bfq"
  ACTION=="add|change", KERNEL=="nvme[0-9]*n[0-9]*", ATTR{queue/scheduler}="none"
'';
```

## 7. 语言工具链（第十五章）：26.05 已核实版本与破坏性变更

| 工具 | 属性 | 版本/状态 |
|---|---|---|
| Node.js | `pkgs.nodejs` | **24 LTS**（默认，22→24 破坏性升级） |
| `pkgs.nodejs_22` / `_26` | ✅ 存在；`nodejs_latest = nodejs_26` | |
| **`pkgs.nodePackages.*`** | ❌ **26.05 整体删除** → 改用顶层属性 | release notes:117 |
| `corepack_latest` | ❌ 已删除；`nodejs-slim` 不再带 corepack | release notes:144,445 |
| Python | `pkgs.python3` = **3.13** | |
| uv / bun / deno | **0.11.21 / 1.3.13 / 2.8.3** | |
| typescript / tsx / esbuild | ✅ 存在 | |
| **ts-node** | ❌ **404，不在 nixpkgs** → 用 `tsx` | |
| `swc-core` | ❌ 404 | |
| mise / devenv / ruff | ✅ 存在 | |
| **pnpm** | ✅ `pkgs.pnpm` = `pnpm_11`（`all-packages.nix:2967`）；by-name **无** | 另有 `pnpm_8/9/10/10_29_2/10_latest/12` |
| **yarn** | ✅ `pkgs.yarn`，**就在 by-name**（`by-name/ya/yarn/package.nix`） | 另有 `yarn-berry` / `yarn-zpm` |
| **rustup** | ✅ `pkgs.rustup`（`all-packages.nix:4396`）；by-name **无** | 属性有效，可直接用 |

**三层策略**：L2 `devShell`（项目，首选）→ L1 系统包 → L3 官方包管理器（逃生舱）

**核心坑**

- `npm i -g` 在 NixOS 报 `EACCES` 是**设计如此** → `npm config set prefix ~/.npm-global`
- **`environment.sessionVariables.PATH` 会覆盖而非追加 PATH → 破坏系统 PATH**。用 shell rc 或 Home Manager `home.sessionPath`
- `pip install` 报 `externally-managed-environment`（PEP 668）→ devShell / venv / `uv`
- **`programs.nix-ld.libraries` 的「默认 `[ ]`」是误读** —— 选项声明虽写 `default = [ ]`，但 `config` 段（`nix-ld.nix:47-64`）**无条件注入 14 个基础库**（`zlib zstd stdenv.cc.cc curl openssl attr libssh bzip2 libxml2 acl libsodium util-linux xz systemd`）。因类型是 `listOf`（合并语义 = **拼接**），你写的 `libraries` 是**追加**而非替换。所以「开了还报缺库」的真正原因是**基础集只覆盖 CLI 场景**，GUI 应用需补 `libGL` / `libxkbcommon` / `gtk3` / `xorg.*`
- 26.05：`buildPythonPackage` 遇 `pytestFlagsArray` 现在**直接报错**（以前是警告）
- 26.05：`buildNpmPackage` 新增 `npmDepsFetcherVersion`（设 `2` 修复 npm workspaces 构建）

## 8. MCP / SearXNG / Agent 工具（第十六章）

### 8.1 npm 型 MCP server 的四种处理方式

| 方式 | 做法 | 何时用 |
|---|---|---|
| 1 | **nixpkgs 有就用 nixpkgs**（如 `pkgs.mcp-nixos`，已核实存在） | 首选 |
| 2 | `npx -y <pkg>` | ⚠️ NixOS 上易失败（原生模块链接宿主 glibc） |
| 3 | **`npm i -g` 到用户目录 + 写绝对路径** | **重度用户推荐** |
| 4 | `buildNpmPackage` 打成 derivation | 要多机复现 |

**关键**：方式 2/3 都需要 **`programs.nix-ld` + 自己列 `libraries`**（`libuv`、`libsecret` 等）。

### 8.2 SearXNG（`services.searx`）全部选项

`enable` / `openFirewall` / `domain` / `environmentFile` / `redisCreateLocally` / `settings` / `settingsFile` / `faviconsSettings` / `limiterSettings` / `configureUwsgi` / `configureNginx` / `uwsgiConfig`

| 要点 | 说明 |
|---|---|
| **agent 需要 JSON** | 必须 `settings.search.formats = [ "html" "json" ]`，**默认只有 html** |
| **`secret_key` 不能明文** | 会进 `/nix/store`（全局可读、永久保留）→ 用 `environmentFile` |
| 26.05 改名 | `configFile`→**`settingsFile`**；`runInUwsgi`→**`configureUwsgi`**；`settings.redis`→**`settings.valkey`**（旧名仍兼容但警告） |

### 8.3 Playwright

| 项 | 值 |
|---|---|
| 版本 | **1.59.1** |
| 正确用法 | `pkgs.playwright-driver.browsers` / `.browsers-chromium` + `PLAYWRIGHT_BROWSERS_PATH` |
| ❌ 错误用法 | `npx playwright install` —— 下载的浏览器在 NixOS 上**大概率启动失败** |
| 体积 | `browsers` 全量含 Chromium+Firefox+WebKit+ffmpeg（数 GB）；agent 用途用 `browsers-chromium` |

### 8.4 凭据与沙箱

- ❌ API key 写进 `configuration.nix` → 进 `/nix/store`，全局可读、永久保留
- ✅ **sops-nix / agenix**，`owner` 必须是**你的普通用户**（否则非 root agent 读不到）
- 给 filesystem MCP **只暴露专用工作目录**，不要暴露整个家目录
- 原则：**agent 的爆炸半径 = 它需要访问的目录**

## 9. 安全 / 防病毒 / FHS（第十七章）

### 9.1 SELinux 之问：**NixOS 没有 SELinux 模块**

| 机制 | 状态 |
|---|---|
| **AppArmor** | ✅ `security/apparmor.nix` |
| **SELinux** | ❌ **无模块**（module-list.nix 匹配数 = **0**） |
| audit / auditd | ✅ `security/audit.nix`、`security/auditd.nix` |
| ClamAV / fail2ban | ✅ `services/security/{clamav,fail2ban}.nix` |

**为什么没有**：SELinux 需要对整个文件系统打标签，而 `/nix/store` 是内容寻址、只读、多代共存的 —— 同一个 store path 被不同代际共享，**标签无法按代际区分**，语义上与 Nix 模型冲突。

**NixOS 的正确隔离姿势**：**systemd 沙箱**（按服务粒度）

```ini
ProtectSystem = "strict"
ProtectHome = "read-only"
PrivateTmp = true
PrivateDevices = true
NoNewPrivileges = true
RestrictSUIDSGID = true
SystemCallFilter = [ "@system-service" ]
```

### 9.2 防病毒：NixOS 的真实优势与**没有**的优势

| 维度 | 谁更好 |
|---|---|
| 系统级持久化 | **NixOS**（`/nix/store` 只读 → 无法写 `/usr/bin`、无法改 `/etc/ld.so.preload`） |
| 供应链完整性 | **NixOS**（内容寻址 + 签名 cache + 可复现构建 + 可独立验证 hash） |
| 被入侵后恢复 | **NixOS**（generation 原子回滚） |
| **用户级恶意代码（投毒 npm/pip 包）** | **打平 —— 一样中招** |
| **钓鱼 / 社工 / 浏览器漏洞** | **打平** |
| 杀毒软件生态 | 传统发行版（但对桌面用户无意义） |

**诚实结论**：**NixOS 让你「更不容易被持久化」，但不会让你「更不容易被钓鱼」。** 它解决系统完整性问题，不解决人的判断力问题。

### 9.3 FHS 决策树（从上往下试）

```
nixpkgs 里有 → nix-shell -p / systemPackages
从源码编译   → devShell
预编译二进制 → programs.nix-ld（libraries 必须自己列！）
AppImage     → programs.appimage = { enable = true; binfmt = true; }
完整 FHS 树  → buildFHSEnv
临时试一下   → steam-run ./binary
```

| 关键事实 | 说明 |
|---|---|
| `programs.appimage.binfmt = true` | 注册 magic-based binfmt（匹配 `AI\x01`/`AI\x02`）→ **AppImage 可双击运行** |
| `programs.appimage` 选项 | `enable` / `binfmt`（都默认 false）/ `package`（默认 `pkgs.appimage-run`） |
| `steam-run` | 依赖 Steam 运行时，**不是长期方案** |
| `nix-ld` + `appimage` | **可以同时开**，不冲突 |

### 9.4 安全加固 ↔ 性能优化的真实冲突

> **`kernel.unprivileged_bpf_disabled = 1` 会让 `services.scx` 失效** —— sched_ext 需要 BPF 能力。要用 scx 就不要设这一条。

## 10. 不加外部仓库逼近 CachyOS（第十八章）

**一句话**：CachyOS 被称道的「手感」主要来自**用户态调度器 + 进程优先级**两层，这两层 nixpkgs 都是一等公民；**唯一真正拿不到的是 BORE 内核补丁**。

### 10.1 逐层可复刻性

| CachyOS 层 | nixpkgs 原生替代 | 状态 |
|---|---|---|
| 内核（BORE / BMQ / POC idle selector） | 无。`linux_zen` **也不含** BORE | ❌ 拿不到 |
| 用户态调度器 `scx-scheds` | `services.scx`（26 个调度器，含 `scx_lavd` / `scx_bpfland`） | ✅ 完全 |
| 进程优先级 ananicy-cpp + **CachyOS 官方规则** | `services.ananicy` + `pkgs.ananicy-rules-cachyos` | ✅ 完全 |
| sysctl（`70-cachyos-settings.conf`） | `boot.kernel.sysctl` 逐行翻译 | ✅ 可抄（有 2 个坑） |
| udev（9 条规则） | `services.udev.extraRules` | ✅ 7 条可抄 / 2 条抄不了 |
| zram + THP | `zramSwap` + `systemd.tmpfiles.rules` | ✅ 可抄（**别抄 100%**） |
| uksmd（用户态 KSM） | `hardware.ksm`（内核 KSM） | ⚠️ 近似 |
| systemd limits / journald / timesyncd | `systemd.settings.Manager` / `services.journald.extraConfig` | ✅ 部分（**timeout 别抄**） |
| mesa-git / proton-cachyos | 无（只有稳定 `mesa` / `proton-ge-bin`） | ❌ 拿不到 |

### 10.2 两个关键包（已核实存在）

```
pkgs.ananicy-rules-cachyos   0-unstable-2026-05-19  ← 就是 CachyOS 官方仓库 CachyOS/ananicy-rules（rev 74b314e…）
pkgs.ananicy-cpp             1.2.0                  ← CachyOS 用的引擎（不是老的 ananicy）
```

**配置要点**：`package`（引擎）与 `rulesProvider`（规则来源）是**两个不同选项**，配错任一个都不会生效。

```nix
services.ananicy = {
  enable = true;
  package = pkgs.ananicy-cpp;                  # 引擎
  rulesProvider = pkgs.ananicy-rules-cachyos;  # ← CachyOS 官方规则（复制到 /etc/ananicy.d/）
};
services.scx = { enable = true; scheduler = "scx_lavd"; };
```

### 10.3 关于 BORE：三条硬事实

1. BORE 的内核符号是 **`CONFIG_SCHED_BORE`**，只存在于 `linux-cachyos`（变体：`-bore` / `-hardened` / `-rt-bore` / `-deckify`）。
2. **nixpkgs 从未收录 CachyOS 内核**（`linux-kernels.nix` + `all-packages.nix` 里 `cachy` grep = **0**）。
3. **`linux_zen` 也不含 BORE** —— `zen-kernel` v7.2.9-zen1 的 `kernel/Kconfig.preempt` 里搜不到 `bore`；`kernel/sched/fair.c` 里的 `burst` 是**上游 CFS 的 burst quota**（`cfs_b->burst_time` / `nr_burst`），与 BORE 无关。

**替代路径**：BORE 想解决的问题（交互/游戏任务优先、降卡顿）由 **`scx_lavd`** 在用户态达成，而且能靠 `SCX_SCHEDULER_OVERRIDE` **热切换**做 A/B —— 这一点比 BORE 更灵活。

### 10.4 换 `linux_zen` 唯一的硬收益：`NTSYNC` 是内建的

`zen-kernels.nix` 的 `structuredExtraConfig` 里 **`NTSYNC = yes`**（编译进内核），而**默认内核的 `common-config.nix` 没有 `CONFIG_NTSYNC`**（上游默认 `N`）→ 默认内核很可能没有 `ntsync.ko`。
CachyOS 靠 `/usr/lib/modules-load.d/ntsync.conf` 加载模块；NixOS 换 zen 后 `/dev/ntsync` 直接存在，**不需要写 `boot.kernelModules`**（写反而可能加载失败）。

zen 其余差异（都已在源码核实）：`PREEMPT=yes`（`mkOverride 90` 强制）、`PREEMPT_LAZY=no`、`HZ=1000`、`IOSCHED_BFQ=yes`（内建）、`ZEN_INTERACTIVE=yes`、`FUTEX`/`FUTEX_PI=yes`、`DEFAULT_FQ_CODEL=yes`。**对 `amdgpu` 没有任何额外收益**（zen 是调度/延迟补丁）。

### 10.5 CachyOS sysctl 的两个坑

| CachyOS 原值 | 坑 |
|---|---|
| `kernel.unprivileged_userns_clone = 1` | **主线内核没有这个键**（Debian/Arch 系补丁）。写了 systemd-sysctl 报错 |
| `kernel.printk = 3 3 3 3` | NixOS 里**必须写成字符串**（`boot.kernel.sysctl` 只接受 bool / int / string / null） |

其余可抄项（原文件逐行读过）：`vm.swappiness=100`（**前提是有 zram**）、`vm.vfs_cache_pressure=50`、`vm.dirty_bytes=268435456`、`vm.dirty_background_bytes=67108864`、`vm.dirty_writeback_centisecs=1500`、`vm.page-cluster=0`、`kernel.nmi_watchdog=0`、`kernel.kptr_restrict=2`、`net.core.netdev_max_backlog=4096`、`fs.file-max=2097152`。

**明确不要抄**：`DefaultTimeoutStartSec=15s`（NixOS 的 rebuild/激活会被打断）、`zram-size = ram`（100% 会 OOM）、`modprobe.d/amdgpu.conf`（只对 GCN 1/2 老卡）、`blacklist.conf`（代价是失去硬件看门狗）、`20-audio-pm.rules`（依赖 CachyOS 自研脚本）。

### 10.6 udev 规则：7 条可抄、2 条抄不了

| CachyOS 文件 | 结论 |
|---|---|
| `60-ioschedulers.rules` | ✅ HDD→`bfq` / SATA SSD·eMMC→`mq-deadline` / **NVMe→`kyber`** |
| `50-sata.rules` | ✅ SATA ALPM 强制 `max_performance` |
| `69-hdparm.rules` | ✅ 但**必须写 `${pkgs.hdparm}/bin/hdparm`**（NixOS 没有 `/usr/bin`） |
| `40-hpet-permissions` / `99-cpu-dma-latency` | ⚠️ 可抄，只对专业音频（JACK）有意义 |
| `30-zram.rules` | ⚠️ 部分 —— NixOS 里用 `zramSwap` + sysctl 更干净 |
| `20-audio-pm.rules` | ❌ 依赖 CachyOS 自研 `/usr/lib/udev/audio-pm-ctl` |
| `71-nvidia` / `85-iw-regulatory` | ➖ N/A（你是 AMD + 有线） |

### 10.7 验收（最关键的一条）

```bash
cat /sys/kernel/sched_ext/root/ops   # 有输出 = 内核支持 sched-ext，scx 那套能完整用上
ls /etc/ananicy.d/00-default/        # 有 Games/ Audio-Video/ 等目录 = CachyOS 规则已生效
for d in /sys/block/*/queue/scheduler; do echo "$d: $(cat $d)"; done
```

> **注意 `services.scx` 有个静默失败**：内核不支持时它靠 `ConditionPathIsDirectory=/sys/kernel/sched_ext` **直接跳过，不报错**。所以必须自己验一次。

## 11. 第二轮全量复核（v1.3）：修正了什么

对全文做了一次逐条一手复核（22 个 nixpkgs 模块 + 内核源码 + 两套 release notes + Wiki）。**结论：主体可靠，但有 6 类事实错误被改正。**

### 11.1 模块路径错误（原稿写错，已改正）

| 项 | 原稿（❌ 404） | 正确路径 |
|---|---|---|
| GNOME | `services/x11/desktop-managers/gnome.nix` | **`services/desktop-managers/gnome.nix`** |
| Plasma 6 | `services/x11/desktop-managers/plasma6.nix` | **`services/desktop-managers/plasma6.nix`** |
| GDM | `services/x11/display-managers/gdm.nix` | **`services/display-managers/gdm.nix`** |
| SDDM | `services/x11/display-managers/sddm.nix` | **`services/display-managers/sddm.nix`** |
| xdg portal | `services/x11/xdg-portal.nix` | **`config/xdg/portal.nix`** |

> **可复用的教训**：NixOS 把「桌面环境」和「显示管理器」从 `services/x11/` 搬到了 `services/` 下，但 `services/x11/display-managers/` 目录**仍然存在**（只剩 lightdm / slim / startx / sx / xpra）。所以 `ls` 目录看不出问题，**必须逐个 curl 验证文件本身**。

### 11.2 「两套 release notes」是两个不同文件

| 文件 | 讲什么 |
|---|---|
| `doc/release-notes/rl-2605.section.md` | **nixpkgs** 层（GCC 15、glibc 2.42、`corepack_latest` 删除） |
| `nixos/doc/manual/release-notes/rl-2605.section.md` | **NixOS** 层（内核 6.12→6.18、`linux_hardened` 移除、`systemd.extraConfig` 移除） |

引「内核升级」时引到前者 = 引错文件。

### 11.3 `programs.nix-ld.libraries`：「默认空」是误读（高价值）

见第 7 节的核心坑。要点：**选项声明 `default = [ ]` ≠ 最终生效值**；模块 config 段强制注入 14 个库；`listOf` 的合并是**拼接**，用户写法是**追加**。

> **可复用的教训**：判断一个选项的「实际默认值」时，**不能只看 `mkOption { default = ...; }`** —— 还要看同一模块（或别的模块）的 `config` 段有没有**强制赋值**。`defaultText` 字段是识别这种差异的线索（本例它写着 *"baseLibraries derived from systemd and nix dependencies."*）。

### 11.4 内核侧全部加固（原稿正确）

`linux_default = linux_6_18`（`linux-kernels.nix:740`）、`linux_latest = linux_7_2`（`:742`）、`linux_hardened`/`linux-rt`/`linux_lqx`/`linux_libre` 全 `throw`、默认内核 `PREEMPT=no`+`PREEMPT_LAZY`（`common-config.nix:1417-1419`）、`SCHED_CLASS_EXT`（`:1430`）、`NTSYNC` 未设（grep=0）、`scx.full` = 26 个调度器。

### 11.5 包存在性：一条修正 + 若干精确化

- ❌→✅ **`yarn` 就在 by-name**（原稿记「by-name 404」）
- ⚠️→✅ `pnpm` / `rustup` by-name 确实无，但**属性有效**（`all-packages.nix:2967` / `:4396`）
- ⚠️ `ollama-{rocm,cuda,vulkan,cpu}` **无独立 by-name 目录**，由 `all-packages.nix:424-427` 用 `acceleration` 参数生成
- ⚠️ `scx` 在 `pkgs/os-specific/linux/scx/`，**不在 by-name**

### 11.6 新增发现（原稿未覆盖）

- `hardware.amdgpu.opencl.enable` / `zluda.enable` **会 `mkDefault` 开 `hardware.graphics.enable`** —— 所以「谁会替你开 graphics」的完整答案是 3 处（原稿只说 steam）
- `hardware.amdgpu.zluda.package` 是第 7 个选项
- `services.scx` 的 `ExecStart` 有**两个**覆盖变量：`SCX_SCHEDULER_OVERRIDE` **和** `SCX_FLAGS_OVERRIDE`
- `services.lact.settings` 存在，但非空时会让 GUI 无法改配置

## 12. 第三轮新增（v1.4）：Hermes / OpenClaw 在 NixOS 上的落地与坑

新增第十九～二十二章。**核心是回答「作为服务时，root 权限会不会导致 user 改不了配置」。**

### 12.1 三套管理方案的定位（第十九章）

- `configuration.nix`（系统层）/ `home-manager`（用户层）/ `flake`（依赖层）**不是三选一**，是三个层次。flake 里通常仍然有 `configuration.nix`。
- **Home Manager 不在 nixpkgs 里**（`module-list.nix` grep = 0），是 `nix-community` 独立仓库；有 standalone 模式，**不需要 root**。
- 混合方案最大的浪费：`environment.systemPackages` 与 `home.packages` 写同一个包 = 装两遍。

### 12.2 flake 进阶（第二十章）

- **`pkgs.unstable` 不存在** —— 一个 NixOS 配置的 `pkgs` 只来自一个 nixpkgs 实例。
- **但「两套 nixpkgs 并存」≠「必须有 flake」**（v1.5 修正）。不用 flake 也有三条路：channel（`import <nixos-unstable> {}`）、`builtins.fetchTarball`、`builtins.fetchGit` + 钉 `rev`。**flake 只是让这件事最顺手 + 自动管版本号（`flake.lock`）。**
- 四种写法：**`_module.args.pkgsUnstable`（✅ 推荐，按需求值）**、overlay 挂 `pkgs.unstable`（⚠️ 官方论坛不推荐：「完全没必要，很可能拖慢 eval」）、overlay 逐包覆盖（有依赖树混血风险）、`legacyPackages` 直取（改动面最小）。
- **`follows` 是最容易搞错的一行**：第三方 flake 的 `nixpkgs` input 应该 `follows` 你自己的，否则 `/nix/store` 里出现两套 glibc。HM input 不 follow 更糟 —— 两个 HM 会让 `home-manager switch` 直接失败。

### 12.3 两个软件的支持等级与部署层次（第二十一章）

| 软件 | nixpkgs 包 | nixpkgs 模块 | 上游官方 flake | 支持等级 |
|---|---|---|---|---|
| **OpenClaw** | ✅ `pkgs.openclaw`（**带 `knownVulnerabilities`**） | ❌ 无 | ✅ `github:openclaw/nix-openclaw`（712★，三套模块：nixos / home-manager / darwin） | 上游官方维护，**但不接受 PR、Issue 不监控** |
| **Hermes Agent** | ❌ 不在 nixpkgs | ❌ 无 | ✅ 官方仓库自带 `flake.nix` + `nix/nixosModules.nix` | **官方明说 Tier 2，best-effort** |

**两个官方都用同一套语言说同一件事**：*"一个人的 agent"应该跑成用户服务，不是系统服务。* → **`systemd.user.services`**。

### 12.4 核心答案：root 权限边界（第二十一章 §21.7 / §21.10）

| 部署方式 | 服务运行身份 | 配置在哪 | 谁的 | **普通用户能改配置吗** | **对话里让 agent 改能生效吗** | 需要 root 吗 |
|---|---|---|---|---|---|---|
| **官方 bash / `nix profile`** | **你自己** | `~/.hermes/config.yaml` 或 `~/.openclaw/openclaw.json` | **你** | ✅ **能** | ✅ **能** | ❌ 不用 |
| **Home Manager 模块** | **你自己**（`systemd.user.services`） | `~/.hermes/` 或 `~/.openclaw/`（Nix 写） | 你 | ⚠️ 文件可写，但**每次 switch 被 Nix 覆盖**；OpenClaw 侧是**指向 Nix store 的只读符号链接** | ❌ **不能**（`HERMES_MANAGED` / `OPENCLAW_NIX_MODE=1` 主动拦） | ❌ **不用** |
| **NixOS 系统模块** | `hermes` / `openclaw` **系统用户** | **`/var/lib/hermes/.hermes/`**（`0750`）或 **`/etc/openclaw/openclaw.json`**（`0755 root root`） | **root** | ❌ **不能**（`/var/lib/hermes` 连 `ls` 都 permission denied） | ❌ 不能 | ✅ **要**（`sudo nixos-rebuild switch`） |
| **Hermes container 模式** | 系统服务 + 容器内非特权用户 | `/data/.hermes/config.yaml` | root | ❌ 不能 | ❌ 不能 | ✅ 要 |

> **一句话**：**要"agent 能在对话里改自己的配置"，只有官方 bash / `nix profile` 那条路。** 声明式（模块）与可对话修改，**不可兼得**。

**关键机制名**（记这两个就不会迷路）：
- Hermes：`HERMES_MANAGED` 环境变量 + `HERMES_HOME/.managed` 标记文件 → 阻断 `hermes setup` / `config edit` / `config set` / `gateway install` / `gateway uninstall`
- OpenClaw：`OPENCLAW_NIX_MODE=1`（nix-openclaw 自动设）→ 配置只读；非 Nix 场景用 `OPENCLAW_CONFIG_READONLY=1`

### 12.5 自启：`linger` 是唯一必须一次性 root 的地方（第二十一章 §21.6）

- **用户级 systemd 服务默认只在你登录期间存在**。`loginctl enable-linger <user>`（或 NixOS 的 `users.users.<n>.linger = true`）才能开机自启。**这需要 root 设一次，而且 Home Manager 自己设不了**（linger 是账户属性）。
- **Hermes 的 cron 依赖它**：cron job 走 `systemd-run --user --scope`，没有 user manager 就 **fail closed —— 一个 cron job 都不跑，且不报错**。
- Hermes 的 NixOS 模块自动处理（`linger = lib.mkDefault (!cfg.container.enable)` + 排序 `linger-users.service` + `preStart` 轮询 `/run/user/<uid>/bus` 最多 10s）。**但 `mkDefault` 会被你自己的用户声明压掉** —— 用 `createUser = false` 时务必自己写 `linger = true`。

### 12.6 坑与社区意见（第二十二章）

**四类坑，代价差别极大：**

| 类别 | 具体 | 代价 |
|---|---|---|
| **① 构建成本** | flake **无二进制缓存**，每次 bump nixpkgs **重建 ~666 个 derivation**（`#130870`） | 🔴 极贵：4vCPU/8GB VPS 上 OOM killer **两次杀掉 `nix-daemon`**；加 12 GB swap 后仍需数小时 |
| **② NixOS 环境** | **stub-ld**：预编译动态 ELF 跑不起来；Hermes 工具闭包永远"不同步"（`#134249`） | 🟠 中：刷屏警告，但功能可用（`ffmpeg`/`node`/`npm` 由 nixpkgs 提供） |
| **③ 权限与生命周期** | 无 linger → cron 静默全不跑；手写系统 unit 漏 `User=` → **agent 以 root 跑** | 🔴 极贵且隐蔽 |
| **④ 版本与身份** | `hermes --version` 报旧版本日期（`#135217`）或报 `0.0.0` | 🟢 低：用 `nix path-info` 旁证 |

**三方社区态度：**
- **nixpkgs 侧**：OpenClaw 被标 insecure，**导致自动更新卡死**（Discourse #76940，维护者 `chrisportela` 原话：*"There are also a number of CVEs filed for it routinely"*；社区回答 *"No"*）。要最新版别依赖 `pkgs.openclaw`。
- **OpenClaw 官方**：**不接受 PR，GitHub Issue 不监控**，唯一渠道是 Discord `#golden-path-deployments`。
- **Hermes 官方**：接受 PR，Nix issue 活跃（3374 条命中），但**优先级低于 Tier 1**。

**第三方补充**：`0xrsydn/nix-hermes-agent`（46★，活跃）——**选项名是 `config` 不是 `settings`**，配置文件是 `cli-config.yaml` 不是 `config.yaml`，**有 `skills` 声明式但没有 HM 模块、没有 container 模式，且未见 linger 处理**。抄配置时选项名不能混用。

## 13. 第四轮（v1.5）：双分支版本实测 + 混合版本策略的两处修正

**本轮动作**：在 `nixos-26.05` 与 `nixos-unstable` 两个分支上逐包比对版本，并复核「稳定基座 + 滚动组件」相关结论。

### 13.1 逐包实测（2026-10-12）

| 组件 | 26.05 | nixos-unstable | 差异 |
|---|---|---|---|
| 内核 `linuxPackages_latest` | **7.2.9** | **7.2.9** | ❌ 无 |
| 内核 `linuxPackages`（默认） | **6.18.55**（LTS） | **6.18.55**（LTS） | ❌ 无 |
| **Mesa** | **26.1.8** | **26.2.4** | ✅ 有 |
| **proton-ge-bin** | **GE-Proton11-1** | **GE-Proton11-7** | ✅ 有 |
| **gamescope** | **3.16.23** | **3.16.31** | ✅ 有 |
| **mangohud** | **1.91.6** | **1.91.6** | ❌ 无 |

**复验**（`<branch>` = `nixos-26.05` / `nixos-unstable`）：
```bash
curl -sL "https://raw.githubusercontent.com/NixOS/nixpkgs/<branch>/pkgs/os-specific/linux/kernel/kernels-org.json"
curl -sL "https://raw.githubusercontent.com/NixOS/nixpkgs/<branch>/pkgs/development/libraries/mesa/common.nix"
```

### 13.2 修正一：内核「AMD 可以自由滚」→「能滚，但没必要」

- 两分支 `pkgs/top-level/linux-kernels.nix` 的 `packageAliases` **逐字相同**（`linux_default = packages.linux_6_18; linux_latest = packages.linux_7_2;`），`kernels-org.json` 里 `"7.2" → 7.2.9` 也完全一致。
- **stable 分支会定期把内核 rebase 到最新补丁。** 所以 **26.05 上跨源拿内核 = 多拉一整份 nixpkgs，换来的版本号一模一样**。
- 正确写法：`boot.kernelPackages = pkgs.linuxPackages_latest;`（**属于基座 `pkgs`，不跟 unstable**）。
- **跨源换内核真正的失败模式是模块树**：`boot.extraModulePackages`（`listOf types.package`）被拼进 `system.modulesTree = [ (lib.getOutput "modules" kernel) ] ++ config.boot.extraModulePackages;`（`nixos/modules/system/boot/kernel.nix:197-202`、`:394`）→ 「为 6.18 编译的 .ko」与「7.2 内核」并存。
- **仍不能跨源**：`r8168` 等树外模块、NVIDIA、ZFS、VirtualBox。

### 13.3 修正二：「两套 nixpkgs 必须有 flake」→「不用 flake 也有三条路」

| 路 | 需要 channel？ | 需要 flake？ | 锁版本？ | 日常升级 |
|---|---|---|---|---|
| **A** channel（`import <nixos-unstable> {}`） | ✅ | ❌ | ❌ 完全不锁 | 2 步 |
| **B** `builtins.fetchTarball` | ❌ | ❌ | ⚠️ 加 `sha256` 才锁 | 2 步（手工查 hash） |
| **C** `builtins.fetchGit` + 钉 `rev` | ❌ | ❌ | ✅ 手工锁 | 2 步（手工查 rev） |
| **D** flake | ❌ | ✅ | ✅ `flake.lock` | 2 步（`nix flake update`） |

> **看清本质**：B/C 的日常升级和 D 一样是 2 步，差别只在第 1 步是「你手工改 hash/rev」还是「`nix flake update` 替你改 `flake.lock`」。**flake 没让升级变简单，它只是把「手工锁」自动化了。**

**推荐写法修正**：overlay 挂 `pkgs.unstable` **官方论坛不推荐**（「完全没必要，很可能拖慢 eval」）；**推荐 `_module.args.pkgsUnstable = unstable;`**（按需求值，eval 开销小）。

### 13.4 首次搭建 vs 日常升级（步骤数）

| 口径 | 首次 | 日常 |
|---|---|---|
| A channel | 3 步 | 2 步 |
| B/C `configuration.nix` + fetch | 3 步 | 2 步 |
| D flake + 手动换锁 | **6 步** | 2 步 |
| E flake + 自动换锁 | **8 步** | **0 步** |

**flake 的「6 步」是一次性成本**（写 `flake.nix` / `git init` / 首次 rebuild 生成 `flake.lock`）。搭完之后每天 2 步（配了自动换锁就是 0 步）。

**详版**：`nixos-ops-guide.md` §6.0 / §6.2 / §6.4 ③ / §6.6；`nixos-amd-guide.md` §11.2.1 / §20.4.1 / §20.5 / 附录 B.12。

## 14. 第五轮（v1.6）：把 NixOS 用成「Bazzite 模式」（第二十三章）

> 用户第 8 问最后一条。**核心结论：能复刻约 80%，剩下 20%（开箱即用整机体验 + GUI 门户）不该复刻。**

### 14.1 Bazzite 的六层软件层级（官方原文，`[官方]`）

来源：<https://docs.bazzite.gg/Installing_and_Managing_Software/software-intro/>

**从最推荐到最不推荐**：

| # | Bazzite 层级 | 关键措辞 |
|---|---|---|
| ① | Bazzite Portal（`ujust`） | 定位为「系统级设置的扩展」而非应用商店 |
| ② | **Bazaar（Flatpak）** | ***"it is primary method of obtaining software on Bazzite"*** |
| ③ | Homebrew | 只用于 CLI/TUI 工具 |
| ④ | Containers（Distrobox / Quadlet） | Flatpak 与 brew 都没有时的出路 |
| ⑤ | AppImage | 依赖宿主系统级库 |
| ⑥ | `rpm-ostree` 分层 | ***"not recommended, use as a last resort"*** |

### 14.2 映射表：哪两处顺序是**反的**（最高价值的一条）

| # | Bazzite | NixOS 对应 | 等价度 |
|---|---|---|---|
| ① | Portal / `ujust` | `programs.nh` + 自写 `justfile` | ⚠️ 70% |
| ② | **Flatpak 优先** | **Nix 优先，Flatpak 兜底** | ❌ **顺序相反** |
| ③ | Homebrew | nixpkgs / HM / `nix profile` | ✅ 更强 |
| ④ | Distrobox | `pkgs.distrobox`（**同为 1.8.2.5**） | ✅ 等价 |
| ⑤ | AppImage | `programs.appimage.binfmt = true` | ✅ 等价 |
| ⑥ | **`rpm-ostree` 是最后手段** | **`environment.systemPackages` 是首选** | ❌ **顺序相反** |
| — | 原子更新 + 回滚 | generations（**粒度更细**） | ✅ 更强 |
| — | Secure Boot 出厂支持 | 需 lanzaboote（外部 flake） | ⚠️ 50% |
| — | Gaming Mode | `programs.steam.gamescopeSession` | ⚠️ 60% |
| — | Waydroid | `virtualisation.waydroid` | ✅ 等价 |
| — | 掌机工具链 | 零件在 nixpkgs，接线自己做 | ⚠️ 60% |

> **哲学差异（一句话）**：Bazzite = **镜像只读 → 应用外挂**；NixOS = **声明式中心化 → 应用进 nixpkgs**。**两条哲学是镜像对称的，照抄层级顺序会得到最糟结果。**

### 14.3 高价值发现（源码级核实，`nixos-26.05`）

| 发现 | 证据 |
|---|---|
| **NixOS 默认内核已编入 `ANDROID_BINDER_IPC` / `ANDROID_BINDERFS`（`tristate = "y"`）** → **装 Waydroid 不需要自定义内核**（推翻社区流传的过时说法） | `pkgs/os-specific/linux/kernel/common-config.nix:1447-1457` |
| `pkgs.inputplumber` **v0.77.1**（`ShadowBlip/InputPlumber`）在 nixpkgs | `pkgs/by-name/in/inputplumber/package.nix` |
| `pkgs.powerstation` 在 nixpkgs（*"Open source TDP control and performance daemon with DBus interface"*） | `pkgs/by-name/po/powerstation/package.nix` |
| `pkgs.bazaar` 在 nixpkgs（*"FlatHub-first app store for GNOME"*）→ **Bazzite 的图形应用商店可直接装** | `pkgs/by-name/ba/bazaar/package.nix` |
| `pkgs.distrobox` = **1.8.2.5**，与 Bazzite 镜像里的 `Distrobox 1.8.2.5-1` **完全同版本** | `pkgs/by-name/di/distrobox/package.nix` |
| **`pkgs.nh` = 4.4.2**，且有**官方 NixOS 模块** `programs.nh`（`enable` / `package` / `flake` / `clean.{enable,dates,extraArgs}`） | `nixos/modules/programs/nh.nix` |
| `programs.steam.gamescopeSession` 默认 `steamArgs = [ "-tenfoot" "-pipewire-dmabuf" ]`，并 mkDefault `programs.gamescope.enable` | `nixos/modules/programs/steam.nix` |
| `virtualisation.waydroid` 自动开 LXC、写 `psi=1`、信任 `waydroid0`、按 nftables 自动选 `waydroid-nftables` | `nixos/modules/virtualisation/waydroid.nix` |
| **`services.flatpak` 只有 `enable` + `package`**；含断言 `xdg.portal.enable == true`（证明 `remotes` 不存在） | `nixos/modules/services/desktops/flatpak.nix` |
| `system.autoUpgrade.operation` 的 enum **只有 `switch` / `boot`**；`dates` 默认 `"04:40"`；`allowReboot` 默认 `false` | `nixos/modules/tasks/auto-upgrade.nix` |
| `pkgs.decky-loader` / `pkgs.lanzaboote` = **404**；lanzaboote 上游最新 **v1.2.0**（2026-09-26） | by-name 探测 + GitHub API |

### 14.4 `nh` ↔ `ujust` 对照（NixOS 上最接近 `ujust` 的东西）

`ujust` 动词体系：`install-` / `get-` / `setup-` / `configure-` / `toggle-` / `fix-` / `distrobox-` / 裸动词（recipe 在 `/usr/share/ublue-os/just`）。

`nh` 能力（官方文档核实）：`nh os switch|boot|test` / `nh home switch` / `nh darwin` / `nh search packages|options|offline|prs|issues` / `nh clean`（含 gcroots 清理）+ 代际 inspect/rollback + `nom` 构建树 + `dix` 变更 diff。

> **`nh` 对 ADHD 友好的点**：`nh os switch` 会在切换前把「哪些包变了」列出来让你确认，比 `nixos-rebuild switch` 一按就切安全得多。

### 14.5 四个反模式（照抄 Bazzite 会踩）

| # | 反模式 | 正确做法 |
|---|---|---|
| 1 | 照抄「Flatpak 优先」 | NixOS 上会把系统拆两半（主题/字体/**中文输入法**都要额外打通）→ **Nix 优先，Flatpak 兜底** |
| 2 | 照抄「`rpm-ostree` 分层是最后手段」 | NixOS 里**命令式的 `nix profile install` 才是最后手段**；声明式的 `systemPackages` / `home.packages` 都是首选 |
| 3 | 照抄「rebase 换镜像很随意」 | NixOS 换 nixpkgs 输入会**触发重建**（§22.2 的 666 个 derivation）。Bazzite 的 rebase 是**下载**，NixOS 换源可能是**编译几小时** |
| 4 | 照抄「brew 装 CLI」 | NixOS 上 `brew` 是外来户（需 FHS + 自管 PATH）→ 用 `home.packages` / `nix shell` |

### 14.6 Bazzite 复刻不了的 20%（且不该复刻）

| 项 | 为什么 |
|---|---|
| **Bazzite Portal（GUI 勾选门户）** | 与「配置即代码」哲学冲突。**NixOS 的替代品是 agent** —— 「用自然语言勾选」才是 NixOS 的原生 Portal |
| **开箱即用整机体验** | Bazzite 的价值在「把几十个开源组件针对几十种机型调好」，这是**人力**不是**技术** |
| **出厂 Secure Boot** | 需 lanzaboote + 自管密钥 + 进 BIOS 清 key。**桌面游戏机威胁模型下收益接近 0，建议跳过** |

**详版**：`nixos-amd-guide.md` 第二十三章（17 节）+ 附录 B.13。

## 15. 第六轮（v1.7）：openSUSE Aeon 模式 —— 稳定基座 + 最新应用（第二十四章）

> 用户问：「要做到类似 openSUSE Aeon，基座是稳定，但 apps 是最新的，如何做」

### 15.1 ★ 前提修正：Aeon 的基座**不是**冻结版本，是滚动的 Tumbleweed

LWN 一手技术分析原文（`[媒体·一手]` <https://lwn.net/Articles/927373/>）：

> *"with a **minimal openSUSE Tumbleweed** as the base operating system and applications running as Flatpaks or in containers"*
> *"Its biggest benefit is **availability of the newest software releases without sacrificing system stability**."*

**「稳定基座」有两种完全不同的实现方式：**

| 实现方式 | 代表 | 「稳定」的来源 | 基座版本 |
|---|---|---|---|
| **冻结版本集** | Debian stable / RHEL / **NixOS 26.05** | 版本不变 → 行为不变 | 固定 |
| **原子 + 极简 + 隔离** | **Aeon** / MicroOS / Silverblue / **NixOS** | 变了能整批回滚，且坏不到基座 | 滚动 |

> **NixOS 两种都能给。** 这是本章最重要的结论 —— 所以「稳定基座 + 最新应用」在 NixOS 上有**三条**路，Aeon 只有一条。

### 15.2 Aeon 技术栈（LWN 一手原文）

| 层 | 做法 | 原文关键句 |
|---|---|---|
| 基座 | minimal **Tumbleweed**，Btrfs root **boot 后只读** | *"mounted read-only after boot"* |
| 更新 | systemd timer **每天** `transactional-update`（zypper 包装）→ 新建 snapshot → 标记下次启动 | *"System updates are done automatically every day"* |
| 失败 | 丢弃 snapshot；**启动检测到问题自动回滚**；手动 `transactional-update rollback` | *"it automatically rolls back"* |
| GUI 应用 | **全部 Flatpak** 在 `~/.local/share/flatpak`，自动更新；GNOME Software **只装 Flathub** | *"it's configured to **only** install Flatpaks from Flathub"* |
| CLI/开发 | **Distrobox**（Tumbleweed 容器，>75,000 RPM）；`distrobox-export` 导出到菜单 | — |
| 兜底装包 | `transactional-update` 装 RPM —— **只给驱动/内核模块/VPN 客户端** | *"every extra package in the host incurs extra risk of instability"* |
| 防火墙 | 默认**没有**（by design，与容器运行时冲突） | — |

### 15.3 三条路（核心表）

| 维度 | 路 A：Aeon 式 | 路 B：双 nixpkgs | 路 C：混合（**推荐**） |
|---|---|---|---|
| 基座 | 26.05 极简 | 26.05 | 26.05 |
| GUI 应用 | **Flatpak** | **nixpkgs-unstable** | 按需 |
| CLI/开发 | **Distrobox** | HM + unstable | HM + unstable |
| 系统级滚动组件 | 不动 | unstable | **只取 mesa** |
| 应用进配置 | ❌ | ✅ | ⚠️ 部分 |
| 构建成本 | **零** | 中 | 低 |
| 可复现 | ❌ | ✅ | ⚠️ |
| 主题/字体/**输入法** | ❌ 要额外打通（§7） | ✅ 天然一致 | ⚠️ 部分 |

### 15.4 ★ HM 官方 FAQ 的 `pkgsUnstable` 写法（本轮首次取到的一手材料）

Home Manager 官方 FAQ 有专节 *"How do I install packages from Nixpkgs unstable?"*（`home-manager/release-26.05/docs/manual/faq/unstable.md`）。NixOS 模块下的官方写法：

```nix
# flake.nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixpkgs-unstable";  # ← 注意分支名
  home-manager = {
    url = "github:nix-community/home-manager/release-26.05";
    inputs.nixpkgs.follows = "nixpkgs";
  };
};

# configuration.nix（模块里）
({ config, ... }: {
  home-manager.extraSpecialArgs = {
    pkgsUnstable = import nixpkgs-unstable {
      inherit system;
      config   = config.nixpkgs.config;    # ★★ 官方明确要求
      overlays = config.nixpkgs.overlays;  # ★★ 官方明确要求
    };
    # 若用默认 nixpkgs 配置，官方说可简写：
    # pkgsUnstable = nixpkgs-unstable.legacyPackages.${system};
  };
})

# home.nix
{ pkgs, pkgsUnstable, ... }: {
  home.packages = with pkgsUnstable; [ firefox chromium vscode ];
}
```

**为什么那两行必须写**：不传 `config` → 基座开了 `allowUnfree` 但 `pkgsUnstable.vscode` 会**求值失败**；不传 `overlays` → 基座的 overlay 在 unstable 里不存在。

### 15.5 让**整个 HM** 用 unstable：`pkgsPath` 覆盖（源码级）

HM 内部（`modules/modules.nix:119`）：
```nix
_module.args.pkgsPath = lib.mkDefault (
  if lib.versionAtLeast config.home.stateVersion "20.09" then pkgs.path else <nixpkgs>
);
_module.args.pkgs = lib.mkDefault pkgs;
```

**是 `mkDefault` → 可覆盖**：
```nix
home-manager = {
  useGlobalPkgs = false;   # ★ 必须关（否则 nixpkgs.* 被禁用）
  sharedModules = [ { _module.args.pkgsPath = inputs.nixpkgs-unstable.outPath; } ];
  users.<你> = { pkgs, ... }: { home.packages = with pkgs; [ firefox ]; };
};
```

**代价**：`useGlobalPkgs = false` 时 HM 会**自己 `import pkgsPath (...)`**（`nixpkgs.nix:58`）→ 多一次 nixpkgs 求值；且 HM 的包与系统的包**哈希不同、无法共享**（同一 Firefox build 两份）。

**`useGlobalPkgs = true` 的硬约束**（`nixpkgs-disabled.nix`）：`nixpkgs.config` / `nixpkgs.overlays` **被禁用**，有断言 + warning：*"`nixpkgs` options are disabled when `home-manager.useGlobalPkgs` is enabled."*

### 15.6 Aeon ↔ NixOS 更新/回滚对照

| Aeon | NixOS | 备注 |
|---|---|---|
| 每天自动 `transactional-update` | `system.autoUpgrade` + `dates` | ✅ 等价 |
| 更新不影响运行中的系统，重启生效 | `operation = "boot"` | ✅ 等价（enum 只有 `switch`/`boot`） |
| 启动失败**自动**回滚 | 手动选旧 generation | ❌ **NixOS 唯一明显不如 Aeon 的一项** |
| `transactional-update rollback` | `nixos-rebuild switch --rollback` | ✅ 等价 |
| 装包要重建快照 + **重启** | rebuild，**不用重启** | ✅ **NixOS 更强** |
| 整镜像回滚 | 单包 / 整 generation 都能回滚 | ✅ **NixOS 更强** |

### 15.7 基座该留什么（NixOS 判据 ≠ Aeon 判据）

Aeon 的判据是**风险**（*"every extra package in the host incurs extra risk of instability"*）；**NixOS 的判据应该是作用域**：

| 进基座（`environment.systemPackages`） | 不进 |
|---|---|
| 内核/模块/固件、图形驱动、桌面环境本体、显示/网络/音频栈 | GUI 应用、CLI 工具、语言工具链、媒体应用 |
| 必须全局可见的工具（`git`/`curl`/`htop`） | `nix profile install` 装的任何东西 |

**理由**：NixOS 的基座包**不会互相污染**（独立闭包），所以「装一个搞坏另一个」基本不发生。**但基座包越多 → `nix flake update` 重建面越广**（§22.2 的 666 个 derivation）。

### 15.8 四条反模式

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | 以为「稳定基座」= 冻结版本 | 错过「滚动 + 原子回滚」这条路 | 先分清两种「稳定」（§15.1） |
| 2 | 照抄 Aeon「Flatpak 是唯一渠道」 | 失去可复现性 + §7 三个坑 + 换机要手动重装 | Flatpak 是**兜底** |
| 3 | `pkgsUnstable` 不传 `config.nixpkgs.config` | unfree 包**求值直接失败** | 照抄官方 FAQ 那两行 |
| 4 | 改 `pkgsPath` 忘关 `useGlobalPkgs` | 改了没用 + warning | 两者成对出现 |

**详版**：`nixos-amd-guide.md` 第二十四章（10 节）+ 附录 B.14。

## 16. 第七轮（v1.8）：二进位包与依赖问题完整手册（第二十五章）

### 16.1 ★★ 本轮最重要的时效性发现：26.05 `xorg` 包集弃用 + `libX*` → `libx*` 全表改名

**这是唯一一条「不知道就会照着旧教程配错」的事实，且影响网上绝大多数 nix-ld 教程（含 LLM 训练数据）。**

| 证据 | 位置 |
|---|---|
| `xorg` 包集已弃用 | `nixos/doc/manual/release-notes/rl-2605.section.md:235`（2026-01-29）+ `pkgs/top-level/aliases.nix:2361` |
| 全部 `libX*` → `libx*` | `pkgs/top-level/aliases.nix:1178-1207`（2026-02-06） |

| 旧写法（会打弃用警告） | 26.05 新写法 |
|---|---|
| `pkgs.xorg.libX11` | `pkgs.libx11` |
| `pkgs.xorg.libXext` | `pkgs.libxext` |
| `pkgs.xorg.libXrender` | `pkgs.libxrender` |
| `pkgs.xorg.libXi` | `pkgs.libxi` |
| `pkgs.xorg.libXcomposite` | `pkgs.libxcomposite` |
| `pkgs.xorg.libXdamage` | `pkgs.libxdamage` |
| `pkgs.xorg.libXrandr` | `pkgs.libxrandr` |
| `pkgs.xorg.libXcursor` | `pkgs.libxcursor` |
| `pkgs.xorg.libXfixes` | `pkgs.libxfixes` |
| `pkgs.xorg.libXtst` | `pkgs.libxtst` |
| `pkgs.xorg.libXScrnSaver` | `pkgs.libxscrnsaver` |
| `pkgs.xorg.libXxf86vm` | `pkgs.libxxf86vm` |
| `pkgs.xorg.libxcb` | `pkgs.libxcb` |
| `pkgs.xorg.libXau` | `pkgs.libxau` |
| `pkgs.xorg.libXdmcp` | `pkgs.libxdmcp` |
| `pkgs.xorg.libXshmfence` | `pkgs.libxshmfence` |
| `pkgs.xorg.libXfont` | **`pkgs.libxfont_1`**（注意：数字在后，不是 `libxfont1`） |
| `pkgs.xorg.libXfont2` | **`pkgs.libxfont_2`** |

> **旧名仍可用**（`aliases.nix` 保留了映射），但会打弃用警告，**未来版本会移除**。

### 16.2 「二进位包」的 6 种来源 × 「依赖问题」的 6 类根因

**来源**（决定用哪种方案）：① nixpkgs 里就有 ② 官方预编译二进制 ③ 第三方包管理器下载的（npm/pip） ④ AppImage ⑤ 安装器/归档（`.run`/`.deb`/`.rpm`/`.tar.gz`） ⑥ 容器镜像/跨架构

**根因**（决定能不能修）：

| # | 根因 | 报错 | 能修吗 |
|---|---|---|---|
| 1 | 动态链接器路径写死 | `No such file or directory`（其实缺 `/lib64/ld-linux-x86-64.so.2`） | ✅ 容易（nix-ld） |
| 2 | 共享库缺失 | `cannot open shared object file: libfoo.so.1` | ✅ 容易（nix-ld + libraries） |
| 3 | 文件系统布局假设 | 找不到 `/usr/share/xxx`、`/opt/xxx` | ✅ 中等（FHS env） |
| 4 | **glibc 版本不匹配** | `version 'GLIBC_2.38' not found` | ⚠️ 难（FHS env / 容器） |
| 5 | 运行时外部命令 / shebang | `bad interpreter`、`python3: command not found` | ✅ 容易（wrapProgram） |
| 6 | 内核接口 / setuid / 驱动 | `modprobe: module not found` | ❌ **不能这么修** |

> **第 1、2 类占 90%，`programs.nix-ld` 一条配置解决。** 判别：`cannot open shared object file`（好办）vs `version 'GLIBC_2.xx' not found`（难办）。

### 16.3 NixOS 为什么会有这个问题的机制根源（源码级）

| 事实 | 证据文件 |
|---|---|
| **NixOS 用 `systemd.tmpfiles.rules` 的 `r` 规则（删除）主动删掉 `/lib64/ld-linux-x86-64.so.2`** —— 不是「本来就没有」 | `nixos/modules/config/ldso.nix` |
| `programs.nix-ld` 启用后把该路径换成 **`L+` 符号链接** 指向 nix-ld 的 loader；导出 `NIX_LD` + `NIX_LD_LIBRARY_PATH` | `nixos/modules/programs/nix-ld.nix` |
| **`programs.nix-ld` 模块自带 14 个基础库**（不是「默认空」）：`zlib` `zstd` `stdenv.cc.cc` `curl` `openssl` `attr` `libssh` `bzip2` `libxml2` `acl` `libsodium` `util-linux` `xz` `systemd` | 同上 |
| **`programs.nix-ld` 不影响系统自带程序** —— nixpkgs 构建的 ELF 里硬编码了 store 里的 loader 绝对路径，不经过该符号链接 | 机制推断（nix-ld README） |
| **nixpkgs 的 python / node 不走 nix-ld**（已指向 store 里的 glibc）→ pip/npm 原生模块失败时开 nix-ld **没用**，要用官方 wrapper | nix-ld 官方 README |
| nix-ld **不支持非 NixOS**，**只支持 x86_64 / aarch64** | 同上 |

### 16.4 14 种方案按「侵入性」排序（从低到高）

| # | 方案 | 适用 | 侵入性 |
|---|---|---|---|
| 1 | **直接用 nixpkgs 版** | 有的话永远首选 | 无 |
| 2 | `nix shell` / `nix run` 临时 | 试一下 | 无 |
| 3 | **`programs.nix-ld`** | 第 1、2 类根因（90%） | 极低 |
| 4 | `programs.nix-ld.libraries = [...]` | 补缺库 | 极低 |
| 5 | **`programs.appimage`** | AppImage | 低 |
| 6 | `pkgs.patchelf` 改二进制 | 单文件、可改 | 低（但破坏签名） |
| 7 | `autoPatchelfHook` | 打包成 derivation | 中 |
| 8 | `wrapProgram` / `makeWrapper` | 缺外部命令、shebang | 中 |
| 9 | **`pkgs.buildFHSEnv`**（= `buildFHSEnvBubblewrap`） | 第 3、4 类根因 | 中高 |
| 10 | **`steam-run ./binary`** | 借 Steam 的 FHS 环境 | 低（但依赖 steam） |
| 11 | `pkgs.dpkg` / `rpm` 解包到用户目录 | `.deb` / `.rpm` | 中 |
| 12 | **`nix-alien`**（`nix run github:thiagokokada/nix-alien -- ./myapp`） | 自动诊断 + 生成配置 | 低（**不在 nixpkgs**） |
| 13 | **Distrobox 容器** | 什么都不想管 / glibc 冲突 | 高（但是终极方案） |
| 14 | `boot.binfmt.emulatedSystems` | 跨架构 | 高 |

### 16.5 `buildFHSEnv` 的关键参数（源码核实）

- **`pkgs.buildFHSEnv` = `buildFHSEnvBubblewrap`**（`all-packages.nix:360-362`）；`buildFHSEnvChroot` 已弃用
- 目录布局：`/lib32`（multiPkgs 32 位）+ `/lib64`（multiPkgs + targetPkgs 64 位）+ **`/lib` → `/lib64` 符号链接**
- **永远自动包含**：`glibcLocales` `glibc`（或 `glibc_multi`）`gcc.cc.lib` `bashInteractiveFHS` `coreutils` `less` `shadow` `su` `gawk` `diffutils` `findutils` …
- **`/etc` 从宿主 `--ro-bind` 30 项**：`passwd` `group` `shadow` `hosts` `resolv.conf` `nsswitch.conf` `sudoers` `localtime` `zoneinfo` `machine-id` `os-release` `pam.d` `fonts` `alsa` `ssl/certs` `ca-certificates` `dconf` …
  - → 这解释了**为什么 FHS 环境能读宿主 `/etc/passwd`、能用系统字体、能解析 DNS、能验证 TLS**，也解释了**为什么在里面改字体/证书不生效**
- 参数：`targetPkgs` / `multiPkgs` / `multiArch` / `includeClosures` / `runScript` / `unshare*`（默认全 `false`）/ `privateTmp` / `chdirToPwd`（默认 `true`）/ `dieWithParent`（默认 `true`）/ `extraInstallCommands` / `extraPreBwrapCmds` / `extraBwrapArgs`
- 实现细节：有个**静态编译的 `container-init` shim** 先跑 `ldconfig` 再 `exec` 真 `/init`（防止 `LD_PRELOAD` 与 **fhsenv in fhsenv** 场景崩溃 —— 源码注释明确提到 Steam 包装的游戏）

### 16.6 `programs.appimage` 的关键事实

- 选项只有 **`enable` / `package` / `binfmt`**（**没有 `extraPkgs`**）
- `binfmt` 注册的 magic 是 **`AI\x01` 与 `AI\x02`**（AppImage type 1 / type 2）
- 不注册 binfmt 时用 `appimage-run ./foo.AppImage`

### 16.7 三类「解决不了」的情况（诚实交代）

| 类型 | 为什么不行 | 正确做法 |
|---|---|---|
| **内核模块 / DKMS 驱动** | nix-ld / FHS 都在用户态，**碰不到内核** | `boot.extraModulePackages` / `boot.kernelModules`，或换内核 |
| **需要 setuid 的程序** | Nix store 是只读的、**不能 setuid** | `security.wrappers`（且二进制必须已在 store 里） |
| **glibc 版本硬冲突** | 换 loader 不够，需要**整套配套 glibc** | 容器（Distrobox）—— 别折腾 glibc |

### 16.8 一页速查

| 问题 | 一行答案 |
|---|---|
| `No such file or directory` 但文件存在 | `programs.nix-ld.enable = true;` |
| `libfoo.so.1: cannot open shared object file` | nix-ld + `programs.nix-ld.libraries` |
| 不知道缺哪个库 | `readelf -d ./myapp \| grep NEEDED` / `nix-alien-find-libs ./myapp` |
| 某个 `.so` 属于哪个包 | `nix-locate --top-level libfoo.so.1`（需先 `nix-index` 建库） |
| 自动搞定 | `nix run github:thiagokokada/nix-alien -- ./myapp` |
| AppImage 双击没反应 | `programs.appimage = { enable = true; binfmt = true; };` |
| 硬编码 `/usr/lib` | `pkgs.buildFHSEnv { ... }` |
| 借 Steam 运行时 | `steam-run ./binary` |
| `GLIBC_2.xx not found` | 容器 —— 别折腾 glibc |
| pip 装的原生模块加载不了 | nixpkgs python **不走 nix-ld** → 官方 wrapper 设 `LD_LIBRARY_PATH` |
| 26.05 `pkgs.xorg.libX11` 报弃用 | 改 **`pkgs.libx11`**（§16.1 全表） |
| 内核模块 / setuid | ❌ nix-ld / FHS 都不行 → §16.7 |
| 跨架构 | `boot.binfmt.emulatedSystems = [ "aarch64-linux" ];` |

**详版**：`nixos-amd-guide.md` 第二十五章（11 节）+ 附录 B.15。

## 可复用操作

```bash
# ── 装机后第一步 ──
sudo chown -R $USER:users /etc/nixos && cd /etc/nixos && git init && git add . && git commit -m init

# ── AMD 验证 ──
lspci -k | grep -A3 -i vga          # 期望 Kernel driver in use: amdgpu
nix-shell -p libva-utils --run vainfo
nix-shell -p vulkan-tools --run "vulkaninfo --summary | head -20"

# ── 网卡验证 ──
lspci -k | grep -A3 -i ethernet     # 期望 Kernel driver in use: r8169
lsmod | grep -E "r8168|r8169"

# ── 中文验证 ──
fc-list :lang=zh | head -5
fc-match "sans-serif:lang=zh"
fcitx5-diagnose | head -40

# ── agent 非 root 部署 ──
npm config set prefix ~/.npm-global
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
nix profile install nixpkgs#uv && uv tool install hermes-agent

# ── 用户级服务 ──
systemctl --user daemon-reload && systemctl --user enable --now my-agent
loginctl enable-linger $USER        # 或 users.users.<name>.linger = true

# ── agent 服务化后的权限与自启自查（第二十一、二十二章）──
loginctl show-user hermes | grep Linger           # 必须 Linger=yes，否则 cron 静默不跑
ls -l /run/user/$(id -u hermes)/bus               # 用户总线 socket 必须存在
systemctl show -p MainPID --value hermes-agent    # 系统模块：取 PID
ps -o user= -p $(systemctl show -p MainPID --value hermes-agent)   # ★ 必须不是 root
systemctl cat openclaw-gateway | grep -E '^\s*(User|Group)='       # 手写 unit 必查
nix path-info --json $(readlink -f $(which hermes) | sed 's|/bin/.*||') | jq -r '.[].version'  # 版本信 Nix 不信 --version

# ── 验证闸门（永远不要跳过）──
sudo nixos-rebuild dry-build
```

**游戏 / 性能诊断**

```bash
ls /sys/kernel/sched_ext && systemctl status scx      # scx 是否可用/在跑
cat /sys/kernel/sched_ext/root/ops                    # 当前生效的调度器
sudo systemctl set-environment SCX_SCHEDULER_OVERRIDE=scx_bpfland && sudo systemctl restart scx
cat /sys/block/nvme0n1/queue/scheduler                # I/O 调度器（方括号=生效）
cat /sys/devices/system/cpu/amd_pstate/status         # active/passive/guided
zcat /proc/config.gz | grep -E "SCHED_CLASS_EXT|NTSYNC|IOSCHED_BFQ|PREEMPT_"
sysctl vm.max_map_count fs.inotify.max_user_watches   # 先看 NixOS 已设什么
```

**语言工具链 / MCP**

```bash
npm config set prefix ~/.npm-global && npm config set cache ~/.npm-cache
npm ls -g --depth=0 && which <pkg>                    # 拿绝对路径写进 MCP 配置
uv tool install <cli>
pkg-config --cflags --libs openssl                     # devShell 内诊断
patchelf --print-interpreter ./binary ; ldd ./binary | grep "not found"
curl -s "http://127.0.0.1:8888/search?q=x&format=json" | jq '.results[:3]'
export PLAYWRIGHT_BROWSERS_PATH="$(nix-build '<nixpkgs>' -A playwright-driver.browsers --no-out-link)"
```

## 坑与反直觉（速查）

1. **`hardware.graphics.enable` 默认 false 且桌面不自动开** —— 漏了它会出现「没有硬件加速」但无报错
2. **写 `videoDrivers = [ "amdgpu" ]` 反而变差** —— 默认 modesetting 才对
3. **`amd_pstate=active` 冗余**、**`r8169.aspm=0` 不存在**、**`thermald` 是 Intel 的** —— 三个流传很广的错误建议
4. **`services.flatpak.remotes` 不存在** —— 大量教程把它当 nixpkgs 内置选项
5. **`gdm.wayland` 已删除** —— 老教程「GNOME 出问题切 X11」在 26.05 失效
6. **fcitx5 不能用 systemPackages 装** —— 会破坏 addon 检测
7. **Wayland 下不要设 `GTK_IM_MODULE`** —— 与 `waylandFrontend = true` 自相矛盾
8. **`noto-fonts-emoji` 不存在** —— 是 `noto-fonts-color-emoji`
9. **`nix.binaryCaches` 在 26.05 会构建失败**
10. **flake 文件不 `git add` 就等于不存在**
11. **`elevator=` 内核参数是死参数** —— 内核自己只打印警告，I/O 调度器只能用 udev/sysfs
12. **NixOS 已把 `vm.max_map_count` 设成 1048576** —— 抄 SteamOS 调优值是多余的
13. **`linux_cachyos` 在 nixpkgs 不存在**；`linux_lqx`/`_libre`/`_hardened`/`-rt` **26.05 已全部删除**
14. **`linux_xanmod`（lts）版本号低于 `linux_xanmod_latest`（main）** —— 命名反直觉
15. **`services.scx` 与 `services.system76-scheduler` 互斥** —— scx 替换了 CFS
16. **`kernel.unprivileged_bpf_disabled = 1` 会让 scx 失效**
17. **`programs.nix-ld.libraries` 默认是空列表** —— 开了不等于能用
18. **`environment.sessionVariables.PATH` 会覆盖系统 PATH** —— 破坏环境
19. **`programs.mangohud` 不是 NixOS 选项**（是 Home Manager 的）
20. **`npx playwright install` 在 NixOS 基本不可用** —— 用 `pkgs.playwright-driver`
21. **SELinux 在 NixOS 没有模块** —— 别找
22. **SearXNG 默认不输出 JSON** —— 必须显式 `formats = [ "html" "json" ]`
23. **`pkgs.nodePackages.*` 26.05 已整体删除** —— 改用顶层属性
24. **`ts-node` 不在 nixpkgs** —— 用 `pkgs.tsx`
25. **`programs.steam` 对 `hardware.graphics.enable` 是硬赋值** —— 你在别处写 `false` 会 option conflict
26. **`pkgs.bore` 不是 BORE 调度器** —— 它是 TCP 隧道工具（`delan/nonymous`，v0.4.1）
27. **`services.ananicy` 的 `package` 与 `rulesProvider` 是两个选项** —— 配错任一个都不会有规则
28. **`systemd.extraConfig` 在 26.05 已删除** —— 用 `systemd.settings.Manager`（写了会直接报错）
29. **`kernel.unprivileged_userns_clone` 主线内核不存在** —— 照抄 CachyOS 的 sysctl 会报错
30. **`linux_zen` 不含 BORE** —— 想靠 zen 拿到 BORE 是错的（BORE 只在 `linux-cachyos`）
31. **`zramSwap.memoryPercent = 100`（CachyOS 的 `zram-size = ram`）会 OOM** —— 用 50–75
32. **`services.irqbalance` / `hardware.ksm` 在桌面上收益接近 0（KSM 还可能为负）** —— 别当免费提升
33. **CachyOS 的 `DefaultTimeoutStartSec=15s` 在 NixOS 上是破坏性的** —— 会打断 rebuild/激活
34. **`services.scx` 内核不支持时静默跳过** —— 必须 `cat /sys/kernel/sched_ext/root/ops` 自己验
35. **`pkgs.unstable` 不存在** —— 一个 NixOS 配置的 `pkgs` 只来自一个 nixpkgs 实例。但**「两套 nixpkgs 并存」不必有 flake**：channel / `fetchTarball` / `fetchGit`+`rev` 都能做到（v1.5 修正）
36. **第三方 flake 的 `nixpkgs` input 不 `follows` 你 = 装两套 glibc** —— HM input 不 follow 更糟，两个 HM 会让 `home-manager switch` 直接失败
37. **Hermes 官方明说 Nix/NixOS 是 Tier 2** —— *"Commits to `main` may break these packages at any point in time"*。要稳就走 Docker 或 FHS
38. **`pkgs.openclaw` 带 `knownVulnerabilities`** —— 安装要在 `permittedInsecurePackages` 里放行，**且版本号变了字符串要跟着改**（最稳做法：先不写，看报错原文）
39. **`pkgs.openclaw` 的更新受限于人工批准** —— 维护者原话：标 insecure 导致 r-ryantm 自动更新卡死（Discourse #76940）。要最新版别依赖它
40. **OpenClaw 官方不接受 PR、Issue 不监控** —— 唯一支持渠道是 Discord `#golden-path-deployments`
41. **Hermes 的 flake 没有二进制缓存** —— 每次 bump nixpkgs 要本地**编译 ~666 个 derivation**（`#130870`）；8 GB 内存不够，OOM killer 会杀掉 `nix-daemon`
42. **`sourcePreference = "wheel"` 救不了构建量** —— uv2nix 仍要为每个 wheel 生成 derivation，且结果不被缓存
43. **NixOS 上 Hermes 的工具闭包永远"不同步"** —— `check_runtime()` 每次刷屏警告 ffmpeg/node/npm；`hermes pm install` 因 **stub-ld** 必然失败（`#134249`）。`programs.nix-ld` 修不了它（PM 不走那个垫片）
44. **无 `linger` → Hermes 的 cron 静默全不跑** —— 走 `systemd-run --user --scope`，fail closed 且不报错。`loginctl show-user hermes | grep Linger` 自查
45. **`linger = lib.mkDefault` 会被你自己的用户声明压掉** —— 用 `createUser = false` 时务必自己写 `linger = true`
46. **手写系统 unit 漏 `User=` → agent 以 root 跑** —— OpenClaw 官方原文：*"unsafe and unsupported for this setup"*。`systemctl show -p MainPID` + `ps -o user=` 自查
47. **NixOS 系统模块下改配置必须 root** —— Hermes 的 `/var/lib/hermes` 是 `0750 hermes:hermes`（连 `ls` 都 permission denied）；OpenClaw 的 `configPath` **有硬断言必须 `/etc/` 下**（`0755 root root`）
48. **HM 模块下不需要 root，但 agent 也改不了配置** —— `HERMES_MANAGED` / `OPENCLAW_NIX_MODE=1` 会主动拦 CLI 写入
49. **Hermes 的 container 模式与 `backend.mode` 互斥**（硬断言）—— 容器跑 gateway only，桌面/面板后端不能同时用
50. **container 的 writable layer 会丢** —— 改 `image` / `extraVolumes` / `extraOptions` 触发容器重建，`apt`/`pip`/`npm` 装的全没（`/data` 与 `/home/hermes` 保留）
51. **Podman 用户跑 container 模式要额外配免密 sudo** —— Docker 用户不需要
52. **`hermes --version` 会骗你** —— 报旧版本日期（`#135217`）或 `0.0.0`。判断版本信 `nix path-info`，别信 `--version`
53. **第三方 `nix-hermes-agent` 的选项名是 `config` 不是 `settings`** —— 配置文件也叫 `cli-config.yaml`。两个项目的例子**不能互相抄**
54. **`pkgs.openclaw` 有三个同实现的二进制** —— `openclaw` / `moltbot` / `clawdbot`（后两个是软链）。老教程写 `clawdbot` 不是错
55. **「NixOS 装 Waydroid 必须自定义内核」是过时说法** —— `common-config.nix` 里 `ANDROID_BINDER_IPC` / `ANDROID_BINDERFS` 都是 `tristate = "y"`（编进内核），**默认内核直接满足模块断言**
56. **`services.flatpak` 只有 `enable` + `package`** —— 网上写的 `services.flatpak.remotes` / `uninstallUnmanaged` **在 26.05 不存在**（源码全文核实）。加 Flathub 要自己 `flatpak remote-add`
57. **`services.flatpak` 有硬断言** —— 不开 `xdg.portal.enable` 会**直接求值失败**，不是警告
58. **`programs.nh.clean.enable` 与 `nix.gc.automatic` 互斥** —— 两个都开会有 warning 且互相抢锁
59. **Bazzite 的层级顺序在 NixOS 上是反的** —— 「Flatpak 优先」「rpm-ostree 是最后手段」两条都**不能照抄**。NixOS 里 Nix 优先、`environment.systemPackages` 是首选，**命令式的 `nix profile install` 才是最后手段**
60. **别把「Bazzite 能随意 rebase」的习惯带到 NixOS** —— Bazzite rebase = 下载镜像；NixOS 换 nixpkgs 输入 = 可能**本地编译几百个包**
61. **`pkgs.decky-loader` / `pkgs.hhd` 不在 nixpkgs**（404）—— 想要 Bazzite 的完整掌机体验，这两块**无解**
62. **`inputplumber` / `powerstation` / `bazaar` 都在 nixpkgs** —— 但「有零件」≠「有体验」，Bazzite 的护城河是**机型适配接线**，不是组件本身
63. **Aeon 的基座是滚动的 Tumbleweed，不是冻结版本** —— 它的「稳定」来自**原子 + 极简 + 隔离**，不是版本冻结。**误以为「稳定 = 冻结」会漏掉 NixOS 的「滚动 + 原子回滚」这条路**
64. **`pkgsUnstable` 必须传 `config.nixpkgs.config` 和 `overlays`** —— 否则基座开了 `allowUnfree` 而 unstable 那份没开，`pkgsUnstable.vscode` 会**求值失败**（HM 官方 FAQ 明确要求这两行）
65. **`home-manager.useGlobalPkgs = true` 时 `nixpkgs.*` 选项被禁用** —— 有断言 + warning：*"`nixpkgs` options are disabled when `home-manager.useGlobalPkgs` is enabled."* **改 `pkgsPath` 必须同时关掉它，否则改了没用**
66. **`useGlobalPkgs = false` 会让 HM 自己 import 一份 nixpkgs** —— 多一次求值，且 HM 的包与系统包**哈希不同、无法共享**（同一 Firefox 会被 build 两份）
67. **Aeon 有「启动失败自动回滚」，NixOS 没有开箱实现** —— NixOS 要在启动菜单手动选旧 generation。这是本文档找到的**唯一 NixOS 明显不如 Aeon 的一项**
68. **NixOS 的 `switch` 不需要重启，Aeon 的 `transactional-update` 需要** —— 所以 NixOS 能做到「Aeon 式原子性 + 不重启」
69. **★★ 26.05 的 `xorg` 包集已弃用，`libX*` 全部改名 `libx*`** —— `pkgs.xorg.libX11` 现在会打弃用警告。**网上所有 nix-ld 教程（含大量 LLM 训练数据）用的都是旧写法**。全表见 §16.1
70. **`libXfont` → `libxfont_1`、`libXfont2` → `libxfont_2`**（**数字在下划线后面**）—— 按 `libxfont1` / `libxfont2` 写会找不到
71. **NixOS 是「主动删除」`/lib64/ld-linux-x86-64.so.2`** —— 用 `systemd.tmpfiles.rules` 的 **`r` 规则**（`config/ldso.nix`），不是「本来就没有」。**这解释了为什么报错是 `No such file or directory` 而不是「找不到库」**
72. **`programs.nix-ld.libraries` 默认不是空** —— 模块自带 **14 个基础库**（zlib/zstd/stdenv.cc.cc/curl/openssl/attr/libssh/bzip2/libxml2/acl/libsodium/util-linux/xz/systemd）。**「默认空」是误读**
73. **nixpkgs 的 python / node 不走 nix-ld** —— 它们已指向 store 里的 glibc。**pip / npm 装的原生模块加载失败时，开 nix-ld 没用**，要用官方 wrapper 设 `LD_LIBRARY_PATH`
74. **`buildFHSEnv` 的 `/etc` 是从宿主 `--ro-bind` 进来的（30 项）** —— 所以 FHS 环境能读宿主 `/etc/passwd`、用系统字体、解析 DNS、验证 TLS；**也所以在里面改字体/证书不生效**
75. **`pkgs.buildFHSEnv` = `buildFHSEnvBubblewrap`** —— `buildFHSEnvChroot` 已弃用。**不是 chroot，是 bubblewrap 沙箱**
76. **`programs.appimage` 只有 `enable` / `package` / `binfmt` 三个选项** —— **没有 `extraPkgs`**（网上有教程这么写）。binfmt 注册的 magic 是 `AI\x01` / `AI\x02`
77. **nix-ld 修不了内核模块和 setuid 程序** —— 前者在用户态够不到内核（用 `boot.extraModulePackages`），后者 Nix store 是只读的不能 setuid（用 `security.wrappers`，且二进制必须已在 store 里）
78. **`GLIBC_2.xx not found` 不要试图用 nix-ld / FHS 修** —— 换 loader 不够，需要整套配套 glibc。**唯一现实解是容器（Distrobox）**

## 未核实 / 存疑

| 项 | 状态 |
|---|---|
| ~~Hermes Agent 的 NixOS 模块确切选项名~~ | ✅ **第三轮已解决**：模块名 **`services.hermes-agent`**（不是 `services.hermes`），选项表见正文 §21.8 与附录 B.11.4 |
| ~~OpenClaw 的完整 CLI / skills 目录结构~~ | ⚠️ **部分解决**：配置文件确为 `openclaw.json`；nixpkgs **无** `services.openclaw` 模块；skills 由 activation 复制到 per-instance runtime 目录并加进 `skills.load.extraDirs`，**但绝对路径未逐字确认** |
| Hermes flake 的**首次安装**实际构建量（非 update 后） | 未核实（只有 update 后 ~666 的数字） |
| ~666 这个数字在 16 核 / 32 GB 机器上的耗时 | 未核实（报告来自 4 vCPU / 8 GB） |
| `programs.nix-ld` 能否修 Hermes 的 stub-ld 问题 | ❌ **推断为不能**（PM 不走 nix-ld 垫片），**未实测验证** |
| OpenClaw `runtimePlugins` 的完整可选值 | 未核实（只知 `discord` / `copilot`） |
| Hermes HM 模块与 NixOS 模块**同时导入**的行为 | 未核实（不建议同时用） |
| `0xrsydn/nix-hermes-agent` 是否真的无 linger | 核实·源码（限定 2026-10-11 那版），用前请自己 `grep -n linger` 复验 |
| Discord `#golden-path-deployments` 里的实际内容 | 未找到（Discord 无法 HTTP 抓取） |
| OpenClaw HM 路的 `openclaw.json` 是否真为符号链接 | 核实·源码（依据 activation 里的 `ln -sfn`），未真机 `ls -l` 确认 |
| `amdgpu.dcdebugmask` / `gpu_recovery` 取值 | 未核实 |
| `services.scx` 对 AMD 游戏的收益 | 未核实（缺一手基准） |
| `scx_lavd` 对 AMD 桌面游戏的实测收益 | 未核实（只知由 Igalia 受 Valve 委托） |
| `scx` 各调度器之间的取舍 | 未核实（上游文档是设计意图，非实测） |
| `WINENTSYNC` / `PROTON_USE_NTSYNC` 变量名 | 社区来源，未从 Proton 官方文档确认 |
| Proton 是否默认启用 ntsync | 未核实 |
| `/dev/ntsync` 设备节点名 | 未核实（udev 规则基于推断） |
| EPP 的 `systemd.tmpfiles` 写法时序 | 部分未核实（可能早于 amd_pstate 初始化） |
| `split_lock_mitigate=0` 的实际收益 | 社区来源，机理明确但未实测 |
| `services.ananicy` 与 `scx` 的交互 | 未核实 |
| `linux_zen` 在 AMD 上是否真优于默认 6.18 | 未核实（编译期差异已核实，体验提升无基准） |
| `mcp-nixos` 之外的 MCP server 覆盖度 | 未核实（只核实了 mcp-nixos 存在） |
| SearXNG MCP server 的确切包名/参数 | 未核实（生态多实现，参数各异） |
| ~~`pkgs.rustup` / `pkgs.pnpm` / `pkgs.yarn` 确切属性路径~~ | ✅ **已解决**：`pkgs.rustup`（`all-packages.nix:4396`）、`pkgs.pnpm` = `pnpm_11`（`:2967`）、**`pkgs.yarn` 就在 by-name**（原记「by-name 404」是错的） |
| ~~`programs.nix-ld.libraries` 的「够用集合」~~ | ✅ **部分解决**：模块自带 14 个基础库（原记「默认空」已修正）；GUI 额外库清单仍按报错逐步补 |
| `hardware.cpu.amd.updateMicrocode` 的收益 | 默认值已核实（false），收益未实测 |
| `LIBVA_DRIVER_NAME=radeonsi` 是否必要 | 未核实（官方未要求，属偏方） |
| **`inputplumber` / `powerstation` 在 NixOS 上是否真能驱动掌机** | 未核实（包存在已源码核实；缺 udev / 服务 / 机型数据库三块接线） |
| `virtualisation.waydroid` 在 AMD 显卡上的图形性能 | 未核实（渲染路径是否用上 AMD GPU 未验证） |
| `waydroid` 与 AppArmor / devices cgroup 的冲突 | 未核实（NixOS 无 SELinux 模块，但严格 AppArmor 策略可能挡 `/dev/binder*`） |
| `programs.steam.gamescopeSession` 的 HDR 在 26.05 是否可用 | 未核实（取决于 gamescope 版本 + Mesa + 显示器，与配置正确性无关） |
| Bazzite 的 `Gamescope 3.16.31` 与 nixpkgs 上游 gamescope 的补丁差异 | 未核实（Bazzite 用自建 spec） |
| `nh search` 的 elasticsearch 端点在**中国大陆**的可达性 | 未核实（走 `search.nixos.org` ES API，未实测是否需代理） |
| `pkgs.bazaar` 在 nixpkgs 的具体版本号 | 未核实（上游同为 `kolunmi/bazaar`，版本未读出） |
| Bazzite 的「90 天镜像保留」是否有书面 SLA | 官方措辞有，**SLA 未核实**（官网是描述现状） |
| `hhd`（Handheld Daemon）是否有 nixpkgs 打包计划 | 未找到 |
| **NixOS 是否有「启动失败自动回滚」实现** | 未核实（Aeon 有，NixOS 需手动；nixpkgs 内未见模块，第三方方案未查） |
| `home-manager.useGlobalPkgs = false` 的实际代价 | 推断（源码：HM 会 `import pkgsPath`；缺内存/时间实测数字） |
| `pkgsUnstable` 不传 `config` 时的具体报错 | 推断（基于 nixpkgs unfree 机制，未实际触发） |
| `_module.args.pkgsPath` 在 HM 用户级覆盖的副作用 | 未核实（`mkDefault` 可覆盖已核实；与 `useUserPackages` 的交互未实测） |
| **Aeon 当前镜像/组件版本** | 未核实（LWN 是 2023-03 的；「3,600 Flatpak」「75,000 RPM」是当时数字） |
| Aeon 是否仍默认不装防火墙 / 仍无 FDE | 媒体·2023（Richard Brown 说法，2026 现状未核实；Aeon 已改用 TIK 安装器） |
| `nixpkgs-unstable` 与 `nixos-unstable` 两分支的差异 | 官方（存在性）+ 未核实（包版本是否逐字相同未实测；HM 官方 FAQ 用前者） |
| 路 C「只滚 mesa」的长期风险 | 未核实（mesa 跨大版本可能与基座内核/`libdrm` 有 ABI 约束，无长期数据） |
| `r8169.aspm=0` 不存在 | 社区来源（内核邮件列表），非正式文档 |
| `r8169` 对 RTL8125 的稳定性 | 社区经验，无权威一手出处 |
| `plasma-login-manager` 是否已取代 SDDM | **来源冲突**：Wiki 说是默认，源码仍是 SDDM → **以源码为准** |
| GNOME 分数缩放 / Flatpak 主题统一 | 无原生声明式方案 |
| 中文输入法在 Flatpak 应用内 | 普遍报告失效，无系统性一手数据 |
| Reddit 社区数据 | **未找到**（`old.reddit.com` 返回 Blocked），已用 NixOS Discourse / Arch BBS / HN 替代 |
| NixOS 的 SELinux 支持路线 | 未找到官方声明 |
| CachyOS 的 `audio-pm-ctl` / `pci-latency` 等价实现 | **未找到**（CachyOS 自研脚本，nixpkgs 无对应包） |
| `kernel.sysrq` 在 NixOS 默认内核的出厂值 | 未核实（取决于内核 Kconfig `MAGIC_SYSRQ_DEFAULT_ENABLE`） |
| NixOS user manager 的 `DefaultLimitNOFILE` 声明式写法 | 未核实（`systemd.settings` 只管 system manager） |
| `systemd.services."user@".serviceConfig.Delegate` 的合并行为 | 未核实（改前先 `systemctl cat user@.service`） |
| CachyOS 是否默认启用 `uksmd` | 未核实 |
| `kyber` vs `none` 在 NVMe 上的实际差异 | 未核实（两者都可用，无一手对比数据） |
| CachyOS 各 scx 调度器的默认选择 | 部分未核实（只知它提供 `scx-scheds`） |
| nixpkgs 中其它 CachyOS 相关包的覆盖度 | 未核实（只逐项核实了 `ananicy-rules-cachyos` 与若干 404） |
| **`programs.nix-ld.libraries` 的「万能起步集」覆盖度** | 经验值（按类别拼的集合，非官方；无「跑 N 个程序成功 M 个」的统计） |
| **nix-ld 的 `NIX_LD_LIBRARY_PATH` 边界** | 官方（机制）+ 未核实（「程序内部再 exec 子进程」「setuid 程序」两类边界未实测） |
| **`buildFHSEnv` 的 `/etc` 30 项绑定是否会变** | 核实·源码（2026-10 快照）+ 未核实（上游可能增删，使用前 `grep -n ro-bind` 复验） |
| **`xorg` 包集别名会保留到哪个版本** | 未核实（`aliases.nix` 保留映射，但**未标注移除时间表**） |
| **`libX*` → `libx*` 改名对下游包的影响** | 未核实（别名层做了兼容，用户手写旧名会警告；**长期是否硬失败未确认**） |
| **AppImage type 3 是否可用** | 核实·源码（只注册 `AI\x01`/`AI\x02`）+ 未核实（type 3 未确认） |
| **nix-alien 在 26.05 的可用性** | 未核实（是否已适配 `xorg` 改名未验证） |
| **`steam-run` 对非游戏二进制的边界** | 官方（机制）+ 未核实（Steam FHS 带游戏向库，对非游戏程序是否有副作用未实测） |
| **`nix-locate` 数据库的体积与建库耗时** | 未核实（首次约几分钟、数百 MB 是估计） |
| **`dpkg`/`rpm` 解包 `.deb`/`.rpm` 的完整流程** | 推断（逻辑成立，未端到端实测真实 `.deb`） |
| **`boot.binfmt.emulatedSystems` 的性能代价** | 官方（机制）+ 未核实（倍率未测；需要 JIT 的程序可能直接不工作） |
| **`programs.nix-ld` 与 `programs.appimage` 同时开启是否冲突** | 未核实（机制不同，理论不冲突，未实测共存） |

## 出处（主要）

- **NixOS Wiki · AMD GPU**：https://wiki.nixos.org/wiki/AMD_GPU
- **NixOS Wiki · Fcitx5**：https://wiki.nixos.org/wiki/Fcitx5
- **Valve Proton · NTFS 警告**：https://github.com/ValveSoftware/Proton/wiki/Using-a-NTFS-disk-with-Linux-and-Windows
- **`elevator=` 死参数**：https://github.com/torvalds/linux/blob/master/block/elevator.c
- **sched-ext（scx）**：https://github.com/sched-ext/scx
- **Zen 内核**：https://github.com/zen-kernel/zen-kernel
- **XanMod**：https://xanmod.org
- **SearXNG**：https://github.com/searxng/searxng
- **uv**：https://docs.astral.sh/uv/
- **nix-ld**：https://github.com/nix-community/nix-ld
- **sops-nix**：https://github.com/Mic92/sops-nix
- **systemd 沙箱指令**：https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html
- **nixpkgs 源码**（`nixos-26.05`）：`hardware/graphics.nix`、`services/hardware/amdgpu.nix`、`services/hardware/lact.nix`、`services/x11/xserver.nix`、`i18n/input-method/{default,fcitx5}.nix`、`config/fonts/fontconfig.nix`、`config/users-groups.nix`、`config/zram.nix`、`config/sysctl.nix`、`programs/steam.nix`、`programs/gamescope.nix`、`programs/gamemode.nix`、`programs/nix-ld.nix`、`programs/appimage.nix`、`programs/direnv.nix`、`services/scheduling/scx.nix`、`services/networking/searx.nix`、`services/hardware/udev.nix`、`security/{apparmor,audit,auditd}.nix`、`services/security/{clamav,fail2ban}.nix`、`pkgs/top-level/linux-kernels.nix`、`pkgs/os-specific/linux/kernel/{common-config,zen-kernels,xanmod-kernels}.nix`、`pkgs/os-specific/linux/scx/`、`pkgs/development/web/playwright/driver.nix`、`pkgs/os-specific/linux/{r8168,r8125}`、`doc/release-notes/rl-2605.section.md`
- **镜像**：https://mirrors.ustc.edu.cn/help/nix-channels.html · https://mirrors.tuna.tsinghua.edu.cn/help/nix-channels/
- **MCP**：https://github.com/utensils/mcp-nixos

**CachyOS 对照（第十八章，全部一手）**

- **CachyOS-Settings**（§18.4–18.7 逐行翻译的原始文件）：https://github.com/CachyOS/CachyOS-Settings
  - `usr/lib/sysctl.d/70-cachyos-settings.conf`、`usr/lib/udev/rules.d/{20-audio-pm,30-zram,40-hpet-permissions,50-sata,60-ioschedulers,69-hdparm,71-nvidia,85-iw-regulatory,99-cpu-dma-latency}.rules`、`usr/lib/modprobe.d/{amdgpu,blacklist,nvidia}.conf`、`usr/lib/modules-load.d/ntsync.conf`、`usr/lib/systemd/zram-generator.conf`、`usr/lib/tmpfiles.d/{thp,thp-shrinker}.conf`、`usr/lib/systemd/{system,user}.conf.d/10-limits.conf`、`etc/security/limits.d/20-audio.conf`
- **CachyOS 官方 ananicy 规则仓库**（nixpkgs 已打包为 `pkgs.ananicy-rules-cachyos`）：https://github.com/CachyOS/ananicy-rules
- **CachyOS 内核**（BORE = `CONFIG_SCHED_BORE`；BMQ 与 sched-ext 不兼容）：https://github.com/CachyOS/linux-cachyos
  - 调度器技术说明：https://deepwiki.com/CachyOS/linux-cachyos/3-cpu-schedulers
  - 构建变量 `_cpusched` / `_preempt` / `_HZ_ticks`：`linux-cachyos/PKGBUILD`
- **CachyOS Wiki · sched-ext**：https://wiki.cachyos.org/configuration/sched-ext/
- **zen-kernel `v7.2.9-zen1`**（用于确认它**不含** BORE）：https://github.com/zen-kernel/zen-kernel/tree/v7.2.9-zen1
- **nixpkgs 新增核实项**：`pkgs/by-name/an/ananicy-rules-cachyos/package.nix`、`pkgs/by-name/an/ananicy-cpp/package.nix`、`pkgs/by-name/bo/bore/package.nix`（TCP 隧道）、`nixos/modules/services/misc/ananicy.nix`、`nixos/modules/hardware/ksm.nix`、`nixos/modules/system/boot/systemd/tmpfiles.nix`、`nixos/modules/services/hardware/irqbalance.nix`、`nixos/modules/tasks/cpu-freq.nix`

**Bazzite 对照（第二十三章，全部一手）**

- **Bazzite 官网**（image based / 90 天镜像保留 / Secure by design / 镜像组件版本表）：https://bazzite.gg/
- **Bazzite 文档 · 六层软件层级**（原文）：https://docs.bazzite.gg/Installing_and_Managing_Software/software-intro/
- **Bazzite 文档 · `ujust` 动词体系**：https://docs.bazzite.gg/Installing_and_Managing_Software/ujust/
- **Bazzite 文档 · 应用管理索引**：https://docs.bazzite.gg/Installing_and_Managing_Software/
- **`nh` 官方文档**（子命令全集 / 官方 NixOS 模块）：https://github.com/nix-community/nh/blob/master/docs/README.md
- **lanzaboote**（Secure Boot，最新 v1.2.0）：https://github.com/nix-community/lanzaboote
- **nixpkgs 新增核实项（第五轮）**：`nixos/modules/programs/nh.nix`、`pkgs/by-name/nh/{nh,nh-unwrapped}/package.nix`、`nixos/modules/programs/steam.nix`、`nixos/modules/programs/gamescope.nix`、`nixos/modules/virtualisation/waydroid.nix`、`nixos/modules/services/desktops/flatpak.nix`、`nixos/modules/tasks/auto-upgrade.nix`、`nixos/modules/system/boot/loader/systemd-boot/systemd-boot.nix`、`pkgs/os-specific/linux/kernel/common-config.nix:1447-1457`（binder）、`pkgs/by-name/{di/distrobox,in/inputplumber,po/powerstation,ba/bazaar,um/umu-launcher}/package.nix`

- 完整逐条出处见交付物 `nixos-amd-guide.md` 附录 B（含 B.9 CachyOS 对照专节 · B.13 Bazzite 对照专节 · B.14 Aeon 对照专节）

**Aeon / MicroOS Desktop 对照（第二十四章，一手）**

- **LWN · OpenSUSE MicroOS Desktop: a Flatpak-based immutable distribution**（Koen Vervloesem，2023-03-29）：https://lwn.net/Articles/927373/ —— §24.1/§24.2 全部技术细节的**一手来源**（基座是 Tumbleweed、Btrfs 只读、`transactional-update` 机制、Flatpak 在 `~/.local/share/flatpak`、GNOME Software 只装 Flathub、Distrobox >75,000 RPM、*"every extra package in the host incurs extra risk of instability"*、无防火墙 by design）
- **Aeon 官网**：https://aeondesktop.github.io/ （三条卖点原文：Automated Maintenance / Minimal Yet Functional / Flatpak / Distrobox / Transactional Update）
- **FOSS Wiki · Aeon**：https://foss.wiki/Aeon （「Release Model: Rolling」旁证；该站自标 lacks citations，仅作旁证）
- **openSUSE 中文社区 · 更名公告**：https://suse.org.cn/社区新闻/2023/05/27/opensuse-aeon.html
- **⚠️ openSUSE Wiki `Portal:Aeon` 在核实期间数据库故障**（*"Cannot access the database"*），故本章未使用 Wiki

**Home Manager 官方 FAQ 与源码（第六轮新增核实项）**

- **HM 官方 FAQ · How do I install packages from Nixpkgs unstable?**：`home-manager/release-26.05/docs/manual/faq/unstable.md`（§24.5.1 照抄官方骨架）
- `home-manager/release-26.05/nixos/common.nix`（`useGlobalPkgs` / `useUserPackages` / `extraSpecialArgs` / `sharedModules` / `users` / `minimal` 等全部选项）
- `home-manager/release-26.05/modules/misc/nixpkgs.nix:58`（`_pkgs = import pkgsPath (...)`）
- `home-manager/release-26.05/modules/misc/nixpkgs-disabled.nix`（`useGlobalPkgs = true` 时 `nixpkgs.*` 被禁用的断言与 warning）
- `home-manager/release-26.05/modules/modules.nix:119-122`（`pkgsPath` / `pkgs` 的 `mkDefault` 默认值）
- 分支探测：`home-manager/release-26.05`、`nixpkgs/nixpkgs-unstable`、`nixpkgs/nixos-unstable`、`nixpkgs/nixos-26.05` 均存在（HTTP 200）


**nixpkgs 模块源码（第七轮，二进位包与依赖，逐文件核实）**

- `nixos/modules/config/ldso.nix` —— **`environment.ldso` 用 `systemd.tmpfiles.rules` 的 `r` 规则主动删除 `/lib64/ld-linux-x86-64.so.2`**
- `nixos/modules/programs/nix-ld.nix` —— 模块全文；**自带 14 个基础库**（zlib/zstd/stdenv.cc.cc/curl/openssl/attr/libssh/bzip2/libxml2/acl/libsodium/util-linux/xz/systemd）；`L+` 符号链接；导出 `NIX_LD` + `NIX_LD_LIBRARY_PATH`
- `nixos/modules/programs/appimage.nix` —— 选项只有 `enable`/`package`/`binfmt`；binfmt magic `AI\x01`/`AI\x02`
- `pkgs/top-level/all-packages.nix:360-362` —— **`buildFHSEnv = buildFHSEnvBubblewrap`**
- `pkgs/build-support/build-fhsenv-bubblewrap/default.nix` —— 目录布局（`/lib32` + `/lib64` + `/lib`→`/lib64`）、自动包含的基础包、**`/etc` 的 30 项 `--ro-bind`**、`container-init` 静态 shim 的设计理由（源码注释原文）
- `pkgs/build-support/build-fhsenv-common.nix` —— `buildFHSEnv` 全部参数（`targetPkgs`/`multiPkgs`/`multiArch`/`includeClosures`/`runScript`/`unshare*`/`privateTmp`/`chdirToPwd`/`dieWithParent`/`extraInstallCommands`/`extraPreBwrapCmds`/`extraBwrapArgs`）
- `pkgs/games/steam/fhsenv.nix` —— `steam-run` 是 `buildFHSEnv` 的一层包装
- **`nixos/doc/manual/release-notes/rl-2605.section.md:235`** —— **`xorg` 包集弃用公告**（2026-01-29）
- **`pkgs/top-level/aliases.nix:1178-1207`** —— **全部 `libX*` → `libx*` 改名映射**（2026-02-06）
- **`pkgs/top-level/aliases.nix:2361`** —— `xorg` 包集别名条目

**上游项目 README（第七轮）**

- **nix-ld**：https://github.com/Mic92/nix-ld —— 三个 FHS 弱点原文、**nixpkgs python/node 不走 nix-ld**、`pythonld` wrapper 写法、**不支持非 NixOS**、**只支持 x86_64/aarch64**
- **nix-alien**：https://github.com/thiagokokada/nix-alien —— `nix-alien` / `nix-alien-ld` / `nix-alien-find-libs` 三个命令、`-l`/`-p` 参数、dlopen 局限、**不在 nixpkgs**、`follows` 不受支持
- **nix-index**：https://github.com/nix-community/nix-index —— `nix-locate --top-level` 的用法与「需先 `nix-index` 建库」的前置条件

- 完整逐条出处见交付物 `nixos-amd-guide.md` 附录 B（含 **B.15 二进位包与依赖专节**）
