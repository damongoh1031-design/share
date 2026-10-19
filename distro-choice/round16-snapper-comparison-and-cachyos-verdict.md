# 第 16 轮：Arch / Kubuntu / Fedora 都用 snapper 的综合比较 —— 以及 CachyOS 到底适不适合

> 前置约束：**稳定优先，同时尽量发挥硬件**；排除 CachyOS 作为默认答案（本轮改为回答"适合吗"）。
> 核查日期：2026-10-19。所有版本号均为一手查询结果（Arch 官方仓库 JSON API、Fedora packages API、Ubuntu Launchpad API、CachyOS-PKGBUILDS 源码）。

---

## 0. 一句话结论

**"三家都装 snapper" 是个假命题 —— 装上 snapper 不等于拥有回滚能力。** snapper 只是快照引擎，它不知道"你刚装了个包"，也不会出现在 GRUB 菜单里。真正决定你能不能在被更新搞挂之后救回系统的，是另外三样东西：**事务级自动钩子、GRUB 快照启动集成、`/boot` 是否在快照范围内**。这三样在三家发行版上的差距是**结构性的（有没有这个包）**，不是配置差距（配不配得对）。

补齐之后：**Arch 是唯一三件套齐备且全在官方仓库的**；**Kubuntu 有自动钩子但没有救生艇**；**Fedora 44 的自动钩子包还在、但宿主 dnf4 已经被删了，等于没有**。

**CachyOS 的答案**：它在 snapper 这条线上**是全场最强的，没有第二**——因为它把 Arch 的三件套预先接线好了，还额外送你一张"出厂快照"。但这条优势回答不了"稳定"这个问题：它优化的是**出错后能不能救**，不是**会不会出错**。所以答案取决于你更怕哪一个。

---

## 1. 先把 snapper 拆开：它提供什么、缺什么

很多人把 "装 snapper" 当成 "拥有 openSUSE 那种原子回滚"。实际上 openSUSE 的体验由**四个部件**拼成，snapper 只是其中之一：

| 部件 | 作用 | openSUSE 里是谁 |
|---|---|---|
| **① 快照引擎** | 创建 / 比较 / 清理快照，管理多套配置 | `snapper` 本体 |
| **② 事务钩子** | 每次装包前自动拍 pre、装完拍 post，并配对 | `snapper-zypp-plugin`（zypper 插件） |
| **③ 启动集成** | 把快照变成 GRUB 菜单项，开不了机也能进 | openSUSE 的 grub2 内建 btrfs+snapper 支持 / 其他发行版用 `grub-btrfs` |
| **④ 布局前提** | `/boot` 必须和 `/` 在同一个 Btrfs 里，否则快照不含内核 | 安装器默认布局 |

**只装 ① 的结果**：你能手动 `snapper create`、能 `snapper list`、能 `snapper rollback` —— 但前提是**系统还能开机**。系统开不了机时，snapper 一点用都没有，你只能拿 Live USB 挂载子卷手动修。

这是本轮最重要的判断：**②③④ 缺任何一项，"用 snapper 管理" 就只是"多了一层手动备份"，不构成稳定性优势。**

### ④ 的权威依据（ArchWiki）

> If `/boot` is on a non-Btrfs partition, "you are not able to do snapper backups with it."

也就是说：`/boot` 单独分一个 ext4 分区（这是 Fedora 安装器的**默认行为**），snapper 就**管不到内核和 initramfs**。回滚 `/` 到三天前，`/boot` 里还是今天的内核 + 今天的 initramfs —— initramfs 里引用的模块在旧 root 上可能不存在，直接开不了机。这不是理论风险，是 Btrfs 回滚最常见的翻车点。

---

## 2. 一手核实矩阵（2026-10-19）

### 2.1 部件可用性

