# CachyOS 优化对 Proton 运行游戏的收益排序（2077 / Palworld / Soulmask 等）

- **调研日期**：2026-10-16
- **聚焦问题**：如果游戏是通过 Proton 运行的（如赛博朋克 2077、幻兽帕鲁 Palworld、灵魂面甲 Soulmask），CachyOS 哪一项优化收益最大？
- **承接**：`cpu-bound-sim-games-optimization.md`（原生单线程模拟游戏，第九轮）
- **一句话结论**：**冠军换层了。** 原生游戏里"编译层无效"，是因为游戏二进制由厂商预编译；**Proton 游戏多了一整层"发行版自己维护并重编译"的代码——Wine / DXVK / vkd3d-proton / Mesa，正好在 CPU 关键路径上**。所以 CachyOS 的招牌（v3/v4 + LTO/PGO/BOLT）**第一次真正生效**，收益最大的单项变成**翻译层 + 运行时栈**（Proton-CachyOS / DXVK / vkd3d-proton / Mesa 的发行版优化构建），其次是 **NTSync**（内核级 NT 同步原语，收益主要在帧时间一致性而非平均帧）。

---

## 一、与原生游戏的结构性差异（这是全部结论的来源）

| 维度 | 原生 Linux 游戏（RimWorld / 群星 / CK3） | **Proton 运行的游戏（2077 / Palworld / Soulmask）** |
|---|---|---|
| 游戏本体 | 原生 ELF 二进制，**厂商预编译** | **Windows PE 二进制**，仍是厂商预编译 |
| 关键路径上还有什么 | 几乎只有游戏自己的代码 | **多了一整层：Wine(ntdll/kernel32) → DXVK(D3D9/10/11→Vulkan) → vkd3d-proton(D3D12→Vulkan) → Mesa RADV/驱动** |
| 这层由谁构建 | — | **发行版自己**（`proton-cachyos`、`dxvk`、`vkd3d-proton`、`mesa` 都是包） |
| CachyOS 招牌优化是否触达 | ❌ 碰不到游戏二进制 | ✅ **碰得到翻译层——而翻译层在 CPU 关键路径上** |
| 额外固定成本 | 无 | **翻译开销**（每个 draw call 要过 DXVK/vkd3d；每个同步调用要过 Wine） |

> **推论**：原生场景下 CachyOS 的编译层"打空"；Proton 场景下它**打在关键路径上**。这是两次提问结论不同的唯一原因。

---

## 二、收益排序（Proton 场景）

| 排名 | 优化项 | 预期收益 | 生效条件 | 是否 CachyOS 独有 |
|---|---|---|---|---|
| **1** | **翻译层 + 运行时栈的发行版优化构建**（Proton-CachyOS / DXVK / vkd3d-proton / Mesa 的 v3/v4 + LTO/PGO/BOLT 重编译） | CPU 受限时**个位数 %～十余 %** | 必须 CPU 受限 | ✅ **是** |
| **2** | **NTSync**（内核级 Windows NT 同步原语） | 平均帧 **≈ 0**（对比 esync/fsync）；**帧时间一致性 / 卡顿 / 1% low 改善** | 内核 ≥ 6.14；CachyOS 2025-03 起**默认启用** | ⚠️ 非独有，但**默认开启最早** |
| 3 | GPU 栈新版本 + FSR4 / Reflex / Anti-Lag 2 | 大（GPU 受限时） | — | ⚠️ 是"新"，不是"优化" |
| 4 | 调度延迟栈（BORE / EEVDF 调参 / 1000Hz / PREEMPT_DYNAMIC） | 卡顿 / 1% low | — | 部分 |
| 5 | 着色器缓存 / DXVK async（消除 shader 编译卡顿） | 首次进入场景的卡顿大幅减少 | 首次运行 | 部分（Proton-CachyOS 带 per-game 着色器缓存） |
| 6 | 编译层对**游戏本体** | **≈ 0**（游戏仍是 Windows 二进制，不重编译） | — | — |
| 7 | 内存层（ZRAM / THP / MGLRU） | 仅 Palworld / Soulmask **大基地**内存吃紧时有效 | RAM < 工作集 | — |

**筛选规则**：1、2、5 是 Proton 场景**新增**的有效项；6 依旧无效；4、7 与原生场景相同（降级为次要）。

---

## 三、冠军项详解：翻译层 + 运行时栈

### 3.1 为什么它是冠军

