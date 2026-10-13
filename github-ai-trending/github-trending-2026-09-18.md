# GitHub 趋势日报 · 2026-09-18

> 数据源：github.com/trending（daily 视图）｜筛选口径：当日新增 Star 高、技术方向有代表性、具备工程参考价值
> 去重说明：本期 10 条详细条目均为**上期未展开**的仓库；上期已推送仓库的当日新动态单独归入文末「上期条目新动态」章节。

---

## 今日榜单速览

| # | 仓库 | 语言 | 总 Star | 今日 +Star | 状态 |
|---|------|------|---------|-----------|------|
| 1 | cloudflare/security-audit-skill | JavaScript | 11,126 | +3,607 | 上期已推 |
| 2 | alibaba/open-code-review | Go | 35,437 | +3,286 | 上期已推 |
| 3 | Tencent/BrowserSkill | TypeScript | 4,518 | +1,302 | **新增** |
| 4 | affaan-m/ECC | JavaScript | 261,342 | +1,171 | 上期已推 |
| 5 | Tencent/WeKnora | Go | 26,534 | +1,125 | 上期已推 |
| 6 | alphaXiv/OpenResearch | Rust | 5,093 | +939 | 上期已推 |
| 7 | NationalSecurityAgency/ghidra | Java | 78,648 | +912 | 上期已推 |
| 8 | JustVugg/colibri | C | 35,861 | +873 | 上期已推 |
| 9 | abue-ammar/tinycast | Swift | 6,234 | +739 | 上期已推 |
| 10 | addyosmani/agent-skills | JavaScript | 95,988 | +680 | **新增（详）** |
| 11 | jamiepine/voicebox | TypeScript | 54,945 | +667 | **新增（详）** |
| 12 | anthropics/claude-code | TypeScript | 145,951 | +538 | **新增** |
| 13 | ever-co/ever-gauzy | TypeScript | 7,630 | +470 | 上期简提 |
| 14 | cline/cline | TypeScript | 68,614 | +380 | **新增** |
| 15 | TencentCloud/Octop | Python | 3,614 | +367 | **新增** |
| 16 | roboflow/supervision | Python | 50,864 | +329 | **新增** |
| 17 | anthropics/knowledge-work-plugins | Python | 24,633 | +287 | **新增** |
| 18 | n8n-io/n8n | TypeScript | 205,111 | +281 | **新增** |
| 19 | coder/coder | Go | 14,939 | +145 | **新增** |
| 20 | cilium/cilium | Go | 25,308 | +111 | 新增（未展开） |

**今日最大变化**：榜单前 9 名中有 8 个是上期已出现的仓库，热度延续性极强；但**新增入场者集中在"Agent 与真实环境/真实工作流对接"这一层**——浏览器、语音、远程主机、云端开发环境、企业职能插件，全部指向同一个问题：Agent 怎么进入真实的生产环境。

---

## 1. Tencent/BrowserSkill ⭐+1,302（总 4,518）

**事件**：腾讯开源 BrowserSkill，让 AI Agent 直接使用你**已经登录的真实浏览器**，且不打断你正在做的事。MIT 许可。上线首日 +1,302 Star，冲进 Trending 前三。

**核心内容**
- **架构是三层本地路由**：Agent harness → `bsk` CLI → 本地 daemon（`127.0.0.1` 上的 WebSocket）→ 浏览器扩展 → **Agent Window**。Agent 永远不直连浏览器，只通过 shell 调 `bsk`。
- **不干扰用户**：任务在独立的、可见的 Agent Window 中执行，你自己的浏览器窗口不受影响；需要操作你已打开的标签页时必须**显式借用（borrow）**，任务完成归还。
- **复用真实登录态**：无需为 Agent 单独建测试账号，直接操作已登录的站点——这是它能做真实业务自动化的关键前提。
- **零框架锁定**：任何具备 shell 能力的 Agent 都能用。官方列出 Cursor、Claude Code、Codex、OpenClaw、CodeBuddy、WorkBuddy、Pi、Hermes Agent，以及 DeepSeek Harness（通过 npm 一等插件 `@wxg-prc-cpg/browser-skill-dsh-plugin` 提供原生 `browser_*` 工具）。
- **人机协作内建**：遇到验证码、登录、确认对话框等只有人能做的步骤，Agent 可请求接管（`request-help`），完成后继续。
- **安全模型的关键设计——权限的权威源在浏览器，不在 CLI**。0.3.0 起，`--unattended`、`tab borrow --no-confirm`、`BSK_REQUEST_HELP=off` 全部**不能再绕过确认**，仅保留参数兼容；扩展弹窗里「借用前确认」和「允许请求人类帮助」两个开关默认全开，且**按浏览器 profile 保存，对所有会话生效**。
- **工程细节**：Cargo + pnpm workspace；`bsk doctor` 做连接诊断；skill 自动更新仅在内容与上次安装版本一致时执行，**本地编辑会被保留并暂停自动更新**；协议 1.3 与 1.0–1.2 保持连接兼容；扩展支持中/英/韩三语。
- 附带 `evals/browser`：确定性本地页面 + **Agent 中立的浏览器能力评测**。

