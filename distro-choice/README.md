# 脱离 CachyOS 的发行版选型（稳定优先 + 尽量发挥硬件）

- **调研日期**：2026-10-16
- **系列**：Linux 游戏性能调研 第 14 轮（前 13 轮见 `../cachyos/`）
- **核心问题**：**不要 CachyOS**，以**稳定优先**为前提，尽量发挥硬件，针对三类场景（CPU 密集原生游戏 / CPU 密集 Proton 游戏 / GPU 密集 Proton 游戏）**分别**选一个发行版
- **候选池（8 个）**：openSUSE Tumbleweed、openSUSE Slowroll、Arch、Fedora、Ubuntu、Debian、NixOS、Solus
- **一句话结论**：**CPU 密集原生 → openSUSE Slowroll；CPU 密集 Proton → openSUSE Tumbleweed；GPU 密集 Proton → openSUSE Tumbleweed（AMD）/ Ubuntu 26.04 LTS（NVIDIA）。** 如果只能装一个系统，选 **openSUSE Slowroll**。

---

## 0. 三场景答案速览

| 场景 | **冠军** | 亚军 | 一句话理由 |
|---|---|---|---|
| **① CPU 密集 Linux 原生游戏**<br>（RimWorld / 群星 / CK3） | **openSUSE Slowroll** | Debian 13（+backports） | 发行版对原生游戏的贡献 **≈ 0**（编译层碰不到游戏二进制）→ 既然选谁都不快，就选**最稳 + 能回滚 + 内核够新**的 |
| **② CPU 密集 Proton 游戏**<br>（2077 / Palworld / Soulmask 的 CPU 受限场景） | **openSUSE Tumbleweed** | Arch / Fedora 44 | 唯一有效杠杆是**翻译层 + 图形栈**，而它**吃版本时效性** → 要最新 Mesa/DXVK/vkd3d；TW 用**默认自带的 Btrfs+snapper** 给滚动风险兜底 |
| **③ GPU 密集 Proton 游戏**<br>（4K / 路径追踪 / 高画质） | **openSUSE Tumbleweed**（AMD）<br>**Ubuntu 26.04 LTS**（NVIDIA） | Fedora 44 | 唯一有效杠杆是**GPU 驱动版本**。AMD 要最新 RADV → Mesa 26.2.4（TW/Arch/Fedora 都在最新）；NVIDIA 用专有驱动，**Mesa 版本无关**，此时 Ubuntu 的驱动分发最省事 + LTS 最稳 |

> **注**：用户列了 7 项但实际给了 8 个发行版（openSUSE 占两个变体）。本报告按 **8 个候选**逐一裁决。

---

## 1. 先定义"稳定"，否则没法比

"稳定"在发行版语境里是**三个独立维度**，很多人混为一谈：

| 维度 | 含义 | 谁能给 |
|---|---|---|
| **① 更新频率可控** | 不会某天开机被迫接受 500 个包 | 固定发布周期（Fedora / Ubuntu / Debian / NixOS）或慢速滚动（Slowroll） |
| **② 出问题能回滚** | 升级炸了能一键退回 | **openSUSE（Btrfs+snapper 默认自带）** > NixOS（声明式）> Arch/CachyOS（需手动配）> Debian/Ubuntu/Fedora/Solus（无） |
| **③ 软件质量（不追新特性）** | 进仓库前经过更多测试 | Debian stable / Ubuntu LTS / Slowroll > Fedora / TW > Arch |

**关键校准**：维度 ③ 常被高估。滚动发行版（TW/Arch）的包**不是"未测试的"**，而是"测试窗口短"；真正的风险在**你的硬件组合恰好踩到回归**——此时**维度 ②（能否回滚）比维度 ③ 重要得多**。

> **这就是 openSUSE 系在本报告里胜出的根本原因**：它是唯一**同时**具备「慢速/可控更新」与「开箱即用的原子回滚」的主流发行版。Arch 更快，但炸了要自己救；Debian 更稳，但硬件发挥不足。

---

## 2. 一手版本对照（2026-10-16 直接探测仓库/镜像）

**这是本报告的地基**——所有版本号均来自直接 HTTP 抓取发行版官方仓库，非二手转述。

