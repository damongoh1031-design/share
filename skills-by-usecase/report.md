# skills.sh 按用途选型清单（每用途一个最优解 · 去重版）

> **这份清单要解决什么**：skills.sh 上有 **176 个上榜 skill + 102 个官方厂商的数千个官方 skill**，同一个用途往往有 3-5 个候选（比如「写测试」至少有 `tdd` 和 `test-driven-development` 两个）。这份清单**为每个用途只留一个**，并明确标注「不要同时装什么」。
>
> **核验方式**：2026-10-14 一手抓取 skills.sh 的 **176 条 All Time 榜单**、**8 个 Topics 分类页**、**102 个官方厂商列表**、**50 条安全审计记录**，以及 20+ 个 skill 详情页原文。所有安装量、审计评级均为实测。
>
> **配套文件**：`report.html`（可视化）、`data/use-case-matrix.json`（用途→推荐矩阵）、`data/topics.json`（8 个分类全量）、`data/official-creators.json`（102 厂商）、`data/audits.json`（50 条审计）、`data/leaderboard.json`（176 条榜单）

---

## 〇 三条使用原则

**① 一个用途只装一个。** 重叠的 skill 会让 agent 重复劳动、浪费 context，还会互相干扰（比如两个 TDD skill 都要求「先写测试」，agent 会不知道该听谁的）。

**② 先看用途，再看安装量。** 安装量高只说明流行，不代表适合你的用途。`find-skills`（3.8M）是入口，但它在「写测试」这个用途上毫无用处。

**③ 装之前必看安全审计。** 实测 50 条审计记录里，**Gen Agent Trust Hub 有 3 个 Med Risk、Snyk 有 8 个 Med Risk + 1 个 High Risk**。详见第五章。

---

## 一 用途 → 唯一推荐（总表）

### A 编程开发

| 用途 | 唯一推荐 | 安装量 | 它解决什么 |
|---|---|---|---|
| **开工前对齐需求**（防返工） | `grill-me` | 1.4M | AI 编程最高频失败模式：它做的不是你要的 |
| **统一领域语言**（命名/术语） | `domain-modeling` | 816.5K | agent 用 20 个词说 1 个词的事，token 和可读性双输 |
| **架构设计纪律** | `codebase-design` | 792.3K | 提供 module/interface/depth/seam 词汇，防止说成「component/service」 |
| **架构体检 / 找重构候选** | `improve-codebase-architecture` | 1.1M | agent 加速编码也加速软件熵增，需定期体检 |
| **写测试** | `tdd` | 1.1M | AI 写的测试测实现细节，一重构就全红 |
| **纠错 / 难 bug** | `diagnosing-bugs` | 777.5K | 难 bug 靠猜猜不出来，强制先建稳定复现的反馈回路 |
| **代码审查** | `code-review` | 729.7K | 两轴审查：编码规范 + 是否忠实实现原 spec |
| **需求 → 实现全流程** | `implement` | 718.4K | 按 spec 施工，在约定接缝跑 tdd，收尾跑 code-review |
| **超大工程规划** | `wayfinder` | 664.8K | 规划超过一个 agent session 容量的大块工作 |
| **原型验证** | `prototype` | 934.3K | 用一次性原型回答设计问题，别直接写进正式代码 |
| **TypeScript 类型设计** | `typescript-advanced-types`（wshobson） | — | 泛型约束/条件类型/映射类型/模板字面量等高级模式 |
| **PR 撰写** | `pr` | — | PR 正文形态：最小可视化摘要 + 前后证据 + 合并风险评级 |
| **Git 危险操作护栏** | `git-guardrails-claude-code` | 463.7K | 防止 agent 执行危险 git 命令 |
| **合并冲突** | `resolving-merge-conflicts` | 551.0K | 冲突解决流程 |
| **复盘改进 agent 环境** | `retro` | 225.1K | 建议改进导航/自动检查/规范/steering 文件 |

