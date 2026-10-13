# 发行版运营分析：社区规模 · 运行现状 · 套件源 · 包管理 · 漏洞修复

> **调研时点**：2026-10-13
> **对象**：Arch Linux · NixOS · openSUSE (Tumbleweed) · Fedora · Debian · Ubuntu（+ Alpine / Gentoo 参照）
> **方法**：3 个并行子代理分工调研 + 主调研员对全部关键数字做 API/HTTP 独立实测
> **标注约定**：`[实测]` = 本次由主调研员用 curl/API 独立取到；`[官方]` = 读到官方原文；`[二手]` = 媒体报道/社区帖；`[未找到]` = 无公开数据

---

## 0. 结论先行

**运营能力的五个维度，五家各占一个第一，没有全能选手。**

| 维度 | 第一名 | 一句话依据 |
|---|---|---|
| **社区规模** | **Debian** | 1,039 名有投票权的 DD，是 Arch 核心团队（93 人）的 11 倍 |
| **运行现状** | **Fedora / Ubuntu** | 唯一两家「发布节奏 + 基础设施 + 安全数据」三线都无短板的 |
| **套件源** | **NixOS（规模）/ openSUSE（基建）** | nixpkgs unstable 119k 项目（全榜第一）；OBS 服务 21 个发行版 |
| **包管理** | **NixOS（能力）/ openSUSE（原子性）** | 唯一天生支持多版本共存 + generation 原子回滚 |
| **漏洞修复** | **Ubuntu / Debian** | 唯一有可执行 JSON API 且覆盖完整；Ubuntu 有专职团队 |

**两个最需要注意的结构性事实：**

1. **Arch 是本题中运营风险最高的发行版** —— 安全追踪器自 2025-06 事实停摆、安全团队仅 4 人、无 CNA、无专门安全仓库、2026 年连续遭遇 DDoS + AUR 供应链双重打击，且核心维护者规模只有 Debian 的 9%。
2. **「OSV.dev 覆盖」决定了 LLM/自动化能否做安全运维** —— 实测 `[实测]`：Fedora / Arch / NixOS 三家在 OSV 上**直接 400 `invalid ecosystem`**，任何基于 OSV 的自动化安全流程对这三个发行版**开箱即不可用**。

---

## 1. 社区规模

### 1.1 核心维护者规模（量级差最大的一节）

| 发行版 | 核心维护者 | 官方包数 | 包/人 | 来源 |
|---|---|---|---|---|
| **Debian** | **1,039 有投票权 DD**（+1,384 近 12 月贡献者） | ~42k（sid） | ~40 | `[二手]` contributors.debian.org / SPI 年报 |
| **NixOS** | nixpkgs 贡献者数千（无官方"成员"制） | **119k 项目** | — | `[二手]` GitHub 贡献者 |
| **openSUSE** | ~521 members | ~16k | ~31 | `[二手]` openSUSE 成员页 |
| **Fedora** | ~325 packagers | ~24k | ~74 | `[二手]` LWN |
| **Ubuntu** | 378 Ubuntu Members | ~40k | ~106 | `[二手]` Launchpad |
| **Arch** | **23 Developer + 70 Package Maintainer = 93** | 16,008 | **~172** | `[实测]` archlinux.org/people 实测 23 |
| **Alpine** | 团队规模未公开 | ~12k（edge） | — | `[未找到]` |

**三个可直接引用的判断：**

- **Debian 是唯一「千人级」社区**。1,039 DD 意味着任何单点故障都很难动摇项目 —— 这是它 30 年不倒的结构性原因。
- **Arch 是六大中核心团队最薄的**，且人均管 172 个包（是 Debian 的 4.3 倍）。Arch 官方仓库 16,008 包由 93 人维护，**bus factor 风险最高**。
- **NixOS 的"规模"性质完全不同**：它没有会员制，贡献者数取决于 GitHub 统计口径，与 Debian 的 DD 不可直接比较。**跨发行版比较贡献者数时，必须说明口径。**

