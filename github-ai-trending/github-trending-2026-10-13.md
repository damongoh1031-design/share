# GitHub AI 趋势日报 · 2026-10-13

> 数据源：github.com/trending 主榜（daily/weekly/monthly）+ 18 个语言维度榜，共 **21 个榜、231 条去重**。抓取 0 次失败（21 并发 × 8 次重试）。
> 筛选口径：当日/本周增幅 + 技术方向代表性 + 工程参考价值；**与 memory.md 已推送清单逐条比对，本期 10 条详细以全新面孔为主**。

---

## 一、榜单速览（TOP 20 · 按增幅）

| # | 仓库 | 语言 | 总 Star | 增幅 | 榜位 | 状态 |
|---|------|------|--------:|-----:|------|------|
| 1 | morluto/rea | TS | 171,179 | +45,327 日 | main-daily/weekly | 已推送·今日 #1 |
| 2 | debpalash/VoiceStudio | Python | 60,816 | +37,110 日 | main-daily | 已推送 |
| 3 | boykopovar/AnyPS5 | C++ | 33,291 | +27,263 日 | main-weekly | 已推送 |
| 4 | vectorize-io/hindsight | Python | 48,928 | +25,557 日 | main-daily | 已推送 |
| 5 | alibaba/open-code-review | Go | 46,638 | +24,317 月 | main-monthly | 已推送 |
| 6 | affaan-m/ECC | JS | 278,062 | +22,583 月 | main-monthly | 已推送 |
| 7 | paperclipai/paperclip | TS | 101,092 | +20,601 | main-daily | 已推送 |
| 8 | **rohitg00/ai-engineering-from-scratch** | Python | 68,236 | +13,880 月 | main-monthly | **新面孔** |
| 9 | JustVugg/colibri | C | 41,581 | +13,470 月 | main-monthly | 已推送 |
| 10 | addyosmani/agent-skills | JS | 105,766 | +12,396 月 | main-monthly | 已推送 |
| 11 | **mattpocock/skills** | Shell | 288,307 | +11,139 周 | main-weekly | **新面孔** |
| 12 | Tencent/WeKnora | Go | 33,602 | +11,159 日 | lang-go | 已推送 |
| 13 | NationalSecurityAgency/ghidra | Java | 85,501 | +9,722 月 | lang-java | 已推送 |
| 14 | tashfeenahmed/freellmapi | TS | 34,242 | +8,213 | — | 已推送 |
| 15 | NVIDIA/OpenShell | Rust | 16,014 | +7,457 | — | 已推送 |
| 16 | TencentCloud/Octop | Python | 8,985 | +7,333 日 | lang-python | 已推送 |
| 17 | trycua/cua | Rust | 29,542 | +7,084 | — | 已推送 |
| 18 | DuarteSantos8/openGym | JS | 10,674 | +6,621 | — | 已推送 |
| 19 | anthropics/claude-code | TS | 150,489 | +6,422 | — | 已推送 |
| 20 | **cathrynlavery/diagram-design** | HTML | 52,998 | +2,081 日 | main-daily/lang-html | **新面孔** |

**关键读数：主榜继续固化。** main-daily 9 条 / weekly 11 条 / monthly 22 条中，**仅 3 条全新面孔**（ai-engineering-from-scratch、mattpocock/skills、diagram-design）。本期 10 条详细中 **7 条来自语言榜，3 条来自主榜月度**。

---

## 二、10 条重点动态（事件 / 内容 / 为什么值得关注）

### 1. mattpocock/skills — 「反 GSD/BMAD/Spec-Kit」的最小技能集，周增幅 +11,139

