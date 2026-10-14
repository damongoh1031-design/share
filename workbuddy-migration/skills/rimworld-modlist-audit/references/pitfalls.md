# 踩坑清单（已验证）

## 一、RimSort 社区工坊数据库

### 1. `dependencies` 字段存的是**工坊 ID**，不是 packageId
最致命的坑。直接拿 `dependencies` 里的值和已装 packageId 比对，会把
「VEF 已装（packageId = `oskarpotocki.vanillafactionsexpanded.core`）」
误报成「缺 2023507013」。

✅ 必须先建 `workshopId → packageId` 映射再判断。

### 2. 同一 packageId 对应**多个工坊条目**
例：`ceteam.combatextended` 同时存在
- `3620445246` = Combat Extended（gameVersions = `["1.5"]`）
- `2890901044` = Combat Extended（gameVersions = `["1.6"]`）

若不按 `gameVersions` 优先取 1.6，报告里会写出「CE 是 1.5 版」这种错误结论。
**在 1.6 游戏上装 1.5 版 CE 是严重问题** —— 必须区分清楚。

### 3. 覆盖率约 70%
230/336。未收录的**绝大多数是汉化包**（`zh.*` / `rwzh.*` / `shavius.*` / `zh.mzmgow.*`）。
另外有些条目存在但 `name` 为空字符串 —— 也算「未解析」，需用工坊检索兜底。

### 4. `dependencies` 混入了 `loadAfter`
社区库把 `About.xml` 的 `modDependencies` 与 `loadAfter` 合并了。
→ 「缺 X」大多只是 **loadAfter 落空，无害**。
→ 要判断**真·硬依赖缺失**，必须读源码 `About/About.xml` 的 `<modDependencies>`。

---

## 二、Combat Extended

### 5. **不在官方支持清单 ≠ 不兼容**
最容易被误判的一条。很多模组自带 CE 补丁，例如 AobaKuma 全系列：
`LoadFolders.xml` 里 `IfModActive="CETeam.CombatExtended,CETeam.CombatExtended_steam"`
→ 条件加载 `1.6/CE/` 目录（含 Defs + Patches + Languages）。
CE 官方 `SupportedThirdPartyMods.md` 里根本没有这些名字。

✅ 对战斗类模组，**必须下载源码看有没有自带补丁**，不能只看清单。

### 6. CE 补丁目录名**不统一**
- `Dead-Man-Switch/1.6/CE/`
- `Fortification-Industrial/1.6/CombatExtended/`（不是 `CE`！）
- `Fortification-Industrial/1.6/Vanilla/`（`IfModNotActive` → 无 CE 时的降级版）

✅ 检查脚本要同时匹配 `CE` 与 `CombatExtended`，否则会把「有补丁」误判成「无补丁」。

### 7. CE 有 1.5 / 1.6 两条工坊条目
见坑 2。另外 CE 的 `About.xml` 里 `<supportedVersions>` 与 `<modVersion>`
（如 `16.7.3.0`）是版本结论的权威来源。

### 8. 补丁应用顺序的准确表述
RimWorld 官方 Wiki（`Modding_Tutorials/PatchOperations`）原文：
> "Patching is run after all XML Defs are loaded into memory and **in mod list order**."

→ 全部 Def 先加载，再按**模组列表顺序**应用补丁。
→ 所以「补丁模组要排在被补丁模组之后」本质是**优先级/覆盖**问题，**不是** def 不存在的问题。
→ 一个排在后面的模组，其自身补丁会**覆盖**前面模组（含 CE）对同一节点的修改。

**推论（易说错）**：CE 的集成补丁目标（如 VFE Security）即使排在 CE 之后，
补丁**仍然生效**（def 都在内存里）。风险只在于目标模组自身也补丁同一节点时会盖掉 CE 的数值。

---

## 三、Steam 工坊抓取

### 9. browse 页内嵌 JSON 的键**被转义**
实际是 `\"publishedfileid\":\"...\"`，直接按 `"publishedfileid"` 正则会 0 命中。

