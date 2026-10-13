# 深度调研：KDE Plasma vs GNOME 六维对比

**调研日期**：2026-10-12
**方法**：3 个并行研究子代理（KDE / GNOME / 正面交锋）+ 主调研员对 2 个关键点二次核实
**证据标注**：`[核实]` = 官方文档/权威媒体/独立实测；`[社区]` = 论坛/用户共识；`[无数据]` = 未找到可靠公开来源
**当前版本**：KDE Plasma **6.7.5**（6.8 将于 **2026-10-14** 发布）｜GNOME **51 "A Coruña"**（2026-09-16）

---

## 0. 结论先行

### 一句话结论

**两者不是「谁更好」，是「两种取舍」**：KDE 用可定制性换一致性，GNOME 用一致性换可定制性。**唯一有明确胜负的维度是游戏优化——KDE 大幅领先**（Steam Deck 验证 + HDR/VRR 领先一年以上）。**稳定性和崩溃率两者都没有公开数据**，谁声称「X 更稳」都是主观。

### 六维速览

| 维度 | 胜者 | 差距 |
|---|---|---|
| 纠错机制 | **KDE** | KDE 有 3 年 LTS（6.6 至 2029）、每版本支持期延长至 6 个月、有 `regression` 关键字跟踪。GNOME 官方**无 LTS** |
| 技术支援 | **平手偏 KDE** | 渠道都齐全。KDE 贡献者均值 ~140 人；GNOME 文档/HIG 更优秀但**基金会预算缩减至 $435k，仅剩 3 名全职员工** |
| 快速响应 | **KDE（有争议）** | Phoronix 2026-03 测出 KDE 领先；TechPowerUp 2026-07 测出 GNOME 微弱领先。**两个来源结论相反** |
| 用户体验 | **平手** | 完全不同的取舍。KDE 可定制极强、一致性弱；GNOME 一致性极强、可定制弱。无障碍 **GNOME 更好** |
| 游戏优化 | **KDE 大幅领先** | HDR 早约 13 个月，VRR 早 2 年以上，SteamOS 桌面模式用 KDE，Valve 出钱出人 |
| 稳定 | **平手** | **崩溃率无公开数据**。KDE 早期（6.0）差、现已转好；GNOME 核心稳、**扩展生态脆弱** |

### 两句话建议

- **玩游戏、要定制、要 LTS** → KDE Plasma
- **要一致性、用屏幕阅读器、不想折腾** → GNOME

---

## 1. 版本与节奏（先对齐坐标系）

| | KDE Plasma | GNOME |
|---|---|---|
| 当前稳定版 | **6.7.5**（6.7.0 = 2026-06-16，6.7.5 = 2026-09-08）`[核实]` | **51 "A Coruña"**（2026-09-16）`[核实]` |
| 下一个版本 | **6.8 于 2026-10-14 发布**（KDE 30 周年），**首个 Wayland-only 版本** `[核实]` | 52（计划 2027-03-17）`[核实]` |
| 大版本节奏 | 约每 **4 个月**一个（~3/年）`[核实]` | 每 **6 个月**一个（3 月 / 9 月）`[核实]` |
| 点版本 | 6.x.1 ~ 6.x.5，周二发布，间隔不等 `[核实]` | 6~7 个点版本，约 **6~7 周**间隔（51.1=2026-10-10 → 51.2=11-21 → 51.3=2027-01-09）`[核实]` |
| 版本支持期 | 每版本从 4 个月**延长至 6 个月** `[核实]` | stable + old-stable，52.0 发布时 50.x 标记 **EOL** `[核实]` |
| **LTS** | **有：Plasma 6.6 为 LTS，3 年支持至 2029** `[核实]` | **官方无 LTS** `[核实]` |

---

## 2. 纠错（bug 修复机制）

