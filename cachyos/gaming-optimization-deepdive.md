# CachyOS 游戏优化深度剖析：优化项 / 参数值 / 目的 / 证据 / Phoronix 评测公平性

- **调研日期**：2026-10-16
- **聚焦问题**：游戏优化到底做了什么？怎么优化？优化了哪些具体数值？目的是什么？效果证据有多少？Phoronix 有几篇评测？评测条件是否公平全面？
- **结论先行**：优化项**真实、可核查**（全部代码/配置在 GitHub 公开）；"优化了什么数值"可以**精确回答**（BORE 参数、sysctl、tick rate、IO 调度器分配等）；但"效果证据"链条中，**最强的一环是 Phoronix 的综合基准，而它在方法学上存在明显混杂变量（confounder）**；**游戏专项证据反而最薄弱**，主要来自个人 UP 主的单样本测试。

---

## 一、游戏优化清单：到底做了什么

CachyOS 的"游戏优化"不是单一开关，而是**四层叠加**。下面按层拆解。

### A. 编译层 —— 让 CPU 少空转

| 优化项 | 做法 |
|---|---|
| 全仓库重编译 | 整个软件仓库按 `x86-64-v3` / `x86-64-v4` / `znver4` 指令集重建，而非使用 Arch 的通用二进制 |
| LTO | Clang **ThinLTO**，默认在主包 `linux-cachyos` 启用；支持分布式 ThinLTO 加速构建 |
| PGO | 核心包启用 PGO；内核用 **AutoFDO**（类 PGO 的采样优化） |
| BOLT | 核心包额外做 BOLT 后链接优化 |
| GCC 高级 flag | `-fivopts`、`-fmodulo-sched` |
| kCFI | 使用 LLVM 时可选内核控制流完整性（安全向，非性能向） |

> **目的**：现代指令集 + 跨函数优化，让编译器生成更紧凑、更少分支预测失败的代码 → **减少 CPU 空转**，收益自然落在**吃 CPU 的场景**（1080p/2K、竞技网游、模拟类）。

### B. 内核层 —— 降低调度延迟与抖动

| 优化项 | 做法 / 数值 |
|---|---|
| 调度器可选 | `EEVDF`（默认，含 CachyOS 自有 tunables）/ `BORE` / `BMQ`（Project C）/ `RT-BORE`（实时） |
| sched-ext (SCX) | 用户态可插拔调度器（BPF），`scx_loader` 管理，可运行时切换；**与 BMQ 变体不兼容** |
| Tick rate | 默认 **1000Hz**；可选 100 / 250 / 300 / 500 / 600 / 750 / 1000 Hz |
| 抢占模型 | **PREEMPT_DYNAMIC**（full / lazy / voluntary / none 运行时可选） |
| POC Selector | 类 `scx_cake` 的 **Piece-Of-Cake** 快速空闲 CPU 选择器，**降低唤醒延迟** |
| `sched/wait LIFO accept()` | socket accept() 按 LIFO 处理，改善缓存效率 |
| MGLRU + "Cachy Sauce" MM 调参 | LRU-gen 工作集保护、compaction/watermark 调整、hugepage 回收 |
| I/O 调度器 | 增强 BFQ 与 mq-deadline；集成 **ADIOS v3.2.0** 多队列 I/O 调度器 |
| VRAM cgroup (DMEM) | DRM 子系统设备内存控制器，可按 cgroup 限制显存占用 |
| 补丁集 | Linux 7.1 基线合并 **15 个 topic 分支**：`amd-isp4`、`bbr3`、`cachy`、`cgroup-vram`、`drm-fair`、`hdmi`、`lenovo-wmi`、`mglru`、`preempt-ipi`、`sched-cluster`、`snd-codecs`、`t2`、`vesa-dsc-bpp` 等 |
| 游戏硬件适配 | Steam Deck 补丁（Audio / HW Quirks / HID）、ROG Ally、MSI Claw HID（deckify） |
| 显示相关 | HDR 启用、AMDGPU `amdgpu_ignore_min_pcap`、AMD 上 HDMI VRR、ALLM 与被动 VRR connector 属性 |

> **目的**：把"游戏卡顿"的来源——**调度延迟、唤醒延迟、内存回收抖动、I/O 排队**——逐项压掉。

