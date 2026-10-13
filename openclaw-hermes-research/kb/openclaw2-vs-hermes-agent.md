---
id: openclaw2-vs-hermes-agent
title: OpenClaw 2.0 vs Hermes Agent 深度对比（记忆/自进化/纠错/故障率/Arch-NixOS/按OS安装配置）
tags: [openclaw, hermes-agent, ai-agent, memory, self-evolution, reliability, nixos, arch, install, docker, windows, macos]
created: 2026-10-13
updated: 2026-10-13
version: 1.1.0
status: stable
source: 本次会话实测调研（官方文档/GitHub issues/AUR 实测/社区分析）
confidence: 已核实（官方一手来源）；社区感受类数据为单一来源转引
---

# OpenClaw 2.0 vs Hermes Agent 深度对比

**TL;DR**：两者正收敛于"有界核心+可扩展外延"，但风险结构相反——OpenClaw 2.0（v2026.8.1, 2026-08-31）记忆/技能治理强、生态大，代价是高频发版的回归密度（regression 标签累计 3,200+，社区自述约 25% 更新打挂集成）；Hermes Agent（Nous Research, 2026-02, MIT）记忆自动、进化闭环完整、任务级回滚领先，代价是自评估虚高会把错误固化为技能、低频发版未经同规模验证。Arch/NixOS 结论镜像互补：NixOS 声明式党选 OpenClaw+nix-openclaw（不可变模式+秒回滚），Arch 轻量党选 hermes-agent（AUR 当日更新、7 票）。

## 项目基线（对齐 2026-10-13）

| 项 | OpenClaw | Hermes Agent |
|---|---|---|
| 最新大版本 | 2.0 = v2026.8.1（2026-08-31） | 持续小版本，v0.21.7（2026-10-12） |
| 技术栈 | Node.js（AUR 为 npm tarball） | Python 3.10+/uv（AUR 带 uv+nodejs 依赖） |
| 治理方 | 开源社区+官方团队 | Nous Research |
| 发版节奏 | 约每 1-2 周；2.0 前 230 天 106 版 | 低频；截至 2026.5.8 仅 11 版 |
| 2.0 规模 | 933 贡献者/16,000+ PR（官方口径；另有媒体口径 987/16,977） | — |

## 记忆系统

| 维度 | Hermes | OpenClaw 2.0 |
|---|---|---|
| 核心结构 | MEMORY.md 2,200 字符 + USER.md 1,375 字符硬上限；超限返回错误强制 Agent 合并—删除—写入 |  dreaming 后台巩固 + Dream Diary + 来源追溯 |
| 遗忘 | 容量逼出的主动遗忘 | `openclaw memory forget`（派生层可忘、原始对话保留） |
| 检索 | L1 冻结快照注入 system prompt（护 prefix cache）+ L2 SQLite FTS5 会话搜索（~20ms，`~/.hermes/state.db`）+ 8 个外部记忆 provider | 2.0 起内置记忆统一检索路径；会话存储 2.0 才迁 SQLite（降级需备份） |
| 写入安全 | 写入前扫描 prompt 注入/凭据/SSH 后门/不可见 Unicode | secret 经掩码提示请求、不进模型上下文 |
| 新暴露面 | — | v2026.9.2：共享 Gateway 下 agent 可读其他 agent 会话，互不信任用户须拆 Gateway |

## 自进化

- Hermes：四支柱（Curated Memory/Skills/Nudge+后台 Review/Honcho）；SKILL.md 兼容 agentskills.io；`skill_manage` create/patch；`/learn`；linter 只警告不拦截；`write_approval` 默认 false（开启后暂存 `~/.hermes/pending/skills/` 逐条审批）；离线 GEPA 管线（DSPy+GEPA，五阶段仅 Phase 1 落地，$2-10/次，**永远人工 PR 永不自动 commit**）。
- OpenClaw：Skill Workshop 提案制——agent 只写 PROPOSAL.md，apply 才生效；apply 前重跑扫描器+写回滚元数据；approvalPolicy 默认 auto 可设 pending；自主捕获每次扫描最多 1-3 个提案、永不能执行生命周期操作；ClawHub 技能 13,700+（社区口径：知乎 13,729/阿里云 13,625，两文同源，非官方统计）；Workshop 跨工作区技能持久化到 **v2026.9.3**（1,844 PRs/190 贡献者）才落地——该特性曾被错误挂到 v2026.9.2。
- 互认：OpenClaw 2.0 onboarding 可导入 Claude Code/Codex/Hermes 记忆。

