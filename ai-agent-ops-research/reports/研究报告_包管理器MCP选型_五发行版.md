# 包管理器 MCP 选型研究报告（apt / dnf / zypper / yum / pacman / nixos-rebuild / snap / flatpak）

**版本** v1.0 · **成稿日期** 2026-10-12 · **检索方式** GitHub Search API（11 组限定式查询）+ 仓库 README / 源码文件直读 · **覆盖发行版** Debian/Ubuntu、Fedora/RHEL 系、openSUSE/SLES、Arch、NixOS + 跨发行版（snap/flatpak）

> 本报告回答一个具体问题：**要用 MCP 在 NixOS / Fedora / Ubuntu / Arch / openSUSE 上执行 `apt`、`dnf`、`zypper`、`yum`/`pacman`、`nixos-rebuild`、`snap`、`flatpak` 来更新系统，有哪些 MCP 可用？**
> 全文先给出「可用性总表」，再逐发行版取证，最后给三种推荐架构。每一条能力断言都标注证据等级；凡搜索结果里同名但实际无关的项目，单独列入「命名陷阱」章。

---

## 摘要

**一句话结论：8 个目标命令里只有 4 个有真正可用的专用 MCP（apt / dnf / zypper / pacman），没有一个专用 MCP 能覆盖全部发行版；而「真正能执行全系统升级」的专用工具，全网只有 `brianlechthaler/apt-mcp` 的 `apt_update` + `apt_upgrade` 一对。**

### 三条核心结论

1. **`snap` 与 `flatpak` 完全没有可用的专用 MCP。** 唯一名叫 flatpak-mcp-server 的仓库 README 只有 27 字节（空壳）。这两个必须走通用 shell MCP。
2. **`yum` 不需要专用 MCP。** RHEL 8+ / CentOS 8+ / Fedora 22+ 里 `yum` 就是 `dnf` 的符号链接；只有 RHEL/CentOS 7 才是真正的 yum。搜索 `yum mcp` 得到的全是无关项目。
3. **`openSUSE/managesw-mcp` 是唯一一个跨包管理器的官方 MCP**——openSUSE 官方组织出品，官方原文：*"Most of the functions are only available on `zypper` and `dnf` based systems"*，同时覆盖 openSUSE/SLES 与 Fedora/RHEL 系。

### 一张表看完

| 目标命令 | 发行版 | 有可用专用 MCP？ | 最佳选择 | 能执行全系统升级？ |
|---|---|---|---|---|
| `apt` / `apt-get` | Debian / Ubuntu | ✅ 有 2 个 | **`brianlechthaler/apt-mcp`**（0★，MIT） | ✅ **`apt_update` + `apt_upgrade`** |
| `dnf` | Fedora / RHEL 系 | ✅ 有 2 个 | **`openSUSE/managesw-mcp`**（2★，MIT） | ⚠️ `install_patches` 装补丁，无 `distro-sync` |
| `zypper` | openSUSE / SLES | ✅ 有 3 个 | **`openSUSE/managesw-mcp`** 或 **`openSUSE/mcp-server-zypp`** | ⚠️ 同上；`mcp-server-zypp` 只有单包 install |
| `yum` | RHEL / CentOS 7 | ❌ 不需要 | 走 dnf 路径 | — |
| `pacman` | Arch | ✅ 有 1 个 | **`nihalxkumar/arch-mcp`**（59★） | ❌ **只有单包安装 + 更新检查** |
| `nixos-rebuild` | NixOS | ✅ 有 2 个 | **`JEFF7712/nix-agent`**（16★） | ✅ `build`/`diff`/`switch`/`generations` |
| `snap` | Ubuntu / 通用 | ❌ **没有** | 通用 shell MCP 兜底 | — |
| `flatpak` | 通用 | ❌ **没有** | 通用 shell MCP 兜底 | — |

### 三条推荐架构

- **方案 A · 专用 MCP 组合**（按发行版各装一个）：Debian/Ubuntu→`apt-mcp`；Fedora/openSUSE→`managesw-mcp`；Arch→`arch-mcp` + 兜底；NixOS→`nix-agent` + `mcp-nixos`。
- **方案 B · 统一 shell 执行层**（多发行版混合环境推荐）：**`tumf/mcp-shell-server`**（201★，MIT，argv 数组执行 + `ALLOW_COMMANDS`/`ALLOW_PATTERNS` 白名单 + 结构化审计日志 + 脱敏）。
- **方案 C · SSH 集中式**（多机）：`classfang/ssh-mcp-server` + `--whitelist` 正则完整命令匹配。

> ⚠️ **最重要的一条反直觉**：`nihalxkumar/arch-mcp` 里那个叫 `safe_system_update` 的东西**是 Prompt，不是 Tool**。它位于 README 的 `### Prompts (Guided Workflows)` 段下，作用是「检查 Arch News → 验磁盘空间 → 列更新 → 检查服务 → **给建议**」，**它不执行 `pacman -Syu`**。看到工具名就下结论会直接搞错。

---

## 第 1 章 需求映射：8 个命令 → 真实系统命令

### 1.1 命令映射表

| 用户说的命令 | 发行版 | 刷新索引 | 升级已装包 | 全系统升级（含依赖变更） | 备注 |
|---|---|---|---|---|---|
| `apt` | Debian / Ubuntu | `apt update` | `apt upgrade` | `apt full-upgrade` | 也是 `apt-get` |
| `dnf` | Fedora / RHEL 8+ | `dnf makecache` | `dnf upgrade` | `dnf distro-sync` | `dnf update` 是别名 |
| `rpm-ostree` | Fedora Silverblue / Kinoite | `rpm-ostree refresh-md` | `rpm-ostree upgrade` | 同左 | 不可变系统，**不能用 `dnf install`** |
| `zypper` | openSUSE Leap | `zypper refresh` | `zypper update` | `zypper dup` | Leap 用 `update` |
| `zypper` | openSUSE Tumbleweed | `zypper refresh` | — | **`zypper dup`** | ⚠️ 滚动版**必须**用 `dup` |
| `transactional-update` | openSUSE MicroOS / Aeon | — | `transactional-update up` | 同左 | 不可变系统 |
| `pacman` | Arch | `pacman -Sy` | `pacman -Syu` | `pacman -Syu` | ⚠️ 不要只 `-Sy` 不 `-u` |
| `yay` / `paru` | Arch（AUR） | — | `yay -Syu` | `yay -Syu` | 第三方 helper |
| `nixos-rebuild` | NixOS | `nix-channel --update` 或 `nix flake update` | — | `nixos-rebuild switch --upgrade` | ⚠️ 顺序：先更新 channel/flake，再 switch |
| `snap` | Ubuntu / 通用 | `snap refresh --list` | `snap refresh` | 同左 | — |
| `flatpak` | 通用 | `flatpak update --appstream` | `flatpak update` | 同左 | — |

### 1.2 三个必须先澄清的点

**（1）`yum` 不需要专用 MCP。**
RHEL 8+ / CentOS 8+ / Fedora 22+ 中 `yum` 是 `dnf` 的符号链接，底层就是 dnf。只有 RHEL 7 / CentOS 7 才是真正的 yum（Python 2 实现）。因此「yum MCP」既不存在也不必要——用 dnf 路径即可。

**（2）`zypper update` 与 `zypper dup` 不是一回事。**
openSUSE Leap 用 `update`（保守，不跨版本）；**Tumbleweed 是滚动发行版，必须用 `dup`**。如果用 `update` 在 Tumbleweed 上做全量更新，会遇到依赖冲突。任何给 openSUSE 用的 MCP 如果只暴露一个模糊的 "upgrade"，在 Tumbleweed 上就是错的。

**（3）NixOS 的「更新系统」是两阶段。**
`nixos-rebuild switch --upgrade` 会先更新 channels 再重建；如果用 flake，则必须 `nix flake update`（或 `nix flake update <input>`）之后再 `nixos-rebuild switch`。把这两步合成一个「upgrade」工具会掩盖「flake 锁文件变更」这个关键决策点。

---

## 第 2 章 可用性总表

证据等级：**A** = 源码直读 · **B** = 仓库 README 原文 · **C** = 仅搜索结果元数据 · **D** = 本报告推断

