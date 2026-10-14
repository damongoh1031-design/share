# 模型越强，Skills 还需要吗？

> **核心问题**：在 Opus 5.5 / GPT-6 Astra 这一代模型的能力下，Skills 是否还需要？是否约束了模型的能力？哪些仍然必备？
>
> **结论先说**：
> 1. **需要，但分工会迁移**——从「补模型的能力短板」转向「注入模型无从知道的私有上下文 + 守住硬边界」。
> 2. **确实会约束模型，而且有硬数据**：Claude Code 为适配 Opus 5 **删掉了 80% 以上的系统提示词**，消融测试甚至发现删掉后模型有时**显得更聪明**。
> 3. **判定标准是「模型相对的」，且官方给了可执行测试**：*"Would the agent get this wrong without this instruction? If the answer is no, cut it."*
> 4. **数量应该减少，但单位价值应该上升。** 判断标准从「有用吗」变成「**它装的是模型不可能知道的东西吗**」。
>
> **核验方式**：2026-10-14 抓取 Anthropic 官方工程博客、agentskills.io 规范与最佳实践原文（`.md` 端点）、mattpocock 的 `writing-for-agents` SKILL.md 原文、Agent-Skills-for-Context-Engineering README，以及中文/英文独立测评与学术引用。
>
> **配套文件**：`report.html`（可视化）、`data/evidence.json`（证据分级与原文引语）、`data/classification.json`（skill 三分类映射）

---

## 〇 先破一个前提

**「模型更强 → skills 更没用」这个推论是错的。** 一线厂商和学术界的表述恰好相反。

### 证据 1：Anthropic 官方（2025-10-16）

> **Claude is powerful, but real work requires procedural knowledge and organizational context.**
>
> **As model capabilities improve**, we can now build general-purpose agents that interact with full-fledged computing environments... **But as these agents become more powerful, we need more composable, scalable, and portable ways to equip them with domain-specific expertise.**

**注意这句话的因果方向**：不是「模型弱所以需要 skills」，而是「**模型强了，才更需要 skills**」——因为强模型把瓶颈从「会不会做」推到了「知不知道」。

同一篇文章的类比很精准：

> Building a skill for an agent is like putting together an **onboarding guide for a new hire**.

新员工能力再强，也需要知道**你们公司**的报销流程。这就是 skills 的定位。

### 证据 2：agentskills.io 规范首句

> **Agents are increasingly capable, but often don't have the context they need to do real work reliably.** Skills solve this by packaging **procedural knowledge and company-, team-, and user-specific context** into portable, version-controlled folders that agents load on demand.

### 证据 3：学术界

**北京大学通用人工智能国家重点实验室** 2026 年论文《Meta Context Engineering via Agentic Skill Evolution》：

> **静态技能架构是 Agent 的基石**，而动态演化上下文则是从「手动工程」跨越到「自主进化」的桥梁。

该论文引用 `Agent-Skills-for-Context-Engineering` 为「static skill architecture」的基础工作。同一仓库还被 **CMU / Yale / JHU / NEU / Tulane / UAB / OSU / Virginia Tech / Amazon** 合著的《Agent Harness Engineering: A Survey》(2026) 引用。

**「基石」和「桥梁」是两个不同的东西**——skills 是地基，动态上下文演化是在地基上盖的楼。不是替代关系。

### 证据 4：模型能力本身是不均衡的

一份 2026-09 的 40 道编程题实测（GPT-6 Astra / Claude Opus 5.5 / Grok 4.7）：

| 模型 | 纯算法题 | 并发锁状态机 | SQL 优化 | 首 token 延迟 |
|---|---|---|---|---|
| GPT-6 Astra | **强** | **正确率掉到 55%** | — | — |
| Claude Opus 5.5 | — | **通过率最高** | **最高** | **常飙到 1400ms+** |
| Grok 4.7 | — | — | — | **最低** |