| 部件 | **Arch** | **Fedora 44 KDE** | **Kubuntu 26.04** | **Kubuntu 26.10** |
|---|---|---|---|---|
| ① `snapper` 本体 | ✅ `extra/snapper 0.13.2-1` | ✅ `0.13.0-3.fc44` | ✅ `universe` | ✅ `universe` |
| ② 自动快照钩子 | ✅ **`extra/snap-pac 3.0.1-3`** | ⚠️ `python3-dnf-plugin-snapper 4.1.2-11.fc44` **存在但宿主已死** | ✅ **`apt-btrfs-snapshot 4.0.1build1`（universe）** | ✅ 同左 |
| ③ GRUB 快照启动 | ✅ **`extra/grub-btrfs 4.14-1`** | ❌ **全库无此包** | ❌ **archive 内无此包** | ❌ |
| GUI | ✅ `extra/btrfs-assistant 3.0.0-1`、`snapper-fmt 0.11.10-1` | ✅ `btrfs-assistant` | ✅ `btrfs-assistant 2.2-1` + `snapper-gui` | ✅ |
| ④ `/boot` 默认布局 | 由你自己决定 | ❌ **ext4 独立分区（Anaconda 预设）** | 由你自己决定 | 同左 |
| 子卷默认布局 | 无（自建） | `root` + `home`，**无 `/.snapshots`** | `@` + `@home` | 同左 |

### 2.2 关键证据原文

**Arch**（`archlinux.org/packages/search/json/`）：
```
extra/snapper           0.13.2-1
extra/snap-pac          3.0.1-3
extra/grub-btrfs        4.14-1     "Include btrfs snapshots in GRUB boot options"
extra/btrfs-assistant   3.0.0-1
extra/snapper-fmt       0.11.10-1
```
> 结论：**Arch 的 snapper 三件套全部在官方 `extra` 仓库**，不需要 AUR、不需要编译。

**Fedora 44**（`packages.fedoraproject.org`）：
```
snapper                              0.13.0-3.fc44     ✅
python3-dnf-plugin-snapper           4.1.2-11.fc44     ⚠️ 仅 dnf4 插件
dnf (dnf4 本体)                       只有 Fedora 41       ❌ F44 无
libdnf5-plugin-*                     actions / txnupd / cow / notify  ❌ 无 snapper
grub-btrfs                           NOT FOUND         ❌
snap-pac                             NOT FOUND         ❌（Arch 专属）
```
> **这是本轮最关键的一条修正**：`python3-dnf-plugin-snapper` 这个包**确实还在 Fedora 44 仓库里构建**（4.1.2-11.fc44），看起来"Fedora 也有自动快照"。但它是 **dnf4 的 Python 插件**，而 **dnf4 本体从 Fedora 42 起就不再随发行版提供**（`dnf` 包页只列到 Fedora 41）。dnf5 用 C++ 插件（`libdnf5-plugin-*`），**没有 snapper 插件**。
>
> → **在 Fedora 44 上装这个包，它不会工作。** 这是一个"看着有、实际空"的陷阱。

**Fedora 的另一条路**（值得单独说）：
```
snapm            0.7.0-5.fc44     ✅
boom-boot        1.6.8-5.fc44     ✅
```
`snapm` 官方 README 明确写着 **"Bootable snapshots: Generate boot entries for snapshot boot and failsafe revert"**，用法：
```bash
snapm snapset create --bootable --revert before-upgrade / /home
# 重启 → GRUB 里出现 "Snapshot before-upgrade ..."
snapm snapset revert before-upgrade
```
**但它的后端只支持 LVM2（CoW / Thin）和 Stratis —— 明确不支持 Btrfs。**

> → Fedora 想拥有"GRUB 里能选快照 + 一键 revert"，**必须放弃 Btrfs 默认布局，改装 LVM + XFS**。这是 Fedora 独有的第三条路，也是**除 openSUSE 外唯一由发行版自己维护的、一等公民级的快照启动方案**。

**Kubuntu 26.04 / 26.10**（Launchpad API，`resolute` / `stonking`）：
```
apt-btrfs-snapshot   4.0.1build1   universe   "Automatically create snapshot on apt operations"
btrfs-assistant      2.2-1         universe
snapper-gui          0git.960a94834f-8  universe
grub-btrfs           NOT FOUND      ❌
snap-pac             NOT FOUND      ❌
```
> Ubuntu 有**原生的 APT 事务钩子**（`apt-btrfs-snapshot`，比 Fedora 那个空壳实在得多），但**没有 `grub-btrfs`**。26.10 同样有 `apt-btrfs-snapshot 4.0.1build1`。