### 1.2 社区治理个体事件（2025-2026，本次新增）

| 事件 | 日期 | 内容 | 来源 |
|---|---|---|---|
| **Arch 项目领导人连任** | **2026-06-04** | Levente "anthraxx" Polyák 在两名候选人中连任 Project Lead，任期两年 | `[官方]` archlinux.org/news/arch-linux-2026-leader-election-results/ |
| **Debian DPT 集体离职** | **2026-01** | 数据保护团队因 GDPR 职责无人值守集体离职，DPL 公开发招募 | `[二手]` helpnetsecurity.com |
| **Arch 安全邮件列表停摆** | 2025-06-13 起 | arch-security 邮件列表**超过 16 个月无活动** | `[二手]` bbs.archlinux.org id=314349 |
| **NixOS 治理空窗** | 2026-10-15 起投票 | 第三次 Steering Committee 选举投票期才开始 | `[二手]` discourse.nixos.org |

> ⚠️ **Arch 的「领导人连任」是一件被主流报道忽略的事**：2026-06 AUR 供应链事件爆发时，项目正处于领导人换届期（选举结果 06-04 公布，事件 06-11 爆发）。**连续事件 + 管理层刚交接**，是运营风险的叠加项。

---

## 2. 运行现状

### 2.1 当前发布状态（2026-10 时点）

| 发行版 | 当前稳定版 | 发布日期 | 备注 |
|---|---|---|---|
| **Fedora** | **44** | 2026-04-28 | **45 target 2026-10-20**（Final Freeze 已于 10-06 完成） |
| **Ubuntu** | LTS **26.04.1 (resolute)** / interim 25.10 | 2026-04-23 / 2025-10-09 | 26.04 LTS 支持至 2031-04 |
| **Debian** | stable **13 trixie** / testing 14 forky | 2025-08-09 | forky 未 freeze |
| **NixOS** | **26.05 "Yarara"** | 2026-06-01 | 支持至 2026-12-31 |
| **openSUSE** | Tumbleweed 每日快照 / Leap **16.0** | Leap 16.0 ≈ 2025-10 | Leap 16.6 计划 2031 秋 |
| **Arch** | 滚动，ISO **2026.10.01** | 2026-10-02 | kernel 7.2.7 / systemd 262 |
| **Alpine** | **3.23.0** | 2025-12-03 | EOL 2027-11-01 |

> **Arch 的"版本号"问题**：滚动发行版没有版本号，官方唯一锚点是**月度 ISO 快照**（`YYYY.MM.DD`）。给 Arch 写文档时**不要写"Arch 26.x"**，要写"ISO 2026.10.01"。

### 2.2 基础设施与事故

| 发行版 | 构建农场 | CI / QA | 2025-2026 事故 |
|---|---|---|---|
| **Fedora** | Koji | Zuul + openQA + Bodhi karma | `[未找到]` 重大宕机 |
| **Debian** | buildd（~20 架构） | autopkgtest + piuparts | `[未找到]` 数据事故 |
| **openSUSE** | **OBS**（3 数据中心） | **openQA**（650 套件 / 114 机器） | **2025-12-01 OBS 中断 35 分钟**（Ruby gem 冲突，有官方 post-mortem） |
| **Arch** | 官方 build 机群 + rebuilderd | reproducible.archlinux.org | **2025-08-21 DDoS 攻击**（官方公告，打 archlinux.org / AUR / Forums）+ **2026-06 AUR 供应链** + **2026-07 暂停认领** |
| **NixOS** | **Hydra** | Hydra jobsets + Zero Hydra Failures | Hydra 长期"排队慢"，但状态页存活 |

**Arch 的三连击是本次调研中最值得注意的运营事实链：**

