# 用 Hermes Agent / OpenClaw 做 Fedora / Debian / Ubuntu 运维：MCP / Skills / 软件方案全清单

> 第四轮专项调研 · 调研日期 **2026-10-12**
> 前三轮：`research_report_hermes_openclaw_linux_ops.md`（框架机制）、`research_report_nixos_ai_agent_ecosystem.md`（NixOS）、`research_report_arch_ai_ops_ecosystem.md`（Arch）
> 证据分级：**A** = 官方仓库 API/源码直读可复现 · **B** = 项目 README/官方文档原文 · **C** = 项目自述未独立复现 · **D** = 本报告推断

---

## §0 TL;DR

**这三家共享一个决定性事实：它们都跑 systemd。** 所以对你最有用、最该先装的运维 MCP **不是**任何发行版专属的，而是 **`openSUSE/systemd-mcp`** —— 厂商官方组织维护、MIT、通过 **polkit / OAuth2 双授权**、**默认不允许写操作**、有独立 `gatekeeper` 提权守护进程。装一个覆盖 Fedora + Debian + Ubuntu。

发行版差异集中在两处：**包管理器**（`dnf` / `apt`）和**强制访问控制**（Fedora = SELinux + firewalld；Debian/Ubuntu = AppArmor）。

| | **Fedora** | **Debian** | **Ubuntu** |
|---|---|---|---|
| 最值得装的 MCP | **`simonives/redwrench`**（Rust，策略引擎先于执行）+ `amineutron/fedora-agents` | **`copyninja/debsecan-mcp`** → 已更名 **`debvulns`** | `pazuzu1w/ubuntu_mcp_server`（44★ 但 2025-06 停更） |
| 官方自动更新 | `dnf-automatic` | `unattended-upgrades` | `unattended-upgrades` + **Pro/ESM + Livepatch** |
| 重启需求检测 | `dnf needs-restarting`（在 `dnf5-plugins` 里） | `needrestart` | `needrestart` |
| 漏洞扫描 | `dnf updateinfo` / Bodhi | **`debsecan`** + `debvulns` | `pro security-status` / `debsecan` |
| ClawHub 技能生态 | **单件最热**（`fedora-linux-triage` 观测 8.9k） | **最薄** | **最丰富**（10+ 件，最多 1.3k 安装） |
| awesome-copilot 专家 | ✅ `fedora-linux-triage` | ✅ `debian-linux-triage` | ❌ **没有** |
| 强制访问控制 | **SELinux**（+ `firewalld`） | AppArmor | AppArmor（+ snap 自带 confinement） |
| 独有坑 | **不可变系统**（Silverblue/Kinoite：`dnf install` 直接失败）+ **.deb-only 软件要自己重打包** | 内核升级后**不自动重启**，只提示 | **Pro/ESM 是付费订阅**，不绑就没有扩展支持 |

**一句话结论**：`systemd-mcp` + `informant/unattended-upgrades/dnf-automatic` 这类**机制型**安全闸门 + 发行版专属的**漏洞扫描 MCP**，比"给 agent 一个 shell"可靠一个数量级。

**⚠️ 一条贯穿全轮的教训**：r/linuxadmin 在 2026 年记录了一整条 **AI agent 运维事故链**——GuardFall（bash 注入打穿大多数 coding agent）、CVE-2026-59822（LiteLLM MCP 鉴权绕过，进 CISA KEV）、CVE-2026-42271（MCP-bridge 子进程命令注入）。共同失败模式是：**鉴权逻辑信任"重建出来的路径"、"后缀匹配"或"回退对象"，而不是做硬校验。**

---

## §1 通用基座：`openSUSE/systemd-mcp` ⭐（本轮的答案）

**这是四轮调研里唯一一个由发行版厂商官方组织维护、且安全模型完整到可以照抄的 Linux 运维 MCP。**

| 项 | 值 |
|---|---|
| 仓库 | `github.com/openSUSE/systemd-mcp` |
| 维护方 | **openSUSE 官方组织**（非个人项目） |
| 许可 / 语言 | **MIT** / Go |
| 版本 / 最后提交 | **0.3.5** / 2026-09-24 |
| Stars | 10 |
| 关键实现 | **直接通过 systemd 的 C API 连接，不需要 `systemctl`** |
| 安装 | `make build && sudo make install` |

`sudo make install` 会装：`/usr/bin/systemd-mcp`、`/usr/sbin/gatekeeper`、`gatekeeper.service` + `gatekeeper.socket` 两个 systemd unit、以及 **gatekeeper 的 polkit policy**。

**6 个工具**：

| 工具 | 作用 |
|---|---|
| `list_units` | 列出 unit，可按状态（`running`/`failed`）或模式过滤；`mode='files'` 列出所有已安装 unit 文件 |
| `change_unit_state` | 改 unit 状态（start/stop/restart/reload/enable/disable） |
| `check_restart_reload` | 检查 restart/reload 状态（仅在 job 超时后可用） |
| `list_log` | 取指定 service/unit 的最近日志 |
| `get_file` | 读系统文件（内容 + 元数据，支持分页） |
| `get_man_page` | 取 man page（可按 section/chapter 过滤 + 分页） |

**安全模型（这是它最值得抄的部分）**：

| 传输方式 | 授权机制 |
|---|---|
| **stdio（默认）** | **polkit**。unit 操作触发 `org.freedesktop.systemd1.manage-units` 请求。**读操作永远放行**（调用者就是运行 server 的本人）；**只有写操作**触发 polkit |
| **HTTP** | **OAuth2**，audience `systemd-mcp-server`，scope `mcp:read` / `mcp:write` |

**日志访问的三级降级**（设计很讲究）：

1. 如果以 root 运行、或在 `/var/log/journal` 同组 → 直接读全部 journal
2. 否则连 `gatekeeper` 守护进程（`/run/gatekeeper/gatekeeper.socket`）→ 触发 polkit `com.suse.gatekeeper.readlog`
3. 若 gatekeeper 不可用 → 只读当前用户能读的 journal（如自己的 `user-<uid>.journal`），**并在输出里明确提示访问被缩减**

**默认安全的关键 flag**：

| flag | 默认 | 说明 |
|---|---|---|
| `--allow-write` / `-w` | **false** | 默认**不允许**写 systemd。要写必须显式打开 |
| `--allow-read` / `-r` | false | 授权读 |
| `--enabled-tools` | all | 逗号分隔的工具白名单 |
| `--noauth` | — | 关闭鉴权。**必须把值写成字面量 `ThisIsInsecure`** ——故意制造摩擦，防止误用 |
| `--timeout` | 5 | polkit 认证超时（秒） |
| `--toon` | false | 输出改用 token 优化的 object notation |
| `--log-json` | false | 机器可读日志 |

> **为什么它对你最重要**：`--allow-write` 默认 false + 读操作免授权 + 写操作走 polkit + `--noauth` 需要字面量确认，这套组合把"agent 能不能动我的系统"变成了一个**默认安全、需要显式提升**的问题。这比写一句"不要执行危险命令"进 `AGENTS.md` 强得多。

