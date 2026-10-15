---
id: hermes-openclaw-linux-ops-agent-stack
title: 用 Hermes Agent / OpenClaw 做 Linux（Arch、NixOS、Fedora/Debian/Ubuntu、RHEL 系、openSUSE）运维：profile / MCP / 技能 / 知识库选型
tags: [Hermes-Agent, OpenClaw, MCP, NixOS, Arch-Linux, Fedora, Debian, Ubuntu, RHEL, Red-Hat, openSUSE, AUR, systemd, knowledge-base, llm-wiki, agent-profile, sandbox, security]
created: 2026-10-12
updated: 2026-10-15
version: 5
status: stable
source: 本机 Hermes 仓库源码与官方文档审计 + GitHub API / raw 核验 + PyPI + Arch 官方包库 API + Fedora mdapi + Debian sources API + r/NixOS、r/archlinux、r/Fedora、r/linuxadmin 原帖实抓 + clawhub.ai / skills.sh / AUR RPC 实测 + CISA KEV 披露 + Red Hat 官方文档与源码（rhel-lightspeed）
confidence: 已核实
type: Checklist
---

# 用 Hermes Agent / OpenClaw 做 Linux 运维

## TL;DR

Hermes 官方 65 个 MCP、152 个可选技能里**没有任何 NixOS / Arch / Ansible / SSH 运维件**——运维必须自建。最小可行栈 = `SOUL.md` 安全底线 + 项目 `AGENTS.md` + 原生 `llm-wiki` 知识库 + 只读查询 MCP + 带白名单的远程执行 + **沙箱**。知识库选型顺序是 **文件 → MCP → RAG**，不要跳步。

**NixOS 与 Arch 的生态形状完全不同，结论不可互套。** NixOS = 声明式 + 社区答案是**沙箱**（jailed-agents、nix-sandbox-mcp、nix-bwrapper、landlock）；Arch = 命令式 + 社区关注点是**AUR 供应链审计**（200+ 恶意包收养事件）。第二共识是**渐进披露**：用一个参数化工具 + 按需加载的 skill，而不是把能力全塞进上下文。

**Arch 侧最小可行栈**：`arch-mcp`（PyPI 包名 `arch-ops-server`，59★ 活跃）+ `arch-wiki-mcp`（1★，但"引用可校验"设计最该学）+ `herraiz-org/ai-skills`（Apache-2.0，带 CI）+ **官方仓库的 `arch-wiki-lite` / `informant` / `arch-audit`**。Arch 的知识库**不需要 MCP**：`arch-wiki-lite` 一个包给出离线全文 Wiki，体积仅 HTML 版 1/9。

**Fedora / Debian / Ubuntu 三家共享 systemd，所以最该先装的运维 MCP 不是发行版专属的，而是 `openSUSE/systemd-mcp`** —— 厂商官方组织维护、MIT、**polkit / OAuth2 双授权**、**默认 `--allow-write=false`**、有独立 `gatekeeper` 提权守护进程。发行版差异只在两处：包管理器（`dnf` / `apt`）与强制访问控制（Fedora = **SELinux**；Debian/Ubuntu = **AppArmor**）。Fedora 侧最值得看 `simonives/redwrench`（Rust，策略引擎先于执行，四档 tier，连被拒调用都审计）与 `amineutron/fedora-agents`（**暴露工具无权限表条目就拒绝启动**）；Debian 侧看 `debvulns`（原 `debsecan-mcp`，MCP + CLI + Prometheus 三接口，带 EPSS）；Ubuntu 侧 ClawHub 技能最丰富但 star 最高的 MCP 已停更 16 个月。

**⭐ v5 补上最重要一块：Red Hat 官方 `rhel-lightspeed/linux-mcp-server`（317★，Apache-2.0）** —— 固定只读工具集（命令硬编码成元组，无 shell 拼接）+ SSH 多机 + 日志白名单（**不设 `LINUX_MCP_ALLOWED_LOG_PATHS` 就一个文件都读不到**）+ YAML 鉴权策略引擎（`auth_policy.py`，语义层 fail-closed）+ 可选的 LLM Gatekeeper 三层护栏。**它就是官方 "MCP Server for RHEL" 的内核。** 与 `systemd-mcp` 是互补而非替代：前者管**远程舰队只读诊断**，后者管**单机 systemd 深度操作**。⚠️ 它的 HTTP transport **当前无鉴权**，只用 stdio。⚠️ 厂商官方 ≠ 长期维护：`rhel-lightspeed` 组织 20 仓库里 4 个已归档。

版本基准：`NousResearch/hermes-agent` @ `4e7403130e`（commit **2026-09-29**，**已含 CVE-2026-84289 修复**）。Arch 侧数据核验日 **2026-10-12**；Fedora/Debian/Ubuntu 侧数据核验日 **2026-10-12**；RHEL 系 / openSUSE 侧数据核验日 **2026-10-12**。

---

## 1. Hermes 的五个 .md 各管什么（权威分工）

来源：`website/docs/user-guide/which-file-does-what.md`

| 文件 | 装什么 | 谁写 | 何时进上下文 | 位置 |
|---|---|---|---|---|
| `SOUL.md` | 人格、语气、禁止事项 | 你 | 系统提示 **slot #1**，会话开始 | `$HERMES_HOME/SOUL.md` |
| `USER.md` | 用户画像 | **Agent**（`memory` 工具） | 系统提示，会话开始的**冻结快照** | `$HERMES_HOME/memories/` |
| `MEMORY.md` | Agent 自己的笔记 | **Agent** | 同上 | `$HERMES_HOME/memories/` |
| `AGENTS.md` | 项目指令、约定、命令、路径 | 你 | 启动时从工作目录载入，进子目录渐进发现 | 项目工作目录 |
| `.hermes.md` / `HERMES.md` | 同 AGENTS.md，Hermes 专属、优先级最高 | 你 | 同上 | 项目（向上找到 git root） |

**关键机制**
- ⚠️ **配置根目录是 `$HERMES_HOME`，不是 `~/.hermes`。** 本机实测 `HERMES_HOME=C:\Users\Admin\AppData\Local\hermes`，`config.yaml` 在 `$HERMES_HOME/config.yaml`（123,576 字节，`_config_version: 49`），**不在 git 仓库里**；`~/.hermes/` 不存在。
- 一个会话只载入**一个**项目上下文文件，优先级 `.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`，首个命中即止。`SOUL.md` 独立加载，不在此链。
- 记忆是**冻结快照**：会话中途存的东西磁盘立刻写入，但系统提示要下一会话才更新。改 `SOUL.md`/`AGENTS.md` 同样需重启会话。
- **profile 不是沙箱**。`hermes profile create <name>` 只给独立 `HERMES_HOME`（自己的 config/.env/SOUL/memories/skills/cron/state.db），`local` 终端后端下文件系统权限与用户账号相同。

**运维场景的正确分工**：跨项目安全底线 → `SOUL.md`；具体机器/仓库的操作规则 → `AGENTS.md`。

---

## 2. 可复用操作

### 2.1 Hermes 侧配置片段

```yaml
# ~/.hermes/config.yaml —— 危险命令永久白名单（"always" 批准会写到这里）
command_allowlist:
  - "systemctl status *"      # 精确文本或 shell glob
  - "journalctl -u *"
# ⚠️ 绝不要放 rm / dd / mkfs / nix-collect-garbage 之类宽泛模式

# MCP：只读查询 + 远程执行，均收窄工具面
mcp_servers:
  nixos:
    command: "uvx"
    args: ["mcp-nixos"]
    lazy: true                            # 启动只注册 schema，首次调用才起进程
    tools:
      include: ["nix", "nix_versions"]    # 白名单，支持 fnmatch 通配
  ssh:
    command: "npx"
    args: ["-y", "ssh-mcp-server",
           "--whitelist", "^(systemctl|journalctl|df|free|uptime|pacman -Q|nixos-rebuild dry-build).*"]
    env:
      SSH_KEY_PATH: "${env:SSH_KEY_PATH}" # 从 ~/.hermes/.env 解析
    trust: untrusted                      # 每个非只读调用都要人工审批
    tools:
      include: ["execute-command", "list-servers"]
```

`trust: untrusted` 语义：**每一个非只读工具调用都走审批界面**。`readOnlyHint` 由 server 自述，撒谎最多骗过审批、拿不到额外权限；无法识别的值按 `untrusted` 处理（fail-closed）。

### 2.2 NixOS 声明式部署（Hermes 官方模块）

```nix
# configuration.nix
{ config, ... }: {
  services.hermes-agent = {
    enable = true;
    settings.model.default = "anthropic/claude-sonnet-4";
    environmentFiles = [ config.sops.secrets."hermes-env".path ];  # 密钥必须走这里
    addToSystemPackages = true;   # 同时把 HERMES_HOME 设为系统级，CLI 与 gateway 共享状态
  };
  services.hermes-agent.mcpServers.nixos = {
    command = "uvx";
    args = [ "mcp-nixos" ];
  };
}
```

硬警告：`settings` / `environment` 的值会进 `/nix/store`（全局可读），**API key 只能走 `environmentFiles`**。`documents` 选项必须显式设 `workingDirectory`，否则文件落到默认目录；`SOUL.md` 与 `memories/` 用 `hermesHomeFiles` 而非 `documents`。

### 2.3 自定义运维 skill 的 frontmatter
```yaml
---
name: nixos-ops
description: 安全地对 NixOS 主机做配置变更、重建与回滚
version: 1.0.0
author: <你>
license: MIT
platforms: [linux]                 # 可选 macos/linux/windows；省略=全平台
metadata:
  hermes:
    tags: [NixOS, DevOps, Rollback]
    category: devops
    requires_toolsets: [terminal]  # 条件激活
    config:
      - key: nixos.flake_path
        description: "flake 所在路径"
        default: "/etc/nixos"
---
```

安装：`hermes skills install official/<category>/<skill>` 或 `hermes skills install <owner>/<repo>/<skill>`（第三方会先跑安全扫描）。

### 2.4 沙箱化 agent 跑代码（Nix 方案，Linux only）

```jsonc
// MCP client 配置：给 LLM 一个沙箱化的代码执行环境
{
  "mcpServers": {
    "nix-sandbox": {
      "command": "nix",
      "args": ["run", "github:secbear/nix-sandbox-mcp", "--", "--stdio"],
      "env": {
        "PROJECT_DIR": "/home/user/myproject",   // 只读挂载到沙箱内 /project
        "NIX_SANDBOX_ENVS": "github:myorg/envs#data-science,github:myorg/envs#nix-tools"
      }
    }
  }
}
```

自定义环境用 flake 定义（`nix-sandbox-mcp.lib.mkSandbox`，`interpreter_type` 取 `python` / `bash` / `node`）。安全边界：bubblewrap + 独立 user/PID/network/mount namespace，**默认无网络**，项目只读。**不防内核漏洞**（共享宿主内核）——要防不可信代码需等 microvm.nix 后端（独立内核 + KVM）。

### 2.5 MCP 工具元数据漂移监控（Deadbugz 的直接克星）

```python
import hashlib, json

class McpToolFingerprint:
    def __init__(self, trusted_snapshot: dict):
        self.trusted = trusted_snapshot          # 首次人工审查批准时的快照

    def snapshot(self, tools) -> dict:
        sig = {}
        for t in tools:
            canon = json.dumps(
                {"name": t.name, "description": t.description, "schema": t.inputSchema},
                sort_keys=True, ensure_ascii=False)
            sig[t.name] = hashlib.sha256(canon.encode()).hexdigest()[:16]
        return sig

    def verify(self, tools) -> list[str]:
        drift, cur = [], self.snapshot(tools)
        for name, digest in cur.items():
            if name not in self.trusted:
                drift.append(f"新增工具: {name}")
            elif self.trusted[name] != digest:
                drift.append(f"元数据漂移: {name} {self.trusted[name]} -> {digest}")
        for name in self.trusted:
            if name not in cur:
                drift.append(f"工具消失: {name}")
        return drift
# 每次 session 建立/重连后调用；有 drift 就阻断并通知人工，而不是继续信任
```

### 2.6 Arch 侧配置片段（第三轮新增）

```yaml
# ~/.hermes/config.yaml —— Arch MCP 双 server，写操作全部收窄
mcp_servers:
  # 只读引用引擎：建议默认开
  arch-wiki:
    command: "arch-wiki-mcp"          # pipx install arch-wiki-mcp
    lazy: true
    trust: untrusted
    tools:
      include: ["page", "section", "commands", "warnings", "search"]

  # Arch 运维总入口：含写操作，必须收窄
  arch-ops:
    command: "uvx"
    args: ["arch-ops-server"]         # 注意：仓库叫 arch-mcp，包叫 arch-ops-server
    lazy: true
    trust: untrusted                  # ⚠️ 有写操作，绝不放行
    tools:
      include:
        - "search_archwiki"
        - "search_aur"
        - "get_official_package_info"
        - "check_updates_dry_run"
        - "check_database_freshness"
        - "fetch_news"
        - "audit_package_security"
        - "analyze_pkgbuild_safety"
        - "analyze_package_metadata_risk"
        - "diagnose_system"
        - "query_package_history"
        - "verify_package_integrity"
      exclude:                        # 列出来是为了显式说明"为什么没有它们"
        - "install_package_secure"
        - "remove_packages"
        - "manage_orphans"
        - "manage_install_reason"
        - "optimize_mirrors"

# 危险命令永久白名单：只放只读查询
command_allowlist:
  - "checkupdates"
  - "pacman -Q*"
  - "yay -Qu*"
  - "systemctl --failed"
  - "journalctl -u *"
  - "arch-audit"
  - "df -h"
  # ⚠️ 绝不加入：rm / dd / mkfs / pacman -Syu / pacman -R / yay -S
```