---

## 3. 三家的真实体验差异

### 3.1 Arch：三件套齐备，但要你自己接线

Arch 给的是**零件**，不是成品。你要自己做四件事：

1. 安装时决定 `/boot` 放哪 —— 必须放 Btrfs 里（推荐独立子卷 `@boot`），否则第 ④ 条直接失效
2. 手动 `snapper -c root create-config /` 建配置
3. 装 `snap-pac`（提供 pacman 的 pre/post 钩子）
4. 装 `grub-btrfs` + `systemctl enable --now grub-btrfsd`

**代价**：约 30–45 分钟的配置 + 一次试错。**收益**：你得到了 openSUSE 级别的回滚能力，而且完全知道它怎么工作。

**风险点**：`grub-btrfs` 的 `grub-btrfsd` 在 Btrfs 上监控 `/.snapshots`，需要 `inotify` 支持；快照多了以后每次重生成 `grub-btrfs.cfg` 有开销（通常 <1s，可接受）。

### 3.2 Fedora 44：看起来有，实际是空壳

Fedora 的 Btrfs 是默认文件系统（F33 起），但**Fedora 从来没有认真做过 snapper 集成**。原因不难理解：Red Hat 的战略方向是 **LVM/Stratis + boom/snapm**（企业级、可管理、可编排），不是 openSUSE 那套 Btrfs 子卷哲学。

**官方 wiki 原文**（`fedoraproject.org/wiki/Btrfs`）：
> "The Btrfs partition scheme preset creates an **ext4 /boot**, and a Btrfs pool. **Two subvolumes, root and home**, are created from that pool and mounted at / and /home respectively."

三处硬伤：
1. `/boot` 是 **ext4** → 快照**永远不含内核**
2. 只有 `root` + `home` 两个子卷，**没有 `/.snapshots`** → snapper 会自己建，但那是嵌套在 `root` 子卷里的子卷，清理和配额行为都不理想
3. 没有 `grub-btrfs`，而且 Fedora 用 **BLS（Boot Loader Spec）** 的 `/boot/loader/entries/*.conf` 机制 —— `grub-btrfs` 的 `41_snapshots-btrfs` 脚本对这套布局支持很差

**所以 Fedora 44 + snapper 的实际能力 = 手动拍快照 + 手动回滚（系统还能开机时）。** 这连"比没有强一点"都算不上，因为你要多维护一套东西却拿不到关键能力。

**变通方案（不推荐，但可行）**：
```bash
# dnf5 唯一能挂外部命令的插件
sudo dnf install libdnf5-plugin-actions
# 然后自己写 hook 脚本调 snapper create —— 需要自己实现 pre/post 配对、去重、失败处理
```
这是 DIY，不是发行版能力。**如果要走 Fedora，走 snapm + LVM/XFS 那条路，别在 Btrfs + snapper 上耗。**

### 3.3 Kubuntu：有钩子，没有救生艇

Ubuntu 这边反而比 Fedora 实在：

- `apt-btrfs-snapshot` 会在**每次 apt 事务前**自动给 `@` 和 `@home` 拍快照
- `btrfs-assistant` + `snapper-gui` 提供 GUI
- 但 **`grub-btrfs` 不在 Ubuntu archive 里**（universe 也没有）

**结果**：系统能开机时，你有完整的快照历史和 GUI 回滚；**系统开不了机时，你只有 Live USB**。

**另一个坑**：Ubuntu 默认装 **ext4**。想用 Btrfs 必须在安装器里手动选（Kubuntu 26.04 的安装器有 Btrfs 选项，但默认不是）。装了系统才想起来 = 重装。

**第三个坑**：`apt-btrfs-snapshot` 和 `snapper` 是**两套并行体系** —— 前者用 `@apt-snapshot-<时间戳>` 命名，后者用 `/.snapshots/<N>/snapshot`。同时用会有两套快照历史、两套清理策略、互相不知道对方存在。**选一套，别混。**

---

## 4. 补齐后的排序：回滚能力维度

