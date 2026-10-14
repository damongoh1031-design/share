# 个人助理类 AI Agent 的 MCP 生态调研

> **调研问题**：在个人助理类软件（OpenClaw、Hermes Agent 等）上，最热门的 MCP 有哪些？社区公认「必装」的是什么？
>
> **核验方式**：所有 GitHub 量化指标均由主代理通过 GitHub REST API 于 **2026-10-14** 一手核验（81 个仓库直查 + 19 组关键词检索），不采用二手转述。
>
> **配套文件**：`report.html`（可视化）、`data/github-verified.json`（81 仓库原始核验数据）、`data/github-search.json`（19 组检索原始结果）、`data/verify_repos.py`（核验脚本，可复跑）

---

## 〇 结论速览

### 最重要的一个结论

**问「OpenClaw / Hermes 上必装什么 MCP」，这个问题本身预设错了一半。**

个人助理类软件分成两条截然不同的路线，它们的「扩展面」根本不是同一个东西：

| 路线 | 代表 | 扩展的载体 | MCP 的地位 |
|---|---|---|---|
| **Skills 优先** | **OpenClaw**（391,930★） | `SKILL.md` + Markdown 人格文件 | **配角**。能装，但官方与社区的精力都在 Skills 上 |
| **MCP 优先** | **Goose**（55,269★）、**Hermes Agent**（253,604★）、**DSH**（249,310★） | MCP server | **主角**，MCP 就是它的扩展模型 |

所以对 OpenClaw 用户，正确答案是「装 Skills」，不是「装 MCP」。对 Hermes / Goose / DSH 用户，MCP 才是主线。

**本机实证**：本机 `~/.openclaw/workspace/` 里躺着 `AGENTS.md`、`BOOTSTRAP.md`、`IDENTITY.md`、`SOUL.md`、`TOOLS.md`、`USER.md`、`HEARTBEAT.md` 七个 Markdown 文件，**一个 MCP 配置文件都没有**——这不是巧合，是设计。

### 通用核心「必装 5 件套」（跨框架硬共识）

无论用哪个个人助理框架，社区共识收敛到这五类能力。缺了它们，助理就是个会聊天的空壳：

| # | 能力 | 首选实现（已核验★） | 为什么必装 |
|---|---|---|---|
| 1 | **文件系统** | `@modelcontextprotocol/server-filesystem`（官方参考实现） | 助理的「手脚」，读写本地文件是其他一切的前提 |
| 2 | **网页抓取** | `mcp-server-fetch`（官方）/ Firecrawl（7,598★） | 没有它，助理的知识截止在训练日 |
| 3 | **持久记忆** | Knowledge Graph Memory（官方）/ `basic-memory`（4,169★）/ Graphiti（31,730★） | 个人助理的**灵魂**。没有跨会话记忆就只是聊天窗口 |
| 4 | **网络搜索** | Exa（5,126★）/ Brave Search（1,497★）/ Tavily | 抓取是「给 URL」，搜索是「找 URL」，两者不可互替 |
| 5 | **笔记/知识库** | Notion 官方（4,666★）/ Obsidian（4,476★） | 让助理的产出落到你自己的知识体系里，而不是消失在对话里 |

### 一句话警告

**个人助理是 MCP 生态里最危险的宿主**：它拿着你的文件系统权限、邮箱、日历、聊天记录。OpenClaw 已知 **CVE-2026-25253（1-Click RCE，CVSS 8.8）**、**CVE-2026-28363（沙箱逃逸，CVSS 9.9）**，ClawHub 上还爆发过 **ClawHavoc 供应链投毒（341 个恶意技能，投递 Atomic macOS Stealer）**。装 MCP / Skill 前先过一遍第六章的加固清单。

---

## 一 先纠正前提：个人助理 ≠ MCP 优先

### 1.1 OpenClaw 的真相：Skills 才是旗舰机制

OpenClaw（`openclaw/openclaw`，**391,930★**，MIT，2025-11-24 建仓，2026-10-14 仍在日更）是当前 GitHub 上星数最高的个人助理项目之一。但它的扩展哲学不是 MCP。

**MCP 在 OpenClaw 里怎么用**：

- 配置文件 `~/.openclaw/openclaw.json` 中的 `mcp.servers` 段
- Control UI（`http://127.0.0.1:18789/`）→ Settings → MCP → Add server
- CLI：`openclaw mcp add / doctor / status / probe / login / reload / configure`
- 传输支持：Streamable HTTP / SSE / Stdio
- 反向能力：`openclaw mcp serve`——把 OpenClaw 自己暴露成一个 MCP server 给别的客户端用

也就是说 MCP 支持是**完整且一等公民级**的。但——

**真正的旗舰是 Skills，通过 ClawHub 分发**：

- 注册表仓库：`openclaw/clawhub`（**9,508★**，MIT，官方描述就是 "Skill + Plugin Registry for OpenClaw"）
- 安装命令：`openclaw skills install @openclaw/demo`
- Skills 的载体是 `SKILL.md`，遵循 Agent Skills 开放标准（agentskills.io，2025-12-18 发布）

**本机一手实证**（`~/.openclaw/`）：

```
~/.openclaw/
├── skills/
│   └── playwriter -> /c/Users/Admin/.agents/skills/playwriter   ← 软链到共享技能目录
└── workspace/
    ├── AGENTS.md        ← 工作区宪法
    ├── BOOTSTRAP.md     ← 首次启动引导（用完即删）
    ├── IDENTITY.md      ← 助理的自我认知（名字/性格/emoji）
    ├── SOUL.md          ← 价值观与行为边界
    ├── TOOLS.md         ← 环境专属笔记（SSH 主机、摄像头名、TTS 音色）
    ├── USER.md          ← 关于用户本人
    ├── HEARTBEAT.md     ← 周期性自检任务
    └── .openclaw/workspace-state.json
```

**注意：整个 workspace 里没有任何 MCP 配置文件。** 扩展能力全部由「Markdown 文件 + Skills」承担。

本机 `AGENTS.md` 的会话启动协议原文：

> 1. Read `SOUL.md` — this is who you are
> 2. Read `USER.md` — this is who you're helping
> 3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context
> 4. **If in MAIN SESSION**: Also read `MEMORY.md`

