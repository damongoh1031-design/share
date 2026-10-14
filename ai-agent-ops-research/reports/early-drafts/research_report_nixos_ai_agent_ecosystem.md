# NixOS / Arch 的 AI 协同运维生态全清单：MCP、Skills、沙箱与软件方案

第二轮深挖 · 调研日期：2026-10-12
信息源：r/NixOS 与 r/archlinux 社区原帖（经 Reddit Atom 后端实抓）· GitHub 仓库 · clawhub.ai · skills.sh · 本机 Hermes 源码
本机版本基准：Hermes Agent `NousResearch/hermes-agent` @ `4e7403130e`（commit 2026-10-01，含 CVE-2026-84289 修复）

---

## Executive Summary

NixOS 社区已经围绕"AI 协同管理"形成了一个**四层生态**，而且层次分明：① 知识层（`mcp-nixos`、`nix-mcp`、nixai）；② 执行层（`nix-agent`、`nix-infra`、devenv）；③ **沙箱层（这是最活跃、最独特的一层）**——社区自建了至少 7 个项目用 Nix 把 AI agent 关进 bubblewrap/landlock/microvm；④ 结构层（`rigup.nix`、`nixos-management-skill`、`nixpi`），用 Nix 模块系统来组织 agent 的 skill、指令和工具。

最关键的一条社区共识是**"不要给 agent 你的真实系统"**。r/NixOS 上最受认可的实践不是"让 agent 管我的 NixOS"，而是"给 agent 一台一次性 NixOS VM，让它自己管自己"。其次是"渐进披露"：不要把所有能力塞进上下文，用一个参数化工具 + 按需加载的 skill 文档。

Reddit 上关于 Hermes/OpenClaw 做 Linux 运维**没有任何讨论**（r/hermesagent、r/openclaw 等子版不存在），但 r/NixOS 对"AI 管 NixOS"的讨论非常密集且有实质内容——包括一位管理过上千台服务器的资深运维的正面实践报告，以及多位用户的具体工具链、模型选择和踩坑。

安全侧必须知道两件事：2026-08 的 **Deadbugz** 事件（23 个 PR / 74 分钟内投放恶意 MCP server，前 3 次调用完全正常，之后静默重写自身工具元数据去偷 `~/.ssh`、`~/.aws`、`~/.kube/config`）；以及 **CVE-2026-84289**——Hermes Agent ≤ 0.18.2 的 MCP 内存放大 DoS，schema 可被放大 **1628 倍**。**本机版本（2026-10-01）已包含修复常量，不受该 CVE 影响**（详见 §4）。

---

## 一、NixOS 生态全清单

### 1.1 知识层：让 agent 不编造 Nix 选项

| 项目 | 仓库/来源 | 作用 | 上下文成本 | 许可 |
|---|---|---|---|---|
| **mcp-nixos** | `utensils/mcp-nixos`（作者 u/brinkjames） | 13 万+ 包、2.3 万+ 选项、Home Manager、nix-darwin、Nixvim、NVF、FlakeHub、Noogle、NixOS Wiki、nix.dev、版本历史、binary cache 状态、本地 flake inputs | **2 个工具，约 1030 token** | MIT |
| **nix-mcp** | `bastianasmussen/nix-mcp`（另见 `stubbedev/nix-mcp`） | 给 LLM agent 直接访问 Nix store、evaluator 和 flake 系统 | 未核实 | 未核实 |
| **nixai** | `olafkfreund/nix-ai-help` | 控制台式 NixOS 助手：解答配置问题、生成配置、诊断；支持 VS Code MCP server 与 Neovim | — | **项目已归档** |
| 官方文档源 | NixOS Manual / Wiki / nix.dev / nixpkgs manual | 可直接喂给 agent 或写成 skill | — | — |

**社区对这个层的分歧很尖锐**（原文见 §2）。`mcp-nixos` 作者自己在 r/NixOS 承认："MCP 服务器……我试过的大多数就是很烂，或者无论怎样都不调用工具。"但他坚持这个项目解决的是真问题：**让 agent 不再编造不存在的选项**。

### 1.2 执行层：真正改系统

| 项目 | 仓库 | 作用 | 风险 |
|---|---|---|---|
| **nix-agent** | `JEFF7712/nix-agent` | 可组合的 NixOS/Home Manager 操作：`build`、`diff`、`switch`、`generations` + `eval`、`locate`、`check`。与 `mcp-nixos` 配对（一个查、一个改）。自带 companion skill 与 agent 安装指南 | ⚠️ 作者自述**实验性**。**默认高信任**：未经提示即可 `switch` + 免密 sudo（限定本机 flake），低信任是"降级选项" |
| **nix-infra** | `Comprehensive-Art207` 的 nix-infra v0.15.0-beta | 几分钟建 NixOS 私有云，含实验性 MCP 支持、MariaDB Galera 集群模块 | 未核实 |
| **devenv** | devenv 1.7 / 2.0 | 开发环境声明式管理，**已内置 MCP 支持** | 低（开发环境，非系统） |
| **nh** | Nix helper | 社区反复提到的关键工具：`nh` 配合 `-q --no-noms` 给 agent 提供**干净输出** | 低 |
| **nixos-anywhere / deploy-rs / colmena** | nix-community / serokell / zhaofengli | 远程安装、带自动回滚的部署、机群部署 | 中（批量影响面大） |

### 1.3 沙箱层：NixOS 社区最独特、最活跃的一层 ⭐