| # | MCP 仓库 | ★ | 语言 | 许可 | 最后推送 | 覆盖命令 | 是否执行变更 | 证据 |
|---|---:|---|---|---|---|---|---|---|
| 1 | `brianlechthaler/apt-mcp` | 0 | Rust | **MIT** | 2026-06-16 | `apt` / `dpkg` | ✅ 变更需 `confirm: true` | **A** |
| 2 | `GdMacmillan/apt-mcp-server` | 6 | JavaScript | NOASSERTION | 2026-02-26 | `apt` / `dpkg` | ✅ **假设免密 sudo** | B |
| 3 | `openSUSE/managesw-mcp` | 2 | Go | **MIT** | 2026-07-06 | **`zypper` + `dnf`** | ✅ `install_package` / `install_patches` / `modify_repo` | **A** |
| 4 | `openSUSE/mcp-server-zypp` | 0 | C++/Go | GPL-3.0 | 2026-09-04 | `zypper`（libzypp） | ✅ `confirm_install` / `confirm_remove` | B |
| 5 | `anjupathak03/zypper-mcp` | 0 | Python | **无许可** | 2025-12-21 | `zypper` 只读 | ❌ 明确无 install/remove/upgrade | B |
| 6 | `nihalxkumar/arch-mcp` | 59 | Python | GPL-3.0 OR MIT | 2026-03-10 | `pacman` / AUR / Arch Wiki | ⚠️ 仅单包 `install_package_secure` | B |
| 7 | `JEFF7712/nix-agent` | 16 | Python | **MIT** | 2026-10-12 | **`nixos-rebuild`** | ✅ `switch`（**默认高信任**） | B |
| 8 | `bolivian-peru/os-moda` | 120 | Rust | Apache-2.0 | 2026-06-24 | `nixos-rebuild`（SafeSwitch） | ✅ 带自动回滚 | B |
| 9 | `lukasl-dev/rime` | 19 | Rust | MIT | 2026-01-03 | Nix 生态查询 | ❌ 全只读 | B |
| 10 | `utensils/mcp-nixos` | **853** | Python | MIT | 2026-09-05 | NixOS 包/选项查询 | ❌ 只读（2 工具，~1030 token） | B |
| 11 | `stubbedev/nix-mcp` | 1 | Go | MIT | 2026-10-10 | Nix 生态查询（Go 重写 mcp-nixos） | ❌ 只读 | B |
| 12 | `felixdorn/mcp-nix` | 7 | Python | GPL-3.0 | 2026-01-08 | Nix 生态查询 | ❌ 只读 | B |
| 13 | `simonives/redwrench` | — | Rust | MIT OR Apache-2.0 | — | Fedora 系统管理（可跑 dnf） | ✅ 策略引擎 + 四档 tier | B |
| 14 | `amineutron/fedora-agents` | — | TypeScript | MIT | — | **KVM/Borg/Timeshift，非包管理** | ✅ 逐脚本 sudoers | B |
| 15 | `lucasarakaki/flatpak-mcp-server` | 0 | PHP | MIT | 2025-07-18 | 名义上 flatpak | ❌ **README 27 字节，空壳** | **A** |

### 2.1 通用兜底层（覆盖全部 8 个命令）

| # | MCP 仓库 | ★ | 许可 | 关键机制 | 证据 |
|---|---:|---|---|---|---|
| 16 | **`tumf/mcp-shell-server`** | **201** | MIT | **argv 数组执行，不做 shell 字符串解释**；`ALLOW_COMMANDS` + `ALLOW_PATTERNS` 白名单；超时 + 输出字节上限；最小子环境；**结构化审计日志**（argv 脱敏 + SHA-256 摘要） | A |
| 17 | `rhel-lightspeed/linux-mcp-server` | **317** | Apache-2.0 | Red Hat 官方；`run_script` 工具集（Gatekeeper + 人工介入 + OS 沙箱）；硬编码策略「不得添加新仓库」「不得从互联网下载」 | A |
| 18 | `classfang/ssh-mcp-server` | — | 见仓库 | `--whitelist` 正则**完整命令匹配**；启用白名单时含 `;` `&` \| 反引号 `$()` `>` `<` 换行的命令直接拒绝 | B |
| 19 | `iMANDexter/mcp-shell-server` | 2 | MIT | HTTPS + bearer token + 完整审计日志 + systemd；**明确警告「intentionally grants remote command execution」**，建议 `--no-sudo` 起步 | B |
| 20 | `blazickjp/shell-mcp-server` | 22 | Apache-2.0 | 限定目录内执行，支持 bash/sh/cmd/powershell + 超时 | B |

---

## 第 3 章 逐发行版取证

### 3.1 Debian / Ubuntu — `apt`

#### ⭐ `brianlechthaler/apt-mcp`（0★，Rust，MIT）—— 设计最好，星标最低

这是本报告见到的**安全设计最完整的包管理 MCP**，且明确声明遵循 NSA 的《MCP Security Design Considerations》(PP-26-1834)。

**工具面**（证据 A，`docs/features/tools.md`）：

只读 scope（**默认**）：

| 工具 | 作用 | 底层命令 |
|---|---|---|
| `apt_search` | 搜索包 | `apt-cache search` |
| `apt_show` | 包元数据 | `apt-cache show` |
| `apt_policy` | 版本策略 | `apt-cache policy` |
| `apt_depends` / `apt_rdepends` | 依赖 / 反向依赖 | `apt-cache depends` / `rdepends` |
| `apt_list_installed` | 已装包与版本 | `dpkg-query` |
| `apt_list_upgradable` | **有可用升级的包** | `apt list --upgradable` |
| `apt_simulate` | **dry-run 变更操作**（`install`/`remove`/`upgrade`/`purge`/`autoremove`） | `--simulate` |
| `apt_sources_list` | 源列表 | 读 `/etc/apt/sources.list` |
| `apt_version` | 版本 | `apt-get --version` |

变更 scope（需 `APT_MCP_SCOPES=read,mutate` 且 `confirm: true`）：

| 工具 | 底层命令 |
|---|---|
| **`apt_update`** | **`apt-get update`**（刷新索引） |
| **`apt_upgrade`** | **`apt-get upgrade -y`**（升级已装包） |
| `apt_install` / `apt_remove` / `apt_purge` / `apt_autoremove` | 对应 `apt-get` 子命令 |

**安全控制**（证据 A，`docs/security.md`）：

| 控制 | 实现 |
|---|---|
| 最小权限（逐调用） | `APT_MCP_SCOPES` 启动时限定；每个工具声明所需 scope；变更工具必须 `confirm: true` |
| **无 shell** | *"No shell; strict argv"* —— 从根上消除命令注入 |
| 输入校验 | 包名正则 `^[a-z0-9][a-z0-9+.\-]*$`；搜索模式限字母数字 + 有限通配；**单次变更最多 50 个包** |
| 输出上限 | `APT_MCP_MAX_OUTPUT_BYTES`，默认 1 MiB |
| 审计日志 | 结构化 JSON-lines 写 stderr，每次调用 + 每次结果各一条；`params_fingerprint` 存 params 的 **SHA-256** 而非原文；`result_status` ∈ `success`/`denied`/`error` |
| **防工具定义漂移（rug-pull）** | **版本化服务器 `apt-mcp@0.1.0` + pinned tool schemas** |

> ⚠️ **它只有 0★**。设计质量与热度完全倒挂——这是本报告最值得注意的一组反差。用之前自己读一遍源码。

#### ⚠️ `GdMacmillan/apt-mcp-server`（6★，JavaScript）—— 星标更高，安全性更差

- 官方原文：*"it exposes tools for installing, removing, updating, and querying apt packages using the system's native `apt` and `dpkg` binaries with **`sudo` privileges**."*
- 官方原文：*"**Secure, passwordless `sudo` assumed for all operations**"* 与 *"The server assumes the user has passwordless `sudo` for apt operations."*
- 仓库内部目录名是 `popos-control-mcp`，stdio 传输。

> ⚠️ 「假设免密 sudo」意味着这个 MCP 一旦被接入，**Agent 对该机器拥有无门槛 root 包管理权**。它没有任何 scope 分层、没有 `confirm` 二次确认、没有审计日志描述。除非在一次性容器里，否则不建议。

### 3.2 Fedora / RHEL 系 — `dnf`（及 `yum`）

#### ⭐ `openSUSE/managesw-mcp`（2★，Go，MIT）—— 唯一跨 zypper + dnf 的官方 MCP

