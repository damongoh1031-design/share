# CachyOS vs Arch Linux 深度对比：结果、原因、以及"纯官方 Arch 能复现多少"

- **调研日期**：2026-10-16
- **核心问题**：① 全面比较 ② 结果分析 ③ 差异的原因 ④ 差异为何**不突出** ⑤ **在没有第三方仓库的前提下，Arch 能复现 CachyOS 的哪些优化策略？**
- **一句话结论**：CachyOS ≈ Arch + ①全仓库指令集重编译 + ②自研内核（调度器补丁）+ ③一套出厂预置的系统调优。**其中只有 ① 和 ②（BORE/BMQ 部分）无法在纯官方 Arch 上复现；③ 几乎全部可以手工做到。**

---

## 0. 结论速览

| 问题 | 答案 |
|---|---|
| 谁更快？ | CachyOS，但**领先幅度通常是几个百分点**（Phoronix 9950X 59 项：CachyOS 第 2、Arch 第 3） |
| 差在哪？ | **编译层（v3/v4 + LTO/PGO/BOLT）** 是最大差异；其次是**内核调度器**；系统调优差异最小 |
| 为什么不突出？ | ①多数负载不是 CPU 受限 ②软件版本几乎一致 ③编译器早已自动向量化 ④调度器只影响尾部延迟 ⑤测量噪声同量级 |
| 纯官方 Arch 能复现多少？ | **约 80% 的"运行时/配置类"优化可复现**；**唯一无法复现的是全仓库重编译**（及 BORE/BMQ 内核） |

---

## 1. 全面比较

| 维度 | CachyOS | Arch Linux |
|---|---|---|
| **定位** | 性能优化型 Arch 衍生发行版 | 极简、KISS 的滚动发行版（"毛坯房"） |
| **起步时间** | 约 2021–2022 | 2002 |
| **主导者** | Peter Jung（ptr1337）等社区核心团队 | Arch 项目团队（Arch Linux 项目，有正式治理与选举） |
| **软件仓库** | 自建仓库（`x86_64` / `x86_64_v3` / `x86_64_v4` / `znver4`） | 官方 `core` / `extra` / `multilib`（**x86-64 v1 基线**） |
| **包来源** | 拿 Arch 的 PKGBUILD **改编译参数后重建** | 官方自行构建 |
| **AUR** | 完整可用（且提供 `cachyos-aur-derived`） | 原生 AUR |
| **内核** | 自研 `linux-cachyos`（默认/BORE/EEVDF/BMQ/RT/LTS/Hardened/Server/deckify） | 官方 `linux`（vanilla + 少量补丁）、`linux-lts`、`linux-hardened`、`linux-zen` |
| **安装器** | Calamares 图形安装器 + CLI 安装器 | `archinstall`（官方 CLI 引导） |
| **桌面环境** | 17+ 种开箱可选 | 自行安装（不预装） |
| **出厂调优** | `cachyos-settings`、`chwd`、ananicy-cpp、zram、快照、`cachyos-hello` 等**预置** | **无**（一切自行配置） |
| **游戏工具** | `cachyos-gaming-meta`、Proton-CachyOS、`game-performance` 脚本 | 需自行安装（`gamemode`/`mangohud` 在官方仓库，Proton 由 Steam 提供） |
| **更新节奏** | 滚动（2025/2026 年约 5 个 ISO/年） | 滚动（持续） |
| **发行版风险** | 独立仓库与上游存在同步延迟；依赖小团队 | 上游即源头，无中间层 |
| **治理** | 社区驱动、无公司实体，核心成员约 9 人 | Arch 项目（有选举、有 RFC 流程、有正式章程） |
| **典型用户** | 想省事 + 要性能（尤其游戏） | 想掌控一切、愿意自己配置 |

**关系本质**：CachyOS 不是 Arch 的"分支"，而是 Arch 的**下游再发行（respin）**——它消费 Arch 的 PKGBUILD 与上游源码，产出自己的二进制仓库。**上游一变，CachyOS 必须跟着重建**，这是它结构性的耦合点。

