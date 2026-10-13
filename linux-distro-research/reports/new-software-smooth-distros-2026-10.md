# 不选纯滚动发行版：如何拿到「新软件（滞后 ≤1 个月）+ 版本过渡平滑」

**调研日期**：2026-10-12
**方法**：3 个并行研究子代理（Fedora 系 / Debian-Ubuntu 系 / 镜像式与量化方法论）+ 主调研员对 Fedora Mesa 例外与 Fedora 45 日期二次核实
**证据标注**：`[核实]` = 官方文档/Wiki/工单/权威媒体；`[社区]` = 论坛/用户共识

---

## 0. 结论先行

### 先拆掉这个问题里的陷阱

**「滞后 ≤1 个月」不是一个数字，是每个组件各自的数字。** 没有任何发行版能对所有组件都做到 ≤1 个月——内核可以滞后 3 天，而同一个系统里的编译器可能滞后 6 个月。**所以真正的问题是：你在意哪个组件的滞后。**

| 组件 | 谁做得到 ≤1 个月 |
|---|---|
| 内核 | Fedora（数天）、Manjaro（约 2 周）、Aeon/Kalpa（每日） |
| Mesa（游戏关键） | Fedora（**有永久例外可 rebase 大版本**）、Manjaro、Aeon/Kalpa |
| 桌面大版本（GNOME/Plasma） | **只有近滚动/镜像式能做到**。所有 6 个月发布制的都滞后约 6 个月 |
| 编译器 / Python 等语言运行时 | **基本都做不到**，除非用滚动或镜像式 |
| 浏览器 | 大部分发行版都能（Firefox/Chrome 走独立更新通道） |

### 排名（结论）

| 排名 | 方案 | 一句话 |
|---|---|---|
| **1** | **Fedora Workstation / Fedora KDE** | 最平衡。内核 + Mesa 有**永久例外**可在稳定版内 rebase 大版本；代价是桌面大版本和语言运行时滞后约 6 个月 |
| **2** | **Fedora Atomic（Silverblue/Kinoite）+ Universal Blue（Bazzite/Bluefin/Aurora）** | **最平滑**。镜像式原子更新 + 一键回滚 + 每日重建 |
| **3** | **openSUSE Aeon / Kalpa** | 系统层新鲜度 ≈ Tumbleweed（每日快照）+ health-checker 自动回滚。⚠️ 但仍是 beta / alpha |
| **4** | **Manjaro stable** | 唯一「真滚动 + 官方 2 周延迟缓冲」，满足 ≤1 个月 |
| **5** | **Debian testing (forky)** | 正常期约 10 天，⚠️ 但**冻结期退化到数月**，且安全更新不受及时支持 |
| **6** | **任意发行版 + Flatpak / distrobox / Nix** | **最被低估、零取舍**。系统层求稳，应用层求新 |

### 如果只能记一句话

**不想换发行版，就用「稳定基底 + 滚动应用层」（Flatpak + distrobox + Nix）——这是唯一不需要取舍的方案。** 要一个发行版解决，选 **Fedora**。

---

## 1. 四种结构性方案（先看框架）

| 方案 | 代表 | 新鲜度 | 平滑度 | 可回滚 |
|---|---|---|---|---|
| **A. 6 个月发布 + 版本内 rebase 关键组件** | Fedora | 中高 | 高 | 中 |
| **B. 镜像式原子更新** | Silverblue / Aeon / Bazzite | 高 | 高 | **最高** |
| **C. 近滚动 + 延迟** | Debian testing / Manjaro | 中高 | 中 | 低 |
| **D. 稳定基底 + 滚动应用层** | Flatpak / distrobox / Nix / KDE neon | 应用层高、系统层低 | 高 | 视底层 |

**最佳组合是 B + D**：用镜像式原子基底保证平滑与可回滚，用 Flatpak/distrobox 提供滚动应用新鲜度。openSUSE Aeon 正是这个模型的代表。

---

## 2. 方案 A：Fedora —— 最平衡的选择

### 2.1 版本与时间表

