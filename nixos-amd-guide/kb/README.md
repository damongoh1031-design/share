# KB 索引

本目录沉淀可复用的知识文档。同一主题**原地复写**（递增 frontmatter `version`、刷新 `updated`），不建 `-v2` 之类的新文件。

| id | 标题 | 版本 | 状态 | 更新 | 标签 |
|---|---|---|---|---|---|
| [nixos-amd-teaching-guide](./nixos-amd-teaching-guide.md) | NixOS 26.05 教学指南（AMD 平台 · 中文用户 · Vibe Coding）——37 章配置实录 | 2.0 | stable | 2026-10-14 | nixos, amd-gpu, amdgpu, realtek, r8169, fcitx5, gnome, kde-plasma, flatpak, steam, gamescope, scx, sched-ext, linux-zen, cachyos, ananicy-cpp, ananicy-rules-cachyos, bore, zram, thp, ksm, kyber, vibe-coding, hermes-agent, openclaw, codex, mcp, searxng, nix-ld, devshell, apparmor, fhs, flake, nixpkgs-unstable, overlay, home-manager, nix-openclaw, systemd-user-service, linger, bazzite, ujust, rpm-ostree, nh, distrobox, waydroid, lanzaboote, inputplumber, powerstation, bazaar, atomic-update, aeon, microos, transactional-update, pkgsUnstable, useGlobalPkgs, pkgsPath, stable-base-rolling-apps, buildFHSEnv, buildFHSEnvBubblewrap, autoPatchelfHook, patchelf, nix-alien, nix-index, appimage, binfmt, ldso, xorg-deprecation, libx11, glibc-mismatch, steam-run, official-manual-skeleton, mkForce, mkDefault, mkOverride, option-priority, option-types, externalPath, fileSystems, luks, cryptenroll, userborn, mutableUsers, journalctl, cgroup, MemoryMax, nix-gc, boot-entries, nixos-enter, nixos-container, wayland, rocm-clr-icd, radv, va-api, icd-mismatch, nixos-rebuild-switch, bootspec, uki, image-repart, appliance-image, nix-dev, best-practices, system-nix, npins, switch-inhibitor, fsType-required, release-notes-2605, mkShellNoCC, inputsFrom, post-build-hook, cachix, direnv, sphinx-sources-trick, stage1-systemd, dbus-broker, wineWow64Packages, rocm-7, nixfmt |
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
>
> **v1.8（2026-10-12 第七轮：二进位包与依赖问题完整手册）**：`nixos-amd-teaching-guide.md` 升到 **1.8**（24 章 → 25 章），新增第 16 节。问题原话：「NixOS 如何使用二进位包？如何解决依赖问题？给出全面的方式，考虑所有的可能和程式类型、常见依赖」。方法：**全部取 nixpkgs `nixos-26.05` 分支模块源码 + 上游项目 README**，不依赖任何二手教程。
>
> 三条最高价值结论：
>
> 1. **★★ `xorg` 包集在 26.05 已弃用，全部 `libX*` 改名 `libx*`**（`aliases.nix:1178-1207`，2026-02-06；弃用公告 `rl-2605.section.md:235`，2026-01-29）。`pkgs.xorg.libX11` 现在会打弃用警告。**网上所有 nix-ld 教程（含大量 LLM 训练数据）用的都是旧写法** —— 这是本轮影响面最广的一条。
> 2. **NixOS 是「主动删除」`/lib64/ld-linux-x86-64.so.2`**（`config/ldso.nix` 的 `systemd.tmpfiles.rules` **`r` 规则**），不是「本来就没有」。**这解释了为什么报错是 `No such file or directory`。** `programs.nix-ld` 用 `L+` 符号链接把它换回来。
> 3. **`programs.nix-ld` 自带 14 个基础库**（不是「默认空」）+ **nixpkgs 的 python / node 不走 nix-ld** → **pip / npm 原生模块失败时开 nix-ld 没用**，要用官方 wrapper 设 `LD_LIBRARY_PATH`。
>
> 另有：**14 种方案按侵入性排序**（从「直接用 nixpkgs 版」到「Distrobox 容器」）；**`buildFHSEnv` = `buildFHSEnvBubblewrap`**（chroot 版已弃用），其 `/etc` 是从宿主 `--ro-bind` 的 **30 项**（解释了「为什么在里面改字体不生效」）；**三类死路**（内核模块 / setuid / glibc 硬冲突）。
>
> **v1.9（2026-10-12 第八轮：以官方手册结构为骨架重构 + 第二十六～三十五章）**：`nixos-amd-teaching-guide.md` 升到 **1.9**（25 章 → 35 章），新增第 17 节。**本轮性质与前三轮完全不同** —— 前三轮是「按提问补内容」，本轮是「**把官方手册整站拉下来，脚本统计骨架，系统性找缺口**」。问题原话：「https://nixos.org/manual/nixos/stable/ / 从官方文档补充资料 / 以官方文档的结构为骨架重新修正你的指南」。
>
> **方法**（全部可复现）：`curl -sL` 拉整站（1,200,007 字节）→ Node 脚本统计带 `id` 的标题 → 排除 `module-*` / `opt-*` 自动生成章节 → 得到**真实骨架：H1 11 / 叙事 H2 177 / 叙事 H3 80** → 做成双向对照表 → 逐条标注覆盖度 → 把 10 个缺口写成新章节。
>
> **两个关键决策**（用户通过选项确认）：① **「骨架导航 + 补齐缺口」**，而不是物理重排全文 —— **保留现有 25 章编号，不破坏 §x.y 交叉引用**；② **面向 AMD / 中文 / 游戏 / Vibe Coding 画像精选** —— 跳过 ZFS / Xen / Kubernetes / Pantheon / Mattermost / Suwayomi 等服务类章节。
>
> 五条最高价值结论：
>
> 1. **★ 非 longterm 内核会从 nixpkgs 删除，即使在 stable 分支** —— 官方硬规则：在**第一批新稳定内核发布时**移除。**这解释了「为什么写死内核小版本号会突然构建失败」**，正确写法是 `pkgs.linuxPackages_latest` / `_zen` / 默认。
> 2. **★ ICD 混版本静默失败** —— OpenCL/Vulkan 用 **`dlopen`** 加载 runtime，**不受 Nix 构建期依赖追踪保护**。loader 与 runtime 来自不同 nixpkgs → glibc 符号缺失 → **loader 不报错**。**据此修正了第二十章「只滚 mesa」的建议**。
> 3. **覆盖优先级精确数字**：`mkForce`(**50**) < 普通(**100**) < `mkDefault`(**1000**) < 选项 `default`(**1500**)。**顺序优先级是另一套**：`mkBefore`(500) < 普通(1000) < `mkAfter`(1500)，只影响顺序不影响保留。**官方原文 *"lowest priority value"* = 数字最小，容易读反。**
> 4. **`systemctl --user enable` 会链到 `/nix/store/...` → GC 后死链 → 服务静默不自启** —— 官方专段。正确做法是链到 `/run/current-system/sw/lib/systemd/user/`。
> 5. **`nix-collect-garbage -d` 会删掉所有 generation 的 roots → 失去回滚能力**；且 **`/boot` 满了要「删 generation」+「再 rebuild」两步**（漏第二步不生效）。
>
> 另有：**`nixos-rebuild switch` 的 12 步固定动作顺序**；**`X-StopIfChanged` 默认 true**（「新 unit 绝不在旧环境里运行」）；**activation script 每次启动都跑 → 不要塞重活**；**cgroup 默认无内存限制 → `MemoryMax` 治 nix-daemon OOM**；**`users.mutableUsers = false` 时 `useradd` 完全不可用**；**`hashedPassword` 明文进 `/nix/store`**；**`/var/lib/nixos` 存 uid 分配记录，丢了属主乱**；**NixOS 容器「not perfectly isolated」，容器 root 能影响宿主**；**`image.repart` 里 `Label` 与 `fileSystems.*.device` 不一致 → 掉 shell**；**appliance 不适合 generation 更新 → 换整镜像或 A/B（官方点名 Chrome OS）**。

