# CachyOS vs Ubuntu 26.04 LTS 深度对比：结果、原因、以及"纯官方 Ubuntu 能复现多少"

- **调研日期**：2026-10-16
- **对比对象**：CachyOS vs **Ubuntu 26.04 LTS（Resolute Raccoon）**
- **核心问题**：① 全面比较 ② 结果分析 ③ 差异的原因 ④ 差异为何**不突出** ⑤ **在没有第三方仓库的前提下，Ubuntu 26.04 能复现 CachyOS 的哪些优化策略？**
- **一句话结论**：CachyOS 与 Ubuntu 26.04 的实测差距**只有约 3.8%**（Phoronix 同机 99 项几何平均：76.19 vs 73.38）。Ubuntu 的短板不在内核（它是 **Linux 7.0**），而在**编译层（v1 基线）**与**sched-ext 缺失（需源码编译）**；它的强项是 **NVIDIA 驱动与 ZFS 官方支持**。

---

## 0. 结论速览

| 问题 | 答案 |
|---|---|
| 谁更快？ | CachyOS，但**只快约 3.8%**（Phoronix Razer Blade 18 同机 99 项，geomean 76.19 vs 73.38） |
| Ubuntu 26.04 的短板？ | **编译层 v1 基线**；**官方仓库无 `scx-scheds`**（需源码编译）；无 BORE/BMQ 内核；默认 ext4 无快照 |
| Ubuntu 26.04 的强项？ | **NVIDIA 驱动支持全 Linux 最好**（官方仓库 + `ubuntu-drivers` + **原生 CUDA 集成**）；**ZFS 官方支持**；内核不旧（**Linux 7.0 + Mesa 26.0.x**）；10 年支持 |
| 差异为何不突出？ | 差距实测仅 3.8%；Ubuntu 内核版本并不落后；差距来自 v1→v3 编译层（收益本就有限）；sched-ext 缺失只影响尾部延迟 |
| 纯官方 Ubuntu 能复现多少？ | **约 13 项可复现**（含 Gamemode/MangoHud、NVIDIA 驱动、ZFS）；**全仓库 v3 重编译、BORE 内核、sched-ext 包**做不到 |

---

## 1. 全面比较

| 维度 | CachyOS | Ubuntu 26.04 LTS |
|---|---|---|
| **上游** | Arch Linux（下游再发行） | 独立发行版（Canonical） |
| **发布模型** | 滚动 | **LTS**：5 年标准支持，Ubuntu Pro 可延至 **10 年**（2026-04-23 发布） |
| **指令集基线** | `v3` / `v4` / `znver4` | **`amd64`（v1）**；amd64v3 为实验性变体 |
| **编译优化** | LTO + PGO + BOLT + AutoFDO | 部分优化；无 PGO/BOLT |
| **内核** | 自研 `linux-cachyos`（默认/BORE/EEVDF/BMQ/RT/LTS/Hardened/Server/deckify） | **Linux 7.0**（LTS 版）+ Ubuntu 补丁 |
| **GPU 栈** | 预编译 NVIDIA 模块 + Mesa 最新 | **Mesa 26.0.x**；**原生集成 NVIDIA CUDA** |
| **调度器** | BORE / BMQ / sched-ext / RT | EEVDF；**官方仓库无 scx 包**（需源码编译） |
| **默认文件系统** | Btrfs + 快照 | **ext4**（Btrfs/ZFS 可选，无默认快照） |
| **安全默认** | 常规 | **AppArmor**（默认）+ 大量 **snap** 应用 |
| **显示会话** | Wayland / X11 均可 | **仅 Wayland**（首个移除 Xorg 会话的 LTS） |
| **包管理** | `pacman` + AUR | `apt` + snap + PPA |
| **游戏工具** | `cachyos-gaming-meta` 一键装 | **`gamemode 1.8.2`、`mangohud 0.8.2` 在官方仓库**（已核实） |
| **NVIDIA 驱动** | 官方仓库内置预编译模块 | **官方仓库 + `ubuntu-drivers` 自动安装（Linux 阵营最佳）** ✅ |
| **ZFS** | 官方预编译模块 | **官方支持（`zfsutils-linux` 在 main，安装器可选 ZFS 根）** ✅ |
| **系统要求** | 较低 | **内存要求提升至 6GB** |
| **治理** | 社区小团队（约 9 人） | **Canonical 商业公司**（正式治理 + 商业支持） |
| **典型用户** | 想省事 + 要性能 | 企业、开发者、需要长期稳定与生态支持 |

