# GitHub 趋势日报 · 2026-09-28（当日第二次运行 · 月度榜特辑）

> **本期与当日 11:24 那期的关系**：今日 daily 榜 **9 条与上午完全一致**（paperclip / hindsight / VoiceStudio / ai-engineering-from-scratch / PipePipe / scriptc / openrig / univer / Madeira），均已在上午那期覆盖。因此本期改抓 **monthly 榜**（18 条）寻找未推送过的新面孔。
> 数据源：`github.com/trending?since=daily|weekly|monthly`，逐条解析 `<article class="Box-row">`，并用 GitHub API 校验元数据、release 与提交记录。
> 去重口径：严格避开前六期（09-17 / 09-18 / 09-23 / 09-24 / 09-25 / 09-28 上午）已展开的全部仓库。**本期 10 条全部为全新面孔。**

---

## 一、榜单速览

### 本期 10 条来源分布

| 来源 | 数量 | 说明 |
|---|---|---|
| Monthly 榜 | 10 | 全部为本期首次展开 |
| Daily 榜 | 0 | 9 条与上午那期完全重合，无新增 |
| Weekly 榜 | 0 | 18 条全部在前六期已覆盖 |

### 10 条详细条目

| # | 仓库 | 语言 | 月增 | 总 Star | 一句话 |
|---|---|---|---|---|---|
| ① | tt-a1i/archify | JavaScript | +51,711 | 72,988 | 把"画图"做成**可验证产物**的 Agent 技能 |
| ② | bilawalsidhu/gods-eye-view | JavaScript | +37,567 | 44,159 | 浏览器里的"间谍卫星模拟器"，数据全是公开真实的 |
| ③ | ayghri/i-have-adhd | Python | +26,939 | 51,662 | 把"别把答案埋起来"固化成 10 条规则的技能 |
| ④ | THU-MAIC/OpenMAIC | TypeScript | +18,484 | 39,317 | 清华开源多 Agent 互动课堂，课堂问答改成 agent loop |
| ⑤ | miuuyy/codex-chatgpt-web | TypeScript | +10,481 | 12,208 | 把 ChatGPT Web（含 Pro）当 Codex 的原生模型，不耗 Codex 额度 |
| ⑥ | every-app/open-seo | TypeScript | +7,792 | 21,435 | Semrush/Ahrefs 的开源替代，自带 MCP 与 Skills |
| ⑦ | google-research/timesfm | Python | +5,681 | 33,875 | Google Research 时序基础模型，v3.0 权重发布 |
| ⑧ | magnitudedev/magnitude | Rust | +3,743 | 5,295 | 本地推理引擎，先测机器再推荐模型并逐项调优 |
| ⑨ | cursor/plugins | TypeScript | +3,379 | 8,835 | Cursor 官方插件规范与官方插件集 |
| ⑩ | tech-leads-club/agent-skills | TypeScript | +1,954 | 6,928 | 主打"安全加固"的第三方技能注册表 |

**统计**：非 Agent / 非技能类项目 4 条（gods-eye-view、open-seo、timesfm、magnitude），Agent 与技能生态 6 条。

---

## 二、10 条详细

---

### ① tt-a1i/archify — 把"画架构图"从生成内容升级为**可验证交付物**

**事件内容**

JavaScript / MIT，创建于 2026-04-15，月增 **+51,711**（本期月榜增速第 1），总 **72,988** stars、4,932 forks、176 个未关闭 issue。最近提交 2026-09-28（今天）。自述："Agent skill for beautiful, verifiable architecture, workflow, sequence, data-flow, and lifecycle diagrams—self-contained HTML with motion and crisp export."

定位是 **Agent Skill**（仓库自带 `archify/SKILL.md`），不是独立应用。安装方式即技能生态的标准姿势：

```bash
npx skills add tt-a1i/archify -g
```

支持 Cursor、Claude Code、Codex CLI、OpenCode 四类 harness，另有独立的 DeepSeek Harness 插件包（`@tt-a1i/archify-dsh@0.1.0`）。**不需要仓库**也能用——直接对 Agent 描述"Browser → API → Redis 缓存未命中 → PostgreSQL 回填"即可出图。

**五种图类型 + 一种对比模式**：

| 类型 | 适用 | 提示词要点 |
|---|---|---|
| Architecture | 组件、服务、存储、边界 | 范围、核心组件、主路径 |
| Workflow | CI/CD、审批、工具调用、runbook | 参与者、顺序、分支、异常 |
| Sequence | API 调用、缓存回退、鉴权、异步链路 | 调用方、被调方、返回、时序 |
| Data Flow | 管道、血缘、PII、消费方 | 来源、转换、存储、边界 |
| Lifecycle | 状态、重试、等待、终态 | 状态、事件、重试与取消路径 |

外加 **Architecture Delta**：对比 Before / Delta / After 三份已验证快照，输出机器可读回执（machine receipt），用 `node archify/bin/archify.mjs compare architecture base.json head.json out.html --json` 调用。README 明确声明它**不推断影响面、风险或合并安全性**——只呈现作者声明过的事实。

**"可验证"是它的技术核心**（README 的 engineering 小节）：

- **Typed JSON IR** — 每个可渲染模式都有 schema 与可复现源文件。
- **交付前原子校验** — schema、布局、HTML/SVG、路由、标签到路由的净空检查**必须全部通过**，新的 showcase 产物才会替换上一个已知良好版本（fail closed）。
- **机器可读的失败回执** — `validate --json` / `deliver --json` 把非法选项、未知图表类型、不支持的组合统一收进带版本号的失败回执，使用固定的 `arguments` stage 与稳定诊断码，退出码 2；人类模式的 stderr 行为不变。
- **来源校验** — 固定提交的来源校验忽略本地 Git replacement refs，始终读取指定提交的原始对象，避免被替换后的文件或行范围造成误接受/误拒绝。
- **网络行为可关闭** — 更新检查只 GET 一个固定 manifest，不下载不安装；`ARCHIFY_UPDATE_CHECK_DISABLED=1` 可完全断网。

**版本与商业信号**：稳定版 `v2.16.0`（08-30），当前开发身份 `v2.17.0-dev.1`（未发布）。赞助方为 **Kimi Work · Supercode · EverMind/Raven**；已上架 Kimi Work 插件商店（名称"Interactive Architecture Diagram"），并被 Supercode 列为 Editor's Choice。

**值得关注的原因**

