# 游戏性能优化深度比较：NixOS vs Arch Linux vs openSUSE Tumbleweed / Slowroll

**调研日期**：2026-10-12
**方法**：3 个并行研究子代理（每发行版 1 个）+ 主调研员核实跨发行版通用层（内核调度器 / NTSYNC / Wayland HDR）
**证据标注**：`[核实]` = 官方包页/文档/源码直接证据；`[社区]` = 论坛/博客推断；`[宣传]` = 厂商自测，需打折

---

## 0. 结论先行

### 一句话结论

**游戏性能的 90% 不取决于发行版，取决于内核版本、Mesa/NVIDIA 版本、CPU 调度器这三样。** 三个发行版在这三样上的差异是「**滞后多久**」和「**换起来多麻烦**」，而不是「有没有」。唯一真正的结构性差异是 **NixOS 的 stable 频道图形栈落后约一年**。

### 关键判断

| 判断 | 依据 |
|---|---|
| **纯性能天花板**：Arch ≈ Tumbleweed > NixOS | Arch Mesa 26.2.4；TW Mesa 26.2.x。两者几乎同步上游。NixOS stable 停在 Mesa **25.2.6**（落后约一年）`[核实]` |
| **卡顿/帧时间**：三者都能上 `scx_lavd` | 需内核 ≥6.12 + `CONFIG_SCHED_CLASS_EXT`。Arch 的 `scx-scheds` 1.1.3、TW 的 `scx` 1.0.16、NixOS 的 `services.scx` 均可用 `[核实]` |
| **NixOS 反而最优雅** | 一行声明式配置就启用 SteamOS 同款调度器：`services.scx = { enable = true; scheduler = "scx_lavd"; };` `[核实]` |
| **Tumbleweed 的 NVIDIA 最痛** | 驱动是 KMP 内核模块包，**内核升级会导致驱动直接损坏**（6.18 事件），需回退旧内核等重编 `[社区]` |
| **开箱即用**：Tumbleweed > Slowroll > Arch > NixOS | NixOS 有 FHS/`steam-run` 封装、`enable32Bit` 默认关闭等坑 `[核实]` |
| **翻车恢复**：NixOS > Tumbleweed > Slowroll > Arch | NixOS generation 一键回滚；TW snapper + GRUB 快照；Arch 只有 ALA 手动降级 `[核实]` |

### 如果只看一句话

- **要最高帧率且愿意维护** → Arch（或 CachyOS）
- **要最新图形栈又不想天天修** → Tumbleweed
- **要可回滚、可复现、能声明式配调度器** → NixOS（**但必须用 unstable 或换内核，stable 图形栈太旧**）

---

## 1. 先搞清楚：发行版到底在哪一层起作用

游戏性能可以拆成 6 层。**发行版的差异集中在第 1、2 层，第 3–6 层差异很小**（因为大家都用同一批上游组件）。

| 层 | 内容 | 发行版差异度 | 谁决定 |
|---|---|---|---|
| 1. 内核与 CPU 调度器 | `CONFIG_HZ`、PREEMPT、EEVDF、BORE、**sched_ext/scx_lavd** | **高** | 发行版内核包 / 你自己换 |
| 2. 图形栈 | Mesa RADV、NVIDIA 驱动、Vulkan loader、32 位库 | **高** | 发行版仓库的新鲜度 |
| 3. 用户态运行层 | Steam、Proton、GameMode、MangoHud、gamescope | 中 | 发行版打包 + 上游 |
| 4. 显示协议 | Wayland/X11、HDR、VRR、explicit sync | 低 | Plasma/GNOME 版本（大家都用同一批） |
| 5. 文件系统与 I/O | Btrfs vs ext4、`compress=`、I/O 调度器 | 低 | 你装系统时的选择 |
| 6. CPU 调频 | `amd-pstate`、`power-profiles-daemon` vs `tuned` | 中 | 发行版默认 + 你改 |

---

## 2. 图形栈新鲜度（决定性能上限）

