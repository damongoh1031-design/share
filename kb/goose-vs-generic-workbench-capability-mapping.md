---
id: goose-vs-generic-workbench-capability-mapping
title: goose 能力对标速查 —— 术语映射、MCP/Skills 增删、专家团、循环步数、工具上限、系统耦合、渲染与 RAG
tags: [goose, ai-agent, capability-mapping, mcp, subagents, custom-agents, recipes, rag, workbuddy]
created: 2026-10-15
updated: 2026-10-15
version: 1.2
status: stable
source: goose 官方文档库（documentation/ 全量 173 篇，本地抓取快照 2026-10-15）+ 源码级事实快照（v2.2 报告）+ 本文判断
confidence: 已核实
type: Checklist
---

# goose 能力对标速查

## 一句话结论

goose 的「专家团」= **Custom Agents**（`~/.agents/agents/*.md` + `@name` 提及 / `Delegate to` 委派）；它有 Skills / Recipes / Plugins / Hooks / Subagents / Slash Commands，但**没有**向量知识库（无切片·无嵌入·无重排·无语义召回）、**没有** PDF 生成、**没有**多模型同屏对话、**没有**内建 planner。系统耦合极深：Developer extension 的 `shell` 以当前用户权限直接执行任意命令，且默认权限模式（Completely Autonomous）**不询问**。

---

## 1. 术语映射（goose ↔ 通用工作台）

goose 的术语来自两个**外部标准**，不是自研命名：

- **MCP**（Model Context Protocol）→ 工具 / 应用接入层
- **Open Plugins**（open-plugins.com）→ 插件与 hooks 分发层

因此名词与「自研工作台」不能一一对齐。对照如下：

| goose 术语 | 落盘位置 / 入口 | 作用 | 通用工作台对应 |
|---|---|---|---|
| **Extensions** | `~/.config/goose/config.yaml` | 工具接入（内置 / CLI 命令 / 远程 HTTP） | 连接器、MCP 服务器 |
| **Plugins** | `~/.agents/plugins/<name>/` | 容器（`plugin.json`），可含 skills + hooks | 插件包（技能 + 钩子） |
| **Hooks** | `<plugin>/hooks/hooks.json` | 生命周期事件触发本地脚本 | 事件回调 / 钩子 |
| **Skills** | `~/.agents/skills/<name>/SKILL.md` | 按需加载的指令包 | 技能包 / 提示词模板 |
| **Recipes** | Recipe Library / `~/.config/goose/recipes/` | 可复用工作流（打包 extensions + prompt + settings + 参数） | 工作流模板 |
| **Subagents** | 运行时 spawn | 隔离的独立 goose 实例 | 子代理 / 委派 |
| **Custom Agents** | `~/.agents/agents/*.md` | 角色定义（提示词 + 可选 model） | **专家 / 角色（专家团）** |
| **Slash Commands** | `config.yaml` → `slash_commands:` | 把 Recipe 绑成 `/命令` | 自定义命令 |
| **Prompt Templates** | `~/.config/goose/prompts/*.md` | 覆盖系统提示（system / compaction / subagent_system 等 8 个） | 系统提示词编辑 |
| **Prompt Templates / .goosehints** | 项目根 `.goosehints` | 项目级持久指令 | 项目规则文件 |

**goose 独有、通用工作台少见对应的**：Ralph Loop（迭代开发 + 跨模型评审）、RPI Recipe 套件（Research→Plan→Implement）、Terminal-Bench 风格 headless 运行、`GOOSE_ALLOWLIST` 企业白名单。

---

## 2. Recipes 对标

**定义（官方原文）**：Recipes 是 *"reusable workflows that package extensions, prompts, and settings together"*。

| 维度 | goose Recipes | 通用工作台的「提示词预设 / 工作流模板」 |
|---|---|---|
| 内容 | prompt + **extensions 绑定** + settings + parameters + subrecipes | 通常只有 prompt |
| 参数化 | 支持 `parameters`（有类型、可给默认值） | 通常无 |
| 调用 | Recipe Library / `goose run --recipe` / 绑成 slash command | 手动选 |
| 分享 | 本地库、GitHub 库、deeplink、`goose recipe` 子命令 | 复制粘贴 |
| 权限 | 可随 Recipe 固定 permission mode | 无 |

