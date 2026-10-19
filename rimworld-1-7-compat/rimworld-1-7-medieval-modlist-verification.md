# RimWorld 1.7 中世纪清单兼容性核查报告

**核查对象**：`C:\Users\Admin\Documents\Medieval.xml`（ModsConfig，游戏版本 1.6.4871 rev598，启用 363 项）
**核查日期**：2026-10-19
**核查方式**：官方公告 + GitHub 仓库核对 + Steam 工坊页 + 社区实测交叉验证。**未做本机启动实测**（本机未装 RimWorld）。

---

## 0. 结论先行

**这份中世纪清单比科幻清单（ce0906.xml）更难上 1.7**：核心大修 Medieval Overhaul 原作者缺位、CE 未适配、鼠族本体 10-14 更新刚出过回归 bug。建议**这份清单留守 1.6，等两个信号**。

| 动作 | mod | 原因 |
|---|---|---|
| 🔴 上 1.7 前先禁用 | `taranchuk.performanceoptimizer`（+`optimizer.zh`） | 仓库停更于 2026-01；社区实测「优化类应该都有问题」 |
| 🔴 等作者修复 | `nebulae.rimworld` | 社区实测：装上后主界面滚木、ESC 退不出 |
| 🔴 等官方新版 | `ceteam.combatextended` + 7 个 CE 补丁 | CE 7.4（10-15 发布）tag 仍 `v1.6.*`，1.7 版未发 → 整个 CE 生态先留 1.6 |
| 🟠 先禁用再逐个试 | `ods.isekairetexture`、`font.rimesis`、`telefonmast.graphicssettings`、`m00nl1ght.mappreview`、`owlchemist.midsaversaver`、`sarg.smartspeed` | 贴图/字体/图形/性能类，渲染层迁移重灾区 |
| 🟡 最大不确定 | `dankpyon.medieval.overhaul`（中世纪大修全家桶） | 原作者 SirLalaPyon 缺位，页面明示由 EvilEyes/ViralReaction 代管；无公开仓库可验；官方 FAQ 连 CE 兼容都不保证（"Not sure, ask CE"） |
| 🟡 最大不确定 | `athelas.medievaltotalrim.*`（13 个模块） | 公开镜像停在 2026-01，无 1.7 证据 |
| 🟢 已可上 | VE 系列 36 个 + 汉化包 103 个 + `mustard1557.mugb.goblin` | 吧友 10-13 实测「400+ 模组上 1.7 没问题，就一个出问题」；MUGB 作者 10-13 提交「split builds into 1.6 and 1.7 assembly folders」 |

---

## 1. 换个角度：这份清单的 1.7 阻力在哪

| 阻力 | 涉及 mod 数 | 说明 |
|---|---|---|
| **CE 生态** | 8 | CE 本体 + 鼠族 CE 补丁集 + 中世纪要塞 CE 补丁 + Kiiro/Moelotl CE 集成 + DBH 中世纪 CE + MUGB CE 补 + CE 汉化。CE 不出 1.7 版，这一层全动不了 |
| **Medieval Overhaul 大修系** | ~50 | MO 本体 + House Roxmont + QOL fixes + 汉化 + Al9000 系 6 个（fireandsteel/highmedieval/shiningarmor/sengoku/tastysteppe/tastycore）+ Medieval Total Rim 13 个 + 各类城堡/酒馆/药店扩展。全部依赖 MO 的数字/科技树框架 |
| **鼠族生态** | 12 | 本体 NewRatkinPlus + Faction+ + 骑士团 + 地下 + 贴图/命名/武器 addon 群 |
| 其余 C# 功能 mod | ~84 | LOTR 系、魔法系、监狱/医疗/仓储等，无 1.7 证据 |

---

## 2. 逐个核实过的关键 mod（有据可查的）

| mod | 证据 | 日期 | 1.7 状态 |
|---|---|---|---|
| `mustard1557.mugb.goblin` | GitHub commit「split builds into 1.6 and **1.7** assembly folders」 | 2026-10-13 | 🟢 **作者已在做 1.7 构建**， Steam 版更新后即可上 |
| `solaris.ratkinracemod`（=NewRatkinPlus，鼠族本体） | GitHub release 最新为 `1.6`（2026-04-23）；Steam 版 10-14 有更新 | 2026-10-14 | 🟡 活跃维护但无 1.7 构建；**其 10-14 更新在 1.6 存档上引发过鼠鼠头身分离 bug，随后已修复**——更新本体时留意 |
| `rkk.ratknights.core`（鼠族骑士团） | 吧友实测问题根因是「鼠族本体的 BUG」，本体更新后已修复 | 2026-10-15 | 🟢 随本体更新恢复（那个试炼水晶红字是 mod 自身机制问题，非 1.7） |
| `fxz.ratkinfaction`（Ratkin Faction+） | Steam 页：只加敌对派系，兼容 Apparel+/Weapons+/Vehicles+（你都没装） | — | ⚪ 无 1.7 证据 |
| `dankpyon.medieval.overhaul` | Steam 页：原作者缺位，EvilEyes/ViralReaction 代管；FAQ「CE 兼容？Not sure, ask CE」 | 2026-10-19 现状 | 🟡 **无 1.7 证据，中世纪清单的核心风险点** |
| `athelas.medievaltotalrim.core` 等 13 个 | GitHub 镜像最后提交 2026-01-24（且镜像本身不全） | 2026-01-24 | 🟡 无 1.7 证据 |
| `ceteam.combatextended` | release `v1.6.7.4.0` "Waylith Awaits" | 2026-10-15 | 🟡 仍是 1.6 构建，等新版 |
| `brrainz.harmony` | 社区实证：已同步更新 1.7/1.6 | 2026-10-13 | 🟢 已更新（注意：该更新曾把 1.6 的珂莉姆 mod 带炸） |
| `torann.arimworldofmagic` | 仓库在（TorannD/RWoM），未见 1.7 tag | — | ⚪ 无 1.7 证据 |
| `nebulae.rimworld` | 吧友实测：主菜单滚木、ESC 失效 | 2026-10-15 | 🔴 未修复 |
| `taranchuk.performanceoptimizer` | 仓库最后提交 2026-01-12 | 2026-01-12 | 🔴 未适配 |