| 发行版 | **Mesa** | **内核** | 更新模型 | 默认回滚 | 官方仓库游戏工具 | ISA 基线 |
|---|---|---|---|---|---|---|
| **openSUSE Tumbleweed** | **26.2.4** ✅最新 | **7.2.10** ✅最新 | 滚动（日） | ✅ **Btrfs+snapper 默认** | ✅ gamemode 1.8.2 / mangohud **0.8.4** / **scx 1.1.3** / steam | v2 |
| **openSUSE Slowroll** | 26.2.3 | 7.2.8 | **滚动（月批量，滞后 ~2 周）** | ✅ **同 TW** | ✅ **同 TW** | v2 |
| **Arch Linux** | **26.2.4** ✅最新 | **7.2.9.arch1** | 滚动（日） | ⚠️ 需手动（archinstall 可选） | ✅ AUR | v1（+第三方 ALHP v3） |
| **Fedora 44** | **26.2.4**（updates） | 6.19.10（GA 快照） | 6 个月 + 滚动更新 | ⚠️ 需手动配 | ⚠️ gamemode 1.8.2 / mangohud 0.8.3~rc1，**无 scx 包** | v1（v3 推迟 ≥F46） |
| **Ubuntu 26.04 LTS** | 26.0.3 | 7.0.0-14 | LTS 2 年 + HWE | ❌ 无 | ⚠️ 需 PPA / Flatpak | v1（+实验性 amd64v3） |
| **Debian 13 trixie** | **25.0.7** ⚠️ | 6.12.107 | 2 年 + LTS 5 年 | ⚠️ 需手动配 | ❌ 需 backports / Flatpak | v1 |
| **NixOS 26.05** | 未核实（stable 分支冻结于发布时） | 未核实 | 6 个月 + 声明式 | ✅✅ 原子回滚（最强） | ⚠️ 需 `programs.steam.enable` 等配置 | v1（v3 需全量自编） |
| **Solus 4.9** | **25.2.5** ⚠️（polaris 仓库 26.1.8） | current 滚动（shannon 索引 6.16.12；实测用户跑 7.2.6） | 约 5–6 个月 | ❌ 无 | ❌ 生态小 | v1 |

**基准点**：Mesa **26.2.4 发布于 2026-10-01**，是当前最新稳定版。

**三条从表里直接读出的结论**：

1. **openSUSE Slowroll 的"慢"几乎不花钱** —— Mesa 26.2.3 vs 26.2.4 只差 **1 个补丁版本**（约 2 周），内核 7.2.8 vs 7.2.10 差 2 个补丁版本。**用 2 周的时效性换"月度更新 + 默认回滚"，性价比极高。**
2. **Debian 13 与 Solus 掉队 1.5 个大版本**（25.0.7 / 25.2.5 vs 26.2.4）。对 GPU 密集场景这是**实打实的损失**（新游戏优化、新 Vulkan 扩展、RADV 光线追踪改进都在 26.x）。
3. **openSUSE 是唯一官方仓库同时提供 `scx`（sched-ext 调度器）+ gamemode + mangohud + steam 的**。Fedora 官方**没有 scx 包**；Ubuntu/Debian 需要 PPA/backports。

---

## 3. 为什么三类场景答案不同：有效杠杆不一样

这是全部结论的来源。**同一个发行版在三类场景里的价值完全不同**，因为"能碰到的瓶颈"不同。

### 3.1 三类场景的有效杠杆表

| 场景 | 瓶颈 | **发行版能碰到的杠杆** | 发行版能碰到的比例 |
|---|---|---|---|
| **① CPU 密集原生** | 单核 IPC × 频率、内存延迟、L3 容量 | 内核内存管理（MGLRU / THP / ZRAM / swappiness）+ 调度延迟层 | **极小**（游戏二进制厂商预编译，编译层碰不到；硬件才是主因） |
| **② CPU 密集 Proton** | 翻译开销 + 同步开销 | **翻译层 + 运行时栈**（Wine/DXVK/vkd3d/Mesa 的构建与版本）+ NTSync + 调度 | **中**（这层是发行版自己编译的，且在关键路径上） |
| **③ GPU 密集 Proton** | GPU 算力 / 驱动效率 | **GPU 驱动版本**（Mesa RADV / NVIDIA）+ 内核 amdgpu 修复 + 升频技术 | **中**（版本差 1.5 个大版本就是真差距） |