- **事件**：TypeScript 圈知名作者 Matt Pocock（Total TypeScript）把自己 `.agents` 目录里的日常技能开源，一周 +11,139 star、总 288,307（本期最高总星数项目之一）。Shell 榜第 1。
- **核心内容**：
  - **20 个技能 = 14 user-invoked（只在你敲 `/xxx` 时触发，负责编排）+ 8 model-invoked（Agent 可自动取用，承载可复用纪律）**。明确的架构规则：**user-invoked 可以调 model-invoked，但绝不能调另一个 user-invoked**（避免编排套编排）。
  - 四大失效模式对应四组技能：①**没对齐** → `/grill-me`、`/grill-with-docs`（"拷问式"提问，直到设计树每个分支都定死）；②**太啰嗦** → 构建**共享语言（GLOSSARY.md）**，把"课程某章节里的某节课被 '落实'（即在文件系统里拿到位置）"压缩成 "materialization cascade"；③**代码不工作** → `/tdd`（红-绿-重构）+ `/diagnosing-bugs`（建反馈环→最小化→假设→埋点→修→回归测试，逐阶段门控）；④**架构成一团泥** → `/to-spec` 先问清动哪些模块，`/improve-codebase-architecture` 定期扫"深化机会"。
  - 安装走 `npx skills add mattpocock/skills -a <agent>`（Cursor/opencode/devin/windsurf/amp/pi），或 Claude Code/Codex/Copilot/Gemini CLI 各自插件市场。
- **为什么值得关注**：**这是"技能集"这条赛道上第一次明确以"保留你的控制权"为卖点**——README 直接点名 "GSD、BMAD、Spec-Kit 想替你拥有流程，但同时夺走了你的控制，让流程里的 bug 难以定位"。与已推送的 addyosmani/agent-skills（生产级工程技能）、ECC（71 agents 全家桶）形成第三条路线：**小而可改、可组合、不接管流程**。"`/grill-with-docs` 边拷问边建领域模型和 ADR" 是本期最具体的一个工程技巧。

### 2. cathrynlavery/diagram-design — 45 种图的编辑级设计技能，日榜新面孔

- **事件**：日榜（+2,081 日，总 52,998，forks 3,348）与 HTML 语言榜双榜在榜。作者为 littlemight.com 博主自用而做。
- **核心内容**：
  - Agent 说一句话 → 出**一个自包含 HTML + 内联 SVG 文件**（双击即开，无构建、无 JS、无外链图片）。**45 种图型 × 3 变体**（minimal light / minimal dark / full-editorial）。
  - **四个旋钮**：Format（html/svg/png/html+png）、Size（doc-inline/slide-16x9/print-a4…共 10 档，**同时改 viewBox 和字号梯度**——投影幻灯片用 16px 节点名而非 12px）、Detail（faithful ≤24 节点 / balanced ≤12 / simplified ≤7，走**固定降级阶梯**：装饰→重复→叶子簇→基础设施）、Audience（engineer/mixed/executive，**只改措辞不改数量**：`Auth Service / JWT · RS256 · :8443` → `Auth Service / token check` → `Sign-in`）。
  - **导入必附"保真台账"**：列出合并/折叠/丢弃了什么（例：12 源节点→8 绘制；折叠 1 个判定为边标签；丢弃 1 张未连接的便签）。**能导入 Mermaid / draw.io / Excalidraw 并重画**。
  - **品牌上手**："onboard diagram-design to https://yoursite.com" 自动抓取你的配色与字体；对比度检查自动做；字体离线内嵌；多客户切换。
  - **明确写缺点**：输出质量取决于模型、同一 prompt 两次布局可能不同、**没有可 diff 的源格式**（文档放 Git 里且每迭代都改的话 Mermaid 仍更合适）。
- **为什么值得关注**：**"美学"第一次被拆成"参考板 + 可验证约束"再产品化**——4px 网格、CI 查重叠与裁切、1px 细线、无阴影、强调色只留给 1–2 个要点、"最高质量的动作通常是删除"。与已推送的 taste-skill（前端）、video-shotcraft（镜头配方卡）同构，但**唯一切到"技术图表"这个刚需场景**，并诚实指出"不可 diff"这个真实代价。

### 3. rohitg00/ai-engineering-from-scratch — 528 课的 AI 工程课程，月度榜新面孔