```bash
# Arch 知识库落地：离线 Wiki 作为只读原始层
sudo pacman -S arch-wiki-lite arch-wiki-docs informant arch-audit pacman-contrib
export WIKI_PATH=~/ops-arch/kb
mkdir -p "$WIKI_PATH"/{raw,entities,concepts,comparisons,queries}
ln -sfn /usr/share/doc/arch-wiki-lite "$WIKI_PATH/raw/arch-wiki-offline"
informant check                      # 更新前强制读 Arch News

# 装 Arch 专属 skill（herraiz-org 质量最高 + enihcam 打包向）
git clone https://github.com/herraiz-org/ai-skills.git ~/.local/share/ai-skills
git clone https://github.com/enihcam/aur-skills.git    ~/.local/share/aur-skills
for s in ~/.local/share/ai-skills/skills/* ~/.local/share/aur-skills/skills/*; do
  ln -sfn "$s" ~/.hermes/skills/"$(basename "$s")"
done
# ⚠️ 不要把克隆放 /tmp（很多系统挂 tmpfs，重启即清）

# AUR 自查：所有外来包的风险等级
check_pkg() {
  local pkg=$1 status
  status=$(curl -fsS "https://aurwatch.org/api/v1/check?pkg=$pkg" | jq -r '.status' 2>/dev/null)
  printf '%-32s %s\n' "$pkg" "${status:-unknown}"
}
export -f check_pkg
pacman -Qqm | xargs -P16 -I{} bash -c 'check_pkg "$@"' _ {}
```

### 2.7 Fedora / Debian / Ubuntu 配置片段（第四轮新增）

```yaml
# ~/.hermes/config.yaml —— 通用基座：systemd-mcp（默认禁写）
mcp_servers:
  systemd:
    command: "/usr/bin/systemd-mcp"
    args: []                          # ⚠️ 不加 -w → 默认只读（--allow-write 默认 false）
    lazy: true
    trust: untrusted
    tools:
      include: ["list_units", "list_log", "get_man_page", "get_file"]
      exclude: ["change_unit_state"]  # 要改 unit 时再单独放开（会触发 polkit）
```

```bash
# ── 通用：systemd-mcp（厂商官方维护，覆盖三家）──
git clone https://github.com/openSUSE/systemd-mcp && cd systemd-mcp
make build && sudo make install

# ── Fedora ──
sudo dnf install ./redwrench-*.rpm                 # Rust 策略引擎 MCP（tier 从 standard 起步）
sudo dnf install dnf-automatic dnf5-plugins
sudo systemctl enable --now dnf-automatic.timer
dnf needs-restarting -r                            # 重启检测（不是 needrestart）
# 不可变系统：rpm-ostree install <pkg>，不要用 dnf install

# ── Debian ──
pip install debvulns                               # 漏洞分析（MCP + CLI + Prometheus，带 EPSS）
debvulns --severity high
sudo apt install unattended-upgrades needrestart debsecan apt-listchanges apt-listbugs
sudo dpkg-reconfigure -plow unattended-upgrades
sudo needrestart -r l                              # ⚠️ 列出仍跑旧库的服务

# ── Ubuntu ──
pro status && pro security-status                  # Pro / ESM / Livepatch
sudo pro enable livepatch
sudo apt install unattended-upgrades needrestart
snap refresh --list                                # ⚠️ snap 是独立通道，必须单独覆盖
```

```bash
# ── 发行版专家技能（awesome-copilot，v5 修正：实际有 4 类资源路径）──
# ① skills/<d>-linux-triage/SKILL.md  ② agents/<d>-linux-expert.agent.md
# ③ instructions/<d>-linux.instructions.md  ④ plugins/（⚠️ arch 那个是软件架构插件）
for s in arch-linux-triage fedora-linux-triage debian-linux-triage centos-linux-triage; do
  mkdir -p ~/.hermes/skills/$s
  curl -sL "https://raw.githubusercontent.com/github/awesome-copilot/main/skills/$s/SKILL.md" \
    -o ~/.hermes/skills/$s/SKILL.md
done
# 常驻规则（项目级）
for d in arch fedora debian centos; do
  curl -sL "https://raw.githubusercontent.com/github/awesome-copilot/main/instructions/$d-linux.instructions.md" \
    -o ./instructions/$d-linux.instructions.md
done
# ⚠️ 覆盖矩阵：arch / fedora / debian / centos = 三类俱全；ubuntu / rhel / opensuse = 全 404
# ⚠️ Ubuntu 无对应技能 → 用 debian-linux-triage；RHEL 系只有 CentOS 有 → 用 centos-linux-triage
```

### 2.8 通用执行层：Red Hat 官方只读 Linux MCP（v5 新增）

```yaml
# ~/.hermes/config.yaml —— 执行层：厂商官方方案（推荐首选）
mcp_servers:
  linux-tools:                        # Red Hat 官方，只读工具集 + SSH 多机
    command: "/home/<user>/.local/bin/linux-mcp-server"   # uv tool install linux-mcp-server
    env:
      # ⚠️ 不设这个变量，read_log_file 读不到任何文件（fail-closed）
      LINUX_MCP_ALLOWED_LOG_PATHS: "/var/log/messages,/var/log/secure,/var/log/audit/audit.log"
      LINUX_MCP_VERIFY_HOST_KEYS: "True"
      # ❌ 不要设 LINUX_MCP_TOOLSET=run_script  —— 会打开写能力（虽有三层护栏）
      # ❌ 不要设 LINUX_MCP_TRANSPORT=http      —— 官方明说 HTTP 无鉴权，不得用于生产
    lazy: true
    trust: untrusted
    timeout: 60

  systemd:                            # openSUSE 官方，需要 systemd 深度控制时再叠
    command: "/usr/bin/systemd-mcp"
    args: []                          # 不加 -w → 默认只读
    lazy: true
    trust: untrusted
    tools:
      include: ["list_units", "list_log", "get_man_page", "get_file"]
      exclude: ["change_unit_state"]
```

---

## 3. 第三方 MCP 选型表

| MCP | 仓库 | 提供什么 | 工具数/成本 | 许可 | 风险 |
|---|---|---|---|---|---|
| **linux-mcp-server** ⭐⭐ | `rhel-lightspeed/linux-mcp-server`（**Red Hat 官方**） | 只读诊断：services / processes / logs / network / storage / system_info / **PCP 性能**；**SSH 多机**（一次会话切多台主机） | **317★ / 67 forks**，PyPI `linux-mcp-server` 1.7.0，Python ≥3.10，2026-10-10 活跃 | **Apache-2.0** | 默认工具集**结构性只读**（命令硬编码成元组，无 shell 拼接）；日志白名单**不设即读不到**；`auth_policy.py` YAML 策略语义层 fail-closed；SSH 仅密钥 + 默认验主机键。⚠️ **HTTP transport 无鉴权**；`run_script`（LLM Gatekeeper）默认不开且官方评分未填 |
| **okp-mcp** | `rhel-lightspeed/okp-mcp`（Red Hat 官方） | Red Hat Offline Knowledge Portal MCP —— RHEL 版的"离线知识层" | 19★，Apache-2.0 | Apache-2.0 | 只读知识查询。作用对标 Arch 的 `arch-wiki-lite` |
| **mcp-nixos** | `utensils/mcp-nixos` | NixOS 13 万+ 包、2.3 万+ 选项、Home Manager、nix-darwin、Nixvim、NVF、FlakeHub、Noogle、NixOS Wiki、nix.dev、版本历史、binary cache | **2 工具，约 1030 token**（作者以省上下文为设计目标） | MIT | 只读，低 |
| **ssh-mcp-server** | `classfang/ssh-mcp-server` | `execute-command`、`upload`、`download`、`list-servers` | 4 工具 | 见仓库 | 可执行任意 shell；支持 `--whitelist`/`--blacklist` 正则；凭据留本地 |
| **nix-agent** | `JEFF7712/nix-agent` | 真跑 `build`/`diff`/`switch`/`generations` + `eval`/`locate`/`check` | 见仓库 | 见仓库 | ⚠️ 作者自述实验性；**默认高信任**：未经提示即 `switch` + 免密 sudo，低信任是"降级选项" |
| **openSUSE/systemd-mcp** ⭐ | `openSUSE/systemd-mcp` | systemd unit / journal / man page / 文件读取。**直接连 systemd C API，不需要 systemctl** | 6 工具，**10★**，MIT，Go，v0.3.5 | MIT | **默认 `--allow-write=false`** + polkit 授权 + 独立 `gatekeeper` 守护进程。**Fedora/Debian/Ubuntu 通吃**。价值在"厂商官方 + 默认禁写"，不在热度 |
| **redwrench** | `simonives/redwrench` | Fedora 系统管理，**策略引擎先于执行**，四档 tier（safe/standard/developer/unrestricted） | Rust，`.rpm` 发布 | MIT OR Apache-2.0 | **每次调用（含被拒）都写 systemd journal**。业余项目，未进官方仓库 |
| **fedora-agents** | `amineutron/fedora-agents` | KVM/libvirt VM + Borg/Timeshift 备份 | 19 工具（npm `fedora-agents-mcp`） | MIT | **暴露工具无权限表条目则拒绝启动**；逐脚本 sudoers；变更操作永不重试；无网络输出 |
| **debvulns**（原 debsecan-mcp） | `copyninja/debsecan-mcp` | Debian 漏洞分析：MCP + CLI + Prometheus 三接口，**含 EPSS 分数** | `pip install debvulns` | 见仓库 | 只读扫描。⚠️ 旧名 `debsecan-mcp` 停在 0.1.5 |
| `ubuntu_mcp_server` | `pazuzu1w/ubuntu_mcp_server` | Ubuntu 系统操作（"limited control"） | 44★ | 见仓库 | ⚠️ **2025-06-29 后停更约 16 个月**，用前自审源码 |
| **arch-mcp**（= PyPI `arch-ops-server`） | `nihalxkumar/arch-mcp` | Arch Wiki / AUR / 官方仓库 / pacman 状态 / 系统状态 / Arch News（URI Resources + 14 工具 + 4 Prompt） | 59★，v3.4.0，2026-03-10 仍在提交 | **双许可 GPL-3.0-only OR MIT** | ⚠️ **含写操作**：`install_package_secure`/`remove_packages`/`manage_orphans`/`optimize_mirrors` → 必须 `trust: untrusted` + `tools.include` 白名单 |
| **arch-wiki-mcp** | `egarcia74/arch-wiki-mcp` | Arch Wiki 确定性抽取，**每个片段带 SHA-256 + 钉到 revision 的 URL**；三档证据分层；fail-closed | 1★，v2.1.0，零依赖，`pipx` 装 | MIT | 纯只读，低 |
| homelab-mcp | `bshandley/homelab-mcp` | homelab 基础设施管理 | 见仓库 | 见仓库 | 社区项目，装前自审 |
| mcp-homelab-server | `Proto-labs-rnd/mcp-homelab-server` | homelab 工具集 | 见仓库 | 见仓库 | 社区项目，装前自审 |
| docker/mcp-gateway | `docker/mcp-gateway` | Docker 官方 MCP Gateway/Toolkit，按 profile 统一跑 MCP | — | 见仓库 | 官方维护 |
| grafana/mcp-grafana | `grafana/mcp-grafana` | Grafana 仪表盘/数据源/事件查询 | — | 见仓库 | 官方维护 |

`mcp-nixos` 的关键价值：**不需要装 Nix**（`uvx mcp-nixos` 即可），已进 nixpkgs（`pkgs.mcp-nixos`），直接解决"小模型编造 Nix 包名/选项名"的痛点。

**Hermes 官方 65 个 MCP 里与运维相邻的**：`globalping`（网络探测）、`betterstack`（uptime）、`semgrep`、`datadog`、`grafana`、`cloudflare`、`gitlab`、`aws-knowledge`。**没有 SSH / NixOS / Arch。**

---

## 4. 知识库选型：文件 → MCP → RAG

### 前提纠正

Hermes 内置持久记忆 = **2200 字符（memory）+ 1375 字符（user）**，满了直接报错要求先合并条目。官方原话：需要每次运行都用的事实，**skill 比 memory 条目更好**——只在相关时加载，不占那 2200 字符预算。**内置记忆不是知识库。**

### 方案对比

