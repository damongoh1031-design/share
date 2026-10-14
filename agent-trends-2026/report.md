# 2026 年 AI Agent 的十个新趋势

> **调研问题**：在现在的 agent，有什么新趋势？
>
> **核验方式**：2026-10-14 检索并抓取中英文一手/近一手来源——Anthropic《2026 Agentic Coding Trends Report》引述、阿里云开发者 Harness Engineering 实战复盘（含完整方法论与实测数据）、路透社 NPCI 报道引述、虎嗅 KYA 深度分析、METR time horizon 系列、OWASP GenAI Top 10 2026 解读、以及本会话前九轮积累的一手核验数据（skills.sh 102 家官方厂商、MCP 规范演进、AAIF 成立等）。
>
> **配套文件**：`report.html`（可视化）、`data/trends.json`（十大趋势结构化数据 + 证据分级）、`data/evidence.json`（关键引语原文）

---

## 〇 一句话总览

**2026 年 Agent 领域最重要的事，不是「模型又能干更多了」，而是「工程界终于承认：模型能力不是瓶颈」。**

三个关键数字：

| 数字 | 含义 | 来源 |
|---|---|---|
| **60% vs 0-20%** | 开发者 **60%** 的时间已在用 AI 辅助，但能**完全委托**给 Agent 的任务只占 **0-20%** | Anthropic《2026 Agentic Coding Trends Report》 |
| **24.86% → 90.54%** | 同一个存量 Java 应用，加上 Harness 体系后 AI 代码采纳率 | 阿里云开发者实战复盘 |
| **7 个月** | Agent 能完成的任务时长**翻倍周期** | METR |

**「60% vs 0-20%」这个落差是整个 2026 年的核心矛盾**：模型的原始能力已经足够强，但从「能力」到「可信赖的工程产出」之间，横亘着一道系统性鸿沟。**今年的所有新趋势，本质上都是在填这道沟。**

---

## 趋势一：第三次范式跃迁 —— Prompt → Context → Harness

### 三个阶段

| 阶段 | 时间 | 核心问题 | 核心隐喻 |
|---|---|---|---|
| **Prompt Engineering** | 2022-2024 | 怎么把这一次问好？ | 写好一封邮件 |
| **Context Engineering** | 2025 | 给 Agent 看什么？ | 给邮件附上所有正确的附件（Tobi Lutke，Shopify CEO） |
| **Harness Engineering** | **2026** | 怎么设计跨会话、跨 Agent 角色、跨执行阶段的**完整系统**？ | 设计整条流水线 |

**第二阶段的突破性认知**：*「模型的表现上限取决于上下文的质量，而非 prompt 的措辞。」*

**第三阶段的抽象层次跃升**：不再关注「一次对话」或「一次上下文窗口」，而是**跨越多个会话、多个 Agent 角色、多个执行阶段的完整系统架构**。

### 两句关键引语

**OpenAI 工程师 Ryan Lopopolo**（团队用 Agent 构建百万行代码产品后总结）：

> **"Agents aren't hard; the Harness is hard."**

**Mitchell Hashimoto**（HashiCorp 创始人）给出的操作性定义：

> **"Every time you discover an agent has made a mistake, you take the time to engineer a solution so that it can never make that mistake again."**

**注意这句话的落点**：不是「修代码」，而是「**修 Harness**」——从根源上消除同类问题再次发生的可能。

### 一句话定义

> **Harness Engineering 是围绕 AI Coding Agent 设计和构建约束机制（Constraints）、反馈回路（Feedback Loops）、工作流控制（Workflow Orchestration）与持续改进循环（Continuous Improvement）的系统工程实践。**

---

## 趋势二：「Agent 无法评估自己的产出」被确认为核心工程问题

这是本轮调研中**最有解释力的一个发现**。

### Anthropic 的结论

> **"Agents are incapable of accurately evaluating their own work."**

**这句话的分量**：它意味着**不能依赖 Agent 自我审查**，必须构建外部化的、自动化的质量验证体系。

### 四种失败模式（Anthropic Harness 工程博客总结）

