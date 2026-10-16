# CachyOS 深度调研报告

- **调研对象**：CachyOS（基于 Arch Linux 的性能优化发行版）
- **调研日期**：2026-10-16
- **调研维度**：优化技术 / 社区活跃度 / 团队治理 / 打包质量 / Bug 风险
- **一句话定位**：把 Arch Linux 重编译成"开箱即用、还能打游戏"的性能改装成品，是当前 Arch 阵营完成度最高的性能样板间。

---

## 0. 结论速览

| 维度 | 评分 | 核心结论 |
|---|---|---|
| 优化技术 | ★★★★★ | 全仓库按 x86-64-v3/v4/znver4 重编译 + LTO/PGO/BOLT；自研内核提供 EEVDF 调参 / BORE / sched-ext / BMQ / RT 多种调度方案 |
| 社区活跃度 | ★★★★☆ | 2026 年长期霸榜 DistroWatch 第一；Discord / 论坛 / Reddit 均活跃；每年 5 次 ISO 更新节奏 |
| 团队治理 | ★★★☆☆ | 社区驱动、无公司实体；GitHub 公开核心成员仅 9 人，由创始人 ptr1337 主导；资金靠捐赠 + Framework 赞助；**关键人物依赖（bus factor）偏高** |
| 打包质量 | ★★★★☆ | 独立签名仓库、Docker 自动化多架构构建、AUR 衍生仓库、包索引与镜像测速体验好；**与上游 Arch 混装存在同步/ABI 风险** |
| Bug 风险 | ★★★☆☆ | 滚动发行固有风险，叠加"调度器/编译优化"这类前沿特性，以及 NVIDIA、引导、AUR 供应链等具体坑位 |

**总体判断**：工程完成度与社区热度都是真实的，性能收益在 CPU 敏感 / 低帧场景最明显；但收益幅度高度依赖硬件与游戏，且作为小团队主导的滚动发行，用户需具备基本的快照回滚与排障能力。它不是"更好的 Arch"，而是"更省事的 Arch + 一层性能改装"。

---

## 1. 项目背景

- CachyOS 是基于 Arch Linux 的滚动发行版，主打**性能**（而非外观或 AI 概念）。项目约于 2021–2022 年起步（不同来源说法不一），创始 / 主导者为 **Peter Jung（GitHub: ptr1337）**。
- 官方仓库地址：<https://cachyos.org>；包索引：<https://packages.cachyos.org>；Wiki：<https://wiki.cachyos.org>。
- 2024 年全年共发布 **13 个版本**；2025–2026 年改为**每年约 5 次 ISO 更新**的稳定节奏（2026 年 8 月的 2608 镜像是当年第 5 版）。
- 2025–2026 年长期位居 **DistroWatch 人气榜第一**；在 Steam 硬件调查中，CachyOS 用户占比一度达约 **4.21%**，接近 Ubuntu 24.04（该数字来自论坛转述，属二手来源，建议谨慎引用）。

---

## 2. 做了什么优化（技术拆解）

### 2.1 软件仓库：全栈重编译

- CachyOS 维护**独立的软件仓库**，不是直接复用 Arch 官方二进制，而是把 Arch 的 PKGBUILD 拿来按现代 CPU 指令集**重新编译**：
  - **x86-64-v3**（Haswell / Excavator 及更新的 CPU）
  - **x86-64-v4**（需 AVX-512，Skylake-X / Zen4 等）
  - **znver4**（AMD Zen 4 / Zen 5 专属仓库，2024 年 7 月起新装系统对 Zen4/5 自动启用）
- 编译优化叠加：**LTO（链接期优化）**为基线；**核心包额外启用 PGO + BOLT**；内核另有 **AutoFDO + Propeller**（linux-cachyos-lto 变体）。
- 官网表述："Core packages receive additional PGO and BOLT optimization — no manual rebuilds required."

### 2.2 内核：linux-cachyos 系列 + 调度器可选

- 内核基于上游 Linux，叠加 CachyOS 自有 **patch set**（含未主线化 / 未进 stable 的补丁），官方称这些补丁**先经内部测试再发布**。
- 提供多种**内核变体**：
  - `linux-cachyos`（默认，对 **EEVDF** 做响应性调参）
  - `linux-cachyos-bore`（**BORE** 调度器，最大化交互性）
  - `linux-cachyos-eevdf`、`linux-cachyos-bmq`、`linux-cachyos-rt-bore`（实时）
  - `linux-cachyos-lts`、`linux-cachyos-hardened`、`linux-cachyos-server`、手持设备专用变体等
