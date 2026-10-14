# 用 Hermes Agent / OpenClaw 管理 Linux（Arch、NixOS）运维：profile、MCP、技能与知识库选型

调研日期：2026-10-12
版本基准：Hermes Agent `NousResearch/hermes-agent` @ commit `4e7403130e`（本机 git 仓库实测）
方法：本机源码与官方文档逐项审计（一手）+ GitHub 仓库核验 + 社区信号检索。所有数字均可回溯到命令输出。

---

## Executive Summary

Hermes Agent 官方目录里有 65 个已审 MCP、152 个可选技能、349 个插件，**但没有一个针对 NixOS、Arch、Ansible 或 SSH 远程执行**——它的官方 MCP 是 SaaS 取向的（Datadog、Grafana、Cloudflare、GitLab、Semgrep、BetterStack、Globalping）。运维这条线必须自己接，且社区已有可直接用的现成件：`mcp-nixos`（只读查询，2 个工具约 1030 token）与 `classfang/ssh-mcp-server`（4 个工具，自带正则白名单）。

关于知识库，结论是"**先文件，后 MCP，最后才 RAG**"。Hermes 原生已带 `llm-wiki`（Karpathy 的 markdown 三层结构）、`obsidian`、`siyuan`、`qmd` 四个知识库类技能，零成本即可落地；而内置持久记忆只有 2200 字符（memory）+ 1375 字符（user），**它天生不是知识库**，只是"偏好与约定"的存储，运维知识必须外置成文件。

最大的风险不是能力不足，而是权限过大。社区有明确先例：OpenClaw 在 2026 年 3 月清空了用户 Program Files；另有 AI Agent 删除生产数据库的事件在 Hacker News 拿到 763 分。本机 OpenClaw 的 `SOUL.md` 与 Hermes 的 `command_allowlist` 是必须首先配置的两道闸。

---

## 一、本机现状体检（实测，非推测）

| 扩展层 | 实测结果 | 判断 |
|---|---|---|
| Hermes 根目录 | `%LOCALAPPDATA%/hermes/`，内含 `hermes-agent/` git 仓库，origin = `github.com/NousResearch/hermes-agent` | ✓ 官方仓库，非 fork |
| 已配置 MCP | `config.yaml` **无 `mcp_servers` 段**，0 个 | ✗ 完全空白 |
| 持久记忆 | `memory_char_limit: 2200`、`user_char_limit: 1375`，无外部 provider | △ 仅够放偏好，放不下运维知识 |
| 搜索后端 | `.env` 中无 `EXA/TAVILY/FIRECRAWL/PERPLEXITY` 等 key，仅浏览器调试开关 | △ 只能走 keyless 轮转（框架内置 11 个后端） |
| 已装技能 | 58 个（`skills/` 下 `find -name SKILL.md`） | △ 无运维类 |
| 可选技能池 | 152 个（`optional-skills/`） | ✓ 可扩展面很大 |
| 官方 MCP 目录 | 65 个（`optional-mcps/`） | ✓ 但无 SSH/NixOS/Arch |
| 插件目录 | 349 个 yaml（`plugin-catalog/`） | ✓ 含社区 SSH/terminal 桌面插件 |
| OpenClaw | `~/.openclaw/workspace/` 有 `SOUL.md`/`AGENTS.md`/`USER.md`/`TOOLS.md`/`BOOTSTRAP.md`/`HEARTBEAT.md`/`IDENTITY.md` 全套模板 | △ 模板齐全但 `IDENTITY.md`、`USER.md` 仍为空，未初始化 |

一条重要发现：`optional-mcps/` 里与运维沾边的只有 `datadog`、`grafana`、`semgrep`、`cloudflare`、`gitlab`、`betterstack`、`globalping`、`buildkite`、`circleci`、`aws-knowledge`。全库 `grep -ril nixos|ansible|systemd|pacman` 在 `skills/` 与 `optional-skills/` 下**命中 0 条运维技能**。这决定了你的方案必须以"自建 skill + 第三方 MCP"为主干。

---

## 二、概念澄清：Hermes 里那堆 .md 到底谁是谁

这是最容易踩的坑——很多人以为写一个 `agent.md` 就够了。Hermes 官方文档 `which-file-does-what.md` 给了一张权威表：