## 纠错（三层框架）

| 层 | Hermes | OpenClaw |
|---|---|---|
| 任务级 | 改文件前快照 + `/rollback`；/retry /undo /compress（OpenClaw 无对应功能——社区公认空白） | 对话分支级回退/分叉；v2026.9.2 中断任务重启恢复、保存失败答案仍可用 |
| 系统级 | `hermes doctor`（诊断） | `doctor --fix`（修复）+ `triage` 脱敏调试包 + Git 定时快照/可验证 SQLite 备份子系统 |
| 治理级 | `write_approval` 暂存审核（默认关） | 操作一次批准、可查可撤销、任务变则重批 |
| 实证缺陷 | 自评估虚高（Reddit +107 赞："总是觉得自己干得对"）→ 错误固化为技能 | 2.0 迁移期"假成功"：凭据归档后仍报成功、行内 secret 被换占位符 |

## 长期故障率（OpenClaw 五类故障模式）

1. **OOM**：#41778（v2026.3.7，not planned 关闭）→ #45064（v2026.3.12 全 CLI OOM）→ #46522 于 v2026.3.13 修复；根因 Node v24 V8 ABI 不兼容，**锁 Node v22.22.1 可解**。
2. **崩溃循环**：2026.9.6 单版本 3 个 P1（#170458 堆多 GB 冻结事件循环 / #170457 禁用插件仍派生子进程 / #170693 迁移文件重扫致 Gateway 启动失败）；2026.10.2 仍有 #170644/#170525。
3. **迁移事故**：#95495（2026.6.9 静默迁移记忆库，据 issue 自述 1,499 文件/23,694 chunks 归零、3.4GB 旧库 vs 128KB 空壳，regression/P1/data-loss，3 天关闭；终审期页面抓取失败，数字未独立复核）。
4. **性能回归**：#170474 sessions.cleanup <1s→~27s（2026.9.9→10.1）。
5. **发布阻塞**：#170545 P0 release-blocker。
- 官方对策：extended-stable 发布线 + "先备份、等一两个补丁"官方建议 + 备份子系统；安全面：6 CVE/341+ 恶意技能/135k+ Shodan 暴露实例（经 Kilo 转引，单一社区来源）。

## Arch/NixOS 落地（2026-10-13 AUR 实测）

| 包 | 版本/日期 | 维护者 | 票 | 备注 |
|---|---|---|---|---|
| openclaw | 2026.9.9-1（10-08 更新） | ralphptorres | 5 | npm tarball，仅 nodejs；比上游滞后约 5 天；ArchWiki 称 AUR 包"存在 bug 且不稳定"，推荐官方 curl 脚本 |
| openclaw-git | 2026.9.6.r100068（09-27） | SolarAquarion | 2 | Bun 源码构建，make 依赖重；bubblewrap 可选 |
| hermes-agent | 0.21.7-3（**当日更新**） | y0uCeF | 7 | 运行依赖 nodejs/npm/python/uv/agent-browser；被 3 个包依赖 |

- NixOS：**nix-openclaw**（一方 Home Manager 模块）= 版本锁定 + `home-manager switch --rollback` + `OPENCLAW_NIX_MODE=1`（openclaw.json 不可变，禁一切自修改命令）+ NIX_PROFILES PATH 自动发现；Hermes 侧 `nix profile install` 给 hermes/hermes-agent/hermes-acp 三命令、运行时无 pip/venv/npm，但无对等不可变语义。
- 资源门槛：OpenClaw 本地模型 **8 GiB 内存底线**（CPU-only 推理可能数分钟）；Hermes 2GB 最低/4GB 推荐、Python 最低 3.10/推荐 3.11+。
- ACP 双栈：hermes-acp + OpenClaw Gateway 已打通（CSDN 2026-09 实操）。

