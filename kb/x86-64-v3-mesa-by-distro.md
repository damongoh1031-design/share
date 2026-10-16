---
id: x86-64-v3-mesa-by-distro
title: 各发行版是否提供 x86-64-v3 编译的 Mesa（AMD RADV）
tags:
  - linux
  - mesa
  - radv
  - x86-64-v3
  - ubuntu
  - opensuse
  - fedora
  - cachyos
  - 发行版对比
created: 2026-10-16
updated: 2026-10-16
version: 1.0
status: stable
source: 本次直接 HTTP 探测 Ubuntu/ALHP/Gentoo/openSUSE 仓库（一手）+ Phoronix（一手媒体）+ 发行版官方公告
confidence: 已核实
---

# 各发行版是否提供 x86-64-v3 编译的 Mesa（AMD RADV）

## TL;DR

**Ubuntu 有**（25.10 起，归档独立架构组件 `binary-amd64v3`，**实测含 `mesa-vulkan-drivers` / `mesa-libgallium` / `libgl1-mesa-dri`**；实验性、非官方支持、默认关闭）。
**openSUSE 没有**（Tumbleweed 基线 x86-64-**v2**，镜像里无任何 v3 仓库）。
**Fedora 也没有**（v3 提案推迟到至少 Fedora 46）。
真正"基线即 v3"的是 **RHEL 10 系**；**Gentoo** 有官方 v3 二进制包；**Arch 官方是 v1**，需第三方 **ALHP**。
**但 v3 Mesa 对游戏的收益是小且零散的——Mesa 的「版本」≫ Mesa 的「ISA 级别」。**

---

## 1. 供给清单（2026-10-16）

| 发行版 | v3 Mesa？ | 形式 | 状态 |
|---|---|---|---|
| CachyOS | ✅ | 官方 `cachyos-v3` / `cachyos-v4` 仓库 | 默认 |
| **Ubuntu 25.10 / 26.10** | ✅ | 归档独立架构组件 `binary-amd64v3` | **实验性 / 非官方 / 默认关闭** |
| **openSUSE Tumbleweed** | ❌ | —（基线 v2） | 未提供 |
| Fedora | ❌ | — | 推迟到至少 **F46** |
| Arch Linux（官方） | ❌ | 官方仓库仍为 `x86_64`（v1） | — |
| Arch + ALHP | ✅ | 第三方 `core/extra/multilib-x86-64-v{2,3,4}` | 活跃 |
| RHEL 10 / Rocky 10 / Alma 10 | ✅ | **整仓库基线即 x86-64-v3** | 正式 |
| Gentoo | ✅ | 官方二进制包 `binpackages/23.0/x86-64-v3/` | 正式（无 v4） |
| Amazon Linux 2027 | ✅ | x86-64-v3 + LTO | 预览 |
| NixOS | ❌ | nixpkgs 支持 v3 system type，官方缓存只发通用构建 | 需全量自编译 |

---

## 2. Ubuntu：实测证据与用法

### 2.1 归档索引探测（HTTP 状态码）

```
dists/stonking/main/binary-amd64v3/Packages.gz      200   # 26.10
dists/stonking/universe/binary-amd64v3/Packages.gz  200
dists/questing/main/binary-amd64v3/Packages.gz      200   # 25.10
dists/questing/universe/binary-amd64v3/Packages.gz  200
dists/plucky/main/binary-amd64v3/Packages.gz        404   # 25.04 —— 还没有
```

**→ 从 25.10 起才有；25.04 及更早没有。**

### 2.2 Mesa 在里面（26.10 `main/binary-amd64v3`，该组件 6,446 个包）

```
Package: mesa-vulkan-drivers     ← RADV（AMD Vulkan 驱动）
Package: mesa-libgallium
Package: libgl1-mesa-dri
Package: libglx-mesa0
Package: mesa-common-dev
Package: libgl1-mesa-dev
```
`universe/binary-amd64v3`：`mesa-utils` / `mesa-va-drivers` / `mesa-vdpau-drivers` / `mesa-opencl-icd` / `mesa-drm-shim`。
25.10（questing）同样含 `mesa-vulkan-drivers` / `mesa-libgallium` / `libgl1-mesa-dri`。

### 2.3 用法

1. **直接用 amd64v3 ISO**（推荐）：26.10 daily ISO 自 **2026-09-04** 起同时发布 `amd64v3` 镜像。
2. **改装**：先装通用 amd64 ISO/包，再调整 APT 指向 `binary-amd64v3` 组件并升级。

官方定位（Phoronix 原文）："Canonical hasn't **officially introduced a supported solution** but they have offered x86_64-v3/amd64v3 package archives **for testing**"；"the amd64v3 archive **isn't currently enabled by default**"。

---

## 3. openSUSE：实测无 v3

| 检查项 | 结果 |
|---|---|
| Tumbleweed 基线 | **x86-64-v2**（2022 年起从 v1 过渡） |
| `download.opensuse.org/tumbleweed/repo/` 实际内容 | `oss` / `non-oss` / `update` / `debug` / `ports` / `source` / `factory` —— **无 v3 仓库** |
| 探测 `repo/oss-x86_64-v3/`、`repo/x86-64-v3/`、`ports/x86_64-v3/` | 全部 **404** |

**结论**：想要 v3 Mesa 只能自编译（或用 OBS 自建）。注意 openSUSE 的 **v2** 基线已高于 Arch / Fedora / Ubuntu 官方的 **v1**，但仍不是 v3。

---