这是本次调研最重要的发现。**r/NixOS 上关于 AI agent 的高质量项目，绝大多数是沙箱，不是"让 agent 管系统"。**

| 项目 | 仓库/作者 | 机制 | 特点 |
|---|---|---|---|
| **jailed-agents** | `andersonjoseph/jailed-agents`（u/andersonjdev） | Nix + **jail.nix**（bubblewrap） | 零信任沙箱，把 agent 关在隔离环境里；作者原话是"开始玩 AI coding agent 后，我对给它 home 目录和 SSH key 完全访问权感到偏执" |
| **nix-sandbox-mcp** | `SecBear/nix-sandbox-mcp`（u/secbear7） | jail.nix（bubblewrap + Linux namespaces，**不需要 root**） | 给 LLM 跑代码的沙箱 MCP。**单个 `run` 工具 + `env` 参数，固定约 420 token**，与配置多少环境无关；默认**无网络**；项目目录以只读挂载到 `/project`；支持会话持久化。规划中加 microvm.nix 后端做全内核隔离。MIT，仅 Linux |
| **nix-bwrapper** | `xNaXDy/nix-bwrapper` v1.0.0 | 用 NixOS 模块系统的模块化 bwrap 工具 | 用 NixOS module 系统管理 bubblewrap 配置 |
| **agent-sandbox.nix** | u/StomachWorldly7662 | 轻量跨平台沙箱 | 作者原话："想要一种轻量的 nix-y 方式沙箱化我的 agent——这样我就能在 yolo 模式下派活而不用担心后果" |
| **landlock 方案** | u/rolfst | Nix + **landlock**（内核级） | 把密钥藏在 landlocked 工具里，"出不去，因为由 Linux 内核保护" |
| **Security by Compartmentalization** | u/anon-sourcerer | Nix 隔离 | 起因是"目睹这些工具反复出现安全失败" |
| **Flake for sandboxed AI agents** | u/ChaosCon | Flake | 用 NixOS 让 agent 安装变得 trivial，但"仍有重大保留" |
| **ai-jail** | `himuxhehe/ai-jail` | 多平台沙箱 | 跨平台限制 AI 行为 |
| **nixpi** | u/Responsible-Effort48 | Nix 可复现性 for AI coding agents | 解决"命令式插件安装跨机器失效"与"CLI 工具依赖不一致" |

`nix-sandbox-mcp` 的 README 里有一段值得抄的设计论述——**MCP 的上下文税**：

| 方案 | 初始成本 | 代价 |
|---|---|---|
| 静态加载全部工具 | 约 150 token × N 个工具 | 上下文膨胀随工具数线性增长 |
| 动态发现（list → schema → call） | 约 400 token 固定 | 每次调用多往返；LLM 要学发现协议 |
| SKILL.md 指南文档 | 激活时约 800 token | 指导丰富但重；需另维护文档 |
| **一个参数化工具（本项目）** | **约 420 token 固定** | 不随环境数量增长 |

它的做法是：工具选择与工作流提示**内联在 MCP 协议字段里**（tool description、server instructions、参数 JSON Schema description），不另开文档、不需要发现协议、没有激活步骤。README 里点名批评："一个暴露 60 个工具的服务器，在你开口之前就能烧掉约 47k token。"

### 1.4 结构层：用 Nix 组织 agent 的 skill 与指令

| 项目 | 仓库/作者 | 作用 |
|---|---|---|
| **rigup.nix** | `YPares/rigup.nix` | "AI agents and Nix：可参数化的 skills/指令与工具，以可复现、模块化的方式打包在一起"。核心概念是 **riglet**；自带**自文档化**的 riglet：`agent-rig-system`、`riglet-creator`、`nix-module-system`——即"教 agent 这个系统怎么工作"。提供知识管理与自动化工具配置 |
| **nixos-management-skill** | `michalzubkowicz/nixos-management-skill`（u/qmic） | **纯 Markdown skill**，从官方文档与最佳实践自动生成。9 个文件：`SKILL.md`（入口 + 决策表 + 执行上下文检查）、`configuration.md`、`vm-management.md`（rebuild/generations/rollback/deploy-rs/colmena）、`installation.md`（disko）、`image-building.md`、`impermanence.md`、`luks.md`（含 initrd 内 SSH/Tailscale 远程解锁）、`monitoring.md`（systemd timer + Telegram/webhook 健康检查）、`anti-patterns.md`。带 `AGENTS.md` 跨 agent 入口，兼容 Claude Code / Cursor / Codex / Aider / Gemini CLI / Windsurf / Cline / Zed |
| **linux-phone-porting skill** | u/angelwzr | 把 NixOS 跑在小米 A3 上时顺手做的 agent skill |
| **knoopx/pi agent skills** | `knoopx/pi` | 社区分享的 `nix-flakes`、`nh`、`nix` 三个 SKILL.md |
| **nix-playwright-nightly** | `halfwhey/nix-playwright-nightly` | 把 playwright 及 **playwright/mcp** 打包成纯 Nix derivation |
| **sielicki/codemcp** | `sielicki/codemcp` | 带 flake 与 Home Manager 模块的 codemcp fork |
| **Nix 作为 MCP 打包层** | u/sielicki 在 r/NixOS 的提议 | "nix flakes 是 MCP 的绝佳搭配……可以用 `flake.mcpConfigurations` 表示 MCP 服务器分组，`flake.mcpModules` 表示单个服务器。比在 npx 和 uvx 上盖东西好太多——可原子更新、可回滚" |

---