**「最强模型」在具体任务上是分层的。** 一个针对并发状态机注入团队既有模式的 skill，在 Astra 上依然有价值——因为它的短板恰在那里。

### 结论：瓶颈迁移了，不是消失了

| | 2023-2024 | 2026+ |
|---|---|---|
| **瓶颈** | 模型会不会做 | 模型知不知道 |
| **skills 的作用** | 能力补丁（教它怎么做） | **上下文注入**（告诉它你的世界长什么样） |
| **随模型变强的趋势** | 贬值 | **升值** |

---

## 一 Skills 确实会约束模型 —— 五个精确机制

「约束」这个担忧是对的，但笼统地说「限制能力」不准确。**有五个可验证的具体机制**：

### 机制 1：能力补丁会过期，而过期补丁会主动误导

**最硬的证据**：2026 年，Claude Code 创造者 **Boris Cherny** 在 Y Combinator 公开对谈中提到，**为了适配 Opus 5，他们删掉了 Claude Code 超过 80% 的系统提示词**。

那 80% 主要来自旧模型的能力补丁。更关键的是：

> 团队做消融测试时甚至发现，**去掉这些提示后，模型有时会显得更聪明一些**。

**这是「skills 约束模型」最直接的证据**——不是理论推演，是产品团队的消融实验。

### 机制 2：含糊或冲突的规则会让模型过早停止

**OpenAI 在 GPT-6 Astra 官方使用指南中专门提醒**：

> 新模型能够遵循更长、更复杂的指令，**同时也会对 Skill、AGENTS.md 等可访问的指令文件更加敏感**。含糊或相互冲突的规则，可能让模型**过早停下来确认**；过宽的测试要求，也可能让一个小修改触发**远超必要范围的检查**。

**机制很反直觉**：模型能力弱时，一条多余规则只是一段没发挥作用的文字；**模型执行能力增强后，它更可能认真完成这条规则**——于是多读文件、多做测试、多走流程，甚至因为两个边界互相冲突而停止推进。

**即：越强的模型，越会「忠诚地执行」你的错误指令。** 这是「约束」的第二重含义，而且比第一重更危险。

### 机制 3：成本增加，但成功率不增——且成本与长度无关

**ETH Zurich 与 LogicStar.ai 的实证研究**（300 个 SWE-bench Lite 任务 + 138 个 CTXbench 任务，多种编码 Agent）：

| 条件 | 成功率变化 | 成本变化 |
|---|---|---|
| **自动生成的**仓库级上下文文件 | **无显著提升** | **+20%** |
| **开发者亲手写的**上下文文件 | +2.4%（**统计上不显著**） | 同样增加成本 |

**最关键的一个发现**：

> 实验结果与**文件长度没有明显关系**，成本增加更可能来自**每条指令所触发的行为**。

**这句话的分量很重**：删掉一半字数不解决问题。要删的是**会诱发无效行动的指令**。

> **注意口径**：这项研究测的是「常驻上下文文件」（AGENTS.md 类，每轮都加载），不是「按需加载的 skills」。skills 因为有渐进式披露，理论成本更低。但这个结论对 skills 同样适用——**只要一条指令触发了行为，成本就产生了**。

### 机制 4：锁死判断，压缩模型找更短路径的空间

**Eric Provencher**（OpenAI，负责 Codex 开发者体验）在讨论 Astra 的 Prompt 与 Skill 设计时：

> Skill 的入口应当尽量像一个**简洁的路由器**，把详细资料留到真正需要时再加载；**为旧模型写下的固定路线和繁复配方，则应该重新检查**。模型已经能够处理的判断，继续被步骤锁死，**反而会压缩它寻找更短路径的空间**。

「压缩它寻找更短路径的空间」——这是「约束」的第四重含义：**不是做错，而是做得更笨**。

### 机制 5：否定式指令会反向激活被禁行为

`writing-for-agents`（mattpocock）原文：