### B 办公

| 用途 | 唯一推荐 | 说明 |
|---|---|---|
| **飞书全家桶** | **飞书官方 22 件套**（入口 `lark-doc`） | 单组织 16.9M 安装，全站最大官方生态 |
| **Word 文档** | `docx`（Anthropic 官方） | 驱动 Claude 生产环境文档能力 |
| **PDF 处理** | `pdf`（Anthropic 官方） | 读取/提取/合并/拆分/表单 |
| **PPT** | `pptx`（Anthropic 官方） | 创建/解析/编辑幻灯片 |
| **Excel / 表格** | `xlsx`（Anthropic 官方） | 表格为主输入输出时 |
| **文档共创** | `doc-coauthoring` | 结构化文档共创工作流 |
| **内部沟通文稿** | `internal-comms` | 各类内部沟通格式 |
| **Notion** | `makenotion/skills`（官方，23 skill） | Notion 官方 |
| **artifact 套主题** | `theme-factory` | 10 个预设主题（幻灯片/文档/HTML 落地页） |
| **Slack 动画 GIF** | `slack-gif-creator` | 含约束、校验工具、动画概念 |

### C 网页 / 搜索 / 数据获取

| 用途 | 唯一推荐 | 安装量 | 它解决什么 |
|---|---|---|---|
| **agent 操作浏览器** | `agent-browser` | 1.1M | CDP + 无障碍树快照 + `@eN` 元素引用，**token 高效** |
| **需要视觉理解的浏览** | `browser-use`（官方，5 skill） | — | 基于「看到什么」交互，适合纯视觉判断场景 |
| **写 / 跑浏览器测试** | `playwright-cli`（microsoft 官方） | — | 40+ 命令，多浏览器 + 持久 profile + 网络 mock + 追踪 |
| **网页抓取 / 提取 / 监控** | `just-scrape`（scrapegraphai） | 245.0K | **五合一**：search / scrape / extract(JSON) / crawl / monitor |
| **网页搜索** | `tavily-ai/skills`（官方，20 skill） | — | 搜索 API 官方 |
| **网页 → Markdown** | `firecrawl/cli`（官方，286 skill） | — | 官方 CLI，抓取 → LLM 友好格式 |
| **带引用的研究** | `research` | 658.9K | 后台 agent 跑研究，每条结论溯源到一手资料 |

### D 设计 / 前端 / 移动端

| 用途 | 唯一推荐 | 安装量 | 它解决什么 |
|---|---|---|---|
| **生成有品味的 UI** | `frontend-design`（Anthropic 官方） | 985.0K | 拒绝「AI 味」，先定美学方向再写代码 |
| **UI 规范审查** | `web-design-guidelines`（vercel-labs） | 734.2K | 100+ 规则：a11y / 性能 / UX / i18n |
| **设计批评 / 去 AI slop** | `impeccable/critique`（pbakaus） | — | 对照 AI 生成设计反模式，10 个维度结构化批评 |
| **上线前打磨** | `impeccable/polish`（pbakaus） | — | 对齐/间距/一致性/交互态/微交互的最终质检 |
| **设计系统参考** | `ui-ux-pro-max`（nextlevelbuilder） | 395.4K | 50+ 风格 / 161 调色板 / 57 字体对 / 99 UX 规则 / 10 技术栈 |
| **从网站提取设计令牌** | `extract-design-system`（arvindrk） | — | Playwright 逆向出色彩/字体/间距/圆角/阴影 → JSON + CSS |
| **React / Next 性能** | `vercel-react-best-practices` | 799.2K | 40+ 规则 / 8 类，按影响排序 |
| **Next.js App Router** | `next-best-practices`（vercel-labs） | — | App Router / 服务端组件 / 缓存 API / 部署 |
| **组件库** | `shadcn`（shadcn/ui 官方） | 271.1K | shadcn/ui |
| **Expo 原生 UI** | `building-native-ui`（Expo 官方） | — | Expo Router + Apple HIG 对齐 |
| **React Native** | `vercel-react-native-skills` | 240.2K | RN 最佳实践 |
| **静态视觉作品**（海报/PNG/PDF） | `canvas-design`（Anthropic 官方） | — | 用设计哲学创建视觉作品 |
| **算法 / 生成艺术** | `algorithmic-art`（Anthropic 官方） | — | p5.js + 种子随机 + 交互参数 |
| **品牌规范套用** | `brand-guidelines`（Anthropic 官方） | — | 官方品牌色与字体 |