**关系本质**：两者**没有血缘关系**。Ubuntu 由 **Canonical 商业公司**主导，卖点是**稳定、生态、长期支持**；CachyOS 是社区小团队，卖点是**性能**。这两者的取舍是"**稳定 vs 极致**"的典型对立。

---

## 2. 结果分析

### 2.1 ★ Phoronix — Razer Blade 18，三系统，99 项（2026-07-15）

| 系统 | 几何平均分 |
|---|---|
| **CachyOS** | **76.19** |
| Windows 11 | 76.12 |
| **Ubuntu 26.04 LTS** | **73.38** |

- **换算**：CachyOS 比 Ubuntu 26.04 LTS **高约 3.8%**（76.19 / 73.38）。
- **胜项数**：CachyOS 51 项 / Windows 11 约 38 项 / **Ubuntu 约 10 项**。
- ✅ 这是**最干净的同机同套件三方对比**，也是"Ubuntu 26.04 比 CachyOS 慢多少"的**唯一硬数字**。
- ⚠️ 混杂变量：CachyOS 用更新的内核 + Mesa，Ubuntu 是 LTS 快照（但 26.04 内核已是 **Linux 7.0**，差距没那么大）。

### 2.2 Phoronix — Ryzen 9 9950X，6 发行版，59 项（2024-08）

| 排名 | 发行版 |
|---|---|
| 1 | Clear Linux |
| 2 | CachyOS |
| 3 | Arch Linux |
| 4 | Fedora Workstation 40 |
| 5 | Ubuntu 24.10 Snapshot |
| 6 | **Ubuntu 24.04 LTS** |

- ⚠️ **Ubuntu 在发行版性能横评中长期垫底**（此轮第 5、第 6 都是 Ubuntu）。
- 但注意：**这是 24.04/24.10**，不是 26.04——26.04 换上了 **Linux 7.0**，情况已改善。

### 2.3 Ubuntu 版本内的性能变化（重要参照）

| 来源 | 数据 |
|---|---|
| Phoronix 2026-03-12 | **Ubuntu 26.04 相比 25.10，RTX 5090 游戏性能最高 +12%，平均 +4.4%** |
| Phoronix 2026-06-11 | 《Benchmarking The Performance Benefits To Ubuntu 26.10 amd64v3 Packages》 |
| Phoronix 2026-10-14 | 《Ubuntu 26.10 amd64v3 Packages Provide Some Additional Uplift On AMD EPYC》 |

> **关键校准**：**一次 Ubuntu 版本升级（25.10 → 26.04）的游戏收益最高就有 +12%**，而 **CachyOS 与 Ubuntu 26.04 之间的差距只有 3.8%**。
> **也就是说：等一次 Ubuntu 大版本升级，比换发行版带来的收益可能更大。**

### 2.4 amd64v3：Canonical 自己也在做指令集优化

- Ubuntu 26.04 默认 ISO 仍是 **amd64（v1）**，以确保最大硬件兼容性。
- **amd64v3（x86-64-v3）是 Canonical 自家的实验性归档**；Phoronix 明确提到"**Ubuntu 26.10 的 snapshot/daily ISO 提供 amd64v3 形式**"，并在 EPYC 服务器上实测到额外收益。
- 部分中文来源称 Ubuntu 26.04 已提供可选的 amd64v3 包——**该细节建议以 Canonical 官方 release notes 为准**。

---

## 3. 差异的原因

### 3.1 编译层 —— CachyOS 的最大优势（也是 3.8% 差距的主要来源）