### 3.2 由此推出的选型逻辑

```
场景 ①  发行版贡献 ≈ 0
        └─▶ 既然谁都不快，优化目标 = 稳定性最大化
            └─▶ 需要：内核够新（≥6.12 有 sched_ext；≥6.14 有 NTSync）
                     + 能调 sysctl/ZRAM + 出事能回滚
                └─▶ 【openSUSE Slowroll】月度更新 + 默认快照 + 内核 7.2.8 远超门槛

场景 ②  发行版贡献 = 中（唯一有效杠杆是翻译层与图形栈）
        └─▶ 优化目标 = 时效性最大化，但仍要能兜底
            └─▶ 需要：Mesa / DXVK / vkd3d 最新 + 内核最新 + 回滚能力
                └─▶ 【openSUSE Tumbleweed】全部最新 + Btrfs 快照兜底
                    （翻译层优化本身可"打包带走"：proton-cachyos 官方发 x86_64_v3 tarball，
                      任何发行版都能放进 compatibilitytools.d，无需装 CachyOS）

场景 ③  发行版贡献 = 中（唯一有效杠杆是驱动版本）
        ├─ AMD  ──▶ Mesa RADV 版本是硬指标 ──▶ 【openSUSE Tumbleweed】(Mesa 26.2.4)
        └─ NVIDIA ─▶ 用专有驱动，Mesa 版本无关 ──▶ 【Ubuntu 26.04 LTS】
                     （驱动分发最省事 + LTS 最稳 + 内核 7.0 够用）
```

---

## 4. 淘汰赛：8 个候选逐一裁决

### 🥇 openSUSE Slowroll —— 场景 ① 冠军，兼"只装一个系统"的答案

| 项 | 值 |
|---|---|
| Mesa / 内核 | **26.2.3 / 7.2.8**（实测，仅滞后 TW ~2 周） |
| 更新节奏 | **月度批量**（官方口径：Tumbleweed 快照发布后平均 5–10 天进入 Slowroll） |
| 回滚 | ✅ **Btrfs + snapper 默认自带**，`snapper rollback` 一键退回 |
| 官方仓库 | ✅ gamemode / mangohud / scx / steam / NVIDIA 驱动 **全部在官方仓库** |
| ISA 基线 | v2（高于 Arch/Fedora/Ubuntu/Debian 的 v1） |
| 短板 | 滚动发行固有风险（但被月度节奏 + 快照大幅削弱）；中文社区资料少于 Ubuntu |

**为什么它赢场景 ①**：原生游戏的瓶颈在硬件，不在发行版。此时**唯一正确的策略是把稳定性拉满**，而 Slowroll 是候选池里**唯一同时具备「慢速可控更新」+「开箱即用原子回滚」+「内核 7.2.8（远超 sched_ext/NTSync 门槛）」**的选项。性能代价：**约 2 周的包滞后，实测无法察觉。**

**为什么它不赢场景 ②③**：那两个场景**唯一有效杠杆就是软件时效性**，而 TW 免费给你最新版（Mesa 26.2.4 / 内核 7.2.10），代价仅是"更新更频繁"——而 TW 同样有默认快照兜底。**用回滚能力换最新版，在 ②③ 里是划算的。**

---

### 🥈 openSUSE Tumbleweed —— 场景 ②③ 冠军

| 项 | 值 |
|---|---|
| Mesa / 内核 | **26.2.4 / 7.2.10**（实测，**双料最新**） |
| 更新节奏 | 滚动（日快照） |
| 回滚 | ✅ **Btrfs + snapper 默认自带** ← 这是它胜过 Arch 的关键 |
| 官方仓库 | ✅ gamemode 1.8.2 / mangohud **0.8.4**（比 Fedora 新）/ **scx 1.1.3** / steam / NVIDIA 驱动 |
| ISA 基线 | v2 |

**为什么它赢场景 ②**：Proton 的 CPU 开销全在翻译层（Wine → DXVK/vkd3d → Mesa RADV），而这些**全是发行版自己编译的包**。TW 提供最新版本 + 最新内核，且在滚动发行里**唯一默认带原子回滚**。
**为什么它赢场景 ③（AMD）**：Mesa 26.2.4 = 与 Arch 并列最新。RADV 的每版更新都带新游戏优化与光线追踪改进，对 GPU 密集场景是直接收益。

