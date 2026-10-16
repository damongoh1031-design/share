# Ubuntu 26.04 LTS：第三方内核（XanMod / Liquorix 等）+ Mesa PPA 值不值得？

> 第十三轮 · Linux 游戏性能系列（共 13 组报告 = 13 × .md + 13 × .html）｜ 2026-10-16
> 方法：一手 HTTP/API 探测（Ubuntu 归档、Launchpad PPA、deb.xanmod.org、liquorix.net）+ Phoronix 同机实测 + 结构性推断

---

## TL;DR

**三条结论，按"该做什么"排序：**

1. **amd64v3 不用找第三方 —— Ubuntu 26.04 LTS 官方自带，一行配置开启。** 实测 `resolute` 的 `main`/`universe`/`restricted`/`multiverse` 以及 `-updates`/`-security` 六个位置**全部提供 `binary-amd64v3`**，含 `mesa-vulkan-drivers`（RADV）/ `libc6` / `libvulkan1` / `libdrm2`。开启方式：`APT::Architecture-Variants "amd64v3"`（opt-in，默认关）。
2. **Mesa PPA 按需上，不是默认动作。** `kisak-mesa` 在 resolute 上给 **Mesa 26.2.5**（自带 26.0.3，+2 个小版本），而且**PPA 自己也发 `amd64v3` 变体**。只在"遇到具体 Mesa bug / 新硬件 / 需要新 RADV 特性"时才值得——否则收益≈0，代价是 Wayland 会话风险。
3. **第三方内核基本不值得。** XanMod（resolute ✓，7.2.11，有 `x64v1/v2/v3`）和 Liquorix（resolute ✓，7.2.10，**只有 amd64，无 v3**）都只比 Ubuntu 自带的 **Linux 7.0.0-14** 新一点点，而 7.0 已经含 `sched_ext` + MGLRU + NTSync。代价是 DKMS 模块易碎 + 无安全更新承诺。

**量级参照（这是最关键的一条）**：Phoronix 在**同一台** Razer Blade 18 上跑 99 项测试，CachyOS（Linux 7.1 + GCC 16.1.1 + 全套 v3/v4 重编译 + BORE + 更新的 NVIDIA 驱动）**赢 51%**，Windows 11 赢 38%，**Ubuntu 26.04 LTS 只赢 10%**、垫底 43%。**但几何平均是"窄胜"** —— 连整套 CachyOS 优化堆起来都只是险胜，单换一个内核能拿到的份额只会更小。

---

## 一、先看清起点：Ubuntu 26.04 LTS 本身给了什么

26.04 LTS（**Resolute Raccoon**，2026-04-23 发布，支持到 2031-04，Pro 到 2036）不是"旧栈需要打补丁"，而是一个相当新的基线：

| 项 | 26.04 LTS 自带（实测/官方） | 评价 |
|---|---|---|
| 内核 | **Linux 7.0.0-14.14**（`linux-image-generic`，实测） | 跳过 6.20 直接上 7.0，**含 sched_ext、MGLRU、NTSync** |
| Mesa | **26.0.3-1ubuntu1**（实测） | 中上；不是最新但不是旧的 |
| amd64v3 | ✅ 官方 opt-in（`APT::Architecture-Variants`） | **不需要任何第三方仓库** |
| 图形会话 | **Wayland 唯一**，X11 会话已移除；**VRR 默认开启**（退出实验阶段）；HDR 原生支持 | 对游戏是净利好 |
| 实时内核 | **PREEMPT_RT 进主仓库，免费**（不再需要 Pro） | — |
| NVIDIA | 595 系（随仓库） | 比 CachyOS 的 R610 旧一个大版本 |
| AI 栈 | CUDA / ROCm 7.1.0 进官方源 | — |
| 工具链 | GCC 15.2 / Python 3.13.9 / Rust 1.93 / APT 3.0 | APT 3.0 支持 `apt history-undo` |

**关键含义**：第三方内核和 PPA 的卖点（新调度器、新内存管理、新 Mesa 特性）里，**调度器（sched_ext）和内存管理（MGLRU）26.04 已经有了**。剩下能"多拿"的只有：更新的上游版本号、发行版特有补丁集（XanMod 的 le9uo / Clear Linux 补丁）、以及 Mesa 的小版本差。

---

## 二、amd64v3：官方就够，别找第三方

### 2.1 实测：六个位置全部提供 v3 包