### C. 系统层 —— 具体数值（这是"优化什么数值"的核心）

以下数值来自官方 `CachyOS-Settings` 仓库（README 明示）：

**sysctl 内核运行时参数**
- `vm.swappiness = 100`（启动时）；**ZRAM 初始化时提升到 150，并关闭 Zswap**（让匿名页走压缩而非从 page cache 刷出）
- `vm.vfs_cache_pressure`、`vm.dirty_bytes`、`vm.dirty_background_bytes`、`vm.dirty_writeback_centisecs`（平衡内存与磁盘 I/O）
- **禁用** `vm.page-cluster`
- **禁用** `kernel.nmi_watchdog`（减少干扰）
- 启用 `kernel.unprivileged_userns_clone`；限制 `kernel.kptr_restrict`
- `kernel.printk` 隐藏控制台消息；提高 `net.core.netdev_max_backlog`；设置 `fs.file-max`

**udev / 设备级**
- **I/O 调度器按设备类型分配**：HDD → `bfq`；SATA SSD / eMMC → `mq-deadline`；NVMe SSD → `kyber`
- SATA host link power management → **`max_performance`**
- HDD 应用 `hdparm -B 254 -S 0`（禁用 APM 降速与待机）
- 音频：`snd-hda-intel` 省电策略随供电切换（AC 时关闭，避免爆音）
- 设备权限：`rtc0` / `hpet` 归入 `audio` 组；开放 `cpu_dma_latency`

**systemd / 资源**
- ZRAM：`zstd` 压缩、`swap-priority=100`
- `DefaultLimitNOFILE`：system `2048:2097152`，user `1024:1048576`
- 服务超时：`DefaultTimeoutStartSec=15s`、`DefaultTimeoutStopSec=10s`；journald 上限 50MB
- 用户服务资源委托（CPU / cpuset / IO / memory / pids）
- 开机加载 **`ntsync`** 内核模块（Windows 同步原语，替代 esync/fsync 的新方案）

**THP（透明大页）**
- `transparent_hugepage/defrag` → **`defer+madvise`**（面向使用 tcmalloc 的应用）
- `khugepaged/max_ptes_none`（6.12+，优化 THP 内存占用）

**NVIDIA 专有模块参数（modprobe）**
- `NVreg_InitializeSystemMemoryAllocations=0`（跳过 GPU 分配的内存清零）
- `NVreg_DynamicPowerManagement=0x02`（移动 GPU 省电）
- `NVreg_EnableS0ixPowerManagement=1`（支持的笔记本上 S0ix 空闲省电）

**延迟/优先级**
- 音频：`@audio` 组 `rtprio 99`
- `pci-latency` 脚本：声卡 PCI latency timer 设为 **80 cycles**
- `limits.d` 增加 nice 值配置
- `game-performance` 脚本：启动应用时通过 `powerprofilesctl` 切到 **performance** 电源档，并默认抑制屏保（`GAME_PERFORMANCE_SCREENSAVER_ON=1` 可跳过）

> **目的**：把电源档、I/O 队列、内存回收、GPU 内存分配、同步原语这些"游戏外"的干扰项调到低延迟状态。

### D. 游戏运行时层 —— 兼容与画质/延迟特性

| 组件 | 内容 |
|---|---|
| `cachyos-gaming-meta` | GameScope、GOverlay、Heroic Games Launcher、Lutris、MangoHud、Steam 一键装 |
| `cachyos-gaming-applications` | 额外游戏工具与商店插件 |
| `Proton-CachyOS` | 基于 Proton 前沿分支 + Wine-Staging 补丁；集成全屏 FSR、视频/音频解码器（避免过场黑屏）、UMU-Launcher / UMU-ProtonFixes；优先用系统原生库编译（减少冲突） |
| FSR 4 | 环境变量 `PROTON_FSR4_UPGRADE=1` 自动下载并应用最新 FSR 4 DLL |
| OptiScaler | `PROTON_USE_OPTISCALER` 改为默认下载 DLSS DLL，向 FSR4 开放 DLSS 输入 |
| NVIDIA Reflex | 通过 `vkd3d-low-latency` 实现（2026-07 更新） |
| AMD Anti-Lag 2 | 2025-07 起整合进 `mesa-git` |
| Wayland 原生 | `PROTON_ENABLE_WAYLAND=1`；HDR：`PROTON_ENABLE_HDR=1`（实验性） |
| NTSync | `PROTON_USE_NTSYNC=1` |
| DLSS | `dlss-swapper` / `dlss-swapper-dll` 强制最新 DLSS 预设（SR / RR / FG） |
| 手持设备 | `cachyos-handheld` 包 + `linux-cachyos-deckify` 内核（手持设备**唯一受支持**内核） |