**跨发行版可用性**：Fedora / Debian / Ubuntu 全部默认 systemd → **直接可用，无需任何发行版适配**。

---

## §2 Fedora 专属

### 2.1 `simonives/redwrench` —— 策略引擎先于执行的 Fedora MCP ⭐

| 项 | 值 |
|---|---|
| 仓库 | `github.com/simonives/redwrench` |
| 语言 / 许可 | **Rust** / **MIT OR Apache-2.0** |
| 形态 | `.rpm` 发布（Fedora 专用）+ tarball；**有 CI + release** |
| Stars | 未核验（GitHub API 限流，见 §10） |
| 状态 | 作者明示**业余项目**；**尚未进 COPR 或 Fedora 官方仓库** |

**作者动机（原话，非常典型）**：

> "I keep a few old machines at home running Fedora … I wanted an AI coding agent to look after them for me: simple things like restarting a service, chasing down a bad config, or running the odd diagnostic. … **However I didn't want to hand the agents a shell on these machines.**"

**核心机制**：

- **每一个 agent 发来的命令，先过策略引擎，再决定能不能跑**（"decides what they may run **before it runs anything at all**"）
- **每一次调用都写进 systemd journal —— 无论是被允许还是被拒绝**（审计闭环）
- **四个内置 tier**：`safe` / `standard` / `developer` / `unrestricted`，自定义规则可叠加，**不用改一行代码**
- `developer` tier 必须指定 `developer_user`（真实账户名），**没设 server 拒绝启动**；该 tier 下的 `bash`/`python3`/`gcc`/`npm`/`cargo` 以该用户身份运行而**不是 root**
- `timeout_secs` 默认 30（慢镜像上跑 `dnf install` 要调大）
- 目标机**不需要装任何 agent 工具**；可以是标准版或**不可变版**（Silverblue/Kinoite），KDE/GNOME/Server 都行
- 支持 Claude Code、Codex、Google Antigravity 等任何 MCP 客户端

**为什么用 Rust**（作者论证）：server 会 spawn 任意进程、流式读输出、前置强制策略决策 → 需要内存边界与并发状态的严格保证。引用了 **NSA 与白宫国家网络总监**都建议弃用 C/C++ 转向 Rust 的公开表态。

**安装**：

```sh
# 从 release 装（推荐）
sudo dnf install ./redwrench-*.rpm      # 同时装 man page + systemd unit
# 或从源码
sudo dnf install -y cargo rust systemd-devel gcc pkgconf-pkg-config
git clone https://github.com/simonives/redwrench && cd redwrench
cargo build --release
sudo install -m 0755 target/release/redwrench /usr/local/bin/redwrench
```

配置片段（`tier` / `developer_user` / `timeout_secs`）：

```toml
tier = "standard"                 # safe | standard | developer | unrestricted
developer_user = "your-username-here"   # 仅 tier="developer" 时必需
timeout_secs = 120                # 慢镜像上 dnf install 要调大
```

> ⚠️ **`unrestricted` tier 等于放弃它全部价值。** 从 `standard` 起步。

### 2.2 `amineutron/fedora-agents` —— 权限表驱动的 KVM/备份 MCP

| 项 | 值 |
|---|---|
| 仓库 / 包名 | `github.com/amineutron/fedora-agents` / npm **`fedora-agents-mcp`** |
| 语言 / 许可 | TypeScript / **MIT**；有 CI |
| 覆盖 | **KVM/libvirt 虚拟机** + **Borg/Timeshift 备份** |
| 安装 | `npx fedora-agents-mcp`（`--help` 列设置项） |

**它的安全模型是四轮调研里文档化程度最高的**：

1. **每个工具声明两个 flag**：`requiresSudo`（**逐脚本** sudoers 条目，**绝不用全局 sudo**）与 `dangerous`（向 MCP 客户端声明为破坏性 → 客户端必须做人确认）
2. **server 启动时如果发现某个暴露的工具没有权限表条目，直接拒绝启动** ← **fail-closed on unregistered tools**，这是很硬的设计
3. 权限表由 `src/config.ts` 生成（`npm run security:table`），**且在 CI 里校验**
4. **每个工具调用生成 correlation ID**，JSON 审计日志**在回复 agent 之前同步落盘**
5. **重试取决于工具性质**：只有幂等读（`vm_status`/`backup_status`/`backup_list`/`backup_verify`）重试 3 次（1s/2s/5s 退避）；**任何变更操作永不重试**；校验或权限错误立即中止
6. **退出码翻译成类型化 `ErrorCode`**（超时/锁被占/空间不足…），而不是丢一段文本给 agent 猜

**完整权限表（来自 SECURITY.md，19 个工具）**：

| 工具 | sudo | 破坏性 | 作用 |
|---|---|---|---|
| `help` | 否 | 否 | 列出可用工具 |
| `vm_status` | 否 | 否 | 显示 VM 状态 |
| `vm_start` | 否 | 否 | 启动 VM |
| `vm_stop` | 否 | **是** | 停止 VM（可能丢失未保存数据） |
| `vm_exec` | 否 | **是** | 在 VM 内执行命令 |
| `vm_copy` | 否 | **是** | 与 VM 互拷文件 |
| `vm_snapshot` | 否 | **是** | 管理 VM 快照 |
| `vm_verify` | 否 | 否 | 校验 VM 是否为宿主机的忠实副本 |
| `vm_destroy` | **是** | **是** | 永久删除 VM（定义 + 存储）：**不可逆** |
| `vm_clone` | **是** | 否 | 克隆现有 VM |
| `vm_clone_system` | **是** | **是** | 克隆宿主机到 VM（耗时） |
| `vm_export` | 否 | 否 | 导出 VM 为可移植归档（含消毒，classic/exam 模式） |
| `vm_import` | **是** | **是** | 从 `vm_export` 归档导入 VM |
| `backup_status` | **是** | 否 | 备份面板 |
| `backup_list` | **是** | 否 | 列出可用备份 |
| `backup_verify` | **是** | 否 | 校验备份完整性 |
| `backup_create` | **是** | 否 | 创建新备份 |
| `backup_restore` | **是** | **是** | 恢复备份（**破坏性**） |
| `backup_clean` | **是** | **是** | 按保留策略删除备份 |

**威胁模型表（可直接搬进你的安全设计文档）**：

| 威胁 | 缓解 |
|---|---|
| agent 请求销毁 VM | `vm_destroy` 标为 `dangerous` → 客户端人确认；每次调用 JSON 审计 |
| 在 VM 名或路径里注入 | 调用脚本前用 **Zod 严格模式校验** |
| 权限提升 | **逐脚本 sudoers**（root 副本 + 仅限这些路径的 `NOPASSWD`）；libvirt 走 `libvirt` 组（polkit）；**`virsh`/`virt-clone`/`qemu-img` 上没有任何 sudo 规则**（那等于 root） |
| 恢复了错误的备份 | `backup_restore` 标为 `dangerous`；标识符用正则校验 |

