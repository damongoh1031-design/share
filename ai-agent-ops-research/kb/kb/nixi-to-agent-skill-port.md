---
id: nixi-to-agent-skill-port
title: nixi → Hermes/OpenClaw/Codex 规范移植：转换映射、失效清单与安装方式
tags:
  - nixi
  - NixOS
  - skill-port
  - AGENTS.md
  - Hermes-Agent
  - OpenClaw
  - Codex
  - confirmation-gate
  - scoped-sudo
  - MonitoredExecutor
created: 2026-10-12
updated: 2026-10-12
version: 1
status: stable
source: 本次会话实测（nixi 10 个源文件直读 + 转换产物实测落盘）
confidence: 已核实
---

# nixi 规范移植记录

## TL;DR

把 `ewrogers/nixi`（AGPL-3.0，只会 NixOS 的 Go agent）的 **AGENTS.md + docs/** 转换成
通用 agent 可直接加载的 skill 包，落在 **`nixi-port/`**。**只转规范，没转一行 Go 代码。**

**核心结论：你拿到的是「正确的判断规则」，不是「强制力」。** nixi 有 6 项安全保证是在 Go
代码里强制的，skill 只是文字。要真正等价，必须自己配宿主侧（见 §4）。

---

## 1. 产物清单（`nixi-port/`，9 个文件 / 42,004 B）

| 文件 | 大小 | 内容 |
|---|---|---|
| `README.md` | 5,676 B | 安装方式（5 类宿主）+ 转换映射 + 失效清单 + 许可证 |
| `AGENTS.md` | 3,770 B | 跨 agent 入口：三条铁律、关键词→动作表、禁止项 |
| `skills/nixos-ops/SKILL.md` | 7,623 B | 入口：18 行决策表 + 30 行确认矩阵 + 执行顺序 + NixOS 三语义 + 禁止项 |
| `skills/nixos-ops/confirmation-matrix.md` | 3,268 B | 30+ 操作逐条判定 + 批量单次确认 + 好/坏确认请求示例 |
| `skills/nixos-ops/rebuild-generations-upgrades.md` | 4,820 B | 环境判断 / rebuild 全流程 / generation 管理 / flake 与 channel 升级 / 包管理 / 防火墙 / 日志 / timer / 用户 |
| `skills/nixos-ops/secrets-sudo-scope.md` | 3,733 B | 凭据规则 + 19 条 scoped sudo 白名单 + NixOS 落地代码 + `/srv/` 所有权模型 |
| `skills/nixos-ops/containers-mounts-gpu.md` | 4,824 B | Podman 全流程 / NFS-SMB / NVIDIA / AMD（含 APU ROCm+GTT） / timer |
| `skills/nixos-ops/multi-node.md` | 4,232 B | local/ssh/monitored 三档 + SSH 安全参数 + sudo 前置规则 + monitored 红线命令表 + colmena/deploy-rs |
| `skills/nixos-ops/anti-patterns.md` | 4,046 B | A-H 八类反模式（含 devShell 专项） |

## 2. 转换映射（nixi 部件 → port 文件）

| nixi 源 | port 目标 | 转换方式 |
|---|---|---|
| `AGENTS.md` Design Principles | `AGENTS.md` §2 + `SKILL.md` §0 | **铁律原文保留**（dry-run 先行 / 绝不自我批准 / 绝不猜） |
| `AGENTS.md` Confirmation model 5 步 | `SKILL.md` §0.2 + `confirmation-matrix.md` | Go 状态机 → 文字规则；`NEEDS_CONFIRMATION\n` 协议 → "停下来问" |
| `docs/security.md` Confirmation Requirements（30+ 行表） | `confirmation-matrix.md` | **原样搬运** |
| `docs/security.md` Sensitive Data Handling | `secrets-sudo-scope.md` §1 | 转成「正确/错误」对照表 |
| `docs/security.md` Permissions Model（19 条 sudo 表） | `secrets-sudo-scope.md` §2 | **原样搬运** + 补 `security.sudo.extraRules` 落地代码 |
| `internal/tools/executor.go` 三 Executor | `multi-node.md` §1 | 接口 → 三档指令约定 |
| `internal/tools/executor.go` `needsSudo` | `multi-node.md` §4 | 路径感知规则 → 文字表 |
| `internal/tools/executor.go` `isMutatingCommand` | `multi-node.md` §5 | **红线命令表原样搬** |
| `docs/tools.md` `nixos`（20 action） | `rebuild-generations-upgrades.md` | action → CLI 命令 |
| `docs/tools.md` `container`（11 action） | `containers-mounts-gpu.md` §1 | action → podman 命令；保留 stack 命名与 `/srv/` 边界 |
| `docs/tools.md` `mount`（5 action） | `containers-mounts-gpu.md` §2 | 保留 `x-systemd.automount` 铁律 |
| `docs/tools.md` `nvidia`（4 action） | `containers-mounts-gpu.md` §3 | 补「enable 要写什么配置」 |
| `docs/tools.md` `amdgpu`（4 action） | `containers-mounts-gpu.md` §4 | 保留 APU ROCm/GTT 全套 |
| `docs/tools.md` `scheduler`（6 action） | `containers-mounts-gpu.md` §5 | 保留 `Persistent=true` |
| `docs/tools.md` `users`/`network`/`logs`/`files`/`clock`/`system_info` | `rebuild-generations-upgrades.md` §6-§9 | 合并成命令速查 |
| `docs/content/multi-node.md` | `multi-node.md` §2-§3 | node 配置表 + SSH 参数 |
| `nixos-management-skill/anti-patterns.md` + Discourse #80199 | `anti-patterns.md` | 合并扩充到 8 类 |

## 3. 安装方式（各宿主）

| 宿主 | 命令 |
|---|---|
| **Hermes Agent** | `cp -r skills/nixos-ops ~/.hermes/skills/` + `cp AGENTS.md .hermes.md`（或 `/etc/nixos/AGENTS.md`） |
| **OpenClaw** | `cp -r skills/nixos-ops ~/.openclaw/skills/` + `cp AGENTS.md /etc/nixos/AGENTS.md` |
| **OpenAI Codex** | `cp AGENTS.md /etc/nixos/AGENTS.md` + `cp -r skills/nixos-ops /etc/nixos/skills/` |
| **Claude Code** | `cp -r skills/nixos-ops ~/.claude/skills/` |
| **通用（读 AGENTS.md）** | 放 NixOS 配置仓库根目录 |

**Hermes 优先级提示**：`.hermes.md` > `AGENTS.md` > `CLAUDE.md` > `.cursorrules`。
要覆盖某条规则，写在 `.hermes.md` 里。

## 4. ⚠️ 转换后失效的 6 项（必须宿主持平）

| # | nixi 的保证 | 为何失效 | 宿主持平 |
|---|---|---|---|
| 1 | **工具级确认门**：`confirmed` 不在 tool schema 里，LLM 无法伪造 | 通用 agent 的 schema 由宿主生成，skill 改不了 | Hermes `trust: untrusted` + 宿主审批；Codex approval mode；或变更全走受限 MCP |
| 2 | **MonitoredExecutor 硬拒变更** | skill 只能"要求"只读 | `tumf/mcp-shell-server` 的 `ALLOW_COMMANDS` 只放只读命令；或 MCP `--read-only` |
| 3 | **`/srv/` 边界工具层拒绝** | 同理 | `ALLOW_PATTERNS` 把路径写进正则 |
| 4 | **凭据永不进 LLM 上下文**（掩码输入直传工具） | 依赖宿主 secret 管理 | 宿主支持 secret 注入，或手动输入；skill 只能规范"别写进配置" |
| 5 | **输出自动脱敏** | skill 只能要求 | 宿主工具输出过滤 + agent 自觉 |
| 6 | **Levenshtein 节点纠错 / 批量单次确认 / executor 自动 sudo 前置** | 纯 Go 便利功能 | 由 agent 按 skill 规则**模拟**（规则已写明） |

> **最省力组合**：`AGENTS.md`（判断）+ `tumf/mcp-shell-server` + 窄 `ALLOW_PATTERNS`（强制）。

## 5. 转换中刻意没做的三件事

1. **没搬 nixi 的 Web UI / TUI / SQLite 记忆 / LLM 客户端** —— 那是 agent 本体，不是规范。
2. **没搬 nixi 的 `nixos-rebuild` 具体工具名** —— 通用 agent 走 shell，需要的是 CLI 命令。
3. **没把 skill 写成"自动执行"语气** —— nixi 的确认门靠代码，port 只能靠规则，所以
   全文用祈使 + 禁止句式，不用"可以自动"这类描述。

## 6. 坑与反直觉

1. **「skill 装了 = 安全了」是错的。** skill 是 prompt 的一部分，模型可以不遵守。**强制力必须来自
   执行层**（受限 MCP / 宿主审批 / OS 层 sudo）。
2. **nixi 的确认矩阵搬到 skill 后反而变严了** —— 原版在 `internal/tools/executor.go` 里
   `isMutatingCommand` 只拦 6 类命令子集，而 `docs/security.md` 的表列了 30+ 项。port 取了
   更严的那份（文档版），这是有意的。
3. **别把 `AGENTS.md` 叫成 `.hermes.md` 之外再放一份 `CLAUDE.md`** —— Hermes 优先级
   `.hermes.md` > `AGENTS.md`，两份并存时以 `.hermes.md` 为准，容易造成"改了没生效"的困惑。
4. **`security.sudo.extraRules` 里的绝对路径**（如 `/run/current-system/sw/bin/tee`）会随
   NixOS 版本与 profile 变化，落地前用 `which tee` 逐条确认真实路径——写错会让 sudo 规则
   静默失效（不报错但就是不生效）。
5. **AGPL-3.0 的是 nixi 的代码**，不是这些规范文本；规范内容来自 MIT/LGPL/Apache 的上游文档。
   但为免争议，port 内含 nixi 独有的设计描述（如 `isMutatingCommand` 的具体列表）已标注来源。

## 7. 未核实 / 存疑

| 项 | 状态 |
|---|---|
| `~/.hermes/skills/` 是否为 Hermes 真实 skill 路径 | **未核实**。本机 Hermes 的实际 skill 目录未确认，落地前先 `ls ~/.hermes/` 看一眼 |
| `~/.openclaw/skills/` 路径 | **未核实** |
| Hermes 是否要求 SKILL.md 有特定 frontmatter 字段 | **未核实**（port 用了通用 `name`/`description`/`version`） |
| port 加载后的实际 token 占用 | 未实测 |
| `security.sudo.extraRules` 里的 `/run/current-system/sw/bin/*` 路径在本机是否一致 | 未核实 |

## 8. 相关文件

| 文件 | 说明 |
|---|---|
| `nixi-port/` | **本 port 的产物（9 文件 / 42,004 B）** |
| `kb/nixos-llm-tooling-layers.md` | NixOS × LLM 工具四层全景 |
| `kb/nixi-nixos-agent-vs-general-agents.md` | Nixi 项目剖析与平替可行性 |
| `.nixi-src/` | 转换时直读的 nixi 源文档（10 个文件） |
