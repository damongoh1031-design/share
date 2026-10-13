# 各发行版社区全面调研：打包质量 · 质量规范 · 管理层 · 社区规模 · 包维护 · 漏洞速度 · 未来前景

**调研日期**：2026-10-12
**调研对象**：Arch Linux、NixOS、openSUSE、Fedora、Debian、Ubuntu（+ Alpine / Gentoo 作参照）
**方法**：3 个并行子代理按「组织层 / 工程层 / 安全层」分组 + 主调研员独立核实（Arch 官方 API、openQA API、Debian 官方公告、Repology API 可达性测试）
**核实标记**：**[独立核实]** = 主调研员用官方 API/页面直接验证 ｜ **[子代理]** = 来自子代理报告，未经主调研员独立验证 ｜ **[二手]** = 新闻/博客/论坛 ｜ **[未找到]** = 无公开数据

---

## 0. 七维总览（结论先行）

| 维度 | 第一名 | 第二名 | 明显落后 |
|---|---|---|---|
| **治理稳健度** | Debian（纯社区 + 年度选举） | Fedora | **NixOS（连续治理危机）** |
| **社区规模** | Debian（1,039 投票权 DD） | NixOS（nixpkgs 贡献者最多） | **Arch（23 Dev + 70 PM）** |
| **打包质量体系** | openSUSE（openQA 650 测试套件）／Debian（lintian 1,485 项） | Fedora（CI gating） | **Arch（仅 namcap，非强制）** |
| **质量规范完备度** | Debian Policy Manual（最完备） | Fedora Packaging Guidelines | Arch（社区规范，执行弱） |
| **包维护健康度** | **Fedora（唯一有硬性退役时限：6 周）** | Arch（孤儿仅 250） | openSUSE（无公开数据） |
| **漏洞响应** | **Ubuntu／SUSE（专职团队 + 结构化数据）** | Debian（Sub-CNA + 完整 tracker） | **Arch（9 人志愿者 + tracker 停更）** |
| **未来前景** | Ubuntu（LTS 到 2031）／Debian | Fedora（有路线图） | **NixOS（治理 + 资金双危机）** |

**三条最重要的发现**：

1. **「哪个发行版补丁更快」这个问题没有可信答案。** 唯一尝试公开跨发行版 time-to-patch 数据的服务（Vulnpatch）**已主动撤回全部数字**，理由是方法学缺陷。任何声称「A 比 B 快 N 天」的横向结论都应视为不可信。
2. **NixOS 是本次调研中治理风险最高的社区**：2025-09 版主团队 5/7 辞职 → 2026-08 Nixpkgs 核心团队解散 → 基金会连续两年亏损（权益从 €248,993 降到 €168,111）。
3. **Arch 有两个新增风险**：2026-06 AUR 供应链事件（400+ 包被劫持）、2026-08 起 AUR **暂停「包认领」功能**。

---

## 1. 治理与管理层现状

### 1.1 治理模型对照

| 发行版 | 治理模型 | 最高决策体 | 与商业实体关系 |
|---|---|---|---|
| **Arch** | 社区自治 + 单一负责人 | **Project Leader**（**无「理事会」这一机构**） | 财务经 SPI 托管 |
| **NixOS** | 基金会 + 选举委员会 | NixOS Foundation + Steering Committee | 荷兰 Stichting 基金会 |
| **openSUSE** | 社区 Board + 赞助方 | Board（5 名选举 + 1 名主席） | 主席由 SUSE 任命 |
| **Fedora** | 社区 + 公司深度参与 | Council（战略）/ FESCo（技术） | Red Hat 持 Council 3 个常任席位 |
| **Debian** | 纯社区自治 | DPL + Technical Committee | 资金由 SPI 等托管 |
| **Ubuntu** | 公司主导 | Canonical + Community Council | Canonical 全资主导 |

> ⚠️ **修正一个常见前提错误**：**Arch 没有「Arch Council」这一机构**。最高负责人是 Project Leader，职责含无共识时决策、社区领导、CoC 执行、与 SPI 处理财务。很多二手资料会误称「Arch 理事会」。

### 1.2 人事与选举（2026）

