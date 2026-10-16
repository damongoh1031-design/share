---
id: cachyos-proton-games-optimization
title: CachyOS 优化对 Proton 运行游戏的收益排序（2077 / Palworld / Soulmask 等）
tags:
  - cachyos
  - linux-gaming
  - proton
  - dxvk
  - vkd3d
  - ntsync
  - cpu-bound
created: 2026-10-16
updated: 2026-10-16
version: 2.0
status: stable
source: Phoronix / DXVK / vkd3d-proton / CachyOS 官网 / proton-cachyos GitHub Releases API / flatpak issue #6199 / flathub Steam manifest（一手核实）+ 结构性推断
confidence: 推断
---

# CachyOS 优化对 Proton 运行游戏的收益排序

## TL;DR

**冠军换层了。** 原生游戏里"编译层无效"，是因为游戏二进制由厂商预编译；**Proton 游戏多了一整层"发行版自己维护并重编译"的代码——Wine / DXVK / vkd3d-proton / Mesa，正好在 CPU 关键路径上**。所以 CachyOS 的招牌（v3/v4 + LTO/PGO/BOLT）**第一次真正生效**，冠军变成**翻译层 + 运行时栈**；亚军 **NTSync** 的收益主要在**帧时间一致性**，不在平均帧。

---

## 1. 与原生游戏的结构性差异（全部结论的来源）

```
原生游戏：  游戏二进制（厂商预编译） ──▶ 内核 / glibc
Proton 游戏：游戏二进制（厂商预编译） ──▶ Wine → DXVK / vkd3d-proton → Mesa RADV ──▶ 内核
                                        └── 这一整层是发行版的包，CachyOS 会重编译它
```

| 维度 | 原生 Linux 游戏 | Proton 运行的游戏 |
|---|---|---|
| 游戏本体 | 原生 ELF，厂商预编译 | Windows PE，**仍是厂商预编译** |
| 关键路径上还有什么 | 几乎只有游戏自己的代码 | **Wine → DXVK(D3D9/10/11) → vkd3d-proton(D3D12) → Mesa/驱动** |
| 这层由谁构建 | — | **发行版自己**（`proton-cachyos` / `dxvk` / `vkd3d-proton` / `mesa` 都是包） |
| 招牌优化是否触达 | ❌ 碰不到 | ✅ **碰得到，且在 CPU 关键路径上** |
| 额外固定成本 | 无 | **翻译开销**：每个 draw call 过 DXVK/vkd3d，每个同步调用过 Wine |

---

## 2. 收益排序

| 排名 | 优化项 | 预期收益 | 生效条件 | CachyOS 独有？ |
|---|---|---|---|---|
| **1** | **翻译层 + 运行时栈的发行版优化构建**（Proton-CachyOS / DXVK / vkd3d-proton / Mesa 的 v3/v4 + LTO/PGO/BOLT） | CPU 受限时**个位数 %～十余 %** | 必须 CPU 受限 | ✅ 是 |
| **2** | **NTSync**（内核级 Windows NT 同步原语） | 平均帧 **≈ 0**（对比 esync/fsync）；**一致性 / 卡顿 / 1% low 改善** | 内核 ≥ 6.14 | ⚠️ 非独有，但默认开启最早 |
| 3 | GPU 栈新版本 + FSR4 / Reflex / Anti-Lag 2 | 大（GPU 受限时） | — | ⚠️ 是"新"不是"优化" |
| 4 | 调度延迟栈（BORE / EEVDF 调参 / 1000Hz / PREEMPT_DYNAMIC） | 卡顿 / 1% low | — | 部分 |
| 5 | 着色器缓存 / DXVK async（消除 shader 编译卡顿） | 首次进入场景的卡顿大幅减少 | 首次运行 | 部分 |
| 6 | 编译层对**游戏本体** | **≈ 0** | — | — |
| 7 | 内存层（ZRAM / THP / MGLRU） | 仅 Palworld / Soulmask **大基地**内存吃紧时 | RAM < 工作集 | — |