```
dists/resolute/main/binary-amd64v3/Packages.gz           200
dists/resolute/universe/binary-amd64v3/Packages.gz       200
dists/resolute/restricted/binary-amd64v3/Packages.gz     200
dists/resolute/multiverse/binary-amd64v3/Packages.gz     200
dists/resolute-updates/main/binary-amd64v3/Packages.gz   200   ← 安全更新也有
dists/resolute-security/main/binary-amd64v3/Packages.gz  200   ← 安全更新也有
```

`-updates` 和 `-security` 也有 v3 包，意味着**开 v3 不会让你掉出安全更新通道** —— 这是"值得开"的关键前提。

### 2.2 机制：不是新架构，是"同架构的变体"

这一点容易误解。抓 `main/binary-amd64v3` 里的 `mesa-vulkan-drivers`：

```
Package: mesa-vulkan-drivers
Architecture: amd64          ← 注意：仍是 amd64，不是 amd64v3
Version: 26.0.3-1ubuntu1
```

而且 `main/amd64v3` 与 `main/amd64` 的包数**完全相同：6487 vs 6487**。

**→ 这是同一批源码、同一套依赖关系、用 `-march=x86-64-v3` 重新编译的一份平行构建**，靠 APT 3.0 的 *Architecture Variants* 机制切换，不是新增一个 dpkg 架构。所以你**不能**同时装 v1 和 v3 版本 —— 只能整体切换。这也解释了为什么它是"opt-in"。

### 2.3 开启方式（官方，一行）

```bash
echo 'APT::Architecture-Variants "amd64v3";' | sudo tee /etc/apt/apt.conf.d/99enable-amd64v3
sudo apt update && sudo apt full-upgrade
```

**前置条件**：CPU 支持 x86-64-v3（AVX2 / FMA / BMI1 / BMI2 / MOVBE）—— Intel Haswell（2013）+ / AMD Excavator+。先验：

```bash
grep -o -m1 -E 'avx2|bmi2|fma' /proc/cpuinfo | sort -u   # 三条都要有
```

**回滚**：删掉那个文件再 `apt update` 即可（`sudo rm /etc/apt/apt.conf.d/99enable-amd64v3`）。

**注意**：`releases.ubuntu.com/26.04/` 只发布 `amd64` ISO（实测：只有 `ubuntu-26.04-desktop-amd64.iso` / `-live-server-amd64.iso` / `26.04.1` 同款），**没有 amd64v3 ISO**。所以 v3 是"装完之后开"，不是装机时选。（26.10 那边反而有 amd64v3 daily ISO。）

### 2.4 值不值：值，因为成本几乎为零

| | |
|---|---|
| 收益 | **小**。Phoronix 对 Ubuntu 25.10 amd64v3 的标题是 "Some Minor & Rare Performance Advantages For Desktop Workloads"；机制上 RADV 的着色器编译走 LLVM（面向 GPU，与宿主 ISA 无关），受益的只是主机侧 Mesa 代码 |
| 成本 | 一行配置 + 一次 `full-upgrade`，官方维护，安全更新不断档 |
| 结论 | **✅ 值得**。它是"免费抽奖"，不是"性能方案" |

---

## 三、Mesa PPA：按需，不是默认动作

### 3.1 实测可用性（resolute = 26.04）

| PPA | resolute 可用 | Mesa 版本（实测） | 是否发 amd64v3 |
|---|---|---|---|
| Ubuntu 自带 | — | **26.0.3-1ubuntu1** | ✅（官方归档） |
| **kisak/kisak-mesa** | ✅ `dists/resolute/Release` = 200 | **26.2.5~kisak1~r** | ✅ `binary-amd64v3` = 200 |
| **oibaf/graphics-drivers** | ✅ `dists/resolute/Release` = 200 | mesa-git 每日构建（版本未取到，见"未核实"） | ✅ `binary-amd64v3` = 200 |

两个 PPA 都跟上了 resolute，而且**都提供 amd64v3 变体**（它们的 `Release` 里 `Architectures:` 明确列出 `amd64v3`）。这意味着 **PPA + v3 可以叠加**，不冲突。

### 3.2 什么时候值得装

**值得：**
- 你遇到了**具体的 Mesa/RADV bug**（某个游戏崩溃、渲染错误、VRR 异常）—— 先查 Mesa 的 issue 是否在新版修了
- **新硬件**（新 GPU / 新 APU）在 26.0.3 上支持不全
- 你需要某个**新版才有的扩展/特性**（FSR4、新的 RADV 优化、VK_EXT_* 新扩展）
- 你在跑**刚发布的游戏**，已知对 Mesa 版本敏感