**关键操作（任何发行版通用）**：装 CachyOS 官方的 **`x86_64_v3` proton-cachyos tarball** 到 `~/.steam/root/compatibilitytools.d/`——**不需要装 CachyOS**，就能拿到 v3 优化的翻译层。这一步把场景 ② 的"冠军项"从 CachyOS 手里拿到，且不受发行版限制。

---

### 🥉 Debian 13 trixie —— 场景 ① 亚军；场景 ②③ 落选

| 项 | 值 |
|---|---|
| Mesa / 内核 | **25.0.7 / 6.12.107** ⚠️ |
| 稳定性 | ★★★★★（2 年周期 + LTS 5 年，候选池最强） |
| 回滚 | ❌ 无默认机制（需自己配 Btrfs + snapper/timeshift） |
| 官方仓库 | ❌ 无 gamemode / mangohud / steam 的顺滑体验，需 backports / Flatpak |

**裁决**：
- **场景 ①**：可以作为亚军——发行版无关，而 Debian 最稳。但两个扣分项：**内核 6.12.107 恰好卡在门槛上**（6.12 是 sched_ext 进入的版本，但**没有 NTSync**，NTSync 需要 6.14）；**无默认回滚**（而它的"稳"恰恰最依赖回滚兜底）。要补齐得开 backports，而实测 **trixie-backports 里没有 `mesa-vulkan-drivers`**（抓取返回空）。
- **场景 ②③**：**落选**。Mesa 25.0.7 落后 1.5 个大版本，对 Proton 场景是直接损失；且 DXVK/vkd3d 版本同样陈旧。
- 想用 Debian 的正确姿势：**Debian sid**（实测 Mesa 26.2.4 = 最新）——但那时你已经放弃了 Debian 的全部稳定性优势，不如直接选 TW。

---

### Arch Linux —— 场景 ② 亚军；场景 ①③ 因"回滚"落选

| 项 | 值 |
|---|---|
| Mesa / 内核 | **26.2.4 / 7.2.9.arch1**（实测，**最新梯队**） |
| 更新节奏 | 滚动（日） |
| 回滚 | ⚠️ **无默认机制**（archinstall 可勾选 Btrfs+snapper，但非默认、需手动配置） |
| 官方仓库 | ✅ AUR 生态最强；`nvidia` / `nvidia-open` 官方维护 |
| ISA 基线 | v1（**需第三方 ALHP 仓库**才有 v3/v4） |

**裁决**：性能上 Arch 与 TW **基本同档**（都最新、都是滚动）。**Arch 输在"回滚"这一项**——用户明确要求"稳定优先"，而 Arch 升级炸了要自己进 chroot 救，TW 是开机菜单直接选旧快照。这一条差异足以决定胜负。
**加分项**：ALHP 提供 v3/v4 仓库（TW 是 v2 基线且无 v3 仓库）。但 **v3 对游戏的实际收益极小**（RADV 着色器编译走 LLVM，与宿主 ISA 级别基本无关），**不值得为它牺牲回滚能力**。

---

### Fedora 44 —— 场景 ②③ 的备选；不推荐作为首选

| 项 | 值 |
|---|---|
| Mesa / 内核 | **26.2.4**（updates）/ 6.19.10（GA 快照，updates 中持续更新） |
| 更新节奏 | 6 个月大版本 + 滚动更新 |
| 回滚 | ⚠️ **无默认机制**（需手动配 Btrfs + snapper） |
| 官方仓库 | ⚠️ gamemode 1.8.2 ✅ / mangohud 0.8.3~rc1 ✅ / **scx 无** ❌ |
| ISA 基线 | v1（**v3 推迟至至少 F46**） |
| 额外 | SELinux 默认 enforcing；NVIDIA 需 RPM Fusion |

**裁决**：
- **加分**：Mesa 在 updates 里已到 26.2.4（最新梯队）；6 个月周期 + 上游优先，软件质量有保障。
- **扣分**：① **官方仓库没有 sched-ext（scx）包**——想玩调度器实验比 openSUSE/Arch 更受限；② **无默认回滚**；③ NVIDIA 用户需额外启用 RPM Fusion；④ 内核在 GA 快照里落后（6.19 vs 7.2）。
- **结论**：如果用户本来就熟悉 Fedora，可用；**在"稳定 + 发挥硬件"的综合分上不如 openSUSE 系**。