**新增有效项**：1、2、5。**仍无效**：6。**降级为次要**：4、7。

---

## 3. 冠军项：翻译层 + 运行时栈

- DXVK / vkd3d-proton 要把**每一次 DirectX 调用翻译成 Vulkan**；Wine 要把**每一次 Windows syscall / 同步调用**翻译成 Linux 语义。这些代码**每一帧都在跑**，且**由发行版编译**。
- CachyOS 把它们按 `x86-64-v3/v4/znver4` 重编译并叠加 **LTO / PGO / BOLT**——正是"分支密集、指令密集"代码最吃优化的场景。
- **侧证**：DXVK 官方 release notes 以 **"CPU-bound performance"** 作为发布标准（描述符绑定模型改动时写"expected to achieve roughly the same level of CPU-bound performance"）。

**上界**：CachyOS 是**把翻译开销往回补一点**，不是让 Proton 超过原生。CPU 密集型游戏**有原生版就上原生版**。2077 / Palworld / Soulmask 都无原生版，所以这条路径才有意义。

**Proton-CachyOS 额外给的**：基于 Proton 前沿分支 + Wine-Staging 补丁、优先用系统原生库编译；FSR4 自动升级（`PROTON_FSR4_UPGRADE=1`）；NVIDIA Reflex（`vkd3d-low-latency`）；OptiScaler；per-game 着色器缓存；NTSync（`PROTON_USE_NTSYNC=1`）。

---

## 4. 亚军项：NTSync —— 必须打破媒体的夸大

**它是什么**：Windows 游戏用 NT 同步原语（mutex / semaphore / event）协调线程，**每秒可达百万次等待**。Wine 历史上靠 **wineserver 进程 RPC 往返**模拟（socket 发请求 → wineserver 执行 → 回包），对多线程游戏是真实瓶颈。**NTSync**（Elizabeth Figura / CodeWeavers）在**内核里**直接实现，暴露 `/dev/ntsync`，消除用户态往返。2025-01 进 **Linux 6.14 主线**；**Wine 11.0（2026-01）默认启用**；**Proton 11** 跟进；**CachyOS 2025-03 就把 Wine 补丁默认切到 NTSync**（Phoronix 报道）。

**流传的基准表（⚠️ 对比对象是 vanilla Wine，不是 esync/fsync）**：

| 游戏 | 上游 Wine | NTSync | 提升 |
|---|---|---|---|
| Dirt 3 | 110.6 | 860.7 | +678% |
| Resident Evil 2 | 26 | 77 | +196% |
| Tiny Tina's Wonderlands | 130 | 360 | +177% |
| Lara Croft: Temple of Osiris | 141 | 326 | +131% |
| Call of Juarez | 99.8 | 224.1 | +125% |
| The Crew | 26 | 51 | +96% |
| Forza Horizon | 108 | 160 | +48% |
| Anger Foot | 69 | 99 | +43% |
| Total War Saga: Troy | 109 | 146 | +35% |
| Metro 2033 | 164.4 | 199.2 | +21% |

**三条限定**：
1. 对比基准是 **vanilla Wine**；Steam 玩家很多年没用过原版 Wine。
2. 对比 **esync / fsync**，NTSync **基本没有平均帧收益**（社区原话："don't expect 100 more fps, or even 10"）。
3. 核心价值是**正确性 + 一致性**："NTSync isn't faster, it's more correct. It fixes subtle edge cases like **hitches and deadlocks**." → 收益在 **1%/0.1% low**、alt-tab 不冻结、不锁死。

**对 2077 / Palworld / Soulmask**：三者都是现代多线程引擎（REDengine 4 / UE5 / UE4-5），理论上属目标场景，但**不是同步密集型极端案例**（Dirt 3 才是）。合理预期：**一致性小幅改善，平均帧接近 0**。**不要为了 NTSync 换发行版**——内核 ≥ 6.14 的任何发行版都有。

---

## 5. 决定性前置问题：CPU 受限还是 GPU 受限