**它明确声明不做的事**：不从 agent 文本构造 shell 命令（参数经 Zod 校验后作为**独立参数**传入，**绝不插值**）；不写配置路径（`PATHS`）之外的任何位置；**不产生任何网络输出**（仅 stdio + 本地脚本）。

### 2.3 Fedora 官方工具链（均已核验）

| 工具 | 状态 | 作用 |
|---|---|---|
| **`dnf-automatic`** | 存在于 Fedora 44 / 45 / Rawhide（`packages.fedoraproject.org` 命中；mdapi 不索引该 noarch 子包） | 自动下载/安装更新（官方文档 `docs.fedoraproject.org/en-US/quick-docs/autoupdates/`） |
| `dnf5` | 5.4.6.0-1.fc44（mdapi 核验） | 命令行包管理器 |
| **`dnf5-plugins`** | 5.4.6.0-1.fc44（mdapi 核验） | 含 **`needs-restarting`**（重启需求检测）、`config-manager`、`copr`、`builddep` 等 |
| **`rpm-ostree`** | 2026.3-2.fc44（mdapi 核验） | 混合镜像/包系统（Silverblue/Kinoite 的基础） |
| `toolbox` | 0.3-4.fc44（mdapi 核验） | 交互式命令行环境容器 |

> **Fedora 的重启检测在 `dnf5-plugins` 里**，命令是 `dnf needs-restarting`（不是 `needrestart`）。这是与 Debian/Ubuntu 的一个实操差异。

### 2.4 Fedora 独有的两个坑

**坑 1：不可变系统上 `dnf install` 直接失败。**

r/Fedora `1szch0g`（"Fedora Kinoite is underrated"）原话：

> "What I got was a system where my first instinct — **`dnf install tmux` — just does[n't work]**."

不可变版（Silverblue / Kinoite / Bazzite）需要 `rpm-ostree install` 分层，或者用 `toolbox`/`distrobox` 容器。**给 agent 的指令里必须区分"标准 Fedora"与"Fedora Atomic"。** 这也是 ClawHub 上出现 `silverod/rpm-ostree-toolkit`（721 安装）和 `mina-atef-00/hermes-browser-fedora-atomic`（190 安装）的原因。

**坑 2：很多 AI 工具只发 `.deb`，Fedora 用户得自己重打包。**

r/Fedora `1w190ij` 原话：

> "Anthropic finally ships a Linux build, **but only as a .deb**. This repo takes that exact package and adapts it for Fedora as a proper RPM. No more hacking the Windows installer, which broke on recent versions anyway (app opened, Code tab dead)."

**结论：Ubuntu/Debian 优先拿到官方 AI 工具包，Fedora 用户常处于"自己重打包"的位置。** 评估工具链时要考虑这个分发摩擦。

### 2.5 Fedora 在技能市场的覆盖

| 技能 | 安装/观测 | 说明 |
|---|---|---|
| **`githubskills.sh/awesome-copilot/fedora-linux-triage`** | **观测 8.9k** ⭐ | Fedora 专家 triage（详见 §5） |
| `xejrax/brew-install` | 3.1k | "Install missing binaries via **dnf** (Fedora/Bazzite)" |
| `silverod/rpm-ostree-toolkit` | 721 | **Fedora Atomic / Bazzite** 不可变系统管理（rpm-ostree 分层） |
| `mina-atef-00/hermes-browser-fedora-atomic` | 190 | **Hermes 专用**：浏览器在 Fedora Atomic / bootc 上失败时用 |

**Fedora 是三个发行版里"单件技能最热"的**（8.9k 观测）。

---

## §3 Debian 专属

### 3.1 `debvulns`（原 `debsecan-mcp`）—— Debian 漏洞分析三件套

| 项 | 值 |
|---|---|
| 仓库 | `github.com/copyninja/debsecan-mcp` |
| **PyPI 包名** | **`debvulns`**（⚠️ 旧名 `debsecan-mcp` 停在 0.1.5，之后所有开发都在 `debvulns`） |
| Stars | 5；有 CI + Codecov |
| 安装 | `pip install debvulns` |

**一个包，三种接口**：

| 接口 | 命令 | 用途 |
|---|---|---|
| **MCP server** | `debvulns-mcp` | 接入 Claude Desktop / VSCode / opencode 做 AI 辅助漏洞分析 |
| **独立 CLI** | `debvulns` | 命令行扫描，输出 JSON 或 CSV |
| **Prometheus exporter** | `debvulns-exporter` | 暴露漏洞指标给 Grafana 做面板与告警 |

**能力**：

- 扫描**所有已安装包**的已知漏洞
- **CVE 研究**：取指定 CVE 详情，**含 EPSS 分数**（Exploit Prediction Scoring System，即"这个洞被实际利用的概率"）
- **自动识别 Debian suite**（bookworm / trixie / sid…）
- 首次运行下载漏洞库与 EPSS 数据并本地缓存（默认 `/var/cache/debvulns`，不可写则退到 `~/.cache/debvulns`），**超过 24 小时自动刷新**
- 支持按严重度过滤：`critical` / `high` / `medium` / `low` / `negligible`

> **为什么 EPSS 重要**：它把"有 CVE"和"值得今晚就修"区分开了。纯 CVE 列表会让 agent 淹没在噪音里。

### 3.2 Debian 官方工具链（版本经 `sources.debian.org` API 核验）

| 包 | 版本（核验日） | suite | 作用 |
|---|---|---|---|
| **`unattended-upgrades`** | **2.13** | forky, sid | 自动安全更新。⚠️ **默认不自动重启，即使装了新内核也只提示** |
| **`needrestart`** | **3.11-1** | trixie, forky, sid | 库升级后检测哪些服务需要重启 |
| **`debsecan`** | **0.4.20.2** | forky, sid | 基于 Debian Security Tracker 的漏洞扫描 |
| `apt-listchanges` | 4.8+nmu3 | forky, sid | 升级前展示 changelog / NEWS |
| `debian-goodies` | 0.88.2 | trixie, forky, sid | 含 `checkrestart`、`dglob`、`apt-get` 辅助脚本 |

**Debian 侧的标准安全闸门组合**：

```bash
sudo apt install unattended-upgrades needrestart debsecan apt-listchanges apt-listbugs
sudo dpkg-reconfigure -plow unattended-upgrades    # 启用自动安全更新
sudo debsecan --suite bookworm --format detail     # 漏洞扫描
sudo needrestart -r l                              # 列出需要重启的服务
```

> ⚠️ **`unattended-upgrades` 默认不重启。** 内核/glibc 更新后系统仍跑旧代码，直到你手动重启。**这是 Debian/Ubuntu 最常见的安全假象**——"我开了自动更新所以安全了"，实际上一堆服务还在跑有洞的旧库。`needrestart` 就是用来暴露这件事的。

### 3.3 Debian 在技能市场的覆盖：三个发行版里最薄

