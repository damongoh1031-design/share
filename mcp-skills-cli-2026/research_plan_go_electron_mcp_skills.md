# 研究计划：Go + Electron 开发中真正有助益的 Skills 与 MCP（2026-10）

## 一、问题拆解

用户核心诉求：不是"有哪些 MCP"的清单堆砌，而是"哪些对我写 Go / Electron 有**实际助益**"，并延伸到"软件工程全流程（框架、规划、除错、验证）必备的 skills 与 MCP"。

需要产出的关键信息：
1. Go 语言链路：官方/社区是否有权威 MCP（gopls、golangci-lint、Delve 调试、测试/覆盖率、pprof 性能分析、依赖与漏洞扫描、代码生成）
2. Electron 链路：主进程/渲染进程调试、CDP/DevTools 协议、Playwright/Puppeteer、TypeScript 语义层、打包签名、Electron 安全审计
3. 跨语言通用层：文档检索（Context7 类）、语义代码检索（Serena/LSP 类）、规划与任务分解、Git/PR 工作流、静态分析、错误监控、Issue 追踪
4. Skills 生态：Anthropic Agent Skills 规范现状、社区高价值 skill 包（TDD、code review、spec-driven development、superpowers、spec-kit、BMAD、OpenSpec 等）
5. 现实约束：宿主兼容性（Claude Code / Cursor / VS Code / WorkBuddy）、国内网络可达性、token 与性能成本、安全风险（MCP 供应链、prompt injection、工具投毒）

## 二、查询类型判定

**Breadth-first（广度优先）**。理由：Go 生态、Electron/前端生态、通用工程层、Skills 规范生态四条线彼此独立，可并行检索；但每条线内部需要一定深度（要判断"是否真能用、是否维护活跃、是否有坑"），因此每路配备 1 个高能力子代理，共 3 路并行，第 4 路（现实约束与安全）由主线自己完成综合。

## 三、分工

- Agent A：Go 语言生态（工具链 MCP / gopls MCP / lint / debug / test / pprof / 依赖安全）
- Agent B：Electron + TypeScript/Node 生态（CDP、Playwright、TS 语义、打包、安全审计）
- Agent C：通用软件工程 MCP 与 Skills 生态 + MCP 协议规范最新版本与安全议题
- 主线（我）：微信公众号中文信源检索（wechat-article-search skill，时间限定近 90 天），补齐国内视角、落地成本、选型矩阵与最终报告撰写

## 四、检索关键词与时间范围

- 英文：`Go MCP server gopls`、`golangci-lint MCP`、`delve MCP debugger`、`Electron MCP server`、`Chrome DevTools MCP`、`Playwright MCP`、`Context7 MCP`、`Serena MCP semantic code`、`agent skills spec`、`MCP specification 2026`、`MCP security risks`
- 中文：`MCP 推荐`、`Go 开发 AI 编程`、`Electron AI 调试`、`Claude Skills 实践`、`AI 编程 工作流`
- 时间范围：优先 2025-06 至 2026-10；MCP 规范版本、仓库 star/更新时间为硬性核验项
- 中文信源：wechat-article-search，`--days 120`

## 五、合成方式

1. 每路产出"可用清单 + 为什么有用 + 怎么配 + 局限/坑 + 来源链接"
2. 主线按"开发阶段"重排（立项与规划 → 编码 → 调试 → 测试验证 → 交付与运维），而非按语言罗列，这样才对用户有决策价值
3. 给出分级推荐：必装 / 场景化 / 观望，并标注成本与风险
4. 输出 Markdown 报告到工作区根目录