## 按 OS 安装配置（2026-10-13 核验，v1.1.0 新增）

完整可粘贴命令见交付件 `openclaw-hermes-os-install-guide.md`（NixOS→Arch→其他 Linux→macOS→Windows→WSL2→Docker→Termux 八节）。核心新结论：

| 主题 | 结论 |
|---|---|
| OpenClaw 运行时门槛 | v2026.9.3 起 Node `>=24.16.0 <25 \|\| >=26.1.0`（22/23/25 不支持）；RPM 系 Node 链接不安全 SQLite 时安装器保留系统包、自建用户态 Node（`~/.openclaw/tools/cli-node`）；Alpine 官方建议直接用 `node:26-alpine` 容器 |
| Hermes 运行时门槛 | 第一方安装运行于 **Python 3.14**（PM 自管）；`>=3.11,<3.15` 仅为 updater 过渡口径；hermes-agents.net 社区镜像的"3.10/3.11"已过时 |
| Hermes 官方安装形态 | install.sh（POSIX）/ install.ps1（Windows 原生）/ DMG（macOS Apple Silicon only）/ MSIX（Win11 22H2+）/ Docker / Nix（Tier 2）/ Termux APT（aarch64、**当前损坏**）；**AUR、pypi、brew 官方明确不支持** |
| AUR hermes-agent 机制 | `keep-venv-interpreter.patch` 改 `hermes_cli/_launchers.py` 对 pacman 分发返回 None 保持 venv 解释器；`/opt/hermes-agent` + `/usr/bin/hermes` 包装器；`/opt` 只读 + `HERMES_DISABLE_LAZY_INSTALLS=1`；可选 extras 打包时烘焙 |
| Hermes Docker | `nousresearch/hermes-agent`；`/opt/data` 唯一状态源；s6 监管（CMD 是 sleep infinity 心跳，`--no-supervise` 退回旧语义）；网关 8642 / 面板 9119（`HERMES_DASHBOARD=1`，非回环绑定**强制认证门**，`HERMES_DASHBOARD_INSECURE` 已废弃 no-op——源于 2026-06 扫描器种 SSH 后门事件） |
| Docker WAL 坑 | virtiofs（Docker Desktop macOS/OrbStack）与 9p/drvfs（Docker Desktop Windows）上 bind mount 会**静默损坏** WAL 库（integrity_check 都查不出）；v2026.9.14 起新库自动 DELETE 模式，旧库需停机离线转换或换命名卷 |
| Docker 配对坑 | 镜像用 gosu 降权 `hermes`(uid 10000)，`docker exec` 默认 root 建的审批文件 0600 root:root 被**静默忽略**；必须 `docker exec -u hermes`（issue #10270） |
| Hermes Windows 原生 | install.ps1 免管理员；UTF-8 stdio shim（`HERMES_DISABLE_WINDOWS_UTF8=1` 退回）；EDITOR 默认 notepad（VS Code 必须 `code --wait`）；终端走 Git Bash（MinGit 不算）；gateway 自启 = schtasks ONLOGON LIMITED + Startup VBS 兜底 + `pythonw.exe` 分离启动；MSIX 需 Win11 22H2+ |
| OpenClaw Windows | 桌面 app 自带私有 Bun 运行时（**需签名 Windows Bun runtime**，装系统 Node 无效）；Scheduled Task S4U 可登录前运行；**2026.9.4 updater 服务交接留有旧 DB reader，目标 schema>17 激活后回调失败**——需手动包管理流程升级 |
| OpenClaw macOS | .app 需 **macOS 26.2 (Tahoe)+**；Node 24/26 官方二进制需 macOS 13.5+；Bun 路径自动管 Homebrew SQLite |
| WSL2 无人值守 | `dbus-launch true`（非 `/bin/true`，WSL≥2.6.1.0 idle-terminate 回归 #13416）+ `/ru "$env:USERNAME"`（非 SYSTEM，按用户发行版对 SYSTEM 不可见） |
| OpenClaw 守护/OOM | `openclaw gateway install` 渲染 systemd user unit；子进程 `oom_score_adj=1000` 偏置 + unit `OOMPolicy=continue`（不替代内存调优）；`TimeoutStopSec=330` 为 5 分钟 drain 余量 |
| 中文文档滞后 | OpenClaw 中文站 Node 兼容页 v2026.9.3 改口径后仍写旧区间——以英文页/安装器实报为准 |

