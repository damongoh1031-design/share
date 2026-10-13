# 其他滚动发行版全景（2026-10）

> **调研时点**：2026-10-13 ｜ **方法**：3 个并行子代理 + 主调研员独立实测（DistroWatch 排名抓取 / GitHub API / 官方站点）
> **标注**：`[实测]` = 本次独立取到 ｜ `[官方]` = 读到官方原文 ｜ `[二手]` = 媒体 ｜ `[未找到]`
> **范围**：Arch / NixOS / openSUSE TW·Slowroll / Fedora / Debian / Ubuntu **之外**的滚动或半滚动发行版

---

## 0. 结论先行

**DistroWatch 过去 6 个月点击排名（`[实测]` 2026-10-13 抓取，139 条）—— 滚动发行版已经占据主导：**

| 排名 | 发行版 | 6 个月点击 | 类型 |
|---|---|---|---|
| **1** | **CachyOS** | **2,658** | Arch 系真滚动 |
| 9 | Bazzite | 817 | Fedora 不可变 |
| 10 | EndeavourOS | 772 | Arch 系真滚动 |
| 11 | Manjaro | 724 | Arch 系**延迟**滚动 |
| 12 | **PikaOS** | 714 | 新面孔 |
| 13 | **Omarchy** | 624 | **Arch 系 AI 原生** |
| 17 | **Arch 本体** | 531 | — |
| 18 | Artix | 485 | Arch 系无 systemd |
| 19 | Void | 479 | 独立 |

> ⚠️ **DistroWatch 排名的局限**：它统计的是**网站页面点击量**，不是安装量，且容易被话题性带动。**不要当市场份额读**。但作为"关注度"指标仍有参考价值。

**三个本次才发现的重要事实：**

1. **CachyOS 登顶总榜第一**（2658），**超过 Arch 本体（531）5 倍**。Arch 系衍生版的总关注度已远超 Arch 本身。
2. **Omarchy**（DHH 的 Arch 系发行版）GitHub **44,724★** `[实测]` —— 媒体报道还停在 28k（2026-08），两个月涨了 60%。它是**目前最热的"AI 原生"发行版**。
3. **两个已死**：**ArcoLinux**（2025-04 宣布，2025-07-01 关闭全部渠道）、**Funtoo**（官方首页："The existing Funtoo Linux project has ended and the community project has been officially disbanded"）。

**一个尖锐的对照**：**AerynOS 明令禁止 LLM 贡献，Omarchy 把 AI Agent 做成核心卖点。** 2026 年的滚动发行版圈在这个问题上已经分裂。

---

## 1. DistroWatch 完整排名（滚动/半滚动发行版）

`[实测]` 2026-10-13，过去 6 个月页面点击：

| 排名 | 发行版 | 点击 | 滚动模式 |
|---|---|---|---|
| 1 | **CachyOS** | 2,658 | 真滚动（Arch + 优化仓库） |
| 9 | Bazzite | 817 | 不可变镜像（Fedora Atomic） |
| 10 | EndeavourOS | 772 | 真滚动（紧贴 Arch） |
| 11 | Manjaro | 724 | **延迟滚动（约 2 周）** |
| 12 | PikaOS | 714 | 滚动（Debian 系，新） |
| 13 | Omarchy | 624 | 真滚动（Arch + Hyprland） |
| 16 | BigLinux | 533 | 滚动（Arch 系，巴西社区） |
| 17 | Arch | 531 | 真滚动 |
| 18 | Artix | 485 | 真滚动（无 systemd） |
| 19 | Void | 479 | 真滚动（runit） |
| 20 | NixOS | 465 | 声明式滚动 |
| 30 | PCLinuxOS | 324 | 真滚动（apt-rpm） |
| 32 | Alpine | 307 | edge 为滚动 |
| 35 | Garuda | 290 | 真滚动（Arch 系） |
| 41 | Solus | 266 | 真滚动（每周推送） |
| 42 | Kali | 265 | 真滚动（kali-rolling） |
| 44 | **AerynOS** | 258 | 原子更新（非不可变） |
| 46 | Devuan | 256 | ceres = 滚动 |
| 49 | Parrot | 236 | 滚动（Debian testing） |
| 50 | **KDE Linux** | 230 | 不可变镜像 |
| 52 | SteamOS | 222 | 不可变原子（A/B 分区） |
| 61 | Gentoo | 197 | 源码滚动 |
| 64 | KaOS | 190 | 快照式滚动 |
| 66 | Slackware | 183 | current 为开发树 |
| 67 | CentOS | 182 | Stream = 滚动 |
| 68 | Rocky | 182 | 点发布（无滚动分支） |
| 82 | Vanilla | 165 | 不可变（非滚动） |
| 89 | Archcraft | 161 | Arch 系（极简 WM） |
| 96 | OpenMandriva | 152 | ROME = 滚动 |
| 104 | blendOS | 140 | 声明式混合 |
| 114 | Nitrux | 118 | 半滚动 |