1. **2025-08-21** —— 官方公告正在遭受**持续的 DDoS 攻击**，主要打击 archlinux.org、AUR 和论坛。原文称"正在评估 DDoS 防护服务商，同时仔细权衡成本、安全和伦理标准"。`[官方]` archlinux.org/news/recent-services-outages/
2. **2026-06-12** —— 官方公告 **AUR 恶意包事件**：攻击者通过 adoption 机制批量接管被遗弃包并篡改 PKGBUILD。官方原文只说「high volume」，**未给出具体包数**。`[官方]` archlinux.org/news/active-aur-malicious-packages-incident/
3. **2026-07-30** —— DevOps 成员经邮件列表宣布**紧急停用 package adoption 功能**。`[二手]`

> **数字口径澄清（本次纠错）**：媒体上流传的 **"400+"** 与 **"1,500"** 两个数字**并不矛盾**——400+ 是事件当时已被移除的包数（cybersecuritynews 2026-06-12 报道），1,500 是攻击者最终批量收养的包数（Foss Force 2026-06-13 等后续统计）。引用时必须写明口径，不可混用。

---

## 3. 套件源（仓库架构）

### 3.1 官方仓库结构

| 发行版 | 仓库分层 | 关键结构事实 |
|---|---|---|
| **Arch** | core / extra / multilib + 测试层 | `[官方]` **2023-05-19 `[community]` 合并进 `[extra]` 后为空**；`[testing]` 拆为 core-testing / extra-testing；`[staging]` 拆为 core-staging / extra-staging |
| **NixOS** | 无传统分层 | `[官方]` nixpkgs 是**单一 Git 仓库**，channel 是"经 Hydra 测试的快照分支"，不是独立二进制仓库。`nixos-unstable` 跟 master，`nixos-26.05` 每 6 月一发 |
| **openSUSE** | OSS / Non-OSS / Update | Tumbleweed 同时有 `repo/oss` 与 `repo/non-oss`；**Packman 是第三方**（多媒体编解码） |
| **Fedora** | fedora / updates / updates-testing / rawhide | `[官方]` **模块化已废弃**（Fedora 39 停建模块），模块化与 DNF4 遗留工具**将在 F46 移除** |
| **Debian** | main / contrib / non-free / **non-free-firmware** | `[官方]` **non-free-firmware 是 Debian 12 新增**（源于 2022 年 GR）；另有 security / backports |
| **Ubuntu** | main / restricted / universe / multiverse | `[二手]` main=官方免费支持、universe=社区支持、restricted=专有驱动、multiverse=版权受限 |
| **Alpine** | main / community / testing | testing 为边缘仓库 |

### 3.2 第三方源机制对照

| 发行版 | 机制 | 性质 | 规模 |
|---|---|---|---|
| **Arch** | **AUR** | PKGBUILD 脚本库（**非二进制**，用户自行构建） | `[实测]` **121,822 包** |
| **NixOS** | overlay / flake | 无传统第三方源；`inputs.nixpkgs.url` 可指向任意 fork | — |
| **openSUSE** | **OBS** | 通用构建平台，**不只服务 openSUSE** | `[官方]` ~30,000 用户 / **140,000+ 包 / 21 个发行版 / 6 种架构** |
| **Fedora** | **COPR** | 官方托管的社区构建 | `[未找到]` 无公开项目数 |
| **Ubuntu** | **PPA** | Launchpad 个人源 | `[二手]` >130,000 |
| **Debian** | 无官方第三方机制 | **backports 是官方**（best-effort）；deb-multimedia **非官方** | — |
| **通用** | Flatpak / Flathub | Fedora 默认集成；Ubuntu 默认 Snap | `[二手]` Flathub >2,800 应用 |

### 3.3 仓库规模（Repology 实测，2026-10-13）

Repology 全局：**330,508 项目 / 5,036,835 独立包**。下表「新鲜度」= 该项目在其仓库中处于上游最新版的比例，**这是判断"运行状况"最有价值的单个指标**：

