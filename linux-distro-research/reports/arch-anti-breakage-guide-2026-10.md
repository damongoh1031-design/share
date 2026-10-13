# Arch Linux 防滚挂完全指南：预警 · 提醒 · 检查 · Agent 一站式

> **调研时点**：2026-10-13 ｜ **方法**：2 个并行子代理 + 主调研员对全部工具做 AUR RPC / 官方仓库 API / GitHub API / PyPI 独立实测
> **标注**：`[实测]` = 本次独立取到 ｜ `[官方]` = 读到官方原文 ｜ `[二手]` = 第三方 ｜ `[未找到]`

---

## 0. 结论先行

**三个问题的直接答案：**

| 问题 | 答案 |
|---|---|
| **除 Arch News 网页外有什么预警？** | ① **News 有 RSS/Atom**（`archlinux.org/feeds/news/`）② **`arch-manwarn`** 用 pacman hook 硬拦「需要人工介入」的更新 ③ **`archlinux-keyring-wkd-sync.timer`** 默认已启用 |
| **怎么常提醒 + 更新前检查？** | **`checkupdates` + systemd user timer + `notify-send`**（自己搭，约 20 行）或直接用 **`arch-update`**（AUR，460★，2026-10-12 刚更新） |
| **能否用 agent 一站式？** | **能，两条路**：① 现成的 **`arch-mcp`**（59★，PyPI `arch-ops-server`，自带 `safe_system_update` 工作流）② 用 skill 封装（本次已产出，见 §4.2） |

**但必须先说清楚一件事：Arch 官方明确不提供、也不推荐无人值守全自动更新。**

理由不是技术做不到，而是 **manual intervention 公告的存在** —— 有些更新需要人做判断（改配置、重新 enroll TPM2、换包名）。全自动 `-Syu --noconfirm` 遇到这类更新会直接把系统搞坏。**所以正确目标是「自动化检查 + 人工确认执行」，不是「自动化执行」。**

---

## 1. 预警措施（除 Arch News 网页外）

### 1.1 官方渠道（本次全部实测）

| 渠道 | URL / 命令 | 状态 |
|---|---|---|
| **News RSS/Atom** | `https://archlinux.org/feeds/news/` | ✅ `[实测]` HTTP 200，16,235 字节，最新条目 2026-09-22 |
| **Feed 索引页** | `https://archlinux.org/feeds/` | ✅ `[实测]` 列出 News / Wiki changes / 包更新 / ISO 等多个 feed |
| **包更新 feed** | `https://archlinux.org/feeds/packages/x86_64/` | ✅ 可按 arch / repo / 包名自定义 |
| **arch-announce 邮件列表** | `lists.archlinux.org` | ✅ 内容 = News 的镜像，与 RSS 同源，**二选一即可** |
| **arch-security 邮件列表** | — | ⚠️ **已停摆**（最后活动 2025-06-13，超 16 个月） |
| **News JSON API** | — | ❌ **不存在**，只有 RSS/Atom |

**最小预警配置（一条命令）：**

```bash
# 只看需要人工介入的公告 —— 这是最该订阅的
curl -s https://archlinux.org/feeds/news/ | grep -i "manual intervention"
```

### 1.2 新闻门禁工具（pacman hook 类）—— 这才是「预警」的核心

这三者原理相同：**在 pacman 事务前检查未读新闻，有则中断升级**。

| 工具 | 语言 | star | 最后更新 | 拦截策略 | 状态 |
|---|---|---|---|---|---|
| **`arch-manwarn`** | Rust | 25 | 2026-08-02 | **只拦含 "manual intervention" 关键词的新闻** | ✅ AUR v1.4.1-1，9 votes |
| **`newscheck`** | Rust | 6 | 2026-05-28 | 拦所有未读新闻（informant 的 Rust 替代） | ⚠️ AUR v0.2.5-1，仅 **1 vote** |
| **`informant`** | Python | 429 | 2025-06-07 | 拦所有未读新闻 | ❌ **已从 AUR 下架**（RPC 实测 `NOT_IN_AUR`） |