> **Negation** is the failure mode beside this lever: steering by prohibition **drags the forbidden behaviour into context and makes it _more_ available, not less**. *Don't think of an elephant*, and the elephant is all there is; the negation is a weak modifier the strongly-activated concept overruns, so **the ban half-reads as an instruction to do the thing**.

> Prompt the **positive**: state the target behaviour ("write one-line comments") so the banned one is never spoken.

**所以「禁止事项」清单本身就是一种约束伤害**——你越写「不要 X」，X 在上下文里的激活度越高。

---

## 二 官方给的判定标准（可执行）

好消息是：**Anthropic 在规范里给了明确、可执行的测试**，不需要凭感觉。

### 2.1 核心测试：一句话

agentskills.io 最佳实践原文：

> **Ask yourself about each piece of content: "Would the agent get this wrong without this instruction?" If the answer is no, cut it. If you're unsure, test it. And if the agent already handles the entire task well without the skill, the skill may not be adding value.**

**这是全文最重要的一句话。** 它同时给出了：
1. **删除标准**：模型不会做错的，删
2. **不确定时**：去测，不要辩论
3. **整份 skill 的判据**：模型本来就能做好整个任务 → 这个 skill 可能没在增加价值

### 2.2 这个标准是「模型相对的」，不是「读者相对的」

`writing-for-agents` 把这一点讲得极清楚：

> Hunt **no-ops** sentence by sentence: an instruction the model already obeys by default pays load to say nothing. **The test (does it change behaviour versus the default?) is model-relative, not reader-relative**: two people disagreeing about a no-op disagree about the default, and **settle it by running the document, not by debate**. When a sentence fails, **delete the whole sentence rather than trim words from it**.

**「两个人对是不是 no-op 有分歧，本质是对『模型的默认行为是什么』有分歧」** —— 这句话解释了为什么这个争论在公司里总是吵不出结果：**大家在用自己的模型心智模型辩论**。

### 2.3 官方 A/B 评估法

`evaluating-skills` 原文给出的方法极其简单：

> The core pattern is to run each test case **twice: once with the skill and once without it** (or with a previous version). This gives you a baseline to compare against.

**目录结构**：

```
your-skill/
├── evals/
│   └── evals.json          # prompt + expected_output (+ files)
├── iteration-1/
│   ├── case-1/
│   │   ├── with_skill/
│   │   └── without_skill/   ← 基线
│   └── case-2/...
```

**测试用例设计要点**（官方）：
- **先写 2-3 个**，不要一开始就投入太多
- **变化 prompt**：有的随意（"hey can you clean up this csv"），有的精确（"Parse the CSV at data/input.csv, drop rows where column B is null"）
- **至少一个边界条件**（畸形输入、异常请求、指令可能歧义的场景）
- **用真实上下文**（真实文件路径、列名）——"process this data" 这种太模糊，测不出东西

### 2.4 Boris 的「先全删，再逐条加回」

Claude Code 适配新模型的方法论：

> 每次适配新模型，**先移除原有系统提示，再逐条恢复并观察每一条的实际影响**。

**这是把「删」当成默认动作，把「留」当成需要举证的决定。** 与传统习惯（默认保留、偶尔清理）完全相反。

### 2.5 诊断信号：从执行轨迹看，不只看最终输出

官方原文：

> **Read agent execution traces, not just final outputs.** If the agent wastes time on unproductive steps, common causes include:
> - instructions that are **too vague** (the agent tries several approaches before finding one that works)
> - instructions that **don't apply to the current task** (the agent follows them anyway)
> - **too many options presented without a clear default**

**第二条最关键**：「指令不适用于当前任务，但 agent 还是照做了」——这正是「模型变强反而被约束」的表现。

---

## 三 哪些还必备？—— 五类「永不失效」的 skill

把「会不会过期」当坐标轴，所有 skill 可以分成五类。**只有后四类值得留**：

