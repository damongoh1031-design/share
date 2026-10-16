# openSUSE Slowroll 与 Tumbleweed 差异深度研究报告

> 调研时间：2026-10-15（所有实测数据均在此日期采集）
> 调研方法：以 openSUSE 官方仓库实时目录、openQA API、Factory 邮件列表归档、官方 Wiki/News 为一手证据，
> 并对两个发行版的**同名声明的软件包版本**做了逐个比对。
> 结论标注约定：**【实测】**= 本次直接抓取原始数据得出；**【官方】**= 官方文档/公告明示；**【社区】**= 论坛用户经验，未经官方确认。

---

## 0. 一分钟结论

| 维度 | Tumbleweed (TW) | Slowroll |
|---|---|---|
| 一句话 | 上游 Factory 的**实时投影** | TW 的**月度定基 + 叶子包持续修补** |
| 发布节奏【实测】 | 约每 1–2 天一个快照（49 天内 40 个） | 每月 1 次「version bump」定基 + 近乎每日的维护更新 |
| openQA 门禁规模【实测】 | **每个快照 501 个作业** | **每次定基 5 个作业**（仅安装冒烟） |
| 包版本滞后【实测】 | 基准线 | 落后约 9 天～6 周（视包"核心度"而定） |
| 是否无限期滚动 | 是 | 是 |
| 架构覆盖【实测】 | x86_64 + aarch64/ppc64le/riscv64/s390x | **仅 x86_64** |
| 成熟度标记【官方】 | 正式 rolling | **beta / experimental** |
| 与 Leap 关系【官方】 | 并列的另一种选择 | 并列的另一种选择（**不是** Leap 的替代品） |

**核心洞察（本报告最重要的一句）**：Slowroll 的"更稳"**不是**来自更充分的测试，而是来自**时间差**——
它把 TW 已经"踩过的坑"过滤掉（TW 用户先当小白鼠，几天内修好后 Slowroll 才收到修好的版本）。
Slowroll 自己的自动化测试量级比 TW **小两个数量级**，这正是它至今仍被标记为 beta 的原因。

---

## 1. 定位与历史

### 1.1 三者的坐标系

openSUSE 官方路线图把发行版分成三类【官方】：

| 类型 | 发行版 | 周期 |
|---|---|---|
| Rolling Releases | **Tumbleweed** | 持续更新 |
| Rolling Releases | **Slowroll** | **30 天** |
| Atomic Rolling | Aeon / Kalpa / MicroOS | 同 Tumbleweed |
| Classic | Leap / Leap Micro | ~12 个月小版本，~24 个月支持 |

也就是说，官方已经把 Slowroll 与 Tumbleweed 并列为两种**同样是滚动、但节奏不同**的发行版，
而不是把 Slowroll 归到 Leap 那一类。

### 1.2 Slowroll 的由来（以及一个必须澄清的误解）

- Slowroll 诞生于 **2023 年**，由 `bmwiedemann`（Bernhard M. Wiedemann）设计与实现【官方】。
- 它出现在 **Leap 未来未定**（SUSE 转向 ALP）的那段不确定期，但**与 Leap 的发布流程没有任何关系**【官方】。
- 官方多次强调：**Slowroll 不是 Leap 的替代品**。《Clarifying Misunderstandings of Slowroll》一文原话是
  "Think of Slowroll as more of a **skip** than a Leap"（把它理解成"跳着滚"，而不是"跨越版"）。
- 名字是通过社区投票保留下来的【官方】。

> **常见的错误期待**：把 Slowroll 当成"滚动版 Leap"或"更稳的 Tumbleweed"。
> 更准确的说法是 **"Tumbleweed 的月度定基版"**——包全部来自 TW，只是取值时间不同。

### 1.3 当前状态：仍然是 beta

截至 2026-10-15，官方 Wiki 门户与发行版列表都仍把 Slowroll 标为 **beta**【官方】。
Wiki 原文：`Currently, Slowroll is still in beta phase so please be mindful of any bugs, glitches...`

2025 年 1 月的官方新闻给出了原因：`While still marked as experimental (for lack of automated tests)`
——"因为缺少自动化测试"。**注意：这句话到今天需要打折理解**，因为现在已经有 openQA 覆盖了（见第 4 节），
但覆盖面只有 5 个作业，量级远不足以"正式发布"。

