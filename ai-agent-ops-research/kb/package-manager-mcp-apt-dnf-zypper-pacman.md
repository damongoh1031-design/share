---
id: package-manager-mcp-apt-dnf-zypper-pacman
title: 用 MCP 执行包管理器更新（apt / dnf / zypper / yum / pacman / nixos-rebuild / snap / flatpak）× 五发行版
tags:
  - MCP
  - apt
  - dnf
  - zypper
  - pacman
  - nixos-rebuild
  - snap
  - flatpak
  - package-manager
  - system-update
  - openSUSE
  - Arch-Linux
  - Fedora
  - Debian
  - Ubuntu
  - NixOS
created: 2026-10-12
updated: 2026-10-12
version: 1
status: stable
source: 本次会话实测（GitHub Search API 11 组查询 + 23 个仓库 README/源码直读）
confidence: 已核实（元数据与 README/源码断言）；未做端到端部署验证
---

# 用 MCP 执行包管理器更新（apt / dnf / zypper / pacman / nixos-rebuild / snap / flatpak）

## TL;DR

**8 个目标命令里只有 4 个有真正可用的专用 MCP（apt / dnf / zypper / pacman），没有任何单一专用 MCP 覆盖全部发行版；而「真正能执行全系统升级」的专用工具，全网只有 `brianlechthaler/apt-mcp` 的 `apt_update` + `apt_upgrade` 一对。**

`snap` / `flatpak` **零可用专用 MCP**（唯一同名仓库 README 27 字节）；`yum` **不需要**专用 MCP（RHEL 8+ 里它就是 `dnf` 的符号链接）。

---

## 1. 命令映射：用户说的 → 系统真实命令

| 用户说的 | 发行版 | 刷新索引 | 升级已装包 | 全系统升级 | 备注 |
|---|---|---|---|---|---|
| `apt` | Debian / Ubuntu | `apt update` | `apt upgrade` | `apt full-upgrade` | 也是 `apt-get` |
| `dnf` | Fedora / RHEL 8+ | `dnf makecache` | `dnf upgrade` | `dnf distro-sync` | `dnf update` 是别名 |
| `rpm-ostree` | Fedora Silverblue / Kinoite | `rpm-ostree refresh-md` | `rpm-ostree upgrade` | 同左 | 不可变系统，**不能用 `dnf install`** |
| `zypper` | openSUSE Leap | `zypper refresh` | `zypper update` | `zypper dup` | Leap 用 `update` |
| `zypper` | openSUSE Tumbleweed | `zypper refresh` | — | **`zypper dup`** | ⚠️ 滚动版**必须**用 `dup` |
| `transactional-update` | openSUSE MicroOS / Aeon | — | `transactional-update up` | 同左 | 不可变系统 |
| `pacman` | Arch | `pacman -Sy` | `pacman -Syu` | `pacman -Syu` | ⚠️ 不要只 `-Sy` 不 `-u` |
| `yay` / `paru` | Arch（AUR） | — | `yay -Syu` | `yay -Syu` | 第三方 helper |
| `nixos-rebuild` | NixOS | `nix-channel --update` 或 `nix flake update` | — | `nixos-rebuild switch --upgrade` | ⚠️ 先更新 channel/flake，再 switch |
| `snap` | Ubuntu / 通用 | `snap refresh --list` | `snap refresh` | 同左 | — |
| `flatpak` | 通用 | `flatpak update --appstream` | `flatpak update` | 同左 | — |

### 三个必须先澄清的点

1. **`yum` 不需要专用 MCP。** RHEL 8+ / CentOS 8+ / Fedora 22+ 里 `yum` 是 `dnf` 的符号链接（只有 RHEL/CentOS 7 是真 yum，Python 2）。搜 `yum mcp` 命中 0 个相关项目是正常的。
2. **`zypper update` ≠ `zypper dup`。** Leap 用 `update`（保守）；**Tumbleweed 是滚动版，必须 `dup`**，用 `update` 会遇依赖冲突。任何只暴露模糊 "upgrade" 的 MCP 在 Tumbleweed 上就是错的。
3. **NixOS 更新是两阶段。** `nixos-rebuild switch --upgrade` 会先更新 channels；**用 flake 必须先 `nix flake update` 再 `nixos-rebuild switch`**。合成单个「upgrade」工具会掩盖 flake 锁文件变更这个决策点。