以及一句非常能代表这套设计的话：

> **Text > Brain** 📝 — "Mental notes" don't survive session restarts. Files do.

本机 `TOOLS.md` 则明确划清了边界：

> Skills define _how_ tools work. This file is for _your_ specifics.
> Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and **share skills without leaking your infrastructure**.

**结论**：OpenClaw 的架构决策是「人格与知识用 Markdown 文件承载，能力用 Skills 承载，MCP 作为与外部世界对接的可选通道」。**所以不存在、也不会有权威的「OpenClaw 必装 MCP 清单」**——社区的能量全在 Skills 上。

### 1.2 OpenClaw 社区实际在装什么（Skills，非 MCP）

由于没有权威 MCP 榜单，社区共识落在 ClawHub 的 Skills 上。综合中文社区榜单（知乎、Datawhale 等）出现频率最高的：

| Skill | 作用 | 备注 |
|---|---|---|
| **skill-vetter / clawsec** | 安全扫描 | **第一个该装的**——见第六章 |
| `tavily-search` | 联网搜索 | 替代内置搜索 |
| `find-skills` | 技能发现 | 元技能，用来找别的技能 |
| `proactive-agent` | 主动行为 | 配合 HEARTBEAT.md 做定时自检 |
| `github` | GitHub 操作 | |
| `gog` | Google Workspace | |
| `automation-workflows` | 工作流编排 | |
| `bird` | 社媒/内容发布 | |
| `self-improving-agent` | 自我改进 | 把经验写回文件 |
| `feishu-doc` | 飞书文档 | 中国用户高频 |

ClawHub 生态的规模信号（已核验）：

- `openclaw/clawhub`：9,508★
- `mvanhorn/last30days-skill`：**64,191★**（跨 Reddit/X/YouTube/HN/Polymarket 的研究型 Skill，是 ClawHub 生态里星数最高的技能之一）
- `FreedomIntelligence/OpenClaw-Medical-Skills`：3,063★（医疗技能库）
- `YouMind-OpenLab/nano-banana-pro-prompts-recommend-skill`：1,875★
- `LeoYeAI/openclaw-backup`：659★（一键备份 workspace/凭证/技能/历史）

### 1.3 Hermes Agent：MCP 是一级公民，但配了「防膨胀」机制

Hermes Agent（`NousResearch/hermes-agent`，**253,604★**，MIT，2025-07-22 建仓）走的是完全相反的路线：**MCP 是核心扩展机制**。

**本机一手实证**（`%LOCALAPPDATA%/hermes/`）：`config.yaml` 达 **123,576 字节**，其中第 1523–1600 行是完整的 MCP 配置文档段。原文摘要：

```yaml
# MCP (Model Context Protocol) Servers
# Stdio servers (spawn a subprocess):
#   command / args / env
# HTTP servers (connect to a URL):
#   url / headers
#
# mcp_servers:
#   time:
#     command: uvx
#     args: ["mcp-server-time"]
#   filesystem:
#     command: npx
#     args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user"]
#   notion:
#     url: https://mcp.notion.com/mcp
#   github:
#     command: npx
#     args: ["-y", "@modelcontextprotocol/server-github"]
```

**Hermes 有三个设计细节，是整个 MCP 生态里最值得学的**：

**① `lazy` 懒加载**（config.yaml 原文注释）

> `lazy`: register the server's tools from the on-disk schema cache at startup and only spawn/connect it on the first tool call (default: false). Saves one child process per server in processes that rarely call tools.

即：启动时只从磁盘 schema 缓存登记工具，**首次真正调用才拉起子进程**。这是对「装多了启动就慢」的直接回应。

**② MCP 结果单独设溢流阈值**（config.yaml 原文注释）

> MCP tool results (tools named `mcp_*`) spill at a **tighter 50,000-char threshold** than the generic 100K default: MCP servers routinely return un-paginated 20-50K payloads that bloat context and slow every subsequent turn.

即：MCP 工具返回超过 5 万字符就落盘，上下文里只留预览 + 路径。**这是我在整个调研中见到的对「MCP 上下文膨胀」最工程化的解法**——它不是劝你少装，而是让你装了也不炸。

**③ Sampling 默认开启**（server-initiated LLM requests）

```yaml
# sampling:
#   enabled: true           # default: true
#   model: "gemini-3-flash" # override model (optional)
#   max_tokens_cap: 4096
#   max_rpm: 10
```

即允许 MCP server 反向请求 LLM，带 token 上限与限流。

**⚠️ 顺手指出一个陷阱**：Hermes 文档示例里写的是 `@modelcontextprotocol/server-github`——**这是已废弃的旧 npm 包**。现在应该用 `github/github-mcp-server`（33,601★，官方 Go 实现）。官方文档示例也可能过期，别照抄。

**Hermes 的人格文件体系**（与 OpenClaw 同构但更精简）：

- `SOUL.md`（667 字节）——本机原文开头：*"You are Hermes Agent, built by Nous Research. Be direct: match the length of your reply to the weight of the ask..."*
- `AGENTS.md`、`hermes-agent/`（完整源码 git 仓库，含 `README.zh-CN.md`）
- `memories/`、`sessions/`、`skills/`、`knowledge-base/`、`hooks/`、`cron/`、`bot_relay/`

注意 `bot_relay/` 与 `cron/`——**IM 中继 + 定时任务**，这是「个人助理」区别于「编码助手」的两个标志性目录。

### 1.4 三条路线的分野

| | **Skills 优先** | **MCP 优先** | **混合** |
|---|---|---|---|
| 代表 | **OpenClaw** | **Goose**、**Hermes**、**DSH** | LibreChat、LobeChat |
| 扩展单元 | `SKILL.md` | MCP server | 两者都支持 |
| 分发渠道 | ClawHub（9,508★） | MCP Registry / npm / PyPI | 各自市场 |
| 优势 | 轻、可读、可审查、无需进程 | 生态大、跨客户端复用 | 灵活 |
| 劣势 | 生态碎片化、无统一注册表 | 上下文膨胀、进程开销、供应链风险 | 概念复杂 |
| 星数（本体） | 391,930★ | 55,269★ / 253,604★ / 249,310★ | 45,656★ / 83,223★ |

