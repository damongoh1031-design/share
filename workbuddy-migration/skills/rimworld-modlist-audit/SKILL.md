---
name: rimworld-modlist-audit
description: 对 RimWorld（环世界）ModsConfig.xml 模组清单做兼容性/性能/重复/依赖审计，以及两份清单的差异对比、事件（Incident）与派系（Faction）机制核查与清点。当用户上传 ModsConfig.xml 或 modlist，或问「这些模组会不会冲突」「帮我查兼容」「有没有重复的模组」「XX 和 CE 兼容吗」「加载顺序对不对」「哪些模组缺前置」「比较两个模组列表的差异」「事件触发是不是绑死在叙述者/剧本上」「这份清单加了多少个非原版事件」「各派系有没有独特事件/独特机制/怎么和玩家互动」「这个派系能外交吗/能贸易吗」时使用。覆盖：packageId→模组名解析、同名重复检测、依赖缺失与加载顺序逆序检测、两清单 diff（按事件/武器/种族/派系/科技等维度）、汉化包空转检测、事件触发四路径（叙述者/剧本/任务/代码）源码核实与事件清点、派系三维修查（独特事件 / 独特机制 / 与玩家交流）、Combat Extended 官方支持清单与硬黑名单比对、CE 补丁源码级验证、Steam 工坊实时检索。
agent_created: true
---

# RimWorld 模组清单审计

## 为什么需要

RimWorld 玩家常见 300+ 模组清单，冲突表现为「启动红字 / 存档损坏 / 数值不对 / 卡顿」，
但根因分散在：缺失前置、加载顺序逆序、同名重复、框架硬不兼容、大型 overhaul（尤其 Combat Extended）无补丁。
人工核对 300 个 packageId 不可行，必须用**数据库解析 + 官方清单比对 + 源码验证**三层证据。

## 何时使用

- 用户给出 `ModsConfig.xml`（路径或内容），或贴出一长串 packageId
- 用户问某两个模组是否兼容、某模组是否有 CE 补丁、加载顺序是否正确、是否有重复
- 用户说「游戏报红字」「存档打不开」「装了某模组后卡顿」且清单很长

## 第 0 步：先确认环境（不要跳过）

从 `ModsConfig.xml` 读出并明确写出：

- `<version>` → 游戏版本（如 `1.6.4871 rev598`）。**这是所有兼容结论的前提**，1.5 与 1.6 的模组支持完全不同
- `<activeMods>` → 启用模组数（注意：DLC 会在 `<knownExpansions>` 重复登记，去重）
- `<knownExpansions>` → 已购 DLC（Royalty/Ideology/Biotech/Anomaly/Odyssey）。DLC 是硬门槛，缺 DLC 的模组会报错
- **列表顺序 = 加载顺序**，位置序号在后续判断逆序时要用

⚠️ 先检查本机是否装了 RimWorld / Steam（`ls` 各盘 `steamapps/common/RimWorld`、`AppData/LocalLow/Ludeon Studios`）。
**没装是常态** —— 此时全部走线上核证，并在报告里明确标注「未做实际启动/红字/存档实测」。

## 核心流程

### 1. 解析 packageId → 模组名（关键基础设施）

用 **RimSort Steam Workshop Database**（社区维护，含 packageId/name/authors/dependencies/gameVersions）：

```
https://raw.githubusercontent.com/RimSort/Steam-Workshop-Database/main/steamDB.json
```

约 49 MB / 5.7 万条。结构：

```json
{"version": ..., "database": {"<workshopId>": {"packageId":"...", "name":"...",
  "authors":"...", "dependencies":[...], "gameVersions":[...], "tags":[...]}}}
```

直接跑 `scripts/resolve_modlist.py`（改脚本顶部的 XML 路径即可），它会输出：
命中清单、**同名重复**、**依赖缺失**、**加载顺序逆序**、未解析条目。