| 项目 | 事实 |
|---|---|
| 当前稳定版 | **Fedora 44**（2026-04-21 GA，搭载 GNOME 50）`[核实]` |
| 下一版 | **Fedora 45 GA 目标 2026-10-20**（Final Freeze 已于 2026-10-06 完成）`[核实]` |
| 节奏 | 每年 4 月 / 10 月第三周二（约 6 个月）`[核实]` |
| 生命周期 | 约 **13 个月**（Release N 支持到 N+2 发布后 4 周）；**无 LTS** `[核实]` |

### 2.2 关键：稳定版内会不会推新版本软件？

这是 Fedora 能不能满足「≤1 个月」的核心。答案是**分组件**：

| 组件 | 稳定版内是否 rebase 大版本 | 滞后 |
|---|---|---|
| **内核** | ✅ **会**。跟随上游 stable 分支持续 rebase，有**永久例外**（官方原文："We currently have a permanent exception for the Linux kernel"）`[核实]` | **数天** |
| **Mesa** | ✅ **会**。**2026-04-07 FESCo 正式授予永久 updates 例外**（ticket #3584），新 Mesa 大版本可作为更新推到稳定版。Phoronix 原文：与内核「same treatment」`[核实]` | 数周内 |
| **GNOME / Plasma 大版本** | ❌ **不会**。只给点版本，大版本随新 Fedora 发布 `[核实]` | **约 6 个月** |
| **编译器 / Python / 大型运行时** | ❌ **不会**。重大工具链更新必须在 Rawhide 落地 `[核实]` | **约 6 个月** |

**Mesa 永久例外为什么关键**：Mesa 直接决定 Linux 上的游戏性能与新 GPU 支持。Fedora 是**唯一一个既有 6 个月发布制的稳定性、又能在版本内升 Mesa 大版本的发行版**。

### 2.3 Bodhi 更新门槛

Fedora 每个 release 设 `mandatory_days_in_testing`（普通包）与 `critpath.mandatory_days_in_testing`（关键路径）+ `min_karma`。满足任一阈值即可推 stable。`[核实]`

### 2.4 升级平滑度

- `dnf system-upgrade`（离线升级），**支持跳版本**（N → N+2 仍能持续获得更新）`[核实]`
- 每 6 个月要升一次，是这套方案的主要摩擦点

### 2.5 Fedora Rawhide

- 滚动开发树，**每日更新**，持续 rebase 到最新上游 `[核实]`
- `[社区]` 不适合日常使用

---

## 3. 方案 B：Fedora Atomic + Universal Blue —— 最平滑

| 项目 | 事实 |
|---|---|
| 更新模型 | `rpm-ostree upgrade`：镜像式、后台下载、**原子**应用、重启生效 `[核实]` |
| 回滚 | `rpm-ostree rollback`（永久）；启动菜单选旧部署（临时）；**默认保留 2 个部署**，可 `ostree admin pin` 固定 `[核实]` |
| ⚠️ 跳版本 | **不支持**。官方原文："Skipping major releases is currently untested and is thus not supported" `[核实]` |
| 软件新鲜度 | 与 Fedora 主仓库**同步**，故同样受 Fedora 政策约束（内核/Mesa 新，GNOME/Plasma 大版本滞后约 6 个月）`[核实]` |
| 已知限制 | `/usr` 只读；rpm 覆盖（layering）削弱原子性；`/boot` 空间需注意 `[核实]` |

### Universal Blue 系（Bazzite / Bluefin / Aurora）

| 项目 | 事实 |
|---|---|
| 与 Fedora 关系 | 基于 Fedora Atomic Desktops 的 **OCI 镜像**，再叠加增强 `[核实]` |
| 重建频率 | **Bazzite 每日检查并安装更新**（idle 时自动装）；**Bluefin 提供 stable-daily（每日）/ stable（每周）/ gts（最长稳定）三种标签** `[核实]` |
| Bazzite 的游戏优化 | 集成较新内核、Mesa、**Proton / Gamescope**（SteamOS 风格）`[核实]` |
| 用户规模 | `[无数据]` 未找到权威公开数字 |

**取舍**：Atomic 在**平滑度**上最佳（原子 + 回滚 + 每日重建），但**底层包源仍受 Fedora 政策约束**——所以桌面大版本滞后的问题依然存在。

---

## 4. 方案 B 的变体：openSUSE Aeon / Kalpa