| 方案 | 类型 | 存储 | 本地 | Agent 可写 | 维护负担 | 适用 |
|---|---|---|---|---|---|---|
| **Hermes 原生 `llm-wiki`** | 技能 + 文件 | 纯 markdown | ✓ | ✓ | 极低（0 安装） | **首选** |
| **官方仓库离线 Wiki**（Arch） | `arch-wiki-lite` 包 | 纯文本，体积 1/9 | ✓ | ✗（只读层） | 极低（`pacman -S`） | **Arch 首选**，喂给 llm-wiki 的 `raw/` |
| Obsidian vault | 软件 + 技能 | 纯 markdown | ✓ | ✓ | 低 | 想可视化浏览 |
| `qmd` | 技能 + 本地索引 | 索引叠在 md 上 | ✓ | 间接 | 中 | 笔记上百篇后加语义检索 |
| `basic-memory` | MCP server | markdown + 知识图谱 | ✓ 本地优先 | ✓ | 中 | 想跨多个 AI 工具共享 |
| SiYuan（思源） | 软件 + 技能 | 自有格式 | ✓ | ✓ | 中 | 中文笔记体验优先 |
| OpenViking / Holographic | Hermes 记忆 provider | 文件层级 / HRR 代数 | ✓ | ✓ | 中 | 突破 2200 字符的"记忆" |
| Mem0 / Honcho / RetainDB / Supermemory | 记忆 provider | 云或自托管 | 部分 | ✓ | 中高 | 多 agent 共享记忆 |
| RAG（RAGFlow/Dify/向量库） | 平台 | 向量库 | 可自托管 | 间接 | **高** | 文档几千份且需模糊召回 |

### llm-wiki 的结构（Karpathy 模式）

```
wiki/                        # WIKI_PATH 环境变量指定，默认 ~/wiki
├── SCHEMA.md                # 约定、结构规则、领域配置
├── index.md                 # 分节目录 + 一行摘要
├── log.md                   # 追加式操作日志
├── raw/                     # 第 1 层：不可变原始素材（agent 只读）
├── entities/                # 第 2 层：实体页（机器、服务、主机）
├── concepts/                # 第 2 层：概念页
├── comparisons/             # 第 2 层：横向对比
└── queries/                 # 第 2 层：值得留存的查询结果
```

技能强制 agent **每次会话先读 `SCHEMA.md` → `index.md` → 最近 30 条 `log.md`** 完成定位，避免重复建页。核心论点：**RAG 每次查询从零重新发现知识；wiki 只编译一次并持续保持更新**——交叉引用已建好，矛盾已标记。

它就是 markdown 目录：可用 Obsidian/VS Code 打开、git 版本化、**换 agent 也不丢**。

---

## 5. NixOS 生态全清单（第二轮深挖）

### 5.1 知识层：让 agent 不编造 Nix 选项

| 项目 | 仓库 | 作用 | 上下文成本 |
|---|---|---|---|
| **mcp-nixos** | `utensils/mcp-nixos` | 13 万+ 包、2.3 万+ 选项、Home Manager、nix-darwin、Nixvim、NVF、FlakeHub、Noogle、NixOS Wiki、nix.dev、版本历史、binary cache、本地 flake inputs | **2 工具约 1030 token**，MIT，已进 nixpkgs |
| **nix-mcp** | `bastianasmussen/nix-mcp` | 直接访问 Nix store / evaluator / flake 系统 | 未核实 |
| **nixai** | `olafkfreund/nix-ai-help` | 控制台式 NixOS 助手，支持 VS Code MCP 与 Neovim | **项目已归档** |

### 5.2 执行层：真正改系统

| 项目 | 仓库 | 作用 | 风险 |
|---|---|---|---|
| **nix-agent** | `JEFF7712/nix-agent` | `build`/`diff`/`switch`/`generations` + `eval`/`locate`/`check`，与 mcp-nixos 配对（一个查一个改） | ⚠️ 实验性。**默认高信任**：无提示 `switch` + 免密 sudo，低信任是"降级选项" |
| **nh** | Nix helper | 配 `-q --no-noms` 给 agent 提供**干净输出**（社区点名的关键 harness 组件） | 低 |
| **devenv 1.7+** | devenv | 开发环境声明式管理，**内置 MCP 支持** | 低 |
| nixos-anywhere / deploy-rs / colmena | nix-community / serokell / zhaofengli | 远程安装、带自动回滚部署、机群部署 | 中（批量影响面大） |

### 5.3 沙箱层：NixOS 社区最活跃、最独特的一层 ⭐

**r/NixOS 上关于 AI agent 的高质量项目绝大多数是沙箱。**

| 项目 | 仓库 | 机制 | 特点 |
|---|---|---|---|
| **nix-sandbox-mcp** | `SecBear/nix-sandbox-mcp` | jail.nix（bubblewrap + namespaces，**不需 root**） | **单个 `run` 工具 + `env` 参数，固定约 420 token**，与配置环境数无关；默认**无网络**；项目只读挂载 `/project`；会话持久化；规划加 microvm.nix。MIT，仅 Linux |
| **jailed-agents** | `andersonjoseph/jailed-agents` | Nix + jail.nix | 零信任沙箱，把整个 agent 关进隔离环境 |
| **nix-bwrapper** | `xNaXDy/nix-bwrapper` v1.0.0 | NixOS 模块系统的模块化 bwrap | 用 module 系统管 bubblewrap 配置 |
| **landlock 方案** | u/rolfst | Nix + landlock（内核级） | 密钥藏在 landlocked 工具里，"由 Linux 内核保护" |
| agent-sandbox.nix / ai-jail / nixpi | 多个 | 轻量跨平台沙箱 / Nix 可复现性 | 见报告 §1.3 |

**MCP 上下文税对照（nix-sandbox-mcp README 原文数据）**：

| 方案 | 初始成本 | 代价 |
|---|---|---|
| 静态加载全部工具 | 约 150 token × N | 线性膨胀（60 工具 ≈ 47k token） |
| 动态发现 | 约 400 token 固定 | 每次多往返，要学发现协议 |
| SKILL.md 指南 | 激活时约 800 token | 丰富但重，需另维护 |
| **一个参数化工具** | **约 420 token 固定** | 不随环境数增长 |

做法：工具选择与工作流提示**内联在 MCP 协议字段**（tool description / server instructions / 参数 JSON Schema description），不另开文档。

### 5.4 结构层：用 Nix 组织 agent 的 skill 与指令

| 项目 | 仓库 | 作用 |
|---|---|---|
| **nixos-management-skill** | `michalzubkowicz/nixos-management-skill` | **纯 Markdown skill**，从官方文档自动生成。9 文件：`SKILL.md`（入口+决策表+执行上下文检查）、`configuration.md`、`vm-management.md`（rebuild/generations/rollback/deploy-rs/colmena）、`installation.md`（disko）、`image-building.md`、`impermanence.md`、`luks.md`（initrd 内 SSH/Tailscale 远程解锁）、`monitoring.md`（systemd timer + Telegram/webhook 健康检查）、`anti-patterns.md`。带 `AGENTS.md` 跨 agent 入口 |
| **rigup.nix** | `YPares/rigup.nix` | 可参数化 skills/指令/工具，Nix 模块化打包。核心概念 **riglet**；自带自文档化 riglet：`agent-rig-system`、`riglet-creator`、`nix-module-system` |
| **knoopx/pi skills** | `knoopx/pi` | 社区分享的 `nix-flakes`、`nh`、`nix` 三个 SKILL.md |
| **nix-playwright-nightly** | `halfwhey/...` | playwright 及 **playwright/mcp** 打包成纯 Nix derivation |
| **Nix 作为 MCP 打包层** | r/NixOS 提议 | `flake.mcpConfigurations`（服务器分组）+ `flake.mcpModules`（单个服务器）——"比在 npx/uvx 上盖东西好太多，可原子更新、可回滚" |

---

## 6. Arch 生态全清单（第三轮深挖）

### 6.1 两个 Arch 专属 MCP（均已核验）

| | `arch-mcp` / **`arch-ops-server`** | `arch-wiki-mcp` |
|---|---|---|
| 仓库 | `nihalxkumar/arch-mcp` | `egarcia74/arch-wiki-mcp` |
| **安装名** | **`uvx arch-ops-server`**（仓库名 ≠ 包名） | `pipx install arch-wiki-mcp` |
| 版本 / Stars | 3.4.0 / **59★** | 2.1.0 / **1★** |
| 许可 | 双许可 GPL-3.0-only OR MIT | MIT |
| 创建 / 最后提交 | 2025-10-23 / 2026-03-10（活跃） | 2026-01-10 / 2026-07-15 |
| 依赖 | Python ≥ 3.11 | **零依赖** |
| 定位 | Arch 运维总入口 | **引用引擎 / truth perimeter** |
| 写操作 | **有 ⚠️** | 无（纯只读） |

**`arch-mcp` 的 Resources（URI 式只读，不占 tool 名额）**：`archwiki://`、`archrepo://`、`aur://*/info`、`aur://*/pkgbuild`（带安全分析的 PKGBUILD 原文）、`pacman://installed|orphans|explicit|groups|group/*|database/freshness|log/recent|log/failed`、`system://info|disk|services/failed|logs/boot`、`archnews://latest|critical|since-update`、`config://pacman|makepkg`、`mirrors://active|health`

**`arch-mcp` 的 14 个 Tools**：只读查询 `search_archwiki` / `search_aur` / `get_official_package_info` / `check_updates_dry_run` / `check_database_freshness` / `fetch_news` / `audit_package_security` / `analyze_pkgbuild_safety`（**50+ 红旗**）/ `analyze_package_metadata_risk` / `diagnose_system` / `query_package_history` / `verify_package_integrity` / `analyze_pacman_conf` / `analyze_makepkg_conf`；
**写操作 ⚠️** `install_package_secure` / `remove_packages` / `manage_orphans` / `manage_install_reason` / `optimize_mirrors`。
另有 4 个 Prompt：`troubleshoot_issue` / `audit_aur_package` / `analyze_dependencies` / `safe_system_update`。

**`arch-wiki-mcp` 的三档证据分层（最该抄的通用模式）**：

| 档位 | 工具 | revid | SHA-256 hash | 语义 |
|---|---|---|---|---|
| 证据 | `page` `section` `commands` `warnings` | ✅ | ✅ | 可引用、可复算 |
| 半证据 | `links` | ✅ | ❌ | 是目标，不是引文 |
| 指针 | `search` `sections` | ❌ | ❌ | **拒绝伪装成证据** |

原话："This is not 'AI that knows Linux.' This is Linux that won't let AI lie about it." / "**There is deliberately no tool that infers commands from prose.**"
细节设计：`commands` 返回的 `content` 里 `<esp>` **故意保留尖括号**——"so a thoughtless paste fails at the shell instead of acting on the wrong path"。

**文档瑕疵（已核实）**：`herraiz-org/ai-skills` 的 `references/arch-mcp.md` 把 server 链接写成 `github.com/iht/arch-mcp`；那是 2026-08-08 的 **fork**（0★，当日停更）。上游是 `nihalxkumar/arch-mcp`。工具名与上游**逐字一致**（已在 `src/arch_ops_server/tool_metadata.py` 确认），所以技能可用，只需改链接。

### 6.2 三个真实 Arch 专属 Agent Skill 仓库

| 仓库 | Stars / 许可 | 最后提交 | 定位 |
|---|---|---|---|
| **`herraiz-org/ai-skills`** ⭐ | 0 / **Apache-2.0** | 2026-09-05 | **质量最高**：`update-arch-system` + `install-aur-package`，**带 CI + pytest** |
| `enihcam/aur-skills` | 5 / MIT | 2026-10-09 | AUR 打包开发，10 个模块化技能，**有中文 README** |
| `IPauloGermano/arch-agent-skill` | 0 / MIT | 2026-09-07 | 桌面环境向（Hyprland/Sway/KDE/GNOME/Niri/Waybar/主题） |

**`herraiz-org/ai-skills` 的六道闸门（整轮最有价值的流程资产）**：
1. **Preconditions** — `test -r /etc/arch-release`；硬规则：**永不 `pacman -Sy`、永不部分升级、永不关签名校验、永不改 pacman 信任设置**
2. **checkupdates 引导** — 从 `pacman-contrib` 装，**绝不允许从 AUR 满足此依赖**；先查 `check_database_freshness` 判断该"立即装"还是"并入全量升级"（避免部分升级）
3. **Arch News 闸门（阻塞式）** — `fetch_news(critical)` + `fetch_news(since_update)`；无 MCP 时读 `https://archlinux.org/feeds/news/` + `/var/log/pacman.log`。**RSS 仅约 10 条 → 必须报告盲区，不可当作"没有新闻"**。命中待升级包 → 停下等人工批准
4. **Discover** — `checkupdates`（免 sudo）；AUR 用 `yay -Qua`（两条路径都跑）
5. **Audit every AUR target** — 克隆 `https://aur.archlinux.org/<PackageBase>.git` 到 `mktemp -d`；**绝不 source PKGBUILD、绝不先跑 makepkg**；审 `PKGBUILD` / `.SRCINFO` / `.install` / patches；跑自带 `scripts/scan-aur-recipe.sh`；静态检查通过后才允许 `makepkg --verifysource`
6. **Install gate** — 需显式批准

