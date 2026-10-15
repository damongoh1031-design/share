---
type: Checklist
---

# 哪个发行版有「AI 协同管理」的实践？—— 全网扫描报告

**调研日期**：2026-10-12
**调研范围**：发行版官方投入 · GitHub 仓库实测（star / 活跃度经 API 独立核实）· 社区真实实践长文
**方法**：3 个并行子代理（官方集成 / GitHub 项目 / 社区实践）+ 主调研员对全部关键仓库做 GitHub REST API 独立核实（本轮共核实 40+ 仓库）
**核实口径**：GitHub 数据取自 `api.github.com/repos/<owner>/<repo>` 与 `/search/repositories`，抓取时间 2026-10-12

---

## 0. 一句话结论

**没有一个发行版同时赢下三个维度。答案取决于你要的是哪一种「AI 协同」：**

| 你要的是 | 选它 | 硬证据 |
|---|---|---|
| **厂商官方工程化、有 SLA、能进企业** | **RHEL / Fedora** | Red Hat 有**专门的 GitHub 组织 `rhel-lightspeed`**，发布 6+ 个 MCP server；`docs.redhat.com` 有官方安装文档；Red Hat Summit 有动手实验 |
| **社区生态最厚、真实运维实践最多、链路最完整（查→改→回滚）** | **NixOS** | 唯一同时具备「MCP 查询 853★ + MCP 操作 + 回滚 skill + 4 个 AI skills 仓库 + 大量中文真实运维长文」的发行版 |
| **产品化 MCP 覆盖最广、已写进商业产品** | **openSUSE / SUSE** | Multi-Linux Manager 5.2 原生 MCP、Observability MCP、**openQA 原生 MCP**、SUSECON 2026 宣布全产品线 MCP |
| **AI-native 桌面（开箱即用 agent）** | **Bluefin / Bazzite（Universal Blue）** | 内置 goose 作为一等公民；但自家 `bluefin-mcp` 仓库**已归档** |

**明确没有的**：Arch Linux、Debian、Ubuntu、Fedora（社区侧）在 GitHub 上**基本没有**成规模的发行版专属 AI 管理实践 —— 搜索 `arch linux mcp pacman` 返回 **0 个结果**。

---

## 1. 先把「AI 协同管理」拆成三类

用户问的「MCP、skills、软件方案」其实是三种不同东西，混在一起会得出错误结论：

| 类型 | 是什么 | 谁在做 | 成熟度信号 |
|---|---|---|---|
| **① MCP Server** | 给 LLM 客户端（Claude / goose / Gemini CLI）提供「查询或执行」系统操作的工具接口 | 厂商官方 + 个人开发者 | star 数、是否官方文档收录、是否随产品发布 |
| **② Skills** | `SKILL.md` 形式封装的知识/流程（如「NixOS rebuild 后如何验证」「generation 回滚步骤」） | 几乎只有社区 | 是否被真实配置仓库引用 |
| **③ 软件方案** | AI-native 发行版 / 发行版内置 agent | Universal Blue、个人研究项目 | 是否随镜像分发、是否默认启用 |

**关键观察**：**官方几乎只做 ①，社区才做 ②**。所以「哪个发行版有 skills」这个问题的答案只有 NixOS。

---

## 2. 官方侧：厂商到底投了多少

### 2.1 Red Hat / RHEL —— 官方投入最深，且可验证

GitHub 组织 `rhel-lightspeed` 的完整仓库列表（API 实测，2026-10-12）：

| 仓库 | ★ | 最后更新 | 作用 |
|---|---|---|---|
| `linux-mcp-server` | **317** | 2026-10-10 | 让 LLM 客户端远程与 Linux 系统交互（Apache-2.0） |
| `command-line-assistant` | 44 | 2026-10-06 | RHEL 命令行助手（CLA） |
| `docs2db` | 48 | 2026-10-11 | 文档转 RAG 数据库 |
| `okp-mcp` | 19 | 2026-10-12 | Red Hat Offline Knowledge Portal 的 MCP server |
| `sysadmin-agents` | 8 | 2026-07-06 | 系统管理员 agent |
| `goose-proxy` / `goose` | 5 / 4 | 2026-10-12 | goose 相关 |
| `docs2db-mcp-server` | 4 | 2026-07-30 | 文档 RAG 搜索 MCP |
| `redhat-status-mcp` | 2 | 2026-07-06 | 查询 Red Hat 服务状态 |
| `rhel-lightspeed-gitops` | 1 | 2026-07-06 | GitOps 应用集 |
| `HEAL` | 0 | 2026-06-01 | Heuristic Engine for Autonomous Labor |

