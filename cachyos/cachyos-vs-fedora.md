# CachyOS vs Fedora 深度对比：结果、原因、以及"纯官方 Fedora 能复现多少"

- **调研日期**：2026-10-16
- **核心问题**：① 全面比较 ② 结果分析 ③ 差异的原因 ④ 差异为何**不突出** ⑤ **在没有第三方仓库的前提下，Fedora 能复现 CachyOS 的哪些优化策略？**
- **一句话结论**：CachyOS 更快是"**编译层**"的功劳；**Fedora 慢在"配置/打包层"**（Phoronix 实测其垫底源于两个可修复的打包决策，而非编译优化）。而 Fedora 官方仓库**连 scx-scheds 和 BORE 内核都没有**，所以在"调度器实验"这一层，Fedora 比 Arch 更受限。

---

## 0. 结论速览

| 问题 | 答案 |
|---|---|
| 谁更快？ | CachyOS。Phoronix 9950X 59 项：**CachyOS 第 2，Fedora Workstation 40 第 4** |
| Fedora 的"慢"来自哪？ | **不是编译优化，而是打包/配置**——Phoronix 在 Framework 13 Pro（Panther Lake）六发行版横评中 **Fedora 垫底**，根因是 **thermald + tuned-ppd 两个可修复的打包决策** |
| 结构性差异核心？ | Fedora 是 **x86-64 v1 基线**（v3 推迟至 ≥Fedora 46）；CachyOS 是 v3/v4/znver4 + LTO/PGO/BOLT |
| Fedora 反而更强的地方？ | **tuned 电源/性能档体系**（官方且默认）；**内核更新更快**（F45 = Linux 7.2） |
| 纯官方 Fedora 能复现多少？ | **约 12 项可复现**；但 **scx-scheds、BORE 内核、NVIDIA 驱动、全仓库 v3 重编译** 全部**必须走第三方**（COPR / RPM Fusion） |

---

## 1. 全面比较

| 维度 | CachyOS | Fedora |
|---|---|---|
| **上游** | Arch Linux（下游再发行） | 独立发行版（Red Hat 上游试验田） |
| **更新模型** | 滚动 | **6 个月一版** + 约 13 个月支持 |
| **指令集基线** | `v3` / `v4` / `znver4` | **`x86-64`（v1）**，v3 提案推迟至 **≥Fedora 46** |
| **编译优化** | LTO + PGO + BOLT + AutoFDO | **部分 LTO**（F33 起）；无 PGO/BOLT |
| **内核** | 自研 `linux-cachyos`（默认/BORE/EEVDF/BMQ/RT/LTS/Hardened/Server/deckify） | 上游 vanilla + Fedora 补丁，**版本最新**（F45 = Linux 7.2） |
| **调度器** | BORE / BMQ / sched-ext / RT | EEVDF；**内核已启用 sched-ext（`CONFIG_SCHED_CLASS_EXT=y`）但官方仓库无 scx 调度器包** |
| **包管理** | `pacman` + AUR（20 万+） | `dnf5` + COPR + Flatpak + RPM Fusion |
| **默认文件系统** | Btrfs + 快照 | **Btrfs（F33 起）+ swap-on-zram 默认** |
| **安全默认** | 常规 | **SELinux enforcing + firewalld**（默认开启） |
| **电源管理** | `game-performance` 脚本（调用 PPD） | **`tuned` + `tuned-ppd`（F41 起取代 PPD，官方且默认）** |
| **专有驱动** | **官方仓库内置预编译 NVIDIA 模块** | **官方仓库无 NVIDIA 专有驱动，需 RPM Fusion** |
| **安装器** | Calamares 图形 + CLI，17+ DE 可选 | Anaconda（WebUI），Workstation 默认 GNOME |
| **治理** | 社区小团队（约 9 人），无公司实体 | **Fedora 项目**（Red Hat 赞助，FESCo + 正式流程） |
| **典型用户** | 想省事 + 要性能 | 想稳定滚动在"半年一版"节奏、要企业级生态 |

**关系本质**：两者**没有任何血缘关系**——CachyOS 基于 Arch，Fedora 是独立 RPM 系。所以差异不只是"编译参数"，还包括**包管理体系、默认服务、安全策略**这些结构性因素。

