# 除 CachyOS 外，哪些发行版提供 x86-64-v3 编译的 Mesa（AMD RADV）？

- **调研日期**：2026-10-16
- **聚焦问题**：Mesa 有做 AMD v3 编译的，除了 CachyOS 之外，openSUSE 或 Ubuntu 是否有？
- **一句话结论**：**Ubuntu 有**（实验性、非官方支持、默认关闭，但**实测确认归档里含 v3 编译的 Mesa**）；**openSUSE 没有**（Tumbleweed 基线是 x86-64-**v2**，镜像里没有任何 v3 仓库）。顺带扫全：**Fedora 也没有**（v3 提案推迟到至少 F46）；真正"基线即 v3"的是 **RHEL 10 系**；**Gentoo** 有官方 v3 二进制包；**Arch 官方是 v1**，需靠第三方 **ALHP**。

---

## 一、直接回答

| 发行版 | v3 编译的 Mesa？ | 形式 | 状态 | 证据 |
|---|---|---|---|---|
| **CachyOS** | ✅ | 官方 `cachyos-v3` / `cachyos-v4` 仓库 | 默认 | 官方仓库结构 |
| **Ubuntu 25.10 / 26.10** | ✅ **有** | 归档里的独立架构组件 `binary-amd64v3` | **实验性 / 非官方支持 / 默认不启用** | **实测 HTTP 200 + 包清单含 Mesa** |
| **openSUSE Tumbleweed** | ❌ **没有** | —（基线 x86-64-v2） | 未提供 | 镜像目录实测无 v3 仓库 |
| **Fedora** | ❌ 没有 | — | **推迟到至少 Fedora 46** | Phoronix：`Fedora x86-64-v3 Optimized Packages Pushed Back To At Least Fedora 46` |
| **Arch Linux（官方）** | ❌ 没有 | 官方仓库仍是 `x86_64`（v1） | — | archlinux.org `mesa 1:26.2.2-1 Architecture: x86_64` |
| **Arch + ALHP** | ✅ | 第三方 `core/extra/multilib-x86-64-v{2,3,4}` | 活跃（2026-10-16 仍有更新） | alhp.dev 目录列表 |
| **RHEL 10 / Rocky 10 / Alma 10** | ✅ | **整仓库基线就是 x86-64-v3** | 正式 | Rocky Linux 10 公告 |
| **Gentoo** | ✅ | 官方二进制包 `releases/amd64/binpackages/23.0/x86-64-v3/` | 正式（**无 v4**） | 实测 HTTP 200 |
| **Amazon Linux 2027** | ✅ | x86-64-v3 + LTO | 预览 | Phoronix 2026-09-03 |
| **NixOS** | ❌ 官方缓存无 | nixpkgs 支持 v3 system type，官方缓存只发通用构建 | 需全量自编译 | nixpkgs 结构 |

---

## 二、Ubuntu：有，但是"实验性 + 默认关闭"

### 2.1 实测证据（本次直接抓取归档索引）

```
http://archive.ubuntu.com/ubuntu/dists/stonking/main/binary-amd64v3/Packages.gz      -> 200
http://archive.ubuntu.com/ubuntu/dists/stonking/universe/binary-amd64v3/Packages.gz  -> 200
http://archive.ubuntu.com/ubuntu/dists/questing/main/binary-amd64v3/Packages.gz      -> 200
http://archive.ubuntu.com/ubuntu/dists/questing/universe/binary-amd64v3/Packages.gz  -> 200
http://archive.ubuntu.com/ubuntu/dists/plucky/main/binary-amd64v3/Packages.gz        -> 404
```

> `stonking` = Ubuntu 26.10、`questing` = 25.10、`plucky` = 25.04。
> **→ 从 25.10 起才有 amd64v3；25.04 及更早没有。**

### 2.2 Mesa 确实在里面（这是问题的核心）

**26.10 `main/binary-amd64v3`**（该组件共 **6,446 个包**）：