- **事件**：月度榜 +13,880（总 68,236，forks 11,951），MIT。
- **核心内容**：
  - **528 课 / 20 阶段 / Python·TypeScript·Rust·Julia 四语言**，每课固定目录 `code/ + docs/en.md + outputs/`。
  - **六拍教学法**：MOTTO → PROBLEM → CONCEPT → **BUILD IT（裸写数学，不用框架）** → **USE IT（同一件事用 PyTorch/sklearn）** → **SHIP IT（产出 prompt / skill / agent / MCP server）**。**Build/Use 二分是全课脊柱**——先自己实现小版本，再用生产库，从而理解框架在做什么。
  - **每课都交付一个可复用工具**（"别人的课程以'恭喜你学会了 X'结束，这里以你装得上、粘得进日常的工具结束"）。
  - **课程本身用 Agent Skill 形态分发**：`npx skills add rohitg00/ai-engineering-from-scratch`，装完得到 `start-learning`（10 题水平测验→生成个性化 `LEARNING.md`）、`learn`（每会话一课：热身前测→讲→测）、`course-guide`（"注意力机制在哪学"→直接给课）、以及 **MCP 专项 17 课**、**Agent Skills 专项 5 课**、Claude 认证与 MCPA 认证 tutor。
  - 提供**真实主机可发现性/调用/脚本/卸载的证据**要求；缺 Node/npx/python3 时明说"走网站或手读 docs/en.md，但真实主机证据仍待补"。
- **为什么值得关注**：**"教学"本身被做成了可被 Agent 执行的技能**，且把"证据"从口号变成要求（命令、工作目录、退出码、有意义输出）。与已推送的 deepagents-in-action、microsoft/ai-agents-for-beginners 属同类，但它是**唯一把"从零实现"与"生产库对照"作为强制脊柱**，且**唯一自带认证 tutor 和 MCP 专项路线**。

### 4. calesthio/OpenMontage — 第一个开源端到端 Agent 视频生产系统，Python 榜

- **事件**：Python 语言榜在榜（+635，总 67,662，forks 8,639，**AGPLv3**）。README 自标 "GitHub Trending #1 Repository of the Day"。
- **核心内容**：
  - **Agent-first 架构：没有代码编排器，你的编码助手就是编排器**。Agent 读流水线 manifest（YAML）→ 读阶段 director skill（Markdown）→ 调 Python 工具 → 自审 → 检查点 → 在创意决策点求你批准。
  - **11 条完整流水线**：动画解释片 / 动态图形 / 数字人主播 / 电影感预告 / 切片工厂（一长源切多条短片并排序）/ **纪录片蒙太奇（从 Archive.org+NASA+Wikimedia+Pexels 建 CLIP 可检索语料，剪真实运动镜头）** / 混合 / 本地化配音 / 播客再利用 / 屏幕演示 / 口播。
  - **统一流程**：`research → proposal → script → scene_plan → assets → edit → compose`，**Web 研究是一等公民阶段**（动笔前跑 15–25+ 次搜索：YouTube/Reddit/HN/新闻/学术，产出带引用的研究简报）。
  - **零 API key 就能出真视频**：Piper TTS 离线旁白 + 免费归档素材 + Remotion（React）或 HyperFrames（HTML/GSAP，**已推送项目**）渲染 + FFmpeg 后期 + 内置字级字幕。
  - **规模**：100+ 生产工具 / 60+ 供应商集成 / **700+ agent skill 与生产知识文件**。供应商由**7 维评分选择器**（任务契合/输出质量/可控性/可靠性/成本效率/延迟/连续性）自动排序。
  - **质量门**：交付承诺强制**阻断"像幻灯片"的渲染**、渲染前校验计划、**渲染后强制自审（ffprobe + 抽帧 + 音频分析）**，所有供应商选择与回退都记进可审计决策轨迹；**预算治理**（执行前估价、花费上限、逐动作审批阈值）。
- **为什么值得关注**：**"Agent 编排整条生产流水线"从代码领域扩到视频制作**，且抓到两个真实痛点：①**"免费 AI 视频"通常偷偷指"把静图动起来"**，它偏要做真素材剪辑；②**没有代码编排器**——直接把 harness 当运行时。**渲染后强制自审 + 预算上限**是本期"交付质量门"最完整的样本。

### 5. microsoft/litebox — 微软安全导向的 library OS，Rust 榜

- **事件**：Rust 语言榜在榜（+44，总 3,126，forks 166，MIT），**v0.1.0 Initial release 2026-10-07**。
- **核心内容**：
  - **library OS（把 OS 当库链接进进程）**，核心主张：**大幅削减对宿主机的接口面，从而缩小攻击面**。
  - 架构是 **"North / South" 解耦**：给一个 `Platform`（South）接口，就暴露一个 Rust 风格、类 `nix`/`rustix` 的 "North" 接口。**任意 North 与任意 South 可互连**。
  - 四个例子贯穿：**在 Windows 上跑未修改的 Linux 程序** / 在 Linux 上沙箱化 Linux 应用 / 跑在 **SEV-SNP** 上 / 在 Linux 上跑 **OP-TEE** 程序 / 跑在 **LVBS** 上。
  - **同时面向内核态与非内核态场景**。
