---
id: linux-gaming-distro-choice-2026
title: 稳定优先下 Linux 游戏发行版选型（排除 CachyOS，三场景 × 8 候选）
tags:
  - linux-gaming
  - distro-selection
  - opensuse
  - bazzite
  - fedora-atomic
  - kubuntu
  - nixos
  - mesa
  - proton
  - stability
  - snapper
  - btrfs
  - cachyos
created: 2026-10-16
updated: 2026-10-19
version: 2.2
status: stable
source: 本机直接 HTTP 抓取各发行版官方仓库/镜像/GitHub API/nixpkgs 源文件（openSUSE TW+Slowroll、Arch、Fedora 44、Ubuntu 26.04+26.10、NixOS 26.05、Bazzite、CachyOS-PKGBUILDS 源码）+ 前 15 轮报告（Phoronix 基准、proton-cachyos GitHub Releases、flatpak issue #6199、ublue Containerfile）+ 结构性推断
confidence: 已核实
---

# 稳定优先下 Linux 游戏发行版选型（排除 CachyOS）

## TL;DR

**① CPU 密集原生 → openSUSE Slowroll；② CPU 密集 Proton → openSUSE Tumbleweed；③ GPU 密集 Proton → openSUSE Tumbleweed（AMD）/ Kubuntu 26.04 LTS（NVIDIA）。只装一个系统选 openSUSE Slowroll。**

**v2.0 新增关键判断**：**Bazzite 是全场唯一"游戏栈全预装 + 原子回滚 + 自带 CachyOS 调度器"的选项** —— 若这台机器是**纯游戏机**，它在三个场景都可以取代上述答案；若为**主力工作机**，openSUSE 系更合适（因 Bazzite 不可变 + 每日自动更新）。

根本原因：**原生游戏的瓶颈在硬件，发行版贡献 ≈ 0**（游戏二进制厂商预编译）→ 该把稳定性拉满；**Proton 场景的唯一杠杆是翻译层与图形栈时效性** → 要最新版 + 能兜底的滚动发行。

**v2.1 关键修正 —— 三条"隐藏门槛"**（不体现在任何版本对照表里，却直接决定游戏能不能跑）：

1. **openSUSE 默认不装 32 位 Vulkan** → Steam 里的 Proton 游戏**黑屏 / 崩溃**。修：`sudo zypper in libvulkan_radeon-32bit`
2. **openSUSE 的 NVIDIA 走 KMP 内核模块包 → 内核升级即驱动损坏**（6.18 事件）→ **改写场景 ③ 裁决：NVIDIA 用户不推荐 openSUSE**
3. **NixOS `hardware.graphics.enable32Bit` 默认 `false`** → 漏设则 Proton 崩溃

**v2.2 关键修正 —— "都装 snapper" 是个假命题**：snapper 只是快照引擎，**它不知道你刚装了个包，也不会出现在 GRUB 菜单里**。真回滚能力取决于 ① 事务钩子 ② GRUB 集成 ③ `/boot` 在 Btrfs 内。补齐后：**Arch 三件套全在官方 `extra`（唯一）**；**Kubuntu 有 `apt-btrfs-snapshot` 钩子但无 `grub-btrfs`**；**Fedora 44 的 snapper 钩子是 dnf4 插件、而 F42 起已无 dnf4 → 死包，且 `/boot` 是 ext4**。详见 §5。

**CachyOS 裁决（v2.2 补）**：它在 snapper 这条线上**全场最强**（`cachyos-snapper-support` 硬依赖 `snap-pac` + `grub-btrfs-support` 预接线 + 安装器送"出厂快照"），**但这条优势优化的是"出错后能救"，不是"会不会出错"**。→ 纯游戏机/双系统/愿维护 = 适合；主力工作机/求稳 = 不适合。

---

## 1. 三场景 × 8 候选 裁决矩阵

| 候选 | ① CPU 原生 | ② CPU Proton | ③ GPU Proton (AMD) | ③ GPU Proton (NVIDIA) | 关键判据 |
|---|---|---|---|---|---|
| **openSUSE Slowroll** | 🥇 **冠军** | 🥈 备选 | 🥈 备选 | 🥈 备选 | 月度更新 + **默认 Btrfs+snapper** + 内核 7.2.8；Mesa 仅滞后 TW 2 周 |
| **openSUSE Tumbleweed** | 🥉 可用 | 🥇 **冠军** | 🥇 **冠军** | ❌ **不推荐**（KMP 驱动） | Mesa 26.2.4 + 内核 7.2.10 双料最新；**官方 scx 1.1.3**；⚠️ **NVIDIA 走 KMP 模块，内核升级即损坏** |
| **Bazzite**（Fedora 44 Atomic） | 🥈 **亚军** | 🥈 **强亚军** | 🥈 **强亚军** | 🥈 **亚军** | 游戏栈全预装 + **原子回滚 + greenboot** + **CachyOS COPR 的 scx-scheds** |
| **Arch** | ❌ 无默认回滚 | 🥉 | 🥉 | 🥉 | 性能同档 TW，输在"炸了要自己救" |
| **Fedora 44 KDE** | ⚠️ | ⚠️ | ⚠️ | ⚠️ | Mesa 26.2.4 + 内核 7.2.10 都最新，但**官方无 scx + 无默认回滚** |
| **Kubuntu 26.04 LTS** | ⚠️ | ❌ Mesa 落后 | ⚠️ | 🥇 **冠军** | N 卡用专有驱动 → Mesa 无关；驱动分发最省事 + LTS 到 2031。⚠️ 只有 Wayland，无 X11 兜底 |
| **Kubuntu 26.10** | ⚠️ | ⚠️（跑分第一） | ⚠️（跑分第一） | ⚠️ | **Mesa 26.2.4 + 内核 7.3.0 全池最新，但无回滚 + 仅 9 个月** |
| **NixOS 26.05** | ⚠️ | ❌ | ❌ | ❌ | 回滚最强，**游戏栈时效性最弱**（Mesa 26.1.8） |

