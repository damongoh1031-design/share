# 稳定优先下的发行版选型（第 15 轮 · 全研究综合 · 8 候选）

- **调研日期**：2026-10-16
- **系列**：Linux 游戏性能调研 **第 15 轮**（前 14 轮见 `../cachyos/` 与本目录 `README.md`）
- **核心问题**：**不要 CachyOS**；以**稳定优先**为前提、**尽量发挥硬件**；针对三类场景**分别**选一个发行版
- **候选池（8 个，本轮指定）**：openSUSE Tumbleweed、openSUSE Slowroll、Arch、**Fedora 44 KDE**、**Kubuntu 26.04**、**Kubuntu 26.10**、NixOS 26.05、**Bazzite**
- **本轮相对第 14 轮的变化**：**新增 Bazzite（全新候选）**、**新增 Kubuntu 26.10（昨天 10-15 刚发布）**、Fedora/Ubuntu 明确到 KDE 版本、**修正 NixOS 26.05 的 Mesa 与内核实测值**、移除 Debian/Solus

---

## 0. 一句话结论

| 场景 | **冠军** | 亚军 | 核心理由 |
|---|---|---|---|
| **① CPU 密集 Linux 原生**<br>（RimWorld / 群星 / CK3） | **openSUSE Slowroll** | **Bazzite** | 发行版对原生游戏贡献 **≈ 0** → 该把稳定性拉满。Slowroll = 月度批量 + Btrfs/snapper 默认 + 内核 7.2.8 |
| **② CPU 密集 Proton**<br>（2077 CPU 受限 / Palworld / Soulmask 大基地） | **openSUSE Tumbleweed** | **Bazzite** | 唯一杠杆是**翻译层 + 图形栈时效性** → 要最新 Mesa 26.2.4 + 最新内核 + 能兜底 |
| **③ GPU 密集 Proton（AMD）** | **openSUSE Tumbleweed** | Bazzite / Kubuntu 26.10 | 杠杆是 **Mesa RADV 版本** → 26.2.4 是最新档 |
| **③ GPU 密集 Proton（NVIDIA）** | **Kubuntu 26.04 LTS** | **Bazzite（nvidia 镜像）** | N 卡用专有驱动 → **Mesa 版本无关**；此时"驱动分发省事 + LTS 承诺"价值最大 |

> **只装一个系统**：**openSUSE Slowroll**（稳 + 默认回滚 + 内核够新）。
> **如果这台机器只用来玩游戏**：**Bazzite** 可以取代上表全部答案 —— 见 §6。

---

## 1. 本轮综合了哪些研究（全部资产盘点）

| 来源 | 内容 | 本轮如何用 |
|---|---|---|
| `../cachyos/` 13 组 26 份报告 | 四层优化模型、六发行版横比、五份一对一、三份场景专项、v3 Mesa 供给、Ubuntu 第三方内核/PPA 取舍 | 提供**结构性框架**（编译层/内核层/系统层/运行时层）与三场景杠杆分析 |
| `distro-choice/README.md` + `.html`（第 14 轮，本目录） | 三场景 × 8 候选（含 Debian / Solus） | 作为**基线**；本轮沿用其裁决框架，替换候选池 |
| `../kb/linux-gaming-distro-choice-2026.md`（v1.0） | 第 14 轮结论的 KB 精简版 | **原地升级为 v2.0**（本文件为其完整版） |
| `../kb/x86-64-v3-mesa-by-distro.md` | 各发行版 v3 Mesa 供给 | 校准"ISA 级别"的实际价值 |
| `../kb/ubuntu2604-thirdparty-kernel-mesa-ppa.md` | Ubuntu 第三方内核/PPA 取舍 | 场景③ NVIDIA 的决策依据 |
| 同仓库其他会话：`opensuse-slowroll-vs-tumbleweed/` | Slowroll vs TW 逐包比对 + openQA 证据（2026-10-15） | 交叉印证"Slowroll 仅滞后 ~2 周" |
| **本轮新增一手探测** | Bazzite（GitHub Releases + Containerfile + 官方文档）、Kubuntu 26.10 归档、Fedora 44 仓库、NixOS 26.05 nixpkgs | **§2 的地基** |

---

## 2. 一手版本总表（2026-10-16 直接抓取，8 候选）

**基准点**：Mesa **26.2.4 发布于 2026-10-01**，为当前最新稳定版。

