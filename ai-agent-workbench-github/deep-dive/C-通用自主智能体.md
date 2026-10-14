# C 类｜通用自主智能体（11 个）

> 这一类是"你说它做"的通用助理：能操作电脑、浏览器、文件系统。**2026 年最热，也是安全风险最高的一类。**
> 数据快照：2026-10-14 · 标注 `[不确定]` 的为未能一手核实项

---

## 关于这一类的两条路线

在逐个介绍之前，先建立一个分类框架——C 类内部其实是两种不同的东西：

**路线一：本地个人 Agent（以 OpenClaw 为代表）**
核心卖点是**本地数据主权 + 消息渠道入口 + 技能生态**。你通过微信/Telegram 等 IM 给它下指令，它在你的电脑上执行。典型架构是"消息总线网关 + Agent 核心 + 技能库 + 定时任务 + 本地记忆"。代价是**通常没有沙箱**。

**路线二：任务型通用智能体（Manus 的开源平替们）**
核心卖点是**多步骤任务自动化的能力上限**。目标是对标 Manus、Devin、OpenAI Deep Research 这类闭源产品。代表有 OpenHands、Open Interpreter、OpenManus、Suna/Kortix、OWL。

**沙箱隔离是这一类最重要的选型维度**，下面每个项目都会明确标注。

---

## 1. OpenClaw ⭐ 本类最热

> **定位**：本地优先的开源个人 AI 助手 / Agent 运行时
> **仓库**：https://github.com/openclaw/openclaw · **Star**：391,937 · **License**：MIT · **语言**：TypeScript / Node.js · **维护方**：原 Peter Steinberger（奥地利），2026-02 起由独立基金会管理 · **状态**：✅ 极活跃（GitHub 历史上增长最快的项目之一）

### 它是什么

OpenClaw 是 2026 年整个开源 AI 领域最现象级的项目。它用约 4 个月时间斩获 30 万+ Star，并在 2026 年 3 月**超越 Linux 成为 GitHub 历史星标第一的项目**，最终稳定在 39 万量级。

它解决的核心痛点是：**大模型"只说不做"**。你告诉它"把下载目录里上周的截图按日期归档"，传统 ChatBot 会给你一段操作步骤；OpenClaw 会真的去读目录、建文件夹、移动文件。

它的关键设计是**本地优先（Local-First）**：数据、记忆、技能全部存在你的设备上，不上传云端。这让它在"个人数据主权"这件事上比所有云 Agent 都有说服力——也是它能引爆社区的根本原因。

### 核心架构与编排范式

OpenClaw 的架构是一条清晰的链路：**消息渠道 → 调度网关 → Agent 核心 → 技能库 → 心跳任务 → 本地记忆**。

- **Gateway 网关为中心的消息总线架构**：约 **26 个消息平台**（微信、Telegram、WhatsApp、Discord 等）的桥接收敛到**单个长驻 Node.js 进程**。这是它最核心的工程决策——所有入口统一到一个进程，再由它向内调度 LLM 调用、工具执行与记忆读写。
- **Gateway-Agent-Workspace 三层分层**
- **Heartbeat 心跳任务**：支持定时/周期性任务，让它能在你不主动说话时也干活
- **Skills 技能机制**：通过技能包扩展能力，与 MCP 并存
- **双模记忆系统**：文件驱动的本地持久记忆，跨会话"越用越聪明"

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 通过 **Skills（技能）+ MCP** 扩展；在授权下可执行任意操作——读写本地文件、调用系统命令、收发邮件、运行脚本 |
| **记忆机制** | 本地持久记忆：文件驱动设计 + 双模记忆系统，记忆存于本地，跨会话累积 |
| **MCP 支持** | ✅ 原生支持 MCP（并同时使用 Skills 技能机制） |
| **沙箱/执行** | ⚠️⚠️ **无沙箱隔离**——默认获取系统级读写、命令执行等高危权限，直接操作用户真实操作系统与文件系统 |
| **人机协作** | 默认以高权限自动执行，人工介入有限（需在授权/配置层面控制） |
| **RAG** | 以文件驱动的本地记忆为主，是否内置标准 RAG 检索管线未见权威一手说明 |

### 快速上手

```bash
# 社区一键安装脚本（第三方工具，非官方）
curl -fsSL https://raw.githubusercontent.com/miaoxworld/OpenClawInstaller/main/install.sh | bash

# 安装后自检
openclaw --version && openclaw doctor
```

> ⚠️ 上述命令来自第三方安装器仓库与中文教程，**非官方 README 原文**（官方仓库抓取失败）。请以官方文档为准。

**首次使用**：运行安装脚本自动检测环境并装依赖 → 脚本引导完成初始配置（模型/API Key、消息通道）→ 启动后用 `openclaw doctor` 自检 → 在聊天界面下达首个任务。
**中文支持**：**极强** —— 大量中文部署教程、国内加速安装镜像、CNCERT 中文安全指南、活跃中文社区。

### 差异化特色

1. **Gateway 为中心的消息总线架构**：20+ IM 平台桥接收敛为单一长驻进程，统一入口 + 调度 LLM/工具/记忆
2. **本地优先与数据主权**：数据与记忆存于本地设备，MIT 协议可商用可分发
3. **开放的技能生态**：官方 **ClawHub 技能市场** + 社区数千扩展技能 + 心跳定时任务 + 双模记忆
4. **增长极快**：2026 年成为 GitHub 历史星标第一的项目

### ⚠️ 局限与风险（本节必读）

1. **安全风险极高**：
   - **工业和信息化部于 2026-03-12 发布安全预警**
   - **国家互联网应急中心（CNCERT）会同中国网络空间安全协会于 2026 年 3 月联合发布《OpenClaw 安全使用实践指南》**，第一条建议即：**使用专用设备、虚拟机或容器安装 OpenClaw，并做好环境隔离**
   - 列举风险包括：密钥泄露、重要信息误删、功能插件（Skills）投毒、隐私泄露
2. **提示词注入**：网页/邮件中的隐藏恶意指令可诱导它泄露密钥或执行高危操作
3. **ClawJacked 远程控制漏洞**：诱导用户访问恶意网页即可远程控制本地 Agent
4. **权限失控与误操作**：默认系统级权限，可能误删文件/邮件/生产数据，造成不可逆损失；技能商店被指可能成为新攻击入口
5. **运营主体变更**：创始人为个人开发者且已加入 OpenAI，项目转由基金会管理，长期治理与稳定性待观察

### 安全加固建议