**官方文档层面的证据（比 star 数更重要）**：
- `docs.redhat.com` 有专门的 **"Getting started with MCP server for Red Hat Lightspeed"**（更新至 2026-09-30）—— 这是**唯一一个把 MCP server 写进正式产品文档的发行版厂商**
- `access.redhat.com/articles/7141984` —— 汇总 RHEL / Lightspeed / Satellite 三套 MCP server 的资源
- Red Hat Developer 文章《Manage RHEL with MCP servers and Red Hat Lightspeed》（2026-10-08）：用 **goose** 同时挂载 **Lightspeed + Satellite + RHEL 三个 MCP server** 做实操，并总结 LLM 运维的经验教训
- Red Hat Summit 2026 有对应的 hands-on lab

**结论**：RHEL 是「官方工程化」维度唯一的第一名，且它做的是**可交付产品**，不是实验。

> ⚠️ 注意：`linux-mcp-server` 面向的是 **RHEL 系**（RHEL / CentOS Stream / Rocky / Alma / Fedora），不是「RHEL 专属功能」。理论上任何有 systemd + SSH 的发行版都能跑，但**只有 RHEL 有官方支持承诺**。

### 2.2 SUSE / openSUSE —— 产品化 MCP 覆盖面最广

| 产品 | 类型 | 时间 | 来源 |
|---|---|---|---|
| **SUSE Multi-Linux Manager MCP Server** | 商业产品内置 | 博客 2026-02；**5.2 版本原生 MCP** 2026-07 | suse.com/blog；`sovereignhub.suse.com/repositories/suse-agentic-mcp-multi-linux-manager` |
| **SUSE Observability AI Assistant & MCP Server** | 商业产品内置 | 官方文档（latest） | `documentation.suse.com/cloudnative/suse-observability/latest/en/advanced/ai-assistant.html` |
| **openQA 原生 MCP** | 开源基础设施 | 2025-09-23 公布，端点 `/experimental/mcp` | SUSE 官方博客《openQA introduces native MCP Support》；openSUSE News 2025-09-23 |
| **全产品线 MCP 战略** | 战略层 | SUSECON 2026（布拉格，2026-04-22）宣布 | 与 AWS、n8n、Stacklok 等联合 |

**openQA MCP 的细节（已核实）**：
- 由 openSUSE 项目成员把 MCP 集成进 **openQA 测试框架本身**（主仓库 `os-autoinst/openQA`，374★）
- **状态：experimental**，必须在 `openqa.ini` 中**手动启用**
- 用途：让 AI 查询测试结果、监控 openSUSE 的构建质量 —— 这是**唯一一个「发行版把自己的 QA 基础设施开放给 AI」**的案例

**注意**：SUSE 的 MCP 全部是**企业产品**（SUSE Multi-Linux Manager、SUSE Observability），面向的是 SLE / RHEL / Ubuntu 混合环境，**不是给 openSUSE Tumbleweed 桌面用户的**。openQA MCP 才是开源侧的真东西，但它是给**发行版开发者**用的，不是给终端用户管理自己机器用的。

### 2.3 Fedora —— 官方没有 MCP，但有官方 AI 政策

- **没有**官方 MCP server（可复用 RHEL Lightspeed 的代码，但无 Fedora 品牌支持）
- **有** Fedora Council 批准的 **《AI-Assisted Contributions Policy》**（2025-10-24）—— 要求 AI 辅助贡献必须满足 **Accountability（人对内容负责）+ Transparency（披露 AI 使用）+ 遵守许可证**
- 这是治理层面对 AI 的正式表态，在发行版中属先行者

### 2.4 Ubuntu / Canonical —— 有云侧 AI，无系统管理 MCP

- Canonical 的 AI 投入集中在 **Ubuntu AI / 云侧推理**，未发现面向「AI 管理系统」的官方 MCP
- 社区侧 `pazuzu1w/ubuntu_mcp_server` 44★（2025-06 后停更），`54rt1n/container-mcp` 22★

### 2.5 Arch / Debian —— 官方零投入