### E 媒体生成

| 用途 | 唯一推荐 | 安装量 | 说明 |
|---|---|---|---|
| **视频制作（全套）** | `hyperframes`（heygen 官方，21 skill） | 961.9K | HTML/CSS → 确定性 MP4。路由器 + 10 创建工作流 + 4 领域技能 |
| **用 React 做视频** | `remotion-best-practices`（remotion-dev 官方） | 615.1K | 30+ 规则文件：动画/音频/字幕/3D/图表 |
| **图像生成** | `ai-image-generation`（prime-skills/runcomfy） | 377.3K | ⚠️ 同名 5 个 owner，选官方 runcomfy |
| **图生视频 / 视频编辑** | `image-to-video` / `video-edit`（runcomfy） | 432.3K / 434.1K | 同属 runcomfy 官方套装 |
| **音乐生成** | `ai-music`（prime-skills/runcomfy） | 363.3K | — |
| **语音合成 TTS** | `elevenlabs/skills`（官方，12 skill） | — | ElevenLabs 官方 |
| **语音转写 ASR** | `deepgram/skills`（官方，22 skill） | — | Deepgram 官方 |
| **专业视频生成** | `runwayml/skills`（官方，32 skill） | — | Runway 官方 |
| **视频渲染** | `remotion-dev/skills`（官方，19 skill） | — | 与 hyperframes 二选一（见第三章） |

### F 数据 / 后端 / 云（按你的技术栈选一个）

| 技术栈 | 唯一推荐 | 官方 skill 数 |
|---|---|---|
| **Postgres / Supabase** | `supabase-postgres-best-practices` | 17 |
| **Firebase** | `firebase-basics` | 55 |
| **Neon** | `neon-postgres` | 22 |
| **MySQL / PlanetScale** | `planetscale/database-skills` | 8 |
| **DuckDB 分析** | `duckdb/query` | — |
| **Convex** | `convex-quickstart` | 9 |
| **ORM** | `prisma` 官方 | 95 |
| **认证** | `clerk` 官方 | 31 |
| **密钥管理** | `bitwarden` 官方 | 65 |
| **支付** | `stripe/ai` 官方 | 11 |
| **Azure** | `microsoft/azure-skills` | **582** |
| **AWS** | `aws/agent-toolkit-for-aws` | 99 |
| **Cloudflare** | `cloudflare/skills` | 138 |
| **Vercel 部署** | `deploy-to-vercel` | — |
| **IaC** | `pulumi` 或 `hashicorp` | 32 / 74 |
| **可观测性** | `datadog-labs` / `getsentry`(302) / `langfuse` / `posthog`(262) / `signoz` | — |
| **数据管道** | `dagster-io`(53) / `dbt-labs`(14) | — |
| **功能开关** | `launchdarkly` 官方 | 68 |
| **邮件发送** | `resend` 官方 | 13 |
| **工作流自动化** | `n8n-io` 官方 | 41 |
| **CMS** | `sanity-io`(48) / `contentful`(7) / `contentstack`(21) | — |
| **电商** | `shopify`(37) / `medusajs`(30) | — |
| **地图** | `mapbox` 官方 | 24 |
| **实时音视频** | `livekit` 官方 | 1 |
| **时序数据** | `tinybirdco` 官方 | 4 |
| **缓存 / 队列** | `redis` 官方 | 15 |
| **向量库** | `pinecone-io` 官方 | 27 |
| **MCP 开发** | `mcp-builder`（Anthropic 官方） | — |
| **MCP 使用 / 构建** | `mcp-use` 官方 | 6 |

