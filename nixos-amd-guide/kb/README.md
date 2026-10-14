# KB 索引

本目录沉淀可复用的知识文档。同一主题**原地复写**（递增 frontmatter `version`、刷新 `updated`），不建 `-v2` 之类的新文件。

| id | 标题 | 版本 | 状态 | 更新 | 标签 |
|---|---|---|---|---|---|
| [nixos-amd-teaching-guide](./nixos-amd-teaching-guide.md) | NixOS 26.05 教学指南（AMD 平台 · 中文用户 · Vibe Coding）——40 章配置实录 | 2.3 | stable | 2026-10-14 | nixos, amd-gpu, amdgpu, realtek, r8169, fcitx5, gnome, kde-plasma, flatpak, steam, gamescope, scx, sched-ext, linux-zen, cachyos, ananicy-cpp, ananicy-rules-cachyos, bore, zram, thp, ksm, kyber, vibe-coding, hermes-agent, openclaw, codex, mcp, searxng, nix-ld, devshell, apparmor, fhs, flake, nixpkgs-unstable, overlay, home-manager, nix-openclaw, systemd-user-service, linger, bazzite, ujust, rpm-ostree, nh, distrobox, waydroid, lanzaboote, inputplumber, powerstation, bazaar, atomic-update, aeon, microos, transactional-update, pkgsUnstable, useGlobalPkgs, pkgsPath, stable-base-rolling-apps, buildFHSEnv, buildFHSEnvBubblewrap, autoPatchelfHook, patchelf, nix-alien, nix-index, appimage, binfmt, ldso, xorg-deprecation, libx11, glibc-mismatch, steam-run, official-manual-skeleton, mkForce, mkDefault, mkOverride, option-priority, option-types, externalPath, fileSystems, luks, cryptenroll, userborn, mutableUsers, journalctl, cgroup, MemoryMax, nix-gc, boot-entries, nixos-enter, nixos-container, wayland, rocm-clr-icd, radv, va-api, icd-mismatch, nixos-rebuild-switch, bootspec, uki, image-repart, appliance-image, nix-dev, best-practices, system-nix, npins, switch-inhibitor, fsType-required, release-notes-2605, mkShellNoCC, inputsFrom, post-build-hook, cachix, direnv, sphinx-sources-trick, stage1-systemd, dbus-broker, wineWow64Packages, rocm-7, nixfmt, mcp-nixos, search-nixos-org, option-defaults, not-found-false-negative, index-lag, aliases-nix, kernel-removal, auto-cpufreq, home-manager-options, nixhub-io, dual-backend, action-cache, binary-cache-status, unfree-not-cached, browse-action, type-options, similar-suggestion, hm-auto-upgrade, hm-auto-expire, qt-platform-theme-deprecated, discord-nixos, discord-guild-api, discord-widget-json, discord-invite-api, mentoring-channel, reddit-rss, reddit-search-rss, moli-headless-browser, reddit-rate-limit-empty-body, shreddit-post-attrs, no-score-in-rss, hidapi-steam-controller, esp-bootloader-diff, grub-boot-efi, systemd-boot-esp-only, limine-maxGenerations, boot-gardener, catch-22-esp, unstable-mesa-failure, gdm-blinking-cursor, nixdatifier, apdatifier-nixos, aur-malware-rollback, darwin-nix-jargon, cellpackages, flake-parts, mesa-git-rdna4, jovian-nixos, i2c-designware-pci, llm-assisted-flake, chatgpt-wrong-extraPackages, nix-diataxis-epub, nixos-wizard, zero-to-nix, community-quote-discipline |
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

