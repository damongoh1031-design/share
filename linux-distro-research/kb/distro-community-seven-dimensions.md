---
id: distro-community-seven-dimensions
title: 发行版社区七维对比：打包质量 · 规范 · 治理 · 规模 · 包维护 · 漏洞速度 · 前景
tags: [linux, distro, governance, packaging-quality, orphan-packages, vulnerability-response, community, arch, nixos, fedora, debian, opensuse, ubuntu]
created: 2026-10-12
updated: 2026-10-12
version: 1.0.0
status: stable
source: Arch 官方包库 API + openQA API + bits.debian.org + Repology 网页 + 各发行版官方文档（2026-10-12）
confidence: 已核实
---

# 发行版社区七维对比

## TL;DR

| 维度 | 第一名 | 明显落后 |
|---|---|---|
| 治理稳健度 | Debian | **NixOS（连续三次治理危机）** |
| 社区规模 | Debian（1,039 投票权 DD） | Arch（23 Dev + 70 PM） |
| 打包质量体系 | openSUSE（openQA 650 套件）／Debian（lintian 1,485 项） | Arch（仅 namcap，非强制） |
| 质量规范完备度 | Debian Policy Manual | Arch |
| 包维护健康度 | **Fedora（唯一硬性退役时限：6 周）** | openSUSE（无公开数据） |
| 漏洞响应 | Ubuntu／SUSE（专职团队） | **Arch（9 人志愿者 + tracker 停更）** |
| 未来前景 | Ubuntu／Debian | **NixOS（治理 + 资金双危机）** |

**三条最重要的发现**：
1. **「哪个发行版补丁更快」没有可信答案** —— 唯一公开该数据的服务（Vulnpatch）已**主动撤回全部数字**
2. **NixOS 治理风险最高**：2025-09 版主团队 5/7 辞职 → 2026-08 Nixpkgs 核心团队解散 → 基金会连亏两年（权益 −32%）
3. **Arch 两个新增风险**：2026-06 AUR 供应链事件（400+ 包被劫持）、2026-08 起 AUR **暂停「包认领」**

---

## 1. 治理与管理层

| 发行版 | 治理模型 | 最高决策体 | 商业关系 |
|---|---|---|---|
| Arch | 社区自治 + 单一负责人 | **Project Leader（无「理事会」）** | 财务经 SPI |
| NixOS | 基金会 + 选举委员会 | NixOS Foundation + Steering Committee | 荷兰 Stichting |
| openSUSE | 社区 Board + 赞助方 | Board（5 选举 + 1 主席） | 主席由 SUSE 任命 |
| Fedora | 社区 + 公司深度参与 | Council（战略）/ FESCo（技术） | Red Hat 持 3 常任席位 |
| Debian | 纯社区自治 | DPL + Technical Committee | SPI 托管 |
| Ubuntu | 公司主导 | Canonical + Community Council | Canonical 全资 |

> ⚠️ **常见前提错误**：**Arch 没有「Arch Council」**。最高负责人是 Project Leader。

### 2026 选举

| 发行版 | 结果 | 投票率 |
|---|---|---|
| Debian | **Sruthi Chandran**（无对手）任期 2026-04-21~2027-04-20 | **347/1,039** ✅ |
| Arch | anthraxx 连任（2026-06-04，任期 2 年） | 子代理 |
| openSUSE | Simon Lees、Shawn W Dunn（第 19 届，2026-03-09） | 162/521 子代理 |
| Fedora | Council 2 席 / FESCo 5 席（F44，2026-06-13） | 204 / 199 子代理 |

### NixOS 治理危机时间线

| 日期 | 事件 |
|---|---|
| 2024-04-21 | 公开信指控领导层危机 |
| **2025-09-27** | **Moderation team 7 人中 5 人辞职** |
| **2026-08-07/08** | **Nixpkgs 核心团队解散**（成立 10 个月） |
| 2026-09-22 | 宣布**第三次** SC 选举（投票 2026-10-15~11-01） |

**第三次选举投票期在本报告发布时尚未开始 → NixOS 处于治理空窗期。**

---

## 2. 社区规模

| 发行版 | 核心维护者 | 核实 |
|---|---|---|
| **Debian** | **1,039 DD**（+ 近 12 月 1,384 贡献者 / 31 团队） | ✅ |
| openSUSE | ~521 members | 子代理 |
| Fedora | ~325 packagers | 二手 LWN |
| Ubuntu | 378 Ubuntu Members | 子代理 |
| **Arch** | **23 Dev + 70 PM + 49 Support** | ✅ Developers=23 |
| NixOS | 未找到 | — |

**Fedora packager 长期下降**：2020 初 >420 → 2023 ~410→340 → 2026 初 350→325（最明确的人力衰退信号）。