> ⚠️ **重要修正**：`informant` 虽然 GitHub 仓库还在（429★）、但 **AUR 包已下架**（本次 AUR RPC 实测确认），且 GitHub 最后提交停在 2025-06-07。**网上大量教程仍在推荐 informant，那些教程已过期。**
>
> ✅ **推荐改用 `arch-manwarn`** —— 它只拦真正危险的（manual intervention），不会因为一条无关新闻就阻断你升级，误报率低得多。Arch Wiki 也点名了它。

```bash
# 安装（从 AUR）
paru -S arch-manwarn
# 配置：/etc/arch-manwarn/config.toml
#   warn_only = true        # 只警告不阻断（保守起见先这样）
#   include_installed_packages = true
# 注意：arch-manwarn Conflicts: informant —— 两者不能共存
```

### 1.3 其他预警机制

| 机制 | 说明 |
|---|---|
| **`archlinux-keyring-wkd-sync.timer`** | `[官方]` **自 2022-07-29 起默认启用**，每周自动拉取新签名密钥。解决 `marginal trust` 报错 |
| **`reflector`** | `[实测]` extra 仓库，2023-5。自动挑最新同步的镜像 —— **镜像未同步是 404 / 依赖不一致的常见原因** |
| **`check_database_freshness`** | arch-mcp 的工具，检查 pacman 数据库同步状态 |

**签名报错时的正确处置：**

```bash
sudo pacman -Sy archlinux-keyring && sudo pacman -Syu   # 先更 keyring 再升级
# 或
sudo pacman-key --refresh-keys
```

---

## 2. 更新提醒 + 更新前检查

### 2.1 检查工具对照

| 工具 | 来源 | 作用 | 状态 |
|---|---|---|---|
| **`checkupdates`** | `pacman-contrib`（`[实测]` extra 1.13.1-1） | **用临时 DB 检查更新，不污染本地数据库** | ✅ 官方推荐 |
| **`arch-update`** | AUR（`[实测]` v4.4.3-1，**74 votes**，GitHub 460★，**2026-10-12 更新**） | 检查更新 + 新闻 + 孤儿 + pacnew + 缓存 + keyring + 服务，带托盘通知 | ✅ **最活跃的现成方案** |
| **`paru -Qua` / `yay -Qua`** | AUR | 只查 AUR 已装包的更新 | ✅ paru 1260 votes / yay 2649 votes |
| **`arch-audit`** | `[实测]` extra 0.2.0-5 | 查漏洞 | ⚠️ **数据源已停摆**（Arch ASA 自 2025-06 停发），当前不可信 |

**`checkupdates` 的退出码（这是写 timer 的关键）：**

| 退出码 | 含义 |
|---|---|
| `0` | **有更新**（并输出包列表） |
| `1` | 未知失败 |
| `2` | **无更新** |

环境变量：`CHECKUPDATES_DB`（默认 `${TMPDIR:-/tmp}/checkup-$UID`）、`CHECKUPDATES_CHANGE`。选项：`-n/--nosync`（不重同步临时库，适合 timer 常驻）、`-d/--download`（只下载不安装）。

### 2.2 提醒方案 A：自己搭（20 行，可控）

`~/.config/systemd/user/checkupdates.service`：

```ini
[Unit]
Description=Check for Arch updates

[Service]
Type=oneshot
ExecStart=/usr/bin/bash -c 'updates=$(checkupdates 2>/dev/null); [ -n "$updates" ] && notify-send -u normal -i dialog-warning "Arch 更新可用" "$(printf "%s\n" "$updates" | wc -l) 个包:\n$updates"'
```

`~/.config/systemd/user/checkupdates.timer`：