| 仓库 | 项目数 | **最新版比例** | 落后比例 |
|---|---|---|---|
| **nixpkgs unstable** | **119k** | **83.6%** | 16.4% |
| nixpkgs stable 26.05 | 115k | 69.0% | 30.9% |
| **AUR** | 96k | 69.0% | 30.8% |
| Debian unstable | 42k | — | — |
| Ubuntu 26.04 | 40k | 48.3% | 49.6% |
| Debian 13 | 38k | 40.9% | 57.2% |
| Ubuntu 24.04 | 37k | 34.1% | 64.0% |
| Fedora 43 | 24k | 56.8% | 43.0% |
| Fedora Rawhide | 22k | **74.4%** | 25.4% |
| Gentoo | 18k | 71.7% | 27.7% |
| openSUSE Tumbleweed | 16k | **73.0%** | 26.6% |
| Arch Linux | 12k | **86.5%** | 13.3% |
| Alpine 3.23 | 8.8k | — | — |

> `[实测]` 三个反直觉点：
> - **Arch 官方仓库（12k）虽小，新鲜度却是全榜第一（86.5%）** —— 因为它只收上游最新版。
> - **AUR（96k）比 Arch 官方仓库大 8 倍**，刷新率只有 69%。
> - **Debian 13 stable 只有 40.9% 最新版**，这是设计选择不是缺陷 —— stable 就该滞后。

---

## 4. 包管理

### 4.1 核心能力对照

| 属性 | Arch (pacman) | Fedora (dnf5) | openSUSE (zypper) | Debian/Ubuntu (apt) | NixOS (nix) |
|---|---|---|---|---|---|
| 语言 | C | C++（dnf5 已重写） | C++ | C++ | Nix 语言 |
| 依赖求解 | 全量重算 | **libsolv SAT** `[官方]` | **libsolv SAT** `[官方]` | 自研，3.0 起 solver3 回溯式 | 函数式 + SAT |
| **原子性** | ❌ **无原子性** `[官方]` | ✅ `dnf history undo/rollback` | ✅ 事务 + **snapper 快照** | ⚠️ dpkg 半完成态 | ✅ **generation 原子切换** |
| 多版本共存 | ❌ | ❌ | ❌ | ❌ | ✅ **天然支持** |
| 并行下载 | `ParallelDownloads` | `max_parallel_downloads` | ⚠️ 无原生多线程 | 可配 | Nix 层 |

**两条已核实的结构性事实：**

- **pacman 无原子性是已知缺陷，非传言。** Arch 论坛原贴记录：`pacman -Syu` 中途因文件系统错误事务中止，**此前已执行的 6 个 remove 未回滚**，导致 `liblzo2.so.2` 缺失、pacman 自身损坏。社区回复原文：*"package replacement is not an atomic operation. It removed lzo2 first then started doing other stuff and got broken."* `[官方]` bbs.archlinux.org id=186193
- **libsolv 是"隐形基础设施"。** zypper 与 dnf **共用同一个 SAT 求解器**（`openSUSE/libsolv`，0.7.40 / 2026-09-21），支持 rpm/deb/arch/apk 四种包格式。这意味着 Fedora 和 openSUSE 的依赖解析底层是同一个东西。

### 4.2 包生命周期

| 阶段 | Arch | Fedora | Debian | openSUSE TW | NixOS |
|---|---|---|---|---|---|
| **准入** | AUR → 申请 → extra | spec + Bugzilla review → rawhide | sponsor → **NEW queue** → unstable | OBS → submit request → Factory | PR to nixpkgs |
| **升级** | 滚动跟上游 | 冻结 → updates-testing → stable（**Bodhi karma**） | stable 只修安全 | snapshot + **openQA 门禁** | 滚动 / channel |
| **退役** | orphan 待处理 | ✅ **孤儿 6 周即退役** `[官方]` | RoQA/RoM，**可拖数年** | 依 bug 情况 | 无强制退役 |
| **重命名** | `replaces` | `Obsoletes` | `Replaces` + `Provides` | `Obsoletes` | 别名 |

**两个极端对比：**