| 候选 | **Mesa** | **内核** | 更新模型 | **默认回滚** | **scx / sched-ext** | ISA 基线 | 桌面 |
|---|---|---|---|---|---|---|---|
| **openSUSE Tumbleweed** | **26.2.4** ✅ | **7.2.10** ✅ | 滚动（日快照） | ✅ **Btrfs+snapper 自带** | ✅ **官方 1.1.3** | **v2** | KDE/GNOME |
| **openSUSE Slowroll** | 26.2.3 | 7.2.8 | 滚动（**月批量**） | ✅ **同 TW** | ✅ 官方 | **v2** | KDE/GNOME |
| **Arch Linux** | **26.2.4** ✅ | 7.2.9.arch1 | 滚动（日） | ⚠️ 需手动 | ⚠️ AUR | v1（+ALHP v3/v4） | 任意 |
| **Fedora 44 KDE** | **26.2.4** ✅ | **7.2.10** ✅ | 6 个月 + 滚动更新 | ⚠️ 需手动 | ❌ **官方无** | v1（v3 推迟 ≥F46） | KDE 官方 Edition |
| **Kubuntu 26.04 LTS** | 26.0.3 ⚠️ | 7.0.0-14 | LTS 2 年 + HWE | ❌ | ❌ | v1（+**实验 amd64v3**） | KDE |
| **Kubuntu 26.10** | **26.2.4** ✅ | **7.3.0-9.9** ⭐ | 9 个月 | ❌ | ❌ | v1（+**amd64v3 官方架构**） | KDE |
| **NixOS 26.05**（"Yarara"） | **26.1.8** | **6.18（默认）** / 7.2 可选 | 6 个月 + 声明式 | ✅✅ **原子回滚（最强）** | ✅ **有 scx 包** | v1（v3 需全量自编） | KDE/GNOME |
| **Bazzite**（Fedora 44 Atomic） | **26.2.4** ✅ | 7.2.9-ogc3.1 | **镜像化，每日自动** | ✅✅ **原子镜像 + greenboot** | ✅ **CachyOS COPR 的 scx-scheds 1.1.4** | v1 | **KDE（Kinoite 系）** |

**六条关键读数**：

1. **Kubuntu 26.10 是全池性能最高的** —— Mesa 26.2.4 + **内核 7.3.0**（比 TW 的 7.2.10 还新一个次版本）。但它**无任何回滚机制**且**非 LTS（仅 9 个月）**，与"稳定优先"直接冲突。
2. **Bazzite 是唯一"游戏栈全预装"的** —— gamescope 3.16.31 + Gamescope Session + MangoHud 0.8.4 + UMU 1.4.4 + ScopeBuddy + Distrobox 1.8.2.5，开箱即用。
3. **Bazzite 从 CachyOS 维护者（sirlucjan / `bieszczaders`）的 COPR 装 `scx-scheds` + `scx-tools`** —— 这是**非 CachyOS 发行版里唯一自带 CachyOS 生态调度器**的（一手证据：其 `Containerfile` 第 200 行）。
4. **Fedora 44 KDE 官方仓库确认无 `scx-scheds`**（`packages.fedoraproject.org` 与 `src.fedoraproject.org` 均 404）—— 这是它相对 openSUSE 的硬缺口。
5. **NixOS 26.05 实测值修正**：Mesa **26.1.8**（`pkgs/development/libraries/mesa/common.nix`），默认内核 **6.18**（`packageAliases.linux_default`，≥6.14 故**有 NTSync**），且**有 `scx` 包**（`pkgs/os-specific/linux/scx/default.nix` 存在）。→ 第 14 轮的"未核实"已闭环。
6. **Slowroll 的"慢"几乎不花钱** —— Mesa 26.2.3 vs 26.2.4 只差 1 个补丁版本（~2 周），内核 7.2.8 vs 7.2.10 差 2 个补丁版本。降的是**更新频率**，不是**版本水平**。

---

## 3. 三场景的有效杠杆（全部结论的根）

| 场景 | 瓶颈 | **发行版能碰到的杠杆** | 占比 |
|---|---|---|---|
| **① CPU 密集原生** | 单核 IPC × 频率、内存延迟、L3 | 内核内存管理（MGLRU / THP / ZRAM / swappiness）+ 调度延迟层 | **极小**（游戏二进制厂商预编译，编译层碰不到） |
| **② CPU 密集 Proton** | 翻译开销 + 同步开销 | **翻译层 + 运行时栈**（Wine/DXVK/vkd3d/Mesa 的构建与版本）+ NTSync + 调度 | **中** |
| **③ GPU 密集 Proton** | GPU 算力 / 驱动效率 | **GPU 驱动版本**（Mesa RADV / NVIDIA）+ 内核 amdgpu 修复 + 升频 | **中** |

**由此推出选型逻辑**：

```
场景 ①  发行版贡献 ≈ 0
        └─▶ 既然谁都不快 → 优化目标 = 稳定性最大化
            └─▶ 需要：内核 ≥ 6.14（NTSync）+ 能调 sysctl/ZRAM/THP + 出事能回滚
                └─▶ 【openSUSE Slowroll】月度批量 + 默认快照 + 内核 7.2.8

场景 ②  发行版贡献 = 中（唯一杠杆是翻译层与图形栈）
        └─▶ 优化目标 = 时效性最大化，但仍要能兜底
            └─▶ 需要：Mesa/DXVK/vkd3d 最新 + 内核最新 + 回滚能力
                └─▶ 【openSUSE Tumbleweed】Mesa 26.2.4 + 内核 7.2.10 + Btrfs 快照兜底

场景 ③  发行版贡献 = 中（唯一杠杆是驱动版本）
        ├─ AMD  ──▶ Mesa RADV 版本是硬指标 ──▶ 【openSUSE Tumbleweed】(26.2.4)
        └─ NVIDIA ─▶ 用专有驱动，Mesa 版本无关 ──▶ 【Kubuntu 26.04 LTS】
```

---