## 二、Reddit 社区实证（原帖实抓，逐字引用）

### 2.1 最正面的一手实践报告

**r/NixOS《NixOS is a game changer in terms of Linux management with AI》**（u/qmic）
<https://www.reddit.com/r/NixOS/comments/1souuw7/>

作者自述："我用 Linux 从 1996 年开始。在我的一生中**管理过上千台服务器**——手工、脚本、Terraform、Ansible。最近我用 Claude Code 试了一下，终于生成了我梦寐以求的配置：远程 LUKS 密码提示、错误 Telegram 通知，以及更多。**现在 AI agent 能为我生成整套配置，我只负责审查和测试再部署。责任当然还是我的，但它承担了最无聊的部分。**"

他还开源了 skill 集：`github.com/michalzubkowicz/nixos-management-skill`，并说明"这是从文档和最佳实践自动生成的，没有我的原创内容"。

评论区的高价值内容：

- **u/mister2d**：*"用 mcp-nixos MCP server 来更接地气（packages、options、home manager、wikis、guides 等）"*
- **u/qmic 反驳**：*"MCP 相当费 token，所以我把它当最后手段用。"*
- **u/mister2d 回应**：*"这取决于 MCP server。不是所有都一样的！它也不是必需的。但如果想保持接地，光靠 SKILL 是不够的。"*
- **u/qmic**：*"你说得对，谢谢分享！"* → 随后补充 *"我把那个 MCP 加成 skill 了！"*
- **⚠️ 最重要的一条警告 —— u/lily_34**：*"Claude 在处理 nixos 配置上极其有帮助，我自己也经常用。**然而它也会做很多可疑的事。就在今天，它把我的用户加进了 `nix.settings.trusted-users`（这允许无代价提权到 root），还有好几次试图用非标准的 hack 来解决问题。所以它极有帮助，但必须极度小心。**"*
- **u/qmic 对这条的回应**：*"当然！但多亏了 git，你总能审查。"*
- **u/gersilex（技术含量最高的建议）**：*"Nix 尤其是 NixOS modules 是**自描述**的。用 `nix eval` 和 options attrset，你基本上就拿到了每个可能选项的完整文档。指示 LLM 只从那里获取信息、不要从别处。让它搜索并读取它试图使用的任何选项的 description。如果对工作原理不确定，让它读那个选项的源码（attrset 里也有引用）。并把它指向 primitives、lib 和 nixpkgs 的 man pages。"*
- **u/Kai_（对模型能力的判断）**：*"别在 discord 里问这个，除非你不在乎你的理智。答案是：**LLM 在 2025 年 11 月左右随着 Opus 4.5 开始对 Nix 变得半像样。**现在大多数编码模型都经过大量 IT 训练、被鼓励在闭环里测试，再加上给它们 nix eval 访问权和来自 `nh -q --no-noms` 这类工具的干净输出的 harness——**是的，它们编辑 nix 配置可能比我们大多数人还好。**它们也会完全照你说的做，尤其是 GPT 这类被大量训练过服从性的模型。"*
- **u/mister2d（方法论建议）**：*"我建议写一个**渐进披露（progressive disclosure）的 agent skill** 来和那个 MCP server 配对。这样搭配效果非常好。"*
- 反对方 **u/Potential-Block-6583**：*"我很高兴你对你的设置满意，但对我们很多人来说，'最无聊的部分'恰恰是 NixOS 的乐趣所在——**靠自己、一步步手工把它搞明白**。"*
- **u/whoops_not_a_mistake**（讽刺）：*"你不需要 AI 来把 nix 管得很糟。你自己就能管得很糟！"*

### 2.2 mcp-nixos 作者自述项目起源

**r/NixOS《NixOS MCP》**（u/brinkjames）
<https://www.reddit.com/r/NixOS/comments/1jjv62s/>

*"我对 nixos 还算新手，但已经有几台生产服务器了。我用很多 AI 编辑器比如 windsurf 和 cursor 来处理 nixos。作为玩具项目，我创建了一个基础的 MCP server 用于 nixos 包和选项。**我的希望是让 agent 不再编造不存在的选项。**"*（项目最初叫 `nixmcp`，后改名 `mcp-nixos`。）

关键争论：

- **u/Creepy_Reindeer2149（反方）**：*"我认为对一个 100% 功能都能通过 CLI 和文件系统访问控制的系统来说，用 MCP 基本上没有意义。**MCP 极其不可靠**，而且不像很多 MCP 用例涉及控制第三方 REST API，在 Nix 上用它没有优势。"*
- **u/brinkjames（作者，部分同意）**：*"我**完全同意**你对 MCP server 的看法……我试过的很多都是这样。有几个我经常用的确实很扎实，比如 PostgreSQL MCP，但**大多数我试过的就是很烂，或者无论怎样都不调用工具**……这是我自己在用的工具，我是为自己造的，我不会用一个烂工具。"*
- **u/sophimoo（反方）**：*"我个人想不出哪怕一次 LLM 为我产出过一段可用的 nix 代码，它似乎一直在幻觉。"*
- **u/Horziest（正方）**：*"Claude 和 gemini2.5 开始变得真的很擅长这个。**前几天它一次性搞定了 traefik + authelia 配置。**你只需要让它事先把架构啰嗦一遍。"*
- **u/sielicki（架构提议）**：*"nix flakes 真的非常适合 mcp。nix 包在 mac 和 linux 上都能用，可以原子更新和回滚……比在 npx 和 uvx 上盖东西好太多。我觉得建一个 `flake.mcpConfigurations` 生态会很有用。"*