---

## 2. 发布模型：最大的实质差异

### 2.1 Tumbleweed 是怎么跑的

Tumbleweed 是 openSUSE **Factory** 项目的直接产物：包在 Factory 中不断被接受 → 触发依赖链重建 →
整包快照通过 openQA 门禁 → 自动发布为一个"snapshot"。

**Tumbleweed 快照实测节奏**（openQA 组 `openSUSE Tumbleweed`，groupid=1）【实测】：

```
20261014  20261013  20261012  20261011  20261010  20261009  20261008  20261007
20261006  20261005  20261003  20261002  20261001  20260930  20260929  20260928
20260924  20260923  20260922  20260921  20260919  20260918  20260917  20260916
20260915  20260914  20260912  20260911  20260910  20260909  20260908  20260907
20260904  20260902  20260901  20260831  20260830  20260829  20260828  20260827
```

- 40 个快照覆盖 2026-08-27 → 2026-10-15，共 **49 天 ⇒ 约 0.82 个/天**。
- 官方的月度回顾口径一致：**2026 年 8 月 23 个快照**（31 天）、**2026 年 2 月 17 个快照**（28 天）【官方】。
- 即：**平均每 1–2 天一次完整的 `zypper dup` 机会**。

### 2.2 Slowroll 是怎么跑的（两套节奏叠加）

Slowroll 的机制更复杂，必须拆成两层：

**第一层：每月的 "version bump"（定基）**

机制可以完整还原出来【实测 + 官方】：

1. 从 Tumbleweed 挑一个快照作为**基准（base）**，以该快照日期命名。
2. 在 OBS 项目 `openSUSE:Slowroll` 中整体重建（重建量约 25000 个 RPM）。
3. 进 `openSUSE:Slowroll:Build:1` / `:2` 暂存，跑 openQA 冒烟测试。
4. 通过后落到镜像树的 **`next/` 与 `next-full/`** 暂存目录，再提升为正式仓库。

镜像树中可以直接看到这套机制的痕迹【实测】：

```
slowroll/
├── repo/oss/            ← 当前正式仓库
├── next/                ← 下一次定基的暂存
├── next-full/
│   ├── base.20260707/
│   ├── base.20260802/
│   ├── base.20260901/
│   ├── base.20261001/
│   └── base-next-full -> base.20261001   ← 符号链接指向"下一次"
└── iso/
```

**命名与发布时机**：当前正式仓库里的 `openSUSE-release` 版本号是 **`20261001`**，
而 2026-10 的发布工程会议纪要明确写着【一手】：

> `## Bernhard - Slowroll Version bump to 20261001 happened on 2026-10-09 - mostly smooth.
> Still fighting dependency issues from ffmpeg (-mini). Users reported an issue with KDE and
> ext-screens that were previously affecting Tumbleweed`

⇒ **定基编号 = 所依据的 TW 快照日期；标称"每月 9 日前后"= base 快照 + 约 8 天的重建与验证时间。**
这解释了 Wiki 上那句 `big updates once per month (usually around the 9th day of the month +-3d)`。

**第二层：定基之间的持续维护更新**

这是最容易被误解的一点。Slowroll **不是"一个月只更新一次"**，而是**持续推送低风险包**。
实测到的发布公告（Factory 邮件列表，脚本自动生成）【实测】：

| 公告 ID | 包数量 | 内容特征 |
|---|---|---|
| `20261014T0329` | **64 个** | pyside/multimedia/python-* 等叶子包 |
| `20261012T2259` | **126 个** | blender / ffmpeg / vlc / mpv / wireshark 等 |
| `20260820T1623` | **36 个** | ast-grep / gimp / postgresql 等 |

社区用户的体感与此吻合【社区】：
> "You can expect one large update monthly around the 9th and **smaller updates with security and
> bugfixes near-daily** (same frequency as Tumbleweed, but only 30% ...)"

> 同一条讨论里还有用户抱怨在这种"近乎每日"的推送下，一次 `dup` 会装 **1000–2000 个包、1–2 GB**。

