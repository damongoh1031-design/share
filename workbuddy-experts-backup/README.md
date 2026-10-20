# WorkBuddy 专家备份

- 备份时间：2026-10-20
- 专家总数：22 个（含 Agent 单体专家与专家团）
- 总体积：70.5 MB
- 来源：$WORKBUDDY_CONFIG_DIR/plugins/marketplaces/（my-experts / experts / cb_teams_marketplace 三个市场）

## 安装状态（2026-10-20）

内置市场（experts）全部 **14 个专家已下载安装**到 `my-experts/plugins/` 并注册入 `my-experts/marketplace.json`，「我的专家」现共 **15 个**（14 内置 + 1 自建 rimworld-mod-guardian）。安装脚本：`install_builtin_experts.py`（可重复执行，幂等）。专家团市场（cb_teams_marketplace）的 6 个专家未安装，仍在原市场目录可直接使用。

| # | 来源市场 | 目录名 | 类型 | 角色数 | 体积(KB) | 简介 |
|---|---|---|---|---|---|---|
| 1 | my-experts | rimworld-mod-guardian | agent | 1 | 1700.9 | 专注《环世界》模组筛选、版本核验与冲突排障，结合作者说明和社区实测，规划稳定整合与存档保护方案。 |
| 2 | experts | customer-reply | agent | 1 | 150.5 | 客户发火别乱回：售前售后投诉退换四大场景话术直接出，按情绪配安抚策略，禁忌用语自动换，复制就能发。 |
| 3 | experts | deep-research | agent | 1 | 24.4 | - |
| 4 | experts | devops-security-experts | agent | 7 | 445.3 | - |
| 5 | experts | education-training-experts | agent | 4 | 448.2 | - |
| 6 | experts | engineering-tools-experts | agent | 4 | 3152.9 | - |
| 7 | experts | frontend-backend-experts | agent | 7 | 4012.1 | - |
| 8 | experts | gpt-researcher-team | team | 7 | 63.8 | 7 位专业角色分 5 阶段协作完成深度研究：初始调研 → 规划大纲 → 逐章深度研究（审稿修订循环） |
| 9 | experts | kdocs-knowledge-collector | agent | 1 | 430.4 | 把网页、消息、笔记等碎片内容沉淀为结构化知识资产：一键剪藏公众号与网页为云文档，AI 按主题聚合零散 |
| 10 | experts | llm-wiki | agent | 1 | 7.6 | - |
| 11 | experts | malaysia-hr-admin | agent | 1 | 40816.2 | 精通马来西亚招聘、劳动合同、薪酬福利、签证工签与社保，服务企业跨境人力行政咨询。 |
| 12 | experts | malaysia-legal | agent | 1 | 18425.6 | 精通马来西亚公司注册、合同、知识产权、行业准入与数据合规，服务跨境法务合规咨询。 |
| 13 | experts | operations-customer-experts | agent | 5 | 254.8 | - |
| 14 | experts | quality-testing-experts | agent | 8 | 445.6 | - |
| 15 | experts | sales-experts | agent | 8 | 654.4 | - |
| 16 | cb_teams_marketplace | a-share-analysis | agent | 7 | 61.1 | - |
| 17 | cb_teams_marketplace | agent-sdk-dev | agent | 2 | 12.6 | - |
| 18 | cb_teams_marketplace | ai-hedge-fund | agent | 21 | 38.6 | - |
| 19 | cb_teams_marketplace | deep-research | agent | 1 | 24.4 | - |
| 20 | cb_teams_marketplace | gaokao-advisor | agent | 1 | 461.7 | 辅助检索高考知识库并调用分数线、一分一段能力，整理带来源的真题、高校专业和志愿参考；同时提供全流程志 |
| 21 | cb_teams_marketplace | sheetagent | agent | 1 | 498.2 | - |
| 22 | cb_teams_marketplace | trading-agent | agent | 12 | 27.6 | - |

## 说明

- 每个 zip 为该专家目录的完整原样打包（含 .codebuddy-plugin、agents/、skills/、avatars 等）。
- `my-experts` 为自己创建的专家；`experts` / `cb_teams_marketplace` 为内置市场专家（可重新下载，备份用于离线保留）。
- ⚠️ `experts__malaysia-hr-admin.zip`（40MB）与 `experts__malaysia-legal.zip`（18MB）含商业电话号数据集（CSV/duckdb），源自 OSINT 项目数据，属敏感数据。
- 逐字段元数据见 manifest.json。