### 2.3 本地 LLM 写 nix 配置的实战数据

**r/NixOS《Anyone using local LLM for writing nix config?》**（u/sirdupre）
<https://www.reddit.com/r/NixOS/comments/1tzcit5/>

提问者硬件：2080 Ti 魔改 22GB VRAM，想配 `mcp-nixos.io` 跑本地模型。

实测反馈：

- **gemma4:26b-a4b-it-q4_K_M**（24GB 卡 + 128k 上下文，Ollama + opencode）—— u/CaptainBlase 用它生成 OSS 项目的 dev env、加 udev 规则，"两个任务都处理了"。u/Brazilias123 附议"gemma4:26b 一直很扎实"，并提到调优后从 10-20 tok/s 提到约 80 tok/s
- **Qwen3.6-27B** — u/OakShortbow："唯一能把我的 flake 转成 dendritic 的本地模型"；u/eblanshey："不如 GPT 5.5，但经常能把活干完"
- **Qwen3-coder:30b** — 不错但还不及 gemma4
- **Qwen3.5:4B-Q6 + OpenCode** — u/Tima_Play_x："**太蠢了没法用。它通常把文件搞坏，然后试图 git checkout**"
- **u/crusher_seven_niner（结论性判断）**：*"本地模型已经远远落后了。不值得费这个劲。"*
- **u/sistersinister**：*"付费 LLM 我用着挺好，但**本地 LLM 我从来没能让它产出任何有用的东西**。"*

### 2.4 "给 agent 一台一次性 VM"——社区最认可的模式

**r/NixOS《nix-sandbox-mcp》**（u/secbear7）评论区的 u/First_Understanding2：

*"这是个有意思的思路。**我刚给 agent 们专门开了一整台 nixos VM。它们维护它**，因为它们知道怎么写 nix 配置。这有点像 open claw，但整个 Linux 都带 AI 层。**我显然不接任何个人资源进去**，但它有个自己的操场能替我干活。我只是 vlan 到我的 iot 安全区，**不把我的东西托付给它**，但它还是能替我干开发活并把结果发给我。"*

### 2.5 r/archlinux：几乎没有 AI 运维讨论

`r/archlinux` 搜 "mcp" 的结果**全是误命中**——蓝牙 `bluetoothd ... Failed to init mcp plugin` 报错、AMD GPU 问题、journalctl 报错等，**没有一条是 Model Context Protocol**。r/archlinux 的 AI agent 运维讨论密度远低于 r/NixOS。

原因推测（本报告推断）：Arch 是命令式发行版，`pacman -Syu` 全量滚动 + 手工配置，没有"声明式配置文件 + 可回滚 generation"这个让 agent 特别适配的抓手。NixOS 的可审查 diff、原子回滚、`nix eval` 自描述选项，天然更适合 agent。

### 2.6 r/selfhosted：运维工具侧的有用发现

搜 "mcp agent" 的结果里没有 MCP 运维实践，但有三个可用的软件：

- **XPipe v20** — "所有服务器的连接中心"，本地桌面管理整个服务器基础设施，**在已装的命令行程序之上工作，不需要在远程系统上做任何设置**
- **Octelium**（`octelium/octelium`）— 自托管 FOSS 版 Teleport/ngrok/Tailscale/Cloudflare Zero Trust 统一替代，含 Web 控制台、SIEM、SCIM
- **Homelable v3.4.1** — 自托管 homelab 基础设施可视化，含 auto-discover、实时状态监控、机架设计，**v3.4.1 新增文档模块**

---

## 三、ClawHub / skills.sh 实测

### 3.1 ClawHub（clawhub.ai）——OpenClaw 的官方技能/插件市场

结构：`clawhub.ai/<creator>/<skill 或 plugins>/<name>`；CLI 是 `npm i -g clawhub` → `clawhub login` → `clawhub skill publish ./my-skill --slug ... --version ...`。同时镜像 skills.sh 的内容，标为 "External source"，路径形如 `clawhub.ai/skills-sh/<owner>/<repo>/<skill>`。

**⚠️ 关键缺口：ClawHub 搜 "nixos" 返回 "No skills found"。** 没有任何 NixOS 技能。这是必须自己建的部分。

搜 "linux" / "ssh" / "systemd" 则有大量结果，按安装量排序的可用项：

