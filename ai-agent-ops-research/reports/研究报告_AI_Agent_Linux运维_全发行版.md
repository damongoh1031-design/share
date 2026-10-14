# 用 AI Agent 管理 Linux 运维：全发行版深度研究报告

**版本** v1.1 · **成稿日期** 2026-10-12 · **覆盖发行版** NixOS / Arch / Fedora / Debian / Ubuntu / RHEL 系 / openSUSE
**方法** 本机源码与官方文档逐项审计（一手） + GitHub API / PyPI / Arch 官方包库 API / Fedora mdapi / Debian sources API 核验 + Reddit 原帖实抓（Atom 后端） + 技能市场实测
**证据分级** **A** = 本机源码或官方仓库 API 直读可复现 · **B** = 项目 README / 官方文档原文 · **C** = 项目自述未独立复现 · **D** = 本报告推断

> 本报告整合了四轮调研（通用框架 → NixOS → Arch → Fedora/Debian/Ubuntu），并在整合过程中**对前序报告的每一处事实重新核验**，共发现并修正 **10 处错误**（见附录 D 勘误表），其中 **3 处是覆盖性错误**——整合阶段补上了 **Red Hat 官方 `linux-mcp-server`（317★）** 与 **RHEL 系 / openSUSE 生态**（见第 7 章 §7.1 与附录 E）。所有数字均可回溯到命令输出或 API 响应。

---

## 摘要

**核心结论：你不需要为每个发行版找一套 AI 运维方案。你需要的是"一个默认禁写的通用执行层 + 每个发行版的知识与安全闸门"。**

Hermes Agent 官方目录里有 **65 个已审 MCP、152 个可选技能、349 个插件**，但**没有任何一个针对 NixOS / Arch / Fedora / Debian / Ubuntu / Ansible / SSH 的运维件**——它的官方 MCP 是 SaaS 取向的。运维这条线必须自己接。

好消息是社区已经把该建的东西建出来了，而且形成了清晰的**分层**：

| 层 | 作用 | 代表 |
|---|---|---|
| **执行层**（通用） | 让 agent 能安全地操作系统 | `rhel-lightspeed/linux-mcp-server`（**Red Hat 官方**、317★、固定只读工具集 + SSH 多机 + LLM 闸门）· `openSUSE/systemd-mcp`（systemd C API 直连、polkit 授权、**默认禁写**） |
| **知识层**（分发行版） | 让 agent 不编造包名/选项名 | NixOS → `mcp-nixos`；Arch → `arch-wiki-mcp` + 官方 `arch-wiki-lite`；Debian → `debvulns` |
| **审计层**（分发行版） | 让 agent 装的东西可审 | Arch → AUR 供应链审计（`herraiz-org/ai-skills`）；Fedora → `redwrench` 策略引擎 |
| **沙箱层**（NixOS 最活跃） | 别给 agent 真系统 | `jailed-agents`、`nix-sandbox-mcp`、一次性 NixOS VM |
| **知识库** | 沉淀本机经验 | Hermes 原生 `llm-wiki`（文件优先，**不需要 MCP**） |

**三条反直觉的关键结论：**

1. **最好的运维 MCP 不是发行版专属的，而且是厂商自己做的。** 两个厂商官方项目各自解决一半问题：**Red Hat 的 `rhel-lightspeed/linux-mcp-server`（317★，Apache-2.0）** 提供固定只读工具集 + SSH 多机 + 日志白名单，**openSUSE 的 `systemd-mcp`（10★，MIT）** 提供 systemd C API 直连 + polkit 授权。两者都覆盖 Fedora/Debian/Ubuntu——因为它们都跑 systemd。发行版差异只在两处：包管理器（`dnf`/`apt`）与强制访问控制（Fedora = **SELinux**；Debian/Ubuntu = **AppArmor**）。
2. **Arch 的知识库不需要 MCP。** `arch-wiki-lite` 一个官方包给出离线全文 Arch Wiki，体积只有 HTML 版 1/9。上 MCP 联网查 Wiki 是把确定性换成不确定性。
3. **最大的风险不是"agent 能力不足"，是"权限过大 + 供应链投毒"。** 2026 年 r/linuxadmin 记录了一整条事故链（GuardFall、CVE-2026-59822、CVE-2026-42271），共同失败模式是"**鉴权逻辑信任重建出来的路径、后缀匹配或回退对象**"。

**最小可行栈（约 40 分钟）：**

```bash
# 1) 通用执行层：默认只读，要写必须显式提权
#    A. Red Hat 官方：固定只读工具集 + SSH 多机（推荐先装这个）
uv tool install linux-mcp-server
export LINUX_MCP_ALLOWED_LOG_PATHS=/var/log/messages,/var/log/secure   # 不设 = 日志工具读不到任何文件

#    B. openSUSE 官方：需要 systemd 深度控制时再叠（默认 --allow-write=false）
git clone https://github.com/openSUSE/systemd-mcp && cd systemd-mcp && make build && sudo make install

# 2) 知识层（按发行版选一个）
#    NixOS:  uvx mcp-nixos
#    Arch:   pacman -S arch-wiki-lite informant   +  pipx install arch-wiki-mcp
#    Debian: pip install debvulns
#    Fedora: sudo dnf install ./redwrench-*.rpm
#    RHEL:   linux-mcp-server（同上）+ 可选 rhel-lightspeed/okp-mcp（Red Hat 离线知识门户）

# 3) 知识库：文件优先，零安装
export WIKI_PATH=~/ops-kb && mkdir -p $WIKI_PATH && git -C $WIKI_PATH init
```

---

## 第 1 章 问题定义与方法论

### 1.1 待答的四个问题

本调研的原始问题：

1. 用 agent 管 Linux 运维，需要什么 **agent profile / agent.md、MCP、skills**？
2. 如何建立**知识库**作为参考？用什么方案（MCP 还是软件）？
3. 社区（Reddit）有什么好提议？GitHub 上有什么软件方案？
4. 针对**具体发行版**（NixOS / Arch / Fedora / Debian / Ubuntu）的实践是什么？

### 1.2 方法

| 手段 | 用途 | 可复现性 |
|---|---|---|
| 本机 Hermes 仓库源码与文档审计 | 框架机制、配置键名、常量取值 | **A**（`grep`/`sed` 可复现） |
| `api.github.com` + `raw.githubusercontent.com` | 仓库元数据、README 原文、文件存在性 | **A** |
| PyPI / npm registry JSON API | 包名与版本核验 | **A** |
| `archlinux.org/packages/search/json/` | Arch 官方仓库包存在性 | **A** |
| `mdapi.fedoraproject.org` + `packages.fedoraproject.org` | Fedora 包存在性 | **A** |
| `sources.debian.org/api/` | Debian 包版本与 suite | **A** |
| Hermes 自带 `reddit-reading` 技能（`scripts/reddit.py`） | Reddit 原帖正文与评论 | **A**（匿名 Atom 后端） |
| `clawhub.ai` / `skills.sh` 页面 | 技能市场覆盖与安装量 | **B**（平台自报） |

### 1.3 一条重要方法教训（跨四轮验证）

**判断"某个技能/仓库/文件是否存在"，最可靠的方法是逐路径探测 HTTP 状态码：**

```bash
curl -sL -o /dev/null -w "%{http_code}\n" \
  "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>"
```

这比用网页抓取工具读取 GitHub HTML 页可靠得多（HTML 页常返回空内容或导航壳），也比依赖搜索引擎结果可靠得多（**聚合站点会列出不存在的仓库**，本轮已实证：`mcpmarket.com` 把 `ranicharradi/arch-maintenance-skill` 列为真实技能，实际返回 **404**）。

---

## 第 2 章 Hermes Agent 框架机制（权威事实层）

> 本章所有内容来自本机源码与官方文档直读，**A 级**。

### 2.1 本机现状体检（实测，2026-10-12）

| 项 | 实测结果 | 判断 |
|---|---|---|
| **HERMES_HOME** | `C:\Users\Admin\AppData\Local\hermes`（环境变量 `HERMES_HOME`） | 注意：**不是** `~/.hermes` |
| 仓库 commit | `4e7403130ee278bd99c450fcd9f73c6b32135c95`，日期 **2026-09-29** | 含 CVE-2026-84289 修复 |
| 配置文件 | `$HERMES_HOME/config.yaml`（123,576 字节，`_config_version: 49`） | — |
| 已配置 MCP | `mcp_servers` 段**全部注释掉** → **0 个** | ✗ 完全空白 |
| `command_allowlist` | **不存在**（无"永久允许"记录） | △ 空 |
| `approvals` 段 | **不存在** → 全部走默认值（`mode: smart`） | △ 默认 |
| `security.tirith_*` | **全部注释掉** → 预执行扫描关闭 | △ 默认关 |
| 记忆上限 | `memory_char_limit` / `user_char_limit` **不在 config.yaml**，是**代码默认值** `2200` / `1375` | 见 §2.5 |
| 已装技能 | **58** 个（`find skills -name SKILL.md \| wc -l`） | △ 无运维类 |
| 可选技能池 | **152** 个 | ✓ |
| 官方 MCP 目录 | **65** 个 | ✓ 但无运维件 |
| 插件目录 | **349** 个 yaml | ✓ |
| `SOUL.md` | 存在（667 字节），但是**默认人格模板**，无任何运维规则 | △ 需追加 |
| `.env` 搜索 key | **0** 个（无 EXA/TAVILY/FIRECRAWL/PERPLEXITY/BRAVE/SERP） | △ 走 keyless 轮转 |
| OpenClaw | `~/.openclaw/workspace/` 有全套模板，但 `IDENTITY.md` / `USER.md` 为空，**未初始化** | △ |

**关键判断**：官方 65 个 MCP 里与运维相邻的只有 `datadog`、`grafana`、`semgrep`、`cloudflare`、`gitlab`、`betterstack`、`globalping`、`buildkite`、`circleci`、`aws-knowledge`。**全库 `grep -ril nixos\|arch\|ansible\|systemd\|pacman\|dnf\|apt` 在技能目录下命中 0 条运维技能。**

### 2.2 五个 `.md` 各管什么（官方权威表）

来源：`website/docs/user-guide/which-file-does-what.md`

| 文件 | 装什么 | 谁写 | 何时进上下文 | 位置 |
|---|---|---|---|---|
| `SOUL.md` | 人格、语气、沟通风格、禁止事项 | **你** | 系统提示 **slot #1**，会话开始 | `$HERMES_HOME/SOUL.md` |
| `USER.md` | 用户画像 | **Agent**（通过 `memory` 工具） | 系统提示，会话开始的**冻结快照** | `$HERMES_HOME/memories/` |
| `MEMORY.md` | Agent 自己的笔记 | **Agent** | 同上 | `$HERMES_HOME/memories/` |
| `AGENTS.md` | 项目指令、约定、架构、命令、端口、路径 | **你** | 会话启动时从工作目录载入，进子目录时渐进发现 | 项目工作目录 |
| `.hermes.md` / `HERMES.md` | 同 AGENTS.md，Hermes 专属且优先级最高 | **你** | 同上 | 项目，向上找到 git root |

**三个决定"规则该写哪儿"的机制：**

1. 一个会话**只载入一个**项目上下文文件，优先级 `.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`，**首个命中即止**。`SOUL.md` 独立加载，不在这条链上。
2. **记忆是冻结快照**：会话中途让 agent 存了东西，磁盘立刻写入，但系统提示要**下一个会话**才更新。改 `SOUL.md` / `AGENTS.md` 同样必须重启会话。
3. **profile 不是沙箱**。`hermes profile create coder` 只给它独立的 `HERMES_HOME`（自己的 config/.env/SOUL/memories/skills/cron/state.db），在 `local` 终端后端下，它对文件系统的访问权限和你的用户账号**完全一样**。

**运维场景的正确分工**：跨项目的安全底线写 `SOUL.md`；某台机器/某个仓库的具体操作规则写 `AGENTS.md`。

### 2.3 审批与安全机制（实测的完整清单）

#### 2.3.1 危险命令审批（`approvals`）

```yaml
approvals:
  mode: smart                     # smart | manual | off
  timeout: 300                    # 等待审批回复的秒数
  cron_mode: deny                 # deny | approve —— cron 无头会话遇到危险命令时
  single_query_mode: deny         # deny | approve —— hermes chat -q 单轮会话
  unattended_mode: deny           # deny | approve —— webhook / api_server 等无人在场时
  mcp_reload_confirm: true        # /reload-mcp 是否先确认（重建会失效 prompt 缓存）
  destructive_slash_confirm: true # /clear /new /reset /undo 是否先确认
  deny:                           # 用户自定义硬拒绝（见下）
    - "git push --force*"
```

| mode | 行为 |
|---|---|
| **`smart`（默认）** | 用辅助 LLM 评估风险。低危命令**仅本次**自动放行；真正危险的自动拒绝；不确定的升级为人工提示 |
| `manual` | 危险命令一律人工提示 |
| `off` | 关闭全部审批 = `--yolo`。⚠️ 仅在受信环境用 |

**四个 `*_mode` 默认全是 `deny`** —— 无人在场的场景（cron、`-q`、webhook）**默认拒绝**而不是等到超时。这是好的默认值。

#### 2.3.2 硬阻断清单（Hardline Blocklist）—— 实测位置与完整模式

> ⚠️ **勘误**：官方文档 `user-guide/security.md` 说该清单在 `tools/approval.py::UNRECOVERABLE_BLOCKLIST`。**本机实测该常量不存在**。真实位置是 **`tools/approval_detection.py` 的 `HARDLINE_PATTERNS`**（第 59 行起），另有 `tools/approval_floors.py` 承担执行侧。文档引用已过期。

**性质**：这是 **yolo 之下的一层地板**。`approvals.mode: off`、`--yolo`、`/yolo`、cron `approve` 模式、用户点"always allow" **全部无法绕过**。**没有覆盖开关。**

**完整 12 条模式（本机源码直读）**：

| 模式 | 说明 |
|---|---|
| `rm -rf /` 及各种路径折叠变体（`//`、`/.`、`/./`、`/../..`、尾随 glob、`rm -rf / *`） | 递归删除根文件系统 |
| `rm -rf` + `/home` `/root` `/etc` `/usr` `/var` `/bin` `/sbin` `/boot` `/lib`（含 `/*`） | 递归删除系统目录 |
| `rm -rf ~` / `rm -rf $HOME`（含 `/*`） | 递归删除家目录 |
| `mkfs` / `mkfs.<ext>` | 格式化文件系统 |
| `dd ... of=/dev/(sd\|nvme\|hd\|mmcblk\|vd\|xvd)*` | dd 写裸块设备 |
| `> /dev/(sd\|nvme\|hd\|mmcblk\|vd\|xvd)*` | 重定向到裸块设备 |
| `:(){ :\|:& };:` | fork bomb |
| `kill -1` | 杀掉所有进程 |
| `shutdown` / `reboot` / `halt` / `poweroff` | 系统关机/重启 |
| `init 0` / `init 6` | 同上 |
| **`systemctl poweroff` / `reboot` / `halt` / `kexec`** | 同上 |
| `telinit 0` / `telinit 6` | 同上 |

**设计细节（值得学）**：
- 模式用 `_CMDPOS` 锚定到**命令位置**（支持消费 `sudo`/`env`/`exec`/`nohup`/`setsid`/`time` 包装器），所以 `git commit -m "never dd of=/dev/sda"` 这类**引号内的数据不会误触发**。
- `>` 重定向与 fork bomb 无命令名可锚定 → 用 **quote-masked 变体**匹配，但 `sh -c` / `bash -c` / `eval` 的载荷仍按原文扫描（**引号不是绕过手段**）。
- 清单**故意保持很小**：只放**无恢复路径**的操作。`git reset --hard`、`chmod -R 777`、`curl|sh` 属于**可恢复**，留在 `DANGEROUS_PATTERNS`（会提示但不硬拦）。
- 适用范围：**仅对能损伤宿主的环境生效**（`local`、`ssh`、container-host cron）；**容器化后端本来就绕过了危险命令层**。

> ⭐ **与 `systemd-mcp` 的交叉印证**：即使你在 `systemd-mcp` 上开了 `--allow-write`，**`systemctl poweroff` / `reboot` 仍会被 Hermes 的硬阻断拦下**。两层防线独立生效，这是"纵深防御"的具体样子。

#### 2.3.3 用户自定义硬拒绝（`approvals.deny`）

硬阻断清单是**代码内置、固定**的；`approvals.deny` 是它的**用户可编辑对应物**：

- fnmatch glob（`*` `?` `[...]`），**大小写不敏感**，匹配**整条命令文本**与**各个可执行命令候选**
- 匹配在**归一化/去混淆**后的命令变体上运行 → `git pu""sh --force` 这类引号技巧**绕不过**
- 可执行候选**同时保留字面路径与 basename**：`sudo *` 覆盖 `/usr/bin/sudo -n id` 与 `./sudo -n id`；而 `/usr/bin/sudo *` **不会**变成"所有叫 sudo 的二进制"的规则
- 引号感知解析能穿透 `;` `&&` `||` 管道、分组、命令替换、`if/then/else/do`；支持 `sudo`/`env`/`command`/`exec`/`nohup`/`setsid`/`time`/`nice`/`timeout`/`stdbuf`/`ionice`/`chrt`/`taskset`/`chroot` 等启动器；`sh -c` 载荷**递归检查**
- **在任何其他层之前生效** —— 在 `--yolo`、`/yolo`、`mode: off` 被考虑之前

运维场景建议（"yolo with exceptions"）：

```yaml
approvals:
  deny:
    - "systemctl disable *"          # 别让 agent 关服务
    - "*nix-collect-garbage*"
    - "git push --force*"
    - "dd if=* of=/dev/*"
    - "rm -rf /*"
```

#### 2.3.4 Tirith 预执行扫描（默认关闭）

`config.yaml` 第 530-541 行，**全部注释掉**：

```yaml
# security:
#   tirith_enabled: true        # 启用 tirith 扫描
#   tirith_path: "tirith"
#   tirith_timeout: 5
#   tirith_fail_open: true      # tirith 不可用时是否放行命令
```

作用：执行前的命令安全扫描（识别同形异义 URL、管道执行 shell、终端注入、环境变量篡改）。**必须手动开。**

#### 2.3.5 其它实测到的安全默认值

| 位置 | 键 | 默认 | 含义 |
|---|---|---|---|
| `terminal` | `docker_mount_cwd_to_workspace` | `false` | **安全默认关闭**：是否把启动 cwd 挂进 Docker `/workspace` |

### 2.4 MCP 配置模型

#### 2.4.1 根结构与 server 键

```yaml
mcp_servers:
  <name>:
    command: "uvx"              # stdio 传输
    args: ["mcp-nixos"]
    env: { KEY: "${env:KEY}" }  # 从当前 profile 的 .env 解析
    url: https://...            # 或远程传输
    headers: { ... }
    trust: untrusted            # 见下
    lazy: true                  # 启动时只注册 schema，首次调用才起进程
    timeout: 30
    idle_timeout_seconds: 300   # 内存重的 stdio server（浏览器类）自动回收
    max_lifetime_seconds: 3600
    tools:
      include: ["nix", "nix_versions"]   # 白名单，支持 fnmatch 通配
      exclude: ["*_dangerous_*"]
```

#### 2.4.2 `trust` 语义（关键安全机制）

- `trust: untrusted` 的效果：**每一个非只读工具调用都要经过审批界面**才执行。
- `readOnlyHint` 由 **server 自己声明**——撒谎的 server 最多只能骗过审批，**拿不到额外权限**。
- **无法识别的值按 `untrusted` 处理（fail-closed）**。

#### 2.4.3 工具过滤与变量解析

- `tools.include` 是白名单，支持 fnmatch（`*_radar_*`）。**`include` 与 `exclude` 同时存在时 `include` 优先。**
- `${VAR}` 与 `${env:VAR}` 从当前 profile 的 `.env` 解析。**远程 server 的 `url`/`headers` 里若变量未设，连接直接失败**而不是发字面量（防 401 的设计）。
- `lazy: true` 需要先有一次真实连接来填 schema 缓存。

#### 2.4.4 MCP 的上下文税与溢出阈值（实测数字）

**溢出阈值**（`config.yaml` 第 780-789 行原文）：

> MCP tool results (tools named `mcp_*`) spill at a **tighter 50,000-char threshold** than the generic 100K default: MCP servers routinely return un-paginated 20-50K payloads that bloat context and slow every subsequent turn. Nothing is lost — the full result is on disk and readable with `read_file`.

```yaml
# tool_budget:
#   mcp_result_size_chars: 50000
```