- **使用专用设备 / 虚拟机 / 容器安装**（CNCERT 首要建议）
- **权限最小化**：Skill 安装时检查权限清单（Tools / Paths / Network / Scripts），例如 `Tools: exec, browser, web_fetch`、`Paths: ~/Documents/, ~/.ssh/`、`Network: *.amazonaws.com`、`Scripts: setup.sh, sync.py`——含可执行文件与网络访问时务必警惕
- 关注官方 **RFC Issue #10890（Skill 安全框架）**：正在推进权限清单（permission manifests）、签名（signing）、沙箱化（sandboxing）、安装告警
- 可用 **E2B 等硬件级隔离方案**给 OpenClaw"戴安全锁"

### 适合谁 / 典型场景

个人与办公自动化（收发邮件、日程管理、文件整理、自动生成日报）；垂直行业深度应用（金融投研、生物医药研发流程）；通过 IM 渠道以自然语言远程指挥本地 Agent。

### 生态与社区

贡献者规模庞大（2026-03 已超 900 名贡献者、32,400+ Forks）；有 OpenClaw Meetup 线下活动；中文社区爆发式增长；腾讯（WorkBuddy、QClaw、SkillHub）、百度、字节跳动等推出兼容/简化部署方案。

---

## 2. AutoGPT

> **定位**：2023 年引爆自主智能体赛道的鼻祖，现演进为可视化 Agent 编排平台
> **仓库**：https://github.com/Significant-Gravitas/AutoGPT · **Star**：187,566 · **License**：混合/自定义（Platform 为 Polyform Shield，Classic 为 MIT） · **语言**：Python · **维护方**：Significant Gravitas（英国，创始人 Toran Bruce Richards） · **状态**：✅ 非常活跃

### 它是什么

AutoGPT 是 2023 年那个"AI 要自己干活了"的起点。它最早实现的是**自主循环**：Agent 自己 think → act → observe，不断迭代直到任务完成。这个概念在当年引发巨大轰动，也让"自主智能体"成为一个赛道。

但早期版本的问题也很明显：容易陷入死循环、API 费用失控、行为不可预测。所以 AutoGPT 做了一次重要的**战略转型**——从"自由循环的黑盒"转向**"可观测的 DAG 工作流"**。

现在的 AutoGPT 是**双轨架构**：
- **Classic**：保留原有的自由循环自主 Agent（终端形态）
- **Platform**：全新的可视化 **Builder**，用拖拽 **Block（积木）** 的方式搭建 DAG 工作流

这个转型很务实：承认"完全自主"在生产环境不靠谱，转而提供"可设计、可观测、有检查点"的流程编排。

### 核心架构与编排范式

- **Platform**：DAG（有向无环图）工作流执行引擎，每步有状态检查点、可观测
- **Classic**：单 Agent 自由循环（think→act→observe）
- **Block 积木式 Builder**：拖拽连线即可组合可运行、可复用的 Agent，无需手写代码
- **触发方式**：on-demand / 定时 / 触发器

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | Block 组件化工具（WebSearch、FileManager、代码执行、AI Text Generator 等），可插拔、可自定义封装内部接口 |
| **记忆机制** | 内置记忆系统 + 工作流持久化与数据在节点间流转 |
| **MCP 支持** | [不确定]（平台有丰富 Block 集成生态） |
| **沙箱/执行** | Docker 容器化部署，执行隔离 |
| **人机协作** | ✅ 可视化数据流实时查看、逐步骤检查、条件分支/循环/并行，可中断、调试、回放 |
| **RAG** | ✅ 有：数据采集/检索类 Block（如 Exa Websets 等），支持结构化抽取 |

### 快速上手

```bash
# 官方推荐路径：托管平台（付费，无需自建基础设施）
# 注册 https://platform.agpt.co/signup
# 自托管：官方单容器安装器尚未正式上线，需按手动指南
# 参考 https://docs.agpt.co/platform/getting-started
```

**首次使用**：注册托管平台（内置模型访问，**无需自备 API Key**）或按自托管指南配置 `.env` 与模型 Key → 打开 AutoPilot 对话或 Build 画布 → 用自然语言描述任务。
**最低资源**：自托管需 **Docker**（Linux 容器，amd64/arm64）。
**上手难度**：★★☆☆☆（托管）/ ★★★★☆（自托管，安装器尚未正式发布）。

### 差异化特色

1. **双轨架构**：Classic（自由循环）+ Platform（可视化 DAG），务实平衡自主性与可控性
2. **DAG 执行引擎**：从"不可预测的循环"变为"可设计的流程"，每步有状态检查点、可观测
3. **Block 积木式 Builder**：拖拽连线即可组合可运行的 Agent
4. **把"黑盒"Agent 变成"白盒"**——这是它最重要的设计哲学转变

### 局限与风险

1. 早期自主循环模式易陷入死循环、API 费用失控，需靠 DAG 与护栏约束
2. 可视化平台学习曲线较陡，Block 依赖顺序需谨慎设计
3. **许可为混合/自定义条款**（Platform 受 Polyform Shield 限制，不可作为竞品托管服务出售），商用需核对
4. 中文支持仅为第三方机翻链接

### 适合谁 / 典型场景

自动化调研（搜索-整理-生成报告）；内容生成与数据批量处理/结构化抽取；搭建个人/团队自动化助手与内部系统集成。

---

## 3. OpenHands（原 OpenDevin，现名 Agent Canvas）

> **定位**：开源 AI 软件工程智能体，Devin 的开源替代
> **仓库**：https://github.com/OpenHands/OpenHands · **Star**：90,847 · **License**：MIT · **语言**：TypeScript + Python · **维护方**：OpenHands 团队（美国·旧金山） · **状态**：✅ 非常活跃（v1.27.1）

### 它是什么

OpenHands 原名 **OpenDevin**，2024 年 3 月立项时明确以"**Devin 的开源替代**"为旗号（Devin 由 Cognition AI 出品，闭源、约 $500/月）。它用 MIT 协议把同等能力民主化。

它的核心创新是 **CodeAct 架构**：**把所有"动作"统一为可执行代码**，而不是 JSON 工具调用。也就是说，Agent 要浏览网页、执行命令、编辑文件，都是通过写一段代码来完成。这个统一抽象让它的端到端自主性显著强于同类。

它的能力标杆是 **SWE-bench Verified 约 53%+**（顶级模型下），属开源编码智能体第一梯队。

**2026 年重要变化**：项目已改名为 **Agent Canvas**，并提供了 4 种部署方式，安全模型也更明确。

### 核心架构与编排范式