---

## 2. 结果分析

### 2.1 Phoronix — Ryzen 9 9950X，6 发行版，59 项（2024-08-20）

| 排名 | 发行版 |
|---|---|
| 1 | Clear Linux |
| **2** | **CachyOS** |
| 3 | Arch Linux |
| **4** | **Fedora Workstation 40** |
| 5 | Ubuntu 24.10 Snapshot |
| 6 | Ubuntu 24.04 LTS |

- 第 1 名比第 6 名快 **16%**（全跨度）。
- **CachyOS 与 Fedora 之间隔了 Arch 一个名次**，实际差距通常在 **2–6%**。

### 2.2 Phoronix 2026-08 — Framework Laptop 13 Pro（Intel Panther Lake），六发行版 ★ 关键

| 文章 | 日期 |
|---|---|
| Benchmarking Six Linux Distributions On The Framework Laptop 13 Pro | 2026-08 |
| **Analyzing Fedora's Slow Performance On The Framework Laptop 13 Pro With Intel Panther Lake** | **2026-08-11** |
| Tuned-PPD Performance Regression Should Be Fixed With New Linux Kernel | 2026-08-26 |
| CachyOS Outperforming Windows 11, Slight Advantage Over Ubuntu… | 2026 年 |

**结论**：在最新的 Panther Lake 硬件上，**Fedora Workstation 排名垫底**。Phoronix 深入分析后指出，**根因不是编译优化，而是两个可修复的打包决策**：
1. **`thermald` 的问题**（散热/功耗策略未正确适配新硬件）
2. **`tuned` 与 `tuned-ppd` 电源守护进程的交互**导致性能被压制

→ 该回归预计**随新内核修复**。

> ⚠️ **这是理解"CachyOS vs Fedora"最重要的一条**：Fedora 的落后**主要来自配置层，而不是它缺少 v3 编译**。这同时也说明——**配置层的坑可以修，编译层的差距不能"修"**。

### 2.3 其他相关数据点

| 来源 | 数据 |
|---|---|
| Phoronix 2026-07 | Razer Blade 18 上 CachyOS 99 项赢 51 项（geomean 76.19 vs Win11 76.12） |
| Phoronix 2026-07-28 | AMD Ryzen AI 9 HX 470 上 **Windows 11 略微领先 Ubuntu 与 Fedora** |
| Phoronix 2026-03-12 | Ubuntu 26.04 相比 25.10，RTX 5090 游戏性能最高 **+12%（平均 +4.4%）** |

---

## 3. 差异的原因

### 3.1 编译层 —— CachyOS 的最大优势

| 项 | Fedora | CachyOS | 影响 |
|---|---|---|---|
| 指令集基线 | `x86-64`（**v1**） | `v3`/`v4`/`znver4` | **CPU 密集 2–8%** |
| LTO | 部分（F33 起） | 全栈 ThinLTO | 1–3% |
| PGO | 无 | 核心包 + 内核 AutoFDO | 1–4% |
| BOLT | 无 | 核心包 | 1–3% |

> Fedora 的 x86-64-v3 提案已在 2026 年被**推迟至至少 Fedora 46**，官方仓库**至今仍是 v1 基线**。

### 3.2 内核层 —— Fedora 部分占优，部分落后

| 项 | Fedora | CachyOS |
|---|---|---|
| 内核版本 | **最新**（F45 = Linux 7.2，上游优先） | 跟随 Arch（也很新） |
| 调度器 | EEVDF（原生）+ **sched-ext 已启用** | EEVDF 调参 / **BORE** / **BMQ** / RT |
| **scx 调度器包** | ❌ **官方仓库没有**（需 COPR） | ✅ 内置 |
| Tick rate | 常规 | **1000Hz** |
| 补丁集 | Fedora 补丁（面向企业/新硬件） | 15 个 topic 分支 + `CONFIG_CACHY` |

→ **Fedora 的内核更新，但"调度器可玩性"不如 CachyOS，甚至不如 Arch**（Arch 官方 extra 有 `scx-scheds`）。