- DXVK / vkd3d-proton 要把**每一次 DirectX 调用翻译成 Vulkan**；Wine 要把**每一次 Windows syscall / 同步调用**翻译成 Linux 语义。这些代码**每一帧都在跑**，且**由发行版编译**。
- CachyOS 把它们按 `x86-64-v3/v4/znver4` 重编译，叠加 **LTO / PGO / BOLT**——**这正是 DXVK 这类"分支密集、指令密集"代码最吃优化**的场景。
- 侧证：DXVK 官方 release notes 自己就明确以 **"CPU-bound performance"** 作为发布标准（例如描述符缓冲绑定模型改动时写"expected to achieve roughly the same level of CPU-bound performance"）——说明这条路径的 CPU 开销是被项目本身当作一等指标在优化的。

### 3.2 但它**补不回**原生

必须说清楚上界：CachyOS 的优化是**把 Proton 的翻译开销往回补一点**，不是"让 Proton 超过原生"。

- 对 **CPU 密集**的游戏（大基地、密集 AI、大量 draw call），**原生 Linux 版（若有）通常仍优于 Proton**。
- 2077 / Palworld / Soulmask **都没有原生 Linux 版**，所以 Proton 是唯一路径——这时"减少翻译开销"才有意义。

### 3.3 Proton-CachyOS 额外给了什么

| 项 | 内容 | 是否提升帧率 |
|---|---|---|
| 构建来源 | 基于 Proton 前沿分支 + Wine-Staging 补丁，**优先用系统原生库编译** | 间接（吃到 v3/v4 收益） |
| FSR 4 | `PROTON_FSR4_UPGRADE=1` 自动下载应用 FSR 4 DLL | ✅ 帧率（GPU 受限时） |
| NVIDIA Reflex | 通过 `vkd3d-low-latency` 实现（2026-07） | ✅ 降低输入延迟 |
| OptiScaler | 向 FSR4 开放 DLSS 输入 | ✅ 帧率 |
| 着色器缓存 | per-game 着色器缓存 | ✅ 消除 shader 编译卡顿 |
| NTSync | `PROTON_USE_NTSYNC=1` | 一致性为主 |

---

## 四、亚军项详解：NTSync —— 必须打破媒体的夸大

### 4.1 它是什么

Windows 游戏用 NT 同步原语（mutex / semaphore / event）协调线程，**每秒可达百万次等待**。Wine 历史上靠 **wineserver 进程 RPC 往返**模拟这些调用——socket 发请求、wineserver 执行、回包。对多线程游戏这是真实瓶颈。

**NTSync**（Elizabeth Figura / CodeWeavers 开发）在**内核里**直接实现 NT 同步原语，暴露 `/dev/ntsync` 字符设备，**消除用户态往返**。2025-01 合并进 **Linux 6.14 主线**；**Wine 11.0（2026-01）默认启用**；**Proton 11** 跟进；CachyOS **2025-03 就把 Wine 补丁默认切到 NTSync**（早于多数发行版）。

### 4.2 那些"炸裂数字"的真实口径 ⚠️

流传的基准表**对比对象是「原版上游 Wine」**，而不是 esync / fsync：

| 游戏 | 上游 Wine | NTSync | 提升 |
|---|---|---|---|
| Dirt 3 | 110.6 | 860.7 | **+678%** |
| Resident Evil 2 | 26 | 77 | +196% |
| Tiny Tina's Wonderlands | 130 | 360 | +177% |
| Lara Croft: Temple of Osiris | 141 | 326 | +131% |
| Call of Juarez | 99.8 | 224.1 | +125% |
| The Crew | 26 | 51 | +96% |
| Forza Horizon | 108 | 160 | +48% |
| Anger Foot | 69 | 99 | +43% |
| Total War Saga: Troy | 109 | 146 | +35% |
| Metro 2033 | 164.4 | 199.2 | +21% |

**三条必须标注的限定**：
1. **对比基准是 vanilla Wine。** 而 Steam 玩家**很多年没用过原版 Wine** 了。
2. **对比 esync / fsync，NTSync 基本没有平均帧收益**——社区原话："don't expect 100 more fps, or even 10"。
3. **它的核心价值是"正确性"与一致性**，不是速度。开发者表述："NTSync isn't faster, it's more correct. It fixes subtle edge cases like **hitches and deadlocks**." 收益主要体现在 **1% / 0.1% low 与帧时间稳定性**、alt-tab 不冻结、不锁死。

### 4.3 对 2077 / Palworld / Soulmask 意味着什么