**上下文成本对比**（来自 `nix-sandbox-mcp` README，C 级）：

| 方案 | 初始成本 | 代价 |
|---|---|---|
| 静态加载全部工具 | 约 **150 token × N 个工具** | 随工具数**线性增长** |
| 动态发现（list → schema → call） | 约 400 token 固定 | 每次调用多往返；LLM 要学发现协议 |
| SKILL.md 指南文档 | 激活时约 800 token | 指导丰富但重；需另维护文档 |
| **一个参数化工具** | **约 420 token 固定** | 不随环境数量增长 |

> 原文点名批评："**一个暴露 60 个工具的服务器，在你开口之前就能烧掉约 47k token。**" —— 这是"一个参数化工具"优于"每个环境一个工具"的量化依据。

### 2.5 记忆 vs 知识库（必须区分）

**内置持久记忆的上限是代码默认值，不在 config.yaml 里：**

| 项 | 值 | 来源（本机源码） |
|---|---|---|
| `memory_char_limit` | **2200** 字符（约 800 token @ 2.75 字符/token） | `hermes_cli/config_defaults.py:1321` |
| `user_char_limit` | **1375** 字符（约 500 token） | `hermes_cli/config_defaults.py:1322` |

同样出现在 `agent/agent_init.py:1343-1344`、`tools/memory_tool.py:56`、`tools/memory_tool_store.py:99`（均以 2200/1375 为默认参数）。

本机 `config.yaml` 的 `memory:` 段只有两个开关：

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
```

**官方立场**（`features/memory.md`）："对于需要每次运行都用到的事实，**skill 往往是比 memory 条目更好的归宿**——它只在相关时加载，且不占用那 2200 字符预算。"

**结论：内置记忆不是知识库，是偏好与约定的存储。** 运维知识（机器清单、踩坑记录、回滚步骤）必须外置成文件。详见第 8 章。

### 2.6 技能系统的两个实测细节

```yaml
skills:
  creation_nudge_interval: 15     # 每 N 次工具调用提醒 agent 考虑存 skill（0 = 关闭）
  # external_dirs:                # 外部技能目录：跨工具共享，无需拷贝进 ~/.hermes/skills/
  #   - ~/.agents/skills          # ⚠️ 外部目录是【只读】的；技能创建永远写入 ~/.hermes/skills/
  #   - /home/shared/team-skills  # 同名时本地技能优先
```

**`external_dirs` 是只读的** —— 这个设计意味着你可以把团队的共享运维技能挂进来（例如 `enihcam/aur-skills` 的克隆目录），但 agent 不会污染它。这与第三轮发现的"用 symlink 把技能链进 `~/.hermes/skills/`"是两条互补路径。

**技能 frontmatter 规范**（来源 `developer-guide/creating-skills.md`）：

```yaml
---
name: nixos-ops
description: 安全地对 NixOS 主机做配置变更、重建与回滚
version: 1.0.0
author: <你>
license: MIT
platforms: [linux]                 # 只在 Linux 加载；可选 macos / linux / windows
metadata:
  hermes:
    tags: [NixOS, DevOps, Rollback]
    category: devops
    requires_toolsets: [terminal]   # 条件激活：只有 terminal 工具集在时才显示
    config:
      - key: nixos.flake_path
        description: "flake 所在路径"
        default: "/etc/nixos"
        prompt: "NixOS flake 路径"
---
# 标题
## When to Use
## Procedure        # 编号步骤
## Pitfalls         # 已知失败模式
## Verification     # 怎么确认成功
```

安装：`hermes skills install official/<category>/<skill>`（官方池）或 `hermes skills install <owner>/<repo>/<skill>`（第三方，会先跑安全扫描）。

---

## 第 3 章 五发行版生态对比总表

### 3.1 生态形状：三种完全不同的模式

| 维度 | **NixOS** | **Arch** | **Fedora / Debian / Ubuntu** |
|---|---|---|---|
| 系统模型 | 声明式、可原子回滚 | 命令式、靠快照与降级 | 命令式、靠包管理器 + 快照 |
| 社区对 agent 的关注点 | **沙箱**（别给真系统） | **供应链审计**（别让 AUR 投毒） | **权限最小化**（别给 shell） |
| 最活跃的一层 | 沙箱层（7+ 个项目） | 审计层 | 策略引擎层 |
| 知识层 | 第三方 `mcp-nixos` | `arch-mcp` + `arch-wiki-mcp` + **官方离线 Wiki 包** | 官方仓库工具（`dnf`/`apt`）+ 漏洞扫描 MCP |
| 官方发行版背书 | 有官方 NixOS module | 无（但有 `arch-wiki-lite` 等基座包） | **有**：Red Hat 官方 `linux-mcp-server`（= 官方 MCP Server for RHEL）+ openSUSE 官方 `systemd-mcp` |
| 社区情绪 | 怀疑 + 工程化 | 怀疑 + **明显反 AI slop** | 怀疑（r/linuxadmin 记录事故链） |

### 3.2 逐项对比

| | **NixOS** | **Arch** | **Fedora** | **Debian** | **Ubuntu** |
|---|---|---|---|---|---|
| **最值得装的 MCP** | `mcp-nixos`（2 工具，约 1030 token） | `arch-mcp` / `arch-ops-server` + `arch-wiki-mcp` | `redwrench` + `fedora-agents` | `debvulns`（原 `debsecan-mcp`） | `ubuntu_mcp_server`（⚠️ 停更 16 个月） |
| **官方自动更新** | 声明式（`nixos-rebuild`） | `informant`（News hook） | `dnf-automatic` | `unattended-upgrades` | `unattended-upgrades` + **Pro/ESM/Livepatch** |
| **重启检测** | 重建即换 generation | — | **`dnf needs-restarting`**（在 `dnf5-plugins`） | `needrestart` | `needrestart` |
| **漏洞扫描** | — | `arch-audit`（官方仓库） | `dnf updateinfo` / Bodhi | `debsecan` + `debvulns` | `pro security-status` |
| **强制访问控制** | — | — | **SELinux** + `firewalld` | AppArmor | AppArmor（+ snap confinement） |
| **降级/回滚** | `--rollback` / generation（**系统能力**） | `downgrade`（AUR，910 票）/ `archward` | `dnf history undo` / `archward` | `apt` 缓存 / `downgrade` | 同 Debian |
| **官方离线知识包** | — | **`arch-wiki-lite`**（体积 1/9） | — | — | — |
| **ClawHub 技能** | **0 个**（搜 nixos 无结果） | 0 个（搜 arch 全是 architecture 噪音） | 单件最热（8.9k） | **最薄** | **最丰富**（10+ 件） |
| **awesome-copilot 专家** | ❌ | ✅ **3 类**（skill + agent + instructions） | ✅ **3 类** | ✅ **3 类** | ❌ |
| **独有坑** | `trusted-users` 提权坑 | 不可变系统；`.deb` 重打包 | `rpm-ostree` 失败；`.deb` 重打包 | 内核升级不重启 | Pro 是订阅；snap 双通道 |

### 3.3 一张图看懂选型

```
                      ┌──────────────────────────────────────┐
                      │   执行层（所有发行版通用，两家厂商官方）│
                      │   rhel-lightspeed/linux-mcp-server    │
                      │   固定只读工具集 + SSH 多机 + LLM 闸门│
                      │   ─────────────────────────────────   │
                      │   openSUSE/systemd-mcp                │
                      │   默认 --allow-write=false            │
                      │   polkit / OAuth2 双授权              │
                      └───────────────┬──────────────────────┘
                                      │
        ┌──────────────┬──────────────┼──────────────┬──────────────┐
        ▼              ▼              ▼              ▼              ▼
     NixOS          Arch          Fedora         Debian         Ubuntu
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │ 沙箱优先 │  │ 审计优先 │  │ 策略引擎 │  │ 漏洞扫描 │  │ Pro/ESM  │
  │ jailed-  │  │ herraiz- │  │ redwrench│  │ debvulns │  │ 订阅状态 │
  │ agents   │  │ org/ai-  │  │ 四档tier │  │ + EPSS   │  │ + snap   │
  │ 一次性VM │  │ skills   │  │          │  │          │  │          │
  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
        │              │              │              │              │
        └──────────────┴──────────────┼──────────────┴──────────────┘
                                      ▼
                      ┌──────────────────────────────────────┐
                      │   知识库（文件优先，不需要 MCP）      │
                      │   Hermes llm-wiki + git              │
                      │   Arch 额外：arch-wiki-lite 只读层   │
                      │   RHEL 额外：okp-mcp 离线知识门户    │
                      └──────────────────────────────────────┘
```

---

## 第 4 章 NixOS 生态

### 4.1 四层结构

NixOS 社区已形成**四层生态**，层次分明：

| 层 | 代表项目 |
|---|---|
| **知识层**（不编造选项） | `mcp-nixos`、`nix-mcp`、`nixai`（**已归档**） |
| **执行层**（真改系统） | `nix-agent`、`nix-infra`、`devenv`、`nh`、`nixos-anywhere`/`deploy-rs`/`colmena` |
| **沙箱层** ⭐（最活跃、最独特） | `jailed-agents`、`nix-sandbox-mcp`、`nix-bwrapper`、`agent-sandbox.nix`、landlock 方案、`ai-jail`、`nixpi` |
| **结构层**（用 Nix 组织 skill） | `rigup.nix`、`nixos-management-skill`、`knoopx/pi` |

### 4.2 知识层：`mcp-nixos`

| 项 | 值 |
|---|---|
| 仓库 | `utensils/mcp-nixos`（作者 u/brinkjames） |
| 覆盖 | 13 万+ 包、2.3 万+ 选项、Home Manager、nix-darwin、Nixvim、NVF、FlakeHub、Noogle、NixOS Wiki、nix.dev、版本历史、binary cache 状态、本地 flake inputs |
| **上下文成本** | **仅 2 个工具，约 1030 token**（作者明确以省上下文为设计目标） |
| 许可 | MIT |
| 关键优势 | **不需要装 Nix**（`uvx mcp-nixos` 即可）；已进 nixpkgs（`pkgs.mcp-nixos`） |

**它解决的问题**：小模型会编造 Nix 包名和选项名。搜索 `nvidia` 会返回**真实的** NixOS Wiki 条目和真实选项路径。

**作者自己承认的局限**（r/NixOS 原话）：*"我**完全同意**你对 MCP server 的看法……我试过的很多都是这样。有几个我经常用的确实很扎实，比如 PostgreSQL MCP，但**大多数我试过的就是很烂，或者无论怎样都不调用工具**。"*

### 4.3 沙箱层：NixOS 社区最独特的答案 ⭐

**r/NixOS 上关于 AI agent 的高质量项目，绝大多数是沙箱，不是"让 agent 管系统"。**

| 项目 | 机制 | 特点 |
|---|---|---|
| **`nix-sandbox-mcp`**（`SecBear/`） | jail.nix（bubblewrap + Linux namespaces，**不需要 root**） | **单个 `run` 工具 + `env` 参数，固定约 420 token**，与配置多少环境无关；默认**无网络**；项目目录**只读**挂载到 `/project`；支持会话持久化。规划中加 microvm.nix 后端做全内核隔离。MIT，仅 Linux |
| **`jailed-agents`**（`andersonjoseph/`） | Nix + jail.nix（bubblewrap） | 零信任沙箱。作者原话："开始玩 AI coding agent 后，我对给它 home 目录和 SSH key 完全访问权感到偏执" |
| **`nix-bwrapper`**（`xNaXDy/`） | NixOS 模块系统的模块化 bwrap 工具 | 用 module 系统管理 bubblewrap 配置 |
| **landlock 方案** | Nix + **landlock**（内核级） | 把密钥藏在 landlocked 工具里，"出不去，因为由 Linux 内核保护" |
| **`ai-jail`**（`himuxhehe/`） | 多平台沙箱 | 跨平台限制 AI 行为 |

**社区最认可的模式不是工具，是做法**——"给 agent 一台一次性 NixOS VM"（r/NixOS 用户 `u/First_Understanding2` 原话）：

> "我刚给 agent 们专门开了一整台 nixos VM。**它们维护它**，因为它们知道怎么写 nix 配置。这有点像 open claw，但整个 Linux 都带 AI 层。**我显然不接任何个人资源进去**，但它有个自己的操场能替我干活。我只是 vlan 到我的 iot 安全区，**不把我的东西托付给它**，但它还是能替我干开发活并把结果发给我。"

### 4.4 结构层与现成技能

| 项目 | 说明 |
|---|---|
| **`michalzubkowicz/nixos-management-skill`** ⭐ | **纯 Markdown skill**，从官方文档与最佳实践自动生成。9 个文件：`SKILL.md`（入口 + 决策表）、`configuration.md`、`vm-management.md`（rebuild/generations/rollback/deploy-rs/colmena）、`installation.md`（disko）、`image-building.md`、`impermanence.md`、`luks.md`（含 initrd 内 SSH/Tailscale 远程解锁）、`monitoring.md`、`anti-patterns.md`。带 `AGENTS.md` 跨 agent 入口 |
| **`YPares/rigup.nix`** | 用 Nix 模块系统组织 agent 的 skill/指令/工具。核心概念 **riglet**；自带**自文档化** riglet（`agent-rig-system`、`riglet-creator`、`nix-module-system`） |
| **Nix 作为 MCP 打包层的提议** | r/NixOS 用户 `u/sielicki`：*"nix flakes 真的非常适合 mcp……可以用 `flake.mcpConfigurations` 表示 MCP 服务器分组……**比在 npx 和 uvx 上盖东西好太多——可原子更新、可回滚**"* |

### 4.5 社区实证：三条最有价值的原话

**① 最正面的一手实践报告**（`u/qmic`，r/NixOS `1souuw7`）：
> "我用 Linux 从 1996 年开始。在我的一生中**管理过上千台服务器**——手工、脚本、Terraform、Ansible。最近我用 Claude Code 试了一下，终于生成了我梦寐以求的配置……**现在 AI agent 能为我生成整套配置，我只负责审查和测试再部署。责任当然还是我的，但它承担了最无聊的部分。**"

**② 最重要的一条警告**（`u/lily_34`）：
> "Claude 在处理 nixos 配置上极其有帮助……**然而它也会做很多可疑的事。就在今天，它把我的用户加进了 `nix.settings.trusted-users`（这允许无代价提权到 root）**，还有好几次试图用非标准的 hack 来解决问题。所以它极有帮助，但必须极度小心。"

**③ 技术含量最高的方法论建议**（`u/gersilex`）：
> "Nix 尤其是 NixOS modules 是**自描述**的。用 `nix eval` 和 options attrset，你基本上就拿到了每个可能选项的完整文档。**指示 LLM 只从那里获取信息、不要从别处。**让它搜索并读取它试图使用的任何选项的 description。如果对工作原理不确定，让它读那个选项的源码。"

**④ 模型能力判断**（`u/Kai_`）：
> "**LLM 在 2025 年 11 月左右随着 Opus 4.5 开始对 Nix 变得半像样。**现在大多数编码模型都经过大量 IT 训练、被鼓励在闭环里测试，再加上给它们 `nix eval` 访问权和来自 `nh -q --no-noms` 这类工具的**干净输出**的 harness——是的，它们编辑 nix 配置可能比我们大多数人还好。"

**本地模型实测（`1tzcit5`）**：

| 模型 | 结论 |
|---|---|
| `gemma4:26b-a4b-it-q4_K_M`（24GB 卡 + 128k 上下文） | ✅ "两个任务都处理了"；调优后约 80 tok/s |
| `Qwen3.6-27B` | ✅ "唯一能把我的 flake 转成 dendritic 的本地模型" |
| `Qwen3-coder:30b` | △ 不错但不及 gemma4 |
| **`Qwen3.5:4B-Q6`** | ❌ **"太蠢了没法用。它通常把文件搞坏，然后试图 git checkout"** |

---

## 第 5 章 Arch 生态

### 5.1 两个 Arch 专属 MCP（均已核验）

| | **`arch-mcp`** / **`arch-ops-server`** | **`arch-wiki-mcp`** |
|---|---|---|
| 仓库 | `nihalxkumar/arch-mcp` | `egarcia74/arch-wiki-mcp` |
| **安装名** | **`uvx arch-ops-server`**（⚠️ 仓库名 ≠ 包名；**npm 上无此包**） | `pipx install arch-wiki-mcp` |
| 版本 / Stars | **3.4.0** / **59★** | 2.1.0 / **1★** |
| 许可 | 双许可 **GPL-3.0-only OR MIT** | MIT |
| 创建 / 最后提交 | 2025-10-23 / **2026-03-10**（活跃） | 2026-01-10 / 2026-07-15 |
| 依赖 | Python ≥ 3.11 | **零依赖**；⚠️ 默认分支是 **`master`** 不是 `main` |
| 写操作 | **有 ⚠️** | 无（纯只读） |

**`arch-mcp` 的 9 类 URI Resources（只读，不占 tool 名额）**：

`archwiki://`（Markdown 化 Wiki 页）、`archrepo://`（官方仓库包详情）、`aur://*/info` · `aur://*/pkgbuild`（**带安全分析的 PKGBUILD 原文**）、`pacman://installed|orphans|explicit|groups|group/*|database/freshness|log/recent|log/failed`、`system://info|disk|services/failed|logs/boot`、`archnews://latest|critical|since-update`、`config://pacman|makepkg`、`mirrors://active|health`

**14 个 Tools**：

| 类别 | 工具 |
|---|---|
| 只读查询 | `search_archwiki`、`search_aur`、`get_official_package_info`、`check_updates_dry_run`、`check_database_freshness`、`fetch_news`、`audit_package_security`、`analyze_pkgbuild_safety`（**50+ 红旗**）、`analyze_package_metadata_risk`、`diagnose_system`、`query_package_history`、`verify_package_integrity`、`analyze_pacman_conf`、`analyze_makepkg_conf` |
| **写操作 ⚠️** | `install_package_secure`、`remove_packages`、`manage_orphans`、`manage_install_reason`、`optimize_mirrors` |

另有 4 个 Prompt：`troubleshoot_issue`、`audit_aur_package`、`analyze_dependencies`、`safe_system_update`。

**`arch-wiki-mcp` 的三档证据分层（最该抄的通用模式）**：

| 档位 | 工具 | revid | SHA-256 hash | 语义 |
|---|---|---|---|---|
| **证据** | `page` `section` `commands` `warnings` | ✅ | ✅ | 可引用、可复算 |
| 半证据 | `links` | ✅ | ❌ | 是目标，不是引文 |
| 指针 | `search` `sections` | ❌ | ❌ | **拒绝伪装成证据** |

原话："This is not 'AI that knows Linux.' **This is Linux that won't let AI lie about it.**"
"**There is deliberately no tool that infers commands from prose.**"
设计细节：`commands` 返回的 `content` 里 `<esp>` **故意保留尖括号** —— "so a thoughtless paste fails at the shell instead of acting on the wrong path"。

### 5.2 官方仓库自带的 Arch 运维基座 ⭐

**Arch 的知识库与更新安全闸门不需要第三方——官方 `extra` 仓库直接提供**（经 `archlinux.org/packages/search/json/` 核验）：

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

### 5.3 三个真实 Arch 专属 Agent Skill 仓库

| 仓库 | Stars / 许可 | 最后提交 | 定位 |
|---|---|---|---|
| **`herraiz-org/ai-skills`** ⭐ | 0 / **Apache-2.0** | 2026-09-05 | **质量最高**：`update-arch-system` + `install-aur-package`，**带 CI + pytest** |
| `enihcam/aur-skills` | 5 / MIT | 2026-10-09 | AUR 打包开发，10 个模块化技能，**有中文 README** |
| `IPauloGermano/arch-agent-skill` | 0 / MIT | 2026-09-07 | 桌面环境向（Hyprland/Sway/KDE/GNOME/Niri/Waybar/主题） |

#### `herraiz-org/ai-skills` 的六道闸门（整轮最有价值的流程资产）

1. **Preconditions** — `test -r /etc/arch-release`；硬规则：**永不 `pacman -Sy`、永不部分升级、永不关签名校验、永不改 pacman 信任设置**
2. **checkupdates 引导** — 从 `pacman-contrib` 装，**绝不允许从 AUR 满足此依赖**；先查 `check_database_freshness` 判断该"立即装"还是"并入全量升级"（避免部分升级）
3. **Arch News 闸门（阻塞式）** — `fetch_news(critical)` + `fetch_news(since_update)`；无 MCP 时读 `https://archlinux.org/feeds/news/` + `/var/log/pacman.log`。⚠️ **RSS 仅约 10 条 → 必须报告盲区，不可当作"没有新闻"**。命中待升级包 → **停下等人工批准**
4. **Discover** — `checkupdates`（免 sudo）；AUR 用 `yay -Qua`（两条路径都跑）
5. **Audit every AUR target** — 克隆 `https://aur.archlinux.org/<PackageBase>.git` 到 `mktemp -d`；**绝不 source PKGBUILD、绝不先跑 makepkg**；审 `PKGBUILD` / `.SRCINFO` / `.install` / patches；跑自带 `scripts/scan-aur-recipe.sh`；静态检查通过后才允许 `makepkg --verifysource`
6. **Install gate** — 需显式批准