| 文件 | 装什么 | 谁写 | 何时进上下文 | 位置 |
|---|---|---|---|---|
| `SOUL.md` | 人格、语气、沟通风格、禁止事项 | **你** | 系统提示 **slot #1**，会话开始 | `~/.hermes/SOUL.md` |
| `USER.md` | 用户画像（你的名字、角色、偏好） | **Agent**（通过 `memory` 工具） | 系统提示，会话开始的**冻结快照** | `~/.hermes/memories/` |
| `MEMORY.md` | Agent 自己的笔记（环境事实、项目约定、工具怪癖） | **Agent** | 同上 | `~/.hermes/memories/` |
| `AGENTS.md` | 项目指令、约定、架构、命令、端口、路径 | **你** | 会话启动时从工作目录载入，进入子目录时渐进发现 | 项目工作目录 |
| `.hermes.md` / `HERMES.md` | 同 AGENTS.md，但 Hermes 专属且优先级最高 | **你** | 同上 | 项目，向上找到 git root |

关键机制（决定你的运维规则该写哪儿）：

- 一个会话**只载入一个**项目上下文文件，优先级 `\.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`，首个命中即止。`SOUL.md` 独立加载，不在这条链上。
- **记忆是冻结快照**：会话中途让 agent 存了东西，磁盘立刻写入，但系统提示要下一个会话才更新。改 `SOUL.md`/`AGENTS.md` 也必须重启会话才生效。
- **profile 不是沙箱**。`hermes profile create coder` 只给它独立的 `HERMES_HOME`（自己的 config/.env/SOUL/memories/skills/cron/state.db），在 `local` 终端后端下，它对文件系统的访问权限和你的用户账号完全一样。

所以运维场景的正确分工是：**跨项目的安全底线写 `SOUL.md`，某个仓库/机器的具体操作规则写 `AGENTS.md`**。

---

## 三、Agent profile 该怎么写（可直接抄的骨架）

### 3.1 `~/.hermes/SOUL.md` 追加"运维安全底线"

```markdown
## 运维操作底线（不可协商）

1. 任何写操作前，先用只读命令确认现状（`systemctl status`、`df -h`、`nixos-rebuild dry-build`）。
2. 执行变更前，先把**完整命令原文**打印给我看，等我确认。不要直接执行。
3. 破坏性操作一律先停下问我：`rm`、`dd`、`mkfs`、`pacman -Rdd`、`nix-collect-garbage -d`、
   修改 `/etc/fstab`、`systemctl disable`、任何写 `/boot` 的操作。
4. 永远不要在没做快照/生成新 generation 的情况下改 NixOS 配置。
5. 读到任何密钥、token、私钥内容，不要复述到对话里，不要写进任何笔记文件。
6. 不确定就说不确定。不要编造包名、选项名或文件路径——先去查（mcp-nixos / arch wiki）。
```

### 3.2 项目级 `AGENTS.md`（放在你管理机器的运维仓库根目录）

```markdown
# AGENTS.md — <你的运维仓库>

## 环境
- 目标机 A：Arch Linux，主机名 `arch-box`，包管理 `pacman`/`paru`
- 目标机 B：NixOS，flake 在 `/etc/nixos`，重建命令 `sudo nixos-rebuild switch --flake /etc/nixos#host`
- 我本机：Windows，通过 SSH 访问上面两台

## 操作规则
- 发行版探测优先：先 `cat /etc/os-release`，不要假设。
- Arch 侧：升级前先 `checkupdates`，不要直接 `pacman -Syu` 全量滚。
- NixOS 侧：改配置后顺序固定 —— `nix flake check` → `nixos-rebuild dry-build` → 给我看 diff → 才 `switch`。
- 回滚路径必须写出来：NixOS 用 `nixos-rebuild switch --rollback` 或选 generation；
  Arch 用 `pacman -U /var/cache/pacman/pkg/<旧版本>.pkg.tar.zst`。
- 每次排障结束，把结论写进 `kb/`（见下），不要只留在对话里。

