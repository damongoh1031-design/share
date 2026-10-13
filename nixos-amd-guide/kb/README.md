# KB 索引

本目录沉淀可复用的知识文档。同一主题**原地复写**（递增 frontmatter `version`、刷新 `updated`），不建 `-v2` 之类的新文件。

| id | 标题 | 版本 | 状态 | 更新 | 标签 |
|---|---|---|---|---|---|
| [nixos-amd-teaching-guide](./nixos-amd-teaching-guide.md) | NixOS 26.05 教学指南（AMD 平台 · 中文用户 · Vibe Coding）——24 章配置实录 | 1.7 | stable | 2026-10-12 | nixos, amd-gpu, amdgpu, realtek, r8169, fcitx5, gnome, kde-plasma, flatpak, steam, gamescope, scx, sched-ext, linux-zen, cachyos, ananicy-cpp, ananicy-rules-cachyos, bore, zram, thp, ksm, kyber, vibe-coding, hermes-agent, openclaw, codex, mcp, searxng, nix-ld, devshell, apparmor, fhs, flake, nixpkgs-unstable, overlay, home-manager, nix-openclaw, systemd-user-service, linger, bazzite, ujust, rpm-ostree, nh, distrobox, waydroid, lanzaboote, inputplumber, powerstation, bazaar, atomic-update, aeon, microos, transactional-update, pkgsUnstable, useGlobalPkgs, pkgsPath, stable-base-rolling-apps |
| [nixos-operations-guide](./nixos-operations-guide.md) | NixOS 运维指南（26.05）——配置路线、游戏、非 Nix 二进制、混合版本策略、查询工具链、LLM 辅助 | 1.5 | stable | 2026-10-12 | nixos, nix, flakes, home-manager, gaming, steam, appimage, nix-ld, llm-ops, mcp, rolling-release, nixpkgs-unstable, nixhub, flakehub, noogle, systemd-user-service, linger, hermes-agent, openclaw |
| [distro-ai-collaborative-management](./distro-ai-collaborative-management.md) | 发行版「AI 协同管理」实践全景——哪些发行版真的有 MCP / Skills / AI 运维方案 | 1.0 | stable | 2026-10-12 | linux-distro, mcp, agent-skills, ai-ops, redhat, nixos, opensuse, omarchy, bluefin, clawhub, skills-sh |

