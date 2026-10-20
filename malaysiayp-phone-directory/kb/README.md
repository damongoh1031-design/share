# KB 索引

工作区沉淀的可复用结论 / 数据 / 操作步骤。命名按主题，不按日期；同主题原地更新并递增 `version`。

| 文档 | 主题 | 版本 | 更新 |
|---|---|---|---|
| [goose-report-api-verification.md](goose-report-api-verification.md) | 研究报告的 API 级复核方法论 + goose 权威事实快照（2026-10-15）：14 款竞品实时数据、v1.54.0 发布物逐条分类（Linux 占 24/40）、3 处实质错误复盘（排名算错 / 口径混淆 / Flatpak 遗漏）、11 条坑 | 1.0 | 2026-10-15 |
| [opencode-go-third-party-api.md](opencode-go-third-party-api.md) | OpenCode Go API 供第三方客户端调用：`x-opencode-session` 硬门槛、端点别名与协议分流、客户端三档可用性、**Goose 原生接入**、Open WebUI v0.12.2 接入（`{{CHAT_ID}}` 模板）、NewAPI 中转请求头覆盖、实测报错矩阵 | 1.2 | 2026-10-15 |
| [ai-subscription-20usd-2026.md](ai-subscription-20usd-2026.md) | 20 美元档 AI 订阅横评事实库：v4.2 四榜单交叉（LiveBench 2.0 / CursorBench 4.0 / Arena / AA）+ ChatGPT Go 档位模型权限 | 7 | 2026-10-15 |
| [workbuddy-user-skills-migration-bundle.md](workbuddy-user-skills-migration-bundle.md) | WorkBuddy 资产跨 IDE 迁移打包：skills（48 个）+ PAT + 专家包（6 包 26 agents），含去密、`_work`/`.in_use` 剔除、恢复步骤与踩坑 | 1.1.0 | 2026-10-14 |
| [db1-shopee-driver-runbook.md](db1-shopee-driver-runbook.md) | DB1 电话反查驱动器运行手册：gog token / 沙箱代理 / stdout 编码四道关卡 + 脱离会话启动（WMI+VBS，被拦时用 `schtasks /sc once`）+ 持久循环 + 第二阶段（1 万行以后）的 `--max-rows 20000`、失控循环抢文件、父子进程误判为重复循环、定时任务 `validUntil` 过期；**gog 重授权：`--remote --step 1/2` state 机制不可靠（两种报错）→ 改用直连 Google 换 refresh_token + `gog auth import --force`（实测成功）**；**schtasks 拉起的驱动器也会随会话结束被 `^C` 杀掉（判活三件套）、状态文件只在整轮退出时写** | 11 | 2026-10-20 |
| [db1-driver-jsonl-duplicate-recovery.md](db1-driver-jsonl-duplicate-recovery.md) | DB1 反查驱动器因残留 JSONL 重复行导致写前 assert 中止与幂等恢复 | 1 | 2026-10-09 |