**关键差异**：Recipe 能**改变可用工具集和权限模式**，这是它比「提示词模板」强的地方。Subrecipe 支持嵌套，`tutorials/subrecipes-in-parallel.md` 还演示并行跑子 recipe。

---

## 3. 添加 MCP 的四条途径

| 途径 | 操作 |
|---|---|
| CLI 一步装 | `goose mcp <name>`（直接按名字装官方收录的扩展） |
| 交互式配置 | `goose configure` → **Add Extension** → 选 `Built-In` / `Command-Line (stdio)` / `Remote (Streamable HTTP)` |
| Deeplink | `goose://extension?cmd=npx&arg=-y&arg=<pkg>&id=<id>&name=<Name>&description=<desc>` |
| 手写配置 | 编辑 `~/.config/goose/config.yaml` 的 `extensions:` 段 |

- 会话内查看：`/extension`（列出已启用）、`/builtin`（列出内置）
- 移除：`goose configure` → Remove Extension，或删 config.yaml 条目
- 开关：`goose configure` → **Toggle Extensions**（空格切换）
- 企业白名单：`GOOSE_ALLOWLIST` 环境变量指向一个 YAML 白名单文件
- 安装命令必须能被 shell 找到（`npx` / `uvx` / 二进制），否则扩展加载失败

---

## 4. Skills 的增 / 删 / 改

Skills 就是文件系统上的 `SKILL.md`，**没有 GUI 编辑器**——增删改 = 增删改 Markdown 文件。

| 动作 | 做法 |
|---|---|
| 新增（全局） | `mkdir -p ~/.agents/skills/<name>` → 写 `SKILL.md` |
| 新增（项目级） | `<project>/.agents/skills/<name>/SKILL.md` |
| 随插件分发 | `~/.agents/plugins/<plugin>/skills/<name>/SKILL.md` |
| 编辑 | 直接改 `SKILL.md` 正文 |
| 删除 | 删除整个 skill 目录 |
| 查看 | `goose skills list` 或会话内 `/skills` |
| 安装现成 skill | 如 `browser-use skill install` |

`SKILL.md` 必需 frontmatter：

```markdown
---
name: my-skill
description: 一句话说明何时使用本 skill
---

正文：何时用、怎么做、可复用命令、坑。
```

- 可带支持文件（脚本 / 参考文档），skill 目录内相对引用
- 兼容目录：`.goose/skills/`、`.claude/skills/`（Claude Agent Skills 格式直接可用）
- 内置 skill：`web-search`

---

## 5. 对标「专家团」的是什么

**答案：Custom Agents**，叠加 Subagents + Plugins 才是完整对标。

| 维度 | Custom Agents | Subagents |
|---|---|---|
| 本质 | **角色定义**（Markdown + frontmatter） | **隔离实例**（独立 goose 进程） |
| 位置 | `~/.agents/agents/*.md` · `<project>/.agents/agents/*.md` | 运行时 spawn |
| 必需字段 | `name`（必填）；`description` / `model` 可选 | 无 |
| 调用方式 | ① `@code-reviewer` 提及 ② `Delegate to code-reviewer:` 委派到隔离会话 ③ `Load the code-reviewer agent` 加载进当前上下文 | goose 自主 spawn 或由 Recipe 显式 spawn |
| 上下文 | 三种调用方式上下文策略不同 | **默认保留独立上下文** |
| 并发 | 单角色 | sequential（默认）/ parallel |
| 能否再 spawn | 可以（官方：*"Yes, when delegation tools are available"*） | **禁止**（subagent 不能再 spawn subagent） |
| 默认步数 | — | Max Turns **25** / 超时 **5 分钟** |
| 覆盖 | — | `GOOSE_SUBAGENT_MAX_TURNS` / `GOOSE_SUBAGENT_MODEL` / `GOOSE_SUBAGENT_PROVIDER` |

