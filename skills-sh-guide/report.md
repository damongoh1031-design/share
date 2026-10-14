# skills.sh 必备 Skills 深度调研

> **调研问题**：有什么必备的 skills？skills.sh 上最推荐的是什么？各种不同场景下推荐什么？这些 skill 能做什么、解决什么问题？
>
> **核验方式**：主代理于 **2026-10-14** 直接抓取 skills.sh 三张榜单（All Time / Trending / Hot）原始 HTML，解析出**完整 176 条排行榜**（排名 + 安装量）；逐一抓取 6 个主要仓库的 README 与 19 个 Anthropic 官方 SKILL.md 原文；对 8 个代表性 skill 抓取详情页核实能力与**安全审计状态**。
>
> **配套文件**：`report.html`（可视化）、`data/leaderboard.json`（176 条完整榜单）、`data/skills-detail.json`（代表性 skill 详情与安全审计）、`data/fetch_leaderboard.py`（可复跑）

---

## 〇 结论速览

### skills.sh 是什么

**Vercel 出品的 Agent Skills 目录与排行榜**，2026-01-20 上线。站点自称 "**The Agent Skills Directory**" / "**The Open Agent Skills Ecosystem**"。

一条命令安装：

```bash
npx skills add <owner/repo>
# 例：npx skills add mattpocock/skills --skill tdd
```

支持 **20 个 agent**（页面实测）：Claude Code、Cursor、Codex、GitHub Copilot、Windsurf、Gemini、Cline、AMP、Antigravity、OpenClaw、Droid、Goose、Kilo、Kiro CLI、Nous Research、OpenCode、Roo、Trae、VS Code、Zed。CLI 本身支持更多（README 称 "**75 more**"）。

### 最重要的一个发现：榜单被少数几个组织垄断

176 条榜单里，**超过一半来自 5 个组织**：

| 组织 | 上榜数量 | 代表 skill |
|---|---|---|
| **mattpocock/skills** | **约 45 个** | grill-me、tdd、handoff、triage、improve-codebase-architecture |
| **heygen-com/hyperframes** | **21 个** | hyperframes、product-launch-video、faceless-explainer |
| **open.feishu.cn（飞书官方）** | **22 个** | lark-doc、lark-base、lark-wiki、lark-okr（**单组织合计 16.9M 安装**） |
| **microsoft/azure-skills** | **约 17 个** | azure-compliance、azure-compute、azure-kubernetes |
| **leonxlnx/taste-skill** | **约 15 个** | design-taste-frontend、high-end-visual-design |
| prime-skills/runcomfy-agent-skills | 约 12 个 | video-edit、image-to-video、nano-banana-2 |

**这意味着**：所谓「skills.sh 最推荐的」很大程度上是**「mattpocock 和 heygen 最推荐的」**。看到高排名先看 owner。

### 分层必装清单

| 层级 | Skill | 安装量 | 解决什么 |
|---|---|---|---|
| **元技能（第一个装）** | **`find-skills`**（vercel-labs/skills） | **3.8M** | 让 agent 自己去找并装 skill |
| **需求对齐** | **`grill-me`**（mattpocock/skills） | 1.4M | 开工前把需求问清楚，避免返工 |
| **架构守护** | **`improve-codebase-architecture`** | 1.1M | 定期体检代码库，找出该重构的模块 |
| **测试** | **`tdd`**（mattpocock/skills） | 1.1M | 红绿重构循环，产出值得留的测试 |
| **浏览器自动化** | **`agent-browser`**（vercel-labs） | 1.1M | 让 agent 真的能操作网页 |
| **前端设计** | **`frontend-design`**（anthropics/skills） | 985.0K | 拒绝「AI 味」的界面设计 |
| **跨会话交接** | **`handoff`**（mattpocock/skills） | 979.1K | 把当前对话压缩成交接文档 |
| **调试** | **`diagnosing-bugs`**（mattpocock/skills） | 777.5K | 难 bug 的纪律化诊断循环 |
| **省 token** | **`caveman`**（juliusbrussee/caveman） | 572.4K | 让 agent 少说少读，省 33%+ input token |
| **中文办公** | **`lark-doc`** 等（飞书官方） | 770.1K | 飞书文档/多维表格/IM 全打通 |

### 一句警告

**装之前一定看 skill 页面的 Security Audits。** skills.sh 对每个 skill 显示三家审计结果（Gen Agent Trust Hub / Socket / Snyk），实测发现**连高排名 skill 也有 Warn 和 Fail**：

- `triage`（938.7K 安装）→ **Gen Agent Trust Hub: Warn、Snyk: Warn**
- `design-mobile-apps`（799.9K 安装）→ **Snyk: Fail**

---

## 一 skills.sh 平台怎么用

### 1.1 三个榜单的差别

| 榜单 | 指标 | 适合 |
|---|---|---|
| **All Time** | `8W Activity` + `Installs`（8 周活跃 + 累计安装） | 判断长期价值 |
| **Trending (24h)** | `Installs`（24 小时） | 看这周什么在起来 |
| **Hot** | `1H / Change`（1 小时 + 增量） | 看此刻什么在爆 |

**实测差异很大**：All Time 前 10 全是开发/设计类；Trending 前 10 里 **7 个是 heygen 的视频生成类**（hyperframes-cli 32.9K、hyperframes-audio 28.4K、motion-graphics 20.6K…）；Hot 榜前列则是 `limrun-bazel`、`ponytail`、`clickhouse-best-practices` 这类刚起步的。

**结论**：**只看 All Time 会漏掉正在起势的；只看 Trending 会被单一厂商刷屏。**

### 1.2 安装方式

```bash
# 基础安装（owner/repo 简写）
npx skills add vercel-labs/agent-skills

# 指定单个 skill
npx skills add https://github.com/mattpocock/skills --skill tdd

# 装到用户目录而非项目（全局）
npx skills add mattpocock/skills -g

# 只看有哪些 skill，不装
npx skills add mattpocock/skills --list

# 不安装，直接生成 prompt 喂给 agent
npx skills use vercel-labs/agent-skills@web-design-guidelines | claude
npx skills use vercel-labs/agent-skills --skill web-design-guidelines --agent claude-code

# 指定目标 agent
npx skills add mattpocock/skills -a claude-code -a codex
```

**支持多种来源**（README 实测）：GitHub 简写 / 完整 URL / 仓库内子路径 / GitLab / Azure Repos / 任意 git URL / 本地路径 / **私有仓库**（复用 Git 凭证、`gh` CLI 或 SSH）。

### 1.3 单个 skill 页面有什么

抓取详情页实测，每个 skill 页显示：

- **Installs**（安装量）
- **Repository** + **GitHub Stars**（仓库星数）
- **First Seen**（首次收录日期）
- **Security Audits**：Gen Agent Trust Hub / Socket / Snyk 三家结果
- **Summary**（一句话摘要）
- **SKILL.md**（完整原文）
- 一键安装命令

**这四组数据合起来才能判断一个 skill 值不值得装。**

---

## 二 全站 Top 40（2026-10-14 实测）

完整 176 条见 `data/leaderboard.json`。以下为前 40：

