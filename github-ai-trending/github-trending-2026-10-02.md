# GitHub 趋势日报 · 2026-10-02

> 数据源：github.com/trending 三榜合并（daily 15 条 + weekly 18 条 + monthly 24 条，去重后按增幅降序）
> 筛选口径：当日增幅高 + 技术方向有代表性 + 工程参考价值；已结合前九期推送历史去重
> 本期 10 条 = 7 条全新面孔 + 3 条已推送仓库的重大新版本/新事件

---

## 一、榜单速览

| # | 仓库 | 语言 | 增幅 | 总 Star | 一句话 |
|---|---|---|---|---|---|
| 1 | [tashfeenahmed/freellmapi](https://github.com/tashfeenahmed/freellmapi) | TypeScript | 月 +6,611 | 30,021 | 34 家免费 LLM 额度聚合成一个 `/v1` 端点，月 ~7.4B token |
| 2 | [earendil-works/pi](https://github.com/earendil-works/pi) | TypeScript | 日 +298 | 111,367 | 自扩展 Agent harness，含统一 LLM API / TUI / 编码 CLI / 编排运行时 |
| 3 | [androoAGI/starnet](https://github.com/androoAGI/starnet) | JavaScript | 周 +592 | 920 | 像素站台形态的本地优先桌面 harness，房间即权限域 |
| 4 | [anthropics/claude-code](https://github.com/anthropics/claude-code) | TypeScript | 月 +5,819 | 148,896 | v2.1.287：Claude Mods 让插件能改更深行为 |
| 5 | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | TypeScript | 日 +627 | 55,460 | v0.8.108：Studio 补齐音频后期（响度/闪避/波形/节拍源） |
| 6 | [NVIDIA/OpenShell](https://github.com/NVIDIA/OpenShell) | Rust | 日 +2,456 | 14,118 | v0.1.3-pre.2：把沙箱身份与 TLS 身份解耦 |
| 7 | [tile-ai/tilelang](https://github.com/tile-ai/tilelang) | Python | 日 +163 / 周 +481 | 8,162 | 09-30 上线华为昇腾 950 NPU 后端 |
| 8 | [Friedrich-M/UniMate](https://github.com/Friedrich-M/UniMate) | Python | 日 +217 | 1,125 | SIGGRAPH Asia 2026：一个模型驱动异构骨架动画 |
| 9 | [pablostanley/yoinks](https://github.com/pablostanley/yoinks) | TypeScript | 日 +361 | 3,061 | 终端里粘贴链接就下载视频，1,800+ 站点 |
| 10 | [HunxByts/GhostTrack](https://github.com/HunxByts/GhostTrack) | Python | 日 +368 | 16,507 | 老牌 OSINT 菜单工具 v2.2 被重新发现 |

非 Agent 项目 4/10（tilelang、UniMate、yoinks、GhostTrack），与 09-28 ~ 10-01 四期的 4/10 持平。

---

## 二、10 条详细

### 1. tashfeenahmed/freellmapi —— 把"免费额度"当成一种可路由的资源池

**事件**：TypeScript / MIT，月榜 +6,611（总 30,021），本月新晋月榜第 12 位。项目把 34 家厂商的免费层聚合成单一 OpenAI 兼容端点，README 首页直接挂出定价与"免费 vs 付费"的差异。

**核心内容**：
- **规模口径**：34 家 provider、474 个模型家族、635 个免费 provider/model 端点（584 chat / 41 embeddings / 7 transcription / 3 video），README 估算合计 **约 74 亿 token/月** 的免费推理容量。
- **协议面铺满**：`/v1/chat/completions`、`/v1/responses`（Codex CLI 需要）、`/v1/completions`（编辑器 ghost-text）、`/v1/images/generations`、`/v1/videos/generations`、`/v1/audio/speech`、`/v1/audio/transcriptions`、`/v1/embeddings`；另外单独实现 **`/v1/messages`（Anthropic 线格式）**、`/v1beta`（Gemini CLI）、可选 Ollama 仿真（给 Zed / JetBrains 这类本地模型客户端）。
- **路由机制**：六种策略；每个 `(platform, model, key)` 维度记 RPM/RPD/TPM/TPD 计数并学习各厂商上报的上限；429/5xx 时对该 key 冷却并切链上下一个模型；同名模型跨 provider 合并为一条并做组内严格 failover；`auto:<profile>` 可按请求切换命名链（如 coding 链、vision 链）。
- **Fusion 模型**：请求虚拟模型 `fusion` 时把 prompt 扇出给一组异构免费模型并行生成，再由 judge 模型合成一个答案。
- **凭证模型**：provider key 用 AES-256-GCM 存在 SQLite，按请求在内存解密；调用方只拿一个 `freellmapi-…` bearer token。
- **自更新目录**：路由器每天两次从 freellmapi.co 拉签名目录（Ed25519 固定公钥校验），自动应用新模型、配额变更与兼容性修正。免费安装拿"月度快照"（模型进 live feed 后 30 天到达，当前落后约 303 个模型）；付费 $19/年或 $49 终身，只买"当天到达"，代码始终 MIT。
- **运维**：Node 20+ 可跑，空闲约 40MB RSS，支持树莓派；桌面版是菜单栏应用（本地隐藏账号，无需设密码）；提供 `/mcp` 供 ChatGPT 等 MCP 客户端调用推理与查询 provider 健康度。

**值得关注的原因**：
① 这是"**免费额度也是一种可调度资源**"这一判断的第一个成型产品。前九期出现过"额度是一等约束"（codex-chatgpt-web 的 Pro 额度、Paperclip 的按 Agent 月度预算硬上限），本期它变成了被主动聚合、被计费、被路由的对象——README 甚至诚实写明"晚些时候头部模型触顶后端点有效智能会下降，UTC 零点重置"。
② **降级策略被写进架构而非文档**：429/5xx 冷却 + 组内 failover + 30 分钟粘性会话 + 可选中途切换时的 compact handoff note，这是长会话跨异构模型的标准解法。
③ 商业模式本身值得记：**开源路由器 + 付费只买"新鲜目录"**。目录同步落后 30 天不影响功能（"没有任何东西过期，也没有被削弱，只是到得晚"），把"时效"而非"能力"做成付费点，比常见的能力阉割式开源更干净。
④ 风险要明说：没有前沿模型、延迟方差大、无 SLA，README 自己劝退"别在它上面建正经东西"。

---

### 2. earendil-works/pi —— 自扩展 Agent harness，把"供应链"当成一等产品特性

**事件**：TypeScript / MIT，日榜 +298（总 111,367），今天仍在日榜。作者是 badlogic（Mario Zechner）。注意：openrig 的 README 里把 Pi 与 Claude Code、Codex 并列为"可编排的 harness"，本期 Pi 自己进了日榜。

**核心内容**：
- **不是一个工具，是一组包**：`pi-coding-agent`（交互式编码 CLI）、`pi-agent-core`（带工具调用与状态管理的 Agent 运行时）、`pi-ai`（统一多 provider LLM API：OpenAI/Anthropic/Google…）、`pi-tui`（差分渲染终端 UI）、`pi-durable`（持久化会话/任务/文档运行时）、`chord`（独立的应用组合运行时：服务、复制状态、RPC、插件）、`pi-telemetry`（厂商中立的遥测契约 + 参考适配器 + 一致性测试 + 类型化 schema）。
- **默认不给权限系统**，README 直说"Pi 默认以启动它的用户与进程权限运行"，需要边界请自己容器化，并给出三种模式：**Gondolin 扩展**（pi 与 provider 凭证留在宿主机，内置工具与 `!` 命令路由进本地 Linux micro-VM）、**纯 Docker**（整进程进容器）、**OpenShell**（整进程进策略受控沙箱）。
- **供应链硬化做成了工程惯例**：直接外部依赖钉死精确版本；`.npmrc` 设 `save-exact=true` + `min-release-age=2`（避免解析到当天发布的依赖）；`package-lock.json` 是唯一事实源，pre-commit 阻止误提交 lockfile（除非显式设 `PI_ALLOW_LOCKFILE_CHANGE=1`）；发布的 CLI 包内置 `npm-shrinkwrap.json` 钉死传递依赖；本地安装、文档里的 npm 安装、`pi update --self` 一律带 `--ignore-scripts`；CI 用 `npm ci --ignore-scripts`，另有定时工作流跑 `npm audit --omit=dev` 与 `npm audit signatures`；shrinkwrap 生成对依赖的 lifecycle script 走显式 allowlist，新出现的 lifecycle 依赖会让检查失败直到人工审核。
- **贡献策略**：新贡献者的 issue/PR 默认自动关闭，维护者每天人工过一遍。
- **公开训练数据**：配套 `pi-share-hf`，把 OSS 编码 Agent 的真实会话（工具调用、失败、修复）发布到 HuggingFace 数据集，作者自己也持续发布 `pi-mono` 会话。

**值得关注的原因**：
① **"Agent 运行时"这一层被拆到了包级别**。此前 google/ax 管调度、Strands 管进程内循环、Superpowers/OpenSpec 管方法论；Pi 把"统一模型 API / Agent 循环 / TUI / 持久化 / 应用组合 / 遥测"拆成 7 个可独立复用的包，是这一层第一次以**可组合套件**形态出现。
② **供应链安全从"建议"变成"会失败的检查"**，且手段比 10-01 的 claude-code-action（防火墙 runner + 检查脚本）更靠前——它管的是**依赖解析时**（min-release-age=2 防同日发布、lifecycle script allowlist、lockfile 不可擅动）。这与 NVIDIA/SkillSpector 的"安装前扫描"、OpenShell 的"运行前强制"连起来看，安全闸门已经被推到三个不同时刻。
③ **默认不给权限系统 + 明说三种容器化模式**，是"能力与授权一起设计"的又一实例（09-28 gpui-kit、10-01 同季第三次），但姿态更保守：不假装自己有沙箱，直接把边界责任交给用户并给方案。
④ 新贡献者 issue 自动关闭 + 每日人工复核，是**开源项目对抗低质贡献**的新姿态，值得跟。

---

### 3. androoAGI/starnet —— 把权限拓扑画成像素站台，"界面不得断言 harness 无法证明的状态"

**事件**：JavaScript / MIT（仅代码），周榜 +592（总 920），小体量新项目首次进榜。本地优先桌面 Agent harness，前端是像素风太空站。

**核心内容**：
- **产品契约是字面意义的**："**一个房间 = 一个能力域限定的团队**"、"**一条走廊 = 一条被授权交接的通道**"、"**摆放一个物件 = 授予一项真实能力**"。你画的布局就是 Agent 实际跑的工作流。
- **多 Agent 并行**：每个 Agent 有独立 class / persona / loadout，各自独立 workspace、transcript、memory 与受限权限，可同时运行多个——README 强调是"真正独立、有界的 agent run"，不是动画模拟。
- **模型接入**：粘贴 OpenRouter key，或 OAuth 登录 Anthropic / OpenAI / Google；**密钥存 OS keychain，永不出现在前端**；也支持本地 Ollama（`127.0.0.1:11434`，能列出本地模型才报就绪），并诚实标注"本地模型更小，长任务会更慢更糙"。
- **Night Shift**：离开后 Agent 在一条可调的"牵引绳"内继续工作，每个离开期间的动作都记录可复核。
- **Task Briefs**：把模糊需求转成"一个带选项的具体问题"，可经任意已连接渠道发出，而不是静默猜错。
- **OUTBOX**：交付物落成真实文件，不是聊天记录里要考古的滚动条。
- **不模拟任何东西**：README 明确"不模拟收入、已完成工作、模型活动或花费"，核心产品法则是**界面永远不得断言 harness 无法证明的状态**。
- **迁移路径**：可导入已有的 OpenClaw 或 Hermes agent（读磁盘上的 persona / instructions / memory / model），但 API key 不迁移，需在 KEYS 页重填。
- **发布门槛**：Windows 安装包必须通过 Authenticode + 时间戳验证，macOS 两个架构必须通过 Developer ID 与 Apple 公证，所有 updater 产物必须有有效签名，否则流水线拒绝发版；`npm run qa:ready` 的 READY 回执与候选提交绑定，任何新提交都会作废上一个 READY。

**值得关注的原因**：
① **"把不可验证的变成可验证的"本期换了个方向**。前几期是"让产物可复现"（scriptc coverage、Paperclip 原子执行、Hindsight Extraction Tester），Starnet 走的是反方向——**把可视化降级为运行时状态的投影**，明确禁止 UI 表达 harness 证明不了的东西。这是对"Agent 演示造假"这一整类问题的产品级回答。
② **权限模型第一次被做成空间隐喻**：房间=能力域、走廊=授权通道、物件=能力授予。这比"配置文件里写 allowlist"更接近人类直觉，也比 09-29 openrig 的 per-seat 权限更激进——它把授权关系做成了可见、可编辑、可审计的**拓扑**。
③ **本地优先 + 密钥只在 keychain**，且导入第三方 agent 时明确"key 不迁移"，这是把安全边界写进迁移路径。
④ 小仓库（920 star）一周 +592，增速比例最高；但要注意 macOS 覆盖较弱、Linux 不作为公开发布目标，README 自己标了"early release"。

---

### 4. anthropics/claude-code v2.1.287 —— Claude Mods 上线：插件可以修改更深层行为

**事件**：TypeScript，月榜 +5,819（总 148,896），2026-10-01 发布 v2.1.287。这是 10-01 期 v2.1.286 之后的下一个版本，主题从"凭证脱敏"切换到"扩展性 + 可访问性"。

**核心内容**：
- **Claude Mods**：插件现在可以修改更深层的行为。这与 09-29 记录在 claude-code-templates 的"Function Hooks 改名 Claude Mods"对上了——改名是这次能力开放的铺垫。
- **内置 mod "You should know"**：一个侧边 Agent 盯着你的操作与 Claude 的动作，主动标记双方可能漏掉的东西。启用方式：`/plugin enable cc-plugin-you-should-know@builtin`（需第一方会话且开启遥测）。
- **MCP 协议跟进**：支持 2025-11-25 协议下 MCP 服务器发来的 **URL prompt**（例如用于登录）。**带破坏性**：升级后若某 server 连不上，需在其 MCP 配置里加 `"bareElicitationCapability": true`。
- **自托管 runner 内置 `gh api`（仅 REST）**：给使用 Anthropic 托管 git、但机器上没装 GitHub CLI 的 macOS / Linux 会话用。
- **可观测性**：OpenTelemetry 的 `user_prompt` 事件新增 `prompt_text` 字段（`prompt` 的副本，给嵌套点号 key 的后端用），并明确提示"你在哪里丢弃或掩码 `prompt`，就在哪里同样处理它"。
- **Windows**：当拒绝 Bash 工具同时也会关掉 PowerShell 工具、导致 Claude 完全没有 shell 工具时，启动给出警告。
- **本版大量修复集中在可访问性（屏幕阅读器）**：光标位置、diff 中的变更行、审批提示被截断的顶部行、空菜单里的"用数字选择"提示、`/rewind` 摘要选项、`claude agents` 每秒变化的时间戳（改为最多每 10 秒）。此外修了：`rm` 危险命令（如 `/` 或 home）与输出重定向到 `~`/通配路径组合时**丢失 always-ask 保护**；名为 `__proto__` 的 MCP 工具导致组织级 per-tool 权限上限被静默丢弃；`claude -p` 在回复进行中切换模型后每条消息都重复 fallback；resume/compaction 后 CLAUDE.md 被重复附加；附带 17–20 个文件时只投递前 16 个。

**值得关注的原因**：
① **"插件能改多深"是平台开放度的分水岭**。Mods 之前，插件只能加工具/命令/技能；Mods 之后能改更底层行为——这既扩大生态，也扩大信任半径，必然连带推动签名、权限与审计需求（与 Pi 的依赖审核、SkillSpector 的扫描形成同一问题的三个侧面）。
② **"You should know" 是"旁观者 Agent"模式的第一个第一方产品化**：不再让主 Agent 自审，而是另起一个侧边 Agent 专盯遗漏。这与此前"双轴 code review"（10-01 mattpocock `/code-review` 拆 Standards+Spec 并行子代理）是同一思路的两种实现。
③ **可访问性成为一等公民**：一个版本里十几条屏幕阅读器修复，说明 Agent CLI 的用户面正在从"能用终端的开发者"扩大到更广人群。
④ `__proto__` 工具名绕过组织权限上限、危险 `rm` 在重定向组合下丢保护——**都是边界输入型漏洞**，与 10-01 期"7 类凭证脱敏里 5 类是边界输入"结论一致：畸形输入是持续攻击面。

---

### 5. heygen-com/hyperframes v0.8.108 —— "写 HTML 出 MP4"扩成完整音频后期

**事件**：TypeScript / Apache-2.0，日榜 +627（总 55,460），2026-10-02 发布 v0.8.108，单日 2 个提交。发布节奏值得记：09-30 连发 0.8.94/95/96 → 10-01 0.8.102 → 10-02 0.8.108。

**核心内容**：本版是"Studio 音频能力 8 个部件"中的第 2–5 部件落地：
- **2/8 Core**：预览用 Web Audio 播放**带声视频**、音频分组、电平表与 carve（#4814）。
- **3/8 Studio**：片段菜单里加入速度预设、voice、look、裁剪预设与冻结帧（#4815）。
- **4/8 Studio**：**响度归一化 + 在人声下自动闪避（ducking）**，并给出 limiter 报告（#4816）。
- **5/8 Studio**：波形条 + 片段灯 + 峰值标记，以及**视频节拍源**（#4817）。
- **修复**：reload 换掉预览帧前刚做的选择现在会被保留；撤销移动/微移时立即回绘，不再等保存完成。

**值得关注的原因**：
① **"非文本产出物 Agent 化"这一期补上了音频这一环**。前几期覆盖了视频（hyperframes / video-use / MoneyPrinterTurbo）、3D（spirula-studio）、Office（univer）、图片（stable-diffusion.cpp），音频后期一直缺位；本版把响度标准、人声闪避、limiter 报告这些**专业后期工序**做进了确定性渲染管线（headless Chrome 逐帧 + FFmpeg，同输入同输出）。
② **"视频节拍源"意味着时间轴开始被机器理解**：节拍检测结果成为可驱动其他元素的信号，这是从"渲染工具"往"剪辑语义层"走的一步。
③ **一天一个版本的发布节奏**说明这条赛道的迭代压力已经从"能不能生成"转到"后期工序覆盖度"，而 hyperframes 的策略是**用确定性换可复现**——同一输入必须同一输出，这与 10-01 期"产物可复现"主线一致。

---

### 6. NVIDIA/OpenShell v0.1.3-pre.2 —— 把沙箱身份与 TLS 身份解耦

**事件**：Rust，日榜 +2,456（总 14,118），2026-10-01 发布 v0.1.3-pre.2。OpenShell 在 09-30 期首次展开过（内核级拦截 + 形式化验证策略变更）。

**核心内容**（本版变更）：
- `refactor(auth): separate sandbox identity from TLS`（#3110）——**沙箱身份与 TLS 证书身份分离**。
- `docs(auth): clarify gateway mTLS behavior`——把 gateway 的 mTLS 行为写清。
- `test(auth): include workspace scope in TLS authorization checks`——TLS 授权检查里纳入 workspace 作用域。
- `test(e2e): bound service auth sandbox names for large PIDs`——大 PID 场景下服务认证的沙箱命名加边界。

**值得关注的原因**：
① 这条 refactor 修的是一个**架构级耦合**：当"我是哪个沙箱"和"我持有哪张 TLS 证书"被绑在一起时，证书轮换、沙箱迁移、workspace 隔离都会互相牵制。拆开之后，**授权判断可以按 workspace 作用域独立进行**——这是让策略引擎能被形式化验证的前提。
② 与 10-01 期 claude-code-action 的"防火墙 runner"、本期的 Pi 依赖审核、SkillSpector 扫描放在一起看：**Agent 安全已经被拆成三个时刻、四类机制**（安装前扫描 / 依赖解析期约束 / 启动时策略 / 运行时身份与网络强制），OpenShell 负责的是最后一格，而它在补的是身份模型的正确性。
③ 仍是 pre 版本（v0.1.3-pre.2），生产可用性要等正式版。

---

### 7. tile-ai/tilelang —— 昇腾 950 NPU 后端上线，DSL 版图补上国产算力

**事件**：Python，日榜 +163 / 周榜 +481（总 8,162）。**2026-09-30 正式支持华为昇腾 950 NPU**，含原生代码生成、自动调度与同步、SIMD/SIMT 向量编程，并提供 GEMM、FlashAttention 等昇腾示例。

**核心内容**：
- 定位：构建在 TVM 之上的 Pythonic 领域特定语言，用于写高性能 GPU/CPU/NPU kernel（GEMM、Dequant GEMM、FlashAttention、LinearAttention 等），目标是不牺牲底层优化能力的前提下提高开发效率。
- **后端矩阵**：CUDA（含 Blackwell SM100/SM120）、ROCm（CDNA4 MXFP4 / RDNA3/4）、Metal（M5 cooperative-tensor GEMM）、LLVM/CPU，现在加昇腾 NPU。
- 工程配套：TileLang **LSP 已开源**（08-04），对 buffer 形状/dtype/scope/推断布局做 inlay hints，带 hover 与精确诊断；v0.1.13（08-03）上线多后端语言方言、编译器诊断带源码位置、新增 CUDA 与 Metal 硬件路径，并**移除多个遗留 API**（升级前须读兼容性说明）；另有 TileLang Puzzles 交互式练习。
- 编译器工具链：IR Lower Trace（逐 pass 看 IR 变化）、Pass Visualizer、Pass Diff、编译器 pass 耗时分析、跨主机 CUDA 二进制缓存。

**值得关注的原因**：
① **"一份 DSL 覆盖 GPU + CPU + NPU"从口号变成了后端清单**。昇腾 950 后端（原生代码生成 + 自动调度同步）意味着国产 NPU 第一次进入主流 tile 级 DSL 的官方支持矩阵，而不是靠社区 fork。
② **编译器可观测性被当产品做**：Pass Visualizer / Pass Diff / IR Lower Trace / pass 耗时——这类工具以前散落在各编译器内部，TileLang 把它们做成用户可见的一等能力，直接降低 kernel 调优的调试成本。
③ 与前九期"上下文经济"主线的关系：**这一层省的不是 token，是算力**。当模型结构越来越依赖自定义 kernel（稀疏注意力、块量化、MoE 分组 GEMM），DSL 层的生产力就是推理成本的直接变量。

---

### 8. Friedrich-M/UniMate —— 一个模型驱动异构骨架动画（SIGGRAPH Asia 2026）

**事件**：Python，日榜 +217（总 1,125）。论文被 **SIGGRAPH Asia 2026** 接收（07-18），arXiv 2609.05415，作者来自 Princeton / UC Berkeley / MIT / NTU。09-06 放出训练与推理代码，**09-27 放出预览 checkpoint**（HuggingFace）。

**核心内容**：
- 目标：**一个统一模型驱动形态各异的骨架**——双足、四足、鸟类、水生、昆虫、蛇形，以及有关节的刚体物件，全部做进统一规范化（canonicalization）。
- 数据集 **UniML3D**：13,006 条文本配对的运动序列，覆盖上述多样骨架拓扑；原始素材来自 Mixamo、Objaverse-XL-Rigged-Animated、Truebones-ZOO，处理管线含 download → export → rendering → captioning → joint annotation → feature extraction → animation 七阶段。
- **许可边界写得很明确**：Truebones ZOO 的动物动作是商业资产包，许可不允许再分发，管线按用户自购后的标准 `Truebone_Z-OO` 目录结构消费；仓库只提供 prompts / metadata / renders。
- 交互式 3D demo 已上线（three.js）；有待办项"为分布外（新）骨架提供官方预处理管线"。

**值得关注的原因**：
① **"统一"这个词在这里是真的跨拓扑**，不是同一骨架换风格。此前 3D 生成类项目（spirula-studio 的 3DGS）解决的是"重建/表示"，UniMate 解决的是"**运动迁移的拓扑鸿沟**"——四足的动作怎么迁移到蛇形，这是长期靠人工重定向的工作。
② **许可处理是正面示范**：把不可再分发的商业动作包明确划出边界，只发管线与元数据。对比 09-29 期 cua 在 README 里标 AGPL 边界、本期 Pi 的依赖审核，"开源边界必须写清楚"已经成为成熟项目的标配动作。
③ 数据集 + 代码 + checkpoint + 交互 demo 四件套齐全，且 demo 在论文接收前就上线——**研究项目的发布节奏正在向工程产品靠拢**。

---

### 9. pablostanley/yoinks —— 终端视频下载器，把"没有套路"做成卖点

**事件**：TypeScript / MIT，日榜 +361（总 3,061）。`npm i -g yoinks` 或 `npx yoinks`，Node 18+。

**核心内容**：
- 支持 YouTube、X/Twitter、Instagram、Threads、TikTok 及 yt-dlp 覆盖的 1,800+ 站点；粘贴 URL → 选分辨率（或纯音频 mp3）→ 完成。
- **UI 用 Ink（React for terminal）**：全屏居中，退出时恢复 scrollback；↑/↓ 或 j/k 或数字键选择，esc 返回，`^c` 退出；**鼠标可点**（yoink 按钮、格式列表、页脚提示），点 logo 回首页。
- **主题跟随终端**：默认 `auto` 直接取终端自身前景/背景色，不猜；`^t` 或点页脚可循环 auto/light/dark，也可用 `--theme` 指定。
- **依赖自举**：首次运行自动把 yt-dlp 独立二进制下到 `~/.yoinks/bin`（**不需要 Python**）；已有 yt-dlp 则复用；ffmpeg 从 PATH 找，找不到用内置 `ffmpeg-static`。
- 文件存到 `~/Downloads` 并打印路径。Roadmap：`--best`/`--mp3` 脚本模式、`-o <dir>`、播放列表、剪贴板自动建议、yt-dlp 自更新、`curl yoinks.sh | sh`。
- README 有 fair use 声明：个人归档工具，可能违反平台 ToS，只下你有权保留的内容。

**值得关注的原因**：
① **"没有套路"本身就是需求**。README 的对照物是"没有弹窗、没有假下载按钮、没有可疑跳转"——下载器这个品类的用户痛点是广告与欺骗，不是功能缺失。这与 10-01 期 MoneyPrinterTurbo"日志只记缓存文件名不记下载 URL"、09-30 期 reclip"150 行 Flask + 2 依赖"是同一取向：**用克制的工程量换取可审计性**。
② **终端 UI 的体验标准在抬高**：全屏 + 鼠标可点 + 跟随终端主题 + 退出恢复 scrollback，这些细节以前只在 TUI 应用里讲究，现在一个下载器就做到。
③ 依赖自举（自带 yt-dlp 二进制、ffmpeg-static 兜底）把"装不上"这个最大流失点消掉了，是 CLI 分发的正确做法。

---

### 10. HunxByts/GhostTrack —— 老牌 OSINT 菜单工具 v2.2 被重新发现

**事件**：Python，日榜 +368（总 16,507）。版本 2.2，是持续多年的老项目（非本期新开发），本期被趋势榜重新发现。

**核心内容**：终端菜单式信息收集工具，三个入口：**IP Tracker**（可配合 Seeker 拿到目标 IP 后查询）、**Phone Tracker**（按手机号查公开信息）、**Username Tracker**（按用户名查社媒存在情况）。支持 Linux（apt）与 Termux（pkg）安装，纯 Python + `requirements.txt`。

**值得关注的原因**：
① **它是本期唯一的"低工程量高热度"样本**，价值在于解释趋势榜的构成：榜单里始终有一批"菜单包一层公开数据源"的工具，靠使用门槛低获得稳定曝光。看榜单时要能把它和真正的工程进展区分开——这类项目**数月甚至数年没有实质代码变化**，只是被重新发现（09-30 期 rakyll/hey 最后推送 2026-01-10 是同一现象）。
② **能力边界必须说清**：这类"手机号追踪"实际只能拿到运营商归属地、公开社媒关联等**间接信息**，不是实时定位；IP 查询同样只能到 ISP/地理粗略级别。把它当定位工具使用是误解，也是这类工具最常见的滥用来源。
③ 与本期的安全主线对照：Agent 侧在收紧边界（OpenShell 身份解耦、Pi 依赖审核、claude-code 权限修复），而**人的信息收集侧仍是宽松工具在涨**——这个不对称值得记一笔。

---

## 三、其他趋势速览

**上期（10-01）条目新动态**：
- **mvschwarz/openrig v0.6.4**（今天发布）——**Web UI 默认关闭并进入维护模式**，CLI 与 TUI 是唯一受支持路径（要开需 `rig config set ui.enabled true` 并重启 daemon）；daemon 现在校验请求来自哪个地址与哪个页面，自定义 DNS / `/etc/hosts` 别名 / 反代域名需加进 `OPENRIG_ALLOWED_HOSTS`，本机其他端口的开发服务器从浏览器调用需加进 `OPENRIG_ALLOWED_ORIGINS`（拒绝时会告知该加哪个设置）；单 seat rig 支持 `rig seat launch --fresh --stop`；受管 Claude 启动的能力检查（先读 `claude --help`）超时从 1 秒放宽到 5 秒；升级后 seat 启动改用当前版本内置启动文件，不再指向已删除的安装路径；Claude seat 在 auto 模式恢复后需确认同一进程在跑才接受普通消息。
- **pbakaus/impeccable** Skill 4.5.0 + engine-v0.1.11（今天发布，日 +495 / 周 +2,704）。
- **paperclip** canary v2026.1002.0-canary.7（今天），含 `fix(daytona): recover output from stalled log streams`；周 +14,335。
- **hindsight** 周榜第 1（周 +17,403 / 月 +22,416）；另发 `integrations/hermes/v1.2.1`（09-30），仍未出 v0.10.3。
- **VoiceStudio** 周 +16,114，无新版本（仍 v0.5.6）。
- **mattpocock/skills** 日 +883，无新版本（仍 v1.2.3，08-06）；**ponytail** 日 +1,194 / 月 +31,160，无新版本（仍 v4.10.0，09-14）；**superpowers** 日 +455，无新版本（仍 v6.4.2，09-25）；**context-mode** 日 +362，无新版本（仍 v1.0.169，06-29）。
- **TencentCloud/Octop** v1.0.2b5（09-29），月 +4,888；**Tencent/WeKnora** 仍 v0.8.2（09-24），月 +10,740；**dream-num/univer** 周 +5,267，无新版本。
- 月榜头部仍是上一代爆款：archify +35,068、gods-eye-view +31,240、ponytail +31,160、i-have-adhd +26,584、ECC +26,450。

**本期其他在榜**：alibaba/open-code-review（月 +21,646）、anthropics/financial-services（周 +1,270）、HKUDS/CLI-Anything（周 +1,055）、alirezarezvani/claude-skills（周 +743）、vercel/next.js（周 +624）、davila7/claude-code-templates（周 +601）、claude-code-action（周 +376）、FxEmbed（周 +369）、agent-substrate/substrate（周 +365）、trycua/cua（月 +5,674）、NVIDIA/SkillSpector（月 +3,423）、superdesigndev/treg（月 +3,249）、jingyaogong/minimind（月 +6,436）、rohitg00/ai-engineering-from-scratch（周 +6,469）、max-sixty/worktrunk（月 +1,903）、longbridge/gpui-kit（月 +1,786）、fmtlib/fmt（月 +2,130）、flutter/flutter（周 +147）、firebase/firebase-ios-sdk（日 +112）。

---

## 四、当日主线判断

1. **免费额度被当成可调度资源**（freellmapi）。前九期的"额度是一等约束"演进为"额度是资源池"：34 家 provider、635 个端点、~74 亿 token/月 被聚合成一个端点，配 RPM/TPM 学习式计费与 429 冷却切换。降级、粘性会话、跨模型 handoff 全部写进架构。**"时效"而非"能力"成为开源项目的付费点**，这是商业模式上的新样本。

2. **Agent 安全闸门被明确推到四个时刻**：安装前扫描（SkillSpector）、**依赖解析期约束**（Pi 的 `min-release-age=2` + lifecycle script allowlist + lockfile 不可擅动）、启动时策略与身份（OpenShell 把沙箱身份与 TLS 身份解耦、workspace 作用域进 TLS 授权检查）、运行时强制（OpenShell 内核级拦截）。本期新增的是第二格——**供应链安全第一次下沉到"依赖怎么被解析"**。

3. **平台开放度与信任半径同时放大**（claude-code Claude Mods + "You should know" 侧边 Agent）。插件从"加能力"变成"改行为"，第一方还顺势产品化了"旁观者 Agent 专盯遗漏"。这与 mattpocock 的 `/code-review` 双轴并行子代理是同一思路：**别让主 Agent 自审**。

4. **"Agent 运行时可组合套件"成型**（Pi 的 7 个包：模型 API / Agent 循环 / TUI / 持久化 / 应用组合 / 遥测）。此前这一层是分散的单点方案（AX 调度、Strands 进程内循环、Superpowers 方法论），现在第一次出现**可独立复用的包级拆分**。

5. **界面被要求"不得断言 harness 证明不了的状态"**（Starnet）。这是对"Agent 演示造假"的产品级回答，方向与"让产物可复现"相反但互补：一个管产物，一个管呈现。配套的是**权限拓扑空间化**（房间=能力域、走廊=授权通道、物件=能力授予）。

6. **非文本产出物补齐音频后期**（hyperframes Studio 8 部件的 2–5 件：Web Audio 带声预览、响度归一化 + 人声闪避 + limiter 报告、波形条与峰值标记、视频节拍源）。时间轴开始被机器理解（节拍驱动其他元素），确定性渲染（同输入同输出）成为可复现的落点。

7. **算力层的生产力成为成本变量**（tilelang 昇腾 950 后端 + 编译器可观测性四件套）。DSL 覆盖 CUDA/ROCm/Metal/LLVM-CPU/昇腾，Pass Visualizer / Pass Diff / IR Lower Trace 把编译器内部做成用户能力——**这一层省的不是 token，是算力**。

8. **研究项目发布节奏产品化**（UniMate：数据集 + 代码 + checkpoint + three.js 交互 demo 四件套齐全，demo 早于论文接收上线），且**许可边界写得比很多产品还清楚**（Truebones 商业动作包只给管线与元数据）。"开源边界必须写清"已成成熟项目标配（另见 cua 的 AGPL 说明、Pi 的依赖审核）。

9. **CLI/TUI 被重新确认为"受支持路径"**（openrig v0.6.4 把 Web UI 关掉进维护模式，并给 daemon 加 Host/Origin 校验）。这是对"浏览器可达面 = 攻击面"的正面回应，也是对 GUI 维护成本的诚实认账。

10. **榜单构成需分层看**：本期 4/10 为非 Agent 项目（tilelang、UniMate、yoinks、GhostTrack），与 09-28 ~ 10-01 四期持平；其中 GhostTrack 是典型的"低工程量高热度、被重新发现"样本（同 09-30 期 rakyll/hey）。看榜时要把它与真正的工程进展区分开——**并在报告里说清其能力边界（不是实时定位）**。

---

*生成时间：2026-10-02 14:00 (GMT+8) · 数据源：github.com/trending（daily/weekly/monthly 三榜合并去重）*