---

## 2. 可用性总表（8 命令 × 最佳选择）

| 目标命令 | 发行版 | 有可用专用 MCP？ | 最佳选择 | 能执行全系统升级？ |
|---|---|---|---|---|
| `apt` / `apt-get` | Debian / Ubuntu | ✅ 有 2 个 | **`brianlechthaler/apt-mcp`**（0★，MIT） | ✅ **`apt_update` + `apt_upgrade`** |
| `dnf` | Fedora / RHEL 系 | ✅ 有 2 个 | **`openSUSE/managesw-mcp`**（2★，MIT） | ⚠️ `install_patches` 装补丁，无 `distro-sync` |
| `zypper` | openSUSE / SLES | ✅ 有 3 个 | **`managesw-mcp`** 或 **`mcp-server-zypp`** | ⚠️ 同上；`mcp-server-zypp` 只有单包 install |
| `yum` | RHEL / CentOS 7 | ❌ 不需要 | 走 dnf 路径 | — |
| `pacman` | Arch | ✅ 有 1 个 | **`nihalxkumar/arch-mcp`**（59★） | ❌ **只有单包安装 + 更新检查** |
| `nixos-rebuild` | NixOS | ✅ 有 2 个 | **`JEFF7712/nix-agent`**（16★） | ✅ `build`/`diff`/`switch`/`generations` |
| `snap` | Ubuntu / 通用 | ❌ **没有** | 通用 shell MCP 兜底 | — |
| `flatpak` | 通用 | ❌ **没有** | 通用 shell MCP 兜底 | — |

### 候选全表（20 个，证据分级 A=源码直读 / B=README 原文 / C=仅搜索元数据 / D=推断）

| # | 仓库 | ★ | 语言 | 许可 | 最后推送 | 覆盖 | 执行变更 | 证据 |
|---|---:|---|---|---|---|---|---|---|
| 1 | `brianlechthaler/apt-mcp` | 0 | Rust | **MIT** | 2026-06-16 | `apt`/`dpkg` | ✅ 需 `confirm: true` | **A** |
| 2 | `GdMacmillan/apt-mcp-server` | 6 | JS | NOASSERTION | 2026-02-26 | `apt`/`dpkg` | ✅ **假设免密 sudo** | B |
| 3 | `openSUSE/managesw-mcp` | 2 | Go | **MIT** | 2026-07-06 | **`zypper`+`dnf`** | ✅ `install_package`/`install_patches`/`modify_repo` | **A** |
| 4 | `openSUSE/mcp-server-zypp` | 0 | C++/Go | GPL-3.0 | 2026-09-04 | `zypper`(libzypp) | ✅ `confirm_install`/`confirm_remove` | B |
| 5 | `anjupathak03/zypper-mcp` | 0 | Py | **无许可** | 2025-12-21 | `zypper` 只读 | ❌ 明确无 install/remove/upgrade | B |
| 6 | `nihalxkumar/arch-mcp` | 59 | Py | GPL-3.0 OR MIT | 2026-03-10 | `pacman`/AUR/Wiki | ⚠️ 仅单包 `install_package_secure` | B |
| 7 | `JEFF7712/nix-agent` | 16 | Py | **MIT** | 2026-10-12 | **`nixos-rebuild`** | ✅ `switch`（**默认高信任**） | B |
| 8 | `bolivian-peru/os-moda` | 120 | Rust | Apache-2.0 | 2026-06-24 | `nixos-rebuild`(SafeSwitch) | ✅ 带自动回滚 | B |
| 9 | `lukasl-dev/rime` | 19 | Rust | MIT | 2026-01-03 | Nix 生态查询 | ❌ 全只读 | B |
| 10 | `utensils/mcp-nixos` | **853** | Py | MIT | 2026-09-05 | NixOS 包/选项查询 | ❌ 只读（2 工具 ~1030 token） | B |
| 11 | `stubbedev/nix-mcp` | 1 | Go | MIT | 2026-10-10 | Nix 生态查询（Go 重写 mcp-nixos） | ❌ 只读 | B |
| 12 | `felixdorn/mcp-nix` | 7 | Py | GPL-3.0 | 2026-01-08 | Nix 生态查询 | ❌ 只读 | B |
| 13 | `simonives/redwrench` | — | Rust | MIT OR Apache-2.0 | — | Fedora 系统管理（可跑 dnf） | ✅ 策略引擎 + 四档 tier | B |
| 14 | `amineutron/fedora-agents` | — | TS | MIT | — | **KVM/Borg/Timeshift，非包管理** | ✅ 逐脚本 sudoers | B |
| 15 | `lucasarakaki/flatpak-mcp-server` | 0 | PHP | MIT | 2025-07-18 | 名义上 flatpak | ❌ **README 27 字节，空壳** | **A** |
| 16 | **`tumf/mcp-shell-server`** | **201** | Py | MIT | 2026-10-06 | 通用（argv 白名单） | ✅ | A |
| 17 | `rhel-lightspeed/linux-mcp-server` | **317** | — | Apache-2.0 | — | 通用（Guarded run_script） | ⚠️ 策略**禁止下载** | A |
| 18 | `classfang/ssh-mcp-server` | — | — | 见仓库 | — | 通用（SSH + 白名单） | ✅ | B |
| 19 | `iMANDexter/mcp-shell-server` | 2 | — | MIT | — | 通用（HTTPS+bearer+审计） | ✅ 明确警告 | B |
| 20 | `blazickjp/shell-mcp-server` | 22 | — | Apache-2.0 | 2025-08-19 | 通用（限定目录） | ✅ | B |