### G 营销 / 增长（`coreyhaines31/marketingskills` 有 21 个）

| 用途 | 唯一推荐 |
|---|---|
| **SEO 审计** | `seo-audit` |
| **文案撰写** | `copywriting` |
| **营销心理学** | `marketing-psychology` |
| **社媒内容** | `social-content` |
| **内容策略** | `content-strategy` |
| **程序化 SEO** | `programmatic-seo` |
| **定价策略** | `pricing-strategy` |
| **落地页转化（CRO）** | `page-cro` |
| **发布策略** | `launch-strategy` |
| **结构化数据** | `schema-markup` |
| **邮件序列** | `email-sequence` |
| **付费广告** | `paid-ads` |
| **竞品对比页** | `competitor-alternatives` |
| **埋点分析** | `analytics-tracking` |
| **Reddit 获客** | `reddit-automation`（925.5K） |

### H 研究 / 学习 / 元技能

| 用途 | 唯一推荐 | 安装量 |
|---|---|---|
| **找 skill** | `find-skills` | 3.8M |
| **造 skill** | `skill-creator`（Anthropic 官方） | 405.1K |
| **给 agent 写文档** | `writing-for-agents` | 414.2K |
| **带引用研究** | `research` | 658.9K |
| **教学（跨会话）** | `teach` | 808.1K |
| **学术论文上下文** | `paper-context-resolver`（rigorpilot） | 457.0K |
| **上下文交接** | `handoff` | 979.1K |
| **头脑风暴** | `brainstorming`（superpowers） | 391.2K |
| **对话 → spec** | `to-spec` | 661.4K |
| **spec → 工单** | `to-tickets` | 655.3K |
| **issue 分流** | `triage` | 938.7K |
| **多 agent 编排** | `subagent-driven-development` | 227.1K |
| **并行 agent** | `dispatching-parallel-agents` | — |
| **多 agent 运行时** | `stablyai/orca`（orchestration） | 289.3K |
| **提问澄清** | `wait-what` | 399.5K |
| **决策问卷** | `to-questionnaire` | 450.2K |
| **浏览器截图测试 web 应用** | `webapp-testing`（Anthropic 官方） | — |

### I 效率 / 成本

| 用途 | 唯一推荐 | 安装量 | 说明 |
|---|---|---|---|
| **省 token（输出+输入）** | `caveman` | 572.4K | input token 少 33.2%，有 Adobe/JetBrains/Elastic 三方验证 |
| **压缩工具输出 / 日志 / RAG chunk** | `headroomlabs-ai/headroom` | — | JSON 省 60-95% token |
| **项目知识图谱记忆** | `codebase-memory-mcp` | 46,547★ | 158 种语言，亚毫秒级 |
| **Markdown 知识图谱** | `iwe` | 1,771★ | LSP + CLI + MCP 记忆 |

---

## 二 去重决策表（二选一场景）

**这是本文最有实用价值的部分。** 以下 13 组 skill 功能重叠，**每组只装一个**：