---

### Ubuntu 26.04 LTS —— **场景 ③（NVIDIA）冠军**

| 项 | 值 |
|---|---|
| Mesa / 内核 | 26.0.3 / 7.0.0-14 |
| 更新节奏 | LTS 2 年 + HWE 内核滚动 |
| 回滚 | ❌ 无（需 ZFS on root 或第三方工具） |
| 官方仓库 | ⚠️ 需 PPA / Flatpak 才能顺滑玩游戏 |
| ISA 基线 | v1（**但提供实验性 amd64v3**，见前序报告） |
| 独家优势 | **NVIDIA 专有驱动分发最省事**（含 Ubuntu Pro 支持）；AI/CUDA 生态最成熟 |

**裁决**：
- **场景 ①**：可用但不最优。内核 7.0 已含 sched_ext + MGLRU + NTSync ✅，但**无回滚**且 Mesa 落后。
- **场景 ②**：**落选**。Mesa 26.0.3 落后 0.5 个大版本，而 Proton 场景吃时效性。**不过**——Ubuntu 26.04 官方提供 **`binary-amd64v3` 组件**（实测含 `mesa-vulkan-drivers`/RADV），一行 `APT::Architecture-Variants "amd64v3"` 就能整体切到 v3，这是它相对 Debian/Fedora 的独特加分。
- **场景 ③（NVIDIA）**：**冠军**。NVIDIA 用户用的是专有驱动，**Mesa 版本几乎无关**，此时 Ubuntu 的"驱动分发最省事 + LTS 到 2031"的价值压过 Mesa 时效性的劣势。26.04 移除 X11 只剩 Wayland，驱动问题排查难度上升（无 X11 兜底），这是唯一需要提醒的风险。

---

### NixOS 26.05 —— 三个场景均落选

| 项 | 值 |
|---|---|
| 回滚 | ✅✅ **声明式 + 原子回滚（候选池最强）** |
| 游戏栈 | ⚠️ Steam 需 `programs.steam.enable`；Mesa/DXVK 版本取决于 nixpkgs 分支，**stable 分支冻结于发布时** |
| ISA 基线 | v1；**v3 需 `nixpkgs.hostPlatform.gcc.arch = "x86-64-v3"` → 几乎全量本地编译，失去缓存红利** |
| 证据强度 | ⚠️ **Phoronix 从未做过包含 NixOS 的发行版横评**，性能结论全部基于结构性推断 |

**裁决**：NixOS 的**回滚能力是全场最强**，但它的设计目标从来不是游戏：
- **场景 ①**：理论可用（发行版无关），但游戏工具链配置成本高、ZRAM/THP 等需写进 Nix 表达式。
- **场景 ②③**：**落选**。Mesa/DXVK 的更新要等 nixpkgs PR 合并并进入你的分支，**时效性天然落后**；而这两个场景的唯一杠杆就是时效性。
- **一句话**：**NixOS 是"配置管理最优解"，不是"游戏性能最优解"。** 如果你已经重度使用 NixOS，它够用；如果为游戏选型，别选它。

---

### Solus 4.9 —— 三个场景均落选

| 项 | 值 |
|---|---|
| Mesa | **25.2.5**（shannon 仓库实测；polaris 新仓库 26.1.8） ⚠️ |
| 内核 | `linux-current` 滚动跟进（shannon 索引 6.16.12；ProtonDB 实测有用户跑 7.2.6）；`linux-lts` 6.12.52 |
| 更新节奏 | 约 5–6 个月一个大版本（4.8 → 4.9 间隔约 5 个月） |
| 回滚 | ❌ 无 |
| 生态 | ❌ 小团队、社区规模远小于其他候选、无 AUR/PPA/COPR 级别的第三方仓库 |

**裁决**：**淘汰**。
- Mesa 25.2.5 落后 1.5 个大版本，场景 ②③ 直接吃亏。
- 生态薄 → 游戏相关包（gamemode / mangohud / Proton 工具链）覆盖不全，很多要靠 Flatpak 补。
- 小团队 + 无回滚 → 与"稳定优先"的目标相反（**"稳"需要的是能兜底，而不是更新慢**）。
- 唯一亮点：Budgie 桌面与自身技术栈（`ferryd`、eopkg）有独特性，但**与游戏性能无关**。