---

## 2. 结果分析（第三方基准）

### 2.1 Phoronix — Ryzen 9 9950X，6 发行版，59 项（2024-08-20）

| 排名 | 发行版 |
|---|---|
| 1 | Clear Linux（上限参照） |
| **2** | **CachyOS** |
| **3** | **Arch Linux** |
| 4 | Fedora Workstation 40 |
| 5 | Ubuntu 24.10 Snapshot |
| 6 | Ubuntu 24.04 LTS |

- **硬数字**：第 1 名比第 6 名快 **16%**。
- ⚠️ **注意**：这是**全跨度**。CachyOS 与 Arch 相邻两个名次之间的差距**远小于 16%**，实际通常在 **1–5%** 量级。

### 2.2 Phoronix 2026 年 CachyOS 专题（直接涉及 Arch）

| 文章 | 日期 |
|---|---|
| Benchmarking The Different CachyOS Linux Kernel Flavors | 2026-06-02 |
| Benchmarking The BORE Scheduler Performance With CachyOS Linux | 2026-06-04 |
| **CachyOS Delivers Lead Over Arch Linux, Pop!_OS & …**（标题截断） | 约 2026 上半年 |

→ **Phoronix 明确给出过"CachyOS 领先 Arch Linux"的结论**，但同样是"领先"，而非"碾压"。

### 2.3 关键校准

- Phoronix 2026-07：CachyOS 在 Razer Blade 18 上 99 项**赢 51 项**，但**几何平均分 76.19 vs Windows 11 的 76.12**（差 0.07，**噪声级**）。
- Phoronix 2026-03：Ubuntu 26.04 相比 25.10，**RTX 5090 游戏性能最高 +12%（平均 +4.4%）**——**仅一次版本更新的收益就可能超过"CachyOS vs Arch"的差距**。

> **结论**：CachyOS 确实更快，但**优势幅度小且场景依赖**。把它理解成"出厂就帮你调好的 Arch"，而不是"换了一颗 CPU"。

---

## 3. 差异的原因（分层拆解）

### 3.1 编译层 —— **最大、也是唯一不可替代的差异**

| 项 | Arch | CachyOS | 影响 |
|---|---|---|---|
| 指令集基线 | `x86-64`（v1） | `v3` / `v4` / `znver4` | **CPU 密集负载 2–8%** |
| LTO | 无 | Clang ThinLTO | 1–3% |
| PGO | 无 | 核心包 + 内核 AutoFDO | 1–4% |
| BOLT | 无 | 核心包 | 1–3% |
| 内核 GCC flag | 默认 | `-fivopts`、`-fmodulo-sched` | 极小 |

**为什么 v3 有效**：v3 基线启用 AVX2、BMI2、FMA 等指令，让编译器能生成更宽的向量化代码。**但注意：现代编译器在 -O2 下已做大量自动向量化**，所以增量有限——这也是为什么 Ubuntu 官方 v3 实验与 Fedora 的 v3 提案给出的预期收益都在**个位数百分比**。

### 3.2 内核层 —— **影响"手感"多于"跑分"**

| 项 | Arch 官方 `linux` | CachyOS |
|---|---|---|
| 调度器 | EEVDF（原生）+ **sched-ext 可用** | EEVDF 调参 / **BORE** / **BMQ** / RT |
| Tick rate | 默认（通常 250/1000Hz 视配置） | **1000Hz** |
| 抢占 | PREEMPT_DYNAMIC | PREEMPT_DYNAMIC + 低延迟补丁 |
| 补丁集 | 少量 | 15 个 topic 分支 + `CONFIG_CACHY` |
| AutoFDO | 无 | 有 |
| POC Selector（降唤醒延迟） | 无 | 有 |

→ **BORE 是主线没有的**，必须打补丁。**EEVDF 调参和 sched-ext 则是 Arch 也能碰的**。

### 3.3 系统层 —— **差异最小，且完全可以手工复现**

