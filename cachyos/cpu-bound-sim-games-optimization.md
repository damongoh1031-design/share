# CachyOS 优化对 CPU 密集型模拟游戏的收益排序（RimWorld / 群星 / CK3）

- **调研日期**：2026-10-16
- **聚焦问题**：以 CPU 密集的游戏（RimWorld、群星 Stellaris、CK3）而言，CachyOS 做的哪一项优化收益最大？
- **承接**：本系列前八轮（`report.*` / `gaming-optimization-deepdive.*` / `distro-performance-comparison.*` / 五份一对一对比）
- **一句话结论**：对这三款游戏，CachyOS 的**头牌优化（全仓库 x86-64-v3/v4 + LTO/PGO/BOLT 重编译）几乎零收益**——游戏本体是厂商预编译的二进制，发行版重编译碰不到它。**收益最大的那一项是内核的内存管理 + 调度延迟层**（MGLRU / THP `defer+madvise` / `vm.swappiness=100`+ZRAM / BORE-EEVDF 调参 / 1000Hz / PREEMPT_DYNAMIC），量级为**个位数百分比**；**唯一能产生"量级差异"的场景是内存吃紧时避免磁盘 swap**。

---

## 一、先定瓶颈：这三款游戏到底吃什么

| 游戏 | 引擎 | 主瓶颈 | 后期内存足迹 | 对缓存/内存延迟的敏感度 |
|---|---|---|---|---|
| **RimWorld** | Unity（Mono） | **单线程 TPS**，主线程单核 100% | 轻度 mod 4–8 GB；**重度 mod 可达 8–30 GB** | **极高**（社区实测 5800X3D vs 5600X 约 +30%，单样本） |
| **群星 Stellaris** | Clausewitz | **单核为主** + 少量并行作业 | 1000 星后期 8–16 GB | 高（社区共识：换 X3D 有明显改善，但**后期仍会卡**） |
| **CK3** | Clausewitz | **主核（CPU0）长期高占用** + 内存带宽压力 | 后期 6–10 GB | 高 |

**四款共同点（这是全部分析的地基）**：

1. **"后期慢" = 单线程吞吐不足**。推进速度由一条主线程的 IPC × 频率决定。
2. **指针追逐 + 大工作集** → 对 **L3 容量**与**内存延迟**高度敏感（这正是 X3D 在这类游戏上收益大的原因）。
3. **长会话、内存足迹随时间单调增长** → 内存压力是常态而非例外（RimWorld 重度 mod 尤其）。
4. **显卡几乎不参与**——这三款在 1080p 和 4K 下都是 CPU 瓶颈。

> **推论**：能真正加速它们的只有四件事——**单核 IPC × 频率**、**内存延迟/带宽**、**L3 容量**、**RAM 容量**。发行版只能碰到其中两项的一半。这是理解"为什么换发行版收益有限"的关键。

---

## 二、CachyOS 四层优化 × 瓶颈匹配矩阵

| 层 | 具体项 | 是否作用于**游戏自身执行路径** | 对这三款游戏的预期收益 | 置信度 |
|---|---|---|---|---|
| 编译层 | 全仓库 x86-64-v3/v4/znver4 + LTO/PGO/BOLT/AutoFDO | ❌ **不覆盖游戏二进制**（只覆盖内核/glibc/Mesa/Proton/库） | **≈ 0**（经 glibc 与内核路径间接 < 1–2%） | **高** |
| 内核层 | MGLRU + "Cachy Sauce" MM 调参 + THP(`defer+madvise`) | ✅ 作用于内存回收与 TLB | **+1–5%**（内存压力越大越高） | 中 |
| 内核层 | 调度器（BORE / EEVDF 调参 / SCX / sched-cluster）+ 1000Hz tick + PREEMPT_DYNAMIC + POC Selector | ✅ 作用于所有任务 | 吞吐 **+0–3%**；**尾部延迟 / UI 响应改善更明显** | 中 |
| 系统层 | `vm.swappiness=100` + ZRAM(zstd, priority 100) + 关闭 zswap | ✅ 仅在内存吃紧时 | **0 或"量级差异"**（避免磁盘 swap） | 中高（**条件性**） |
| 系统层 | `game-performance` 切 performance 电源档 + amd_pstate/EPP | ✅ 决定单核睿频能否维持 | 台式机 **0–3%**；**笔记本/掌机显著**（功耗受限时） | 中 |
| 系统层 | I/O 调度器按设备分配（NVMe→kyber / SATA SSD→mq-deadline / HDD→bfq）+ dirty 参数 | ⚠️ 只影响加载与存档写入 | 小（不改善稳态 tick） | 中 |
| 运行时层 | Proton-CachyOS / FSR4 / Reflex / NTSync / OptiScaler | ❌ 与这三款无关 | **≈ 0** | **高** |

