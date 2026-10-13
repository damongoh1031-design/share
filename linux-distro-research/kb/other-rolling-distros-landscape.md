---
id: other-rolling-distros-landscape
title: 其他滚动发行版全景：Arch 系 / 独立 / 企业 / 不可变（含 DistroWatch 实测排名）
tags: [linux-distro, rolling-release, cachyos, omarchy, kde-linux, aerynos, void-linux, gentoo, manjaro, distrowatch, immutable]
created: 2026-10-13
updated: 2026-10-13
version: 1.0.0
status: stable
source: 3 个并行子代理 + 主调研员独立实测（DistroWatch 排名抓取 / GitHub API / 官方站点，2026-10-13）
confidence: 已核实
---

# 其他滚动发行版全景（2026-10）

## 一句话结论

**滚动发行版已占据 DistroWatch 关注度主导**：CachyOS 登顶总榜第一（2658 点击，是 Arch 本体的 5 倍）。三个新趋势：**Omarchy**（44,724★，AI 原生 Arch 系）、**KDE Linux**（KDE 官方发行版，不含 pacman）、**AerynOS**（明令禁止 LLM 贡献）。**两个已死**：ArcoLinux、Funtoo。

---

## 1. DistroWatch 排名实测（2026-10-13，过去 6 个月点击）

| 排名 | 发行版 | 点击 | 滚动模式 |
|---|---|---|---|
| **1** | **CachyOS** | **2,658** | Arch 系真滚动 |
| 9 | Bazzite | 817 | Fedora 不可变 |
| 10 | EndeavourOS | 772 | Arch 系真滚动 |
| 11 | Manjaro | 724 | 延迟滚动（约 2 周） |
| 12 | PikaOS | 714 | Debian 系滚动（新） |
| 13 | Omarchy | 624 | Arch 系 **AI 原生** |
| 16 | BigLinux | 533 | Arch 系 |
| **17** | **Arch** | **531** | 真滚动 |
| 18 | Artix | 485 | 无 systemd |
| 19 | Void | 479 | runit |
| 20 | NixOS | 465 | 声明式滚动 |
| 30 | PCLinuxOS | 324 | apt-rpm |
| 32 | Alpine | 307 | edge 为滚动 |
| 35 | Garuda | 290 | Arch 系 |
| 41 | Solus | 266 | 每周推送 |
| 42 | Kali | 265 | kali-rolling |
| 44 | AerynOS | 258 | 原子更新 |
| 46 | Devuan | 256 | ceres |
| 49 | Parrot | 236 | Debian testing |
| 50 | KDE Linux | 230 | 不可变镜像 |
| 52 | SteamOS | 222 | 不可变原子 |
| 61 | Gentoo | 197 | 源码滚动 |
| 64 | KaOS | 190 | 快照式 |
| 66 | Slackware | 183 | current |
| 67 | CentOS | 182 | Stream |
| 82 | Vanilla | 165 | 不可变（非滚动） |
| 96 | OpenMandriva | 152 | ROME |
| 104 | blendOS | 140 | 声明式混合 |

> ⚠️ **方法论局限**：DistroWatch 统计的是**网站页面点击量**，不是安装量，且受话题性带动。**不可当市场份额读**，仅作关注度参考。

---

## 2. Arch 系衍生

