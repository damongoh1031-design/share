# 滚动发行版深度调研：NixOS vs Arch Linux vs openSUSE Tumbleweed / Slowroll

**调研日期**：2026-10-12
**调研维度**：滚动策略 · 打包质量 · 错误汇报 · 长期稳定 · 无人值守
**方法**：3 个并行研究子代理（各自独立检索官方文档/Wiki/新闻/仓库）+ 主调研员对 2 个存疑点二次核实
**证据标注**：`[核实]` = 官方文档或官方渠道直接陈述；`[社区]` = 论坛/第三方统计/推断

---

## 0. 结论先行

### 一句话结论

**这三个发行版都不是同一类东西**：Arch 是「真·上游直通」的激进滚动；openSUSE Tumbleweed 是「带自动化门禁的工程化滚动」；NixOS unstable 是「声明式、可原子回滚的准滚动」——它的更新机制最稳，但 **2026-08 发生了 nixpkgs 核心团队解散事件，长期治理风险需要计入决策**。

### 按场景直接给答案

| 你的场景 | 推荐 | 理由 |
|---|---|---|
| 桌面追新、爱折腾、愿意读公告 | **Arch** | 最接近上游，包最新，AUR 生态最广；代价是必须人工维护 |
| 无人值守服务器 / 边缘设备 | **openSUSE MicroOS**（不是 Tumbleweed） | 只读根 + 事务更新 + health-checker 失败自动回滚，是唯一「原生为无人值守设计」的选项 |
| 要滚动但不想天天修，且要可回滚 | **openSUSE Tumbleweed** | openQA 全系统门禁 + Btrfs/snapper 一键回滚，滚动里工程化程度最高 |
| 声明式配置 / 可复现 / 多机一致 | **NixOS**（stable 频道，别用 unstable） | generation 原子回滚无敌；但别把 unstable 当滚动发行版用 |
| 「比 Tumbleweed 稳、比 Leap 新」的折中 | **Slowroll** | 月更大版本；但仍是实验性项目，社区热度低，需自担风险 |

---

## 1. 滚动策略对比

| 项目 | NixOS (unstable) | Arch Linux | openSUSE Tumbleweed | openSUSE Slowroll |
|---|---|---|---|---|
| 模型 | 跟随 nixpkgs `master`，经 Hydra 构建全绿后推进 channel `[核实]` | core/extra/multilib 三仓 + testing/staging 测试仓 `[核实]` | snapshot（批次）机制，一批 = 一个完整更新集 `[核实]` | 基于 Tumbleweed snapshot，节奏放慢 `[核实]` |
| 更新到用户端的延迟 | 提交进 master 后通常**数天**才进 channel `[核实]` | 小时级～天级，无官方 SLA `[社区]` | 「准备好且自动 QA 通过即发布」 `[核实]` | 大更新每月一次（约每月 9 日 ±3 天） `[核实]` |
| 发布频率 | channel 推进即更新（受 Hydra 门控，可能被卡） | 持续；ISO 每月 1 日刷新 `[核实]` | 可高达每日一次；实测 2026-08 为 **23 个 snapshot / 31 天**，2026-02 为 17 / 28 天 `[核实]` | 月更 + 安全/缺陷修复持续推送 `[核实]` |
| 稳定版/版本号 | 每 6 个月一个稳定版：25.05 → **25.11 Xantusia** → **26.05 Yarara** `[核实]` | **无版本号**，一次性安装永久升级 `[核实]` | 无版本号，snapshot 有编号 | 有「版本 bump」（如 2025-01 那次） |
| 变体 | `nixos-unstable-small`（只等常用包集合，**面向服务器**）；`nixpkgs-unstable`（不含 NixOS 自动测试） `[核实]` | testing / staging / gnome-unstable / kde-unstable `[核实]` | Slowroll / MicroOS / Aeon / Kalpa 共享同一代码源 `[核实]` | — |
| 历史归档 | git 历史 + channel 分支 | **ALA (Arch Linux Archive)**，2013-08 起，存 ISO + 全历史包 + **每日仓库快照** `[核实]` | 旧 snapshot 仓库保留 | 同 TW |