**值得关注的原因**：这是"Agent 用真实浏览器"这个需求第一个把**安全边界设计清楚**的开源实现。此前这一层要么靠 Playwright 起干净实例（拿不到登录态），要么靠各家 Agent 自带的浏览器工具（权限模型模糊）。BrowserSkill 给出了第三条路：**复用真实登录态，但把授权权威放在浏览器扩展而非命令行**——用户在自己熟悉的地方一次设定，Agent 无法用参数覆盖。对做 RPA、Web 自动化、Agent 工具链的团队，"CLI→daemon→扩展"三层路由 + "权威源在客户端"的权限模型，是可以直接抄的架构。另外它显式支持 WorkBuddy/CodeBuddy/DeepSeek Harness，是国内 Agent 生态互操作性的一个正面信号。

---

## 2. addyosmani/agent-skills ⭐+680（总 95,988）

**事件**：Addy Osmani（Google Chrome 团队）出品的 AI 编码 Agent 工程技能集持续走高，现为 **25 个技能 + 9 个 Slash 命令 + 4 个专家 Agent 角色 + 7 份检查清单**，MIT 许可。

**核心内容**
- **技能按软件生命周期六阶段组织**：`DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP`，对应命令 `/spec /plan /build /test /review /ship`（另有 `/constraints`、`/webperf`、`/code-simplify`）。
- 25 个技能中值得单独点出的几个：
  - `interview-me`：**一次只问一个问题**地访谈用户，直到约 95% 置信度才停——直接针对"Agent 猜需求"这个通病。
  - `constraint-driven-development`：先访谈确立质量标准，写出 `CONSTRAINTS.md`，**防止 Agent 为了通过检查而关掉检查或跳过测试**。
  - `doubt-driven-development`：对每个非平凡决策做**对抗式全新上下文审查**（CLAIM → EXTRACT → DOUBT → RECONCILE → STOP）。
  - `source-driven-development`：每个框架决策都必须基于官方文档，要**引用来源**，未经验证的内容要显式标记。
- **反合理化（anti-rationalization）是贯穿设计**：每个技能都带一张"借口表"，列出 Agent 跳过步骤时的常用借口（如"我稍后再补测试"）及对应反驳论据。
- **技能统一结构**：`Overview / When to Use / Process / Rationalizations / Red Flags / Verification`——最后一项是硬性的**证据要求**（测试通过、构建输出、运行时数据），"看起来对了"不算。
- **理论来源明确**：Google 工程实践——《Software Engineering at Google》中的 Hyrum's Law、Beyonce Rule、测试金字塔（80/15/5）、变更规模约 100 行、Chesterton's Fence、主干开发。
- **分发覆盖面极广**：`npx skills add addyosmani/agent-skills` 可装到 70+ Agent；另有 Claude Code 插件市场、Gemini CLI、Codex 插件（v0.122+）、Antigravity CLI、Cursor、Windsurf、OpenCode、Copilot、Kiro 的原生适配目录。

**值得关注的原因**：技能类项目大多停留在"提示词模板合集"，这个是**把资深工程师的判断力结构化成可执行流程**。两个设计特别值得借鉴：一是"反合理化借口表"——它承认 Agent 会找捷径，并把这些捷径预先写成可反驳的文本；二是"验证不可协商"——每个技能以证据要求收尾，把"完成"定义成可核验的事实而非模型的自述。对做 Agent 质量治理、代码规范落地的团队，这 25 个技能文件是可以直接拆开复用的素材库。

---

## 3. jamiepine/voicebox ⭐+667（总 54,945）

**事件**：开源 AI 语音工作室 Voicebox 热度持续攀升，定位是 **ElevenLabs + WisprFlow 的一体化免费开源替代**，MIT 许可，全部本地运行。