| 发行版 | 版本 | 差异 | 状态 |
|---|---|---|---|
| **CachyOS** | 260809（月度 ISO） | 自建优化仓库（x86-64-v3/v4、LTO、BORE）；团队 ~14 人 | ✅ 最热 |
| **EndeavourOS** | Titan Nova（2026-08-28） | **几乎就是 Arch** + Calamares 安装器 | ✅ |
| **Manjaro** | 26.0 "Anh-Linh" | **延迟约 2 周**；**官方不支持 AUR**；团队 ~17 人 | ⚠️ 治理危机 |
| **Omarchy** | 持续 | Arch + Hyprland + Quickshell；**AI 原生**；**44,724★** | ✅ 爆红 |
| **Garuda** | 260819 "Temeraire" | 游戏向，默认 Btrfs+Snapper；**内核已换成 CachyOS 内核** | ✅ |
| **Artix** | 2026.08 | **无 systemd**（OpenRC/runit/s6/dinit）；2026-08 弃 XLibre | ✅ |
| **BlackArch** | 2026 | 渗透测试，**2,863 工具**；团队 ~11 人 | ✅ |
| **Arch Linux ARM** | 持续 | 官方称 "a port of Arch Linux"；**独立打包** | ✅ |
| **SteamOS 3** | 3.8（2026-06-18） | **官方确认基于 Arch**，但**不可变 + A/B 分区** | ✅ 仅官方设备 |
| ~~ArcoLinux~~ | — | — | ❌ **已死 2025-04** |

### Manjaro 治理危机（2026 最重要事件之一）

`[官方]` **2026-03-09** 官方论坛发《Manjaro 2.0 Manifesto》，**19 名团队成员联署**：
- 指项目"十年来持续衰落、失去信任与贡献者"
- 要求脱离母公司 Manjaro GmbH & Co KG，改组非营利 e.V.
- 否则**罢工 / fork**
- 导火索含**反复过期的 SSL/TLS 证书**
- 后续报道称创始人 Philip Müller "stalling"

**含义**：Manjaro 对新手友好，但当前治理不稳。看重长期稳定 → EndeavourOS 或 CachyOS。

### CachyOS 优化的真相

`[官方]` Phoronix 实测 BORE 内核：**"there ultimately wasn't anything too special"** —— BORE 在几何均值上仅排在默认 CachyOS 内核之后。其他优化（x86-64-v3/v4、LTO）**无独立基准**。

---

## 3. 独立滚动

| 发行版 | 包管理 / init | 关键事实 |
|---|---|---|
| **Void Linux** | xbps / **runit** | ✅ 活跃：`void-packages` **3,455★**，push 2026-10-12；glibc + musl 双版本 |
| **Gentoo** | portage / OpenRC·systemd | 源码滚动；**binhost 重大进展**（2023-12 起，2024-02 加 x86-64-v3，2026-08 更新 Quickstart）→ "编译太慢"印象**已部分改观** |
| **Solus** | eopkg / systemd | **4.9 "Serenity"**（2026-04-18）；✅ **已从 2023 危机恢复**（2025-10 启用新仓库 Polaris） |
| **KaOS** | pacman + 自有仓库 | ⚠️ **2026-09 成为首个默认 dinit 的发行版**；2026-02 弃用默认 KDE |
| **PCLinuxOS** | apt-rpm | 真滚动；Magazine 月度出刊至 2026-10 |
| **OpenMandriva ROME** | dnf/rpm 6.1 | **26.09**（2026-10-01）；官方承认遭"蓄意破坏"及缺人手 |
| **Slackware current** | slackpkg | ⚠️ current 是 15.1 预发布树；**15.1 仍未发布**（上稳定版 15.0 = 2022-02） |
| **Alpine edge** | apk / OpenRC | ⚠️ 官方原文："packages can and do break" —— **不适合生产** |
| **Chimera Linux** | apk / **dinit** | 非 GNU（`chimerautils`）、musl、LLVM；~9,000 包；**beta，不建议生产** |
| **Guix System** | Guix / **GNU Shepherd** | **1.5.0**（2026-01-23）；GNU 官方，**独立于 NixOS**；自称 rolling release |
| ~~Funtoo~~ | — | ❌ **已解散**（官方原文确认） |

---

## 4. Debian / Ubuntu 系

