# D 类｜Agent-IDE / 编码工作台（6 个）

> 这一类是"以编码为唯一场景的 Agent 工作台"：工具集（文件读写、终端、git、代码检索）与上下文全部围绕软件工程，交付物是代码变更。
> **2026 年这一类的关键词是"洗牌"**：6 个项目里已有 2 个停运、2 个停滞。
> 数据快照：2026-10-14 · 标注 `[不确定]` 的为未能一手核实项

---

## D 类与 C 类的边界

很多人会困惑：OpenHands 也能写代码，为什么不算 D 类？

区别在**目标**：
- **D 类**（Cline、Aider 等）：目标是"**在你的代码仓库里完成代码变更**"，工具与上下文都锚定在 IDE / 仓库内，人在环中。
- **C 类**（OpenHands、Open Interpreter 等）：目标是"**操作电脑完成任意任务**"，编码只是其中一种能力，可跑在沙箱/云上独立运行。

简言之：D 类是"**副驾驶 / 结对程序员**"，C 类是"**数字员工**"。

---

## 1. Cline

> **定位**：VS Code / JetBrains 内最流行的开源自主编码 Agent 插件
> **仓库**：https://github.com/cline/cline · **Star**：70,289 · **License**：Apache-2.0 · **语言**：TypeScript · **维护方**：Cline Bot Inc.（美国，创始人 Saoud Rizwan） · **状态**：✅ 高度活跃

### 它是什么

Cline 是 D 类中 Star 最高的项目（70,289），也是"VS Code 插件形态编码 Agent"的标杆。

它的核心设计是 **Plan / Act 两阶段模式**：
- **Plan 阶段**：Agent 在只读模式下探查代码库，给出方案，**不修改任何文件**
- **Act 阶段**：用户确认后，Agent 才进入可修改文件、执行命令的执行态

这个"先规划后执行"的分离极大降低了误改风险，也让人更容易判断 Agent 是否理解了需求。

配套的 **Checkpoint 快照机制**是另一个关键设计：每一步改动都可回滚，配合编辑器内的 **diff 预览**，让你能清楚地看到"它到底改了什么"。它还是较早推动 MCP 客户端生态的编码 Agent 之一。

### 核心架构与编排范式

- **单 Agent 循环**，核心为 Plan / Act 两阶段
- **Checkpoint 快照**：每步可回滚
- **三种形态**：IDE 插件（VS Code / JetBrains）+ CLI + 可编程 SDK
- **BYOK**：模型与工具均开放，不绑定单一厂商

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置文件创建/读取/编辑、终端命令执行、浏览器操作（Computer Use）、网页抓取；支持 MCP 扩展 |
| **记忆机制** | 通过项目根目录规则文件（`.clinerules`）与社区常用的 **Memory Bank** 模式实现跨会话项目记忆（文件持久化，非向量记忆） |
| **MCP 支持** | ✅ 原生支持（较早推动 MCP 客户端生态） |
| **沙箱/执行** | ⚠️ **无隔离沙箱**，直接在本机工作区读写文件并执行终端命令（能力等价于用户本人操作） |
| **人机协作** | ⭐ 默认逐步审批：每次文件修改/命令执行均需确认，可开 auto-approve；提供 diff 预览与 Checkpoint 回滚 |
| **RAG** | 无内置向量 RAG；通过代码库检索与文件上下文注入实现上下文管理 |

### 快速上手

```bash
# IDE 插件（推荐）
# VS Code / Cursor / Windsurf / VSCodium / Antigravity：
#   Ctrl/Cmd+Shift+X → 搜索 "Cline" → Install
# JetBrains：插件市场搜索 Cline（插件 ID 28247）

# CLI（需 Node 20+，推荐 22）
npm install -g cline
cline auth
cline "refactor the auth module and add tests"

# SDK
npm install @cline/sdk
```

**前置要求**：CLI 需 Node 20+（推荐 22）；需模型访问（Cline Provider 按量付费 / ClinePass 订阅 / 自带 provider key）。
**上手难度**：★★☆☆☆ —— IDE 插件一键安装，CLI 仅需 Node。

### 差异化特色

1. **Plan/Act 两阶段执行范式**：先规划后执行，兼顾自主性与可控性
2. **Checkpoint 快照机制**：每步改动可回滚，配合 diff 预览降低误改风险
3. **原生 MCP 支持 + BYOK**：模型与工具均开放
4. **提供 IDE 插件 / CLI / SDK 三种形态**，可被二次开发集成