**三个必踩的坑（详见 `references/pitfalls.md`）**：
1. `dependencies` 字段存的是**工坊 ID**，不是 packageId → 必须先建 `workshopId → packageId` 映射，否则会把「VEF 已装」误报成「缺 2023507013」
2. 同一 packageId 可能有**多个工坊条目**（如 CE 有 1.5 / 1.6 两条）→ 按 `gameVersions` 优先取 1.6
3. 覆盖率约 70%（230/336）。**未收录的绝大多数是汉化包**（`zh.*` / `rwzh.*` / `shavius.*`），不是异常

### 2. 同名重复 vs 功能重叠

- **同名完全重复**（两个 packageId 同名）→ 高置信度问题
- 但先排除 **「原作 + 汉化」** 组合（如 `cain.mineshaft`=Mines 2.0 与 `noflag.mines2.0`=Mines 2.0-汉化，是配对的）
- **功能重叠**（不同名但做同一件事）→ 不是 bug，但要列出并标注实测风险

### 3. Combat Extended 比对（用户最常问）

抓 CE 官方仓库 `Development` 分支两个文件：

```
https://raw.githubusercontent.com/CombatExtended-Continued/CombatExtended/Development/About/About.xml
https://raw.githubusercontent.com/CombatExtended-Continued/CombatExtended/Development/SupportedThirdPartyMods.md
```

- `About.xml` 的 `<incompatibleWith>` = **硬黑名单**，命中即明确不兼容（高价值结论）
- `<loadBefore>` / `<loadAfter>` = 加载顺序约束，逐条对照清单里的位置序号
- `SupportedThirdPartyMods.md` ≈ 700 条支持清单，与已装模组名做归一化匹配（去空格/符号/大小写）

**关键认知**：**不在官方清单 ≠ 不兼容**。很多模组（尤其 AobaKuma 系）**自带 CE 补丁**，
通过 `LoadFolders.xml` 的 `IfModActive="CETeam.CombatExtended"` 条件加载自己的补丁目录。
必须下载源码确认，不能只看清单。

### 4. 源码级 CE 补丁验证

对可疑模组浅克隆源码后检查：

```bash
git clone --depth 1 https://github.com/<owner>/<repo>.git
# CE 补丁目录名不统一！
ls */1.6/CE */1.6/CombatExtended */1.6/CE/Patches
cat LoadFolders.xml    # 看 IfModActive / IfModNotActive 条件
```

⚠️ **只查 `1.6/CE` 会误判**：`Fortification-Industrial` 用的是 `1.6/CombatExtended/`。
且 `IfModNotActive="CETeam.CombatExtended"` → `1.6/Vanilla` 是「无 CE 时的降级版」，说明作者做了双向适配。

同时读 `About/About.xml` 的 `modDependencies`（硬依赖，缺了会报错）与 `loadAfter`（软排序，缺了无害）。
**这个区分非常重要** —— 把 `loadAfter` 落空报成「缺前置」是典型误报。

### 5. Steam 工坊实时检索（补数据库盲区）

汉化包和很新的模组不在数据库里，用工坊 browse 页兜底：

```
https://steamcommunity.com/workshop/browse/?appid=294100&searchtext=<关键词>&browsesort=textsearch&section=readytouseitems
```

页面内嵌 JSON，但**键被转义为 `\"`** → 必须先 `html.replace('\\"','"')` 再正则。
可拿到：`publishedfileid` / `title` / `short_description` / `subscriptions` / `tags`。
单条目页 `sharedfiles/filedetails/?id=<id>` 可读 **Required items（必需项）**，用来判定「是汉化包还是完整转载」。

## 两清单对比（diff）

用户给出**两份** `ModsConfig.xml`（或问「比较两个模组列表的差异」）时，先跑
`scripts/diff_modlists.py <A.xml> <B.xml>`，它输出：画像（版本/DLC/交集/独有）、仅 A / 仅 B 的条目（带模组名）、汉化包空转检测。

然后按**用户点名的维度**归类差异（事件 / 武器 / 种族 / 派系 / 科技 / 载具 / 存储 / 建筑…）。
归类靠 packageId 词根 + 社区库 `name`，不要凭记忆猜：