---

## 2. 一手版本对照（2026-10-16 直接抓取官方仓库）

基准点：**Mesa 26.2.4 发布于 2026-10-01，当前最新稳定版**。

| 候选 | Mesa | 内核 | 更新模型 | 默认回滚 | scx | ISA 基线 |
|---|---|---|---|---|---|---|
| openSUSE Tumbleweed | **26.2.4** | **7.2.10** | 滚动（日快照） | ✅ Btrfs+snapper | ✅ 官方 1.1.3 | **v2** |
| openSUSE Slowroll | 26.2.3 | 7.2.8 | 滚动（月批量） | ✅ 同 TW | ✅ 官方 | **v2** |
| Arch Linux | **26.2.4** | 7.2.9.arch1 | 滚动（日） | ⚠️ 需手动 | ⚠️ AUR | v1（+ALHP v3/v4） |
| Fedora 44 KDE | **26.2.4** | **7.2.10** | 6 个月 + 滚动 | ⚠️ 需手动 | ❌ **官方无** | v1（v3 ≥F46） |
| Kubuntu 26.04 LTS | 26.0.3 | 7.0.0-14 | LTS 2 年 + HWE | ❌ | ❌ | v1（+实验 amd64v3） |
| **Kubuntu 26.10** | **26.2.4** | **7.3.0-9.9** ⭐ | 9 个月 | ❌ | ❌ | v1（+**amd64v3 官方架构**） |
| NixOS 26.05 | **26.1.8** | **6.18 默认** / 7.2 可选 | 6 个月 + 声明式 | ✅✅ 最强 | ✅ 有 scx 包 | v1（v3 需自编） |
| **Bazzite**（F44 Atomic） | **26.2.4** | 7.2.9-ogc3.1 | 镜像化，每日自动 | ✅✅ **原子 + greenboot** | ✅ **CachyOS COPR 1.1.4** | v1 |

**六条关键读数**：
1. **Kubuntu 26.10 是全池性能最高的**（Mesa 26.2.4 + 内核 7.3.0），但**无回滚 + 仅 9 个月** → 与"稳定优先"冲突。
2. **Bazzite 是唯一"游戏栈全预装"的**：gamescope 3.16.31 + Gamescope Session + MangoHud 0.8.4 + UMU 1.4.4 + ScopeBuddy + Distrobox 1.8.2.5。
3. **Bazzite 从 `bieszczaders/kernel-cachyos-addons` COPR（CachyOS 维护者 sirlucjan 维护）装 `scx-scheds` + `scx-tools`** —— 非 CachyOS 发行版里唯一自带 CachyOS 生态调度器。
4. **Fedora 44 官方确认无 `scx-scheds`**（`packages.fedoraproject.org` / `src.fedoraproject.org` 均 404）。
5. **NixOS 26.05 实测**：Mesa **26.1.8**（`common.nix`）；默认内核 **6.18**（`linux_default = linux_6_18`，≥6.14 故有 NTSync）；**有 `scx` 包**。→ v1.0 的"未核实"闭环。
6. **openSUSE 是唯一官方仓库同时有 scx + gamemode + mangohud + steam 的**（除 Bazzite 的 COPR 路线）。

### 2.2 三条"隐藏门槛"（v2.1 补入 —— 装完才发现就晚了）

| 门槛 | 命中哪些候选 | 症状 | 修法 |
|---|---|---|---|
| **32 位 Vulkan 库** | **openSUSE TW / Slowroll 默认不装**；**NixOS `hardware.graphics.enable32Bit` 默认 false** | Steam 里的 Proton 游戏**黑屏 / 启动即崩溃** | openSUSE：`sudo zypper in libvulkan_radeon-32bit`（AMD）/ `libvulkan_intel-32bit`（Intel）；NixOS：`hardware.graphics.enable32Bit = true;` |
| **NVIDIA 驱动 = KMP 内核模块包** | **openSUSE TW / Slowroll** | **内核一升级，NVIDIA 驱动直接损坏**（社区已记录 6.18 事件），须回退旧内核等 KMP 重编 | **无优雅解** → **NVIDIA 用户应避开 openSUSE 滚动** |
| **NTSync 是否默认加载** | 全部（内核 ≥ 6.14 都有模块，差别在**是否默认加载**） | 未加载 → 1% low 与 alt-tab 退化（平均帧几乎不变） | `sudo sh -c 'echo ntsync > /etc/modules-load.d/ntsync.conf'`；**Fedora 44 是首个用 `wine-ntsync` 包默认启用的发行版** |

**对比**：**Arch 的 32 位 Vulkan 在 multilib 开箱即有**（Proton 零配置）；**Bazzite 预装全部游戏栈**。

---

## 3. 三场景的有效杠杆

| 场景 | 瓶颈 | 发行版能碰到的杠杆 | 占比 |
|---|---|---|---|
| ① CPU 密集原生 | 单核 IPC×频率、内存延迟、L3 | 内核内存管理（MGLRU/THP/ZRAM/swappiness）+ 调度延迟层 | **极小** |
| ② CPU 密集 Proton | 翻译开销 + 同步开销 | **翻译层 + 运行时栈**（Wine/DXVK/vkd3d/Mesa 的构建与版本）+ NTSync + 调度 | **中** |
| ③ GPU 密集 Proton | GPU 算力 / 驱动效率 | **GPU 驱动版本**（Mesa RADV / NVIDIA）+ 内核 amdgpu 修复 + 升频 | **中** |

**推论**：① 发行版无关 → 优化目标 = 稳定性最大化；②③ 时效性是硬指标 → 优化目标 = 最新版 + 回滚兜底。