1. **它把"生成式输出"改造成"可验收输出"**。多数画图技能产出一次就不管了；Archify 在交付前做五类原子校验，不通过就回退到上一个良好版本，并给机器可读回执。这与 09-24 期 Superpowers/OpenSpec、09-28 上午那期 scriptc `coverage`、Paperclip 原子执行是同一条方法论：**把不可验证的变成可验证的**。
2. **月增 5.1 万星、总量 7.3 万，说明"图"是 Agent 最刚性的输出形态之一**。代码和 Markdown 之外，架构图是唯一既需要结构正确、又需要人眼验收的产物；把两者同时管住，是它区别于 Mermaid 类工具的地方（topics 里直接标了 `mermaid-alternative`）。
3. **技能商业化的可观察样本**。赞助商里同时出现 Kimi Work（模型厂商插件商店）、Supercode（Codex/Cursor 增强层）、EverMind/Raven（Agent 记忆基础设施）——三方都在争"技能分发入口"。一个 MIT 技能能同时拿到三家赞助，说明**技能已成为流量位**。
4. **工程细节可直接抄**：机器可读失败回执 + 稳定诊断码 + 固定 stage 名，是 CLI 面向 Agent 调用时的正确设计；`compare` 只报声明事实、不推断风险，避免了"AI 帮你判断合并安全"这类不可靠承诺。
5. **一个可复用的分发模式**：`npx skills add <repo> -g` + 自带 `SKILL.md` + 额外为特定 harness 出适配包（DSH 插件）。这已是 09-18 期以来最稳定的技能分发路径。

---

### ② bilawalsidhu/gods-eye-view — 公开数据拼出的"上帝视角"，把 OSINT 做成可玩的产品

**事件内容**

JavaScript（WebGL/Cesium），自定义许可（GitHub 标记 NOASSERTION），创建于 2026-06-22，月增 **+37,567**，总 **44,159** stars、8,982 forks、216 个未关闭 issue。站点 `maptheworld.ai`。

自述一句话概括了它的反差感：**"A spy satellite simulator in your browser, except the data is real."**（浏览器里的间谍卫星模拟器——只不过数据是真的。）

项目原名 WorldView，来自一个 YouTube 系列（该系列播放量 5M+，全平台 25M+）。**2026 年 8 月曾登顶 GitHub Trending 日榜与周榜**，获 Product Hunt 当日第 8（由 hashtag 发明者 Chris Messina 提交），JavaScript 之父 Brendan Eich 在 X 上评价"pretty cool"，并被 Pinokio 收录。

**"真实数据"具体指什么**（README 的 What's on the globe）：

| 数据层 | 内容 | 是否需要 Key |
|---|---|---|
| 航班 | 实时应答机航迹，可"钻进驾驶舱"跟随 | 否 |
| 船舶 | 船舶信标 | 否 |
| 卫星 | 轨道根数，可按语音查询下一次过境（升起/峰值/落下时间与可见性） | 否 |
| 地震 | 实时震中 | 否 |
| 交通 | 沿真实道路的聚合位置数据（**模拟**） | 否 |
| 摄像头 | 公开摄像头位姿（**粗估**） | 否 |
| 天气 | GFS / ECMWF 预报风场、历史雷达回放、卫星云图与闪电、NHC/CPHC 气旋路径 | 否 |
| ALPR | OpenStreetMap 中标注的车牌识别摄像头位置（仅位置与标签） | 否 |
| 火灾 / 大坝 / 数据中心 | 可语音计数、筛选、排序 | 否 |
| 高清底图 | Esri 卫星影像 + 免 key 地形；OSM 为回退 | 否 |
| 写实 3D | 需 Cesium ion token（个人非商用）或 Google Maps key | 是 |

**交互能力**（这些是它真正区别于"数据看板"的地方）：

- **Cockpit view** — 坐进被追踪航班，相机全程保持地形在下方。
- **Contacts** — 以目标为圆心 250 km 内的全部接触清单，可逐个进入驾驶舱。
- **Click-to-track** — 锁定目标、画渐隐轨迹、展开元数据；追踪到火灾或船只时**一键交接给最近的实况摄像头**。
- **Voice whiteboard** — 语音在世界地图上画真实边界多边形、标记与航线。
- **3D hangar** — 按机型加载真实 3D 模型（787、ATR-72、Citation、Bell 206、MQ-9），接近时从图标切换为模型。
- **Reskin reality** — GLSL 传感器滤镜：CRT、夜视 NVG、FLIR/热成像、Noir、雪地。
- **Detection overlay / Military HUD** — 屏幕空间包围盒 + ID、战术式抬头显示。
- **Share Links** — 相机、样式、图层乃至被追踪目标都序列化进 URL；README 特意写明"**被追踪目标是交接，不是书签**"。
- **Analyst answers** — 语音提问计数/筛选/排序卫星、数据中心、水坝、航班、船只、火灾、地震，**回答会标明数据源是否过期或是否走了回退源**。
- **Scene director** — 录制电影级相机巡游，支持场景文件导入导出与分享。
- **Nepal flood scene** — 回放 Bhote Koshi 洪水：淹没路径、目击来源、前后对比影像。

**语音控制由一个实时 AI Agent 驱动**，这也是它进入 AI 话题的原因。安装有两条路径：Pinokio 一键（推荐 8.2+），或本地终端运行。**无账号、无 API key 即可启动**，key 通过应用内 POWER UP 面板按需添加。

**值得关注的原因**

1. **它是"公开数据 + 3D 可视化"这条赛道的旗舰样本**。所有信号源（ADS-B、AIS、TLE、地震台网、OSM、气象模型）都是公开的，项目价值全在**聚合与呈现**——这正是 AI 时代最容易做、也最容易做砸的一类产品。它做对了。
2. **"免责声明与能力边界"写得极克制**：交通是模拟的、摄像头位姿是粗估的、ALPR 只有位置没有图像、Bundled 数据非商用。对照 09-25 期 lap 把数据边界写进文档，这是同一类成熟度信号：**公开数据产品必须先讲清哪些不是真数据**。
3. **实时语音 Agent 是它的交互主入口，而不是附加功能**。免手操作 + 语音标注 + 语音问询，把"看地图"变成"对话式情报分析"。这与 09-28 上午那期 VoiceStudio 用 MCP 把语音交给 Agent 是同一趋势的两端。
4. **"被追踪目标是交接，不是书签"是个好设计判断**。分享一个移动目标时，接收方应该看到它的当前位置而非发出时的位置——这类语义细节决定工具能否被真实用于协同。
5. **它证明了非 Agent 项目仍能拿到月榜顶级增速**（+37,567 排本期第 2）。趋势榜并未被 Agent 类项目垄断。

---

### ③ ayghri/i-have-adhd — 把"输出形态"本身做成技能：10 条规则治"答案被埋起来"

**事件内容**

Python / MIT，创建于 2026-05-13，月增 **+26,939**，总 **51,662** stars、2,981 forks、76 个未关闭 issue。tags 直接标了 `claude-code-plugin`、`claude-skills`。

自述："A skill to stop your coding agent from burying the answer. ADHD-friendly output."（一个让你的编码 Agent 别再把答案埋起来的技能。ADHD 友好的输出。）

**它解决的痛点用一组对照说清了**：

| Before（默认行为） | After（装上技能后） |
|---|---|
| "Great question! Let me think about this. Your auth flow has a few moving pieces… Looking at `src/auth.ts`, the `verifyToken` function (around lines 42-58) seems to be using an older `jsonwebtoken` API. One approach would be to update the package and rewrite that function. After making the change, you'd want to run the auth tests… By the way, you might also want to look at your dependency versions overall. Hope this helps! Let me know if you want to dig deeper." | "Run `npm install jsonwebtoken@latest`, then edit `src/auth.ts:42`.<br>1. Open `src/auth.ts`<br>2. Replace `verifyToken` (lines 42–58) with the snippet below<br>3. Run `npm test -- auth.spec.ts`<br><br>Next: paste the first failing line if any test fails." |