- **为什么值得关注**：**与已推送的 mxc（微软沙箱 SDK）、agent-sandbox（K8s CRD）同属"隔离层不自造、只做统一策略面"这条主线，但这一次下沉到了 library OS 层级**——不是包壳（bubblewrap/seatbelt）也不是 microVM，而是**把宿主接口裁剪到最小**这个更激进的方向。且"任意 North 配任意 South"这个设计让同一套安全边界可跨内核态/用户态复用。**微软在隔离层上已同时押注三条路线**（策略面 mxc / 编排面 agent-sandbox / 内核面 litebox）。

### 6. Donchitos/Claude-Code-Game-Studios — 把单人会话变成 49 agents 的游戏工作室，Shell 榜

- **事件**：Shell 语言榜在榜（+79，总 26,269，forks 3,722，MIT）。
- **核心内容**：
  - **49 agents / 74 skills / 12 hooks / 13 rules / 39 模板**，按真实工作室三层组织：**Tier 1 总监**（创意/技术/制作人）→ **Tier 2 部门主管**（game-designer/lead-programmer/art-director/audio-director/narrative-director/qa-lead/release-manager/localization-lead）→ **Tier 3 专家**（23 个具体工种：引擎/网络/工具/UI 程序员、系统/关卡/经济设计师、技术美术、音效、写作、世界构建、UX、性能、DevOps、分析、安全、QA、无障碍、LiveOps、社区）。
  - **引擎专业化**：Godot 4 / Unity / **Unreal Engine 5 三套 agent 集**（各带子专家，UE 走 GAS/Blueprints/Replication/UMG）。
  - **模型分级写在 frontmatter**：3 个总监要 Opus，lead-programmer 与 15 个专家点名 Sonnet，**其余 30 个继承你当前会话的模型**；README 明确 "把层级当作角色资历，不是账单方案"。
  - **本期最诚实的一组数据**：同一 brief 在四个 `modes.rigor` 下建了四款游戏，统计**写第一行游戏代码前产出的文档数**——`minimal` **1 篇**（一页 brief，0 分钟）；`standard` **30 篇**（58 分钟）。全部产出可运行、有测试的游戏。然后**两名盲评 + 一名人类试玩把 `standard` 版排最后**——**多出的 29 篇文档买到的是可追溯性，不是更好的游戏**。
  - **"跑起来并看一眼"是硬门**：任何改变玩家可见内容的 story，**不在游戏被启动、被观察、截图存进 `production/qa/evidence/` 之前不许关闭**；"**解析通过不等于跑过**"；`minimal` 档可免自动测试但**免不了"看一眼"**。
- **为什么值得关注**：**这是"多 Agent 编排"第一次给出带盲评的安排成本实证，而且是自认失败的一版**（文档多≠游戏好）。同时确立一条与 Game Studios 场景匹配的质量门：**视觉产物必须以截图证据闭环**。与已推送的 ECC（71 agents 通用）、OpenMontage（渲染后自审）共享"产物必须被亲眼验证"这条纪律。

### 7. willfaust/Madeira — 无越狱在 iPhone 上跑 Windows PC 游戏，C 榜

