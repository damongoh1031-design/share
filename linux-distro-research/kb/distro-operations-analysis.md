---
id: distro-operations-analysis
title: 发行版运营分析：社区规模 / 运行现状 / 套件源 / 包管理 / 漏洞修复
tags: [linux-distro, operations, package-management, repositories, vulnerability-response, community-scale, repology, osv]
created: 2026-10-13
updated: 2026-10-13
version: 1.0.0
status: stable
source: 3 个并行子代理调研 + 主调研员对全部关键数字做 curl/API 独立实测（2026-10-13）
confidence: 已核实
---

# 发行版运营分析（2026-10）

## 一句话结论

**运营五维没有全能冠军**：社区规模看 Debian（1,039 DD）、运行现状看 Fedora/Ubuntu、套件源看 NixOS（119k 项目）与 openSUSE（OBS 服务 21 发行版）、包管理看 NixOS（generation 原子回滚）、漏洞修复看 Ubuntu/Debian（唯一 OSV 覆盖 + 可执行 JSON API）。**Arch 是运营风险最高的一家**（tracker 停摆 + 4 人安全团队 + 无 CNA + 三连击事故）。

---

## 1. 社区规模

| 发行版 | 核心维护者 | 官方包数 | 包/人 |
|---|---|---|---|
| **Debian** | **1,039 有投票权 DD** | ~42k | ~40 |
| NixOS | 数千贡献者（无成员制） | 119k 项目 | — |
| openSUSE | ~521 members | 16k | ~31 |
| Fedora | ~325 packagers | 24k | ~74 |
| Ubuntu | 378 Members | 40k | ~106 |
| **Arch** | **23 Dev + 70 PM = 93** | 16,008 | **~172** |

- **Debian 是唯一「千人级」社区** → 无单点故障。
- **Arch 核心团队最薄且人均 172 包**（Debian 的 4.3 倍）→ bus factor 风险最高。
- **跨发行版比贡献者数必须说明口径**：NixOS 无成员制，GitHub 贡献者数与 DD 不可比。

### 治理个体事件（2025-2026）
| 事件 | 日期 |
|---|---|
| Arch 项目领导人连任（Levente "anthraxx" Polyák，任期两年） | **2026-06-04** |
| Debian 数据保护团队（DPT）集体离职 | 2026-01 |
| Arch arch-security 邮件列表停摆 >16 个月 | 2025-06-13 起 |
| NixOS 第三次 SC 选举投票期才开始 | 2026-10-15 起 |

---

## 2. 运行现状

### 当前发布状态（2026-10-13）
| 发行版 | 当前稳定版 | 发布日期 |
|---|---|---|
| Fedora | 44 | 2026-04-28（**45 target 2026-10-20**） |
| Ubuntu | LTS 26.04.1 / interim 25.10 | 2026-04-23 / 2025-10-09 |
| Debian | stable 13 trixie / testing 14 forky | 2025-08-09 |
| NixOS | 26.05 "Yarara" | 2026-06-01 |
| openSUSE | Tumbleweed 每日快照 / Leap 16.0 | Leap ≈ 2025-10 |
| Arch | 滚动，ISO **2026.10.01** | 2026-10-02 |
| Alpine | 3.23.0 | 2025-12-03 |

> **Arch 无版本号**：唯一锚点是月度 ISO（`YYYY.MM.DD`）。写文档别写"Arch 26.x"。

### 基础设施与事故
| 发行版 | 构建 | CI/QA | 2025-2026 事故 |
|---|---|---|---|
| Fedora | Koji | Zuul + openQA + Bodhi | 无重大 |
| Debian | buildd | autopkgtest | 无 |
| openSUSE | OBS（3 DC） | openQA（650 套件/114 机器） | **2025-12-01 OBS 中断 35 分钟**（Ruby gem 冲突） |
| Arch | build 机群 + rebuilderd | reproducible.archlinux.org | **三连击**（见下） |
| NixOS | Hydra | Zero Hydra Failures | Hydra 排队慢 |