**要点**：
- NixOS unstable **不是** Arch 意义上的滚动——它是「经过 CI 门控的 curated snapshot」，新鲜度反而可能低于 Arch，且 Hydra 构建失败会**连安全修复一起卡住**（社区已承认此风险）`[社区]`。
- Arch 的 `community` 仓库已于 **2023-05** 并入 `extra`，现在只有三个稳定仓库 `[核实]`。
- Tumbleweed 的 snapshot 是**整体交付**的：不存在「只升一个包」的语义，这从机制上消灭了 partial upgrade 问题。

---

## 2. 打包质量对比

| 项目 | NixOS | Arch Linux | openSUSE TW / Slowroll |
|---|---|---|---|
| 包数量 | **140,000+** 包，1,090,656 commits `[核实]` | 官方「several thousand」（未给精确数）；AUR 第三方统计约 **107,724**（官方 About 页 ">49,000" 已过时）`[社区]` | 未获官方总量；单个大 snapshot 可含约 **4001 个包更新**（2026-07-03）`[核实]` |
| 贡献者规模 | 25.11 周期：**2742 人 / 59,430 commits**；新增 7002 包、更新 25252、移除 6338 `[核实]` | Package Maintainers（原 TU）为官方 staff，需 **2 名 PM 担保 + 邮件列表 + 投票**，新人前两月为 "junior" `[核实]` | OBS 构建；提交经 devel project → Factory `[核实]` |
| CI / 门禁 | OfBorg 在 **PR 阶段**选择性构建（1800s 超时），**但不是 required check**；Hydra 在 merge 后构建 trunk 并驱动 channel `[核实]` | **无全系统自动门禁**；大版本升级靠 `staging` 仓批量重建（如 Python 3.14 rebuild，2025-12-14）`[核实]` | **staging 项目成组集成测试** → openQA 验证包间兼容 → 才并入 Factory `[核实]` |
| 法务/合规审查 | 无独立法务环节 | 无 | **legal-auto 自动扫描 + 触发式人工法务审查** `[核实]` |
| 哲学 / 质量取向 | 可复现构建优先；包由 maintainer 认领 | **「尽量贴近上游，仅在必要时打补丁」**——上游 bug 常被直接继承 `[核实]` | 工程化优先：宁可不发，也不发没过 openQA 的 snapshot |
| 破损包现状 | 半自动标记 `meta.broken`（`mark-broken.sh` 从 Hydra 拉失败列表），长期破损包确实存在，有专门 tracking issue `[核实]` | 官方包「能编译、能共存」即达标；AUR 非官方、**无任何保证** `[核实]` | 未通过门禁的更新被 staging 挡住，不进入用户视野 |
| 供应链事件 | 无重大公开事件 | **2025-06 AUR 大规模供应链攻击（400+ 包被污染）**；2026-06-12 又有 AUR 恶意包事件 `[核实]` | 无重大公开事件 |

**要点**：
- 论「包被放进仓库前经过多少自动验证」：**openSUSE > NixOS > Arch**。
- 论「装完之后能恢复到已知好状态」：**NixOS > openSUSE >> Arch**。
- Arch 的「最小改动」哲学是双刃剑：你能最快拿到上游新特性，也能最快拿到上游的新 bug。

---

## 3. 错误汇报对比

| 项目 | NixOS | Arch Linux | openSUSE TW / Slowroll |
|---|---|---|---|
| 官方 issue 追踪 | GitHub `NixOS/nixpkgs` `[核实]` | **GitLab**（gitlab.archlinux.org），2023-12-03 从 Flyspray 迁移完成 `[核实]` | **Bugzilla**（bugzilla.opensuse.org）`[核实]` |
| 构建失败公开看板 | hydra.nixos.org + status.nixos.org `[核实]` | 无公开全量构建看板 | **openqa.opensuse.org**——每个 snapshot 的测试失败项公开可查 `[核实]` |
| 安全报告渠道 | ⚠️ **不是** 通用的 `security@nixos.org`；官方要求邮件给安全团队**成员个人地址**（附 GPG 指纹），另有 tracker.security.nixos.org 与 Matrix `#security:nixos.org` `[核实]` | 通过 GitLab / `arch-dev-public` 邮件列表 | Bugzilla + `factory@lists.opensuse.org` |
| 用户侧告警机制 | 无专门的「需人工介入」公告页 | **`archlinux.org/news` 的 manual intervention 公告**——滚动升级需人工介入时发公告 `[核实]` | 邮件列表 + 论坛 Tumbleweed 标签 |
| 社区渠道 | Discourse、Matrix | bbs.archlinux.org、IRC/Matrix、`arch-dev-public` | 论坛、Matrix `#support:opensuse.org`、`factory@` 列表 |