- **CodeAct**：以可执行代码作为统一动作空间
- **单 Agent 自主循环** + 多 Agent 委派
- **GitHub 原生集成**：可 @OpenHands 自动修复 Issue 并提交 PR
- **多形态**：Web UI、CLI、Headless 无头模式、Python SDK

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置 Bash 终端、文件读写编辑、浏览器操作、API 调用；可执行任意代码、装依赖、跑测试；支持自定义工具 |
| **记忆机制** | 会话内上下文记忆，支持事件流与状态持久化（跨会话长期记忆能力有限） |
| **MCP 支持** | ✅ 支持（可接入外部 MCP 工具服务器） |
| **沙箱/执行** | ⭐ **Docker 容器沙箱隔离**，代码执行不污染宿主；支持每会话独立容器 |
| **人机协作** | ✅ 支持用户实时介入、审批与中断；通过 GitHub PR Review 进行人工把关 |
| **RAG** | 无独立内置 RAG 引擎，知识主要通过 microagents / 仓库上下文注入 |

### 快速上手（4 种官方方式）

```bash
# 方式1：无沙箱（⚠️ 警告：Agent 拥有完整文件系统访问权限！）
npm install -g @openhands/agent-canvas
agent-canvas                       # 需 Node.js 24+ 和 uv

# 方式2：Docker 沙箱（推荐）
export PROJECTS_PATH="$HOME/projects"
mkdir -p "$PROJECTS_PATH" "$HOME/.openhands"
docker run -it --rm \
  -p 127.0.0.1:8000:8000 \
  -e AGENT_CANVAS_ALLOW_LAN_SESSION_KEY=true \
  -v "$HOME/.openhands:/home/openhands/.openhands" \
  -v "${PROJECTS_PATH}:/projects" \
  ghcr.io/openhands/agent-canvas:1.27.1

# 方式3：多 Docker 沙箱（每个会话独立容器）
OH_CONVERSATION_RUNTIME=docker agent-canvas

# 方式4：源码
git clone https://github.com/OpenHands/OpenHands.git && cd OpenHands
npm install && npm run dev
```

**首次使用**：启动后访问 `http://localhost:8000` → 新建会话 → 配置 LLM（Bring your own model）→ 下达任务。
**最低资源**：方式 1/4 需 **Node.js 24+ 与 uv**；方式 2/3 需 **Docker**。
**上手难度**：★★★☆☆ —— 命令清晰、Docker 一行起，但需理解"沙箱 vs 非沙箱"的安全差异。

### 差异化特色

1. **CodeAct 架构**：把"动作"统一为可执行代码，端到端自主性更强
2. **SWE-bench Verified 约 53%+**（顶级模型下），开源编码智能体第一梯队
3. **Docker 沙箱 + 模型无关设计**，兼顾企业安全与成本优化
4. **GitHub 原生集成**：可 @OpenHands 自动修复 Issue 并提交 PR

### 局限与风险

1. 大型遗留系统的深层架构理解仍依赖人类架构师指导
2. 软件免费但顶级模型（如 Claude 4.5）API 成本可能不菲
3. 处理敏感代码库时需审慎配置网络与文件访问权限

### 安全加固建议（官方明确）

- 本地 `npx` / `npm run dev` 监听**仅绑定 loopback（127.0.0.1）**；若用 `--host 0.0.0.0` 则**不注入 session key**，改用 API Key 输入页
- Docker 默认监听所有容器接口；若发布到 LAN/公网，**必须省略 `AGENT_CANVAS_ALLOW_LAN_SESSION_KEY`** 并在 UI 输入 API Key
- 设置强 `LOCAL_BACKEND_API_KEY`，或用 `docker exec <container> sh -c 'cat "$STATE_DIR/api-key.txt"'` 取回自动生成的 Key
- ⚠️ 方式 1 与方式 4 有明确警告：**Agent 拥有完整文件系统访问权限**

### 适合谁 / 典型场景

自动修复真实 GitHub Issue 并提交 Pull Request；技术债清理、文档更新、测试补充等 7×24 小时低优先任务；通过 SDK 集成进 CI/CD 流水线。

---

## 4. Open Interpreter

> **定位**：终端里的 AI 编码智能体，专为低成本开源模型优化
> **仓库**：https://github.com/OpenInterpreter/open-interpreter · **Star**：68,574 · **License**：Apache-2.0 · **语言**：**Rust**（2026 年由 Python 重写） · **维护方**：Open Interpreter 团队（美国，创始人 Killian Lucas） · **状态**：✅ 活跃（已转型）

### 它是什么

Open Interpreter 原本是"让 LLM 在本地执行代码"的经典开源项目——你自然语言描述需求，它生成代码并在你电脑上跑。这个"本地执行"的概念在 2023-2024 年影响了大量后续项目。

**2026 年它做了一次大转型**：
- **用 Rust 重写**（原 Python 版由社区维护于 `endolith/open-interpreter`），性能与启动体验显著提升
- 定位从"通用本地代码执行"**收缩为"终端编码代理"**，基于 **OpenAI Codex 架构**重写
- **专为低成本开源模型调优**（Kimi K3、GLM 5.3、DeepSeek、Qwen），打破了"AI 编程代理只配旗舰模型"的默认假设——这是它现在最有价值的差异化

### 核心架构与编排范式

- **单 Agent 循环**：读代码 → 改文件 → 跑命令 → 审变更
- **`/harness` 执行框架切换**：可在 native / claude-code / zcode / kimi-code / qwen-code / deepseek-tui / swe-agent / minimal 等之间切换
- **会话恢复**：可随时 resume 之前的会话
- **ACP 协议**：可作为 ACP Agent 接入编辑器

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 读写文件、执行 shell 命令、审查代码改动；支持 permissions、hooks、MCP、skills |
| **记忆机制** | 支持会话恢复（resume），产品配置与会话状态存放于 `~/.openinterpreter` |
| **MCP 支持** | 支持（文档提及 MCP 与 skills）；主题含 ACP 协议 |
| **沙箱/执行** | ⭐ **内置原生沙箱**——在 macOS、Linux、Windows 上于原生沙箱内运行命令；有独立 Sandbox & approvals 文档 |
| **人机协作** | ✅ 保留执行前确认机制（approvals）+ permissions 机制 |
| **RAG** | 无内置 RAG/知识库 |

### 快速上手

```bash
# macOS / Linux
curl -fsSL https://www.openinterpreter.com/install | sh

# Windows (PowerShell)
irm https://www.openinterpreter.com/install.ps1 | iex
```

**首次使用**：用 `/model` 切换 provider/模型（或配置 OpenAI 兼容 Key）→ 终端输入 `i` 或 `interpreter` 启动 → 直接输入任务。
**最低资源**：无 Docker 强制要求（原生沙箱）。
**上手难度**：★★☆☆☆ —— 一条 curl 安装、`i` 即用；但 harness/provider 概念较多。
**中文支持**：✅ **官方简体中文 README**（`README_ZH.md`），另有 Español / 日本語。

### 差异化特色

1. **2026 年用 Rust 重写**，性能与启动体验显著提升
2. **专为低成本开源模型调优**（Kimi、GLM、DeepSeek、Qwen），大幅降低使用成本
3. **内置原生沙箱** + approvals 审批机制，安全模型比同类完整
4. **`/harness` 可切换多种执行框架**（含 claude-code、swe-agent 等），灵活性高