| 项目 | NixOS | Arch Linux | Tumbleweed | Slowroll |
|---|---|---|---|---|
| Mesa（RADV） | unstable **26.2.4** / stable **25.2.6** ⚠️ | **26.2.4**（`vulkan-radeon 1:26.2.4-1`）`[核实]` | **26.2.x**（`Mesa-dri-nouveau-32bit-26.2.4`）`[核实]` | 滞后最多 ~1 个月 |
| 32 位 Vulkan（Steam 必需） | 需 `hardware.graphics.enable32Bit`，**默认 false**，漏设 → Proton 黑屏/崩溃 `[核实]` | `lib32-vulkan-radeon`（multilib，开箱即有）`[核实]` | ⚠️ **AMD 用户需手动 `zypper in libvulkan_radeon-32bit`，默认不装** `[核实]` | 同 TW |
| NVIDIA 内核模块 | `hardware.nvidia.open` 切开源模块；分支多：`production` 595.104.02 / `new_feature` 615.71.09 / `legacy_580`（LTSB，支持到 2028-08）`[核实]` | `nvidia-open` **615.78.08**（2026-10-08 构建）；维护者含 CachyOS 的 ptr1337 `[核实]` | 官方源 `openSUSE-repos-NVIDIA`；新系统默认自动装**已签名开源内核模块**，不影响 Secure Boot `[核实]` | 同 TW |
| NVIDIA 痛点 | 版本号是**打包版本**，滞后取决于 nixpkgs 更新节奏 | 版本新（615.78.08） | ⚠️ **KMP 内核模块包：内核升级导致驱动损坏**，需回退旧内核 `[社区]` | 同 TW |
| 追新手段 | 无官方 mesa-git overlay；靠 `overrideAttrs` 改 `hardware.graphics.package` `[核实]` | AUR：`mesa-git`、`nvidia-beta` | OBS `X11:Drivers:Video` 等第三方源 | 同 TW |

**结论**：
- **Arch 和 Tumbleweed 的 Mesa 几乎同步上游**（都是 26.2.4），这是两者游戏性能天花板高的根本原因。
- **NixOS 的 stable 频道是硬伤**：Mesa 25.2.6 vs 26.2.4，差一个大版本周期。RADV 的每个版本都带实质性游戏修复，落后一年意味着新游戏可能直接跑不起来或性能明显偏低。
- **Tumbleweed 的 AMD 32 位库要手动装**，这是很容易踩的坑（装完 Steam 发现游戏黑屏）。

---

## 3. 内核与调度器（决定卡顿和帧时间稳定性）

### 3.1 可用内核

| | NixOS | Arch | Tumbleweed |
|---|---|---|---|
| 默认内核 | 25.11 → **6.17**；unstable 更新 `[核实]` | `linux` **7.2.x** `[核实]` | `kernel-default` **7.2.x**（7.2.6 / 7.2.9-devel）`[核实]` |
| 游戏向内核 | `linuxPackages_zen`、`linuxPackages_lqx`（Liquorix）、`linuxPackages_xanmod`（含 wine 补丁 + tickless）、`linuxPackages_cachyos`（**nixpkgs 未收录**）`[核实]` | `linux-zen` **7.2.9.zen1-1**（2026-10-06，zen-kernel 补丁集，含 NTSYNC 模块）`[核实]` | 只有 `kernel-default` / `kernel-vanilla`（7.1.6）。**无 kernel-zen / 实时内核** `[核实]` |
| 换内核代价 | `boot.kernelPackages = pkgs.linuxPackages_zen;` 但**需本地重编译**（无缓存时数十分钟~数小时）`[社区]` | `pacman -S linux-zen`，重启即用 | 只能装 `kernel-vanilla`，或自建 OBS 包 |

### 3.2 sched_ext / scx 调度器 —— 本次比较最大的差异点

**为什么重要**：`scx_lavd` 是 Igalia 为 Steam Deck 开发的 BPF 调度器，**最初就是为游戏场景设计**，目标是「提升交互性、减少卡顿」，主要面向单 CCX / 单 socket 系统。它是**运行时动态加载**的，不需要重编内核。`[核实]`

