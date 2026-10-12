# nixi-port — 把 nixi 的规范搬到 Hermes / OpenClaw / Codex

**一句话**：`ewrogers/nixi` 是一个只会 NixOS 的专用 agent（Go，13 个硬编码工具）。
这里把它的**规范**抽出来，转成任何通用 agent 都能加载的 skill —— 不要它的代码，
要它的判断规则。

## 装到哪

### Hermes Agent（项目级）

```bash
# 放进你的 NixOS 配置仓库根目录
cp -r nixi-port/skills/nixos-ops ~/.hermes/skills/          # 用户级
cp nixi-port/AGENTS.md /etc/nixos/AGENTS.md                 # 或项目级
cp nixi-port/AGENTS.md .hermes.md                           # Hermes 最高优先级文件名
```

### OpenClaw

```bash
cp -r nixi-port/skills/nixos-ops ~/.openclaw/skills/
cp nixi-port/AGENTS.md /etc/nixos/AGENTS.md
```

### OpenAI Codex（读 AGENTS.md）

```bash
cp nixi-port/AGENTS.md /etc/nixos/AGENTS.md
cp -r nixi-port/skills/nixos-ops /etc/nixos/skills/
```

### Claude Code

```bash
cp -r nixi-port/skills/nixos-ops ~/.claude/skills/
# 或作为插件市场源
```

### 通用（任何读 AGENTS.md 的 agent）

把 `AGENTS.md` 放在 NixOS 配置仓库根目录即可，它会指向 `skills/nixos-ops/`。

## 目录结构

```
nixi-port/
├── AGENTS.md                        # 跨 agent 入口（agents.md 约定）
├── README.md                        # 本文件
└── skills/
    └── nixos-ops/
        ├── SKILL.md                 # 入口：决策表 + 确认矩阵 + 执行顺序 + 禁止事项
        ├── confirmation-matrix.md   # 30+ 操作逐条判定要不要确认
        ├── rebuild-generations-upgrades.md   # rebuild/generation/升级/包管理配方
        ├── secrets-sudo-scope.md    # 凭据处理 + scoped sudo 白名单 + NixOS 落地配置
        ├── containers-mounts-gpu.md # Podman / NFS-SMB / NVIDIA / AMD GPU 配方
        ├── multi-node.md            # 本地 / SSH / 只读三档 + 红线命令表
        └── anti-patterns.md         # 8 类反模式，任务结束前自查
```

## 转换映射：nixi 的什么 → 这里的什么

| nixi 的部件（Go 实现） | 转成 | 说明 |
|---|---|---|
| `AGENTS.md` 的 Design Principles | `AGENTS.md` + `SKILL.md` §0-§5 | 铁律原文保留 |
| `docs/security.md` Confirmation Requirements | `confirmation-matrix.md` | **30+ 行矩阵原样搬** |
| `docs/security.md` Sensitive Data Handling | `secrets-sudo-scope.md` §1 | 凭据规则 + 正确/错误对照表 |
| `docs/security.md` Permissions Model | `secrets-sudo-scope.md` §2-§4 | **sudo 白名单原样 + NixOS 落地代码** |
| `docs/tools.md` `nixos` 工具 | `rebuild-generations-upgrades.md` | 13 个 action → CLI 命令 |
| `docs/tools.md` `container` / `mount` | `containers-mounts-gpu.md` §1-§2 | 含 stack 命名与 `/srv/` 边界 |
| `docs/tools.md` `nvidia` / `amdgpu` | `containers-mounts-gpu.md` §3-§4 | 含 APU 的 ROCm/GTT 处理 |
| `docs/tools.md` `scheduler` | `containers-mounts-gpu.md` §5 | systemd timer |
| `docs/multi-node.md` + `internal/tools/executor.go` | `multi-node.md` | Executor 三档 → 指令约定 + 红线表 |
| `docs/tools.md` `users` / `network` / `logs` / `files` | `rebuild-generations-upgrades.md` §6-§9 | |
| （社区补充） | `anti-patterns.md` | 合并 `nixos-management-skill` 的 anti-patterns + Discourse #80199 |

## ⚠️ 转换后失效的部分（必须由宿主持平）

nixi 的几条安全保证是**在 Go 代码里强制**的，skill 只是文字，**没有强制力**。
要真正等价，必须自己配宿主侧：

| nixi 的保证 | 为什么在 skill 里失效 | 宿主持平方案 |
|---|---|---|
| **工具级确认门**：`confirmed` 参数不出现在 tool schema，LLM 无法伪造 | 通用 agent 的 tool schema 是宿主生成的，skill 改不了 | Hermes `trust: untrusted` + 宿主审批；Codex approval mode；或所有变更走受限 MCP |
| **MonitoredExecutor 硬拒变更** | skill 只能"要求"agent 只读，不能阻止它 | `tumf/mcp-shell-server` 的 `ALLOW_COMMANDS` 只放只读命令；或 MCP 的 `--read-only` |
| **`/srv/` 边界在工具层拒绝** | 同理 | `ALLOW_PATTERNS` 把路径写进正则 |
| **凭据永不进 LLM 上下文**（掩码输入直传工具） | 靠宿主的 secret 管理 | 宿主要么支持 secret 注入，要么你手动输入；skill 只能规范"不要写进配置" |
| **输出自动脱敏** | skill 只能要求，不能执行 | 宿主工具输出过滤 + agent 自觉 |
| **Levenshtein 节点名纠错 / 批量单次确认 / executor 自动 sudo 前置** | 纯 Go 便利功能 | 由 agent 用 skill 里的规则**模拟**（已在文中写明规则） |

**结论**：这个 port 给你的是**正确的判断规则**；**强制力必须自己补**。
最省力的组合：`AGENTS.md`（判断）+ `tumf/mcp-shell-server` + 窄 `ALLOW_PATTERNS`（强制）。

## 许可证

- 本 port 是**转换产物**，不是 nixi 代码的复制品（未复制任何 Go 源码）。
- 内容来源的许可：NixOS Manual / Home Manager / nix-darwin / `nixos-management-skill` 为 **MIT**；
  Nix Manual 为 **LGPL-2.1**；devenv 为 **Apache-2.0**；NixOS Wiki 为 **MIT**。
- 原项目 `nixi` 本身是 **AGPL-3.0** —— 本 port 不含其代码，故不继承 AGPL。
- 商业/分发前建议把本 port 整体标为 MIT 并保留上述来源声明。

## 上游

- 源仓库：<https://codeberg.org/ewrogers/nixi>（0★ / 0 fork / 1 watcher，
  最后提交 2026-03-31，仅 v0.1.0，无测试）
- 源文档：`AGENTS.md`（6,786 B）、`docs/content/{architecture,tools,security,configuration,multi-node,getting-started}.md`
- 转换日期：2026-10-12