**为什么会这样？** 因为 Slowroll 的自动化脚本用**"核心度（core-ness）"打分**来分流【一手】——
`slowroll-tools` 仓库 README 原文：

> "we need to collect data to asses risk of updates e.g. **the core-ness of a package increases risk of
> breaking other parts that depend on it**. We can try to express that as a single float between
> **0 (leaf - nothing depends on it) and 1 (core - everything depends on it - e.g. systemd/glibc)**"

⇒ **叶子包（多媒体、Python 库、游戏、应用）持续放行；越靠核心（glibc/systemd/编译器/内核）越要等定基。**

### 2.3 节奏对比总表

| 指标 | Tumbleweed | Slowroll |
|---|---|---|
| 完整快照/定基频率【实测】 | ≈0.8/天（月均 17–23 次） | **1 次/月** |
| 维护更新频率【实测】 | 无独立概念（一切都在快照里） | **每周数次、有时同日两次** |
| 单次完整更新体量【社区】 | 数百 MB～1 GB | 定基 1–2 GB；维护更新数十～百个包 |
| 定基命名【实测】 | `20261014`（快照日期） | `20261001`（**继承 TW 快照日期**） |
| 延迟【实测】 | 0 | 见第 3 节 |

---

## 3. 实测：包版本到底差多少

这是最能说明问题的证据。2026-10-15 对**同名软件包**在两个 `repo/oss/x86_64` 目录中逐一比对【实测】：

| 软件包 | Slowroll | Tumbleweed | Slowroll 构建日期 | TW 构建日期 | 结论 |
|---|---|---|---|---|---|
| **kernel-default** | 7.2.8 | **7.2.9** | 2026-09-28 | 2026-10-07 | 落后 **1 个补丁版 / 9 天** |
| **MozillaFirefox** | 156.0 | **157.0.1** | 2026-09-28 | 2026-10-10 | 落后 **1 个大版本 / 12 天** |
| **Mesa** | 26.2.3 | **26.2.4** | 2026-09-21 | 2026-10-02 | 落后 **1 个补丁版 / 11 天** |
| **qemu** | 11.1.1 | **11.1.2** | 2026-09-08 | 2026-10-08 | 落后 **1 个补丁版 / 30 天** |
| **python313** | 3.13.15 | **3.13.16** | — | — | 落后 1 个版本 |
| **gimp** | 3.2.6-3.1 | 3.2.6-**4.1** | — | — | 同上游版本，仅发行号落后 |
| **glibc** | 2.44-**2.1** | 2.44-**3.1** | — | — | 同上游版本，仅发行号落后 |
| **plasma6-workspace** | 6.7.5 | 6.7.5 | — | — | **完全同步** |
| **systemd** | 261.3 | 261.3 | — | — | **完全同步** |
| **php8** | 8.5.11 | 8.5.11 | — | — | **完全同步** |
| **libreoffice** | 26.8.1.1 | 26.8.1.1 | — | — | **完全同步** |
| **gcc16** | 16 | 16 | — | — | **完全同步** |

**如何解读这组数据**：

1. **差距远没有"一个月"那么大。** 因为定基之后维护更新仍在跑，很多包其实已经追平（systemd/Plasma/PHP/LibreOffice 完全一致）。
2. **越核心的包越落后。** 内核、glibc、编译器、Firefox 这几个正是"核心度高 / 风险高"的包，需要等下一个定基。
3. **落后量级是"一个点版本"而不是"一代"。** 差别是 7.2.8 vs 7.2.9，不是 7.1 vs 7.2。
4. **官方口径的 "5 to 10 days after being released in Tumbleweed"**【官方】是一条**平均数**；实测里 qemu 达到 30 天，
   说明长尾是会存在的。

**仓库规模对比【实测】**：`repo/oss/x86_64` 目录下

- Slowroll：**25,019** 个 RPM
- Tumbleweed：**26,256** 个 RPM

即 Slowroll 大约是 TW 的 **95%**，是一个近乎全量的重建，而不是"精简子集"。

---

## 4. 质量门禁：差异最悬殊的一项

openQA 是 openSUSE 的自动化测试引擎，也是决定"能不能发布"的闸门。

