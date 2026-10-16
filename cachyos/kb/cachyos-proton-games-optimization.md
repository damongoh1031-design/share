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
version: 1.0
status: stable
source: Phoronix / DXVK / vkd3d-proton / CachyOS 官网（一手）+ Wine 上游 NTSync 基准表（一手，口径 vanilla Wine）+ 结构性推断
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

## 10. 参考来源

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

---

## 11. 关联文档

- `cachyos/proton-games-optimization.md` / `.html`（本轮完整报告）
- [`cachyos-cpu-bound-strategy-games.md`](./cachyos-cpu-bound-strategy-games.md)（原生单线程模拟游戏，第九轮）
- `cachyos/gaming-optimization-deepdive.md`（四层优化清单 / BORE 参数表）
- `cachyos/distro-performance-comparison.md`（六发行版横比与方法论）