| 场景 | 瓶颈 | 有效项 |
|---|---|---|
| 2077 @ 4K 路径追踪 | GPU 受限 | 只剩驱动版本、DLSS / FSR4、帧生成 |
| 2077 夜之城人群密集区 / 1080p | CPU 受限 | 翻译层 + NTSync + 调度 |
| Palworld 大基地（大量帕鲁 / 掉落物） | CPU 受限 | 翻译层 + 调度；内存也可能吃紧 |
| Soulmask 大基地（大量建造物 / NPC） | CPU 受限 | 同上 |
| 三者 @ 4K 高画质 | GPU 受限 | 驱动 + 升频 |

**60 秒实操判据**：`MANGOHUD=1 %command%` 看 GPU 占用率 —— **< 90% → CPU 受限，值得做；≈ 100% → GPU 受限，别折腾**。

---

## 6. 可复用操作

```bash
# 1) 确认 NTSync 可用（内核 >= 6.14）
uname -r
lsmod | grep ntsync || sudo modprobe ntsync
ls -l /dev/ntsync

# 2) Proton 侧启用（Proton 11+ 默认开；老版本手动）
PROTON_USE_NTSYNC=1 %command%

# 3) 优先用发行版重编译过的 DXVK / vkd3d-proton
pacman -S proton-cachyos dxvk-mingw vkd3d-proton-mingw   # Arch/CachyOS
# 然后在 Steam → 兼容性 → 强制指定 Proton 版本

# 4) 低延迟 / 升频（Proton-CachyOS 已集成）
PROTON_FSR4_UPGRADE=1 %command%    # 自动升级 FSR4 DLL
MANGOHUD=1 %command%               # 看 GPU 占用率，判断瓶颈
```

---

## 7. 坑与反直觉

| 坑 | 说明 |
|---|---|
| "NTSync 提升 678%" | 对比的是**原版上游 Wine**；对比 esync/fsync 基本没有平均帧收益。 |
| "CachyOS 编译优化让游戏更快" | 对原生游戏**无效**；对 Proton 游戏**有效但仅限翻译层**，量级个位数%。 |
| "Proton 能超过原生" | ❌。CachyOS 是**补回**翻译开销，不是消除它。 |
| "4K 下优势消失" | 这条**在 Proton 场景同样成立**（与原生模拟游戏不同）。 |
| "换了发行版就快了" | 对 Proton 游戏，**GPU 驱动版本**（Mesa RADV / NVIDIA 专有）的差异通常大于发行版优化差异。 |
| 2077 的 Proton 版本 | 社区反馈 2077 在 **Proton 8.0** 上更稳、崩溃更少，并非越新越好 → 按游戏查 ProtonDB。 |
| 反例存在 | 有测试显示启用 FSR 3 的《第一后裔》Windows 11 以 63 FPS 领先 Linux 端 54 FPS。 |

---

## 8. 未核实 / 存疑

| 项 | 说明 |
|---|---|
| CachyOS 针对 2077 / Palworld / Soulmask 的对照基准 | **不存在**公开数据；本报告量级为结构性推断 |
| "翻译层重编译带来十余 %" 的上界 | 未经实测标定；DXVK 官方只给相对表述 |
| NTSync 对这三款游戏的具体收益 | 无公开数据；现有基准表全部是对 vanilla Wine 的对比 |
| smzdm 转述的 CachyOS vs Win11 数字（2077 平均 98 vs 91 FPS；星际战士2 1% low 72 vs 58，5600X + RX 6700XT） | 二手转述，未披露方法 → 方向性参考 |
| low_latency_layer（2026-05，统一 Anti-Lag 2 / Reflex 2） | 数据来自二手转述，未核实一手基准 |

---

## 9. 两次提问的结论对照

| 游戏类型 | 冠军项 | 为什么 |
|---|---|---|
| **原生**（RimWorld / 群星 / CK3） | 内核**内存管理 + 调度延迟**层 | 编译层碰不到游戏二进制，只能靠系统层 |
| **Proton**（2077 / Palworld / Soulmask） | **翻译层 + 运行时栈** | 翻译层是发行版重编译的代码，且在 CPU 关键路径上 |