**Tumbleweed**（openQA groupid=1）【实测】：

```
build       日期                  作业数   通过    失败   软失败  未完成
20261014    2026-10-15T06:52:02    501    391     0      73     37
20261013    2026-10-14T01:48:43    501    414     1      86      0
20261012    2026-10-13T05:21:53    501    417     0      84      0
20261011    2026-10-11T20:27:48    501    418     0      83      0
20261010    2026-10-11T08:11:31    501    412     0      89      0
20261009    2026-10-10T03:30:37    501    419     0      82      0
```

⇒ **每个快照 501 个作业**，覆盖安装、升级、桌面、应用等大量场景；失败会阻塞快照发布。

**Slowroll**（openQA groupid=131，`openSUSE Slowroll`）【实测】：

```
build    日期                  作业数   通过   失败   软失败
70.1     2026-10-01T16:55:31      5      2     2      1
69.3     2026-09-09T13:20:05      5      4     1      0
69.2     2026-09-03T09:11:50      5      4     1      0
69.1     2026-09-02T09:53:04      5      1     4      0
68.1     2026-09-02T01:40:18      5      1     4      0
66.1     2026-08-03T05:24:34      5      2     2      1
65.1     2026-08-02T14:06:01      5      1     4      0
64.1     2026-07-30T11:13:59      5      1     4      0
```

作业内容实测（`/api/v1/jobs?groupid=131`）只有 5 个安装冒烟用例：

```
gnome / kde / mediacheck / textmode / uefi   （全部为 DVD x86_64）
```

**⇒ 501 : 5 ≈ 100 : 1。**

**这带来的推论很重要**：

- Slowroll 的开放测试**只验证"这张 DVD 能不能装上、能不能起桌面、介质校验对不对"**，
  不验证应用行为、不验证升级路径、不验证多硬件组合。
- 定基过程**确实会被 openQA 卡住并反复重试**：例如 2026 年 9 月 `69.1 → 69.2 → 69.3` 连续三个 respin，
  直到 9 月 9 日全部通过才放行（对应 Wiki 说的"9 日前后 ±3 天"）。
- 但**首次尝试经常大面积失败**（`64.1/65.1/68.1/69.1` 都是 5 个里失败 4 个）。这说明"冒烟通过"本身不是理所当然。
- 因此：**Slowroll 的稳定性红利主要来自"等 TW 用户先踩坑"，而不是来自自己更严的门禁。**

---

## 5. 技术同源性与真正的差异清单

两者是同一条流水线的不同取值点，所以**大量机制完全相同**：

| 机制 | Tumbleweed | Slowroll | 是否相同 |
|---|---|---|---|
| 包来源 | Factory / Tumbleweed | **直接取自 Tumbleweed** | 同源 |
| 升级命令 | `zypper dup` | `zypper dup` | ✅ 相同 |
| 包管理器/ZYpp | libzypp + zypper | 同左 | ✅ |
| 文件系统与回滚 | Btrfs + snapper，`snapper rollback` | 同左 | ✅ |
| 图形包管理 | Myrlyn（支持二者） | 同左 | ✅ |
| 第三方仓库 | Packman、NVIDIA 等 | **有专门的 Slowroll Packman 仓库** | ⚠️ 有差异 |
| 发布模型 | 无限期滚动，无 EOL | 无限期滚动，无 EOL | ✅ 相同 |
| 仓库定义包 | `openSUSE-repos-Tumbleweed` | `openSUSE-repos-Slowroll` | ⚠️ 不同包 |
| 架构【实测】 | x86_64 + aarch64/ppc64le/riscv64/s390x | **仅 x86_64** | ❌ 不同 |
| openQA 覆盖【实测】 | 501 作业/快照 | 5 作业/定基 | ❌ 悬殊 |
| 成熟度标记【官方】 | 正式 | **beta** | ❌ 不同 |

### 5.1 架构：一个容易被忽略的硬差异

实测 HTTP 探测结果【实测】：

