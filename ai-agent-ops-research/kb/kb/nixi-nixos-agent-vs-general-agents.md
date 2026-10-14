---
id: nixi-nixos-agent-vs-general-agents
title: Nixi（codeberg.org/ewrogers/nixi）项目剖析：Go 写的 NixOS 垂直 agent，能否用 Hermes/OpenClaw/Codex 平替
tags:
  - Nixi
  - NixOS
  - Go
  - Bubble-Tea
  - agent-architecture
  - Hermes-Agent
  - OpenClaw
  - Codex
  - MCP
  - sudo-scope
  - AGPL-3.0
created: 2026-10-12
updated: 2026-10-12
version: 1
status: stable
source: 本次会话实测（Codeberg API 元数据 + 15 个文件直读 + 官网/文档站在线核验）
confidence: 已核实
---

# Nixi 项目剖析与平替可行性

## TL;DR

**Nixi 是一个 Go 写的、只面向 NixOS 的垂直对话式运维 agent（自带 TUI + Web UI），不是 MCP server，`go.mod` 里零 MCP 依赖，全仓库 grep `mcp` = 0 命中。** 它的 13 个工具是 Go 里手写的，不能通过 MCP 扩展。**规模极小且已停更**：0★ / 0 fork / 1 watcher，最后提交 2026-03-31（距今约 6.5 个月），仅 1 个 release `v0.1.0`，**无测试**。

**平替结论**：可以用 Hermes / OpenClaw / Codex 平替，**但不是 1:1**——要拼 4 块（领域 MCP + 权限 + 记忆 + 打包）。**nixi 的配置资产（AGENTS.md / nix/module.nix / scoped sudo 规则表）比它的 13 个 Go 工具更值得抄。**

---

## 1. 项目元数据（2026-10-12 实测）

| 项 | 值 |
|---|---|
| 全名 | `ewrogers/nixi` |
| 托管 | **Codeberg**（GitHub 上无镜像，`nixi+nixos+agent` 搜索 total=1 且是无关项目） |
| 描述 | *"AI agent for managing NixOS servers"* |
| 语言 | **Go** |
| 许可 | **AGPL-3.0**（⚠️ 有传染性） |
| 星标 / Fork / Watcher | **0 / 0 / 1** |
| 创建 / 最后更新 | 2026-03-23 / **2026-03-31**（停更约 6.5 个月） |
| 最后提交 | 2026-03-31 `fix: Ollama tool call compatibility and web UI improvements` |
| 仓库大小 / 文件数 | 4,634 KB / 101 个条目 |
| Release / Tag | **仅 `v0.1.0`**（2026-03-31） |
| Issues / PR | 0 / 0 |
| 测试 | **无**——AGENTS.md 原文：*"No test suite yet — verify changes compile with `go build ./cmd/nixi && go vet ./...`"* |
| 官网 | `docs.nixi.sh` 在线（8,667 B HTML）；`www.nixi.sh/install` 在线（41,026 B 安装脚本，与 `scripts/install.sh` 同尺寸）；`nixi.sh` 根域不可达（http=000） |

## 2. 技术栈（源码实测，非 README 自述）

| 层 | 实测 |
|---|---|
| 语言 / module | Go **1.26.1**，`codeberg.org/nixi/nixi` |
| TUI | **Bubble Tea** v1.3.10 + Bubbles v1.0.0 + Lipgloss + **Glamour** v1.0.0（markdown 渲染） |
| Web | **coder/websocket** v1.8.14；HTTP + WebSocket；前端 vanilla JS 通过 `go:embed` 内嵌二进制 |
| 存储 | **modernc.org/sqlite** v1.47.0（纯 Go，无 CGO）+ **FTS5 全文检索** |
| LLM | 自写双协议流式客户端：Ollama `/api/chat`（NDJSON）+ OpenAI 兼容 `/v1/chat/completions`（SSE）；**按 URL/端口自动探测** API 类型。**无 Anthropic 原生协议** |
| 打包 | `flake.nix`（`pkgs.buildGoModule`，`vendorHash = null` 待填）+ `nixosModules.default` → `services.nixi` |
| 分发 | 静态链接二进制：linux/386 · amd64 · arm64 · riscv64（**仅 Linux**） |

**完整依赖清单只有 6 个直接依赖**：bubbles / bubbletea / glamour / lipgloss / coder-websocket / modernc-sqlite。**没有一个 MCP SDK。**

### 2.1 架构