| # | 冲突组 | ✅ 选它 | ❌ 别装 | 理由 |
|---|---|---|---|---|
| 1 | **整套方法论** | `mattpocock/skills` | `obra/superpowers` | superpowers **自动触发**（省心），mattpocock **手动精细控制**（可控）。两者 `tdd`/`test-driven-development`、`code-review`/`requesting-code-review` 完全重叠 |
| 2 | 写测试 | `tdd`（1.1M） | `test-driven-development`（249.1K） | 同一作者体系内，`tdd` 安装量高 4.4 倍；mattpocock 版有「接缝（seam）」这一核心概念 |
| 3 | 需求对齐 | `grill-me`（1.4M） | `grilling`（907.9K） | `grilling` 是 `grill-me` 的**底层引擎**，装 `grill-me` 会自动调用它 |
| 4 | 需求对齐（含文档） | `grill-with-docs`（1.2M） | — | 与 `grill-me` **互补不冲突**：多出构建 GLOSSARY.md + ADR |
| 5 | 交接 | `handoff`（979.1K） | `claude-handoff`（384.0K） | `handoff` 是正式版，含自动脱敏 + 建议技能列表 |
| 6 | 代码审查 | `code-review`（729.7K） | `requesting-code-review`（251.3K） | mattpocock 版是**两轴并行审查**，更完整 |
| 7 | 调试 | `diagnosing-bugs`（777.5K） | `systematic-debugging`（291.8K） | mattpocock 版有「先建稳定复现回路」的硬约束 |
| 8 | 浏览器操作 | `agent-browser`（1.1M） | `browser-use`（—） | **除非**你要纯视觉判断。agent-browser 用无障碍树 + `@eN` 引用，token 更省 |
| 9 | 移动端设计 | `building-native-ui`（Expo 官方） | `design-mobile-apps`（**Snyk High Risk**）、`sleek-design-mobile-apps` | 前者是官方 + 免费；后两个走第三方付费 API 且**有高危审计** |
| 10 | 前端设计生成 | `frontend-design`（Anthropic，985K） | `design-taste-frontend`（leonxlnx，606.8K） | 官方出品，且 `leonxlnx/taste-skill` 一家 13 个 UI skill 上榜，属商业推广驱动 |
| 11 | 视频 | `hyperframes`（heygen，961.9K） | `remotion-dev/skills` | **除非**你团队已用 React/Remotion。hyperframes 是 HTML/CSS 路线，Remotion 是 React 路线 |
| 12 | 视频生成 | `prime-skills/runcomfy-agent-skills` | 其余 6 个同名 `ai-video-generation` | 同一 skill 被 **7 个 owner** 重复发布（magentosh、101-skills、qu-skills、its-a-skill-issue、bankai-skills、skills-shell），选官方 |
| 13 | 设计系统 | `ui-ux-pro-max`（395.4K） | `tailwind-design-system`（wshobson） | 前者覆盖 10 个技术栈 + 161 调色板，更全 |

### 一个必须注意的「隐性重复」

**mattpocock 的 `codebase-design` 和 `improve-codebase-architecture` 不是重复，是配合关系**：

- `codebase-design` = **词汇与纪律**（module / interface / depth / seam / adapter / leverage / locality）
- `improve-codebase-architecture` = **执行体检**，且它**明确要求**先调用 `codebase-design` 拿词汇

所以这两个要**一起装**。原文：*"Call the Skill tool with 'codebase-design' for the architecture vocabulary... Use these terms exactly in every suggestion, and don't drift into 'component,' 'service,' 'API,' or 'boundary.'"*

---

## 三 你没提到的 12 个高频场景

以下场景在 skills.sh 上有**大量官方 skill 支撑**，但普通用户很少想到：

### ① 云平台运维（官方 skill 数量惊人）

| 厂商 | 官方 skill 数 |
|---|---|
| **NVIDIA** | **1,176** |
| **Microsoft Azure** | **582** |
| **AWS** | 99 |
| **Cloudflare** | 138 |
| HashiCorp | 74 |
| LaunchDarkly | 68 |
| Pulumi | 32 |
| OpenShift | 24 |
| Modal Labs | 1 |

**为什么值得注意**：Azure 官方有 **51 个仓库、582 个 skill**——涵盖 compute / kubernetes / rbac / cost / reliability / compliance / quotas / messaging / cloud-migrate / enterprise-infra-planner。**这已经不是「技能」，是完整的云运维知识库。**

### ② 可观测性与运维（SRE 场景）