| # | 失败模式 | 表现 | 关键数据 |
|---|---|---|---|
| 1 | **One-shot Syndrome** | 拿到复杂需求后试图在单个上下文窗口内完成全部 | 上下文窗口 **Sweet Spot 在 40% 以下**填充率；超过则幻觉/循环/格式错误快速增加 |
| 2 | **Premature Victory Declaration** | 完成部分工作就宣布结束，输出「编码完成」但编译都不过 | — |
| 3 | **Premature Feature Completion** | 认为功能已实现但未做端到端验证，部署后才发现关键路径不通 | 应对：**Browser Automation（Puppeteer MCP）做自动化端到端验证截图** |
| 4 | **Cold Start Problem** | 多会话间缺乏持久化记忆，每次新会话花大量 token 重新理解项目 | — |

**共同根源**：Agent 缺乏外部的结构化约束（Structured Constraints）和反馈机制（Feedback Mechanisms）。

### 应对：角色分离

Anthropic 在 Harness 设计中明确分离三种角色：**Planner（规划）/ Generator（实现）/ Evaluator（验证）**。

> **核心发现**："将做事的 Agent 和评判的 Agent 分开，是一个强有力的杠杆（Powerful Lever）。"

**这条原则向上延伸就是 RSI 的基础**——`Agent-as-a-Judge`（见趋势六）。

---

## 趋势三：Harness 四支柱成为事实标准

综合 Anthropic 的长时任务实践与 OpenAI 用 Codex 构建百万行产品的经验（**3→7 人团队，产出约 1M LOC、1,500 PRs、人均 3.5 PRs/天、效率提升约 10 倍**），可归纳为四根支柱：

### 支柱一：上下文架构 —— 恰好够用，不多不少

**OpenAI 的教训**：早期把 `AGENTS.md` 写成了**百科全书**，结果是——

> **「所有内容都重要 = 没有内容重要」**

**修正方案**：`AGENTS.md` 控制在 **~100 行**，作为**索引和地图（Index & Map）**，指向更深层的 Design Docs、Architecture Specs、Quality Criteria。

**三层加载策略**（实战总结）：

| 层 | 加载时机 | 内容 |
|---|---|---|
| **L1 会话常驻** | 每轮都在 | Agent 定义文件（约 420 行，Index & Map）+ 3 份 Rules |
| **L2 阶段触发** | 进入某阶段时 | 当前阶段的 Skill + 该阶段需要的规范 |
| **L3 按需查询** | Agent 自主决定 | Wiki 业务文档 |

**核心考量**：让 Agent 在任何时刻都拥有「**刚好够用的上下文（Just-enough Context）**」。

### 支柱二：Agent 专业化 —— 受限工具集优于全权限

> 拥有**受限工具集（Constrained Toolset）**的专业 Agent，优于拥有全部权限的通用 Agent。

具体做法就是趋势二的 Planner / Generator / Evaluator 三角色分离。

### 支柱三：持久化记忆 —— 写文件系统，不写上下文窗口

**Anthropic 的标准化启动序列**：

```
检查当前工作目录
  → 读取 Git Log 和进度文件（如 progress.md）
  → 定位优先级最高的未完成任务
  → 开始工作
```

**这使得跨越数十个会话的长时间任务成为可能。** 配合趋势七（长任务能力指数增长）看，这是让长任务真正可用的前提。

### 支柱四：结构化执行 —— 质量门禁 + 精确回退

**铁律**：**永远不让 Agent 在未经审查和批准书面计划之前写代码。**

理想流程：**理解 → 规划 → 执行 → 验证**，每个阶段之间有明确的质量门禁。

**实战中的完整设计**（10 阶段流水线）：

```
需求分析 → 需求评审 → 编码实现 → 编码评审 → 单元测试编写
→ 单元测试评审 → 代码推送 → CI 验证 → 部署验证 → 用户确认
```

每个阶段有三要素：**触发条件（Entry Criteria）/ Skill 加载（Skill Injection）/ 质量门禁（Quality Gate）**

**精确回退路径（Rollback Routes）**：

