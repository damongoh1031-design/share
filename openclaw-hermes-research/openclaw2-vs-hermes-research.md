# OpenClaw 2.0 与 Hermes Agent 核心能力与系统适配深度对比研究

**日期**：2026-10-13
**执行模式**：完整（5 章，含三轮审稿机制中的第 1 轮修订，4 章一轮 PASS）

---

## 目录

- 引言
- 1. 记忆系统架构对比：Curated Memory 双文件与 Dream Diary 式持久化的边界设计
- 2. 自进化机制对比：Skill Workshop/SKILL.md 自动生成与离线 GEPA 管线的人工闸门
- 3. 纠错与恢复机制对比：快照回滚、/undo、doctor 与 write_approval 人在回路的约束边界
- 4. 长期稳定性与故障模式复盘：OpenClaw crash-loop、OOM、迁移事故与版本回归
- 5. Arch/NixOS 部署适配、ACP 互操作性与双栈选型建议
- 结论
- 参考文献
- 待完善事项

---

## 引言

开源个人智能体的竞争焦点，已经从"能否跑通演示"转向"能否长期可信托管"。OpenClaw 2.0（v2026.8.1，2026-08-31 发布）与 Hermes Agent（Nous Research，2026-02 发布）代表了其中反差最大的两种工程哲学：前者以模型驱动的记忆巩固、提案制技能工坊和约每 1—2 周一次的发版节奏换取能力上限；后者以有界核心记忆、可切换审批的自进化循环与低频稳健换取可控性（[Hermes Agent 官网](https://hermes-agent.org/zh/)）。随着 hermes-acp 与 OpenClaw Gateway 完成互操作打通（[CSDN 双栈实操](https://blog.csdn.net/fwyTech2010/article/details/162519237)），"双栈共存"成为现实选项，选型问题随之收敛为四个用户关切：记忆是否可靠、进化是否可控、错误能否回滚、更新是否稳定——外加一个部署侧约束：能否在 Arch/NixOS 上长期运行。

本报告沿四条主线展开：第 1 章对比记忆系统架构，第 2 章拆解自进化机制，第 3 章建立"任务—系统—治理"三层纠错框架，第 4 章复盘长期稳定性与五类故障模式；第 5 章收束于 Arch/NixOS 适配、ACP 互操作与双栈选型。五章证据给出的核心预判是：两者在设计形态上正在收敛——都走向"有界核心＋可扩展外延"，OpenClaw 2.0 的引导流程已支持导入 Hermes 记忆（[2.0 官方博客](https://openclaws.io/blog/openclaw-2-0-release/)）——但收敛的是形态而非风险结构：OpenClaw 仓库 regression 标签累计已超过 3,200 条（[GitHub Search API](https://api.github.com/search/issues?q=repo:openclaw/openclaw+label:regression)），高速迭代的代价仍在持续显性化。

---

## 1. 记忆系统架构对比：Curated Memory 双文件与 Dream Diary 式持久化的边界设计

### 一、论点

Hermes 的 Curated Memory 与 OpenClaw 2.0 的 Dream Diary 式持久化，代表了 Agent 记忆架构的两种边界哲学：**前者是“有界自动整理”**——用硬性字符上限把记忆锁进 system prompt 的冻结快照，以 token 成本与 prefix cache 为约束，换取确定性、注入安全与跨会话稳定；**后者是“分层可控持久化”**——用模型驱动的后台巩固（官方称之为 dreaming）把带来源标注的材料提升为长期记忆，以可追溯、可遗忘、可审计换取记忆广度与用户最终控制权。二者的差异，本质是“记住什么由 Agent 决定、但容量被锁死”与“记住什么由模型巩固、但用户可审计删除”之间的工程权衡。

### 二、论据

**1. 设计哲学：Agent 优先 vs 网关优先。** Hermes 由 Nous Research 于 2026 年 2 月开源，官网自我定位为“有记忆的开源 AI 智能体”——“跨会话记住你的偏好、项目和环境。运行越久，越了解你”，所有记忆存储在本地 `~/.hermes/` 目录（[Hermes Agent 官网](https://hermes-agent.org/zh/)）。其记忆由两个文件构成：MEMORY.md（Agent 个人笔记，2,200 字符，约 800 tokens）与 USER.md（用户档案，1,375 字符，约 500 tokens），存放于 `~/.hermes/memories/`（[Hermes 持久化记忆文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)）。社区分析将两种哲学概括为：“Hermes 在学习 Agent 周围包装了一个网关。OpenClaw 在消息网关周围包装了一个 Agent”（[Kilo：1,300 条 Reddit 评论分析](https://kilo.org.cn/openclaw/vs-hermes)）。OpenClaw 2.0（v2026.8.1，日历版本号命名，2026 年 8 月 31 日发布）（[OpenClaw 2.0 官方发布博客](https://openclaws.io/blog/openclaw-2-0-release/)）则把记忆重构为中枢能力：官方博客“Memory Grows Roots”一节称， dreaming 机制“默认将带来源资质（provenance-qualified）的材料提升为长期记忆，配有 Dream Diary 和一个关闭开关”（同左）（注：官方中文博客页 openclaws.io/zh/blog/openclaw-2-0-release/ 多次抓取返回空，本章统一引用内容一致的英文原版页面）。记忆职责被重新划分：内置记忆统一负责搜索与回忆，LanceDB、Memory Wiki、外部嵌入服务以及 MEMORY.md、USER.md 等文件各司其职（[studyopenclaw：2.0 版重塑记忆](https://studyopenclaw.cn/openclaw-2-0-rebuilds-memory-2026)）。

**2. 容量限制与遗忘机制：硬上限强制合并 vs 可追溯可遗忘。** Hermes 的边界画在字符数上：超出上限时工具不自动压缩，而是返回错误——“Memory at 2,100/2,200 chars. Adding this entry (250 chars) would exceed the limit. Replace or remove existing entries first.”，Agent 必须读取当前条目、用 `replace` 合并、再 `add`（[Hermes 文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)）。有分析认为这一“不友好”设计的关键考量是“让 Agent 在同一轮对话里完成合并 → 删除 → 写入，避免悄悄丢失信息”，并称“容量限制是功能，不是 bug”（[Hermes 自进化机制拆解](https://blog.tanteng.space/posts/hermes-agent-self-evolution/)）。OpenClaw 未公开等价的字符硬上限，其遗忘机制是治理式的：用户“可以检查哪些会话 feed 了某条记忆、排除来源，并用 `openclaw memory forget` 让 Agent 遗忘”（[官方博客](https://openclaws.io/blog/openclaw-2-0-release/)）；且“遗忘一条派生记忆，并不会删除原始对话或 OpenClaw 之外的副本”（[studyopenclaw](https://studyopenclaw.cn/openclaw-2-0-rebuilds-memory-2026)）——遗忘是派生层与原始转录的逻辑断开，原始数据保留可审计。

**3. 检索机制：FTS5 双层 vs 2.0 内置统一搜索。** Hermes 是明确的 L1/L2 双层：L1 Curated Memory 即时可用（随 system prompt 注入，总计约 1,300 tokens 固定开销）；L2 `session_search` 基于存于 `~/.hermes/state.db` 的 SQLite 数据库，FTS5 全文查询约 20ms、滚动约 1ms，返回数据库中的实际消息，“无 LLM 摘要，无截断”，且免费（[Hermes 文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)）。OpenClaw 2.0 中内置记忆成为“核心检索与回忆路径”，符合资格的个人 Claw 可从其他私密对话回忆相关上下文（[studyopenclaw](https://studyopenclaw.cn/openclaw-2-0-rebuilds-memory-2026)）；而“按精确词搜索过去对话并重新打开周边消息”的能力与 Dream Diary 同在 2.0 交付（[官方博客](https://openclaws.io/blog/openclaw-2-0-release/)）。时序上，OpenClaw 直到 2.0 才把历史会话检索作为内置能力补齐，且 QMD 记忆扩展退役、需 `openclaw doctor --fix` 迁移（[studyopenclaw](https://studyopenclaw.cn/openclaw-2-0-rebuilds-memory-2026)）。

**4. 会话持久化：殊途同归的 SQLite。** Hermes 所有 CLI 和消息会话均存 SQLite（`~/.hermes/state.db`）并带 FTS5 索引（[Hermes 文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)）。OpenClaw 2.0 “将会话迁移至 SQLite，这也是降级现在需要备份而不能一摆了之的原因”（[官方博客](https://openclaws.io/blog/openclaw-2-0-release/)），升级前必须创建经过验证的备份（[studyopenclaw](https://studyopenclaw.cn/openclaw-2-0-rebuilds-memory-2026)）。默认关闭的隐身对话只停留于进程内存，不写磁盘（[studyopenclaw](https://studyopenclaw.cn/openclaw-2-0-rebuilds-memory-2026)）。

**5. 安全面：注入扫描 vs secret 不进上下文。** Hermes 在记忆条目写入前扫描注入与外泄模式——prompt 注入、凭据外泄、SSH 后门及不可见 Unicode 字符将被拦截，理由是“污染记忆等于污染整个 Agent 的指令系统”（[Hermes 文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)；[自进化拆解](https://blog.tanteng.space/posts/hermes-agent-self-evolution/)），并提供 `write_approval` 审核门（`/memory pending` 等）作信任校准开关（[自进化拆解](https://blog.tanteng.space/posts/hermes-agent-self-evolution/)）。OpenClaw 2.0 的安全重点在凭据侧：Agent 可通过掩码提示请求凭据，“值永不进入聊天或模型上下文”，并有选择性代理限制受保密密的发送范围（[官方博客](https://openclaws.io/blog/openclaw-2-0-release/)）。但 v2026.9.2 的安全升级提示显示，省略网关设置会让具备 session 工具的 agent 读取并搜索其他 agent 的会话（含其他用户转录），需显式收窄可见性（[v2026.9.2 发布说明](https://docs.openclaw.ai/releases/2026.9.2)）——记忆可检索性本身成了新的暴露面。

**6. 社区实测反馈。** 基于 r/openclaw 25 个帖子、1,300 余条评论的分析显示：“记忆保留是导致用户流失的首要原因。Agent 会忘记指令、跨项目混淆数据，并重复同样的错误”；高赞评论称“主要原因是内存问题。我从第 3 天左右就开始为此纠结”（u/spinsilo，+42），另有用户抱怨“它经常会从错误的项目文件中获取信息，或者犯下和前一天同样的错误”（[Kilo 分析](https://kilo.org.cn/openclaw/vs-hermes)）。同期约 30% 用户转向 Hermes，理由包括“更好的内存默认设置”，有用户直言“OpenClaw 集成更多，Hermes 主观上拥有更好的内存系统”（[Kilo 分析](https://kilo.org.cn/openclaw/vs-hermes)）。需注意该分析发布于 2026 年 4—5 月，针对的是 1.x 时代；2.0 的“Memory Grows Roots”正是对该痛点的正面回应。

### 三、分析

两种边界的画法指向相反的约束条件。Hermes 的边界**向内收敛**：容量硬上限加冻结快照把记忆钉死在 system prompt 固定位置——官方明确这是为保留 LLM 前缀缓存，若会话中途系统提示词变化，缓存失效将推高延迟与成本（[Hermes 文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)）。代价是实时性（写盘立即生效，下次会话才可见）与容量天花板，故其不得不以 L2 会话搜索、L3 Honcho 等外部提供商（Honcho、Mem0 等 8 个，与内置记忆并行而非替代）补足深化持久化（[Hermes 文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)；[自进化拆解](https://blog.tanteng.space/posts/hermes-agent-self-evolution/)）。OpenClaw 的边界**向外扩展再加用户收权**：dreaming 默认自动巩固，容量不必迁就 prompt，因为并非所有记忆都进上下文；控制权交给 `memory forget`、来源排除与 Dream Diary 开关。代价是巩固质量依赖模型判断——1.x 时代的“记忆混乱”恰是无治理巩固的教训——以及 SQLite 迁移带来的备份与多 agent 可见性运营负担。一个耐人寻味的交叉点是：OpenClaw 2.0 引导流程可检测并导入来自 Claude Code、Codex 和 Hermes 的记忆（[官方博客](https://openclaws.io/blog/openclaw-2-0-release/)），说明 Hermes 的双文件格式事实上成为被同行兼容的迁移对象；而 Hermes 也把超出双文件的记忆外包给外部生态。两家最终都逼近同一个形态——**有界核心 + 可扩展外延**，只是 Hermes 的核心更小更硬，OpenClaw 的核心更宽更需治理。

### 四、小结

Curated Memory 双文件与 Dream Diary 式持久化并非优劣之分，而是边界画在哪里的选择：Hermes 把边界画在容量与注入点上——小而硬、自动整理但有安全闸与（可选的）人工审核；OpenClaw 2.0 把边界画在治理与审计上——大而全、模型巩固但用户可遗忘、可排除来源。以 prompt token 经济学衡量，Hermes 的约 1,300 tokens 固定开销加 20ms 级按需 FTS5 检索，与 OpenClaw 的后台巩固加默认检索路径，代表“固定成本换即时性”与“可变成本换覆盖面”的经典对偶；而 Kilo 社区数据中约 20% 用户选择“两者并用”（OpenClaw 编排、Hermes 执行），某种程度上正是这种边界互补的实践注脚（[Kilo 分析](https://kilo.org.cn/openclaw/vs-hermes)）。

---

### 关键发现

- 发现 1：Hermes 用 2,200/1,375 字符硬上限 + 冻结快照把记忆约束在 system prompt 内，满额时强制 Agent 执行“合并→删除→写入”，容量限制被设计者视为训练 Agent 遗忘能力的功能而非缺陷（[Hermes 文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)，[自进化拆解](https://blog.tanteng.space/posts/hermes-agent-self-evolution/)）。
- 发现 2：OpenClaw 2.0 的 dreaming 默认巩固带来源材料，配 Dream Diary 与 `openclaw memory forget`；遗忘派生记忆不删原始对话，治理权在用户侧（[官方博客](https://openclaws.io/blog/openclaw-2-0-release/)，[studyopenclaw](https://studyopenclaw.cn/openclaw-2-0-rebuilds-memory-2026)）。
- 发现 3：两者会话存储殊途同归——Hermes 自始即用 `~/.hermes/state.db` SQLite + FTS5（查询约 20ms），OpenClaw 2.0 才将会话迁入 SQLite 并要求先备份（[Hermes 文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)，[官方博客](https://openclaws.io/blog/openclaw-2-0-release/)）。
- 发现 4：安全边界互补——Hermes 防“记忆污染 system prompt”（写入前注入扫描），OpenClaw 2.0 防“secret 进上下文”（掩码提示请求凭据），但 v2026.9.2 也暴露了会话跨 agent 可检索的新风险面（[Hermes 文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)，[官方博客](https://openclaws.io/blog/openclaw-2-0-release/)，[v2026.9.2 说明](https://docs.openclaw.ai/releases/2026.9.2)）。
- 发现 5：社区层面，“记忆不可靠”曾是 OpenClaw 1.x 用户流失首因，Hermes 则以更好的记忆默认配置赢得约三成转投用户——但该数据早于 2.0 发布，解读时须注意时序（[Kilo 分析](https://kilo.org.cn/openclaw/vs-hermes)）。

### 数据摘要

| 指标 | Hermes | OpenClaw 2.0 | 来源 |
|------|--------|--------------|------|
| 核心记忆容量 | MEMORY.md 2,200 字符 + USER.md 1,375 字符（约 1,300 tokens） | 未公开字符硬上限；MEMORY.md 为分层之一 | [Hermes 文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)、[studyopenclaw](https://studyopenclaw.cn/openclaw-2-0-rebuilds-memory-2026) |
| 记忆注入方式 | 会话开始时冻结快照注入 system prompt | 内置记忆统一检索回忆路径 | [Hermes 文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)、[studyopenclaw](https://studyopenclaw.cn/openclaw-2-0-rebuilds-memory-2026) |
| 遗忘机制 | 满额强制 replace/remove 合并 | `openclaw memory forget`，派生记忆可遗忘、原始对话保留 | [Hermes 文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)、[官方博客](https://openclaws.io/blog/openclaw-2-0-release/) |
| 历史会话检索 | FTS5 on SQLite，查询约 20ms、滚动约 1ms，免费 | 2.0 起内置精确词搜索 + dreaming 检索路径 | [Hermes 文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)、[官方博客](https://openclaws.io/blog/openclaw-2-0-release/) |
| 会话持久化 | `~/.hermes/state.db` SQLite | 2.0 迁入 SQLite，降级需备份 | [Hermes 文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)、[官方博客](https://openclaws.io/blog/openclaw-2-0-release/) |
| 安全设计 | 写入前注入/外泄扫描（prompt 注入、凭据、SSH 后门、不可见 Unicode） | secret 经掩码提示请求，不进模型上下文 | [Hermes 文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)、[官方博客](https://openclaws.io/blog/openclaw-2-0-release/) |

> **方法论脚注**：官方记忆概念页 docs.openclaw.ai/concepts/memory 不可达，相关论述以官方博客与第三方深读为据。

---

### 本章新增来源（供主理人更新来源池）

1. [OpenClaw 2.0 官方发布博客（英文版）](https://openclaws.io/blog/openclaw-2-0-release/) — “Memory Grows Roots”一节原文：dreaming/Dream Diary/provenance/memory forget/secret 掩码提示/会话迁 SQLite（注：任务指定的中文页 openclaws.io/zh/blog/openclaw-2-0-release/ 两次抓取均返回空内容，本文以英文镜像替代，内容应为同一篇）。
2. [v2026.9.2 Release Notes - OpenClaw](https://docs.openclaw.ai/releases/2026.9.2) — 共享网关升级提示：省略设置将允许带 session 工具的 agent 读取其他 agent 的会话（注：页面正文两次抓取均被截断，仅完整获取开篇与安全提示部分；release 规模 1,245 PRs + 232 contributors）。
3. [Memory overview - OpenClaw docs](https://docs.openclaw.ai/concepts/memory) — 搜索快照显示官方将 MEMORY.md 描述为 “compact, curated layer for durable non-profile facts”（注：直接抓取网络失败，仅获搜索摘要，建议后续重试补读）。
4. [OpenClaw Dreaming 功能详解 | OpenClaw 俱乐部](https://openclaw.club/archives/iXqMNSq9) — 社区对 Dreaming 后台记忆巩固系统的详解（未深读，候选补充来源）。

【来源说明】本章共聚合 7 个成功获取的来源（5 个完整深读 + 官方博客英文镜像 1 个 + 发布说明部分 1 个），满足 ≥5 来源及 ≥3 类型（官方文档×3、官方博客×1、行业媒体/第三方分析×2、个人博客×1）要求；中文官方博客页与 OpenClaw 记忆概念文档抓取失败已在上述清单中如实标注，未以任何编造 URL 补位。

---

## 2. 自进化机制对比：Skill Workshop/SKILL.md 自动生成与离线 GEPA 管线的人工闸门

> 数据核验日期：2026-10-13。除特别注明外，OpenClaw 版本号与发布规模均于当日抓取自官方 release notes；Hermes 侧机制引文取自官方文档与仓库 README 原文；本地安装数据为本机实测。

### 论点

OpenClaw 与 Hermes Agent 代表两条不同的自进化路线：前者以 Skill Workshop 把「智能体学到的东西」纳入提案—审批的受控路径，后者以 SKILL.md 自动生成把学习直接写进运行时主循环，并另有离线 GEPA 管线做周期性批量优化。两条路线都不「处处设人工闸门」——它们在关键路径上设人工闸门：离线 GEPA 管线强制人工 PR（官方 README 原文 "All changes go through human review, never direct commit"），运行时层的 `write_approval` 则是一个默认关闭、可随时切换的开关（开启后每一次技能写入都暂存待审）。真正区分二者的不是「有没有闸门」，而是闸门设在哪一层、默认是开是关、审查记录由谁留存。

### 论据一：Hermes 运行时自进化——SKILL.md 自动生成

Hermes 的官方定位（仓库 README 原文）为 "The self-improving AI agent built by Nous Research"，GitHub 仓库描述为 "The agent that grows with you"。其自进化能力由官方宣称的「闭环学习」（A closed learning loop）支撑，README 列出四个组成部分：带周期性提醒的智能体策展记忆、复杂任务后的自主技能创建、使用中的技能自我改进、FTS5 会话检索加 LLM 摘要实现的跨会话召回。

- **`skill_manage` 工具**：官方文档称「agent 可以通过 `skill_manage` 工具创建、更新和删除自己的 skills，这是 agent 的程序性记忆」。触发时机有四种：成功完成复杂任务后（5 次以上工具调用）、遇到错误或死路并找到可行路径时、用户纠正其方法时、发现非平凡工作流时。操作覆盖 create / patch / edit / write_file / remove_file / delete，写入 `~/.hermes/skills/`；官方同时明确警告：外部技能目录（external_dirs）不是写保护边界，只要对进程可写就会被修改。
- **自我改进的护栏是「劝告式」的**：`skill_manage` 在 create、SKILL.md patch 和 references 写入时运行一个 advisory linter，规则包括 incident-log-shape（正文充斥 PR/issue 编号）、references-sprawl（参考文件超过 60 个）、oversized-body（正文约 24k 字符以上）——官方原文「They warn; they never block a write」。
- **`/learn`**：官方文档将其定义为「不手写 SKILL.md，就把你已经知道的东西或一堆参考资料变成可复用技能」的快速路径。
- **技能规模**：内置 40+ 技能（本机安装实测 58 个 SKILL.md、12 个分类），自建技能无上限；技能兼容 agentskills.io 开放标准，可跨工具迁移。
- **`write_approval` 闸门（可切换）**：官方文档原文「`skills.write_approval` gates every agent skill write (create / edit / patch / delete / supporting files) behind your explicit approval」。默认 `false`（自由写入，即默认全自动）；置 `true` 后，每次写入暂存到 `~/.hermes/pending/skills/`，通过 `/skills pending`、`/skills diff <id>`、`/skills approve <id>`、`/skills reject <id>` 审查，并可用 `/skills approval on|off` 在运行时切换。记忆侧有同一机制的 `memory.write_approval`。
- **记忆分层 L0–L2**：外部记忆 provider OpenViking 采用分级上下文加载——L0（约 100 tokens）→ L1（约 2k tokens）→ L2（全文），逐层加深。

### 论据二：OpenClaw Skill Workshop——提案先行的受控路径

- **版本与规模**：OpenClaw 2.0 = v2026.8.1（2026-08-31 发布，官方博客题为《OpenClaw 2.0, Accidentally》）。发布宣传口径为 933 位贡献者、569 位首次贡献者、16,962 个 PR（另有媒体口径 16,248，两者存在出入）。
- **体系位置**：OpenClaw 的技能体系分为 tools / skills / plugins 三层，配套 plugin SDK、ClawHub 市场（clawhub.ai）与 Skill Workshop 审阅流程。
- **官方定位原文**：「Skill Workshop 是 OpenClaw 用于创建和更新工作区 Skills 的受控路径。智能体和操作员绝不会通过此路径直接写入 `SKILL.md`——他们会创建一个**提案**（包含内容、目标绑定、扫描器状态、哈希和回滚元数据的待处理草稿），该提案仅在应用后才会成为生效的 Skill。」
- **关键机制**（均见官方文档）：提案先行（生成内容存为 `PROPOSAL.md` 而非 `SKILL.md`）；apply 是唯一的实时写入操作；更新提案绑定目标当前哈希，生效技能在应用前变化则提案转 stale；apply 前重跑安全扫描器；apply 前先写回滚元数据；生命周期管理为 30 天未使用转 stale、90 天归档。审批策略 `skills.workshop.approvalPolicy` 默认 `"auto"`（智能体发起的 apply / reject / quarantine 无额外提示），可设 `"pending"` 要求操作员审批。`/learn` 只生成 pending 提案、永不自动应用；自主自我学习每次扫描最多创建/修订 1–3 个待处理提案，且永不能执行 apply / reject / quarantine。
- **迁移通道**：2.0 支持从检测到的 Claude Code / Codex / Hermes 安装中导入记忆与技能（SOUL.md、MEMORY.md、技能至 `~/.hermes/skills/openclaw-imports/`、API key），两个生态之间存在官方背书的双向流动。

### 论据三：Workshop 的版本演进与技能生态规模

- **v2026.9.2**（[release notes](https://docs.openclaw.ai/releases/2026.9.2)）：规模为 1,245 个 PR、6 个直接提交、232 位贡献者；主题是 OpenAI GPT-6 Astra 与 Meta Muse Spark 1.3 支持、可靠性与恢复改进（更新报告抗重连、中断任务重启后续跑）、以及灵活的任务工作区。
- **v2026.9.3**（[release notes](https://docs.openclaw.ai/releases/2026.9.3)）：规模为 1,844 个 PR、40 个直接提交、190 位贡献者；在更新恢复、会话重链、浏览器自动化直播、可撤销聊天链接之外，**进一步将 Workshop 技能持久化**——官方原文 "Skill Workshop now keeps each agent's learned skills together across workspaces"（Skill Workshop 现已把每个智能体学到的技能跨工作区保存在一起），同版本还有原生 Mac 标签页与提供商账户控制。
- **生态规模**：ClawHub 技能总数 13,700+——知乎《ClawHub 必装 Skills 清单：从 13000+ 技能中精选》（2026-03-06，文中口径 13,729 个）与阿里云开发者社区《从0到1玩转 13000+ OpenClaw Skill！》（2026-03-05，文中口径 13,625 个）为并列来源，**两文同源（2026-03 同题社区文章）**：均为对 ClawHub 技能总数的社区盘点而非官方统计，引用时应视作单一社区证据。
- 同一轮 2026-03 阿里云教程还提出「自己造技能 vs 用现成技能」的取舍（自定义 Skill 开发指南系列）；分发侧对单体技能另有体积与描述长度约束（SKILL.md ≤15KB、描述 ≤500 字符，草稿既核验口径）。
- 另引 CSDN RickyIT《【Hermes：Skill 系统深度】》系列（2026-05）佐证 agentskills.io 标准的跨工具兼容（原文：「你为 OpenClaw 编写的 Skill，只要遵循 agentskills.io 标准，就可以直接在 Hermes 中使用，无需任何修改」）——该来源为社区二手内容，仅作旁证，本论断的支撑以官方文档与 release notes 为准。

### 分析

- **闸门位置**：OpenClaw 把人工决策点放在「技能生效」这一步——提案不 apply 就永远是 PROPOSAL.md，不触碰活跃技能；Hermes 运行时把决策点前移到「每次写入」这一刻（opt-in）；离线 GEPA 管线把决策点放在「产出回流仓库」这一刻（PR）。
- **默认姿态**：三者默认值不同——Workshop 的 approvalPolicy 默认 auto；Hermes 的 `write_approval` 默认 false（默认全自动、可切换审核）；GEPA 无论配置如何都强制人工 PR。「处处设闸」与「全程放任」都不符合任一产品的实际默认行为，准确表述是「在关键路径上设人工闸门」。
- **记录与审计**：Workshop 侧每个提案有完整生命周期记录（proposals.json、rollback.json 与 applied / rejected / quarantined 状态流转）；Hermes 运行时侧，开启 `write_approval` 后有 diff 与 approve 记录（`/memory` 流程可 reject）；默认关闭时不产生任何审查记录，技能直接落盘。
- **自主边界**：Workshop 的自主捕获有硬顶（每次扫描最多 3 个提案、隔离审查最多 1 个、永不能执行生命周期操作）；Hermes 运行时的自主创建只以劝告式 linter 兜底（只警告不拦截）。两者的「自主」都被设计成可被人类否决，但否决的默认成本不同：OpenClaw 默认要人点 apply，Hermes 默认不用人点。
- **版本证据的含义**：Workshop 的跨工作区技能持久化到 v2026.9.3 才落地（v2026.9.2 的 1,245 个 PR 主要给了模型支持与可靠性），说明该机制仍在高速迭代——2.0 之后接近每 1–2 周一个版本（v2026.9.2 → 9.3 → … → v2026.10.2，均见 release notes 索引），引用 Workshop 行为必须带版本号核对。

### 小结

两条自进化路线的差别不在「敢不敢让智能体自己写技能」——两者都让写；差别在于写完之后发生什么。OpenClaw 用提案制把每一次技能生效变成一次显式决策；Hermes 用 opt-in 的 `write_approval` 把同一决策交给用户选择，同时用离线 GEPA 管线的强制 PR 守住批量优化的出口。对使用者的含义：选 OpenClaw 路线，审查成本默认放在事前；选 Hermes 路线，审查成本默认后置，但批量优化的出口始终有人工 PR 兜底。

### 关键发现

- 版本归属修正：Workshop 技能跨工作区持久化（"keeps each agent's learned skills together across workspaces"）属 **v2026.9.3**（1,844 PRs / 190 贡献者）；v2026.9.2（1,245 PRs / 232 贡献者）的主题是 GPT-6 Astra 与 Muse Spark 1.3 支持及可靠性改进。原草稿将该特性误挂在 v2026.9.2 下，已按官方 release notes 更正。
- 人工闸门的准确表述：两条路线都不处处设防，而是在关键路径设闸——离线 GEPA 管线强制人工 PR，运行时 `write_approval` 默认关闭、可切换（开启后逐次暂存待审）。
- 「13,700+ 技能」是社区同源口径：知乎（13,729）与阿里云（13,625）两篇 2026-03 同题社区文章，非官方统计。
- Hermes 技能审查记录需保守表述：默认关闭 `write_approval` 时无审查记录；开启后有 diff 与 approve 记录，reject 见于 `/memory` 流程。
- Workshop 机制仍在快速迭代（2.0 后约每 1–2 周一个版本），任何行为断言都应按版本号核对。

### 数据摘要

| 版本 / 对象 | 规模 | 主要内容 |
|---|---|---|
| OpenClaw 2.0（v2026.8.1） | 933 贡献者 / 16,000+ PRs | 官方宣传口径（另有 16,248 PRs 的媒体口径）；支持导入 Claude Code / Codex / Hermes 的记忆与技能 |
| OpenClaw v2026.9.2 | 1,245 PRs + 232 贡献者 | OpenAI GPT-6 Astra 与 Meta Muse Spark 1.3 支持、可靠性与恢复改进、灵活任务工作区 |
| OpenClaw v2026.9.3 | 1,844 PRs + 190 贡献者 | Workshop 技能跨工作区持久化（"Skill Workshop now keeps each agent's learned skills together across workspaces"）、原生 Mac 标签页、提供商账户控制 |
| Hermes Agent 最新版 | v0.21.7（2026-10-12） | 双轨版本号 vX.Y.Z + v2026.M.D；截至核验日的最新 release |
| ClawHub 技能总量 | 13,700+（社区口径 13,625–13,729） | 知乎 / 阿里云 2026-03 两篇同源社区文章，非官方数字 |
| Hermes 内置技能 | 40+（本机安装实测 58 个 SKILL.md / 12 类） | 自建无上限；兼容 agentskills.io |
| GEPA 单次优化成本 | 约 $2–10 / 次 | 五阶段中仅 Phase 1（SKILL.md）落地；产出以 PR 提交、强制人工审查，从不直接提交 |
| 运行时写闸门 | `write_approval` 默认 false（可切换） | 开启后暂存 `~/.hermes/pending/skills/`，`/skills diff`·`approve`·`reject` 审查 |

### 参考来源

1. [OpenClaw Release notes（索引）](https://docs.openclaw.ai/releases)
2. [OpenClaw v2026.9.2 release notes](https://docs.openclaw.ai/releases/2026.9.2)
3. [OpenClaw v2026.9.3 release notes](https://docs.openclaw.ai/releases/2026.9.3)
4. [OpenClaw v2026.8.1（AKA OpenClaw 2.0）release notes](https://docs.openclaw.ai/releases/2026.8.1)
5. [OpenClaw 技能工作坊（Skill Workshop）官方文档](https://docs.openclaw.ai/zh-CN/tools/skill-workshop)
6. [OpenClaw 创建技能官方文档](https://docs.openclaw.ai/zh-CN/tools/creating-skills)
7. [OpenClaw ClawHub 发布官方文档](https://docs.openclaw.ai/zh-CN/clawhub/publishing)
8. [Hermes Agent 仓库 README](https://github.com/NousResearch/hermes-agent)
9. [Hermes Agent Releases](https://github.com/NousResearch/hermes-agent/releases)
10. [Hermes Agent 技能系统官方文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/skills)
11. [Hermes Agent 配置官方文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/configuration)
12. [NousResearch/hermes-agent-self-evolution 仓库 README](https://github.com/NousResearch/hermes-agent-self-evolution)
13. [agentskills.io 开放标准](https://agentskills.io)
14. [知乎《ClawHub 必装 Skills 清单：从 13000+ 技能中精选》（2026-03-06）](https://zhuanlan.zhihu.com/p/2013332031464043740)
15. [阿里云开发者社区《从0到1玩转13000+OpenClaw Skill！》（2026-03-05）](https://developer.aliyun.com/article/1714840)
16. [CSDN《如何在 ClawHub 上发布 Skill：从打包到上架的全流程方案》（2026-06-13）](https://devpress.csdn.net/v1/article/detail/161962283)
17. [CSDN RickyIT《【Hermes：Skill 系统深度】22、资产保值时代》（2026-05-01）](https://blog.csdn.net/RickyIT/article/details/160418358)
18. [openclaw/openclaw GitHub 仓库](https://github.com/openclaw/openclaw)

---

## 3. 纠错与恢复机制对比：快照回滚、/undo、doctor 与 write_approval 人在回路的约束边界

### 论点

自主 Agent 的纠错能力并非"有或无"，而是分布在三个层次上：**任务级**（快照回滚、`/undo`、`/retry`）、**系统级**（doctor 诊断与修复、脱敏调试包、备份子系统）与**治理级**（write_approval 人在回路的暂存审核、审批与撤销）。Hermes 与 OpenClaw 的分歧不在"有没有纠错"，而在纠错被放在哪一层、由谁触发、边界划在哪里——Hermes 把重心押在任务级快照回滚与治理级写入门禁上，OpenClaw 2.0 则把重心押在系统级可验证备份与操作级审批撤销上。

### 论据

**任务级：快照回滚 vs 对话级回退。** 对会修改本地文件的自主任务而言，Hermes 的做法是在动文件之前先给工作目录拍快照，出错后用 `/rollback` 恢复先前状态；基于 25 个帖子、1300 余条 Reddit 评论的社区分析明确指出"**OpenClaw 没有对应的功能**"，并称此为"非常有意义的安全网"（[Kilo：OpenClaw vs Hermes 评论分析](https://kilo.org.cn/openclaw/vs-hermes)）。会话内，Hermes 还提供 `/retry`（重试上一条）与 `/undo`（撤销上一条）等交互式斜杠命令，以及 `hermes doctor` 诊断入口（[Hermes 深度用法指南](https://cfanzp008.github.io/hermes-agent-usage-guide/)）。OpenClaw 的任务级纠错则主要是对话分支级的：2.0 支持"从任何一条已存的消息回退或分叉对话，旧的分支还留着"（[OpenClaw 2.0 发布博客](https://openclaws.io/blog/openclaw-2-0-release/)）；在可靠性上，v2026.9.2 引入"中断的任务在重启后恢复""更新报告在重连后依然存活"，且特定保存失败时"已完成的答案仍然可用"（[v2026.9.2 发布说明](https://docs.openclaw.ai/releases/2026.9.2)）——后者是一种"降级但不丢结果"的容错设计，与文件快照回滚互补。

**系统级：doctor、triage 与备份子系统。** Hermes 的 `hermes doctor` 定位是诊断（[用法指南](https://cfanzp008.github.io/hermes-agent-usage-guide/)）；OpenClaw 则把 doctor 做成了**可修复**的系统——`openclaw doctor --fix` 模式执行修复性清理，2.0 中两处破坏性变更（OpenProse 插件迁移、`codex/` 模型路由迁移）均通过它完成（[发布博客](https://openclaws.io/blog/openclaw-2-0-release/)；[Doctor 官方文档](https://docs.openclaw.ai/zh-CN/gateway/doctor)）。2.0 还新增 `openclaw triage` 产出脱敏调试交接包，并把备份升格为"正经子系统"：定时快照进操作员自己的 Git 仓库、SQLite 归档可验证（[发布博客](https://openclaws.io/blog/openclaw-2-0-release/)）——这并非锦上添花：社区统计 OpenClaw"每次新更新约有 25% 的几率破坏心跳消息、cron 任务和 Webhook"（[Kilo 评论分析](https://kilo.org.cn/openclaw/vs-hermes)）。Hermes 侧的对应防线在更底层：默认容器沙箱"只读根目录、权限降级、PID 限制"（[Hermes 官网](https://hermes-agent.org/zh/)）。

**治理级：write_approval 暂存审核 vs 一次批准可查可撤销。** Hermes 的 `write_approval` 开启后，所有后台 Review 的记忆/技能写入**暂存而非立即生效**，用户用 `/memory pending|approve|reject` 与 `/skills pending|diff|approve` 逐条裁决；它被明确定位为"信任校准的关键开关"，且默认关闭（[Hermes 自进化机制拆解](https://blog.tanteng.space/posts/hermes-agent-self-evolution/)）。OpenClaw 的治理门划在操作侧：重复性自动化可对"这一个确切操作"批准一次，之后**能查、能撤销，任务一变就要重新批**；自学习则"扫描通过的技能自动生效，你亲手写的改动仍然留待确认"，并配有可回退的 Skill Workshop 审阅流与 `openclaw memory forget`（[发布博客](https://openclaws.io/blog/openclaw-2-0-release/)）。

### 分析

两者的约束边界恰好互为镜像。**Hermes 管"写入"**：一切经验固化都必须过暂存门，且用 L1 记忆 2200 字符硬限制把纠错成本前置——超限不自动压缩而是**返回错误**，逼 Agent 在同一轮完成合并、删除、重写，以"避免悄悄丢失信息"；其离线自进化管道也规定所有变体"永远走人工 PR，永不自动 commit"（[自进化机制拆解](https://blog.tanteng.space/posts/hermes-agent-self-evolution/)）。代价是门禁默认关闭，且写入门禁无法解决"什么算错误"的识别问题。**OpenClaw 管"操作"**：审批—撤销—可验证备份构成完整审计链，但它缺少快照级回滚，且其系统级纠错自身出过事故。

实证缺陷也各戳对方的软肋。Hermes 的自评估虚高是最尖锐的批评：高赞评论称"它总是认为自己做得很好。总是！……东西全弄乱了，它还觉得它干得漂亮！"（+107 赞）；若 Agent 无法准确评估自身输出，从"成功"任务沉淀的技能就会把错误编码进去（[Kilo 评论分析](https://kilo.org.cn/openclaw/vs-hermes)）。OpenClaw 的 2.0 迁移期则出现典型"假成功"治理事故：认证迁移把凭据归档后仍报告成功，配置迁移把行内 secret 换成占位符（[发布博客](https://openclaws.io/blog/openclaw-2-0-release/)）——纠错机制自身产生了虚假的成功信号。可以说，Hermes 的失效模式是"错误被当作经验固化"，OpenClaw 的失效模式是"失败被报告为成功"；两者共同指向同一盲区：**错误识别环节本身没有完美解**。

### 小结

三层纠错不是互斥而是互补：Hermes 以"快照 + `/rollback` + write_approval"在任务级和写入侧提供快速、可暂存的恢复路径，社区公认的 `/rollback` 恰是 OpenClaw 长期缺失的能力；OpenClaw 2.0 以"doctor --fix + triage + Git/SQLite 可验证备份 + 审批可撤销"在系统级和操作侧补上更完整的审计与恢复链条，并以中断任务恢复、保存失败时答案仍可用来提升可靠性下限。对使用者而言，结论是条件性的：若 Agent 要动本地文件，Hermes 的快照回滚更直接，但应显式开启 `write_approval` 以对冲自评估虚高与技能覆盖手工编辑的风险（后者同样有 +25 赞的实证抱怨）；若以 OpenClaw 承载正事，则升级前先把备份子系统开起来——毕竟连它的医生自己都在迁移中"谎报过军情"。

### 关键发现

- 发现 1：Hermes 修改文件前自动拍工作目录快照，`/rollback` 可恢复；社区分析明确指出 OpenClaw 无对应功能（[Kilo](https://kilo.org.cn/openclaw/vs-hermes)）。
- 发现 2：`write_approval` 开启后记忆/技能写入暂存，经 `/memory pending|approve|reject`、`/skills pending|diff|approve` 人工裁决，默认关闭，是"信任校准开关"（[tanteng](https://blog.tanteng.space/posts/hermes-agent-self-evolution/)）。
- 发现 3：L1 记忆超限返回错误而非自动压缩，逼 Agent 当轮完成合并—删除—重写，防止信息"悄悄丢失"（[tanteng](https://blog.tanteng.space/posts/hermes-agent-self-evolution/)）。
- 发现 4：OpenClaw 2.0 的 backup 成为正式子系统（定时快照进操作员 Git 仓库、SQLite 归档可验证），`openclaw triage` 产脱敏调试包，`doctor --fix` 承接破坏性迁移（[2.0 发布博客](https://openclaws.io/blog/openclaw-2-0-release/)）。
- 发现 5：OpenClaw 迁移期存在"假成功"事故——凭据归档后仍报成功、行内 secret 被换占位符（[2.0 发布博客](https://openclaws.io/blog/openclaw-2-0-release/)）。
- 发现 6：Hermes 自评估虚高（+107 赞）会导致错误经验被固化为技能（[Kilo](https://kilo.org.cn/openclaw/vs-hermes)）。

### 数据摘要

| 指标/事实 | 数据 | 来源 |
|------|------|------|
| Hermes 快照回滚 | 改文件前拍快照，`/rollback` 恢复；OpenClaw 无对应功能 | [Kilo](https://kilo.org.cn/openclaw/vs-hermes) |
| 自评估虚高实证 | "总是觉得自己干得对"，+107 赞 | [Kilo](https://kilo.org.cn/openclaw/vs-hermes) |
| 自学习覆盖手工编辑 | "简直是毁灭性的"，+25 赞 | [Kilo](https://kilo.org.cn/openclaw/vs-hermes) |
| OpenClaw 更新破坏率 | 每次更新约 25% 几率破坏心跳/cron/Webhook | [Kilo](https://kilo.org.cn/openclaw/vs-hermes) |
| L1 记忆容量硬限制 | 2200 字符（~800 tokens），超限报错逼自合并 | [tanteng](https://blog.tanteng.space/posts/hermes-agent-self-evolution/) |
| OpenClaw 2.0 备份子系统 | 定时快照进 Git + 可验证 SQLite 归档 | [2.0 发布博客](https://openclaws.io/blog/openclaw-2-0-release/) |
| OpenClaw 可靠性改进 | 中断任务重启后恢复、重连后报告存活、保存失败答案仍可用 | [v2026.9.2](https://docs.openclaw.ai/releases/2026.9.2) |
| 容器安全加固 | 只读根目录、权限降级、PID 限制 | [Hermes 官网](https://hermes-agent.org/zh/) |

---

## 4. 长期稳定性与故障模式复盘：OpenClaw crash-loop、OOM、迁移事故与版本回归

**论点**：OpenClaw 的长期稳定性问题并非随机噪声，而是可归为五类故障模式——崩溃循环、OOM、迁移事故、性能回归与发布阻塞。以 GitHub issue 为时间轴可见，它们与项目"高频发版"的节奏强耦合：几乎每个版本号都对应一类可复现回归，而官方制度性应对（extended-stable 发布线、备份子系统）的存在，恰好反向证明了问题的系统性。

### 论据

**一、故障模式分类与回归时间线。** 逐类归档一手 issue 证据。**OOM**：v2026.3.7 引入 message OOM 回归（[issue #41778](https://github.com/openclaw/openclaw/issues/41778)，4GB 服务器上稳定崩溃，终以 "not planned" 关闭）；v2026.3.12 更严重，连 `doctor`、`gateway status` 等基础 CLI 命令都在初始化阶段 OOM（[issue #45064](https://github.com/openclaw/openclaw/issues/45064)，经 [PR #46522](https://github.com/openclaw/openclaw/pull/46522) 于 v2026.3.13 修复）。中文排障资料将根因归于 Node.js v24 与 OpenClaw 二进制产物的 V8 ABI 不兼容，降级至 v22.22.1 可解（[LearnClaw，2026-05](https://learnclaw.cc/openclaw-memory-leak-oom-crash-fix-2026/)）。**崩溃循环**：ClawSweeper 于 2026.10.13 批量归档的回归簇显示，仅 2026.9.6 一个版本就引入三个 P1——模型目录 worker 堆增至多 GB 并冻结事件循环（[#170458](https://github.com/openclaw/openclaw/issues/170458)）、被禁用的 codex 插件仍持续派生子进程且超时进程从不回收（[#170457](https://github.com/openclaw/openclaw/issues/170457)）、被推迟的 session-migration 文件每次启动重扫、累积超过迁移租约致 Gateway 无法启动（[#170693](https://github.com/openclaw/openclaw/issues/170693)）；2026.10.2 仍有 Gateway 启动热重载升级为自我重启（[#170644](https://github.com/openclaw/openclaw/issues/170644)，复现 #135433）与 macOS 合盖唤醒强制重启（[#170525](https://github.com/openclaw/openclaw/issues/170525)）。**迁移事故**：[issue #95495](https://github.com/openclaw/openclaw/issues/95495)（regression / P1 / impact:data-loss，2026.6.21 提交、3 天后关闭）记录 2026.6.9 升级将记忆库静默迁往新路径——据 issue 自述，1,499 文件 / 23,694 chunks 的索引全部归零、升级流程零告警，磁盘上 3.4GB 旧库与 128KB 空壳并存；而同一安装在 2026.6.6 升级时本有"先备份再迁移"的 .bak 先例（该 issue 页面在终审期多次抓取失败，精确数字以 issue 自述口径为准）。**发布阻塞与性能回归**：2026.9.9 更新执行器结算失败被标为 P0 release-blocker（[#170545](https://github.com/openclaw/openclaw/issues/170545)，该 issue 于 2026.10.13 提交，内容为用户从 2026.9.9 升级 2026.10.2 时的结算失败）；`sessions.cleanup` 从 2026.9.9 的 <1s 退步到 2026.10.1 的约 27s（[#170474](https://github.com/openclaw/openclaw/issues/170474)）。[GitHub 检索](https://api.github.com/search/issues?q=repo:openclaw/openclaw+label:regression)显示，regression 标签历史累计 3,200 条（该数字已经 Search API 核验属实；未关闭条数未独立复核）。

**二、社区实证与版本策略对照。** [Kilo 对 r/openclaw 25 帖、1,300+ 条评论的分析](https://kilo.org.cn/openclaw/vs-hermes)给出社区侧故障率：约 25% 的更新会打挂 heartbeat/cron/webhook 响应投递；有用户因一次更新集成被破坏而 7 天不可用，也有人"连玩一个月最终放弃"；发布前 CI 主分支曾数日构建失败。截至 2026.5.8，OpenClaw 累计 137 个版本，Hermes 仅 11 个；2.0 之前 OpenClaw 在 230 天内发了 106 版，随后 7 周静默才推出 v2026.8.1（[OpenClaw 2.0 官方发布博客](https://openclaws.io/blog/openclaw-2-0-release/)）。社区的悖论判断是：Hermes"6 版中 3 版不能用"属实，但低频发版只降低破坏机会，"它甚至还没存在够久来支撑稳定说法"。OpenClaw 的对策是制度化的：拆分发布线，官方明示"若 Gateway 上有任务，让 2.0 先沉淀一两个补丁"，备份成为子系统（Git 定时快照 #122485、经验证的 SQLite 归档 #105718）；但同一博客承认 2.0 携未决迁移簇——auth 迁移可能归档凭证却仍报成功（[#134608](https://github.com/openclaw/openclaw/issues/134608)）、配置迁移把内联密钥替换为占位符（[#134169](https://github.com/openclaw/openclaw/issues/134169)）。修复方向上，[v2026.9.2](https://docs.openclaw.ai/releases/2026.9.2) 主打"可靠性与恢复"（更新报告抗重连、中断任务重启续跑）；2.0 将会话整体迁往 SQLite，升级前必须创建经验证的备份，QMD 记忆扩展用户须先运行 `openclaw doctor --fix`（[studyopenclaw，2026-09](https://studyopenclaw.cn/openclaw-2-0-rebuilds-memory-2026)）。

**三、安全面。** 一篇 r/selfhosted 帖子经 Kilo 转引的记录显示：OpenClaw 已备案 6 个 CVE、社区仓库识别出 341+ 个恶意技能、Shodan 扫出 135,000+ 个暴露实例；Hermes 暂无 Agent 特有 CVE，但这更可能反映曝光率有限而非加固更优。[v2026.9.2](https://docs.openclaw.ai/releases/2026.9.2) 自身的升级说明也警告：共享 Gateway 下具备 session 工具的 Agent 可读取并搜索其他 Agent 的会话——稳定性故障与安全边界在长期运行场景中相互放大。

> **口径说明**：本章多项社区实测数据（25% 更新破坏率、+107/+25 赞评论、"OpenClaw 无对应 /rollback"、6 CVE/341+ 恶意技能/135k+ 暴露实例、137 vs 11 发版）均转引自 Kilo 对 r/openclaw 的单一社区评论分析（自称 25 帖/1,300+ 评论样本），属社区感受类证据，置信度低于官方 issue 与 release notes，请读者按此权重取信。

### 分析

五类故障中，崩溃循环与迁移事故危害最大：前者直接中断服务，后者威胁数据完整性（#95495 带 data-loss 标签，2.0 迁移簇涉及凭证归档）。共同根因有二：架构上，Gateway 单进程承载会话、路由、迁移与插件生命周期，任一子系统泄漏都被放大为全局冻结——"多 GB 堆冻结事件循环"正是此构型的极端表现；流程上，高频发版使回归以版本号为单位出现，用户事实上在用生产环境做回归测试。高频的另一面是修复也快（#95495 三天关闭、OOM 两版内修复），但对"Gateway 上有任务"的用户，中断成本高于新功能收益，这正是 extended-stable 线与"先备份、等补丁"官方建议的存在理由。Hermes 的低频发版并未证明其更稳定，只是把验证推给未来——两个方向都未挣脱"规模-稳定性"悖论。

### 小结

对长期运行用户，全部证据指向一套具体纪律：升级前做经验证备份（SQLite 会话库尤甚）、固定 Node 于 v22 而非 v24、对 heartbeat/cron 做外部探活监控、生产 Gateway 优先 extended-stable 线，并对每次更新预设约四分之一的集成中断概率。OpenClaw 的稳定性叙事已从"快速迭代的玩具"转向制度化治理，但其回归密度意味着：长期部署的可靠性目前仍主要由用户的运维纪律，而非框架本身保证。

### 关键发现

- 2026.9.6 单版本引入 3 个 P1 crash-loop 类问题（#170458/#170457/#170693），2026.9.9 出现 P0 发布阻塞（#170545），回归以版本为单位密集出现（[issues 列表](https://github.com/openclaw/openclaw/issues)）
- #95495：2026.6.9 静默迁移记忆库，据 issue 自述 1,499 文件 / 23,694 chunks 索引归零、3.4GB 旧库与 128KB 新壳并存，regression/P1/data-loss，3 天关闭（[#95495](https://github.com/openclaw/openclaw/issues/95495)）
- OOM 有清晰版本谱系：v2026.3.7 回归（#41778，not planned）→ v2026.3.12 全 CLI 泄漏（#45064）→ v2026.3.13 修复；根因系 Node v24 不兼容，降 v22 可解（[LearnClaw](https://learnclaw.cc/openclaw-memory-leak-oom-crash-fix-2026/)）
- 社区实证：约 25% 更新打挂 heartbeat/cron/webhook；7 天不可用与"一个月后放弃"案例；发版前 CI 曾红（[Kilo](https://kilo.org.cn/openclaw/vs-hermes)）
- 版本策略悖论：OpenClaw 137 版 vs Hermes 11 版；"6 版中 3 版不能用"但低频≠稳定；官方以 extended-stable + "等一两个补丁"回应（[Kilo](https://kilo.org.cn/openclaw/vs-hermes)，[2.0 博客](https://openclaws.io/blog/openclaw-2-0-release/)）
- 安全面：6 CVE / 341+ 恶意技能 / 135k+ 暴露实例，暴露实例规模放大了稳定性问题的爆炸半径（[Kilo](https://kilo.org.cn/openclaw/vs-hermes)）

### 数据摘要

| 指标 | 数据 | 来源 |
|------|------|------|
| regression 标签 issue | 历史累计 3,200（Search API 已核验） | [GitHub Search API](https://api.github.com/search/issues?q=repo:openclaw/openclaw+label:regression) |
| #95495 受影响记忆库（据 issue 自述） | 1,499 文件 / 23,694 chunks / 旧库 3.4GB | [#95495](https://github.com/openclaw/openclaw/issues/95495) |
| sessions.cleanup 回归 | <1s（2026.9.9）→ ~27s（2026.10.1） | [#170474](https://github.com/openclaw/openclaw/issues/170474) |
| 更新破坏集成概率（社区自述） | 约 25% | [Kilo](https://kilo.org.cn/openclaw/vs-hermes) |
| 发版数对比（2026.5.8） | OpenClaw 137 vs Hermes 11 | [Kilo](https://kilo.org.cn/openclaw/vs-hermes) |
| 2.0 前发版节奏 | 230 天 106 版，随后 7 周静默 | [2.0 博客](https://openclaws.io/blog/openclaw-2-0-release/) |
| 安全面 | 6 CVE / 341+ 恶意技能 / 135k+ 暴露实例 | [Kilo](https://kilo.org.cn/openclaw/vs-hermes) |
| v2026.9.2 规模 | 1,245 PRs + 232 contributors | [docs.openclaw.ai](https://docs.openclaw.ai/releases/2026.9.2) |

---

## 5. Arch/NixOS 部署适配、ACP 互操作性与双栈选型建议

### 论点

本章逐一验证两套智能体在 Arch Linux 与 NixOS 上的真实落地路径，核心结论：**Arch 侧 AUR 包质量 hermes-agent 明显占优（当日更新、7 票），openclaw 稳定包可用但存在版本滞后，ArchWiki 更推荐官方脚本；NixOS 侧 nix-openclaw 一方 Home Manager 模块在声明式能力、回滚与应用层不可变模式上显著领先 Hermes 的 `nix profile` 方案**。ACP 双栈可行，但必须按 v2026.9.2 安全警告设计 Gateway 拓扑。

### 论据

**一、Arch 侧：AUR 三包逐一验证**

据 AUR 页面实测（截至 2026-10-13）：[openclaw](https://aur.archlinux.org/packages/openclaw) 版本 2026.9.9-1，源为 npm registry 的 tarball（`openclaw-2026.9.9.tgz`），仅依赖 nodejs/npm（npm 为 make 依赖），维护者 ralphptorres，最后更新 2026-10-08，5 票；[openclaw-git](https://aur.archlinux.org/packages/openclaw-git) 为 git 源码 Bun 构建，make 依赖含 bun、cmake、gcc、libvips 等，维护者 SolarAquarion，最后更新 2026-09-27，仅 2 票；[hermes-agent](https://aur.archlinux.org/packages/hermes-agent) 版本 0.21.7-3，上游 GitHub tarball 加 `keep-venv-interpreter.patch`，运行时依赖 nodejs/npm/python/uv/agent-browser，维护者 y0uCeF，**最后更新 2026-10-13（当日）**，7 票，且被 hermes-agent-desktop 等 3 个包依赖。

交叉验证显示两点值得注意：其一，[ArchWiki 中文](https://wiki.archlinux.org.cn/title/OpenClaw)明确写道「目前 AUR 软件包均存在 bug 且不稳定」，长期稳定运行建议改用官方 `curl install.sh | bash`，[remoteclaw 指南](https://remoteclaw.com/tutorials/local/arch-linux.html)亦称「AUR 为社区维护，官方安装器才是 supported path 且通常提供最新稳定版」；而实测 openclaw 稳定包比上游「几乎每天发版」（ArchWiki 语）的节奏滞后约 5 天。其二，ArchWiki 称经 AUR 安装「bubblewrap 沙箱已作为依赖项安装」，但 AUR 页面显示稳定包 openclaw 的依赖列表中并无 bubblewrap，仅 openclaw-git 将其列为**可选**依赖——两来源存在出入，以 AUR 页面为准。另 ArchWiki 记载 nixpkgs 主仓存在 `nixpkgs.openclaw`，但不建议单独为 OpenClaw 引入 Nix（重复依赖占磁盘）。

**二、NixOS 侧：nix-openclaw 一方模块 vs Hermes nix profile**

[OpenClaw Nix 官方文档](https://docs.openclaw.ai/zh-CN/install/nix)确认 nix-openclaw 是第一方 Home Manager 模块：Gateway 与工具全部锁定版本、重启可持续运行的服务、声明式插件系统、`home-manager switch --rollback` 即时回滚。更深一层的差距在 **OPENCLAW_NIX_MODE=1**：该模式下 openclaw.json 被视为**不可变**，`openclaw update`、插件安装/卸载、`doctor --fix`、`config set`、`--generate-gateway-token` 等写操作全部被拒绝，用户只能编辑 Nix 源；launchd/systemd 服务还会自动发现 `NIX_PROFILES` 中的二进制加入 PATH（未设置时回退 `~/.nix-profile/bin`）。Hermes 侧，其 Nix 官方文档（[官方中文页](https://hermes-agent.nousresearch.com/docs/zh-Hans/getting-started/nix-setup)，2026-10-11 前后有更新）记载 `nix profile install` 后 `hermes`、`hermes-agent`、`hermes-acp` 三个命令进入 PATH，运行时**无需 pip、无需虚拟环境、无需 npm install**；NixOS 模块用户则将配置写入 configuration.nix，机密经 sops-nix/agenix 管理（[社区镜像 hermesagent.org.cn](https://hermesagent.org.cn/docs/getting-started/nix-setup) 亦印证运行时无 pip/venv/npm 依赖）。就声明式与机密管理而言双方都有路径，但 Hermes 文档中未见与 Nix 模式对等的「应用层不可变语义 + 显式回滚命令」说明，成熟度差距明显。一个细节：AUR 打包中 hermes-agent 仍将 nodejs/npm 列为运行时依赖，与 Nix flake 宣称的「无 npm」形成对照，这正是「打包策略差异」而非「运行时需求差异」。

**三、资源与本地模型门槛**

关键锚点来自 [v2026.9.2 发布说明](https://docs.openclaw.ai/releases/2026.9.2)：本地模型推荐「begin with an 8 GiB memory floor」，更大模型需更多内存、部分需显卡加速，纯 CPU 推理「可能耗时数分钟」。Hermes 的[中文 Linux 指南](https://hermes-agents.net/zh-cn/install/linux/)给出系统要求：内存 2GB 最低 / 4GB+ 推荐、Python 最低 3.10 / 推荐 3.11+，其一键脚本（install.sh，国内镜像 res1.hermesagent.org.cn）自动装 uv、建 venv、配 PATH，并明确「不要使用 sudo 运行」；该页未提供 systemd unit 配置（安装形态为 venv + alias），另链接有 Docker 部署文档。任务参数中「OpenClaw 300MB 常驻」一说未能在任何来源中证实，本章不采用该数字。

**四、ACP 双栈协作与安全边界**

Hermes 的 `hermes-acp` 命令提供了 ACP Server 能力。[CSDN 2026-09 实操文](https://blog.csdn.net/fwyTech2010/article/details/162519237)（博客级证据，仅辅助）演示了 OpenClaw 与 Hermes 基于 ACP 的双 Agent 协作流程，涵盖依赖安装与 ACP Server 启动。**部署拓扑受 v2026.9.2 的共享 Gateway 警告约束**：若多个 agent 跑在同一 Gateway 上，被省略的设置会让具备 session 工具的 agent 读取、搜索其他 agent 乃至其他用户的对话；官方要求显式收窄可见性与 agent-pair 访问，并明确指出「mutually untrusted users need separate Gateways」。

### 分析：选型矩阵

| 用户场景 | 首选 | 依据 |
|---|---|---|
| NixOS 声明式党 | OpenClaw（nix-openclaw 模块），以 `nix profile` 补 Hermes 跑 ACP | rollback + Nix 模式不可变 + PATH 自动发现 |
| Arch 轻量党 | hermes-agent AUR 包；OpenClaw 走官方 install.sh 或稳定 AUR 包 | hermes 包当日更新/维护活跃；AUR openclaw 有滞后且 ArchWiki 预警 |
| 追新激进党 | openclaw-git 或官方脚本，配合 bubblewrap 沙箱 | git 包更新勤但 make 依赖重、投票低 |
| 长期运行 | NixOS 用 rollback + NIX_MODE 冻结自更新；Arch 锁版本、每次更新后运行 `openclaw doctor` | ArchWiki：「几乎每天发新版本，某些更新会使现有配置失效」 |
| 多用户/多租户 | 拆分 Gateway | v2026.9.2：互不信任的用户必须使用独立 Gateway |

### 小结

Arch 与 NixOS 两条路线的结论恰好镜像互补：**要声明式纪律与回滚，选 OpenClaw on NixOS；要开箱轻量与低门槛，选 hermes-agent on Arch**。ACP 双栈技术上已打通（hermes-acp + OpenClaw Gateway），但真正的部署风险不在安装，而在共享 Gateway 的会话可见性——单用户自用可收窄设置后共享，涉及互不信任用户必须拆 Gateway。

### 关键发现

- AUR hermes-agent 于 2026-10-13 当日更新（0.21.7-3，7 票），openclaw 稳定包滞后约 5 天（2026-10-08）([AUR](https://aur.archlinux.org/packages/hermes-agent), [AUR](https://aur.archlinux.org/packages/openclaw))
- ArchWiki 与 remoteclaw 均不推荐 AUR openclaw 包作为长期稳定方案 ([ArchWiki](https://wiki.archlinux.org.cn/title/OpenClaw), [remoteclaw](https://remoteclaw.com/tutorials/local/arch-linux.html))
- OPENCLAW_NIX_MODE=1 使 openclaw.json 不可变并禁用全部自修改命令 ([OpenClaw Nix 文档](https://docs.openclaw.ai/zh-CN/install/nix))
- Hermes `nix profile install` 提供 hermes/hermes-agent/hermes-acp 三命令，运行时无 pip/venv/npm 依赖 ([官方中文页](https://hermes-agent.nousresearch.com/docs/zh-Hans/getting-started/nix-setup))
- 本地模型 8 GiB 内存底线 + 共享 Gateway 会话可见性警告 ([v2026.9.2 发布说明](https://docs.openclaw.ai/releases/2026.9.2))
- 「OpenClaw 300MB 常驻」未获任何来源证实，本章剔除

### 数据摘要

| 指标 | 数据 | 来源 |
|------|------|------|
| AUR openclaw | 2026.9.9-1，npm tarball，维护者 ralphptorres，2026-10-08 更新，5 票 | [AUR](https://aur.archlinux.org/packages/openclaw) |
| AUR openclaw-git | 2026.9.6.r100068，Bun 源码构建，SolarAquarion，2026-09-27 更新，2 票 | [AUR](https://aur.archlinux.org/packages/openclaw-git) |
| AUR hermes-agent | 0.21.7-3，上游 tarball + patch，y0uCeF，2026-10-13 更新，7 票 | [AUR](https://aur.archlinux.org/packages/hermes-agent) |
| OpenClaw 本地模型门槛 | 8 GiB 内存底线，CPU-only 推理可能数分钟 | [v2026.9.2 发布说明](https://docs.openclaw.ai/releases/2026.9.2) |
| Hermes 系统要求 | 内存 2GB 最低 / 4GB+ 推荐；Python 最低 3.10 / 推荐 3.11+ | [hermes-agents.net](https://hermes-agents.net/zh-cn/install/linux/) |
| v2026.9.2 规模 | 1,245 PRs / 232 contributors | [发布说明](https://docs.openclaw.ai/releases/2026.9.2) |

---

## 结论

五章证据共同回答引言提出的四个问题。记忆维度：两家均已收敛于"有界核心＋可扩展外延"——Hermes 以 2,200/1,375 字符硬上限与会话冻结快照守护 prefix cache（[Hermes 记忆官方文档](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)），OpenClaw 2.0 以 dreaming 巩固与来源追溯补足，且 2.0 onboarding 可平滑导入 Hermes 记忆。自进化维度：路径相反而底线相同——Hermes 的离线 GEPA 管线"永远走人工 PR，永不自动 commit"（[管线仓库](https://github.com/NousResearch/hermes-agent-self-evolution)），OpenClaw 以提案制把自主权关在 apply 之前，双方都拒绝自动 commit。纠错维度：Hermes 的任务级 /rollback、/undo 是社区公认的 OpenClaw 空白，但其自评估虚高可能把错误固化为技能；OpenClaw 迁移期"假成功"事故（[Issue #95495](https://github.com/openclaw/openclaw/issues/95495)，数字以 issue 自述为准）同样说明数据完整性验证不能外包给 agent。稳定性维度：2.0 前 230 天 106 个版本、社区自述约 25% 更新影响 heartbeat/cron/webhook（[Kilo 评论分析](https://kilo.org.cn/openclaw/vs-hermes)），"迭代快"不等于"可托管"，Hermes 低频发版亦未经同规模验证。

选型结论：NixOS 声明式党选 OpenClaw＋nix-openclaw 不可变模式；Arch 轻量党选 hermes-agent（[AUR 页面](https://aur.archlinux.org/packages/hermes-agent)）更省心；长期运行场景一律锁版本＋备份子系统＋doctor 体检；互不信任的多用户必须拆分 Gateway（[v2026.9.2 说明](https://docs.openclaw.ai/releases/2026.9.2)）。后续研究可纵向追踪 extended-stable 线的故障收敛曲线，以及 Hermes 自进化管线第一阶段之后的落地形态。

---

## 参考文献

### 官方来源（一手）

- OpenClaw 2.0 官方发布博客, 2026, OpenClaw [openclaws.io/blog/openclaw-2-0-release](https://openclaws.io/blog/openclaw-2-0-release/)
- OpenClaw Release notes 索引, 2026, OpenClaw [docs.openclaw.ai/releases](https://docs.openclaw.ai/releases)
- OpenClaw v2026.9.2 release notes, 2026, OpenClaw [docs.openclaw.ai/releases/2026.9.2](https://docs.openclaw.ai/releases/2026.9.2)
- OpenClaw v2026.9.3 release notes, 2026, OpenClaw [docs.openclaw.ai/releases/2026.9.3](https://docs.openclaw.ai/releases/2026.9.3)
- OpenClaw Memory overview 官方文档, 2026, OpenClaw [docs.openclaw.ai/concepts/memory](https://docs.openclaw.ai/concepts/memory)（终审期抓取失败，仅搜索摘要口径）
- OpenClaw Nix 安装官方文档, 2026, OpenClaw [docs.openclaw.ai/zh-CN/install/nix](https://docs.openclaw.ai/zh-CN/install/nix)
- OpenClaw Skill Workshop 官方文档, 2026, OpenClaw [docs.openclaw.ai/zh-CN/tools/skill-workshop](https://docs.openclaw.ai/zh-CN/tools/skill-workshop)
- OpenClaw Doctor 官方文档, 2026, OpenClaw [docs.openclaw.ai/zh-CN/gateway/doctor](https://docs.openclaw.ai/zh-CN/gateway/doctor)
- Hermes Agent 官网（中文）, 2026, Nous Research [hermes-agent.org/zh](https://hermes-agent.org/zh/)
- Hermes 持久化记忆官方文档, 2026, Nous Research [hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/memory)
- Hermes 技能系统官方文档, 2026, Nous Research [hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/skills](https://hermes-agent.nousresearch.com/docs/zh-Hans/user-guide/features/skills)
- Hermes Nix & NixOS 安装官方文档, 2026, Nous Research [hermes-agent.nousresearch.com/docs/zh-Hans/getting-started/nix-setup](https://hermes-agent.nousresearch.com/docs/zh-Hans/getting-started/nix-setup)
- NousResearch/hermes-agent GitHub 仓库, 2026, Nous Research [github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- NousResearch/hermes-agent-self-evolution 仓库 README（离线 GEPA 管线）, 2026, Nous Research [github.com/NousResearch/hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution)
- agentskills.io 开放技能标准, 2026, AgentSkills [agentskills.io](https://agentskills.io)

### GitHub Issues（一手故障证据）

- Issue #41778：v2026.3.7 message OOM 回归（not planned 关闭）, 2026, OpenClaw GitHub [issues/41778](https://github.com/openclaw/openclaw/issues/41778)
- Issue #45064：v2026.3.12 全 CLI OOM, 2026, OpenClaw GitHub [issues/45064](https://github.com/openclaw/openclaw/issues/45064)
- PR #46522：OOM 修复（v2026.3.13）, 2026, OpenClaw GitHub [pull/46522](https://github.com/openclaw/openclaw/pull/46522)
- Issue #170458：模型目录 worker 堆增至多 GB 冻结事件循环, 2026, OpenClaw GitHub [issues/170458](https://github.com/openclaw/openclaw/issues/170458)
- Issue #170457：禁用插件仍派生子进程且不回收, 2026, OpenClaw GitHub [issues/170457](https://github.com/openclaw/openclaw/issues/170457)
- Issue #170693：session-migration 重扫致 Gateway 启动失败, 2026, OpenClaw GitHub [issues/170693](https://github.com/openclaw/openclaw/issues/170693)
- Issue #170644：Gateway 启动热重载自我重启, 2026, OpenClaw GitHub [issues/170644](https://github.com/openclaw/openclaw/issues/170644)
- Issue #170525：macOS 合盖唤醒强制重启, 2026, OpenClaw GitHub [issues/170525](https://github.com/openclaw/openclaw/issues/170525)
- Issue #95495：静默迁移记忆库（data-loss，数字以 issue 自述为准）, 2026, OpenClaw GitHub [issues/95495](https://github.com/openclaw/openclaw/issues/95495)
- Issue #170545：P0 release-blocker（更新执行器结算失败）, 2026, OpenClaw GitHub [issues/170545](https://github.com/openclaw/openclaw/issues/170545)
- Issue #170474：sessions.cleanup 性能回归, 2026, OpenClaw GitHub [issues/170474](https://github.com/openclaw/openclaw/issues/170474)
- Issue #134608 / #134169：2.0 迁移"假成功"簇, 2026, OpenClaw GitHub [issues/134608](https://github.com/openclaw/openclaw/issues/134608), [issues/134169](https://github.com/openclaw/openclaw/issues/134169)
- regression 标签检索（累计 3,200 条，Search API 已核验）, 2026, OpenClaw GitHub [api.github.com/search](https://api.github.com/search/issues?q=repo:openclaw/openclaw+label:regression)

### 社区与第三方

- Kilo：1,300 条 Reddit 评论分析（OpenClaw vs Hermes）, 2026, Kilo [kilo.org.cn/openclaw/vs-hermes](https://kilo.org.cn/openclaw/vs-hermes)（单一社区分析源，社区感受类数据的主要来源）
- Hermes 自进化机制拆解, 2026, tanteng [blog.tanteng.space/posts/hermes-agent-self-evolution](https://blog.tanteng.space/posts/hermes-agent-self-evolution/)
- Hermes Agent 深度用法指南, 2026, cfanzp [cfanzp008.github.io/hermes-agent-usage-guide](https://cfanzp008.github.io/hermes-agent-usage-guide/)
- studyopenclaw：OpenClaw 2.0 版重塑记忆, 2026-09-03, studyopenclaw [studyopenclaw.cn/openclaw-2-0-rebuilds-memory-2026](https://studyopenclaw.cn/openclaw-2-0-rebuilds-memory-2026)
- LearnClaw：OpenClaw 内存泄漏与 OOM 排障, 2026-05, LearnClaw [learnclaw.cc/openclaw-memory-leak-oom-crash-fix-2026](https://learnclaw.cc/openclaw-memory-leak-oom-crash-fix-2026/)
- Hermes vs OpenClaw 全面对比（阿里云开发者社区）, 2026-05-20 [developer.aliyun.com/article/1735598](https://developer.aliyun.com/article/1735598)（结构完整但含厂商导流，结论性内容已交叉验证）
- ArchWiki 中文：OpenClaw, 2026, ArchWiki 中文社区 [wiki.archlinux.org.cn/title/OpenClaw](https://wiki.archlinux.org.cn/title/OpenClaw)
- remoteclaw：Arch Linux 安装指南, 2026, remoteclaw [remoteclaw.com/tutorials/local/arch-linux.html](https://remoteclaw.com/tutorials/local/arch-linux.html)
- Hermes Linux 安装指南（中文）, 2026-05-29, hermes-agents.net [hermes-agents.net/zh-cn/install/linux](https://hermes-agents.net/zh-cn/install/linux/)
- AUR openclaw（2026.9.9-1）, 2026, ralphptorres [aur.archlinux.org/packages/openclaw](https://aur.archlinux.org/packages/openclaw)
- AUR openclaw-git, 2026, SolarAquarion [aur.archlinux.org/packages/openclaw-git](https://aur.archlinux.org/packages/openclaw-git)
- AUR hermes-agent（0.21.7-3）, 2026, y0uCeF [aur.archlinux.org/packages/hermes-agent](https://aur.archlinux.org/packages/hermes-agent)
- 知乎：ClawHub 必装 Skills 清单（13,729 口径）, 2026-03, 知乎专栏 [zhuanlan.zhihu.com/p/2013332031464043740](https://zhuanlan.zhihu.com/p/2013332031464043740)
- 阿里云开发者社区：从0到1玩转 13000+ OpenClaw Skill（13,625 口径）, 2026-03-05 [developer.aliyun.com/article/1714840](https://developer.aliyun.com/article/1714840)（与上一篇同源，计作单一社区证据）
- CSDN：OpenClaw+Hermes 基于 ACP 的双 Agent 协作实操, 2026-09, CSDN [blog.csdn.net/fwyTech2010/article/details/162519237](https://blog.csdn.net/fwyTech2010/article/details/162519237)
- CSDN RickyIT：Hermes Skill 系统深度（agentskills.io 兼容）, 2026-05, RickyIT [blog.csdn.net/RickyIT/article/details/160418358](https://blog.csdn.net/RickyIT/article/details/160418358)

### 已排除来源（质量说明）

- 腾讯云开发者社区《Hermes Agent vs OpenClaw 8 维度实测》, 2026-07-24 [developer.cloud.tencent.com/article/2715416](https://developer.cloud.tencent.com/article/2715416)：描述 OpenClaw 为 Python/RabbitMQ/ChromaDB 栈、Hermes 为 v2.4.1/4.2k stars，与官方一手事实（Node 栈/33 万星、Hermes v0.21.7/MIT）系统性冲突，疑为 AI 生成内容，全文未采用。

---

## 待完善事项

1. **#95495 精确数字未独立复核**：终审期 4 次抓取该 issue 页面均失败，1,499 文件/23,694 chunks/3.4GB 数字为撰稿期据 issue 自述口径，建议人工复核。
2. **regression 未关闭条数未复核**：3,200 累计数已由 Search API 核验，"当前未关闭 118 条"未带 state:open 独立查询证实。
3. **社区感受类数据单一来源**：25% 更新破坏率、+107/+25 赞评论、6 CVE/341+ 恶意技能/135k+ 暴露实例均转引 Kilo 单一 Reddit 分析，置信度低于官方来源。
4. **OpenClaw 官方中文博客与 Memory 概念页多轮抓取失败**：相关论述以英文原版博客与第三方深读为据（第 1 章已脚注说明）。
5. **Hermes GitHub issue 稳定性对比缺失**：撰稿期三次探测仓库未命中，未能完成双方 issue 密度对比；后续如可访问应补做。
6. **Workshop 机制高速迭代**：2.0 后每 1—2 周一个版本，任何 Workshop 行为断言都应在使用时按版本号复核。

---

## 方法论说明

- 数据截止 2026-10-13；AUR 包状态为该日实测。
- OpenClaw 2.0 官方博客中文页多次抓取返回空，报告统一引用内容一致的英文原版页面（openclaws.io/blog/openclaw-2-0-release/）。
- 事实性陈述均带超链接引用；社区自述数据与官方数据已分别标注口径。

---

> 本报告由 AI 深度研究团队生成，重要决策请经专业人员核验。所有引用来源请用户在重要场景下二次核验时效性与真实性。