**10 条规则**（全文在 `skills/i-have-adhd/SKILL.md`）：

1. 先给下一步动作
2. 多步任务编号
3. 结尾给一个具体下一步
4. 抑制跑题
5. 每轮重述当前状态
6. 时间估算具体到分钟，不写"一会儿"
7. 让进展可见
8. 报错平铺直叙
9. 列表上限 5 条
10. **不要开场白、不要复述、不要收尾语**

**安装与定制**：可直接把提示词粘给 CLI（"Install the i-have-adhd skill/plugin from https://github.com/ayghri/i-have-adhd, refer to the repo's AGENTS.md"），或走 Claude 插件市场（`claude plugin marketplace add` + `install`）。改规则的方式是 fork → 编辑 `SKILL.md` → 换回自己的副本，README 还提醒先 `uninstall` 上游同名插件再装 fork（**fork 与上游共享同一插件名**，这是个真实的坑）。

**生态细节**：README 有 **11 种语言**（含简中、阿拉伯语、波斯语、泰语、越南语等）；致谢写明"松散改编自《The Adult ADHD Tool Kit》，但适配的是 LLM 该怎么回答，而不是人该怎么安排一天"。近期 PR 里出现 `fix/evals-token-cost-delta`（**验证成本测量并报告输入开销**）与 `feat/session-eval`（会话评测），说明它在给"输出风格"做量化评测。

**值得关注的原因**

1. **它把"输出形态"这一层独立出来了**。此前的技能都在补能力（画图、剪视频、查数据），这个技能只改**回答的形状**：结论前置、步骤编号、列表封顶 5 条、无客套。这是"人机接口层"的技能化——用户真正抱怨的往往不是模型不够聪明，而是答案被埋在第三段。
2. **它是"用规则约束模型行为"的极简版本**。10 条规则全是可判定的（编号了吗？列表超 5 条了吗？有"Hope this helps"吗？），因此**可以被自动评测**——仓库里正在跑的 token 成本与会话评测 PR 就是这个方向。对照 09-24 期 impeccable 的 61 条确定性设计规则，两者是同一思路在不同对象上的应用。
3. **"每轮重述当前状态"这条规则值得单独记**。长会话中 Agent 最容易丢的是"我们进行到哪了"，而不是事实细节；把状态重述写成强制规则，比事后让用户翻记录有效得多。
4. **5.1 万星、76 个 open issue 的比值说明需求普遍且维护跟得上**。一个只含 `SKILL.md` 的仓库能到这个量级，反过来证明**技能分发的边际成本已接近零，稀缺的是判断力**。
5. **它给出了"技能可被 fork 并本地改写"的完整路径**，包括同名冲突的处理。技能生态要成熟，这种"我能改它"的路径必须清晰。

---

### ④ THU-MAIC/OpenMAIC — 清华多 Agent 互动课堂：把课堂问答从流程图改成 agent loop

**事件内容**

TypeScript（Next.js 16 + React 19 + LangGraph 1.1）/ MIT，清华大学 MAIC 团队，创建于 2026-03-11，月增 **+18,484**，总 **39,317** stars、6,110 forks、171 个未关闭 issue。Demo：`open.maic.chat`。论文见 JCST'26（DOI 10.1007/s11390-025-6000-0）。

自述："Open Multi-Agent Interactive Classroom — Get an immersive, multi-agent learning experience in just one click."

**近期版本是理解它的关键**：

| 版本 | 日期 | 内容 |
|---|---|---|
| **v1.1.1** | 09-26 | **安全版本**。修复 MinerU Cloud 解析时用裸 `fetch` 拉取供应商返回的预签名上传 URL 与结果 ZIP URL——**无 SSRF 校验、跟随重定向不检查、无体积上限**；当服务端未配置 MinerU Cloud 时调用方可自带 base URL，从而把服务端的 `PUT` 上传与结果下载指向 loopback / 私有地址。现全部走严格 provider transport，每个重定向跳都校验，上传与 ZIP 必须是 HTTPS 公网地址，上传不跟随重定向，地址策略拒绝不重试；JSON 响应、ZIP 下载与每个解压条目都加体积上限并在超限时立刻停止解压；共享 SSRF guard 现在还按内嵌 IPv4 归类 `::/96` IPv4-compatible IPv6。`GHSA-cpjc-vgjh-c5jp`（#1688 报告） |
| **v1.1.0** | 09-24 | 课堂聊天默认跑在 **agent loop** 上；设置按课程工作流重组，**每个生成步骤可选模型**；Token Plans 一键预设（TokenDance、MiniMax、Seed、Kimi）；新增 OpenRouter 图像/视频 provider、Gemini 3.8/3.7 Flash、小米 MiMo V2.6；TTS 限流改"降速而非失败"；可选单租户模式；渲染服务加入准入控制与单任务资源预算 |
| **v1.0.0** | 08-27 | Pro workbench：**与 Agent 对话来规划课程**、逐页构建与修订；服务端持久化会话可取消/恢复/接管；会话材料（文档/音频/视频/网页搜索）；课程工具 + **24 个内置技能**（幻灯片、测验、互动组件、PBL、图像、视频、语音、`.pptx` 导入）；provider 中立（模型、媒体、搜索、存储全可换） |
| v0.3.x | 06–08 月 | MP4 一键导出、服务端持久化（Postgres 参考实现）、直接操作幻灯片（拖拽/缩放/旋转/多选）、"Edit with AI" 走**校验过的 JSON Patch**、多格式文档解析、**v0.3.0 从 AGPL-3.0 重新许可为 MIT** |

**v1.1.0 最有价值的一条是"问你所见"**：学习者可以在播放条上**指向某个 PPT 元素、某个互动组件或白板上的涂鸦**然后提问；声明了状态的互动页会在提问时刻被**采样当前状态**，因此"老师"能解释学习者实际看到的结果，`read_scene` 则暴露互动页的静态说明。同时老师可读课件、查互动实验的实时状态、并联网搜索后再回答。

**部署与生态**：Vercel 一键部署；需要至少一个 LLM provider key（其余可选）；OpenClaw 集成；Lemonade 本地 AI；FunASR 本地 ASR；社区走 Discord 与飞书；四语言 README。

**值得关注的原因**