| 技能 | 观测/安装 | 说明 |
|---|---|---|
| `cepheiden/openbot-esxi` | 1.9k | "Zero-touch **Debian 13** VM deployment on VMware ESXi 8"，构建 custom preseed |
| `nvidiaskills.sh/holoscan-install-debian` | 1.8k | NVIDIA Holoscan SDK 的 Debian/apt 安装（**领域专用，非运维通用**） |
| `xixu-meskills.sh/secure-linux-web-hosting` | 13 | 把云服务器变成安全可达的 Web 主机 |

**没有 Debian 通用的系统管理/巡检/加固技能。** Debian 用户要用技能得自己写，或者借用 Ubuntu 的（apt 生态兼容度高）。

---

## §4 Ubuntu 专属

### 4.1 `pazuzu1w/ubuntu_mcp_server`（44★，但已停更）

| 项 | 值 |
|---|---|
| Stars | **44**（三个发行版专属 MCP 里最高） |
| 最后提交 | **2025-06-29** ⚠️ |
| 描述 | "an mcp server built to give claude config **limited control** over ubuntu os operations" |

**它是 Ubuntu 侧 star 最高的专属 MCP，但已停更约 16 个月。** 用之前必须自己审源码。作者的设计意图（"limited control"）方向是对的，但**长期未维护的、能操作操作系统的 MCP** 是明确的风险项。

### 4.2 Ubuntu Pro / ESM / Livepatch / Landscape（Ubuntu 独有的运维面）

这是 **Ubuntu 与 Fedora、Debian 最大的结构性差异**：Ubuntu 把"安全更新"做成了**付费订阅 + 集中管理**的产品。

| 组件 | 作用 |
|---|---|
| **Ubuntu Pro** | 订阅制。**ESM（扩展安全维护）** 把安全补丁覆盖期延长到**十年以上** |
| **Livepatch** | **在不重启的情况下打高危/严重内核 CVE 补丁**。LTS 绑定 Pro 订阅后**自动启用** |
| **Landscape** | 集中式面板，可在**舰队规模**上管理 Livepatch 配置与机器状态 |
| `pro` 客户端 | 本地管理订阅、ESM、Livepatch 状态 |

```bash
# 查看 Ubuntu Pro / ESM / Livepatch 状态
pro status
pro security-status                 # 包的安全更新状态
sudo pro enable livepatch
# 舰队规模用 Landscape（自托管或 SaaS）
```

> **对 AI 运维的含义**：Ubuntu 侧的"安全闸门"可以是**订阅状态检查**——`pro security-status` 会直接告诉你哪些包已经过了标准支持期、没有安全更新。这比"读 CVE 列表"更接近"我到底安不安全"。

### 4.3 Ubuntu 在技能市场的覆盖：三个发行版里最丰富 ⭐

**这是本轮的一个反直觉发现**：虽然 awesome-copilot **没有** Ubuntu 专家技能（见 §5），但 ClawHub 上 Ubuntu 的技能生态**明显比 Fedora 和 Debian 丰富**——因为 Ubuntu 是最常见的服务器发行版。

| 技能 | 安装 | 说明 |
|---|---|---|
| `zelzaclaw/doc-sysadmin` | 1.3k | "Especialista TI Ubuntu 24.04"——管宿主机的磁盘、内存、RAM 等 |
| `linsuisheng034/ubuntu-browser-session` | 1.2k | 需要真实 Ubuntu Server 浏览器会话时用 |
| **`chengchiangwork/ubuntu-inspector`** | 1k | **Ubuntu 系统巡检**：CPU、内存、磁盘、网络、服务状态、安全审计 |
| `kklouzal/ubuntu-encyclopedia` | 951 | **文档优先工作流**：Ubuntu 专属问题先查文档再答 |
| `solomonneas/proxmox-create-vm` | 951 | 在 Proxmox VE 上建 Ubuntu 24.04 LXC / VM |
| `solomonneas/hyperv-create-vm` | 914 | 在 Windows Hyper-V 上用 cloud-init 建 Ubuntu 24.04 VM |
| `shenzheke/ubuntu-wsl-system-cleanup` | 842 | **审计并安全清理** Ubuntu 24.04 的系统垃圾、缓存、日志、临时文件 |
| `twinsgeeks/ubuntu-ai` | 789 | 在 Ubuntu/Debian 上搭本地 AI 平台 |
| `krishnakumarmahadevan-cmd/toolweb-ubuntu-hardening`（+ `-v2`） | 681 / 685 | 生成专业 Linux 安全加固配置文件（22.04 LTS） |
| `twinsgeeks/ubuntu-ollama` | 682 | 在 Ubuntu 上跑 Ollama + 多机路由 |
| `microsnow/wsl-service-deploy` | 449 | WSL Ubuntu 服务一键部署（`wsl.exe` + `su -c root` + aptitude，无需 SSH） |
| `svetlyoh/gmail-connect` | 155 | 在 Ubuntu 上给 OpenClaw 接 Gmail（本地 OAuth 向导） |

> **注意 `ubuntu-encyclopedia` 的设计**：它是"**文档优先**工作流"——Ubuntu 专属问题先查文档再回答。这和 Arch 的 `arch-wiki-mcp`（§第三轮）、r/archlinux 的"Wiki 优先"规范是**同一个模式**，说明"用文档锚定 agent"已经成为跨发行版的共识做法。

### 4.4 snap 的额外注意

Ubuntu 默认带 snap。`snap` 有自己的 confinement 机制和更新节奏（`snap refresh` 独立于 `apt`）。**给 agent 的更新流程里要明确覆盖两条通道**（`apt` + `snap`），否则会出现"apt 说全更新了，但 snap 包还是旧的"。

---

## §5 `github/awesome-copilot` 发行版专家矩阵（A 级核验）

**GitHub 官方 `awesome-copilot` 仓库（55k★）里有成套的发行版专家技能。** 路径是 `skills/<name>/SKILL.md`（部分旧的仍在 `agents/<name>.agent.md`）。

| 技能 | 路径 | 存在性（HTTP） |
|---|---|---|
| **`fedora-linux-triage`** | `skills/fedora-linux-triage/SKILL.md` | **200 ✅** |
| **`debian-linux-triage`** | `skills/debian-linux-triage/SKILL.md` | **200 ✅** |
| `arch-linux-expert` | `agents/arch-linux-expert.agent.md` | **200 ✅** |
| `ubuntu-linux-triage` | 探测 6 个变体名 | **全部 404 ❌** |

**⚠️ Ubuntu 没有对应的专家技能** —— 尽管 Ubuntu 是三者里技能市场最丰富的。这是个明显的空白（可能是 `debian-linux-triage` 被认为已覆盖 Ubuntu）。

**两个 triage 技能的内容对比**（都是同一个模板骨架）：

