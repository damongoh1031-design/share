---
id: ubuntu2604-thirdparty-kernel-mesa-ppa
title: Ubuntu 26.04 LTS 上第三方内核与 Mesa PPA 的取舍（XanMod / Liquorix / kisak / oibaf）
tags:
  - linux
  - ubuntu
  - ubuntu-2604-lts
  - xanmod
  - liquorix
  - mesa
  - amd64v3
  - 内核
  - 游戏性能
created: 2026-10-16
updated: 2026-10-16
version: 1.0
status: stable
source: 本次直接 HTTP/API 探测（Ubuntu 归档、Launchpad PPA、deb.xanmod.org、liquorix.net）+ Phoronix 同机实测 + 官方文档
confidence: 已核实
---

# Ubuntu 26.04 LTS：第三方内核与 Mesa PPA 的取舍

## TL;DR

**在 Ubuntu 26.04 LTS 上，第三方内核基本不值得，Mesa PPA 按需，而 amd64v3 应该直接用官方的（一行配置）。**

1. **amd64v3 官方自带**：`resolute` 的 `main`/`universe`/`restricted`/`multiverse` + `-updates` + `-security` 六个位置**全部有 `binary-amd64v3`**（实测 200），含 `mesa-vulkan-drivers`（RADV）/ `libc6` / `libvulkan1` / `libdrm2`。开启：`APT::Architecture-Variants "amd64v3"`（opt-in）。
2. **Mesa PPA 按需**：`kisak-mesa` 在 resolute 上 = **Mesa 26.2.5**（自带 26.0.3），两个主流 PPA 都发 `amd64v3` 变体。只在遇到具体 Mesa/RADV bug、新硬件、或需要新特性时装。
3. **第三方内核基本不值得**：XanMod（resolute ✓，7.2.11，`x64v1/v2/v3`）和 Liquorix（resolute ✓，7.2.10，**仅 amd64**）都只比自带的 **Linux 7.0.0-14** 新一点点，而 7.0 已含 `sched_ext` + MGLRU + NTSync。代价：DKMS 易碎 + 无安全更新承诺。
4. **量级参照**：Phoronix 同机 99 项测试，CachyOS 全套优化赢 51%、Ubuntu 26.04 LTS 只赢 10%（垫底 43%），但**几何平均是"窄胜"** → 连整套优化都只险胜，单换内核能分到的更小。

---

## 1. Ubuntu 26.04 LTS 基线（实测/官方）

| 项 | 值 | 备注 |
|---|---|---|
| 代号 / 发布 | Resolute Raccoon / 2026-04-23 | 支持到 2031-04，Pro 到 2036 |
| 内核 | **Linux 7.0.0-14.14**（`linux-image-generic`） | 跳过 6.20；含 sched_ext / MGLRU / NTSync |
| Mesa | **26.0.3-1ubuntu1** | `mesa-vulkan-drivers` |
| amd64v3 | ✅ 官方 opt-in | 归档已就绪，默认关 |
| 图形会话 | **Wayland 唯一**（X11 会话已移除）；VRR 默认开；HDR 原生 | ⚠️ 影响 Mesa PPA 的风险评估 |
| 实时内核 | PREEMPT_RT 进主仓库，免费 | — |
| NVIDIA | 595 系 | CachyOS 同期为 R610 |
| 工具链 | GCC 15.2 / Python 3.13.9 / Rust 1.93 / APT 3.0 | APT 3.0 有 `apt history-undo` |

---

## 2. amd64v3：用官方的，别用第三方

### 2.1 实测可用位置

```
dists/resolute/main/binary-amd64v3/Packages.gz           200
dists/resolute/universe/binary-amd64v3/Packages.gz       200
dists/resolute/restricted/binary-amd64v3/Packages.gz     200
dists/resolute/multiverse/binary-amd64v3/Packages.gz     200
dists/resolute-updates/main/binary-amd64v3/Packages.gz   200
dists/resolute-security/main/binary-amd64v3/Packages.gz  200
```

`-updates` / `-security` 也有 → **开 v3 不掉出安全更新通道**。

### 2.2 机制（关键，易误解）

```
Package: mesa-vulkan-drivers
Architecture: amd64          ← 仍是 amd64，不是 amd64v3
Version: 26.0.3-1ubuntu1

main/amd64v3 包数 = 6487
main/amd64   包数 = 6487     ← 完全相同
```