### 局限与风险

1. **Token 消耗大、成本高**（自主多步循环易烧钱），需自备 API Key
2. 复杂任务可能偏离目标或陷入循环，需要人工及时纠偏
3. 默认逐步审批在长任务中点击负担较重；**无官方中文文档**

### 适合谁 / 典型场景

跨多个文件的重构与功能开发（如新增 API 端点并同步改测试）；需要执行终端命令的自动化任务（安装依赖、跑测试、修复报错）；在 IDE 内以自然语言完成端到端小功能交付。

---

## 2. Aider

> **定位**：终端内的 AI 结对编程工具，以 git 原生工作流为核心
> **仓库**：https://github.com/Aider-AI/aider · **Star**：49,539 · **License**：Apache-2.0 · **语言**：Python · **维护方**：Paul Gauthier（创始人）及社区 · **状态**：⚠️ 活跃度下降（最后提交 2026-05-22）

### 它是什么

Aider 是"终端党"的最爱，它的两个设计在 D 类里独树一帜：

**① git 原生**
每一次 AI 修改都**自动生成一个 git commit**。这意味着：
- 不满意？`/undo` 一条命令回退
- 想看改了什么？`git diff` 或 `git log` 一目了然
- 每个改动都有提交信息，可追溯

这个设计把"版本控制"变成了 Agent 的安全网——比任何快照机制都更符合工程师的习惯。

**② 仓库地图（repo map）**
这是 Aider 的**核心技术特色**：用 **tree-sitter** 解析代码符号，为整个代码库构建一张**紧凑的结构化地图**注入上下文。这样 Agent 不需要把全部代码喂给模型，也能"理解"整个仓库的结构——在大型代码库中显著节省 Token 并提升定位准确度。

需要留意的信号：**Aider 最后提交为 2026-05-22**，约 5 个月未更新，新特性迭代停滞。

### 核心架构与编排范式

- **单 Agent 循环**，通过 `/chat`、`/code` 等斜杠命令驱动
- **编辑文件—提交—回退闭环**：以 git 提交为原子单位
- **纯终端工作流**：无 GUI、无 IDE 依赖
- **可脚本化/批处理**：适合融入 CI

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | ⚠️ **工具面较窄**：主要能力是编辑文件（以 diff 格式写回）+ 通过 `--test` 运行测试命令；不内置浏览器等工具 |
| **记忆机制** | 以会话历史 + git 提交记录承载；无长期向量记忆 |
| **MCP 支持** | ❌ **不支持 MCP**（核心设计未纳入） |
| **沙箱/执行** | 本地执行，直接读写文件与 git；无隔离沙箱 |
| **人机协作** | ⭐ 每次改动自动生成 git commit，用户可 review、`/undo` 回退，天然与版本控制结合 |
| **RAG** | ⭐ **核心特色为仓库地图（repo map）**：tree-sitter 解析代码符号构建结构化代码库地图注入上下文 |

### 快速上手

```bash
# 推荐：独立环境安装
python -m pip install aider-install
aider-install

# 一行脚本
# Mac/Linux:
curl -LsSf https://aider.chat/install.sh | sh
# Windows PowerShell:
powershell -ExecutionPolicy ByPass -c "irm https://aider.chat/install.ps1 | iex"

# uv / pipx / pip
uv tool install --force --python python3.12 --with pip aider-chat@latest
pipx install aider-chat
python -m pip install -U --upgrade-strategy only-if-needed aider-chat
```

```bash
cd /to/your/project
aider --model sonnet --api-key anthropic=<key>
# 或 aider --model deepseek --api-key deepseek=<key>
```

**前置要求**：Python 3.8–3.13（pipx 3.9–3.12、pip 3.9–3.12）；模型 API Key（Anthropic/OpenAI/DeepSeek 等）。
**上手难度**：★★☆☆☆ —— 一行脚本安装，纯 CLI 交互，Git 原生集成。

### 差异化特色

1. **git 原生**：每次 AI 修改自动生成 commit，可随时回滚、可追溯、易 diff
2. **仓库地图（repo map）**：基于 tree-sitter 提取符号构建结构化代码库地图，是其在大型仓库中高效利用上下文的独特技术
3. **纯终端工作流**，模型无关且支持本地模型，轻量无 IDE 依赖
4. **可脚本化/批处理**，适合融入 CI 或自动化流程