**Arch 三连击**：
1. **2025-08-21** 官方公告持续 **DDoS 攻击**（打 archlinux.org / AUR / Forums）
2. **2026-06-12** 官方公告 **AUR 恶意包事件**（adoption 机制被滥用）
3. **2026-07-30** 紧急停用 package adoption

> **数字口径澄清**：媒体上 **"400+"** = 事件当时已移除的包数；**"1,500"** = 攻击者最终批量收养的包数。两者**不矛盾**，是不同口径，引用必须写明。

---

## 3. 套件源

### 官方仓库结构
| 发行版 | 分层 | 关键事实 |
|---|---|---|
| Arch | core / extra / multilib | **2023-05-19 `[community]` 并入 `[extra]` 后为空**；testing/staging 各拆 core/extra |
| NixOS | 无传统分层 | nixpkgs 单一 Git 仓库；channel = Hydra 测试过的快照分支，非独立二进制仓库 |
| openSUSE | OSS / Non-OSS / Update | Packman 是**第三方** |
| Fedora | fedora / updates / updates-testing / rawhide | **模块化已废弃**（F39 停建），F46 移除 DNF4 遗留 |
| Debian | main / contrib / non-free / **non-free-firmware** | non-free-firmware 是 **Debian 12 新增**（2022 GR） |
| Ubuntu | main / restricted / universe / multiverse | main=官方支持、universe=社区支持 |

### 第三方源
| 发行版 | 机制 | 规模 |
|---|---|---|
| Arch | **AUR**（PKGBUILD 脚本库，非二进制） | **121,822 包** |
| openSUSE | **OBS**（不只服务 openSUSE） | **~30,000 用户 / 140,000+ 包 / 21 发行版** |
| Ubuntu | PPA | >130,000 |
| Fedora | COPR | 无公开数 |
| NixOS | overlay / flake | — |
| Debian | 无官方（backports 算官方，best-effort） | — |

### 仓库规模与新鲜度（Repology 实测）
全局：**330,508 项目 / 5,036,835 包**

| 仓库 | 项目数 | 最新版比例 |
|---|---|---|
| nixpkgs unstable | 119k | 83.6% |
| nixpkgs stable 26.05 | 115k | 69.0% |
| AUR | 96k | 69.0% |
| Ubuntu 26.04 | 40k | 48.3% |
| Debian 13 | 38k | 40.9% |
| Fedora 43 | 24k | 56.8% |
| Fedora Rawhide | 22k | 74.4% |
| openSUSE Tumbleweed | 16k | 73.0% |
| **Arch** | 12k | **86.5%** |

> 反直觉：**Arch 官方仓库最小但最新鲜（86.5%）**；**AUR 比 Arch 官方大 8 倍**；Debian stable 只 40.9% 是设计选择。

---

## 4. 包管理

| 属性 | Arch | Fedora | openSUSE | Debian/Ubuntu | NixOS |
|---|---|---|---|---|---|
| 求解器 | 全量重算 | libsolv SAT | libsolv SAT | solver3（3.0） | 函数式+SAT |
| **原子性** | ❌ 无 | dnf history | snapper | 半完成态 | **generation** |
| 多版本共存 | ❌ | ❌ | ❌ | ❌ | ✅ |

- **pacman 无原子性是已核实缺陷**：事务中止时已执行的 remove 不回滚，可损坏 pacman 自身。
- **libsolv 是隐形基础设施**：zypper 与 dnf 共用同一 SAT 求解器，支持 rpm/deb/arch/apk。

### 生命周期极端对比
- **Fedora**：唯一硬性退役时限 —— **孤儿 6 周即退役**（FESCo 政策原文）。
- **Debian**：孤儿包可滞留十年（WNPP 实测 `dpkg-cross` 已 orphaned 3,695 天）。