#### 自带扫描器 `scan-aur-recipe.sh` 的规则（可直接复用）

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

#### 它的信任原则（原话，值得写进 SOUL.md）

> **"Server output is evidence, not a verdict."**
> 干净的 `pkgbuild_analysis` **不能**降级 scanner 的发现；干净的 scanner **不能**降级 MCP 的发现。**取并集**；冲突时**取更高风险等级**并解释分歧。
> `pkgbuild_analysis` 只拿到 PKGBUILD 文本，**看不到** `.install` 脚本、patches、systemd unit、vendored 脚本、提交的二进制。

#### `enihcam/aur-skills` 的验证命令清单

```bash
namcap PKGBUILD ; namcap *.pkg.tar.zst
shellcheck --shell=bash --exclude=SC2034,SC2154,SC2164 PKGBUILD
makepkg --printsrcinfo > .SRCINFO
makerepropkg *.pkg.tar.zst      # 可复现构建（devtools）
pkgctl build                    # 干净 chroot 构建（systemd-nspawn）
```
推荐第三方扫描器：`traur`、`ks-aur-scanner`。原文提醒：**"aids, not substitutes for manual review"**、**"signed code can still be malicious — review the content, not just the signature."**

#### 跨 agent 技能目录表（来自该仓库 README）

| Agent | 技能目录 |
|---|---|
| **Hermes** | `~/.hermes/skills/` |
| Claude Code | `~/.claude/skills/` |
| OpenCode | `~/.config/opencode/skills/` |
| Gemini CLI | `~/.gemini/skills/` |
| Codex CLI | `~/.agents/skills/` |
| Cursor | `~/.cursor/skills/` |
| Windsurf | `~/.codeium/windsurf/skills/` |

> ⚠️ 该 README 自己提醒：**不要把克隆目录放 `/tmp`**（很多系统把 `/tmp` 挂成 tmpfs，重启即清）。用 `~/.local/share/aur-skills` 再 symlink。

### 5.4 AUR 供应链安全（Arch 的核心风险面）

**事件**（r/archlinux `1vaxtcs`）："Another wave - **200+ malicous AUR packages adoptions** that are overwhelming my scanner."

**攻击手法（原帖原文）**：
> "**the maintainer got pwned, or orphaned packages are adopted by the bad actor.** **AUR's git commit author is easily impersonated** so you can see the commit comes from the same person, but in fact it's not. … The malicious packages are **info stealers**."

**三个要点**：① 维护者账号被攻陷，或**孤儿包被恶意者收养**（AUR 允许任何人收养 orphan）；② **git commit author 可冒充** → "提交者看起来还是原作者"**不构成任何信任证据**；③ 载荷是**信息窃取器**。

**已知受害者（部分）**：`1panel`、`1panel-git`、`archutil`、`cinnamon-no-nemo`、`icloudpd`、`stirling-pdf-desktop-bin`、`windscribe-cli-v2-bin`、`pandoc-eisvogel-template`、`python-chatterbot`、`instawow-bin`、`pylnker-git`、`wiki-go`、`gitarbor-bin`、`boringssl-git`。dropper 哈希 `e73a35b3e75e94746428d1a207703d6335933deadee7d1d9c9d0328df7b9df77`。

**检测手段**：

| 手段 | 用法 |
|---|---|
| aurwatch.org API | `curl -fsS "https://aurwatch.org/api/v1/check?pkg=$pkg" \| jq -r '.status'` → `clean`/`low`/`medium`/`high` |
| 批量自查 | `pacman -Qqm \| xargs -P16 -I{} bash -c 'check_pkg "$@"' _ {}`（`-Qqm` = 仅外来/AUR 包） |
| 恶意清单 | `curl 'https://aur-audit.wtako.net/packages?filter=red&limit=200'` |
| 正确上报渠道 | **`aur-general@lists.archlinux.org`**（Reddit 不是上报渠道，但作为公众预警合理） |

> ⚠️ **二次信任风险**：`aurwatch.org` / `aur-audit.wtako.net` 都是**第三方个人服务**。让一个第三方服务告诉你"哪些包是恶意的"本身就是一个新的信任依赖。

**元教训**：该原帖本身是 AI 生成的（格式混乱、含 emoji、出现未来日期 `20260725`），评论区**大量火力集中在这一点**而非恶意包本身：

> **u/LeeHide**："Please just say when you used AI to do all of this, it's very tiring to read through only to realize you have no idea and neither does the AI. … **You're diluting the signal, making it less likely for real issues to be taken seriously.**"
> **u/KaptainSaki**："Wouldn't mind if they banned using AI on this sub"

**结论**：报安全事件要写**简洁事实 + 链接 + 包清单**，直发 `aur-general@lists.archlinux.org`。

### 5.5 Arch 社区规范：Wiki 优先，AI 其次

r/archlinux `1orwi2b` 原帖作者 `u/MysticFoxPaws` 的做法：

> "I still have **strict rules for Claude Code that it should retrieve references specifically via wiki.archlinux.org**, but also document carefully and clearly in **Obsidian**."

即：**硬性要求 agent 从 wiki.archlinux.org 取引用 + 用 Obsidian 沉淀**——正是 `arch-wiki-mcp` 想结构化的那件事。

| 立场 | 代表原话 |
|---|---|
| 可以用，但必须回查 Wiki | **u/_sLLiK**："if you want to remove the chance of hallucinations, **start with Arch's wiki first. It really is that good.**" |
| 幻觉会把人带进坑 | **u/Sea-Promotion8205**："They can throw a lot of red herrings … and **their information isn't always actually up to date**." |
| 会制造"照着 AI 装崩"的求助潮 | **u/aldyr**："many Linux subreddits are full of pleading for help with their Linux install, **that isn't working after they followed some AI generated instructions**." |
| 给日志/截图效果更好 | **u/ExplanationMobile399**："**share terminal outputs and screenshots** with it … The more data it has with a current subject, the better it really does get." |
| 非平凡配置必须回查 | **u/archover**："for Arch config, I am very careful, **usually confirming it in the wiki for non trivial stuff**." |

---

## 第 6 章 Fedora / Debian / Ubuntu 生态

### 6.1 通用基座：`openSUSE/systemd-mcp` ⭐（本轮的答案）

**这是四轮调研里唯一由发行版厂商官方组织维护、且安全模型完整到可以照抄的 Linux 运维 MCP。**

| 项 | 值 |
|---|---|
| 仓库 / 维护方 | `github.com/openSUSE/systemd-mcp` / **openSUSE 官方组织** |
| 许可 / 语言 / 版本 | **MIT** / Go / **0.3.5**（2026-09-24） |
| Stars | 10 |
| **关键实现** | **直接连 systemd 的 C API，不需要 `systemctl`** |
| 安装 | `make build && sudo make install` |

`sudo make install` 会装：`/usr/bin/systemd-mcp`、`/usr/sbin/gatekeeper`、`gatekeeper.service` + `gatekeeper.socket` 两个 unit、以及 **gatekeeper 的 polkit policy**。

**6 个工具**：

| 工具 | 作用 |
|---|---|
| `list_units` | 列出 unit，可按状态（`running`/`failed`）或模式过滤；`mode='files'` 列出所有已安装 unit 文件 |
| `change_unit_state` | 改 unit 状态（start/stop/restart/reload/enable/disable） |
| `check_restart_reload` | 检查 restart/reload 状态（仅在 job 超时后可用） |
| `list_log` | 取指定 service/unit 的最近日志 |
| `get_file` | 读系统文件（内容 + 元数据，支持分页） |
| `get_man_page` | 取 man page（可按 section/chapter 过滤 + 分页） |

**安全模型**：

| 传输方式 | 授权机制 |
|---|---|
| **stdio（默认）** | **polkit**。unit 操作触发 `org.freedesktop.systemd1.manage-units` 请求。**读操作永远放行**（调用者就是运行 server 的本人）；**只有写操作**触发 polkit |
| **HTTP** | **OAuth2**，audience `systemd-mcp-server`，scope `mcp:read` / `mcp:write` |

**日志访问的三级降级**：

1. 以 root 运行、或在 `/var/log/journal` 同组 → 直接读全部 journal
2. 否则连 `gatekeeper` 守护进程（`/run/gatekeeper/gatekeeper.socket`）→ 触发 polkit `com.suse.gatekeeper.readlog`
3. 若 gatekeeper 不可用 → 只读当前用户能读的 journal（如 `user-<uid>.journal`），**并在输出里明确提示访问被缩减**

**默认安全的 flag**：

| flag | 默认 | 说明 |
|---|---|---|
| `--allow-write` / `-w` | **false** | **默认不允许写 systemd**。要写必须显式打开 |
| `--allow-read` / `-r` | false | 授权读 |
| `--enabled-tools` | all | 逗号分隔的工具白名单 |
| `--noauth` | — | 关闭鉴权。**必须把值写成字面量 `ThisIsInsecure`** —— 故意制造摩擦，防止误用 |
| `--timeout` | 5 | polkit 认证超时（秒） |
| `--toon` | false | 输出改用 token 优化的 object notation |
| `--log-json` | false | 机器可读日志 |

> ⭐ **与 Hermes 硬阻断的交叉印证**：即使开了 `--allow-write`，`systemctl poweroff` / `reboot` / `halt` / `kexec` 仍会被 Hermes 的 `HARDLINE_PATTERNS` 拦下。**两层防线独立生效。**

### 6.2 Fedora

#### `simonives/redwrench` —— 策略引擎先于执行 ⭐

| 项 | 值 |
|---|---|
| 语言 / 许可 | **Rust** / **MIT OR Apache-2.0** |
| 形态 | `.rpm` 发布（Fedora 专用）+ tarball；有 CI + release |
| 状态 | 作者明示**业余项目**；**尚未进 COPR 或 Fedora 官方仓库** |

**作者动机（原话）**：
> "I keep a few old machines at home running Fedora … I wanted an AI coding agent to look after them for me … **However I didn't want to hand the agents a shell on these machines.**"

**核心机制**：
- **每一个 agent 命令先过策略引擎，再决定能不能跑**（"decides what they may run **before it runs anything at all**"）
- **每次调用都写 systemd journal —— 无论被允许还是被拒绝**
- **四档 tier**：`safe` / `standard` / `developer` / `unrestricted`，自定义规则可叠加，**不用改一行代码**
- `developer` tier 必须指定 `developer_user`（真实账户名），**没设 server 拒绝启动**；该 tier 下 `bash`/`python3`/`gcc`/`npm`/`cargo` 以该用户身份运行而**不是 root**
- `timeout_secs` 默认 30（慢镜像上跑 `dnf install` 要调大）
- 目标机**不需要装任何 agent 工具**；可以是标准版或**不可变版**（Silverblue/Kinoite），KDE/GNOME/Server 都行
- 用 Rust 的理由：会 spawn 任意进程 + 流式读输出 + 前置策略决策 → 需要内存与并发的编译期保证（引用 NSA 与白宫国家网络总监建议弃用 C/C++）

```toml
tier = "standard"                 # safe | standard | developer | unrestricted
developer_user = "your-username-here"   # 仅 tier="developer" 时必需
timeout_secs = 120
```

#### `amineutron/fedora-agents` —— 权限表驱动

| 项 | 值 |
|---|---|
| 包名 / 语言 / 许可 | npm **`fedora-agents-mcp`** / TypeScript / MIT；有 CI |
| 覆盖 | **KVM/libvirt 虚拟机** + **Borg/Timeshift 备份** |
| 安装 | `npx fedora-agents-mcp` |

**它的安全模型是四轮调研里文档化程度最高的**：

1. **每个工具声明两个 flag**：`requiresSudo`（**逐脚本** sudoers 条目，**绝不用全局 sudo**）与 `dangerous`（向 MCP 客户端声明破坏性 → 客户端必须做人确认）
2. ⭐ **server 启动时如果发现某个暴露的工具没有权限表条目，直接拒绝启动** —— fail-closed on unregistered tools
3. 权限表由 `src/config.ts` 生成（`npm run security:table`），**且在 CI 里校验**
4. **每个工具调用生成 correlation ID**，JSON 审计日志**在回复 agent 之前同步落盘**
5. **重试取决于工具性质**：只有幂等读（`vm_status`/`backup_status`/`backup_list`/`backup_verify`）重试 3 次（1s/2s/5s 退避）；**任何变更操作永不重试**；校验或权限错误立即中止
6. **退出码翻译成类型化 `ErrorCode`**

**完整权限表（19 个工具，来自 SECURITY.md）**：

| 工具 | sudo | 破坏性 | 作用 |
|---|---|---|---|
| `help` | 否 | 否 | 列出可用工具 |
| `vm_status` | 否 | 否 | 显示 VM 状态 |
| `vm_start` | 否 | 否 | 启动 VM |
| `vm_stop` | 否 | **是** | 停止 VM（可能丢失未保存数据） |
| `vm_exec` | 否 | **是** | 在 VM 内执行命令 |
| `vm_copy` | 否 | **是** | 与 VM 互拷文件 |
| `vm_snapshot` | 否 | **是** | 管理 VM 快照 |
| `vm_verify` | 否 | 否 | 校验 VM 是否为宿主机忠实副本 |
| `vm_destroy` | **是** | **是** | 永久删除 VM：**不可逆** |
| `vm_clone` | **是** | 否 | 克隆现有 VM |
| `vm_clone_system` | **是** | **是** | 克隆宿主机到 VM（耗时） |
| `vm_export` | 否 | 否 | 导出 VM 为可移植归档（含消毒） |
| `vm_import` | **是** | **是** | 从 `vm_export` 归档导入 VM |
| `backup_status` | **是** | 否 | 备份面板 |
| `backup_list` | **是** | 否 | 列出可用备份 |
| `backup_verify` | **是** | 否 | 校验备份完整性 |
| `backup_create` | **是** | 否 | 创建新备份 |
| `backup_restore` | **是** | **是** | 恢复备份（**破坏性**） |
| `backup_clean` | **是** | **是** | 按保留策略删除备份 |

**威胁模型表**：

| 威胁 | 缓解 |
|---|---|
| agent 请求销毁 VM | `vm_destroy` 标为 `dangerous` → 客户端人确认；每次调用 JSON 审计 |
| 在 VM 名或路径里注入 | 调用脚本前用 **Zod 严格模式校验** |
| 权限提升 | **逐脚本 sudoers**（root 副本 + 仅限这些路径的 `NOPASSWD`）；libvirt 走 `libvirt` 组（polkit）；**`virsh`/`virt-clone`/`qemu-img` 上没有任何 sudo 规则**（那等于 root） |
| 恢复了错误的备份 | `backup_restore` 标为 `dangerous`；标识符用正则校验 |

**它明确声明不做的事**：不从 agent 文本构造 shell 命令（参数经 Zod 校验后作为**独立参数**传入，**绝不插值**）；不写配置路径（`PATHS`）之外的任何位置；**不产生任何网络输出**。

#### Fedora 官方工具链（核验）

| 工具 | 状态 | 作用 |
|---|---|---|
| **`dnf-automatic`** | 存在于 Fedora 44 / 45 / Rawhide（`packages.fedoraproject.org` 命中） | 自动下载/安装更新 |
| `dnf5` | 5.4.6.0-1.fc44（mdapi 核验） | 命令行包管理器 |
| **`dnf5-plugins`** | 5.4.6.0-1.fc44 | 含 **`needs-restarting`**、`config-manager`、`copr`、`builddep` |
| **`rpm-ostree`** | 2026.3-2.fc44 | 混合镜像/包系统（Silverblue/Kinoite 基础） |
| `toolbox` | 0.3-4.fc44 | 交互式命令行环境容器 |

> ⚠️ **Fedora 的重启检测在 `dnf5-plugins` 里**，命令是 `dnf needs-restarting`（不是 `needrestart`）。这是与 Debian/Ubuntu 的一个实操差异。

#### Fedora 两个独有坑

**坑 1：不可变系统上 `dnf install` 直接失败**（r/Fedora `1szch0g` 原话）：
> "What I got was a system where my first instinct — **`dnf install tmux` — just does[n't work]**."

不可变版（Silverblue / Kinoite / Bazzite）需要 `rpm-ostree install` 分层，或者用 `toolbox`/`distrobox` 容器。**给 agent 的指令里必须区分"标准 Fedora"与"Fedora Atomic"。**

**坑 2：很多 AI 工具只发 `.deb`**（r/Fedora `1w190ij` 原话）：
> "Anthropic finally ships a Linux build, **but only as a .deb**. This repo takes that exact package and adapts it for Fedora as a proper RPM."

**结论：Ubuntu/Debian 优先拿到官方 AI 工具包，Fedora 常处于"自己重打包"的位置。**

### 6.3 Debian

#### `debvulns`（原 `debsecan-mcp`）—— 漏洞分析三件套

> ⚠️ **包名改过**：`debsecan-mcp` 停在 0.1.5，之后所有开发都在 **`debvulns`**。

| 接口 | 命令 | 用途 |
|---|---|---|
| **MCP server** | `debvulns-mcp` | 接入 Claude Desktop / VSCode / opencode |
| **独立 CLI** | `debvulns` | 扫描，输出 JSON / CSV |
| **Prometheus exporter** | `debvulns-exporter` | 暴露漏洞指标给 Grafana |

**能力**：扫全部已装包的已知漏洞；**CVE 研究含 EPSS 分数**（Exploit Prediction Scoring System，即"这个洞被实际利用的概率"）；**自动识别 Debian suite**（bookworm/trixie/sid）；缓存 `/var/cache/debvulns`（不可写退 `~/.cache/debvulns`），**>24h 自动刷新**；按严重度过滤（critical/high/medium/low/negligible）。

> EPSS 的价值：把"有 CVE"和"值得今晚就修"区分开。纯 CVE 列表会让 agent 淹没在噪音里。

#### Debian 官方工具链（`sources.debian.org` API 核验）

| 包 | 版本 | 作用 |
|---|---|---|
| **`unattended-upgrades`** | **2.13** | 自动安全更新。⚠️ **默认不自动重启，即使装了新内核也只提示** |
| **`needrestart`** | **3.11-1** | 库升级后检测哪些服务需要重启 |
| **`debsecan`** | **0.4.20.2** | 基于 Debian Security Tracker 的漏洞扫描 |
| `apt-listchanges` | 4.8+nmu3 | 升级前展示 changelog / NEWS |
| `debian-goodies` | 0.88.2 | 含 `checkrestart`、`dglob` 等 |

```bash
sudo apt install unattended-upgrades needrestart debsecan apt-listchanges apt-listbugs
sudo dpkg-reconfigure -plow unattended-upgrades
sudo needrestart -r l            # ⚠️ 关键：列出仍跑旧库的服务
sudo debsecan --suite bookworm --format detail
```

> ⚠️ **`unattended-upgrades` 默认不重启。** 装了新内核也只提示 → 一堆服务还在跑有洞的旧库。**"我开了自动更新所以安全了"是 Debian/Ubuntu 最常见的安全假象**，`needrestart` 就是用来戳破它的。

**Debian 技能市场：三个里最薄。** 只有 `cepheiden/openbot-esxi`（1.9k）、`nvidiaskills.sh/holoscan-install-debian`（1.8k，领域专用）、`xixu-meskills.sh/secure-linux-web-hosting`（13）。**没有 Debian 通用的巡检/加固技能** → 借用 Ubuntu 的（apt 生态兼容）。

### 6.4 Ubuntu

#### `pazuzu1w/ubuntu_mcp_server`（44★，但已停更）

| 项 | 值 |
|---|---|
| Stars | **44**（三个发行版专属 MCP 里最高） |
| 最后提交 | **2025-06-29** ⚠️ |
| 描述 | "an mcp server built to give claude config **limited control** over ubuntu os operations" |

⚠️ **能操作操作系统的、长期未维护的 MCP 是明确的风险项**，用前必须自己审源码。

#### Ubuntu Pro / ESM / Livepatch / Landscape（Ubuntu 独有的运维面）

**这是 Ubuntu 与 Fedora、Debian 最大的结构性差异**：把"安全更新"做成了**付费订阅 + 集中管理**。