---

## 2. Arch 系衍生（最热闹的一支）

| 发行版 | 版本（2026-10） | 与 Arch 的差异 | 状态 |
|---|---|---|---|
| **CachyOS** | **260809**（2026-08-09，月度 ISO） | 自建优化仓库（x86-64-v3/v4、LTO、BORE 内核）；团队约 14 人 | ✅ 最热 |
| **EndeavourOS** | **Titan Nova**（2026-08-28） | **几乎就是 Arch**（直接用 Arch 仓库）+ Calamares 图形安装器 | ✅ |
| **Manjaro** | **26.0 "Anh-Linh"**（2026-01） | **延迟约 2 周**（官方原文 "roughly a couple of weeks"）；**官方不支持 AUR**（原文 "Use the AUR at your own risk! No support will be provided"）；团队约 17 人 | ⚠️ **治理危机** |
| **Omarchy** | 持续更新 | Arch + Hyprland + Quickshell；**AI 原生**；GitHub **44,724★** `[实测]` | ✅ 爆红 |
| **Garuda** | **260819 "Temeraire"** | 性能/游戏向，默认 Btrfs+Snapper 快照；**默认内核已从 linux-zen 换成 CachyOS 内核** | ✅ |
| **Artix** | **2026.08**（+ 每周构建 ISO） | **无 systemd**（OpenRC/runit/s6/dinit 四选）；2026-08 弃 XLibre 回归 Xorg | ✅ |
| **BlackArch** | 2026 | 渗透测试向，**2,863 个工具**（官方原文）；团队约 11 人 | ✅ |
| **Arch Linux ARM** | 持续 | 官方称 "We are a port of Arch Linux"；**独立打包，非实时镜像** | ✅ |
| **Archcraft** | 排名 89 | 极简 WM 预配置 | ✅ |
| **SteamOS 3** | **3.8**（2026-06-18） | **官方确认 "SteamOS is an Arch Linux-based Linux distribution"**；但**不可变 + A/B 分区原子更新**，与 Arch 滚动流脱钩 | ✅ 仅官方设备 |
| **RebornOS** | 2025.04.26 | 安装时可自选大量 DE | ✅ 但极小众 |
| ~~**ArcoLinux**~~ | — | — | ❌ **已死（2025-04）** |

### Manjaro 的治理危机（本次最重要的新事件）

`[官方]` **2026-03-09**，一份《Manjaro 2.0 Manifesto》发在 Manjaro 官方论坛，**19 名团队成员联署**：
- 指项目"十年来持续衰落、失去信任与贡献者"
- 要求**脱离母公司 Manjaro GmbH & Co KG**，改组为非营利 e.V.
- 否则**罢工 / fork**
- 导火索之一是**反复过期的 SSL/TLS 证书**

后续报道称创始人 **Philip Müller 正在拖延**。**这是 2026 年最值得关注的发行版治理事件之一**（与 NixOS 的治理危机并列）。

> **对用户的含义**：Manjaro 虽然排名第 11、对新手友好，但**当前治理不稳**。如果看重长期稳定，EndeavourOS（同源但更简单）或 CachyOS 风险更低。

---

## 3. 独立滚动（非 Arch 系）

