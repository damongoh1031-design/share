---
name: ai-product-research
description: |
  AI 产品竞品调研与选型方法论。用于对比 AI 工作台 / Agent 平台 / AI 客户端（如 WorkBuddy、Octop、LobeHub、LibreChat、Cherry Studio、WeKnora、AnythingLLM、ChatGPT、Claude、Gemini），
  判断「面具/工作区隔离」「知识库作用域」「记忆机制」「扩展机制」「连接器」「多租户能力」「双端同步」等关键能力，判断产品的演进路线与定位，并产出可信的对比报告。
  含四条铁律（来源可靠度 / 优先读本机 / 先确认抽象单位 / 强制对称动作防确认偏差）、10 个分析框架（A 工作区构成 / B 共享隔离两级 / C 技能作用域 / D 双端同步 / E 扩展哲学 / F 连接器五判点 / G 知识库六判点 / H 记忆五判点 / I 差异分级 A-B-C / J 企业级基础设施七判点）、
  五套任务路径：「找替代品」（GitHub 检索避坑：API 限额 / AND 语义 / topic 限定式 / 高星死项目 / README 徽章 / 仓库迁移 / 表格脚本生成）、「验证候选是否适配」（需求清单固化 / 逐条证据出处 / 四个高价值探针 / 未发布功能三方核查（含「发布了但停更」反向应用）/ 一次性门槛与永久性门槛的区分 / 订阅额度换算：credits 单价 → 加价率 → 平台费占比分解 / **隔离单位横向对齐：「工作空间」三问判据**）、「判断演进路线与产品定位」（**三证据交叉验证：代码骨架 + 时间线 + 组织事实** / 文案与实现的双向错位 / Release body 扫描定位转折点 / 仓库内 PLAN·PoC 文档作为方向证据 / CLAUDE.md·AGENTS.md 作为项目自述 / 区分 agent 是「产品」还是「基础设施」）、「复核前序排除理由」（**排除理由逐条重验 + 三分表：当时就错 / 产品变了 / 仍成立** / 许可证以 `LICENSE` 文件为准 / GUI 有无 / 知识库有无 / 隔离强度的限定词（`off by default` / `not a perfect` / `experimental` / `untested on`）/ **区分「防串味」与「防对抗」** / 逻辑隔离 vs 物理隔离 / 第三方榜单只能用来「发现名字」/ Star 数必须对照头部仓库）与「新候选深度调研」（**来源优先级逐层执行并标注等级** / **「查不到」本身就是结论：HN 零结果 + Reddit 403 要如实报告并给旁证** / HN Algolia 检索与评论树提取 / **Show HN 帖五类金矿信息（合规缺失·作者自认短板·被质疑未答·寿命怀疑·作者给出的正确用法）** / **含母体的四列对照：GUI 封装层为了降低门槛会做减法** / **三个隐形开关（被禁用的工具·默认关闭·数据外流）必须全文 grep** / 目录分割许可五要素 / README 404 的两种成因（小写文件名·非 main 默认分支）/ 英文原文+中文译文对照引用），
  以及报告结构与 131 条常见误判（含新增二十二条：Windows 文件名大小写覆盖导致的「下载成功≠内容正确」/ Drift·moor schema JSON 表名在 `entity['data']['name']` / 开源仓内设计文档可能描述的是商业版（CE vs Pro 双轨）/ 官方文档同一指标三个数字（README 9 · 对比页 13 · 代码 15）/ 产品文档与技术文档冲突时以技术文档为准 / README 引用的卫星仓要逐个查许可与停更天数 / 复核脚本自身的 `colspan` 假阳性 / **有 Dockerfile 不等于可自部署（要区分「应用」与「凭据转发器」）** / **官方文档没写不等于代码没有（能力结论以类型定义为准，文档只用来理解意图）** / **`Mixed`/`extra='allow'` 类型不是取证终点，要找反向查询或专用 spec 文件换路取证** / **知识库是独立实体 ≠ 知识库能独立挂载（P2 必须看「工作区 ↔ 知识库」关联表，deepchat 是反例）** / **正则筛选器筛品类两次失败且方向相反（180/198 通过 vs 0 通过），改为人眼扫全量** / **`nohup` 后台任务跨轮被回收，长任务必须用工具自带后台机制 + 每 N 项落盘** / **星数排名已与产品形态脱钩（private-gpt 57.5k⭐ 自述已转型为 API 层，不再是客户端）** / **compose 里列出的服务不等于会启动（必须读 `profiles:`，Onyx Lite 里 opensearch/minio/redis 全被 profiles 排除）** / **计数前必须先定义判定标准（Onyx 连接器数 53→58→52，三次不一致）** / **两处官方描述冲突先怀疑粒度差异再怀疑错误（Onyx Lite 的「Agent knowledge 仍可用」不是矛盾而是概括 vs 字段级的粒度差）** / **精简模式的能力边界必须用字段级守卫函数判定（找 `*_validate_*` / `if not DISABLE_*` / `raise HTTPException`），概括式文案会误导** / **单产品深度调研必须给出横向对比里看不见的东西（多实体 / 多机制 / 数据库约束 / 迁移中状态 / 守卫函数）**）。
  **单产品深度调研（类型六）的处理方式**：当用户指名某一个产品要求「深入讨论和介绍」时，不要扩写横向报告，要挖横向对比时被压成一个格子的东西——①**找第二、第三个同类实体**（Onyx 除 `Persona` 外还有 `UserProject`，后者在 Lite 下反而完整可用）②**数清一个实体上有几种同类机制**（Onyx `Persona` 有 4 种知识挂载：document_sets / user_files / hierarchy_nodes / attached_documents，注释统一写 "for scoped search"）③**读数据库约束**（`CheckConstraint` / `ondelete=` / `unique index` 常比字段本身更能说明设计意图）④**查项目是否处于迁移中**（Onyx 正在 Vespa → OpenSearch，有 `ONYX_DISABLE_VESPA` + 一组迁移状态枚举，这是升级风险的重要来源）⑤**读守卫函数**（`*_validate_*` 定义的是能力真实边界）⑥**给出 8 条左右未验证项**，其中至少 1 条要标明是「逻辑外推」而非直接证据。
  **「独立工作区 / 自部署 / 稳定」三指标的可判定拆法**（复合词必须先拆子问题：独立工作区 → ①有无实体 ②提示词是否自有字段 ③能否绑知识库 ④知识库本身有无作用域；自部署 → ①有无服务端 ②是应用还是代理 ③数据是否自持；稳定 → ①许可能否被收回（是否带 CLA / 是否 copyleft 不可撤回）②项目会不会死（治理结构 + 巴士系数 + 卫星仓停更）③升级会不会崩（测试占比 + 门禁类型 + 有无非单元测试安全网，如属性测试 / 性能门禁 / 可访问性门禁）。**注意「许可不可被收回」与「可自由白标」是两件相反的事**：MIT 宽松可白标但可被未来改条款（已发布代码仍可用）；GPL/AGPL 不可撤回但传染性强）。
  **GitHub 配额耗尽的解法（实测）**：`search/repositories` 是**独立配额桶**（10 次/分钟），`q=repo:a+repo:b+repo:c+repo:d+repo:e` 一次可核验 5 个仓库；源码取证首选 `codeload.github.com/{owner}/{repo}/tar.gz/refs/heads/{main|master}`，**完全不受 API 限流**；先 `tar -tzf` 列名定向 grep 再 `tar -xzf --wildcards` 局部解压。
  补充（2026-10-07 实测）：**批量取 README 的第二个不受限通道**是 `raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md`（`main` 与 `master` 各试一次），一次可拉十几个仓库的正文而完全不消耗 `core` 配额——比 `/repos/{o}/{r}/readme`（走 core 桶，60 次/小时，一批 README 就能打满）划算得多。**`core` 桶耗尽后 `search` 桶仍可用**，所以此时改走 `search/repositories?q=repo:...` 做元数据核验。
  **两个新踩坑**：①`q=repo:` 堆叠里只要有一个仓库名不存在（改名/换 owner/打错），**整个查询返回 422 `Validation Failed`，不是静默忽略**——先用 `q=<name> in:name` 确认真实 owner/name 再堆叠。②Git Bash 里 `curl -o` 用**相对路径会静默失败**（bash 的 CWD 与 Windows 进程的 CWD 不同），必须用绝对 Windows 路径；同一循环里给多个分支/文件名写输出时要用**互不冲突的文件名**（Windows 大小写不敏感，`README.md` 与 `readme.md` 会互相覆盖）。
description_en: |
  Methodology for researching and comparing AI workbench / agent platform / AI client products. Use when evaluating assistant isolation, knowledge base scoping,
  memory mechanisms, extension models, connectors, multi-tenancy, or cross-device sync — and when judging a product's trajectory and positioning, or producing trustworthy comparison reports.
  Includes 4 iron rules (source reliability, read local runtime first, confirm the abstraction unit, forced symmetric actions to counter confirmation bias),
  10 analysis frameworks, five task playbooks — finding open-source alternatives (rate limits, AND semantics, topic qualifiers, abandoned high-star repos,
  README badge traps, repo-rename detection, script-generated tables), validating whether a specific candidate fits a requirement list (requirement
  weight table, per-item evidence citations, four high-value probes, three-way release verification incl. the "released but stale" reverse case,
  one-off vs permanent barrier distinction, subscription quota conversion: credit unit price → markup multiple → platform-fee share breakdown,
  isolation-unit cross-alignment with the three-question "workspace" test), judging trajectory and positioning (three-way cross-validation:
  code skeleton + timeline + organizational facts; bidirectional copy-vs-implementation drift; release-body scanning to locate the pivot;
  in-repo PLAN/PoC docs as direction evidence; CLAUDE.md/AGENTS.md as project self-description; distinguishing agent-as-product from agent-as-infrastructure),
  re-auditing previously rejected candidates (re-verifying each prior exclusion reason and classifying it as wrong-at-the-time / product-changed /
  still-holds; license read from the LICENSE file rather than the API field; GUI presence; knowledge-base presence; hunting isolation qualifiers such as
  "off by default", "not a perfect security boundary", "experimental", "untested on <platform>"; distinguishing anti-bleed isolation from adversarial
  multi-tenancy; logical vs physical isolation; third-party listicles only for discovering names; star counts validated against top repos),
  and deep-diving newly suggested candidates (executing the requested source-priority ladder and labelling each item's tier; treating "not found" as a
  finding — HN zero results and Reddit 403 must be reported honestly with corroborating evidence; HN Algolia search and comment-tree extraction;
  the five goldmine signals inside a Show HN thread: missing license, author-admitted weakness, unanswered challenge, longevity skepticism,
  the author's own "correct usage"; **four-column comparison that includes the parent product**, since GUI wrappers do subtraction to lower the
  barrier; three hidden switches — disabled tools, off-by-default features, data leaving the machine — that require a full-text grep; the five
  elements of a directory-split license; the two causes of a README 404 (lowercase filename, non-main default branch); bilingual original-plus-translation
  quoting) — report structures, and 123 documented misjudgments.
agent_created: true
---

# AI 产品竞品调研方法论

## 何时使用

**先判断动作类型 —— 五类任务的方法不同，走错路径会白做。**

**类型一：对比 / 找替代品（广度优先、检索驱动）**
用户要求对比两个以上 AI 工作台 / Agent 平台 / AI 客户端，或要求在 GitHub 上找某产品的替代品。
典型问题：「A 和 B 有什么差异」「能不能做到面具级记忆隔离」「知识库能否跨工作区共享」「哪个更适合多租户」「在 github 上寻找 X 的替代品，按功能维度列出」。
→ 走「技术避坑：GitHub 检索」那节。

**类型二：验证某个候选是否适配（深度优先、源码驱动）**
用户已有一个候选，要核对它是否符合此前沉淀的需求清单。
典型问题：「全面调研 X，查询是否符合我之前的需求」「X 能不能满足我那几条要求」。
→ **不要检索 GitHub，只对一个仓库做深度取证。** 走「技术避坑：验证候选是否适配」那节。

**类型三：判断演进路线 / 产品定位（深度优先、三证据交叉验证）**
用户问的是「它往哪走」，不是「它有什么」。
典型问题：「X 是否也和 Y 一样走 agent／通用工作台路线」「X 还是停滞在 chat 吗」「X 的定位是什么」「X 和 Y 的路线异同」。
→ 走「技术避坑：判断演进路线与产品定位」那节。**关键：不要用功能清单回答路线问题。**

**类型四：复核前序排除理由（重新评估已被淘汰的候选）**
用户回头问一个**此前已评估过、且已被排除**的候选，或问「有没有更优秀的」。
典型问题：「之前介绍过的 X，是否更完美的替代」「X 现在还是不是当初那个样子」「还有更好的吗」。
→ **不要从零重新调研，先做一件事：把前序排除它的理由逐条列出来，再逐条验证是否仍然成立。** 走「技术避坑：复核前序排除理由」那节。
→ **关键认知：产品会演进，前序的排除理由会过期。** 而「过期」有两种——**当时就错**，和**当时对但产品变了**。两者要分开报告。

**四类任务的共同前提**：先把需求的「抽象单位」和「权重」固化下来（铁律三），再动手。

**类型五：新候选深度调研（一次性调研多个同族产品，且要求来源优先级）**
用户直接给出一批（通常 2–4 个）新候选的仓库地址，要求调研，且往往附加**来源优先级约束**。
典型问题：「调研这三个仓库」「找资料尽量从官网、官方论坛、英文 blog、社区论坛（Reddit/Discord）优先搜索」「然后翻译成中文」。
→ 走「技术避坑：新候选深度调研」那节。
→ **关键认知一：来源优先级本身就是一项任务要求，必须逐条执行并标注等级** —— 「优先英文来源」经常得到一个**反直觉的结论：查不到**。查不到不是失败，**「零结果」本身就是结论**（说明该产品在英文社区无影响力），必须如实报告而不是含糊过去。
→ **关键认知二：同族产品要横向对照，但对照对象必须包含「它们所封装的母体产品」**。三个 GUI 封装产品互相比较得不出结论，把它们和母体 CLI 产品放在同一张表里，才会发现「封装层为了降低门槛而放弃了隔离」。

---

## 铁律一：来源可靠度排序（最重要）

AI 产品领域的中文内容**大量是 AI 生成的营销稿或代理商 SEO 内容**，错误率极高。

**可靠度从高到低：**

1. **本机运行时文件**（如果产品装在用户机器上）—— 最高，无可辩驳
2. **官方定价页 / 版本说明文档**
3. **官方操作文档 / 发布说明**
4. **GitHub README / Issue / Discussion**
5. **官方认证考试大纲**（如 Anthropic CCAO-F，会明确写清产品设计意图）
6. **第三方技术博客**（需交叉验证，注意供应商倾向）
7. **SEO 稿 / 横评软文**（今日头条、搜狐、php.cn、fenyai.com 等）—— **基本不可信，直接忽略**

**已证实的高价值来源：**
- Anthropic 认证考试大纲会明确写清产品设计意图（如「Memory is scoped per Project」）
- GitHub Issue 常包含设计意图原文（如 Octop Issue #618 说明了技能两级模型）

**警惕：** 记忆类产品（MemX、MemoryLake 等）的博客有夸大「记忆问题」以推销自身产品的动机。涉及功能有无的关键判断必须回溯官方口径。

### 铁律一的延伸：媒体转述与官方原话存在「强度差」

比「说错」更隐蔽的问题是「说满」——媒体把产品能力说得比官方原话更强，两者不矛盾，但强度差很多。

**已确认案例（Octop 专家沙箱）：**
- 媒体/发布说明稿：「专家沙箱**默认不信任**，无法越界访问宿主机文件系统与网络」
- 官方一手原话（文档站 + 仓库）：「可插拔后端 + 隔离边界 + Docker/OpenSandbox 沙箱 + `root_dir` jail」
- 强度差：前者暗示**开箱即强隔离**；后者意味着**实际强度取决于你选哪种后端，默认的本地文件系统模式并不是强隔离**

**处置规则：** 凡一手来源（仓库源码、官方文档站、官方 README）查不到、只见于媒体转述的说法，**必须单独标注为「媒体转述，未经官方确认」，不做采信**。不要因为它听起来更有利就写进结论。

**另一类：官方自身口径冲突。** 同一产品不同文档说法不一致时，标注冲突并给出验证方法，不要挑一个有利的写。已见案例：Octop Roadmap 标「PC/移动端客户端」未完成但安装章节已提供桌面客户端下载；README 徽章版本 `0.9.33` vs 发布说明称已发 1.0 GA。

---

## 铁律二：优先读本机文件

如果调研的产品装在用户机器上，**先读运行时文件**，这比任何文档都硬。

**WorkBuddy 示例路径：**
```
~/.workbuddy-ai/
├── settings.json                      # enabledPlugins 是扁平 map，看插件作用域
├── skills/                            # 单一扁平目录 → 用户级，无面具维度
├── plugins/cache/workbuddy-builtin/
│   ├── prompt-common/*/fragments/     # 记忆系统实现原文
│   │   ├── memory-context.md          # 记忆注入：三个模板变量拼接
│   │   └── workbuddy-memory-system.md # 三层记忆定义
│   ├── skill-expert-manager/*/references/
│   │   ├── plugin-json-spec.md        # 专家包结构（含 skills 字段）
│   │   └── agent-md-spec.md           # Agent 定义（含 skills 预加载字段）
│   └── interactionmode-*/             # 模式插件
└── memory/                            # 工作记忆
```

**能从中得到什么：** 记忆的真实存储形态、作用域、插件/技能的作用域、专家包能否内嵌资源。
这些是文档里查不到的实现细节。

**实测有效的取证路径（WorkBuddy）：**
```
~/.workbuddy-ai/plugins/cache/workbuddy-builtin/<plugin>/*/.codebuddy-plugin/plugin.json
  → 插件清单：hooks / skills / agents / commands / mcpServers 五类扩展点

~/.workbuddy-ai/plugins/cache/workbuddy-builtin/skill-expert-manager/*/references/
  ├── plugin-json-spec.md    # 专家包字段（expertType / agentName / teamInfo / members）
  ├── agent-md-spec.md       # Agent frontmatter、「不可添加 tools」、协作铁律
  ├── team-spec.md           # 专家团 4 正则 + 5 红线
  └── avatar-spec.md

~/.workbuddy-ai/plugins/marketplaces/     # 生态规模实测（官方 58 / 外部 149 / 团队 30）
~/.workbuddy-ai/plugins/cache/workbuddy-builtin/interactionmode-*/fragments/
  → 模式系统的六类提示词片段；expert 模式的 current-mode.md 全文只有 {{ PluginAgentPrompt }}

# 连接器层（常被忽略但信息量很大）
~/.workbuddy-ai/connectors-marketplace/.codebuddy-connector/connectors.json
  → 连接器注册表：id / type(mcp|cli) / auth_mode，以及 auth_injection_rules（跨连接器令牌注入规则）
~/.workbuddy-ai/connectors-marketplace/connectors/<id>/cli.json
  → CLI 型连接器：runtime / init / auth / unAuth / status / versionCheck / authUrlDomain
~/.workbuddy-ai/connectors-marketplace/connectors/<id>/skills/
  → 连接器自带技能（数量往往远超连接器数，如飞书 28 个）
~/.workbuddy-ai/connectors/<用户UID>/
  → 凭证落地：.master.key + 加密令牌 + 加密状态（salt/kdf/headerOverrides）+ 本地物化 mcp.json
```

**注意：`models.json` 含 API Key，不要整文件读取或输出。** 需要了解模型配置能力时查官方文档，或只 grep 字段名（`grep -oE '"[a-zA-Z_]+"\s*:' models.json`）。

### 铁律二的延伸：两类「证伪型」本机证据（价值极高）

常规取证是「读到某个文件证明能力存在」。但**能证明能力不存在的证据更硬**——它一次性排除一整类可能。优先找这两类：

**① 本机数据库 schema —— 查能力是否落本地结构化存储**

产品装在本地时，它的 SQLite/DB 表结构就是它的数据模型。查表清单和字段，能直接判断「记忆/知识/某能力是否结构化存储」。**只读打开，不要写入**：

```python
import sqlite3
con = sqlite3.connect('file:workbuddy.db?mode=ro', uri=True)   # ← mode=ro 只读
ts = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
for t in ts:
    print(t, con.execute('SELECT COUNT(*) FROM "%s"' % t).fetchone()[0])
print([r[1] for r in con.execute('PRAGMA table_info(sessions)')])   # 看关键表的字段
```

已见收获：WorkBuddy `workbuddy.db` **10 张表零记忆/知识表** → 记忆是纯 Markdown 由模型读写；`workspaces` 表只有 `path` + `last_opened_at` → **「工作区」就是个文件夹路径**，隔离靠文件系统。这两条比读十页文档都直白。

**② 账户功能开关表 —— 区分「能力不存在」和「本账户未开通」**

产品常把功能做成账户级开关。找到这份配置能拿到**一份比任何文档都完整的产品能力地图**，而且能证明某些能力「框架在但本账户没开」——避免把「未开通」误判成「没做」。

已见路径与收获：
```
~/.workbuddy-ai/cache/acc-product-config-v3.json   → productFeatures，141 项开关
  KnowledgeBase:true / ImaKnowledge:false / TencentDocsKnowledge:false
  TencentLexiangKnowledge:false / TencentNetDriveKnowledge:false / MemoryManagement:true
  knowledgeBases: [{provider: "Tencent"}]
```
→ 结论修正：「WorkBuddy 知识源少」不准确，准确说法是**「知识源可扩展（原生库 + IMA/腾讯文档/乐享/网盘），但按账户开通」**。这是企业交付模式的选择，不是能力缺失。

**③ 附：API manifest 与脚本 docstring 就是规格书**

有些产品的技能包会把 API 清单和请求体字段**直接落成本机文件**，比官方文档还全：
```
~/.workbuddy-ai/skill-library/*/api-manifest.json        # 34 个 API 的完整签名（字段名 + 类型）
~/.workbuddy-ai/skill-library/*/manage/rag_search.py     # docstring 里写全了请求体全字段与服务端行为
```
从 `rag_search.py` 的 docstring 拿到了 `enableRerank:true` 固定开、`searchMode:1`=KInfra Retrieve、`minScore` 不下发（服务端 rerank.threshold 过滤）——**这三条决定了整个检索质量栈的判断，官方文档里一条都没有**。

**④ 找「第二模型」的提示词 —— 理解产品设计意图的最佳入口（被低估）**