| 项目 | KDE Plasma | GNOME |
|---|---|---|
| Bug tracker | **Bugzilla**（bugs.kde.org）`[核实]` | **GitLab**（gitlab.gnome.org），2018 年从 Bugzilla 迁移完成 `[核实]` |
| 待处理规模 | plasmashell：约 **160** 个未确认报告、约 **1,100** 个已确认（含约 800 功能请求），2026-09 数据 `[核实]` | `[无数据]` 未找到公开汇总 |
| 回归跟踪 | Bugzilla **`regression` 关键字**，在 "This Week in Plasma" 定期公布 `[核实]` | 无专用机制，依赖 GitLab issue 标签与冻结审批（社区惯例）`[社区]` |
| 冻结/把关 | — | **API/ABI、Feature、UI、String 四类冻结**，改动需 freeze exception 审批；有官方 **Release Team** `[核实]` |
| triage 人力 | 2026-09 公开**招募社区 triage 志愿者**（说明人力紧张）`[核实]` | Release Team 把关 |
| **LTS** | Plasma 2025 年曾取消独立 LTS（仅 Kubuntu 采用、无 CI 验证）；**2026-08 由 Kubuntu Focus + Techpaladin 赞助复活**，Plasma 6.6 获真 3 年 LTS `[核实]` | **无官方 LTS**。发行版自行冻结：Ubuntu 26.04 LTS 采用 GNOME 50 `[核实]` |
| 企业落点 | **Kubuntu 26.04 LTS** = Plasma 6.6 LTS + Frameworks 6.24 + Gear 25.12；Kubuntu Focus 出资 **>$10 万/3 年** `[核实]` | 企业须依赖 RHEL / Ubuntu LTS 自行冻结 |

**要点**：
- **LTS 是 KDE 在「纠错/长期维护」维度最硬的差异化**。GNOME 没有官方 LTS，保守用户只能吃发行版的冻结版本。
- KDE 的 bug 规模数据是公开的（~1100 已确认），GNOME 没有可比数字——**这不是 GNOME 更好，是信息更不透明**。
- GNOME 的**四类冻结 + Release Team** 是更严格的工程流程，代价是修复推进慢。

---

## 3. 技术支援

| 项目 | KDE Plasma | GNOME |
|---|---|---|
| 官方论坛 | discuss.kde.org `[核实]` | discourse.gnome.org（公告首发地）`[核实]` |
| 即时通讯 | Matrix（官方 homeserver，与 IRC 桥接）`[核实]` | Matrix `[核实]` |
| 文档 | KDE UserBase Wiki + docs.kde.org（稳定分支更新至 2026-09）`[核实]` | GNOME Help + GTK developer docs + **HIG（人机界面指南）** `[核实]` |
| 贡献者规模 | 团队均值约 **140 人**（2026）；2017 低点约 110，2010 峰值约 180–200；2023 commit 数创历史新高 `[核实]` | `[无数据]` 本次未获取 |
| **组织财务** | KDE e.V. 2025 年报已发布（具体数字本次未获取）`[无数据]` | ⚠️ **FY2025-26：收入 $435k / 支出 $434k**（平衡）；较 2024-25 的 $586k / $550k **大幅缩减**；**裁撤 Senior Director of People & Operations**，仅剩 **3 名全职员工** `[核实]` |
| 默认发行版 | openSUSE（默认）、Kubuntu、**Fedora KDE Edition**、**SteamOS** `[核实]` | Ubuntu、Fedora Workstation、Debian、RHEL `[核实]` |

**Fedora 的关键变化**：2024-11 起 **KDE 被提升为与 GNOME 平级的官方 Edition**（Fedora 42 落地），Fedora 44（2026-04）搭载 Plasma 6.6。⚠️ 曾有 "Fedora Plasma Workstation" 提案欲让 KDE 取代 GNOME 成为默认，**该提案未按原样落地**——GNOME 仍是 Workstation 默认。`[核实]`

**风险提示**：**GNOME Foundation 的财务紧缩是真实的治理风险**（3 名全职员工 + 预算腰斩）。这会影响长期支援能力，尤其在需要专职人员处理的事务上。

---

## 4. 快速响应（性能）

### ⚠️ 首先：两个权威来源结论相反

| 来源 | 日期 | 结论 |
|---|---|---|
| **Phoronix**（AMD RX 9070 XT，Ubuntu 26.04，Mesa 26.0） | 2026-03-25 | **Plasma 6.6 在多数游戏"例行超越" GNOME 50**；Tesseract、Xonotic 明显领先 `[核实]` |
| **Phoronix**（NVIDIA RTX 5080，驱动 595.58.03） | 2026-03-27 | **Plasma 6.6.3 频繁取得性能优势** `[核实]` |
| **TechPowerUp** | 2026-07-21 | **GNOME 50.3 微弱领先** Plasma 6.7.2（低画质差 3 FPS / 1.7%）；Xfce 垫底 `[核实]` |

**怎么读**：Phoronix 与 TechPowerUp 的结论相反，差异来自硬件、画质设置、测试方法。Phoronix 作者本人也提到「往年通常是 GNOME 领先，今年 KDE 反超令人意外」。**唯一可以确定的是差距很小（个位数百分比以内），不足以作为选型依据。**