**不值得：**
- 26.0.3 已经能跑你的游戏 → 平均帧收益通常测不出来
- 你只是想"更新一点" → LTS 上装 PPA 是拿稳定性换版本号

### 3.3 LTS 上装 PPA 的真实代价

| 风险 | 说明 |
|---|---|
| **Wayland 会话崩溃** | 26.04 是 **Wayland 唯一**（X11 会话已删），oibaf 类 PPA 覆盖 Mesa 库时若出问题，**没有 X11 兜底**。这是 26.04 相比 24.04 新出现的风险 |
| 与 HWE 栈冲突 | 26.04 LTS 后续会推 HWE 内核/图形栈，PPA 固定在某些 Mesa 版本上容易打架 |
| 依赖漂移 | 26.04 的 `libc6 >= 2.43`、`libllvm21` 等基础库与 PPA 构建目标可能错位 |
| 回滚 | 必须用 `ppa-purge` 才干净，`apt remove` 会留下一堆半旧包 |

**建议姿势**：把它当**临时工具**而不是长期状态 —— 遇到问题时装、验证、然后决定是留还是 purge。

---

## 四、第三方内核：XanMod / Liquorix 实测

### 4.1 可用性（实测）

| 内核 | Ubuntu 26.04（resolute）支持 | 版本 | ISA 变体 | 仓库 |
|---|---|---|---|---|
| **XanMod** | ✅ `dists/resolute/Release` = 200 | **7.2.11-xanmod1** | `x64v1` / `x64v2` / `x64v3`（**无 v4**） | `deb.xanmod.org` |
| **Liquorix** | ✅ `dists/resolute/Release` = 200 | **7.2-18ubuntu1~resolute**（内核 7.2.10） | **只有 amd64（v1）** | `liquorix.net/ubuntu/` |
| Ubuntu 自带 | — | **7.0.0-14.14** | `amd64` + `amd64v3` 变体 | 官方归档 |

**一个暴露结构的细节**：Liquorix 的包名是 `linux-image-7.2.10-2-liquorix-amd64`，版本串是 `7.2-18ubuntu1~resolute` —— **`ubuntu1~resolute` 这个后缀说明它是拿 Ubuntu 自己的内核源码包，叠加 Zen/Liquorix 补丁集重新构建的**。这带来两个后果：① 它继承了 Ubuntu 的内核配置和 `amd64` 单架构（**没有 v3**）；② 它天然贴合 Ubuntu 的模块 ABI 约定，比 XanMod 的"独立树"更不容易踩 DKMS。

**XanMod 则是独立树**（`gitlab.com/xanmod/linux`），版本跟主线更紧（7.2.11 vs Ubuntu 7.0）。

### 4.2 XanMod 到底多给了什么

官方特性页列出的（对比 Ubuntu 7.0 已含项）：

| XanMod 特性 | Ubuntu 26.04 已有？ | 净增量 |
|---|---|---|
| Google MGLRU（多代 LRU） | ✅ 7.0 已默认 | **0** |
| `sched_ext`（SCX）支持 | ✅ 7.0 已含 | **0** |
| BBRv3 TCP 拥塞控制（默认） | 部分（内核含 bbr，默认不一定是 v3） | 小 |
| **Firelzrd 'le9uo'**（内存压力下保护匿名页/干净页） | ❌ | **★ 真实增量** |
| **Clear Linux 补丁集（部分）** | ❌ | 小～中 |
| LLVM Polly / Software Pipelining / 额外 x86_64 优化 | ❌ | 小 |
| Graysky 的 GCC/Clang CPU 选项 | ❌ | 小 |
| ORC unwinder / PCIe ACS Override / Steam Deck EC 传感器 / Android Binder | ❌ | 与游戏无关或小众 |

**→ 真正值得注意的只有 `le9uo`**：它针对"内存压力下不该被换出的页"做保护。对照本系列**第九轮的结论**（CPU 密集模拟游戏的冠军是内核"内存管理 + 调度延迟"层，且唯一能量级差异的场景是"内存吃紧时避免磁盘 swap"）—— `le9uo` 正好打在这个点上。**如果你的机器内存吃紧（16GB 或更少、跑大存档的群星/CK3），XanMod 的 le9uo 是这一整轮里唯一有理论依据的第三方内核增量。**