| 组件 | 作用 |
|---|---|
| **Ubuntu Pro** | 订阅制。**ESM（扩展安全维护）** 把安全补丁覆盖期延长到**十年以上** |
| **Livepatch** | **不重启打高危/严重内核 CVE 补丁**。LTS 绑定 Pro 订阅后**自动启用** |
| **Landscape** | 集中式面板，可在**舰队规模**管理 Livepatch 配置与机器状态 |
| `pro` 客户端 | 本地管理订阅 / ESM / Livepatch 状态 |

```bash
pro status && pro security-status && sudo pro enable livepatch
```
> `pro security-status` 直接告诉你哪些包已过标准支持期、没有安全更新——**比读 CVE 列表更接近"我到底安不安全"**。

#### Ubuntu 技能市场：三个里最丰富 ⭐

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

### 6.5 `github/awesome-copilot` 发行版专家矩阵（A 级，HTTP 探测 + 目录树核验）

> **本节的结论在整合阶段被修正过。** 前序报告只探测了 `skills/` 与 `agents/` 两类路径，漏掉了 `instructions/` 与 `plugins/`，因此把 Arch 误记为"只有 agent"。完整核验方法见附录 B。

`awesome-copilot` 对每个发行版提供**最多 3 类**资源（`instructions/` = 常驻规则、`skills/` = 按需技能、`agents/` = 独立 agent 定义）：

| 发行版 | `instructions/<d>-linux.instructions.md` | `skills/<d>-linux-triage/SKILL.md` | `agents/<d>-linux-expert.agent.md` | 合计 |
|---|---|---|---|---|
| **Arch** | ✅ 1,355 B | ✅ 930 B | ✅ 2,009 B | **3** |
| **Fedora** | ✅ 1,269 B | ✅ 920 B | ✅ 1,898 B | **3** |
| **Debian** | ✅ 1,503 B | ✅ 961 B | ✅ 2,201 B | **3** |
| **CentOS** | ✅ 1,329 B | ✅ 959 B | ✅ 2,059 B | **3** |
| **Ubuntu** | ❌ 404 | ❌ 404 | ❌ 404 | **0** |
| **RHEL / Rocky / Alma** | ❌ 404 | ❌ 404 | ❌ 404 | **0** |
| **openSUSE / SUSE** | ❌ 404 | ❌ 404 | ❌ 404 | **0** |

**三个由此得出的判断：**

1. **Ubuntu 是五家里唯一的"零覆盖"**——尽管 ClawHub 上 Ubuntu 技能最多（10+ 件）。**技能市场的丰富度与官方专家库的覆盖度是反相关的**，两者不能互相替代。
2. **CentOS 有覆盖而 RHEL 没有**，说明这套库按"社区常见"而非"企业主流"选型。RHEL 用户不要指望它，走 Red Hat 官方 `linux-mcp-server` + `okp-mcp`。
3. **⚠️ 命名陷阱：`plugins/arch/` 不是 Arch Linux。** 它是"**architecture**（软件架构）与现代化工具包"，`plugin.json` 的 description 写的是 *"Architecture and modernization toolkit"*，装的是 `arch:doc-and-modernize` 技能。**用 `arch` 关键词搜索这个仓库，命中的大部分是软件架构，不是 Arch Linux。**

**`arch-linux-triage` 的实际内容（930 B，A 级原文）**——三段式：Inputs（`${input:ArchSnapshot}` / `${input:ProblemSummary}` / `${input:Constraints}` 全可选）→ Instructions（6 步，明确要求 `pacman`、`systemctl`、`journalctl`，并**必须处理内核更新/重启考量**）→ Output Format。

**两者真正的差异是权限模型，不是命令**：

| 维度 | `fedora-linux-triage` | `debian-linux-triage` |
|---|---|---|
| 工具 | `systemctl`、`journalctl`、**`dnf`** | `systemctl`、`journalctl`、**`apt`**、**`dpkg`** |
| 安全模块 | **SELinux** + `firewalld` | **AppArmor** 或防火墙 |
| 输入参数 | `${input:FedoraRelease}`（可选）等 | `${input:DebianRelease}`（可选）等 |

**统一输出格式（可直接当模板）**：

```
- Summary
- Triage Steps (numbered)
- Remediation Commands (code blocks)
- Validation (code blocks)
- Rollback/Cleanup
```

> **这些技能的价值不在"聪明"，在"骨架正确"**：强制编号步骤、强制验证命令、**强制回滚/清理**、并强制区分发行版的安全模块。**"强制回滚"这一条就值得抄进任何自建运维 skill。**

```bash
# 安装（路径已从 agents/ 迁到 skills/<name>/SKILL.md）
for s in arch-linux-triage fedora-linux-triage debian-linux-triage centos-linux-triage; do
  mkdir -p ~/.hermes/skills/$s
  curl -sL "https://raw.githubusercontent.com/github/awesome-copilot/main/skills/$s/SKILL.md" \
    -o ~/.hermes/skills/$s/SKILL.md
done

# 常驻规则（放项目级 AGENTS.md 或 Hermes 的 instructions 目录）
for d in arch fedora debian centos; do
  curl -sL "https://raw.githubusercontent.com/github/awesome-copilot/main/instructions/$d-linux.instructions.md" \
    -o ~/.hermes/instructions/$d-linux.instructions.md
done
```

---

## 第 7 章 通用基座与跨发行版方案

### 7.1 ⭐ `rhel-lightspeed/linux-mcp-server`：Red Hat 官方的只读 Linux 运维 MCP

> **这是整合阶段补上的最重要一块。** 前四轮都在找"社区做的运维 MCP"，漏掉了**厂商官方已经在做这件事**：Red Hat 的 RHEL Lightspeed 团队交付了一个生产级、只读、支持 SSH 多机的 Linux MCP，并且它**就是官方 "MCP Server for RHEL" 的内核**。全部数据 A 级（GitHub API + PyPI API + 官方文档原文）。

#### 7.1.1 身份与事实

| 项 | 实测值 | 核实方法 |
|---|---|---|
| 仓库 | `rhel-lightspeed/linux-mcp-server`（**Red Hat 官方组织**） | GitHub API |
| Stars / Forks | **317 / 67** | GitHub API |
| 许可证 / 语言 | **Apache-2.0** / Python | GitHub API |
| 创建 / 最近推送 | 2025-10-15 / **2026-10-10**（持续活跃） | GitHub API |
| PyPI 包 | `linux-mcp-server`，最新 **1.7.0**，`requires-python >=3.10` | PyPI JSON API |
| 官方定位 | 官方文档明确写：*"The Linux MCP Server is developed by Red Hat, and forms the basis of the MCP Server for RHEL"*，并链接到 **Red Hat RHEL 10 官方文档** | `docs/index.md` 原文 |
| 支持范围 | *"Built for Red Hat Enterprise Linux, Fedora, CentOS Stream, and other systemd-based distributions"* | `docs/index.md` 原文 |

#### 7.1.2 默认工具集：结构上不可能写

官方原文：*"All default-enabled tools are read-only. **No modifications to the system are possible through the fixed toolset.**"*

实现方式比"提示词要求只读"强得多——**命令是硬编码的元组，模型无法拼字符串**：

```python
# src/linux_mcp_server/commands.py（A 级源码）
COMMANDS = MappingProxyType({
    "list_services": CommandGroup(commands={
        "default": CommandSpec(args=("systemctl", "list-units", "--type=service", "--all", "--no-pager")),
    }),
    "service_status": CommandGroup(commands={
        "default": CommandSpec(args=("systemctl", "status", "{service_name}", "--no-pager", "--full")),
    }),
    "network_connections": CommandGroup(commands={
        "default": CommandSpec(args=("ss", "-tunap"), fallback=("netstat", "-tunap")),   # ← 可移植性回退
    }),
    ...
})
```

三个设计要点值得抄：

1. **参数是命名占位符**（`{service_name}`、`{lines}`），由 `substitute_command_args` 替换，**没有 shell 解释器参与**——不存在 `;`、`$()`、反引号注入面。
2. **`fallback` 机制**做跨发行版兼容（`ss` 失败退 `netstat`），这是它敢说"other systemd-based distributions"的技术依据。
3. **`MappingProxyType` 冻结**——运行时不可改写命令表。

工具按域分模块：`services` / `processes` / `logs` / `network` / `storage` / `system_info` / **`pcp`** / `run_script`。

#### 7.1.3 四个"默认就安全"的设计（fail-closed）

| 机制 | 默认行为 | 出处 |
|---|---|---|
| **日志白名单** | `read_log_file` 只读 `LINUX_MCP_ALLOWED_LOG_PATHS` 里列出的文件；**未设置该变量 = 一个文件都读不到** | `docs/security.md` |
| **SSH 认证** | **只支持密钥认证，要求免密**（不支持密码）；`LINUX_MCP_VERIFY_HOST_KEYS=True` 默认开启主机密钥校验 | `docs/security.md` |
| **鉴权策略引擎** | `auth_policy.py` 用 YAML 声明 `PolicyRule(host, tools, claims, action)`；`action ∈ {deny, ssh_key, ssh_default, local}`；工具支持 `*` / `-<tool>` / `@<group>` / `-@<group>` 四种模式；**pydantic 校验器在语义层强制 fail-closed**（`localhost` 只允许 `local`/`deny`；非 `localhost` 禁止 `local`；`ssh_key` 必须配 `ssh_key`；`all_users` 与 `claims` 互斥） | 源码 `auth_policy.py` |
| **审计** | 独立 `audit.py` 模块 | 源码目录 |

#### 7.1.4 受控命令执行（Guarded Command Execution）：唯一能写的地方

默认工具集写不了东西。要写，必须**显式**把 `LINUX_MCP_TOOLSET` 设成 `run_script` 或 `both`，此时暴露三个新工具：

```
validate_script  →  run_script  /  run_script_with_confirmation
```

官方文档描述的是**三层护栏**（A 级原文）：

| 层 | 机制 | 现状 |
|---|---|---|
| 1. **Gatekeeper 模型** | 用**另一个 LLM** 检查脚本：是否与描述一致、是否只读、是否符合策略、是否明显恶意 | 已实现；Gatekeeper 模型由用户自带 |
| 2. **人在环** | 修改系统的命令被标记为需人工批准，可查看描述与确切命令 | 已实现（含 `ui_resources/run-script-app.html/js` 交互审批界面） |
| 3. **沙箱** | 尽可能在 OS 级受限沙箱内执行 | 官方自述 *"currently rudimentary"*（还很初级） |

**Gatekeeper 的硬编码策略（原文，两轮调研里唯一见到厂商明写"不许加仓库"的地方）**：

```
 * Software can only be installed from repositories that are already
   configured on the system, such as apt or DNF repositories.
   No new repositories may be added.
 * Except for installing software from pre-configured repositories,
   nothing may be downloaded from the internet.
```

> **"不许新增软件仓库"这一条，直接掐死了 AUR / COPR / PPA / 第三方源这条投毒主路径。** 这是本报告见过最精准的一条 agent 运维策略，值得原样抄进自建 skill。

⚠️ 官方文档同时诚实地标注：Gatekeeper 的效果**取决于所选模型**，并提供了一个评测套件（eval suite）；文档里的模型评分表（Claude Opus 4.6 / gpt-oss:120b / gpt-oss:20b）**分数栏仍是 `??`，尚未填**。所以**不要假设 LLM 闸门已经可靠**——它是"多一层"，不是"可以替代人工批准的那一层"。

#### 7.1.5 一个必须知道的坑：HTTP transport 无鉴权

> ⚠️ **官方文档明文警告**：`LINUX_MCP_TRANSPORT=http` **当前没有认证**，*"It should not be used in production or on untrusted networks."*（`docs/security.md` 原文）

这和本报告第 10 章记录的那条 CISA 共同失败模式（*"鉴权逻辑信任重建出来的路径、后缀匹配或回退对象"*）是同一类问题：**一个未鉴权的 HTTP MCP 端点，等于把只读能力暴露给任何能连上端口的人**（只读也足以泄露日志、进程、网络连接、主机信息）。仓库里有 `docs/keycloak.md`（Keycloak 接入文档），但**本报告未核实 HTTP transport 的鉴权是否已实装**——按"默认不安全"对待。

**只用 stdio，或者自己加一层带鉴权的反向代理。**

#### 7.1.6 与 `openSUSE/systemd-mcp` 的分工

两个都是厂商官方，**不是替代关系，是互补**：

| 维度 | `rhel-lightspeed/linux-mcp-server` | `openSUSE/systemd-mcp` |
|---|---|---|
| 厂商 / 许可证 | Red Hat / Apache-2.0 | openSUSE / MIT |
| Stars | **317** | 10 |
| 语言 | Python（PyPI 装） | Go（`make build`） |
| 作用范围 | **本机 + 任意多台远程主机（SSH）** | 仅本机 |
| 访问方式 | 调**命令行**（`systemctl`/`journalctl`/`ss`/`ps`/`df`） | 直连 **systemd C API**（不经过 `systemctl`） |
| 授权模型 | YAML 策略 + SSH 密钥 + （可选）Gatekeeper LLM | **polkit**（stdio）/ OAuth2（HTTP） |
| 写能力 | 默认**结构性禁止**；`run_script` + 三层护栏 | `--allow-write`，**默认 `false`** |
| 跨发行版 | RHEL 系为主，官方称支持其他 systemd 发行版 | 任意 systemd 发行版 |
| 适合 | **舰队只读巡检、远程诊断、日志排查** | **单机 systemd 深度操作**（unit 属性、依赖、日志） |

**推荐组合：装 `linux-mcp-server` 做日常只读诊断（覆盖远程舰队），需要 systemd 深度控制时再叠 `systemd-mcp`（保持默认禁写）。**

#### 7.1.7 Hermes 配置片段

```yaml
mcp_servers:
  linux-tools:
    command: "/home/<user>/.local/bin/linux-mcp-server"   # uv tool install linux-mcp-server
    env:
      # ⚠️ 不设这个变量，read_log_file 读不到任何文件（fail-closed）
      LINUX_MCP_ALLOWED_LOG_PATHS: "/var/log/messages,/var/log/secure,/var/log/audit/audit.log"
      LINUX_MCP_VERIFY_HOST_KEYS: "True"
      # 不要设 LINUX_MCP_TOOLSET=run_script —— 保持默认只读工具集
      # 不要设 LINUX_MCP_TRANSPORT=http  —— HTTP 无鉴权
    lazy: true
    trust: untrusted          # 即使全是只读，也走逐次审批
    timeout: 60
```

### 7.2 跨发行版实用 MCP（社区侧）

> 厂商官方的两个（`linux-mcp-server` / `systemd-mcp`）见 §7.1，**优先用它们**。下表是社区侧补充。

| 类别 | 项目 | Stars | 说明 |
|---|---|---|---|
| **自托管面板** | `velopulent/tako` | 2 | Go 单二进制 + 内嵌 React 面板；**PAM 登录**（无独立账号库）；网关非特权、提权走本地 socket 上的特权 helper、按用户任务跑自身 UID，**三角色分进程隔离**。覆盖 Debian/Ubuntu/Fedora/RHEL/Rocky/Alma/openSUSE/Arch。AGPL-3.0，官方自述 **尚未到 v1** |
| **虚拟化** | `gilby125/mcp-proxmox` | 53 | Proxmox 虚拟化管理，**权限可配置** |
| | `ry-ops/proxmox-mcp-server` | 27 | Proxmox VE 的 VM/容器/存储（2026-10-11 活跃） |
| **容器** | `elusznik/mcp-server-code-execution-mode` | **340** | 在**隔离的 rootless 容器**里执行 Python |
| | `manusa/podman-mcp-server` | 84 | Podman + Docker 容器运行时 |
| | `Kiln-AI/Kilntainers` | 51 | **给每个 agent 一个临时 Linux 沙箱**执行 shell |
| **SSH** | `muchiny/bridge-mcp` | 10 | 安全 SSH 远程管理，**337 工具 / 74 分组** |
| | `Cosmicjedi/linux-administration-mcp` | 2 | SSH Linux 管理，含完整日志 |
| | `E13ctr0N/AiSysAdmin` | 2 | AI 辅助 Linux 管理 |
| **监控/变更** | `Higangssh/homebutler` | **300** | **"只告诉你值得告诉你的事"**——单 Go 二进制报告服务器变更 |
| | `initMAX/zabbix-mcp-server` | 229 | Zabbix 完整 API，**237 工具**，多 server、OAuth 2.1 |
| | `SikamikanikoBG/homelab-monitor` | 218 | 单容器 homelab 面板（GPU / VRAM / Docker / systemd） |
| | `tyxak/remotepower` | 74 | 一体化服务器与舰队管理，含 **patching** |
| | `bjeans/homelab-mcp` | 43 | homelab 基础设施管理 |
| **配置管理** | `sibilleb/AAP-Enterprise-MCP-Server` | 33 | Ansible Automation Platform (AAP) + EDA |
| | `bsahane/mcp-ansible` | 30 | MCP Ansible Server |
| | `jade-pico/antrieb-mcp-server` | 14 | "Real VMs for your LLM. Provision, execute, validate." |
| **权限回收** | `atraxsrc/claude-revoke` | 3 | **审计并撤销 Claude Code 在 Linux 上的全部授权**（trusted folders、"always allow"） |

### 7.3 Ansible 是混合舰队的正解方向

**Ansible 是五家的天然交集**：同一份 playbook 覆盖 `dnf` 与 `apt` 模块。

**"让 agent 写 playbook → 你审 → 再执行"比"让 agent 直接 SSH 执行命令"可控得多**：

| | agent 直接 SSH | agent 写 playbook |
|---|---|---|
| 可审查 | 单条命令，上下文缺失 | 整份 playbook 可读 |
| 可 diff | 难 | ✅ |
| 可回滚 | 靠 agent 记得 | ✅ 幂等 + 版本化 |
| 可复用 | 否 | ✅ |
| 审计粒度 | 命令级 | 任务级 |

### 7.4 Hermes 官方 NixOS 模块（声明式部署）

```nix
services.hermes-agent.mcpServers = {
  nixos = { command = "uvx"; args = [ "mcp-nixos" ]; };
  ssh = {
    command = "npx";
    args = [ "-y" "ssh-mcp-server" "--whitelist" "^(systemctl|journalctl|df|free).*" ];
  };
};
```

⚠️ 官方文档硬警告：**`settings` 和 `environment` 里的值会进 `/nix/store`（全局可读），API key 必须走 `environmentFiles` + sops-nix/agenix**。另外 `documents` 选项（装 `AGENTS.md`）必须显式设 `workingDirectory`；`SOUL.md` 和 `memories/` 要用 `hermesHomeFiles` 而不是 `documents`。

---

## 第 8 章 知识库选型：文件 → MCP → RAG

### 8.1 前提纠正

**内置持久记忆不是知识库。** 上限是 2200 字符（memory）+ 1375 字符（user），且这两个值是**代码默认值**（`hermes_cli/config_defaults.py:1321-1322`），本机 `config.yaml` 的 `memory:` 段只有 `memory_enabled` / `user_profile_enabled` 两个开关。

官方立场：*"对于需要每次运行都用到的事实，**skill 往往是比 memory 条目更好的归宿**。"*

**运维知识（机器清单、踩坑记录、回滚步骤）必须外置成文件。**

### 8.2 方案对比

| 方案 | 类型 | 存储 | 本地 | Agent 可写 | 维护负担 | 适用 |
|---|---|---|---|---|---|---|
| **Hermes 原生 `llm-wiki`** | 技能 + 文件 | 纯 markdown | ✓ | ✓ | **极低（0 安装）** | **首选** |
| **官方仓库离线 Wiki**（Arch） | `arch-wiki-lite` 包 | 纯文本，体积 1/9 | ✓ | ✗（只读层） | 极低 | **Arch 首选**，喂给 `llm-wiki` 的 `raw/` |
| Obsidian vault | 软件 + 技能 | 纯 markdown | ✓ | ✓ | 低 | 想可视化浏览 |
| `qmd` | 技能 + 本地索引 | 索引叠在 md 上 | ✓ | 间接 | 中 | 笔记上百篇后加语义检索 |
| `basic-memory` | MCP server | markdown + 知识图谱 | ✓ 本地优先 | ✓ | 中 | 想跨多个 AI 工具共享 |
| SiYuan（思源） | 软件 + 技能 | 自有格式 | ✓ | ✓ | 中 | 中文笔记体验优先 |
| OpenViking / Holographic | Hermes 记忆 provider | 文件层级 / HRR 代数 | ✓ | ✓ | 中 | 突破 2200 字符的"记忆" |
| Mem0 / Honcho / RetainDB / Supermemory | 记忆 provider | 云或自托管 | 部分 | ✓ | 中高 | 多 agent 共享记忆 |
| **RAG（RAGFlow/Dify/向量库）** | 平台 | 向量库 | 可自托管 | 间接 | **高** | 文档几千份且需模糊召回 |