**读法**：把"✅ 作用于游戏执行路径"这一列筛出来，只剩**内核内存管理、内核调度、系统层内存/电源**三类。这就是全部候选池。

---

## 三、冠军：内核「内存管理 + 调度延迟」这一层

### 3.1 为什么是它

三款游戏的痛点有两类，恰好各自对应这一层的一半：

| 痛点 | 表现 | 对应优化 | 机制 |
|---|---|---|---|
| **后期 tick 变慢** | 回合/天推进时间随存档膨胀而拉长 | THP(`defer+madvise`) + MGLRU + MM 调参 | 大堆内存下减少 **TLB miss**；改进页回收，降低分配/回收路径的停顿 |
| **后期卡顿瞬间 / UI 迟滞** | 画面一顿一顿、点界面不跟手 | BORE / EEVDF 调参 + 1000Hz tick + PREEMPT_DYNAMIC + POC Selector | 缩短调度与唤醒延迟，让前台/交互线程优先拿到 CPU |
| **内存吃紧**（重度 mod） | 硬盘灯狂闪、几秒一卡 | `vm.swappiness=100` + ZRAM | 用**压缩内存**替代**磁盘 swap** |

### 3.2 量级预期（必须诚实）

- **稳态 tick 吞吐**：CachyOS 相对通用发行版的优势，属于**个位数百分比**量级。前八轮的校准结论在此同样成立——发行版间差异远小于硬件换代或内核/驱动版本差异。
- **卡顿瞬间（尾部延迟）**：改善幅度**大于**吞吐改善。这与社区观测到的"涨得最猛的是 1% low，不是平均帧"完全一致。
- **⚠️ 但对这三款游戏，"1% low 改善"不等于"痛点改善"**：它们的痛点是 **TPS 不达标（吞吐）**，不是帧时间抖动。所以调度层的收益被**打折**。

### 3.3 唯一能产生「量级差异」的单项

**`vm.swappiness=100` + ZRAM** —— 且**只在物理内存小于存档工作集时**生效。

- 机制：把匿名页留在**压缩后的内存**里，而不是写到磁盘。磁盘 swap 的延迟是微秒→毫秒级的跃迁，一旦触发，游戏从"慢"变成"卡死"。
- **反直觉的代价**：ZRAM 的压缩/解压**消耗 CPU**。对 CPU 密集型游戏，这是一个**真实的负项**。内存充足时依赖 ZRAM 反而可能变慢。
- **正确排序**：**加内存 > ZRAM > 磁盘 swap**。ZRAM 是"内存不够时的止损"，不是"加速手段"。

---

## 四、最反直觉的一点：头牌优化为什么在这三款游戏上失效

CachyOS 的宣传口径是"编译优化减少 CPU 空转 → 收益落在吃 CPU 的地方"，因此**推不出**"CPU 密集型游戏收益最大"。原因：

1. **包仓库重编译的对象是发行版自己的包**（内核、glibc、Mesa、Proton、各类库）。**游戏二进制来自 Steam / 厂商，CachyOS 不参与其构建。**
2. **这三款都有原生 Linux 版**（RimWorld、Stellaris、CK3 均提供）。走原生版时**连 Proton 都不在链路上**，编译层的覆盖面进一步缩小到"内核 + glibc + Mesa"。
3. **模拟循环写在游戏自己的代码里**，而那段代码是厂商用厂商的编译选项构建的，v3/v4/LTO/PGO 一个都吃不到。
4. **唯一剩下的间接路径**：
   - `glibc` 的 `malloc` / `memcpy` / 字符串函数——但 glibc 早已用 **IFUNC 运行时分派**（自动选 AVX2/AVX-512 实现），重编译带来的增量很小；
   - **内核自身**的页回收与调度代码路径——被 v3/v4 重编译，收益亚百分比级。