很多产品除主 agent 外还跑**第二个 LLM**（安全裁决器 / 分类器 / critic / 审查器）。**它的提示词是理解这个产品「怎么想」的最佳入口**，因为：

| 原因 | 说明 |
|---|---|
| 它必须写清规则 | 裁决器含糊 = 误判率高 |
| 它必须划清边界 | 要写明**什么不管** |
| 它包含威胁模型 | 直接告诉你产品认为什么危险 |
| 它常比主提示词更长 | 实测：安全裁决器 **25,564 字符 > 主 agent 19,607 字符** |

**搜法**：在提示词库里 grep `classifier` / `safety` / `guard` / `critic` / `review` / `judge`。

**已见收获（`auto-mode-classifier-instructions`，14 章节）**：
- `By default, actions are ALLOWED`（默认放行，刻意的设计选择）
- **HARD BLOCK**（用户意图无法解除）vs **SOFT BLOCK**（可明确授权解除）双层
- Scope 明确划界：`prevents security-relevant harm only — not agent quality or efficiency issues. An agent looping... must never be blocked`（**死循环不归安全管**）
- User Intent Rule **双向且门槛不对称**：Authorize 高门槛（须「acting dangerously」）/ Bound 低门槛（「a pause, which is cheap」）

**为什么这条反直觉但有效**：**要看一个产品怎么想，去看它写给自己第二个模型的规则** —— 那是它给自己人看的作业规程，不是对外文案。

### 铁律二附：开源产品的源码级取证

对方产品开源时，**仓库实现比官方文档更硬**。优先找这几类文件：

- **API 路由与模块**（如 Octop 的 `dashboard/src/api/modules/*.ts`）——从接口路径就能看出作用域设计。例：`/api/agents/{agent_id}/memory/*` 直接证明记忆是**按 Agent 隔离**的。
- **数据目录布局**（如 `~/.octop/agents/<agent_id>/` 内有 `SOUL.md`、`skills/`）——文件位置本身就是隔离证据。
- **仓库内设计文档**（如 `docs/agent-interop-mailbox.md`）——常直接标注实现状态与已知限制（例：inbox 是纯内存队列、重启丢任务）。
- **配置默认值**——默认值往往暴露产品真实的安全姿态（例：`hitl.enabled=False`、`tool_guard mode=warn`）。

**抓取路径：**
```
# 仓库文件树（会截断，但能看清目录结构）
https://api.github.com/repos/<org>/<repo>/git/trees/main?recursive=1

# 具体文件（稳定可用）
https://raw.githubusercontent.com/<org>/<repo>/main/<path>
```

### 铁律二附二：先看依赖，再看代码（识别「薄壳 + 闭核」）

**这是本轮最有价值的一条新方法。** 一个开源仓库可能有几百上千个文件，但**它的核心可能根本不在仓库里**。

**动作**：打开仓库后，**第一件事是读 `pyproject.toml` / `package.json` / `go.mod` / `Cargo.toml`**，不是读 `src/`。

**实测案例（Octop）**：

- 仓库有 569 个 Python 文件，看起来是个完整产品
- 但 `pyproject.toml` 的依赖里有四个包：`orcakit-harness-agent` / `harness-memory` / `harness-gateway` / `harness-browser`
- 这四个包**不在仓库里**，从 PyPI 安装
- 仓库自己的 `docs/architecture.md` 承认：`It glues three reusable libraries … into one wheel`

→ **定性：壳开源、核闭源。** 仓库里的 569 个文件是「集成层 + 领域层 + 前端」，真正的 agent 运行时在外部包里。

**然后必须做的一步：去 PyPI / npm 查这些外部包。**

```
curl -s https://pypi.org/pypi/<package>/json | python -c "
import sys,json; d=json.load(sys.stdin)['info']
print(d['version'], d['summary'], d.get('license'), d.get('home_page') or d.get('project_urls'))"
```

**最关键的发现往往在这里**：这些包的元数据会声明 License 并给出仓库地址。**但你必须真的去访问那个地址。**

实测：四个包的元数据**全部声明 MIT 并指向 `github.com/TencentCloud/harness-*`，而那四个地址访问全部 `Not Found`**。

> **声明不等于存在。** PyPI/npm 元数据里的 License 和仓库地址是发布者自己填的字段，没有任何校验。

**这一招的反向收益**：外部包的 `summary` 字段常直接暴露上游。实测：`orcakit-harness-agent` 的 summary 原文是 `Production-grade Harness Agent built on top of LangChain Deep Agents.` —— **一句话就把闭核内核的开源上游交代了**，后续只需对照 `langchain-ai/deepagents` 的能力清单，八项对八项全部对齐。

> **判断口诀**：仓库大 ≠ 产品完整。**依赖列表才是产品的骨架，`src/` 只是皮肤。**

### 铁律二附三：计数必须用对口径（复核一次）

**所有从命令输出抄进报告的数字，都要用第二种方法复核一遍。** 第一遍用的往往是最省事的命令，而最省事的命令口径常常不对。

**实测踩到的两个错（同一个错因）**：

| 报告原写法 | 实际 | 错因 |
|---|---|---|
| 「19 个专家目录」 | **18 个目录** + 1 个 `README.md` | `ls <dir> \| wc -l` 数的是**条目**，含 README |
| 「490 个子智能体」 | **489 个角色定义** + 1 个 `README.md` | 同上 |

**正确口径**：

```bash
# 数目录
find <dir> -maxdepth 1 -mindepth 1 -type d | wc -l

# 数文件（排除 README 等说明文件）
find <dir> -name "*.md" ! -iname "README*" | wc -l

# 数目录下的所有条目（含文件，用于交叉验证）
find <dir> -maxdepth 1 -mindepth 1 | wc -l
```

**另一个同类问题**：表格结构要匹配内容性质。实测把「8 处真实仓库迁移」和「2 处容易搞错的同名仓库」塞进同一张表，列头写「原地址 | 现地址 | 备注」——后两行根本不符合这个 schema。**拆成两张表比凑一张更清楚。**

---

## 铁律三：先确认需求的抽象单位

**这是最容易出错的一步。** 用户说「多租户」「隔离」「共享」时，含义可能完全不同。

必须区分：
- **多租户**（多个外部客户，各有身份）→ 抽象单位是「用户」，需要访问权隔离
- **单账户多工作区**（一个人管多个抽屉）→ 抽象单位是「工作区」，只需上下文隔离
- **多个工作线**（自己的几个项目）→ 传统 Chat 的 Project 就够

**两者的方案完全不同。** 单账户多工作区比多租户简单得多——不需要权限体系、不需要通道隔离、不需要担心账户边界。

**确认话术：** 「是租户自己登录进来用，还是你代他们操作、他们只收结果？」
这一句能省掉一半的返工。

**实测经历（18 轮研究）**：需求的抽象单位改过三次 —— 多租户 → 单账户多工作区 → 约束叠加（双端同步 + 隐私 + 新手友好）。**每次改，首选都要换。** 抽象单位没定之前，所有方案设计都是在猜。

---

## 铁律四：用强制对称动作防确认偏差

**这是最难自我察觉的一类错误。** 确认偏差不会让你「编造证据」，但会让你**停止搜索** —— 你找到 3 条有利证据就收手了，而第 4 条可能推翻前 3 条。

**行为证据（我的自省）**：写「A 独有」那一轮，找证据的效率明显高于写「B 独有」那一轮。同样的取证动作，在「想证明 A 强」的时候更快找到想要的证据。

**唯一有效的解法是流程，不是自觉**：

| 强制动作 | 作用 |
|---|---|
| 挖完「A 独有」→ **必须**再挖一遍「B 独有」，且篇幅对称 | 防止单向取证 |
| 写完「A 的优点」→ **必须**再写一遍「A 的代价」 | 防止软文 |
| 每条差异定级时 → **双向都定一遍** | 防止只给己方短板定 B/C 级 |
| 对照表 → **必须含等级列**，两侧 A 级缺失都列全 | 防止分级只停在正文里 |
| 报告结构 → 诚实评估与未解问题**各自单独成章** | 防止被埋在正文里 |

**判断自己有没有偏**：如果整份报告里「我方」的 A 级优势明显多于对方的，**先假设是自己取证不足**，再去补一轮对方的取证。

### 一条通用防线（能拦住大多数「无/没有/不存在」类错误）

> **在写下任何「无 / 没有 / 不存在」之前，先问一遍：**
> **「如果这个东西存在，它会藏在哪个文件里？」**
> **然后去看那个文件。**

**实测：这一问能拦住我 18 轮里 6 个错误中的 5 个。**

---

## 分析框架

### 框架 A：面具 / 工作区的构成要素

拆成七个要素逐一验证，不要笼统问「支持面具吗」：
1. 名字与描述
2. 预设身份指令（system prompt）
3. 专属知识文件
4. 输出风格 / 人格
5. **独立记忆** ← 唯一真正的分水岭
6. 独立对话历史
7. 分享给他人

前 3 项 + 第 6 项几乎所有产品都支持；**第 5 项决定成败**。

### 框架 B：「共享 / 隔离」两级架构识别

**关键问题：这个产品的知识库，是一个可以挂在多个工作区上的独立实体，还是每个工作区自带的附件？**

- **独立实体**（可跨工作区挂载）→ 能做到「知识库共享 + 记忆隔离」
- **工作区附件**（绑定单个工作区）→ 做不到，每份资料要重传

已验证：
| 产品 | 知识库性质 | 结论 |
|---|---|---|
| LobeHub 资源库 | 独立实体，「为每个助理建立独立的知识库，或者在空间中共享资源」 | ✅ 两级 |
| Octop 知识库 | 独立实体，公共/私有分级 | ✅ 两级 |
| Cherry Studio 知识库 | 独立实体，可多智能体绑定 | ✅ |
| ChatGPT / Claude / Gemini | **工作区附件**（Project 级文件） | ❌ |

### 框架 C：技能作用域

**技能是「能力」还是「文件包」？** 这决定它能否承载数据。

| 产品 | 技能定义 | 技能启用 | 能否带数据 |
|---|---|---|---|
| WorkBuddy | 专家包内嵌 `./skills/`，**单一扁平用户级目录，无实例级共享层** | 专家级（Agent frontmatter `skills` 预加载） | ✅ 文件包（`references/` + `scripts/` + `templates/`） |
| Octop | **两级**：实例级技能包 + 专家工作区级技能，可双向复制 | 专家级（`skills_disabled` 排除，`SkillFilterMiddleware` 热同步） | ✅ 文件夹（`SkillFilePart{path, content_base64}`，可含 scripts/references/examples） |
| LobeHub | 工作区安装 | 智能体级 | ❌ 技能=能力 |
| AnythingLLM | 实例级文件 | 工作区级 | ⚠️ JS 代码 |

**两级 vs 单级的实操差别：** 有实例级共享层的产品（Octop）能做到「**多个工作区各自隔离、但共用一套技能/知识库**」——这正是「单账户多工作区」需求的架构答案。单级产品（WorkBuddy）只能靠复制模拟共享，副本不会自动更新。
**已知限制：** Octop 在沙箱存储模式下**只能复制技能包、无法挂载目录**，共享技能改动不会同步到已复制的副本。

### 框架 D：双端同步的三种实现

| 路径 | 机制 | 代表 | 隐私 |
|---|---|---|---|
| 云端账号同步 | 数据在厂商云 | LobeHub 云版、ChatGPT、Claude | 最差 |
| 自建服务端 + 各端访问 | 数据在自己服务器，一致性天然成立 | Octop、LobeHub 自托管 | 中 |
| 本地优先 + 文件同步 | 数据在本机，靠 WebDAV 增量同步 | Cherry Studio | 最好 |

### 框架 E：扩展机制的两种哲学（声明式 vs 代码式）

对比两个工作台/Agent 平台的扩展能力时，**先判断它的扩展单元是「声明」还是「代码」**。这比列功能清单有效得多。

| | 声明式（WorkBuddy / Claude Code 一脉） | 代码式（Octop） |
|---|---|---|
| 扩展单元 | 一份 JSON 清单 + Markdown 提示词 + 可选脚本 | 一个入口文件（`main.py` 的 `setup(ctx)`） |
| 扩展者角色 | 提示词工程师（懂业务就能写） | 应用开发者（要会写代码） |
| 工具注册 | 只能挂外部 MCP，**不能自建原生工具** | 原生注册（`ctx.tool()`），支持参数表单 |
| 钩子本质 | **外部命令回调**（`"type":"command"`），只能看环境变量、执行副作用 | **可编程中间件**（`ctx.middleware()`），能读写运行时状态 |
| 界面扩展 | ⚠️ **plugin 层不支持，但另有 extension 层与 MCP App 层支持**（见下方警告） | ✅ 可注入前端渲染器（如 `ui/dist/index.js` + `octo_ui` JSON 协议） |
| 能力上限 | 提示词层 + 脚本 + **（extension 层可到独立进程 + 微前端 UI）** | 一直延伸到 UI 层 |
| 生态策略 | 常兼容成熟标准（如 Claude Code 插件格式）→ **继承生态** | 自建格式 → **生态从零长** |
| 产出效率 | 高（半小时一个专家） | 低（要写代码、读注册 API） |

**判断口诀：** 看它的 `plugin.json` / manifest 里有没有「入口函数」字段。没有 → 声明式，能力天花板低但上手快、生态可能更成熟；有 → 代码式，能力天花板高但门槛高、生态早期。

> ### ⚠ 已踩过的坑：别只看一层扩展模型
>
> **我犯过这个错。** 对比扩展能力时，我只查了 WorkBuddy 的 `.codebuddy-plugin/plugin.json`（五类扩展点 `skills`/`agents`/`commands`/`hooks`/`mcpServers`，确实没有 UI 字段），就下结论「**没有任何前端扩展点**」，并定级为 A 级架构差异。
>
> **错了。** 后续取证发现同一个产品还有两层：
> - **`extension.json` + `distribution.json`** — `service.entry` + `process: fork`（独立服务进程）+ `renderer: "mf"`（**Module Federation 微前端**）+ `permissions` + `rollout.{strategy,percentage}`（灰度）+ `resident`（常驻）+ `activationEvents`
> - **MCP App** — `mcp-app-preload.js` 在沙箱 `<webview>` 里渲染 MCP 提供的 HTML 资源，可向宿主索取 `host/getToken` / `host/getWBCurrentSessionId`
>
> **教训：一个产品的扩展模型可能有多层，每层有不同的声明文件。只查一层 = 取样偏差。**
>
> **标准动作：** 查扩展能力时，先列全候选声明文件再逐个看 —— `plugin.json` / `extension.json` / `distribution.json` / `manifest.json` / `mcp.json` / `cli.json` / `SKILL.md` frontmatter / `package.json` 的自定义字段。**并且去客户端资源目录（如 `resources/`、`app.asar.unpacked/`）里 grep 一遍 preload / bootstrap / entry 类文件名**——`mcp-app-preload.js` 这种文件名的存在本身就是证据。
>
> **代价：** 我上一轮把 B 级差异误报为 A 级护城河。等级判错会直接误导选型（「对方架构里没这一层」和「对方只是没做好」是两回事）。

**注意：** 声明式产品往往把「工具权限」收归平台（如 WorkBuddy 明确「开发者不可自行添加 tools，所有工具权限由系统统一分配」）。这是安全性设计，但意味着**你无法做工具级精细授权**。代码式产品通常给权限开关，代价是**默认值可能很宽松**（如 Octop `hitl.enabled=False`、`tool_guard mode=warn`），配置责任落在你身上。

---

### 框架 F：连接器层的五个判别点

「连接器」是各家都用的词，但含义可能完全不同。**不要假设两边对称**——不对称本身就是有效结论。按这五个问题逐一查：

**1. 连接器是磁盘目录，还是数据库记录？**
- 磁盘目录（清单文件 + 子目录）→ 声明式，接新连接器 = 写配置
- 数据库记录（表里一行，凭证是 BLOB 字段）→ 数据驱动，接新连接器 = 改代码
- 已见：WorkBuddy = 磁盘目录（`connector-meta.json` / `mcp.json` / `cli.json` + `skills/`）；Octop = 数据库表 `connectors`（`credential_blob` / `shared` / `config_json`）

**2. 连接器带不带技能？← 最本质的分歧**
- 带技能 → 连接器 = 接入通道 + **教 AI 怎么用的说明书**。AI 知道「何时用哪个能力、何时该反问用户」。代价是要大量人工投入（一个飞书连接器带 28 个技能）。
- 不带技能 → 连接器 = **一把刀**。技能与连接器解耦，AI 只看到工具描述，领域知识要自己写技能补。
- **这是「有和没有」的差别，不是「多和少」。**

**3. 支持 CLI 型连接器吗？支持得多深？**
- 关键子问题：① 有没有声明式清单（如 `cli.json`）还是硬编码在源码里？② 运行时是否托管（Node/Python 双运行时 or 只一种）？③ **安装目录是否隔离到平台管理目录，还是污染用户系统 npm/pip**？
- 已见：WorkBuddy = 声明式 + Node/Python 双运行时托管 + 目录隔离（接新 CLI = 写个 JSON）；Octop = 硬编码 `_SPECS` + 仅 npm + 只隔离配置目录不隔离安装目录（接新 CLI = 改 Python 提 PR）
- **「声明式 + 隔离」是开放能力，「硬编码 + 不隔离」是内置功能**——量级差异。

**4. OAuth 是内置管理器还是各连接器自理？**
- 2026 年这层已收敛：OAuth 2.1 + PKCE + DCR（动态客户端注册）+ 公共客户端（不持 client_secret）是行业标准。两边都实现了。
- **这层通常不构成差异**，别在这里找区分度。真正要看的是 Token 自动刷新有没有、刷新失败怎么引导重新授权。

**5. 凭证存在哪？**
- 本地文件 + 本地加密 → 凭证不出机器，但换机器要重新授权
- 控制面数据库 → 可跟库迁移，但**库能放远程 PostgreSQL 时凭证就上服务器了**
- 已见：WorkBuddy = `~/.workbuddy-ai/connectors/<UID>/` + `.master.key` 本地加密；Octop = 控制面 DB 的 `credential_blob`（Fernet 加密）

**额外留意：有没有「跨连接器凭据编排」。** 某些场景需要把两个连接器的令牌拼进同一次请求（如同时连了主账号与 OA 账号）。WorkBuddy 用 `auth_injection_rules` 声明式支持；这类机制多数产品没有，属于差异化能力。

---

### 框架 G：知识库层的六个判别点

「知识库」这个词的歧义比「连接器」更大——有的产品指的是**内容管理平台**（文档/表格/网盘都在里面），有的指**纯 RAG 管线**。**先分清它是什么，再比能力**，否则会得出「A 知识库比 B 弱」这种没有意义的结论。

**1. 它是内容管理平台，还是 RAG 管线？← 先分这一刀**
- 内容管理平台 → 节点有多种类型、有空间/目录树、有协作与分享、检索只是其中一个能力
- 纯 RAG 管线 → 只有上传 → 解析 → 分块 → 向量化 → 检索这一条线
- 已见：WorkBuddy 资料库 = 内容平台（六种 `kind`：doc / page / database / link / drive / smh + 空间协作 + 轻发布 + 34 个 API）；Octop 知识库 = 纯 RAG（17 文件包，除检索外无内容管理）
- **这条决定需求匹配**：要「沉淀 + 协作 + 分享」只有内容平台能做；要「纯检索 + 可控」管线更直接

**2. 检索栈是托管服务还是自建实现？自建的话有没有 ANN？**
- 看检索请求里有没有 `rerank` / `searchMode` / `threshold` 这类字段——有说明后端是成熟检索服务
- 自建的要**查源码里 `search()` 的实现**：是 `SELECT ... WHERE vector <-> ?` 走索引，还是全表拉出来算余弦？
- 已见：WorkBuddy = KInfra Retrieve（`searchMode:1`）+ `enableRerank:true` 固定开 + 服务端 `rerank.threshold` 过滤；Octop = 每库一个 SQLite，`SELECT` 无 `WHERE` 无 `LIMIT`，Python 循环手算余弦，**无 HNSW / 无 IVFFlat / 无 faiss**
- **全表扫描是可扩展性上限，不是实现细节**——几万 chunk 后延迟线性增长，且改不动（代码级问题）

**3. 索引参数暴露在哪一级？**
- 选项：不可调（服务端）／实例级／知识库级／文档级
- 已见：WorkBuddy 只有 `limit`（默认 20 最大 100）；Octop 有 `chunk_size`(800) / `chunk_overlap`(120) / `retrieval_k`(8) / `context_char_budget`(6000)，但源码首行注释写着 **`Instance-wide`**——整个实例一套，不能按知识库或专家差异化
- **「有参数」和「参数够用」是两件事**，要看作用域粒度

**4. 分块是按结构还是按字符？**
- 按结构 → chunk 带块 ID 或语法族标记（能映射回原文结构）
- 按字符 → 固定步长硬切，不认段落/标题/句子边界
- 已见：WorkBuddy chunk 带 `blockIds`，`nodeKind` 决定语法族（doc=markdown / web|page=纯文本 / database=字段拼接）；Octop `chunk_text()` 全文 24 行，`range(0, len(content), step)` 硬切

**5. 知识库能不能绑定到智能体？← 结构差异，不是程度差异**
- 查智能体/专家的 manifest 规范里有没有知识库字段
- 已见：Octop 专家 profile 有 `knowledge_base_ids`，**三级作用域**（实例实体 → 专家预设默认 → 每轮 `configurable` 覆盖）；WorkBuddy 专家规范 21 个字段**零知识库字段**（三份规范搜「知识库/资料库/knowledge/library/spaceId」零命中）
- **WorkBuddy 的检索范围只能由 Agent 调用时传 `spaceIds`/`nodeIds` 决定**——不可声明、不可预设、不可审计
- **负向证据的价值**：三份规范全文搜关键词零命中，比「文档里没提」强得多，可以直接下结论

**6. 可见性模型是几级？**
- 已见：WorkBuddy = 空间成员角色（个人空间 / 团队空间）；Octop = `owner_user_id = ? OR shared = 1` 两级
- **额外留意 `default_open` 这类「默认挂载」标志的作用域**。Octop 的 `default_open` 是 **per-owner** 偏好——共享知识库标了默认开启也只对创建者注入，不污染其他用户上下文。这个细节在文档里查不到，只有读源码注释才知道

---

### 框架 H：记忆层的五个判别点

记忆比知识库更容易被高估。**核心问题只有一个：它是文本，还是数据？** 但要用五个问题把它问实。