```
用户 → TUI / Web UI → Agent（最多 10 轮工具调用）→ LLM Client → Ollama / OpenAI 兼容 API
                              ↓
                        Tool Registry → Executor → Local(os/exec) 或 SSH
```

- Agent 循环：发历史 + tool schema → 流式返回 → 有 tool call 就执行 → 结果回灌 → 重复，直到 LLM 返回纯文本。
- 流式全程走 Go channel（`<-chan StreamEvent`），上下文取消向下传播。
- 每次 LLM 调用前**自动召回相关记忆**并重建 system prompt。

### 2.2 13 个工具（硬编码，不是 MCP）

`clock` · `system_info` · `container`（Podman 全生命周期 + URL 智能部署 + stack） · `nixos`（改配置 / rebuild / 回滚 / 包 / 服务 / 防火墙 / channel / generation / gc） · `network` · `files` · `logs` · `mount`（NFS/SMB/USB + 凭据） · `users`（NixOS 用户 + SSH key + 组） · `scheduler`（systemd timer） · `nvidia` · `amdgpu` · `memory` · `nodes`

> ⚠️ 文档里写「13 tools」，CHANGELOG 里列了 14 个（含 `clock`）。**数量口径不一致，以源码 `agent.New()` 注册表为准。**

## 3. ⭐ 三处真正值钱的设计（可复用资产）

### 3.1 工具级确认门（`docs/security.md`）

- `confirmed` 参数**从 LLM 的 tool schema 里隐藏** → LLM 无法伪造、无法绕过。
- 确认由 **agent 层**处理，不由 LLM 处理；工具返回 bullet 摘要，agent 直接呈现。
- 读操作免确认；写操作全要：改 NixOS 配置 / rebuild / rollback / reboot / 防火墙开闭 / 装删包 / 系统升级 / 增删 channel / gc generation / unmount / 用户组与 shell 变更 / GPU 驱动 / 建删定时任务。
- 说「yes + 附加指令」会合并成一个工作流，不重复确认。

### 3.2 三层 Executor 抽象（`internal/tools/executor.go`，实测 7,223 B）

| Executor | 实现 |
|---|---|
| `LocalExecutor` | `os/exec` + `Setsid: true`（防子进程写 `/dev/tty` 冲掉 TUI）+ 注入 `/run/current-system/sw/bin` 到 PATH |
| `SSHExecutor` | `ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10`，参数逐个 shell-quote 后拼接 |
| **`MonitoredExecutor`** | 包装任意 executor，**在 executor 层拒绝所有变更命令**（`isMutatingCommand`），LLM 要什么都被拒 → **node 级只读** |

两个关键判定函数分工明确：
- `needsSudo()` —— **路径感知**，只对 `/srv/` `/etc/` `/var/` `/mnt/` 下的操作前置 sudo；`nixos-rebuild`/`reboot`/`passwd`/`nix-channel`/`nix-env` 等无条件 sudo。
- `isMutatingCommand()` —— **比 `needsSudo` 更宽**，无论路径一律拦：`sudo`/`nixos-rebuild`/`reboot`/`tee`/`mkdir`/`rm`/`cp`/`mv`/`chmod`/`chown`/`ssh-keygen`/`ssh-copy-id`，以及 `podman run|rm|stop|pull|rmi|network|volume`、`systemctl start|stop|restart|enable|disable|mask`。

> **设计原则（AGENTS.md 原文）**：工具必须走 `Executor` 接口，**永不直接 `os/exec`**，这样同一份工具代码本地/远程通用。例外只有 `memory`（直连本地 SQLite）和 `nodes`（自建 `LocalExecutor` 做 SSH 探测）。

### 3.3 Scoped sudo 白名单（`docs/security.md` + 41 KB `install.sh`）

只对 19 类命令给 sudo，通过 NixOS `security.sudo.extraRules` 落地：

`nixos-rebuild` · `systemctl` · `podman`/`docker` · `nix-env` · `nix-channel` · `nix-store` · `reboot` · `tee`（写 `/etc/nixos/`） · `nft`/`iptables` · `mkdir -p /srv/*` · `rm -rf /srv/*`（仅用户明确要求时） · `mount` · `umount` · `mkdir -p /mnt/*` · `chmod` · `passwd` · `chpasswd` · `chown` · `mkdir -p /home/*` · `systemd-run`

**明确不给 `rm` / `cp` / `mv` 免密 sudo**（防 `/srv/` 外的误伤或恶意破坏）。`/srv/` 归 `nixi` 用户所有，容器数据全部限制在 `/srv/<name>/`，`/srv/` 外的 volume mount 在工具层就被拒。