---

## 3. 逐项要点

### 3.1 `brianlechthaler/apt-mcp`（0★，Rust，MIT）—— 星标最低，设计最好

**读范围（默认）**：`apt_search`、`apt_show`、`apt_policy`、`apt_depends`、`apt_rdepends`、`apt_list_installed`、`apt_list_upgradable`、`apt_simulate`、`apt_sources_list`、`apt_version`

**写范围**（需 `APT_MCP_SCOPES=read,mutate` **且** 每次传 `confirm: true`）：**`apt_update`**（`apt-get update`）、**`apt_upgrade`**（`apt-get upgrade -y`）、`apt_install`、`apt_remove`、`apt_purge`、`apt_autoremove`

安全设计（证据 A，`docs/security.md`）：
- 遵循 **NSA CSI MCP Security Design Considerations PP-26-1834**
- **无 shell；严格 argv**
- 包名正则 `^[a-z0-9][a-z0-9+.\-]*$`
- 单次写操作最多 50 个包；`APT_MCP_MAX_OUTPUT_BYTES` 默认 1 MiB
- JSON-lines 审计到 stderr，`params_fingerprint` = SHA-256
- **防 rug-pull**：版本化 server `apt-mcp@0.1.0` + 固定工具 schema

⚠️ **`apt_upgrade` 是 `apt-get upgrade -y`，不是 `full-upgrade`**——不处理需要新增/删除依赖的升级。要 full-upgrade 得走通用 shell 层。

### 3.2 `openSUSE/managesw-mcp`（2★，Go，MIT）—— 唯一跨 zypper + dnf 的官方 MCP

官方原文：*"Most of the functions are only available on `zypper` and `dnf` based systems"*

源码直读（`managesw-mcp.go`，8,618 B）：`modelcontextprotocol/go-sdk/mcp` + cobra/viper，env 前缀 `MANAGESW_MCP`，后端在 `internal/pkg/syspackage`，OS 检测在 `internal/pkg/oscheck`，stdio + Streamable HTTP(TLS)。

**9 个工具**：`list_packages`、`query_package`、`search_package`（支持通配符）、`list_repos`、`list_patches`、**`install_patches`**（全部，或按 category/severity）、`install_package`、`remove_package`、**`modify_repo`**（增/启/禁/改/删软件源——**高危**）。

⚠️ **无 `distro-sync` / 全量升级工具**；**`modify_repo` 比装包危险得多**（等于控制包来源）。