- **sched-ext（SCX）**：支持用户态可插拔调度器（BPF 实现），由 `scx_loader` 管理，可在运行时切换。注意 **SCX 与 BMQ 内核变体不兼容**。

### 2.3 系统级调优与工具链

| 组件 | 作用 |
|---|---|
| `ananicy-cpp` + `ananicy-rules` | 按规则自动调整进程 CPU/IO 优先级 |
| `CachyOS-Settings` | 通过 sysctl / udev 规则做全系统微调，对 NVIDIA 显卡有专门适配 |
| `chwd` | 硬件检测与配置，自动识别并安装所需驱动 |
| `CachyOS Hello` | 欢迎 / 一键应用优化与修复 |
| `CachyOS Kernel Manager` | 图形化安装、配置内核与 sched-ext |
| `cachyos-rate-mirrors` | 自动测速并排序 Arch / CachyOS 镜像源 |
| `systemd-boot-manager` | 自动生成 systemd-boot 启动项 |
| `cachy-chroot` | 便捷 chroot，自动挂载 fstab 与 LUKS |
| `Shelly` | 默认图形包管理器（2026 年从 C# **重写为 Zig**，启动更快，支持 AUR PKGBUILD 预览） |
| `Proton-CachyOS` | 优化版 Proton 兼容层（含通过 vkd3d-low-latency 实现的 NVIDIA Reflex 低延迟） |

### 2.4 安装体验

- 两套安装器：**Calamares 图形安装器** + **CLI 安装器**（New-Cli-Installer，C++）。
- 支持 **17+ 桌面环境 / 窗口管理器**（KDE Plasma、GNOME、COSMIC、Hyprland、Sway、Niri、i3、XFCE…）。
- 默认 **Btrfs + 快照回滚**；支持 LUKS2 加密、Plymouth、bcachefs、T2 MacBook、手持设备游戏模式等。
- 2026 年起默认启用 **Wayland**。

### 2.5 性能成色（证据与反证）

**正面证据：**
- Phoronix 在 Razer Blade 18 上做 **Windows 11 vs Ubuntu 26.04 LTS vs CachyOS** 的 **99 项**跨系统测试（2026-07-15），CachyOS **赢下 51 项**；几何平均分 **76.19**，Windows 11 为 **76.12**（差距仅 0.07），Ubuntu 明显落后。
- 社区实测（i7-13700KF + RTX 5090，KDE Wayland + NVIDIA 610 驱动）中，CS2 的 **1% low 帧比 Windows 11 高约 20%**。
- RX 5700 XT 上 11 款游戏实测，Linux 侧平均帧率比 Win11 高约 6.4%。

**需要注意的反证 / 局限：**
- 99 项里**赢的是"项数"不是"51%"**，且赢的多为**小分差**，测试混合了编译、渲染、模拟负载，并非全是游戏。
- 性能提升**主要集中在低帧（1% low）和 CPU 敏感的高帧竞技游戏**；GPU 吃满的 3A 大作差距小得多。
- 社区共识："Linux 游戏收益的大头来自 **Proton / 驱动 / 内核**，这部分红利任何发行版都能吃到；CachyOS 独有的是**编译优化 + 调度器调校**那一层。" 这层值多少帧，取决于你的硬件和游戏。
- 现有测试多为**单样本、高端硬件**，缺少多机型、多档位的对照实验。
- 在 Phoronix 同一台机器上的**本地 AI 推理**测试中，Windows 11 反而大幅领先——说明优化并非"全面碾压"。

---

## 3. 社区活跃度

**官方渠道规模（截至 2024 年底官方年度总结）：**
- Discord：**4500+** 成员
- Reddit（r/cachyos）：**3100+** 成员
- 官方论坛（discuss.cachyos.org）：**1500+** 成员
- Telegram：**800+** 成员

**流量与下载量（2024 全年）：**
- 数据传输 **1.4 PB**，请求 **7.65 亿次**，月独立访客约 **23.4 万**
- ISO 下载约 **1.9 万次 / 月**

**活跃度佐证：**
- **发布节奏**：2024 年 13 个版本 → 2025/2026 年每年 5 次 ISO，节奏稳定且密集。
- **GitHub**：`linux-cachyos` 约 **4.6k star**，`proton-cachyos` 约 **1.5k star**，组织下 **123 个仓库**，多个仓库更新日期就在调研当天（2026-10-16）。
- **榜单与份额**：DistroWatch 人气榜长期第一；Steam 调查中占比约 4.21%。
- **第三方关注**：Linus Tech Tips 的"该换哪款 Linux"视频（B 站 6 万+ 播放）、Phoronix 多轮基准、HowToGeek / Linuxiac 持续报道。
- **社区氛围**：论坛 / Discord 被官方定位为"详细支持问题"与"快速问答"的主阵地，用户反馈具体（如掌机风扇控制、MSI Claw 兼容性等）。