**1. 记忆存在哪？是文件还是结构化存储？**
- **决定性做法：查本机数据库 schema。** 如果产品装在本地，直接看它的 SQLite/DB 里有没有记忆表——这是**证伪型证据**，能一次性排除「记忆落本地结构化存储」的可能
- 已见：WorkBuddy `workbuddy.db` **10 张表零记忆表**（sessions / workspaces / automations / automation_runs / automation_runtime_state / automation_delivery_outbox / buddy_snapshots / session_usage / migration_meta / drizzle_migrations）→ 记忆是纯 Markdown 文件，由模型用 Edit 工具直接读写，**无索引、无检索、无结构化存储、无生命周期**
- 已见：Octop 记忆落 `memory.sqlite` 或 PostgreSQL，**六层实体**

**2. 记忆是模型自己写的，还是系统自动提取的？**
- 模型自己写 → 透明可读可直接编辑（优点），但没有去重、没有检索、没有生命周期，量大了只能靠模型维护
- 系统自动提取 → 有工程化，但你看不懂它在记什么，只能通过面板/API 观察
- 已见：WorkBuddy = 模型用 Edit 工具写 Markdown（靠字符限额控体积：Layer2 4000 / Layer3 3000 字符每会话）；Octop = 系统自动提取 + 人工可介入

**3. 有没有生命周期管理？（候选 / 晋升 / 废弃 / 替换）**
- 有 → 记忆是有状态的数据，能纠错能过期
- 无 → 记忆是文本，只能覆盖重写
- 已见：Octop 六层实体 `raw_events` → `candidates`（`:promote` 晋升 / `:reject` 拒绝）→ `atoms`（`:deprecate` 废弃 / `:replace` 替换创建后继）+ `entities` / `episodes` / `journal`；WorkBuddy 无这些概念
- **「候选 → 晋升」这个环节的存在，说明提取不自动写库、有审核**——这是设计意图的直接证据

**4. 提取策略可配吗？按谁配？**
- 已见：Octop 的 `extract-config` 按**专家**配：`memory_enabled` / `extract_on_session_end` / `extract_trigger_mode`(`idle`|`interval`) / `extract_idle_seconds` / `extract_interval_seconds` / **`aux_model`（记忆提取专用辅助模型）**
- **`aux_model` 这类字段很说明意图**：记忆提取用独立小模型跑，不占主模型配额

**5. 隔离单位是什么？← 唯一真正的分水岭**
- 候选单位：账户 / 用户 / 工作区 / 智能体
- **注意：隔离单位是「工作区」不等于「智能体」。** 如果会话表里有 `expert_id` 但记忆不按它分，那就是做不到专家级隔离，只能「一个专家一个工作区」用目录隔离冒充
- 已见：WorkBuddy 隔离单位是**工作区**（`workspaces` 表只有 `path` + `last_opened_at`——工作区就是个文件夹路径），`sessions` 表有 `expert_id` 但无 memory 字段；Octop 命名空间 `agent_<agent_id>` **硬编码**，物理上无共享层
- **顺手查后端的可插拔性**：Octop 记忆后端 sqlite / postgres 可换，且**控制面是 PG 时自动切到 PG** → 隔离从文件级降为命名空间级。这个细节会改变隔离强度的结论

**额外留意：有没有审计与人工干预。** Octop 手工创建/修正记忆的审计标为 `actor=user` 且**客户端不可覆盖**，且人工修正**不产生对话事件与提取候选**（不污染自动提取链路）。有这类设计的说明记忆被当成需要追责的数据对待。

**证据缺口要标注**：Octop 的记忆内核 `harness_memory` **未开源**，提取算法、分层合并、检索方式、衰减策略四项无法验证。**凡只能从 API 面反推的判断，必须标注「非实现证据」。**

---

### 框架 I：差异分级——把「没做」和「做不了」分开

用户问「A 有哪些 B 没有的功能」时，**不要直接罗列差异**。先给每条差异定级，否则会把「对方改个版本就能追上」和「对方架构里根本没有这一层」混在一起，误导选型。

| 等级 | 含义 | 判定动作 |
|---|---|---|
| **A 级** | 架构级不可能 | 找对方的**扩展点清单 / 数据模型**，看有没有对应槽位。**无槽位 = A** |
| **B 级** | 有对应物但机制不同 | 两边都能做同一件事，但实现路径 / 作用域 / 可调性不同 |
| **C 级** | 产品路线选择 | 能力上双方都能做，只是谁做了谁没做，改版可能追上 |

**判定顺序（照做）：**
1. **先拉对方的扩展点/能力清单**（如 WorkBuddy 插件清单只有 `skills` / `agents` / `commands` / `hooks` / `mcpServers` 五类）
2. **逐条对照待评能力需要落在哪个槽位**。槽位不存在 → A 级，结论可以写「这不是做得不如，是扩展模型里没这一层」
3. 槽位存在但语义不同 → B 级，重点写**机制差异**（作用域粒度、参数可控性、失败可见性）
4. 槽位存在且语义相同 → C 级，**明确写「改版可能追上」**，不要让用户误判为护城河

**典型 A 级实例（已验证）：** WorkBuddy 的工具结果只能是文本或 Markdown，**没有任何前端扩展点**；Octop 的 `plugin.yaml` 有 `ui.entry` + `ui.manifest.json`，工具可返回 `octop_ui` 信封（`{"octop_ui": {"renderer": ..., "version": ...}, "data": {...}, "text": "纯文本回退"}`）渲染成卡片，并支持 `host.patchResult(callId, data)` **L2 刷新——零 token、零新回合**。这是 A 级：前端渲染层在 WorkBuddy 的扩展模型里不存在。

**反向也要做。** 同一个能力在对方侧可能是 A 级缺失。定级是双向的，不要只给自己有利的方向定级。

**报告里必须有一张完整对照表（含等级列）**，否则分级只停在正文里，读者无法速查。

---

### 框架 J：企业级基础设施的七个判别点

回答「A 有什么 B 没有的」时，**最容易漏掉的一类能力是「基础设施」**——它不出现在功能列表里，只在运行时目录、数据库 schema、客户端资源里露出来。这类能力往往是真正的 A 级差异。

**七个判别点，逐一去运行时目录里找：**

| # | 判别点 | 找什么 | 为什么重要 |
|---|---|---|---|
| 1 | **审计是否防篡改** | 日志里有没有 `prevHash` / `hash` / `sequence` / 分段清单 / `state.json` 链头 | 「日志」和「**可举证的**责任链」是两回事。有哈希链 = 能防改历史 |
| 2 | **变更是否可回滚** | `changes-index` / `changes-detail` / **`checkpointId`** / 文件版本目录（`@v1 @v2`） | 有 diff 索引 + 检查点 = 按轮次回滚，不用自己管 git |
| 3 | **产物是否可溯源** | 产物索引里有没有 `sourceTool` / `requestId` / `toolCallId` / `ownerConversationId` | 四个 ID 齐全 = 「这个文件是谁、什么时候、用什么工具生成的」可追 |
| 4 | **动作是否被裁决** | 有没有第二个模型的提示词（安全裁决器 / 分类器 / critic） | **规则匹配 vs LLM 语义裁决**是两种代际。看提示词长度，25K 字符的裁决器就是重投入 |
| 5 | **有没有威胁情报** | `threat-database` / IOC 表（`ioc` / `ioc_type` / `category` / `family`） | 本地 IOC 库 = 能离线阻断已知恶意目标 |
| 6 | **投递是否可靠** | 自动化表里有没有 **outbox 模式**（`dedupe_key` / `lease_owner` / `lease_expire_at` / `attempt_count` / `max_attempts`） | 「定时跑一下」和「至少一次投递 + 租约防重 + 退避」不是一个量级 |
| 7 | **上下文是否分级管理** | 阈值配置（warning / critical / emergency 多层 + 按模型覆盖 + 多动作维度） | 单一阈值 = 粗暴截断；多层阈值 + 按模型覆盖 = 精细调度 |

**附加判别点（产品侧）：**

- **扩展模型有几层？** 见框架 E 的警告。`plugin.json` 之外还有 `extension.json` / `distribution.json` / MCP App。
- **有没有「工作强度」档位？**（如 `/effort ultracode`：每个实质请求先规划动态工作流）——这比模型选择更能反映产品对「重度使用」的支持程度。
- **有没有自我复盘？** 找 `insights-*` 类提示词，看是否产出 `user_satisfaction_counts`（尤其有没有 **`frustrated`** 这类负向计数）。**关心「人用得怎么样」vs 只关心「系统跑得怎么样」是两种自我认知。**
- **有没有区域合规强制约束？**（如地图数据白名单 + 禁止清单 + 领土完整要求）——这类能力对海外竞品是 A 级，因为**不是「没做」，是「不会做」**。

**反向使用：** 这套判别点也能用来评估**开源自托管产品**的缺口。本机对比中，开源侧的对应物通常是「你自己配」（如规则匹配的 `tool-guard`、系统 cron、可插拔但默认关闭的 history 归档）。

**诚实标注义务：** 基础设施类能力经常有「开关存在但本账户/本区域未开通」的情况。**必须先去产品配置表（如 `acc-product-config-v3.json` 的 `productFeatures`）核对**，区分「平台有能力」与「本机可用」，并在报告里明确写出读法约定。

---

## 技术避坑：文档抓取

### ★ 万能技巧：官方文档站加 `.md` 后缀取源文

**很多文档站（Docusaurus / Mintlify / VitePress 类）支持在页面 URL 后加 `.md` 直接返回 Markdown 源文。**

实测（Open WebUI，2026-09）：

```
https://docs.openwebui.com/features/chat-conversations/memory        # HTML，含导航噪声
https://docs.openwebui.com/features/chat-conversations/memory.md     # ✅ Markdown 源文，干净完整
```

**为什么这个技巧价值高**：
- 不受导航/侧边栏干扰，拿到完整正文
- 表格、代码块结构完整保留
- 用 WebFetch 抓时，模型能读到更多有效内容

**标准动作**：抓官方文档前，**先试 `.md` 后缀**；失败再退回 HTML。

### 路径猜测一定会失败 —— 改用「限定域搜索」

**不要猜文档路径。** 实测 `docs.openwebui.com/features/authentication-access/rbac` 返回 404，真实路径是**带尾斜杠**的 `.../rbac/`。

**正确做法**：用 `WebSearch` 限定官方域找真实路径：

```
WebSearch(query="Open WebUI docs RBAC permissions groups workspace", allowed_domains=["docs.openwebui.com"])
```

**注意中英文文档站可能是两个域**：Open WebUI 有 `docs.openwebui.com`（英）和 `docs.openwebui.cn`（中）。中文站的翻译有时能直接确认术语（如「工作空间」），**但版本可能滞后，数字一律以英文站/源码为准**。

### 已确认的失败源

**lobehub.com 的 `/zh/docs/*` 路径大量返回 404。** 有效替代：

```
# LobeHub 文档镜像（稳定可用）
https://raw.githubusercontent.com/northword/lobehub/refs/heads/canary/docs/<path>.zh-CN.mdx

# 例如
https://raw.githubusercontent.com/northword/lobehub/refs/heads/canary/docs/usage/start.zh-CN.mdx
https://raw.githubusercontent.com/northword/lobehub/refs/heads/canary/docs/usage/getting-started/memory.zh-CN.mdx
https://raw.githubusercontent.com/northword/lobehub/refs/heads/canary/docs/usage/getting-started/resource.zh-CN.mdx
```

**其他已知失败源：** `contextqmd.com` 常返回 500；GitHub discussions/issues 直链可能 404（改用搜索定位）。
`lobehub.org.cn/docs/...` 部分可用。

**已实测稳定可用的官方路径（2026-09 验证）：**
```
# WorkBuddy 开放平台开发者规范（内容完整，最权威的一手扩展规范）
https://open.workbuddy.cn/docs/expert     # 专家包结构 + plugin.json 全字段 + Agent frontmatter + MCP/连接器依赖
https://open.workbuddy.cn/docs/skill      # SKILL.md 结构 + references/scripts/templates + allowed-tools

# WorkBuddy 产品文档
https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Model
https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Expert-Center
https://cloud.tencent.com/document/product/1831/134445    # 企业版模型配置

# Octop 官方仓库（raw 路径稳定）
https://raw.githubusercontent.com/TencentCloud/Octop/main/README_CN.md
https://raw.githubusercontent.com/TencentCloud/Octop/main/plugins/README_CN.md

# 仓库文件树（会截断，但够看清目录结构）
https://api.github.com/repos/TencentCloud/Octop/git/trees/main?recursive=1
```

---

## 技术避坑：GitHub 检索（做「找替代品」类任务必读）

### 限额（实测，2026-09）

| 接口 | 未认证限额 | 说明 |
|---|---|---|
| `search/repositories` | **10 次/分钟** | ⚠️ 不是 60 次/小时。`sleep(7)` 不足以保证安全 |
| `repos/{owner}/{repo}` | **60 次/小时** | 与所有其他 core 调用共享配额 |
| `gh` CLI | **常不可用** | 先 `which gh` 确认；不可用就老老实实处理限额 |

**403 处理必须是递增退避**（65s / 80s / 95s / 110s），不能固定 sleep。实测 45 组检索式总耗时约 10 分钟，其中含多次 403 退避。

**先查两个桶各自的余量**（一次调用就够，别靠猜）：

```bash
curl -s -H "User-Agent: rs" https://api.github.com/rate_limit | \
  python -c "import json,sys;d=json.load(sys.stdin)['resources'];[print(k,d[k]['remaining'],'/',d[k]['limit']) for k in ('core','search')]"
```

### ★ 配额耗尽后的两条出路（本轮实测，比等待划算得多）

**背景：一次批量抓 40 个 `repos/{owner}/{repo}` 会把 60 次/小时的 core 配额一次打满**，脚本随后进入退避重试，**2 分 37 秒后零输出**（`X-RateLimit-Remaining: 0`，`X-RateLimit-Resource: core`）。等恢复要 1 小时，不可接受。

**出路一：改用 `search` 桶 —— 它是独立的配额桶（10 次/分钟）。**

`repo:` 限定符可以在一次请求里**堆叠**，用 `+` 连接即得 OR 语义：

```
q=repo:ChatGPTNextWeb/NextChat+repo:janhq/jan+repo:khoj-ai/khoj+repo:onyx-dot-app/onyx+repo:siyuan-note/siyuan
```

实测一次拿到 5 个仓库的完整元数据（`stargazers_count` / `license.spdx_id` / `created_at` / `pushed_at` / `open_issues_count` / `forks_count` / `language` / `topics` / `homepage` / `archived`），**与 `repos/` 单查等价**。按 5 个/请求 + `sleep(7)`，一分钟可核验 50 个仓库。**注意返回的 `total_count` 可能小于请求数——说明有仓库坐标不存在，要单独用 `q=<name> in:name` 重找。**

**出路二（源码取证首选）：用 `codeload` 直接下源码包，完全不受 API 限流。**

```bash
# main 或 master，逐个试
curl -sL -o repo.tgz -w "http=%{http_code} size=%{size_download}\n" \
  "https://codeload.github.com/{owner}/{repo}/tar.gz/refs/heads/main"
```

拿到 tarball 后**先用 `tar -tzf` 列文件名做定向 grep，再 `tar -xzf --wildcards` 只解需要的路径**，不要全量解压（Onyx 9,531 个文件、FastGPT 111MB）。这条路径是本轮 14 个仓库源码核查的主力——比 Trees API 更快、更完整、且没有配额。

**代价**：大仓库下载慢（jan 130MB+ 在限速下没能下完，最终只能读 README 并在报告里如实标注「未做源码核查」）。**所以要按价值排序，先下最可能入围的。**

### `q` 是 AND 语义（最大的坑）

**多裸词组合会返回 0 结果。** 实测：`graph agent orchestration state machine stars:>3000` → `total=0`。原因是多个裸词必须**同时**出现在 name / description / readme 中。

**第一轮 10 组里 6 组返 0，命中率 40%。**

**修正：改用 `topic:` 限定式**，命中率提升到接近 100%：

```
topic:agent-memory stars:>500
topic:workflow-engine stars:>2000
topic:model-context-protocol stars:>3000
topic:agent-skills stars:>200
topic:code-interpreter stars:>500
```

**注意 `topic:` 也会带回噪声。** 实测 `topic:observability` 命中 netdata / cilium / jaeger（基础设施 APM，不是 LLM 可观测）；`topic:knowledge-base` 命中 AFFiNE / siyuan / logseq（笔记应用，不是 RAG）；`topic:proactive` 命中 Windows 加固工具。**topic 只是提高召回，筛选必须人工做。**

### 检索脚本模板（累积去重 + 退避）

```python
def search(q, per_page=10, sort="stars", tries=4):
    url = ("https://api.github.com/search/repositories?q="
           + urllib.parse.quote(q)
           + f"&sort={sort}&order=desc&per_page={per_page}")
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json", "User-Agent": "research-script"})
    for t in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                time.sleep(65 + t * 15)      # 递增退避，别用固定 sleep
            else:
                return None
    return None

# 累积去重：读已有结果，用 full_name 做 known 集合，只追加新条目
```

### search 结果的 star 数会滞后 → 必须定向复核

**search 返回的是索引快照，`GET /repos/{owner}/{repo}` 才是实时值。** 实测同一个仓库两处差 30+ stars。

**做法**：入围候选（约 30–60 个）全部走 `repos/` 单独核验一次，同时抓 `created_at`（算星数/天筛查注水）和 `pushed_at`（算停更天数）。

### 表格数据必须脚本生成，禁止手写

星数、语言、最后推送、License 这四列**手写必错**。做法：

1. 先把所有候选元数据存成一个 `_all.json`
2. 再写一个生成脚本，从 JSON 读值填表
3. 生成后校验：`s.count('| - | - | - | - | - |')` 应为 0（表示没有取不到值的行）

### 四个必查的「隐藏坑」（都在实测中踩到过）

| 坑 | 检测方法 | 实测案例 |
|---|---|---|
| **高星死项目** | 按 `pushed_at` 算停更天数 | `daytonaio/daytona` 71,722⭐ 已公告停止维护；`coqui-ai/TTS` 46,023⭐ 停更 763 天 |
| **README 徽章 ≠ LICENSE** | 同时看 README 徽章、`raw.../LICENSE` 原文、API 的 `license.spdx_id` | `Tencent/WeKnora` README 写 MIT，实际是腾讯自定义许可；API 的 `NOASSERTION` 才对 |
| **仓库迁移** | 访问旧地址会返回 `Moved Permanently` | `sst/opencode`→`anomalyco/opencode`；`comfyanonymous/ComfyUI`→`Comfy-Org/ComfyUI`；`microsoft/presidio`→`data-privacy-stack/presidio` |
| **同名陷阱** | 核对 `full_name` 与产品描述是否一致 | `getzep/zep` 自述 "not Zep's product or service"，真开源件是 `getzep/graphiti`；**`nbonamy/witsy` 只有 8⭐（创建 2026-04-14），真仓是 `Kochava-Studios/witsy`（2,027⭐ AGPL-3.0）** |

**同名陷阱的自动化检测**：把候选按 `stars` 升序看一遍。**真产品不会只有个位数 star**，所以「名字对但 star 极低 + 创建日期很新」的组合几乎必然是空壳/同名仓。本轮就是这样发现 witsy 的。

**迁移检测代码**：抓 `repos/` 时若返回 `Moved Permanently`，用 `curl -sL` 跟随重定向拿规范名，并**用规范名做数据集的 key**（否则 `full_name` 与 key 不一致，表格会取不到值）。

### 双向评估是「替代品调研」的硬要求

只写「目标产品独有的能力」会系统性高估它。**必须对称地写一遍「开源独有的能力」**，且给出具体数字对比。

实测收益：本轮因此发现 8 项开源明确更强的能力（沙箱隔离强度、记忆检索质量、技能生态规模、技能治理、认证、编排可靠性、可观测、用量计费），其中「沙箱隔离强度」是**数量级差距**而非程度差距——这类结论只有对称取证才能得出。

---

## 技术避坑：验证候选是否适配（做「查询 X 是否符合我的需求」类任务必读）

**动作类型不同，方法就不同。** 前面「GitHub 检索」那节是给「**找**替代品」的（广度优先、检索驱动）；这节是给「**验证**某个候选」的（深度优先、源码驱动）。

**判据**：用户请求里出现「是否符合我的需求」「调研 X」+ 已有明确需求清单 → 走这条路径。**不要去检索 GitHub，只对一个仓库做深度取证。**

### 第一步：先把需求清单固化成「编号 + 权重」表

**不要一边查一边回忆需求。** 从历史记忆里把约束抄成表格，带权重：

| 权重 | 约束 |
|---|---|
| 必须 | … |
| 最好 | … |
| 场景 | … |
| 隐含 | … |

**「隐含」这一行最容易被漏掉，但它往往是唯一的失败项。** 实测：用户原话「我不会敲命令」在十四轮里一直是隐含约束，本轮首次成为判定项，结果它是七条里唯一不符合的。

**固化后不要中途改。** 判定表要能一条条对回去。

### 第二步：逐条判定，每条都要给「证据出处」

**禁止写「符合」而不给出处。** 判定格式：

```
### 需求 N：xxx —— ✅/⚠️/❌
**我的需求原文**：…
**WeKnora 的机制**：…
**证据**：文件路径 + 行号 + 原文引用
**判定依据**：…
**边界/局限**：…
```

**「边界」这一栏是关键。** 判「符合」不等于没有条件。实测：

- 记忆隔离判 ✅，但边界是「粒度是空间×人，**不是**空间×智能体×人」——如果不写清，用户按错误理解去用就会踩坑
- 数据安全判 ✅，但边界是「字段级加密 ≠ 全库加密，对话和文档明文落库，安全靠机器是你的」——不写清就是误导

### 第三步：三个高价值探针（按性价比排序）

**探针一：双形态产品的对比表**

如果产品有 Lite/标准、免费/企业等双形态，**去读它的对比表**（如 `docs/LITE.md`）。那张表就是官方在告诉你「哪些需求不能同时满足」。

实测价值最高的一次：WeKnora 的 `docs/LITE.md` 直接暴露了「多空间隔离」与「零依赖部署」互斥 —— 这是整份报告最重要的发现，而它藏在一个 16 行的表格里。

**探针二：配额/上限常量的注释**

**常量值本身没意义，注释里的理由才是证据。** 实测：