> **一句话**：CachyOS 的招牌对"发行版自己的软件"有效（编译器、渲染、AI 推理等负载，这正是 Phoronix 99 项里它能赢 51 项的地方），但对"厂商预编译的游戏本体"基本无效。**宣传口径里的"CPU 密集"指的是"负载类型"，不是"游戏"**。

---

## 五、可复用操作：在任意发行版上复现这几项

```bash
# 1) 内存管理：THP 设为 defer+madvise（减少大堆的 TLB miss）
echo 'defer+madvise' | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

# 2) 交换策略：ZRAM 兜底（仅在内存 < 存档工作集时才值得开）
#    Arch/CachyOS: zram-generator；Fedora 默认已开；Ubuntu: systemd-zram-generator
sudo pacman -S zram-generator
printf '[zram0]\nzram-size = ram / 2\ncompression-algorithm = zstd\nswap-priority = 100\n' \
  | sudo tee /etc/systemd/zram-generator.conf
echo 'vm.swappiness = 100' | sudo tee /etc/sysctl.d/99-swap.conf

# 3) 电源档：避免单核睿频被省电策略压住
sudo pacman -S power-profiles-daemon   # 或 tuned（Fedora）
powerprofilesctl set performance

# 4) 调度延迟：EEVDF 可运行时调参（无需换内核）
sysctl kernel.sched_base_slice_ns       # 查看
# 或装 sched-ext（Arch: scx-scheds；openSUSE: scx；NixOS: services.scx.enable）
scxctl start --scheduler scx_lavd

# 5) 把游戏本体跑原生 Linux 版，不要走 Proton（这三款都有原生版）
```

> **BORE / BMQ 不在主线**，必须换 `linux-cachyos` 内核（或自编译补丁）。**这是 CachyOS 唯一无法在其他发行版"纯官方仓库"里复现的内核项**（详见前八轮结论）。

---

## 六、坑与反直觉

1. **"CPU 密集型游戏吃编译优化"是营销口径，不是机制。** 机制上编译器层碰不到游戏二进制。
2. **"收益在 1% low"这条对这三款游戏不成立（作为卖点）。** 它们的痛点是吞吐（TPS / 回合推进速度），不是帧时间抖动。拿 1% low 的改善去说服模拟游戏玩家，是错位的。
3. **"4K 下优势消失"对这三款游戏无意义**——它们在任何分辨率都是 CPU 瓶颈，所以"CachyOS 在低分辨率才有效"这条边界条件不适用于本问题。
4. **换发行版的收益，小于升级硬件。** 对这三款游戏，真正的加速手段排序是：**X3D CPU（L3 容量） > 内存容量 > 内核/调度调优 > 换发行版**。但注意：**即使上 X3D，群星后期 1000 星仍会卡**——这是游戏架构问题，发行版救不了。
5. **ZRAM 有 CPU 开销。** 内存充足时它是净负项。
6. **社区"群星/CK3 在 Linux 上比 Windows 快"的说法**，多为 ProtonDB 单样本主观报告，**无对照基准**，只能作为方向性参考。

---

## 七、未核实 / 存疑

- **没有**任何 CachyOS 针对这三款游戏（或任何模拟类游戏）的**公开对照基准**。本报告的收益量级为**基于瓶颈画像的结构性推断**，非实测。
- **BORE 对模拟类游戏吞吐的具体影响**：无公开数据。Phoronix 有 BORE 内核专项评测，但内容不是游戏帧率/模拟吞吐。
- **RimWorld 5800X3D +30%**：来自百度贴吧/B站个人实测，单样本、无重复、未披露存档与 mod 清单 → **社区实证**，非已核实。
- **CK3"主核占用高 + 内存带宽压力"**：来自百度文库二手分析 → **推断**，未找到一手 profiling。
- **THP/MGLRU 对模拟类游戏的具体增益百分比**：无该场景实测数据，机制成立但量级未标定。
- **ZRAM 在游戏场景下的 CPU 开销量化**：无实测数据。