### 关键安全守则
**Arch 绝不能用 `pacman -Sy pkg` 代替 `pacman -Syu`** —— 前者造成 partial upgrade，是毁系统最常见原因。

### 换代动向
| 项目 | 状态 |
|---|---|
| **ALPM**（Rust 重写 pacman） | Sovereign Tech Fund 资助 15 个月 |
| **apt 3.0** | 已发布 2025-04-05，solver3 回溯式 |
| **dnf5**（C++） | 已成 Fedora 默认 |
| **nixos-rebuild-ng**（Python） | 自 25.11 起默认 |

### 已知痛点
- **openSUSE**：zypper 刷新极慢（论坛实测 `zypper ref` **8 分 4 秒**）
- **Ubuntu**：snap 强制（Firefox/Chromium 默认 snap，26.04 仍如此）

---

## 5. 漏洞修复运营

### OSV.dev 覆盖（关键实测，用 `POST /v1/query`）
| 生态 | 结果 |
|---|---|
| Debian / Ubuntu / Alpine | ✅ 200 + 真实 CVE |
| openSUSE / SUSE | ⚠️ **200 但返回空 `{}`**（有名无实） |
| **Fedora / Arch / NixOS** | ❌ **400 `invalid ecosystem`**（根本不存在） |

> **最重要运营结论**：OSV-Scanner / osv-scalibr / 各类 SBOM 工具对 Fedora、Arch、NixOS **开箱即失效**。要自动化安全运维，这三家必须自建数据管道。

### 结构化 CVE 数据库（实测）
| 发行版 | 端点 | 实测 |
|---|---|---|
| Debian | `security-tracker.debian.org/tracker/data/json` | ✅ 82.5 MB / 4,073 源包 |
| Ubuntu | `ubuntu.com/security/cves.json` | ✅ 29 KB |
| Alpine | `secdb.alpinelinux.org/v3.22/main.json` | ✅ 90 KB |
| SUSE | `api.suse.com/security/cve` | ⚠️ 需认证（401） |
| Arch | `security.archlinux.org/issues/all.json` | ⚠️ 2444 条但**公告 2025-06 停发** |
| NixOS | `tracker.security.nixos.org` | ⚠️ **纯 JS 壳（1031 字节），无 API** |
| Fedora | Bodhi `?type=security` | ⚠️ 无独立库 |

**两个数据陷阱**：
- **Arch ASA「数据在场但停滞」**：JSON 仍返回 2444 条，只看它会误判为活跃；实际覆盖率 **<0.3%**（55 CVE vs Debian 同期 21,528）。
- **NixOS tracker 真实活跃**（`NIXPKGS-YYYY-NNNN`）—— 纠正"NixOS 无 CVE 追踪"的假设，但无 API。

### CNA 身份
| 有 | 无 |
|---|---|
| Red Hat / SUSE / Canonical / Debian / Fedora | **Arch / Alpine / NixOS** |

### 补丁最后一公里
- **Fedora Bodhi**：唯一显式可量化门槛 —— 普通 **1 karma/7 天**，关键路径 **2 karma/14 天**
- **Debian**：独立安全归档 security.debian.org（不等 point release）
- **Arch**：无专门安全仓库，完全依赖滚动节奏

### Debian Security Tracker 实测
| Suite | resolved | open |
|---|---|---|
| sid | 66,300 | 3,969 |
| forky (testing) | 60,006 | 3,528 |
| trixie (stable) | 56,220 | 7,849 |
| bookworm (oldstable) | 54,889 | 11,973 |

> **open 数随版本变老而上升** —— 这是"旧版支持"的真实成本。

---

## 可复用操作