- **openSUSE 官方组织**仓库（`github.com/openSUSE`）。
- 官方原文：*"`managesw-mcp` is a server that exposes OS software management functions through the Model Context Protocol (MCP). It allows you to manage **packages, repositories, and patches** on a Linux system. **Most of the functions are only available on `zypper` and `dnf` based systems**"*
- 实现（证据 A，读 `managesw-mcp.go`）：Go + 官方 MCP SDK（`github.com/modelcontextprotocol/go-sdk/mcp`）+ cobra/viper；后端抽象在 `internal/pkg/syspackage`，系统识别在 `internal/pkg/oscheck`；环境变量前缀 `MANAGESW_MCP`；支持 stdio 与 Streamable HTTP（含 TLS）。

**9 个工具**（证据 A，源码 `Name`/`Description` 字段）：

| 工具 | 说明 | 变更性 |
|---|---|---|
| `list_packages` | 列出已装包 | 只读 |
| `query_package` | 查包信息（已装或在仓库中） | 只读 |
| `search_package` | 在已启用仓库搜索（支持通配符） | 只读 |
| `list_repos` | 列出仓库（名称/URL/启用状态） | 只读 |
| `list_patches` | **列出可用补丁**（名称/类别/严重性） | 只读 |
| **`install_patches`** | **安装补丁**——可全部，或按类别/严重性选子集 | ⚠️ **变更** |
| `install_package` | 安装包及其依赖 | ⚠️ 变更 |
| `remove_package` | 移除包及其依赖 | ⚠️ 变更 |
| `modify_repo` | 启用/禁用/改属性/新增/删除仓库 | ⚠️ **高危变更** |

> ⚠️ **三个必须知道的点**：
> 1. **只有 2★**，Go 单文件（8,618 字节），README 仅 955 字节。成熟度低。
> 2. **`modify_repo` 是高危工具**——它能新增或删除软件源，等于控制「包从哪来」。这比装包本身危险得多，接入时必须单独评估。
> 3. **没有 `distro-sync` / 全系统升级工具**。`install_patches` 是补丁安装（近似于安全更新），不是 `dnf upgrade`。

#### `simonives/redwrench`（Rust，MIT OR Apache-2.0）—— 策略引擎式，Fedora 专属

- 定位是 **Fedora 系统管理 MCP**，不是包管理 MCP；但它能执行命令，配置里明确提到 `dnf install` 超时场景。
- 核心设计（证据 B）：
  - **策略引擎先于执行**，四档内置 tier：`safe` / `standard` / `developer` / `unrestricted`
  - **自定义规则叠加在 tier 之上，且最先评估**（*"Custom rules layer on top of the tier and are evaluated FIRST"*）
  - **每次调用都写 systemd journal，无论被允许还是被拒绝**
  - `developer` tier 需要指定运行用户名（不用 root 跑 bash/python/gcc/npm/cargo）
- 安装：官方 release 提供 `.rpm`（在 Fedora 上构建）；`sudo dnf install ./redwrench-*.rpm`
- ⚠️ **尚未进 COPR 或 Fedora 官方仓库**（README 的 ROADMAP 承认），作者自述是业余项目。

#### `amineutron/fedora-agents`（MIT，npm `fedora-agents-mcp`）—— 名字骗人，不做包管理

- 实际功能：**KVM/libvirt 虚拟机 + Borg/Timeshift 备份**。19 个工具，**没有一个碰 dnf/rpm**。
- 但它的**权限设计是全报告最值得抄的**（证据 B）：
  - 每个工具声明是否需要 sudo、是否具破坏性；**客户端必须确认破坏性调用**
  - 参数在任何脚本运行前用 **Zod 校验**
  - **root 权限逐脚本授予**：sudoers **不对 `virsh` / `virt-clone` / `qemu-img` 开 NOPASSWD**（因为那等于把整个虚拟化层通过 sudo 交出去），只对复制脚本逐条授权
  - 安装器生成 `/etc/sudoers.d/lyra` 并**先用 `visudo -cf` 校验再生效**
  - 日志写 JSON 到 `MCP_AGENTS_LOG_DIR`（默认 `/var/log/mcp-agents`），**文件权限 0600，绝不写 `/tmp`**

> ⚠️ **`yum` 的结论**：搜索 `yum mcp server in:name,description` 结果为 0 个相关项目。RHEL/CentOS 7 的 yum 场景没有专用 MCP，用 dnf 路径或通用 shell MCP。

### 3.3 openSUSE / SLES — `zypper`

openSUSE 官方组织（`github.com/openSUSE`）在这个领域产出了 4 个 MCP，其中 2 个与包管理直接相关：

| 仓库 | ★ | 语言 | 许可 | 最后推送 | 用途 |
|---|---:|---|---|---|---|
| `openSUSE/managesw-mcp` | 2 | Go | MIT | 2026-07-06 | **跨 zypper + dnf 的包/仓库/补丁管理** |
| `openSUSE/mcp-server-zypp` | 0 | C++/Go | GPL-3.0 | 2026-09-04 | **libzypp 级 zypper 管理** |
| `openSUSE/systemd-mcp` | 10 | Go | MIT | 2026-09-24 | systemd（**不是包管理**） |
| `openSUSE/mcp-bugzilla` | 14 | Python | 无许可 | 2026-10-01 | Bugzilla 查询 |

#### ⭐ `openSUSE/mcp-server-zypp`（0★，GPL-3.0）—— 安全设计最讲究，但缺 upgrade

**8 个工具，按是否需 root 分层**（证据 B）：

| 工具 | 需要 root | 作用 |
|---|---|---|
| `search_packages` | 否 | 按名称/摘要找包 |
| `find_providers` | 否 | 哪些包提供某能力 |
| `find_dependents` | 否 | 哪些包依赖某包 |
| `check_updates` | 否 | **列出可用更新** |
| `plan_install` | 否 | **dry-run 求解安装——不做任何变更** |
| `plan_remove` | 否 | **dry-run 求解移除——不做任何变更** |
| `confirm_install` | **是** | 真正安装，**受 GPG 密钥信任与许可证接受门控** |
| `confirm_remove` | **是** | 真正移除 |

**三条值得单独记的设计**（证据 B）：

1. **只有两个 `confirm_*` 工具会碰系统，且除非 worker 进程是 root 否则拒绝运行。** `plan_*` 与只读工具永远可用、永不改动。
2. **GPG 密钥信任决策只能走交互式 elicitation**：*"There is no tool argument that can pre-approve a key fingerprint — an LLM agent can only accept or reject a key through an interactive MCP elicitation round-trip, never by passing an argument that bypasses the prompt."* 这一条直接堵死「Agent 自己批准一个陌生签名密钥」的攻击面。
3. **`confirm_*` 在 RPM 事务真正开始前可取消，开始后绝不打断**：*"interrupting a live RPM transaction is a good way to corrupt the local package database."*

**架构（证据 B）**：Go proxy（说 MCP，stdio 或可选 HTTP）+ C++ worker（链 libzypp，掌管全部包管理逻辑）。**每次工具调用起一个全新的 `zypp-mcp-tool` 子进程，用完即退**——这既让 Go 侧永不碰 C++ ABI，也绕开 libzypp 的可重入约束（一次调用的库状态不会泄漏到下一次）。工具 schema 定义在 C++ 侧（`worker/src/tools/registry.h`），Go proxy 启动时用 `--list-tools` 动态发现。

> ⚠️ **关键缺口**：`check_updates` 只**列**可用更新，**没有 `confirm_upgrade`**。所以这个 MCP 能做「查有什么更新」+「装/删单个包」，**不能一键全系统升级**。要 `zypper update` / `zypper dup` 还得靠通用执行层。
> ⚠️ 0★，GPL-3.0（注意许可证传染性）。

#### ❌ `anjupathak03/zypper-mcp`（0★，**无许可证**）—— 只读，且不可用

- 14 个工具，全是只读：`search_packages`、`package_info`、`list_installed`、`list_updates`、`list_repos`、`what_provides`、`list_patches`、`patch_info`、`list_patterns`、`pattern_info`、`list_products`、`product_info`、`list_licenses`、`history`。
- 官方原文：*"Only read-only zypper operations are exposed; there are no install/remove/upgrade commands."*
- 所有命令带 `--non-interactive --no-refresh --color=never`；有小型 allowlist 阻止变更命令被调用。
- ⚠️ **仓库没有 LICENSE 文件**。无许可证 = 默认保留全部权利 = 不能合法使用/分发。