### 4.3 但风险清单是硬的

XanMod 官方**自己**在页面顶部写着：

> *"Note: The current NVIDIA, OpenZFS, VirtualBox, VMware Workstation / Player and some other dkms modules **may not support the latest kernel versions**."*

| 风险 | 具体后果 |
|---|---|
| **DKMS 断裂** | NVIDIA 驱动（26.04 用 595 系）随内核升级需重编模块；XanMod 跟主线太快时模块编译失败 → 掉到 nouveau / 黑屏 |
| **无安全更新承诺** | Ubuntu 的 CVE 补丁按 LTS 节奏走，XanMod 靠上游 + 作者个人。**26.04 的 LTS 承诺（到 2031）对第三方内核不成立** |
| **回滚麻烦** | 需要在 GRUB 里手动选旧内核，且要保证 Ubuntu 原内核没被清掉 |
| **收益不可测** | 没有针对"Ubuntu 7.0 vs XanMod 7.2"的游戏对照基准存在（Phoronix 做的是发行版间对比，不是内核间） |
| **Livepatch 失效** | Ubuntu Pro 的 Livepatch 只覆盖 Ubuntu 签名内核 |

---

## 五、收益校准：CachyOS vs Ubuntu 26.04 LTS 同机实测

这是本轮最有价值的一手数据（Phoronix，2026-07-15，文章 *Ubuntu 26.04 LTS vs. Windows 11 vs. CachyOS Performance On A $5399 Laptop*）。

**硬件**：Razer Blade 18 RZ09-0582，**Intel Core Ultra 9 290HX Plus + NVIDIA GeForce RTX 5090 Laptop**（$5399，雷蛇首款走 Canonical 认证的笔记本）。

**三个系统的实际栈：**

| | Ubuntu 26.04 LTS | CachyOS | Windows 11 |
|---|---|---|---|
| 内核 | Linux 7.0 | **Linux 7.1** | — |
| 编译器 | GCC 15.2 | **GCC 16.1.1** | MSVC |
| NVIDIA 驱动 | **R595** | **R610** | 官方 |
| 其他 | 默认 | 全套 v3/v4 重编译 + BORE + 调优 | Razer 出厂配置 |

**99 项测试结果：**

| 指标 | CachyOS | Windows 11 | Ubuntu 26.04 LTS |
|---|---|---|---|
| **拿下第一的比例** | **51%** | 38% | **10%** |
| **垫底的比例** | — | 约 50% | **43%** |
| **几何平均** | **窄胜**（narrow victory） | 微胜 Ubuntu | 三者中最末 |

原文结论：*"On a geo mean basis, Microsoft Windows 11 just edged past Ubuntu 26.04 LTS … Meanwhile CachyOS battled the two to secure a narrow victory on a geo mean basis."*

### 5.1 怎么读这组数据

**正面读法（对 Ubuntu 不利）**：Ubuntu 26.04 LTS 只赢 10%、垫底 43% —— 在**这台机器上**它明显是三者里最弱的默认配置。而且 CachyOS 还多了一个 NVIDIA 驱动大版本（R610 vs R595），这部分**不是内核/编译优化的功劳**，是驱动版本。

**反面读法（对"换内核"不利）**：**几何平均是窄胜**。也就是说，把 CachyOS 的**全部**优化（新内核 + 新编译器 + v3/v4 全量重编译 + BORE + 新驱动）加在一起，整体差距仍然是"窄"的。**你要复现的那部分里，只换一个内核能分到的份额更小** —— 因为：
- CachyOS 的份额里，**编译层**（v3/v4 + LTO/PGO/BOLT 重编译整套用户态）占相当比重 → **Ubuntu 用官方 amd64v3 就能拿到这一层的大头**，不需要 XanMod
- **驱动版本差**（R610 vs R595）在 NVIDIA 场景下可能贡献了可观份额 → **换内核完全拿不到这一块**
- **BORE / 调度调参** → 只在 CPU 受限时生效，而且第九轮已论证其量级是个位数百分比

**结论**：这组数据支持"**开官方 v3 + 按需上 Mesa PPA**"，**不支持**"为了性能换第三方内核"。

---

## 六、关于「linux-bqx」

**查不到这个内核。** 我做了四类检索，全部零结果：