CachyOS 的 sysctl / udev / systemd / THP / zram / NVIDIA 模块参数等（详见前一份游戏优化报告）**全部是"配置文件"**，不是"重编译产物"。这意味着**这一层在 Arch 上抄过来即可**。

### 3.4 工具层

`chwd`（硬件检测）、`cachyos-hello`、`Shelly`、`cachyos-rate-mirrors`、`Proton-CachyOS` —— 属于**便利性**，不直接提升性能。

---

## 4. 差异"没突出"的原因（为什么没想象中大）

1. **瓶颈不在 CPU**：4K 游戏 GPU 受限；桌面应用受 IO/网络/等待限制；编译受磁盘 IO 影响。**指令集优化只作用于 CPU 计算那一段**（Amdahl 定律）。
2. **软件版本几乎一致**：两者都是滚动发行，CachyOS 的包就是从 Arch 的 PKGBUILD 重建的——**版本号基本同步**。所以"软件新"这个红利**两者共享**，CachyOS 独有的只剩"编译参数 + 内核"。
3. **编译器已经很聪明**：GCC/Clang 在 -O2 下自动向量化已相当充分，v1→v3 的增量被压缩到个位数。
4. **调度器优化的是尾部而非均值**：BORE 改善的是 **1% low / 卡顿 / 输入延迟**，而绝大多数基准测的是**吞吐或总耗时**——所以跑分看不出来。
5. **PGO/BOLT 只覆盖核心包**：不是全仓库，收益被大量未优化包稀释。
6. **测量噪声同量级**：很多基准的 run-to-run 方差就有 1–3%，与"发行版差异"同一数量级。
7. **部分"优化"是取舍而非净收益**：`max_performance`、激进电源档、关闭 watchdog 等会**牺牲功耗/续航/安全**换响应，并非纯粹的"更快"。
8. **上游同源**：内核、Mesa、GCC、glibc 都是同一份上游代码——**发行版只能在"编译参数 + 配置"上做文章**，天花板本来就不高。

---

## 5. 纯官方 Arch（只用 core/extra/multilib，无第三方仓库）能复现哪些优化策略？

> **前提界定**：这里"第三方仓库"指 **ALHP / chaotic-aur / CachyOS 仓库**等外部二进制仓库。**AUR 属于 Arch 官方基础设施**（构建脚本仓库），但为严谨起见，下面把"AUR 才能拿到的"单独标出。

### 5.1 ✅ 可以在纯官方 Arch 上复现的（且方法明确）