```ini
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

> ⚠️ **最常见的坑：systemd 里发不出桌面通知。**
> system 级 service / cron **没有** `DISPLAY` 和 `DBUS_SESSION_BUS_ADDRESS`，`notify-send` 会报 `The connection is closed`。
>
> **官方推荐解法**（Arch Wiki 原文）：用 `systemd-run` 进入用户会话：
> ```bash
> systemd-run --machine=<user>@.host --user notify-send '标题' '正文'
> ```
> 若用 **user timer**，先确保环境已导入：
> ```bash
> systemctl --user import-environment DISPLAY WAYLAND_DISPLAY DBUS_SESSION_BUS_ADDRESS
> ```
> 或在 service 里显式写：
> ```ini
> Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
> Environment=DISPLAY=:0
> ```

### 2.3 提醒方案 B：直接用 `arch-update`（省事）

```bash
paru -S arch-update
```

它自动提供：systemd timer 周期检查、托盘图标、桌面通知，检查范围覆盖**更新 / Arch 新闻 / 孤儿包 / pacnew / 旧缓存 / keyring / 需重启的服务**。

> 与 informant 的本质区别：**arch-update 不拦事务**，它定时提醒 + 引导你处理；informant / arch-manwarn 是**硬拦事务**。两者可以组合用。

### 2.4 更新前 Checklist（9 步，可粘贴）

```bash
# ① 读新闻 + 找人工介入公告（官方要求「升级前必读」）
curl -s https://archlinux.org/feeds/news/ | grep -iE "<title>|manual intervention" | head -20

# ② 检查 keyring 是否需要先更新
checkupdates | grep archlinux-keyring

# ③ 检查镜像同步状态
sudo reflector --latest 20 --protocol https --age 12 --sort rate --save /etc/pacman.d/mirrorlist

# ④ 检查磁盘空间（官方建议）
df -h / /var /boot

# ⑤ 打快照（btrfs）
sudo snapper -c root create -d "pre-update $(date +%F)"

# ⑥ 处理上次遗留的 .pacnew
sudo pacdiff

# ⑦ 备份包列表与配置
pacman -Qqe > ~/pkglist-$(date +%F).txt

# ⑧ 预览更新（-d 会顺便下载，不装）
checkupdates -d

# ⑨ 正式更新 —— 必须是 -Syu，绝不用 -Sy
sudo pacman -Syu

# —— 更新后 ——
systemctl --failed            # 失败的服务
sudo pacdiff                  # 处理本次 .pacnew
sudo checkservices            # 重启用旧库的进程（archlinux-contrib）
sudo rebuild-detector         # 找需重建的 AUR 包
needrestart                   # 判断是否需重启服务/内核
journalctl -b -p 3            # 本次启动的错误
```

`[实测]` 相关包都在官方仓库：`archlinux-contrib`（extra 20261009-1）、`rebuild-detector`（extra 4.4.5-1）。

---

## 3. 兜底机制（真正「不会滚挂」的部分）

### 3.1 自动快照：`snap-pac`

| 项 | 值 |
|---|---|
| 包 | `snap-pac` —— `[实测]` **官方 extra 仓库 3.0.1-3**（不是 AUR！） |
| 作用 | 用 snapper 在 **pacman 事务前后自动打 btrfs 快照** |
| 配置 | `/etc/snap-pac.ini`（默认只快照 root） |
| 跳过 | `SNAP_PAC_SKIP=y sudo pacman -Syu` |
| 回滚 | `sudo snapper -c root undochange N..M` |

```bash
sudo pacman -S snap-pac snapper
sudo snapper -c root create-config /
```

> ⚠️ **已知坑**：snap-pac 的 pre hook 在 db sync **之后**执行 → 回滚后 pacman 数据库未回滚，可能造成 partial upgrade。回滚后务必检查 `checkupdates` 状态。

### 3.2 其他兜底手段（全部实测在官方仓库）

| 手段 | 包 | 说明 |
|---|---|---|
| **备用内核** | `linux-lts`（`[实测]` core 6.18.56-1，2026-10-12） | 主内核挂了可从引导菜单选 LTS |
| **快照（非 btrfs）** | `timeshift`（`[实测]` extra 26.09.0-1） | 支持 rsync 模式 |
| **保留旧版本包** | `paccache`（pacman-contrib） | **默认保留 3 个版本**，`paccache -k N` 自定义；`paccache.timer` 每周自动清理 |
| **降级单个包** | `downgrade`（`[实测]` AUR v12.0.3-1，**910 votes**） | 从缓存或 ALA 找旧版 |
| **降级到任意日期** | ALA `https://archive.archlinux.org/` | 包保留数年 |

> **关键前提**：**不要把 `/var/cache/pacman/pkg` 清空** —— 这是你能降级的弹药库。`paccache -k 3` 保留 3 个版本是合理默认。