## 4. "稳定"的三个独立维度（评分标准）

| 维度 | 含义 | 谁给得了 |
|---|---|---|
| **① 更新频率可控** | 不会某天开机被迫接受 500 个包 | 固定周期（Fedora/Kubuntu/NixOS）或慢速滚动（**Slowroll**）> 日滚动（TW/Arch/Bazzite 默认） |
| **② 出问题能回滚** | 升级炸了能一键退回 | **Bazzite（原子镜像 + greenboot 自动健康检查）≥ openSUSE（Btrfs+snapper）> NixOS（声明式）> Arch（需手动）> Fedora/Kubuntu（无）** |
| **③ 软件质量（测试窗口）** | 进仓库前经过更多测试 | Kubuntu LTS / NixOS stable / Slowroll > Fedora / TW > Arch |

**关键校准**：维度 ③ 常被高估。滚动的包**不是"未测试的"**，只是"测试窗口短"；真风险是**你的硬件组合踩到回归** —— 此时**维度 ② 比 ③ 重要得多**。

> **这是 openSUSE 系与 Bazzite 共同胜出的根本原因**：它们是候选池里**仅有的"可控更新 + 开箱即用回滚"**的两条路线（openSUSE 用文件系统快照，Bazzite 用整镜像原子切换）。

---

## 5. 8 候选逐一裁决

### 🥇 openSUSE Slowroll —— 场景 ① 冠军，兼"只装一个系统"的答案

| 项 | 值 |
|---|---|
| Mesa / 内核 | **26.2.3 / 7.2.8**（实测，仅滞后 TW ~2 周） |
| 更新节奏 | **月度批量**（官方口径：TW 快照发布后 5–10 天进入 Slowroll） |
| 回滚 | ✅ **Btrfs + snapper 默认自带**，`snapper rollback` 一键退回 |
| 官方仓库 | ✅ gamemode / mangohud / **scx** / steam / NVIDIA 驱动**全部在官方仓库** |
| ISA 基线 | **v2**（高于 Arch/Fedora/Kubuntu/NixOS/Bazzite 的 v1） |
| 短板 | 滚动固有风险（被月度节奏 + 快照大幅削弱）；中文资料少于 Ubuntu |

**为什么赢场景 ①**：原生游戏瓶颈在硬件，不在发行版 → **唯一正确策略是把稳定性拉满**。Slowroll 是候选池里**唯一同时具备「慢速可控更新」+「开箱即用回滚」+「内核 7.2.8 远超 sched_ext/NTSync 门槛」+「官方仓库一站式游戏工具」**的选项。性能代价：约 2 周包滞后，实测无法察觉。

---

### 🥇 openSUSE Tumbleweed —— 场景 ②③（AMD）冠军

| 项 | 值 |
|---|---|
| Mesa / 内核 | **26.2.4 / 7.2.10**（实测，**双料最新**） |
| 更新节奏 | 滚动（日快照，**手动触发 `zypper dup`**） |
| 回滚 | ✅ **Btrfs + snapper 默认自带** ← 这是它胜过 Arch / Fedora 的关键 |
| 官方仓库 | ✅ gamemode 1.8.2 / mangohud **0.8.4** / **scx 1.1.3** / steam / NVIDIA 驱动 |

**为什么赢场景 ②**：Proton 的 CPU 开销全在翻译层（Wine → DXVK/vkd3d → Mesa RADV），而这些**全是发行版自己编译的包**。TW 给最新版本 + 最新内核，且在滚动发行里**唯一默认带原子回滚**。
**为什么赢场景 ③（AMD）**：Mesa 26.2.4 与 Arch / Bazzite / Kubuntu 26.10 并列最新。RADV 每版更新都带新游戏优化与光追改进。

**关键操作**：装 CachyOS 官方的 **`x86_64_v3` proton-cachyos tarball** 到 `~/.steam/root/compatibilitytools.d/` —— **不需要装 CachyOS**。

---

### 🆕 Bazzite —— 全场"游戏特化"最强，场景 ① 亚军 / ②③ 强亚军

| 项 | 值 |
|---|---|
| 基础 | **Fedora 44 Atomic Desktop**（Kinoite 系，`rpm-ostree` 镜像化） |
| Mesa / 内核 | **26.2.4**（最新）/ **7.2.9-ogc3.1**（ublue 自编译 flavour） |
| 更新节奏 | **Desktop 镜像每日自动**；Deck 镜像手动（可关、可换 stable/testing/unstable 分支） |
| **回滚** | ✅✅ **GRUB 选旧镜像 / `rpm-ostree rollback` / `bazzite-rollback-helper`** + **`greenboot` 启动健康检查失败自动回滚** |
| **调度器** | ✅ **`scx-scheds` + `scx-tools`，来自 `bieszczaders/kernel-cachyos-addons` COPR（CachyOS 维护者 sirlucjan 维护）** |
| 游戏栈 | ✅ **全部预装**：gamescope 3.16.31 + Gamescope Session + MangoHud 0.8.4 + UMU 1.4.4 + ScopeBuddy + InputPlumber + SteamOS-Manager + Distrobox 1.8.2.5 |
| HDR | ✅ Gamescope HDR 管线（SteamOS 同源） |
| NVIDIA | ✅ 专用镜像预装 **615.78.08（open）/ 580.178.04（LTS）** |
| ISA 基线 | v1（继承 Fedora） |
| 短板 | **不可变系统**（装系统级软件需 `rpm-ostree install` 或 Distrobox）；**内核是 ublue 自编译**（不在 Fedora 安全更新覆盖内，补丁集不透明）；每日自动更新需手动关 |

