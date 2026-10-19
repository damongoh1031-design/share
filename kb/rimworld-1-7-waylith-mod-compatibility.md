---
id: rimworld-1-7-waylith-mod-compatibility
title: "RimWorld 1.7（Waylith 引擎）Mod 兼容性核查方法与时令结论"
tags: [rimworld, 环世界, 1.7, waylith, mod兼容性, unity迁移, 工坊数据库]
created: 2026-10-19
updated: 2026-10-19
version: 1
status: stable
source: 2026-10-19 会话实测（官方公告 + GitHub API + 贴吧/B站社区实测交叉验证）
confidence: 已核实（官方公告/GitHub 版本）/ 社区实证（贴吧实测）/ 推断（分类风险）
---

# RimWorld 1.7（Waylith 引擎）Mod 兼容性核查

**一句话结论**：RimWorld 1.7 于 2026-10-12 发布（Steam unstable 分支，主分支仍 1.6），官方承诺「绝大多数 mod 一行不改可跑 + 存档双向兼容」；真正会炸的是优化类、贴图/字体类、以及个别等作者修的 C# mod —— 大批黄警告只是版本号问题，不是不兼容。

## 事实卡（2026-10-12 官方公告，已核实）

| 项 | 事实 |
|---|---|
| 引擎 | Unity → 自研 Waylith（底层 BRUTAL 框架开源 + fork .NET 10 + Unity API 兼容壳） |
| 性能 | 官方测试 2–4 倍；后期存档 2.2 倍；1500 mod 包加载 14min→6min |
| 存档 | 双向兼容（1.6↔1.7） |
| Mod | 免改可跑；未更新者仅黄字 "potentially unsupported" |
| 分支 | 仅 unstable 测试分支；主分支 1.6；稳定版无时间表 |
| 硬门槛 | >10 年老 PC 可能跑不动 |

## 分类风险模型（336 mod 实测口径）

| 类别 | 数量 | 风险 | 判据 |
|---|---|---|---|
| DLC/本体 | 6 | 🟢 | 官方客户端 |
| 汉化包（纯 XML） | 108 | 🟢 | DefInjected 不碰汇编，与引擎无关 |
| Vanilla Expanded 系列 | 82 | 🟢 | 框架仓库持续活跃 + 社区实测 OK |
| 框架库 | 35 | 🟡 | 逐个看仓库/release tag |
| 其他 C# mod | 97 | 🟡 | 无人验证，需二分实测 |
| 优化/性能类 | 7 | 🟠 | 改游戏循环/缓存 = 引擎迁移重写区 |
| 贴图/字体类 | 3 | 🟠 | 渲染层更换，UP 主实测「个别贴图 mod 有大问题」 |

## 已核实的个例（截至 2026-10-19）

| mod | 状态 | 证据 |
|---|---|---|
| `ceteam.combatextended` | 🟡 未适配，等新版 | release `v1.6.7.4.0`（2026-10-15）tag 仍 v1.6.*，标题 "Waylith Awaits" |
| `brrainz.harmony` | 🟢 已双版本更新 | 社区实证 2026-10-13；但该更新曾把 1.6 的珂莉姆带炸 —— 框架更新有回归风险 |
| `iforgotmysocks.caravanadventures` | 🟢 已适配 | v1.9.0（2026-10-16）release 写明 compatibility with RimWorld v1.7 |
| `nebulae.rimworld` | 🔴 未修复 | 实测装上后主菜单滚木、ESC 失效 |
| `taranchuk.performanceoptimizer` | 🔴 未适配 | 仓库停更于 2026-01-12 |
| `smashphil.vehicleframework` | 🟢 较稳 | 社区讨论中 SOS2 才需等（VF 本身无事故） |
| Replace Stuff / Mod Manager Continued | ✅ | 实测问题在「原版」和 MM，换 Continued 或未装则无关 |

## 可复用操作

**1. 摸清 336 个 mod 的 1.7 态势（流程）**
```bash
# 1) packageId → 名称/依赖（RimSort 工坊库，约 49MB）
python ~/.workbuddy-ai/skills/rimworld-modlist-audit/scripts/resolve_modlist.py <ModsConfig.xml>
# 2) 分类：zh 前缀/.zh = 汉化包；oskarpotocki./vanillaexpanded./vanillaracesexpanded./vanillaquestsexpanded. = VE 系
# 3) 逐个核实只做两类：框架库查 GitHub release tag；社区实测查贴吧/B站关键词「1.7 不兼容」
# 4) 对单个仓库：https://api.github.com/repos/<owner>/<repo>/releases?per_page=3
```

**2. RimSort 工坊库 `gameVersions` 字段不能当 1.7 判据**
汉化包普遍把 supportedVersions 写成 1.0–1.9 全量规避警告，DB 命中「1.7」≠ 作者适配过。1.7 判据优先级：**release tag/changelog > commit message > 社区实测 > gameVersions 字段**。

**3. 上 1.7 顺序**：备份 ModsConfig.xml + 存档目录 → unstable 分支 → 先纯框架+VE+汉化 → 禁 8 个高危（performanceoptimizer、nebulae、isekairetexture、font.rimesis、graphicssettings、mappreview、midsaversaver、smartspeed）→ CE 等 Waylith 版 → 红字二分法 + Player.log。

## 坑与反直觉

1. **黄字 ≠ 不兼容**。1.7 下满屏黄警告是官方设计的版本号提示，别慌着回退。
2. **框架更新会制造新事故**：harmony 同步更 1.6/1.7 时把 1.6 的珂莉姆 mod 带炸 —— 大版本切换期「不动」也是一种策略。
3. **优化 mod 是重灾区**：社区原话「优化类的应该都有问题」。它们改的恰是引擎迁移重写的区域（缓存/循环/IO）。
4. **1.7 目前 = 测试版**：官方主分支仍是 1.6，存档双向兼容让回退无痛，但 mod 数据可能只在单版本验证过。
5. **CE 这类大修要等 tag**：看 release tag 是不是还叫 `v1.6.*`，"Waylith Awaits" 这种标题只是愿景不是适配。

## 未核实 / 存疑

- 336 个 mod 中约 200 个 C# mod 无公开 1.7 证据（理论上「绝大多数免改」，未实测）。
- 1.7 稳定版上线时间、Steam Workshop 在 1.7 的行为、HugsLib 官方仓库未找到（404，未核其实时适配状态）。
- RimTalk（`cj.rimtalk` 系）在 1.7 的表现未检索到任何信息。
- 本报告未做本机启动实测；结论以上线源为凭，游玩前仍需自测。