**pacman Hook 示例**（升级内核前备份 /boot；编号必须 <05 以先于 snap-pac）：

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

**降级命令：**

```bash
# 从 ALA 直接装指定版本（自动校验签名）
sudo pacman -U https://archive.archlinux.org/packages/l/linux/linux-6.16.1.arch1-1-x86_64.pkg.tar.zst
```

---

## 4. Agent 一站式方案

### 4.1 现成的：`arch-mcp`（推荐先试这个）

**本次最重要的发现** —— 前序调研曾认为「Arch 的 AI 生态基本为零」，**这个结论需要修正**。

| 项 | 值 |
|---|---|
| 仓库 | `nihalxkumar/arch-mcp` —— `[实测]` **59★**，Python，最后推送 **2026-03-10** |
| PyPI | `arch-ops-server` —— `[实测]` **v3.4.0**，17 个 release，最后上传 2026-02-12 |
| 许可 | GPL-3.0 / MIT 双许可 |
| 安装 | `uvx arch-ops-server`（需 Python 3.11+） |
| 声明 | **非官方社区项目**（README 明示 "Unofficial community project, not affiliated with Arch Linux"） |

**它提供的工具（正是用户问的那些）：**

| 工具 | 作用 |
|---|---|
| `check_updates_dry_run` | 检查可用更新（不执行） |
| `get_latest_news` | 抓 Arch News RSS |
| **`check_critical_news`** | **找需要人工介入的关键新闻** |
| **`get_news_since_last_update`** | **自上次更新以来的新闻** |
| `check_disk_space` | 磁盘空间 + 警告 |
| `check_failed_services` | 失败的系统服务 |
| `check_database_freshness` | pacman 数据库同步状态 |
| `get_pacman_cache_stats` | 包缓存大小与年龄 |
| `optimize_mirrors` | 镜像管理（status/test/suggest/health） |
| `analyze_pkgbuild_safety` | **PKGBUILD 安全分析（50+ 红旗）** |
| `install_package_secure` | 带安全检查的安装（拦截恶意包） |
| `query_package_history` | 查 pacman 日志历史 |

**⭐ 关键：它自带一个 `safe_system_update` Prompt（引导工作流）：**

> 检查关键新闻 → 验证磁盘空间 → 列出更新 → 检查服务 → 给出建议

**这正好是用户要的「一站式」。**

**接入 WorkBuddy 的方式**（写入 `~/.workbuddy-ai/mcp.json`）：

```json
{
  "mcpServers": {
    "arch-linux": {
      "command": "uvx",
      "args": ["arch-ops-server"]
    }
  }
}
```

> ⚠️ **三点注意**：
> 1. 这是**社区项目**，非 Arch 官方，安全自负。
> 2. 最后更新 2026-03，已 **8 个月未动** —— 用它做安全检查前，先确认它读的 News RSS 与 AUR 接口仍然有效。
> 3. 它包含 `install_package_secure` / `remove_packages` 等**写操作**，且需提权。建议先只用只读工具（`check_*` / `get_*`），确认可信后再放开写操作。
> 4. **必须在 Arch 上运行** —— 大部分工具标了 "Arch only"。

### 4.2 自建的：`arch-update-guard` skill（本次产出）

考虑到 `arch-mcp` 已 8 个月未更新、且依赖 `uvx` 环境，本次另外产出了一个**零依赖 skill**，直接用系统自带的 Python + `pacman-contrib`，无需 MCP 配置：

**位置**：`skills/arch-update-guard/`

**它做什么**：一条命令完成「更新前全套检查」，输出结构化报告供 agent 解析判断。

```bash
python3 arch_update_guard.py check      # 全套更新前检查
python3 arch_update_guard.py news       # 只看需要人工介入的公告
python3 arch_update_guard.py snapshot   # 打 btrfs 快照（需确认）
```

**与 arch-mcp 的分工**：