**Goose 是最彻底的 MCP 优先者**：它的扩展模型就是「MCP 即扩展」，内置 70+ 扩展，并且是 **AAIF（Agentic AI Foundation）的创始项目与参考实现**。已核验：`block/goose` **已迁移至 `aaif-goose/goose`**（55,269★，Apache-2.0）——这个迁移本身就是 AAIF 落地的证据。

---

## 二 个人助理框架 MCP 成熟度分层

按「MCP 是否一等公民 + 是否有官方配置文档 + 是否处理了膨胀问题」三条标准分层：

### Tier 1 — MCP 成熟度最高

| 框架 | 星数 | License | MCP 形态 | 亮点 |
|---|---|---|---|---|
| **Goose**（aaif-goose/goose） | 55,269★ | Apache-2.0 | MCP 即扩展模型，70+ 内置 | AAIF 创始项目；MCP 的参考实现 |
| **Hermes Agent**（NousResearch） | 253,604★ | MIT | `mcp_servers:` 一等配置 | **lazy 懒加载 + 50K 溢流 + sampling** |
| **DSH**（deepseek-ai/deepseek-harness） | 249,310★ | MIT | 原生 MCP 客户端 | Cordis 插件系统可热插拔；裸引擎 |

**DSH 补充**：原生 MCP 客户端是 `@deepseek-ai/dsh-mcp-client`，但 DSH 是「裸引擎」，不预置任何 MCP server。社区方案 **`dsh-mcp-bridge`**（Edge-Echo，MIT）一键接入 6 个：`everything` / `memory` / `filesystem` / `github` / `playwright` / `remote-http`。

### Tier 2 — 支持 MCP 但非核心

| 框架 | 星数 | 说明 |
|---|---|---|
| **Open Interpreter**（openinterpreter/openinterpreter） | 68,574★ | 已转型为「面向开放模型的编码 agent」（Kimi K3 / GLM 5.3） |
| **Agent Zero**（agent0ai/agent-zero） | 19,458★ | 注意：已从 `frdel/agent-zero` 迁移 |
| **OpenManus**（FoundationAgents/OpenManus） | 58,637★ | |
| **Letta**（letta-ai/letta） | 25,125★ | 原 MemGPT，记忆机制是核心卖点 |
| **Suna**（kortix-ai/suna） | 20,273★ | |
| **AutoGPT**（Significant-Gravitas） | 187,564★ | 平台化转型中，MCP 深度有限 |

### Tier 3 — MCP 支持薄弱或未核实

| 框架 | 星数 | 状态 |
|---|---|---|
| **Khoj**（khoj-ai/khoj） | 37,680★ | ⚠️ **未能核实其 MCP 支持**（最近推送 2026-08-02） |
| **Fabric**（danielmiessler/Fabric） | 44,254★ | 以 prompt 模式为主，非 MCP 架构 |
| **AgentVerse**（OpenBMB） | 5,156★ | ⚠️ **已 2 年未更新**（2024-09-09） |
| **AutoGen**（microsoft/autogen） | 61,394★ | ⚠️ **已半年未更新**（2026-04-15） |

### 中国系个人助理（本机/中文生态）

| 项目 | 星数 | 说明 |
|---|---|---|
| **CowAgent**（zhayujie） | **47,390★** | 开源个人 AI 助理 & Agent Harness，自我进化 + 记忆 + 多平台 |
| **QwenPaw**（agentscope-ai） | **35,668★** | 阿里 AgentScope 出品，可本机/云部署，多聊天应用接入 |
| **DeepChat**（ThinkInAIXYZ） | 6,360★ | 桌面智能助理 |
| **Everywhere**（Sylinko） | 6,314★ | 屏幕感知型桌面助理，用当前应用上下文 + MCP 工具跨应用操作 |
| **OpenAgent**（the-open-agent） | 5,689★ | computer-use + browser-use + 编码 agent |

**注意**：CowAgent（47,390★）与 QwenPaw（35,668★）这两个中国项目的星数**高于 Goose（55,269★ 之下，但高于多数 Tier2）**，但英文社区几乎不提它们。这是「个人助理」品类里一个明显的信息壁垒。

---

## 三 社区公认必装 MCP（分层清单）

### 3.1 通用核心 5 件套（硬共识）

前面第〇章已列。这里补充**为什么是这五个**：

- **Filesystem + Fetch** 是「能干活」的下限
- **Memory** 是「像个助理而不是搜索引擎」的分水岭
- **Search** 与 **Fetch** 是互补关系：搜索负责发现，抓取负责深入
- **Notes** 是让助理的产出**沉淀到你已有的知识体系**，而不是随对话消失

**反共识提醒**：**不要装第 6、7、8 个「顺便也装上」。** 见第四章。

### 3.2 分品类推荐（全部经 API 核验）

#### 记忆 / 上下文（个人助理的灵魂）

| MCP | 星数 | License | 最后推送 | 备注 |
|---|---|---|---|---|
| **Graphiti**（getzep） | **31,730★** | Apache-2.0 | 2026-10-14 | 实时知识图谱，企业级 |
| **basic-memory**（basicmachines-co） | 4,169★ | AGPL-3.0 | 2026-10-12 | 基于 Markdown 的本地记忆，**与 Obsidian 天然兼容** |
| **mcp-memory-service**（doobidoo） | 2,013★ | Apache-2.0 | 2026-10-14 | 知识图谱 + 自主整合 |
| **Knowledge Graph Memory**（官方参考） | 含于 servers 91,238★ | — | — | 官方最常被引用的记忆实现 |
| **mcp-trader**（wshobson） | 273★ | — | 2025-08-24 | ⚠️ **已归档** |

#### 笔记 / 知识库

| MCP | 星数 | License | 最后推送 | 备注 |
|---|---|---|---|---|
| **Notion 官方**（makenotion） | 4,666★ | MIT | 2026-09-20 | 官方维护，**首选** |
| **mcp-obsidian**（MarkusPfundstein） | 4,476★ | MIT | 2026-08-31 | 走 Obsidian REST API 插件 |
| **obsidian-wiki**（Ar9av） | 3,567★ | MIT | 2026-10-13 | 让 agent 用 Obsidian 维护「数字大脑」 |
| **obsidian-local-rest-api**（coddingtonbear） | 3,024★ | MIT | 2026-10-11 | REST API + MCP，本地 vault |
| **mcp-notion-server**（suekou） | 920★ | MIT | 2026-07-31 | 社区版，官方版优先 |
| **obsidian-mcp**（StevenStavrakis） | 742★ | MIT | 2026-10-08 | 轻量 |