### 3.3 `openSUSE/mcp-server-zypp`（0★，GPL-3.0）—— 安全设计最讲究，但缺 upgrade

**8 工具，按 root 分档**：
- 非 root：`search_packages`、`find_providers`、`find_dependents`、`check_updates`、`plan_install`（dry-run 求解）、`plan_remove`（dry-run）
- 需 root：`confirm_install`、`confirm_remove`

关键安全原文：
- *"GPG key trust decisions are elicitation-only. There is no tool argument that can pre-approve a key fingerprint — an LLM agent can only accept or reject a key through an interactive MCP elicitation round-trip, never by passing an argument that bypasses the prompt."*
- *"`confirm_install`/`confirm_remove` are cancellable up until the RPM transaction itself starts, and never interrupted once it has (interrupting a live RPM transaction is a good way to corrupt the local package database)."*

架构：Go proxy 说 MCP（stdio，HTTP 仅调试），**每次工具调用新起一个 `zypp-mcp-tool` C++ worker**（一次性进程，不持有长驻 libzypp 状态）；线协议 = Content-Length 分帧 JSON（LSP 风格，`worker/src/transport.h/.cc`）；`--list-tools` 输出纯 JSON；工具 schema 在 `worker/src/tools/registry.h` + 每工具一个 `.cc`。

⚠️ **没有 `confirm_upgrade` 工具**。

### 3.4 `nihalxkumar/arch-mcp`（59★，GPL-3.0 OR MIT）—— 唯一专用 Arch MCP

**Tools（`### Tools (Executable Functions)`）**：`check_updates_dry_run`、`install_package_secure`、`remove_packages`、`manage_orphans`（总是先 dry-run）、`manage_install_reason`、`verify_package_integrity`、`optimize_mirrors`(status/test/suggest/health)、`get_system_info`、`check_disk_space`、`check_failed_services`、`get_boot_logs`、`get_pacman_cache_stats`、`analyze_pacman_conf`、`analyze_makepkg_conf`、`analyze_pkgbuild_safety`（50+ 红旗）、`analyze_package_metadata_risk`、`query_package_history`（all/package/failures/sync）、`query_file_ownership`、`get_official_package_info`、`list_group_packages`、`list_package_groups`、`search_archwiki`、`search_aur`、`get_latest_news`、`get_news_since_last_update`、`check_critical_news`、`check_database_freshness`、`troubleshoot_issue`、`audit_aur_package`、`analyze_dependencies`

**Resources**：`pacman://installed`、`pacman://orphans`、`pacman://explicit`、`pacman://groups`、`pacman://group/*`、`pacman://database/freshness`、`pacman://log/recent`、`pacman://log/failed`、`archnews://since-update`、`config://pacman`、`mirrors://active`、`mirrors://health`

**Prompts（`### Prompts (Guided Workflows)`）**：`troubleshoot_issue`、`audit_aur_package`、`analyze_dependencies`、**`safe_system_update`**（"Check critical news → Verify disk space → List updates → Check services → **Recommendations**"）

> ⚠️ **`safe_system_update` 是 Prompt，不是 Tool——它给建议，不执行 `pacman -Syu`。** 看到工具名就下结论会直接搞错。

⚠️ README **零** root / sudo / polkit 说明——写权限如何获得未文档化。

### 3.5 NixOS 六个项目：能改的只有 2 个

