---
type: Checklist
---

# GitHub AI 趋势日报 · 2026-10-15

> 数据源：github.com/trending 主榜（daily 12 / weekly 12 / monthly 22）+ 18 个语言维度榜（python / typescript / rust / go / c / c++ / javascript / java / swift / vue / html / cuda / jupyter-notebook / csharp / kotlin / ruby / shell / php，均为 `?since=daily`），合计 305 条、去重 282 个仓库。抓取 21 个榜一次全过、0 次重试。
> 距上期（10-13）相隔 2 天。**主榜 46 条中仅 3 条新面孔**（vxcontrol/pentagi、K-Dense-AI/scientific-agent-skills、twostraws/SwiftUI-Agent-Skill），本期 10 条详细中 7 条来自语言维度榜。
> 增幅口径：`+N stars today / this week / this month`，**不同榜的周期不可互相比较**，本文每条标注来源榜。

---

## 一、榜单速览

| # | 仓库 | 语言 | 总 Star | 增幅 | 来源 | 一句话 |
|---|---|---|---|---|---|---|
| 1 | [vxcontrol/pentagi](https://github.com/vxcontrol/pentagi) | Go | 29,861 | +1,025 (today) | main daily / lang:go | 自托管多 Agent 自主渗透测试，20+ 工具跑在 Docker 沙箱 |
| 2 | [google/agentmesh](https://github.com/google/agentmesh) | Go | 1,067 | +40 (today) | lang:go | Google 官方 Agent 私有网络，默认零可达 + OIDC 身份 |
| 3 | [vercel-labs/skills](https://github.com/vercel-labs/skills) | TypeScript | 34,990 | +658 (today) | lang:typescript | `npx skills` CLI 本体，支持 79 个 agent |
| 4 | [twostraws/SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill) | Markdown | 6,001 | +930 (this week) | main weekly | Paul Hudson 的 SwiftUI Pro 技能，专打 LLM 常犯错误 |
| 5 | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | Python | 49,604 | +163 (today) | main daily / lang:python | 177 个科研技能 + arXiv 论文，从 Claude 专属改为跨宿主 |
| 6 | [MakazhanAlpamys/Soup](https://github.com/MakazhanAlpamys/Soup) | Python | 9,051 | +247 (today) | lang:python | 一个 YAML 微调 LLM，8B 在 4GB 笔记本 GPU 上训 |
| 7 | [Crosstalk-Solutions/project-nomad](https://github.com/Crosstalk-Solutions/project-nomad) | TypeScript | 40,195 | +274 (today) | lang:typescript | 离线优先知识/教育服务器，Docker 编排一整套离线栈 |
| 8 | [TecharoHQ/anubis](https://github.com/TecharoHQ/anubis) | Go | 23,412 | +64 (today) | lang:go | Web AI 防火墙，用工作量证明挡爬虫 |
| 9 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | TypeScript | 74,716 | +146 (today) | lang:typescript | Claude Flow 改名 Ruflo，Claude Code / Codex 的 meta-harness |
| 10 | [ggml-org/Llama-Windows](https://github.com/ggml-org/Llama-Windows) | C# | 128 | +41 (today) | lang:csharp | ggml 官方 Windows 11 托盘应用，一键跑 llama.cpp |

---

## 二、10 条详细

### 1. vxcontrol/pentagi —— 自托管多 Agent 渗透测试，把"能力边界"单独写成章节

**事件**：Go 项目 PentAGI 进入主榜 daily，日 +1,025，总 29,861，forks 4,480。作者 VXControl 是迪拜的一家安全工程公司。

**核心内容**
- 定位：开源、自托管的**多 Agent 自主渗透测试系统**。用自然语言描述目标与目标，一组专职 Agent 规划工作、在隔离 Docker 沙箱内运行 **20+ 专业工具**（nmap、Metasploit、sqlmap 等），记忆已知信息，最后出报告。
- 模型侧不锁供应商：内置 10+ 云 LLM 供应商 + 任意 OpenAI 兼容端点（含 Azure OpenAI）+ 本地 Ollama / vLLM，附一份 `vLLM + Qwen3.5-27B-FP8` 生产部署指南；聚合器侧接 OpenRouter / DeepInfra / Atlas Cloud / OpenCode Go plan。
- 记忆与图谱：结果与成功手法存 PostgreSQL + **pgvector**；可选 **Neo4j 知识图谱（Graphiti 驱动）**追踪主机、服务、发现之间的语义关系。
- 工程面：REST + GraphQL 双 API（Bearer token）、Langfuse（LLM 可观测）+ Grafana/Prometheus（系统监控）双看板、微服务架构可横向扩、Docker Compose 交互式安装器覆盖 Linux/macOS/Windows。
- 企业版增量：Agent profiles、插件、MCP server、客户级报告、实时攻击链视图。
- **自陈能力边界（单独成节）**：明确说 PentAGI 是"自主 + 助手引导的渗透测试平台"，**不是 CALDERA 式 BAS / 对手仿真产品**，没有预定义战役与攻击计划；"BAS 式 Agent 自写攻击脚本"属概念或未来工作，**不是今天已实现的功能**；JSON flow-report 导出**今天不算受支持输出格式**。

**值得关注的原因**
- 渗透测试这条线在过去两期已经有三家（10-05 ARTEX 双图架构、10-12 Armur-Ai/Pentest-Swarm-AI、10-13 速览），**本期是第一条走"自托管 + 知识图谱 + 企业版"路线的**：不追求评测基准，先解决"在我自己的机器上、用我选的模型、数据不出门"。
- 与 10-12 的 ARTEX 对照看更有意思：ARTEX 把状态放在**图与清单**里、planner 是唯一意图生成者；PentAGI 把状态放在 **PostgreSQL+pgvector 与可选 Neo4j** 里。两者都在回答"无状态会话下，Agent 的记忆放哪"。
- **"Current Capability Boundaries" 这个章节名本身就是信号**：把"我们不是什么"写成 README 一级结构，与 10-13 微软 litebox、10-12 webcodex 属同一条纪律——先否掉读者可能有的错误期待。

---

### 2. google/agentmesh —— Google 官方给 Agent 做的私有网络，默认零可达

**事件**：全新仓库 `google/agentmesh` 首次出现在 Go 语言榜（+40，总 1,067，forks 174）。README 明确写"已把名字更新为 **Agent Mesh** 以更贴合生态定位"。

**核心内容**
- 一句话：**给 AI Agent 用的私有网络**。节点跑在 Agent 旁边，提供三件事——把工具与模型**发布**到网络、**发现并调用**别人发布的东西、一个所有节点都能验证的**身份**。
- 两条全局性质：
  - **默认什么都不可达**：节点的服务在配置显式声明前不暴露；任何节点不得调用 mesh 策略未授予的服务；**授权按服务名判定，永不按地址判定**。
  - **身份来自你自己的身份提供方**：节点用 OIDC token 或一次性 bootstrap token 入网，控制平面把它换成**短期、可离线验证**、绑定节点自身密钥的凭证。
- 网络：能直连就直连，不能直连走 relay，因此可跨笔记本 / 容器 / 集群 / 手机，且穿透 NAT。
- 四个程序：`agentmesh-control-plane`（验证入网、签发凭证、持有策略）、`agentmesh-router`（知名对等点 + 中继 + 发现表）、`agentmesh-node`（跑在 Agent 旁，把本地后端发布到 mesh，并把 mesh 以**本地 MCP server + OpenAI 兼容 API** 暴露给 Agent）、`agentmesh-one`（控制平面 + router + Web 控制台合一的单二进制，面向笔记本与小规模部署）。
- 上手成本刻意压低：一行 install 脚本 → `agentmesh-node join <testnet>` → `agentmesh-node run --daemonize`（本地 MCP server 在 `127.0.0.1:8080`）→ `agentmesh-node skill install` 教会 Agent 使用；也可用 GitHub Codespaces 一条 `make testnet` 在自己账号的免费额度上起一个带公网 HTTPS 的控制平面，让笔记本和手机都能入网。
- **状态与免责**：pre-1.0；node / router / control plane / 身份与策略模型"形状已稳定"并有测试套件与两个公开 testnet 验证；沙箱化 Agent 蓝图与移动端 App 仍是 preview。Apache-2.0，**明确声明这不是 Google 官方支持的产品，也不在 Google 开源漏洞奖励计划范围内**。

**值得关注的原因**
- 这是**大厂第一次把"Agent 之间的网络层"做成独立开源项目**。此前同类都在单机或单集群内（10-09 微软 mxc 管策略、10-08 K8s SIG 的 agent-sandbox 管编排、10-13 litebox 管内核），Agent Mesh 补的是**跨机器、跨网络、跨组织的发现与授权**这一格。
- 两处设计判断值得抄：①**授权绑服务名不绑地址**——地址会变（容器重建、IP 漂移），服务名是意图；②**控制平面签发的凭证必须能离线验证**——否则每次调用都要回连控制平面，网络分区即全线瘫痪。
- 与 10-12 celld（Deno 用条件写代替共识）形成对照：两者都在"去中心化的 Agent 基础设施"上做减法，一个减共识、一个减可达面。

---

### 3. vercel-labs/skills —— 过去多期反复出现的 `npx skills` 本体首次上榜

**事件**：`vercel-labs/skills` 进入 TypeScript 语言榜，日 +658，总 34,990，forks 2,981。npm 包名就是 `skills`。

**核心内容**
- 定位：**开放 agent 技能生态的 CLI**。支持 OpenCode、Claude Code、Codex、Cursor 以及另外 75 个 agent（README 顶部由 `agent-list` 标记自动生成，属"文档不漂移"的做法）。
- 源格式覆盖极广：GitHub 简写 / 完整 URL / 仓库内子路径 / GitLab / **Azure Repos（含 `?path=` 与 `version=GBmain` 参数）** / 任意 git URL（含 `git@`）/ 本地路径 / **直链 SKILL.md 或 `.zip`·`.tar`·`.tar.gz`·`.tgz`**。
- 私仓复用既有凭据且**不搬运 token**：GitHub HTTPS 与简写源先走普通 Git 凭据，失败且 gh CLI 已登录则试 `gh repo clone`，再退 SSH；**明确不执行 `gh auth token`、不把 gh 凭据拷进 Node 进程**；tree 查询先匿名 API、再显式环境 token、再 `gh api`，凭据永不打印。
- 下载有界：直链下载默认上限 **10 MiB**、解压内容 **25 MiB**、压缩包 **1000 个文件**，三个上限各有环境变量可覆盖（`SKILLS_DOWNLOAD_MAX_BYTES` / `SKILLS_EXTRACT_MAX_BYTES` / `SKILLS_EXTRACT_MAX_FILES`）。
- 安装作用域与方式：project（`./<agent>/skills/`，随项目提交）vs global（`~/<agent>/skills/`）；交互式安装可选 **symlink（推荐，单一真源便于更新）** 或 copy。
- 命令全集：`add` / `use`（不安装直接用，把生成的 prompt 打到 stdout，或 `--agent` 直接交互起一个 agent）/ `list`(ls) / `find`（fzf 式交互，支持 `--owner` 限定组织）/ `update` / `init` / `remove`(rm)。

**值得关注的原因**
- 这是**过去至少六期报告里反复出现的那条命令（`npx skills add ...`）的官方仓库第一次自己上榜**。到本期为止，`npx skills add` 已经在 mattpocock/skills、addyosmani/agent-skills、twostraws、K-Dense 等多处被当作标准安装方式引用——**事实标准的分发层由 Vercel 持有，而不是任何一家模型厂商**。
- 值得抄的三条工程细节：①**凭据不落地**（不读 token、不打印、不拷进进程，只借 gh 的既有认证）；②**下载/解压三档上限默认开**（供应链侧的 fail-closed，与 09-30 NVIDIA SkillSpector 的"技能 26.1% 含漏洞"基线配套）；③**文档由标记自动生成**（agent 列表与 npm 版本徽章同步，防止支持矩阵漂移）。
- 与同期的 dotnet/skills、aws/agent-toolkit-for-aws、anthropics/claude-plugins-official 放在一起看：**厂商都在往"技能/插件分发"这一层落子**，而分发工具的赢家是平台方。

---

### 4. twostraws/SwiftUI-Agent-Skill —— 领域权威把二十年经验压成一个技能

**事件**：`twostraws/SwiftUI-Agent-Skill` 进入主榜 weekly，周 +930，总 6,001，forks 218。作者 Paul Hudson（Hacking with Swift / Total Swift 系列）。

**核心内容**
- 技能名 **SwiftUI Pro**，用途是让编码助手写出"更聪明、更简单、更现代"的 SwiftUI：覆盖导航、布局、动画、状态管理、VoiceOver、废弃 API 等。
- **设计目标写得非常具体：针对 LLM 真正会犯的错**——"它们有时把按钮做得对 VoiceOver 不可见、频繁使用已废弃 API、写出会引发意外性能问题的代码"。
- 采用 [Agent Skills](https://agentskills.io/home) 格式，因此 Claude Code、Codex、Gemini、Cursor 通用；同时提供 Claude Code 插件市场路线（`/plugin marketplace add twostraws/SwiftUI-Agent-Skill`）。
- 安装走标准路径：`npx skills add https://github.com/twostraws/swiftui-agent-skill --skill swiftui-pro`；README 还贴心地给出了 `npx: command not found` → `brew install node` → 没有 Homebrew 先装 Homebrew 的完整排错链。
- 触发方式三档：斜杠命令（Claude `/swiftui-pro`、Codex `$swiftui-pro`）、带参数的局部检查（`/swiftui-pro Check for deprecated API`）、自然语言。
- 这是一个**系列**而非单点：SwiftData Pro、Swift Concurrency Pro、Swift Testing Pro，外加一个索引仓库 Swift-Agent-Skills。
- **贡献指南里有条罕见的约束**："**不要重复 LLM 已经知道的东西，那会白烧 token**。聚焦边界情况、意外行为、软废弃（soft deprecation）这类。"并要求所有工作 MIT 授权以便最大化受益面。

**值得关注的原因**
- 技能生态到本期已经明显分层：**通用流程类**（mattpocock/addyosmani，管"怎么做工程"）vs **领域知识类**（本条目，管"这个框架的正确写法是什么"）。后者对作者权威性的依赖远高于前者——同一个 SKILL.md 标准，装的是完全不同的东西。
- **"针对 LLM 实际会犯的错"这个选题口径值得抄**：不是把官方文档压缩一遍，而是把"模型默认会写错的地方"显式列出。这与 10-13 mattpocock 的 GLOSSARY.md 压缩长句、10-12 asd-ste100 的受控语言，是同一思路在三个不同层面的实现。
- 附带一条产业信号：**Swift / Apple 平台是本期语言榜里少见的"技能供给充足"方向**（同榜还有 SwiftUI、SwiftData、Swift Concurrency、Swift Testing 四个 Pro 技能 + AltStore + FluidVoice + Rectangle），说明移动端 Agent 化的落地速度落后于后端，但技能层已经开始补齐。

---

### 5. K-Dense-AI/scientific-agent-skills —— 177 个科研技能，带论文和免责边界

**事件**：`K-Dense-AI/scientific-agent-skills` 同时进入主榜 daily 与 Python 语言榜，日 +163，总 49,604，forks 4,439。

**核心内容**
- **177 个科学与研究技能**，覆盖生物信息/基因组、化学信息与药物发现、蛋白质组与质谱、临床研究与证据工作流、医疗 AI 与生物信号、临床前研究与动物福利、显微与医学影像/数字病理、神经科学与电生理、机器学习、材料与化学、物理与天文、工程与仿真、数据分析与可视化、化学海洋学、地理空间与遥感、实验室自动化、科学传播、多组学与系统生物学、蛋白工程、Agent 平台与基础设施、研究方法论、法规与标准。
- **有论文**：arXiv:2609.00065《Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents》；技能库版本 v2.72.0。
- **改名本身就是核心信息**：原名 "Claude Scientific Skills"，现改名为 "Scientific Agent Skills"，理由写得很直白——"**同一批技能，更广的兼容性**：现在支持任何遵循开放 Agent Skills 标准的 AI Agent，不再只支持 Claude"。同时提供 [Agent Plugins](https://agent-plugins.org/) 可移植包形态（`plugin.json` + `skills/`），支持该标准的客户端可整包加载。
- 每个技能提供的不只是"怎么调包"，还包括**该领域的科学惯例与验证检查**；配套 100+ 科学数据库、技能指南（docs/skill-guides/）、完整目录（docs/skills.md）。
- 自家产品线：**K-Dense BYOK** —— 免费的本地 AI 科学家，自带 API key、40+ 模型可选、数据留在本机、重负载可选经 Modal 上云。
- **免责边界写到技能颗粒度**（本期最值得抄的部分）：
  - 临床研究与证据工作流：明确只做"**来源绑定的报告草稿结构**"与"临床医生撰写治疗决策的格式化"，不替医生决策。
  - 动物实验：多变量严重度评分与人道终点预测，**"是严重度评估的辅助，永远不是决策规则"**（服务于 3R / EU Directive 2010/63/EU 报告）。
  - 法规与标准：为 ISO 管理体系与实验室标准准备证据工件，**"供合格评审，永远不是认证、认可或方法放行决定"**。

**值得关注的原因**
- 与本期第 3、第 4 条合看，**技能层正在形成完整的产业链**：分发工具（vercel-labs/skills）→ 领域内容（scientific-agent-skills / SwiftUI Pro）→ 厂商市场（claude-plugins-official / aws / dotnet）。本期一天之内四层同时有项目上榜。
- **"从单一厂商专属改名成跨宿主"是一个可观察的趋势动作**：说明作者判断"绑定某个 Agent 品牌"的收益已经低于"覆盖所有宿主"。这与 10-12 Panniantong/Agent-Reach、10-13 mattpocock 的 `npx skills add` 多宿主分发是同向的。
- 免责写法值得所有垂类 Agent 项目抄：**不是在 README 底部加一句"仅供参考"，而是把"我能做到哪一步、由谁签字"写到具体技能条目里**。这与 09-23 anthropics/financial-services 把"人工签核"写进合规声明是同一套做法，本期扩展到了科研与医疗。

---

### 6. MakazhanAlpamys/Soup —— 一个 YAML 微调 LLM，且"从未生效的配置"现在直接拒绝加载

**事件**：Python 项目 Soup 进入语言榜，日 +247，总 9,051，forks 1,473。

**核心内容**
- 定位：**一条命令微调 / 后训练 LLM**，"不用 SSH、不用跟配置地狱搏斗"。流程三步：`pip install "soup-cli[train]"` → `soup init --template chat` → `soup train`。
- **核心能力是 layer streaming**：把冻结的基座权重留在显存之外，**一次只把一个 decoder layer 喂给 GPU**，因此能在 **4GB 笔记本 GPU 上微调 8B 模型**。opt-in 开关 `stream_layers: true`，仍标 BETA。
- **基准数字写得极其诚实，值得逐句读**：
  - 原始数字（v0.72.2）：RTX 3050 Laptop 4GB 上 Llama-3.1-8B-Instruct + NF4，**119.6 tok/s @ 952 MHz，峰值 3.32 GB**，与常驻运行**逐位一致（bit-exact）**，并在 H100 上以 113.00 tok/s 独立复现于同样的 3.32 GB。
  - 但 README 紧接着说明：**这些是 v0.73.0 正确性修复之前的数据**，修复在 32B 上付出了 −4.8%。
  - 修复后的数据（另一位贡献者 @umran666 的 RTX 3050 Laptop 4GB）：**208.6 tok/s @ 1935–1957 MHz，峰值 2.40 GB**。然后自己拆台：**"这 1.74× 的原始增益来自时钟，不是加速"**——1935/952 ≈ 2.03，折算下来每单位时钟反而慢约 14%（59% vs 68% 的 GEMM 上限占比）；而且大层流式改变了两行的内存访问模式，**"连这个比例也不是同类比较"**。
  - 附完整记录 `benchmarks/gate-v0.72.2-nf4.md`、论文 DOI、以及一个**免费 Colab T4 复现 notebook**（把进程限制到 4GB，然后断言流式模型与常驻模型逐位相同）。
- **v0.76.0 的破坏性变更（本期最硬的一条设计纪律）**：
  - **"Soup 接受却从未生效的设置，现在会在加载时直接拒绝。"** 那些被校验、被文档化、但在它声称配置的路径上**没有任何代码读取**的选项，现在会在加载时报错，**报错信息点名是哪个字段、该怎么改**；其余未读旋钮先警告，并**点名哪个版本会开始拒绝**。README 明说"**以前能加载的配置现在可能加载不了**"，建议先跑 `soup doctor --config soup.yaml`。
  - 被点名拒绝的包括：`training.quantization_aware: true`（**它从未真的跑过量化感知训练**）、`training.use_longlora`、`training.ebft_variant`、`training.gdpo_variant`、无 setup 读取时的 `rope_scaling_type`、文本 `sft`/`tts` 路径之外的 `freeze_layers`/`freeze_ratio`、`sft`/`tts` 之外的 `auto_mixed_precision`、以及七个没有 unsloth setup 的任务上的 `backend: unsloth`。
  - **验证损失现在真的被评估了**：`data.val_split` 一直在切出行，但 transformers 后端**没有任何 trainer 评估过它们**——现在每个拿到 split 的任务在每轮末尾（或按 `training.eval_steps`）评估并记录 val loss，代价是运行时间增加几个百分点。**对 `grpo`/`ppo`/`online_dpo` 是破坏性变更**：默认不再留出，每一行都参与训练。
  - **破坏性：每个非标准 `grpo_variant` 现在真的应用 `grpo_beta` KL 惩罚**。此前 `gspo`/`dapo`/`dr_grpo`/`bnpo`/`two_sided`/`rft` 校验了 `grpo_beta` 然后丢掉，**因此已有的变体配置无法复现之前的运行**；`grpo_beta: 0` 现在表示无 KL 并跳过 reference forward。
  - 层流式的磁盘层改为后台线程 + 直接 I/O，并可跨 NVMe 条带化：在一台 36 GB 的 70B 形状 NF4 存储、内存装不下的 RTX 5070 Laptop 8GB 机器上，冷启动一步从 **110.5 s（同步读）降到 16.2–17.3 s**。

**值得关注的原因**
- **"配置被接受但从未生效"是 2026 年被反复验证的一类静默失败**（10-05 ponytail 一行 plugin.json 让规则静默失效、10-06 claude-mem 的异步 hook 拦不住任何东西、10-12 engram 的 `/health` 能力协商）。Soup 的解法是**把它变成加载期硬错误，并在报错里点名字段与改法**——这是目前见到的对这类 bug 最彻底的一种工程回答：**不允许"配置看起来生效了"这种状态存在**。
- **自我削弱的基准披露又进一级**：过去几期的样本是"主动报出对自己不利的指标"（codegraph 自曝残余上下文 +80%、RuView 撤回 100% 检测率）；Soup 更进一步——**主动把自家最漂亮的数字（1.74×）拆解掉，说明它其实是时钟差异而非算法加速，并且明说连折算比例也不是同类比较**。
- 与 10-12 colibri（纯 C，MoE experts 留磁盘按需读）、10-13 airllm（2.8T 在 3.72GB VRAM 上训练）同属"**把显存门槛搬到磁盘带宽**"这条线：本期 Soup 把这件事做进了训练侧（此前多在推理侧）。

---

### 7. Crosstalk-Solutions/project-nomad —— 离线优先知识服务器，反着写硬件要求

**事件**：TypeScript 项目 Project NOMAD 进入语言榜，日 +274，总 40,195，forks 4,057。官网 projectnomad.us，另有独立的硬件 benchmark 社区榜。

**核心内容**
- 定位：**自包含、离线优先的知识与教育服务器**——"装满关键工具、知识和 AI，让你随时随地保持知情与有能力"。
- 架构：一个管理 UI（"Command Center"）+ API，**用 Docker 编排一整套容器化工具**，负责安装、配置、更新，用户不用管。安装是完全终端式的，所有功能通过浏览器访问，因此**不需要桌面环境**（可以纯当 server 跑，用别的客户端访问）。
- 内置能力（每项都标了上游组件）：
  - **AI 对话 + 知识库** —— 本地 Ollama（或 LM Studio / llama.cpp 等 OpenAI 兼容后端），文档上传 + 语义检索（**Qdrant**）
  - **信息库** —— 离线 Wikipedia、医学参考、电子书（**Kiwix**）
  - **教育平台** —— Khan Academy 课程与进度追踪（**Kolibri**）
  - **离线地图** —— 可下载区域地图（**ProtoMaps**）
  - **数据工具** —— 加解密/编码/分析（**CyberChef**）
  - **笔记** —— 本地 markdown 笔记（**FlatNotes**）
  - **系统 benchmark** —— 硬件打分 + 社区排行榜
  - **Supply Depot** —— 一键应用目录（PDF 工具、文件浏览器、电子书库、密码管理器……）+ 支持跑自定义容器
  - **自动更新** —— 核心软件、已装应用、离线内容可 opt-in 按自定义计划自动更新
- 安装：Debian 系（推荐 Ubuntu 26.04 LTS，24.04 LTS / Debian 12 亦支持），一条 curl 管道装；高级用户可直接用 docker-compose 模板；Windows 走 WSL2 社区支持路径。
- **硬件要求写得跟同类项目相反**：明确说"很多同类离线生存计算机是为最低配硬件设计的，Project NOMAD 恰恰相反——**我们强烈建议用带 GPU 的强机器**"。裸装（无 AI）整栈 **< 1 GB 内存 / 5 GB 磁盘**；加上 AI 助手后装机量约 **25 GB**（Ollama + 通用模型），并解释原因：**模型需要约等于其下载体积的内存**，有独显走 VRAM、没有就走系统内存——"这是下面数字高得多的最大原因"。推荐配置 32 GB 内存 + RTX 3060 级显卡 + 250 GB SSD。

**值得关注的原因**
- **非 Agent 项目，但是"本地优先 + 自带编排"这条主线的教科书样本**：它不发明组件，而是把 Kiwix/Kolibri/CyberChef/Qdrant/Ollama 这些成熟件用 Docker 编成一个可运维的整体，并自己承担"安装、配置、更新"这三件最难的部分。这与 10-06 mailflare（自带云账号）、10-06 openGym（文件级数据边界）属同一族：**自托管产品的竞争点已经不在功能，在"运维负担谁扛"**。
- **"诚实的容量账本"值得抄**：把"模型需要约等于下载体积的内存"这条容易被忽略的约束写在设备要求里，并解释为什么有 GPU 和无 GPU 的推荐值差这么多。同类项目常把"支持本地大模型"写成一句无成本的卖点。
- 附带的**社区硬件 benchmark 榜**是个有意思的产品设计：把"跑得动什么"变成用户可比较、可贡献的公开数据，与 10-05 llmfit 的"估算值自带输入与验证方法 + 实测 tok/s 提 PR 回填"是同一种做法。

---

### 8. TecharoHQ/anubis —— 反 AI 爬虫的"核弹式"方案，且自己先说了它有多粗暴

**事件**：Go 项目 Anubis 进入语言榜，日 +64，总 23,412，forks 771（**forks/star 比 0.033，属偏低，说明是真部署而非收藏**）。

**核心内容**
- 定位：**Web AI 防火墙工具**，用一道或多道挑战"称量来者的灵魂"（借用埃及称心仪式的典故），保护上游资源不被爬虫机器人淹没。
- 设计目标写得很直白：**保护"小互联网"**——帮它们挡住 AI 公司涌来的无尽请求洪流。因此**尽量轻量，确保每个人都付得起保护自己社区的成本**。
- **自我警告放在正文最显眼处**："Anubis 有点像一个核弹式响应。这会导致你的网站**同时被小型爬虫挡住**，也可能妨碍像 **Internet Archive 这样的'好机器人'**。" 缓解办法是配置 bot policy 定义显式放行（`docs/docs/admin/policies.mdx`），作者说正在整理一套"已知好机器人"的策展清单，以在可发现性与可用性之间折中。
- **明确说了"多数情况你不需要它"**："大多数情况下你不需要这个，用 Cloudflare 保护源站大概就够了。但在你不能或不愿用 Cloudflare 的场景下，Anubis 就是为你准备的。"
- 生态面：官方文档站 anubis.techaro.lol；打包状态通过 repology 徽章展示多发行版覆盖；赞助分 Diamond/Gold 两档。

**值得关注的原因**
- **非 Agent 基础设施，但它回答的是 Agent 生态的另一半问题**：过去几期我们一直在记"Agent 如何访问互联网"（10-05 caveman 的 `caveman browse`、10-06 Agent-Reach 的 17 个平台、本期 apify 的 8000+ Actor）；Anubis 是**内容方的防御侧**——"我如何决定谁可以访问我"。攻防两端在同一天同时出现在榜上，是这一波 Agent 落地进入存量博弈的标志。
- **"先说自己有多粗暴"是本期第二次出现的诚实模式**（另一次是 PentAGI 的 Capability Boundaries）：README 主动列出"会误伤好机器人、可能挡住 Internet Archive、多数情况不如用 Cloudflare"，这直接降低了误用成本，也让项目更容易被正确评估。
- 与 09-25 cilium、10-13 ghostlock-app 一类"确定性工程"项目共享一个特征：**改动面小、行为可预测、文档把不适用场景写在前面**。

---

### 9. ruvnet/ruflo —— Claude Flow 改名 Ruflo，做 Claude Code / Codex 的 meta-harness

**事件**：TypeScript 项目 ruflo 进入语言榜，日 +146，总 74,716，forks 8,892。README 首行即说明**"Claude Flow 现在叫 Ruflo"**。

**核心内容**
- 定位：**给 Claude Code 和 Codex 用的 Agent meta-harness**。README 给出的一句公式是"**Agent = Model + Harness**"——模型负责写，harness 提供工具、记忆、循环、沙箱与控制，让它真的能干成事。Ruflo 就是那层 harness。
- 规模：**100+ 专职 Agent**、协调式 swarms、自学习记忆、**跨机器的联邦通信**（安全地跟别的机器上的 Agent 对话而不泄数据）、企业安全护栏。README 提到"你不需要学 **314 个 MCP 工具**或 **26 个 CLI 命令**"——即这两组数字就是它实际暴露的面。
- 使用路径：Claude Code 内 `/plugin marketplace add ruvnet/ruflo` + 装 `ruflo-core` / `ruflo-console` / `ruflo-mods` 三个插件，然后 `/ruflo`；**要求 Claude Code 2.1.287 或更高**。Codex 或其他 MCP 客户端走 `npx ruflo@latest init wizard`，本地 stdio MCP 配 `npx -y ruflo@latest mcp start`；纯终端可用 `npx ruflo tui`（`--plain` 打印单帧供脚本用），有 Overview / Cost / Swarm / Events / Missions 面板。
- 架构一句话（README 自述为"概念流程，不是实时执行轨迹"，属克制的表述）：User → Ruflo (CLI/MCP) → Router → Swarm → Agents → Memory → LLM providers，**记忆把有效经验反馈回路由**。
- 附带 ruOS Desktop（可经 `https://ruos.cognitum.one/mcp` 接 ChatGPT / Claude）与 `npx ruvector`。
- 安全提示写在前台：**"Mods 以你账号的权限运行；装之前先审代码。"** 另附 14 章的《RuFlo Explained》文档（从基础想法到第一个有用任务，再到记忆、Agent 团队、插件、成本与验证）。
- 命名解释：作者 rUv 说"Ru"是他的名字，"flo"是干到凌晨三点；底层跑 Cognitum.One 的 Rust 引擎、embedding、记忆与插件系统。

**值得关注的原因**
- **本期是"项目改名"这一现象最清晰的一次记录**（另有 OpenCreator 原名 KrillinAI、Scientific Agent Skills 原名 Claude Scientific Skills、Agent Mesh 也刚改过名）。改名本身是信号：**当上游 harness（Claude Code / Codex）成为宿主，第三方 harness 只能靠"能力层"而不是"品牌层"立足**——ruflo 的名字已经完全不提 Claude，但它的入口仍然是 Claude Code 插件市场。
- **"314 个 MCP 工具 / 26 个 CLI 命令"这个量级值得警惕也值得学**：它选择了"全都要"的路线，与 10-13 mattpocock 的"少而精、绝不接管你的流程"、10-13 微软 litebox 的"缩小接口面"正好相反。两种路线的共存说明**harness 层还没有收敛**。
- **`/plugin marketplace add` 成为第三方 harness 的标准分发入口**：本期 ruflo、twostraws、wshobson/agents、AWS toolkit 全部走这条路。Anthropic 的插件市场事实上成了"Agent 能力层"的 App Store，这一点在 claude-plugins-official 的规则设计里也能看到（见速览）。

---

### 10. ggml-org/Llama-Windows —— 官方把本地推理做成系统托盘里的一个图标

**事件**：`ggml-org/Llama-Windows` 首次出现在 C# 语言榜，日 +41，总 **128**（全站最小总星之一，属全新仓库），forks 17。

**核心内容**
- 定位：**Windows 11 托盘应用**，用来在本机跑 llama.cpp 模型。是 **Llama for Mac 的 WinUI 3 移植版**——即 ggml 官方自己出的桌面壳。
- 形态：常驻系统托盘，点击弹出**无边框、Mica 材质**的浮出面板。
- 关键能力：
  - **零配置 llama.cpp** —— 复用你已有的 `llama.exe`，没有就替你下一个
  - **一键模型** —— 从 Hugging Face Hub 浏览并下载推荐模型
  - **模型详情** —— 点开任一模型可挑上下文长度，并**逐选项给出内存估算（从 GGUF header 读取）**，按模型记忆；另有聊天、复制 model ID、生成 curl 请求、跳转 HF 页面
  - **标准存储** —— 模型放在 Hugging Face 缓存目录，与 `llama.cpp` 及其他工具共享
  - **类 Spotlight 全局浮层** —— 任意应用里按 `Alt+Space` 唤起已加载模型的对话窗口；**隐藏而非关闭**，所以再次唤起是瞬时的、会话还在
- 实现：应用管理一个 `llama serve` 进程并通过其 REST API 通信；模型在 `%USERPROFILE%\.cache\huggingface\hub`，设置与日志在 `%LOCALAPPDATA%\Llama`。
- **隐私声明写得很精确**：不发遥测（无事件、无分析、无 install id）；唯一外发的 HTTP 请求（模型下载、版本检查、调用本地 llama-server）只带标准 User-Agent `llama-win/0.12.0 (10.0.26100; x64)`，即应用版本 + Windows 构建号 + 处理器架构；**提示词与推理 100% 留在本地**。
- 构建：需要 .NET 10 SDK（ARM64 或 x64 主机，SDK 可交叉编译两者）；按平台传 `-p:Platform` 与 `-r`；官方构建**关闭 Trim/R2R**，因为应用依赖反射式 JSON 序列化与 COM `dynamic` 互操作，裁剪器会剥掉（README 直接点名 IL2026/IL2072 警告）。

**值得关注的原因**
- **"本地推理"的最后一公里从 CLI 挪到了操作系统界面**。此前这条线的样本都是命令行的（llama.cpp、Ollama、10-05 ds4、10-12 colibri、10-13 ninfer）；本期 ggml 官方直接出一个托盘应用，并把"模型多大、能开多长上下文、占多少内存"做成下载前可读的估算——**这一步把"能不能跑"从试错变成查看**。
- **零遥测 + 精确到 User-Agent 字段的披露**值得抄。本期反例是 10-07 的 ChromeDevTools MCP（三处默认开启遥测需逐项关闭）；Llama-Windows 的写法是"我们只发这些字段，就这么多"——**披露的粒度应该是字段级，而不是"我们重视你的隐私"**。
- 与 10-06 esp32-c3-adblock、10-13 tinyjsapp 一类"极致工程的小东西"共享气质：**总星只有 128，但 README 的信息密度高于绝大多数万星项目**。这类项目在语言榜里才看得到，主榜永远不会给它们位置。

---

## 三、其他趋势速览

**厂商技能/插件市场集中落子（本期最强的一股信号）**
- **anthropics/claude-plugins-official**（Python，+181，总 38,140）—— Anthropic 官方策展的插件目录，分 `/plugins`（Anthropic 自研）与 `/external_plugins`（伙伴与社区）。两条规则值得抄：①**插件 `name` 是不可变 slug**——一旦发布就不能改，改名会让用户端报 `plugin-not-found`；要改 UI 显示就改 `displayName`；确需改名必须在顶层 `renames` map 里登记，插件加载器会在下次同步时**透明地把旧 slug 重写为新 slug**。②**skill-bundle 插件**：当源仓库只有 `SKILL.md` 而没有 `.claude-plugin/plugin.json` 时，市场条目可用 `strict: false` + 显式 `skills` 数组直接声明。顶部警告也照例前置："装之前请确认你信任该插件；Anthropic 不控制插件里包含的 MCP server、文件或其他软件。"
- **aws/agent-toolkit-for-aws**（Python，+16，总 2,878，Apache-2.0，**状态 GA**）—— AWS 官方给编码 Agent 的工具箱。四个插件：`aws-core`（服务选型、CDK/CloudFormation、serverless、容器、存储、可观测、计费、SDK 用法、部署）、`aws-agents`（用 Bedrock 与 AgentCore 在 AWS 上构建 AI Agent）、`aws-data-analytics`（数据湖、分析、ETL，用 S3 Tables + Glue + Athena）、`aws-agents-for-devsecops`（事件调查、代码评审、发布就绪 UAT、漏洞扫描、用 AWS DevOps Agent 与 Security Agent 跑渗透测试）。**分发三条路**：AWS CLI 内 `aws configure agent-toolkit`、Anthropic 官方市场（默认已加）、直接加自家 marketplace。README 还写了 `Plugin not found` 时先 `/plugin marketplace update` 的排错。
- **dotnet/skills**（C#，+13，总 5,640）—— .NET 团队的技能集，**16 个插件**（dotnet / advanced / data / diag / msbuild / nuget / upgrade / maui / ai / template-engine / test / test-migration / aspnetcore / blazor / winforms / dotnet11）。两处独特：①**开了一个 Skill Value 仪表盘**（dotnet.github.io/skills/），按插件、技能、executor 模型、judge 模型列出 **token 用量、耗时、激活率、未通过率**——这是目前见到的第一个"技能价值"的公开量化面板；②明确划清组件边界：skills 与 MCP servers 是 Agent Plugins 1.0 定义的可移植类型，`agents/*.agent.md` 走 GitHub Copilot 自定义 agent 约定（**不会**被装成 Codex 原生 agent），而 Codex 原生 agent 需要 `.codex/agents/*.toml`——**本仓库目前不发这类文件，因为 Codex 插件安装不会把它们放到发现位置**。
- **wshobson/agents**（Python，+118，总 40,799）—— 跨 harness 的组件集合：**94 个插件（92 本地 + 2 外部）/ 202 个 agent / 184 个技能 / 105 个命令**，一套 Markdown 源适配 7 个工具（Claude Code / Codex CLI / Cursor / OpenCode / Antigravity CLI / GitHub Copilot / Pi），并附**能力矩阵**（各 harness 的模型映射、工具权限、hooks、安装差异）。值得记的细节：**Codex 原生安装有 8 KB 预算，超长技能体会被拆成 reference 文件**；`gh skill install` 与 `npx skills` 两条安装器都能**不 clone 仓库**直接从 GitHub 读技能。
- **apify/apify-mcp-server**（TypeScript，+233，总 11,279）—— Apify 官方 MCP，把 **Apify Store 的数千个现成 Actor** 变成 Agent 工具（社交、搜索引擎、地图、电商抓取）。本期两个新动向：①**支持 agentic payments** —— 可从 AGI 买 token 跑任意 Actor，或经**direct x402（仅 Pay Per Event Actor）**或 **Skyfire** 按请求付费；②**移除 legacy SSE transport**，`https://mcp.apify.com/sse` 已下线，统一走 Streamable HTTP。托管版还独有"对结构化 Actor 结果做 output schema 推断"这一能力，本地 stdio 跑没有。

**硬件 / 端侧**
- **78/xiaozhi-esp32**（C++，+164，总 31,144，forks 7,277）—— MCP 语音聊天机器人固件。本期更新：**要求 ESP-IDF v6.0.1 以上（推荐 6.1），5.x 不再支持**；当前构建矩阵 **171 个变体**（ESP32-S31 需 IDF 6.1+）；MQTT 与 BluFi 加密代码迁移到 **PSA Crypto**；音频管线并发、MQTT/UDP 包校验、发布矩阵选择三处加固。能力面：Wi-Fi/有线/ USB RNDIS/ 4G Cat.1 多路联网、ESP-SR 离线唤醒词、WebSocket 与 MQTT+UDP 双传输、Opus 流式、**说话人识别（3D-Speaker）**、**设备侧 MCP**（扬声器/LED/舵机/GPIO）+ **云侧 MCP**（智能家居、PC 桌面操作、知识搜索、邮件）；支持 138 个板型目录。
- **geo-tp/ESP32-Bit-Pirate**（C++，+64，总 6,091）—— 把 ESP32 变成多协议开发/分析工具，致敬 Bus Pirate。支持**通过串口或 Wi-Fi Web CLI** 交互，模式覆盖 HiZ / I2C（扫描、glitch、从机、dump、eeprom）/ SPI / UART / 半双工 UART / 1WIRE / 2WIRE / 3WIRE / DIO / 红外 / USB（HID、flashrom、存储）/ 蓝牙（BLE HID、扫描、伪造、嗅探）/ Wi-Fi 与以太网（嗅探、deauth、nmap、netcat）/ JTAG（SWD、openOCD）/ I2S / CAN / Sub-GHz / RFID / RF24 / FM / CELL（SIM 卡 dump、短信、通话）/ LoRa（含 meshtastic）。有网页刷写器、Web Serial 工具与硬件指南。
- **altic-dev/FluidVoice**（Swift，+40，总 12,150）—— macOS 听写应用，**端侧 STT + 自训 AI 增强**。
- **CoplayDev/unity-mcp**（C#，+43，总 14,963）与 **IvanMurzak/Unity-MCP**（C#，+23，总 4,461）—— Unity 编辑器的 MCP 桥，两条独立实现同日同榜。

**跨平台跑别人平台的东西（本期仍有 3 个）**
- **sp00nznet/xboxrecomp**（C，+15，总 212）—— **把任意 Xbox 游戏二进制变成原生 Windows 可执行文件，"没有模拟、没有解释器"**；同作者 **sp00nznet/ps3recomp**（C，+14，总 435）—— PS3 静态重编译运行时库。与 10-06 AnyPS5、10-13 Madeira / GameNative / winlator / quiver 同族，共同点是**翻译 + 兼容 + 图形三段解耦**。

**其他值得记的新面孔**
- **Fincept-Corporation/FinceptTerminal**（C++，+46，总 32,510，AGPL-3.0）—— C++20 + Qt6 + Python 的金融终端。商业模式写得比多数开源项目清楚：开源仓库保持 AGPL-3.0 免费，**Enterprise 私有版 $15/$30/$45 per user/mo**（Exclusive / Exclusive+ / Exclusive Pro），**Quantcept** 研究台免费档 $0（350 credits，不绑卡）/ Alpha $3 / Apex $8（30 天通行证，**不自动续费**，学生 Apex $5）。
- **krillinai/OpenCreator**（TypeScript，+95，总 13,109，Apache-2.0，**原名 KrillinAI**）—— 面向创作者的 AI 工作台 + Skills。**不重造 Agent 循环，直接把 Codex CLI 当执行引擎**，自己在外面加本地 Runtime、可视工作区与桌面宿主。首次启动会扫描本地 Codex 配置，**主动提出复用已有的 ChatGPT 登录或 API key**。Web 是唯一前端实现，Desktop 加载同一份 Web 构建，只额外加需要操作系统的能力（目录选择、窗口生命周期、托盘、原生通知）。**数据、附件、日志默认全留本地**，带审批与脱敏诊断。有全局/项目/线程三级记忆 + 可复现的 Run 输入快照。
- **lbjlaq/Antigravity-Manager**（Rust，+64，总 32,230）—— 把常见 **Web Session（Google / Anthropic）转成标准 API 接口**的多账号管理与协议代理台，v4.9.6。赞助位几乎全是 API 中转服务商（报价从官方价 2% 到 38% 不等），与 10-05 记录的 router-for-me/CLIProxyAPI 同型。
- **plugin87/ux-ui-agent-skills**（JavaScript，+45，总 1,768）—— 把 Claude 变成资深设计架构师：**DTCG tokens、52 个组件、WCAG 2.2 AA-AAA**。
- **p1neappleXpress/OpenFlux**（Go，+55，总 2,166）—— 网络栈研究工具，可插拔传输的 TCP 隧道。
- **isair/jarvis**（Python，+31，总 2,071）—— 桌面私有本地 AI 助手，语音与文本聊天 + 个人记忆 + 听写。
- **sandeco/reversa**（JavaScript，+11，总 1,750）—— **把遗留系统转换成可执行规格**交给 AI 编码 Agent。
- **wondelai/skills**（Shell，+14，总 2,427）—— 商业/营销/UX/编码框架技能，取自畅销书。
- 主流与大仓库回榜（不展开）：flutter（周 +1,117）、ghidra（日 +1,008 / 月 +11,461）、claude-code（月 +6,685）、openai/codex、rust-lang/rust、microsoft/vscode、react、supabase、tensorflow、kubernetes、golang/go、python/cpython、nvm、ohmyzsh、Homebrew、redis、tauri、tokio、ruff、uv、esbuild、jq、zstd、llama.cpp、ImHex、Apktool、jadx、AltStore、Dopamine、Files、Sonarr、PowerShell、KernelSU、Maestro、ONLYOFFICE、DocuSeal、Mastodon、Rails、Ventoy、karpathy/llm.c、karpathy/nn-zero-to-hero、OpenBMB/MiniCPM、QwenLM/Qwen3-VL、flashinfer、DeepEP、cutlass、BitNet、colmap、ZLUDA、Folia、PaperBoat。

---

## 四、已推送仓库新版本与重大动态（10-13 → 10-15）

> 数据来自各仓库 `releases.atom`，只列 10-13 及之后。

**★ 本期最大动态：morluto/rea 一周涨 214,837 stars，跃居主榜 weekly 第一**
- rea（TypeScript，总 **249,843**，forks **62,736**）：**weekly +214,837 / daily +41,034**，两个数字都远超同期任何项目。对照 10-07 期它的总量还只有 10,401——**8 天涨了约 24 倍**，是本期唯一一个量级跳变。
- 同期发布 **rea-agents v6.5.0**（10-14 12:32）：
  - **JavaScript 源选择**：分析精确指定的应用路径，**不把 import 扩展进选中范围**；未选中的文件保留身份与显式的 unknown 覆盖；摘要投递与源选择解耦（#1944）。
  - **代码分割恢复**：从多个选中输入恢复相关 bundle，保留**逐文件出处（provenance）**与下游跨 chunk import。**同时自曝验证范围**："已记录的 CLI/MCP 覆盖范围是 Linux x64 + Wakaru 1.14.0 + 源码自有的 esbuild/webpack fixture；**其他宿主、其他版本、任意应用等价性仍未验证**"（#1686）。
  - **包导入解析**：用选中的 loader 与包祖先关系解析精确的 import 别名，而不是猜兄弟文件（#1862）。
  - **保留分析视图**：可 opt-in 紧凑的 inventory/WASM、managed 元数据、Android manifest、Dart AOT、Mach-O、EVM 摘要，然后**翻页读取已保留的 Evidence 而无需重跑分析**；分析或清理失败时，已完成的 Evidence 与部分观察仍然可用。

**★ 其余新版本（按重要度）**
| 仓库 | 新版本 | 时间 | 要点 |
|---|---|---|---|
| vectorize-io/hindsight | **v1.0.0** | 10-13 | 记忆层正式 1.0。**破坏性：`refactor(openclaw)!` 移除 agent-sdk 包与 `agent_knowledge_*` 工具**；API 侧"拒绝 tag 作用域调用者访问按整库回答的操作"；**每个集成用各自的 User-Agent 自我标识**；大量修 coding-agents 集成（Claude Code chunk 丢失与时间戳、Cursor Windows hooks、Zed 原生 MCP url、pi 会话 cwd、Codex 启动、Grok Build）；**保留的会话保持完整**（pi 运行、失败操作、退出、btw 会话）；OpenClaw 插件读取结束转录改走 OpenClaw 自己的 reader |
| JuliusBrussee/caveman | **4.0.0 / 4.0.1** | 10-13 | 一次安装命令统一为 `npx @caveman-ai/cli`；新增**经 Caveman Cloud 的 Auto 路由**（在本地 proxy 之上），`caveman-auto` 出现在 Claude Code 与 OpenCode 的模型选择器里、**1M 上下文窗口**；**翻译器覆盖 Messages / Chat Completions / Responses 全部九个方向**（Claude Code 因此能跑在 ChatGPT 计划这类 Responses 宿主上）；**代理在会话暂停期间保持 Anthropic prompt cache 热**（暖机时机来自实测返回时间、最多两个并发、`caveman stats` 列出每次暖机）；**模块索引 `modules.json` 列在二进制发布的签名校验清单里，CLI 拒绝清单未列出的索引**；配置家目录统一为 `~/.caveman/cloud.json`（旧配置一次性迁移、无竞态、遥测 opt-out 一并带过）；登录用共享 device flow 且**拒绝非本机的明文 HTTP Cloud**；目录新增 Sonnet 5.5 / Haiku 5.5 / GPT-6.1 Sol / GPT-6 Luna |
| rtk-ai/rtk | **v1.0.1**（+ dev-1.0.2-rc.548） | 10-14 / 10-15 | 输出侧压缩工具进入 1.0。本版修两处：`rtk gain` 只在命令存在时才建议 `rtk pipeline share`（#4557）；**`llm-proxy start` 与 agent 启动器现在遵守 `RTK_PROXY_BIND`**（#4556） |
| Tencent/WeKnora | **v0.8.3** | 10-14 | **连续 9 期停在 v0.8.2 后终于发新版**。要点：新增**系统管理员模型目录控制台**；**共享空间 Agent 可驱动调用方的本地浏览器**；`feat(lite): install and run skills on the host`（**在宿主机上安装并运行技能**）；文档解析支持 **MinerU 4.0 V1 API**（自托管）且解析超时可配；**检索侧统一 rerank 并暴露诊断**、修召回正确性/分数刻度/成本/Agent 工具；图库新增 schema 驱动的筛选与重做工具栏；**引用文档直接打开到被引段落**；修"知识库上限为 0"、"解析卡在 processing/finalizing"、**合并相邻 assistant 消息时保留 tool_calls（避免孤儿 tool 消息导致整轮 400）**、Feishu Wiki 分页重复 token 死循环、Notion 增量同步在资源发现失败时中止、RSS 拒绝超长响应而非接受截断内容 |
| DietrichGebert/ponytail | **v5.2.0** | 10-13 | **修"档位在上下文压缩后回落到默认"**；**macOS 上 hook 不再丢输出**（改为同步写 hook 输出，避免 `process.exit` 丢掉），**规则集因此保证送达**；Cursor 安装器不再动它不认识的 `hooks.json`、不再误删同名用户 hook；OpenCode 不再卡在 review 且支持 `/ponytail default`；pi 支持 `/ponytail` 参数补全；OMP 新会话从默认档位开始 |
| thedotmack/claude-mem | **v13.39.0**（10-13，另有 v13.38.0/13.37.0 同日） | 10-13 | **Codex 子代理线程在压缩后拿回记忆时间线**：Codex 压缩线程时记忆时间线会掉出历史；根线程已通过 SessionStart(source compact) 拿回，但 **Codex 从不给子代理线程发 SessionStart**，于是压缩过的子代理在没有记忆的情况下继续干活。新增 **PostCompact hook**（按 `session_id` + `agent_id` 标记被压缩的线程）；该线程下次 PostToolUse 照常记录 observation、消费标记、**一次性把时间线作为 additionalContext 返回**；SessionStart 清除标记，因此根线程不会拿到两次 |
| alibaba/open-code-review | **v1.13.0** | 10-13 | **支持通过公开 Responses 用 ChatGPT 计划做评审**（#1622）；**支持 ACP 服务**（#1218）；修：渲染后 prompt 溢出记为失败评审、被删文件可通过 `file_read_diff` 读取、被删文件在自己的路径下列出、OpenCode 输出在 Windows 上的保留；npm 改用 trusted publishing 发布 |
| NVIDIA/OpenShell | **v0.1.4**（10-13）+ v0.1.5-pre.1/2（10-14）+ Dev Build（10-15） | — | v0.1.4 亮点：**snap 默认以用户服务方式运行 gateway**；**新增仅 operator 可读的 provider 凭据检索**（#4357）；**CI 用必需状态检查把合并门控在维护者批准上**（#3176）；`refactor(runtime): confine and reduce unsafe code`；gateway 新增 gRPC server reflection；**providers 支持稳定的凭据占位符**；修"凭据别名在 revision 驱逐后解析失败"。v0.1.5-pre.1 把 **gateway OCSF 事件导出为 OTLP log records**；pre.2 为 **RUSTSEC-2026-0346..0349 升 rustls 到 0.23.46** |
| TencentCloud/Octop | **v1.0.2b8** | 10-14 | 新增**对话 mid-turn steering**、专家记忆的备份/恢复/存储维护、Telegram 可限制允许的用户 ID；新增**语雀（Yuque）网关连接器**；支持 `.wps`/`.doc`（经 firecrawl-anydoc）；修 Windows 记忆备份恢复、微信旧库定时任务与重启后推送、审批放通与 Steer 续跑、历史加载中消息消失、**知识库上限为 0 视为无上限**、本地索引内存与重启边界、技能集缺包、撤销授权未清 API Key、桥接层"把 WebSocket 403 当成路由缺失"、同时登录与附件隧道；升级 octop-harness 1.0.3 / octop-gateway 1.0.2 |
| heygen-com/hyperframes | v0.8.155 → **v0.8.160** | 10-13 → 10-15 | 三天 6 版 |
| paperclipai/paperclip | canary **2026.1015.0-canary.6** | 10-15 | 一日 4 版；含"报告未分类 Codex 轮次为何失败"（#16354）、"在 attention 状态下恢复 GitHub webhook 校验"（#16263） |
| tester-army/e2e | **e2e@0.21.0** / web@0.15.0 / mobile@0.12.1 / smol@0.1.1 / decision@0.2.2 | 10-14 | **`app.command.inheritEnv`** 按名字或尾部 `*` 前缀从宿主传变量（`['DATABASE_URL','STRIPE_*']`），**只在该变量已设置时才复制**；`command.env` 优先于继承值，继承值在带引号的启动失败信息里同样被脱敏；**裸 `*` 与非末尾 `*` 一律 `INVALID_CONFIG`**。新增 `E2E_CACHE_DIR` 与 `e2e run --cache-dir <dir>` 替代 `cache.dir`，让同一项目的 checkout 与 worktree 共享回放缓存，**flag 优先于环境变量** |
| stablyai/orca | **v1.4.226**（+ v1.4.225，10-14） | 10-15 | Jira 接入看板/冲刺/状态视图、保存的筛选、规划列、可复用 prompt 模板、更快的分派、**CLI 侧更安全的 Agent 访问**；文件夹工作区更易找到，新工作区可只跑自己的 setup 脚本；原生 chat 支持内联编辑 diff、长代码行折行、**Mermaid 图缩放**、**显示 Codex 上下文用量**、保持正确的权限模式；**Windows/WSL：可在 WSL 发行版里跑实验性 managed host** |
| longbridge/gpui-kit | **v0.7.3**（**v0.7.2 已 yank**） | 10-13 | v0.7.3 含 v0.7.2 全部改动并把 GPUI 移到 gpui-pre 0.3.9 快照；**直接从 v0.7.1/v0.7.2 升到 v0.7.3**。新增只读 Diff 查看器（含 Git history 示例，支持 Unified/Split、语法高亮、折叠、变更导航、行内词/字符强调、软换行、注释、双向或 diff3 冲突展示）、可选 GPUI Fast 后端、可配置对话框入场；刷新 TextView 排版、改进文本选择、Editor 补全、表格、菜单、tooltip 与无障碍；**停掉若干逐帧状态写入，长滚动视图不再重建**。另有一条工程细节：网站的 Shell 页面改为跟随它发布的二进制（`shell-<tag>` 标签），因此**重建二进制后文档不会与下载物不一致** |
| xtool-org/xtool | **v1.22.2** | 10-14 | **破坏性：更新了 Apple ID 登录所用的设备指纹（现在向 Apple 呈现为 Pixel 7 设备），修复认证问题——使用 Apple ID 认证的用户升级后需重新登录**；packer 用 `XcodeProjectFormat` 生成 Xcode 工程；自定义 SwiftVersion 解析器；修 login 使用不匹配的 client-info；加入更新的 Apple Root CA |
| topoteretes/cognee | **v1.6.4** | 10-13 | 向量存储与 DB 可靠性：LanceDB 与 pgvector 适配器**检索时不再返回原始向量列**（降内存、防失败）；Turso 打开失败统一抛 `OperationalError`；**移除 LanceDB 后台剪枝任务**（此前会干扰检索）；补测试修 harness |
| trycua/cua | **Cua Spaces v0.9.1**（10-15）+ v0.9.0（10-14）+ nightly-lume | — | Spaces 从 0.8.x 跨到 0.9.x |
| backnotprop/plannotator | v0.28.18 / .19 / **.20** | 10-13 → 10-14 | **Inbox 成为连接各 agent 的入口**（agent 被明确告知何时该用 Inbox）、code review 支持渲染 Markdown、Inbox 设置分区、iPad 与窄窗口适配、手机端 Inbox、"新问题门铃"、标记已读、按文件步进线程、**提问会话结束后仍可回复**、长线程只折叠出新增部分、"跳过了 N 个问题"的回复 |
| addyosmani/agent-skills | **0.6.13** | 10-13 | 修三个"照抄就跑不起来"的代码示例（错误边界每次渲染都抛、调用了未定义的 refetch、zod 标题校验接受了纯空格标题）；修两个 simplify-ignore bug（可能丢受保护代码 / 让已回滚的改动复活）；**test-driven-development 现在能在"代码已在 prompt 里"时触发**（"给这个函数加单测"与"贴一段没提测试的 bug"从 0/6 提升到 6/6，无新增误触发）；给 README 列出哪些宿主设了书面门槛 |
| rohitg00/ai-engineering-from-scratch | **Edition 2026.10.3** | 10-15 | 课程从 523 课扩到 **542 课**（20 阶段）；**新增逆向工程赛道**（Phase 13 共 14 课，从自己构建的编译产物字节一路到有证据支撑的伪代码）；讲 ELF/Mach-O/PE 程序解剖、反汇编与控制流图、lift 到 IR 与 SSA、System V / Windows x64 / AArch64 调用约定、编译器惯用法、链接与 stripped 二进制、数据与类型恢复、动态分析、字节码格式（Python/JVM/.NET/WebAssembly）、二进制 diff 与符号执行，以及**给 AI 辅助分析用的 ground-truth 记分卡**；每课在自己的 fixture 上跑真工具（llvm-objdump、Ghidra、radare2、rizin、angr、lldb、LIEF、javap、wasm-objdump）；新增第三本手册与 LaTeX 数学 |
| t8y2/dbx | v0.6.43 / **v0.6.44** | 10-14 | 连续两版 |

**长期无新版**：artcraft v0.41.0（09-26）、cathrynlavery/diagram-design（**releases.atom 0 entry，从未发过 release**）、earthtojake/text-to-cad（最后条目早于 10-13）、debpalash/VoiceStudio（早于 10-13）、ifixai-ai/iFixAi（早于 10-13）、mksglu/context-mode（早于 10-13）、mvschwarz/openrig（早于 10-13，**连续第 2 期无新版**）、Gentleman-Programming/engram、affaan-m/ECC、storytold/artcraft。

---

## 五、当日主线判断

1. **技能/插件分发的四层产业链在同一天全部上榜**。分发工具（**vercel-labs/skills**，79 个 agent）→ 领域内容（**K-Dense 的 177 个科研技能 + 论文**、**twostraws 的 SwiftUI Pro 系列**）→ 厂商市场（**anthropics/claude-plugins-official**、**aws/agent-toolkit-for-aws** GA、**dotnet/skills**）→ 托管平台（**apify-mcp-server** 开始接 agentic payments）。**分发层由平台方持有、内容层由领域权威持有、市场层由云厂商持有**——三层各归其位，这是本期最清晰的产业结构信号。
2. **"Agent 之间的网络层"首次被大厂做成独立开源项目**（**google/agentmesh**）。此前同类都在单机或单集群内；本期补上跨机器、跨网络、跨组织的发现与授权。两处设计判断可直接复用：**授权绑服务名不绑地址**、**控制平面签发的凭证必须能离线验证**。
3. **官方厂商开始给"技能价值"建量化面板**（**dotnet/skills 的 Skill Value 仪表盘**：按插件/技能/executor 模型/judge 模型列 token 用量、耗时、激活率、未通过率）。这是接续 09-30 NVIDIA SkillSpector（26.1% 技能含漏洞）之后，技能生态从"安全基线"走到"价值基线"的一步。
4. **"配置被接受却从未生效"成为被正面解决的一类 bug**（**Soup v0.76.0 在加载期直接拒绝从未生效的设置，并在报错里点名字段与改法**）。这与此前记录的四处静默失效（ponytail 的 plugin.json、claude-mem 的异步 hook、engram 的能力协商、openrig 的 daemon 重启）合起来，构成 2026 年最一致的一条教训：**控制平面失效常常无声，所以必须把"没生效"变成硬错误**。本期 ponytail v5.2.0 修的"档位在上下文压缩后回落"、claude-mem 修的"子代理线程压缩后丢记忆"、gpui-kit 的"重建二进制后文档与下载物不一致"，都是同一个病的不同部位。
5. **诚实披露升级到"主动拆解自家最漂亮的数字"**（**Soup 自己说明 1.74× 的增益来自时钟而非加速，并说连折算比例也不是同类比较**；**PentAGI 把能力边界单列一节**说"不是 BAS、JSON 导出不算支持格式"；**Anubis 在正文里说自己像核弹、会误伤 Internet Archive、多数情况不如 Cloudflare**）。这比前几期的"修正数值"更进一步——**不再只是承认弱点，而是主动否定读者可能产生的夸大解读**。
6. **垂类 Agent 的免责写法已经细化到技能颗粒度**（K-Dense 的临床/动物实验/法规技能各自写明"是辅助不是决策规则""供合格评审而非认证"）。配合 09-23 anthropics/financial-services 的"人工签核前置"，**"我做到哪一步、由谁签字"正在成为垂类 Agent 的入场券**。
7. **本地推理的最后一公里从 CLI 挪到操作系统界面**（**ggml-org/Llama-Windows** 托盘应用 + `Alt+Space` 全局浮层 + 下载前给内存估算）。同一天，端侧这条线还有 78/xiaozhi-esp32（IDF 6.0.1+，171 个构建变体，设备侧 + 云侧双 MCP）与 FluidVoice（macOS 端侧 STT）。
8. **非 Agent 基础设施转向"我如何决定谁可以访问我"**（**TecharoHQ/anubis** 的 Web AI 防火墙）。过去几期我们记的都是"Agent 如何访问互联网"；本期防御侧首次以足够体量上榜。同一逻辑下，**Project NOMAD 把"离线优先"做成一套可运维的 Docker 编排**，回答的是"断网时我还有什么"。
9. **改名/品牌迁移成为高频现象**：Claude Flow → **Ruflo**、KrillinAI → **OpenCreator**、Claude Scientific Skills → **Scientific Agent Skills**、Agent Mesh 刚改名。共同动机是**摆脱上游宿主品牌、覆盖更多宿主**——当 Claude Code / Codex 成为宿主，能力层项目只能靠能力而不靠品牌立足。而它们的分发入口仍然高度集中在 Anthropic 的插件市场（本期 ruflo、twostraws、wshobson、AWS toolkit 全部走 `/plugin marketplace add`）。
10. **两条互斥的 harness 哲学同日同榜**：ruflo 的"全都要"（314 个 MCP 工具 / 26 个命令 / 100+ Agent）vs mattpocock/skills 的"少而精、绝不接管你的流程"（上期记录）。**harness 层远未收敛**。
11. **非 Agent 项目 3/10**（project-nomad / anubis / Llama-Windows），为本期偏低的水平，但**"具体问题 + 极致工程 + 高文档密度"的样本比例继续上升**（Llama-Windows 128 stars 但 README 信息密度高于多数万星项目；ESP32-Bit-Pirate 24 种协议；xboxrecomp 212 stars 做 Xbox 二进制静态重编译）。
12. **语言榜仍是新面孔的唯一稳定来源**：主榜 46 条仅 3 条新（其中 1 条还是 weekly 榜的），**7/10 来自语言维度榜**。本期新面孔在 `csharp`（Llama-Windows、dotnet/skills、unity-mcp）、`go`（agentmesh、anubis、pentagi）、`c++`（ESP32-Bit-Pirate、FinceptTerminal）三个语言里最集中。

---

## 六、方法论与坑（本期新增）

- **数据源与抓取**：主榜 3 个 + 语言榜 18 个 = **21 个榜并发抓取，0 次重试一次全过**（对比 10-09 的 21 榜大面积 504）→ 504 确认是间歇性问题，**带重试的 curl 落盘 + 本地解析必须常备**，但不必因噎废食。去重口径：305 行 → 282 个仓库。
- **`fetch_trending.py` 的 `merge()` 会跨榜取 max 增幅，这在跨周期时会误导**：本期首版合并后 rea 显示 "+214,837"，实际那是 **weekly** 增幅，它当天 daily 只有 +41,034。**报告里必须逐条标注来源榜与周期，不能把合并后的单一数字当"当日增幅"用**。判断某个仓库的今日表现时，要回到对应 board 的原始 HTML 单独取数。
- **解析器沿用已固化的两处修正**：①仓库名用 `href="/(owner)/(repo)"[^>]*data-view-component`（`data-hydro-click` 前置）；②**总 star 数在 `</svg>` 之后**（`stargazers"[^>]*>.*?</svg>\s*([\d,]+)`，需 DOTALL）。本期 21 榜全部解析成功、无 total=0。
- **`releases.atom` 取正文的有效姿势**：`curl` 落盘 → 按 `<entry>` 块正则解析 → 分别取 `<title>` / `<updated>` / `<content type="html">` → `html.unescape` + `re.sub(r'<[^>]+>','')`。**注意 `<updated>` 在 `<title>` 之前**（顺序与直觉相反），按 `<entry>` 块解析才不会错位。本期 31 个仓库的 atom 全部抓取成功，WeKnora / hindsight / rtk / caveman / ponytail / rea / OpenShell / Octop / claude-mem / open-code-review 的正文均完整取到。
- **README 一律三支兜底**（`HEAD` → `main` → `master`）+ 落盘后 `sed -e 's/<[^>]*>//g'` + `head -N` 定点读，**不整篇读**（pentagi 254 KB / wondelai 135 KB / xboxrecomp 107 KB / scientific-agent-skills 84 KB）。本期 27 个 README 全部 HEAD 分支一次成功。
- **GitHub REST API 全程未使用**（延续 10-01 起的做法，避免 60 次/小时的未认证配额）。
- **本次未使用 `--lang`**：`fetch_trending.py` 不支持，语言榜统一用内联 Python `importlib` 加载脚本复用 `parse_board(html, 'daily')`，返回字典键为 `name` / `lang` / `desc` / `total` / `gain` / `forks` / `board`。