| | NixOS | Arch | Tumbleweed |
|---|---|---|---|
| 包 | `services.scx` 模块（声明式）`[核实]` | `scx-scheds` **1.1.3-2**（extra，2026-09-05）`[核实]` | `scx` **1.0.16-2.1**（版本落后于 Arch）`[核实]` |
| 启用方式 | `services.scx = { enable = true; scheduler = "scx_lavd"; };` —— **一行配置** | `pacman -S scx-scheds` 后手动跑 `scx_lavd` | `zypper in scx` + `scx.service` + `/etc/default/scx` |
| 前提 | 内核 ≥6.12（25.11 的 6.17 满足）`[核实]` | 内核需 `CONFIG_SCHED_CLASS_EXT`（Arch 官方内核据报已启用）`[社区]` | 内核 ≥6.12（远超）`[核实]` |
| 附加工具 | — | — | ⚠️ `scx_loader.service` **尚未打包**（安全审查中）`[核实]` |

**结论**：三者都能用上 SteamOS 同款调度器，但 **NixOS 的声明式写法最优雅**（一行配置、可回滚、可复现），Arch 版本最新，Tumbleweed 版本落后且缺自动切换服务。

### 3.3 CPU 调频

| | NixOS | Arch | Tumbleweed |
|---|---|---|---|
| 机制 | `powerManagement.cpuFreqGovernor`；`services.power-profiles-daemon` / `services.tuned` 均可声明式启用 `[核实]` | 默认倾向 `power-profiles-daemon`；游戏社区常用 `tuned` `[社区]` | ⚠️ **默认 `power-profiles-daemon`（0.30），不是 SUSE 传统的 `tuned`** `[核实]` |
| 游戏建议 | governor 设 `performance` | 同上 | 手动切 `performance` profile 或装 tuned `[社区]` |

### 3.4 NTSYNC —— 被低估的一项

- **NTSYNC 在 Linux 6.14 进入主线**，把 Windows NT 的同步原语实现在 `/dev/ntsync` 字符设备上，Wine/Proton 可直接调用，替代 E-SYNC/F-SYNC。`[核实]`
- **修复了 E-SYNC/F-SYNC 处理不好的游戏**：Bioshock 系列、Call of Duty Black Ops I / II。`[核实]`
- GE-Proton **检测到模块已加载就默认启用 NTSYNC**。`[核实]`
- **Fedora 44 是第一个通过 `wine-ntsync` 包默认启用该模块的发行版**（2025-12-02 提案）。`[核实]`
- 三个发行版内核版本都 ≥6.14，**模块都存在**；差异在于**是否默认加载**。Arch 的 `linux-zen` 明确提供 NTSYNC 模块。`[核实]`

**实操**：三者都可以手动加 `/etc/modules-load.d/ntsync.conf`（内容 `ntsync`）确保加载。

---

## 4. 游戏运行层（工具链齐备度）

| 组件 | NixOS | Arch | Tumbleweed |
|---|---|---|---|
| Steam | `programs.steam.enable`（自动置 `hardware.graphics.enable` + `enable32Bit`；**不自动开防火墙端口**）`[核实]` | `multilib/steam 1.0.0.87-3`，**官方仓库** `[核实]` | **OSS 仓库**，`zypper install steam`；也可 Flatpak `[核实]` |
| GameMode | `programs.gamemode` 模块 `[核实]` | `extra/gamemode` `[社区]` | 官方仓库 `gamemode 1.8.2` `[核实]` |
| MangoHud | `programs.mangohud` 模块 `[核实]` | `extra` `[社区]` | 官方仓库 `mangohud 0.8.2` `[核实]` |
| gamescope | `programs.gamescope` 模块 `[核实]` | `extra` `[社区]` | games:tools OBS 包 `[核实]` |
| Lutris / Heroic / Bottles | 均在 nixpkgs `[核实]` | `extra` 或 AUR `[社区]` | Lutris 在 Package Hub/OSS；Heroic/Bottles 主要走 Flatpak/OBS `[社区]` |
| **Proton-GE** | ⚠️ **nixpkgs 无打包**，需 overlay（`daluca/proton-ge-overlay`）或手动放 `compatibilitytools.d` `[核实]` | AUR `proton-ge-custom-bin` `[社区]` | ⚠️ **无官方包**，用 ProtonUp-Qt(Flatpak) 或手动 `[核实]` |
| Wayland/HDR/VRR | 25.11 默认 GNOME 49（**已移除 X11**）+ Plasma 6；gamescope 提供 HDR/VRR/限帧 `[核实]` | Plasma 6.6；explicit sync 自 Plasma 6.1 + NVIDIA 555+ 默认启用 `[核实]` | KDE **2026-01 起默认 Wayland**；Plasma **6.7.4**、GNOME **50.4**；**HDR 仅 Wayland** `[核实]` |