**为什么它是本轮的"变量"**：Bazzite 一次性解决了三个场景里最麻烦的部分 ——
- 场景 ①：`greenboot` 自动回滚（**比 snapper 更"硬"**，升级失败自动退回上一镜像）+ 预装 scx 调度器
- 场景 ②：游戏栈全预装（省掉 gamemode/mangohud/gamescope/UMU 全部手工配置）+ 原子兜底
- 场景 ③：NVIDIA 镜像预装驱动 + HDR + gamescope

**为什么它仍不是主答案（对"稳定优先"而言）**：
1. **每日自动更新**与"更新频率可控"直接冲突（虽然能关）。
2. **不可变**意味着场景 ① 要调的 sysctl / THP / ZRAM 虽然仍可改（`/etc/sysctl.d` 可写、`/sys/kernel/mm/...` 运行时可变），但内核参数要 `rpm-ostree kargs`，多一层心智负担。
3. **内核 `7.2.9-ogc` 是 ublue 自编译** —— 硬件踩坑时排查路径与常规发行版不同，且**不在 Fedora 的 LTS/安全承诺内**。
4. 出问题时**社区规模与中文资料远少于 openSUSE/Ubuntu**。

> **一句话定位**：**Bazzite 是"把 SteamOS 的思路做到通用 PC 上"的答案。** 如果这台机器是**纯游戏机 / 客厅 HTPC / 掌机**，它是本候选池最优解；如果是**主力工作机顺便玩游戏**，openSUSE 系更合适。

---

### Kubuntu 26.10 —— 性能第一，但因"无回滚 + 非 LTS"出局

| 项 | 值 |
|---|---|
| Mesa / 内核 | **26.2.4 / 7.3.0-9.9** ⭐ **全候选池最新**（含内核） |
| 发布日期 | **2026-10-15**（昨天） |
| 支持周期 | **9 个月**（非 LTS） |
| 回滚 | ❌ **无** |
| ISA | v1，但 **`amd64v3` 是官方架构之一**（`Release` 文件 `Architectures: amd64 amd64v3 arm64 …`） |
| 官方仓库游戏工具 | ❌ 需 PPA / Flatpak |
| 独家优势 | 性能最高 + `amd64v3` 官方可切（`APT::Architecture-Variants "amd64v3"`） |

**裁决**：**场景①②③ 均落选（对"稳定优先"的用户）**。它是"性能最大化"路线的答案，不是"稳定优先"路线的答案 —— 没有回滚机制 + 9 个月就要再升级一次，两条都违背用户的首要约束。
**但它值得知道**：如果你后来改成"性能优先"，**Kubuntu 26.10 + amd64v3** 是候选池里跑分最高的组合。

---

### Kubuntu 26.04 LTS —— **场景 ③（NVIDIA）冠军**

| 项 | 值 |
|---|---|
| Mesa / 内核 | 26.0.3 / 7.0.0-14 |
| 支持周期 | **LTS 2 年 + HWE**（→ 2031） |
| 回滚 | ❌ 无 |
| ISA | v1，**提供实验性 `amd64v3`**（实测含 `mesa-vulkan-drivers`） |
| 独家优势 | **NVIDIA 专有驱动分发最省事**（`ubuntu-drivers`）+ AI/CUDA 生态最成熟 |

**裁决**：
- **场景 ①**：可用但不最优（内核 7.0 已含 sched_ext + MGLRU + NTSync ✅，但无回滚）。
- **场景 ②**：**落选** —— Mesa 26.0.3 落后 0.5 个大版本，而 Proton 吃时效性。
- **场景 ③（NVIDIA）**：**冠军**。N 卡用专有驱动 → **Mesa 版本几乎无关**，此时"驱动分发最省事 + LTS 到 2031"的价值压过 Mesa 时效性劣势。
- ⚠️ **26.04 移除 X11、只剩 Wayland** → 图形栈出问题**没有 X11 兜底**，N 卡用户尤其注意。

---

### Arch Linux —— 场景 ②③ 亚军，因"无默认回滚"让位

| 项 | 值 |
|---|---|
| Mesa / 内核 | **26.2.4 / 7.2.9.arch1**（最新梯队） |
| 回滚 | ⚠️ **无默认机制**（`archinstall` 可勾 Btrfs+snapper，但非默认、需手配） |
| 官方仓库 | ✅ AUR 生态最强 |
| ISA | v1（**需第三方 ALHP 才有 v3/v4**） |

**裁决**：性能与 TW **基本同档**（都最新、都滚动）。**输在"回滚"** —— 用户明确"稳定优先"，而 Arch 升级炸了要自己进 chroot 救，TW 是开机菜单直接选旧快照。ALHP 的 v3/v4 是加分项，但 **v3 对游戏实际收益极小**，不值得为它牺牲回滚能力。