问题："装包自动拍 + 开不了机从 GRUB 菜单进快照 + 内核一起回滚" —— 三家谁能做到？

| | 自动拍 | GRUB 菜单 | 含内核 | 开箱程度 | 评级 |
|---|---|---|---|---|---|
| **Arch + 三件套** | ✅ snap-pac | ✅ grub-btrfs | ✅（若 `/boot` 在 Btrfs） | 需自己配 30–45 分钟 | **A** |
| **Fedora 44 + Btrfs + snapper** | ❌ 钩子失效 | ❌ 无包 | ❌ ext4 `/boot` | — | **F** |
| **Fedora 44 + LVM/XFS + snapm** | ⚠️ systemd timer（非事务级） | ✅ boom-boot | ✅（LVM 快照含 `/boot`） | 需手动分区 + 配 timer | **B+** |
| **Kubuntu 26.04 + snapper** | ✅ apt-btrfs-snapshot | ❌ 无包 | ✅（若 `/boot` 在 Btrfs） | 装包即用（钩子部分） | **B** |
| **openSUSE TW/Slowroll** | ✅ zypp 插件 | ✅ 内建 | ✅ | 安装器默认 | **A+** |
| **CachyOS** | ✅ snap-pac（预接线） | ✅ grub-btrfs-support（预接线） | ✅（Btrfs 安装） | **安装完即有出厂快照** | **A+** |

**这张表是本轮的核心答案。** 注意两件事：

1. **Fedora 在"都用 snapper"这个条件下是全场最差**，而且差得很隐蔽 —— 因为它有一个名字对得上的包，让人以为能用。
2. **CachyOS 在这条线上和 openSUSE 并列第一**，比原版 Arch 还高一档（因为预接线）。

---

## 5. 但回滚能力 ≠ 稳定性 —— 这是两个正交的维度

这是本轮必须讲清楚的一点，否则前面的结论会被误读。

| 维度 | 问题 | snapper 能改善吗 |
|---|---|---|
| **会不会出错** | 更新引入回归、驱动崩、内核不兼容 | ❌ **完全不能** |
| **出错后能不能救** | 有没有退路、退路多快 | ✅ 这是 snapper 的全部价值 |

**滚动发行版的真实风险不是"包没测试"，而是"测试窗口短"**（前序轮次已校准）。snapper 把"踩到回归"从**灾难**降级为**麻烦** —— 但麻烦仍然是麻烦：你要中断工作、重启、进快照、rollback、再重启、重新登录、恢复没保存的东西。**一天里发生一次，这天就废了一半。**

所以：

- **Arch + snapper** = 高风险 + 强退路 → 适合"能接受偶尔花 20 分钟恢复"的人
- **Kubuntu + snapper** = 低风险 + 中退路 → 适合"不想花那 20 分钟"的人
- **CachyOS + snapper** = 高风险 + 最强退路 + 省调优 → 适合"愿意用维护时间换性能"的人

**没有一个选项能同时给你"不出错"和"最强退路"。** 这就是选择本身。

---

## 6. CachyOS：适合吗？

### 6.1 它在 snapper 这条线上确实是最强的 —— 一手证据

这一条不是推测，是读了 CachyOS 的打包源码（`CachyOS/CachyOS-PKGBUILDS` master 分支）。

**包一：`cachyos-snapper-support 1.0.2-1`**
```bash
pkgdesc='CachyOS package that handles snapper configs.'
depends=(snapper snap-pac)      # ← 硬依赖 snap-pac：自动事务快照开箱即用
conflicts=(timeshift)           # ← 明确排斥 timeshift，避免双体系
# 安装 /etc/snapper/config-templates/cachyos-root
```
`post_install` 做的事：
```bash
systemctl enable --now snapper-cleanup.timer
#systemctl enable snapper-timeline.timer      ← 被注释掉：默认不开每小时快照
snapper --no-dbus -c root create-config --template cachyos-root /
```
配置模板 `cachyos-root` 的关键值：
```
TIMELINE_CREATE="no"            # 不做每小时快照（省磁盘、减少干扰）
NUMBER_LIMIT="50"               # 最多留 50 个事务快照
NUMBER_LIMIT_IMPORTANT="15"     # important 标记的最多留 15 个
SPACE_LIMIT="0.5"  FREE_LIMIT="0.2"
BACKGROUND_COMPARISON="yes"
```
> 这个取舍是对的：**只保留"装包前/后"的事务快照，不做定时快照。** 定时快照对游戏机是纯浪费（你打游戏时文件几乎不变）。

