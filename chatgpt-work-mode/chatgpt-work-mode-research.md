# ChatGPT Work 模式深度研究报告

> 调研日期：2026-10-16 ｜ 数据口径：截至 2026-10-16 的公开资料
> 来源：OpenAI 官方帮助中心 / OpenAI Learn 官方文档 / 百度百科 / 一线实测文章（详见文末来源）

---

## 0. TL;DR

| 问题 | 一句话结论 |
|---|---|
| 与普通聊天差异 | Chat = 给答案（一段文字）；Work = 交成品（文件、表格、PPT、网站）。Work 是 Agent 模式，会拆步骤、调工具、迭代到交付 |
| 如何设置 | 桌面端顶部模式切换器选 **Work**（Chat / Work / Codex 三选一）；网页/手机端为入口之一。付费套餐才完整可用 |
| 如何强化 | 给"目标+材料+约束+验收标准"而非指令；挂 plugins（`@` 调用）；选对模型（Astra/Sol/Luna）+ 推理强度（max/ultra）；用定时任务与资料库 |
| 能否装 skills / MCP | **能，但有套餐门槛**。Skills 官方定位为 Business/Enterprise/Healthcare/Edu；MCP 完整版（含写入）限 Business/Enterprise/Edu，Pro 仅读；均为网页版。Work 自身主推 **plugins**（60+ 连接器） |
| 有 loop 吗 | **有**。这是 Work 与 Chat 的本质区别：任务分解 → 调用工具 → 校验 → 迭代 → 交付；支持暂停待批准、云端后台续跑、定时/事件触发/监控任务；`ultra` 档会并行调用 4 个子智能体 |

---

## 1. ChatGPT Work 是什么

- **发布**：2026-07-10（当地时间 7 月 9 日），与 GPT-5.6 同步推出。
- **定位**：办公智能体（office agent）。官方原文："**delegate real work to ChatGPT**"——把一个有明确产出物的任务交出去，拿回可审阅的成果。
- **驱动模型演进**：GPT-5.6（Sol / Terra / Luna）→ 2026-09-03 起接入 GPT-6 Astra → 2026-09-23 接入 GPT-6 Sol / Luna → **2026-10-14 GPT-5.5 退出 Work**。
- **底层**：使用 Codex 的执行框架（沙箱 + 权限控制），但**去掉了工作树等偏编程界面**，包装成通用办公体验。
- **交付物**：文档、表格、幻灯片、报告、网页应用（Site）。
- **特色能力**：Computer Use（通过桌面端内置浏览器直接操作电脑，完成没有 API 的任务）；Cloud Browser（云端浏览器，可读页面、点击、填表）。

### Chat / Work / Codex 三分法（官方口径）

| 模式 | 官方用途 | 读取的内容 | 交付结果 |
|---|---|---|---|
| **Chat** | 创建、学习和探索；对话与沟通 | 当前对话 + 你提供的材料 | 一段回答 / 内容 |
| **Work** | 研究、文件与其他知识工作 | 邮件、文档、聊天记录、日历、业务系统 | 文档、表格、幻灯片、网页应用等**成品文件** |
| **Codex** | 构建、调试、发布 | 代码仓库、测试、Git 上下文 | 代码变更、diff、测试结果、PR |

> 产品负责人 Tara Seshan 表态：多入口是"从聊天向 Agent 迁移"的过渡形态，理想状态是用户不用区分三者，只描述任务、由系统自动选模型与执行框架。

---

## 2. 与普通聊天模式的差异（核心）

### 2.1 范式差异：线性对话 vs 状态机

| 维度 | Chat | Work |
|---|---|---|
| 交互模型 | 线性：提问 → 回答 → 追问 | 状态机：拆解 → 执行 → 校验 → 修改 → 交付 |
| 你的输入 | 一个问题 / 一段指令 | 一个**目标** |
| 交付物 | 文本 | 可打开编辑的**文件** |
| 工具链 | 无外部工具执行循环 | 有外部工具链接入 + 执行循环 |
| 上下文 | 每次交互相对独立 | 多步骤之间保持上下文，持续迭代 |
| 耗时 | 秒级 | 分钟级到小时级（实测案例：同一任务 Chat 秒出文字，Work 用 23 分钟产出 3 份文件） |
| 可追溯性 | 弱 | 强：每步有执行轨迹，可点开查看来源与操作 |
| 人工介入 | 无 | 可随时改方向、回答问题、**审批关键动作** |

