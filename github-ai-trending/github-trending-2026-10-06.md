# GitHub 趋势日报 · 2026-10-06

> 数据源：github.com/trending 三榜合并（daily **14** / weekly **21** / monthly **23**）+ 语言维度榜（python/typescript/rust/go/c/c++ 六榜）二次换榜
> 筛选口径：当日/本周新增 Star 高 + 技术方向有代表性 + 工程参考价值；优先取前十一期未展开的新面孔
> 说明：GitHub trending 的排列顺序 ≠ star 增幅排序，下文只报增幅，不声称名次

---

## 一、本期速览

| # | 仓库 | 语言 | 总 Star | 增幅 | 来源 | 一句话 |
|---|---|---|---|---|---|---|
| 1 | [DuarteSantos8/openGym](https://github.com/DuarteSantos8/openGym) | JavaScript | 4,486 | +1,433 (日) | daily | 自托管健身追踪，passkey + 断网不丢数据 |
| 2 | [boykopovar/AnyPS5](https://github.com/boykopovar/AnyPS5) | C++ | 5,114 | +997 (日) | daily | PS5 可执行文件**重链接**成原生 Linux/Windows 程序，非模拟器 |
| 3 | [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | Shell | 157,388 | +2,116 (周) / +744 (日) | daily+weekly | 完整"AI 代理公司"：8 大部门 + runbook 花名册 |
| 4 | [VictorTaelin/OptMem](https://github.com/VictorTaelin/OptMem) | Python | 1,962 | +85 (日，新仓库) | python 榜 | 426 token 提示 + 一个脚本 = Agent 永久记忆 |
| 5 | [M-Abozaid/esp32-c3-adblock](https://github.com/M-Abozaid/esp32-c3-adblock) | C++ | 1,483 | +196 (日) | daily | $2 ESP32-C3 跑 Pi-hole，53.7 万域名塞进 flash |
| 6 | [ruvnet/RuView](https://github.com/ruvnet/RuView) | Rust | 96,608 | +225 (日) | rust 榜 | 用 WiFi 穿墙感知呼吸/心率，$9 节点 |
| 7 | [666ghj/MiroFish](https://github.com/666ghj/MiroFish) | Python | 76,530 | +485 (日) | python 榜 | 群体智能预测引擎，千 Agent 数字沙盘推演未来 |
| 8 | [storytold/artcraft](https://github.com/storytold/artcraft) | Rust | 2,593 | +222 (日) | rust 榜 | "艺术家的 IDE"：3D 构图 + 62 模型目录 |
| 9 | [hieunc229/mailflare](https://github.com/hieunc229/mailflare) | TypeScript | 4,547 | +141 (日) | typescript 榜 | Cloudflare 上的自托管邮箱，免费收发 |
| 10 | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | TypeScript | 96,723 | +534 (日) | daily | **v13.32.0**：文件读取闸门默认开启（回归） |

### 已推送仓库的新动态（未展开详述，仅记变化）

| 仓库 | 动态 |
|---|---|
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | **v0.8.135→136→137**（10-05~10-06 单日三连发）：大内联图/脚本预览内存大幅下降、音频超导出上限报"Too loud"并 hover 显示峰值、Whisper `transcribe` 自动识别语种 + `--no-runtime-install` |
| [NVIDIA/OpenShell](https://github.com/NVIDIA/OpenShell) | **v0.1.3-pre.4**（10-05）+ 10-06 Development Build；本版仅 CI 级变更（预发布失败通知值班工程师） |
| [pingdotgg/t3code](https://github.com/pingdotgg/t3code) | nightly 0.0.46.2702：Effect 升 **4.0.1 稳定版**、新增 **原生 `/goal` 给 Codex/Claude 带目标状态 UI**、webhook 触发器 + relay 隧道转发、PR rate limit 时等待而非全失败 |
| [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | 10-06 有新发布（正文未在 atom 出现） |
| [pablostanley/yoinks](https://github.com/pablostanley/yoinks) | 仍 v0.3.1（**最后发布 2026-07-17**），日 +355 属热度回温非新开发 |
| Tencent/WeKnora / hindsight / VoiceStudio | 本期均无新版本 |

---

## 二、10 条详细

### 1. DuarteSantos8/openGym — 自托管健身追踪，把"数据主权"做成产品约束

**事件**：日增 +1,433 登顶当日榜，总 4,486。README 首句即立场："Most workout apps keep your data on their servers... or vanish when the company does."（2026-09-28 发布 v1.3.9）

**核心内容**：
- **技术栈极简到近乎挑衅**：后端是 `node:http` **只有两个依赖**（`@simplewebauthn/server` + `web-push`），全部数据存成 `./data` 下的 JSON；前端 React 19 + Vite 打静态文件，nginx 代理 `/api` 保证同源（passkey 硬要求）。
- **同步是"服务端乐观锁 + 客户端合并"**：每个 profile 一份文档带服务端 revision，设备发送上次见到的 revision + 本地改动；若期间别的设备写过，服务端**拒绝并返回当前文档**让设备合并重试。断网/登出期间未上传的改动不丢弃，界面显示离线横幅。
- **备份边界写死**：`./data` 下四个文件（`db.json` / `state-*.json` / `audit.log` / `secret`），"备好 `./data` 就是备份了全部"；passkey 私钥永不进服务端，留在手机安全硬件或密码管理器。
- **AI 教练与 MCP 均默认关闭**：AI 教练跑在你自己的服务器上、用你自己的 provider key（Anthropic/OpenAI/Gemini/Ollama），**每一处改动都要你批准**；MCP server 只读且本地，不进 Docker 构建。
- 训练逻辑（递进规则、1RM 估算、历史回读）放在 `frontend/src/lib/` 的**纯函数**里并配测试；API 用 OpenAPI spec 描述。

**值得关注的原因**：
- 这是"自托管替代 SaaS"公式的**又一次完整实例**，但它把"数据边界"写到了文件级粒度（哪四个文件、哪个字段会/不会写入），比 09-25 lap 的 EXIF 边界声明更彻底——**"边界可审计"正在从加分项变成入场券**。
- 两个依赖的后端 + JSON 存储 + 纯函数训练逻辑，是**"AI 时代的软件应该是可被 Agent 改的模板"**这一主张的可运行样本：代码小到人和 Agent 都能一次读完。
- passkey + 同源约束 + revision 冲突合并，是本地优先应用"既要离线可用又不要账号"的**三件套标准解**，可以直接抄。

---

### 2. boykopovar/AnyPS5 — PS5 游戏"重链接"成原生 Windows/Linux 程序

**事件**：C++ 榜日 +997，总 5,114。v0.1.0/0.1.1 于 09-28 同日发布。

**核心内容**：
- **不是模拟器**。项目含一个 [relinker](core/relinker)，把 PS5 可执行文件**转换成目标系统的原生格式**，再配上项目自实现的 [系统 prx 库](core/libs/prx) 做动态链接——"No emulation or separate runtime process"。
- 着色器重编译器输出 **SPIR-V**（构建时开 `ANYPS5_ENABLE_SPIRV_TOOLS` 就用 Spirv-Tools 校验）。
- 已跑通游戏清单（`docs/user/COMPATIBILITY.md`）：*Dreaming Sarah*（2D 平台）在 GTX 1050 Ti / i5-7500 上**稳定 60 fps**。
- 兼容性报数方式很克制：徽章显示的是"项目已知函数中被实现的百分比"，并加注"总数会随已声明函数增加而变大"——**不虚报覆盖率**。
- **不支持或意外状态一律抛 `std::runtime_error`**，`what()` 打到 stderr 后进程终止——明确选择 fail-fast 而非静默降级。
- 输入映射支持 SDL 手柄（含摇杆/扳机），键盘鼠标走 `anyps5-input.ini`；GPL-2.0 only；免责声明声明不含任何版权固件/密钥。

**值得关注的原因**：
- **"重编译原生"路线再次被验证**（此前有各类 N64/SM64 反编译项目），它绕开了模拟器的性能墙与法律灰区：产物是原生程序，不需要模拟器运行时。这与 10-05 的 AnyPS5 原始描述"automatic PS5 executables porting"一致，**说明该路线已从"能跑"进入"能跑 60fps"阶段**。
- **报数方式是对本期主线的最佳注脚**：兼容性徽章主动声明"分母会变"，与 codegraph（09-30 自曝残余上下文 +80%）、ponytail（09-29 主动下调自己的数字）构成同一条连续曲线——**开源项目的可信度来自主动削弱自己的数字**。
- fail-fast 而不是"尽量跑"，是系统软件在**正确性与可用性不可兼得**时的一个明确取舍，值得关注后续是否有人做按游戏分级的容错层。

---

### 3. msitarzewski/agency-agents — 把"一家 AI 代理公司"做成可安装花名册

**事件**：周 +2,116，日 +744，总 157,388（fork 25,383）。README 明写"Born from a Reddit thread"。

**核心内容**：
- **8 大部门**：Engineering / Design / Marketing / Project Management / Testing / Spatial Computing / Specialized / Game Development 等，每个 Agent 是**一个独立 Markdown 文件**，含 Identity & personality、Core mission & workflows、Technical deliverables、Success metrics。
- 职位具体到离谱且有判断力：`Reality Checker`（证据制认证、质量门、发布签字）、`Whimsy Injector`（微交互、彩蛋、品牌个性）、`Reddit Community Builder`、`Autonomous Optimization Architect`（LLM 路由、影子测试、成本护栏）、`Git Workflow Master`、`Filament Optimization Specialist`。
- **`strategy/runbooks.json` 是关键机制**：runbook 定义一个团队花名册（roster），installer 的 `--agent` / `--agents-file` 直接吃 runbook 列出的 agent id，**"一个 runbook 的团队按清单一次性装好"**——这就是把"组织配置"变成可版本化的数据文件。
- **多 harness 一键安装**：`scripts/install.sh --tool <t>` 覆盖 claude-code / cursor / codex / gemini-cli / opencode / copilot / openclaw / aider / windsurf / kimi / osaurus / hermes / vibe / dsh 等；`--division` / `--agent` 可只装子集；`--dry-run` 预览。
- **直面工具限制**：README 主动指出 OpenCode 运行时**只注册约 119 个 agent，其余静默丢弃**（附 upstream bug 链接），并说明 installer 会在选择超限时警告——**把上游缺陷写进自己的文档**。
- 另有原生桌面 App（macOS/Linux/Windows）浏览并一键安装 + 自动更新。

**值得关注的原因**：
- 这是 **09-28 paperclip（Agent 组织治理）与 09-30 alirezarezvani/claude-skills（388 技能）之间的第三条路线**：不是运行时管理、也不是技能库，而是**"岗位定义 + 组织拓扑"作为可分发资产**。`runbooks.json` 让"团队"第一次成为可被 CLI 解析、可被 diff 的对象。
- **agent 人格化 + 交付物导向**正在从"角色扮演"变成"合同"：每个 agent 文件都要写 success metrics，这与 10-05 iFixAi 的"独立审计、不得自评"是同一条治理思路的两端（定义职责 vs 验证职责）。
- 主动把 **OpenCode 119 上限**写进 README，是"边界可审计"在生态层面的延伸：**做多平台分发的人，必须替用户记住每个平台的天花板**。

---

### 4. VictorTaelin/OptMem — 426 token 的提示 + 一个脚本 = Agent 永久记忆

**事件**：Python 日榜 +85，总 1,962（**全新仓库**，2026-10-06 06:02 才有首个 release 记录，正文尚未写出）。

**核心内容**：
- 作者 VictorTaelin（前 Penrose/交互式定理证明领域知名人物）走**极简路线**：安装只需 `curl … install.sh | sh`，它打印一个 `## Memory` 块，**粘到 `AGENTS.md` 或 `CLAUDE.md` 顶部就装完了**；工具落在 `~/.optmem/memo`（单文件 Python 3，零依赖）。
- **存储设计是"位置即身份"**：`memory/LOG.txt` 每行一条记录、**定宽**、追加写、永不编辑；`TREE/` 里的摘要是**纯缓存，可从日志整体重建**。因此每次查找都是一次 seek——**一百万条记忆（608 MB）时 `wake` 只需 0.03 秒**。
- **六级命令**：`wake`（会话第一条命令，读记忆）/ `note`（记一条，≤280 字节，一次一条）/ `nap`（回答到期的合并）/ `recall`（逐字搜索全部记忆）/ `zoom`（把一个树节点展开成两半）/ `forget`（删掉坏摘要，下次 nap 重建）。
- **子代理被明确禁止使用**：提示词里写死"If you're a subagent: skip everything above"，并要求 spawn 时附一句 `You are a subagent. Don't run memo.`——理由是**子代理无法判断什么已被知道，它的记录会重复且错误**。
- `WAKE_LINES` 是**读取预算而非存储预算**，随时可改，不触发任何重算。

**值得关注的原因**：
- 记忆层此前已分两条路线（09-25：hindsight 服务化+LLM vs ai-memory 文件化+零 LLM），OptMem 是**第三条、也是最极端的一条：把记忆做成一个"定宽日志 + 可重建缓存"的 Unix 工具**，连数据库都不用。它的隐含主张是"**记忆不是检索问题，是文件格式问题**"。
- **"0.03 秒读 100 万条记忆"这一数字的取得方式值得学**：不是优化查询，而是设计**定宽记录使查找退化为一次 seek**。这与 09-30 context-mode 用 SQLite+FTS5+BM25 而非向量库、PageIndex 用树索引而非向量，构成**同一批"反向量化"工程判断的第四例**。
- **"子代理不得写记忆"是一条之前没被显式说过的规则**。它与 10-05 paperclip 的不可变审计日志、iFixAi 的"不得自评"是同一族约束：**写入权必须与判断力对齐**。

---

### 5. M-Abozaid/esp32-c3-adblock — $2 芯片跑 Pi-hole，53.7 万域名装进 flash

**事件**：日 +196，总 1,483。被 [Tom's Hardware](https://www.tomshardware.com/networking/clever-hacker-fits-537-000-domains-in-a-tiny-usd5-esp32-ad-blocking-dongle-firmware-uses-only-around-50kb-of-ram-and-can-answer-blocked-lookups-in-10-milliseconds)、XDA、Korben 报道。周更 blocklist（10-05 自动构建 **110,162 条**）。

**核心内容**：
- **核心技巧**：不要把 blocklist 放 RAM，而是**把域名存成有序的 40-bit 哈希放进 flash，然后二分查找**。141k 域名 = 0.67 MB flash + **约 50 KB RAM**，一次查询约 18 次 flash 读（含 WiFi 往返约 10 ms）。
- **为什么是 40 bit**：按生日界算，141k 域名碰撞约 0 个，537k 约 1 个；降到 32 bit 省 20% flash 却要在 250k 时冒约 7 个碰撞；升到 64 bit 每个域名浪费 3 字节去解决一个不存在的问题——**参数选择有完整推导**。
- **同一技巧在大芯片上更划算**：16 MB 的 ESP32-S3 上哈希可放约 **270 万域名**，而字符串方案在 8 MB PSRAM 里只能放约 46.6 万——"哈希放 flash 基本处处胜过字符串放 PSRAM，C3 只是让这件事无可辩驳"。
- **安全章节写得像渗透报告**：状态变更端点（`/ban` `/addblock` `/upload` `/update` `/forgetwifi`…）全部要 HTTP Basic Auth；**明确声明 Basic Auth 是 LAN 信任边界控制而非加密**（base64、明文 HTTP、可被嗅探）；额外要求自定义 `X-Requested-With: c3-adblock` 头来堵**浏览器缓存 Basic Auth 导致的 CSRF**（`<form>` 自动提交带不上自定义头）；自定义域名渲染前 HTML 转义，堵存储型 XSS；`secrets.h` 仍是占位密码时固件打警告并显示横幅但**仍然启动**——这个"不拦你但告诉你"的选择也写明了。
- 约束与取舍透明：固件 OTA 需要双 app 槽 → blocklist 只剩约 1.3 MB（约 25 万域名）；要 53.7 万就得放弃 OTA，由 `partitions.csv` 决定。

**值得关注的原因**：
- 这是**"算法选择换来数量级成本差"的教科书案例**：同一功能，从"$8 带 PSRAM 的板子"降到 "$2 不带 PSRAM 的板子"，靠的不是优化代码而是换数据结构。它给所有"边缘侧跑 AI/规则引擎"的项目一个提示：**先问"我到底必须把什么放在 RAM 里"**。
- 安全章节是本期最好的一份**"自曝弱点式"文档**：明确说 Basic Auth 挡不住 on-path 攻击者、说 AP 配置门户是开放的无密码的、说默认密码是公开的——**它列出的是"我防护了什么、没防住什么、为什么接受"**，而不是"我很安全"。
- 与 10-05 的 text-to-cad（Windows Smart App Control 拦截未签名模块）等一起，说明**"物理世界 + 边缘设备"分支正在快速增长**，且这些项目的文档质量普遍高于纯软件项目。

---

### 6. ruvnet/RuView — 用 WiFi 信号穿墙测呼吸与心率

**事件**：Rust 榜日 +225，总 96,608（fork 12,712），MIT，测试 1,463 通过。

**核心内容**：
- **原理**：用**低至 $9 的 ESP32 节点采 CSI（信道状态信息）**，捕捉人呼吸/移动对射频的扰动，得到存在/人数/呼吸率/心率/活动识别/环境指纹；配套 Cognitum Seed 做持久记忆与 **Ed25519 见证链**（每次测量密码学存证）。**无摄像头、无可穿戴、无需联网**。
- **模型小到可笑的量级**：Hugging Face 上的 `ruvnet/wifi-densepose-pretrained` 模型 **8 KB（4-bit 量化）**，Raspberry Pi 上微秒级推理。
- **主动撤回旧指标**：v2 encoder 报告**诚实的、无标签的留出集 temporal-triplet 准确率 82.3%**（相比 66.4% raw），并注明"此前的 100% 存在检测是在单类录音上测的，已撤回"。同一份 README 里还标注"unified RF world model 的精度在真实数据验证前仍是合成的"。
- **生态对接完整**：Home Assistant（`--mqtt` 一个开关，21 个实体/节点，含 10 个语义状态如 someone-sleeping / fall-risk-elevated）+ Apple Home（HAP-1.1 bridge）+ Google Home + Alexa + Matter；3 个 starter HA Blueprint。
- **RuView MetaHarness**：把"上手/标定/训练/验证/查证主张"做成 npm 工具链——`doctor`（环境自检 + 带来源的指引）、`devices`、`esp32 --watch`、`mcp start`（stdio 或 HTTP）、`mod`（Claude Code 集成）、`claim-check`（检查一份报告里的主张是否站得住）、`verify`（重放确定性证明）、`brain search`。
- **安全默认**：Agent 运行默认只读，写工作区要 `--allow-write` **和** `--confirm` 两个都开；读硬件要 `device-access` 授权；**刷固件和标定永不通过 HTTP 传输执行**；设备上报的生命体征标注为"未验证"；检索到的 brain 内容"是证据不是权威"。
- 版本 v0.9.1，`npx @ruvnet/ruview@0.9.1`。

**值得关注的原因**：
- **"感知"正在脱离摄像头**。从 09-30 PageIndex（读取不下模型）、10-05 text-to-cad（Agent 进物理世界），到 RuView **用环境已有的射频当传感器**，同一主线在三个不同模态上推进：**用已有基础设施替代新增硬件**。
- **`claim-check` 这个命令是本期最值得抄的设计**：它把"模型/项目宣称的指标是否被证据支持"做成一个可执行的检查项。与 09-30 SkillSpector 的 SARIF 基线、10-05 codegraph 的"两臂都屏蔽自家 CLI"连起来看，**"可验证性"已经从一个属性变成了一个工具类别**。
- **撤回 100% 那个数字的处理方式**（在 README 里明写"是在单类录音上测的，已撤回"）是研究型项目该有的样子，也是"数据集泄漏/单类评测"这类常见错误的公开纠错样本。

---

### 7. 666ghj/MiroFish — 群体智能引擎，在数字沙盘里推演未来

**事件**：Python 榜日 +485，总 76,530（fork 11,701）。演示含"武大舆情模拟"与"《红楼梦》后 40 回推演"。

**核心内容**：
- **五步工作流**：① **Graph Building**（从种子材料抽实体 + 注入个体/集体记忆 + 建 GraphRAG）→ ② **Environment Setup**（实体关系抽取 + Persona 生成 + Agent 配置注入）→ ③ **Simulation**（**双平台并行模拟** + 自动解析预测需求 + 动态时序记忆更新）→ ④ **Report Generation**（ReportAgent 带工具集深度交互）→ ⑤ **Deep Interaction**（**可以直接和沙盘里的任意 Agent 对话**）。
- **输入输出极简**：上传种子材料（数据分析报告、新闻、甚至小说）+ 一句自然语言的预测需求 → 返回详细预测报告 + 一个可深度交互的高保真数字世界。
- **"上帝视角"注入变量**：模拟过程中可动态注入变量以推演不同未来轨迹。
- **定位自觉分层**：宏观层面是"决策者的预演实验室（政策/公关零风险测试）"，微观层面是"个人创作者的创意沙盘（推演小说结局）"——**把严肃预测和好玩模拟放在同一个产品里，并明说两者都算用途**。
- 技术栈：Node 18+ 前端 + Python 3.11/3.12 + `uv`；LLM 走任意 OpenAI SDK 兼容端点（推荐 Qwen-plus/Bailian），外部记忆依赖 **Zep Cloud**（免费额度够简单使用）；README 提醒"**消耗大，先用少于 40 轮试**"。

**值得关注的原因**：
- **这是"多 Agent"从工具走向"社会模拟"的一次落地**，且它把成本控制写在了安装说明里（"先用少于 40 轮"），说明作者清楚这类系统的**主要成本是 token 而不是算力**——延续了本期"算力克制"主线的另一种形态。
- **"可以直接和模拟世界里的 Agent 对话"是一个新的交互范式**：模拟不再是跑完出一份报告，而是**一个可以继续追问的世界**。这比 09-28 THU-MAIC 的互动课堂更进一步（那边是教学场景，这边是不设限的推演沙盘）。
- 值得关注的**风险也在这**：高保真数字世界里跑出的结论，与真实世界的差距如何标注？RuView 用了"untagged 数据标注为 unvalidated"的做法——**MiroFish 这类系统目前还没看到对应的置信度披露机制**，这是后续该盯的点。

---

### 8. storytold/artcraft — "艺术家的 IDE"：先搭场景再生成

**事件**：Rust 榜日 +222，总 2,593。最新 v0.41.0（09-26）。

**核心内容**：
- **主张："Turn prompting into *crafting*"**——不是"输入一句提示等一张图"，而是**先建构场景再生成**：2D 里合成、3D 里布景、选配合你工作的模型。
- **视觉控制能力清单**（这是它区别于所有 prompt 工具的地方）：Image to Location（虚拟演员放进一致环境、同房间规划多机位）、3D 图像合成（背景/前景/道具分层建立景深）、Image to 3D Mesh、**Character Posing**（先摆姿势再生成）、**Scene Blocking with Kitbashing**（用 3D 素材套件控制机位/摆放/景深）、**Character Identity Transfer**（用摆好姿势的人偶引导角色位置与姿势）、背景移除、混合素材合成。
- **模型目录 62 个，按提供商分组**：Images 16（Nano Banana / GPT Image 1.5~2.5 / FLUX.1~1.1 / Seedream 4~5.0 Pro Ultra）、Video 25（Seedance 1.0~2.0 / Kling 1.6~3.0 / Veo 2~3.1 Lite）、另有 music & sound、3D meshes、worlds（World Labs Marble + Gaussian splats）；外部提供商含 **Grok（Grok Imagine/Video）、Midjourney、Sora 1/2 + GPT Image 1**。
- 目录**逐条标注状态**：† = 当前禁用，‡ = 受限模型（桌面端不可用）——不假装所有模型都能用。

**值得关注的原因**：
- **"控制"正在成为 AI 创作工具的竞争力分界线**。此前 09-30 hyperframes 用 HTML→确定性 MP4 解决"可复现"，10-01 MoneyPrinterTurbo 解决"多入口"，10-05 OpenMontage 解决"渲染前审批门"——artcraft 补的是**"生成之前先决定构图、身份、机位"**这一环，也是唯一一个把 **3D 台面**做成一等公民的。
- **62 个模型的目录化管理**说明一个新问题浮出水面：模型多到需要一个专门的**模型目录层**（带启用状态、提供商映射、能力分类）。这与 cursor/plugins 在 09-28 做 MCP 插件声明 server placement 属同类——**生态膨胀后，元数据管理本身成为产品**。
- 值得盯的点是许可与来源：README 注释说明目录来源是自家 Rust 源码里的配置文件而不是手写表格——**目录与代码同源**，减少了文档漂移。

---

### 9. hieunc229/mailflare — 跑在你自己 Cloudflare 账号里的邮箱

**事件**：TypeScript 日榜 +141，总 4,547。

**核心内容**：
- **一键 Deploy to Cloudflare**，整套跑在你的 Cloudflare 账号里；邮件存在**你自己的 D1 数据库**，附件存在**你自己的 R2 桶**——无论用哪个发送/接收提供商。
- **收发可混搭、按域名选择**：接收默认走 Cloudflare Email Routing（免费）；发送可用 Resend（免费 **3,000 封/月、100 封/天、3 个域名**）、Amazon SES（新账号 $200 额度约 200 万封；之后 **$0.10 / 千封**）、或 Cloudflare Email Sending（需 **$5/月 付费 Worker 计划**）；DNS 仍由 Cloudflare 管。
- **功能是"完整邮箱"而非转发器**：邮箱（个人/共享 + 授权他人访问）、收发带附件/富文本/签名/自动回复、**日历**（重复事件 + 时区 + 参与者收邀请）、**预约页**（公开链接让别人订你的空闲时间）、搜索/文件夹/星标/稍后/归档/垃圾/回收站、**路由规则**（存储/转发/拒收/分类）、实时收信通知、导入导出 + 联系人 + 屏蔽发件人。
- **管理面完整**：用户、权限、API key、webhooks、**审计日志、备份**；**AI 助手**（搜邮件、起草回复、管理日历事件）；**MCP 访问**（每个 key 独立权限）。
- 诚实标注价格与陷阱：价格会变，请自己核对；**SES 新账号默认在 sandbox，只能投递给已验证地址**，要去 AWS 控制台申请生产权限；部署需要 `CF_TOKEN` 且**必须给足一组 scoped 权限**，且 **Worker 名必须保持 `mailflare`**（改名会坏）。

**值得关注的原因**：
- 这是"**自带云账号的自托管**"（BYO-Cloud）模式的又一标准件，和 10-05 openship（列出需你在云厂商侧应用的防火墙规则）属同一族：**产品把运行成本与责任显式交还给用户的云账号，自己只交付代码与迁移路径**。
- 关键增量是**"数据与算力同账户"**：邮件正文在你 D1、附件在你 R2、算力在你 Worker——**"数据不出户"从服务端自托管进一步缩小到"不出你的云账号"**，比传统自托管少了一个"我信任的那台 VPS"环节。这个模式对国内用户的实际价值是账单可预测（免费层明确）与治理边界清晰。
- **MCP + 每 key 独立权限 + 审计日志**三件套同时出现，说明"给 Agent 开邮箱"已经被当成**需要权限模型的正经集成**，而不是一个 API key 打天下——和 10-01 claude-code-action 的"安全约束写成会失败的 CI 检查"是同一条治理曲线的两端。

---

### 10. thedotmack/claude-mem **v13.32.0** — 文件读取闸门回归并默认开启

**事件**：三榜俱在（日 +534，总 96,723），**v13.32.0 于 2026-10-06 05:51 GMT+8 发布**（距本期运行约 8 小时）。

**核心内容**：
- **File Read Gate 回来了，且默认开启**：当 Claude Code 试图 `Read` 整个代码文件、而 claude-mem 已有该文件的 observations 时，**这次 Read 被拒绝**，改为给模型该文件的 observation 时间线 + 更便宜的替代路径：
  - 要当前代码 → `smart_outline` 拿符号与行号，再 `smart_unfold` 展开需要的那几个；
  - 要历史工作 → `get_observations`；
  - **要精确行（例如 Edit 之前）→ 带 `offset`/`limit` 的定向 Read**。部分读取永远放行，且**它满足 Edit 的 read-before-edit 规则，所以编辑永不卡死**。
- **这段历史写得极清楚**（值得学）：闸门 4 月就做了但没发——**它破坏了 Edit**，当天软化成"允许 + 附加上下文"，v12.0.0 发的就是这个；7 月 hook 改成异步，**而异步 hook 什么都拦不住**；本版把闸门拿回来，并用"放行定向 Read"解决 Edit 问题（附 PR #4549）。
- **六个条件全部满足才拦**（否则不拦）：① 是 Claude Code 主会话（不是 Codex/Kimi/Qwen Code/子代理）② 文件是 `smart_outline` 能解析的代码（不是 md/yaml/toml/json）③ 文件按同一套 symlink-aware 规则在工作区内 ④ 文件 ≥1,500 字节且**最新 observation 比文件新** ⑤ 这次 Read 会返回整个文件 ⑥ 支撑 smart 工具的 tree-sitter CLI 已安装。
- **可关闭且有三条路径**：settings.json 的 `CLAUDE_MEM_FILE_READ_GATE_ENABLED: "false"`、同名环境变量、或 viewer 里 Advanced → "Block full-file reads" 开关；`CLAUDE_MEM_DISABLE_FILE_CONTEXT=1` 关掉整个 hook。**闸门关闭时 Read 正常通过，时间线仍作为上下文附加。**
- **fail-open 明确**：PreToolUse 的 Read hook 恢复同步（15 秒上限、3 秒 worker 预算），**慢或缺失的 worker 永不阻塞 Read**；hook 不再回 `allow`，所以 Claude Code 自身的权限提示照常生效。
- **带一个可跑的对照实验**：`npm run eval:read-gate` 用真实 Claude Code 对两个隔离的、预置数据的 worker 跑（一个开闸门一个关），**在 `claude-sonnet-5-5`（每例 3 轮）和 `claude-opus-5-5`（每例 2 轮）上所有判定均通过**：开闸门的每次整文件 Read 都被拒、没有任何一轮拿到整个文件、答案靠 outline/unfold 正确、编辑只改了预期行。
- 另新增 opt-in 的 **worker 空闲退出**（`CLAUDE_MEM_IDLE_EXIT_SEC`，默认 0 保持现状）。

**值得关注的原因**：
- **这是本期"成本战场第四层"——控制 Agent 读什么——最激进的一次落地**。此前 claude-mem 靠三层检索省 token（09-30），现在直接**在工具层拦截**。它与 context-mode 的"让模型写代码去读数据"、codegraph 的"少工具调用"、e2e 的"录制回放不调模型"合起来，说明**成本优化的阵地已从 prompt 挪到了工具调用边界**。
- **"异步 hook 拦不住任何东西"这个 bug 值得所有做 hook 的人记住**——一个安全/成本控制机制被异步化后**静默失效**，和 10-05 ponytail 的"一行 plugin.json 让规则从未注册到模型"是同一种失败模式：**控制平面失效时通常是无声的**。
- **附上真实模型的对照实验**（两个隔离 worker + 双模型多轮）把"我修好了"变成了"可复现地证明修好了"，这是本期"自证方法学"的又一次出现；同时它把失败的尝试（4 月为什么没发）写进发布说明，**比结果更值钱**。

---

## 三、其他趋势速览

| 项目 | 数据 | 看点 |
|---|---|---|
| [M-Abozaid/esp32-c3-adblock](https://github.com/M-Abozaid/esp32-c3-adblock) | 周更 blocklist 10-05 自动构建 110,162 条 | 周更由 GitHub Actions 自动完成并发布到固定 URL，设备设一次即长期自持 |
| [Alishahryar1/free-claude-code](https://github.com/Alishahryar1/free-claude-code) | Python，+120，总 56,759 | 让 Claude Code/Codex/VSCode/Pi/OpenCode 等 10 个 harness 走免费额度 |
| [p-e-w/heretic](https://github.com/p-e-w/heretic) | Python，+117，总 33,471，forks 3,743 | 自动 abliteration，社区已发 5,000+ 模型（09-30 起持续在榜） |
| [gumyr/build123d](https://github.com/gumyr/build123d) | Python，+19，总 3,317 | **text-to-cad 的底层 CAD 库**（10-05 已推 text-to-cad，这是其依赖） |
| [CluvexStudio/Aether](https://github.com/CluvexStudio/Aether) | Rust，+22，总 2,094，**v2.3.0 10-04** | 抗审查客户端：MASQUE(HTTP/3&2) + WireGuard + 嵌套隧道；**端到端数据面校验后才信任网关** |
| [skyhook-io/radar](https://github.com/skyhook-io/radar) | Go，+36，总 3,654 | 缺失的 K8s UI，**内置给 Agent 用的 MCP server** |
| [henrygd/beszel](https://github.com/henrygd/beszel) | Go，+29，总 25,992 | 轻量服务器监控，历史数据 + docker stats |
| [linshenkx/prompt-optimizer](https://github.com/linshenkx/prompt-optimizer) | TypeScript，+146，总 36,541，AGPL | 四形态（Web/桌面/Chrome 扩展/Docker）+ **分析与对比评估**（判断 prompt 是否真的变好）+ MCP；纯客户端直连供应商 |
| [gvisor](https://github.com/google/gvisor) | Go，+39，总 19,559 | 容器应用内核，Agent 沙箱的底层常客 |
| [turso](https://github.com/tursodatabase/turso) | Rust，+37，总 24,642 | Rust SQLite 兼容库，**开始说 Postgres 协议** |
| [FalkorDB](https://github.com/FalkorDB/FalkorDB) | Rust，+391，总 7,516 | GraphBLAS 之上的超快图数据库，稀疏矩阵 |
| [longbridge/gpui-kit](https://github.com/longbridge/gpui-kit) | Rust，+141，总 16,237 | Rust GUI 组件（10-01 已展开） |
| [Effect-TS/effect](https://github.com/Effect-TS/effect) | TypeScript，周 +791 | **4.0.1 稳定版**已被 t3code 等采用 |
| [caddyserver/caddy](https://github.com/caddyserver/caddy) | Go，日 +515 / 周 +683，总 77,241 | 自动 HTTPS 的 Web 服务器，连续在榜 |
| [TencentCloud/Octop](https://github.com/TencentCloud/Octop) | Python，周 +1,416，总 7,056 | 单进程多用户多 Agent 自托管助手 |
| [dortania/OpenCore-Legacy-Patcher](https://github.com/dortania/OpenCore-Legacy-Patcher) | Python，+32，总 18,450 | 老 Mac 装新 macOS，非 AI 类常青树 |
| [Ollama](https://github.com/ollama/ollama) | Go，+73，总 182,287 | 本地模型运行时的基本盘 |

---

## 四、当日主线判断

1. **"边界可审计"成为入场券**：openGym 把数据边界写到文件名与字段级（哪四个文件、passkey 私钥不进服务端）；esp32-c3-adblock 的安全章节明说 Basic Auth 是"LAN 信任边界控制而非加密"，并列出 AP 门户开放、默认密码公开等**没防住的部分**；agency-agents 主动把 OpenCode 的 119 agent 上限写进自己 README。**"我防护了什么/没防住什么/为什么接受"正在替代"我很安全"。**

2. **反向量化的第四例，且这次连数据库都不要了**：OptMem 用"定宽日志 + 可重建缓存"实现 100 万条记忆 0.03 秒读取。继 PageIndex（树索引）、context-mode（SQLite+FTS5+BM25）、ai-memory（Markdown+git）之后，**"记忆/检索不是向量问题"已是稳定判断**，且实现越来越轻。

3. **成本战场进入第四层：控制"读什么"与"不产生什么"**：claude-mem v13.32.0 直接**在 PreToolUse hook 拒绝整文件 Read**，改发 observation 时间线。加上 e2e 的录制回放、context-mode 的写代码读数据、codegraph 的少工具调用，**省钱的着力点已整体移到工具调用边界，而不是 prompt 压缩**。

4. **开源项目的可信度来自主动削弱自己的数字**：RuView **公开撤回"100% 存在检测"**（单类录音所致），改为 82.3% 的诚实留出集指标，并标注 world model 精度"在真实数据验证前仍是合成的"；AnyPS5 的兼容性徽章注明分母会随声明增长；claude-mem 把"4 月为什么没发"写进发布说明。这条曲线从 09-29 ponytail 开始，本期到达新高度。

5. **"控制平面失效通常是无声的"成为共识性教训**：claude-mem 明写"异步 hook 拦不住任何东西"；前一天 ponytail 才刚修"一行 plugin.json 让规则从未注册到模型"。**做权限、成本、安全 hook 的人必须先回答"它失效时我会不会知道"。**

6. **验证本身成为工具类别**：RuView 的 `claim-check`（检查一份报告的主张是否站得住）+ `verify`（重放确定性证明）、claude-mem 的 `eval:read-gate`（真实模型双 worker 对照）、iFixAi 的"不得自评"硬编码。**"把不可验证的变成可验证的"已经产品化。**

7. **组织/岗位定义成为可分发资产**：agency-agents 的 `runbooks.json` 让"团队花名册"变成可被 CLI 解析、可被 diff、可被版本管理的数据文件；配合 OptMem 的"子代理不得写记忆"、paperclip 的不可变审计日志，**Agent 治理的关注点从"能力"转向"写入权与判断力的对齐"**。

8. **感知与创作都在"先建构、后生成"**：artcraft 主张先搭 3D 场景/摆姿势/定机位再生成（62 模型目录带启用状态），RuView 主张用环境已有的 WiFi 当传感器（而非新增摄像头）。**共同点是都不新增输入硬件，而是先把已有信号结构化。**

9. **"自带云账号"型自托管的公式定型**：mailflare = 开源代码 + Deploy to Cloudflare + 数据落你自己的 D1/R2 + 混搭 Resend/SES + 免费层明确 + 加价与陷阱写清楚（Worker 名不能改、SES 默认 sandbox）。与 10-05 openship（列出云侧防火墙规则）同族：**产品只交付代码与迁移路径，成本与责任显式交给用户的云账号。**

10. **非 Agent 项目 6/10，为近十二期最高**：openGym、AnyPS5、esp32-c3-adblock、RuView、artcraft、MiroFish 中严格意义上的"Agent 工具链"只有 OptMem、agency-agents、claude-mem 三条。**本期榜单的结构性信号是：Agent 基础设施之外的"具体问题 + 极致工程"项目在回潮**，且它们的文档质量（边界、参数推导、失败记录）普遍高于纯 Agent 项目。

---

### 方法论备忘（本次运行）

- 三榜合并仍是标准流程：daily **14** / weekly **21** / monthly **23**。**daily 连续多期在 8–17 之间波动，单榜永远凑不够 10 条。**
- 本期 daily/weekly/monthly 三榜候选**已被上午 10-05 期的记录占用不多**（本次为 10-06 首次运行，与 10-05 相隔一天，三榜已刷新），因此**无需换语言维度**即取到足够新面孔。语言维度榜（`/trending/<lang>?since=daily`）仍作为补位手段，本期用于补齐 rust / python / typescript 三条（RuView / MiroFish / mailflare / OptMem）。
- `fetch_trending.py` 增加 `--lang` 参数尝试失败（脚本未支持），改用内联 Python 复用同一 `parse_board` 逻辑抓语言榜，效果一致。
- **`releases.atom` 取正文的有效姿势**：`curl` 下载到本地文件后用 `sed -e 's/<[^>]*>//g'` 去标签即可拿到 HTML 实体编码的正文（`&lt;p&gt;`），claude-mem / hyperframes / Aether / esp32 全部成功。**注意**：OptMem 的 atom **只有 `<updated>` 没有 `<entry>`/`<content>`**（新仓库首发 release 尚无正文），artcraft 的正文仅为"See the assets below"——**这两类要改从 README 取信息**。
- GitHub REST API 仍未使用（配额问题）；全部信息来自 `github.com/trending` HTML、`raw.githubusercontent.com/<o>/<r>/HEAD/README.md`、`releases.atom`，无一失败。
- `releases.atom` 的 `<title>` 与 `<entry>` 顺序不保证对应，解析 `entry` 块内的 `title` 更稳（本次用 `sed` 顺序读 title/updated，因 atom 结构规整未出错；若后续出错改用 entry 块内解析）。