**小结**：社区活跃度**高且真实**，属于 Arch 衍生发行中热度最靠前的一档。但需注意：热度很大程度由 2025–2026 年"Arch 桌面 / 游戏"这波大趋势（SteamOS、Omarchy 带动）推动，存在**热度周期性回落**的可能。

---

## 4. 团队治理

### 4.1 组织结构

- 性质：**独立、社区驱动的开源项目**，**没有公司实体**，官网明确写"independent, community-driven project"。
- GitHub 组织公开可见成员 **9 人**：

| 姓名 | GitHub | 备注 |
|---|---|---|
| Peter Jung | `ptr1337` | 创始人 / 主导者，邮箱 admin@cachyos.org，大量 PR 由他 merge |
| Eric Naim | `1Naim` | 内核配置维护 |
| Anton Ždanov | `azdanov` | 成员 |
| Lysec | `Ly-sec` | 成员 |
| NextWorks | `NextWork123` | 成员 |
| Piotr Górski | `sirlucjan` | 成员 |
| SoulHarsh007 | `SoulHarsh007` | 成员 |
| Vasiliy Stelmachenok | `ventureoo` | 工具链 / 镜像测速等 |
| Vladislav Nepogodin | `vnepogodin` | 成员 |

- 组织外的重要贡献者：**firelzrd**（BORE 调度器作者）、**loathingKernel**（Proton-CachyOS）。

### 4.2 资金与赞助

- 官网设 **Support / 捐赠** 入口，用途明确列示：**镜像与构建服务器、网站托管等基础设施**、**让核心团队投入更多时间做内核优化与打包**、**购买不同硬件做兼容性测试**。
- 外部赞助：模块化笔记本厂商 **Framework** 已成为赞助商，提供**硬件用于测试优化**并承诺**每月捐赠**。
- 另有镜像站合作（清华 TUNA、中科大 USTC 等）。

### 4.3 决策模式与治理风险

- 决策以 **GitHub Pull Request + Review + merge** 为主，从公开 PR 看，**ptr1337 是主要审批/合并者**，呈现"核心人物主导 + 小团队协作"的模式。
- **主要治理风险**：
  1. **关键人物依赖（bus factor 低）**：公开核心成员仅 9 人，项目方向与发布高度依赖创始人。
  2. **无正式治理章程 / 基金会**：没有公开的选举、决策委员会或路线图治理机制，长期可持续性依赖个人意愿与捐赠。
  3. **资金来源单一**：以个人捐赠 + 单一硬件厂商赞助为主，抗风险能力弱于有商业实体支撑的发行版。
  4. **与上游关系**：深度依赖 Arch Linux 的上游包与 PKGBUILD，属"寄生式创新"，上游策略变化会直接传导。

---

## 5. 打包质量

### 5.1 打包流程

- **来源**：以 Arch 官方 PKGBUILD 为基础，修改编译参数（`_processor_opt` 等）后重建，产出独立仓库。
- **构建基础设施**：使用 **Docker 构建镜像**（如 `pttrr/docker-makepkg-znver4`）+ `makepkg`；脚本 `script.sh` / `script-v3-v4.sh` 支持多架构批量构建；用 `repo-manage-util` 更新仓库索引。
- **多仓库矩阵**：`x86_64`、`x86_64_v3`、`x86_64_v4`、`znver4`。
- **签名**：仓库包由 CachyOS 签名密钥签名（`pacman-key --recv-keys F3B607488DB35A47`）。
- **AUR 衍生仓库**：`cachyos-aur-derived` 仓库（约 30+ issues / 30+ PRs 的活跃度）用于托管部分 AUR 衍生包。
- **包索引与镜像**：`packages.cachyos.org` 提供包检索；官方 mirrorlist API 用于镜像排序；`cachyos-rate-mirrors` 自动测速换源。

### 5.2 质量保障

- 内核补丁**先内部测试再发布**（官方 Wiki 表述）。
- 发行前有 **ISO 快照校验**（sha256 + GPG 双签名）。
- 工具链持续现代化：Shelly 重写为 Zig、Cachy-Updater 基于 Arch-Update 4.x + Rust 重写、安装器代码重构并修了一批 bug。

### 5.3 打包质量风险点