- **事件**：C 语言榜在榜（+294，总 2,331，forks 308，**GPL-3.0-or-later + Madeira Converter Exception**）。0.1.0→0.1.3 在 10-01~10-03 四连发。
- **核心内容**：
  - **不越狱**，把未修改的 Windows 游戏跑在单个 iOS app 里。四层：
    - **FEX-Emu**：运行时把游戏的 x86/x86-64 翻译成 ARM64；
    - **Wine 11.4 为 ARM64EC 构建**——Wine 本身原生跑，**只有游戏自己的代码被翻译**；32 位游戏走 WoW64；
    - **DXMT**：用 Metal 画 D3D 9/10/11；
    - **madeira-d3d12**：自研 D3D 12 on Metal，**运行时用 Apple Metal Shader Converter 转换 DXIL shader**。
  - **iOS 应用不能启动别的程序 → 一切在一个进程里**，连 Wine 的 server 都退化成线程。
  - **Steam 集成完整**：登录、浏览已拥有游戏、安装更新、通过 Valve 自己的 Windows Steam 客户端启动（Madeira Dock）；**Steam Cloud 存档**双向同步并**从不静默覆盖双侧都改过的存档，被替换的一律备份**。
  - **硬门槛写明**：iOS 26+（唯一可靠版本）、**必须 JIT**（iOS 只在调试器附着时允许）→ 因此**永远不可能上 App Store**；免费 Apple ID 签名 7 天过期需每周续签。
  - **自曝**："活跃研究项目，很多游戏能启动、部分玩得好，但性能与兼容性逐游戏不同，且变化很快。**预期粗糙边缘。**"
- **为什么值得关注**：**"翻译层 + 兼容层 + 图形层"三段解耦在移动端第一次完整落地**，且把"合法可行的绕行路径"（JIT 需调试器 → 明确放弃商店分发）当成产品前提而非缺陷。与已推送的 winlator（Android 跑 Windows 应用）、GameNative、AnyPS5（PS5 可执行文件移植）共同说明:**"跨平台运行别人平台的软件"是本期最热的一类工程项目**。

### 8. YuE2（multimodal-art-projection/YuE）— 符号 + 音频统一的前沿音乐生成，Python 榜

- **事件**：Python 语言榜在榜（+216，总 11,833，forks 1,344）。机构署名：HKUST / M·A·P / Tokenwave.AI / NYU / Stanford / MBZUAI / NOIZ / ACE Studio。
- **核心内容**：
  - **主张"在符号里作曲，在声音里创作"**——同一套生成能力同时覆盖**符号（乐谱）与音频**。
  - **前沿质量的自证口径**：在自建 **WildSongBench（192 prompts，2026-09-12，自动评测）** 上**与 Suno v5/v6 有竞争力**；YuE2（best-of-8）取得 **6.9632 SongBench Avg，是所有被评测设置中观测到的最高均值**；坐标轴为归一化对比指数，气泡面积表示 AudioBox 制作质量。
  - **零样本翻唱（zero-shot covers）+ Agent 式编辑**：同一 checkpoint 可以做风格重编、"就乐谱/编曲/歌词展开对话式精修"。翻唱路径先由 **SheetSage2** 转录参考录音（MIDI 派生合成监督 + 结构化解码 + 自回归蒸馏，八个基准集评测），再生成。
  - **Agent skill 化**：`yue2-music` skill（v1.2.0，09-25）"把一句描述、ABC 乐谱或参考录音变成器乐"。**默认流程 = YuE2 写谱 → 把 Vocal 音符搬到器乐轨 → 渲染**；只有明确要求才新作曲。skill 会保留人声音高/起音/时值并记录重叠部分，**但仍需人耳检查人声泄漏与旋律保真**。
  - 配 **MERT2（full-song 编码器）**、**SheetSage2**、**WildSongBench 数据集** 三个 HF 资产，在线免费试用 + Music Arena 投票。
- **为什么值得关注**：**"符号规划 + 音频生成"这条技术路线第一次拿出可与 Suno 正面比的前沿分数**，且**把评测集、编码器、转录模型一并开源**。同时它示范了生成式项目的一种交付形态：**发布 agent skill（而不仅是模型权重）**，并把"仍需人耳验收"写在关键路径上。与已推送的 VoxCPM（TTS）共同构成"开源音频生成"的双子位。

### 9. breferrari/obsidian-mind — 给编码 Agent 装一个会自我组织的 Obsidian 大脑，TS 榜

- **事件**：TypeScript 语言榜在榜（+69，总 5,269，forks 597，MIT）。支持 Claude Code（完整）/ Codex CLI / Gemini CLI。
- **核心内容**：
  - **一个 Obsidian vault 就是 Agent 的持久记忆**：North Star、活跃项目、组织成员、决策记录、绩效档案、事故档案。
  - 会话式命令落到实处：`/om-standup`（读 North Star + 活跃项目 + 未结任务 + 近期 git 变更 → "你有 2 个活跃项目，auth 重构卡在 API 契约上，2 点要跟 Sarah 1:1，上次她点了可观测性"）；`/om-dump`（开会随口一说 → **自动更新 org/people/Sarah Chen.md、建 1-1 记录、建决策记录"Redis 迁移延到 Q2"、写进 Brag Doc、更新活跃项目加"发布前加错误监控"**）；`/om-incident-capture <slack 链接>`。
  - 集成 **obsidian-cli（kepano）+ obsidian-skills + qmd 语义检索**；Node 22+；Obsidian 1.12+；`shardmind install` 或 `git clone` 同一 vault。
  - 多语言 README（en/ja/zh/ko）。