**包二：`grub-btrfs-support 1.0.0-1`**（维护者 Peter Jung / ptr1337，CachyOS 核心开发者）
```bash
depends=(cachyos-snapper-support grub-btrfs)
# 装两个 systemd 单元
```
```
# grub-btrfs-snapper.path
[Path]
PathModified=/.snapshots
```
```
# grub-btrfs-snapper.service
ExecStart=bash -c '... /etc/grub.d/41_snapshots-btrfs ...'
```
> 作用：**`/.snapshots` 一变就重生成 `grub-btrfs.cfg`**。原版 Arch 你要自己 enable `grub-btrfsd`，CachyOS 用 systemd `.path` 单元替你做了，而且更省资源（只在变化时触发，不是常驻守护）。

**包三：安装器的出厂快照**（`cachyos-calamares` → `src/scripts/btrfs-installation-snapshot`）
```bash
SNAP_ID=$(snapper --no-dbus -c root create --print-number \
    --description "Fresh CachyOS Installation" \
    --userdata "important=yes")
mkdir -p /etc/cachyos
echo "$SNAP_ID" > /etc/cachyos/installation-snapshot
```
> 装完系统立刻拍一张"出厂快照"，标记 `important=yes`（不会被清理算法删），并把 ID 存下来。**这意味着任何时候你都能一键回到刚装完的状态** —— 这个设计比 Arch、Fedora、Ubuntu 都好，是真正的"重装替代品"。

**结论：CachyOS 的 snapper 栈 = Arch 三件套 + 预接线 + 出厂快照。这是它最被低估的优点，比它的编译器优化实在得多。**

### 6.2 代价（为什么它仍然不是"稳定优先"的答案）

| 代价 | 具体 |
|---|---|
| **滚动** | 没有 Slowroll / Leap 等价物。`cachyos` 仓库跟 Arch 同步，只是额外重编译 |
| **小团队** | 核心维护者个位数（ptr1337、sirlucjan 等）。bus factor 极低 |
| **变量更多** | 内核带 BORE/sched-ext 补丁、包用额外 CFLAGS/LTO 重编译 → **出问题时排查路径比 Arch 长**（是上游 bug 还是 CachyOS 补丁引入的？） |
| **收益量级小** | 前序轮次结论：性能收益个位数百分比，且**CPU 密集原生游戏几乎为 0**（游戏二进制是厂商预编译的，编译层碰不到） |
| **仓库信任** | 第三方仓库 + 自签名包，供应链面比 Arch 官方大 |

**关键矛盾**：snapper 让你"出错了能救"，但 CachyOS 恰恰**更容易让你需要救**（补丁多、滚动快、测试窗口短）。**它把退路做到最好，同时把风险也抬高了。** 净效果是不是正的，取决于你的时间成本。

### 6.3 结论：条件表

| 你的情况 | 适合装 CachyOS 吗 | 理由 |
|---|---|---|
| **纯游戏机**（这台机器只打游戏，坏了不耽误正事）+ 愿意每月花点时间看更新 | ✅ **适合** | snapper 三件套 + 出厂快照 + 预调 sysctl/udev，省下的调优时间 > 维护时间 |
| **主力工作机**（有不能中断的活）+ 求稳 | ❌ **不适合** | 一次回归 = 半天报废。选 Kubuntu 26.04 或 openSUSE Slowroll |
| **双系统 / 有备用机** | ✅ 适合 | 风险被隔离，退路充足 |
| **只要 CPU 密集原生游戏** | ❌ 不值得 | 收益 ≈ 0，纯担风险 |
| **GPU 密集 Proton + AMD 显卡** | ⚠️ 看情况 | 收益来自 Mesa/DXVK 新版本，但 Arch 官方仓库同样新，**CachyOS 的额外收益很小** |
| **想省调优但要 Arch 生态** | ✅ 适合 | 它本质是"Arch + 现成调优 + 现成快照栈"，比手动配 Arch 省事 |