---

## 4. "稳定"的三个独立维度

| 维度 | 含义 | 谁给得了 |
|---|---|---|
| ① 更新频率可控 | 不会某天被迫接受 500 个包 | 固定周期（Fedora/Kubuntu/NixOS）或慢速滚动（**Slowroll**）> 日滚动（TW/Arch/**Bazzite 默认**） |
| ② 出问题能回滚 | 升级炸了能一键退回 | **Bazzite（原子镜像 + greenboot 自动健康检查）≈ openSUSE（Btrfs+snapper 原生）> CachyOS（snapper 三件套预接线）> Arch（三件套齐备但需自配）> Kubuntu（有 APT 钩子、无 GRUB 救生艇）> Fedora 44（Btrfs 下等于无，见 §5）** |
| ③ 软件质量（不追新） | 测试窗口更长 | Kubuntu LTS / NixOS stable / Slowroll > Fedora / TW > Arch |

**关键校准**：③ 被高估。滚动的包不是"未测试的"，只是"测试窗口短"；真风险是你的硬件组合踩到回归 —— 此时 **② 比 ③ 重要得多**。这是 openSUSE 系与 Bazzite 共同胜出的根本原因。

---

## 5. snapper 真实回滚能力矩阵（v2.2 新增，第 16 轮）

### 5.1 核心判断：装 snapper ≠ 有回滚能力

**snapper 只是快照引擎，它不知道"你刚装了个包"，也不会出现在 GRUB 菜单里。** openSUSE 的"原子回滚"体验由四个部件拼成，snapper 只是其中之一：

| 部件 | 作用 | 缺了会怎样 |
|---|---|---|
| ① 快照引擎 `snapper` | 创建/比较/清理，多套配置 | — |
| ② **事务钩子** | 装包前自动拍 pre、装完拍 post 并配对 | 只有手动快照 → 出事时那张"昨天的"快照可能已过期 |
| ③ **GRUB 启动集成** | 快照变成 GRUB 菜单项 | **开不了机时 snapper 完全无用**，只能 Live USB |
| ④ **`/boot` 在 Btrfs 内** | 内核/initramfs 一起进快照 | 回滚 `/` 后内核不匹配 → 开不了机 |

ArchWiki 原文（④）：`/boot` 在非 Btrfs 分区时 **"you are not able to do snapper backups with it"**。

### 5.2 一手核实矩阵（2026-10-19）

| 部件 | Arch | Fedora 44 KDE | Kubuntu 26.04 | Kubuntu 26.10 | CachyOS |
|---|---|---|---|---|---|
| ① `snapper` | ✅ `extra 0.13.2-1` | ✅ `0.13.0-3.fc44` | ✅ universe | ✅ universe | ✅（Arch 源） |
| ② 自动钩子 | ✅ **`extra/snap-pac 3.0.1-3`** | ❌ **`python3-dnf-plugin-snapper 4.1.2-11.fc44` 是 dnf4 插件，F42 起已无 dnf4 → 死包** | ✅ **`apt-btrfs-snapshot 4.0.1build1`**（universe，原生 APT 钩子） | ✅ 同左 | ✅ **预接线**（`cachyos-snapper-support` 硬依赖 `snap-pac`） |
| ③ GRUB 集成 | ✅ **`extra/grub-btrfs 4.14-1`** | ❌ 全库无 | ❌ archive 无 | ❌ | ✅ **预接线**（`grub-btrfs-support` + systemd `.path` 监听 `/.snapshots`） |
| ④ `/boot` 默认布局 | 自选（须放 Btrfs） | ❌ **ext4 独立分区**（Anaconda 预设原文） | 自选（须放 Btrfs） | 同左 | Btrfs（推断，中置信） |
| 子卷默认 | 自建 | `root` + `home`，**无 `/.snapshots`** | `@` + `@home` | 同左 | 含 `@snapshots`（推断） |
| GUI | `btrfs-assistant 3.0.0` | `btrfs-assistant` | `btrfs-assistant 2.2` + `snapper-gui` | ✅ | `btrfs-assistant` |

**Fedora 的隐藏陷阱**：`python3-dnf-plugin-snapper` 在 F44 仓库里**仍在构建**（4.1.2-11.fc44），名字对得上，但 dnf4 本体从 F42 起不再随发行版提供（`dnf` 包页只列到 Fedora 41）。dnf5 用 C++ 插件（`libdnf5-plugin-actions/txnupd/cow/notify`），**无 snapper 插件**。→ **装了不工作，且不报错。**

### 5.3 Fedora 的第三条路：snapm + boom-boot（LVM/Stratis only）

| 包 | F44 版本 | 能力 |
|---|---|---|
| `snapm` | `0.7.0-5.fc44` | **Bootable snapshots**：生成 GRUB 快照启动项 + failsafe revert |
| `boom-boot` | `1.6.8-5.fc44` | BLS 启动条目管理器 |

```bash
sudo dnf install snapm boom-boot
sudo snapm snapset create --bootable --revert pre-update / /home
sudo snapm snapset revert pre-update && sudo reboot
```
**但 snapm 后端只支持 LVM2（CoW/Thin）和 Stratis —— 明确不支持 Btrfs。** 想用必须放弃 Fedora 的 Btrfs 默认布局，改 LVM + XFS。好处：**LVM 快照含 `/boot`，内核一起回滚**，且与 Fedora 的 BLS 机制原生兼容；坏处：非事务级触发（靠 systemd timer 或手动）。

### 5.4 补齐后评级

| 方案 | 自动拍 | GRUB 菜单 | 含内核 | 开箱程度 | 评级 |
|---|---|---|---|---|---|
| openSUSE TW/Slowroll | ✅ zypp | ✅ 内建 | ✅ | 安装器默认 | **A+** |
| **CachyOS** | ✅ snap-pac | ✅ grub-btrfs-support | ✅ | **装完即有出厂快照** | **A+** |
| Arch + 三件套 | ✅ snap-pac | ✅ grub-btrfs | ✅ | 需自配 30–45 min | **A** |
| Fedora 44 + LVM/XFS + snapm | ⚠️ timer | ✅ boom-boot | ✅ | 手动分区 | **B+** |
| Kubuntu 26.04 + snapper | ✅ apt-btrfs-snapshot | ❌ | ✅ | 钩子即装即用 | **B** |
| Fedora 44 + Btrfs + snapper | ❌ | ❌ | ❌ | — | **F** |

### 5.5 回滚能力 ≠ 稳定性（两个正交维度）

| 维度 | 问题 | snapper 能改善 |
|---|---|---|
| 会不会出错 | 更新引入回归、驱动崩、内核不兼容 | ❌ 完全不能 |
| 出错后能不能救 | 有没有退路、多快 | ✅ 这是它的全部价值 |

snapper 把"踩到回归"从**灾难**降为**麻烦**，但麻烦仍是麻烦：中断工作 → 重启 → 进快照 → rollback → 再重启 → 重新登录 → 恢复现场。**一天一次，这天就废了一半。**

### 5.6 CachyOS 条件性裁决（回答"适合吗"）

**它在 snapper 这条线上是全场最强，没有第二。** 一手证据（`CachyOS/CachyOS-PKGBUILDS` master）：

- `cachyos-snapper-support 1.0.2-1`：`depends=(snapper snap-pac)`、`conflicts=(timeshift)`，装 `cachyos-root` 模板，`post_install` 执行 `systemctl enable --now snapper-cleanup.timer` + `snapper -c root create-config --template cachyos-root /`；**`snapper-timeline.timer` 被注释掉**（不做每小时快照）
- 模板关键值：`TIMELINE_CREATE="no"`、`NUMBER_LIMIT="50"`、`NUMBER_LIMIT_IMPORTANT="15"`、`SPACE_LIMIT="0.5"`、`FREE_LIMIT="0.2"`
- `grub-btrfs-support 1.0.0-1`（维护者 ptr1337）：`depends=(cachyos-snapper-support grub-btrfs)`，装 `grub-btrfs-snapper.path`（`PathModified=/.snapshots`）+ `.service`（调 `/etc/grub.d/41_snapshots-btrfs`）
- 安装器 `btrfs-installation-snapshot`：装完立即 `snapper create --description "Fresh CachyOS Installation" --userdata "important=yes"`，ID 存入 `/etc/cachyos/installation-snapshot` → **一键回到出厂**

**代价**：滚动（无 Slowroll 等价物）、核心维护者个位数、内核带 BORE/sched-ext 补丁 + 额外 CFLAGS → 出问题时排查路径比 Arch 长、性能收益个位数百分比且 CPU 密集原生游戏 ≈ 0。

| 你的情况 | 适合 CachyOS？ |
|---|---|
| 纯游戏机 + 愿意每月花点时间看更新 | ✅ 适合（省下的调优时间 > 维护时间） |
| 主力工作机 + 求稳 | ❌ 不适合（一次回归 = 半天报废） |
| 双系统 / 有备用机 | ✅ 适合（风险隔离） |
| 只要 CPU 密集原生游戏 | ❌ 不值得（收益 ≈ 0） |
| GPU 密集 Proton + AMD | ⚠️ Arch 官方同样新，CachyOS 增量小 |
| 想省调优但要 Arch 生态 | ✅ 适合（本质是"Arch + 现成调优 + 现成快照栈"） |

**一句话**：CachyOS 是"Arch 的最佳发行版形态"，但它仍然是 Arch。**它把退路做到最好，同时把风险也抬高了。**

### 5.7 可复用操作

**Arch 三件套**（全在 `extra`，无需 AUR）：
```bash
sudo pacman -S snapper snap-pac grub-btrfs btrfs-assistant
sudo snapper -c root create-config /
# 若已有 /.snapshots 子卷，替换 snapper 新建的那个
sudo btrfs subvolume delete /.snapshots && sudo mkdir /.snapshots
sudo btrfs subvolume create /.snapshots && sudo chmod 750 /.snapshots
sudo systemctl enable --now snapper-cleanup.timer grub-btrfsd
# 验收：装个包看是否生成 pre/post 对
sudo pacman -S htop && sudo snapper -c root list
```
子卷布局（UEFI）：`@`→/、`@home`、`@log`、`@cache`、`@snapshots`→/.snapshots、**`@boot`→/boot（必须是 Btrfs 子卷，不能是 ext4 分区）**，ESP 挂 `/boot/efi`。

**Kubuntu 26.04**：安装时手动把 `/` 选 **Btrfs**（默认 ext4，不改就白搭），然后 `sudo apt install apt-btrfs-snapshot`。**`apt-btrfs-snapshot` 与 `snapper` 是两套体系（前者 `@apt-snapshot-*`，后者 `/.snapshots/<N>/`），选一套别混。** 救生艇必须提前演练：Live USB + `mount -o subvol=@` + bind mount + chroot。

**Fedora 44**：Btrfs + snapper 这条路放弃；要回滚就走 LVM/XFS + `snapm`/`boom-boot`。

### 5.8 新增坑（第 16 轮）

1. **`python3-dnf-plugin-snapper` 在 Fedora 44 是死包** —— 包在构建、宿主 dnf4 已停供，装了不工作且无提示。
2. **Fedora 的 `/boot` 是 ext4** —— Anaconda Btrfs 预设原文 "creates an ext4 /boot"，快照永远不含内核。
3. **`grub-btrfs` 只在 Arch 官方仓库** —— Fedora 全库无、Ubuntu archive 无。这是"能不能从菜单进快照"的唯一开关。
4. **`snapm` 不支持 Btrfs** —— 只支持 LVM2/Stratis。
5. **`/.snapshots` 必须是独立子卷** —— 否则是嵌套子卷，清理/配额行为异常。
6. **CachyOS 模板默认 `TIMELINE_CREATE="no"`** —— 只有 pacman 事务快照，无每小时快照（安装脚本里 timeline 那行是注释掉的）。
7. **`grub-btrfs` 读只读快照需 overlayfs hook** —— 且**不兼容 systemd initramfs**（须 Busybox initramfs）。
8. **`snapper rollback` 后 GRUB 默认项未必更新** —— 回滚后须 `grub-mkconfig` 或手动选一次。
9. **`snap-pac` 断电会留 pre 孤儿** —— 用 `snapper list --columns number,type,description` 定期清。

---

## 6. Bazzite 解剖（v2.0 新增，本轮最大变量）

**定位**：`Fedora 44 Atomic Desktop`（Kinoite 系，`rpm-ostree` 镜像化）+ ublue 的游戏特化层。

| 维度 | 实测值 |
|---|---|
| 基础镜像 | Fedora 44 Atomic（stable tag `44.20261012.1`，2026-10-13） |
| Mesa | **26.2.4-1**（最新） |
| 内核 | **7.2.9-ogc3.1**（ublue 自编译 `ogc` flavour，**非 Fedora 官方内核**） |
| KDE | 6.7.5 |
| 调度器 | **`scx-scheds` + `scx-tools`，来自 `bieszczaders/kernel-cachyos-addons` COPR** |
| 游戏栈 | gamescope 3.16.31 / Gamescope Session / MangoHud 0.8.4-2 / UMU 1.4.4 / ScopeBuddy / InputPlumber / SteamOS-Manager / PowerStation / Distrobox 1.8.2.5 |
| NVIDIA | 专用镜像预装 **615.78.08（open）/ 580.178.04（LTS）** |
| HDR | ✅ Gamescope HDR 管线（SteamOS 同源） |
| 回滚 | GRUB 选旧镜像 / `rpm-ostree rollback` / `bazzite-rollback-helper` + **`greenboot` 启动健康检查失败自动回滚** |
| 更新 | Desktop 镜像**每日自动**；Deck 镜像手动（可关、可换 stable/testing/unstable） |
| 安全加固 | SELinux、`ublue-os-selinux-workarounds`、`bees`（Btrfs 去重）、`ryzenadj`、`fw-fanctrl` |

**它补上了 Fedora 的三个硬缺口**：① scx（走 COPR）；② 原子回滚 + greenboot 自动健康检查；③ 游戏栈全预装。

**它带来的三个新代价**：① **不可变**（装系统级软件需 `rpm-ostree install` 或 Distrobox）；② **每日自动更新**（与"更新频率可控"冲突，需手动关）；③ **内核是 ublue 自编译**（不在 Fedora 安全更新覆盖内，补丁集不透明）。

---

## 7. 可复用操作

### 7.1 场景 ①：openSUSE Slowroll

```bash
uname -r                                        # 应 >= 7.2
ls /sys/kernel/sched_ext && echo "sched_ext OK"
ls /dev/ntsync || sudo modprobe ntsync          # NTSync 需内核 >= 6.14

sudo zypper install gamemode mangohud scx steam # 全部官方仓库
sudo zypper install libvulkan_radeon-32bit      # ★ 32 位 Vulkan，Proton 必需（默认不装）
sudo zypper install systemd-zram-service

sudo tee /etc/sysctl.d/99-gaming.conf <<'EOF'
vm.swappiness=100
vm.vfs_cache_pressure=50
vm.dirty_ratio=10
vm.dirty_background_ratio=5
EOF
sudo sysctl --system

echo 'defer+madvise' | sudo tee /sys/kernel/mm/transparent_hugepage/defrag
sudo snapper list && sudo snapper rollback <编号>   # 出事回滚
```

### 7.2 场景 ②：openSUSE Tumbleweed —— 把 CachyOS 冠军项"打包带走"

```bash
sudo zypper install gamemode mangohud scx steam
sudo zypper install libvulkan_radeon-32bit      # ★ 32 位 Vulkan（默认不装，漏了 Proton 黑屏）

# proton-cachyos 官方发独立 x86_64_v3 tarball，任何发行版可用，无需装 CachyOS
TAG="cachyos-11.0-20261005-slr"                 # 用前先查最新 tag
mkdir -p ~/.steam/root/compatibilitytools.d
curl -LO "https://github.com/CachyOS/proton-cachyos/releases/download/$TAG/proton-cachyos-11.0-20261005-slr-x86_64_v3.tar.xz"
tar -xf proton-cachyos-11.0-20261005-slr-x86_64_v3.tar.xz -C ~/.steam/root/compatibilitytools.d/

ls -l /dev/ntsync
MANGOHUD=1 MANGOHUD_CONFIG=fps,frametime,gpu_util %command%   # GPU < 90% 才是 CPU 受限
```

### 7.3 场景 ③：AMD → TW；NVIDIA → Kubuntu 26.04 LTS

```bash
# AMD
sudo zypper install mesa-vulkan-drivers mesa-dri-drivers vulkan-tools
sudo zypper install libvulkan_radeon-32bit      # ★ 32 位 Vulkan，Proton 必需
vulkaninfo --summary | grep -E "driverName|driverInfo"

# NVIDIA (Kubuntu 26.04 LTS；注意只有 Wayland)
#   ⚠️ 不要用 openSUSE 滚动 —— NVIDIA 驱动是 KMP 内核模块包，内核升级会直接损坏驱动
ubuntu-drivers devices && sudo ubuntu-drivers install && nvidia-smi

# 可选：整体切 amd64v3（官方提供，实测含 mesa-vulkan-drivers）
echo 'APT::Architecture-Variants "amd64v3";' | sudo tee /etc/apt/apt.conf.d/99enable-amd64v3
sudo apt update && sudo apt full-upgrade

flatpak install flathub com.valvesoftware.Steam
flatpak install flathub org.freedesktop.Platform.VulkanLayer.MangoHud
```

### 7.4 【替代路线】Bazzite（三场景通用）

```bash
# 安装：https://bazzite.gg/ 按硬件/桌面选镜像（AMD / NVIDIA / 掌机 / Deck 版）

rpm-ostree status                  # 看当前镜像与可回滚版本
ujust --help                       # 看可用任务；在 Bazzite Portal 关自动更新

rpm-ostree rollback                # 出事回滚
bazzite-rollback-helper list && bazzite-rollback-helper rebase <旧版本>

scxctl start -s scx_bpfland        # 调度器已预装（来自 CachyOS COPR）
ls /dev/ntsync                     # 内核 7.2.9 >= 6.14

sudo tee /etc/sysctl.d/99-gaming.conf <<'EOF'
vm.swappiness=100
vm.vfs_cache_pressure=50
EOF
sudo sysctl --system

rpm-ostree install <pkg>           # 不可变系统装系统级软件（会叠加一层，慎用）
distrobox create --image archlinux:latest --name arch   # 更推荐
```

---

## 8. 坑与反直觉

| 坑 | 说明 |
|---|---|
| "换个发行版游戏就快了" | ❌ 原生游戏几乎为零；Proton 是个位数百分比。**硬件（X3D/内存/GPU）才是最大杠杆。** |
| "Kubuntu 26.10 版本最新所以最好" | ❌ 最新 ≠ 最适合。它**无任何回滚 + 仅 9 个月支持** → 对"稳定优先"是负分。 |
| "Bazzite 就是个 Fedora 皮肤" | ❌ 它补了 Fedora 三个硬缺口：**scx（CachyOS COPR）**、**原子回滚 + greenboot**、**游戏栈全预装**。 |
| **"Bazzite 自带 CachyOS 内核"** | ❌ 用的是 **ublue 自编译的 `ogc` flavour**，不是 `linux-cachyos`。**只有 `scx-scheds`/`scx-tools` 来自 CachyOS 维护者的 COPR。** |
| "不可变系统不能调游戏参数" | ❌ 可以。`/etc/sysctl.d` 可写、`/sys/kernel/mm/...` 运行时可变、ZRAM 用 `zram-generator`。**只有内核参数需 `rpm-ostree kargs`。** |
| "Debian 最稳所以最适合游戏" | 稳定 ≠ 适合。Mesa 25.0.7 / 内核 6.12 是实打实损失，且**无默认回滚**。 |
| "Arch 比 TW 快" | 实测**同档**（都 Mesa 26.2.4）。差异在运维模型。 |
| "Slowroll 是降级版" | ❌ 实测只滞后 ~2 周。降的是**更新频率**，不是**版本水平**。 |
| "v3 重编译能提升帧数" | 收益极小且零散。RADV 着色器编译走 LLVM，与宿主 ISA 基本无关。**Mesa 版本 ≫ Mesa 的 ISA 级别。** |
| "装 proton-cachyos 必须用 CachyOS" | ❌ 官方发独立 `x86_64_v3` tarball，任何发行版可用。 |
| "Fedora 的 SELinux 拖慢游戏" | 影响可忽略，不是不推荐它的理由（理由是无 scx + 无回滚 + NVIDIA 需 RPM Fusion）。 |
| "Ubuntu 26.04 移除 X11 无所谓" | 图形栈出问题**没有 X11 兜底**，排查难度高于 24.04。N 卡尤其注意。 |
| "NixOS 游戏栈太旧" | 半对：Mesa 26.1.8 确实偏旧，但它有 scx 包、内核 6.18（含 NTSync）、回滚最强。问题是**配置成本**与**时效性跟不上**。 |
| **"openSUSE 官方有 NVIDIA 驱动所以 N 卡没问题"** | ❌ **反了**。TW / Slowroll 的 NVIDIA 是 **KMP 内核模块包**，**内核一升级驱动就损坏**，要回退旧内核等重编。**N 卡用户应避开 openSUSE 滚动。** |
| **"装完 Steam 就能玩 Proton"** | ❌ **openSUSE 默认不装 32 位 Vulkan** → Proton **黑屏 / 崩溃**。必须 `sudo zypper in libvulkan_radeon-32bit`。 |
| **"NixOS 的 Steam 配置照抄就行"** | ❌ `hardware.graphics.enable32Bit` **默认 false** → 漏设则 Proton 黑屏。 |
| **"scx 调度器 = 装上就行"** | ⚠️ 要挑对。**`scx_lavd` 是 Igalia 为 Steam Deck 开发的游戏向低尾延迟调度器**。TW 还**缺 `scx_loader.service`**（未打包）→ 无自动切换。 |
| **"RimWorld 卡顿要换图形栈"** | ❌ 反了。RimWorld 是**单线程 TPS 瓶颈**，图形栈几乎无关。该做：`taskset` 绑核 + `scx_lavd` + governor `performance` + **Performance Fish 模组**（社区公认后期提升最大）。 |
| **"Fedora 的游戏栈比 openSUSE 差"** | ❌ 部分反了。**Fedora 44 是首个用 `wine-ntsync` 包默认启用 NTSync 的发行版**，这点比 openSUSE 强。 |

---

## 9. 未核实 / 存疑

| 项 | 说明 |
|---|---|
| **Bazzite `ogc` 内核 flavour 的补丁集** | 仅确认 flavour 名与版本号（7.2.9-ogc3.1），**未取得补丁清单**（是否含 BORE / fsync / 游戏向补丁不明）。 |
| **Bazzite stable 跟随 Fedora 44 → 45 的时间点** | 抓取时 `unstable-45` 已在构建、`fedora-release-common` 44-18 → 45-0.10，**stable 迁移时点未确认**。 |
| **Kubuntu 26.04 LTS 的 NVIDIA 驱动版本** | 本轮未测。 |
| **Bazzite 与 openSUSE 的同机游戏对照** | 不存在。**Bazzite 在场景 ②③ 与 TW 的"胜负"是结构性推断**，不是实测。 |
| 三套方案的实际帧率增益 | 无公开同机对照基准；量级判断来自结构分析 + 一手版本差异。 |
| Slowroll 的长期项目承诺 | 维护承诺与社区规模**弱于 Tumbleweed**，未取得官方路线图确认。 |
| NixOS 26.05 的游戏实测 | **Phoronix 从未做过含 NixOS 的发行版横评**，性能结论全部基于结构性推断。 |
| **openSUSE 的 `scx_loader.service` 打包状态** | 另一会话 2026-10-12 报告称"安全审查中、尚未打包"；本轮未复核。 |
| **Fedora 44 / Kubuntu 的 32 位 Vulkan 默认状态** | 本轮未逐一核实（Arch 已确认 multilib 开箱即有；openSUSE 与 NixOS 已确认有坑）。 |

---

## 10. 参考来源

**本轮直接 HTTP 探测（2026-10-16）**
- **Bazzite**：`https://api.github.com/repos/ublue-os/bazzite/releases`（stable `44.20261012.1`：Mesa 26.2.4-1 / 内核 7.2.9-ogc3.1 / gamescope 3.16.31 / MangoHud 0.8.4-2 / KDE 6.7.5 / NVIDIA Open 615.78.08 / NVIDIA LTS 580.178.04；unstable `45.20261016`：scx-scheds 1.1.3-3 → 1.1.4-1）；`raw.githubusercontent.com/ublue-os/bazzite/main/Containerfile`（`KERNEL_FLAVOR=ogc`；**`dnf5 -y copr enable bieszczaders/kernel-cachyos-addons` + `dnf5 -y install scx-scheds scx-tools`**；`greenboot`、`ScopeBuddy`、`bpftune-gaming`）；`https://docs.bazzite.gg/General/FAQ/` 与 `/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/`；`https://copr.fedorainfracloud.org/api_3/build/list/?ownername=bieszczaders&projectname=kernel-cachyos-addons`（`source_package.name = scx-scheds`，submitter `sirlucjan`）
- **Kubuntu 26.10**：`http://archive.ubuntu.com/ubuntu/dists/stonking/Release`（`Version: 26.10`，`Date: Thu, 15 Oct 2026`，`Architectures: amd64 amd64v3 arm64 armhf i386 ppc64el riscv64 s390x`）+ `dists/stonking/main/binary-amd64/Packages.gz`（mesa-vulkan-drivers 26.2.4-1ubuntu1 / libgl1-mesa-dri 26.2.4-1ubuntu1 / linux-image-generic 7.3.0-9.9 / libc6 2.44-1ubuntu2；6,446 包）
- **Kubuntu 26.04**：`dists/resolute/main/binary-amd64/Packages.gz`（26.0.3-1ubuntu1 / 7.0.0-14）
- **Fedora 44**：`https://dl.fedoraproject.org/pub/fedora/linux/updates/44/Everything/x86_64/Packages/{m,k}/`（mesa-vulkan-drivers-26.2.4-1.fc44.x86_64.rpm / kernel-7.2.10-200.fc44.x86_64.rpm）；`packages.fedoraproject.org/pkgs/scx-scheds/scx-scheds/` → **404**
- **NixOS 26.05**：`raw.githubusercontent.com/NixOS/nixpkgs/nixos-26.05/pkgs/development/libraries/mesa/common.nix`（`version = "26.1.8"`）；`pkgs/top-level/linux-kernels.nix`（`linux_default = packages.linux_6_18`、`linux_latest = packages.linux_7_2`）；`pkgs/os-specific/linux/kernel/kernels-org.json`（6.18.56 / 7.2.10）；`pkgs/os-specific/linux/scx/default.nix` → 200；`rl-2605.section.md`（"Yarara", 2026-05-30）
- **openSUSE**：`https://download.opensuse.org/{tumbleweed,slowroll}/repo/oss/x86_64/`（Mesa 26.2.4 / 26.2.3；kernel-default 7.2.10 / 7.2.8；gamemode 1.8.2；mangohud 0.8.4；scx 1.1.3）
- **Arch**：`https://geo.mirror.pkgbuild.com/{core,extra}/os/x86_64/`（mesa 1:26.2.4-1、linux 7.2.9.arch1）
- **snapper 生态（v2.2）**：`archlinux.org/packages/search/json/?name={snapper,snap-pac,grub-btrfs,btrfs-assistant,snapper-fmt}` → extra 0.13.2-1 / 3.0.1-3 / 4.14-1 / 3.0.0-1 / 0.11.10-1；`packages.fedoraproject.org/pkgs/{snapper/snapper,dnf-plugins-extras/python3-dnf-plugin-snapper,dnf/dnf,snapm/snapm,boom-boot/boom-boot}` → 0.13.0-3.fc44 / 4.1.2-11.fc44 / **仅 F41** / 0.7.0-5.fc44 / 1.6.8-5.fc44；`api.launchpad.net/...getPublishedSources&source_name={apt-btrfs-snapshot,grub-btrfs,btrfs-assistant,snapper-gui}&distro_series=...{resolute,stonking}` → 4.0.1build1 / **404** / 2.2-1 / 0git
- **CachyOS 打包源码**：`raw.githubusercontent.com/CachyOS/CachyOS-PKGBUILDS/master/{cachyos-snapper-support,grub-btrfs-support}/{PKGBUILD,*.install,snapper-template-root-cachyos,grub-btrfs-snapper.path,grub-btrfs-snapper.service}`；`raw.githubusercontent.com/CachyOS/cachyos-calamares/cachyos/src/scripts/btrfs-installation-snapshot`

**外部**
- [openSUSE News — Tumbleweed Monthly Update（Slowroll 滞后 5–10 天官方口径）](https://news.opensuse.org/2025/01/29/tw-monthly-update-january/)
- [Bazzite 官网](https://bazzite.gg/) ｜ [Bazzite 文档](https://docs.bazzite.gg/)
- [Phoronix — Operating Systems 评测列表](https://www.phoronix.com/reviews/Operating+Systems)
- [Mesa 官方发布节奏](https://www.mesa3d.org/news/)
- [Fedora Wiki — Btrfs（Anaconda 预设："creates an ext4 /boot … two subvolumes, root and home"）](https://fedoraproject.org/wiki/Btrfs)
- [snapshotmanager/snapm — Bootable snapshots，后端仅 LVM2/Stratis](https://github.com/snapshotmanager/snapm)
- [Antynea/grub-btrfs — 支持 snapper/timeshift/yabsnap 快照](https://github.com/Antynea/grub-btrfs)
- ArchWiki `Btrfs#Snapper`（`/boot` 在非 Btrfs 分区时无法做 snapper 备份）

---

## 11. 关联文档

- `distro-choice/round16-snapper-comparison-and-cachyos-verdict.md` / `.html`（**第 16 轮完整报告 v1.0**：snapper 真实回滚能力矩阵 + CachyOS 条件性裁决，本文件 §5 的展开版）
- `distro-choice/round15-stability-first-8-candidates.md` / `.html`（**第 15 轮完整报告 v2.1**，本文件的展开版）
- `distro-choice/README.md` / `.html`（第 14 轮：候选池含 Debian 13 / Solus 4.9）
- `../linux-distro-research/reports/linux-gaming-perf-2026-10.md`（**同仓库另一会话 2026-10-12**：六层优化模型 / **32 位 Vulkan 门槛** / **NVIDIA KMP 痛点** / `scx_lavd` 游戏定位 / RimWorld 特化）—— **本文件 v2.1 的"隐藏门槛"来源**
- [`x86-64-v3-mesa-by-distro.md`](./x86-64-v3-mesa-by-distro.md)（各发行版 v3 Mesa 供给）
- [`ubuntu2604-thirdparty-kernel-mesa-ppa.md`](./ubuntu2604-thirdparty-kernel-mesa-ppa.md)（Ubuntu 第三方内核/PPA 取舍）
- `../cachyos/`（前 13 轮：六发行版横比、五份一对一、三份场景专项、四层优化清单）

---

## 12. 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0 | 2026-10-16 | 初版。三场景 × 8 候选（openSUSE TW/Slowroll、Arch、Fedora 44、Ubuntu 26.04、Debian 13、NixOS 26.05、Solus 4.9）裁决矩阵 + 一手版本对照 + 三套落地方案 |
| **2.0** | 2026-10-16 | **候选池替换**：+**Bazzite**（全新，第 15 轮）、+**Kubuntu 26.10**（Mesa 26.2.4 / 内核 7.3.0），Fedora/Ubuntu 明确到 KDE 版，移除 Debian/Solus；**新增 §5 Bazzite 解剖**（Containerfile / CachyOS COPR / greenboot / 游戏栈清单）；**修正 NixOS 26.05 实测值**（Mesa 26.1.8 / 内核 6.18 / 有 scx 包，v1.0 的"未核实"闭环）；§4 "稳定三维度"加入 Bazzite 的原子回滚档位；新增 Bazzite 落地方案 |
| **2.1** | 2026-10-16 | **新增 §2.2 三条"隐藏门槛"**（与同仓库 `linux-distro-research/reports/linux-gaming-perf-2026-10.md` 交叉校验后补入）：① **openSUSE 默认不装 32 位 Vulkan** → Proton 黑屏；② **openSUSE 的 NVIDIA 走 KMP 内核模块包，内核升级即损坏** → **改写 §1 矩阵，NVIDIA 列从"备选"改为"不推荐"**；③ **NixOS `hardware.graphics.enable32Bit` 默认 false**；补入 `scx_lavd` 的游戏向定位与 NixOS 一行声明式启用、**Fedora 44 首个用 `wine-ntsync` 默认启用 NTSync**、RimWorld 特化（`taskset` + Performance Fish）、TW 的 `power-profiles-daemon` / `scx_loader` 缺位；§7 坑表 +7 条 |
| **2.2** | 2026-10-19 | **新增 §5「snapper 真实回滚能力矩阵」**（第 16 轮）：确立**"装 snapper ≠ 有回滚能力"**四部件模型（引擎 / 事务钩子 / GRUB 集成 / `/boot` 在 Btrfs 内）；一手核实 Arch 三件套全在 `extra`、**Fedora 44 的 `python3-dnf-plugin-snapper` 是 dnf4 死包（F42 起无 dnf4）且 `/boot` 为 ext4**、Kubuntu 有 `apt-btrfs-snapshot` 但无 `grub-btrfs`、Fedora 另有 `snapm`+`boom-boot` 但**仅 LVM/Stratis 不支持 Btrfs**；**改写 §4 维度②评级**（Kubuntu/Fedora 重新分档）；**CachyOS 条件性裁决**：snapper 线上全场最强（预接线 + 出厂快照）但仍是 Arch，纯游戏机适合 / 主力工作机不适合；新增 §5.8 坑 9 条 |