### 3.3 配置/打包层 —— **Fedora 特有的坑（也是最可修复的）**

- **`tuned` + `tuned-ppd`**：Fedora 41 起用它们取代 `power-profiles-daemon`。这是**系统化的电源/性能档管理**（优势），但**与 `thermald` 的交互曾导致性能回归**（Phoronix 2026-08 实测）。
- **SELinux enforcing + firewalld + auditd**：默认开启，开销通常 **<1–2%**，但在 IO/系统调用密集负载上可测。
- **默认 GNOME + 更多后台服务**：相对 CachyOS 的精简默认有额外开销。

### 3.4 包生态层

| 项 | Fedora | CachyOS |
|---|---|---|
| 专有 NVIDIA | **需 RPM Fusion（第三方）** | 官方仓库内置预编译模块 |
| ZFS | 官方无，需第三方 | 官方预编译模块 |
| AUR 等价物 | COPR（第三方）+ Flatpak | AUR（原生） |

---

## 4. 差异"没突出"的原因

1. **Fedora 的内核其实更新**：F45 = Linux 7.2，上游优先策略让 Fedora 在**新硬件/新特性**上不落后——"内核红利"它也有。
2. **Fedora 从 F33 起已用部分 LTO**，并非"零优化"。
3. **Fedora 的落后主因是配置而非编译**：Phoronix 已证明其垫底源于 `thermald` / `tuned-ppd` 两个**可修复**问题——**能被修好的差距，就不是结构性差距**。
4. **SELinux / firewalld 的开销通常很小**（1–2% 量级），多数基准测不出来。
5. **瓶颈不在 CPU**（Amdahl 定律）：4K 游戏 GPU 受限、桌面受 IO/网络限制。
6. **软件版本差异被发行节奏抹平**：Fedora 半年一版 + 滚动内核，与 Arch 的"最新"差距不大。
7. **测量噪声同量级**：run-to-run 方差常有 1–3%。
8. **部分"优化"是取舍**：`max_performance`、激进电源档是**用功耗/续航换响应**。

---

## 5. 纯官方 Fedora（无第三方仓库）能复现哪些优化策略？

> **前提界定**："第三方仓库"指 **COPR / RPM Fusion / Terra** 等外部仓库。

### 5.1 ✅ 可以在纯官方 Fedora 上复现的（12 项）

| # | CachyOS 的优化策略 | 纯 Fedora 复现方法 | 来源 |
|---|---|---|---|
| 1 | **CPU 性能档 / 电源档** | `tuned-adm profile latency-performance`（低延迟）/ `throughput-performance`（吞吐）/ `accelerator-performance`（GPU） | **官方 `tuned`，且是 Fedora 默认**——**比 CachyOS 的 `game-performance` 脚本更系统** |
| 2 | **EEVDF 调参** | `kernel.sched_base_slice_ns`（默认 base slice 3ms） | 官方内核自带 |
| 3 | **抢占模型选择** | 内核 cmdline `preempt=full`（Fedora 内核为 PREEMPT_DYNAMIC） | 官方内核自带 |
| 4 | **全套 sysctl 调优** | `/etc/sysctl.d/99-cachy.conf`：swappiness、dirty_*、page-cluster=0、nmi_watchdog=0、file-max、max_map_count | 官方内核 |
| 5 | **I/O 调度器按设备分配** | udev 规则：HDD→`bfq`、SATA SSD→`mq-deadline`、NVMe→`kyber` | 三种都在官方内核 |
| 6 | **THP defrag = defer+madvise** | `tmpfiles.d` | 官方内核 |
| 7 | **zram + zstd** | `zram-generator`（官方）+ `/etc/systemd/zram-generator.conf`；**Fedora 自 F33 起已默认启用 swap-on-zram** | **官方仓库** |
| 8 | **NTSync** | `modprobe ntsync`（Linux 6.14 起主线） | 官方内核自带（模块） |
| 9 | **游戏运行时工具** | `dnf install gamemode mangohud goverlay` | **官方仓库**（已核实：gamemode **1.8.2** 在 F43/F44/F45；mangohud、goverlay 也在官方仓库） |
| 10 | **Btrfs 快照回滚** | `dnf install snapper` 或 `btrfs-assistant` | 官方仓库 |
| 11 | **SATA 链接电源 / hdparm** | udev 规则 + `hdparm -B 254 -S 0` | 官方仓库 |
| 12 | **音频 rtprio / PCI latency** | `/etc/security/limits.d/` + `setpci` 脚本 | 官方仓库 |