| packageId 词根 | 实际归属 | 易错点 |
|---|---|---|
| `oskarpotocki.vanillafactionsexpanded.core` | **Vanilla Expanded Framework（框架本体）** | 名字像「派系核心」，其实是 VE 框架；两边通常都有，不算内容差异 |
| `vanillaexpanded.vfecore` / `.vfearchitect` / `.vfeart` / `.vfefactory` / `vfe*` | **Vanilla Furniture Expanded**（家具） | 与 `oskarpotocki.vfe.*`（Vanilla **Factions** Expanded）是两套东西 |
| `oskarpotocki.vfe.empire/pirates/deserters/insectoid2` | Vanilla **Factions** Expanded 内容包 | 中世纪向清单会换成 `oskarpotocki.vfe.medieval2/tribals` |
| `vanillaexpanded.viehar` | VIE - **Hats and Rags** | 不要猜成 "Holidays and Rituals" |
| `vanillaexpanded.vwebf` | VWE - **Bioferrite** | — |
| `aoba.framework` | **Fortified Features Framework**；`aoba.fortress.*` = Fortifications 系列 | — |
| `van.dacrypts` / `van.datools` | **Dark Ages** 系列（Crypts and Tombs / Medieval Tools） | — |
| `solaris.furniturebase` | GloomyFurniture | 靠 `rwzh.chinesepack.furniturebase`（=GloomyFurniture zh-pack）反推 |

**两条清单常常是「同一底座 + 不同内容层」**：先算交集，把交集写成「共同底座」（框架/QoL/共享种族），
差异才按维度列。这样结论才对得上「为什么是两份而不是一份」。

**汉化包空转**：某清单里装了汉化但没装本体（本体只在另一份里）→ 汉化空转，不报错但无效果。
`diff_modlists.py` 会做启发式检测，但部分「汉化」实为「本体+汉化」合并包，**必须人工确认**。

⚠️ **不要混装两边的科技层**（如 World Tech Level 与高科技内容扩展）—— 属推断，需实测。

## 事件（Incident）触发机制与清点

用户问「事件是怎么触发的 / 事件是不是绑死在叙述者上 / 这份清单加了多少个事件」时用。
**必须查源码，不能凭印象**（这是本 skill 里最容易出错的部分）。

### 四条触发路径（源码已核实，RimWorld 1.6）

| 路径 | 关键源码 | 经过叙述者 |
|---|---|---|
| ① 叙述者按 **category** 抽 | `StorytellerComp_CategoryMTB.MakeIntervalIncidents` → `UsableIncidentsInCategory(Props.category, …)` | 是 |
| ② 叙述者按 **defName** 显式发 | `StorytellerComp_FactionInteraction` / `_Triggered` 的 `Props.incident` | 是 |
| ③ **剧本**定时强制/禁用 | `ScenPart_CreateIncident`（`intervalDays/minDays/maxDays/repeat`）、`ScenPart_DisableIncident` | 否，绕过 |
| ④ **任务**强制触发 | `QuestNode_Incident` / `QuestNode_CreateIncidents` → `QuestPart_Incident`，`incidentParms.forced = true` | 否，绕过 |

**核心机制**：`StorytellerComp.UsableIncidentsInCategory` 是

```csharp
return DefDatabase<IncidentDef>.AllDefsListForReading.Where(CanUseIncident);
// CanUseIncident: if (incident.category != cat) return false; ... return incident.Worker.CanFireNow(...)
```

→ 叙述者**遍历整个 Def 数据库按 category 匹配**。
所以**模组只要新增 `IncidentDef` 并给原版 category，就会被对应叙述者自动纳入，完全不用改叙述者**。

**正反两个实证**（都是 VE 系列，可直接复查）：
- `VanillaEventsExpanded`：加 30 个事件，全仓 **0 个 `StorytellerDef`** → 照样会触发
- `VanillaGeneticsExpanded`：自定义 `IncidentCategoryDef GR_HybridRaid` + `baseChance 0`，同样 0 个 `StorytellerDef` → **叙述者永远抽不到，只能靠代码/任务触发**