| # | Skill | 来源 | 安装量 |
|---|---|---|---|
| 1 | **find-skills** | vercel-labs/skills | **3.8M** |
| 2 | **grill-me** | mattpocock/skills | 1.4M |
| 3 | **grill-with-docs** | mattpocock/skills | 1.2M |
| 4 | **agent-browser** | vercel-labs/agent-browser | 1.1M |
| 5 | **improve-codebase-architecture** | mattpocock/skills | 1.1M |
| 6 | **tdd** | mattpocock/skills | 1.1M |
| 7 | hyperframes-cli | heygen-com/hyperframes | 1.0M |
| 8 | setup-matt-pocock-skills | mattpocock/skills | 997.5K |
| 9 | **frontend-design** | **anthropics/skills** | 985.0K |
| 10 | **handoff** | mattpocock/skills | 979.1K |
| 11 | hyperframes | heygen-com/hyperframes | 961.9K |
| 12 | **triage** | mattpocock/skills | 938.7K |
| 13 | **prototype** | mattpocock/skills | 934.3K |
| 14 | reddit-automation | flowkit-labs/skills | 925.5K |
| 15 | **grilling** | mattpocock/skills | 907.9K |
| 16 | media-use | heygen-com/hyperframes | 885.0K |
| 17 | hyperframes-animation | heygen-com/hyperframes | 853.1K |
| 18 | hyperframes-registry | heygen-com/hyperframes | 842.4K |
| 19 | **domain-modeling** | mattpocock/skills | 816.5K |
| 20 | **teach** | mattpocock/skills | 808.1K |
| 21 | hyperframes-core | heygen-com/hyperframes | 803.0K |
| 22 | design-mobile-apps | designed-by-ai/skills | 800.0K |
| 23 | vercel-react-best-practices | vercel-labs/agent-skills | 799.2K |
| 24 | **codebase-design** | mattpocock/skills | 792.3K |
| 25 | **diagnosing-bugs** | mattpocock/skills | 777.5K |
| 26 | hyperframes-creative | heygen-com/hyperframes | 775.2K |
| 27 | **lark-doc** | open.feishu.cn | 770.1K |
| 28 | web-design-guidelines | vercel-labs/agent-skills | 734.2K |
| 29 | **code-review** | mattpocock/skills | 729.7K |
| 30 | **implement** | mattpocock/skills | 718.4K |
| 31 | ask-matt | mattpocock/skills | 715.7K |
| 32 | wayfinder | mattpocock/skills | 664.8K |
| 33 | to-spec | mattpocock/skills | 661.4K |
| 34 | hyperframes-keyframes | heygen-com/hyperframes | 659.8K |
| 35 | **research** | mattpocock/skills | 658.9K |
| 36 | to-tickets | mattpocock/skills | 655.3K |
| 37 | remotion-best-practices | remotion-dev/skills | 615.1K |
| 38 | design-taste-frontend | leonxlnx/taste-skill | 606.8K |
| 39 | **caveman** | juliusbrussee/caveman | 572.4K |
| 40 | general-video | heygen-com/hyperframes | 569.7K |

**读法提醒**：mattpocock 一家占了前 40 里的 **18 个**。这不代表它们都「必备」——**它们是同一个作者的一套完整方法论，装整套才有意义**（见第四章）。

---

## 三 分场景推荐（核心章节）

### 3.1 元技能层 —— 先装这个

#### `find-skills`（vercel-labs/skills，3.8M，全站第一）

**它做什么**：让 agent 自己去发现并安装 skill。

**详情页原文**：

> Discover and install specialized agent skills from the open ecosystem when users need extended capabilities.
>
> - Helps identify relevant skills by domain and task when users ask "how do I do X" or "find a skill for X"
> - Provides `npx skills find [query]` command to search interactively and `npx skills add <package>` to install from GitHub or other sources
> - Recommends skills based on **install count (prefer 1K+)**, **source reputation (official sources like Vercel, Anthropic)**, and **GitHub stars** to ensure quality
> - **Checks the skills.sh leaderboard first** for battle-tested, popular options before running CLI searches

**解决什么**：你不用再手动逛榜单——直接问 agent「有没有做 X 的 skill」，它自己去查、去比、去装。

**为什么它排第一**：它是**入口**。装了它，后面所有 skill 的发现成本归零。

#### `skill-creator`（anthropics/skills，405.1K）

**原文**：*"Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test..."*

**解决什么**：找不到合适的就自己造。这是官方出的**造 skill 的 skill**。

> 另有 `obra/superpowers` 的 `writing-skills`（含测试方法论）和 mattpocock 的 `writing-for-agents` / `writing-great-skills`，都是「怎么给 agent 写文档」的元技能。

### 3.2 需求对齐 / 设计阶段 —— 最被低估的一类

#### `grill-me`（mattpocock/skills，1.4M，全站第二）

**详情页原文**：

> Relentless interviewing skill that stress-tests plans and designs through systematic questioning.
>
> - Conducts **deep-dive questioning across all aspects of a plan**, walking through decision trees branch-by-branch until shared understanding is reached
> - Automatically explores the codebase to answer questions where code context is available, reducing redundant back-and-forth
> - Designed for **design reviews, architecture validation, and pre-implementation planning** where thorough vetting prevents downstream issues

**解决什么**：**AI 编程最高频的失败模式是「它做的不是你要的」。** 这个 skill 强制在动手前把需求问透。

作者原文（README）：

> The most common failure mode in software development is misalignment. You think the dev knows what you want. Then you see what they've built - and you realize it didn't understand you at all. This is just the same in the AI age. There is a communication gap between you and the agent. **The fix for this is a grilling session.**

#### `grill-with-docs`（1.2M）

比 `grill-me` 多了**构建领域模型**：边问边更新 `GLOSSARY.md` 和 ADR。作者的例子很有说服力：

> **BEFORE**: "There's a problem when a lesson inside a section of a course is made 'real' (i.e. given a spot in the file system)"
> **AFTER**: "There's a problem with the materialization cascade"

**收益**（作者原文）：变量/函数/文件名用统一语言命名 → 代码库更易导航 → **agent 思考更省 token**。

#### `grilling`（907.9K）—— 底层原语

**原文**：*"Interview the user relentlessly about a plan, decision, or idea until every branch of the design tree is resolved. **The reusable interview primitive behind** `grill-me`, `grill-with-docs`, `triage`, `wayfinder` and `improve-codebase-architecture`."*

即：`grill-me` 是「入口」，`grilling` 是「引擎」。装 `grill-me` 时它会被自动调用。

#### `domain-modeling`（816.5K）

**原文**：*"Actively build and sharpen a project's domain model: challenge terms against the glossary, stress-test with edge-case scenarios, and update `GLOSSARY.md` and ADRs inline."*

#### `brainstorming`（obra/superpowers，391.2K）

**原文**：*"Drawing out intent before building"*

#### `prototype`（934.3K）

**原文**：*"Build a throwaway prototype to answer a design question, either a single shareable HTML file for state/logic questions, or several radically different UI variations toggleable from one route."*

**解决什么**：不确定的设计问题，**先用一次性原型验证，别直接写进正式代码**。

### 3.3 开发流程 —— 从 spec 到合并

这是 mattpocock 生态最完整的部分。**它们是一条流水线，单独装一个价值有限**：

| 阶段 | Skill | 安装量 | 做什么 |
|---|---|---|---|
| 配置（每仓库跑一次） | `setup-matt-pocock-skills` | 997.5K | 配 issue tracker、triage 标签、领域文档位置 |
| 找路 | `ask-matt` | 715.7K | 路由器：告诉你该用哪个 skill |
| 规划 | `to-spec` | 661.4K | 把当前对话转成 spec 并发布到 issue tracker |
| 拆票 | `to-tickets` | 655.3K | 把计划拆成 tracer-bullet 工单，标注阻塞关系 |
| 大工程规划 | `wayfinder` | 664.8K | 规划**超过一个 agent session 容量**的大块工作 |
| **实现** | `implement` | 718.4K | 按 spec/工单施工，在约定接缝上跑 `/tdd`，收尾跑 `/code-review` |
| 批量实现 | `implement-spec` | 235.0K | 在一个集成分支上实现整个 spec，**并行 subagent 打满就绪前沿** |
| 代码审查 | `code-review` | 729.7K | **两轴审查**：Standards（编码规范 + Fowler 坏味道基线）+ Spec（是否忠实实现原 issue），跑并行子代理互不污染 |
| PR | `pr` | — | PR 正文的形态：最小可视化摘要 + 前后证据 + 合并风险评级 |
| 收尾 | `retro` | 225.1K | 复盘并建议改进 agent 环境（导航、自动检查、规范、steering 文件） |