**核心内容**
- **补齐了语音 I/O 的完整闭环**：ElevenLabs 只做输出（TTS）、WisprFlow 只做输入（听写），Voicebox 两者兼做，并用一个**捆绑的本地 LLM（Qwen3）**把两端桥接起来（用于听写文本精炼和语音人格化）。
- **克隆与合成**：零样本克隆只需几秒音频；**7 个 TTS 引擎**可按次切换（Qwen3-TTS、Qwen CustomVoice、LuxTTS、Chatterbox Multilingual、Chatterbox Turbo、TADA、Kokoro），覆盖 **23 种语言**，另有 50+ 精选预设声音。
- **听写**：全局热键支持按住说话/切换两种模式；macOS 下自动粘贴到聚焦文本框，并做**原子化剪贴板保存/恢复**；STT 基于 Whisper（MLX 或 PyTorch）。
- **创作**：Stories Editor 多轨时间线（对话、播客、叙事），支持拖拽、内联裁剪/分割、每轨版本固定；**无限长度生成**（按句边界分块 + 交叉淡入淡出，上限 50,000 字符）；8 种基于 Spotify `pedalboard` 的后处理效果（音高、混响、延迟、合唱、压缩、增益、高低通）。
- **Agent 集成是重点**：内置 MCP Server（4 个工具），`voicebox.speak` 让任意支持 MCP 的 Agent（Claude Code、Cursor、Cline、Windsurf）**用你克隆的声音说话**；支持把 Claude Code 绑定到某个语音、Cursor 绑定到另一个；语音人格由本地 Qwen3 驱动，提供 Compose（生成角色化台词）与 Speak in character（改写为角色语气再 TTS）。
- **工程栈**：Tauri（Rust）而非 Electron，前端 React + TS，后端 FastAPI（Python），REST API 默认绑定 `127.0.0.1:17493`，SQLite 存储；GPU 后端覆盖 MLX / CUDA / ROCm / DirectML / IPEX-XPU / CPU。
- **一个 LLM、一份显存**：同一个 Qwen3（0.6B/1.7B/4B）同时服务听写精炼和语音人格，共享运行时与模型缓存。

**值得关注的原因**：它把"本地语音栈"这件事做完整了——不是单点模型，而是**从麦克风到扬声器的全链路，且全部离线**。更关键的是 `voicebox.speak` 这个 MCP 工具：它把"Agent 说话"变成了一个标准接口，让语音从"给人听"变成"Agent 输出通道的一部分"。对做语音应用、无障碍交互、多模态 Agent 的团队，它展示了两个可复用的思路——**用同一个本地小模型同时承担多个人格化任务以节省显存**，以及**用 MCP 把语音能力做成 Agent 的通用工具而非某个应用的私有能力**。

---

## 4. anthropics/claude-code ⭐+538（总 145,951）

**事件**：Claude Code 重新冲上趋势榜，伴随 **v2.1.274 / v2.1.275 / v2.1.276** 三个版本在 48 小时内连续发布（含一次紧急热修复）。

**核心内容**
- **记忆能力连续两版强化**：修复记忆文件"年龄标注"在压缩/恢复后变化导致 **prompt 缓存未命中**的问题（直接影响成本）；VSCode 端新增 Memory 与 Instructions 入口，可查看、编辑、删除已保存记忆与自动记忆开关。
- **插件安全显著收紧**：从 npm 源安装插件改用 `npm pack --ignore-scripts` 拉取并做完整性校验，**不再执行包的 install 脚本**；修复插件/marketplace 日志中泄露 git/ssh URL 里密码与 token 的问题。
- **新增 claude.ai 账户同步**：把网页端启用的 skills 与 plugins 同步到终端会话，可分别用 `syncClaudeAiSkills: false` / `syncClaudeAiPlugins: false` 关闭。
- **企业/网关能力**：Claude apps gateway 新增登录账户确认、`store.connect_timeout_seconds`、SIGTERM 时最多 25 秒在途请求排空（`CLAUDE_GATEWAY_DRAIN_TIMEOUT_MS`）；spend-limit 检查从 4 次数据库往返压到 1 次；自托管 runner 修复 token 刷新失败后每轮 401 的问题。
- **MCP 侧**：新增 `CLAUDE_CODE_MCP_STARTUP_WAIT_MS` 限制首轮等待 MCP 连接的时间；修复 Streamable HTTP MCP 工具调用被硬编码在约 5 分钟超时的问题；Bedrock/Vertex/Foundry 默认切换到 v2 MCP 客户端与 **MCP 2026-07-28** 协议协商。
- **Agent 体验**：新增 `ctrl+enter` 打断当前轮次并一次性发送所有排队消息；`/code-review` 改为精简的 inline 审查提示，不再派生大量审查子代理。
- **修复大批量问题**：恢复会话因畸形转录崩溃、Grep/Glob 大搜索挂起或 OOM、全屏模式冻结、worktree 隔离会话接受嵌套 shell 展开（改为拒绝）等。
- 注意：v2.1.275 引入了网关场景下 `400 Input tag 'advisor_20260301'` 的回归，v2.1.276 已热修复，**建议直接用 2.1.276**。