## 可复用操作

```bash
# OpenClaw on NixOS（声明式，推荐长期运行）
# 1) nix-openclaw flake + programs.openclaw.config（见 github.com/openclaw/nix-openclaw）
# 2) OPENCLAW_NIX_MODE=1 自动生效 → 只能改 Nix 源，回滚:
home-manager switch --rollback

# OpenClaw on Arch（官方路径优先，AUR 备选）
curl -fsSL https://openclaw.ai/install.sh | bash   # 官方脚本（supported path）
# yay -S openclaw  # AUR：版本滞后约 5 天，ArchWiki 预警不稳定

# Hermes on Arch
yay -S hermes-agent    # 当日更新；或官方: curl -fsSL .../install.sh | bash（勿用 sudo）

# Hermes on NixOS/Nix
nix profile install github:...   # 提供 hermes / hermes-agent / hermes-acp
```

**升级纪律（OpenClaw 长期运行）**：升级前经验证备份（SQLite 会话库）→ 锁 Node v22.22.1 →  heartbeat/cron 外部探活 → 生产用 extended-stable → 每次更新预设约 25% 集成中断概率 → 更新后 `openclaw doctor`。

## 坑与反直觉

1. **腾讯云那篇"8 维度实测"是 AI 生成文**：描述 OpenClaw 为 Python/RabbitMQ/ChromaDB 栈、Hermes v2.4.1/4.2k stars，与官方一手事实全面冲突——凡引用其二手数据的文章都不可信。
2. **Workshop 技能持久化属 v2026.9.3 不是 v2026.9.2**：审稿机器核验官方 release notes 才发现，中文社区多篇对比文都挂错了版本。
3. **Hermes 低频发版≠更稳定**：137 vs 11 发版对比只说明破坏机会少；"6 版中 3 版不能用"同样出现在社区批评中。
4. **Hermes 记忆容量硬限制是特性不是 bug**：2,200 字符逼 Agent 当轮合并—删除—写入，避免静默丢弃；但也带来"下次会话才可见"的陈旧性。
5. **AUR 包状态比README 更诚实**：ArchWiki 称 openclaw 两 AUR 包都带 bubblewrap，实测稳定包依赖列表里没有（openclaw-git 仅列为可选）——以 AUR 页面为准。
6. **"OpenClaw 300MB 常驻"无任何来源**：多轮搜索未证实，已从报告剔除。
7. **OpenClaw 2.0 发布前静默 7 周 + 官方自己建议"等一两个补丁"**：大版本迁移自带 auth/config 迁移未决簇（#134608/#134169）。

## 未核实 / 存疑

- #95495 的 1,499 文件/23,694 chunks/3.4GB 精确数字：issue 自述口径，终审期 4 次抓取失败，未独立复核。
- regression 标签"当前未关闭 118 条"：仅累计 3,200 经 Search API 核验。
- 25% 更新破坏率 / 6 CVE / 341+ 恶意技能 / 135k+ 暴露实例：均转引 Kilo 单一 Reddit 分析（25 帖/1,300+ 评论），置信度低于官方来源。
- Hermes GitHub issue 稳定性密度：撰稿期三次探测仓库未命中，双方 issue 对比缺失。
- OpenClaw 官方中文博客与 Memory 概念页多轮抓取失败，报告以英文原版+第三方深读为据。
