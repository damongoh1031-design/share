---
id: arch-anti-breakage-guide
title: Arch Linux 防滚挂指南：预警 / 提醒 / 检查 / Agent 一站式
tags: [arch-linux, rolling-release, pacman, snapshot, btrfs, systemd-timer, mcp, agent, manual-intervention]
created: 2026-10-13
updated: 2026-10-13
version: 1.0.0
status: stable
source: 2 个并行子代理 + 主调研员对全部工具做 AUR RPC / 官方仓库 API / GitHub API / PyPI 独立实测（2026-10-13）
confidence: 已核实
---

# Arch 防滚挂指南（2026-10）

## 一句话结论

**Arch 官方不提供也不推荐无人值守自动更新**，因为 manual intervention 公告意味着需要人工判断。正确目标是「**自动化检查 + 人工确认执行**」。三件套：**News RSS + `arch-manwarn`（硬拦）+ `snap-pac` 快照兜底**；agent 一站式可用现成的 `arch-mcp` 或本仓产出的 `arch-update-guard` skill。

---

## 1. 官方预警渠道（实测）

| 渠道 | URL | 状态 |
|---|---|---|
| **News RSS/Atom** | `https://archlinux.org/feeds/news/` | ✅ HTTP 200，16,235 字节 |
| Feed 索引 | `https://archlinux.org/feeds/` | ✅ 含 News / Wiki changes / 包更新 / ISO |
| 包更新 feed | `https://archlinux.org/feeds/packages/x86_64/` | ✅ 可按 arch/repo/包名定制 |
| arch-announce 邮件列表 | `lists.archlinux.org` | ✅ = News 镜像，与 RSS 同源，二选一 |
| arch-security 邮件列表 | — | ⚠️ **已停摆**（最后活动 2025-06-13，>16 个月） |
| News JSON API | — | ❌ **不存在**，只有 RSS/Atom |

```bash
# 最该订阅的：只看需人工介入的公告
curl -s https://archlinux.org/feeds/news/ | grep -i "manual intervention"
```

---

## 2. 新闻门禁工具（pacman hook 类）

原理相同：**pacman 事务前检查未读新闻，有则中断升级**。

| 工具 | 语言 | star | 最后更新 | 拦截策略 | 状态 |
|---|---|---|---|---|---|
| **`arch-manwarn`** | Rust | 25 | 2026-08-02 | **只拦 manual intervention 关键词** | ✅ AUR v1.4.1-1，9 votes ← **推荐** |
| `newscheck` | Rust | 6 | 2026-05-28 | 拦所有未读新闻 | ⚠️ AUR v0.2.5-1，仅 1 vote |
| `informant` | Python | 429 | 2025-06-07 | 拦所有未读新闻 | ❌ **已从 AUR 下架** |

> ⚠️ **重要修正**：`informant` GitHub 仓库还在（429★），但 **AUR 包已下架**（AUR RPC 实测 `NOT_IN_AUR`），且最后提交停在 2025-06-07。**网上大量教程仍推荐 informant，那些教程已过期。**
>
> ✅ 改用 `arch-manwarn` —— 只拦真正危险的，误报率低得多，Arch Wiki 也点名了它。
> ⚠️ `arch-manwarn` 与 `informant` 冲突（Conflicts），不能共存。

---

## 3. 更新提醒方案

### 检查工具

| 工具 | 来源 | 说明 |
|---|---|---|
| **`checkupdates`** | `pacman-contrib`（extra 1.13.1-1） | **用临时 DB 检查，不污染本地库** |
| **`arch-update`** | AUR v4.4.3-1（74 votes，GitHub 460★，**2026-10-12 更新**） | 检查更新+新闻+孤儿+pacnew+缓存+keyring+服务，带托盘通知 ← **最活跃** |
| `paru -Qua` / `yay -Qua` | AUR | 只查 AUR 已装包 |
| `arch-audit` | extra 0.2.0-5 | ⚠️ **数据源已停摆**，当前不可信 |

**`checkupdates` 退出码**（写 timer 的关键）：

| 码 | 含义 |
|---|---|
| `0` | **有更新**（并输出列表） |
| `1` | 未知失败 |
| `2` | **无更新** |

### systemd user timer 模板

```ini
# ~/.config/systemd/user/checkupdates.service
[Unit]
Description=Check for Arch updates
[Service]
Type=oneshot
ExecStart=/usr/bin/bash -c 'updates=$(checkupdates 2>/dev/null); [ -n "$updates" ] && notify-send -u normal -i dialog-warning "Arch 更新可用" "$(printf "%s\n" "$updates" | wc -l) 个包:\n$updates"'
```
```ini
# ~/.config/systemd/user/checkupdates.timer
[Unit]
Description=Daily Arch update check
[Timer]
OnCalendar=*-*-* 09:00:00
Persistent=true
RandomizedDelaySec=1h
[Install]
WantedBy=timers.target
```
```bash
systemctl --user enable --now checkupdates.timer
```