### 局限与风险

1. 无 GUI，仅终端形态，对不熟悉命令行的用户门槛较高
2. ⚠️ **活跃度下降（2026-05 后无提交），新特性迭代停滞**
3. **工具能力偏窄**（无浏览器/MCP），大型仓库 repo map 仍会消耗可观 Token

### 适合谁 / 典型场景

终端内对现有仓库进行多文件修改与重构（自动提交便于回退）；在大型代码库中借助 repo map 做定向修改，控制上下文规模；以脚本/批处理方式批量应用代码变更。

---

## 3. Continue

> **定位**：可自托管模型的开源编码助手/Agent，强调企业私有化部署
> **仓库**：https://github.com/continuedev/continue · **Star**：36,218 · **License**：Apache-2.0 · **语言**：TypeScript · **维护方**：Continue Dev, Inc.（美国·旧金山） · **状态**：✅ 活跃

### 它是什么

Continue 的差异化在两点：

**① 三位一体的 IDE 集成**
它不只是"Agent 插件"，而是同时提供**内联代码补全（autocomplete）+ 聊天问答 + Agent 模式**三种能力。这跟 Cline 那种"纯 Agent"定位不同——Continue 更像"一个完整的 AI 编码助手"，Agent 只是其中一种模式。

**② 强私有化 / 自托管**
它最强调的是**企业私有化部署**：可以完全本地运行、对接企业自有或本地模型（Ollama 等），**数据不出内网**。对于金融、政企等对数据合规有硬要求的团队，这是关键卖点。

配置方式是**声明式的**：通过 `config.yaml` / Continue Hub 定义助手（Assistants）、模型与上下文策略，团队可以统一规范。它也是本次调研中**唯一明确带代码库索引检索（`@codebase`）**的编码工作台。

### 核心架构与编排范式

- **单 Agent 循环** + 可配置的 Assistants / 规则体系
- **四种模式**：Agent / Chat / Edit / Autocomplete
- **CLI（`cn`）**：面向终端
- **config.yaml / Continue Hub**：声明式配置助手、模型与上下文策略

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置读写文件、代码检索、终端等工具；支持 MCP 扩展 |
| **记忆机制** | 以规则文件与 `@`-提及的上下文管理为主，无长期向量记忆 |
| **MCP 支持** | ✅ 支持 |
| **沙箱/执行** | 本地执行（读写文件/终端），无隔离沙箱 |
| **人机协作** | 提供审批与可配置的确认机制，权限与自动化程度可按助手配置 |
| **RAG** | ✅ 内置 **`@codebase` 代码库检索（索引式）**，并支持接入文档/知识源 |

### 快速上手

```bash
# VS Code 扩展：Marketplace 搜索 "Continue"（Continue.continue）
# JetBrains：Marketplace 插件 22707
# CLI：cn
```

```yaml
# ~/.continue/config.yaml
models:
  - name: Claude
    provider: anthropic
    model: claude-sonnet-4
    apiKey: ${{ secrets.ANTHROPIC_API_KEY }}
```

> ⚠️ 配置文件名与字段本次未从官方页面确认，请以官方文档为准。

**前置要求**：VS Code 或 JetBrains；模型 API Key 或本地模型（Ollama）。
**上手难度**：★★☆☆☆ —— 插件市场一键装，配置文件化。

### 差异化特色

1. **补全 + 聊天 + Agent 三位一体**的深度 IDE 集成，区别于纯 Agent 插件
2. **config.yaml / Hub 可编程配置**助手、模型与上下文，适合团队统一规范
3. **强私有化/自托管能力**，可对接企业自有或本地模型，数据不出内网
4. **企业化支持**：商业实体运营，文档较完善

### 局限与风险

1. 功能面广、配置项多，`config` 上手成本较高
2. 纯 Agent 自主能力相对 Cline / Roo 偏弱，更偏"辅助"定位
3. 部分高级能力与企业功能绑定，开源版与商业版边界需留意

### 适合谁 / 典型场景

企业内网环境中以私有/本地模型提供 IDE 编码助手；日常编辑器内代码补全与代码库问答（`@codebase`）；通过自定义助手固化团队编码规范与上下文策略。

---

## 4. Roo Code

