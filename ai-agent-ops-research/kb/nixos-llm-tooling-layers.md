---
id: nixos-llm-tooling-layers
title: NixOS × LLM 工具全景：四层架构（基础设施 / 知识 / 掌控 / 验证）+ 可借鉴设计模式
tags:
  - NixOS
  - LLM
  - MCP
  - agent-skills
  - nix-skills
  - mcp-nixos
  - nixfmt
  - statix
  - deadnix
  - nixd
  - nix-index
  - nix-sandbox-mcp
  - ZFS-preflight
created: 2026-10-12
updated: 2026-10-12
version: 1
status: stable
source: 本次会话实测（GitHub 14 组检索式 + 18 仓库 README/元数据直读 + NixOS Discourse 原帖 + 官网核验）
confidence: 已核实（元数据与 README/源码）；未做端到端部署实测
---

# NixOS × LLM 工具全景（四层）

## TL;DR

**提高 LLM 对 NixOS 的「理解」靠知识层 + 验证层；提高「掌控」靠掌控层。** 最被低估的是**验证层**——`statix` / `deadnix` / `nixfmt` / `nix flake check` / `nixos-rebuild dry-activate` / `nix-locate` 这 6 件套直接决定 LLM 是猜还是查。

**四个最高价值单项**：`olafkfreund/nix-skills`（10 个 pinned skill + NixOS module）、`utensils/mcp-nixos`（853★，2 工具 ~1,030 token 覆盖 130K 包 / 23K 选项）、`vespo92/mcp-nixos-ops`（ZFS preflight + flake-aware + node opt-in，设计最讲究）、`Kyure-A/agent-skills-nix`（261★，声明式管 skill 来源）。

---

## 第 0 层 · 基础设施（让 skill / MCP 可声明式管理）

| 项目 | ★ / 许可 | 价值 |
|---|---|---|
| **`Kyure-A/agent-skills-nix`** | 261★ MIT | 声明式管理 Agent Skills：flake-pinned 来源、`discover` 递归扫 `SKILL.md`、`idPrefix` 防 ID 冲突、npins registry + 原子 lock、`enable/explicit` 白名单。**内置 10 个 target 默认路径表**（agents / codex / opencode / claude / copilot / cursor / windsurf / antigravity / gemini / pi） |
| **`natsukium/mcp-servers-nix`** | 308★ Apache-2.0 | Nix 框架 + 27 个预配置 MCP 模块；`flavor` 适配 7 种客户端（claude / claude-code / vscode / vscode-workspace / **codex** / opencode / zed）；`envFile` + `passwordCommand` 凭据处理 + 版本 pin |
| **`numtide/llm-agents.nix`** | — | AI coding agent 包集合，**每日自动更新**，`nix run github:numtide/llm-agents.nix#<agent>` |

## 第 1 层 · 知识层（提高「理解」）

| 项目 | ★ / 许可 | 覆盖 |
|---|---|---|
| **`olafkfreund/nix-skills`** | 17★ MIT | **本轮最强发现。10 个 skill**：nix-language / nix-workflow / nixos-operations / nixos-coding-agents / nixos-wiki / home-manager / nix-darwin / microvm-nix / devenv-project / nixpkgs-development。带 `nixosModules.agentic` + Home Manager module + `nix run …?dir=demo` 一次性 VM。上游版本 pinned，每 skill 保留独立许可 |
| **`marceloeatworld/nixos-ai-skill`** | 30★ **无许可证** | 每日 GitHub Actions 从 4 个官方仓库（nix.dev / nixpkgs `nixos/doc/manual/` / nix-pills / release-wiki）**全量未删节**生成 ~40 个 reference；`SKILL.md` 当路由表；兼容 33+ 客户端 |
| `michalzubkowicz/nixos-management-skill` | 61★ MIT | 9 文件：SKILL.md 决策表 / configuration / vm-management / installation / image-building / impermanence / luks / monitoring / **anti-patterns.md**。README 自带装前安全审查提示词 |
| **`utensils/mcp-nixos`** | **853★** MIT | 2 工具 **~1,030 token**：130K+ 包、23K+ 选项、5K+ HM 选项、1K+ nix-darwin、2K+ noogle 函数签名、5K+ Nixvim、2.4K+ NVF、NixHub 版本史（带 nixpkgs commit hash）、binary cache 状态、FlakeHub、wiki.nixos.org + nix.dev、本地 `/nix/store` flake inputs |
| `lukasl-dev/rime` | 19★ MIT | 19 个只读 Nix/NixOS/HM/nvf/Nixhub 查询工具 |
| `felixdorn/mcp-nix` / `stubbedev/nix-mcp` | 7★ GPL-3.0 / 1★ MIT | Nix 生态知识（前者覆盖面广，后者 Go 重写 mcp-nixos，单二进制 + MCP roots 含 `X-Mcp-Root` header） |
| `nix-community/manix` | 133★ Apache-2.0 | CLI 选项/函数文档搜索 |

## 第 2 层 · 掌控层（提高「控制」）