**值得关注的原因**：这份变更日志是观察"**Agent CLI 正在从编码工具变成企业基础设施**"的最好样本。三个信号很明确：①记忆被当成需要维护缓存一致性的工程对象（而不是提示词拼接）；②插件安装被当成**供应链攻击面**来治理（禁 install 脚本 + 完整性校验 + 凭证泄露修复）；③网关、排空、消费限额、OpenTelemetry 这些词密集出现——这是服务端基础设施的语汇，不是编辑器插件的语汇。对自建 Agent 平台的团队，它的企业特性清单可以直接当作需求对照表。

---

## 5. cline/cline ⭐+380（总 68,614）

**事件**：Cline 两条发布线同日推进——桌面端 **desktop-v0.0.31**（引入 SSH 远程开发）与 **desktop-v0.0.32**（20 小时后热修复启动崩溃），VS Code 扩展端发布 **v4.1.19**。

**核心内容**
- **桌面端新增 SSH 远程开发**：应用本体留在本地，可对远程机器操作。Agent 工具、工作区发现、Git 元数据、会话持久化**全部在远端主机运行**，只通过隧道转发已认证的 Cline Hub 协议。支持 SSH config 别名；主机元数据存于 `~/.cline/data/settings/remote-environments.json`（权限 `0600`，**只记身份文件路径，不存私钥内容**）；首次连接自动上传自包含 helper 到 `~/.cline/remote/`，**无需 apt / npm / root / 全局 CLI / 公网端口**。限制：远程会话暂不支持文件附件与本地编辑器打开远程文件。
- **子代理并行执行**：同一步骤中派生的子代理改为并行运行（此前串行），显著缩短多任务耗时；仅紧邻的并行调用会重叠，有序工具仍按序执行。
- **desktop-v0.0.32 修复了一次典型的构建漂移事故**：应用后台会跑自己的 Cline Hub 副本，但 app 与 Hub 由同一代码的不同副本构建，导致 Hub 声明的构建标识与应用预期不一致 → 应用关掉自己刚启动的 Hub → 启动超时报 `No compatible hub runtime is available`。修复方式是让两部分加载同一份代码副本，并**把真实编译产物的端到端启动测试纳入 CI**。
- **v4.1.19 的重点在安全与上下文**：
  - 修复 Windows 上工作区内植入的 `rg.exe` / `git.exe` / `powershell.exe` 被优先执行的问题（启动时设 `NoDefaultCurrentDirectoryInExePath`）——典型的**二进制劫持防御**。
  - 长任务上下文压缩触发逻辑修复：原逻辑按约 3 字符/token 粗估，对反汇编、图片转储、压缩源码这类高密度内容严重失准导致压缩不触发；现改为同时采用提供商上报的 token 数。
  - `apply_patch` 不再静默覆盖已存在文件；凭证保存时移除不可见字符（覆盖 AWS/GCP/SAP 字段与自定义 header）。
  - 中断重试：临时提供商错误导致的中途失败最多重试 3 次（带退避），已输出内容的回合不重试。
  - 内置模型目录从 5,788 增至 **6,079**，新增 4 个提供商；44 个提供商的默认模型变更（多数指向 DeepSeek V4.1 Flash）。
  - 默认在支持该功能的模型上开启网页搜索（YOLO 模式除外）。

**值得关注的原因**：这期更新里有两个**可以直接搬到自己项目里的教训**。第一是安全侧：`NoDefaultCurrentDirectoryInExePath` 这个修复——当 Agent 的工作目录是被克隆或下载的代码时，"当前目录优先"就是一个可利用的二进制劫持入口，任何在 Windows 上跑 Agent 的项目都该检查这一点。第二是工程侧：v0.0.32 那个"同一代码的两份副本构建出不一致标识"的 bug，根因不是逻辑错误而是**构建产物漂移**，修复手段是把真实产物纳入 CI 端到端测试——这是所有做多进程/多组件桌面 Agent 的团队都会踩的坑。此外，上下文压缩从"字符粗估"改为"采用提供商上报 token 数"也是一条通用经验：**token 估算不要自己拍脑袋，用服务端的真实计数**。

---

