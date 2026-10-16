# CachyOS vs NixOS 26.05 深度对比：结果、原因、以及"纯官方 NixOS 能复现多少"

- **调研日期**：2026-10-16
- **对比对象**：CachyOS vs **NixOS 26.05「Yarara」**（2026-05-30 发布）
- **核心问题**：① 全面比较 ② 结果分析 ③ 差异的原因 ④ 差异为何**不突出** ⑤ **在没有第三方仓库的前提下，NixOS 26.05 能复现 CachyOS 的哪些优化策略？**
- **一句话结论**：**NixOS 是六者中"证据最弱、定位最不同"的一个**——它从不在性能上竞争，卖点是**声明式配置与原子回滚**。但它有个反直觉的发现：**sched-ext 调度器与 NVIDIA 驱动都是官方 nixpkgs 原生支持**（比 Fedora 省事），**唯一真正做不到的是"全仓库 v3 重编译"**——虽然 nixpkgs 在**配置上支持** `x86_64-v3-linux`，但那意味着**几乎全部包都要本地编译**。

---

## 0. 结论速览

| 问题 | 答案 |
|---|---|
| 谁更快？ | **无法确证**——⚠️ **Phoronix 从未做过包含 NixOS 的发行版横评**，本报告结论**全部基于结构性推断** |
| 结构性判断 | NixOS 官方缓存是**通用 x86_64 构建（v1 档）**，与 Arch/Fedora/Ubuntu 同档，落后 CachyOS 的 v3/v4 |
| NixOS 反而更强的地方？ | **sched-ext 官方声明式支持**（`services.scx.enable`）；**NVIDIA 驱动官方 nixpkgs 支持（无需第三方仓库）**；**generations 原子回滚**（比 Btrfs 快照更彻底） |
| 最大短板？ | **官方二进制缓存不提供 CPU 优化构建**；要 v3 必须**全量本地编译**；无 BORE/BMQ 内核；默认 LTS 内核 |
| 差异为何不突出？ | NixOS 的内核可自由切换、scx 官方可用；且它**根本不以性能为卖点**——卖点是可复现性 |
| 纯官方 NixOS 能复现多少？ | **约 13 项可复现**（且多为**声明式一行配置**）；**全仓库 v3 重编译、BORE/BMQ 内核**做不到 |

---

## 1. 全面比较

| 维度 | CachyOS | NixOS 26.05「Yarara」 |
|---|---|---|
| **上游** | Arch Linux（下游再发行） | 独立发行版（NixOS 项目） |
| **发布模型** | 滚动 | **半年一版**（26.05 于 2026-05-30 发布，支持至 **2026-12-31**） |
| **核心理念** | 性能优先 | **声明式配置 + 可复现 + 原子回滚** |
| **配置方式** | 命令式（改 `/etc`、装包） | **声明式（`configuration.nix`，配置即代码）** |
| **指令集基线** | `v3` / `v4` / `znver4` | **通用 `x86_64-linux`（v1 档）**；nixpkgs 另有 `x86_64-v1/v2/v3-linux` system type |
| **二进制缓存** | 自建 v3/v4 仓库 | **cache.nixos.org（通用构建）** |
| **编译优化** | LTO + PGO + BOLT + AutoFDO | 无系统性 PGO/BOLT |
| **内核** | 自研 `linux-cachyos`（BORE/EEVDF/BMQ/RT…） | 默认 **`linuxPackages`（LTS）**；可切 `linuxPackages_latest` 等**任意版本** |
| **调度器** | BORE / BMQ / sched-ext / RT | EEVDF；**sched-ext 官方声明式支持** ✅ |
| **默认文件系统** | Btrfs + 快照 | **ext4**（安装器可配 Btrfs） |
| **回滚机制** | Btrfs 快照 | **generations（原子、声明式，可选启动项）** ✅ |
| **安全默认** | 常规 | 无强制 MAC 默认（可选 AppArmor/SELinux） |
| **NVIDIA 驱动** | 官方仓库预编译模块 | **`services.xserver.videoDrivers = ["nvidia"]`（官方 nixpkgs，需 allowUnfree）** ✅ |
| **游戏工具** | `cachyos-gaming-meta` | `programs.steam.enable`；gamemode / mangohud / lutris 在 nixpkgs |
| **包数量** | Arch + AUR（20 万+） | **nixpkgs 12 万+**（26.05 新增 20442、移除 17532） |
| **本版亮点** | — | **systemd stage 1 成为默认**；GNOME 50；**GCC 15**；LLVM 21；x86_64-darwin 弃用 |
| **贡献规模** | 核心约 9 人 | **2842 名贡献者 / 59703 commits（单版）** |
| **学习曲线** | 中等（Arch 系） | **陡峭（需学 Nix 语言）** |
| **治理** | 社区小团队 | NixOS 基金会 + 正式 RFC 流程 |