| 项目 | ★ / 许可 | 关键能力 |
|---|---|---|
| **`vespo92/mcp-nixos-ops`** | 0★ **无许可证**（README 自称 MIT，矛盾） | **设计最讲究，值得直接抄**。1 工具 9 action：`list-nodes`/`status`/`rebuild-dry`/`validate`/`zfs-preflight`/`generations`/`diff`/`rebuild-switch`/`rollback`。① **ZFS preflight 门**——重建前验 pool 已导入且健康；② **flake-aware**——只在节点 `useFlake: true` 时才传 `--flake`，混用会开不了机；③ **node opt-in + 每调用 confirm** 双门；④ **dry-run first**；⑤ SSH ControlMaster 复用，后续调用 ~60ms |
| `JEFF7712/nix-agent` | 16★ MIT | `build`/`diff`/`switch`/`generations`；默认高信任（免密 sudo + 无提示 switch），低信任要手动降 |
| `bolivian-peru/os-moda` | 120★ Apache-2.0 | SafeSwitch 重建 + 健康检查失败自动回滚 + SHA-256 哈希链审计账本。作者自述「不要上生产」 |
| **`jacopone/clawnix`** | 4★ MIT | **`evolve` 插件是最值得借鉴的单点设计**：propose → 写入 `/etc/nixos/clawnix-evolved.nix` 专用 overlay → `nix flake check` → Telegram/web 审批 → `nixos-rebuild switch` → **失败自动 revert overlay + 回退 generation**。agent **只能改一个 overlay 文件**，sudo 规则窄到 `nixos-rebuild` |
| `nix-community/nixos-anywhere` | **3488★** MIT | SSH 远程装 NixOS，零接触供给 |
| `nix-community/colmena` | **2393★** MIT | 无状态 NixOS 集群部署，并行 + 失败隔离 |
| `serokell/deploy-rs` | **2370★** NOASSERTION | flake 部署 + **自动回滚** |
| `nix-community/nh` | —（nixpkgs 内） | nix helper，一条命令做 os 切换 / 搜索 / 清理 |

## 第 3 层 · 验证层（最被低估，直接决定 LLM 会不会瞎编）

**格式与 lint**

| 工具 | ★ / 许可 | 用途 |
|---|---|---|
| `NixOS/nixfmt` | **1626★** MPL-2.0 | 官方 formatter（push 2026-10-06） |
| `kamadorueda/alejandra` | **1412★** Unlicense | 另一种 formatter，风格更激进 |
| `Mic92/nixfmt-rs` | 165★ MPL-2.0 | Rust 重写 nixfmt |
| **`oppiliappan/statix`** | **960★** MIT | lint + 建议（repo 已从 `NixOS/statix` 迁到 `oppiliappan/`） |
| **`astro/deadnix`** | **790★** GPL-3.0 | 死代码扫描（已从 `juspay/deadnix` 迁到 `astro/`） |

**LSP**

| 工具 | ★ / 许可 | 用途 |
|---|---|---|
| **`nix-community/nixd`** | **1500★** LGPL-3.0 | Nix 语言服务器（C++，基于 Nix 库）。Discourse 原帖明确建议配 `nixd` + `nixfmt` |

**查找与诊断**

| 工具 | ★ / 许可 | 用途 |
|---|---|---|
| **`nix-community/nix-index`** | **1359★** | 「哪个包提供这个文件」——Discourse 原话：**teach it nix-index** |
| `nix-community/nix-index-database` | **623★** MIT | 每周更新的 nix-index 数据库 |
| `utdemir/nix-tree` | **1083★** BSD-3-Clause | 依赖图可视化 |
| `maralorn/nix-output-monitor` | **1679★** | 构建输出解析 |
| `Gabriella439/nix-diff` | **500★** BSD-3-Clause | 解释两个 derivation 为何不同 |
| `symphorien/nix-du` | **484★** LGPL-3.0 | gc-roots 可视化，算能回收多少空间 |
| `nix-community/nix-melt` | **317★** MPL-2.0 | flake.lock 浏览器 |
| `juspay/omnix` | **282★** AGPL-3.0 | `omnix health` 等（`nix-health` 49★ 已并入此仓库） |
| `nix-community/nixdoc` | **175★** GPL-3.0 | 生成 Nix library 文档 |

**内建验证命令**（零成本，最该进 skill）：`nix flake check` · `nixos-rebuild dry-activate` / `dry-build` · `nix eval` · `nixos-rebuild build --upgrade`

## 第 4 层 · 沙箱层

