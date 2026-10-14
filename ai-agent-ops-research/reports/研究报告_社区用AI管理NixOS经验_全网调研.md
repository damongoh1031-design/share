# 全网社区调研：人们如何用 AI 管理 NixOS / Nix

**调研日期**：2026-10-13
**证据等级标注**：`已核实`= 抓到原文/元数据；`社区实证`= 多源一致的社区说法；`推断`= 本人归纳
**规模**：抓取 3,305 条原始条目 → 通过「AI × Nix」双关键词过滤 **979 条高相关贴文**，其中 60 个 NixOS Discourse 主题读全文（636 帖）、HN 362 条（28 故事 + 334 评论）、GitHub 148 条（102 个仓库）。

---

## 0. TL;DR

1. **社区对「AI 管理 NixOS」的态度是撕裂的，且撕裂点不在技术而在信任**。同一批人里，有人用 Claude 把项目改成 flake 后就去喝茶（`crertel`），也有人把「Call to ban AI commits」顶到 **618 赞**。官方最终落地的是「**human in the loop + 强制披露**」，不是禁止也不是放任。
2. **用户侧最成熟的用法不是「让 AI 管服务器」，而是「让 AI 写 Nix 表达式 + 用 NixOS 的可回滚性兜底」**。多个真实工作流都长这样：AI 出 diff → `nixos-rebuild dry-activate` 看变更 → `switch` → 失败 `--rollback`。
3. **最被反复提到的痛点不是模型笨，是「没有事实源」**。`jamesbrink` 因此写了 `mcp-nixos`（853★）：*"this tool keeps AI from hallucinating packages and options using up to date info"*。
4. **反向用法同样庞大**：用 Nix 打包/运行 AI 工具（`llm-agents.nix`、Claude Code 打包、Pi agent flake、nixified.ai）。这是目前 Nix 生态里 AI 相关活动**最密集**的方向。
5. **踩坑共识**（`tomberek` 在 skills 讨论帖列出的「AI 明显需要指导的事」）：永远不要 `find /nix/store/*something-* -iname libsomething.so`；不理解 devShells；要教 `nix-index`；打包/报错时该去搜 nixpkgs 的 issue/PR。
6. **一个被普遍忽视的风险**：generation 回滚只回滚**配置**，不回滚数据库状态与分布式状态（`cafkafk`）。「最坏损失一个 generation」是「我们讲给孩子的甜谎」。

---

## 1. 调研方法与数据规模

### 1.1 采集路径

| 来源 | 接口/方式 | 原始抓取 | 通过过滤 | 备注 |
|---|---|---|---|---|
| NixOS Discourse | 官方 `search.json` 逐关键词翻页 + `/t/<id>.json` 取全文 | 1,600 帖 | 469 帖 / 428 主题 | 23 个关键词 × 3 页 |
| Hacker News | Algolia `search` / `search_by_date` API | 1,148 条 | 362 条 | 13 组查询，故事 + 评论 |
| GitHub | `search/issues` API | 553 | 148 | 3 组查询，102 个仓库 |
| Reddit / X / Discord | 搜索引擎 + 直连尝试 | 4 | 0 | **均被反爬阻断，见 §1.3** |

**过滤条件**：文本同时命中①AI 词（llm / gpt / chatgpt / claude / codex / copilot / gemini / deepseek / qwen / mistral / ollama / openai / anthropic / mcp / cursor / cline / aider / windsurf / vibe cod / ai agent / ai powered …）与②Nix 词（nix / nixos / flake / nixpkgs / home-manager / nix-darwin / nixos-rebuild / devshell / configuration.nix …）。

### 1.2 「贴文」计数口径

- **979 条** = 通过双关键词过滤的独立贴文/条目数（Discourse 按帖计，HN 按故事/评论计，GitHub 按 issue/PR 计）。
- **636 帖** = 60 个 Discourse 主题读到的正文帖数（分析引文主要来自这里）。
- **60 个主题** = 读全文的 Discourse 主题数。

### 1.3 ⚠️ 采集受限说明（必须如实记录）

| 平台 | 尝试的路径 | 结果 |
|---|---|---|
| Reddit | `www.reddit.com/.../search.json`、`old.reddit.com`、`api.reddit.com` | 全部 **HTTP 403**（IP 级封锁，非 UA 问题） |
| Reddit | PullPush、Arctic Shift、redlib × 3、safereddit、r.jina.ai | 429 / 422 / 000 / 403；Arctic Shift 无自由文本 `q` 参数 |
| DuckDuckGo html | `site:reddit.com` 系列查询 | 前几次成功，随后进入 **anomaly 反爬页** |
| Bing | `site:reddit.com` 系列查询 | 有 `b_algo` 结果块但对 `site:` 查询几乎零返回 |
| Brave / Ecosia / Startpage / Qwant / Mojeek / searx ×2 | — | captcha / 403 / JS 渲染 |
| X (Twitter) | `site:x.com` 经上述引擎 | 无有效结果 |

**结论**：本轮 Reddit / X / Discord 的实际抓取量接近于零，报告中的 Reddit/X 内容仅来自内置搜索引擎的少量间接结果（且多为项目链接而非贴文）。**若要补这块，需要换出口 IP 或用 Reddit API 凭据**。Discord 除公开邀请页外无搜索面，`nixos-kr/ephemeral-nixos-on-discord` 这类项目只能从 GitHub 侧观察。

---

## 2. 社区版图：谁在用 AI 干什么

### 2.1 使用模式分布（979 条命中，可多属）

| 模式 | 命中数 | 占比 |
|---|---|---|
| A. 用 AI 写/改 NixOS 配置（configuration.nix / flake / module） | 301 | 30.7% |
| B. AI Agent 运维 NixOS 服务器（rebuild / 回滚 / 多机） | 231 | 23.6% |
| C. 用 Nix 打包/运行 AI 工具（**反向方向**） | 200 | 20.4% |
| D. 安全与信任边界（sandbox / sudo / 凭据 / prompt injection） | 119 | 12.2% |
| E. AI 教学/答疑 NixOS（skills / AGENTS.md / 文档给 agent 看） | 98 | 10.0% |
| F. 本地推理 / GPU（CUDA / ROCm / vLLM / lmstudio） | 56 | 5.7% |
| G. MCP × NixOS | 46 | 4.7% |
| H. 反对/怀疑 AI 用于 NixOS | 32 | 3.3% |
| I. AI 生成配置的坑/翻车 | 16 | 1.6% |
| 未分类 | 332 | 33.9% |

> 注：占比按命中贴文数 / 979 计算；「未分类」多为边缘提及。**反对声（32 条直接命中）远小于其声量**——反对主要集中在少数几个高赞大帖里（见 §6）。

### 2.2 时间线（Discourse 关键主题）

| 日期 | 主题 | 赞 | 意义 |
|---|---|---|---|
| 2025-04-04 | MCP-NixOS 发布 | 17 | 「给 AI 接 NixOS 事实源」路线起点 |
| 2025-11-18 | NixOS automation with AI | 26 | 用户提出完整的 brain/body agent 架构设想 |
| 2026-03-16 | Policy on vibe coded nix tools? | 389 | vibe coding 产物质量引发信任危机 |
| 2026-04-06 | Coding Agent workflow for NixOS | 12 | 真实工作流交流（llm-agents.nix / bwrap / distrobox） |
| 2026-05-11 | nixpkgs core team 自动化/AI 政策 | 74 | 官方政策成形：human in the loop + 披露 |
| 2026-06-14 | Call to ban AI commits | 618 | 抵制声量峰值 |
| 2026-06-28 | Let's create skills for nixpkgs development | 419 | 「给 agent 写技能」路线 |
| 2026-07-15 | LLMs in nixpkgs | 788 | 社区立场普查帖 |
| 2026-09-21 | Documentation needs to be created towards agents | 423 | 「llms.txt / agent 文档」路线 |
| 2026-09-22 | NixOs and Nix skill for LLM's | 17 | 落到具体 skill 仓库 |

---

## 3. 六大使用模式（附社区原话）

### 3.1 模式 A：用 AI 写/改 NixOS 配置

这是**命中数最高（301 条）**也最成熟的模式。共同特征：AI 负责生成 Nix 表达式，人负责 review 与 `nix flake check`。

**典型工作流（`crertel`，topic 77272，2026-04-27，已核实）**：
> "I check out a repo, point Claude at it, say 'figure out how to make this work as a flake', and go do other things, occasionally checking back and tweaking its work and spotting mistakes. It's neat."

**`JRMurr` 开发 Tix（Nix 类型检查器/LSP）时的自述（topic 76810，已核实）**：
> "while I did start this project a year ago myself, when i picked it back up a few months ago I've been primarily developing it with claude. If you feel strongly about vi[sibility of this]..."

**`mbrock` 用 Claude subagents 并行研究 Fil-C 补丁（topic 71476，2025-10-29，已核实）**：
> "I wanted to know how the patches were actually done, so I used a bunch of Claude subagents to simultaneously re[ad them]"

**`lucasew` 用 agent skill 批量提 PR（topic 78627，2026-06-28，已核实）**：
> "Like it or not, AI agents are here to stay... If you ask nicely, they can even do the whole flow of a PR without intervention and ship good code, taking into account gotchas that a human would spend a lot of time checking."
> "I didn't actually write this code, only review. It dispatched the nixpkgs-review run via my Github Actions trick and took the hashes from the logs."
> "It's like recruiting a new maintainer, but this new maintainer can read really fast and doesn't forget half the things on the way. **If you don't give it context it will mess up.**"

**`7c6f434c` 观察到的新人用法（topic 72275，2025-11-19，已核实）**：
> "I have seen (in PRs I have merged) an inexperienced user ask CoPilot for a review, very reasonably dismiss half (because it's pointless and/or misguided) but also force-push with the rest of the CoPilot suggestions applied... But probably an ability to correct the diff manually is still needed."

### 3.2 模式 B：AI Agent 运维 NixOS 服务器

#### 3.2.1 社区提出的「理想架构」（topic 72275，2025-11-18，26 赞）

`fieldempty` 的设想几乎就是一份产品需求文档（已核实原文）：