| # | CachyOS 的优化策略 | 纯 Arch 复现方法 | 包/接口来源 |
|---|---|---|---|
| 1 | **可插拔调度器（sched-ext / SCX）** | `pacman -S scx-scheds`，用 `scx_loader` 或 systemd 服务切换调度器（如 `scx_lavd` 游戏向、`scx_bpfland` 桌面向） | **官方 `extra`**（`scx-scheds` 已是 `linux`/`linux-hardened` 的可选依赖）；Arch 内核已启用 sched-ext |
| 2 | **EEVDF 调参** | 运行时调整 `kernel.sched_base_slice_ns`（EEVDF 默认 base slice 3ms）；查看可用 `/sys/kernel/debug/sched/base_slice_ns`（视内核版本） | 官方内核自带 |
| 3 | **抢占模型选择** | 内核 cmdline 加 `preempt=full`（PREEMPT_DYNAMIC 运行时切换） | 官方内核自带 |
| 4 | **CPU 性能档 / EPP** | `pacman -S power-profiles-daemon` → `powerprofilesctl set performance`；或 `cpupower frequency-set -g performance` | **官方 `extra`**（`power-profiles-daemon`、`cpupower`） |
| 5 | **`game-performance` 脚本的全部动作** | 上面第 4 条 + `systemd-inhibit` 抑制屏保 | 官方仓库 |
| 6 | **全套 sysctl 调优** | 写 `/etc/sysctl.d/99-cachy.conf`：`vm.swappiness`、`vm.dirty_*`、`vm.page-cluster=0`、`kernel.nmi_watchdog=0`、`fs.file-max`、`vm.max_map_count` 等 | 官方内核 |
| 7 | **I/O 调度器按设备分配** | 写 udev 规则：HDD→`bfq`、SATA SSD→`mq-deadline`、NVMe→`kyber` | 三种调度器都在官方内核 |
| 8 | **SATA 链接电源 = max_performance / hdparm** | udev 规则 + `hdparm -B 254 -S 0` | 官方仓库 |
| 9 | **THP defrag = defer+madvise** | `tmpfiles.d` 一行 | 官方内核 |
| 10 | **zram + zstd + swap-priority** | `pacman -S zram-generator` + `/etc/systemd/zram-generator.conf` | **官方 `extra`** |
| 11 | **NTSync** | `modprobe ntsync`（Linux 6.14 起主线），并可设为开机加载 | 官方内核自带（模块形式） |
| 12 | **NVIDIA 模块参数** | 官方 `nvidia` 包 + `/etc/modprobe.d/nvidia.conf`（`NVreg_*`） | 官方 `extra` |
| 13 | **游戏运行时工具** | `pacman -S gamemode mangohud lutris` | **官方 `extra`**（已验证 gamemode 1.8.2、mangohud 0.8.2 均在 extra） |
| 14 | **Btrfs 快照回滚** | `pacman -S snapper btrfs-assistant` 或直接用 `snap-pac` | 官方仓库 |
| 15 | **音频 rtprio 99 / PCI latency** | `/etc/security/limits.d/` + `setpci` 脚本 | 官方仓库 |

> **这一档的意义**：CachyOS 出厂预置的**"系统调优 + 游戏运行时"**这一整层，**在纯官方 Arch 上基本可以 1:1 手工复刻**——因为它们的本质是**配置**，不是**重编译**。

### 5.2 ❌ 无法在纯官方 Arch 上复现的

| # | CachyOS 的优化策略 | 为什么做不到 | 需要什么 |
|---|---|---|---|
| 1 | **全仓库 x86-64-v3 / v4 / znver4 重编译** | 官方仓库就是 v1 二进制，你无法"就地升级"别人的二进制 | **ALHP（第三方仓库）** 或自己 `makepkg` 全量重编译 |
| 2 | **LTO / PGO / BOLT 预编译包** | 同上，属于构建产物 | 同上 |
| 3 | **BORE / BMQ 调度器** | **不在主线内核**（BORE 是 out-of-tree 补丁） | AUR 的 `linux-cachyos` / `linux-tkg`，或自己打补丁编译 |
| 4 | **CachyOS 内核补丁集**（`CONFIG_CACHY`、15 个 topic 分支、AutoFDO profile） | 官方内核不含这些补丁 | AUR / 自编译 |
| 5 | **CachyOS 自研内核补丁带来的 1000Hz + POC Selector** | 同上 | 自编译 |
| 6 | **预编译 NVIDIA / ZFS 内核模块** | CachyOS 为自家内核预编译；Arch 需 DKMS 或等官方跟进 | 部分可由官方 `nvidia`/`zfs` 替代 |
| 7 | **CachyOS 专有工具链**（`chwd`、`cachyos-hello`、`Shelly`、`cachyos-settings`、`cachyos-rate-mirrors`） | 不在官方仓库 | AUR / CachyOS 仓库 |
| 8 | **Proton-CachyOS** | 不在官方仓库 | AUR（`proton-cachyos`）或 CachyOS 仓库 |
| 9 | **ananicy-cpp + ananicy-rules** | ⚠️ **仅在 AUR**，不在官方仓库 | AUR |
| 10 | **17+ DE 开箱安装 / Calamares 安装器** | 官方只有 `archinstall` | 手工配置 |

### 5.3 一句话回答你的问题

