# GitHub AI 趋势日报 · 2026-10-12

> 数据源：github.com/trending 主榜（daily 8 / weekly 12 / monthly 22）+ 语言维度榜 14 个（python / typescript / rust / go / c / c++ / javascript / java / swift / vue / html / cuda / jupyter-notebook，共 174 条去重后 181 个仓库）
> 距上期（10-09）相隔 3 天（跨周末）。**主榜 daily 8 条中 7 条为已推送仓库**（唯一新面孔：bilawalsidhu/gods-eye-view），weekly 12 / monthly 22 中仅 6 条新 → **本期 10 条详细中 9 条来自语言维度榜 / monthly 榜**。
> 星数为抓取时点数值；GitHub trending 的排列顺序不等于增幅排序，本报告只报增幅不声称名次。

---

## 一、榜单速览

| # | 仓库 | 语言 | 总 Star | 增幅 | 来源 | 一句话 |
|---|---|---|---|---|---|---|
| 1 | [bilawalsidhu/gods-eye-view](https://github.com/bilawalsidhu/gods-eye-view) | JS | 51,745 | **+25,143/日** | daily · monthly · javascript | 浏览器里的"间谍卫星"模拟器，数据全是真的公开源 |
| 2 | [alibaba/open-code-review](https://github.com/alibaba/open-code-review) | Go | 46,203 | +24,146/月 | monthly · go | 阿里内部 AI 代码评审，两年大规模验证后开源 |
| 3 | [affaan-m/ECC](https://github.com/affaan-m/ECC) | JS | 277,262 | +22,438/月 | monthly | "Agent Harness 操作系统"：71 agents / 311 skills |
| 4 | [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) | Python | 96,044 | +16,862/月 | monthly | 一句话给 Agent 装上"读全网"的能力 |
| 5 | [JustVugg/colibri](https://github.com/JustVugg/colibri) | C | 41,265 | +13,726/月 | monthly | 纯 C，在 8–16GB 内存机器上跑 744B MoE |
| 6 | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | JS | 105,054 | +11,891/月 | monthly | Addy Osmani 的生产级工程技能包（25 skills） |
| 7 | [farion1231/cc-switch](https://github.com/farion1231/cc-switch) | Rust | 142,831 | +385/日 | rust | 10 个 Agent CLI 的统一控制面 + 本地路由 |
| 8 | [denoland/celld](https://github.com/denoland/celld) | Rust | 5,440 | +90/日 | rust | Deno 官方：自托管分布式 Durable Objects |
| 9 | [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill) | Python | 4,494 | +936/周 | weekly | 把航空业受控语言标准装成 Agent 技能 |
| 10 | [ranxianglei/billion-context](https://github.com/ranxianglei/billion-context) | TS | 913 | +337/周 | weekly | 可逆的分层上下文压缩代理，附论文 |

---

## 二、10 条详细

### 1. bilawalsidhu/gods-eye-view — 公开数据拼出的"上帝视角"，单日增幅榜首

**事件**：前 Google/Bing 工程师 Bilawal Sidhu（Halfpixel）把 YouTube 上累计 5,000 万+ 播放的 **God's Eye View 系列（原 WorldView）** 完整开源。仓库同时出现在 daily / monthly / JavaScript 三个榜，**日增 +25,143，为当日全站最大增幅**，总 51,745 / forks 10,388。今年 8 月曾登顶 GitHub Trending 日榜与周榜。

**核心内容**
- **形态是本地浏览器应用**：CesiumJS + Google Photorealistic 3D Tiles + Vite，**无前端框架**，`npm run doctor` 自检后 `npm run dev` 起在 `localhost:4173`；也可用 Pinokio 一键装（Windows/macOS/Linux）。
- **零 key 起步**：航班应答机（adsb.lol）、船舶、卫星 TLE（CelesTrak）、地震（USGS）、公开摄像头、电台、火箭发射、天气（NOAA/ECMWF）、OSM 上的车牌识别摄像头位置——**全部免注册**。可选的免费 key 层是 AISStream / FIRMS / TomTom / OpenSky / Cesium ion。
- **AI 语音代理**：走 OpenAI Realtime API，**内置 30 个 voice tools**——语音画标注多边形、问任意卫星下次过境时间（rise/peak/set）、按语音对卫星/数据中心/水坝做计数与排序，回答会明说"数据源已过期"或"当前走的是回退源"。
- **数据工程细节可抄**：飞机/船舶图标按**真实航向做逐帧屏幕空间投影**（任何视角都不"打转"）；实时源 15–30s 一次，**渲染滞后一个间隔 + 航位推算插值**；卫星用 SGP4 传播并用 GMST 实时校正，避免逐秒抖动；OpenSky 信用额度调速器 + TomTom 瓦片日预算 + 本地 TLE 缓存。
- **凭据边界**：所有碰私钥的 API（OpenAI / AISStream / OpenSky OAuth / 摄像头帧）**走服务端代理**，含 SSRF 防护、响应体积上限、错误信息脱敏；浏览器只拿到 Google Maps 与 Cesium ion 两个 key。**默认只绑 localhost**；要开 LAN 必须显式 `--host 0.0.0.0`，且 README 明确警告"LAN 可见 = 你的 key 对能访问的人可见"、并把 `GEV_ALLOWED_HOSTS` 作为 Host 头白名单（与 10-08 flowsint 同一手法）。
- **诚实口径**：成本表逐条标"$0 / 免费 key / 计量"；OpenAI 语音会话有**实时花费读数 + $2 警告 + $5 硬上限**；明确声明"app 层限流不是账单上限，先去配供应商配额和预算告警"。

**值得关注的原因**
这是"**开源情报（OSINT）工具平民化**"的一个拐点级样本：把过去属于专业 GEOINT 软件的多源融合（航空 + 海事 + 轨道 + 气象 + 地面摄像头）做成了可在笔记本上跑的网页应用。更值得注意的是它**主动划出伦理红线**——"本项目只建模事件、资产、基础设施与系统；**不做针对特定个人的搜索、人脸识别或人员追踪，越过这条线的 PR 不会被合并**"。在同期世界模型/感知类项目（10-06 RuView 的 WiFi 穿墙感知）不断扩张采集面时，这份"能力清单 + 明确不做清单"的写法值得作为模板。工程上，"滞后一帧 + 插值 + 服务端凭据代理 + Host 白名单 + 花费硬上限"这四件套，是任何"前端直连多源付费 API"的项目都可以直接复用的默认姿势。

---

### 2. alibaba/open-code-review — 阿里把内部 AI 代码评审开源，并给出"确定性 × Agent"混合架构

**事件**：阿里巴巴开源内部官方 AI 代码评审助手 **Open Code Review**（CLI 命令 `ocr`，npm 包 `@alibaba-group/open-code-review`）。Go 榜与 monthly 榜同时上榜，**月增 +24,146**，总 46,203 / forks 3,349，Apache-2.0，OpenSSF Best Practices **Gold** 徽章。README 自述"过去两年服务数万名开发者，发现数百万个代码缺陷"。

**核心内容**
- **明确定位"通用 Agent 做代码评审的三个痛点"**：大 changeset 会**挑文件偷懒**（覆盖不全）、**位置漂移**（报的行号对不上）、**质量不稳**（纯自然语言 Skill 难调试）。根因诊断是"纯语言驱动架构对评审过程缺乏硬约束"。
- **架构 = 确定性工程 × Agent 各司其职**：
  - 工程侧负责**不能出错**的部分——精确文件选择（哪些必评、哪些过滤）、**智能文件打包**（如 `message_en.properties` 与 `message_zh.properties` 捆成一个评审单元，每包跑一个**隔离上下文的子 Agent**，大 changeset 下稳定且天然并发）、**模板引擎驱动的规则匹配**（按文件特征挂规则，替代纯语言提示）、以及独立的**评论定位模块与评论反思模块**。
  - Agent 侧只负责动态决策与动态取上下文——场景化提示词（省 token）+ **从生产数据工具调用轨迹里蒸馏出的专用工具集**（按调用频率分布、单工具重复率、新工具对调用链的影响来裁剪）。
- **基准是可复核的**：**AACR-Bench**——50 个热门开源仓库 / 200 个真实 PR / 10 种语言，80+ 资深工程师交叉标注 **1,505 条 ground-truth 问题**，数据集已发在 Hugging Face（`Alibaba-Aone/aacr-bench`）。结论口径诚实：**Precision 与 F1 显著高于通用 Agent（同底层模型），token 消耗约 1/9，速度更快；但 Recall 更低——这是刻意换取低噪音的取舍**。
- **命令面**：`ocr review`（工作区/分支区间/单 commit）、`ocr scan`（无 diff 的全文件扫描，用于陌生代码库审计）、`ocr session list` + `--resume`（中断续跑）、`--format json --output`（给宿主 Agent 消费）、以及 **`ocr delegate`** 委派模式——OCR 只做文件选择与规则解析，**评审由你自己的编码 Agent 用它的 LLM 完成，无需配 OCR 的 key**。
- 集成面覆盖 Claude Code / Codex / Cursor / Kimi Code / OpenCode / QCA 与通用 skill，CI 侧有 GitHub Actions、GitLab CI、GitFlic CI、Gerrit；另有 Session Viewer 浏览器复盘与 OpenTelemetry 遥测。

**值得关注的原因**
代码评审是 2026 年 Agent 落地最拥挤的赛道（CodeRabbit、Greptile 是 ECC 的赞助商，同榜还有 openai/codex-security），但**这条新闻的独特点是"用工程约束换稳定性，而不是用更强的模型"**：把"必须不出错"的环节从 LLM 手里拿走，只把"动态决策"留给模型。这与 10-07 rtk（把压缩前移到输出进上下文之前）、10-08 ponytail v5（先算影响面再动手）构成同一条方法论——**Agent 系统的可靠性来自把不确定的部分切小，而不是让模型更聪明**。另外两处值得记：① **发布带可复核基准与数据集**（接续 ADR-Bench、SkillSpector 的"先建基线"惯例）；② **主动报告自己更差的指标（Recall）并解释取舍**，是"诚实披露从修正数值升级为修正口径"的又一例。

---

### 3. affaan-m/ECC — 把 Agent Harness 当操作系统来做，277k 星

**事件**：**ECC（Agent Harness Operating System）** 登上 monthly 榜，**月增 +22,438，总 277,262 / forks 41,354**（本次抓取中星数最高的新面孔）。MIT 许可；v2.0.0「The Agent Harness Operating System」于 2026-06 发布。

**核心内容**
- **一句话定位**：`plan → test → implement → review → verify → remember → improve`。README 的原话是"与其在每个提示词里重建这套流程，不如装一次，让它成为你的 Agent 工作方式的一部分"，并给出原则 **"Optimize the context window. Persist everything else."**
- **规模**：**71 个 agents / 311 个 skills / 97 个命令**。agents 覆盖 planner、architect、tdd-guide、code-reviewer、security-reviewer、build-error-resolver、e2e-runner、refactor-cleaner、doc-updater、chief-of-staff、loop-operator、harness-optimizer，以及**按语言分的 reviewer/build-resolver**（C++ / F# / Go / Python / TS / Java / Kotlin / Ruby / Rust / PyTorch / MLE / database / HarmonyOS）。
- **仓库结构即"单一事实源"**：根目录是唯一真源（`agents/`、`skills/`、`commands/`、`rules/`、`hooks/`、`scripts/`），各平台适配器（`.claude-plugin/`、`.codex/`、`.opencode/`、`.cursor/`）只做**打包或映射，不维护独立副本**——与 10-08 skills-manager 的"给状态一个唯一入口"是同一设计意图。
- **跨 harness 能力矩阵**：最佳支持 Claude Code，原生 Codex / Qoder 插件路径，其余（Cursor / OpenCode / Gemini / Zed / GitHub Copilot / Antigravity / Qwen 等）走"能力受限适配器"，README 明确要求**先看 support status matrix 再假设功能对齐**。
- **记忆与学习**：`continuous-learning`（v1 Stop-hook 模式抽取）与 **`continuous-learning-v2`（基于 instinct 的学习 + 置信度打分）**；`iterative-retrieval`（子 Agent 渐进式上下文精炼）；`strategic-compact`（主动压缩建议）。
- **Token 优化写成可抄的配置**：默认 `opus` → 建议 `sonnet`（**约降 60% 成本，覆盖 80%+ 编码任务**）、`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` 从 95 调到 **50**（长会话质量更好）、子 Agent 用 haiku、订阅用户关掉 API 费率估算告警（保留上下文/范围/循环告警）。
- **商业化边界写得很直白**："OSS 永远 MIT，本仓库永远免费；ECC Pro 是给私有仓库用的托管 GitHub App（$19/席/月），赞助与 Pro 订阅养活了'一个人每周为 7 个 harness 发版'这件事"。
- **供应链告警**：README 置顶 Warning 列出**唯一官方来源**（GitHub 仓库、npm 的 `ecc-universal` / `ecc-agentshield`、GitHub App、插件 slug `ecc@ecc`、官网 ecc.tools），并声明"第三方转载与镜像未经审核，可能含恶意代码"。

**值得关注的原因**
"技能包 / 插件市场"这条线本期仍在膨胀，但 ECC 是其中**唯一把"整条开发流程 + 记忆 + 学习 + 安全扫描"打包成一个可安装单元**的项目，且量级（71/311/97）远超同类。它同时暴露了这个赛道的真实商业模式：**开源主体 + 私有仓库托管订阅**，与 10-08 Spotify（把内部门户接进 Claude Code）、本期 cursor/plugins 属于同一波"大厂/个人都在抢 Agent 工作流的入口"。而它置顶的"唯一官方来源"警告，正是 09-28 Snyk 13.4%、09-30 SkillSpector 26.1% 那组技能漏洞基线数据落地后的直接反应——**供应链治理开始写进项目 README 本身**。

---

### 4. Panniantong/Agent-Reach — "一句话给 Agent 装上互联网能力"

**事件**：中文作者 Panniantong 的 **Agent Reach** 上 monthly 榜，**月增 +16,862**，总 96,044 / forks 8,410，MIT，Python 3.10+。README 顶部挂了 Trendshift「GitHub Trending #1 Repository of the Day」徽章。

**核心内容**
- **要解决的问题写得很具体**（逐条对应现实失败场景）：YouTube 拿不到字幕、Twitter API 要付费、Reddit 被 403、小红书必须登录、B 站通用下载工具被风控全拦、搜索要么付费要么质量差、抓回来一堆 HTML 标签没法读。
- **安装与更新都是一句话**：把一段 `raw.githubusercontent.com/.../docs/install.md` 的链接丢给自己的 Agent，它自己装；更新同理。**不查文档**——直接说"帮我配 XXX"，Agent 会引导。
- **核心机制是"多后端路由 + 首选/备选"**：每个平台都是"首选 + 备选"多后端，某个接入方式失效就换下一个，**用户无感**。README 给了真实案例：2026-06 yt-dlp 被 B 站风控封死 → 切到 bili-cli，用户零操作。
- **平台覆盖面**（装好即用 / 配置后解锁）：网页阅读、YouTube 字幕+搜索、任意 RSS、全网语义搜索（MCP 接入免 key）、GitHub（公开读/搜索；配置后可私有仓库与提 Issue/PR）、Twitter/X、B 站（bili-cli 免登录搜索+详情）、Reddit、Facebook、Instagram、小红书、LinkedIn、**Boss 直聘（CDP 链路体检 + 专用真 Chrome 手动登录）**、V2EX、**雪球（行情/搜索/热门帖/热门股排行）**、小宇宙播客（Whisper 转录）。
- **隐私与凭据边界写得很细**：Cookie 只存本地不上传；**Twitter 只接受用户用 Cookie-Editor 手工导出的内容**；**Agent Reach 不替用户执行小红书登录、也不读小红书浏览器 Cookie**，OpenCLI 只使用用户**已经存在且明确控制的** Chrome 会话；`agent-reach configure xhs-cookies` **不会**把 Cookie 注入 OpenCLI/Chrome；Cookie 保存后仅用于 `agent-reach doctor` 检查配置齐全，直接跑上游 twitter 命令仍需在进程环境里显式设 `TWITTER_AUTH_TOKEN` / `TWITTER_CT0`。
- **自带诊断**：`agent-reach doctor` 一条命令报告哪个通、哪个不通、怎么修。成本口径：工具与 API 全免费，唯一可能花钱的是服务器代理（**$1/月**），本地电脑不需要。

**值得关注的原因**
这是本期**工程参考价值最直接**的一条：它把"Agent 联网"这件所有人都要自己踩坑的事，收敛成一个带**自愈式多后端路由 + 配置边界声明 + 诊断命令**的成品。三处设计值得抄：① **"接入方式会换代，你不用操心"**——把易腐层（平台风控/API 变更）封装在项目内，而不是让用户每次升级；② **Cookie 与会话的边界写成可审计的清单**（谁导出、谁注入、哪些命令不注入），与 10-08 flowsint 的部署安全默认值同一水准；③ **针对中文生态的覆盖（小红书/B 站/Boss 直聘/雪球/小宇宙）** 是英文同类项目普遍缺失的，对中文用户是硬需求。赞助商里同时出现腾讯云 Lighthouse 部署 OpenClaw 的入口，说明这类"给 Agent 补能力"的项目已经开始被云厂商当作获客渠道。

---

### 5. JustVugg/colibri — 纯 C，把 744B MoE 跑在 8GB 内存的笔记本上

**事件**：**colibri** 上 monthly 榜，**月增 +13,726**，总 41,265 / forks 4,545。v2.0.0 已在发布页（README 示例输出显示 `colibri v2.0.0 · GLM-5.2 · 744B MoE · int4 · streaming CPU`）。多语言 README（含简体/繁体中文、日、意、印尼）。

**核心内容**
- **原理一句话**：MoE 每个 token 只用模型的一小部分，colibri **把常驻的那部分留在 RAM，把 experts 留在磁盘上按需读**。纯 C，**每个模型族一个文件**，无需 GPU。
- **硬件门槛与实测数据（README 逐条给机型与 tok/s）**：
  - 最低 **8GB RAM**（建议 16GB+），最小模型 **22GB 磁盘**，显卡可选。
  - **GLM-5.2（744B，含 MTP head）**：下载 429GB，**RAM 16/24GB 起**；实测 25GB 笔记本冷启 0.05–0.1 tok/s、128GB Ryzen AI Max+ 395 上 1.83 tok/s、6× RTX 5090 上 9.0–9.2 tok/s。
  - **Kimi K3（2.8T，最大开源模型）**：下载 **1.56TB**，RAM 32/64GB，约 **9.4 秒/token**，expert 读取速度 6.3GB/s。
  - **DeepSeek V4 Flash（284B）**：167GB，16/32GB RAM，CPU-only 0.93 tok/s（Ryzen 7 5800X, 32GB）→ 1.5–1.6 tok/s（RTX 5080）。
  - **Qwen3.6-35B-A3B**：23GB，10/20GB RAM，CPU 6.0 tok/s、集显 Vulkan 9.9、CUDA 30.0 tok/s。
  - 另有 **Inkling（975B）/ MiMo-V2.6 Pro（1.02T）/ GLM-5.3（744B）/ Qwen3.8-Flash-Next（125B）/ OLMoE（7B）/ Qwen3.8-27B（dense，含视觉）** 等，**13 个引擎**（10 个语言模型 + 1 个图像 `Qwen-Image-2.1` + 2–3 个决策模型 Laya / GLiNER2.5-Decide / Clef）。
- **安装是一步**：Windows 双击 `START-HERE.bat`（缺 Python 会主动装）、Linux `./start-here.sh`。安装器会**先探机器**（RAM/空闲磁盘/CPU/GPU）→ **推荐能塞进 RAM 的最强模型**并把"只能从磁盘流式跑"的更大模型列在下面 → 按机器编译引擎（有编译器就本地编译，否则下载预编译；CUDA 装了就编 CUDA，否则 Vulkan）→ **下载带断点续传** → 起服务并打开 dashboard。
- **服务接口是双协议**：同时暴露 `OpenAI base URL: http://127.0.0.1:8000/v1` 与 `Anthropic base URL: http://127.0.0.1:8000`。
- **排错表很实用**：下载中断重跑续传；GPU 构建失败会自己退到 Vulkan 再退到 CPU 并说明原因；WSL 下把模型目录放在 Linux 盘（`/mnt/c` 慢好几倍）。

**值得关注的原因**
"在消费级硬件上跑前沿模型"这条线本期出现两个方向：AirLLM（日榜 +548，**70B 单卡 4GB**，最新已支持 Kimi K3 2.8T 在 **3.72GB VRAM**，且 2026/09 起支持**训练**）走的是"逐层流式 + 量化/不量化"的 Python 路线；**colibri 走的是"纯 C + 每模型族一个引擎文件 + 磁盘流式 experts"**，把依赖面压到接近零。两者共同的含义是：**"跑得动"的门槛正在从显存转移到磁盘带宽与内存**——colibri 明确说"速度由磁盘决定，NVMe 帮助最大"。它也给出了罕见的**逐机型实测表**（含失败与极慢情形，如 25GB 笔记本 0.05 tok/s），这种"把最差情况也写出来"的口径与 10-06 esp32-adblock 自曝 Basic Auth、10-09 mxc 主动 Warning 属于同一类诚实披露。

---

### 6. addyosmani/agent-skills — Addy Osmani 把"资深工程师的工作流"打包成 25 个技能

**事件**：Google Chrome 团队 Addy Osmani 的 **agent-skills** 上 monthly 榜，**月增 +11,891**，总 105,054 / forks 10,968。定位 "Production-grade engineering skills for AI coding agents"。

**核心内容**
- **技能映射到开发全生命周期**，并给出 9 个斜杠命令：`/spec`（Spec before code）→ `/plan`（Small, atomic tasks）→ `/build`（One slice at a time）→ `/test`（Tests are proof）→ `/constraints`（Decide it once, enforce it everywhere）→ `/review`（Improve code health）→ `/webperf`（Measure before you optimize）→ `/code-simplify`（Clarity over cleverness）→ `/ship`（Faster is safer）。
- **`/build auto`**：spec 完成后一次批准即可自主跑完计划与全部任务——README 强调它"移除的是任务**之间**的人为停顿，不是验证"：每个任务仍然测试驱动、单独提交，**遇到失败或高风险步骤会暂停**。
- **技能会按上下文自动激活**：设计 API 触发 `api-and-interface-design`，做 UI 触发 `frontend-ui-engineering`。
- **分发走通用 CLI**：`npx skills add addyosmani/agent-skills` 可装进 **70+ 个 Agent**（Claude Code / Cursor / Codex / Copilot / Cline…），也支持 `--list` 浏览与单技能安装；Claude Code 另有 marketplace 与 `--plugin-dir` 路径。
- **主动公开自身缺陷**：README 用引用块说明"**单独安装某个技能时，`npx` 只拷贝 `skills/<name>/`，不带仓库级的 `references/`**，技能仍可用但共享 checklist 路径会失效"，并给出三种绕法与 issue 编号（#361）。
- **安装坑也写清楚**：marketplace 走 SSH 克隆，没配 SSH key 会失败；Windows/macOS 上 `/plugin install` 报 `Permission denied (publickey)` 时，推荐一次性 `git config --global url."https://github.com/".insteadOf git@github.com:`。
- 其余按 harness 分档：Cursor 要求把 workflow skills 放 `.cursor/skills/`、策略放 `.cursor/rules/*.mdc`，并明确"**不要把完整技能粘进 rules**"。

**值得关注的原因**
与 ECC 的"大而全"相比，addyosmani/agent-skills 的价值在于**"少而硬"**：25 个技能全部对应有明确判据的工程动作（spec / test / review / webperf / ship），且每条都给出"关键原则"一句话，可直接当团队规范。它同时展示了当前技能分发的**事实标准正在形成**——`npx skills add`（vercel-labs/skills CLI）已被多个项目采用（本期 taste-skill 10-09、asd-ste100、nao 都用同一入口）。最后，**主动披露"单装技能会丢共享引用"这种可复现的移植性缺口**，比声称"完美兼容 70+ Agent"更有价值。

---

### 7. farion1231/cc-switch — 10 个 Agent CLI 的统一控制面，142k 星

**事件**：**CC Switch** 上 rust 榜，**日增 +385，总 142,831 / forks 9,515**（Tauri 2 桌面应用）。副标题已扩到 "Claude Code, Claude Desktop, Codex, Gemini CLI, Grok Build, OpenCode, OpenClaw, Hermes Agent, Pi & MiniMax Code"。官网 ccswitch.io（README 明确"唯一官网"，其余为仿冒）。

**核心内容**
- **一键换供应商，不再手改配置**：**90+ 供应商预设**（可按名称含中文、按域名搜索，同厂商不同套餐/区域合并成一行）；切换时**只替换 endpoint / key / model 等连接信息**，你自己加的插件、hooks、MCP、设置与注释**原样保留**，且首次改写前自动备份配置文件；编辑器会预览改写后的配置文件长什么样。
- **本地路由 + 故障转移**（本期最有价值的部分）：
  - **API 格式互转**：在 Anthropic Messages / OpenAI Chat Completions / OpenAI Responses / Gemini Native 之间转换——Claude Code 与 Claude Desktop 可以用 OpenAI 或 Gemini 格式的供应商，Codex 与 Grok Build 可以用 Chat Completions 或 Anthropic Messages 的供应商。
  - **按工具独立开关路由模式**；路由模式下换供应商**对后续请求立即生效**；退出 CC Switch 时**先把直连配置写回**。
  - **自动故障转移**：每个工具配一条 failover 队列，请求失败自动切下一个供应商，**带熔断器与供应商健康监控**；另有"整流器"自动修复某些上游处理不了的请求（如 thinking 签名、不支持图片时回退）。
- **聚合模式**：把多个供应商的模型汇进一个模型列表，在客户端模型选择器里直接选，请求按所选模型路由到对应供应商（README 说明聚合**不提供故障转移**；Claude Code 需 2.1.243+；会话内换模型要重建 prompt cache，**首轮会更贵**）。
- **统一 MCP / Prompts / Skills 面板**：一处管理所有 MCP server 并选择同步到哪些工具；Prompts 库按工具写入 `CLAUDE.md` / `AGENTS.md` / `GEMINI.md`（**写入前把文件原内容存回库**）；Skills 可搜 skills.sh、从 GitHub 仓库或 ZIP 一键装、检查并一键全量更新，**同步方式可选软链/拷贝**。
- **用量与成本**：不启用本地路由也能用——默认扫描各工具本地会话日志，按供应商与模型统计请求数、token、缓存命中率、输出速度与花费，带趋势图、全年热力图与逐请求日志；供应商卡片与托盘显示剩余额度与重置倒计时（如 "5h 94% left"），覆盖官方订阅配额、Coding Plan 5 小时/周/月配额与账户余额（DeepSeek / OpenRouter / SiliconFlow 等），也支持自定义定价或从 models.dev 导入。
- **会话管理器**：把各工具会话日志解析成结构化内容（文本/thinking/工具调用/工具结果/图片分列），每轮工作折叠成一行摘要（**多少步、改了多少文件、失败几次**，失败标红），右侧有会话大纲，支持会话内搜索、Markdown 导出、复制单轮或整段，以及复制 resume 命令续聊。
- **跨设备同步**：WebDAV（坚果云/Nextcloud/群晖）或 S3 兼容存储（AWS S3 / Cloudflare R2 / 阿里 OSS / 腾讯 COS）。
- **一处风险自陈**：Accounts（Beta）支持把多个 GitHub Copilot / ChatGPT / xAI 订阅当作供应商使用，但 README 明确写"**在官方客户端之外使用订阅可能违反厂商服务条款，风险自负**"。

**值得关注的原因**
本期"控制面"主题的最强样本。当一个人同时用 Claude Code、Codex、Gemini CLI、OpenCode、OpenClaw 等 10 个 CLI 时，配置（供应商、MCP、skills、prompts）会散落在 10 套互不兼容的 JSON/TOML/YAML 里，cc-switch 的做法是**在本地插一层代理，把"格式差异 + 供应商差异 + 额度差异"全部吸收**。这与 10-09 docker-agent（Agent 变 OCI 制品）、10-08 skills-manager（技能状态唯一入口）指向同一判断：**Agent 生态越碎片化，"统一控制面"就越值钱**。同时它示范了两种高价值工程动作——**换供应商只动连接字段、其余配置原样保留**（把"最小完整变更"原则用在配置文件上），以及**退出时把直连配置写回**（避免"代理成了单点故障"这类控制面失效问题，正是"控制平面失效常常无声"的正面解法）。

---

### 8. denoland/celld — Deno 官方：把 Cloudflare Durable Objects 搬到自己的机器上

**事件**：Deno 团队开源 **celld**，上 rust 榜（**+90**，总 5,440 / forks 295），官网 celld.dev，二进制经 `gh attestation verify` 可校验来源。定位一句话：**Self-hosted, distributed Durable Objects**。

**核心内容**
- **一句话能力**：一个开源 daemon，**在你自己的机器上跑 Cloudflare Workers 应用**——Workers、Durable Objects、KV、Queues、D1、R2、Workflows、Cron Triggers、静态资源，**直接用你已有的 `wrangler.json` 部署**。
- **架构（"每个对象是一个 cell"）**：
  - 一个节点 = 一个 `celld` 进程，每台机器跑一个，**每个节点内嵌 V8 执行 Wrangler 打包产物**。
  - 共享同一个 bucket 的节点构成一个 **fleet**，bucket 里存部署、cell 状态与小体量所有权记录。**用一次条件写（conditional bucket write）取得某个 cell 的所有权**，因此同一时刻只有一个节点拥有它——**不需要成员协议、故障检测器或共识服务**。节点间用签名 HTTP 做路由与复制日志传输。
  - **持久性证明**：每个已提交的 SQLite 写入按 **LTX 复制格式**捕获；单节点靠把数据传到 bucket 证明持久（**因此单节点写入慢得多**）；两个及以上节点时 owner 把数据发给 1–2 个其他节点，**对方落盘即算持久**，之后再由 celld 上传 bucket。接管前会从原 owner 恢复未关闭的日志，所以**长期状态在 bucket 里，节点本身可替换**。
  - **成本模型**：不活跃的 cell 几乎零成本。
- **覆盖面（每行都链到一个可直接部署的示例）**：Workers（fetch handler / service binding / JS RPC / Node 兼容）、Durable Objects（SQLite 存储、alarms、休眠 WebSocket）、KV（list/metadata/expiration/bulk import）、Queues（生产者/批量消费者/重试/死信）、D1（批量、迁移）、R2（读写、list、分片上传）、Workflows（持久步骤、sleep、事件、暂停重启）、Cron（fleet 内每个时刻只跑一次）、静态资源、Dynamic Workers（运行时加载代码 + Tail Worker 可观测）、**Containers（实验性，`@cloudflare/containers`）**、**Sandboxes（Cloudflare Sandbox SDK，每个沙箱一个容器）**。
- **明确的适用范围**：需要 Cloudflare 网络、GPU 或浏览器农场的产品**不在范围内**；`docs/cloudflare-compat.md` **逐项列出上面的服务各自的缺口**。
- 安装：`curl -fsSL https://celld.dev/install.sh | sh`（版本目录 + 单个 symlink 指向当前版本，卸载即删 symlink 与 releases）；也有 ghcr.io 的 Linux x86-64/ARM64 镜像，长期状态交给 S3/GCS/Azure Blob。

**值得关注的原因**
这是一条**基础设施层面的路线级事件**：过去"边缘运行时"是只能租不能自有的东西，celld 把它变成"一个进程 + 你自己的对象存储桶"。技术上最值得记的是它的**去共识设计**——用"bucket 上的条件写"代替选主，用"写入被复制到 N 个节点的磁盘"代替 quorum 日志，用"长期状态放对象存储 + 节点可替换"代替持久化节点。这与 10-08 kubernetes-sigs/agent-sandbox、10-09 microsoft/mxc 一起，说明**"把云厂商能力搬回自托管"正在成为独立赛道**；而它与本期 agent-substrate（Go，K8s 上跑百万级 Agent 沙箱）、flowsint 这类自托管项目的共同点都是：**先把"数据落在你自己的存储里"作为默认，再谈功能**。对自托管 AI 服务的用户（Open WebUI / ComfyUI 那类常驻服务）来说，celld 提供了一条"用 Workers 生态写业务逻辑、但状态归自己"的实际路径。

---

### 9. danyuchn/asd-ste100-skill — 把航空业"受控语言"标准装成 Agent 技能

**事件**：**ASD-STE100 Skill** 上 weekly 榜，**周增 +936**，总 4,494 / forks 259，MIT。作者 danyuchn。

**核心内容**
- **它是什么**：把 **ASD-STE100 Simplified Technical English（STE）**——航空与国防工业为了防止飞机维修指令被误读而建立的受控语言标准——重定向用途，**用来重写"机器要读的英文"**：Agent 之间的消息、工具/函数描述、错误信息、system prompt、跨 Agent 指令。
- **为什么对 Agent 有效（论证很干净）**：STE 存在的原因是"误读一条航空指令可能死人，而读者常常不是英语母语者、且**没有作者可以打电话确认**"。一个 LLM Agent 解析另一个 Agent 的输出时处境**惊人地相似**：没有回信道、无法问"你是指 X 还是 Y"。**防止机械师误读扭矩规格的规则，同样能防止下游 Agent 误读工具描述。**
- **两种模式**：**Strict**（流程、错误信息、工具描述——遵守固定词汇表）与 **STE-flavored**（README、PR 描述、说明性散文——保留句子纪律但不锁词汇）。
- **工作方式**：逐句标出违规（歧义用词、完成时/复杂时态、actor 不明的被动语态、一句多指令、超大名词簇、省略词、超长句、短语动词、名词化、分号、堆叠的模糊限定、营销形容词）→ 逐句改写，**且不得丢弃原句中的任何事实、条件或范围限定**；如果更短的写法会丢精度，就保留长写法并**标注这个取舍**而不是悄悄简化 → **只输出改写后的文本**（无前言、无模式说明、无变更摘要），故意未简化时附一行 `Kept as-is:`。
- **自曝边界（本期最诚实的一段）**：
  - 结构规则是机械可指的（能指出具体词或标点），**依赖 ASD 官方词典的规则只标为"建议"而非强制**，需要品味的一律交给人。
  - **linter 只检查结构模式，不做原文与改写文的比对、不验证要求强度是否保持、也不证明语义被保留**——"零违规"只意味着配置的结构检查没发现问题。
  - 具体覆盖：分号、一小列软短语动词（spin up / reach out / dive into / kick off / circle back / touch base）、名词化、营销形容词、被动语态、完成时（含不规则分词）、长句、同义词轮换、列表项里的悬空连词；**不检查名词簇长度（需要词性标注）**、**不认识列表外的短语动词（所以 "take off the panel" 会通过）**、**从不标记模糊限定或情态**。
  - **不复制 ASD 官方约 900 词的批准词典**（Issue 9 只允许在获得 ASD 书面授权或属于八类机构时复制，本项目都不属于），只应用底层原则。
  - **本仓库自己的散文也过不了自己的 linter**（规则表引用了被禁止的模式，有些句子太长）——README 直接给出复现命令 `python scripts/ste-lint.py --baseline 41 SKILL.md` 并说"把发现当作示例而不是缺陷"。
  - 最后一句限制写得很到位：**"它修正的是文本的形式，不是内容。一段什么也没说的文字，改完会变得又短又干净，而且依然是空的。"**
- 安装走 `npx skills add danyuchn/asd-ste100-skill`（匿名安装遥测，`DISABLE_TELEMETRY=1` 可关）。

**值得关注的原因**
这是本期**唯一一个"新类别"**：此前所有 Agent 技能都在扩**能力**（写代码、做 PPT、审代码、抓数据），这一条在**收窄语言本身**——因为 Agent 与 Agent 之间没有澄清回路，歧义就是 bug。它把"提示词工程"从"怎么让模型听懂"翻转成"**怎么让输出不可被误读**"，而且用的是一个有 30+ 年工业史、有编号（Issue 9）、有授权边界的正式标准。工程上它给出了一个**可抄的模式**：把规则分成"机械可判定（强制执行）/ 依赖外部词典（标为建议）/ 需要品味（交给人）"三档，并且**明说 linter 不证明语义等价**——这与 10-08 open-ontologies 的"证书可独立复验"、10-07 rea 的"unknown 不算通过"是同一方向的严谨性。

---

### 10. ranxianglei/billion-context — 可逆的分层上下文压缩代理（附论文与长期实证）

**事件**：**billion-context** 上 weekly 榜，**周增 +337**，总 913 / forks 83。npm 包 `billion-context`，CLI 命令 `bili`（`bili-proxy` 为别名）。README 顶部挂了一篇**开源在仓库内（MIT）的论文**。

**核心内容**
- **一句话定位**："billion-context 位于**任意** Agent 与它的模型 API 之间，用 acp-kernel 压缩重写 Anthropic/OpenAI 流"。**压缩的时机与内容由模型自己决定**，不是硬截断阈值。目标是"小上下文窗口（100K 就够）+ 5× fewer tokens + 单会话跑数月（billions of tokens）"。
- **论文给出的规模（README 自述）**：4.5 个月、三台主机、**174,327 次模型调用、累计输入 18.76B tokens（跨主机约 24.7B）**，在 204,800 token 模型上**零窗口违规**，最长会话 8,584–12,049 次调用。论文是"living document"，任何人可改，欢迎 PR。
- **与宿主内置摘要器的差别**：这里压缩是**增量、可逆、且对 prefix cache 友好**的——摘要按小范围写入、可按需解压、**cache 前缀保持完整**。README 给出健康指标：**健康会话保持 95–97% 的 prefix-cache 命中率，压缩本身开销 ≤2%**；持续偏低时用 `/acp` 或 `/acp-cache` 归因，常见原因按顺序是：上游 cache TTL 过期 · 切换模型 · bili 的 bug（请上报）· 其他。
- **注入四个上下文管理工具**，由模型自己按需调用，`compress` 由代理在服务端执行，因此被折叠的区间在历史里一直保持"已摘要"直到恢复：`compress`（把一段消息折成详细摘要）、`decompress`（需要精确细节时还原）、`search_context`（在摘要与可见消息上做关键词搜索）、`acp_status`（上下文用量总览 + 哪些区间仍可压缩）。
- **接入三选一**：① **原生插件** `bili plugin install <client>`（bili 成为客户端内的插件）；② **启动器** `bili <client>`（代理与客户端一起起，**不碰真实配置文件**）；③ **改 baseURL**，加 `/bili/` 前缀（最通用）。客户端覆盖极广：pi / omp / opencode / dsh / kimi / hermes / zcode 原生插件，以及 claude / codex / gemini / qwen / iflow / aider / copilot / amp / goose / trae / qoder / codebuddy / mcode / jcode / antigravity 等启动器。
- **会话身份设计（本期技术上最细的一段）**：
  - 压缩状态**以客户端自己提供的会话值原样为键**——不做哈希，也**不掺入协议/上游/API key 维度**（这些会在对话中途变化，导致用户还在说话时状态被孤立，#280/#286）。
  - 取值优先级"先到先得"：插件头 `x-bili-plugin-conversation`（必须同时带 `x-bili-plugin` 标记）→ 各客户端专用头（`x-claude-code-session-id` / `x-grok-session-id` / `x-mavis-session-id`）→ 通用头（`x-session-affinity` / `x-acp-session` / `x-session-id` / `x-opencode-session` / `session-id`）→ body 字段（Responses 线上的 `session_id` / `metadata.session_id`，以及 `prompt_cache_key` 优先于内容指纹回退）。会话 id **从不发给上游**。
  - **无头客户端的"匿名前缀亲和"**（#309）：没有会话信号时，从**重放的历史本身**解析会话——只有当请求历史**从位置 0 起逐字节重现**某会话的消息链时才重新附着；否则分配自己的确定性 `pfa-…` 会话。后果写得很清楚：**恢复的对话能重新附着自己的会话（即使代理重启过，#499）；用相同开场白的新任务不会继承另一段对话的压缩块**；完全没有可用信号时返回显式 400 而不是静默串台。
  - **派生子会话继承父会话的压缩上下文**（#1333/#1362）：子会话出生时上报血缘（`parentConversationId`），代理记录只读的 `derivedFrom` 链接，`decompress`/`search_context` 沿父链回退查找（防环、深度上限 8）；**不向子会话拷贝任何东西，也不修改父会话**。
- **可操作的环境细节**：`bili start` 占用 8787，各 lane 自动生成的实例在独立的 `18787` 起自管区（冲突 +1 且每个 lane 记住漂移）；**Windows 上要把 `%USERPROFILE%\.local\share\billion-context\` 加入杀软排除项**（代理每轮重写状态文件，Defender/索引器/OneDrive 会锁文件导致 EPERM）；会话文件清理**默认关闭**（`BILI_SESSION_GC=1` 才开，且必须同时满足"超过 7 天"与"从未压缩过且最新请求体 ≤1M tokens"才删，每次删除审计留痕）。
- **许可与状态（两个必须点出的地方）**：MIT **外加一条附加条款**——任何用户能看见或交互的产品/服务若使用本软件，**必须在首页、文档或 About/Credits 页声明使用了 billion-context 并链回本仓库**。而 `Status` 一节写的是：**"Early. 协议处理与压缩针对 mock 测试（500+ 通过）。真实模型集成测试是下一个里程碑。会有粗糙的地方。"**

**值得关注的原因**
上下文成本这条线本期已有 rtk（10-07，**输出进上下文前**压缩 bash 输出）、claude-mem（10-09，**读取的边界**）、context-mode，billion-context 补的是**第三层：已经进上下文的对话本身**，而且给出了两个此前没人认真处理的约束——**压缩必须可逆**（`decompress`）和**必须不破坏 prefix cache**（95–97% 命中率指标）。它的会话身份设计（不掺可变维度、无头客户端用逐字节前缀亲和、相同开场白不继承、无信号返回 400 而非静默串台）是"**跨轮状态保真是最大 bug 来源**"这条反复验证的教训的正面工程答案，值得单独存档。**但要按口径读**：README 顶部那组 174,327 次调用 / 18.76B tokens 的数据来自论文所述的长期实证（基于 acp-kernel 方案），而 `bili` 这个代理自身仍处于"mock 测试通过、真实模型集成待做"的早期状态——**两者不是同一成熟度**，采用前应先在自己的会话上验证 prefix-cache 命中率与压缩质量。

---

## 三、其他趋势速览

**大厂 / 官方项目**
- [NationalSecurityAgency/ghidra](https://github.com/NationalSecurityAgency/ghidra)（Java，83,506，**月 +8,451**，monthly + java 榜）— NSA 逆向工程框架热度回温，与本期 ghidra-mcp（10-08）、rea（10-07/10-11）构成"逆向工程 MCP 化"的底座层。
- [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins)（Python，29,128，**月 +5,173**）— Anthropic 官方开源 **11 个岗位插件**（productivity / sales / customer-support / product-management / marketing / legal / finance / data / enterprise-search / bio-research / cowork-plugin-management），面向 **Claude Cowork**（兼容 Claude Code）；每个插件 = skills + connectors（MCP）+ 斜杠命令 + 子 Agent，**全部是 markdown 与 JSON，无代码、无基础设施、无构建步骤**；设计意图明确写着"真正的价值在于把它改成你们公司的工具、术语与流程"。
- [anthropics/financial-services](https://github.com/anthropics/financial-services)（Python，39,400，**月 +4,698**）— Anthropic 官方**金融服务参考实现**：投行/股票研究/私募/财富管理四类工作流，**同一份源可两路部署**（Cowork 插件 或 Claude Managed Agents API `/v1/agents`）；含 10 个命名 Agent（Pitch / Meeting Prep / Market Researcher / Earnings Reviewer / Model Builder / Valuation Reviewer / GL Reconciler / Month-End Closer / Statement Auditor / KYC Screener）；**合规边界写在最前面**——不构成投资/法律/税务建议，只起草分析产物，**不做投资推荐、不执行交易、不绑风险、不过账、不批准准入，每份输出都需人类签核**；Partner-built 里有 LSEG 与 S&P Global。
- [cursor/plugins](https://github.com/cursor/plugins)（TS，10,907，**周 +3,610**）— Cursor 官方插件市场：**100+ 插件**，含官方自研（teaching / thermos 分支审查 / create-plugin / ralph-loop / pr-review-canvas / docs-canvas / cursor-sdk / orchestrate / advisor）、社区作者插件（continual-learning / cursor-team-kit / pstack / dyl-stack / cli-for-agent）与**大量第三方集成**（Gmail / Google 全家桶 / Salesforce / GitHub / Playwright / HubSpot / Zoom / X / Stripe 系 / Robinhood / Coinbase / Interactive Brokers / S&P Global / Workday / QuickBooks…）。清单标注 author 与 category，仓库是多插件 marketplace（根 `.cursor-plugin/marketplace.json`，每个插件带 `.cursor-plugin/plugin.json` + `skills/` + `rules/` + `mcp.json`）。

**Agent 运行时 / 沙箱**
- [agent-substrate/substrate](https://github.com/agent-substrate/substrate)（Go，4,872，**月 +3,014**，Apache-2.0）— "**secure-by-default 的 Agent 执行运行时，在 Kubernetes 上跑百万级沙箱**"：宣称比标准容器运行时**密度高 10 倍**、**resume < 500ms**、**每秒 500+ 次 suspend/resume 激活**，原生零信任内核与网络隔离，支持 **microVM 与 gVisor** 等多种沙箱技术并统一生命周期；核心机制是"**把大量 actor（Agent 应用）映射到少量就绪 worker**"，利用 Agent 类应用大部分时间空闲这一事实做重度多路复用。（注意：与 10-08 agent-sandbox、10-09 mxc 同属"Agent 沙箱"主题，本期仅作速览。）

**中文生态 / 内容生产**
- [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)（Python，60,396，**日 +1,104**）— AI 从任意文档生成**原生 PowerPoint**；核心主张"**可编辑已是底线，真正的差别是你能拿到多少 PowerPoint 本身**"——原生形状与连接线（带可调手柄）、数据驱动的图表与表格、完整文本/图片/填充/效果模型、经模板路线可拿到真实 `p:sldMaster` / `p:sldLayout` 继承；提供 PowerPoint ↔ SVG 映射指南（**逐特性记录差距，SmartArt 是刻意不做而非缺口**）；三条承诺：成本透明（只花模型费）、**数据留在本地**、不锁平台；明说"**这是工具不是许愿池**：harness + model = agent，工作流只占一半，模型决定上限"（推荐 Kimi K3 或 Claude + ~1M 上下文 + 图像生成）。
- [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search)（Python，46,135，**日 +504**）— 基于 Claude Code 的求职框架：fork 后填 profile，让 Claude 评估职位、定制 CV、写求职信、准备面试；README 明确"**与 Anthropic 无关联**"并声明"**没有任何附属加密货币、代币或付费赞助计划，声称有的一律视为诈骗**"。
- [lyogavin/airllm](https://github.com/lyogavin/airllm)（Jupyter，36,521，**日 +548**）— 老项目持续回温；**2026/09 起支持训练**（逐层流式加载冻结权重、适配器留 GPU：Qwen3.8-Flash-Next 125B 在 **6GB** 下训练，Qwen3.8-27B 在 ~2GB）；推理侧 **Kimi K3（2.8T）3.72GB VRAM**（RTX 6000 Ada 实测）、DeepSeek-V3（671B）~12GB、Qwen3-235B ~3GB。
- [chthollyphile/folia-major](https://github.com/chthollyphile/folia-major)（TS，5,002，**日 +555**）— 专注歌词动画的本地/Navidrome/多平台在线音乐播放器。
- [microsoft/TRELLIS.2](https://github.com/microsoft/TRELLIS.2)（Python，11,857，+95）— 微软 3D 生成：原生且紧凑的结构化 latent。
- [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design)（HTML，24,837，+56）与 [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill)（HTML，已推送）— 中文 HTML 原生设计/幻灯片技能。
- [datawhalechina/Agent-Learning-Hub](https://github.com/datawhalechina/Agent-Learning-Hub)（HTML，8,591，+35）— 中文 AI Agent 学习路线与资料库。

**工具与基础设施**
- [multica-ai/multica](https://github.com/multica-ai/multica)（Go，52,486，+70）— "**会出现在看板上的 Agent**"：把工作指派给 AI 编码 Agent，像指派给同事一样——它接单、报进度、提阻塞、交回待审；可自托管、兼容你已有的 Agent CLI、不锁定。
- [Wei-Shaw/sub2api](https://github.com/Wei-Shaw/sub2api)（Go，43,729，+75）与 [QuantumNous/new-api](https://github.com/QuantumNous/new-api)（Go，49,727，+71）— 中文 API 中转/聚合层（前者把 Claude/OpenAI/Gemini/Grok 订阅统一接入并支持"拼车共享"，后者是统一模型聚合分发中枢）。与 cc-switch 构成"多供应商接入"的三种做法：桌面端代理 / 服务端中转 / 网关聚合。
- [larksuite/cli](https://github.com/larksuite/cli)（Go，17,624，+16）— 飞书官方 CLI（由 larksuite 团队维护）。
- [microsoft/BitNet](https://github.com/microsoft/BitNet)（C++，40,703，+195）— 微软 1-bit LLM 官方推理框架，回温。
- [getnao/nao](https://github.com/getnao/nao)（TS，1,908，+20，Apache-2.0，YC 公司）— 开源分析 Agent 框架：`nao-core` CLI 建"文件系统式上下文"（数据/元数据/建模/规则/MCP 都可塞）→ `nao sync` → `nao chat`；**自带评测**（`tests/` 里用 yaml 写问题与期望 SQL，`nao test` 跑分、`nao test server` 看面板）、上下文可版本化并追踪 Agent 表现随时间变化；可自托管 + 自带 LLM key。
- [CopilotKit/OpenIntelligentUI](https://github.com/CopilotKit/OpenIntelligentUI)（TS，2,673，+278，MIT）— 基于 CopilotKit + **AG-UI** 的开源生成式 UI：把提问变成可交互的解释、对比与可用工具（3D 讲解、对比、计算器、路线图）。
- [xtool-org/xtool](https://github.com/xtool-org/xtool)（Swift，7,023，+427）— 跨平台 Xcode 替代：在 Linux/WSL/macOS 上用 SwiftPM 构建并签名安装 iOS 应用，可编程访问 Apple Developer Services（`setup` / `auth` / `sdk` / `new` / `dev` / `ds` / `devices` / `install` / `launch`），并提供 `XKit` SwiftPM 库。
- [EricTechPro/super-board](https://github.com/EricTechPro/super-board)（HTML，183，+31，v3.1.1）— "加任务、走开、拿到带证据的已合并 PR"：8 个 skills（5 个你敲、3 个看板自己跑）+ 9 个命令 + **6 个 guard hook**。
- [microsoft/TRELLIS.2](https://github.com/microsoft/TRELLIS.2)、[Project-HAMi/HAMi](https://github.com/Project-HAMi/HAMi)（Go，4,693，+36，K8s 上异构 GPU 共享）、[optiscaler/OptiScaler](https://github.com/optiscaler/OptiScaler)（C++，+36，跨 GPU 的 DLSS/FSR/XeSS 桥接与帧生成）、[safijari/openpuck](https://github.com/safijari/openpuck)（C++，+15，NRF52840 Pro Micro 上仿 Steam Controller 的开源固件）、[ran-j/PS2Recomp](https://github.com/ran-j/PS2Recomp)（C++，+11，PS2 静态重编译为原生 PC 程序）、[MiaAI-Lab/sparkDash](https://github.com/MiaAI-Lab/sparkDash)（JS，+21，多 DGX Spark 监控面板）、[repowise-dev/repowise](https://github.com/repowise-dev/repowise)（Python，+67，代码库健康评分与自动修复建议）。
- [tarwin/tinyjsapp](https://github.com/tarwin/tinyjsapp)（C，912，**日 +142**）— 用 JS 写原生应用（前后端），约 5MB。

**已推送仓库的最新版本（本期无重大新事件，仅列动态）**
- **morluto/rea v6.4.0**（10-11）— 新增 **Android 设备检查/拆分包获取/日志/截图/文件传输/显式应用生命周期（走 ADB）+ Apktool 解 manifest 与本地化字符串**；JEB 支持（通过调用方启动的本地 JEB MCP server 浏览工程单元并反编译选中项）；大分析场景可不加载全部载荷就发现保留的 Evidence。
- **mvschwarz/openrig v0.6.9**（10-11）— Slack 决策的 typed answer 会保留、Slack 状态显示待重试的入站记录、内核从启动失败恢复后正确显示 ready、跨主机发送与长等待不再误报失败、停止投递的 Slack 连接会被捕获并替换；12 项变更中 3 项来自外部贡献者（0.6.8 的 21 项中 12 项来自 9 位外部贡献者）。**升级后必须重启 daemon。**
- **heygen-com/hyperframes v0.8.149**（10-11）— 应用可直接 `import { transcribe, removeBackground }`；v0.8.147 起渲染卡住会说明卡在 Chrome 的哪一步并给处置建议。
- **earthtojake/text-to-cad v0.7.21**（10-11）— 修 STEP 尾部崩溃、首次快照浏览器竞态、Windows worker 控制台窗口。
- **tashfeenahmed/freellmapi v0.13.9**（10-11）— 已退役模型不再进路由、幂等重试收紧、修 CLI 默认端口、加俄语 README；v0.13.7 起加 rerank 与 moderation 端点、自定义端点组、路由可靠性下限。
- **Alishahryar1/free-claude-code v6.13.6**（10-11）、**anthropics/claude-code v2.1.296**（10-09）、**tester-army/e2e** `@e2e-dev/web@0.14.0` / `smol@0.1.0` / `mobile@0.11.0`（10-09）、**vectorize-io/hindsight v0.10.3**（10-08）、**DietrichGebert/ponytail v5.1.0**（10-08）、**thedotmack/claude-mem v13.35.0**（10-09）、**paperclipai/paperclip** canary/nightly `2026.1011.*`。
- 长期无新版：**Tencent/WeKnora v0.8.2**（09-24）、**TencentCloud/Octop v1.0.2b6**（10-06）、**debpalash/VoiceStudio v0.5.6**（09-23）、**storytold/artcraft v0.41.0**（09-26）、**mksglu/context-mode v1.0.169**（06-29）。

---

## 四、当日主线判断

1. **"公开数据 + 本地运行"成为情报类应用的新默认**。gods-eye-view 用 8 个免 key 公开源 + 服务端凭据代理 + localhost 绑定 + $5 花费硬上限，把"看起来像禁区"的能力做成可审计的本地应用；flowsint（10-08）、Agent-Reach（本期）在同一姿势上。配套的是**主动划出"不做清单"**（不查人、不人脸识别、不追踪个人）。
2. **Agent 生态的竞争重心从"给能力"转向"统一控制面"**。同一天四条各自解决一部分：cc-switch（桌面代理统一 10 个 CLI 的供应商/MCP/skills/额度）、open-code-review（用确定性工程约束评审流程）、ECC（把整条开发流程 + 记忆 + 学习打包）、agent-skills（把团队规范固化成 25 个技能）。共同判断是：**碎片化越深，"唯一入口"越值钱**。
3. **上下文成本进入第三层：压缩"已进上下文的对话本身"**。rtk（输出进上下文前）→ claude-mem（读取边界）→ **billion-context（已消费的对话，且必须可逆 + 不破坏 prefix cache，健康线 95–97% 命中率）**。三条线共同否定了"硬截断"这一默认做法。
4. **"跑得动"的门槛从显存搬到磁盘带宽**。colibri（纯 C，744B 需 16–24GB RAM + 429GB 磁盘，速度由磁盘决定）与 airllm（Kimi K3 2.8T 在 3.72GB VRAM）是同一趋势的两条实现路径；代价是 tok/s 掉到个位数甚至 0.1 级——**"能跑"和"能用"之间的差距被明码标价写进 README**。
5. **诚实披露继续升级：从"修正数值"到"修正能力边界"**。本期典型：open-code-review 主动报自己更低的 Recall 并解释取舍；asd-ste100 用整段说明"linter 不证明语义等价、不覆盖列表外短语动词、本仓库自己都过不了自己的 lint"；colibri 把 0.05 tok/s 的最差情况写进表；billion-context 在论文级数据旁标注"代理本身仍是 early、mock 测试通过、真实模型集成待做"。
6. **"受控语言"成为 Agent 输出的新约束层**（asd-ste100）。当 Agent 之间没有澄清回路时，歧义就是 bug；把一个有编号、有授权边界的工业标准（ASD-STE100）装成技能，是提示词工程的反向解法。
7. **云能力"可自托管化"继续推进**（celld：把 Durable Objects 变成"一个进程 + 你的对象存储桶"，用条件写代替共识）。与 agent-sandbox、mxc、substrate 合起来看，"把云厂商的运行时/隔离能力搬回自己机器"已是独立赛道。
8. **厂商官方插件市场仍在扩容，但重心从"给工具"移到"接已有系统"**：anthropics 的 11 个岗位插件 + 金融服务参考实现（明确"只起草、需人类签核、不做投资建议"）、Cursor 的 100+ 插件（大量第三方 SaaS 集成）。**合规与免责声明被写进 README 首屏**。
9. **技能分发的事实标准正在收敛到 `npx skills add`**（addyosmani/agent-skills、asd-ste100-skill、taste-skill、nao 均采用），并配 `--list` 预览、单技能安装与更新命令。
10. **非 Agent 项目约 4/10**，但"具体问题 + 极致工程"的比例在上升（celld 的去共识设计、colibri 的磁盘流式引擎、asd-ste100 的三档规则、billion-context 的会话身份设计）。

---

*本期新增筛选口径：语言维度榜已固定为并列第一数据源（本期 14 个榜，含 jupyter-notebook 与 cuda 两个低增幅榜）。主榜头部固化 + 跨周末三天，daily 榜仅 1 条新面孔，9/10 详细条目来自语言榜与 monthly 榜。*