| 发行版 | 包管理 / init | 版本 | 关键事实 |
|---|---|---|---|
| **Void Linux** | `xbps` / **runit** | ISO 20250202 | ✅ **活跃**：`void-packages` **3,455★**，最后 push **2026-10-12** `[实测]`；glibc 与 musl 双版本 |
| **Gentoo** | `portage` / OpenRC·systemd | profile **23.0** | ✅ **源码滚动**（`~amd64` = testing）；**二进制包重大进展**：2023-12 起官方 binhost，2024-02 加 x86-64-v3，2026-08 更新 Quickstart —— "编译太慢"的印象**已部分改观**；`gentoo/gentoo` 2,466★ |
| **Solus** | `eopkg` / systemd | **4.9 "Serenity"**（2026-04-18） | ✅ **已从 2023 危机恢复**：2025-10-11 启用新稳定仓库 **Polaris**；`getsolus/packages` 140★，push 2026-10-13 `[实测]` |
| **KaOS** | `pacman` + **自有仓库** | 2026.09（2026-09-13） | ⚠️ **重大转向**：2026-02 弃用默认 KDE Plasma 改 niri/Noctalia；**2026-09 成为首个默认 dinit** 的发行版 |
| **PCLinuxOS** | `apt-rpm` | 2026 | ✅ 真滚动；社区活跃（PCLinuxOS Magazine 月度出刊至 2026-10） |
| **OpenMandriva ROME** | `dnf`/rpm 6.1 | **26.09**（2026-10-01） | ⚠️ 官方承认近期遭"蓄意破坏"及缺人手 |
| **Slackware current** | `slackpkg`（无依赖解析） | 15.1 **未发布** | ⚠️ current 是 15.1 的预发布树；ChangeLog 更新至 2026-10-10；上一稳定版 15.0 是 **2022-02** |
| **Alpine edge** | `apk` / OpenRC | edge | ⚠️ 官方原文："many changes are not heavily tested (or tested at all), and packages can and do break" —— **不适合生产** |
| **Chimera Linux** | `apk` / **dinit** | 20251220（beta） | 非 GNU（用 `chimerautils`）、musl、LLVM；**~9,000 包**；`cports` 354★，push 2026-10-13；**仍 beta，不建议生产** |
| **Guix System** | Guix / **GNU Shepherd** | **1.5.0**（2026-01-23） | GNU 官方项目，**独立于 NixOS**；官方自称 "as a rolling release"；Scheme 语言 |
| ~~**Funtoo**~~ | — | — | ❌ **已死**：官方 "project has ended and the community project has been officially disbanded" |

---

## 4. Debian / Ubuntu 系滚动

| 发行版 | 上游 | 滚动模式 | 关键事实 |
|---|---|---|---|
| **Debian sid** | — | 真滚动 | `[官方]` sid 页面原文：**"This distribution will never get released"**；安全更新"**not** managed by the security team"；"Use it at your own risk!" |
| **Debian testing** | sid | 半滚动 | `[官方]` migration delay = **10 / 5 / 2 天**（按上传紧急度） |
| **Kali** | Debian testing | 真滚动（kali-rolling，默认主分支） | 版本 **2026.2**（2026-06-29）；官方定位渗透测试，**不推荐日常** |
| **Parrot OS** | Debian testing | 滚动 | 版本 **7.4**（2026-10-03）；`[官方]` 明确 **"Parrot can be used as a daily system"**（比 Kali 立场宽松） |
| **Rhino Linux** | Ubuntu **devel 分支** | 真滚动 | 版本 **2026.1**（2026-05-24），内核 7.0.9；用 **Pacstall** 补最新软件 |
| **Devuan ceres** | Debian sid | 真滚动 | `[官方]` ceres = "an alias for Debian's sid"；无 systemd |
| antiX / MX Linux | Debian **stable** | ❌ **不是滚动** | 点发布；MX 25.3（2026-09-20）、antiX 26 |

---

## 5. 企业 / 云滚动

| 发行版 | 模式 | EOL / 关键事实 |
|---|---|---|
| **CentOS Stream** | **minor release 滚动**（"updates are **not batched** into minor releases"） | Stream 9 → **2027-05-31**；Stream 10 → **2030-05-31**（`[二手]` 多源） |
| **Fedora Rawhide** | 真滚动 | `[官方]` "Is Rawhide a 'rolling release'? It depends… but **yes**"；面向"advanced users, testers, and package maintainers" |
| **AlmaLinux Kitten** | 滚动（AlmaLinux 10 上游） | ✅ **仍活跃**（子代理曾怀疑已停）；镜像每 3 个月重建；支持期对齐 CentOS Stream 10 |
| **Rocky Linux** | ❌ **无滚动分支** | 纯 RHEL 下游重建，点发布 |
| **openSUSE Aeon / Kalpa** | 不可变 + 滚动 | `[官方]` **2023-05-27** 从 MicroOS Desktop 拆分：GNOME→Aeon、KDE→Kalpa；Kalpa 目前 **Alpha** |

