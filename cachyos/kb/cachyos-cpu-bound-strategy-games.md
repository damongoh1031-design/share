---
id: cachyos-cpu-bound-strategy-games
title: CachyOS 对 CPU 密集型策略/模拟游戏的优化收益（RimWorld / 群星 / CK3）
tags:
  - cachyos
  - linux-gaming
  - cpu-bound
  - scheduler
  - simulation-games
  - memory-management
  - kernel
created: 2026-10-16
updated: 2026-10-16
version: 2.0
status: stable
source: CachyOS 官方 Wiki/GitHub（一手核实）+ Paradox 官方开发者日志（一手）+ 社区实测 + 结构性推断
confidence: 推断
---

# CachyOS 对 CPU 密集型策略/模拟游戏的优化收益

## 一句话结论

对 RimWorld / 群星 / CK3 这类单线程 + 内存延迟敏感的大战略模拟游戏，**CachyOS 的招牌优化（全仓库 x86-64-v3/v4 + LTO/PGO/BOLT 重编译）收益 ≈ 0**——游戏二进制由厂商预编译，发行版重编译碰不到它。**收益最大的单项取决于机器条件**：

| 机器条件 | 冠军项 | 量级 |
|---|---|---|
| **功耗受限**（笔记本 / 掌机 / 小机箱 / 温度墙） | `game-performance` 电源档 / 单核睿频维持 | 可显著 |
| **内存吃紧**（重度 mod 存档 / RAM < 工作集） | `vm.swappiness=100` + ZRAM + THP/MGLRU | 0 或**量级** |
| **两者都不成立**（台式 + 内存充足） | 只剩内核调度延迟层 | 个位数百分比 |

**参照系**：群星 3.14 → 4.3 官方提速约 **2.6×**（同一台 i9-14900K）。发行版层能拿到的（个位数百分比）与游戏自身优化差一个数量级。

---

## 1. 瓶颈画像（决定一切的前提）

| 游戏 | 引擎 | 主瓶颈 | 后期内存足迹 | 缓存/内存延迟敏感度 |
|---|---|---|---|---|
| RimWorld | Unity (Mono) | 单线程 TPS，主线程单核 100% | 轻度 4–8 GB；重度 mod 8–30 GB | 极高 |
| 群星 Stellaris | Clausewitz | 单核为主 + **部分多线程**；瓶颈含 **CPU 等待**与**内存分配抖动**（官方 4.3 日志） | 1000 星后期 8–16 GB | 高 |
| CK3 | Clausewitz | 主核 CPU0 长期高占用 + 内存带宽压力 | 后期 6–10 GB | 高 |

**四个共同点**：①"后期慢" = 单线程吞吐不足；②指针追逐 + 大工作集 → 对 L3 容量/内存延迟敏感；③内存足迹随时间单调增长；④显卡几乎不参与（任何分辨率都 CPU 瓶颈）。

**推论**：真正能加速它们的只有 **单核 IPC × 频率**、**内存延迟/带宽**、**L3 容量**、**RAM 容量**。发行版只能碰到其中两项的一半。

---

## 2. CachyOS 四层优化 × 瓶颈匹配

| 层 | 具体项 | 作用于游戏执行路径？ | 预期收益 | 置信度 |
|---|---|---|---|---|
| 编译层 | v3/v4/znver4 + LTO/PGO/BOLT/AutoFDO | ❌ 不覆盖游戏二进制 | ≈ 0（间接 <1–2%） | 高 |
| 内核层 | MGLRU + Cachy Sauce MM 调参 + THP(`defer+madvise`) | ✅ 内存回收与 TLB | +1–5%（内存压力越大越高） | 中 |
| 内核层 | BORE / EEVDF 调参 / SCX / sched-cluster + 1000Hz + PREEMPT_DYNAMIC | ✅ 所有任务 | 吞吐 +0–3%；尾部延迟/交互响应改善更大 | 中 |
| 系统层 | `vm.swappiness=100` + ZRAM(zstd) + 关 zswap | ✅ 仅内存吃紧时 | **0 或"量级差异"** | 中高（条件性） |
| 系统层 | `game-performance` 电源档 + amd_pstate/EPP | ✅ 单核睿频维持 | 台式 0–3%；**功耗受限机器显著** | 中 |
| 系统层 | I/O 调度器按设备分配 + dirty 参数 | ⚠️ 只影响加载/存档写入 | 小 | 中 |
| 运行时层 | Proton-CachyOS / FSR4 / Reflex / NTSync | ❌ 与这三款无关 | ≈ 0 | 高 |

**筛选规则**：只看「作用于游戏执行路径 = ✅」的行 → 候选池只剩**内核内存管理、内核调度、系统层内存/电源**。