---

## 八、总结表

| 问题 | 回答 |
|---|---|
| 这三款游戏的瓶颈是什么？ | 单线程吞吐 + 内存延迟（指针追逐、大工作集）+ 后期内存足迹膨胀；显卡不参与 |
| CachyOS 哪一项收益最大？ | **内核内存管理 + 调度延迟层**（MGLRU / THP / swappiness+ZRAM / BORE-EEVDF 调参 / 1000Hz / PREEMPT_DYNAMIC） |
| 预期量级？ | 吞吐**个位数百分比**；尾部延迟改善更大但对这三款游戏价值打折 |
| 唯一能"量级"改变的是哪项？ | `vm.swappiness=100` + ZRAM——**且仅在内存吃紧时**；内存充足时它是净负项 |
| 头牌优化（v3/v4 + LTO/PGO/BOLT）有效吗？ | **基本无效**。游戏二进制不由发行版重编译，且三款均有原生 Linux 版 |
| 运行时层（Proton-CachyOS / FSR4 / Reflex）呢？ | **无关**。三款有原生版；FSR4/Reflex 是 GPU 特性 |
| 真正的加速手段排序？ | **X3D CPU > 内存容量 > 内核/调度调优 > 换发行版** |
| 证据强度？ | 机制清晰、方向可靠，但**无针对这三款游戏的公开对照基准**；量级为结构性推断 |

---

## 九、一手证据：开发者自己怎么说（最硬的校准）

这一节把上面的推断钉在**第一方数据**上——因为它给出了所有发行版优化的**参照系**。

### 9.1 群星 4.3「Cetus」开发日志（2026-02-06，官方）

同一台机器（**i9-14900K / 32GB / RTX 3060**）、巨型星系、士官难度、同存档同随机种子，用 `-gamestatetimer` 记录"每年秒数"：

| 版本 | 开局速度 | 后期速度 | 说明 |
|---|---|---|---|
| 3.14 | 30.52 秒/年 | **2269 年退化到 44.63 秒/年** | 基线 |
| **4.3** | **11.54 秒/年**（快于每月 1 秒） | 直到 2269 年才退化到 3.14 的**开局**速度 | **约 2.6×** |

**他们靠什么拿到的**（全部是游戏自身代码层）：
- 新增**依赖跟踪**，减少更新时的 **CPU 等待时间**、减少"月度卡顿"
- **减小线程批处理粒度**，让 CPU 需求不均的对象更好分布到多核
- **重用内存、减少更新中的分配/释放**（"优化了警报管理器中的内存分配"）
- 把触发器依赖计算**移到合适的脉冲**（微刻/日刻/周刻/月刻/年刻），减少触发器评估次数
- 优化字符串相关函数、舰队图标逻辑

### 9.2 三条直接推论

1. **游戏版本 > 一切发行版优化。** 3.14 → 4.3 是 **2.6 倍**；而 CachyOS 相对通用发行版在这类负载上的差异是**个位数百分比**。换发行版前先看游戏版本是不是最新的。
2. **群星不是纯单线程，且瓶颈含"CPU 等待"与"内存分配抖动"。** 这**印证**了内核调度/内存层是唯一有效的发行版抓手（对应"月度卡顿"），但也说明**天花板由游戏代码决定**。
3. **CK3 开发日志 #187（2025-10-15，Technical Lead Joel）**同样把性能作为专门主题（随"溥天之下"扩展发布），基调是"新增功能带来的模拟负载需要专项优化"——即**后期慢的主因在游戏代码与存档规模**，不在操作系统。

> ⚠️ 本节两条一手来源的方法学提醒：官方测试用的是 **Windows** 机器，且是**版本间对比**（不是发行版间对比）。它证明的是"游戏自身优化量级"，不是"Linux 比 Windows 快多少"。

---

## 十、与前序 KB 结论的对齐（重要）

