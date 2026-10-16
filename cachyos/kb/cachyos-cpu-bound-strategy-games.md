---
id: cachyos-cpu-bound-strategy-games
title: CachyOS 对 CPU 密集型策略游戏的优化收益
tags:
  - cachyos
  - linux-gaming
  - cpu-bound
  - scheduler
  - simulation-games
created: 2026-10-16
updated: 2026-10-16
version: 1.0
status: draft
source: CachyOS 官方 Wiki/GitHub、游戏开发者公告、本次会话分析
confidence: 推断
---

## 一句话结论

对 RimWorld、Stellaris、Crusader Kings 3，若必须挑一项先测，选 CachyOS 的 `game-performance` 性能电源档；它只在原有电源策略限制了持续 CPU 频率时可能明显加快模拟，桌面机已稳定满频时收益可能接近零，公开资料没有证明它在这三款游戏中必然胜过其他 CachyOS 优化。

---

## 收益判断

| 优化项 | 对模拟速度的预期 | 对流畅度/响应的预期 | 判断 |
|---|---|---|---|
| `game-performance` / performance 电源档 | 若 CPU 受电源策略、笔记本功耗限制或频率响应限制，可能提高持续频率；否则差异小 | 可能降低负载期间的频率响应等待 | **首选 A/B 测试项；有条件的推断** |
| 默认 CachyOS EEVDF 调参 / BORE | 没有这三款游戏的可靠对照数据；一般不应假设能提高模拟吞吐 | 目标是交互响应、调度延迟与重负载下的流畅感 | **可能改善体感，不等于更多游戏日/秒；官方目标已核实** |
| CPU 架构优化包、LTO/PGO/BOLT | 游戏主程序通常是预编译发行物，不会因换发行版而重新编译；被优化的系统库等可能有次级收益 | 可能小幅影响部分系统组件 | **不应默认视为最大收益；机制推断** |
| 1000Hz tick / 实时内核 | 没有证据说明提高模拟吞吐 | 低延迟目标不等于更快；CachyOS 官方明确表示 RT 内核不提升游戏性能 | **不要为了游戏速度改用 RT 内核** |

### 按目标选择

- **想让游戏时间推进更快**：先比较 performance 电源档与原策略；重点看游戏内模拟速度，而非 GPU FPS。
- **想减少后台负载下的卡顿**：可测试默认 EEVDF 与 BORE，但用帧时间/卡顿指标判定，不以模拟吞吐代替。
- **想提升后期速度**：游戏版本、存档状态、Mod、CPU 单核持续性能与温度/功耗限制，可能比发行版调度器差异更关键。该判断对具体配置属于推断。

---

## 证据与边界

1. CachyOS 官方 `CachyOS-Settings` README 描述 `game-performance` 会在启动应用时通过 `powerprofilesctl` 切换到 `performance` 电源档；README 没有给出对上述三款游戏的提升百分比。
2. CachyOS Kernel 官方 Wiki 将默认内核定位为响应性调校，提供 BORE、EEVDF 等变体；官方 FAQ 明确说实时内核不会改善游戏性能，且可能因更多抢占而降低性能。
3. CachyOS 官方 `Why CachyOS?` 将 EEVDF 调优与 BORE 的目标描述为桌面响应性/交互性。这不能直接证明策略游戏的模拟吞吐更高。
4. CK3 开发者 2025-10-15 的性能日志，以及《群星》4.3 开发者性能测试，说明游戏版本自身的模拟优化是重要变量；换发行版前应锁定游戏版本、存档、设置和 Mod。
5. 截至 2026-10-16，未找到对 RimWorld、Stellaris、CK3 使用相同存档/场景进行 CachyOS 优化项逐项对照的高质量公开基准。因此无法给出普适百分比或无条件唯一冠军。

---

## 可复用操作

1. 选一个固定存档和固定模拟区间；固定游戏版本、Mod、画质、后台程序与电源接入状态。
2. 先用原电源策略跑基线，再用 Steam 启动参数 `game-performance %command%` 复测。
3. 每种状态至少跑 3 次，比较中位数；同时记录 CPU 持续频率、温度与功耗，排除热降频或功耗墙。
4. 记录游戏模拟吞吐，而非只看帧率：
   - Stellaris 可用启动参数 `-gamestatetimer` 生成 tick 时间日志；日志可能很大。
   - RimWorld 记录相同存档与场景下的 TPS/推进速度。
   - CK3 使用相同存档、日期跨度和游戏速度，比较推进该跨度所需的墙钟时间。
5. 如果差异小于多次运行的自然波动，不要为这些游戏仅为追求模拟速度切换内核调度器。

---

## 坑与反直觉

- **performance 不会超频**：它改变的是系统电源策略，不会突破 CPU 的功耗、温度或硬件频率上限；热设计受限时还可能更快触及温度墙。
- **CPU 密集不等于调度器受限**：主线程已独占核心时，换调度器可能几乎不改变模拟速度。
- **低帧/响应性与游戏时间推进速度是不同指标**：BORE/EEVDF 的响应改善不能直接换算成更多 tick 或更快的日历时间。
- **不要把游戏版本差异归功于操作系统**：模拟算法、线程化和 Mod 更新可能远大于发行版差异。

---

## 未核实 / 存疑

| 项 | 说明 |
|---|---|
| 三款游戏中 performance 电源档的实际提升幅度 | 缺少同机型、同存档、重复运行的 CachyOS A/B 数据；受 CPU、固件、电源档、温度和游戏版本影响。 |
| BORE、默认 EEVDF 与其他调度器对这三款游戏的模拟吞吐差异 | 缺少针对同一游戏工作负载的受控测试。 |
| 各游戏当前版本/Mod 对 CPU 并行度和瓶颈线程的具体分布 | 需要按版本、存档和 Mod 组合实际 profiling。 |

---

## 参考来源

- CachyOS Kernel Wiki（调度器、1000Hz、内核变体及 RT FAQ）：https://wiki.cachyos.org/features/kernel/ （访问：2026-10-16）
- CachyOS-Settings（`game-performance` 脚本用途）：https://github.com/CachyOS/CachyOS-Settings （访问：2026-10-16）
- Why CachyOS?（性能包与调度器目标）：https://wiki.cachyos.org/cachyos_basic/why_cachyos/ （页面标注更新：2026-01-27）
- Crusader Kings III Dev Diary 187 — Performance & Optimization（2025-10-15）：https://store.steampowered.com/news/app/1158310/view/535490230242770974
- 《群星》4.3 性能与线程改进开发日志（2026-02-06，中文转载）：https://news.17173.com/content/02062026/070655049.shtml