#### `tdd`（1.1M）—— 值得单独说

**详情页原文**：

> Test-driven development with vertical slices, behavior-focused tests, and incremental red-green-refactor cycles.
>
> - Emphasizes **integration-style tests that verify behavior through public APIs, not implementation details**; tests should survive refactors unchanged
> - Requires **vertical slicing** (one test → one implementation → repeat) instead of horizontal slicing (all tests first, then all code), preventing brittle, behavior-insensitive test suites
> - Includes planning phase to confirm interface changes, prioritize behaviors to test, and design for testability before writing code

**SKILL.md 原文的关键概念**：

> A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.
>
> **Test only at pre-agreed seams.** Before writing any test, write down the seams under test and confirm them with the user. No test is written at an unconfirmed seam.

**解决什么**：AI 写的测试往往「测实现细节」，一重构就全红。这个 skill 强制测**行为**、在**接缝**上测。

#### `codebase-design`（792.3K）+ `improve-codebase-architecture`（1.1M）

**`codebase-design` 提供词汇表**：module、interface、depth、seam、adapter、leverage、locality。原文要求 *"Use these terms exactly in every suggestion, and don't drift into 'component,' 'service,' 'API,' or 'boundary.'"*

**`improve-codebase-architecture` 详情页原文**：

> Analyze codebases for architectural friction and propose **module-deepening refactors** as testability improvements.
>
> - Explores codebases organically to surface **shallow modules, tightly-coupled components, and untested seams** rather than following rigid heuristics
> - Applies John Ousterhout's **"deep module"** principle: small interfaces hiding large implementations for better testability and AI navigability
> - Generates **multiple radically different interface designs** (minimalist, flexible, caller-optimized, ports & adapters) via **parallel sub-agents**, then recommends the strongest approach
> - Creates GitHub issue RFCs documenting the problem space, design trade-offs, and refactoring rationale

作者建议：**每隔几天在代码库上跑一次**。原文自我定位很克制：*"It is a survey, not a rescue: on a genuinely old codebase it will find real candidates, but it won't untangle the mud for you."*

**解决什么**：作者的诊断——*"agents can radically speed up coding, they also **accelerate software entropy**. Codebases get more complex at an unprecedented rate."*

#### `obra/superpowers` 的对应能力（15 个 skill）

**这是一套完整方法论**，README 原文：

> As soon as it sees that you're building something, it *doesn't* just jump into trying to write code. Instead, it **steps back and asks you what you're really trying to do**. Once it's teased a spec out of the conversation, it shows it to you **in chunks short enough to actually read and digest**. After you've signed off on the design, your agent puts together an implementation plan that's clear enough for **an enthusiastic junior engineer with poor taste, no judgement, no project context, and an aversion to testing** to follow. It emphasizes **true red/green TDD, YAGNI, and DRY**.
>
> Next up, once you say "go", it launches a ***subagent-driven-development*** process... It's not uncommon for your agent to **work autonomously for a couple hours at a time** without deviating from the plan.

技能分组（README "What's Inside"）：

- **Testing**：`test-driven-development`
- **Debugging**：`systematic-debugging`（4 阶段根因流程）、`verification-before-completion`、`diagnosing-superpowers`
- **Collaboration**：`brainstorming`、`writing-plans`、`executing-plans`、`dispatching-parallel-agents`、`requesting-code-review`、`receiving-code-review`、`using-git-worktrees`、`finishing-a-development-branch`、`subagent-driven-development`
- **Meta**：`writing-skills`、`using-superpowers`

**与 mattpocock 的区别**：superpowers **自动触发**（"the skills trigger automatically, you don't need to do anything special"）；mattpocock 主要是**手动调用**（`/grill-me` 这种）。**二选一，别都装**——都装会重复。

### 3.4 调试与排错

#### `diagnosing-bugs`（mattpocock/skills，777.5K）

**原文**：

> Disciplined diagnosis loop for hard bugs and performance regressions: **build a feedback loop that goes red on this bug → minimise → hypothesise → instrument → fix → regression-test.**

**解决什么**：难 bug 靠猜是猜不出来的。强制先建一个「能稳定复现」的反馈回路，再最小化、再假设、再插桩。

#### `systematic-debugging`（obra/superpowers，291.8K）

**原文**：*"4-phase root cause process (includes root-cause-tracing, defense-in-depth, condition-based-waiting techniques)"*

#### `verification-before-completion`（obra/superpowers，238.3K）

**原文**：*"Ensure it's actually fixed"*

**解决什么**：AI 最常犯的错是「声称修好了但没验证」。这个 skill 强制在宣布完成前做验证。

### 3.5 协作与交接

#### `handoff`（mattpocock/skills，979.1K）

**详情页原文**：

> Summarize conversations into handoff documents for seamless agent-to-agent transitions.
>
> - Compacts current conversation context into a structured document saved to the **OS temp directory**, enabling fresh agents to resume work without re-reading full chat history
> - **Automatically suggests relevant skills** the next agent should invoke based on conversation content
> - Avoids duplication by **referencing existing artifacts (PRDs, plans, ADRs, issues, commits, diffs) by path or URL** rather than repeating their content
> - **Redacts sensitive data including API keys, passwords, and PII** before handoff
> - Tailors handoff focus based on user-provided arguments describing the next session's goals

**SKILL.md 原文**（很短，说明它很聚焦）：

> Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS (`$TMPDIR`, else `/tmp`; `%TEMP%` on Windows) - not the current workspace.
>
> Include a "**suggested skills**" section in the document, naming which skills the next agent should call the Skill tool for.
>
> Do not duplicate content already captured in other artifacts. Reference them by path or URL instead.
>
> **Redact any sensitive information**, such as API keys, passwords, or personally identifiable information.

**解决什么**：上下文窗口满了 / 要换 agent / 要开会中断时，把上下文无损压缩，而不是从头讲一遍。

#### `triage`（938.7K）

**详情页原文**：

> State machine-driven issue triage with role-based workflow management and agent brief generation.
>
> - **Two category roles** (`bug`, `enhancement`) and **five state roles** (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) guide issues through a standardized workflow
> - Supports querying unlabeled issues, in-progress triage, and issues awaiting reporter feedback
> - Includes **reproduction testing for bugs, grilling sessions for incomplete issues**, and templates for triage notes and agent briefs
> - Respects prior triage context, codebase ADRs, and out-of-scope knowledge bases

**一个很好的设计细节**（SKILL.md 原文）：triage 期间发的每条评论都**必须**以这句话开头：

```
> *This was generated by AI during triage.*
```

**解决什么**：issue 堆积、状态混乱。而且**主动标注 AI 生成**，避免误导。

#### `wait-what`（399.5K）

**原文**：*"Fire this the moment a message doesn't land. The agent re-pitches it with the context you're missing, in plain English, using your `GLOSSARY.md` vocabulary."*

**解决什么**：agent 说的你没听懂时，不用忍着，直接触发重新解释。

#### `to-questionnaire`（450.2K）

**原文**：*"Turn a decision you can't answer alone into a Markdown questionnaire for the one person who can, filled in async, or together over a meeting. **It grills you about the send** (who it's for, what you need back), **not the subject**."*

### 3.6 学习与研究