> **定位**：由 Cline 分叉演进的编码 Agent，主打"一整个 AI 开发团队"（多模式 Modes）
> **仓库**：https://github.com/RooCodeInc/Roo-Code · **Star**：24,281 · **License**：Apache-2.0 · **语言**：TypeScript · **维护方**：RooCodeInc · **状态**：❌ **已停运归档（2026-05-15）**

### 它是什么

Roo Code 从 Cline 分叉而来，最大的创新是**模式系统（Modes）**：内置 **Code / Architect / Ask / Debug** 等多个角色，每个 Mode 可以**限定不同的工具权限**。比如 Architect 模式只能读和规划、不能改文件；Code 模式才能写代码。这相当于把"一个人干完所有事"拆成"一个团队分工协作"。

它对 **MCP 的集成也很激进**，曾提供 MCP 服务市场式的扩展体验。规则文件（`.roorules`）高度可定制，适合团队固化编码规范。

**但项目已经停运了。** 官方于 **2026-05-15 停止运行**，GitHub 仓库归档（`archived=true`），官网 roocode.com 现跳转至云端 Agent 产品 **Roomote**。社区由 **Kilo Code、Zoo Code、CodeDeeper** 等 fork 接力。

> **选型结论：新用户不建议再选 Roo Code。** 老用户应迁移到上述 fork 之一。这个案例本身也很有说明性——它反映了"VS Code 插件形态"可能正在被"云端沙箱 Agent"取代。

### 核心架构与编排范式

- **多角色模式编排**：内置 Code / Architect / Ask / Debug 等 Mode，可自定义 Mode 并赋予不同角色与工具权限
- **通过切换角色完成规划、编码、调试分工**
- **对 MCP 集成激进**（曾提供 MCP 服务市场）

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置文件/命令/浏览器工具，并对 MCP 支持较为激进；可执行代码与命令 |
| **记忆机制** | 通过 `.roorules` / 自定义规则文件与 Mode 级指令实现持久化上下文 |
| **MCP 支持** | ✅ 原生支持（对 MCP 生态集成激进，是其主要卖点之一） |
| **沙箱/执行** | 本地执行，无隔离沙箱 |
| **人机协作** | 提供审批与 auto-approve 选项，可按 Mode 配置权限边界 |
| **RAG** | 无内置向量 RAG |

### 快速上手

```bash
# VS Code Marketplace（推荐）
#   Ctrl/Cmd+Shift+X → 搜索 "Roo Code"（作者 RooVeterinaryInc）→ Install
# Open VSX：用于 VSCodium / Windsurf 等
# VSIX 手动安装：从 GitHub Releases 下载 .vsix → 扩展视图 "..." → Install from VSIX
# 另有 Roo Code Nightly 预发布版
```

**前置要求**：VS Code **1.84.0+**；模型 provider API Key。
**上手难度**：★★☆☆☆ —— 插件市场一键装，配置简单。

### 差异化特色

1. **模式系统（Modes）**：内置+可自定义角色，可限定每个 Mode 的工具权限
2. **对 MCP 集成激进**，支持 MCP 服务市场式扩展
3. **规则文件（`.roorules`）高度可定制**，适合团队固化规范

### 局限与风险

1. ⚠️ **官方已停运、仓库归档、不再更新，存在安全与兼容性风险**
2. ⚠️ **新用户不建议再选**；老用户需迁移到 Kilo Code / Zoo Code / CodeDeeper 等 fork
3. MCP 激进集成带来配置复杂度与稳定性波动

---

## 5. Void

> **定位**：开源的 AI 代码编辑器（VS Code fork），定位为 Cursor 的开源替代方案
> **仓库**：https://github.com/voideditor/void · **Star**：28,759 · **License**：Apache-2.0 · **语言**：TypeScript · **维护方**：Void 团队 · **状态**：❌ **已弃用并归档**

### 它是什么

Void 走的是另一条路：不是做插件，而是**fork VS Code 做一个独立的 AI 编辑器**——直接对标 Cursor，但开源、隐私友好（模型自带 Key、代码不上传第三方）。

它曾获得 28,759 Star，社区期待很高。但功能上一直比 Cursor "极简"：**缺少代码库索引、MCP、Rules** 等关键能力。

**项目已于 2026 年初暂停开发，README 明确标注 "Void is now deprecated... no longer accepting contributions"**，仓库归档，最后提交 2026-06-02。

> **选型结论：不建议新项目采用。** 但它作为"VS Code fork 的最佳参考实现"仍有价值——新 fork 列表见 `github.com/voideditor/void-forks`。

