# RimWorld 1.7 模组兼容性核查报告

**核查对象**：`C:\Users\Admin\Documents\ce0906.xml`（ModsConfig，游戏版本 1.6.4871 rev598，启用 336 项）
**核查日期**：2026-10-19（周一）
**核查方式**：官方公告 + GitHub 仓库版本核对 + 社区实测反馈交叉验证。**未做本机启动实测**（本机未装 RimWorld）。

---

## 0. 结论先行

**你的 336 个 mod 里，大部分可以原样搬进 1.7，但有 3 类必须先处理**：

| 动作 | mod | 原因 |
|---|---|---|
| 🔴 上 1.7 前先禁用 | `taranchuk.performanceoptimizer`（+`optimizer.zh`） | GitHub 仓库最后提交停在 2026-01，无 1.7 适配；社区实测「优化类应该都有问题」 |
| 🔴 等作者修复 | `nebulae.rimworld`（NebulaeFlood's Lib） | 社区实测：装上后主界面按钮点了就滚木、ESC 都退不出 |
| 🟠 先禁用再逐个试 | `ods.isekairetexture`、`font.rimesis`、`telefonmast.graphicssettings`、`m00nl1ght.mappreview`、`owlchemist.midsaversaver`、`sarg.smartspeed` | 贴图/字体/图形/性能类，正是引擎迁移（换渲染层）最敏感的类别，已有 UP 主实测「个别贴图 mod 有大问题」 |
| 🟢 已确认适配 | `iforgotmysocks.caravanadventures` | v1.9.0 于 2026-10-16 发布，release 原文 "compatibility with RimWorld v1.7" |
| 🟡 等官方新版 | `ceteam.combatextended` | CE 7.4（v1.6.7.4.0）2026-10-15 发布，tag 仍是 `v1.6.*`，标题 "Waylith Awaits" = 1.7 版在途未发 |

**108 个汉化包（纯 XML）和 81 个 Vanilla Expanded 系列是当前证据下最稳的两块**，不用动。

---

## 1. RimWorld 1.7 是什么（官方口径，2026-10-12 公告）

| 项 | 事实 |
|---|---|
| 变更 | 引擎从 **Unity 迁到自研 Waylith**（Ludeon 自研，底层为 RocketWerkz 开源的 BRUTAL 框架 + fork 的 .NET 10 运行时 + Unity API 兼容壳） |
| 玩法/画面 | 官方称「完全不变」；性能提升 2–4 倍（后期存档实测 2.2 倍；1500 mod 包加载 14 分钟→6 分钟） |
| 存档 | **双向兼容**：1.6 存档可在 1.7 开，1.7 存档可回 1.6 |
| Mod | 官方原话「绝大多数 mod 无需作者任何修改即可运行」；未更新的 mod 只显示**黄色 "potentially unsupported" 警告**，仅因版本号变更，不代表真不兼容 |
| 上线方式 | 目前仅在 Steam **unstable 测试分支**；主分支保持 1.6。稳定版时间表未公布 |
| 已知硬门槛 | 服役超 10 年的老 PC 可能跑不动 |

> 官方要 mod 作者做的事：测试自己的 mod → 发一个标 1.7-compatible 的版本 → 玩家端黄警告消失。**公告日至今仅一周，绝大多数作者还没发新版**，所以黄警告会很多，属预期。

---

## 2. 336 个 mod 分类风险总表

| 类别 | 数量 | 1.7 预期 | 依据 |
|---|---|---|---|
| 官方本体 + 5 DLC | 6 | 🟢 必兼容 | 1.7 就是官方客户端 |
| 汉化包（纯 XML 翻译，无 C#） | 108 | 🟢 低风险 | 只改 DefInjected/Keyed 文本，不碰汇编；rwzh 系列 supportedVersions 已放宽到 1.7 |
| Vanilla Expanded 全家桶（框架+81 内容） | 82 | 🟢 较稳 | 框架仓库 10-17/18 仍在活跃提交；社区实测「vef 的框架…兼容性都还行」 |
| 框架/前置库（Harmony、HugsLib、VF、EBFW、SRALib、Aoba、Adaptive Storage 等） | 35 | 🟡 分化 | Harmony 已同步更 1.7（社区实证）；多数无公开仓库可验 → 见 §3 逐个表 |
| 其他 C# 功能 mod | 97 | 🟡 需实测 | 官方口径「绝大多数免改」+ Unity 兼容壳存在，但无人人验证过；这也是**最可能出红字的一层** |
| 优化/性能类 | 7 | 🟠 高风险 | 改游戏循环/缓存，正是引擎迁移重写区；社区原话「优化类的应该都有问题」 |
| 贴图/字体类 | 3 | 🟠 高风险 | 渲染层整体更换；UP 主实测「个别贴图 mod 有大问题」 |
| Combat Extended（+补丁） | 2+ | 🟡 未适配 | 1.7 版未发布，见 §3 |

---

## 3. 逐个核实过的关键 mod（有据可查的）