> **目的**：把"能跑"和"跑得好"补齐——**兼容性**（反作弊/解码器/启动器）+ **画质升频**（FSR4/DLSS）+ **输入延迟**（Reflex / Anti-Lag 2 / NTSync）。

---

## 二、BORE 调度器：优化了什么数值（完整参数表）

这是"优化什么数值"最硬的答案。BORE（Burst-Oriented Response Enhancer）由 **firelzrd** 开发，CachyOS 深度参与测试。其核心思路：**给每个任务算一个"突发度（burstiness）"分数，分数越低（越不贪 CPU）的任务获得更长的时间片与更激进的唤醒抢占。**

**机制**：跟踪任务自上次 yield / sleep / IO-wait 以来消耗的 CPU 时间（burst time）→ 取 bit count → 用 offset 与 coefficient 调整 → 得到 **0–39 的 burst score**（类似 niceness）。**分数每降低 1，可消耗的时间片约变为 1.25 倍。**

| 参数 | 范围 | 默认值 | 作用 |
|---|---|---|---|
| `sched_bore` | 0–1 | **1** | 启用 / 关闭 BORE 机制 |
| `sched_burst_cache_lifetime` | 0–4294967295 | **60000000**（ns，60ms） | fork 时计算的平均 burst time 缓存时长 |
| `sched_burst_fork_atavistic` | 0–3 | **2** | 祖先进程 burst time 继承（拓扑 hub/stub 树）；对大量 fork 场景（如内核编译）提升响应性 |
| `sched_burst_penalty_offset` | 0–64 | **22** | 计算 burst score 时从 burst time bit count 中减去的位数；越大则短突发任务越不被"过强" |
| `sched_burst_penalty_scale` | 0–4095 | **1280**（即 1.25x） | 按 burst time 比例区分任务的强度 |
| `sched_burst_smoothness_long` | 0–1 | **1** | 长时平滑（抑制突发尖峰） |
| `sched_burst_smoothness_short` | 0–1 | **0** | 短时平滑（0 = 不平滑） |
| `sched_burst_exclude_kthreads` | 0–1 | **1** | 1 = 仅对非内核任务生效 |
| `sched_burst_parity_threshold` | u8 | **2** | runqueue 任务数超过该值时自适应关闭 `RUN_TO_PARITY` |
| `sched_deadline_boost_mask` | u32 | `ENQUEUE_INITIAL \| ENQUEUE_WAKEUP` | 以此标志入队时 deadline 减半 |

> **目的**：在"吞吐"与"响应性"之间偏向后者——**保证前台/交互任务（游戏、输入）优先获得 CPU**，代价是批处理任务权重下降。

---

## 三、优化的目的是什么（目标拆解）

| 目标 | 对应手段 |
|---|---|
| 减少 CPU 空转、提高 IPC | 全仓库 v3/v4/znver4 重编译、LTO/PGO/BOLT、AutoFDO |
| 降低调度延迟与抖动 | BORE / EEVDF 调参 / sched-ext、1000Hz tick、PREEMPT_DYNAMIC、POC Selector |
| 让游戏/前台优先 | BORE burstiness、ananicy-cpp 规则、`game-performance` 切 performance 档、nice 值 |
| 降低输入延迟 | AMD Anti-Lag 2、NVIDIA Reflex（vkd3d-low-latency）、NTSync |
| 减少 I/O 与内存抖动 | IO 调度器按设备分配、MGLRU、zram zstd、dirty 参数、THP 调优 |
| 提升兼容性（"能跑"） | Proton-CachyOS、deckify 内核、Steam Deck / ROG Ally / MSI Claw 补丁、反作弊修复 |
| 提升画质/帧率（低配） | FSR4 自动升级、OptiScaler、GameScope + FSR 缩放、DLSS 预设强制 |