- Arch：搜索 `arch linux mcp pacman` = **0 结果**；ArchWiki 有 Anubis 反爬，无法确认是否有隐藏讨论
- Debian：有 **LLM 使用总决议**（2026-08-30，既不背书也不禁止），属治理表态，无技术产品

---

## 3. 社区侧：GitHub 项目实测（本轮全部经 API 独立核实）

### 3.1 NixOS —— 生态最厚，且是唯一有「完整闭环」的

| 仓库 | ★ | 最后更新 | 类别 | 说明 |
|---|---|---|---|---|
| `utensils/mcp-nixos` | **853** | 2026-09-05 | 查询 | 查 nixpkgs 包、NixOS 选项、Home Manager、nix-darwin、flake。MIT。**本报告核实过的最高星发行版专属 MCP** |
| `bolivian-peru/os-moda` | **120** | 2026-06-24 | 操作系统 | 为 AI agent 造的 OS 层，对 NixOS 服务器提供**带类型、可审计、原子回滚**的工具访问。⚠️ 作者自述 **"Research-grade; run it on a disposable box, not production"** |
| `michalzubkowicz/nixos-management-skill` | **61** | 2026-07-18 | Skills | **从官方文档与网站生成**的 NixOS AI Agent Skills，含最佳实践 |
| `marceloeatworld/nixos-ai-skill` | **30** | 2026-10-10 | Skills | 自动更新的 NixOS/Nix 生态文档，喂给 AI 编码助手 |
| `Kihara777/NixKits` | 28 | 2026-10-12 | Skills | 中文项目：软件、补丁、NixOS 模块与 AI 编码助手技能合集 |
| `lukasl-dev/rime` | 19 | 2026-01-03 | 查询 | 面向 NixOS 用户的 MCP server（已半年未更新） |
| `z1-0/skills-nix` | 17 | 2026-10-11 | Skills | AI agent skills with Nix |
| `JEFF7712/nix-agent` | 16 | 2026-10-12 | **操作** | MCP server + skill，用于**管理** NixOS 系统（不只是查询） |
| `felixdorn/mcp-nix` | 7 | 2026-01-08 | 查询 | Nixpkgs / NixOS / Home Manager / nixvim 的 MCP |
| `yolo-labz/nixos-ops-skill` | 0 | 2026-10-05 | Skills | Claude Code 的 NixOS 运维技能：**rebuild、debug、generations** |
| `vespo92/mcp-nixos-ops` | **0** | 2026-04-06 | 操作 | 通过 SSH 管理 NixOS 机器。⚠️ **0 star、创建当天即停止更新、无 license** —— 不可作为实践证据 |
| `iuliandita/skills` | 7 | 2026-10-08 | Skills | 基础设施/安全/工程的通用 agent skills（非 NixOS 专属） |
| `rokokol/nix-best-practices-skill` | 0 | 2026-10-08 | Skills | Nix 最佳实践（formatter 查不出的那部分） |

**NixOS 的独特性（这是回答用户问题的核心）**：

```
查询  mcp-nixos (853★)          ← 让 AI 知道「有哪些选项、怎么写才对」
操作  JEFF7712/nix-agent (16★)  ← 让 AI 能「执行 rebuild」
回滚  nixos-ops-skill           ← 让 AI 会「处理 generations 与回滚」
知识  nixos-management-skill (61★) + nixos-ai-skill (30★)
```

**四个环节都有独立项目，这在其他任何发行版上都不存在。** 原因很直白：NixOS 的系统状态是**纯文本 + 声明式**，天然适合 LLM 读写；其他发行版的系统状态是命令式副作用，AI 只能靠 shell 猜。

### 3.2 Universal Blue（Bluefin / Bazzite）—— AI-native 桌面，但自家 MCP 已归档

| 仓库 | ★ | 状态 | 说明 |
|---|---|---|---|
| `ublue-os/bazzite` | **9176** | 活跃（2026-10-12） | 游戏向镜像式发行版 |
| `ublue-os/bluefin` | **2622** | 活跃（2026-10-12） | 工作站向镜像式发行版 |
| `projectbluefin/bluefin-mcp` | 5 | **⚠️ 已归档（archived: true）** | 面向 Bluefin 的 MCP server —— **项目已停止** |