**共同点**：收益量级都在**个位数百分比**（除非内存吃紧或功耗受限）。**换发行版永远不是最大杠杆——硬件（X3D / 内存容量 / GPU 驱动版本）才是。**

---

## 10. 部署变体：只装 proton-cachyos 拿到多少（v2.0 新增）

**决定性事实（一手核实）**：proton-cachyos 的 GitHub release 直接发布**独立 tarball**，且**含 `x86_64_v3` 变体**：

| 资产（tag `cachyos-11.0-20261005-slr`） | 说明 |
|---|---|
| `proton-cachyos-11.0-20261005-slr-x86_64.tar.xz` | 通用基线（v1） |
| **`proton-cachyos-11.0-20261005-slr-x86_64_v3.tar.xz`** | **x86-64-v3 优化构建** |
| `proton-cachyos-11.0-20261005-slr-arm64.tar.xz` | ARM64 |

→ **不需要装 CachyOS 就能拿到 v3 优化的翻译层**。官方只发 v3（不发 v4，因 AVX-512 覆盖面太窄）。

| 优化项 | 只装 proton-cachyos | 说明 |
|---|---|---|
| 翻译层（Wine / DXVK / vkd3d 的 v3 构建） | ✅ **保留** | 官方 `_v3` tarball 自带 |
| Proton-CachyOS 补丁（FSR4 / Reflex / OptiScaler / 着色器缓存 / UMU） | ✅ 保留 | 在同一个包里 |
| CachyOS 内核（BORE / EEVDF / 1000Hz / 补丁集） | ❌ 拿不到 | 需装 `linux-cachyos` 内核 |
| Mesa / RADV 的 v3/v4 构建 | ❌ 拿不到 | **Proton 不打包 Mesa**，用宿主的 |
| NTSync | ⚠️ 取决于宿主 | 需内核 ≥ 6.14 + 加载 `ntsync` |
| CachyOS-Settings（sysctl / IO / ZRAM / THP / 电源档） | ❌ 拿不到 | 发行版层 |
| 优化过的 glibc | ❌ 拿不到 | 宿主提供 |

**结论**：拿到约**一半**——「翻译层」那一半（也正是冠军项）。

---

## 11. Flatpak 下损失多少（v2.0 新增）

### 11.1 沙箱开销可忽略，代价在"换栈"

Flatpak 用 bubblewrap **命名空间隔离**，**不拦截系统调用** → 沙箱本身对帧率影响可忽略。
**真正的代价**：Flatpak 应用的依赖来自 runtime（`org.freedesktop.Platform`），**不是宿主**。实测清单：

```
Mesa  org.freedesktop.Platform.GL.default  25.1.7  24.08  system
```

→ **Flatpak Steam 里的 Mesa 来自 runtime 扩展，不是宿主的 Mesa**；glibc 同理。

| 维度 | Flatpak Steam 下 | 影响 |
|---|---|---|
| Mesa / RADV | ❌ runtime 版本 | **在 CachyOS 上丢掉 v3/v4 优化构建**；滚动发行版上可能比宿主旧 |
| glibc | ❌ runtime 版本 | 丢掉宿主 v3/v4 优化 |
| NVIDIA 专有驱动 | ✅ 宿主提供 | GL extension 挂载宿主驱动 → N 卡受影响较小 |
| 内核（调度 / 内存 / NTSync 驱动） | ✅ 宿主内核 | CachyOS 内核收益**保留** |
| 沙箱开销 | 可忽略 | — |

### 11.2 `/dev/ntsync` 在 Flatpak 下**可用**

Flatpak 对新设备类型的默认策略：「**允许通过 `--device=all`，否则不允许**」（flatpak issue #6199）。而 **Flatpak Steam 的 manifest 含 `--device=all`**（实测 `com.valvesoftware.Steam.yml` 第 45 行，另有 `--allow=multiarch`、`--allow=devel`）→ **`/dev/ntsync` 应当可见**（仍需内核 ≥ 6.14）。