## 6. TencentCloud/Octop ⭐+367（总 3,614）

**事件**：腾讯云开源自托管 AI 助手平台 Octop，**1.0.0** 正式版，MIT 许可。定位是"给家庭和小型团队用的、可并行运作的数字生命体"。

**核心内容**
- **单进程架构是它最硬的技术选择**：不用外部队列或消息代理，Web UI、IM、cron **全部通过进程内的同一个 `HarnessProcessor` 路由**；所有状态在启动时从控制面数据库重建，因此**重启安全**。依赖注入根是 `SharedServices`，`UserManager` 下挂每用户的 `HarnessAgentManager`，再下挂每 Agent 的 `AgentRuntime`。
- **多用户 + 多 Agent**：一个 admin 服务整个家庭/团队，基于 JWT 隔离，每用户拥有独立 Agent 与工作区；每个 Agent 有**自己的工作区、provider、channel 和 cron**。
- **MBTI 人格系统**：16 种人格模板 + 交互式测验，为每个 Agent 赋予独立性格——在自托管助手里相当罕见。
- **双向 ACP 集成**：既能作为 ACP 服务器被外部工具调用（`octop acp --agent main`，供 Zed / OpenCode 使用），也能**委托给外部编码 Agent**（OpenCode、CodeBuddy、Claude Code、Codex），带权限门控。
- **交互面齐全**：Web Dashboard（React 18 + TS + Vite + Ant Design）、CLI（`octop run/chat/acp`）、HTTP/SSE/WebSocket API；另有**终端 AI+**（浏览器内交互式 shell）、**浏览器 AI+**（无头 Chromium）、**远程桌面**（Linux/Windows/macOS 实时屏幕与输入）。
- **安全设计**：JWT 多用户隔离、工具审批、Shell 命令防护栏（规则可编辑，位于 `~/.octop/security/tool_guard/`）、**PII 脱敏在数据离开工作区之前完成**。
- **记忆可移植**：由 `harness-memory` 驱动，记忆随工作区迁移，而非绑定在独立服务上。
- **部署极简**：安装脚本用 `uv` 在 `~/.octop/` 下建隔离 venv，**无需预装 Python**；支持一行脚本（macOS/Linux/Windows）、PyPI、Docker、以及桌面应用产物（Windows NSIS、macOS DMG、Linux tar.gz，甚至 **FnOS NAS 的 .fpk 包**）。三步启动：`octop init` → `octop run` → 访问 `127.0.0.1:8088`。
- **模型支持**：OpenAI 兼容 API、DashScope（通义千问）、Ollama 及其他预设；支持本地 ONNX 嵌入模型。
- **路线图**：共享资源池、专家共享、浏览器技能**录制回放**、AgentTeams（协调者自主调度多个专家）、自进化（把日常对话提炼为可复用技能）、原生桌面与移动客户端。
- 附带生态：`harness-agent` / `harness-gateway` / `harness-memory` / `harness-browser` 正在准备开源。

**值得关注的原因**：多数自托管 AI 助手是**单人单 Agent**的思路，Octop 直接把坐标系换成"多用户 + 多 Agent + 可并行"，并且用**单进程 + 启动时重建状态**这个反直觉的方案换来重启安全——省掉了外部消息代理，代价是所有并发压力都压在一个进程里。这个取舍是否成立要看规模，但对家庭/小团队这个量级是合理的。另外两个细节值得注意：一是 PII 脱敏被放在"数据离开工作区之前"而不是"日志写入之前"，位置选得更前；二是它同时提供**入站和出站 ACP**，意味着它既能当 Agent 平台也能当 Agent 编排层。对做私有化 AI 助手、多租户 Agent 平台的团队，这是目前国产开源里架构文档最完整的一份参考。

---

## 7. roboflow/supervision ⭐+329（总 50,864）

**事件**：Roboflow 的计算机视觉工具库 Supervision 重新上榜。它是 CV 领域最常用的"模型之上那一层"。

**核心内容**
- **定位明确：模型无关（model agnostic）的工具箱**。任何分类、检测、分割模型都能接入，提供从数据加载到实时区域计数的构建块。
- **三块能力**：
  - **Models 连接器**：为 Ultralytics、Transformers、MMDetection、Inference 等主流库提供转换器，统一返回 `sv.Detections`；`rfdetr` 等新库已原生返回该类型。
  - **Annotators（标注器）**：高度可定制，可自由组合出所需可视化（`BoxAnnotator` 等），是它最被广泛使用的能力。
  - **Datasets 工具**：在 YOLO / Pascal VOC / COCO 三种格式间**加载、切分、合并、保存、转换**，全部支持按需加载（`__getitem__` 惰性读图），能直接 `merge` 两个类别空间不同的数据集。