| 失败 | 回退到 |
|---|---|
| CI 失败且测试为 0/0 | 阶段 5（测试编写） |
| 编译错误 | 阶段 3（编码实现） |
| 需求不符 | 阶段 1（需求分析） |

**评审循环上限（Iteration Cap）**：需求评审最多 3 轮，编码/测试评审最多 2 轮，超出升级人工——**防止 Agent 陷入无限自我修改循环**。

**5 个 Human-in-the-Loop 确认点**：需求待决议 / 计划评审后 / 编码评审后 / 部署环境参数 / 最终交付。

### 两条值得记住的原则

> **"Waiting is expensive, fixing is cheap."**
> ——宁可让 Agent 多跑一轮验证，也不要在人工 Review 时才发现问题。

> **"The agent's knowledge boundary equals the repository's file boundary."**
> ——**如果某条架构约定不在代码库中以机器可读的形式存在，对 Agent 来说它就不存在。**

**第二条尤其深刻**：它解释了为什么「写在群聊里的约定」等于不存在，也解释了趋势四（KYA）和 skills 生态爆发的根本原因。

---

## 趋势四：Agent 身份与支付 —— 从 KYC 到 KYA

**这是 2026 年最被低估的一条趋势线。** 2026-09-10 一天之内发生了两件事：

### 事件 A：印度 NPCI 筹建 AI Agent Registry

路透社援引知情人士报道，**印度国家支付公司（NPCI）**正在为其筹划中的 **Unified Agentic Protocol** 建设一套 **AI Agent Registry**，用于审核、验证并**持续监控**那些代表用户在 UPI 网络中发起支付的 AI Agent。

**规模量级**：UPI 仅 2026 年 8 月一个月就处理约 **245.1 亿笔交易**，金额约 **29.82 万亿卢比**。

**路线图**：从低金额高频消费（日用品）起步，未来可能扩展到「价格达阈值自动买入」，甚至执行投资行为；Registry 可能从 UPI 延伸到银行卡、账单支付。

### 事件 B：Ant International + Mastercard + Visa 联合推进 KYA 互操作框架

同一天宣布推进 **Know-Your-Agent Interoperability Framework**，建立在三方既有协议之上：

| 一方 | 协议 |
|---|---|
| Visa | Trusted Agent Protocol |
| Mastercard | Verifiable Intent |
| Ant International | Agentic Mobile Protocol |

**三个设计重点**：
1. **Operator Traceability** —— 把 Agent 追溯到经过验证的运营者、持卡人或组织
2. **共享的 Certification Requirements** —— 标准化验证 Agent 的安全与行为能力
3. **Continuous Transaction Monitoring** —— 依据身份、交易行为与风险信号**持续重新评估**

**Mastercard 走得更远**：其 **Agent Pay** 体系已公开使用 KYA 说法，并通过 Verifiable Intent 证明交易确实来自经过认证的用户意图与明确同意；面向机构场景引入程序化 **Permissioning**（预设授权规则与消费边界）。

### 为什么 KYC 之后必然出现 KYA

**传统前提**：Identity 和 Action 属于同一个主体——「提出意图的人、拥有权限的人和最终按下按钮的人，本来就是同一个人。」

**Agent 打破了这个前提**：

```
过去：Human ──→ Action
现在：Human → Agent → Tool → Payment Network → Merchant
```

链条拉长后，只知道 Human 是谁不够了。系统还必须知道：**这个 Agent 是谁、谁在运行它、谁把权限委托给了它、它此刻执行的是哪个任务、这次调用是否仍在那个任务被允许的范围内。**

### 信任链的完整形态

| 阶段 | 链 |
|---|---|
| 传统 | `Identity → Permission → Action` |
| Agent 时代（中间状态） | `Identity → Delegation → Mission → Intent → Boundary → Action` |
| 完整因果链 | `Human → Agent Identity → Delegation → Intent → Boundary → Execution → Evidence` |

### 哲学转变：从「信任主体」到「信任执行」

原文讲得极透：