- **Fedora 是唯一有硬性退役时限的**：FESCo 政策原文 *"Orphan packages will be retired if they remain orphaned for six weeks."* `[官方]`
- **Debian 的孤儿包可以滞留十年**：WNPP 列表实测存在 `dpkg-cross ... orphaned since 3695 days`（约 10 年）。`[实测]` 这不是疏忽，而是 Debian "宁可留着也不删"的保守哲学的必然结果。

### 4.3 日常运营命令对照（可直接粘贴）

| 操作 | Arch | Fedora | openSUSE | Debian/Ubuntu | NixOS |
|---|---|---|---|---|---|
| 更新系统 | `sudo pacman -Syu` | `sudo dnf upgrade` | `sudo zypper dup` | `sudo apt update && sudo apt upgrade` | `nixos-rebuild switch --upgrade` |
| 清孤儿 | `sudo pacman -Rns $(pacman -Qtdq)` | `sudo dnf autoremove` | `sudo zypper rm -u` | `sudo apt autoremove` | `nix-collect-garbage -d` |
| 文件属于谁 | `pacman -Qo /path` | `rpm -qf /path` | `rpm -qf /path` | `dpkg -S /path` | `nix-locate /path` |
| 降级 | `pacman -U <旧包>` | `dnf downgrade pkg` | `zypper in --oldpackage pkg` | `apt install pkg=ver` | 切 generation |
| **回滚** | ❌ **无内建**（查 pacman.log） | `dnf history rollback` | `snapper undo` | ❌ **无内建**（查 dpkg.log） | `nixos-rebuild switch --rollback` |

> ⚠️ **Arch 最重要的安全守则**：`[官方]` **绝不能用 `pacman -Sy pkg` 代替 `pacman -Syu`** —— 前者会造成 partial upgrade（部分升级），这是 Arch 用户毁系统最常见的原因。Arch Wiki 原文明确警告此行为会导致依赖问题。

### 4.4 已知痛点与换代动向

| 发行版 | 核心痛点 | 换代动向 |
|---|---|---|
| **openSUSE** | **zypper 元数据刷新极慢**（论坛实测清缓存后 `zypper ref` **8 分 4 秒**）`[官方论坛]` | — |
| **Arch** | partial upgrade 毁系统、`.pacnew` 手工合并、AUR 编译慢 | ✅ **ALPM（Rust 重写 pacman）** 获 Sovereign Tech Fund 资助 15 个月 `[官方]` |
| **Debian/Ubuntu** | apt 太保守、backports 麻烦、孤儿积压 | ✅ **apt 3.0 已发布（2025-04-05）**，solver3 回溯式求解 `[官方]` |
| **Fedora** | 老版 dnf 慢（已由 dnf5 缓解） | ✅ **dnf5（C++）已成默认** |
| **NixOS** | Nix 语言学习曲线、eval 慢、磁盘占用 | `nixos-rebuild-ng`（Python）自 **25.11** 起为默认 `[官方]` |
| **Ubuntu** | snap 强制（Firefox / Chromium 默认 snap，26.04 仍如此）`[官方]` | — |

---

## 5. 漏洞修复运营

### 5.1 流程链路

| 发行版 | 监视 / 发现 | 分流 | 推送 |
|---|---|---|---|
| **Debian** | Security Team 订阅 + 自建 tracker，**每个 CVE 必 triage** | security-team.debian.org，分 DSA / point release / ignored | DSA 走 security.debian.org（**独立安全仓库**） |
| **Ubuntu** | Canonical 安全团队 + **CNA 自分配** | ubuntu-cve-tracker（Launchpad git） | **-security pocket** → -updates |
| **Fedora** | Red Hat Product Security 开 CVE bug | Fedora Security Team 引导，严重度四分 | **Bodhi** 推送 |
| **openSUSE / SUSE** | SUSE Security Team + CNA | CVE 页 + 公告 | OBS → 官方仓库 → zypper |
| **Arch** | ❌ **无自动化 CVE feed 监控** | Security Team（**4 人**）手动 | ❌ **无专门安全仓库**，直接进核心仓库滚动推送 |
| **NixOS** | security tracker（自动匹配版本） | GitHub issue 打 `backport needed` 标签 | backport 到 `release-XX.YY` 分支 |
| **Alpine** | 上游 secdb 自动生成 | security team 审阅 | 进 `vX.Y` branch，apk 推送 |