> **Fedora 的加分项**：第 1 条（`tuned`）在 Fedora 上是**官方、默认、有 profile 体系**的，比 CachyOS 的脚本式做法更规范；第 7 条（zram）Fedora **默认就已经开了**。

### 5.2 ❌ 无法在纯官方 Fedora 上复现的（10 项，均需第三方）

| # | CachyOS 的优化策略 | 为什么做不到 | 需要什么 |
|---|---|---|---|
| 1 | **全仓库 x86-64-v3 / v4 重编译** | 官方仓库是 **v1** 二进制；v3 提案推迟至 ≥Fedora 46 | COPR 或自建 |
| 2 | **LTO / PGO / BOLT 预编译包** | 属构建产物 | 同上 |
| 3 | **BORE 调度器内核** | **官方无 BORE**（非主线） | **COPR `kernel-cachyos-bore`** |
| 4 | **BMQ / RT-BORE 内核** | 同上 | COPR `kernel-cachyos-bmq` / `-rt-bore` |
| 5 | **sched-ext 调度器（`scx-scheds`）** | ⚠️ **已核实：Fedora 官方仓库（F43/F44/F45/Rawhide/EPEL）搜索结果均为 0** | **COPR**（如 `bieszczaders/kernel-cachyos-addons`） |
| 6 | **1000Hz + AutoFDO 内核** | 官方内核非 1000Hz，无 AutoFDO profile | COPR `kernel-cachyos`（1000Hz + BORE，含 GCC 与 LLVM-ThinLTO 两种构建） |
| 7 | **NVIDIA 专有驱动 / 预编译模块** | ⚠️ **Fedora 官方仓库不含 NVIDIA 专有驱动**（只有 nouveau） | **RPM Fusion** |
| 8 | **ZFS 支持** | 官方仓库不含 ZFS（许可原因） | 第三方仓库 |
| 9 | **CachyOS 专有工具链 / Proton-CachyOS** | 不在官方仓库 | COPR / 自建 |
| 10 | **ananicy-cpp** | 不在官方仓库 | COPR |

### 5.3 直接回答你的问题

> **Fedora 在"没有第三方仓库"的前提下，能复现 CachyOS 约 12 项"运行时/配置类"优化**——包括 **`tuned` 电源/性能档体系、EEVDF 参数、抢占模式、全套 sysctl、I/O 调度器分配、zram、THP、NTSync、Gamemode/MangoHud/Goverlay、Btrfs 快照**。
>
> **但 Fedora 官方仓库的"缺口"比 Arch 更大**，以下四项**必须走第三方**：
> 1. **全仓库 v3/v4 重编译**（v3 推迟至 ≥Fedora 46）
> 2. **BORE / BMQ 内核**（需 COPR）
> 3. **sched-ext 调度器包 `scx-scheds`**（⚠️ 官方仓库**完全没有**）
> 4. **NVIDIA 专有驱动**（需 **RPM Fusion**）

### 5.4 ★ Arch 与 Fedora 的关键差异（值得单独记住）

| 能力 | Arch 官方仓库 | Fedora 官方仓库 |
|---|---|---|
| `scx-scheds`（sched-ext 调度器） | ✅ **有**（extra） | ❌ **没有**（需 COPR） |
| NVIDIA 专有驱动 | ✅ **有**（extra） | ❌ 没有（需 RPM Fusion） |
| `tuned` 电源/性能档体系 | ❌ 没有（用 PPD） | ✅ **有且默认** |
| zram 默认启用 | ❌ 需自配 | ✅ **默认开启** |
| 指令集基线 | v1 | v1 |