**关系本质**：两者**没有血缘关系**，且**目标完全不同**——CachyOS 追求"**开箱最快**"，NixOS 追求"**配置可复现、系统可原子回滚**"。**性能从来不是 NixOS 的竞争维度**，这是理解本对比的前提。

---

## 2. 结果分析

### 2.1 ⚠️ 证据缺口：NixOS 是六者中证据最弱的

| 评测 | 是否含 NixOS |
|---|---|
| Phoronix Ryzen 9 9950X，6 发行版，59 项（2024-08） | ❌ |
| Phoronix Framework Laptop 13 Pro，6 发行版（2026-08） | ❌ |
| Phoronix Razer Blade 18 三系统（2026-07） | ❌ |
| Phoronix HP Dev One，6 发行版（2022-06） | ❌ |
| **Phoronix 全部发行版横评** | **❌ 从未包含 NixOS** |

→ **本报告关于 NixOS 性能的结论全部基于结构性推断，置信度最低。** 请把下面的判断当作"原理推演"，而非"实测排名"。

### 2.2 结构性推断

| 维度 | 判断 | 依据 |
|---|---|---|
| 指令集 | **通用 x86_64（v1 档）**——与 Arch/Fedora/Ubuntu 同档，落后 CachyOS | 官方缓存 `cache.nixos.org` 为通用构建 |
| 编译优化 | 无系统性 PGO/BOLT | nixpkgs 构建策略 |
| 内核 | **默认 LTS**（较旧）；但**可自由切到 latest** | `boot.kernelPackages` |
| 调度器 | **scx 官方声明式可用**——与 Arch/openSUSE 同档，**强于 Fedora 与 Ubuntu** | sched-ext 官方 INSTALL.md |
| 回滚 | **generations 原子回滚**——**强于所有对手** | NixOS 核心机制 |

**综合判断**：NixOS 的**默认性能档位大致与 Arch/Fedora/Ubuntu 同档（v1 档）**，落后 CachyOS 若干个百分点；但它的**内核可自由切换**、**scx 官方可用**，所以**用户有充分手段自行补齐**。它的真正价值在**性能之外的维度**。

---

## 3. 差异的原因

### 3.1 编译层 —— CachyOS 的最大优势，也是 NixOS 的最大结构性劣势

| 项 | NixOS 26.05 | CachyOS | 影响 |
|---|---|---|---|
| 指令集基线 | **通用 `x86_64-linux`（v1）** | `v3`/`v4`/`znver4` | **CPU 密集 2–8%** |
| LTO | 部分包 | 全栈 ThinLTO | 1–3% |
| PGO | 无 | 核心包 + 内核 AutoFDO | 1–4% |
| BOLT | 无 | 核心包 | 1–3% |