| 检索位置 | 结果 |
|---|---|
| GitHub 仓库搜索 `linux-bqx` | 0 个匹配 |
| AUR RPC 搜索 `bqx` | 0 个匹配 |
| 中文网络检索（`linux-bqx` / `bqx 内核` / `bqx 调度器`） | 无任何内核相关结果 |
| Launchpad / 发行版仓库 | 无 |

**可能的候选**（你大概指的是其中之一）：

| 候选 | 说明 |
|---|---|
| **Liquorix**（仓库/包名常见缩写 `lqx`） | Ubuntu 可用 ✓，本报告第四节已实测 |
| **XanMod** | Ubuntu 可用 ✓，本报告第四节已实测 |
| **CachyOS 的 `linux-cachyos-bore` / `linux-cachyos-bmq`** | BORE / BMQ 调度器变体，**Arch 专属**，Ubuntu 用不了 |
| **linux-tkg** | 编译脚本集（自己选调度器/编译器），非二进制仓库，Ubuntu 上需自行构建 |
| **BFQ**（`bfq`） | 其实是**IO 调度器**不是内核；CachyOS-Settings 会给 HDD 分配 bfq，所有主流内核都已内置 |

如果你是某个具体名字看错了，告诉我准确拼写，我再去核。

---

## 七、决策表（游戏为主）

| 动作 | 收益 | 风险 | 值不值 |
|---|---|---|---|
| **开官方 amd64v3** | 小（桌面负载"minor & rare"） | **极低**（官方维护，安全更新不断档，一行可回滚） | ✅ **值得，先做这个** |
| **升级到 26.04.1 + 后续 HWE 栈** | 小～中（内核/图形栈跟进） | 低 | ✅ 值得 |
| **确认 NTSync 生效**（Wine/Proton 游戏） | 中（1% low + 兼容性，见第十轮 KB） | 低 | ✅ 值得，零成本 |
| **kisak-mesa PPA** | 中（26.0.3 → 26.2.5，**仅遇到具体 bug 时**） | 中（Wayland 无 X11 兜底） | ⚠️ **按需** |
| **oibaf mesa-git PPA** | 中高（最新特性） | **高**（每日构建 + Wayland 唯一会话） | ❌ 除非你是测试者 |
| **XanMod 内核** | 极小（唯一亮点 le9uo，内存吃紧时可能有用） | 中高（DKMS 断裂 / 无安全更新 / 回滚麻烦） | ⚠️ **一般不值得** |
| **Liquorix 内核** | 极小（延迟优化；**且无 v3**） | 中（继承 Ubuntu 源码，比 XanMod 温和） | ⚠️ 一般不值得 |
| **为了性能换发行版（CachyOS）** | 中（同机实测赢 51% vs 10%，但 geo mean 窄胜） | 高（脱离 LTS 支持周期） | 视你对"稳定 5 年"的估值 |

### 推荐执行顺序

1. **开官方 amd64v3**（一行，零成本）
2. **升到 26.04.1**，确认 NVIDIA 驱动 + Wayland/VRR/HDR 正常
3. **验证 NTSync** 在 Wine/Proton 游戏里生效（见第十轮 KB 的判据）
4. **只在遇到具体 Mesa/RADV bug 时**上 kisak PPA，问题解决后考虑 purge
5. **别换内核**，除非你有明确理由：内存吃紧要 le9uo、需要 sched_ext 自定义调度器、或特定硬件在 7.0 上支持不全

---

## 八、可复用操作

