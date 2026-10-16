# Hermes Agent × goose：集成路径与自进化选型 · 总结

> 调研日期：2026-10-16 ｜ 方法：本机源码取证（Hermes 完整源码 + goose 上游源码）+ 双方官方文档交叉验证
> 本机：Windows 11；Hermes Agent 已安装（`C:\Users\Admin\AppData\Local\hermes\`）；**goose 未安装**（因此所有端到端结论均为未实测）

本目录把「Hermes 能不能当 goose 的后端」这一个问题拆成**四条路径**，并追答了由此派生出的两个关键子问题（知识库 / 记忆与技能自进化）。

---

## 文档导航

| 文件 | 内容 |
|---|---|
| **`report.md`** | 主交付物。四条路径的双方配置、证据清单、未验证项，含第 9 节（知识库）与第 10 节（自进化）两篇追加调研 |
| `outline.yaml` | 调研条目定义：items = 4 条候选集成路径，含执行记录 |
| `fields.yaml` | 每条路径必须核验的 7 个维度（支持级别 / 传输协议 / 谁跑工具循环 / 双方配置 / 扩展透传 / 证据分级 / 风险） |
| `README.md` | 本文件：一页结论 + 与姊妹项目的取舍 |

---

## 一页结论：四个问题，四个答案

| 你的问题 | 答案 | 关键依据 |
|---|---|---|
| Hermes 能当 goose 的**模型**吗？ | ✅ **路径 A** | `hermes proxy`（OpenAI 兼容，默认 `127.0.0.1:8645`），纯凭证透传，goose 保留自己的 loop 与 70+ 扩展。十分钟可跑通 |
| Hermes 能当 goose 的**智能体后端/运行时**吗？ | ✅ **路径 B** | Hermes API server（默认 `127.0.0.1:8642`，模型名 `hermes-agent`），"agent 即模型"，Hermes 侧跑完整工具循环 |
| goose 没有知识库，哪条路径能**用到 Hermes 的知识能力**？ | ✅ **B（或等价的 C）** | 知识能力全在 agent 层 → 只有让 Hermes 的 agent 真跑起来才用得上。**A 完全用不到，D 用不到**（`hermes mcp serve` 是消息桥，不暴露知识检索） |
| goose 要用上 Hermes 的**记忆/技能自进化**，选哪条？ | ✅ **只有 B** | 自进化 = nudge + background review fork + **curator**，而 curator 的触发点只有 "CLI session start / **gateway housekeeping** / serve 维护定时器" —— **只有 B 天然常驻 gateway** |

**一句话**：官方可达的「Hermes 作为 goose 运行时」= **路径 B**；「Hermes 作为 goose 模型」= **路径 A**；至于 goose 官方那种 ACP 运行时委托（路径 C），**goose 侧没有入口**，需要变通或推上游。

---

## 四条路径总表

| # | 路径 | 传输协议 | 谁跑工具循环 | goose 扩展是否被使用 | 双方原生支持？ |
|---|---|---|---|---|---|
| A | `hermes proxy` → goose 自定义 provider | OpenAI Chat Completions | **goose** | ✅ 是 | ✅ 双方文档都覆盖 |
| B | Hermes API server → goose 自定义 provider | OpenAI Chat Completions | **Hermes** | ❌ 否（Hermes 用自己的工具集） | ✅ 双方文档都覆盖 |
| C | `hermes acp` ← goose ACP provider | ACP over stdio | **Hermes** | ✅ 可透传（作为 MCP server） | ❌ **goose 侧封闭**（仅 5 个写死的 ACP adapter） |
| D | `hermes mcp serve` → goose extension | MCP over stdio | goose 跑，Hermes 被调用 | ✅ 是 | ✅ 双方原生支持 |

**判据来源**：goose 源码 `ProviderDef` 的 `RUNS_OWN_TOOL_LOOP` 常量——ACP provider 为 `true`，声明式 custom provider 强制 `false`。「模型」与「运行时」在 goose 里是硬编码区分，不是文案差异。

### 路径 C 的三种变通

| 方案 | 做法 | 评价 |
|---|---|---|
| **C1** | 放一个叫 `pi-acp` 的脚本，内部 exec `hermes acp` | 最快，属 hack。选 `pi-acp` 是因为它 `session_mode_id: None`（不会推 Hermes 不认识的 mode）；代价是模型选择**可能不生效** |
| **C2** | 自建 goose 发行版（Custom Distributions），照 `claude_acp.rs` 抄一个 `hermes_acp.rs` | 工程上最干净，一次性投入 |
| **C3** | 推上游（ACP 有 registry，Hermes 已合规） | 成本最低 |

---

## 关键机制速查（踩坑清单）

**走 B 时的四个开关（最容易踩的坑）**

1. **`memory.write_approval` / `skills.write_approval` 必须保持 `false`**（默认值）。一旦为 `true`，文档原话是 "writes **outside the interactive CLI** are held for review and **never reach the file**" —— 而 API server 正是 outside CLI，且审批入口（`/memory approve all`、`/skills approve`）在 CLI/messaging 上，**goose 侧看不见也批不了 → 自进化静默失效**。这是头号杀手。
2. **钉住 `X-Hermes-Session-Id`**。nudge 计数器挂在 agent 实例上，而 agent 缓存是 per-session；不发会话头 → 每轮新 session → 计数器归零 → nudge 不触发。（⚠️ 逻辑外推，未实测）
3. **盯住 background review 的 token 成本**。它是 **post-turn** fork，goose 是高频调用方；用 `auxiliary.background_review.max_input_tokens` 封顶，或路由到便宜模型。
4. **别把工具关掉**：`memory.memory_enabled: false`、`user_profile_enabled: false`，或把 `memory`/`skills` 放进 `agent.disabled_toolsets` → 自进化归零。

**Hermes 的「知识库」真相**：Hermes **没有** knowledge-base / rag 产品页。知识资产是四类、全在 agent 层——① 内建持久记忆 `MEMORY.md`(2200 字符) + `USER.md`(1375 字符)，会话开始整块注入（**冷冻快照**）；② `session_search`（`state.db` FTS，需要会话边界）；③ 7 个外部记忆 provider（honcho/o.../supermemory，同时只能开一个）；④ 技能体系（knowledge-base skill、bundled `llm-wiki`、optional 的 `qmd`/`siyuan`/`chroma`/`qdrant`/`pinecone`）。

**走 B 的副作用**：goose 自己的 `memory` 扩展与 Hermes 的记忆是**两套独立存储，不会合并**。你得到的是"goose 把活派给了一个会自己记事的同事"。

---

## 与姊妹项目的关系：两条通向「自进化」的路线

本仓库里另有一份相关调研 [`opencode-goose-self-evolving-agent`](../opencode-goose-self-evolving-agent/report.md)，同样产出于 2026-10-16，回答的是**另一个方向**的问题。两者是同一目标（让 goose/opencode 具备自进化）的两种策略：

| | **路线 ①：自建**（`opencode-goose-self-evolving-agent`） | **路线 ②：借后端**（本项目） |
|---|---|---|
| 主张 | 给 goose/opencode 补上 Hermes 的 7 件工程件（技能自动创建、回合后自审、curator、有界记忆、reward signal、调度、共享技能根） | 不改造前端，直接把 Hermes 当后端（路径 B），**白拿**它的记忆/技能/curator |
| 代价 | 需要自己写插件（实测：opencode 1 个插件文件、goose 1 个插件目录）；**缺 provenance 层**，归档动作必须人工确认 | **放弃 goose 自己的 loop 与 70+ 扩展**；两套记忆不合并；受 Hermes 更新状态影响 |
| 收益 | 保留 goose 原生能力；`~/.agents/skills` 一次沉淀、**三家复用**；goose 在 hooks/cron/token 计量上甚至比 Hermes 更完整 | 零改造得到完整闭环（nudge + review fork + curator 三项全活） |
| 何时选 | 你要**长期跑 goose 本体**，且在意扩展生态与技能库复用 | 你要**立刻得到**带记忆/技能的 agent，且接受"执行者是 Hermes" |

**交叉结论**：路线 ① 里被列为"必做项"的 **reward signal（可测量的进化）**，在路线 ② 里由 Hermes 的 `curator usage` 遥测天然提供——这也是路线 ② 唯一无法被路线 ① 轻易追平的一环。反之，路线 ① 的 `~/.agents/skills` 共享根红利，路线 ② 拿不到。

**共同红线（两份报告独立得出同一结论）**：**"自动写技能 + 无闸门 = 提示注入的自我放大回路"**。路线 ① 的解法是把"自动写技能"降级为"写待办队列"；路线 ② 的解法是守住 `write_approval` 的默认值 / 显式打开审批。

---

## 建议落地顺序

```powershell
# 前置：先把 Hermes 更新收敛，否则一切命令都会被依赖安装打断
hermes update          # 或 hermes pm install
hermes doctor
hermes acp --check     # 仅路径 C 依赖这步

