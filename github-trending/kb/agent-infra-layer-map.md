---
id: agent-infra-layer-map
title: Agent 基础设施分层图：上下文 / 网关 / 技能 / UI / 专业工具
tags: [agent-infra, code-graph, llm-gateway, agent-skills, generative-ui, mcp, cost-control]
created: 2026-10-19
updated: 2026-10-19
version: 1.0.0
status: draft
source: GitHub trending 2026-10-19 快照 + 各项目 README / GitHub Release / API
confidence: 已核实（版本与机制）／自报（性能与压缩比）
---

# Agent 基础设施分层图

## 一句话结论

2026-10 的 agent 工具链已经分五层，每层都在从"能用"走向"可运维"：**上下文层**用显式图谱替代向量检索，**网关层**把订阅与免费额度当资源调度，**技能层**长出 inventory/doctor/lockfile，**UI 层**竞争输出语言，**专业工具层**用 provenance + bounded retry 换取不可逆操作的安全。

---

## 1. 分层与代表项目（2026-10-19）

| 层 | 解决什么 | 代表项目 | 关键机制 | 成熟度 |
|---|---|---|---|---|
| 上下文 / 代码理解 | 让模型"知道"代码库结构与跨文件关系 | Graphify（128k★，v0.9.92） | tree-sitter AST + 调用图 + Leiden 社区；边打 `EXTRACTED/INFERRED/AMBIGUOUS`；**无向量库** | 0.9.x，schema 三日两 bump |
| 模型接入 / 网关 | 多供应商路由、额度、成本、密钥 | OmniRoute（78k★）、otari（Mozilla，660★） | 前者 quota-aware fallback + token 压缩；后者虚拟 key + 预算 + 用量追踪 | OmniRoute 超高频发版；otari 0.x |
| 技能运行 / 运维 | 技能的安装、可见性、健康、版本 | lazyskills（561★）、ASPIRE（NVIDIA，554★） | 跨 agent 可见性矩阵 + `doctor --json`；ASPIRE 把"训练"定义为技能精炼 | 早期，单人/实验室维护为主 |
| 生成式 UI | 模型输出结构化界面而非纯文本 | OpenUI（11.9k★，Lang 1.0） | 组件库 → 生成系统提示词 → 流式 DSL → 渲染器 | lang-core 1.0，runtime 0.4.x |
| 专业工具 MCP | 在不可逆领域（EDA/CAD/运维）安全执行 | Konnect（KiCad，217 工具）、versus-incident（AI SRE） | 证据来源标注、变更说明、重试边界、reader/action 凭证分离 | 单点成熟，缺通用规范 |

---

## 2. 关键判断（可复用）

| # | 判断 | 证据 | 状态 |
|---|---|---|---|
| 1 | 代码 RAG 的价值在**结构**不在压缩；小仓库用图无收益 | Graphify 自报 52 文件 71.5x、6 文件 ~1x | 自报 |
| 2 | 上下文基础设施以 **skill** 而非 SDK 分发 | Graphify 提供 Claude Code / Cursor / Codex / Gemini CLI 四份技能；ASPIRE 用 `.claude/skills` + `.codex/skills` 交付复现流程 | 已核实 |
| 3 | 网关分化为两条路：免费额度套利 vs 成本治理 | OmniRoute（150+ 免费、quota fallback） vs otari（虚拟 key、预算） | 已核实 |
| 4 | 消费级订阅正在被接成 provider | TradingAgents v0.7.0 `chatgpt` provider 走 OpenAI 开源应用登录 | 已核实 |
| 5 | 反代从换 IP 升级到换 **TLS 指纹** | opencode2api v1.4.2 对齐官方 Bun 运行时握手；AIStudio2API 代理池 + 账户绑定 | 已核实 |
| 6 | 技能数量过了手工管理阈值 | lazyskills 专抓缺 SKILL.md / frontmatter 非法 / 断链 / 孤儿 lock / ghost skill | 已核实 |
| 7 | 生成式 UI 竞争从组件协议下沉到**输出语言** | OpenUI Lang 1.0 + React/Vue/Svelte/Angular runtime | 已核实 |
| 8 | 不可逆领域的 MCP 必须自带 provenance 与重试边界 | Konnect v0.13.0 "Live Truth / Bounded Recovery"；拒绝通不过自身安全检查的计划 | 已核实 |
| 9 | AI SRE 的可落地形态是"取证 + 门控"而非自动修复 | versus-incident 只读调查工具 + 审批动作绑定集群 + 凭证分离 | 已核实 |
| 10 | 主榜固化，增量在语言榜与版本事件 | 2026-10-19：周榜 10 条 / 月榜 20 条零新面孔 | 已核实 |