**要点**：
- **openSUSE 的透明度最高**：openQA 把「这批更新挂了哪些测试」直接摊在公网上，任何人都能复核，这是三者中唯一的。
- **Arch 的 news 机制是「必须订阅」的硬性依赖**：错过 manual intervention 公告 = 升级可能挂。
- NixOS 的安全报告渠道比较反直觉（找个人而非组邮箱），运维流程里需要提前记下。

---

## 4. 长期稳定性对比

| 项目 | NixOS | Arch Linux | openSUSE TW / Slowroll |
|---|---|---|---|
| 升级原子性 | **是**。相同输入 → 确定性构建；升级原子化，断电中断后系统仍一致，只会停在旧/新其一 `[核实]` | 否。`pacman -Syu` 过程中断可能留下半升级状态 | 是（事务性）。snapshot 整体应用 `[核实]` |
| 回滚机制 | **generation 机制**：`nixos-rebuild switch --rollback` 立即回上一代；boot 菜单可选任意旧 generation `[核实]` | **无官方快照回滚**。降级靠 ALA：`pacman -U <archive-url>` 降级单包，或把 pacman.conf 指向 `archive.archlinux.org/repos/<日期>/` 后 `pacman -Syyuu` 整机回退 `[核实]` | **Btrfs + snapper**：`zypper dup` 前自动建快照；重启 → GRUB2 选「Start Bootloader from a read-only snapshot」→ `sudo snapper rollback` `[核实]` |
| 已知结构性风险 | flakes 自 Nix 2.4 起仍是**实验性**；CA derivations 亦为实验特性，随时可能引入 breaking change `[核实]` | **partial upgrade 被官方明令禁止**；`.pacnew`/`.pacsave` 必须人工合并；内核更新后必须重启 `[核实]` | 3 代内核驱动模块可能跟不上；NVIDIA 闭源驱动每次内核升级需重编；**AMDGPU-PRO 不支持 TW**；VMware/VirtualBox 模块不保证；Packman 编解码器偶发不兼容 `[核实]` |
| 磁盘占用 | generation 累积占空间，**必须配 `nix.gc` 自动回收**，否则 `/`、`/boot` 会满 `[核实]` | 常规；ALA 本地缓存放大 | Btrfs 快照占空间，需配 snapper 清理策略 |
| 长期不升级的后果 | 影响较小（可 `nix flake update` 或换 channel） | **间隔越久越难升**——依赖连锁升级 + 会错过人工介入公告 `[社区]` | 影响较小（snapshot 整体升级） |

### 关键：Arch 的历史人工介入事件（全部来自 archlinux.org/news）

| 日期 | 事件 |
|---|---|
| 2024-03-29 | **xz 后门事件** |
| 2024-03-04 | mkinitcpio hook 迁移与早期 microcode |
| 2024-07-01 | openssh-9.8p1 升级后需重启 sshd |
| 2024-09-14 | pacman 7.0.0 与本地仓库需手动介入 |
| 2025-02-03 | glibc 2.41 损坏 Discord 安装 |
| 2025-06-21 | linux-firmware 升级需手动介入 |
| 2026-09-22 | mkinitcpio ≥42 的 TPM2 LUKS 解锁需手动介入 |

> 近 3 年至少 7 次需要用户手动干预。这是「Arch 不适合无人值守」的最直接证据。

### ⚠️ 必须计入的 NixOS 治理风险（2026-08 已核实）

2026-08-08，**nixpkgs 核心团队宣布解散**（官方 Discourse 公告，PR `NixOS/org#277`）。核心团队自述原因：

- 治理职责过重，与 Steering Committee (SC) 存在**长期微管理**与沟通失灵；
- 团队流失严重，招新「仅 1 人响应」，无法维持健康规模；
- 强调「不是某一次事件，而是长期模式的累积」，两人将**减少 nixpkgs 参与**且不竞选 SC。

**直接后果**（公告原文）：*"The matters in our jurisdiction are left with no direct owner at present, with the SC acting as the final backstop as always."* —— 该团队管辖范围内的事务**目前无直接负责人**。