1. **教育是继金融之后第二个被"具名 Agent 团队"完整打包的垂类**。09-23 期推过 anthropics/financial-services（10 个金融垂类 Agent，人工签核写进合规声明），OpenMAIC 是同一条路线在教育上的落地，而且**它的产品形态是课堂本身**（课件 + 测验 + 互动 + 讲解），不是"帮你备课的助手"。
2. **v1.1.0 的"指向元素提问 + 采样互动页当前状态"解决的是多模态 Agent 的核心难题：Agent 必须知道用户此刻在看什么**。09-23 期 video-use 的解法是"给更少但更对的信息"（45M token → 12KB 文本 + 按需 PNG）；OpenMAIC 的解法是"在提问那一刻去读你指的东西的实时状态"。两者都在解决同一个问题——**把无限的视觉上下文收敛成一次精准取值**。
3. **v1.1.1 的 SSRF 修复是本期的安全样本，细节值得逐条抄**：供应商返回的 URL 不等于可信 URL；重定向必须逐跳校验；上传不得跟随重定向；解压要设上限（zip bomb）；地址策略拒绝不得重试（否则变成探测器）；`::/96` 这类 IPv4-compatible IPv6 必须按内嵌 IPv4 归类。任何"让用户自带 base URL"的自托管产品都适用这套清单。
4. **"从 director graph 改为 agent loop"是一次架构倒退式进步**：流程图式编排可控但僵硬，agent loop 灵活但难控；它选择在**课堂问答**这个具体场景上换成 loop，并保留"可读课件、可查实验状态、可联网"的工具边界。这比"全站换 agent"更务实。
5. **v0.3.0 从 AGPL 换成 MIT，是明确的分发策略选择**：要进 Vercel 一键部署、要能被 OpenClaw/Lemonade 集成、要被企业自托管，AGPL 是阻力。许可证变更是产品决策，不是法律细节。
6. **24 个内置技能 + `.pptx` 导入 + 每步可选模型**，说明它已经不是 demo，而是"课程生产流水线"。每步可选模型这一点尤其务实——出大纲、生成幻灯片、生成互动页对模型的要求完全不同。

---

### ⑤ miuuyy/codex-chatgpt-web — 把 ChatGPT Web（含 Pro）装进 Codex 的模型选择器，且不耗 Codex 额度

**事件内容**

TypeScript / MIT，创建于 2026-07-26，月增 **+10,481**，总 **12,208** stars、967 forks、20 个未关闭 issue。**今天（09-28）刚发 v6.1.3**，此前 09-23 至 09-27 连续发了 v6.0.0 → v6.1.0 → v6.1.1 → v6.1.2 → v6.1.3，五天五版。

自述："Use ChatGPT Web (including Pro) as a native model in Codex — with context, tools, streaming and images, without using Codex quota."

**核心主张**：用你账号里已有的 ChatGPT Web 模型（含 Pro），从 **Codex 原生模型选择器**里直接选，走 **ChatGPT Web 自己的用量额度**，不消耗 Work 或 Codex 配额；同时保持同一套界面、任务、图片与流式输出。

**V6 的六个要点**：

- **模型名清晰 + 原生 Effort 控制** — 自动模型以 `(Web)` 结尾：**GPT-5.6 Luna / GPT-5.6 Sol / GPT-5.6 Pro / GPT-6 Pro**。Sol 通过 Codex 的 Effort 选择器暴露你账号支持的推理档位；Instant 单独成项以保住自己的上下文预算；旧任务继续解析到原模式。
- **Pro 的 Limits 页** — 可选开启，针对 Pro $100 与 $200 套餐分别跟踪模型额度，**用量到 75% 起显示黄色警示**。README 明确写这是**本地估算**（滚动窗口、只统计经本 launcher 发出的消息），不是 OpenAI 的剩余额度或重置时间。
- **Bigger Context 拆更小的部分** — 大请求改用**六个有序部分**（原为三个），工具与附件挂在最后一部分，整体上下文与压缩预算保持不变。
- **每轮开新浏览器会话** — 可选，把同一 Codex 任务的上下文重建在一个全新的 ChatGPT 会话里。**代价是发送更多上下文**，好处是避免 ChatGPT 在多轮后丢失工具。默认关闭，仅自动模式可用。
- **Save chats in ChatGPT** — 可选，用常规会话替代 Temporary Chat；ChatGPT 的记忆与自定义指令可能生效。默认关闭。
- **原生 Linux ARM64 包** — x64 与 ARM64 的 AppImage 与运行时包各自独立安装更新。

**三种模式（权限姿态写得很清楚）**：

| 模式 | 发消息 | 本地 Codex 工具 |
|---|---|---|
| Browser-only | 自动 | 否 |
| Full harness（With Automation） | 自动 | 是，经 MCP |
| **Zero Risk** | **手动粘贴并发送** | 是，经独立 MCP 连接器 |

**Full harness 的技术细节**：ChatGPT 的工具调用经**官方 `openai/tunnel-client`** 回连到当前 Codex 任务。隧道是**出站**的——不暴露公网 IP、不开入站端口、不需要路由器端口转发。需要开启 ChatGPT Developer Mode 并创建一个名为 `Codex Native2` 的 Tunnel 连接器（Authentication: None、Allow all actions）。写/改动作还要求 ChatGPT 工作区与管理员策略允许。**未显式开启 `--auto-approve-tool-calls` 时，意外的审批弹窗一律 fail closed**；该选项只点"Allow once"，永不永久授权。

**上下文与限额的实测口径**（README 的 Limits 一节）：Plus Medium/High 使用**实测 90,000 token 窗口**，实验性 **3× context** 可到 270,000 token，全程支持 Codex 原生压缩。

**其他**：应用自带浏览器与运行时，**不需要单独装 Chrome / Node / Bun**；更新走 launcher 或 `install-launcher.sh` / `install-launcher.ps1`（校验 checksum、保留 ChatGPT profile 与 launcher 设置）；诊断走 Activity → Export safe log + Run doctor。

**值得关注的原因**

1. **它把"额度"变成了产品的一等公民**。V6 专门做 Limits 页、75% 预警、把两个 Pro 模型与共享额度分开统计，并在 README 里**明确区分"本地估算"与"官方剩余额度"**。这与 09-25 期 stablyai/orca 的"成本合计遗漏模型时显式声明"是同一条趋势：**AI 工具的可信度越来越取决于它是否诚实地描述成本**。
2. **"五天五版、20 个 open issue"说明它面对的是高频变化的真实目标**。它的工作对象是别人家的 Web UI（选择器、登录态、Pro 标识、限流提示都会变），因此维护成本天然高。任何"把 Web 产品当 API 用"的项目都适用这个判断：**稳定性来自快速跟进，而不是抽象层**。
3. **Zero Risk 模式是个诚实的设计**。它不读也不操作 ChatGPT 页面，由用户自己选模型、自己粘贴、自己确认"Sent"。在自动化与合规之间，它给出了一个"只做本地一半"的中间态。
4. **`openai/tunnel-client` 的出站隧道是通用做法**：不暴露公网 IP、不开入站端口，只做出站长连接。要打通"云端 Agent ↔ 本地工具"，这是目前最省事的拓扑。
5. **风险必须说明**：这类工具处在订阅条款的灰色地带，且依赖对第三方 Web UI 的自动化。README 也写明"写/改动作需要 ChatGPT 工作区与管理员策略允许"——**能用不等于合规**，企业环境使用前需自行核对条款。它的真正价值在于**揭示了"额度"正在成为多产品并行的核心约束**，而不是推荐照搬。

---

### ⑥ every-app/open-seo — Semrush/Ahrefs 的开源替代，把"数据费"交还给用户

**事件内容**

TypeScript / MIT，创建于 2026-02-27，月增 **+7,792**，总 **21,435** stars、2,751 forks、196 个未关闭 issue。站点 `openseo.so`。最新版 `v0.1.9`（09-17）。