### 核心架构与编排范式

- **单 Agent 循环**，支持内联改写（inline edit）、聊天与基础 Agent 模式
- **VS Code fork 架构**：React + Tailwind 挂载、EditCodeService 等
- **自定义 AI provider**（FIM 自动补全等）

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | ⚠️ 能力较基础：以内联编辑与文件改写为主，工具生态薄弱 |
| **记忆机制** | 无长期记忆机制 |
| **MCP 支持** | ❌ 不支持（相较 Cursor 缺少 MCP、Rules 等高级配置） |
| **沙箱/执行** | 本地编辑，无隔离沙箱 |
| **人机协作** | 以内联 diff 预览与编辑确认为主 |
| **RAG** | ❌ 无（相较 Cursor 缺少代码库索引/后台代理等高级能力） |

### 快速上手

不适用（已停止维护）。旧版本可从仓库 Releases 下载。

### 差异化特色

1. **基于 VS Code fork 的开源 AI 编辑器**，是 Cursor 开源替代路线的代表
2. **隐私友好**：模型自带 Key、代码不上传第三方（自托管/直连模型）
3. **开源可控**，支持本地模型（Ollama）
4. 作为 VS Code fork 的架构参考仍有价值

### 局限与风险

1. ⚠️ **已弃用并归档，2026 年初起停止主动开发，无法获得新功能与安全修复**
2. 功能相较 Cursor 明显"极简"，缺乏代码库索引、MCP、Rules 等
3. 开发中断，社区生态难以为继

---

## 6. bolt.diy

> **定位**：bolt.new 的官方开源版本，在浏览器内生成/运行/部署全栈 Web 应用
> **仓库**：https://github.com/stackblitz-labs/bolt.diy · **Star**：约 20,000 · **License**：MIT（WebContainers API 企业部署另有商业许可） · **语言**：TypeScript · **维护方**：社区项目（stackblitz-labs 组织，最初由 Cole Medin 发起） · **状态**：⚠️ 维护模式（不再计划新功能）

### 它是什么

bolt.diy 是 **bolt.new 的开源版**，核心技术是 **StackBlitz 的 WebContainers**——它让你在**浏览器里**跑一个完整的 Node.js 运行时，包括终端和文件系统。所以你可以：用自然语言描述一个全栈应用 → 它生成代码 → 在浏览器里实时运行 → 一键部署。

它跟 bolt.new / v0 最大的区别是**模型自由**：支持 **22+ 模型提供方**（OpenAI、Anthropic、Gemini、Groq、xAI、DeepSeek、Mistral、HuggingFace、Ollama、LM Studio、OpenRouter 等），基于 Vercel AI SDK，你可以自由切换对比生成效果。

它还有一个独特的安全优势：**代码跑在浏览器沙箱（WebContainers）里，不触碰本机文件系统**。

需要留意两点：① README 明确表示 **"不再计划新功能（no new features are planned）"**，处于维护模式；② 底层依赖 **WebContainers API**，企业部署受其商业许可条款约束。

### 核心架构与编排范式

- **单 Agent 循环**：提示词 → 生成代码 → 实时预览 → 迭代修改
- **WebContainers 运行时**：浏览器内隔离的 Node.js 环境（含终端、文件系统）
- **快照恢复**：项目快照机制
- **Git 集成**：克隆/推送、ZIP 导出
- **一键部署**：Netlify / Vercel / GitHub Pages

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 依托 WebContainers 在浏览器内运行 Node.js 运行时、终端与文件系统；支持文件冲突锁、快照恢复、代码库搜索、Git 克隆/推送、ZIP 导出；支持 MCP 工具 |
| **记忆机制** | 会话内上下文 + 项目快照（snapshot）机制，无长期向量记忆 |
| **MCP 支持** | ✅ 支持（可在提示附件菜单选择 MCP 工具） |
| **沙箱/执行** | ⭐ **浏览器内 WebContainers 沙箱**（隔离的 Node.js 运行时），不触碰本机文件系统 |
| **人机协作** | 实时预览 + 可视化 diff 查看 + 快照恢复，用户可逐步确认与回退 |
| **RAG** | 无内置向量 RAG；提供代码库搜索 |

### 快速上手

