# RimWorld 1.7 战争整合包（war2.xml）兼容性核查报告

**核查对象**：`C:\Users\Admin\Documents\war2.xml`（ModsConfig，游戏版本 1.6.4871 rev598，启用 227 项）
**核查日期**：2026-10-19
**核查方式**：官方公告 + GitHub 仓库核对 + Steam 工坊依赖关系 + 社区实测交叉验证。**未做本机启动实测**（本机未装 RimWorld）。

---

## 0. 结论先行

**结构判断：这是三份清单里 CE 浓度最高的战争包。非 CE 部分（~190 个）随时可上 1.7，CE 部分（4 个）等 PR #4802 合并。先处理 2 个 Nebulae 和 8 个优化类。**

| 动作 | mod | 原因 |
|---|---|---|
| 🔴 上 1.7 前先禁用 | `nebulae.rimworld`（NebulaeFlood's Lib） | 社区实测 10-15：装上后主界面进功能页滚木、ESC 失效，只能回退 1.6。**本清单自己装着它**（第 58 行） |
| 🔴 连带禁用 | `nebulae.simplymoreroofs` | RimSort 库依赖关系证实：`Simply More Roofs` **硬依赖 NebulaeFlood's Lib**（deps=nebulae.rimworld）→ 本体炸它跟着炸 |
| 🔴 先禁用 | `taranchuk.performanceoptimizer`（+`optimizer.zh`） | 仓库停更 2026-01；社区实测「优化类应该都有问题」 |
| 🟠 先禁用再逐个试 | `blue.adaptivetps`、`arkymn.slowerpawntickrate`、`owlchemist.midsaversaver`(+zh)、`telefonmast.graphicssettings`(+tinygrox zh)、`sarg.smartspeed`(+soulwolf zh)、`owlchemist.smartfarming`(+soulwolf zh)、`arandomkiwi.rimsaves`(+zh) | 8 个优化/性能类全中招重灾区（改 tick/缓存/渲染，正是引擎迁移重写区） |
| 🟠 先禁用 | `ods.isekairetexture` | 贴图类，UP 主实测「个别贴图 mod 有大问题」 |
| 🟡 等 CE | `ceteam.combatextended`、`ceteam.combatextendedarmors`、`ceteam.combatextendedattachments`、`lemontea.combatextendedzh` | 见 §2，CE 主线 1.7 适配在途但未合并，**两个官方 addon 仓库已停更** |
| 🟢 可上 | Ve 55 + 汉化 82 + Harmony + `iforgotmysocks.caravanadventures` | 吧友 10-13 实测 400+ mod 无缝；Caravan Adventures v1.9.0 已适配 |

---

## 1. 227 个 mod 分类风险总表

| 类别 | 数量 | 1.7 预期 | 依据 |
|---|---|---|---|
| 官方本体 + 5 DLC | 6 | 🟢 | 官方客户端 |
| 汉化包（纯 XML） | 82 | 🟢 | 不碰汇编 |
| Vanilla Expanded 系 | 55 | 🟢 较稳 | 框架仓库 10-17/18 活跃 + 400+ 实测 |
| CE 生态 | 4 | 🟡 等 CE | §2 |
| 框架库 | 22 | 🟡 | Harmony 已更新；Nebulae 2 个见 🔴 |
| 优化/性能类 | 8 | 🟠 高风险 | §0 |
| 贴图类 | 1 | 🟠 | ods.isekairetexture |
| 其他 C# mod | 49 | 🟡 需实测 | RimTalk、RimJob World、mx.shield、ctrlf、poupun、zruic 等，无 1.7 证据 |

---

## 2. CE 生态核查（本清单特有重点，2026-10-19 实查）

