# 知识库索引（cachyos 项目）

| slug | 标题 | tags | version | updated | status |
|---|---|---|---|---|---|
| [`cachyos-cpu-bound-strategy-games`](./cachyos-cpu-bound-strategy-games.md) | CachyOS 对 CPU 密集型策略/模拟游戏的优化收益（RimWorld / 群星 / CK3，**原生**） | cachyos, linux-gaming, cpu-bound, scheduler, simulation-games, memory-management, kernel | 2.0 | 2026-10-16 | stable |
| [`cachyos-proton-games-optimization`](./cachyos-proton-games-optimization.md) | CachyOS 对 **Proton 运行**游戏的优化收益（2077 / Palworld / Soulmask；翻译层 + NTSync）＋ **部署变体**（官方 `x86_64_v3` tarball 可脱离 CachyOS 使用）＋ **Flatpak 影响**（图形栈被 runtime 替换，`--device=all` 使 ntsync 可用） | cachyos, linux-gaming, proton, dxvk, vkd3d, ntsync, flatpak, cpu-bound | 2.0 | 2026-10-16 | stable |

> 两篇构成一组对照：**原生游戏 → 冠军是内核内存/调度层；Proton 游戏 → 冠军是翻译层 + 运行时栈**。共同点是收益量级都在个位数百分比。