| 项目 | 事实 |
|---|---|
| 状态 | **Aeon（GNOME）= beta**；**Kalpa（KDE）= alpha**（官方门户标注）`[核实]` |
| 更新频率 | `transactional-update.timer` **每日 00:00–02:00** 运行；写入新 btrfs 快照，重启生效 `[核实]` |
| 基底 | 即 Tumbleweed，**跟随每日 snapshot** → 系统层新鲜度 ≈ Tumbleweed `[核实]` |
| **自动回滚** | `health-checker` 启动时检查关键服务。systemd-boot / grub2-bls 下首次启动失败按 `/etc/kernel/tries` 重试，仍失败则标记该 entry 不可用并启动下一个；**legacy grub2 下直接回滚到上次已知可用快照** `[核实]` |
| 软件安装优先级 | **Flatpak → 用户 Distrobox → root Distrobox → 本地二进制 → transactional-update**；官方明确 `transactional-update pkg install` **"不支持，改了就不给支持"** `[核实]` |
| 官方定位 | "你不用操心的桌面 OS"；"**Resilient: automatically rolls back to its last working state**" `[核实]` |

**这套模型的意义**：**系统库新鲜度 ≈ Tumbleweed（每日快照）**，**应用新鲜度由 Flathub 决定（通常很新）**——两头都新，且自动回滚。

**代价**：⚠️ **Aeon 是 beta、Kalpa 是 alpha**，不能当生产级稳定方案。

---

## 5. 方案 C：近滚动 + 延迟

### 5.1 Manjaro stable（唯一「真滚动 + 官方延迟」）

- 官方 Wiki 原文：stable 分支的包"**经过约两周（roughly a couple of weeks）由 Unstable/Testing 用户测试**"才进入 stable `[核实]`
- **满足 ≤1 个月**，且延迟本身就是缓冲 → 比 Arch 平滑
- ⚠️ `[社区]` 争议：AUR 与延迟导致部分依赖错位

### 5.2 Debian testing（当前代号 **forky** = Debian 14）

| 项目 | 事实 |
|---|---|
| 迁移延迟 | 包须在 unstable 停留 **10 / 5 / 2 天**（视 upload urgency），且无 RC bug、各架构编译完成、依赖可满足 `[核实]` |
| 是否滚动 | **否**（半滚动）。由脚本自动从 sid 生成 `[核实]` |
| ⚠️ 冻结期 | 分 transition / soft / hard / full 多阶段，发布前**数月**进入；冻结期 testing 几乎停滞，**软件可落后上游数月** `[核实]` |
| ⚠️ 安全更新 | testing **不受安全团队及时支持**，官方建议安全优先者切回 stable `[核实]` |
| 结论 | **正常期满足 ≤1 个月，全年不满足** |

---

## 6. 明确不满足的选项（避坑）

| 发行版 | 为什么不行 |
|---|---|
| **Ubuntu 过渡版**（26.10 "Stonking Stingray"，2026-10-15） | **版本内不跨大版本 rebase Mesa**（26.04 锁 Mesa 26.0.x，要 26.2 必须升 26.10）→ 滞后可达 5 个月。内核走 HWE 栈，滞后约 1 个周期 `[核实]` |
| **KDE neon** | Ubuntu **24.04 LTS** 基底 + 最新 KDE。**只有 KDE 生态新**（Plasma 6.7.4 发布即打包），Mesa / 内核 / GNOME 库等**约 2 年旧** `[核实]` |
| **Linux Mint** | 最保守（Ubuntu LTS + Cinnamon），滞后可达 2 年 `[核实]` |
| **Pop!_OS** | 跟随 LTS，只有自研 COSMIC 桌面新 `[核实]` |
| **Clear Linux（Intel）** | ⚠️ **2025-07-18 已停止开发**，不要选 `[核实]` |
| **Chakra** | 半滚动但基本停滞 `[核实]` |

---

## 7. 方案 D：稳定基底 + 滚动应用层（最被低估）

这是**唯一零取舍**的方案——它把「应用新鲜度」和「系统稳定性」解耦：

| 工具 | 作用 | 新鲜度 |
|---|---|---|
| **Flatpak** | 应用独立于发行版打包与更新 | 通常很新（Flathub 跟进上游） |
| **Distrobox / Toolbx** | 在容器里跑另一个发行版的用户空间 | 可以装任何发行版的包 |
| **Nix** | 在任何发行版上装新软件，不污染系统 | 跟随 nixpkgs unstable |
| **AppImage / 静态二进制** | 单文件应用 | 取决于上游 |