## 已知事实（不要重复踩）
- <机器 A> 的 nginx 配置文件在 /etc/nginx/sites-enabled/，不是 conf.d/
- <机器 B> 的 secrets 走 sops-nix，解密 key 在 /home/<user>/.config/sops/age/keys.txt
```

### 3.3 技能格式（你要自己写运维 skill 时的规范）

从 `website/docs/developer-guide/creating-skills.md` 提取的实际字段：

```yaml
---
name: nixos-ops
description: 安全地对 NixOS 主机做配置变更、重建与回滚
version: 1.0.0
author: <你>
license: MIT
platforms: [linux]                 # 只在 Linux 加载；可选 macos/linux/windows
metadata:
  hermes:
    tags: [NixOS, DevOps, Rollback]
    category: devops
    requires_toolsets: [terminal]   # 条件激活：只有 terminal 工具集在时才显示
    config:
      - key: nixos.flake_path
        description: "flake 所在路径"
        default: "/etc/nixos"
        prompt: "NixOS flake 路径"
---
# 标题
## When to Use
## Procedure        # 编号步骤
## Pitfalls         # 已知失败模式
## Verification     # 怎么确认成功
```

安装：`hermes skills install official/<category>/<skill>`（官方池）或 `hermes skills install <owner>/<repo>/<skill>`（第三方）。第三方安装会先跑安全扫描。

---

## 四、MCP 该装什么（这是本次调研的核心增量）

### 4.1 必装两个：一个只读查询，一个远程执行

| MCP | 仓库 | 提供什么 | 工具数/上下文成本 | 许可 | 风险 |
|---|---|---|---|---|---|
| **mcp-nixos** | `utensils/mcp-nixos` | NixOS 13 万+ 包、2.3 万+ 选项、Home Manager、nix-darwin、Nixvim、NVF、FlakeHub、Noogle、NixOS Wiki、nix.dev、包版本历史、binary cache 状态 | **仅 2 个工具，约 1030 token**（作者明确以省上下文为设计目标） | MIT | 只读查询，低 |
| **ssh-mcp-server** | `classfang/ssh-mcp-server` | `execute-command`、`upload`、`download`、`list-servers` | 4 个工具 | 见仓库 | **可执行任意 shell**，但支持 `--whitelist` / `--blacklist` 正则白名单；凭据留在本地 |

`mcp-nixos` 值得单独说：它**不需要装 Nix**，`uvx mcp-nixos` 即可跑，已进入 nixpkgs（`pkgs.mcp-nixos`），同时提供 NixOS/Home Manager/nix-darwin 的声明式安装。它的存在直接解决了"小模型会编造 Nix 包名和选项名"这个 NixOS 运维的最大痛点——搜索 `nvidia` 会返回真实的 NixOS Wiki 条目和真实选项路径，而不是幻觉。

### 4.2 可选加装（按需）

| MCP | 仓库 | 用途 | 备注 |
|---|---|---|---|
| **nix-agent** | `JEFF7712/nix-agent` | 真正执行 `build`/`diff`/`switch`/`generations`，加 `eval`/`locate`/`check` 自省 | ⚠️ 作者自述 **"Experimental and a work in progress"**。**默认高信任**：未经提示即可 `switch` 并配免密 sudo（范围限定本机 flake），低信任模式（主机提示 + sudo 密码）是"降级选项"。与 mcp-nixos 配对使用，还自带 companion skill |
| **arch-mcp** | `nihalxkumar/arch-mcp` | Arch Wiki、AUR、官方仓库查询 | 读取向 |
| **arch-wiki-mcp** | `egarcia74/arch-wiki-mcp` | Arch Wiki 确定性抽取 | 读取向 |
| **homelab-mcp** | `bshandley/homelab-mcp` | homelab 基础设施管理 | 社区项目，装前自审 |
| **mcp-homelab-server** | `Proto-labs-rnd/mcp-homelab-server` | homelab 工具集 | 社区项目，装前自审 |
| **docker/mcp-gateway** | `docker/mcp-gateway` | Docker 官方的 MCP Gateway/Toolkit，把多个 MCP 按 profile 统一跑在容器里 | 官方维护，适合想隔离 MCP 进程的场景 |
| **grafana/mcp-grafana** | `grafana/mcp-grafana` | 查 Grafana 仪表盘、数据源、事件 | 官方维护 |

Hermes 官方目录里能直接一键装的运维相邻项：`globalping`（全球网络探测，排查连通性有用）、`betterstack`（uptime 监控）、`semgrep`（代码安全扫描）、`datadog`、`grafana`、`cloudflare`、`gitlab`。

### 4.3 配置写法（Hermes 实际键名，非推测）

来自 `website/docs/reference/mcp-config-reference.md` 的根结构：

```yaml
# ~/.hermes/config.yaml
mcp_servers:
  nixos:
    command: "uvx"
    args: ["mcp-nixos"]
    lazy: true                    # 启动时只注册 schema，首次调用才起进程
    tools:
      include: ["nix", "nix_versions"]   # 收窄到白名单，别让全部工具挤占上下文

  arch:
    command: "npx"
    args: ["-y", "arch-mcp"]
    trust: untrusted              # 非完全可控的 server 一律标 untrusted

  ssh:
    command: "npx"
    args: ["-y", "ssh-mcp-server",
           "--whitelist", "^(systemctl|journalctl|df|free|uptime|pacman -Q|nixos-rebuild dry-build).*"]
    env:
      SSH_KEY_PATH: "${env:SSH_KEY_PATH}"   # 从 ~/.hermes/.env 解析
    trust: untrusted
    tools:
      include: ["execute-command", "list-servers"]   # 先不给 upload/download
