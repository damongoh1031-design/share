# KB 索引

工作区沉淀的可复用结论 / 数据 / 操作步骤。命名按主题，不按日期；同主题原地更新并递增 `version`。

| 文档 | 主题 | 版本 | 更新 |
|---|---|---|---|
| [goose-docs-zh-translation-pipeline.md](goose-docs-zh-translation-pipeline.md) | goose 官方资料中文手册全量翻译流水线：**33 章 / 397 页面节 / 2,764,724 B（源 2,793,527 B 的 99%）** 完成快照 —— 文档站正文 173 页 + **博客 112 篇** + **Recipe 模板 67 个** + 仓库治理 16 篇 + 文档站工程 29 个；7 步流程（Trees API 抓取 → groups 分章 → 写作契约 → 并行子代理 → **围栏感知审计** → README+完整版 → 哈希复核）、审计五项判据、**围栏感知解析的闭围栏三条件**、**11 条坑**（**4 空格缩进围栏致配对错位**、**YAML 内嵌缩进围栏致 Markdown 提前闭合→外层升级 4 反引号**、纯行计数≠配对计数、模板页 `](/)` 占位链、体积判据 90–130%、`git ls-tree` 中文名八进制转义须 `-z`、目录镜像覆盖、子代理分片临时文件） | 1.2 | 2026-10-15 |
| [goose-vs-generic-workbench-capability-mapping.md](goose-vs-generic-workbench-capability-mapping.md) | goose 能力对标速查：**术语映射表**（Extensions/Plugins/Hooks/Skills/Recipes/Subagents/**Custom Agents**/Slash Commands ↔ 通用工作台）、Recipes 对标、MCP 四条添加途径、Skills 增删改、**对标「专家团」= Custom Agents**、多模型只能切换不能同屏、plan 走 RPI Recipe（无内建 planner）、**三层循环步数**（主 1000 / subagent 25 / Ralph 10）、**工具 < 25 性能拐点** + 4 种权限模式、**shell 默认免批准且以用户权限运行（sudo 取决于 sudoers）**、渲染能力（HTML ✅ / PDF ❌ 只能读）、**无自研 RAG 栈**（替代方案 6 项对照）+ 15 条坑；v1.2 记录中文手册全量完成（22/22 章、173 页、commit 143193e） | 1.2 | 2026-10-15 |
| [goose-report-api-verification.md](goose-report-api-verification.md) | 研究报告的三级复核方法论（API → 官方文档 → 源码）+ goose 权威事实快照（2026-10-15）：14 款竞品实时数据、v1.54.0 发布物逐条分类（Linux 占 24/40）、官方文档库全量抓取法（173 篇 → 14 内置扩展 / 73 MCP / 20+ CLI 子命令 / 上下文参数 / GDK / Roaming）、**源码全量文件树枚举法（3,038 文件）+ code search 判定"计划 vs 既成事实" + 发布产物版本间 diff**、8 处源码 vs 文档落差、3 处实质错误复盘、26 条坑 | 1.2 | 2026-10-15 |
| [opencode-go-third-party-api.md](opencode-go-third-party-api.md) | OpenCode Go API 供第三方客户端调用：`x-opencode-session` 硬门槛、端点别名与协议分流、客户端三档可用性、**Goose 原生接入**、Open WebUI v0.12.2 接入（`{{CHAT_ID}}` 模板）、NewAPI 中转请求头覆盖、实测报错矩阵 | 1.2 | 2026-10-15 |
| [ai-subscription-20usd-2026.md](ai-subscription-20usd-2026.md) | 20 美元档 AI 订阅横评事实库：v4.2 四榜单交叉（LiveBench 2.0 / CursorBench 4.0 / Arena / AA）+ ChatGPT Go 档位模型权限 | 7 | 2026-10-15 |
| [workbuddy-user-skills-migration-bundle.md](workbuddy-user-skills-migration-bundle.md) | WorkBuddy 资产跨 IDE 迁移打包：skills（48 个）+ PAT + 专家包（6 包 26 agents），含去密、`_work`/`.in_use` 剔除、恢复步骤与踩坑 | 1.1.0 | 2026-10-14 |