### 2.2 关键澄清：不是"聊天只能说、工作才能做"

- 普通 Chat **也**有搜索、文件分析、沙箱代码执行能力，界线并不严格。
- Work **不**比 Chat "更聪明"，只是更长、更多步骤、能出文件。概念解释、快速问答上 Work 反而更慢（要先拆解、规划再执行）。
- 判断标准只有一条：**你要的是答案，还是成果？** 答案走 Chat，成果走 Work，代码走 Codex。

### 2.3 额度差异（容易踩坑）

- **Chat 与 Work/Codex 额度独立**。Chat 有独立消息限额；图片生成、语音各有独立限额与重置周期。
- **Work 与 Codex 共享"智能体用量"池**：ChatGPT Work、Codex、ChatGPT for Excel、Workspace Agents 都从同一池扣减。
- 计费按 **Token 消耗**（2026-04 起），受模型选择、上下文长度、工具调用、运行时长、推理强度影响，不是按消息条数。
- 2026-07 曾临时取消 Plus/Business/Pro 的 5 小时限制 → **2026-08-26 起恢复** Plus 的 5 小时滚动窗口（与周限额并行）。额度用尽可购买额外 credits，或等下次重置。

---

## 3. 如何设置 / 打开

### 3.1 入口

| 端 | 情况 |
|---|---|
| **桌面端**（macOS / Windows） | 新版 ChatGPT 桌面 App 顶部有 **Chat / Work / Codex** 模式切换器。Work 能力最强：可用本地文件、内置浏览器、Computer Use。原有 ChatGPT 桌面端更名为 **ChatGPT Classic**；Codex 独立 App 已并入 |
| **网页端** | 模式切换器内 Work 为独立入口（Work 可跑在云端沙箱） |
| **手机端** | 有 Work 入口；顶部下拉菜单可切 Chat。Codex 不能直接在手机进入，但可通过 Remote 标签远程查看桌面任务 |

### 3.2 套餐可用性（存在资料冲突，已标注）

- **官方（baoyu 转述 OpenAI 帮助中心）**：Work 不是独立付费产品，含在现有订阅中，**Free 到 Enterprise 全档可用，差别主要是额度**。
- **一线实测（2026-09-24）**：桌面端 Work 已扩展到**所有套餐**；网页/手机端的 Work 主要面向 Plus / Pro / Business / Enterprise / Edu，Free 和 Go 在这些入口里不含 Work。
- **初期开放顺序**：Pro / Enterprise / Edu 优先 → Plus / Business 随后。
- **已过时说法**：有文章称"Work 仅对 Pro 和 Team 开放"，与 8–9 月后的官方更新不符，**不建议采信**。

### 3.3 已安装却看不到 Work 的排查顺序

1. 桌面 App 是否最新版（菜单 > 检查更新）
2. 是否登录了正确账号
3. 是否进了公司 Workspace（管理员可能限制功能/模型）
4. 是否处于逐步开放阶段（不同工作区权限不同）

### 3.4 执行位置：本地 vs 云端

| | 本地 Work | 云端 Work |
|---|---|---|
| 运行环境 | 本机，OS 原生隔离（macOS Seatbelt / Windows Sandbox） | OpenAI 托管 VM 沙箱，Codex 任务执行框架 |
| 能读本地文件/应用 | ✅ | ❌（除非开启 Local computer access with Work Cloud） |
| 电脑关机后继续跑 | ❌ | ✅ |
| 适合 | 整理本地目录、操作本机应用 | 查公开资料、处理上传材料、长任务、定时任务 |
| 实测配置 | — | Plus：4 核 / 4GB / 约 60GB 临时盘 / 无 GPU；Pro：9 核 / 9GB |