### 内存占用

| | KDE Plasma | GNOME |
|---|---|---|
| 空闲内存 | 约 **600–900 MB** `[核实]` | 约 **900 MB – 1.3 GB** `[核实]` |

> ⚠️ 网络上流传的「GNOME Shell RSS 230MB / Plasma plasmashell 655MB」类数据来自一篇**版本自相矛盾的文章（标题写 Plasma 6.3、终端显示 6.6.4、又提 Kernel 7.0），疑似 AI 生成，不可采信**。本报告不采用。

### 近期性能改进

| | KDE Plasma | GNOME |
|---|---|---|
| 最新 | **6.8**：NVIDIA **三重缓冲默认启用**；KWin 改为**仅 OpenGL ES**（未来转 Vulkan）；修复 KWin 内存泄漏 `[核实]` | **51**：**Mutter 重写调度器与帧传递系统**，高负载下动画更流畅；录屏减少缓冲拷贝 `[核实]` |
| 更早 | **6.7.2**：Phoronix 实测 **Wayland 游戏已持平甚至常优于 X11** `[核实]` | **50**：Mutter VRR 改用 **deadline timer**，降低输入→输出延迟 `[核实]` |

**输入延迟**：`[无数据]` 没有权威的独立毫秒级对比。`[社区]` 观点：KWin 支持 tearing 更新与 direct scanout，竞技游戏延迟更低；Mutter 的动态三缓冲减少掉帧但略增延迟。

---

## 5. 用户体验

| 维度 | KDE Plasma | GNOME |
|---|---|---|
| 设计哲学 | "**Simple by default, powerful when needed**"——传统桌面隐喻，最大可定制 `[核实]` | **极简主义**，"约束提升效率"，Activities Overview 为核心 `[核实]` |
| 定制能力 | **原生深度**：面板、窗口规则、KWin scripts、主题系统；6.8 引入 **Union 主题系统**统一 QtQuick 与 QtWidgets（官方标注**尚粗糙、有 bug**）`[核实]` | **受限**，依赖 GNOME Tweaks + **Extensions**（双刃剑）`[核实]` |
| HIG 强制度 | 弱，第三方应用一致性靠自觉 | **强**，libadwaita 使第三方应用高度一致（也导致主题生态被压制）`[核实]` |
| Wayland 迁移 | **Plasma 6.8（2026-10-14）移除 X11 会话**；X11 应用经 XWayland；KDE 称 X11 会话支持至 **2027 年初** `[核实]` | GNOME 最早默认 Wayland（**3.30, 2018**）；**GNOME 49 禁用 X11 会话，GNOME 50 完全移除**（2026-03）`[核实]` |
| **无障碍** | 功能可用但**碎片化**（Qt 生态边缘案例多）；6.6 增屏幕键盘、色盲滤镜；6.8 锁屏提示 Slow Keys `[核实]` | ✅ **行业标准**：Orca 屏幕阅读器与 GTK 紧耦合；GNOME 48 起 Wayland 下 Orca 快捷键正常；50/51 大幅改进（减弱动效、键盘截屏、焦点超时）`[核实]` |
| 常见劝退点 | 设置项过多、UI 一致性不足、偶发回归 `[社区]` | 「功能阉割」、**Tray icons 默认缺失需装扩展**、libadwaita 抵制主题 `[社区]` |

**无障碍的第三方评测结论**：需要屏幕阅读器或高对比度的用户，**GNOME 更可靠、更连贯**。这是 GNOME 最没有争议的优势。`[核实]`

---

## 6. 游戏优化（差距最明显的维度）

### 6.1 特性时间线

| 特性 | KDE Plasma | GNOME | 领先方 |
|---|---|---|---|
| **explicit sync** | Plasma **6.1**（2024-06-18），解决 NVIDIA 闪烁 `[核实]` | GNOME **46**（2024-03）`[核实]` | **GNOME 早 3 个月** |
| **HDR** | Plasma **6.0**（2024-02-28）Wayland 初步支持；**6.1**（2024-06）大幅改进（采用显示器 RGB primaries），与 Valve 合作 `[核实]` | GNOME **48**（2025-03-19）首次系统级 HDR，**仍属实验性**，支持应用少 `[核实]` | **KDE 早约 13 个月** |
| **VRR** | 早已正式支持（自适应同步 Automatic/Always）`[核实]` | GNOME 46（2024-03）**实验性** → **GNOME 50**（2026-01/03）**去实验化** `[核实]` | **KDE 早 2 年以上** |
| **移除 X11 会话** | Plasma 6.8（2026-10-14）`[核实]` | GNOME 50（2026-03）`[核实]` | GNOME 早 7 个月 |