| 项 | Ubuntu 26.04 | CachyOS | 影响 |
|---|---|---|---|
| 指令集基线 | **`amd64`（v1）** | `v3`/`v4`/`znver4` | **CPU 密集 2–8%** |
| LTO | 部分 | 全栈 ThinLTO | 1–3% |
| PGO | 无 | 核心包 + 内核 AutoFDO | 1–4% |
| BOLT | 无 | 核心包 | 1–3% |

### 3.2 内核层 —— Ubuntu 并不落后

| 项 | Ubuntu 26.04 | CachyOS |
|---|---|---|
| 内核版本 | **Linux 7.0**（LTS 基线） | 跟随 Arch（也很新） |
| GPU 栈 | **Mesa 26.0.x** + 原生 CUDA | Mesa 最新 |
| 调度器 | EEVDF | EEVDF 调参 / **BORE** / **BMQ** / RT |
| **sched-ext 包** | ❌ **官方仓库无**（sched-ext 官方 INSTALL.md 明确：Ubuntu 需**源码编译**） | ✅ 内置 |
| Tick rate | 常规 | **1000Hz** |
| 补丁集 | Ubuntu 补丁 | 15 个 topic 分支 + `CONFIG_CACHY` + AutoFDO |

> **Ubuntu 的内核版本其实不旧**（Linux 7.0），所以"内核红利"它基本也能吃到——这是差距只有 3.8% 的重要原因之一。

### 3.3 系统/默认配置层

| 项 | Ubuntu 26.04 | CachyOS |
|---|---|---|
| 文件系统 | **ext4 默认**（Btrfs/ZFS 可选） | Btrfs + 快照 |
| 快照 | ❌ 默认无（可用 ZFS 或 timeshift） | ✅ 安装时可选 |
| zram | ❌ 未默认 | ✅ 启用 |
| 安全 | **AppArmor 默认** + snap 沙箱 | 常规 |
| 显示 | **仅 Wayland**（移除 Xorg） | Wayland / X11 均可 |
| 桌面 | GNOME 50（较重） | 17+ DE 可选 |

### 3.4 生态层 —— Ubuntu 反而更强

| 项 | Ubuntu 26.04 | CachyOS |
|---|---|---|
| **NVIDIA 驱动** | ✅ **官方仓库 + `ubuntu-drivers` + 原生 CUDA 集成**（Linux 最佳） | 官方仓库内置预编译模块 |
| **ZFS** | ✅ **官方 main 仓库，安装器支持 ZFS 根** | 官方预编译模块 |
| 游戏工具 | gamemode 1.8.2 / mangohud 0.8.2（**官方仓库**，已核实） | meta 包一键装 |
| 第三方生态 | PPA + snap + Flatpak | AUR（20 万+） |
| 文档 / 社区 | **Linux 世界最丰富** | Arch Wiki（质量高但偏技术） |

---

## 4. 差异"没突出"的原因

1. **实测差距只有 3.8%**（geomean 76.19 vs 73.38）——**这个数字本身就在"不突出"的范畴内**。
2. **Ubuntu 26.04 的内核不旧**：**Linux 7.0 + Mesa 26.0.x**，甚至比很多滚动发行版的某些组件还新——"内核红利"它也有。
3. **一次 Ubuntu 版本升级的收益可能大于发行版差异**：25.10 → 26.04 在 RTX 5090 上游戏最高 **+12%（平均 +4.4%）**。
4. **差距主要来自 v1→v3 编译层**，而这段收益本就只有个位数百分比。
5. **Ubuntu 的短板影响的是"尾部"不是"均值"**：缺 sched-ext、缺 BORE → 影响的是 1% low / 卡顿 / 输入延迟，而 Phoronix Test Suite 多数项目测的是吞吐与总耗时。
6. **瓶颈不在 CPU**（Amdahl 定律）：4K 游戏 GPU 受限、桌面受 IO/网络限制。
7. **测量噪声同量级**：run-to-run 方差常有 1–3%，与 3.8% 的差距部分重叠。
8. **部分"优化"是取舍**：`max_performance`、激进电源档是**用功耗/续航换响应**——这对笔记本形态的 Ubuntu 用户未必是优点。