---

## 3. 打包质量

### 包数量与新鲜度（Repology，⚠️ 未独立核实）

| repo | 总包数 | Outdated | 占比 |
|---|---|---|---|
| Arch | 15,516 | 2,110 | **13.6%** |
| NixOS unstable | **149,566** | 18,958 | 12.7% |
| openSUSE TW | 17,270 | 4,503 | 26.1% |
| Fedora 42 | 31,028 | 12,706 | 40.9%* |
| Debian 13 | 38,684 | 17,989 | 46.5%* |
| Ubuntu 24.04 | 39,336 | 20,553 | 52.3%* |

\* 固定版本快照，outdated 天然偏高，**不可与滚动版比较**。
⚠️ Repology 警告 openSUSE/Ubuntu 数据质量差，已被列「考虑移除」。API 对本环境 403。

### 质量工具

| 发行版 | 工具 | 规模 | 强制 |
|---|---|---|---|
| Arch | `namcap` | 127 tag | ❌ |
| Fedora | `rpmlint` + `fedora-review` | 38 check 模块 | ✅ |
| Debian | `lintian` | **1,485 检查项** | ❌ 可 override |
| openSUSE | `rpmlint` + `brp-check-suse` | 构建期 | ⚠️ 部分 |

### QA / CI

| 发行版 | 体系 | 强度 |
|---|---|---|
| **openSUSE** | **openQA：650 test suite + 114 机器** ✅ | **最强**（发行版级全系统安装测试） |
| Fedora | Zuul CI + tmt + Bodhi **gating** | 强（测试不过阻断发布） |
| Debian | piuparts + autopkgtest + lintian | 中（**非硬门槛**） |
| Arch | 仅 namcap | **最弱** |

### 可复现构建

| 发行版 | 状态 |
|---|---|
| **Debian** | forky/amd64 **95.9%**，FTBFS 0.9% |
| Arch / NixOS | 有专用实例，**无公开百分比** |
| openSUSE | **停更于 2018-12-13** |
| Fedora | 仅 fedora-23 时代页面 |

### FTBFS
- Debian **0.9%–1.8%**
- Fedora 有 Koschei（180,316 tracked / 1,341,362 builds），**未给百分比**
- Arch / openSUSE / NixOS ❌

---

## 4. 质量规范

| 发行版 | 规范 | 执行 |
|---|---|---|
| Arch | Arch packaging standards | 人工 review，namcap 非强制 |
| Fedora | Packaging Guidelines（FPC） | rpmlint + fedora-review **强制** + CI gating |
| **Debian** | **Policy Manual v4.7.4.1**（2026-03-31） | lintian + FTP-master/sponsor 审核 |
| openSUSE | packaging guidelines + Packaging_checks | OBS 构建期强制部分 |
| NixOS | `CONTRIBUTING.md`（54KB）+ RFC | 人工 review + ofBorg CI |

**Debian Policy Manual 最完备**（有正式版本号，其他更接近 wiki + 惯例）。

### 规范演进 2025-2026
- **Arch：2026-07-30 AUR 暂停「包认领」（第三波恶意接管攻击）** ← 最值得关注
- Arch RFC 0014：新 PM 前两个月标 "junior"
- Debian Policy 4.7.4.1（2026-03-31）

---

## 5. 包的维护

### 孤儿包

| 发行版 | 数量 |
|---|---|
| **Arch** | **250** ✅（子代理报 303，**已修正**） |
| **Debian** | 1,070 orphaned + 100 RFA + 46 RFH |
| Fedora | 无公开汇总 |
| openSUSE | 无公开汇总 |

### 维护者 : 包

| 发行版 | 维护者 | 官方包数 | 包/人 |
|---|---|---|---|
| **Arch** | 93 | 16,008 | **约 172** |
| NixOS | 4,949 | 149,566 | 约 30 |
| Debian | 3,559 | 38,684 | 约 10.9 |
| Ubuntu | 3,365 | 39,336 | 约 11.7 |

**Arch 人均包数是 Debian 的 16 倍。**

### 退役流程

| 发行版 | 时限 |
|---|---|
| **Fedora** | **孤儿满 6 周 → 退役**（唯一硬性时限） |
| Debian | FTP-master 从 unstable 移除，无明确时限 |
| Arch | TU/Dev 决定；AUR 走 orphan/adopt（**adoption 已禁用**） |
| openSUSE / NixOS | 无明确时限 |

### 关键包维护
❌ **六家均无公开的「关键包指定维护者」清单。**
Debian 2026 GSoC 立项 **DebNet: Visualising the Bus Factor** —— 计算每个源码包的 Bus Factor / Fragility Score / Dependency Impact，目标正是识别「被过少人维护的关键包」。