| 发行版 | 最新选举 | 结果 | 投票率 |
|---|---|---|---|
| **Debian** | DPL 2026 | **Sruthi Chandran**（**无对手**） | **347 / 1,039** Developers **[独立核实]** |
| **Arch** | Project Leader 2026-06-04 | Levente "anthraxx" Polyák **连任**（任期 2 年，2 名候选人） | **[子代理]** |
| **openSUSE** | Board 第 19 届（2026-03-09） | Simon Lees、Shawn W Dunn 当选 | **162 / 521** 成员 **[子代理]** |
| **Fedora** | F44（2026-06-13） | Council 2 席 / 204 投票人；FESCo 5 席 / 199 投票人 | **[子代理]** |

**Debian DPL 已独立核实**：`bits.debian.org/2026/04/dpl-elections-2026.html`（2026-04-20）原文确认 Sruthi Chandran 当选，347/1,039 Developers 用 Condorcet 方法投票，任期 2026-04-21 ~ 2027-04-20，前任 Andreas Tille 任职两年。她也是**首位女性、首位亚洲 DPL**（[二手] opendatakerala.org 2026-04-21）。

**openSUSE 主席变动**：2026-05-07 Gerald Pfeifer 卸任，Jeff Mahoney 接任；2026-06-24 Ihno Krumreich 补缺至 2026 年底 **[子代理]**。

### 1.3 NixOS 治理危机完整时间线（本次调研最重要的组织层发现）

| 日期 | 事件 | 来源 |
|---|---|---|
| 2024-04-21 | 匿名 + 署名者公开信，指控领导层危机 | [二手] LWN |
| **2025-09-27** | **Moderation team 7 人中 5 人立即辞职**，抗议 Steering Committee 干预 | [子代理] Discourse |
| **2026-08-07/08** | **Nixpkgs 核心团队解散**（成立仅 10 个月；成员 alyssais、emilazy），理由：SC 微观管理、沟通失灵、授权不清、倦怠。此前曾 onboard 19 名新 committer | [子代理] Discourse |
| 2026-09-22 | 宣布**第三次** SC 选举，投票期 2026-10-15 ~ 11-01；资格为过去 4 年 ≥25 commits 或 ≥1 merged PR | [子代理] Discourse |

**这是三次连续事件，不是孤立事故。** 且第三次 SC 选举的投票期（2026-10-15 起）**尚未开始** —— 也就是说 NixOS 在本报告发布时**处于治理空窗期**。

### 1.4 Debian 的 LLM 治理决议

**GR-2026-002「LLM usage in Debian」投票结果（2026-08-30）**：鼓励尽量避免 LLM、偏好人类贡献 **[子代理]** `debian.org/vote/2026/`。这是发行版层面对 AI 的正式治理表态（Fedora 亦有类似的《AI-Assisted Contributions Policy》，2025-10-24 批准）。

---

## 2. 社区规模

### 2.1 可量化指标

| 发行版 | 指标 | 数值 | 核实 |
|---|---|---|---|
| **Arch** | Developers | **23** | **[独立核实]** archlinux.org/people/developers/ |
| Arch | Package Maintainers | 70 | [子代理] |
| Arch | Support Staff | 49 | [子代理] |
| **Debian** | 有投票权 Developers | **1,039** | **[独立核实]** bits.debian.org |
| Debian | 近 12 个月贡献者 | 1,384 人 / 31 个团队 | [子代理] contributors.debian.org |
| Debian | 2025 年新增 | 22 DD + 26 DM | [子代理] SPI Annual Report |
| **Fedora** | Packagers | **约 325**（2026 年初约 350） | [二手] LWN |
| Fedora | Count Me 周活系统 | 约 100 万（+9% YoY） | [二手] LWN |
| **openSUSE** | Members | 约 521 | [子代理] |
| **NixOS** | 贡献者总数 | **未找到** | — |
| **Ubuntu** | Ubuntu Members | 378 直接 / 584 总计 | [子代理] Launchpad |
| Ubuntu | MOTU 人数 | **未找到** | — |

### 2.2 规模量级对比（关键洞察）

| 发行版 | 核心维护者规模 | 量级 |
|---|---|---|
| Debian | 1,039 DD + 1,384 贡献者 | **千人级** |
| Fedora | ~325 packager | **百人级** |
| openSUSE | ~521 members | **百人级** |
| NixOS | 未找到总数（nixpkgs 包数 >80,000） | 未知 |
| **Arch** | **23 Dev + 70 PM = 93 人** | **百人以下** |
| Ubuntu | 378 Ubuntu Members（+ Canonical 雇员） | 百人级 |