**NixOS 特有的两个坑**：
1. **FHS 封装开销**：Steam 由 `buildFHSEnv` / `steam-run` 包裹，有额外启动开销；缺库需 override `extraLibraries`。`[核实]`
2. **`nix-ld`**：跑非打包 Linux 二进制用（`programs.nix-ld.enable`），默认库极少需手加。`[核实]`

**Tumbleweed 特有的坑**：自 20250211 起默认启用 **SELinux**，曾导致 Wine/Proton/Lutris 异常。**已修复**——`selinux-policy-targeted-gaming` 包现为 steam 依赖。`[核实]`

---

## 5. 不可变变体能不能玩游戏（Aeon / Kalpa）

| 问题 | 答案 |
|---|---|
| 能装 Steam 吗 | 能，走 **Flatpak**（系统预配 Flathub），路径与 Bazzite 类似 `[核实]` |
| 能装 NVIDIA 吗 | 能：`transactional-update -i pkg install openSUSE-repos-NVIDIA` 再装 `nvidia-video-G06` `[核实]` |
| 有 GPU 性能损失吗 | 只读根 / Flatpak 化**本身无 GPU 性能损失**；容器隔离可能影响部分反作弊 `[社区/推断]` |
| 有 Bazzite 对应物吗 | **没有**。openSUSE 无游戏专用不可变发行版；Aeon/Kalpa 非游戏导向 `[核实]` |

---

## 6. 性能优化的代价与翻车恢复

| | NixOS | Arch | Tumbleweed | Slowroll |
|---|---|---|---|---|
| 追新导致驱动/性能回退的风险 | 中（取决于频道） | 高 | 高 | 低 |
| 恢复手段 | **generation 一键回滚**：`nixos-rebuild switch --rollback`，或启动菜单选旧代 `[核实]` | **无官方快照**。`downgrade` + `IgnorePkg`，或 ALA 整机回退 `[核实]` | **Btrfs + snapper**：GRUB 选只读快照 → `snapper rollback` `[核实]` | 同 TW |
| 恢复速度 | 秒级（切 generation） | 分钟级（手动） | 秒级（重启选快照） | 秒级 |
| 「装完即忘」可行吗 | 需要（rebuild + GC） | 需要（更新 + 驱动回退 + `.pacnew`） | 中等 | 中等 |

**结论**：NixOS 在「翻车后多快能回来」上碾压——这也是它唯一的游戏场景结构性优势。Arch 完全靠你自己。

---

## 7. CachyOS 作为参照（Arch 系的游戏优化发行版）

因为很多「Linux 游戏性能」的讨论最终都会指向 CachyOS，这里单列。

| 项目 | 内容 |
|---|---|
| 技术手段 | **BORE 调度器** + "Cachy Sauce" 补丁集；仓库分三级：**x86-64-v4（全 Arch 包 + LTO）、x86-64-v3（全 Arch 包 + LTO）、x86-64（仅内核）** `[核实]` |
| 内核包 | `linux-cachyos-bore-lto` 等 `[核实]` |
| **实际收益** | Phoronix 2024-02-29 用 Threadripper 7995WX 测 x86-64-v3/v4 仓库，**多数工作负载增益温和（个位数百分比）** `[核实]` |
| 官方宣传 | "blazingly fast" 属**自测宣传**，需打折 `[宣传]` |
| 现状 | 缺 2026 年的独立量化数据；Arch 的 `nvidia-open` 维护者中就有 CachyOS 的 ptr1337 `[核实]` |