这是**一年内 NixOS 第二次核心治理团队因治理问题集体退出**（上一次是 moderation 团队）。

**对决策的影响**：不影响 nixpkgs 当下的代码质量与回滚能力，但**削弱了对 3–5 年长期维护产能的信心**。若把 NixOS 用于关键长期基础设施，建议把这当作一条独立风险项评估。

### Slowroll 的特殊情况

- 官方 Wiki 仍标注为 **experimental**（2023 年发布，基于 Tumbleweed 的慢速滚动）`[核实]`。
- 大更新每月一次（约每月 9 日 ±3 天），安全/缺陷修复持续推送；用 `zypper dup` 升级；从 Leap/TW 迁移用 `opensuse-migration-tool` `[核实]`。
- 2024-07 曾规划**季度**更新，后改为**月度** `[核实]`。
- **社区热度信号**：Slowroll 专属的官方新闻最后一篇是 **2025-01-09**（新年版本 bump），此后近 21 个月无 Slowroll 专题新闻。但**镜像仍在持续产出**——阿里云镜像站显示 `opensuse-slowroll-next-full-base.20261001`（2026-10-01）`[核实]`。
- 结论：**项目活着，但社区投入与宣传显著低于 Tumbleweed**。选它 = 承担一个小众项目的持续性风险。

---

## 5. 无人值守（unattended）对比

| 项目 | NixOS | Arch Linux | openSUSE TW / Slowroll |
|---|---|---|---|
| 官方自动升级机制 | **有**。`system.autoUpgrade`（`nixos-upgrade.timer/.service`，`Persistent=true`），支持 `dates`、`randomizedDelaySec`、`allowReboot` `[核实]` | **无** `[核实]` | 无内置「一键全自动」；但可用 `zypper dup` + systemd timer `[社区]` |
| 自动重启 | 仅当 `allowReboot=true`（或 `operation="boot"`）；**默认 false** `[核实]` | 不适用 | 可用 `transactional-update` + 重启 |
| 失败自动回滚 | ❌ **不自动**。新 generation 启动失败需**手动**在 bootloader 选旧项（约 3 次按键）；NixOS 无内置 kexec 运行时回滚 `[核实]` | ❌ 无 | ✅ **MicroOS 有 health-checker**：更新后校验系统，异常**自动回滚** `[核实]` |
| 事务性更新 | 原生（generation） | ❌ | `transactional-update`：基于 btrfs 快照的原子更新，变更下次重启才生效 `[核实]` |
| 钉住版本 | `nix flake lock` 锁定 / 换 channel | 无（ALA 可整机回退但需手动） | **`tumbleweed-cli`** 可钉住/切换指定 snapshot，避免盲跟 `[核实]` |
| 官方无人值守方案 | 无专用发行版 | 无 | **MicroOS**（server，非 beta）：只读根 + 事务更新 + health-checker，为容器主机/边缘/大规模无人值守设计；**每个 TW snapshot 自动产出对应 MicroOS 版本** `[核实]` |
| 桌面不可变版 | — | — | **Aeon**（beta）/ **Kalpa**：基于 Tumbleweed 的不可变桌面，Kalpa 后台定期跑 `transactional-update dup` `[核实]` |
| 关键障碍 | 无自动回滚，但原子性使其「失败也停在旧系统」 | ① 必须读 news ② 可能需人工介入 ③ `.pacnew` 需手动合并 ④ 内核更新后需重启 ⑤ 部分升级会毁系统 `[核实]` | TW 上自动 `zypper dup` **无内置失败自动回滚**，需自建 snapper/health 逻辑 `[核实]` |
| 社区共识 | 【社区】多数认为服务器**可开** `autoUpgrade`（建议 `operation="boot"`，用 stable 或 `-small` channel 而非 unstable） | 【社区】**不适合**全自动无人值守。`arch-unattended-updates` 作者本人明确说明「Arch 是滚动版、无 partial-upgrade 支持、无仅安全仓库」 | 【核实】官方推荐无人值守/边缘/容器用 **MicroOS 或 Leap Micro**；求稳用 **Leap**；要最新且愿运维才用 Tumbleweed |

### 无人值守就绪度排序