---

### Fedora 44 KDE —— 版本最新，但缺 scx 且无回滚

| 项 | 值 |
|---|---|
| Mesa / 内核 | **26.2.4 / 7.2.10-200.fc44** ✅ **双料最新**（本轮实测确认） |
| 更新节奏 | 6 个月 + 滚动更新 |
| 回滚 | ⚠️ 需手动配 Btrfs + snapper |
| **scx** | ❌ **官方仓库无 `scx-scheds`**（`packages.fedoraproject.org` / `src.fedoraproject.org` 均 404） |
| ISA | v1（v3 推迟 ≥F46） |
| 额外 | SELinux 默认 enforcing；NVIDIA 需 RPM Fusion；KDE 自 Fedora 42 起为官方 Edition |

**裁决**：
- **加分**：Mesa 与内核**都在最新梯队**（与 TW 并列），软件质量有保障。
- **扣分**：① **官方无 scx 包**（想玩调度器要走 COPR）；② **无默认回滚**；③ NVIDIA 需 RPM Fusion；④ 内核版本虽新，但 Fedora 的内核策略偏保守（上游优先、少打游戏向补丁）。
- **结论**：如果本来就熟悉 Fedora，可用；**在"稳定 + 发挥硬件"综合分上不如 openSUSE 系与 Bazzite**。
- **有意思的对照**：Bazzite 就是"Fedora 44 + 补上 Fedora 缺的东西"（scx 走 COPR、回滚用 rpm-ostree、游戏栈预装）。**所以 Fedora 44 KDE 的所有缺口，Bazzite 都补上了 —— 而代价是不可变性。**

---

### NixOS 26.05 —— 回滚最强，但游戏栈时效性与配置成本吃亏

| 项 | 值 |
|---|---|
| 版本 | **26.05 "Yarara"，2026-05-30** |
| Mesa | **26.1.8**（`common.nix` 实测）→ 落后最新 26.2.4 一个次版本 |
| 内核 | **默认 6.18**（`linux_default`，6.18.56）/ 可选 **7.2**（`linux_latest`，7.2.10）→ **6.18 ≥ 6.14，有 NTSync** ✅ |
| 回滚 | ✅✅ **声明式 + 原子回滚（候选池最强之一）** |
| scx | ✅ **有 `scx` 包**（`pkgs/os-specific/linux/scx/default.nix` 存在） |
| ISA | v1；v3 需 `nixpkgs.hostPlatform.gcc.arch = "x86-64-v3"` → **几乎全量本地编译，失去缓存红利** |
| 证据强度 | ⚠️ **Phoronix 从未做过含 NixOS 的发行版横评**，性能结论全部基于结构性推断 |

**裁决**：
- **场景 ①**：理论可用（发行版无关），但 ZRAM / THP / sysctl 都要写进 Nix 表达式，配置成本高于 openSUSE/Bazzite。
- **场景 ②③**：**落选**。Mesa 26.1.8 落后最新一个次版本，且 DXVK/vkd3d 更新要等 nixpkgs PR 合并进你的分支 → **时效性天然落后**，而这两个场景的唯一杠杆就是时效性。
- **一句话**：**NixOS 是"配置管理最优解"，不是"游戏性能最优解"。**

---

## 6. 最终裁决矩阵

| 候选 | ① CPU 原生 | ② CPU Proton | ③ GPU Proton (AMD) | ③ GPU Proton (NVIDIA) | 一句话 |
|---|---|---|---|---|---|
| **openSUSE Slowroll** | 🥇 **冠军** | 🥈 备选（差 2 周） | 🥈 备选 | 🥈 备选 | 稳 + 默认回滚 + 内核够新；"只装一个"的最佳答案 |
| **openSUSE Tumbleweed** | 🥉 可用 | 🥇 **冠军** | 🥇 **冠军** | 🥈 备选 | 双料最新 + 默认快照兜底 |
| **Bazzite** | 🥈 **亚军** | 🥈 **强亚军** | 🥈 **强亚军** | 🥈 **亚军** | 游戏栈全预装 + 原子回滚 + CachyOS 调度器；**纯游戏机首选** |
| **Arch** | ❌ 无默认回滚 | 🥉 | 🥉 | 🥉 | 性能同档 TW，输在"炸了要自己救" |
| **Fedora 44 KDE** | ⚠️ | ⚠️ | ⚠️ | ⚠️ | Mesa/内核都最新，但**无 scx + 无回滚 + NVIDIA 需 RPM Fusion** |
| **Kubuntu 26.04 LTS** | ⚠️ | ❌ Mesa 落后 | ⚠️ | 🥇 **冠军** | N 卡 + 求稳的最佳解；A 卡吃亏 |
| **Kubuntu 26.10** | ⚠️ | ⚠️（性能最高） | ⚠️（性能最高） | ⚠️ | **跑分第一但无回滚 + 仅 9 个月** → 与"稳定优先"冲突 |
| **NixOS 26.05** | ⚠️ | ❌ | ❌ | ❌ | 回滚最强，游戏栈时效性最弱 |

**"如果只能装一个"** → **openSUSE Slowroll**。
**"如果这是纯游戏机"** → **Bazzite**。