- **安装**：`pip install supervision`，要求 Python ≥ 3.10。
- 配套资源完善：Roboflow notebooks、inference、autodistill、multimodal-maestro；Hugging Face Space 可在线试标注器；另有 cheatsheet、cookbooks、end-to-end examples。
- 典型教程场景：**停留时间分析**（目标检测 + 追踪 + 区域计时，用于零售/交通）、**车速估计**（YOLO + ByteTrack + 透视变换）。

**值得关注的原因**：这是本期榜单里**唯一一个非 Agent 项目**，而上榜本身就是一个信号——在 Agent 话题占据几乎全部注意力的当下，CV 工程的基础设施仍在被大量使用。它的价值在于"**把模型和业务之间那层胶水标准化**"：检测结果统一成 `sv.Detections` 之后，追踪、区域计数、标注、数据集格式转换全部变成可组合的积木，换模型不用重写业务逻辑。对做视频分析、工业质检、零售客流、自动驾驶感知数据管线的团队，它是省时间的默认选择。顺带一提，`multimodal-maestro` 这个配套项目正在把 CV 能力接入多模态 Agent——这是 CV 与 Agent 两条线开始交汇的地方，值得留意。

---

## 8. anthropics/knowledge-work-plugins ⭐+287（总 24,633）

**事件**：Anthropic 开源 **11 个面向知识工作者的插件**，为 Claude Cowork 打造，同时兼容 Claude Code。

**核心内容**
- **11 个插件按职能划分**：productivity、sales、customer-support、product-management、marketing、legal、finance、data、enterprise-search、bio-research，外加一个 `cowork-plugin-management`（用来创建和定制新插件）。
- **每个插件绑定一套 Connector**，这是它区别于普通提示词模板的核心。例如：
  - `sales`：Slack、HubSpot、Close、Clay、ZoomInfo、Notion、Jira、Fireflies、Microsoft 365
  - `finance`：Snowflake、Databricks、BigQuery、Slack、Microsoft 365
  - `bio-research`：PubMed、BioRender、bioRxiv、ClinicalTrials.gov、ChEMBL、Synapse、Wiley、Owkin、Open Targets、Benchling
  - `product-management`：Slack、Linear、Asana、Monday、ClickUp、Jira、Notion、Figma、Amplitude、Pendo、Intercom、Fireflies
- **统一目录结构**：`.claude-plugin/plugin.json`（清单）+ `.mcp.json`（工具连接）+ `commands/`（显式触发的 Slash 命令）+ `skills/`（Claude 自动取用的领域知识）。
- **纯文件、零代码**：全部是 Markdown 和 JSON，没有代码、没有基础设施、没有构建步骤。
- **安装**：Cowork 里从 claude.com/plugins 安装；Claude Code 里 `claude plugin marketplace add anthropics/knowledge-work-plugins` 然后 `claude plugin install sales@knowledge-work-plugins`。安装后技能按相关性自动触发，Slash 命令形如 `/sales:call-prep`、`/data:write-query`、`/finance:reconciliation`。
- **官方明确定位为"起点而非成品"**：建议企业替换 `.mcp.json` 指向自己的工具栈、把公司术语与组织流程写进技能文件、按团队实际做法改工作流。

**值得关注的原因**：这是"**Agent 插件 = 技能 + 命令 + 连接器**"这个三元组第一次被平台方用 11 个真实职能场景完整示范。三个可提炼的结论：①Anthropic 把**连接器（MCP）当成插件的一等公民**，说明企业落地的瓶颈不在模型能力而在"能不能拿到数据"；②**纯 Markdown/JSON、无构建步骤**是有意的选择——降低了企业定制的门槛，改文件即可，不用碰 CI；③官方把"通用起点 + 企业自行定制"写进 README 而不是提供开箱即用的成品，等于承认**流程知识无法通用化，只能由企业自己注入**。对做企业级 Agent 落地的团队，这 11 个插件的目录结构和连接器清单可以直接当作自己插件体系的设计基线。

---

## 9. n8n-io/n8n ⭐+281（总 205,111）

**事件**：n8n 发布 **2.39.7**（stable）与 **1.123.81**（1.x 维护线），均为补丁版本。本轮无 AI 相关新功能。

**核心内容**
- **2.39.7**（core + editor）：
  - 修复某条规则抛异常时"**破坏性变更检测（breaking change detection）**"会中断的问题，改为保持继续运行。
  - 修复编辑器凭证输入框未发送数字值的问题。