#### `teach`（808.1K）

**原文**：*"Teach the user a new skill or concept over multiple sessions, using the current directory as a **stateful teaching workspace**."*

**解决什么**：把「学一个东西」变成跨会话的持续过程，而不是每次从零问。

#### `research`（658.9K）

**详情页原文**：

> **Spin up a background agent to do the research, so you keep working while it reads.**
>
> Its job:
> 1. Investigate the question against **primary sources** (official docs, source code, specs, first-party APIs), **not a secondary write-up of them**. Follow every claim back to the source that owns it.
> 2. Write the findings to a single Markdown file, **citing each claim's source**.
> 3. Save it where the repo already keeps such notes

**解决什么**：研究不阻塞你干活，且**每条结论都要溯源到一手资料**。

#### `academy-guide`（anthropics/skills）

**原文**：*"Stop and check this skill before finishing any reply to a question about how to use Claude or a Claude product — it recommends matching courses, tutorials, and use cases..."*

### 3.7 前端 / UI 设计

#### `frontend-design`（anthropics/skills，985.0K）—— 官方出品，排名最高的非 mattpocock 开发类 skill

**详情页原文**：

> **Distinctive, production-grade frontend interfaces that reject generic AI aesthetics** through intentional design choices.
>
> - Guides **aesthetic direction selection** (brutalist, maximalist, retro-futuristic, luxury, organic, etc.) before implementation
> - Emphasizes **typography, color theming with CSS variables, motion design, spatial composition, and textural details** as core design pillars
> - Generates working code (HTML/CSS/JS, React, Vue) that matches implementation complexity to the aesthetic vision
> - **Explicitly avoids overused fonts, clichéd color schemes, and predictable layouts** that characterize generic AI-generated interfaces

**SKILL.md 原文的开场设定**（很能说明它的思路）：

> Approach this as the design lead at a design studio known for giving every client a distinct visual identity that is not mistaken for anyone else's. This client has already **rejected proposals that felt cliché or templated**, and is paying for a distinctive point of view.

以及一条很具体的反套路规则：

> a big number with a small label, supporting stats, and a gradient accent is **the default treatment, so only use it if that's truly the best option**.

**解决什么**：**AI 生成的界面千篇一律**。这个 skill 强制先定美学方向，再写代码。

#### `web-design-guidelines`（vercel-labs/agent-skills，734.2K）

**README 原文**：*"Review UI code for compliance with web interface best practices. Audits your code for **100+ rules** covering accessibility, performance, and UX."*

覆盖：Accessibility（aria-label、语义 HTML、键盘处理）、Focus States、Forms、Animation（`prefers-reduced-motion`）、Typography（弯引号、省略号、`tabular-nums`）、Images、Performance（虚拟化、布局抖动、preconnect）、Navigation & State（URL 反映状态、深链）、Dark Mode & Theming、Touch & Interaction、Locale & i18n（`Intl.DateTimeFormat`）

**注意**：它和 `frontend-design` 是**互补**的——前者是「**创造**好看的设计」，后者是「**审查**是否符合规范」。

#### `vercel-react-best-practices`（799.2K）

**README 原文**：*"React and Next.js performance optimization guidelines from Vercel Engineering. Contains **40+ rules across 8 categories, prioritized by impact**."*

分类：消除瀑布流（Critical）、包体积优化（Critical）、服务端性能（High）、客户端数据获取（Medium-High）、重渲染优化（Medium）、渲染性能（Medium）、JS 微优化（Low-Medium）

#### `design-taste-frontend`（leonxlnx/taste-skill，606.8K）

leonxlnx 的 taste-skill 有约 15 个 UI 相关 skill 上榜，是**独立设计师路线**，与 Vercel/Anthropic 的官方路线并行。

#### 其他 UI 类

| Skill | 安装量 | 说明 |
|---|---|---|
| `design-mobile-apps`（designed-by-ai） | 800.0K | 通过 sleek.design REST API 生成移动端设计 |
| `ui-ux-pro-max`（nextlevelbuilder） | 395.4K | — |
| `shadcn`（shadcn/ui 官方） | 271.1K | shadcn/ui 组件库 |
| `emil-design-eng`（emilkowalski） | 350.9K | 设计工程 |
| `break-ui`、`animate-expo`（emilkowalski） | Hot 榜 | — |
| `no-ai-slop`（petergyang） | Hot 榜 | 去 AI 味 |
| `make-interfaces-feel-better`（jakubkrehel） | Hot 榜 | 界面手感 |

### 3.8 视频 / 媒体生成 —— 榜单上最大的「新势力」

`heygen-com/hyperframes` 是**开源框架，把 HTML/CSS/媒体/可寻址动画渲染成确定性 MP4**。21 个 skill 上榜，README 原文：

> The skills teach agents the HyperFrames production loop: **plan the video, write valid HTML, wire seekable animations, add media, lint, preview, and render.**

**架构是「路由器 + 创建工作流 + 领域技能」三层**：

| 类型 | Skill | 何时用 |
|---|---|---|
| **路由器** | `/hyperframes` | **任何视频/动画/动态图形需求都先读它** |
| 创建工作流 | `/product-launch-video` | 网站营销/发布/推广视频（≤3 分钟，最佳 30-90 秒） |
| | `/faceless-explainer` | 从任意文本讲清一个概念，视觉全部 LLM 生成 |
| | `/pr-to-video` | GitHub PR → 变更日志/特性揭示视频（走 `gh` CLI） |
| | `/embedded-captions` | 给已有口播视频加字幕 |
| | `/talking-head-recut` | 口播/访谈/播客加设计图形层 |
| | `/motion-graphics` | 短片头/动效（~10 秒内） |
| | `/music-to-video` | 音乐 → 节拍同步视频 |
| | `/slideshow` | 演示/路演/交互式 deck（**输出可导航 deck，不是渲染视频**） |
| | `/general-video` | 兜底：多场景、品牌片、循环 |
| | `/remotion-to-hyperframes` | 把已有 Remotion 组合迁移过来（单向） |
| 领域技能 | `/hyperframes-core` | 组合契约：`data-*` 计时属性、tracks、子组合 |
| | `/hyperframes-animation` | 动画知识：GSAP / Lottie / Three.js / Anime.js / CSS / WAAPI |
| | `/hyperframes-keyframes` | 可寻址关键帧编写 |
| | `/hyperframes-creative` | 非动画的创意方向：调色板、字体、旁白、节拍规划 |

**安装提醒**（README 原文很重要）：

> The picker opens with **nothing pre-selected** — the **Core Skills** group is all you need: the `/hyperframes` router installs each creation workflow **on demand**.
> ⚠️ **a non-interactive or agent run without `--skill` installs all 21**.

即：**非交互安装会一次装 21 个**，务必用 `--skill` 指定。

**其他媒体类**（Trending 榜主力）：

| Skill | 来源 | 安装量（24h） |
|---|---|---|
| ai-image-generation | magentosh/superpowers | 29.9K |
| uizze-ui | uizze/uizze | 27.6K |
| ai-music / video-edit / image-to-video | gencraft-labs/skills | 15.5K |
| ai-video-generation | prime-skills/runcomfy-agent-skills | — |
| kling-3-0 / nano-banana-2 | prime-skills/runcomfy-agent-skills | — |
| remotion-best-practices | remotion-dev/skills | 615.1K |

### 3.9 办公 / 企业

#### 飞书官方（`open.feishu.cn` / `larksuite/cli`）—— **单组织 16.9M 安装，全站最大**

lark-cli README 原文：

> The official **Lark/Feishu** CLI tool, maintained by the **larksuite** team — built for humans and AI Agents. Covers core business domains including Messenger, Docs, Base, Sheets, Slides, Calendar, Mail, Tasks, Meetings, Markdown, and more, with **200+ commands and 26 AI Agent Skills**.