### ⚠️ 最大的坑：systemd 里发不出桌面通知

system 级 service / cron **没有** `DISPLAY` 和 `DBUS_SESSION_BUS_ADDRESS`，`notify-send` 报 `The connection is closed`。

**官方推荐解法**（Arch Wiki）：用 `systemd-run` 进入用户会话
```bash
systemd-run --machine=<user>@.host --user notify-send '标题' '正文'
```
user timer 需先导入环境：
```bash
systemctl --user import-environment DISPLAY WAYLAND_DISPLAY DBUS_SESSION_BUS_ADDRESS
```
或显式写：
```ini
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
Environment=DISPLAY=:0
```

---

## 4. 兜底机制（真正「不会滚挂」的部分）

| 手段 | 包 | 实测状态 |
|---|---|---|
| **自动快照** | **`snap-pac`** | ✅ **官方 extra 3.0.1-3**（不是 AUR！）pacman 事务前后自动打 btrfs 快照 |
| 快照管理 | `snapper` | ✅ extra 0.13.2-1 |
| 非 btrfs 快照 | `timeshift` | ✅ extra 26.09.0-1 |
| **备用内核** | `linux-lts` | ✅ core 6.18.56-1（2026-10-12） |
| 保留旧版本 | `paccache` | **默认保留 3 个版本**，`paccache.timer` 每周清理 |
| 降级单包 | `downgrade` | ✅ AUR v12.0.3-1，**910 votes** |
| 降级到任意日期 | ALA `https://archive.archlinux.org/` | 包保留数年 |

```bash
sudo pacman -S snap-pac snapper
sudo snapper -c root create-config /
```

> ⚠️ **snap-pac 已知坑**：pre hook 在 db sync **之后**执行 → 回滚后 pacman 数据库未回滚，可能造成 partial upgrade。回滚后务必检查 `checkupdates` 状态。

> ⚠️ **关键前提**：**不要清空 `/var/cache/pacman/pkg`** —— 这是降级的弹药库。

**pacman Hook 示例**（升级内核前备份 /boot；编号须 <05 以先于 snap-pac）：
```ini
# /etc/pacman.d/hooks/04-backupboot.hook
[Trigger]
Operation = Upgrade
Type = Package
Target = linux
[Action]
Description = Backing up /boot...
When = PreTransaction
Exec = /usr/bin/rsync -avzq --delete /boot /.bootbackup
```

---

## 5. Agent 一站式方案

### 5.1 现成的：`arch-mcp`

> **修正前序结论**：前序曾认为「Arch 的 AI 生态基本为零」，**不成立**。

| 项 | 值 |
|---|---|
| 仓库 | `nihalxkumar/arch-mcp` — 59★，Python，最后推送 2026-03-10 |
| PyPI | `arch-ops-server` — v3.4.0，17 releases，最后上传 2026-02-12 |
| 许可 | GPL-3.0 / MIT 双许可 |
| 安装 | `uvx arch-ops-server`（需 Python 3.11+） |
| 声明 | **非官方社区项目** |

**关键工具**：`check_updates_dry_run` / `get_latest_news` / **`check_critical_news`** / **`get_news_since_last_update`** / `check_disk_space` / `check_failed_services` / `check_database_freshness` / `optimize_mirrors` / `analyze_pkgbuild_safety` / `install_package_secure` / `query_package_history`

**⭐ 自带 `safe_system_update` Prompt**：检查关键新闻 → 验证磁盘空间 → 列出更新 → 检查服务 → 给建议

接入（`~/.workbuddy-ai/mcp.json`）：
```json
{ "mcpServers": { "arch-linux": { "command": "uvx", "args": ["arch-ops-server"] } } }
```

⚠️ 三点注意：① 社区项目，安全自负 ② **最后更新 2026-03，8 个月未动** ③ 含 `install_package_secure`/`remove_packages` 等**写操作且需提权**，建议先用只读工具。

### 5.2 自建的：`arch-update-guard` skill

本仓产出，零依赖（系统 Python 3），无需 MCP 配置。

```bash
python3 arch_update_guard.py check      # 全套更新前检查
python3 arch_update_guard.py json       # JSON 输出供 agent 解析
python3 arch_update_guard.py news       # 只看需人工介入的公告
python3 arch_update_guard.py snapshot --yes   # 打快照
python3 arch_update_guard.py selftest   # 解析逻辑自检（不需 Arch）
```

**退出码**：`0` 正常 / `1` 有 WARN / `2` 有 BLOCK（别更新）/ `3` 环境错误

**10 项检查**：环境 / News 公告 / 待更新包 / 磁盘 / pacnew / failed 服务 / 快照就绪 / 备用内核 / 包缓存 / 密钥环

**位置**：`skills/arch-update-guard/`

---

## 6. 真实滚挂案例（2025-2026）