自述："Open source alternative to Semrush and Ahrefs."，README 的定位句更直接："**SEO tool for the people.** If tools like Semrush or Ahrefs are too expensive or bloated, OpenSEO is a pay-as-you-go alternative that you actually control."

**六大工作流**：关键词研究、排名跟踪、竞品洞察、外链、站点审计、AI 可见性（AI Visibility）。

**它的核心设计是"自带数据源 + 透明加价"**：

- 必须自备 **DataForSEO API key**（自托管时你直接付给 DataForSEO）。
- 官方托管版 $10/月，README 明说盈利方式是"**对每次 DataForSEO 请求加收 28%**"。把加价率写进 README，是少见的坦白。
- 无订阅、按用量付费、可 fork 后自己改。

**自托管两条路径（推荐顺序明确）**：

| 路径 | 适用 | 说明 |
|---|---|---|
| Docker（简单） | 个人本机试用 | README 建议：除非你已在自托管其他应用且有把握，否则**优先用 Cloudflare 而非 Railway / Coolify / Dokploy**（后者的简化支持在未来几个月补上） |
| **Cloudflare（推荐）** | 面向公网、多设备或团队 | **免费套餐即可** |

**Agent 是它的第一类用户**：内置 **MCP server**，Claude Code、OpenClaw、Hermes 等 Agent 可直接读你的 SEO 数据；另配可复用的 **Agent Skills** 引导 Agent 完成 SEO 任务（也支持自建）。连贡献流程都技能化了——仓库提供 `/simple-issue-description` 技能，用 `npx skills add every-app/open-seo --skill simple-issue-description` 安装。

**值得关注的原因**

1. **它给出了"替代昂贵 SaaS"的标准拆法**：**开源前端 + 自托管 + 自带数据源 API key + 透明加价率**。Semrush/Ahrefs 的贵主要贵在数据与历史库，不在 UI；把 UI 与工作流开源、把数据费按用量直付，是对的选择。与 09-25 期 lap（本地优先照片管理）、09-28 上午那期 VoiceStudio（本地语音栈）构成同一模式的三次出现。
2. **"AI Visibility"被列为一等工作流**。传统 SEO 工具盯的是搜索排名，OpenSEO 直接做了"你在 AI 回答里的可见度、情绪与引用来源"。**GEO（生成式引擎优化）已经从概念变成工具里的一个 tab**。
3. **推荐自托管在 Cloudflare 免费套餐上，是个具体的成本判断**。SEO 抓取是低频、突发、无状态的负载，Workers + 免费额度天然匹配；用常驻容器反而是浪费。这与 09-25 期 FxEmbed 用 Cloudflare Workers 做链接展开是同一取舍。
4. **MCP + Skills 让 SEO 从"人操作工具"变成"Agent 调用数据"**。关键词研究、外链分析这类工作本质是"取数 → 归纳 → 产出内容"，非常适合 Agent；把 MCP 做成一等入口，等于把工具嵌进了内容生产流水线。
5. **196 个 open issue 与 2,751 forks** 说明它被大量 fork 后自行改造——这正是 README 鼓励的（"Fork and vibe code your own custom tool"）。**把"可 fork"当产品定位而非风险**，是开源替代类项目的正确姿态。

---

### ⑦ google-research/timesfm — 时序基础模型发到 v3.0，且开始修 Apple Silicon 推理路径

**事件内容**

Python / Apache-2.0，Google Research，创建于 2024-04-29，月增 **+5,681**，总 **33,875** stars、3,263 forks、263 个未关闭 issue。官方介绍页：Google Research 博客《A decoder-only foundation model for time-series forecasting》。

**近期版本与提交**：

| 版本/提交 | 时间 | 内容 |
|---|---|---|
| **v3.0.0** | 08-28 | **新模型权重与配套代码：TimesFM-3.0** |
| v3.0.2 | 09-09 | 版本号提升；`timesfm3/mlx` 在非 mac 平台优雅处理缺失 mlx |
| 09-14 一批 MLX 修复 | 09-14 | `timesfm3/mlx` 对齐 torch：**拼接（stitching）、CPM RevIN、残差激活、NaN 处理**；尊重 `ff_activation` / `v_norm` / `causal_attention` / `use_rope_var` / `use_memory_*`；接受 `silu` 作为激活别名并加深 CPM refine 覆盖 |
| #509 / #510 | 09-15 | MLX–Torch 数值对齐修复；`_weights_cached()` 回退到扫描缓存快照（修 stale ref） |

**技术定位**：TimesFM 是**解码器式（decoder-only）时序基础模型**，做零样本 / 少样本预测——即不做逐数据集训练，直接把历史序列喂进去出预测。这一路线对传统统计模型（ARIMA/ETS）与梯度提升树（LightGBM 等）构成直接替代压力，尤其在**大量短序列、冷启动、需批量预测**的场景。

**值得关注的原因**

1. **时序预测是"基础模型化"最晚也最实用的一块**。语言、图像、语音、代码之后，时间序列是每个企业都有的数据形态（销量、流量、库存、能耗、指标）。一个能零样本工作的时序基础模型，替代的是**每张表都要单独建模调参**的旧流程。
2. **v3.0 发在 8 月底、9 月却在月度榜上持续走高**，说明热度不是发布瞬间的脉冲，而是**被实际使用后扩散**的。对照 09-17 至 09-28 的观察，这是少数"发布后越用越热"的项目。
3. **9 月中旬的提交几乎全在修 MLX 后端与 Torch 的数值一致性**——这是一条高信息量的信号：**本地 Apple Silicon 推理是真实需求，且"和 Torch 结果对不上"是用户最不能忍的问题**。修 stitching、RevIN、残差激活、NaN 处理这些细节，比加新功能更能说明用户在拿它做真事。
4. **`silu` 别名、`use_rope_var`、`causal_attention` 这类配置对齐**，说明社区在加载**第三方转换权重**（很可能来自 HuggingFace 上的社区量化/移植版）。基础模型的分发一旦离开官方权重，配置兼容性就成了主要摩擦。
5. **对做数据分析类 Agent 的人有直接意义**：时序预测可作为 Agent 的一个工具被调用（读表 → 预测 → 出图 → 写结论）。它不需要 GPU 集群，本地 MLX/CPU 也能跑，正好适配"Agent 在本机跑工具"的形态。

---

### ⑧ magnitudedev/magnitude — 本地推理引擎的差异化不在"能跑"，而在"帮你选 + 帮你调"

**事件内容**

Rust / Apache-2.0，创建于 2026-06-12，月增 **+3,743**，总 **5,295** stars、379 forks、21 个未关闭 issue。站点 `magnitude.dev`。CLI 包 `@magnitudedev/cli` 当前 `0.1.5`（09-23），09-18 至 09-23 六天内发了 0.1.1 → 0.1.5。

自述："Open source inference engine for the hardware you already own. **Profiles your machine, recommends the best open models for it, and tunes them for your exact hardware.** Works on Apple Silicon, NVIDIA, AMD, or nothing but a CPU."

**使用三步**：下载安装 → 在 **Discover** 里挑一个被推荐的模型并下载 → 在 **Connections** 里连上你已在用的 Agent。桌面应用自带 `magnitude` CLI。