---

## 7. 三套落地方案

### 7.1 场景 ①：openSUSE Slowroll

```bash
# 1) 确认内核能力（应 >= 7.2，含 sched_ext / MGLRU / NTSync）
uname -r
ls /sys/kernel/sched_ext 2>/dev/null && echo "sched_ext OK"
ls /dev/ntsync 2>/dev/null || sudo modprobe ntsync

# 2) 游戏工具链（全部官方仓库，无需第三方）
sudo zypper install gamemode mangohud scx steam

# 3) 内存层调参（对"后期卡顿"最有效，配合 ZRAM）
sudo zypper install systemd-zram-service
sudo tee /etc/sysctl.d/99-gaming.conf <<'EOF'
vm.swappiness=100
vm.vfs_cache_pressure=50
vm.dirty_ratio=10
vm.dirty_background_ratio=5
EOF
sudo sysctl --system

# 4) THP 设 defer+madvise（减少内存抖动）
echo 'defer+madvise' | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

# 5) 出事回滚（这是选它的核心理由）
sudo snapper list && sudo snapper rollback <编号>
```

**实测预期**：对 RimWorld / 群星 / CK3，**唯一可能产生量级差异的是内存吃紧时避免磁盘 swap**（ZRAM + swappiness=100）。其余为个位数百分比。**换发行版救不了后期卡顿 —— 换 X3D 或加内存才行。**

### 7.2 场景 ②：openSUSE Tumbleweed

```bash
sudo zypper install gamemode mangohud scx steam

# 【关键】装 CachyOS 官方的 v3 优化 Proton —— 不需要装 CachyOS
#    先查最新 tag：https://github.com/CachyOS/proton-cachyos/releases
TAG="cachyos-11.0-20261005-slr"
mkdir -p ~/.steam/root/compatibilitytools.d
curl -LO "https://github.com/CachyOS/proton-cachyos/releases/download/$TAG/proton-cachyos-11.0-20261005-slr-x86_64_v3.tar.xz"
tar -xf proton-cachyos-11.0-20261005-slr-x86_64_v3.tar.xz -C ~/.steam/root/compatibilitytools.d/
# Steam → 属性 → 兼容性 → 强制指定该 Proton 版本

ls -l /dev/ntsync                      # 内核 7.2.10 >= 6.14 ✅
MANGOHUD=1 MANGOHUD_CONFIG=fps,frametime,gpu_util %command%   # GPU < 90% 才是 CPU 受限
```

> **TW 的滚动更新请在玩游戏前留一次 `snapper list` 回滚点**，别在周末排位前做大升级。

### 7.3 场景 ③：AMD → TW；NVIDIA → Kubuntu 26.04 LTS

```bash
# AMD（openSUSE Tumbleweed）
sudo zypper install mesa-vulkan-drivers mesa-dri-drivers vulkan-tools
vulkaninfo --summary | grep -E "driverName|driverInfo"   # 确认 RADV 版本

# NVIDIA（Kubuntu 26.04 LTS；注意只有 Wayland）
ubuntu-drivers devices && sudo ubuntu-drivers install && nvidia-smi

# 可选：整体切 amd64v3（26.04 官方提供，实测含 mesa-vulkan-drivers）
echo 'APT::Architecture-Variants "amd64v3";' | sudo tee /etc/apt/apt.conf.d/99enable-amd64v3
sudo apt update && sudo apt full-upgrade

flatpak install flathub com.valvesoftware.Steam
flatpak install flathub org.freedesktop.Platform.VulkanLayer.MangoHud
```

### 7.4 【替代路线】Bazzite（三场景通用）

```bash
# 1) 安装：官网按硬件/桌面选镜像（AMD / NVIDIA / 掌机 / Deck 版）
#    https://bazzite.gg/

# 2) 先关掉每日自动更新（如果你要"更新频率可控"）
ujust --help                       # 看可用任务
#   在 Bazzite Portal 里关闭自动更新，或改到 testing/unstable 分支由自己控节奏
rpm-ostree status                  # 看当前镜像与可回滚的版本

# 3) 回滚（出事时）
rpm-ostree rollback
bazzite-rollback-helper list && bazzite-rollback-helper rebase <旧版本>
#   或在 GRUB 菜单直接选上一个镜像

# 4) 调度器（已预装 scx-scheds / scx-tools，来自 CachyOS COPR）
scxctl start -s scx_bpfland        # 或按 scx_tools 的用法选择
ls /dev/ntsync                     # 内核 7.2.9 >= 6.14 ✅

# 5) 场景① 的内存层调参（/etc 在 rpm-ostree 下可写）
sudo tee /etc/sysctl.d/99-gaming.conf <<'EOF'
vm.swappiness=100
vm.vfs_cache_pressure=50
EOF
sudo sysctl --system

# 6) 需要系统级软件时（不可变系统的正确姿势）
rpm-ostree install <pkg>           # 会叠加一层，慎用
distrobox create --image archlinux:latest --name arch   # 更推荐：容器里折腾
```

---

## 8. 坑与反直觉