### 局限与风险

1. 定位已从"通用本地代码执行"收缩为"编码代理"，与原经典用途有差异
2. 依赖开源模型的能力上限，复杂任务效果不及顶级闭源模型
3. Rust 重写后生态与旧版插件/用法不兼容风险

### 适合谁 / 典型场景

在终端中用自然语言驱动读仓库、改文件、跑命令；以低成本开源模型完成日常编码/脚本任务；本地自动化（数据整理、批量文件处理）。

---

## 5. OpenManus

> **定位**：MetaGPT 团队开源的"Manus 平替"
> **仓库**：https://github.com/FoundationAgents/OpenManus · **Star**：58,635 · **License**：MIT · **语言**：Python · **维护方**：MetaGPT 团队 / FoundationAgents（中国） · **状态**：✅ 活跃维护

### 它是什么

2025 年 3 月，Manus 凭借"通用任务智能体"概念爆火但需要邀请码。**MetaGPT 团队在 3 小时内开源了 OpenManus**，号称"无需邀请码即可实现任何想法"，迅速成为 Manus 最知名的开源平替。

它的工程取向是"**开箱即用**"：默认集成 **Browser Use**（以 MCP 形式）做浏览器自动化，集成 **crawl4ai** 做网页抓取，还内置独立的 DataAnalysis Agent 做数据分析与可视化。安装完配好 `config.toml` 就能用。

它也有配套的研究项目 **OpenManus-RL**（与 UIUC 合作），基于 GRPO 等强化学习方法调优 LLM Agent。

需要留意：项目自我定位是"简单实现/原型"，多 Agent 流程（`run_flow`）被官方标注为 **unstable**；且**没有内置沙箱**。

### 核心架构与编排范式

- **单 Agent 循环**（OpenManus Agent）为主
- **可选多 Agent 工作流**（`run_flow.py` / PlanningFlow，官方标注 unstable）
- **DataAnalysis Agent**：独立的数据分析与可视化 Agent
- **MCP 集成**：Browser Use 作为默认 MCP Server

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 浏览器自动化（Browser Use CLI 3.0，含 browser_exec / browser_screenshot）、爬虫（crawl4ai）、Python 代码执行、文件操作 |
| **记忆机制** | 短期会话记忆（Memory 模块，记录对话与执行历史） |
| **MCP 支持** | ✅ 原生支持（提供 `run_mcp.py` 入口；Browser Use 作为默认 MCP Server） |
| **沙箱/执行** | ⚠️ **无内置沙箱**——在本机直接执行代码、操作文件与浏览器；浏览器侧靠 `uvx` 隔离依赖 |
| **人机协作** | 终端交互式执行，用户可在对话中给出指令与干预；无图形化审批流 |
| **RAG** | 主要依赖 crawl4ai 网页抓取与实时检索，未明确内置标准 RAG 知识库管线 |

### 快速上手

```bash
# 方式1：conda
conda create -n open_manus python=3.12 && conda activate open_manus
git clone https://github.com/FoundationAgents/OpenManus.git && cd OpenManus
pip install -r requirements.txt

# 方式2：uv（官方推荐）
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/FoundationAgents/OpenManus.git && cd OpenManus
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -r requirements.txt
```

**首次使用**：`cp config/config.example.toml config/config.toml` → 编辑 `[llm]` 段填 `api_key`/`base_url`/`model` → `python main.py` 启动 → 终端输入任务（多智能体用 `run_flow.py`，MCP 版用 `run_mcp.py`）。
**浏览器配置**：默认启动 `uvx browser-use --cli-mcp`（`uvx` 隔离依赖），本地模式自动连接 Chrome/Chromium 无需 Key；云浏览器需 `export BROWSER_USE_API_KEY="bu_..."`；用 `OPENMANUS_DISABLE_BROWSER_USE=1` 关闭默认 MCP 服务。
**最低资源**：Python 3.12；无 Docker 要求。
**上手难度**：★★★☆☆ —— 安装简单，但配置 `config.toml` + 浏览器依赖 + 无沙箱需自担风险。
**中文支持**：✅ **官方中文 README**（`README_zh.md`）+ **飞书交流群**。

### 差异化特色

1. **3 小时极速原型 + MetaGPT 团队背书**，成为 Manus 开源平替的标志性项目
2. **默认集成 Browser Use（MCP 形式）+ crawl4ai**，开箱具备浏览器操作与网页抓取
3. **官方配套 OpenManus-RL**（与 UIUC 合作，基于 GRPO 强化学习调优）
4. 支持通过 `config.toml` 挂载多 Agent 与 DataAnalysis Agent

### 局限与风险

1. 项目定位为"简单实现/原型"，多 Agent 流程（run_flow）被官方标注为 **unstable**
2. 依赖外部 LLM API key，复杂任务 token 消耗较大
3. ⚠️ **无内置沙箱，README 无专门安全章节**——因可执行本机命令，**建议自行用容器/VM 隔离**
4. 文档相对简略、内置 RAG/长期记忆能力有限

### 适合谁 / 典型场景

网页信息收集、整理与摘要（爬虫 + 浏览器自动化）；数据分析与可视化任务（DataAnalysis Agent）；通用多步骤任务自动化与想法验证。

---

## 6. Suna / Kortix

> **定位**：开源"AI 操作系统"，自我定位为 Claude Cowork / ChatGPT Work 的开源替代
> **仓库**：https://github.com/kortix-ai/suna · **Star**：20,273 · **License**：自定义（GitHub 识别 NOASSERTION） · **语言**：TypeScript · **维护方**：Kortix Inc.（美国） · **状态**：✅ 活跃维护

### 它是什么

Suna（名字是 Manus 倒过来写）2024 年 10 月开源，是 Kortix AI 用 3 周做出的 Manus 开源平替。**2026 年它已更名为 Kortix**，定位升级为"**开源 AI 操作系统**"，直接对标 Claude Cowork / ChatGPT Work。

它是本次调研中**企业级治理做得最完整**的通用智能体：

- **每个会话一台独立的隔离云沙箱**（microVM 或容器）+ **独立 git 分支**，产物通过 **change request 人工审查**后才合并
- **"一切即代码"**：Agent、技能、记忆、连接器、触发器都是 git 仓库里的文件，可版本化、可 diff、可 grep、全公司共享
- **按工具/参数的 Allow-Ask-Block 审批门**：细到每次调用的参数都能设"允许/询问/阻止"，Ask 会挂起直到人工批准
- 凭据由服务端代理，**原始 Key 不进沙箱**；secrets 静态加密 + 运行时注入
- SAML 2.0 SSO + SCIM 2.0、完整审计日志
- **Agent 合并默认拒绝（deny-by-default）**