| 维度 | `fedora-linux-triage` | `debian-linux-triage` |
|---|---|---|
| description | "Triage and resolve Fedora issues with **dnf, systemd, and SELinux-aware** guidance" | "Triage and resolve Debian Linux issues with **apt, systemd, and AppArmor-aware** guidance" |
| 输入参数 | `${input:FedoraRelease}`（可选）/ `${input:ProblemSummary}` / `${input:Constraints}`（可选） | `${input:DebianRelease}`（可选）/ 同上 |
| 工具 | `systemctl`、`journalctl`、**`dnf`** | `systemctl`、`journalctl`、**`apt`**、**`dpkg`** |
| 安全模块 | **SELinux** + `firewalld` | **AppArmor** 或防火墙 |
| 通用要求 | 每个主要改动后给验证命令；给回滚/清理步骤 | 同左（+ "ask concise follow-ups if required"） |

**统一输出格式**（两者一致，可直接当模板用）：

```
- Summary
- Triage Steps (numbered)
- Remediation Commands (code blocks)
- Validation (code blocks)
- Rollback/Cleanup
```

> **这两个技能的价值不在"聪明"，在"骨架正确"**：强制编号步骤、强制验证命令、**强制回滚/清理**、并强制区分发行版的安全模块。**"强制回滚"这一条就值得抄进任何自建运维 skill。**
>
> **注意它明确区分 SELinux（Fedora）与 AppArmor（Debian/Ubuntu）** —— 这正是"发行版专属"的实际含义：不是命令不同，是**权限模型不同**。

**安装方式**（`gh skill` 或直接拷文件）：

```bash
# 方式 1：拷进 Hermes 技能目录
mkdir -p ~/.hermes/skills/fedora-linux-triage
curl -sL https://raw.githubusercontent.com/github/awesome-copilot/main/skills/fedora-linux-triage/SKILL.md \
  -o ~/.hermes/skills/fedora-linux-triage/SKILL.md
mkdir -p ~/.hermes/skills/debian-linux-triage
curl -sL https://raw.githubusercontent.com/github/awesome-copilot/main/skills/debian-linux-triage/SKILL.md \
  -o ~/.hermes/skills/debian-linux-triage/SKILL.md
```

---

## §6 AI agent 运维的安全事故链（r/linuxadmin，2026）

**r/linuxadmin 在 2026 年系统性地记录了"AI agent 管 Linux"这件事翻车的案例。** 这些不是理论风险，是已进 CISA KEV 的实际利用。

### 6.1 GuardFall —— 用几十年前的 bash 技巧打穿 coding agent

r/linuxadmin `1unxuvf`："Decades-Old Bash Tricks Expose AI Coding Agents to Supply Chain Attacks"

**关键结论**：攻击名 **GuardFall**，用 bash 注入手法绕过大多数 coding agent 的防护。评论区：

> **u/yourapostasy**："**Continue was the only agent that resisted these injection attacks named GuardFall**, but was discontinued after the team behind it was aquihired by Cursor earlier in 2026."
> **u/cachevexy**："wild that the only one that held up got aquihired and shut down lol kinda proves the point that **we're building on shaky foundations if a random bash trick can own most of these agents**"

**含义**：agent 的注入防护不是"配好了就安全"的静态属性。**一个几十年前的 bash 技巧就能打穿多数实现**，而唯一防住的那个已经停止维护了。

### 6.2 CVE-2026-59822 —— LiteLLM MCP 鉴权绕过（进 CISA KEV）

**这个直接命中"用 LiteLLM 给 MCP 工具做网关"的架构。**

| 项 | 值 |
|---|---|
| 组件 | LiteLLM 的 MCP Streamable HTTP endpoint |
| 机制 | 该 endpoint 支持对上游 MCP server 做 OAuth2 passthrough。**当请求的 LiteLLM key 校验失败时，回退路径本应转交 passthrough 逻辑，实际却替换成一个空的 `UserAPIKeyAuth()` 对象**。下游代码把它当成合法会话 |
| 净效果 | **任何带伪造 `Authorization` 头的请求都能到达 MCP endpoint，可以列出已配置的工具并调用它们。全程不需要任何有效 key** |
| CVSS v4 | **8.8**（AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N） |
| 修复版本 | **1.84.0** |
| 临时缓解 | 在反向代理上**阻断 `/mcp/` 路由** |

**同族**：LiteLLM 今年**第二次进 KEV**。CVE-2026-42271（**MCP-bridge 子进程命令注入**，修复于 1.83.7）6 月进 KEV，且据第三方分析**可与 Starlette Host-header 漏洞 CVE-2026-48710 串联**。

> ⚠️ **如果你在 LiteLLM 前面挂 MCP 工具链，必须确认两个修复都已越过（1.83.7 与 1.84.0），而不是只打最新的那个。**

### 6.3 共同失败模式（这条最有价值）

CISA 把这批和另外 6 个在野利用的 CVE（Starlette、Kestra、Artifactory、Switchvox、SonicWall SMA 1000）打包发布，原文总结：

> "**most share the same failure class: auth logic trusting a reconstructed path, a suffix match, or a fallback object instead of doing a hard check**"

**翻译成运维 checklist**：

1. **不接受"重建出来的路径"做鉴权**（路径归一化后再判，别用拼接结果）
2. **不用后缀匹配做鉴权**（`endsWith('/mcp')` 这类判断可被绕过）
3. **回退路径绝不返回"空但合法"的对象**（失败就是失败，不要 `return UserAPIKeyAuth()`）

### 6.4 同批次其它相关事件

| 事件 | 要点 |
|---|---|
| **CVE-2026-9198**（Langflow） | `GET /api/v1/auto_login` **给任何网络调用者签发 SUPERUSER JWT**，无鉴权、不绑定 loopback。进 CISA KEV（8 月 4 日） |
| **RovoBlast**（Atlassian Rovo，DEF CON 34 / Varonis） | 单个 URL 参数 `rovoChatPrompt` 预填聊天入口 → 劫持 Rovo AI 助手。影响 Jira/Confluence/Bitbucket + 50 多个 SaaS connector |
| **Cryptographic Context Injection**（Adversa AI） | **把 prompt injection 载荷加密**，让分类器读不到，再让模型自己解密执行 |
| **DNS-AID**（Linux Foundation） | 开源 DNS-based discovery for AI agents——生态开始出现"agent 发现"的基础设施层 |
| `atraxsrc/claude-revoke`（3★，2026-10-10） | **审计并撤销 Claude Code 在 Linux 上被授予的一切**：trusted folders、"always allow" 列表等。**这是给 agent 做"权限回收"的工具**，值得关注 |

> **对 Fedora/Debian/Ubuntu 运维的直接含义**：你要装的 MCP server 越多，上面这些失败类别的暴露面越大。**优先选"默认禁写 + 显式提权"的 server（如 `systemd-mcp`、`redwrench`），而不是"给 agent 一个 shell"的通用执行器。**

---

## §7 跨发行版的实用 MCP（VM / 容器 / 监控 / 配置管理）

这些不区分发行版，但对"用 agent 管一批 Fedora/Debian/Ubuntu 机器"是刚需。

### 7.1 虚拟化