**关键优势**：你可以在 Ubuntu LTS / Debian stable / RHEL 这类**极稳的基底**上，用 Flatpak 拿到最新的 GIMP、Blender、OBS，用 distrobox 跑 Arch 或 Fedora 的工具链，用 Nix 拿最新的 CLI 工具。**系统层一动不动，应用层随便新。**

**KDE neon 是这个思路的极端版本**（LTS 基底 + 滚动 KDE），但只覆盖 KDE 生态。

---

## 8. 排序推荐表（综合）

| 排名 | 方案 | 内核 | Mesa | 桌面大版本 | 平滑度 | 适合谁 |
|---|---|---|---|---|---|---|
| **1** | **Fedora Workstation / KDE** | ✅ 数天 | ✅ 可 rebase | ❌ 约 6 个月 | 高 | 要最新内核/Mesa/浏览器，能接受每 6 个月升一次 |
| **2** | **Fedora Atomic + Bazzite/Bluefin** | ✅ 数天 | ✅ 可 rebase | ❌ 约 6 个月 | **最高** | 要最省心的更新体验 + 回滚 |
| **3** | **openSUSE Aeon / Kalpa** | ✅ 每日 | ✅ 每日 | ✅ 每日 | 高（+自动回滚） | 要自动更新 + 自动回滚，能接受 beta |
| **4** | **Manjaro stable** | ✅ 约 2 周 | ✅ 约 2 周 | ✅ 约 2 周 | 中高 | 要真滚动但要有缓冲 |
| **5** | **Debian testing (forky)** | ✅ 约 10 天 | ✅ 约 10 天 | ✅ 约 10 天 | 中 | 能接受冻结期 + 安全更新滞后 |
| **6** | **任意发行版 + Flatpak/distrobox/Nix** | — | — | 应用层 ✅ | 最高 | **零取舍，不想换发行版** |

---

## 9. 怎么自己量化滞后（可操作方法）

**方法**：选 3–5 个代表性组件（Mesa、Linux 内核、Python、Firefox），查其**上游 release 日期** vs **发行版仓库中该包的版本日期**，取差值。

| 工具 | 用途 | 局限 |
|---|---|---|
| **repology.org** | 直接对比**同一软件在 120+ 仓库的版本**，每小时更新；按 newest / outdated / legacy 分类 | 版本号比较算法可能误判；**滚动仓库标 "rolling" 不参与比较** |
| pkgs.org | 查各发行版包版本 | 不含日期差 |
| release-monitoring.org | 监控上游 release | 需自行关联 |
| DistroWatch | 发行版整体概况 | 粒度过粗，非包级 |

**关键提醒**：测「滞后」必须**分组件测量**。用一个数字概括一个发行版是错的。

---

## 10. 存疑与未核实项

| 项 | 状态 |
|---|---|
| Fedora Updates Policy 官方原文 | `docs.fedoraproject.org` 的 Updates Policy 与 kernel-overview 页本次被反爬/JS 拦截；要点由 FESCo #3584 工单、`KernelRebases` Wiki、Phoronix 交叉佐证。**建议以浏览器复核原文** |
| Fedora 45 的「内核 7.2 / GNOME 51」 | 来自二手源，需以官方 release notes 二次确认 |
| Universal Blue 用户规模 | 无权威公开数字 |
| Bluefin 各标签的精确构建时钟 | 官方页抓取失败，仅来自搜索摘要 |
| Debian forky 的冻结日期表 | 官方页未列 freeze 时间表 |
| Ubuntu `-updates` 对 Mesa 的推送规则 | 未取到官方政策原文，结论基于 26.04 vs 26.10 的 Mesa 版本对比推断 |
| Manjaro 的 AUR 错位问题 | 属社区讨论，非官方承认 |

---

## 11. 参考来源