- **1.123.81**（偏安全与依赖）：
  - 修复受域名限制的凭证在自身节点中无法正常工作的问题。
  - `undici` 升级至 7.29.1，`vm2` 升级至 3.12.2，Snowflake SDK 升级至 3.3.0。
- **供应链透明度值得单独一提**：每个正式版本都附带 `sbom-source.cdx.json`（SBOM）、`vex.openvex.json`（OpenVEX 漏洞声明），2.39.7 另附 `THIRD_PARTY_LICENSES.md`。
- 所有版本由 `n8n-assistant[bot]` 自动发布，附件由 `github-actions[bot]` 上传。

**值得关注的原因**：本期两个版本都是补丁，但它上榜的理由和 AI 无关，而在于**工程治理的示范性**——尤其是 1.123.81 里 `vm2` 从 2.x 升到 3.12.2：`vm2` 曾是 Node 生态最著名的沙箱逃逸重灾区，2.x 有多个高危 CVE，n8n 这种要执行用户自定义代码的平台必须盯死这条依赖。另外，"**规则抛错时破坏性变更检测不能中断**"这个修复反映出一个通用原则：**质量门禁自身必须比被检查的代码更健壮**，否则一个异常就能让整个检测静默失效。每个 release 都带 SBOM + OpenVEX 也值得其他自托管项目抄——企业采购时这是硬性合规项。对做工作流自动化、低代码平台、需要执行不可信代码的团队，这两条都有直接参考价值。

---

## 10. coder/coder ⭐+145（总 14,939）

**事件**：自托管云端开发环境平台 Coder 上榜。它的定位在近期发生了明显位移——从"云端开发环境"扩展为"**云端开发环境 + AI 编码 Agent**"。

**核心内容**
- **核心抽象**：工作区（Workspaces）用 **Terraform 定义**（EC2 VM、K8s Pod、Docker 容器等），通过 **WireGuard 隧道**连接，空闲时自动关机以省成本；开发者的入职时间从数天压缩到数秒。
- **Coder Agents 是最值得关注的新增能力**：在**你自己的基础设施上**运行原生 AI 编码 Agent，其**执行循环运行在控制面（control plane）**。带来的三个性质：
  - **工作区内不存在 LLM 凭证**（no API keys in workspaces）；
  - **每个动作都携带用户身份**；
  - 集中化的**模型治理、成本追踪与审计日志**。
  - 模型可自带任意供应商（Anthropic、OpenAI、Google、Bedrock、自托管）。
- **AI Gateway**：统一处理 AI 工具链的认证、审计与成本控制。
- **快速开始**：`curl -L https://coder.com/install.sh | sh` 然后 `coder server`，访问 `localhost:3000` 即可建 Docker 模板并拉起第一个工作区；生产部署加 PostgreSQL 13+ 与外部访问 URL（`--postgres-url` / `--access-url`）。
- **集成面**：Coder Registry（模板/模块）、**Coding Agents 模块（把 Claude Code、Codex、OpenCode 隔离运行在 Coder 工作区中）**、`coderd` Terraform Provider、VS Code 扩展、JetBrains Toolbox 插件、Dev Containers、Kubernetes Log Stream、自托管 VS Code 扩展市场（可用于离线/隔离网络）、GitHub Actions，以及 `coder/agents-chat-action`（对 GitHub issue 或 PR 直接发起 Coder Agents 会话）。
- 许可：开源核心 + Premium 付费（面向大团队的付费特性）。带 OpenSSF Best Practices 与 Scorecard 徽章。

**值得关注的原因**：Coder 回答的是"**Agent 写代码这件事在企业里归谁管**"。它的答案很清晰：Agent 不能拿到自己的凭证，必须**借用用户身份、在受管的基础设施上、由控制面执行循环**。这个设计把三个企业最头疼的问题一次性解决了——密钥散落在工作区、Agent 行为无法归因、模型成本无法核算。把"AI Gateway"作为独立组件提供（集中认证 + 审计 + 成本控制）也是一个值得注意的产品判断：**企业在 Agent 时代需要的第一样东西可能不是更强的模型，而是统一的模型出入口**。对做内部开发平台、需要给 Agent 划安全边界的团队，这是目前最完整的开源参照。

---

## 上期条目新动态（去重章节）

上期已推送仓库中，今日有值得单独记录的变化：