> 一个 AI Agent 可能完整走完全部 KYA 流程：真实存在、注册合法、证书有效、平台可信、可追溯到真实用户，用户也确实授权它「帮我买一张周五晚上去上海的机票，预算不超过 2000 元」。
>
> 但接下来仍可能出现完全不同的执行结果：**误解日期、选择用户不接受的机场、在原始任务已被取消后继续执行、因 Prompt Injection 悄悄改变目标、或仍握着完全合法的 Credential 却把这笔 1800 元的授权用在另一个毫不相干的交易对象上。**
>
> **这里没有 Credential Theft，没有 Identity Spoofing，没有未经注册的 Agent，甚至没有传统意义上的权限越界。**

**核心转变**：

> 从 **"Can I trust this Agent"** 变成 **"Can I trust this execution"**。

> **真正的成熟，不是从不可信的人走向可信的人，而是从可信的人走向可信的结构。**

**新口号**：

| | 保护对象 |
|---|---|
| `Money can only move through **authenticated identities**` | 账户 |
| `Money can only move through **authorized executions**` | **现实结果** |

### 一个尚未解决的问题：责任归属

路透社在报道 NPCI 计划时特别提到：**对于错误支付或未经授权支付究竟由谁承担责任，监管层面仍未有定论。**

**这个空白本身是重要信号**——只要责任无法沿因果链分配，就说明产业仍缺少把 Delegation / Intent / Boundary / Execution / Evidence 串起来的技术结构。

---

## 趋势五：智能体商业协议标准化竞赛

| 协议/产品 | 方 | 时间 |
|---|---|---|
| **Agentic Commerce Protocol (ACP)** | OpenAI | — |
| **Universal Commerce Protocol (UCP)** | **Google**（开源） | **2026-01** |
| **Agent Pay** | Mastercard（对全美持卡人开放） | 2025-11 |
| Stripe + Tempo | Stripe | 2026-03 |
| **Agent Wallet**（智付底座） | 连连数字 | 2026-04 |

**Google UCP 的定位**：开源的商业协议规范，目标是在 AI 时代支持由 AI Agent 主导的电商交易体验——定义 AI 电商系统如何在**商品发现、评估、结账与下单**全流程中与商家交互。

**信号**：2025 年被认为是「智能体阶段的第一年」。**支付与电商是第一批出现跨厂商协议竞争的领域**——这通常是基础设施成熟的前兆。

---

## 趋势六：RSI 递归自进化成为研究前沿

**虎嗅（2026-03-24）的判断**：「**2026 Agent 最大突破是『递归自进化』**，三年后有望实现『神经计算机』」。

### 三层定义

| 层 | 含义 |
|---|---|
| 自修改 | 系统能改自己的代码 |
| 自改进 | 改完确实变强 |
| **递归自改进（RSI）** | **多次迭代，且新版本在「改进自身的能力」上超越前代** |

### 关键使能技术：Agent-as-a-Judge

> **Agent-as-a-Judge 之所以重要，不只是因为它能评估，更因为它为 recursive self-improvement 提供了（闭环）。**

**这正好接回趋势二**——「Agent 无法评估自己的产出」，所以要用**另一个 Agent** 来评估。

### 代表工作

| 工作 | 方 | 内容 |
|---|---|---|
| **MASS**（多 Agent 自监督） | UC Berkeley + Sakana AI | 联合学习编排 + 有界子 Agent 执行。对照实验：单 Agent 学生模型用**多约 1.4 倍的已处理监督 token** 训练，胜率 **64.0%** |
| **RSI-Anything** | PhAI Labs | 从代码/数学等数字任务，走向需要连续交互的计算机环境乃至物理世界 |

**MASS 的结论**：*「优化 Agent 之间的协作方式，并让各个子 Agent 在明确的任务范围内执行工作，有助于提高训练数据的质量。」* —— 与趋势三的「Agent 专业化」互相印证。

### ⚠️ 必须标注的风险

RSI 同时是**最有争议**的方向。它把「Agent 无法自评」的问题从工程问题升级为**对齐问题**：如果改进者与被改进者是同一类系统，评估偏差会被递归放大。**这也是 Agent-as-a-Judge 必须独立的根本原因。**

---

## 趋势七：长任务能力指数增长，失败模式同步放大

### METR 的量化