- **为什么值得关注**：**记忆层第五条路线 = "把笔记应用本体当存储"**（前四条：claude-mem 服务端有界披露 / engram 单 Go 二进制 + SQLite / atlas 会话数据库 / billion-context 可逆压缩）。它的**独特点是把"人已经拥有的知识结构"（人物页、决策记录、Brag Doc）作为记忆 schema**，而不是自造一套笔记格式——**记忆写作的目标从"给 Agent 看"扩展到"给人做绩效与 1:1 用"**，这一点很新。

### 10. jakubantalik/transitions.dev + kushagrasinghx/BitChord — 「动效」与「客户端」两条小切口，HTML/Kotlin 榜

- **事件**：transitions.dev（HTML 榜，+103，总 5,022，forks 217）；BitChord（Kotlin 榜，+94，总 3,036，forks 283）。
- **核心内容**：
  - **transitions.dev**：**43+ 手作 CSS 过渡**，每张卡演示一个交互模式并给一段**可粘贴的独立 CSS 片段**（`:root` 语义自定义属性 + `t-*` 命名空间类 + `@media (prefers-reduced-motion: reduce)` 守卫）。`npx transitions-dev add card-resize` 单条拉取（免费无需账号），Pro 走**设备流无密码登录**（终端里不放 API key）。**同时作为 agent skill 分发**（`npx skills add Jakubantalik/transitions.dev`，18 个逐过渡参考文件 + `_root.css`），并附带 `transitions-ui-generation`：**让任何 UI 看起来像 Agent 正在生成它**——先从元素自身结构画出点状线框，再揭晓真实 UI（两种模式：`skeleton` / `skeleton-texts` 带 agent 日志）。**skill 由 index.html 生成，保证片段与演示站一致**。
  - **BitChord**：现代 YouTube Music 客户端，审美取自 Apple 系；本地文件 + YT Music 后端。
- **为什么值得关注**：**"动效"被做成可拉取、可粘贴、尊重减弱动效偏好的基础设施**（这一点比多数动效库做得细），并且**演示站 → skill 单向生成**避免了文档与实现漂移——这是已推送 guizang-ppt-skill、diagram-design 之外的第三种分发工程做法。`transitions-ui-generation` 则把"**AI 正在生成**"这个视觉隐喻本身做成了可复用动效。

---

## 三、其他趋势速览

**本期新面孔（按增幅，未进详细）**

| 仓库 | 语言 | 总 Star | 增幅 | 一句话 |
|------|------|--------:|-----:|--------|
| tgeorgiadis/quiver-launcher | C# | 1,803 | +79 | GitHub/GitLab release 启动器 3.x；标签筛选 + Quiver 目录 + **Thunderstore/GameBanana mod 管理**；2.4.x 无法原地升 3.0（须手动迁库） |
| omacom/omarchy | Shell | 44,700 | +92 | DHH 的"美观、有趣、agentic"Linux 发行版；手册在 `manual/` 为唯一权威源（31 章） |
| gtsteffaniak/filebrowser | Go | 8,689 | +64 | Web 文件浏览器 |
| utkarshdalal/GameNative | Kotlin | 11,230 | +48 | Android 原生跑 PC 游戏，Steam/Epic/GOG/Amazon 集成（与 Madeira 同类） |
| opendataloader-project/opendataloader-pdf | Java | 29,659 | +56 | 面向 AI-ready 数据的 PDF 解析器，自动化 PDF 无障碍 |
| deanpeters/Product-Manager-Skills | Shell | 7,312 | +38 | **77 个 PM 框架技能 + 6 命令工作流** v0.84；MITRE 问题框定画布、Geoffrey Moore 定位模板、Amazon Working Backwards 新闻稿；**功能与教学双目标**；CC BY-NC-SA 4.0 |
| google/skills | Python | 21,226 | +43 | Google 官方"Google 产品与技术"Agent Skills |
| expo/skills | Shell | 2,801 | +56 | Expo 官方 Agent Skills 集 |
| Paymenter/Paymenter | PHP | 2,639 | +126 | 免费开源主机商网店（PHP 榜第 1） |
| karatektus/pl_mail | PHP | 286 | +30 | 自托管 Gmail 风格多账号 IMAP 邮件客户端 |
| nautechsystems/nautilus_trader | Rust | 29,901 | +36 | 生产级 Rust 原生交易引擎（确定性事件驱动） |
| YuKongA/ghostlock-app | Kotlin | 1,857 | +38 | **CVE-2026-43499 futex 提权一键执行 App**；按 `uname -r` 精确匹配内核 profile，**核心修复过的内核拒绝**（退出码 6）；偏移提取器**从不从邻居内核族猜值**，输出一律标注"未验证候选" |
| Armur-Ai/Pentest-Swarm-AI | Go | 2,875 | +50 | 渗透测试 Swarm |