| 仓库 | 今日 +Star | 新动态 |
|------|-----------|--------|
| cloudflare/security-audit-skill | **+3,607** | **今日榜首**。总 Star 从 8,543 涨到 11,126（两日累计 +4,534），单日增量是上期的近 4 倍，热度不降反升。说明"覆盖率账本 + 对抗性验证 + schema 校验"这套安全审计方法论正在被大规模采纳和传播。上期已详述方法论，此处不重复。 |
| alibaba/open-code-review | +3,286 | 仍在榜第二，总 Star 33,213 → 35,437（两日 +2,224）。热度维持在高位。 |
| affaan-m/ECC | +1,171 | 总 Star 从 260,684 增至 261,342，仍在增长但增速较上期放缓。 |
| Tencent/WeKnora | +1,125 | 仍在榜，v0.8.0 热度延续。 |
| alphaXiv/OpenResearch | +939 | 仍在榜，v0.2.4 热度延续。 |
| JustVugg/colibri | +873 | 仍在榜，增速较上期（+1,546）回落约 44%。 |
| NationalSecurityAgency/ghidra | +912 | 仍在榜，增速略降。 |
| abue-ammar/tinycast | +739 | 仍在榜，增速较上期（+1,179）回落约 37%。 |
| ever-co/ever-gauzy | +470 | 上期仅简提，今日继续在榜但未进入详细条目。 |

**观察**：上期 10 个条目中有 9 个今日仍在榜，但**除 cloudflare 外全部出现增速回落**（colibri −44%、tinycast −37%）。cloudflare/security-audit-skill 是唯一逆势加速的项目，且从第 8 名跃升到第 1 名。

---

## 其他趋势速览

| 仓库 | 今日 +Star | 一句话 |
|------|-----------|--------|
| cilium/cilium | +111 | 基于 eBPF 的网络、安全与可观测性方案，CNCF 毕业项目，稳态流量 |
| （榜单外） | — | 本期 Trending 页面共 20 个仓库，全部已在上表中列出 |

---

## 今日主线判断

1. **Agent 正在"落地"到真实环境，而不是停留在沙箱里**。今日新增入场者高度集中在同一层：Tencent/BrowserSkill（真实浏览器 + 真实登录态）、jamiepine/voicebox（真实麦克风与扬声器）、cline/cline（真实远程主机，SSH）、coder/coder（真实企业基础设施 + 用户身份）、TencentCloud/Octop（真实 IM 渠道与远程桌面）。**共性问题是同一个：怎么让 Agent 带着真实凭证进入真实系统，同时不失控**。而答案也趋同——**权限的权威源从 Agent 手里拿走，放到用户/平台侧**（BrowserSkill 把开关放在浏览器扩展且 CLI 无法覆盖；Coder 让工作区内不存在 LLM 凭证、每个动作带用户身份）。

2. **"技能 + 命令 + 连接器"三元组成为 Agent 能力的标准封装单元**。addyosmani/agent-skills（25 技能 + 9 命令）、anthropics/knowledge-work-plugins（11 插件，每个含 skills/commands/.mcp.json）、Tencent/BrowserSkill（`bsk install-skill` 自动装入各 harness）、voicebox（MCP 工具）——四个项目在同一周用同一套结构描述能力。这意味着 Agent 能力的**分发问题**已经基本解决，竞争焦点转向**谁能定义出更好的能力内容**。

3. **Agent 质量治理从"提示词"升级到"证据要求"**。addyosmani/agent-skills 每个技能以验证证据收尾、明确要求"看起来对了不算"；claude-code 把记忆当成需要维护缓存一致性的工程对象；n8n 强调"质量门禁自身必须比被检查代码更健壮"。**"完成"正在被重新定义为可核验的事实，而不是模型的自述**——这与上期"可靠性靠确定性工程兜底"的主线是同一个趋势的延续和深化。

4. **供应链安全成为 Agent 生态的显性议题**。本周密集出现：claude-code 插件安装禁用 npm install 脚本并做完整性校验、修复日志泄露 token；cline 修复 Windows 工作区二进制劫持（`NoDefaultCurrentDirectoryInExePath`）与 `apply_patch` 静默覆盖；n8n 每版本附 SBOM + OpenVEX 并升级 `vm2`。**Agent 的插件/技能就是代码，安装即执行**——这个认知正在变成工程实践。

5. **本地化与离线化继续扩张，且重心从"模型"转向"完整链路"**。上期主线是推理成本向存储转移（colibri）；本期 voicebox 把整个语音 I/O 栈本地化、Octop 用 `uv` 建隔离环境做到无需预装 Python、Coder 支持自托管扩展市场用于隔离网络。**"本地优先"正在从单点技术变成产品的默认架构假设**。