#### ❌ `lioilsources/LeapDoctor`（0★，无许可证）—— 只是一个 idea 记录

README 全文 317 字节，内容是 5 行想法草稿：

```
20/2/2026
- Idea: Ask Claude Code to update my new Suse Leap desktop
- provide right augmented context about desktop configuration to Claude
- provide MCP tool to know what commands to execute
- provide MCP tool to know weher to search for logs
- safety net by snapper to rollback on failure
```

无实现、无许可证。**不可用**。（但其思路——「用 snapper 快照做回滚网」——值得借鉴。）

### 3.4 Arch — `pacman`

#### `nihalxkumar/arch-mcp`（59★，GPL-3.0 OR MIT）—— 唯一专用 Arch MCP，但**没有全系统升级工具**

**可执行工具（Tools）全清单**（证据 B，按 README 分段）：

| 分段 | 工具 |
|---|---|
| 包管理 | `check_updates_dry_run`（检查可用更新）、**`install_package_secure`**（带安全检查安装，阻止恶意包）、`remove_packages`、`manage_orphans`（列/删孤儿包，**永远先 dry-run**）、`manage_install_reason`、`verify_package_integrity` |
| 镜像 | `optimize_mirrors`（status/test/suggest/health 四动作） |
| 系统状态 | `get_system_info`、`check_disk_space`、`check_failed_services`、`get_boot_logs`、`get_pacman_cache_stats` |
| 配置 | `analyze_pacman_conf`、`analyze_makepkg_conf` |
| 安全分析 | `analyze_pkgbuild_safety`（**50+ 红旗**）、`analyze_package_metadata_risk`（包信任评分：投票数/维护者/年龄） |
| 查询 | `query_package_history`（4 种查询：all / package / failures / sync）、`query_file_ownership`、`get_official_package_info`、`list_group_packages`、`list_package_groups` |
| 知识 | `search_archwiki`、`search_aur`、`get_latest_news`、`get_news_since_last_update`、`check_critical_news`、`check_database_freshness` |
| 诊断 | `troubleshoot_issue`、`audit_aur_package`、`analyze_dependencies` |

**资源（Resources，URI 形式）**：`pacman://installed`、`pacman://orphans`、`pacman://explicit`、`pacman://groups`、`pacman://group/*`、`pacman://database/freshness`、`pacman://log/recent`、`pacman://log/failed`、`archnews://since-update`、`config://pacman`、`mirrors://active`、`mirrors://health`。

**Prompts（引导式工作流）**：

| Prompt | 工作流 |
|---|---|
| `troubleshoot_issue` | 提关键词 → 搜 Wiki → 上下文建议 |
| `audit_aur_package` | 取元数据 → 分析 PKGBUILD → 安全建议 |
| `analyze_dependencies` | 查仓库 → 映射依赖 → 建议安装顺序 |
| **`safe_system_update`** | **检查关键 News → 验磁盘空间 → 列更新 → 检查服务 → 给建议** |

> ⚠️⚠️ **最重要的纠正**：`safe_system_update` **在 Prompts 段，不在 Tools 段**。它是一条「引导工作流」，输出是**建议**，**它不执行 `pacman -Syu`**。
> 这意味着 **arch-mcp 无法执行全系统升级**——它能装单个包（`install_package_secure`）、能查有什么更新（`check_updates_dry_run`）、能检查 Arch News、能分析 AUR 包风险，但**没有 `pacman -Syu` 的执行工具**。
> README 里**没有**任何关于 root / sudo / 权限提升的说明——它如何获得写权限未文档化，这本身是个需要自查的点。

**权限配置建议**（沿用前序报告结论）：arch-mcp 含写操作，接入时应设 `trust: untrusted` + `tools.include` 白名单。

### 3.5 NixOS — `nixos-rebuild`

NixOS 侧的 MCP 生态是全报告最丰富的（6 个以上），但**必须区分「查」与「改」**。

#### ⭐ `JEFF7712/nix-agent`（16★，Python，MIT）—— 唯一专用 `nixos-rebuild` 执行 MCP

- 官方原文：*"A local MCP server that gives AI agents composable NixOS / Home Manager operations: **build, diff, switch, and generations** for the operational core, plus **eval, locate, and check** for config introspection."*
- 与 `mcp-nixos` 明确配对：*"nix-agent operates on your actual configuration, `mcp-nixos` handles package and option discovery."*（一个改，一个查）
- 附带两个技能：`skills/nix-agent/SKILL.md`（工作流技能）与 `skills/nix-agent-init/SKILL.md`（仓库上手指南）
- 支持本地用量日志：`NIX_AGENT_USAGE_LOG=1` 记录逐调用字节计量，`nix-agent usage` 汇总

> ⚠️⚠️ **默认是「高信任」，低信任是「降级选项」**。官方原文：*"The documented default is **high trust**: unprompted `switch` / `generations` and **passwordless sudo narrowed to this machine's flake**. Lower trust (host prompts, a sudo password) is an **opt-down**."*
> 也就是说，**照文档装完，Agent 可以不经提示就 `nixos-rebuild switch` 并免密 sudo**。而且作者自述 *"Experimental and a work in progress."*
> 对比它自己的文档名 `docs/privileged-automation.md`（"default non-interactive dry-activate, switch, and rollback"）——它默认走 dry-activate 再 switch 再 rollback，比裸 switch 好，但仍是无人值守的 root 级系统变更。

#### `bolivian-peru/os-moda`（120★，Rust，Apache-2.0）—— 最完整的 NixOS agent OS，但自述研究级

- 定位：*"An operating system built for AI agents. You operate the server by talking to it."*
- **92 个结构化工具**，10 个 Rust 守护进程，v1.3.0，Apache-2.0
- 核心机制：
  - **SafeSwitch**：改 NixOS 配置 → 重建 → **健康检查失败则自动回滚**
  - **SHA-256 哈希链审计账本**（append-only ledger），结构化变更全部上链
  - `system_health` 返回 **JSON 而非文本**（不用正则去解析）
  - 因为 NixOS 每次变更都是一个带 generation 号的事务，回滚是一条命令
  - 可在 Claude Code（默认）/ OpenClaw / 云端 managed-agent 之间切换运行时，无需 SSH 或重建
- 官方示例：*"Install nginx and reverse-proxy port 3000" —— it edits NixOS config, rebuilds via SafeSwitch with auto-rollback if health checks fail.*

> ⚠️⚠️ **作者自己给出了极强的免责声明，必须原样转述**：
> - *"osModa is an ambitious **solo project** (~250 commits; 247 tests + a self-run pentest — **not** an external audit), **not battle-tested infrastructure**."*
> - *"the safety model has a **known gap** it's actively closing: the default runtime's native shell/file tools **aren't yet routed through the approval gate and audit ledger** (the hook that fixes this is built and wire-tested, but not yet verified end-to-end on a live box)"*
> - *"**Run it on a fresh, disposable server — not a production machine you care about.**"*
> - 组件成熟度不均：*"the runtime, the agentd contracts, and the ledger are solid; the mesh, the crypto wallet, voice, and the skill engine are earlier and less proven."*
> 结论：**想法最好，但当前不能上生产**。它值得作为架构参考（「用 NixOS 事务性做 Agent 的安全网」这个思路是对的），不适合直接部署。

#### 只读的 Nix 知识层（不能改系统）

| 项目 | ★ | 语言 | 许可 | 说明 |
|---|---:|---|---|---|
| **`utensils/mcp-nixos`** | **853** | Python | MIT | **只 2 个工具，约 1030 token**——作者明确以「省上下文」为设计目标（*"We consolidated 17 tools into 2 because your AI's context window isn't infinite."*）。覆盖 13 万+ 包、2.3 万+ 选项、Home Manager、nix-darwin、Nixvim、NVF、FlakeHub、Noogle、NixOS Wiki、nix.dev、版本历史、binary cache。**不需要装 Nix**（`uvx mcp-nixos`），支持 stdio / HTTP / Docker |
| `lukasl-dev/rime` | 19 | Rust | MIT | Nix / NixOS / Home Manager / nvf / Nixhub 查询；工具如 `nix_evaluate`、`nix_packages_search`、`nixos_wiki_search`、`nixos_channels`、`home_manager_options_search`。**全只读，无 switch** |
| `stubbedev/nix-mcp` | 1 | Go | MIT | mcp-nixos 的 Go 重写版，同样 2 工具面；单静态二进制（几十 MB RSS vs Python 运行时约 150 MB）；**支持 stdio + HTTP + MCP roots（含 `X-Mcp-Root` 头）**，一个 HTTP 实例可服务多个客户端 |
| `felixdorn/mcp-nix` | 7 | Python | GPL-3.0 | 覆盖 Nixpkgs、NixOS、Home Manager、Nix Darwin、Nixvim、Impermanence、MicroVM.nix、nix-nomad、sops-nix、nixos-hardware、disko；能搜 nix 标准库与函数定义、查某包存在于哪些 nixpkgs 版本 |