METR 于 2025-03 提出「**50% 任务完成时间跨度**」指标（模型在 50% 成功率下能完成的任务，对应人类完成所需的时间长度）。其经验外推线：

> **"the length of tasks models can complete is well predicted by an exponential trend, with a doubling time of around 7 months"**

**即：能力大致每 7 个月翻倍。**

### 一个具体案例（2026-05）

**Claude Mythos Preview**：
- **17 小时长任务**
- 一个月修掉 **423 个 Firefox bug**

按 7 个月翻倍曲线，从 1 小时到 17 小时是 4 次翻倍 ≈ 28 个月。若该案例属实，**实际进度快于 METR 的拟合曲线**。

### 评测基准的同步升级

**AgencyBench**（2026 年初）：标志着评测进入「百万 Token」时代——**138 个真实场景任务，平均需要约 90 次工具调用**，重点考察 Agent 在**长达数小时的长程任务中的稳定性**，而非单步决策。

### ⚠️ 反面：能力增长放大失败后果

**注意一个不对称**：任务时长翻倍，意味着**失败的影响面也翻倍**。

- 1 小时任务出错 → 浪费 1 小时
- 17 小时任务出错 → 浪费 17 小时 + 可能已产生副作用（改了代码、发了 PR、动了钱）

**这解释了为什么 Harness 的「质量门禁 + 精确回退 + 循环上限」在 2026 年成为刚需**——不是因为模型变差了，而是因为**试错成本随任务长度线性上升**。

---

## 趋势八：Agent 安全焦点从「注入」转向「过度自主」

### OWASP GenAI LLM Top 10 2026 的核心变化

**风险焦点从 Prompt Injection 转向 Excessive Agency（过度自主权）。**

新的 ASI 分类（Agentic Security 类目）覆盖：

| 编号 | 风险 |
|---|---|
| ASI02 | **Tool Misuse & Exploitation**（工具滥用） |
| ASI03 | **Identity & Privilege Abuse**（身份与权限滥用） |
| ASI04 | **Agentic Supply Chain Vulnerabilities**（Agent 供应链漏洞） |
| ASI05 | **Unexpected Code Execution**（意外代码执行） |
| ASI06 | **Memory & Context Poisoning**（记忆与上下文投毒） |
| ASI07 | **Insecure Inter-Agent Communication**（不安全的 Agent 间通信） |

**这个清单本身就是趋势信号**：从「输入被污染」转向「Agent 自己做的事越界了」。

### 一个深刻的技术洞察（Docker 博客，2026-05-18）

> **The agent's context window is a flat namespace.** The credential file looks the same as the source file looks the same as the README looks the same as the prompt injection. **There's no architectural distinction between "data the agent should treat as authoritative" and（不可信数据）.**

**「Agent 的上下文窗口是一个扁平命名空间」**——凭证文件、源码文件、README、prompt injection 长得一模一样，架构上没有任何区分。

**这是对当前 Agent 架构最尖锐的批评之一**，也解释了为什么会出现下面的动作。

### 行业级动作

**英伟达联合逾 100 家厂商推出 Open Agent Safety Platform**，核心组件为 **OpenShell 开源沙箱**。

> ⚠️ **本条据行业日报转述，未见官方公告核实，需谨慎对待。**

**本会话前几轮的一手核验可佐证这个方向的真实性**：skills.sh 上有 **`bitwarden/ai-plugins`（65 个 skill，密钥管理）**、**`auth0/agent-skills`（34 个）**、**`clerk/skills`（31 个）**、**`coinbase/agentic-wallet-skills`（29 个）**、**`microsoft/azure-skills` 含 `entra-agent-id`**——**认证、密钥、Agent 身份已经成为官方 skill 生态里成规模的品类。**

---

## 趋势九：多 Agent 从「预定义团队」走向「运行时动态派生」

### 变化

| | 传统多 Agent | 2026 新形态 |
|---|---|---|
| 团队结构 | **预定义** | **运行时动态派生** |
| 生命周期 | 固定 | 任务完成后**自动解散** |
| 隐喻 | 组建一个团队 | **按需扩缩，一个指令孵化一支临时团队** |