**Arch 是六大中核心维护者最少的**，但管着 16,008 个官方包 —— 人均约 172 包（详见第 5 节）。

**Fedora packager 长期下降趋势**（[二手] LWN）：2020 初 >420 → 2023 约 410→340 → 2026 初 350→325。这是本次调研中最明确的**人力衰退信号**。

---

## 3. 打包质量

### 3.1 包数量与新鲜度（Repology，2026-10-12）

| repo | 总包数 | Outdated | Outdated 占比 | Problems |
|---|---|---|---|---|
| Arch | 15,516 | 2,110 | **13.6%** | 911 |
| NixOS unstable | **149,566** | 18,958 | **12.7%** | 3,700 |
| openSUSE Tumbleweed | 17,270 | 4,503 | 26.1% | 1,822 |
| Fedora 42 | 31,028 | 12,706 | 40.9% | 2,965 |
| Debian 13 | 38,684 | 17,989 | 46.5% | 3,284 |
| Ubuntu 24.04 | 39,336 | 20,553 | **52.3%** | 4,173 |

⚠️ **重要读法说明（不要误读这张表）**：
- Fedora 42 / Debian 13 / Ubuntu 24.04 是**固定版本快照**，outdated 占比天然偏高，**不代表维护质量差**
- 只有滚动版（Arch / NixOS unstable / openSUSE TW）之间可比
- **Repology 官方警告 openSUSE 与 Ubuntu 的 repo 数据质量差**（版本造假、无源码链接），**两者已被列入「考虑移除」**
- ⚠️ **本表未经主调研员独立核实**：Repology API 对本环境返回 **403 Forbidden**（带 UA 亦被拒），数据来自子代理读取网页

其他口径（[子代理]）：Arch 官方仓库自报 **16,008** 包；Fedora 全分支共 **82,747** 包。

### 3.2 自动化质量检查工具

| 发行版 | 工具 | 规模 | 是否强制 |
|---|---|---|---|
| **Arch** | `namcap` | 127 个 tag（E/W/I 三级） | ❌ **非强制**，人工运行 |
| **Fedora** | `rpmlint` + `fedora-review` | rpmlint 38 个 check 模块 | ✅ **review 必跑** |
| **Debian** | `lintian` | **1,485 个 tag/检查项** | ❌ 可 override |
| **openSUSE** | `rpmlint` + `brp-check-suse` | 构建期自动 | ⚠️ 部分 error 阻断构建 |

### 3.3 QA / CI 覆盖率

| 发行版 | 体系 | 强度 |
|---|---|---|
| **openSUSE** | **openQA** | **最强**：**650 个 test suite、114 台机器** **[独立核实]** |
| **Fedora** | Zuul-based CI + tmt + Bodhi **gating** | 强：测试不通过则**阻断更新发布** |
| **Debian** | piuparts + autopkgtest + lintian | 中：**均非上传硬门槛** |
| **Arch** | 仅 namcap | **最弱**：无 CI 强制，AUR 无自动检查 |

**openQA 数据已独立核实**：`openqa.opensuse.org/api/v1/test_suites` 返回 **650** 个测试套件，`/api/v1/machines` 返回 **114** 台机器（2026-10-12）。覆盖 Tumbleweed / Leap / ARM / RISC-V / s390x，是**发行版级全系统安装测试** —— 这是 openSUSE 在打包质量维度最硬的护城河。

### 3.4 可复现构建（reproducible builds）

| 发行版 | 状态 |
|---|---|
| **Debian** | forky/amd64 **95.9%** 可复现、0.9% FTBFS；unstable/amd64 94.8%、1.6% FTBFS |
| Arch | reproducible.archlinux.org（rebuilderd），**无公开百分比** |
| NixOS | reproducible.nixos.org，**仅方法说明，无覆盖率数字** |
| **openSUSE** | 测试数据**停留在 2018-12-13**，实质停更 |
| **Fedora** | 仅到 **fedora-23** 时代的页面，早已停更 |

**只有 Debian 有公开、可信、持续更新的可复现构建覆盖率。**

### 3.5 FTBFS（构建失败）比例

| 发行版 | 数据 |
|---|---|
| Debian | **0.9%–1.8%** |
| Fedora | 有 **Koschei** 持续跟踪：tracked **180,316** 包、总构建 1,341,362 次，但**未直接给出百分比** |
| Arch / openSUSE / NixOS | ❌ 无公开汇总 |