```
Package: mesa-vulkan-drivers     ← RADV（AMD Vulkan 驱动）在这里
Package: mesa-libgallium
Package: libgl1-mesa-dri
Package: libglx-mesa0
Package: mesa-common-dev
Package: libgl1-mesa-dev
```

**26.10 `universe/binary-amd64v3`**：

```
Package: mesa-utils        Package: mesa-va-drivers
Package: mesa-utils-bin    Package: mesa-vdpau-drivers
Package: mesa-opencl-icd   Package: mesa-drm-shim
```

**25.10 `main/binary-amd64v3`** 同样含 `mesa-vulkan-drivers` / `mesa-libgallium` / `libgl1-mesa-dri`。

→ **Ubuntu 有做 v3 编译的 Mesa，且 RADV（`mesa-vulkan-drivers`）在内。**

### 2.3 怎么用（两条路径）

1. **直接用 amd64v3 ISO**（推荐）：Ubuntu 26.10 的 daily ISO 自 **2026-09-04** 起同时发布 `amd64v3` 镜像（与通用 amd64、arm64、riscv64 并列）。这是官方为简化流程新加的。
2. **改装**：先装通用 amd64 的 ISO/包，再调整 APT 指向 `binary-amd64v3` 组件并升级。

### 2.4 官方定位（Phoronix 原文）

> "Canonical hasn't **officially introduced a supported solution** but they have offered x86_64-v3/amd64v3 package archives **for testing**."
> "the amd64v3 archive **isn't currently enabled by default** on capable systems or anything along those lines"

→ **可用，但不在支持范围内。**

---

## 三、openSUSE：没有

| 检查项 | 结果 |
|---|---|
| Tumbleweed 指令集基线 | **x86-64-v2**（2022 年起从 v1 过渡） |
| `download.opensuse.org/tumbleweed/repo/` 实际内容 | `oss` / `non-oss` / `update` / `debug` / `ports` / `source` / `factory` —— **无任何 v3 仓库** |
| 探测 `tumbleweed/repo/oss-x86_64-v3/` | 404 |
| 探测 `tumbleweed/repo/x86_64-v3/` | 404 |
| 探测 `ports/x86_64-v3/tumbleweed/repo/oss/` | 404 |

**结论**：openSUSE Tumbleweed 想要 v3 编译的 Mesa，**只能自己编译**（或用 OBS 自建仓库），发行版不提供。

> 注意区分：openSUSE 的 **v2** 基线已经高于 Arch / Fedora / Ubuntu 官方仓库的 **v1**——但它不是 v3。

---

## 四、重要校准：v3 Mesa 到底值多少？（别高估）

| 证据 | 结论 |
|---|---|
| Phoronix《Ubuntu 25.10 amd64v3 Benchmarks》**2025-10-31** | 标题即：**"Some Minor & Rare Performance Advantages For Desktop Workloads"** —— **收益小且零散** |
| Phoronix《Ubuntu 26.10 amd64v3 Packages...》**2026-10-14** | 在 **AMD EPYC** 上有 "some additional uplift"（**服务器负载更明显**） |
| 机制 | RADV 的**着色器编译走 LLVM**，面向实际 GPU、与宿主 ISA 级别基本无关；受益的是**主机侧 Mesa 代码**（状态设置、命令缓冲构建、描述符管理），AVX2 能帮上的幅度有限 |

> **对游戏而言：Mesa 的「版本」≫ Mesa 的「ISA 级别」。**
> 想提升 A 卡游戏性能，优先级应是：**更新的 Mesa（mesa-git / kisak PPA / 新发行版）> 内核与固件 > v3 重编译**。

---

## 五、坑与反直觉

| 坑 | 说明 |
|---|---|
| Ubuntu amd64v3 当成正式功能 | ❌ **实验性、不受官方支持**；混装 v1/v3 包有依赖风险 |
| 以为 openSUSE 有 v3 | ❌ 它是 **v2** 基线。比 v1 高，但不是 v3 |
| 以为 Fedora 有 v3 | ❌ 提案**推迟到至少 Fedora 46** |
| 把 ALHP 与 CachyOS 仓库混用 | ❌ 两套 v3 仓库都覆盖 core/extra，混用会打架 |
| 忽略硬件门槛 | v3 需 **Intel Haswell（2013）/ AMD Excavator** 及更新；v4 需 **AVX-512**（消费级大多没有，这也是 CachyOS 只给 Proton 发 v3 变体的原因） |
| 期待"换 v3 白捡帧数" | 桌面游戏负载实测是**小且零散**的收益；4K/GPU 受限时归零 |