**推论**：一个 `IncidentDef` 若 category 是自定义的、又没人引用它，就是"死事件"。
判断"会不会发生"要看：`category`（是否原版分类）＋ `baseChance`/`hidden` ＋ 是否被 `<incident>` / quest / scenpart / Comp 引用。

**另外**：模组可以**新增叙述者本身**（如 VFE 系列的 `VFEE_AriadneArchduchess` / `VFEM_Maynard`，VPE 的 `VPE_Basilicus`）——这是"加新叙述者"，不是"改原版叙述者"，别混。

### 清点步骤（2026-10-09 更新，推荐用双通道版）

> ⚠️ **旧基线陷阱**：`RimWorld-zh/RimWorld-Core` 的 `Version.txt` 是 **`0.19.2009 rev486`（1.0 时代）**，
> 它的「Core 共 63 个 `IncidentDef`」**不是 1.6 的数字**。因为模组不会重定义原版 defName，
> 「非原版事件条数」不受影响；但**「workerClass 是原版还是自定义」的归类会错**。
> 要判定 worker 归属，请用 `Chillu1/RimWorldDecompiled` 里的 `IncidentWorker_*` 类名做基线。

1. **建仓库映射（别猜）**：`scripts/build_ve_repo_map.py Vanilla-Expanded ve_map.json`
   拉组织全部仓库的 `About/About.xml` 用 **XML 解析**取 `packageId`。
   ❌ 不要用正则抓第一个 `<packageId>` —— `About.xml` 里 `<modDependencies>` 也有 `<packageId>`，
   实测会把 `VanillaRanchingExpanded` 映射成 `brrainz.harmony`。
2. **补非 VE 模组**：GitHub 搜索 + `raw.githubusercontent.com/<repo>/<branch>/About/About.xml`
   逐个验证 `packageId` 是否与清单一致（搜索结果里同名补丁模组很多，必须验 id）。
3. **双通道扫描**：`scripts/scan_events2.py <modlist.xml> <map.json> <out.json>`
   - XML 通道：`IncidentDef` 全字段 + `ParentName` 递归继承 + `StorytellerDef` 的 comp 列表
     + `IncidentCategoryDef` / `ScenPartDef` / `QuestScriptDef` / `GameConditionDef` + Patches 目标
   - C# 通道：`IncidentWorker` / `StorytellerComp` 子类、`[HarmonyPatch]`、`.forced = true`、`incidentQueue.Add`
   - 版本过滤：有 `1.6/` 只取 1.6，否则**降级到仓库最高版本**并记录 `version_used`
4. **定向 C# 取证**：`scripts/grep_cs.py <modlist.xml> <map.json> <out.json>`
   把 `forced` / `patch Storyteller` / `patch Incident` / `queueAdd` 落到 `文件:行号`。
5. **聚合**：`scripts/agg_events.py scanA_all.json scanB_all.json agg.json`（需同目录有 `vanilla_workers.json`）
6. **去重口径**：统计 StorytellerComp / ScenPart / C# 计数时**按仓库去重，不是按 packageId**——
   汉化包和多模块模组（如 `athelas.medievaltotalrim.*` 13 个模块共用一个仓库）会把数字虚高。
7. **必须写覆盖度**：能拿到源码的模组占比往往只有 10%~25%（纯 Steam 发布的 XML 模组没有公开仓库）。
   给出的数字要标注为「已核实下限」，并列出「很可能带事件但无源码」的模组名，不能当完整总数报。

### 深度对比要点（做 A vs B 事件对比时）

- **`parms.forced = true` 的计数会被 debug 菜单污染**：很多模组作者写了
  `new DebugMenuOption(...)` 里 `parms.forced = true` 用来手动召唤袭击。
  实测 MUGB 的 8 处里 **7 处是 debug、只有 1 处（信标 `QueueIncident`）是玩法路径**。
  → 报告前必须逐条看上下文，不能只报总数。判据：往前 25 行内出现 `DebugMenuOption` / `Dialog_DebugOptionList` 即为 debug。