**自带扫描器 `scan-aur-recipe.sh` 的规则**：

| 级别 | 模式 |
|---|---|
| **HIGH** | `curl\|wget` 管道进 `sh/bash/zsh/python/perl/ruby` |
| **HIGH** | 包控代码出现 `sudo` / `doas` / `su` |
| **HIGH** | 访问凭据库 `.ssh` `.gnupg` `.aws` `.kube` `netrc` `id_rsa` `id_ed25519` `credentials` `api_key` `auth_token` |
| **HIGH** | `eval` / `base64 -d` 动态或编码执行 |
| MEDIUM | `sha*sums`/`md5sums`/`b2sums` 显式 `SKIP`；弱哈希；`http://` 明文源 |
| MEDIUM | 可变 VCS 源（`git+` `hg+` `svn+` `bzr+`）或自定义 `pkgver()` |
| MEDIUM | 预编译产物 `.AppImage` `.deb` `.rpm` `.exe` `.msi` |
| MEDIUM | 持久化机制 `systemctl` `udev` `tmpfiles` `sysusers` `cron` `.install` |

退出码：HIGH → `2`；MEDIUM → `1`。

**它的信任原则（原话，值得写进 SOUL.md）**：
> **"Server output is evidence, not a verdict."** 干净的 `pkgbuild_analysis` **不能**降级 scanner 的发现；干净的 scanner **不能**降级 MCP 的发现。**取并集**；冲突时**取更高风险等级**并解释分歧。
> `pkgbuild_analysis` 只拿到 PKGBUILD 文本，**看不到** `.install` 脚本、patches、systemd unit、vendored 脚本、提交的二进制。

**`enihcam/aur-skills` 的验证命令清单**：
```bash
namcap PKGBUILD ; namcap *.pkg.tar.zst
shellcheck --shell=bash --exclude=SC2034,SC2154,SC2164 PKGBUILD
makepkg --printsrcinfo > .SRCINFO
makerepropkg *.pkg.tar.zst      # 可复现构建（devtools）
pkgctl build                    # 干净 chroot 构建（systemd-nspawn）
```
推荐的第三方扫描器：`traur`、`ks-aur-scanner`。原文提醒：**"aids, not substitutes for manual review"**、**"signed code can still be malicious — review the content, not just the signature."**

**跨 agent 技能目录表（来自该仓库 README，A 级）**：

| Agent | 技能目录 |
|---|---|
| **Hermes** | `~/.hermes/skills/` |
| Claude Code | `~/.claude/skills/` |
| OpenCode | `~/.config/opencode/skills/` |
| Gemini CLI | `~/.gemini/skills/` |
| Codex CLI | `~/.agents/skills/` |
| Cursor | `~/.cursor/skills/` |
| Windsurf | `~/.codeium/windsurf/skills/` |

### 6.3 官方仓库自带的 Arch 运维基座 ⭐（本轮最有价值的发现）

**Arch 的知识库与更新安全闸门不需要第三方——官方 `extra` 仓库直接提供。** 全部经 `archlinux.org/packages/search/json/` 核验（2026-10-12）：

| 包 | 仓库 | 版本 | 作用 |
|---|---|---|---|
| **`arch-wiki-lite`** | `extra/any` | `20261003-1` | **Arch Wiki 去 HTML 版，体积 1/9，console 可搜可读** |
| `arch-wiki-docs` | `extra/any` | `20261003-1` | Arch Wiki 离线浏览优化版 |
| **`informant`** | `extra/any` | `0.6.0-2` | **Arch News 阅读器 + pacman hook**（更新前强制读新闻） |
| `arch-audit` | `extra/x86_64` | `0.2.0-5` | 基于 Arch Security Team 数据的 CVE 审计 |
| `pacman-contrib` | `extra/x86_64` | `1.13.1-1` | 提供 `checkupdates`（免 sudo 查更新） |
| `downgrade` | **AUR** | 910 票 / pop 7.95 | 从缓存或 Arch Linux Archive 降级 |
| `paru` | **AUR** | 1260 票 / pop 19.83 | 功能最全的 AUR helper |

**结论：Arch 的知识库不需要 MCP，也不需要 RAG。**

```bash
pacman -S arch-wiki-lite arch-wiki-docs informant arch-audit pacman-contrib
# arch-wiki-lite → 本地全文可 grep 的 Wiki（离线、确定、无网络依赖、不会被投毒）
# informant      → 更新前自动拦下让你读新闻（用机制替代提示词）
# arch-audit     → CVE 扫描，可做定期巡检
```

### 6.4 非 AI 的软件方案（同样解决 Arch 更新安全）

| 工具 | Stars / 许可 | 能力 |
|---|---|---|
| **`indyfive11/archward`** | 1 / GPL-3.0 | **快照 · 风险分级 · pacman+AUR · pacnew 策略 · 逐包取消选择 · 粒度+批量回滚 · 自定义 hook · 更新后校验**。CLI + PySide6 GUI。靠 `ID_LIKE` 支持 Arch/EndeavourOS/Manjaro/CachyOS/Garuda/Artix |
| `codexspidey/archsafe` | 3 / 无 | AI 安全分析 CLI。⚠️ **2026-06-24 后无提交、无许可证 → 弃坑，勿依赖** |

`archward` 的功能集正好是 NixOS 用声明式天生解决、Arch 必须靠工具补上的那块。

### 6.5 社区实证：Arch 用户实际怎么用 AI（r/archlinux `1orwi2b`）

原帖"Arch for Beginners with Claude CLI-Code = Very Useful"，作者 `u/MysticFoxPaws` 的做法：
> "I still have **strict rules for Claude Code that it should retrieve references specifically via wiki.archlinux.org**, but also document carefully and clearly in **Obsidian**."

即**硬性要求 agent 从 wiki.archlinux.org 取引用 + 用 Obsidian 沉淀**——正是 `arch-wiki-mcp` 想结构化的那件事。

社区共识（按被认可程度）：
- **u/_sLLiK**："if you want to remove the chance of hallucinations, **start with Arch's wiki first. It really is that good.**"
- **u/Sea-Promotion8205**："They can throw a lot of red herrings … and **their information isn't always actually up to date**."
- **u/aldyr**："many Linux subreddits are full of pleading for help with their Linux install, **that isn't working after they followed some AI generated instructions**."
- **u/ExplanationMobile399**："**share terminal outputs and screenshots** with it … The more data it has with a current subject, the better it really does get."
- **u/archover**："for Arch config, I am very careful, **usually confirming it in the wiki for non trivial stuff**."

### 6.6 技能市场对 Arch 的覆盖：几乎为零（A 级）

| 市场 | 查询 | 结果 |
|---|---|---|
| clawhub.ai | `q=arch` | **全是 architecture（软件架构）技能**。唯一 Arch Linux 项是 `j3ffyang/arch-sign-off`（往文件尾追加 `btw, i use arch`，591 安装）——**玩笑技能** |
| clawhub.ai | `q=pacman` | 仅 1 个无关结果：`chris0x88/pacman-hedera`（DeFi agent） |
| AUR | `search/mcp` | 282 结果但**热度极低**（榜首 `engram-bin` pop 仅 1.76）。含 `github-mcp-server`/`-bin`（MIT）、`python-fastmcp`、`serena`、`codebase-memory-mcp-bin` |

**Arch 的 AI 运维能力不在技能市场，在 GitHub 小仓库 + 官方仓库包里。** 市场搜索只会给你架构噪音。

---

## 7. Fedora / Debian / Ubuntu / RHEL 系 / openSUSE 生态全清单（第四轮 + v5 补充）

### 7.1 ⭐ 通用基座：`openSUSE/systemd-mcp`（本轮的答案）

**四轮调研里唯一由发行版厂商官方组织维护、且安全模型完整到可以照抄的 Linux 运维 MCP。**

| 项 | 值 |
|---|---|
| 仓库 / 维护方 | `github.com/openSUSE/systemd-mcp` / **openSUSE 官方组织** |
| 许可 / 语言 / 版本 | **MIT** / Go / **0.3.5**（2026-09-24） |
| 关键实现 | **直接连 systemd 的 C API，不需要 `systemctl`** |
| 安装 | `make build && sudo make install`（装 `/usr/bin/systemd-mcp` + `/usr/sbin/gatekeeper` + 两个 unit + polkit policy） |
| 跨发行版 | Fedora / Debian / Ubuntu 全部默认 systemd → **直接可用** |

**6 个工具**：`list_units`、`change_unit_state`、`check_restart_reload`、`list_log`、`get_file`、`get_man_page`

**安全模型（最值得抄的部分）**：

| 传输 | 授权 |
|---|---|
| **stdio（默认）** | **polkit**（unit 操作触发 `org.freedesktop.systemd1.manage-units`）。**读操作永远放行**（调用者本人跑 server）；**只有写操作**触发 polkit |
| **HTTP** | **OAuth2**，audience `systemd-mcp-server`，scope `mcp:read` / `mcp:write` |

**日志访问三级降级**：root 或 journal 同组 → 直读全部；否则连 `gatekeeper`（`/run/gatekeeper/gatekeeper.socket`，触发 polkit `com.suse.gatekeeper.readlog`）；再不可用 → 只读当前用户能读的 journal，**并在输出里明确提示访问被缩减**。

**默认安全的 flag**：`--allow-write`/`-w` **默认 false**（要写必须显式开）；`--enabled-tools` 工具白名单；**`--noauth` 必须把值写成字面量 `ThisIsInsecure`**（故意制造摩擦）；`--timeout`（polkit 认证超时，默认 5s）；`--toon`（token 优化输出）。

### 7.2 三发行版对比（差异只在两处：包管理器 + 强制访问控制）

| | **Fedora** | **Debian** | **Ubuntu** |
|---|---|---|---|
| 最值得装的 MCP | **`simonives/redwrench`**（Rust 策略引擎）+ `amineutron/fedora-agents` | **`debvulns`**（原 `debsecan-mcp`） | `pazuzu1w/ubuntu_mcp_server`（44★，**2025-06 停更**） |
| 官方自动更新 | `dnf-automatic` | `unattended-upgrades` | `unattended-upgrades` + **Pro/ESM + Livepatch** |
| 重启检测 | **`dnf needs-restarting`**（在 `dnf5-plugins`） | `needrestart` | `needrestart` |
| 漏洞扫描 | `dnf updateinfo` / Bodhi | **`debsecan`** + `debvulns` | `pro security-status` / `debsecan` |
| 强制访问控制 | **SELinux** + `firewalld` | AppArmor | AppArmor（+ snap confinement） |
| ClawHub 生态 | 单件最热（`fedora-linux-triage` 观测 **8.9k**） | **最薄** | **最丰富**（10+ 件，最多 1.3k） |
| awesome-copilot 专家 | ✅ `fedora-linux-triage` | ✅ `debian-linux-triage` | ❌ **没有** |
| 独有坑 | **不可变系统** `dnf install` 直接失败；**AI 工具多只发 `.deb`** | 内核升级**不自动重启** | **Pro/ESM 是订阅**；**apt + snap 双通道** |

### 7.3 Fedora 专属

**`simonives/redwrench`**（Rust，MIT OR Apache-2.0，`.rpm` 发布，作者明示业余项目、未进 COPR/官方仓库）：

- **每个 agent 命令先过策略引擎再决定能否跑**（"decides what they may run **before it runs anything at all**"）
- **每次调用都写 systemd journal，无论允许还是拒绝**（审计闭环）
- **四档 tier**：`safe` / `standard` / `developer` / `unrestricted`；`developer` 必须设 `developer_user`（真实账户），**没设则拒绝启动**；该 tier 下 `bash`/`python3`/`gcc`/`npm`/`cargo` 以该用户身份跑而**不是 root**
- `timeout_secs` 默认 30（慢镜像上 `dnf install` 要调大）
- 目标机**不需要装任何 agent 工具**；标准版或**不可变版**都行
- 用 Rust 的理由：会 spawn 任意进程 + 流式读输出 + 前置策略决策 → 需要内存与并发的编译期保证（引用 NSA / 白宫国家网络总监建议弃用 C/C++）

**`amineutron/fedora-agents`**（TypeScript，MIT，npm `fedora-agents-mcp`，KVM/libvirt + Borg/Timeshift）：

- 每工具声明 `requiresSudo`（**逐脚本** sudoers，**绝不用全局 sudo**）与 `dangerous`（向客户端声明破坏性 → 必须人确认）
- **暴露的工具没有权限表条目 → server 拒绝启动**（fail-closed on unregistered tools）
- 权限表由 `src/config.ts` 生成（`npm run security:table`）**且在 CI 校验**
- 每调用一个 correlation ID，JSON 审计日志**在回复 agent 之前同步落盘**
- **重试取决于工具性质**：只有幂等读（`vm_status`/`backup_status`/`backup_list`/`backup_verify`）重试 3 次（1s/2s/5s）；**变更操作永不重试**
- 退出码翻译成类型化 `ErrorCode`
- **明确不做**：不从 agent 文本构造 shell（Zod 校验后作为**独立参数**传入，绝不插值）；不写 `PATHS` 之外；**无任何网络输出**
- 威胁模型：`vm_destroy`/`backup_restore` 标 `dangerous`；**`virsh`/`virt-clone`/`qemu-img` 上没有任何 sudo 规则**（那等于 root）