| 项目 | 能改系统？ | 说明 |
|---|---|---|
| **`JEFF7712/nix-agent`**（16★，MIT） | ✅ | `build` / `diff` / `switch` / `generations`；**默认高信任**：无提示 `switch` + 免密 sudo（窄到本机 flake），低信任是「降级选项」；作者自述 *"Experimental and a work in progress."* |
| **`bolivian-peru/os-moda`**（120★，Apache-2.0） | ✅ | SafeSwitch（重建 + 健康检查失败自动回滚）、SHA-256 哈希链审计账本、原子 NixOS generation 回滚。**作者自述**：*"~250 commits; 247 tests + a self-run pentest — not an external audit"*；*"the default runtime's native shell/file tools aren't yet routed through the approval gate and audit ledger"*；*"**Run it on a fresh, disposable server — not a production machine you care about.**"* |
| `utensils/mcp-nixos`（853★） | ❌ | *"🚨 No Nix/NixOS Required!"*；*"Just two [tools]. We consolidated 17 tools into 2 because your AI's context window isn't infinite."*（~1,030 token）；`nix(action, query, source, type, channel, limit, version, system)` + `nix_versions` |
| `lukasl-dev/rime`（19★） | ❌ | Nix/NixOS/Home Manager/nvf/Nixhub 只读查询 |
| `stubbedev/nix-mcp`（1★） | ❌ | Go 重写 mcp-nixos，同样 2 工具；单静态二进制（~几十 MB RSS vs Python ~150 MB）；MCP roots 含 `X-Mcp-Root` HTTP header |
| `felixdorn/mcp-nix`（7★） | ❌ | 覆盖 Nixpkgs/NixOS/Home Manager/Nix Darwin/Nixvim/Impermanence/MicroVM.nix/sops-nix/disko 等 |

### 3.6 Fedora 专属

- **`simonives/redwrench`**（Rust）：4 档 tier（`safe`/`standard`/`developer`/`unrestricted`）；**自定义规则叠在 tier 之上且先于 tier 求值**；**每次调用（允许或拒绝）都写 systemd journal**。⚠️ 不在 Fedora 官方仓库也不在 COPR，只能下 release `.rpm` 手装；作者自称 hobby project。
- **`amineutron/fedora-agents`**：⚠️ **实际是 KVM/libvirt VM + Borg/Timeshift 备份，19 个工具没有一个碰 dnf/rpm**。但其权限设计值得抄：每工具声明是否需要 sudo / 是否破坏性；客户端必须确认破坏性调用；参数 Zod 校验后才跑脚本；**root 逐脚本授权**（sudoers 故意不对 `virsh`/`virt-clone`/`qemu-img` 开 NOPASSWD）；安装器生成 `/etc/sudoers.d/lyra` 并用 `visudo -cf` 校验后才启用；日志写 `MCP_AGENTS_LOG_DIR`（默认 `/var/log/mcp-agents`）JSON 0600，**从不写 `/tmp`**。

### 3.7 通用兜底层

| 仓库 | 关键机制 |
|---|---|
| **`tumf/mcp-shell-server`**（201★，MIT） | **argv 数组执行，不做 shell 字符串解释**；`ALLOW_COMMANDS` + `ALLOW_PATTERNS` 白名单；超时 + 输出上限；**最小子环境**（`MCP_SHELL_CHILD_ENV_ALLOWLIST`）；审计事件 `shell_execution_audit`；**脱敏** argv/env 中含 `SECRET`/`TOKEN`/`PASSWORD`/`PASSWD`/`API_KEY`/`ACCESS_KEY`/`PRIVATE_KEY`/`KEY`/`CREDENTIAL`/`AUTH` 的值 → `[REDACTED]`，长非数值 → 短 SHA-256 摘要；**审计日志故意不含原始 stdout/stderr**；默认拒绝 `find -exec`、shell/解释器启动器、`awk system()`、`tar --checkpoint-action=exec`、`env`、`xargs`、`timeout`/`nice`/`nohup`、`sed`/`less`/`vim`/`ssh`、别名 `gfind`/`gawk`/`gtar`/`gsort`、GNU `sort` 的外部程序选项（`--compress-program`/`-o`/`--output`/`--files0-from`/`-T`，含缩写与簇写 `--co`/`--o`/`-ro FILE`/`-rT DIR`）、**所有 git 命令级 config 覆盖**与持久 `git config` 写入。**官方明说**：*"they are not an OS sandbox"*、*"Allowlisting a command name is not a sandbox for that program's own argument-level execution features."* |
| `classfang/ssh-mcp-server` | `execute-command`（带 timeout）、`job-start`（后台，返回 `job_id`）、`upload`、`download`、`list-servers`；`--whitelist`/`--blacklist` 正则**完整命令匹配**；启用白名单后含 `;` `&` `\|` 反引号 `$()` `>` `<` 换行的命令**直接拒绝**；非零退出（如 `dnf check-update` → 100）返回输出 + `[exit code] N` 而非工具错误 |
| `rhel-lightspeed/linux-mcp-server`（317★，Apache-2.0） | `LINUX_MCP_TOOLSET=run_script\|both`；三层护栏（Gatekeeper LLM + 人工介入 + OS 沙箱「rudimentary」）；硬编码策略 *"No new repositories may be added"* / *"nothing may be downloaded from the internet"*；⚠️ `LINUX_MCP_TRANSPORT=http` **无认证**；Gatekeeper 评分表仍 `??`。**设计上不适合做系统更新**（禁下载），只适合只读诊断 |
| `iMANDexter/mcp-shell-server`（2★，MIT） | HTTPS + bearer token + 审计日志 + systemd；acme.sh/Let's Encrypt TLS；零依赖。**警告原文**：*"⚠️ This tool intentionally grants remote command execution. Anyone holding the token can run commands as the service user — and as root if you granted sudo. ... start with `--no-sudo`."* |
| `blazickjp/shell-mcp-server`（22★，Apache-2.0） | 命令只在指定目录内执行；bash/sh/cmd/powershell；超时控制 |