- 桌面端 composer 可手动选 **local** 或 **cloud**。
- 开启 **Local computer access with Work Cloud** 后，可在桌面/手机/网页间**跨设备续跑**（需要管理员开启 sync；企业默认不变）。
- **重要**：云端/本地是两条线。网页/手机端 Work 对话与桌面端 Work 对话**不互通**（Chat 对话则互通）。官方表述为 "at launch" 限制。

---

## 4. 如何强化（把 Work 用出效果）

### 4.1 提示词：从"下指令"改成"派活"

官方建议一次给全五要素：**目标结果 → 材料来源 → 约束 → 什么算好 → 何时停下等审批**。

| 弱 | 强 |
|---|---|
| "帮我做个客户调研的 PPT" | "审阅附件访谈记录和问卷结果，为产品管理层会议做 8 页 PPT。聚焦客户最集中的 3 个问题，附支撑证据，把'发现'与'建议'分开，标出证据不足的结论。用 @Google Drive 取源文档。先给我草稿审阅，不要直接当终稿。" |

**核心心法（实测总结）**：Chat 的提示词是"小"的（总结这段、解释这个）；Work 的价值在于**你交给它的"所有权"越大，它越有用**。不要让它一次解决一个问题，让它对整个任务负责。

可直接套用的 7 个高价值提示词：

1. **幕僚长**：担任我项目的幕僚长，审阅我分享的所有资料，找出待办、按优先级组织，只有需要我做决策时才来找我。
2. **全量速读**：审阅这个文件夹所有文档，标出关键点与矛盾之处，生成我 5 分钟能读完的摘要。
3. **真金白银推荐**：结合专业评测、用户反馈、规格、长期成本与可靠性对比这些产品，推荐你会自掏腰包买的那款并解释原因。
4. **接管收件箱**：浏览我的邮件，归类相似信息，找出紧急事项，起草回复，生成一份仍需我关注的行动清单。
5. **笔记成稿**：整理这些笔记，分成逻辑段落，找出缺失信息，生成可直接分享的精炼文档。
6. **持续盯梢**：监控这个主题，只在发生重大变化时通知我，忽略常规更新。
7. **做完而非下一步**：我的目标是完成这个项目。拆成可管理阶段，独立完成你能做的一切，只有绝对必要时才来问我要输入。

**设边界**：明确写 "只用这些来源" / "只比较前 5 个选项" / "发送前停下"。

### 4.2 接插件（plugins）——最直接的强化

- 路径：左侧导航 **Customize → Plugins**，安装与工作相关的插件。
- 调用：提示词里输入 `@` + 插件名，指定从哪个工具取数；ChatGPT 也会自动判断该用哪个。
- 官方口径支持 **60+ 连接器**：Slack、Gmail、Google Drive、SharePoint、Microsoft Teams、Outlook、Salesforce、日历、CRM、项目管理工具等。
- 把高频流程固化：可通过对话**创建/编辑插件**，做成可复用的工作流。

### 4.3 选模型 + 推理强度

| 模型 | 定位 | 相对成本 |
|---|---|---|
| GPT-6 Astra | 需要缜密推理、视觉判断、精致成品时用 | 高 |
| GPT-6.1 Sol | 复杂任务、比 Astra 便宜 | 中 |
| Luna | 简单任务、高吞吐、快 | 低 |

- Free / Go 只能用 Terra；Plus 及以上可选并调 effort。
- `max`：更深推理；`ultra`：**同时调用 4 个子智能体**。
  - `ultra` 在 **Work 中仅 Pro / Enterprise** 可用；在 Codex 中 Plus 及以上即可用。

### 4.4 资料库（Library）

- Pro 提供 100GB 云盘，可挂载 Google Drive 等外部云盘。
- 建议把历史素材、数据放进去，让 Work 直接做选题、标题优化、月度数据分析。
- **重要观念**：把 Work 当"任务工作区"，不要当唯一存储位置。源码进正式仓库，重要成果下载或显式存到 Library / 项目。沙箱状态、聊天记录、Library 文件、项目文件**生命周期不同**——聊天还在 ≠ 进程还在跑。

### 4.5 材料放在 Google Drive（官方事实）

