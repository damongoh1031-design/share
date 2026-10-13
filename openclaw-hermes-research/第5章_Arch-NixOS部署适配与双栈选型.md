# Arch/NixOS 部署适配、ACP 互操作性与双栈选型建议

## 论点

本章逐一验证两套智能体在 Arch Linux 与 NixOS 上的真实落地路径，核心结论：**Arch 侧 AUR 包质量 hermes-agent 明显占优（当日更新、7 票），openclaw 稳定包可用但存在版本滞后，ArchWiki 更推荐官方脚本；NixOS 侧 nix-openclaw 一方 Home Manager 模块在声明式能力、回滚与应用层不可变模式上显著领先 Hermes 的 `nix profile` 方案**。ACP 双栈可行，但必须按 v2026.9.2 安全警告设计 Gateway 拓扑。

## 论据

**一、Arch 侧：AUR 三包逐一验证**

据 AUR 页面实测（截至 2026-10-13）：[openclaw](https://aur.archlinux.org/packages/openclaw) 版本 2026.9.9-1，源为 npm registry 的 tarball（`openclaw-2026.9.9.tgz`），仅依赖 nodejs/npm（npm 为 make 依赖），维护者 ralphptorres，最后更新 2026-10-08，5 票；[openclaw-git](https://aur.archlinux.org/packages/openclaw-git) 为 git 源码 Bun 构建，make 依赖含 bun、cmake、gcc、libvips 等，维护者 SolarAquarion，最后更新 2026-09-27，仅 2 票；[hermes-agent](https://aur.archlinux.org/packages/hermes-agent) 版本 0.21.7-3，上游 GitHub tarball 加 `keep-venv-interpreter.patch`，运行时依赖 nodejs/npm/python/uv/agent-browser，维护者 y0uCeF，**最后更新 2026-10-13（当日）**，7 票，且被 hermes-agent-desktop 等 3 个包依赖。

交叉验证显示两点值得注意：其一，[ArchWiki 中文](https://wiki.archlinux.org.cn/title/OpenClaw)明确写道「目前 AUR 软件包均存在 bug 且不稳定」，长期稳定运行建议改用官方 `curl install.sh | bash`，[remoteclaw 指南](https://remoteclaw.com/tutorials/local/arch-linux.html)亦称「AUR 为社区维护，官方安装器才是 supported path 且通常提供最新稳定版」；而实测 openclaw 稳定包比上游「几乎每天发版」（ArchWiki 语）的节奏滞后约 5 天。其二，ArchWiki 称经 AUR 安装「bubblewrap 沙箱已作为依赖项安装」，但 AUR 页面显示稳定包 openclaw 的依赖列表中并无 bubblewrap，仅 openclaw-git 将其列为**可选**依赖——两来源存在出入，以 AUR 页面为准。另 ArchWiki 记载 nixpkgs 主仓存在 `nixpkgs.openclaw`，但不建议单独为 OpenClaw 引入 Nix（重复依赖占磁盘）。

**二、NixOS 侧：nix-openclaw 一方模块 vs Hermes nix profile**

[OpenClaw Nix 官方文档](https://docs.openclaw.ai/zh-CN/install/nix)确认 nix-openclaw 是第一方 Home Manager 模块：Gateway 与工具全部锁定版本、重启可持续运行的服务、声明式插件系统、`home-manager switch --rollback` 即时回滚。更深一层的差距在 **OPENCLAW_NIX_MODE=1**：该模式下 openclaw.json 被视为**不可变**，`openclaw update`、插件安装/卸载、`doctor --fix`、`config set`、`--generate-gateway-token` 等写操作全部被拒绝，用户只能编辑 Nix 源；launchd/systemd 服务还会自动发现 `NIX_PROFILES` 中的二进制加入 PATH（未设置时回退 `~/.nix-profile/bin`）。Hermes 侧，其 Nix 官方文档（[官方中文页](https://hermes-agent.nousresearch.com/docs/zh-Hans/getting-started/nix-setup)，2026-10-11 前后有更新）记载 `nix profile install` 后 `hermes`、`hermes-agent`、`hermes-acp` 三个命令进入 PATH，运行时**无需 pip、无需虚拟环境、无需 npm install**；NixOS 模块用户则将配置写入 configuration.nix，机密经 sops-nix/agenix 管理（[社区镜像 hermesagent.org.cn](https://hermesagent.org.cn/docs/getting-started/nix-setup) 亦印证运行时无 pip/venv/npm 依赖）。就声明式与机密管理而言双方都有路径，但 Hermes 文档中未见与 Nix 模式对等的「应用层不可变语义 + 显式回滚命令」说明，成熟度差距明显。一个细节：AUR 打包中 hermes-agent 仍将 nodejs/npm 列为运行时依赖，与 Nix flake 宣称的「无 npm」形成对照，这正是「打包策略差异」而非「运行时需求差异」。

**三、资源与本地模型门槛**

关键锚点来自 [v2026.9.2 发布说明](https://docs.openclaw.ai/releases/2026.9.2)：本地模型推荐「begin with an 8 GiB memory floor」，更大模型需更多内存、部分需显卡加速，纯 CPU 推理「可能耗时数分钟」。Hermes 的[中文 Linux 指南](https://hermes-agents.net/zh-cn/install/linux/)给出系统要求：内存 2GB 最低 / 4GB+ 推荐、Python 最低 3.10 / 推荐 3.11+，其一键脚本（install.sh，国内镜像 res1.hermesagent.org.cn）自动装 uv、建 venv、配 PATH，并明确「不要使用 sudo 运行」；该页未提供 systemd unit 配置（安装形态为 venv + alias），另链接有 Docker 部署文档。任务参数中「OpenClaw 300MB 常驻」一说未能在任何来源中证实，本章不采用该数字。

**四、ACP 双栈协作与安全边界**

Hermes 的 `hermes-acp` 命令提供了 ACP Server 能力。[CSDN 2026-09 实操文](https://blog.csdn.net/fwyTech2010/article/details/162519237)（博客级证据，仅辅助）演示了 OpenClaw 与 Hermes 基于 ACP 的双 Agent 协作流程，涵盖依赖安装与 ACP Server 启动。**部署拓扑受 v2026.9.2 的共享 Gateway 警告约束**：若多个 agent 跑在同一 Gateway 上，被省略的设置会让具备 session 工具的 agent 读取、搜索其他 agent 乃至其他用户的对话；官方要求显式收窄可见性与 agent-pair 访问，并明确指出「mutually untrusted users need separate Gateways」。

## 分析：选型矩阵

| 用户场景 | 首选 | 依据 |
|---|---|---|
| NixOS 声明式党 | OpenClaw（nix-openclaw 模块），以 `nix profile` 补 Hermes 跑 ACP | rollback + Nix 模式不可变 + PATH 自动发现 |
| Arch 轻量党 | hermes-agent AUR 包；OpenClaw 走官方 install.sh 或稳定 AUR 包 | hermes 包当日更新/维护活跃；AUR openclaw 有滞后且 ArchWiki 预警 |
| 追新激进党 | openclaw-git 或官方脚本，配合 bubblewrap 沙箱 | git 包更新勤但 make 依赖重、投票低 |
| 长期运行 | NixOS 用 rollback + NIX_MODE 冻结自更新；Arch 锁版本、每次更新后运行 `openclaw doctor` | ArchWiki：「几乎每天发新版本，某些更新会使现有配置失效」 |
| 多用户/多租户 | 拆分 Gateway | v2026.9.2：互不信任的用户必须使用独立 Gateway |

## 小结

Arch 与 NixOS 两条路线的结论恰好镜像互补：**要声明式纪律与回滚，选 OpenClaw on NixOS；要开箱轻量与低门槛，选 hermes-agent on Arch**。ACP 双栈技术上已打通（hermes-acp + OpenClaw Gateway），但真正的部署风险不在安装，而在共享 Gateway 的会话可见性——单用户自用可收窄设置后共享，涉及互不信任用户必须拆 Gateway。

## 关键发现

- AUR hermes-agent 于 2026-10-13 当日更新（0.21.7-3，7 票），openclaw 稳定包滞后约 5 天（2026-10-08）([AUR](https://aur.archlinux.org/packages/hermes-agent), [AUR](https://aur.archlinux.org/packages/openclaw))
- ArchWiki 与 remoteclaw 均不推荐 AUR openclaw 包作为长期稳定方案 ([ArchWiki](https://wiki.archlinux.org.cn/title/OpenClaw), [remoteclaw](https://remoteclaw.com/tutorials/local/arch-linux.html))
- OPENCLAW_NIX_MODE=1 使 openclaw.json 不可变并禁用全部自修改命令 ([OpenClaw Nix 文档](https://docs.openclaw.ai/zh-CN/install/nix))
- Hermes `nix profile install` 提供 hermes/hermes-agent/hermes-acp 三命令，运行时无 pip/venv/npm 依赖 ([官方中文页](https://hermes-agent.nousresearch.com/docs/zh-Hans/getting-started/nix-setup))
- 本地模型 8 GiB 内存底线 + 共享 Gateway 会话可见性警告 ([v2026.9.2 发布说明](https://docs.openclaw.ai/releases/2026.9.2))
- 「OpenClaw 300MB 常驻」未获任何来源证实，本章剔除

## 数据摘要

| 指标 | 数据 | 来源 |
|------|------|------|
| AUR openclaw | 2026.9.9-1，npm tarball，维护者 ralphptorres，2026-10-08 更新，5 票 | [AUR](https://aur.archlinux.org/packages/openclaw) |
| AUR openclaw-git | 2026.9.6.r100068，Bun 源码构建，SolarAquarion，2026-09-27 更新，2 票 | [AUR](https://aur.archlinux.org/packages/openclaw-git) |
| AUR hermes-agent | 0.21.7-3，上游 tarball + patch，y0uCeF，2026-10-13 更新，7 票 | [AUR](https://aur.archlinux.org/packages/hermes-agent) |
| OpenClaw 本地模型门槛 | 8 GiB 内存底线，CPU-only 推理可能数分钟 | [v2026.9.2 发布说明](https://docs.openclaw.ai/releases/2026.9.2) |
| Hermes 系统要求 | 内存 2GB 最低 / 4GB+ 推荐；Python 最低 3.10 / 推荐 3.11+ | [hermes-agents.net](https://hermes-agents.net/zh-cn/install/linux/) |
| v2026.9.2 规模 | 1,245 PRs / 232 contributors | [发布说明](https://docs.openclaw.ai/releases/2026.9.2) |