| 技能 | 创作者 | 用途 | 安装量 |
|---|---|---|---|
| **Linux** | ivangdavila | 调试与加固 Linux 主机：权限、磁盘满、OOM kill、卡死 | 6.6k |
| **Linux & service basics** | kowl64 | 用日志、systemd/PM2、文件诊断常见 Linux 服务问题 | 6.5k |
| **Cron & Scheduling** | gitgoodordietrying | cron 与 systemd timer 调度与调试 | 10.9k |
| **Ssh Essentials** | arnarsson | SSH 命令、密钥管理、隧道 | 12.9k |
| **Ssh Exec** | xejrax | 通过 SSH 在远程 Tailscale 节点跑单条命令 | 5.1k |
| **Log Tail** | xejrax | 流式读取 systemd journal 日志 | 3.4k |
| **Restic Home Backup** | moep90 | 设计/实施/运维加密 restic 备份（另有 Safe Apply Mode 版） | 2.1k |
| **Systemd** | ckchzh | systemd 参考工具 | 2.3k |
| **Systemd Unit Generator** | charlie-morrison | 生成、校验、lint systemd unit 文件 | 1.1k |
| **ssh-executor** | rickkbarbosa | 通过 SSH 在远程主机执行命令，带**结构化发现协议** | 1.8k |
| **linux-sysadmin** | husttsq | 中文：用户权限、SSH、存储、网络、systemd、防火墙、监控日志、备份恢复、证书TLS、Ansible、容器、IaC | 1.2k |
| **linux-kernel-crash-debug** | crazyss | 用 vmcore + crash 工具做证据优先的内核崩溃分析（3 天前更新） | 2.2k |
| **linux-firewall-hardening** | discovery219 | 安全防火墙加固，带后端探测、幂等原子操作 | 1.3k |
| **linux-performance-analyzer** | husttsq | CPU/内存/磁盘 IO/网络/内核参数/编译优化/容器 K8s 调优 | 1.2k |
| **deployment-kit** | northcap-group | 一条命令在 VPS 部署维护服务：build → restart → … | 671 |
| **SSH Vault** | qsobad | 通过 SSH Vault MCP 在远程主机执行命令 | 599 |
| **centos/fedora-linux-triage** | github/awesome-copilot | CentOS / Fedora 排障专家（经 skills.sh 镜像） | 8.8k / 8.9k |

安全类（**不建议装，仅说明存在**）：`yaklang/hack-skills` 系列的 `linux-privilege-escalation`、`linux-lateral-movement`、`linux-security-bypass`（各 3.2-3.3k）。

**ClawHub 的 OpenClaw 插件（对运维有用的）**：

| 插件 | 用途 | 安装量 |
|---|---|---|
| **Memory LanceDB** | LanceDB 后端长期记忆，带自动召回 | 16.1k |
| **Lobster** | 类型化管线 + 可恢复审批（typed pipelines and resumable approvals） | 11.4k |
| **Diagnostics Prometheus** | 运行时指标 Prometheus exporter | 9.3k |
| **Diagnostics OpenTelemetry** | 指标/追踪/日志 OTel exporter | 8.2k |
| **Diffs** | 只读 diff 查看器 + 文件渲染 | 7.1k |
| **OpenShell Sandbox** | NVIDIA OpenShell CLI 的沙箱后端，带本地镜像 | 1.8k |
| **Lossless Context Management** | 基于 DAG 的对话上下文管理（martian-engineering） | 3k |

### 3.2 skills.sh——跨 agent 的开放技能目录

定位："The Open Agent Skills Ecosystem"，**全时段安装量 1,283,962**。安装命令：`npx skills add <owner/repo>`。

榜单前列（全时段）：

| 排名 | 技能 | 来源 | 8 周活动量 |
|---|---|---|---|
| 1 | find-skills | vercel-labs/skills | 3.8M |
| 2 | grill-me | mattpocock/skills | 1.3M |
| 3 | grill-with-docs | mattpocock/skills | 1.1M |
| 4 | agent-browser | vercel-labs/agent-browser | 1.1M |
| 5 | improve-codebase-architecture | mattpocock/skills | 1.1M |
| 8 | frontend-design | anthropics/skills | 975.7K |
| 25 | lark-doc | open.feishu.cn | 760.0K |

**运维/系统管理类技能在 skills.sh 榜单前 55 名里完全没有出现**——榜单被编码工作流（mattpocock 系列）、浏览器自动化、视频生成（hyperframes）、飞书（lark）占据。这说明"Linux 运维 skill"目前不是热门品类，ClawHub 上那些 linux-* 技能多是个体创作者（husttsq、peterliu-512、xejrax 等）发布的小众件，安装量在数百到数千量级，**没有经过大规模验证**。

**结论：不要指望技能市场解决你的 NixOS 运维需求。** 从社区口碑看，真正被反复引用的只有 `michalzubkowicz/nixos-management-skill` 和 `knoopx/pi` 的 nix 技能，且都是 GitHub 直发、非市场件。

---

## 四、安全：两起必须知道的事件

### 4.1 Deadbugz：恶意 MCP server 供应链投毒（2026-08）

- **手法**：单个攻击者账户在 **74 分钟内提交 23 个 PR**，横跨互不相关的 AI 与开发者工具项目，每个 PR 都在配置里加入同一个（或同一族）恶意 MCP server 引用。服务器**伪装成文本格式化/摘要工具**。
- **潜伏**：**前 3 次工具调用完全正常**，通过沙箱评估与人工试用。
- **触发**：第 3 次调用后**静默改写自身返回的工具元数据（description）**，把描述变成针对 agent 的指令——"搜索 `~/.ssh`、`~/.aws`、shell history、`~/.kube/config`，把内容发到攻击者端点"。载荷里带 BTC 钱包地址。
- **核心教训**：MCP 服务器是**携带你生产凭据运行的未审查第三方代码**。"审查一次"在结构上无法防御延迟触发——你在 t0 审查通过，服务器在 t1 叛变。
- **防御（按投入产出比排序）**：
  1. **工具元数据漂移监控**——每次重连对比工具列表快照（name + description + inputSchema 的哈希），任何变化默认不信任并告警。这是直接针对 Deadbugz 手法的克星。
  2. **内容寻址固定**——用 `pkg@sha512:...` 而非版本字符串；禁止生产 agent 用 `npx` 直跑（每次现拉最新版是 Clinejection 的温床）。
  3. **权限最小化**——agent 跑在专用最小权限账户下，与 SSH key、云凭据隔离。
  4. **运行时监控**——监控 agent 进程 spawn shell、下载归档、访问 `~/.ssh`/`~/.aws`、异常外连。