> **v2.1（2026-10-14 第十轮：mcp-nixos 交叉核实）**：`nixos-amd-teaching-guide.md` 升到 **2.1**（37 章 → 38 章），新增第 19 节。问题原话：「根据 mcp-nixos 来修正报告」。**本轮性质是「用实时数据源反向核对前 37 章的结论」** —— 不是补内容，是验证。
>
> **工具**：**mcp-nixos v3.1.0**（<https://github.com/utensils/mcp-nixos>，MIT，直连 search.nixos.org 的 Elasticsearch 索引，**不需要装 Nix**），`uvx mcp-nixos@latest` 直跑。**约 325 条查询**，12 个批次。
>
> **★ 修正了 3 处**（全部已就地改）：
>
> 1. **`services.hardware.auto-cpufreq` → `services.auto-cpufreq`** —— **「文件在 `services/hardware/` 目录」≠「选项在 `services.hardware.` 下」**（写错会求值失败）
> 2. **`nixfmt-rfc-style` → `pkgs.nixfmt`（1.5.0）** —— 描述原文 *"Official formatter for Nix code"*；**不存在 `nixfmt-rfc-style` 这个包**
> 3. **`services.openssh.generateHostKeys` 默认值** —— 实测 **Default = `services.openssh.enable`**（跟随 sshd），不是 `true`
>
> **★ 三处错误的共同点**：**全部来自「从命名规律推断」而不是「读源码读错」** —— 这是本 KB 首次系统性暴露「推断型错误」的占比。**推断比读错更危险，因为它看起来很有道理。**
>
> **★ 本轮最强的两条证据**：
> - **`boot.initrd.systemd.enable`：25.11 = `false`，26.05 = `true`** —— 双 channel 实测，**「默认值真的变了」的直接证据**（比读 release notes 更硬）
> - **`linux_7_0`（7.0.14）/ `linux_7_1`（7.1.2）在 25.11 存在、26.05 消失** —— **「非 longterm 内核会被从 nixpkgs 删除」的实物证据**（`linux_7_2` 还在，**被删的是「被超越的」那两代**）
>
> **★★ 本轮确立的通用方法论：`NOT_FOUND` ≠ 不存在。** mcp-nixos 索引查不到的名字有**四类假阴性**：① **别名**（`xorg.libX11` / `libX11` / `fonts.fonts` / `nix.binaryCaches`）② **attrset 中间层**（`services.lact` → 查 `services.lact.enable`）③ **派生 attrset**（`linuxPackages` → 查 `linuxKernel.kernels.linux_6_18`）④ **nix.conf 键**（`extra-substituters` / `post-build-hook`）。**四步判据都不命中，才判定为真的不存在。**
>
> **★ 这条纪律保护了一个正确结论**：`xorg.libX11` 等 5 个名字**全部 `NOT_FOUND`**，但源码对比证明它们是 **`warn` 别名**（25.11 无 `libX11` 别名条目、`xorg` 是真实包集；26.05 有 `libX11 = libx11; # Added 2026-02-06` 且 `xorg` 变成 `warnAlias` 别名集）—— **§25.2 的 `xorg` 改名结论无需修改**。
>
> **另有**：**`nixfmt` 1.5.0 / `bazaar` 0.7.15 / `powerstation` 0.8.1 / `rocmPackages.clr` 7.2.3 / `scx.full` 1.1.2 / `npins` 0.4.2 / `nodejs` 24.21.0 / `python3` 3.13.15** 等一批版本号已核实；**`profiles/hardened` 的移除手法**是「文件在、内容是 `mkRemovedOptionModule` 存根」—— **看文件在不在判断不出是否被移除**。