---

## 6. 不可变 / 声明式（新一代"滚动"）

| 发行版 | 基础 | 模式 | 关键事实 |
|---|---|---|---|
| **Bazzite** | Fedora Atomic | OCI 镜像 + bootc | `[实测]` **9,177★**，push 2026-10-13；游戏向 |
| **Bluefin / Aurora** | Fedora Atomic | OCI 镜像 + bootc | `[实测]` Bluefin **2,626★**；90 天镜像归档可回滚 |
| **Fedora Silverblue / Kinoite** | Fedora Atomic | 镜像式 | 跟 Fedora 点发布周期，**不是经典滚动** |
| **KDE Linux** | **Arch 包构建** | 不可变镜像 | `[官方]` **"不应视为基于 Arch 的发行版"** —— 仅用 Arch 构建，**安装后连 pacman 都没有**；只支持 Wayland；应用走 Flatpak |
| **Vanilla OS** | **已从 Ubuntu 转 Debian** | 不可变（ABRoot） | 版本 **3 "Reunion"**（2026-08-24）；**非滚动** |
| **blendOS** | Arch | 声明式混合 | ⚠️ `[实测]` GitHub **最后 push 2025-10-21**（近一年未动），尽管官方博客称 v5 活跃 —— **需谨慎** |
| **Endless OS** | Debian stable | 不可变 OSTree | ❌ **非滚动**，点发布 |

---

## 7. 三个值得单独说的新面孔

### 7.1 Omarchy —— AI 原生的 Arch 系

| 项 | 值 |
|---|---|
| GitHub | `omacom/omarchy` —— `[实测]` **44,724★**，push **2026-10-13** |
| 基础 | **Arch + Hyprland（Wayland 合成器）+ Quickshell** |
| 作者 | **DHH**（David Heinemeier Hansson，Ruby on Rails / Basecamp 创始人） |
| 核心卖点 | **AI 原生** —— 开箱预置多个 AI Agent 集成 |
| 生态 | 已有独立生态：`omacom/try-omarchy`（2,586★，在 macOS 上试跑）、`tobi/disktree`（2,876★）等 |
| 争议 | 有；被批评"过度个人风格"和 AI 集成的必要性 |

> **为什么值得注意**：它把「AI 协同管理」从外挂工具变成了**发行版的默认组成部分**。对比本仓另一份调研（`kb/ai-collaborative-distro-practice.md`）的结论——当时 Arch 的 AI 生态"基本为零"——Omarchy 代表了一个新方向。

### 7.2 KDE Linux —— KDE 官方下场做发行版

| 项 | 值 |
|---|---|
| 定位 | `[官方]` KDE 的"**参考实现**"——展示 KDE 技术栈的最佳形态 |
| 基础 | **用 Arch 的包构建，但官方明确"不应视为基于 Arch 的发行版"** |
| 关键差异 | **安装后不含 pacman**；不可变镜像 + 原子更新；**只支持 Wayland**；应用主要走 **Flatpak** |
| 版本 | kdelinux-20261001（2026-10-01） |
| 排名 | DistroWatch 第 50（230 点击） |

> **为什么值得注意**：KDE 是第一个由大型桌面环境项目**官方直接维护**的发行版。它的存在可能会改变"KDE 用户该用哪个发行版"这个问题的答案。

### 7.3 AerynOS —— Serpent OS 的继任者，且**禁止 LLM**

| 项 | 值 |
|---|---|
| 来历 | **Serpent OS 改名继任**，由前 Solus 开发者 **Ikey Doherty** 创建 |
| 模式 | **原子更新（但官方强调"非不可变"）**，从零构建 |
| 版本 | 2026.02（2026-03 报道） |
| **争议点** | `[官方]` **2026-01 确立禁止 LLM 贡献的政策**，理由是**训练数据的伦理问题与环境成本** |
| 排名 | DistroWatch 第 44（258 点击） |

> **为什么值得注意**：它与 Omarchy 形成**正面对照** —— 一个把 AI 做成卖点，一个明令拒绝 LLM 参与。2026 年的发行版社区在这个问题上已经分裂，**选型时值得知道你的发行版站在哪一边**。

---

## 8. 已死 / 停维名单（重要，避免踩坑）