---

## 3. 为什么招牌优化对游戏本体失效（核心反直觉）

1. **包仓库重编译的对象是发行版自己的包**（内核、glibc、Mesa、Proton、库）。游戏二进制来自 Steam / 厂商，CachyOS 不参与其构建。
2. **这三款都有原生 Linux 版** → 走原生版时连 Proton 都不在链路上，编译层覆盖面进一步缩小到"内核 + glibc + Mesa"。
3. **模拟循环在游戏自己的代码里**，由厂商用厂商的编译选项构建，v3/v4/LTO/PGO 一个都吃不到。
4. **仅存的间接路径**：glibc 的 `malloc`/`memcpy`（早已 IFUNC 运行时分派，增量很小）+ 内核自身的页回收/调度路径（亚百分比级）。

> 宣传口径里的"CPU 密集"指**负载类型**，不指**游戏**。招牌对"发行版自己的软件"有效（编译器、渲染、AI 推理），对"厂商预编译的游戏本体"基本无效。

---

## 4. 一手证据：开发者自己怎么说

### 4.1 群星 4.3「Cetus」开发日志（2026-02-06，官方）

同机（i9-14900K / 32GB / RTX 3060）、巨型星系、士官难度、同存档同种子，`-gamestatetimer` 记录"每年秒数"：

| 版本 | 开局 | 后期 |
|---|---|---|
| 3.14 | 30.52 秒/年 | 2269 年退化到 **44.63 秒/年** |
| **4.3** | **11.54 秒/年** | 到 2269 年才退化到 3.14 的**开局**速度 |

**≈ 2.6×**，全部来自游戏自身代码层：依赖跟踪减少 **CPU 等待**与"月度卡顿"、减小线程批处理粒度以分布到多核、**重用内存并减少更新中的分配/释放**、把触发器计算移到合适的脉冲、优化字符串函数。

### 4.2 三条推论

1. **游戏版本 > 一切发行版优化**（2.6× vs 个位数百分比）。
2. **群星不是纯单线程**，且瓶颈含"CPU 等待"与"内存分配抖动" → 印证内核调度/内存层是唯一有效的发行版抓手，但天花板由游戏代码决定。
3. **CK3 开发日志 #187（2025-10-15，Technical Lead Joel）**把性能作为专门主题 → 后期慢主因在游戏代码与存档规模。

> ⚠️ 官方测试用 **Windows** 机器且是**版本间**对比，不是发行版间对比。

---

## 5. 可复用操作

### 5.1 A/B 对照方法（判定"是否真有效"）

1. 固定存档 + 固定模拟区间；锁定游戏版本、Mod、画质、后台程序、电源接入状态。
2. 先用原策略跑基线，再用 `game-performance %command%` 复测。
3. 每状态 ≥3 次，比较**中位数**；同时记录 CPU 持续频率、温度、功耗，排除热降频/功耗墙。
4. **测模拟吞吐，不是帧率**：
   - 群星：启动参数 `-gamestatetimer` 生成 tick 时间日志（300 年约 30MB）
   - RimWorld：同存档同场景的 TPS / 推进速度
   - CK3：同存档同日期跨度、同游戏速度，比较墙钟时间
5. 差异小于多次运行的自然波动 → 不要为模拟速度切换内核调度器。

### 5.2 系统侧落地（任意发行版）

```bash
# THP：减少大堆内存的 TLB miss
echo 'defer+madvise' | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

# ZRAM 兜底（仅内存 < 存档工作集时才值得开）
sudo pacman -S zram-generator
printf '[zram0]\nzram-size = ram / 2\ncompression-algorithm = zstd\nswap-priority = 100\n' \
  | sudo tee /etc/systemd/zram-generator.conf
echo 'vm.swappiness = 100' | sudo tee /etc/sysctl.d/99-swap.conf

# 电源档：避免单核睿频被省电策略压住
powerprofilesctl set performance          # Fedora 用 tuned

# 调度延迟：sched-ext 可运行时切换，无需换内核
scxctl start --scheduler scx_lavd         # Arch: scx-scheds / openSUSE: scx / NixOS: services.scx.enable

# 跑原生 Linux 版，不要走 Proton（这三款都有原生版）
```

**BORE / BMQ 不在主线** → 必须换 `linux-cachyos` 内核或自编译补丁；这是 CachyOS 唯一无法在其他发行版"纯官方仓库"里复现的内核项。

**硬件优先级（比调系统更有效）**：X3D CPU（L3 容量）> 内存容量 > 内核/调度调优 > 换发行版。

---

## 6. 坑与反直觉