1. **与 Arch 官方仓库混装**：CachyOS 优化包与 Arch 官方包混用可能造成版本 / ABI 漂移，社区与官方均建议**整仓切换而非混装**。
2. **同步延迟**：独立仓库相对 Arch 官方存在**滞后**，上游紧急安全更新需等 CachyOS 重建后才进入其仓库。
3. **AUR 供应链**：`cachyos-aur-derived` 及 AUR 包本身存在**恶意包风险**（2025 年 6 月 AUR 曾发生恶意包事件）。新版 Shelly 增加 **PKGBUILD 预览**正是针对此风险的缓解措施。
4. **keyring / 镜像运维**：用户侧常见问题是 keyring 过期、镜像同步不一致、磁盘空间不足导致更新中断（社区建议滚动更新前预留 ≥10GB、备份 `/var/lib/pacman/local` 与 `/etc/pacman.conf`）。

**小结**：打包工程质量在同类 Arch 衍生项目中属**上游水平**——自动化、多架构、签名、索引齐备；但"独立仓库 + 重编译"这一模式天然带来**同步与混装**两类风险。

---

## 6. Bug 风险

### 6.1 结构性与固有风险

- **滚动发行固有风险**：上游更新随时可能引入回归，需自备快照回滚（官方默认 Btrfs + 快照，但需用户**安装时主动选择并实测恢复流程**）。
- **前沿特性风险**：sched-ext / BORE / BMQ / 实时内核、AutoFDO / Propeller 等属"尝鲜级"技术，稳定性与主线内核存在差距。
- **硬件门槛**：不支持**无 SSE4.2 指令集**的 CPU；v3/v4 仓库要求较新的 CPU（v4 需 AVX-512）。

### 6.2 已观察到的具体问题

| 类别 | 具体问题 |
|---|---|
| 调度器 | sched-ext / scx 在**登录前加载**时报 warning（源自 CachyOS 社区报告，scx issue #1160）；**SCX 与 BMQ 内核变体不兼容** |
| NVIDIA | Arch 侧 **590 驱动放弃 Pascal 支持**，GTX 10 系及更老卡需切 **legacy 分支**，装机和后续维护多一道工序；**Secure Boot 下闭源驱动签名验证**易失败；**Wayland + NVIDIA explicit-sync** 会导致部分 WebKit/GTK 应用启动闪退（需环境变量绕过） |
| 引导 | GRUB **未识别 Windows** 导致双系统菜单缺失；`grub.cfg` 参数 / UUID 配置错误导致无法启动；UEFI 下 grub-install 目标错误 |
| 游戏 | **内核级反作弊网游基本无解**（CS2 等平台反作弊存争议）；部分游戏需依赖特定 Proton-CachyOS 版本 |
| 安装 | 安装器访问地区判定服务、镜像源、驱动（NVIDIA 闭源）等环节易出错；安装失败原因集中在内核安装、Proton 兼容、GRUB 配置、AUR 包 |
| 供应链 | AUR / AUR 衍生仓库的**恶意包**风险（2025-06 事件） |

### 6.3 争议与需存疑的说法

- **"性能提升"的宣传口径**：收益主要体现在低帧与 CPU 敏感场景，且部分"Linux 游戏更强"的结论被归因于 Proton / 驱动，而非发行版本身；测试样本偏少。
- **部分二手来源需谨慎**：如"2026 年 1 月版本率先支持 FSR 4.0 AI 补帧"等表述来自百科 / 聚合站，未在官方渠道得到一致确认。
- **中文技术博客（CSDN 等）大量为 SEO 聚合内容**，其技术细节（如构建脚本路径）可作参考，但不宜作为权威依据。

---

## 7. 结论与建议

**适合安装：**
- 显卡为 AMD 或较新 NVIDIA，游戏库以 Steam 单机 + Proton 兼容网游为主——收益最直接。
- 掌机用户（官方支持 ROG Ally、Steam Deck OLED/LCD、Legion Go / Legion Go S）。
- 想要 Arch 的滚动更新与 AUR，但不想手动装系统 / 手搓内核的"不想折腾的 Arch"用户。
- 国内用户友好：官方 ISO 下载列表含清华 TUNA 源，`cachyos-rate-mirrors` 可自动换源。

**不建议安装：**
- 主力是**强反作弊网游**（内核级反作弊基本无解）。
- **GTX 10 系及更老的 Pascal 卡**（需 legacy 驱动，维护成本高）。
- 完全不想折腾、且必须使用特定专业软件的用户。