### Fedora
- [Fedora Linux Release Life Cycle — Fedora Docs](https://docs.fedoraproject.org/en-US/releases/lifecycle/)
- [Updates policy — Fedora Docs](https://docs.fedoraproject.org/en-US/fesco/Updates_Policy/)
- [KernelRebases — Fedora Project Wiki](https://fedoraproject.org/wiki/KernelRebases)
- [Fedora Linux Kernel Overview — Fedora Docs](https://docs.fedoraproject.org/en-US/quick-docs/kernel-overview/)
- [Mesa Granted Permanent Updates Exception For Fedora Linux — Phoronix (2026-04-07)](https://www.phoronix.com/news/Mesa-Updates-Exception-Fedora)
- [Issue #3584: Grant permanent updates exception for Mesa — Pagure FESCo](https://pagure.io/fesco/issue/3584)
- [Fedora Linux 45 Schedule: Key tasks](https://fedorapeople.org/groups/schedule/f-45/f-45-key-tasks.html)
- [Fedora 45 Final Freeze: October 20 Release Date Set (linuxcompatible)](https://www.linuxcompatible.org/story/fedora-45-final-freeze-october-20-release-date-set-as-trackers-clear/)
- [Testing updates — Bodhi documentation](https://fedora-infra.github.io/bodhi/8.2/user/testing.html)
- [Updates, Upgrades & Rollbacks — Fedora Atomic Desktops Docs](https://docs.fedoraproject.org/en-US/atomic-desktops/updates-upgrades-rollbacks/)
- [Upgrading Fedora Linux Using DNF System Plugin — Fedora Docs](https://docs.fedoraproject.org/en-US/quick-docs/upgrading-fedora-offline/)
- [Rawhide — Fedora Docs](https://docs.fedoraproject.org/en-US/releases/rawhide/)
- [Update Guide — Bazzite Documentation](https://docs.bazzite.gg/Installing_and_Managing_Software/Updates_Rollbacks_and_Rebasing/updating_guide/)
- [Universal Blue — Documentation](https://universal-blue.org/documentation.html)
- [Bluefin Administrator's Guide](https://docs.projectbluefin.io/administration/)
- [Fedora Silverblue — Atomic Desktops](https://fedoraproject.org/atomic-desktops/silverblue/)

### Debian / Ubuntu
- [Debian "testing" distribution（官方，迁移延迟 10/5/2 天）](https://www.debian.org/devel/testing)
- [Debian "forky" Release Information](https://www.debian.org/releases/forky/index)
- [britney2 documentation — Debian release team](https://release.debian.org/doc/britney/)
- [Ubuntu 26.10 release notes（官方）](https://documentation.ubuntu.com/release-notes/26.10/)
- [Ubuntu 26.04 LTS release notes（官方）](https://documentation.ubuntu.com/release-notes/26.04/)
- [Ubuntu kernel lifecycle / HWE（官方）](https://ubuntu.com/kernel/lifecycle)
- [Rhino Linux 官网](https://rhinolinux.org/)
- [Rhino Linux 2026.1 — linuxiac](https://linuxiac.com/rhino-linux-2026-1-released-with-lomiri-desktop-images/)
- [KDE neon 官网](https://neon.kde.org/)
- [Vanilla OS — Updates](https://vanillaos.org/updates)
- [System76 Blog — COSMIC 1.0.8](https://system76.com/blog/post/cosmic-1-0-8-released)

### 镜像式 / 半滚动 / 方法论
- [Portal:Aeon — openSUSE Wiki](https://en.opensuse.org/Portal:Aeon)
- [Portal:Kalpa — openSUSE Wiki](https://en.opensuse.org/Portal:Kalpa)
- [Portal:Distribution/Releases — openSUSE Wiki](https://en.opensuse.org/Portal:Distribution/Releases)
- [Aeon Software Installation Wiki](https://github.com/AeonDesktop/Project/wiki/Software-Installation)
- [health-checker(8) manpage — openSUSE](https://manpages.opensuse.org/Tumbleweed/health-checker/health-checker.8.en.html)
- [Manjaro Wiki — Switching Branches（官方延迟政策）](https://wiki.manjaro.org/index.php?title=Switching_Branches)
- [Repology — About](https://repology.org/docs/about)
- [Intel Ends Clear Linux OS Development (OMG!Linux)](https://www.omglinux.com/intel-clear-linux-os-discontinued-2025/)
- [Endless OS — Updates overview](https://support.endlessos.org/en/endless-os/updates)
- [DistroWatch: KaOS 2025.05](https://distrowatch.org/12457)