> **v2.2（2026-10-14 第十一轮：mcp-nixos 完整能力面）**：`nixos-amd-teaching-guide.md` 升到 **2.2**（38 章 → 39 章），新增第 20 节。**本轮性质是「补盲 + 辨析」** —— 第十轮只用了这个工具的 **1/11 的 source 和 4/8 的 action**。
>
> **工具**：同一个 **mcp-nixos v3.1.0**，但本轮**通读了上游 README 的「The Tools」章节**（第十轮未读），据此系统实测 **11 个 source × 8 个 action**，并**首次核实 home-manager 侧**（正文 91 处提到 HM，第十轮一条都没查）。**约 150 条查询**，9 个新批次（`mcp-batch-12` … `-20`）。
>
> **★★★ 本轮最重要的发现：mcp-nixos 内部有两条互不相通的后端。**
>
> | 走哪条路 | 后端 | 跟踪 | 实测新鲜度 |
> |---|---|---|---|
> | `info` / `search` / `stats` / `browse` + **`channel=`** | **search.nixos.org** | 你指定的 channel | **2026-10-14**（当日） |
> | **`nix_versions`** + **`action=cache`** + `source=nixhub` | **NixHub.io**（Jetify） | **只有 unstable 历史，无 `channel` 参数** | **2026-08-27**（滞后约 7 周） |
>
> **同一个包，两个答案**：`steam` 26.05=1.0.0.85 / NixHub=1.0.0.87；`mesa` 26.05=26.1.8 / NixHub=26.2.1；`proton-ge-bin` 26.05=GE-Proton11-1 / NixHub=`3`；**`firefox` 26.05=157.0.1 / NixHub=154.0.1（比 stable 还旧）**；`nodejs` 26.05=24.21.0 / NixHub=26.8.1。
> **决定性旁证**：`nix_versions(package="nodejs", version="24.21.0")` → **`Version 24.21.0 not found`**，但 26.05 里 `nodejs` 就是 24.21.0。
>
> **★ 第二轮发现：HM 侧索引有三个系统性特性** —— ① **不返回默认值**（`programs.firefox.enable` 在 NixOS 侧有 `Default: false`，**HM 侧没有 `Default:` 行** → **第十轮那条「没有 `Default:` 行 = 没有默认值」的判据在 HM 侧失效**）② **描述被截断**（`xdg.portal.enable` 断在 `… so that`）③ **忽略 `channel` 参数**（`stats` 在 26.05 与 25.11 下返回**完全相同**的 5,661 / 28 —— 因为 **HM 不在 nixpkgs 里**，反向佐证了这一点）。**正文 25 条 HM 选项已逐条核实**，24 条正确。
>
> **★★ 本轮最有价值的实务发现：HM 内建的两个服务。** `services.home-manager.autoUpgrade`（6 选项）/ `services.home-manager.autoExpire`（5 选项）—— 本 KB 原来只有**系统层**的 `system.autoUpgrade` / `nix.gc`，而 agent 按硬约束跑在**用户层**，**系统层 GC 看不见也清不掉 HM 的用户 generation 链**。`autoExpire` 就是官方给这个问题的答案。（已补进正文 §11.3「层次 5」与 §19.6）
>
> **★★ `action=cache` 实测**：`mesa` ✅ CACHED（58.7 MB）/ `proton-ge-bin` ✅ CACHED（162 B）/ `firefox` ✅ / **`steam` ❌ `NOT CACHED`** —— **因为它是 `unfreeRedistributable`；`cache.nixos.org` 不缓存 unfree 包**。这是「为什么装 Steam 那么慢」的物理原因。（已补进 §22.2）
>
> **★ 本轮修正 1 处 / 补充 5 处**：
> 1. **修正 §6.5** —— `qt.platformTheme` 在 **HM 侧已弃用**（官方描述原文 *"Deprecated. Use `qt.platformTheme.name` instead."*）。**26.05 的深色模式问题是第二层坑，第一层是选项本身已弃用**
> 2. 补充 **§11.3**（HM 侧自动更新）· **§19.6**（HM 自动升级/清理）· **§22.2**（`action=cache`）· **§38.7**（假阴性第⑤⑥类）· **§29 unit 表**（`home.mount` 消歧）
>
> **★ 假阴性从四类扩到六类** —— 新增 **第⑤类：第三方模块选项**（`home-manager.users` / `.useGlobalPkgs` / `.useUserPackages` 在 nixpkgs 索引里**永远查不到**，因为它们是 HM 仓库自带的 NixOS 模块提供的）与 **第⑥类：freeform 子键**（`xdg.portal.config.common.default` —— 查父选项，`Example:` 字段里就写着）。**判据升级为「六步 + 一次 `search`」**（因为 `search` 带 `type=options` 能查到很多 `info` 查不到的东西）。
>
> **★ 两条独立佐证**：① 本指南说「`programs.mangohud` 是 HM 侧选项」→ NixOS 侧 `NOT_FOUND` ✅ / HM 侧 ✅；② 本指南说「Hermes / OpenClaw 不在 nixpkgs」→ `services.hermes-agent.enable` `NOT_FOUND` + HM 侧 `openclaw` **`No Home Manager options found`** ✅
>
> **★ 第十轮版本号复现性**：本轮重跑 15 个包（`mangohud` / `goverlay` / `gamemode` / `gamescope` / `mesa` / `heroic` / `bottles` / `wine` / `lact` / `inputplumber` / `powerstation` / `bazaar` / `nixfmt` / `firefox` / `chromium`）—— **全部与第十轮一致**。
>
> **两轮方法论的关系**：**第十轮**发现「**索引的边界**」（四类假阴性 → 查不到）；**第十一轮**发现「**索引内部的分裂**」（同一工具不同 action 给出不同值 → **查到了错的值还以为是对的**）。**后者更隐蔽，也更值得警惕。**