### 11.3 NTSync 性能口径（flatpak 维护者，一手权威）

- "**ntsync is around the same speed as fsync**"（平均帧同级）
- 价值在 "better game/app compatibility ... and **better 1% lows** (less CPU overhead and less RAM usage)"
- "**If you have a fast CPU it would typically already handle fsync without much issues. People who are very CPU-bottlenecked would probably still see a big performance improvement with ntsync though.**"
- "not change as much as some people have been misled to believe based on benchmarks that **compared vanilla wine (no esync/fsync hacks) vs ntsync**"
- 实测例：**3600X + 5700XT 上部分游戏 1% low 翻约三倍**
- 机制：esync/fsync **完全忽略** waitstate 调用；NTSync 在内核真正实现 → "**which is why CPU bound situations under Linux punished frame rates**"

### 11.4 三种部署方式的收益保留度

| 优化层 | 原生 CachyOS | 别的发行版 + proton-cachyos(v3) | Flatpak Steam（+ v3 Proton） |
|---|---|---|---|
| 翻译层 v3 优化 | ✅ | ✅ | ✅ 需手动放入 |
| Proton-CachyOS 补丁 | ✅ | ✅ | ✅ 需手动放入 |
| CachyOS 内核 | ✅ | ❌ | ✅ 宿主内核 |
| Mesa / RADV v3/v4 | ✅ | ❌ 用宿主 Mesa | ❌ **用 runtime Mesa** |
| glibc 优化 | ✅ | ❌ | ❌ |
| NTSync | ✅ 默认开 | ⚠️ 需内核 ≥ 6.14 | ⚠️ 需内核 ≥ 6.14 |
| CachyOS-Settings | ✅ | ❌ | ❌ |
| 沙箱开销 | 无 | 无 | 可忽略 |

**一句话**：**翻译层优化可以"打包带走"，系统层优化不能。**

### 11.5 操作

```bash
# 任何发行版：装 v3 版 proton-cachyos（无需装 CachyOS）
TAG="cachyos-11.0-20261005-slr"      # 用前先查最新 tag
mkdir -p ~/.steam/root/compatibilitytools.d
curl -LO "https://github.com/CachyOS/proton-cachyos/releases/download/$TAG/proton-cachyos-11.0-20261005-slr-x86_64_v3.tar.xz"
tar -xf proton-cachyos-11.0-20261005-slr-x86_64_v3.tar.xz -C ~/.steam/root/compatibilitytools.d/

# Flatpak Steam：同一份 tarball，换个目录
mkdir -p ~/.var/app/com.valvesoftware.Steam/data/Steam/compatibilitytools.d
tar -xf proton-cachyos-11.0-20261005-slr-x86_64_v3.tar.xz \
    -C ~/.var/app/com.valvesoftware.Steam/data/Steam/compatibilitytools.d/

# 确认沙箱里的内核与 NTSync
flatpak run --command=sh com.valvesoftware.Steam -c 'uname -r; ls -l /dev/ntsync'
```

### 11.6 新增坑（v2.0）

| 坑 | 说明 |
|---|---|
| "Flatpak 更慢" | 沙箱开销可忽略；真正的代价是**图形栈被换成 runtime 版本** |
| 在 CachyOS 上用 Flatpak Steam | 相当于**自废武功**：宿主优化过的 Mesa/glibc 被换成 runtime 通用版 |
| 从 AUR 装 proton-cachyos = 官方构建？ | ❌ 自行编译的 flag 取决于本机与 PKGBUILD；要 v3 就用官方 `_v3` tarball |
| v3 变体硬件要求 | 需 CPU 支持 **AVX2**（Intel Haswell 2013+ / AMD Excavator+） |
| Flatpak runtime 的 Mesa 版本 | 可能**比宿主旧**（滚动发行版尤其） |

### 11.7 新增未核实（v2.0）

