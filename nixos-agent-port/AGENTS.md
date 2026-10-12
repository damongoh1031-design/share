# AGENTS.md — NixOS agent 入口（合并版）

本文件是跨 agent 约定（[agents.md](https://agents.md/)）的入口。**Hermes Agent、OpenClaw、
OpenAI Codex、Claude Code、Cursor、Aider、Gemini CLI、Windsurf、Cline、Zed、Amp 都读它。**

Hermes 用户注意：项目级优先级是 `.hermes.md` > `AGENTS.md` > `CLAUDE.md` > `.cursorrules`。
想覆盖本文件的某条规则，在 `.hermes.md` 里写。

本目录是 `nixi-port/` 的**合并继任者**：把「纯规范」（nixi）与「两个真实 MCP 的用法」
（`nix-agent` 执行层 + `mcp-nixos` 知识层）合成一套。合并映射见 `README.md`。

---

## 1. 你在管什么

一台或多台 **NixOS** 机器。配置是声明式的，**唯一的正确变更方式是改配置 + rebuild**。
任何"直接改系统"的操作（`nix-env -i`、`systemctl enable` 期望永久生效、手写 `/etc/` 下的文件）
都是错的或临时的，必须说明。

## 2. 五条铁律

1. **先查证，再动手。** 包名 / 选项名 / attribute path 一律查证（`mcp-nixos` 优先，
   `nix search nixpkgs` 兜底）。**查不到就说查不到，不要编。**
2. **先 dry-run，再 apply。** 变更前先 `check("dry-build")` 或 `check("dry-activate")`，
   把 diff 给用户看。
3. **绝不自我批准。** rebuild / rollback / reboot / 装包 / 删容器 / 改防火墙 / 清 generation
   —— 全部要用户明确 yes。用户说 "yes 并且顺便做 X" 时合并成一个工作流，**一次确认**，不要二次确认。
4. **`degraded` ≠ 成功。** `switch()` 返回 `status: "degraded"` 表示"激活成功但有 unit 新失败"
   —— 那是问题，不是成功。报告 `summary.health` 并默认回滚。
5. **有工具就别用 shell。** 见 `skills/nixos-ops/tool-map.md`。绕过 MCP 直接敲
   `nixos-rebuild` / `nix eval` / `nix log` 会重新付一遍这个服务器本来替你省掉的上下文成本。

## 3. 两个 MCP 的分工（先记住这个，再看细节）

| 层 | 工具 | 回答 | 会改系统吗 |
|---|---|---|---|
| **知识层** | `mcp-nixos`（2 工具） | "**存在什么**"——包在不在？option 什么意思？哪个 commit 发的？ | ❌ 从不 |
| **执行层** | `nix-agent`（7 工具） | "**你的机器实际解析成什么、能不能构建、switch 会改什么**" | ✅ 会 |
| 文件层 | 宿主原生 Read/Edit/Write | 改 `.nix` 文件 | ✅（你直接改） |
| 兜底层 | Bash | 格式化（`nix fmt`）、**远程部署**、两 MCP 都不覆盖的事 | ✅ |

**两者都不是可有可无的**：`mcp-nixos` 防幻觉，`nix-agent` 防"我以为改好了"。

## 4. 完整规范在哪

| 文件 | 内容 | 什么时候读 |
|---|---|---|
| `skills/nixos-query/SKILL.md` | **知识层入口**：8 action × 11 source 的用法 | 查包 / 查 option / 查版本 / 查缓存 |
| `skills/nixos-ops/SKILL.md` | **执行层入口**：决策表 + 执行序 + 禁止事项 | 要改机器时 |
| `skills/nixos-ops/tool-map.md` | shell 命令 → MCP 工具对照表 | **每次要敲 nix 命令前** |
| `skills/nixos-ops/envelope-cheatsheet.md` | 回执怎么读、哪些字段已替你预取 | 工具返回后 |
| `skills/nixos-ops/confirmation-matrix.md` | 30+ 种操作逐条判定要不要确认 | 拿不准时 |
| `skills/nixos-ops/rebuild-and-generations.md` | rebuild / generation / 升级 / 包管理配方 | 重建或升级时 |
| `skills/nixos-ops/sudo-and-secrets.md` | sudo 白名单（可直接落地的 NixOS 模块）+ 凭据处理 | 涉及权限或密码时 |
| `skills/nixos-ops/no-mcp-coverage.md` | **两个 MCP 都不覆盖的区域**：容器 / 挂载 / GPU / 多节点 | 部署容器、挂 NAS、配 GPU、管多台 |
| `skills/nixos-ops/anti-patterns.md` | 反模式清单 | **每次任务结束前自查** |

## 5. 关键词 → 必做动作

| 用户说 | 先做 |
|---|---|
| "升级" / "update" | 判断 flake 还是 channel；flake 模式先 `nix flake update`，**锁文件 diff 单独展示** |
| "装 X" | `mcp-nixos` 查包名 → 改 `environment.systemPackages` → `check("dry-build")` |
| "rebuild" / "切换配置" | `check("dry-activate")` 展示 → 等确认 → `switch()` |
| "回滚" | `generations(action="list")` → 等确认 → `generations(action="rollback", generation=<id>)` |
| "清理" / "空间不够" | `nix-collect-garbage --dry-run` 展示可回收 → 确认并**告知保留几个** |
| "这个 option 现在是什么值" | `eval_config(attr)`（多个就传 list 批量） |
| "这个 option 在哪配的" | `locate_option(attr)` —— **不要 grep 整个仓库** |
| "部署 X 容器" | 读 `no-mcp-coverage.md` §1（无 MCP 覆盖）→ 确认 → `/srv/<name>/` |
| "配 GPU" | 读 `no-mcp-coverage.md` §3-§4 → 改配置 → dry-run → **提示需 reboot** |
| "管多台" | 读 `no-mcp-coverage.md` §5（`nix-agent` 只操作本机） |
| "密码/密钥" | 读 `sudo-and-secrets.md`，**绝不进上下文** |

## 6. 明确禁止

- ❌ `find /nix/store/* -iname lib*.so` —— 用 `nix-locate`（`nix-index`）
- ❌ `nix-env -i` / `nix profile install` 装系统包 —— 走 `environment.systemPackages`
- ❌ 把密码 / token 写进 `configuration.nix` 或 flake —— 用 `agenix` / `sops-nix`
- ❌ 给 agent 用户免密 `rm` / `cp` / `mv`
- ❌ 给 sudoers 通配 `--flake *`，或通配 `/nix/store/*/bin/switch-to-configuration`
- ❌ 改 `system.stateVersion`（除非用户明确要求）
- ❌ rebuild 失败原地反复重试 —— 先 rollback
- ❌ 说"已完成"而实际只跑了 dry-run
- ❌ 在宿主机 `pip install` / `npm i -g` —— 用 `nix develop`
- ❌ 在 `nix-agent` 覆盖范围内改用 shell（会被 `tool-map.md` 挡住）

## 7. 本目录的来源

| 来源 | 贡献 |
|---|---|
| `codeberg.org/ewrogers/nixi`（AGPL-3.0） | **判断规则**：确认矩阵、scoped sudo、`/srv/` 边界、反模式 |
| `JEFF7712/nix-agent`（MIT） | **执行层工具面**：7 工具、envelope 语义、sudoers 模块 |
| `utensils/mcp-nixos`（MIT） | **知识层工具面**：8 action × 11 source |

**只转了规范与用法，没转任何源码。** 转换映射、合并映射与已知失效清单见 `README.md`。