**与「专家团」的实质差距**：goose 没有「多角色同屏协作 / 圆桌」UI；一个 agent 一次跑一个角色，编排责任在**你**或**Recipe**（例如 RPI 的 research 阶段固定 spawn 3 个并行 subagent）。官方 `custom-agents.md` 有一张 *"When to Use Agents, Skills, or Recipes"* 决策表。

Subagent 的安全约束（官方明示）：禁止 spawn 新的 subagent、禁止改 extension、禁止改 schedule。

---

## 6. 多模型同时对话

**不支持真正的「同屏并行多模型对话」。**

| 机制 | 实际行为 |
|---|---|
| `/model` | 会话内**切换**模型（一次只有一个在跑） |
| Subagents | 可各自跑独立 provider + model ⇒ 相当于「分工」，不是「同屏对比」 |
| Ralph Loop | worker / reviewer **双模型**（一个写、一个审）——唯一官方「双模型」范式 |
| `GOOSE_SUBAGENT_PROVIDER` / `GOOSE_SUBAGENT_MODEL` | 为 subagent 单独指定提供方与模型 |

若目标是「同一问题让多个模型各答一遍再对比」，goose 需要你自己跑多个会话或写 Recipe 编排，没有原生 UI。

---

## 7. plan / subagent 分派 / 循环步数

### 7.1 有没有 plan？

**没有内建 planner。** goose 是自主 agent（agentic loop），不是 plan-then-execute 架构。

官方给的 plan 方案是 **RPI Recipe 套件**（`tutorials/rpi.md`）：

| 阶段 | Slash Command | 产出 |
|---|---|---|
| Research | `/research_codebase "topic"` | `thoughts/research/YYYY-MM-DD-HHmm-topic.md`；**并行 spawn 3 个 subagent**：`find_files` / `analyze_code` / `find_patterns` |
| Plan | `/create_plan "feature"` | `thoughts/plans/YYYY-MM-DD-HHmm-desc.md`，含明确 phase、文件路径、代码片段、成功判据、checkbox |
| Implement | `/implement_plan "plan path"` | 逐 phase 执行 + 每 phase 后验证 + 回写 checkbox |
| Iterate | `/iterate_plan`（可选） | 只重研究变化部分，外科式改 plan |

官方实测数据：10 个 phase / 32 个文件 → Research 9 分钟 + Plan 4 分钟 + Implement 39 分钟 ≈ 52 分钟，PR 一次通过且 Code Review Agent 零评论。

### 7.2 会不会分派 subagent？

**自主决定**（仅在 Completely Autonomous 模式下允许自动 spawn），也可由用户显式 `Delegate to`，或由 Recipe 固定 spawn。

### 7.3 循环步数（最接近 librechat「agent 循环步数」的设置）

| 层级 | 默认值 | 覆盖方式 |
|---|---|---|
| 主会话 Max Turns | **1000** | `GOOSE_MAX_TURNS` 环境变量；`goose session --max-turns` / `goose run --max-turns` |
| Subagent Max Turns | **25** | `GOOSE_SUBAGENT_MAX_TURNS` |
| Subagent 超时 | **5 分钟** | — |
| Ralph Loop 迭代次数 | **10** | `RALPH_MAX_ITERATIONS` |
| 工具调用次数 | 无独立上限（受 Max Turns + 权限模式约束） | — |
| Auto-Compaction 触发 | `min(80% 上下文窗口, 225,000 tokens)` | `GOOSE_AUTO_COMPACT_THRESHOLD` / `GOOSE_AUTO_COMPACT_TOKEN_LIMIT` |

官方 Max Turns 建议：探索 **5–10** / 中等任务 **25–50** / 复杂自动化 **100+**。

⇒ **对标 librechat 的「循环步数」：用 Ralph Loop 的 `RALPH_MAX_ITERATIONS` 或主会话 `--max-turns`。**