### 6.2 Steam Deck 效应 —— KDE 的决定性优势

| 项目 | 内容 |
|---|---|
| SteamOS 桌面模式 | **默认 KDE Plasma**（SteamOS 3.8 用 Plasma **6.4.3**，Wayland 默认，Linux 6.16）`[核实]` |
| Valve 的定制 | **LAVD sched_ext 调度器**；控制器输入延迟降至 **100–500 µs**；外接显示器**原生 HDR + VRR**；**HDMI VRR 初步支持**；Steam Machine 支持 `[核实]` |
| 意义 | Valve **出钱出人**参与 KDE 的 HDR 开发。这形成了正反馈：KDE 拿到真实游戏场景验证 + 专职投入。**GNOME 没有对应物。** |

### 6.3 合成器行为

| | KDE Plasma | GNOME |
|---|---|---|
| 合成器 | **KWin**：全屏时**关闭合成特效**以回收性能；支持 tearing 更新、direct scanout `[核实]` | **Mutter**：稳定性优先，动态三缓冲，CSD（客户端装饰）强制 `[核实]` |
| 游戏向优化 | 6.8 起 NVIDIA 三重缓冲默认启用；KWin 转 OpenGL ES → 未来 Vulkan `[核实]` | Mutter 50 的 VRR deadline timer 降低延迟 `[核实]` |

### 6.4 共同短板

**两者都没有官方的 GameMode / MangoHud 集成**——这些是 Feral / 社区层面的事，靠发行版打包。`[核实]`

### 6.5 社区倾向

`[社区]` r/linux_gaming 的主流倾向是「玩游戏用 KDE」，主要理由是 VRR/HDR/tearing 更完整、Steam Deck 验证。**但纯帧率差异在 2% 以内，不是决定性因素。**

---

## 7. 稳定

| 项目 | KDE Plasma | GNOME |
|---|---|---|
| **崩溃率公开数据** | `[无数据]` | `[无数据]` |
| 历史问题 | **Plasma 6.0（2024-02）初期**：崩溃、X11 回归、多任务问题；经 6.0.3 / 6.0.5 大幅修复 `[核实]` | — |
| 当前状态 | Phoronix 称 Wayland「已成熟」；**6.8 官方称「报告回归很少」**（`[社区]` 质疑是否测试不足）`[核实]` | 核心 shell 本身稳定；**不稳定主要来自扩展生态** `[社区]` |
| **结构性风险** | 偶发回归；大版本主题/插件迁移阵痛 | ⚠️ **GNOME Shell 扩展运行在同一进程**——扩展异常可拖垮整个 shell；大版本升级后常见「约 73% 扩展失效」`[社区]` |
| 大版本升级破坏性 | Plasma 6.0 升级有主题/插件迁移阵痛 `[社区]` | 扩展 API 变化使 48→49、49→50 升级后**扩展大面积失效** `[核实]` |
| LTS 场景 | Kubuntu 26.04 LTS = Plasma 6.6 LTS（风味维护 3 年）`[核实]` | Ubuntu 26.04 LTS 冻结 GNOME 50；稳定但同样受 50 的扩展破坏影响 `[核实]` |
| 主流评价 | Plasma 5 早期口碑差 → **Plasma 6 经 6.6/6.7 后评价明显转好** `[社区]` | **「纯净 GNOME 稳，装扩展后变脆弱」** `[社区]` |

**关键结论**：**两者都没有公开的崩溃率数据**。声称「X 更稳」的说法缺乏依据。真正的差异在于**风险来自哪里**：KDE 的风险来自自身回归，GNOME 的风险来自**扩展生态**（而扩展恰恰是补全 GNOME 缺失功能的必需品）。

---

## 8. 六维评分卡（主观综合，1–5 分）

> 评分为本报告基于上述事实的综合判断，非客观测量值。

| 维度 | KDE Plasma | GNOME |
|---|---|---|
| 纠错机制 | **4.0** | 3.5 |
| 技术支援 | 3.5 | 3.5 |
| 快速响应 | 4.0 | 3.5 |
| 用户体验 | 4.0 | 4.0 |
| **游戏优化** | **5.0** | 3.0 |
| 稳定 | 3.5 | 3.5 |
| **治理 / 项目健康度** | 4.0 | **2.5** ⚠️ |