> ⚠️ **NixOS 的正确组合是「一个查 + 一个改」**：`mcp-nixos`（或 `nix-mcp` / `mcp-nix`）负责「这个选项叫什么、这个包在哪个版本」，`nix-agent` 负责 `build`/`diff`/`switch`。只装查询层，Agent 会编造选项名；只装执行层，Agent 会写错配置。

### 3.6 Snap — 完全没有

- 搜索 `snap package mcp server in:name,description` → **1 个结果**，且是 `canonical/discourse-mcp-snap`（把 Discourse MCP 打包成 strict snap），**与 snap 包管理无关**。
- Canonical（snap 的维护方）没有发布任何 snap 管理 MCP。
- **结论：`snap refresh` 没有任何专用 MCP，必须走通用 shell MCP。**

### 3.7 Flatpak — 只有空壳

| 仓库 | ★ | 语言 | 许可 | 实际情况 |
|---|---:|---|---|---|
| `lucasarakaki/flatpak-mcp-server` | 0 | PHP | MIT | **README 全文 27 字节**，内容只有标题 `# Flatpak MCP Server in PHP`。无工具说明、无安装方式。**实质是空壳**（证据 A：直接读到 27 字节） |
| `MVDW-Java/flatpak-doc-mcp` | 0 | Python | 无许可 | **只查 flatpak 文档**，不管理包 |
| `musmandev092/claude-desktop-flatpak-for-linux` | 1 | Python | MIT | 把 Claude Desktop 打成 flatpak，**不是 flatpak 管理** |
| `wanbnn/unity-mcp-flatpak` | 0 | Shell | MIT | 与 flatpak 包管理无关 |

- 搜索 `flatpak update install mcp in:name,description` → **0 个结果**。
- **结论：`flatpak update` 没有任何可用专用 MCP，必须走通用 shell MCP。**

---

## 第 4 章 通用兜底层

当专用 MCP 缺失（snap、flatpak、yum、Arch 全系统升级、zypper 全量升级）时，通用执行层是唯一出路。以下是本报告核验过的四个选项，按推荐度排序。

### 4.1 ⭐ `tumf/mcp-shell-server`（201★，MIT）—— 推荐首选

这是通用 shell MCP 里**设计最严谨**的一个。官方定位：*"A trusted execution server implementing the Model Context Protocol (MCP). It runs allowlisted commands as **argv arrays**, with stdin input, contained redirection, a minimal child environment, execution limits, and structured audit logging."*

**核心机制**（证据 A，README 全文直读）：

| 机制 | 实现 |
|---|---|
| **argv 数组执行** | *"Allowed commands run via subprocess argv **without shell-string interpretation**"* —— 从根上消除 shell 注入 |
| **安全管道** | *"Pipelines preserve and validate argv segments instead of invoking a shell"* |
| 白名单 | `ALLOW_COMMANDS`（命令名）或 **`ALLOW_PATTERNS`（完整匹配，含参数）** |
| 执行限制 | 服务端默认超时 + 最大超时 + 输出字节上限，全部强制 |
| **最小子环境** | 子进程只拿到小份白名单环境（`MCP_SHELL_CHILD_ENV_ALLOWLIST`），**不继承服务端全部密钥** |
| **结构化审计日志** | 事件名 `shell_execution_audit`，覆盖成功/拒绝/超时/输出超限/进程错误 |
| 审计脱敏 | 含 `SECRET`/`TOKEN`/`PASSWORD`/`API_KEY`/`PRIVATE_KEY`/`CREDENTIAL`/`AUTH` 等标记的 argv 与环境值替换为 `[REDACTED]`；长值转短 SHA-256 摘要；**审计日志不含原始 stdout/stderr** |

**默认参数加固**（证据 A，官方列出的拒绝清单）——这是它区别于其他 shell MCP 的关键：即使命令名被允许，以下参数形态仍被拒绝：

`find -exec`、shell/解释器启动器、`awk system()`、`tar --checkpoint-action=exec`、`env`、`xargs`、命令包装器 `timeout`/`nice`/`nohup`、shell 逃逸工具 `sed`/`less`/`vim`/`ssh`、常见替代名 `gfind`/`gawk`/`gtar`/`gsort`、GNU `sort` 的外部程序选项（`--compress-program`、`-o`/`--output`、`--files0-from`、`-T`/`--temporary-directory`，含缩写与聚合形式如 `--co`、`--o`、`-ro FILE`、`-rT DIR`）、**所有 Git 命令级配置覆盖**（`git -c <name=value>`）与持久 `git config` 写入。

**用于包管理的配置**：

```bash
# 用 ALLOW_PATTERNS 做「命令 + 参数」全匹配，而不是只放命令名
ALLOW_PATTERNS='^apt-get (update|upgrade|full-upgrade)$|^dnf (makecache|upgrade|check-update)$|^zypper (refresh|update|dup)$|^pacman -Syu$|^nixos-rebuild (dry-activate|switch)( --upgrade)?$|^snap refresh$|^flatpak update$'
ALLOW_COMMANDS='systemctl,journalctl,df,ss'
MCP_SHELL_CHILD_ENV_ALLOWLIST='LANG,LC_ALL'
```

> ⚠️⚠️ **官方明示的边界，必须原样转述**：
> - *"The measures below are the server's own enforceable boundary; **they are not an OS sandbox**. A command-name allowlist controls which executables the server launches directly, but an allowed program still runs with the server process's OS authority and may read accessible files, consume CPU, spawn child processes, or reach the network."*
> - *"The command-specific rejection rules described under Security are **best-effort defense in depth** against known dangerous argument forms. They are **non-exhaustive**, and they are **not a proof that an allowed program is safe**."*
> - *"Allowlisting a command name is **not a sandbox** for that program's own argument-level execution features."*
>
> 翻译成人话：**`ALLOW_COMMANDS="pacman"` 会允许 `pacman -Rdd`（跳过依赖检查强删）这种危险组合。要真正收紧，必须用 `ALLOW_PATTERNS` 全匹配，或者把执行层放进容器/VM。** 白名单降低暴露面，但不替代隔离边界。

### 4.2 `classfang/ssh-mcp-server` —— 多机场景

- 工具：`execute-command`（含超时）、`job-start`（远端后台任务，返回 `job_id`）、`upload`、`download`、`list-servers`
- 策略：`--whitelist` / `--blacklist`，**逗号分隔的正则表达式**
- **关键安全设计**（证据 B，中文 README 原文）：*"白名单按**完整命令匹配**；启用白名单时，包含 `;`、`&`、`|`、反引号、`$()`、`>`、`<` 或换行符的命令会被**直接拒绝**，不能使用命令连接、管道、重定向或命令替换绕过校验。"*
- 官方示例白名单：
  ```
  --whitelist "^ls(?: [A-Za-z0-9_./-]+)*$,^cat [A-Za-z0-9_./-]+$,^df(?: -[A-Za-z]+)*(?: [A-Za-z0-9_./-]+)?$"
  ```
- 官方警告：*"**强烈建议** 使用 `--whitelist` 选项来限制可执行的命令集合。如果没有白名单，任何命令都可以在远程服务器上执行，这可能带来重大的安全风险。"*
- 另一个细节：命令正常执行但以非零退出码结束时（如 `grep` 无匹配），**直接返回输出并附 `[exit code] N`**，不当作工具错误——这对 `dnf check-update`（有更新时返回 100）这类语义很重要。

**用于包管理的白名单**：

```
--whitelist "^apt-get (update|upgrade)$|^dnf (makecache|upgrade|check-update)$|^zypper (refresh|update|dup)$|^pacman -Syu$|^nixos-rebuild (dry-activate|switch)( --upgrade)?$|^snap refresh$|^flatpak update$"
```