## 4. 关键校准：v3 Mesa 对游戏值多少

| 证据 | 结论 |
|---|---|
| Phoronix《Ubuntu 25.10 amd64v3 Benchmarks》2025-10-31 | 标题即 **"Some Minor & Rare Performance Advantages For Desktop Workloads"** —— 收益小且零散 |
| Phoronix《Ubuntu 26.10 amd64v3 Packages...》2026-10-14 | 在 **AMD EPYC** 上有 "some additional uplift"（服务器负载更明显） |
| 机制 | RADV 的**着色器编译走 LLVM**（面向实际 GPU，与宿主 ISA 无关）；受益的是**主机侧 Mesa 代码**（状态设置 / 命令缓冲构建 / 描述符管理），AVX2 增益有限 |

**优先级**：更新的 Mesa（mesa-git / kisak PPA / 新发行版） > 内核与固件 > v3 重编译。

---

## 5. 可复用操作

```bash
# 判断本机是否支持 v3（需 AVX2/FMA/BMI1/BMI2/MOVBE）
grep -o -m1 -E 'avx2|bmi2|fma' /proc/cpuinfo | sort -u

# Ubuntu：检查 amd64v3 组件是否可用
curl -sI "http://archive.ubuntu.com/ubuntu/dists/$(lsb_release -cs)/main/binary-amd64v3/Packages.gz" | head -1

# Arch：ALHP（注意：不要与 CachyOS 仓库混用）
#   /etc/pacman.conf 追加（URL 以 ALHP 官方文档为准）：
#   [core-x86-64-v3]
#   Server = https://<alhp-mirror>/x86-64-v3/$repo/os/$arch

# 看 Mesa 版本与 RADV 是否在用（比 ISA 级别更重要的指标）
glxinfo -B | grep -E 'OpenGL renderer|OpenGL version'
vulkaninfo --summary 2>/dev/null | grep -E 'driverName|apiVersion'
```

---

## 6. 坑与反直觉

| 坑 | 说明 |
|---|---|
| 把 Ubuntu amd64v3 当正式功能 | ❌ 实验性、不受支持；混装 v1/v3 包有依赖风险 |
| 以为 openSUSE 有 v3 | ❌ 它是 **v2** 基线，比 v1 高但不是 v3 |
| 以为 Fedora 有 v3 | ❌ 提案推迟到至少 Fedora 46 |
| ALHP 与 CachyOS 仓库混用 | ❌ 两套都覆盖 core/extra，会打架 |
| 忽略硬件门槛 | v3 需 Intel Haswell（2013）/ AMD Excavator+；v4 需 AVX-512（消费级大多没有） |
| 期待"换 v3 白捡帧数" | 桌面游戏负载实测**小且零散**；4K / GPU 受限时归零 |

---

## 7. 未核实 / 存疑

- **ALHP 的确切仓库 URL**：常见路径探测 404，但 `alhp.dev/` 目录列表显示 `core/extra/multilib-x86-64-v3`（含 v2/v4）存在且 `lastupdate` = 2026-10-16 → 仓库存在，路径以官方文档为准。
- **Void Linux 是否有 v3 仓库**：未找到证据，暂记"无"。
- **openMandriva 的 znver4 优化构建**：未核实。
- **Amazon Linux 2027**：仅知为预览状态，包覆盖未核实。
- **Ubuntu amd64v3 的实测游戏帧率增益**：无游戏专项对照数据（Phoronix 只做了桌面/服务器负载）。

---

## 8. 参考来源

- Phoronix — Canonical Experimenting With x86-64-v3 Packages For Ubuntu 26.10（2026-06-08）：https://www.phoronix.com/news/Ubuntu-26.10-amd64v3-Packages
- Phoronix — Ubuntu 26.10 amd64v3 Daily ISOs Now Being Published（2026-09-07）：https://www.phoronix.com/news/Ubuntu-26.10-amd64v3-Daily
- Ubuntu 26.10（stonking）amd64v3 归档索引：https://archive.ubuntu.com/ubuntu/dists/stonking/main/binary-amd64v3/
- Phoronix — Fedora x86-64-v3 Optimized Packages Pushed Back To At Least Fedora 46：https://www.phoronix.com/news/Fedora-x86-64-v3-Delayed-F46
- ALHP 仓库目录列表：https://alhp.dev/
- Arch Linux — mesa 1:26.2.2-1 (x86_64)：https://www.archlinux.org/packages/extra/x86_64/mesa/
- Rocky Linux 10.0 GA 公告（x86-64-v3 基线）：https://rockylinux.org/news/rocky-linux-10-0-ga-release
- Gentoo 官方 x86-64-v3 二进制包：https://distfiles.gentoo.org/releases/amd64/binpackages/23.0/x86-64-v3/
- Phoronix — Amazon Linux 2027 Preview: Linux 7.1, x86-64-v3 & LTO（2026-09-03）：https://www.phoronix.com/search/AVX
- openSUSE 过渡到 x86-64-v2 的报道（2022-11）：https://baijiahao.baidu.com/s?id=1750799707561198248

---

## 9. 关联文档

- `cachyos/x86-64-v3-mesa-by-distro.md` / `.html`（本轮完整报告）
- [`cachyos-proton-games-optimization.md`](../../cachyos/kb/cachyos-proton-games-optimization.md)（Proton 游戏优化收益 + 部署变体 + Flatpak）
- [`cachyos-cpu-bound-strategy-games.md`](../../cachyos/kb/cachyos-cpu-bound-strategy-games.md)（原生单线程模拟游戏）