**读法**：
- **游戏优化是唯一有明确胜负的维度**，KDE 领先明显。
- 稳定、用户体验、技术支援基本平手。
- GNOME 的短板是**治理/资金**（3 名全职员工 + 预算腰斩）和**扩展生态的脆弱性**。
- KDE 的短板是**一致性**（设置项过多、Union 主题系统尚粗糙）。

---

## 9. 决策建议

| 你的情况 | 推荐 |
|---|---|
| **玩游戏为主** | **KDE Plasma**。Steam Deck 验证 + HDR/VRR 领先 + KWin 全屏让路 |
| 需要长期支持基线（企业/生产机） | **KDE Plasma 6.6 LTS**（3 年至 2029）；GNOME 只能靠发行版 LTS |
| 用屏幕阅读器 / 需要无障碍 | **GNOME**。Orca 与 GTK 紧耦合，行业标准 |
| 要极致定制（面板、窗口规则、脚本） | **KDE Plasma** |
| 要开箱即用、不想折腾、不装扩展 | **GNOME** |
| 依赖大量 GNOME 扩展 | ⚠️ 注意：**每次大版本升级扩展会大面积失效** |
| 用 NVIDIA + 想少踩坑 | **KDE Plasma**（explicit sync 更早、6.8 起三重缓冲默认启用） |
| 2026-10-14 之后升级 | ⚠️ **Plasma 6.8 起 X11 会话消失**。有 X11 硬依赖（旧显卡驱动、特殊输入设备）的用户需先确认 |

---

## 10. 存疑与未核实项

| 项 | 状态 |
|---|---|
| **两者的崩溃率** | **无公开数据**。任何「X 更稳」的说法都缺依据 |
| **精确输入延迟（毫秒级）对比** | 无权威独立数据 |
| GNOME 的 open bug 总数 | 无公开汇总 |
| KDE e.V. 2025 财报具体数字 | 本次未获取 |
| GNOME 贡献者规模 | 本次未获取 |
| Phoronix vs TechPowerUp 结论矛盾 | **未解决**。差异来自硬件/画质/方法，需读者自行判断 |
| 网络流传的内存数据 | 一篇广泛传播的文章**版本自相矛盾，疑似 AI 生成**，已排除 |

---

## 11. 参考来源