### 类别 A：能力补丁 —— 会过期，应持续瘦身 ⚠️

**特征**：教模型「怎么做一件通用的事」。

| 典型 skill | 会过期的部分 | 该保留的部分 |
|---|---|---|
| `tdd` | 「先写测试再写实现」——模型现在会 | 「**接缝（seam）必须先与用户确认**」——这是你们团队的约定 |
| `diagnosing-bugs` | 「建回路→最小化→假设→插桩」——模型现在会 | 「**必须先有一个能稳定复现的 red 回路，才允许动手修**」——硬门槛 |
| `grill-me` | 「开工前问清需求」——模型现在会 | 「**需求未对齐前不许开始实现**」——门禁 |
| `code-review` | 「两轴审查」——模型现在会 | 你们的**编码规范** + 原 issue 在哪 |
| `brainstorming` | 大概率整份已是 no-op | 可能无 |
| `prototype` | 部分 no-op | 「原型必须是一次性的、不进主干」——纪律 |

**处理方式**：不是删掉，而是**只留硬门槛，删掉教学部分**。

### 类别 B：私有上下文注入 —— 长期有效，随模型变强而升值 ✅

**特征**：装的是模型**不可能知道**的东西。这是官方定义的核心价值。

`writing-for-agents` 给了一个极精确的判据：

> The **environment** is a source of truth too (`package.json` scripts, config files, the directory layout, `--help` output), and a document that restates it is a **cache**: a copy of a lookup, earning its load only when the lookup is expensive. **Cache what the agent cannot find by looking: the unwritten convention, the reason behind a choice, the gotcha no config confesses.**

**「缓存那些 agent 查不到的东西：没写下来的约定、某个选择背后的原因、任何配置文件都不会坦白的坑。」**

| 典型 skill | 装的是什么私有信息 |
|---|---|
| `domain-modeling` / `GLOSSARY.md` | **你们团队的术语**。原文例子：`"the materialization cascade"` 替掉 20 个词的描述 |
| `codebase-design` | **你们的架构词汇约定**。原文硬性要求只能用 module/interface/depth/seam，**不许说 component/service/API/boundary** |
| `setup-matt-pocock-skills` | 你们的 issue tracker 在哪、用什么标签、文档放哪 |
| `writing-for-agents` | 你们给 agent 写文档的规范 |
| **官方企业 skill**（Azure 582 / 飞书 22 / Prisma 95 / Supabase 17 / Clerk 31） | **你们的云账号、表结构、API、权限模型** |
| `extract-design-system` | **你们的设计令牌** |
| `lark-doc` 等飞书 22 件套 | **你们公司的文档/审批/OKR 结构** |

**这一类的判断标准**：问「模型不装这个，能靠搜索/读代码/试错搞明白吗？」——**能，就不必要；不能，就是必备。**

### 类别 C：硬边界与确定性 —— 长期有效 ✅

**特征**：不该交给概率判断的部分。

官方最佳实践里有一句关键的校准原则：

> **Match specificity to fragility.** Give the agent freedom when multiple approaches are valid and the task tolerates variation... **Be prescriptive when operations are fragile, consistency matters, or a specific sequence must be followed.**

| 典型 skill | 装的是什么硬边界 |
|---|---|
| `git-guardrails-claude-code` | 危险 git 命令护栏 |
| `handoff` 的脱敏段 | *"Redact any sensitive information, such as API keys, passwords, or personally identifiable information."* |
| `triage` 的标注要求 | *"Every comment or issue posted... **must** start with: > *This was generated by AI during triage.*"* |
| `caveman` | 确定性压缩，不靠模型自觉 |

**⚠️ 关键补充**：Anthropic 官方明确指出，**能用代码的就不该用自然语言**：

> Large language models excel at many tasks, but certain operations are better suited for traditional code execution. For example, **sorting a list via token generation is far more expensive than simply running a sorting algorithm**. Beyond efficiency concerns, **many applications require the deterministic reliability that only code can provide.**