---

## 4. 质量规范

### 4.1 官方规范文档对照

| 发行版 | 规范文档 | 覆盖范围 | 执行力度 |
|---|---|---|---|
| **Arch** | Arch packaging standards / PKGBUILD 规范 | PKGBUILD 写法、目录、依赖、许可证 | 人工 review；namcap 非强制 |
| **Fedora** | Packaging Guidelines（**FPC** 维护） | 全 spec 规则、命名、宏、许可 | rpmlint + fedora-review **强制** + CI gating |
| **Debian** | **Debian Policy Manual v4.7.4.1**（**2026-03-31** 发布） | **全系统策略，最完备** | lintian 提示 + FTP-master/sponsor 人工审核 |
| **openSUSE** | openSUSE packaging guidelines + Packaging_checks | spec、rpmlint 规则 | OBS 构建期强制部分规则 |
| **NixOS** | nixpkgs `CONTRIBUTING.md`（54KB）+ RFC 流程 | 派生式打包、命名、meta | 人工 review + ofBorg CI |

**Debian Policy Manual 是六大中最完备的**，且版本化发布（4.7.4.1，2026-03-31）—— 这是一份有正式版本号的规范性文档，其他发行版的规范更接近「wiki 页面 + 惯例」。

### 4.2 规范演进（2025-2026）

| 发行版 | 变更 | 影响 |
|---|---|---|
| **Arch** | **2026-07-30 AUR 暂停「包认领（adoption）」功能**（第三波恶意接管攻击） | ⚠️ **AUR 治理出现信任危机** |
| Arch | RFC 0014：新 Package Maintainer 前两个月标记为 "junior" | 提高新人门槛 |
| **Debian** | Policy 4.7.4.1 发布（2026-03-31） | 规范更新 |
| Fedora | 推进治理现代化（Innovation Lifecycle 框架、贡献者投票资格重定义） | 治理调整 |

**Arch 的 AUR 认领停用是本年度最值得关注的规范层事件** —— AUR 是 Arch 生态的核心竞争力，而认领机制是 AUR 包能持续维护的基础。停用意味着**大量孤儿 AUR 包将无法被接管**。

---

## 5. 包的维护状况

### 5.1 孤儿包（orphan packages）

| 发行版 | 数量 | 核实 |
|---|---|---|
| **Arch** | **250**（官方仓库） | **[独立核实]** archlinux.org API（两种 limit 口径均为 250） |
| **Debian** | **1,070** orphaned + **100** RFA + **46** RFH | [子代理] debian.org/devel/wnpp/ |
| **Fedora** | ❌ 无公开汇总数字 | — |
| **openSUSE** | ❌ 无公开汇总（OBS 搜索需登录） | — |

> ⚠️ **修正子代理数据**：子代理报告称 Arch 有 **303** 个 orphan 包，主调研员用 Arch 官方 API 两种口径复核，实际为 **250**。以 250 为准。

### 5.2 维护者 : 包 比例

| 发行版 | 维护者数 | 官方包数 | **包 / 人** |
|---|---|---|---|
| **Arch** | 23 Dev + 70 PM = **93** | 16,008 | **约 172** |
| NixOS | 4,949（Repology） | 149,566 | 约 30 |
| Debian | 3,559（Repology） | 38,684 | 约 10.9 |
| Ubuntu | 3,365（Repology） | 39,336 | 约 11.7 |

> ⚠️ **两个子代理的数据互相矛盾**：子代理 2 称 Arch 有「17 Dev + 54 PM ≈ 71 人」，子代理 1 称「23 Dev + 70 PM」。主调研员**独立核实 Developers = 23**（archlinux.org/people/developers/），故采信 23 Dev + 70 PM = 93。**PM 数（70）未经独立核实。**

**Arch 的人均包数是六家中最集中的（约 172 包/人，是 Debian 的 16 倍）。** 这既是效率的体现（滚动版淘汰快），也是 bus factor 风险。

**关于「一人管几千包」**：Repology 未公开个人级数据，**未能核实**具体个案。Nixpkgs 因 149k 包 + 社区驱动，个别 maintainer 管数百包属常见，但无权威统计。

### 5.3 包的退役流程