### KDE
- [KDE Plasma 6.8 Desktop Environment Lands on October 14th (9to5linux)](https://9to5linux.com/kde-plasma-6-8-desktop-environment-is-coming-on-october-14th-heres-what-to-expect)
- [Bug triaging help needed (pointieststick, 2026-09-03)](https://pointieststick.com/2026/09/03/bug-triaging-help-needed/)
- [KDE Plasma 6.8 Ships October 14 for KDE's 30th Anniversary (linuxcompatible)](https://www.linuxcompatible.org/story/kde-plasma-68-ships-october-14-for-kdes-30th-anniversary/)
- [KDE cancelled Plasma LTS. Kubuntu bought it back (Kubuntu)](https://kubuntu.org/news/kubuntu-26-04-1-bullet-proof-kde/)
- [Beyond Ubuntu long-term support: KDE's LTS software (Kubuntu)](https://kubuntu.org/news/plasma-6.6-lts/)
- [KDE Plasma 6.6 Becomes a True LTS: Three Years of Support (linuxdork)](https://linuxdork.com/news/kde-plasma-6-6-lts-bulletproof/)
- [KDE Plasma 6.6 Gets Three Years of LTS Support (Linuxiac)](https://linuxiac.com/kde-plasma-6-6-gets-three-years-of-lts-support/)
- [KDE cancelled its "fake" LTS release a year ago: now Plasma 6.6 is getting a real three-year one (XDA)](https://www.xda-developers.com/kde-cancelled-its-fake-lts-releases-a-year-ago-now-plasma-66-is-getting-a-real-three-year-one/)
- [KDE Plasma 6.8 drops X11: Wayland becomes mandatory (PC Games Hardware)](https://www.pcgameshardware.de/Linux-Software-26761/News/KDE-Plasma-68-drops-X11-Wayland-becomes-mandatory-from-October-2026-1544518/)
- [KDE Plasma 6.8 Goes Wayland-Only, Ending X11 Support (gokhshtein)](https://gokhshtein.com/news/2026-09-30-kde-plasma-68-goes-wayland-only-what-the-x11-exit-means-for)
- [This Week in Plasma: Shadows for Steam and Discord (Planet KDE)](https://planet.kde.org/nate-graham-2026-07-18-this-week-in-plasma-shadows-for-steam-and-discord/)
- [As KDE Turns 30, Contributors and Commits are Going Strong (Slashdot)](https://tech.slashdot.org/story/26/09/21/0647232/as-kde-turns-30-contributors-and-commits-are-going-strong)
- [Going all-in on a Wayland future (KDE Blogs)](https://blogs.kde.org/2025/11/26/going-all-in-on-a-wayland-future/)
- [Plasma 6.1 announcement - Explicit Sync (KDE)](https://kde.org/announcements/plasma/6/6.1.0/)
- [KDE Plasma 6.7 Adds Simultaneous HDR and ICC Color Management (lunar.computer)](https://lunar.computer/kde-plasma-6-7-adds-simultaneous-hdr-and-icc-20260616)
- [SteamOS 3.8.10: Support for Steam Machines and KDE Plasma 6.4 (desdelinux)](https://blog.desdelinux.net/en/SteamOS-3.8.10-support-for-Steam-Machines-and-KDE-Plasma-6.4/)
- [Distributions shipping KDE (kde.org)](https://kde.org/distributions/)
- [Schedules/Plasma 6 (KDE Community Wiki)](https://community.kde.org/Schedules/Plasma_6)
- [Help & Support for KDE Software (kde.org)](https://kde.org/support/)

### GNOME
- [Introducing GNOME 51 — Release Notes](https://release.gnome.org/51/)
- [GNOME 51 released — GNOME Discourse](https://discourse.gnome.org/t/gnome-51-released/38820)
- [Introducing GNOME 50 — GNOME Discourse](https://discourse.gnome.org/t/introducing-gnome-50/34400)
- [GNOME Release Calendar](https://release.gnome.org/calendar/)
- [Foundation Budget Report: 2025-26 — GNOME Discourse](https://discourse.gnome.org/t/foundation-budget-report-2025-26/32629)
- [2024-2025 budget and economic review — GNOME Foundation](https://blogs.gnome.org/foundation/2024/10/10/budget-and-economic-review/)
- [GNOME Has Fully Dropped X11 (linuxdork)](https://linuxdork.com/news/gnome-drops-x11-wayland-default/)
- [Updates and Breakage — GNOME JavaScript (gjs.guide)](https://gjs.guide/extensions/overview/updates-and-breakage.html)
- [Orca Screen Reader](https://orca.gnome.org/)
- [Fedora Plasma Workstation change proposal](https://fedoraproject.org/wiki/Changes/FedoraPlasmaWorkstation)
- [Fedora Linux 44 Released (linuxgratis)](https://linuxgratis.com/en/articles/fedora-44)

### 正面交锋与实测
- [KDE Plasma 6.6 Delivers An Impressive Edge For Radeon Graphics Over GNOME 50 (Phoronix, 2026-03-25)](https://www.phoronix.com/review/ubuntu-2604-gnome-kde)
- [KDE Plasma 6.6 Showing Frequent Performance Advantage Over GNOME 50 With NVIDIA R595 (Phoronix, 2026-03-27)](https://www.phoronix.com/review/nvidia-595-kde-gnome)
- [Plasma 6.7 X11 vs Wayland Gaming Performance (Phoronix, 2026-07)](https://www.phoronix.com/review/plasma-67-wayland-cachyos)
- [VRR Improvements Merged To GNOME 50 (Phoronix)](https://www.phoronix.com/news/Mutter-50-VRR-Deadline)
- [GNOME Barely Beats KDE in Gaming Benchmark Comparison (TechPowerUp, 2026-07-21)](https://www.techpowerup.com/350946/gnome-barely-beats-kde-in-gaming-benchmark-comparison-xfce-with-x11-dead-last)
- [KDE vs. GNOME: Ultimate Comparison (phoenixNAP, 2025-12-18)](https://phoenixnap.com/kb/kde-vs-gnome)
- [KDE Making Good Progress On HDR, Better Gamescope Integration (Phoronix)](https://www.phoronix.com/news/KDE-HDR-Colors-Part-3)
- [SteamOS — Valve Developer Community](https://developer.valvesoftware.com/wiki/SteamOS)
- [Variable refresh rate — ArchWiki](https://wiki.archlinux.org/title/Variable_refresh_rate)
- [2025 KDE e.V. Report — KDE e.V.](https://ev.kde.org/reports/ev-2025/)