- **「改叙述者」要看是框架层还是模组层**：
  - 框架层（`VanillaExpandedFramework`）的 `[HarmonyPatch(typeof(StorytellerComp), "IncidentChanceFinal")]`
    挂在**基类**上，一次实现全体 VE 模组共享；
  - 模组层的 patch 只对某个 `StorytellerDef` 生效。
  两边都装 VEF 时，真正差异是「框架之外还叠了几层模组级 patch」。
- **新增叙述者要看 comp 列表是不是模板克隆**：VEF 提供一套标准 comp 骨架
  （`RandomMain mtbDays=1.35` + `Disease×2` + `ThreatsGenerator` + `FactionInteraction×4`
  + `CategoryIndividualMTBByBiome×3` + `RandomQuest onDays=10/12` + `CategoryMTB mtbDays=15` + `Triggered`），
  VE 系列（VFE Empire / Pirates / Medieval2 / Tribals / VPE）的叙述者大多是逐条套用再改几个数值。
  判断"原创度"就看有没有模板外的 comp（如 `_ByVisibility` 变体、`ExclusiveIncidents`、自定义 comp）。
- **运行时替换 comp 对象**是自建系统的招牌写法：
  `[HarmonyPatch(typeof(Storyteller), "InitializeStorytellerComps")]` 里
  `__instance.storytellerComps[i] = new StorytellerComp_XXX { props = ... }`。
  XML 里看不到任何差异，全部在 C# 里完成。
- **`baseChance = 0` 不是"死事件"**：要顺着找触发者（自定义 comp / `forced` 队列 / quest / scenpart）。
  实测 MUGB 的 4 个 `baseChance=0` 全是信标仪式的结果事件。

## 派系（Faction）深度审计

用户问「各派系有没有独特事件 / 独特机制 / 怎么和玩家互动」时用这一节。

### 第 0 步（必做）：先列仓库顶层版本目录

**这是本节最容易翻车的地方。** VFE 多个模组的 GitHub 仓库**滞后于 Steam 版本**，且同名仓库可能不是同一个模组：

| 想要的模组 | ❌ 错误仓库（滞后） | ✅ 正确仓库 |
|---|---|---|
| VFE Medieval 2 | `Vanilla-Expanded/VanillaFactionsExpanded-Medieval`（只到 **1.4**，这是 Medieval **1**） | `Vanilla-Expanded/VanillaFactionsExpanded-Medieval2`（**1.6**） |
| VFE Insectoids 2 | `Vanilla-Expanded/VanillaFactionsExpanded-Insectoids`（只到 **1.4**） | `Vanilla-Expanded/VanillaFactionsExpanded-Insectoids2`（**1.6**） |
| Medieval Overhaul | `SirLalaPyon/MedievalOverhaul`（只到 **1.5**，Steam 已 1.6） | 无 1.6 镜像，**须标注"源码版本滞后"** |

所以**先跑一次"列顶层目录"**，确认 `1.6/` 存在；不存在就用 GitHub search 找 `-2` 后缀 / fork，仍找不到则在报告里标 ⚠️。

### 扫描

`scripts/scan_factions.py <repos.txt> <out.json> [--jobs N]`，`repos.txt` 每行 `<packageId> <owner/repo>`。
它输出每个仓库的：`factions`（**FactionDef 原始 XML 块**，含全部字段）、`incidents`、`quests`、`scenparts`、`gameconditions`、`code`（.cs 文件名）、`patch_targets`、`faction_comps`、`version_used`。

⚠️ `pick_version()` 的行为：目标版本（默认 1.6）缺失时**退化为最高可用版本**，而不是全保留 —— 否则 1.2/1.3/1.4 目录会混入、重复计数。

### 三个分析维度（用户要的就是这个）

**① 独特事件** —— 从 `incidents` 取，注意 `category` 与 `workerClass`：
- `category` 是原版分类（Misc/ThreatBig/FactionArrival…）→ 叙述者会自动抽（活事件）
- `category` 是**自定义分类** → 必须再查有没有**配套的 `StorytellerCompProperties_*`**，否则是"死事件"
  - 正样本：MUGB 哥布林 `MUGB_GoblinCaravanAmbush` + `MUGB.StorytellerCompProperties_MUGBGoblinCaravanAmbush` ✅
  - 反样本：VGE `GR_HybridRaid` + `baseChance 0` + 无 comp ❌