这套设计让它成为"既要通用智能体能力、又要企业合规"时最有说服力的选择。

### 核心架构与编排范式

- **以"会话（session）"为单位的单 Agent 执行**（OpenCode agent）
- **组织级多 Agent 并行**：可并行数千个沙箱
- **每 session 独立沙箱 + 独立 git 分支**
- **多入口**：Web、Slack、Microsoft Teams、CLI、桌面端、移动端统一到同一会话
- **触发器**：cron 定时 / webhook 触发、无人值守运行

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 连接器生态 **3,000+ 应用**；支持 MCP、OpenAPI、GraphQL 与 raw HTTP；凭证由服务端代理 |
| **记忆机制** | 公司级"记忆"：以文件/git 仓库形式持久化，随项目版本化、可 diff、可 grep |
| **MCP 支持** | ✅ 支持（另有 OpenAPI/GraphQL/HTTP 等多种接入） |
| **沙箱/执行** | ⭐⭐ **每会话独立云沙箱**——Platinum provider 用 microVM，默认用容器；凭证服务端代理，仅提交内容得以保留 |
| **人机协作** | ⭐ 完善的审批机制：每个工具可设 Allow / Ask / Block（精确到参数），change request 默认 deny-by-default 由人审查合并 |
| **RAG** | 主要通过连接器与记忆文件实现知识调用 |

### 快速上手

```bash
# 安装 CLI
curl -fsSL https://kortix.com/install | bash
# 脚手架 + 上线
kortix init          # 生成 kortix.yaml + agents/skills/runtime 配置
kortix ship          # 推送仓库并在云上部署
# 自托管（一套 Docker Compose）
kortix self-host start
kortix hosts use selfhost   # ↔ kortix hosts use cloud
```

**首次使用**：注册 kortix.com（托管云，$40/座/月起）或 `kortix self-host start`（首次交互式设置只问集成凭据，端口/URL/Key/Docker 默认值自动生成）→ `kortix init` 生成项目 → `kortix sessions new --prompt "..."` 下达任务 → `kortix cr ls` 审阅变更请求。
**最低资源**：自托管需 **Docker Compose**。
**上手难度**：★★★☆☆ —— 三条命令起云版，自托管需理解 git-repo-as-config 与审批门模型。

### 差异化特色

1. **每会话一个隔离云沙箱 + 独立 git 分支**，产物经 change request 审批合并，天然可审计、可回滚
2. **"一切即代码"**：Agent、技能、记忆、连接器、触发器均为 git 文件，可版本化
3. **企业级治理最完整**：Allow-Ask-Block 审批门、审计轨迹、SAML SSO/SCIM、按项目加密密钥
4. **多入口统一会话**：Web、Slack、Teams、CLI、桌面与移动端

### 局限与风险

1. **许可为非标准（NOASSERTION）协议**，且核心价值依赖 Kortix Cloud，自托管虽有 Docker 栈但集成体验受限
2. 架构偏重（多服务 + 沙箱 + git 工作流），部署与运维门槛较高、资源占用大
3. 产品定位/命名较新（已从 Suna 转向 Kortix 品牌），生态与文档仍在快速演进
4. SOC 2 Type I 已取得、Type II 进行中（**厂商自述，未经独立验证**）

### 适合谁 / 典型场景

后台云端编码 Agent：每任务一个沙箱+分支，产出经审查的 change request；Slack / Teams 内团队级 AI 助手；替代 Zapier 式自动化：定时（cron）或 webhook 触发、无人值守运行。

---

## 7. OWL（Optimized Workforce Learning）

> **定位**：基于 CAMEL 框架的开源多智能体协作通用智能体
> **仓库**：https://github.com/camel-ai/owl · **Star**：20,151 · **License**：[不确定] GitHub 未检测到标准协议文件 · **语言**：Python · **维护方**：CAMEL-AI 团队/社区 · **状态**：✅ 活跃维护

### 它是什么

OWL 基于 **CAMEL 框架**构建，核心是 CAMEL 的 **role-playing（角色扮演）机制**：一个 User Agent 和一个 Assistant Agent 通过动态对话协商来完成任务分工。这与 CrewAI 的角色扮演不同——OWL 的分工是**动态涌现**的，而不是预先定义的固定 DAG。

它的能力标杆是 **GAIA 基准**：发布时（2025-03）取得 58.18 平均分、**开源框架第一**，后续提升至 69.09，仍称开源框架第一。

它整合了 CAMEL 生态的**上百种工具包**（在线搜索、浏览器自动化、多模态处理、文档解析、代码执行等），并原生支持 MCP。

> ⚠️ 两个重要提示：① **许可证不清晰**——GitHub 未检测到标准协议文件，商用合规性存疑；② 本次调研中官方 README 多次抓取返回空内容，其部署细节**未能一手核实**。

### 核心架构与编排范式

- **多 Agent 协作**：基于 CAMEL 的 role-playing 机制（User Agent + Assistant Agent 动态对话协商）
- **Planner / Workforce 式任务分解与协作**
- **动态分工**而非固定 DAG

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 集成 CAMEL 工具包（Toolkits，**逾百种工具**）：在线搜索（Google/DuckDuckGo/Baidu）、浏览器自动化（Playwright）、多模态处理、文档解析、代码执行等 |
| **记忆机制** | CAMEL ChatAgent 的记忆机制（短期会话记忆，可选长期/向量记忆） |
| **MCP 支持** | ✅ 原生支持（MCPToolkit） |
| **沙箱/执行** | ⚠️ 在本地环境执行代码与浏览器操作；**无内置强隔离沙箱** |
| **人机协作** | [不确定] 主要以自动化执行为主 |
| **RAG** | 支持文档解析与检索类工具（依托 CAMEL 工具包） |

### 快速上手

```bash
# ⚠️ 以下为常见做法，本次未能核实官方 README
git clone https://github.com/camel-ai/owl.git && cd owl
conda create -n owl python=3.11 && conda activate owl
pip install -r requirements.txt
playwright install
# 在 .env 配置 OPENAI_API_KEY 等
python owl/run.py     # 或使用 Streamlit Web UI
```

**部署形态**：提供 Docker 与 **Streamlit Web 界面**。
**最低资源**：[不确定]
**上手难度**：[不确定]（推断 ★★★☆☆）

### 差异化特色

1. **GAIA 基准表现领先**：发布时 58.18 平均分、开源框架第一；后续提升至 69.09
2. **原生集成 MCP**，并整合 CAMEL 生态上百种工具包（搜索/浏览器/多模态/文档/代码）
3. **基于 CAMEL 的多智能体 role-playing 协作范式**，动态分工而非固定 DAG
4. 提供 Docker 与 Streamlit Web UI，工程可用性较好