```bash
# ── 0) 先确认 CPU 够不够 v3（三条都要有）
grep -o -m1 -E 'avx2|bmi2|fma' /proc/cpuinfo | sort -u

# ── 1) 开官方 amd64v3（Ubuntu 26.04 LTS，opt-in）
echo 'APT::Architecture-Variants "amd64v3";' | sudo tee /etc/apt/apt.conf.d/99enable-amd64v3
sudo apt update && sudo apt full-upgrade

# 验证是否生效
apt policy mesa-vulkan-drivers          # 看候选版本来源
cat /etc/apt/apt.conf.d/99enable-amd64v3

# 回滚
sudo rm /etc/apt/apt.conf.d/99enable-amd64v3 && sudo apt update

# ── 2) 看当前实际栈（换内核/PPA 前后各跑一次做对照）
uname -r
glxinfo -B | grep -E 'OpenGL renderer|OpenGL version'
vulkaninfo --summary 2>/dev/null | grep -E 'driverName|apiVersion'
apt policy mesa-vulkan-drivers linux-image-generic

# ── 3) kisak-mesa PPA（按需；26.04 上 = Mesa 26.2.5）
sudo add-apt-repository ppa:kisak/kisak-mesa
sudo apt update && sudo apt full-upgrade
# 干净回滚（推荐）
sudo apt install ppa-purge && sudo ppa-purge ppa:kisak/kisak-mesa

# ── 4) XanMod 内核（⚠️ 装前先备份 / 确认 DKMS 能编）
wget -qO - https://dl.xanmod.org/archive.key | sudo gpg --dearmor -vo /etc/apt/keyrings/xanmod-archive-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/xanmod-archive-keyring.gpg] http://deb.xanmod.org $(lsb_release -sc) main" \
  | sudo tee /etc/apt/sources.list.d/xanmod-release.list
sudo apt update
apt-cache search '^linux-xanmod'          # 先看清有哪些变体
# 选 v3 变体（v4 不存在，XanMod 自己说 "x86-64-v4 (AVX-512) (no kernel benefit)"）
sudo apt install --no-install-recommends dkms libelf-dev clang lld llvm
sudo apt install linux-xanmod-x64v3
# 保留 Ubuntu 原内核以便 GRUB 回退；不要 purge linux-image-generic

# ── 5) Liquorix（Ubuntu 侧仓库已确认存在：liquorix.net/ubuntu/dists/resolute/）
#     安装方式以 https://liquorix.net/ 官方说明为准（本报告未实测安装流程）
```

---

## 九、坑与反直觉

| 坑 | 说明 |
|---|---|
| **以为 v3 要靠第三方** | ❌ 26.04 LTS 官方就带，还带在 `-security`/`-updates` 里。去装第三方 v3 仓库（ALHP 之类）是**纯增风险** |
| **以为 v3 是新架构能共存** | ❌ `Architecture: amd64`，是**变体**不是新架构。不能同时装 v1+v3，只能整体切 |
| **以为 26.04 有 amd64v3 ISO** | ❌ 实测 `releases.ubuntu.com/26.04/` 只有 `amd64` ISO。v3 是装完之后开（26.10 那边才有 v3 daily ISO） |
| **在 26.04 上装 Mesa PPA 的风险比 24.04 高** | ⚠️ **26.04 移除了 X11 会话，只剩 Wayland**。Mesa 出问题没有 X11 兜底 —— 这是 24.04 时代不存在的风险 |
| **以为换内核能拿到 CachyOS 的差距** | ❌ CachyOS 的 51% vs 10% 里混了**更新的 NVIDIA 驱动（R610 vs R595）**和**全套用户态 v3/v4 重编译**，这两块换内核都拿不到 |
| **以为 XanMod 有 x64v4** | ❌ 只有 v1/v2/v3。XanMod 自己标注 "x86-64-v4 (AVX-512) (no kernel benefit)" |
| **以为 Liquorix 有 v3** | ❌ 实测 `Architectures: amd64`，**只有 v1**。想要 v3 内核得走 XanMod 或 CachyOS |
| **忽略 DKMS** | ⚠️ XanMod 官方明说 NVIDIA/OpenZFS/VirtualBox/VMware 模块**可能不支持最新内核**。26.04 用 NVIDIA 595，装第三方内核前先确认模块能编 |
| **把第三方内核当"LTS 的一部分"** | ❌ Ubuntu 的 LTS 承诺（到 2031）**不覆盖第三方内核**。安全更新节奏由上游 + 个人维护者决定 |
| **`apt remove` 回滚 PPA** | ❌ 会留下半旧包和依赖错位。用 `ppa-purge` |

---

## 十、未核实 / 存疑

