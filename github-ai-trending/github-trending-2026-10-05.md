# GitHub 趋势日报 · 2026-10-05

> 数据源：github.com/trending 三榜合并（daily 16 条 + weekly 19 条 + monthly 23 条）
> 筛选口径：当日新增 Star 高 + 技术方向有代表性 + 与前十期（09-17 ~ 10-02）推送清单不重复
> 本期构成：**9 条全新面孔 + 1 条已推送仓库的重大新版本**（claude-code v2.1.289）

---

## 一、榜单速览

| # | 仓库 | 语言 | 总 Star | 增幅 | 来源 | 一句话 |
|---|---|---|---|---|---|---|
| 1 | [antirez/ds4](https://github.com/antirez/ds4) | C | 23,452 | +211 (today) | daily | Redis 作者为 DeepSeek V4 写的专用本地推理引擎 |
| 2 | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | TS | 96,144 | +628 (today) | daily | 跨会话持久记忆，hook 自动捕获 + 三层检索 |
| 3 | [pingdotgg/t3code](https://github.com/pingdotgg/t3code) | TS | 25,187 | +490 (today) / +1,304 (week) | daily+weekly | Agent 控制面，手机/网页/桌面遥控本机各 harness |
| 4 | [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | Python | 63,238 | +245 (today) | daily | 开源 agentic 视频生产系统，12 条生产线 |
| 5 | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) | Python | 16,879 | +83 (today) | daily | 给 Agent 装 CAD/制造能力，从建模到 G-code |
| 6 | [tester-army/e2e](https://github.com/tester-army/e2e) | TS | 3,150 | +345 (today) | daily | 自然语言 e2e 测试，录制回放零模型调用 |
| 7 | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | JS | 53,091 | +197 (today) | daily | 50 个营销技能，营销成首个成规模非工程垂直 |
| 8 | [garrytan/gstack](https://github.com/garrytan/gstack) · [michael-denyer/pstack-claude](https://github.com/michael-denyer/pstack-claude) | TS / JS | 135,169 / 1,149 | +125 / +232 (today) | daily | 名人/团队 harness 配置打包分发，跨 6 种 harness 移植 |
| 9 | [OpenCut-app/OpenCut](https://github.com/OpenCut-app/OpenCut) | TS | 92,161 | +512 (today) | daily | 开源 CapCut 替代，重写后要带 MCP server |
| 10 | [anthropics/claude-code](https://github.com/anthropics/claude-code) | TS | 149,427 | +5,996 (month) | monthly | **v2.1.289**：一口气修 5 类沙箱/符号链接权限绕过 |

---

## 二、10 条详细

### 1. antirez/ds4（DwarfStar）— Redis 作者亲自下场做"专用而非通用"的本地推理引擎

**事件内容**
- Salvatore Sanfilippo（antirez，Redis 作者）发布 DwarfStar（仓库名 `ds4`），C 写的原生推理引擎，日增 +211，总星 23,452。
- 目标明确且刻意窄：**不做通用 GGUF runner**，只为少数几个开放权重模型做专门优化——DeepSeek V4 Flash（含实验性视觉模型）、DeepSeek V4.1 Flash（Metal + CUDA 文本）、DeepSeek V4 PRO、GLM 5.2/5.3、GLM 5.3 Flash、Qwen3.8 Flash Next。必须用它自己产出的 GGUF 文件。
- 硬件覆盖：**Metal 为主目标**（96GB+ Mac，不足则 SSD streaming）、**NVIDIA CUDA**（主战场是 DGX Spark，同时支持其他后端不支持的 Ada Lovelace 多卡，8×L40S 实测 16 会话 126 t/s 聚合）、**ROCm**（Strix Halo / Framework Desktop）。
- 四个二进制：`ds4`（交互 CLI）、`ds4-agent`（原生 coding agent，直跑推理不起 HTTP 服务，保留 token 历史与 KV 状态）、`ds4-server`（HTTP 服务，默认 127.0.0.1:8000）、`ds4-eval`（内嵌能力回归测试）。
- 工程细节：KV 会话存 `~/.ds4/kvcache`（可 save/list/switch/del/strip，strip 只留文本去掉大 KV）、`--think-level 1..100` 分级推理、`--power N` 用吞吐换 GPU 负载、方向性引导 `--dir-steering-file`、`--mtp` 投机解码、两台 Mac 用 RDMA 做张量并行。
- 显式声明：**"AI full disclosure"** 章节明说本项目在 AI coding agent 强力辅助下开发，并逐条致谢 llama.cpp / GGML（保留了 GGML 作者的版权声明与部分 MIT 源码）。
- 作者还写了段方法论：因为 AI，**软件应该作为"可改模板"而不是"覆盖所有配置的成品"来发布**，建议用户直接让 coding agent 读项目、改项目、为自己的硬件做调优和 QA。

**值得关注的原因**
1. **反潮流路线**：在 llama.cpp 已成事实标准的格局下，选择"为少数模型专门优化"而不是"支持所有模型"，用窄换快。这是对"通用推理框架是否必要"的正面否定，且是知名工程师下的注。
2. **新硬件一等公民**：DGX Spark、Strix Halo、Framework Desktop 被当主力目标而不是兼容列表里的一行，说明 128GB 笔记本 / 256GB 工作站这档硬件的模型适配开始有人专门做。
3. **发布哲学变了**：把"用户会用 Agent 改你的代码"写进 README 并据此设计项目形态——这是 09-28 Madeira 那条"AI 生成代码与上游政策冲突"之后，第一次有知名作者**主动把这件事当成正面设计前提**。
4. **本地 coding agent 独立成型**：`ds4-agent` 不依赖 HTTP 服务，把 token 历史与模型状态绑在一起，是对"本地模型 + Agent"这一形态的具体实现，可与 10-02 的 Pi、09-30 的 OpenShell 放在同一条线上看。

---

### 2. thedotmack/claude-mem — 用生命周期 hook 自动捕获的跨会话记忆层

**事件内容**
- TypeScript，Apache-2.0，日增 +628，总星 96,144，当前 v13.30.0（10-04 发布）。定位是"为 Claude Code 构建的持久记忆压缩系统"。
- 架构五件套：**5 个生命周期 hook**（SessionStart / UserPromptSubmit / PostToolUse / Stop / SessionEnd，共 6 个脚本）自动捕获工具调用观测 → **worker 服务**（本地 HTTP API + Web 查看器，由 Bun 托管）→ **SQLite** 存 sessions/observations/summaries → **mem-search 技能**做自然语言查询 → **Chroma 向量库**做语义 + 关键词混合检索。
- 检索走**三层工作流**（4 个 MCP 工具）：`search` 先拿带 ID 的紧凑索引（~50–100 token/条）→ `timeline` 看某条观测前后的时序上下文 → `get_observations` 只对筛出的 ID 拉全文（~500–1,000 token/条）。官方称 **~10x token 节省**，核心是"先过滤再取详情"。
- 多 harness 覆盖极广：Claude Code、OpenCode、Antigravity CLI、OMP（Oh My Pi）、Grok Bot（无 host hook，改为监听聊天日志文件），另有 OpenClaw 网关一键脚本（可把观测实时推 Telegram/Discord/Slack）。
- 隐私控制：`<private>` 标签排除敏感内容；支持 Cloud Sync 到 cmem.ai（worker 写时同步，无守护进程）；支持 `CLAUDE_MEM_MODE=code--zh` 简体中文模式（内置，无需额外安装）。
- 商业化：安装时引导登录，观察者模式**离线跑（不占你的 Claude 套餐）、免费 14 天**，试用结束自动回落；也支持自带 OpenRouter / Gemini key 或直接用 Anthropic 套餐。CI/非交互场景可跳过登录。

**值得关注的原因**
1. **记忆层的第三条路线**：09-25 的 hindsight 是"服务化 + 用 LLM 做记忆"、ai-memory 是"Markdown+git 为事实源 + 零 LLM"，claude-mem 走的是**hook 自动捕获 + 完全不用手工整理**。三条路线的前提都是跨 harness、跨会话，但成本模型与数据主权假设完全不同。
2. **"先过滤再取详情"是把上下文经济做成产品**：与 09-30 context-mode 的"写代码去读数据"、10-01 codegraph 的"少工具调用"同一族解法——不压缩 token，而是**让不需要的 token 根本不进上下文**。
3. **记忆层开始有可卖的东西**：免费额度不占用户套餐、到期自动回落，这是把"记忆"当成可计费资源而不是纯功能。参照 10-02 freellmapi"时效即付费点"，本期是**额度即付费点**。
4. 反例提示：README 里出现 CMEM 代币（第三方发行、作者"官方拥抱"），这是开源 Agent 基础设施与代币经济混杂的一个样本，值得留意。

---

### 3. pingdotgg/t3code — 不卖模型、不卖额度，只做 Agent 的"控制面"

**事件内容**
- TypeScript，日增 +490 / 周增 +1,304，总星 25,187（仓库无描述，靠 README 说明）。作者是 Theo（pingdotgg）。
- 自我定位：**"agent harness control surface"**——不自己实现 Agent，而是遥控你机器上已经装好并登录的 harness：Claude Code、Codex、Cursor CLI、Grok Build、OpenCode、Google Antigravity。
- 四端齐发：**iOS App（App Store 已上）+ Android App（Play 已上）+ Web（app.t3.codes）+ Electron 桌面**。核心卖点之一是 **remote-ready**：从手机或另一台机器远程访问本机的 Agent 会话。
- 安装路径很齐：`curl … install.sh | sh`（PowerShell 有对应版本）、`npx t3@latest` 免安装试用、`winget`、Homebrew cask、.deb、AUR（stable + nightly 两套，AUR 打包在仓库内维护）。`t3 service install` 可做成后台常驻服务。
- 明确的"我们卖你什么"：**"Nothing."** README 直说不想做产品化收费，灵感来自 Codex desktop / Conductor / Claude Desktop / Cursor Glass 但都不达标，目标是"性能好、远程可用、真开源"，方向错了用户可以 fork 自建。
- 早期状态声明：项目"very very early"，**基本不接受外部贡献**（小修可考虑，大功能不收）。构建工具链用 Vite+（需要全局 `vp`）。

**值得关注的原因**
1. **控制面与 harness 解耦**：这是本期最清晰的一个新品类判断——不抢 Agent 的位置，只抢"你从哪操作 Agent"。复用用户已有的订阅，等于绕开了模型额度与账号体系，也绕开了"要不要自建 Agent"的争论。
2. **移动端遥控成为一等需求**：把 iOS/Android 原生 App 放在与桌面并列的位置（而不是"以后再做的客户端"），与 09-28 stablyai/orca、10-02 starnet 的"多环境状态保持"同向，但这次是直接做成手机 App。
3. **"Nothing." 这种回答正在变成一种产品策略**：10-02 的 starnet（"不模拟收入/已完成工作/模型活动/花费"）、09-30 的 openship（列出需要你自己去云厂商侧加的规则），本期再添一例——**开源 Agent 工具开始用"我不做什么"来建立信任**。
4. 参考价值：`t3 service install` + 多包管理器覆盖 + AUR nightly 通道，是一套可直接照抄的分发方案。

---

### 4. calesthio/OpenMontage — 把"视频生产"整条流水线交给 Agent，且审批门放在渲染前

**事件内容**
- Python，AGPLv3，日增 +245，总星 63,238。自称"世界首个开源 agentic 视频生产系统"，规模：**12 条生产线、100+ 工具、700+ agent skills**。
- 关键区别（README 主动强调）：不只是"把几张静图动起来"。它能为免费/开源工作流做**真正的视频**——从免费素材库和开放档案建立语料、检索真实动态片段、剪成时间轴、渲染成片。
- 两种入口：① 从零描述；② **粘贴一个你喜欢的参考视频**（YouTube/Short/Reel/TikTok/本地片段），Agent 分析转写、节奏、场景、关键帧、风格后，给出 2–3 个差异化方案 + **诚实的工具路径 + 成本估算 + 小样**，再决定是否全量生产。
- **Backlot 实时故事板**：本地看板随流水线自填——阶段点亮、脚本落成剧本页、场景卡在生成资产时闪烁、每一次 provider 决策与每一美元花费上墙。**故事板现在是真的审批门**：资产生成会在逐场景 contact sheet（take、prompt、单资产成本、质量分）处暂停，等你在聊天里批准后才渲染。整场生产可 `▶ REPLAY RUN` 按时间戳回放。
- 成本公开：README 直接列案例总价——60 秒皮克斯风格动画短片 **$1.33**（6 个 Kling v3 动态片段 + Google Chirp3-HD 旁白 + 免版税钢琴 + Remotion 合成）；50 秒竖屏变形短片 **约 $4**；七世界音乐短片 **约 $5**。每个官方视频都附完整 prompt、流水线、所用工具与成本。
- 兼容 Claude Code / Cursor / Copilot / Windsurf / Codex 等能读文件、跑代码的编码助手；依赖 Python 3.10+、FFmpeg、Node 18+。

**值得关注的原因**
1. **审批门的位置选对了**：不是渲染完再让你否决，而是**在花钱生成资产之前**用 contact sheet 卡住。这是"人在回路"从口号变成流水线结构，比 09-23 financial-services 把人工签核写进合规声明更进一层——这次是写进渲染时序。
2. **成本透明到案例级**：$1.33 / $4 / $5 这种数字，加上"每个视频附完整 prompt 与工具路径"，让"Agent 做视频"从演示变成可复算的工程。与 09-29 ponytail 主动修正自己数字同一取向。
3. **许可对照**：AGPLv3，对比 09-30 heygen/hyperframes 的 Apache-2.0——同样做"写 HTML 出视频"，两家在授权上完全相反，说明这个品类的商业模式还没收敛。
4. **"从参考视频起步"是正确的交互设计**：把"我想要的风格"从抽象 prompt 变成已有的具体样本，等于用 Agent 做风格迁移 + 成本预估，比空 prompt 高效得多。

---

### 5. earthtojake/text-to-cad — Agent 第一次打通"建模 → 制造"的物理闭环

**事件内容**
- Python，MIT，日增 +83，总星 16,879，v0.7.11（10-03）。一句话定位：给 Agent 装 CAD 超能力。技术底座是 build123d 0.11 + OpenCASCADE 7.9，核心包是 `cadgen`（PyPI 上）。
- **12 个技能**构成完整链条：`cad`（自然语言/图片生成与编辑 CAD 模型，**STEP 为主产物**，可导出 STL/3MF/GLB）、`step.parts`（找标准件：螺丝/轴承/电机/连接器）、`engineering-drawing`（带尺寸标注、隐藏线、孔标注、标题栏的 PDF 工程图）、`dxf`（2D 轮廓/模板/垫片/排料）、`urdf` / `srdf` / `sdf`（机器人描述文件、MoveIt 规划组、仿真器模型与世界）、`sendcutsend`（上传前校验）、`dfam-check`（按工艺测网格可打印性：壁厚、悬垂、支撑体积、构建方向）、`dfm`（钣金/CNC/注塑评审，**每条发现都要带测量证据 + 引用规则**）、`gcode`（OrcaSlicer 切片，用你自己的打印机预设）、`bambu-labs`（推送打印）。
- 多 harness 原生插件：Codex（需 0.142.0+，装了之后 Codex App 侧栏出现 CAD 视图、每个线程旁有 CAD 标签页）、Claude Code、Cursor、Grok Build；Claude Desktop 走 MCP（`uvx --from cadgen==0.7.11 cadgen mcp`）。
- 文档写得极细：安装用 `npx skills add`（并说明 `npx skills update` 会**静默漏掉新技能**，必须用 `add` 覆盖）、退役技能 `cad-viewer` 的清理方式、模型/路径/内容永不外传的分析数据边界、**Windows 11 Smart App Control 会拦未签名的 OCP 原生模块**（报 `DLL load failed while importing OCP`，只能关掉或改用 WSL）。

**值得关注的原因**
1. **Agent 首次进入物理制造闭环**：从"自然语言 → STEP → 工程图 → 切片 → 打印机"全链打通，这是非文本产出物 Agent 化（09-30 视频/3D/Office、10-02 音频后期）之后，**第一次跨到实体**。
2. **"每条发现都要带证据 + 引用规则"**：DFM 技能的设计原则，与 09-18 起反复出现的"证据要求"、09-30 SkillSpector 的 fail-closed 同源——把不可争辩的量化依据写进技能，而不是让模型给建议。
3. **平台限制被写成第一类文档**：Smart App Control 无法加白名单、只能关掉或走 WSL，这种"环境级死路"写清楚比藏着更有价值；同一段还点名"签名不是本仓库能做的事"，责任边界划得干净。
4. 与 09-30 `ahujasid/mcp-for-blender` 对照：一个是 3D 内容创作，一个是可制造的工程件——**3D 这条线正在分成"好看的"和"能造的"两支**。

---

### 6. tester-army/e2e — 把 Agent 步骤录下来回放，让 e2e 测试的模型成本归零

**事件内容**
- TypeScript，Apache-2.0，日增 +345，总星 3,150。TesterArmy 出品，自我定位"下一代 web 与移动端 e2e 测试框架"。
- 用法：**在同一个测试里，先用自然语言让 agent 驱动应用达成目标，再用 locator 与断言验证结果**。示例（升级到 Pro 套餐）：`app.open('/settings/billing')` → `agent.act('upgrade the workspace to the Pro plan')` → `agent.assert('the invoice preview shows a prorated amount')` → `expect(screen.getByRole('status')).toContainText('Pro')`。
- **核心机制**：被后续断言验证过的 agent 步骤会**记录动作，下次运行直接回放，不调用模型**，直到应用发生变化。没有 agent 步骤的测试完全不需要模型。模型可自带订阅、API key 或本地模型。
- 包结构清晰拆开：`e2e`（SDK/runner/CLI）、`@e2e-dev/web`（Playwright 驱动 Chromium/Firefox/WebKit）、`@e2e-dev/mobile`（iOS/Android 模拟器）、`@e2e-dev/github`（把结果发成 PR 评论）、`@e2e-dev/kernel`（托管浏览器）、`@e2e-dev/eas`（托管 iOS/Android 模拟器）、`@e2e-dev/decision`（有界语义动作与断言的决策模型执行器）。
- 上手：`npx e2e init` 会问引擎（web/mobile）与模型供应商，然后写配置和示例测试。文档随包发布，Agent 可离线读 `node_modules/e2e/docs`。
- 遥测可关（`npx e2e telemetry disable` / `E2E_TELEMETRY_DISABLED=1`），且明确不传测试内容、应用内容与凭证；状态标注为"1.0 前 API 仍可变"。

**值得关注的原因**
1. **录制回放是测试领域的成本解**：Agent 测试最大的反对意见是"每次跑都烧 token"。用"首次用模型、之后确定性回放、应用变了才重新用模型"，把成本压成一次性的——这与 09-30 context-mode"不产生中间结果"、10-01 codegraph"少工具调用"是同一族思路在测试域的落地。
2. **自然语言步骤与确定性断言共存**：不要求你全用自然语言（不可回归），也不要求你全写 selector（脆弱）。两者写在同一个测试里，是"Agent 进 CI"这一问题的具体折中。
3. **托管模拟器即服务**：`@e2e-dev/kernel` 与 `@e2e-dev/eas` 把浏览器与移动模拟器做成托管资源，说明**测试基础设施也在走"Agent 需要的算力/设备外包"**这条路。
4. 参照系：与 09-24 HKUDS/CLI-Anything、09-30 openship 一样，属"把 Agent 的配套设施单独做成产品"。

---

### 7. coreyhaines31/marketingskills — 营销成为技能生态里第一个成规模的非工程垂直

**事件内容**
- JavaScript，MIT，日增 +197，总星 53,091，当前 v2.11.17（10-03）。作者 Corey Haines（Conversion Factory 创始人，Swipe Files 作者）。
- 规模：**约 50 个营销技能**，覆盖 SEO & 内容（seo-audit / ai-seo / site-architecture / programmatic-seo / schema / aso / content-strategy）、CRO（cro / signup / onboarding / popups / paywalls）、内容与文案（copywriting / copy-editing / cold-email / emails / social / video / image / sms）、付费与度量（ads / ad-creative / ab-testing / analytics / attribution）、增长与留存（referrals / free-tools / churn-prevention / community-marketing / lead-magnets / co-marketing）、销售与 GTM（revops / sales-enablement / launch / pricing / competitors / competitor-profiling / prospecting / directory-submissions）、策略（marketing-ideas / marketing-psychology / customer-research / marketing-plan / marketing-loops / marketing-council / offers / events / public-relations / influencer-marketing）。
- **结构设计**：`product-marketing` 是共享上下文基座，**所有其他技能在做任何事前都先读它**（产品、受众、定位）。技能之间交叉引用形成依赖图（如 copywriting ↔ cro ↔ ab-testing、seo-audit ↔ schema ↔ ai-seo、customer-research → copywriting/cro/competitors）。
- 安装三条路径：`npx skills add`（可 `--skill` 只装指定几个，注意在 agent 会话内运行会非交互并可能只装到 Claude Code 不读的目录，需显式 `-a claude-code`）、Claude Code 插件、以及标准 Agent Skills spec 兼容的其他 harness（Codex/Cursor/Windsurf）。
- **资助模式有明确边界规则**：Verified Partners（本期为 Converly、Ploy）出资，但"经过审核、披露、与中立选项并列列出、**永不影响核心技能推荐什么**"，完整规则写在 `tools/PARTNERS.md`。发布节奏很快（v2.11.16 加 OpenAI Codex 插件，v2.11.17 接 hyperframes 集成指南）。

**值得关注的原因**
1. **营销是技能生态的第一个规模化非工程垂直**：前十期的技能几乎全是编码/审查/安全/研究。50 个营销技能 + 依赖图 + 上下文基座，说明**技能封装这套模式可以脱离代码场景**，且规模能起来。
2. **"技能图谱"成型**：不再是一堆互不相关的 SKILL.md，而是有基座、有交叉引用、有明确依赖关系的图。这与 10-01 alirezarezvani 的"Skills(how)/Agents(what)/Personas(who) 三层切分"是两个不同方向的体系化尝试。
3. **赞助与中立性被写成可执行规则**：`PARTNERS.md` + "永不影响推荐" + 与中立选项并列，这是 09-30 SkillSpector 量化技能供应链风险之后，**维护者主动给商业化设边界**的第一个清晰样本。
4. **与 hyperframes 互接**：v2.11.17 把 video 技能接上 hyperframes 集成指南，说明技能之间开始形成跨仓库调用——**技能生态出现"依赖他人技能"的现象**，这会引出兼容与版本管理问题。

---

### 8. garrytan/gstack + michael-denyer/pstack-claude — "名人 harness 配置"变成独立分发品类

**事件内容**
- **gstack**（TS，MIT，日增 +125，总星 135,169）：作者 Garry Tan（Y Combinator 总裁兼 CEO）。把 Claude Code 变成一支虚拟工程团队——**23 个专家角色 + 8 个工具**，全部是 slash 命令、全部是 Markdown、全部免费。角色包括 CEO（重审产品）、Eng Manager（锁架构）、Designer（抓 AI slop）、Reviewer（找生产 bug）、QA Lead（开真浏览器）、Security Officer（跑 OWASP + STRIDE）、Release Engineer（发 PR）。
  - 附带一段**方法论自证**：Karpathy 说"自 2025 年 12 月起几乎没手打过一行代码"，Garry Tan 据此给出自己的数据——近 60 天发 3 个生产服务、40+ 功能（兼职，同时全职跑 YC）；按**逻辑代码变更**（非原始 LOC，因为 AI 会灌水）算，2026 年run rate 约为 2013 年的 **810×**（11,417 vs 14 逻辑行/天），并给出完整方法与复现脚本（`docs/ON_THE_LOC_CONTROVERSY.md`）。
  - 团队模式：`./setup --team` + `gstack-team-init required`，仓库不 vendored 任何文件，每次会话做一次限流一小时的静默自动更新检查。OpenClaw 侧有 4 个原生方法论技能上 ClawHub（office-hours / ceo-review / investigate / retro），无需开 Claude Code 会话。
  - 可移植：`./setup --host auto|codex|…` 装到多个 Agent，`./setup --status` 一行一 host 报版本。
- **pstack-claude**（JS，日增 +232，总星 1,149，v0.9.67）：把 Lauren Tan 的 Cursor 技能栈 `pstack` **移植到 Claude Code / Codex / Pi / OpenCode / Gemini CLI / Prime Agent**。有 `poteto-mode` 统一入口，按目标调用正确工作流（planning / features / refactoring / performance / investigation / prototype / PR maintenance / shipping）。
  - 两个细节：① **命名策略 fork 显式声明**在 `tools/forks.json`，跟踪上游同时保留自己的改动；② 配套独立插件 `agent-formal-verify` 给"测试够不到的并发 bug 与不变量"加 **TLA+ 模型检验与 Lean 证明**。零服务端零遥测，脚本本地跑，PR 工具用你的 gh 登录。

**值得关注的原因**
1. **这个品类本期坐实**：09-18 addyosmani/agent-skills、10-01 mattpocock/skills、本期 gstack + pstack-claude —— **"某个知名工程师把自己的 harness 配置打包分发"已经是稳定品类**，且四条路线差异明显（工程技能集 / 反框架的精简集 / 组织化虚拟团队 / 跨 harness 移植）。
2. **跨 harness 移植成为常态**：pstack 从 Cursor 搬到 6 种 harness，与 10-02 Pi 的 7 包、09-30 多 harness 插件清单同向——**"写一次，装到处"** 已经是分发侧的默认期望，不再是加分项。
3. **形式化验证被挂上 Agent 技能**：`agent-formal-verify` 用 TLA+ / Lean 处理"测试够不到的不变量"，这是对 09-24 起"把不可协商约束写进流程"的**数学化升级**——不是加检查项，是加证明。
4. **自证方法学成为标配**：gstack 专门写文档回应 LOC 争议并给复现脚本，与 09-29 ponytail 修正自身数字、10-01 codegraph 两臂屏蔽自家 CLI 是同一趋势——**趋势榜单上的头部项目开始主动削弱自己的漂亮数字**。

---

### 9. OpenCut-app/OpenCut — 开源 CapCut 替代的"重写"，明确要带 MCP server

**事件内容**
- TypeScript，MIT，日增 +512，总星 92,161。定位：web / 桌面 / 移动三端的免费开源视频编辑器。
- 当前状态是**推倒重写**，README 直接列出重写后的目标：**Editor API**、一等公民的第三方插件（靠 plugin-first 架构实现）、**Rust 核心支撑一套代码跑桌面+移动+浏览器**、**MCP server（给 AI agent 用）**、**headless 模式**（自动化与批量渲染）、编辑器内直接放一个脚本标签页。
- 过渡安排清楚：旧版移到 `opencut-app/opencut-classic`（**今天该用的就是它**），opencut.app 仍跑经典版；重写版暂在 new.opencut.app，成熟后接管。
- 开发栈：proto（moonrepo）+ moon 任务编排，`moon run web:dev` / `api:dev` / `desktop:dev`。当前明确**不接受外部贡献**（架构设计期）。
- 赞助方为 fal.ai（生成式图像/视频/音频模型平台）。MIT 许可。

**值得关注的原因**
1. **非 AI 项目把 AI 接口写进重写目标**：MCP server + headless + 脚本标签页，说明"编辑器要不要给 Agent 留接口"这件事，**在非 AI 原生项目里也已变成架构决策而不是附加功能**。这与 09-23 dream-num/univer 把 Office SDK 重定位为 "Office Harness for AI Agents" 是同一条线，但这次是社区型消费级工具。
2. **"Rust 核心 + 一套代码三端"是当前主流重写方案**：与 09-30 t8y2/dbx（Rust/Tauri）、09-25 julyx10/lap（Tauri+Rust）一致，桌面/移动/Web 统一已从"可选"变成"重写时的默认起点"。
3. **重写期把旧版独立成仓库并明说"今天用哪个"**：比"我们正在重写所以现在不能用"务实得多，也避免用户踩到半成品——一种值得照抄的过渡沟通方式。
4. **赞助方是生成式模型平台**：fal.ai 赞助一个剪辑器，暗示"生成资产 → 剪辑"正在被视作同一条生产链（可与 OpenMontage 对照）。

---

### 10. anthropics/claude-code v2.1.289 — 一口气修 5 类沙箱与符号链接权限绕过

**事件内容**（已推送仓库的新版本，10-03 发布；上一期记录为 v2.1.287）
- 本期最集中的是**权限规则被绕过**这一类，共修 5 处：
  1. 复合 shell 命令中**嵌套部分**的 deny/ask 规则，压不住用户安装的 mod 的批准（受管机器上）；
  2. **沙箱自动放行**时，命令前带展开值的环境变量前缀（如 `TZ="$HOME" rm -rf build`）会让 Bash deny/ask 规则匹配不到真正的命令；
  3. 同样在沙箱自动放行下，命令前有**裸变量赋值**时 deny/ask 规则被跳过；
  4. Read deny 规则**不作用于通过符号链接** @ 提及、变更或在 IDE 中选中的文件；
  5. 用户安装的插件**能改写组织托管的 MCP server 登录工具的描述**。
- 稳定性/正确性修复量很大，集中在插件（mod）体系：mod 的 `ui.render` 写出会让行抛错的值导致会话以"不可恢复接口错误"结束（现在引擎改画自己的行）；mod 的 band/pane 画失败不再连带拖垮周围内容（改为单独失败并抛 `ui.fault`）；band 画失败不再短暂让下方卡片让位；终端不认识某边框样式导致启动冻结或强制退出；插件区域高度为 0 却持续增长导致会话以接口错误结束；插件 on-screen handler 异步抛错导致受管/后台会话结束；`plugin list/eval/update` 显示本地文件夹 marketplace 插件的陈旧副本、`--plugin-dir` 符号链接不热重载；升级后**第一个会话加载不了已安装 mod**；插件 pane 在链接含 localhost、路径含 `@`、大写 host 或 `file:` 路径时画不出东西。
- 其他：`agent.spawn` 给 teammates 用、插件 hook 事件共用同一个 agent id、`$.agent.list()` 加 idle 与 waiting 状态；终端对含 tab / 游离转义 / C1 控制字符 / tab+CRLF 的文本不再画到下方行上；mod pane 右对齐内容不再压到关闭标记下；`claude plugin validate` 修两类误判；VSCode 侧**回滚** 2.1.288 一个可能让登出更频繁的 `claude auth status` 改动；大型文件在插件代码面板中改为按最终宽度一次性布局，打开更快。

**值得关注的原因**
1. **沙箱自动放行是新的攻击面**：三条修复（嵌套复合命令、环境变量前缀、裸变量赋值）全是"规则写得没错，但沙箱放行的匹配器看错了目标"。这与 10-01 记录的"7 类凭证脱敏漏洞里 5 类是边界输入"完全同构——**权限系统必须按畸形输入测试，而不是按正常写法测试**。
2. **符号链接再次成为绕过通道**：Read deny 规则对 symlink 无效。同一类问题在 09-30 SkillSpector 的误报攻坚（shell 引号归属与赋值边界）里出现过，说明"路径与 shell 解析"是这类系统的长期薄弱面。
3. **插件系统（Claude Mods）进入"权限自省"阶段**：插件能改写组织托管 MCP server 的登录工具描述——这是 10-02 记录 Claude Mods"可修改更深层行为"的必然代价。本版大量修复都在把 mod 的失败**限制在它自己的区域内**（单独失败、抛 `ui.fault`、不拖垮周围），方向是对的：**先隔离，再谈能力**。
4. **升级后首个会话加载不了 mod** 这类 bug，是"可修改深层行为的插件"带来的新型运维问题——插件生态成熟度开始取决于**生命周期边界是否可靠**，而不只是 API 有多强。

---

## 三、其他趋势速览

**已推送仓库的新动态（本期不展开，仅记变化）**
- [NVIDIA/OpenShell](https://github.com/NVIDIA/OpenShell)（Rust，周 +5,996，总 14,873）— 10-02 发 **v0.1.3-pre.3**（`feat(snap): ship the standalone prover binary in the snap` #3717），10-03 又有 "OpenShell Development Build"。**形式化验证的 prover 开始随 snap 一起分发**，说明"策略变更须经证明"这条线在往可安装的方向走。
- [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)（JS，日 +1,894，月 +30,466，总 154,910）— **v4.10.2（10-03）/ v4.10.3 / v4.11.0（10-04）三连发**。v4.10.2 是安全与可靠性版：**生命周期 hook 不再把插件路径拼进 shell 文本**、慢的 subagent matcher 不再挂住会话、npm 发布改为等测试绿；v4.11.0 修一个自伤 bug——**从 v4.10.2 起 root `plugin.json` 里一行改动让 Codex/VS Code/Qwen 把 ponytail 当成 skills-only Agent Plugin 加载，hook 从未注册、规则从未到模型**，本版删掉该行恢复完整功能；另加 review/audit 的 `reuse` 标签、Hermes 改为只发一次规则集、7 个新 agent 的文档化安装。**教训值得记：Agent Plugin 与 skills-only 插件的行为差异可以静默让整个技能失效。**
- [mvschwarz/openrig](https://github.com/mvschwarz/openrig)（TS，周 +4,251，总 4,991）— **v0.6.5（10-04）**。升级须知三条：① `CODEX_HOME` 与 daemon 不一致要先对齐（受管 resume 现在只用 daemon 选定的 home）；② **升完 CLI 必须重启 daemon**（否则跑的还是旧构建，首次启动会建两个 usage 索引）；③ **Codex seat 的沙箱内现在有网络**（要关就设 `network_access = false`）。另：shell 启动文件不再能改 seat 的 OpenRig 设置（每次启动重放 daemon 的 `OPENRIG_URL`/`OPENRIG_HOME`）；`rig ps` 把卡在"仅 pane 权限提示"的 seat 计入 attention 总数；`rig usage top` 拒绝越界窗口、缺计数器的 seat 显示 unknown 而非 0。**发布说明含"如何测试"章节 + 包 SHA-256 + 明确列出"未测试：macOS 上的真 Claude Code、真 Codex/Pi、Windows"**，这份披露质量在榜单上属第一档。
- [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)（TS，周 +3,096，总 56,784）— 10-02 的 v0.8.108 之后**继续高频连发到 v0.8.127（10-05 01:04）**，节奏未放缓。
- [Effect-TS/effect](https://github.com/Effect-TS/effect)（TS，周 +702，总 16,971）— **effect@4.0.1（10-04）**，配套 `@effect/vitest@4.0.1`。榜单上少见的"非 Agent 基础设施大版本"，TS 生态的生产级 effect 系统进入 4.x。
- [caddyserver/caddy](https://github.com/caddyserver/caddy)（Go，日 +24，总 76,575）— **v2.11.7（10-03）**，v2.11.6（10-01）之后的补丁。
- [getsentry/sentry](https://github.com/getsentry/sentry)（Python，日 +152，总 45,391）— 开发者优先的错误追踪与性能监控，日榜中唯一的传统可观测性项目。
- [vectorize-io/hindsight](https://github.com/vectorize-io/hindsight)（周 +10,623，总 45,509）— 仍停在 v0.10.2（09-29），无新版本；[debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio)（周 +14,689 周榜第 1，总 53,181）仍 v0.5.6（09-23）；[Tencent/WeKnora](https://github.com/Tencent/WeKnora)（月 +10,912，总 32,029）仍 v0.8.2（09-24）。**三者都是"榜单热度高但无新版本"，本期不展开。**
- 其他在榜已推送项：paperclip（周 +8,732）、Agent-Reach（日 +980 / 周 +4,789）、impeccable（日 +1,171 / 周 +4,242）、ai-engineering-from-scratch（周 +4,904）、yoinks（周 +2,361）、MoneyPrinterTurbo（周 +2,291）、GhostTrack（周 +1,778）、coursebook（周 +1,626）、TencentCloud/Octop（周 +1,496）、alirezarezvani/claude-skills（周 +1,024）、tilelang（周 +839）、addyosmani/agent-skills（日 +336）、vercel/next.js（周 +477）。

**月榜仍在但前十期已展开的**：gods-eye-view（+30,324）、archify（+30,184）、i-have-adhd（+26,627）、ECC（+26,306）、open-code-review（+22,080）、freellmapi（+6,502）、NSA/ghidra（+6,321）、trycua/cua（+5,942）、context-mode（+5,116）、financial-services（+4,143）、cursor/plugins（+3,095）、treg（+2,955）、substrate（+2,515）、knowledge-work-plugins（+2,297）、worktrunk（+2,049）。

---

## 四、当日主线判断

1. **"控制面"与"harness"彻底分家（t3code）**。不实现 Agent、不卖模型、不卖额度，只做遥控层并复用用户已有订阅——这是本期最干净的新品类判断。配合 09-28 paperclip（组织治理）与 openrig（harness 编排），Agent 周边的"管理/操作层"已经形成三层：组织层、编排层、控制面层。

2. **Agent 进入物理世界（text-to-cad）**。非文本产出物的 Agent 化走了十期，从视频（09-30）、3D（09-30）、音频后期（10-02）、Office（09-28）终于跨到**可制造的实体件**。而且入口不是"生成好看的 3D"，是"生成能切片的 STEP"。

3. **成本控制的战场从"压缩 token"转到"根本不产生调用"（e2e + claude-mem）**。e2e 用录制回放把 Agent 步骤的模型成本变成一次性；claude-mem 用三层检索让不需要的 token 不进上下文。加上 09-30 context-mode 的"写代码去读数据"、10-01 codegraph 的"少工具调用"，这条线已经连成完整谱系：**不产生中间结果 → 不读取 → 不调用模型**。

4. **记忆层第三条路线落地，且开始有商业模式（claude-mem）**。hindsight 服务化 + 用 LLM、ai-memory 文件化 + 零 LLM、claude-mem hook 自动捕获 + 混合检索。三条路线的前提相同（跨 harness 跨机器），差异全在**成本模型与数据主权**。本期新增的信号是：记忆被当成可计费资源（离线额度 + 到期回落）。

5. **审批门往前挪，且挪到花钱之前（OpenMontage）**。09-23 financial-services 把人工签核写进合规声明，本期 OpenMontage 把审批门写进渲染时序——资产生成前按场景 contact sheet 卡住。**"人在回路"从声明变成了流水线结构。**

6. **技能生态出现"垂直化"与"跨仓库依赖"（marketingskills）**。50 个营销技能 + 共享上下文基座 + 技能互相引用，说明技能封装能脱离编码场景并规模化；而 marketingskills 接 hyperframes 集成指南，意味着**技能开始依赖他人的技能**，兼容与版本管理问题会随之而来。同时赞助与中立性被写成可执行规则（`PARTNERS.md`）。

7. **权限系统的薄弱面被反复证明是"解析"而不是"策略"（claude-code v2.1.289）**。沙箱自动放行下的嵌套复合命令、环境变量前缀、裸变量赋值，加符号链接绕过 Read deny——全是规则写对了但匹配器看错目标。与 10-01 的"7 类凭证脱敏里 5 类是边界输入"、09-30 SkillSpector 的 shell 引号归属攻坚同构。**结论：这类系统必须按畸形输入测试。**

8. **插件/技能生态的成熟度取决于生命周期边界，而非 API 强度（ponytail + claude-code）**。ponytail 因一行 `plugin.json` 让 hook 静默不注册、规则从未到模型；claude-code 本版大量修复都在"让 mod 的失败限制在自己区域内"。**先隔离、再给能力**正在成为共识。

9. **开源工具用"我不做什么"建立信任，且自证方法学成标配**。t3code（"Nothing."）、starnet（不模拟证明不了的状态）、openship（列出你要自己去云上加的规则）、openrig（发布说明带 SHA-256 + 明确"未测试"清单）、gstack（专门写文档回应 LOC 争议 + 复现脚本）、ponytail（连续两期修正自己的数字）。**头部项目在主动削弱自己的漂亮数字。**

10. **非 Agent 项目 4/10**（ds4 属推理引擎基础设施、OpenCut 属消费级工具、Effect 4.0.1、caddy v2.11.7 计入速览）。与 09-28 ~ 10-02 五期的 4/10 持平，结构稳定：**Agent 占六成，基础设施与消费工具各占两成。**

---

*报告生成时间：2026-10-05 09:40 (GMT+8) · 数据源 github.com/trending · 三榜合并去重*