| 发行版 | 上游 | 关键事实 |
|---|---|---|
| **Debian sid** | — | `[官方]` **"This distribution will never get released"**；安全更新"**not** managed by the security team" |
| **Debian testing** | sid | `[官方]` migration delay = **10 / 5 / 2 天** |
| **Kali** | Debian testing | **2026.2**；官方定位渗透测试，**不推荐日常** |
| **Parrot OS** | Debian testing | **7.4**（2026-10-03）；`[官方]` **"can be used as a daily system"** |
| **Rhino Linux** | Ubuntu **devel** | **2026.1**（2026-05-24）；用 **Pacstall** 补最新软件 |
| **Devuan ceres** | Debian sid | `[官方]` ceres = "an alias for Debian's sid" |
| antiX / MX | Debian **stable** | ❌ **不是滚动** |

---

## 5. 企业 / 云

| 发行版 | 模式 | 关键事实 |
|---|---|---|
| **CentOS Stream** | minor release 滚动（"updates are **not batched**"） | Stream 9 → **2027-05-31**；Stream 10 → **2030-05-31** |
| **Fedora Rawhide** | 真滚动 | `[官方]` "…but **yes**"；面向 advanced users / testers |
| **AlmaLinux Kitten** | 滚动（AlmaLinux 10 上游） | ✅ **仍活跃**；镜像每 3 月重建 |
| **Rocky Linux** | ❌ **无滚动分支** | 纯 RHEL 下游 |
| **Aeon / Kalpa** | 不可变 + 滚动 | `[官方]` **2023-05-27** 从 MicroOS Desktop 拆分；Kalpa 为 **Alpha** |

---

## 6. 不可变 / 声明式

| 发行版 | 基础 | 关键事实 |
|---|---|---|
| **Bazzite** | Fedora Atomic | **9,177★**（push 2026-10-13） |
| **Bluefin / Aurora** | Fedora Atomic | Bluefin **2,626★**；90 天镜像归档可回滚 |
| **KDE Linux** | **Arch 包构建** | `[官方]` **"不应视为基于 Arch 的发行版"** —— **安装后不含 pacman**；只支持 Wayland；应用走 Flatpak |
| **Vanilla OS** | **已从 Ubuntu 转 Debian** | **3 "Reunion"**（2026-08-24）；**非滚动** |
| **blendOS** | Arch | ⚠️ GitHub **最后 push 2025-10-21**，尽管官方称 v5 活跃 —— **信号矛盾** |
| **Endless OS** | Debian stable | ❌ 非滚动 |

---

## 7. 三个新面孔

### Omarchy（AI 原生）
- `omacom/omarchy` —— **44,724★**，push 2026-10-13（媒体报道还停在 28k）
- **Arch + Hyprland + Quickshell**，作者 **DHH**（Rails / Basecamp 创始人）
- **核心卖点：AI 原生**，预置多个 AI Agent
- 已有生态：`try-omarchy`（2,586★）、`disktree`（2,876★）
- **意义**：把「AI 协同管理」从外挂工具变成发行版默认组件

### KDE Linux（KDE 官方下场）
- KDE 的"**参考实现**"；**用 Arch 的包构建，但不含 pacman**
- 不可变镜像 + 原子更新；**只支持 Wayland**；应用走 Flatpak
- kdelinux-20261001（2026-10-01）；DistroWatch 第 50
- **意义**：第一个由大型桌面环境项目官方直接维护的发行版

### AerynOS（禁止 LLM）
- **Serpent OS 改名继任**，前 Solus 开发者 **Ikey Doherty** 创建
- 原子更新（官方强调"非不可变"）；2026.02
- `[官方]` **2026-01 确立禁止 LLM 贡献的政策**，理由是**训练数据伦理 + 环境成本**
- **意义**：与 Omarchy 正面对照 —— **2026 年发行版社区在 AI 问题上已分裂**

---

## 8. 已死 / 停维