- **`linux-bqx`**：检索无果（GitHub / AUR / 中文网络 / Launchpad），**未能确认存在**。见第六节候选清单。
- **oibaf PPA 在 resolute 上的确切 Mesa 版本**：`Packages.gz` 抓取多次超时/为空（该 PPA 包量大），只确认了 `dists/resolute/Release` = 200 且 `Architectures` 含 `amd64v3`。版本号请以 `apt policy mesa-vulkan-drivers` 本地实测为准。
- **Liquorix 的安装脚本**：`liquorix.net/ubuntu/dists/resolute/` 存在已实测，但**安装流程未实测**（本报告不给未经验证的一键脚本）。
- **XanMod `le9uo` 的实际游戏收益**：无任何公开的游戏对照基准。"内存吃紧时可能有帮助"是基于第九轮结论的**结构性推断**，不是实测。
- **Ubuntu 7.0 与 XanMod 7.2 的游戏帧率对照**：不存在。Phoronix 做的是发行版间对比，不是内核间对比。
- **Ubuntu amd64v3 的游戏帧率增益**：无游戏专项对照数据（Phoronix 只做了桌面/服务器负载）。第十二轮 KB 已记录同一缺口。
- **26.04 LTS 后续 HWE 栈的内核版本**：未核实（影响"是否还需要第三方内核拿新硬件支持"的判断）。
- **Phoronix 那 99 项测试的具体构成**：只取到汇总（51/38/10 与 geo mean 结论），未逐项核对。文中提到 Llama.cpp 的 OpenBLAS CPU 后端 Windows 明显更快、Vulkan 后端三者接近 —— 说明测试含 AI 负载，不全是游戏。

---

## 十一、参考来源

- Phoronix — *Ubuntu 26.04 LTS vs. Windows 11 vs. CachyOS Performance On A $5399 Laptop*（2026-07-15）：https://www.phoronix.com/review/razer-blade18-windows-linux
- Phoronix — *Canonical Experimenting With x86-64-v3 Packages For Ubuntu 26.10*（2026-06-08）：https://www.phoronix.com/news/Ubuntu-26.10-amd64v3-Packages
- Phoronix — *Ubuntu 26.10 amd64v3 Daily ISOs Now Being Published*（2026-09-07）：https://www.phoronix.com/news/Ubuntu-26.10-amd64v3-Daily
- Phoronix — *Ubuntu 25.10 amd64v3 Benchmarks*（2025-10-31，"Some Minor & Rare Performance Advantages For Desktop Workloads"）
- Ubuntu 26.04 LTS 归档索引（本次直接抓取）：https://archive.ubuntu.com/ubuntu/dists/resolute/
- 异次元软件 — *Ubuntu 26.04 LTS 新功能汇总，值得升级吗？*（2026-04-27，含 amd64v3 opt-in 配置与 Linux 7.0 特性）：https://www.iplaysoft.com/ubuntu-2604.html
- 腾讯云开发者社区 — *Ubuntu 26.04 LTS 正式发布*（2026-03-24 / 05-06）
- XanMod 官方（特性清单 + APT 仓库说明 + psABI 变体表）：https://xanmod.org/
- XanMod resolute 仓库（本次直接抓取）：https://deb.xanmod.org/dists/resolute/Release
- Liquorix resolute 仓库（本次直接抓取）：https://liquorix.net/ubuntu/dists/resolute/Release
- kisak-mesa PPA（本次直接抓取）：https://ppa.launchpadcontent.net/kisak/kisak-mesa/ubuntu/dists/resolute/
- oibaf graphics-drivers PPA（本次直接抓取）：https://ppa.launchpadcontent.net/oibaf/graphics-drivers/ubuntu/dists/resolute/

---

## 十二、关联文档

- [`../kb/ubuntu2604-thirdparty-kernel-mesa-ppa.md`](../kb/ubuntu2604-thirdparty-kernel-mesa-ppa.md)（本轮 KB 沉淀）
- [`x86-64-v3-mesa-by-distro.md`](x86-64-v3-mesa-by-distro.md) / [`.html`](x86-64-v3-mesa-by-distro.html)（第十二轮：各发行版 v3 Mesa 供给清单）
- [`../kb/x86-64-v3-mesa-by-distro.md`](../kb/x86-64-v3-mesa-by-distro.md)
- [`proton-cachyos-and-flatpak.md`](proton-cachyos-and-flatpak.md)（第十一轮：proton-cachyos 独立使用 + Flatpak）
- [`proton-games-optimization.md`](proton-games-optimization.md)（第十轮：Proton 游戏优化收益排序 + NTSync 口径）
- [`cpu-bound-sim-games-optimization.md`](cpu-bound-sim-games-optimization.md)（第九轮：原生 CPU 密集模拟游戏）
- [`../cachyos/kb/cachyos-proton-games-optimization.md`](kb/cachyos-proton-games-optimization.md)
- [`../cachyos/kb/cachyos-cpu-bound-strategy-games.md`](kb/cachyos-cpu-bound-strategy-games.md)