- Bluefin 的 AI 方案是**内置 goose 作为一等接口**，并**拥抱 RHEL Lightspeed 的代码**（Bluefin 官方文档明说）
- 另有 `llmman` + Docker Model Runner 做本地模型、`Ctrl-Alt-Backspace` 快捷启动 Alpaca
- **修正上一轮子代理的结论**：`bluefin-mcp` 不是活跃项目，已归档。Bluefin 的 AI 能力来自**集成 goose**，不是自研 MCP

### 3.3 其他发行版 / 通用项目

| 仓库 | ★ | 支持对象 | 说明 |
|---|---|---|---|
| `pazuzu1w/ubuntu_mcp_server` | 44 | Ubuntu | 给 Claude 有限控制 Ubuntu 的 MCP（2025-06 后停更） |
| `lacs-project/sysknife` | 16 | 通用 Linux | **typed + approval-gated + Ed25519-audited** 的 AI 管理系统，安全设计突出 |
| `lukasl-dev/rime` | 19 | NixOS | 见上 |
| `oborchers/mcp-server-pacman` | 11 | 通用 | ⚠️ **名称有误导性**：实为**包索引查询器**，不是 Arch `pacman` 系统管理 |
| `felixlheureux/mcpd` | 4 | 通用 Linux | 暴露 100+ Linux 系统管理工具（stdio） |
| `lioilsources/LeapDoctor` | 0 | **openSUSE Leap 16** | 唯一明确针对 openSUSE 的社区 MCP（0★，2026-02 停更） |
| `Spectro34/packaging-agent` | 0 | openSUSE OBS | AI 驱动的 **OBS 打包升级 agent**，自述 93% OBS 验证通过率 |
| `amineutron/fedora-agents` | 1 | Fedora | KVM/libvirt + Borg/Timeshift 备份的 MCP（1★） |
| `kinnoo-project/mcp-os` | 1 | Unix 系 | security-first 的 MCP 套件 |
| `Derek-Coleman-Associates-Corporation/cve-fix-check` | 0 | 跨发行版 | 跨 OSV + 各发行版 tracker 的 CVE 查询 |
| `26zl/cybersec-toolkit` | 70 | Debian/Ubuntu/Kali/Fedora/Arch | 一键装 670+ 安全工具（非 AI 管理，但覆盖多发行版） |

### 3.4 「AI-native OS」新物种（不是发行版，但值得知道）

| 仓库 | ★ | 说明 |
|---|---|---|
| `papercomputeco/stereOS` | **496** | 基于 Linux、为 AI agent 加固并专门构建的操作系统 |
| `hertz-ai/HARTOS` | 51 | AI-native OS：模型跑在本地硬件、节点 P2P 联邦、OpenAI 兼容 API、自带 Wayland compositor、8GB 可跑 |
| `timfewi/tentaflake` | 30 | 在**单台 NixOS** 上声明式部署并管理多个隔离 AI agent |
| `SoulKyu/leandro` | 14 | AI SRE agent，通过 Google Chat 诊断 K8s 事故 |
| `HashWarlock/nixo` | 13 | Rust 写的 AI 编码工作流沙箱编排 |
| `GutMutCode/opencode-nix` | 6 | OpenCode 打包成 NixOS 包 |
| `kcoopermiller/maid-os` | 5 | NixOS AI Agent（2024-05 起停更） |

**注意**：`stereOS`(496★) 和 `HARTOS`(51★) 是**独立自研 OS**，不是「某个现有发行版的 AI 实践」。它们证明这个方向有热度，但不构成对用户问题的回答。

---

## 4. Skills 生态：只有 NixOS 有

这是本轮调研最干净的一个结论。

- **NixOS 相关 skills 仓库**：至少 7 个（`nixos-management-skill` 61★、`nixos-ai-skill` 30★、`NixKits` 28★、`skills-nix` 17★、`nixos-ops-skill`、`nix-best-practices-skill`、`kevinher7/agent-toolkit`）
- **其他发行版**：搜索 `nixos skill claude` 有 5 个结果；换成 Arch / Fedora / Debian / openSUSE **无对应仓库**

**为什么会这样**：skills 是把「隐性运维知识」写成 Markdown 给 LLM 读。NixOS 的运维知识天然是「模块选项 + 最佳实践 + rebuild 流程」这种可文档化形态；而 Arch 的运维知识是「ArchWiki 上 200 个互相引用的页面」，很难压缩成一个 skill。

