# GitHub AI 趋势日报 · 2026-10-08

> 数据源：github.com/trending 主榜（daily 13 / weekly 11 / monthly 25）+ **语言维度榜 12 个（155 条去重）**
> 说明：主榜头部已被前十三期推送过的项目占满（daily 仅 2 条新面孔），本期新面孔主要来自语言维度榜，来源列已如实标注。

## 榜单速览

| # | 仓库 | 语言 | 总 Star | 增幅 | 来源 | 一句话 |
|---|---|---|---|---|---|---|
| 1 | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | JS | 157,808 | +27,653 (月) | monthly | **v5.0.0 今日发布**：规则重建为"最小完整变更" |
| 2 | [kubernetes-sigs/agent-sandbox](https://github.com/kubernetes-sigs/agent-sandbox) | Go | 4,183 | +12 (日) | go | K8s 官方 `Sandbox` CRD，Agent 运行时编排收口 |
| 3 | [uber/ADR](https://github.com/uber/ADR) | Python | 1,923 | +25 (日) | python | Uber 生产级 Agent 检测响应，MLSys 2026 |
| 4 | [spotify/portal-ai-plugins](https://github.com/spotify/portal-ai-plugins) | TS | 2,425 | +2,181 (月) | monthly | Spotify 官方插件市场 + 廉价模型外派插件 |
| 5 | [xerj-org/xerj](https://github.com/xerj-org/xerj) | Rust | 3,135 | +339 (日) | rust | 本地 AI 搜索，"参考别人怎么解"降 token 2.7× |
| 6 | [bethington/ghidra-mcp](https://github.com/bethington/ghidra-mcp) | Java | 4,806 | +201 (日) | java | **209 个 MCP 工具** + 实时调试器 + P-code 仿真 |
| 7 | [fabio-rovai/open-ontologies](https://github.com/fabio-rovai/open-ontologies) | Rust | 926 | +121 (日) | rust | Lean 4 验证的本体变更证书，拒绝伪造证明 |
| 8 | [reconurge/flowsint](https://github.com/reconurge/flowsint) | TS | 9,518 | +215 (日) | typescript | OSINT 图谱调查，安全默认值写得很细 |
| 9 | [xingkongliang/skills-manager](https://github.com/xingkongliang/skills-manager) | Rust | 5,729 | +56 (日) | rust | 跨工具技能管理器，agent 只能经它改技能 |
| 10 | [steipete/CodexBar](https://github.com/steipete/CodexBar) | Swift | 22,293 | +47 (日) | swift | 92 个供应商的额度/重置时间进菜单栏 |

---

## 详细条目

### 1. DietrichGebert/ponytail **v5.0.0「Ponytail 5」**（JS，月 +27,653，总 157,808）

**事件**：10-08 03:51（GMT+8）发布 v5.0.0，规则、审查、审计三件全部从零重建。

**核心内容**
- **规则重写，长度减半**。目标改为「**最小完整变更**」：动手前 agent 必须先映射这次改动必须触达的一切（callers、测试、配置）以及可能破坏什么。**每条回复结尾必须写明跳过了什么、没检查什么、以及风险。**
- **Codebase map**：会话开始时给 agent 一张仓库已有内容的简图，先复用再新写。
- **`/ponytail-review` 重做为完整审查**：bug、安全、真实负载、缺失测试、速度、该删什么。读的是变更触及的代码，**不只是 diff**。每条发现必须说清四件事：代码在做什么 / 会出什么问题 / 怎么修 / 不改会怎样。
- **`/ponytail-audit`**：同样检查覆盖整个仓库，排序并指出先修什么。
- **基准**（对照不带 skill 的同款 agent：Claude Code + Opus 5.5，39 个任务含真实 FastAPI + React 仓库，各跑 5 次）：代码 **−53%**、时间 **−41%**、成本 **−26%**、输出 token **−45%**，且 **98% 的有风险逻辑带测试**（对照组 68%）。

**值得关注的原因**
1. 上一版（v4.12.0，10-05）刚把审查发现项编号化，v5 直接把「**先算影响面再写代码**」写成流程前提——从"少写"进到"少写且不破坏"。
2. 「每条回复必须声明跳过了什么」是继 09-29 主动修正自家数字、10-01 codegraph 自曝残余上下文 +80% 之后的又一步：**把不确定性写进输出契约**，而不只是修数值。
3. 98% 测试覆盖率这个数字比 LOC 更能站住——**"少写代码"本身无法证伪，但"少写且带测试"可以**。

---

### 2. kubernetes-sigs/agent-sandbox（Go，日 +12，总 4,183，Apache-2.0，v1.0.5.post1 10-06）

**事件**：Kubernetes **SIG Apps** 下的 `Sandbox` CRD 与控制器进入 v1.0.5 系列。

**核心内容**
- 核心 CRD `Sandbox`：**有稳定身份、持久存储、可暂停/恢复的单容器有状态长跑负载**。定位是填补 Deployment（无状态副本）与 StatefulSet（编号稳定）之间的空白——"像一台轻量单容器 VM，但建在 K8s 原语上"。
- 扩展三件套：
  - `SandboxTemplate` — 可复用模板，便于管理大量同类 Sandbox；
  - `SandboxClaim` — 从预热池领取，屏蔽底层配置细节；
  - `SandboxWarmPool` — 预热池，缩短新 Sandbox 就绪时间。
- **边界写得很清楚**：agent-sandbox **只是编排器**，低层容器隔离**委托给 gVisor / Kata Containers 等 Sandbox Runtime**，通过 `RuntimeClass` 配置 Pod。

**值得关注的原因**
1. 这是「**Agent 运行时 K8s 化**」的官方收口：09-23 期的 google/ax + agent-substrate 还是自建调度层，现在 K8s 官方 SIG 给出了标准 CRD——**自建调度层的窗口期在关闭**。
2. **职责切分是本期最值得抄的设计**：编排（本仓库）与隔离（gVisor/Kata）分层，谁都不越界；对照 10-02 Pi 的"默认不给权限系统，明说三种容器化"，思路一致但上升到了 K8s 标准 API。
3. WarmPool + Claim 把「Agent 冷启动」当**资源池问题**处理，是 09-29 trycua「云桌面池」的 K8s 原生版。

---

### 3. uber/ADR（Python，日 +25，总 1,923，Apache-2.0，MLSys 2026）

**事件**：Uber 开源 Agentic AI Detection and Response（ADR），**已在 Uber 生产环境部署**，配套论文被 **MLSys 2026** 接收。

**核心内容** — 五能力，其中四项开源：
| 能力 | 内容 |
|---|---|
| **Discovery** | 盘点员工端点上的 AI 应用、CLI agent、IDE 扩展、本地模型运行时、MCP server，标记未知面 |
| **Observability** | 跨 macOS/Linux/Windows 采集 7+ AI 编码工具的 agent 意图、工具调用、执行轨迹；含 Gemini CLI 会话日志与嵌套子代理 |
| **Benchmark** | ADR-Bench：**300+ 任务、134 个 MCP server、覆盖全部 17 种 agent 攻击技术** |
| **Detection** | 两层架构：高召回分诊 + 对可疑会话做更深的 agentic 推理 |
| **Prevention** | **本次开源不含**（"Stay tuned"） |

开源部分为 Discovery / Sensor / ADR-Bench / Detector；离线 **ADR Explorer** 引擎未开源。提供 `--detector llamafirewall` 无 key 冒烟路径。

**值得关注的原因**
1. **企业侧 Agent 安全第一次拿到"生产验证 + 同行评审"双背书**。此前同类（NVIDIA SkillSpector、OpenShell）要么厂商自评，要么社区扫描——这次是 Uber 生产数据 + MLSys 论文。
2. **攻击面清单可直接复用**（134 MCP server / 17 攻击技术 / 300+ 任务），比"26.1% 技能含漏洞"这类比例数字更可操作。
3. **Prevention 故意不开源** + 明确给出可复现评估流程（`docs/REPRODUCIBILITY.md`），把"开源边界"与"可复现性"分开处理——这是 10-02 UniMate 之后第二次看到边界写得这么清楚的厂商发布。

---

### 4. spotify/portal-ai-plugins（TS，月 +2,181，总 2,425）

**事件**：Spotify 开源官方插件市场，把内部开发者门户 **Spotify Portal** 接进 Claude Code / Codex / Cursor。

**核心内容**
- 六个工作流：`setup` / `doctor` / `search` / `service` / `actions` / `feedback`，底层调 `npx @spotify/portal-cli`。
- `doctor` 做**只读就绪诊断**（插件、CLI、认证、action 是否可用）；`actions` 提供 **built-in help + dry-run + confirmation** 三重保护；`service` 生成含归属、健康、事故、文档的服务简报。
- 重点在附带插件 **shunt**（暂仅 Claude Code）：把 **I/O 密集的 agent 工作——批量读文件、生成样板代码——通过 Portal CLI actions registry 路由到 AiKA 模式的廉价 worker 模型**。

**值得关注的原因**
1. **大厂开源内部 AI 生产力系统已成季候**：10-05 Cloudflare OS → 10-07 cursor/plugins → 今日 Spotify。区别是这次给的是"**接已有内部系统**"（门户、目录、actions）而不是另起一套。
2. **shunt 是任务级模型分级路由的第一个产品化样本**——不是"换个便宜模型"，而是按**工作类型**（读文件 / 写样板）定向外派，与 10-05 openhuman 用 System 1 小模型做工具检索是同一判断的两个实现。
3. `actions` 的 dry-run + 确认，把"让 Agent 调内部系统"的安全边界做成**默认路径**而不是可选项。

---

### 5. xerj-org/xerj（Rust，日 +339，总 3,135，Apache-2.0，v1.0.0-rc.91 今日 05:54）

**事件**：本地 AI 搜索引擎 XERJ 进入 rc.9x 密集迭代（rc.88 → rc.91 两天内）。

**核心内容**
- 自动索引任意文件夹，coding agent 不再逐个读文件。核心用例 **reference coding**：给 agent 一个任务，它先**下载并索引最接近的开源仓库，先复用别人怎么解决，再自己写**。
- **受控研究**（8 任务 / 4 语言 / 每臂 16 次 / 真实 `claude -p` token 计数）：输出 token 降至 **1/2.7**，解出率保持 **16/16**；日常使用报告约 5×。
- 检索 BM25 + kNN + hybrid；**默认 embedder 是词法、离线的**，神经 embedder 需 opt-in 且下载约 90 MB。单静态二进制，无 JVM。
- `xerj gain` 报"**实际省了多少——计数而非估算**"。`--insecure` 被明确声明为信任边界（关 TLS 与 API key 鉴权 = 超级用户可读删全部索引），默认只绑 127.0.0.1，其他接口明文绑定会拒绝启动。
- **加入社区的方式是提交一份实地报告 PR**（明说"负面评价也是好报告"），CLA 豁免。

**值得关注的原因**
1. **"参考别人已开源的解"被产品化成检索原语**。与 10-05 codegraph、09-30 PageIndex 并列但切口不同：那两者检索的是"自己的代码库"，XERJ 检索的是"别人已经解过的题"。
2. 默认词法 embedder + 神经 opt-in 是「**反向量化**」阵营的又一样本（PageIndex / context-mode / cognee / OptMem 之后），且**首次把 embedding 下载体积直接写进徽章**——把成本披露做到包装层。
3. `xerj gain`（计数而非估算）+ 把加入门槛设为"交一份可含负面结论的报告"，把 10-01 codegraph、10-07 rtk 的诚实口径又推了一步。

---

### 6. bethington/ghidra-mcp（Java，日 +201，总 4,806，v7.0.0-rc.1）

**事件**：Ghidra 的 MCP 服务端进入 7.0.0-rc.1；今日随 Ghidra 生态整体升温（同榜还有 LaurieWired/GhidraMCP +106、NationalSecurityAgency/ghidra +306）。

**核心内容**
- **209 个 MCP 工具，自称竞品 3 倍**。不止读：重命名、定型、注释、建结构、执行脚本、**P-code 仿真、实时调试器集成**。
- **实时调试**：16 个 `/debugger/*` 端点走 Ghidra TraceRmi 框架（Windows PE 用 dbgeng，其他平台 gdb/lldb）：launch、中断/恢复、step into/over/out、断点、寄存器、内存读、栈回溯，支持 **ASLR 感知的静态↔动态地址换算**；可选代理 22 个 `debugger_*` 工具到外部调试器。
- **SHA-256 函数哈希匹配做跨二进制版本的文档迁移**——"文档一次，处处适用"。
- 批量操作降低 **93%** API 调用；headless + GUI 双模、Docker 就绪。
- **v5.0 起把命名规范、类型安全、文档标准下沉到工具层**（自称 "opinionated by design"）：agent 与人类工程师不用在每次 prompt 里塞风格指南也能产出一致结果。

**值得关注的原因**
1. 对照 10-07 的 morluto/rea（约 130 工具），**逆向工程 MCP 的"工具数竞争"已经开打**，且都在从只读转向**写操作 + 动态分析**。
2. 「把团队约定下沉到工具层，而不是每次塞进 prompt」是本期最实用的一条工程结论，与 10-07 omnigent 的策略引擎、10-06 OptMem 的"位置即身份"同属**把规则写进代码而非文档**。
3. 跨二进制文档迁移解决了 RE 领域真实的重复劳动，是 MCP 工具少见的**领域原生价值**，而非通用能力包装。

---

### 7. fabio-rovai/open-ontologies（Rust，日 +121，总 926，MIT，v2.0.1 09-28）

**事件**：单二进制 Rust 工具，给生产本体（ontology）做"变更前影响分析 + 可独立验证的证明"。

**核心内容**
- 主张：**改动前先看清全部后果，再给评审者一份不需要信任你的证明。**
- **示例极具说服力**：一条 `ex:hasParent rdfs:domain ex:Person` 的改动——文本 diff 只有一行、blast radius 报 0、risk 报 low，但**新产生 901 条此前不存在的推论**（owl-rl 规则表，0.04s 算完）。**文本 diff 完全看不到这个缺口。**
- 输出**证书**：任何人几个月后**无需本机安装该软件、无需联网**，用 `oo-cert asserted.tsv derivations.tsv` 即可复验，退出码 0，定理 `OOCert.certificate_sound` 覆盖结果。
- **写入伪造结论，同一检查器退出 1 并指出哪条规则不成立**（README 称"这个拒绝，而不是头条数字，才是经得起审视的部分"）。
- 另有对 GCHQ HQDM 两个文件的实证审计：RDFS 版有 23 个"当类用但从未声明"的术语、12 个 range 指向关系而非类；OWL 版三个检查全过却不连贯——tableaux 判定 195 个类可满足、39 个不可判定，HermiT 正好把同样的 39 个判为不可满足。**每个计数都由测试重新计算**。
- 引擎 MIT 且承诺保持 MIT，商业价值放在托管平台。

**值得关注的原因**
1. **"可验证性"从 CI 检查升级为数学证明**。此前 09-28 Paperclip 原子执行、10-06 RuView 的 claim-check 还都停留在"工程可验证"，这里是 Lean 4 + 一阶逻辑证书。
2. **"文本 diff 看不见语义缺口"是对所有改配置/改 schema/改权限场景的通用警告**，与 10-05 claude-code 5 类权限绕过（匹配器看错目标）同源：表面正确、语义已变。
3. 证明被要求"**评审者无需信任作者**"，与 10-02 iFixAi 的"SUT 与 Judge 必须不同厂商，否则标记自评不可引用"是同一原则的两级实现。

---

### 8. reconurge/flowsint（TS，日 +215，总 9,518，Apache-2.0，v1.2.13 10-03）

**事件**：开源 OSINT 图谱调查工具，社区活跃度回升。

**核心内容**
- 图谱式侦察：实体覆盖域名 / IP / ASN / CIDR / 组织 / 个人 / 邮箱 / 电话 / 社交账号 / 加密钱包 / 网站；自动富化器含 DNS 正反向、子域枚举、WHOIS、ASN→CIDR、Maigret 用户名搜索、邮箱泄露查询、钱包交易与 NFT、网站爬虫与追踪脚本识别、n8n 连接器。
- 模块化五层：`types → enrichers → core → api → app`；FastAPI + PostgreSQL + Neo4j + Redis + Celery；前端在数千节点下不卡。
- **部署安全默认值写得很细**：
  - 只暴露 5173 一个端口；Postgres / Redis / Neo4j / API **全部绑 127.0.0.1**，仅经前端代理可达；
  - nginx 用 `map $http_host $is_flowsint_host` 做 **Host 头白名单防 DNS 重绑定**，默认只放 localhost / 127.0.0.1 / [::1]，**LAN 与公网部署必须自己 opt-in 主机名**；
  - 三个密钥（`AUTH_SECRET` / `MASTER_VAULT_KEY_V1` / `NEO4J_PASSWORD`）附生成命令。

**值得关注的原因**
1. **自托管工具的"安全默认值"正在成为竞争维度**——从"能跑"到"默认不害你"。Host 白名单 + 全内网绑定是可直接抄的模板（对照 10-06 esp32-c3-adblock 主动自曝 Basic Auth 是 LAN 信任边界而非加密）。
2. OSINT 图谱与 09-29 PLFM_RADAR、10-06 RuView 同属"感知世界"一类，但这是**纯公开数据 + 图谱推理，没有新增任何传感器**。
3. 明确 ETHICS.md + 明列"不得用于未授权入侵/骚扰/人肉"，与 10-07 ARTEX 的免责声明形成同季模式：**能力越强的工具，越把边界写在正文最显眼处**。

---

### 9. xingkongliang/skills-manager（Rust/Tauri，日 +56，总 5,729，v1.40.3 10-01）

**事件**：跨工具的 AI Agent 技能管理器，桌面 App（另有 CLI/概念图）。

**核心内容**
- 一个中央技能库（默认 `~/.skills-manager`），来源支持 Git 仓库、本地文件夹、`.zip` / `.skill` 归档、skills.sh 市场。
- 四个层级：**Library（中央库）/ Preset（命名技能组，一键整组开关）/ Global Workspace（按 agent 展示其全局目录的**真实**内容，含非本工具安装的技能）/ Project Workspace（项目级技能目录，可与中央库双向同步）**，另加 Linked Workspace 指向任意目录。
- **关键设计：让 agent 自己驱动 Skills Manager 去装技能、部署到别的 agent、查询"谁在哪"，而不是偷偷写进 agent 的文件夹**——这样来源、preset、更新追踪、每个 agent 的状态都不会被绕过。
- 多工具同步用 symlink 或 copy，卡片按 agent 显示徽章与实时同步状态；更新追踪可对比本地与上游内容。
- **备份/多设备同步接私有 GitHub 仓库，且合并是"技能感知"的**：一台重命名 + 另一台编辑能干净合并；真冲突不阻塞（本地保留，让你选 keep mine / use remote / keep both），快照可随时还原。操作有本地活动日志，可导出 zip 报障。

**值得关注的原因**
1. 技能生态从"分发"进入"**资产管理**"期。10-01 alirezarezvani 的 388 技能、10-05 marketingskills 的依赖图之后，缺的正是"跨 13 个工具时谁装了什么、版本对不对"。
2. **「让 agent 通过管理器改技能，而不是直接写文件夹」是本期最有价值的架构判断**——它把 10-07 那条"控制平面失效常常无声"（ponytail 一行 json 静默失效、rtk hook 不覆盖 Read/Grep）的正解具体化了：**给状态一个唯一入口**。
3. "技能感知合并"= 把 10-06 agency-agents 的"runbooks.json 可解析可 diff"推到"可三方合并"。

---

### 10. steipete/CodexBar（Swift，日 +47，总 22,293，MIT，0.73.0 10-07）

**事件**：macOS 菜单栏小工具（另有 Qt6 Linux 桌面版与跨平台 CLI），持续迭代。

**核心内容**
- 把**每个 AI 编码供应商的额度与重置时间**放到菜单栏。按 provider 显示 session / 周 / 月三类窗口与**重置倒计时**——"别猜要不要现在开始那个长任务"。
- 信用余额、Admin API 花费面板、供应商账单摘要、本地成本扫描；供应商状态轮询（事故徽章 + 栏图标叠层）。
- **隐私优先：复用已有会话（OAuth、device flow、API key、浏览器 cookie、本地文件），不存任何密码。**
- README 顶图标注 **92 个 provider**。分发渠道完整：Homebrew cask/formula、AUR、以及 macOS/Linux 的 arm64/x86_64/musl 静态 CLI 压缩包。

**值得关注的原因**
1. **"额度"这条线第四期连续在榜**：10-01 miuuyy 的 Pro Limits 75% 预警 → 10-02 freellmapi 的免费额度调度 → 10-05 claude-mem 的离线额度 + 到期回落 → 今日 CodexBar。说明**多产品并行 + 订阅额度已是常态工作方式**，不再是边缘需求。
2. 把额度做成**常驻可见的状态栏**，是"成本可见性"诉求的最轻量解；而"复用现有会话、不存密码"是这类工具唯一站得住的实现路径。
3. **92 个 provider 这个数字本身就是信号**——编码 agent 的供应商数量已多到需要专门工具做聚合。

---

## 其他趋势速览

| 仓库 | 语言 | 日增幅 | 要点 |
|---|---|---|---|
| [EpicGames/raddebugger](https://github.com/EpicGames/raddebugger) | C | +90 | Epic 原生 Windows x64 调试器（ALPHA）+ 自定义 **RDI 调试信息格式** + **RAD Linker**：debug info 数 GB 时链接**快 50%**，并避免 PDB 32 位内部表溢出导致的损坏。老项目热度回温，非新开发 |
| [microsoft/power-platform-skills](https://github.com/microsoft/power-platform-skills) | JS | +5 | 微软官方 Power Platform 插件市场。一键安装器自动装 `pac` CLI、探测 GitHub Copilot CLI / Claude Code、注册市场并开启自动更新。**今日第三家厂商官方插件市场** |
| [maximhq/bifrost](https://github.com/maximhq/bifrost) | Go | +22 | 高性能 AI 网关（HTTP v2.2.6），单 OpenAI 兼容 API 聚合 23+ 供应商 + 自动故障转移 + 语义缓存。**企业版才解锁自适应负载均衡、集群、护栏、MCP 网关** |
| [calesthio/Crucix](https://github.com/calesthio/Crucix) | JS | +13 | 本地"情报终端"，**仅 1 个依赖（express）**。27 个 OSINT 源（卫星火点/航班/辐射/星座/经济指标/市场/冲突/制裁/社交情绪）每 15 分钟并行拉取，接 LLM 后推 Telegram/Discord 告警。明确警告**未发行任何代币** |
| [harry0703/MangoDisk](https://github.com/harry0703/MangoDisk) | Rust | +32 | 与 MoneyPrinterTurbo 同一作者。跨平台磁盘清理，**安全条款很硬**：默认只读扫描、清理前必须确认、系统优化只用内置已验证设置且**永不接受任意注册表路径/终端命令/脚本**、改完回读验证、CLI 非交互必须 `--yes`；清理规则只接受声明式 TOML 且必须有明确安全边界 |
| [vorssaint/vorssaint-utils](https://github.com/vorssaint/vorssaint-utils) | Swift | +236 | macOS 菜单栏全家桶，"一个图标干十几个付费 App 的活"，本地优先，GPL-3.0 |
| [microsoft/markitdown](https://github.com/microsoft/markitdown) | Python | +188 | 文件/Office 文档转 Markdown（总 189k，长期在榜） |
| [smicallef/spiderfoot](https://github.com/smicallef/spiderfoot) / [Z4nzu/hackingtool](https://github.com/Z4nzu/hackingtool) | Python | +193 / +213 | 老牌 OSINT / 渗透工具集被重新发现，非新开发 |
| [mirage-project/mirage](https://github.com/mirage-project/mirage) / [deepseek-ai/DeepGEMM](https://github.com/deepseek-ai/DeepGEMM) | CUDA | +4 / +181 | MegaKernel 编译、FP8/FP4 GEMM，算力层持续在榜 |

**已推送仓库的动态**
- [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) 已到 **v0.8.140**（10-07 10:04），超过上期记录的 0.8.139。
- [trycua/cua](https://github.com/trycua/cua) 连发 `nightly-lume-v0.6.2`（10-08）。
- [xerj-org/xerj](https://github.com/xerj-org/xerj) 已升入本期详细（rc.91，今日发布）。
- 无新主版本：[thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) 仍 v13.34.2（10-06）、[mvschwarz/openrig](https://github.com/mvschwarz/openrig) 仍 v0.6.6（10-07）、[Tencent/WeKnora](https://github.com/Tencent/WeKnora) 仍 v0.8.2（09-24）、[vectorize-io/hindsight](https://github.com/vectorize-io/hindsight) 仅 integrations 子包更新。

---

## 当日主线判断

1. **厂商官方插件市场同日三家**（Spotify / 微软 / 前日 Cursor），且都从"给能力"转向"**接已有内部系统**"——大厂 Agent 化的落点是**门户与权限**，不是模型。
2. **Agent 运行时被 K8s 官方收口**（agent-sandbox 的 `Sandbox` CRD），且把"编排"与"隔离"职责显式切开（RuntimeClass 交给 gVisor/Kata）。自建调度层的窗口期在关闭。
3. **企业 Agent 安全拿到双背书**（Uber ADR：生产部署 + MLSys 2026），攻击面清单（134 MCP server / 17 攻击技术 / 300+ 任务）可直接复用；同时**"Prevention 不开源"成为新常态**。
4. **「最小完整变更」取代「最小变更」**（ponytail v5）：先算影响面、回复必须声明跳过了什么——**不确定性进入输出契约**。
5. **可验证性升到数学层**（open-ontologies 的 Lean 4 证书 + 主动拒绝伪造证明），且要求"评审者无需信任作者"——与 iFixAi"不得自评"同源。
6. **技能生态进入资产管理期**（skills-manager）。关键判断：**给状态一个唯一入口，让 agent 通过它改，而不是直接写文件夹**——这是对"控制平面失效常常无声"的正面解法。
7. **额度/成本可见性连续第四期在榜**（CodexBar，92 provider）。多产品并行 + 订阅额度已成常态工作方式。
8. **自托管默认值成为竞争维度**：flowsint 的 Host 白名单 + 全内网绑定 vs esp32-c3-adblock 主动自曝 Basic Auth 非加密——**同一季，两种诚实**。
9. **检索"参考别人的解"被产品化**（xerj，输出 token 1/2.7，默认词法 embedder、神经 opt-in）。"反向量化"阵营再添一例。
10. **逆向工程 MCP 工具数开打**（ghidra-mcp 209 工具 vs rea 约 130），且都从只读转向**写操作 + 动态分析**。
11. 非 Agent 项目 4/10（raddebugger 工具链、flowsint 基础设施属性、CodexBar 监控、open-ontologies 形式方法），与前几期持平。