覆盖 **18 个业务域**：Calendar、Messenger、Docs、Drive、Markdown、Base（多维表格）、Sheets、Slides、Tasks、Wiki、Contact、Mail、Meetings、Attendance、Approval、OKR、Project（Meegle）、Apps

上榜的飞书 skill 包括：`lark-doc`（770.1K）、`lark-okr`、`lark-markdown`、`lark-vc-agent`、`lark-base`、`lark-wiki`、`lark-workflow-standup-report`、`lark-openapi-explorer`、`lark-skill-maker`、`lark-approval`、`lark-slides`、`lark-attendance`、`lark-drive`、`lark-note`、`lark-apps`

**架构亮点**（README 原文）：三层命令系统 —— **Shortcuts（人和 AI 友好）→ API Commands（平台同步）→ Raw API（全覆盖）**；安全上做**输入注入防护、终端输出净化、OS 原生钥匙串存凭证**。

**为什么值得注意**：**这是榜单上唯一一个中国厂商官方、且体量最大的生态。** 装飞书 skill 等于让 agent 直接操作飞书全家桶。

#### 其他企业类

| 组织 | 上榜 skill 数 | 代表 |
|---|---|---|
| `microsoft/azure-skills` | 约 17 | azure-compliance、azure-compute、azure-messaging、azure-kubernetes、azure-rbac、azure-cost、azure-reliability、entra-agent-id |
| `prisma/skills` | 8 | prisma-client-api、prisma-database-setup、prisma-cli、prisma-postgres、prisma-upgrade-v7 |
| `supabase/agent-skills` | 2 | supabase-postgres-best-practices、supabase |
| `neondatabase/agent-skills` | 1 | neon-postgres |
| `clickhouse/agent-skills` | 1 | clickhouse-best-practices |
| `google/agents-cli` | 1 | google-agents-cli-adk-code |

### 3.10 营销 / 增长

| Skill | 来源 | 安装量 | 说明 |
|---|---|---|---|
| `reddit-automation` | flowkit-labs/skills（doany.ai） | **925.5K** | 在 Reddit 找真正需要你产品的人，**诚实披露身份**后回复 |
| `seo-audit` | coreyhaines31/marketingskills | 227.4K | 网站 SEO 审计 |

`reddit-automation` 原文值得一读（它的伦理立场很明确）：

> Reddit rewards real contribution and punishes spam. The way to market here is **not to hide** — it's to genuinely help, **disclose your affiliation**, and only bring up your product when it truly answers the question. This skill runs two moves: **find the few threads where you can actually help, then draft a reply worth posting.**

### 3.11 省 token / 成本控制 —— 一个被忽视的品类

#### `caveman`（juliusbrussee/caveman，572.4K）

**这个 skill 很有意思，且有第三方学术验证。**

README 原文：

> **Caveman make your AI agent say less and read less. Code stay exact. Brain still big.**

**第三方验证**（README 引用）：

| 来源 | 实验 | 结果 |
|---|---|---|
| **Adobe Research**（CAVEWOMAN 论文，引用了本仓库） | Caveman 风格输出，8 模型 × 5 数据集 | **每模型成本降 1.4-2.4 倍，最高 3 倍** |
| **Elasticsearch Labs** | Caveman 模式重制到 ES，8 个真实 MCP 场景 | **响应 token 少 63.6%**，"Zero information loss" |
| **JetBrains** | 86 个真实编码任务，配对 A/B | **无质量损失**（p = 0.82），输出 token 少 8.5% |

**六个组成部分**（v4.0，可单独开关）：

| 部分 | 做什么 | 实测 |
|---|---|---|
| **Say less** | agent 回答短，代码保持精确 | 63 → 20 token，同样修复 |
| **Read less** | 日志/JSON/CSV/测试输出在模型读之前先压缩 | **input token 少 33.2%** |
| **Auto** | 按任务选模型和 effort | 比 Opus xhigh **便宜 54%**，同分 |
| **Blocks** | code mode：agent 保留写过的脚本并复用 | 一次测试运行 **397 → 76 token** |
| **Waste fixes** | 找出 token 花在哪并修 | — |
| **Browse** | 网页返回前先压缩 | 页面小 **129.8 倍** |

**两条重要发现**（README 原文，解释了它的设计边界）：

> Adobe: **cavemanning *your* prompt makes answers worse**, so caveman never touches your prompt.
> JetBrains: agent sessions are mostly code and tool calls, which the voice leaves alone. So caveman grew rocks that shrink what the agent *reads* and what it *runs on*.

**输出示例**：

| 指令 | 输出 token |
|---|---|
| 无 | 6,983 |
| `/caveman` | 63 → 20 |
| `/ultracave` | 14 |
| `/megacave` | **13**（甚至用文言/古语） |

安装：`npx @caveman-ai/cli@latest`，支持 Claude、Codex、Gemini CLI、OpenCode 等 30+。

**同类**：`headroomlabs-ai/headroom`（75,305★，压缩工具输出/日志/RAG chunks，JSON 省 60-95% token）、`juliusbrussee/caveman` 家族（caveman-compress、caveman-review、caveman-commit、caveman-stats）

### 3.12 文档与知识管理

#### Anthropic 官方文档三件套（**生产环境在用**）

anthropics/skills README 原文：

> We've also included the document creation & editing skills that power **Claude's document capabilities** under the hood in the `skills/docx`, `skills/pdf`, `skills/pptx`, and `skills/xlsx` subfolders. **These are source-available, not open source**, but we wanted to share these with developers as a reference for more complex skills that are **actively used in a production AI application**.

| Skill | SKILL.md 原文触发条件 |
|---|---|
| **`pdf`** | *"anytime the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs..."* |
| **`docx`** | *"whenever the user wants to create, read, edit, or manipulate Word documents (.docx files) or Word templates (.dotx files)"* |
| **`pptx`** | *"any time a .pptx or .potx file is involved in any way — as input, output, or both"* |
| **`xlsx`** | *"any time a spreadsheet file is the primary input or output"* |

**注意 License 差异**：这两个 skill 是 **source-available，不是 open source**。其他 Anthropic skill 多为 Apache 2.0。

#### 其他 Anthropic 官方 skill（19 个全表）

| Skill | 做什么 |
|---|---|
| `algorithmic-art` | 用 p5.js 做算法艺术（带种子随机与交互参数） |
| `brand-guidelines` | 应用 Anthropic 官方品牌色与字体 |
| `canvas-design` | 用设计哲学创建 .png/.pdf 视觉作品（海报等） |
| `claude-api` | Claude API / SDK 参考（模型 id、定价、参数、流式、工具、MCP、缓存、迁移） |
| `discernment-nudge` | 在给出实质性建议后做「审慎提醒」 |
| `doc-coauthoring` | 结构化文档共创工作流 |
| `frontend-design` | （见 3.7） |
| `internal-comms` | 写各类内部沟通文档 |
| `mcp-builder` | 构建高质量 MCP server |
| `skill-creator` | （见 3.1） |
| `slack-gif-creator` | 为 Slack 优化的动画 GIF |
| `theme-factory` | 给 artifact 套主题（10 个预设主题） |
| `web-artifacts-builder` | 用 React + Tailwind + shadcn/ui 构建复杂 claude.ai HTML artifact |
| `webapp-testing` | 用 Playwright 测试本地 web 应用 |
| `academy-guide` | 推荐 Claude 相关课程/教程 |

#### 文档写作规范

`writing-guidelines`（vercel-labs/agent-skills）：*"Review docs and prose for compliance with the Vercel writing handbook. Audits your pages for **80+ rules** covering voice, structure, content types, code samples, typography, and AI workflow."*