→ 同一批源码、同一套依赖，用 `-march=x86-64-v3` 重编译的**平行构建**，靠 APT 3.0 的 *Architecture Variants* 切换。**不是新 dpkg 架构 → v1 与 v3 不能共存，只能整体切。**

### 2.3 开启 / 回滚

```bash
# 前置：CPU 需 AVX2 / FMA / BMI1 / BMI2 / MOVBE（三条 grep 结果都要有）
grep -o -m1 -E 'avx2|bmi2|fma' /proc/cpuinfo | sort -u

echo 'APT::Architecture-Variants "amd64v3";' | sudo tee /etc/apt/apt.conf.d/99enable-amd64v3
sudo apt update && sudo apt full-upgrade

# 回滚
sudo rm /etc/apt/apt.conf.d/99enable-amd64v3 && sudo apt update
```

**无 amd64v3 ISO**：实测 `releases.ubuntu.com/26.04/` 只有 `ubuntu-26.04-desktop-amd64.iso` / `-live-server-amd64.iso` / `26.04.1` 同款。v3 是"装完之后开"。（26.10 有 amd64v3 daily ISO。）

### 2.4 收益

Phoronix 对 Ubuntu 25.10 amd64v3 的标题即 *"Some Minor & Rare Performance Advantages For Desktop Workloads"*。机制：RADV 着色器编译走 LLVM（面向 GPU，与宿主 ISA 无关），受益的只是主机侧 Mesa 代码。
→ **收益小，成本≈0，值得开。**

---

## 3. Mesa PPA 对比（resolute 实测）

| 来源 | resolute 可用 | Mesa 版本 | 发 amd64v3 |
|---|---|---|---|
| Ubuntu 自带 | — | **26.0.3-1ubuntu1** | ✅ |
| `kisak/kisak-mesa` | ✅ Release 200 | **26.2.5~kisak1~r** | ✅ 200 |
| `oibaf/graphics-drivers` | ✅ Release 200 | mesa-git 每日构建（版本未取到） | ✅ 200 |

两个 PPA 的 `Release` 里 `Architectures:` 都含 `amd64v3` → **PPA + v3 可叠加**。

**装的条件**：遇到具体 Mesa/RADV bug / 新硬件支持不全 / 需要新版特性（FSR4、新 RADV 优化、新 VK 扩展）/ 新游戏对 Mesa 版本敏感。
**不装的条件**：26.0.3 已能跑你的游戏（收益≈0）。

**26.04 特有的风险**：X11 会话已移除 → Mesa 出问题**没有 X11 兜底**（24.04 时代不存在此风险）。回滚必须用 `ppa-purge`。

---

## 4. 第三方内核实测（resolute）

| 内核 | resolute | 版本 | ISA 变体 | 仓库 |
|---|---|---|---|---|
| XanMod | ✅ Release 200 | 7.2.11-xanmod1 | `x64v1/v2/v3`（**无 v4**） | `deb.xanmod.org` |
| Liquorix | ✅ Release 200 | 7.2-18ubuntu1~resolute（内核 7.2.10） | **仅 amd64** | `liquorix.net/ubuntu/` |
| Ubuntu 自带 | — | 7.0.0-14.14 | `amd64` + `amd64v3` | 官方归档 |

**结构差异**：Liquorix 版本串含 `ubuntu1~resolute` → 是**拿 Ubuntu 内核源码包 + Zen/Liquorix 补丁集重建**，故只有 `amd64` 单架构（无 v3），但贴合 Ubuntu 模块 ABI。XanMod 是**独立树**（`gitlab.com/xanmod/linux`），版本跟主线更紧。

### XanMod 净增量（对比 Ubuntu 7.0）

| XanMod 特性 | 26.04 已有 | 净增量 |
|---|---|---|
| MGLRU | ✅ | 0 |
| sched_ext | ✅ | 0 |
| BBRv3 默认 | 部分 | 小 |
| **Firelzrd `le9uo`**（内存压力下保护匿名页/干净页） | ❌ | **★ 唯一真实增量** |
| Clear Linux 补丁集（部分） | ❌ | 小～中 |
| LLVM Polly / Software Pipelining | ❌ | 小 |
| Graysky GCC/Clang CPU 选项 | ❌ | 小 |