#### 日历 / 邮件 / 办公套件

| MCP | 星数 | License | 最后推送 | 备注 |
|---|---|---|---|---|
| **google_workspace_mcp**（taylorwilsdon） | 3,336★ | MIT | 2026-10-09 | **一个覆盖 Gmail/Calendar/Docs/Sheets/Slides/Chat/Forms/Tasks/Drive/Search** |
| **keeper.sh**（ridafkih） | 1,387★ | AGPL-3.0 | 2026-10-13 | 通用日历 MCP：Google/Outlook/O365/iCloud 聚合同步 |
| **google-calendar-mcp**（nspady） | 1,199★ | MIT | 2026-10-13 | 专注日历 |
| **google-docs-mcp**（a-bonus） | 673★ | MIT | 2026-10-11 | Docs/Sheets/Drive/Gmail/Calendar |
| **mcp-email-server**（Wh1isper） | 360★ | BSD-3 | 2026-10-13 | 多账户 IMAP/SMTP，跨三平台 |
| **imap-mcp-server**（nikolausm） | 109★ | MIT | 2026-10-13 | AES-256 加密的多邮箱 |
| **email-mcp**（codefuturist） | 127★ | LGPL-3.0 | 2026-10-10 | 全功能 IMAP + SMTP |
| **Gmail-MCP-Server**（GongRzhe） | 1,168★ | MIT | 2025-08-06 | ⚠️ **已归档**——曾是热门，勿再用 |
| **mcp-atlassian**（sooperset） | 6,001★ | MIT | 2026-09-19 | Jira + Confluence |
| **zapier-mcp** | 435★ | MIT | 2026-07-29 | 一个 MCP 接 8000+ 应用（官方托管） |

#### IM / 沟通

| MCP | 星数 | License | 最后推送 | 备注 |
|---|---|---|---|---|
| **slack-mcp-server**（korotovsky） | 1,863★ | MIT | 2026-07-16 | 无需权限申请、支持 DM/群 DM/GovSlack |
| **lark-openapi-mcp**（larksuite，飞书官方） | 836★ | MIT | 2025-08-14 | ⚠️ **已 14 个月未更新** |
| **wecom-bot-mcp-server**（loonghao） | 104★ | MIT | 2026-10-13 | 企业微信机器人 |
| **open-feishu-mcp-server**（ztxtxwd） | 87★ | MIT | 2026-01-27 | 飞书社区实现 |

#### 搜索 / 抓取 / 浏览器

| MCP | 星数 | License | 最后推送 | 备注 |
|---|---|---|---|---|
| **apify-mcp-server** | 11,112★ | MIT | 2026-10-14 | 数千个现成爬虫，社媒/搜索/地图/电商通吃 |
| **firecrawl-mcp-server** | 7,598★ | MIT | 2026-10-14 | 官方抓取，Cursor/Claude 标配 |
| **exa-mcp-server** | 5,126★ | MIT | 2026-10-07 | 语义搜索，AI 原生 |
| **playwright-mcp**（microsoft） | **38,117★** | Apache-2.0 | 2026-10-08 | 浏览器自动化，**编程场景第一** |
| **brave-search-mcp-server**（brave 官方） | 1,497★ | MIT | 2026-10-14 | 官方实现，隐私优先 |
| **mcp-playwright**（executeautomation） | 5,665★ | MIT | 2025-12-13 | ⚠️ 已被官方版超越 |
| **BrowserMCP/mcp** | 7,182★ | Apache-2.0 | 2025-04-24 | ⚠️ **停更 18 个月** |
| **hyperbrowserai/mcp** | 789★ | MIT | 2025-11-20 | ⚠️ 停更 11 个月 |
| **mcp-server-browserbase** | 3,401★ | Apache-2.0 | 2026-07-20 | ⚠️ **已归档** |
| **oxylabs-mcp** | 104★ | MIT | 2026-09-07 | ⚠️ **已归档** |
| **perplexityai/modelcontextprotocol** | 2,564★ | MIT | 2026-10-13 | 官方 Perplexity API |

#### 地图 / 智能家居 / 媒体 / 天气

| MCP | 星数 | License | 最后推送 | 备注 |
|---|---|---|---|---|
| **ha-mcp**（homeassistant-ai） | **5,062★** | MIT | 2026-10-13 | **智能家居首选**；MCP Toplist 全局榜唯一个人用途前 10 |
| **homeassistant-mcp**（tevonsb） | 575★ | Apache-2.0 | 2026-01-25 | 社区版 |
| **hass-mcp**（voska） | 346★ | MIT | 2026-10-10 | 轻量 |
| **spotify-mcp**（varunneal） | 613★ | MIT | 2026-03-11 | ⚠️ 停更 7 个月 |
| **caiyun-weather**（caiyunapp 官方） | 47★ | MIT | 2026-09-01 | 彩云天气官方 |

#### 财经 / 翻译 / 信息流

| MCP | 星数 | License | 最后推送 | 备注 |
|---|---|---|---|---|
| **maverick-mcp**（wshobson） | 704★ | MIT | 2026-10-13 | Yahoo Finance + 技术分析 + 组合追踪 + 回测 |
| **stock-screener**（xang1234） | 349★ | Apache-2.0 | 2026-10-14 | 覆盖美/中/港/日/印/韩/台等 12 市场，80+ 筛选器 |
| **DeepL 官方**（DeepL/deepl-mcp-server） | 117★ | MIT | 2026-10-13 | 官方翻译 |
| **TrendRadar**（sansan0） | **62,892★** | GPL-3.0 | 2026-10-13 | 多平台舆情聚合 + RSS + 智能预警 |
| **chubbyskills**（chubbyguan） | 1,239★ | MIT | 2026-10-08 | 抖音/B站/小红书/公众号/X/播客 → 个人知识库，附 MCP server |
| **zenfeed**（glidea） | 1,716★ | AGPL-3.0 | 2026-07-10 | AI 增强 RSS |