---

## 6. 漏洞响应速度

### 核心结论：不存在可信的跨发行版 time-to-patch 数据集

| 来源 | 实际 |
|---|---|
| **Vulnpatch** | ❌ **全部 `medianDays` 主动撤回为 null**。理由：算法丢弃未修复 CVE（恰好最慢那批）、计时起点错误，导致「Debian 被渲染成最快却修复率最低」 |
| WMP/cve-patch-duration | ⚠️ 仅 1 commit、**0 star、无结果数据** |
| ICSE 2026 论文 | 补丁跨发行版传播延迟中位 530 天（Fedora↔Debian），但这是**补丁共享**不是安全响应 |
| Chainguard 报告 | 只讲自家镜像 SLA，非发行版对比 |
| Endor Labs / Wiz / Project Zero | ❌ 未找到 |

> **任何声称「A 比 B 快 N 天」的横向结论都应视为不可信。**

### 公告机制

| 发行版 | 公告 | 机器可读 |
|---|---|---|
| Ubuntu | USN | ✅ notices.json + OVAL + OSV + VEX |
| Debian | DSA / DLA | ⚠️ 无官方 REST API（数据在 git） |
| Fedora | Bodhi | ✅ RSS + JSON API |
| openSUSE | openSUSE-SU / SUSE-SU | ⚠️ 非结构化 |
| **Arch** | **ASA**（有机制！） | ⚠️ **tracker 当前停更** |
| **NixOS** | NIXPKGS-YYYY-NNNN + GitHub Advisory | ✅ tracker.security.nixos.org |
| Alpine | secdb | ✅ 每日更新 JSON+YAML |

> ⚠️ **修正两处误判**：Arch **有**安全公告机制（ASA + 9 人团队 + arch-security 列表），但 tracker 停更；NixOS **有**完整公告机制。

### 安全团队

| 发行版 | 性质 |
|---|---|
| Ubuntu | **Canonical 专职** |
| SUSE/openSUSE | **SUSE 商业专职** |
| Debian | 志愿者为主 |
| Fedora | 无独立专职，Red Hat Product Security 覆盖 |
| **Arch** | **9 名志愿者** |
| NixOS | 志愿者 |

**最本质的能力差异**：Ubuntu/SUSE 有拿薪水的安全团队。

### 覆盖范围陷阱

| 发行版 | 支持范围 | 陷阱 |
|---|---|---|
| **Debian** | **仅 main** | contrib/non-free/non-free-firmware **不受安全支持** |
| **Ubuntu** | Main/Restricted 5 年免费 | **Universe 仅 "best-effort"，完整支持需 Pro 付费** |
| Fedora | ~13 个月 | N-2 EOL |
| Arch | core/extra/multilib | **无固定支持窗口** |
| NixOS | ~7 个月 | 周期短 |
| openSUSE | TW 滚动 / Leap LTS | 差异大 |

### OSV.dev 覆盖
- ✅ **Debian、Alpine、Ubuntu**、Rocky、Alma
- ❌ **Arch、Fedora、openSUSE、NixOS、Gentoo**

### CNA
- ✅ Debian（**Sub-CNA**）、Red Hat（**CNA + LR**，2025-02）、Linux 内核（2024-02 起）
- ✅ SUSE / Canonical（二手）
- ❌ Arch / Alpine / Gentoo / NixOS

### LTS 安全周期
- Ubuntu：5 年 + Pro 10 年（+Legacy 15 年）
- Debian LTS：~5 年（bullseye **2026-08-31 EOL**）
- Fedora：~13 个月 ｜ NixOS：~7 个月 ｜ Arch/TW：**无 LTS**

### 真实案例（均无法给出「差几天」）
- xz 后门 CVE-2024-3094（2024-03-29）：Fedora Rawhide/40 与 openSUSE TW 为「含毒」版本，数小时内回滚
- regreSSHion CVE-2024-6387（2024-07-01）：各发行版数天内
- glibc Looney Tunables CVE-2023-4911（2023-10-03）：数天内

**可推断（非实测）**：滚动版在「上游已发包」类漏洞上天然占优（无 backport 等待），但在「上游无修复」类漏洞上依赖志愿者速度。**无数据证明哪边净胜。**

---

## 7. 未来发展前景