> "Machine A (the 'brain'): a beefy server/desktop that only runs a local LLM (Llama, Qwen-2).
> Machine B (the 'body'): a completely separate NixOS machine that does all the real work.
> The LLM on Machine A is the only administrator of Machine B. Interaction happens exclusively over SSH + a tiny privileged agent that can:
> - Pull the current flake or configuration.nix
> - Pull recent journalctl / dmesg / failed units
> - Accept my natural-language request ('add Tailscale with exit-node', 'install Ollama and expose it via nginx with HTTPS', 'why is Docker not starting after the last reboot?')
> - **Generate only the diff/patch**
> - Run `nixos-rebuild dry-activate` and show me exactly what will change
> - On my 'yes, apply' - run `nixos-rebuild switch`
> - If anything fails or the health-check script reports problems in the next few minutes - **automatic `nixos-rebuild switch --rollback`**"

这个「**只出 diff → dry-activate 展示 → 人工确认 → switch → 健康检查失败自动回滚**」的闭环，与本项目前几轮调研到的 `vespo92/mcp-nixos-ops`、`jacopone/clawnix` evolve 插件的设计高度一致——**说明这是社区自发收敛出的同一答案**（`社区实证`）。

#### 3.2.2 真实在跑的工作流

**`LorenzBischof`（topic 76873，2026-04-07，已核实）**——目前调研到最完整的个人方案：
> "I am currently using claude-code wrapped in bwrap. I hooked up a NixOS test which loads my NixOS configuration and the coding agent uses it interactively to run commands and take screenshots etc. This [is] useful for validating runtime behaviour that cannot be caught at eval time. I am still learning and experimenting, but **I think NixOS is uniquely positioned for this kind of workflow**."

**`crertel`（topic 77272）**：
> "NixOS has been very effective for giving certain types of agents (I call them gremlins...) power over how they organize their sandbox VMs."
> "giving it full access to NixOS to rebuild its VM has been really funny to watch."

**Stapelberg 的 coding-agent VMs（HN 109 分 / 48 评论，2026-02-01，已核实）**：《Coding Agent VMs on NixOS with Microvm.nix》是本轮 HN 上 AI×Nix 相关系分数最高的内容，技术路线是 microvm.nix 跑一次性 agent VM。

**Discord 侧的 `nixos-kr/ephemeral-nixos-on-discord`（已核实 README）**：Discord bot 启动临时 NixOS sandbox VM，内嵌 LLM agent 交互式教用户 NixOS——「AI 教学」与「沙箱」结合的少见案例。

### 3.3 模式 G：MCP × NixOS——因为「AI 在幻觉包名」

`jamesbrink` 的 `mcp-nixos`（现 `utensils/mcp-nixos`，853★ MIT）发布帖（topic 62640，2025-04-04，已核实）：

> "Wanted to share my mcp-nixos server with other who might find it helpful. **I use AI editors / Agents and Claude a lot, this was a bit of a passion project for me as its a tool I really wanted.** Any feedback, criticisms roasting etc is welcome.
> TLDR is this tool **keeps AI from hallucinating packages and options** using up to date info."

HN 上的对应条目标题本身就说明了动机：**"MCP-NixOS: When Your AI Needs to Learn NixOS Options Aren't Magic"**（已核实）。

这类「给 AI 接事实源」的项目在本轮 GitHub 抓取中出现频率很高，且普遍带 `nixos` / `mcp` / `ai` 标签，是 2025–2026 年 Nix 生态最活跃的新项目类别（`推断`，基于 148 条 GitHub 命中的主题分布）。

### 3.4 模式 C：用 Nix 打包 / 运行 AI 工具（反向方向，20.4%）

这是**活动最密集**的方向，且与「AI 管 NixOS」是两条独立的线：

| 项目 | 证据 | 说明 |
|---|---|---|
| `numtide/llm-agents.nix` | HN + Discourse 多次提及；`bitbloxhub` 在用 | 每日自动更新的 AI coding agent Nix 包集合（Claude Code / Codex / Amp / Pi…） |
| Packaging Claude Code on NixOS | Discourse topic 61072，9 帖 | 早期打包讨论 |
| Pi coding agent flakes | topic 78034 / 78035 | `services.pi-coding-agent` / `programs.pi-coding-agent` |
| `nixified-ai/flake` | GitHub 已核实 | AI 项目 Nix flake + 二进制缓存 |
| `cdepillabout/mkAIDerivation` | topic 66137，87 赞 | **让 LLM 现场生成 derivation**（IFD + evil-nix），社区当笑话看但技术真实 |
| `mirkolenz/llmhop` | topic 78057 | NixOS module 跑多个 LLM 推理服务器并在它们之间路由 |
| `deepclause/agentvm` | HN 评论提及 | container2wasm 实现的 agent VM |

**一个非常实用的经验（`bitbloxhub`，topic 76873，已核实）**：
> "I run the Pi coding agent in a arch distrobox, it seems to work well. There are also some third-party flakes for it, but **I prefer the distrobox as Pi moves much faster than I update my flake inputs**, and I am also unsure how well they work with extensions."

即：**对更新极快的 agent，用 distrobox 容器而不是钉死在 flake 里**——这是社区给出的可操作妥协。

### 3.5 模式 E：AI 教学 / 给 agent 写技能

**`olafkfreund` 的 `nix-skills`（topic 80199，2026-09-22，已核实）**——声明「由 Claude、Codex、Antigravity 协助创建，全部经人工 review」：

| Skill | 用途 | 参考基准 |
|---|---|---|
| `nix-language` | 写/解释/调试/审查 Nix 表达式 | Nix 2.35.2 |
| `devenv-project` | 配置与排查 devenv 项目环境 | devenv v2.3.1 |
| `nixpkgs-development` | 打包、overlay、library API | master 快照 + 26.11 |
| `nixos-wiki` | 查 NixOS 配置与排障 | 2026-09-22 导出的 17 个精选主题 |

**`tomberek` 给出的「AI 明显需要指导的事」清单（topic 80199 #4，已核实，本轮最高价值段落之一）**：

> - "find /nix/store/*something-* -iname libsomething.so **please never do this**"
> - "not understanding devShells"
> - "**teach it nix-index**"
> - "when packaging or running into errors it is almost always helpful to **search through expertise in the Nixpkgs repo issues/prs**"
> - "(my pet peeve: using python when awk/jq would be just as fine)"
>
> "Also note that the entrypoint into the ecosytem for different people tends to fall into a few categories. Their user experience tends to be different enough to have specialized skills for: **developers** (using Nix itself, devShells are common) / **home-manger** (customizing, adjusting, often on darwin) / **nixos** (…)"

**`lucasew` 的 skills for nixpkgs（topic 78627，419 赞）**：提议把流程固化成 agent 可读的 checklist，并明确指出「**Today, the skill location is standard; place them on .agents/skills**」。

### 3.6 模式 F：本地推理 / GPU

- `60594`：*Getting Started with Local LLM on NixOS (CUDA, Ollama, Open WebUI)*（已核实）。
- `fieldempty` 的 brain 机器本身就是「本地 LLM 当 NixOS 管理员」的设想（本地 Llama/Qwen，不走云 API）。
- `LorenzBischof` 用 lmstudio，朋友更信 vLLM（topic 76873）。
- `64345` *Nothing but Nix*（87 赞）：痛点是「每次改配置都要为第三方内核模块、Ollama、自定义 override 额外编译」——**本地 AI 负载放大了 NixOS 的编译时间问题**。

---

## 4. 翻车与坑：社区实测出来的真实问题

### 4.1 「generation 回滚」的安全性被高估（本轮最重要的技术警告）

`cafkafk`（topic 72275 #6，2025-11-19，已核实）直接反驳了「最坏损失一个 generation」：

> "The worst thing that can happen is we lose one generation and be back exactly where we started. **This is a bit of a lie we tell to kids.** In reality, aside from just the config (which Nix gives you rollback for), there is also **the state of databases and such, as well as distributed state** (e.g., if you are running any distributed systems — think Matrix protocol, Fediverse, things like that).
> Thus, the realistically best guarantee you can actually get is **Nix + file-system snapshots** for rollback of local-state and config. But there doesn't seem to be any general purpose hammer that you can hit distributed state with yet to give you rollback: worth keeping in mind!"

**可操作结论**：让 AI 改 NixOS 之前，先配置**文件系统快照**（ZFS/Btrfs snapshot），否则数据库/有状态服务的变更不在回滚范围内。这与前几轮调研中 `mcp-nixos-ops` 的「ZFS 预检门」是同一个结论的不同表达（`社区实证`）。

### 4.2 「模型根本不懂 Nix」

- `sunya`（topic 72028）：「**Google Gemini or ChatGPT know very little about Nix**」（已核实）。
- `cafkafk`：「**LMs aren't there yet for Nix/NixOS in my experience**, but they're getting there. Seems the best way to make them sort of useful is to **put a local copy of the manuals in RAG and give them access to a local checkout of nixpkgs** for referncing. Generally, **search tools just seem to make them hallucinate even more** in my experience.」（已核实）
  - ⚠️ 注意最后一句与主流「上 MCP/搜索工具」的建议**相反**——这是本轮发现的少数反直觉证据，值得记录为存疑项。
- `7karni`（topic 72275 #7）贴出「ChatGPT 5.1 sanity-checking a minor package.nix PR」的截图作为反例（已核实，图内容未逐像素判读）。

### 4.3 「vibe coded 工具」质量与信任危机

`ttamttam1` 发起、**389 赞**的讨论（topic 76300，2026-03-16，已核实）：

> "someone announces a new tool that looks exciting, and then it turns out to be vibe coded. I come into these projects super excited, read through their code, realize it's **hastily generated AI slop, spot a few security red flags**, don't even bother pointing them out because the project is BSL or ARR licensed... In fact it feels like **vibe coded projects are quickly becoming nearly as abundant as normal projects**."

`lisanna`（同帖，已核实）：
> "Back when I tried out vibe coding earlier this year with Opus 4.5 I had a miserable experience getting it to produce something even barely working, let alone good, when I asked it to re-implement part of my custom build hook. **I didn't know it was possible to be bad at vibe coding as a software engineer with a decade of experience using a frontier model**..."

`TLATER`（topic 79202，已核实）看到某工具的 client/server 设计时的反应：
> "Docker-style client/server thing Very weird, **was this created because the author doesn't grok systemd units and asked an LLM to write something in rust?**"