- 三者都是**现代多线程引擎**（REDengine 4 / UE5 / UE4-5），理论上属于 NTSync 的目标场景。
- 但它们**不是同步密集型的极端案例**（Dirt 3 那种"物理引擎疯狂同步"才是）。所以合理预期是：**一致性小幅改善，平均帧接近 0**。
- **不要为了 NTSync 换发行版**——内核 ≥ 6.14 的任何发行版都有，CachyOS 的优势只是"默认开 + 开得早"。

---

## 五、决定性的前置问题：CPU 受限还是 GPU 受限

同一款游戏，答案完全不同：

| 场景 | 瓶颈 | 有效项 |
|---|---|---|
| 2077 @ 4K 路径追踪 | **GPU 受限** | 只剩驱动版本、DLSS / FSR4、帧生成。**翻译层优化几乎无效** |
| 2077 夜之城人群密集区 / 1080p | CPU 受限 | 翻译层 + NTSync + 调度 |
| Palworld 大基地（大量帕鲁 / 掉落物） | CPU 受限 | 翻译层 + 调度；内存也可能吃紧 |
| Soulmask 大基地（大量建造物 / NPC） | CPU 受限 | 同上 |
| 三者 @ 4K 高画质 | GPU 受限 | 驱动 + 升频 |

> **实操判据**：先把画质/分辨率**降到最低**看帧率是否上升。
> - 上升 → GPU 受限 → CachyOS 的翻译层优化对你**没用**，去调 DLSS/FSR4/驱动。
> - 不上升 → CPU 受限 → 翻译层 + NTSync + 调度才有意义。

---

## 六、可复用操作

```bash
# 1) 确认 NTSync 可用（内核 >= 6.14）
uname -r
lsmod | grep ntsync || sudo modprobe ntsync
ls -l /dev/ntsync

# 2) Proton 侧启用（Proton 11+ 默认开；老版本手动）
#    Steam 启动项：
PROTON_USE_NTSYNC=1 %command%

# 3) 降低 Proton 的 CPU 开销：优先用发行版重编译过的 DXVK/vkd3d
#    Arch/CachyOS：pacman -S proton-cachyos dxvk-mingw vkd3d-proton-mingw
#    并在 Steam → 兼容性 → 强制使用指定 Proton 版本

# 4) 着色器卡顿：开启 DXVK 异步着色器（如发行版提供）
DXVK_ASYNC=1 %command%          # 部分构建才有；新版 DXVK 已默认异步

# 5) 低延迟（GPU 侧，Proton-CachyOS 已集成）
PROTON_FSR4_UPGRADE=1 %command% # 自动升级 FSR4 DLL
```

**判断该不该折腾的 60 秒实验**：同一存档，用 `MANGOHUD=1 %command%` 看 GPU 占用率——
- GPU 占用 < 90% → CPU 受限 → 上面这些**值得做**。
- GPU 占用 ≈ 100% → GPU 受限 → **别折腾**，去调画质与升频。

---

## 七、坑与反直觉

| 坑 | 说明 |
|---|---|
| **"NTSync 提升 678%"** | 对比的是**原版上游 Wine**。对比 esync/fsync **基本没有平均帧收益**。 |
| **"CachyOS 编译优化让游戏更快"** | 对原生游戏**无效**（碰不到游戏二进制）；对 Proton 游戏**有效但仅限翻译层**，量级个位数%。 |
| **"Proton 能超过原生"** | ❌。CachyOS 是**补回**翻译开销，不是消除它。CPU 密集型游戏有原生版就上原生版。 |
| **4K 下 CachyOS 优势消失** | 这条**在 Proton 场景同样成立**（与原生模拟游戏不同）。2077 4K 路径追踪是纯 GPU 瓶颈。 |
| **"换了发行版就快了"** | 对 Proton 游戏，**GPU 驱动版本**（Mesa RADV / NVIDIA 专有驱动）的版本差异，通常大于发行版优化差异。 |
| **2077 的 Proton 版本选择** | 社区反馈 2077 在 **Proton 8.0** 上帧率更稳、崩溃更少，而非越新越好 → 按游戏查 ProtonDB。 |
| **反例存在** | 有测试显示启用 FSR 3 的《第一后裔》Windows 11 以 63 FPS 领先 Linux 端 54 FPS → 升频技术的跨平台支持仍有差异。 |

---

## 八、未核实 / 存疑