---

## 5. 最终裁决表

| 候选 | 场景 ①<br>CPU 原生 | 场景 ②<br>CPU Proton | 场景 ③<br>GPU Proton | 一句话 |
|---|---|---|---|---|
| **openSUSE Slowroll** | 🥇 **冠军** | 🥈 备选（仅差 2 周） | 🥈 备选 | 稳 + 默认回滚 + 内核够新；"只装一个"的最佳答案 |
| **openSUSE Tumbleweed** | 🥉 可用（更勤更新） | 🥇 **冠军** | 🥇 **冠军（AMD）** | 双料最新 + 默认回滚，滚动风险被快照兜住 |
| **Arch** | ❌ 无默认回滚 | 🥈 亚军 | 🥈 亚军 | 性能同档 TW，输在"炸了要自己救" |
| **Fedora 44** | ⚠️ 可用 | 🥉 备选 | 🥉 备选 | Mesa 已最新，但无 scx、无回滚、NVIDIA 需 RPM Fusion |
| **Ubuntu 26.04 LTS** | ⚠️ 可用 | ❌ Mesa 落后 | 🥇 **冠军（NVIDIA）** | N 卡 + 求稳的最佳解；A 卡吃亏 |
| **Debian 13** | 🥈 亚军 | ❌ | ❌ | 最稳但硬件发挥不足（Mesa 25.0.7 / 内核 6.12） |
| **NixOS 26.05** | ⚠️ 可用 | ❌ | ❌ | 回滚最强，游戏栈时效性最弱 |
| **Solus 4.9** | ❌ | ❌ | ❌ | 生态薄 + 版本落后 1.5 代 |

---

## 6. 三套落地方案（装完就做这些）

### 6.1 场景 ①：openSUSE Slowroll

```bash
# 1) 确认内核与调度器能力（应 >= 7.2，含 sched_ext / MGLRU / NTSync）
uname -r
ls /sys/kernel/sched_ext 2>/dev/null && echo "sched_ext OK"
ls /dev/ntsync 2>/dev/null || sudo modprobe ntsync

# 2) 装游戏工具链（全部在官方仓库，无需第三方）
sudo zypper install gamemode mangohud scx steam

# 3) 内存层调参（对"后期卡顿"最有效，配合 ZRAM）
sudo zypper install systemd-zram-service   # 或使用 zram-generator
sudo tee /etc/sysctl.d/99-gaming.conf <<'EOF'
vm.swappiness=100
vm.vfs_cache_pressure=50
vm.dirty_ratio=10
vm.dirty_background_ratio=5
EOF
sudo sysctl --system

# 4) THP 设为 defer+madvise（减少内存抖动）
echo 'defer+madvise' | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

# 5) 出事回滚（这是选它的核心理由）
sudo snapper list
sudo snapper rollback <编号>
```

**实测预期**：对 RimWorld / 群星 / CK3，**唯一可能产生量级差异的是内存吃紧时避免磁盘 swap**（ZRAM + swappiness=100）。其余（调度器/THP）为个位数百分比。**别指望换发行版能救后期卡顿——换 X3D 或加内存才是。**

### 6.2 场景 ②：openSUSE Tumbleweed

```bash
# 1) 基础工具（同 6.1）
sudo zypper install gamemode mangohud scx steam

# 2) 【关键】装 CachyOS 官方的 v3 优化 Proton —— 不需要装 CachyOS
#    先查最新 tag：https://github.com/CachyOS/proton-cachyos/releases
TAG="cachyos-11.0-20261005-slr"
mkdir -p ~/.steam/root/compatibilitytools.d
curl -LO "https://github.com/CachyOS/proton-cachyos/releases/download/$TAG/proton-cachyos-11.0-20261005-slr-x86_64_v3.tar.xz"
tar -xf proton-cachyos-11.0-20261005-slr-x86_64_v3.tar.xz -C ~/.steam/root/compatibilitytools.d/
# 然后在 Steam → 属性 → 兼容性 → 强制指定该 Proton 版本

# 3) 确认 NTSync 生效（内核 7.2.10 >= 6.14 ✅）
ls -l /dev/ntsync
PROTON_USE_NTSYNC=1 %command%     # Proton 11+ 默认开，老版本手动

# 4) 判瓶颈：GPU 占用 < 90% 才值得继续折腾
MANGOHUD=1 MANGOHUD_CONFIG=fps,frametime,gpu_util %command%
```

