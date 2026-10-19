# RimWorld 1.7 仙路整合包（xianlu.xml）兼容性核查报告

**核查对象**：`C:\Users\Admin\Documents\xianlu.xml`（ModsConfig，游戏版本 1.6.4871 rev598，启用 343 项）
**核查日期**：2026-10-19
**核查方式**：官方公告 + GitHub 仓库核对 + RimSort 依赖库 + 前三份清单既有实测交叉验证。**未做本机启动实测**（本机未装 RimWorld）。

---

## 0. 结论先行

**结构：343 个的「OA 框架 + 鼠族 + 多族混编」大包。可上的部分（VE 65 + 汉化 101 + 框架 36）与前两份同源、随时可迁；卡点三个：CE 8 个等版、Nebulae 1 个禁用、鼠族 15 个本体无 1.7 确认。**

| 动作 | mod | 原因 |
|---|---|---|
| 🔴 禁用 | `nebulae.rimworld`（NebulaeFlood's Lib） | 10-15 实测 1.7 主菜单滚木/ESC 失效，未修复。已查 RimSort 依赖库：**本清单内无连带者**（Simply More Roofs 不在这份清单），只禁它一个即可 |
| 🔴 卸载或补装 | `optimizer.zh` | Performance Optimizer 的汉化，但**本体 `taranchuk.performanceoptimizer` 没装** → 纯空转，建议直接卸载（别指望它了，本体已停更） |
| 🟡 等 CE | CE 本体 + `chaiop.ratkincepatchcollection`、`kiiroseries.ceintegration`、`moelotlseries.ceintegration`、`ufhi.series.cepatch`、`lemontea.combatextendedzh`、`happyzz.ce.mustard1557.mugb.goblin`、`tot.celetech.mkiii` | CE 主线 PR #4802 未合并；addon 不全跟随 |
| 🟡 等本体 | 鼠族 15 个（本体 `solaris.ratkinracemod`=NewRatkinPlus + `fxz.*` + `rkk.ratknights.core` + `rku.ratkinunderground` + `oark.ratkinfaction.*` 等） | 本体 GitHub release 停 1.6（4 月）；Steam 版 10-14 更新曾在 1.6 存档引发头身分离（已修）。无 1.7 构建确认 |
| 🟠 先禁再逐个试 | 优化/图形类 12 个：`sarg.smartspeed`(+soulwolf zh)、`owlchemist.midsaversaver`(+chinesepackage zh)、`telefonmast.graphicssettings`(+tinygrox zh)、`m00nl1ght.mappreview`(+zh.m00nl1ght zh)、`owlchemist.smartfarming`(+soulwolf zh)、`arandomkiwi.rimsaves`(+rwzh zh) | 改 tick/缓存/渲染 = 引擎迁移重写区 |
| 🟠 先禁用 | `ods.isekairetexture` | 贴图类，UP 主实测「个别贴图 mod 有大问题」 |
| 🟢 可上 | VE 65 + 汉化 101 + Harmony + `iforgotmysocks.caravanadventures` + `mustard1557.mugb.goblin`(+zh) | 400+ mod 实测口径 + MUGB 1.7 构建已开工（10-13）+ CA v1.9.0 已适配 |

---

## 1. 343 个 mod 分类风险总表

| 类别 | 数量 | 1.7 预期 | 依据 |
|---|---|---|---|
| 官方本体 + 5 DLC | 6 | 🟢 | 官方客户端 |
| 汉化包（纯 XML） | 101 | 🟢 | 不碰汇编 |
| Vanilla Expanded 系 | 65 | 🟢 较稳 | 框架仓库活跃 + 400+ 实测 |
| CE 生态 | 8 | 🟡 等 PR #4802 | 同前 |
| 框架库 | 36 | 🟡 分化 | Harmony 已更新；`v1024.ebframework`、`oark.oberoniaaurea.framework`、`lat.rimstro`、`tsa.worlddominationexperimental`、`cyberware.2077` 均**无公开仓库**（GitHub 搜索零结果，Steam/国内渠道独占）→ ⚪ 未核实 |
| 鼠族生态 | 15 | 🟡 等本体 | 本体 release 停 1.6 |
| 其他种族（Kiiro/Yuran/MoeLotl/Prodrake/龙族等） | 8 | ⚪ 未核实 | 无 1.7 证据 |
| 优化/性能类 | 12 | 🟠 高风险 | 同前 |
| 其他 C# mod | 92 | 🟡 需实测 | RimTalk、Storage、监狱、 Hospitality 系等，无 1.7 证据 |