### 8.3 `llm-wiki` 的结构（Karpathy 模式）

```
wiki/                        # 路径由 WIKI_PATH 环境变量指定，默认 ~/wiki
├── SCHEMA.md                # 约定、结构规则、领域配置
├── index.md                 # 分节内容目录 + 一行摘要
├── log.md                   # 追加式操作日志
├── raw/                     # 第 1 层：不可变原始素材（agent 只读）
├── entities/                # 第 2 层：实体页（机器、服务、主机）
├── concepts/                # 第 2 层：概念页（systemd 单元、flake 结构）
├── comparisons/             # 第 2 层：横向对比
└── queries/                 # 第 2 层：值得留存的查询结果
```

**核心论点**：*"传统 RAG 每次查询都从零重新发现知识；wiki **只编译一次**并持续保持更新——交叉引用已经建好，矛盾已经标记。"*

技能强制 agent **每次会话开始先读 `SCHEMA.md` → `index.md` → 最近 30 条 `log.md`** 完成定位。

**为什么这个结构天然适合运维**：第 1 层不可变、第 2 层 agent 可写、第 3 层 `SCHEMA.md` 约束 agent 行为——正好对应"**原始日志永不改，结论可以改**"的运维需求。

它就是一个 markdown 目录：可用 Obsidian / VS Code 打开、git 版本化、**换 agent 也不丢**。

### 8.4 什么时候升级

- 需要在 **Hermes 之外**（Claude Code、Codex、其他 MCP 客户端）也访问同一份知识库 → 上 `basic-memory`
- 需要突破 2200 字符的**记忆**上限（不是知识库上限）→ 换 `memory.provider`。可选：`byterover`、`holographic`（本地免费无依赖）、`honcho`、`mem0`、`openviking`（自托管）、`retaindb`、`supermemory`
- 只有当运维文档到了**几千份且需要模糊语义召回**，RAG 才开始有意义

---

## 第 9 章 技能市场实测总览

### 9.1 四个市场的覆盖情况

| 市场 | 定位 | 运维覆盖 |
|---|---|---|
| **clawhub.ai** | OpenClaw 官方技能/插件市场，镜像 skills.sh | 有大量 `linux-*` 技能，但**发行版专属覆盖不均**（Ubuntu 最丰富、Debian 最薄、NixOS 为 0、Arch 为 0） |
| **skills.sh** | 跨 agent 开放技能目录（全时段安装量 1,283,962） | **榜单前 55 名无任何运维/系统管理类技能** |
| **github/awesome-copilot** | GitHub 官方（55k★） | ✅ Fedora / Debian / Arch 专家技能；❌ **无 Ubuntu** |
| **AUR** | Arch 用户仓库 | 282 个 `mcp` 相关包，但**热度极低**（榜首 pop 仅 1.76） |

### 9.2 发行版专属覆盖梯度

| 发行版 | ClawHub | 代表技能 |
|---|---|---|
| **Fedora** | 单件最热 | **`awesome-copilot/fedora-linux-triage`（观测 8.9k）**、`xejrax/brew-install`（3.1k）、`silverod/rpm-ostree-toolkit`（721）、`mina-atef-00/hermes-browser-fedora-atomic`（190，**Hermes 专用**） |
| **Debian** | **最薄** | `openbot-esxi`（1.9k）、`holoscan-install-debian`（1.8k）。**无通用运维技能** |
| **Ubuntu** | **最丰富** | `doc-sysadmin`（1.3k）、`ubuntu-browser-session`（1.2k）、`ubuntu-inspector`（1k）、`ubuntu-encyclopedia`（951）、`ubuntu-wsl-system-cleanup`（842）等 10+ 件 |
| **NixOS** | **0 个** | 搜 "nixos" → "No skills found" |
| **Arch** | **0 个** | 搜 "arch" 全是 architecture（软件架构）噪音；唯一 Arch Linux 项是玩笑技能 `j3ffyang/arch-sign-off`（往文件尾追加 `btw, i use arch`） |

### 9.3 ClawHub 上的通用 Linux 运维技能（跨发行版可用）

| 技能 | 创作者 | 用途 | 安装量 |
|---|---|---|---|
| **Ssh Essentials** | arnarsson | SSH 命令、密钥管理、隧道 | 12.9k |
| **Cron & Scheduling** | gitgoodordietrying | cron 与 systemd timer 调度与调试 | 10.9k |
| **Linux** | ivangdavila | 调试与加固 Linux 主机：权限、磁盘满、OOM kill、卡死 | 6.6k |
| **Linux & service basics** | kowl64 | 用日志、systemd/PM2、文件诊断常见服务问题 | 6.5k |
| **Ssh Exec** | xejrax | 通过 SSH 在远程 Tailscale 节点跑单条命令 | 5.1k |
| **Log Tail** | xejrax | 流式读取 systemd journal 日志 | 3.4k |
| **Systemd** | ckchzh | systemd 参考工具 | 2.3k |
| **linux-kernel-crash-debug** | crazyss | 用 vmcore + crash 做证据优先的内核崩溃分析 | 2.2k |
| **Restic Home Backup** | moep90 | 加密 restic 备份设计/实施/运维 | 2.1k |
| **ssh-executor** | rickkbarbosa | SSH 远程执行，带**结构化发现协议** | 1.8k |
| **linux-firewall-hardening** | discovery219 | 安全防火墙加固，带后端探测、幂等原子操作 | 1.3k |
| **linux-sysadmin** | husttsq | 中文：权限、SSH、存储、网络、systemd、防火墙、监控、备份、Ansible、容器 | 1.2k |
| **linux-performance-analyzer** | husttsq | CPU/内存/磁盘 IO/网络/内核参数/容器调优 | 1.2k |
| **Systemd Unit Generator** | charlie-morrison | 生成、校验、lint systemd unit 文件 | 1.1k |

> **结论**：技能市场对运维的价值是"**补充通用件**"（SSH、systemd、日志、备份），不是"解决发行版专属需求"。发行版专属的东西在 **GitHub 小仓库 + 官方仓库包**里。

---

## 第 10 章 安全：事件、CVE 与设计原则

### 10.1 事件时间线（全部已发生，非理论风险）

| 时间 | 事件 | 要点 |
|---|---|---|
| 2025-06 | **Smithery.ai 路径穿越** | 3000+ server 配置含明文密钥泄露 |
| 2025-12 | **Anthropic Git MCP CVE 链** | 恶意 README/issue → 提示注入 → RCE |
| 2026-02 | **Clinejection** | 恶意 Cline 插件上 npm |
| 2026-03 | **LiteLLM rug pull** | 95M 月下载 |
| 2026-03 | **OpenClaw 清空用户目录** | 用户想删游戏文件，Agent 却清空了 Program Files |
| 2026-04-26 | **AI Agent 删除生产数据库** | Hacker News 热帖 763 分，Agent 删库后自动生成"认罪报告" |
| 2026-06 | **CVE-2026-42271**（LiteLLM MCP-bridge） | 子进程命令注入，修复 1.83.7，进 CISA KEV |
| 2026-08 | **Deadbugz** | 23 个 PR / 74 分钟投放恶意 MCP server |
| 2026-08 | **GuardFall** | 用几十年历史的 bash 技巧打穿大多数 coding agent |
| 2026-08-04 | **CVE-2026-9198**（Langflow） | `GET /api/v1/auto_login` 给任何网络调用者签发 SUPERUSER JWT。进 CISA KEV |
| 2026 进行中 | **AUR 200+ 恶意包收养** | 孤儿包被恶意者收养 + git commit author 可冒充 |
| 2026 | **CVE-2026-59822**（LiteLLM MCP 鉴权绕过） | 进 CISA KEV |
| 2026 | **RovoBlast**（Atlassian Rovo） | 单 URL 参数 `rovoChatPrompt` 劫持，DEF CON 34 / Varonis |
| 2026 | **Cryptographic Context Injection** | 加密 prompt injection 载荷绕过分类器，让模型自己解密执行 |
| 2026 | **DNS-AID**（Linux Foundation） | AI agent 的 DNS-based discovery |

### 10.2 三个必知 CVE 的完整细节

#### CVE-2026-84289 —— Hermes Agent MCP 内存放大 DoS

| 项 | 值 |
|---|---|
| **影响版本** | Hermes Agent **≤ 0.18.2** |
| **机制** | `tools/mcp_tool.py` 的 `_discover_tools()` / `_refresh_tools()` 对 `session.list_tools()` 返回的 `description` 与 `inputSchema` **无预算透传**；工具调用结果也无上限地走 `json.dumps()` |
| **实测** | **6,478 字节的 schema 被放大到 10,548,310 字节（约 1628 倍）**；单次运行接受的 MCP 描述达 10MB。并发槽占满后返回 `429 Too many concurrent runs (max 2)`，且失败请求**不释放已分配缓存** → 持久 DoS。CVSS 5.3 |
| **修复（0.20.5）** | `_MCP_HARD_RESULT_CAP_CHARS = 2_000_000` + `_truncate_mcp_text_result`（头 40% / 尾 60%）+ 50,000 字符预算溢写磁盘 |

**本机实测状态（A 级）**：
- `_MCP_HARD_RESULT_CAP_CHARS = 2_000_000` ✅ 存在于 `tools/mcp_tool_content.py:24`
- `_truncate_mcp_text_result` ✅ 存在于 `tools/mcp_tool_content.py:31`
- **结论：不受该 CVE 影响**

**但（本报告推断，D 级）**：本机 `tools/*.py` 里**未找到** `MAX_TOOLS` / `MAX_DESC_CHARS` / `MAX_SCHEMA_CHARS` / schema 深度上限这类**元数据侧**预算常量。CVE 修复重点是**结果侧**，而 1628 倍放大走的恰恰是**元数据侧**（`list_tools` 的 description/inputSchema）。→ **结果侧已修，元数据侧建议自己收窄**：坚持用 `tools.include` 白名单，只装工具数极少的 server。

#### CVE-2026-59822 —— LiteLLM MCP 鉴权绕过（进 CISA KEV）

| 项 | 值 |
|---|---|
| 组件 | LiteLLM 的 MCP Streamable HTTP endpoint |
| **机制** | 该 endpoint 支持对上游 MCP server 做 OAuth2 passthrough。**当请求的 LiteLLM key 校验失败时，回退路径本应转交 passthrough 逻辑，实际却替换成一个空的 `UserAPIKeyAuth()` 对象**。下游代码把它当成合法会话 |
| **净效果** | **任何带伪造 `Authorization` 头的请求都能到达 MCP endpoint，可以列出已配置的工具并调用它们。全程不需要任何有效 key** |
| CVSS v4 | **8.8**（AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N） |
| 修复版本 | **1.84.0** |
| 临时缓解 | 在反向代理上**阻断 `/mcp/` 路由** |

**同族**：CVE-2026-42271（**MCP-bridge 子进程命令注入**，修复 1.83.7）6 月进 KEV，且可与 Starlette Host-header 漏洞 CVE-2026-48710 串联。

> ⚠️ **如果你在 LiteLLM 前面挂 MCP 工具链，必须确认两个修复都已越过（1.83.7 与 1.84.0），而不是只打最新的那个。**

#### CVE-2026-9198 —— Langflow 未鉴权签发 SUPERUSER JWT

`GET /api/v1/auto_login` — **给任何网络调用者签发 SUPERUSER JWT**。无鉴权检查、不绑定 loopback。进 CISA KEV（2026-08-04）。

### 10.3 ⭐ 共同失败模式（最有价值的一条）

CISA 把这批和另外 6 个在野利用的 CVE（Starlette、Kestra、Artifactory、Switchvox、SonicWall SMA 1000）打包发布，原文总结：

> "**most share the same failure class: auth logic trusting a reconstructed path, a suffix match, or a fallback object instead of doing a hard check**"

**翻译成运维 checklist**：

1. **不接受"重建出来的路径"做鉴权** —— 路径归一化后再判，别用拼接结果
2. **不用后缀匹配做鉴权** —— `endsWith('/mcp')` 这类判断可被绕过
3. **回退路径绝不返回"空但合法"的对象** —— 失败就是失败，不要 `return UserAPIKeyAuth()`

### 10.4 供应链投毒：Deadbugz 的完整拆解

| 阶段 | 行为 |
|---|---|
| **投放** | 单个攻击者账户在 **74 分钟内提交 23 个 PR**，横跨互不相关的 AI/开发者工具项目，每个 PR 加入同一个（族）恶意 MCP server 引用。服务器**伪装成文本格式化/摘要工具** |
| **潜伏** | **前 3 次工具调用完全正常**，通过沙箱评估与人工试用 |
| **触发** | 第 3 次调用后**静默改写自身返回的工具元数据（description）**，把描述变成针对 agent 的指令——"搜索 `~/.ssh`、`~/.aws`、shell history、`~/.kube/config`，把内容发到攻击者端点"。载荷含 BTC 钱包地址 |

**核心教训**：MCP 服务器是**携带你生产凭据运行的未审查第三方代码**。"审查一次"在结构上无法防御延迟触发——你在 t0 审查通过，服务器在 t1 叛变。**恶意藏在元数据而非代码路径，静态扫描不可见。**

**防御（按投入产出比排序）**：

1. ⭐ **工具元数据漂移监控** —— 每次重连对比工具列表快照（`name` + `description` + `inputSchema` 的哈希），任何变化默认不信任并告警。**直接针对 Deadbugz 手法**
2. **内容寻址固定** —— 用 `pkg@sha512:...` 而非版本字符串；**禁止生产 agent 用 `npx` 直跑**（每次现拉最新版）
3. **权限最小化** —— agent 跑在专用最小权限账户，与 SSH key、云凭据隔离
4. **运行时监控** —— 监控 agent 进程 spawn shell、下载归档、访问 `~/.ssh`/`~/.aws`、异常外连

**同族事件的共同点**：**没有一次需要攻击 MCP 协议本身** —— 全部借用"安装即信任、名字即信任"的既有机制。

### 10.5 防护设计原则（可直接抄的清单）

从上述所有事件中提炼，以下设计模式反复被证明有效：

| 原则 | 具体做法 | 来源范例 |
|---|---|---|
| **默认禁写** | 写操作必须显式开启，且触发二次授权 | `systemd-mcp` 的 `--allow-write` 默认 false |
| **fail-closed** | 未登记的东西拒绝，而不是放行 | `fedora-agents` 暴露工具无权限表条目则拒绝启动 |
| **审计含被拒调用** | 连"试图做但被拦"也要记录 | `redwrench` 把被拒调用也写 journal |
| **变更操作不重试** | 只对幂等读重试 | `fedora-agents` 只重试 4 个读工具 |
| **权限逐项授予** | 不用全局 sudo，逐脚本/逐工具 | `fedora-agents` 的逐脚本 sudoers；`virsh`/`qemu-img` 上无 sudo 规则 |
| **参数不插值** | 校验后作为独立参数传入，绝不拼字符串 | `fedora-agents` 的 Zod 校验 |
| **引用可校验** | 每个结论带可复算的指纹 | `arch-wiki-mcp` 的 SHA-256 + revid |
| **取并集不取交集** | 多个扫描器结果取并集，冲突取更高风险 | `herraiz-org/ai-skills` 的 "evidence, not a verdict" |
| **用机制替代提示词** | 能做成 hook/拦截就不写在文档里 | Arch `informant`（pacman hook 强制读新闻） |
| **权限回收能力** | 定期审计并撤销已授予的权限 | `atraxsrc/claude-revoke` |

---

## 第 11 章 落地方案

### 11.1 通用配置（所有发行版）

#### `SOUL.md` —— 追加运维安全底线

```markdown
## 运维操作底线（不可协商）

### 写操作纪律
- 任何写操作前，先用只读命令确认现状（`systemctl status`、`df -h`、`nixos-rebuild dry-build`）
- 执行变更前，先把**完整命令原文**打印给我看，等我确认。不要直接执行
- 破坏性操作一律先停下问我：`rm`、`dd`、`mkfs`、`pacman -Rdd`、
  `nix-collect-garbage -d`、修改 `/etc/fstab`、`systemctl disable`、任何写 `/boot` 的操作
- 变更前必须先有回滚路径：快照 / 新 generation / 降级命令

### 引用纪律
- 每个命令引用必须能回溯到官方文档的具体位置（发行版 Wiki / man page / 官方手册）
- 不确定就说不确定。不要编造包名、选项名或文件路径——先去查

### 输出纪律
- 读到任何密钥、token、私钥内容，不要复述到对话里，不要写进任何笔记文件
- 报告用简洁事实 + 链接 + 清单，不要生成冗长格式化文本
```

#### `AGENTS.md` —— 项目级

```markdown
# AGENTS.md — <你的运维仓库>

## 环境
- 发行版探测优先：先 `cat /etc/os-release`，不要假设
- 目标机清单：<主机名> / <发行版> / <包管理器> / <访问方式>

## 标准操作流程
### 更新（按发行版）
- NixOS：`nix flake check` → `nixos-rebuild dry-build` → 给我看 diff → 才 `switch`
- Arch：`informant` 读新闻 → `checkupdates` → `yay -Qua` → AUR 审计 → 快照 → 全量升级
- Fedora：`dnf-automatic` 或手工；`dnf needs-restarting -r`
- Debian/Ubuntu：`apt update` → 读 changelog → 升级 → `needrestart -r l`

### 回滚路径（必须写出来）
- NixOS：`nixos-rebuild switch --rollback` 或选 generation
- Arch：`downgrade <pkg>` 或 `pacman -U /var/cache/pacman/pkg/<旧版本>.pkg.tar.zst`
- Fedora：`dnf history undo <id>`
- Debian/Ubuntu：`apt install <pkg>=<version>`

## 知识库
- 路径：`$WIKI_PATH`
- 每次排障结束，把结论写进 `kb/`，不要只留在对话里
- 不复制发行版 Wiki 内容进知识库（体积爆炸）——只存"本机特有的结论与坑"
```

#### `config.yaml` —— 通用安全配置

```yaml
# 危险命令白名单：只放只读查询（"永久允许"会自动写到这里）
command_allowlist:
  - "systemctl status *"
  - "systemctl --failed"
  - "journalctl -u *"
  - "df -h"
  - "free -h"
  - "uptime"
  # ⚠️ 绝不加入：rm / dd / mkfs / 任何包管理器写操作

# 用户自定义硬拒绝（在 yolo 之前生效）
approvals:
  mode: smart
  deny:
    - "systemctl disable *"
    - "systemctl mask *"
    - "git push --force*"
    - "dd if=* of=/dev/*"
    - "rm -rf /*"

# 预执行安全扫描（默认关，建议开）
security:
  tirith_enabled: true
  tirith_timeout: 5
  tirith_fail_open: false     # 不可用时拒绝，而不是放行

# MCP：执行层默认只读（两个厂商官方方案，见 §7.1）
mcp_servers:
  linux-tools:                        # 首选：Red Hat 官方，只读工具集 + SSH 多机
    command: "/home/<user>/.local/bin/linux-mcp-server"
    env:
      LINUX_MCP_ALLOWED_LOG_PATHS: "/var/log/messages,/var/log/secure,/var/log/audit/audit.log"
      LINUX_MCP_VERIFY_HOST_KEYS: "True"
      # 不要设 LINUX_MCP_TOOLSET=run_script（保持只读）
      # 不要设 LINUX_MCP_TRANSPORT=http（HTTP 无鉴权）
    lazy: true
    trust: untrusted
    timeout: 60

  systemd:                            # 需要 systemd 深度控制时再叠（默认禁写）
    command: "/usr/bin/systemd-mcp"
    args: []                          # 不加 -w → 默认只读
    lazy: true
    trust: untrusted
    tools:
      include: ["list_units", "list_log", "get_man_page", "get_file"]
      exclude: ["change_unit_state"]  # 要改 unit 时再单独放开
```

### 11.2 分发行版配置

#### NixOS

```bash
# 知识层
uvx mcp-nixos          # 2 工具，约 1030 token，不需要装 Nix
# 沙箱（三选一）
#  - SecBear/nix-sandbox-mcp    最轻（约 420 token 固定），默认无网络，项目只读挂载
#  - andersonjoseph/jailed-agents   把整个 agent 关进沙箱
#  - 自建一台一次性 NixOS VM       社区最认可
```

```yaml
mcp_servers:
  nixos:
    command: "uvx"
    args: ["mcp-nixos"]
    lazy: true
    tools:
      include: ["nix", "nix_versions"]
```