```bash
# 前置：Node >= 22.12.0、pnpm >= 9.15.9（npm install -g pnpm）
git clone https://github.com/stackblitz-labs/bolt.diy.git && cd bolt.diy
pnpm install && pnpm run dev        # → http://localhost:5173

# Docker
cp .env.example .env.local
docker compose --profile development up          # 开发
pnpm run dockerbuild:prod && docker compose --profile production up   # 生产

# 桌面版：Releases 下载 Electron 二进制，或 pnpm electron:build:dist
```

```bash
# .env.local 中填入：
# ANTHROPIC_API_KEY=...  OPENAI_API_KEY=...  GEMINI_API_KEY=...
# OLLAMA_BASE_URL=http://127.0.0.1:11434
```

**前置要求**：Node ≥ 22.12.0、pnpm ≥ 9.15.9；模型 API Key 或本地端点。
**上手难度**：★★★☆☆ —— 需 Node/pnpm 构建，支持 Docker 与桌面版。

### 差异化特色

1. **基于 WebContainers 的浏览器内全栈运行环境**，无需本地安装 Node 即可生成并运行应用
2. **22+ 模型提供方自由选择**（区别于 bolt.new/v0 仅用 Claude 的单一模型策略）
3. **一键部署到 Netlify / Vercel / GitHub Pages**，并提供 Electron 桌面端
4. **内置 Supabase 集成、数据可视化图表与 MCP 工具**

### 局限与风险

1. ⚠️ **处于维护模式，不再新增功能，长期演进存疑**
2. 依赖 WebContainers API，**企业部署受其商业许可条款约束**
3. 面向原型/中小项目，复杂大型工程能力有限

### 适合谁 / 典型场景

用自然语言快速生成并预览全栈 Web 应用原型；在同一界面切换不同 LLM 对比生成效果；教学/演示场景下零环境搭建地构建和部署小应用。

---

## D 类横向速查

| 项目 | Star | License | 形态 | 记忆 | MCP | 上手 | 状态 |
|---|---|---|---|---|---|---|---|
| **Cline** | 70,289 | Apache-2.0 | IDE 插件 / CLI / SDK | `.clinerules` + Memory Bank | ✅ | ★★☆ | ✅ 高度活跃 |
| **Aider** | 49,539 | Apache-2.0 | 终端 CLI | git 提交历史 | ❌ | ★★☆ | ⚠️ 停滞（2026-05） |
| **Continue** | 36,218 | Apache-2.0 | IDE 插件 / CLI | 规则文件 + `@codebase` 索引 | ✅ | ★★☆ | ✅ 活跃 |
| **Void** | 28,759 | Apache-2.0 | 独立编辑器（VS Code fork） | 无 | ❌ | N/A | ❌ **已弃用** |
| **Roo Code** | 24,281 | Apache-2.0 | IDE 插件 | `.roorules` + Mode 指令 | ✅ | ★★☆ | ❌ **已停运** |
| **bolt.diy** | ~20,000 | MIT | 浏览器 / Docker / Electron | 项目快照 | ✅ | ★★★ | ⚠️ 维护模式 |

### 这一类的三个关键判断

**1. 三个 VS Code 插件（Cline / Roo Code / Continue）的真实差异**

| 维度 | Cline | Roo Code | Continue |
|---|---|---|---|
| 模式系统 | Plan / Act 两阶段 | ⭐ 多 Mode（Code/Architect/Ask/Debug） | 无角色模式 |
| 上下文管理 | `.clinerules` + Memory Bank | `.roorules` + Mode 指令 | config 助手 + ⭐ `@codebase` 索引 |
| 定位 | 纯自主 Agent | 纯自主 Agent | 补全+聊天+Agent 三合一 |
| 状态 | ✅ 活跃 | ❌ 停运 | ✅ 活跃 |

**2. 为什么这一类在洗牌**

Roo Code 停运、Void 弃用、Aider 停滞，同时云端 Agent（如 Roo Code 的继任产品 Roomote）兴起——说明"**VS Code 插件**"这一形态可能正在被"**云端沙箱 Agent**"取代。插件形态的瓶颈在于：没有隔离、依赖本机环境、Token 成本由用户承担。

**3. 选型建议**

- VS Code 内日常开发 → **Cline**
- 企业私有化、要数据不出内网 → **Continue**
- 终端党、重视 git 可追溯 → **Aider**（但需接受其停滞）
- 浏览器内快速做原型 → **bolt.diy**
- **避开**：Void（已弃用）、Roo Code（已停运）