```
200  ports/aarch64/tumbleweed/repo/oss/     ← TW 有 aarch64
200  ports/ppc/tumbleweed/repo/oss/         ← TW 有 ppc64le
200  ports/riscv/tumbleweed/repo/oss/       ← TW 有 riscv64
200  ports/zsystems/tumbleweed/repo/oss/    ← TW 有 s390x
404  ports/aarch64/slowroll/repo/oss/       ← Slowroll 无 aarch64
404  ports/riscv64/slowroll/                ← Slowroll 无 riscv64
```

Slowroll 的 `repo/oss/` 下只有 `x86_64/` 与 `noarch/`；所有 ISO 都是 `openSUSE-Slowroll-DVD-**x86_64**-BuildNN.N`。
**⇒ 如果你在 ARM / RISC-V / POWER / s390x 上，Slowroll 不是选项。**

### 5.2 第三方仓库与驱动【官方】

Wiki 明确警告：

- **不建议**在 Slowroll 上叠加 development 仓库，除非该包是为 Slowroll 专门编译的。
- 未针对 Tumbleweed 测试过的第三方仓库可能**直接弄坏系统**。
- Packman：**可能可用，但偶尔会坏**；官方提供专用源：
  ```
  zypper ar --refresh -p 70 http://ftp.gwdg.de/pub/linux/misc/packman/suse/openSUSE_Slowroll/Essentials/ packman
  ```
- NVIDIA：早期直接**复用 TW 的 NVIDIA 仓库**（`openSUSE-repos` 变更日志中有
  "Re-use TW Nvidia repo for Slowroll"）。

**实践含义**：Slowroll 的第三方生态**比 TW 更薄**。尤其是闭源驱动、OBS 社区包、
按"TW 的库版本"编译的第三方二进制，在 Slowroll 上会遇到依赖不匹配。

---

## 6. 用户侧实际体验差异

### 6.1 每日/每周体感

| 场景 | Tumbleweed | Slowroll |
|---|---|---|
| 多久想更新一次 | 每天都有新快照 | 平时小更新，月初一次大更新 |
| 大更新体量【社区】 | — | **1000–2000 个包 / 1–2 GB** |
| 会不会被打断 | 高频；被部分用户抱怨"像在管小孩" | 明显更少 |
| 出问题时的补救 | snapper 回滚 | snapper 回滚（同） |
| 是否需要懂内核模块编译【官方】 | 官方建议"需要进阶技能"（第三方内核驱动） | 同样适用 |

### 6.2 "更稳"到底稳在哪——社区实证

2026 年 2 月论坛讨论《Is slowroll to be recommended these days?》中的高赞回答【社区】：

> "Slowroll is Tumbleweed with some delay. That means that **immediate problems that might bring
> Tumbleweed to a halt, and that are typically fixed within a few days, won't ever hit you**;
> you just receive the new version of the packages that already include the fix.
> The bump in the road is already smoothed over by the time you get there."

同一帖里另一位用户给出了具体案例【社区】：

> "Yeah, SR users f.e. **weren't hit by the ddcutil / udev issues**."

还有长期用户反馈"用了两年很稳"、"在 6 年前的老笔记本上工作良好"。

**但也要注意反面证据**：定基本身会把 TW 尚未修好的问题一起带进来。2026 年 10 月的发布工程纪要明确记录
【一手】：

> `Users reported an issue with KDE and ext-screens that were previously affecting Tumbleweed`

⇒ **Slowroll 不是"没有问题"，而是"问题的到达时间被推迟、且很多已被上游修掉"。**

---

## 7. 迁移与切换

### 7.1 官方迁移工具【官方】

openSUSE 提供了 `opensuse-migration-tool`，明确支持双向迁移：

```
Tumbleweed       → Slowroll        ✅ 支持
Slowroll         → Tumbleweed      ✅ 支持
Leap             → Tumbleweed / Slowroll   ✅ 支持
Tumbleweed       → Leap            ❌ 不支持（降级）
```

操作步骤（官方推荐流程）：

```bash
sudo zypper in opensuse-migration-tool
sudo opensuse-migration-tool --dry-run     # 先干跑
sudo opensuse-migration-tool               # 真正迁移
sudo reboot
```

**注意事项【官方】**：

- 发行版仓库里打包的那版工具**缺一个修复，可能导致迁移到 Slowroll 失败**；
  官方建议遇到问题就去 GitHub 拉最新版直接运行。