**Fedora 官方工具（核验）**：`dnf-automatic`（44/45/Rawhide 存在）、`dnf5` 5.4.6.0-1.fc44、**`dnf5-plugins` 5.4.6.0-1.fc44（含 `needs-restarting`）**、`rpm-ostree` 2026.3-2.fc44、`toolbox` 0.3-4.fc44。

**Fedora 独有坑**：
- **不可变系统（Silverblue/Kinoite/Bazzite）上 `dnf install` 直接失败**，要 `rpm-ostree install` 或 `toolbox`。给 agent 的指令必须区分"标准 Fedora"与"Fedora Atomic"。
- **很多 AI 工具只发 `.deb`**：Anthropic 的 Claude Desktop Linux 版只发 `.deb`，Fedora 用户自己重打包成 RPM。评估工具链时要算这个分发摩擦。

**Fedora 技能市场**：`awesome-copilot/fedora-linux-triage`（观测 **8.9k**）、`xejrax/brew-install`（3.1k）、`silverod/rpm-ostree-toolkit`（721）、`mina-atef-00/hermes-browser-fedora-atomic`（190，**Hermes 专用**）。

### 7.4 Debian 专属

**`debvulns`（原 `debsecan-mcp`）** —— ⚠️ **包名改过**，旧名停在 0.1.5：

| 接口 | 命令 | 用途 |
|---|---|---|
| MCP server | `debvulns-mcp` | 接入 Claude Desktop / VSCode / opencode |
| 独立 CLI | `debvulns` | 扫描，输出 JSON / CSV |
| Prometheus exporter | `debvulns-exporter` | 暴露漏洞指标给 Grafana |

能力：扫全部已装包的已知漏洞；**CVE 研究含 EPSS 分数**（被实际利用的概率）；**自动识别 Debian suite**（bookworm/trixie/sid）；缓存 `/var/cache/debvulns`（不可写退 `~/.cache/debvulns`），**>24h 自动刷新**；按严重度过滤。
> EPSS 的价值：把"有 CVE"和"值得今晚就修"区分开。纯 CVE 列表会让 agent 淹没在噪音里。

**Debian 官方工具（`sources.debian.org` API 核验）**：`unattended-upgrades` **2.13**、`needrestart` **3.11-1**、`debsecan` **0.4.20.2**、`apt-listchanges` 4.8+nmu3、`debian-goodies` 0.88.2（含 `checkrestart`）。

```bash
sudo apt install unattended-upgrades needrestart debsecan apt-listchanges apt-listbugs
sudo dpkg-reconfigure -plow unattended-upgrades
sudo needrestart -r l            # ⚠️ 关键：列出仍跑旧库的服务
sudo debsecan --suite bookworm --format detail
```

> ⚠️ **`unattended-upgrades` 默认不重启。** 装了新内核也只提示。**"我开了自动更新所以安全了"是 Debian/Ubuntu 最常见的安全假象**——一堆服务还在跑有洞的旧库。`needrestart` 就是用来戳破它的。

**Debian 技能市场：三个里最薄。** 只有 `cepheiden/openbot-esxi`（1.9k，Debian 13 zero-touch ESXi 部署）、`nvidiaskills.sh/holoscan-install-debian`（1.8k，领域专用）、`xixu-meskills.sh/secure-linux-web-hosting`（13）。**没有 Debian 通用的巡检/加固技能** → 借用 Ubuntu 的（apt 生态兼容）。

### 7.5 Ubuntu 专属

**`pazuzu1w/ubuntu_mcp_server`**：**44★**（三个发行版专属 MCP 里最高），但**最后提交 2025-06-29，已停更约 16 个月**。⚠️ **能操作操作系统的、长期未维护的 MCP 是明确风险项**，用前必须自己审源码。

**Ubuntu Pro / ESM / Livepatch / Landscape —— Ubuntu 与另两家最大的结构性差异**（把"安全更新"做成了**付费订阅 + 集中管理**）：

| 组件 | 作用 |
|---|---|
| **Ubuntu Pro** | 订阅制；**ESM** 把安全补丁覆盖延长到**十年以上** |
| **Livepatch** | **不重启打高危/严重内核 CVE 补丁**；LTS 绑定 Pro 后**自动启用** |
| **Landscape** | 集中面板，可在**舰队规模**管理 Livepatch 与机器状态 |
| `pro` 客户端 | 本地管理订阅 / ESM / Livepatch 状态 |

```bash
pro status && pro security-status && sudo pro enable livepatch
```
> `pro security-status` 直接告诉你哪些包已过标准支持期、没有安全更新——**比读 CVE 列表更接近"我到底安不安全"**。

**Ubuntu 技能市场：三个里最丰富** ⭐（尽管 awesome-copilot **没有** Ubuntu 专家技能）：

| 技能 | 安装 | 说明 |
|---|---|---|
| `zelzaclaw/doc-sysadmin` | 1.3k | Ubuntu 24.04 宿主机管理（磁盘/RAM） |
| `linsuisheng034/ubuntu-browser-session` | 1.2k | 真实 Ubuntu Server 浏览器会话 |
| **`chengchiangwork/ubuntu-inspector`** | 1k | **系统巡检**：CPU/内存/磁盘/网络/服务/安全审计 |
| `kklouzal/ubuntu-encyclopedia` | 951 | **文档优先工作流**（先查文档再答） |
| `solomonneas/proxmox-create-vm` | 951 | Proxmox VE 上建 Ubuntu 24.04 LXC/VM |
| `solomonneas/hyperv-create-vm` | 914 | Hyper-V + cloud-init 建 Ubuntu 24.04 |
| `shenzheke/ubuntu-wsl-system-cleanup` | 842 | **审计并安全清理**系统垃圾/缓存/日志 |
| `twinsgeeks/ubuntu-ai` / `ubuntu-ollama` | 789 / 682 | Ubuntu/Debian 上搭本地 AI 平台 |
| `krishnakumarmahadevan-cmd/toolweb-ubuntu-hardening`（+v2） | 681 / 685 | 加固配置文件生成（22.04 LTS） |
| `microsnow/wsl-service-deploy` | 449 | WSL Ubuntu 服务一键部署 |

> `ubuntu-encyclopedia` 的"**文档优先**"与 Arch 的 `arch-wiki-mcp`、r/archlinux 的"Wiki 优先"是**同一个模式** → "用文档锚定 agent"已成跨发行版共识。

**Ubuntu 的 snap 双通道坑**：`snap refresh` 独立于 `apt`。给 agent 的更新流程必须显式覆盖两条，否则会出现"apt 说全更新了，snap 包还是旧的"。

### 7.6 `github/awesome-copilot` 发行版专家矩阵（A 级，**v5 已修正**）

⚠️ **修正说明**：v4 只探测了 `skills/` 与 `agents/` 两类路径，**漏掉了 `instructions/` 与 `plugins/`**，因此把 Arch 误记为"只有 agent"。**正确做法：拉全量目录树 `git/trees/main?recursive=1`，不要猜路径名。**

该仓库对每个发行版提供**最多 3 类**资源：

| 发行版 | `instructions/<d>-linux.instructions.md` | `skills/<d>-linux-triage/SKILL.md` | `agents/<d>-linux-expert.agent.md` | 合计 |
|---|---|---|---|---|
| **Arch** | ✅ 1,355 B | ✅ 930 B | ✅ 2,009 B | **3** |
| **Fedora** | ✅ 1,269 B | ✅ 920 B | ✅ 1,898 B | **3** |
| **Debian** | ✅ 1,503 B | ✅ 961 B | ✅ 2,201 B | **3** |
| **CentOS** | ✅ 1,329 B | ✅ 959 B | ✅ 2,059 B | **3** |
| **Ubuntu** | ❌ 404 | ❌ 404 | ❌ 404 | **0** |
| **RHEL / Rocky / Alma** | ❌ 404 | ❌ 404 | ❌ 404 | **0** |
| **openSUSE / SUSE** | ❌ 404 | ❌ 404 | ❌ 404 | **0** |

**三个判断**：① **Ubuntu 是唯一"零覆盖"**，尽管它 ClawHub 技能最多 → **市场丰富度 ≠ 官方专家库覆盖度**；② **有 CentOS 无 RHEL** → 这套库按"社区常见度"而非"企业装机量"选型；③ ⚠️ **`plugins/arch/` 不是 Arch Linux**，是 software **architecture** 插件（`plugin.json`: *"Architecture and modernization toolkit"*）——**用 `arch` 搜这个仓库，大部分命中是软件架构噪音**。

**三者真正的差异是权限模型，不是命令**：Fedora 版 = `dnf` + **SELinux** + `firewalld`；Debian 版 = `apt` + `dpkg` + **AppArmor**；Arch 版 = `pacman` + `systemctl` + `journalctl`（**必须处理内核更新/重启考量**）。

**统一输出格式（可直接当模板）**：`Summary` → `Triage Steps (numbered)` → `Remediation Commands` → `Validation` → **`Rollback/Cleanup`**。**"强制回滚"这一条就值得抄进任何自建运维 skill。**

### 7.7 跨发行版实用 MCP（VM / 容器 / 监控 / 配置管理）

| 类别 | 项目 |
|---|---|
| 虚拟化 | **`gilby125/mcp-proxmox`**（53★，权限可配置）、`ry-ops/proxmox-mcp-server`（27★，2026-10 活跃） |
| 容器 | **`manusa/podman-mcp-server`**（84★）、**`elusznik/mcp-server-code-execution-mode`**（340★，rootless 容器执行 Python）、`Kiln-AI/Kilntainers`（51★，临时沙箱） |
| SSH | **`muchiny/bridge-mcp`**（10★，337 工具 / 74 分组）、`Cosmicjedi/linux-administration-mcp`、`E13ctr0N/AiSysAdmin` |
| 监控/变更 | **`Higangssh/homebutler`**（300★，"只告诉你值得告诉你的事"）、`initMAX/zabbix-mcp-server`（229★，237 工具）、`SikamikanikoBG/homelab-monitor`（218★）、`tyxak/remotepower`（74★，含 patching） |
| 配置管理 | `sibilleb/AAP-Enterprise-MCP-Server`（33★，Ansible AAP）、`bsahane/mcp-ansible`（30★）、`jade-pico/antrieb-mcp-server`（14★） |

> **Ansible 是三家天然交集**：一份 playbook 覆盖 `dnf` 与 `apt`。**混合舰队上，"让 agent 写 playbook → 你审 → 再跑"比"让 agent 直接 SSH 执行"可控得多**（可审、可 diff、可回滚、可版本化）。

---

### 7.8 RHEL 系（v5 新增）：厂商官方最强，社区侧最弱

**`rhel-lightspeed` 组织全表（20 仓库，A 级）**——按 star 排序，⭐ = 与本主题相关：

| Stars | 仓库 | 状态 | 作用 |
|---|---|---|---|
| **317** | ⭐ `linux-mcp-server` | 活跃 | 只读 Linux 运维 MCP（= 官方 MCP Server for RHEL 的内核） |
| 48 | `docs2db` | 活跃 | 文档入库 RAG 管道 |
| 44 | ⭐ `command-line-assistant` | 活跃 | Red Hat 官方 AI 命令行助手（2024-10-17 创建，readthedocs） |
| 19 | ⭐ `okp-mcp` | 活跃 | Offline Knowledge Portal MCP = RHEL 的离线知识层 |
| 8 | `sysadmin-agents` | **已归档** | sysadmin agent 实验 |
| 6 | `docs2db-api` | 活跃 | RAG API |
| 5 | `goose-proxy` | 活跃 | Goose 代理 |
| 4 | `goose` / `docs2db-mcp-server` | 活跃 | Goose fork / 文档 MCP |
| 2 | `redhat-status-mcp` | **已归档** | Red Hat 服务状态 |
| 1 | `rhel-lightspeed-gitops` | **已归档** | GitOps 实验 |
| 0 | `HEAL` / `roz` / `pypi-cla` / `ci-container` / `roadmap-ci-container` / `renovate-config` / `coderabbit` / `rhel-cla-installer` | 部分活跃 | 基础设施与实验 |
| 0 | `textprep` | **已归档** | 文本预处理 |

**20 个里 4 个已归档 → 厂商官方 ≠ 长期维护，同样要看 `archived`。**

**社区侧：几乎全军覆没（A 级）**

| 项目 | Stars | 状态 | 判断 |
|---|---|---|---|
| `narmaku/linux-mcp-server-archived` | 0 | **已归档**（创建 13 天后停） | **唯一的 RHEL 专属社区 MCP** |
| `velopulent/tako` | 2 | 活跃 | 自托管面板（PAM 登录 + 三角色分进程隔离），覆盖 RHEL/Rocky/Alma；自述未到 v1 |
| `tommy-k/mcp-servermigrate` / `cu0001/aix-rhel-mcp-server` | 0 | — | 未成熟 |

**`awesome-copilot`：只有 CentOS 有（3 类俱全），RHEL / Rocky / Alma 全 404。**