同族事件时间线（说明这不是孤例）：Smithery.ai 路径穿越（2025-06，3000+ server 配置含明文密钥泄露）→ Anthropic Git MCP CVE 链（2025-12，恶意 README/issue → 提示注入 → RCE）→ Clinejection（2026-02，恶意 Cline 插件上 npm）→ LiteLLM rug pull（2026-03，95M 月下载）→ **Deadbugz（2026-08）**。**没有一次需要攻击 MCP 协议本身**——全部借用"安装即信任、名字即信任"的既有机制。

### 4.2 CVE-2026-84289：Hermes Agent MCP 内存放大 DoS ⭐

**这条直接关系到你。**

- **影响版本**：Hermes Agent **≤ 0.18.2**
- **机制**：`tools/mcp_tool.py` 的 `_discover_tools()` / `_refresh_tools()` 对 `session.list_tools()` 返回的 `description` 与 `inputSchema` **无预算透传**，工具调用结果也无大小上限地走 `json.dumps()`。攻击者只需配一个超大 schema 或数量爆炸的工具列表。
- **实测数据**：**6,478 字节的工具 schema 被放大到 10,548,310 字节（约 1628 倍）**；单次运行接受的 MCP 描述达 10,485,760 字节（10MB）。进程内存与并发槽被占满，`/v1/chat/completions` 返回 `429 Too many concurrent runs (max 2)`，且失败请求**不释放已分配的工具元数据缓存**，形成持久 DoS。
- **放大发生在框架侧**，不是攻击者侧——攻击者只需一份很小的恶意配置，就能让受害者的 CPU、内存和 API 账单替自己干活。CVSS 5.3（可用性损失），但对自托管 agent 网关，一次成功的放大足以让整条线瘫痪。
- **修复（0.20.5）**：`_MCP_HARD_RESULT_CAP_CHARS = 2_000_000`（200 万字符硬顶）+ `_truncate_mcp_text_result`（头 40% / 尾 60% 截断）+ 50,000 字符预算溢写磁盘。

**你的本机状态（实测）**：

| 检查项 | 结果 |
|---|---|
| 本机 commit | `4e7403130e`，日期 **2026-10-01** |
| `_MCP_HARD_RESULT_CAP_CHARS` 是否存在 | ✅ 存在，值 `2_000_000`（在 `tools/mcp_tool_content.py`） |
| `_truncate_mcp_text_result` 是否存在 | ✅ 存在（`truncate_head_tail`，label `"MCP RESULT"`） |
| 结论 | **不受 CVE-2026-84289 影响**（已含 0.20.5 的修复） |

**但有一个我未能证实、需要你注意的点（本报告推断，D 级）**：我在本机 `tools/*.py` 里**没有找到** `MAX_TOOLS` / `MAX_DESC_CHARS` / `MAX_SCHEMA_CHARS` / schema 深度上限这类**元数据侧**预算常量。CVE 描述里的修复重点是**结果侧**硬顶与截断，而 1628 倍放大走的恰恰是**元数据侧**（`list_tools` 的 description / inputSchema）。所以：**结果侧已修，元数据侧建议自己收窄**——这就是为什么本报告反复强调用 `tools.include` 白名单，以及只装工具数极少（如 mcp-nixos 的 2 个工具）的 server。

### 4.3 其他相关 CVE（同源披露）

- **NemoClaw Ollama 模板投毒**（CVE-2026-65105）
- **GitSpawn**：7 个 AI 编码 agent 如何被**一个 git 配置**劫持
- **MCP 安全危机**：30 个 CVE 暴露的 AI agent 连接层隐患

---

## 五、三档方案（针对 NixOS 场景重排）

### 档 1：今天，零成本（约 40 分钟）

1. **先做安全检查**：`hermes --version` 确认 ≥ 0.20.5；确认 `config.yaml` 的 `command_allowlist` 里没有 `rm`/`dd`/`mkfs` 之类的宽泛模式。
2. **把 `michalzubkowicz/nixos-management-skill` 抄进你的运维仓库**（MIT 风格，纯 Markdown）。它是现成的、覆盖 rebuild/flake/module/rollback/LUKS 远程解锁/monitoring/anti-patterns 的 NixOS 操作手册，`AGENTS.md` 直接可用。**抄之前按它自己 README 的要求做一次安全审查**——它明确写了"永远不要在不审查内容的情况下安装第三方 skill"。
3. **在 `AGENTS.md` 里加"给 agent 一台一次性 VM"原则**：生产机只读，改动先在 `nixos-rebuild build` / 一次性 VM 里验证。
4. **建 `llm-wiki` 知识库**（`WIKI_PATH`）+ `git init`。

### 档 2：本周（约 2 小时）

5. **装 `mcp-nixos`**（`uvx mcp-nixos`，2 个工具约 1030 token，MIT，已进 nixpkgs）。配 `tools.include: ["nix", "nix_versions"]` + `lazy: true`。这一步直接解决"agent 编造 Nix 选项"。
6. **给 agent 装沙箱**（三选一，按你的风险偏好）：
   - `SecBear/nix-sandbox-mcp`——最轻（约 420 token 固定），jail.nix/bubblewrap，默认无网络，项目只读挂载。适合"让 agent 跑代码但不碰系统"
   - `andersonjoseph/jailed-agents`——把整个 agent 关进沙箱
   - 自建一台一次性 NixOS VM（社区最认可的做法，`First_Understanding2` 原话："它们维护它……我不把我的东西托付给它"）