#### 开发 / 代码（个人助理用户也常装）

| MCP | 星数 | License | 最后推送 | 备注 |
|---|---|---|---|---|
| **context7**（upstash） | **63,010★** | MIT | 2026-10-13 | 实时文档注入，**编程场景 star 第一** |
| **playwright-mcp**（microsoft） | 38,117★ | Apache-2.0 | 2026-10-08 | 浏览器自动化 |
| **github-mcp-server**（github 官方） | 33,601★ | MIT | 2026-10-13 | 官方 Go 实现 |
| **DesktopCommanderMCP**（wonderwhy-er） | 10,047★ | MIT | 2026-10-14 | 终端控制 + 文件搜索 + diff 编辑，**个人助理场景最对口** |
| **supabase/mcp** | 2,950★ | Apache-2.0 | 2026-10-14 | 数据库 |
| **mcp-server-cloudflare** | 4,378★ | Apache-2.0 | 2026-10-09 | 边缘计算 |
| **getsentry/toolkit** | 928★ | NOASSERTION | 2026-10-14 | ⚠️ 已从 `getsentry/sentry-mcp` 改名 |
| **mcp-jetbrains**（JetBrains） | 962★ | Apache-2.0 | 2026-01-07 | ⚠️ 停更 9 个月 |
| **linear-mcp-server**（jerhadf） | 346★ | MIT | 2025-05-01 | ⚠️ **停更 17 个月** |
| **semgrep/mcp** | 687★ | MIT | 2025-10-28 | ⚠️ **已归档** |
| **e2b-dev/mcp-server** | 393★ | Apache-2.0 | 2026-04-16 | ⚠️ **已归档**（用 `e2b-dev/E2B` 14,341★ 本体） |

### 3.3 中国生态必装（中文用户的真实刚需）

英文榜单几乎完全覆盖不到这一块。以下为本轮检索一手核验结果：

| 能力 | 推荐 | 星数 | 说明 |
|---|---|---|---|
| **地图** | `sugarforever/amap-mcp-server` | 131★ | 高德地图，支持 stdio/sse/streamable-http |
| | `@amap/amap-maps-mcp-server` | npm 包 | 官方 npm 版，约 42.6 万次采用（下载量口径，非星数） |
| **天气** | `caiyunapp/mcp-caiyun-weather` | 47★ | 彩云天气官方 |
| **微信读书** | `freestylefly/mcp-server-weread` | 577★ | 微信读书 MCP，社区最常引 |
| | `BENZEMA216/awesome-weread` | 66★ | 基于微信读书**官方 Agent Skill**（2026-05-17 发布）的二创精选 |
| **飞书** | `larksuite/lark-openapi-mcp` | 836★ | 官方，⚠️ 停更 14 个月 |
| | `ztxtxwd/open-feishu-mcp-server` | 87★ | 社区替代 |
| **企业微信** | `loonghao/wecom-bot-mcp-server` | 104★ | 仍在活跃维护（2026-10-13） |
| **公众号/RSS** | `tmwgsicp/wechat-download-api` | 1,170★ | 公众号文章获取 + RSS + 反风控 + MCP 接入 |
| **A股/财经** | `xang1234/stock-screener` | 349★ | 含中国/中国香港/中国台湾市场 |
| **中国 MCP 索引** | `zackchewa/awesome-china-mcp` | 26★ | 高德/12306/小红书/飞书/语雀/A股 的策展索引 |
| **企业查询** | `ballcheung/china-company-check-mcp` | 1★ | 基于 GSXT/SAMR 官方工商数据 |

**⚠️ 中国生态的三个现实**：

1. **星数普遍很低**（几十到几百），但**采用率高**——中文用户不看 GitHub star，看的是公众号文章和社群推荐。不要用星数判断中国 MCP 的可用性。
2. **官方 MCP 普遍停更**：飞书官方 14 个月未更新、腾讯文档没有可核验的官方 MCP 仓库。企业 IM 类 MCP 的维护质量是短板。
3. **腾讯文档 MCP 未能找到官方仓库**。本轮检索到的相关仓库均为第三方「灵感源自腾讯文档」的 skill 项目，非官方集成。

### 3.4 PulseMCP 下载量硬数据（另一把尺子）

星数反映「开发者关注度」，下载量反映「实际装机量」。个人助理场景下，两者差异很大：

| MCP | PulseMCP 下载量 | 备注 |
|---|---|---|
| **Desktop Commander** | 202k | 终端 + 文件，个人助理对口 |
| **Notion** | 168k | 笔记类第一 |
| **Fetch** | 164k | 官方，装机量最大 |
| **Grafana** | 155k | 可观测性 |
| **Supabase** | 152k | 数据库 |
| **Knowledge Graph Memory** | **147k** | 记忆类第一 |
| **Time** | **138k** | 极小但极高装机——时区处理是刚需 |
| **FireCrawl** | 136k | 抓取 |
| **Stripe** | 133k | 支付 |
| **GitLab** | 131k | 代码托管 |
| **Slack** | 74.7k | IM |
| **Google Workspace** | 67k | 办公套件 |

**注意「Time」排第 7**——一个功能极简（就是告诉 LLM 现在几点）的 MCP 却有 138k 下载。这说明**个人助理场景里，低价值但高频的基础设施型 MCP 反而装机率最高**。

**MCP Toplist 全局榜的偏差**：全局 Top 10 几乎全是编程/dev 工具，唯一个人用途进榜的是 **Home Assistant MCP（#6）**。**结论：全局排行榜不能用来回答「个人助理该装什么」**——这是本次调研最重要的方法论修正之一。

---

## 四 上下文膨胀：个人助理场景的头号杀手

### 4.1 硬证据

**证据 A — GitHub Copilot CLI issue #3024**：用户装了 20+ 个 MCP，**吃掉 94k / 128k context**，导致启动变慢、崩溃、严重幻觉。

**证据 B — Hermes config.yaml 原文**（本机实测）：

> MCP servers routinely return un-paginated 20-50K payloads that bloat context and slow every subsequent turn.

Hermes 的应对是给 `mcp_*` 工具单独设 **50,000 字符**溢流阈值（通用默认是 100K）。

**证据 C — Hermes 的 `lazy` 设计**：启动只登记 schema，首次调用才拉起进程。这是对「装多了拖慢启动」的正面回答。