### 4.4 「AI 味」可被识别

- `abathur`（topic 29018）：「sounds very much like **how ChatGPT responds to being corrected**」（已核实）。
- `numinit`（topic 79736 #2，已核实）：「Ironically, **LLMs tend to be excellent at summarization, but people still use it to submit walls of text** for some reason。」
- `rhendric`（topic 79021）在同帖直接问：「**Am I talking to an LLM?**」（已核实）。
- `ethancedwards`（topic 79736 #1）描述的现象：PR 描述 804 词、commit message 550 词、单条评论 150+ 词——「**I doubt they've read the code**」。

### 4.5 状态管理需要真实删除权限

`7c6f434c`（topic 72275 #5，已核实）指出 agent 架构的一个硬缺口：
> "some **state management (cleaning up stale data of specific services) needs actually deleting things locally**, and getting to do this management requires **privileged access**."

即：纯声明式 + 只出 diff 的做法，覆盖不了「清理服务残留数据」这类必须真的删东西的场景。

---

## 5. 社区态度光谱：从抵制到拥抱

### 5.1 官方政策（最重要的锚点）

nixpkgs core team 2026-05-11 更新（topic 77567，74 赞，已核实），社区成员 `malikwirin` 引述的政策核心：

> "Every contribution to Nixpkgs and related development venues, including code, documentation, and communication on GitHub and Matrix, **must have a responsible person in the loop who is accountable for that contribution and reviews it before submission, and must transparently disclose any non-trivial use of automation** to produce it, including but not limited to LLM-based AI tools."

配套规则：不披露复杂自动化 + 自动化产生的内容直接被拒；PR 模板要求人类先写摘要。

### 5.2 立场分布（按原话归类）

| 立场 | 代表 | 原话（已核实） |
|---|---|---|
| **工具可用，拒绝低质量** | `knoopx` | "im not against llms as tools, im against the corporate circus and low effort contributions. i dont mind if contributors use llms as long as they **review, test and communicate as humans**." 并引用 *"a computer can never be held accountable, therefore a computer must never make a management decision."* |
| **问题不是 AI 是 slop** | `tejing` | "Banning AI entirely is too unenforceable... **AI isn't the problem. Slop is the problem.** I see no reason to use those tools myself, but I acknowledge that some workflows involving such tools can produce results of sufficient quality." |
| **政策已是最优妥协** | `TLATER` | "Given the upstream contributor base a full rejection is almost definitely impossible... **This policy is probably the most sensible compromise possible.**" |
| **自由软件原则反对** | `coolcuber` | "using **proprietary LLMs to develop free software is too far for me**... Having an agents.md file in the root directory of Nixpkgs is not something I would ever use... adding a symlink called CLAUDE.md... **is an indirect endorsement of unfree tooling** right in the root directory of Nixpkgs." |
| **实用主义分家路线** | `tomberek` | "reduce the contention. Create and start a project to make such documentation, skills, tools, guides, whatever, **in an new repo. Make it usable as a sidecar**... **People that want to opt-in can; and those that want to opt-out don't need to do anything.**" |
| **文档优先服务于人** | `mihaimarcheac` | "I work in AI, I use AI a lot, but **relying on AIs for too long and reading their output is a sure way to ingest brain asbesthos**. Documentation should be **for the users first, then for the developers, and only then for agents**." |
| **反对「agent 专用文档」** | `arcayr` | "i'm unsure why you believe that a linux distribution almost exclusively centered around being able to **manually put together exactly the system you want** in a declarative fashion would be best served by throwing it into what is, for most people, **a magic black box**..." |
| **无障碍/健康需求方** | `ashebanow` | "I have **Long COVID**, and if I try to program, I have only a few hours before my brain fogs out... **Using LLMs has changed that.** I can invest the hours I have available to build a harness and build rigid quality standards. I then let the LLM run with that while I rest. **It's been a huge force multiplier**..." |
| **社区氛围警告** | `samestep` | "I'm sorry for the overly hostile responses you're receiving... Unfortunately **AI is quite a sore subject in this community**... right now it's simply **difficult to have productive discussions about these topics**." |

### 5.3 声量与人数的错位

- 直接反对 AI 的命中贴文只有 **32 条**（3.3%），但「Call to ban AI commits」拿到 **618 赞**、「LLMs in nixpkgs」**788 赞**、「Can we explicitly ban LLM-generated PR descriptions」**352 赞**。
- 说明：**反对者在少数帖子高度集中并高赞，支持者分散在大量工具/工作流帖里**。用「命中数」衡量会低估反对声量，用「最高赞帖」衡量会低估实际使用者数量（`推断`）。

---

## 6. 工具与项目生态（本轮抓取实证）

### 6.1 给 AI 接 NixOS 事实源（MCP / 数据源）

| 项目 | 星/许可 | 本轮证据 | 用途 |
|---|---|---|---|
| `utensils/mcp-nixos` | 853★ MIT | Discourse 62640 + HN + KB 前轮 | 包/选项/HM/nix-darwin/noogle 查询，约 1,030 token 上下文 |
| `utensils/mcp-nixos-ops` 等 ops 类 | — | 前轮 KB | build/diff/switch/rollback + ZFS 预检门 |
| `natsukium/mcp-servers-nix` | 308★ | HN + 前轮 | 27 个 MCP 模块 + 7 客户端口味 |
| `nixos-kr/ephemeral-nixos-on-discord` | — | GitHub README | Discord bot + 临时 NixOS VM + LLM 教学 |

### 6.2 给 agent 的技能 / 文档

| 项目 | 证据 | 说明 |
|---|---|---|
| `olafkfreund/nix-skills` | topic 80199，17 赞 | 4 个 skill，声称 Claude/Codex/Antigravity 协助创建 + 人工 review |
| `olafkfreund/agent-skills-nix` | topic 80199 + 前轮 | 声明式 skill 管理，10 个 agent 目标路径 |
| `michalzubkowicz/nixos-management-skill` | 前轮 KB | rebuild/flake 管理技能 |
| `.agents/skills/` 约定 | `lucasew`，topic 78627 | 社区正在形成的标准位置 |

### 6.3 用 Nix 跑 AI 工具

| 项目 | 证据 | 说明 |
|---|---|---|
| `numtide/llm-agents.nix` | topic 76873 + HN | 每日自动更新的 agent 包集合 |
| Pi coding agent flakes | topic 78034 / 78035 | `services.pi-coding-agent` |
| `nixified-ai/flake` | GitHub | AI 项目 flake + 二进制缓存 |
| `cdepillabout/mkAIDerivation` | topic 66137，87 赞 | LLM 现场生成 derivation（IFD） |
| `mirkolenz/llmhop` | topic 78057 | NixOS module 路由多个 LLM 推理服务器 |
| `microvm.nix` | HN 109 分 | coding agent VM 基座 |
| `deepclause/agentvm` | HN 评论 | container2wasm agent VM |

---

## 7. 可复用结论（落地建议）

1. **闭环照抄社区收敛出的形态**：AI 只出 diff → `nixos-rebuild dry-activate` 展示 → 人工确认 → `switch` → 健康检查失败自动 `--rollback`。多个独立来源（用户设想 + `mcp-nixos-ops` + `clawnix`）给出同一答案。
2. **先配快照再让 AI 碰系统**：generation 回滚不覆盖数据库与分布式状态，ZFS/Btrfs 快照是真实安全网。
3. **默认联网模型不懂 Nix，必须给事实源**：本地 nixpkgs checkout + 手册副本（RAG）或 `mcp-nixos` 类 MCP；注意有使用者反馈「搜索工具反而增加幻觉」，需自行 A/B。
4. **技能按使用者类型分开写**（`tomberek`）：开发者（devShells 常见）/ home-manager 用户（常在 darwin）/ NixOS 管理员——三套入口经验差异大到需要专门 skill。
5. **给 agent 的禁令要写进 skill**：不要 `find /nix/store/*...-* -iname lib*.so`；不会用 devShell；要会用 `nix-index`；打包报错去搜 nixpkgs issue/PR。
6. **对更新极快的 agent 用 distrobox 而非钉死 flake**（`bitbloxhub` 实证），否则追版本成本吃掉收益。
7. **合规最小动作**：披露。任何 AI 参与的提交加 `Assisted-by` / `Co-authored-by` 说明，是 nixpkgs 政策的硬要求，也是社区信任的底线。

---

## 8. 未核实 / 存疑

| 项 | 状态 |
|---|---|
| Reddit / X / Discord 的真实讨论量与内容 | **未采集到**（反爬阻断），本报告不含这三平台的一手贴文。补采需换出口 IP 或 Reddit API 凭据 |
| `cafkafk` 说「搜索工具让模型幻觉更多」 | 单一来源，与主流建议相反，标为`存疑` |
| ChatGPT 5.1 检查 package.nix 的截图结论 | 有图未逐像素判读，仅记录存在该反例 |
| 979 条的社群代表性 | 只覆盖 Discourse/HN/GitHub 三个可编程采集源；Reddit 缺失会改变权重分布 |
| `mkAIDerivation` 是否被实际使用 | 社区当玩笑讨论，未见使用报告 |
| `nixos-kr/ephemeral-nixos-on-discord` 的活跃度/star 数 | 只读了 README，未查仓库元数据 |
| 「反对 32 条 vs 618 赞」的声量推断 | 基于本轮样本，`推断`级 |

---

## 9. References（本轮实际访问的一手来源）

### 9.1 NixOS Discourse 主题（读全文的 60 个）