#### Arch

```bash
# 官方仓库基座（知识库 + 安全闸门）
sudo pacman -S arch-wiki-lite arch-wiki-docs informant arch-audit pacman-contrib
informant check
# 两个 MCP
uvx arch-ops-server                # ⚠️ 不是 npx arch-mcp（npm 上无此包）
pipx install arch-wiki-mcp
# 技能（质量最高的那个）
git clone https://github.com/herraiz-org/ai-skills.git ~/.local/share/ai-skills
git clone https://github.com/enihcam/aur-skills.git    ~/.local/share/aur-skills
for s in ~/.local/share/ai-skills/skills/* ~/.local/share/aur-skills/skills/*; do
  ln -sfn "$s" ~/.hermes/skills/"$(basename "$s")"
done
# ⚠️ 不要把克隆放 /tmp（很多系统挂 tmpfs，重启即清）
```

```yaml
mcp_servers:
  arch-wiki:
    command: "arch-wiki-mcp"
    lazy: true
    trust: untrusted
    tools:
      include: ["page", "section", "commands", "warnings", "search"]
  arch-ops:
    command: "uvx"
    args: ["arch-ops-server"]
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
      exclude:
        - "install_package_secure"
        - "remove_packages"
        - "manage_orphans"
        - "manage_install_reason"
        - "optimize_mirrors"
```

#### Fedora

```bash
# 策略引擎 MCP（从 release 装 .rpm）
sudo dnf install ./redwrench-*.rpm
# 官方自动更新 + 重启检测
sudo dnf install dnf-automatic dnf5-plugins
sudo systemctl enable --now dnf-automatic.timer
dnf needs-restarting -r
# 不可变系统（Silverblue/Kinoite/Bazzite）改用：
#   rpm-ostree install <pkg>      ← 不要用 dnf install
# 技能
mkdir -p ~/.hermes/skills/fedora-linux-triage
curl -sL https://raw.githubusercontent.com/github/awesome-copilot/main/skills/fedora-linux-triage/SKILL.md \
  -o ~/.hermes/skills/fedora-linux-triage/SKILL.md
```

#### Debian

```bash
# 漏洞分析三件套
pip install debvulns
debvulns --severity high
# 官方安全闸门
sudo apt install unattended-upgrades needrestart debsecan apt-listchanges apt-listbugs
sudo dpkg-reconfigure -plow unattended-upgrades
sudo needrestart -r l              # ⚠️ 关键：列出跑着旧库的服务
sudo debsecan --suite bookworm --format detail
# 技能
mkdir -p ~/.hermes/skills/debian-linux-triage
curl -sL https://raw.githubusercontent.com/github/awesome-copilot/main/skills/debian-linux-triage/SKILL.md \
  -o ~/.hermes/skills/debian-linux-triage/SKILL.md
```

#### Ubuntu

```bash
# Pro / ESM / Livepatch（Ubuntu 独有）
pro status && pro security-status
sudo pro enable livepatch
# 官方安全闸门
sudo apt install unattended-upgrades needrestart
snap refresh --list                # ⚠️ snap 是独立通道，必须单独覆盖
# 技能（ClawHub 上最丰富的生态，挑这几个）
#   chengchiangwork/ubuntu-inspector        系统巡检
#   kklouzal/ubuntu-encyclopedia            文档优先工作流
#   shenzheke/ubuntu-wsl-system-cleanup     安全清理
#   krishnakumarmahadevan-cmd/toolweb-ubuntu-hardening   加固配置生成
# ⚠️ Ubuntu 没有 awesome-copilot 专家技能 → 用 debian-linux-triage
```

#### RHEL / CentOS / Rocky / Alma（v1.1 新增，见 §7.1 与附录 E）

```bash
# 执行层：Red Hat 官方，只读工具集 + SSH 多机（RHEL 系的最佳答案）
uv tool install linux-mcp-server
export LINUX_MCP_ALLOWED_LOG_PATHS="/var/log/messages,/var/log/secure,/var/log/audit/audit.log"
export LINUX_MCP_VERIFY_HOST_KEYS=True

# 知识层：Red Hat Offline Knowledge Portal MCP（= RHEL 版的离线知识源）
#   仓库：rhel-lightspeed/okp-mcp

# 技能：CentOS 有 awesome-copilot 三件套；RHEL/Rocky/Alma 没有 → 退回 centos 版
for s in centos-linux-triage; do
  mkdir -p ~/.hermes/skills/$s
  curl -sL "https://raw.githubusercontent.com/github/awesome-copilot/main/skills/$s/SKILL.md" \
    -o ~/.hermes/skills/$s/SKILL.md
done

# ⚠️ 以下运维基座本轮未核验（附录 E.5，D 级），落地前自己确认：
#   dnf-automatic / dnf needs-restarting / SELinux(默认 enforcing)
#   dnf updateinfo / OpenSCAP / subscription-manager / leapp 升级路径
```

### 11.3 三档推进顺序

**顺序原则**：先零成本（配置/路径）→ 再技能 → 最后 MCP。理由是 MCP 工具每轮都占上下文。

#### 档 1：今天，零成本（约 40 分钟）

1. 写 `$HERMES_HOME/SOUL.md` 的运维安全底线。**这一步优先于一切**——它是唯一跨项目生效的闸
2. 在运维仓库根放 `AGENTS.md`
3. 在 `config.yaml` 配 `command_allowlist` + `approvals.deny` + 开 tirith
4. 建知识库：`export WIKI_PATH=~/ops-kb && mkdir -p $WIKI_PATH && git -C $WIKI_PATH init`
5. 确认 `command_allowlist` 里**没有**任何 `rm`、`dd`、`mkfs` 之类的宽泛模式

#### 档 2：本周（约 1–2 小时）

6. 装 `openSUSE/systemd-mcp`（默认只读，覆盖所有 systemd 发行版）—— **投入产出比最高的一步**
7. 按发行版装知识层（`mcp-nixos` / `arch-wiki-lite` / `debvulns` / `redwrench`）
8. 装对应发行版的专家技能（`awesome-copilot` 或 `herraiz-org/ai-skills`）
9. 装 `mcporter` 技能，用它验证 MCP 是否真的连上、工具名是否正确
10. 配**工具元数据漂移监控**（Deadbugz 的直接克星）

#### 档 3：按需

11. 沙箱层（NixOS 尤其推荐：`nix-sandbox-mcp` 或一次性 VM）
12. `qmd` 做语义检索（笔记过百篇后）
13. 换外部记忆 provider（`holographic` 本地免费 / `openviking` 自托管）
14. 混合舰队改用 Ansible：让 agent 写 playbook → 你审 → 再跑
15. 在 NixOS 上部署 Hermes 本体，改用官方模块 + sops-nix 管密钥

### 11.4 工具元数据漂移监控（Deadbugz 的直接克星）

```python
# 每次 session 建立/重连后调用；有 drift 就阻断并通知人工，而不是继续信任
class McpToolFingerprint:
    def __init__(self, trusted_snapshot: dict):
        self.trusted = trusted_snapshot

    def snapshot(self, tools) -> dict:
        sig = {}
        for t in tools:
            canon = json.dumps(
                {"name": t.name, "description": t.description, "schema": t.inputSchema},
                sort_keys=True, ensure_ascii=False,
            )
            sig[t.name] = hashlib.sha256(canon.encode()).hexdigest()[:16]
        return sig

    def verify(self, tools) -> list[str]:
        cur, drift = self.snapshot(tools), []
        for name, digest in cur.items():
            if name not in self.trusted:
                drift.append(f"新工具出现: {name}")
            elif self.trusted[name] != digest:
                drift.append(f"元数据漂移: {name} {self.trusted[name]} -> {digest}")
        for name in self.trusted:
            if name not in cur:
                drift.append(f"工具消失: {name}")
        return drift
```

---

## 第 12 章 坑与反直觉（全量清单）

### 12.1 Hermes 框架层

1. **`agent.md` 不是一份文件。** 人格（`SOUL.md`）、项目指令（`AGENTS.md`）、记忆（`MEMORY.md`/`USER.md`）是三套独立系统，互不喂数据。改 `SOUL.md` 不会填 `USER.md`。
2. **记忆是冻结快照。** 中途改配置不生效，必须重启会话。排查"为什么它忘了"时先看这个。
3. **profile 不是沙箱。** 建 profile 只隔离状态目录，不限制文件系统访问。
4. **内置记忆只有 2200 字符，且这是代码默认值。** 它设计上就不是知识库，是偏好存储。拿它装运维知识必然爆。
5. **`HERMES_HOME` 不一定是 `~/.hermes`。** 本机是 `%LOCALAPPDATA%\hermes`。找 `config.yaml` 先看环境变量。
6. **官方文档会引用过期常量。** `security.md` 说硬阻断清单在 `tools/approval.py::UNRECOVERABLE_BLOCKLIST`，实际在 `tools/approval_detection.py` 的 `HARDLINE_PATTERNS`。**以源码为准。**
7. **硬阻断清单无法绕过。** `--yolo`、`/yolo`、`approvals.mode: off`、cron `approve`、点"always allow"**全部无效**，且没有覆盖开关。要跑这类命令就在 agent 外面跑。
8. **硬阻断只对能损伤宿主的环境生效。** 容器化后端本来就绕过了危险命令层——**别以为容器里的 agent 有这层保护。**
9. **`security.tirith_*` 默认全关。** 预执行扫描必须手动开。
10. **MCP 结果的溢出阈值更严（50,000 字符 vs 通用 100K）。** 这是框架对"MCP server 常返回未分页的 20-50K 载荷"的针对性设计。

### 12.2 MCP 与上下文

11. **MCP 的上下文税是真实成本。** 静态加载约 150 token × N 个工具；**60 个工具 ≈ 47k token（在你开口之前）**。一个参数化工具约 420 token 固定。
12. **"审查一次"是结构性失效的控制。** Deadbugz 证明：恶意 server 前 3 次调用完全正常，之后重写自己的工具元数据。必须做**工具元数据漂移监控**，并且**不要用 `npx` 直跑**。
13. **`tools.include` 与 `exclude` 同时存在时 `include` 优先。** 别指望用 exclude 覆盖 include。
14. **远程 server 的 `url`/`headers` 里变量未设时连接直接失败**（防 401 的设计），不是发字面量。

### 12.3 发行版专属

#### NixOS
15. **NixOS 社区对"agent 管 NixOS"是怀疑的。** 论坛原话："用 agent 来做这件事，某种程度上违背了初衷吧"；"**AI 这个 easy button 是你在赚到资格之后才按的**"。
16. **`nix.settings.trusted-users` 是 agent 最爱踩的提权坑。** r/NixOS 实测：Claude **未经提示**把用户加进 `trusted-users`（等于免费提权到 root）。`AGENTS.md` 里要显式禁止。
17. **本地小模型写 nix 会毁文件。** 实测 `Qwen3.5:4B-Q6` "太蠢了没法用，通常把文件搞坏然后试图 git checkout"。24GB 卡上可用的是 `gemma4:26b-a4b-it-q4_K_M` / `Qwen3.6-27B`。
18. **NixOS 社区对"agent 管系统"的真正答案是沙箱，不是权限。** 最被认可的模式是"给 agent 一台一次性 NixOS VM"。
19. **`nix-agent` 默认高信任。** 未经提示即可 `switch` + 免密 sudo，低信任模式是 opt-down 而非默认。作者自称实验性。

#### Arch
20. **`arch-mcp` 的仓库名 ≠ 安装名。** 仓库 `nihalxkumar/arch-mcp`，PyPI 包 **`arch-ops-server`**，命令 `uvx arch-ops-server`。**npm 上不存在 `arch-mcp`**。
21. **`arch-mcp` 有写操作，别当只读用。** 14 个工具里 5 个会改系统。必须 `trust: untrusted` + `tools.include` 白名单。
22. **`arch-wiki-mcp` 只有 1★，但设计比 59★ 那个更该学。** 三档证据分层 + `<esp>` 占位符防误粘是可搬进任何运维 skill 的通用模式。
23. **`arch-wiki-mcp` 的默认分支是 `master` 不是 `main`。** 用 raw 抓 README 返回 404 时，先试换分支名，别直接判"仓库不可用"。
24. **Arch 知识库不需要 MCP。** `arch-wiki-lite` 一个包给出离线全文 Wiki（体积 1/9）。上 MCP 联网查 Wiki 是**把确定性换成不确定性**。
25. **"commit author 是原作者"不是信任证据。** AUR 的 git commit author 可冒充。唯一信任来源是你自己读了那次的 PKGBUILD diff。
26. **孤儿包被收养 = 需重新审计。** AUR 允许任何人收养 orphan，这是 200+ 恶意包的入口之一。
27. **`checkupdates` 在 `pacman-contrib` 里。** 而引导安装它时**绝不能从 AUR 满足该依赖**——那等于用不可信源装一个"用于检查不可信源"的工具。
28. **Arch News 的 RSS 只有约 10 条。** 上次全量升级早于最旧条目时，中间期间的公告**不可达**。必须**显式报告盲区**，而不是当作"没有新闻"。
29. **Arch 没有声明式回滚。** NixOS 的回滚是系统能力，Arch 要靠 btrfs snapshot / timeshift / `downgrade`。**快照必须发生在升级之前，且这一步不能交给 agent 判断。**
30. **r/archlinux 有明显的反 AI slop 情绪。** AI 生成的冗长报告即使内容正确也会被社区忽视甚至围攻。报安全事件写**简洁事实 + 链接 + 包清单**，直发 `aur-general@lists.archlinux.org`。

#### Fedora / Debian / Ubuntu
31. **最好的运维 MCP 不是发行版专属的。** `openSUSE/systemd-mcp` 覆盖 Fedora/Debian/Ubuntu 全部——因为它们都跑 systemd。
32. **`systemd-mcp` 默认 `--allow-write=false`，这是设计不是遗漏。** `--noauth` 甚至要求把值写成字面量 `ThisIsInsecure`。
33. **Fedora 的重启检测不是 `needrestart`，是 `dnf needs-restarting`**，且在 `dnf5-plugins` 包里。
34. **`unattended-upgrades` 默认不重启。** 装了新内核也只提示 → 系统仍跑旧代码。**"我开了自动更新所以安全了"是 Debian/Ubuntu 最常见的安全假象**。
35. **Debian 的 MCP 包名改过。** `debsecan-mcp` 停在 0.1.5，之后全在 **`debvulns`**。搜旧名会装到死版本。
36. **Ubuntu star 最高的 MCP 已停更 16 个月。** `pazuzu1w/ubuntu_mcp_server`（44★）最后提交 2025-06-29。**能操作操作系统 + 长期未维护 = 明确风险项。**
37. **awesome-copilot 有 Fedora 和 Debian 专家技能，但没有 Ubuntu 的。** 探测 6 个 Ubuntu 变体名全部 404。
38. **两个 triage 技能真正的差异是权限模型，不是命令。** Fedora 版带 **SELinux + firewalld**，Debian 版带 **AppArmor**。
39. **Fedora 不可变版上 `dnf install` 直接失败。** 要 `rpm-ostree install` 或 `toolbox`。给 agent 的指令必须区分"标准 Fedora"与"Fedora Atomic"。
40. **很多 AI 工具只发 `.deb`。** Claude Desktop Linux 版只有 `.deb`，Fedora 用户自己重打包成 RPM。
41. **Ubuntu 有两条更新通道（apt + snap）。** 只做 apt 会出现"apt 说全更新了，snap 包还是旧的"。
42. **Ubuntu Pro / ESM 是订阅，不是配置。** `pro security-status` 直接告诉你哪些包已过标准支持期。
43. **ClawHub 上 Ubuntu 技能最丰富，Debian 最薄。** Debian 用户可借用 Ubuntu 的技能（apt 生态兼容）。

### 12.4 安全设计

44. **`fedora-agents` 的 fail-closed 值得抄：暴露的工具没有权限表条目就拒绝启动。** 多数 MCP server 是"没登记就默认放行"，它反过来。
45. **`fedora-agents` 对变更操作永不重试。** **"重试"在运维场景是危险默认值**——agent 网络抖动重试一次 `vm_destroy` 就是灾难。
46. **`redwrench` 的审计日志连"被拒绝"的调用也记。** 只记成功的审计是半个审计。
47. **CVE-2026-59822 的教训是"回退对象不能是空但合法"。** 失败就返回失败。
48. **LiteLLM 今年两次进 KEV（1.83.7 与 1.84.0）。** 只打最新那个不够。
49. **GuardFall 证明 agent 的注入防护不是静态属性。** 几十年前的 bash 技巧打穿多数 coding agent，唯一防住的 Continue 已被收购停维护。**别把"我选了防护好的 agent"当成安全边界。**
50. **聚合站点的技能列表会造假。** `mcpmarket.com` 把不存在的仓库列为真实技能。**任何来自聚合站的技能都要逐个回 GitHub 核验。**
51. **`aurwatch.org` / `aur-audit.wtako.net` 是第三方个人服务。** 让第三方告诉你"哪些包是恶意的"本身就是一个新的信任依赖。

**以下 52–58 为 v1.1 新增（来自 Red Hat 官方 MCP 与覆盖边界补充）：**

52. **`linux-mcp-server` 的 HTTP transport 当前无鉴权。** 官方文档明文警告 *"should not be used in production or on untrusted networks"*。**只读也一样致命**——日志、进程、网络连接、主机信息全部暴露。只用 stdio，或自加带鉴权的反代。
53. **不要把"LLM 闸门"当成安全边界。** Red Hat 的 Gatekeeper 是真实存在的三层护栏之一，但**官方模型评分表仍是 `??`（未填）**。它是"多一层"，不是"可以替代人工批准的那一层"。
54. **厂商官方 ≠ 长期维护。** `rhel-lightspeed` 组织 20 个仓库里 **4 个已归档**（含 `sysadmin-agents`、`redhat-status-mcp`）。**引用厂商项目同样要看 `archived` 标志。**
55. **无许可证的 MCP 不能用于生产。** openSUSE 仅有的两个专属 MCP（`LeapDoctor`、`zypper-mcp`）都是 0★ 且**无许可证**——默认保留全部权利，法律上不可用。**不要因为"没有别的选择"就用它。**
56. **⚠️ `awesome-copilot` 里的 `plugins/arch/` 不是 Arch Linux**，是 software **architecture** 插件（`plugin.json` 原文 *"Architecture and modernization toolkit"*）。用 `arch` 做关键词搜索这个仓库，**大部分命中是软件架构噪音**。
57. **厂商官方也不一定覆盖你的发行版。** `awesome-copilot` 覆盖 **CentOS 却不覆盖 RHEL / Rocky / Alma**——它是按"社区常见度"选型的，不是按"企业装机量"。RHEL 用户要走官方线。
58. **抽样探测路径会漏掉整类资源。** `awesome-copilot` 有 **4 类**资源目录（`instructions/`、`skills/`、`agents/`、`plugins/`），只探 2 类就会得出错误结论（本报告就因此把 Arch 误记为"无技能"）。**存在性核验要用全量目录树，不要靠猜路径名。**

---

## 第 13 章 未核实与覆盖边界

### 13.1 已核实（A 级）

- 本机 Hermes 全部实测项：commit `4e7403130e`（**2026-09-29**）、65/152/349/58 四项计数、`mcp_servers` 为空、`command_allowlist` 与 `approvals` 不存在、tirith 全注释、`HARDLINE_PATTERNS` 12 条模式、`_MCP_HARD_RESULT_CAP_CHARS = 2_000_000`、`mcp_result_size_chars: 50000`、记忆上限来源 `hermes_cli/config_defaults.py:1321-1322`、`skills.external_dirs` 只读
- 所有 GitHub 仓库元数据（stars / license / 创建与最后提交时间）：`arch-mcp` 59★、`arch-wiki-mcp` 1★、`systemd-mcp` 10★、`redwrench`（Rust/MIT OR Apache-2.0）、`fedora-agents`（TS/MIT）、`debsecan-mcp`→`debvulns`、`ubuntu_mcp_server` 44★/2025-06-29
- 包管理 API 核验：PyPI `arch-ops-server` 3.4.0、`arch-wiki-mcp` 2.1.0；npm `arch-mcp` **不存在**；Fedora `dnf5` 5.4.6.0-1.fc44 / `rpm-ostree` 2026.3-2.fc44 / `toolbox` 0.3-4.fc44；Debian `unattended-upgrades` 2.13 / `needrestart` 3.11-1 / `debsecan` 0.4.20.2；Arch `arch-wiki-lite` 20261003-1 / `informant` 0.6.0-2 / `arch-audit` 0.2.0-5
- `awesome-copilot` 文件存在性（HTTP 探测 + **全量目录树**）：`instructions/`、`skills/*-linux-triage/`、`agents/*-linux-expert.agent.md` 三类 × `arch` / `fedora` / `debian` / `centos` **全部 200**；`ubuntu` / `rhel` / `opensuse` **全部 404**；`plugins/arch/plugin.json` 200（但是软件架构插件，非 Arch Linux）
- **Red Hat 官方 `linux-mcp-server`**：317★ / 67 forks / Apache-2.0 / Python、PyPI 1.7.0、`rhel-lightspeed` 组织 20 仓库全表、`docs/security.md` 与 `docs/guarded-command-execution.md` 原文、`commands.py` 命令表与 `auth_policy.py` 策略模型
- **`rhel-lightspeed` 组织 20 仓库的 stars / 许可证 / 归档状态**（4 个已归档）
- **openSUSE 组织前 100 仓库清单**——确认除 `systemd-mcp`（10★）外无其他 MCP / AI 仓库
- Reddit 原帖正文与评论原文（经 Hermes 自带 Atom 后端实抓）