> ⚠️ `nixos-rebuild switch` 通常耗时数分钟，会超过 `execute-command` 的超时。这类长任务应改用 `job-start` 后台任务（同样经过白名单校验）。

### 4.3 `rhel-lightspeed/linux-mcp-server`（317★，Apache-2.0）—— RHEL 系官方路径

- Red Hat 官方（`rhel-lightspeed` 组织），**默认工具集是结构性只读的**：命令硬编码成元组、具名占位符、无 shell 插值。
- **要执行包管理必须显式开启受保护命令执行**：`LINUX_MCP_TOOLSET=run_script|both`
- 三道护栏：Gatekeeper LLM + 人工介入 + OS 沙箱（官方自称 *"rudimentary"*）
- **硬编码策略**：*"No new repositories may be added"*、*"nothing may be downloaded from the internet"*（除预配置仓库）

> ⚠️ 两个已知问题（沿用前序报告结论）：
> 1. `LINUX_MCP_TRANSPORT=http` **没有认证**，官方警告不要用于生产或不可信网络。
> 2. **Gatekeeper 模型的评分表在官方文档里仍是 `??`（未公布）**——不要把它当唯一防线。
>
> 另一层限制：硬编码策略「不得添加新仓库」+「不得从互联网下载」，意味着这个工具集**在设计上就不适合做「更新系统」**——更新需要下载。它对 RHEL 的价值在只读诊断，不在包管理。

### 4.4 `iMANDexter/mcp-shell-server`（2★，MIT）—— 远程 shell，警告最直白

- 定位：*"Give an AI agent a real shell on your own Linux box — over HTTPS, behind a bearer token, with a full audit log."*
- 零依赖；TLS 走 acme.sh / Let's Encrypt；systemd 服务
- **官方警告原文**：*"⚠️ **This tool intentionally grants remote command execution.** Anyone holding the token can run commands as the service user — and as root if you granted sudo. Read Security before you deploy it, and **start with `--no-sudo`**."*
- 优点：警告写得诚实，`--no-sudo` 默认起步是正确姿势。

---

## 第 5 章 命名陷阱与假候选

本章记录检索过程中实际踩到的坑。**这些是「搜索第一名但完全不是你要的东西」的典型**。

### 5.1 ⚠️ `oborchers/mcp-server-pacman`（11★）—— 与 Arch Linux 毫无关系

搜索 `pacman mcp server` 排第一（11★，MIT）的项目，名字叫 pacman，README 里也确实写「Pacman MCP Server」，但：

> *"A Model Context Protocol server that provides package index querying capabilities. This server enables LLMs to search and retrieve information from package repositories like **PyPI, npm, crates.io, Docker Hub, and Terraform Registry**."*

它的工具是 `search_package`（index ∈ pypi/npm/crates/terraform）、`package_info`、`search_docker_image`、`docker_image_info`、`terraform_module_latest_version`。

**这里的 "pacman" 是「包管理器」的泛称（package manager 的缩写玩法），指的是编程语言包索引，不是 Arch 的 pacman。** 它完全不能 `pacman -Syu`。

### 5.2 ⚠️ `arch-mcp` 的 `safe_system_update` 是 Prompt 不是 Tool

见 §3.4。这是本报告最重要的一处纠正。判断依据：它在 README 的 `### Prompts (Guided Workflows)` 表里，不在 `### Tools (Executable Functions)` 表里；且描述结尾是 "Recommendations"（给建议）。

### 5.3 ⚠️ 搜索 `apt` 被 Aptos 区块链污染

`apt mcp server in:name,description` 返回 24 个结果，其中至少 8 个是 **Aptos 区块链**（`Tlazypanda/aptos-mcp-server`、`rishi-xyz/aptos-mcp`、`ctianming/moveflow_aptos_mcp_server`、`ToolOracle/aptoracle`、`Aptoide/aptoide-mcp`）、或 **Aptabase 分析**（`aptabase/aptabase-mcp`）、或**意大利房产爬虫**（`n3pt7un/apt_scrape`）、或 **AST 分析**（`clouatre-labs/aptu-coder`）。真正操作 Debian apt 的只有 2 个。

### 5.4 ⚠️ 搜索 `dnf` 被游戏污染

`dnf mcp in:name,description` 返回 1 个结果：`heihuo000/pvfUtility-MCP`，描述是 *"用于 pvfUtility 的 MCP 服务器 - **DNF 游戏文件**的 AI 辅助集成系统"*。这里的 DNF 是《地下城与勇士》(Dungeon & Fighter)。

### 5.5 无许可证 = 不可用

| 仓库 | 问题 |
|---|---|
| `anjupathak03/zypper-mcp` | 无 LICENSE 文件 → 默认保留全部权利 |
| `lioilsources/LeapDoctor` | 无 LICENSE 文件 |
| `openSUSE/mcp-bugzilla` | 搜索结果 `license: None`（虽然出自官方组织） |
| `E13ctr0N/AiSysAdmin` | 无许可证 |
| `domdomegg/shell-exec-mcp` | 搜索结果 `license: None` |

> ⚠️ 无许可证 ≠ 开源。GitHub 上公开可见的代码，默认是「保留全部权利」，**没有授权你使用**。企业内部用之前必须确认许可。

### 5.6 名字骗人的项目

| 仓库 | 名字暗示 | 实际是 |
|---|---|---|
| `amineutron/fedora-agents` | Fedora 系统管理 | **KVM/libvirt 虚拟机 + Borg/Timeshift 备份**，不碰 dnf |
| `oborchers/mcp-server-pacman` | Arch pacman | PyPI/npm/crates.io 索引查询 |
| `openSUSE/systemd-mcp` | openSUSE 包管理 | **systemd**，与包管理无关 |
| `lucasarakaki/flatpak-mcp-server` | flatpak 管理 | 27 字节空壳 |
| `musmandev092/claude-desktop-flatpak-for-linux` | flatpak | 把 Claude Desktop 打包成 flatpak |

---

## 第 6 章 推荐架构

### 方案 A · 专用 MCP 组合（按发行版各装一个）

适合：**单一发行版的固定环境**，要最好的工具语义和最小的权限面。

| 发行版 | 装什么 | 配置要点 |
|---|---|---|
| Debian / Ubuntu | **`brianlechthaler/apt-mcp`** | `APT_MCP_SCOPES=read` 起步；要升级改 `read,mutate`；变更工具必须传 `confirm: true` |
| Fedora / RHEL 系 | **`openSUSE/managesw-mcp`** | ⚠️ **接入前单独评估 `modify_repo`**（能改软件源）；建议先只用 `list_*` / `query_*` / `search_*` |
| openSUSE / SLES | **`openSUSE/mcp-server-zypp`**（查+单包）或 **`managesw-mcp`** | `plan_*` 免 root、`confirm_*` 必须 root；GPG 信任走交互 elicitation，别关掉 |
| Arch | **`nihalxkumar/arch-mcp`** | `trust: untrusted` + `tools.include` 白名单；⚠️ **全系统升级需兜底** |
| NixOS | **`JEFF7712/nix-agent`**（改）+ **`mcp-nixos`**（查） | ⚠️ nix-agent 默认高信任（免密 sudo + 无提示 switch），务必先按 `docs/privileged-automation.md` 走 dry-activate 路径 |
| snap / flatpak | — | **无专用 MCP，必须走方案 B 或 C** |

**这个方案的缺口**：Arch 全系统升级、zypper 全量升级、snap、flatpak 四项仍无覆盖 → 仍需方案 B/C 补。

### 方案 B · 统一 shell 执行层（多发行版混合环境推荐）

适合：**同时管 2 个以上发行版**，或需要覆盖 snap/flatpak。

**组件**：`tumf/mcp-shell-server`（201★，MIT）

```bash
# 用 ALLOW_PATTERNS 做「命令 + 参数」全匹配 —— 不要只放命令名
ALLOW_PATTERNS='^apt-get (update|upgrade|full-upgrade)$|^dnf (makecache|upgrade|check-update)$|^zypper (refresh|update|dup)$|^pacman -Syu$|^nixos-rebuild (dry-activate|switch)( --upgrade)?$|^snap refresh$|^flatpak update$'
ALLOW_COMMANDS='systemctl,journalctl,df,ss,uptime'
MCP_SHELL_CHILD_ENV_ALLOWLIST='LANG,LC_ALL'
```