**openSUSE MicroOS（原生支持，自动回滚）> NixOS（可自动化，但回滚需人工）> openSUSE Tumbleweed（可自动化，无自动回滚）> Slowroll（同 TW 但项目小众）>>> Arch（官方/社区一致反对）**

---

## 6. 五维评分卡（主观综合，1–5 分）

> 评分为本报告基于上述事实的综合判断，非客观测量值，仅供快速比较。

| 维度 | NixOS | Arch Linux | Tumbleweed | Slowroll |
|---|---|---|---|---|
| 滚动新鲜度 | 3.0 | **5.0** | 4.0 | 2.5 |
| 打包质量 | 4.5 | 3.5 | **4.5** | 4.5 |
| 错误汇报透明度 | 3.0 | 4.0 | **5.0** | 4.5 |
| 长期稳定性 | 4.5 | 2.5 | 4.0 | **4.5** |
| 无人值守就绪度 | 4.0 | 1.5 | 3.5 | 3.5 |
| **治理/项目健康度** | **2.5** ⚠️ | 4.0 | 4.5 | **2.5** ⚠️ |

**读法**：
- Arch 在「新鲜度」上一骑绝尘，在「无人值守」上垫底——这不是缺点，是定位。
- Tumbleweed 是**唯一没有明显短板**的选项。
- NixOS 技术机制最强，但治理风险把它拉下来。
- Slowroll 各项稳健，但治理/项目健康度是短板（实验性 + 社区投入低）。

---

## 7. 决策建议

### 如果你要「无人值守长期跑」

1. **首选 openSUSE MicroOS**：唯一原生带「更新失败自动回滚」的选项，openQA + health-checker 双保险。
2. **次选 NixOS stable 频道 + `system.autoUpgrade`**：务必设 `operation = "boot"` 或 `allowReboot`，并配好 `nix.gc`；接受「回滚要人按 3 下键」这个前提。**不要用 unstable 做无人值守。**
3. **Tumbleweed 可用但需自建**：`zypper dup` + timer + 自己的 snapper 健康检查脚本；或直接用 `tumbleweed-cli` 钉 snapshot 手动推进。
4. **不要用 Arch 做无人值守**。这是官方与社区的一致立场，不是保守建议。

### 如果你要「桌面追新 + 自己掌控」

- **Arch**：包最新、AUR 最广、文档最厚（ArchWiki）。代价是必须订阅 news、处理 `.pacnew`、接受偶发人工介入。
- **Tumbleweed**：如果你想要 Arch 的新度但不想天天修，且机器有 Btrfs，选它。

### 如果你要「声明式 / 多机一致 / 可复现」

- **NixOS**，但用 **stable 频道**而非 unstable。把治理风险当作一条已知风险项登记。

---

## 8. 存疑与未核实项（交给读者复核）

| 项 | 状态 |
|---|---|
| Arch 上游 → stable 的精确延迟 | 官方从未给出量化数字，报告中标注为定性/社区推断 |
| Arch 官方包精确数量 | 官方 About 页写 "several thousand"；AUR 数量官方页已过时（>49,000），第三方统计 ~107,724 |
| Tumbleweed 包总量 | 未获官方数字 |
| Arch ↔ Tumbleweed 升级失败率量化对比 | **不存在公开数据**；任何「TW 比 Arch 稳 X%」的说法都是推断 |
| openSUSE staging 流程专门文档页 | 未抓取到独立文档页，建议用 openqa.opensuse.org/group_overview/2 复核 |
| `transactional-update.timer` 在 TW 上的原文依据 | 未直接读到 TW 文档原文（SLE Micro 文档确认 transactional-update 默认行为） |
| Slowroll 当前是否已脱离 experimental | 官方 Wiki 仍标 experimental；镜像仍在产出（2026-10-01），但专题新闻停在 2025-01 |

---

## 9. 参考来源