### 三种架构（已形成共识分类）

- **Orchestrator（主控）** —— 一个中心 Agent 调度
- **Peer-to-peer（对等）** —— Agent 之间直接协作
- **Hierarchical（层级）** —— 多级嵌套

### 与趋势三的关系

**「动态派生子 Agent」正是「Agent 专业化」的自然延伸**：不再预先定义所有角色，而是**在需要时按任务派生一个受限工具集的专家**。

**本会话的一手证据**：skills.sh 上 `obra/superpowers` 的 **`subagent-driven-development`**（两阶段审查：先查 spec 合规，再查代码质量）、**`dispatching-parallel-agents`**（并发 subagent 工作流）、`stablyai/orca` 的 **`orchestration`**（289.3K 安装）——**「多 Agent 编排」已经是一个有专门 skill 的成熟品类**。

---

## 趋势十：记忆从「会话内」升级为「跨会话基础设施」，并成为新攻击面

### 升级路径

```
会话记忆（有窗口就丢）
  → 跨会话持久记忆
  → 文件系统 / 图记忆 / 向量记忆 混合架构
```

**Anthropic 的实践已经把它标准化**：进度写 `progress.md` + 读 Git Log，**而不是塞进上下文窗口**（见趋势三支柱三）。

**本会话的一手证据**（skills.sh 上「记忆」已成规模品类）：
- `mem0ai/mem0`（67,153★）
- `MemTensor/MemOS`（11,854★，自述 hybrid-retrieval + 省 35.24% token）
- `basicmachines-co/basic-memory`（4,167★，Markdown 本地记忆）
- `microsoft/kernel-memory`、`memodb-io/memobase`、`doobidoo/mcp-memory-service`
- 以及 Anthropic 官方 `Knowledge Graph Memory`

### ⚠️ 但记忆同时成为攻击面

OWASP 2026 把 **ASI06 Memory & Context Poisoning（记忆与上下文投毒）** 单列为风险项。

**逻辑很直接**：记忆是**跨会话持久**的，一旦被投毒，**污染会持续影响后续所有会话**——比一次性的 prompt injection 危害大得多。而且记忆通常由 Agent **自动写入**，人不会逐条审查。

**这是一个尚未被充分重视的新风险。**

---

## 反趋势：三个「降温信号」

**一个成熟的趋势报告必须包含反面证据。** 2026 年有三条明确的降温信号：

### 信号一：上下文文件可能不划算

**ETH Zurich + LogicStar.ai 实验**（300 个 SWE-bench Lite + 138 个 CTXbench）：

| 条件 | 成功率 | 成本 |
|---|---|---|
| 自动生成的仓库级上下文文件 | **无显著提升** | **+20%** |
| 开发者亲手写的上下文文件 | +2.4%（**统计不显著**） | 同样增加 |

**且**：*「实验结果与文件长度没有明显关系，成本增加更可能来自每条指令所触发的行为。」*

### 信号二：旧提示词会主动伤害

**Claude Code 创造者 Boris Cherny**：为适配 Opus 5 **删掉 >80% 系统提示词**；**消融测试发现删掉后模型有时显得更聪明**。

### 信号三：窗口变大不等于变好

> **"context windows are constrained not by raw token capacity but by attention mechanics"** —— 随长度增加会出现 lost-in-the-middle、U 型注意力曲线、注意力稀缺。

**「把窗口当垃圾桶」是 2026 年最普遍的反模式。**

---

## 小结：2026 年的 Agent 在解决什么问题

把所有趋势收敛成一句话：

> **2026 年的 Agent 工程，正在从「让模型能做」转向「让系统的产出可被信任」。**

| 趋势 | 在解决什么信任问题 |
|---|---|
| 一、Harness Engineering | 谁来保证跨会话的产出质量 |
| 二、自我评估缺陷 | 模型不能自评，谁来评 |
| 三、四支柱 | 用什么结构保证 |
| 四、KYA | 谁在代表谁行动 |
| 五、商业协议 | 机器之间怎么交易 |
| 六、RSI | 系统能不能改进自己（以及谁来评估这个改进） |
| 七、长任务 | 时间越长，信任成本越高 |
| 八、安全 | 越自主，越需要边界 |
| 九、动态多 Agent | 谁负责哪个局部 |
| 十、记忆 | 跨会话的连续性靠什么保证 |