**② 独特机制** —— 三个证据源，按可信度排序：
1. `modExtensions` 块（如 `VEF.Factions.FactionDefExtension`、`KCSG.CustomGenOption`、`VEF.Graphics.TaggedDefProperties`）
2. `.cs` 文件名（`code` 字段）—— 如 `MerchantGuild.cs` / `Dialog_Barter.cs` / `GenStep_*.cs` / `LordJob_*.cs`
3. **解包后 grep C#**（这一步不能省）—— Harmony 补丁才是机制的铁证
   例：`VFEM2_MerchantGuild` 的"禁用货币"只写在补丁里：
   ```csharp
   [HarmonyPatch(typeof(TradeDeal), "CurrencyTradeable", MethodType.Getter)]
   public static void Postfix(ref Tradeable __result)
   { if (Find.WindowStack.IsOpen<Dialog_Barter>()) __result = null; }
   ```

**③ 与玩家的交流** —— 看这几个字段/来源：
| 线索 | 含义 |
|---|---|
| `permanentEnemy` / `naturalEnemy` | 是否可外交；`naturalEnemy` = 天敌但非永久敌对 |
| `dialogFactionGreeting*` / `dialogMilitaryAidSent` | **自定义对话**（有就是精细设计，去语言文件读原文） |
| `caravanTraderKinds` / `visitorTraderKinds` / `baseTraderKinds` | 贸易渠道 |
| `QuestScriptDef` 数量与命名 | 任务链深度（如 `VFED_*` 16 个 = 完整剧情线） |
| `modExtensions.startingGoodwillByFactionDefs` | 起始好感（VEF 框架机制） |
| `rescueesCanJoin` | 救援后可否招募 |
| `replacesFaction` | **替换原版派系**（如 Saurid 替换 `OutlanderRough`） |
| `isPlayer=true` | 是玩家开局，不是可外交 NPC —— **统计时要分开算** |

### 报告写法

- 分**「玩家派系」与「NPC 派系」**两张表，别混在一起
- 每个派系按 **独特事件 / 独特机制 / 与玩家的交流** 三小段写
- 派系描述（`<description>`）里的原文往往直接点明外交定位，**引用原文比转述可靠**
  （例：`VFEP_Mercenaries` 原文 "unlike other pirate factions, mercenaries can be communicated with and befriended"）
- 明确标注 **✅ 已核实 / ⚠️ 源码版本滞后 / ❌ 无公开源码（Steam 独占）**

## 报告必须包含的分级

| 等级 | 含义 |
|---|---|
| 🔴 需处理 | 已核实的问题（硬不兼容命中、硬依赖缺失、明确的 CE 补丁缺口） |
| 🟠 建议调整 | 加载顺序逆序、集成补丁目标排在框架之后 |
| 🟡 需实测 | 官方称兼容但有社区报告、改同一批逻辑的模组 |
| 🟢 无风险 | 明确核对通过的项（**必须写出来**，用户需要知道哪些不用管） |
| ⚪ 未核实 | 无法解析/无法访问的项，**绝不编造结论** |

## 铁律

1. **区分「硬依赖缺失」与「loadAfter 落空」** —— 后者无害，报成前者是误报
2. **不在官方支持清单 ≠ 不兼容** —— 必须查作者是否自带补丁（源码）
3. **时效性结论必须附核查日期 + 版本号**（CE 版本 / 游戏版本 / 模组版本）
4. **没做实测就写「未验证」** —— 兼容性最终需要玩家在自己版本下实测
5. 不要建议「删存档 / 清空模组目录」作为默认解法；排查用**单项变更 + 备份 + 逐组隔离**
6. 谈热度时区分 **累计订阅数** 与 **近期趋势**

## 参考文件