为什么它比「给 Agent 一个 sudo shell」好：
- **argv 数组执行**，无 shell 字符串解释 → 无 `;` `&&` `|` 注入面
- **审计日志**：每次调用一条 `shell_execution_audit`，含脱敏 argv、有效 timeout、output_limit
- **最小子环境**：不继承服务端的 API key 等密钥
- 默认拒绝 `find -exec` / `xargs` / `env` / `timeout` / `sed` / `vim` / `ssh` / git `-c` 覆盖等已知逃逸向量

> ⚠️ 但仍必须配 OS 层隔离（容器 / VM / 专用用户）。官方明说它不是 OS 沙箱。

### 方案 C · SSH 集中式（多机）

适合：**一台工作台管 N 台机器**。

**组件**：`classfang/ssh-mcp-server`

```bash
--whitelist "^apt-get (update|upgrade)$|^dnf (makecache|upgrade|check-update)$|^zypper (refresh|update|dup)$|^pacman -Syu$|^nixos-rebuild (dry-activate|switch)( --upgrade)?$|^snap refresh$|^flatpak update$"
```

- 白名单按**完整命令匹配**；启用后含 `;` `&` `|` 反引号 `$()` `>` `<` 换行的命令**直接拒绝**
- `nixos-rebuild switch` 这类长任务用 `job-start` 后台任务（同样过白名单）

### 方案 D · 只读优先（推荐作为起点）

**先只读，再开写。** 每个发行版都能先接只读层：

| 发行版 | 只读层 | 能做什么 |
|---|---|---|
| Debian/Ubuntu | `apt-mcp`（`APT_MCP_SCOPES=read`） | `apt_list_upgradable`、`apt_simulate` |
| Fedora/openSUSE | `managesw-mcp` 的 `list_*` / `query_*` / `search_*` | 列更新、查补丁 |
| openSUSE | `mcp-server-zypp` 的 `check_updates` + `plan_*` | 列更新、dry-run 求解 |
| Arch | `arch-mcp` 的 `check_updates_dry_run` + `check_critical_news` + `get_news_since_last_update` | 列更新、读 Arch News |
| NixOS | `mcp-nixos` / `nix-mcp` + `nix-agent` 的 `build` / `diff` | 查包查选项、`nixos-rebuild build`（不 activate） |
| 全发行版 | `tumf/mcp-shell-server` 只放 `--version` / `list-updates` 类 | 统一只读巡检 |

跑通只读巡检 2 周、确认 Agent 的判断可靠之后，再逐条开写权限。这是前序报告里「AI agent 运维事故链」给出的最直接教训。

---

## 第 7 章 坑与反直觉

1. **`arch-mcp` 的 `safe_system_update` 是 Prompt，不是 Tool**——它给建议，不执行 `pacman -Syu`。
2. **`oborchers/mcp-server-pacman` 与 Arch 无关**——它查 PyPI/npm/crates.io。
3. **`snap` 和 `flatpak` 完全没有可用的专用 MCP**。flatpak 那个仓库 README 只有 27 字节。
4. **`yum` 不需要专用 MCP**——RHEL 8+/CentOS 8+ 里 yum 是 dnf 的符号链接。
5. **只有 `apt-mcp` 提供真正的全系统升级工具对**（`apt_update` + `apt_upgrade`）。其余全部只能装单个包或列更新。
6. **`openSUSE/managesw-mcp` 是唯一跨 zypper + dnf 的官方 MCP**，但只有 2★、单文件 8.6 KB。
7. **`managesw-mcp` 的 `modify_repo` 比装包危险得多**——它能新增/删除软件源，等于控制包来源。
8. **`mcp-server-zypp` 没有 `confirm_upgrade`**——只能查更新 + 装/删单包。
9. **`GdMacmillan/apt-mcp-server` 假设免密 sudo**，官方原文 *"Secure, passwordless `sudo` assumed for all operations"*。
10. **`brianlechthaler/apt-mcp` 是 0★ 但设计最好**——遵循 NSA PP-26-1834，`APT_MCP_SCOPES` 分层、无 shell、argv 严格、审计日志脱敏、版本化防 rug-pull。**星标与质量倒挂**。
11. **`JEFF7712/nix-agent` 默认高信任**——免密 sudo + 无提示 `switch`，低信任是「降级选项」。
12. **`bolivian-peru/os-moda` 作者自己说不要上生产**——默认运行时的 shell/文件工具**尚未接入审批门与审计账本**，且未做外部审计。
13. **`tumf/mcp-shell-server` 不是 OS 沙箱**——官方明说命令白名单不约束程序自身行为；`ALLOW_COMMANDS="pacman"` 会允许 `pacman -Rdd`。要用 `ALLOW_PATTERNS`。
14. **`arch-mcp` README 没有任何 root/sudo 说明**——它如何获得写权限未文档化，接入前必须自查。
15. **`oborchers/mcp-server-pacman` 和 `heihuo000/pvfUtility-MCP` 是检索污染**——前者是包索引，后者是 DNF 游戏。
16. **搜索 `apt` 有 8/24 是 Aptos 区块链**——加 `linux` 或 `debian` 限定词才能过滤。
17. **无许可证的仓库不能用**：`anjupathak03/zypper-mcp`、`lioilsources/LeapDoctor`、`E13ctr0N/AiSysAdmin`、`domdomegg/shell-exec-mcp` 等。
18. **`lioilsources/LeapDoctor` 只有 5 行想法**，无实现。
19. **`amineutron/fedora-agents` 不做包管理**——它是 KVM/libvirt + 备份，但它的 sudoers 逐脚本授权设计值得抄。
20. **`redwrench` 不在 Fedora 官方仓库也不在 COPR**——只能从 release 下 `.rpm` 手动装。
21. **`linux-mcp-server` 的硬编码策略禁止下载**——所以它**在设计上就不适合做系统更新**，只适合只读诊断。
22. **`LINUX_MCP_TRANSPORT=http` 无认证**，官方警告不要用于生产。
23. **NixOS 的更新是两阶段**（先 `nix flake update` / `nix-channel --update`，再 `nixos-rebuild switch`），合成一个「upgrade」工具会掩盖 flake 锁文件变更这个决策点。
24. **openSUSE Tumbleweed 必须用 `zypper dup`**，用 `update` 会遇依赖冲突。任何只暴露模糊 "upgrade" 的 MCP 在 Tumbleweed 上是错的。
25. **Arch 不要只 `pacman -Sy` 不 `-u`**（部分升级会炸系统）。白名单必须写成 `^pacman -Syu$` 全匹配。
26. **Fedora Silverblue / Kinoite / openSUSE MicroOS 是不可变系统**，不能用 `dnf install` / `zypper in`，要用 `rpm-ostree` / `transactional-update`。上面的所有 MCP 都没覆盖这一层。
27. **`apt-mcp` 的 `apt_upgrade` 是 `apt-get upgrade -y`**，不是 `full-upgrade`——它不会处理需要新增/删除依赖的升级。要 `full-upgrade` 得自己走 shell 层。
28. **`ssh-mcp-server` 启用白名单后含 `|` 的命令会被拒**——但 `dnf check-update` 返回 100 是正常语义，它已特殊处理（返回输出 + `[exit code] N`）。
29. **`nixos-rebuild switch` 会超时**——它跑几分钟，必须用 `job-start` 后台任务而不是 `execute-command`。
30. **GitHub Search API 未认证配额是 10 次/分钟**。本报告跑了 11 组查询，中间被限流 2 次，必须加 `sleep` 间隔。

---

## 第 8 章 未核实与覆盖边界

### 8.1 未取得一手证据的项

| 项 | 状态 | 原因 |
|---|---|---|
| `openSUSE/managesw-mcp` 的 dnf 后端实现细节 | 部分 | README 明确说支持 dnf；源码中后端在 `internal/pkg/syspackage`，未逐个文件读 |
| `arch-mcp` 的权限提升方式 | **未核实** | README 完全没提 root / sudo / polkit |
| `arch-mcp` 的 `install_package_secure` 是否真执行 pacman | 未核实 | 描述是「Install with security checks」，未读源码确认调用链 |
| `simonives/redwrench` 的星标与最新推送 | 未核实 | 本轮 core API 配额耗尽（60/60），仅有前序报告数据 |
| `amineutron/fedora-agents` 的星标与最新推送 | 未核实 | 同上 |
| `classfang/ssh-mcp-server` 的星标 | 未核实 | 同上 |
| `iMANDexter/mcp-shell-server` 的完整审计字段 | 部分 | 仅 README 摘要 |
| 各候选的许可证商业条款 | 未核实 | 多个仓库 `license.spdx_id` 为 `NOASSERTION` 或缺失 |
| `openSUSE/mcp-server-zypp` 是否计划加 upgrade 工具 | 未核实 | 未读 issue / roadmap |