| 项 | 说明 |
|---|---|
| 可用范围 | 资料库中的 Google Drive 正逐步向**网页版** Plus / Pro / Business / Enterprise / Edu / Healthcare 推出；**「对话」与「工作」两种模式下均可使用**，移动端稍后 |
| 权限 | 遵循你现有的 Drive 权限；初期含「我的云端硬盘」+ 直接分享给你的项目，**尚不含「共享云端硬盘」** |
| 调用 | 资料库中浏览/搜索 → 输入框或 `@提及` 加入对话；也可选中**文件夹**要求综合处理 |
| 关键性质 | 资料库中的 Drive 文件**保持与原始来源的连接**（非静态副本）；官方明确：**受支持且获授权时，ChatGPT 可直接更新原始文件** |
| 删除 | **无法**从 ChatGPT 删除 Drive 文件，须回 Drive 操作 |

**放 Drive 的收益与代价**

- 收益：跨端/关机问题消失（云端 Work 直接读 Drive）；`@文件名` 即用，始终指向最新版；Drive 自带版本历史可回滚。
- 代价：**它改的是原稿本身**（链接非副本）。防护：走"两轮制"（第一轮只出对照表并禁止改文件，确认后第二轮才写回）+ 要求另存为新文件 + 禁用文件夹级指令。
- 格式建议：Google Docs 原生格式带自动格式化（智能引号、自动更正）；要精确控制标点缩进，稿子用 `.md` / `.docx` 存 Drive 更稳。

**资料库容量（官方）**：Free 500 MB｜Go 4 GB｜Plus / Business 20 GB｜Pro 100 GB。单文件 ≤ 512 MB，文字/文档类 ≤ 200 万 token。资料库占用与「每日附件/对话用量」分开计算。

**训练开关**：Free / Plus / Go / Pro 若开启「为所有人改进模型」，通过应用访问的信息**可能被用于训练**；Business / Enterprise / Edu 默认不用于训练。未发表作品建议关闭。

### 4.6 常见"翻车"场景

1. 任务描述模糊（"做个好看的 PPT"）→ Work 无法执行，因为它不知道"好看"和该放什么。
2. 数据来源不清晰（没说文件在哪、怎么关联）→ 读错文件或漏关键数据。
3. 成果需人工审批 → 输出质量取决于输入质量，**交付前必须自己终审**。

---

## 5. 能否装 Skills / MCP？

**结论：能，但取决于套餐与端，且 Work 自身主推的是 plugins 而非 MCP。**

### 5.1 Skills（技能）

- **官方定义**：可重复使用与分享的工作流，包含指令、示例、代码；安装后 ChatGPT 会在合适时自动使用。
- **官方可用范围**：**ChatGPT Business、Enterprise、Healthcare、Edu**（取决于工作区设置与产品可用性）；Codex 等其他 OpenAI 产品也支持，可用性/安装/同步方式可能不同。
- **创建方式（4 种）**：
  1. 对话创建（技能 → 建立 → 通过对话建立）
  2. 编辑器创建（chatgpt.com/skills/editor）
  3. 从电脑上传（技能 → 建立 → 从电脑上传）
  4. 安装他人/工作区分享的技能
- 符合条件的账号默认含 **skill-creator** 技能，用于生成、更新、排障。
- 上传的技能会先扫描：多数即刻可用；部分标记"需要检查"；疑似风险内容标记"已封锁"。
- 管理员权限项：启用技能 / 启用技能上传 / 分享技能 / 将技能发布至工作区 / 启用技能安装。
- **冲突点**：官方文档未把 Skills 列给个人付费档，但一线实测（2026-07）称在**网页端切到 Work 模式后可直接 `@skills` 调用**，上传的 skills 落在云沙箱 `/root/.codex/skills/remote-skills`。→ **实测可用，但官方口径未覆盖，建议以自己账号实际能否看到"插件 → 技能"页签为准。**

### 5.2 MCP