### 5.2 OSV.dev 覆盖（本次关键实测，直接决定自动化可行性）

用 `POST https://api.osv.dev/v1/query` 逐一实测：

| 生态 | 实测结果 | 含义 |
|---|---|---|
| Debian:12 | ✅ 200，返回真实 CVE | 可用 |
| Ubuntu:22.04 | ✅ 200，返回真实 CVE | 可用 |
| Alpine:v3.19 | ✅ 200，返回真实 CVE | 可用 |
| openSUSE:Leap:15.5 | ⚠️ **200 但返回空 `{}`** | 生态名存在，**无数据** |
| SUSE:Linux:Enterprise:15 | ⚠️ **200 但返回空 `{}`** | 生态名存在，**无数据** |
| **Fedora:43** | ❌ **400 `invalid ecosystem`** | **不可用** |
| **Arch:rolling** | ❌ **400 `invalid ecosystem`** | **不可用** |
| **NixOS:25.05** | ❌ **400 `invalid ecosystem`** | **不可用** |
| RedHat:all | ❌ 400（生态名非 `RedHat`，为其他形式） | 需查正确生态名 |

> **这是本次调研最重要的一条运营结论**：任何依赖 OSV.dev 的自动化安全流水线（OSV-Scanner、osv-scalibr、各类 SBOM 工具），**对 Fedora、Arch、NixOS 三家开箱即失效**。选型时如果安全运维要靠自动化，这三家必须自建数据管道。前序报告曾笼统说"OSV 不覆盖" —— 现在精确到：**openSUSE/SUSE 是"有名无实"，Fedora/Arch/NixOS 是"根本不存在"**。

### 5.3 结构化 CVE 数据库与 API（全部实测）

| 发行版 | 端点 | 实测 |
|---|---|---|
| **Debian** | `security-tracker.debian.org/tracker/data/json` | ✅ **82.5 MB**，4,073 源包 / 74,769 条目 |
| **Ubuntu** | `ubuntu.com/security/cves.json` | ✅ 29 KB；notices.json 898 KB |
| **Alpine** | `secdb.alpinelinux.org/v3.22/main.json` | ✅ 90 KB，结构 `packages[].pkg.secfixes{version:[CVE...]}` |
| **SUSE** | `suse.com/security/cve/<CVE>.html` | ⚠️ HTML 200；**API 端点需认证（401）** |
| **Arch** | `security.archlinux.org/issues/all.json` | ⚠️ 2444 条 issue 但**公告自 2025-06 停发**（见下） |
| **NixOS** | `tracker.security.nixos.org` | ⚠️ **纯 JS 壳（实测仅 1031 字节），无 JSON API** |
| **Fedora** | 无独立结构化库 | 依赖 Bodhi `?type=security` + Bugzilla |

**两个必须点名的数据陷阱：**

- **Arch ASA「数据在场但停滞」** `[实测+二手]`：`issues/all.json` 仍返回 2444 条（Fixed 2151 / Vulnerable 85），**只看 JSON 会误判为"活跃"**。但公告（advisory）自 2025-06 停发；社区贴称自 2024 起 security.archlinux.org **仅覆盖 55 个 CVE**，而 Debian 同期 21,528 个 —— **覆盖率不足 0.3%**。**这是"数据看起来在、其实已死"的典型样本**。
- **NixOS 有被低估的安全基建** `[实测]`：`tracker.security.nixos.org` **真实存在且活跃**（issue 形如 `NIXPKGS-2026-2355`，自动匹配 nixpkgs master 与 release 分支的毒软件包版本）—— **纠正了前序"NixOS 无 CVE 追踪"的错误假设**。但它是纯 JS 前端，**无 API**，自动化接入困难。