**一句话**：**CachyOS 是"Arch 的最佳发行版形态"，但它仍然是 Arch。** 如果你接受 Arch 的风险模型，那没有比它更好的选择；如果你不接受，它做得再好也不解决问题。

---

## 7. 三场景裁决重算（在"都用 snapper"前提下）

| 场景 | 裁决 | 理由（本轮新增的 snapper 视角） |
|---|---|---|
| **CPU 密集原生游戏**<br>（如 RimWorld、Factorio、Paradox 系） | **Kubuntu 26.04 LTS** | 发行版对原生游戏贡献 ≈ 0 → 优化目标纯化为"稳定"。snapper 只当保险，`apt-btrfs-snapshot` 够用；不需要 GRUB 集成，因为**这类场景几乎不会把系统搞到开不了机** |
| **CPU 密集 Proton**<br>（CPU 瓶颈的 Windows 游戏） | **Arch + 三件套** | Proton 吃 Wine/DXVK/Mesa 的**新版本**，这是唯一有效杠杆。而 Arch 是**唯一"自动快照 + GRUB 救生艇 + 含内核"全齐**的选择 → 新版本带来的回归风险被 snapper 对冲掉了 |
| **GPU 密集 Proton · AMD** | **Arch + 三件套** | 同理，Mesa RADV 新版本是关键。CachyOS 可选（收益增量小） |
| **GPU 密集 Proton · NVIDIA** | **Kubuntu 26.04 LTS** | 闭源驱动跟内核强耦合，滚动风险不对称。Ubuntu 的 HWE 内核 + 驱动包组合经过 Canonical 测试；出问题时 `apt-btrfs-snapshot` 能退，且 NVIDIA 驱动问题通常表现为"能开机但黑屏/花屏"，可进 TTY 处理，**不需要 GRUB 级救生艇** |
| **要绝对稳 + 要 Btrfs 回滚** | **openSUSE Slowroll** | 仍是唯一"开箱即用原子回滚"的选项，snapper 是它的原生能力而非外挂 |

**如果一定要选一个"最稳的 Arch 体验"** → **Arch + snapper 三件套**，而不是 CachyOS。因为你要的是 Arch 的软件新度，不是它的编译器优化。

---

## 8. 落地步骤

### 8.1 Arch 三件套（推荐路径）

**安装时**：`/boot` 不要单独分区，或用 Btrfs 子卷 `@boot`。
```
# 子卷布局（UEFI）
@        → /
@home    → /home
@log     → /var/log
@cache   → /var/cache
@snapshots → /.snapshots     # ← 必须是独立子卷
@boot    → /boot             # ← 必须是 Btrfs 子卷，不能是 ext4 分区
```
ESP 挂 `/boot/efi`（FAT32，512M–1G）。

**装完**：
```bash
# 1. 装三件套（全在 extra，无需 AUR）
sudo pacman -S snapper snap-pac grub-btrfs btrfs-assistant

# 2. 建 root 配置
sudo snapper -c root create-config /

# 3. 让 snapper 用已有的 /.snapshots 子卷（create-config 会新建一个，需替换）
sudo btrfs subvolume delete /.snapshots
sudo mkdir /.snapshots
sudo btrfs subvolume create /.snapshots
sudo chmod 750 /.snapshots

# 4. 启用清理 + grub-btrfs 守护
sudo systemctl enable --now snapper-cleanup.timer
sudo systemctl enable --now grub-btrfsd

# 5. 验证：随便装个包，看是否自动生成 pre/post 快照
sudo pacman -S htop
sudo snapper -c root list
```
**验收标准**：`snapper list` 里出现一对 `pre`/`post`，`description` 是 `pacman -S htop`。然后 `sudo grub-mkconfig -o /boot/grub/grub.cfg`，重启看 GRUB 里有没有 "Arch Linux snapshots" 子菜单。

### 8.2 Kubuntu 26.04

**安装时**：手动分区，`/` 选 **Btrfs**（默认是 ext4，不改就白搭）。Ubuntu 安装器会自动建 `@` + `@home`。