> **关键机制**：nixpkgs **原生支持** `x86_64-v1-linux` / `x86_64-v2-linux` / `x86_64-v3-linux` 作为 system type，所以**配置层面你可以启用 v3**。**但官方二进制缓存只提供通用 `x86_64-linux` 构建**——一旦改成 v3，**几乎全部包都要在本地重新编译**（可能数小时到数天），且**无法再从官方缓存下载**。
> **这就是 NixOS 与 CachyOS 的本质差异：CachyOS 提供现成的 v3/v4 二进制仓库，NixOS 提供"能编译 v3 的能力"但不提供现成产物。**

### 3.2 内核层 —— NixOS 有弹性，但默认保守

| 项 | NixOS 26.05 | CachyOS |
|---|---|---|
| 默认内核 | **`linuxPackages`（LTS，较旧）** | 跟随 Arch（较新） |
| 可切换性 | ✅ **任意版本**（`linuxPackages_latest`、`_rt`、`_hardened`…） | ✅ 多种变体 |
| 调度器 | EEVDF + **scx 官方声明式** ✅ | EEVDF 调参 / **BORE** / **BMQ** / RT |
| BORE/BMQ | ❌ 无 | ✅ 内置 |
| Tick rate | 常规 | **1000Hz** |
| AutoFDO | 无 | 有 |

### 3.3 系统/默认配置层 —— NixOS 全部"声明式"

| 项 | NixOS 26.05 | CachyOS |
|---|---|---|
| sysctl | **`boot.kernel.sysctl = { ... }`（声明式）** | `/etc/sysctl.d/`（命令式） |
| 内核参数 | **`boot.kernelParams = [ ... ]`** | 引导器配置 |
| zram | **`zramSwap.enable = true`** | 配置文件 |
| 回滚 | **generations（原子）** ✅ | Btrfs 快照 |
| 文件系统 | ext4 默认 | Btrfs + 快照 |
| 本版变化 | **systemd stage 1 成为默认**（initrd 现代化） | — |

### 3.4 生态层

| 项 | NixOS 26.05 | CachyOS |
|---|---|---|
| **NVIDIA 驱动** | ✅ **官方 nixpkgs（`videoDrivers = ["nvidia"]`，需 allowUnfree）** | 官方仓库预编译模块 |
| 游戏工具 | nixpkgs（`programs.steam.enable`、gamemode、mangohud、lutris） | meta 包一键装 |
| 专有软件 | 官方支持（需 allowUnfree） | AUR | 
| 第三方生态 | **Flakes（nix-gaming、nixos-hardware 等）** | AUR（20 万+） |
| 可复现性 | **★★★★★（配置即代码）** | ★★ |

---

## 4. 差异"没突出"的原因

1. **NixOS 根本不以性能为卖点**：它的核心价值是**声明式、可复现、原子回滚**——性能不在它的竞争清单上。这是"差异不突出"的**最根本原因**。
2. **内核可自由切换**：`boot.kernelPackages = pkgs.linuxPackages_latest` 一行就能拿到与 CachyOS 同代的内核——"内核红利"可自取。
3. **scx 官方可用**：NixOS 在**调度器实验这一层不落后**（比 Fedora、Ubuntu 都强）。
4. **NVIDIA 无需第三方仓库**：比 Fedora（需 RPM Fusion）省事，接近 Arch/CachyOS 的体验。
5. **官方缓存是通用构建**：这是 NixOS 唯一"结构性吃亏"的点，但它是**可复现性的代价**——为了"同一份配置在所有机器上得到同一个系统"，必须用通用二进制。
6. **瓶颈不在 CPU**（Amdahl 定律）：4K 游戏 GPU 受限、桌面受 IO/网络限制。
7. **测量噪声同量级**：run-to-run 方差常有 1–3%。
8. **部分"优化"是取舍**：激进电源档是**用功耗/续航换响应**。

---

## 5. 纯官方 NixOS 26.05 能复现哪些优化策略？

> **前提界定**："第三方仓库"指**第三方 Flake / Cachix 缓存 / 外部 overlay**等。**nixpkgs 官方仓库 + cache.nixos.org 视为官方**。