**社区长文已核实的引用**：`blog.jinli.io`《NixOS（四）：用AI维护配置——维护者技能》（2026-09-23）直接给出了一个 skill 的 frontmatter：

> "Maintain this repository's multi-machine NixOS flake and its operational documentation. Use when changing NixOS ..."

这是 skills 生态**在真实个人仓库里被使用**的直接证据。

---

## 5. 真实实践案例（不是项目，是「有人在用」）

### 5.1 中文社区（已逐条核实存在）

| 标题 | 平台 | 日期 | 内容 |
|---|---|---|---|
| 我让 AI 参与维护 **9 台 NixOS**（中）：权限、故障案例与… | 知乎 | 2026-08-03 | 权限、secrets、存储、监控、测试、任务验证的真实案例 |
| 我让 AI 参与维护 **9 台 NixOS**（下）：协作流程、证据边界… | 知乎 | 2026-08-03 | 协作流程与「证据边界」 |
| NixOS（四）：用 AI 维护配置——维护者技能 | blog.jinli.io | 2026-09-23 | 给出可用的 maintainer skill |
| 开发者发现 NixOS 与 AI 编程绝配：声明式配置天然契合大模型 | 80aj.com（V2EX 转载） | 2026-07-31 | 论点：人类难记 Nix 语法，AI 反而擅长 |
| MCP-NixOS：一个 Nix 配置的「终结者」 | 腾讯云开发者 | 2026-01-29 | VS Code Remote + MCP-NixOS 的实操 |

**「9 台 NixOS」这个案例的分量**：它不是单机玩具，是**多机 fleet 运维**，且分三篇写成系列（上/中/下），说明作者是认真在做。这是全网能找到的**最详细的一份 AI 运维真实记录**，而它恰好是 NixOS。

### 5.2 英文侧

| 来源 | 日期 | 内容 |
|---|---|---|
| Red Hat Developer | 2026-10-08 | 用 goose 挂载 3 个 MCP server 管 RHEL，总结 LLM 运维教训 |
| SUSE 官方博客 | 2025-09-23 / 2026-02 / 2026-07 | openQA MCP、Multi-Linux Manager MCP |
| Fedora Docs | 2025-10-24 | AI-Assisted Contributions Policy |

### 5.3 反面意见（必须一起看）

| 来源 | 日期 | 观点 |
|---|---|---|
| NixOS Discourse 讨论帖 | 2026-04-26 | 有人主张「用 agent 去配置就**违背了用 NixOS 的意义**」（NixOS 的价值正是让人理解系统）。**帖内未出现成功实践报告** |
| Kiteworks《Why Sysadmins Still Don't Trust AI With Production Systems》 | 2026-08-03 | 系统管理员对 AI 介入生产环境的信任度仍然很低 |
| Cursor + Railway 事故 | **2026-04-27** | AI agent **自主删除生产数据库**，HN 638 分。是「AI 运维」最著名的翻车案例 |
| `os-moda` 作者自述 | 2026-06 | "Research-grade; run it on a **disposable box, not production**" |

**这是本轮最重要的风险提示**：连最激进的 AI-native OS 项目作者都明确说「别用在生产」。任何「用 LLM 管发行版」的方案，在 2026-10 这个时间点，**默认前提都应该是「有快照/回滚兜底 + 有人复核」**。

---

## 6. 结论：到底选哪个

### 场景 A：企业 / 有支持合同 / 要进生产
→ **RHEL（+ Fedora 作为免费试验田）**
理由：唯一有官方 MCP 文档、唯一有专门 GitHub 组织持续投入、唯一有 Summit 动手实验。可复用代码到 Fedora/Rocky/Alma。

### 场景 B：个人 / 自托管 / 想要最活跃的社区生态
→ **NixOS**
理由：唯一三类（MCP + skills + 软件方案）都有的发行版；查询→操作→回滚链路完整；中文真实运维长文最多；`mcp-nixos` 853★ 是所有发行版专属 MCP 里最高星的。
代价：Nix 语言学习曲线；且默认**不启用** Btrfs 快照、`system.autoUpgrade` **失败不自动回滚**（详见第五份报告），需要自己补保护。

### 场景 C：想要「开箱就有 AI」
→ **Bluefin（Universal Blue）**
理由：内置 goose、本地模型（llmman + Docker Model Runner）、拥抱 RHEL Lightspeed 代码。
注意：自研 `bluefin-mcp` **已归档**，别指望它。