| 坑 | 说明 |
|---|---|
| **"换个发行版游戏就快了"** | ❌ 对原生游戏**几乎为零**；对 Proton 是**个位数百分比**（除非内存吃紧或 GPU 驱动差 1.5 代）。**硬件（X3D / 内存容量 / GPU）才是最大杠杆。** |
| **"Kubuntu 26.10 版本最新所以最好"** | ❌ 版本最新 ≠ 最适合。它**无任何回滚**且**仅 9 个月支持** → 对"稳定优先"是负分。 |
| **"Bazzite 就是个 Fedora 皮肤"** | ❌ 它补了 Fedora 的三个硬缺口：**scx（走 CachyOS 维护者的 COPR）**、**原子回滚 + greenboot 自动健康检查**、**游戏栈全预装**。 |
| **"不可变系统不能调游戏参数"** | ❌ 可以。`/etc/sysctl.d` 可写、`/sys/kernel/mm/...` 运行时可变、ZRAM 用 `zram-generator` 配置。**只有内核参数需要 `rpm-ostree kargs`。** |
| **"Bazzite 自带 CachyOS 内核"** | ❌ 它用的是 **ublue 自编译的 `ogc` flavour**（7.2.9-ogc），不是 `linux-cachyos`。**只有 `scx-scheds`/`scx-tools` 来自 CachyOS 维护者的 COPR。** |
| **"Debian 最稳所以最适合游戏"** | 稳定 ≠ 适合。Debian 13 的 Mesa 25.0.7 / 内核 6.12 是**实打实的性能损失**，且**无默认回滚**。 |
| **"Arch 比 TW 快"** | 实测**同档**（都 Mesa 26.2.4）。差异在**运维模型**：Arch 炸了要 chroot 救，TW 开机选旧快照。 |
| **"Slowroll 是降级版"** | ❌ 实测只滞后 **~2 周**（Mesa 26.2.3 vs 26.2.4）。降的是**更新频率**，不是**版本水平**。 |
| **"v3 重编译能提升帧数"** | 收益**极小且零散**。RADV 着色器编译走 LLVM，与宿主 ISA 级别基本无关。**Mesa 的"版本" ≫ 它的"ISA 级别"。** |
| **"装 proton-cachyos 必须用 CachyOS"** | ❌ 官方发布独立 `x86_64_v3` tarball，任何发行版放进 `compatibilitytools.d` 即可。 |
| **"NixOS 游戏栈太旧"** | 半对：Mesa **26.1.8**（落后 1 个次版本）确实偏旧，但它**有 scx 包**、默认内核 **6.18（含 NTSync）**、回滚能力全场最强。它的问题不是"旧"，是**配置成本**与**时效性跟不上**。 |
| **Kubuntu 26.04 只有 Wayland** | 图形栈出问题**没有 X11 兜底**，排查难度高于 24.04。N 卡用户尤其注意。 |

---

## 9. 未核实 / 存疑

| 项 | 说明 |
|---|---|
| **Bazzite 的 `ogc` 内核 flavour 具体补丁集** | 仅确认 flavour 名与版本号（7.2.9-ogc3.1），**未取得补丁清单**（是否含 BORE / fsync / 游戏向补丁不明）。`ublue-os/akmods` 的 `images.yaml` 只给构建矩阵，不给补丁集。 |
| **Bazzite `stable` 分支跟随 Fedora 44 → 45 的时间点** | 抓取时 `unstable-45` 已在构建、`fedora-release-common` 44-18 → 45-0.10，**stable 迁移时点未确认**。 |
| **Kubuntu 26.04 LTS 的 NVIDIA 驱动版本** | 本轮未测（`ubuntu-drivers` 的候选版本未抓）。 |
| **三套方案的实际帧率增益** | 不存在公开的同机对照基准；量级判断来自前 14 轮结构性分析 + 一手版本差异。 |
| **Slowroll 的长期项目承诺** | 相对较新的变体，维护承诺与社区规模**弱于 Tumbleweed**，未取得官方路线图确认。 |
| **Bazzite 与 openSUSE 的同机游戏对照** | 不存在。**Bazzite 在场景 ②③ 与 TW 的"胜负"是结构性推断**，不是实测。 |
| **Fedora 44 updates 中内核的最新版本** | 抓到 `kernel-7.2.10-200.fc44`（目录列表），**未逐一核对是否为绝对最新**。 |

---

## 10. 参考来源

**本轮一手探测（2026-10-16）**

- **Bazzite**
  - GitHub Releases API：`https://api.github.com/repos/ublue-os/bazzite/releases`（stable `44.20261012.1`：Mesa 26.2.4-1 / 内核 7.2.9-ogc3.1 / gamescope 3.16.31 / MangoHud 0.8.4-2 / KDE 6.7.5 / NVIDIA Open 615.78.08 / NVIDIA LTS 580.178.04；unstable `45.20261016`：scx-scheds 1.1.3-3 → 1.1.4-1）
  - `Containerfile`（`raw.githubusercontent.com/ublue-os/bazzite/main/Containerfile`）：`KERNEL_FLAVOR=ogc`、**`dnf5 -y copr enable bieszczaders/kernel-cachyos-addons` + `dnf5 -y install scx-scheds scx-tools`**、`greenboot`、`ScopeBuddy`、`bpftune-gaming`
  - 官方文档：`https://docs.bazzite.gg/General/FAQ/`、`/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/`
  - COPR 元数据：`https://copr.fedorainfracloud.org/api_3/build/list/?ownername=bieszczaders&projectname=kernel-cachyos-addons`（`source_package.name = scx-scheds`，submitter `sirlucjan`）