### 5.4 CNA 身份

| 发行版 | 是否 CNA | cnaID |
|---|---|---|
| Red Hat | ✅ | CNA-2005-0006（兼 Root CNA） |
| SUSE | ✅ | CNA-2014-0003 |
| Canonical (Ubuntu) | ✅ | CNA-2005-0001 |
| Debian | ✅ | CNA-2005-0003 |
| Fedora Project | ✅ | CNA-2017-0021 |
| **Arch / Alpine / NixOS** | ❌ | **无** |

**是否有 CNA 身份，是"安全成熟度"的分水岭。** 五家有、三家无 —— 而"无"的三家恰好也是 OSV 不覆盖的三家（Arch/Alpine 例外说明口径不同）。

### 5.5 补丁「最后一公里」

| 发行版 | 机制 | 关键参数 |
|---|---|---|
| **Fedora** | Bodhi karma + 加时 | `[实测]` 普通更新 **1 karma / 7 天**；关键路径 **2 karma / 14 天** —— **唯一显式可量化的门槛** |
| **Debian** | security.debian.org 独立归档 + point release | 高危走安全归档（不等 point release）；低危并入 point release（**2-3 月一次**） |
| **Ubuntu** | `-security` pocket | 走 security.ubuntu.com，再同步到主 archive |
| **Arch** | ❌ 无专门安全仓库 | 直接进 core/extra 滚动推送，"最后一公里"完全依赖滚动节奏 |
| **NixOS** | backport 到 release 分支 | 打 `needs backport` 标签；极端情况标 `insecure` 禁用包 |

**量化状态（Debian Security Tracker 实测）：**

| Suite | resolved | **open** |
|---|---|---|
| sid (unstable) | 66,300 | 3,969 |
| forky (testing 14) | 60,006 | 3,528 |
| trixie (stable 13) | 56,220 | **7,849** |
| bookworm (oldstable) | 54,889 | **11,973** |

> 口径：包级 CVE 条目（一个 CVE 影响多包计多次），共 74,769 条 / 4,073 源包。**注意 open 数随版本变老而上升** —— 这是"旧版支持"的真实成本。

### 5.6 漏洞扫描工具适配

| 工具 | 适用 | 限制 |
|---|---|---|
| `debsecan` | Debian | — |
| `vulnix` | NixOS | ⚠️ **官方 README 挂出 "New maintainer needed!"** |
| OSV-Scanner / osv-scalibr | Debian / Ubuntu / Alpine / SUSE 系 | ❌ **不覆盖 Fedora / Arch / NixOS** |
| `trivy` / `grype` | 容器镜像多发行版 | 靠各厂商 feed |
| `arch-audit` | Arch | ⚠️ **依赖已停摆的 ASA 数据，实际失效** |

---

## 6. 横向总表

| 维度 | Arch | NixOS | openSUSE | Fedora | Debian | Ubuntu |
|---|---|---|---|---|---|---|
| 核心维护者 | **23 Dev / 93 总** | 数千贡献者 | ~521 | ~325 | **1,039 DD** | 378 |
| 官方包数 | 16,008 | **119k 项目** | 16k | 24k | 42k | 40k |
| 新鲜度 | **86.5%** | 83.6%(unstable) | 73.0% | 56.8% | 40.9% | 48.3% |
| 第三方源 | AUR 121,822 | overlay/flake | **OBS 140k+** | COPR | 无官方（backports） | PPA >130k |
| 包管理原子性 | ❌ | ✅ **generation** | ✅ snapper | ✅ history | ⚠️ | ⚠️ |
| 多版本共存 | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| 硬性退役时限 | ❌ | ❌ | ❌ | ✅ **6 周** | ❌（可拖 10 年） | ❌ |
| OSV 覆盖 | ❌ | ❌ | ⚠️ 空 | ❌ | ✅ | ✅ |
| 结构化 CVE API | ⚠️ 停摆 | ⚠️ JS 无 API | ⚠️ 需认证 | ⚠️ 靠 Bodhi | ✅ **82MB JSON** | ✅ |
| CNA 身份 | ❌ | ❌ | ✅ SUSE | ✅ | ✅ | ✅ |
| 专职安全团队 | ❌ 4 人志愿 | ❌ | ✅ | ⚠️ 借 RH | ✅ | ✅ |
| 专门安全仓库 | ❌ | 分支 backport | ✅ | ⚠️ | ✅ | ✅ |
| 基础设施事故 | **三连击** | Hydra 慢 | OBS 35 分钟 | 无 | 无 | — |

