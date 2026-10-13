# GitHub 趋势日报 · 2026-10-12 14:00（同日第二次运行）

> **数据源构成**：主榜 daily **8** / weekly **12** / monthly **22**，**三榜合计 42 条全部为已推送仓库**（daily 8 条与上午 09:43 那期逐条一致）。
> 本期改用**「语言维度 × weekly/monthly」这一新组合**（上午只用了「语言维度 × daily」），另加**按口语语言筛选**（`?spoken_language_code=zh|en`），共 26 个榜、**353 个去重仓库**，其中 **270 个从未推送过**。本期 10 条详细**全部为全新面孔**。
>
> **口径声明**：GitHub trending 的排序**不是**按增幅排序；下表 `增幅` 列标注了所属周期（今日 / 本周 / 本月），**跨榜不可比较**。语言榜条目的增幅口径为"本周"或"本月"，与主榜 daily 的"今日"不同。

---

## 一、榜单速览（本期 10 条）

| # | 仓库 | 语言 | 总 Star | 增幅 | 来源 | 一句话 |
|---|---|---|---|---|---|---|
| 1 | [lexmount/moli](https://github.com/lexmount/moli) | Rust | 16,628 | +14,631（本月）/ +9,308（本周） | rust-monthly / rust-weekly | 为 Agent 写的 Rust 无头浏览器，结构优先、布局按需，不包 Chromium |
| 2 | [pacifio/atlas](https://github.com/pacifio/atlas) | Rust | 9,589 | +6,589（本月） | rust-monthly | "Agent 的版本控制"：把 commit 挂回产出它的会话，多 Agent 共享一份记忆 |
| 3 | [vastsa/PI-Desktop](https://github.com/vastsa/PI-Desktop) | TypeScript | 6,680 | +4,031（本月） | typescript-monthly | 建在 pi Agent Harness 之上的持久化桌面工作台，插件可扩展桌面本身 |
| 4 | [yyjeqhc/webcodex](https://github.com/yyjeqhc/webcodex) | Rust | 2,252 | +1,610（本月） | rust-monthly | 让云端 AI（ChatGPT/Claude）通过 MCP 用你本机真实仓库与工具链 |
| 5 | [Gaurav-Gosain/tuios](https://github.com/Gaurav-Gosain/tuios) | Go | 5,208 | +1,595（本月）/ +541（本周） | go-monthly / go-weekly | 知道 Agent 在干什么的终端窗口管理器，Agent 之间可互相发消息 |
| 6 | [Neroued/ninfer](https://github.com/Neroued/ninfer) | C++ | 2,936 | +1,361（本月） | c++-monthly | 从零写的单卡（RTX 5090）专用推理引擎，只服务指定 checkpoint |
| 7 | [Gentleman-Programming/engram](https://github.com/Gentleman-Programming/engram) | Go | 7,141 | +640（本月） | go-monthly | 单二进制 + SQLite/FTS5 的 Agent 持久记忆，14 种 Agent 统一接入 |
| 8 | [AtomicBot-ai/atomic-agent](https://github.com/AtomicBot-ai/atomic-agent) | TypeScript | 3,258 | +579（本周） | typescript-weekly | 本地优先 Agent，自研 TurboQuant llama.cpp；Fusion 模式一模型规划一池执行 |
| 9 | [littledivy/mimic](https://github.com/littledivy/mimic) | Python | 2,614 | +364（本周） | python-weekly | 抓一次 App 流量，AI 生成 Python 客户端，把任意 App 当库调用 |
| 10 | [trymirai/uzu](https://github.com/trymirai/uzu) | Rust | 2,185 | +345（本周） | rust-weekly | 端侧推理引擎，Rust 核 + Python/TS/Swift 绑定，吃 Apple 统一内存 |

---

## 二、10 条详细

### 1. lexmount/moli — 为 Agent 重写的无头浏览器（Rust，本月 +14,631）

**事件**：语言榜（Rust）本月/本周双榜第一，总 star 16,628，最新版 **v1.1.16（2026-10-11）**，10-04 起基本日更。

**核心内容**
- **不是 Chromium 包装**：独立浏览器内核，自建生命周期。依赖栈公开写明：`html5ever`（解析）+ `rusty_v8`/V8（JS）+ Servo/Stylo（选择器与层叠）+ Taffy/Parley（盒模型与文本排版）+ AnyRender/Vello CPU（软件渲染）。
- **核心设计是"结构优先，像素按需"**：DOM 与样式是唯一真源；默认 `LayoutPolicy::Mock`（确定性几何、不真跑 layout/paint）；加 `--layout` 才启用真实布局、命中测试、坐标输入、截图、screencast。
- **布局是一次性快照，不是持续维护的状态**：首次几何请求构建工作树 → 冻结成不可变 `FrozenLayoutTree`（与 DOM 解耦）→ 只保留最新一棵；截图永远重建并替换；screencast 只比对不透明 visual-state token，无变化不发帧；**paint 结果永不复用**。
- **三套协议共用同一内核**：CDP / WebDriver Classic / WebDriver BiDi 同一个端点，不需要另装 ChromeDriver/geckodriver；Playwright 可直接 `chromium.connectOverCDP("http://127.0.0.1:9222")`。
- **输出直接为 Agent 优化**：`--dump markdown` / `semantic_tree_text` / `screenshot` / `pdf`；`--eval` 做显式交互后导出。
- **自曝 benchmark**：192 个中英文站点抓取，Moli 有效页 103（53.6%）、中位 1.43s、中位 RSS **73 MiB**；Chrome Headless 101（52.6%）、1.43s、**773 MiB**。Lexbench 1,308 可比任务里 Moli 成功率 81.88%，Chrome 99.85%，Lightpanda 53.29%；中位 CPU 100.6ms / 内存 92 MiB，约 Chrome 的 15% / 13%。
- **边界写清**：不做 GUI 浏览器、无 GPU 合成器、不追求逐像素对齐 Chrome、高保真 Canvas/WebGL/媒体播放不支持；**不支持的协议路径返回显式错误，"绝不假装浏览器动作/事件/网络观测/视觉结果发生过"**。
- 商业模式：开源内核（Apache-2.0 / MIT 双许可）+ Lexmount Browser 托管云运行时（open-core）。

**值得关注的原因**
- 浏览器自动化这条线一直靠"重跑一遍完整渲染"付成本，Moli 把**成本结构本身**改掉：不渲染就不付渲染的钱。这和 10-07 的 rtk（输出进上下文前压缩）、10-09 的 claude-mem（读取边界）、10-12 上午的 billion-context（压缩已消费对话）是同一条主线的第四站——**成本战场从"模型读什么"推进到"运行时算不算像素"**。
- 它和已推送的 `vercel-labs/agent-browser`（原生 Rust 浏览器自动化 CLI）、`ChromeDevTools/chrome-devtools-mcp`（官方 MCP，被动只读 CDP）构成三足：**自建内核 vs 驱动真实 Chrome vs 官方协议桥**。三种信任姿态第一次同框。
- 诚实的 benchmark 姿态（把自己的成功率放在 Chrome 旁边、把"分母"和"未测项"写明）与 10-06 RuView 撤回 100% 指标、10-12 上午 colibri 写 0.05 tok/s 一致，已是新入场者的默认礼貌。

---

### 2. pacifio/atlas — 给编码 Agent 做版本控制（Rust，本月 +6,589）

**事件**：Rust 月榜高位，总 star 9,589，最新版 **v0.3.4（2026-09-28）**；本月为热度回温（无新版本）。

**核心内容**
- **要解决的问题定义得很准**：Agent 写了大量代码但不留下推理。"产生变更的 prompt、它调用的工具、它先试后弃的方案，全都在滚动缓冲区里，直到滚走为止。活下来的只有一条模型写的 commit message。"后果三条：**Agent 每次从零开始 / 换 Agent 就断线 / 上下文散在十处**（知识库、`CLAUDE.md`、`AGENTS.md`、每个 Agent 自己的记忆文件，没有任何东西一次读完）。
- **Checkpoint = commit 挂回会话**：`.atlas/sessions.db` 记录每个会话的 prompt、消息、工具调用、触及文件、应用的 patch；commit（**即使从终端、从别的编辑器、Atlas 关着时提交的**）会被观测并链回产出它的会话；**链接能穿过 amend 和 rebase**（按 patch-id 重指），真歧义时**选择孤儿化而不是猜**。
- **多 Agent 共享一份记忆**：Claude Code、Codex、Atlas 自带 Agent，以及 ACP registry 里任意 Agent（Cursor / OpenCode / Kilo Code…）可并排跑在同一份代码上；每轮把"活跃计划 / 决策 / 文件变更 / 失败 / 架构笔记 + 语义匹配"注入 prompt。**Claude Code 的决策会出现在 Codex 的下一条 prompt 里**。嵌入在本地算，检索不出机器。
- **不锁死**：笔记是 markdown、画布是 JSON、会话是 JSONL、编辑器是磁盘上的文件，关了 Atlas 可以用 vim 接着干；唯一例外是 checkpoint 记录（SQLite，放项目 gitignored 的 `.atlas/`），因为它是被查询的不是被阅读的。
- **`@` 注入先本地解析**：文件/文件夹/符号/分支/commit/笔记/论文/历史会话；**文件夹解析成指针而非粘贴**（`@` 一个 5000 行文件发的是路径，Agent 按需读，不占满整个会话的上下文窗口）。
- 其他：写入前先做密钥脱敏；`Capture health` 每项目一个信号（OK / Degraded / Stopped，各带原因与下一步）；可导入已有 Claude Code 历史。

**值得关注的原因**
- **"Agent 的产出没有出处"第一次被当成产品问题解决**。此前十期的记忆层都在解决"Agent 记得什么"（hindsight / ai-memory / claude-mem / engram），Atlas 解决的是"**代码是谁在什么推理下改的**"——从"记忆"转向"溯源"。
- **跨 Agent 共享记忆 = 把 Agent 从可替换的执行器变成可接力的角色**。这与 10-07 omnigent 的 `switch-agent` 返回 410 要求 fork 形成对照：一个主张"换 Agent 要显式分叉"，一个主张"换 Agent 不该丢上下文"。**会话身份的两种哲学**同时在场。
- 与 10-12 上午的 cc-switch（10 个 CLI 的统一控制面）互补：cc-switch 统一**配置**，Atlas 统一**历史与记忆**。控制面品类继续细分。

---

### 3. vastsa/PI-Desktop — 建在 pi Agent Harness 上的桌面工作台（TS，本月 +4,031）

**事件**：TypeScript 月榜，总 star 6,680，最新 **v0.18.0（2026-10-10）**，紧随其后 **v0.18.0-beta.6（2026-10-11）**（新增加密 S3 配置备份与同步）。

**核心内容**
- **定位明确**：不做"某个模型的包装"，也不做"又一个 IDE 扩展"，而是给 Agent 一个**持久、独立、可扩展的桌面工作区**——项目、会话、评审、预览、Agent 都住在自己的空间里，不依赖特定 IDE 或终端。
- **技术栈**：Electron + **Rust host core** + **pi Agent Harness**（即 10-05 记录的 `earendil-works/pi`）+ 可安装插件。README 直写"**Pi 提供 Agent 引擎，PI-Desktop 围绕它构建持久工作区、会话、权限、插件与编排**"。
- **插件不止扩展 Agent，还扩展桌面本身**：面板 / 视图 / 浮动挂件 / 主题 / 后台服务 / MCP server / 插件间消息总线；分发为 `.piplug` 包 + 插件市场。
- **权限是一等公民**：特权操作一律过 PI-Desktop 的权限层；插件按风险等级分档（10-10 的 beta.4 专门做"插件权限风险档位与权限矩阵对齐"）。
- **编排**：可委派 Subagent，也可并行协调完整 Worker Session；模型可换（云 / 本地 / 自定义网关），不必重建工作流。
- 其他：本地优先、模型无关；支持 macOS/Windows/Linux。

**值得关注的原因**
- **上一代项目成为下一代地基，本期第二次验证**（10-05 是 `cloudflare/cloudflare-os` 依赖 pi 的 `pi-agent-core`）。pi 从"自扩展 harness"变成了**桌面产品的引擎层**，说明 Agent 运行时的分层已经稳定到可以被人当地基用。
- **"插件扩展桌面本身"是新的**。此前 10-09 的 Docker agent（Agent 是 OCI 制品）、10-08 的 cursor/plugins 都在扩展 Agent 的能力；PI-Desktop 把扩展面提到**工作区外壳**这一层（面板/挂件/主题/后台服务），意味着 Agent 客户端开始像浏览器一样被插件化。
- 与同期 `manaflow-ai/cmux`（Ghostty 终端为 Agent 而做）、`Gaurav-Gosain/tuios`（终端 WM）一起，说明**"Agent 该住在哪里"仍在激烈试错**：终端、IDE、桌面工作台三条路都在加注。

---

### 4. yyjeqhc/webcodex — 让云端 Agent 用你本机的真实环境（Rust，本月 +1,610）

**事件**：Rust 月榜，总 star 2,252，最新 **v0.4.6（2026-10-04）**，被官方标为"长期稳定版，公开工具名将保持稳定"。

**核心内容**
- **架构是 Server + Runner 两层**：AI 客户端（ChatGPT / Claude / 其他 MCP 客户端）→ WebCodex Server（认证与路由）→ 你机器上的 Runner（持有仓库、Git、编译器、测试）。**代码不需要搬进托管工作区**；被请求的文件内容与其他工具结果仍会回传给 AI 客户端（README 明说）。
- **给 Agent 的是真实工具链**：读/搜/检视/守卫式修改代码、跑命令与测试与格式化与编译器、看 Git status/diff、**长任务可观测而不是占住一个模型回合**。
- **人审有落点**：Runtime Console（浏览器里看活动/项目/Session/Agent 通信）、Workflow Session evidence、Jobs、Git/diff 审阅——**不另建一套任务/结果验收子系统**。
- **两种用法**：`webcodex share` 一条命令临时共享一个仓库；或多机接入自建 Server 做长期部署。
- **诚实度罕见**：README 明说六种安装包"**仍需原生构建与安装验收**，真机安装、重启保持、GUI 行为、升级**尚未在三平台全部验收**，本文档**不声称跨平台行为一致**"；v0.4.4/0.4.5 的 Windows 产物被**主动撤回**（warning 块）。
- 安全：`SECURITY.md` 明说 WebCodex 能读改文件、能在项目边界内执行命令，请自管凭证、只注册该给助手访问的项目根。

**值得关注的原因**
- **"云端模型 + 本地环境"这一格此前是空的**。10-08 的 `spotify/portal-ai-plugins`（内部门户接进 CLI）、10-09 的 `docker/docker-agent`（Agent 是 OCI 制品）都在解决"Agent 在哪跑"；webcodex 解决的是"**云端 Agent 怎么用我本机的代码**"，且明确不走"把代码上传到托管沙箱"的路线。
- **和 10-09 `CursorTouch/Windows-MCP`（computer-use）互补**：一个给 Agent 本机 GUI/UI 元素，一个给 Agent 本机**开发环境与工具链**。两条都是"把 Agent 的能力半径扩到用户机器"，风险模型相同（能力换权限）。
- 这份 README 把"未验收"写进正文，是**"诚实披露第三级：修正能力边界"**的又一例，比 10-12 上午 colibri 的 0.05 tok/s 更前进一步——**连"文档声称的行为"都先否掉**。

---

### 5. Gaurav-Gosain/tuios — 知道 Agent 在干什么的终端窗口管理器（Go，本周 +541 / 本月 +1,595）

**事件**：Go 周榜/月榜双榜，总 star 5,208，**v0.9.0（2026-10-08，距 v0.8.5 约 490 commits）→ v0.9.1 → v0.9.2（2026-10-09，含 HTTP/2 与 net/http 安全修复）**。

**核心内容**
- **它是终端复用器 + 窗口管理器**：vim 式模态界面、多 pane、workspace、BSP 平铺、kitty 图形协议、命令面板；基于 Charm 栈（Bubble Tea v2 + Lipgloss v2），事件驱动渲染，空闲 CPU 近零。
- **关键差异是"Agent 状态是一等公民"**：任何程序都能通过 **OSC 7501** 告诉 tuios 它在干什么；daemon 保住会话、能跨机器连会话、**让各个 pane 里的编码 Agent 汇报状态并互相发消息**。文档里 `docs/AGENT_STATE.md` 覆盖：状态、**Inbox**、审批、**fleets**、跨机器、grants、MCP。
- **tmux Shim**：让"驱动 tmux 的工具"（例如 Claude Code 的 agent teams）在 tuios 里照跑。
- **v0.9.0 的实质变更**：任何程序都能上报状态；配置可拆多文件；yank 保留为 paste buffer；`attach -d` 独占会话；ssh agent 跟着进 pane；**连完全没有图形能力的终端也能显示图片**。
- 其他：Homebrew / AUR / Nix / Go install / Docker 五路安装；`tuios update` 会**先检测是谁在管这个二进制**，是包管理器就打印正确命令而不是覆盖它。

**值得关注的原因**
- **多 Agent 协作的"操作系统层"第一次出现在终端里**。此前十期的多 Agent 都在应用层（paperclip 组织化 / openrig 编排 / t3code 控制面 / zeron 控制面），tuios 把它下沉到**窗口管理器的状态总线**：Agent 之间通过 OSC 汇报 + 互相发消息 + Inbox 审批。
- **"控制平面失效常常无声"的正面解法**：Agent 状态不再是各 CLI 自己打印的日志，而是**由终端统一接收的结构化事件**。这与 10-08 `skills-manager`（给状态一个唯一入口，让 Agent 通过它改而不是直接写文件夹）是同一思路。
- `tuios update` 检测"谁拥有这个二进制"这一点很小但很关键：**自更新不得越过包管理器**，与 10-09 `mxc` 的遥测四条件、`agent-browser` 的 checksum 校验同属"更新路径的权限自觉"。

---

### 6. Neroued/ninfer — 单卡专用推理引擎（C++，本月 +1,361）

**事件**：C++ 月榜，总 star 2,936，无 release（源码构建分发）。

**核心内容**
- **范围刻意极窄**：从零写的 C++/CUDA 推理引擎，**只跑 Qwen3.5 系列的 Dense 与 MoE**，**只跑单张 NVIDIA RTX 5090**（构建阶段直接拒绝非 `sm_120a` 架构），运行时**只驻留一个模型、启动时固定 1–8 条执行 lane**。
- **五份官方产物**：Qwen3.6-27B（groupwise-int / nvfp4）、Qwen3.8-27B（groupwise-int / nvfp4）、Qwen3.6-35B-A3B（groupwise-int）；`.ninfer` v3 制品把模型配置、编码权重、逻辑绑定、前端资源打在一起；**v2 制品可在本地升级不必重下权重**。
- **性能自证（并发 MTP3 解码，tok/s / 接受率）**：Qwen3.6-27B nvfp4 在 C=1/2/4/8 为 **202.4 / 399.7 / 699.7 / 1,146.9**；Qwen3.6-35B-A3B groupwise-int 达 **642.5 / 907.2 / 1,213.5 / 1,380.7**。单请求 7,680-token prefill 最高 **17,705 tok/s**（35B-A3B），260,096-token prefill 仍 5,247 tok/s。
- **接口兼容**：本地 CLI + **OpenAI / Anthropic 兼容的 HTTP API**；单请求逻辑上限 240,000 token，共享 240,000-token Device KV 池，KV 类型 fp8（Qwen3.8 用 FP8 E4M3 row-256，Qwen3.6 用 INT8 group-64）。
- **边界诚实**：明确"**没有 install target、没有打包好的二进制分发，只能从源码构建树运行**"；支持范围写死为 Linux + 5090。

**值得关注的原因**
- **"能跑"与"能用"的差距，本期第二次被明码标价**。10-12 上午 colibri 用纯 C 磁盘流式把门槛压到 8GB RAM（代价 0.05 tok/s）；ninfer 反向——**只服务一个 GPU、一个模型族，换取 1000+ tok/s**。两条路并存说明推理引擎市场正在**按场景切片**，而不是追求通用。
- 与 10-07 DeepGEMM-Ascend、10-05 tilelang 昇腾 950 同属"**算力层去单一供应商 + 专业化**"：一端是国产/多厂商后端铺开，一端是**单卡极致优化**。
- 兼容 OpenAI/Anthropic 双线格式已成新引擎的**默认礼貌**（10-12 上午 cc-switch 做四格式互转、10-05 freellmapi 铺满 `/v1` + `/v1/messages` + `/v1beta`），说明**协议兼容层已被默认为基础设施而非差异点**。

---

### 7. Gentleman-Programming/engram（+ gentle-ai）— 单二进制的 Agent 记忆，配一套确定性工程环境（Go，本月 +640 / +1,114）

**事件**：Go 月榜两席。**engram 总 star 7,141，最新 v3.3.2（2026-10-10）**；**gentle-ai 总 star 7,691，17 种 Agent 集成**。engram 另有 `pi-v0.4.2`（2026-10-11）。

**核心内容（engram）**
- **一个 Go 二进制 + 一个 SQLite 文件**：`SQLite + FTS5` 全量检索，**不需要 Node/Python/Docker**；暴露 CLI / HTTP API / MCP（stdio）/ 交互式 TUI 四种面。接入 **14 种 setup target**（Claude Code / Pi / OpenCode / Gemini CLI / Codex / Antigravity / Windsurf / Qwen Code / Kiro / Cursor / VS Code Copilot / Kilo Code / Kimi Code / CommandCode）+ 任意 MCP 兼容 Agent。
- **本地优先、可移植**：本地 SQLite 是权威源；Git Sync 导出**压缩分块**用于跨机器共享；Engram Cloud 可选、**项目级**复制/共享，带浏览器可视化。
- **项目感知**：解析顺序为"显式项目 → `ENGRAM_PROJECT` → cwd 检测"；全局读必须显式 `--all` / `all_projects=true`，**不允许与显式项目混用**。
- **一处值得注意的保守设计**：Codex 的**写操作**要求运行中 core 的 `/health` 响应里声明 `capabilities.runtime_session_resolution: true` 才能解析宿主会话，**`root_session_resume` 单独不够**；不兼容时写操作保持阻塞并给出明确诊断，**只读与非 Engram 调用不受影响**；**hook 永不自动重启 server**。

**核心内容（gentle-ai）**
- 定位是"**你已经用的那个 Agent 的确定性工程环境**"：给它**记忆（Engram）+ 工作流 + 证据**。README 开篇即"你的 Agent 写完代码就忘了一切，对项目没有主张，除了让你逐行读之外没有办法证明它做了什么"。
- **17 种集成**：Pi / OpenCode / Claude Code / Codex / Cursor / VS Code Copilot / Gemini CLI / Kilo Code / Kimi Code / Kiro IDE / Qwen Code / Hermes / Antigravity / Windsurf / OpenClaw / Trae / Conductor，走**原生配置**而非另造一套。

**值得关注的原因**
- **记忆层第四条路线落地：不接 LLM、不建向量库、只用一个 FTS5 文件**。对比已推送的 hindsight（服务化 + LLM 重排）、ai-memory（Markdown+git 为真源）、cognee（图谱 + 本地小模型）、claude-mem（hook + 三层有界检索）——**engram 是"最没有技术含量但最容易运维"的一档**，而它的 star 数不比任何一条路线低。
- **"能力协商写进健康检查"是新的**：`/health` 不只是存活探针，还携带**能力声明**，写操作必须等能力到位才放行；**hook 永不自动重启 server**（宁可阻塞也不静默降级）。这是对"控制平面失效常常无声"最直接的工程回应。
- gentle-ai 的定位值得记一笔：它不提供 Agent，提供**给任意 Agent 装上的纪律**（记忆 + 工作流 + 证据）。与 10-12 上午的 `asd-ste100-skill`（把受控语言装成技能）、10-06 `agency-agents`（把岗位定义成可 diff 的文件）同属"**方法论本身成为可分发资产**"。

---

### 8. AtomicBot-ai/atomic-agent — 本地优先 Agent，Fusion 模式（TS，本周 +579）

**事件**：TypeScript 周榜，总 star 3,258。**v0.6.7（2026-10-07）** + **Desktop v0.0.1（2026-10-07，首个公开桌面版）**。README 自标"Developer preview，API/命令/配置/行为仍在变，需要稳定集成点请 pin 版本"。

**核心内容**
- **控制循环与全部状态都在你机器上**：能浏览网页、读写文件、跑经批准的 shell 命令、检视文档、跨会话记忆、定时跟进、通过 MCP 调外部工具。可**纯本地模型、纯云模型，或两者同时**。
- **Fusion 模式**：一个模型负责规划，**一池 worker 负责执行**。
- **自研 TurboQuant `llama.cpp`**，README 称在小本地模型上带来 **+30–50% 吞吐**；"llama.cpp first"，让小的量化模型在消费级硬件上撑得住长多步任务。
- **自证 benchmark**：GAIA validation Level 1（53 题），Atomic Agent 与 Hermes 驱动**同一个**本地 `qwen-3.6-35b-a3b`（`llama-server`、UD-Q4_K_XL），**同样的步数与超时预算，唯一变量是 agent loop**：**Atomic Agent 69.8% vs Hermes 58.5%**。
- **首次运行的迁移向导**：可选导入 **Claude Code**（skills / memory / MCP servers / sessions + 可选 provider keys）、**Codex**（skills / memory / sessions + 可选 keys）、**Oh-My-Pi**（skills / MCP / sessions）、**Pi**（skills / sessions）、**Hermes**（sessions / cron + 可选 keys）、**OpenClaw**（sessions / cron）。原则：**不覆盖已存在的、不动源数据**。
- **卸载写得比安装还细**：一条命令删掉状态目录（配置/记忆/会话/任务/trace/已下载模型）+ 二进制与别名 + 资源目录 + 安装器写进 shell rc 的那一行；**先打印将要删除什么及体积，再要求你手打 `uninstall` 这个词**；支持 `--dry-run` / `--keep-data` / `--keep-binary` / `--keep-path` / `--yes`。
- 其他：HTTP 与 Tauri sidecar 两种嵌入方式；`/compact` 自动压缩（对话占满模型窗口留出的 90% 时触发，压到约 65%，**完整会话转录仍在磁盘上不变，当前任务的开场请求与最新消息逐字保留**）。

**值得关注的原因**
- **"本地优先 Agent"第一次给出可比的 agent-loop 基准**。GAIA L1 上 69.8% vs 58.5%，控制变量做得很干净（同模型、同步数、同超时），**说明在本地小模型上，harness 的差距可以大于模型的差距**——这对"要不要换更大模型"是个反向结论。
- **导入清单等于一张 Agent 生态地图**：Claude Code / Codex / Oh-My-Pi / Pi / Hermes / OpenClaw 六家可迁移，说明**用户数据（skills/memory/sessions）已经开始跨 harness 流动**，和 Atlas 的"跨 Agent 共享记忆"、cc-switch 的"10 个 CLI 统一控制面"是同一趋势的三个切面。
- 卸载流程（打印 + 打词确认 + 四项 keep 开关）是**"数据主权"在安装器层面的落地**，比多数项目对"我到底删了什么"更负责。

---

### 9. littledivy/mimic — 抓一次流量，AI 生成 App 客户端（Python，本周 +364）

**事件**：Python 周榜，总 star 2,614，无 release（`uv tool install` 分发）。作者 littledivy（Deno 生态开发者）。

**核心内容**
- **一句话**：拦截任意 App，然后**像调库一样从 Python 调它**。示例即 `Hinge().get_recommendations()` / `acc.like(subject_id, comment="hi lol")`——而 `hinge_client.py` **不是手写的，是 AI 读抓到的端点生成的**。
- **原理讲得很直白**：多数 App 的每个请求都带同一组认证值（bearer token、device id、session id、cookie），**这些值跨调用是稳定的**；从你真实发出的一个请求里抓一次，就能在新请求里重放。
- **三步流水线**：`capture traffic (mitmproxy) → extract auth (mimic.Session) → generate client (claude 读抓到的端点)`。生成的客户端是 `mimic.App` 之上的**普通 Python**，可当普通文件编辑；带命名方法、body 模板，以及移动 API 常见的**多步调用链**（一次调用取 token、下一次花掉）。
- **三种抓取后端**：mitmproxy（iOS 默认，走 `uvx` 拉起，无需单独装）/ `Copy as cURL` 粘贴（有 Web 版的都行，**不需要代理和证书**）/ HAR 文件。
- **手工建会话三路**：`Session.from_mitm(host)` / `Session.from_curl(text)` / `Session(base_url=..., headers=...)`。
- **401 处理有分寸**：幂等请求遇 401 **触发一次从 mitmweb 重新取 token 并重试**；**非幂等请求不重试**，除非显式 `refresh=True`。
- 安装：`sh install.sh` 会装 `uv`，mimic 进隔离 tool env；`mimic doctor` 检查 proxy 与 claude 是否就绪；`record` 会**填好你 Mac 的局域网 IP 并逐步引导**，并提示"证书信任设置这一步很容易漏，漏了什么都不工作"。

**值得关注的原因**
- **"把 App 变成库"是 Agent 工具面的新一格**。此前的工具化路线是：给 Agent 一个浏览器（moli / agent-browser）、给 Agent 一个终端（tuios / uniterm）、给 Agent 一套 MCP（ghidra-mcp / rea）。mimic 走的是**逆向 API 契约**——不模拟界面、不驱动 UI，直接生成可编程的 API 客户端。这与 10-08 `bethington/ghidra-mcp`（把命名规范/类型安全下沉到工具层）、10-07 `morluto/rea`（按"Agent 想学什么"重排工具目录）属于同一条"**Agent 原生重做传统专业工具**"的延长线。
- **"AI 生成代码 + 人类可编辑的普通 Python"是这次的分寸**：生成物不藏起来、不是不透明 DSL，而是你可以直接改的文件——和 10-12 上午 ECC（根目录唯一真源、适配器只打包不建副本）的"不锁死"是同一种产品判断。
- 风险面同样直白（重放别人的认证 token、按 App 的 ToS 走灰区），README 未做伦理声明——**这一条是本期唯一没有边界声明的高热度项目**，值得记录。

---

### 10. trymirai/uzu — 端侧推理引擎，多语言绑定（Rust，本周 +345）

**事件**：Rust 周榜，总 star 2,185。**0.6.0（10-01）→ 0.6.1（10-05）→ 0.6.2（10-08）→ 0.6.3（10-10）**，10 天内四连发。

**核心内容**
- **定位**："把 AI 直接部署进你的 App"——零延迟、完整数据隐私、**零推理成本**。
- **四语言绑定**：Rust 核（`uzu` crate）、**Python（PyPI `uzu`，`uv add uzu==0.6.3`）**、**TypeScript（npm `@trymirai/uzu`）**、**Swift（SPM，支持 iOS / macOS / Mac Catalyst，Swift 5.9）**。
- **明确利用 Apple 统一内存**；提供**统一的模型配置**（`alibaba:qwen3.5:0.8b:mirai:mirai-m:4` 这种可寻址的模型串），让新增模型支持变简单。
- **可追踪的计算**：README 把"traceable computations to ensure correctness against the source-of-truth implementation"列为关键特性——**与参考实现对齐可验证**，而不是只报吞吐。
- 用法极简：`EngineConfig` → `Engine::new` → `engine.model(...)` → 带进度回调的下载器 → `engine.chat(model, ...)` → `session.reply(messages, ...)`，回复对象里 `reasoning()` 与 `text()` 分开取。

**值得关注的原因**
- **"端侧推理"的竞争点从"能不能跑"转到"能不能嵌进产品"**。10-12 上午 colibri 解决"最低 8GB RAM 也能跑"，ninfer 解决"单卡跑满"，uzu 解决"**用四种语言把一个引擎塞进 iOS/Web/桌面应用**"——三条路对应三种买家（爱好者 / 单机重度用户 / 应用开发者）。
- **"计算可追踪以对齐参考实现"**是这一格里少见的**正确性主张**，而不是纯性能主张；与 10-09 `mxc` 的 `--audit`（反推能力清单）、10-08 `open-ontologies`（可独立验证的证明）同属"**让产物可被第三方复核**"。
- 与 10-05 `antirez/ds4`（刻意窄的专用引擎、原生 coding agent 不起 HTTP）对照：**uzu 走绑定进 App，ds4 走单机二进制**，同一层两种交付形态。

---

## 三、其他趋势速览

### 大厂 / 官方项目
- **[hydra-db/hydradb](https://github.com/hydra-db/hydradb)**（Rust，本月 +10,029，总 13,011，AGPL-3.0，v0.2.0 09-30）— **对象存储原生的分布式图数据库**：图记录/WAL/manifest/不可变遍历索引全放 S3 兼容存储，查询节点与索引器**只保留可丢弃的本地状态**，可随时重建或扩容；写者用对象存储 CAS 租约选举 + SlateDB writer epoch 隔离旧写者；每个查询跑在一个 pinned SlateDB 快照上；支持 Neo4j Bolt 5.x 驱动 + OpenCypher + GraphBLAS 遍历。**它是本期新增面孔里增幅第二高的项目**（仅次于 moli），且是**唯一把"存算分离"做到图数据库层的**——对 Agent 知识图谱/记忆的持久层是个现成答案。
- **[Robbyant/lingbot-map](https://github.com/Robbyant/lingbot-map)**（Python，本周 +793，总 18,004，Apache-2.0）— **ECCV 2026 最佳论文候选**，流式 3D 重建的 feed-forward 基础模型：Geometric Context Transformer 用 anchor context + pose-reference window + trajectory memory 把坐标接地、稠密几何线索、长程漂移校正统一进单一流式框架；paged KV cache 注意力，**518×378 分辨率下约 20 FPS，序列长度超过 10,000 帧**仍稳定。模型已上 HuggingFace 与 ModelScope。
- **[microsoft/mcp-for-beginners](https://github.com/microsoft/mcp-for-beginners)**（Jupyter，本月 +269，总 17,430）+ **[microsoft/ai-agents-for-beginners](https://github.com/microsoft/ai-agents-for-beginners)**（本月 +2,665，总 76,956）+ **[datawhalechina/deepagents-in-action](https://github.com/datawhalechina/deepagents-in-action)**（本月 +683）— 培训侧继续铺：微软官方 MCP 课程（.NET/Java/TS/Python 跨语言示例）、LangChain 官方大使的《Deep Agents 实战》中文书。
- **[e2b-dev/runtime](https://github.com/e2b-dev/runtime)**（Go，本月 +455，总 1,710）— **E2B 的运行时开源**："Cloud、Enterprise、以及你自己的机器背后是同一个 runtime"，沙箱底座从托管产品变成可自托管件。
- **[higgsfield-ai/higgsfield](https://github.com/higgsfield-ai/higgsfield)**（Jupyter，本月 +1,781，总 5,956）— 容错、高可扩展的 GPU 编排 + 面向**数十亿到数万亿参数**训练的 ML 框架。
- **[NVIDIA/cuvs](https://github.com/NVIDIA/cuvs)**（+7）/ **[NVIDIA/cuopt](https://github.com/NVIDIA/cuopt)**（+6）/ **[NVIDIA/nccl-extensions](https://github.com/NVIDIA/nccl-extensions)**（+2，总 68）— NVIDIA 三个新仓同时进 CUDA 榜：GPU 向量检索与聚类、GPU 决策优化、NCCL 设备/主机 API 之上的通信模式。**都是库，不是产品**。

### Agent 工具与生态
- **[LaurieWired/GhidraMCP](https://github.com/LaurieWired/GhidraMCP)**（Java，本周 +765，总 11,077）— Ghidra 的 MCP server 原版重回榜单。与已推送的 `bethington/ghidra-mcp`（209 个工具、P-code 仿真、实时调试器）形成对照：**同一个 Ghidra，两条 MCP 路线**（轻量原版 vs 全量重武器），本期两者同时在榜。
- **[ys-ll/uniterm](https://github.com/ys-ll/uniterm)**（Go，本周 +156，总 823）— 一体化终端，覆盖 **30+ 协议**（SSH/Telnet/Mosh/Serial/Raw TCP/本地+WSL、SFTP/SCP/FTP/SMB/WebDAV/S3/Zmodem、RDP/VNC/SPICE/X11、8 种数据库、K8s/Docker/Podman/nerdctl/WSLC）+ **内置可自主规划并执行多轮 shell 命令的 AI Agent**；执行模式四档（Bypass / 仅危险 / 危险+写 / 全部确认）；**内置 MCP server 让 Claude Code/Codex/Gemini CLI 在已保存的连接上跑命令与传文件，凭证不出 App**。
- **[Bennettxai/FounderOS](https://github.com/Bennettxai/FounderOS)**（Go，本周 +97，总 1,063）— **一人公司的指挥中心**：把通讯、客户漏斗、社媒增长、财务、知识图谱、以及**一队各司其职的具名 AI Agent** 收进一块屏；v2 从 Next.js+SQLite 迁到 **BusinessOS 栈**（SvelteKit 2 + Go/Gin + PostgreSQL/Redis + Elixir/OTP 的 Optimal Engine 做知识/记忆）；`/os/org` 写的是"operator → Conductor → pillars → workers"的组织层级。
- **[kaishi00/hermes-conduit](https://github.com/kaishi00/hermes-conduit)**（Swift，本周 +63，总 248）— **Hermes Agent 的原生 iOS 客户端**，已上 App Store；**直连你自托管的 Hermes dashboard，无中继服务、无额外进程**；桌面开一个会话、手机上接着聊，**"会话列表一样，因为是同一个数据库"**；支持 CarPlay 语音、Bot Mode、多 dashboard 隔离凭证、Capabilities 页开关 skills/tools/MCP、内联审批、Face ID 锁 + Keychain。
- **[gepa-ai/gepa](https://github.com/gepa-ai/gepa)**（Jupyter，本周 +79，总 6,944）— **Genetic-Pareto 反射式优化**：用 LLM **读完整执行轨迹**（报错、profiling、推理日志）诊断失败原因并定向修改，而不是把轨迹压成一个标量奖励；**100–500 次评估 vs GRPO 的 5,000–25,000+（快 35×）**；自报 ARC-AGI Agent 准确率 32%→89%（架构发现）、Jinja 编码 Agent 解决率 55%→82%（自动学技能）、云调度策略省 40.2% 成本；50+ 生产用例（Shopify/Databricks/Dropbox/OpenAI/Pydantic/MLflow）。Tobi Lütke（Shopify CEO）的评价被放在 README 顶部。
- **[Armur-Ai/Pentest-Swarm-AI](https://github.com/Armur-Ai/Pentest-Swarm-AI)**（Go，本月 +339，总 2,825）— Agent 集群自主渗透测试，ReAct 编排 recon / 分类 / 利用 / 报告四类专家。与已推送的 `Autumn-27/ARTEX`（双图架构）、`vxcontrol/pentagi`、`SnailSploit/Claude-Red` 一起，**"AI 渗透测试"已从单个项目变成一个稳定细分**。
- **[mnfst/awesome-free-llm-apis](https://github.com/mnfst/awesome-free-llm-apis)**（JS，本周 +706 / 本月 +2,404，总 9,901）— 永久免费 LLM API 清单（含 API Keys）。与已推送的 `tashfeenahmed/freellmapi`（把免费额度当可调度资源、靠"时效"收费）构成"**清单 vs 路由器**"的配套。
- **[withmarbleapp/os-taxonomy](https://github.com/withmarbleapp/os-taxonomy)**（JS，本周 +161，总 4,809）— Marble 开源的**儿童学习内容结构化分类体系**：1,590 个微主题 / 3,221 条先修边 / 8 个学科，对齐国家课程标准。**非 AI 项目，但正是"给 Agent 用的领域本体"最标准的形态**。

### 中文生态
- **[hicccc77/WeFlow](https://github.com/hicccc77/WeFlow)**（TS，本周 +269，总 14,971）— **完全本地、实时**的微信聊天记录查看/分析/导出工具，可生成年度报告与数据。与已推送的 `hicccc77` 同类路线（本地优先 + 数据不出机器）在中文工具里持续走热。
- **[ScottSloan/Bili23-Downloader](https://github.com/ScottSloan/Bili23-Downloader)**（Python，zh 周榜 +334，总 8,301）、**[JoeanAmier/TikTokDownloader](https://github.com/JoeanAmier/TikTokDownloader)**（zh 日榜 +976，总 16,708）、**[qist/tvbox](https://github.com/qist/tvbox)**（本月 +716）— 中文口语榜（`spoken_language_code=zh`）里这三条最稳，**本期首次把口语语言维度纳入抓取**。

### 已推送仓库的新版本 / 新动态
| 仓库 | 新版本 | 时间 | 要点 |
|---|---|---|---|
| [paperclipai/paperclip](https://github.com/paperclipai/paperclip) | canary v2026.1012.0-canary.1/2/3 | **今日 10-12** | 一日三连：server 把失败的工作区任务报 **422 而非 500**；daytona 租约创建撞 deadline 时记录 provider 状态；restore 在挂住任务前**重试沙箱回拷** |
| [DuarteSantos8/openGym](https://github.com/DuarteSantos8/openGym) | **v1.4.0**（10-09）+ v1.4.1（10-10） | 10-09/10 | 史上最大更新：**动作库 1,324 → 5,632**，47 个社区 PR / 20 位贡献者；**老版本设备与 v1.4.0 服务端互通**，不认识的新动作也不会丢；v1.4.1 修更新检查（原先问 GitLab 镜像所以永远查不到）+ 300MB 下载改流式落盘并校验 checksum |
| [trycua/cua](https://github.com/trycua/cua) | Cua Spaces v0.8.0-beta.3 | 10-10 | 继续 beta 迭代 |
| [NVIDIA/OpenShell](https://github.com/NVIDIA/OpenShell) | v0.1.4-pre.2 + Development Build | 10-09/10 | 新增**仅 operator 可用的 provider 凭证读取**接口 |
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | v0.8.148 / v0.8.149 | 10-11 | 继续高频发版 |
| [morluto/rea](https://github.com/morluto/rea) | v6.3.0 → **v6.4.0** | 10-09/11 | 继续 6.x 快节奏 |
| [mvschwarz/openrig](https://github.com/mvschwarz/openrig) | v0.6.8 → **v0.6.9** | 10-09/11 | 升级后**须重启 daemon** |
| [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) | v0.7.20 / v0.7.21 | 10-10/11 | — |
| [tashfeenahmed/freellmapi](https://github.com/tashfeenahmed/freellmapi) | v0.13.8 / **v0.13.9** | 10-11 | 一日两发 |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | v5.1.0 | 10-08 | 无新版本（本期仍为最新） |
| [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | v13.35.0 | 10-09 | 无新版本 |
| [vectorize-io/hindsight](https://github.com/vectorize-io/hindsight) | v0.10.3 | 10-08 | 无新版本 |
| [Tencent/WeKnora](https://github.com/Tencent/WeKnora) | v0.8.2 | 09-24 | **连续第 7 期无新版本** |
| [debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio) | v0.5.6 | 09-23 | **连续第 8 期无新版本** |
| [mksglu/context-mode](https://github.com/mksglu/context-mode) | v1.0.169 | 06-29 | **近 3.5 个月无新版本** |
| [TencentCloud/Octop](https://github.com/TencentCloud/Octop) | v1.0.2b6 | 10-06 | 无新版本 |
| [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) | v1.5.0 | 06-11（tag 侧无更新） | 月榜仍在，代码侧持续提交 |

---

## 四、当日主线判断（本期）

1. **"Agent 的产出没有出处"被当成产品问题解决**。Atlas 把 commit 挂回产出它的会话（含 prompt / 工具调用 / 推理 / patch），并让链接**穿过 amend 与 rebase**、真歧义时**孤儿化而不猜**。此前十期的记忆层解决"Agent 记得什么"，本期第一次系统性解决"**代码是谁在什么推理下改的**"。
2. **成本战场推进到第五层：运行时算不算像素**。账本已完整：不产生中间结果（e2e 录制回放）→ 不读取（claude-mem 读取门）→ 不调用模型（e2e / context-mode）→ 不让会话启动等待（claude-mem 索引）→ **不渲染**（moli 结构优先、布局按需）。moli 用 73 MiB vs Chrome 773 MiB 的内存差把这一层量化了。
3. **"Agent 该住在哪里"三路同时加注**：终端（tuios 用 OSC 7501 做 Agent 状态总线、uniterm 内置自主 Agent）、桌面工作台（PI-Desktop 用插件扩展桌面本身）、云端模型 + 本机环境（webcodex 的 Server/Runner）。**没有任何一条路显出收敛迹象**。
4. **用户数据开始跨 harness 流动**。Atomic Agent 的导入清单（Claude Code / Codex / Oh-My-Pi / Pi / Hermes / OpenClaw）+ Atlas 的跨 Agent 共享记忆 + cc-switch 的 10 个 CLI 统一控制面，三件事在同一周出现。**"换 Agent 要重新解释一遍"正在被当成缺陷修掉**。
5. **记忆层第四条路线落地且最朴素**：engram 只用 Go 二进制 + SQLite/FTS5，不接 LLM、不建向量库，14 种 Agent 接入。四条路线（服务化 LLM / 文件化零 LLM / 图谱本地小模型 / FTS5 单文件）**star 数没有明显高下**，说明这个市场还没有收敛到最优解。
6. **"能力协商写进健康检查"是新的控制面纪律**。engram 的写操作要等 `/health` 声明 `runtime_session_resolution: true` 才放行，**hook 永不自动重启 server**；moli 不支持的动作**返回显式错误而不假装发生过**。这两条都是对"**控制平面失效常常无声**"（本期第三次提及）的正面回应。
7. **推理引擎按场景切片，而不是追求通用**：ninfer 只服务 RTX 5090 + Qwen3.5（换 1,000+ tok/s）、colibri 磁盘流式压到 8GB RAM（换 0.05 tok/s）、uzu 用四语言绑定嵌进 App、ds4 刻意窄化只跑指定模型族。**"能跑"与"能用"的差距被明码标价**。
8. **诚实披露已进入第四级：连文档声称的行为都先否掉**。webcodex 明写"六种安装包仍需验收、**本文档不声称跨平台行为一致**"，并主动撤回 Windows 产物；ninfer 明写"**没有 install target、没有打包二进制**"。对比前几期的"修正数值"（RuView 撤回 100%）→"修正口径"（rtk 拆穿自家标题）→"修正能力边界"（colibri 写 0.05 tok/s）。
9. **对象存储正在成为一切持久层的默认底座**。hydradb 把图数据库整个建在 S3 兼容存储上（查询节点只保留可丢弃状态）；此前 10-12 上午 celld（Deno 的分布式 Durable Objects）也是"长期状态在 bucket，节点可替换"。**"存算分离"从数据仓库下沉到图数据库与 Agent 状态**。
10. **本期 10 条全部为 Agent 相关**，非 Agent 项目 0/10（本期最低）。原因明确：**主榜 42 条全重复**，新面孔只能从语言 × weekly/monthly 里挖，而这个组合里高增幅项几乎都是 Agent 基础设施。**这不是偏好，是榜单结构的产物**——上期（10-12 上午）非 Agent 占 4/10，是因为语言 × daily 里混入了大量具体问题型工程。
11. **官方/大厂项目在本期新面孔里占比不高**（微软 3 条培训类、NVIDIA 3 个库、E2B 1 个 runtime），**与 10-09 那期的"大厂集体落子 Agent 运行时"形成反差**——本期是**个人与小团队项目主导**（moli / atlas / tuios / mimic / ninfer / uzu / PI-Desktop 均为个人或小团队）。

---

## 五、方法论脚注

- **抓取**：带重试的 curl 落盘 + 本地解析（`code==200 && size>100000`，最多 10 次、间隔 4–5s），26 个榜并发一次跑完，**本期 0 次 504**。`fetch_trending.py` 的网络层仍不可依赖（单次失败即放弃），但**它的 `parse_board()` 可直接 `importlib` 复用**。
- **本期维度组合**（重要）：主榜 daily/weekly/monthly 三榜 **42 条 100% 重复**，与上午那期逐条一致 → **语言榜必须换周期而不只换语言**。上午用的是「14 语言 × daily」，本期用「14 语言 × weekly」+「7 语言 × monthly」+「zh/en 口语语言 × daily/weekly」，一次拿到 270 条未推送仓库。**结论：语言榜的 `since` 参数是同一语言下完全不同的一批仓库**。
- **新增可用维度**：`https://github.com/trending?spoken_language_code=zh|en&since=daily|weekly` —— 中文榜（22/21 条）里有主榜与语言榜都看不到的中文项目（WeFlow / Bili23 / TikTokDownloader / tvbox / Ehviewer）。
- **`gain` 口径不可跨榜比较**：本期表格里 moli 同时有"本月 +14,631"与"本周 +9,308"，两者是不同周期的累计，**不能相减也不能取 max 当同口径用**。
- **坑**：`uzu` 与 `mimic`、`ninfer` 的 `releases.atom` **只有 `<updated>` 无 `<entry>/<content>`**（无正文），改从 README 取；`hydradb`/`founderos` atom 条目极少（3 / 1 条），也以 README 为主。README 一律 `curl` 落盘 + `sed -e 's/<[^>]*>//g'` + `head -N` 定点读，不整篇读（atomic-agent 64KB / uzu 46KB / scrapling 36KB）。
- **GitHub REST API 全程未使用**（配额早已耗尽，且 trending 不提供 API）。

---

*生成时间：2026-10-12 14:00 GMT+8 · 数据源：github.com/trending（主榜 3 + 语言榜 21 + 口语语言榜 3，共 353 条去重）· 本期为同日第二次运行，与上午 09:43 那期零重复*