| 厂商 | skill 数 | 用途 |
|---|---|---|
| **getsentry** | **302** | 错误追踪 |
| **posthog** | **262** | 产品分析 |
| **Datadog** | 43 | 监控 |
| Langfuse | 23 | LLM 可观测 |
| SigNoz | 13 | APM |
| Dash0 | 4 | 可观测 |
| Axiom | 12 | 日志 |

### ③ 数据管道与 ETL

`dagster-io`（53 skill）、`dbt-labs`（14）、`temporalio`（7，工作流编排）、`tinybirdco`（4，时序）、`duckdb`（分析查询）

### ④ 认证 / 支付 / 密钥（合规敏感场景）

`clerk`（31）、`auth0`（34）、`better-auth`（13）、`stripe`（11）、`coinbase`（29，加密钱包）、`whopio`（1）、**`bitwarden`（65，密钥管理）**

### ⑤ 内容管理与电商

`sanity-io`（48）、`contentful`（7）、`contentstack`（21）、`webflow`（37）、`wix`（23）、`wordpress`（18）、`shopify`（37）、`medusajs`（30）

### ⑥ 移动端原生开发

`expo`（18，含 `building-native-ui` / `native-data-fetching` / `expo-tailwind-setup` / `upgrading-expo`）、`flutter`（88）、`callstackincubator`（21）、`kotlin`（4）

### ⑦ 前端生态框架

`nuxt`（7）、`sveltejs`（3）、`facebook/react`（14）、`vercel/ai`（131，AI SDK）、`vercel/turborepo`（1）、`shadcn/ui`（1）

### ⑧ 语音与音频

`elevenlabs`（12，TTS）、`deepgram`（22，ASR）、`livekit`（1，实时音视频）、`runwayml`（32，视频生成）

### ⑨ 数据可视化 / 3D / 图表

`tldraw`（19，无限画布）、`mapbox`（24，地图）、`google-labs-code/stitch-skills`（30，UI 生成）

### ⑩ 邮件与通知

`resend`（13，事务邮件）、`brave`（26，搜索）、`tavily-ai`（20，搜索）

### ⑪ AI/ML 工程

`huggingface`（45）、`nvidia`（1,176）、`pytorch`（14）、`langchain-ai`（86）、`mastra-ai`（19）、`rivet-dev`（11）、`google-gemini`（29）、`openai`（278）

### ⑫ 测试与质量门禁（多形态）

`coderabbitai`（6，AI 代码审查）、`semgrep`（6，静态分析）、`antithesishq`（17，模糊测试）、`currents-dev`（Playwright 最佳实践）、`microsoft/playwright-cli`

---

## 四 四个「值得单独说」的 skill

### 4.1 `caveman` —— 唯一有第三方学术验证的省钱 skill

**三方验证**（README 引用）：

| 来源 | 结果 |
|---|---|
| **Adobe Research**（CAVEWOMAN 论文引用本仓库） | 每模型成本降 1.4-2.4 倍，最高 **3 倍** |
| **Elasticsearch Labs** | 响应 token 少 **63.6%**，"Zero information loss" |
| **JetBrains**（86 个真实编码任务配对 A/B） | **无质量损失**（p = 0.82），输出 token 少 8.5% |

**六个可独立开关的组件**：Say less（63→20 token）、Read less（**input token 少 33.2%**）、Auto（比 Opus xhigh 便宜 **54%**）、Blocks（397→76 token）、Waste fixes、Browse（页面小 **129.8 倍**）

**一条重要设计边界**：*"Adobe: cavemanning **your** prompt makes answers worse, so caveman **never touches your prompt**."* —— 它只压缩输出和工具返回，从不改你的输入。

### 4.2 `ui-ux-pro-max` —— 设计参考的数据量最大