Ralph Loop 状态文件（`~/.goose/ralph/`）：`task.md` / `iteration.txt` / `work-summary.txt` / `work-complete.txt` / `review-result.txt` / `review-feedback.txt` / `.ralph-complete` / `RALPH-BLOCKED.md`。

---

## 8. Tool scaling（工具数量）与调控层级

**官方建议：启用工具总数 < 25。** 原文（`guides/managing-tools/tool-permissions.md`）：

> goose performs best with fewer than 25 total tools enabled

原因：减少 context window 占用、防止 *tool decision paralysis*（工具过多导致模型选错工具）。

| 调控机制 | 粒度 | 说明 |
|---|---|---|
| Extension 开关（`/extension`、`/builtin`、`goose configure` → Toggle Extensions） | 按扩展整体 | 主要手段 |
| **Tool Permissions** 三级（Always Allow / Ask Before / Never Allow） | 按工具 | 仅 Manual / Smart 模式生效 |
| **Permission Modes** 四种 | 全会话 | 见下表 |
| `GOOSE_ALLOWLIST` | 组织级 | 企业白名单 YAML |
| `adjust-tool-output.md` 相关设置 | 按工具输出体积 | 间接省 context |

四种 Permission Modes：

| 模式 | CLI 值 | 行为 |
|---|---|---|
| Completely Autonomous | `auto` | **默认**。全部自动执行，不问 |
| Manual Approval | `approve` | 每次工具调用都要批准 |
| Smart Approval | `smart_approve` | 只读操作自动，写/执行类询问 |
| Chat Only | `chat` | 不执行工具，只对话 |

会话内切换：`/mode`。

**结论**：工具总量无硬上限，但「性能拐点」在 25 个；控制手段是**关扩展 + 设权限**，不是设一个数字。

---

## 9. 与 Linux / 操作系统的耦合深度

**极深 —— 这是 goose 的设计核心，也是最需要设防的地方。**

Developer extension 暴露 5 个工具：

| 工具 | 参数 | 官方风险标记 |
|---|---|---|
| `shell` | `command`, `timeout_secs`(可选) | ⚠️ High |
| `write` | `path`, `content` | ⚠️ High |
| `edit` | `path`, `before`, `after` | ⚠️ High |
| `tree` | `path`, `depth` | ✅ Low |
| `read_image` | `source`, `crop`(可选) | ✅ Low |

关键事实：

- `shell` **继承 goose 进程环境**：`PATH` / `HOME` / `USER` / `AGENT_SESSION_ID`
- 以**当前用户权限**运行 —— 不是沙箱
- 默认权限模式是 Completely Autonomous ⇒ **默认不询问就执行**
- 因此：`bash` ✅、任意脚本 ✅（`chmod +x` 后直接跑）、`sudo` ⚠️ **取决于用户 sudoers 配置**（若配了 NOPASSWD，goose 可直接提权）
- 官方文档专门给了 **block-sudo hook 示例**（`PreToolUse` + `matcher: "^shell$"`）—— 说明官方认为 sudo 需要主动拦截
- Desktop / launcher 启动时**可能不加载 shell 启动文件**（`.bashrc` / `.zshrc`），导致 `PATH` 与终端不一致

隔离方案（官方教程）：`goose-in-docker.md`、`isolated-development-environments.md`；SECURITY.md 建议 gVisor / 容器 / VM。

Hook 可拦截的事件（与系统耦合相关的）：`BeforeShellExecution` / `AfterShellExecution` / `BeforeReadFile` / `AfterFileEdit` / `PreToolUse`。其中 **只有 `PreToolUse` 和 `Stop` 能阻断**，其余事件是观察性的。

---

## 10. 可视化面板与渲染能力