**RHEL 系运维基座（D 级，未核验）**：`dnf-automatic`、`dnf needs-restarting`、SELinux（默认 enforcing）、`dnf updateinfo` / OpenSCAP、`subscription-manager`、`leapp` 升级路径。⚠️ **`redhat/leapp` 与 `redhat/insights-client` 在 GitHub 上都是 404**（这些组件不在 `redhat` 组织下）→ 想落地必须自己补核验。

### 7.9 openSUSE（v5 新增）：唯一的官方 AI 产物就是 systemd-mcp

- `openSUSE/systemd-mcp`：**10★**，Go，MIT，2026-09-24 推送。**`openSUSE` 组织前 100 仓库里没有第二个 MCP / AI 仓库。**
- 运维基座（官方仓库，非 AI 但 agent 会用）：`snapper`（**1,177★**，Btrfs 快照回滚——**agent 改配置前最该先建的东西**）、`open-build-service`（1,083★）、`libsolv`（610★）、`zypper`（495★）、`transactional-update`（142★）、`opensuse-migration-tool`（66★）。
- **openSUSE 专属 MCP / 技能 = 0。** 仅有的两个候选项目都是 0★ 且 **无许可证**（`lioilsources/LeapDoctor` 创建次日停更；`anjupathak03/zypper-mcp` 单日提交）→ ⚠️ **无许可证 = 默认保留全部权利，法律上不可用于生产。**
- **SLE（SUSE Linux Enterprise）侧未覆盖。**

---

## 8. 社区实证要点（r/NixOS 原帖）
**最正面的一手报告**（u/qmic，《NixOS is a game changer in terms of Linux management with AI》）：管理过**上千台服务器**（手工/脚本/Terraform/Ansible）的老运维，用 Claude Code 生成远程 LUKS 密码提示 + 错误 Telegram 通知等配置。原话：*"责任当然还是我的，但它承担了最无聊的部分。"*

**⚠️ 最关键的警告**（u/lily_34）：*"Claude……也会做很多可疑的事。**就在今天，它把我的用户加进了 `nix.settings.trusted-users`（这允许无代价提权到 root）**，还有好几次试图用非标准的 hack 来解决问题。所以它极有帮助，但必须极度小心。"*

**技术含量最高的建议**（u/gersilex）：*"Nix 尤其 NixOS modules 是**自描述**的。用 `nix eval` 和 options attrset，你基本上就拿到了每个可能选项的完整文档。**指示 LLM 只从那里获取信息、不要从别处。**让它搜索并读取它试图使用的任何选项的 description，不确定时读那个选项的源码。"*

**模型能力时间线**（u/Kai_）：*"LLM 在 **2025 年 11 月左右随着 Opus 4.5** 开始对 Nix 变得半像样……**它们编辑 nix 配置可能比我们大多数人还好。**它们也会完全照你说的做。"*

**MCP 之争**（作者 u/brinkjames 自己承认）：*"我**完全同意**你对 MCP server 的看法……**大多数我试过的就是很烂，或者无论怎样都不调用工具。**"* 反方 u/Creepy_Reindeer2149：*"对一个 100% 功能都能通过 CLI 和文件系统控制的系统，用 MCP 基本没意义。MCP 极其不可靠。"* 折中方案（u/mister2d）：*"写一个**渐进披露的 agent skill** 来和那个 MCP server 配对，效果非常好。"*

**社区最认可的模式**（u/First_Understanding2）：*"**我刚给 agent 们专门开了一整台 nixos VM。它们维护它**……我显然不接任何个人资源进去……**不把我的东西托付给它**，但它还是能替我干开发活。"*

**本地模型实测**：`gemma4:26b-a4b-it-q4_K_M`（24GB）与 `Qwen3.6-27B` 可用；**`Qwen3.5:4B` "太蠢了没法用，通常把文件搞坏然后试图 git checkout"**。

**r/archlinux 几乎没有 AI 运维讨论**——搜 "mcp" 全是蓝牙 `Failed to init mcp plugin` 报错等误命中。推断原因：Arch 是命令式发行版，缺"声明式配置 + 可回滚 generation + `nix eval` 自描述选项"这些让 agent 特别适配的抓手。

---

## 9. 技能市场实测（clawhub.ai / skills.sh）

**⚠️ ClawHub 搜 "nixos" 返回 "No skills found"**——没有任何 NixOS 技能。运维类只能从 GitHub 直发件拿。

ClawHub 上按安装量的可用件（`clawhub.ai/<creator>/<skill>`，CLI 是 `npm i -g clawhub`）：

| 技能 | 创作者 | 用途 | 安装量 |
|---|---|---|---|
| Ssh Essentials | arnarsson | SSH 命令、密钥管理、隧道 | 12.9k |
| Cron & Scheduling | gitgoodordietrying | cron 与 systemd timer 调度调试 | 10.9k |
| Linux | ivangdavila | 权限、磁盘满、OOM kill、卡死调试加固 | 6.6k |
| Linux & service basics | kowl64 | 日志、systemd/PM2 排障 | 6.5k |
| Ssh Exec | xejrax | SSH 在远程 Tailscale 节点跑单条命令 | 5.1k |
| Log Tail | xejrax | 流式读 systemd journal | 3.4k |
| Systemd | ckchzh | systemd 参考工具 | 2.3k |
| linux-kernel-crash-debug | crazyss | vmcore + crash 证据优先分析 | 2.2k |
| Restic Home Backup | moep90 | 加密 restic 备份（另有 Safe Apply Mode 版） | 2.1k |
| ssh-executor | rickkbarbosa | SSH 执行 + **结构化发现协议** | 1.8k |
| linux-firewall-hardening | discovery219 | 后端探测 + 幂等原子加固 | 1.3k |
| linux-sysadmin | husttsq | 中文：权限/SSH/存储/网络/systemd/防火墙/备份/TLS/Ansible/容器/IaC | 1.2k |

ClawHub 的 OpenClaw 插件（运维相关）：**Memory LanceDB**（16.1k，LanceDB 长期记忆 + 自动召回）、**Lobster**（11.4k，类型化管线 + 可恢复审批）、**Diagnostics Prometheus**（9.3k）、**Diagnostics OpenTelemetry**（8.2k）、**Diffs**（7.1k，只读 diff 查看器）、**OpenShell Sandbox**（1.8k）。

**skills.sh**（"The Open Agent Skills Ecosystem"，全时段安装量 1,283,962，安装命令 `npx skills add <owner/repo>`）：**榜单前 55 名里没有任何运维/系统管理类技能**——被编码工作流（mattpocock 系列）、浏览器自动化（vercel-labs/agent-browser）、视频生成（hyperframes）、飞书（lark）占据。**不要指望技能市场解决 NixOS 运维需求。**

**Arch 侧同样为零**（详见 §6.6）：clawhub.ai 搜 `arch` 全是 architecture（软件架构）噪音，搜 `pacman` 只有 1 个无关 DeFi 技能；AUR 上有 282 个 mcp 相关包但热度极低（榜首 pop 仅 1.76）。**两个发行版的运维能力都不在技能市场里。**

**Fedora / Debian / Ubuntu 侧则完全不同——市场覆盖有明显梯度**（第四轮实测）：

| 发行版 | ClawHub 覆盖 | 代表技能 |
|---|---|---|
| **Fedora** | 单件最热 | **`awesome-copilot/fedora-linux-triage`（观测 8.9k）**、`rpm-ostree-toolkit`（721）、`hermes-browser-fedora-atomic`（190，**Hermes 专用**） |
| **Debian** | **最薄** | `openbot-esxi`（1.9k，ESXi 部署）、`holoscan-install-debian`（1.8k，领域专用）。**无通用运维技能** |
| **Ubuntu** | **最丰富** | `doc-sysadmin`（1.3k）、`ubuntu-browser-session`（1.2k）、`ubuntu-inspector`（1k，系统巡检）、`ubuntu-encyclopedia`（951，文档优先）、`ubuntu-wsl-system-cleanup`（842）、`toolweb-ubuntu-hardening`（681）等 10+ 件 |

**结论：技能市场对 Ubuntu 覆盖最好（最常见服务器发行版），Fedora 单件最热，Debian 最薄（可借用 Ubuntu 的）。但三家都缺"官方维护的运维技能"** —— `awesome-copilot` 只有 Fedora 与 Debian 的 triage（Ubuntu 探测 6 个变体名全 404）。

---

## 10. 安全：四起必知事件

### 10.1 Deadbugz（2026-08）——恶意 MCP server 供应链投毒

单账户 **74 分钟内提交 23 个 PR**，横跨互不相关的 AI/开发者工具项目，植入同一族恶意 MCP server（伪装成文本格式化/摘要工具）。**前 3 次调用完全正常**，之后**静默重写自身工具元数据（description）**，把描述变成偷 `~/.ssh`、`~/.aws`、shell history、`~/.kube/config` 的指令并外传。载荷含 BTC 钱包地址。

**教训**：MCP server 是**携生产凭据运行的未审查第三方代码**。"审查一次"在结构上失效——t0 审查通过，t1 叛变。恶意藏在**元数据**而非代码路径，静态扫描不可见。

**防御（按 ROI 排序）**：
1. **工具元数据漂移监控**——每次重连对比工具列表快照（name + description + inputSchema 的哈希），任何变化默认不信任并告警。**直接克星**。
2. **内容寻址固定**——用 `pkg@sha512:...` 而非版本字符串；**禁止生产 agent 用 `npx` 直跑**（每次现拉最新版）。
3. **权限最小化**——agent 跑在专用最小权限账户，与 SSH key、云凭据隔离。
4. **运行时监控**——监控 agent spawn shell、下载归档、访问 `~/.ssh`/`~/.aws`、异常外连。

同族事件：Smithery.ai 路径穿越（2025-06，3000+ server 配置含明文密钥泄露）→ Anthropic Git MCP CVE 链（2025-12）→ Clinejection（2026-02）→ LiteLLM rug pull（2026-03，95M 月下载）→ Deadbugz（2026-08）。**没有一次需要攻击 MCP 协议本身。**

### 10.2 CVE-2026-84289——Hermes Agent MCP 内存放大 DoS ⭐

- **影响**：Hermes Agent **≤ 0.18.2**
- **机制**：`tools/mcp_tool.py` 的 `_discover_tools()` / `_refresh_tools()` 对 `list_tools()` 返回的 `description` 与 `inputSchema` **无预算透传**；工具结果无上限走 `json.dumps()`。
- **实测**：**6,478 字节 schema → 10,548,310 字节（约 1628 倍）**；单次运行接受的 MCP 描述达 10MB。并发槽占满后返回 `429 Too many concurrent runs (max 2)`，且失败请求不释放已分配缓存 → 持久 DoS。CVSS 5.3。**放大发生在框架侧，攻击者只需很小的恶意配置。**
- **修复（0.20.5）**：`_MCP_HARD_RESULT_CAP_CHARS = 2_000_000` + `_truncate_mcp_text_result`（头 40%/尾 60%）+ 50,000 字符预算溢写磁盘。

**本机实测状态**：commit `4e7403130e`（2026-10-01）；`tools/mcp_tool_content.py` 中 `_MCP_HARD_RESULT_CAP_CHARS = 2_000_000` **存在**，`_truncate_mcp_text_result` **存在** → **不受该 CVE 影响**。

**但（本报告推断，D 级）**：本机 `tools/*.py` 里**未找到** `MAX_TOOLS` / `MAX_DESC_CHARS` / `MAX_SCHEMA_CHARS` / schema 深度上限这类**元数据侧**预算常量。CVE 修复重点是**结果侧**，而 1628 倍放大走的恰恰是**元数据侧**（`list_tools` 的 description/inputSchema）。→ **结果侧已修，元数据侧建议自己收窄**：坚持用 `tools.include` 白名单，只装工具数极少的 server（如 mcp-nixos 的 2 个）。

### 10.3 AUR 供应链投毒（Arch 侧核心风险，2026 进行中）

r/archlinux `1vaxtcs`："Another wave - **200+ malicous AUR packages adoptions** that are overwhelming my scanner."（原帖 `u/Saren-WTAKO`）

**攻击手法（原帖原文）**：
> "**the maintainer got pwned, or orphaned packages are adopted by the bad actor.** **AUR's git commit author is easily impersonated** so you can see the commit comes from the same person, but in fact it's not. … The malicious packages are **info stealers**."

三个要点：① 维护者账号被攻陷，或**孤儿包被恶意者收养**（AUR 允许任何人收养 orphan）；② **git commit author 可冒充** → "提交者看起来还是原作者"**不构成任何信任证据**；③ 载荷是**信息窃取器**。

已知受害者（部分）：`1panel`、`1panel-git`、`archutil`、`cinnamon-no-nemo`、`icloudpd`、`stirling-pdf-desktop-bin`、`windscribe-cli-v2-bin`、`pandoc-eisvogel-template`、`python-chatterbot`、`instawow-bin`、`pylnker-git`、`wiki-go`、`gitarbor-bin`、`boringssl-git`。dropper 哈希 `e73a35b3e75e94746428d1a207703d6335933deadee7d1d9c9d0328df7b9df77`。

**检测手段**：