> **⭐ 第 3 点是纯 NixOS 系统配置，与 agent 无关——任何 agent（Hermes / Codex / OpenClaw）都能直接复用。**

### 3.4 其他值得一提的

- **Sensitive data handling**：SMB 密码 / 数据库凭据 / API key 走**掩码输入**，**直接传给工具，永不进入 LLM 对话历史**；所有工具输出中的密码/token/secret 全部脱敏；NixOS 配置读取自动过滤敏感行；SMB 凭据存 `/srv/.credentials/` 600 权限 root 所有。
- **Web UI 认证**：bcrypt 哈希存 `~/.config/nixi/config.toml`；HMAC 签名 httpOnly cookie，30 天过期，每次服务启动重新生成；未认证的 WebSocket 升级返回 401；登录失败返回通用错误（防用户枚举）。
- **记忆**：`~/.local/share/nixi/memory.db`，SQLite + FTS5；`/clear` 和重启都不丢；`/memories` 命令不过 LLM 直接列。

## 4. 平替可行性分析（核心问题）

### 4.1 逐部件映射

| nixi 的部件 | 通用 agent 平替方案 | 差距 |
|---|---|---|
| 13 个领域工具 | `JEFF7712/nix-agent`（rebuild/switch/rollback）+ `utensils/mcp-nixos`（只读查包/选项）+ `tumf/mcp-shell-server`（通用 argv 白名单，覆盖 container/mount/network/logs/users）+ `openSUSE/systemd-mcp`（服务 + timer，polkit） | **3 块没有现成 MCP**：GPU 驱动（nvidia/amdgpu）、SMB 凭据管理、compose 智能部署 → 得自己写或走 shell 层 |
| 工具级确认门 | Hermes `trust: untrusted` + 宿主审批；Codex approval modes | **粒度不同**：nixi 是「工具级 + schema 隐藏参数」，宿主审批是「整轮 / 整命令」 |
| `MonitoredExecutor`（node 级只读） | Hermes `tools.include` 白名单 / MCP `--read-only` | 近似，但 nixi 的拦截点在 **executor 层**，比工具白名单更靠底 |
| SQLite + FTS5 记忆 | Hermes 原生 llm-wiki（Karpathy 模式）/ `basic-memory` MCP | 近似 |
| TUI | Hermes CLI / Codex CLI | 近似 |
| Web UI（多会话 + 认证 + WebSocket 流式） | **Open WebUI**（更强，含 RBAC、多用户） | 通用方案更强 |
| NixOS module 打包 | 自己写 | **可直接抄 nixi 的 `nix/module.nix`（4,188 B）** |
| Scoped sudo 白名单 | **直接抄** | **无差距——纯系统配置** |

### 4.2 结论

| 需求 | 选择 |
|---|---|
| 「开箱即用的 NixOS 专用 agent」 | **nixi**（但风险：6.5 个月无提交 / 0 测试 / 仅 v0.1.0 / AGPL-3.0） |
| 「一套 agent 同时管 NixOS + Arch + Fedora + openSUSE」 | **Hermes / OpenClaw / Codex 是唯一解**——nixi 只会 NixOS |
| 「改 flake / 写 Nix 表达式」 | **Codex 明显更强**——nixi 只会模板化改配置 + `tee` 到 `/etc/nixos/` |
| 「最省力路线」 | 抄 nixi 的 `AGENTS.md` + `nix/module.nix` + scoped sudo 规则表 → 接到 Hermes/Codex，配 `nix-agent` + `mcp-nixos` + `tumf/mcp-shell-server` |

> **一句话**：nixi 是「垂直整合的成品」，Hermes/Codex 是「通用底盘 + 自己拼装」。**nixi 的代码价值低于它的配置文件价值。**

## 5. 可复用操作

### 5.1 直接抄的三个文件

```bash
base=https://codeberg.org/ewrogers/nixi/raw/branch/main
curl -sL "$base/AGENTS.md"       -o AGENTS.md        # 6,786 B NixOS 运维规范
curl -sL "$base/nix/module.nix"  -o nixi-module.nix  # 4,188 B NixOS module
curl -sL "$base/scripts/install.sh" -o nixi-install.sh  # 41,026 B，含 sudo 规则表
curl -sL "$base/docs/content/security.md" -o security.md # 7,062 B 安全模型全文
```

### 5.2 抄它的 sudo 规则思路（落到 NixOS）

