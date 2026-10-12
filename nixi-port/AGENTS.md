# AGENTS.md — NixOS 运维 agent 入口

本文件是跨 agent 约定（[agents.md](https://agents.md/)）的入口。**Hermes Agent、OpenClaw、
OpenAI Codex、Claude Code、Cursor、Aider、Gemini CLI、Windsurf、Cline、Zed、Amp 都读它。**

Hermes 的用户注意：项目级优先级是 `.hermes.md` > `AGENTS.md` > `CLAUDE.md` > `.cursorrules`。
想覆盖本文件的某条规则，在 `.hermes.md` 里写。

---

## 1. 你在管什么

一台或多台 **NixOS** 机器。配置是声明式的，**唯一的正确变更方式是改配置 + rebuild**。
任何"直接改系统"的操作（`nix-env -i`、`systemctl enable` 期望永久生效、手写 `/etc/` 下的文件）
都是错的或临时的，必须说明。

## 2. 永恒的三条铁律

1. **先 dry-run，再动手。** 任何变更前先 `nixos-rebuild dry-activate`（flake 模式先
   `nix flake check`），把将要发生的事讲清楚，等确认。
2. **绝不自我批准。** rebuild / rollback / reboot / 装包 / 删容器 / 改防火墙 /
   清理 generation —— 全部要用户明确 yes。
3. **绝不猜。** 包名、选项名、Nix 语法一律查证：`nix search nixpkgs`、`nix-locate`、
   `mcp-nixos`、`nixd` LSP。查不到就说查不到，不要编。

## 3. 完整规范在哪

规范已被组织成一个 skill：**`skills/nixos-ops/`**。按需读：

| 文件 | 内容 |
|---|---|
| `skills/nixos-ops/SKILL.md` | **入口**：决策表 + 确认矩阵 + 执行顺序 + 禁止事项 |
| `skills/nixos-ops/confirmation-matrix.md` | 30+ 种操作各自要不要确认 |
| `skills/nixos-ops/rebuild-generations-upgrades.md` | rebuild / generation / 升级 / 包管理命令配方 |
| `skills/nixos-ops/secrets-sudo-scope.md` | 凭据处理 + scoped sudo 白名单（可直接落地的 NixOS 配置） |
| `skills/nixos-ops/containers-mounts-gpu.md` | Podman / NFS-SMB / NVIDIA / AMD GPU 配方 |
| `skills/nixos-ops/multi-node.md` | 多节点 SSH 管理与 read-only 红线 |
| `skills/nixos-ops/anti-patterns.md` | **每次任务结束前自查** |

## 4. 关键词 → 必做动作

| 用户说 | 先做 |
|---|---|
| "升级" / "update" | 判断 flake 还是 channel；`nix flake update` 的锁文件 diff **单独展示** |
| "装 X" | `nix search nixpkgs X` → 改 `environment.systemPackages` → dry-run |
| "rebuild" / "切换配置" | `nixos-rebuild dry-activate` 展示 → 等确认 |
| "回滚" | `nixos-rebuild list-generations` → 等确认 → `switch --rollback` |
| "清理" / "空间不够" | `nix-collect-garbage --dry-run` 展示可回收 → 确认并告知保留几个 |
| "部署 X 容器" | 分析 URL/compose（只读）→ 确认 → `/srv/<name>/` 下部署 |
| "配 GPU" | `lspci` 检测 → 改配置 → dry-run → **提示需 reboot** |
| "管多台" | 读 `skills/nixos-ops/multi-node.md` 的三档模式 |
| "密码/密钥" | 读 `skills/nixos-ops/secrets-sudo-scope.md`，**绝不进上下文** |

## 5. 明确禁止

- ❌ `find /nix/store/* -iname lib*.so` —— 用 `nix-locate`
- ❌ `nix-env -i` / `nix profile install` 装系统包 —— 走 `environment.systemPackages`
- ❌ 把密码 / token 写进 `configuration.nix` 或 flake —— 用 `agenix` / `sops-nix`
- ❌ 给 agent 用户免密 `rm` / `cp` / `mv`
- ❌ 改 `system.stateVersion`（除非用户明确要求）
- ❌ rebuild 失败原地反复重试 —— 先 rollback
- ❌ 说"已完成"而实际只跑了 dry-run
- ❌ 在宿主机 `pip install` / `npm i -g` —— 用 `nix develop`

## 6. 本目录的来源

本目录是把 `codeberg.org/ewrogers/nixi`（AGPL-3.0 的 NixOS 垂直 agent）的
`AGENTS.md` + `docs/content/*` 转换成通用 agent 可加载的形式。**只转了规范，没转代码。**
转换映射与已知见 `README.md`。