**一个有意思的规则**：禁用词包括 `easy` / `simple` / `quick`。

`mintlify`（mintlify/docs，Hot 榜 131+111）— 文档站构建。

---

## 四 三大生态深度解析

### 4.1 mattpocock/skills —— 榜单的真正主导者

- **289.5K GitHub stars**，约 **45 个 skill 上榜**
- 作者 Matt Pocock（Total TypeScript 作者），newsletter 约 6 万订阅
- 仓库定位原文：*"My agent skills that I use every day to do **real engineering** - not vibe coding."*

**它的设计哲学**（README 原文，很值得读）：

> Developing real applications is hard. Approaches like **GSD, BMAD, and Spec-Kit** try to help by **owning the process**. But while doing so, **they take away your control** and make bugs in the process hard to resolve.
>
> These skills are designed to be **small, easy to adapt, and composable**. They work with any model. They're based on decades of engineering experience.

**一个关键的架构设计**（README 原文）：

> These split on one axis: **who can invoke them**. **User-invoked** skills are reachable only when you type them (e.g. `/grill-me`); their job is to **orchestrate**. **Model-invoked** skills can be invoked by you *or* reached for automatically by the agent when the task fits; they hold the **reusable discipline**. A user-invoked skill may invoke model-invoked skills, but **never another user-invoked one**.

| 分类 | User-invoked（手动） | Model-invoked（可自动） |
|---|---|---|
| **Engineering** | ask-matt、grill-with-docs、triage、improve-codebase-architecture、setup-matt-pocock-skills、to-spec、to-tickets、implement、implement-spec、wayfinder、retro | prototype、diagnosing-bugs、research、tdd、domain-modeling、codebase-design、code-review、pr、wizard |
| **Productivity** | grill-me、handoff、teach、to-questionnaire、wait-what | grilling、writing-for-agents |

**它诊断的 4 个失败模式**（README 原文，这是整个生态的理论基础）：

1. **The Agent Didn't Do What I Want** → 用 `grill-me` / `grill-with-docs`
2. **The Agent Is Way Too Verbose** → 用共享语言（GLOSSARY.md），原文：*"Agents are usually dropped into a project and asked to figure out the jargon as they go. So they **use 20 words where 1 will do**."*
3. **The Code Doesn't Work** → 用 `tdd` / `diagnosing-bugs`，原文引用 *"the rate of feedback is your speed limit"*
4. **We Built A Ball Of Mud** → 用 `improve-codebase-architecture`，原文引用 Kent Beck *"Invest in the design of the system every day."*

**其他值得注意的**：`git-guardrails-claude-code`（463.7K）、`resolving-merge-conflicts`（551.0K）、`wizard`（503.6K，生成交互式 bash 向导让人做只有人能做的事）、`setup-pre-commit`（453.4K）

### 4.2 obra/superpowers —— 最完整的「全自动」方法论

- **15 个 skill**，自动触发
- 支持 **16+ 个 harness**（Claude Code、Antigravity、Codex App/CLI、Cursor、Devin CLI、Factory Droid、Gemini CLI、GitHub Copilot CLI、Grok Build CLI、Kimi Code、OpenCode、Pi、Qwen Code、**Hermes Agent**、Muse）
- 核心创新：**subagent-driven-development**（两阶段审查：先查 spec 合规，再查代码质量）
- 有商业支持通道（sales@primeradiant.com）

**与 mattpocock 的选择建议**：**superpowers 偏「全自动流水线」，mattpocock 偏「手动精细控制」**。前者省心，后者可控。**不要同时装**。

### 4.3 vercel-labs —— 前端与平台侧

两个仓库：
- **`vercel-labs/skills`**：只有 `find-skills`（但它是全站第一）
- **`vercel-labs/agent-skills`**：`vercel-optimize`、`react-best-practices`、`web-design-guidelines`、`writing-guidelines`、`vercel-composition-patterns`、`vercel-react-native-skills`
- **`vercel-labs/agent-browser`**：`agent-browser`（1.1M，全站第 4）

### 4.4 open.feishu.cn —— 唯一上榜的中国厂商生态

见 3.9。**16.9M 总安装量是全站单一组织最高**。lark-cli 是 MIT 开源、Go 写的官方 CLI，覆盖 18 业务域、200+ 命令、26 个 agent skill。

**对中国用户的实际意义**：如果你的工作流在飞书上，这是**投入产出比最高的一批 skill**——装一次，agent 就能操作飞书文档、多维表格、IM、日历、审批、OKR、会议。

---

## 五 安全与陷阱

### 5.1 安全审计状态 —— 装之前必看

**skills.sh 对每个 skill 显示三家审计结果**：Gen Agent Trust Hub、Socket、Snyk。实测结果**并不都是 Pass**：

| Skill | 安装量 | Gen Agent Trust Hub | Socket | Snyk |
|---|---|---|---|---|
| `grill-me` | 1.4M | Pass | Pass | Pass |
| `research` | 658.9K | Pass | — | — |
| `design-mobile-apps` | **800.0K** | Pass | Pass | **❌ Fail** |
| `triage` | **938.7K** | **⚠️ Warn** | — | **⚠️ Warn** |

**结论**：
1. **安装量高 ≠ 安全。** `triage`（938.7K）和 `design-mobile-apps`（800.0K）都在前 25 名，但都有 Warn 或 Fail。
2. **审计结果不一致是常态。** `design-mobile-apps` 是 Pass/Pass/Fail——三家结论不同，说明它们测的维度不同。
3. **Warn/Fail 不等于恶意**，可能是权限过大、外部 API 调用、或依赖问题。但**必须自己看 SKILL.md 判断**。

**实操建议**：

```bash
# 装之前先看它带不带可执行脚本
npx skills add <owner/repo> --list        # 先列出，不安装
# 然后去 skills.sh/<owner>/<repo>/<skill> 看 Security Audits
```

### 5.2 星数与安装量严重脱节

| Skill | GitHub Stars | Installs | 比值 |
|---|---|---|---|
| `design-mobile-apps` | **15** | **799.9K** | 5.3 万倍 |
| `mattpocock/skills`（仓库） | 289.5K | — | — |
| `grill-me` | 289.5K（仓库） | 1.4M | 4.8 倍 |

**说明什么**：`design-mobile-apps` 只有 15 star 却有 80 万安装——**它靠的是榜单曝光和 sleek.design 的商业推广，不是社区认可**。

**判断方法**：**同时看 Stars、Installs、First Seen 三个指标。** 星数低但安装量高的，多半是商业推广驱动。

### 5.3 榜单水分的识别方法

**实测发现三种「刷榜」形态**：

**① 同一 skill 被多个 fork 重复上榜**

Trending 榜里 `ai-video-generation` 出现了 6 次，来自 6 个不同 owner：

```
magentosh/superpowers、101-skills/superpowers、qu-skills/superpowers、
its-a-skill-issue/superpowers、bankai-skills/superpowers、skills-shell/superpowers
```

`ai-image-generation` 同理出现 4 次（magentosh、its-a-skill-issue、bankai-skills、gencraft-labs）。

**② 单一厂商占据整个榜单段位**

Trending 前 10 里 **7 个是 heygen**；All Time 前 40 里 **18 个是 mattpocock**。

**③ 新建仓库陡增**

Hot 榜里 `limrun-bazel`（139+139）、`design-taste-frontend-v2-experimental`（139+139）、`ponytail`（208+117）都是**增量 = 总量**，即当天新建当天上榜。

**识别清单**：