**一句话**：目标是**把"尾部表现"（卡顿瞬间、输入延迟）拉平**，而不是提高平均帧上限——这也解释了为什么**收益主要体现在 1% low 而非平均帧**。

---

## 四、效果证据：有多少？强度如何？

### 4.1 强证据（第三方、方法透明）

| 指标 | 数值 | 条件 | 强度 |
|---|---|---|---|
| Phoronix 三系统横评 | **99 项中 CachyOS 赢 51 项**（Windows 11 约 38 项，Ubuntu 约 10 项） | Razer Blade 18（$5399），同一台机器，2026-07-15 | 中高 |
| 几何平均分 | **CachyOS 76.19 / Windows 11 76.12 / Ubuntu 26.04 LTS 更低** | 同上 | **低**（差 0.07，噪声级） |

> ⚠️ 注意口径：**"赢 51 项"≠"领先 51%"**，且 99 项混合编译、渲染、模拟、AI 负载，**不是游戏专项**。

### 4.2 中等证据（社区实测，单样本）

| 指标 | 数值 | 条件 |
|---|---|---|
| CS2 低帧 | **1% low 比 Windows 11 高约 20%** | i7-13700KF + RTX 5090，KDE Wayland + NVIDIA 610 驱动，1080p/2K |
| 11 款游戏平均帧 | Linux 侧平均**比 Win11 高约 6.4%** | RX 5700 XT（A 卡老将），Linux 7.2.6 + Mesa 26.2.3 |
| Minecraft | 社区声称"提升 30%"乃至"接近 Windows 两倍" | 个人测试，无对照披露 |

### 4.3 弱证据 / 存疑

- **"相比 Nobara / Garuda 有 10–15% FPS 提升，并已在 ProtonDB 统计中验证"**（来源为 CSDN 转载笔记）→ **该说法不成立**：ProtonDB 是玩家兼容性上报平台，**不提供对照基准测试**，无法"验证"帧率提升幅度。此条应视为营销式表述。
- **官方 AutoFDO 内核优化**：有专门的官方博客（2411）说明方法，但**给出的主要是"优化方法"而非独立可复现的对照数字**。
- **反证**：Phoronix 在同一台 Razer Blade 18 上的**本地 AI 推理**测试中，**Windows 11 大幅领先**（有报道称 3.4 倍）——说明优化并非"全面碾压"，而是**场景特定**。

### 4.4 证据链的结构性问题

1. **游戏专项测试几乎都来自个人 UP 主**（单样本、单机型、多为高端 N 卡）。
2. **平均帧提升有限，宣传的是 1% low**；两者混用容易造成误解。
3. **收益与场景强相关**：CPU 受限（1080p/2K、竞技网游、模拟类）收益大；**4K 下 GPU 成为瓶颈，优势明显收窄**（社区原话："到 4K 显卡压力上来优势就没了"）。
4. **归因困难**：Linux 游戏收益的大头来自 **Proton / 驱动 / 上游内核**，任何发行版都能吃到；CachyOS 独有的只是"编译优化 + 调度器调校"那一层。

---

## 五、Phoronix 到底有多少 CachyOS 评测？

### 5.1 已确认的 Phoronix 相关评测（至少 3–4 篇）

| # | 主题 | 时间 | 内容 |
|---|---|---|---|
| 1 | **CachyOS 内核变体横评** | 约 2025-11 | 对比 CachyOS 的多个内核风味（默认 / hardened / 其他），"从 hardened 内核的性能开销到其他有趣的性能结论" |
| 2 | **BORE 内核专项评测** | 承接上一篇 | 原文："One kernel flavor I hadn't tested though was their build with the BORE scheduler. Given the interest and feedback from Phoronix readers, here is an article focused on…"——即**应读者要求单独评测 BORE 构建** |
| 3 | **Ubuntu 26.04 LTS vs Windows 11 vs CachyOS** | **2026-07-15** | Razer Blade 18（$5399），**99 项**跨系统对比 |
| 4 | Q3 2026 汇总 | 2026-09-30 | "More AI In Open-Source, CachyOS, Ryzen AI Halo, Framework Laptop 13 Pro & Other Q3 Hits"——季度盘点中提及 |