| 格式 | 支持 | 实现 |
|---|---|---|
| **Markdown** | ✅ 渲染 | Desktop / CLI 原生渲染助手输出 |
| **HTML** | ✅ 渲染 | ① **Apps extension**：单文件 HTML/JS/CSS 应用，存 `~/.local/share/goose/apps/`，在**沙箱独立窗口**运行，可从侧栏 `Apps` 页启动或导入他人 `.html` ② **MCP Apps**：可**内联在对话里**，也能全屏 / 画中画 |
| **图表** | ✅ 自动 | **Auto Visualiser** extension（内置）：Sankey / Radar / Donut·Pie / Treemap / Chord / Leaflet 地图 / Mermaid / 折线·柱状·散点。自动判断用哪种图，可导出为 HTML 分享 |
| **PDF** | ⚠️ **只能读，不能生成** | `pdf-mcp`（`uvx mcp-read-pdf`）提取文本；**没有内置 PDF 导出**。要出 PDF 得靠 shell 调外部工具（pandoc / wkhtmltopdf / headless 浏览器） |

注意：MCP Apps 官方标注为 **experimental**（行为与支持可能变）。Apps 内的 UI 可以调工具、读资源（受 CORS 限制），但**不能与 goose 对话**。

---

## 11. 知识库 / 切片 / 嵌入 / 重排 / 召回

**结论：goose 没有自研 RAG 栈。** 没有切片器、没有嵌入模型、没有向量库、没有重排、没有语义召回。

最接近的替代（**都不是 RAG**）：

| 需求 | goose 的替代 | 机制 | 是否语义检索 |
|---|---|---|---|
| 长期记忆 | **Memory extension** | 按 `category` + `tags` 存文本，落 `~/.config/goose/memory/` 或 `.goose/memory/`；工具 `remember_memory` / `retrieve_memories` / `remove_memory_category` / `remove_specific_memory` | ❌ 按标签 |
| 结构化记忆 | **Knowledge Graph Memory MCP** | 实体 + 关系图（`npx -y @modelcontextprotocol/server-memory`） | ❌ 图遍历 |
| 跨会话检索 | **Chat Recall** | **关键词**搜索历史会话（SQLite）；默认关闭；v1.14.0 前压缩过的会话不可搜 | ❌ 关键词 |
| 代码库进 context | **Repomix MCP** | 把仓库**压缩打包**成 AI 友好格式，省 token | ❌ 全量打包 |
| 实时文档 | **Context7 MCP** | 按库名拉取最新官方文档 | ❌ 在线拉取 |
| 代码结构索引 | **Analyze platform extension**（内置，默认开） | 三种模式（Structure / Semantic / Focus）+ 符号跨文件追踪 + 调用图（`follow_depth`）；输出 >50,000 字符时需 `force=true` | ❌ AST 级，但是**goose 里最接近「索引」的东西** |
| 语义记忆 | — | **无** | — |

**若要真 RAG**：接第三方向量库 MCP，或用 Memory / Knowledge Graph 近似。是否有社区 MCP 提供完整 RAG 链路（切片+嵌入+重排+召回）——**未核实**。

---

## 12. 一句话总结：goose 强在哪、缺在哪

| 维度 | goose | 典型「通用工作台」 |
|---|---|---|
| 系统耦合 | 极深（原生 shell / 脚本 / 提权） | 通常较浅或有沙箱 |
| 工具接入 | MCP 一等公民（73 篇 MCP 文档） | 视产品 |
| 角色 / 专家 | Custom Agents（文件式，无编排 UI） | 常见「专家团」编排 UI |
| 工作流 | Recipes（含 extensions + 权限绑定） | 通常只有提示词预设 |
| 循环控制 | 三层可设（主 1000 / sub 25 / Ralph 10） | 视产品 |
| 多模型 | 只能切换，不能同屏 | 部分产品支持并排对比 |
| 知识库 | **无 RAG** | 常自带 |
| PDF 产出 | **不能生成** | 常自带 |
| 可分享性 | Recipe deeplink / GitHub 库 / Plugin 包 | 视产品 |

---

## 13. 中文文档状态与翻译进度（2026-10-15）

### 官方是否有中文

**截至 2026-10-15，goose 官方文档没有官方中文版本。** 官方 Docusaurus 配置 `documentation/docusaurus.config.ts` 明确写 `defaultLocale: "en"`、`locales: ["en"]`，且仓库 `documentation/` 下没有 `i18n/` 目录。第三方中文介绍/教程不等于官方逐页翻译。

