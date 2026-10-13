---
name: arch-update-guard
description: Arch Linux 更新前检查闸门。当用户说「Arch 要更新吗」「更新前检查一下」「Arch 会不会滚挂」「帮我看看 Arch 有没有需要人工介入的公告」「Arch 更新提醒」，或在 Arch 上准备执行 pacman -Syu 之前使用。只读检查 + 结构化报告，零第三方依赖。
---

# arch-update-guard · Arch 更新前检查闸门

## 这个 skill 解决什么

Arch 是滚动发行版，**官方明确不提供也不推荐无人值守全自动更新** —— 因为有些更新需要人工判断（改配置、重新 enroll TPM2、换包名）。全自动 `pacman -Syu --noconfirm` 遇到这类更新会直接把系统搞坏。

所以正确目标是：**自动化检查 + 人工确认执行**。本 skill 负责前半段。

## 快速用法

```bash
PY=python3   # Arch 上系统自带
SK="<本 skill 目录>/scripts/arch_update_guard.py"

# 全套更新前检查（人类可读）
"$PY" "$SK" check

# 结构化输出，供 agent 解析
"$PY" "$SK" json

# 只看需要人工介入的公告
"$PY" "$SK" news

# 打快照（写操作，需 --yes）
"$PY" "$SK" snapshot --yes

# 不依赖 Arch 环境的解析逻辑自检
"$PY" "$SK" selftest
```

## 退出码语义（agent 应据此判断）

| 退出码 | 含义 | agent 应采取的行动 |
|---|---|---|
| `0` | 一切正常 | 可以提示用户执行 `sudo pacman -Syu` |
| `1` | 有 WARN 项 | 先引导用户处理 warn 项（磁盘 / 快照 / 内核兜底） |
| `2` | **有 BLOCK 项** | **不要建议直接更新** —— 必须先读公告 / 处理阻塞 |
| `3` | 环境错误 | 非 Arch，或缺少工具 |

## 检查项清单

| id | 检查内容 | 何时会 BLOCK |
|---|---|---|
| `env` | 是否 Arch 系 | 非 Arch |
| `news` | **Arch News 里的「需人工介入」公告** | 最近 15 条有命中 |
| `updates` | 待更新包（`checkupdates`） | 不会 BLOCK，但会标出高危包 |
| `disk` | 磁盘空间 | 任一挂载点 ≥95% |
| `pacnew` | `/etc` 下的 `.pacnew`/`.pacsave` 遗留 | 不会 BLOCK |
| `services` | `systemctl --failed` | 不会 BLOCK |
| `snapshot` | btrfs + snapper + snap-pac 是否就绪 | 不会 BLOCK |
| `kernel` | 是否有 `linux-lts` 备用内核 | 不会 BLOCK |
| `cache` | `/var/cache/pacman/pkg` 是否还有降级弹药 | 不会 BLOCK |
| `keyring` | `archlinux-keyring` + wkd-sync timer | 不会 BLOCK |

**高危包**（出现在待更新列表里会额外提示）：
`linux` / `linux-lts` / `linux-zen` / `systemd` / `glibc` / `pacman` / `mkinitcpio` / `archlinux-keyring` / `nvidia*` / `linux-firmware` / `plasma-workspace` / `kwin` / `gnome-shell` / `grub` / `refind`

## 建议的 agent 工作流

用户说「我要更新 Arch」时，按这个顺序：

1. **先跑检查**
   ```bash
   python3 arch_update_guard.py json
   ```
2. **看退出码与 `level` 字段**
   - `BLOCK` → 把 `news` 里的 `hits` 逐条展示给用户，**明确说「先读完这些公告再更新」**，不要替用户跳过
   - `WARN` → 列出 warn 项，问用户是否要先处理（尤其 `snapshot` 和 `kernel` 两项是兜底）
3. **若一切就绪**，提示用户：
   ```bash
   sudo pacman -Syu     # 注意：绝不能用 -Sy
   ```
4. **更新后**提醒跑：
   ```bash
   systemctl --failed
   sudo pacdiff
   sudo checkservices      # archlinux-contrib
   sudo rebuild-detector
   ```

## 硬约束（不要违反）

1. **绝不代替用户执行 `pacman -Syu`。** 这是需要用户本人判断的操作。
2. **绝不建议 `pacman -Sy` 或 `pacman -Sy <pkg>`。** 会造成 partial upgrade，是 Arch 最常见的毁系统方式。Arch Wiki 明确警告。
3. **BLOCK 级新闻不能"帮用户跳过"。** 如果用户说"不管了直接更新"，仍然要把公告内容完整展示一次再让用户决定。
4. **`snapshot` 是写操作**，必须显式 `--yes`；agent 不要在未获用户同意时调用。
5. **不要在非 Arch 系统上假装检查通过** —— 脚本会返回 BLOCK，如实转达。

## 与 arch-mcp 的分工

| | `arch-mcp`（社区项目，59★） | 本 skill |
|---|---|---|
| 依赖 | Python 3.11+ 与 `uvx` | 系统 Python 3 |
| 接入 | 需配 MCP（`~/.workbuddy-ai/mcp.json`） | 直接跑脚本 |
| 覆盖 | 12+ 工具，含写操作（install/remove） | 只读检查 + 快照 |
| 更新 | 最后推送 2026-03（8 个月未动） | 本 skill 新写 |
| 适合 | 想要完整 MCP 生态 | 想要最小可用的检查闸门 |

两者可并存。若用户想要「完整 MCP 一站式」，指导他配置 `arch-mcp`：
```json
{ "mcpServers": { "arch-linux": { "command": "uvx", "args": ["arch-ops-server"] } } }
```
注意它是**非官方社区项目**，且含提权写操作。

## 依赖

- **必需**：Python 3.8+（Arch 自带）
- **推荐**：`pacman-contrib`（提供 `checkupdates`）、`snapper` + `snap-pac`（快照兜底）、`linux-lts`（备用内核）
- 缺失时会降级为 WARN，不会崩溃

## 安全说明

- **纯只读**（除 `snapshot` 子命令，且需 `--yes`）
- 零第三方依赖，只用 Python 标准库
- 网络访问仅 `https://archlinux.org/feeds/news/`（读取公开 RSS）
- 不读取、不外发任何本地文件内容