**怎么读**：CachyOS 的收益是**真实的但温和的**（个位数百分比），不是「换发行版帧率翻倍」。它的真正价值在于**省掉自己调优的功夫**（BORE 内核 + 优化仓库开箱即有）。

---

## 8. 针对 RimWorld 的特化建议

> RimWorld 是 Unity/Mono 引擎、**CPU 单线程瓶颈**，后期卡顿来自 TPS（ticks per second）而非 GPU。所以对 RimWorld 而言，**第 1 层（内核/调度器/调频）比第 2 层（图形栈）重要得多**。

| 手段 | 做法 | 效果 |
|---|---|---|
| **CPU 亲和性固定** | 用 `taskset` 把游戏固定到特定核心，改善缓存局部性、减少上下文切换。社区项目 `cebarks/Rimworld-LinuxMisc` 就是干这个的 `[核实]` | Linux 特有，见效明显 |
| **调度器** | `scx_lavd`（低尾延迟，减少卡顿）`[核实]` | 针对交互性负载 |
| **CPU governor** | 设 `performance`，避免降频拖慢 tick | 中 |
| **模组层面** | **Performance Fish** 模组（智能缓存 + 算法优化）——这是 RimWorld 后期性能提升幅度最大的单一手段 `[社区]` | 大 |
| **图形栈** | 对 RimWorld **几乎无关**。不用为它追 Mesa/NVIDIA 最新版 | 无 |

**结论**：如果你的主要目标是 RimWorld，**三个发行版在图形栈上的差异对你几乎无意义**；应该关注的是「能不能方便地设 CPU governor / 上 scx 调度器 / 用 taskset」。这三件事在 Arch 和 NixOS 上都很容易（NixOS 甚至可以声明式写死），Tumbleweed 需要手动。

---

## 9. 游戏性能评分卡（主观综合，1–5 分）

> 评分为本报告基于上述事实的综合判断，非客观测量值。

| 维度 | NixOS | Arch | Tumbleweed | Slowroll |
|---|---|---|---|---|
| 图形栈新鲜度 | 3.0 ⚠️ | **5.0** | **5.0** | 3.5 |
| 内核 / 调度器可调性 | 4.5 | **5.0** | 4.0 | 3.5 |
| 游戏工具链齐备度 | 4.0 | **5.0** | 4.5 | 4.0 |
| 开箱即用（少折腾） | 3.0 | 3.5 | **4.5** | 4.0 |
| 更新翻车可恢复性 | **5.0** | 3.0 | 4.5 | 4.5 |
| NVIDIA 支持质量 | 3.5 | **4.0** | 2.5 ⚠️ | 2.5 ⚠️ |

---

## 10. 决策建议

| 你的情况 | 推荐 | 关键动作 |
|---|---|---|
| 追求最高帧率，AMD 显卡，愿意维护 | **Arch**（或 CachyOS 省事） | `pacman -S linux-zen scx-scheds gamemode mangohud gamescope` |
| 追新但不想天天修，NVIDIA 以外 | **Tumbleweed** | `zypper in steam gamemode mangohud scx`；**记得手动装 `libvulkan_radeon-32bit`** |
| 要可回滚 / 可复现 / 声明式配调度器 | **NixOS**，**必须用 unstable 或换 zen 内核** | `services.scx.enable = true; scheduler = "scx_lavd";` + `hardware.graphics.enable32Bit = true;` |
| NVIDIA 显卡 + 游戏为主 | **Arch**（避开 Tumbleweed 的 KMP 重编问题） | 用 `nvidia-open` 615.x |
| 只想装完就玩、不折腾 | **Tumbleweed**（或考虑 Bazzite，非本报告范围） | 装完 `zypper install steam lutris mangohud gamemode` |
| 主要玩 RimWorld 这类 CPU 瓶颈游戏 | **任选，Arch/NixOS 略优** | 优先搞 `scx_lavd` + governor + taskset，别折腾显卡 |