| 发行版 | 流程 | 时限 |
|---|---|---|
| **Fedora** | 孤儿满 **6 周** → Rawhide/Branched 退役，留 `dead.package` 说明 | ✅ **唯一有硬性时限** |
| **Debian** | 长期孤儿 → 评估后由 FTP-master 从 unstable 移除 | 无明确时限 |
| **Arch** | 仓库包由 TU/Dev 决定；AUR 走 orphan/adopt（**当前 adoption 被禁用**） | 无明确时限 |
| **openSUSE / NixOS** | 无明确时限（NixOS 靠 PR 删除） | 无 |

**Fedora 的「6 周退役」是六家中最透明、最可预期的机制。**

### 5.4 关键包（critical path）维护

❌ **六家均无公开的「关键包指定维护者」清单。**

值得注意的动向：Debian 2026 GSoC 有一个项目叫 **DebNet: Visualising the Bus Factor** —— 用 UDD 数据构建包依赖图与维护者-包图，计算每个源码包的 **Bus Factor、Fragility Score、Dependency Impact**，目标正是**识别「被过少的人维护的关键包」**（[子代理] Debian GSoC 2026 项目列表）。这说明 Debian 已把这个问题正式立项。

---

## 6. 漏洞响应速度

### 6.1 核心结论：**不存在可信的跨发行版 time-to-patch 数据集**

这是本维度最重要的发现，也是本次调研最反直觉的结论。逐条核实：

| 来源 | 声称 | 实际 |
|---|---|---|
| **Vulnpatch** `time-to-fix` 基准 | 做跨发行版（NixOS/Debian/Arch/Alpine/Fedora/Ubuntu）补丁速度对比 | ❌ **所有 `medianDays` 已被主动撤回为 `null`**。作者原文理由：算法「把未修复的 CVE 丢弃（恰好是最慢的那批）、计时起点是服务首次观测到修复而非发行版发布时刻」，导致「**Debian 被渲染成最快，却拥有最低的修复率**」 |
| **WMP/cve-patch-duration** | 测量内核 CVE 上游修复→发行版发包天数 | ⚠️ 仅 1 次 commit（2026-05-20）、**0 star、未发布任何结果数据** |
| **ICSE 2026** 论文《Patch Sharing across Four Linux Distributions》 | 学术对比 | 给出**补丁跨发行版传播延迟中位数 530 天（Fedora↔Debian）**、169 天（Fedora↔openEuler）—— **但这是「维护补丁共享」，不是安全响应速度** |
| **Chainguard**《State of Trusted Open Source》(2025-12) | 商业报告 | 只讲**自家镜像** SLA（Critical <20h 均值、63.5% 24h 内），**不是发行版对比** |
| **Endor Labs / Wiz / Project Zero** | — | ❌ **未找到**针对发行版补丁速度的横向数据集 |
| commandlinux.com「Linux Security Patch Release Time Statistics 2026」 | 称企业级发行版关键补丁 24–48 小时内 | ⚠️ **无逐发行版数据**，系二手拼贴，可信度低 |

> **结论：CVE 公开 → 发行版发布补丁的「平均/中位天数」，目前没有可信、可复现、跨发行版的公开数据。** 唯一尝试公开该数据的服务已因方法学缺陷撤回数字。**任何声称「A 比 B 快 N 天」的横向结论都应视为不可信。**

### 6.2 漏洞公告机制

| 发行版 | 公告形式 | 机器可读源 |
|---|---|---|
| **Ubuntu** | USN（Ubuntu Security Notices） | ✅ `/security/notices.json` API + **OVAL + OSV + VEX**（三种 JSON 格式） |
| **Debian** | DSA（stable）/ DLA（LTS） | ⚠️ **无官方 REST API**；数据在 git 仓库 + Tracker 查询界面 |
| **Fedora** | Bodhi security update | ✅ RSS `/rss/updates/?type=security` + JSON API |
| **openSUSE** | openSUSE-SU / SUSE-SU | ⚠️ SUSE CVE 数据库页面，**非结构化 API** |
| **Arch** | **ASA（Arch Linux Security Advisory）** | ⚠️ 有 tracker `security.archlinux.org`，**但 ArchWiki 明确警告「The tracker is currently not updated」** |
| **NixOS** | `NIXPKGS-YYYY-NNNN` + GitHub Security Advisories | ✅ `tracker.security.nixos.org` |
| **Alpine** | **secdb** | ✅ **每日更新**的 JSON + YAML（按分支，如 `v3.19/main.yaml`） |
| Gentoo | GLSA | `glsa.gentoo.org` |