---

## 2. 这份清单的存量问题（1.6 时就存在，建议顺手修）

| 级别 | 问题 |
|---|---|
| 🔴 | `optimizer.zh` 空转（本体缺失，见 §0） |
| 🟠 | **双汉化并存**：`chinesepack.veterano.mythicages.megafaunabestiary` 与 `veterano.mythicages.megafaunabestiary.zhmiz` 翻同一个 mod，互相覆盖，保留一个即可 |
| 🟠 | 7 处加载顺序逆序：`nagisa.orion.hospitality`(#66) 应在 `orion.hospitality`(#203) 后；`seekiworksmod.no16`(#100，Allow Tool 补丁) 应在 `unlimitedhugs.allowtool`(#132) 后；`vanillaexpanded.vfesecurity`(#197) 应在 `vanillaexpanded.vwe`(#228) 后；`shavius.vpsye.zh`(#217) 应在 `vpe.hemosage`(#222)/`vpe.puppeteer`(#223) 后；`chinesepack.veterano.mythicages.megafaunabestiary`(#278) 应在 `veterano...zhmiz`(#279) 后；`zh.mrhydralisk.voeadditionaloutposts`(#309) 应在 `zh.vanillaexpanded.outposts`(#327) 后 |
| 🟡 | `zh.adaptive.storage.neolithic` 部分空转：你装了 ideology/primitive/deepstorage 三个本体，但缺 Neolithic Module / Global Settings / Old Simple Storage |
| 🟡 | `shavius.vie.zh` 对应的 `vanillaexpanded.ideo.sophianstyle` 未装（其余 4 个 VIE 子模组都装了） |

## 3. 上 1.7 操作顺序

1. 备份 `ModsConfig.xml` + `AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\`。
2. Steam → RimWorld 属性 → 测试版 → `unstable`。
3. 先卸/禁 4 个：`nebulae.rimworld`、`optimizer.zh`、`ods.isekairetexture`，加 12 个优化/图形类。
4. CE 8 个先禁（等 PR #4802 + addon 跟进）。
5. 裸客户端 → VE 65 + 汉化 101 + Harmony + Caravan Adventures（先更 v1.9.0）+ MUGB 首批上。
6. 鼠族 15 个：先把本体 NewRatkinPlus 更到最新（修过头身分离 bug 的版本），其余观察；OA 框架系（oark.*）作为未核实项单独一天试。
7. 剩余 92 个 C# mod 分批上，红字二分 + `Player.log`。
8. 回退无痛：存档双向兼容。

## 4. 四份清单横向对比（今日全部查完）

| 清单 | 规模 | 卡点 | 就绪度 |
|---|---|---|---|
| ce0906 科幻 | 336 | CE 2 个 + 优化 7 + Nebulae 1 | 最高 |
| Medieval 中世纪 | 363 | MO 缺位 + CE + 鼠族 | 最低，留守 1.6 |
| war2 战争包 | 227 | CE 4（addon 仓库停更）+ Nebulae 2 | 中 |
| xianlu 仙路 | 343 | CE 8 + 鼠族 15 + Nebulae 1 | 中偏下 |

## 5. 数据来源

官方博客（10-12）；GitHub CE 仓库及 addon 仓库、NewRatkin、MUGB、CaravanAdventures（10-12~10-19 各次实查）；百度贴吧实测（NebulaeFlood、鼠族本体、400+ mod 实测）；RimSort 工坊库（依赖/顺序/空转分析）。**下次复查触发**：PR #4802 合并 / 鼠族本体发 1.7 / NebulaeFlood 更新 / OA 框架发版。