---

## 11. 存疑与未核实项

| 项 | 状态 |
|---|---|
| **三个发行版的游戏帧率直接对比数据** | **不存在**。任何「X 比 Y 快 N%」的说法都需警惕，除非是 Phoronix 这类独立实测 |
| Arch 官方内核是否默认 `CONFIG_SCHED_CLASS_EXT=y` | 未从官方 config 直接确认，仅有 `scx-scheds` 存在 + 内核列为 optional dep 的间接证据 |
| `linux-zen` 具体 `CONFIG_HZ` / `PREEMPT` 值 | 未取到 config，仅知来自 zen-kernel 补丁集（**非 BORE**） |
| NixOS 各 NVIDIA 分支的滞后天数 | 未量化 |
| Tumbleweed 的 `scx` 版本（1.0.14 vs 1.0.16） | 两个来源有差异，以官方 wiki 1.0.16 为准 |
| Slowroll 的 Mesa 实际滞后 | 推断为「最多 1 个月」，未取到具体版本号 |
| CachyOS 2026 年的性能收益 | 缺当前独立量化数据，仅 2024 Phoronix 旧测 |

---

## 12. 参考来源

### NixOS
- [nixpkgs mesa common.nix (unstable, 26.2.4)](https://raw.githubusercontent.com/NixOS/nixpkgs/nixos-unstable/pkgs/development/libraries/mesa/common.nix)
- [nixpkgs mesa common.nix (nixos-25.11, 25.2.6)](https://raw.githubusercontent.com/NixOS/nixpkgs/nixos-25.11/pkgs/development/libraries/mesa/common.nix)
- [nixpkgs nvidia-x11 default.nix (unstable)](https://raw.githubusercontent.com/NixOS/nixpkgs/nixos-unstable/pkgs/os-specific/linux/nvidia-x11/default.nix)
- [MyNixOS: hardware.nvidia.branch](https://mynixos.com/nixpkgs/option/hardware.nvidia.branch)
- [MyNixOS: hardware.graphics.enable32Bit](https://mynixos.com/nixpkgs/option/hardware.graphics.enable32Bit)
- [MyNixOS: services.scx](https://mynixos.com/nixpkgs/options/services.scx)
- [NixOS Wiki: Gaming](https://wiki.nixos.org/wiki/Gaming)
- [NixOS Wiki: Nix-ld](https://wiki.nixos.org/wiki/Nix-ld)
- [fufexan/nix-gaming README](https://raw.githubusercontent.com/fufexan/nix-gaming/master/README.md)
- [daluca/proton-ge-overlay](https://github.com/daluca/proton-ge-overlay)
- [xddxdd/nix-cachyos-kernel](https://github.com/xddxdd/nix-cachyos-kernel)
- [kronflux/nixos-gaming](https://github.com/kronflux/nixos-gaming)
- [Jovian-NixOS: Steam](https://jovian-experiments.github.io/Jovian-NixOS/steam.html)
- [NixOS Discourse: Installing the Zen/Liquorix/CachyOS kernel](https://discourse.nixos.org/t/installing-the-zen-liquorix-cachyos-kernel/63663)

### Arch Linux
- [Arch Linux - vulkan-radeon 1:26.2.4-1](https://archlinux.org/packages/extra/x86_64/vulkan-radeon/)
- [Arch Linux - nvidia-open 615.78.08-1](https://archlinux.org/packages/extra/x86_64/nvidia-open/)
- [Arch Linux - linux-zen 7.2.9.zen1-1](https://archlinux.org/packages/extra/x86_64/linux-zen/)
- [Arch Linux - steam 1.0.0.87-3 (multilib)](https://archlinux.org/packages/multilib/x86_64/steam/)
- [Arch Linux - scx-scheds 1.1.3-2](https://archlinux.org/packages/extra/x86_64/scx-scheds/)
- [ArchWiki - Gaming](https://wiki.archlinux.org/title/Gaming)
- [ArchWiki - Improving performance](https://wiki.archlinux.org/title/Improving_performance)
- [ArchWiki - NVIDIA](https://wiki.archlinux.org/title/NVIDIA)
- [GitHub - CachyOS/linux-cachyos](https://github.com/CachyOS/linux-cachyos)
- [Phoronix - Arch Linux CachyOS Benchmarks Of x86-64-v3 & x86-64-v4](https://www.phoronix.com/review/cachyos-x86-64-v3-v4)
- [Phoronix - The Performance Of Arch Linux Powered CachyOS](https://www.phoronix.com/review/cachyos-linux-perf)
- [Stop Linux Gaming Stutter: Automatic CPU Scheduler Switching with sched_ext](https://blog.foulkes.cloud/arch-linux-gaming-scx-scheduler/)

### openSUSE
- [Pluggable CPU schedulers - openSUSE Wiki](https://en.opensuse.org/Pluggable_CPU_schedulers)
- [SDB:NVIDIA drivers - openSUSE Wiki](https://en.opensuse.org/SDB:NVIDIA_drivers)
- [Steam - openSUSE Wiki](https://en.opensuse.net.cn/Steam)
- [Portal:Slowroll - openSUSE Wiki](https://en.opensuse.net.cn/Portal:Slowroll)
- [为什么选择 openSUSE 玩游戏是个好主意 (suse.org.cn)](https://www.suse.org.cn/%E7%A4%BE%E5%8C%BA%E6%96%B0%E9%97%BB/2025/05/31/gaming-with-opensuse.html)
- [Nvidia drivers after kernel update - openSUSE Forums](https://forums.opensuse.org/t/nvidia-drivers-after-kernel-update/190209)
- [Tuned in Tumbleweed - openSUSE Forums](https://forums.opensuse.org/t/tuned-in-tumbleweed/195796)
- [openSUSE Tumbleweed SELinux and Gaming fix is now in](https://lowtechlinux.com/2025/03/30/opensuse-tumbleweed-selinux-and-gaming-fix-is-now-in/)
- [openSUSE Tumbleweed to enable Wayland by default on KDE Plasma](https://lowtechlinux.com/2026/01/08/opensuse-tumbleweed-to-enable-wayland-by-default-on-kde-plasma/)
- [games:tools / gamescope - openSUSE Build Service](https://build.opensuse.org/package/show/games:tools/gamescope)
- [gamemode-1.8.2 RPM (pkgs.org)](https://opensuse.pkgs.org/tumbleweed/opensuse-oss-x86_64/gamemode-1.8.2-1.6.x86_64.rpm.html)
- [Best option for Steam games on NVIDIA/Proton, Slowroll or MicroOS? - openSUSE Forums](https://forums.opensuse.org/t/best-option-for-steam-games-on-nvidia-proton-slowroll-or-microos/169745)

### 跨发行版通用层
- [scx_lavd - sched_ext 官方文档](https://sched-ext.com/docs/scheds/rust/scx_lavd)
- [GitHub - sched-ext/scx](https://github.com/sched-ext/scx)
- [Extensible Scheduler Class — The Linux Kernel documentation](https://www.kernel.org/doc/html/next/scheduler/sched-ext.html)
- [LAVD: From Gaming to Server Fleets (kernel-recipes 2026)](https://kernel-recipes.org/en/2026/schedule/lavd-from-gaming-to-server-fleets-a-bpf-scheduler-for-cloud-ml-and-edge/)
- [Igalia - scx_lavd OSPM 2026 slides](https://www.igalia.com/downloads/slides/scx_lavd-ospm2026.pdf)
- [Fedora Changes/NTSYNC-Contained](https://fedoraproject.org/wiki/Changes/NTSYNC-Contained)
- [Linux kernel docs: NTSYNC](https://docs.kernel.org/userspace-api/ntsync.html)
- [GamingOnLinux - NTSYNC in Linux kernel 6.14](https://www.gamingonlinux.com/2025/01/ntsync-for-proton-wine-now-in-linux-kernel-6-14-that-should-make-many-steamos-users-happy/)
- [GitHub - cebarks/Rimworld-LinuxMisc](https://github.com/cebarks/Rimworld-LinuxMisc)