**装完**：
```bash
# 自动 APT 快照（这是 Ubuntu 的原生钩子）
sudo apt install apt-btrfs-snapshot

# 可选：GUI + snapper 体系（二选一，别和上面混用）
# sudo apt install btrfs-assistant snapper
```
**救生艇（必做）**：准备一个 Ubuntu Live USB。开不了机时：
```bash
# Live 环境
sudo mount -o subvol=@ /dev/nvme0n1p2 /mnt
sudo mount -o subvol=@home /dev/nvme0n1p2 /mnt/home
sudo mount /dev/nvme0n1p1 /mnt/boot/efi
for i in dev proc sys run; do sudo mount --bind /$i /mnt/$i; done
sudo chroot /mnt
# 里面用 apt-btrfs-snapshot list / rollback，或 snapper rollback
```
> 这一步请**提前演练一次**。没演练过的救生艇等于没有。

### 8.3 Fedora 44 —— 两条路，选一条

**路线 A（不推荐）：Btrfs + snapper**
放弃。自动钩子失效、`/boot` 是 ext4、没有 GRUB 集成，三条全废。

**路线 B（推荐）：LVM + XFS + snapm**
安装时手动分区：
```
/boot      ext4  1G        （或 xfs）
/          xfs   LVM 逻辑卷（thin pool）
swap       LVM 逻辑卷
```
```bash
sudo dnf install snapm boom-boot
# 手动拍可启动快照
sudo snapm snapset create --bootable --revert pre-update / /home
sudo snapm snapset list
# 更新
sudo dnf upgrade --refresh
# 坏了：GRUB 里选 "Snapshot pre-update ..." 或
sudo snapm snapset revert pre-update && sudo reboot
# 好了：清掉
sudo snapm snapset delete pre-update
```
```bash
# 自动化的唯一办法：systemd timer（不是事务级，但可用）
sudo systemctl enable --now snapm-daily.timer   # 需确认单元名，见 snapm 文档
```
> 这条路的好处：**LVM 快照包含 `/boot`**，所以内核一起回滚；`boom-boot` 写 BLS 条目，和 Fedora 的启动机制原生兼容。坏处：**手动分区 + 不是事务级触发**（你要靠定时或记得手动拍）。

---

## 9. 坑（本轮新增 10 条）

1. **`python3-dnf-plugin-snapper` 在 Fedora 44 是死包** —— 包还在构建（4.1.2-11.fc44），但 dnf4 从 F42 起不再提供。装了不工作，且不会有任何报错提示。
2. **Fedora 的 `/boot` 是 ext4** —— Anaconda 的 Btrfs 预设明确写 "creates an ext4 /boot"。快照永远不含内核。
3. **`grub-btrfs` 只在 Arch 官方仓库** —— Fedora 全库无、Ubuntu archive 无。这是"能不能从菜单进快照"的唯一开关。
4. **`snapm` 不支持 Btrfs** —— 只支持 LVM2（CoW/Thin）和 Stratis。Fedora 想用它必须改分区方案。
5. **`apt-btrfs-snapshot` 和 `snapper` 是两套体系** —— 前者用 `@apt-snapshot-<时间戳>`，后者用 `/.snapshots/<N>/`。同时用会有两套历史、两套清理，互不感知。**选一套。**
6. **`/.snapshots` 必须是独立子卷** —— `snapper create-config` 会自己建一个，但如果你已经有布局，要先删掉再建，否则变成嵌套子卷，清理和配额行为异常。
7. **CachyOS 模板默认 `TIMELINE_CREATE="no"`** —— 只有 pacman 事务快照，没有每小时快照。想要定时快照得自己改 `/etc/snapper/configs/root` 并 `systemctl enable snapper-timeline.timer`（安装脚本里这行是注释掉的）。
8. **`grub-btrfs` 读只读快照需要 overlayfs** —— 需 `grub-btrfs-overlayfs` hook，且**不兼容 systemd initramfs**（必须用 Busybox initramfs）。Arch 上如果用了 systemd hook，从快照启动会失败。
9. **`snapper rollback` 之后 GRUB 默认项可能仍指向旧快照** —— rollback 会把当前状态存成新快照并切回旧快照，但 `grub.cfg` 的 `default` 条目未必更新。回滚后**必须** `grub-mkconfig` 或手动选一次。
10. **`snap-pac` 的 pre/post 对在断电时会留孤儿** —— pacman 事务中途断电，pre 快照存在但没有对应 post，`snapper list` 里显示为 `pre`。用 `snapper -c root list --columns number,type,description` 定期检查清理。