---

## 3. 可复用操作

### 3.1 代码图谱（Graphify）

```bash
pipx install graphifyy          # 包名是 graphifyy，不是 graphify（后者在回收中）
graphify install
# 在 Claude Code 里
/graphify .                     # 全量
/graphify . --update            # 只重抽改动文件
/graphify . --watch             # 代码保存即时重建（纯 AST，不调模型）
graphify hook install           # post-commit 自动重建
/graphify . --mcp               # 起 MCP stdio server
```

判据：仓库小于 ~10 个文件时不必上图谱，结构收益 > 压缩收益。

### 3.2 自托管网关（otari）

```yaml
# v0.28.0 起 provider key 必须显式具名
openai:
  api_key: ${OPENAI_API_KEY}
ollama:            # 无 key 供应商要留空条目
```

升级注意：未声明的 provider 直接报错；环境变量隐式兜底已取消。

### 3.3 技能体检（lazyskills）

```bash
lazyskills doctor                 # 只读，不改技能/lock
lazyskills doctor --json          # 给脚本或其他 agent 调
lazyskills find --json "browser automation"
```

判据：出现"装了但 agent 看不见"时，先跑 doctor 看可见性矩阵，不要重装。

### 3.4 生成式 UI（OpenUI）

```bash
npx @openuidev/cli@latest create --name genui-chat-app
```

链路：组件库 → 由组件库生成系统提示词 → 模型输出 OpenUI Lang → 流式渲染。

---

## 4. 坑与反直觉

| 坑 | 表现 | 处理 |
|---|---|---|
| PyPI 同名包 | `graphify` 名字在回收，实际包名 `graphifyy` | 认准包名，装错会拿到同名无关包 |
| 图谱缓存 schema 变动 | 0.9.91 / 0.9.92 连续 bump，升级后首次构建全量重抽 | 升级放到空闲时段 |
| 网关 `latest` | OmniRoute 单版 2,022 条变更 / 1,454 修复 | 必须 pin 版本 |
| 配置源切换 | otari v0.28.0 取消 env 隐式读取 | 升级前把每个 key 写进 config |
| 反代升级会话重算 | opencode2api 升级后进行中对话可能换 key/出口，上游缓存失效 | 别在长任务中途升级 |
| 免费流量协议变化 | 免费模型改走 HTTP/1.1，连接数上升 | 检查代理/连接池上限 |
| 技能"装了没生效" | 不同 harness 搜索路径不同，出现 ghost skill | 用可见性矩阵按 agent 查，不要看目录存在与否 |
| 论文复现 ≠ 验证 | ASPIRE 真机 recipe 是从演示会话蒸馏，非新验证 | 引用时标注来源 |
| 自报压缩比 | 71.5x / 67% / 15–95% 均为项目自述 | 用自己的语料复跑再引用 |

---

## 5. 未核实 / 存疑

- Graphify 的 71.5x token 压缩：仅项目自带 worked example，未独立复现。
- OmniRoute "375 providers / 150+ free / 1,400+ models"：项目自述，未逐家核对条款与限速。
- OpenUI "比 JSON 少 67% token"：未指定语料与组件库规模，无法直接外推。
- ASPIRE 的 99% / 97–100%：作者自报，benchmark 配置与 seed 未逐一复核。
- 订阅当 provider（TradingAgents `chatgpt`）的平台合规态度：未查证 OpenAI 对自动化框架使用消费级订阅的明文政策。
- opencode2api 的 TLS 指纹伪装在平台侧是否已被识别：无公开信息。