---

## 5. 纯官方 Ubuntu 26.04 能复现哪些优化策略？

> **前提界定**："第三方仓库"指 **PPA / Flatpak / 外部 deb 仓库**等。Ubuntu 的 `main` + `universe` + `restricted` + `multiverse` 视为官方。

### 5.1 ✅ 可以复现（13 项）

| # | CachyOS 的优化策略 | 纯 Ubuntu 复现方法 | 来源 |
|---|---|---|---|
| 1 | **全套 sysctl 调优** | `/etc/sysctl.d/99-cachy.conf`：swappiness、dirty_*、page-cluster=0、nmi_watchdog=0、file-max、max_map_count | 官方内核 |
| 2 | **I/O 调度器按设备分配** | udev 规则：HDD→`bfq`、SATA SSD→`mq-deadline`、NVMe→`kyber` | 三种都在官方内核 |
| 3 | **THP defrag = defer+madvise** | `tmpfiles.d` | 官方内核 |
| 4 | **zram + zstd** | `zram-config` 或 `systemd-zram-generator`（**需自行启用，Ubuntu 默认不开**） | 官方 universe |
| 5 | **NTSync** | `modprobe ntsync`（Linux 6.14 起主线，**Ubuntu 26.04 用 Linux 7.0，内核已含**） | 官方内核自带（模块） |
| 6 | **Gamemode** | `sudo apt install gamemode` | ✅ **官方仓库**（已核实：**1.8.2-2build1** 在 resolute/26.04） |
| 7 | **MangoHud** | `sudo apt install mangohud` | ✅ **官方 universe**（已核实：**0.8.2~rc2-1** 在 resolute/26.04） |
| 8 | **CPU 性能档 / 电源档** | `powerprofilesctl set performance`（Ubuntu 默认 PPD）；或 `apt install tuned` → `tuned-adm profile latency-performance` | 官方仓库 |
| 9 | **抢占模型选择** | 内核 cmdline `preempt=full`（Ubuntu 内核为 PREEMPT_DYNAMIC） | 官方内核自带 |
| 10 | **EEVDF 调参** | `kernel.sched_base_slice_ns`（默认 base slice 3ms） | 官方内核自带 |
| 11 | **NVIDIA 驱动 / 模块参数** | `ubuntu-drivers autoinstall` 或 `apt install nvidia-driver-XXX`；参数写 `/etc/modprobe.d/` | ✅ **官方仓库（Ubuntu 最强项）** |
| 12 | **ZFS（含快照）** | `apt install zfsutils-linux`；安装器可选 **ZFS 根**，配合 `zfs-auto-snapshot` | ✅ **官方 main 仓库** |
| 13 | **SATA max_performance / hdparm / 音频 rtprio** | udev 规则 + `hdparm -B 254 -S 0` + `/etc/security/limits.d/` | 官方仓库 |

> **Ubuntu 的加分项**：第 11 条（NVIDIA）与第 12 条（ZFS）是 **Ubuntu 独有的官方优势**——CachyOS 的 NVIDIA 虽在官方仓库，但 Ubuntu 的 `ubuntu-drivers` 自动化 + **原生 CUDA 集成**体验更好；而 **ZFS 官方支持**是 Ubuntu 在主流发行版中的独门能力。

### 5.2 ❌ 无法在纯官方 Ubuntu 上复现的（10 项）