### 局限与风险

1. 🔴 **许可协议不清晰**（GitHub 未检测到标准协议文件），商用合规性存疑
2. 多智能体协作对模型能力与 token 消耗要求高，长任务成本与稳定性是常见痛点
3. ⚠️ **无强沙箱隔离**，工具调用（浏览器/代码）的稳定性与安全需自行加固
4. 中文支持依托 CAMEL-AI 中文社区，文档提供中文版本

### 适合谁 / 典型场景

真实世界网页调研与多来源信息汇总；多步骤通用任务自动化（跨搜索、浏览、文档、代码）；多模态/文档处理与研究型任务。

---

## 8. Agent Zero

> **定位**：具备完整（Docker 隔离）计算机环境的通用自主智能体框架
> **仓库**：https://github.com/agent0ai/agent-zero（早期为 `frdel/agent-zero`） · **Star**：19,458 · **License**：自定义开源协议（非 OSI 标准） · **语言**：Python · **维护方**：个人开发者 frdel → agent0ai 组织 · **状态**：✅ 活跃维护

### 它是什么

Agent Zero 的最大特色是**默认在 Docker 容器里运行**——它给 Agent 一个**完整的、隔离的 Linux 环境**（默认是 Kali Linux 系），Agent 在这个环境里拥有自己的终端、文件系统与浏览器。

这个设计解决了通用智能体最核心的安全问题：**Agent 的"破坏半径"被限制在容器内**，不会污染你的真实系统。在本次调研的 C 类项目里，这是安全边界最好的方案之一（另一个是 Suna/Kortix 的云沙箱）。

它还有两个特点：**层级多 Agent 架构**（上级 Agent 可以派生下属 Agent 并行协作）；以及**"透明 + 可定制"**——提示词、工具（叫 instruments）、记忆全部可改，适合开发者深度定制。

### 核心架构与编排范式

- **单 Agent 循环 + 层级式多 Agent**：上级 Agent 可派生下属 Agent 并行协作
- **instruments 工具集**：终端命令执行、Python 代码执行、文件读写、浏览器、搜索等
- **持久记忆**：跨会话保留，基于文件/向量方式
- **Web UI**：聊天界面 + 容器内终端/文件系统可视化

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 内置 instruments 工具集：终端命令执行、Python 代码执行、文件读写、浏览器、搜索等；提示词与工具可自定义/扩展 |
| **记忆机制** | 持久记忆（跨会话保留，基于文件/向量方式），可长期积累 |
| **MCP 支持** | ✅ 支持（作为 MCP 客户端接入外部工具） |
| **沙箱/执行** | ⭐⭐ **Docker 容器隔离为最大特色**——默认在隔离的 Kali Linux 容器中运行，Agent 拥有自己的终端/文件/浏览器环境，与宿主系统隔离 |
| **人机协作** | 通过 Web UI 交互与人工干预，可查看/中断执行过程 |
| **RAG** | [不确定] 支持文档/知识处理，是否内置标准 RAG 管线未一手确认 |

### 快速上手

```bash
# ⚠️ 典型用法（本次未能核实官方 README）
docker run -p 50001:80 agent0ai/agent-zero
```

**首次使用**：启动容器 → 浏览器打开 Web UI → 在 Settings 中填 LLM/API Key → 在对话框下达任务。
**最低资源**：**需要 Docker**；CPU/内存 [不确定]。
**上手难度**：[不确定]（按 Docker 一键部署的常见形态推断约 ★★☆☆☆）

### 差异化特色

1. **默认 Docker 容器隔离**：Agent 在独立 Linux 环境中拥有完整终端、文件系统与浏览器，**安全边界优于本地直跑方案**
2. **层级多 Agent 架构**：可自行派生下属 Agent 协同完成复杂任务
3. **"透明 + 可定制"**：提示词、工具（instruments）、记忆均可修改，便于深度定制
4. 模型无关（LiteLLM），自带 Web UI，开箱可用

### 局限与风险

1. 采用**自定义（非标准 OSI）协议**，商用/分发条款需自行确认
2. Docker 运行带来资源占用与部署门槛，面向技术用户、学习曲线较陡
3. 个人开发者主导，长期治理与稳定性存在不确定性

### 适合谁 / 典型场景

需要隔离执行环境的自动化任务（代码/脚本/运维）；安全研究与渗透测试类任务（默认 Kali Linux 环境）；开发者自建可定制的通用自主智能体。

---

## 9. Devika

> **定位**：首个开源 Agentic Software Engineer，最初作为 Devin 的开源替代
> **仓库**：https://github.com/stitionai/devika · **Star**：19,553 · **License**：MIT · **语言**：Python · **维护方**：Stition AI（印度） · **状态**：❌ **疑似停更（最后提交 2025-09-25）**

### 它是什么

Devika 是 2024 年"开源 Devin"浪潮的早期代表。它的设计是**多 Agent 分工**：把任务拆成规划、研究、编码等角色，由不同子 Agent 承担——这个思路在当年很新颖。

它也曾快速走红（19,553 Star、2,567 forks），但**维护基本停滞了**：最后提交为 2025-09-25，近一年无更新。更重要的是，**README 首行已引导用户转向 Opcode（opcode.sh）**——即"Devika 的第二代版本"。

README 自己也明确标注项目处于 **very early development / experimental**，**大量功能未实现或已损坏**。

> **选型结论：不建议在新项目中使用 Devika。** 如果对它感兴趣，应关注其继任项目 Opcode。

### 核心架构与编排范式

- **多 Agent 协作**：规划 / 研究 / 编码等子 Agent 分工，角色扮演式
- **Web UI**：浏览器界面查看进度并介入
- **模型无关**：支持 OpenAI、Anthropic、Groq、Ollama 等

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 代码执行、网页浏览/检索、文件操作等 |
| **记忆机制** | 短期会话记忆（项目周期内上下文） |
| **MCP 支持** | ❌ 不支持（项目早于 MCP 生态） |
| **沙箱/执行** | ⚠️ **无沙箱**——README 未提及隔离；Agent 直接在本机写代码、跑浏览器（Playwright） |
| **人机协作** | Web UI 中可查看进度并介入 |
| **RAG** | 通过内置研究 Agent 进行联网检索（非独立向量库 RAG） |

### 快速上手

```bash
git clone https://github.com/stitionai/devika.git && cd devika
uv venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
playwright install --with-deps   # 浏览器能力
python devika.py                 # 启动后端

# 前端（另开终端）
cd ui/
bun install
bun run start
```