### 5.1 ✅ 可以复现（13 项，且几乎全是"声明式一行"）

| # | CachyOS 的优化策略 | 纯 NixOS 复现方法（写进 `configuration.nix`） | 来源 |
|---|---|---|---|
| 1 | **可插拔调度器（sched-ext）** | <code>services.scx.enable = true;<br>services.scx.scheduler = "scx_lavd";<br>boot.kernelPackages = pkgs.linuxPackages_latest;</code> | ✅ **官方 nixpkgs**（24.11 起），**声明式**，比 CachyOS 手动切换更规范 |
| 2 | **NVIDIA 驱动** | <code>services.xserver.videoDrivers = [ "nvidia" ];<br>hardware.nvidia.modesetting.enable = true;</code>（需 `nixpkgs.config.allowUnfree = true`） | ✅ **官方 nixpkgs**，**无需第三方仓库** |
| 3 | **游戏工具** | `programs.steam.enable = true;` + `environment.systemPackages = [ pkgs.gamemode pkgs.mangohud pkgs.lutris ];` | 官方 nixpkgs |
| 4 | **CPU 性能档** | `services.power-profiles-daemon.enable = true;`（或 `services.tuned.enable = true;`） | 官方模块 |
| 5 | **全套 sysctl** | `boot.kernel.sysctl = { "vm.swappiness" = 100; "kernel.nmi_watchdog" = 0; ... };` | 官方内核 |
| 6 | **内核启动参数** | `boot.kernelParams = [ "preempt=full" ];` | 官方内核 |
| 7 | **zram + zstd** | `zramSwap.enable = true;` | 官方模块 |
| 8 | **THP defrag** | 通过 `boot.kernel.sysctl` 或 `tmpfiles` | 官方内核 |
| 9 | **I/O 调度器按设备分配** | `services.udev.extraRules = '' ... '';` | 官方内核 |
| 10 | **NTSync** | `boot.kernelModules = [ "ntsync" ];`（Linux 6.14 起主线） | 官方内核 |
| 11 | **EEVDF 调参** | `boot.kernel.sysctl."kernel.sched_base_slice_ns" = 3000000;` | 官方内核 |
| 12 | **快照 / 回滚** | **generations 原子回滚**（`nixos-rebuild --rollback`，或启动菜单选上一代） | ✅ **NixOS 核心机制，强于 Btrfs 快照** |
| 13 | **任意内核版本** | `boot.kernelPackages = pkgs.linuxPackages_latest;`（或 `_rt` / `_hardened`） | 官方 nixpkgs |

> **NixOS 的加分项**：第 1、2、12 项——**sched-ext 与 NVIDIA 都是官方支持**（比 Fedora 省事），**generations 回滚比 Btrfs 快照更彻底**（整个系统状态原子切换，不依赖文件系统）。而且**全部通过配置文件声明**，可版本控制、可复现。

### 5.2 ❌ 无法在纯官方 NixOS 上复现的（8 项）

| # | CachyOS 的优化策略 | 为什么做不到 | 需要什么 |
|---|---|---|---|
| 1 | **现成的全仓库 x86-64-v3 / v4 二进制** | ⚠️ **官方缓存 `cache.nixos.org` 只提供通用 `x86_64-linux`（v1）构建** | **本地全量重编译**（配置上支持，见下注）或第三方 Cachix |
| 2 | **LTO / PGO / BOLT 预编译包** | 无系统性优化构建 | 本地重编译 |
| 3 | **BORE 调度器内核** | nixpkgs 无 BORE（非主线） | 第三方 Flake / 自建内核 |
| 4 | **BMQ 内核** | 同上 | 同上 |
| 5 | **1000Hz + AutoFDO 内核** | 官方内核无这些配置 | 自建内核 |
| 6 | **CachyOS 工具链 / Proton-CachyOS** | 不在 nixpkgs | 第三方 Flake（如 `nix-gaming`） |
| 7 | **ananicy-cpp** | 不在 nixpkgs | 第三方 Flake / overlay |
| 8 | **预编译 NVIDIA 模块（免本地构建）** | 内核非官方标准版本时需本地构建模块 | 用官方缓存内核版本，或本地构建 |