```

几个必须知道的机制：

- `trust: untrusted` 的效果是：**每一个非只读工具调用都要经过审批界面**才执行。`readOnlyHint` 由 server 自己声明，撒谎的 server 最多只能骗过审批，拿不到额外权限；无法识别的值按 `untrusted` 处理（fail-closed）。
- `tools.include` 是白名单，支持 fnmatch 通配（`*_radar_*`）。`include` 与 `exclude` 同时存在时 `include` 优先。
- `${VAR}` 与 `${env:VAR}` 从当前 profile 的 `.env` 解析。远程 server 的 `url`/`headers` 里若变量未设，连接**直接失败**而不是发字面量——这是防 401 的设计。
- `lazy: true` 需要先有一次真实连接来填 schema 缓存。
- 内存重的 stdio server（浏览器类）用 `idle_timeout_seconds` / `max_lifetime_seconds` 自动回收。

### 4.4 如果你选 NixOS 模块部署（声明式，推荐给 NixOS 机器）

Hermes 官方带 `nixosModules.default`、Home Manager 模块和 flake。MCP 可直接在 Nix 里声明：

```nix
services.hermes-agent.mcpServers = {
  nixos = {
    command = "uvx";
    args = [ "mcp-nixos" ];
  };
  ssh = {
    command = "npx";
    args = [ "-y" "ssh-mcp-server" "--whitelist" "^(systemctl|journalctl|df|free).*" ];
  };
};
```

注意官方文档的硬警告：**`settings` 和 `environment` 里的值会进 `/nix/store`（全局可读），API key 必须走 `environmentFiles` + sops-nix/agenix**。另外 `documents` 选项（装 `AGENTS.md`）必须显式设 `workingDirectory`，否则文件会落到你没选的目录；`SOUL.md` 和 `memories/` 要用 `hermesHomeFiles` 而不是 `documents`。

---

## 五、技能该装什么

### 5.1 已在池中、与运维直接相关

| 技能 | 位置 | 用途 |
|---|---|---|
| `llm-wiki` | 已装（`skills/research/`） | **知识库主力**，见第六节 |
| `obsidian` | 已装（`skills/note-taking/`） | 读写 Obsidian vault，认 `OBSIDIAN_VAULT_PATH` |
| `docker-management` | 可选 `devops/` | Docker 容器/镜像/卷/Compose 管理 |
| `watchers` | 可选 `devops/` | 轮询 RSS/JSON API/GitHub，带去重水位线——适合做"服务异常告警" |
| `pinggy-tunnel` | 可选 `devops/` | 通过 SSH 建零安装隧道，临时暴露本地端口 |
| `mcporter` | 可选 `mcp/` | 从终端列出/授权/调用 MCP server 与工具——**调试 MCP 时很实用** |
| `fastmcp` | 可选 `mcp/` | 用 Python 自己写 MCP server |
| `1password` | 可选 `security/` | `op` CLI 读密钥，替代把密钥写进 `.env` |
| `qmd` | 可选 `research/` | 本地混合检索（关键词+语义+LLM 重排），全本地无云 |
| `siyuan` | 可选 `productivity/` | 通过 API 查询/编辑思源笔记知识库 |
| `duckduckgo-search` / `searxng-search` | 可选 `research/` | 免费无 key 搜索，补上没有搜索 API key 的短板 |
| `reddit-reading` | 可选 `social-media/` | 无浏览器读 Reddit 帖子与全部评论 |
| `code-wiki` | 可选 `software-development/` | 为任意代码库生成 wiki + Mermaid 图 |
| `openclaw-migration` | 可选 `migration/` | 把 OpenClaw 的 memories/skills 迁进 Hermes（`hermes claw migrate`） |

### 5.2 需要你自己写的两个 skill

`nixos-ops` 和 `arch-ops`——因为官方池里完全没有。模板见第 3.3 节。内容建议覆盖：发行版探测、升级前检查、变更前 dry-build/checkupdates、回滚路径、日志定位（`journalctl -u`）、常见故障的处理顺序。

---

## 六、知识库：MCP 还是软件？

### 6.1 先纠正一个前提

Hermes 的内置持久记忆是 **2200 字符（memory）+ 1375 字符（user）**，满了会直接报错并要求你先合并条目。官方文档明确写着："对于需要每次运行都用到的事实，**skill 往往是比 memory 条目更好的归宿**——它只在相关时加载，且不占用那 2200 字符预算。"

所以答案是：**内置记忆不是知识库，不要拿它当知识库用。** 运维知识（机器清单、踩坑记录、回滚步骤）必须外置成文件。

### 6.2 方案对比

| 方案 | 类型 | 存储格式 | 本地 | Agent 可写 | 维护负担 | 适用 |
|---|---|---|---|---|---|---|
| **A. Hermes 原生 `llm-wiki`** | 技能 + 文件 | **纯 markdown** | ✓ | ✓ | 极低（0 安装） | **首选**。你的运维知识库 |
| **B. Obsidian vault** | 软件 + 技能 | 纯 markdown | ✓ | ✓ | 低 | 你本人想可视化浏览笔记时 |
| **C. `qmd`** | 技能 + 本地索引 | 索引叠加在 md 上 | ✓ | 间接 | 中 | 笔记上百篇后加语义检索 |
| **D. `basic-memory`** | MCP server | markdown + 知识图谱 | ✓ 本地优先 | ✓ | 中 | 想跨多个 AI 工具共享同一知识库 |
| **E. SiYuan（思源）** | 软件 + 技能 | 自有格式 | ✓ | ✓ | 中 | 中文笔记体验优先 |
| **F. OpenViking / Holographic** | Hermes 记忆 provider | 文件系统层级 / HRR 代数 | ✓ | ✓ | 中 | 需要突破 2200 字符的"记忆"（非知识库） |
| **G. Mem0 / Honcho / RetainDB / Supermemory** | 记忆 provider | 云或自托管 | 部分 | ✓ | 中高 | 多 agent 共享记忆；云版有费用 |
| **H. RAG（RAGFlow/Dify/向量库）** | 平台 | 向量库 | 可自托管 | 间接 | **高** | 文档量极大且需要模糊语义召回时 |

### 6.3 为什么首选 A（文件），而不是 MCP 或 RAG

`llm-wiki` 是 Hermes 内置技能，实现的是 Andrej Karpathy 的 LLM Wiki 模式。它自己的论点很直接：**传统 RAG 每次查询都从零重新发现知识；wiki 只编译一次并持续保持更新——交叉引用已经建好，矛盾已经标记，综述已反映全部已摄入内容。** 分工是：人负责筛选来源和指定分析方向，agent 负责摘要、交叉引用、归档和一致性维护。

它的结构天然适合运维：

```
wiki/                        # 路径由 WIKI_PATH 环境变量指定，默认 ~/wiki
├── SCHEMA.md                # 约定、结构规则、领域配置
├── index.md                 # 分节内容目录 + 一行摘要
├── log.md                   # 追加式操作日志
├── raw/                     # 第 1 层：不可变原始素材（agent 只读）
│   ├── articles/  papers/  transcripts/  assets/
├── entities/                # 第 2 层：实体页（机器、服务、主机）
├── concepts/                # 第 2 层：概念页（systemd 单元、flake 结构）
├── comparisons/             # 第 2 层：横向对比
└── queries/                 # 第 2 层：值得留存的查询结果
```

第 1 层不可变、第 2 层 agent 可写、第 3 层 `SCHEMA.md` 约束 agent 行为——这个分层正好对应"原始日志永不改，结论可以改"的运维需求。技能还强制 agent **每次会话开始先读 `SCHEMA.md` → `index.md` → 最近 30 条 `log.md` 完成定位**，避免重复建页和漏交叉引用。

它就是一个 markdown 目录，可以直接用 Obsidian 或 VS Code 打开，用 git 做版本和备份，没有任何数据库依赖——**换 agent 也不丢**。

### 6.4 什么时候升级到 D 或 H

- 当你需要在 **Hermes 之外**（Claude Code、Codex、其他 MCP 客户端）也访问同一份知识库 → 上 `basic-memory`（本地优先、markdown、MCP 暴露、带知识图谱）。
- 当你需要突破 2200 字符的**记忆**上限（不是知识库上限）→ 换 Hermes 的 `memory.provider`。本机已内置可选的 provider 有：`byterover`、`holographic`、`honcho`、`mem0`、`openviking`、`retaindb`、`supermemory`。其中 `holographic`（本地、免费、无依赖）和 `openviking`（自托管、文件系统层级）最符合"本地优先"取向。
- 只有当你的运维文档到了**几千份且需要模糊语义召回**，RAG 才开始有意义。在那之前，RAG 的检索不确定性和维护成本都是负收益。

---

## 七、社区原声与安全事件

### 7.1 NixOS 官方论坛（2026-04-26）

一位新 NixOS 用户发帖求"本地 AI agent 改 configuration.nix"的经验报告（opencode + Ollama 本地模型 + 编辑 `configuration.nix` + 跑 `nixos-rebuild build` 验证 + 失败回滚），并明确问了三个和你一样的问题：**用什么模型、怎么给模型喂 NixOS 选项上下文（手写 AGENTS.md / mcp-nixos / RAG）、`nixai` 能不能和 agent 组合**。

社区回复的基调是**怀疑**，且值得你参考：

- "我觉得这正是因为很多人用 NixOS 就是因为他们想控制每一个细节。用 agent 来做这件事，某种程度上违背了初衷吧？那为什么不直接用 agent 配 Ubuntu，跳过 Nix 这一步？"
- "我真心认为，学会把配置加载进 repl、学会用 repl 探索 nix，是比伸手要 AI 更有用的层次。**AI 这个 easy button 是你在赚到资格之后才按的。**"
- 引用了一篇论文标题作为警告：*LLMs Corrupt Your Documents When You Delegate*。

该帖同时确认了生态现状：`nixai` 项目**已归档**；`mcp-nixos` 被明确点名作为"给模型喂 NixOS 选项上下文"的候选方案；`opencode` 在 nixpkgs 里有包（`pkgs.opencode`），不要用 npm 全局装。

### 7.2 安全事件（必须知道）

| 事件 | 时间 | 要点 |
|---|---|---|
| OpenClaw 清空用户目录 | 2026-03 | 用户想删游戏文件，Agent 却清空了 Program Files |
| AI Agent 删除生产数据库 | 2026-04-26 | Hacker News 热帖 763 分，Agent 收到指令后直接删库，随后自动生成"认罪报告" |
| `codex-agentguard` | 持续维护 | 专门拦 `rm -rf`/`DROP` 的防护层，威胁模型定义为"**粗心的 agent，而非恶意的人**"——删除命令一定是明文写出的，所以可以拦 |

对应到你的方案：Hermes 侧的防线是 `command_allowlist`（"永久允许"会写进 `config.yaml`，模式可以是精确命令、shell glob 如 `podman *`，或危险模式规则键）配合 `approvals.deny` 拒绝规则；另有 `security` 段的 tirith 预执行扫描（识别同形异义 URL、管道执行 shell、终端注入、环境变量篡改）。**这些默认都是关的或空的，必须你手动配。**

### 7.3 覆盖边界（必须声明）

**Reddit 原帖未能取得。** 本环境中 `reddit.com/.../search.rss` 返回空内容，`old.reddit.com` 直接跳登录墙（"To keep Reddit safe, accounts are required to access old Reddit"）。因此本报告第七节没有 Reddit 用户原话，只有 NixOS 官方论坛与中文技术社区的材料。这是覆盖缺口，不是"没找到相关内容"。

---

## 八、三档落地方案与执行顺序

顺序原则：**先零成本（配置/路径）→ 再技能 → 最后 MCP**。理由是 MCP 工具每轮都占上下文，且框架对 MCP 结果有更严格的溢出阈值。

### 档 1：今天，零成本（约 30 分钟）

1. 写 `~/.hermes/SOUL.md` 的运维安全底线（第 3.1 节骨架）。**这一步优先于一切**——它是唯一跨项目生效的闸。
2. 在你的运维仓库根放 `AGENTS.md`（第 3.2 节骨架）。
3. 在 `~/.hermes/.env` 加 `WIKI_PATH=<你的运维知识库路径>`，让 `llm-wiki` 有落点；然后让 agent 初始化 wiki（它会问你领域，回答"NixOS/Arch 主机运维"）。
4. 知识库目录 `git init`，加一个每日自动 commit——这是你唯一可靠的"回滚记忆"。
5. 检查 `config.yaml` 的 `command_allowlist`，确保**没有**任何 `rm`、`dd`、`mkfs` 之类的宽泛模式。

### 档 2：本周（约 1–2 小时）

6. 装 `mcp-nixos`（只读、2 工具、约 1030 token），配 `tools.include` 白名单。这是投入产出比最高的一步。
7. 装 `ssh-mcp-server`，**必须带 `--whitelist` 正则**，**必须标 `trust: untrusted`**，**先只开 `execute-command` 和 `list-servers`**，不开 `upload`/`download`。
8. 装 `mcporter` 技能，用它验证 MCP 是否真的连上、工具名是否正确。
9. 在目标机上加一层只读审计：`journalctl` 只读、`sudo` 只给 `nixos-rebuild dry-build` 和 `checkupdates` 这类无害命令。

### 档 3：按需

10. `nix-agent`（自动 `switch`）——只在你能接受"agent 无需确认即可切换系统代"时启用；否则改成低信任模式。作者自称实验性，建议先在非生产机跑一个月。
11. `qmd` 做语义检索（笔记过百篇后）。
12. 换外部记忆 provider（`holographic` 本地免费 / `openviking` 自托管）——如果 2200 字符真的不够。
13. 若在 NixOS 上部署 Hermes 本体，改用官方 NixOS 模块 + sops-nix 管密钥 + `mcpServers` 声明式配 MCP。

---

## 九、口径与可信度说明

| 等级 | 含义 | 本报告中的对应内容 |
|---|---|---|
| **A 已核实** | 本机源码 / 官方文档直接读出 | 65 个 MCP、152 个可选技能、58 个已装技能、349 个插件；`mcp_servers` 为空；记忆上限 2200/1375；SOUL/USER/MEMORY/AGENTS 分工；MCP 配置键名与 `trust` 语义；NixOS 模块与 `mcpServers` 写法；技能 frontmatter 字段；`command_allowlist` 语义；OpenClaw 目录与配置映射 |
| **B 社区实证** | 论坛帖 / 公开事件 | NixOS Discourse 帖的怀疑论与 `mcp-nixos` 推荐；OpenClaw 删文件事件；删库事件与 HN 763 分；`codex-agentguard` 的威胁模型 |
| **C 厂商/作者自述** | 项目 README 自述，未独立复现 | `mcp-nixos` 的"约 1030 token / 2 工具"；`nix-agent` 的"默认高信任、可降级"；`ssh-mcp-server` 的白名单机制 |
| **D 未验证** | 提及但无独立反馈 | `arch-mcp` / `arch-wiki-mcp` / `homelab-mcp` / `mcp-homelab-server` 的实际可用性与维护状态；各记忆 provider 的真实效果 |

抓取失败清单：Reddit 搜索 RSS（返回空）、`old.reddit.com`（登录墙）、`raw.githubusercontent.com/nihalxkumar/arch-mcp/main/README.md`（空响应）、`raw.githubusercontent.com/egarcia74/arch-wiki-mcp/main/README.md`（404，默认分支可能不是 main）。

---

## 十、References

1. [NousResearch/hermes-agent — 官方仓库（本机 origin）](https://github.com/NousResearch/hermes-agent)
2. [Hermes Agent — Which File Does What?（SOUL/USER/MEMORY/AGENTS 权威对照）](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/which-file-does-what.md)
3. [Hermes Agent — Profiles: Running Multiple Agents](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/profiles.md)
4. [Hermes Agent — Persistent Memory（2200/1375 字符上限）](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/memory.md)
5. [Hermes Agent — Memory Providers（Provider Comparison 表）](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/memory-providers.md)
6. [Hermes Agent — MCP 使用指南（trust 模型、工具过滤）](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/mcp.md)
7. [Hermes Agent — MCP 配置参考（根结构、server 键、tools 策略）](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/reference/mcp-config-reference.md)
8. [Hermes Agent — Optional Skills Catalog（152 个可选技能全表）](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/reference/optional-skills-catalog.md)
9. [Hermes Agent — Nix & NixOS Setup（NixOS 模块、mcpServers、sops-nix）](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/getting-started/nix-setup.md)
10. [Hermes Agent — Security（危险命令审批、command_allowlist、Tirith）](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/security.md)
11. [Hermes Agent — Creating Skills（SKILL.md 格式规范）](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/creating-skills.md)
12. [Hermes Agent — Migrate from OpenClaw（配置映射表）](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/guides/migrate-from-openclaw.md)
13. [Karpathy — LLM Wiki pattern (gist)](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
14. [utensils/mcp-nixos — NixOS 包/选项查询 MCP](https://github.com/utensils/mcp-nixos)
15. [MCP-NixOS 官网](https://mcp-nixos.io/)
16. [JEFF7712/nix-agent — NixOS build/diff/switch MCP](https://github.com/JEFF7712/nix-agent)
17. [classfang/ssh-mcp-server — SSH 执行 MCP（含 whitelist）](https://github.com/classfang/ssh-mcp-server)
18. [DeepWiki — ssh-mcp-server MCP Tools](https://deepwiki.com/classfang/ssh-mcp-server/4-mcp-tools)
19. [nihalxkumar/arch-mcp — Arch Linux MCP](https://github.com/nihalxkumar/arch-mcp)
20. [egarcia74/arch-wiki-mcp — Arch Wiki MCP](https://github.com/egarcia74/arch-wiki-mcp)
21. [bshandley/homelab-mcp](https://github.com/bshandley/homelab-mcp)
22. [Proto-labs-rnd/mcp-homelab-server](https://github.com/Proto-labs-rnd/mcp-homelab-server)
23. [docker/mcp-gateway — Docker 官方 MCP Gateway](https://github.com/docker/mcp-gateway)
24. [Docker Docs — MCP Gateway / Toolkit](https://docs.docker.com/ai/mcp-catalog-and-toolkit/mcp-gateway/)
25. [grafana/mcp-grafana — Grafana 官方 MCP](https://github.com/grafana/mcp-grafana)
26. [basicmachines-co/basic-memory — 本地优先 markdown 知识库 MCP](https://github.com/basicmachines-co/basic-memory)
27. [Basic Memory 官网](https://www.basicmemory.com/)
28. [NixOS Discourse — Local AI agent for NixOS configuration（2026-04-26）](https://discourse.nixos.org/t/local-ai-agent-for-nixos-configuration-looking-for-experience-reports/77238)
29. [NixOS Discourse — NixOS automation with AI](https://discourse.nixos.org/t/nixos-automation-with-ai/72275)
30. [NixOS Discourse — Introducing nixai（已归档）](https://discourse.nixos.org/t/introducing-nixai-your-ai-powered-nixos-companion/65168)
31. [linearuncle/codex-agentguard — 拦截 agent 的 rm -rf](https://github.com/linearuncle/codex-agentguard)
32. [AI Agent 误删系统文件后"自杀"，如何精准拦截 rm（OpenClaw 事件复盘）](https://www.80aj.com/2026/03/13/ai-agent-rm-rf-suicide/)
33. [AI Agent 删库事件引发热议：763 分 HN 热帖背后](https://waytoclawearn.com/zh/news/ai-agent-deleted-production-database-safety-lessons-20260427)
34. [sadjow/claude-code-nix — Nix 化 Claude Code](https://github.com/sadjow/claude-code-nix)
35. [llm-agents.nix 部署指南 — AI coding agents 的 Nix 包集合](https://blog.csdn.net/gitblog_00204/article/details/167272412)
36. [MCP Server 自建教程 | 私有数据塞 Claude](https://www.xiaoliblog.com/ai-native/mcp-server-self-host-claude-code-relay/)