- 官方 `_v3` tarball 的**具体编译 flag**（是否含 LTO/PGO/BOLT，还是仅 `-march=x86-64-v3`）→ **未核实**，仅确认资产名
- Flatpak 沙箱内 `/dev/ntsync` 的**实测**可用性 → 基于 manifest 的**推断**
- **Flatpak vs 原生 Steam 的帧率对照基准** → 不存在；"沙箱开销可忽略"为机制推断

---

## 12. 参考来源

- Phoronix — CachyOS Adds Limine Bootloader, Easier Samba Integration & NTSYNC Wine（2025-03-30）：https://www.phoronix.com/news/CachyOS-March-2025-Release
- Phoronix — Wine 11.0 For January Release With NTSYNC & New WoW64 Mode：https://www.phoronix.com/news/Wine-11.0-January-2026
- Phoronix — Operating Systems 评测列表：https://www.phoronix.com/reviews/Operating+Systems
- Wine 10.16 发布讨论 + NTSync 基准表（原始对比为 vanilla Wine）：https://piefed.zeromedia.vip/honey/48215
- Lemmy — Wine 11 rewrites how Linux runs Windows games（含"NTSync 对比 esync/fsync 无额外收益"的关键更正）：https://lemmy.org/post/4796101
- byteiota — Linux Gaming NTSYNC: 678% FPS Gains：https://byteiota.com/linux-gaming-ntsync-678-fps-gains-5-market-share
- 什么值得买 —《Linux 跑 Windows 游戏，真的快了》：https://post.smzdm.com/p/arzg575q
- 什么值得买 —《Linux 打游戏竟比 Win11 还稳？Proton 黑科技让帧率反超》：https://post.smzdm.com/p/arz2q7p7/
- DXVK Releases：https://github.com/doitsujin/dxvk/releases
- vkd3d-proton Releases：https://github.com/HansKristian-Work/vkd3d-proton/releases
- CachyOS 官网：https://cachyos.org/
- ProtonDB — Palworld / Just Cause 3：https://www.protondb.com/app/1623730 、https://www.protondb.com/app/225540
- **CachyOS/proton-cachyos — GitHub Releases API（资产清单含 `x86_64_v3` tarball）**：https://api.github.com/repos/CachyOS/proton-cachyos/releases/403217640/assets
- **proton-cachyos release tag `cachyos-11.0-20261005-slr`**：https://github.com/CachyOS/proton-cachyos/releases/tag/cachyos-11.0-20261005-slr
- **flatpak/flatpak Issue #6199 — `/dev/ntsync` 权限 + NTSync 性能权威表述**：https://github.com/flatpak/flatpak/issues/6199
- **flathub/com.valvesoftware.Steam — manifest（`--device=all` / `--allow=multiarch` / `--allow=devel`）**：https://github.com/flathub/com.valvesoftware.Steam/blob/master/com.valvesoftware.Steam.yml

---

## 13. 关联文档

- `cachyos/proton-games-optimization.md` / `.html`（第十轮完整报告）
- `cachyos/proton-cachyos-and-flatpak.md` / `.html`（第十一轮完整报告：部署变体 + Flatpak）
- [`cachyos-cpu-bound-strategy-games.md`](./cachyos-cpu-bound-strategy-games.md)（原生单线程模拟游戏，第九轮）
- `cachyos/gaming-optimization-deepdive.md`（四层优化清单 / BORE 参数表）

---

## 14. 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0 | 2026-10-16 | 初版。冠军 = 翻译层 + 运行时栈；亚军 NTSync（含 vanilla Wine 口径纠正） |
| **2.0** | 2026-10-16 | 新增 §10 **部署变体**（官方发布 `x86_64_v3` 独立 tarball → 不装 CachyOS 也能拿到翻译层优化）、§11 **Flatpak**（沙箱开销可忽略，代价是图形栈被 runtime 替换；`--device=all` 使 `/dev/ntsync` 可用；flatpak 维护者对 NTSync 性能的权威表述）；新增三种部署方式的收益保留度矩阵与操作命令 |
- `cachyos/distro-performance-comparison.md`（六发行版横比与方法论）