`le9uo` 对照本系列第九轮结论（CPU 密集模拟游戏冠军 = 内核内存管理 + 调度延迟层；唯一量级差异场景 = 内存吃紧时避免磁盘 swap）→ **内存吃紧（≤16GB、大存档群星/CK3）时是唯一有理论依据的第三方内核增量**（无游戏实测基准）。

### 风险（XanMod 官方自述）

> *"The current NVIDIA, OpenZFS, VirtualBox, VMware Workstation / Player and some other dkms modules **may not support the latest kernel versions**."*

- DKMS 断裂（26.04 用 NVIDIA 595，模块可能编不过 → nouveau / 黑屏）
- **无安全更新承诺**（Ubuntu LTS 承诺不覆盖第三方内核）
- 回滚需手动选 GRUB 旧内核
- 无"Ubuntu 7.0 vs XanMod 7.2"游戏对照基准
- Ubuntu Pro Livepatch 失效

---

## 5. 收益校准：CachyOS vs Ubuntu 26.04 LTS 同机

Phoronix 2026-07-15，Razer Blade 18 RZ09-0582（Core Ultra 9 290HX Plus + RTX 5090 Laptop，$5399）。

| | Ubuntu 26.04 LTS | CachyOS | Windows 11 |
|---|---|---|---|
| 内核 | 7.0 | 7.1 | — |
| 编译器 | GCC 15.2 | GCC 16.1.1 | MSVC |
| NVIDIA | R595 | **R610** | 官方 |

**99 项测试：**

| 指标 | CachyOS | Windows 11 | Ubuntu 26.04 LTS |
|---|---|---|---|
| 第一的比例 | **51%** | 38% | **10%** |
| 垫底的比例 | — | ~50% | **43%** |
| 几何平均 | **窄胜** | 微胜 Ubuntu | 三者最末 |

原文：*"On a geo mean basis, Microsoft Windows 11 just edged past Ubuntu 26.04 LTS … Meanwhile CachyOS battled the two to secure a narrow victory on a geo mean basis."*

**推论（重要）**：CachyOS 的份额里混了 ① 更新的 NVIDIA 驱动（R610 vs R595）② 全套用户态 v3/v4 重编译 ③ 新内核 + BORE。其中 ② 用 Ubuntu 官方 amd64v3 就能拿到大头，① 换内核完全拿不到，③ 量级是个位数百分比。
→ 该数据**支持"开官方 v3 + 按需 Mesa PPA"**，**不支持"为性能换第三方内核"**。

---

## 6. 可复用操作

```bash
# 开官方 amd64v3
echo 'APT::Architecture-Variants "amd64v3";' | sudo tee /etc/apt/apt.conf.d/99enable-amd64v3
sudo apt update && sudo apt full-upgrade
# 回滚
sudo rm /etc/apt/apt.conf.d/99enable-amd64v3 && sudo apt update

# 前后对照（换任何东西都先跑一遍基线）
uname -r
glxinfo -B | grep -E 'OpenGL renderer|OpenGL version'
vulkaninfo --summary 2>/dev/null | grep -E 'driverName|apiVersion'
apt policy mesa-vulkan-drivers linux-image-generic

# kisak-mesa PPA（按需）
sudo add-apt-repository ppa:kisak/kisak-mesa
sudo apt update && sudo apt full-upgrade
sudo apt install ppa-purge && sudo ppa-purge ppa:kisak/kisak-mesa   # 干净回滚

# XanMod（⚠️ 装前备份 + 确认 DKMS 能编；保留 Ubuntu 原内核以便 GRUB 回退）
wget -qO - https://dl.xanmod.org/archive.key | sudo gpg --dearmor -vo /etc/apt/keyrings/xanmod-archive-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/xanmod-archive-keyring.gpg] http://deb.xanmod.org $(lsb_release -sc) main" \
  | sudo tee /etc/apt/sources.list.d/xanmod-release.list
sudo apt update && apt-cache search '^linux-xanmod'
sudo apt install --no-install-recommends dkms libelf-dev clang lld llvm
sudo apt install linux-xanmod-x64v3
```

---

## 7. 坑与反直觉

