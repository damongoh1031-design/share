# GitHub 趋势日报 · 2026-10-07

> 数据源：github.com/trending 三榜合并（daily **12** 条 / weekly **12** 条 / monthly **23** 条）+ 语言维度榜补位（python / typescript / rust / go / c++ / javascript / cuda / html）。
> **本期主榜几乎全是重复条目**：daily 12 条里只有 3 条此前未推送，weekly 12 条、monthly 23 条则全部为已推送仓库。因此本期 10 条详细条目有 **9 条来自语言维度榜**（主榜看不到的项目），1 条为已推送仓库的重大新版本。
> 增幅为 GitHub 展示的周期新增 star；**榜单排列顺序不等于增幅排序**，下文只报增幅不声称名次。

---

## 一、本期速览表

| # | 仓库 | 语言 | 总 Star | 增幅 | 来源 | 一句话 |
|---|---|---|---|---|---|---|
| 1 | [morluto/rea](https://github.com/morluto/rea) | TypeScript | 10,401 | +2,956 (today) | daily | 一个 MCP 覆盖二进制/应用/运行时行为的逆向工程 |
| 2 | [mvschwarz/openrig](https://github.com/mvschwarz/openrig) | TypeScript | 5,560 | +3,327 (this week) | weekly | **v0.6.6**：装完即问你要建什么，队伍可分享安装 |
| 3 | [tester-army/e2e](https://github.com/tester-army/e2e) | TypeScript | 6,577 | +1,725 (today) | daily | **0.13.0**：弃 tsx 自建 oxc loader，Node 版本硬门槛 |
| 4 | [deepseek-ai/DeepGEMM](https://github.com/deepseek-ai/DeepGEMM) | Cuda | 8,779 | +199 (today) | daily | **DeepGEMM Ascend 上线**，CUDA kernel 库出 NPU 后端 |
| 5 | [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | HTML | 44,195 | +228 (today) | daily/html | 42 种编辑级图表技能，自包含 HTML+SVG |
| 6 | [rtk-ai/rtk](https://github.com/rtk-ai/rtk) | Rust | 82,575 | +101 (today) | rust | 在命令输出进上下文前压缩它，最高省 90% |
| 7 | [topoteretes/cognee](https://github.com/topoteretes/cognee) | Python | 31,505 | +82 (today) | python | 无 API key 也能跑的自托管 AI 记忆平台 |
| 8 | [omnigent-ai/omnigent](https://github.com/omnigent-ai/omnigent) | Python | 10,636 | +28 (today) | python | **v0.17.0**：跨 harness 的 meta-harness |
| 9 | [backnotprop/plannotator](https://github.com/backnotprop/plannotator) | TypeScript | 9,185 | +25 (today) | typescript | 计划/diff 的浏览器标注审阅面 |
| 10 | [RyanCodrai/turbovec](https://github.com/RyanCodrai/turbovec) | Rust | 17,348 | +26 (today) | rust | 2/4-bit 向量索引，比 FAISS 快 4.4×、内存小 7.8× |
| — | [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) | JavaScript | 4,530 | +40 (today) | javascript | 官方社区插件市场只读镜像（详第 9 条） |

**主榜其余条目（本期已在速览层，未展开）**：ponytail（月 +28,592）、i-have-adhd（月 +27,129）、ECC（月 +25,085）、hindsight（月 +23,797）、open-code-review（月 +22,361）、paperclip（月 +18,199）、hyperframes（月 +13,590）、colibri（月 +13,243）、WeKnora（月 +11,017）、freellmapi（月 +6,832）、ghidra（月 +6,688）、OpenShell（月 +6,640）、cua（月 +6,232）、claude-code（月 +6,022）、Octop（月 +5,766）、context-mode（月 +5,188）、Agent-Reach（周 +6,454）、financial-services（月 +4,264）、openGym（周 +3,318）、AnyPS5（周 +3,073）、yoinks（周 +2,947）、substrate（月 +2,638）、knowledge-work-plugins（月 +2,444）、worktrunk（月 +2,151）、byoungd/up（周 +2,154）、claude-mem（周 +2,104）、PageIndex（周 +2,079）、GhostTrack（周 +2,017）、mattpocock/skills（日 +889）、agency-agents（日 +623）、text-to-cad（日 +619）、impeccable（日 +616）、cursor/plugins（月 +3,273）、gods-eye-view（月 +30,225）、archify（月 +28,776）。

---

## 二、10 条详细

### 1. morluto/rea — 逆向工程被"Agent 原生"重做

- **仓库**：morluto/rea（TypeScript，MIT，总 10,401，日 **+2,956**，本期 daily 增幅第一）
- **事件**：v4.1.0 于 10-06 17:57 (GMT+8) 发布；v4.0.0 / v4.0.1 于 10-05 连发。一天内从 4.0.0 走到 4.1.0。

**核心内容**
- 定位是"**一个 MCP 覆盖二进制、应用与运行时行为的逆向工程**"，口号是"看到一个你喜欢的功能，把它理解到二进制层"。连接 Agent 后可直接说"逆向 Notes 应用的离线搜索，讲清它怎么工作，再用 TypeScript + SQLite 给我的项目做一个"。
- 工具目录约 **130 个工具、11 个族**：Native inspection 41、Investigation workflows 14、Native macOS utilities 7、Artifact graph 5、Managed PE/CLI 7、Firmware 2、Android APK 5、Browser observation 9、Electron 5、JavaScript runtime 2、Application workflows 11、Workspace/observation 21。
- 三档深度、依赖逐级上升：**静态 JS/Electron 分析零依赖**（不需 Hopper/Ghidra，且不执行目标应用，只需 Node 22.19+）；原生二进制需 Hopper（自带 license）/ Ghidra **12.1.x + JDK 21** / IDA Pro（**复用 mrexodia/ida-pro-mcp** 的既有注册，分 attached 与 headless 两档）；固件用调用方自备的 Binwalk/Unblob；APK 用自备 headless JADX + Java（**不用模拟器、不执行 APK**）。
- v4.1.0 新增：headless JADX 静态 APK 分析（#738）、Ghidra **原子函数标注**（改名字与入口注释，可执行字节不变，#709）、**Windows x64 只读 PE 分析**（本机 NTFS + 捆绑 Job Object + 私有 DACL + 路径准入，#699）、Ghidra NativeAOT 元数据恢复（#748）、DOS COM/MZ 显式 16 位实模式（#702 / #697）、IDA 只读 GUI + headless provider（#754）、Binwalk/Unblob 固件（5a7c769）。
- **证据模型是产品一级对象**：每次结论带 Evidence bundle（artifact identity / provider / locations / confidence / limitations），可 export / import / canonicalize / compare；Open questions 专门跟踪未解项、矛盾与后续探针；重建检查只报 pass / fail / unknown，**缺失证据不算通过**。快照按"目标字节 + 操作 + 参数 + 工具 + 设置"全匹配才复用，且只读、owner-only 权限。
- 分工清晰：步骤 1–5（打开识别 → 搜字符串/过程 → 连到可执行代码 → 重建控制流 → 反编译）由 REA 做，步骤 6（在你自己项目里写功能）由 Agent 用它自己的编辑与测试工具完成。

**值得关注的原因**
1. **逆向工程是"Agent 原生重做传统专业工具"的最清晰样本**——工具目录按"Agent 想学什么"命名（app overview、function dossier、feature trace），而不是按 Hopper/IDA 的功能名。同一趋势本期还有 plannotator（把代码审阅做成浏览器标注面）。
2. **不重造引擎，把商业工具当 BYO provider**。Hopper / Ghidra / IDA 都是"你已经有的"，REA 只做统一契约与证据层。这与 09-30 OpenShell"不重造内核、只做闸门"同思路：新品类先占编排位，不占实现位。
3. **权限权威源继续外移**：静态分析不执行目标、Windows 侧只读 PE 边界写死（25 个只读操作、无变更权限）、浏览器观察是**被动**的（不导航、不点击、不执行 JS，凭证/cookie/Authorization 头不保留）。
4. 它把"从看懂到写出来"放在同一会话闭环，等于把"抄功能"从人工逆向（数天）压缩到一次对话——这是能力提升，同时也是**开源许可与竞品分析的新灰区**，README 明确声明"不声称恢复原始源码、不自动克隆应用"。
5. 文档纪律罕见：`docs/product-catalog.json` 由源码生成，PR CI 校验目录、叙述文档与 schema 一致——延续"把不可验证的变成可验证的"。

---

### 2. deepseek-ai/DeepGEMM — CUDA kernel 库出了昇腾后端

- **仓库**：deepseek-ai/DeepGEMM（Cuda，总 8,779，日 +199）
- **事件**：README News **2026.09.30** 两条——①**DeepGEMM Ascend 上线**，新仓库 `deepseek-ai/DeepGEMM-Ascend`；②新增 locality domain 等优化（#462）。本条属热度回温，非新发布。

**核心内容**
- 统一的高性能 tensor core kernel 库，把现代 LLM 的关键计算原语收进**一套 CUDA 代码**：GEMM（FP8 / FP4 / BF16）、融合 MoE（**Mega MoE**，通信重叠）、lightning indexer 的 MQA scoring、HyperConnection（HC）。所有 kernel 走 **DeepJIT** 运行时编译，安装时无需 CUDA 编译。
- 设计取舍：借鉴 CUTLASS / CuTe 概念但**不重度依赖其模板与代数**，核心 kernel 函数数量有限，定位是"可读的 GPU kernel 优化教材 + 生产级性能"。
- 分组 GEMM 只按 M 轴分组（N/K 必须固定）——针对 MoE 专家同形场景；连续布局服务训练前向与推理 prefill，masked 布局服务 CUDA graph 下的解码（CPU 不知道每个专家收多少 token，用 mask 只算有效部分），输入可直接接 DeepEP 的低延迟 kernel 输出。
- 硬件门槛：SM90 只支持 NT 布局、缩放因子 FP32；SM100 支持全部布局、缩放因子需打包 **UE8M0**（4 个压进一个 `torch.int`）。要求 SM90/SM100、CUDA 12.9+、CUTLASS 4.0+。

**值得关注的原因**
1. **"算力层去单一供应商"从编译器层走到 kernel 层**。10-02 记录过 tilelang 上线华为昇腾 950 NPU 后端；DeepGEMM 是更核心的一环——MoE 推理的 GEMM 原语本身有了非 NVIDIA 实现。两个信号叠加，说明这条线不是单一项目的选择。
2. **Ascend 版单独开仓库而不是塞进主仓**，意味着两条线共享接口、各自维护优化：即"同一套 MoE 原语，两套硬件实现"。这比"分支里加 if-else"更接近可维护的多后端架构。
3. DeepGEMM 的独特价值是"可读性"，Ascend 版等于把这份可读性复制到国产芯片侧——**降低 NPU 侧 kernel 优化的入门门槛**，长期影响大于短期性能数字。
4. 注意口径：日榜 +199 是热度回温，不是 10-07 的新闻。DeepGEMM 的 release 列表最近仍是 07-20 的 `nv_dev_*` tag，**Ascend 的进展只在 README News 与独立仓库里**。

---

### 3. cathrynlavery/diagram-design — 图表进入"编辑级审美"垂直

- **仓库**：cathrynlavery/diagram-design（HTML，总 44,195，日 +228）
- **事件**：v2.5.10 新增 **10 种布局语法**（Sankey、鱼骨图、Wardley map、看板、用户旅程、部署图、依赖图、UML 类图、故事地图、数据库 schema）；10-07 06:02 仍有新发布。

**核心内容**
- 给 Claude Code / Codex / GitHub Copilot / Factory Droid / Pi 及任何兼容 Agent Skills 的宿主用的**图表技能**。产物是**自包含 HTML + SVG**：无构建步骤、无 JavaScript、无外链图片，浏览器直接打开。
- **42 种图表类型**：架构、IT 现状（遗留与现代化）、流程图、时序、状态机、ER/数据模型、时间线、泳道、四象限、雷达、飞轮、嵌套、树、组织图、层叠、Venn、金字塔/漏斗、柱状、矩形树、折线、Gantt、散点、高层、流程、Medallion、数据流、DP 集成、DP 安全矩阵，加上 v2.5.10 的 10 种。每种配三个静态变体（minimal light / minimal dark / full-editorial）。
- **关键抽象是"语义模式与布局分离"**：队列、策略追踪、信任边界这类语义可以复用最近似的既有类型，不必为每个语义新增一种图——类型数不随语义爆炸。
- 可把 draw.io / Mermaid / Excalidraw 源**重绘**成指定格式、尺寸与细节层级（正面抢 Mermaid 的地盘，且态度鲜明："No Mermaid slop"、"No Figma"、"No generic rounded boxes"）。
- 设计纪律写成硬规则：最高质量的动作通常是**删除**；每个节点都要挣得自己的位置；强调色只留给读者该先看的 1–2 个对象；目标信息密度 4/10。60 秒读你的网站匹配品牌色。
- 供应链声明：官方构建只来自本仓库，其他名字下的插件目录列表是**非官方副本**；PRIVACY.md 列出技能会发什么网络请求。

**值得关注的原因**
1. **技能生态长出了"输出审美"这个垂直**。10-06 的 impeccable 是"设计语言"（61 条确定性规则、零 LLM），diagram-design 是"图表类型库"。两者都在解决同一个默认失败模式：Agent 一画图就是通用圆角框，跟站点风格无关。
2. **"语义与布局分离"是可复用的工程抽象**，任何"类型库型"技能都该抄这个解法——否则类型枚举会随业务语义线性膨胀。
3. 零依赖自包含 HTML 是"产物可复现"的又一实现（同 hyperframes 写 HTML 出确定性 MP4）：**同一输入同一输出，不依赖外部 CDN 与运行时**。
4. "官方构建只来自本仓库、其他同名列表是山寨"已成 README 标配——技能供应链的信任声明正在标准化（本期第 9 条是厂商侧的另一半）。

---

### 4. rtk-ai/rtk — 在命令输出进入上下文之前就压缩它

- **仓库**：rtk-ai/rtk（Rust，总 82,575，日 +101）
- **事件**：10-06 至 10-07 密集发版，`dev-0.51.1-rc.510 → rc.515`，约每 20–30 分钟一个 rc。

**核心内容**
- **拦截 shell 命令并在 Agent 读到输出前压缩它**。单个 Rust 二进制，100+ 命令支持，开销 <10ms。四种策略组合：智能过滤（去注释/空白/样板）、分组（文件按目录、错误按类型）、截断（保上下文、砍冗余）、去重（重复日志行折叠为带计数的一行）。
- 覆盖范围示例：`ls`/`tree` → 树形 + 文件计数；`cat`/`read` → 签名与结构优先（`-l aggressive` 只留签名）；`grep`/`rg`/`ast-grep` → 按文件分组、长行截断；`git status`/`diff`/`log` → 紧凑格式；`git add/commit/push` → 只回一行确认；`cargo test`/`npm test`/`pytest`/`go test`/`jest`/`vitest`/`playwright` → **只留失败，通过折叠为计数**；`ruff`/`sqlfluff`/`golangci-lint`/`cargo clippy`/`tsc` → 按规则与文件分组；`docker ps` → 只留必要字段。
- 集成方式分两类：**hook 型** Agent 在执行前重写命令（`git status` → `rtk git status`），支持 Claude Code / Codex / Cursor / Gemini CLI / Windsurf / Cline / Kilo Code / Antigravity / Kimi / Pi / OMP / Hermes / Factory Droid / Trae；**插件型**（如 Hermes）走插件 API 重写。
- **明确的能力边界**：hook 只在 Bash 工具调用上运行——Claude Code 内置的 `Read` / `Grep` / `Glob` **不经过**，所以那三条路径不会自动压缩，需改用 shell 命令或直接调 `rtk read` / `rtk grep` / `rtk find`。
- **诚实口径写得比多数项目好**："省 90% 是省 bash 输出，不等于省 90% 账单"——bash 输出只是 input token 的一个来源，input token 又只是账单的一部分，削减比例会逐级稀释；token 数按 `bytes/4` 估算（**不内置 tokenizer**），因此**百分比可靠、绝对值近似**。另正面回答"不会破坏 Claude prompt cache"：过滤每命令只做一次，结果进历史后按常规缓存，输出更小反而让 cache 读写更便宜。

**值得关注的原因**
1. **成本压缩继续前移到"输出进入上下文之前"**。此前的账本是：不产生中间结果（context-mode 写代码）→ 不读取（claude-mem File Read Gate）→ 不调用模型（e2e 录制回放）。rtk 是**在命令输出生成后、进入上下文前**这一格，比前三者都更靠前。
2. **它与 10-05 的 caveman 几乎同构**：caveman 的 proxy 管"agent 读什么"（本地跑、六类文件 -82.4%），rtk 管"agent 从 shell 读什么"。两处独立出现，说明"读入侧压缩"已是稳定产品位，不是单点创意。
3. **口径层面的自我削弱比数值层面的更少见**。此前是 ponytail 修正自己的数字、RuView 撤回"100% 检测"、codegraph 自曝残余上下文 +80%；rtk 是**直接拆穿自家标题的营销口径**（"省 90%"不等于省 90%），并说明估算方法不可靠在哪。
4. hook 只覆盖 Bash 这一点本身就是提醒：**控制平面失效常常是无声的**——你以为压缩了，但 Read/Grep 路径根本没经过。这是本期第三次出现同类教训（另见 claude-mem 的 prompt-cache 回归、ponytail 的档位静默失效）。

---

### 5. omnigent-ai/omnigent — meta-harness 成为一层产品

- **仓库**：omnigent-ai/omnigent（Python 3.12+，Apache-2.0，总 10,636，日 +28）
- **事件**：v0.17.0 于 10-06 02:02 (GMT+8) 发布；nightly `v0.18.0.dev20261007` 同日跟进。

**核心内容**
- 定位"**所有 AI Agent 的开源 meta-harness**"：在 Claude Code / Codex / Cursor / OpenCode / Hermes / Pi 以及你自己写的 Agent 之上做统一编排层，**换或组合 harness 而不用重写**。
- 五个能力面：①会话跨设备跟随（终端 → 浏览器 → 手机，消息/子代理/终端/文件保持同步）；②同会话混多个 Agent（让一个 Agent 审另一个的活，或按各家长处分任务）；③模型来源一等（自有 API key / Claude 或 ChatGPT 订阅 / 任意兼容网关）；④协作（分享会话让人旁观、共驾或 fork）；⑤**云沙箱**：Modal / Daytona / Blaxel / Islo / E2B / Gensee / CoreWeave / Kubernetes / **OpenShell** / Boxlite / microsandbox / Databricks，可由 CLI 启动或由 server 按会话供给（managed hosts）。
- **策略引擎**（govern）：在危险动作前暂停等批准、**给花费设上限**、限制 Agent 可触达的工具；作用域可选整个 server / 单个 Agent / 单个会话。
- v0.17.0 变更：桌面 App 走**系统浏览器 OIDC 登录**（静默续期、公开 PKCE 客户端、显式 provider 端点、显示运维方设定的服务端名）；工作区标签/常用视图/最近会话的键盘快捷键；侧栏 agent 层级更易扫读；**策略新增周期制成本预算、`PolicyEvent` 上下文带 `conversation_id`、RESPONSE 阶段的 `turn_final` 指示**。破坏性变更：`POST /v1/sessions/{id}/switch-agent` 返回 **410 Gone**，改为把会话 fork 到另一个 Agent。
- 安装：`uv tool install omnigent` 或 `pip install "omnigent"`，extras 分三组（模型 provider / 沙箱 provider / SDK harness），另有 Homebrew tap。

**值得关注的原因**
1. **"meta-harness"这一层正式有人做产品**。加上 10-05 的 t3code（控制面）、paperclip（组织层）、openrig（团队编排），Agent 管理已经分到**四层**且各有独立入场者。
2. **成本预算进策略引擎**（周期制，而非只做展示）。这与 paperclip 的"按 Agent 月度硬上限"同向：额度从"提醒你花了多少"变成"在动作前拦住"。
3. **上一代项目正在变成下一代产品的地基**——沙箱供应商列表里有 OpenShell，存储/记忆 extras 里有 hindsight。10-05 已记 pi 被 cloudflare-os 列为关键依赖，本期是双例。
4. **"会话身份不可变"被写成 API 约束**：switch-agent 直接 410，要求 fork。与 10-06 记录 OptMem 的"位置即身份"同思路——**不可变比可变更便宜**，因为省掉了一整类状态同步 bug。
5. 它把"多 harness"当默认假设，而非"选一个赢家"。这是对 09-28 openrig"rig 包住 harnesses"的正面确认：**harness 会长期并存**已被产品层接受。

---

### 6. backnotprop/plannotator — 把"人在回路"做成浏览器标注面

- **仓库**：backnotprop/plannotator（TypeScript，总 9,185，日 +25）
- **事件**：v0.28.1 → v0.28.6 于 10-05 至 10-06 六连发。

**核心内容**
- **本地浏览器审阅面**，通过各 harness 的 hook 与命令接入 Claude Code / Codex / Copilot CLI / Gemini CLI / OpenCode / Kiro / Droid / Amp / Pi。
- 工作方式：Agent 提出计划、产出 HTML、或写完代码时，工作内容**自动在浏览器打开**，你标注、评论，反馈直接回给 Agent 让它照做。覆盖四类：①文档/计划/规格/HTML 标注（本地文件、目录、任意 URL、Agent 上一条消息）；②代码审阅（本地未提交改动、远程 PR/MR，支持 Git / GitButler / Jujutsu / Perforce / GitHub / GitLab）；③HTML artifact 标注；④**plan mode 无需命令**——任何 harness 的 hook 一生成计划，审阅面就打开。
- 审阅面内建 AI：可就正在审的内容提问，或发起 AI 审阅并把评论直接贴到 diff 上。
- 近期修复读起来像一份"跨轮状态保真"的 bug 清单：v0.28.4 **修"Agent 编辑文件后评论丢失"**、修"PR 描述反馈被丢弃"；v0.28.5 支持**一次审多个文件**、**决策点名具体文件**、休眠后 Ask this session 重连。
- 配套：Herdr Annotate（把同款审阅搬进终端，支持对终端文本、整份 Markdown、Agent 回复标注）、plannotator-tui（独立 TUI）。标注统一存 Plannotator 数据目录，**终端审阅与 App 审阅可累积**。

**值得关注的原因**
1. **异步人在回路的具体产品形态**。10-05 记过三种实现：cloudflare-os 的"本地模拟结果后批量批"、OpenMontage 的"渲染前逐场景卡住"、openhuman 的 `NeedsConfirmation`。plannotator 补上第四种——**把审阅动作做成浏览器界面，并把反馈结构化回灌给 Agent**。
2. 它**不换 harness，只加一层**：全部走 hook 与 slash 命令接入。这是"不重写你的工作流"的最低摩擦路径，也是这类工具能快速覆盖 9 个 harness 的原因。
3. **"评论丢失"和 claude-mem 的 prompt-cache 回归是同类问题**——跨轮、跨进程的状态保真是这类工具最大的 bug 来源（本期第 4 条 rtk 的 hook 边界、第 10 条 openrig 的档位持久化也是）。这类工具真正难的不是功能，是**状态在什么时候被谁改写**。
4. "决策点名具体文件"是把人的自然语言反馈变成**机器可执行的引用**——审阅闭环里最容易被忽略的一环。

---

### 7. topoteretes/cognee — 记忆层第三条路线：知识图谱 + 本地小模型

- **仓库**：topoteretes/cognee（Python 3.10–3.14，总 31,505，日 +82）
- **事件**：v1.6.2（09-29，"Embedding reliability & Slack history"）、v1.6.1（09-24，Google Sync & Visualization）、v1.6.0（09-18，Keyless workflows & pipeline reliability）。

**核心内容**
- **自托管 AI 记忆平台**：把文档、代码、对话转成可搜索、可复用的知识图谱，给 Agent 提供跨会话的长期记忆。
- **不配 LLM key 也能跑**：无 key 时用本地 **GLiNER** 模型抽取图、用本地 embedding 模型向量化（首次使用下载），**CPU 即可，零 API key、零成本**。README 直接写明"我们依赖跑在你 CPU 上的免费小模型"。
- 三条典型用法：①**Company Brain**——把文档、对话、工单、代码、Agent 产出并成共享记忆，把某个决策连回它背后的讨论与实现；②跨运行记忆——保留项目上下文、过往决策、修过的 bug、学到的规则，把会话教训蒸馏成另一会话可检索的持久知识；③领域接地——用自定义数据模型与本体（ontology）把记忆结构化成你的应用需要的实体与关系。
- 接入方式：MCP 与插件（给已有 Agent 加记忆）、自托管部署、或 Cognee Cloud。学术支撑：arXiv **2505.24478**《Optimizing the Interface Between Knowledge Graphs and LLMs for Complex Reasoning》（Markovic 等，2025）。

**值得关注的原因**
1. **记忆层的第三条路线落地**。此前两条：hindsight（服务化 + LLM，Retain/Recall/Reflect，周榜第 1）与 ai-memory（Markdown + git 为事实源，**默认零 LLM 调用**）。cognee 是**知识图谱 + 本地小模型抽取**。三条路线的共同前提都是"跨会话、跨 harness、跨机器"。
2. **"不配 key 就能跑"把记忆层的边际成本压到 0**，正面回应 10-06 记的"读取记忆不该花模型的钱"。区别在于：hindsight 靠"纯 DB 读"省调用，cognee 靠"本地小模型"省调用——**同一目标，两种技术选型**。
3. **定位从"个人 Agent 的上下文"提升到"组织共享知识"**（Company Brain），与 paperclip 的组织化 Agent 管理、agency-agents 的部门化岗位定义同向：Agent 的"记忆"正在被当成组织资产设计。
4. **记忆品类开始要求可引用依据**——有同行评审论文、有 arXiv 编号。这与"验证本身成为工具类别"一脉相承（09-30 SkillSpector 的量化基线、10-06 的 claim-check / eval:read-gate）。

---

### 8. ChromeDevTools/chrome-devtools-mcp — 官方厂商 MCP 的信任姿态样本

- **仓库**：ChromeDevTools/chrome-devtools-mcp（TypeScript，总 53,050，日 +44）
- **事件**：最近版本 v1.10.0 / v1.10.1（09-23）；本期**重新进入 TS 语言榜**，无新发布。

**核心内容**
- Google 官方把 **Chrome DevTools 做成 MCP 服务器**（另有 CLI，可不用 MCP），让编码 Agent（Antigravity / Claude / Cursor / Copilot 等）**控制和检查一个活体 Chrome**。三件事：①性能洞察——用 DevTools 录 trace 并提取可执行建议；②高级调试——分析网络请求、截图、读控制台消息（带 source-map 栈）；③可靠自动化——用 puppeteer 驱动动作并**自动等待结果**。
- **边界写得比功能还清楚**：
  - 只官方支持 Google Chrome 与 Chrome for Testing，其他 Chromium 内核浏览器"可能能用但不保证"；
  - 性能工具可能把 trace URL 发给 Google **CrUX** API 取真实用户体验数据（`--no-performance-crux` 关）；
  - **默认收集使用统计**（工具调用成功率、延迟、环境信息，`--no-usage-statistics` 关；`CI` 或 `CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS` 环境变量存在时自动关）；
  - 默认定期查 npm 更新（`CHROME_DEVTOOLS_MCP_NO_UPDATE_CHECKS` 关）；
  - 免责声明：它**把浏览器实例的全部内容暴露给 MCP 客户端**，客户端可以检查、调试、修改浏览器或 DevTools 里的任何数据，别共享敏感信息。

**值得关注的原因**
1. **"活体浏览器"是最脏的环境，现在被纳入 Agent 可观测范围**。对照本期第 1 条：rea 的 browser observation 走**被动**只读 CDP（不导航、不点击、不执行 JS、不保留凭证），chrome-devtools-mcp 走**主动**控制 + 自动化。**同一协议，两种信任姿态**——这是安全设计上的真实分歧点，不是谁对谁错。
2. **三处默认开启（使用统计 / 更新检查 / CrUX 外发）+ 三条明确关闭开关**，且 CI 环境自动关统计。这是"默认开启的遥测必须逐项可关"的可引用样本。
3. 把"暴露浏览器全部数据"写成免责声明而非藏起来，与"边界可审计成入场券"一致（同 10-06 的 openGym 文件级边界、esp32 自曝 Basic Auth 非加密、agency-agents 写明上游 119 上限）。
4. **官方厂商自己做 MCP 已成常态**（此前 10-01 记录过 modelcontextprotocol/servers 官方参考实现的并发与校验修复）。官方入场把"参考实现"推向"生产实现"，代价是遥测与数据边界需要显式协商。

---

### 9. anthropics/claude-plugins-community — 插件供应链的收口方就位

- **仓库**：anthropics/claude-plugins-community（JavaScript，总 4,530，日 +40）

**核心内容**
- Anthropic 官方**社区插件市场的只读镜像**。仓库里的 `.claude-plugin/marketplace.json` 就是可安装社区插件清单，**每晚从 Anthropic 内部审核流水线同步**。
- 每个列出的插件都满足三段门槛：经 claude.ai 提交（`clau.de/plugin-directory-submission`）→ 通过**自动化安全扫描** → 批准分发。
- 安装：Claude Cowork 走 `claude.com/plugins`；Claude Code 用 `claude plugin marketplace add anthropics/claude-plugins-community` 再 `claude plugin install @claude-community`。
- **治理选择很硬**：直接对本仓库开 PR 会被**自动关闭**，所有变更只能从内部审核流水线流出。
- 关联三个仓库：`anthropics/claude-plugins-official`（Anthropic 自维护插件）、`knowledge-work-plugins`（职能岗位插件，09-18 曾展开）、本仓库（社区插件）。

**值得关注的原因**
1. **插件/技能供应链从"社区自发"变成"厂商审核 + 自动化扫描 + 夜间同步"三段式**。把本期与前几期串起来看，这条线已经闭环：09-28 tech-leads-club 引用 Snyk"13.4% 市场技能含严重漏洞"→ 09-30 SkillSpector 给出首个可引用大样本基线（**31,132 技能中 26.1% 含漏洞、5.2% 疑似恶意**）→ 10-07 Anthropic 官方市场把"自动化扫描 + 内部审核"写成准入。**发现问题的一方和收口的一方都到位了**。
2. **"PR 自动关闭"是治理选择，不是偷懒**。理由与 10-05 cloudflare-os 拒绝外部贡献完全一致：AI 让写代码变简单后，难的是 review 与一致性。厂商选择把变更权收进流水线。
3. **"只读镜像"意味着市场不再是 git 协作产物而是流水线产物**——插件分发的权威源从社区转向厂商。对使用者的直接影响：**"在 GitHub 上能搜到"不再等于"可信"**，要认清单是否来自这条流水线。
4. 与本期第 3 条形成对照：技能作者在 README 里自证"官方构建只来自本仓库"，平台方在镜像里做审核同步。**信任声明正在从作者自述变成平台背书**。

---

### 10. mvschwarz/openrig v0.6.6 — 团队从"配"变成"装"

- **仓库**：mvschwarz/openrig（TypeScript，总 5,560，**周 +3,327**，本期 weekly 增幅第二）
- **事件**：**v0.6.6 于 10-07 02:04 (GMT+8) 发布**（构建自 main 的 `2620dea8`，含 #900 之后）。

**核心内容**
- 主题是"**让你快速到达你的 Agent**"：装完 OpenRig 后，kernel 的 operator 会主动迎接、问你想建什么、**给三支队选一支**，并在你自己的项目里启动。队伍现在**可分享、可从 GitHub 文件夹链接安装**；`workshop`（OpenRig 的四人建队，可在任意仓库里干活）从 `openrig.dev/rigs` 一条命令安装。
- 内置队伍**改名且不保留别名**：`starter`（Claude Code 建者 + Codex 审者）、`factory`（lead / advisor / builder / QA / design / 两个 reviewer）、专项队 `code-review` / `research` / `pm`，外加 `secrets-manager` 与 kernel。`adversarial-review` → `code-review`、`research-team` → `research`、`pm-team` → `pm`，**这三个没有别名**。
- 一批内置队**下线**：`conveyor`、`demo`、`implementation-pair`、`product-team`、`first-project-claude`、`first-project-mixed`、`factory-rsi`（已用它们建过的 rig 仍可恢复）。
- 两处默认值调整：**实现者与 QA Agent 不再默认加载 TDD 技能**（技能仍可用）；团队 seat 的默认权限改为**更少提示**——非 kernel 的 Claude Code / Codex seat，在既无 member/rig 级 `permission_policy`、也无该 seat 的权限选择、（Codex）无具名 profile 时，下次启动/恢复/fork/交接会拿到团队默认值。
- 升级须知（延续该项目一贯风格）：**升级 CLI 后必须重启 daemon**（运行中的 daemon 保留旧构建：`rig daemon stop` 再 `rig daemon start`）；daemon 首次启动会加一列数据库字段用于"非打断式选择"（已有 rig 默认关）；捆绑的 openrig-core 插件升到 0.1.4，运行中的 seat 下次启动才拿到。

**值得关注的原因**
1. **"团队配置"从需要设计的资产变成可安装的包**（GitHub 文件夹链接 + `openrig.dev/rigs` 一行命令）。这与 10-06 agency-agents 的 `strategy/runbooks.json`（团队花名册可被 CLI 解析、可 diff）同向：**Agent 团队定义正在变成可分发、可版本化的对象**。
2. **"改名不保留别名 + 下线内置队 + 默认不再加载 TDD"是一组明确的减法**。产品层主动拆掉自己积累的配置面，与 10-01 OpenClaw"整体退役 Tasks/TaskFlow"、mattpocock"禁 user-invoked 互调"同一信号：**删子系统成为成熟度标志**。
3. **默认权限改为"更少提示"**，与 10-01 claude-code-action"无人可问时一律拒绝"的默认值相反——两个项目对"默认该多问还是少问"给出了相反答案。这是本期最值得盯的分歧：**默认值的取舍取决于是否有人在旁边**。
4. 升级须知写得像运维手册（重启 daemon / 数据库加列 / 插件版本 / 已知未测项）。这种"自证方法学 + 明说未测范围"的做法（此前 v0.6.5 就带 SHA-256 与"未测试：macOS 真 Claude Code、真 Codex/Pi、Windows"）已成该项目签名。

---

## 三、其他趋势速览

**主榜/语言榜中未展开但值得记录**
- **tester-army/e2e `@e2e-dev/web@0.13.0`**（TS，日 +1,725，10-06）— **破坏性：要求 Node 22.22.3+ 或 24.8.0+**，CLI 在旧版拒绝启动并点名要升到哪个版本（Node 22.12–22.22.2、23、24.0–24.7 全不支持）。**弃 tsx 改用自建 oxc loader**，理由直指 tsx 带来的 esbuild postinstall 会让 pnpm 11+ 的 `pnpm install` 报 `ERR_PNPM_IGNORED_BUILDS`；现在 e2e 装的东西**没有任何一个会跑安装脚本**。附带一批语义变更（`.cts` 里的 `import` 不再编译成 `require`、拒绝 Bun/Deno 运行时、JS 文件里的 import 按 Node 规则解析而非 tsconfig paths）。**这是"pnpm 11 阻止依赖 build script"这条供应链策略在工具链上的连锁反应**，与本机 DSH 插件安装踩到的坑同源。
- **thedotmack/claude-mem v13.34.0 → 13.34.2**（TS，周 +2,104，10-06 17:13~18:17）— 13.34.2 移除一处 worker 回归：自 v13.29.0 起 worker 在每个请求前剪枝 observer 对话历史，一旦某个 tool-use 交换跌出最近 8 条消息就**原地替换为 stub**，结果**改写了 provider 已经收到的消息**——从第 5 次观察起，每条请求都改动更早的消息，prompt 前缀不再一致，走前缀缓存的 provider（OpenRouter / Gemini 等共享 HTTP observer 循环）无法复用缓存。现在共享 HTTP provider 不再剪枝，已发送的消息原样重发。**并明确声明"未在生产测过成本影响，因此本版不做任何省钱声明"**。典型样本：为了省 token 做的优化，反而在缓存层把省下的又花了回去。
- **heygen-com/hyperframes v0.8.137 → 0.8.139**（TS，月 +13,590）— 内置转写搬进桌面 App，`transcribe --json` 边听边流式吐词（parakeet-mlx 除外）；修 Studio 缩放/撤销/重载后拖拽落点、嵌套场景在根无时间轴时保持原位、`fromTo` 起始帧只取 from 值、时间轴跳转不再启动即将取消的缩略图加载。
- **NVIDIA/OpenShell v0.1.3-pre.5**（Rust，周 +5,228 / 月 +6,640，10-06）— 仅 CI 级变更（安全 workflow 改用 gpt-6.1-sol + high reasoning effort）；10-07 有新的 dev build。
- **DietrichGebert/ponytail v4.13.0**（JS，月 +28,592，10-05 18:54）— 主题是"**让 ponytail 稳定待在你设定的档位**"：Codex 切档会送达新档规则、每个项目保留自己的模式、**off 就是真 off**、状态栏徽章能扛住插件更新；**Kimi Code 加入 host，弃 ZCode**；README 增西/韩/简中/日四语。
- **earthtojake/text-to-cad v0.7.15**（Python，日 +619）— 导出带圆角的扫掠茶杯为闭合网格；CI 只跑"这个改动可能弄坏的东西"，安装分支写在 PyPI 之后。
- **pingdotgg/t3code** nightly `0.0.46-nightly.20261007.2761`（10-07 05:40）— 保持日更节奏。
- **OpenCut-app/OpenCut** 无新发布（最后 09-24 的 FFmpeg 8.1.3 build）；**pbakaus/impeccable** 无新发布（最后 10-02 Skill 4.5.0）；**msitarzewski/agency-agents** 10-07 有发布但 atom 无正文。

**本期新面孔（未展开）**
- [Joooook/12306-mcp](https://github.com/Joooook/12306-mcp)（JS，日 +320，总 2,265）— 基于 MCP 的 **12306 购票查询服务器**，已支持车次查询、列车过滤、**过站查询、中转查询**；配套 `12306-skill`。**MCP 垂类化已进入中文生活服务**。
- [AprilNEA/OpenLogi](https://github.com/AprilNEA/OpenLogi)（Rust，日 +163，总 23,014，v0.8.11 10-02）— Logitech Options+ 的**原生本地优先替代**，走 HID++ 与 UVC；纯文本 TOML 配置可跨机同步、GUI 旁有真 CLI；Linux 一等公民。安装须知写明"**先退出 Options+，两者争抢 HID++ 访问，同一接收器只能有一个 owner**"。
- [caddyserver/caddy](https://github.com/caddyserver/caddy)（Go，日 +566，总 77,434）— 自动 HTTPS 的 HTTP/1-2-3 服务器，本期 Go 榜增幅最高。
- [FalkorDB/FalkorDB](https://github.com/FalkorDB/FalkorDB)（Rust，日 +343，总 7,730）— 基于 GraphBLAS 稀疏邻接矩阵的图数据库（10-05 曾入速览）。
- [Stremio/stremio-web](https://github.com/Stremio/stremio-web)（JS，日 +211，总 14,415）— 老项目热度回温。
- [rui314/mold](https://github.com/rui314/mold)（Rust，日 +168，总 17,520）— 现代链接器。
- [eolix/photosuite](https://github.com/eolix/photosuite)（Rust，日 +118，总 833）— 忠于经典 Photoshop 的桌面图像编辑器，原生 PSD/PSB 兼容。
- [0x4m4/hexstrike-ai](https://github.com/0x4m4/hexstrike-ai)（Python，日 +53，总 12,478）— 面向 Agent 的攻击性安全 MCP 服务器（与 10-05 的 ARTEX 同域）。
- [0xShug0/audio.cpp](https://github.com/0xShug0/audio.cpp)（C++，日 +32，总 3,330）— 纯 C++ 音频模型推理引擎（ggml 驱动），TTS / STT / VAD 一体。
- [mirage-project/mirage](https://github.com/mirage-project/mirage)（CUDA，总 2,538）— Mirage Persistent Kernel，把 LLM 编译成单个 MegaKernel；[osayamenja/FlashMoE](https://github.com/osayamenja/FlashMoE)（CUDA，总 305）— 单 kernel 内做分布式 MoE（NeurIPS '25）。两条都属"算力层"信号，可下期跟进。
- [byoungd/up](https://github.com/byoungd/up)（JS，**周 +2,154**，总 67,567）— 中英双语终身学习指南，**中文非技术仓库连续多期在榜**（榜单结构性信号）。
- 其余：ys-ll/uniterm（Go，+32，总 751，30+ 协议一体化终端）、guohuiyuan/go-music-dl（Go，+27，10+ 平台音乐下载）、kanoqwq/UFI-TOOLS（JS，+260）、slavakurilyak/awesome-ai-agents（Go，+14）。

---

## 四、当日主线判断

1. **"Agent 原生"正在重做传统专业工具**。rea 把逆向工程的工具目录按"Agent 想学什么"重排（app overview / function dossier / feature trace），plannotator 把代码审阅做成浏览器标注面。**共同点：不是给旧工具加一个 LLM 对话框，而是按 Agent 的工作方式重新切分能力边界。**
2. **算力层"去单一供应商"从编译器走到 kernel**。DeepGEMM Ascend 单独开仓库，接续 10-02 tilelang 的昇腾 950 后端。同一套 MoE 原语、两套硬件实现，且共享接口不共享优化。
3. **成本压缩继续前移到"输出进入上下文之前"**。账本已四层：不产生中间结果（context-mode）→ 不读取（claude-mem）→ 不调用模型（e2e 录制回放）→ **不让原始输出进上下文（rtk / caveman）**。
4. **口径层面的诚实成为新标准**。rtk 拆穿"省 90% 是输出不是账单"、claude-mem"不测成本就不宣称省钱"、e2e 明说语义破坏点、openrig 明说未测平台。此前是修正数值（ponytail / RuView / codegraph），现在是**修正口径本身**。
5. **跨轮状态保真是这类工具最大的 bug 来源**。claude-mem 的 prompt-cache 回归（优化反而把缓存省下的花回去）、plannotator 的评论丢失、ponytail 的档位静默失效、rtk 的 hook 不覆盖 Read/Grep、openrig 的"升级必须重启 daemon"——**"控制平面失效通常是无声的"本期第三次被验证**。
6. **插件/技能供应链治理形成闭环**。SkillSpector 量化（26.1% 含漏洞 / 5.2% 疑似恶意）→ Anthropic 官方社区市场"自动化扫描 + 内部审核 + 夜间同步 + PR 自动关闭"。发现问题的一方与收口的一方都到位了，**"GitHub 上能搜到"不再等于可信**。
7. **记忆层第三条路线落地且都不花钱**。hindsight（纯 DB 读省调用）、ai-memory（默认零 LLM）、cognee（本地小模型 + 知识图谱）。三条路线共同前提是跨会话跨 harness；分歧在"记忆存在哪、谁来读"。
8. **"反向量化"与"压缩向量"并存，共同点是拒绝默认架构**。turbovec 证明向量可以留但必须压到 2–4 bit 并直搜压缩形式，OptMem（10-06）证明连数据库都不用。**float32 + HNSW 这个默认组合正在被两边同时放弃。**
9. **官方厂商默认开启的遥测必须逐项可关**。chrome-devtools-mcp 三个默认开启项（使用统计 / 更新检查 / CrUX 外发）+ 三条关闭开关 + CI 自动关。官方入场把"参考实现"推向"生产实现"，代价是数据边界需要显式协商。
10. **上一代项目成为下一代产品的地基**。omnigent 的沙箱列表含 OpenShell、记忆 extras 含 hindsight；10-05 已记 pi 被 cloudflare-os 列为关键依赖。**Agent 基础设施开始出现明确的"上下游分层"。**
11. **会话身份不可变被写成 API 约束**。omnigent 把 switch-agent 改为 410 Gone 并要求 fork；同 10-06 OptMem 的"位置即身份"。不可变比可变更便宜——省掉一整类状态同步 bug。
12. **本期榜单 Agent 生态占比为近十三期最高**。10 条详细里与 Agent 完全无关的只有 2 条（turbovec / DeepGEMM）。主榜 47 条（三榜去重）几乎全是已推送项目，**新面孔只能从语言维度榜取到**——这本身说明主榜头部已固化。

---

## 附：数据与方法备注

- 抓取：`.workbuddy-ai/scripts/fetch_trending.py --period daily|weekly|monthly`（纯 stdlib，无 token、无配额）。三榜条数：daily 12 / weekly 12 / monthly 23。
- **语言维度榜补位**：`fetch_trending.py` 不支持 `--lang`，用内联 Python 复用其 `parse_board()` 抓 `/trending/<lang>?since=daily`（python / typescript / rust / go / c++ / javascript / cuda / html 共 8 榜，合计 99 条）。**本期 10 条详细中 9 条来自语言榜**。
- 发布信息：`releases.atom`（`<content>` 去标签后即发布正文，成功用于 rea / turbovec / plannotator / omnigent / openrig / claude-mem / hyperframes / e2e / text-to-cad / ponytail）。`diagram-design` 与 `agency-agents` 的 atom **只有 `<updated>` 无正文**，改从 README 取信息。
- README：`raw.githubusercontent.com/<owner>/<repo>/main|master/README.md`（rea 51KB、diagram-design 54KB、plannotator 27KB、omnigent 26KB，均先 `sed` 去标签再定点 `sed -n` 取段，不整篇读）。
- **GitHub REST API 全程未使用**（10-01 起 60/h 配额已耗尽，未再尝试）。