> **说明**：Phoronix 站内列表页/搜索页在本次抓取中未能完整渲染，以上为**可确证**的部分。可以确定的是：**Phoronix 对 CachyOS 的评测以"内核变体/调度器"为主（≥2 篇），跨发行版横评为 1 篇（99 项）**。目前**没有**找到 Phoronix 专门做"CachyOS 游戏帧率"的评测。

### 5.2 评测条件是否公平、全面？

**公平的部分 ✅**
- **同一台硬件、同一时段、同一测试套件**（Phoronix Test Suite），控制住了硬件变量。
- **公开原始数据**（OpenBenchmarking.org），可复核。
- **内核变体横评隔离了调度器变量**（BORE vs EEVDF vs hardened），这是方法学上最干净的一组。

**不够公平 / 不够全面的部分 ❌**

| 问题 | 说明 |
|---|---|
| **单一机型** | 仅 Razer Blade 18（高端 Intel + NVIDIA），无法外推到 AMD 平台、中低端机、掌机 |
| **版本混杂（关键 confounder）** | CachyOS 用的是**更新的内核 + 更新的 Mesa/驱动**，而 Ubuntu 26.04 是 **LTS 快照**。差异**不完全来自"发行版优化"**，也来自"软件版本更新"——这与"CachyOS 的优化值多少帧"是两个问题 |
| **负载构成偏科** | 99 项含编译、渲染、模拟、AI 等，**纯游戏项占比低**，不能直接回答"游戏快多少" |
| **统计口径** | "51/99 胜"是**胜项数**；geomean 76.19 vs 76.12 **差 0.07，属噪声级**，不足以支撑"显著更快" |
| **缺少帧时间分析** | Phoronix Test Suite 多数项目是吞吐/耗时型，**不是帧生成时间 / 1% low 分析**；而 CachyOS 的收益恰恰主要在 1% low |
| **单次运行** | 未披露重复运行次数与置信区间 |
| **未做归因拆解** | 未把"编译优化 / 调度器 / 内核版本 / 驱动版本"各自的贡献度分离（仅内核横评那篇部分做到了） |
| **未覆盖 4K** | 未系统覆盖 4K 等 GPU 瓶颈场景（而该场景恰恰是 CachyOS 优势消失的地方） |

### 5.3 评价

> Phoronix 的评测在**"跨系统整体性能"**这一命题上方法严谨、可复核，是当前**最可靠的第三方证据**；但它**不能作为"游戏优化有效"的直接证据**——它既没有做游戏帧率/帧时间专项，也存在"新版内核+新驱动"对"LTS 快照"的混杂变量。
>
> **结论**：想验证"CachyOS 游戏优化值多少帧"，目前**没有高质量、多机型、控制变量的公开评测**。最靠谱的做法是**自己在目标机型上用同一游戏、同一画质、记录 1% low 与帧时间**做 A/B 对照。

---

## 六、总结

| 问题 | 回答 |
|---|---|
| 做了什么优化？ | 四层叠加：编译层（v3/v4/znver4 + LTO/PGO/BOLT）、内核层（BORE/EEVDF/SCX、1000Hz、PREEMPT_DYNAMIC、MGLRU、ADIOS）、系统层（sysctl/IO 调度器/ZRAM/THP/NVIDIA 模块参数）、运行时层（Proton-CachyOS、FSR4、Reflex、NTSync） |
| 如何优化？ | 编译期做指令集与跨函数优化；运行期用调度器把 CPU 优先给交互任务；系统层把电源/IO/内存回收调到低延迟；运行时层补齐兼容与画质升频 |
| 优化什么数值？ | **可精确列举**：BORE 10 个参数（含 `sched_burst_penalty_offset=22`、`penalty_scale=1280`、burst score 0–39、每 -1 约 1.25x 时间片）、tick 1000Hz、`vm.swappiness=100`（ZRAM 150）、NOFILE、IO 调度器按设备分配、NVIDIA `NVreg_*` 等 |
| 目的是什么？ | 压掉延迟与抖动，优先保障**尾部表现（1% low / 输入延迟）**，而非提高平均帧上限 |
| 效果证据多少？ | 强：Phoronix 99 项/51 胜（但混杂变量）；中：CS2 1% low +20%、RX 5700 XT 平均 +6.4%；弱/存疑："10–15% FPS、ProtonDB 验证"（不成立）；反证：同机 AI 推理 Windows 胜、4K 优势消失 |
| Phoronix 几篇？ | 可确证 **≥3 篇**：内核变体横评、BORE 内核专项、三系统 99 项横评（另有季度汇总提及） |
| 评测公平全面吗？ | **部分公平**（同机同套件、公开数据、内核横评隔离了调度器）；**不够全面**（单机型、版本混杂、游戏项少、无帧时间、无 4K、单次运行、未做归因拆解） |