✅ `html = html.replace('\\"', '"')` 之后再正则。

### 10. 抓取用 curl 可行，但要带 UA
```bash
curl -sL --max-time 40 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \
  "https://steamcommunity.com/workshop/browse/?appid=294100&searchtext=<kw>&browsesort=textsearch&section=readytouseitems"
```
可拿到 `publishedfileid` / `title` / `short_description` / `subscriptions` / `tags`。

### 11. 单条目页的 **Required items（必需项）** 能区分「汉化包」与「完整转载」
`sharedfiles/filedetails/?id=<id>` 的 "Required items" 若指向原模组 → 是汉化包（正常配对）；
若不指向任何原模组且自带完整 Defs → 可能是**重复转载**（会冲突）。

### 12. 汉化包的 packageId 命名毫无规律
`cy.nicehealthtab`、`seekiworksmod.no16`、`zh.mzmgow.*`、`rwzh.chinesepack.*`、`shavius.*.zh`
—— 前缀是作者/汉化组代号，**无法从 packageId 推断它汉化的是哪个模组**。
✅ 只能靠工坊检索 + 条目页的必需项反查。

---

## 四、Windows 沙箱环境

### 13. Python 读 `/tmp/xxx` 会解析成 `C:\tmp\xxx`
Git Bash 的 `/tmp` 实为 `C:\Users\Admin\AppData\Local\Temp`。
**跨工具读写同一文件时一律用真实 Windows 路径**：
`C:/Users/Admin/AppData/Local/Temp/...`。

### 14. 大文件下载用 curl 到 `/tmp` 可行
`curl -sL --max-time 300 "<url>" -o steamDB.json`（49MB 没问题）。
但**不要**用 curl 写含中文/空格的 Windows 路径。

---

## 五、GitHub 源码抓取（派系/事件核查专用）

### 15. ⚠️ 仓库名对得上 ≠ 是同一个模组，且**仓库常年滞后于 Steam**
最坑的一条。VFE 系列多个模组的 GitHub 仓库停在旧版本，且**同名仓库可能是另一个模组**：

| 想要的模组 | ❌ 陷阱仓库 | ✅ 正确仓库 |
|---|---|---|
| VFE Medieval **2** | `VanillaFactionsExpanded-Medieval`（只到 **1.4**，其实是 Medieval **1**） | `VanillaFactionsExpanded-Medieval2`（**1.6**） |
| VFE Insectoids **2** | `VanillaFactionsExpanded-Insectoids`（只到 **1.4**） | `VanillaFactionsExpanded-Insectoids2`（**1.6**） |
| Medieval Overhaul | `SirLalaPyon/MedievalOverhaul` 只到 **1.5**，Steam 已 1.6，**无镜像** | 只能用 1.5 并在报告标 ⚠️ |

✅ **扫描前必须先列仓库顶层目录**（`tarfile` 遍历取 `m.name.split('/')[1]`），确认 `1.6/` 存在。
若不存在 → 用 GitHub search 找 `-2` 后缀 / fork；仍找不到 → 报告里标「源码版本滞后」，不要默认数据准确。

### 16. 版本目录过滤必须**退化到最高可用版本**，不能全保留
早期实现「有 1.6 才过滤，没有就全保留」→ 把 1.2/1.3/1.4 三个目录的定义**全部算进去重复计数**。
✅ 正确逻辑：`1.6` 在 → 只留 `1.6/` + 无版本目录；`1.6` 不在 → **取最高可用版本**（`max` 后按数值元组排序）。

### 17. 模组仓库的 `Defs/` 可能不在顶层
- 多数：`<repo>/1.6/Defs/...`
- VFE Medieval 2：`<repo>/1.6/Defs/...`（正常）
- MUGB：`<repo>/Defs/...`（**无版本目录**，单版本仓库）
- Medieval Kingdoms：`<repo>/MedievalKingdoms_Byzantium/1.6/Defs/...`（**模块名在版本号之前**）
✅ 版本判定要扫**所有路径段**（`{s for s in rel.split('/') if re.match(r'^\d+\.\d+$', s)}`），不能只看第一段。