---

## 4. 可复用操作

### 4.1 方案 B 配置（多发行版混合环境推荐）

```bash
# tumf/mcp-shell-server —— 用 ALLOW_PATTERNS 做「命令 + 参数」全匹配，不要只放命令名
export ALLOW_PATTERNS='^apt-get (update|upgrade|full-upgrade)$|^dnf (makecache|upgrade|check-update)$|^zypper (refresh|update|dup)$|^pacman -Syu$|^nixos-rebuild (dry-activate|switch)( --upgrade)?$|^snap refresh$|^flatpak update$'
export ALLOW_COMMANDS='systemctl,journalctl,df,ss,uptime'
export MCP_SHELL_CHILD_ENV_ALLOWLIST='LANG,LC_ALL'
```

### 4.2 方案 C 配置（多机 SSH 集中式）

```bash
# classfang/ssh-mcp-server
--whitelist "^apt-get (update|upgrade)$|^dnf (makecache|upgrade|check-update)$|^zypper (refresh|update|dup)$|^pacman -Syu$|^nixos-rebuild (dry-activate|switch)( --upgrade)?$|^snap refresh$|^flatpak update$"
```

`nixos-rebuild switch` 这类长任务必须用 `job-start`（后台），不要用 `execute-command`（会超时）。

### 4.3 方案 A 配置（单发行版，以 apt 为例）

```json
{
  "mcpServers": {
    "apt": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "apt-mcp-run", "apt-mcp"],
      "env": { "APT_MCP_SCOPES": "read" }
    }
  }
}
```

只读起步；要升级把 `APT_MCP_SCOPES` 改成 `read,mutate`，且每次变更调用必须传 `confirm: true`。

### 4.4 方案 D：各发行版只读巡检起点

```bash
# Debian / Ubuntu
apt list --upgradable 2>/dev/null; apt-get -s upgrade | tail -5

# Fedora / RHEL 系
dnf check-update; dnf updateinfo summary

# openSUSE
zypper list-updates; zypper patches
# Tumbleweed: zypper dup --dry-run

# Arch（升级前必读 Arch News）
checkupdates; pacman -Qqe > /tmp/explicit.txt; curl -s https://archlinux.org/feeds/news/ | head -60

# NixOS
nixos-rebuild dry-activate; nixos-rebuild build --upgrade

# 通用
df -h; systemctl --failed; journalctl -p err -b --no-pager | tail -30
```

**建议节奏**：跑通只读巡检 2 周、确认 Agent 判断可靠之后，再逐条开写权限。

### 4.5 复现检索（GitHub Search API）

```bash
# 未认证配额：search 10 次/分钟。必须加 sleep，否则会被限流
q='apt mcp server in:name,description,readme'
curl -sL "https://api.github.com/search/repositories?q=$(python -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$q")&sort=stars&order=desc&per_page=15"
sleep 5
```