**通用口径（科学清单同样适用，已核实）**：官方 10-12 公告——绝大多数 mod 无需修改可跑 1.7、存档双向兼容、1.7 仅在 unstable 分支；吧友 10-13 实测「400+ 模组无缝衔接，就一个出问题」。黄警告只是版本号提示。

---

## 3. 这份清单自身的存量问题（1.6 时就存在，与 1.7 无关，建议顺手修）

| 问题 | 详情 |
|---|---|
| 🔴 汉化空转 ×5 | `rwzh.leafzxg.epoeforked`（本体 `vat.epoeforked` 没装）；`spirit.medievalfantasyquestrewards.parta.zht`（本体 `botchjob.medievalfantasythemedrelicquests` 没装——你装的 `botchjob.medievalfantasyrareresources` 是另一个 mod）；`zh.adaptive.storage.neolithic`（一整套 Adaptive 存储本体没装）；`shavius.vve.zh`（缺 VVE Tier3/Upgrades）；`shavius.alphavehicles.zh`（缺 Alpha Vehicles Early Cars） |
| 🟠 加载顺序逆序 ×2 | `nagisa.orion.hospitality`(#55) 应排在 `orion.hospitality`(#181) **之后**；`zh.warlocksforge.fishtraps`(#252) 应排在 `rwzh.chinesepack.vcef`(#273) **之后** |
| 🟡 部分空转 | `shavius.vie.zh` 对应的 5 个 VIE 子模组（viehar/viesas/dryads/relicsandartifacts/sophianstyle）未装 |
| ⚪ 待人工确认 | `qaq.qaaaq` 与 `qa.qqijq` 两个 QaQ 系并存；社区库未收录，需人工确认是不同 mod 还是重复 |

---

## 4. 上 1.7 的操作顺序（如果非要现在上）

1. **备份**：`ModsConfig.xml` + `AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\`（存档）。
2. **切 unstable 分支**：Steam → RimWorld 属性 → 测试版 → unstable。
3. **先裸客户端** → 再上「VE 36 + 汉化 103 + Harmony + MUGB」这一层，吧友已验证 400+ 规模只有个位数问题。
4. **CE 整层先禁用**（8 个），等 CE 发 Waylith 版（tag 不再 v1.6.*）。
5. **MO 大修族最后上且单独一天试**：MO 无公开仓库、无 1.7 证据，是全清单最大不确定项；MO + MTR + Al9000 系建议整体等。
6. **鼠族先更本体到最新**（修过头身分离 bug 的版本）再上；骑士团/地下/贴图 addon 跟随本体。
7. 先禁 7 个高危：`taranchuk.performanceoptimizer`(+`optimizer.zh`)、`nebulae.rimworld`、`ods.isekairetexture`、`font.rimesis`(+`openclaw.translation.rimesis.chinese`)、`telefonmast.graphicssettings`(+`tinygrox.chs.graphicssettings`)、`m00nl1ght.mappreview`(+`zh.m00nl1ght.mappreview`)、`owlchemist.midsaversaver`(+`chinesepackage.owlchemist.midsaversaver`)。
8. 爆红字二分法 + `Player.log`。

**更稳的路线**：这份清单留守 1.6 主分支，等 ①CE 出 Waylith 版 ②MO 代管者发 1.7 更新 ③1.7 上主分支稳定版——三个信号任一明确再迁。存档双向兼容，晚迁没有代价。

---

## 5. 数据来源与时效

| 来源 | 日期 | 用途 |
|---|---|---|
| Ludeon 官方博客 | 2026-10-12 | 1.7 事实卡 |
| GitHub `CombatExtended-Continued/CombatExtended` | 2026-10-15 | CE = v1.6 构建 |
| GitHub `mustard1557/MUGB_Public` | 2026-10-13 | 1.6/1.7 双构建进行中 |
| GitHub `solaris0115/NewRatkin` | 2026-04-23 / Steam 10-14 | 鼠族本体版本线 |
| GitHub `athelas-tr/MedievalKingdoms_Rimworld` | 2026-01-24 | MTR 镜像停滞 |
| Steam 工坊 `Medieval Overhaul`(3219596926) | 2026-10-19 | 原作者缺位、代管声明、CE 兼容 FAQ |
| Steam 工坊 `NewRatkinPlus`(1578693166) | 2026-10-19 | 本体身份 + GitHub 直链 |
| 百度贴吧 rimworld 吧 ×5 | 2026-10-13 ~ 10-18 | 400+ mod 实测、鼠族 bug、NebulaeFlood、优化类 |
| RimSort 工坊数据库 | 2026-10 | 363→名称解析、依赖/顺序分析 |

**下次复查触发**：CE 发 Waylith 版 / MO 代管者发 1.7 更新 / 1.7 上主分支。