> **v2.0（2026-10-14 第九轮：nix.dev guides + NixOS 26.05 release notes）**：`nixos-amd-teaching-guide.md` 升到 **2.0**（35 章 → 37 章），新增第 18 节。问题原话：「https://nix.dev/guides/ / 从官方文档补充资料」。**本轮定位：第八轮补的是 reference（官方手册 = 「有什么选项」）；第九轮补的是 guides（nix.dev = 「怎么写才对」）+ release notes（「26.05 改了什么」）。**
>
> **★ 通用技巧**：**任何 Sphinx 站的 Markdown 源都在 `/_sources/<路径>.md`** —— 比抓 HTML 干净得多（`https://nix.dev/guides/` 的 HTML 只有 26,649 B 且 `<main>` 几乎为空，是 JS 渲染的）。
>
> 六条最高价值结论：
>
> 1. **★★ `fileSystems.<name>.fsType` 在 26.05 不再有默认值，必须显式写** —— 而**官方手册正文仍说「可以省略」**。这是「**官方手册正文滞后于 release notes + 模块源码**」的实证（源码对比：25.11 有 `default = "auto"`，26.05 删掉了）。**跟着手册写配置反而会报错。**
> 2. **★★ 26.05 默认 Stage 1（initrd）= systemd** —— scripted 已弃用、**26.11 移除**。**这解决了本 KB 上一版的一条存疑项**（第八轮推断为 scripted，是错的）。急救参数要先试 `rd.systemd.break=pre-switch-root`。
> 3. **★ Switch inhibitors：26.05 多了一道「切换前检查」** —— 对比字符串列表，有差异则**拒绝切换**；`NIXOS_NO_CHECK=1` 可绕过。**这是第三十三章之前缺的一块拼图。**
> 4. **★ `import <nixpkgs> {}` 不完全可复现** —— 官方原话 *"by default impurely reads from the file system to obtain configuration parameters"*。**这解释了为什么 `pkgsUnstable` 必须显式传 `config` 和 `overlays`。**
> 5. **★ `nix-ld` 的两条关键细节** —— ① 启用后**必须「登出再登入」**；② **`x86_64` 上不支持 32 位可执行文件** → **Steam / Wine 的 32 位游戏不能用 nix-ld**，必须走 `steam-run` / `buildFHSEnv`。
> 6. **★ `profiles/hardened` 已移除 + `wineWowPackages` 改名 `wineWow64Packages`**（官方警告 prefix 不向后兼容、**可能丢数据**，`yabridge` / `wineasio` 用户必查）。
>
> 另有：**官方最佳实践七条**（URL 加引号 / 避免 `rec` / 顶层不用 `with` / 不用 `<...>` lookup path / `import <nixpkgs> {}` 不纯 / `//` 是浅合并 / `src = ./.;` 不可复现）—— **这是官方唯一明确说「不要这么写」的地方，可直接作 Agent 代码审查清单**；**`system.nix`**（26.05 新增配置入口，不用 channel 也不用 flake）；**npins**；**自定义二进制缓存的安全警告**（私钥持有者能往 store 里塞任意文件）；**`mkShellNoCC`**（nix.dev recipe 全用它，比 `mkShell` 少带 `stdenv.cc`）；**数据库损坏 ≠ store 损坏**（用 sqlite `.dump` 重建，不要 `--repair`）。

## 约定

- frontmatter 必填：`id` / `title` / `tags` / `created` / `updated` / `version` / `status` / `source` / `confidence`
- 正文结构：一句话结论 → 分主题（表格优先）→ 可复用操作 → 坑与反直觉 → 未核实/存疑
- `confidence` 取值：`已核实` / `社区实证` / `推断`
- 提炼，不复制对话痕迹；数据带口径与日期；结论标核实状态