| 发行版 | 终止时间 | 证据 |
|---|---|---|
| **ArcoLinux** | **2025-04 宣布，2025-07-01 关闭全部渠道** | 项目负责人 Erik Dubois 公告；过渡支持至 2025-07-01 `[二手，多源一致]` |
| **Funtoo** | **已解散** | `[官方]` funtoo.org 首页："The existing Funtoo Linux project has ended and the community project has been officially disbanded"（2026-06-12 更新） |
| ~~CentOS Linux~~ | 2021-12 转向 Stream | （历史事件，CentOS Linux 8 于 2021 EOL） |
| **blendOS** | ⚠️ **存疑** | `[实测]` GitHub 最后 push 2025-10-21；官方博客称 v5 活跃 —— **信号矛盾** |

---

## 9. 按需求选型

| 你的需求 | 推荐 | 理由 |
|---|---|---|
| **要 Arch 但安装省事** | **EndeavourOS** | 几乎就是 Arch + 图形安装器，无额外仓库层 |
| **要 Arch + 性能优化** | **CachyOS** | 关注度第一；但注意 Phoronix 实测 BORE 优势不显著 |
| **要 Arch + 游戏/好看 + 快照** | **Garuda** | 默认 Btrfs+Snapper，代价是内存占用高（官方承认） |
| **要 Arch + AI 原生** | **Omarchy** | 44,724★，预置 AI Agent |
| **不要 systemd** | **Void**（runit）/ **Artix**（四选 init）/ **Devuan**（ceres） | Void 最活跃（每日提交） |
| **要源码编译但不想全编译** | **Gentoo** | 官方 binhost 已覆盖 amd64+arm64 常用包 |
| **要轻量独立滚动** | **Solus** | 已从 2023 危机恢复，每周推送 |
| **要企业级滚动** | **CentOS Stream 10** | EOL 2030-05-31，RHEL 上游 |
| **要不可变 + KDE** | **KDE Linux** / **Bazzite** | 前者 KDE 官方，后者游戏向且 9,177★ |
| **要容器基础** | **Alpine stable**（不是 edge） | edge 官方明说不适合生产 |
| **避免** | ~~ArcoLinux~~ / ~~Funtoo~~ / Manjaro（治理危机中） | 前两个已死 |

---

## 10. 存疑与未核实

| 项目 | 状态 |
|---|---|
| DistroWatch 排名的方法论 | ⚠️ 统计的是**页面点击**，非安装量，受话题性影响；**不可当市场份额** |
| Manjaro 2.0 Manifesto 的最终结果 | `[二手]` 截至 2026-10 未见解决公告；Philip Müller "stalling" 说法来自媒体报道 |
| CachyOS 优化的实际收益 | `[官方]` Phoronix 实测 BORE 内核 **"there ultimately wasn't anything too special"**；其他优化（x86-64-v3/v4、LTO）无独立基准 |
| Void 的包总数与团队人数 | `[未找到]` 无官方公开数字 |
| Gentoo 开发者精确人数 | `[未找到]` 仅知"数百名" |
| blendOS 是否仍活跃 | ⚠️ **信号矛盾**：GitHub 2025-10 后无 push，但官方博客称 v5 活跃 |
| PikaOS / BigLinux / AnduinOS / RakuOS | `[未找到]` 排名靠前但本轮未深入调研，需单独核实 |
| Chimera Linux 包数（~9,000） | `[二手]` 来源为应用商店描述 |
| SteamOS 3.8 普通 PC 安装的支持范围 | `[二手]` 称支持更多 AMD PC/掌机，但官方仅认证三款设备 |

---

## 附录：本次实测命令

```bash
# DistroWatch 6 个月排名
curl -sL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "https://distrowatch.com/dwres.php?resource=popularity" | grep -A2 "Last 6 months"

# 核实各发行版活跃度（GitHub API，比抓网页可靠）
for r in omacom/omarchy ublue-os/bazzite void-linux/void-packages \
         gentoo/gentoo getsolus/packages blend-os/blendOS KDE/kde-linux; do
  echo -n "$r  "
  curl -s "https://api.github.com/repos/$r" \
    | python -c "import sys,json;d=json.load(sys.stdin);print(d.get('stargazers_count'),str(d.get('pushed_at'))[:10])"
done
```

---

*报告生成：2026-10-13 ｜ 3 个并行子代理 + 主调研员独立实测（DistroWatch 排名抓取 / GitHub API / 官方站点）*