| 项 | 结论 |
|---|---|
| 完整 MCP（含写入/修改） | **Business、Enterprise/Edu**（网页版） |
| Pro | 可连**只读/抓取**权限的自定义 MCP 服务器 |
| 移动端 | ❌ 不支持 |
| 是否需开发者模式 | **不需要**。当前 Plugins 体验下，直接 Plugins → 加号 → **Add custom MCP server**，逐个确认风险警告即可 |
| 连接方式 | 公网 HTTPS MCP 端点 URL，或 Secure MCP Tunnel（连本地/私网服务器） |
| 写操作安全 | 可能要求确认；部分高风险动作直接阻断 |
| 变更同步 | **不自动更新**，用"冻结快照"，需管理员 Refresh 后重新发布 |

- 注意：官方 MCP 文档**未出现 "Work mode" 字样**，因此"MCP 应用在 Work 模式下是否可用"**无官方明确说明**；可确认的是 Workspace Agents 采用"逐 agent 控制"决定动作可用性，且带交互式 UI 的 App 在 company knowledge 中不支持。
- 对照：**Claude Cowork 用 MCP 连接器**（Slack/Notion/HubSpot/Jira/Linear + 11 个行业插件）；**ChatGPT Work 用 plugins 目录**。两条技术路线不同。

---

## 6. 有 loop 吗？——有，而且是核心

### 6.1 Agent 循环

Work 的底层就是 agentic loop：

```
目标输入 → 任务拆解 → 制定计划 → 调用工具/插件 → 执行
   ↑                                                ↓
   └──────── 校验结果 / 自我修正 ←── 失败或不合规 ←──┘
                          ↓
                   交付成品（文件）+ 执行轨迹
```

- 中间任一步失败可回退重做；状态机式流转，直到到达"交付"状态。
- 可**暂停等你批准**（safety review / 需批准的动作会暂停任务）。
- 官方描述：可以跟随进度、回答问题、改变方向、审批重要动作。

### 6.2 三种"持续运行"机制

| 机制 | 说明 |
|---|---|
| **云端后台续跑** | 云端 Work 任务在你离开对话、关闭电脑后仍继续跑 |
| **定时任务（Scheduled Tasks）** | 一次性 / 周期性 / 事件触发 / 监控变化 |
| **Computer Use** | 桌面端后台操作其他应用，屏幕上出现"第二个光标" |

### 6.3 定时任务细则（官方）

- 创建：前往 **已安排**；或在对话里直接说"包裹送达后通知我"。
- **事件触发任务在 Work 模式中运行**，可响应 Gmail / Slack / GitHub 的受支持活动（需先在设置 > 应用连接；Slack 需在每个频道加 `@ChatGPT`）。
- 需要 **Work 模式访问权限** + 符合条件的 Plus/Pro/Business/Enterprise/Edu。**Free、Go、FedRAMP 不支持事件触发**。
- 活动任务上限：Free/Go **3**、Plus **5**、Business/Edu **10**、Pro/Enterprise **15**。
- 频率：Free 每天最多 1 次；付费可**最高每小时 1 次**并指定精确时间。事件触发任务合计**每小时最多 30 次、每天最多 720 次**。
- 不支持：语音聊天、GPT。不活跃任务可能被自动暂停。
- 桌面 App 可显示已有事件触发任务，但**创建/编辑触发条件要用网页版**。

### 6.4 并行子智能体

`ultra` 推理强度会**同时调用 4 个子智能体**——这是 loop 的横向扩展（并行分支），目前 Work 中仅 Pro / Enterprise 可用。

---

## 7. 决策树：该用哪个

1. 交付物只需文字 → **Chat**
2. 需要可编辑文件（PPT / Excel / Word / 网站）→ **Work**
3. 交付物是代码或涉及代码仓库 → **Codex**
4. 需要跨工具联动（读 Gmail、操作 Slack、调 API）→ **Work**
5. 需要定时执行或长期监控 → **Work（云端）**
6. 需要本地文件/本机应用 → **Work（本地）** 或 Codex（按工程环境）

推荐组合：**用 Chat 理清思路 → 用 Work 完成交付 → 用 Codex 处理代码**。

---

## 8. 与 Claude Cowork 的对照（同一赛道）