> **v2.3（2026-10-14 第十二轮：Discord 与 Reddit 社区信号）**：`nixos-amd-teaching-guide.md` 升到 **2.3**（39 章 → 40 章），新增第 21 节。问题原话：「根据 discord 和 reddit 来补充资料」。**本轮性质是「从官方文档/索引之外引入第三类证据源」** —— 前十轮全是官方文档、源码、实时索引；本轮首次系统采集**社区一手数据**（Discord 官方 API + Reddit 定向搜索），并**明确划定社区数据的适用边界**。
>
> **★ 两条数据通路（全部可复现）**：
> - **Discord 官方 API（无需认证）**：官方邀请链接 **`https://discord.gg/BqdJJFER4H`**（从 <https://nixos.org/community/> 提取）→ `GET https://discord.com/api/v10/invites/BqdJJFER4H?with_counts=true` → **20,092 成员 / 3,695 在线** / `guild_id=568306982717751326` / `Nix/NixOS (unofficial)`；`GET /api/v10/guilds/568306982717751326/widget.json` → **7 个公开频道**（`General` / `More General` / **`Mentoring Group`** / **`Mentoring 1-1`** / `Conferences & Meetups` / `asocial-stream-watchers😋` / `AFK`）。`preview` 端点 **401**（需 bot token）。
> - **Reddit 定向搜索（moli 无头浏览器 + `.rss`）**：`curl` 直连 `.json`/`.rss` **全部 403**（189,908 B 阻断页）；全部 redlib / safereddit / rsshub 第三方前端 **429/403/404/410/418/502/000**；`api.pullpush.io` 与 `answeroverflow.com` 返回**明确的商业拒绝**（原文 *"This website does not provide free scraping resources for agents…"*）。**唯一走通**：本机 moli v1.1.17 + `www.reddit.com/r/<sub>/search.rss`，**9 组查询 / 225 帖 / 后台串行 7 分 13 秒**。
>
> **★★★ 本轮最重要的工程发现：Reddit 限流的真实形态不是 429，而是 200 + 39 字节空 body。** 无间隔请求时返回 `<html><head></head><body></body></html>`（**HTTP 200 但解析出 0 条 entry，静默失败**）。**→ 可复用纪律：抓取判据看 `<entry>` 数量，不看 HTTP 状态码。** 实测参数：**相邻请求 ≥ 35–40 秒、必须串行、2–5 次重试**（8 组中 3 组各需 1 次重试，均在第二次成功）。
>
> **★ 口径边界（必须写清）**：Reddit RSS **有** `title`/`link`/`updated`/`author`/`content`（首帖正文开头约 400–600 字符）；**没有** **`score`** / **`comment-count`** / 评论区全文。**→ 本轮 Reddit 数据「不能做热度排序」**（`sort=top` 的顺序有意义，分数值拿不到）。Discord 公开 API 只有规模/在线数/7 个频道名，**无任何频道内容**。
>
> **三条最高价值社区实证**：
>
> 1. **★ 把「只滚 mesa」从 `[未核实]` 升级为 `[社区实证]`** —— `1wuvnh2`（**2026-10-01**，u/Stunning-Mix492）原文 *"I use a simple gnome setup with flakes, pointing to the 26.05 stable release… After boot splash, I'm stuck on a blinking cursor, GDM does not launch… **Solved: do not use unstable mesa on stable release :)**"*；用户**最初误判为 systemd 问题**。**据此修正 §24.6 的路 C 建议**（mesa 改为「不要单独滚」），并补 §32.6 的 `journalctl -b -1` 诊断命令。
> 2. **★ ESP 三引导器行为差异 + catch-22 + 免安装救援命令** —— `1wofaax`（**2026-09-23**，u/Lonely-Scarcity-3387）：GRUB *"only if you set it up that way. If you mount the ESP at `/boot/efi` instead of `/boot`, kernels and initrds stay on your root filesystem"*；systemd-boot *"can't read from the root partition"*；*"`configurationLimit` prunes old entries automatically, **but only before the ESP fills up**… Once it's full, you hit a **catch-22** because the rebuild has to copy new files before it can delete old ones"*；Limine 最差（`maxGenerations` 默认无限制）。救援：`nix run --extra-experimental-features "nix-command flakes" github:DanielTallon/nix-packages#boot-gardener`。**补进 §30.5。**
> 3. **★ LLM 说错的实例** —— `1mq7qni`（2025-08-14，u/VoNpo）：ChatGPT 建议在 `hardware.graphics.extraPackages` 里塞 mesa/vulkan/libva，**作者起疑去 Reddit 求证** *"Is there any real truth to this, any devs here to confirm which is the correct way?"*。**本指南 §32.1 已核实：`hardware.graphics.enable = true` 已包含这些，只有 OpenCL 需额外装。**
>
> **★ 本轮新增的唯一知识点**：**2026 款 Steam 手柄需要 `programs.steam.extraPackages = [ pkgs.hidapi ];`** —— `1th46tr`（**2026-05-18**，u/Cyb0lic）原文 *"the Steam client uses **hidapi** for this communication, which **isn't installed by default**"*（*"UPDATE: This is no-longer an issue with the beta version of the Steam client."*）。**补进 §8.1。**
>
> **★ 8 处就地修正/补充**：§8.1（Steam 手柄 hidapi）· §11.3 层次 6（**Nixdatifier** —— `1x2h00h`，2026-10-10，flake input 过时提醒 + generation 时间线 + dry-run 预览）· §17.2.5（**回滚 generation 能清掉病毒吗？** —— 分两半回答 + 5 行持久化点表 + AUR vs nixpkgs 供应链差异）· §24.6（路 C 修正）· §30.5（三引导器）· §32.6（只滚 mesa 实证）· §36.14（**黑话对照表** —— `darwin.nix`/`cellPackages`/`flake-parts`/`dendritic`/`den` 等 10 个词，回应 `1uhwn3m` 原文 *"if you are a beginner, get off!"*）· 附录 E.3（**推翻**旧结论「Reddit 抓取被拦截」）。
>
> **★ LLM 辅助写 flake 的 5 个真实案例**（2025-08 → 2026-10 / 4 种模型）：`1rtjyz9`（Claude，*"checking its work every step of the way"*）· `1rqtu0j`（Claude）· `1wvx3r2`（Claude）· `1qi7a2g`（Gemini）· `1mq7qni`（ChatGPT，**说错的实例**）。**`1rtjyz9` 逐句对应本指南原则**：*"I did however decide exactly on how I wanted it"* → 人定架构（§34 提示词模板）；*"checking its work every step of the way"* → `dry-build` 作验证闸门（§0.3 铁律 3）。
>
> **★ 三轮方法论的递进**：**第十轮** = **查不到 ≠ 不存在**（索引的边界）；**第十一轮** = **查到了 ≠ 是对的**（索引内部分裂）；**第十二轮** = **有人这么说 ≠ 事实如此**（社区数据的适用范围）。**共同点：都不是「数据错了」，而是「数据的适用范围被误判了」。**
>
> **★ 三条可复用纪律**：① **抓取判据看内容，不看状态码**（Reddit 限流 = 200 + 39 字节空 body）；② **社区帖「取方法不取数字」**（`1ae5y4l` 的 `rev` 早已过期但回滚方法不过期；`jw4nv7`（2020）的 `services.xserver.videoDrivers` 写法在 26.05 已弃用）；③ **社区帖必须有「保质期意识」+ 官方复核**（引用带日期，用官方文档 / mcp-nixos 复核）。
>
> **★ 六个引用反模式**（§40.11）：拿年度榜当学习资料（**r/NixOS 年度榜 25 条几乎全是玩梗帖** —— *"chads use nix"* / *"NixOS made me lose my wife"*）· 用 RSS 做热度排序 · 照抄版本号 · 把社区帖当官方立场 · 以为知道 Discord 话题分布 · 试图绕过付费墙。
>
> **★ 自我限制（诚实声明）**：**本轮未独立复现任何一条社区帖的故障或修复** —— 所有社区结论均为「**引用 + 官方交叉核对**」，非本机实测。`1mgj1dw`（mesa-git 对 RDNA4 最高 +41%）等性能数字**附作者自述** *"it was only one iteration per case so there could be measurement errors"*。**Discord 频道内容（需 bot token）仍是未完成项。**

## 约定

- frontmatter 必填：`id` / `title` / `tags` / `created` / `updated` / `version` / `status` / `source` / `confidence`
- 正文结构：一句话结论 → 分主题（表格优先）→ 可复用操作 → 坑与反直觉 → 未核实/存疑
- `confidence` 取值：`已核实` / `社区实证` / `推断`
- 提炼，不复制对话痕迹；数据带口径与日期；结论标核实状态