| 项目 | Stars | 说明 |
|---|---|---|
| **`gilby125/mcp-proxmox`** | 53 | Proxmox 虚拟化管理，**权限可配置** |
| `ry-ops/proxmox-mcp-server` | 27 | 管理 Proxmox VE 的 VM/容器/存储（**2026-10-11 仍在提交**） |
| `bsahane/mcp-proxmox` | 21 | 较旧（2025-11） |

### 7.2 容器

| 项目 | Stars | 说明 |
|---|---|---|
| **`manusa/podman-mcp-server`** | **84** | Podman + Docker 容器运行时 MCP |
| `Kiln-AI/Kilntainers` | 51 | **给每个 agent 一个临时 Linux 沙箱**执行 shell |
| `elusznik/mcp-server-code-execution-mode` | **340** | 在**隔离的 rootless 容器**里执行 Python，可配选项 |

### 7.3 SSH 远程执行（收窄版）

| 项目 | Stars | 说明 |
|---|---|---|
| **`muchiny/bridge-mcp`** | 10 | 安全 SSH 远程管理，**337 个工具 / 74 个分组**（2026-10-09） |
| `Cosmicjedi/linux-administration-mcp` | 2 | SSH Linux 管理，含完整日志 |
| `E13ctr0N/AiSysAdmin` | 2 | AI 辅助 Linux 管理（OpenAI/Anthropic 均可） |
| `mge1512/mcp-server-admintasks` | 2 | Linux 管理任务执行器 |

### 7.4 监控 / 变更追踪

| 项目 | Stars | 说明 |
|---|---|---|
| **`Higangssh/homebutler`** | **300** | **"只告诉你值得告诉你的事"** —— 单 Go 二进制，报告服务器上的变更（2026-10-12 活跃） |
| `initMAX/zabbix-mcp-server` | 229 | Zabbix 完整 API，**237 个工具**，多 server、OAuth 2.1 + bearer |
| `SikamikanikoBG/homelab-monitor` | 218 | 单容器 homelab 面板（GPU / 本地 AI VRAM / Docker / systemd） |
| `tyxak/remotepower` | 74 | 一体化服务器与舰队管理（Web UI），含 **patching** |
| `bjeans/homelab-mcp` | 43 | homelab 基础设施管理 MCP |

### 7.5 配置管理（跨发行版的"正解"方向）

| 项目 | Stars | 说明 |
|---|---|---|
| `sibilleb/AAP-Enterprise-MCP-Server` | 33 | Ansible Automation Platform (AAP) + Event-Driven Ansible |
| `bsahane/mcp-ansible` | 30 | MCP Ansible Server（较旧，2025-10） |
| `jade-pico/antrieb-mcp-server` | 14 | "Real VMs for your LLM. Provision, execute, validate."（LLM4Ops） |
| `imatza-rh/mcp-zuul` | 21 | Zuul CI 的 MCP（Red Hat 关联） |

> **Ansible 是 Fedora/Debian/Ubuntu 三者的天然交集**：同一份 playbook 覆盖三家（`dnf` 与 `apt` 模块）。**如果目标是一个混合舰队，"让 agent 写 Ansible 再跑 Ansible"比"让 agent 直接 SSH 执行命令"可控得多** —— 因为 playbook 可审、可 diff、可回滚、可版本化。这条建议在本轮所有材料里都成立。

---

## §8 推荐栈：三发行版各自可直接抄

### 8.1 通用（三家都装）

```bash
# ① systemd-mcp：厂商官方维护，默认禁写，polkit 授权
git clone https://github.com/openSUSE/systemd-mcp && cd systemd-mcp
make build && sudo make install
# 默认不授权写；要允许写才加 --allow-write（且会触发 polkit 确认）
```

```yaml
# ~/.hermes/config.yaml
mcp_servers:
  systemd:
    command: "/usr/bin/systemd-mcp"
    args: []                      # 不加 -w → 默认只读
    lazy: true
    trust: untrusted              # 写操作要走审批
    tools:
      include: ["list_units", "list_log", "get_man_page", "get_file"]
      exclude: ["change_unit_state"]   # 要改 unit 时再单独放开
```

### 8.2 Fedora

```bash
# 策略引擎先于执行的 Fedora MCP（从 release 装 .rpm）
sudo dnf install ./redwrench-*.rpm
# 官方自动更新 + 重启检测
sudo dnf install dnf-automatic dnf5-plugins
sudo systemctl enable --now dnf-automatic.timer
dnf needs-restarting -r          # 是否需要重启
# 不可变系统（Silverblue/Kinoite）改用：
# rpm-ostree install <pkg>       # 不要用 dnf install
```

```toml
# /etc/redwrench/config.toml（或作者指定路径）
tier = "standard"                # safe | standard | developer | unrestricted
timeout_secs = 120
```

```bash
# 技能
mkdir -p ~/.hermes/skills/fedora-linux-triage
curl -sL https://raw.githubusercontent.com/github/awesome-copilot/main/skills/fedora-linux-triage/SKILL.md \
  -o ~/.hermes/skills/fedora-linux-triage/SKILL.md
```

### 8.3 Debian

```bash
# 漏洞分析三件套（MCP + CLI + Prometheus）
pip install debvulns
debvulns --severity high          # 只看 high 以上
# 官方安全闸门
sudo apt install unattended-upgrades needrestart debsecan apt-listchanges apt-listbugs
sudo dpkg-reconfigure -plow unattended-upgrades
sudo needrestart -r l             # ⚠️ 关键：列出跑着旧库的服务
sudo debsecan --suite bookworm --format detail
```

```bash
# 技能
mkdir -p ~/.hermes/skills/debian-linux-triage
curl -sL https://raw.githubusercontent.com/github/awesome-copilot/main/skills/debian-linux-triage/SKILL.md \
  -o ~/.hermes/skills/debian-linux-triage/SKILL.md
```

### 8.4 Ubuntu

```bash
# Pro / ESM / Livepatch 状态（Ubuntu 独有）
pro status
pro security-status
sudo pro enable livepatch
# 官方安全闸门（与 Debian 相同）
sudo apt install unattended-upgrades needrestart
# ⚠️ snap 是独立通道，必须单独覆盖
snap refresh --list
```

```bash
# 技能（ClawHub 上最丰富的生态，挑这几个）
# chengchiangwork/ubuntu-inspector        系统巡检
# kklouzal/ubuntu-encyclopedia            文档优先工作流
# shenzheke/ubuntu-wsl-system-cleanup     安全清理
# krishnakumarmahadevan-cmd/toolweb-ubuntu-hardening  加固配置生成
```

### 8.5 混合舰队：走 Ansible

```bash
# 三个发行版一份 playbook（dnf / apt 模块自动适配）
# 让 agent 写 playbook → 你审 → 再执行。可 diff、可回滚、可版本化。
```

---

## §9 坑与反直觉