| 手段 | 用法 |
|---|---|
| aurwatch.org API | `curl -fsS "https://aurwatch.org/api/v1/check?pkg=$pkg" \| jq -r '.status'` → `clean`/`low`/`medium`/`high` |
| 批量自查 | `pacman -Qqm \| xargs -P16 -I{} bash -c 'check_pkg "$@"' _ {}`（`-Qqm` = 仅外来/AUR 包） |
| 恶意清单 | `curl 'https://aur-audit.wtako.net/packages?filter=red&limit=200'` |
| 正确上报渠道 | **`aur-general@lists.archlinux.org`**（Reddit 不是上报渠道，但作为公众预警合理） |

**政策讨论**：社区在问"是否应限制或禁止孤儿包被收养"；有人主张"根本不该允许改包的推送者，维护者跑路就停更，想接手就 fork 成新包名"。

**⚠️ 二次信任风险**：aurwatch.org / aur-audit.wtako.net 都是**第三方个人服务**。让一个第三方服务告诉你"哪些包是恶意的"本身就是一个新的信任依赖——生产环境使用前请自行评估。

### 10.4 AI agent 运维事故链（r/linuxadmin，2026）

| 事件 | 要点 |
|---|---|
| **GuardFall**（`1unxuvf`） | 用**几十年历史的 bash 技巧**做 prompt injection，打穿**大多数** coding agent 的防护。唯一防住的是 **Continue**，而它 2026 年初被 Cursor 收购后**停止维护**。评论："a random bash trick can own most of these agents" |
| **CVE-2026-59822**（LiteLLM，`1w5yvf5`） | MCP Streamable HTTP endpoint 的 OAuth2 passthrough。**key 校验失败时回退路径替换成空的 `UserAPIKeyAuth()` 对象**，下游当成合法会话 → **任何伪造 `Authorization` 头的请求都能列出并调用 MCP 工具，无需有效 key**。CVSS v4 **8.8**，修复 **1.84.0**，进 CISA KEV。缓解：反代阻断 `/mcp/` |
| **CVE-2026-42271**（LiteLLM，同族） | **MCP-bridge 子进程命令注入**，修复 1.83.7，6 月进 KEV，可与 Starlette Host-header 漏洞 CVE-2026-48710 串联 |
| **CVE-2026-9198**（Langflow，`1vl6ofz`） | `GET /api/v1/auto_login` **给任何网络调用者签发 SUPERUSER JWT**，无鉴权、不绑 loopback。进 CISA KEV |
| **RovoBlast**（`1vm56v9`） | Atlassian Rovo 经单个 URL 参数 `rovoChatPrompt` 被劫持（DEF CON 34 / Varonis），影响 Jira/Confluence/Bitbucket + 50 多 connector |
| **Cryptographic Context Injection**（`1vu37hc`） | 把 prompt injection 载荷**加密**让分类器读不到，再让模型自己解密执行 |
| **DNS-AID**（`1ts0gip`） | Linux Foundation 发布：AI agent 的 DNS-based discovery（生态开始出现 agent 发现层） |
| `atraxsrc/claude-revoke`（3★） | **审计并撤销 Claude Code 在 Linux 上被授予的一切**（trusted folders、"always allow" 列表）。给 agent 做权限回收的工具 |

**⭐ 共同失败模式（CISA 原文，最有价值的一条）**：

> "most share the same failure class: **auth logic trusting a reconstructed path, a suffix match, or a fallback object instead of doing a hard check**"

翻译成 checklist：
1. **不接受"重建出来的路径"做鉴权**（路径归一化后再判）
2. **不用后缀匹配做鉴权**（`endsWith('/mcp')` 可绕过）
3. **回退路径绝不返回"空但合法"的对象**（失败就是失败）

**⚠️ 在 LiteLLM 前挂 MCP 工具链的，必须确认越过 1.83.7 与 1.84.0 两个修复，而不是只打最新的那个。**

---

## 11. 坑与反直觉

1. **官方目录大 ≠ 覆盖你的场景。** 65 个 MCP + 152 个技能听起来很多，全库 `grep -ril nixos|ansible|systemd|pacman` 在技能目录下命中 **0 条运维技能**。别被数量骗了。
2. **`agent.md` 不是一份文件。** Hermes 里人格（SOUL.md）、项目指令（AGENTS.md）、记忆（MEMORY.md/USER.md）是三套独立系统，互不喂数据。改 SOUL.md 不会填 USER.md。
3. **记忆是冻结快照。** 中途改配置不生效，必须重启会话。排查"为什么它忘了"时先看这个。
4. **profile 不是沙箱。** 建 profile 只隔离状态目录，不限制文件系统访问。
5. **内置记忆只有 2200 字符。** 它设计上就不是知识库，是偏好存储。拿它装运维知识必然爆。
6. **NixOS 社区对"agent 管 NixOS"是怀疑的。** 论坛原话："用 agent 来做这件事，某种程度上违背了初衷吧"；"AI 这个 easy button 是你在赚到资格之后才按的"。本地小模型在 Nix 语法上幻觉严重。
7. **`nix-agent` 默认高信任。** 未经提示即可 `switch` + 免密 sudo，低信任模式是 opt-down 而非默认。作者自称实验性。
8. **`llm-wiki` 的价值在"编译一次"，不在"检索"。** 若你只是想要语义搜索，`qmd` 更轻。
9. **Reddit 在本环境可抓，但必须走 Atom 后端。** `reddit.com/*/search.rss` 与 `old.reddit.com` 直连会被拦（后者跳登录墙），但 Hermes 自带的 `reddit-reading` 技能（`optional-skills/social-media/reddit-reading/scripts/reddit.py`）可用——默认匿名 Atom 后端，**约 1 请求/分钟/IP**，遇 429 自动等待重试。**匿名后端不含点赞数与评论嵌套**，只能拿正文与评论内容。要互动数需在 `~/.hermes/.env` 注册免费 Reddit "script" 应用（`REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`，**是应用注册不是账号登录**）。
10. **NixOS 社区对"agent 管系统"的真正答案是沙箱，不是权限。** r/NixOS 上 AI agent 相关的高质量项目绝大多数是沙箱（jailed-agents、nix-sandbox-mcp、nix-bwrapper、landlock）。最被认可的模式是"给 agent 一台一次性 NixOS VM，让它自己管自己"。
11. **ClawHub 上没有 NixOS 技能**（搜 "nixos" → "No skills found"）。skills.sh 榜单前 55 名也没有任何运维类技能。技能市场解决不了 NixOS 运维需求。
12. **MCP 的上下文税是真实成本。** nix-sandbox-mcp 的 README 给的数据：静态加载 60 个工具 ≈ 47k token（在你开口之前）。**这是"一个参数化工具"优于"每个环境一个工具"的量化依据**（约 420 vs 1200+ token）。
13. **`nix.settings.trusted-users` 是 agent 最爱踩的提权坑。** r/NixOS 用户实测：Claude 未经提示把用户加进 `trusted-users`（等于免费提权到 root）。`AGENTS.md` 里要显式禁止。
14. **本地小模型写 nix 会毁文件。** 实测 `Qwen3.5:4B-Q6` "太蠢了没法用，通常把文件搞坏然后试图 git checkout"。24GB 卡上可用的是 `gemma4:26b-a4b-it-q4_K_M` / `Qwen3.6-27B`。
15. **MCP 的"审查一次"是结构性失效的控制。** Deadbugz 证明：恶意 server 前 3 次调用完全正常，之后重写自己的工具元数据。必须做**工具元数据漂移监控**（快照哈希对比），并且**不要用 `npx` 直跑**（每次现拉最新版）。

**Arch 专属（第三轮）**：

16. **`arch-mcp` 的仓库名 ≠ 安装名。** 仓库 `nihalxkumar/arch-mcp`，PyPI 包 **`arch-ops-server`**，命令 `uvx arch-ops-server`。搜 "arch-mcp pip install" 找不到。
17. **`arch-mcp` 有写操作，别当只读用。** 14 个工具里 5 个会改系统（`install_package_secure`/`remove_packages`/`manage_orphans`/`manage_install_reason`/`optimize_mirrors`）。必须 `trust: untrusted` + `tools.include` 白名单。
18. **`arch-wiki-mcp` 只有 1★，但设计比 59★ 那个更该学。** 三档证据分层（证据/半证据/指针）+ `<esp>` 占位符防误粘（"so a thoughtless paste fails at the shell"）是可搬进任何运维 skill 的通用模式。
19. **`herraiz-org/ai-skills` 把 arch-mcp 链接指向了一个 fork。** `iht/arch-mcp` 是 2026-08-08 的 fork（0★，当日停更）。工具名与上游逐字一致，技能能用，改链接即可。
20. **Arch News 的 RSS 只有约 10 条。** 任何"更新前查新闻"的工作流都有盲区：上次全量升级早于最旧条目时，中间期间的公告**不可达**。必须**显式报告盲区**，而不是当作"没有新闻"。
21. **`checkupdates` 在 `pacman-contrib` 里，不在 `pacman` 里。** 而引导安装它时**绝不能从 AUR 满足该依赖**——那等于用不可信源装一个"用于检查不可信源"的工具。
22. **"commit author 是原作者"不是信任证据。** AUR 的 git commit author 可冒充。唯一信任来源是你自己读了那次的 PKGBUILD diff。
23. **孤儿包被收养 = 需重新审计。** AUR 允许任何人收养 orphan，这是本轮 200+ 恶意包的入口之一。把"maintainer 变更"和"orphan 被收养"当作审计触发器。
24. **Arch 知识库不需要 MCP。** `arch-wiki-lite` 一个包给出离线全文 Wiki（体积 1/9）。上 MCP 联网查 Wiki 是**把确定性换成不确定性**。
25. **clawhub.ai 搜 "arch" 全是 architecture 噪音。** 唯一 Arch Linux 项是个玩笑 skill（`j3ffyang/arch-sign-off`）。技能市场对 Arch 运维零覆盖。
26. **r/archlinux 有明显的反 AI slop 情绪。** AI 生成的冗长报告即使内容正确也会被社区忽视甚至围攻（200+ 恶意包事件的原帖就被这样对待）。报安全事件写**简洁事实 + 链接 + 包清单**，直发 `aur-general@lists.archlinux.org`。
27. **`informant` 在官方仓库，不在 AUR。** 它把"更新前读新闻"从"agent 记得要做"变成"pacman 强制拦你"——**用机制替代提示词**，比写进 AGENTS.md 可靠。
28. **`codexspidey/archsafe` 已弃坑。** 2026-06-24 后无提交、无许可证。同类需求用 `archward`（GPL-3.0，2026-08 仍在更新）或自建。
29. **Arch 没有声明式回滚，必须靠快照补。** 这是与 NixOS 最大的结构性差异：NixOS 的回滚是系统能力，Arch 要靠 btrfs snapshot / timeshift / `downgrade`。**快照必须发生在升级之前，且这一步不能交给 agent 判断。**
30. **聚合站点的技能列表会造假。** `mcpmarket.com` 把 `ranicharradi/arch-maintenance-skill` 列为真实技能，但该仓库**返回 404、不存在**。任何来自聚合站的技能都要**逐个回 GitHub 核验**。

**Fedora / Debian / Ubuntu 专属（第四轮）**：