> 拉 README 走 `raw.githubusercontent.com`（不占 API 配额），但必须 `curl -sL` + 检查文件非空（200 空响应也是坑）。

---

## 5. 坑与反直觉

1. **`arch-mcp` 的 `safe_system_update` 是 Prompt 不是 Tool**——给建议，不执行 `pacman -Syu`。
2. **`oborchers/mcp-server-pacman`（11★）与 Arch 无关**——它索引 PyPI/npm/crates.io/Docker Hub/Terraform Registry。
3. **`snap` 和 `flatpak` 完全没有可用的专用 MCP**（flatpak 那个 README 27 字节）。
4. **`yum` 不需要专用 MCP**——RHEL 8+ 里它是 dnf 的符号链接。
5. **只有 `apt-mcp` 提供真正的全系统升级工具对**（`apt_update` + `apt_upgrade`），其余全部只能装单包或列更新。
6. **`managesw-mcp` 的 `modify_repo` 比装包危险得多**——能增删软件源。
7. **`mcp-server-zypp` 没有 `confirm_upgrade`**——只能查更新 + 装/删单包。
8. **`GdMacmillan/apt-mcp-server` 假设免密 sudo**（原文 *"Secure, passwordless `sudo` assumed for all operations"*），且内部目录名是 `popos-control-mcp`。
9. **`brianlechthaler/apt-mcp` 是 0★ 但设计最好**——**星标与质量倒挂**。6★ 的那个安全性更差。
10. **`JEFF7712/nix-agent` 默认高信任**——免密 sudo + 无提示 `switch`，低信任是「降级选项」。
11. **`os-moda` 作者自己说不要上生产**——shell/文件工具未接入审批门与审计账本。
12. **`tumf/mcp-shell-server` 不是 OS 沙箱**——`ALLOW_COMMANDS="pacman"` 会允许 `pacman -Rdd`。必须用 `ALLOW_PATTERNS`。
13. **`arch-mcp` README 无任何 root/sudo 说明**——写权限获取方式未文档化。
14. **搜索 `apt` 有 8/24 是 Aptos 区块链**（`Tlazypanda/aptos-mcp-server`、`rishi-xyz/aptos-mcp`、`ctianming/moveflow_aptos_mcp_server`、`ToolOracle/aptoracle`、`Aptoide/aptoide-mcp`）+ Aptabase 分析（`aptabase/aptabase-mcp`）+ 意大利房产爬虫（`n3pt7un/apt_scrape`）+ AST 分析（`clouatre-labs/aptu-coder`）。**只有 2 个真操作 Debian apt**。
15. **搜索 `dnf` 被游戏污染**——`heihuo000/pvfUtility-MCP` 是 DNF（Dungeon & Fighter）游戏文件工具。
16. **搜索 `yum mcp server` → 0 个相关结果**（这本身是正确结论，不是检索失败）。
17. **搜索 `flatpak mcp` → 7 个全无关**；`snap package mcp server` → 只有 `canonical/discourse-mcp-snap`（把 Discourse MCP 打包成 snap）。
18. **无许可证 = 不可用**：`anjupathak03/zypper-mcp`、`lioilsources/LeapDoctor`、`openSUSE/mcp-bugzilla`（官方组织但 license 为 None）、`E13ctr0N/AiSysAdmin`、`domdomegg/shell-exec-mcp`。
19. **`lioilsources/LeapDoctor` README 只有 317 字节**，纯想法草稿。
20. **`amineutron/fedora-agents` 不做包管理**——是 KVM/libvirt + 备份。
21. **`redwrench` 不在 Fedora 官方仓库也不在 COPR**——只能下 release `.rpm` 手装。
22. **`linux-mcp-server` 硬编码禁止下载**——设计上就不适合做系统更新。
23. **NixOS 更新两阶段**——先 `nix flake update`，再 `nixos-rebuild switch`。
24. **Tumbleweed 必须 `zypper dup`**，用 `update` 会遇依赖冲突。
25. **Arch 不要只 `pacman -Sy` 不 `-u`**（部分升级会炸系统）；白名单必须写 `^pacman -Syu$` 全匹配。
26. **Fedora Silverblue / Kinoite / openSUSE MicroOS 是不可变系统**，用 `rpm-ostree` / `transactional-update`，**上面所有 MCP 都没覆盖这一层**。
27. **`apt-mcp` 的 `apt_upgrade` 是 `upgrade -y` 不是 `full-upgrade`**。
28. **`ssh-mcp-server` 白名单拒绝含 `|` 的命令**，但 `dnf check-update` 返回 100 是正常语义（已特殊处理）。
29. **`nixos-rebuild switch` 会超时**——必须 `job-start`。
30. **GitHub 未认证配额：core 60/小时、search 10/分钟、code_search 60/小时**。本轮 11 组查询被限流 2 次；core 配额中途耗尽（`remaining: 0`），导致部分仓库星标/推送日期无法二次核实。