1. **最好的运维 MCP 不是发行版专属的。** `openSUSE/systemd-mcp`（厂商官方、MIT、polkit 授权、默认禁写）覆盖 Fedora/Debian/Ubuntu 全部——因为它们都跑 systemd。**先装它，再考虑发行版专属件。**
2. **`openSUSE/systemd-mcp` 默认 `--allow-write` = false。** 这不是遗漏，是设计。要写 systemd 必须显式打开，且会触发 polkit 确认。`--noauth` 甚至要求把值写成字面量 `ThisIsInsecure`。
3. **Fedora 的重启检测不是 `needrestart`。** 是 `dnf needs-restarting`，且在 `dnf5-plugins` 包里。Debian/Ubuntu 才是 `needrestart`。
4. **`unattended-upgrades` 默认不重启。** 装了新内核也只提示。系统仍跑旧代码 → **"我开了自动更新所以安全了"是 Debian/Ubuntu 最常见的安全假象**。`needrestart` 就是用来戳破它的。
5. **Debian 的 MCP 包名改过。** `debsecan-mcp` 停在 0.1.5，**之后全在 `debvulns`**。搜旧名会装到死版本。
6. **Ubuntu 的 star 最高 MCP 已停更 16 个月。** `pazuzu1w/ubuntu_mcp_server`（44★）最后提交 2025-06-29。**能操作操作系统的、长期未维护的 MCP = 明确风险项**，用前必须自己审源码。
7. **awesome-copilot 有 Fedora 和 Debian 专家技能，但没有 Ubuntu 的。** 探测 6 个 Ubuntu 变体名全部 404。Ubuntu 用户直接用 `debian-linux-triage`（apt 生态兼容）。
8. **两个 triage 技能真正的差异是权限模型，不是命令。** Fedora 版带 **SELinux + firewalld**，Debian 版带 **AppArmor**。这才是"发行版专属"的实际含义。
9. **Fedora 不可变版上 `dnf install` 直接失败。** Silverblue/Kinoite/Bazzite 要 `rpm-ostree install` 或 `toolbox`。**给 agent 的指令必须区分"标准 Fedora"和"Fedora Atomic"**，否则它会一直报同一个错。
10. **很多 AI 工具只发 `.deb`。** Anthropic 的 Claude Desktop Linux 版只发 `.deb`，Fedora 用户得自己重打包成 RPM。**Ubuntu/Debian 优先拿到官方包，Fedora 常在"自己重打包"的位置。**
11. **`fedora-agents` 的 fail-closed 设计值得抄：暴露的工具没有权限表条目就拒绝启动。** 绝大多数 MCP server 是"没登记就默认放行"，它反过来。
12. **`fedora-agents` 对变更操作永不重试。** 只有幂等读重试 3 次（1s/2s/5s）。**"重试"在运维场景是危险默认值**——agent 网络抖动重试一次 `vm_destroy` 就是灾难。
13. **`redwrench` 的审计日志连"被拒绝"的调用也记。** 只记成功的审计是半个审计。**审计的价值在于能看到"谁试图做什么但被拦了"。**
14. **CVE-2026-59822 的教训是"回退对象不能是空但合法"。** LiteLLM 在校验失败时返回空 `UserAPIKeyAuth()`，下游当成合法会话 → 任何伪造 Authorization 头都能调 MCP 工具。**失败就返回失败。**
15. **LiteLLM 今年两次进 KEV，修复版本是 1.83.7 和 1.84.0。** 只打最新那个不够。**在 LiteLLM 前挂 MCP 工具链的必须两个都过。**
16. **GuardFall 证明 agent 的注入防护不是静态属性。** 几十年前的 bash 技巧打穿多数 coding agent，唯一防住的那个（Continue）已被收购停维护。**别把"我选了防护好的 agent"当成安全边界。**
17. **Ubuntu 有两条更新通道（apt + snap）。** 只做 apt 会出现"apt 说全更新了，snap 包还是旧的"。给 agent 的流程必须显式覆盖两条。
18. **Ubuntu Pro / ESM 是订阅，不是配置。** `pro security-status` 会直接告诉你哪些包已过标准支持期、没有安全更新——这比读 CVE 列表更接近"我到底安不安全"。
19. **ClawHub 上 Ubuntu 技能最丰富，但 Debian 最薄。** 同为 apt 系，Ubuntu 有 10+ 件（最多 1.3k 安装），Debian 只有 3 件且都是领域专用（ESXi / NVIDIA）。**Debian 用户可借用 Ubuntu 的技能。**
20. **Ansible 是混合舰队的正解方向。** 同一份 playbook 覆盖 dnf 与 apt。**"让 agent 写 playbook → 你审 → 再跑"比"让 agent 直接 SSH 执行"可控得多**（可 diff、可回滚、可版本化）。
21. **`ubuntu-encyclopedia` 用"文档优先"设计，和 Arch 的 `arch-wiki-mcp`、r/archlinux 的"Wiki 优先"是同一个模式。** "用文档锚定 agent"已是跨发行版共识。

---

## §10 未核实 / 存疑

- **`simonives/redwrench` 的 star 数、release 数量、issue 状态未核验** —— GitHub API 在本轮触达未认证限流（`remaining 0 / 60`），`api.github.com/repos/simonives/redwrench` 返回 429。README 经 `raw.githubusercontent.com` 读取成功（B 级）。**作者自述是业余项目、未进 COPR 或 Fedora 官方仓库。**
- `amineutron/fedora-agents` 同样因限流未拿到 star 数/许可证字段（README 与 SECURITY.md 读取成功，B 级）。
- `copyninja/debsecan-mcp` 同样未拿到 star 数（README 成功）。
- **`redwrench` 的四个 tier 具体允许/拒绝哪些命令，未逐条核验**（README 只给了 tier 名称与设计说明）。用前必须自己读策略文件。
- **`openSUSE/systemd-mcp` 的 6 个工具未实际调用测试**；`gatekeeper` 的 polkit policy 实际内容未逐行核验（C 级）。
- `pazuzu1w/ubuntu_mcp_server` 的 44★ 与实际能力未复现；**已停更约 16 个月**，风险自评。
- `debvulns` 的 EPSS 数据源与刷新机制未实测（C 级，来自 README）。
- **各发行版官方工具的"AI 友好性"未评估** —— `dnf-automatic`、`unattended-upgrades`、`needrestart` 是否输出机器可读格式、是否适合 agent 解析，本轮未验证。
- ClawHub 的"安装量"是平台自报的观测值，**不同技能之间可比性存疑**（有 "Updated 5mo ago" 与 "Observed 6d ago" 两种口径混用）。
- **未做**：r/Ubuntu 与 r/debian 的 AI 运维讨论深挖（本轮 r/debian / r/Ubuntu 搜索结果与 AI 运维相关性低，只有零散个案）；`snap` 与 agent 交互的实际坑；Ubuntu Pro 定价与 AI 运维的成本模型；RHEL/CentOS/Rocky 系列（本轮未覆盖）。
- **本轮未覆盖但相邻**：`CVE-2026-9198`（Langflow）、`RovoBlast`（Atlassian）、`Cryptographic Context Injection` 的完整技术细节——均来自 r/linuxadmin 转述的第三方分析（C 级），未回原始报告核验。