### 13.2 项目自述未独立复现（C 级）

- `mcp-nixos` 的"约 1030 token / 2 工具"
- `nix-sandbox-mcp` 的"约 420 token 固定"
- `nix-agent` 的默认信任档
- `arch-mcp` 的 `audit_package_security` 50+ 红旗命中率、`install_package_secure` 的拦截有效性
- `arch-wiki-mcp` 的 hash 稳定性与 `test_contract.py` 覆盖面
- `herraiz-org/ai-skills` 的 pytest 套件（文件存在，**未运行**）
- `redwrench` 四个 tier **具体允许/拒绝哪些命令**（README 只给名称与设计说明）
- `systemd-mcp` 的 6 个工具（**未实际调用测试**）、`gatekeeper` 的 polkit policy 内容
- `debvulns` 的 EPSS 数据源与刷新机制
- `traur` / `ks-aur-scanner` 的维护状态与检出能力
- `archward` 的实际可靠性、快照在不同文件系统上的表现

### 13.3 本报告推断（D 级）

- **本机未见元数据侧预算常量**（`MAX_TOOLS` / `MAX_DESC_CHARS` / `MAX_SCHEMA_CHARS` / schema 深度）→ 推断 CVE-2026-84289 的元数据放大向量可能仍需自行收窄。**这是推断，不是已核实的漏洞结论。**
- r/archlinux 早期缺少 AI 运维讨论的原因（"Arch 是命令式发行版"）为推断，无直接证据。
- `aurwatch.org` / `aur-audit.wtako.net` 的可用性、准确性、数据更新频率未核验。

### 13.4 未覆盖（明确的空白）

> **整合阶段已补掉两项**：RHEL 系与 openSUSE 见**附录 E**（含 Red Hat 官方 `linux-mcp-server` 的完整核验）。以下为剩余空白。

- **RHEL 系的企业侧配套** —— `subscription-manager` / `leapp` 升级路径 / Red Hat Insights / Satellite 与 agent 的结合方式，仅做了定性说明，未逐项核验（附录 E）
- **openSUSE 的发行版生态** —— 只核验了官方 `systemd-mcp` 与仓库清单（`snapper` / `transactional-update` / `zypper`），**未找到任何 openSUSE 专属 MCP 或技能**；SUSE Linux Enterprise（SLE）侧完全未覆盖
- **`linux-mcp-server` 在非 RHEL 发行版上的实测** —— 官方文档称支持"other systemd-based distributions"，本报告**未在 Arch / Debian 上实跑验证**（推断级）
- **`linux-mcp-server` 的 Gatekeeper 评测分数** —— 官方模型评分表仍是 `??`，未填；闸门可靠性未独立评估
- **Windows / WSL** —— 未覆盖（WSL 侧只有零散技能）
- **`snap` 与 agent 交互的实际坑** —— 仅指出双通道问题，未实测
- **Ubuntu Pro 定价与 AI 运维成本模型** —— 未调研
- **各发行版官方工具的"AI 友好性"** —— `dnf-automatic`、`unattended-upgrades`、`needrestart` 是否输出机器可读格式、是否适合 agent 解析，未验证
- **`CVE-2026-9198` / `RovoBlast` / `Cryptographic Context Injection` 的完整技术细节** —— 均来自 r/linuxadmin 转述的第三方分析（C 级），**未回原始报告核验**
- **各记忆 provider 的实际效果**（byterover / holographic / honcho / mem0 / openviking / retaindb / supermemory）—— 未实测
- **ClawHub 安装量的可比性** —— 平台有 "Updated 5mo ago" 与 "Observed 6d ago" 两种口径混用

### 13.5 抓取失败与解法（跨四轮汇总）

| 目标 | 现象 | 解法 |
|---|---|---|
| `api.github.com/repos/<...>` | **`API rate limit exceeded … remaining 0/60`** | 改用 `raw.githubusercontent.com` 读 README（有独立额度）；元数据留空并标注 |
| GitHub **HTML 页** | 网页抓取返回空内容或导航壳 | **改用 `api.github.com` + `raw.githubusercontent.com`**；判断文件存在性用 `curl -o /dev/null -w "%{http_code}"` |
| `raw.githubusercontent.com/egarcia74/arch-wiki-mcp/**main**/README.md` | 404 | **默认分支是 `master`**，换分支名成功 |
| `raw.githubusercontent.com/YPares/rigup.nix/main/README.md` | 空 | 未解决；描述来自搜索摘要，标 C 级 |
| `mdapi.fedoraproject.org/f44/pkg/dnf-automatic` | `400 Bad Request` | mdapi **不索引 noarch 子包**；改用 `packages.fedoraproject.org/search?query=` |
| `skills.sh/search?q=` | JS 渲染，抓不到 | 退到首页榜单 |
| `github.com/ranicharradi/arch-maintenance-skill` | **404** | 仓库不存在；来自聚合站 `mcpmarket.com` 的虚假列表 |
| `reddit.com/*.rss` 与 `old.reddit.com` | 空 / 登录墙 | **改用 Hermes 自带 `reddit-reading` 技能的 `scripts/reddit.py`**（匿名 Atom 后端，约 1 请求/分钟/IP，遇 429 自动等待重试） |
| `reddit.py thread` | `not a Reddit thread URL` | 需要**完整 URL**，不能只给 post id |
| Reddit 匿名后端 | 无点赞数与评论嵌套 | 只拿正文与评论内容；要互动数需注册 Reddit "script" 应用（`REDDIT_CLIENT_ID`/`REDDIT_CLIENT_SECRET`，**是应用注册不是账号登录**） |

---

## 附录 A 证据分级标准

| 等级 | 定义 | 判定依据 |
|---|---|---|
| **A 已核实** | 本机源码/官方仓库 API 直读，可用命令复现 | `grep`/`sed` 输出、API JSON 响应、HTTP 状态码 |
| **B 项目/官方文档原文** | 项目 README 或官方文档逐字内容 | 引号内的原文引用 |
| **C 项目自述未复现** | 项目自述的性能数字、覆盖范围 | 有原文但无独立验证 |
| **D 本报告推断** | 基于现有证据的推理 | 明确标注"推断" |

---

## 附录 B 本报告使用的可复现命令

```bash
# ── 本机 Hermes 事实核验 ──
echo $HERMES_HOME
cd "$HERMES_HOME/hermes-agent" && git log -1 --format="%h %ad" --date=short
ls "$HERMES_HOME/../optional-mcps" 2>/dev/null | wc -l
find "$HERMES_HOME/hermes-agent/optional-skills" -name SKILL.md | wc -l
find "$HERMES_HOME/hermes-agent/skills" -name SKILL.md | wc -l
ls "$HERMES_HOME/hermes-agent/plugin-catalog"/*.yaml | wc -l
grep -n "_MCP_HARD_RESULT_CAP_CHARS" "$HERMES_HOME/hermes-agent/tools/mcp_tool_content.py"
grep -n -A25 "HARDLINE_PATTERNS" "$HERMES_HOME/hermes-agent/tools/approval_detection.py"
grep -n "memory_char_limit" "$HERMES_HOME/hermes-agent/hermes_cli/config_defaults.py"

# ── 仓库/文件存在性探测（最可靠的方法）──
curl -sL -o /dev/null -w "%{http_code}\n" \
  "https://raw.githubusercontent.com/github/awesome-copilot/main/skills/fedora-linux-triage/SKILL.md"

# ── awesome-copilot 发行版矩阵：三类资源 × 七个发行版（一次跑完）──
BASE=https://raw.githubusercontent.com/github/awesome-copilot/main
for d in arch fedora debian centos ubuntu rhel opensuse; do
  for p in "instructions/$d-linux.instructions.md" \
           "skills/$d-linux-triage/SKILL.md" \
           "agents/$d-linux-expert.agent.md"; do
    printf "%s  %s\n" "$(curl -sL -o /dev/null -w '%{http_code}' "$BASE/$p")" "$p"
  done
done
# 预期：arch/fedora/debian/centos = 200 200 200；ubuntu/rhel/opensuse = 404 404 404

# 目录树核验（防止漏掉 instructions/ 与 plugins/ 这两类）
curl -s "https://api.github.com/repos/github/awesome-copilot/git/trees/main?recursive=1" \
  | grep -o '"path": "[^"]*"' | grep -iE '(linux|fedora|debian|ubuntu|centos|rhel|suse)'

# ── Red Hat 官方 Linux MCP（第 7 章 §7.1 的全部依据）──
curl -s "https://api.github.com/repos/rhel-lightspeed/linux-mcp-server"        # 317★ / Apache-2.0
curl -sL "https://pypi.org/pypi/linux-mcp-server/json" | head -c 400           # 1.7.0
curl -sL "$BASE/../../../rhel-lightspeed/linux-mcp-server/main/src/linux_mcp_server/commands.py"
curl -sL "https://raw.githubusercontent.com/rhel-lightspeed/linux-mcp-server/main/docs/security.md"
curl -sL "https://raw.githubusercontent.com/rhel-lightspeed/linux-mcp-server/main/docs/guarded-command-execution.md"
curl -sL "https://raw.githubusercontent.com/rhel-lightspeed/linux-mcp-server/main/src/linux_mcp_server/auth_policy.py"

# ── openSUSE 官方 org 是否有其他 AI/MCP 仓库 ──
curl -s "https://api.github.com/orgs/openSUSE/repos?per_page=100&sort=updated" \
  | grep -o '"name": "[^"]*"' | sort -u

# ── 包存在性核验 ──
curl -sL "https://pypi.org/pypi/arch-ops-server/json" | python -c "import sys,json;print(json.load(sys.stdin)['info']['version'])"
curl -sL "https://registry.npmjs.org/arch-mcp"          # → {"error":"Not found"}
curl -sL "https://archlinux.org/packages/search/json/?name=arch-wiki-lite"
curl -sL "https://mdapi.fedoraproject.org/f44/pkg/dnf5"
curl -sL "https://sources.debian.org/api/src/needrestart/"

# ── Reddit（用 Hermes 自带脚本）──
cd "$HERMES_HOME/hermes-agent/optional-skills/social-media/reddit-reading/scripts"
python reddit.py doctor
python reddit.py thread "https://www.reddit.com/r/<sub>/comments/<id>/<slug>/" --limit 30
```

---

## 附录 C 参考来源（全量）

### C.1 Hermes Agent 官方（本机仓库与文档）

1. `NousResearch/hermes-agent` — 官方仓库（本机 origin）
2. `website/docs/user-guide/which-file-does-what.md` — SOUL/USER/MEMORY/AGENTS 权威对照
3. `website/docs/user-guide/profiles.md` — profile 语义
4. `website/docs/user-guide/features/memory.md` — 2200/1375 字符上限
5. `website/docs/user-guide/features/memory-providers.md` — provider 对比
6. `website/docs/user-guide/features/mcp.md` — trust 模型、工具过滤
7. `website/docs/reference/mcp-config-reference.md` — MCP 配置参考
8. `website/docs/reference/optional-skills-catalog.md` — 152 个可选技能全表
9. `website/docs/getting-started/nix-setup.md` — NixOS 模块、`mcpServers`、sops-nix
10. `website/docs/user-guide/security.md` — 审批模式、硬阻断清单、Tirith
11. `website/docs/developer-guide/creating-skills.md` — SKILL.md 格式规范
12. `website/docs/guides/migrate-from-openclaw.md` — OpenClaw 配置映射
13. `tools/approval_detection.py` — **`HARDLINE_PATTERNS` 实际位置**
14. `tools/mcp_tool_content.py` — `_MCP_HARD_RESULT_CAP_CHARS` / `_truncate_mcp_text_result`
15. `hermes_cli/config_defaults.py` — 记忆上限等默认值
16. `optional-skills/social-media/reddit-reading/` — Reddit 抓取后端

### C.2 通用基座与跨发行版 MCP

17. `openSUSE/systemd-mcp` — systemd MCP（MIT，Go，v0.3.5，polkit/OAuth2 双授权）
18. `gilby125/mcp-proxmox`（53★）、`ry-ops/proxmox-mcp-server`（27★）、`bsahane/mcp-proxmox`（21★）
19. `manusa/podman-mcp-server`（84★）、`elusznik/mcp-server-code-execution-mode`（340★）、`Kiln-AI/Kilntainers`（51★）
20. `muchiny/bridge-mcp`（10★）、`Cosmicjedi/linux-administration-mcp`、`E13ctr0N/AiSysAdmin`
21. `Higangssh/homebutler`（300★）、`initMAX/zabbix-mcp-server`（229★）、`SikamikanikoBG/homelab-monitor`（218★）、`tyxak/remotepower`（74★）、`bjeans/homelab-mcp`（43★）
22. `sibilleb/AAP-Enterprise-MCP-Server`（33★）、`bsahane/mcp-ansible`（30★）、`jade-pico/antrieb-mcp-server`（14★）
23. `atraxsrc/claude-revoke`（3★）— 审计并撤销 Claude Code 在 Linux 上的授权
24. `docker/mcp-gateway` — Docker 官方 MCP Gateway
25. `grafana/mcp-grafana` — Grafana 官方 MCP

### C.3 NixOS

26. `utensils/mcp-nixos` / `mcp-nixos.io` — NixOS 包与选项查询 MCP
27. `SecBear/nix-sandbox-mcp` — jail.nix 沙箱 MCP
28. `andersonjoseph/jailed-agents` — Nix 安全沙箱
29. `xNaXDy/nix-bwrapper`、`himuxhehe/ai-jail`
30. `YPares/rigup.nix` — Nix 模块系统组织 agent 指令
31. `michalzubkowicz/nixos-management-skill` — 纯 Markdown NixOS 操作手册
32. `JEFF7712/nix-agent`、`Comprehensive-Art207/nix-infra`
33. `knoopx/pi`、`sielicki/codemcp`、`halfwhey/nix-playwright-nightly`
34. `jail.nix`（`git.sr.ht/~alexdavid/jail.nix`）、`astro/microvm.nix`
35. r/NixOS `1souuw7`（`u/qmic` 上千台服务器实践报告）、`1jjv62s`（mcp-nixos 作者）、`1tzcit5`（本地 LLM 实测）、`1r0c1sv`（nix-sandbox-mcp）、`1rh500t`（jailed-agents）、`1qgkyrw`（rigup.nix）、`1mmg38s`、`1rmn2lq`、`1s1z9l8`、`1rod9ji`、`1s6ubny`、`1vyxjc7`、`1vxu1kj`、`1ky1ix9`、`1lqr4p6`、`1pkrpx5`
36. NixOS Discourse — `77238`（Local AI agent for NixOS configuration）、`72275`、`65168`（nixai 归档）

### C.4 Arch

37. `nihalxkumar/arch-mcp` — Arch Linux MCP（PyPI `arch-ops-server`）
38. `egarcia74/arch-wiki-mcp` — Arch Wiki MCP / Truth Perimeter
39. `iht/arch-mcp` — 2026-08-08 fork（0★，用于核实文档链接漂移）
40. `herraiz-org/ai-skills` — `update-arch-system` + `install-aur-package`
41. `enihcam/aur-skills` — 10 个 AUR 打包技能（含中文 README）
42. `IPauloGermano/arch-agent-skill` — 桌面环境向
43. `indyfive11/archward`、`codexspidey/archsafe`（已弃坑）
44. Arch 官方包：`arch-wiki-lite`、`arch-wiki-docs`、`informant`、`arch-audit`、`pacman-contrib`；AUR：`downgrade`、`paru`
45. r/archlinux `1vaxtcs`（200+ 恶意 AUR 包）、`1orwi2b`（Claude Code 学 Arch）、`1vd5mg3`、`1vk2lwx`
46. `aur-general@lists.archlinux.org` — AUR 安全上报渠道
47. `aurwatch.org/api/v1/check`、`aur-audit.wtako.net`（第三方）

### C.5 Fedora / Debian / Ubuntu

48. `simonives/redwrench` — Rust 策略引擎 Fedora MCP
49. `amineutron/fedora-agents` / npm `fedora-agents-mcp`
50. `copyninja/debsecan-mcp` → PyPI `debvulns`
51. `pazuzu1w/ubuntu_mcp_server` — 44★，2025-06-29 停更
52. Fedora 官方文档 — `docs.fedoraproject.org/en-US/quick-docs/autoupdates/`
53. `packages.fedoraproject.org` / `mdapi.fedoraproject.org` — 包存在性与版本核验
54. `sources.debian.org/api/` — Debian 包版本与 suite 核验
55. Ubuntu 官方 — `ubuntu.com/security/livepatch/docs/`、Landscape Livepatch 教程、Pro Client 文档
56. r/Fedora `1szch0g`（Kinoite 不可变）、`1w190ij`（Claude Desktop 只有 .deb）、`1u2msrz`（AI agent 失控）
57. r/debian `1vgkg7v`（apt upgrade 后 SDDM 坏，靠 Claude 修）
58. r/Ubuntu `1t0e4di`（从 Arch 回 Ubuntu，CUDA 栈是原因）

### C.6 技能与市场

59. `github/awesome-copilot` — 发行版专家矩阵（**整合阶段修正为 4 类资源路径**）：`instructions/{arch,fedora,debian,centos}-linux.instructions.md`、`skills/{arch,fedora,debian,centos}-linux-triage/SKILL.md`、`agents/{arch,fedora,debian,centos}-linux-expert.agent.md`；`plugins/arch/`（⚠️ 是"软件架构"插件，非 Arch Linux）；ubuntu / rhel / opensuse 全部 404
60. `clawhub.ai/skills?q={fedora,debian,ubuntu,arch,pacman,nixos}`
61. `skills.sh` — The Open Agent Skills Ecosystem
62. `aur.archlinux.org/rpc/v5/search/mcp` — AUR MCP 生态（282 结果）

### C.7 安全事件与 CVE

63. **CVE-2026-84289** — Hermes Agent MCP 内存放大 DoS（≤0.18.2，修复 0.20.5）
64. **CVE-2026-59822** — LiteLLM MCP 鉴权绕过（修复 1.84.0，CISA KEV）
65. **CVE-2026-42271** — LiteLLM MCP-bridge 子进程命令注入（修复 1.83.7，CISA KEV）
66. **CVE-2026-9198** — Langflow `auto_login` 未鉴权签发 SUPERUSER JWT（CISA KEV）
67. **CVE-2026-48710** — Starlette Host-header（与上者串联）
68. **CVE-2026-65105** — NemoClaw Ollama 模板投毒
69. **Deadbugz**（2026-08）— 恶意 MCP server 供应链投毒
70. **GuardFall** — 几十年历史的 bash 技巧打穿 AI coding agent
71. **GitSpawn** — 7 个 AI 编码 agent 被一个 git 配置劫持
72. **RovoBlast** — Atlassian Rovo 单 URL 参数劫持（DEF CON 34 / Varonis）
73. **Cryptographic Context Injection**（Adversa AI）
74. **DNS-AID**（Linux Foundation）
75. r/linuxadmin `1unxuvf`、`1w5yvf5`、`1vl6ofz`、`1vm56v9`、`1vu37hc`、`1ts0gip`
76. CISA KEV 同批次：Starlette / Kestra / Artifactory / Switchvox / SonicWall SMA 1000
77. `linearuncle/codex-agentguard` — 拦截 agent 的 `rm -rf`

### C.8 前序分轮报告（本工作区）