---

## 6. 推荐架构

| 方案 | 适用 | 组件 | 缺口 |
|---|---|---|---|
| **A · 专用 MCP 组合** | 单一发行版固定环境 | 按发行版各装一个（见 §3） | Arch 全系统升级 / zypper 全量升级 / snap / flatpak 四项无覆盖 |
| **B · 统一 shell 执行层** | **多发行版混合（推荐）** | `tumf/mcp-shell-server` | 必须另配 OS 层隔离（容器/VM/专用用户） |
| **C · SSH 集中式** | 一台工作台管 N 台机器 | `classfang/ssh-mcp-server` | 同 B |
| **D · 只读优先** | **推荐作为起点** | 各发行版只读层（见 §4.4） | 只读，无写能力 |

**三份报告的执行层结论一致**：优先用专用 MCP（最小权限 + 可审计），缺失时用 `tumf/mcp-shell-server` 这类 argv 白名单执行层兜底，**永远不要给 Agent 一个裸 sudo shell**。

---

## 7. 未核实 / 存疑

| 项 | 状态 | 原因 |
|---|---|---|
| `managesw-mcp` 的 dnf 后端实现细节 | 部分 | README 明确说支持 dnf；后端在 `internal/pkg/syspackage`，未逐文件读 |
| `arch-mcp` 的权限提升方式 | **未核实** | README 完全没提 root / sudo / polkit |
| `arch-mcp` 的 `install_package_secure` 是否真执行 pacman | 未核实 | 描述是「Install with security checks」，未读源码确认调用链 |
| `simonives/redwrench`、`amineutron/fedora-agents`、`classfang/ssh-mcp-server` 的星标与最新推送 | 未核实 | 本轮 core API 配额耗尽（60/60） |
| `iMANDexter/mcp-shell-server` 的完整审计字段 | 部分 | 仅 README 摘要 |
| 各候选的许可证商业条款 | 未核实 | 多个仓库 `license.spdx_id` 为 `NOASSERTION` 或缺失 |
| `openSUSE/mcp-server-zypp` 是否计划加 upgrade 工具 | 未核实 | 未读 issue / roadmap |
| 是否真有可用 snap / flatpak MCP | **未核实（倾向无）** | 仅检索 GitHub；未查 npm / PyPI / Glama / Smithery / PulseMCP |

### 方法论边界

1. **本轮未做端到端实测**——所有能力断言来自 README 原文 / 源码直读 / 搜索结果元数据，**未实际部署任一 MCP 执行 `apt upgrade` 验证**。
2. **「未发现」≠「不存在」**。
3. **检索只覆盖 GitHub**，未查 MCP 目录站。
4. **未评估代码质量与维护活跃度**——0★ 项目可能明天停更。

---

## 8. 相关文件

| 文件 | 说明 |
|---|---|
| `研究报告_包管理器MCP选型_五发行版.md` | 完整报告（8 章 + 3 附录，含 30 条坑、证据分级） |
| `研究报告_包管理器MCP选型_五发行版.html` | 自包含 HTML（47 条 TOC、0 断链、23 表、15 警示块） |
| `kb/hermes-openclaw-linux-ops-agent-stack.md` | 前序 KB（Hermes/OpenClaw 运维栈，v5） |
| `kb/general-agent-workbench-alternatives.md` | 前序 KB（通用 Agent 工作台六项能力，v1） |