50+ 设计风格 · **161 调色板** · **57 字体配对** · 99 UX 指南 · 10 技术栈（React / Next.js / Vue / Svelte / SwiftUI / RN / Flutter / Tailwind / shadcn / HTML）· 25 种图表 · 161 种产品类型模式 · 覆盖网站/落地页/仪表盘/管理后台/电商/SaaS/作品集/博客/移动应用

**它和 `frontend-design` 的区别**：`frontend-design` 教 agent「怎么做出有品味的选择」，`ui-ux-pro-max` 给 agent「一个可查询的设计数据库」。**两者可共存**。

### 4.3 `just-scrape` —— 一个顶五个

五条核心命令，覆盖了网页数据获取的完整链条：

| 命令 | 用途 |
|---|---|
| `search` | 发现（找 URL） |
| `scrape` | 抓原始页面（markdown / HTML / 截图 / 链接 / 图片） |
| `extract` | AI 结构化 → **JSON（可选 schema 校验）** |
| `crawl` | 批量抓整站章节 |
| `monitor` | 定时变化追踪 |

**如果你的用途是「从网上拿数据」，这一个就够**，不用再装 firecrawl + tavily + 各种爬虫。

### 4.4 `impeccable` —— 把「设计质量」拆成 6 个可调用动作

pbakaus 的 impeccable 在 Design 主题里有 6 个 skill，覆盖设计工作流的不同阶段：

| Skill | 用途 |
|---|---|
| `critique` | 对照 AI 生成设计反模式做 10 维度结构化批评 |
| `polish` | 上线前最终质检：对齐/间距/一致性/交互态/微交互 |
| `bolder` / `quieter` | 视觉强度调节 |
| `delight` | 增加愉悦感 |
| `distill` | 简化提炼 |

**`critique` 的 10 个维度**：视觉层级、信息架构、情感共鸣、可发现性、构图、字体、色彩策略、状态处理、微文案、可供性。

---

## 五 安全审计：哪些别装

实测 50 条审计记录（排名按安装量）：

| 审计源 | 分布 |
|---|---|
| **Gen Agent Trust Hub** | 25 Safe / **3 Med Risk** / 22 Pending |
| **Socket** | 0 alerts（已审的 28 个）/ 22 Pending |
| **Snyk** | 19 Low Risk / **8 Med Risk** / **1 High Risk** / 22 Pending |

### 5.1 有风险的 skill（实测清单）

| Skill | 安装量 | Gen | Snyk | 判断 |
|---|---|---|---|---|
| **`design-mobile-apps`** | 799.9K | Safe | **🔴 High Risk** | **不建议装**。走 sleek.design 付费 API，星数仅 15 |
| `improve-codebase-architecture` | 1.1M | **🟡 Med** | **🟡 Med** | 全站第 5，但双中危。它是纯 Markdown 指令型，风险可能来自「要求跑 git 命令 + 创建 GitHub issue」 |
| `triage` | 938.7K | **🟡 Med** | **🟡 Med** | 双中危。风险可能来自「自动往 issue tracker 发评论」 |
| `hyperframes-animation` | 853.1K | **🟡 Med** | Low | 中危 |
| `find-skills` | 3.8M | Safe | **🟡 Med** | 全站第一，Snyk 中危——**因为它会执行 `npx skills add` 安装任意来源的 skill** |
| `agent-browser` | 1.1M | Safe | **🟡 Med** | 浏览器自动化天然需要宽权限 |
| `hyperframes-cli` / `hyperframes` / `hyperframes-registry` | 1.0M / 961.9K / 842.4K | Safe | **🟡 Med** | — |
| `reddit-automation` | 925.5K | Safe | **🟡 Med** | 涉及外部平台操作 |

### 5.2 飞书官方 22 个 skill 全部「Pending」

实测发现：`lark-doc`、`lark-base`、`lark-drive`、`lark-shared`、`lark-im`、`lark-calendar`、`lark-approval`、`lark-sheets`、`lark-wiki`、`lark-contact`、`lark-task`、`lark-slides`、`lark-mail`、`lark-whiteboard`、`lark-event`、`lark-openapi-explorer`、`lark-attendance`、`lark-minutes`、`lark-skill-maker`、`lark-workflow-meeting-summary`、`lark-workflow-standup-report`、`lark-vc` —— **全部是 Pending**（未完成审计）。