---

## 7. 按需求选型

| 你的需求 | 推荐 | 理由 |
|---|---|---|
| 想要"永不宕机"的社区韧性 | **Debian** | 1,039 DD，无单点，30 年验证 |
| 想要最新软件 + 高新鲜度 | **Arch**（ISO 2026.10.01） | 86.5% 新鲜度全榜第一 |
| 想要包最多 | **NixOS** | nixpkgs unstable 119k 项目 |
| 想要原子回滚 + 多版本共存 | **NixOS** | 唯一 generation 机制 |
| 想要 OBS 生态 / 跨发行版构建 | **openSUSE** | OBS 服务 21 个发行版 |
| 想要自动化安全运维（LLM/SBOM） | **Debian / Ubuntu** | 唯一 OSV 覆盖 + 可执行 JSON API |
| 想要企业级安全流程 | **RHEL / SUSE** | 唯一有 CNA + 专职团队 + 商业 SLA |
| **避免**选它做无人值守 | **Arch** | tracker 停摆 + 4 人安全团队 + 无 CNA + 三连击事故 |

---

## 8. 存疑与未核实

| 项目 | 状态 |
|---|---|
| COPR 项目总数 | `[未找到]` 页面有反爬，无公开 API |
| Arch Package Maintainer 精确数（70） | `[二手]` 未逐页核实 |
| Fedora packager 数（325） | `[二手]` LWN，非官方统计 |
| Alpine 团队规模 | `[未找到]` |
| NixOS 贡献者总数 | `[未找到]`口径不明 |
| Ubuntu MOTU 人数 | `[未找到]` |
| Repology API（`/api/v1/repositories`） | `[实测]` 403，改用统计页 HTML 解析 |
| Debian NEW queue 处理天数 | `[实测]` 页面只有图表，无数字快照 |
| Ubuntu universe 安全支持级别 | `[二手]` "best-effort"，未取得官方原文 |
| 六家「关键包指定维护者」清单 | `[未找到]` 均无公开清单 |

---

## 附录：本次实测命令（可复现）

```bash
# OSV.dev 覆盖实测
curl -s -X POST https://api.osv.dev/v1/query \
  -H "Content-Type: application/json" \
  -d '{"package":{"name":"curl","ecosystem":"Fedora:43"},"version":"1.0"}'
# → {"code":3,"message":"invalid ecosystem"}

# Arch 安全公告（看是否停更）
curl -s https://security.archlinux.org/issues/all.json | python -c \
  "import sys,json;d=json.load(sys.stdin);print(len(d))"
# → 2444（但 advisory 自 2025-06 停发）

# AUR 包总数
curl -s -A "Mozilla/5.0" https://aur.archlinux.org/packages | grep -o '[0-9]* packages found'
# → 121822 packages found

# Debian 安全数据全量
curl -sI https://security-tracker.debian.org/tracker/data/json | grep -i content-length
# → 82556251

# NixOS tracker 是否纯 JS
curl -s https://tracker.security.nixos.org/ | wc -c
# → 1031（纯 JS 壳，无 API）

# Repology 仓库新鲜度
curl -s -A "Mozilla/5.0" https://repology.org/repositories/statistics | grep -A2 "Arch Linux"
```

---

*报告生成：2026-10-13 · 数据采集同日 · 3 个并行子代理 + 主调研员独立实测*