仓库中已有前序会话产出的 KB 文档 `cachyos/kb/cachyos-cpu-bound-strategy-games.md`（v1.0，结论：*"若必须挑一项先测，选 `game-performance` 性能电源档"*）。本报告与它**不矛盾，而是给出分叉条件**：

| 机器条件 | 冠军项 | 量级 |
|---|---|---|
| **功耗受限**（笔记本 / 掌机 / 小机箱 / 温度墙） | **`game-performance` 电源档 / 单核睿频维持** | 可显著 |
| **内存吃紧**（重度 mod 存档 / RAM < 工作集） | **`vm.swappiness=100` + ZRAM + THP/MGLRU** | 0 或**量级** |
| **两者都不成立**（台式机 + 内存充足） | 只剩调度延迟层 | 个位数百分比 |

> 前序文档的"电源档"结论在**功耗受限机器**上成立；本报告补充了**内存吃紧**这一分支，并给出"两者都不成立时收益退化为个位数"的上界。两版合并后写入 KB v2.0。

---

## 参考来源

- [CachyOS Kernel — 官方 Wiki（内核特性、变体、tick rate、AutoFDO、补丁）](https://wiki.cachyos.org/features/kernel)
- [Why CachyOS? — 官方 Wiki（EEVDF tunables、BORE、仓库）](https://wiki.cachyos.org/cachyos_basic/why_cachyos)
- [CachyOS-Settings — GitHub（sysctl / udev / systemd / NVIDIA 模块参数 / game-performance）](https://github.com/CachyOS/CachyOS-Settings)
- [BORE (Burst-Oriented Response Enhancer) Scheduler — GitHub（完整 tunables 与默认值）](https://github.com/YuZyu9527/bore-scheduler)
- [linux-cachyos — GitHub（内核补丁与 topic 分支，含 sched-cluster / POC selector）](https://github.com/CachyOS/linux-cachyos)
- [CachyOS 官网（x86-64-v3/v4、LTO/PGO/BOLT、调度器选项）](https://cachyos.org/)
- [什么值得买 —《CachyOS 8月大版本解读：帧率暴涨20%有几分真》（三项边界条件分析）](https://post.smzdm.com/p/ad72697p/)
- [百度贴吧 —《5800x3d提升环世界性能实测，大三缓真的有用吗?》](https://tieba.baidu.com/p/8093977756)
- [B站专栏 —《锐龙5800X3D，96MB三缓的性能加成》（含 RimWorld 存档实测）](https://www.bilibili.com/read/mobile?id=17470155)
- [百度贴吧 —《群星后期卡顿根源：单核运算与人口计算问题》](https://tieba.baidu.com/p/7989432387)
- [百度贴吧 —《9800X3D 是这游戏的解决方案吗?》（群星 9800X3D 后期仍卡）](https://tieba.baidu.com/p/9554806755)
- [百度文库 —《CK3 是多核还是单核？十字军之王3性能优化与CPU选择全解析》](https://wenku.baidu.com/view/f4b6527b1d2e453610661ed9ad51f01dc28157bb.html)
- [ProtonDB — Stellaris（CachyOS 用户报告）](https://www.protondb.com/app/281990)
- [ProtonDB — RimWorld（CachyOS 用户报告）](https://www.protondb.com/app/294100)
- [Phoronix — CachyOS 内核变体横评 / BORE 专项 / 三系统 99 项横评](https://www.phoronix.com/reviews/Operating+Systems)
- [Paradox 官方 —《群星》4.3「Cetus」性能优化与线程改进开发日志（2026-02-06）](https://news.17173.com/content/02062026/070655049.shtml)
- [Paradox 官方 — Crusader Kings III Dev Diary #187: Performance & Optimization（2025-10-15，Steam）](https://store.steampowered.com/news/app/1158310/view/535490230242770974)

> **来源质量说明**：官方 Wiki / GitHub / Phoronix 为一手来源；什么值得买做了边界条件分析，可信度较高；贴吧、B站、百度文库、ProtonDB 为社区来源，**本报告已逐条标注其强度**（社区实证 / 推断 / 单样本主观）。本报告的核心结论（头牌优化对游戏本体无效、冠军是内存+调度层）为**结构性推断**，机制明确但缺该场景的对照实测。