**厂商官方继续落子**：**microsoft/litebox**（library OS）、**google/skills**、**expo/skills**、**EpicGames/unreal-engine-skills-for-claude-code-plugin**（+30，UE 官方 Claude Code 插件）。

**已推送仓库新版本/新动态**

| 仓库 | 新版本 | 时间 (UTC) | 备注 |
|------|--------|-----------|------|
| paperclip | canary v2026.1013.0-canary.0→4 | 10-13 01:45–05:26 | **今日 5 连发**：任务持久化项目级选项、聊天停止轮询失败 run、用户头像 |
| claude-mem | **v13.36.0 → v13.36.1 → v13.37.0** | 10-12 18:12 → 10-13 03:07 | 单日三版 |
| hyperframes | v0.8.150 → **v0.8.151** | 10-12 14:18 / 10-13 04:33 | 连续两日 |
| cua | Spaces v0.8.0-beta.4/5 + **cua-driver-rs v0.35.0** | 10-12 22:53 / 10-13 02:52 | |
| Octop | **v1.0.2b7** | 10-12 12:31 | 上期还是 b6 |
| openrig | **v0.6.10** | 10-12 07:01 | |
| hindsight | integrations/* 批量发版（vapi/smolagents/pipecat/paperclip/opencode） | 10-12 10:2x–10:4x | 主包未动，**集成层密集迭代** |
| open-code-review | v1.12.13 | 10-08 | |
| AI Engineering from Scratch | Edition 2026.10.2 | 10-10 | |
| **长期无新版** | WeKnora v0.8.2（**连续第 8 期**，09-24）、text-to-cad v0.7.21（10-11） | | |

---

## 四、当日主线判断

1. **主榜固化已成常态，本期接近极限**：daily/weekly/monthly 共 42 条里**只有 3 条全新面孔**，10 条详细中 7 条被迫从语言榜取。**"新面孔只在语言维度和月度榜"应视为当前稳定结论**，不必再期待主榜 daily 出新。
2. **"技能集"赛道出现明确分歧**：本期同时有 mattpocock/skills（小而可改、**不接管流程**、20 技能）、Donchitos/Game-Studios（49 agents 重度编排）、deanpeters/PM-Skills（77 框架、**功能与教学双目标**）、google/skills、expo/skills（厂商官方）。**关键分野是"是否接管你的流程"**——Matt Pocock 直接在 README 点名批评 GSD/BMAD/Spec-Kit 夺走控制权，这是本期最有立场的一句技术判断。
3. **"多 Agent 编排"收到第一份带盲评的负面实证**：Game Studios 自曝 30 篇文档的 `standard` 版被盲评排最后，**多出的文档只买到可追溯性**。这直接反驳了"编排越重越好"的默认假设。
4. **交付质量门继续收紧，且开始针对具体产物类型**：Game Studios「改可见内容必须截图存证，解析通过≠跑过」、OpenMontage「渲染前校验 + 渲染后 ffprobe/抽帧/音频自审 + 交付承诺阻断幻灯片渲染」。**质量门从"检查代码"转向"亲眼检查产物"**。
5. **隔离层全线下沉**：微软同日不同层级三押注——mxc（策略面，委托 bubblewrap/seatbelt/microVM）、agent-sandbox（编排面，K8s CRD）、**litebox（内核面，library OS，削减宿主接口面）**。**"North 配任意 South"这种接口解耦设计**值得直接借鉴。
6. **记忆层出现第五条路线且最"人间"**：obsidian-mind 把**人已有的知识结构**（人物页/决策记录/Brag Doc）当记忆 schema，记忆写作的目标从"给 Agent 读"扩展到"给人做绩效与 1:1"。**五条路线（服务端有界披露 / Go+SQLite / 会话库 / 可逆压缩 / 笔记应用本体）star 数无明显高下，说明尚未收敛。**
7. **"跨平台跑别人平台的东西"是本类目最热**：Madeira（iPhone 跑 Windows 游戏，无越狱）、winlator、GameNative（Android 跑 PC 游戏）、AnyPS5（PS5 可执行文件移植）、quiver-launcher（从 GitHub/GitLab release 装应用）。**共同点是靠"翻译层+兼容层+图形层"三段解耦，且都不掩饰合法绕行路径（如放弃商店分发）。**
8. **课程类项目开始"技能化 + 证据化"**：ai-engineering-from-scratch 用 9 个 agent skill 分发课程，并要求真实主机的可发现性/调用/脚本/卸载证据，**"缺 preflight 就明说证据待补"**。
9. **诚实披露已进入第五级：主动交出对自己不利的对照数据**（Game Studios 盲评排名、Madeira「预期粗糙边缘」、diagram-design 明说"没有可 diff 的源格式，文档改动频繁就用 Mermaid"、ghostlock 偏移提取器"从不猜值、输出一律标注未验证候选"）。
10. **非 Agent 项目 4/10**（Madeira、transitions.dev、quiver、BitChord），与 10-09、10-12 持平；但**官方/大厂项目占比回升**（微软 litebox、Google skills、Expo skills、Epic UE 插件、YuE2 八机构联署）。

---

## 五、执行说明与本期方法论增量

- **数据源**：`github.com/trending` 主榜 daily/weekly/monthly（9/11/22 条）+ **18 个语言维度榜**（python/typescript/rust/go/c/c++/javascript/java/swift/vue/html/cuda/jupyter-notebook/csharp/kotlin/ruby/shell/php，日榜）→ 231 条去重。本期把语言榜从 14 个扩到 18 个（新增 csharp/kotlin/ruby/shell/php），**新增 5 个榜共贡献 8 个有效新面孔**（quiver/omarchy/BitChord/pl_mail/nautilus/ghostlock/PM-Skills/Paymenter），**扩榜收益仍然为正**。
- **抓取**：21 个并发 × 每 URL 8 次重试（判据 `code==200 && size>100000`），**本期 0 次重试、一次全过**（上期 10-09 曾大面积 504）。curl 落盘 + 本地解析，**GitHub REST API 全程未使用**。
- **解析器修正（重要）**：本期首版解析出现两个 bug，均已修复——①`/trending` 页面 repo 链接的 `<a>` 带 `data-hydro-click` **前置属性**，`href` 后紧跟 `class="Link"><svg` 才能命中（不可用 `<h2[^>]*>\s*<a href=`）；②**总 star 数在 `</svg>` 之后**（`/stargazers"[^>]*>.*?</svg>\s*([\d,]+)\s*<`），首版误把 "45,327 stars today" 的增幅当总数、结果全部 total=0。详见 kb 方法论文档 v1.2.0。
- **README 读取**：一律 `curl` 三支兜底（HEAD/main/master）+ `grep -n '^#\+ '` 先看章节再 `sed -n` 定点读；tinyjsapp 99KB、ai-engineering 112KB、obsidian-mind 50KB、diagram-design 52KB 均未整篇读。
- **`releases.atom` 解析**：仍需按 `<entry>` 块正则解析（`<updated>` 在 `<title>` **之前**，顺序反直觉）。本期 diagram-design / openmontage 的 atom **0 entry**（无 release），改从 README 取。

> **口径说明**：`gain` 随榜位不同（daily="stars today"、weekly="stars this week"、monthly="stars this month"），**跨榜不可当同口径比较**。表中增幅列已标注口径，未标注者为单榜唯一来源。