```go
// Picked to comfortably cover legitimate "personal + a couple of side-projects" use
// while blunting drive-by abuse against POST /tenants (see CreateTenant).
const defaultMaxOwnedTenantsPerUser = 10
```

注释直接写出了**目标用户画像**，比任何产品文档都有说服力。

**探针三：i18n 术语测试 / 命名治理类 CI 测试**

如果产品有「术语治理」测试（如强制禁用某个词），那是**概念地位的强证据**。实测 WeKnora 有一条测试强制所有面向用户的文案禁用「租户/tenant」，必须叫「工作区/workspace」：

```js
const localeChecks = [
  { name: 'zh-CN', locale: zhCN, forbidden: /租户/ },
  { name: 'en-US', locale: enUS, forbidden: /\btenants?\b/i },
]
test('user-facing locale values use workspace terminology', () => { ... })
```

**底层表叫 `tenants`，产品层刻意叫「工作空间」，还专门写测试守住 —— 说明这是一等公民概念，不是顺带提的功能。**

**探针四：三层存储识别（做「知识库 / 提示词管理」类维度必读）**

**同一个产品可能有 2–3 套互相独立的文件/知识存储，作用域各不相同。不能假设「上传了就能搜」。**

实测 LobeHub 有三层，官方提示词原文就是最好的入口（`builtin-tool-knowledge-base/src/systemRole.ts`）：

```
Most user files live in the resource library, NOT in knowledge bases
Agent Documents only manages the agent's own notes/skills, not the user's uploads
they live in a separate store
```

| 层 | 是什么 | 能不能语义搜索 | 作用域 |
|---|---|---|---|
| 资源库（Resource Library） | 上传文件的**默认去处** | **不能**（`listFiles` 无需预索引，只是列表） | 工作区 |
| 知识库（Knowledge Base） | **必须手动组织**进去 | 能（`searchKnowledgeBase`） | 工作区，所有角色可浏览 |
| 助理文稿（Agent Documents） | 助理私有笔记/技能 | 助理内可读 | **助理级 / 当前话题级**（`scope?: 'agent' \| 'currentTopic'`） |

**这个探针的通用价值**：**「上传」和「可检索」是两个动作。** 新手最容易在「上传完以为就能问」这里翻车。报告里必须写成一句可执行的话：**上传到资源库 ≠ 可语义搜索，要再手工建知识库并导入。**

**★ 附带洞察（比机制本身更有价值）**：LobeHub 的记忆是全局的（8 张表只有 `userId`），但助理文稿有 `scope`。合起来看，官方其实在表达一个设计观：

> **「你是谁」应该全局（记忆），「这个项目怎么做」应该有作用域（文稿）。**

**这可以用来反推用户的真实需求。** 实测：用户的需求 2「工作区级记忆隔离」，深挖后可能真正要的是「隔离项目知识」而不是「隔离人格记忆」——后者用文稿的 `scope` 就能给到。**遇到「记忆隔离」类需求时，先问：要隔离的是「人格」还是「项目知识」？**

### 第四步：「未发布功能」的三方核查法

产品文档里说的功能，可能还没发布。**三方对照**：

| 来源 | 可信度 | 说明 |
|---|---|---|
| CHANGELOG / README | 低（宣传） | 会说「已发布」 |
| ROADMAP 的勾选状态 | 中（自认） | `[ ]` 就是官方承认未完成 |
| **Release 产物 + 打包脚本** | **高（事实）** | 有没有安装包、支持哪些平台 |

实测：WeKnora 桌面应用三方结果完全冲突 —— 文档齐全、CI 里有 Windows amd64 构建任务，但 tag 触发被注释掉、Release 无产物、只有 `package-mac-app.sh`（macOS）。

**注意**：ROADMAP 的可信度要**用同文件里已勾选项反证**。如果同一个 ROADMAP 里别的章节有 `[x]`，说明这不是没维护的文档，未勾选是真实的未完成。

**★ 反向应用：发布了但停更了（本轮新增）**

原方法是查「宣传了但没发布」。**但还有一种相反的情况：「发布了，但停更了」。**

**标准动作**：查完 Release 产物后，**还要算「最后 Release 距今天数」，并与主项目对比**。

实测（Open WebUI 桌面应用）：

| 项 | 值 |
|---|---|
| `open-webui/desktop` 最后 Release | v0.0.20，**2026-05-06** |
| 距今 | **135 天** |
| Windows 安装包下载量 | `open-webui-x64-setup.exe` **100,792 次** |
| 主项目最后推送 | 2026-09-18（**0 天前**） |

**结论**：桌面应用**真实可用**（10 万+ 下载，不是「有代码没发布」），**但停更 4.5 个月，而主项目在高速迭代** → **兼容性风险实在**。

**所以「有 Release 产物」要分三种情况写**：
1. 有产物 + 在维护 → ✅ 可用
2. **有产物 + 停更 → ⚠️ 可用但兼容性存疑**（本轮遇到的情况）
3. 无产物 + 有代码 → ❌ 未发布

**另一个细节**：卫星仓库的许可可能与主项目不同。实测 `open-webui/desktop` 是 **AGPL-3.0**，而主项目是 Open WebUI License（NOASSERTION）。**混用多个仓库时，每个都要单独查许可。**

### 第五步：结论要落到「用户该做什么决定」

判定表给完，必须回答：

1. **如果条件 A 成立 → 选它；如果条件 B 成立 → 选替代品。** 不要给「都行」的结论。
2. **明确列出「这个结论依赖的前提」。** 实测：WeKnora 的结论依赖「用户能找到人帮忙部署一次」，前提不成立则结论反转 —— 必须写出来。
3. **列出「我可能高估/低估的地方」。** 未实测的部分要诚实标注。

### 第六步（最重要）：区分「一次性门槛」与「永久性门槛」

**这是本轮唯一改变结论方向的方法。**

用户说「我不会敲命令」时，不要直接判死刑。拆开看：

- **部署**需要敲命令 → 一次性（低频）
- **日常使用**需要敲命令吗？→ 逐项验证 UI 覆盖

实测 WeKnora 的 UI 覆盖：知识库 / 文档上传 / 对话 / 智能体 / 记忆开关 / 搜索配置 / 模型配置 **全部有页面**。所以「不会敲命令」的真实含义是「不能自己完成安装」，不是「不能使用产品」。

**通用问法**：遇到「用户能力不足」类约束，先问 —— **这个能力是每次都要用，还是只用一次？**

**但要诚实标注例外**：版本升级也需要命令（`docker compose pull` + `up -d`），所以准确说是「低频」而非严格的「一次性」。这个漏洞要在报告里点出来，不能藏。

### 第七步：订阅额度换算（做「以 X 模型为基准算额度」类任务必读）

**用户指定计价基准时（如「以 deepseek v4 flash 为基准」），要输出的是「可比较的数字」，不是「一堆 credits」。** 五步走：

**① 先把计价基准对齐到实际模型名**

**平台上的模型名常常是别名，且会重定向。** 实测 LobeHub：`V4 Flash` / `V4 Flash Vision Exp` / `V4 Pro` **三个名字全部重定向到 `V4.1 Flash`**，价格一致。用户说的「v4 flash」实际对应 V4.1 Flash。**不核对这一步，后面全算错。**

**② 取平台侧的 credits 单价（输入/输出分开）**

实测 LobeHub × DeepSeek V4.1 Flash：输入 **0.33M credits / 1M tokens**，输出 **1.32M credits / 1M tokens**。注意**输入输出单价不同**，必须分开，不能用平均价。

**③ 用官方价反推「加价率」**

| 步骤 | 做法 |
|---|---|
| 取官方价 | 模型厂商官网价目表（注意**分时/峰谷**：DeepSeek 空闲输入缓存未命中 1 元/M、输出 4 元/M，高峰翻倍） |
| 换算 | 按当日汇率折美元（查中间价，不要用记忆里的汇率） |
| 算单价 | `credits 单价 ÷ 1,000,000 × 档位月费 ÷ 档位 credits` |
| 加价率 | `平台单价 ÷ 官方单价` |

实测结果：**2.54×–5.75×**（Ultimate 年付最便宜 2.54×，Starter 月付最贵 5.75×）。

**④ 分解「平台费 vs 模型费」——这一步最有说服力**

用官方估算的消息数反推每条成本，再乘消息数得模型成本，与月费相减得平台费：

| 档位 | 月费 | 消息数 | 模型成本 | 平台费 | 平台费占比 |
|---|---|---|---|---|---|
| Starter（月付） | $12.9 | 3,200 | $2.25 | $10.65 | **83%** |
| Ultimate（年付） | $39.9 | 22,300 | $15.65 | $24.25 | **61%** |

**结论一句话：「订阅费里 61–83% 是平台费，模型钱只占 17–39%。」** 这比列一堆 credits 数字有用得多。

**⑤ 必查三个「限制解除」的边界**

用户最容易误解的就是「我买了/我 BYOK 了，是不是就没限制了」。实测：

| 问题 | LobeHub 的答案 | 证据 |
|---|---|---|
| BYOK 能解除所有限制吗？ | **只解消息数，不解文件/向量存储配额** | 配额按档位算，与模型来源无关 |
| 自托管版有额度吗？ | **没有，完全不受限** | `spendGate.ts` 原文 `Default: no spend accounting, so nothing is ever refused`；`getSubscriptionPlan()` 是桩，永远返回 `Plans.Free` |
| 「消息数」是精确值吗？ | **官方承认是估算** | `PlanLimitPricingBasis = 'approximate' \| 'estimated' \| 'exact' \| 'unknown'` |

**⑥ 硬要求：所有算术必须用脚本二次复核**

按本方法论「从命令输出抄下来的数字都要用第二种方法复核」的规矩，额度换算**必须**写脚本验算一遍。本轮验算项：年付等效月价、credits 单价、credits-per-message 口径、官方价换算、加价率、成本分解 —— **六项全部通过**。

**⑦ 两个数据源陷阱**

- **定价页是实时数据源，文档站可能滞后数代。** 实测 LobeHub 文档站还在讲 `GPT-4.1` / `Claude 3.7 Sonnet` / `DeepSeek V3` / `R1`，而定价页已是 `GPT-6 Astra` / `Claude Fable 5.1` / `DeepSeek V4.1 Flash`。**额度数字一律以实时定价页为准，文档站只用于提取机制说明。**
- **同一页两套价格不矛盾，可能是年付等效月价。** 「$9.9/Month」与「$12.9 Month / $118.8 Year」并存 → `118.8 ÷ 12 = 9.9`。**看到价格对不上先算除法，别急着报「官方数据冲突」。**

**⑧ 档位枚举里可能有「未在售」的档**

实测 LobeHub 的 `Plans` 枚举有 5 档（Free / Hobby / Premium / Starter / Ultimate），但 **Hobby 未在售**。**枚举值 ≠ 可购买档位**，报告里要区分。

### 第八步：隔离单位横向对齐（做多产品对照必读）

**这是本轮最重要的新方法，它解释了「为什么我前几轮反复换首选」。**

**核心动作**：调研多个产品时，**把每个产品的「同一类抽象」（工作区 / 记忆 / 知识库 / 助手）的数据层实现并列成一张表**，用同一把尺子量。

**为什么必须做**：同一个词在不同产品里指代**完全不同的东西**。不做这张表，就会把「A 的工作区」和「B 的工作区」当成同一个东西来比 —— 结论必然反复摇摆。

#### ★「工作空间」三问判据（可复用到任何「隔离」类判断）

看到 UI 上的「工作空间 / Workspace / 工作区」，**回源码确认三件事**：

| # | 问题 | 判定 |
|---|---|---|
| 1 | **它在数据库里有表吗？** | 没有表 → **不是边界**，只是 UI 区块名或权限命名空间 |
| 2 | **它有隔离键吗？** | 有表但表里只有 `user_id` → **不是独立边界** |
| 3 | **记忆/对话/知识库的查询语句里，有没有按它过滤？** | 没有 → **隔离不成立** |

**三个都过，才是真正的工作区隔离。**

**实测回测四个产品（这张表本身就是报告的核心结论）**：

| 层次 | 产品 | 数据层实现 | 是隔离边界吗 | 记忆按它分吗 |
|---|---|---|---|---|
| **真边界** | WeKnora | `tenants` 表 + `tenant_members` 多对多 + CI 测试守命名 | ✅ 是 | ✅ **是** |
| **部分边界** | LobeHub | Workspace 真表 + 三角色矩阵 + 订阅绑定 | ✅ 是 | ❌ **不是** |
| **路径** | WorkBuddy | `workspaces` 表只有 `path` + `last_opened_at` | ⚠️ 文件系统路径 | ⚠️ 仅 Layer3 |
| **UI 区块名** | Open WebUI | **没有表**，只有权限前缀 `workspace.{models,knowledge,prompts,tools,skills}` | ❌ **不是** | ❌ 不是 |

**Open WebUI 的陷阱最隐蔽**：中文 i18n 里明明白白写着 `"Workspace": "工作空间"`，但全部 38 张表里**连 `group` 都有表，`workspace` 没有**。而且文档里反复出现「Workspace > Models > Edit」这种路径，让人以为是「工作区里的模型」，实际是「个人资源管理区里的自定义模型」。

#### 配套动作：官方文档搜作用域关键词

**做隔离类判断时，先去官方文档搜这几个词**：`scoped` / `per-` / `belongs to` / `tied to` / `isolated`。

实测收获：Open WebUI 官方记忆文档一句 **`Memories are stored locally in your Open WebUI database and are scoped to your user account.`** —— **比读十处源码都直接。**

**这是「官方文档明说」这一类证据的价值**：它不是实现细节，是**产品对自己作用域的正式声明**。

#### 配套动作：把「该产品有哪些抽象」也列成表

不要只列「工作区」。把该产品**全部的组织层抽象**列出来，标清每个的作用域：

以 Open WebUI 为例（一次列全，避免遗漏）：

| 抽象 | 表 | 作用域 | 是什么 |
|---|---|---|---|
| 用户 | `user` | — | **真正的隔离边界** |
| 组 | `group` + `group_member` | 跨用户 | ACL 主体 |
| 文件夹 | `folder` | 用户内 | 对话组织树 |
| 频道 | `channel` + `channel_member` | 多用户 | 协作空间 |
| 自定义模型 | `model` | 用户 / 可授权 | **「面具」**（含知识库绑定 + 能力开关） |
| 知识库 | `knowledge` + `access_grant` | 用户 / 可授权给组 | 独立实体 |
| 提示词 | `prompt` | 用户 / 可授权 | slash command（有版本历史） |
| 记忆 | `memory` | **用户** | 只有 `user_id` |
| 笔记 | `note` | 用户 | 富文本 |
| 自动化 | `automation` | 用户 + 文件夹 | RRULE 定时 |

**列全之后，「有没有工作区」这个问题就变成了「哪一层能承担工作区的职责」** —— 这比直接问「支持吗」有用得多。

---

## 技术避坑：判断演进路线与产品定位（做「X 是否也走 Y 的路线」类任务必读）

**判据**：用户问的是**「它往哪走」**，不是「它有什么」。典型问题：「X 是否也和 Y 一样走 agent／通用工作台路线」「X 还是停滞在 chat 吗」「X 的定位是什么」。

**核心原则：不要用功能清单回答路线问题。**

功能清单会骗人，而且是**双向**骗人：

| 骗法 | 表现 | 案例 |
|---|---|---|
| **实现超前** | 代码早就是新形态了，文案还停在旧形态 | LibreChat：GitHub description 仍是 `Enhanced ChatGPT Clone`，README 仍说 `self-hosted AI chat platform`，**但代码是完整 agent harness（170 个 agent 模块 + 18 项能力 + 13 个租户隔离中间件）** |
| **文案超前** | 品牌重定位了，实现没跟上 | LobeHub 自称 `Chief Agent Operator`／「下一代 Agent harness」，**但 8 张记忆表只有 `userId`** |

**所以「路线定位」必须用三样东西交叉验证，单看任何一个都会误判。**

### 证据一：代码骨架（不是功能清单）

**看什么**：数据模型 + 运行时模块 + 能力开关的**权威清单**。

| 看哪 | 为什么 |
|---|---|
| **数据模型的字段** | 字段是设计意图最硬的证据。`agent` 表里有 `recursion_limit` / `edges` / `git_identity` / `memory_scope` → 产品把「agent 会循环、会组队、会写代码、有独立记忆」当作默认事实 |
| **运行时模块的目录结构** | 目录名就是能力地图。`agents/{checkpoints,hitl,steering,triggers,hooks,failures,subagents}` → 这不是「加了个 agent 功能」 |
| **能力开关的示例配置** | **不要数 README，去读 `*.example.yaml` / `config.example.*`**。LibreChat 的 `librechat.example.yaml` 里有一行 `capabilities: [...]`，14 项默认 + 4 项 opt-in —— 这是产品对自己能力的正式声明 |
| **字段的注释** | 注释里的「为什么」比字段名值钱。例：`/** Memory partition: 'agent' isolates memories per (user, agent); default shared pool */` |

**⚠️ 不要数文件数当成熟度**。文件多可能是半成品堆积（LibreChat 的 `agents/` 里混着 `legacy.ts` / `migration.ts` / `harvest.ts` / `fading.ts`，没读过的不要当能力）。**数量只用来判断「投入规模」，判断「成熟度」要看测试。**

**测试投入是成熟度的更好指标**：

| 信号 | 例子 |
|---|---|
| 测试文件占比 | LibreChat `packages/api/src/agents`：154 测试 / 324 总数 = **47.5%** |
| **属性测试**（而非断言测试） | `@antithesishq/bombadil`，规格名 `hitl-lifecycle` / `steering-lifecycle` |
| **覆盖率守门测试** | `tenantIsolation.coverage.spec.ts`：任何一个带 `tenantId` 的模型漏挂隔离插件，测试就红 |
| **性能/可访问性门禁** | `npm run lighthouse`（CI 加 250ms/查询）、`@axe-core/playwright` |
| **为某个状态机专门写 e2e** | HITL 与 Steering 各有一份生命周期规格 |

### 证据二：时间线（「有」不等于「早就在做」）

**做法：抓 GitHub Release 全量，按时间正序扫关键词首次出现。**

```python
# 分页抓 release（per_page=100），注意有的仓库总 release 数 < 200，page2 会返 0
d = json.load(open('lc_rel.json'))
d = sorted(d, key=lambda r: r['published_at'])       # 正序
found = {}
for r in d:
    body = (r.get('body') or '')
    for k in ['agent', 'MCP', 'Subagent', 'Skill']:
        if k.lower() in body.lower() and k not in found:
            found[k] = (r['tag_name'], r['published_at'][:10])
```

**实测收获（LibreChat）**：

```
agent    首次出现于 v0.3.3    (2023-04-21)   ← 噪声，只是词出现过
MCP      首次出现于 v0.7.6    (2024-12-20)   ← 真转折点
Subagent 首次出现于 v0.8.6-rc1 (2026-05-13)
```

**然后必须读转折点那个版本的 body 原文**，确认是「新功能」还是「顺手提了一句」：

> ### 🤖 Agents
> - Introducing LibreChat's **No-Code Agentic Framework**

**`Introducing` / `New` 这类动词是判据。** 只有 `Introducing` 才是转折点。

**交叉验证技巧：把外部包的创建日期和 Release 日期对齐。** 实测：`@librechat/agents` 的 npm 首发是 **2024-08-28**，而 `v0.7.5-rc1` 发布于 **2024-08-27** —— **同一天**，说明这个 RC 就是为 agent 运行时铺路的。

**⚠️ Release body 里的关键词扫描会有噪声**（`agent` 在 v0.3.3 就出现，但那是「user agent」之类）。**必须回读原文确认。**

### 证据三：组织事实（决定它对谁负责）

**路线问题有一半答案不在代码里，在「谁拥有它」里。**

| 要查什么 | 为什么 |
|---|---|
| **是否被收购 / 合并** | 收购方的战略叙事会改写路线图。LibreChat 被 ClickHouse 收购 → 官方定位从「chat platform」变为「**AI agent framework**」+「**Agentic Data Stack**」 |
| **收购方的整合先例** | 同一家收购方的历史 playbook 会重演。ClickHouse 的 `PeerDB`、`HyperDX`（→ 变成 ClickStack 的 UX）说明**「保持独立」的承诺要打折看** |
| **公开的规模数据** | 客户案例比功能清单更能证明成熟度。Shopify 用 30+ MCP server / 数千 agent；ClickHouse 内部用它处理 70% 数仓查询 |
| **融资 / 商业化状态** | 决定它靠什么活：订阅（要圈用户）vs 企业服务（要建地基） |

**查法**：
- 官网首页 banner（**banner 常常是收购/重大消息的第一落点**，比 About 页新）
- 官方博客 / 新闻稿（搜 `<产品名> acquired`）
- 官网 `<title>` / `meta description` 与 GitHub description **对比**（三者不一致本身就是结论）

**⚠️ 收购公告要读「What's next」那一节，而不是「我们很兴奋」那一节。** 实测 ClickHouse 公告的路线图原文：

> Think of it as a **'happy path' for agentic analytics** in LibreChat. This will include:
> - Seamless integration of the LibreChat experience alongside your ClickHouse Cloud instances
> - Extended support for **data visualizations**
> - **OAuth, end-to-end user identification, security, and governance schemes**
> - **Tailored context providing (aka. semantic layer)**

**这四行才是路线，前面都是客套。**

### 配套动作一：仓库内的 PoC / PLAN 文档是「方向」的最佳证据

**开源仓库里常有一份「还没进主干的能力」的规划文档。** 它比任何对外文案都直接，因为**它是写给自己人看的**。

**找法**：`find . -iname "*PLAN*" -o -iname "*README*"` 后 grep `track` / `PoC` / `worktree` / `migration`。

**实测收获（LibreChat `search/README.md`）**：

> # Search stack PoC infrastructure (**Track 1**)
> Docker Compose stack for the **new chat-search architecture** in `PLAN.md`
> (worktree `postgres-ferretdb-clickhouse-rag-b6bc87`, "Infrastructure" track).
> Stands up four services: `ferretdb-postgres`, `ferretdb`, `chat_search_db`, `clickhouse`.
> Table DDL (`chat_search.documents/embeddings/**outbox**/watermark`) is **track 4**'s job

**这一份文档同时给出了四个信号**：
1. **收购方的技术（ClickHouse）已经在仓库里跑起来了** → 收购不是纸面叙事
2. **有 `PLAN.md` 和多 track 计划** → 内部有分轨推进
3. **`outbox` 又出现**（触发投递也用 outbox）→ **团队级的一致工程习惯**
4. `ferretdb`（MongoDB 协议兼容层）出现 → **在评估存储引擎替换**