> In our example, the PDF skill includes a pre-written Python script that reads a PDF and extracts all form fields. **Claude can run this script without loading either the script or the PDF into context.** And because code is deterministic, this workflow is consistent and repeatable.

**所以 Anthropic 的 `docx` / `pdf` / `pptx` / `xlsx` 是这一类里最典型的**——它们**不是提示词，是确定性代码**。模型再强，跑排序算法也比逐 token 生成便宜得多。**这类 skill 永远不会因为模型变强而失效。**

### 类别 D：随模型变强而「升值」的新必备 ✅

**特征**：模型越强，越需要它们来管理模型。

| skill | 为什么随模型变强而升值 |
|---|---|
| `find-skills` | 模型越强，自己发现/评估 skill 的能力越强，这个入口价值越高 |
| `skill-creator` | Anthropic 原话：*"we hope to enable agents to **create, edit, and evaluate Skills on their own**"* |
| **上下文工程类**（`context-compression` / `filesystem-context` / `memory-systems` / `self-managed-context`） | **因为瓶颈迁移到了上下文**——见下方 |
| `research` | 溯源纪律，与模型能力无关，但与「可信度」强相关 |

**为什么上下文工程类会升值**：`Agent-Skills-for-Context-Engineering` 说得很透：

> The fundamental challenge is that **context windows are constrained not by raw token capacity but by attention mechanics**. As context length increases, models exhibit predictable degradation patterns: the "lost-in-the-middle" phenomenon, **U-shaped attention curves**, and **attention scarcity**.

**窗口再大也解决不了注意力稀缺。** 所以「如何筛选、压缩、调度信息」的重要性只会上升。

该项目的实测数据（Digital Brain 案例）：**用渐进式披露，token 消耗降低 60%，任务成功率提升 45%。**

### 类别 E：可审计 / 可复现 —— 合规场景长期有效 ✅

skills 的一个被低估的价值：它让 agent 行为**可审查、可版本控制、可复现**。

官方原文：

> **Repeatable workflows**: Turn multi-step tasks into **consistent, auditable procedures**.
> **Cross-product reuse**: Build a skill once and use it across any skills-compatible agent.

**这不是「模型做不到」，而是「组织需要留痕」。** 只要 AI 参与有合规要求的流程，这一类就永远需要——**与模型能力无关**。

---

## 四 实操：给自己的 skills 做一次「减法」

把上面的原则变成一个可执行流程。**建议在每次模型大版本升级时跑一遍。**

### 第 1 步：先全删（或全禁用），跑代表性任务

学 Boris 的方法：**把「删」当默认，把「留」当需要举证的决定**。

具体做法：新建一个只保留 skill 元数据的配置，或用 `--list` 类命令禁用全部，然后跑你日常最典型的 5-10 个任务。

### 第 2 步：只把「稳定复现的失败」加回来

观察模型在**没有** skills 时：
- 哪里反复失败？
- 哪里反复问你？
- 哪里产出了不符合你们约定的东西？

**只对稳定复现的缺口加回指令。**

### 第 3 步：逐条 A/B 验证

用官方方法：同一 prompt 跑两次，`with_skill` vs `without_skill`。

**判据**：
- 成功率无提升 + 成本上升 → **删**
- 成功率提升但不稳定 → 再跑几轮
- 模型本来就能做好 → **删**（官方原话：*"the skill may not be adding value"*）

### 第 4 步：分类归位

| 内容类型 | 归到哪 |
|---|---|
| 私有事实、约定、坑 | **skill**（按需加载） |
| 确定性逻辑（排序、校验、格式转换） | **脚本**（不占上下文） |
| 人的决策（目标、取舍、验收标准） | **保持为指令** |
| 能力教学（"先思考再回答"） | **删** |
| 禁止事项清单 | **改写成正面表述** |
| 通用最佳实践（"handle errors appropriately"） | **删**（官方明确点名这是无效内容） |