| mod（packageId） | 证据 | 日期 | 1.7 状态 |
|---|---|---|---|
| `ceteam.combatextended` | GitHub release `v1.6.7.4.0` "Waylith Awaits" | 2026-10-15 | 🟡 **仍是 1.6 构建**，1.7 版未发；带 CE 上 1.7 属抢跑 |
| `brrainz.harmony` | 贴吧实测反馈「harmony 更新 1.7 的同时也更新了 1.6」 | 2026-10-13 | 🟢 已双版本更新（社区实证）；注意：该更新曾把 1.6 的「珂莉姆」mod 带炸，**更新框架本身有回归风险** |
| `oskarpotocki.vanillafactionsexpanded.core` / `vanillaexpanded.vfecore` | 仓库提交活跃（smart weapons、custom fire system） | 2026-10-17/18 | 🟢 团队在岗，未发 1.7 tag 但无坏消息 |
| `iforgotmysocks.caravanadventures` | v1.9.0 release："compatibility with RimWorld v1.7" | 2026-10-16 | 🟢 **已适配**（贴吧此前实测爆红字，作者周末已修） |
| `nebulae.rimworld` | 贴吧实测：装上后主菜单进功能页直接滚木、ESC 无效，只能回退 1.6 | 2026-10-15 | 🔴 **未修复**，等作者 |
| `taranchuk.performanceoptimizer` | 仓库最后提交 2026-01-12，无 1.7 痕迹 | 2026-01-12 | 🔴 未适配，建议 1.7 下先禁用 |
| `smashphil.vehicleframework`（载具框架） | 贴吧讨论「载具框架+sos2 呢，sos2 总得等更新」→ VF 本身未见事故，**SOS2 才需等**（你没装 SOS2） | 2026-10-13 | 🟢 较稳 |
| Replace Stuff（原版） | 实测不兼容 → 换 `Replace Stuff - Continued` 即可 | 2026-10-13 | ✅ 你没装原版，无需处理 |
| Mod Manager (Continued) | 1.7 下拖拽 mod 粘滞 | 2026-10-15 | ✅ 你没装，无需处理 |
| 种族 mod（残阳3/翠鸟/空洞骑士/涅瓦莲/渡鸦） | 吧友实测：涅瓦莲炸得最彻底、渡鸦族有小问题已有补丁 | 2026-10-13 | ✅ 你这清单里没有这几个 |

**无法逐个核实的**：其余 ~200 个 C# mod（含 `cj.rimtalk` 全家、`jaxe.bubbles`、`v1024.ebframework`、`dizhuan.sralib`、`aoba.*`、`hailuan.customquestframework`、`kindseal.*`、`astryl.truerpginventory`、`vr.missilegirl` 等）——名字都在上面分类表里，**没有任何公开证据说它们兼容或不兼容**，只能按「官方口径 + 实测」判定。不编造结论。

---

## 4. 上 1.7 的安全操作顺序

1. **备份**：复制整个 `ModsConfig.xml` + `%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\`（存档所在）到另一处。1.7 在 unstable 分支，随时可能回退。
2. **切分支**：Steam 库 → 右键 RimWorld → 属性 → 测试版 → 选 `unstable` → 重启 Steam。
3. **第一批只上稳的**：VE 全家桶 + Harmony + Caravan Adventures（先更到 v1.9.0）+ 全部汉化包。原生无 mod 跑一次，确认客户端本身没问题。
4. **先禁这 8 个再进**：`taranchuk.performanceoptimizer`(+`optimizer.zh`)、`nebulae.rimworld`、`ods.isekairetexture`、`font.rimesis`(+`openclaw.translation.rimesis.chinese`)、`telefonmast.graphicssettings`(+`tinygrox.chs.graphicssettings`)、`m00nl1ght.mappreview`(+`zh.m00nl1ght.mappreview`)、`owlchemist.midsaversaver`(+`chinesepackage.owlchemist.midsaversaver`)、`sarg.smartspeed`(+`soulwolf.ch.smartspeed`)。
5. **CE 最后上**：等 CE 发 Waylith 版（tag 不再是 v1.6.*）。在此之前 CE 生态（`ufhi.series.cepatch`、`tot.celetech.mkiii`、`lemontea.combatextendedzh`）留在 1.6。
6. **爆红字就二分**：mod 列表对半禁用定位，日志看 `Player.log`。吧友经验：1.7 的红字 80% 是个别 C# mod，不是配置问题。
7. **回退无痛**：存档双向兼容，切回主分支即回 1.6。

---

## 5. 顺带发现（与 1.7 无关，1.6 时就存在）

- `zh.adaptive.storage.neolithic`（汉化包）声明的依赖本体没装：Adaptive Storage Neolithic Module / Global Settings / Old Simple Storage —— 若只装了 `adaptive.storage.framework`，该汉化可能空转。
- `shavius.vie.zh` 引用了未安装的 `vanillaexpanded.ideo.sophianstyle`（软依赖，无害但无效果）。
- 以上为社区库元数据口径，最终以各 mod 目录内 About.xml 的 `modDependencies` 为准。

---

## 6. 数据来源与时效

| 来源 | 日期 | 内容 |
|---|---|---|
| Ludeon 官方博客（1.7 公告） | 2026-10-12 | 引擎迁移、存档双向兼容、mod 免改、unstable 分支 |
| GitHub `CombatExtended-Continued/CombatExtended` | 2026-10-15 | CE 7.4 = v1.6 构建 |
| GitHub `iforgotmysocks/CaravanAdventures` | 2026-10-16 | v1.9.0 适配 1.7 |
| GitHub `Vanilla-Expanded/VanillaExpandedFramework` | 2026-10-18 | 活跃开发中 |
| GitHub `Taranchuk/PerformanceOptimizer` | 2026-01-12 | 已停更 |
| 百度贴吧 rimworld 吧实测帖 ×4 | 2026-10-13 ~ 10-15 | 点名不兼容清单、Replace Stuff、Mod Manager、NebulaeFlood |
| B 站 UP 主实测视频 | 2026-10-13 | 红字原因、贴图 mod 问题 |
| RimSort 工坊数据库 | 2026-10 | 336→名称解析（其 gameVersions 字段不可作为 1.7 判据：汉化包普遍写 1.0–1.9 全版本） |

**下次复查触发**：CE 发 Waylith 版 / NebulaeFlood 更新 / 1.7 上主分支稳定版 —— 任一发生即重跑本报告。