### 8.2 明确的方法论边界

1. **本轮未做端到端实测**。所有能力断言来自 README 原文、源码文件直读或搜索结果元数据，**未实际部署任一 MCP 执行 `apt upgrade` / `dnf upgrade` 验证**。
2. **「未发现」不等于「不存在」**。snap / flatpak 的结论是「在 GitHub 检索中未发现可用的专用 MCP」，不排除存在未打关键词标签的私有项目。
3. **检索只覆盖 GitHub**。未检索 npm / PyPI / Glama / Smithery / PulseMCP 等 MCP 目录站。这些站点可能有 GitHub 描述里没写关键词的项目。
4. **未评估各 MCP 的代码质量与维护活跃度**。0★ 项目可能明天就停更。
5. **本轮 core API 配额耗尽**（14:25 时已 60/60），部分仓库的精确星标/推送日期只能引用前序报告或搜索结果快照（检索日 2026-10-12）。

### 8.3 与前序报告的关系

| 报告 | 解决的问题 |
|---|---|
| `研究报告_AI_Agent_Linux运维_全发行版.md` | 用 Hermes Agent 管 Linux 需要什么 MCP / Skills / 知识库方案 |
| `研究报告_通用Agent工作台选型_六项能力.md` | 除 Hermes Agent 外还有哪些通用 Agent 工作台可用 |
| **本报告** | **具体到 8 个包管理命令，每个发行版有哪些 MCP 可用** |

三份报告的执行层结论一致：**优先用专用 MCP（最小权限 + 可审计），缺失时用 `tumf/mcp-shell-server` 这类 argv 白名单执行层兜底，永远不要给 Agent 一个裸 sudo shell。**

---

## 附录 A 证据分级说明

| 等级 | 含义 | 本报告的典型来源 |
|---|---|---|
| **A** | 源码 / 文件直读，可复现 | `brianlechthaler/apt-mcp` 的 `docs/features/tools.md` 与 `docs/security.md`；`managesw-mcp.go` 的工具注册字段；`lucasarakaki/flatpak-mcp-server` 的 27 字节 README |
| **B** | 仓库 README 原文 | `nihalxkumar/arch-mcp` 的工具表；`openSUSE/mcp-server-zypp` 的八工具表；`tumf/mcp-shell-server` 的安全说明 |
| **C** | 仅搜索结果元数据 | 星标、许可证、推送日期 |
| **D** | 本报告推断 | 「`ALLOW_COMMANDS="pacman"` 会允许 `pacman -Rdd`」的推论；各方案适用场景判断 |

## 附录 B 可复现命令

### B.1 检索式（GitHub Search API）

```bash
# 未认证配额：search 10 次/分钟。必须加 sleep，否则会被限流
q(){ curl -s -m 25 "https://api.github.com/search/repositories?q=$(python -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$1")&sort=stars&order=desc&per_page=15" \
  | python -c "import sys,json;d=json.load(sys.stdin);[print(i['full_name'],i['stargazers_count'],(i.get('license') or {}).get('spdx_id'),i['pushed_at'][:10]) for i in d.get('items',[])]"; }

q "apt mcp server in:name,description"           # 注意过滤 Aptos 区块链噪声
q "dnf mcp in:name,description"                  # 注意过滤 DNF 游戏噪声
q "zypper mcp in:name,description"
q "pacman mcp server in:name,description"        # 第一名与 Arch 无关
q "nixos mcp in:name,description"
q "opensuse mcp server in:name,description"      # ← 找到 managesw-mcp 与 mcp-server-zypp
q "flatpak mcp in:name,description"
q "snap package mcp server in:name,description"  # → 0 个相关
q "shell command execution mcp server in:name,description"
q "ansible mcp server in:name,description"
q "nixos-rebuild mcp in:name,description,readme"
```

### B.2 直读源码确认工具集（比 README 可靠）

```bash
# managesw-mcp 的 9 个工具（Go 源码里的 Name/Description 字段）
curl -sL "https://raw.githubusercontent.com/openSUSE/managesw-mcp/main/managesw-mcp.go" \
  | grep -nE 'Name:|Description:'

# apt-mcp 的工具与 scope 划分
curl -sL "https://raw.githubusercontent.com/brianlechthaler/apt-mcp/main/docs/features/tools.md"
curl -sL "https://raw.githubusercontent.com/brianlechthaler/apt-mcp/main/docs/security.md"
```

### B.3 方案 B 的完整配置（`tumf/mcp-shell-server`）

```bash
# 只放「命令 + 参数」全匹配，不要只放命令名
export ALLOW_PATTERNS='^apt-get (update|upgrade|full-upgrade)$|^dnf (makecache|upgrade|check-update)$|^zypper (refresh|update|dup)$|^pacman -Syu$|^nixos-rebuild (dry-activate|switch)( --upgrade)?$|^snap refresh$|^flatpak update$'
export ALLOW_COMMANDS='systemctl,journalctl,df,ss,uptime'
export MCP_SHELL_CHILD_ENV_ALLOWLIST='LANG,LC_ALL'
```

### B.4 方案 A 的 `apt-mcp` 配置

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
要开变更：把 `APT_MCP_SCOPES` 改为 `read,mutate`，且每个变更工具必须传 `confirm: true`。

### B.5 各发行版的只读巡检命令（可作起点）

```bash
# Debian / Ubuntu
apt list --upgradable

# Fedora / RHEL 系
dnf check-update            # 有更新时退出码 100，属正常
dnf updateinfo list security

# openSUSE
zypper list-updates
zypper list-patches

# Arch
pacman -Qu
checkupdates                # pacman-contrib 提供，不锁数据库
# 升级前必读 Arch News

# NixOS
nixos-rebuild dry-build     # 不 activate
nixos-rebuild dry-activate

# 通用
snap refresh --list
flatpak update --appstream && flatpak remote-ls --updates
```

## 附录 C 参考链接

| 项目 | 链接 |
|---|---|
| `brianlechthaler/apt-mcp` | https://github.com/brianlechthaler/apt-mcp |
| `GdMacmillan/apt-mcp-server` | https://github.com/GdMacmillan/apt-mcp-server |
| `openSUSE/managesw-mcp` | https://github.com/openSUSE/managesw-mcp |
| `openSUSE/mcp-server-zypp` | https://github.com/openSUSE/mcp-server-zypp |
| `openSUSE/systemd-mcp` | https://github.com/openSUSE/systemd-mcp |
| `nihalxkumar/arch-mcp` | https://github.com/nihalxkumar/arch-mcp |
| `JEFF7712/nix-agent` | https://github.com/JEFF7712/nix-agent |
| `bolivian-peru/os-moda` | https://github.com/bolivian-peru/os-moda |
| `utensils/mcp-nixos` | https://github.com/utensils/mcp-nixos |
| `lukasl-dev/rime` | https://github.com/lukasl-dev/rime |
| `stubbedev/nix-mcp` | https://github.com/stubbedev/nix-mcp |
| `felixdorn/mcp-nix` | https://github.com/felixdorn/mcp-nix |
| `simonives/redwrench` | https://github.com/simonives/redwrench |
| `amineutron/fedora-agents` | https://github.com/amineutron/fedora-agents |
| `tumf/mcp-shell-server` | https://github.com/tumf/mcp-shell-server |
| `classfang/ssh-mcp-server` | https://github.com/classfang/ssh-mcp-server |
| `rhel-lightspeed/linux-mcp-server` | https://github.com/rhel-lightspeed/linux-mcp-server |
| `iMANDexter/mcp-shell-server` | https://github.com/iMANDexter/mcp-shell-server |
| NSA MCP 安全设计考量 (PP-26-1834) | https://www.nsa.gov/Portals/75/documents/Cybersecurity/CSI_MCP_SECURITY.pdf |

---

*报告完 · v1.0 · 2026-10-12 · 11 组检索式 × 20 个 MCP × README/源码直读 · 证据分级见附录 A · 未核实项见第 8 章*