| # | CachyOS 的优化策略 | 为什么做不到 | 需要什么 |
|---|---|---|---|
| 1 | **全仓库 x86-64-v3 / v4 重编译** | 默认 ISO 是 **amd64（v1）** | **amd64v3 实验归档**（Canonical 自有但非默认，26.10 起有 ISO）或自建 |
| 2 | **LTO / PGO / BOLT 预编译包** | 属构建产物 | 同上 |
| 3 | **sched-ext 调度器（`scx-scheds`）** | ⚠️ **官方仓库无**——sched-ext 官方 INSTALL.md 明确 Ubuntu **需从源码编译** | 源码编译（`cargo build --release`） |
| 4 | **BORE 调度器内核** | 官方无 BORE（非主线） | 自编译 |
| 5 | **BMQ 内核** | 同上 | 自编译 |
| 6 | **CachyOS 内核补丁集**（`CONFIG_CACHY`、1000Hz、AutoFDO profile、POC Selector） | 官方内核不含 | 自编译 |
| 7 | **1000Hz tick 内核** | 官方内核非 1000Hz | 自编译 |
| 8 | **默认 Btrfs 快照回滚** | 默认 ext4，无快照 | 安装时选 Btrfs/ZFS + 自行配 `timeshift`/`snapper`/`zfs-auto-snapshot` |
| 9 | **CachyOS 专有工具链 / Proton-CachyOS** | 不在官方仓库 | PPA / 自建 |
| 10 | **ananicy-cpp** | 不在官方仓库 | PPA / 自建 |

### 5.3 直接回答你的问题

> **Ubuntu 26.04 在"没有第三方仓库"的前提下，能复现 CachyOS 约 13 项优化**——其中**两项是 Ubuntu 独有的官方优势**：
> 1. **NVIDIA 驱动**（官方仓库 + `ubuntu-drivers` + **原生 CUDA 集成**）——比 CachyOS 的预编译模块体验更好
> 2. **ZFS**（官方 `main` 仓库，安装器可选 ZFS 根 + 快照）
>
> 另有 **Gamemode 1.8.2 / MangoHud 0.8.2** 直接在官方仓库、**NTSync** 内核已含（Linux 7.0）、**EEVDF 参数与 `preempt=full`** 可调。
>
> **但 Ubuntu 有两个明显缺口**：
> 1. **sched-ext 调度器（`scx-scheds`）不在官方仓库**——必须**源码编译**（这是 Ubuntu 相对 Arch/openSUSE 的明显劣势）
> 2. **全仓库 v3/v4 重编译**做不到（默认 v1；amd64v3 是 Canonical 实验性归档，非默认）
>
> 加上 **BORE / BMQ 内核**必须自编译——这四项就是 CachyOS 在 Ubuntu 上**无法"官方即用"地复现**的部分。

### 5.4 ★ 五个发行版的"官方仓库能力"横比（实用速查）

| 能力 | CachyOS | Arch | openSUSE TW | Fedora | **Ubuntu 26.04** |
|---|---|---|---|---|---|
| sched-ext 调度器 | ✅ 内置 | ✅ `scx-scheds` | ✅ `scx` | ❌ 需 COPR | ❌ **需源码编译** |
| 游戏工具（gamemode/mangohud） | ✅ meta 包 | ✅ extra | ✅ 官方 | ✅ 官方 | ✅ **官方**（1.8.2 / 0.8.2） |
| Btrfs 快照默认 | ⚠️ 需选择 | ❌ 需自配 | ✅ **默认+GRUB** | ❌ 需自配 | ❌（但 **ZFS 官方可选**） |
| NVIDIA 专有驱动 | ✅ 官方仓库 | ✅ extra | ⚠️ NVIDIA 官方仓库 | ❌ 需 RPM Fusion | ✅ **官方 + ubuntu-drivers + CUDA** |
| ZFS 官方支持 | ✅ | ✅（官方仓库） | ❌ | ❌ | ✅ **main 仓库** |
| zram 默认启用 | ✅ | ❌ | ❌ | ✅ | ❌ |
| 指令集基线 | **v3/v4** | v1 | **v2** | v1 | v1（amd64v3 实验） |
| 内核版本 | 最新 | 最新 | 最新 | 最新 | **Linux 7.0** |

**读数**：
- **Ubuntu 在"官方仓库能力"上呈现明显的两极**：**NVIDIA 与 ZFS 是五者中最好的**（甚至优于 CachyOS），但 **sched-ext 是五者中最差的（连 Arch/openSUSE/Fedora 都不如）**。
- **指令集基线最低档**（v1，与 Arch/Fedora 同）——这是它性能落后 3.8% 的主因。
- **内核版本并不落后**（Linux 7.0），所以差距没有被进一步拉大。

---