**它自己划的差异线（FAQ 里最值得读的一段）**：

> **与 Ollama / LM Studio 的区别**：它们跑你选的模型；**Magnitude 帮你选**。它在下载前就估算每个模型与量化版本在你机器上的表现，然后把你选中的那个**针对你的确切硬件做调优**——从上下文大小到投机解码。

**能力清单**：

- **认识你的机器** — 先做硬件画像，**下载前**给出 tok/s 估算
- **推荐最优模型** — 按速度、准确率、智能程度、内存占用排序
- **端到端调优** — 投机解码等全部按你的硬件预设
- **一键接 Agent** — Pi、OpenCode、Hermes、OpenClaw、Codex、Claude Code、Oh My Pi、Cline
- **零边际成本** — 无 token 费用、无 API key、无限流
- **完全私有离线** — 模型、提示词、文件全在本机；模型下载后可断网
- **按需加载** — 请求时加载，空闲或内存吃紧时卸载
- **硬件覆盖** — macOS/Linux/Windows 原生；Apple Silicon、NVIDIA、AMD、**纯 CPU**，含统一内存机型（**DGX Spark、Strix Halo**）

**值得关注的原因**

1. **"帮你选"比"帮你跑"是更值钱的判断**。本地推理的工具层已经饱和（Ollama、LM Studio、llama.cpp 全家桶），真正的痛点是"我这张卡到底该跑哪个模型的哪个量化"——这是个需要硬件画像 + 性能建模的问题。Magnitude 把答案放在**下载之前**，直接省掉"下 40GB 发现跑不动"的循环。
2. **统一内存机型被明确列为支持目标（DGX Spark、Strix Halo）**，这是对 2026 年硬件趋势的准确判断：本地推理的主战场正在从"消费级独显"转向"大内存统一架构"。
3. **"空闲或内存吃紧时卸载模型"是本地 Agent 工作流的关键机制**。本地跑 Agent 最容易踩的坑不是算力不够，而是**模型常驻把内存吃光导致整机变慢**。按需加载/卸载让本地推理可以和日常办公共存。
4. **一键连 8 种 harness，是"本地模型"与"编码 Agent"之间的最后一公里**。09-28 上午那期的 VoiceStudio（MCP 暴露本地语音）、这期的 Magnitude（本地模型暴露给 harness），本质都是**把本地能力接到 Agent 的工具链上**——本地优先的竞争已经不在模型侧，在接线侧。
5. **六天五个 CLI 版本、只有 21 个 open issue**，说明迭代快且收敛好；21 个 issue 对 5,295 stars 是很低的比值。

---

### ⑨ cursor/plugins — 编辑器厂商自己下场做插件市场，并开始声明"服务端放在哪"

**事件内容**

TypeScript，**无 LICENSE 文件**，创建于 2026-01-23，月增 **+3,379**，总 **8,835** stars、829 forks、154 个未关闭 issue。最近提交 2026-09-25。

自述："Cursor plugin specification and official plugins." 仓库结构是**根目录下每个插件一个独立目录，各自带 `.cursor-plugin/plugin.json` manifest**——即它同时是**规范**（specification）与**官方插件集**。

**插件分四类**：

| 类别 | 插件 |
|---|---|
| **Developer Tools**（Cursor 自研） | `thermos`（热核级分支审查：深度安全/正确性审计、严苛代码质量量表、并行子代理、可选 merge-ready PR 流）、`orchestrate`（把大任务扇出到并行云 Agent，含 planner / worker / verifier 与结构化交接）、`advisor`（重大决策前、卡住时、宣布完成前咨询更强的模型）、`ralph-loop`（自指式迭代循环）、`agent-compatibility`（CLI 驱动的仓库兼容性扫描 + 审计启动/校验/文档与现实的差距）、`pr-review-canvas`、`docs-canvas`、`cursor-sdk`（用 TypeScript SDK 构建应用与自动化）、`create-plugin`、`teaching` |
| **Developer Tools**（社区作者） | `cli-for-agent`（**设计 Agent 能可靠运行的 CLI** 的模式：flags、带示例的 help、管道、错误、幂等、dry-run）、`continual-learning`（用高信号要点增量更新 `AGENTS.md` 的转录驱动记忆）、`cursor-team-kit`、`pstack`（Lauren Tan）、`grok-voice` |
| **Productivity** | Gmail、Google Drive、Google Calendar、Google Docs、Google Sheets、Google Slides |
| **Integrations**（第三方 SaaS） | GitHub、Playwright、Salesforce、HubSpot、X、Zoom、Gong、Intercom、Clay、Docusign、Navan、Ashby、Outreach、Amplemarket、Juicebox、Profound、Circleback 等 |

**最近提交里最值得注意的技术动作是"声明服务端位置"**：

```
posthog-mcp: declare server placement (1.0.1)
third_party: declare server placement for TinyFish, beehiiv, Trello, Buffer, Plaud (1.0.1)
```

即 **MCP 插件必须显式声明它的 server 是远端还是本地**。同期还出现一次"重复 PostHog 插件先 revert 再重加"（#431 revert → #437 重加），说明审核流程在收紧。

**值得关注的原因**

1. **厂商官方入场，与第三方技能分发形成两条路线**。09-24 期推过 davila7/claude-code-templates（第三方做 Claude Code 配置分发），09-18 期推过 anthropics/knowledge-work-plugins（模型厂商做职能插件）。**Cursor 现在把规范与官方插件放进同一个仓库**，意味着"插件市场"的入口正被编辑器厂商收编——第三方分发层的空间会被压缩。
2. **`server placement` 声明是 MCP 生态的成熟标志**。MCP 插件的安全模型与"server 在哪跑"直接相关：远端 server 意味着凭证与数据出境，本地 server 意味着要装东西、要读文件。**把它变成 manifest 里的必填声明**，是把安全边界从文档搬进格式。
3. **插件列表本身就是一份"Agent 工作流"的现状清单**：`orchestrate`（并行云 Agent + verifier）、`advisor`（决策前问更强的模型）、`thermos`（并行子代理 + 严苛质量量表）、`ralph-loop`（自指迭代）、`continual-learning`（增量更新 `AGENTS.md`）。**五种都在解决同一件事：如何让多个 Agent 的输出可信**——与 09-24 期 Superpowers/OpenSpec、09-28 上午那期 openrig 的 owner/checker 配对完全同源。
4. **`cli-for-agent` 这个插件值得单独看**：它教的是"怎么设计 CLI 才能被 Agent 可靠调用"——flags、help 带示例、可管道、错误可读、幂等、dry-run。09-25 期 Hindsight 的 `--json`、这期 archify 的机器可读失败回执，都是同一个工程课题：**CLI 的第一类用户正在从人变成 Agent**。
5. **`grok-voice`（实时语音到语音 + 转录 + 朗读 + 日志驱动的修复循环）与 `Profound`（跟踪 AI 可见度、情绪与引用）** 显示插件已经覆盖到"语音交互"与"GEO 度量"这两个新领域。

---