### 18. "自定义事件分类"要连 comp 一起查，否则会误判为活事件
`IncidentDef.category` 是自定义的（不在原版 Misc/ThreatBig/… 里）时，必须再搜有没有
`StorytellerCompProperties_*` 引用它。
- 有 comp → 事件真的会被抽到（MUGB `MUGB_GoblinCaravanAmbush`）
- 无 comp 且 `baseChance 0` → **死事件**，叙述者永远不会选它（VGE `GR_HybridRaid`）

### 19. 机制的铁证在 C# 补丁里，不在 XML
`FactionDef` 的 XML 只能看出"派系长什么样"，看不出"派系怎么运作"。
必须解包后 grep `.cs`：
- `MerchantGuild.cs` 继承 `MovingBase` → 会移动的定居点
- `Dialog_Barter.cs` + `[HarmonyPatch(typeof(TradeDeal), "CurrencyTradeable")]` → 禁用货币
- `GenStep_WildMen.cs` 里的 `SetRelationDirect(..., Hostile, false)` → 强制敌对
✅ 抓取时同时收集 `.cs` 文件名清单，再对关键文件逐个读。

### 20. 统计派系时**玩家派系要单独算**
`isPlayer=true` 的派系是**开局剧本**，不是可外交的 NPC。
混在一起算会得出"A 侧有 14 个派系"这种误导结论（实际 NPC 派系只有 7 个）。

---

## 六、事件清点专用（2026-10-09 新增）

### 21. ❌ 用正则从 `About.xml` 抓 `<packageId>` 会命中**依赖 id**

`About.xml` 的结构是 `<ModMetaData>` 里既有根节点的 `<packageId>`，
也有 `<modDependencies>` / `<loadAfter>` 里的一堆 `<packageId>`。
正则取第一个匹配，实测把 `VanillaRanchingExpanded` 映射成了 `brrainz.harmony`、
把 `VanillaPsycastsExpanded-Puppeteer` 映射成了 `ludeon.rimworld.royalty`。

✅ 必须 **XML 解析**（`ET.fromstring` 后 `root.findtext('packageId')`），只取根节点子元素。
✅ 批量建映射用 `scripts/build_ve_repo_map.py <org> <out.json>`（16 线程，125 个仓库约 10 秒）。

### 22. ⚠️ `RimWorld-zh/RimWorld-Core` 是 **1.0 时代镜像**，不能当 1.6 基线

该仓库 `Version.txt` = `0.19.2009 rev486`（B19 / 1.0），`IncidentDef` 只有 **63** 个。

**影响范围**：
- 「模组新增了多少事件」**不受影响** —— 模组不会重定义原版 `defName`，差集是空操作。
- 「workerClass 是原版还是自定义」**会错** —— 1.1~1.6 新增的原版 worker
  （`IncidentWorker_GiveQuest` / `_Eclipse` / `_SolarFlare` / `_MechCluster` /
  `_ShuttleCrash` / `_DefoliatorShipPartCrash` / `_Disease_*` / Anomaly 全系列）都不在 B19 列表里，
  会被误判成"自定义"。

✅ 判定 worker 归属请用 `Chillu1/RimWorldDecompiled`（1.6 反编译）里的 `IncidentWorker_*` 类名做基线。

### 23. ⚠️ `parms.forced = true` 的计数**会被 debug 菜单严重污染**

模组作者常写这样的调试工具：

```csharp
options.Add(new DebugMenuOption(points + " points", DebugMenuOptionMode.Action, delegate
{
    IncidentParms parms = StorytellerUtility.DefaultParmsNow(...);
    parms.forced = true;                       // ← 会被 grep 命中
    parms.raidStrategy = MUGBDefOf.MUGB_GoblinMortarTunnelSiege;
    ...
}));
Find.WindowStack.Add(new Dialog_DebugOptionListLister(options));
```