**判断**：它们是飞书官方（larksuite 团队）维护、MIT 开源，**来源可信**；但审计未完成，装前建议自己过一遍 SKILL.md。

### 5.3 一条实用的安全原则

> **「Med Risk」在 skills.sh 上几乎等同于「这个 skill 会做有副作用的操作」。**

纯文本指令型 skill（如 `grill-me`、`tdd`）基本都是 Safe/Low Risk；凡是 **Med Risk** 的，通常意味着它会：执行 shell 命令、调用外部 API、往第三方平台写数据、或安装其他 skill。

**这不是坏事**——`agent-browser` 装成 Safe 反而说明它没在做它该做的事。**关键是自己知道它要什么权限。**

---

## 六 数据可信度

### 6.1 来源分级

| 级别 | 来源 | 可信度 |
|---|---|---|
| **A 级（一手实测）** | skills.sh 176 条榜单 + 8 个 Topics + 102 官方厂商 + 50 条审计记录 + 20+ skill 详情页原始 HTML 解析 | **高** |
| **B 级（官方原文）** | 各仓库 README、SKILL.md frontmatter | 高 |
| **C 级（厂商自述）** | caveman 引用的 Adobe/JetBrains/Elastic 数据（**未独立复核论文**） | 中 |

### 6.2 本轮的关键发现（上一轮报告未覆盖的）

1. **skills.sh 有 8 个 Topics 分类**：React(6) / Next.js(7) / Design & UI(16) / Mobile(6) / Agent workflows(20) / Databases(13) / Testing(5) / Marketing(21)
2. **有 102 个官方厂商**，合计数千个官方 skill。**NVIDIA 1,176 个、Anthropic 605 个、Microsoft 582 个、GitHub 406 个、Sentry 302 个**
3. **有独立的 Audits 页**，给出 Gen/Socket/Snyk 三家评级（不是只有 Pass/Fail）
4. **每个 skill 页底部有 "Related skills"**，是发现同用途替代品的最佳入口
5. **有 Packs 功能**：可把多个 skill 打包成一个安装命令，但 pack 默认不公开
6. **官方 API 存在但需认证**：`https://skills.sh/api/v1/skills`，返回 401，需 Vercel OIDC token
7. **站内搜索是纯客户端渲染**，无法通过 URL 参数抓取

### 6.3 明确未核实 / 存疑项

1. **「去重」用途未找到专门的 skill。** 在 176 条榜单、8 个 Topics、102 个官方厂商中均未发现以「结果去重 / 来源去重」为核心功能的 skill。**目前这类工作由 agent 自身或研究类 skill（`research`、`last30days` 系列）承担。** 这是本次调研的一个明确缺口。
2. **各 skill 的实际使用效果**：本轮为**桌面调研 + 数据核验**，未逐个安装运行。
3. **Audits 页只覆盖 50 条**（按安装量排序的前 50），排名 51-176 的审计状态未收录。
4. **官方厂商的「skills 数」口径**：页面显示的是该 creator 所有仓库的 skill 总数（如 NVIDIA 48 repos / 1176 skills），**不等于每个都值得装**。
5. **`improve-codebase-architecture` / `triage` 的 Med Risk 具体原因**：未深挖，判断依据是 SKILL.md 描述的行为（跑 git 命令、创建 issue、发评论）。
6. **caveman 引用的 Adobe 论文（arXiv 2606.24083）**：未独立核验。

---

*报告生成：2026-10-14 ｜ 数据核验：skills.sh 176 条榜单 + 8 Topics + 102 官方厂商 + 50 条审计 + 20+ skill 详情页 ｜ 本机环境：Windows 11*