- 迁移过程会**禁用所有非默认仓库**。
- 迁移**不需要重装系统**（社区也确认："You do not need to reinstall"）。

### 7.2 手动方式（旧文档保留的做法）【官方】

```bash
# Leap → Slowroll 需先补一个源
sudo zypper addrepo https://download.opensuse.org/slowroll/repo/oss/ leap-to-slowroll
# 然后切换 openSUSE-repos 并 dup
```

### 7.3 方向性：只有"降级"是慢的

- **Slowroll → TW**：纯升级，通常顺滑。
- **TW → Slowroll**：本质是**部分降级**（很多包版本要往回走）。虽然官方支持，
  但降级历来是发行版里最容易出问题的操作。建议干跑 + snapper 快照 + 先备份。

---

## 8. 你该选哪一个（决策矩阵）

| 你的处境 | 建议 |
|---|---|
| 想要最新内核/驱动/桌面，愿意承担偶发问题 | **Tumbleweed** |
| 生产机 / 办公主力机，最怕"更新完起不来" | **Slowroll** |
| 需要在 ARM、RISC-V、POWER、s390x 上跑 | **只能 Tumbleweed**（Slowroll 无这些架构） |
| 依赖大量 OBS 第三方包 / 闭源驱动 | **Tumbleweed**（第三方生态按 TW 的库版本编译） |
| 厌烦每天都有更新提示 | **Slowroll** |
| 需要企业级、可预期的 ABI 与多年支持 | **Leap 16.x**（不是这两个中的任何一个） |
| 想极简、原子更新、可回滚的不可变系统 | Aeon / Kalpa / MicroOS（节奏同 TW） |
| 新硬件（刚上市半年的 CPU/GPU）首发支持 | **Tumbleweed**（Slowroll 要等一个定基周期） |

**一句话选择法**：
> 想**现在就拿到** → Tumbleweed；想**别人先试过再给我** → Slowroll；想**五年不变** → Leap。

---

## 9. 常见误解与坑

| 误解 | 事实 |
|---|---|
| "Slowroll 是一个月只更新一次" | 错。定基每月一次，但**维护/安全更新几乎每天**（实测 10 月 12 日 126 个包、14 日 64 个包）。 |
| "Slowroll 是稳版的 Leap 替代品" | 错。官方反复强调它不是 Leap 替代品；它仍是无限期滚动、无 EOL。 |
| "Slowroll 比 TW 测试更充分" | **反了**。Slowroll 自己只有 5 个安装冒烟作业，TW 有 501 个。慢工出来的"稳"来自延迟，不来自测试。 |
| "慢 = 落后一个月" | 实际多数包只落后 1 个点版本、9–30 天；不少包（systemd/Plasma/PHP/LibreOffice）与 TW 完全一致。 |
| "直接从 TW 切过去随便切" | 官方工具支持，但那是**部分降级**。务必 `--dry-run` + 快照。 |
| "第三方仓库随便加" | Wiki 明确警告会弄坏系统；Packman 要用 Slowroll 专用源；NVIDIA 源是复用 TW 的。 |
| "包会少很多" | 实测只少约 5%（25,019 vs 26,256 个 RPM）。 |

---

## 10. 治理与可持续性观察

- **主开发者高度集中**：Slowroll 由 `bmwiedemann` 设计并维护脚本，发布工程会议里由他单线汇报。
  **巴士系数偏低**是该发行版最需要留意的结构性风险。
- **自动化程度高**：定基、维护更新、公告邮件（"this mail was generated by a script"）都是自动化的，
  这对冲了一部分单点风险。
- **上游依赖强**：Slowroll 完全建立在 Factory/Tumbleweed 之上，自身**没有独立的分支维护负担**
  （社区常引用的说法是"没有重复劳动、不与 SLE 版本锁步"）。这意味着只要 TW 活着，Slowroll 的输入就存在。
- **长期定位已明确**：官方路线图把 Slowroll 的周期写作 30 天，与 TW 并列——说明它已从
  "2023 年的实验"演化为**长期存在的产品线**，即使仍标 beta。

---

## 11. 未验证项 / 需要谨慎的部分