> **⚠️ 关于第 1 条的重要澄清**：**nixpkgs 在配置层面原生支持 `x86_64-v3-linux`**（`nix-env` 会列出 `Additional system types: ... x86_64-v3-linux`），你可以通过 `nixpkgs.hostPlatform` 与 `gcc.arch = "x86-64-v3"` 启用。
> **但官方缓存不提供 v3 产物**——一旦启用，**几乎全部包都要本地编译**，代价是数小时到数天的构建时间 + 磁盘空间。
> **所以准确表述是：NixOS "能编译 v3"，但不"提供现成的 v3 二进制"。** 这与 CachyOS 的现成 v3/v4 仓库是**工程便利性**上的本质差别。

### 5.3 直接回答你的问题

> **NixOS 26.05 在"没有第三方仓库"的前提下，能复现 CachyOS 约 13 项优化**——而且**几乎每一项都是 `configuration.nix` 里的一行声明**，可版本控制、可复现、可原子回滚。
>
> 其中**三项是 NixOS 的相对优势**：
> 1. **sched-ext 调度器**（`services.scx.enable`）——**官方 nixpkgs 原生支持**（比 Fedora 的 COPR、Ubuntu 的源码编译都省事）
> 2. **NVIDIA 驱动**（`videoDrivers = ["nvidia"]`）——**官方 nixpkgs**，无需第三方仓库
> 3. **generations 原子回滚**——比 CachyOS 的 Btrfs 快照更彻底
>
> **唯一真正做不到的是"全仓库 v3/v4 重编译"**：nixpkgs **配置上支持** `x86_64-v3-linux`，但**官方缓存只提供通用构建**，启用 v3 意味着**几乎全部包都要本地编译**。加上 **BORE / BMQ 内核**必须自建——这两项是 CachyOS 在 NixOS 上**无法"官方即用"地复现**的部分。

### 5.4 ★ 六个发行版的"官方仓库能力"总横比（实用速查）

| 能力 | CachyOS | Arch | openSUSE TW | Fedora | Ubuntu 26.04 | **NixOS 26.05** |
|---|---|---|---|---|---|---|
| sched-ext 调度器 | ✅ 内置 | ✅ `scx-scheds` | ✅ `scx` | ❌ 需 COPR | ❌ 需源码编译 | ✅ **`services.scx`（声明式）** |
| 游戏工具 | ✅ meta 包 | ✅ extra | ✅ 官方 | ✅ 官方 | ✅ 官方 | ✅ **nixpkgs** |
| 默认快照/回滚 | ⚠️ 需选择 | ❌ 需自配 | ✅ **默认+GRUB** | ❌ 需自配 | ❌（ZFS 可选） | ✅ **generations 原子回滚** |
| NVIDIA 专有驱动 | ✅ 官方 | ✅ extra | ⚠️ NVIDIA 官方仓库 | ❌ 需 RPM Fusion | ✅ **官方+CUDA** | ✅ **官方 nixpkgs** |
| ZFS 官方支持 | ✅ | ✅ | ❌ | ❌ | ✅ **main 仓库** | ✅（nixpkgs 有） |
| zram 默认启用 | ✅ | ❌ | ❌ | ✅ | ❌ | ❌（但一行可开） |
| **指令集基线** | **v3/v4** | v1 | **v2** | v1 | v1（amd64v3 实验） | **v1（配置可切 v3，但需全量编译）** |
| 内核版本自由度 | 多种变体 | 多种 | 多种 | 较新 | **Linux 7.0** | **任意版本** |
| 可复现性 | ★★ | ★★ | ★★★ | ★★★ | ★★★ | **★★★★★** |