**⚠️ 必须标注这是「方向证据」不是「现状能力」**（原文自称 `infra only - no migrations, no app code`）。

### 配套动作二：`CLAUDE.md` / `AGENTS.md` 是项目自述（被低估）

**2025 年之后的仓库常有一份给 AI 编码 agent 的指令文件。它的「Project Overview」章节是一份高质量的架构自述**，比 README 的技术部分更准（因为写给它自己用）。

**实测收获（LibreChat `CLAUDE.md`）**：

> | Workspace | Language | Side | Dependency | Purpose |
> | `/api` | JS (legacy) | Backend | `packages/api`, `packages/data-schemas`, `packages/data-provider`, `@librechat/agents` | Express server — **minimize changes here** |
> | `/packages/api` | **TypeScript** | Backend | ... | **New backend code lives here** |
>
> The source code for `@librechat/agents` (**major backend dependency, same team**) lives at `<...>`

**三个收获**：
1. **架构方向明确**（`/api` 是 legacy，新代码去 `/packages/api`）
2. **承认了外部依赖的规模**（`major backend dependency`）
3. **给出了 agent 运行时的源码地址** → 直接指向「壳开源核闭源」的检查

**⚠️ 但这类文件里的路径会过时。** 实测它指向 `github.com/danny-avila/agents`，而该地址 **301 重定向**到 `github.com/LibreChat-AI/agents`。**凡是文档里给的地址，都要实际访问一次。**

### 配套动作三：路线问题要给出「两家是不是同一个目的地」

用户问「X 是否**也和 Y 一样**」，**答案要拆成两层，不能只答一层**：

| 层次 | 问法 | 实测答案（LibreChat vs LobeHub） |
|---|---|---|
| **方向** | 都在从 chat 走向 agent 吗？ | **一样** |
| **目的地** | 走的是同一条路线吗？ | **不一样** —— LobeHub 把 agent 当**产品**（应用商店，卖专家）；LibreChat 把 agent 当**基础设施**（运行时，卖地基） |

**判据（怎么区分「产品」和「基础设施」）**：

| 维度 | 当产品 | 当基础设施 |
|---|---|---|
| 触发来源 | 用户开对话 | 用户 **或** 定时器 **或** webhook **或** MCP **或** 内部事件 |
| 执行边界 | 一次对话回合 | 一次**投递**，可能跨进程/跨副本/跨重启 |
| 失败语义 | 报错给用户 | **至少一次投递 + 退避重试 + 死信 + 重入队** |
| 状态 | 对话历史 | **checkpoint** + **补偿动作**（`action_compensated` / `history_repaired`） |
| 收入来源 | 订阅（模型加价） | 企业服务 / 云集成（软件本体免费） |

**最快的判据：去看它的数据模型里有没有「分布式系统的字段」。** 实测 `triggerDelivery` 有：

```ts
certainty: 'definite' | 'ambiguous'      // 承认「失败有时无法判定是否已生效」
outcome:   'succeeded' | 'retry' | 'dead' // 死信
resolution: 'checkpoint_verified' | 'action_compensated' | 'history_repaired'  // saga 补偿
claimToken / configRevision               // fencing token + 配置版本
```

**一个「给人用的工作台」不会有这些字段。**

### 配套动作四：对称取证不能省（否则结论只有一半）

**「X 和 Y 的路线异同」是双向问题，必须两边都取证。**

**实测教训**：本轮取证 LibreChat 时发现它有 `subagents` / `schedules` / `hitl` / `steering` / `chain` / `observability` 六项能力，但**前序对 LobeHub 的取证只覆盖了功能/跨平台/知识库/提示词管理/订阅额度五个维度**，没查这六项。

**处置**：在对照表里把这六项**标为「未验证」，不能写成 LobeHub 的缺失**。并在报告里明确指出「这是本报告最大的证据缺口，要回答完整版必须再补一轮对称取证」。

**判据**：**对照表里「未验证」超过 3 项时，必须在报告里显式声明结论的完整度不足。**

### 与「验证候选是否适配」（类型二）的关系

| | 类型二（验证适配） | 类型三（判断路线） |
|---|---|---|
| 问题 | 「它能满足我的需求吗」 | 「它往哪走」 |
| 主证据 | **逐条需求的证据出处** | **代码骨架 + 时间线 + 组织事实** |
| 关键产出 | 需求判定表（✅/⚠️/❌） | **转折点 + 目的地判断** |
| 必须包含 | 证据索引 + 未验证事项 | **定位文案 vs 实现 的错位分析** |
| 共同的坑 | 都不要信 README 的自述 | 同 |

**两类可以叠加**：用户常先问「X 是否符合我的需求」（类型二），再问「X 和 Y 的路线异同」（类型三）。**叠加时，类型三的对照表要复用类型二已取证的数据，避免重复劳动。**

---

## 技术避坑：复核前序排除理由（做「X 是不是更好的替代」类任务必读）

**判据**：用户回头问一个**已经评估过、且已被排除**的候选。

**核心认知：产品会演进，前序的排除理由会过期。**

**实测教训（本方法论最贵的一课）**：OpenClaw 在第 11 轮是首选，第 12 轮因「配置驱动、全 CLI、与新手友好直接冲突」被排除。第 26 轮复核发现——**它有完整的浏览器 GUI**（`Control UI`：建 Agent、管 roster、改权限、配 MCP、看记忆全在里面）。**前序的排除理由是错的，而它错误地影响了后续十几轮的结论。**

**所以类型四的第一步不是「重新调研」，而是「逐条验证排除理由」。**

### 第一步：把前序的排除理由变成一张可验证的清单

去读前序报告 / 记忆文件，把「为什么排除它」写成**可验证的断言**，不要写成印象。

| 坏写法（不可验证） | 好写法（可验证） |
|---|---|
| 「配置太复杂」 | 「建 Agent / 绑通道 / 设文件权限需要执行 CLI 命令」 |
| 「知识库不行」 | 「RAG 需要自己搭技能，没有内建知识库功能」 |
| 「许可是问题」 | 「LICENSE 文件未核对，商用前必须自查」 |

### 第二步：给每条理由定性（三类，报告里必须分开）

| 定性 | 含义 | 处置 |
|---|---|---|
| **A. 当时就错** | 前序取证不到位，结论本身就是错的 | 直接推翻，并说明前序错在哪（**要公开修正**） |
| **B. 当时对，产品变了** | 产品确实演进过 | 引用新版证据，标注版本号与日期 |
| **C. 仍然成立** | 排除理由有效 | 保留排除结论 |

**实测（OpenClaw，第 12 轮 → 第 26 轮）**：

| 前序理由 | 定性 | 证据 |
|---|---|---|
| 「全部敲 CLI」 | **A. 当时就错** | `docs.openclaw.ai/web/control-ui.md`：`Choose New agent in the sidebar` / `Manage agents opens /settings/agents` / `chat composer's Execution permissions menu` |
| 「知识库非内建」 | **B. 产品变了** | bundled `memory-wiki` 插件 + `vault.scope: 'agent'` |
| 「许可证未确认」 | **B. 产品变了**（现在是 MIT + 501(c)(3) 基金会） | `LICENSE` 文件 |
| 「文件系统级隔离最硬」 | **A. 当时就错**（前序过度乐观） | `Sandboxing is off by default` + `This is not a perfect security boundary` |
| 「60 天破 25 万 star，已超 React 成 GitHub 星标第一」 | **A. 当时就错**（采信第三方文章未验证） | API 实测：freeCodeCamp 455,708 > OpenClaw 390,025 |

**五条里三条是「当时就错」。** 这说明：**前序结论越是被第三方文章喂出来的，越要重新验证。**

### 第三步：四个必须重新取证的项（排除理由最常出错的地方）

| 项 | 为什么容易过期 | 怎么查 |
|---|---|---|
| **许可证** | 项目常在中途改许可，或从个人转为基金会 | **读 `LICENSE` 文件本身**。⚠️ GitHub API 的 `license.spdx_id` 不可信：OpenClaw 实测 API 返回 `NOASSERTION`，文件里是 **MIT**（因为版权行写法不标准，licensee 工具识别失败） |
| **GUI 有无** | 「只有 CLI」是最常见的过时结论 | 抓文档站，搜 `Control UI` / `Dashboard` / `Web UI` / `Desktop`；**不要只看 README 的 Install 章节**（那里永远只有命令行） |
| **知识库有无** | 常从「要靠插件搭」变成「官方 bundled plugin」 | 抓文档站搜 `wiki` / `knowledge base` / `embedding`；**注意区分 bundled plugin（官方内置）和社区技能** |
| **隔离强度** | 前序容易把「设计意图」当成「默认行为」 | 搜 `default` / `off by default` / `not a perfect` / `experimental` 这类**限定词**。**产品宣传隔离能力时用的是最强的配置，默认值往往弱得多** |

**判据：产品文档里凡是出现「X is off by default」「not a perfect security boundary」「is experimental」「untested on <平台>」的句子，都要原样引用进报告。** 这些是官方自己给的折扣。

### 第四步（最重要）：判定「隔离」的语义 —— 防串味 ≠ 防对抗

**这是决定隔离方案能不能用的分水岭，而前序经常把两者混为一谈。**

| | **隔离**（防串味） | **对抗隔离**（防恶意租户） |
|---|---|---|
| 问题 | 「数据不该混」 | 「防止 A 主动越权读 B」 |
| 典型场景 | 代客户操作，不能把 A 的信息带出来 | 多租户 SaaS，租户之间互相敌对 |
| 产品给什么 | **一个进程内多工作区**（多 Agent / 多 Workspace） | **每个租户一个进程/容器/机器** |
| 是否违背「单账户」 | ✅ 不违背 | ❌ **必然违背**（多实例） |

**实测：OpenClaw 官方自己划了这条线**（`start/teams.md`）：

> A gateway is **one trust domain**. ... session ownership, presence, and roles are **collaboration guardrails inside the boundary, not isolation between adversaries.**
> If you need to serve **mutually untrusted people or organizations**, run **one gateway per tenant** instead.

**所以拿到任何「多租户」方案，先问一句：用户要的是防串味，还是防对抗？**
- 防串味 → 多工作区方案就够，**不要被「必须多实例」的说法吓退**
- 防对抗 → 承认它必然违背「单账户」约束，让用户自己权衡

**配套判据：隔离是逻辑的还是物理的**

| | 逻辑隔离 | 物理隔离 |
|---|---|---|
| 实现 | 同一数据库 + 查询层过滤（`tenantId` / `agentId`） | 独立目录 + 独立数据库文件 |
| 案例 | LibreChat（13 个查询中间件 + 覆盖率守门测试） | OpenClaw（独立 `agentDir` + 独立 SQLite） |
| 失效模式 | **漏一处过滤 → 静默串味** | **路径逃逸**（绝对路径可达主机其他位置） |
| 怎么防 | 覆盖率守门测试 | 开沙箱 + `workspaceAccess: none` |
| 跨工作区共享 | 天然容易（去掉过滤） | **必须显式配路径** |

**两者都是有诚意的方案，只是失效模式不同。报告里要写清是哪一种，因为「怎么防它失效」完全不同。**

### 第五步：横向扫描的纪律（回答「还有更好的吗」）

**这一步最容易翻车，因为搜索结果 90% 是 SEO 榜单。**

| 纪律 | 实测教训 |
|---|---|
| **第三方榜单只能用来「发现名字」，不能用来「确认事实」** | 某篇「12 Best OpenClaw Alternatives」把 `nanoclaw` 写成 `nanoclaw/nanoclaw`（实际 `nanocoai/nanoclaw`）、`zeroclaw` 写成 `zeroclaw/zeroclaw`（实际 `zeroclaw-labs/zeroclaw`）、`moltis` 写成 `moltis/moltis`（实际 `moltis-org/moltis`）—— **三个路径全部 404** |
| **文章提到的产品可能根本不存在** | 同一篇文章列的 **「Grip AI」**，用 GitHub 搜索 API 查只返回 1 个 2024 年的 3-star 无关项目 |
| **Star 数不等于排名，必须对照头部仓库** | 前序说 OpenClaw「已超 React 成 GitHub 星标第一」；实测 freeCodeCamp **455,708** > OpenClaw **390,025** |
| **「未发现」比「不存在」诚实** | 扫描不到就写「本轮未发现新的重量级候选」，**不要写「不存在」** |

**搜索后必须做的动作**：把每个名字拿去 `api.github.com/search/repositories?q=<name>+in:name` 验证，拿到真实的 `full_name` / `stargazers_count` / `created_at` / `pushed_at` / `license`。

### 与前三类的关系

| | 类型一（找替代） | 类型二（验证适配） | 类型三（判断路线） | **类型四（复核排除）** |
|---|---|---|---|---|
| 问题 | 「有哪些」 | 「它能满足吗」 | 「它往哪走」 | **「当初排除它对吗」** |
| 起点 | 空白 | 一个候选 + 需求清单 | 一个候选 + 一个参照物 | **前序的排除理由清单** |
| 主证据 | GitHub 检索 | 逐条需求的出处 | 代码骨架 + 时间线 + 组织事实 | **排除理由逐条重验 + 变化点** |
| 关键产出 | 候选长名单 | 需求判定表 | 转折点 + 目的地 | **「当时就错 / 产品变了 / 仍成立」三分表** |
| 特有风险 | 漏候选 | 采信 README | 单边取证 | **沿用前序的错，把错当既定事实** |

**类型四最常见的失败**：直接去查新功能，忘了问「前序到底为什么排除它」。**结果查了一堆新特性，却没能回答「现在能不能翻案」——因为不知道当初的罪名是什么。**

---

## 技术避坑：新候选深度调研（做「调研这几个仓库」类任务必读）

**适用**：用户一次性给出一批（2–4 个）新候选仓库，要求调研；常附**来源优先级**约束（官网 → 官方论坛 → 英文 blog → 社区论坛），并常要求**翻译成中文**。

### 第一步：把「来源优先级」当成一项任务要求来执行，而不是建议

用户说「优先官网 / 官方论坛 / 英文 blog / Reddit / Discord」，就要**按这个顺序逐层取证，并在报告里显式标注每条的来源等级**。

建立一张来源表：

| 层级 | 来源 | 拿到什么 |
|---|---|---|
| ① 官网 | 产品官网 | 定位、定价、FAQ（**官方一手口径**） |
| ② 官方仓库 | README + LICENSE + 目录结构 | 功能清单、许可证、技术栈、架构 |
| ③ 官方文档 | `docs/` 或文档站 | 机制细节 |
| ④ 英文 blog | 技术媒体 / 独立分析 | 品类背景 |
| ⑤ 社区论坛 | **Hacker News / Reddit / Discord** | **真实评价、作者回复、争议** |
| ⑥ 中文来源 | CSDN / 知乎 / 微信公众号 | **仅作交叉参考，不采信其数据** |

**⚠️ 层级 ⑤ 是最容易被跳过、但信息密度最高的一层。** 尤其当产品作者亲自回复时，那些回复往往**推翻了产品官网的宣传**。

### 第二步：★ 核心判据 —— 「查不到」本身就是结论

**这是本类任务最重要的一条认知。**

用户要求「优先英文来源」，执行后极可能得到一个反直觉的结果：**这三个产品的英文社区讨论度是零。**

**处置方式（必须照做）**：

1. **不要含糊过去**（不写「相关讨论较少」这种话）
2. **把它写成一个显式的事实结论**：**「A 和 B 在英文社区零讨论，它们是中文社区驱动的项目」**
3. **给出旁证**，把「零结果」从「我没查到」升级为「客观事实」：
   - 社区入口的语言（企业微信群 / 飞书群 vs Discord）
   - 贡献者命名习惯
   - 鸣谢的社区（如 `LINUX DO`）
   - 引用的文章链接（微信公众号）
   - 用英文关键词搜索，返回的前 N 条是否全是中文站点
4. **在报告里单开一节说明这个局限**，并说明「本报告的英文一手证据集中在哪几项」

**判据：HN Algolia API 返回空体 = 零讨论，不是 API 故障。** 先确认是「0 条结果」还是「请求失败」，前者要当结论用。

### 第三步：HN 检索的完整姿势（社区论坛层的主力）

| 动作 | 方法 |
|---|---|
| **按关键词检索** | `https://hn.algolia.com/api/v1/search?query=<关键词>` |
| **按时间排序检索** | `.../search_by_date?query=<关键词>` |
| **取单个帖子的完整评论树** | `https://hn.algolia.com/api/v1/items/<objectID>` → 递归遍历 `children` |
| **Reddit** | ⚠️ **`https://www.reddit.com/search.json?q=...` 常返回 HTTP 403**（反爬）。降级方案：`WebSearch(query=..., allowed_domains=["reddit.com"])`；**若仍返回非 Reddit 内容，如实报告为「未检出」，不要编造** |

**⚠️ 空结果的处理**：`AionUi` / `ClawX` 在 HN 上返回 **0 条**，`json.load` 抛 `JSONDecodeError: Expecting value: line 1 column 1`。**这不是 API 坏了，是「零结果」**。加一个判定分支，把空体识别为「零讨论」。

### 第四步：★ 从 HN 帖里能挖出官网永远不会写的东西

**Show HN 帖（作者亲自在场）是本类任务的信息金矿。** 要专门提取这五类内容：

| 类型 | 为什么重要 | 实测案例（openwork） |
|---|---|---|
| **① 合规缺失** | 发布时可能没有许可证 | 作者被指出后几分钟才补上 MIT：`Oh damn thanks for flagging. I just added an MIT license.` |
| **② 作者自认短板** | **比任何第三方评价都可信** | `Yeah it is still too technical.` + 给出三条补救计划（预打包配置 / 内嵌 opencode / 去掉术语） |
| **③ 被质疑且未答的问题** | **未答本身就是风险信号** | `What's the security boundary here - there's no mention of a VM?` → **作者没回答** |
| **④ 社区对项目寿命的怀疑** | 判断「快克隆」风险 | `I ignore these things until they're 3-6 months old and still iterating.` |
| **⑤ 作者给出的「正确用法」** | 常与官网宣传不同 | 作者自己说正确做法是「**混合模式**：你在远程服务器装好，让非技术同事做一次性设置连过去」 |

**判据：作者自己的话 > 官网文案。** 官网是营销部门写的，HN 回复是工程师当场写的。

**⚠️ 反向使用「项目寿命怀疑」这条判据**：`browningstreet` 的检验条件是「3-6 个月且还在迭代」。**要拿这个条件去对照创建日期与最近推送日期** —— openwork 创建 2026-01-14、调研日 2026-09-18、当天还在推送 → **它通过了这个社区自设的检验**。**把「社区质疑」和「质疑是否已被证伪」一起报告，才是完整的。**

### 第五步：同族产品必须做「含母体」的四列对照

**这是本类任务最容易做错的地方。**

用户给了三个 GUI 封装产品，如果只做三列对照，结论会停留在「各有千秋」。

**正确做法：把「它们所封装/参照的母体产品」也加进来，做成四列。**

实测收益（AionUi / ClawX / openwork 三个都是 OpenClaw 生态产品）：

| 只做三列 | **加上母体（OpenClaw）后** |
|---|---|
| 三个都支持多 Agent | **发现三个的隔离能力全部弱于母体** |
| 各有取舍 | **发现规律：GUI 封装层为了降低门槛，主动放弃了隔离概念** |
| 结论：选一个 | **结论：它们不是替代关系，是不同层**（引擎 / 仪表盘 / 车库 / 分发网络） |

**提炼出的结构性洞察**（可复用于同类任务）：

> **「GUI 封装」为了降低门槛，通常做减法：**
> - 减掉隔离概念（让所有 Agent 共享一个文件夹，因为「隔离」是用户要理解的概念）
> - 减掉有风险的联网工具（因为安全争议，干脆关掉搜索）
> - 减掉单账户（把账户升级成组织，因为要按席位收费）

**→ 判据：拿到任何「X 的 GUI 封装版」，都要问「它为了易用性减掉了什么」，而不是只看它加了什么。**

### 第六步：三个必须主动去查的「隐形开关」

GUI 封装产品常在 README 里用一句不起眼的话，关掉一个关键能力。**必须逐项检索**：

| 查什么 | 检索关键词 | 实测案例 |
|---|---|---|
| **① 被禁用的工具** | `disables` / `disabled at both` / `policy layers` | ClawX 原文 `ClawX disables OpenClaw's general-purpose web_search tool at both the agent and Gateway policy layers. This includes Moonshot (Kimi) search` → **与「联网核验」需求直接冲突** |
| **② 默认关闭的功能** | `off by default` / `opt-in` / `requires Developer Mode` | ClawX 的 Computer Use `off by default, including existing installations` |
| **③ 会离开本机的数据** | `send their contents to` / `uploaded` / `remote endpoint` | 截图 `reading them for model vision can send their contents to your model provider`；openwork 的 MCP 端点 `api.openworklabs.com` |

**判据：一个产品「有没有某能力」和「默认开不开」是两件事，报告里必须分开写。** 而且「默认关」往往写在 README 中段的一句 `note` 里，不在功能列表里 —— **必须全文 grep，不能只读功能列表。**

### 第七步：许可证陷阱（本类任务连续两轮踩同一个坑）

**GitHub API 的 `license.spdx_id` 字段不可信，必须读 `LICENSE` 文件本身。**

实测两次：

| 产品 | API 返回 | `LICENSE` 文件实际 | 后果 |
|---|---|---|---|
| **OpenClaw** | `NOASSERTION` / `Other` | **MIT**（版权行写 `OpenClaw Foundation`） | 差点误判为「自定义许可」 |
| **openwork** | **`NOASSERTION`** | **目录分割许可**（`ee/` 之外 MIT，`ee/` 内是 EE License） | 差点误判为「就是 MIT」 |

**规律：只要版权行不是标准模板（写公司名/基金会名而非个人名），licensee 工具就会识别失败。**

**→ 判据：`NOASSERTION` 只代表「GitHub 没认出来」，不代表「没有许可证」。必须读原文。**

**目录分割许可的读法（类似 GitLab）**：要逐项提取四个数字 ——
1. 哪部分是真 MIT（本例：`ee/` 之外）
2. 哪部分是 source-available（本例：`ee/` 内的组织控制平面）
3. **免费门槛**（本例：`free for organizations with up to 5 users` / `free to evaluate for 30 days at any size` / `always free for development and testing`）
4. **是否有「自动转 MIT」条款**（本例：`Each ee/ release additionally converts to MIT two years after publication`）
5. **早期版本的许可证**（本例：`FSL-1.1-MIT`，非开源）

