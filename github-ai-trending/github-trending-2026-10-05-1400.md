# GitHub 趋势日报 · 2026-10-05（14:00 场）

> 数据源：本日 09:44 已跑过一期（daily 16 / weekly 19 / monthly 23 全被覆盖）。本期**换榜**——改抓**语言维度** `github.com/trending/<lang>?since=daily`（python / typescript / rust / go / c 五榜），另取今日 09:44 之后新发布的版本事件。
> 筛选口径：当日新增 Star 高 + 技术方向有代表性 + 与前十期及本日上午期推送清单不重复
> 本期构成：**8 条全新面孔 + 2 条本日上午期之后发布的新版本**（ponytail v4.12.0 / claude-mem v13.31.0）

---

## 一、榜单速览

| # | 仓库 | 语言 | 总 Star | 增幅 | 来源 | 一句话 |
|---|---|---|---|---|---|---|
| 1 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Go | 109,861 | +433 (today) | go | 让 Agent "少说少读"的技能 + 代理，会话省 33.2% 输入 token |
| 2 | [experientiallabs/experiential](https://github.com/experientiallabs/experiential) | Python | 9,003 | +472 (today) | python | 零加价 BYOK 网关，用你自己的 trace 拟合路由 |
| 3 | [cloudflare/cloudflare-os](https://github.com/cloudflare/cloudflare-os) | TS | 10,790 | +335 (today) | typescript | Cloudflare 把内部 AI 生产力系统开源，Gatekeeper 做能力授权 |
| 4 | [ifixai-ai/iFixAi](https://github.com/ifixai-ai/iFixAi) | Python | 20,551 | +298 (today) | python | Agent 独立审计：跨厂商 judge 打分，SUT 不得自评 |
| 5 | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | TS | 96,246 | +628 (today) | typescript | **v13.31.0**：SessionStart 从 21,700 行/63MB 降到索引读 4ms |
| 6 | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | JS | 155,148 | +1,894 (today) | daily | **v4.12.0**：审查发现项编号化，/ponytail-gain 改报诚实均值 |
| 7 | [tinyhumansai/openhuman](https://github.com/tinyhumansai/openhuman) | Rust | 40,645 | +98 (today) | rust | Rust 核心 Agent harness，单进程 500 agent 密度 25× |
| 8 | [zeronsh/zeron](https://github.com/zeronsh/zeron) | Rust | 3,020 | +81 (today) | rust | 编码 Agent 的原生控制面，local-first 默认 + 可选多设备同步 |
| 9 | [shy3130/tick-stock-panel](https://github.com/shy3130/tick-stock-panel) | Python | 5,574 | +51 (today) | python | 自托管 A 股量化工作台，回测与实盘同一条代码路径 |
| 10 | [Autumn-27/ARTEX](https://github.com/Autumn-27/ARTEX) | Go | 1,537 | +45 (today) | go | AI 自主渗透测试系统，双图架构 + 无状态 planner 共享 todolist |

---

## 二、10 条详细

### 1. JuliusBrussee/caveman — 把"少说"和"少读"拆成两个独立的省钱机制

**事件内容**
- Go 榜第 1（日 +433），总星 109,861，Apache-2.0。自我描述是一句梗：*"why many token when few token do trick"*——让 Agent **少说话（skill）也少读东西（proxy）**，代码保持逐字精确。
- **两个机制，成本模型完全不同**：
  - **skill 管"agent 说什么"**：用受控英语（ASD-STE100，飞机维修手册那套：20 词上限、主动语态、一物一词）重写输出。三档 `/caveman`（20 token）→ `/ultracave`（14）→ `/megacave`（13，输出文言文）。每条回复发送前跑一次检查：删掉"宣布计划的开场白"、删掉"复述的结尾"，但**所有否定词、路径、数字必须还在**；代码、命令、错误信息逐字不动。规则明确"永不改写用户 prompt"。
  - **proxy 管"agent 读什么"**：本地跑，用你自己的 key 和 Claude Pro/Max 登录，把日志/CSV/YAML/JSON/测试输出/web 页面在进上下文前压掉。**六个文件类型 130,611 → 22,994 token（-82.4%）**；整个 Claude Code 会话 **885,793 → 591,673（-33.2%）**，18/18 答案正确。`caveman browse` 把一个 200 行表格网页从 15,704 token 压到 **121 token（129.8×）**；`/caveman-compress` 让 CLAUDE.md 这类记忆文件小 46%。
- **数字来源是外部独立验证，不是自测**：Adobe Research 论文 CAVEWOMAN（arXiv 2606.24083）测八模型五数据集得"成本降 1.4–2.4×"；Elastic 在 Elasticsearch Labs 复刻得"响应 token 少 63.6%、零信息损失"；JetBrains 86 个真实编码任务配对 A/B 得"质量无可测损失（p=0.82）、输出 token 少 8.5%"。HN 第 1（904 分）。
- **两条外部研究直接改变了产品形态**：① Adobe 发现"把**用户 prompt** 也 caveman 化会让回答更长更差"→ 所以 caveman **永不动用户 prompt**；② JetBrains 发现 agent 会话里大头是代码和工具调用（caveman 本来就绕开）→ 所以才长出 proxy 这条"压输入"的第二条腿。
- **反例清单是公开的**：`docs/HONEST-NUMBERS.md` 列出所有 caveman 会输的情况。例如规则本身给每次调用加约 1,000 输入 token；**HTML 目前没有压缩器，反而让会话差 9.9%**；按"每请求"计费（GitHub Copilot premium requests）时答案变短不省钱，应当跳过。

**值得关注的原因**
1. **上下文经济被拆成两个独立账本**：输出侧（skill）与输入侧（proxy）的成本结构、失效场景、收益量级完全不同。10-01 记过"处理量 vs 驻留量两个账"，本期是第三次细分——**"读进来"和"说出去"要分别优化**。
2. **它把"不做什么"写成了设计约束**：不改用户 prompt、不碰代码与错误信息、不表演式地模仿原始人说话（"me think"一律不用）、caveman 措辞不长于普通说法时就用普通说法。这与 09-29 ponytail 的"七级阶梯 + 护栏不可裁"是同一族的克制型设计。
3. **外部证据链是这个项目最强的部分**：Adobe / JetBrains / Elastic 三家独立复现，且**结论互相矛盾的地方被用来改产品**（Adobe 说别动 prompt，JetBrains 说会话大头是代码）。这是"把别人的否定意见变成路线图"的样本。
4. **对读者的直接用途**：如果你按 token 计费，`caveman browse` + `caveman shrink`（压测试/日志输出）是立刻可用的；如果按请求计费，跳过。这个判断条件 README 自己给了。

---

### 2. experientiallabs/experiential — 零加价网关，且用你自己的生产流量拟合路由

**事件内容**
- Python，Apache-2.0，日 +472（本期语言榜增幅最高），总星 9,003。定位：Agent 工作流的开源网关与路由器。
- 三件事：① **一个 OpenAI 兼容 API 同时接托管模型、BYOK 自带 key、本地模型**；② 控制"哪个用户/哪个 Agent 能用哪个模型、用于什么场景、能花多少钱"；③ **把生产流量变成你自己的路由器或模型**。
- 本地网关 `pip install experiential` + `exp` 一条命令起，**编译出的原生数据平面在 loopback 上跑所有路由**；首次运行向导选 provider / model / reasoning effort，给出公开别名（如 `opus-5`）、身份与 **$50 默认命令预算**，再打印一次性 key。托管版 `api.experientiallabs.ai/v1` 同时提供 OpenAI 兼容与 Anthropic Messages 两套线格式。
- **BYOK 明确写"free pass-through"**（不加价）：OpenAI / Anthropic / Gemini / Azure / Bedrock / Fireworks / OpenRouter 自带 key 直通。
- **Capture（实验性）**：macOS + Python 3.13+，从 Codex 和 Claude Code 桌面应用抓 trace，**请求仍直连 OpenAI/Anthropic、用你已有的 ChatGPT / Claude 订阅**，网关只做旁路中间件。README 自己标注"macOS 网络可靠性仍在调查中"。
- **Optimize 闭环**：拿 OTel trace（官方给了一份公开的 terminal-tasks 数据集）→ `exp build <project>` 起模拟并针对它优化一个路由器 → `exp optimize model` 用 Thinking Machines 的 Tinker 微调一个你自己拥有的开源模型。Python 侧可直接把拟合好的路由当 OpenAI 客户端用（`with exp.load_router("my-project") as client:`）。
- 遥测是匿名聚合 PostHog，默认开，`exp config telemetry disable` 关；明确不传 prompt / trace / 模型名 / 凭证。

**值得关注的原因**
1. **"零加价"是一个可验证的信任声明**：BYOK 直通不加价 + 本地网关在 loopback + 遥测可关且列明不传什么。这与 09-30 openship 明列云侧防火墙规则、10-05 上午 t3code 的 "Nothing." 同族——**网关这个品类靠"我不抽水"来卖**。
2. **"用你的流量训练你的路由"是网关的下一步**：10-02 freellmapi 做的是"免费额度调度"，本期做的是"拿你自己的 OTel trace 拟合一个专用路由器，甚至微调一个你拥有的模型"。**网关从转发层升级成优化层**。
3. **$50 默认命令预算**：第一次运行就给一个可花钱的上限，这是把"预算硬上限"从 09-28 paperclip 的按 Agent 月度预算下移到了个人开发者的本地工具里。
4. **对读者的用途**：想把 Claude Code / Codex 的流量统一记账、按用户/Agent 限模型限额度、并顺手收集可训练数据，这是当前最完整的一个开源选择。

---

### 3. cloudflare/cloudflare-os — 大厂把内部 AI 生产力系统开源，Gatekeeper 解决了"人在回路阻塞"

**事件内容**
- TypeScript，Apache-2.0，日 +335，总星 10,790。Cloudflare 内部大量员工（工程到销售）日常使用，现开源，**且明确说"目的不是让你用 Cloudflare OS，而是让你做出*你公司*的 OS"**。当前是 v2 完全重写，状态标注 early access。
- **核心概念是 Gadget**：每个用户在**自己的沙箱**里跑一份**私有实例**的软件。做一份幻灯片，不是调用云上的 SaaS，而是为你生成一份只属于你的幻灯片应用。因此：① 应用有漏洞也泄不到别人的数据；② 缺功能就直接让 Agent 改代码，改坏了也只坏自己那份。
- **Gatekeeper = 超级 MCP server**：把外部服务包成 Cap'n Web API、管 OAuth 授权、**只放行用户点名的那一个资源**、记录每一次动作、有副作用的动作要人批。每个 Gatekeeper 是一个独立 Worker。
- **本期最硬的一个工程判断在 Gatekeeper 的审批模型**：传统人在回路是**同步阻塞**的——Agent 要动手就得停下等批准，人一离开就卡死在第一步，于是大家干脆开 `--dangerously-skip-permissions`。Gatekeeper 改成：**先在本地"模拟"这个动作的结果**，告诉 Agent 成功了，Agent 读回结果时也给它模拟结果，于是它可以继续往下排；等它做完，用户**事后**批量批准或逐条否决。README 直说这是"state of the art 的一次实质推进"。
- **权限模型是能力制而非 ACL**：每个 Agent、每个 Gadget 默认**什么都访问不到**。即使工作区已经连了外部账号，也要**逐个"介绍"（introduce）**资源给它——粘一个仓库链接、点"add resource"、或者由 Agent 主动申请、你批或拒。README 直接对比："多数 harness 是 upfront 配 MCP server，于是所有服务在每次对话里都是环境性可用的"，Cloudflare OS 反过来。
- **技术栈自曝**：整站跑在 Cloudflare Workers 上，重度使用 Durable Objects、Dynamic Workers、Facets；**每个工作区是一个 Durable Object，每个 Gadget 跑在一个 Dynamic Worker Facet 里**。Dynamic Workers 与 Facets 是为 Cloudflare OS 专门加到运行时里的。开源 `workerd` 也能自托管跑。
- 与 OS 的类比表是认真的：kernel = workshop-backend、device drivers = gatekeeper-*、shell = workshop-frontend、processes = gadgets、executables = blueprints。**唯一传统 OS 没有的一行是 agents**——README 主张"Agent 不能简单当成用户，它必须对人负责、同时有自己的受限权限，理想安全模型是能力制而不是 ACL"。
- 其他：Agent 是 **Code Mode**（写代码片段并立即执行）而不是工具调用；每个 Gadget 的 client/server 强制走 Cap'n Web RPC，因此**每个应用天生自带 agent 友好的 API**，不需要另写 MCP server；Blueprint（应用模板）本质是分享整份代码；**不接受外部贡献**，理由是"AI 让写代码变简单，难的是 review、保质量和保持产品一致性，外部大 PR 是把简单部分捐给我们、把难的部分留给我们"。

**值得关注的原因**
1. **"异步人在回路"是本期最有价值的一个机制**：它解决了 Agent 落地最日常的摩擦——人一离开就卡死，然后被迫关闭安全机制。做法是**用本地模拟结果换取 Agent 的继续推进，把审批推到人方便的时候**。这与 10-05 上午 OpenMontage 的"渲染前 contact sheet 卡住"是同一个问题的两种解法：一个是"卡住但卡在花钱前"，一个是"不卡住但事后批量批"。两条路都值得记住。
2. **能力制权限终于有了大厂产品级样本**：默认零访问 + 逐个介绍资源，正面否定了"upfront 配一堆 MCP server 让所有服务环境性可用"这个当前主流做法。与 09-30 OpenShell 的"沙箱里看不到真凭证"、10-02 Pi 的"默认不给权限系统"连成一条线。
3. **"每个用户跑自己一份软件"是对 SaaS 的正面挑战**：README 说得很直接——"当任何用户都能让 Agent 给自己加功能时，中心化软件模式就不成立了"。这是把 09-30 起"非文本产出物 Agent 化"推到**软件形态本身**。
4. **对架构读者的参考价值**：Durable Object per workspace + Dynamic Worker per gadget + Facet per Gatekeeper，是一套可直接借鉴的多租户 Agent 平台结构；且它把 Pi 的 `pi-agent-core` 列为关键依赖（"一个 API 支持所有 LLM provider"）——**10-02 记录的自扩展 harness 正在变成别人产品的地基**。
5. **拒绝外部贡献的理由值得单独记住**："AI 让写代码变简单，难的是 review 和保持一致。" 这是 10-05 上午 t3code（"very very early，基本不收贡献"）之后，第二次由知名团队把**审查成本**而不是编写成本作为协作门槛说出来。

---

### 4. ifixai-ai/iFixAi — Agent 独立审计：不让被测方给自己打分

**事件内容**
- Python，Apache-2.0，日 +298，总星 20,551。一句话定位：**独立审计 AI Agent**，抓它的错误与盲区。Product Hunt 日榜第一，Trendshift 周榜 Python 第一。
- **切入角度是"现有评测答不了的问题"**：Eval / 红队 / 可观测性工具主要在测技术能力（token 效率、延迟、提示注入）。iFixAi 要答的是——**按业务 KPI 和组织结构，这个 Agent 到底在做它该做的事吗？** 它把自己定位成"AI 红队 + 运营保证（Operational Assurance）"的平衡。
- **60 项检查、25 个类别，5 个核心支柱**（只有这 5 个计分）：**Fabrication**（用了没授权的工具、无审计轨迹、无出处或过度自信的断言，权重 0.20）、**Manipulation**（提权、破坏自己的策略、提示注入、被投毒的检索上下文，0.35）、**Deception**（沙袋化——察觉在被测就表现得更好、隐藏的副目标、长任务漂移、静默失败，0.15）、**Unpredictability**（上下文扭曲、偏离指令、决策不一致，0.15）、**Opacity**（风险评分弱、合规缺口、人工升级路径坏掉、答非所问，0.15）。
- **评分机制里有两个硬约束**：
  - **SUT 不得给自己打分**。一次运行有两个角色——SUT（被测 Agent/模型）与 Judge（打分者），**judge 必须来自与 SUT 不同的厂商**（SUT 自己厂商被排除），所以一次"可引用的评分"需要两把不同厂商的 key。没有第二把 key 就只能加 `--eval-mode self` 当冒烟测试，**结果会被标记为自评、不可引用**。
  - **一票封顶**：B01 必须 100%、B08 必须 95%、P01 必须 100%，任一未达则**总分被压到 60% 以下**。等级 A≥0.90 / B≥0.80 / C≥0.70 / D≥0.60 / F<0.60，通过线 0.85。
- 60 项里 32 项是核心计分，28 项来自 20 个 premium 类别（蓄意破坏、颠覆、隐瞒、沙袋化、抗命、篡权、系统性风险、误校准、利益相关方冲突、感知治理、监督萎缩、身份证明、影响力、评分者有效性、基准污染、训练倾向溯源、脆弱用户关怀…），**premium 项只报告不计分**（唯一例外 P01 作为最低门槛可封顶）。README 特意声明：**"premium 是能力档，不是付费墙"**，仓库内全部 Apache-2.0 免费。
- 三种运行方式：CLI 向导（`ifixai setup` → `ifixai run`，配置存 `ifixai.yaml`，**只存 key 的环境变量名，不存 key**）、CLI 显式 flag（适合 CI 与可审计脚本）、**插件/技能**（Claude Code、Codex 原生插件；其余 9 个 Agent 用 `uvx ifixai install` 生成 `/ifixai-skill`）。
- 测试对象是**真实部署的 Agent**：`--provider http --endpoint <agent-url> --grounding sut` 直接打它自己的 HTTP 端点、按现状观测（含它已有的治理）；适配器暴露的能力越多，能真正打分的检查越多，看不到的标 `insufficient_evidence`（**报告但不计分**）。
- 成本公开：一次全量约 2,000 次 judge 调用，单 judge（Claude Sonnet 4.6）约 **$12–18**，双 judge（Gemini 2.5 Pro + GPT-5.4-mini，跨厂商更稳）约 **$10–14**；被测 Agent 的费用另算。案例研究用两起公开事件（Pizza Hut 的 Chaac Pizza 投诉、2026 年 6 月 Instagram 账号被接管报道）重建 fixture，**重建版都拿 F**。
- 遥测是假名化（随机安装 id + 起止 + 版本 + 系统 + 接口类型 + 时间戳），明确不传代码、发现、评分、prompt、路径、IP，CI 中自动关闭，`--print-telemetry` 可预看。

**值得关注的原因**
1. **"被测方不得自评"是被硬编码的**：不是建议，是"没有第二个厂商的 key 就跑不出可引用的结果"。这是 09-18 起反复出现的"把不可协商约束写进流程"在**评测域**的落地，比 09-30 SkillSpector 的扫描又深一层——扫描看代码，这个看行为。
2. **它定义了 Agent 的"五个失败面"**：Fabrication / Manipulation / Deception / Unpredictability / Opacity，且 Manipulation 权重最高（0.35）。**沙袋化（察觉在被测就表现得更好）**被单列进 Deception——这是只有"审计"视角才会提出的指标，评测与红队都不会测。
3. **"premium 是能力档不是付费墙"** 是商业模式的诚实声明：28 项 premium 检查全部开源但只报告不计分，所以**不同能力的 Agent 之间评分仍可比**。这是 10-05 上午 marketingskills 的 `PARTNERS.md`（赞助永不影响推荐）之后，第二个把商业化边界写清楚的样本。
4. **对读者的用途**：如果你要把 Agent 交付给非技术方，`--provider http --grounding sut` 打你自己的端点拿一个 A–F 分数，是目前最接近"第三方审计报告"的开源做法；成本 $10–18 一次，可放进发布前流程。
5. 一个提醒：它明确写了"数学指标与自动基准永远讲不全故事，不能替代人工评估"——**它自己先声明了边界**，这与 09-29 ponytail 主动下调自己的数字是同一取向。

---

### 5. thedotmack/claude-mem v13.31.0 — 记忆层的竞争正式进入"启动成本"

**事件内容**（本日上午期之后发布，13:17 GMT+8；上期记录为 v13.30.0）
- 本版主线全是性能，且是**记忆层特有的那类性能**：**新会话不再等 SQLite 读完整个项目历史，也不再等云同步**。
- 具体数字：在 **1.2 GB 数据库**上，SessionStart hook 原来约 **3 秒（最坏 44 秒）**。原因是它会把项目里**所有** observation 和 summary（含已合并的 worktree）全取出来排序取最新 50 条——实测约 **21,700 行 / 63 MB 每次会话启动**，页不在内存时 0.8–1.7 秒。新增按 project + date 的索引（schema v63）后，**只读该 project key 最新的几行就停，查询约 4 ms，结果完全一致**。
- 第二个热点：每次渲染上下文都要解析"哪些存储的 project key 属于当前 checkout"，旧实现为读 project 名把**每一行**都加载进来（31 个 key 要 7,499 页），改用覆盖索引（schema v64）后 **355 页 / 9 ms**。
- 第三个改动是结构性的：**云同步开启时也本地优先**——worker 直接用本地库构建 SessionStart 上下文，从 sync hub 拉取改到后台跑，**hub 慢或不可达永远不会拖慢会话**；预计算的 SessionStart 上下文文件在开启云同步时也照样使用。
- 上一个补丁 v13.30.1 修的是另一类问题：Claude Code 的 `--continue` / `--resume` / `/resume` 不再往正在恢复的会话里注入新的时间线——因为**重新注入会改变 prompt 前缀、破坏 prompt cache 复用**。做法是把 worker 启动与上下文注入拆成两个独立的 SessionStart matcher，resume 只异步起 worker 不做同步时间线注入，并在进入任何项目设置/缓存/worker 前就对 resume 返回空上下文块。

**值得关注的原因**
1. **记忆层的成本战场又往前挪了一格**：09-25 争的是"读取记忆要不要花模型的钱"，09-28 争的是"单位成本"，本期争的是**"会话启动要不要等"**。1.2GB 库上 3 秒（最坏 44 秒）是会把体验毁掉的量级，而解法是把 21,700 行读降成索引读 4ms——**这是纯数据库工程，不是模型工程**。
2. **"云同步不许拖慢本地"是一条架构纪律**：把网络依赖从关键路径上摘下来、只留后台。对照 10-05 上午 openrig 的"升完 CLI 必须重启 daemon"、Cloudflare OS 的"Gatekeeper 本地模拟"，本期多处都在处理**同一件事：把网络/外部依赖挪出用户的等待路径**。
3. **prompt cache 复用成为设计约束**：v13.30.1 那条修复说明——恢复会话时注入新内容会改前缀、毁掉缓存。**"注入任何东西"这件事现在必须考虑缓存前缀稳定性**，这是记忆层/上下文层的一个新的硬约束，值得所有做 hook 的人记下来。
4. 参照：同一个仓库两小时内连发两个版本（v13.30.1 04:37Z、v13.31.0 05:17Z），节奏很快；README 里出现 CMEM 代币（第三方发行）这一情况在上午期已记录，本期无新变化。

---

### 6. DietrichGebert/ponytail v4.12.0 — "少写"赛道把自证再收紧一格

**事件内容**（本日上午期之后发布，11:44 GMT+8；上期记录为 v4.11.0）
- 四个实质变化：
  1. **审查与审计的发现项编号化**——现在可以直接回"修第 2 和第 4 条"，不用再引述行号。这是把"人机对话里的引用成本"显式产品化。
  2. **`/ponytail-gain` 改报诚实均值**：从旧的"单次基线中位数"改成**agentic 基准的平均值**（代码少 54%、token 少 22%、成本低 20%、快 27%、安全性保持）。README 原文点明旧数字是被"话多的基线"抬高的——**主动把最漂亮的数字换成更难看但更真的数字**。
  3. **CodeBuddy 通过现有的 Claude 插件接入**（不新增一套安装），同时补了 Qwen Code、Goose、Muse Code CLI、Command Code、Kilo Code VS Code 扩展、Factory Droid、ZCode 的适配文档。
  4. README 瘦身，**每个 Agent 的安装步骤全部移进 INSTALL.md**；并在 README 里**点名"唯一官方安装来源"**（防仿冒分发）。
- 其他修复：`/ponytail-debt` 现在能抓到 `/* ponytail: */` 块注释，并在扫描时跳过 `.git`、`node_modules`、`dist`、`build`；审计删除操作前**必须先做全树 caller 检查**；`/bin/sh` 不存在的环境跳过对应 hook 检查；bench 在正确性检查失败时上报真实错误而不是笼统失败。
- 上一版 v4.11.0 的自伤 bug 教训仍适用（上午期已记）：**从 v4.10.2 起 root `plugin.json` 里一行改动让 Codex / VS Code / Qwen 把 ponytail 当成 skills-only 插件加载，hook 从未注册、规则从未到模型**。本版继续在收紧这条线（`docs: name the only official install sources`、`CONTRIBUTING.md` 加了 ruleset 变更的基准门槛）。

**值得关注的原因**
1. **"把发现项编号"是一个被低估的交互设计**：Agent 输出里最贵的成本是**人复述给 Agent 的那一段**。编号化把"引用"从复制粘贴变成两个数字，这属于 09-30 context-mode"不产生中间结果"的同一族思路——**减少人机之间的往返载荷**。
2. **"主动换掉更好看的数字"已经连续三期出现**（09-29 修正 80–94% → 均值 54%；本期把 single-shot 中位数换成 agentic 均值）。这不再是个例，而是**这个赛道维护者的默认动作**：因为"少写"的收益最容易被话多的基线夸大，所以必须自证。
3. **"点名唯一官方安装来源"是技能生态的新需求**：当 SKILL.md 成为通用分发格式（09-17 起记录），仿冒分发就是必然问题。同期 10-02 Pi 的做法是"依赖解析期约束 + 只允许 lockfile 单一事实源"，两条线都在收紧分发可信度。
4. **ruleset 变更设基准门槛**：`CONTRIBUTING.md` 要求改规则集必须过基准，这是把"质量约束写进 CI"（10-01 claude-code-action）搬到了技能仓库里。

---

### 7. tinyhumansai/openhuman — Rust harness 把"单进程多 Agent 密度"当成核心指标

**事件内容**
- Rust 核心，GPL-3.0，日 +98，总星 40,645。README 自述"上线一周内连续九天 GitHub trending 第一"。同一套核心出四份东西：Tauri v2 桌面应用（Win/macOS/Linux）、浏览器 SPA、`ratatui` 终端客户端、以及一个 Rust 库 `openhuman-embed`。
- **密度是它最硬的数字**：核心**跑在进程内**（不是 UI 通过 socket 连的独立 daemon）。同一进程内 50 / 100 / 500 个 live agent 的边际成本实测 **1,985 / 1,866 / 1,770 KiB**，总计 223 MiB / 356 MiB / **1,393 MiB**。同样负载若开 500 个独立进程，每实例约 48 MiB——**共享一个进程约 25 倍密度**。冷启动一个 agent turn 102 ms，九阶段 bootstrap（配置加载、注册表初始化、agent 构建、记忆构建、首轮）476 ms；slim 构建常驻约 42 MiB RSS（其中约 15.2 MiB 私有堆）。
- **模块化靠 Cargo feature gate**：贡献者默认 9 个 gate；纯 slim 构建 51 MiB（stripped），加回 `skills` + `flows`（推荐的嵌入配方）约 60 MiB，全开 116 MiB（未 strip）。`scripts/kernel-floor.sh` 对**依赖数量做只降不升的棘轮**——防止依赖数回涨。能力来自可加载原生模块：tinydocs / tinyvoice / tinyjuice / tinyruntime / tinywallet / tinymcp / tinychannels / tinyconnectors，每个配一个定义接口与线格式的 `*-bus` 契约 crate。
- **Jev：用 System 1 小模型做决策而不是生成文本**。它是一个小决策模型（走 TinyHumans System One 代理），输入一个问题 + 一组固定选项，返回每个选项的**校准概率**——三种形态：Choice（选一个）、Score（打分）、Noul（是/否）。**它从不写散文**。最清楚的用途是**工具检索**：215 个核心工具 + 1,000 个 Composio 动作、160 次测试请求下，纯 BM25 检索的 top-1 命中率 **22.5%**，且在 31 个"其实不需要工具"的请求里**多调了 26 次**；改成"先用 embedding 取 top-20 候选、再让 Jev 在候选里选"，top-1 命中 **62.0%**（top-3 内 66.7%），**多余调用降到 1 次**，p50 1.5 秒（BM25 是 28 ms）。若让 Jev 先选 Composio 的应用族、再选族内动作，Composio 单项 top-1 提到 **80.3%**。没有 TinyHumans 凭证时自动回落 BM25。
- Jev 也驱动浏览器工具里的分步决策：**有后果的动作（下单、发送、删除）返回 `NeedsConfirmation` 而不是执行**。
- **Workflows 是保存下来的类型化自动化图**（基于开源的 tinyflows），22 种节点（agent 调用、HTTP、代码、条件、循环、子工作流、审批…），可按计划/应用事件/手动触发，支持暂停后中途恢复。**与 n8n/Zapier 的区别是：你描述要什么，Agent 起草图，你在画布上审阅并保存**，而不是手工连线。
- **可嵌入**：`openhuman-embed` 是一个进程一个 `Runtime`、上面挂任意多个独立 `Agent`，每个有自己的 provider、访问档位（`Access::readonly()` / `Access::full()`）、工作目录、MCP server、技能、提示词与沙箱——README 给了一段 reviewer（只读、不改文件）+ fixer（全权）串联的真实示例代码。
- **商业模式是"一把 key 通吃"**：一个 TinyHumans API key 覆盖托管推理（含 OpenRouter 目录）、web 搜索、embedding、媒体生成、集成、语音、Jev 排序器；代码里 `.api_key("th_…")` 或环境变量 `OPENHUMAN_BACKEND_API_KEY` 一次配好。所有引擎（LLM / embedding / memory / web search）都是配置选择而非硬编码，可换成 Ollama、LM Studio、MLX、任意本地 OpenAI 兼容服务、Claude Agent SDK，或 26 家 BYOK；记忆引擎可指向托管的 CortexDB 或你自己的 CortexDB，**两个都不配则记忆关闭**。

**值得关注的原因**
1. **"单进程多 Agent 密度"是一个新的可比指标**：以前比的是 token 成本、延迟、上下文长度；本期第一次看到把 **KiB/agent 与 25× 进程密度**作为核心卖点，且给了完整方法论。这与 09-23 agent-substrate 的"10x 密度、30x 超卖"是同一条线在**单机**层面的落地——**Agent 的运行成本开始按内存密度算**。
2. **System 1 小模型做工具选择第二次出现**：09-29 记录过 trycua 的 **CUA-S1**（forms profile 打分决策），本期是 Jev 在工具检索上把 top-1 从 22.5% 提到 62%、把多余调用从 26 次压到 1 次。**"不让主模型做低价值决策"正在成为标准结构**，而且这里的收益是双份的——准确率提升 + 调用次数下降（也就是钱）。
3. **"有后果的动作返回 NeedsConfirmation"**：把审批点写在决策层而不是写在工具层，与本期 Cloudflare OS 的 Gatekeeper、上午 OpenMontage 的 contact sheet 构成三种人在回路实现。
4. **依赖棘轮（`kernel-floor.sh`）值得单独抄**：对依赖数量做"只降不升"的自动约束，是防止项目随时间变肥的工程手段，在 10-02 Pi 的"依赖解析期约束"之后，本期从另一个方向解决同一个问题。
5. **诚实标注**：README 说"单机上千 agent 是这个方向，不是我们已达成的数字"——**没把方向当成已实现**。

---

### 8. zeronsh/zeron — 控制面品类坐实，第二个入场者，且信任半径写得比第一个清楚

**事件内容**
- Rust，MIT，日 +81，总星 3,020。定位：**本地优先地控制你的编码 Agent**——Claude Code、Codex、Cursor、Devin、Grok、Hermes、Pi、Antigravity，可选多设备同步。赞助方是 The Context Company。
- **默认就是 local-only**：每台设备跑一个小引擎、会话存在该设备上；**全新安装不开账号、不连网络**即可用。`curl … install.sh | sh` 会立刻起 daemon 并在重启后保持，同时写一个 per-user 的 `zeron.desktop` 与图标。Linux 需要系统 ALSA 运行时（`libasound.so.2`），**headless 模式也要**（因为它共用桌面可执行文件）；安装器会先确认二进制能起来再激活，并报告缺失的运行时库。
- **多设备同步是可选且"只在你想要时"才开**：`zeron login` 会改变下次引擎启动所选的 profile，所以必须先 `zeron daemon stop`；`login` / `logout` 在引擎占用数据目录时**拒绝改凭证**。桌面应用遵守同一条"下次重启生效"的边界。
- **信任半径被写得很具体**（这是本条的看点）：同一同步账号下的设备**被信任可远程访问工作区**——能列、读、写另一台设备的文件；开启 `Show ignored files` 会让 gitignore 的文件（**例如 `.env`**）在远端可见；**`.git` 永远排除**。README 直说：只把你愿意交出其工作区全部内容的设备登进去。另外，**登录不会上传、移动或导入已有的本地会话**——本地会话及其附件留在本地 profile 下，退出登录回到 local-only 时它们会重新出现。
- 其他：桌面端启动时 + 每小时 + 唤醒后检查更新，后台下载，侧栏提示"Update ready — restart to apply"，不重启则下次退出时安装；`ZERON_AUTO_UPDATE=0` 只提醒不下载；daemon 装成服务时会在没有活跃 agent 运行/终端时重启到新版本；Windows 安装器**按用户安装、不需要管理员权限**，也提供便携 ZIP（把 `zeron-update.json` 放在 `zeron.exe` 旁边可应用内更新）。

**值得关注的原因**
1. **"控制面"从一家变成两家**：上午期 t3code（四端、remote-ready、卖 "Nothing."）刚被记为**新品类**，本期 zeron 就以几乎对立的路线入场——**t3code 把远程当主卖点，zeron 把 local-only 当默认、同步当可选**。同一个位置出现两种哲学，说明这个位置是真的。
2. **"默认不联网"成为可售卖的属性**：全新安装不连网络、不建账号。这与 09-28 起"本地优先从单点技术变成默认架构假设"一致，但本期是把它**当成产品默认值**而不是选项。
3. **信任半径的写法值得照抄**：直接写明"同账号设备可读写你的文件、开 ignored files 会暴露 .env、`.git` 永远排除、只登你信任的设备"。这是 10-02 cua 的 AGPL 许可说明、10-05 上午 openrig 的"未测试清单"之后，**又一次把风险从脚注搬到正文**。
4. **"登录不动已有数据"是本地优先工具的必备承诺**：不上传、不迁移、退出后本地会话原样回来。做多设备同步的工具如果做不到这一点，本地优先就是假的。
5. 参照价值：`zeron status` / `zeron daemon start|stop|restart` / `zeron update` 这套命令面，加上"桌面应用与 headless 共用可执行文件"导致的 ALSA 依赖，是自托管 Agent 工具在**桌面与服务器双形态**下的真实踩坑记录。

---

### 9. shy3130/tick-stock-panel — 自托管 A 股量化工作台：口径统一 + 明确不做荐股

**事件内容**
- Python，MIT，日 +51，总星 5,574，**fork 1,338（fork/star 比 0.24，本期最高）**。定位：自托管、零运维的 A 股"选股 + 监控 + 回测"量化工作台，Docker 单容器，数据全落本地 Parquet。
- **架构第一原则是"数据工程优先"**，八个特点里最关键的三个：
  - **能力路由矩阵**：6 类数据集按数据源**声明能力独立路由**——同一数据集可随时换源，**指标与回测口径不变**。注册表集中定义、可扩展，带档位探测（TickFlow 的 None/Free/Starter/Pro/Expert）+ 插件源能力声明，且 **fail-closed**（声明了 `pct_unit` 却没提供就拒收）。数据源已插件化（官方 TickFlow SDK、fuyao 同花顺 REST、YAML 自定义源、示例插件）。
  - **单一 enriched 口径**：**只存 15 列基础数据、现算 68 列指标信号**；选股 → 回测 → 监控 → 复盘吃同一份数据。这是对"选股、回测、监控各用一套工具导致口径对不上"的直接回答。
  - **回测 = 实盘同路径**：策略执行只有一条 `StrategyEngine.run`；分钟策略逐交易日回放 + **"当日已知"纪律**，README 明确目标是"杜绝未来函数"。
- **执行与隔离**：回测跑在 **spawn worker 子进程**里，持久 run ID，刷新/切页重连不丢任务，主服务永不被计算卡住。选股引擎用 Polars **毫秒级扫全 A 股**（25 个内置策略 + 自定义信号 + AI 生成），日线与分钟策略统一单池、按策略声明周期自动路由。
- **回测四视图**：因子回测（IC/IR、分层收益、多空组合，62+ 因子目录先筛掉无效指标）、策略回测（净值曲线、回撤、夏普、胜率、盈亏比、蒙卡回撤，T+1 / 手续费 / 滑点 / 止损，SSE 流式进度，评分因子策略附**因子归因**——胜/败单入场信号日的因子对比）、分钟策略回测（逐日回放信号、分钟收盘入场、分钟级成交明细）、挖掘（嵌套样本外因子与策略挖掘：训练区间因子方向重估 + 相关性去重 + 多因子排名组合搜索，**候选入库后显式确认才发布，永不自动上线**）。
- **AI 助手是"读 + 写"分离的**：21 个查询工具覆盖个股/大盘/板块/自选/持仓/信号/策略/因子/数据完整性/扩展数据表；另有 **4 个动作工具**（生成信号策略 / 回测 / 加自选 / 数据补全），**写操作先弹确认卡**（完整待执行参数可见、可确认/取消、120 秒超时自动取消）才执行；逐字流式输出 + 工具调用足迹卡（参数与耗时可展开核对），**每条回答附风险与数据口径提示**。AI 是完全解耦的扩展模块，**删目录即卸载**；AI 接口走 OpenAI 兼容（DeepSeek / 通义 / Ollama 等）。
- **开放能力**：Open API（Token 管理）+ MCP。
- **边界写得极克制**：README 开篇即声明"谨作为本地量化提供解决思路与方案，**不作为投资软件或者看盘软件**"，并列出**明确不做**：不对标同花顺/通达信、**不内置"AI 荐股 / 涨停预测"**；仅供学习研究使用。

**值得关注的原因**
1. **金融垂类 Agent 的正确做法被演示出来了**：不是"让 LLM 荐股"，而是**先把数据口径做成基础设施**（能力路由矩阵 + 单一 enriched 口径 + 只存 15 列现算 68 列），再把 AI 作为"能读全站数据、写操作要确认"的一层。这与 09-23 anthropics/financial-services 把人工签核写成合规声明是同一取向，但这次是**开源个人项目**。
2. **"回测与实盘同一条代码路径 + 当日已知纪律"是防未来函数的工程答案**：只有一条 `StrategyEngine.run`，意味着回测里跑通的东西就是实盘跑的东西。任何做量化工具的人都会立刻认出这个设计的价值。
3. **"永不自动上线"是本期第三次出现**：挖掘出的候选因子/策略**入库后需显式确认才发布**（上午 OpenMontage 是资产生成前卡住，Cloudflare OS 是事后批量批）。**自动化的产出必须经人确认才生效**正在成为跨领域默认。
4. **fail-closed 的数据源契约**：声明能力却没提供就拒收，而不是静默按默认处理。这与 09-30 SkillSpector 的 fail-closed 资源上限、10-02 Pi 的依赖约束同族——**边界处宁可拒绝也不猜**。
5. **"明确不做"清单**：不对标行情软件、不做 AI 荐股/涨停预测。在金融这个最容易被诱导越界的领域，**把不做什么写在第一屏**本身就是产品判断。fork/star 0.24 说明它被大量拿去改造自用，而不是只被收藏。

---

### 10. Autumn-27/ARTEX — Agent 长链任务的最完整工程样本：双图 + 无状态 planner 共享 todolist

**事件内容**
> 说明：ARTEX 是开源安全研究项目，README 以醒目篇幅声明**仅限个人学习、代码研究与本地隔离环境验证，严禁对任何线上系统/网站发起扫描、探测、利用或攻击（无论是否获得授权）**，并在免责声明中引用《网络安全法》《数据安全法》《个人信息保护法》。本文只讨论其架构与工程方法。
- Go 单体后端（`go:embed` 内嵌 Next.js 前端）+ PostgreSQL，AGPL-3.0，日 +45，总星 1,537。作者 Autumn-27（同一作者的 ScopeSentry 资产收集系统可一键同步资产）。百度"agent+"攻防挑战赛冠军项目。Agent 能力由作者自己的 `norma` SDK 提供（agentcore / tool / permission / harness / memory / transcript）。
- **核心是双图架构**，把"目标是什么"和"测到什么程度"拆成两张独立又相连的图：
  - **资产图（全局共享，跨任务同一份真值库）**：节点为 root_domain / subdomain / ip / service / app / endpoint，归属公司；域名→子域→服务→端点的父子关系与去重 key **全部由程序计算，Agent 只提交原始信息**。
  - **探索图（每任务独立）**：节点为 goal / intent / fact / finding / hint，用 `spawns` / `derived_from` / `yields` / `proves` 连成**血缘链**，回答"哪个方向派生自哪些事实、产出了什么"。
  - **两图靠锚点表相连**（`exploration_anchors(node_id, asset_id)`）：既能从探索方向看它打了哪些资产，也能从某个资产反查它被哪些意图测过、得出过哪些事实。这直接支撑**资产测试覆盖度**与**资产覆盖图**（范围内资产 + 已测高亮）。
- **角色分工是严格的**：**planner 是唯一的意图生成者**，读探索图态势、判目标、只在有未覆盖的新方向时派意图进 frontier；**worker 领一条意图**、用真实工具执行（Bash / HTTP，全程走记录型 MITM 代理留痕 + CA 验证）、把新资产/事实/漏洞写回两图后即停。引擎是事件驱动的闭环：图一变（debounce）就唤醒 planner，planner 派意图，worker 执行写回，写回又触发下一轮，直到 `prove_goal`。**大多数唤醒派 0 个意图——没有新方向就结束。**
- **两个关键机制**（这是本期最值得抄的部分）：
  - **worker 之间的过程级信息交换**：有价值的观察常常只出现在某个 worker 的**执行过程**里而没被写成正式 fact。于是 worker 可以 `search_all_worker_traces(q)` 在**本任务其他 work 的执行过程**里按关键字检索（自动排除自己这条意图，命中项带 `intent_id`），再用 `list_worker_traces` / `get_worker_trace(intent_id, step_ids=[…])` 取具体几步的完整内容。**信息以"执行过程"为粒度在 worker 之间流动，但边界不变**——每个 worker 仍只做自己领到的那条意图。
  - **planner 的跨唤醒共享 todolist**：真实攻击链是有前后依赖的多步序列（发现注入点 → 拿到凭据 → 横向 → 提权），一次性并行派下去只会乱套。但 planner 是事件驱动的、**每次唤醒都是全新会话**。解法是让它持有一份**按任务保留、跨唤醒常驻的规划待办**：一条串行链只记录一次，之后每轮只对"前置步骤已完成、其依赖的 fact 已存在"的下一步派意图，并随进展把已被 fact 满足的步骤标完成。**于是攻击链在"事件驱动 + 无状态会话"的环境下仍能稳定推进、不重复、不错序。**
- **人在回路**：有 `mainagent` 做人在环路对话，有 `guard` / `intercept` 工具审批门，前端有全局"审批记录"、任务内"拦截审批"与对话中的审批卡片，均支持展开看调用详情。
- **自更新做得比多数产品认真**：页面一键更新 → 下载当前平台发布包 → **比对 Release 的 SHA256SUMS** → **用 `-h` 冒烟测试新二进制** → 暂存为 `artex.new` → 程序退出由 `start.sh` 换装。**校验或冒烟不通过就丢弃暂存件继续跑旧版**；新版若**连续 3 次启动失败自动回滚到 `artex.old`**（失败的留作 `artex.failed`）；随时可手动回滚。开发构建（版本号含 `dev` 或 git describe 后缀）**禁用更新**。数据库迁移不用手执行——每次启动幂等重跑 `schema.sql`（`ADD COLUMN` / `CREATE INDEX IF NOT EXISTS`），即"重启即迁移"。Docker 下**只换程序不换镜像**（镜像里的 playwright/nmap 等工具链不跟着升级），这一点也写明了。
- 其他：可预置可编辑的 `retester`（漏洞复测）Agent；复测结论分"仍可复现 / 已修复 / 无法确认"，**结论为"已修复"时自动改漏洞处置状态**，其他结论保留原状态，原始证据与报告始终保留；同一漏洞复测中复用已有会话。**演示模式只生成明确标注的模拟记录、不请求真实目标**。部署支持一键脚本 / Docker Compose / 预编译二进制 / 源码单二进制 / 跨平台 Release 打包，UPX 默认关闭并解释了原因（可能与部分内核/虚拟化/安全策略不兼容）。

**值得关注的原因**
1. **这是"无状态 Agent 会话"这一限制的最完整解法**：planner 每次唤醒都是新会话，但靠**共享 todolist** 把串行依赖链保住；worker 各自只领一条意图，但靠**过程级检索**互相复用观察。**"状态不放在会话里，放在图与清单里"**——这比单纯加大上下文窗口是更本质的答案。
2. **"程序算事实，模型提交原始信息"是本期最干净的一条分工原则**：域名→子域→服务的父子关系、去重 key 全由代码计算，Agent 只负责提交它看到的东西。**不让模型做它可以算错的事**，这与 09-30 PageIndex 的"结构生成零 LLM"、10-05 上午 e2e 的"录制回放"同族。
3. **双图 + 锚点的结构可迁移**：资产图（真值）+ 探索图（血缘）+ 锚点（连接）这套三元结构，任何"长时间跨多个对象推进的任务"都能用——不需要是安全场景。
4. **自更新的质量在榜单上属第一档**：SHA-256 校验 + 冒烟测试 + 失败丢弃 + 连续失败自动回滚 + 开发构建禁用 + 明说 Docker 只换程序不换镜像。这是 10-05 上午 openrig（发布说明带 SHA-256 + 明确"未测试"清单）之后，**把"更新失败怎么办"完整回答**的第二个项目。
5. **演示模式生成"明确标注的模拟记录"且不请求真实目标**：与 10-02 starnet 的"界面不得断言 harness 无法证明的状态"同一条原则——**不能假装做过**。

---

## 三、其他趋势速览

**语言榜新面孔（本期未展开）**
- [router-for-me/CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI)（Go，日 +129，总 **54,171**，forks 8,232）— 把 CLI 类模型账号（Codex OAuth、Claude Code OAuth、Grok Build、Gemini CLI/AI Studio/Vertex、Antigravity、Meta Muse、Devin）统一暴露成 **OpenAI / Gemini / Claude 兼容 API**，支持**多账号轮询负载均衡**、流式/非流式/WebSocket、函数调用、多模态输入。README 的赞助位几乎全是 API 中转服务商（PackyCode / AICodeMirror / APIKEY.FUN / Cubence / Aiberm / OpenLux / PatewayAI 等，报价从"官方价 5%"到"官方价 90%"不等）——**这个赞助列表本身就是一条信号：CLI 订阅账号池化已经形成配套的灰色供给链**。对使用者的提醒：把 CLI 订阅账号当 API 用，是否符合各家服务条款需要自行核对，本报告不背书。
- [AlexsJones/llmfit](https://github.com/AlexsJones/llmfit)（Rust，日 +64，总 37,608）— 检测 CPU/内存/GPU/VRAM（CUDA、Apple Silicon、ROCm、oneAPI），按 **质量 / 速度 / 适配 / 上下文** 四维给模型打分，估算模型来自内存带宽模型 + 运行时采样 + 社区实测；支持 MoE、多 GPU、动态量化选择。**关键设计：每个估算值都带着自己的输入一起发布**，`llmfit info <model>` 会显示这个数字假设了什么、以及在你机器上怎么验证。**新功能是"实测回填"**：下载模型 → 起服务 → 实测 tok/s/TTFT → 从 TUI 直接提 PR 回项目（不需要 `gh` CLI、不需要第三方账号），合并后同硬件的其他人**在跑之前就能看到 `✓` 实测值**。Windows 二进制经 SignPath 签名（并诚实说明"某个 release 可能因为签名 job 跳过/失败而发布未签名产物，请自行验签"）。
- [p-e-w/heretic](https://github.com/p-e-w/heretic)（Python，日 +171，总 33,252，forks 3,721）— 自动化"模型对齐移除"工具（directional ablation / abliteration + Optuna 的 TPE 参数优化），**通过同时最小化拒答数与相对原模型的 KL 散度**自动找参数，目标是"尽量保留原模型智力"。README 给的可复现对比：gemma-3-12b-it 原版 97/100 拒答，社区手工版 KL 1.04 / 0.45，Heretic 自动版拒答 3/100 且 **KL 0.16**。社区已用其发布 **5,000+** 模型。**治理含义值得记**：这类工具把"移除安全对齐"变成了不需要理解 transformer 内部、会跑命令行就能做的事，且质量已接近人工专家——模型分发侧的信任假设需要重新评估。
- [tursodatabase/turso](https://github.com/tursodatabase/turso)（Rust，日 +46，总 24,608）— SQLite 兼容的 Rust 数据库，**实验性支持 Postgres 线协议**。
- [FalkorDB/FalkorDB](https://github.com/FalkorDB/FalkorDB)（Rust，日 +164，总 7,016）— 基于 GraphBLAS 稀疏邻接矩阵的超快图数据库。
- [tailscale/tailcat](https://github.com/tailscale/tailcat)（Go，日 +53，总 8,141）— "像 netcat，但走 Tailscale 数据面、不走它的控制面"。
- [cjpais/Handy](https://github.com/cjpais/Handy)（Rust，日 +84，总 32,863）— 完全离线的可扩展语音转文字桌面应用。
- [zerx-lab/FluxDown](https://github.com/zerx-lab/FluxDown)（Rust，日 +299，总 3,860）— Rust 多协议下载管理器（HTTP/FTP/BitTorrent 磁力/HLS/DASH），浏览器集成。
- [LuxAlgo/Vela](https://github.com/LuxAlgo/Vela)（TS，日 +103，总 965）— LuxAlgo 开源其金融图表核心。
- [vllm-project/semantic-router](https://github.com/vllm-project/semantic-router)（Go，日 +15，总 6,033）— vLLM 官方的可编程"多模型混合"路由器。
- [mostlygeek/llama-swap](https://github.com/mostlygeek/llama-swap)（Go，日 +16，总 5,840）— 为任意本地 OpenAI/Anthropic 兼容服务做可靠模型换入换出。
- [github/github-mcp-server](https://github.com/github/github-mcp-server)（Go，日 +21，总 33,373）— GitHub 官方 MCP server 仍在榜。
- [earendil-works/pi](https://github.com/earendil-works/pi)（TS，日 +401）— 10-02 已展开（7 包拆分、依赖解析期约束）。**本期新信号**：Cloudflare OS 把 `pi-agent-core` 列为关键依赖并致谢（"一个 API 支持所有 LLM provider"）——**自扩展 harness 正在变成别人产品的地基**。
- 其他：EchoMuse（Alexa 替代）、kaifcodec/user-scanner（含原生 MCP 的 OSINT 套件）、jamwithai/production-agentic-rag-course、Bennettxai/FounderOS-DEMO、hieunc229/mailflare、ys-ll/uniterm、NdoleStudio/httpsms、samwhosung/benilla（Rust + Bevy 从零写 WoW 1.12.1 客户端）。

**已推送仓库今日新动态（本日上午期之后）**
- [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage)（Python）— 今日 **14:01 GMT+8** 有新发布（atom 无正文，无法取变更明细）。上午期已展开其 Backlot 审批门与案例成本，本期只记时间。
- [pingdotgg/t3code](https://github.com/pingdotgg/t3code)（TS）— 今日 12:31 GMT+8 发 `0.0.46-nightly.20261005.2667`；夜间通道按天连发（10-04 一天内 2652 / 2657 两个 nightly）。
- [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)（TS）— 停在 v0.8.127（10-05 01:04 GMT+8），本日上午期已记；节奏仍在"一天多版"的量级。
- [NVIDIA/OpenShell](https://github.com/NVIDIA/OpenShell)（Rust）— 停在 10-03 的 Development Build（v0.1.3-pre.3 是 10-02）；周 +5,996。
- [mvschwarz/openrig](https://github.com/mvschwarz/openrig)（TS）— 仍 v0.6.5（10-04）；本日上午期已展开。
- [vectorize-io/hindsight](https://github.com/vectorize-io/hindsight)（Python，周 +10,623）仍 v0.10.2（09-29）；[debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio)（周 +14,689 周榜第 1）仍 v0.5.6（09-23）；[Tencent/WeKnora](https://github.com/Tencent/WeKnora)（月 +10,912）仍 v0.8.2（09-24）——**三个"热度高无新版本"连续第二期不变**。
- 其他在榜已推送项：paperclip（周 +8,732）、Agent-Reach（日 +980）、impeccable（日 +1,171）、ai-engineering-from-scratch（周 +4,904）、yoinks（周 +2,361）、MoneyPrinterTurbo（周 +2,291）、GhostTrack（周 +1,778）、coursebook（周 +1,626）、Octop（周 +1,496）、alirezarezvani/claude-skills（周 +1,024）、tilelang（周 +839）、addyosmani/agent-skills（日 +336）、next.js（周 +477）、caddy（v2.11.7，10-03）、getsentry/sentry（日 +152）、Effect-TS/effect（日 +243）。

---

## 四、当日主线判断

1. **大厂开始把"内部 AI 工作台"整体开源（cloudflare-os）**。而且给的是**可复制的架构**而不是演示：Durable Object per workspace + Dynamic Worker per gadget + Facet per Gatekeeper，加上"Gadget 每人一份私有实例"这个对 SaaS 的正面挑战。**它把"AI 让每个人都能改自己用的软件"当成架构前提，而不是当成功能。**

2. **"异步人在回路"是本期最硬的一个新机制**。Gatekeeper 的做法是：**本地模拟动作结果 → 让 Agent 继续推进 → 人方便时批量批准或否决**。它直接解决"人一离开就卡死，于是被迫关掉安全机制"这个日常摩擦。本期三种人在回路实现并列：cloudflare-os（事后批量批）、OpenMontage（渲染前卡住，上午期）、openhuman（有后果的动作返回 `NeedsConfirmation`）。

3. **成本战场细分到第四层：会话启动成本**。caveman 把"agent 说什么（skill）"与"agent 读什么（proxy）"拆成两个独立账本；claude-mem v13.31.0 把 SessionStart 从 **21,700 行 / 63 MB 读降到索引读 4 ms**（1.2GB 库上从约 3 秒、最坏 44 秒）。**上下文经济的账本现在是四个：不产生中间结果 → 不读取 → 不调用模型 → 不让会话启动等待。**

4. **Agent 审计成为独立环节，且"不得自评"被硬编码（iFixAi）**。一次运行必须 SUT 与 Judge 来自不同厂商，否则结果标记为自评、不可引用；三项 mandatory minimum 未达则总分封顶 60%。**这是把 09-30 SkillSpector 的"安装前扫描代码"推进到"运行中审计行为"**，并给出了五个失败面（Fabrication / Manipulation / Deception / Unpredictability / Opacity），其中"沙袋化（察觉在被测就变好）"是只有审计视角才会提的指标。

5. **控制面品类一天内坐实（t3code → zeron）**，且两个入场者路线对立：**t3code 卖 remote-ready，zeron 默认 local-only、同步可选**。同一位置两种哲学同月出现，说明这个位置是真的。而且 zeron 把**信任半径写进正文**：同账号设备可读写你的文件、开 ignored files 会暴露 `.env`、`.git` 永远排除、登录不上传本地会话。

6. **"单进程多 Agent 密度"与"System 1 小模型"是两个新出现的硬指标（openhuman）**。500 agent 一个进程、边际 1,770 KiB/agent、约 25× 进程密度；Jev 小模型把工具检索 top-1 从 BM25 的 22.5% 提到 62%、**多余调用从 26 次压到 1 次**。前者接 09-23 substrate 的"10x 密度"，后者接 09-29 cua 的 CUA-S1——**"不让主模型做低价值决策"第二次出现，且这次同时改善了准确率和费用。**

7. **垂类 Agent 的正确做法是"先做数据口径，再谈 AI"（tick-stock-panel）**。能力路由矩阵（换源不换口径、fail-closed）、只存 15 列现算 68 列、**回测与实盘同一条 `StrategyEngine.run`**、"当日已知"纪律防未来函数、写操作确认卡、以及**明确不做 AI 荐股/涨停预测**。fork/star 0.24 说明它被大量改造自用。

8. **无状态 Agent 会话的完整解法出现了（ARTEX）**：planner 每次唤醒都是新会话，靠**跨唤醒共享 todolist** 保住串行依赖链；worker 只领一条意图，靠**过程级检索**（`search_all_worker_traces` → `get_worker_trace`）互相复用执行过程中的观察。核心原则是**"状态不放在会话里，放在图与清单里"**，且"域名父子关系与去重 key 全部由程序计算，Agent 只提交原始信息"——**不让模型做它可以算错的事**。

9. **网关分化成两条路**：experiential 走"零加价 BYOK + 用你自己的 OTel trace 拟合专用路由、甚至微调自己的模型"（网关从转发层升级成优化层）；CLIProxyAPI 走"把 CLI 订阅账号池化成 OpenAI 兼容 API + 多账号轮询"（README 赞助位全是 API 中转服务商，**供给链已经成形**）。前者是工程，后者有服务条款风险，**两者需要的信任前提完全不同**。

10. **榜单方法论更新：同日第二次运行要换"维度"而不只是换"周期"**。本日 09:44 已用掉 daily/weekly/monthly 三榜，14:00 这期改用**语言维度** `/trending/<lang>?since=daily`（python / typescript / rust / go / c）——**一次性拿到 8 条全新面孔**，且能观察到主榜看不到的东西（例如 caveman 在 Go 榜第 1、CLIProxyAPI 在 Go 榜、ARTEX 在 Go 榜，都未进主 daily 榜）。**建议后续同日多跑时固定加这一步。**

11. **本期非 Agent 项目 1/10，为十一期最低**。语言维度榜单上今天几乎全是 Agent 相关（Agent 工具 / harness / 控制面 / 记忆 / 审计 / 网关 / 垂类 Agent），非 Agent 项（turso、FalkorDB、Handy、FluxDown、Vela、tailcat、caddy、sentry、Effect）都只出现在速览层。**这不是筛选偏差，是当天的真实结构**：主 daily 榜 16 条里 Agent 相关占 13 条，语言榜把长尾也捞上来后，非 Agent 密度更低。

---

*报告生成时间：2026-10-05 14:00 (GMT+8) · 数据源 github.com/trending（语言维度五榜 daily）+ releases.atom + raw.githubusercontent.com · 与当日 09:44 期去重*