### 手册规模与完成状态

**已完成：22/22 章、173/173 页面节，全量交付。**

| 项目 | 状态（截至 2026-10-15 17:40 GMT+8） |
|---|---|
| 源语料 | `aaif-goose/goose/documentation/docs/`，173 个 Markdown / MDX 页面，1,351,256 字节 |
| 分章 | 22 章，`groups.json` 核验覆盖 173/173 页；无重复、无遗漏 |
| 已产出 | **第 01–22 章全部完成**，173 个 `## ` 页面节，每节带 `> 原文：` 出处 |
| 译文体积 | 1,287,665 字节 / 源 1,351,256 字节 = **95%**（落在 90%–130% 完整区间内） |
| 内容量 | 图片 30 · 代码块 1,089 · 表格行 808 · 标题 译 1,404 / 源 1,391 |
| 审计 | `_verify/audit_zh.py` 五项判据（页面节数 / 出处行 / 相对资源 / 围栏奇偶 / 体积）**22 章全 OK，零待修问题** |
| 手册总目录 | `goose-docs-zh/README.md`（953 行，含阅读建议 + 逐章逐页目录） |
| 单文件完整版 | `goose-docs-zh/goose-zh-完整版.md`（1,074,746 字节） |
| GitHub | `damongoh1031-design/share` → `goose-docs-zh/`，**commit `143193e`**，26 个文件；远端 blob 哈希 26/26 与本地逐一致 |

### 曾被阻塞的经过（已解除）

第 13–20 章补译阶段，多名并行翻译代理收到 **429 too many requests / usage exceeds frequency limit**（系统给出恢复时间 2026-10-16 11:41:47 UTC+8）。**2026-10-15 17:30 实测额度已恢复**，并行 7 章一次性跑通，全量完成。

方法论与踩坑已单独沉淀：[goose-docs-zh-translation-pipeline.md](goose-docs-zh-translation-pipeline.md)。

---

## 修订记录

- **1.2**（2026-10-15）：中文手册**全量完成**（22/22 章、173/173 页、95% 体积、五项审计全绿），已推送 commit `143193e` 并完成远端哈希复核；第 13 节改为完成状态，方法论外链至 `goose-docs-zh-translation-pipeline.md`。
- **1.1**（2026-10-15）：核实 goose 官方文档仅启用英文 locale；补记中文手册 22 章分组、14 章/81 页完成进度、部分 GitHub commit 与 429 额度恢复时间。
- **1.0**（2026-10-15）：初版 goose 能力对标速查。

---

## 可复用操作

### 查 goose 版本与命令面
```sh
goose --version
goose --help
goose skills list
goose plugin install <name> [--auto-update]
goose mcp <name>
goose configure          # Add / Remove / Toggle Extensions
```

### 会话内命令速查
```
/model <name>            # 切换模型
/mode <auto|approve|smart_approve|chat>
/extension               # 已启用扩展
/builtin                 # 内置扩展
/skills                  # 已加载 skills
/compact                 # 手动压缩上下文
@<agent-name>            # 提及 custom agent
/<recipe-command>        # 调用绑定到 recipe 的 slash command
```

### 关键环境变量
```sh
GOOSE_MAX_TURNS=1000
GOOSE_SUBAGENT_MAX_TURNS=25
GOOSE_SUBAGENT_MODEL=<model>
GOOSE_SUBAGENT_PROVIDER=<provider>
RALPH_MAX_ITERATIONS=10
GOOSE_AUTO_COMPACT_THRESHOLD=0.8
GOOSE_AUTO_COMPACT_TOKEN_LIMIT=225000
GOOSE_CONTEXT_STRATEGY=summarize   # summarize | truncate | clear | prompt
GOOSE_ALLOWLIST=/path/to/allowlist.yaml
GOOSE_STOP_HOOK_BLOCK_CAP=<n>
```