**结论**：
- 想在 **Fedora** 上玩 **sched-ext / BORE** → **必须开 COPR**（好在 CachyOS 官方维护了一个 COPR：`CachyOS/copr-linux-cachyos`，提供 `kernel-cachyos`、`kernel-cachyos-bore`、`kernel-cachyos-bmq`、`kernel-cachyos-rt-bore`，含 GCC 与 LLVM-ThinLTO 两种构建）。
- 想在 **Fedora** 上要 **NVIDIA 专有驱动** → **必须开 RPM Fusion**。
- **Fedora 唯一"官方就能碾压 Arch"的一项是 `tuned` 性能档体系**——这是 Fedora 官方、默认、带 profile 的，CachyOS 只是用脚本调用 PPD。

---

## 6. 参考来源

- [Phoronix — Operating Systems 评测列表（含 Analyzing Fedora's Slow Performance / Benchmarking Six Linux Distributions On The Framework Laptop 13 Pro）](https://www.phoronix.com/reviews/Operating+Systems)
- [Phoronix — Fedora 分类（x86-64-v3 推迟至 Fedora 46 / Tuned-PPD 回归修复）](https://www.phoronix.com/linux/Fedora)
- [Phoronix — 新闻列表（Tuned-PPD Performance Regression / Fedora CoreOS To Enable systemd-oomd & zRAM）](https://www.phoronix.com/news)
- [IT之家 —《哪个 Linux 发行版最能发挥 AMD 锐龙 9 9950X 处理器实力？59 项实测》](https://www.ithome.com/0/790/322.htm)
- [Fedora Packages — scx-scheds 搜索（F43/F44/F45/Rawhide/EPEL 均为 0 结果）](https://packages.fedoraproject.org/search?query=scx-scheds)
- [Fedora Packages — gamemode 1.8.2（F43/F44/F45）](https://packages.fedoraproject.org/pkgs/gamemode/gamemode/)
- [Fedora Packages — mangohud](https://packages.fedoraproject.org/pkgs/mangohud/mangohud)
- [Fedora Packages — goverlay](https://packages.fedoraproject.org/pkgs/goverlay/goverlay)
- [Fedora Wiki — Releases/41/ChangeSet（tuned 取代 power-profiles-daemon）](https://fedoraproject.org/wiki/Releases/41/ChangeSet)
- [Fedora Wiki — Changes/Optimized Binaries for the AMD64 Architecture](https://fedoraproject.org/wiki/Changes/Optimized_Binaries_for_the_AMD64_Architecture)
- [Red Hat Bugzilla #2293665 — tuned / tuned-ppd 取代 power-profiles-daemon](https://bugzilla.redhat.com/show_bug.cgi?id=2293665)
- [GitHub — CachyOS/copr-linux-cachyos（Fedora 用 CachyOS 内核 COPR）](https://github.com/CachyOS/copr-linux-cachyos)
- [FossLinux — How to Fix Slow Fedora: A Beginner Performance Guide（Fedora 垫底的两个打包原因）](https://www.fosslinux.com/category/fedora)
- [什么值得买 —《Fedora 45 倒计时2个月：最受期待的优化来不及了》（x86-64-v3 延到 F46）](https://post.smzdm.com/p/a6zdpkz0/)
- [CachyOS 官方 Wiki — Why CachyOS?](https://wiki.cachyos.org/cachyos_basic/why_cachyos)
- [CachyOS 官方 Wiki — Kernel](https://wiki.cachyos.org/features/kernel)
- [tuned-profiles 手册（latency-performance / throughput-performance / accelerator-performance 定义）](https://www.mankier.com/7/tuned-profiles)
- [Fedora 33 发布公告（默认 Btrfs + zram + 更多 LTO）](http://baijiahao.baidu.com/s?id=1681718249930120337&wfr=spider&for=pc)
- [Linux Kernel 文档 — /proc/sys/kernel/](https://www.kernel.org/doc/html/latest/admin-guide/sysctl/kernel.html)

> **来源质量说明**：Phoronix、Fedora 官方包页（packages.fedoraproject.org）、Fedora Wiki、CachyOS 官方 Wiki、tuned 手册为一手来源；IT之家、什么值得买、FossLinux 为二手转述；CSDN 文章仅用于交叉验证细节。