**实测**：MUGB 全仓 8 处 `parms.forced = true`，其中 **7 处在 `MGBMod.cs` 的 debug 菜单里**，
只有 1 处（`MGBGoblinBeacon.QueueIncident`）是真正的玩法路径。
直接报「B 侧用 forced 8 次」会得出完全错误的结论。

✅ 逐条看上下文再定性。判据：**往前 25 行内出现 `DebugMenuOption` / `Dialog_DebugOptionList` 即为 debug**。
✅ 报告里把「玩法路径」和「debug 工具」分开列。

### 24. ⚠️ 统计结构数要**按仓库去重**，不是按 packageId

汉化包和多模块模组会把数字虚高：
- `mustard1557.mugb.goblin` 与 `mustard1557.mugb.goblin.zh` 指向同一仓库 → StorytellerComp 被算两遍
- `athelas.medievaltotalrim.*` 13 个模块共用 `athelas-tr/MedievalKingdoms_Rimworld` → 全仓被扫 13 遍

**实测差异**：B 侧 StorytellerComp 按 packageId 数是 62，按仓库去重后是 **47**。

✅ 用 `repo` 字段做去重键（`IncidentDef` 本身按 `defName` 去重就够了，因为 defName 全局唯一）。

### 25. ⚠️ 版本过滤会**静默丢掉整个模块**

`athelas.medievaltotalrim.events`（MTR Events）在仓库里 1.6 目录下 **0 个 `IncidentDef`**，
版本过滤把 1.5 的内容滤掉后就什么都剩不下 —— 结果看起来像"这个模组没有事件"，
但真相可能是"1.6 目录里确实没有，事件只在 1.5 目录"。

✅ 扫描结果里必须记录并输出 `version_used`，报告里对降级/过滤过的仓库打 ⚠️ 标注。
✅ 对"结果异常为 0"的仓库，回头确认它到底有哪些版本目录（`tarfile` 列顶层目录）。

### 26. ⚠️ 仓库名猜错会**静默漏掉整个模组**

实测踩坑：`TorannD/ARimWorldOfMagic`（猜的）→ 404；真实仓库是 **`TorannD/RWoM`**。
`DankPyon/MedievalOverhaul` / `Medieval-Overhaul/MedievalOverhaul` → 404；
真实仓库是 **`SirLalaPyon/MedievalOverhaul`**（另有一批可用 fork，如 `RanMd/MedievalOverhaul`）。
ARWoM 一个模组就有 **10 个事件**，漏掉直接让 B 侧总数少两成。

✅ 每个模组至少试 2~3 个候选名，并用 `raw.githubusercontent.com/<repo>/<branch>/About/About.xml`
   验证 `packageId` **与清单里的一致**（同名补丁模组很多，`MedievalOverhaulGoldCoinsPatch` 之类会误导）。
✅ 找不到时先查 `references/pitfalls.md` 和 `SKILL.md` 里「已验证的线上源码来源」表，别重复试错。

---

## 七、常见误报清单（报告里别写错）

| 现象 | 真相 |
|---|---|
| 「缺前置 2023507013」 | 工坊 ID 未映射，VEF 其实已装 |
| 「XX 不在 CE 支持清单 → 不兼容」 | 作者可能自带补丁，需源码确认 |
| 「汉化包缺前置模组」 | 多为 `loadAfter` 落空，无害 |
| 「Mines 2.0 和 Mines 2.0-汉化 是重复」 | 是原作 + 汉化，正常配对 |
| 「CE 排在 VFE Security 之前 → 补丁失效」 | Def 全先加载，补丁仍生效，只是优先级问题 |
| 「Graze up 与 Grazing Area 重复」 | 机制不同（不摧毁植物 vs 放牧区域），互补 |
| 「累计订阅数 = 近期热度」 | 两个不同指标，不可混用 |