**贯穿所有趋势的一条主线**：**「把隐性知识显性化、把主观判断结构化、把一次性经验固化为可复用约束」**。

这正好解释了本会话前九轮观察到的现象：**skills 生态（102 家官方厂商、数千个官方 skill）和 MCP 生态的爆发，本质上都是这条主线的产物。**

---

## 数据可信度

### 来源分级

| 级别 | 来源 | 可信度 |
|---|---|---|
| **A 级（一手）** | 本会话前九轮的一手核验数据（skills.sh 176 榜单 / 102 官方厂商 / 50 条审计 / 143 个 MCP 仓库）；Anthropic 官方工程博客原文；agentskills.io 规范原文 | **高** |
| **B 级（官方报告引述）** | Anthropic《2026 Agentic Coding Trends Report》（经二手引述）；METR time horizon 系列（经二手引述）；OWASP GenAI LLM Top 10 2026（经二手解读） | 中高 |
| **C 级（具名实战复盘）** | 阿里云开发者 Harness Engineering 实战（作者具名、含完整方法论与实测数字）；路透社 NPCI 报道引述；虎嗅 KYA 分析（作者 Havenlon Labs） | 中高 |
| **D 级（待核实）** | Open Agent Safety Platform / OpenShell 沙箱（**仅见行业日报转述**）；Claude Mythos Preview 的 17 小时 / 423 bug（**单一来源**） | 中低 |

### 明确未核实 / 存疑项

1. **「Anthropic 2026 Agentic Coding Trends Report」的原始报告**：本轮只拿到二手引述的「60% vs 0-20%」数字，**未找到报告原文**。
2. **Open Agent Safety Platform / OpenShell**：**仅见二手行业日报转述**，未找到英伟达官方公告。原引述文章本身也标注为「据转述、待官方公告核实」。
3. **Claude Mythos Preview 的 17 小时长任务与 423 个 Firefox bug**：**单一来源**（知乎），未从 METR 或 Anthropic 官方确认。
4. **METR「7 个月翻倍」**：为 METR 论文中的经验外推线，且**不同基准的 time horizon 边界相差超过 100 倍**，单条曲线不能代表所有任务类型。
5. **NPCI 的 AI Agent Registry 计划**：路透社引述**知情人士**，**NPCI 官方未确认**，细节仍在酝酿。
6. **Visa/Mastercard/Ant International 的 KYA 框架**：公告自述为「正在形成中的框架」，**既无公开技术规范，也无治理机构和时间表**。
7. **OpenAI 百万行代码案例**（3→7 人 / 1M LOC / 1,500 PRs / 10 倍效率）：来自二手引述，**未找到 OpenAI 官方出处**。
8. **Harness 实战的 24.86% → 90.54%**：**单一项目的自述数据**，非受控实验，且「AI 代码采纳率」的定义可能因团队而异。
9. **RSI 的能力边界**：MASS / RSI-Anything 均为**近期论文，未见独立复现**。

### 本轮方法说明

**一个反复出现的困难**：中文科技媒体的深度文章大量托管在**知乎（拒绝抓取）和微信公众号（需鉴权）**，本轮多篇文章只能通过 WebFetch 的摘要或转载站（uml.org.cn、CSDN、百家号）获取。**这导致部分引述存在「二次转述」风险**，已在来源分级中标注。

**相对可靠的做法**：优先抓取**带具名作者、含完整方法论和原始数字**的实战复盘（如阿里云开发者那篇 Harness 文章），以及**能拿到原文的规范类文档**（agentskills.io 的 `.md` 端点）。

---

*报告生成：2026-10-14 ｜ 核验：Anthropic 官方博客 + agentskills.io 规范原文 + 阿里云 Harness 实战复盘 + 路透社引述 + METR 系列 + OWASP 2026 解读 + 本会话前九轮一手数据 ｜ 本机环境：Windows 11*