| 日期 | 事件 | 原因 | 避免 |
|---|---|---|---|
| 2025-06-20 | Plasma 6.4 + X11 | 默认只装 wayland 会话 | 装 `plasma-x11-session kwin-x11` |
| 2025-06-21 | linux-firmware 拆分 | 幽灵文件冲突 | `pacman -Rdd linux-firmware && pacman -Syu linux-firmware` |
| 2025-12-20 | NVIDIA 590 | 弃 Pascal(GTX10) | 换 `nvidia-open` 或锁版本 |
| 2026-04-05 | iptables 默认 nft | 默认后端变更（**无报错**） | 装 `iptables-nft` |
| 2026-05-25 | varnish → vinyl-cache | 包改名（7 步迁移） | 按公告迁移 |
| **2026-09-22** | **mkinitcpio ≥42** | 改 PCR 0-7/9/12-14 | **重新 enroll TPM2** |
| 2026-06-12 | AUR 恶意包事件 | 供应链 | 每次读 PKGBUILD diff |

**五种翻车套路**（比案例更重要）：
1. **包改名 / 合并** → 旧包名消失
2. **大版本配置不兼容** → 服务起不来
3. **硬件被除名** → 驱动不支持老硬件
4. **默认行为变更** → **完全无报错**，最阴险
5. **幽灵文件冲突** → 需先卸后装

---

## 可复用操作

```bash
# —— 更新前 9 步 ——
# ① 读新闻 + 找人工介入
curl -s https://archlinux.org/feeds/news/ | grep -iE "<title>|manual intervention" | head -20
# ② keyring 是否需要先更
checkupdates | grep archlinux-keyring
# ③ 镜像同步
sudo reflector --latest 20 --protocol https --age 12 --sort rate --save /etc/pacman.d/mirrorlist
# ④ 磁盘
df -h / /var /boot
# ⑤ 快照
sudo snapper -c root create -d "pre-update $(date +%F)"
# ⑥ 上次遗留 pacnew
sudo pacdiff
# ⑦ 备份包列表
pacman -Qqe > ~/pkglist-$(date +%F).txt
# ⑧ 预览（-d 顺便下载）
checkupdates -d
# ⑨ 正式更新（必须 -Syu）
sudo pacman -Syu

# —— 更新后 ——
systemctl --failed
sudo pacdiff
sudo checkservices          # archlinux-contrib
sudo rebuild-detector
needrestart
journalctl -b -p 3

# —— 降级 ——
sudo pacman -U https://archive.archlinux.org/packages/l/linux/linux-6.16.1.arch1-1-x86_64.pkg.tar.zst
```

---

## 坑与反直觉

1. **`informant` 已从 AUR 下架** —— GitHub 仓库还在，导致大量教程"看起来有效"。AUR RPC 才是真相。
2. **Arch 官方明确反对无人值守全自动更新** —— 不是技术做不到，是 manual intervention 需要人判断。
3. **`checkupdates` 退出码 2 = 无更新**（不是 1）—— 写 timer 时搞反会导致每次都误报。
4. **systemd 里 `notify-send` 静默失败** —— 缺 `DISPLAY`/`DBUS_SESSION_BUS_ADDRESS`，报 `connection is closed`。官方解法是 `systemd-run --machine=...@.host --user`。
5. **`snap-pac` 在官方 extra，不在 AUR** —— 很多人以为要 AUR。
6. **snap-pac 的 pre hook 在 db sync 之后** → 回滚后数据库未回滚，可能 partial upgrade。
7. **`arch-audit` 看起来能用但数据源已死** —— 依赖 2025-06 停发的 Arch ASA。
8. **默认行为变更类更新完全无报错** —— iptables 切 nft 后端就是例子，只能靠读公告发现。
9. **`/var/cache/pacman/pkg` 是降级弹药库** —— 清空它等于放弃降级能力。
10. **`arch-mcp` 存在但 8 个月未更新** —— 用前先验证它读的 RSS/AUR 接口仍有效。

---

## 未核实 / 存疑

| 项目 | 状态 |
|---|---|
| `arch-update` 确切 unit 文件名与配置路径 | 未找到（GitHub 直连被拦），建议装后 `pacman -Ql arch-update` |
| `arch-mcp` 12 个工具当前是否全部可用 | 未实测（需 Arch 环境）；仓库 8 个月未更新 |
| `pacman-notifier`/`pacupdate`/`archup` 等旧工具 | 二手，多为 2011-2015 年产物 |
| `informant` AUR 下架的确切原因与时间 | 未找到，仅确认当前 RPC 返回 `NOT_IN_AUR` |
| Reddit 版更新前 checklist | 未找到，本文 checklist 为 Arch Wiki 官方口径整理 |

---

## 相关文档

- `reports/arch-anti-breakage-guide-2026-10.md` —— 完整报告
- `skills/arch-update-guard/` —— 本次产出的检查闸门 skill
- `kb/distro-operations-analysis.md` —— 各发行版运营对比（含 Arch 风险分析）
- `kb/ai-collaborative-distro-practice.md` —— 发行版 AI 协同实践
- `kb/config-drift-and-residual-files.md` —— 配置漂移与残余文件