| 项目 | ★ / 许可 | 机制 |
|---|---|---|
| `SecBear/nix-sandbox-mcp` | 16★ MIT | bubblewrap + user/pid/net/mount namespace，**默认无网络**，项目只读挂载。**上下文预算设计值得抄**：单 `run(code, env, session)` 工具，**固定 ~420 token**，加环境不加工具（对比：8 个独立工具要 1,200+ token 且线性增长）。microvm.nix VM 后端 planned |
| `HashWarlock/nixo` | 13★ **无许可证** | Rust，88+ agent + 24 tool catalog，bubblewrap；macOS 用 Docker sidecar |
| `gotha/agentbox` | 5★ BSD-3-Clause | NixOS VM 隔离跑 agent |
| `timfewi/tentaflake` | 30★ MIT（pre-1.0） | systemd 监督的 OCI agent 容器（Hermes + ZeroClaw adapters）、cosign 镜像门、Restic 备份、Falco 检测 |

---

## 可借鉴的 5 个设计模式

| # | 模式 | 出处 | 为什么值得抄 |
|---|---|---|---|
| 1 | **ZFS preflight 门** | `mcp-nixos-ops` | 重建前先验 pool 已导入且健康，比事后回滚有用 |
| 2 | **flake-aware 开关** | `mcp-nixos-ops` | `--flake` 只在节点声明 `useFlake` 时传；混用直接开不了机 |
| 3 | **scoped overlay + 自动回滚** | `clawnix` `evolve` | agent 只能改一个专用 overlay 文件；`nix flake check` 前置；失败自动 revert + 回退 generation |
| 4 | **单参数化工具 + 固定上下文预算** | `nix-sandbox-mcp` / `mcp-nixos` | 环境加参数值，不加工具数；上下文成本恒定 |
| 5 | **flakes + npins 声明式管 skill 来源** | `agent-skills-nix` | 比 `git clone` 到 `~/.claude/skills` 可复现、可审计、可回滚 |

## 社区原声（NixOS Discourse #80199，2026-09-22）

- `find /nix/store/*something-* -iname libsomething.so` —— **永远别这么干**
- 必须教它 **devShell 是什么**（agent 最常搞错）
- **教它 `nix-index`**
- 打包或报错时去搜 nixpkgs 的 issues / PRs
- 入口分三类要分开做 skill：**开发者（devShell）/ home-manager（darwin 居多）/ NixOS 运维（`nixos-rebuild switch`）**
- opcode/opencode 里可配 `nixd` LSP + `nixfmt` formatter

## 给 Hermes / Codex / OpenClaw 的最小落地清单

| # | 装什么 | 作用 |
|---|---|---|
| 1 | `utensils/mcp-nixos`（853★ MIT，2 工具 ~1030 token） | 知识层，防幻觉包名/选项名 |
| 2 | `vespo92/mcp-nixos-ops`（抄设计自建）或 `JEFF7712/nix-agent` | 执行层 |
| 3 | `olafkfreund/nix-skills` 10 个 skill，用 `agent-skills-nix` 声明式管 | 规范层 |
| 4 | CLI 接地：`statix` + `deadnix` + `nixfmt` + `nix flake check` + `nixos-rebuild dry-activate` + `nix-locate` | 验证层 |
| 5 | `nixd` LSP（Codex / opencode / Zed 都支持） | 代码智能 |
| 6 | `SecBear/nix-sandbox-mcp`（跑不可信代码时） | 沙箱层 |

## 许可证红旗

| 项目 | 问题 |
|---|---|
| `marceloeatworld/nixos-ai-skill`（30★） | **无许可证**。内容来自 NixOS 官方仓库（各带原许可），但仓库本身无许可，商业/分发前先问作者 |
| `vespo92/mcp-nixos-ops`（0★） | GitHub 元数据 `license = None`，**README 写 MIT**——矛盾，用前确认 |
| `HashWarlock/nixo`（13★）、`DanielRamosAcosta/nixos-mcp`、`aldebogdanov/nixos-colmena-deploy-mcp`、`andre-amorim/nix-mcp` | 无许可证 |

## 未核实 / 存疑

| 项 | 状态 |
|---|---|
| `nh` 的仓库级元数据 | 未核实（检索式未命中，只确认 nixpkgs 有该包） |
| `nix-sandbox-mcp` / `nixo` / `mcp-nixos-ops` 的实际安全边界 | **未做端到端实测**，全部是 README/源码断言 |
| Codeberg / GitLab / SourceHut 上的 NixAI 项目 | **未查**。Nix 社区在 sr.ht 很活跃（`jail.nix` 就在 `git.sr.ht/~alexdavid/`） |
| r/NixOS 原帖 | 未检索（本轮以 Discourse + GitHub 为主） |
| `nix-skills` 各 skill 的实际 token 占用 | 未核实（未加载实测） |
| `mcp-nixos` 的默认工具集具体包含哪些 | 未核实（README 有 `#default-toolset` 锚点未展开读） |

## 相关文件

| 文件 | 说明 |
|---|---|
| `nixi-port/` | **nixi 规范转 Hermes/OpenClaw 可用的 skill 包** |
| `kb/nixi-to-agent-skill-port.md` | nixi → agent skill 的转换映射记录 |
| `kb/nixi-nixos-agent-vs-general-agents.md` | Nixi 项目剖析与平替可行性 |
| `kb/package-manager-mcp-apt-dnf-zypper-pacman.md` | 包管理器 MCP 选型 |