**首次使用**：首次运行自动生成 `config.toml`；在 Web UI 设置页填 API Key（BING / GOOGLE_SEARCH / OPENAI / GEMINI / CLAUDE / MISTRAL / GROQ / NETLIFY 等）→ 打开 `http://127.0.0.1:3001` → 新建项目 → 输入高层目标。
**最低资源**：**Python >=3.10 且 <3.12、NodeJs >=18、bun、uv**；无 Docker 要求。
**上手难度**：★★★★☆ —— 需 uv + bun + Playwright 三套工具链，且项目自身"实验性、功能多损坏"。

### 差异化特色

1. 早期 Devin 开源平替的先驱，多 Agent 分工（规划-研究-编码）设计清晰
2. 模型无关 + 本地部署 + Web UI，上手门槛低
3. 曾以"开源 Devin"概念迅速走红

### 局限与风险

1. ⚠️ **维护基本停滞（最后提交 2025-09-25），长期选型风险高**
2. ⚠️ **项目自述处于实验阶段，大量功能未实现或已损坏**
3. ⚠️ **无沙箱**——Agent 可写文件 + 浏览网页，需自行容器化
4. 已转向继任项目 Opcode

---

## 10. UI-TARS

> **定位**：字节出品的原生 GUI 智能体，用自研视觉语言模型直接"看屏幕、点按钮、填表"
> **仓库**：https://github.com/bytedance/UI-TARS · **Star**：11,596（配套 UI-TARS-desktop 约 3.8 万） · **License**：Apache-2.0 · **语言**：Python（Desktop 为 TypeScript） · **维护方**：字节跳动 ByteDance（中国） · **状态**：⚠️ 模型仓库更新放缓（2026-01 后）；桌面应用仓库较活跃

### 它是什么

UI-TARS 代表的是**"纯视觉 GUI 操作"路线**——与 Browser Use 的"读 DOM 结构"路线相对。

它的做法是：**截屏 → 视觉语言模型直接输出坐标点击**。不依赖 DOM、不依赖无障碍树，因此能操作任何图形界面：桌面应用、手机 App、无 DOM 的 canvas 应用。

代价也很明显：
- **grounding（坐标定位）是最大失败点**——点错 40 像素会"静默成功"于错误目标
- **每步截图导致 Token 成本高**（单步与总步数都更贵）
- **直接操控真实桌面"破坏半径"大**，严肃使用必须跑在沙箱/VM 中

需要区分清楚：`bytedance/UI-TARS` 是**模型 + 代码库**（研究性质），不是端到端应用；本地桌面应用版见 **UI-TARS-desktop** 仓库，Web 自动化见 **Midscene.js**。

值得注意的是，业界正在**收敛**：UI-TARS 的 **Agent TARS** 已推出 **GUI + DOM 混合浏览器模式**——"有结构用结构，无结构用像素"成为共识。

### 核心架构与编排范式

- **单 Agent 端到端**：VLM 一体化集成感知-推理-行动，无预定义规则
- **专为 GUI grounding 训练**的视觉语言模型（ByteDance-Seed/UI-TARS-*）
- **双形态**：UI-TARS Desktop（原生 GUI 应用）+ Agent TARS（多模态智能体栈）
- **混合模式**：GUI + DOM

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | GUI 操作（鼠标键盘、触摸、像素级点击）；Agent TARS 提供 GUI+DOM 混合浏览器模式 |
| **记忆机制** | [不确定] |
| **MCP 支持** | Agent TARS 侧支持 MCP |
| **沙箱/执行** | ⚠️ **无内置沙箱**（属模型/研究代码）；需自行在 VM/容器中运行目标环境 |
| **人机协作** | 桌面应用支持可视化查看与人工接管 |
| **RAG** | 无内置 RAG（浏览器混合模式可读 DOM 结构） |

### 快速上手

```bash
# 后处理工具包（模型输出 → 可执行 pyautogui 代码）
pip install ui-tars
# 或
uv pip install ui-tars

# 模型部署与推理：见 README_deploy.md
# 模型权重：huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B
```

```python
from ui_tars.action_parser import parse_action_to_structure_output, parsing_response_to_pyautogui_code
```

**首次使用**：按 `README_deploy.md` 部署模型（HuggingFace endpoint / 自建推理）→ `pip install ui-tars` → 用 `parse_action_to_structure_output(...)` 解析坐标动作（`factor=1000`，`model_type="qwen25vl"`）→ `parsing_response_to_pyautogui_code(...)` 生成可执行代码。
**最低资源**：⚠️ **需较强算力，建议 GPU**（7B 模型本地服务需 GPU）；用 HuggingFace 托管 endpoint 可免本地 GPU。
**上手难度**：★★★★☆ —— 面向研究者/工程师，需自建推理 + 坐标后处理，非开箱即用。

### 差异化特色

1. **端到端 VLM 专为 GUI grounding 训练**，论文公开（arXiv:2501.12326）
2. **具备开放词汇定位与像素级操作能力**，可驱动无 DOM 的 canvas / 桌面应用
3. **一仓库双形态**：UI-TARS Desktop（约 3.8 万星）+ Agent TARS
4. **已推出 GUI+DOM 混合浏览器模式**，代表纯像素路线向混合收敛

### 局限与风险

1. **grounding 坐标定位是最大失败点**，点错像素会"静默成功"于错误目标
2. **每步截图导致 Token 成本高**
3. ⚠️ **直接操控真实桌面"破坏半径"大**，严肃使用必须跑在沙箱/VM 中
4. ⚠️ **官方 Limitations 段落明确警示**：模型在 GUI 任务（**含绕过 CAPTCHA 等认证挑战**）表现强，**可能被滥用于未授权访问或受保护内容的自动化**；官方称"内部安全评估正在进行"。**建议仅在隔离环境/授权范围内使用**
5. 最新版本 UI-TARS-2（2025-09-04）与 UI-TARS-1.5（2025-04-16）均为 2025 年发布，2026 年新版本 [不确定]

### 适合谁 / 典型场景

跨应用 GUI 自动化（设置对话框、虚拟机控制台等无结构 UI）；桌面端/手机端界面操作与 GUI 智能体研究；浏览器内任务（通过混合 DOM 模式）。

---

## 11. Bytebot

> **定位**：自带虚拟桌面环境的开源 Computer-Use Agent
> **仓库**：https://github.com/bytebot-ai/bytebot · **Star**：11,075 · **License**：Apache-2.0 · **语言**：TypeScript · **维护方**：Bytebot AI · **状态**：❌ **已归档停更（2025-09-12）**

### 它是什么

Bytebot 的定位是"**有自己电脑的 AI**"——它自带一个完整的 **Ubuntu 22.04 + XFCE 虚拟桌面**，跑在 Docker 容器里。Agent 在里面用鼠标键盘操作真实的图形界面，而你通过 **NoVNC 在浏览器里实时观看、随时接管**。