---

## 10. 存疑 / 未核实

| 项 | 状态 |
|---|---|
| CachyOS 安装器的 `/boot` 布局（是否在 Btrfs 子卷内） | **推断（中置信）**。安装器脚本注释写 "present on all btrfs installs"，且官方维护 `grub-btrfs-support`（快照启动包）→ 强烈暗示 `/boot` 在 Btrfs 内。未取到 Calamares 分区配置一手文件（`cachyos-calamares` 仓库内只有上游 Calamares 默认配置，CachyOS 的 `etc/calamares/` 在二进制包里）。 |
| Fedora 44 是否 100% 无 dnf5 snapper 插件 | **推断（高置信）**。基于 `libdnf5-plugin-*` 全量搜索结果只有 actions/txnupd/cow/notify，以及 dnf4 包已停供。未做安装实测。 |
| `apt-btrfs-snapshot` 与 `snapper` 并存的冲突程度 | **推断（中置信）**。基于两者命名/布局设计差异，未实测共存行为。 |
| Kubuntu 26.10 的 `btrfs-assistant` / `snapper-gui` | **未核实**（只确认 `snapper` 与 `apt-btrfs-snapshot` 在 `stonking/universe`）。 |
| `snapm` 的自动定时单元确切名称 | **未核实**（README 只说 "Integration with systemd timers"，未列单元名）。 |
| CachyOS 的 `grub-btrfs-support` 是否安装器默认安装 | **推断（中置信）**。`btrfs-installation-snapshot` 脚本检查 `cachyos-snapper-support`，未检查 `grub-btrfs-support` → 可能需手动装。 |

---

## 11. 参考（一手来源）

| 来源 | 用途 |
|---|---|
| `https://archlinux.org/packages/search/json/?name=<pkg>` | Arch 官方仓库版本（snapper / snap-pac / grub-btrfs / btrfs-assistant） |
| `https://packages.fedoraproject.org/pkgs/<src>/<pkg>/` | Fedora 各版本可用性（snapper / python3-dnf-plugin-snapper / dnf / snapm / boom-boot） |
| `https://api.launchpad.net/1.0/ubuntu/+archive/primary?ws.op=getPublishedSources&source_name=<pkg>&distro_series=...resolute` | Ubuntu 26.04 包（apt-btrfs-snapshot / grub-btrfs / btrfs-assistant / snapper-gui） |
| `https://fedoraproject.org/wiki/Btrfs` | Anaconda Btrfs 预设："creates an ext4 /boot … two subvolumes, root and home" |
| `https://github.com/snapshotmanager/snapm` | snapm 特性 + 后端限制（仅 LVM2/Stratis，无 Btrfs） |
| `https://raw.githubusercontent.com/CachyOS/CachyOS-PKGBUILDS/master/cachyos-snapper-support/{PKGBUILD,cachyos-snapper-support.install,snapper-template-root-cachyos}` | CachyOS snapper 栈一手定义 |
| `https://raw.githubusercontent.com/CachyOS/CachyOS-PKGBUILDS/master/grub-btrfs-support/{PKGBUILD,grub-btrfs-snapper.path,grub-btrfs-snapper.service}` | CachyOS grub-btrfs 预接线 |
| `https://raw.githubusercontent.com/CachyOS/cachyos-calamares/cachyos/src/scripts/btrfs-installation-snapshot` | 出厂快照脚本 |
| `https://github.com/Antynea/grub-btrfs` | grub-btrfs 支持 snapper/timeshift/yabsnap 快照 |
| ArchWiki `Btrfs#Snapper` | `/boot` 在非 Btrfs 分区时无法做 snapper 备份 |