**抓取失败与解法（本轮新增）**：

| 目标 | 现象 | 解法 |
|---|---|---|
| `api.github.com/repos/simonives/redwrench` 等 | **`API rate limit exceeded … remaining 0/60`** | 改用 `raw.githubusercontent.com` 读 README（成功）；star 数留空并标注 |
| `github.com/github/awesome-copilot/tree/main/agents` | WebFetch 返回空内容（GitHub HTML 页通病） | **改用 `raw.githubusercontent.com` 逐路径探测 HTTP 状态码**（200/404）——这个方法高效且确定 |
| `mdapi.fedoraproject.org/f44/pkg/dnf-automatic` | `400 Bad Request` | mdapi **不索引 noarch 子包**；改用 `packages.fedoraproject.org/search?query=` 确认存在 |
| `clawhub.ai/skills?q=...` | 部分查询无结果 | 换关键词重试；安装量口径需注意 |
| Reddit 匿名后端 | 反复 429（约 1 请求/分钟/IP） | 脚本自动等待重试；串行调用 |

---

## §11 参考来源

**通用基座**
1. `github.com/openSUSE/systemd-mcp` — 官方 openSUSE 组织维护的 systemd MCP（MIT，Go，v0.3.5，polkit/OAuth2 双授权）

**Fedora**
2. `github.com/simonives/redwrench` — Rust 策略引擎 Fedora MCP（MIT OR Apache-2.0，`.rpm` 发布）
3. `github.com/amineutron/fedora-agents` / npm `fedora-agents-mcp` — KVM + Borg/Timeshift MCP（MIT，含 SECURITY.md 权限表）
4. `docs.fedoraproject.org/en-US/quick-docs/autoupdates/` — `dnf-automatic` 官方文档
5. `packages.fedoraproject.org/search?query=dnf-automatic` — Fedora 44/45/Rawhide 存在性核验
6. `mdapi.fedoraproject.org/f44/pkg/{dnf5,dnf5-plugins,rpm-ostree,toolbox}` — 版本核验
7. r/Fedora `1szch0g` — Kinoite 不可变系统与 `dnf install` 失败
8. r/Fedora `1w190ij` — Claude Desktop 只有 `.deb`，社区重打包为 RPM
9. r/Fedora `1u2msrz` — "AI agent runs amok in Fedora and elsewhere"（评论质疑是账号失陷而非 AI）

**Debian**
10. `github.com/copyninja/debsecan-mcp` → PyPI `debvulns` — Debian 漏洞分析（MCP + CLI + Prometheus，EPSS 集成）
11. `sources.debian.org/api/src/{unattended-upgrades,needrestart,debsecan,apt-listchanges,debian-goodies}` — 版本与 suite 核验

**Ubuntu**
12. `github.com/pazuzu1w/ubuntu_mcp_server` — 44★，2025-06-29 后停更
13. `ubuntu.com/security/livepatch/docs/` — Livepatch 官方文档（不重启打高危内核 CVE）
14. `ubuntu.com/tutorials/manage-livepatch-configurations-at-scale-with-landscape` — Landscape 舰队级管理
15. `documentation.ubuntu.net.cn/pro-client/` — Ubuntu Pro 客户端文档

**发行版专家技能**
16. `github.com/github/awesome-copilot` → `skills/fedora-linux-triage/SKILL.md`（HTTP 200）
17. `github.com/github/awesome-copilot` → `skills/debian-linux-triage/SKILL.md`（HTTP 200）
18. `github.com/github/awesome-copilot` → `agents/arch-linux-expert.agent.md`（HTTP 200）
19. `ubuntu-linux-triage` 及 6 个变体名 — **全部 404，Ubuntu 无对应专家技能**

**AI agent 运维安全（r/linuxadmin）**
20. `1unxuvf` — GuardFall：几十年历史的 bash 技巧打穿 AI coding agent
21. `1w5yvf5` — **CVE-2026-59822** LiteLLM MCP 鉴权绕过（CVSS v4 8.8，修复 1.84.0，进 CISA KEV）
22. `1vl6ofz` — **CVE-2026-9198** Langflow `auto_login` 未鉴权签发 SUPERUSER JWT
23. `1vm56v9` — **RovoBlast**：Atlassian Rovo 经单 URL 参数被劫持（DEF CON 34 / Varonis）
24. `1vu37hc` — **Cryptographic Context Injection**：加密 prompt injection 载荷绕过分类器
25. `1ts0gip` — Linux Foundation 发布 **DNS-AID**（AI agent 的 DNS 发现）
26. CISA KEV 同批次（Starlette / Kestra / Artifactory / Switchvox / SonicWall SMA 1000）——共同失败模式："auth logic trusting a reconstructed path, a suffix match, or a fallback object"

**跨发行版 MCP（VM / 容器 / 监控 / 配置管理）**
27. `gilby125/mcp-proxmox`（53★）、`ry-ops/proxmox-mcp-server`（27★）、`bsahane/mcp-proxmox`（21★）
28. `manusa/podman-mcp-server`（84★）、`Kiln-AI/Kilntainers`（51★）、`elusznik/mcp-server-code-execution-mode`（340★）
29. `muchiny/bridge-mcp`（10★，337 工具）、`Cosmicjedi/linux-administration-mcp`、`E13ctr0N/AiSysAdmin`
30. `Higangssh/homebutler`（300★）、`initMAX/zabbix-mcp-server`（229★）、`SikamikanikoBG/homelab-monitor`（218★）、`tyxak/remotepower`（74★）、`bjeans/homelab-mcp`（43★）
31. `sibilleb/AAP-Enterprise-MCP-Server`（33★）、`bsahane/mcp-ansible`（30★）、`jade-pico/antrieb-mcp-server`（14★）
32. `atraxsrc/claude-revoke`（3★）— 审计并撤销 Claude Code 在 Linux 上的全部授权

**技能市场**
33. `clawhub.ai/skills?q=fedora` — fedora-linux-triage（观测 8.9k）、rpm-ostree-toolkit（721）、hermes-browser-fedora-atomic（190）、brew-install（3.1k）
34. `clawhub.ai/skills?q=debian` — openbot-esxi（1.9k）、holoscan-install-debian（1.8k）
35. `clawhub.ai/skills?q=ubuntu` — ubuntu-inspector（1k）、doc-sysadmin（1.3k）、ubuntu-browser-session（1.2k）、ubuntu-encyclopedia（951）等 10+ 件

**前四轮报告**
36. `research_report_hermes_openclaw_linux_ops.md` — 框架机制、五文件分工、MCP 上下文税、CVE-2026-84289
37. `research_report_nixos_ai_agent_ecosystem.md` — NixOS 四层生态、沙箱共识
38. `research_report_arch_ai_ops_ecosystem.md` — Arch MCP / Skills / 官方仓库基座 / AUR 供应链安全