### 最小 Custom Agent（对标「专家」）
```markdown
<!-- ~/.agents/agents/code-reviewer.md -->
---
name: code-reviewer
description: 只做代码评审，不改文件
model: claude-sonnet-4-5
---

你是严格的代码评审者。只指出问题，不修改文件。
输出格式：问题 / 位置 / 为什么是问题 / 建议改法。
```
调用：`@code-reviewer 评审 src/` 或 `Delegate to code-reviewer: 评审 src/`

### 最小 Skill
```sh
mkdir -p ~/.agents/skills/my-skill
cat > ~/.agents/skills/my-skill/SKILL.md <<'EOF'
---
name: my-skill
description: 何时使用本 skill
---

步骤 / 命令 / 坑。
EOF
```

### 拦截 sudo（官方示例思路）
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "^shell$",
        "hooks": [{ "type": "command", "command": "${PLUGIN_ROOT}/scripts/block-sudo.sh" }]
      }
    ]
  }
}
```
`block-sudo.sh` 从 stdin 读 JSON payload，检查 `.tool_input.command` 是否含 `sudo`，命中则 stdout 打印 `{"decision":"block","reason":"..."}`。

---

## 坑与反直觉

1. **`shell` 工具默认免批准**，且默认权限模式是 Completely Autonomous —— 首次使用就要意识到这一点，不是「用了才会问」。
2. **Subagent 默认只有 25 turns**，比主会话的 1000 少 40 倍；复杂子任务会被截断，需要 `GOOSE_SUBAGENT_MAX_TURNS`。
3. **Subagent 不能再 spawn subagent**，也不能改 extension / schedule —— 想多级编排必须自己用 Recipe 串。
4. **Hooks 的 `matcher` 是正则不是 glob**：写 `"*"` 是非法正则，规则会被**静默跳过**（只在日志里警告）。要匹配全部用 `.*` 或省略 matcher。
5. **Hook 的 stdout 是决策通道**：脚本里 `echo "checking..."` 会让一个本来健康的 hook 被读成「无决策」。诊断信息必须走 stderr。
6. **只有 `PreToolUse` 和 `Stop` 能阻断**；`UserPromptSubmit` / `PostToolUse` / `Before*` / `After*` 的 block 会被忽略。
7. **`on_failure` 只对 `PreToolUse` 生效**，`Stop` 永远 fail-open。
8. **`SubagentStart` / `SubagentStop` 事件当前不会发出**，注册了也永不触发。
9. **Skills 没有 GUI**，增删改就是操作文件系统；`goose skills list` 只是查看。
10. **工具超过 25 个性能下降**，是官方明确写的拐点，不是经验值。
11. **PDF 只能读不能写** —— 以为能导出 PDF 会踩空。
12. **Chat Recall 默认关闭**，且 v1.14.0 之前压缩过的会话搜不到。
13. **Desktop 启动可能不加载 `.bashrc`**，`PATH` 与终端不一致，扩展/脚本找不到命令。
14. **MCP Apps 是 experimental**，行为可能变；Apps 内的 UI 不能反过来和 goose 对话。
15. **Custom Agents 三种调用方式上下文不同**：「提及」在当前上下文，「委派」到隔离会话，「加载」把角色指令塞进当前上下文 —— 选错会污染或丢失上下文。

---

## 未核实 / 存疑

1. 是否存在社区 MCP 提供**完整 RAG 链路**（切片 + 嵌入 + 重排 + 语义召回）——未核实。
2. 通用工作台侧功能（如「专家团」的具体实现细节）为**本文了解**，非该产品官方文档来源；对标结论按功能语义匹配，不保证术语一致。
3. goose 的 `shell` 在 Windows 上的行为细节（是否走 Git Bash / WSL）未逐条核实。
4. 各 MCP 文档（73 篇）未逐篇读完，仅读了与本次 11 问相关的 20+ 篇；剩余部分可能包含额外能力。
5. Auto Visualiser 的导出 HTML 是否可直接作为交付物分发（是否自包含）未实测。