- **没有** CachyOS 针对 2077 / Palworld / Soulmask 的**公开对照基准**（同机、同存档、同设置）。本报告量级为**结构性推断**。
- **"翻译层重编译带来十余 %"** 的上界未经实测标定；DXVK 官方只以 "roughly the same level of CPU-bound performance" 这类相对表述描述，未给出 CachyOS 构建的对照数据。
- **NTSync 对 2077 / Palworld / Soulmask 的具体收益**：无公开数据。现有基准表全部来自 Wine 上游对 vanilla Wine 的对比。
- **smzdm 转述的 CachyOS vs Win11 数字**（2077 平均 98 vs 91 FPS；星际战士2 1% low 72 vs 58，5600X + RX 6700XT）：**二手转述，未披露测试方法** → 方向性参考。
- **low_latency_layer（2026-05，统一 Anti-Lag 2 / Reflex 2）** 的实测数据来自二手转述，未核实一手基准。

---

## 九、两次提问的结论对照（一句话版）

| 游戏类型 | 冠军项 | 为什么 |
|---|---|---|
| **原生**（RimWorld / 群星 / CK3） | 内核**内存管理 + 调度延迟**层 | 编译层碰不到游戏二进制，只能靠系统层 |
| **Proton**（2077 / Palworld / Soulmask） | **翻译层 + 运行时栈**（Proton-CachyOS / DXVK / vkd3d / Mesa） | 翻译层是发行版重编译的代码，且在 CPU 关键路径上 |

**共同点**：两者的收益量级都在**个位数百分比**（除非内存吃紧或功耗受限，才可能出现量级差异）。**换发行版永远不是最大杠杆——硬件（X3D / 内存容量 / GPU 驱动版本）才是。**

---

## 参考来源

- [Phoronix — CachyOS Adds Limine Bootloader, Easier Samba Integration & NTSYNC Wine（2025-03-30）](https://www.phoronix.com/news/CachyOS-March-2025-Release)
- [Phoronix — Wine 11.0 For January Release With NTSYNC & New WoW64 Mode](https://www.phoronix.com/news/Wine-11.0-January-2026)
- [Phoronix — Operating Systems 评测列表（CachyOS 内核变体 / BORE 专项 / 跨发行版横评）](https://www.phoronix.com/reviews/Operating+Systems)
- [Phoronix — Linux/WINE 频道（Wine 11.x 系列发布）](https://www.phoronix.com/linux/WINE)
- [Wine 10.16 发布讨论 + NTSync 基准表（原始对比为 vanilla Wine）](https://piefed.zeromedia.vip/honey/48215)
- [Lemmy — Wine 11 rewrites how Linux runs Windows games（含"NTSync 对比 esync/fsync 无额外收益"的关键更正）](https://lemmy.org/post/4796101)
- [byteiota — Linux Gaming NTSYNC: 678% FPS Gains（含 Elizabeth Figura 的 50–150% 表述与"一致性 > 速度"分析）](https://byteiota.com/linux-gaming-ntsync-678-fps-gains-5-market-share)
- [什么值得买 —《Linux 跑 Windows 游戏，真的快了》（NTSync 时间线与瓶颈拆解）](https://post.smzdm.com/p/arzg575q)
- [什么值得买 —《Linux 打游戏竟比 Win11 还稳？Proton 黑科技让帧率反超》（含 CachyOS 游戏实测与反例）](https://post.smzdm.com/p/arz2q7p7/)
- [什么值得买 —《Linux 游戏性能竟超 Win11？》（Proton-CachyOS 功能清单）](https://post.smzdm.com/p/a263rl0q/)
- [DXVK Releases（以 CPU-bound performance 为发布标准）](https://github.com/doitsujin/dxvk/releases)
- [vkd3d-proton Releases（Direct3D 12 → Vulkan）](https://github.com/HansKristian-Work/vkd3d-proton/releases)
- [CachyOS 官网（CPU-specific package builds / 内核调度）](https://cachyos.org/)
- [百家号 — proton-cachyos 加入 NVIDIA Reflex 支持（vkd3d-low-latency）](https://baijiahao.baidu.com/s?id=1871489454503971896)
- [ProtonDB — Palworld](https://www.protondb.com/app/1623730)
- [ProtonDB — Just Cause 3（Proton-CachyOS 用户报告）](https://www.protondb.com/app/225540)

> **来源质量说明**：Phoronix、DXVK/vkd3d 官方仓库、CachyOS 官网为一手；Wine 上游的 NTSync 基准表为一手但**口径是 vanilla Wine**（本报告已明确标注）；什么值得买、百家号为二手转述，已标注。核心结论（Proton 场景冠军换层为翻译层 + 运行时栈）为**结构性推断**，机制明确但缺该场景的 CachyOS 对照实测。