**读数**：
- **NixOS 在"官方仓库能力"上并不弱**——sched-ext、NVIDIA、游戏工具全在官方，**回滚机制是六者中最强的**。它的唯一结构性劣势是**"官方缓存不提供 CPU 优化构建"**。
- **NixOS 与 CachyOS 的对比本质不是"性能之争"，而是"**极致性能 vs 极致可复现**"的取舍。**

---

## 6. 参考来源

- [NixOS 官方博客 — NixOS 26.05 released（2026-05-30，支持至 2026-12-31；systemd stage 1 默认、GNOME 50、GCC 15、2842 贡献者 / 59703 commits）](https://nixos.org/blog/announcements/2026/nixos-2605/)
- [sched-ext/scx — INSTALL.md（NixOS 24.11+ 官方 nixpkgs：`services.scx.enable`；Arch 官方 scx-scheds；openSUSE 官方 scx；Fedora 需 COPR；Ubuntu 需源码编译）](https://github.com/sched-ext/scx/blob/main/INSTALL.md)
- [NixOS/nixpkgs Issue #384035（`nix-env` 输出显示 `Additional system types: x86_64-v1-linux, x86_64-v2-linux, x86_64-v3-linux`）](https://github.com/NixOS/nixpkgs/issues/384035)
- [NixOS/nixpkgs Issue #342989（`services.power-profiles-daemon.enable` 模块）](https://github.com/NixOS/nixpkgs/issues/342989)
- [NixOS/nixpkgs Issue #467814（NVIDIA 内核模块与 kernel 6.18 的构建问题，说明 NVIDIA 由 nixpkgs 提供）](https://github.com/NixOS/nixpkgs/issues/467814)
- [CSDN — NixOS 26.05 "Yarara" 正式发布（版本支持情况）](https://blog.csdn.net/techforward/article/details/161599018)
- [程序员茄子 — NixOS 26.05 "Yarara" 深度实战（`boot.kernelPackages` 默认 LTS / latest）](https://www.chenxutan.com/d/3099.html)
- [NixOS 官方手册 — NixOS 26.05 Release Notes](https://nixos.org/manual/nixos/stable/release-notes)
- [NixOS 官方手册 — Nixpkgs 26.05 Release Notes](https://nixos.org/manual/nixpkgs/stable/release-notes)
- [CSDN — NixOS 硬件支持详解（`services.xserver.videoDrivers = ["nvidia"]`）](https://blog.csdn.net/gitblog_00456/article/details/152106889)
- [USTC Linux 101 — 其他的 Linux 发行版：技术差异简介（NixOS 声明式配置）](https://101.lug.ustc.edu.cn/Appendix/distribution/)
- [Phoronix — Operating Systems 评测列表（**确认：所有发行版横评均未包含 NixOS**）](https://www.phoronix.com/reviews/Operating+Systems)
- [CachyOS 官方 Wiki — Why CachyOS?](https://wiki.cachyos.org/cachyos_basic/why_cachyos)
- [CachyOS 官方 Wiki — Kernel](https://wiki.cachyos.org/features/kernel)
- [CachyOS 官方 Wiki — sched-ext 使用指南](https://wiki.cachyos.org/configuration/sched-ext/)
- [Linux Kernel 文档 — /proc/sys/kernel/](https://www.kernel.org/doc/html/latest/admin-guide/sysctl/kernel.html)

> **来源质量说明**：NixOS 官方博客与官方手册、sched-ext 官方 INSTALL.md、NixOS/nixpkgs 官方 Issue 为一手来源；CSDN、程序员茄子为二手转述。
> **⚠️ 最重要的证据声明**：**Phoronix 从未发布过包含 NixOS 的发行版性能横评**。本报告对 NixOS 的性能判断**全部基于结构性推断**（官方缓存为通用构建、无系统性 PGO/BOLT、默认 LTS 内核），**没有任何同机实测数据支撑**——置信度是六个对比对象中最低的。