### 第 5 步：定期体检两个失败模式

`writing-for-agents` 命名了这两个病：

| 病 | 定义 | 症状 |
|---|---|---|
| **Sediment**（沉积） | *"stale layers that settle because **adding feels safe and removing feels risky**, until you must core down through them to find what is still live."* | 文件越改越长，没人敢删 |
| **Sprawl**（蔓延） | *"a document simply too long, **even when every line is live and unique**. Attention thins across the excess."* | 每行都对，但整体太长 |

**注意 Sprawl 的定义**：**即使每一行都是活的、唯一的，太长也是问题。** 这推翻了「只要没废话就没关系」的直觉。

### 第 6 步：用「引导词」压缩，而不是加规则

`writing-for-agents` 提供了一个正向技巧：

> A **leading word** is a compact concept **already living in the model's pretraining** that the agent thinks with while running the document (_lesson_, _fog of war_, _tracer bullets_). Repeated as a token, never as a sentence, it **accumulates a distributed definition** and anchors a whole region of behaviour in the fewest tokens, **by recruiting priors the model already holds**.

**即：模型越强，预训练里「装」的概念越多，一个词能锚定的行为区域越大。** 这本身就是「模型变强让 skills 可以更短」的正面证据。

例子：
- "fast, deterministic, low-overhead" → **`tight`**（a `tight` loop）
- "a loop you believe in" → **`red`**（循环在 bug 上变 `red`，或不变——把模糊门槛变成二元可观测状态）

**警告**：*"a made-up word recruits no priors: you pay in definition tokens what a pretrained word gives free"* —— 自造词没有预训练红利。

---

## 五 一个反直觉的结论

**模型越强 → skills 的数量应该减少，但单位价值应该上升。**

| | 模型弱时 | 模型强时 |
|---|---|---|
| **skills 该装几个** | 多（补短板） | **少**（补上下文） |
| **每份 skill 该多长** | 长（详细步骤） | **短**（只留私有事实 + 硬边界） |
| **判断标准** | 「有用吗」 | 「**它装的是模型不可能知道的东西吗**」 |
| **失效信号** | 模型做不对 | **模型照做了不该做的指令** |

**最后一个变化最重要**：模型弱时，skill 失效的信号是「没效果」；**模型强时，skill 失效的信号是「太有效」**——它忠实地执行了你为旧模型写的补丁，从而多做了无用功。

### 那到底还剩什么？

如果只能留 5 个，按「模型不可能知道」排序：

1. **你们的领域术语表**（`GLOSSARY.md` / `domain-modeling`）——模型猜不出 `materialization cascade` 指什么
2. **你们的架构词汇约定**（`codebase-design`）——模型默认会说 component/service，但你们要求说 module/seam
3. **企业官方 skill**（Azure / 飞书 / Prisma / Supabase）——**你们的账号、表结构、权限模型**
4. **硬边界护栏**（`git-guardrails` + 脱敏 + 审计标注）——不该交给概率判断
5. **确定性代码**（`docx`/`pdf`/`pptx`/`xlsx`）——不是提示词，是脚本，永远比 token 生成便宜

**这五个的共同点：都不教模型「怎么做」，只告诉模型「你的世界长什么样、边界在哪」。**

---

## 六 一个仍然开放的问题

必须诚实标注一个**本轮未能回答**的问题：

**skills 的「降方差」价值，是否独立于「提成功率」的价值？**

- 支持方：官方定义里有 *"Repeatable workflows: Turn multi-step tasks into **consistent, auditable** procedures"*——一致性本身就是价值
- 反对方：ETH Zurich 的实证显示，开发者亲手写的上下文文件只带来 **+2.4% 平均提升，且统计上不显著**，同时增加成本