### 场景 D：你想要的是「发行版把自己的 QA 开放给 AI」
→ **openSUSE（openQA MCP）**
这是独一无二的案例，但面向发行版开发者，不是终端用户。

### 不建议
- **Arch**：官方零投入，社区零成规模项目（搜索 0 结果）。用 AI 管 Arch 意味着 AI 面对的是命令式副作用 + 无回滚 + 无声明式状态，风险最高
- **Debian/Ubuntu**：官方无系统管理 MCP，社区项目多为 2025 年停更

---

## 7. 存疑 / 未核实 / 已修正

### 本轮通过 GitHub API 独立核实并**修正**的结论

| 上一轮子代理的说法 | 实测结果 | 修正 |
|---|---|---|
| `bluefin-mcp` 是 Bluefin 的活跃 MCP 方案 | **5★，archived: true（已归档）** | 不能作为活跃方案 |
| `vespo92/mcp-nixos-ops` 是 NixOS 操作类 MCP | **0★，创建当天（2026-04-06）后无更新，无 license** | 不可作为实践证据 |
| `bolivian-peru/os-moda` 是「120★ 的 AI OS 实践」 | 120★ 属实，但作者自述 **research-grade，勿用于生产** | 需加风险标注 |
| `JEFF7712/nix-agent` 存在性存疑 | **确实存在，16★，2026-10-12 仍更新** | 确认存在 |
| `oborchers/mcp-server-pacman` 疑似 Arch 管理工具 | 11★，描述为 **"package index querying"** | 是查询器，非系统管理 |
| `iuliandita/skills` 是重要的 NixOS skill 集 | 仅 **7★**，且为通用基础设施 skills | 规模被高估 |
| `utensils/mcp-nixos` 853★ | **853★ 已核实** | ✅ 属实 |
| `rhel-lightspeed/linux-mcp-server` 317★ | **317★ 已核实**，且组织下有 6+ 相关仓库 | ✅ 属实，且投入被低估 |
| goose 在 `block/goose` | **已迁移至 `aaif-goose/goose`，55171★** | 组织变更 |

### 未核实 / 无数据
- 「LLM 生成 NixOS 配置的成功率」：**全网无任何量化实测数据**（含本报告）
- NixOS Discourse 反对帖的**完整讨论内容**：仅从搜索摘要获得，未逐条读原文
- 各发行版**真实使用 AI 运维的用户规模**：无任何数据
- `Spectro34/packaging-agent` 自称的「93% OBS 验证通过率」：**无第三方验证**
- `rhel-lightspeed` 下 `goose` / `goose-proxy` 两个仓库**无描述**，用途未核实
- `stereOS` / `HARTOS` 是否基于某个现有发行版：**未核实**

### 方法论备注
- 本轮所有 star / 更新日期均来自 GitHub REST API，**不再依赖网页抓取**（上一轮 GitHub 页面 WebFetch 多次返回空，是结论不可靠的根因）
- 搜索查询的召回率有限：`arch linux mcp pacman` 返回 0 结果，但**不等于 Arch 绝对没有**，只能说「没有成规模、可被搜索到的项目」

---

## 附：可直接粘贴的验证命令

```bash
# 核实任意仓库的真实 star / 活跃度（不依赖网页）
curl -s "https://api.github.com/repos/utensils/mcp-nixos" \
  | python -c "import sys,json;d=json.load(sys.stdin);print(d['stargazers_count'],d['pushed_at'],d['archived'])"

# 按 star 排序搜索某发行版的 MCP 生态
curl -s "https://api.github.com/search/repositories?q=nixos+mcp&sort=stars&order=desc&per_page=15" \
  | python -c "
import sys,json
for i in json.load(sys.stdin)['items']:
    print(f\"{i['stargazers_count']:>6}*  {i['full_name']:<40} {i['pushed_at'][:10]}  {(i.get('description') or '')[:70]}\")"

# 列出某组织的全部仓库（看官方投入深度）
curl -s "https://api.github.com/orgs/rhel-lightspeed/repos?per_page=50&sort=updated" \
  | python -c "
import sys,json
for i in json.load(sys.stdin):
    print(f\"{i['stargazers_count']:>5}*  {i['name']:<35} {i['pushed_at'][:10]}\")"
```