- [Nixpkgs's current development workflow is not sustainable](https://discourse.nixos.org/t/nixpkgss-current-development-workflow-is-not-sustainable/18741) — 858 赞 / 116 回复 / 2022-04-20
- [LLMs in nixpkgs](https://discourse.nixos.org/t/llms-in-nixpkgs/78964) — 788 赞 / 94 回复 / 2026-07-15
- [Call to ban AI commits](https://discourse.nixos.org/t/call-to-ban-ai-commits/78262) — 618 赞 / 93 回复 / 2026-06-14
- [Init System freedom on NixOS](https://discourse.nixos.org/t/init-system-freedom-on-nixos/78333) — 542 赞 / 135 回复 / 2026-06-17
- [Documentation needs to be created towards agents](https://discourse.nixos.org/t/documentation-needs-to-be-created-towards-agents/80179) — 423 赞 / 59 回复 / 2026-09-21
- [Let's create skills for nixpkgs development](https://discourse.nixos.org/t/lets-create-skills-for-nixpkgs-development/78627) — 419 赞 / 48 回复 / 2026-06-28
- [Policy on vibe coded nix tools?](https://discourse.nixos.org/t/policy-on-vibe-coded-nix-tools/76300) — 389 赞 / 72 回复 / 2026-03-16
- [Can we explicitly ban LLM-generated PR descriptions, commits?](https://discourse.nixos.org/t/can-we-explicitly-ban-llm-generated-pr-descriptions-commits/79736) — 352 赞 / 62 回复 / 2026-08-25
- [PRs already reviewed](https://discourse.nixos.org/t/prs-already-reviewed/2617) — 340 赞 / 3222 回复 / 2019-04-07
- [PRs ready for review _](https://discourse.nixos.org/t/prs-ready-for-review/3032) — 322 赞 / 7409 回复 / 2019-05-25
- [Nix-init - Generate Nix packages from URLs with hash prefetching, dependency inference, li](https://discourse.nixos.org/t/nix-init-generate-nix-packages-from-urls-with-hash-prefetching-dependency-inference-license-detection-and-more/25035) — 176 赞 / 23 回复 / 2023-01-28
- [How to piss off your Nix friends](https://discourse.nixos.org/t/how-to-piss-off-your-nix-friends/79881) — 125 赞 / 24 回复 / 2026-09-01
- [Outdated vulnerable applications in the official repository](https://discourse.nixos.org/t/outdated-vulnerable-applications-in-the-official-repository/79021) — 108 赞 / 55 回复 / 2026-07-17
- [Radically improving Nix/NixOS security with Fil-C](https://discourse.nixos.org/t/radically-improving-nix-nixos-security-with-fil-c/71476) — 104 赞 / 29 回复 / 2025-10-29
- [Nothing but Nix - reclaim 130GB for Nix in GitHub runners](https://discourse.nixos.org/t/nothing-but-nix-reclaim-130gb-for-nix-in-github-runners/64345) — 87 赞 / 13 回复 / 2025-05-16
- [mkAIDerivation: generate a derivation on the fly from a prompt using an LLM](https://discourse.nixos.org/t/mkaiderivation-generate-a-derivation-on-the-fly-from-a-prompt-using-an-llm/66137) — 81 赞 / 13 回复 / 2025-06-27
- [Nixpkgs core team update 2026-05-11 – automation/AI policy feedback and new members wanted](https://discourse.nixos.org/t/nixpkgs-core-team-update-2026-05-11-automation-ai-policy-feedback-and-new-members-wanted/77567) — 74 赞 / 4 回复 / 2026-05-11
- [[no-LLM] `nix-weather-hs` - analyzing un-built derivation graphs for cache availablility](https://discourse.nixos.org/t/no-llm-nix-weather-hs-analyzing-un-built-derivation-graphs-for-cache-availablility/79113) — 51 赞 / 27 回复 / 2026-07-22
- [Running playwright tests](https://discourse.nixos.org/t/running-playwright-tests/25655) — 48 赞 / 55 回复 / 2023-02-21
- [Better why-depends (fill in the gaps)](https://discourse.nixos.org/t/better-why-depends-fill-in-the-gaps/31246) — 44 赞 / 11 回复 / 2023-08-03
- [Tix - A custom nix type checker/LSP](https://discourse.nixos.org/t/tix-a-custom-nix-type-checker-lsp/76810) — 40 赞 / 13 回复 / 2026-04-03
- [Nixos-telemetry flake](https://discourse.nixos.org/t/nixos-telemetry-flake/79704) — 38 赞 / 27 回复 / 2026-08-23
- [Copilot in nixpkgs pull requests?](https://discourse.nixos.org/t/copilot-in-nixpkgs-pull-requests/70332) — 38 赞 / 14 回复 / 2025-10-03
- [Agentic control layer for NixOS that proposes patches instead of mutating directly](https://discourse.nixos.org/t/agentic-control-layer-for-nixos-that-proposes-patches-instead-of-mutating-directly/77419) — 34 赞 / 15 回复 / 2026-05-05
- [Dynamic Derivations Working Group #2](https://discourse.nixos.org/t/dynamic-derivations-working-group-2/79802) — 33 赞 / 10 回复 / 2026-08-28
- [🚀 Introducing nixai: Your AI-Powered NixOS Companion](https://discourse.nixos.org/t/introducing-nixai-your-ai-powered-nixos-companion/65168) — 31 赞 / 19 回复 / 2025-06-04
- [What are the differences between nix-bwrapper, nixpak, jail.nix and nixjail and which one ](https://discourse.nixos.org/t/what-are-the-differences-between-nix-bwrapper-nixpak-jail-nix-and-nixjail-and-which-one-should-i-chose/79202) — 30 赞 / 8 回复 / 2026-07-28
- [A few annecdotal NixOS install UX issues](https://discourse.nixos.org/t/a-few-annecdotal-nixos-install-ux-issues/63546) — 27 赞 / 13 回复 / 2025-04-27
- [NixOS automation with AI](https://discourse.nixos.org/t/nixos-automation-with-ai/72275) — 26 赞 / 9 回复 / 2025-11-18
- [Nix-housing: live inside a sandbox - better hygiene for your shell](https://discourse.nixos.org/t/nix-housing-live-inside-a-sandbox-better-hygiene-for-your-shell/79501) — 25 赞 / 5 回复 / 2026-08-10
- [Should we add AI tool Co-authored-by linting to CI?](https://discourse.nixos.org/t/should-we-add-ai-tool-co-authored-by-linting-to-ci/80177) — 22 赞 / 6 回复 / 2026-09-21
- ["Eelco's Legacy"](https://discourse.nixos.org/t/eelcos-legacy/21832) — 20 赞 / 3 回复 / 2022-09-19
- [50$ bounty for Modelio](https://discourse.nixos.org/t/50-bounty-for-modelio/76502) — 18 赞 / 19 回复 / 2026-03-22
- [Packaging Claude Code on NixOS](https://discourse.nixos.org/t/packaging-claude-code-on-nixos/61072) — 18 赞 / 9 回复 / 2025-03-02
- [MCP-NixOS - Because Your AI Assistant Shouldn't Hallucinate About Packages](https://discourse.nixos.org/t/mcp-nixos-because-your-ai-assistant-shouldnt-hallucinate-about-packages/62640) — 17 赞 / 1 回复 / 2025-04-04
- [NixOs and Nix skill for LLM's](https://discourse.nixos.org/t/nixos-and-nix-skill-for-llms/80199) — 17 赞 / 6 回复 / 2026-09-22
- [Use of ChatGPT et al](https://discourse.nixos.org/t/use-of-chatgpt-et-al/29018) — 16 赞 / 2 回复 / 2023-06-11
- [Nix flake check + JUnit = Junix](https://discourse.nixos.org/t/nix-flake-check-junit-junix/79124) — 16 赞 / 8 回复 / 2026-07-23
- [The Nix moment: how LLMs, advances in hardware, big name adoption, and the supply chain ar](https://discourse.nixos.org/t/the-nix-moment-how-llms-advances-in-hardware-big-name-adoption-and-the-supply-chain-are-pushing-nix-well-past-the-inflection-point/77272) — 15 赞 / 3 回复 / 2026-04-27
- [Great Software that should be in nixpkgs](https://discourse.nixos.org/t/great-software-that-should-be-in-nixpkgs/68131) — 15 赞 / 12 回复 / 2025-08-19
- [Updated after 3 week vacation. gnupg says "no pinentry"](https://discourse.nixos.org/t/updated-after-3-week-vacation-gnupg-says-no-pinentry/4731) — 13 赞 / 10 回复 / 2019-11-10
- [Coding Agent workflow for NixOS](https://discourse.nixos.org/t/coding-agent-workflow-for-nixos/76873) — 12 赞 / 5 回复 / 2026-04-06
- [A GPT3 Rant about NixOS](https://discourse.nixos.org/t/a-gpt3-rant-about-nixos/24341) — 11 赞 / 3 回复 / 2022-12-31
- [Setting Deep learning Python project with CUDA support using uv2nix](https://discourse.nixos.org/t/setting-deep-learning-python-project-with-cuda-support-using-uv2nix/72028) — 11 赞 / 3 回复 / 2025-11-12
- [Add SSH key to agent at login using KWallet](https://discourse.nixos.org/t/add-ssh-key-to-agent-at-login-using-kwallet/25175) — 11 赞 / 7 回复 / 2023-02-02
- [PhoeNix: managing NixOS machines through templates, flakes, PXE and nixos-anywhere](https://discourse.nixos.org/t/phoenix-managing-nixos-machines-through-templates-flakes-pxe-and-nixos-anywhere/78143) — 9 赞 / 3 回复 / 2026-06-08
- [`gitlab:`-formatted flake inputs now blocked by Cloudflare](https://discourse.nixos.org/t/gitlab-formatted-flake-inputs-now-blocked-by-cloudflare/80505) — 9 赞 / 11 回复 / 2026-10-10
- [Managing Multiple NixOS Machines with Claude Code via SSH](https://discourse.nixos.org/t/managing-multiple-nixos-machines-with-claude-code-via-ssh/74259) — 8 赞 / 3 回复 / 2026-01-13
- [This month in Nix documentation - #6 - March to May 2024](https://discourse.nixos.org/t/this-month-in-nix-documentation-6-march-to-may-2024/46894) — 7 赞 / 1 回复 / 2024-06-12
- [Packaging Open Policy Agent policies with Nix · Determinate Systems](https://discourse.nixos.org/t/packaging-open-policy-agent-policies-with-nix-determinate-systems/28379) — 7 赞 / 3 回复 / 2023-05-22
- [Getting Started with Local LLM on NixOS (CUDA, Ollama, Open WebUI)](https://discourse.nixos.org/t/getting-started-with-local-llm-on-nixos-cuda-ollama-open-webui/60594) — 5 赞 / 1 回复 / 2025-02-20
- [Run local AI chatbot using Nix](https://discourse.nixos.org/t/run-local-ai-chatbot-using-nix/48382) — 5 赞 / 1 回复 / 2024-07-03
- [Coding Agent VMs on NixOS with microvm.nix](https://discourse.nixos.org/t/coding-agent-vms-on-nixos-with-microvm-nix/75152) — 5 赞 / 2 回复 / 2026-02-09
- [Pi-flake – Nix flake for Pi coding agent (NixOS + Home Manager modules)](https://discourse.nixos.org/t/pi-flake-nix-flake-for-pi-coding-agent-nixos-home-manager-modules/78034) — 5 赞 / 2 回复 / 2026-06-03
- [Claude Code and security isolation](https://discourse.nixos.org/t/claude-code-and-security-isolation/71543) — 4 赞 / 5 回复 / 2025-10-31
- [EloTouch Multitouch driver](https://discourse.nixos.org/t/elotouch-multitouch-driver/79267) — 4 赞 / 1 回复 / 2026-07-31
- [NixPaint, Paint with Lambda's](https://discourse.nixos.org/t/nixpaint-paint-with-lambdas/77203) — 4 赞 / 2 回复 / 2026-04-23
- [Local AI agent for NixOS configuration — looking for experience reports](https://discourse.nixos.org/t/local-ai-agent-for-nixos-configuration-looking-for-experience-reports/77238) — 3 赞 / 9 回复 / 2026-04-26
- [How to install Pi coding agent on NixOS with Home Manager](https://discourse.nixos.org/t/how-to-install-pi-coding-agent-on-nixos-with-home-manager/78035) — 3 赞 / 1 回复 / 2026-06-03
- [NixOS module that runs your LLM inference servers and routes between them](https://discourse.nixos.org/t/nixos-module-that-runs-your-llm-inference-servers-and-routes-between-them/78057) — 2 赞 / 2 回复 / 2026-06-04

### 9.2 Hacker News（Algolia API）

- [HN Algolia Search API](https://hn.algolia.com/api/v1/search?query=nixos+ai) — 本轮 13 组查询入口
- [Coding Agent VMs on NixOS with Microvm.nix](https://news.ycombinator.com/item?id=46844410) — 109 分 / 48 评论
- [Show HN: Microsoft Office running with Wine on Linux with no virtualization](https://news.ycombinator.com/item?id=49746401) — 97 分 / 91 评论
- [Show HN: Nucleus – A security-hardened, Nix-native container runtime](https://news.ycombinator.com/item?id=48469039) — 40 分 / 13 评论
- [Ask HN: Is GPT-5 a regression, or is it just me?](https://news.ycombinator.com/item?id=45238859) — 6 分 / 7 评论
- [Using "Hi Claudette " on Claude.ai](https://news.ycombinator.com/item?id=47143143) — 4 分 / 2 评论
- [Show HN: 60-Second Linux Analysis, Supercharged with Nix and LLMs](https://news.ycombinator.com/item?id=45150357) — 4 分 / 1 评论
- [Show HN: A lightweight Git history explorer written in Go](https://news.ycombinator.com/item?id=46237588) — 3 分 / 0 评论
- [Show HN: nix-mcp-servers – MCP server Nix package repo](https://news.ycombinator.com/item?id=43614089) — 3 分 / 2 评论
- [MCP-NixOS: When Your AI Needs to Learn NixOS Options Aren't Magic](https://news.ycombinator.com/item?id=43513181) — 2 分 / 1 评论
- [Linux Prepper Podcast – Episode on Trying NixOS, Selfhosted Tools, Local AI](https://news.ycombinator.com/item?id=43601984) — 2 分 / 1 评论
- [Prototyping NixOS with FDE, tang and Podman using Claude.AI](https://news.ycombinator.com/item?id=46750444) — 2 分 / 1 评论
- [Show HN: Grain Synonym: Create multi-aesthetic OS variants](https://news.ycombinator.com/item?id=46638956) — 2 分 / 0 评论

### 9.3 GitHub

- [GitHub Search Issues API](https://api.github.com/search/issues?q=nixos+ai+agent) — 3 组查询，102 个仓库
- https://github.com/NixOS/nixpkgs — 23 条命中
- https://github.com/shikanime-labs/machines — 5 条命中
- https://github.com/agentydragon/ducktape — 4 条命中
- https://github.com/higherorderfunctor/nix-agentic-tools — 4 条命中
- https://github.com/logos-co/logos-basecamp — 4 条命中
- https://github.com/BJSummerfield/nixcfg — 3 条命中
- https://github.com/tkoyama010/dotfiles — 3 条命中
- https://github.com/cloud-gouv/securix — 2 条命中
- https://github.com/bmazzarol-bunnings/bmazzarol-bunnings — 2 条命中
- https://github.com/MasterofNull/NixOS-Dev-Quick-Deploy — 2 条命中

### 9.4 其他

- https://michael.stapelberg.ch/posts/2026-02-01-coding-agent-microvm-nix/ — Coding Agent VMs on NixOS with microvm.nix（HN 109 分故事的来源）
- https://github.com/nixos-kr/ephemeral-nixos-on-discord/ — Discord bot + 临时 NixOS VM + LLM 教学
- https://github.com/cdepillabout/mkAIDerivation — LLM 现场生成 derivation
- https://github.com/numtide/llm-agents.nix — AI coding agent 的 Nix 包集合
- https://github.com/olafkfreund/nix-skills — 可复用 Nix agent skills
- https://github.com/deepclause/agentvm — container2wasm agent VM（HN 评论提及）

---

## 附录：贴文明细（精选）

### A. NixOS Discourse 主题（按赞数排序，共 60 个主题已读全文）

| # | 赞 | 回复 | 日期 | 主题 | 分类 | 链接 |
|---|---|---|---|---|---|---|
| 1 | 858 | 116 | 2022-04-20 | Nixpkgs's current development workflow is not sustainable | 教学 | [link](https://discourse.nixos.org/t/nixpkgss-current-development-workflow-is-not-sustainable/18741) |
| 2 | 788 | 94 | 2026-07-15 | LLMs in nixpkgs | 综合 | [link](https://discourse.nixos.org/t/llms-in-nixpkgs/78964) |
| 3 | 618 | 93 | 2026-06-14 | Call to ban AI commits | 综合 | [link](https://discourse.nixos.org/t/call-to-ban-ai-commits/78262) |
| 4 | 542 | 135 | 2026-06-17 | Init System freedom on NixOS | 打包AI工具 | [link](https://discourse.nixos.org/t/init-system-freedom-on-nixos/78333) |
| 5 | 423 | 59 | 2026-09-21 | Documentation needs to be created towards agents | Agent运维/MCP | [link](https://discourse.nixos.org/t/documentation-needs-to-be-created-towards-agents/80179) |
| 6 | 419 | 48 | 2026-06-28 | Let's create skills for nixpkgs development | 打包AI工具 | [link](https://discourse.nixos.org/t/lets-create-skills-for-nixpkgs-development/78627) |
| 7 | 389 | 72 | 2026-03-16 | Policy on vibe coded nix tools? | 翻车 | [link](https://discourse.nixos.org/t/policy-on-vibe-coded-nix-tools/76300) |
| 8 | 352 | 62 | 2026-08-25 | Can we explicitly ban LLM-generated PR descriptions, commits? | 综合 | [link](https://discourse.nixos.org/t/can-we-explicitly-ban-llm-generated-pr-descriptions-commits/79736) |
| 9 | 340 | 3222 | 2019-04-07 | PRs already reviewed | 写配置/Agent运维 | [link](https://discourse.nixos.org/t/prs-already-reviewed/2617) |
| 10 | 322 | 7409 | 2019-05-25 | PRs ready for review _ | Agent运维/打包AI工具 | [link](https://discourse.nixos.org/t/prs-ready-for-review/3032) |
| 11 | 176 | 23 | 2023-01-28 | Nix-init - Generate Nix packages from URLs with hash prefetching, dependency i | 综合 | [link](https://discourse.nixos.org/t/nix-init-generate-nix-packages-from-urls-with-hash-prefetching-dependency-inference-license-detection-and-more/25035) |
| 12 | 125 | 24 | 2026-09-01 | How to piss off your Nix friends | 反对 | [link](https://discourse.nixos.org/t/how-to-piss-off-your-nix-friends/79881) |
| 13 | 108 | 55 | 2026-07-17 | Outdated vulnerable applications in the official repository | 打包AI工具 | [link](https://discourse.nixos.org/t/outdated-vulnerable-applications-in-the-official-repository/79021) |
| 14 | 104 | 29 | 2025-10-29 | Radically improving Nix/NixOS security with Fil-C | 综合 | [link](https://discourse.nixos.org/t/radically-improving-nix-nixos-security-with-fil-c/71476) |
| 15 | 87 | 13 | 2025-05-16 | Nothing but Nix - reclaim 130GB for Nix in GitHub runners | 综合 | [link](https://discourse.nixos.org/t/nothing-but-nix-reclaim-130gb-for-nix-in-github-runners/64345) |
| 16 | 81 | 13 | 2025-06-27 | mkAIDerivation: generate a derivation on the fly from a prompt using an LLM | 写配置/打包AI工具 | [link](https://discourse.nixos.org/t/mkaiderivation-generate-a-derivation-on-the-fly-from-a-prompt-using-an-llm/66137) |
| 17 | 74 | 4 | 2026-05-11 | Nixpkgs core team update 2026-05-11 – automation/AI policy feedback and new me | 打包AI工具 | [link](https://discourse.nixos.org/t/nixpkgs-core-team-update-2026-05-11-automation-ai-policy-feedback-and-new-members-wanted/77567) |
| 18 | 51 | 27 | 2026-07-22 | [no-LLM] `nix-weather-hs` - analyzing un-built derivation graphs for cache ava | 综合 | [link](https://discourse.nixos.org/t/no-llm-nix-weather-hs-analyzing-un-built-derivation-graphs-for-cache-availablility/79113) |
| 19 | 48 | 55 | 2023-02-21 | Running playwright tests | MCP | [link](https://discourse.nixos.org/t/running-playwright-tests/25655) |
| 20 | 44 | 11 | 2023-08-03 | Better why-depends (fill in the gaps) | 综合 | [link](https://discourse.nixos.org/t/better-why-depends-fill-in-the-gaps/31246) |
| 21 | 40 | 13 | 2026-04-03 | Tix - A custom nix type checker/LSP | 打包AI工具 | [link](https://discourse.nixos.org/t/tix-a-custom-nix-type-checker-lsp/76810) |
| 22 | 38 | 27 | 2026-08-23 | Nixos-telemetry flake | 综合 | [link](https://discourse.nixos.org/t/nixos-telemetry-flake/79704) |
| 23 | 38 | 14 | 2025-10-03 | Copilot in nixpkgs pull requests? | 打包AI工具 | [link](https://discourse.nixos.org/t/copilot-in-nixpkgs-pull-requests/70332) |
| 24 | 34 | 15 | 2026-05-05 | Agentic control layer for NixOS that proposes patches instead of mutating dire | 写配置/Agent运维 | [link](https://discourse.nixos.org/t/agentic-control-layer-for-nixos-that-proposes-patches-instead-of-mutating-directly/77419) |
| 25 | 33 | 10 | 2026-08-28 | Dynamic Derivations Working Group #2 | 综合 | [link](https://discourse.nixos.org/t/dynamic-derivations-working-group-2/79802) |
| 26 | 31 | 19 | 2025-06-04 | 🚀 Introducing nixai: Your AI-Powered NixOS Companion | 综合 | [link](https://discourse.nixos.org/t/introducing-nixai-your-ai-powered-nixos-companion/65168) |
| 27 | 30 | 8 | 2026-07-28 | What are the differences between nix-bwrapper, nixpak, jail.nix and nixjail an | 写配置/反对 | [link](https://discourse.nixos.org/t/what-are-the-differences-between-nix-bwrapper-nixpak-jail-nix-and-nixjail-and-which-one-should-i-chose/79202) |
| 28 | 27 | 13 | 2025-04-27 | A few annecdotal NixOS install UX issues | 综合 | [link](https://discourse.nixos.org/t/a-few-annecdotal-nixos-install-ux-issues/63546) |
| 29 | 26 | 9 | 2025-11-18 | NixOS automation with AI | 写配置 | [link](https://discourse.nixos.org/t/nixos-automation-with-ai/72275) |
| 30 | 25 | 5 | 2026-08-10 | Nix-housing: live inside a sandbox - better hygiene for your shell | 教学 | [link](https://discourse.nixos.org/t/nix-housing-live-inside-a-sandbox-better-hygiene-for-your-shell/79501) |
| 31 | 22 | 6 | 2026-09-21 | Should we add AI tool Co-authored-by linting to CI? | 打包AI工具 | [link](https://discourse.nixos.org/t/should-we-add-ai-tool-co-authored-by-linting-to-ci/80177) |
| 32 | 20 | 3 | 2022-09-19 | "Eelco's Legacy" | 综合 | [link](https://discourse.nixos.org/t/eelcos-legacy/21832) |
| 33 | 18 | 19 | 2026-03-22 | 50$ bounty for Modelio | 写配置 | [link](https://discourse.nixos.org/t/50-bounty-for-modelio/76502) |
| 34 | 18 | 9 | 2025-03-02 | Packaging Claude Code on NixOS | 打包AI工具 | [link](https://discourse.nixos.org/t/packaging-claude-code-on-nixos/61072) |
| 35 | 17 | 1 | 2025-04-04 | MCP-NixOS - Because Your AI Assistant Shouldn't Hallucinate About Packages | Agent运维/MCP | [link](https://discourse.nixos.org/t/mcp-nixos-because-your-ai-assistant-shouldnt-hallucinate-about-packages/62640) |
| 36 | 17 | 6 | 2026-09-22 | NixOs and Nix skill for LLM's | 综合 | [link](https://discourse.nixos.org/t/nixos-and-nix-skill-for-llms/80199) |
| 37 | 16 | 2 | 2023-06-11 | Use of ChatGPT et al | 综合 | [link](https://discourse.nixos.org/t/use-of-chatgpt-et-al/29018) |
| 38 | 16 | 8 | 2026-07-23 | Nix flake check + JUnit = Junix | 打包AI工具 | [link](https://discourse.nixos.org/t/nix-flake-check-junit-junix/79124) |
| 39 | 15 | 3 | 2026-04-27 | The Nix moment: how LLMs, advances in hardware, big name adoption, and the sup | 写配置/安全 | [link](https://discourse.nixos.org/t/the-nix-moment-how-llms-advances-in-hardware-big-name-adoption-and-the-supply-chain-are-pushing-nix-well-past-the-inflection-point/77272) |
| 40 | 15 | 12 | 2025-08-19 | Great Software that should be in nixpkgs | 综合 | [link](https://discourse.nixos.org/t/great-software-that-should-be-in-nixpkgs/68131) |
| 41 | 13 | 10 | 2019-11-10 | Updated after 3 week vacation. gnupg says "no pinentry" | Agent运维 | [link](https://discourse.nixos.org/t/updated-after-3-week-vacation-gnupg-says-no-pinentry/4731) |
| 42 | 12 | 5 | 2026-04-06 | Coding Agent workflow for NixOS | Agent运维/打包AI工具 | [link](https://discourse.nixos.org/t/coding-agent-workflow-for-nixos/76873) |
| 43 | 11 | 3 | 2022-12-31 | A GPT3 Rant about NixOS | 写配置/安全 | [link](https://discourse.nixos.org/t/a-gpt3-rant-about-nixos/24341) |
| 44 | 11 | 3 | 2025-11-12 | Setting Deep learning Python project with CUDA support using uv2nix | 写配置/安全 | [link](https://discourse.nixos.org/t/setting-deep-learning-python-project-with-cuda-support-using-uv2nix/72028) |
| 45 | 11 | 7 | 2023-02-02 | Add SSH key to agent at login using KWallet | Agent运维 | [link](https://discourse.nixos.org/t/add-ssh-key-to-agent-at-login-using-kwallet/25175) |
| 46 | 9 | 3 | 2026-06-08 | PhoeNix: managing NixOS machines through templates, flakes, PXE and nixos-anyw | MCP/教学 | [link](https://discourse.nixos.org/t/phoenix-managing-nixos-machines-through-templates-flakes-pxe-and-nixos-anywhere/78143) |
| 47 | 9 | 11 | 2026-10-10 | `gitlab:`-formatted flake inputs now blocked by Cloudflare | 综合 | [link](https://discourse.nixos.org/t/gitlab-formatted-flake-inputs-now-blocked-by-cloudflare/80505) |
| 48 | 8 | 3 | 2026-01-13 | Managing Multiple NixOS Machines with Claude Code via SSH | Agent运维 | [link](https://discourse.nixos.org/t/managing-multiple-nixos-machines-with-claude-code-via-ssh/74259) |
| 49 | 7 | 1 | 2024-06-12 | This month in Nix documentation - #6 - March to May 2024 | 写配置/打包AI工具 | [link](https://discourse.nixos.org/t/this-month-in-nix-documentation-6-march-to-may-2024/46894) |
| 50 | 7 | 3 | 2023-05-22 | Packaging Open Policy Agent policies with Nix · Determinate Systems | 综合 | [link](https://discourse.nixos.org/t/packaging-open-policy-agent-policies-with-nix-determinate-systems/28379) |
| 51 | 5 | 1 | 2025-02-20 | Getting Started with Local LLM on NixOS (CUDA, Ollama, Open WebUI) | 本地推理 | [link](https://discourse.nixos.org/t/getting-started-with-local-llm-on-nixos-cuda-ollama-open-webui/60594) |
| 52 | 5 | 1 | 2024-07-03 | Run local AI chatbot using Nix | 写配置 | [link](https://discourse.nixos.org/t/run-local-ai-chatbot-using-nix/48382) |
| 53 | 5 | 2 | 2026-02-09 | Coding Agent VMs on NixOS with microvm.nix | 综合 | [link](https://discourse.nixos.org/t/coding-agent-vms-on-nixos-with-microvm-nix/75152) |
| 54 | 5 | 2 | 2026-06-03 | Pi-flake – Nix flake for Pi coding agent (NixOS + Home Manager modules) | 写配置/Agent运维 | [link](https://discourse.nixos.org/t/pi-flake-nix-flake-for-pi-coding-agent-nixos-home-manager-modules/78034) |
| 55 | 4 | 5 | 2025-10-31 | Claude Code and security isolation | 安全 | [link](https://discourse.nixos.org/t/claude-code-and-security-isolation/71543) |
| 56 | 4 | 1 | 2026-07-31 | EloTouch Multitouch driver | 本地推理 | [link](https://discourse.nixos.org/t/elotouch-multitouch-driver/79267) |
| 57 | 4 | 2 | 2026-04-23 | NixPaint, Paint with Lambda's | 综合 | [link](https://discourse.nixos.org/t/nixpaint-paint-with-lambdas/77203) |
| 58 | 3 | 9 | 2026-04-26 | Local AI agent for NixOS configuration — looking for experience reports | 综合 | [link](https://discourse.nixos.org/t/local-ai-agent-for-nixos-configuration-looking-for-experience-reports/77238) |
| 59 | 3 | 1 | 2026-06-03 | How to install Pi coding agent on NixOS with Home Manager | 综合 | [link](https://discourse.nixos.org/t/how-to-install-pi-coding-agent-on-nixos-with-home-manager/78035) |
| 60 | 2 | 2 | 2026-06-04 | NixOS module that runs your LLM inference servers and routes between them | 本地推理 | [link](https://discourse.nixos.org/t/nixos-module-that-runs-your-llm-inference-servers-and-routes-between-them/78057) |

### B. Hacker News 条目（共 362 条匹配：28 故事 + 334 评论）

| # | 分 | 评论 | 日期 | 标题 | 分类 | 链接 |
|---|---|---|---|---|---|---|
| 1 | 109 | 48 | 2026-02-01 | Coding Agent VMs on NixOS with Microvm.nix | Agent运维 | [link](https://news.ycombinator.com/item?id=46844410) |
| 2 | 97 | 91 | 2026-09-17 | Show HN: Microsoft Office running with Wine on Linux with no virtualiz | 写配置/打包AI工具 | [link](https://news.ycombinator.com/item?id=49746401) |
| 3 | 40 | 13 | 2026-06-09 | Show HN: Nucleus – A security-hardened, Nix-native container runtime | Agent运维/安全 | [link](https://news.ycombinator.com/item?id=48469039) |
| 4 | 6 | 7 | 2025-09-14 | Ask HN: Is GPT-5 a regression, or is it just me? | 教学/翻车 | [link](https://news.ycombinator.com/item?id=45238859) |
| 5 | 4 | 2 | 2026-02-24 | Using "Hi Claudette " on Claude.ai | 写配置 | [link](https://news.ycombinator.com/item?id=47143143) |
| 6 | 4 | 1 | 2025-09-06 | Show HN: 60-Second Linux Analysis, Supercharged with Nix and LLMs | Agent运维/打包AI工具 | [link](https://news.ycombinator.com/item?id=45150357) |
| 7 | 3 | 0 | 2025-12-11 | Show HN: A lightweight Git history explorer written in Go | 综合 | [link](https://news.ycombinator.com/item?id=46237588) |
| 8 | 3 | 2 | 2025-04-07 | Show HN: nix-mcp-servers – MCP server Nix package repo | 写配置/MCP | [link](https://news.ycombinator.com/item?id=43614089) |
| 9 | 2 | 1 | 2025-03-29 | MCP-NixOS: When Your AI Needs to Learn NixOS Options Aren't Magic | MCP/教学 | [link](https://news.ycombinator.com/item?id=43513181) |
| 10 | 2 | 1 | 2025-04-06 | Linux Prepper Podcast – Episode on Trying NixOS, Selfhosted Tools, Loc | 综合 | [link](https://news.ycombinator.com/item?id=43601984) |
| 11 | 2 | 1 | 2026-01-25 | Prototyping NixOS with FDE, tang and Podman using Claude.AI | 综合 | [link](https://news.ycombinator.com/item?id=46750444) |
| 12 | 2 | 0 | 2026-01-15 | Show HN: Grain Synonym: Create multi-aesthetic OS variants | Agent运维 | [link](https://news.ycombinator.com/item?id=46638956) |
| 13 | 2 | 1 | 2026-02-09 | Show HN: Nix-sandbox-MCP: Reproducible, isolated code execution for Cl | MCP/安全 | [link](https://news.ycombinator.com/item?id=46948620) |
| 14 | 2 | 0 | 2024-06-18 | Vibe Transcribe – A FOSS local LLM front end for macOS, Windows and *N | 综合 | [link](https://news.ycombinator.com/item?id=40721284) |
| 15 | 2 | 0 | 2023-03-23 | Show HN: Inject VSCode code, errors, and definitions into your ChatGPT | 写配置/打包AI工具 | [link](https://news.ycombinator.com/item?id=35269246) |
| 16 | 2 | 1 | 2024-03-01 | CloudWatch Agent for NixOS | Agent运维 | [link](https://news.ycombinator.com/item?id=39560986) |
| 17 | 2 | 0 | 2026-02-02 | Coding Agent VMs on NixOS with Microvm.nix | Agent运维 | [link](https://news.ycombinator.com/item?id=46850952) |
| 18 | 2 | 0 | 2026-03-05 | Claude Code Live ISO for NixOS, Boot into a Sway Desktop with Claude C | 综合 | [link](https://news.ycombinator.com/item?id=47264218) |
| 19 | 2 | 0 | 2025-04-01 | Show HN: LDAPEnforcer, idempotent LDAP user and group management | 写配置 | [link](https://news.ycombinator.com/item?id=43546481) |
| 20 | 2 | 0 | 2026-06-05 | Show HN: LLMhop – A tiny, stateless router for LLMs with a NixOS modul | 写配置/本地推理 | [link](https://news.ycombinator.com/item?id=48406517) |
| 21 | 2 | 0 | 2026-09-16 | Show HN: Pkgbot – Fast Linux package search engine | 打包AI工具 | [link](https://news.ycombinator.com/item?id=49730611) |
| 22 | 2 | 0 | 2026-07-25 | Sandbox-bwrap-Nix: A lightweight sandbox for AI agents and experiments | Agent运维/安全 | [link](https://news.ycombinator.com/item?id=49046290) |
| 23 | 2 | 0 | 2025-07-25 | NixOS MCP Server | MCP | [link](https://news.ycombinator.com/item?id=44683707) |
| 24 | 1 | 0 | 2025-08-11 | Security by Compartmentalization for AI Coding Agents on NixOS | Agent运维/安全 | [link](https://news.ycombinator.com/item?id=44861448) |
| 25 | 1 | 0 | 2026-01-18 | Vibe Coding Safely: The Ultimate Guide to AI Dev with OpenCode and Nix | 综合 | [link](https://news.ycombinator.com/item?id=46670837) |
| 26 | 1 | 0 | 2026-02-26 | Show HN: Praktor – Multi-agent Claude Code orchestrator with Docker is | Agent运维/MCP | [link](https://news.ycombinator.com/item?id=47173187) |
| 27 | 1 | 0 | 2026-03-13 | Show HN: Nixcage – Sandbox AI coding agents per project with Nix and d | 安全 | [link](https://news.ycombinator.com/item?id=47365963) |
| 28 | 1 | 0 | 2025-06-30 | Future of post-open-source? Considering a "source-visible, non-runnabl | Agent运维/打包AI工具 | [link](https://news.ycombinator.com/item?id=44425545) |

**HN 高信息量评论摘选**（280 条超过 250 字符的匹配评论）：

- @gbro3n（2026-05-15）：Similar to this, but NixOS. Having AI to help me through made this so much easier. I was sold on the idea of an &#x27;IaC&#x27; config based machine, after a general push to move all of my processes towards full GitOps. Windows had been pretty good to me (running 4 years on the s [link](https://news.ycombinator.com/item?id=48151018)
- @QRY（2025-07-18）：Their work has molded a lot of my views on technology, such a breath of fresh air when I first found out about them! They really inspired me to look at my own work and ask how to make it more resilient, how to decrease dependencies. From my experience, achieving provider independ [link](https://news.ycombinator.com/item?id=44607150)
- @bigyabai（2026-09-10）：If we admit that iteration is part of quality, then you&#x27;ve basically just described why Omarchy keeps stubbing it&#x27;s toe on embarrassing issues like default container misconfiguration. > Maybe Nix is part of the solution, maybe staying on Arch and fixing problems there,  [link](https://news.ycombinator.com/item?id=49649710)
- @pxc（2026-06-26）：> Firstly, NixOS is hype NixOS is more than 20 years old, and virtually all of the things that make it compelling were already present a decade ago. If it&#x27;s not for you, you&#x27;ll know after you give it a try. But for those for whom it clicks, it&#x27;s desirable because i [link](https://news.ycombinator.com/item?id=48681695)
- @alembic_fumes（2026-03-22）：The author almost touches on the one more topic that I adore about Nix, but ends up just so missing it: NixOS is absolutely incredible for its ability to be configured through AI tooling. And I don&#x27;t mean that it&#x27;s better than other operating systems, I mean that it&#x2 [link](https://news.ycombinator.com/item?id=47482095)
- @ironmagma（2026-08-05）：Location: West coast (Fairbanks, AK) Remote: Yes Willing to relocate: No Technologies: Anything TypeScript-related, Go, Rust, Python, PHP, NixOS Resume&#x2F;CV: https:&#x2F;&#x2F;philippeterson.com&#x2F;resume LinkedIn: https:&#x2F;&#x2F;www.linkedin.com&#x2F;in&#x2F;philip-peter [link](https://news.ycombinator.com/item?id=49178756)
- @jquaint（2025-09-11）：For me, the success is having a simple way to prompt an Agent AI to modify my NixOS desktop and get live feedback. It can use the above MCP to search NixOS options and packages for me and make recommendations and edit the actual files, rebuild, etc. It can then use nix flake chec [link](https://news.ycombinator.com/item?id=45216846)
- @bigyabai（2026-09-10）：I think everything you just said is absolutely correct, and deliberately avoids answering my initial question. It&#x27;s an outraged response to my tone towards Arch, btw. Why is Omarchy&#x27;s AI-generated philosophy superior to NixOS&#x27; battle-tested architecture? Popularity [link](https://news.ycombinator.com/item?id=49637303)
- @wiether（2026-09-06）：> just giving the LLM the ssh keys and having at it. It’s pretty good. I&#x27;m mostly fine letting AI write code because its easily auditable and you can follow changes through the Git history. Whereas, it you let the AI go free on a server, you mostly have no idea what it did a [link](https://news.ycombinator.com/item?id=49584166)
- @rrvsh（2026-10-04）：Location: Singapore Remote: Yes Willing to relocate: Yes, preferably to San Francisco, but also open to New York and London. I am a Singapore citizen and eligible for the H-1B1 route for US roles. Technologies: Python, Rust, TypeScript, PostgreSQL, Nix&#x2F;NixOS, Linux, AWS, GCP [link](https://news.ycombinator.com/item?id=49950724)
- @jimnotgym（2026-09-25）：Well what I wrote was not on the homepage of nixos.com, or obvious after a few clicks. Claude summarised it very nicely. I now know I don&#x27;t need NixOS. Perhaps the real meatheads are the ones who spam threads with anti-ai memes, rather than looking at the utility of what the [link](https://news.ycombinator.com/item?id=49842517)
- @mirashii（2026-09-16）：The mistake here is thinking or treating AI tools as special or different in any way. We’ve had tooling that does this for decades. Ansible, puppet, saltstack, NixOS&#x2F;home-manager, and dozens of other solutions. Even better, writing the configuration is extra simple now, sinc [link](https://news.ycombinator.com/item?id=49729978)

### C. GitHub 条目（共 148 个匹配 / 去自动化噪声后 127 条，来自 102 个仓库）

| # | 仓库 | 类型 | 评论 | 日期 | 标题 | 链接 |
|---|---|---|---|---|---|---|
| 1 | `NixOS/nixpkgs` | pr | 27 | 2026-09-17 | python3Packages.openai: 2.53.0 -> 3.14.1 | [link](https://github.com/NixOS/nixpkgs/pull/564353) |
| 2 | `NixOS/nixpkgs` | pr | 16 | 2026-05-28 | ghidra: various fixes for aarch64-darwin | [link](https://github.com/NixOS/nixpkgs/pull/525313) |
| 3 | `TABConf/8.tabconf.com` | issue | 8 | 2026-06-28 | Agentic Engineering for Bitcoin Developers | [link](https://github.com/TABConf/8.tabconf.com/issues/11) |
| 4 | `NixOS/nixpkgs` | pr | 8 | 2026-10-06 | AGENTS.md: add instructions for LLMs | [link](https://github.com/NixOS/nixpkgs/pull/570711) |
| 5 | `defangdevs/agent-box` | pr | 6 | 2026-10-03 | feat: explicitly pair agent-box peers for direct messaging | [link](https://github.com/defangdevs/agent-box/pull/799) |
| 6 | `NixOS/nixpkgs` | pr | 6 | 2026-10-10 | .github/PULL_REQUEST_TEMPLATE: reorder checkboxes | [link](https://github.com/NixOS/nixpkgs/pull/572612) |
| 7 | `agentydragon/ducktape` | pr | 5 | 2026-09-16 | cluster: wire rugged's NPU-backed LLM into litellm | [link](https://github.com/agentydragon/ducktape/pull/7112) |
| 8 | `qgis/QGIS` | pr | 5 | 2026-10-07 | nix: update dev environment and instructions | [link](https://github.com/qgis/QGIS/pull/67696) |
| 9 | `NixOS/nixpkgs` | pr | 4 | 2026-10-12 | python3Packages.lerobot: 0.6.0 -> 0.6.1 | [link](https://github.com/NixOS/nixpkgs/pull/573305) |
| 10 | `Algorithmiq/monoprop` | pr | 4 | 2026-10-08 | chore!: 🐍 raise Python minimum to 3.12 | [link](https://github.com/Algorithmiq/monoprop/pull/395) |
| 11 | `nix-community/nh` | pr | 3 | 2026-09-30 | treewide: better activation, remote builds and generation  | [link](https://github.com/nix-community/nh/pull/812) |
| 12 | `NixOS/nixpkgs` | pr | 3 | 2026-10-08 | pi-coding-agent: 1.0.4 -> 1.1.0 | [link](https://github.com/NixOS/nixpkgs/pull/571605) |
| 13 | `agentydragon/ducktape` | pr | 3 | 2026-10-13 | Park the OpenClaw and devbox image CI workflows | [link](https://github.com/agentydragon/ducktape/pull/10233) |
| 14 | `Gentleman-Programming/gentle-shell` | issue | 2 | 2026-09-01 | gentle-ai install failed on nixos | [link](https://github.com/Gentleman-Programming/gentle-shell/issues/548) |
| 15 | `hellas-ai/nix-strix-halo` | pr | 2 | 2026-10-05 | chore(deps): bump nixpkgs in / | [link](https://github.com/hellas-ai/nix-strix-halo/pull/199) |
| 16 | `paperclipai/paperclip` | pr | 2 | 2026-08-05 | feat(nix): add native NixOS packaging | [link](https://github.com/paperclipai/paperclip/pull/10883) |
| 17 | `DeterminateSystems/nix-src` | pr | 2 | 2026-10-01 | Add skills for upstreaming and downstreaming commits / PRs | [link](https://github.com/DeterminateSystems/nix-src/pull/648) |
| 18 | `T0PSH31F/NFP` | pr | 2 | 2026-09-24 | feat(hermes): add missing mistral_api_key secret to sops a | [link](https://github.com/T0PSH31F/NFP/pull/10) |
| 19 | `fredsystems/nixos` | pr | 2 | 2026-10-13 | feat(skills): add shebang-env-discipline skill | [link](https://github.com/fredsystems/nixos/pull/2564) |
| 20 | `can1357/oh-my-pi` | pr | 2 | 2026-10-11 | fix(tui,coding-agent): enable kitty enhanced paste when th | [link](https://github.com/can1357/oh-my-pi/pull/15369) |
| 21 | `NixOS/nixpkgs` | pr | 2 | 2026-10-12 | whichllm: 0.5.19 -> 0.5.20 | [link](https://github.com/NixOS/nixpkgs/pull/573340) |
| 22 | `pop-os/cosmic-settings-daemon` | pr | 2 | 2026-03-20 | refactor: nix flake for build and dev | [link](https://github.com/pop-os/cosmic-settings-daemon/pull/138) |
| 23 | `NixOS/nixpkgs` | pr | 2 | 2026-10-12 | scummvm: 2026.3.0 -> 2026.4.0, modernize, init games | [link](https://github.com/NixOS/nixpkgs/pull/573278) |
| 24 | `mp-complete/nix-common` | pr | 2 | 2026-10-11 | Remove legacy Pi wrappers and add pi-coding-agent | [link](https://github.com/mp-complete/nix-common/pull/32) |
| 25 | `UnstoppableMango/github` | pr | 2 | 2026-09-21 | ci: use unmango/actions setup-nix | [link](https://github.com/UnstoppableMango/github/pull/433) |
| 26 | `logos-co/logos-basecamp` | pr | 2 | 2026-10-06 | Test/MCP UI module inspector search filters the table | [link](https://github.com/logos-co/logos-basecamp/pull/485) |
| 27 | `github/copilot-cli` | issue | 2 | 2026-05-02 | NixOS keychain support is broken | [link](https://github.com/github/copilot-cli/issues/3081) |
| 28 | `hoprnet/notification-service` | pr | 1 | 2026-10-05 | Bump nixpkgs from `4975466` to `c59305b` in the nix-flake- | [link](https://github.com/hoprnet/notification-service/pull/40) |
| 29 | `shikanime-labs/machines` | pr | 1 | 2026-10-09 | Add a headless browser CDP service for Hermes agents | [link](https://github.com/shikanime-labs/machines/pull/1480) |
| 30 | `fleetdm/fleet` | pr | 1 | 2026-09-30 | Document enrolling NixOS hosts | [link](https://github.com/fleetdm/fleet/pull/54421) |
| 31 | `NixOS/nixpkgs` | pr | 1 | 2026-09-09 | nixos/intune: enable daemon socket and agent timer | [link](https://github.com/NixOS/nixpkgs/pull/561698) |
| 32 | `UnstoppableMango/thecluster.lan` | pr | 1 | 2026-10-10 | fix(nix): build web only on builders that advertise x86-64 | [link](https://github.com/UnstoppableMango/thecluster.lan/pull/57) |
| 33 | `NixOS/nixpkgs` | pr | 1 | 2026-09-24 | nixos/t3code: init | [link](https://github.com/NixOS/nixpkgs/pull/566470) |
| 34 | `NixOS/nixpkgs` | issue | 1 | 2026-10-08 | nixos/polkit: service restarts unnecessarily | [link](https://github.com/NixOS/nixpkgs/issues/571880) |
| 35 | `bmazzarol-bunnings/bmazzarol-bunnings` | issue | 1 | 2026-10-10 | Set up Hermes + ROCm + Ollama + Qwen3.8-27B (unattended) | [link](https://github.com/bmazzarol-bunnings/bmazzarol-bunnings/issues/23) |
| 36 | `NixOS/nixpkgs` | pr | 1 | 2026-10-11 | firecrawl-cli: 1.24.6 -> 1.26.3 | [link](https://github.com/NixOS/nixpkgs/pull/572814) |
| 37 | `shikanime-labs/machines` | pr | 1 | 2026-10-12 | Add a local browser to automata's hermes-agent | [link](https://github.com/shikanime-labs/machines/pull/1520) |
| 38 | `curtisjm/nix` | pr | 1 | 2026-09-25 | Add personal headless NixOS development host | [link](https://github.com/curtisjm/nix/pull/3) |
| 39 | `AnimMouse/NixOS-ISO-Torrents` | pr | 1 | 2026-08-12 | Torrent RSS feed | [link](https://github.com/AnimMouse/NixOS-ISO-Torrents/pull/17) |
| 40 | `LivingTwice/lumen` | pr | 1 | 2026-10-07 | Linux support | [link](https://github.com/LivingTwice/lumen/pull/1) |
| 41 | `NixOS/nixpkgs` | pr | 1 | 2026-10-10 | treewide: remove obsolete x86_64-darwin code | [link](https://github.com/NixOS/nixpkgs/pull/572291) |
| 42 | `UnstoppableMango/travel` | pr | 1 | 2026-09-13 | chore(nix): use UnstoppableMango/nix-systems flake module | [link](https://github.com/UnstoppableMango/travel/pull/18) |
| 43 | `UnstoppableMango/travel` | pr | 1 | 2026-09-21 | ci: use unmango/actions setup-nix | [link](https://github.com/UnstoppableMango/travel/pull/23) |
| 44 | `formalverification/agda-native-air` | issue | 1 | 2026-10-10 | [M5-25] run-server.sh: skip nix develop when AGDA_MCP_BIN  | [link](https://github.com/formalverification/agda-native-air/issues/249) |
| 45 | `logos-co/logos-basecamp` | pr | 1 | 2026-10-06 | Test/MCP UI module inspector interface view lists methods/ | [link](https://github.com/logos-co/logos-basecamp/pull/488) |

### D. 匹配规模统计

| 来源 | 原始抓取 | 通过 AI×Nix 双关键词过滤 | 说明 |
|---|---|---|---|
| NixOS Discourse | 1,600 帖 | 469 帖 / 428 主题 | 23 个关键词 × 3 页 |
| Hacker News (Algolia) | 1,148 条 | 362 条 | 13 组查询，故事+评论 |
| GitHub issues/PRs/discussions | 553 | 148 | 3 组查询 |
| 搜索引擎（DDG/Bing/内置） | 4 | 0 | Reddit/X/Discord 受反爬限制，覆盖率低 |
| **合计** | **3305** | **979** | 全部为「AI × Nix」双命中 |

### E. 使用模式分布（按主题归类，可多属）

| 模式 | 命中贴文数 |
|---|---|
| (未分类) | 332 |
| A. 用 AI 写/改 NixOS 配置 | 301 |
| B. AI Agent 运维 NixOS 服务器 | 231 |
| D. 用 Nix 打包/运行 AI 工具 | 200 |
| G. 安全与信任边界 | 119 |
| E. AI 教学/答疑 NixOS | 98 |
| H. 本地推理 / GPU | 56 |
| C. MCP × NixOS | 46 |
| I. 反对/怀疑 AI 用于 NixOS | 32 |
| F. AI 生成配置的坑/翻车 | 16 |
| **合计命中** | **1431** |