```bash
# 1. OSV.dev 覆盖探测（改 ecosystem 即可测各发行版）
curl -s -X POST https://api.osv.dev/v1/query -H "Content-Type: application/json" \
  -d '{"package":{"name":"curl","ecosystem":"Fedora:43"},"version":"1.0"}'
# 200+CVE=可用 / 200+{}=有名无实 / 400=不存在

# 2. Arch 安全公告活跃度检测
curl -s https://security.archlinux.org/issues/all.json | python -c \
  "import sys,json;d=json.load(sys.stdin);print(len(d))"

# 3. NixOS tracker 是否可自动化（看字节数）
curl -s https://tracker.security.nixos.org/ | wc -c   # 1031 = 纯 JS 壳

# 4. AUR 包总数
curl -s -A "Mozilla/5.0" https://aur.archlinux.org/packages | grep -o '[0-9]* packages found'

# 5. Debian 安全数据体积
curl -sI https://security-tracker.debian.org/tracker/data/json | grep -i content-length

# 6. Alpine secdb
curl -s https://secdb.alpinelinux.org/v3.22/main.json | head -c 300

# 7. Repology 新鲜度（注意 API 403，需用网页）
curl -s -A "Mozilla/5.0" https://repology.org/repositories/statistics | grep -A2 "Arch Linux"

# 8. Arch 维护者规模
curl -s -A "Mozilla/5.0" https://archlinux.org/people/developers/ \
  | python -c "import sys,re;print(len(set(re.findall(r'/people/[a-z-]+/#([a-z0-9_]+)', sys.stdin.read()))))"
```

---

## 坑与反直觉

1. **OSV 有"假覆盖"** —— openSUSE/SUSE 返回 200 但内容为空 `{}`，脚本若不检查 body 会误判为"已覆盖"。
2. **Arch 安全数据"在场但已死"** —— JSON 返回 2444 条，实际公告 2025-06 停发。**用数据存在性判断活跃度会翻车**。
3. **pacman 没有原子性** —— 事务失败不回滚，可能损坏 pacman 自身（不只是应用）。
4. **`pacman -Sy pkg` 会毁系统** —— 必须 `-Syu`；这是 Arch 用户最常见的自伤方式。
5. **AUR 不是二进制仓库** —— 是 PKGBUILD 脚本库，用户自行构建，无官方审核 → 2026 供应链事件的结构性原因。
6. **zypper 慢是真实痛点** —— 不是主观感受，论坛有 8 分钟刷新的实测帖。
7. **Repology API 返回 403** —— 必须抓 `repositories/statistics` 的 HTML，且需带 UA。
8. **Debian 孤儿包滞留十年不是疏忽** —— 是"宁可留着也不删"哲学的结果，与 Fedora 的 6 周硬性退役形成极端对比。
9. **Arch 的 DDoS 公告曾被忽略** —— 2025-08 官方公告持续 DDoS，主流报道极少，但它解释了 2025-2026 Arch 服务不稳的背景。
10. **"400 vs 1500"不是矛盾是口径** —— 移除数 vs 收养数。引用二手数字前必须回原公告确认口径。

---

## 未核实 / 存疑

| 项目 | 状态 |
|---|---|
| COPR 项目总数 | 无公开 API，页面反爬 |
| Arch PM 精确数（70）/ Fedora packager（325） | 二手，未逐页核实 |
| Alpine 团队规模 / NixOS 贡献者总数 / Ubuntu MOTU 人数 | 无公开数据 |
| Repology API `/api/v1/repositories` | 实测 403 |
| Debian NEW queue 处理天数 | 页面仅图表，无数字快照 |
| Ubuntu universe 安全支持级别原文 | 二手 |
| 六家「关键包指定维护者」清单 | 均无公开清单 |

---

## 相关文档

- `reports/distro-operations-analysis-2026-10.md` —— 完整报告
- `kb/distro-community-seven-dimensions.md` —— 七维社区对比（治理/规范/维护）
- `kb/llm-sysadmin-distro-selection.md` —— LLM 运维选型（与本文 OSV 覆盖部分强相关）
- `kb/config-drift-and-residual-files.md` —— 配置漂移与残余文件
- `kb/linux-distro-deep-research-summary.md` —— 综合研究总纲