这个"可视化 + 可接管"的设计很讨喜：你能看到 Agent 到底在干什么，出问题能立刻接管。它提供三套 API：Agent API（任务管理）、ComputerUse API（鼠标键盘）、MCP（对接外部工具）。部署方式也很灵活：Railway 一键、Docker Compose、Kubernetes/Helm。

**但项目已归档。** 最后提交为 2025-09-12，仓库标记 `archived=true`，已约一年未更新。

> **选型结论：不建议新项目采用。** 它的架构思路（虚拟桌面 + NoVNC 接管）值得参考，但需要自己维护。

### 核心架构与编排范式

- **单 Agent 循环**
- **三套 API**：Agent API（`localhost:9991/tasks`）、ComputerUse API（`localhost:9990/computer-use`）、MCP
- **虚拟桌面**：容器内 Ubuntu 22.04 + XFCE，NoVNC 远程访问（`localhost:9992`）
- **Takeover Mode**：人工接管

### 关键能力

| 维度 | 说明 |
|---|---|
| **工具调用** | 鼠标/键盘控制、ComputerUse API 精确操作、文件与桌面操作 |
| **记忆机制** | [不确定] |
| **MCP 支持** | ✅ 支持（可连接 Claude Desktop 等外部工具） |
| **沙箱/执行** | ⭐ **Docker 容器化 Linux 桌面，天然隔离**，安全可控 |
| **人机协作** | ⭐ 通过 NoVNC 在浏览器实时查看并随时接管控制 |
| **RAG** | 无内置 RAG |

### 快速上手

```bash
# 方式1：Railway 一键部署（最简单）
# https://railway.com/deploy/bytebot

# 方式2：Docker Compose
git clone https://github.com/bytebot-ai/bytebot.git && cd bytebot
echo "ANTHROPIC_API_KEY=sk-ant-..." > docker/.env   # 或 OPENAI_API_KEY / GEMINI_API_KEY
docker-compose -f docker/docker-compose.yml up -d
# 打开 http://localhost:9992

# 方式3：Kubernetes / Helm
helm install bytebot ./helm --set agent.env.ANTHROPIC_API_KEY=sk-ant-...
```

**首次使用**：部署后在 `docker/.env` 填一个 AI provider Key → 打开 `http://localhost:9992`，在 **Desktop 标签页**配置桌面（装程序、配密码管理器、登录站点）→ 用自然语言创建任务并实时观看执行。
**最低资源**：**需要 Docker**；无需本地 GPU（用云端 AI API）。
**上手难度**：★★☆☆☆ —— Docker Compose 两条命令起，UI 直观；Railway 一键更简单。

### 差异化特色

1. **自带完整虚拟桌面**：容器化 Linux + NoVNC，浏览器即可观看与接管
2. **三套 API**：Agent API（任务管理）、ComputerUse API（鼠标键盘）、MCP（对接外部工具）
3. **开源自托管，任务全程可视化**，支持随时人工接管
4. 支持 LiteLLM 接入 Azure/AWS Bedrock/Ollama 等 100+ provider

### 局限与风险

1. ⚠️ **项目已归档停更（2025-09-12），无后续维护，选型风险高**
2. 依赖截图的 computer-use 路线，grounding 与稳定性/成本存在通病
3. 维护方信息与社区活跃度低；README 无专门安全加固章节

### 适合谁 / 典型场景

桌面级任务自动化（跨应用操作）；需要真实图形界面的浏览器/软件操作任务；自托管环境下的安全电脑操作代理。

---

## C 类横向速查

### 能力与风险对比

| 项目 | Star | License | 沙箱隔离 | 上手 | 状态 | 一句话 |
|---|---|---|---|---|---|---|
| **OpenClaw** | 391,937 | MIT | 🔴 **无沙箱** | ★★★ | ✅ | 最热，本地优先，安全争议最大 |
| AutoGPT | 187,566 | ⚠️ 混合 | 🟡 Docker | ★★☆/★★★★ | ✅ | 鼻祖，已转 DAG 平台 |
| OpenHands | 90,847 | MIT | 🟢 Docker（可每会话独立） | ★★★ | ✅ | SWE-bench 53%+，编码最强 |
| Open Interpreter | 68,574 | Apache-2.0 | 🟢 **原生沙箱** | ★★☆ | ✅ | Rust 重写，专为开源模型优化 |
| OpenManus | 58,635 | MIT | 🔴 **无沙箱** | ★★★ | ✅ | Manus 平替，开箱即用 |
| Suna / Kortix | 20,273 | 🔴 自定义 | 🟢🟢 **每会话 microVM** | ★★★ | ✅ | 企业级治理最完整 |
| OWL | 20,151 | 🔴 不明 | 🔴 **无沙箱** | [不确定] | ✅ | GAIA 开源第一，许可存疑 |
| Agent Zero | 19,458 | 🔴 自定义 | 🟢 **Docker（Kali）** | [不确定] | ✅ | 默认容器隔离 |
| Devika | 19,553 | MIT | 🔴 **无沙箱** | ★★★★ | ❌ 停更 | 已转向 Opcode |
| UI-TARS | 11,596 | Apache-2.0 | 🔴 **无沙箱** | ★★★★ | ⚠️ | 纯视觉 GUI 路线 |
| Bytebot | 11,075 | Apache-2.0 | 🟢 Docker 桌面 | ★★☆ | ❌ 归档 | 虚拟桌面 + NoVNC 接管 |

### 沙箱隔离梯度（安全边界由弱到强）

```
🔴 无沙箱         OpenClaw · OpenManus · OWL · Devika · UI-TARS
    ↓
🟡 Docker 容器     AutoGPT · Agent Zero · OpenHands · Bytebot
    ↓
🟢 原生/混合沙箱    Open Interpreter
    ↓
🟢🟢 每会话隔离     Suna / Kortix（microVM + 独立 git 分支 + 审批门）
```

### 2026 年这一类的重要变化（选型必读）

| 项目 | 变化 |
|---|---|
| OpenClaw | 成为 GitHub 历史星标第一；CNCERT 发布安全指南；创始人加入 OpenAI，项目转基金会 |
| OpenHands | 改名为 **Agent Canvas**，提供 4 种部署方式与明确安全模型 |
| Suna | **更名为 Kortix**，定位升级为"AI 操作系统" |
| Open Interpreter | **Rust 重写**，基于 OpenAI Codex 架构，转型为终端编码代理 |
| Devika | **停止维护**，转向继任项目 **Opcode**（opcode.sh） |
| AutoGPT | 从自由循环转向**托管平台 + 可视化 DAG**，自托管安装器尚未正式发布 |
| Bytebot | **已归档停更** |
| UI-TARS | 模型侧更新放缓，桌面应用侧较活跃；已推出 GUI+DOM 混合模式 |