**证据 D — Hermes 的 `inherit_mcp_toolsets`**：子代理默认继承父级 MCP 工具集，但可设 `false` 做严格交集，避免工具集爆炸式复制。

### 4.2 最小负载方案

社区收敛的经验值：

| 档位 | MCP 数量 | 适用 | context 占用 |
|---|---|---|---|
| **极简** | 3 | 纯聊天 + 文件 | ~10-15% |
| **推荐** | **5-6** | 通用个人助理 | ~20-30% |
| **上限** | 8 | 多角色重度使用 | ~35-45% |
| **红线** | >10 | — | **>50% 即危险** |

**红线判据**：MCP 工具定义占用超过 **50% context**，就会出现启动慢、工具选择错乱、幻觉加剧。

**实操建议**：

1. **按项目/场景分组，不要全开**。用客户端的分组功能或 Hermes 的 `lazy`。
2. **优先选「一个 MCP 覆盖多能力」的**。例如 `google_workspace_mcp`（3,336★）一个就覆盖 Gmail + Calendar + Docs + Sheets + Slides + Chat + Forms + Tasks + Drive + Search，远优于装 5 个单一 MCP。
3. **优先选支持工具过滤的**。Hermes 支持 `--allow-tool` 白名单；本机 WorkBuddy 的 `gog` 就配了 `--allow-tool sheets,drive_search,drive_get,docs_get`——**只开你要用的 4 个工具**，这是最有效的减负手段。
4. **警惕「工具爆炸」型 MCP**。像 Apify（11,112★）能接数千个爬虫，工具列表可能极长，务必配合白名单。

---

## 五 安全：个人助理是最危险的 MCP 宿主

个人助理的权限边界覆盖文件系统、邮箱、日历、IM、浏览器——**一旦被攻破，损失是「数字生活的全部」**，而不是「一个项目仓库」。

### 5.1 OpenClaw 已知漏洞全谱

| 编号 | 名称 | 严重度 | 性质 |
|---|---|---|---|
| **CVE-2026-25253** | 1-Click RCE | **CVSS 8.8** | 单次点击即可远程代码执行 |
| **CVE-2026-25593** | ClawJacked | 高 | WebSocket 端口暴力破解 |
| **CVE-2026-28363** | — | **CVSS 9.9** | 沙箱逃逸 |
| — | — | — | **CNNVD 累计 82 个漏洞** |

**暴露面**：据公开统计，**超过 27 万个 OpenClaw 实例暴露在公网**。

### 5.2 ClawHavoc 供应链投毒事件

**这是整个 MCP/Skill 生态迄今最严重的一起供应链攻击**：

- 攻击者在 ClawHub 上传 **341 个恶意技能**
- 投递载荷：**Atomic macOS Stealer**（窃取钥匙串、浏览器凭证、加密钱包）
- 攻击面：技能安装即执行

**教训**：Skills 和 MCP 一样是**可执行代码**。`SKILL.md` 里可能藏着 `scripts/` 目录，装了就等于在本地跑了别人的代码。

### 5.3 加固清单（按优先级）

**① 装任何 Skill / MCP 之前先审代码**

这是第一条，也是最重要的一条：

```bash
# 装之前先看它到底带不带可执行脚本
find <skill-or-mcp-dir> -name "*.sh" -o -name "*.py" -o -name "*.js" | head
grep -rn -E "curl|wget|base64 -d|eval|exec|rm -rf" <skill-dir>/
```

**② 先装安全扫描类 Skill**：OpenClaw 社区共识是**第一个装 `skill-vetter` / `clawsec`**，用它扫后续要装的技能。

**③ 绝不给 MCP 超出需要的权限**

- 用 `--allow-tool` 白名单，不要全开
- 文件系统 MCP 只挂载必要目录，**绝不挂 `~` 或 `/`**
- 邮箱/日历 MCP 用**只读 scope**起步

**④ 不要暴露到公网**

- OpenClaw 默认监听 `127.0.0.1:18789`，**不要改成 0.0.0.0**
- 需要异地访问用 Tailscale / WireGuard，不要直接端口转发

**⑤ 中国用户的官方指引**

工信部针对此类个人助理软件发布了**「六要六不要」加固指南**——涉及账号隔离、最小权限、来源审查等。国内部署建议对照执行。

**⑥ 数据卫生**

- 记忆文件（`MEMORY.md` / `memories/`）会沉淀个人信息，**不要放进公开 Git 仓库**
- 本机实测：`~/.workbuddy-ai/mcp.json` 的 `gog` 配置里**明文写着个人邮箱**——这类配置文件如果被同步到公开仓库就是直接泄露
- OpenClaw 的做法值得学：`AGENTS.md` 明确规定 **`MEMORY.md` 只在主会话加载，绝不在共享上下文（Discord/群聊）加载**，理由是"contains personal context that shouldn't leak to strangers"

**⑦ 销毁式操作走回收站**

OpenClaw `AGENTS.md` 的 Red Lines 原文：

> Don't exfiltrate private data. Ever.
> Don't run destructive commands without asking.
> `trash` > `rm` (recoverable beats gone forever)

---

## 六 陷阱清单（重要，全是实测）

### 6.1 已归档的 MCP（旧教程仍在推荐）

| 仓库 | 星数 | 归档 | 说明 |
|---|---|---|---|
| `appcypher/awesome-mcp-servers` | 5,795★ | ✅ | 榜单本身归档了 |
| `browserbase/mcp-server-browserbase` | 3,401★ | ✅ | 浏览器自动化 |
| `supermemoryai/apple-mcp` | 3,123★ | ✅ | Apple 原生工具（已从 `dhravya/apple-mcp` 改名） |
| `mcp-router/mcp-router` | 2,137★ | ✅ | 2026-09-18 终止开发支持 |
| **`GongRzhe/Gmail-MCP-Server`** | **1,168★** | ✅ | **曾是 Gmail 类最热门，已归档** |
| `semgrep/mcp` | 687★ | ✅ | 安全扫描 |
| `e2b-dev/mcp-server` | 393★ | ✅ | 用 `e2b-dev/E2B`（14,341★）本体 |
| `wshobson/mcp-trader` | 273★ | ✅ | 股票 |
| `oxylabs/oxylabs-mcp` | 104★ | ✅ | 抓取 |
| `Beltran12138/wecom-docs-mcp-server` | 7★ | ✅ | 已被官方 `WecomTeam/wecom-cli` 取代 |