**最诚实的结论**：CachyOS 的优化**工程上是真实且可审计的**（参数都在 GitHub），但**"游戏帧率提升多少"这件事目前缺乏高质量公开证据**。宣传中的"20%""翻倍"等数字均来自单样本个人测试或未经证实的说法，**应视为个案而非普遍结论**。

---

## 参考来源

- [CachyOS Kernel — 官方 Wiki（内核特性、变体、tick rate、AutoFDO、补丁）](https://wiki.cachyos.org/features/kernel)
- [Why CachyOS? — 官方 Wiki（EEVDF tunables、BORE、仓库）](https://wiki.cachyos.org/cachyos_basic/why_cachyos)
- [CachyOS-Settings — GitHub（sysctl / udev / systemd / NVIDIA 模块参数 / game-performance / dlss-swapper）](https://github.com/CachyOS/CachyOS-Settings)
- [BORE (Burst-Oriented Response Enhancer) Scheduler — GitHub（完整 tunables 与默认值）](https://github.com/YuZyu9527/bore-scheduler)
- [linux-cachyos — GitHub（内核补丁与 topic 分支）](https://github.com/CachyOS/linux-cachyos)
- [CachyOS/kernel-patches — GitHub（自定义内核补丁）](https://github.com/CachyOS/kernel-patches)
- [CachyOS 官网（x86-64-v3/v4、LTO/PGO/BOLT、调度器选项）](https://cachyos.org/)
- [Phoronix — Operating Systems 评测列表（CachyOS 内核变体横评 / BORE 专项 / 三系统横评）](https://www.phoronix.com/reviews/Operating+Systems)
- [Phoronix — 新闻列表（2026 Q3 汇总提及 CachyOS）](https://www.phoronix.com/news)
- [什么值得买 —《CS2低帧暴涨20%、99项测试赢51项》](https://post.smzdm.com/p/a6zdp68o/)
- [什么值得买 —《CachyOS 8月大版本解读：帧率暴涨20%有几分真》（三项边界条件分析）](https://post.smzdm.com/p/ad72697p)
- [CSDN — CachyOS 游戏相关改进与操作教程（元包、环境变量、GameScope）](https://blog.csdn.net/hkbbkk/article/details/156546935)
- [百家号 — proton-cachyos 加入 NVIDIA Reflex 支持](https://baijiahao.baidu.com/s?id=1871489454503971896)
- [百家号 — CachyOS Proton 更新：一键让 A 卡用上 FSR4](https://baijiahao.baidu.com/s?id=1867887910965288018)
- [百家号 — RX 5700 XT 实测 11 款游戏：Linux 平均帧率比 Win11 高 6.4%](https://baijiahao.baidu.com/s?id=1877015523615591832)
- [17173 — 实测 AI 性能对比（CachyOS 76.19 居首、Windows 11 76.12）](https://news.17173.com/content/07202026/180059320.shtml)
- [百家号 — 5400 美元 Razer Blade 18 本地 AI：Windows 11 领先 Ubuntu 与 CachyOS](https://baijiahao.baidu.com/s?id=1871302446977445301)
- [sched-ext/scx Issue #1160（CachyOS 社区报告的 scx pre-login 加载问题）](https://github.com/sched-ext/scx/issues/1160)
- [CachyOS 官方 blog — 2411 Kernel AutoFDO](https://cachyos.org/blog/2411-kernel-autofdo/)
- [OpenBenchmarking.org（Phoronix Test Suite 公开结果）](https://openbenchmarking.org/)

> **来源质量说明**：官方 Wiki / GitHub / Phoronix 为一手来源；什么值得买两篇转述了 Phoronix、LTT 与社区实测数据，并做了边界条件分析，可信度较高；CSDN、百家号、17173 为二手/聚合来源，其中"10–15% FPS 提升"等表述**已被本报告标注为不成立或存疑**。