| | `arch-mcp` | `arch-update-guard`（本 skill） |
|---|---|---|
| 依赖 | Python 3.11+ + uvx | 系统 Python 3（Arch 自带） |
| 接入 | 需配 MCP | 直接跑 |
| 覆盖 | 12+ 工具，含写操作 | 只读检查 + 快照 |
| 更新 | 2026-03（8 个月未动） | 本次新写 |
| 适合 | 想要完整 MCP 生态 | 想要最小可用的检查闸门 |

---

## 5. 真实滚挂案例（2025-2026）

| 日期 | 事件 | 原因 | 避免方式 |
|---|---|---|---|
| 2025-06-20 | **Plasma 6.4 + X11** | 默认只装 wayland 会话 | 手动装 `plasma-x11-session kwin-x11` |
| 2025-06-21 | **linux-firmware 拆分** | 幽灵文件冲突 | `pacman -Rdd linux-firmware && pacman -Syu linux-firmware` |
| 2025-10-31 | dovecot 2.4 | 配置不兼容 | 读公告改配置 |
| 2025-12-20 | **NVIDIA 590** | 弃 Pascal(GTX10) 支持 | 换 `nvidia-open` 或锁版本 |
| 2026-04-05 | iptables 默认 nft | 默认后端变更（**无报错**） | 装 `iptables-nft` |
| 2026-05-25 | varnish → vinyl-cache | 包改名（7 步迁移） | 按公告迁移 |
| 2026-07-21 | virtualbox-ext-vnc | 幽灵文件 | 先卸或 `--overwrite` |
| **2026-09-22** | **mkinitcpio ≥42** | systemd hook 加 pcrseparator，改 PCR 0-7/9/12-14 | **重新 enroll TPM2**（`systemd-cryptenroll`） |
| 2026-06-12 | **AUR 恶意包事件** | 供应链（adoption 被滥用） | 每次读 PKGBUILD diff |

**五种翻车套路（比具体案例更重要）：**

1. **包改名 / 合并** → 旧包名消失，配置指向失效
2. **大版本配置不兼容** → 服务起不来（dovecot、zabbix）
3. **硬件被除名** → 驱动不支持老硬件（NVIDIA Pascal）
4. **默认行为变更** → **完全无报错**，最阴险（iptables 后端）
5. **幽灵文件冲突** → 需要先卸后装（linux-firmware、virtualbox-ext-vnc）

**通用防护**：`arch-manwarn` 能自动拦住第 1-5 类中**官方标注了 manual intervention 的**；剩下靠快照兜底。

---

## 6. Arch Wiki 官方口径（System maintenance）

`[官方]` Arch Wiki 的 System maintenance 页面要点：

1. **升级前必读**首页新闻，或订阅 RSS / arch-announce
2. **永不做 partial upgrade** —— 不要 `pacman -Sy`，一律 `pacman -Syu`；慎用 `--overwrite` 和 `-d`
3. **`checkupdates`** 是官方点名「无需同步库即可安全预览」的工具
4. 更新后处理 `.pacnew`（`pacdiff` / `checkservices`）、重启服务/内核
5. 装 **`linux-lts`** 备用内核；更新镜像列表；`rebuild-detector` 找需重建的 AUR 包
6. 备份 pacman db、包列表、配置
7. 降级是最后手段，优先看 `/var/log/pacman.log` 与论坛

---

## 7. 存疑与未核实

| 项目 | 状态 |
|---|---|
| `arch-update` 的确切 unit 文件名与配置路径 | `[未找到]` GitHub 直连被拦，建议装后 `pacman -Ql arch-update` 确认 |
| `arch-mcp` 的 12 个工具在当前是否全部可用 | `[未找到]` 需在 Arch 上实测；仓库 8 个月未更新 |
| `pacman-notifier` / `pacupdate` / `archup` 等旧工具 | `[二手]` 多为 2011-2015 年产物，基本停更 |
| Reddit 版「更新前 checklist」 | `[未找到]` 论坛抓取受限，§2.4 为 Arch Wiki 官方口径整理 |
| `informant` AUR 下架的确切原因与时间 | `[未找到]` 仅确认当前 RPC 返回 `NOT_IN_AUR` |

---

*报告生成：2026-10-13 ｜ 2 个并行子代理 + 主调研员独立实测（AUR RPC / 官方仓库 API / GitHub API / PyPI）*