> ⚠️ **修正两处常见误判**：
> - **Arch 是有安全公告机制的**（ASA + 专用 tracker + `arch-security` 邮件列表 + 9 人志愿团队，需 2 人复核才发布）—— 并非「没有安全公告」。**但它的 tracker 当前停更**，这是真正的隐患。
> - **NixOS 也有完整公告机制**（tracker + GitHub Advisory + Discourse），并非「无公告」。

### 6.3 安全团队（是否专职）

| 发行版 | 团队性质 |
|---|---|
| **Ubuntu** | **Canonical 专职** Ubuntu Security Team（UCT 追踪器） |
| **SUSE/openSUSE** | **SUSE Security Team（商业公司专职）**，负责 SLES + Leap + Tumbleweed |
| **Debian** | Debian Security Team（**志愿者为主**，含 DSA/LTS 分工） |
| **Fedora** | **无独立专职团队**，由 Red Hat Product Security 覆盖 |
| **Arch** | **9 名志愿者**（无专职） |
| **NixOS** | 公开成员志愿者 |
| Alpine | 社区团队 |

**这是发行版间最本质的安全能力差异**：Ubuntu/SUSE 有**拿薪水的安全团队**，Arch/NixOS/Debian 靠志愿者。

### 6.4 漏洞覆盖范围（陷阱最多的一节）

| 发行版 | 纳入安全支持的包/版本 | 关键陷阱 |
|---|---|---|
| **Debian** | **仅 main** | ⚠️ **contrib / non-free / non-free-firmware 不受安全支持** |
| **Ubuntu** | Main/Restricted：5 年免费完整支持；**Universe/Multiverse：仅 "best-effort"** | ⚠️ **Universe 的完整支持需要 Ubuntu Pro（esm-apps）付费** |
| **Fedora** | 约 **13 个月**（当前版 + 前一版） | N-2 达 EOL |
| **Arch** | 仅 **core / extra / multilib**，随滚动更新 | **无固定支持窗口** |
| **NixOS** | stable 分支约 **7 个月**（如 26.05 支持至 2026-12-31） | 周期短 |
| **openSUSE** | Tumbleweed = 滚动（"lifetime forever"）；Leap = LTS | 两者差异大 |

### 6.5 OSV.dev 覆盖情况（数据基础设施成熟度指标）

| 状态 | 发行版 |
|---|---|
| ✅ **已覆盖** | **Debian**、**Alpine**（SecDB 转换）、**Ubuntu**、Rocky Linux、AlmaLinux |
| ❌ **未覆盖** | **Arch、Fedora、openSUSE、NixOS、Gentoo** |

**这直接反映梯队**：Debian / Alpine / Ubuntu 的安全数据**结构化、可被 OSV 消费**；Arch / NixOS / openSUSE / Fedora 缺乏标准化机器可读出口。对「用 LLM 做安全运维」的场景，这是硬约束。

### 6.6 CNA（CVE 编号机构）身份

| 发行版 | 是否 CNA |
|---|---|
| **Debian** | ✅ **Sub-CNA**（仅分配 Debian 自身漏洞的 CVE） |
| **Red Hat（含 Fedora）** | ✅ CNA，2025-02 起为 **CNA-LR（最后手段 CNA）** |
| **Linux 内核** | ✅ 2024-02 起自建 CNA（CVE 量激增 13 倍） |
| SUSE / Canonical | ✅ CNA（二手来源） |
| **Arch / Alpine / Gentoo / NixOS** | ❌ 未核实为 CNA |

### 6.7 安全支持周期（LTS）

| 发行版 | 周期 |
|---|---|
| **Ubuntu** | 5 年标准 + Pro 10 年（+ Legacy 15 年） |
| **Debian LTS** | 约 5 年（bullseye 已于 **2026-08-31** EOL） |
| **Fedora** | 约 13 个月 |
| **NixOS** | 约 7 个月 |
| **Arch / Tumbleweed** | **无 LTS** |

**社区发行版均无安全 SLA**；有 SLA 的是商业产品（Chainguard Critical 7 天、SUSE/RHEL 商业订阅）。

### 6.8 真实案例（注意：都无法给出「差几天」）