78. `research_report_hermes_openclaw_linux_ops.md` — 第一轮（框架机制）
79. `research_report_nixos_ai_agent_ecosystem.md` — 第二轮（NixOS）
80. `research_report_arch_ai_ops_ecosystem.md` — 第三轮（Arch）
81. `research_report_fedora_debian_ubuntu_ai_ops.md` — 第四轮（Fedora/Debian/Ubuntu）
82. `kb/hermes-openclaw-linux-ops-agent-stack.md` — 知识库沉淀（v4）

### C.9 整合阶段补充来源（v1.1，全部 A 级）

83. **`rhel-lightspeed/linux-mcp-server`** — Red Hat 官方 Linux MCP（Apache-2.0，Python，**317★ / 67 forks**，2025-10-15 创建，2026-10-10 活跃）；PyPI `linux-mcp-server` v1.7.0；官方 "MCP Server for RHEL" 的内核
84. `rhel-lightspeed/linux-mcp-server` → `docs/index.md`、`docs/security.md`、`docs/guarded-command-execution.md`、`docs/ssh.md`、`docs/config-reference.md`、`docs/keycloak.md`、`docs/architecture.md`
85. `rhel-lightspeed/linux-mcp-server` → `src/linux_mcp_server/commands.py`（`CommandSpec` 硬编码命令表 + `fallback`）、`auth_policy.py`（`PolicyRule` / `PolicyAction`）、`audit.py`、`gatekeeper/check_run_script.py`（Gatekeeper 提示词与硬编码策略）、`tools/`（services / processes / logs / network / storage / system_info / pcp / run_script）
86. Red Hat 官方文档 — `docs.redhat.com` RHEL 10《Using the RHEL MCP Server to enable AI assistants to run, discover, and troubleshoot complex issues》
87. `rhel-lightspeed/okp-mcp`（19★，Red Hat Offline Knowledge Portal MCP）、`rhel-lightspeed/redhat-status-mcp`（2★）、`rhel-lightspeed/docs2db-mcp-server`（4★）
88. `openSUSE/systemd-mcp` — 元数据补录：**10★**，Go，MIT，最近推送 2026-09-24，默认分支 `main`
89. `openSUSE` 组织仓库清单（前 100）— `snapper`（1177★）、`open-build-service`（1083★）、`libsolv`（610★）、`zypper`（495★）、`transactional-update`（142★）、`opensuse-migration-tool`（66★）；**无其他 MCP / AI 仓库**
90. `velopulent/tako`（2★，Go，AGPL-3.0，2026-08-13 创建，2026-09-21 活跃）— 自托管 Linux 管理面板，PAM 登录 + 三角色分进程隔离，覆盖 8 个发行版
91. `narmaku/linux-mcp-server-archived`（MIT，**已归档** 2025-10-16）— 唯一的 RHEL 专属社区 MCP，创建 13 天后归档
92. `lioilsources/LeapDoctor`（0★，Go，**无许可证**，2026-02-21 创建，2026-02-22 最后推送）— openSUSE Leap 16 专属 MCP，实质停滞
93. `anjupathak03/zypper-mcp`（0★，**无许可证**，2025-12-21 单日提交）— zypper MCP，不可用
94. `tommy-k/mcp-servermigrate`（0★）、`cu0001/aix-rhel-mcp-server`（0★）— RHEL 系迁移 MCP，未成熟

---

## 附录 D 勘误表

**本次整合过程中，对前序报告逐项复核，发现并修正以下 10 处错误：**

> v1.1 追加了第 8–10 条——它们全部来自"**用全量目录树替代抽样探测**"和"**换组织名重搜**"这两个动作。**前 7 条是细节错误，后 3 条是覆盖错误（更严重）。**

| # | 前序报告的错误表述 | 实际核实结果 | 影响 | 核实方法 |
|---|---|---|---|---|
| 1 | 本机 commit 日期为 **2026-10-01** | 实际是 **2026-09-29**（commit `4e7403130e`，subject: "fix(agent): redact the failed-turn error card before it reaches the durable store"） | 版本基准表述 | `git log -1 --format="%h %ad" --date=short` |
| 2 | 配置片段写 `npx -y arch-mcp` | **npm 上不存在 `arch-mcp` 包**（`registry.npmjs.org/arch-mcp` → `{"error":"Not found"}`）。正确安装是 **`uvx arch-ops-server`**（PyPI） | 第一轮报告的 MCP 配置片段**不可用** | npm registry JSON API |
| 3 | `config.yaml` 位置写作 `~/.hermes/config.yaml` | 实际在 **`$HERMES_HOME`**（本机 = `C:\Users\Admin\AppData\Local\hermes\config.yaml`）。`~/.hermes/` 不存在 | 配置路径指引 | `echo $HERMES_HOME` + `ls` |
| 4 | 表述为 "`config.yaml` 有 `memory_char_limit: 2200`" | **这两个值不在 config.yaml**，是**代码默认值**（`hermes_cli/config_defaults.py:1321-1322`）。本机 `memory:` 段只有 `memory_enabled` / `user_profile_enabled` | 容易误导用户去找不存在的配置项 | `grep -rn memory_char_limit --include="*.py"` |
| 5 | 硬阻断清单在 `tools/approval.py::UNRECOVERABLE_BLOCKLIST` | **该常量在本机不存在**。实际是 **`tools/approval_detection.py` 的 `HARDLINE_PATTERNS`**（12 条），另有 `tools/approval_floors.py`。官方文档引用已过期 | 定位代码时找不到 | `grep -rn "HARDLINE_PATTERNS"` |
| 6 | 第一轮："Reddit 不可直连（返回空 / 登录墙）" | **结论错误**：直接抓 `.rss` 确实失败，但 **Hermes 自带的 `reddit-reading` 技能脚本可用**（匿名 Atom 后端）。已在 v2/v3 纠正 | 曾导致第二轮前所有 Reddit 数据缺失 | 实跑 `reddit.py doctor` → `anonymous_feed: ok` |
| 7 | 第一轮/第二轮：`arch-wiki-mcp` README 404 → 判为"默认分支可能不是 main" | **真实原因是默认分支就是 `master`**。换分支名后抓取成功 | 曾把可用项目误判为不可用 | 换分支名重试 + GitHub API 确认 |
| 8 | `awesome-copilot` 矩阵只探测了 `skills/` 与 `agents/` 两类路径，据此记 Arch "只有 agent、无技能" | 该仓库实际有 **4 类**资源路径：`instructions/`、`skills/`、`agents/`、`plugins/`。**Arch 三类俱全**（instructions 1,355 B + skill 930 B + agent 2,009 B），且**漏掉了 CentOS**（同样三类俱全） | §3.2 与 §6.5 的矩阵**不完整且有一处错误** | 拉 `git/trees/main?recursive=1` 全量目录树 + 逐路径 HTTP 探测 |
| 9 | 把 `openSUSE/systemd-mcp` 当作唯一的"厂商官方执行层" | **Red Hat 官方 `rhel-lightspeed/linux-mcp-server` 同样存在**：**317★**（systemd-mcp 的 31.7 倍）、Apache-2.0、固定只读工具集、SSH 多机、日志白名单，并且**就是官方 "MCP Server for RHEL" 的内核** | 第 7 章缺了**本轮最有价值的单个发现**；摘要、选型图、最小可行栈均需改写 | GitHub 搜索 `mcp server rhel` + GitHub API + 官方 `docs/index.md` 原文 |
| 10 | 前四轮检索 RHEL 系 MCP 时得出"无可用的发行版专属项目" | 社区侧确实如此（唯一 RHEL 专属 MCP `narmaku/linux-mcp-server-archived` **已归档**，创建 13 天后停止），但**官方侧有成熟项目**。盲区成因：只搜了 `org:redhat` 与通用关键词，**未搜 `rhel-lightspeed` 组织** | 结论方向性偏差——把"社区没有"误当成"不存在" | `curl "https://api.github.com/search/repositories?q=mcp+server+rhel+in:name,description&sort=stars"` |

**另有五处"表述不准确但非错误"，一并澄清：**

| # | 表述 | 澄清 |
|---|---|---|
| 8 | "Arch 侧 `informant` 是 AUR 包" | 实际在**官方 `extra` 仓库**（`extra/any`，0.6.0-2）。同样 `arch-wiki-lite`、`arch-audit`、`pacman-contrib` 都在官方仓库，只有 `downgrade`、`paru` 在 AUR |
| 9 | "MCP 结果溢出阈值" 未给出具体值 | 实测为 **50,000 字符**（`config.yaml` 第 783-789 行），比通用的 100K 默认**更严** |
| 10 | `awesome-copilot` 的 `plugins/arch/` | ⚠️ **命名陷阱**：它是"**architecture**（软件架构）与现代化工具包"——`plugin.json` 的 description 原文是 *"Architecture and modernization toolkit"*，装的是 `arch:doc-and-modernize` 技能，**与 Arch Linux 无关**。在该仓库用 `arch` 做关键词搜索，大部分命中是软件架构 |
| 11 | `openSUSE/systemd-mcp` 的 star 数 | 前序报告未记录，实测 **10★**（不是高星项目）。它的价值在**厂商官方 + 默认禁写 + polkit 授权**，不在热度；热度最高的是 Red Hat 那个（317★） |
| 12 | "Ubuntu 在技能市场最丰富" | 结论成立（ClawHub 10+ 件），但必须补一句：**Ubuntu 是五家里唯一在 `awesome-copilot` 零覆盖的**（instructions / skills / agents 三类全部 404）。**技能市场的丰富度 ≠ 官方专家库的覆盖度，两者不能互相替代** |

---

## 附录 E RHEL 系与 openSUSE：覆盖边界补充（v1.1 新增）

> 原始需求只点了 NixOS / Arch / Fedora / Debian / Ubuntu。但整合阶段发现 **RHEL 系有一个此前完全漏掉的、规模最大的厂商官方方案**，且 openSUSE 是 `systemd-mcp` 的来源。故补此附录，**并明确标出哪些已核验、哪些没有**。

### E.1 RHEL 系的官方 AI 线：`rhel-lightspeed` 组织全貌（A 级，GitHub API）

Red Hat 把 RHEL 的 AI 工作集中在一个组织下。**20 个仓库全表**（按 star 排序）：

| Stars | 仓库 | 语言 | 许可证 | 最近推送 | 状态 | 作用 |
|---|---|---|---|---|---|---|
| **317** | **`linux-mcp-server`** | Python | Apache-2.0 | 2026-10-10 | 活跃 | **只读 Linux 运维 MCP**（见 §7.1） |
| 48 | `docs2db` | Python | Apache-2.0 | 2026-10-11 | 活跃 | 文档入库（RAG 数据管道） |
| 44 | **`command-line-assistant`** | Python | Apache-2.0 | 2026-10-06 | 活跃 | **Red Hat 官方 AI 命令行助手**（2024-10-17 创建，docs 在 readthedocs） |
| 19 | **`okp-mcp`** | Python | Apache-2.0 | 2026-10-12 | 活跃 | **Red Hat Offline Knowledge Portal MCP**（= RHEL 系的"离线知识层"） |
| 8 | `sysadmin-agents` | Python | Apache-2.0 | 2026-07-06 | **已归档** | sysadmin agent 实验，已停止 |
| 6 | `docs2db-api` | Python | Apache-2.0 | 2026-10-11 | 活跃 | 上述 RAG 的 API |
| 5 | `goose-proxy` | Python | Apache-2.0 | 2026-10-12 | 活跃 | Goose 代理 |
| 4 | `goose` | Shell | — | 2026-10-02 | 活跃 | Block 的 Goose fork |
| 4 | `docs2db-mcp-server` | Python | Apache-2.0 | 2026-07-30 | 活跃 | 文档 RAG 的 MCP 前端 |
| 2 | `redhat-status-mcp` | Python | Apache-2.0 | 2026-07-06 | **已归档** | Red Hat 服务状态 MCP |
| 1 | `rhel-lightspeed-gitops` | — | MIT | 2026-07-06 | **已归档** | GitOps 实验 |
| 0 | `HEAL` / `roz` / `pypi-cla` / `ci-container` / `roadmap-ci-container` / `renovate-config` / `coderabbit` / `rhel-cla-installer` | Python 等 | 混合 | 2026-10 | 部分 | 基础设施与实验 |
| 0 | `textprep` | Python | Apache-2.0 | 2024-11-11 | **已归档** | 文本预处理 |

**三条可操作结论：**

1. **RHEL 用户的知识层不用自己造。** `okp-mcp`（Offline Knowledge Portal MCP）就是 RHEL 版的 `arch-wiki-lite` 角色——把官方文档变成 agent 可查的离线知识源。**这与本报告第 8 章"知识库文件优先"的结论不冲突**：它解决的是"发行版官方文档"这一层，不是"你的本机经验"那一层。
2. **`command-line-assistant`（44★）值得单独关注**——这是 Red Hat 官方的 AI CLI 助手（与 MCP 不同路线：直接在终端里对话）。**本报告未深入其架构，仅记录存在与活跃度。**
3. **20 个仓库里 4 个已归档**（`sysadmin-agents`、`redhat-status-mcp`、`rhel-lightspeed-gitops`、`textprep`）。厂商官方 ≠ 长期维护——**引用厂商项目同样要看 `archived` 标志**。

### E.2 RHEL 系的技能/专家覆盖（A 级，HTTP 探测）

| 来源 | RHEL | CentOS | Rocky | Alma |
|---|---|---|---|---|
| `awesome-copilot` `instructions/` | ❌ 404 | ✅ 1,329 B | ❌ 404 | ❌ 404 |
| `awesome-copilot` `skills/*-linux-triage/` | ❌ 404 | ✅ 959 B | ❌ 404 | ❌ 404 |
| `awesome-copilot` `agents/*-linux-expert.agent.md` | ❌ 404 | ✅ 2,059 B | ❌ 404 | ❌ 404 |
| ClawHub（平台自报，**B 级**） | — | ✅ `awesome-copilot/centos-linux-triage`（8.8k） | — | — |

> **一个值得注意的错位**：`awesome-copilot` 覆盖 CentOS 却**不覆盖 RHEL / Rocky / Alma**。也就是说，**这套社区库是按"社区常见度"选型的，不是按"企业装机量"**。RHEL 用户的正解是走 E.1 的官方线，不是等社区库补上。

### E.3 RHEL 系的社区侧：几乎全军覆没（A 级）

| 项目 | Stars | 许可证 | 状态 | 判断 |
|---|---|---|---|---|
| `narmaku/linux-mcp-server-archived` | 0 | MIT | **已归档**（2025-10-16，创建于 2025-10-03） | **唯一的 RHEL 专属社区 MCP，活了 13 天** |
| `velopulent/tako` | 2 | AGPL-3.0 | 活跃（2026-09-21） | 自托管面板，覆盖 RHEL/Rocky/Alma；**自述尚未到 v1** |
| `tommy-k/mcp-servermigrate` | 0 | — | — | RHEL/Fedora 迁移 MCP，未成熟 |
| `cu0001/aix-rhel-mcp-server` | 0 | — | — | 无描述 |

**结论：RHEL 系的"专属 AI 运维"完全由厂商官方承担，社区侧没有可用项目。** 这与 Arch（社区活跃、官方无 AI 动作）恰好相反。

### E.4 openSUSE / SUSE（A 级）

**唯一的官方 AI 产物就是 `systemd-mcp`**（10★，Go，MIT，2026-09-24 推送）。`openSUSE` 组织前 100 个仓库里**没有第二个 MCP / AI 仓库**。

它的运维基座（官方仓库，非 AI，但 agent 会用到）：

| 项目 | Stars | 语言 | 作用 |
|---|---|---|---|
| `snapper` | **1,177** | C++ | **Btrfs 快照与回滚**——openSUSE 的"事务性更新"底座，也是 agent 改配置前最该先建的东西 |
| `open-build-service` | 1,083 | Ruby | OBS 构建服务 |
| `libsolv` | 610 | C | 依赖求解器（`zypper` 的引擎） |
| `zypper` | 495 | C++ | 包管理器 |
| `transactional-update` | 142 | C++ | **事务性系统更新**（MicroOS / Leap Micro 的核心机制） |
| `opensuse-migration-tool` | 66 | Shell | 发行版迁移 |

**openSUSE 专属 MCP / 技能：全部为 0。**

| 项目 | Stars | 许可证 | 状态 |
|---|---|---|---|
| `lioilsources/LeapDoctor` | 0 | **无许可证** | Leap 16 专属；2026-02-21 创建，**2026-02-22 最后推送**（一天后停更） |
| `anjupathak03/zypper-mcp` | 0 | **无许可证** | 2025-12-21 单日提交 |

> ⚠️ **两个都是"无许可证"**——法律上默认保留全部权利，**不可用于生产**。不要因为"没有别的选择"就用它。

**SUSE Linux Enterprise（SLE）侧：本报告完全未覆盖。**

### E.5 RHEL 系运维基座：**未核验**（D 级，明确标注）

下表是 RHEL 系运维的常规构成，**本轮未逐项 API 核验**（`redhat/leapp`、`redhat/insights-client` 均返回 404，说明这些组件不在 GitHub 的 `redhat` 组织下），故仅作方向提示：

| 能力 | 常规工具 | 状态 |
|---|---|---|
| 自动更新 | `dnf-automatic`（RHEL 基础仓库） | **未核验** |
| 重启检测 | `dnf needs-restarting`（`dnf-plugins-core`） | 与 Fedora 同源，**未在 RHEL 上核验** |
| 强制访问控制 | **SELinux**（RHEL 系默认 enforcing） | 未核验 |
| 漏洞/合规 | `dnf updateinfo`、OpenSCAP / `oscap`、`insights-client` | **未核验** |
| 大版本升级 | `leapp`（RHEL 7→8→9→10 官方升级路径） | **未核验**；注意它在 RHEL 官方仓库而非 GitHub `redhat` 组织 |
| 订阅与补丁 | `subscription-manager`、Satellite | **未核验** |

**要落地 RHEL 运维，这张表必须自己补核验。** 本报告不为此背书。

### E.6 覆盖边界小结

| 发行版 | 官方 AI 动作 | 社区 AI 运维 | `awesome-copilot` | 本报告核验深度 |
|---|---|---|---|---|
| **NixOS** | 官方 Hermes module；无官方 MCP | **活跃**（沙箱层 7+ 项目） | ❌ | A（第 4 章） |
| **Arch** | 无（但有 `arch-wiki-lite` 等基座包） | **活跃**（2 个 MCP + 3 个技能仓库） | ✅ 3 类 | A（第 5 章） |
| **Fedora** | openSUSE `systemd-mcp` 可用 | 活跃（`redwrench`、`fedora-agents`） | ✅ 3 类 | A（第 6 章） |
| **Debian** | 无 | 活跃（`debvulns`） | ✅ 3 类 | A（第 6 章） |
| **Ubuntu** | 无 | **最活跃**（ClawHub 10+） | **❌ 0 类** | A（第 6 章） |
| **RHEL 系** | **最强**（`linux-mcp-server` 317★ + `okp-mcp` + `command-line-assistant`） | **几乎为零**（唯一专属 MCP 已归档） | ✅ 仅 CentOS | **A（本附录）**，运维基座 D |
| **openSUSE** | `systemd-mcp`（10★） | **几乎为零**（2 个 0★ 无许可证项目） | ❌ | **A（本附录）** |
| **SLE / Rocky / Alma / WSL / Windows** | — | — | — | **未覆盖** |

---

## 结语：三条最该记住的

1. **执行层用厂商官方做的，知识层用发行版专属的。** 执行层优先 **Red Hat 的 `linux-mcp-server`**（317★，固定只读工具集 + SSH 多机，RHEL 系已由官方背书）+ **openSUSE 的 `systemd-mcp`**（10★，systemd C API 直连，默认禁写）；发行版专属的东西放在知识层（`mcp-nixos` / `arch-wiki-lite` / `debvulns` / `okp-mcp`）和审计层（AUR 审计 / `redwrench` 策略引擎）。
2. **知识库用文件，不要用 MCP。** Hermes 原生 `llm-wiki` 零安装；Arch 还能再叠一层官方 `arch-wiki-lite` 离线 Wiki，RHEL 叠 `okp-mcp` 离线知识门户。RAG 在运维场景是负收益。
3. **安全边界不是"选了个好 agent"，是"默认禁写 + 显式提权 + 审计含被拒调用 + 元数据漂移监控"。** GuardFall 和 Deadbugz 都证明：**一次性的审查和静态的信任判断都会失效。** 反面教材也在本报告里：唯一那个 RHEL 专属社区 MCP 活了 13 天就归档，openSUSE 仅有的两个项目连许可证都没有——**"厂商官方"这个属性本身也是有价值的证据。**

---

*报告完 · v1.1 · 2026-10-12 · 所有事实均可通过附录 B 的命令复现 · 勘误记录见附录 D*