### 6.2 高星但停更（星数是历史遗产，不代表能用）

| 仓库 | 星数 | 停更时长 | 最后推送 |
|---|---|---|---|
| `BrowserMCP/mcp` | 7,182★ | **18 个月** | 2025-04-24 |
| `jerhadf/linear-mcp-server` | 346★ | **17 个月** | 2025-05-01 |
| `larksuite/lark-openapi-mcp` | 836★ | **14 个月** | 2025-08-14 |
| `hyperbrowserai/mcp` | 789★ | 11 个月 | 2025-11-20 |
| `executeautomation/mcp-playwright` | 5,665★ | 10 个月 | 2025-12-13 |
| `JetBrains/mcp-jetbrains` | 962★ | 9 个月 | 2026-01-07 |
| `varunneal/spotify-mcp` | 613★ | 7 个月 | 2026-03-11 |

### 6.3 仓库改名（照抄旧 URL 会 404 或找到错的东西）

| 旧名 | 新名 | 备注 |
|---|---|---|
| `block/goose` | **`aaif-goose/goose`** | 55,269★，AAIF 迁移 |
| `deepseek-ai/DeepSeek-Harness` | `deepseek-ai/deepseek-harness` | 249,310★ |
| `mendableai/firecrawl-mcp-server` | `firecrawl/firecrawl-mcp-server` | 7,598★ |
| `supabase-community/supabase-mcp` | `supabase/mcp` | 2,950★ |
| `jlowin/fastmcp` | `PrefectHQ/fastmcp` | 28,069★ |
| `lobehub/lobe-chat` | `lobehub/lobehub` | 83,223★ |
| `danny-avila/LibreChat` | `LibreChat-AI/LibreChat` | 45,656★ |
| `frdel/agent-zero` | `agent0ai/agent-zero` | 19,458★ |
| `All-Hands-AI/OpenHands` | `OpenHands/OpenHands` | 90,850★ |
| `getsentry/sentry-mcp` | `getsentry/toolkit` | 928★ |
| `ppl-ai/modelcontextprotocol` | `perplexityai/modelcontextprotocol` | 2,564★ |
| `dhravya/apple-mcp` | `supermemoryai/apple-mcp` | 3,123★（已归档） |
| `apify/actors-mcp-server` | `apify/apify-mcp-server` | 11,112★ |

### 6.4 「MCP 仓库」实为库本体（别搞混）

- `microsoft/markitdown`（**190,126★**）是**文档转 Markdown 的 Python 库**，MCP 只是它的捆绑功能之一
- `microsoft/playwright`（**97,679★**）是**浏览器自动化框架本体**；真正的 MCP 是 `microsoft/playwright-mcp`（38,117★）
- `modelcontextprotocol/servers`（91,238★）是**官方参考服务器集合**，不是一个可安装的 MCP
- `punkpeye/awesome-mcp-servers`（**96,313★**）是**榜单**，不是 MCP
- `steipete/openclaw`（20★）是**个人 fork**，不是 OpenClaw 主仓库（主仓库是 `openclaw/openclaw`，391,930★）

### 6.5 官方参考服务器的现状

`modelcontextprotocol/servers`（91,238★）里，**官方维护的活跃参考服务器只剩 7 个**：

Filesystem · Memory · Sequential Thinking · Time · Fetch · Git · Everything

**已归档**的官方/准官方实现（旧教程大量引用）：
`servers/src/gdrive` · `servers/src/google-maps` · `servers/src/slack` · `servers/src/sqlite`

**这意味着**：网上大量"官方 GDrive MCP / 官方 Google Maps MCP"教程已经失效。用前务必去仓库确认路径还在不在。

### 6.6 口径陷阱

| 常见说法 | 真相 |
|---|---|
| 「MCP 生态已破 10 万」 | 这是 **Linux Foundation 生态口径**；**官方 MCP Registry 约 3.03 万条**（`modelcontextprotocol/registry`，7,354★） |
| 「技能描述上限 200 字符」 | 规范是 **1,024 字符**（帮助中心写 200 是错的） |
| 「技能预算是 X words」 | 是 **tokens** 不是 words |
| 「OpenClaw 有 390k star」 | ✅ **正确**，实测 **391,930★**（此前腾讯文章说的 280k 是旧数据） |
| 「Hermes Agent 支持 MCP」 | ✅ 正确，且是本轮 MCP 成熟度最高的框架之一 |

---

## 七 数据可信度与方法

### 7.1 本轮数据来源分级

| 级别 | 来源 | 可信度 |
|---|---|---|
| **A 级（一手实测）** | 主代理 GitHub REST API 直查（81 仓库）+ 本机文件系统实测（`~/.openclaw/`、`%LOCALAPPDATA%/hermes/`、`~/.dsh/`、`~/.workbuddy-ai/mcp.json`） | **高** |
| **B 级（官方文档）** | OpenClaw 本机 workspace 文件、Hermes `config.yaml` 内嵌文档、ClawHub 仓库说明 | 中高 |
| **C 级（二手聚合）** | PulseMCP 下载量、MCP Toplist 排名、中文社区榜单 | 中 |
| **D 级（受限未核实）** | Reddit / Hacker News 直接抓取（**被 403 abuse-block 拦截**），社区共识由排名聚合器 + 下载量信号重建 | **标注为 moderate-confidence** |

### 7.2 明确未核实的项

诚实标注，避免以讹传讹：

1. **Reddit / Hacker News 直接抓取失败**（403）。「社区共识」是从排名聚合器与下载量信号重建的，非直接引语。
2. **Hermes Web UI 内建的「推荐服务一键安装列表」内容未核实**——本机 `config.yaml` 里该段全部是注释掉的示例。
3. **Khoj（37,680★）的 MCP 支持未核实**。
4. **ClawHub 注册表规模**：不同来源给出 3,286 vs 5,700+ 两个数，未取到权威口径。
5. **OpenClaw 支持的 IM 平台数「26」**：来自二手转述，未从官方文档核实。
6. **Hermes-as-MCP-server**（把 Hermes 暴露为 MCP server）能力未核实。
7. **腾讯文档官方 MCP**：未找到可核验的官方仓库。
8. **DSH 主仓库 URL**：`deepseek-ai/dsh` 返回 404，实际仓库是 `deepseek-ai/deepseek-harness`（249,310★）。
9. **`nbonamy/witsy`**：API 返回仅 8★、2026-04-14 建仓，疑为抢注或同名仓库，**不是**那个知名的 Witsy 客户端，本轮不采信。