- [ ] 看 owner 是否在榜单上占了 10 个以上（厂商刷屏）
- [ ] 看同一个 skill 名是否出现在多个 owner 下（fork 刷榜）
- [ ] 看 `First Seen` 是否很近（新仓陡增）
- [ ] 看 Stars 与 Installs 的比值是否悬殊
- [ ] **看 Security Audits 是否有 Warn/Fail**

### 5.4 其他陷阱

| 陷阱 | 说明 |
|---|---|
| **非交互安装会装全部** | hyperframes README 明确警告：*"a non-interactive or agent run without `--skill` installs all 21"*。用 `--skill` 指定 |
| **同一能力重复装** | mattpocock 与 superpowers 的 `tdd` / `test-driven-development`、`code-review` / `requesting-code-review` 功能重叠，**同时装会让 agent 重复劳动** |
| **`find-skills` 会推荐基于安装量的 skill** | 它自己的原文：*"Recommends skills based on install count (prefer 1K+)"*——**安装量高不等于适合你** |
| **Anthropic 文档三件套不是开源** | README 原文：*"These are source-available, not open source"* |
| **CLI 支持数 > 榜单支持数** | 榜单页面显示 20 个 agent，但 CLI README 说支持 "75 more"。装之前确认你的 agent 在不在 |
| **`find-skills` 与 WorkBuddy 内置的 `find-skills` 同名** | 本机已有 `find-skills`（codebuddy-plugins-official），注意区分 |

---

## 六 数据可信度

### 6.1 来源分级

| 级别 | 来源 | 可信度 |
|---|---|---|
| **A 级（一手实测）** | skills.sh 三张榜单原始 HTML 解析（176 条完整排名 + 安装量）；6 个仓库 README 原文；19 个 Anthropic SKILL.md 原文；8 个 skill 详情页（含安全审计） | **高** |
| **B 级（官方文档）** | 各仓库 README 自述能力与设计哲学 | 高 |
| **C 级（独立二手）** | 腾讯云开发者社区、CSDN、51CTO、优设网等对榜单的独立测评 | 中 |
| **D 级（厂商自述数据）** | caveman 引用的 Adobe/JetBrains/Elastic 实验数据（**为仓库自述，未独立复核论文**） | 中 |

### 6.2 独立交叉验证

搜索到的第三方测评与本次实测**基本一致**：

- 2026-01 的文章称 skills.sh「5 万人热用」「Top 10 多数为开发者准备」
- 2026-07 的文章称「第一名 240 万热度」（本次实测 `find-skills` 已 **3.8M**，增长合理）
- 多篇文章提到 `seo-audit`、`pricing-strategy` 等非开发类 skill（本次实测 `seo-audit` 排 #174，227.4K）

**一个被反复提到的独立观点**（优设网）：*"做产品、运营、市场的，这个仓库比 Top 10 更值得装。"*

### 6.3 明确未核实 / 存疑项

1. **`8W Activity` 的确切口径**：页面表头写 `8W Activity`，但同一位置也标 `Installs`。推测是「8 周活跃安装」，但**未从官方文档确认**。
2. **`All Time (1,312,146)` 的含义**：推测是收录的 skill 总数，未确认。
3. **`design-mobile-apps` 的 Snyk Fail 具体原因**：未深挖。它通过 sleek.design 的 REST API 工作，需要 `SLEEK_API_KEY`——Fail 可能与外部 API 调用或权限有关。
4. **`triage` 的 Warn 具体原因**：未深挖。它是纯 Markdown 指令型 skill（无脚本），Warn 可能来自「要求 agent 自动往 issue tracker 发评论」这类行为。
5. **各 skill 的实际使用效果**：本轮为**桌面调研 + 数据核验**，未逐个实际安装运行。
6. **Trending/Hot 榜的数字口径**：Trending 显示 `Installs`（24h），Hot 显示 `1H / Change`，与 All Time 的 `8W Activity` 口径不同，**不可直接跨榜比较**。
7. **caveman 引用的 Adobe 论文（arXiv 2606.24083）**：未独立核验论文内容，仅为仓库自述引用。

### 6.4 本轮方法说明

**核心方法：直接解析原始 HTML 而非依赖摘要。**

skills.sh 的榜单是服务端渲染的，安装量在 `<span class="font-mono text-sm text-foreground">3.8M</span>` 这样的结构里。本轮用正则解析出**完整 176 条**（含排名与安装量），比只读前 20 条摘要可靠得多——**这也是发现「同一 skill 被 6 个 fork 重复上榜」的唯一途径**。

---

## 附录：完整 Top 176 榜单

见 `data/leaderboard.json`。以下为第 41-176 名（前 40 见第二章）：

