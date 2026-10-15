---
type: Checklist
---

# Linux 发行版深度研究报告

**Arch · NixOS · openSUSE · Fedora · Debian · Ubuntu（+ Alpine / Gentoo 参照）**

| | |
|---|---|
| **报告版本** | 1.0.0 |
| **数据截止** | 2026-10-12 |
| **覆盖维度** | 17 个 |
| **调研方式** | 13 个并行子代理 + 主调研员对关键数据做 API 级独立核实 |
| **纠错记录** | 本轮修正 11 处错误/矛盾数据（见第 17 章） |

---

## 目录

- [第 0 章 执行摘要](#第-0-章-执行摘要)
- [第 1 章 方法论与可信度声明](#第-1-章-方法论与可信度声明)
- [第 2 章 六个候选：基本信息全景](#第-2-章-六个候选基本信息全景)
- **Part I · 系统层**
  - [第 3 章 滚动更新策略与长期稳定性](#第-3-章-滚动更新策略与长期稳定性)
  - [第 4 章 配置漂移与残余文件](#第-4-章-配置漂移与残余文件)
  - [第 5 章 打包质量与质量规范](#第-5-章-打包质量与质量规范)
  - [第 6 章 包的维护与孤儿包](#第-6-章-包的维护与孤儿包)
- **Part II · 安全层**
  - [第 7 章 漏洞响应能力](#第-7-章-漏洞响应能力)
  - [第 8 章 安全默认配置](#第-8-章-安全默认配置)
  - [第 9 章 硬件兼容与驱动](#第-9-章-硬件兼容与驱动)
- **Part III · 体验层**
  - [第 10 章 桌面环境：KDE vs GNOME](#第-10-章-桌面环境kde-vs-gnome)
  - [第 11 章 游戏性能优化](#第-11-章-游戏性能优化)
  - [第 12 章 软件新鲜度与平滑升级](#第-12-章-软件新鲜度与平滑升级)
  - [第 13 章 文档、生态与第三方支持](#第-13-章-文档生态与第三方支持)
  - [第 14 章 容器与云场景](#第-14-章-容器与云场景)
- **Part IV · 智能层**
  - [第 15 章 LLM 介入系统运维](#第-15-章-llm-介入系统运维)
  - [第 16 章 AI 协同管理的实践](#第-16-章-ai-协同管理的实践)
- **Part V · 组织层**
  - [第 17 章 社区治理、规模与前景](#第-17-章-社区治理规模与前景)
- **Part VI · 决策**
  - [第 18 章 综合选型决策](#第-18-章-综合选型决策)
  - [第 19 章 数据缺口与纠错记录](#第-19-章-数据缺口与纠错记录)
  - [附录 A 一页速查表](#附录-a-一页速查表)
  - [附录 B 可复用验证命令](#附录-b-可复用验证命令)

---

# 第 0 章 执行摘要

## 0.1 一句话结论

**不存在「最好的发行版」，只存在「与你的约束条件最匹配的发行版」。** 本报告覆盖的 17 个维度中，没有任何一个发行版同时拿下超过 5 个维度的第一名。

## 0.2 十七个维度的第一名

| # | 维度 | 第一名 | 关键证据 |
|---|---|---|---|
| 1 | 滚动更新可控性 | **openSUSE Tumbleweed** | openQA 门禁，唯一有公开构建失败看板的滚动版 |
| 2 | 声明式可回滚 | **NixOS** | generation 机制，配置即代码 |
| 3 | 配置漂移治理 | **NixOS** / **Fedora Atomic** | 构建期暴露 / `ostree admin config-diff` |
| 4 | 打包质量体系 | **openSUSE** | openQA **650 测试套件 + 114 机器** ✅ |
| 5 | 质量规范完备度 | **Debian** | Policy Manual **v4.7.4.1**（2026-03-31） |
| 6 | 包维护透明度 | **Fedora** | 唯一有硬性退役时限（**6 周**） |
| 7 | 漏洞响应 | **Ubuntu / SUSE** | 唯一有**拿薪水的专职安全团队** |
| 8 | 安全默认配置 | **Fedora** | SELinux 默认 enforcing + firewalld 默认启用 |
| 9 | 硬件/驱动易用性 | **Ubuntu / openSUSE** | `ubuntu-drivers` 一键 / YaST 一键安装器 |
| 10 | 桌面环境成熟度 | **KDE Plasma** | HDR 早 13 个月、VRR 早 2 年+ |
| 11 | 游戏性能 | **CachyOS**（Arch 系） | 但收益是**个位数百分比**，非翻倍 |
| 12 | 软件新鲜度 | **Arch**（outdated 13.6%） | ⚠️ 但 Repology 数据未独立核实 |
| 13 | 文档质量 | **Arch** | ArchWiki **892,004 次编辑 / 4,453 条目** ✅ |
| 14 | 容器/云场景 | **Alpine** | Docker Hub **123.5 亿次拉取**，镜像 3.2 MB ✅ |
| 15 | LLM 运维适配 | **NixOS**（有人监督）／**MicroOS**（无人值守） | 见第 15 章 |
| 16 | AI 协同生态 | **NixOS**（社区）／**RHEL**（官方） | 见第 16 章 |
| 17 | 治理稳健度 | **Debian** | 1,039 投票权 DD，无资金危机 |

## 0.3 五条核心结论

**结论一：文档与生态的「双极结构」**
ArchWiki 是全 Linux 世界最好的文档（**892,004 次编辑**，已核实），但 Arch 官方零安全投入；Ubuntu 有专职安全团队和最好的商业软件支持，但文档质量远不如 Arch。**没有发行版同时拥有最好的文档和最好的安全。**

**结论二：NixOS 是「技术最优、组织最危」**
技术上 NixOS 是唯一从架构上消灭配置漂移和孤儿包的发行版；但组织上它经历了三次连续治理危机（2025-09 版主团队 5/7 辞职 → 2026-08 Nixpkgs 核心团队解散 → 基金会连亏两年，权益降 32%），且**第三次 SC 选举投票期在本报告发布时尚未开始**。

**结论三：「哪个发行版补丁更快」没有可信答案**
唯一公开跨发行版 time-to-patch 数据的服务（Vulnpatch）**已主动把全部数字撤回为 null**，理由是算法把「未修复的 CVE」直接丢弃（恰好是最慢的那批）。**任何声称「A 比 B 快 N 天」的横向结论都不可信。**

**结论四：安全能力的分水岭是「有没有拿薪水的安全团队」**
Ubuntu（Canonical 专职）、SUSE（SUSE 专职）与 Arch（**9 名志愿者**）、NixOS、Debian 之间存在结构性差距。这直接反映在 OSV.dev 覆盖上：**Debian / Alpine / Ubuntu 入选，Arch / Fedora / openSUSE / NixOS 全部缺位**。

**结论五：滚动发行版的「不可控」是被高估的担忧，真正的痛点是配置漂移**
openSUSE Tumbleweed 用 openQA 门禁把滚动更新做成了有质量保证的流程；NixOS 用声明式把升级变成可回滚事务。**长期运维真正的痛点是配置文件冲突（`.pacnew` / `.rpmnew` / `.dpkg-dist`）与语义漂移** —— 前者靠工具，后者只有 NixOS 能自动拦截。

## 0.4 三十秒选型

| 你的情况 | 选它 | 一句话理由 |
|---|---|---|
| 企业生产 / 要支持合同 | **RHEL**（Fedora 作试验田） | 唯一官方 MCP + 专职安全团队 + SLA |
| 个人主力机 / 要稳定 + 新软件 | **Fedora Workstation** | 6 个月周期 + 内核/Mesa 永久例外 |
| 想要最活跃的社区 + AI 生态 | **NixOS** | 唯一三类 AI 实践齐备，但接受治理风险 |
| 想学 Linux / 要最好的文档 | **Arch** | ArchWiki 无出其右，但安全靠自己 |
| 桌面要最新 + 要质量门禁 | **openSUSE Tumbleweed** | openQA 650 测试套件兜底 |
| 游戏为主 | **CachyOS / Bazzite** | 但收益是个位数百分比 |
| 服务器 / 求稳 | **Debian** | 治理最稳、规范最完备 |
| 容器 / 云原生 | **Alpine** | 123.5 亿次拉取，3.2 MB 镜像 |
| 完全不想维护 | **Aeon / MicroOS** | 唯一「自动更新 + 失败自动回滚」闭环 |

---

# 第 1 章 方法论与可信度声明

## 1.1 调研方式

本报告整合了 8 轮独立深度调研（累计 13 个并行子代理），并对**所有关键量化数据做了主调研员的独立核实**。

**核实手段**（本轮实际使用）：
- GitHub REST API（仓库 star / 活跃度 / 归档状态 / 源码内容）
- Arch 官方包库 API（包数、孤儿包数）
- Arch 官方 people 页面（维护者人数）
- openQA 官方 API（测试套件数、机器数）
- Docker Hub API（镜像拉取量）
- ArchWiki MediaWiki API（文档规模）
- bits.debian.org（DPL 选举结果）
- rpmfind 文件列表（rpm 包内容）
- nixpkgs 源码（`lib/modules.nix`）

## 1.2 数据标记体系

| 标记 | 含义 |
|---|---|
| ✅ **已核实** | 主调研员通过官方 API / 官方页面 / 源码直接验证 |
| ◐ **子代理** | 来自子代理报告，未经主调研员独立验证 |
| ⚠️ **二手** | 新闻 / 博客 / 论坛 / 第三方转述 |
| ❌ **无公开数据** | 检索后确认不存在可靠公开数据 |

## 1.3 本报告的主要局限

1. **Repology 数据未经独立核实** —— Repology API 对本环境返回 **403 Forbidden**（带 User-Agent 亦被拒）。所有包数 / outdated 占比数字来自网页读取，仅作参考。
2. **「哪个发行版补丁更快」无解** —— 见第 7 章，这是数据层面的结构性空白，不是调研不努力。
3. **多站点反爬** —— `wiki.archlinux.org`（Anubis PoW）、`build.opensuse.org`（PoW）、`repology.org/api`（403）、`manpages.opensuse.org`（返回空）均不可程序化抓取，已改用等价来源。
4. **社区评价类结论不可量化** —— 如「ArchWiki 是最好的文档」属社区共识，无客观排名数据。

---

# 第 2 章 六个候选：基本信息全景

| | **Arch** | **NixOS** | **openSUSE TW** | **Fedora** | **Debian** | **Ubuntu** |
|---|---|---|---|---|---|---|
| **发布模型** | 滚动 | 滚动 + 半年 stable | 滚动（snapshot） | 6 个月 | 约 2 年 | 6 个月 / 2 年 LTS |
| **内核**（2026-10） | 7.2.7 ◐ | 6.18 LTS ◐ | 7.2.x ✅ | 7.2.6 ◐ | 6.12 LTS ◐ | 7.0 ◐ |
| **官方包数** | 16,008 ◐ | **149,566** ◐ | 17,270 ◐ | 82,747（全分支）◐ | 69,830 ◐ | 39,336 ◐ |
| **核心维护者** | **93**（23 Dev ✅ + 70 PM ◐） | ❌ 无数据 | ~521 members ◐ | ~325 packagers ⚠️ | **1,039 DD** ✅ | 378 Members ◐ |
| **默认 MAC** | ❌ 无 | ❌ 无 | SELinux ✅ | SELinux ✅ | AppArmor（部分）◐ | AppArmor ✅ |
| **默认防火墙** | ❌ 无 | ✅ 有 | firewalld ◐ | firewalld ✅ | ❌ 无 | ufw 预装但 inactive ◐ |
| **包管理器** | pacman | nix | zypper | dnf | apt | apt |
| **配置文件保护** | `backup=()` | 声明式（无冲突） | `%config` | `%config` | `conffiles` | `conffiles` |
| **安全团队** | **9 志愿者** ◐ | 志愿者 ◐ | **SUSE 专职** ✅ | Red Hat 代管 ◐ | 志愿者为主 ◐ | **Canonical 专职** ✅ |
| **治理** | 社区 + Leader | 基金会 + 选举 SC | Board + SUSE | Council + FESCo | 纯社区 + DPL | Canonical 主导 |

---

# Part I · 系统层

# 第 3 章 滚动更新策略与长期稳定性

## 3.1 三种滚动模型

| 模型 | 代表 | 机制 | 失败模式 |
|---|---|---|---|
| **无门控连续滚动** | Arch | 包一旦进入 `extra` 立即可用 | 上游破坏性变更直接抵达用户 |
| **快照门控滚动** | openSUSE TW | staging → openQA 测试 → 发布 snapshot | 单个 snapshot 可能整体延后 |
| **渠道门控滚动** | NixOS unstable | Hydra 构建全绿才推进 channel | channel 可能长时间不前进 |

## 3.2 逐项对比

| 维度 | Arch | NixOS | openSUSE TW |
|---|---|---|---|
| **门禁** | ❌ 无 | ✅ Hydra 构建门控 | ✅ **openQA 测试门控** |
| **快照粒度** | 包级（每次 `pacman -Syu`） | channel 级（数天一次） | snapshot 级（**2026-08 发 23 个 / 31 天** ◐） |
| **构建失败看板** | ❌ 无 | ✅ Hydra | ✅ **openQA 公开实例** |
| **回滚能力** | ⚠️ 需 ALA（Arch Linux Archive）降级 | ✅ **generation 一键回滚** | ✅ btrfs 快照 + `snapper rollback` |
| **自动更新** | ❌ 无官方 | ✅ `system.autoUpgrade` | ✅ `zypper dup` 可定时 |
| **自动更新失败回滚** | — | ❌ **不自动回滚** | ✅ health-checker（MicroOS） |
| **无人值守适用性** | ❌ 最差 | ⚠️ 中（需人工兜底） | ✅ **最好** |

## 3.3 关键事实

- **NixOS 的 `nixos-unstable` 不是 bleeding edge**，而是 Hydra 门控的 curated snapshot —— 这常被误解。
- **NixOS 的 `system.autoUpgrade` 失败不自动回滚**，需人工在 bootloader 选旧 generation。这是它与 MicroOS 的核心差距。
- **Arch 没有官方自动更新**，`systemd` timer 需自己写；且 Arch 明确不承诺安全支持。
- **openSUSE Tumbleweed 是三者中唯一有公开构建质量看板的**（openQA）。
- **Slowroll 仍标记为 experimental**（专题新闻停在 2025-01，2026-09 仍 beta ◐）—— 定位是「月更版 Tumbleweed」，但**尚未脱离实验状态**。

## 3.4 本章结论

| 你的需求 | 选择 |
|---|---|
| 要最新 + 要质量门禁 | **openSUSE Tumbleweed** |
| 要最新 + 可精确回滚 | **NixOS** |
| 要最新 + 接受自己负责 | **Arch** |
| 要无人值守长期运行 | **MicroOS / Aeon**（非纯滚动，但这是唯一闭环解） |

---

# 第 4 章 配置漂移与残余文件

> 这是长期滚动运维**真正的痛点**，也是前六轮调研中被反复追问的主题。

## 4.1 先分类：四种「漂移」

| 类型 | 是什么 | 能否自动解决 |
|---|---|---|
| **A. 文件级冲突** | 你的改动与上游改动撞车（`.pacnew` / `.rpmnew` / `.dpkg-dist`） | 能检测，**不能自动判定谁对** |
| **B. 语义漂移** | 你的配置一字未改，但上游改了默认值/废弃了选项 | **只有 NixOS 能硬拦截** |
| **C. 孤儿包** | 不再被任何包依赖的包 | ✅ 能全自动 |
| **D. 残余文件** | 不属于任何包的文件 / 包删除后残留的目录 | 能检测，清理需人工判断 |

## 4.2 最关键、最容易被误解的机制

> **只有被声明为「配置文件」的文件才有保护。**
>
> Arch 的 `backup=()` 数组、RPM 的 `%config`、Debian 的 `DEBIAN/conffiles` —— **没声明的文件升级时直接覆盖，连 `.pacnew` 都不会留。**

**含义**：漂移不只表现为「多出文件」，也表现为「**本地修改静默消失**」。这是比 `.pacnew` 堆积更隐蔽的问题。

## 4.3 冲突文件生成规则

**Arch（三方 MD5 比对）**

| 比对结果 | pacman 行为 |
|---|---|
| 你没改，上游改了 | 静默覆盖 |
| 你改了，上游没改 | 保留你的 |
| **都改了** | **保留你的，新版存 `.pacnew` 并告警** |

- 查某包的 backup 列表：`pacman -Qii <pkg>`
- **反直觉**：安装**其他**包也可能改到本包的文件，导致你没动手却生成 `.pacnew`（Arch FS#77404）

**Fedora / RHEL（三后缀）**

| 后缀 | 条件 | 结果 |
|---|---|---|
| `.rpmnew` | `%config(noreplace)`，双方都改 | 保留你的，新版存 `.rpmnew` |
| `.rpmsave` | `%config`（无 noreplace），双方都改 | 装新版，你的存 `.rpmsave` |
| `.rpmorig` | `rpm -i` 非升级安装且文件不属于任何包 | 已有文件改名 `.rpmorig` |

**Debian（唯一默认强制表态）**
dpkg 对 `conffiles` 做三方比对，**只有双方都改才交互提示**：`Y/I` 装维护者版（你的存 `.dpkg-old`）／`N/O` 保留本地（新版存 `.dpkg-dist`）／`D` 看 diff／`Z` 开 shell。

**openSUSE（唯一自带 systemd service）**
- ✅ **已核实**：`/usr/lib/systemd/system/rpmconfigcheck.service` 存在于 rpm 包中（rpmfind 对 `rpm-4.20.1-11.1` 的文件列表）
- ⚠️ **但没有配套的 `.timer`** → **不会自动运行**，需 `systemctl start rpmconfigcheck` 或自建 timer

## 4.4 横向对比

| 机制 | 默认自动检测 | 官方工具 | **三方合并** | 升级时提示 |
|---|---|---|---|---|
| Arch `.pacnew` | ⚠️ 仅 warning | `pacdiff` | ✅ **`-3`**（需缓存有 base 包） | 否 |
| Fedora `.rpmnew` | ❌ | `rpmconf`（Fedora 官方仓库） | ❌ 仅两方 | 否 |
| Debian `.dpkg-dist` | ✅ | dpkg 内建 + `ucf` | ⚠️ dpkg 非三方；**ucf 支持** | ✅ **唯一** |
| openSUSE | ⚠️ 有 service 无 timer | `rpmconf` | ❌ 仅两方 | 否 |

## 4.5 结构性解法

**NixOS —— 漂移在构建期暴露**

上游废弃选项时的行为（**已从 nixpkgs 源码核实**）：

| 函数 | 行为 |
|---|---|
| `mkRenamedOptionModule` | 只 warning + 转发 |
| `mkAliasOptionModule` | 静默转发，不警告 |
| **`mkRemovedOptionModule`** | **硬 `throw`，中断 rebuild** |

`lib/modules.nix` 第 1863 行原文：
```nix
throw "The option `${showOption optionName}' can no longer be used since it's been removed. ${replacementInstructions}";
```

> ⚠️ **官方文档说 "warning"，实现是 `throw`** —— 文档与实现不一致，以源码为准。第三方佐证：mobile-nixos issue #731。

**NixOS 仍有漂移的例外**：`/var`、`/home`（有状态数据不受管）、`nix-env -i` 装的包、手工 systemd unit、home-manager 只撤自己创建的符号链接、`/nix/store` 无限增长（需 GC）。

**Fedora Atomic —— 内置漂移检测器**
```bash
ostree admin config-diff
# 打印当前 /etc 与默认 /usr/etc 的差异：A=新增 M=修改 D=删除
```
升级时 `/etc` 走**三方合并**：本地改过的永久保留，未改的升到新默认。**不用 `.rpmnew` 机制。**

**MicroOS / Aeon —— `/etc` 也在快照里**
只读根 + btrfs 快照，回滚即回滚配置。`health-checker` 在 legacy grub2 下首次启动失败自动回滚。⚠️ 无 `config-diff` 等价物。

## 4.6 最被低估的通用解法：etckeeper

```bash
sudo etckeeper init && sudo etckeeper commit "初始状态"
sudo etckeeper vcs log --oneline -20
etckeeper unclean && echo "有未记录的 /etc 改动"   # 可直接做漂移告警
```

**它不解决冲突，但让所有漂移可追溯、可回滚、可审计。** 跨发行版，装完当天见效。Arch 官方 `extra` 仓库有（`etckeeper 1.18.23-3`，2026-04-14 ✅）。

## 4.7 本章结论

| 需求 | 方案 |
|---|---|
| 不想有漂移 | **NixOS**（唯一从架构上消灭） |
| 要能一眼看出漂移 | **Fedora Atomic**（`ostree admin config-diff`） |
| 要能一键回滚配置 | **MicroOS / Aeon**（`/etc` 在快照里） |
| 已在命令式发行版上 | **etckeeper + 定期 `pacdiff` / `rpmconf`** |

---

# 第 5 章 打包质量与质量规范

## 5.1 包数量与新鲜度

| repo | 总包数 | Outdated | 占比 | Problems |
|---|---|---|---|---|
| Arch | 15,516 | 2,110 | **13.6%** | 911 |
| NixOS unstable | **149,566** | 18,958 | **12.7%** | 3,700 |
| openSUSE TW | 17,270 | 4,503 | 26.1% | 1,822 |
| Fedora 42 | 31,028 | 12,706 | 40.9%* | 2,965 |
| Debian 13 | 38,684 | 17,989 | 46.5%* | 3,284 |
| Ubuntu 24.04 | 39,336 | 20,553 | **52.3%*** | 4,173 |

◐ 全部为子代理读取 Repology 网页所得。**Repology API 对本环境 403，未独立核实。**
\* 固定版本快照，outdated 天然偏高，**不可与滚动版直接比较**。
⚠️ Repology 官方警告 openSUSE / Ubuntu 的 repo 数据质量差（版本造假、无源码链接），**两者已被列入「考虑移除」**。

**其他口径**：Arch 官方仓库自报 **16,008** 包；Fedora 全分支 **82,747** 包；Debian 13 **69,830** 包；NixOS nixpkgs **>140,000** 包；AUR **121,709** 包。

## 5.2 自动化质量检查

| 发行版 | 工具 | 规模 | 强制 |
|---|---|---|---|
| **Arch** | `namcap` | 127 个 tag | ❌ **非强制** |
| **Fedora** | `rpmlint` + `fedora-review` | 38 个 check 模块 | ✅ **review 必跑** |
| **Debian** | `lintian` | **1,485 个检查项** | ❌ 可 override |
| **openSUSE** | `rpmlint` + `brp-check-suse` | 构建期 | ⚠️ 部分 error 阻断 |

## 5.3 QA / CI 覆盖率

| 发行版 | 体系 | 强度 |
|---|---|---|
| **openSUSE** | **openQA** | ✅ **最强**：**650 个 test suite + 114 台机器**（独立核实） |
| **Fedora** | Zuul CI + tmt + Bodhi **gating** | 强：测试不过则**阻断更新发布** |
| **Debian** | piuparts + autopkgtest + lintian | 中：**均非上传硬门槛** |
| **Arch** | 仅 namcap | **最弱**：无 CI 强制，AUR 无自动检查 |

> **openQA 数据已独立核实**：`openqa.opensuse.org/api/v1/test_suites` → **650**；`/api/v1/machines` → **114**。覆盖 Tumbleweed / Leap / ARM / RISC-V / s390x，是**发行版级全系统安装测试** —— openSUSE 在打包质量维度最硬的护城河。

## 5.4 可复现构建

| 发行版 | 状态 |
|---|---|
| **Debian** | forky/amd64 **95.9%** 可复现、0.9% FTBFS；unstable 94.8%、1.6% FTBFS |
| Arch | reproducible.archlinux.org，**无公开百分比** |
| NixOS | reproducible.nixos.org，**仅方法说明** |
| **openSUSE** | 测试数据**停留在 2018-12-13**，实质停更 |
| **Fedora** | 仅到 **fedora-23** 时代页面，早已停更 |

**只有 Debian 有公开、可信、持续更新的可复现构建覆盖率。**

## 5.5 FTBFS（构建失败）

| 发行版 | 数据 |
|---|---|
| Debian | **0.9%–1.8%** |
| Fedora | Koschei 追踪 **180,316** 包 / 1,341,362 次构建，**未给百分比** |
| Arch / openSUSE / NixOS | ❌ 无公开汇总 |

## 5.6 质量规范文档

| 发行版 | 规范 | 执行力度 |
|---|---|---|
| **Arch** | Arch packaging standards / PKGBUILD 规范 | 人工 review；namcap 非强制 |
| **Fedora** | Packaging Guidelines（**FPC** 维护） | rpmlint + fedora-review **强制** + CI gating |
| **Debian** | **Policy Manual v4.7.4.1**（2026-03-31） | lintian 提示 + FTP-master/sponsor 人工审核 |
| **openSUSE** | packaging guidelines + Packaging_checks | OBS 构建期强制部分 |
| **NixOS** | `CONTRIBUTING.md`（54KB）+ RFC 流程 | 人工 review + ofBorg CI |

**Debian Policy Manual 是六家中最完备的**，且有正式版本号 —— 其他发行版的规范更接近「wiki 页面 + 惯例」。

**规范演进（2025-2026）**
- ⚠️ **Arch：2026-07-30 AUR 暂停「包认领（adoption）」功能**（第三波恶意接管攻击）—— 本年度最值得关注的规范层事件
- Arch RFC 0014：新 Package Maintainer 前两个月标记为 "junior"
- Debian Policy 4.7.4.1 发布（2026-03-31）

---

# 第 6 章 包的维护与孤儿包

## 6.1 孤儿包

| 发行版 | 数量 | 核实 |
|---|---|---|
| **Arch** | **250** | ✅ **独立核实**（Arch 官方 API，两种 limit 口径一致） |
| **Debian** | **1,070** orphaned + 100 RFA + 46 RFH | ◐ |
| **Fedora** | ❌ 无公开汇总（政策：孤儿 **6 周后退役**） | — |
| **openSUSE** | ❌ 无公开汇总 | — |

> ⚠️ **本轮纠错**：子代理报告称 Arch 有 **303** 个孤儿包，独立核实实际为 **250**。

## 6.2 维护者 : 包 比例

| 发行版 | 维护者数 | 官方包数 | **包 / 人** |
|---|---|---|---|
| **Arch** | 23 Dev ✅ + 70 PM ◐ = **93** | 16,008 | **约 172** |
| NixOS | 4,949 ◐ | 149,566 | 约 30 |
| Debian | 3,559 ◐ | 38,684 | 约 10.9 |
| Ubuntu | 3,365 ◐ | 39,336 | 约 11.7 |

**Arch 人均包数是 Debian 的 16 倍。** 这既是效率（滚动版淘汰快），也是 bus factor 风险。

> ⚠️ **本轮纠错**：两个子代理对 Arch 维护者数的说法互相矛盾（「17 Dev + 54 PM」vs「23 Dev + 70 PM」）。独立核实 **Developers = 23**，故采信 23 + 70。

## 6.3 退役流程

| 发行版 | 流程 | 时限 |
|---|---|---|
| **Fedora** | 孤儿满 **6 周** → Rawhide/Branched 退役，留 `dead.package` | ✅ **唯一硬性时限** |
| **Debian** | 长期孤儿 → FTP-master 从 unstable 移除 | 无明确时限 |
| **Arch** | 仓库包由 TU/Dev 决定；AUR 走 orphan/adopt（**adoption 已禁用**） | 无明确时限 |
| **openSUSE / NixOS** | 无明确时限 | 无 |

## 6.4 关键包（critical path）维护

❌ **六家均无公开的「关键包指定维护者」清单。**

**值得注意的动向**：Debian 2026 GSoC 立项 **DebNet: Visualising the Bus Factor** —— 用 UDD 数据构建包依赖图与维护者-包图，计算每个源码包的 **Bus Factor / Fragility Score / Dependency Impact**，目标正是**识别「被过少的人维护的关键包」**。这说明 Debian 已把这个问题正式立项。

---

# Part II · 安全层

# 第 7 章 漏洞响应能力

## 7.1 核心结论：**不存在可信的跨发行版 time-to-patch 数据集**

这是本维度最重要的发现。逐条核实：

| 来源 | 声称 | 实际 |
|---|---|---|
| **Vulnpatch** `time-to-fix` | 跨发行版补丁速度对比 | ❌ **全部 `medianDays` 已撤回为 `null`**。作者原文理由：算法「把未修复的 CVE 丢弃（恰好是最慢的那批）、计时起点是服务首次观测到修复而非发行版发布时刻」，导致「**Debian 被渲染成最快，却拥有最低的修复率**」 |
| **WMP/cve-patch-duration** | 内核 CVE 修复时长 | ⚠️ 仅 1 次 commit（2026-05-20）、**0 star、未发布任何结果** |
| **ICSE 2026** 论文 | 补丁跨发行版传播 | 中位延迟 530 天（Fedora↔Debian）—— **但这是「维护补丁共享」，不是安全响应** |
| **Chainguard** 报告 | 商业 | 只讲**自家镜像** SLA（Critical <20h），**不是发行版对比** |
| Endor Labs / Wiz / Project Zero | — | ❌ **未找到**发行版横向数据集 |
| commandlinux.com | 企业级 24–48 小时内 | ⚠️ **无逐发行版数据**，二手拼贴，可信度低 |

> **任何声称「A 比 B 快 N 天」的横向结论都应视为不可信。**

## 7.2 漏洞公告机制

| 发行版 | 公告 | 机器可读源 |
|---|---|---|
| **Ubuntu** | USN | ✅ `/security/notices.json` + **OVAL + OSV + VEX** |
| **Debian** | DSA / DLA | ⚠️ **无官方 REST API**（数据在 git） |
| **Fedora** | Bodhi | ✅ RSS + JSON API |
| **openSUSE** | openSUSE-SU / SUSE-SU | ⚠️ 非结构化 |
| **Arch** | **ASA（有机制！）** | ⚠️ **tracker 当前停更**（ArchWiki 明确警告 "The tracker is currently not updated"） |
| **NixOS** | `NIXPKGS-YYYY-NNNN` + GitHub Advisory | ✅ `tracker.security.nixos.org` |
| **Alpine** | secdb | ✅ **每日更新**的 JSON + YAML |

> ⚠️ **修正两处常见误判**：
> - **Arch 是有安全公告机制的**（ASA + 专用 tracker + `arch-security` 邮件列表 + 9 人志愿团队，需 2 人复核才发布）—— 并非「没有安全公告」。**但它的 tracker 当前停更**，这才是真正的隐患。
> - **NixOS 也有完整公告机制**，并非「无公告」。

## 7.3 安全团队（最本质的能力差异）

| 发行版 | 团队性质 |
|---|---|
| **Ubuntu** | ✅ **Canonical 专职** Ubuntu Security Team |
| **SUSE/openSUSE** | ✅ **SUSE Security Team（商业专职）**，负责 SLES + Leap + Tumbleweed |
| **Debian** | ◐ 志愿者为主（含 DSA / LTS 分工） |
| **Fedora** | ◐ 无独立专职团队，由 **Red Hat Product Security** 覆盖 |
| **Arch** | ◐ **9 名志愿者**（无专职） |
| **NixOS** | ◐ 志愿者 |

## 7.4 覆盖范围陷阱

| 发行版 | 支持范围 | **陷阱** |
|---|---|---|
| **Debian** | **仅 main** | ⚠️ **contrib / non-free / non-free-firmware 不受安全支持** |
| **Ubuntu** | Main/Restricted 5 年免费 | ⚠️ **Universe/Multiverse 仅 "best-effort"，完整支持需 Ubuntu Pro 付费** |
| **Fedora** | 约 13 个月 | N-2 达 EOL |
| **Arch** | core / extra / multilib | **无固定支持窗口** |
| **NixOS** | stable 约 **7 个月** | 周期短 |
| **openSUSE** | TW 滚动 / Leap LTS | 两者差异大 |

## 7.5 OSV.dev 覆盖（数据基础设施成熟度）

| 状态 | 发行版 |
|---|---|
| ✅ **已覆盖** | **Debian**、**Alpine**（SecDB 转换）、**Ubuntu**、Rocky、Alma |
| ❌ **未覆盖** | **Arch、Fedora、openSUSE、NixOS、Gentoo** |

**对「用 LLM 做安全运维」的场景，这是硬约束。**

## 7.6 CNA（CVE 编号机构）

| 发行版 | 是否 CNA |
|---|---|
| **Debian** | ✅ **Sub-CNA** |
| **Red Hat（含 Fedora）** | ✅ CNA，2025-02 起为 **CNA-LR** |
| **Linux 内核** | ✅ 2024-02 起自建（CVE 量激增 13 倍） |
| SUSE / Canonical | ✅（二手） |
| **Arch / Alpine / Gentoo / NixOS** | ❌ 未核实为 CNA |

## 7.7 安全支持周期（LTS）

| 发行版 | 周期 |
|---|---|
| **Ubuntu** | 5 年标准 + Pro 10 年（+ Legacy 15 年） |
| **Debian LTS** | 约 5 年（bullseye 已于 **2026-08-31** EOL） |
| **Fedora** | 约 13 个月 |
| **NixOS** | 约 7 个月 |
| **Arch / Tumbleweed** | **无 LTS** |

**社区发行版均无安全 SLA**；有 SLA 的是商业产品（Chainguard Critical 7 天、SUSE/RHEL 商业订阅）。

## 7.8 真实案例（注意：都无法给出「差几天」）

| 案例 | 披露 | 情况 |
|---|---|---|
| **xz 后门 CVE-2024-3094** | 2024-03-29 | Fedora Rawhide/40 与 openSUSE Tumbleweed 为「含毒」版本，**数小时内**回滚/降级；Debian stable 未受影响；Arch 未进入 stable。**精确小时数未见权威统计** |
| **regreSSHion CVE-2024-6387** | 2024-07-01 | Debian/Ubuntu/RHEL/SUSE/Alpine 等「数天内」发布补丁 |
| **glibc Looney Tunables CVE-2023-4911** | 2023-10-03 | 各发行版数天内跟进 |

**可推断（非实测）**：滚动发行版在「上游已发包」类漏洞上**天然占优**（无 backport 等待），但在「上游无修复」类漏洞上**依赖志愿者打包速度**。**没有任何数据能证明哪边净胜。**

---

# 第 8 章 安全默认配置

## 8.1 强制访问控制（MAC）默认状态

| 发行版 | 默认 MAC | 细节 |
|---|---|---|
| **Fedora/RHEL** | **SELinux** | ✅ 默认 **enforcing**（targeted） |
| **openSUSE TW** | **SELinux** | ✅ 自 Build 20250211 起默认 enforcing；AppArmor 可作替代 |
| openSUSE Leap 15.x | AppArmor | 默认 AppArmor；SELinux 需手动 |
| **Debian** | AppArmor | ◐ 默认启用，但**仅对部分精选 profile enforce，非全系统** |
| **Ubuntu** | AppArmor | ✅ 十余年默认 MAC；snap 用 strict confinement |
| **Arch** | ❌ **无** | 默认不启用任何 MAC，AppArmor/SELinux 均需手动 |
| **NixOS** | ❌ **无** | AppArmor「2026-04 起可用但尚未正确集成」；SELinux 无完善集成（2019 起停滞） |
| **Alpine** | ❌ **无** | 需 `apk add` + 改 `lsm=` cmdline |

## 8.2 默认防火墙

| 发行版 | 默认状态 |
|---|---|
| **Fedora** | ✅ firewalld 预装且**默认启用** |
| **NixOS** | ✅ `networking.firewall` **默认启用** |
| openSUSE TW | ◐ firewalld 默认 |
| **Ubuntu** | ◐ ufw **预装但默认 inactive** |
| **Debian** | ❌ 无默认规则 |
| **Arch** | ❌ **无**（官方原文：两种方案都不会自动启用） |
| **Alpine** | ❌ 无 |

## 8.3 全盘加密（安装器层）

| 发行版 | 安装器 FDE |
|---|---|
| **Fedora** | ✅ Anaconda 勾选 "Encrypt System" → LUKS |
| **Ubuntu** | ✅ 安装器提供 LUKS FDE |
| **Debian** | ✅ "Guided - encrypted LVM"，亦支持加密 /boot |
| **openSUSE** | ◐ YaST 分区器支持 LVM + 全盘加密 |
| **NixOS** | ✅ 声明式（`boot.initrd.luks`） |
| **Arch** | ◐ 需手动（archinstall 可选 LUKS） |
| **Alpine** | ❌ 安装器默认不提供自动 FDE |

## 8.4 安全基线工具

| 发行版 | 工具 |
|---|---|
| **Fedora** | ✅ OpenSCAP + `scap-security-guide`（含 CIS / STIG profile） |
| **Ubuntu** | ✅ Ubuntu Security Guide (USG)，CIS / DISA-STIG |
| **Debian** | ❌ 无官方内置基线工具（社区 hardening 指南） |
| **SUSE** | ✅ openSUSE SELinux 策略源自 Fedora policy；SLES 有独立 hardening guide |

## 8.5 安全默认值的争议

- ⚠️ **openSUSE TW 把默认 MAC 从 AppArmor 切到 SELinux**（2025-02）引发社区讨论
- ⚠️ **Ubuntu snap confinement** 长期被批 strict/classic 边界模糊；CVE-2026-8933 snap-confine 提权再次聚焦
- ⚠️ **Ubuntu 26.04 桌面最低内存 4GB → 6GB** 引争议
- ⚠️ Fedora SELinux 学习曲线：admin 常误用 `setenforce 0` 而非 `audit2allow`

## 8.6 本章结论

| 需求 | 选择 |
|---|---|
| 要开箱即有 MAC + 防火墙 | **Fedora**（SELinux enforcing + firewalld 默认） |
| 要企业级安全基线 | **Fedora**（OpenSCAP）/ **Ubuntu**（USG） |
| 要默认无 MAC 的简洁性 | **Arch**（但风险自负） |

---

# 第 9 章 硬件兼容与驱动

## 9.1 NVIDIA 专有驱动安装

| 发行版 | 方式 | Secure Boot 签名 |
|---|---|---|
| **Ubuntu** | ✅ `sudo ubuntu-drivers install`（一键，自动检测） | 安装时**自动 MOK 注册** |
| **openSUSE** | ✅ YaST **一键安装器**（NVIDIA 官方仓库） | 支持 |
| **Debian** | 启用 `non-free`/`non-free-firmware` 后 `apt install nvidia-driver` | 需手动 MOK |
| **Fedora** | RPM Fusion → `dnf install akmod-nvidia`（等待 akmods 编译 2–5 分钟） | 需手动 MOK |
| **Arch** | `pacman -S nvidia nvidia-utils`（官方 extra）；老卡用 AUR | 需自行签名 |
| **NixOS** | ✅ `hardware.nvidia` 声明式（含 open kernel module 开关） | 需自行处理 |

**结论**：Ubuntu 与 openSUSE 对新手最友好；NixOS 声明式但调试成本高；Debian/Arch 最手动。

## 9.2 Secure Boot

| 发行版 | 开箱支持 |
|---|---|
| **Ubuntu / Fedora / openSUSE** | ✅ 有微软签名 shim，装机即用 |
| **Debian** | `shim-signed` 包；2026-07 因 2013 CA 过期已更新签名 |
| **Arch** | ❌ 官方不提供签名引导，需 `sbctl` 自签 + 注册 MOK |
| **NixOS** | ❌ 无开箱支持；实验性 Lanzaboote |

## 9.3 笔记本支持

- **指纹**：统一走 `fprintd`/`libfprint`，实际覆盖取决于硬件型号
- **电源**：GNOME/KDE 默认 `power-profiles-daemon`；TLP 为可选替代
- **休眠**：⚠️ **Fedora 默认禁用**，且 Secure Boot lockdown 下内核直接拒绝休眠；Ubuntu 亦默认常禁用
- **触控板手势**：由 Wayland/libinput 提供，GNOME 50 / Plasma 6.6 均原生支持

## 9.4 内核版本对照（2026-10）

| 发行版 | 内核 |
|---|---|
| Arch | 7.2.7 ◐ |
| openSUSE TW | 7.2.x ✅ |
| Fedora 44 | 7.2.6 ◐ |
| **NixOS 26.05** | **6.18 LTS** ◐ |
| Ubuntu 26.04 | 7.0 ◐ |
| **Debian 13** | **6.12 LTS** ◐ |
| Alpine 3.24 | 6.18 LTS ◐ |

**新硬件支持速度**：Arch ≈ Tumbleweed > Fedora > Ubuntu > NixOS ≈ Debian

> ⚠️ **重要提醒**：NixOS stable 与 Debian stable 的内核落后约 1 年 —— 这对新硬件（尤其是新笔记本）是实际障碍。

## 9.5 系统资源占用

| 发行版 | 最低 RAM | 桌面空闲 RAM | 安装磁盘 |
|---|---|---|---|
| **Ubuntu 26.04** | ✅ **6 GB** | ~1.8–2.2 GB ◐ | 25 GB 最小 ✅ |
| Fedora 44 | ❌ 无官方数字 | ~1.2 GB ◐ | ~8 GB ◐ |
| **Arch** | ✅ **512 MiB** | 依 DE | 极简 ~2 GB ◐ |
| Debian 13 | ❌ 无公开精确值 | 依 DE | ❌ 无公开 |
| NixOS | ❌ 无公开 | 依 DE | ❌ 无公开 |
| Alpine | ~128 MB（无 GUI）◐ | — | 极小 |

> ❌ **各发行版「最小安装（无桌面）」的内存占用缺乏统一公开基准。** Phoronix 的 GNOME/KDE 对比为 netbook 时代历史数据，不宜引用为 2026 数值。

---

# Part III · 体验层

# 第 10 章 桌面环境：KDE vs GNOME

## 10.1 版本与支持周期

| | KDE Plasma | GNOME |
|---|---|---|
| 当前版本 | **6.7.5** | **51 "A Coruña"**（2026-09-16） |
| 下一版本 | **6.8 于 2026-10-14 发布 = 首个 Wayland-only** | — |
| **LTS** | ✅ **6.6 是真 3 年 LTS（至 2029）** | ❌ **官方无 LTS** |
| 治理 | KDE e.V. | ⚠️ **GNOME Foundation FY2025-26 预算 $435k（较上年 $586k 腰斩），仅剩 3 名全职员工** |

## 10.2 游戏特性时间差

| 特性 | KDE | GNOME | 领先 |
|---|---|---|---|
| **HDR** | 6.0 / 6.1 | 48 | **KDE 早 13 个月** |
| **VRR** | 早期 | 较晚 | **KDE 早 2 年以上** |
| explicit sync | 较晚 | 较早 | GNOME 早 3 个月 |

**SteamOS 桌面模式用 KDE Plasma**，Valve 定制 LAVD 调度器 + 控制器延迟 100–500µs。

## 10.3 游戏性能（结论矛盾，不可作为选型依据）

| 来源 | 时间 | 结论 |
|---|---|---|
| **Phoronix** | 2026-03 | KDE 领先 |
| **TechPowerUp** | 2026-07 | GNOME 微弱领先 **1.7%** |

**两者结论相反。差距在个位数百分比以内，不足以作为选型依据。** 差异来自硬件/画质/方法。

## 10.4 内存占用

| | KDE | GNOME |
|---|---|---|
| 实测区间 | 约 600–900 MB | 约 900 MB–1.3 GB |

> ⚠️ **排除的不可信数据**：网络流传「GNOME Shell RSS 230MB / plasmashell 655MB」来自一篇版本自相矛盾的文章（标题写 Plasma 6.3、终端显示 6.6.4、又提 Kernel 7.0），**疑似 AI 生成，已剔除**。

## 10.5 其他维度

- **无障碍**：✅ **GNOME 明确更好**（Orca 与 GTK 紧耦合）—— 这是唯一有第三方明确结论的维度
- **稳定性**：**两者崩溃率均无公开数据**；GNOME 的不稳定主要来自扩展生态（大版本升级后约 **73% 扩展失效**）
- **纠错与支援**：KDE 有 KDE e.V. + Bugzilla；GNOME 有 GitLab + Discourse，但基金会财务腰斩是治理风险

## 10.6 本章结论

| 需求 | 选择 |
|---|---|
| 游戏 / HDR / 可变刷新率 | **KDE Plasma** |
| 无障碍 / 简洁 / 一致性 | **GNOME** |
| 要长期稳定支持 | **KDE Plasma 6.6 LTS**（GNOME 无 LTS） |
| 要活跃的第三方扩展 | ⚠️ 两者都有生态脆弱性 |

---

# 第 11 章 游戏性能优化

## 11.1 六层性能模型

| 层 | 内容 | 影响 |
|---|---|---|
| 1 | 内核 / 调度器 / governor | **最大**（尤其单线程瓶颈游戏） |
| 2 | 图形栈（Mesa / 驱动） | 大 |
| 3 | 合成器 / 桌面环境 | 中 |
| 4 | Proton / 兼容层 | 中 |
| 5 | 游戏本体设置 | 大 |
| 6 | 硬件 | 决定性 |

## 11.2 图形栈新鲜度

| 发行版 | Mesa 版本 | 评价 |
|---|---|---|
| Arch | **26.2.4** | 最新 |
| openSUSE TW | **26.2.x** | 与 Arch 持平 |
| **NixOS stable** | **25.2.6** | ⚠️ **落后约一年** |

## 11.3 关键组件

- **`scx_lavd`**（Igalia 为 Steam Deck 开发，原为游戏场景）：三发行版都可用
  - NixOS：`services.scx` 一行声明式启用（最优雅）
  - Arch：`scx-scheds` **1.1.3**（最新）
  - openSUSE TW：`scx` **1.0.16**（落后）
- **NTSYNC**：Linux 6.14 进主线，**Fedora 44 首个默认启用**；三发行版内核都 ≥6.14，差异只在是否默认加载
- **CachyOS 收益**：Phoronix 实测**个位数百分比**，**非营销所说的翻倍**

## 11.4 三个具体的坑（已验证）

| 坑 | 说明 |
|---|---|
| **Tumbleweed NVIDIA 是 KMP 内核模块包** | **内核升级会导致驱动损坏**（2026 年 6.18 事件） |
| **Tumbleweed 的 AMD 32 位 Vulkan 默认不装** | 需手动 `zypper in libvulkan_radeon-32bit` |
| **NixOS `hardware.graphics.enable32Bit` 默认 false** | 漏设导致 **Proton 黑屏** |

## 11.5 RimWorld 特化建议（用户为 RimWorld 1.6 玩家）

RimWorld 是 **Unity/Mono 单线程瓶颈**游戏：

1. **第 1 层（内核/调度器/governor/taskset）远比第 2 层（图形栈）重要**
2. **Performance Fish 模组是最大单一提升手段**
3. 图形栈优化对 RimWorld 几乎无意义

> ⚠️ **三发行版无任何公开游戏帧率对比数据。**

---

# 第 12 章 软件新鲜度与平滑升级

## 12.1 核心重构：「滞后 ≤1 个月」不是单一数字

**没有发行版对所有组件都做到 ≤1 个月。** 必须分组件测量。

## 12.2 Fedora 的杀手锏

✅ **Fedora Mesa 永久 updates 例外**：2026-04-07 FESCo 正式授予（ticket #3584），Phoronix 称与内核「same treatment」。

**这是唯一既有 6 个月发布制的稳定性、又能在版本内升 Mesa 大版本的发行版。**

| 组件 | Fedora 稳定版内是否 rebase |
|---|---|
| 内核 | ✅ 永久例外 |
| Mesa | ✅ 永久例外 |
| GNOME / Plasma 大版本 | ❌ |
| 编译器 / Python | ❌（滞后约 6 个月） |

## 12.3 其他结构性方案

| 方案 | 状态 |
|---|---|
| **Fedora Atomic / Bazzite** | ✅ 每日重建；⚠️ **不支持跳版本**（官方原文 "Skipping major releases is currently untested and is thus not supported"） |
| **openSUSE Aeon / Kalpa** | ⚠️ **Aeon = beta、Kalpa = alpha**；`transactional-update.timer` 每日 00:00–02:00；health-checker 自动回滚 |
| **Manjaro stable** | ◐ 官方延迟约两周（Wiki 原文 "roughly a couple of weeks"） |
| **Debian testing** | 迁移延迟 **10/5/2 天**；⚠️ **冻结期退化到数月**；⚠️ **安全更新不受及时支持** |
| **Ubuntu 过渡版** | ⚠️ **不跨大版本 rebase Mesa**（26.04 锁 26.0.x） |
| **KDE neon** | ⚠️ **只有 KDE 生态新**，Mesa/内核停在 Ubuntu 24.04（约 2 年旧） |
| **Clear Linux** | ❌ **已于 2025-07-18 停止开发** |

## 12.4 最优解排序

1. **Fedora Workstation / KDE**
2. **Fedora Atomic + Bazzite**
3. **Aeon / Kalpa**
4. **Manjaro stable**
5. **Debian testing**
6. **任意发行版 + Flatpak / distrobox / Nix**（零取舍，最被低估）

---

# 第 13 章 文档、生态与第三方支持

## 13.1 文档规模（可量化）

| 发行版 | 文档体系 | 量化事实 |
|---|---|---|
| **Arch** | **ArchWiki** | ✅ **29,799 页 / 4,453 条目 / 892,004 次编辑 / 68,767 用户 / 241 活跃用户 / 12 管理员** |
| **Ubuntu** | Ask Ubuntu | ✅ **425,477 问题 / 2,187,929 用户 / 540,591 回答** |
| **Debian** | Policy Manual + Reference + Wiki | ✅ Policy Manual v4.7.4.1 |
| **Fedora** | docs.fedoraproject.org（Quick Docs） | ✅ 以短篇 HOW-TO/FAQ 为主，非全覆盖手册 |
| **openSUSE** | Wiki + doc.opensuse.org | ✅ 官方手册 + 社区 Wiki 双轨 |
| **NixOS** | nix.dev + manual + wiki + Nix Pills | ⚠️ **文档至少分散在 5 处，官方 Wiki 与非官方 Wiki 并存** |

**ArchWiki 地位**：社区普遍称其为「Linux 最好的文档」—— 属二手评价（无客观排名），但**其规模（近 90 万次编辑）在所有发行版 Wiki 中最高**（已核实）。

**NixOS 文档是公认弱点**：多篇独立批评一致指出「分散、过时、新手不友好」，需读 nixpkgs 源码才能解决晦涩错误。

## 13.2 中文资源

| 发行版 | 中文社区 |
|---|---|
| Arch | ✅ wiki.archlinuxcn.org + forum.archlinuxcn.org |
| Debian | ✅ debiancn.org + forums.debiancn.org |
| openSUSE | ✅ forum.suse.org.cn + opensusecn.org |
| NixOS | ✅ wiki.nixos.cn |
| Ubuntu | ❌ 中文社区活跃度**无公开量化数据** |

## 13.3 学习曲线

- 无权威排名。社区共识（⚠️二手）：**Gentoo（编译）> NixOS（Nix 语言）> Arch（DIY 但不编译）**
- **NixOS 的 Nix 语言被反复评为「最不直觉」，是首要采纳障碍**
- **AI 友好度**：ArchWiki 是标准 MediaWiki，**有开放 API、可结构化抓取**（已实测）；这对 RAG / LLM 运维友好。NixOS 因文档碎片化，社区反需「靠 LLM 把文档拼起来」，而 AI 又易幻觉出不存在的 option。

## 13.4 商业软件官方支持的发行版

| 软件 | 官方支持的发行版 |
|---|---|
| **Docker Desktop** | Ubuntu、Debian、RHEL、Fedora；⚠️ **Arch 为实验性、未测试验证** |
| **Steam** | **推荐最新 Ubuntu LTS**（Valve 测试最多） |
| **Google Chrome** | Ubuntu 18.04+、Debian 10+、openSUSE 15.5+、Fedora 39+ |
| **Microsoft Edge** | 同上（2026-08-31 对齐 Chromium） |
| **VS Code** | 官方 .deb/.rpm/Snap；**Arch、Nix 为社区维护** |
| **NVIDIA CUDA** | Ubuntu、RHEL/Alma/Rocky/Oracle、Fedora、SLES、openSUSE Leap、Debian、Amazon Linux、Azure Linux |
| **SQL Server** | ⚠️ **2025 起仅 RHEL + Ubuntu（SLES 被移除）** |
| **MATLAB R2026b** | Ubuntu 24.04/22.04、Debian 13/12、RHEL 10/9/8、SLED/SLES 15 SP4+ |
| **DaVinci Resolve** | ⚠️ **官方仅 CentOS 7.3 / Rocky 8.6+**，其他需社区方案 |
| **Zoom** | Debian、Ubuntu、Linux Mint、**Arch** |
| Slack | 提供 .deb / .rpm |
| Spotify / Discord / 1Password | 提供 .deb/.rpm；❌ **无官方「支持发行版」清单** |

> **共性结论**：商业软件官方支持高度集中在 **Ubuntu LTS + RHEL + Fedora + Debian + openSUSE**；**Arch / NixOS 普遍依赖社区包或 Flatpak**；**Alpine 几乎无桌面商业软件支持**。

## 13.5 Flatpak / Snap / AppImage

| 机制 | 量化事实 |
|---|---|
| **Flathub** | ◐ 总下载 **4,816,770,277**；桌面应用 **3,699**；已验证应用 **2,198** |
| **Snap Store** | ❌ **无公开应用总量**（Canonical 未发布） |
| **默认预装** | Fedora、openSUSE、Linux Mint 默认 Flatpak；**Ubuntu 默认 Snap、不预装 Flatpak** |

## 13.6 第三方仓库机制

| 机制 | 归属 | 规模 |
|---|---|---|
| **AUR** | Arch | ◐ **121,709 包** |
| **nixpkgs** | NixOS | ✅ **>140,000 包** |
| **OBS** | openSUSE | ⚠️ 官方称「近 30,000 用户构建 140,000+ 包」 |
| **COPR** | Fedora | ❌ 包总数无公开数据 |
| **PPA** | Ubuntu | ❌ 包总数无公开数据 |

**AUR 的独特性**：唯一以「用户提交 PKGBUILD + 社区投票」为主、规模达 12 万级的第三方源。⚠️ 但 2026-07 起**暂停「包认领」功能**，是其治理风险。

---

# 第 14 章 容器与云场景

## 14.1 Docker Hub 官方镜像拉取量（✅ 独立核实，2026-10-12）

| 镜像 | 累计拉取量 |
|---|---|
| **alpine** | **12,350,838,923**（123.5 亿） |
| **ubuntu** | **10,099,287,939**（101.0 亿） |
| debian | 1,754,964,165（17.5 亿） |
| centos | 1,186,168,050（11.9 亿） |
| fedora | 137,108,374（1.37 亿） |
| rockylinux | 46,005,170（4600 万） |
| **archlinux** | **34,549,120**（3455 万） |

## 14.2 基础镜像大小

| 镜像 | 压缩拉取大小 | libc |
|---|---|---|
| busybox | ~1.4 MB | musl |
| **alpine:latest** | **~3.2 MB** | musl |
| debian:bookworm-slim | ~28 MB | glibc |
| ubuntu:24.04 | ~29 MB | glibc |
| debian:bookworm | ~49 MB | glibc |

**Alpine 约为 Debian slim 的 1/9。** 代价：musl 与 glibc 差异导致部分 native wheel / 预编译二进制不兼容。

## 14.3 云厂商官方镜像

| 云 | 官方提供的发行版 |
|---|---|
| **GCP** | Debian、Ubuntu、RHEL、RHEL for SAP、Rocky（含 NVIDIA）、AlmaLinux、CentOS、SLES（含 SAP）、openSUSE、Fedora CoreOS、COS；**SLES/RHEL/Windows 为付费 premium** |
| **AWS** | Amazon Linux、RHEL、SUSE、Ubuntu、Debian（Marketplace） |
| **Azure** | Ubuntu、RHEL、SLES、Debian 等（Azure Linux 为自研） |

## 14.4 服务器/企业定位

- **RHEL / SLES**：企业级付费支持（GCP/AWS 均列为 premium）
- **Ubuntu Server**：Canonical 商业支持，**商业软件首选**（Steam / Chrome / SQL Server / MATLAB 均首选 Ubuntu LTS）
- **Debian**：社区维护、跨架构最广（「Universal OS」，13 版 69,830 包、多架构）
- **Alpine**：容器/嵌入式，商业桌面软件几乎零支持

## 14.5 云原生专用 OS 的基础

| 系统 | 基础 |
|---|---|
| **Bottlerocket** | ⚠️ AWS 自研、Rust 实现、**非某发行版衍生** |
| **Flatcar** | ⚠️ **CoreOS Container Linux 的直接 fork**（Gentoo 血统） |
| **Talos Linux** | ⚠️ 从零构建、**无基础发行版**、纯 API 管理 |
| **Fedora CoreOS** | ✅ 基于 Fedora |
| **openSUSE Leap Micro** | ✅ 基于 openSUSE |
| **Container-Optimized OS (COS)** | ⚠️ Google，基于上游/Chromium OS 血统 |

---

# Part IV · 智能层

# 第 15 章 LLM 介入系统运维

## 15.1 七维评分

| 发行版 | AI 了解度 | 系统透明 | 日志清晰 | 步骤规范 | 少人工 | 公告预警 | 保护措施 | **合计** |
|---|---|---|---|---|---|---|---|---|
| **Aeon / MicroOS** | 3.5 | 4.0 | 4.0 | 4.0 | **4.5** | 3.5 | **4.5** | **27.5** |
| **Fedora Atomic** | 4.0 | 4.0 | 3.5 | 4.0 | 4.0 | 3.5 | 3.5 | **26.5** |
| **openSUSE TW** | 3.5 | 3.5 | **4.5** | 3.5 | 3.5 | 3.5 | 3.5 | **25.5** |
| **NixOS** | 3.5 | **4.5** | 3.0 | 4.0 | 3.0 | 3.0 | 3.0 | **24.0** |
| **Ubuntu** | **4.5** | 3.5 | 3.5 | 3.5 | 3.0 | **4.5** | 2.5 | **24.0** |
| **Arch** | 3.0 | 3.0 | 3.0 | 3.0 | 2.5 | 3.0 | 3.0 | **20.5** |

## 15.2 两条路线

| 场景 | 选择 | 理由 |
|---|---|---|
| **AI 全无人值守** | **openSUSE MicroOS / Aeon** | 唯一「自动更新 + 失败自动回滚」闭环 + **唯一默认开 Btrfs 快照** |
| **AI 有人监督** | **NixOS** | 系统状态即文本 + 构建期校验 + generation 回滚 |

## 15.3 关键事实

- ✅ **RHEL 10 是唯一官方提供 MCP server 的发行版**（RHEL Lightspeed）；Red Hat Developer 2026-10-08 有实操文章
- ✅ **Arch 的 `archlinux.org/feeds/news/` 是唯一有专门「manual intervention」公告机制的发行版**（RSS 已核实）；近例含 mkinitcpio 42 TPM2、NVIDIA 590 弃 Pascal、xz 后门
- ✅ **Ubuntu 安全 API 最完善**（`/security/notices.json` + OVAL + 3 种 JSON）
- ✅ **OSV.dev 不覆盖 Arch / Fedora / openSUSE / NixOS**
- ✅ **openSUSE 是唯一默认 Btrfs + 自动快照（zypper 事务 pre/post）+ GRUB 启动快照 + snapper rollback 的发行版**
- ✅ **NixOS 默认不启用 Btrfs 快照**（手册分区示例用 ext4）
- ✅ **Fedora Workstation 默认 Btrfs 但默认不启用快照**；Ubuntu 24.04 安装器**已移除 ZFS 选项**
- ✅ **NixOS generation ≠ Btrfs 快照**：generation 只管声明式配置，DB / 用户文件 / 日志不受管

## 15.4 关键洞察

> **公告预警不需要跟发行版绑定** —— AI 可同时订阅 Arch news（破坏性变更）+ OSV.dev（漏洞）+ 发行版自身 security-announce。

---

# 第 16 章 AI 协同管理的实践

## 16.1 三类实践的分布

| 你要的 | 选它 | 硬证据 |
|---|---|---|
| **官方工程化 / 企业可用** | **RHEL**（Fedora 作试验田） | GitHub 组织 `rhel-lightspeed` 有 **6+ 个 MCP 仓库**；`docs.redhat.com` 有正式 Getting Started |
| **社区生态 + 真实实践最厚** | **NixOS** | 唯一「查询 853★ → 操作 16★ → 回滚 skill → 4 个 AI skills 仓库」全链路齐备 |
| **产品化 MCP 覆盖最广** | **openSUSE / SUSE** | Multi-Linux Manager 5.2 原生 MCP + Observability MCP + **openQA 原生 MCP** |
| **AI-native 桌面** | **Bluefin / Bazzite** | 内置 goose 随镜像分发 |
| **基本为零** | **Arch / Debian / Ubuntu** | 搜 `arch linux mcp pacman` = **0 结果** |

## 16.2 RHEL：官方投入最深（✅ 独立核实）

`rhel-lightspeed` 组织的仓库（2026-10-12）：

| 仓库 | ★ | 更新 |
|---|---|---|
| `linux-mcp-server` | **317** | 2026-10-10 |
| `docs2db` | 48 | 2026-10-11 |
| `command-line-assistant` | 44 | 2026-10-06 |
| `okp-mcp` | 19 | 2026-10-12 |
| `sysadmin-agents` | 8 | 2026-07-06 |
| `goose-proxy` / `goose` | 5 / 4 | 2026-10-12 |
| `docs2db-mcp-server` | 4 | 2026-07-30 |
| `redhat-status-mcp` | 2 | 2026-07-06 |
| `rhel-lightspeed-gitops` | 1 | 2026-07-06 |
| `HEAL` | 0 | 2026-06-01 |

**官方文档层证据**（比 star 更重要）：`docs.redhat.com` 有 **"Getting started with MCP server for Red Hat Lightspeed"**（更新至 2026-09-30）—— **唯一把 MCP server 写进正式产品文档的发行版厂商**。

## 16.3 NixOS：社区全链路闭环

```
查询  utensils/mcp-nixos        853★  MIT，2026-09-05
操作  JEFF7712/nix-agent         16★  2026-10-12 仍更新
回滚  yolo-labz/nixos-ops-skill   0★  Claude Code 的 rebuild/debug/generations
知识  michalzubkowicz/nixos-management-skill  61★
      marceloeatworld/nixos-ai-skill          30★
      Kihara777/NixKits                       28★（中文）
      z1-0/skills-nix                         17★
```

**四个环节各有独立项目 —— 其他任何发行版都不存在此现象。** 根因：NixOS 系统状态是纯文本 + 声明式，天然适合 LLM 读写。

## 16.4 修正的结论

| 上一轮说法 | 实测 |
|---|---|
| `bluefin-mcp` 是 Bluefin 的活跃方案 | **5★，archived: true（已归档）** |
| `vespo92/mcp-nixos-ops` 是 NixOS 操作类 MCP | **0★**、创建当天即停更、无 license |
| `bolivian-peru/os-moda` 是「AI OS 实践」 | 120★ 属实，但作者自述 **"Research-grade; run it on a disposable box, not production"** |
| `oborchers/mcp-server-pacman` 疑似 Arch 管理工具 | 是**包索引查询器**，非系统管理 |
| goose 在 `block/goose` | **已迁至 `aaif-goose/goose`（55171★）** |

## 16.5 风险侧

- ⚠️ **2026-04-27 Cursor + Railway 的 AI agent 自主删除生产数据库**（HN 638 分）—— 最著名的翻车案例
- ⚠️ NixOS Discourse（2026-04-26）有人主张「用 agent 配置就违背了用 NixOS 的意义」，帖内无成功实践报告
- ⚠️ Kiteworks《Why Sysadmins Still Don't Trust AI With Production Systems》(2026-08-03)

> **2026-10 这个时间点，任何「用 LLM 管系统」的方案，默认前提都应该是「快照/回滚兜底 + 有人复核」。**

---

# Part V · 组织层

# 第 17 章 社区治理、规模与前景

## 17.1 治理模型

| 发行版 | 治理模型 | 最高决策体 | 商业关系 |
|---|---|---|---|
| **Arch** | 社区自治 + 单一负责人 | **Project Leader（无「理事会」）** | 财务经 SPI |
| **NixOS** | 基金会 + 选举委员会 | NixOS Foundation + Steering Committee | 荷兰 Stichting |
| **openSUSE** | 社区 Board + 赞助方 | Board（5 选举 + 1 主席） | 主席由 SUSE 任命 |
| **Fedora** | 社区 + 公司深度参与 | Council（战略）/ FESCo（技术） | Red Hat 持 3 常任席位 |
| **Debian** | 纯社区自治 | DPL + Technical Committee | SPI 托管 |
| **Ubuntu** | 公司主导 | Canonical + Community Council | Canonical 全资 |

> ⚠️ **常见前提错误**：**Arch 没有「Arch Council」这一机构**。最高负责人是 Project Leader。

## 17.2 2026 选举

| 发行版 | 结果 | 投票率 |
|---|---|---|
| **Debian** | ✅ **Sruthi Chandran**（无对手），任期 2026-04-21 ~ 2027-04-20 | **347 / 1,039** |
| Arch | ◐ anthraxx 连任（2026-06-04，任期 2 年） | — |
| openSUSE | ◐ Simon Lees、Shawn W Dunn（第 19 届，2026-03-09） | 162 / 521 |
| Fedora | ◐ Council 2 席 / FESCo 5 席（F44，2026-06-13） | 204 / 199 |

**Debian DPL 已独立核实**：`bits.debian.org/2026/04/dpl-elections-2026.html` 原文确认。Sruthi Chandran 也是**首位女性、首位亚洲 DPL**。

## 17.3 NixOS 治理危机完整时间线

| 日期 | 事件 |
|---|---|
| 2024-04-21 | 匿名 + 署名者公开信，指控领导层危机 |
| **2025-09-27** | **Moderation team 7 人中 5 人立即辞职**，抗议 Steering Committee 干预 |
| **2026-08-07/08** | **Nixpkgs 核心团队解散**（成立仅 10 个月；成员 alyssais、emilazy），理由：SC 微观管理、沟通失灵、授权不清、倦怠。此前曾 onboard 19 名新 committer |
| **2026-09-22** | 宣布**第三次** SC 选举，投票期 **2026-10-15 ~ 11-01** |

> **这是三次连续事件，不是孤立事故。** 且第三次 SC 选举的投票期**在本报告发布时尚未开始** —— NixOS 目前处于**治理空窗期**。

## 17.4 社区规模

| 发行版 | 指标 | 数值 |
|---|---|---|
| **Debian** | 有投票权 Developers | ✅ **1,039** |
| Debian | 近 12 月贡献者 | ◐ 1,384 人 / 31 团队 |
| **Arch** | Developers | ✅ **23** |
| Arch | Package Maintainers / Support Staff | ◐ 70 / 49 |
| openSUSE | Members | ◐ ~521 |
| Fedora | Packagers | ⚠️ ~325（2026 初 ~350） |
| Fedora | Count Me 周活系统 | ⚠️ ~100 万（+9% YoY） |
| Ubuntu | Ubuntu Members | ◐ 378 直接 / 584 总计 |
| **NixOS** | 贡献者总数 | ❌ **未找到** |
| Ubuntu | MOTU 人数 | ❌ **未找到** |

**Fedora packager 长期下降**：2020 初 >420 → 2023 约 410→340 → 2026 初 350→325 ⚠️ —— **最明确的人力衰退信号**。

## 17.5 资金状况

**NixOS Foundation —— 连续两年亏损**

| 年份 | 净收支 | 权益（累计） |
|---|---|---|
| 2023 | — | **€248,993** |
| 2024 | **−€55,862**（首次亏损） | €193,130 |
| 2025 | **−€25,019**（含 €38k 补缴 2021-23 公司税） | **€168,111** |

**权益两年下降 €80,882（约 32%）。**

其他：Debian / SPI 2025 审计财报约 2026-11 发布；GNOME 基金会 2024-10 批准削减预算方案。

## 17.6 未来前景

| 发行版 | 路线图 | 风险 |
|---|---|---|
| **Fedora** | 维持 6 个月周期；**AI Developer Desktop 获 Council 批准**；**Hummingbird**（容器化滚动）2026-05 宣布 | ⚠️ packager 下降；探索 Open Collective |
| **openSUSE** | ⚠️ **Slowroll 仍 beta（2026-09）**；Aeon；Kalpa | 未发现资金危机 |
| **Debian** | Debian 14 **Forky**（预计 2027）；15 = **Duke** | 未发现资金危机 |
| **Ubuntu** | **26.04 LTS（2026-04-23）支持至 2031-04** | 未发现 |
| **Arch** | **无官方路线图** | ⚠️ **2026-06-11 AUR 供应链事件（400+ 包被劫持）；2026-08 暂停 AUR 包收养** |
| **NixOS** | flakes 稳定化进行中（RFC 136），**flakes 仍为实验特性** | ⚠️ **治理危机 + 资金** |

---

# Part VI · 决策

# 第 18 章 综合选型决策

## 18.1 按场景推荐

| 场景 | 首选 | 次选 | 避免 |
|---|---|---|---|
| **企业生产服务器** | RHEL | Ubuntu LTS / Debian | Arch、NixOS |
| **个人主力机（要稳）** | Fedora Workstation | Debian stable | — |
| **个人主力机（要新）** | openSUSE Tumbleweed | Arch | — |
| **学习 Linux** | Arch（ArchWiki） | Fedora | — |
| **游戏** | CachyOS / Bazzite | Arch + scx_lavd | NixOS stable（图形栈落后） |
| **桌面最新 + 质量门禁** | openSUSE Tumbleweed | Fedora Rawhide | — |
| **完全不想维护** | Aeon / MicroOS | Fedora Atomic | Arch |
| **AI 无人值守运维** | MicroOS / Aeon | Fedora Atomic | Arch |
| **AI 有人监督运维** | NixOS | openSUSE TW | — |
| **容器 / 云原生** | Alpine | Debian slim | Arch |
| **要最好的文档** | Arch | Debian | NixOS |
| **要长期稳定支持** | Ubuntu LTS（10 年） | Debian LTS（5 年） | Arch、NixOS（7 个月） |

## 18.2 风险矩阵

| 发行版 | 主要风险 | 严重度 |
|---|---|---|
| **NixOS** | 治理危机（3 次连续）+ 基金会连亏 2 年（权益 −32%）+ 第三次 SC 选举未开始 | 🔴 **高** |
| **Arch** | AUR 供应链事件 + 暂停包认领 + 官方零安全投入 + 9 人志愿安全团队 | 🟠 **中高** |
| **openSUSE TW** | Slowroll 仍 beta + 可复现构建测试停更（2018）+ Repology 数据质量差 | 🟡 **中** |
| **Fedora** | packager 数持续下降（420→325）+ 依赖 Red Hat 预算 | 🟡 **中** |
| **Debian** | LTS 安全支持由志愿者承担 + testing 冻结期安全更新滞后 | 🟢 **低** |
| **Ubuntu** | universe 仓库仅 best-effort 安全支持 + Canonical 单方决策 | 🟢 **低** |
| **Alpine** | musl 兼容性 + 商业桌面软件几乎零支持 | 🟡 **中**（容器场景外） |

## 18.3 决策树

```
你的首要约束是什么？
│
├─ 要进企业生产、要支持合同
│   └─ RHEL（免费试验田用 Fedora）
│
├─ 完全不想维护系统
│   └─ Aeon / MicroOS（唯一自动更新+失败自动回滚闭环）
│
├─ 要长期稳定（5 年以上）
│   ├─ 要商业支持 → Ubuntu LTS（Pro 可到 10 年）
│   └─ 要纯社区   → Debian LTS（约 5 年）
│
├─ 要最新软件
│   ├─ 要质量门禁 → openSUSE Tumbleweed（openQA 650 套件）
│   ├─ 要可精确回滚 → NixOS（但有治理风险）
│   └─ 要最好的文档 → Arch
│
├─ 游戏为主
│   └─ CachyOS / Bazzite（收益是个位数百分比）
│
├─ 容器 / 云原生
│   └─ Alpine（123.5 亿次拉取，3.2 MB）
│
└─ 要用 AI 运维
    ├─ 无人值守 → MicroOS / Aeon
    └─ 有人监督 → NixOS（唯一从架构上消灭配置漂移）
```

---

# 第 19 章 数据缺口与纠错记录

## 19.1 本轮纠正的 11 处错误/矛盾

| # | 项 | 错误说法 | 纠正后 |
|---|---|---|---|
| 1 | **Arch 孤儿包数** | 303 | ✅ **250**（Arch 官方 API，两种口径一致） |
| 2 | **Arch Developers** | 子代理 A 说 17；子代理 B 说 23 | ✅ **23**（官方 people 页） |
| 3 | **bluefin-mcp 状态** | Bluefin 的活跃 MCP 方案 | **5★ 且已归档（archived: true）** |
| 4 | **vespo92/mcp-nixos-ops** | NixOS 操作类 MCP 证据 | **0★、创建当天停更、无 license** |
| 5 | **os-moda 可用性** | 120★ 的 AI OS 实践 | 作者自述 **"not production"** |
| 6 | **mcp-server-pacman** | 疑似 Arch 系统管理工具 | 是**包索引查询器** |
| 7 | **JEFF7712/nix-agent** | 存在性存疑 | ✅ **确实存在**（16★，2026-10-12 更新） |
| 8 | **goose 仓库位置** | `block/goose` | **已迁至 `aaif-goose/goose`（55171★）** |
| 9 | **Arch 无安全公告** | 常见说法 | Arch **有** ASA 机制（9 人团队），**但 tracker 停更** |
| 10 | **mkRemovedOptionModule** | 官方文档称 "warning" | **实现是 `throw`（源码核实）** |
| 11 | **Arch 有「理事会」** | 常见说法 | **Arch 无 Council，最高是 Project Leader** |

## 19.2 结构性数据缺口（本身就是结论）

| 缺口 | 说明 |
|---|---|
| **跨发行版 time-to-patch 数据集** | ❌ **不存在**。唯一数据源（Vulnpatch）已撤回全部数字 |
| **「LLM 最了解哪个发行版」** | ❌ 无任何公开数据 |
| **「LLM 生成 NixOS 配置成功率」** | ❌ 无任何实测 |
| **各发行版崩溃率** | ❌ 无公开数据 |
| **「关键包指定维护者」清单** | ❌ 六家均无 |
| **最小安装内存基准** | ❌ 无统一公开基准 |
| **Fedora / openSUSE 孤儿包总数** | ❌ 无公开数据 |
| **Arch / NixOS 可复现构建覆盖率** | ❌ 无公开数字 |
| **个人级包维护量分布** | ❌ 无权威统计 |
| **Snap Store 应用总数** | ❌ Canonical 未公开 |
| **COPR / PPA 包总数** | ❌ 无公开数据 |
| **NixOS 贡献者总数 / Ubuntu MOTU 人数** | ❌ 未找到 |
| **三发行版游戏帧率对比** | ❌ 无公开数据 |
| **Slowroll 是否脱离 experimental** | ❌ 未确认（2026-09 仍 beta） |

## 19.3 未能独立核实的项

| 项 | 原因 |
|---|---|
| **Repology 全部数字**（包数 / outdated / problems） | **API 返回 403 Forbidden**（带 UA 亦被拒） |
| Arch Package Maintainers = 70 / Support Staff = 49 | 页面可抓但解析未完成 |
| Fedora packager ≈325 | 仅二手 LWN 来源 |
| Arch Project Leader 2026 选举详情 | 子代理来源，未核实官方公告页 |
| openSUSE Board 162/521 投票率 | 子代理来源 |
| Flathub 下载量 48.1 亿 | 子代理读取网页（API 返回空） |
| AUR 121,709 包 | 子代理读取网页（RPC 空参数返回 0） |

## 19.4 抓取失败说明

| 站点 | 障碍 | 替代方案 |
|---|---|---|
| `wiki.archlinux.org` | Anubis PoW 反爬 | Arch 官方包库 API、ArchWiki API（部分可用） |
| `build.opensuse.org` | PoW 反爬 | rpmfind 文件列表 |
| `repology.org/api` | 403 Forbidden | 网页读取（已标注） |
| `manpages.opensuse.org` | 返回空 | SUSE 官方博客、中文社区镜像 |
| `docs.fedoraproject.org`（部分页） | 返回空 | FESCo 工单交叉佐证 |
| `en.opensuse.org` 主站 | PoW 防护 | 镜像站、`suse.org.cn` |

---

# 附录 A 一页速查表

| | Arch | NixOS | openSUSE TW | Fedora | Debian | Ubuntu |
|---|---|---|---|---|---|---|
| 发布模型 | 滚动 | 滚动+半年 | 滚动 | 6 个月 | ~2 年 | 6 个月/2 年 |
| 内核 | 7.2.7 | 6.18 LTS | 7.2.x | 7.2.6 | 6.12 LTS | 7.0 |
| 官方包数 | 16,008 | **149,566** | 17,270 | 82,747 | 69,830 | 39,336 |
| 核心维护者 | **93** | ❌ | ~521 | ~325 | **1,039** | 378 |
| 默认 MAC | ❌ 无 | ❌ 无 | SELinux | SELinux | AppArmor | AppArmor |
| 默认防火墙 | ❌ | ✅ | ✅ | ✅ | ❌ | 预装未启用 |
| 冲突处理 | pacnew | 声明式 | rpmnew | rpmnew | dpkg-dist | dpkg-dist |
| 三方合并 | ✅ pacdiff -3 | — | ❌ | ❌ | ⚠️ ucf | ⚠️ ucf |
| 孤儿包 | **250** | 结构上无 | ❌ | ❌ | 1,070 | — |
| 退役时限 | 无 | 无 | 无 | ✅ **6 周** | 无 | 无 |
| 安全团队 | 9 志愿者 | 志愿者 | **SUSE 专职** | Red Hat 代管 | 志愿者 | **Canonical 专职** |
| OSV.dev | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| CNA | ❌ | ❌ | ✅ | ✅ | ✅ Sub | ✅ |
| LTS 安全周期 | 无 | ~7 月 | Leap LTS | ~13 月 | ~5 年 | 5–10 年 |
| 文档规模 | **892k 编辑** | 分散 | 双轨 | Quick Docs | Policy Manual | Ask Ubuntu 42.5 万问 |
| 容器拉取量 | 3455 万 | — | 1152 万 | 1.37 亿 | 17.5 亿 | 101 亿 |
| 治理风险 | 🟠 中高 | 🔴 **高** | 🟡 中 | 🟡 中 | 🟢 低 | 🟢 低 |

---

# 附录 B 可复用验证命令

```bash
# ── GitHub：核实任意仓库真实状态（不依赖网页抓取）──────────────
curl -s "https://api.github.com/repos/OWNER/REPO" \
  | python -c "import sys,json;d=json.load(sys.stdin);print(d['stargazers_count'],d['pushed_at'],d['archived'])"

# 按 star 排序扫描某发行版生态
curl -s "https://api.github.com/search/repositories?q=nixos+mcp&sort=stars&order=desc&per_page=15" \
  | python -c "
import sys,json
for i in json.load(sys.stdin)['items']:
    print(f\"{i['stargazers_count']:>6}*  {i['full_name']:<40} {i['pushed_at'][:10]}\")"

# 列出厂商组织全部仓库（判断官方投入深度）
curl -s "https://api.github.com/orgs/rhel-lightspeed/repos?per_page=50&sort=updated" \
  | python -c "
import sys,json
for i in json.load(sys.stdin): print(f\"{i['stargazers_count']:>5}*  {i['name']}\")"

# ── Arch 官方 API ──────────────────────────────────────────
# 孤儿包计数
curl -s "https://archlinux.org/packages/search/json/?maintainer=orphan&limit=500" \
  | python -c "import sys,json;print(len(json.load(sys.stdin)['results']))"
# → 250

# ── openQA（openSUSE 的 QA 护城河）──────────────────────────
curl -s "https://openqa.opensuse.org/api/v1/test_suites" \
  | python -c "import sys,json;print(len(json.load(sys.stdin)['TestSuites']))"
# → 650
curl -s "https://openqa.opensuse.org/api/v1/machines" \
  | python -c "import sys,json;print(len(json.load(sys.stdin)['Machines']))"
# → 114

# ── Docker Hub 镜像拉取量 ──────────────────────────────────
for i in alpine ubuntu debian fedora archlinux; do
  curl -s "https://hub.docker.com/v2/repositories/library/$i/" \
    | python -c "import sys,json;d=json.load(sys.stdin);print(f\"{d['name']:<12} {d['pull_count']:>15,}\")"
done

# ── ArchWiki 文档规模 ──────────────────────────────────────
curl -s "https://wiki.archlinux.org/api.php?action=query&meta=siteinfo&siprop=statistics&format=json" \
  | python -c "
import sys,json
d=json.load(sys.stdin)['query']['statistics']
print('pages:',d['pages'],'articles:',d['articles'],'edits:',d['edits'],'activeusers:',d['activeusers'])"

# ── 配置漂移自查（任意发行版）─────────────────────────────
sudo etckeeper init && sudo etckeeper commit "初始状态"
find /etc -name '*.pacnew' -o -name '*.rpmnew' -o -name '*.dpkg-dist' -o -name '*.pacsave'
systemd-delta --type=overridden

# ── 各发行版配置冲突处理 ───────────────────────────────────
sudo pacdiff -3 --sudo        # Arch（唯一三方合并）
sudo rpmconf -a               # Fedora / openSUSE
rpmconf -D                    # Fedora 非交互审计
sudo systemctl start rpmconfigcheck   # openSUSE（有 service 无 timer）
ostree admin config-diff      # Fedora Atomic（看 /etc 漂移）
```

---

**报告结束**

*本报告基于 2026-10-12 及之前的公开数据。Linux 生态变化迅速，关键决策前请以官方最新公告为准。所有标注 ✅ 的数据已通过官方 API 独立核实；标注 ◐ 的数据来自子代理报告；标注 ⚠️ 的为二手来源。*
