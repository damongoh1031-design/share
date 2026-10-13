# GitHub AI 趋势日报 · 2026-10-09

> 数据源：github.com/trending 主榜（daily 9 / weekly 11 / monthly 24）+ 语言维度榜 12 个（python / typescript / rust / go / c / c++ / javascript / cuda / html / java / swift / vue，共 155 条去重）
> **主榜头部已彻底固化**：daily 9 条中仅 1 条新面孔（liquidslr/system-design-notes），weekly 11 条与 monthly 24 条**全部为已推送仓库**。本期 10 条详细中 **9 条来自语言维度榜 + 1 条为已推送仓库今日重大新版本**。
> 星数为抓取时点数值；GitHub trending 的排列顺序不等于增幅排序，本报告只报增幅不声称名次。

---

## 一、榜单速览

| # | 仓库 | 语言 | 总 Star | 增幅 | 来源 | 一句话 |
|---|---|---|---|---|---|---|
| 1 | [microsoft/mxc](https://github.com/microsoft/mxc) | Rust | 1,862 | +135 | rust | 微软官方跨平台沙箱执行 SDK，策略驱动的分层隔离 |
| 2 | [docker/docker-agent](https://github.com/docker/docker-agent) | Go | 4,257 | +766 | go | Docker 官方 Agent 构建/运行运行时，Agent 可推 OCI 仓库分发 |
| 3 | [openai/codex-security](https://github.com/openai/codex-security) | TS | 11,042 | +30 | typescript | OpenAI 官方安全扫描 CLI + TypeScript SDK |
| 4 | [microsoft/agent-framework](https://github.com/microsoft/agent-framework) | Python | 14,023 | +27 | python | 微软官方 Agent 框架，吞并 Semantic Kernel + AutoGen |
| 5 | [CursorTouch/Windows-MCP](https://github.com/CursorTouch/Windows-MCP) | Python | 8,367 | +360 | python | Windows 计算机使用 MCP，不依赖视觉模型 |
| 6 | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | JS | 93,894 | +338 | javascript | 反 AI slop 的前端审美技能包 |
| 7 | [koala73/worldmonitor](https://github.com/koala73/worldmonitor) | TS | 88,103 | +89 | typescript | 实时全球情报仪表盘，本地 AI 可零 key 跑 |
| 8 | [Tracer-Cloud/opensre](https://github.com/Tracer-Cloud/opensre) | Python | 11,666 | +81 | python | AI SRE 的框架 + RL 训练评测环境 |
| 9 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | TS | 10,930 | +241 | typescript | 电影级产品视频 Agent 技能，157 张镜头配方卡 |
| 10 | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) **v13.35.0** | TS | 98,677 | +670 | daily | 渐进式记忆检索，三步有界披露 + 原生记忆桥 |

---

## 二、10 条详细

### 1. microsoft/mxc — 微软把「Agent 沙箱」做成可嵌入的跨平台 SDK

**事件**：微软开源 **Microsoft eXecution Container (MXC)**，定位是"运行不可信代码（模型输出、插件、工具）的沙箱化执行系统"，覆盖 Windows / Linux / macOS。仓库今日在 Rust 榜上榜（+135，总 1,862，forks 109），**MXC SDK v1.0.0 于 10-07 发布**（此前为 v1.0.0-rc4/rc5）。

**核心内容**
- **形态是 SDK 依赖，不是服务**：Rust（`mxc-sdk`）/ .NET（`Microsoft.Mxc.Sdk`）/ Node（`@microsoft/mxc-sdk`）三套 typed SDK 编译进你自己的应用；非 SDK 场景可用 `wxc-exec.exe` 吃 JSON 容器创建请求（有 stable schema）。
- **九个后端、按平台给默认值**：Windows 11 x64/ARM64 默认 `processcontainer`（另有 `windows_sandbox`、`wslc`、`microvm`、`hyperlight`、`isolation_session`）；Linux 默认 `bubblewrap`（另有 `lxc`、`microvm`、`hyperlight`）；macOS 默认 `seatbelt`。带 \* 的为实验性。
- **策略三件套**：文件系统策略（只读 / 读写 / 拒绝路径清单）、网络策略（代理、出站控制、按后端的主机过滤）、UI 策略（剪贴板 / 显示 / GUI 访问）。生命周期为 provision → start → execute → stop → deprovision 的**有状态长跑容器**。
- **两个自我削弱式设计**：① `--audit` 模式**会关掉该工作负载的全部沙箱安全**，README 用 Warning 明确写"绝不要用它跑不可信代码"，定位是给策略作者反推"这个可信工具到底需要哪些文件和能力"；② 遥测需**四条件同时满足**（单次运行 opt-in + Windows 用户显式同意 + 管理策略允许 + 应用在请求里打开开关），并声明"管理员可以阻止遥测，但不能替用户给出同意"。

**值得关注的原因**
Agent 运行时隔离这条线在两周内被连推三次：09-30 NVIDIA/OpenShell（运行前/运行时强制）、10-08 kubernetes-sigs/agent-sandbox（K8s CRD 收口编排），现在 **微软从"SDK 内嵌"这条第三路切进来**——不抢编排层、不抢 K8s，只做"任何 app 都能把不可信代码塞进去"的那一层。同时它把"编排 vs 隔离"的边界写得很清楚（隔离委托给各 OS 原生机制），与 agent-sandbox 把隔离委托给 RuntimeClass→gVisor/Kata 是同一分工。**"隔离层不自己造、只做统一策略面"正在成为大厂共识。**

---

### 2. docker/docker-agent — Docker 官方下场做 Agent 运行时，并把 Agent 变成 OCI 制品

**事件**：Docker Engineering 的 **docker-agent** 今日在 Go 榜大幅上榜（**+766**，总 4,257，forks 496），最新版 **v1.149.0**（10-07）。

**核心内容**
- **是 `docker` CLI 插件**：Docker Desktop 4.63+ 已预装，直接 `docker agent run`；Homebrew / 二进制发布亦可（symlink 到 `~/.docker/cli-plugins/docker-agent`）。
- **声明式 YAML 定义 Agent**：`agents:` 下写 model / description / instruction / toolsets，工具集可引用任意 MCP server（本地、远程、Docker 化），也内置 think / todo / memory 工具与 RAG（BM25、embedding、hybrid、rerank 可插拔）。
- **多 Agent 自动委派**：root agent 可把任务分给专门化的子 agent 团队。
- **最关键的一条：Agent 是可分发制品**——"Push agents to any OCI registry, pull and run them anywhere"，即 `docker agent run myorg/agent:tag`。这等于把 Agent 定义、工具依赖、模型配置当成容器镜像一样版本化与分发。
- **自举**：README 明写"We use `docker-agent` to build `docker-agent`"（`docker agent run ./golang_developer.yaml`）。

**值得关注的原因**
过去两周"Agent 分发格式"一直在抢：SKILL.md（技能）、plugin marketplace（Claude / Cursor / Spotify / 微软 / GitHub）、rig（openrig）。Docker 给出的答案是**复用已有的 OCI 标准**而不是另造一套——这一招绕开了"生态分裂"，代价是必须绑定容器运行时。同时这是**基础设施厂商连续第二天在 Agent 赛道落子**（10-08 是微软 Power Platform 插件市场 + Spotify Portal），且都指向同一结论：**大厂 Agent 化的落点是分发与权限，不是模型**。

---

### 3. openai/codex-security — OpenAI 官方把安全扫描做成 CLI + SDK + CI

**事件**：`@openai/codex-security`（命令别名 `cs`）在 TypeScript 榜上榜（+30，总 11,042，forks 858），最新版 **Codex Security 0.2.0**（10-06）。

**核心内容**
- **不只是扫，是"发现 → 验证 → 打补丁 → 复验"闭环**：deep scan 会对仓库/指定路径跑**并行发现 worker**；随后验证候选发现、生成补丁、并**验证已有修复**。
- **可产出治理资产**：`cs policy .` 草拟 `SECURITY.md` 策略（草稿落在 checkout 之外，需人工 review 后手动拷贝到 `Policy target` 才生效——**生成≠安装**）；扫描会保存威胁模型，可用 `cs export --artifact threat-model` 单独导出。
- **企业集成面铺得很全**：导入 GitHub code scanning 告警，导出 SARIF / JSON / CSV，发布到 Linear 或自建 findings service（`cs serve`），支持 owner 建议（从源码与 Git 历史推断）。
- **两处诚实标注**：① findings service 的 API **没有内置鉴权**；② 导入会把完整 finding JSON 发给配置的 embeddings 端点，**即使已用 ChatGPT 登录也仍需 embedding API key**。
- **CI 姿势要求沙箱**：官方 GitHub Action 示例先 `apt-get install bubblewrap apparmor-profiles` 并加载 `bwrap-userns-restrict` 策略，再跑扫描；模型示例为 `gpt-5.6-sol`、effort high。另有 Daybreak Blue 权限档（`--cyber-access-program`）与 Trusted Access for Cyber 审批。

**值得关注的原因**
这是**第一个由模型厂商官方提供、且覆盖"修复验证"的安全 Agent 产品**。它把 10-01 起观察到的一条规律又推进一步：Agent 安全能力正在从"扫描器"变成"带证据链的流程"——验证候选、复验修复、SARIF 外发、owner 归属，全部要求可审计。另外它主动暴露"findings service 无鉴权"，属于 10-06 起延续的**主动削弱自身数字/边界**的诚实模式。

---

### 4. microsoft/agent-framework — 微软官方 Agent 框架完成两代合并

**事件**：**microsoft/agent-framework (MAF)** 在 Python 榜上榜（+27，总 14,023，forks 2,447），**python-1.21.0 于 10-08 发布**，dotnet-1.24.0 于 10-07 发布。

**核心内容**
- **三语言、一套概念**：Python 与 C#/.NET 完整实现且 API 对齐，Go 走独立仓库 `microsoft/agent-framework-go`。
- **图式编排 + 生产级语义**：sequential / concurrent / handoff / group collaboration 四种模式；内建 **checkpointing、streaming、human-in-the-loop、time-travel**。
- **两条迁移路径**：官方提供 **Migration from Semantic Kernel** 与 **Migration from AutoGen** 指南——即微软把自己前两代 Agent 产品线收口到 MAF 一个框架。
- **部署与观测**：Foundry Hosted Agents 号称"额外 2 行代码"把 Agent 部署到托管基础设施；OpenTelemetry 分布式追踪内置；另有 DevUI 交互式开发界面。
- **声明式 Agent 与 Agent Skills**：支持 YAML 定义 Agent；仓库内有一份 **`docs/decisions/0037-agent-skills-design.md`** 专门记录技能体系的设计决策（把 SKILL.md 生态的接口设计做成 ADR，属于少见做法）。
- AF Labs 单独发实验包（benchmarking / RL / 研究向）。

**值得关注的原因**
"官方框架收口"是本期与 mxc 并列的第二个微软动作，但意义不同：**MAF 让"Agent 框架"这一层不再由社区项目主导**。对使用者的直接后果是——Semantic Kernel 与 AutoGen 两个生态的迁移成本被一次性摊掉；对生态的后果是——技能/插件/托管三条线被同一个厂商同时握在手里（MAF + mxc 沙箱 + Foundry 托管 + Power Platform 插件市场）。

---

### 5. CursorTouch/Windows-MCP — Windows 计算机使用 MCP，绕开视觉模型

**事件**：**Windows-MCP** 在 Python 榜上榜（+360，总 8,367，forks 926），最新版 v0.8.7（09-30）。

**核心内容**
- **原生操作 Windows UI**：通过系统 UI 元素直接交互（打开应用、控窗、模拟输入、文件导航、QA 测试），官方 MCP server，`mcp-name: io.github.CursorTouch/Windows-MCP`，已进 MCP Registry 与 PyPI（支持 `uvx windows-mcp`）。
- **明确不依赖视觉**："Unlike many automation tools, Windows-MCP doesn't rely on any traditional computer vision techniques or specific fine-tuned models; it works with any LLMs"——**视觉可选**，走 UI Automation 而非截图理解。
- **覆盖面罕见地宽**：支持 **Windows 7 / 8 / 8.1 / 10 / 11**（多数 computer-use 方案只做 Win10+）。
- 生态信号：README 称在 Claude Desktop Extensions 目录**达到 200 万+ 用户**；同作者另发 `windows-use`（基于 Windows-MCP 构建的 agent）。
- 生态位对照：与本期同榜的 `vercel-labs/agent-browser`（Rust 原生浏览器自动化 CLI，43,704 star）、以及此前推送的 `chrome-devtools-mcp` 构成"桌面 / 浏览器"两套 computer-use 入口。

**值得关注的原因**
Computer-Use 的分歧点一直是"看屏幕"还是"读结构"。Windows-MCP 选了**读结构**，代价是只能吃 UI Automation 暴露的东西，收益是**不需要视觉模型、延迟与成本低一个量级、且能覆盖到 Win7**。这与 10-05 期 t3code 的"控制面与 harness 分家"、10-07 期 rea 的"按 Agent 想学什么重排工具目录"是同一思路：**把不可靠的感知换成可靠的接口**。

---

### 6. Leonxlnx/taste-skill — 把「审美」做成可移植技能，对抗 AI slop

**事件**：**taste-skill** 在 JavaScript 榜上榜（+338，**总 93,894**，forks 6,377），自称 "The Anti-Slop Frontend Framework for AI Agents"。

**核心内容**
- **纯技能形态**：可移植 Agent Skills，`npx skills add`（走 `vercel-labs/agent-skills` 的 CLI）一次安装全部技能，兼容 Codex / Cursor / Claude Code。
- **管的是"品味"而非功能**：升级布局、排版、动效、间距，目标是让 AI 生成的界面不再"千篇一律的模板感"。
- **额外含图像生成技能**：用于生成参考板（reference boards）——分 web / mobile / brand kit 三类；工作流是先用图像生成器出参考帧，再交给 Codex / Cursor / Claude Code 实现。
- **商业动作**：作者团队另开 **TasteCode**（`tastecode.dev`，本地桌面工作台，内置 design agent，brief → build → 视觉复核），开源在 `Leonxlnx/tastecode`。
- **明确的免责声明**：README 置顶"Taste Skill has no official token, coin, or crypto project"，凡用其名号的项目均无关联——延续了 10-08 calesthio/Crucix 同类声明的做法。
- 赞助方含 Sidrune AI、interfaces.dev、React Bits、IMG.LY、Sent.dm。

**值得关注的原因**
"输出形态/输出质量"作为独立赛道又添一例（前有 09-24 impeccable 的 61 条确定性设计规则、09-28 i-have-adhd 的 10 条可判定输出规则）。差别在于 taste-skill **把审美拆成"参考板（图）+ 实现约束（技能）"两段**，等于承认纯文本规则不足以约束视觉质量。同时 93.9k star 的总量说明这是真实需求而非话题热度。

---

### 7. koala73/worldmonitor — 实时全球情报仪表盘，且默认零 API key

**事件**：**worldmonitor** 在 TypeScript 榜上榜（+89，**总 88,103**，forks 13,443），AGPL-3.0。

**核心内容**
- **多流融合**：AI 新闻聚合 + 地缘政治监测 + 基础设施跟踪；**跨流相关性分析**（军事、经济、灾害、升级信号收敛）。
- **双地图引擎**：globe.gl 的 3D 地球与 deck.gl 的 WebGL 平面地图共用同一套图层目录。
- **硬指标产品化**：**Country Instability Index (CII) v8** —— 31 个 Tier-1 国家的实时分数、分档与约 24 小时变动量；另有 Finance radar（交易所、大宗、加密、市场合成指数）。
- **本地 AI 优先**："run everything with Ollama, no API keys required"。
- **单代码库多站点变体**：world / tech / finance / commodity / happy / energy 六个变体 + Tauri 2 桌面端（macOS / Windows / Linux）同一发布流程；多语言 UI 含原生语种 feed 与 RTL 支持，README 有简体中文版。
- **维护状态表**：README 明确列出各 surface 的 support status，告诉使用者"哪些接口可以安全依赖"。

**值得关注的原因**
把"公开数据 + 本地模型 + 多视图"做成一个可自托管的态势感知产品，与 09-28 gods-eye-view（浏览器写实地球 + 全公开数据）构成同一品类，但 worldmonitor 更进一步：**它把"不稳定指数"这种判断性输出做成了带版本号（v8）的公开指标**，并对每个 surface 标注维护状态——这是本期"边界可审计"主题在数据产品上的版本。

---

### 8. Tracer-Cloud/opensre — 为 AI SRE 造一个 SWE-bench

**事件**：**OpenSRE v0.1** 在 Python 榜上榜（+81，总 11,666，forks 1,707），Apache-2.0，标注为 public alpha。

**核心内容**
- **明确对标 SWE-bench 的缺口**：README 论证——SWE-bench 给编码 agent 提供了可规模化的训练数据与清晰反馈，而**生产事故响应至今没有等价物**（分布式故障更慢、更嘈杂、更难模拟与评测）。OpenSRE 要建的是"面向 agentic 基础设施事故响应的**开放强化学习环境** + 真实生产故障的端到端测试"。
- **连接 60+ 已有工具**：不替换你的监控/日志/追踪栈，只做上层。
- **三入口**：交互式 shell（REPL，slash 命令含 `/status`、`/cost`、`/sessions`、`/resume`、`/compact`、`/integrations list`、`/agents`）、headless CLI（`opensre ask "why is checkout-api slow?"`，可进 CI）、Python 内嵌 API（`start_embedded_session()`）。
- **测试目录有纪律**：`tests/e2e` 跑云上真实场景，且"保持语义化命名，让 e2e vs unit、local vs cloud 的边界一目了然"（`tests/README.md`）。
- 安装一行：`curl -fsSL https://install.opensre.com | bash -s -- -gh`（Windows 有 PowerShell 版）。

**值得关注的原因**
这是**"垂类 Agent 先解决评测"的又一例**（09-30 NVIDIA/SkillSpector 建技能漏洞基线、10-08 uber/ADR 建 ADR-Bench）。区别在于 OpenSRE 直接以 RL 训练环境为目标——**先把"怎么算做对了"变成可规模化的数据集，再谈 agent 能力**。SRE 是少数"证据天然分散在日志/指标/追踪/runbook/Slack 里"的领域，正是 Agent 该解但最难评的题。

---

### 9. Vincentwei1021/video-shotcraft — 视频生成从"提示词"转向"配方卡"

**事件**：**video-shotcraft** 在 TypeScript 榜上榜（+241，总 10,930，forks 974），定位是 Claude Code / Codex 的 Agent 技能。

**核心内容**
- **规模化的镜头库**：**157 张镜头配方卡 · 214 种风格 · 214 个动效预览**，外加一套可直接用的模板；用 Remotion 渲染真视频（真实页面捕获、2.5D 运镜、节拍对齐剪辑、电影级 SFX）。
- **Motion Workbench**：交付后开一个 CapCut 式浏览器工作台（`node workbench/scripts/open.mjs <project>`），影片被拆成 shot / transition / caption / SFX 轨道**且与创作时一致**；可在 schema 驱动面板改文案/字号/颜色，移动、裁剪、变速，从库中拖入 **216 个 demo 动效**，再用 Remotion 导出——**预览与渲染逐帧一致**。
- **一键换主题**：模板可在 Ink Press / Modern Light / Midnight / Sage / Coral / Iris / Deep Ocean / Obsidian Violet / Vintage Kraft 九种电影主题间切换且保留编辑。
- **同系列扩展**：**video-talkcraft**（解说视频），核心是**字级时间戳本地对齐（每字中位 20–40 ms）**、78 张解说动效配方卡、**7 层防幻灯片镜头系统**（连续相机曲线、视差平面、idle/yield 生命周期、呼吸感环境）、纯切字幕、三重 QA 门。
- 三语 README（英/中/日），另有 AtomGit 镜像。

**值得关注的原因**
这是**"把创作知识固化成可检索卡片"这一模式在视频领域的落地**：过去视频生成卖的是模型能力，现在卖的是 157 张配方 + 214 个动效 + 一个能改的工作台。配合 09-30 hyperframes（HTML→确定性 MP4）、10-05 OpenMontage（Backlot 渲染前审批门），可以看到**视频 Agent 的竞争点已经从"能不能生成"移到"产物能不能被精确修改"**——预览与渲染逐帧一致、工作台轨道与创作一致，都是在解决"不可回改"这个根本问题。

---

### 10. thedotmack/claude-mem v13.35.0 — 记忆检索改成「三步有界披露」

**事件**：**claude-mem v13.35.0 于今日 11:34（GMT+8）发布**（10-09 03:34 UTC），仓库在 daily 榜 +670（总 98,677，forks 8,651）。距 10-06 的 v13.34.2 三天，属已推送仓库的重大新版本。

**核心内容**
- **单一检索入口 `mem_search`，三步有界披露**：
  - **guided 模式（默认）**：回复自带 `mem-search step 1 of 3`（索引）→ `step 2 of 3`（最多 `maxDetails` 个选中锚点的上下文）→ `step 3 of 3`（一批细节）；每步末尾给可读的下一步指令与 `Continue with:` 游标，**Agent 可以提前停**。
  - **auto 模式**：一次调用内跑完三阶段，用**排序的词法检索**按"标题命中多少查询词"选锚点（忽略停用词与 prompt），无命中则去掉停用词重试一次；**全程零 LLM 调用**。
- **游标设计**：27 字符不透明游标（`ms_` + 24 个 URL-safe 字符）；检索范围、原始选项、已披露 ID 集合都存在**服务端有界状态**里，15 分钟过期——**Agent 不再在调用间搬运序列化的检索行**。游标不能换选项复用，`selectedIds` 必须来自上一轮回复；过期或外来游标返回人话错误要求重查。
- **上限全部写死**：索引 ≤20 行，`maxDetails` 默认 3 上限 5，`depthBefore/After` 默认 2 上限 3，查询 ≤500 字符 / 1 KiB。
- **工具回复改人类可读文本**：搜索、上下文、选中记录、原始工具调用、语料库操作、服务端观察等 MCP 回复不再返回 pretty-printed JSON 信封或重复的 `structuredContent`，改为索引 / 证据 / 写入回执 / 摘要。
- **新增 `save_memory`**：显式写入偏好、更正、决策、交接与可复用经验；**server runtime 下会在调用本地 worker 前拒绝**，指向 `observation_add`。
- **原生记忆桥（Claude Code + Codex）**：`PreToolUse` hook 现在识别原生记忆查找（`memory_search`、本地 `memory` 工具的读命令、以及 scoped 到 Claude Code 项目 `memory` 目录 / `autoMemoryDirectory` / Codex `memories` 目录 / 配置的 note root 的 Read·Grep·Glob·Bash），命中后**附加一次同主题 `mem_search` 结果作为额外上下文**，原生工具照常执行。附加内容上限 10,000 字符，且**框定为"检索到的数据，不得提供指令"**，JSON 形态的旧 worker 回复直接丢弃；worker 不可用时 hook 让路。
- **opt-in Markdown 笔记监听**：`CLAUDE_MEM_MEMORY_WATCH_ROOTS` 最多 8 个 `{path, project, platformSource}`，**默认空、绝不自动扫全项目或全局 Codex 记忆**；轮询等待内容稳定才导入，跳过隐藏文件 / 符号链接 / >64 KiB 文件；每次读取绑定到根内被校验过的确切文件（**防链接/移动/换父目录绕过**），永不改写源文件、零模型调用；编辑按 revision 存储，内容指纹去重，删源不删档。
- **检索不再观察自己**：对 claude-mem 自身 search/context 工具与原生 `memory_*` 查找的调用**被排除在观察采集之外**——"搜记忆"不再生成关于"搜记忆"的新记忆；显式 `save_memory` 写入保留回执但不重复生成第二条观察。
- **三个开关**：`CLAUDE_MEM_MEMORY_INSTRUCTIONS_ENABLED`、`CLAUDE_MEM_MEMORY_SEARCH_HOOK_ENABLED`、`CLAUDE_MEM_MEMORY_WATCH_ROOTS`。

**值得关注的原因**
记忆层连续第五期在榜，本期提交方向**全部集中在"读取的边界"**：披露分步、状态有界、上限写死、游标不可复用、hook 让路、监听默认空、检索不自我观察。这与 10-01 期提出的"上下文经济两个账（处理量 vs 驻留量）"呼应——**本期解决的是驻留量里的第三类：检索自身产生的副作用**。另外"附加内容不得提供指令"是把 09-30 期 SkillSpector 记录的**记忆投毒**攻击面写进了实现约束。

---

## 三、其他趋势速览

**已推送仓库今日/近日新版本**
- **DietrichGebert/ponytail v5.1.0**（10-09 00:20 GMT+8）— **不再把自己的名字写进用户代码**：刻意走捷径处改用中性注释 `shortcut: <the limit>, <when to upgrade>`；`/ponytail-debt` 仍能找到旧的 `ponytail:` 标记所以账本不丢；可用 `CLAUDE.md`/`AGENTS.md` 自定义或禁用该词。**发布前用 5.0.0 对照实测：标记数、通过率、成本三项均相同**（自证"改名不伤性能"）。
- **morluto/rea v6.1.0**（10-09 09:08 GMT+8）— 从 10-07 的 v4.1.0 两天跳到 6.x。**两处破坏性变更**：Hopper 正则模式改用 ECMAScript Unicode 语法（替代 Python re），匹配跑在**可取消 worker + 5 秒 deadline** 里，literal 模式保留 Unicode casefold；**移除 `set_current_document`**，改用 `open_binary` 切目标。新增 Grok Build / Grok Bot 注册；大量 apple / browser / artifacts 边界修复（keyed archive 整数精度、source-map 嵌套列偏移、Windows 脚本清单根归一化）。
- **vectorize-io/hindsight v0.10.3**（10-09 07:47 GMT+8，自 09-29 的 v0.10.2 后首个版本）— `fix(coding-agents): hold the deepen lock with a heartbeat, not a 30-minute TTL`（**用心跳持有加深锁替代 30 分钟 TTL**）；`treat memory as a past record, and let teams add their own guidance`；新增 **TraeCode (TRAE CN) harness**；过滤 Codex 非会话内容。
- **NVIDIA/OpenShell v0.1.3-pre.7**（10-09 13:49 GMT+8）+ Development Build（10-09 13:49）— `feat(ocsf): emit full JSON records to supervisor stderr`（OCSF 事件全量 JSON 输出到 supervisor stderr，并保留控制台记录边界）；pre.6 加了**维护者审批闸门的两个 stdlib 辅助脚本**（`check_maintainer_approval.py` 折叠每个 reviewer 的最新决定性立场，非 approval 即非零退出，**无 handle 时 fail closed**）。
- **anthropics/claude-code v2.1.295**（10-09 03:48 GMT+8；另有 2.1.293 / 2.1.294）— 距 10-05 记录的 v2.1.289 已连发多版。
- **earthtojake/text-to-cad v0.7.19**（10-09 09:41 GMT+8；10-08 已发 0.7.17/0.7.18）。
- **mvschwarz/openrig v0.6.7**（10-08 20:46 GMT+8）；**earendil-works/pi v1.1.0**（10-08 06:26）；**agent-substrate/substrate v0.4.0**（10-08 08:15）；**paperclip canary/v2026.1009.0-canary.0**（今日）；**heygen-com/hyperframes v0.8.143**（10-09 07:51）；**trycua/cua nightly-lume 0.6.2-nightly.20261009**。
- 无新版本：Tencent/WeKnora 仍 v0.8.2（09-24）、dream-num/univer 最新仍 09-29、mattpocock/skills 仍 v1.3.1（10-04）。

**新面孔（未展开）**
- **vercel-labs/agent-browser**（Rust，+69，**总 43,704**，Apache-2.0）— Vercel Labs 的浏览器自动化 CLI，**原生 Rust 二进制**，`npm i -g agent-browser` / Homebrew / Cargo 三路安装，首跑从 Chrome for Testing 下浏览器；v0.38.2（10-01）。与 Windows-MCP 构成"浏览器 / 桌面"两套 computer-use 入口。
- **facebook/rebalancer**（C++，+60，总 362）— Meta 开源的**分配问题求解器**（DSL + 库，C++/Python 接口）；本地搜索与 MIP（支持 FICO Xpress / Gurobi / 开源 HiGHS）双路；单进程多线程可处理约 100 万对象/容器；设计见 **OSDI 2024 论文**《Optimizing Resource Allocation in Hyperscale Datacenters》，已在 Meta 用于硬件与服务器分配、ML 训练/推理放置、流量路由、负载均衡迁移。
- **ItzCrazyKns/Vane**（TS，+44，总 37,168，MIT）— 隐私优先的 AI 回答引擎，完全跑在自己硬件上；SearxNG 搜索、Ollama 本地 LLM 或 OpenAI/Claude/Gemini/Groq；三档搜索模式（Speed / Balanced / Quality）；引用来源、图视频搜索、文件上传、指定域名搜索；Docker 镜像。
- **stacklok/toolhive**（Go，+8，总 2,255，Apache-2.0）— 企业级 MCP 平台：**每个 MCP server 跑在隔离容器里 + 最小权限文件（无本地凭证）**；**语义化工具检索号称省最多 85% token**；带 K8s operator 与 IdP / OTel 集成；主打"自托管 MCP registry 与 gateway，避免 shadow MCP"。
- **op7418/guizang-ppt-skill**（HTML，+70，总 27,455）— 中文 HTML 单文件横向翻页 PPT 技能，内置两套视觉系统（电子杂志×电子墨水 / 瑞士国际主义），含 PPT 配图、多平台封面、完整排练与演讲者模式；作者把踩过的坑写进 `checklist.md`；`npx skills add` 安装，Claude Code / Codex 均支持。
- **github/awesome-copilot**（JS，+41，总 39,826）— GitHub 官方的 Copilot 自定义资源集合（agents / instructions / skills / hooks / workflows / plugins），另有 cookbook 与 **machine-readable `llms.txt`** 供 Agent 消费。
- **bmad-code-org/BMAD-METHOD**（Python，+51，总 53,966，MIT）— Agile AI-Driven Development 方法论，交付环 Clarify → Plan → Build & verify → Learn and adjust；支持 skills CLI / Claude Code 插件 / Codex 插件三条安装路线。
- 其他：**liquidslr/system-design-notes**（+393，daily 唯一新面孔，系统设计面试书笔记）、**scholay/rimes**（Swift，+253，现代 macOS 输入法 librime + buffer workbench）、**DmNote-App/DmNote**（TS，+263，DJMAX 键位查看器）、**IAmTomShaw/f1-race-replay**（Python，+148）、**microsoft/mxc**（已详述）、**traces-ai/burn**、**edwardkim/rhwp**（Rust+wasm 的 hwp 查看编辑器）、**HakanSeven12/OpenCADStudio**（Rust CAD）、**martin-olivier/airgorah**（Rust WiFi 安全审计）、**vercel-labs/agent-browser**、**llm-d/llm-d-router** 与 **kai-scheduler/KAI-Scheduler**（推理/K8s 调度层）。

---

## 四、当日主线判断

1. **基础设施厂商同日集体落子 Agent 运行时**——Docker 给运行时 + OCI 分发，微软给可嵌入沙箱 SDK（mxc）+ 统一框架（MAF），OpenAI 给安全闭环（codex-security）。**共同点：都不做模型，做的是"Agent 跑在哪、怎么分发、怎么审计"。**
2. **隔离层不再自造，只做统一策略面**——mxc 把隔离委托给 bubblewrap/seatbelt/processcontainer/microVM，自己只提供文件/网络/UI 三套策略与 typed SDK。这与 agent-sandbox 委托 RuntimeClass→gVisor/Kata 完全同构，**"编排、隔离、策略"三层分工已经稳定**。
3. **Agent 分发格式之争出现第三条路**——SKILL.md（技能）、各家 plugin marketplace（插件）、现在 OCI registry（Docker Agent）。Docker 选择复用既有标准而非另造，代价是绑定容器。
4. **Computer-Use 分化为"读结构"与"看屏幕"两派且同日同榜**——Windows-MCP（UI Automation，不依赖视觉，覆盖 Win7–11）vs agent-browser / chrome-devtools-mcp（浏览器侧）。**读结构这一派在成本与可靠性上占优，代价是覆盖面受限于接口暴露程度。**
5. **记忆层的战场移到"读取的边界"**——claude-mem v13.35.0 把披露分步、状态有界、游标不可复用、hook 让路、监听默认空、检索不自我观察一次性做完；配合 hindsight 的"用心跳持有锁替代 TTL"，**"跨轮状态保真是最大 bug 来源"这条规律第四次被验证**（前三次：prompt-cache 回归、评论丢失、档位静默失效）。
6. **诚实披露从"修正数值"升级为"修正表述"**——ponytail v5.1.0 改名后主动对照 5.0.0 证明"标记数/通过率/成本不变"；mxc 的 `--audit` 用 Warning 说明它会关掉全部沙箱安全；codex-security 明说 findings service 无鉴权。**"自证不伤性能"与"主动标注危险开关"成为发版常规动作。**
7. **垂类 Agent 一律先建评测/基线再谈能力**——OpenSRE 直接以"AI SRE 的 SWE-bench"为使命（RL 环境 + 端到端故障测试），接续 SkillSpector 的技能漏洞基线、ADR 的 ADR-Bench。**"先定义怎么算做对了"已成为垂类 Agent 项目的入场门槛。**
8. **"审美/品味"被拆成参考板 + 实现约束两段**——taste-skill（图像生成参考板 + 布局排版动效技能）与 video-shotcraft（157 张镜头配方卡 + 可改工作台）同日同榜，说明**纯文本规则不足以约束视觉质量，需要可检索的卡片库 + 可回改的产物**。
9. **判断性输出开始带版本号与维护状态**——worldmonitor 的 CII v8（31 国 24h 变动）+ 各 surface 的 support status 表，把"这个指标会变、这个接口能依赖"写进产品界面。**数据产品也开始做边界可审计。**
10. **非 Agent 项目 4/10**（mxc 属安全基础设施、worldmonitor 属情报可视化、video-shotcraft 属创作工具、facebook/rebalancer 属运筹优化），与 09-28~10-08 的 4–6/10 区间持平。本期特点是**大厂官方项目占比显著升高**（微软 2、Docker 1、OpenAI 1、GitHub 1、Vercel 1、Meta 1）。

---

*生成时间：2026-10-09 14:00 (GMT+8) · 数据抓取时点同上*