**这两种说法不矛盾但也不互相支持。** 「一致性」的价值难以用 SWE-bench 这类成功率指标衡量——它衡量的是「每次是否一样」，而不是「是否更对」。

**如果你所在的组织对「行为可预测」有硬需求（金融、医疗、合规），降方差本身就值得成本。否则，按成功率判断即可。**

---

## 七 数据可信度

### 7.1 来源分级

| 级别 | 来源 | 可信度 |
|---|---|---|
| **A 级（一手原文）** | Anthropic 官方工程博客全文；agentskills.io 规范 + 最佳实践 + 评估方法（`.md` 端点原文）；`writing-for-agents` SKILL.md 全文；`Agent-Skills-for-Context-Engineering` README | **高** |
| **B 级（官方转述 + 具名）** | Boris Cherny（Claude Code 创造者）在 Y Combinator 的对谈；OpenAI GPT-6 Astra 官方使用指南；Eric Provencher（OpenAI Codex DX） | 中高（**经中文二手转述，未取得英文原文**） |
| **C 级（学术）** | 北大《Meta Context Engineering via Agentic Skill Evolution》(arXiv 2601.21557)；CMU/Yale 等《Agent Harness Engineering: A Survey》(2026)；ETH Zurich + LogicStar.ai 实验 | 中高（**论文原文未逐字核验，为引用转述**） |
| **D 级（实测测评）** | 40 道编程题三模型对比（知乎，2026-09-28） | 中（单一来源、样本量未知） |

### 7.2 明确未核实 / 存疑项

1. **Boris Cherny 的「80%」和「消融测试显示删掉后更聪明」**：来自中文科技媒体转述的 YC 对谈内容，**未取得英文原文或视频记录**。这是本文最关键的论据之一，建议自行核对原始来源。
2. **OpenAI GPT-6 Astra 官方使用指南的具体措辞**：同上，为中文转述。
3. **ETH Zurich + LogicStar.ai 实验**：数据（+20% / +23% / +2.4%）为转述，**未读取论文原文**。且该实验测的是「常驻上下文文件」而非「按需加载的 skills」，**不能直接外推到 skills**。
4. **北大论文**：仅确认了「静态技能架构是 Agent 的基石」这句引用，**未读全文**，无法评估其方法论。
5. **`Agent-Skills-for-Context-Engineering` 的「token 降 60% / 成功率升 45%」**：来自项目自述的单一案例（Digital Brain），**非受控实验**。
6. **40 道编程题对比**：单一来源，未说明题目分布、重复次数、评分方式。
7. **Opus 5.5 的状态**：搜索结果提到「Claude Opus 5.5」代号 `claude-wafer-eap`，为 API 形式提供；而 **Claude Opus 5 于 2026-07-24 发布**。两者关系（5.5 是 5 的迭代还是下一代）**未确认**。GPT-6 Astra 于 **2026-09-03 发布**。
8. **「skills 是否约束模型」缺乏受控实验**：本轮所有证据都是间接的（产品团队经验、上下文文件实验、官方指南警告）。**没有见到「同一模型 + 同一任务 + 有/无 skill」的公开对照实验数据。** 这本身是一个值得注意的空白——官方给的 A/B 方法正是为了让你自己做这个实验。

### 7.3 本轮方法说明

**一个技术细节**：agentskills.io 的文档页正文是 JS 渲染的，直接抓 HTML 只能拿到目录。**在 URL 后加 `.md` 可以拿到完整 Markdown 原文**（如 `https://agentskills.io/skill-creation/best-practices.md`），站点还在 `/llms.txt` 提供了全站文档索引。这个技巧对本轮获取官方原文至关重要。

---

*报告生成：2026-10-14 ｜ 核验：Anthropic 官方博客 + agentskills.io 规范原文（.md 端点）+ SKILL.md 原文 + 学术引用 + 独立测评 ｜ 本机环境：Windows 11*