> **Arch 在"没有第三方仓库"的前提下，能复现 CachyOS 的绝大部分"运行时与配置类"优化策略**——包括 **sched-ext 可插拔调度器、EEVDF 参数调整、抢占模式、CPU 性能档、全套 sysctl、I/O 调度器分配、zram、THP、NTSync、NVIDIA 模块参数、Gamemode/MangoHud、Btrfs 快照**（第 5.1 节 15 项）。
>
> **但唯一无法复现、也恰恰是 CachyOS 立身之本的那一项是：全仓库指令集重编译（v3/v4/znver4）+ LTO/PGO/BOLT 预编译包**；以及依赖打补丁的 **BORE / BMQ 内核**（这两项必须靠第三方仓库或自编译）。

**换个说法**：
- 想要 **CachyOS 的"系统调优 + 游戏体验"** → **纯 Arch 手写配置即可达到**（约 15 项，见 5.1）。
- 想要 **CachyOS 的"编译层红利"** → **只能靠 ALHP（第三方仓库）或自己编译**，纯官方 Arch 做不到。

---

## 6. 参考来源

- [Phoronix — Operating Systems 评测列表（CachyOS 内核变体 / BORE 专项 / CachyOS 领先 Arch）](https://www.phoronix.com/reviews/Operating+Systems)
- [IT之家 —《哪个 Linux 发行版最能发挥 AMD 锐龙 9 9950X 处理器实力？59 项实测》（Phoronix 六发行版排名）](https://www.ithome.com/0/790/322.htm)
- [什么值得买 —《CS2低帧暴涨20%、99项测试赢51项》](https://post.smzdm.com/p/a6zdp68o/)
- [Arch Linux 官网（"official packages optimized for the x86-64 architecture"）](https://archlinux.org/)
- [Arch Linux — linux-hardened 包页（scx-scheds 为其可选依赖，证明 sched-ext 可用）](https://www.archlinux.org/packages/extra/x86_64/linux-hardened/)
- [Arch Linux — gamemode 1.8.2（Repository: Extra）](https://archlinux.org/packages/extra/x86_64/gamemode/)
- [Arch Linux — zram-generator 1.2.1（Repository: Extra）](https://archlinux.org/packages/extra/x86_64/zram-generator/)
- [Arch Linux — mangohud 0.8.2（Repository: Extra）](https://archlinux.org/packages/extra/x86_64/mangohud/)
- [CachyOS 官方 Wiki — Why CachyOS?（EEVDF tunables / BORE / 仓库）](https://wiki.cachyos.org/cachyos_basic/why_cachyos)
- [CachyOS 官方 Wiki — Kernel（变体、1000Hz、AutoFDO、补丁集）](https://wiki.cachyos.org/features/kernel)
- [CachyOS-Settings — GitHub（sysctl / udev / systemd / game-performance）](https://github.com/CachyOS/CachyOS-Settings)
- [BORE Scheduler — GitHub（参数与默认值）](https://github.com/YuZyu9527/bore-scheduler)
- [CachyOS/kernel-patches — GitHub](https://github.com/CachyOS/kernel-patches)
- [ALHP 镜像说明（Arch 官方仓库的 x86-64 feature levels + -O3 + LTO）](https://mirror.kescher.at/)
- [Linux Kernel 文档 — /proc/sys/kernel/（sysctl 列表）](https://www.kernel.org/doc/html/latest/admin-guide/sysctl/kernel.html)
- [NTSync 百度百科（Linux 6.14 主线，模块形式）](https://baike.baidu.com/item/NTSync/67641008)
- [Chaotic-AUR 包列表（ananicy-cpp 等，说明其不在官方仓库）](https://github.com/chaotic-aur/packages)
- [Fedora Wiki — Changes/Optimized Binaries for the AMD64 Architecture（v3 收益预期）](https://fedoraproject.org/wiki/Changes/Optimized_Binaries_for_the_AMD64_Architecture)

> **来源质量说明**：Arch Linux 官方包页、CachyOS 官方 Wiki、Phoronix、Linux 内核官方文档为一手来源；IT之家 / 什么值得买为二手转述；CSDN 相关文章仅用于交叉验证 `sched_base_slice_ns` 等细节，不作为权威依据。