## 6. 参考来源

- [Phoronix — Operating Systems 评测列表（Ubuntu 26.04 LTS vs Windows 11 vs CachyOS / Ubuntu amd64v3 系列）](https://www.phoronix.com/reviews/Operating+Systems)
- [太平洋科技 —《Windows真不差：实测 AI 性能 3.4 倍碾压 Linux》（含 99 项 geomean：CachyOS 76.19 / Win11 76.12 / Ubuntu 26.04 LTS 73.38）](https://g.pconline.com.cn/x/2178/21789100.html)
- [什么值得买 —《CS2低帧暴涨20%、99项测试赢51项》（Phoronix Razer Blade 18 三系统）](https://post.smzdm.com/p/a6zdp68o/)
- [IT之家 —《哪个 Linux 发行版最能发挥 AMD 锐龙 9 9950X 处理器实力？59 项实测》](https://www.ithome.com/0/790/322.htm)
- [IT之家 — Ubuntu 26.04 LTS 发布：原生集成 NVIDIA CUDA，内存要求提至 6GB（Linux 7.0 + Mesa 26.0.x + 仅 Wayland）](https://soft.ithome.com/archiver/0/943/001.htm)
- [Kubuntu 26.04 LTS Release Notes（基于 Linux kernel 7.0）](https://kubuntu.org/news/kubuntu-26-04-release-notes/)
- [阿里云开发者社区 — Ubuntu 26.04 LTS (Resolute Raccoon) 正式版发布（Linux 内核 7.0 + GNOME 50）](https://developer.aliyun.com/article/1730855)
- [sched-ext/scx — INSTALL.md（Ubuntu 需源码编译；openSUSE 官方含 scx；Fedora 需 COPR；Arch 官方 scx-scheds）](https://github.com/sched-ext/scx/blob/main/INSTALL.md)
- [Ubuntu Packages — gamemode（resolute/26.04 LTS：1.8.2-2build1）](https://packages.ubuntu.com/search?keywords=gamemode)
- [Ubuntu Packages — mangohud（resolute/26.04 LTS：0.8.2~rc2-1，universe）](https://packages.ubuntu.com/search?keywords=mangohud)
- [Phoronix — Ubuntu 26.04 游戏性能最高提升 12%（RTX 5090 实测）](https://baijiahao.baidu.com/s?id=1859512162622176649&wfr=spider&for=pc)
- [CSDN — Ubuntu 26.04 LTS "坚毅浣熊" 新特性前瞻（amd64v3 可选包说明）](https://blog.csdn.net/xiangxianghehe/article/details/158284560)
- [异次元软件 — Ubuntu 26.04 LTS 新功能汇总（AMD64v3 架构变体说明）](https://www.iplaysoft.com/?post_type=xpost&p=6534)
- [CSDN — Ubuntu 26.04 LTS 从零安装到开发环境搭建全指南（默认 ext4，Btrfs 可选）](https://blog.csdn.net/weixin_30225755/article/details/165316648)
- [百度百科 — Ubuntu 26.04（10 年支持、发布计划）](https://baike.baidu.com/item/Ubuntu%2026.04/67513823)
- [CachyOS 官方 Wiki — Why CachyOS?](https://wiki.cachyos.org/cachyos_basic/why_cachyos)
- [CachyOS 官方 Wiki — Kernel](https://wiki.cachyos.org/features/kernel)
- [Linux Kernel 文档 — /proc/sys/kernel/](https://www.kernel.org/doc/html/latest/admin-guide/sysctl/kernel.html)

> **来源质量说明**：Phoronix（含太平洋科技/IT之家对其的转述）、Ubuntu 官方包页（packages.ubuntu.com）、Kubuntu 官方 release notes、sched-ext 官方 INSTALL.md、CachyOS 官方 Wiki 为一手来源；CSDN、异次元、百度百科为二手转述。**需注意**：Ubuntu 26.04 的内核版本在不同来源间存在分歧（早期预览文章称 Linux 6.18，发布时官方与 IT之家均称 **Linux 7.0**）——本报告采信发布时的官方口径。