**落地建议（四条安全路线）：**
1. 别直接抹盘，先双系统或装到第二块盘，日用一周再决定。
2. 安装时选 **Btrfs** 方案，装完**亲手测一次快照恢复**。
3. AUR 装包**先看 PKGBUILD**（Shelly 已支持预览），别盲装。
4. 滚动更新前**备份 pacman 数据库与配置**、预留磁盘空间。

**后续值得关注的三个信号：**
1. **服务器版（Server Edition）** 何时从实验性转正（2026 年 8 月已出现在 CLI 安装器中）。
2. **掌机支持名单**是否继续扩大。
3. **NVIDIA legacy 驱动支持**是否继续收缩。

---

## 8. 参考来源

- [CachyOS 官网](https://cachyos.org/)
- [Why CachyOS? — CachyOS Wiki](https://wiki.cachyos.org/cachyos_basic/why_cachyos)
- [CachyOS Wiki 首页](https://wiki.cachyos.org/)
- [CachyOS GitHub 组织](https://github.com/CachyOS)
- [CachyOS GitHub 组织成员](https://github.com/orgs/CachyOS/people)
- [linux-cachyos 仓库](https://github.com/CachyOS/linux-cachyos)
- [CachyOS/distribution（通用 bug 反馈仓库）](https://github.com/CachyOS/distribution)
- [linux-cachyos PR #450（1Naim / ptr1337）](https://github.com/CachyOS/linux-cachyos/pull/450)
- [Phoronix — Operating Systems 评测列表（含 Ubuntu 26.04 LTS vs Windows 11 vs CachyOS）](https://www.phoronix.com/reviews/Operating+Systems)
- [什么值得买 —《CS2低帧暴涨20%、99项测试赢51项》（含 Phoronix / LTT 数据与社区反馈）](https://post.smzdm.com/p/a6zdp68o/)
- [知乎 —《CachyOS 2024 年终总结》（引用官方 blog 2412）](https://zhuanlan.zhihu.com/p/15207016754)
- [CachyOS 官方 blog 2412 December Release](https://cachyos.org/blog/2412-december-release/)
- [百度百科 — CachyOS（运营模式 / 核心团队）](https://baike.baidu.com/item/CachyOS/67612806)
- [HowToGeek — Arch Linux-Based CachyOS Just Got A Great Update](https://www.howtogeek.com/cachyos-august-2025-update/)
- [IT之家/百家号 — 2026 第 5 个镜像：8 月 CachyOS 更新（Shelly 用 Zig 重写）](https://baijiahao.baidu.com/s?id=1873191297072040767)
- [百家号 — CachyOS 八月大更：服务器版要来了](https://baijiahao.baidu.com/s?id=1874543976873000903)
- [百家号 — proton-cachyos 加入 NVIDIA Reflex 支持](https://baijiahao.baidu.com/s?id=1871489454503971896)
- [百家号 — RX 5700 XT 实测 11 款游戏：Linux 平均帧率比 Win11 高 6.4%](https://baijiahao.baidu.com/s?id=1877015523615591832)
- [17173 — 实测 AI 性能对比（CachyOS 76.19 排名第一）](https://news.17173.com/content/07202026/180059320.shtml)
- [sched-ext/scx Issue #1160（CachyOS 社区报告的 pre-login 加载问题）](https://github.com/sched-ext/scx/issues/1160)
- [CSDN — CachyOS 内核编译脚本详解（Docker 构建 / repo-manage-util）](https://blog.csdn.net/gitblog_00388/article/details/150696048)
- [CSDN — CachyOS 仓库配置完全指南（SCX 与 BMQ 不兼容）](https://blog.csdn.net/gitblog_01109/article/details/148464921)
- [CSDN — CachyOS 2026 首轮更新：镜像下载与软件源同步排查指南](https://blog.csdn.net/weixin_33483304/article/details/167228794)
- [CSDN — 手动安装 CachyOS 时如何正确配置 GRUB](https://ask.csdn.net/questions/8340900)
- [USTC 镜像站 — CachyOS 帮助](https://ipv4.mirrors.ustc.edu.cn/help/cachyos.html)
- [CachyOS 论坛（discuss.cachyos.org）](https://discuss.cachyos.org/)
- [CachyOS Discord](https://discord.gg/cachyos-862292009423470592)

> **来源质量说明**：官方站点（cachyos.org / wiki.cachyos.org）、GitHub、Phoronix 为一手/权威来源；知乎年度总结与什么值得买文章转述了官方 blog 与 Phoronix/LTT 的数据，可信度较高；百度百科、CSDN、百家号、17173 等为二手或聚合来源，其数字与表述已在正文中标注"需谨慎引用"。