> **v1.3（2026-10-12 第二轮复核）**：对前两份文档做了一次**逐条一手源码复核**，改正了 6 类事实错误（5 处模块路径 + 1 处 nix-ld 默认库误读），并把 3 条 `[部分未核实]` 升级为已核实。要点见 `nixos-amd-teaching-guide.md` 第 11 节。
>
> **v1.4（2026-10-12 第三轮：新增四章）**：`nixos-amd-teaching-guide.md` 升到 **1.4**（18 章 → 22 章），新增第 12 节。内容为 **Hermes Agent / OpenClaw 在 NixOS 上的落地**（安装 / 管理 / 自启 / **root 权限边界** / Home Manager / flake / 官方 bash）与**坑与社区意见**。全部证据来自 2026-10-12 的官方 flake 源码、官方文档、GitHub issue 与 NixOS Discourse 核实。**核心结论：声明式部署与"agent 能在对话里改自己的配置"不可兼得。**
>
> **v1.5（2026-10-12 第四轮：双分支版本实测）**：两份 NixOS 文档均升到 **1.5**，各新增一节（教学指南第 13 节 / 运维指南第 4 节扩充）。方法是在 `nixos-26.05` 与 `nixos-unstable` 两个分支上**逐包比对版本**，据此**修正了两处过宽结论**：
>
> 1. **内核不再整行判「❌ 不要跨源」** —— 实测两分支 `packageAliases` 与 `kernels-org.json` **逐字相同**（`linuxPackages_latest` 两边都是 **7.2.9**）。**26.05 上跨源拿内核 = 多拉一整份 nixpkgs，换来相同版本号。** 正确做法是 `pkgs.linuxPackages_latest`（跟基座走）。仍不能跨源的是**树外模块**（NVIDIA / ZFS / VirtualBox / `r8168`）。
> 2. **「两套 nixpkgs 必须有 flake」是错的** —— 不用 flake 也有三条路：channel / `builtins.fetchTarball` / `builtins.fetchGit` + 钉 `rev`。**flake 的价值不是「能做到」，而是「把手工锁自动化」。** 同时修正推荐写法：overlay 挂 `pkgs.unstable` 官方论坛**不推荐**，应改用 `_module.args.pkgsUnstable`。
>
> 另有实测数据：Mesa 26.1.8→26.2.4、proton-ge-bin GE-Proton11-1→11-7、gamescope 3.16.23→3.16.31 有实质差异；**mangohud 1.91.6 两边无差**。
>
> **v1.6（2026-10-12 第五轮：Bazzite 使用模式对照）**：`nixos-amd-teaching-guide.md` 升到 **1.6**（22 章 → 23 章），新增第 14 节。内容为**「如何让 NixOS 做到类似 Fedora Bazzite 的使用模式」**的完整映射。方法：**Bazzite 侧全部取官方文档原文**（六层软件层级、`ujust` 动词体系、image-based/回滚/Secure Boot 声明），**NixOS 侧全部直接读 `nixos-26.05` 源码**。
>
> 三条最高价值结论：
>
> 1. **能复刻约 80%，剩下 20%（开箱即用整机体验 + GUI 门户）不该复刻。** 六层层级逐条有对应物，但**②Flatpak 优先 / ⑥rpm-ostree 是最后手段这两条顺序是反的** —— 照抄会得到最糟结果。
> 2. **NixOS 默认内核已编入 `ANDROID_BINDER_IPC` / `ANDROID_BINDERFS`（`tristate = "y"`）** → 装 Waydroid **不需要自定义内核**，推翻社区流传的过时说法。
> 3. **Bazzite 的掌机组件大多在 nixpkgs 里**：`pkgs.inputplumber`（v0.77.1）、`pkgs.powerstation`（TDP 控制 daemon）、`pkgs.bazaar`（FlatHub-first 商店）、`pkgs.distrobox`（**同为 1.8.2.5**）。**缺的不是零件，是机型适配接线。**
>
> 另有：`pkgs.nh`（4.4.2，**官方 NixOS 模块 `programs.nh`**）= NixOS 上最接近 `ujust` 的东西；`services.flatpak` **只有 `enable` + `package`**；`pkgs.decky-loader` / `pkgs.lanzaboote` = 404。
>
> **v1.7（2026-10-12 第六轮：Aeon 模式 —— 稳定基座 + 最新应用）**：`nixos-amd-teaching-guide.md` 升到 **1.7**（23 章 → 24 章），新增第 15 节。问题原话：「要做到类似 openSUSE Aeon，基座是稳定，但 apps 是最新的，如何做」。方法：**Aeon 侧取 LWN 一手技术分析 + 官网原文**，**NixOS 侧取 Home Manager 官方 FAQ 专节 + HM/NixOS 源码**。
>
> 三条最高价值结论：
>
> 1. **★ 前提修正：Aeon 的基座是滚动的 openSUSE Tumbleweed，不是冻结版本。** 它的「稳定」来自**原子 + 极简 + 隔离**，不来自版本冻结。**「稳定基座」有两种含义**（冻结式 / 原子式），**NixOS 两种都能给** —— 所以有**三条**路，Aeon 只有一条。
> 2. **HM 官方 FAQ 有专节 *"How do I install packages from Nixpkgs unstable?"***，NixOS 模块下的官方写法是 `home-manager.extraSpecialArgs = { pkgsUnstable = import nixpkgs-unstable { inherit system; config = config.nixpkgs.config; overlays = config.nixpkgs.overlays; }; }` —— **那两行 `config`/`overlays` 是官方明确要求**，漏了 unfree 包会求值失败。
> 3. **三条路**：A（Aeon 式：基座极简 + Flatpak + Distrobox）/ B（双 nixpkgs：官方 FAQ 写法）/ **C（混合，推荐：只把 mesa 取 unstable + 应用按需）**。NixOS 比 Aeon 多一个能力：**基座、组件、应用可各自有各自的新鲜度与回滚粒度**。
>
> 另有一处**诚实的短板**：**Aeon 有「启动失败自动回滚」，NixOS 没有开箱实现**（需手动在启动菜单选旧 generation）。这是本文档找到的唯一 NixOS 明显不如 Aeon 的一项。

## 约定

- frontmatter 必填：`id` / `title` / `tags` / `created` / `updated` / `version` / `status` / `source` / `confidence`
- 正文结构：一句话结论 → 分主题（表格优先）→ 可复用操作 → 坑与反直觉 → 未核实/存疑
- `confidence` 取值：`已核实` / `社区实证` / `推断`
- 提炼，不复制对话痕迹；数据带口径与日期；结论标核实状态