| 坑 | 说明 |
|---|---|
| 以为 v3 要靠第三方 | ❌ 26.04 官方就带，且 `-security`/`-updates` 也有 |
| 以为 v3 是新架构能共存 | ❌ `Architecture: amd64`，是变体；不能 v1+v3 同时装 |
| 以为 26.04 有 v3 ISO | ❌ 实测只有 `amd64` ISO（26.10 才有 v3 daily） |
| 忽略 26.04 无 X11 兜底 | ⚠️ Wayland 唯一 → Mesa PPA 风险高于 24.04 |
| 以为换内核能拿 CachyOS 的差距 | ❌ 差距里混了 NVIDIA 驱动大版本 + 全套用户态 v3/v4 重编译 |
| 以为 XanMod 有 x64v4 | ❌ 只有 v1/v2/v3；官方标注 "x86-64-v4 (AVX-512) (no kernel benefit)" |
| 以为 Liquorix 有 v3 | ❌ `Architectures: amd64`，只有 v1 |
| 忽略 DKMS | ⚠️ XanMod 官方明说 NVIDIA/OpenZFS/VirtualBox/VMware 模块可能不支持最新内核 |
| 把第三方内核当 LTS 的一部分 | ❌ LTS 承诺（到 2031）不覆盖第三方内核 |
| 用 `apt remove` 回滚 PPA | ❌ 用 `ppa-purge` |

---

## 8. 未核实 / 存疑

- **`linux-bqx`**：GitHub 仓库搜索、AUR RPC 搜索、中文网络检索、Launchpad 全部零结果 → **未能确认存在**。可能候选：Liquorix（`lqx`）、XanMod、CachyOS 的 `linux-cachyos-bore`/`-bmq`（Arch 专属）、linux-tkg、BFQ（其实是 IO 调度器）。
- **oibaf PPA 在 resolute 的确切 Mesa 版本**：`Packages.gz` 多次抓取超时/为空；只确认 `Release` = 200 且 `Architectures` 含 `amd64v3`。
- **Liquorix 安装流程**：仓库存在已实测，安装步骤未实测。
- **XanMod `le9uo` 的游戏实测收益**：无公开基准，属结构性推断。
- **Ubuntu 7.0 vs XanMod 7.2 的游戏帧率对照**：不存在。
- **Ubuntu amd64v3 的游戏帧率增益**：无游戏专项对照（Phoronix 只测桌面/服务器）。
- **26.04 LTS 后续 HWE 栈的内核版本**：未核实。
- **Phoronix 99 项测试的逐项构成**：只取到汇总；文中提到含 Llama.cpp 等 AI 负载，不全是游戏。

---

## 9. 参考来源

- Phoronix — Ubuntu 26.04 LTS vs. Windows 11 vs. CachyOS Performance On A $5399 Laptop（2026-07-15）：https://www.phoronix.com/review/razer-blade18-windows-linux
- Phoronix — Canonical Experimenting With x86-64-v3 Packages For Ubuntu 26.10（2026-06-08）：https://www.phoronix.com/news/Ubuntu-26.10-amd64v3-Packages
- Phoronix — Ubuntu 25.10 amd64v3 Benchmarks（2025-10-31）
- Ubuntu 26.04 归档索引（本次抓取）：https://archive.ubuntu.com/ubuntu/dists/resolute/
- 异次元软件 — Ubuntu 26.04 LTS 新功能汇总（2026-04-27，含 amd64v3 opt-in 配置）：https://www.iplaysoft.com/ubuntu-2604.html
- XanMod 官方：https://xanmod.org/
- XanMod resolute 仓库（本次抓取）：https://deb.xanmod.org/dists/resolute/Release
- Liquorix resolute 仓库（本次抓取）：https://liquorix.net/ubuntu/dists/resolute/Release
- kisak-mesa PPA（本次抓取）：https://ppa.launchpadcontent.net/kisak/kisak-mesa/ubuntu/dists/resolute/
- oibaf graphics-drivers PPA（本次抓取）：https://ppa.launchpadcontent.net/oibaf/graphics-drivers/ubuntu/dists/resolute/

---

## 10. 关联文档

- `cachyos/ubuntu2604-kernel-and-mesa-ppa.md` / `.html`（本轮完整报告）
- [`x86-64-v3-mesa-by-distro.md`](x86-64-v3-mesa-by-distro.md)（各发行版 v3 Mesa 供给清单）
- [`../cachyos/kb/cachyos-proton-games-optimization.md`](../cachyos/kb/cachyos-proton-games-optimization.md)（Proton 游戏优化 + NTSync + Flatpak）
- [`../cachyos/kb/cachyos-cpu-bound-strategy-games.md`](../cachyos/kb/cachyos-cpu-bound-strategy-games.md)（原生 CPU 密集模拟游戏）