以下内容本次调研**没有拿到确证**，报告中已尽量回避或标注：

1. **Slowroll 的精确"支持承诺"**：官方没有给出 SLA、也没有 EOL 日期（因为它是滚动版），
   但也没有明确承诺"永久存在"。**（逻辑外推，非直接证据）**
2. **openQA 的 5 个作业是否是硬门禁**：从连续 respin 推断是**阻断式**门禁，但未见官方文档明确定义。
3. **`next/` 与 `next-full/` 的精确语义**：本次实测看到 `base.YYYYMMDD` 目录与 `base-next-full` 符号链接，
   推断为定基暂存区；未找到官方文字定义。
4. **`MicroOS-Slowroll`**：只在 `opensuse-migration-tool` 的支持路径列表里出现过，
   本次**未在镜像树中找到对应发布物**，是否存在独立产品待确认。
5. **维护更新公告的准确频次**：邮件列表归档页有分页/反爬限制，本次只逐条确认到具体几封（10 月 12 日、14 日等），
   **未得到完整月度计数**。
6. **镜像数据存在同步时滞**：本次比较用的是 MirrorCache 上的目录快照，个别文件时间戳可能落后于主镜像。
7. **"5 to 10 days" 的官方说法与实测 30 天（qemu）的矛盾**：官方口径应是均值，长尾未被覆盖。
   **（推测，未经官方确认）**

---

## 12. 参考来源

**一手数据（本次直接抓取）**
- openQA API：`https://openqa.opensuse.org/api/v1/job_groups`、`/job_groups/1/build_results`、`/job_groups/131/build_results`、`/jobs?groupid=131`
- 镜像树：`https://download.opensuse.org/slowroll/`（`repo/oss/x86_64/`、`iso/`、`next/`、`next-full/`）、`https://download.opensuse.org/tumbleweed/repo/oss/x86_64/`
- Factory 邮件列表 2026-10 归档（含 Release Engineering 会议纪要、Slowroll 更新公告）
- `https://github.com/openSUSE/slowroll-tools`（core-ness 打分机制）
- `https://github.com/openSUSE/opensuse-migration-tool`（支持的迁移路径）

**官方文档与公告**
- [Portal:Slowroll (openSUSE Wiki)](https://en.opensuse.org/Portal:Slowroll)
- [openSUSE:Roadmap (openSUSE Wiki)](https://en.opensuse.org/openSUSE:Roadmap)
- [Archive:Old Slowroll Page](https://en.opensuse.org/Archive:Old_Slowroll_Page)
- [Clarifying Misunderstandings of Slowroll](https://news.opensuse.org/2024/01/19/clarifying-misunderstandings-of-slowroll)
- [Slowroll Set for a Quarter of Updates](https://news.opensuse.org/2024/07/03/slowroll-set-for-a-quarter-of-updates)
- [Slowroll Updates Boost Stability, Enhance Performance](https://news.opensuse.org/2024/09/02/slowroll-up)
- [New Year Starts with Slowroll Version Bump](https://news.opensuse.org/2025/01/09/ny-starts-with-slowroll-vb/)
- [Tumbleweed Monthly Update – August 2026](https://news.opensuse.org/2026/09/02/tw-monthly-update-august/)
- [SDB:Upgrade Tumbleweed](https://en.opensuse.org/SDB:Upgrade_Tumbleweed)

**媒体与社区**
- [Phoronix: openSUSE Slowroll Released As A Slower Alternative To openSUSE Tumbleweed](https://www.phoronix.com/news/openSUSE-Slowroll)
- [FOSS Force: Slowroll: openSUSE's New Take on the Rolling Release Model](https://fossforce.com/2023/09/slowroll-opensuses-new-take-on-the-rolling-release-model)
- [openSUSE Forums: Is slowroll to be recommended these days?](https://forums.opensuse.org/t/is-slowroll-to-be-recommended-these-days/191974)
- [openSUSE Forums: Slowroll – updates released almost daily?](https://forums.opensuse.org/t/slowroll-updates-released-almost-daily/184168)

---

*报告结束。所有【实测】数据可通过上述 API/目录链接复现；数据采集于 2026-10-15，滚动发行版状态随时间变化，建议按需复核。*