---

## 六、未核实 / 存疑

- **ALHP 的确切仓库 URL**：我按常见路径（`mirror.alhp.dev/x86-64-v3/core/os/x86_64/core.db`）探测得 **404**，但 `alhp.dev/` 的目录列表明确显示 `core-x86-64-v3/`、`extra-x86-64-v3/`、`multilib-x86-64-v3/`（含 v2/v4）存在且 `lastupdate` 为 **2026-10-16** → **仓库存在，路径以官方文档为准**。
- **Void Linux 是否有 v3 仓库**：未找到任何证据，暂记为"无"。
- **openMandriva 的 znver4 优化构建**：未核实。
- **Amazon Linux 2027**：仅知为预览状态，具体包覆盖未核实。
- **Ubuntu amd64v3 的实测游戏帧率增益**：Phoronix 的结论是"桌面负载收益小且零散"，但**没有游戏专项对照数据**。

---

## 参考来源

- [Phoronix — Canonical Experimenting With x86-64-v3 Packages For Ubuntu 26.10（2026-06-08）](https://www.phoronix.com/news/Ubuntu-26.10-amd64v3-Packages)
- [Phoronix — Ubuntu 26.10 amd64v3 Daily ISOs Now Being Published（2026-09-07）](https://www.phoronix.com/news/Ubuntu-26.10-amd64v3-Daily)
- [Ubuntu 26.10（stonking）amd64v3 归档索引](https://archive.ubuntu.com/ubuntu/dists/stonking/main/binary-amd64v3/)
- [Phoronix — Fedora x86-64-v3 Optimized Packages Pushed Back To At Least Fedora 46](https://www.phoronix.com/news/Fedora-x86-64-v3-Delayed-F46)
- [Phoronix — Fedora Yet To Decide On x86_64-v3 Packages For Fedora Linux 45](https://www.phoronix.com/news/Fedora-x86-64-v3-Undecided)
- [Phoronix — Ubuntu 25.10 amd64v3 Benchmarks: Some Minor & Rare Performance Advantages For Desktop Workloads（2025-10-31）](https://www.phoronix.com/search/AVX)
- [Phoronix — Ubuntu 26.10 amd64v3 Packages Provide Some Additional Uplift On AMD EPYC（2026-10-14）](https://www.phoronix.com/reviews/Operating+Systems)
- [ALHP 仓库目录列表（core/extra/multilib 的 v2/v3/v4）](https://alhp.dev/)
- [Arch Linux — mesa 1:26.2.2-1 (x86_64)（官方仓库为 v1）](https://www.archlinux.org/packages/extra/x86_64/mesa/)
- [Rocky Linux 10.0 GA 公告（x86-64-v3 基线）](https://rockylinux.org/news/rocky-linux-10-0-ga-release)
- [Gentoo 官方 x86-64-v3 二进制包仓库](https://distfiles.gentoo.org/releases/amd64/binpackages/23.0/x86-64-v3/)
- [openSUSE Tumbleweed 过渡到 x86-64-v2 的报道（2022-11）](https://baijiahao.baidu.com/s?id=1750799707561198248)
- [Phoronix — Amazon Linux 2027 Now in Preview: Powered By Linux 7.1, x86-64-v3 & Built With LTO（2026-09-03）](https://www.phoronix.com/search/AVX)

> **来源质量说明**：Ubuntu 归档索引、ALHP 目录列表、Gentoo 二进制仓库、Arch 官方包页、openSUSE 镜像目录均为**本次直接 HTTP 探测/抓取**（一手）；Phoronix 文章为一手媒体。ALHP 的确切仓库 URL 与 Void/openMandriva 的状态**未核实**，已在第六节标注。