| 发行版 | 终止 | 证据 |
|---|---|---|
| **ArcoLinux** | 2025-04 宣布，2025-07-01 关渠道 | 负责人 Erik Dubois 公告 |
| **Funtoo** | 已解散 | 官方首页："project has ended and the community project has been officially disbanded" |
| **blendOS** | ⚠️ 存疑 | GitHub 2025-10-21 后无 push，但官方称 v5 活跃 |

---

## 可复用操作

```bash
# DistroWatch 6 个月关注度排名
curl -sL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "https://distrowatch.com/dwres.php?resource=popularity" | grep -A2 "Last 6 months"

# 核实发行版活跃度（GitHub API 比抓网页可靠得多）
for r in omacom/omarchy ublue-os/bazzite void-linux/void-packages \
         gentoo/gentoo getsolus/packages blend-os/blendOS KDE/kde-linux; do
  echo -n "$r  "
  curl -s "https://api.github.com/repos/$r" \
    | python -c "import sys,json;d=json.load(sys.stdin);print(d.get('stargazers_count'),str(d.get('pushed_at'))[:10])"
done

# 单个发行版详情（DistroWatch mobile 版，比首页好抓）
curl -sL -A "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)" \
  "https://distrowatch.com/table-mobile.php?distribution=kdelinux"
```

---

## 坑与反直觉

1. **CachyOS 关注度是 Arch 的 5 倍** —— Arch 系衍生版的总热度已远超 Arch 本体。
2. **DistroWatch 排名不是市场份额** —— 是页面点击量，受话题性影响。别拿它当"哪个发行版用户多"。
3. **Manjaro 官方不支持 AUR** —— 原文 "Use the AUR at your own risk! No support will be provided"。很多人以为 Manjaro 能用 AUR 就等于 Arch 体验。
4. **Manjaro 的"延迟滚动"约两周** —— 官方措辞是 "roughly a couple of weeks"，含糊但确实是缓冲。
5. **CachyOS 的 BORE 内核优势不显著** —— Phoronix 实测结论是 "nothing too special"。
6. **KDE Linux 不含 pacman** —— 它用 Arch 的包构建，但官方明确说"不应视为基于 Arch 的发行版"。
7. **SteamOS 官方确认基于 Arch**，但走不可变 A/B 分区，与 Arch 滚动流**脱钩**。
8. **Gentoo 的"编译太慢"已部分改观** —— 官方 binhost 覆盖 amd64+arm64 常用包。
9. **Alpine edge 不是给生产用的** —— 官方原文说 "packages can and do break"。生产用 stable。
10. **AerynOS 禁止 LLM 贡献，Omarchy 主打 AI 原生** —— 同一年的两个极端，选型前值得知道你的发行版站哪边。
11. **blendOS 的信号矛盾** —— GitHub 一年没 push，官方博客却说活跃。以 GitHub 为准。

---

## 未核实 / 存疑

| 项目 | 状态 |
|---|---|
| Manjaro 2.0 Manifesto 的最终结果 | 截至 2026-10 未见解决公告 |
| CachyOS 其他优化（x86-64-v3/v4、LTO）的实际收益 | 无独立基准 |
| Void 包总数与团队人数 | 无官方公开数字 |
| Gentoo 开发者精确人数 | 仅知"数百名" |
| blendOS 是否仍活跃 | **信号矛盾** |
| PikaOS / BigLinux / AnduinOS / RakuOS | 排名靠前但未深入调研 |
| Chimera Linux 包数（~9,000） | 二手来源 |
| SteamOS 3.8 普通 PC 安装支持范围 | 官方仅认证三款设备 |

---

## 相关文档

- `reports/other-rolling-distros-2026-10.md` —— 完整报告
- `kb/rolling-distro-selection-nixos-arch-opensuse.md` —— 三大滚动发行版五维对比
- `kb/arch-anti-breakage-guide.md` —— Arch 防滚挂指南
- `kb/ai-collaborative-distro-practice.md` —— AI 协同实践（Omarchy/AerynOS 是重要更新）
- `kb/distro-operations-analysis.md` —— 运营维度对比