### 第八步：两个技术陷阱（本类任务实测踩到）

| 陷阱 | 现象 | 修复 |
|---|---|---|
| **README 文件名大小写** | `raw.githubusercontent.com/.../main/README.md` 返回 **404（14 字节）** | **AionUi 的文件名是小写 `readme.md`**。404 时先试小写 |
| **默认分支不是 `main`** | `.../main/README.md` 返回 **404** | **openwork 的默认分支是 `dev`**。取 README 前先查 API 的 `default_branch` |

**→ 通用修复流程：404 时按顺序试 ①小写 `readme.md` ②查 `default_branch` 后用 `dev/README.md` ③用 GitHub API 的 `contents` 接口列目录找真实文件名。不要直接断定「README 不存在」。**

### 第九步：报告结构（本类任务）

| 部分 | 内容 |
|---|---|
| **摘要** | 一句话结论 + 三个决定性事实（**每个事实都要引原文**） |
| **第一部分 来源与方法** | 来源表 + **单开一节说明「英文来源极少的局限」** + 三个仓库基础事实表 + 取证陷阱 |
| **第二部分 逐个调研** | 每产品：定位 → 核心机制 → 差异化能力 → **隐形开关（禁用/默认关/数据外流）** → 小结表 |
| **第三部分 横向对照** | **含母体的四列对照表** + 三个对照结论 |
| **第四部分 需求回填** | 七条需求 × 三产品矩阵 + **逐条说明**（关键差异要展开，不能只打勾叉） |
| **第五部分 诚实评估** | 各自代价 + **未验证项表（含「为什么没验证」）** + **自己的错误清单** + 结论 |
| **附录** | 完整功能/清单表 + 证据索引（含来源等级说明 + 本地取证文件清单） |
| **结语** | 决策树（用代码块画）+ **「三个不要」清单** + 一句话收束 |

**「三个不要」是本类报告的有效收尾形式**：把最容易被误用的三个用法明确列为禁止项。

**翻译要求**：用户要求「翻译成中文」时，**关键原文一律用「英文原文 + 中文译文」对照引用**，不要只给译文。因为译文会丢失判据关键词（`off by default` / `disables` / `NOASSERTION` 这类词必须在原文里可见）。

---

## 输出规范

1. **先给结论，再给论据。** 一句话说清推荐什么、为什么。
2. **公开修正自己的错误判断。** 调研跨多轮时，前期结论可能被后期证据推翻——明确标注「修正」，不要静默改口。
3. **区分「官方明确」和「待实测」。** 文档没写的不要猜，标注为待验证并给出验证方法。
4. **报告里保留来源列表**，按可靠度排序，并标注第三方来源的倾向性。
5. **给出可执行的验证方法**，而不只是结论。例如隔离测试：「在 A 里说一个虚构的高辨识度信息，去 B 里问，看是否泄露」。
6. **标注证据层级**。报告里区分「本机运行时（实现）」「源码级证据（实现）」「官方规范（契约）」「官方文档（宣传）」「媒体转述（不采信）」五档。**一手来源查不到的说法一律标注，不写进结论。**
7. **同一产品口径冲突时列冲突，不挑有利的写**，并给出验证方法。
8. **回答「A 有什么 B 没有」时，必须给每条差异定级（A 架构级 / B 机制不同 / C 路线选择）并附完整对照表。** 不分级会把「改版能追上」误报成护城河，或把「架构里没这一层」轻描淡写成功能缺失。
9. **诚实评估要单独成章。** 列出对方特色能力的代价与未验证项（如自托管=运维责任转移、插件 UI=供应链风险面扩大、角色库数量≠质量、人格系统无评测）。**只写优点的对比报告是软文，不是调研。**
10. **「未解问题」也要单独成章**，并给每项标验证难度与验证方法。**一份调研的价值，一半在于它说了什么，一半在于它承认自己不知道什么。** 别用「待验证」一句话糊过去——要写清「怎么验」。
11. **单份快报 vs 整合长报告，结构不同。** 单轮产出用「结论 → 依据 → 对照表 → 诚实评估」；多轮整合用**起承转合结构**：

| 部分 | 内容 | 作用 |
|---|---|---|
| 序章 | 为什么有这份文档 / 三个承诺 / 一条主线 | 立信 |
| **起** | 最初的问题 + 第一次取证 + 方法论第一课 | 交代起点 |
| **承** | 需求如何演化 + 假设如何崩塌 + 首选如何更换 | 展示过程（**不要只给最终结论，过程本身是价值**） |
| **转** | 视角反转：从外部需求转向内部实现 | 制造转折，得出「为什么是这个答案」 |
| **合·方法论** | 铁律 + 证据层级 + 分析框架 + 差异分级 + 误判清单 + **自己的错误清单** | **最有价值的部分** |
| **合·选型** | 决策树 + 场景映射表（含「两边都不满足」）+ 未解问题 | 可直接落地 |
| 附录 | 轮次索引 / 速查卡 / 来源清单 / 术语表 | 可查 |
| 结语 | 最终结论 + 通用防线 + **本报告局限** | 收束 |

**关键：整合报告里「我的错误清单」必须单独成章**，列出自己每轮判断错在哪、错因、后果、处置。这比 39 条别人的坑更有说服力。

12. **对比报告必须写「两边都不满足」的场景。** 大部分报告不写，因为它看起来像「没结论」。但**「两边都不行」是最有价值的结论之一**——它告诉你别在这两个里面选，去别处找。

---

## 常见误判（已踩过的坑）