### ⑩ tech-leads-club/agent-skills — 技能供应链的安全问题被量化了：13.4% 的技能含严重漏洞

**事件内容**

TypeScript（100%）/ 自定义许可（NOASSERTION），创建于 2026-01-19，月增 **+1,954**，总 **6,928** stars、555 forks、**仅 30 个未关闭 issue**。npm 包 `@tech-leads-club/agent-skills`；站点 `agent-skills.techleads.club`。

自述："The secure, validated skill registry for professional AI coding agents. Extend Antigravity, Claude Code, Cursor, Copilot and more with absolute confidence."

**它引用并直接对标的是一份第三方扫描报告**：

> 在一个 [Snyk Agent Scan 报告](https://github.com/snyk/agent-scan/blob/main/.github/reports/skills-report.pdf) 显示**超过 13% 的市场技能含严重漏洞**的生态里，Agent Skills 作为一个**经过验证、测试、安全**的能力库存在。

**它宣称的安全措施（README 的 Security & Trust）**：

- **100% 开源、无二进制**
- **CI/CD 中做静态分析**
- **不可变完整性** — lockfile + 内容哈希
- **人工审核提示词**（human-curated prompts）
- **CLI 纵深防御** — 净化（sanitization）、路径隔离、**符号链接防护**、**原子 lockfile**、审计轨迹
- **发布前每个技能都用 Snyk Agent Scan（原 mcp-scan）扫描**
- 威胁模型与漏洞上报流程写在 `SECURITY.md`

**技能目录结构标准化**：

```
packages/skills-catalog/skills/
  (category-name)/skill/
    SKILL.md      ← 主指令
    templates/    ← 文件模板
    references/   ← 按需加载的文档
```

**支持矩阵按三档分层**（这一点很务实）：

| Tier 1（主流） | Tier 2（上升） | Tier 3（企业） |
|---|---|---|
| Claude Code、Cline、Cursor、GitHub Copilot、Windsurf | Aider、Antigravity、Gemini CLI、Kilo Code、Kiro、OpenAI Codex、Roo Code | Amazon Q、Augment、Droid (Factory.ai)、OpenCode、Sourcegraph Cody、Tabnine |

近期提交：新增 `/mcp/` 落地页；marketplace 侧边栏展示版本、运行时、支持的 Agent 与 `allowed-tools`；支持按文件生成 ZIP 下载；`tlc-discover` 升 0.9.0、`tlc-spec-lean` 升 1.1.0；还修过一处"在 spec-driven 落地页上**删掉保证结果的文案**"（`fix(marketplace): drop guaranteed-outcome copy`）。

**值得关注的原因**

1. **"13.4% 的市场技能含严重漏洞"这个数字，比任何一篇安全倡议都更有推动力**。它把"技能供应链风险"从定性担忧变成定量事实。无论数字本身口径如何（项目引用的是 Snyk 的报告），**这个量级足以支持"技能安装需要像依赖安装一样做审计"的结论**——这与 09-18 期记录的 n8n SBOM + OpenVEX、09-24 期 claude-code-templates 的 RCE 修复（`GHSA-79wm-x847-7cvg`，0.0.0.0 绑定 + CORS 通配 + `shell:true`）、09-28 上午那期 Madeira 的"AI 代码不得回馈上游"构成完整的一条线：**Agent 生态的安全议题正在从"模型会不会乱来"转向"你装的东西是谁写的"**。
2. **"符号链接防护 + 原子 lockfile + 路径隔离"这套 CLI 防御清单，是安装器类工具的最小正确集**。技能安装器要写文件到 `~/.claude/skills`、`~/.cursor/` 等目录，路径穿越与符号链接是最直接的攻击面；lockfile 不原子则在并发或中断时会留下半装状态。
3. **`allowed-tools` 出现在 marketplace 侧边栏**，说明"技能能调用哪些工具"正在被**结构化声明**，而不只是写在提示词里。这是把权限从"描述"变成"字段"的第一步——与本期 ⑨ cursor/plugins 的 `server placement` 声明是同一类动作。
4. **"删掉保证结果的文案"这个提交很小但很重要**。技能市场最容易失控的是营销话术（"保证 X 结果"），而技能的实际效果高度依赖模型与上下文。**主动删掉这类承诺**，是可信度建设。
5. **三级支持矩阵避免了"假装全平台兼容"**。Tier 1 才是真支持的，Tier 3 是"能装但预期有限"。技能生态的跨 harness 兼容性普遍被夸大，分层标注是诚实的做法。
6. **30 个 open issue / 6,928 stars 是全期最健康的比值之一**（对比本期 ① archify 176/72,988、④ OpenMAIC 171/39,317），说明它把精力放在审核与收敛，而不是拉需求。

---

## 三、其他趋势速览

### 本期未展开但值得记一条（月榜第 11 个新面孔）

**pollen-robotics/microduck_rl**（Python / Apache-2.0，创建 2025-12-06，月增 +2,276，总 2,301 stars、496 forks）— Pollen Robotics 为 **~800 g、~25 cm 高的双足机器人 Microduck** 开源的 RL 训练环境，基于 **mjlab（MuJoCo Warp）+ PPO**，50 Hz 训练 → 导出 **ONNX** → 部署到真机。它的价值在于**把完整 sim2real 配方写进了仓库**：BAM 执行器物理模型（Dynamixel XL330 的电压控制律、反电动势、Coulomb/Stribeck/负载相关摩擦）+ 域随机化（电池电压、负载压降、指令延迟、摩擦幅值）+ **±1° 齿隙（backlash）仿真**（每个舵机串一个不受驱动的 `passive_<joint>_backlash` 铰链，且编码器读的是齿隙**之后**的位置，观测与动作维度不变，因此 ONNX 导出与运行时无需改动）。任务覆盖行走、跌倒恢复、起立、坐站、低头触地、踢球、**前滚翻**、轮滑（swizzle、下坡滑行、轮上起立）等，部署时在共享的 **61 维观测契约**下热切换策略。无 GPU 可用 `--hf-jobs` 跑在 Hugging Face Jobs 上。**在 ~800 g 这个尺度上，执行器保真度就是 sim2real 差距的主要来源**——这句话对整个机器人 RL 领域都成立。

### 前六期已推送仓库的新动态（不重复详述）

| 仓库 | 新动态 |
|---|---|
| **vectorize-io/hindsight**（日 +4,520 / 周 +11,089） | 周榜第 1；`v0.10.1`（09-21），无新版本 |
| **paperclipai/paperclip**（日 +2,401 / 周 +7,364） | 周榜第 2；`v2026.916.1`（09-21），无新版本 |
| **stablyai/orca**（周 +6,227） | `v1.4.214`（09-26）Notebooks 原生渲染 `.ipynb` + 持久 Jupyter kernel；`v1.4.215`（09-27）profile JSON 与 SQLite 不一致时展示各自最后保存时间 |
| **Tencent/WeKnora**（周 +2,705 / 月 +9,985） | 仍 `v0.8.2`（09-24），本周无新版本 |
| **cloudflare/security-audit-skill**（月 +19,427） | 月榜第 1；周 +4,805 排第 4，已从 09-25 的退榜中恢复 |
| **anthropics/claude-code**（周 +1,493） | `v2.1.283`（09-25）新增 `x-claude-code-prompt-id` 网关提示头、`availableModelsMatch: "exact"`、`deniedModels` |
| **debpalash/VoiceStudio**（月 +27,329） | 09-28 上午那期已详述；`v0.5.6`（09-23） |
| **Tencent/BrowserSkill**（月 +6,144） | 无新版本 |
| **superdesigndev/treg**（月 +2,945） | 无新版本 |
| **alibaba/open-code-review**（月 +20,657） | 无新版本 |
| **anthropics/financial-services**（月 +3,340） | 无新版本 |
| **rohitg00/ai-engineering-from-scratch** | 日 +790 / 周 +3,850，仍在双榜 |
| **affaan-m/ECC**（周 +5,175）、**davila7/claude-code-templates**（周 +1,154）、**HKUDS/CLI-Anything**（周 +1,105）、**TencentCloud/Octop**（周 +869）、**cloudflare/quiche**（周 +521）、**anthropics/knowledge-work-plugins**（周 +478）、**FxEmbed/FxEmbed**（周 +432） | 均无重大新事件 |

### 榜单结构观察

- **Daily 榜与 11:24 完全一致（9 条）**：头部固化。GitHub trending 的日榜在同一日内不刷新候选池，只有 star 增量在变；因此**同日二次运行必须换榜才有新信息量**，本期改抓 monthly 是正确的取数方式。
- **Monthly 榜 18 条中，11 条是前六期未推送过的新面孔**，其中 10 条进入本期详细。月榜呈现的是"上一代爆款"（archify 4 月建仓、i-have-adhd 5 月、gods-eye-view 6 月），与日榜的"本周新爆"互补。
- **本期 10 条中，技能类占 4 条**（archify / i-have-adhd / agent-skills / cursor 官方插件集），是近七期最高的技能占比。09-17 期提出的"`SKILL.md` 成为事实上的技能分发格式"，在本期已经演化为**分层**：官方（Cursor）、加固第三方（agent-skills）、垂直高价值（archify、i-have-adhd）。
- **非 Agent 项目 4 条**（gods-eye-view / open-seo / timesfm / magnitude），比 09-25 与 09-28 上午的 5/10 略降，但性质不同——本期这几条都是"AI 相关但非 Agent 编排"（本地推理、基础模型、SaaS 替代、数据可视化）。

---

## 四、当日主线判断（本期）

1. **技能生态从"有没有"进入"分几层、能不能验"的阶段。** 本期四条技能类项目恰好构成完整光谱：**Cursor 官方插件集**（厂商收编入口，并把 MCP 的 `server placement` 变成 manifest 必填声明）、**agent-skills**（第三方加固注册表，引用"13.4% 技能含严重漏洞"并给出 symlink 防护 + 原子 lockfile + Snyk 扫描的完整清单）、**archify**（垂直高价值技能，交付前做五类原子校验、失败回执机器可读、不通过就回滚到上一个良好版本）、**i-have-adhd**（只改输出形态的极简技能）。**同一个格式，四种不同的信任策略。**

2. **"输出形态"第一次被当作独立问题处理。** i-have-adhd 只做一件事：结论前置、步骤编号、列表封顶 5 条、不要开场白和收尾语。它拿到 5.1 万星说明**用户的真实抱怨大量集中在"答案被埋在第三段"**，而不是模型能力。这类规则全部可自动判定，因此可以被评测——它正在做的 token 成本与会话评测 PR 就是证据。

3. **垂类 Agent 扩张到教育，并且必须解决"Agent 知道用户此刻在看什么"。** OpenMAIC v1.1.0 把课堂问答从 director graph 换成 agent loop，允许学习者**指向某个 PPT 元素、互动组件或白板涂鸦**提问，并在提问时刻**采样互动页的实时状态**。对照 09-23 期 video-use 的"45M token → 12KB 文本 + 按需 PNG"，两者是同一难题的两种解法：**把无限的视觉上下文收敛成一次精准取值。**

4. **"额度"成为多产品并行时代的一等约束，并催生了跨产品额度工具。** codex-chatgpt-web 的核心卖点就是"用 ChatGPT Web 的额度，不耗 Codex 的额度"，V6 专门做了 Limits 页与 75% 预警，并**明确区分"本地估算"与"官方剩余额度"**。这与 09-25 期 orca 的"成本合计遗漏模型时显式声明"同源：**AI 工具的可信度越来越取决于它如何描述成本。**

5. **本地推理的竞争焦点从"能跑"转向"帮你选 + 帮你调"。** Magnitude 的差异线划得很清楚——Ollama / LM Studio 跑你选的模型，它**在下载前估算每个模型与量化在你机器上的 tok/s**，然后针对确切硬件调优（上下文大小、投机解码），并明确支持统一内存机型（DGX Spark、Strix Halo）与纯 CPU。配合 VoiceStudio（本地语音 + MCP），**本地优先的战场已经不在模型侧，而在"把本地能力接到 Agent 工具链上"这一侧。**

6. **"自托管替代昂贵 SaaS"的模式已经标准化。** OpenSEO 的公式是：**开源前端 + 自托管（推荐 Cloudflare 免费套餐）+ 自带数据源 API key（DataForSEO）+ 把加价率写进 README（托管版加收 28%）**。同一模式在本期与上期出现三次（OpenSEO、VoiceStudio、lap），说明用户已经接受了"UI 开源、数据费直付"这个交易结构。

7. **安全议题继续从"模型行为"转向"供应链与集成边界"。** 本期两个具体样本：OpenMAIC v1.1.1 修复 MinerU Cloud 的 SSRF（供应商返回的 URL 不可信、重定向须逐跳校验、上传不得跟随重定向、解压须设上限、地址策略拒绝不得重试、`::/96` 按内嵌 IPv4 归类），agent-skills 把"13.4% 技能含严重漏洞"变成可引用的数字并给出加固清单。**"让用户自带 base URL"的自托管产品，现在有了一份可直接照抄的检查项。**

8. **非 Agent 的 AI 基础层仍在稳定推进。** TimesFM v3.0（Google Research 时序基础模型）在 8 月底发布后**越用越热**，9 月中旬的提交几乎全在修 MLX 与 Torch 的数值一致性（stitching、RevIN、残差激活、NaN 处理）——**本地 Apple Silicon 推理是真实需求，且"和 Torch 对不上"是用户最不能忍的问题。** 时序预测作为 Agent 的一个工具（读表 → 预测 → 出图 → 结论）已经具备落地条件。

9. **公开数据 + 3D 可视化仍是独立热点，且"边界声明"已成标配。** gods-eye-view 用全公开数据源（ADS-B、AIS、TLE、地震台网、OSM、GFS/ECMWF）拼出可交互的写实地球，月增 3.7 万星，8 月曾登顶日榜与周榜。它把"交通是模拟的、摄像头位姿是粗估的、ALPR 只有位置没有图像、Bundled 数据非商用"全部写进 README——**公开数据产品必须先讲清哪些不是真数据。**

---

*报告生成时间：2026-09-28 14:20 (GMT+8)*