| 维度 | ChatGPT Work | Claude Cowork |
|---|---|---|
| 沙箱 | OS 原生隔离（Seatbelt / Windows Sandbox），内置浏览器 | 本机隔离 Linux VM，产物直接落盘 |
| 连接方式 | plugins 目录（60+） | MCP 连接器 + 11 个行业插件 |
| 跨设备 | 桌面/网页/手机 Work 对话**不互通**（at launch） | 会话可在桌面/网页/手机流转 |
| 定时任务 | ✅ | ✅ |
| Computer Use | ✅（较成熟） | 研究预览阶段 |

---

## 9. 未核实 / 存疑

1. **Skills 是否对个人付费档开放**：官方文档只列 Business/Enterprise/Healthcare/Edu；一线实测称网页 Work 可 `@skills`。**存疑，需以账号实测为准。**
2. **MCP 在 Work 模式下的可用性**：官方 MCP 文档未提及 Work mode。**无官方确认。**
3. **Free/Go 在桌面端能否用 Work**：一处实测称"桌面端 Work 已扩展到所有套餐"，官方帮助中心口径为"全档可用、差别在额度"，但网页/手机端 Free 不含 Work。**建议以自己客户端实际显示为准。**
4. **额度具体数值**：官方未公布统一的"每次任务消耗 X credits"标准，受多变量影响，无法换算成固定条数。
5. 部分中文来源为 AI 生成内容（如百家号部分文章标注"内容由AI智能生成"），本报告仅采信其可与其他来源交叉验证的部分。

---

## 来源

- [OpenAI Learn：Get started with ChatGPT Work](https://learn.chatgpt.com/docs/get-started-with-work)
- [OpenAI 帮助中心：ChatGPT 中的定时任务](https://help.openai.com/zh-hans-cn/articles/10291617-tasks-in-chatgpt)
- [OpenAI 帮助中心：使用档案库管理 ChatGPT 中的文件](https://help.openai.com/zh-hant-hk/articles/20001052-file-storage-and-library-in-chatgpt)
- [OpenAI 帮助中心：ChatGPT 中的已连接应用](https://help.openai.com/zh-hans-cn/articles/11487775-apps-in-chatgpt)
- [OpenAI 帮助中心：ChatGPT 中的技能](https://help.openai.com/zh-hant/articles/20001066-skills-in-chatgpt)
- [OpenAI 帮助中心：Developer mode and MCP apps in ChatGPT](https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt-beta)
- [OpenAI 帮助中心：ChatGPT 智能代理](https://help.openai.com/zh-hant-hk/articles/11752874-chatgpt-agent)
- [OpenAI 帮助中心：ChatGPT Business 模型与限额](https://help.openai.com/zh-hant-hk/articles/12003714-chatgpt-business-models-limits)
- [OpenAI：ChatGPT is now a partner for your most ambitious work](https://openai.com/index/chatgpt-for-your-most-ambitious-work/)
- [宝玉：一文看懂 ChatGPT、Codex、Work 的差别](https://baoyu.io/blog/chatgpt-work-codex-guide)
- [百度百科：ChatGPT Work](https://baike.baidu.com/item/ChatGPT%20Work/68671672)
- [人人都是产品经理：ChatGPT 桌面端重大更新，最新使用指南](https://www.woshipm.com/ai/6471619.html)
- [人人都是产品经理：OpenAI 整合 Codex 能力，ChatGPT 网页版正在变成云端 AI 电脑](https://www.woshipm.com/it/6435958.html)
- [百家号：ChatGPT Work 在哪里打开？普通 Chat 和 Work 到底有什么区别](https://baijiahao.baidu.com/s?id=1877195015735632022)
- [百家号：ChatGPT Work 深度体验：这 7 个提示词让它变身你的私人助理](https://baijiahao.baidu.com/s?id=1871841558415037285)
- [CSDN：同样是 ChatGPT，为什么有人产出文件有人只得到回答](https://blog.csdn.net/weixin_66526635/article/details/164251752)
- [百家号：ChatGPT Plus 又恢复 5 小时限制？真正受影响的是 Codex 与 Work](https://baijiahao.baidu.com/s?id=1875018079930509036)