```nix
security.sudo.extraRules = [
  { users = [ "nixi" ];
    commands = [
      { command = "/run/current-system/sw/bin/nixos-rebuild"; options = [ "NOPASSWD" ]; }
      { command = "/run/current-system/sw/bin/systemctl";     options = [ "NOPASSWD" ]; }
      # ... 按 §3.3 的 19 类清单逐条加
      # ⚠️ 不要给 rm / cp / mv 免密 sudo
    ];
  }
];
```

### 5.3 照抄它的 Executor 分层到自己的 MCP 方案

| nixi 概念 | MCP 等价物 |
|---|---|
| `LocalExecutor` | 本地 stdio MCP（`tumf/mcp-shell-server` 本地模式） |
| `SSHExecutor` | `classfang/ssh-mcp-server`（`--whitelist` 完整命令正则） |
| `MonitoredExecutor` | MCP 的 `--read-only`（如 `github-mcp-server --read-only`）或宿主侧 `tools.include` 白名单 |
| `needsSudo` 路径感知 | `ALLOW_PATTERNS` 里按命令 + 参数全匹配 |
| `isMutatingCommand` 宽拦截 | `ALLOW_COMMANDS` 只放只读命令 |

## 6. 坑与反直觉

1. **它根本不是 MCP server**——`go.mod` 零 MCP 依赖，全仓库 grep `mcp` = 0 命中。想「加个 MCP 扩展它」做不到，只能改 Go 代码。
2. **文档写 13 tools，CHANGELOG 列 14 个**——数量口径不一致。
3. **AGPL-3.0 有传染性**——要把 nixi 集成进自己的对外服务，需评估开源义务。
4. **仅 Linux**——无 macOS / Windows 二进制；且核心功能强依赖 NixOS（`nixos-rebuild` / `nix-channel` / `nix-env` / `nix-store` / `/run/current-system/sw/bin`），**在非 NixOS 上大部分工具会失效**。
5. **6.5 个月无提交 + 0 测试 + 仅 1 个 release**——`v0.1.0` 即全部。依赖它 = 依赖一个人 9 天的产出（创建 2026-03-23 → 最后提交 2026-03-31）。
6. **`flake.nix` 的 `vendorHash = null` 是待填状态**——直接 `nix build` 会失败，需先跑一次拿到正确 hash。
7. **Web UI 默认绑 `0.0.0.0`**（`nix/module.nix` 的 `web.host` 默认值）——暴露到 LAN 之外必须上反代 + TLS。
8. **无 MCP 意味着无法复用生态**——GitHub MCP、包管理器 MCP、搜索 MCP 全部接不上。这是它与 Hermes/Codex 的根本差距。
9. **官网分裂**：`docs.nixi.sh` 与 `www.nixi.sh/install` 在线，但 `nixi.sh` 根域不可达——评估时别只试根域就判定项目死了。
10. **Codeberg 的 `updated_at` 会因元数据变更刷新**——判断活跃度要看**最后提交时间**，不是 `updated_at`。

## 7. 未核实 / 存疑

| 项 | 状态 |
|---|---|
| `internal/tools/` 各文件里 13 个工具的实际注册数量 | 部分（读了 `registry.go` 与 `executor.go`，未逐文件数 `Name()` 实现） |
| `install.sh` 的完整 sudo 规则（41 KB 未逐行读） | 部分（§3.3 清单来自 `docs/security.md` 表格） |
| 项目是否已实质停更 vs 只是作者休息 | **推断**（6.5 个月无提交 + 0 issue/PR，倾向停更） |
| 是否有其他分发渠道（AUR / nixpkgs 已收录？） | 未核实 |
| Hermes / OpenClaw / Codex 的**具体版本**对 NixOS 运维的支持度 | 未核实（本 KB 只做部件级映射，未做端到端实测） |
| `docs.nixi.sh` 的文档是否与 `main` 分支同步 | 未核实 |

## 8. 相关文件

| 文件 | 说明 |
|---|---|
| `kb/hermes-openclaw-linux-ops-agent-stack.md` | Hermes / OpenClaw Linux 运维栈（含 NixOS 执行层表） |
| `kb/package-manager-mcp-apt-dnf-zypper-pacman.md` | 包管理器 MCP 选型 |
| `kb/github-mcp-server-official.md` | GitHub 官方 MCP Server |
| https://codeberg.org/ewrogers/nixi | 项目仓库 |
| https://docs.nixi.sh | 官方文档站（在线） |