| 发行版 | 路线图 | 风险 |
|---|---|---|
| Fedora | 6 个月周期；**AI Developer Desktop 获批**；**Hummingbird**（容器化滚动）2026-05；Innovation Lifecycle | ⚠️ packager 下降；探索 Open Collective |
| openSUSE | **Slowroll 仍 beta（2026-09）**；Aeon；Kalpa | 未发现 |
| Debian | Debian 14 **Forky**（预计 2027）；15 = **Duke** | 未发现 |
| Ubuntu | **26.04 LTS（2026-04-23）支持至 2031-04** | 未发现 |
| Arch | **无官方路线图** | ⚠️ AUR 供应链事件 + 暂停认领 |
| NixOS | flakes 稳定化进行中（RFC 136） | ⚠️ 治理危机 + 资金 |

### NixOS Foundation 财务

| 年份 | 净收支 | 权益 |
|---|---|---|
| 2023 | — | €248,993 |
| 2024 | **−€55,862** | €193,130 |
| 2025 | **−€25,019** | **€168,111** |

**权益两年降 €80,882（约 32%）。**

其他：Debian/SPI 2025 审计财报约 2026-11 发布；GNOME 基金会 2024-10 削减预算。

---

## 8. 可复用操作

```bash
# Arch 官方 API：孤儿包计数（子代理数据需复核时用）
curl -s "https://archlinux.org/packages/search/json/?maintainer=orphan&limit=500" \
  | python -c "import sys,json;print(len(json.load(sys.stdin)['results']))"

# openQA 规模（openSUSE 的 QA 护城河）
curl -s "https://openqa.opensuse.org/api/v1/test_suites" \
  | python -c "import sys,json;print(len(json.load(sys.stdin)['TestSuites']))"
curl -s "https://openqa.opensuse.org/api/v1/machines" \
  | python -c "import sys,json;print(len(json.load(sys.stdin)['Machines']))"

# 核对任意发行版的人员规模
curl -s "https://archlinux.org/people/developers/" \
  | python -c "import sys,re;print(len(set(re.findall(r'/people/[a-z-]+/#([a-z0-9_]+)', sys.stdin.read()))))"

# 注意：repology.org/api/v1/* 对本环境返回 403，需用浏览器读网页
```

---

## 9. 坑与反直觉

1. **「哪个发行版补丁更快」没有可信答案** —— 唯一数据源已撤回。别信任何横向天数对比。
2. **Arch 是有安全公告机制的**（ASA + 9 人团队），但它的 tracker 当前停更 —— 这是「有机制但没维护」的典型。
3. **Arch 没有「Arch Council」**，最高负责人是 Project Leader。很多二手资料写错。
4. **Debian 只对 main 提供安全支持**，contrib/non-free 不受保护。
5. **Ubuntu 的 universe 仓库只有 "best-effort" 安全支持**，完整支持要买 Pro。
6. **OSV.dev 不覆盖 Arch/Fedora/openSUSE/NixOS** —— 想用 LLM 做安全运维，这是硬约束。
7. **outdated 占比不能跨发行版比较**：固定版本快照（Fedora 42/Debian 13/Ubuntu 24.04）天然偏高。
8. **openSUSE 与 Ubuntu 的 Repology 数据质量差**，官方已列「考虑移除」。
9. **可复现构建只有 Debian 有可信覆盖率**（95.9%）；openSUSE 停在 2018、Fedora 停在 F23。
10. **Fedora 的「6 周退役」是六家中唯一硬性时限**，其他发行版都没有明确时限。
11. **Arch 人均 172 包**（Debian 的 16 倍）—— 效率也是 bus factor 风险。
12. **NixOS 第三次 SC 选举投票期（2026-10-15 起）在本报告发布时尚未开始**，处于治理空窗期。
13. **NixOS 基金会权益两年降 32%**，叠加治理危机，是六家中组织风险最高的。
14. **Fedora packager 数从 420+ 降到 325**（2020→2026），是最明确的人力衰退信号。

---

## 10. 未核实 / 存疑

**主调研员独立核实并修正**：
- Arch orphan：303 → **250**（Arch 官方 API，两种 limit 一致）
- Arch Developers：子代理报 17 与 23 矛盾 → **23**（官方 people 页）
- openQA：**650 test suite / 114 机器**（官方 API 确认）
- Debian DPL：**Sruthi Chandran，347/1,039**（bits.debian.org 确认）

**无法独立核实**：
- **Repology 全部数字**（API 403，仅网页来源）
- Arch PM = 70 / Support = 49
- Fedora packager ≈325（仅二手 LWN）
- NixOS 贡献者总数、Ubuntu MOTU 人数、Ubuntu Community Council 活跃度
- Arch Project Leader 2026 选举详情、openSUSE Board 投票率

**结构性数据缺口（本身即结论）**：
- 跨发行版 time-to-patch 数据集不存在
- 六家均无「关键包指定维护者」公开清单
- Fedora / openSUSE 孤儿包总数无公开数据
- Arch / NixOS 可复现构建覆盖率无公开数字
- 个人级包维护量分布无权威统计