31. **最好的运维 MCP 不是发行版专属的。** `openSUSE/systemd-mcp`（厂商官方、MIT、polkit 授权、默认禁写）覆盖 Fedora/Debian/Ubuntu 全部——因为它们都跑 systemd。**先装它，再考虑发行版专属件。**
32. **`systemd-mcp` 默认 `--allow-write=false`，这是设计不是遗漏。** 要写 systemd 必须显式打开并触发 polkit；`--noauth` 甚至要求把值写成字面量 `ThisIsInsecure`。
33. **Fedora 的重启检测不是 `needrestart`，是 `dnf needs-restarting`**，且在 `dnf5-plugins` 包里。Debian/Ubuntu 才是 `needrestart`。
34. **`unattended-upgrades` 默认不重启。** 装了新内核也只提示 → 系统仍跑旧代码。**"我开了自动更新所以安全了"是 Debian/Ubuntu 最常见的安全假象**，`needrestart` 就是用来戳破它的。
35. **Debian 的 MCP 包名改过。** `debsecan-mcp` 停在 0.1.5，之后全在 **`debvulns`**。搜旧名会装到死版本。
36. **Ubuntu star 最高的 MCP 已停更 16 个月。** `pazuzu1w/ubuntu_mcp_server`（44★）最后提交 2025-06-29。**能操作操作系统 + 长期未维护 = 明确风险项。**
37. **awesome-copilot 有 Fedora 和 Debian 专家技能，但没有 Ubuntu 的。** 探测 6 个 Ubuntu 变体名全部 404。Ubuntu 用 `debian-linux-triage`。
38. **两个 triage 技能真正的差异是权限模型，不是命令。** Fedora 版带 **SELinux + firewalld**，Debian 版带 **AppArmor**。这才是"发行版专属"的实际含义。
39. **Fedora 不可变版上 `dnf install` 直接失败。** Silverblue/Kinoite/Bazzite 要 `rpm-ostree install` 或 `toolbox`。给 agent 的指令必须区分"标准 Fedora"与"Fedora Atomic"。
40. **很多 AI 工具只发 `.deb`。** Claude Desktop Linux 版只有 `.deb`，Fedora 用户自己重打包成 RPM。**Ubuntu/Debian 优先拿到官方包，Fedora 常在"自己重打包"的位置。**
41. **`fedora-agents` 的 fail-closed 值得抄：暴露的工具没有权限表条目就拒绝启动。** 多数 MCP server 是"没登记就默认放行"，它反过来。
42. **`fedora-agents` 对变更操作永不重试。** 只有幂等读重试 3 次。**"重试"在运维场景是危险默认值**——agent 网络抖动重试一次 `vm_destroy` 就是灾难。
43. **`redwrench` 的审计日志连"被拒绝"的调用也记。** 只记成功的审计是半个审计；**价值在于能看到"谁试图做什么但被拦了"。**
44. **CVE-2026-59822 的教训是"回退对象不能是空但合法"。** LiteLLM 校验失败时返回空 `UserAPIKeyAuth()`，下游当成合法会话 → 任何伪造 `Authorization` 头都能调 MCP 工具。**失败就返回失败。**
45. **LiteLLM 今年两次进 KEV（修复版本 1.83.7 与 1.84.0）。** 只打最新那个不够。**在 LiteLLM 前挂 MCP 工具链的必须两个都过。**
46. **GuardFall 证明 agent 的注入防护不是静态属性。** 几十年前的 bash 技巧打穿多数 coding agent，唯一防住的 Continue 已被收购停维护。**别把"我选了防护好的 agent"当成安全边界。**
47. **Ubuntu 有两条更新通道（apt + snap）。** 只做 apt 会出现"apt 说全更新了，snap 包还是旧的"。流程必须显式覆盖两条。
48. **Ubuntu Pro / ESM 是订阅，不是配置。** `pro security-status` 直接告诉你哪些包已过标准支持期、没有安全更新——比读 CVE 列表更接近"我到底安不安全"。
49. **ClawHub 上 Ubuntu 技能最丰富，Debian 最薄。** 同为 apt 系，Ubuntu 有 10+ 件（最多 1.3k），Debian 只有 3 件且都是领域专用（ESXi / NVIDIA）。**Debian 用户可借用 Ubuntu 的技能。**
50. **Ansible 是混合舰队的正解方向。** 一份 playbook 覆盖 `dnf` 与 `apt`。**"让 agent 写 playbook → 你审 → 再跑"比"让 agent 直接 SSH 执行"可控得多**（可 diff、可回滚、可版本化）。
51. **`ubuntu-encyclopedia` 用"文档优先"设计，和 Arch 的 `arch-wiki-mcp`、r/archlinux 的"Wiki 优先"是同一个模式。** "用文档锚定 agent"已是跨发行版共识。

**52–58（v5 新增，来自 Red Hat 官方 MCP 与覆盖边界补充）：**

52. **`linux-mcp-server` 的 HTTP transport 当前无鉴权。** 官方文档明文：*"should not be used in production or on untrusted networks"*。**只读也一样致命**——日志、进程、网络连接、主机信息全暴露。**只用 stdio**，或自加带鉴权的反代。
53. **不要把"LLM 闸门"当成安全边界。** Red Hat 的 Gatekeeper 是真实存在的三层护栏之一（Gatekeeper LLM + 人在环 + 沙箱），但**官方模型评分表仍是 `??`（未填）**，且沙箱官方自述 *"rudimentary"*。它是"多一层"，不是"可以替代人工批准的那一层"。
54. **厂商官方 ≠ 长期维护。** `rhel-lightspeed` 组织 20 仓库里 **4 个已归档**。引用厂商项目同样要看 `archived` 标志。
55. **无许可证的 MCP 不能用于生产。** openSUSE 仅有的两个专属 MCP 都是 0★ 且**无许可证**（默认保留全部权利，法律上不可用）。**不要因为"没有别的选择"就用它。**
56. **⚠️ `awesome-copilot` 里的 `plugins/arch/` 不是 Arch Linux**，是 software **architecture** 插件。用 `arch` 搜这个仓库，**大部分命中是软件架构噪音**。
57. **厂商官方也不一定覆盖你的发行版。** `awesome-copilot` 覆盖 **CentOS 却不覆盖 RHEL / Rocky / Alma**——按"社区常见度"选型，不是按"企业装机量"。**技能市场丰富度 ≠ 官方专家库覆盖度**（Ubuntu 就是反例：ClawHub 最多，官方库 0 覆盖）。
58. **抽样探测路径会漏掉整类资源。** `awesome-copilot` 有 **4 类**资源目录（`instructions/`、`skills/`、`agents/`、`plugins/`），只探 2 类就会得出错误结论。**存在性核验要拉全量目录树（`git/trees/main?recursive=1`），不要靠猜路径名。**

---

## 12. 未核实 / 存疑

- ~~`arch-mcp`、`arch-wiki-mcp` 未核验~~ → **第三轮已核验**（GitHub API + PyPI + Arch 官方包库 API），见 §6.1。
- `homelab-mcp`、`mcp-homelab-server` 的 star 数、最后提交时间、实际可用性未核验。
- **Arch 侧（第三轮新增，均 C 级）**：`arch-mcp` 的实际工具体验、`audit_package_security` 的 50+ 红旗命中率、`install_package_secure` 的拦截有效性——**均未独立复现**；`arch-wiki-mcp` 的 hash 稳定性与 `test_contract.py` 覆盖面未复现；`herraiz-org/ai-skills` 的 pytest 套件**存在但未运行**（A 级确认文件存在，未验证通过状态）；`traur` / `ks-aur-scanner` 的维护状态与检出能力未核验；`archward` 的实际可靠性、快照在不同文件系统上的表现未实测。
- **⚠️ `aurwatch.org` / `aur-audit.wtako.net` 均为第三方个人服务**，可用性、准确性、数据更新频率**未核验**。它们来自 Reddit 原帖评论（C 级）。生产环境使用前自行评估——**让第三方服务告诉你"哪些包是恶意的"本身就是一个新的信任依赖**。
- AUR 上的 MCP 包（`github-mcp-server` 等，0 票、个人维护）**安全性未审计**。
- **第三轮未做**：r/archlinux 关于 AUR 事件的后续帖（是否有限制孤儿收养的正式决议）、Arch 官方对 AI 生成 bug report 的政策、`paru`/`yay` 的 `--news` 实际行为差异。
- **Fedora / Debian / Ubuntu 侧（第四轮新增，均 C 级）**：`simonives/redwrench` 的 **star 数 / release 数 / issue 状态未核验**（GitHub API 触达未认证限流 `remaining 0/60`，返回 429；README 经 raw 读取成功）——**作者自述业余项目、未进 COPR 或 Fedora 官方仓库**；`redwrench` 四个 tier **具体允许/拒绝哪些命令未逐条核验**，用前必须自己读策略文件；`amineutron/fedora-agents` 与 `copyninja/debsecan-mcp` 同样未拿到 star 数（README/SECURITY.md 读取成功）；`openSUSE/systemd-mcp` 的 6 个工具**未实际调用测试**，`gatekeeper` 的 polkit policy **未逐行核验**；`pazuzu1w/ubuntu_mcp_server` 的 44★ 与实际能力未复现；`debvulns` 的 EPSS 数据源与刷新机制未实测。
- **各发行版官方工具的"AI 友好性"未评估** —— `dnf-automatic`、`unattended-upgrades`、`needrestart` 是否输出机器可读格式、是否适合 agent 解析，未验证。
- ClawHub 的"安装量"是平台自报观测值，**不同技能间可比性存疑**（"Updated 5mo ago" 与 "Observed 6d ago" 两种口径混用）。
- **第四轮未做**：r/Ubuntu 与 r/debian 的 AI 运维讨论深挖（搜索结果与 AI 运维相关性低，只有零散个案）；`snap` 与 agent 交互的实际坑；Ubuntu Pro 定价与 AI 运维成本模型；`CVE-2026-9198`（Langflow）、`RovoBlast`（Atlassian）、`Cryptographic Context Injection` 的完整技术细节——均来自 r/linuxadmin 转述的第三方分析（C 级），未回原始报告核验。
- **v5 新增存疑**：
  - `linux-mcp-server` **在非 RHEL 发行版上的实测**——官方文档称支持 "other systemd-based distributions"，**未在 Arch / Debian 上实跑验证**（D 级推断）。
  - `linux-mcp-server` 的 **Gatekeeper 评测分数**官方仍是 `??`；`run_script` 的三层护栏（尤其沙箱层）**未实际测试**。
  - `linux-mcp-server` 的 **`auth_policy.py` 完整语义**只读了前 90 行与 pydantic 校验器，**未逐行读完**；`docs/keycloak.md` 的 Keycloak 接入**是否已实装于 HTTP transport 未核实**（按"默认不安全"对待）。
  - `rhel-lightspeed/command-line-assistant`（44★）**仅记录存在与活跃度，未深入架构**。
  - **RHEL 系运维基座**（`dnf-automatic` / `dnf needs-restarting` / SELinux / OpenSCAP / `subscription-manager` / `leapp`）**全部未核验**（D 级）。注意 `redhat/leapp` 与 `redhat/insights-client` 在 GitHub 上均 404。
  - **SLE（SUSE Linux Enterprise）侧完全未覆盖。**
  - `velopulent/tako`（2★）**未实际部署测试**；自述"尚未到 v1"。
- 各记忆 provider（byterover / holographic / honcho / mem0 / openviking / retaindb / supermemory）的实际效果未实测。
- `mcp-nixos` 的"约 1030 token / 2 工具"、`nix-sandbox-mcp` 的"约 420 token"、`nix-agent` 的默认信任档、`nixos-management-skill` 的覆盖范围——**均为项目自述，未独立复现**（C 级）。
- `YPares/rigup.nix` 的 README 两次抓取均返回空（GitHub 页面与 raw 均失败），其描述来自搜索结果摘要，非逐字 README。
- `nix-mcp`（bastianasmussen / stubbedev 两个同名仓库）、`nix-infra`、`ai-jail`、`nixpi` 的实际可用性与维护状态未核验。
- **本机 Hermes 未见元数据侧预算常量**（`MAX_TOOLS` / `MAX_DESC_CHARS` / `MAX_SCHEMA_CHARS` / schema 深度）——据此推断 CVE-2026-84289 的元数据放大向量可能仍需自行收窄。**这是推断，不是已核实的漏洞结论**（D 级）。
- r/archlinux 缺少 AI 运维讨论的原因（"Arch 是命令式发行版"）为**本报告推断**，无直接证据。

**抓取失败与解法清单**（跨三轮汇总）：

| 目标 | 现象 | 解法 |
|---|---|---|
| `raw.githubusercontent.com/egarcia74/arch-wiki-mcp/**main**/README.md` | 404 | **默认分支是 `master`**，改分支名成功（第二轮曾误判为"仓库不可用"） |
| `github.com/nihalxkumar/arch-mcp` 等 GitHub **HTML 页** | WebFetch 返回空内容 | 改用 `api.github.com/repos/...` + `raw.githubusercontent.com/.../main/README.md` 成功 |
| `raw.githubusercontent.com/YPares/rigup.nix/main/README.md` | 空 | 未解决；描述来自搜索结果摘要，非逐字 README |
| `skills.sh/search?q=nixos` | JS 渲染，无结果 | 退到首页榜单 |
| `github.com/ranicharradi/arch-maintenance-skill` | **404** | 仓库不存在；来自聚合站 `mcpmarket.com` 的虚假列表 |
| `api.github.com/repos/<...>`（第四轮） | **`API rate limit exceeded … remaining 0/60`** | 改用 `raw.githubusercontent.com` 读 README（成功）；star 数留空并标注 |
| `github.com/github/awesome-copilot/tree/main/agents` | WebFetch 返回空（GitHub HTML 页通病） | **改用 `raw.githubusercontent.com` 逐路径探测 HTTP 状态码（200/404）** —— 高效且确定，是判断"技能是否存在"的最佳方法 |
| `mdapi.fedoraproject.org/f44/pkg/dnf-automatic` | `400 Bad Request` | mdapi **不索引 noarch 子包**；改用 `packages.fedoraproject.org/search?query=` 确认存在 |
| Reddit 匿名后端 | 无点赞数/评论嵌套 | 只拿正文与评论内容；要互动数需注册 Reddit "script" 应用 |
| **抽样探测 GitHub 仓库的路径**（v5） | 只探 `skills/` + `agents/` 就下结论 | ⚠️ **漏掉整类资源**（`awesome-copilot` 实际有 4 类）。**拉全量目录树**：`curl "https://api.github.com/repos/<o>/<r>/git/trees/main?recursive=1"` 再 grep |
| **`org:redhat` 搜不到任何 MCP**（v5） | 据此判定"RHEL 无官方方案" | ❌ **错误结论**。实际在 `rhel-lightspeed` 组织下（317★）。**搜厂商方案要试多个组织名**，或用 `q=mcp+server+<关键词>` 全站搜 |