| 案例 | 披露 | 情况 |
|---|---|---|
| **xz 后门 CVE-2024-3094** | 2024-03-29 | Fedora Rawhide/40 与 openSUSE Tumbleweed 为「含毒」版本，**数小时内**回滚/降级；Debian stable 未受影响；Arch 未进入 stable。**精确小时数未见权威统计** |
| **regreSSHion CVE-2024-6387** | 2024-07-01 | Debian/Ubuntu/RHEL/SUSE/Alpine 等「数天内」发布补丁 |
| **glibc Looney Tunables CVE-2023-4911** | 2023-10-03 | 各发行版数天内跟进 |

**结构性差异（可推断，非实测）**：滚动发行版（Arch / Tumbleweed）在「上游已发包」类漏洞上**天然占优**（无 backport 等待）；但在「上游无修复」类漏洞上**依赖志愿者打包速度**，反而可能更慢。这个权衡**没有任何数据能证明哪边净胜**。

---

## 7. 未来发展前景

### 7.1 路线图与风险信号

| 发行版 | 路线图 / 方向 | 风险信号 |
|---|---|---|
| **Fedora** | 维持 6 个月周期（F44 于 2026-05 发布）；**AI Developer Desktop 获 Council 批准**；**Hummingbird**（容器化滚动）2026-05 宣布；Innovation Lifecycle 提案 | ⚠️ **packager 数持续下降**；探索 Open Collective 捐款以「扩大 Red Hat 预算之外的资助」 |
| **openSUSE** | **Slowroll 仍处 beta（2026-09）**；Aeon（只读系统，随 Tumbleweed 周期）；Kalpa（实验性 KDE MicroOS spin） | 未找到资金/人力危机的公开讨论 |
| **Debian** | Debian 14 **Forky**（testing，冻结/发布日期未定，**预计 2027**）；15 代号 = **Duke** | SPI 2025 审计财报约 2026-11 发布；**未找到资金危机** |
| **Ubuntu** | **26.04 LTS（2026-04-23 发布）支持至 2031-04**，Pro ESM 可至 10 年 | 未找到 |
| **Arch** | **无官方长期路线图**（一贯如此） | ⚠️ **2026-06-11 AUR 供应链事件（400+ 包被劫持）；2026-08 暂停 AUR 包收养** |
| **NixOS** | flakes 稳定化仍在进行（RFC 136 要求先稳定 CLI），**flakes 仍为实验特性** | ⚠️ **治理危机（见 1.3）；基金会连年亏损** |

### 7.2 资金状况（关键差异）

**NixOS Foundation —— 连续两年亏损，权益持续下降**：

| 年份 | 净收支 | 权益（累计） |
|---|---|---|
| 2023 | — | **€248,993** |
| 2024 | **−€55,862**（首次亏损） | €193,130 |
| 2025 | **−€25,019**（含 €38k 补缴 2021-23 公司税；剔除后 +€13,130） | **€168,111** |

**权益两年下降 €80,882（约 32%）。** 结合治理危机，NixOS 是本次调研中**组织风险最高的社区**。

**其他**：
- **Debian / SPI**：2025 审计财报约 2026-11 才发布（尚未出）
- **GNOME 基金会**（与 Fedora Workstation 相关）：2024-10 批准削减预算的财年方案（[二手] linuxiac）
- **Fedora**：正在探索 Open Collective 捐款渠道，暗示 Red Hat 预算之外的资金需求

### 7.3 参照：Gentoo / Alpine

- **Gentoo**：选举产生的 Council（7 席，年选）治理 **[二手]**
- **Alpine**：core team 治理，**2025-08 发布治理文档 v0.1b** —— 一个容器场景快速增长的发行版正在正式化治理

---

## 8. 综合判断：按需求选

| 你的优先级 | 推荐 | 理由 |
|---|---|---|
| **治理稳健 + 长期可预期** | **Debian** | 唯一「纯社区 + 年度选举 + 无商业主导」；Policy Manual 最完备；无资金危机 |
| **企业级安全响应** | **Ubuntu / SUSE** | 唯一有**拿薪水的专职安全团队**；结构化安全数据（OVS/OVAL/VEX）；LTS 到 2031 |
| **打包质量体系最强** | **openSUSE** | openQA 650 测试套件 + 114 机器（独立核实），唯一发行版级全系统安装测试 |
| **包新鲜度 + 规模** | **NixOS**（包最多，149k）／**Arch**（outdated 最低，13.6%） | ⚠️ 但 NixOS 有治理风险，Arch 有 AUR 风险 |
| **维护透明度** | **Fedora** | 唯一有硬性退役时限（6 周）+ CI gating + Koschei FTBFS 追踪 |
| **避免风险** | ⚠️ **NixOS**（治理 + 资金双危机）／**Arch**（AUR 停用认领） | — |