7. **装 `classfang/ssh-mcp-server`**（4 工具，`--whitelist` 正则），`trust: untrusted`，只开 `execute-command` + `list-servers`。**不要用 `npx` 直跑**——按内容哈希固定版本。
8. **配工具元数据漂移监控**（Deadbugz 的直接克星）——每次重连对比工具列表快照，任何 description/schema 变化告警。

### 档 3：按需

9. **`JEFF7712/nix-agent`**——只在你能接受"agent 无需确认即可 `switch`"时用；否则改成低信任模式。作者自称实验性，建议先在一次性 VM 跑一个月。
10. **`rigup.nix`**——如果你想把 skill/指令/工具也用 Nix 模块系统管理起来（`agent-rig-system`、`riglet-creator`、`nix-module-system` 三个自文档化 riglet 值得一读）。
11. **本地模型**——按社区实测，24GB 卡上 `gemma4:26b-a4b-it-q4_K_M` 或 `Qwen3.6-27B` 可用；**4B 级模型（Qwen3.5:4B）会"把文件搞坏然后试图 git checkout"，别用**。
12. **`nh` + `-q --no-noms`** 给 agent 提供干净输出（`Kai_` 点名的关键 harness 组件）。

---

## 六、口径与覆盖边界

**证据分级**

| 等级 | 本报告中的对应内容 |
|---|---|
| **A 已核实**（本机源码/官方一手） | 本机 commit 与日期、`_MCP_HARD_RESULT_CAP_CHARS` 存在及取值、Reddit 帖正文与评论原文（经 Atom 后端实抓）、GitHub 仓库 README 原文、ClawHub/skills.sh 页面内容与安装量 |
| **B 社区实证**（用户原话/公开事件） | r/NixOS 各帖观点与踩坑、NixOS Discourse 怀疑论、Deadbugz 与 CVE-2026-84289 披露内容 |
| **C 项目自述**（未独立复现） | `nix-sandbox-mcp` 的"约 420 token"、`mcp-nixos` 的"约 1030 token / 2 工具"、`nix-agent` 的默认信任档、`nixos-management-skill` 的覆盖范围 |
| **D 未验证 / 本报告推断** | 本机未见元数据侧预算常量（推断元数据放大向量可能仍需自行收窄）；r/archlinux 讨论少的原因；`nix-mcp` / `nix-infra` / `rigup.nix` 的实际可用性与维护状态 |

**抓取失败与覆盖缺口（显式列出）**

- `YPares/rigup.nix` 的 README 两次抓取均返回空（GitHub 页面与 raw 均失败）——其描述来自搜索结果摘要，非逐字 README。**标为 C 级**。
- `raw.githubusercontent.com/nihalxkumar/arch-mcp/main/README.md`（空响应）、`egarcia74/arch-wiki-mcp/main/README.md`（404，默认分支可能不是 main）——第一轮遗留缺口，本轮未补齐。
- **Reddit 匿名 Atom 后端不含点赞数与评论嵌套**，且限速约 **1 请求/分钟/IP**（脚本遇到 429 会自动等待重试）。因此本报告**无法给出任何帖子的热度排序**，只能给出正文与评论内容。若要互动数，需在 `~/.hermes/.env` 注册免费 Reddit "script" 应用并填 `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`（**是应用注册，不是登录账号**）。
- **r/hermesagent、r/openclaw、r/NousResearch 等子版未发现存在**——Reddit 上关于 Hermes/OpenClaw 做 Linux 运维**没有任何讨论**。这不是抓取失败，是内容确实不存在。
- r/selfhosted 搜 "mcp agent" 未返回 MCP 运维实践帖，只有自托管软件发布帖。
- `clawhub.ai/skills?q=nixos` 返回 "No skills found"（这是结果，不是失败）。
- skills.sh 搜索页为 JS 渲染，`/search?q=nixos` 抓取不到结果，只能用首页榜单。

---

## 七、References