### 7.3 本机环境实测清单

| 项 | 实测值 |
|---|---|
| OpenClaw | `~/.openclaw/`，含 `skills/`（1 个软链 skill）+ `workspace/`（7 个 Markdown + 1 个 state json），**无 MCP 配置** |
| Hermes Agent | `%LOCALAPPDATA%/hermes/`，`config.yaml` 123,576 字节，含完整 `mcp_servers` 文档段；`SOUL.md` 667 字节；有 `bot_relay/`、`cron/`、`memories/`（空） |
| DSH | `~/.dsh/`，profiles 有 `desktop` 与 `web` 两个，均为 pnpm workspace；含 `.dsh-market/` 市场状态 |
| WorkBuddy | `~/.workbuddy-ai/mcp.json` **只配了 3 个 MCP**（gog / web-search / nixos，全 stdio） |
| **重要观察** | 编程场景 star 最高的三个 MCP（Context7 63,010★ / Playwright 38,117★ / GitHub 33,601★）**在本机一个都没配**——说明「最热门」与「实际在用」差距很大 |

---

## 附录：本轮核验的 GitHub 原始数据（节选）

完整数据见 `data/github-verified.json`（81 条）与 `data/github-search.json`（19 组检索）。

### 个人助理 / Agent 框架本体

| 仓库 | 星数 | Forks | License | 建仓 | 最后推送 |
|---|---|---|---|---|---|
| `openclaw/openclaw` | **391,930** | 82,429 | MIT | 2025-11-24 | 2026-10-14 |
| `NousResearch/hermes-agent` | **253,604** | 55,022 | MIT | 2025-07-22 | 2026-10-14 |
| `deepseek-ai/deepseek-harness` | **249,310** | 29,998 | MIT | 2026-08-13 | 2026-10-09 |
| `Significant-Gravitas/AutoGPT` | 187,564 | 45,943 | NOASSERTION | 2023-03-16 | 2026-10-14 |
| `OpenHands/OpenHands` | 90,850 | 12,042 | MIT | 2024-03-13 | 2026-10-14 |
| `openinterpreter/openinterpreter` | 68,574 | 5,900 | Apache-2.0 | 2023-07-14 | 2026-10-11 |
| `microsoft/autogen` | 61,394 | 9,279 | CC-BY-4.0 | 2023-08-18 | ⚠️ 2026-04-15 |
| `FoundationAgents/OpenManus` | 58,637 | 10,172 | MIT | 2025-03-06 | 2026-09-30 |
| `aaif-goose/goose` | **55,269** | 6,428 | Apache-2.0 | 2024-08-23 | 2026-10-14 |
| `zhayujie/CowAgent` | 47,390 | — | MIT | — | 2026-10-14 |
| `khoj-ai/khoj` | 37,680 | 2,511 | AGPL-3.0 | 2021-08-16 | 2026-08-02 |
| `agentscope-ai/QwenPaw` | 35,668 | — | Apache-2.0 | — | 2026-10-14 |
| `letta-ai/letta` | 25,125 | 2,644 | Apache-2.0 | 2023-10-11 | 2026-09-10 |
| `kortix-ai/suna` | 20,273 | 3,435 | NOASSERTION | 2024-10-05 | 2026-10-14 |
| `agent0ai/agent-zero` | 19,458 | 3,826 | NOASSERTION | 2024-06-10 | 2026-10-13 |
| `ThinkInAIXYZ/deepchat` | 6,360 | — | Apache-2.0 | — | 2026-10-13 |
| `Sylinko/Everywhere` | 6,314 | — | NOASSERTION | — | 2026-10-11 |
| `the-open-agent/openagent` | 5,689 | — | Apache-2.0 | — | 2026-10-14 |
| `OpenBMB/AgentVerse` | 5,156 | 523 | Apache-2.0 | 2023-05-06 | ⚠️ 2024-09-09 |

### MCP 基础设施

| 仓库 | 星数 | License | 最后推送 |
|---|---|---|---|
| `modelcontextprotocol/servers` | 91,238 | NOASSERTION | 2026-10-13 |
| `punkpeye/awesome-mcp-servers` | 96,313 | MIT | 2026-10-09 |
| `PrefectHQ/fastmcp` | 28,069 | Apache-2.0 | 2026-10-13 |
| `modelcontextprotocol/python-sdk` | 24,570 | MIT | 2026-10-13 |
| `modelcontextprotocol/typescript-sdk` | 13,577 | NOASSERTION | 2026-10-14 |
| `modelcontextprotocol/inspector` | 11,071 | NOASSERTION | 2026-10-14 |
| `modelcontextprotocol/registry` | 7,354 | NOASSERTION | 2026-10-11 |
| `MCPJam/inspector` | 2,257 | NOASSERTION | 2026-10-14 |
| `punkpeye/fastmcp`（TS 版） | 3,274 | MIT | 2026-10-04 |
| `wong2/awesome-mcp-servers` | 4,361 | MIT | 2026-07-13 |

### MCP 客户端 / 个人助理前端

| 仓库 | 星数 | License | 最后推送 |
|---|---|---|---|
| `lobehub/lobehub` | 83,223 | NOASSERTION | 2026-10-14 |
| `Mintplex-Labs/anything-llm` | 67,043 | MIT | 2026-10-14 |
| `CherryHQ/cherry-studio` | 52,615 | AGPL-3.0 | 2026-10-14 |
| `LibreChat-AI/LibreChat` | 45,656 | MIT | 2026-10-14 |
| `chatboxai/chatbox` | 42,014 | GPL-3.0 | 2026-09-24 |

---

*报告生成：2026-10-14 ｜ 数据核验：GitHub REST API 一手直查 ｜ 本机环境：Windows 11*