---

## 9. 存疑 / 未核实

### 主调研员独立核实并修正的项

| 项 | 子代理数据 | 独立核实结果 |
|---|---|---|
| **Arch orphan 包数** | 303 | ✅ **250**（Arch 官方 API，两种 limit 口径一致） |
| **Arch Developers** | 子代理 2 说 17；子代理 1 说 23 | ✅ **23**（archlinux.org/people/developers/） |
| **openQA test suites / machines** | 650 / 114 | ✅ **650 / 114**（openQA 官方 API） |
| **Debian DPL 2026** | Sruthi Chandran，347/1,039 | ✅ **完全一致**（bits.debian.org 官方） |

### 无法独立核实的项

| 项 | 原因 |
|---|---|
| **Repology 全部数字**（包数 / outdated / problems） | **Repology API 对本环境返回 403 Forbidden**（带 User-Agent 亦被拒）。数据来自子代理读网页，**未经独立验证** |
| **Arch Package Maintainers = 70 / Support Staff = 49** | Arch people 页面可抓但需精确解析，本轮未完成 |
| **Fedora packager ≈325** | 仅二手 LWN 来源 |
| **NixOS 贡献者总数** | 未找到 |
| **Ubuntu MOTU 人数** | 未找到 |
| **Ubuntu Community Council 2025-26 活跃度** | 未找到明确公开证据 |
| **Arch Project Leader 2026 选举详情** | 子代理来源，主调研员未独立核实官方公告页 |
| **openSUSE Board 162/521 投票率** | 子代理来源 |

### 结构性数据缺口（本身就是结论）

- **跨发行版 time-to-patch 数据集：不存在**（Vulnpatch 已撤回）
- **六家均无「关键包指定维护者」公开清单**
- **Fedora / openSUSE 的孤儿包总数：无公开数据**
- **Arch / NixOS 的可复现构建覆盖率：无公开数字**
- **个人级包维护量分布：无权威统计**

### 抓取失败说明
`wiki.archlinux.org`（Anubis PoW）、`build.opensuse.org`（PoW）、`repology.org/api`（403）、`manpages.opensuse.org`（返回空）在本环境不可程序化抓取。相关结论已改用等价来源（Arch 官方包库 API、openQA API、bits.debian.org、rpmfind 文件列表、GitHub API）并逐条标注可靠性。

---

## 附：一张表看懂

| | Arch | NixOS | openSUSE | Fedora | Debian | Ubuntu |
|---|---|---|---|---|---|---|
| 治理模型 | 社区自治 + Leader | 基金会 + 选举 SC | Board + SUSE | Council + FESCo + Red Hat | 纯社区 + DPL | Canonical 主导 |
| 核心维护者 | **93** | 未找到 | ~521 members | ~325 packagers | **1,039 DD** | 378 members |
| 官方包数 | 16,008 | **149,566** | 17,270 | 31,028(F42) | 38,684(D13) | 39,336(24.04) |
| Outdated 占比 | **13.6%** | 12.7% | 26.1% | 40.9%* | 46.5%* | 52.3%* |
| 质量工具 | namcap（非强制） | CONTRIBUTING + ofBorg | openQA（650 套件） | rpmlint 强制 + gating | lintian（1,485 项） | 同 Debian |
| 可复现构建 | 无数字 | 无数字 | 停更(2018) | 停更(F23) | **95.9%** | — |
| 孤儿包 | **250** | — | 无数据 | 无数据（6 周退役） | 1,070 | — |
| 安全团队 | **9 志愿者** | 志愿者 | **SUSE 专职** | Red Hat 代管 | 志愿者为主 | **Canonical 专职** |
| OSV.dev | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| CNA | ❌ | ❌ | ✅(二手) | ✅ | ✅ Sub-CNA | ✅(二手) |
| LTS 安全周期 | 无 | ~7 个月 | Leap LTS | ~13 个月 | ~5 年 | 5 年(+Pro 10) |
| 资金风险 | — | **连亏 2 年** | 未发现 | packager 下降 | 未发现 | — |

\* 固定版本快照，outdated 天然偏高，不可与滚动版直接比较。