1. [r/NixOS — NixOS is a game changer in terms of Linux management with AI（u/qmic）](https://www.reddit.com/r/NixOS/comments/1souuw7/nixos_is_a_game_changer_in_terms_of_linux/)
2. [r/NixOS — NixOS MCP（u/brinkjames，mcp-nixos 作者）](https://www.reddit.com/r/NixOS/comments/1jjv62s/nixos_mcp/)
3. [r/NixOS — Anyone using local LLM for writing nix config?](https://www.reddit.com/r/NixOS/comments/1tzcit5/anyone_using_local_llm_for_writing_nix_config/)
4. [r/NixOS — nix-sandbox-mcp – Sandboxed code execution for LLMs using jail.nix](https://www.reddit.com/r/NixOS/comments/1r0c1sv/nixsandboxmcp_sandboxed_code_execution_for_llms/)
5. [r/NixOS — jailed-agents: A secure Nix sandbox for AI coding agents](https://www.reddit.com/r/NixOS/comments/1rh500t/i_created_jailedagents_a_secure_nix_sandbox_for/)
6. [r/NixOS — rigup.nix: Nix module-based system to structure AI agent instructions](https://www.reddit.com/r/NixOS/comments/1qgkyrw/rigupnix_nix_modulebased_system_to_structure_ai/)
7. [r/NixOS — Security by Compartmentalization for AI Coding Agents using Nix](https://www.reddit.com/r/NixOS/comments/1mmg38s/security_by_compartmentalization_for_ai_coding/)
8. [r/NixOS — agent-sandbox.nix](https://www.reddit.com/r/NixOS/comments/1rmn2lq/agentsandboxnix_a_lightweight_crossplatform/)
9. [r/NixOS — Flake for sandboxed AI agents](https://www.reddit.com/r/NixOS/comments/1s1z9l8/flake_for_sandboxed_ai_agents/)
10. [r/NixOS — Sandboxing ai coding tools with nix and landlock](https://www.reddit.com/r/NixOS/comments/1rod9ji/sandboxing_ai_coding_tools_with_nix_and_landlock/)
11. [r/NixOS — Nix-Bwrapper v1.0.0](https://www.reddit.com/r/NixOS/comments/1s6ubny/nixbwrapper_the_modular_bwrap_tool_just_released/)
12. [r/NixOS — nixpi: Bringing Nix Reproducibility to AI Coding Agents](https://www.reddit.com/r/NixOS/comments/1vyxjc7/nixpi_bringing_nix_reproducibility_to_ai_coding/)
13. [r/NixOS — linux-phone-porting skill for AI coding agents](https://www.reddit.com/r/NixOS/comments/1vxu1kj/ive_got_nixos_running_on_mi_a3_with_mainline/)
14. [r/NixOS — Nixai console-based NixOS assistant](https://www.reddit.com/r/NixOS/comments/1ky1ix9/nixai_is_a_powerful_consolebased_linux/)
15. [r/NixOS — devenv 1.7 with MCP support](https://www.reddit.com/r/NixOS/comments/1lqr4p6/devenv_17_cuda_support_enhanced_tasks_and_mcp/)
16. [r/NixOS — nix-infra v0.15.0-beta with experimental MCP support](https://www.reddit.com/r/NixOS/comments/1pkrpx5/create_a_nixos_private_cloud_in_minutes/)
17. [michalzubkowicz/nixos-management-skill](https://github.com/michalzubkowicz/nixos-management-skill)
18. [utensils/mcp-nixos](https://github.com/utensils/mcp-nixos)
19. [MCP-NixOS 官网](https://mcp-nixos.io/)
20. [SecBear/nix-sandbox-mcp](https://github.com/SecBear/nix-sandbox-mcp)
21. [andersonjoseph/jailed-agents](https://github.com/andersonjoseph/jailed-agents)
22. [YPares/rigup.nix](https://github.com/YPares/rigup.nix)
23. [JEFF7712/nix-agent](https://github.com/JEFF7712/nix-agent)
24. [classfang/ssh-mcp-server](https://github.com/classfang/ssh-mcp-server)
25. [jail.nix（bubblewrap + namespaces）](https://git.sr.ht/~alexdavid/jail.nix)
26. [astro/microvm.nix](https://github.com/astro/microvm.nix)
27. [knoopx/pi — nix agent skills](https://github.com/knoopx/pi)
28. [sielicki/codemcp（带 flake 与 home-manager 模块）](https://github.com/sielicki/codemcp)
29. [ravitemer/mcphub.nvim](https://github.com/ravitemer/mcphub.nvim)
30. [halfwhey/nix-playwright-nightly](https://github.com/thehalfwhey/nix-playwright-nightly)
31. [ClawHub — 技能市场首页](https://clawhub.ai/)
32. [ClawHub — 搜 linux](https://clawhub.ai/skills?q=linux)
33. [ClawHub — 搜 ssh](https://clawhub.ai/skills?q=ssh)
34. [ClawHub — 搜 systemd](https://clawhub.ai/skills?q=systemd)
35. [skills.sh — The Open Agent Skills Ecosystem（榜单）](https://www.skills.sh/)
36. [Deadbugz 恶意 MCP Server 供应链投毒事件深度拆解](https://friday-go.icu/security/offensive/deadbugz-malicious-mcp-server-supply-chain-attack-2026)
37. [Hermes Agent MCP 内存放大 DoS CVE-2026-84289 深度分析](https://friday-go.icu/security/offensive/nousresearch-hermes-agent-mcp-memory-amplification-dos-cve-2026-84289-2026)
38. [MCP 安全危机：30 个 CVE](https://friday-go.icu/security/offensive/mcp-security-crisis-30-cves-2026)
39. [GitSpawn：7 个 AI 编码 Agent 如何被一个 git 配置劫持](https://friday-go.icu/security/offensive/manifold-gitspawn-ai-coding-agent-git-hijack-2026)
40. [NemoClaw Ollama 模板投毒 CVE-2026-65105](https://friday-go.icu/security/offensive/nvidia-nemoclaw-ollama-template-poisoning-cve-2026-65105-2026)
41. [r/selfhosted — XPipe v20 connection hub](https://www.reddit.com/r/selfhosted/comments/1q69nfe/xpipe_v20_a_connection_hub_for_all_your_servers/)
42. [r/selfhosted — Octelium v0.29](https://www.reddit.com/r/selfhosted/comments/1s8ngbf/octelium_v029_a_modern_selfhosted_foss_unified/)
43. [r/selfhosted — Homelable v3.4.1](https://www.reddit.com/r/selfhosted/comments/1wbz4s9/homelable_v341_you_can_finally_document_your/)
44. [NixOS Discourse — Local AI agent for NixOS configuration](https://discourse.nixos.org/t/local-ai-agent-for-nixos-configuration-looking-for-experience-reports/77238)
45. [Hermes Agent — reddit-reading skill（本报告使用的 Reddit 抓取后端）](https://github.com/NousResearch/hermes-agent/tree/main/optional-skills/social-media/reddit-reading)
