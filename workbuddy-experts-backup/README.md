# WorkBuddy 专家备份

- 更新时间：2026-10-20（第三次刷新）
- 备份 zip 总数：59 个，总体积 163.5 MB
- 覆盖三个市场：my-experts（我的专家，29 个）/ experts（内置市场，23 个）/ cb_teams_marketplace（专家团市场，7 个专家）

## 我的专家（my-experts，已安装 29 个）

由内置市场 22 个 + 专家团市场 6 个 + 自建 1 个组成；内置市场 trading-agent（13 角色）因目录名被专家团版占用，未单独装入。

| # | 专家 | 角色数 | 来源市场 |
|---|---|---|---|
| 1 | a-share-analysis | 7 | 专家团市场 |
| 2 | agent-sdk-dev | 2 | 专家团市场 |
| 3 | ai-hedge-fund | 21 | 专家团市场 |
| 4 | customer-reply | 1 | 内置市场 |
| 5 | data-ai-experts | 8 | 内置市场 |
| 6 | deep-research | 1 | 内置市场 |
| 7 | design-experts | 9 | 内置市场 |
| 8 | devops-security-experts | 7 | 内置市场 |
| 9 | education-training-experts | 4 | 内置市场 |
| 10 | engineering-tools-experts | 4 | 内置市场 |
| 11 | engineering-workflow-skills | 1 | 内置市场 |
| 12 | frontend-backend-experts | 7 | 内置市场 |
| 13 | gaokao-advisor | 1 | 专家团市场 |
| 14 | gpt-researcher-team | 7 | 内置市场 |
| 15 | industry-service-experts | 5 | 内置市场 |
| 16 | kdocs-knowledge-collector | 1 | 内置市场 |
| 17 | llm-wiki | 1 | 内置市场 |
| 18 | malaysia-hr-admin | 1 | 内置市场 |
| 19 | malaysia-legal | 1 | 内置市场 |
| 20 | openspec-doc-team | 4 | 内置市场 |
| 21 | operations-customer-experts | 5 | 内置市场 |
| 22 | product-experts | 4 | 内置市场 |
| 23 | product-strategy-team | 6 | 内置市场 |
| 24 | quality-testing-experts | 8 | 内置市场 |
| 25 | rimworld-mod-guardian | 1 | 自建 |
| 26 | sales-experts | 8 | 内置市场 |
| 27 | sheetagent | 1 | 专家团市场 |
| 28 | spatial-computing-experts | 6 | 内置市场 |
| 29 | trading-agent | 12 | 专家团市场（内置版重名跳过） |

## 本次新增（2026-10-20 内置市场刷新）

内置市场今日新增 9 个专家，已全部装入我的专家并备份：

| 专家 | 角色数 | 体积(KB) |
|---|---|---|
| data-ai-experts | 8 | 457.7 |
| design-experts | 9 | 3828.1 |
| engineering-workflow-skills | 1 | 419.8 |
| industry-service-experts | 5 | 79.6 |
| openspec-doc-team | 4 | 1330.6 |
| product-experts | 4 | 4260.0 |
| product-strategy-team | 6 | 2031.0 |
| spatial-computing-experts | 6 | 11.8 |
| trading-agent | 13 | 33.5 |

## 文件清单

- dist/：59 个 zip，命名为 `<市场>__<专家名>.zip`，内容为该专家目录完整原样打包
- manifest.json：逐专家元数据（来源、体积、角色、安装状态）
- my-experts-marketplace.json：我的专家注册清单快照（恢复时需放回 my-experts/.codebuddy-plugin/）
- install_experts.py：从指定市场安装专家到 my-experts（幂等）
- install_builtin_experts.py：首轮内置市场安装脚本（历史留存）
- backup_experts.py：重新生成本备份

## 敏感数据提示

- my-experts 与 experts 下的 malaysia-hr-admin / malaysia-legal 各含一份商业电话号数据集（CSV/duckdb，源自 OSINT 项目），推送 public 仓库已获用户确认。