| 组件 | 证据 | 状态 |
|---|---|---|
| `ceteam.combatextended` 本体 | `1.7-Test` 分支 10-12 首提交；PR #4802 仍 Open、CI unstable、0 review；正式版 tag 仍 `v1.6.7.4.0` | 🟡 适配在途，未发布 |
| `ceteam.combatextendedarmors` | GitHub `CombatExtended-Continued/CombatExtendedArmors` 最后 push **2026-08-14** | 🔴 仓库停更，无 1.7 动静 |
| `ceteam.combatextendedattachments` | GitHub `CombatExtended-Continued/CombatExtendedAttachments` 最后 push **2025-09-10** | 🔴 停更快一年，无 1.7 动静 |
| `lemontea.combatextendedzh` | CE 汉化，随 CE 本体 | 🟡 |

**含义**：即便 CE 本体明天合了 PR #4802，Armors/Attachments 两个官方 addon 也大概率不能同步上 1.7——**这个战争包整体迁 1.7 的瓶颈是 CE 全家桶，不是其他任何东西**。盯 PR #4802 合并 + Armors/Attachments 仓库恢复 push。

---

## 3. Nebulae 链（本清单第二硬伤）

- `nebulae.rimworld`（NebulaeFlood's Lib）：10-15 吧友实测——装上后主界面能显示按钮，点进去就滚木、ESC 都退不出、只能回退 1.6。**未修复**。
- `nebulae.simplymoreroofs`：RimSort 依赖库证实 deps=`nebulae.rimworld` → 主库崩，它必崩。
- 处理：这两个一起禁，等作者修 Lib。

## 4. 上 1.7 操作顺序

1. 备份 `ModsConfig.xml` + `AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\`。
2. Steam → RimWorld 属性 → 测试版 → `unstable`。
3. 先禁 11 个：2 Nebulae + performanceoptimizer(+optimizer.zh) + adaptivetps + slowerpawntickrate + midsaversaver(+zh) + graphicssettings(+tinygrox zh) + smartspeed(+soulwolf zh) + smartfarming(+soulwolf zh) + rimsaves(+zh) + isekairetexture。
4. CE 4 个也先禁（Armors/Attachments 仓库停更，抢跑无意义）。
5. 裸客户端 → VE 55 + 汉化 82 + Harmony + Caravan Adventures（先更到 v1.9.0）首批上。
6. 剩余 49 个 C# mod 每 5-6 个一批上，爆红字二分 + `Player.log`。
7. 回退无痛：存档双向兼容。

## 5. 存量问题（1.6 时就存在）

| 问题 | 详情 |
|---|---|
| 🔴 汉化空转 | `rwzh.leafzxg.epoeforked`（本体 `vat.epoeforked` 没装）；`zh.adaptive.storage.neolithic`（整套 Adaptive 存储本体没装） |
| 🟡 部分空转 | `rwzh.chinesepack.vfe` 覆盖 15 个 VFE 模块，你装了大部分但缺 `vfesecurity`/`vfefactory`（无害，仅这两模块无汉化） |
| 🟡 顺序逆序 | `zh.mzmgow.sbz.gravshipstorage`(#120) 排在 `zh.adaptive.storage.neolithic`(#122) 前；`shavius.vpsye.zh`(#184) 应排在 `vanillaexpanded.vpe.hemosage`(#185) 后 |

## 6. 数据来源

| 来源 | 日期 |
|---|---|
| Ludeon 官方博客 | 2026-10-12 |
| GitHub `CombatExtended-Continued/CombatExtended`（1.7-Test 分支/PR #4802） | 2026-10-12 ~ 10-19 |
| GitHub `CombatExtendedArmors` / `CombatExtendedAttachments`（push 时间） | 2026-08-14 / 2025-09-10 |
| GitHub `iforgotmysocks/CaravanAdventures`（v1.9.0） | 2026-10-16 |
| 百度贴吧 rimworld 吧（NebulaeFlood 实测、400+ mod 实测） | 2026-10-13 ~ 10-15 |
| RimSort 工坊库（依赖关系：Simply More Roofs → NebulaeFlood's Lib） | 2026-10 |

**下次复查触发**：PR #4802 合并 / CE Armors·Attachments 恢复 push / NebulaeFlood 更新。