- **Kubuntu 26.10（stonking）**：`http://archive.ubuntu.com/ubuntu/dists/stonking/Release`（`Version: 26.10`，`Date: Thu, 15 Oct 2026`，`Architectures: amd64 amd64v3 arm64 armhf i386 ppc64el riscv64 s390x`）+ `dists/stonking/main/binary-amd64/Packages.gz`（mesa-vulkan-drivers 26.2.4-1ubuntu1 / libgl1-mesa-dri 26.2.4-1ubuntu1 / linux-image-generic 7.3.0-9.9 / libc6 2.44-1ubuntu2；6,446 包）
- **Kubuntu 26.04（resolute）**：`dists/resolute/main/binary-amd64/Packages.gz`（mesa 26.0.3-1ubuntu1 / linux-image-generic 7.0.0-14）
- **Fedora 44**：`https://dl.fedoraproject.org/pub/fedora/linux/updates/44/Everything/x86_64/Packages/{m,k}/`（mesa-vulkan-drivers-26.2.4-1.fc44.x86_64.rpm / kernel-7.2.10-200.fc44.x86_64.rpm）；`packages.fedoraproject.org/pkgs/scx-scheds/scx-scheds/` → **404**（官方无此包）
- **NixOS 26.05**：`raw.githubusercontent.com/NixOS/nixpkgs/nixos-26.05/pkgs/development/libraries/mesa/common.nix`（`version = "26.1.8"`）；`pkgs/top-level/linux-kernels.nix`（`linux_default = packages.linux_6_18`、`linux_latest = packages.linux_7_2`）；`pkgs/os-specific/linux/kernel/kernels-org.json`（6.18.56 / 7.2.10）；`pkgs/os-specific/linux/scx/default.nix` → **200**；release notes `rl-2605.section.md`（"Yarara", 2026-05-30）；channel commit `26f4107e47e3ad0ffd0db220469ba83b6f6d96e8`
- **openSUSE / Arch**：沿用第 14 轮实测（`download.opensuse.org/{tumbleweed,slowroll}/repo/oss/x86_64/`；`geo.mirror.pkgbuild.com/{core,extra}/os/x86_64/`）

**前序报告**
- `distro-choice/README.md` / `.html`（第 14 轮，本目录）
- `../cachyos/`（13 组 26 份：`distro-performance-comparison`、`cachyos-vs-{arch,fedora,opensuse,ubuntu2604,nixos2605}`、`cpu-bound-sim-games-optimization`、`proton-games-optimization`、`proton-cachyos-and-flatpak`、`x86-64-v3-mesa-by-distro`、`ubuntu2604-kernel-and-mesa-ppa`、`gaming-optimization-deepdive`）
- 同仓库其他会话：`opensuse-slowroll-vs-tumbleweed/openSUSE-Slowroll-vs-Tumbleweed-深度研究报告.md`

**外部**
- [openSUSE News — Tumbleweed Monthly Update（Slowroll 滞后 5–10 天官方口径）](https://news.opensuse.org/2025/01/29/tw-monthly-update-january/)
- [Phoronix — Operating Systems 评测列表](https://www.phoronix.com/reviews/Operating+Systems)
- [Bazzite 官网](https://bazzite.gg/) ｜ [Bazzite 文档](https://docs.bazzite.gg/)
- [Mesa 官方发布节奏](https://www.mesa3d.org/news/)

---

## 11. 关联文档

- [`README.md`](./README.md) / [`README.html`](./README.html)（第 14 轮：三场景 × 8 候选，候选池含 Debian / Solus）
- [`../kb/linux-gaming-distro-choice-2026.md`](../kb/linux-gaming-distro-choice-2026.md)（**v2.0**，本报告的 KB 版）
- [`../kb/x86-64-v3-mesa-by-distro.md`](../kb/x86-64-v3-mesa-by-distro.md)
- [`../kb/ubuntu2604-thirdparty-kernel-mesa-ppa.md`](../kb/ubuntu2604-thirdparty-kernel-mesa-ppa.md)
- [`../cachyos/`](../cachyos/)（前 13 轮）

---

## 12. 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| 第 14 轮 | 2026-10-16 | 三场景 × 8 候选（openSUSE TW/Slowroll、Arch、Fedora 44、Ubuntu 26.04、Debian 13、NixOS 26.05、Solus 4.9） |
| **第 15 轮** | 2026-10-16 | **候选池替换为：+Bazzite、+Kubuntu 26.10，Fedora/Ubuntu 明确到 KDE，移除 Debian/Solus**；新增 Bazzite 一手解剖（Containerfile / COPR / greenboot）；Kubuntu 26.10 实测（Mesa 26.2.4 + 内核 7.3.0）；**修正 NixOS 26.05（Mesa 26.1.8 / 内核 6.18 / 有 scx）**；裁决矩阵加入 Bazzite 列 |