- `scripts/resolve_modlist.py` —— 单清单：一步跑出解析/重复/依赖/顺序四张表
- `scripts/diff_modlists.py` —— 两清单：画像 + 仅A/仅B 条目 + 汉化空转检测
- `scripts/build_ve_repo_map.py` —— **建权威 packageId→仓库 映射**（拉组织全部仓库的 `About/About.xml` 用 XML 解析，避开依赖 id 误匹配）
- `scripts/scan_mod_events.py` —— 旧版：只扫 XML，按 packageId→仓库清点新增 Def/事件（含叙述者绑定）
- `scripts/scan_events2.py` —— **新版双通道**：XML（`IncidentDef` 全字段 + `ParentName` 继承 + `StorytellerDef` comp 列表 + ScenPart/Quest/GameCondition + Patch 目标）+ C#（`IncidentWorker`/`StorytellerComp` 子类、`[HarmonyPatch]`、`.forced = true`、`incidentQueue.Add`），含版本降级逻辑
- `scripts/grep_cs.py` —— **定向 C# 取证**：把 `forced` / `patch Storyteller` / `patch Incident` / `queueAdd` 落到 `文件:行号`
- `scripts/agg_events.py` —— 聚合两清单扫描结果，输出分类分布 / 自定义 worker 比 / 独有事件 / 按模组分组（需同目录有 `vanilla_workers.json`）
- `scripts/scan_factions.py` —— 派系专项：抓 FactionDef 全字段 + 关联事件/任务 + .cs 文件名 + patch 目标；含版本目录退化逻辑
- `references/pitfalls.md` —— 踩坑清单与已验证的技术细节（§六 是事件清点专用 6 条）

## 已验证的线上源码来源

| 用途 | 仓库 |
|---|---|
| 原版 Core Defs 镜像（事件/叙述者/剧本基线） | `RimWorld-zh/RimWorld-Core`（branch `master`） |
| 反编译 C# 源码（触发逻辑） | `Chillu1/RimWorldDecompiled`（branch `master`），关键文件在 `RimWorldDecompiled-master/RimWorld/` 与 `.../RimWorld.QuestGen/` |
| Vanilla Expanded 全系列（~90 个模组） | `Vanilla-Expanded/<ModName>`，分支多为 `main`，少数 `master`（如 VanillaEventsExpanded、VanillaFurnitureExpanded、VanillaFactionsExpanded-Settlers） |
| Medieval Overhaul | `SirLalaPyon/MedievalOverhaul`（`master`，**只到 1.5，滞后于 Steam 的 1.6**） |
| A RimWorld of Magic | `TorannD/RWoM`（`main`） |
| Medieval Total Rim / Medieval Kingdoms | `athelas-tr/MedievalKingdoms_Rimworld`（`main`，**镜像不全，缺 Events / Russia / Mongols 模块**） |
| Caravan Adventures | `iforgotmysocks/CaravanAdventures`（`master`） |
| Research Reinvented | `petetimessix/ResearchReinvented`（`main`） |
| World Tech Level | `m00nl1ght-dev/WorldTechLevel`（`main`） |
| VFE Medieval 2（1.6） | `Vanilla-Expanded/VanillaFactionsExpanded-Medieval2`（`main`） |
| VFE Insectoids 2（1.6） | `Vanilla-Expanded/VanillaFactionsExpanded-Insectoids2`（`main`） |
| MUGB 哥布林（含专属叙述者 + 信标仪式） | `mustard1557/MUGB_Public`（`main`，**单版本仓库，无 1.x 目录**；注释为韩文） |
| VEF 框架（FactionDefExtension 等机制） | `Vanilla-Expanded/VanillaExpandedFramework`（`main`） |

**配额与抓取**：匿名 GitHub API 仅 60 次/小时（很快耗尽）。用 `https://codeload.github.com/<owner>/<repo>/tar.gz/refs/heads/<branch>` 下 tarball，tar 流式只抽 `Defs/` 与 `Patches/`；`raw.githubusercontent.com` 单独取文件不受该配额限制。仓库很多时先跑 HEAD 探测分支与存在性（见 `scan_mod_events.py` 的 fetch 逻辑）。