# 第 1 步（10 分钟，必成）：路径 A —— 先用上订阅
hermes portal
hermes proxy start
# 另开终端：
$env:GOOSE_PROVIDER="openai"; $env:OPENAI_HOST="http://127.0.0.1:8645"
$env:OPENAI_API_KEY="sk-unused"; $env:GOOSE_MODEL="Hermes-4-70B"
goose session

# 第 2 步（30 分钟，高价值）：路径 B —— 让 Hermes 真正当后端，并白拿自进化
#   .env 设 API_SERVER_ENABLED=true / API_SERVER_KEY=<长随机串>
#   hermes gateway
#   goose 建 custom provider 指向 http://127.0.0.1:8642/v1/chat/completions，模型名 hermes-agent
#   并发 X-Hermes-Session-Id 钉住会话

# 第 3 步（想清楚再动）：路径 C
#   先花 10 分钟试 C1 影子二进制（pi-acp → hermes acp），不行再评估 C2 / C3
```

---

## 未验证项汇总（12 条，务必当作假设）

> 根因：本机 **goose 未安装**，且 Hermes 处于 `source-update` 中途状态，`hermes proxy status` 触发依赖安装超时 —— 上述所有命令均来自 `--help` / 源码 / 文档，**非运行时实测**。

**路径 C**
1. C1 影子二进制方案从未实测；不确定 `session/new` 是否被 Hermes 的 mode/model 校验拒绝。
2. `set_config_option` 收到未知 `config_id` 是静默还是报错。

**路径 B**
3. goose 发来的 `tools` 是否被 Hermes 忽略（文档未承诺执行调用方 tools）。**这是选 B 还是 C 的分水岭**。
4. SSE 自定义事件 `hermes.tool.progress` 与 goose 流解析器的兼容性。
5. goose 的 `headers` / `OPENAI_CUSTOM_HEADERS` 能否成功注入每轮请求（抓包未做）。

**路径 A**
6. 模型是否稳定返回 OpenAI 格式 `tool_call`（proxy 未成功启动）。

**route 级**
7. `custom_providers/*.json` 手写后是否被热加载。
8. Hermes 更新收敛状态本身未验证。

**知识库（§9.5）**
9. `qmd` 挂到 goose 是否可用（未在本机安装验证）。
10. goose 内建 memory 扩展的实际能力边界（未读源码、未实测）。

**自进化（§10.5）**
11. nudge 计数器是否真因每轮新 session 而归零（逻辑外推）。
12. `write_approval: true` 下 API server 写入的确切命运（是落盘不通知，还是完全不落盘）；curator 是否会被 ACP 进程间接触发。

---

## 复现环境

| 项 | 值 |
|---|---|
| Hermes 安装 | `C:\Users\Admin\AppData\Local\hermes\`（源码检出 `hermes-agent\`） |
| Hermes 配置文件 | `C:\Users\Admin\AppData\Local\hermes\config.yaml`、`.env` |
| 关键结论来源 | 详见 `report.md` 第 6 节「证据清单」 |
| goose 源码 | 上游 `crates/goose/src/...`（本机缓存于 `%TEMP%\goose-src\`） |