**注意**：TW 的滚动更新请在**玩游戏前**留一次 `snapper list` 的回滚点，别在周末排位前做大升级。

### 6.3 场景 ③：AMD → TW；NVIDIA → Ubuntu 26.04 LTS

**AMD（openSUSE Tumbleweed）**
```bash
sudo zypper install mesa-vulkan-drivers mesa-dri-drivers vulkan-tools
vulkaninfo --summary | grep -E "driverName|driverInfo"   # 确认 RADV 版本
# 升频/低延迟按游戏选：FSR4 / Anti-Lag 2 / 帧生成
```

**NVIDIA（Ubuntu 26.04 LTS）**
```bash
# 官方驱动最省事；注意 26.04 只有 Wayland，没有 X11 兜底
ubuntu-drivers devices
sudo ubuntu-drivers install          # 或指定版本
nvidia-smi

# 可选：整体切到 amd64v3（Ubuntu 26.04 官方提供，实测含 mesa-vulkan-drivers）
echo 'APT::Architecture-Variants "amd64v3";' | sudo tee /etc/apt/apt.conf.d/99enable-amd64v3
sudo apt update && sudo apt full-upgrade

# 装游戏工具（官方仓库没有，走 Flatpak 最省事）
flatpak install flathub com.valvesoftware.Steam
flatpak install flathub org.freedesktop.Platform.VulkanLayer.MangoHud
```

---

## 7. 坑与反直觉

| 坑 | 说明 |
|---|---|
| **"换个发行版游戏就快了"** | ❌ 对原生游戏**几乎为零**；对 Proton 是**个位数百分比**（除非内存吃紧或 GPU 驱动差 1.5 代）。**硬件（X3D / 内存容量 / GPU）才是最大杠杆。** |
| **"Debian 最稳所以最适合游戏"** | 稳定 ≠ 适合。Debian 13 的 Mesa 25.0.7 / 内核 6.12 是**实打实的性能损失**，且**没有默认回滚**——它的"稳"需要你手动配 Btrfs+snapper 才能兑现。 |
| **"Arch 比 TW 快"** | 实测**同档**（都 Mesa 26.2.4，内核 7.2.9 vs 7.2.10）。差异在**运维模型**：Arch 炸了要 chroot 救，TW 开机选旧快照。 |
| **"Slowroll 是降级版"** | ❌ 实测只滞后 **~2 周**（Mesa 26.2.3 vs 26.2.4）。它降的是**更新频率**，不是**版本水平**。 |
| **"滚动发行不能用来玩游戏"** | 可以，但**必须配回滚**。openSUSE 默认给你；Arch 要自己配；Fedora/Debian/Ubuntu/Solus 干脆没有。 |
| **"v3 重编译能提升游戏帧数"** | 收益**极小且零散**。RADV 着色器编译走 LLVM（面向实际 GPU），与宿主 ISA 级别基本无关。**Mesa 的"版本" ≫ 它的"ISA 级别"。** |
| **"装 proton-cachyos 必须用 CachyOS"** | ❌ 官方发布独立 `x86_64_v3` tarball，任何发行版放进 `compatibilitytools.d` 即可。**这是把 CachyOS 的冠军项"打包带走"的关键。** |
| **Fedora 的 SELinux 拖慢游戏** | 影响可忽略，**不是**不推荐它的理由。真正的理由是无 scx 包 + 无默认回滚 + NVIDIA 需 RPM Fusion。 |
| **Ubuntu 26.04 移除 X11** | 只剩 Wayland → 图形栈出问题**没有 X11 兜底**，排查难度高于 24.04。N 卡用户尤其注意。 |

---

## 8. 未核实 / 存疑

