# GitHub AI 趋势日报 · 2026-10-01

> 数据源：github.com/trending 三榜合并（daily 17 条 + weekly 18 条 + monthly 23 条），按本期新增 Star 降序。
> 说明：**GitHub trending 的排列顺序不等于 Star 增幅排序**，本报告只报增幅、不报名次。
> 去重口径：前八期（09-17 ~ 09-30）已展开过的仓库不再重复；已有仓库仅在其出现**新版本或重大新事件**时以新事件形式推送。

---

## 一、榜单速览

### 本期 10 条详细条目

| # | 仓库 | 语言 | 总 Star | 增幅 | 来源 | 一句话 |
|---|---|---|---|---|---|---|
| 1 | [mattpocock/skills](https://github.com/mattpocock/skills) | Shell | 273,203 | 日 +876 | daily | Matt Pocock 的工程技能集，公开反对"框架替你拥有流程" |
| 2 | [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) | C | 72,667 | 日 +118 | daily | 预建代码知识图谱，一次调用替代 grep 爬文件；**公开了对自己不利的上下文占用数据** |
| 3 | [openclaw/openclaw](https://github.com/openclaw/openclaw) | TypeScript | 391,061 | 日 +136 | daily | v2026.9.7：2,818 PR、344 贡献者；接入 OpenAI Agents API，**同时删掉 Tasks/TaskFlow 整套子系统** |
| 4 | [jingyaogong/minimind](https://github.com/jingyaogong/minimind) | Python | 62,994 | 月 +7,328 | monthly | 3 元 / 2 小时从零训练 64M LLM，全链路 PyTorch 原生实现 |
| 5 | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | Python | 27,079 | 周 +711 | weekly | 388 技能 / 118 Agent / 13 平台，一套 SKILL.md 多端分发 |
| 6 | [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) | TypeScript | 9,294 | 周 +329 | weekly | v1.0.238：CI 里的 Claude **迁到出网防火墙 runner + auto 权限模式** |
| 7 | [longbridge/gpui-kit](https://github.com/longbridge/gpui-kit) | Rust | 15,374 | 月 +1,600 | monthly | Rust 桌面应用框架，75+ 组件 + **JS 扩展运行时**（能力逐个授权） |
| 8 | [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | Python | 76,215 | 日 +123 | daily | 1000+ 技能清单；**用 MCP 网关补上"技能只说怎么做、不能做事"的缺口** |
| 9 | [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | Python | 127,690 | 日 +431 | daily | 中文 AI 短视频流水线，四种入口（Agent/WebUI/API/CLI）+ 一键跨平台发布 |
| 10 | [anthropics/claude-code](https://github.com/anthropics/claude-code) | TypeScript | 148,757 | 月 +5,807 | monthly | **v2.1.286**：凭证脱敏大规模修补 + 权限提示栈计数 + `--bare` 语义重定义 |

### 其他值得记一笔

| 仓库 | 语言 | 总 Star | 增幅 | 来源 | 说明 |
|---|---|---|---|---|---|
| [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | TypeScript | 90,863 | 日 +50 | daily | 官方参考 MCP 服务器集中修并发与校验：记忆图谱加互斥锁、批量去重、查询串限长 2048、加载时按 Schema 校验 |
| [mvschwarz/openrig](https://github.com/mvschwarz/openrig) | TypeScript | 3,191 | 日 +624 | daily | **v0.6.3**（09-30）修复托管 Claude 消息链路 |
| [paperclipai/paperclip](https://github.com/paperclipai/paperclip) | TypeScript | 95,461 | 月 +15,694 | monthly | canary v2026.1001.0-canary.1：**停止重放语义不明的数据库断连** |
| [stablyai/orca](https://github.com/stablyai/orca) | TypeScript | 82,572 | 周 +5,987 | weekly | v1.4.218（09-30） |
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | TypeScript | 54,882 | 日 +349 | daily | v0.8.102（10-01），当天仍在连发 |
| [NVIDIA/OpenShell](https://github.com/NVIDIA/OpenShell) | Rust | 13,177 | 日 +1,281 | daily | v0.1.3-pre.1（09-30） |
| [t8y2/dbx](https://github.com/t8y2/dbx) | Rust | 23,408 | 日 +1,138 | daily | DBX v0.6.29（09-30） |
| [longbridge/gpui-kit](https://github.com/longbridge/gpui-kit) | Rust | 15,374 | 月 +1,600 | monthly | 见第 7 条 |
| [byoungd/up](https://github.com/byoungd/up) | JavaScript | 66,503 | 日 +743 | daily | 中文非技术"人生进阶指南"，连续多期在榜（榜单结构信号） |

**已推送仓库状态检查（本期无新版本，不展开）**：Tencent/WeKnora 仍 v0.8.2（09-24）、vectorize-io/hindsight v0.10.2（09-29）、dream-num/univer v1.0.3（09-29）、debpalash/VoiceStudio 仍 v0.5.6（09-23）、VectifyAI/PageIndex v0.2.20（09-28）、NVIDIA/SkillSpector v2.12.0（09-23）、DietrichGebert/ponytail v4.10.0（09-14）。

---

## 二、10 条详细

### 1. mattpocock/skills — 273k Star 的个人技能集，公开反对"框架替你拥有流程"

**事件**
Matt Pocock（Total TypeScript 作者）把日常自用的 agent skills 开源为独立仓库，一天涨 876 星，总星数已达 273,203、fork 22,967。README 里直接点名竞品：

> "Approaches like GSD, BMAD, and Spec-Kit try to help by owning the process. But while doing so, they take away your control and make bugs in the process hard to resolve."
> （GSD / BMAD / Spec-Kit 这类方法想帮你，方式是**接管你的流程**；代价是你失去控制权，且流程本身的 bug 极难排查。）

**核心内容**
- **两条安装路线，两种哲学**：Claude Code 插件（`claude plugins install mattpocock-skills`）装成只读托管包、随作者更新自动升级 → "你订阅而非 fork"；`npx skills@latest add mattpocock/skills` 则把可编辑的技能文件拷进你的仓库 → 你可以改。README 明确警告：**两条都装会得到每个技能的两份**。
- **技能分两类，按"谁能调用"切分**：user-invoked（只有你敲 `/xxx` 才触发，职责是编排，如 `/grill-me`、`/to-spec`、`/triage`、`/wayfinder`）与 model-invoked（你或 agent 都可触发，承载可复用纪律，如 `/tdd`、`/diagnosing-bugs`、`/code-review`、`/codebase-design`）。规则是：**user-invoked 可以调 model-invoked，但绝不能调另一个 user-invoked**——避免编排层互相递归。
- **四个失败模式对应四类修法**：①"agent 做的不是我想要的" → `/grill-me`、`/grill-with-docs`（先拷问再动手）；②"agent 太啰嗦" → 共享语言（`GLOSSARY.md`，把"There's a problem when a lesson inside a section of a course is made 'real'"压成"There's a problem with the materialization cascade"）；③"代码不跑" → 反馈回路（`/tdd`、`/diagnosing-bugs`）；④"盖成泥球" → `/improve-codebase-architecture` 定期扫描深化机会，出 HTML 报告再逐个拷问。
- **工程细节**：`/code-review` 拆成两轴并行子代理——Standards（是否守本仓规范 + Fowler 坏味道基线）与 Spec（是否忠实实现原始 issue），两条互不污染；`/pr` 规定 PR 正文必须是"能让变更被看懂的最小可视化 + 前后证据 + 单向门/双向门判定与爆炸半径"；`/wizard` 生成交互式 bash 向导，把"只有人能做"的步骤（开凭证、配 CI secret、走陌生第三方后台）脚本化。

**值得关注的原因**
这是本期最强的**反框架信号**。2026 年 Q3 的主流叙事是"把不可协商约束写进流程与文件"（09-24 的 superpowers / OpenSpec / impeccable，09-29 的 ponytail），解法普遍是**加重框架**。mattpocock/skills 走的是相反方向：**技能要小、要可组合、要能被你改坏再修好**，并给出可执行的分层纪律（user-invoked 不互调）来保证"小"不会退化成"乱"。更值得注意的是它用 273k Star 证明这条路线有巨大受众——**开发者对"框架接管流程"的容忍度，可能比工具厂商以为的低得多**。

---

### 2. colbymchenry/codegraph — 代码知识图谱，以及一份"对自己不利"的基准

**事件**
`codegraph` 进入日榜（+118，总 72,667）。它做的事和 09-24 的 DeusData/codebase-memory-mcp 同类（预建代码图谱替代 grep 爬文件），但**首次公开了一份包含负面结论的完整基准**，这在同品类里很少见。

**核心内容**
- **机制**：解析出每个符号、调用边、依赖的预建知识图谱，agent 一次 `codegraph_explore` 拿到相关源码 + 调用路径（**含 grep 跟不了的动态派发跳转**）+ 变更爆炸半径。解析内核是**原生 Rust**，20 种语言，且每种语言上线前要求"图谱与参考引擎逐字节一致"。
- **性能自适配**：worker 池按真实核数（cgroup 感知，2 核 VPS 就按 2 核算，不按宿主 64 核）+ 实测可用内存 + 本项目解析成本来定尺寸。工作站跑全并行流水线（Swift 编译器仓库 27k 文件约 100 秒首建，单文件改动重同步约 4 秒）；2 核 / 6GB VPS 走"保证跑完"的流水线——**Linux 内核（70k 文件、2M 符号、6.4M 关系）12 分钟内索引完成，而内存优先的设计在跑到 1% 前就 OOM**。
- **正面基准**（7 个真实开源库、7 种语言、Claude Opus 4.8、每臂 4 次取中位数）：88% 更少工具调用 · 53% 更快 · 62% 更少 token · 44% 更便宜 · **7 个库的文件读取全部降到 0**。Excalidraw 上 2 次调用 vs 43 次、3.6 倍速。
- **关键的方法论细节**：基准 harness **在两个臂里都屏蔽了 `codegraph` CLI**。原因写得很直白——不屏蔽时对照臂的 agent 在 **28 次运行中有 26 次**从 PATH 上找到 CLI 并通过 Bash 走了 CodeGraph，而 CLI 调用不计入工具调用、其输出仍进上下文，**双向污染对比**。屏蔽后 28 次对照运行全部被拦，污染 0 次。
- **反直觉的负面数据**：CodeGraph 只降低**吞吐成本**（处理掉的 token、花的钱），**不降低上下文残留**。同一批 7 个库的多轮会话里，CodeGraph 结束时窗口里留存的检索上下文比读文件方案**多约 80%**——VS Code 上 67k token vs 18k。机制和它的优点同源：它返回**一个稠密的原文载荷**，答完还留在窗口里；而 grep-and-read 方案产生大量小结果，会被淘汰掉。"更少的 token 处理量"和"更大的常驻足迹"同时为真。小窗口跑长会话需要为此留预算。

**值得关注的原因**
三点值得单独记：
1. **这是本期唯一一份主动削弱自己结论的基准**。屏蔽对照臂 CLI、公开"残余上下文 +80%"、并指出成本更多取决于"问题需要多少发现工作"而非仓库大小（需要 28–43 次工具调用的问题省 57–78%，7 次就能答完的问题基本持平）——这种披露水平在 trending 项目里罕见。
2. **它把"上下文经济"的账算得更细了**。前几期的共识是"少花 token"（09-24 的 99.2% 节省、45M→12KB）；codegraph 说明"处理量"和"驻留量"是两个独立指标，可以一升一降。这对选型是硬约束：**短问答、小窗口 → 图谱赢；长会话、小窗口 → 要重新算**。
3. **"2 核 VPS 也能索引 Linux 内核"是个工程判断**。它把资源自适配当成一等需求（cgroup 感知、诚实内存、按项目实测），说明本地优先工具的部署目标已经从开发者笔记本扩散到廉价云主机。

---

### 3. openclaw/openclaw v2026.9.7 — 2,818 个 PR 的大版本，一边加能力一边删子系统

**事件**
OpenClaw 发 v2026.9.7（09-30），规模：**518 个直接提交、2,818 个 PR、344 位贡献者**。仓库总星 391,061（日 +136），是全榜体量最大的项目，此前八期均未展开。

**核心内容**
- **新增**：接入 **OpenAI Agents API**（可选运行时，聊天跑在持久化托管的 Linux 工作区里，带 web search、OpenClaw 工具、文件传输；自托管执行需自己的 controller 与匹配的 workspace 路径，且不支持文件传输）+ **Sign in with ChatGPT (Beta)**；模型与视频生成选项扩展。
- **删除**：**Tasks 与 TaskFlow 的 panel / 命令 / API 整体退役**。官方给出的替代路径是 subagent controls、ACP sessions、后台进程、Cron 历史或 Lobster pipelines；插件作者必须从被移除的 Task 接口迁移，subagent 的 wait/cancel 改用 `runId` / `runIds`；**TaskFlow Webhooks 没有等价的 HTTP 替代**。
- **Tool Search 迁移**：拆成独立的 search / description / call 三个工具，旧的 JavaScript 工具 `tool_search_code` 移除（JS 编排改用 Code Mode）。手工升级或延迟修复后**必须先跑 `openclaw doctor --fix` 再重启，否则旧设置会直接阻止启动**。
- **权限与安全面**：共享网络的默认未认证连接配额从每 IP 32 提升到 128 个挂起连接（README 级文档里明确写了"这允许更多 socket 消耗服务器资源，管理员可以调低"）；工具详情与诊断**显示文件系统路径但保留凭证脱敏**；已安装插件页展示账号与凭证设置（Connect / Configure / Edit），并明确 "Connected / Configured 只表示已保存设置，不代表服务可用或密钥有效"。
- **协作语义**：同权限参与者可以 steer 共享轮次（跨设备用同一 Owner token），但 steering 不打断正在运行的工具，Incognito 与云 worker 轮次不支持。

**值得关注的原因**
**"删掉一个完整子系统"比"加功能"更能说明项目成熟度**。Tasks/TaskFlow 被 subagent controls + ACP + 后台进程 + Cron 四套机制取代，说明 OpenClaw 认定"任务编排"不该是独立产品面，而应该是**既有原语的组合**——这和第 1 条 mattpocock 的"user-invoked 不该互调"是同一判断的两个尺度（一个是技能层，一个是产品层）。同时它把破坏性迁移写得很硬：`doctor --fix` 不跑就起不来、Webhooks 无 HTTP 替代、旧插件需手工迁移。接入 OpenAI Agents API 则说明头部 Agent 客户端开始把"跑在谁的托管工作区里"做成可选项，而非立场。

---

### 4. jingyaogong/minimind — 3 元、2 小时，从零训一个 64M 的 LLM

**事件**
minimind 进月榜（月 +7,328，总 62,994）。项目目标是**完全从 0 开始**，用约 3 元成本和 2 小时训练时间，训出约 64M 参数的超小语言模型。体积约为 GPT-3 的 1/2700。

**核心内容**
- **"3 元 / 2 小时"的口径写得很清楚**：2 小时 = SFT 阶段在单张 NVIDIA 3090 上跑完 1 epoch 的实测耗时；3 元 = 对应时段的 GPU 租用成本。
- **不依赖高层抽象**：所有核心算法代码从 0 用 PyTorch 原生实现，**不用 `transformers` / `trl` / `peft` 提供的高层接口**。作者的理由直指痛点——这些库十几行代码就能跑完"加载模型 + 加载数据 + 推理 + 强化学习"，便利的同时把开发者与底层实现隔离开，"用乐高自己拼出一架飞机，远比坐在头等舱里飞行更让人兴奋"。
- **覆盖全链路**：极简模型结构、MoE、数据清洗、预训练、SFT、LoRA、RLHF（DPO）、RLAIF（PPO / GRPO / CISPO）、Tool Use、**Agentic RL**、自适应思考、模型蒸馏。四种推理入口（Transformers / PyTorch 原生 / ollama / vllm）+ 可选 Streamlit WebUI。
- **模态扩展线**：MiniMind-V（视觉）、MiniMind-O（Omni 多模态）、MiniMind-dLM（扩散语言模型）、MiniMind-Linear（线性模型）。
- **近期提交全部是训练正确性修复**：LoRA 推理路径与训练输出对齐、残差累积步之后才保存最终 checkpoint、残差梯度在保存前更新、清理冗余注释。都是"教程代码必须真的对"这类问题。
- 定位明确：**不只是全阶段开源复现，也是一套面向 LLM 入门与实践的教程**。Apache 2.0。

**值得关注的原因**
前几期登榜的教学类项目（09-29 的 cs341-illinois/coursebook、rohitg00/ai-engineering-from-scratch）解决的是"教材怎么防腐"，minimind 解决的是**"门槛能不能降到个人付得起"**。3 元 / 2 小时这个量级意味着：**理解 LLM 内部机制不再需要任何机构资源**，一张 3090 的单次租用就够。而"不用 transformers/trl/peft"是明确的教学立场——用高层抽象学不到东西。配上"提交全在修训练正确性"，说明这个项目的价值不在 Star 数，而在于它是**很多人第一次真正跑通完整训练链路的那个仓库**。月榜 +7,328 说明这类"从零复现"需求持续旺盛，与 Agent 工具链的火热是两条独立曲线。

---

### 5. alirezarezvani/claude-skills — 388 技能、13 平台，SKILL.md 成了通用分发格式

**事件**
进周榜（周 +711，总 27,079）。号称最全的开源 Claude Code 技能 / 插件库：**388 个技能、118 个 Agent、150 个命令、7 个人格**，一套内容适配 **13 种 AI 编码工具**。

**核心内容**
- **一套 SKILL.md 多端分发**：原生支持 Claude Code 插件、Codex agent skills、Gemini CLI skills、Hermes Agent skills、Mistral Vibe skills，其余通过 `scripts/convert.sh` 转换。**明确写着"用同一个 agentskills.io SKILL.md 标准，无需格式转换"**。
- **技能 / Agent / 人格三层区分**（这个切分值得记）：Skills = *how to execute a task*（单领域、语气中立）；Agents = *what task to do*（单领域、专业语气）；Personas = *who is thinking*（跨领域、带人格）。三者可组合。
- **体量与依赖纪律**：706 个 Python CLI 脚本，**全部只用标准库、零 pip 安装**；823 个模板 / 检查清单 / 领域知识文件。领域覆盖工程、DevOps、营销（含 AEO——面向 LLM 引用的"答案引擎优化"）、安全（PreToolUse hooks）、合规、C-level 顾问（CFO/CMO/CRO/CPO/COO/CHRO/CISO/GC/CDO/CAIO/CCO/VPE 人格 + 21 个 `/cs:*` 命令）、生产力、学术研究栈（litreview / grants / dossier / patent / syllabus / notebooklm / deep-research + 混合路由）、企业研究运营。
- **Windows 用户的坑被单独文档化**：必须 `git clone -c core.symlinks=true`（开开发者模式），否则 `.gemini/` / `.codex/` / `.vibe/` / `.hermes/` 镜像树会检出成 1 行指针文本而不是技能；并需设 `PYTHONUTF8=1`，否则打印 Unicode 的工具在旧代码页控制台会崩。
- 最新发布 v2.12.0（08-25）；v2.9.0 引入企业研究运营模块。

**值得关注的原因**
第 1 条（mattpocock/skills）代表"少而精、可改"，这一条代表**"多而全、可移植"**，两条同日同榜，构成技能生态的两极。更重要的信号是：**SKILL.md 已经事实上成为跨厂商的技能分发格式**——13 个平台共用一份源、零格式转换、零第三方依赖。这和 09-17 首期的判断（"SKILL.md 成为事实上的技能分发格式"）在两周后得到规模化验证。同时它把"零 pip 安装、纯标准库"当成硬约束，与 09-24 HKUDS/CLI-Anything 的"零妥协依赖"是同一条纪律：**技能要能在任何装了 Python 的地方直接跑，否则就失去了跨平台的意义**。

---

### 6. anthropics/claude-code-action v1.0.238 — 无人值守的 CI Agent 被套上出网防火墙

**事件**
v1.0.238（09-30）进周榜（周 +329，总 9,294）。这个仓库的价值不在功能，而在于**它是"Agent 在 CI 里无人可问"这个场景的官方安全样本**。

**核心内容**
- **把所有调用 Claude 的 workflow job 从 `ubuntu-latest` 迁到 GitHub 的出网防火墙 runner（`ubuntu-24.04-firewall`）**，并给每个 job 传 `--permission-mode auto`（`claude.yml` 除外）。
- **为什么必须换 auto 模式**：文档写得很直接——这些运行**没有人可以询问**，此前遇到需要权限而 allowed tools 未覆盖的工具调用时，会**一律拒绝**。auto 模式下 Claude Code 会自行复核每个此类调用，通过安全检查才执行。issue 分诊步骤还额外传 `--disallowedTools` 排除它根本不需要的工具。
- **网络允许列表落成文件**：`.github/egress-firewall.yaml` 以 enforce 模式列出 job 可访问的 host 及各自用途。
- **把安全约束做成 CI 检查**：新增 `workflow-hardening.yml` + `check_workflow_hardening.py`，当①有 job 调用 Claude 却不在防火墙 runner 上、②没传 `--permission-mode auto`、③允许列表缺失/为空/非 enforce 模式/含 `*` 通配 host、④settings 文件（含 `--settings` 指定的仓内文件）设置了权限模式、⑤job 定义里出现 `defaultMode`、⑥settings 指向仓库外文件——任一命中就**失败**。`claude.yml` 的豁免必须写明理由。
- **模型版本与 auto 模式的耦合**：检查还会在 auto 模式步骤指定了早于 `claude-opus-4-6` 的模型时失败，因为 Claude Code **在这些旧模型上不跑 auto 模式，会回退到默认权限模式**。issue 分诊步骤显式 pin `--model claude-opus-5`（原因：2.1.280 后默认模型变了，而这个 CI 账号无权访问新默认模型）。
- **把纪律写进 CLAUDE.md**：新增 "Security hardening for GitHub Actions" 章节，让新写和改动的 workflow 自动继承这些保护。

**值得关注的原因**
这是"**Agent 不该持有凭证**"（09-23 treg / Agent-Reach）与"**Agent 安全从建议变产品矩阵**"（09-30 NVIDIA OpenShell + SkillSpector）两条线的落地补完：**当一个 Agent 无人可问时，权限模型的默认值必须翻转**——从"拒绝一切"改成"自我复核后放行"，同时用出网防火墙把爆炸半径框住。更值得记的是工程手法：**安全约束不是写在文档里，而是写成会失败的 CI 检查**（含通配 host、含豁免必须写理由、含模型版本与权限模式的隐式耦合）。这和第 1 条 mattpocock 的"把不可协商约束写进流程与文件"是同一方法论，只是尺度落在 CI 上。

---

### 7. longbridge/gpui-kit — Rust 桌面框架，把"能力逐个授权"做进插件层

**事件**
进月榜（月 +1,600，总 15,374）。Longbridge 把支撑自家商业桌面端 Longbridge Pro 的框架抽出来开源：GPUI Kit。

**核心内容**
- **三层结构，一个依赖**：应用只依赖 `gpui-kit` 一个 crate，它 pin 住匹配的 GPUI 版本并 re-export GPUI、base、component、assets。
  - `gpui-component`：完整带样式的组件系统（75+ 组件与基础件，覆盖表单、导航、浮层、数据展示、编辑、反馈、布局）
  - `gpui-base`：无样式的行为、状态与基础设施（你自己拥有设计系统时用）
  - `gpui-shell`：**Rust 宿主承载的 JavaScript 运行时**，让已发布的 Rust 应用以脚本形式加载面板与业务逻辑
- **分层原则一句话**：**行为属于基础层，表现属于应用层**（Behavior belongs to the foundation. Presentation belongs to the application.）。README 用 shadcn 生态做类比：GPUI ↔ HTML+Tailwind，`gpui-base` ↔ Base UI，`gpui-component` ↔ shadcn 的带样式组件层。
- **JS 扩展的安全模型**：`gpui-shell` 让插件"**每一项能力都必须被显式授予**"（with every capability granted explicitly）——不授予就不可用。
- **实测能力边界**：代码编辑器在 **200K 行**下稳定（Tree-sitter 高亮 + LSP 诊断/补全/悬停）；数据表虚拟滚动 + 固定/可调列 + 排序 + 单元格选择，跨**数十万行**；GPU 加速 **120 FPS**；Dock 布局（可调面板、可拖 tab、嵌套分屏、边缘停靠）**全部可序列化**；`wasm32-unknown-unknown` 跑 Web；AccessKit 无障碍角色/名称/状态/关系/动作进交互层且有测试覆盖；**UI 集成测试**能在无头窗口里渲染真实组件、驱动指针与键盘输入、断言状态/焦点/布局/无障碍。
- 官方提供"可执行应用配方 + AI 辅助开发验收检查"（`examples/ai_recipes/`），即**给 Agent 的起步模板与验证命令**。

**值得关注的原因**
本期唯一的**桌面应用框架**，也是少数几个把"Agent 可验证性"当成框架交付物的项目——`examples/ai_recipes/` 里放的是**验收检查命令**，等于承认"Agent 写 Rust UI"需要一个可跑通的验证回路。更值得注意的是 JS 扩展模型：**能力逐个显式授予**，和 09-18 期 Tencent/BrowserSkill"权限权威源放在扩展侧"、09-30 OpenShell"沙箱内看不到真凭证"是同一条设计纪律的第三次出现——**扩展性必须和能力授权一起设计，不能事后打补丁**。Rust + GPUI 这条线（09-30 还登过 longbridge/gpui-kit 的速览位）说明桌面端在 Agent 时代重新被认真对待：**本地优先不只是"数据不出门"，也包括"界面不依赖浏览器"**。

---

### 8. ComposioHQ/awesome-claude-skills — 1000+ 技能清单，以及"技能不会做事"的补丁

**事件**
进日榜（日 +123，总 76,215）。Composio 维护的 Claude Skills / Plugins 精选清单，1000+ 条，覆盖 Claude.ai、Claude Code 以及 Codex、Cursor、Gemini CLI、Antigravity 等编码 agent。

**核心内容**
- **它把技能生态的缺口讲得最清楚**：
  > "Skills tell your agent **how** to work. An MCP Gateway gives it secure access to the tools it needs."
  > （技能告诉 agent **怎么做**；MCP 网关给它安全访问所需**工具**的权限。）
- **对应解法是 `connect-apps` 插件**：`claude --plugin-dir ./connect-apps-plugin` 安装，跑 `/connect-apps:setup` 贴 API key，然后 Claude 就能发邮件、建 issue、发 Slack。底层是 Composio 的 **MCP Gateway**——单一 MCP 端点接 1,000+ 集成，自带认证、**基于团队的访问控制、审计日志**、生产级可靠性。
- 近期提交以社区技能收录为主：`overkill`、`building-blog` 等逐个 PR 合入。
- Apache-2.0；README 顶部就是 Composio 的商业入口（这是它的商业模式，但技能清单本身开源可用）。

**值得关注的原因**
**它精确指出了一个结构性事实：SKILL.md 是纯文本指令，本身没有执行能力。** 前八期反复出现"技能 + 命令 + 连接器三元组"（09-18 anthropics/knowledge-work-plugins）、"技能注册表"（09-28 tech-leads-club/agent-skills，引 Snyk 报告"13.4% 市场技能含严重漏洞"），但很少把**"技能 × 工具访问"的分工**说得这么干净。Composio 的答案是：技能管方法论，网关管认证与审计，两者解耦。这也解释了为什么 1000+ 条清单有存在价值——**当技能变成廉价商品，稀缺的是"能安全调到 1000 个 SaaS 的凭证层"**。同时它提醒了一个风险面：技能清单越开放，供应链安全的量化基线（09-30 SkillSpector 的 26.1% 含漏洞 / 5.2% 疑似恶意）就越重要。

---

### 9. harry0703/MoneyPrinterTurbo — 中文 AI 短视频流水线，四种入口

**事件**
进日榜（日 +431，总 127,690，fork 19,971）。老牌中文项目（2024-03 创建），本期重新上榜。核心：给一个主题或关键词，自动生成视频脚本、匹配素材、生成字幕与背景音乐，合成高清短视频。

**核心内容**
- **四种入口**：**AI Agent、WebUI、API、CLI**——既能快速上手，也能接自动化流程。支持批量生成多条成片、任务历史、生成设置与 API Key 的导入/导出/恢复。
- **模型服务覆盖面极广**：脚本侧支持 Kimi/Moonshot、OpenAI、Anthropic、Gemini、DeepSeek、通义千问、Azure OpenAI、火山方舟、xAI Grok、MiniMax、小米 MiMo；兼容层支持胜算云、APIMart、Cloudflare AI Gateway、ModelScope、AIHubMix、AIML API、EvoLink、OpenRouter、Ollama、OneAPI、LiteLLM、Groq、Pollinations 等统一网关与本地环境。
- **素材侧**：本地图片/视频上传 + Pexels / Pixabay / Coverr 免费库存；文生视频接秘塔 MiniMax H3（768P/2K、4–15 秒、9:16 / 16:9 / 1:1）、火山方舟 Seedance、WaveSpeed、OFox、MuAPI（异步，可配 Endpoint / 画幅 / 分辨率 / 轮询）、OpenAI 兼容文生图（可把生成图转成动态片段）。
- **配音**：自动配音 / 上传配音 / 无配音三选，含音色试听与完整预览；集成 **Edge TTS（免费、无需 API Key）**、Azure Speech、SiliconFlow、Gemini、小米 MiMo、MiniMax、ElevenLabs、Chatterbox、Kokoro、Fish Audio、ModelBest VoxCPM。
- **成片**：9:16（1080×1920）/ 16:9（1920×1080）/ 1:1（1080×1080），**一键跨平台发布到 TikTok、Instagram、YouTube Shorts**。
- **近期提交集中在可观测性**：合成阶段原来卡在 50% 不动、最终渲染完全不写日志 → 现在 `combine_videos` 接受 progress_callback 并按已覆盖时长上报（单视频 50%→75%）；每处理一个片段打一行日志；最终渲染每 30 秒心跳。素材下载同理——超过 15 秒的单个下载打带大小/百分比/速度的心跳（**只记缓存文件名，绝不记下载 URL**），任务从 40%→50%。代码注释直言："在慢连接下，那是几十分钟里，一个正在跑的任务看起来和一个卡死的任务完全一样。"

**值得关注的原因**
两条：
1. **"四种入口"是把 Agent 当一等公民**。同一套流水线既给你点按钮，也给 Agent 调——这是 09-30 期"非文本产出物被系统性 Agent 化"（hyperframes 视频 / mcp-for-blender 3D / univer Office）的延续，但 MoneyPrinterTurbo 走的是**中文内容生产 + 短视频变现**这条更接地气的路，127k Star 是需求强度的直接证据。
2. **提交内容暴露了这类长流水线工具的真实痛点**：不是功能不够，而是**"跑着还是死了分不清"**。把进度回调、心跳、分阶段百分比补齐，并顺手做对一件事——**日志只记缓存文件名不记下载 URL**——说明作者对"日志本身是泄露面"有意识。这与 09-30 期 dbx"密钥辅助代码只在 keyring 构建编译"、reclip"150 行 + 2 依赖"属同一类"工程克制"。

---

### 10. anthropics/claude-code v2.1.286 — 凭证脱敏大规模修补，权限提示栈计数

**事件**
v2.1.286（09-30）发布，月榜在榜（月 +5,807，总 148,757）。这是本期唯一一条"已推送仓库的重大新版本"，因为**改动集中在凭证泄露与权限可见性**，值得单独记。

**核心内容**
- **凭证脱敏是本期主线，一口气修了 7 类**：①MCP 错误消息在 `Bearer` / `Basic` 出现在 key 名之前时**显示了凭证值**；②百分号编码的 Bearer token 只被部分遮蔽；③日志与转录里 key 名内含**不可见字符**（如零宽空格）导致脱敏失效；④URL 密码含 `)`、引号、`]`、`&` 或第二个 `@` 时泄露一部分；⑤URL 密码跨过 `/` 进入方括号 host（如 `[::1]`）时泄露；⑥`/feedback` 存盘的 zip 里会话转录在脱敏后**包含非法 JSON 行**；⑦ssh URL 场景。
- **权限提示栈**：多个权限请求堆叠时，提示里加 "2 of 5" 这样的计数。
- **`--bare` 语义重定义**：只连接命令行上点名的 MCP server、不向模型发任何 system reminder、不启动后台任务；在 `--bare` 下，shell 命令到超时就是停止，**不再转入后台**。
- **重试策略收紧**：一个限额现在覆盖整个模型调用——按默认重试设置，一个失败的调用**最多发 14 次请求**。
- **插件供应链**：插件安装**拒绝 git 仓库或文件夹形式的 npm 源**，依赖只能从 registry 包安装。
- **MCP 相关修复**：connector 在 server 丢掉旧 MCP 握手后长达一天不列出工具；`/usage` 不把 server 尚在连接或刚连接时的工具调用计入该 server；重复的 MCP 登录请求替换待处理链接导致链接失效。
- **模型降级**：当 API 拒绝默认模型或别名解析出的模型时，现在会在同档位的上一个模型上**重试一次**；模型降级通知与 autocompact 抖动错误会说明**上下文窗口是否从 1M 掉到 200K**。
- **子代理**：worktree 隔离的子代理首次读文件时不再从 worktree 副本重复加载项目 CLAUDE.md 及其 imports；`/compact`、`/clear`、`/rewind` 在查看后台 agent 转录时被敲下，**现在会弹窗点名目标并先确认**，不再静默作用到主对话。
- **提交前验证**：当项目或用户技能里存在名为 `verify` 的技能时，Claude 会在提交前被要求运行它（文档类与测试类提交除外）。

**值得关注的原因**
**脱敏 bug 的形态本身值得记**：7 类里有 5 类是"脱敏逻辑在正常输入下工作，在边界输入下漏"——不可见字符、百分号编码、`Basic` 出现在 key 名前、URL 密码含标点、跨 `/` 到方括号 host。这说明**凭证脱敏是攻击面而非功能**，必须按畸形输入测试。同时 `--bare` 语义收紧 + 重试限额覆盖整个模型调用（最多 14 次请求）+ 插件只从 registry 装依赖，三条合起来是同一个方向：**把"Agent 运行时会自己做什么"的范围收窄并写清楚**。`/compact` 在后台转录视图里弹窗确认目标，则是把 09-28 期 orca"子代理输出归属 bug"暴露的同一类问题（**操作作用域必须显式**）在客户端侧补上。

---

## 三、当日主线判断

1. **技能生态正式分裂成两极，且同日同榜**：`mattpocock/skills`（少而精、可改、反框架接管流程，273k Star）对 `alirezarezvani/claude-skills`（388 技能、13 平台、多而全、零依赖可移植，27k Star）。两者共享同一个前提——**SKILL.md 是通用分发格式**——但在"该不该让框架拥有流程"上立场相反。这是 09-17 首期"SKILL.md 成为事实上的技能分发格式"判断的规模化落地。

2. **"删子系统"成为项目成熟度的信号**：OpenClaw 在 2,818 个 PR 的大版本里**整体退役 Tasks/TaskFlow**，改用 subagent controls + ACP + 后台进程 + Cron 的组合；同一天 mattpocock 规定"user-invoked 技能不得互相调用"。**产品层和技能层同时在做同一件事：拆掉独立编排层，改用既有原语的组合。**

3. **基准披露进入"自我削弱"阶段**：codegraph 在两个对照臂都屏蔽自家 CLI（否则 28 次里 26 次被对照臂偷偷调用）、公开"残余上下文 +80%"这一不利数据、并区分"处理成本"与"驻留成本"。这比 09-29 ponytail 主动把 80–94% 修正为"均值 54%"更进一步——**从"修正过高的数字"到"主动测出并公开自己的负面指标"**。

4. **上下文经济从"省 token"细化为"分两个账"**：处理量（token processed / 花多少钱）与驻留量（会话结束时窗口里还剩多少）可以**一降一升**。这给选型加了硬约束：短问答小窗口用图谱赢，长会话小窗口要重算。前几期"45M→12KB""99.2% 节省"的单指标叙事到此为止。

5. **"Agent 不该持有凭证"落到 CI 无人值守场景**：claude-code-action 把所有调用 Claude 的 job 迁到出网防火墙 runner，并把安全约束写成**会失败的 CI 检查**（含通配 host、含豁免必须写理由、含模型版本与 auto 权限模式的隐式耦合）。权限默认值在"无人可问"时必须翻转——从"拒绝一切"改成"自我复核后放行 + 出网白名单"。

6. **凭证脱敏被证明是攻击面**：claude-code v2.1.286 一口气修 7 类脱敏漏洞，其中 5 类是边界输入（不可见字符、百分号编码、关键字顺序、URL 标点、方括号 host）。**脱敏必须按畸形输入测试**，这是新的工程要求。

7. **本地优先扩散到"界面层"**：gpui-kit 用 Rust 交付桌面框架 + **能力逐个显式授权的 JS 扩展运行时**。"扩展性必须和能力授权一起设计"在同一季度内第三次出现（BrowserSkill 扩展侧权威源 → OpenShell 沙箱无真凭证 → gpui-shell 逐项授权）。

8. **教学与复现类项目是独立需求曲线**：minimind 月 +7,328（3 元 / 2 小时训 64M LLM、不用 transformers/trl/peft），与 Agent 工具链的火热互不相关。**降低门槛本身有巨大受众**，且项目近期提交全在修训练正确性——教程代码必须真的对。

9. **非文本产出物的 Agent 化进入中文内容生产**：MoneyPrinterTurbo 127k Star，"AI Agent / WebUI / API / CLI 四入口"，且近期提交集中在**可观测性**（进度回调、心跳、分段百分比）。这类长流水线的真实痛点是"跑着还是死了分不清"，而非功能缺失。

10. **非 Agent 项目占 4/10**（minimind、gpui-kit、MoneyPrinterTurbo、modelcontextprotocol/servers），与 09-28 / 09-29 / 09-30 持平。

---

*生成时间：2026-10-01 14:52 (GMT+8) · 数据源：github.com/trending 三榜合并 + 各仓库 README / CHANGELOG / release feed 核对*