### NixOS
- [Channel branches - Official NixOS Wiki](https://wiki.nixos.org/wiki/Channel_branches)
- [Automatic system upgrades - Official NixOS Wiki](https://wiki.nixos.org/wiki/Automatic_system_upgrades)
- [nixos-rebuild - Official NixOS Wiki](https://wiki.nixos.org/wiki/Nixos-rebuild)
- [Flakes - Official NixOS Wiki](https://wiki.nixos.org/wiki/Flakes)
- [Security Team | Nix & NixOS](https://nixos.org/community/teams/security/)
- [NixOS Blog / Announcements / 2025](https://nixos.org/blog/announcements/2025/)
- [GitHub - NixOS/nixpkgs](https://github.com/NixOS/nixpkgs)
- [OfBorg and CI - Nix Docs](https://zemdregon.github.io/nix-docs/06-nixpkgs/contribution/ofborg-and-ci/)
- [The Nixpkgs core team has disbanded - NixOS Discourse (官方公告)](https://discourse.nixos.org/t/the-nixpkgs-core-team-has-disbanded/79413)
- [Nixpkgs Core Team Disbanded: NixOS Governance Fails Again](https://byteiota.com/nixpkgs-core-team-disbanded-nixos-governance-fails-again/)
- [Tracking: x86_64-linux packages that have never built - GitHub](https://github.com/NixOS/nixpkgs/issues/566956)

### Arch Linux
- [Arch Linux - About](https://archlinux.org/about/)
- [Arch Linux - News](https://archlinux.org/news/)
- [ArchWiki - Arch Linux Archive](https://wiki.archlinux.org/title/Arch_Linux_Archive)
- [ArchWiki - pacman/Pacnew and Pacsave](https://wiki.archlinux.org/title/Pacman/Pacnew_and_Pacsave)
- [ArchWiki - Package Maintainers](https://wiki.archlinux.org/title/Package_Maintainers)
- [ArchWiki - Official repositories](https://wiki.archlinux.org/title/Official_repositories)
- [ArchWiki - Partial upgrade](https://wiki.archlinux.org/title/Partial_upgrade)
- [Arch Linux - Bugtracker migration to GitLab completed](https://archlinux.org/news/bugtracker-migration-to-gitlab-completed/)
- [Arch Linux - Todo: Python 3.14 rebuild](https://archlinux.org/todo/python-314-rebuild/)
- [Arch Linux - Release 2026.10.01](https://archlinux.org/releng/releases/2026.10.01/)
- [GitHub - adobloug/arch-unattended-updates](https://github.com/adobloug/arch-unattended-updates)
- [bbs.archlinux.org - Why is pacman -Sy bad?](https://bbs.archlinux.org/viewtopic.php?id=241092)

### openSUSE
- [Portal:Tumbleweed - openSUSE Wiki](https://en.opensuse.org/Portal:Tumbleweed)
- [Portal:Slowroll - openSUSE Wiki](https://en.opensuse.org/Portal:Slowroll)
- [Portal:MicroOS - openSUSE Wiki](https://en.opensuse.org/Portal:MicroOS)
- [Portal:Aeon - openSUSE Wiki](https://en.opensuse.org/Portal:Aeon)
- [Portal:Kalpa - openSUSE Wiki](https://en.opensuse.org/Portal:Kalpa)
- [openSUSE:OpenQA - openSUSE Wiki](https://en.opensuse.org/openSUSE:OpenQA)
- [openSUSE:Factory submissions](https://en.opensuse.org/openSUSE:Factory_submissions)
- [openSUSE:Legal review](https://en.opensuse.org/openSUSE:Legal_review)
- [Updating, upgrading, snapshots and best practices](https://doc.opensuse.org/documentation/tumbleweed/updating_upgrading_reverting/)
- [Tumbleweed Monthly Update - August 2026](https://news.opensuse.org/2026/09/02/tw-monthly-update-august/)
- [Tumbleweed Monthly Update - February 2026](https://news.opensuse.org/2026/03/02/tw-monthly-update-feb/)
- [Slowroll Set for a Quarter of Updates (2024-07-03)](https://news.opensuse.org/2024/07/03/slowroll-set-for-a-quarter-of-updates/)
- [New Year Starts with Slowroll Version Bump (2025-01-09)](https://news.opensuse.org/2025/01/09/ny-starts-with-slowroll-vb/)
- [SDB:NVIDIA drivers - openSUSE Wiki](https://en.opensuse.org/SDB:NVIDIA_drivers)
- [GitHub - openSUSE/transactional-update](https://github.com/openSUSE/transactional-update)
- [GitHub - boombatower/tumbleweed-cli](https://github.com/boombatower/tumbleweed-cli)
- [openQA Factory staging group overview](https://openqa.opensuse.org/group_overview/2)