| 误判 | 真相 |
|---|---|
| 「只有 Octop 能私有化部署」 | WorkBuddy 也有私有化档位，差异在销售模式不是能力 |
| 「Gemini Gems 记忆隔离是真的」 | Gem 指令隔离，但账户级 Personal context 会跨 Gem 串（可关闭） |
| 「所有产品记忆都是用户级」 | ChatGPT Project-only Memory、Claude Scoped Memory 已是 Project 级 |
| 「AnythingLLM 无长期记忆」 | 有 Memories，官方描述可绑定工作区 |
| 「传统 Chat 不能做面具隔离」 | 2026 年已追上，Project 级隔离是认真的 |
| 「记忆功能是隔离的主依据」 | 记忆机制最不稳定；**知识库作用域才是该依赖的那一层** |
| 「闭源产品不能换模型」 | WorkBuddy 支持自定义 Provider / Token Plan / Ollama 本地部署，API Key 仅存本地 `models.json` 不上云 |
| 「Octop 有专家市场」 | Roadmap 里「专家共享」「资源共享池」均未落地；只有内置专家库 |
| 「Octop 记忆隔离不明确」 | 源码级证据：记忆 API 全挂 `/api/agents/{id}/memory/*`，命名空间 `agent_<id>`，**按专家隔离是默认架构行为** |
| 「Octop 专家沙箱默认不信任」 | **媒体转述**，一手来源查不到；官方原话是「可插拔后端 + 隔离边界」，默认本地文件系统模式并非强隔离 |
| 「WorkBuddy 记忆能完全按工作区隔离」 | 三层记忆里**前两层跨工作区共享**（云端档案层不可控 + 用户级 MEMORY.md 全局），只有项目级是隔离的 |
| 「Octop 多智能体没做」 | 有已实现的 Inbox + Callback（`@` 提及、`ask_agent`）；缺的是 Roadmap 里的「协调者自主调度」。**但 inbox 是纯内存队列，重启丢任务** |
| 「连接器就是 MCP Server」 | WorkBuddy 的连接器是 **MCP 的超集**：分 MCP 型与 CLI 型（不可混用），且普遍自带 `skills/` 教 AI 怎么用（飞书 28 个、企微 14 个） |
| 「两边连接器是对称的」 | 结构完全不同：WorkBuddy = 磁盘目录 + 清单文件 + 技能；Octop = 数据库记录 + Python dataclass 清单 + **不带技能**（技能与连接器完全解耦）。**不对称本身就是结论** |
| 「CLI 型连接器两边差不多」 | 差一个量级：WorkBuddy = 声明式 `cli.json` + Node/Python 双运行时托管 + 安装目录隔离；Octop = 硬编码 `_SPECS` + 仅 npm + **不隔离安装目录**（进系统 npm global） |
| 「连接器数量可以直接比」 | 口径不同：WorkBuddy 注册表 14 条但还有内置连接器（腾讯文档/ima/QQ邮箱/微云不在注册表里）；Octop 代码 `_CATALOG` 23 条。且 WorkBuddy 的「14」背后是 28+14+5+4 个技能 |
| 「官方文档说凭证在本地」 | 需回源码验证。Octop 官方文档称凭证存 `~/.octop/secrets/`，实际该目录只放 `jwt_secret`，**凭证加密后存控制面数据库**——数据库可换远程 PostgreSQL，风险性质不同 |
| 「记忆功能是隔离的主依据 / 知识库作用域才是该依赖的那一层」 | **两边都要限定**。WorkBuddy 资料库是**空间级**共享，不是专家级；要「知识库共享 + 记忆隔离」得靠 Agent 调用时传 `spaceIds`，**不是架构保证**。Octop 才有专家级知识库绑定 |
| 「WorkBuddy 记忆能按工作区隔离」 | **部分成立**：只有 Layer3 隔离。Layer1 是**本机单一文件** `<uid>_memory.md`（已实测，账户级、服务端每次会话刷新覆盖），Layer2 全局单文件。且隔离维度是**工作区不是专家** |
| 「WorkBuddy 的知识库是向量库」 | 先分清形态：资料库首先是**内容管理平台**（六种 `kind`：doc/page/database/link/drive/smh + 空间协作 + 轻发布），检索只是能力之一；检索栈是服务端 **KInfra Retrieve**，`enableRerank:true` 固定开、阈值在服务端 `rerank.threshold` 过滤（`minScore` 客户端不下发） |
| 「Octop 知识库比 WorkBuddy 弱」 | **要拆开**：检索栈确实弱一代（**全表扫描 + Python 进程内余弦，无 ANN、无 rerank、无阈值**），但**可控性/可观测性/参数可调/专家级绑定全面强于 WorkBuddy**。不是单向的弱 |
| 「Octop 知识库参数可调所以更灵活」 | 作用域要看清楚：源码首行写着 **`Instance-wide`**——整个实例一套 `chunk_size`/`overlap`/`k`/`budget`，**不能按知识库或按专家差异化**。「有参数」不等于「参数够用」 |
| 「WorkBuddy 专家能预设知识库」 | **不能**。三份专家规范（`plugin-json-spec` / `agent-md-spec` / `team-spec`）搜「知识库/资料库/knowledge/library/spaceId」**零命中**；plugin.json 全 21 字段无知识库字段。检索范围只能由 Agent 调用时传参 |
| 「WorkBuddy 知识源少」 | 不准确。`productFeatures` 里有四个外部知识源（`ImaKnowledge` / `TencentDocsKnowledge` / `TencentLexiangKnowledge` / `TencentNetDriveKnowledge`），本账户全 `false`。准确说法是**「知识源可扩展但按账户开通」**——企业交付模式的选择，不是能力缺失 |
| 「WorkBuddy 记忆是结构化存储」 | **查 DB 证伪**：`workbuddy.db` 10 张表**零记忆表**。记忆是纯 Markdown 由模型用 Edit 工具直接读写，**无索引、无检索、无结构化存储、无生命周期**。且 `workspaces` 表只有 `path` + `last_opened_at`——工作区就是个文件夹路径 |
| 「Octop 记忆是黑盒」 | 数据模型其实完全可还原（六层实体 `raw_events`/`candidates`/`atoms`/`entities`/`episodes`/`journal` + 完整生命周期）。**真正的缺口是内核**：`harness_memory` 包**未开源**，提取算法/分层合并/检索方式/衰减策略四项无法验证，只能从 API 面反推 |
| 「Octop 的插件也就是 MCP 工具换皮」 | **不是**。Octop 插件有**前端注入点**：`plugin.yaml` 的 `ui.entry` + `ui.manifest.json` 把 renderer 名绑定到 tool，工具返回 `octop_ui` 信封渲染成卡片，并支持 `host.patchResult(callId, data)` **L2 刷新——零 token、零新回合**。11 个内置插件全部带 UI |
| 「插件差异是『做得好不好』的问题」 | ~~是架构级（A 级）~~ → **修正为 B 级**。我曾据 `plugin.json` 只有五类扩展点判定「没有任何前端扩展点」，**错了**。WorkBuddy 另有 `extension.json`（fork server + Module Federation renderer + 权限 + 灰度 + 常驻）和 MCP App 桥（`mcp-app-preload.js` + `host/getToken`）。**教训：查扩展能力必须查全所有层，只查一层就是取样偏差** |
| 「扩展系统的权限模型都一样」 | 有模型 ≠ 模型够细。WorkBuddy extension 的 `permissions: ["*"]` 是通配；Octop 插件没有权限模型但也没有 fork 进程和宿主任意访问能力。**「有」和「够细」是两件事** |
| 「有日志就等于可审计」 | 要分清「日志」和「**可举证的**责任链」。WorkBuddy 审计每条带 `sequence`+`prevHash`+`hash`，分段关闭写 `entryCount`/`firstHash`/`lastHash`/`fileSha256` —— 设计意图是**防篡改**。但**同时要问「链头锚定在哪」**：若 `manifest.jsonl` 和 `state.json` 与日志同目录，删掉整个目录就都没了。防篡改强度必须实测 |
| 「开源产品的能力缺口就是没有」 | 通常是「**你自己配**」。Octop 侧对应物：`tool-guard` 规则匹配（vs LLM 裁决器）、系统 cron（vs outbox + 租约）、`history_v2` 默认关闭（vs 默认全开的留痕）。这是设计哲学差异，不是能力缺失 |
| 「定时任务都差不多」 | 差一个量级。看自动化表里有没有 **outbox 模式**：`dedupe_key` / `lease_owner` / `lease_expire_at` / `attempt_count` / `max_attempts` / `next_run_at` / `last_error_code`。这是**至少一次投递 + 租约防重 + 退避重试**，属分布式系统设计 |
| 「模型清单越长能力越强」 | 要看**有没有档位抽象**。WorkBuddy 是两层：5 个抽象档位（default/fast/balanced/primary/deep）+ 23 个具名模型 + credits 计价（跨度 33 倍）。**档位抽象让用户不用懂模型也能选对**，这比模型数量更有价值 |
| 「多模态不支持 = 产品没有」 | **先查区域策略**。WorkBuddy 本机 `isOversea: true` + `DisableMultimodalGeneration: true`，注释原文「海外版下线多模态能力，给主 agent 注入 capability_constraints prompt」。**平台技能定义存在，只是本区域未开通**。区分「能力不存在」与「本账户未开通」是本方法论的核心动作 |
| 「主动式能力就是定时任务」 | 差在**主动性归属**。WorkBuddy 是「你配置它执行」（automation）；Octop 是「它知道自己该盯什么，你只配什么时候可以打扰你」——`HEARTBEAT.md` 心跳清单 + `proactive_care.py` 推送礼仪（`active_hours` 09:00–22:00、`min_interval_hours` 5，校验原文「不能小于 1 小时（防止频繁打扰）」）+ 分级告警（🔴立即 / 🟡汇总 / 🟢仅记录） |
| 「人格/角色就是个提示词文件」 | Octop 是**结构化数据**：16 套 `MBTIProfile` dataclass 含四轴百分比 `dimensions` + 六维行为映射 `behavior`（answer_style/casual_chat/conflict/creativity/emotion/planning），持久化到 `agents.persona_mbti`，渲染进 `SOUL.md`。且**故意不给编辑接口**（原文：`"no admin endpoint for persona content — by design: persona drift across users would make agent behaviour irreproducible."`） |
| 「子智能体库数量可以当质量指标」 | **不能**。489 个角色（272 中 + 217 英）本质是提示词模板，**无评测数据**。数量只反映覆盖广度，不反映能力 |
| 「ACP 只是接个 IDE」 | 是**双向**的：入向被 Zed 驱动（`octop acp --agent main`，stdio JSON-RPC，独立进程）；出向有 `acp_runner` 工具可委派给 **7 个外部 runner**（opencode/codebuddy/claude_code/codex/kimi_code/cursor_cli/pi），**权限提示回流到聊天**。作用域还分层：runner 卡片按用户存、工具开关按 agent 存 |
| 「自托管 = 更安全」 | 要打折。Octop 自托管把**所有运维责任转移给你**，且 `tool-guard` 安全规则默认偏宽松需自己配；插件能注入前端 = 第三方插件可执行任意前端代码，**供应链风险面更大** |
| 「Octop 是个完整开源项目」 | **壳开源、核闭源**。`TencentCloud/Octop` 是 MIT 开源（569 个 py 文件），但四个核心包 `harness-agent` / `harness-memory` / `harness-gateway` / `harness-browser` 走 PyPI wheel 分发，**仓库地址全部 404**。判据：读 `pyproject.toml` 的依赖列表，不是数 `src/` 的文件数 |
| 「PyPI 声明 MIT + 给了仓库地址 = 开源可用」 | **声明不等于存在**。实测四个 harness 包的 PyPI 元数据全部声明 MIT 并指向 `github.com/TencentCloud/harness-*`，四个地址访问全部 `Not Found`。**元数据字段是发布者自填、无任何校验** |
| 「闭核内核无法替代」 | 要去查它的**上游**。`orcakit-harness-agent` 的 PyPI summary 原文 `built on top of LangChain Deep Agents`，而 `langchain-ai/deepagents`（29,534⭐ MIT）的能力清单与 Octop 的 harness 能力**八项对八项全部对齐**（sub-agents / 可插拔文件系统 / 上下文管理 / 沙箱 shell / 持久记忆 / HITL / 技能 / MCP 工具）。**闭核的是集成成品，不是不可复现的技术** |
| 「README 徽章写 MIT 就是 MIT」 | **必须读 LICENSE 全文再判**。我一度写「`Tencent/WeKnora` 徽章写 MIT 但仓库真正的 LICENSE 是腾讯自定义许可」——**这是错的**。读全文后原文是 `This project is licensed under the MIT License except for the third-party components listed below... Tencent does not impose any additional limitations beyond what is outlined in the respective licenses of these third-party components.` —— 标准 MIT + 第三方声明，不是限制性许可。**错因：只看了 `head -6` 就下结论。LICENSE 必须读到出现实际授权语句为止。** 三处对照仍要做：README 徽章 / `LICENSE` 全文 / API `spdx_id` |
| 「71,722⭐ 的项目可以用」 | **按星数排序选型必然踩坑**。`daytonaio/daytona` 71,722⭐，README 顶部公告「As of June 2026, Daytona's core development has moved to a private codebase. This repository will receive no further updates」。同类：`AUTOMATIC1111/stable-diffusion-webui` 164,996⭐ 停更 200 天、`coqui-ai/TTS` 46,023⭐ 停更 763 天。**排序必须结合 `pushed_at`** |
| 「`getzep/zep` 是开源记忆产品」 | **不是**。该仓库自述 "This repository is **not** Zep's product or service"，只是 Zep Cloud 的示例与集成。真正的开源件是 **`getzep/graphiti`**（30,975⭐ Apache-2.0，时序上下文图）。**同名/同组织的仓库要核对描述与定位** |
| 「mem0 的基准数据可以直接引用」 | **要带限定**。README 自认「Scores reflect Mem0's **managed platform**, which includes proprietary optimizations **not available in the open-source SDK**」。LoCoMo 92.5 / LongMemEval 94.4 是托管平台成绩，OSS SDK 达不到同等数字 |
| 「多关键词 GitHub 检索能命中」 | **`q` 是 AND 语义**。`graph agent orchestration state machine stars:>3000` → `total=0`。第一轮 10 组里 6 组返 0（命中率 40%）。**改用 `topic:` 限定式后接近 100%**。另：`search` 接口未认证限额是 **10 次/分钟**（不是 60/小时） |
| 「开源在治理层一定弱」 | 要**逐维度看**，不能整体判断。Octop 侧 27 个维度里 20 个可 ★★★ 直接替换；沙箱隔离强度（CubeSandbox RustVMM+KVM vs `root_dir` jail）是**数量级差距**；技能治理（Octop 无回滚无隔离）、认证（Keycloak vs JWT+argon2）、编排可靠性（Temporal vs 进程内处理器 + 纯内存 inbox）都是开源更强 |
| 「对称动作只是形式」 | **不是，它会改变结论**。同一套方法、同一个四层模型，WorkBuddy 得到「企业级基础设施、合规层基本空白」，Octop 得到「壳开源核闭源、闭核内核有开源上游」。**不做对称动作，极易把上一个对象的结论错误套到新对象上** |
| 「README 说『remembers who you are』= 记忆是用户级」 | **读源码再判**。WeKnora README 的措辞让人以为记忆按人存（那会破坏工作区隔离），实际 `MemoryScope{TenantID, SubjectID}` + 唯一索引 `(tenant_id, subject_id)` + 包注释 `one principal inside one workspace`，是**空间×人**级。**宣传措辞的抽象层级 ≠ 实现的作用域** |
| 「有记忆隔离就够了」 | 要问**隔离维度有几个**。WeKnora 的 `MemoryScope` 只有两个字段，**没有 `AgentID`**——意味着同一空间内所有智能体共享同一份个人记忆，智能体级只能「关」不能「开」（源码原文 `There is no "on" that overrides the workspace`）。**「按空间隔离」和「按智能体隔离」是两个能力，有一个不等于有另一个** |
| 「开源产品必须有官方 SaaS 才叫能用」 | 要查清「云」是什么云。`WeKnora Cloud` 听起来像官方托管平台，实为**模型供应商集成**（CHANGELOG 原文 `provider integration, providing hosted LLM models`），与 OpenAI provider 同级。判据：查 ROADMAP 里「官方提供完整云端服务」是否勾选 —— WeKnora 是 `[ ]` 未勾选 |
| 「CHANGELOG 说发布了 = 能下载到」 | **要查 Release 产物和打包脚本**。WeKnora 桌面应用（Wails）代码齐全、文档齐全、CI 里有 Windows amd64 构建任务，但 `release-lite.yml` 的 tag 触发被注释掉、当前 Release 无任何产物、仓库只有 `package-mac-app.sh`。**三方核查：CHANGELOG（宣传）→ ROADMAP 勾选状态（自认）→ Release 产物 + 打包脚本（事实）** |
| 「Lite 版能救部署门槛」 | **先看它砍掉了什么**。WeKnora Lite 确实零依赖、数据全本地、默认仅本机访问，但 `docs/LITE.md` 明确 **「不提供共享空间」「单空间」**——即用需求 1/2/3 换需求 7。**轻量版不是「同一个产品的简化安装」，是「能力子集」** |
| 「用户说『我不会敲命令』= 这个产品不能用」 | **先区分一次性门槛与永久性门槛**。部署要敲命令，日常使用不用（逐项验证 UI 覆盖：知识库/文档/对话/智能体/记忆开关/搜索配置/模型配置都有页面）。**遇到「用户能力不足」类约束，先问：这个能力是每次都要用，还是只用一次？**（注意：版本升级也要敲命令，所以准确说是「低频」而非「一次性」） |
| 「一个产品满足或不满足需求」 | 可能是**两条产品线各满足一半且互斥**。WeKnora 标准版满足「多空间隔离 + 跨空间共享」但破坏「不敲命令」，Lite 版反之。**读双形态产品的对比表（如 `docs/LITE.md`），那张表就是官方在告诉你「哪些需求不能同时满足」** |
| 「记忆功能在助理里启用 = 记忆按助理隔离」 | **启用位置 ≠ 存储作用域**。LobeHub 可以在每个助理单独开关记忆，但**8 张记忆表全部只有 `userId`**（`user_memories` / `user_memories_contexts` / `_preferences` / `_activities` / `_identities` / `_experiences` / `user_persona_documents` / `_histories`），**没有 `agentId`、没有 `workspaceId`**。官方提示词自认这是 `global personal preference`。**判隔离必须查 schema 的列，不能查 UI 的开关** |
| 「知识库就是上传文件的地方」 | **「上传」和「可检索」是两个动作。** LobeHub 上传默认进**资源库**（只是文件列表，`listFiles` 无需预索引），**必须手动建知识库再导入**才能 `searchKnowledgeBase`。官方原文 `Most user files live in the resource library, NOT in knowledge bases`。**同一产品可能有三套独立存储（资源库 / 知识库 / 助理私有），必须逐个确认作用域** |
| 「credits 就是模型费」 | **要拆开算。** LobeHub × DeepSeek V4.1 Flash 实测：订阅费里**平台费占 61–83%，模型费只占 17–39%**（Starter 月付模型成本 $2.25 / 平台费 $10.65）。**只报「多少钱多少 credits」是没做分析的** |
| 「买了订阅 / BYOK 就没有限制了」 | **要逐项查限制类型。** LobeHub 的 **BYOK 只解除消息数限制，不解除文件/向量存储配额**；而**自托管版才真的没有额度**（`spendGate.ts` 原文 `Default: no spend accounting, so nothing is ever refused`，`getSubscriptionPlan()` 是桩永远返回 `Plans.Free`）。**「解除哪个限制」比「有没有限制」重要** |
| 「官方给的消息数是精确值」 | **官方代码里自己承认是估算**：`PlanLimitPricingBasis = 'approximate' \| 'estimated' \| 'exact' \| 'unknown'`。反推口径 ≈ 1,562.5 credits/条（输入 2,000 tokens + 输出 684 tokens）**是估算假设，不是官方承诺** |
| 「文档站和定价页数据一致」 | **定价页是实时数据源，文档站可能滞后数代。** LobeHub 文档站还在讲 `GPT-4.1` / `Claude 3.7 Sonnet` / `DeepSeek V3` / `R1`，定价页已是 `GPT-6 Astra` / `Claude Fable 5.1` / `DeepSeek V4.1 Flash`。**额度数字一律以实时定价页为准；文档站只用于提取机制说明，不引用数字** |
| 「同一页两个价格是官方数据冲突」 | **先算除法。** 「$9.9/Month」与「$12.9 Month / $118.8 Year」并存 → `118.8 ÷ 12 = 9.9`，是**年付等效月价**（年付折扣 23.3%）。**急着报「官方自相矛盾」之前，先验证是不是口径不同** |
| 「档位枚举里的都能买」 | **枚举值 ≠ 可购买档位。** LobeHub 的 `Plans` 有 5 档（Free / Hobby / Premium / Starter / Ultimate），**Hobby 未在售**。报告里要区分「代码里有」与「网站上能买」 |
| 「产品定位是稳定的，可以沿用前序结论」 | **必须重新读当前 README / 文档。** LobeHub 旧名 `lobe-chat`（→ `Moved Permanently`），现名 `lobehub/lobehub`，定位已从「聊天客户端」变为 `Chief Agent Operator`（文档自称「下一代 **Agent harness**」，**把 Agent 当作工作单元**）。**跨轮调研时，前序对产品定位的描述必须重新验证，否则整段分析的前提是错的** |
| 「迁移文件名说明了它的作用」 | **要读到实际 SQL。** `0057_add_topic_user_memory_extract_status.sql` 看起来像「按话题隔离记忆」，实际只是**给 `topics` 加 GIN 索引**、跟踪提取进度，与隔离无关。同类：`gatekeeper.ts` 看起来像隔离机制，实际是**记忆分层路由**（activity / context / experience / identity / preference 五层裁决）。**文件名会骗人，必须读到实际逻辑** |
| 「订阅是账户级的」 | **可能绑在工作区上。** LobeHub 的订阅绑定工作区（官方措辞「主 Owner 持有计费关系」），意味着「一个账户多个工作区」的成本是未知项。**这也影响「单账户」这条需求的实际代价** |
| 「助理分享出去是白赚的」 | **计费在创建者身上。** `spendGate.ts` 注释原文 `A shared agent runs under its CREATOR's identity, so every visitor turn is billed to the creator`，所以有 `AgentShareConfig.monthlySpendLimit` 上限。**「分享」类功能一定要查计费归属** |
| 「前序轮次已经判过这条，不用重查」 | **跨轮结论必须重验，且可能被推翻。** 前序第十四轮判定「LobeHub 唯一六项全中」，本轮源码取证发现**记忆 8 张表只有 `userId`，需求 2 不成立**。**同一产品被反复调研时，最危险的不是没查，是「沿用上次的结论」** |
| 「UI 上有『工作空间』就是工作区隔离」 | **必须回源码查三件事：①有表吗 ②有隔离键吗 ③查询里按它过滤吗。** Open WebUI 的中文 i18n 明明写着 `"Workspace": "工作空间"`，但**全部 38 张表里连 `group` 都有表，`workspace` 没有** —— 它只是权限前缀 `workspace.{models,knowledge,prompts,tools,skills}`，含义是「这个用户有没有权限在自己的工作空间里建 X」。**而且文档里反复出现「Workspace > Models > Edit」，让人以为是「工作区里的模型」，实际是「个人资源管理区里的自定义模型」** |
| 「名字叫 multitenancy 的适配器 = 多租户隔离」 | **要读它怎么取 tenant_id。** Open WebUI 有 `qdrant_multitenancy.py` / `milvus_multitenancy.py`，且 `ENABLE_QDRANT_MULTITENANCY_MODE` **默认 `true`**，看起来像多租户隔离。实际 `_get_collection_and_tenant_id()` 里 **`tenant_id = collection_name`** —— 「多租户」在这里是**存储优化**（一个物理集合装多个逻辑集合，避免创建上千个 collection），**不是隔离边界**。**`tenant_id` 的值是集合名（`user-memory-<uid>` / `file-<fid>`），不是用户或组织** |
| 「README 的功能计数可信」 | **可能高估也可能低估，一律以源码计数为准。** 实测反向案例：Open WebUI README 写 `Pick from 9 vector databases`，实际 `retrieval/vector/dbs/` 有 **15 个适配器 / 13 个独立后端**（多出 `mariadb_vector` / `opengauss` / `valkey` / `weaviate`）。**通常官方宣传会高估，但也有低估的** |
| 「没有原生移动端 = 移动端不可用」 | **PWA 已经很接近原生。** Open WebUI 无任何移动端仓库（25 个仓库全查过），但有 PWA（`native app-like feel and offline access`）。**现代 PWA 可添加到主屏、可推送、可离线**。判「移动端不可用」前要先问：**是「没有 App」，还是「不能用」？** |
| 「开源项目 = 标准开源许可」 | **必须查 `spdx_id`，且要读完 LICENSE 全文。** Open WebUI 的 GitHub API `license.spdx_id` 是 **`NOASSERTION`** —— 不是 MIT，也不是任何 OSI 认证许可。它是 **`Open WebUI License`**，第 4 条**禁止修改/移除/遮挡品牌**，例外三种（**30 天滚动期内终端用户 ≤50 人** / 书面许可 / 企业许可）。许可史：MIT → BSD-3-Clause → Open WebUI License。**源码里连记忆审查器的 system prompt 都带许可声明**（`# LICENSE covers this Open WebUI system identifier. Do not alter...`）—— 说明产品方在认真执行 |
| 「有 Release 产物 = 一直在维护」 | **还要算「最后 Release 距今天数」并与主项目对比。** Open WebUI 桌面应用 v0.0.20（2026-05-06，**停更 135 天**）有 22 个安装包、Windows 安装包下载量 **100,792 次** —— 真实可用，但主项目 0 天前还在推。**「有产物」要分三种：在维护 ✅ / 停更 ⚠️ 兼容性存疑 / 无产物 ❌ 未发布** |
| 「星数最高 = 最适合我」 | **星数只反映流行度，不反映抽象单位是否匹配。** Open WebUI **152,435⭐**（是 LobeHub 的 1.8 倍、WeKnora 的 5.8 倍），但它的隔离单位是「用户」，而需求是「单账户内的多工作区」—— **架构上正交，星数再高也补不上**。**选型第一步永远是确认抽象单位，不是看星数** |
| 「`grep`/`glob` 数出来的数字可以直接用」 | **Windows 下 Python `glob` 返回反斜杠路径，`f.split('/')[-1]` 会静默失效。** 实测：`glob.glob('.../web/*.py')` 后用 `/` 分割排除 `main.py`/`utils.py` → **返回 33（错的，正确答案 31）**，因为返回的是 `backend\open_webui\...\main.py`，排除集合永远匹配不上。**静默失效的过滤器比没有过滤器更危险 —— 它给你一个「看起来对」的数字。** 所有计数必须用第二种方法交叉验证（如 `ls \| grep -v -x`） |
| 「复核脚本本身不需要复核」 | **本轮第二次踩「计数工具不可靠」的坑。** 用 `awk` 数 Markdown 标题层级时写了 `gsub(/^#/,"#")` —— `gsub` 返回替换次数，但 `^#` 在行首**只匹配一次**，永远返回 1，于是 63 个各级标题全被算成 h1。**改用 Python `re.match(r'^(#+)\s', ln)` 取 `len(m.group(1))` 才对**（正确结果 h1=1 / h2=10 / h3=39 / h4=13）。**复核脚本自己也要用第二种方法验一次** |
| 「文档站路径可以猜」 | **不要猜，用限定域搜索。** `docs.openwebui.com/features/authentication-access/rbac` 返回 404，真实路径是**带尾斜杠**的 `.../rbac/`。正确做法：`WebSearch(query=..., allowed_domains=["docs.openwebui.com"])`。**并且先试加 `.md` 后缀取 Markdown 源文**（`.../memory.md`），比 HTML 干净得多，能拿到完整正文 |
| 「README / GitHub description 就是产品定位」 | **文案与实现的错位是双向的，而且可能差很远。** LibreChat 的 GitHub description 至今写着 `Enhanced **ChatGPT Clone**`、README 正文写着 `self-hosted **AI chat platform**`，**但代码是完整 agent harness**（170 个 agent 模块 + 18 项能力 + 13 个租户隔离中间件）—— 这叫**实现超前**。反向案例是 LobeHub：自称 `Chief Agent Operator` 但 8 张记忆表只有 `userId` —— 这叫**文案超前**。**定位类问题一律以代码骨架为准，文案只用来判断「它希望被谁理解」。** 三者（官网 title / GitHub description / README 正文）不一致本身就是结论 |
| 「功能清单能回答路线问题」 | **不能。** 路线问题（「它往哪走」）要靠**代码骨架 + 时间线 + 组织事实**三证据交叉验证。只看功能清单会以为「刚加了个 agent 功能」；只看时间线会以为「早就在做」；只看 README 会以为「还是个聊天平台」。**三者缺一都会误判** |
| 「有 agent 功能 = 走 agent 路线」 | **要区分它把 agent 当「产品」还是当「基础设施」。** LobeHub 把 agent 当**产品**（应用商店，卖专家）；LibreChat 把 agent 当**基础设施**（运行时，卖地基）。判据看数据模型里有没有**分布式系统的字段**：`certainty: 'definite' \| 'ambiguous'`（承认失败无法判定）、`outcome: 'dead'`（死信）、`resolution: 'action_compensated' \| 'history_repaired'`（saga 补偿）、`claimToken` / `configRevision`（fencing token + 配置版本）。**一个「给人用的工作台」不会有这些字段** |
| 「npm / PyPI 元数据里的仓库地址 404 = 一定闭源」 | **要实际访问，而且正反两个方向都要用。** 前序用这条查出 Octop 的「壳开源核闭源」（四个 harness 包仓库地址全部 404）。本轮**反过来用**：`@librechat/agents` 声明 `github.com/LibreChat-AI/agents` → **实际 HTTP 200、MIT、未归档、2 天前还在推** → **核真的开源**。**同一个检查动作，一次查出「假开源」，一次查出「真开源」。不做这一步，两个结论都会写错** |
| 「`CLAUDE.md` / `AGENTS.md` 里的路径是准的」 | **会过时，必须实际访问。** 这类文件（给 AI 编码 agent 的指令）里的「Project Overview」是**高质量架构自述**，但路径会漂。实测 LibreChat 的 `CLAUDE.md` 写源码在 `github.com/danny-avila/agents`，实际 **`301 Moved Permanently` → `github.com/LibreChat-AI/agents`**。**文档过时 ≠ 仓库有问题，但不实际访问就发现不了** |
| 「`package.json` 的 `license` 字段可信」 | **以 `LICENSE` 文件为准。** 实测 LibreChat 根 `package.json` 写 `"license": "ISC"`，而 `LICENSE` 文件是 `MIT License`、GitHub API 的 `spdx_id` 也是 `MIT`。**三处不一致时，`LICENSE` 文件 + API 为准，`package.json` 字段最不可信** |
| 「fork 数 < star 数 = 这个仓库不重要」 | **要反过来读。** 实测 `LibreChat-AI/agents` 是 **64⭐ / 120 forks**（fork 数是 star 的 1.9 倍）。这是**「被依赖」而非「被收藏」**的仓库特征 —— 作为依赖被 fork 使用，而不是作为目的地被收藏。**低 star + 高 fork 的仓库往往是关键依赖** |
| 「主仓库健康 = 卫星仓库也健康」 | **要逐个查许可 + 停更天数。** 实测 `LibreChat-AI` 组织 11 个仓库：主项目 MIT、`admin-panel` 是 **AGPL-3.0**、`code-interpreter` 是 **Apache-2.0**，另有 3 个停更 465–526 天。**混用多仓库时每个都要单独查许可**（AGPL 的传染性需要评估） |
| 「agent 模块数多 = 成熟度高」 | **数量只反映投入规模，不反映成熟度。** 实测 LibreChat 的 `packages/api/src/agents/` 有 170 个非测试 TS 文件，但里面混着 `legacy.ts` / `migration.ts` / `harvest.ts` / `fading.ts` 这类可能半成品的模块。**判成熟度要看测试投入**：测试文件占比（154/324 = **47.5%**）、有没有**属性测试**（`@antithesishq/bombadil`）、有没有**覆盖率守门测试**、有没有为某个状态机**专门写 e2e 生命周期规格**（HITL / Steering 各一份） |
| 「收购公告的『保持开源』承诺 = 一定保持」 | **要读「What's next」那一节，而不是「我们很兴奋」那一节。** ClickHouse 公告承诺 `remains 100% open-source under its existing MIT license`，**但路线图明确要加「ClickHouse happy path」**（原生集成、数据可视化、OAuth/治理、**语义层**）。**「通用性不被削弱」是承诺，不是保证。** 判据：查收购方的**整合先例** —— ClickHouse 之前收了 PeerDB 和 HyperDX（后者变成 ClickStack 的 UX），说明它的 playbook 是深度整合而非保持独立 |
| 「单一命令数出来的结构指标可以直接用」 | **结构指标也要三口径验证。** 复核报告时用三种方法数代码围栏：`grep -c '^```'` / Python 逐行 `startswith` / `awk '/^```/{c++}'` → 三个都返回 **54**。**单口径可能踩到转义或行首空白问题**（见「复核脚本本身不需要复核」那条）。标题层级要用 `re.match(r'^(#+)\s', ln)` 取 `len(m.group(1))`，**不要用 `awk` 的 `gsub(/^#/,"#")`**（行首只匹配一次，永远返回 1） |
| 「仓库里没有 PLAN / PoC 文档 = 没有规划」 | **要找，而且它是最直接的方向证据。** 开源仓库里常有「还没进主干的能力」的规划文档，**因为它写给自己人看，所以比对外文案诚实**。实测 LibreChat 的 `search/README.md` 同时给出四个信号：①收购方的技术（ClickHouse 容器）**已经在仓库里跑起来**（收购不是纸面叙事）②有 `PLAN.md` 和 **track 编号**（内部有分轨计划）③**`outbox` 在触发投递和搜索索引里都出现**（团队级一致的工程习惯）④出现 `ferretdb`（MongoDB 协议兼容层）→ **在评估存储引擎替换**。**找法**：`find . -iname "*PLAN*" -o -iname "*README*"` 后 grep `track` / `PoC` / `worktree` / `migration`。**⚠️ 必须标注这是「方向证据」不是「现状能力」** |
| 「Release body 里搜到关键词 = 那个版本引入的」 | **必须回读原文确认是「新功能」还是「顺手提了一句」。** 实测 LibreChat 的 release body 关键词扫描：`agent` 首次出现于 v0.3.3（2023-04，**噪声**，可能只是 user agent）、`MCP` 于 v0.7.6（2024-12，**真转折点**）、`Subagent` 于 v0.8.6-rc1（2026-05）。**判据是动词** —— 只有 `Introducing` / `New` / `feat:` 才是转折点。**交叉验证技巧**：把外部包的创建日期与 Release 日期对齐（实测 `@librechat/agents` npm 首发 2024-08-28，`v0.7.5-rc1` 发布 2024-08-27 —— **同一天**，说明该 RC 就是为 agent 运行时铺路的） |
| 「对照表里没写 = 对方没有」 | **「没查」和「没有」是两件事，必须分开标注。** 本轮做 LibreChat vs LobeHub 路线对照时，LibreChat 侧查到 `subagents` / `schedules` / `hitl` / `steering` / `chain` / `observability` 六项，但**前序对 LobeHub 的取证只覆盖了五个维度**，没查这六项。**处置：在对照表里标「未验证」，不能写成 LobeHub 的缺失。** 判据：**对照表里「未验证」超过 3 项时，必须在报告里显式声明结论完整度不足** |
| 「前序已经排除过的候选，不用再看」 | **产品会演进，排除理由会过期 —— 而且「过期」有两种。** 实测 OpenClaw：第 12 轮因「配置驱动、全 CLI」被排除，第 26 轮复核发现**它有完整的浏览器 GUI**（建 Agent / 管 roster / 改权限 / 配 MCP / 看记忆全在里面）。**五条排除理由里三条是「当时就错」**（全 CLI、无知识库、星标第一），两条是「产品变了」（许可证、隔离强度）。**所以复核类任务的第一步不是查新功能，而是「把前序的排除理由逐条变成可验证的断言，再逐条重验」** —— 否则会查了一堆新特性，却回答不了「现在能不能翻案」 |
| 「第三方榜单里的仓库路径是对的」 | **榜单只能用来「发现名字」，不能用来「确认事实」。** 实测某篇「12 Best OpenClaw Alternatives」：`nanoclaw` 写成 `nanoclaw/nanoclaw`（实际 `nanocoai/nanoclaw`）、`zeroclaw` 写成 `zeroclaw/zeroclaw`（实际 `zeroclaw-labs/zeroclaw`）、`moltis` 写成 `moltis/moltis`（实际 `moltis-org/moltis`）—— **三个路径用 API 查全部 404。** 处置：每个名字都必须拿去 `api.github.com/search/repositories?q=<name>+in:name` 重新解析出真实 `full_name` |
| 「榜单里提到的产品都存在」 | **有些是编的。** 同一篇文章列的 **「Grip AI」**，用 GitHub 搜索 API 查 `grip ai agent`，只返回 **1 个 2024 年的 3-star 无关项目** —— 该产品不存在。**判据：任何进报告的产品名，必须有一个可访问的 GitHub API 返回体或官方站点作为凭证。** |
| 「GitHub API 的 `license` 字段可信」 | **必须读 `LICENSE` 文件本身。** 实测 OpenClaw：API 返回 `license.spdx_id = "NOASSERTION"`、`name = "Other"`，**但 `LICENSE` 文件第一行是 `MIT License`，版权方 `OpenClaw Foundation`** —— 因为版权行写法不标准，GitHub 的 licensee 工具没识别出来。**这个字段的错误是「双向」的**：既可能把 MIT 报成 Other（本案例），也可能把自定义许可报成标准许可（见「以 `LICENSE` 文件为准，`package.json` 字段最不可信」那条） |
| 「Star 数第一 = 真的是第一」 | **必须对照头部仓库。** 前序第 11 轮写 OpenClaw「60 天破 25 万 star，**已超 React 成为 GitHub 星标第一**」—— 这条来自第三方文章，未验证。实测：OpenClaw **390,025**⭐ 确实极高，但 **freeCodeCamp 455,708**⭐、**996.ICU 277,142**⭐ 都在同一量级，**「第一」不成立**。**处置：写「极高」可以，写「第一」必须用 API 对照 `freeCodeCamp/freeCodeCamp` 等头部仓库。** |
| 「产品宣传的隔离能力 = 默认行为」 | **宣传用的是最强配置，默认值往往弱得多。** 实测 OpenClaw：文档写「文件系统级隔离」「沙箱后端」，但原文是 **`Sandboxing is off by default`**、**`This is not a perfect security boundary`**、**`each agent's workspace is the default cwd, not a hard sandbox`**（绝对路径可达主机其他位置）。**判据：凡是文档里出现 `off by default` / `not a perfect` / `is experimental` / `untested on <平台>` 的句子，都要原样引用进报告** —— 这些是官方自己给的折扣 |
| 「隔离就是隔离，不用分类」 | **「防串味」和「防对抗」是分水岭，混为一谈会导致误判。** 实测 OpenClaw 官方自己划线（`start/teams.md`）：`A gateway is one trust domain ... roles are collaboration guardrails inside the boundary, not isolation between adversaries` / `If you need to serve mutually untrusted people or organizations, run one gateway per tenant`。**含义**：要「防串味」→ 多工作区方案就够，**不违背单账户约束**；要「防对抗」→ **必然多实例**，直接撞「单账户」硬约束。**拿到任何多租户方案，先问用户要的是哪一种** |
| 「文档站的 `.md` 后缀全站通吃」 | **要逐个试，Mintlify 系支持，其他站不支持。** 实测：`docs.openclaw.ai/concepts/multi-agent.md` → **200 且是干净 Markdown**（Mintlify 站，`.md` 后缀可全站拉原文）；`hermes-agent.nousresearch.com/docs/**/*.md` → **全部 404**（统一返回 9,379 字节的 404 页）。**处置：先用一个已知存在的页面探测后缀可用性**（能拿到 frontmatter `---` 开头就是通的），不通就改用 WebFetch。**⚠️ 顺带：404 页的大小如果是固定值，说明是统一 404 页，别把它当成内容** |
| 「英文社区查不到 = 我没查好」 | **可能是真的零讨论，而这本身就是结论。** 实测 AionUi / ClawX 在 HN Algolia API 上返回 **0 条**（`json.load` 抛 `JSONDecodeError`，**不是 API 故障，是零结果**）。**处置：①把空体识别为「零讨论」②不要含糊写成「讨论较少」，要写成显式结论「该产品是中文社区驱动的项目」③给旁证把它从「我没查到」升级为「客观事实」**（社区入口是企业微信群/飞书群而非 Discord、贡献者命名习惯、鸣谢 `LINUX DO`、引用链接全是微信公众号、用英文关键词搜索前 N 条全是中文站点）④单开一节说明这个局限 |
| 「社区质疑 = 项目有问题」 | **要同时报告「质疑是否已被证伪」。** 实测 openwork 的 Show HN 帖里 `browningstreet` 立了个检验条件：`I ignore these things until they're 3-6 months old and still iterating.`。**把这个条件拿去对照创建日期与最近推送日期**：创建 2026-01-14、调研日 2026-09-18、当天还在推送 → **它通过了社区自设的检验**。**只报质疑不报验证，会把「已被证伪的怀疑」写成「现存风险」** |
| 「三个同类产品互相对比就够了」 | **必须把「它们所封装/参照的母体产品」也加进来做四列对照。** 实测 AionUi / ClawX / openwork 三个都是 OpenClaw 生态产品：**只做三列 → 结论是「各有千秋」；加上 OpenClaw 母体 → 发现「三个的隔离能力全部弱于母体」**，进而提炼出结构性规律：**GUI 封装层为了降低门槛会主动做减法**（减掉隔离概念、减掉有风险的联网工具、把单账户升级成组织）。**判据：拿到任何「X 的 GUI 封装版」，都要问「它为了易用性减掉了什么」** |
| 「GUI 封装版 = 功能更多」 | **多数是功能更少，只是更易用。** 实测三个封装的共同点：ClawX 主动禁用 `web_search`（含 Kimi）、AionUi 的 Team Mode 让 `all agents share the same folder`、openwork 把账户升级成组织按席位收费。**「封装」的常见动作是「关掉难解释的东西」** —— 而这些东西往往正是高级需求所依赖的 |
| 「README 的功能列表 = 全部能力」 | **关键限制常写在列表之外的 `note` 里。** 实测 ClawX 的 `web_search` 禁用声明藏在「Local Computer Use」小节末尾的一段 `> Web search note:` 引用块里，**不在功能列表里**。**处置：全文 grep 三类关键词 —— ①`disables` / `disabled at both` / `policy layers`（被禁用的工具）②`off by default` / `opt-in` / `requires Developer Mode`（默认关闭）③`send their contents to` / `uploaded` / `remote endpoint`（数据外流）** |
| 「README 请求 404 = 仓库有问题」 | **先试两个变体：小写文件名 + 非 `main` 默认分支。** 实测：AionUi 的 README 文件名是**小写 `readme.md`**（`README.md` 返回 404 / 14 字节）；openwork 的**默认分支是 `dev`**（`main/README.md` 返回 404）。**修复顺序：①试小写 ②查 API 的 `default_branch` 后用 `dev/README.md` ③用 `contents` 接口列目录找真实文件名。不要直接断定「README 不存在」** |
| 「作者说『太技术化』只是客气」 | **这是产品方对自己最可信的负面评价，要当硬结论用。** 实测 openwork 作者原话 `Yeah it is still too technical.`，并给出三条补救计划（预打包配置 / 把 opencode 内嵌进应用 / 去掉堆砌的术语）—— **这三条恰好是另外两个竞品已经做到的事**。**判据：作者自认的短板 > 任何第三方评测。** 因为作者有动机淡化缺点，他说出来的一定是真的 |
| 「被质疑后作者没回答 = 这事不重要」 | **未答本身就是风险信号，要原样记录。** 实测 openwork 的 HN 帖里 `philipwhiuk` 问 `What's the security boundary here - there's no mention of a VM or anything to isolate the agent from the file system?` —— **作者全程未回答**，回答的是另一位用户（`i think the point is to access the filesystem`）。**处置：在报告的「未验证项」表里列出来，注明「官方未回应」** |
| 「产品有 Android 工程 = 有 Android 应用」 | **工程目录的存在 ≠ 已发布产品。** 实测 AionUi 的 `mobile/` 是完整的 React Native / Expo 工程（有 `app.config.ts` / `eas.json` / `metro.config.js` / `__tests__` / `versions/`），**但官网、README、Releases 里都没有任何已发布的 APK / iOS 应用**。**处置：只能写「有工程痕迹」，不能写「有 Android 应用」；并给出可验证的替代路径**（本例：AionUi 的 WebUI 模式 + 手机浏览器，或 IM 通道） |
| 「目录分割许可 = 不是开源」 | **要逐项拆开读，它往往是「一部分真 MIT + 一部分 source-available」。** 实测 openwork 的 `LICENSE`：`Everything outside ee/ is MIT` / `Everything under ee/ is under the OpenWork EE License`（source-available）。**必须提取五个要素：①哪部分真 MIT ②哪部分 source-available ③免费门槛（`free for organizations with up to 5 users` / `free to evaluate for 30 days at any size` / `always free for development and testing`）④是否有自动转 MIT 条款（`Each ee/ release additionally converts to MIT two years after publication`）⑤早期版本许可证（本例 `FSL-1.1-MIT`，非开源）。** 判据：**「桌面应用能不能白用」和「组织功能要不要付费」是两个独立问题，不能用一个「开源/不开源」概括** |
| 「按席位收费只是定价方式」 | **席位定价会暴露产品的目标用户，进而暴露它与「单账户」需求的结构性冲突。** 实测 openwork：`The Team Starter plan includes your first 5 seats free, then $10 per seat per month` + `sign in and choose your OpenWork organization` + `Invite teammates, create teams, and manage access from one place` + 核心 MCP 走 `api.openworklabs.com`。**四个证据合起来说明：它的整个价值主张建立在「多人组织」之上。** 用户要的是「一个屋主，多个抽屉」，它给的是「一个公司，多个员工」。**判据：看到按席位收费 + 组织控制台，就先去核对「单账户」这条需求** |
| 「下载返回 200 就是拿到了内容」 | **Windows 文件名大小写不敏感，会让探测动作自己毁掉证据。** 为判断 README 文件名大小写，同一目录先后下载 `README.md`（200，12,387 字节）与 `readme.md`（404，14 字节），后者**直接覆盖**前者——我据此一度准备写「该仓库没有 README」，是错的。**判据：批量下载必须用互不冲突的输出名；且每个文件都要 `head -c` 看首字节 + 核文件大小，不能只看 HTTP 状态码**（14 字节的 404 页与正文同名为 `404: Not Found`） |
| 「Drift / moor schema JSON 的 `entity['name']` 是表名」 | **表名在 `entity['data']['name']`。** 实测 Kelivo 的 `drift_schema_v3.json`（46 个实体）：按 `e['name']` 取全部返回 `None`，**险些得出「schema 里没有表」而推翻整个记忆章节**。正确读法：`type=='table'` → `e['data']['name']`，字段在 `e['data']['columns'][i]['name']`。**判据：解析陌生 JSON 前先 `print(json.dumps(entity[0])[:1500])` 看清结构，不要凭字段名猜** |
| 「开源仓库里的设计文档 = 该开源产品的能力」 | **可能描述的是商业版。** 实测 Chatbox：仓库内 `docs/technical/index.md` 的标题是「**Chatbox Pro** 技术设计文档」，而 README 原文写着 `This is the repository for the Chatbox Community Edition` + `We regularly sync code from the pro repo to this repo, and vice versa.` → **CE 是 Pro 的子集，仓库里的技术文档描述的是商业版**。不发现这一点，会把 Pro 的能力（会话级 Skills、完整知识库）当成 CE 的写进对照表，**系统性高估**。**判据：读仓库内文档前先读它的索引页，确认它描述的是哪个产品** |
| 「官方文档里的功能数字可以直接引用」 | **同一项目内可能有三个不同数字，而且可能高估也可能低估。** 实测 Open WebUI 的向量库数量：README 原文 `Pick from 9 vector databases`、官方竞品对比页原文 `13 vector databases`、代码实测 `retrieval/vector/dbs/` 下 **15 个适配器 / 13 个独立后端**（多出 mariadb_vector / opengauss / valkey / weaviate）。**处置：三个数字并列呈现，以源码计数为准，不挑一个用** |
| 「产品文档说有的功能 = 真的有」 | **同仓技术文档可能明确说未实现，此时以技术文档为准并公开标注冲突。** 实测 Chatbox：`docs/product/tools-and-integrations.md` 写「会话级：在输入框 Skills 菜单按会话覆盖启用列表」，而 `docs/technical/agent-skills.md` 写「**会话级覆盖（未实现）**——当前代码未实现，工具构建只读全局 `skills.enabledSkillNames`」。**判据：产品文档（写给用户看）与技术文档（写给自己看）冲突时，技术文档更可信；且必须在报告里给出可执行的验证方法（本例：会话内切 Skills 菜单，抓请求体看注入列表是否变化）** |
| 「README 里被引用的卫星仓 = 该平台受支持」 | **要逐个查许可 + 停更天数。** 实测 Kelivo 的鸿蒙支持指向独立仓 `Chevey339/kelivo-ohos`：**最后推送 2025-09-25（停更 362 天）、且仓库无任何 LICENSE 文件**。README 正文却把 HarmonyOS 与 iOS/Android 并列在下载表里。**判据：跨仓引用必须逐个核验 `pushed_at` + `license`，停更天数要与主仓对照后再决定是否写进能力表** |
| 「我的校验脚本报出的不一致 = 真的不一致」 | **复核脚本自己也要复核，`colspan` / `rowspan` 都会造成假阳性。** 第一次用「每行 `<td`/`<th` 计数」校验 HTML 表格列数，报出「表 10 列数不一致：2 vs 4」——实际是刻意用了 `colspan="3"`，**是设计而非缺陷**；补上 colspan 修正后再跑，又报「表 1 列数不一致：2 vs 3」——这次是 `rowspan="4"`（rowspan 行之后的行天然少一个单元格），**仍是设计**。**判据：HTML 结构校验必须同时计入 `colspan` 与 `rowspan`；同一类假阳性重复出现两次，说明该写的是「解析器」而不是「正则计数」** |
| 「仓库里有 Dockerfile / docker run 命令 = 可自部署」 | **要读部署文档描述的是「应用」还是「凭据转发器」。** 实测 Chatbox 的 `team-sharing/` 有 `Dockerfile` + `Caddyfile` + `main.sh` + 完整 docker run 教程，看起来像自部署；读 README 原文才发现唯一目的是 `share the resources of the same OpenAI API account without exposing your API KEY`——**Caddy 反代 + Key 注入，不托管任何应用逻辑、不存数据、无用户管理，且只支持 OpenAI 一家**。**判据：部署后你拿到的是一个应用，还是一个凭据转发器？判据落在「部署文档的组件清单」而非「有没有容器文件」** |
| 「官方文档没写这个能力 = 代码里没有」 | **这是「在写下任何『无』之前先问它藏在哪个文件里」的反方向犯法。** 实测 Chatbox：`docs/technical/agent-soul-memories.md` 描述记忆为「全局条目列表」，我据此写「Chatbox 记忆是全局单一列表，无 scope 字段」——**错的**。实际 `src/shared/types/agent-persona.ts` 有 `export type MemoryScope = { type:'global' } \| { type:'copilot'; copilotId: string; epoch: number }`，且 `copilotStore.ts` 有 `COPILOT_MEMORY_OWNERS_STORAGE_KEY`（注释：`Copilots whose chats keep their own memory list instead of the global one`）。**设计文档描述的往往是默认行为，不是全部实现。判据：能力类结论必须以类型定义/schema 为准，文档只用来理解意图** |
| 「数据模型里是 `Mixed` / `extra='allow'` 类型 = 无法判定」 | **要换一条路径取证，不要就此放弃。** 实测两例：LibreChat 的 `tool_resources: Schema.Types.Mixed` 与 Open WebUI 的 `ModelParams(extra='allow')` 都看不出字段。解法有二：①**找反向查询**——Open WebUI 的 `models.py` 里有 `select(Model.id, Model.user_id, Model.meta).filter(cast(Model.meta, String).like(f'%{file_id}%'))`，**从「哪个模型的 meta 引用了这个文件」反推出 `meta.knowledge` 存的是引用**；②**找同名字段的专用测试文件**——`agentWorkspace.spec.ts` 里的断言（`code_workspace_id: 'project-a'`）比 schema 更直接。**判据：Mixed 类型不是取证终点，是换路的信号** |
| 「知识库是独立实体 = 知识库能独立挂载」 | **这是「独立工作区」类判断最容易犯的错，两者差别极大。** 实测 `ThinkInAIXYZ/deepchat`：有完整的内置知识库引擎（`src/main/knowledge/` 下 `knowledgeBase.ts` / `database/knowledgeDatabase.ts` / `ports.ts` / `routes.ts` / `taskQueue.ts`，类型含 `KnowledgeChunkMessage` / `MetricType = 'l2'\|'cosine'\|'ip'` / `KnowledgeVectorInsert`，还有 `KnowledgeDatabasePort` / `KnowledgeEmbeddingPort` / `KnowledgeFilePort` / `KnowledgeTaskQueuePort` 四组依赖注入接口），但**全部知识库管理界面都在 `src/renderer/settings/components/`（应用级设置）**，`knowledgeBaseId` 只被 `knowledge/*` 与 `api/KnowledgeClient.ts` 引用，没有「某工作区绑定某几个知识库」这种字段——它是把知识库包成 MCP 工具（`builtinKnowledgeServer.ts` 等）交给 agent 调用。**判据：P2 的判定必须看「工作区 ↔ 知识库」的关联表/外键，不是看知识库引擎存不存在** |
| 「写个正则就能把目标品类从搜索结果里筛出来」 | **两次都失败，且失败方向相反——这条路本身不可靠。** 实测：第一版「噪声正则排除 + 正向正则保留」筛 198 条候选，**180 条通过**（immich 相册、gitea、milvus、uptime-kuma 全混入，因为它们的描述里含 `self-hosted` 或 `AI`）；第二版收紧正则后结果是 **0 条**。**过宽则无过滤作用，过窄则全军覆没。处置：改为「先列全量、人工判定」**——198 条按 star 排序逐行读完，比调正则更快也更准。**判据：品类筛选靠人眼扫一遍全量列表，正则只用来做粗排或关键词计数** |
| 「`nohup ... &` 起的后台任务能跨轮存活」 | **不能，会被回收。** 实测：用 `nohup python s3.py > s3.log 2>&1 &` 起批量抓取任务，返回后 `sleep 55; cat s3.log` 为空；下一轮再看，`ps aux \| grep s3.py` 已无进程，`s3.log` 仍是 0 字节，**工作全部丢失**。**判据：长任务要用工具自带的后台机制（`run_in_background`，有 task_id 与完成通知），不要自己 `nohup`；且脚本必须「每 N 项落盘一次」**（本轮 `s5.py` 用 `if i%6==0: save()` + 末尾 `save()`，中断也只丢最后几项） |
| 「星数排名能代表产品形态」 | **不能，两者已经脱钩。** 实测 `zylon-ai/private-gpt`（**57,524 ⭐**）：README 现在写着「PrivateGPT is the open-source **API layer** that turns local models into production AI applications.」/「PrivateGPT **does not run models itself.** It connects to any OpenAI-compatible inference server via `OPENAI_API_BASE`.」/「This UI is a **demonstrator, not the core product.** Developers are expected to build their own applications on top of the API.」，并自绘对比表把 Onyx/Open WebUI 归为「self-hosted AI applications」而自己是「API layer for building self-hosted AI applications」。**它已经从「本地私有 ChatGPT 客户端」转型为「后端」，不再是客户端。** 同一批里还有：`ChatGPTNextWeb/NextChat` 88,799⭐ 但全仓 `knowledge\|embed\|vector\|rag` 只命中 3 个无关文件（无知识库）；`chatchat-space/Langchain-Chatchat` 38,658⭐ 已停更 316 天；`h2oai/h2ogpt` 11,965⭐ 停更 348 天。**判据：星数只能用来「发现名字」，产品形态必须回 README 首段 + 源码目录结构确认。凡是用星数排序找替代品，都会系统性地把死仓库和已转型项目排到前面** |
| 「compose / 配置文件里列出的服务 = 会启动」 | **不等于，必须读 `profiles:` 字段。** 实测 Onyx：`grep "^  [a-z0-9_-]+:" docker-compose.onyx-lite.yml` 得到 7 个服务，含 `opensearch` / `minio` / `redis`，一度误判「Lite 也跑 OpenSearch」。实际这些服务全部被 `profiles: ["opensearch"]` 之类排除，默认不启动（该文件顶部注释明写 "Moves both model servers, OpenSearch, MinIO, Redis (cache), and the background worker to **profiles** so they do not start by default"）。**判据：数服务前先看 `profiles`，有 profiles 且未被 `--profile` 激活的服务不算在部署栈里** |
| 「目录数可以直接数出来当指标」 | **不行，计数前必须先定义判定标准。** 实测 Onyx 连接器数量得到过 **53 → 58 → 52** 三个值：第一次按目录名过滤混入了工具目录（`google_utils` / `microsoft_utils` / `cross_connector_utils`）；第二次模式放宽把辅助目录也计入；第三次才定标准「目录内存在 `connector.py` 或 `*_connector.py`」。**判据：凡是报告里要写数字的，先在脚本里写死判定函数，并在报告里显式说明口径（本报告最终写「52 个，口径=目录含 connector.py，其中 4 个为非外部服务类」）。先数后解释必然出错** |
| 「两处官方描述互相冲突 = 其中一处是错的」 | **先怀疑粒度差异，再怀疑错误。** 实测 Onyx：`docker-compose.onyx-lite.yml` 注释称 Lite 下 "connectors and RAG search are disabled, but ... Projects, **Agent knowledge**, code interpreter still works"，而 `persona/api.py::_validate_vector_db_knowledge` 在 `DISABLE_VECTOR_DB=true` 时对 `document_set_ids` / `hierarchy_node_ids` / `document_ids` 一律抛 HTTP 400。看似矛盾，**实际是粒度不同**：代码是字段级精确（哪几个 `*_ids` 被拒），注释是概括式（「Agent 还能挂东西」），两句话都对——Lite 下仍可挂**用户上传文件**（走 FileReaderTool）。**判据：发现冲突时先做粒度对齐（一句话在回答哪个层级的问题），能对齐就不要判「官方有错」；这个顺序能省掉大量无效的「找错」工作** |
| 「精简模式（Lite / CE / 无 GPU 模式）的能力边界看官方概括即可」 | **必须用字段级校验函数判定，概括式文案会误导。** 实测 Onyx Lite 的精确边界只能从 `_validate_vector_db_knowledge` 的 docstring 得到：「`document_sets`, `hierarchy_nodes`, and `attached_documents` all depend on the vector DB for search filtering. **`user_files` are still allowed because they use the FileReaderTool path instead.**」→ 结论：**Lite 不是「精简版 Onyx」，是「没有知识库的 Onyx」**。官方 docs 的措辞（"Includes LLM chat, tools, file uploads, and Projects"）其实更准，因为它**没有**把 knowledge 列进 Lite 能力清单。**判据：找 `*_validate_*` / `if not DISABLE_*` / `raise HTTPException` 这类守卫函数，它们定义的是真实边界；`README` 与 compose 注释只用来理解意图** |
| 「单产品深度调研 = 把前面横向报告里的结论扩写一遍」 | **不行，深度调研必须产出横向对比里不可能出现的东西。** 实测 Onyx 单产品报告（14 节 / 17 表）中真正有价值的是横向报告里没有的：①**发现第二个工作区实体** `UserProject`（`instructions` + `user_files` + `chat_sessions`，且 **Lite 下完整可用**，对纯自用比 Agent 更贴合）②`Persona` 上有 **4 种知识挂载机制**（`document_sets` / `user_files` / `hierarchy_nodes` / `attached_documents`），注释统一写 "for **scoped search**" → 挂载是**收窄检索范围**而非复制数据 ③`replace_base_system_prompt` 是**布尔开关**而非双字段 ④`Memory` 表**无 `agent_id`** → 记忆不能按 Agent 分区（横向报告只写了「Onyx 有记忆」，深度调研才看出它没有分区）⑤沙箱出口代理用 mitmproxy 做**凭据注入**，"the real secret never has to live in the sandbox pod" ⑥`CheckConstraint("user_id IS NULL OR owner_group_id IS NULL")` + `ondelete="SET NULL"` 保证删用户不销毁共享 Agent ⑦发现项目**正在从 Vespa 迁往 OpenSearch**（`ONYX_DISABLE_VESPA` / `opensearch_migration.py` / 一组迁移状态枚举）。**判据：单产品报告至少要给出「横向对比时因为只有一个格子而看不见的东西」——多实体、多机制、约束、迁移中状态、守卫函数** |