| # | Skill | 来源 | 安装量 |
|---|---|---|---|
| 41 | microsoft-foundry | microsoft/azure-skills | 564.3K |
| 42 | azure-compliance | microsoft/azure-skills | 553.5K |
| 43 | resolving-merge-conflicts | mattpocock/skills | 551.0K |
| 44 | hyperframes-audio | heygen-com/hyperframes | 548.4K |
| 45 | azure-messaging | microsoft/azure-skills | 544.4K |
| 46 | azure-compute | microsoft/azure-skills | 509.2K |
| 47 | ai-image-generation | magentosh/superpowers | 509.0K |
| 48 | wizard | mattpocock/skills | 503.6K |
| 49 | azure-cloud-migrate | microsoft/azure-skills | 502.0K |
| 50 | google-agents-cli-adk-code | google/agents-cli | 495.0K |
| 51 | lark-doc | larksuite/cli | 469.8K |
| 52 | product-launch-video | heygen-com/hyperframes | 468.8K |
| 53 | lark-base | larksuite/cli | 467.6K |
| 54 | git-guardrails-claude-code | mattpocock/skills | 463.7K |
| 55 | lark-wiki | larksuite/cli | 463.2K |
| 56 | azure-quotas | microsoft/azure-skills | 457.3K |
| 57 | paper-context-resolver | lllllllama/rigorpilot-skills | 457.0K |
| 58 | lark-workflow-standup-report | larksuite/cli | 456.7K |
| 59 | lark-openapi-explorer | larksuite/cli | 456.5K |
| 60 | repo-intake-and-plan | lllllllama/rigorpilot-skills | 456.2K |
| 61 | lark-skill-maker | larksuite/cli | 456.2K |
| 62 | minimal-run-and-audit | lllllllama/rigorpilot-skills | 456.2K |
| 63 | env-and-assets-bootstrap | lllllllama/rigorpilot-skills | 456.1K |
| 64 | faceless-explainer | heygen-com/hyperframes | 454.2K |
| 65 | setup-pre-commit | mattpocock/skills | 453.4K |
| 66 | to-questionnaire | mattpocock/skills | 450.2K |
| 67 | azure-upgrade | microsoft/azure-skills | 450.1K |
| 68 | remotion-to-hyperframes | heygen-com/hyperframes | 448.3K |
| 69 | writing-beats | mattpocock/skills | 447.0K |
| 70 | writing-shape | mattpocock/skills | 446.5K |
| 71 | motion-graphics | heygen-com/hyperframes | 446.1K |
| 72 | writing-fragments | mattpocock/skills | 446.0K |
| 73 | scaffold-exercises | mattpocock/skills | 445.0K |
| 74 | supabase-postgres-best-practices | supabase/agent-skills | 443.8K |
| 75 | migrate-to-shoehorn | mattpocock/skills | 441.1K |
| 76 | ai-avatar-video | qu-skills/superpowers | 440.1K |
| 77 | high-end-visual-design | leonxlnx/taste-skill | 438.3K |
| 78 | redesign-existing-projects | leonxlnx/taste-skill | 437.2K |
| 79 | video-edit | prime-skills/runcomfy-agent-skills | 434.1K |
| 80 | image-to-video | prime-skills/runcomfy-agent-skills | 432.3K |
| 81 | nano-banana-2 | prime-skills/runcomfy-agent-skills | 432.0K |
| 82 | lark-approval | larksuite/cli | 431.9K |
| 83 | image-edit | prime-skills/runcomfy-agent-skills | 431.6K |
| 84 | azure-enterprise-infra-planner | microsoft/azure-skills | 427.4K |
| 85 | azure-kubernetes | microsoft/azure-skills | 420.9K |
| 86 | writing-for-agents | mattpocock/skills | 414.2K |
| 87 | lark-slides | larksuite/cli | 412.5K |
| 88 | lark-attendance | larksuite/cli | 409.6K |
| 89 | kling-3-0 | prime-skills/runcomfy-agent-skills | 407.5K |
| 90 | skill-creator | anthropics/skills | 405.1K |
| 91 | minimalist-ui | leonxlnx/taste-skill | 405.1K |
| 92 | loop-me | mattpocock/skills | 403.9K |
| 93 | caveman-commit | juliusbrussee/caveman | 402.2K |
| 94 | embedded-captions | heygen-com/hyperframes | 399.6K |
| 95 | wait-what | mattpocock/skills | 399.5K |
| 96 | caveman-review | juliusbrussee/caveman | 398.2K |
| 97 | caveman-compress | juliusbrussee/caveman | 397.0K |
| 98 | azure-rbac | microsoft/azure-skills | 396.7K |
| 99 | codex-pet | prime-skills/runcomfy-agent-skills | 395.9K |
| 100 | lark-okr | larksuite/cli | 395.8K |
| 101 | ui-ux-pro-max | nextlevelbuilder/ui-ux-pro-max-skill | 395.4K |
| 102 | pr-to-video | heygen-com/hyperframes | 394.9K |
| 103 | vercel-composition-patterns | vercel-labs/agent-skills | 392.2K |
| 104 | brainstorming | obra/superpowers | 391.2K |
| 105 | caveman-help | juliusbrussee/caveman | 389.4K |
| 106 | full-output-enforcement | leonxlnx/taste-skill | 385.6K |
| 107 | claude-handoff | mattpocock/skills | 384.0K |
| 108 | gpt-taste | leonxlnx/taste-skill | 380.6K |
| 109 | industrial-brutalist-ui | leonxlnx/taste-skill | 378.7K |
| 110 | ai-video-generation | prime-skills/runcomfy-agent-skills | 377.3K |
| 111 | ai-image-generation | prime-skills/runcomfy-agent-skills | 377.3K |
| 112 | lark-markdown | larksuite/cli | 377.1K |
| 113 | stitch-design-taste | leonxlnx/taste-skill | 376.8K |
| 114 | runcomfy-cli | prime-skills/runcomfy-agent-skills | 374.5K |
| 115 | brandkit | leonxlnx/taste-skill | 371.4K |
| 116 | video-extend | prime-skills/runcomfy-agent-skills | 371.3K |
| 117 | music-to-video | heygen-com/hyperframes | 367.0K |
| 118 | image-to-code | leonxlnx/taste-skill | 367.0K |
| 119 | ai-music | prime-skills/runcomfy-agent-skills | 363.3K |
| 120 | ace-step | prime-skills/runcomfy-agent-skills | 362.8K |
| 121 | azure-cost | microsoft/azure-skills | 362.6K |
| 122 | imagegen-frontend-web | leonxlnx/taste-skill | 361.9K |
| 123 | prisma-client-api | prisma/skills | 360.9K |
| 124 | prisma-database-setup | prisma/skills | 360.1K |
| 125 | prisma-cli | prisma/skills | 358.3K |
| 126 | talking-head-recut | heygen-com/hyperframes | 357.3K |
| 127 | imagegen-frontend-mobile | leonxlnx/taste-skill | 355.8K |
| 128 | azure-hosted-copilot-sdk | microsoft/azure-skills | 355.3K |
| 129 | prisma-postgres | prisma/skills | 352.5K |
| 130 | to-prd | mattpocock/skills | 351.6K |
| 131 | emil-design-eng | emilkowalski/skills | 350.9K |
| 132 | slideshow | heygen-com/hyperframes | 347.4K |
| 133 | prisma-driver-adapter-implementation | prisma/skills | 347.3K |
| 134 | prisma-upgrade-v7 | prisma/skills | 347.0K |
| 135 | airunway-aks-setup | microsoft/azure-skills | 346.9K |
| 136 | prisma-postgres-setup | prisma/skills | 346.9K |
| 137 | lark-vc-agent | larksuite/cli | 346.9K |
| 138 | cavecrew | juliusbrussee/caveman | 345.7K |
| 139 | caveman-stats | juliusbrussee/caveman | 344.6K |
| 140 | prisma-compute | prisma/skills | 342.2K |
| 141 | prisma-mongodb-upgrade | prisma/skills | 340.8K |
| 142 | to-issues | mattpocock/skills | 339.1K |
| 143 | setup-ts-deep-modules | mattpocock/skills | 333.0K |
| 144 | impeccable | pbakaus/impeccable | 331.6K |
| 145 | supabase | supabase/agent-skills | 324.5K |
| 146 | entra-agent-id | microsoft/azure-skills | 323.2K |
| 147 | hyperframes-studio | heygen-com/hyperframes | 319.7K |
| 148 | ai-research-explore | lllllllama/rigorpilot-skills | 317.4K |
| 149 | design-taste-frontend-v1 | leonxlnx/taste-skill | 312.2K |
| 150 | lark-apps | larksuite/cli | 307.4K |
| 151 | writing-great-skills | mattpocock/skills | 306.5K |
| 152 | orca-cli | stablyai/orca | 297.0K |
| 153 | ai-video-generation | skills-shell/superpowers | 295.3K |
| 154 | systematic-debugging | obra/superpowers | 291.8K |
| 155 | orchestration | stablyai/orca | 289.3K |
| 156 | ai-image-generation | its-a-skill-issue/superpowers | 288.9K |
| 157 | azure-reliability | microsoft/azure-skills | 286.4K |
| 158 | figma | heygen-com/hyperframes | 276.3K |
| 159 | ai-image-generation | bankai-skills/superpowers | 273.8K |
| 160 | writing-plans | obra/superpowers | 272.5K |
| 161 | shadcn | shadcn/ui | 271.1K |
| 162 | using-superpowers | obra/superpowers | 262.4K |
| 163 | requesting-code-review | obra/superpowers | 251.3K |
| 164 | test-driven-development | obra/superpowers | 249.1K |
| 165 | just-scrape | scrapegraphai/just-scrape | 245.0K |
| 166 | neon-postgres | neondatabase/agent-skills | 243.2K |
| 167 | vercel-react-native-skills | vercel-labs/agent-skills | 240.2K |
| 168 | verification-before-completion | obra/superpowers | 238.3K |
| 169 | pptx | anthropics/skills | 235.5K |
| 170 | implement-spec | mattpocock/skills | 235.0K |
| 171 | lark-note | larksuite/cli | 233.9K |
| 172 | executing-plans | obra/superpowers | 233.4K |
| 173 | diagnose | mattpocock/skills | 227.6K |
| 174 | seo-audit | coreyhaines31/marketingskills | 227.4K |
| 175 | subagent-driven-development | obra/superpowers | 227.1K |
| 176 | retro | mattpocock/skills | 225.1K |

---

*报告生成：2026-10-14 ｜ 数据核验：skills.sh 三榜单原始 HTML 解析（176 条）+ 6 仓库 README + 19 个官方 SKILL.md + 8 个详情页安全审计 ｜ 本机环境：Windows 11*