| 坑 | 说明 |
|---|---|
| "CPU 密集型游戏吃编译优化" | 营销口径，不是机制。编译器层碰不到游戏二进制。 |
| "收益在 1% low" | 对这三款错位：痛点是**吞吐**（TPS / 每年秒数），不是帧时间抖动。 |
| "4K 下优势消失" | 不适用——这三款在任何分辨率都 CPU 瓶颈。 |
| **`performance` 不会超频** | 它只改电源策略，不突破功耗/温度/硬件上限；热设计受限时还可能更快撞温度墙。 |
| **RT 内核不提升游戏性能** | CachyOS 官方 FAQ 明确：实时内核不会改善游戏性能，且可能因更多抢占而降低性能。 |
| **CPU 密集 ≠ 调度器受限** | 主线程已独占核心时，换调度器可能几乎不改变模拟速度。 |
| ZRAM 是"加速手段" | ❌ 压缩耗 CPU，内存充足时是**净负项**。它是"内存不够时的止损"。 |
| 换发行版能救后期 | ❌ 即使上 X3D，群星后期 1000 星仍会卡——游戏架构问题。 |
| 社区"Linux 比 Windows 快" | 多为 ProtonDB 单样本主观报告，无对照基准。 |
| 把游戏版本差异归功于 OS | 模拟算法、线程化、Mod 更新可能远大于发行版差异。 |

---

## 7. 未核实 / 存疑

| 项 | 说明 |
|---|---|
| 三款游戏中各优化项的实际提升幅度 | 缺少同机型、同存档、重复运行的 CachyOS A/B 数据 |
| BORE / EEVDF / SCX 对这三款游戏**模拟吞吐**的差异 | 缺少针对同一游戏工作负载的受控测试 |
| THP / MGLRU 在该场景的增益百分比；ZRAM 的 CPU 开销量化 | 机制成立，量级未标定 |
| RimWorld 5800X3D +30% | 贴吧/B站个人实测，单样本、未披露存档与 mod 清单 → 社区实证 |
| CK3"主核占用高 + 内存带宽压力" | 百度文库二手分析 → 推断，未找到一手 profiling |
| 各游戏当前版本/Mod 的 CPU 并行度与瓶颈线程分布 | 需按版本、存档、Mod 组合实际 profiling |

---

## 8. 参考来源

- CachyOS Kernel Wiki（调度器、1000Hz、内核变体、RT FAQ）：https://wiki.cachyos.org/features/kernel/
- CachyOS-Settings（`game-performance` 脚本）：https://github.com/CachyOS/CachyOS-Settings
- Why CachyOS?（性能包与调度器目标）：https://wiki.cachyos.org/cachyos_basic/why_cachyos/
- BORE 调度器 tunables：https://github.com/YuZyu9527/bore-scheduler
- linux-cachyos（内核补丁与 topic 分支）：https://github.com/CachyOS/linux-cachyos
- Paradox 官方 —《群星》4.3「Cetus」性能与线程改进开发日志（2026-02-06）：https://news.17173.com/content/02062026/070655049.shtml
- Paradox 官方 — CK3 Dev Diary #187: Performance & Optimization（2025-10-15）：https://store.steampowered.com/news/app/1158310/view/535490230242770974
- Phoronix — CachyOS 内核变体横评 / BORE 专项 / 三系统 99 项横评：https://www.phoronix.com/reviews/Operating+Systems
- 什么值得买 —《CachyOS 8月大版本解读：帧率暴涨20%有几分真》：https://post.smzdm.com/p/ad72697p/
- 百度贴吧 —《5800x3d提升环世界性能实测》：https://tieba.baidu.com/p/8093977756
- ProtonDB — Stellaris / RimWorld（CachyOS 用户报告）：https://www.protondb.com/app/281990 、https://www.protondb.com/app/294100

---

## 9. 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0 | 2026-10-16 | 初版。结论：若必须挑一项先测，选 `game-performance` 电源档 |
| **2.0** | 2026-10-16 | 合并四层优化×瓶颈匹配矩阵；补入"编译层不覆盖游戏二进制"机制、瓶颈画像、群星 4.3 官方 2.6× 一手数据、CK3 DD#187；将结论改为**分叉条件表**（功耗受限→电源档 / 内存吃紧→内存层 / 两者不成立→调度层）；补入硬件优先级与 A/B 测量方法 |

## 10. 关联文档

- `cachyos/cpu-bound-sim-games-optimization.md` / `.html`（本轮完整报告）
- `cachyos/gaming-optimization-deepdive.md`（四层优化清单 / BORE 参数表 / Phoronix 公平性）
- `cachyos/distro-performance-comparison.md`（六发行版横比与方法论）
- `cachyos/cachyos-vs-arch|fedora|opensuse|ubuntu2604|nixos2605.md`（五份一对一对比）