| 项 | 说明 |
|---|---|
| **NixOS 26.05 的 Mesa / 内核具体版本** | nixpkgs 文件路径多次探测失败（404），**未取得精确版本号**。结论基于"stable 分支冻结于发布时"的结构性推断。 |
| **Solus 的 `linux-current` 当前实际版本** | `packages.getsol.us` 索引显示 6.16.12，但 ProtonDB 有用户报告 Solus 4.9 上跑 7.2.6 → **索引可能滞后**，两者矛盾未解决。 |
| **Fedora 44 updates 中的最新内核版本** | 目录抓取失败（返回空）。已知 GA 快照为 6.19.10。 |
| **Debian trixie-backports 是否有 Mesa** | 抓取 `mesa-vulkan-drivers` 返回空，**可能只是尚未 backport 或包名不同**，未做二次确认。 |
| **三套方案的实际帧率增益** | 不存在公开的同机对照基准；本报告的量级判断来自前 13 轮的结构性分析 + 一手版本差异。 |
| **Slowroll 的长期项目承诺** | Slowroll 是 openSUSE 相对较新的变体，其长期维护承诺与社区规模**弱于 Tumbleweed**，未取得官方路线图确认。 |

---

## 9. 参考来源（本轮一手探测 + 前序报告）

**本轮直接 HTTP 探测（2026-10-16）**
- Arch 仓库：`https://geo.mirror.pkgbuild.com/{core,extra}/os/x86_64/`（mesa 1:26.2.4-1、linux 7.2.9.arch1）
- openSUSE 仓库：`https://download.opensuse.org/{tumbleweed,slowroll}/repo/oss/x86_64/`（Mesa 26.2.4 / 26.2.3；kernel-default 7.2.10 / 7.2.8；gamemode 1.8.2；mangohud 0.8.4；scx 1.1.3）
- Fedora：`https://dl.fedoraproject.org/pub/fedora/linux/{releases,updates}/44/Everything/x86_64/os/Packages/`（mesa-vulkan-drivers 26.0.3 GA → 26.2.4 updates；kernel 6.19.10；无 scx 包）
- Debian：`https://deb.debian.org/debian/dists/{trixie,sid}/main/binary-amd64/Packages.gz`（25.0.7 / 26.2.4；内核 6.12.107；无 amd64v3 组件）
- Ubuntu：`http://archive.ubuntu.com/ubuntu/dists/resolute/main/binary-amd64/Packages.gz`（mesa-vulkan-drivers 26.0.3-1ubuntu1）
- Solus：`https://packages.getsol.us/{shannon,polaris,unstable}/m/mesalib/`（25.2.5 / 26.1.8 / 26.2.1；linux-current 6.16.12、linux-lts 6.12.52）
- Mesa 官方发布节奏：https://www.mesa3d.org/news/（26.2.4 于 2026-10-01 发布）

**前序 13 轮报告（本工作区 `../cachyos/`）**
- `distro-performance-comparison.md`（六发行版横比 + 方法论 + Phoronix 9950X 59 项）
- `cachyos-vs-{arch,fedora,opensuse,ubuntu2604,nixos2605}.md`（五份一对一）
- `cpu-bound-sim-games-optimization.md`（场景 ① 的结构性分析）
- `proton-games-optimization.md` / `proton-cachyos-and-flatpak.md`（场景 ② 的结构性分析 + 部署变体）
- `x86-64-v3-mesa-by-distro.md`（各发行版 v3 Mesa 供给）
- `ubuntu2604-kernel-and-mesa-ppa.md`（Ubuntu 第三方内核/PPA 取舍）
- `gaming-optimization-deepdive.md`（四层优化清单）

**同仓库其他会话的相关成果**
- `opensuse-slowroll-vs-tumbleweed/openSUSE-Slowroll-vs-Tumbleweed-深度研究报告.md`（2026-10-15，另一会话）：对两个 openSUSE 变体做了逐包版本比对与 openQA 证据，**与本报告"Slowroll 只滞后 ~2 周"的实测互相印证**。
- `linux-distro-research/`、`nixos-amd-guide.md`（同仓库，主题相邻）

**外部**
- [openSUSE News — Tumbleweed Monthly Update（Slowroll 滞后 5–10 天的官方口径）](https://news.opensuse.org/2025/01/29/tw-monthly-update-january/)
- [ProtonDB — 发行版实测分布（Solus 4.9 / kernel 7.2.6）](https://www.protondb.com/app/1332010)
- [linuxmi — Solus 4.9 发布](https://www.linuxmi.com/tag/solus)
- [Phoronix — Operating Systems 评测列表](https://www.phoronix.com/reviews/Operating+Systems)
