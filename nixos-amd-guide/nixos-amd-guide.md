# NixOS 教学指南（AMD 平台 · 中文用户 · Vibe Coding）

### 从装机到日常：AMD 显卡 / AMD CPU / Realtek 有线网卡 / GNOME 与 KDE / Flatpak / Steam / AI Agent 管理

| 项 | 值 |
|---|---|
| 适用版本 | NixOS 26.05「Yarara」（2026-05-30 发布，安全支持至 2026-12-31） |
| 下一版本 | NixOS 26.11「Zokor」（2026 年 11 月底） |
| 硬件画像 | **AMD 显卡 + AMD CPU + Realtek 有线网卡**（无 NVIDIA、无无线） |
| 用户画像 | 中文用户 · GNOME 或 KDE · Flatpak · Steam · Vibe Coding |
| 文档版本 | 1.9 |
| 核实日期 | 2026-10-12（**第八轮：以官方手册 stable 的结构为骨架重排导航，并补齐第二十六～三十五章**，见附录 B.16） |
| 姊妹文档 | `nixos-ops-guide.md`（通用深度手册，含完整理论推导） |

---

## 目录

> [!TIP]
> **先看导航章** → **官方手册骨架导航**（紧接本目录之后）。它把官方手册的 5 个 Part / 177 个叙事章节做成一张双向对照表，你可以**按官方顺序查**，也可以**按本指南顺序学**。

| 章 | 内容 | 你会得到什么 |
|---|---|---|
| **导航** | **官方手册骨架导航** | 官方 5 个 Part ↔ 本指南的**逐条对照表** + 覆盖度 + 缺口清单 |
| **零** | 怎么用这份指南 | 你的硬件画像、证据分级、三条铁律 |
| **一** | NixOS 心智模型速通 | 三个概念解释后面所有报错 |
| **二** | 装机（AMD 平台） | 从 U 盘到首次登录 |
| **三** | AMD 硬件配置 | 显卡 / CPU / 内核 / 监控工具的完整配置 |
| **四** | 网络（Realtek 螃蟹卡） | 驱动选择 + NetworkManager + 国内镜像源 |
| **五** | 中文环境 | locale / 字体 / fcitx5 输入法 |
| **六** | 桌面环境：GNOME vs KDE | 选型对比 + 两套完整配置 |
| **七** | Flatpak | portal 配置 + 三个必知坑 |
| **八** | Steam 与游戏 | AMD 路径 + gamescope + 反作弊现状 |
| **九** | Vibe Coding 工具链 | Hermes / OpenClaw / Codex 的**非 root** 部署 |
| **十** | 让 Agent 管系统 | skills + MCP + 四种权限方案 + 安全护栏 |
| **十一** | 长期运维与跨版本升级 | GC / 混合版本策略 / 自动更新 / 回滚 |
| **十二** | Nix 生态查询工具链 | 五个查询站的分工与实测端点 |
| **十三** | 完整配置（可直接复制） | 一份能直接用的 `configuration.nix` |
| **十四** | 游戏性能榨干 | 内核选型 / scx 调度器 / I/O / Valve 优化 / 反优化清单 |
| **十五** | 语言工具链与编译依赖 | npm / bun / uv / Python / Rust / Go / TS + devShell |
| **十六** | MCP 与 Agent 配套工具 | npm 型 MCP / SearXNG / Playwright / 凭据 |
| **十七** | 安全加固、防病毒与 FHS | SELinux 之问 / ClamAV / 完整 FHS 决策树 |
| **十八** | 不加外部仓库逼近 CachyOS | ananicy-cpp + CachyOS 官方规则 / scx / sysctl 与 udev 逐条翻译 |
| **十九** | 三套管理方案的正确定位 | configuration.nix / flake / home-manager 各管什么 + 一页裁决表 |
| **二十** | flake 进阶 | 多 nixpkgs 输入 / overlay / **只让某个包用 unstable** / `follows` 的坑 / **不用 flake 的三条路** / ⚠️ **第八轮修正：「只滚 mesa」有 ICD 混版本风险（见 §32.6）** |
| **二十一** | **Hermes / OpenClaw 落到 NixOS** | 安装 · 管理 · 自启 · **root 权限边界** · HM · flake · 官方 bash（八问全答） |
| **二十二** | **坑、故障、难点与社区意见** | 666 个 derivation 的构建地狱 / stub-ld / linger 静默失效 / 三方社区态度 |
| **二十三** | **把 NixOS 用成「Bazzite 模式」** | Bazzite 六层软件层级逐条映射 / `nh` 与 `ujust` 对照 / 掌机工具链在 nixpkgs 的现状 / **四个反模式** |
| **二十四** | **openSUSE Aeon 模式：稳定基座 + 最新应用** | 「稳定」的两种含义 / Aeon 技术栈拆解 / **三条路（Flatpak 优先 · 双 nixpkgs · 混合）** / HM 官方 FAQ 的 `pkgsUnstable` 写法 / ⚠️ **第八轮修正：路 C 的「只滚 mesa」见 §24.6 警告** |
| **二十五** | **二进位包与依赖问题：完整手册** | 6 种来源 × 6 类依赖根因 / **★ 26.05 `xorg` 弃用全表** / 诊断命令 / **14 种方案按侵入性排序** / 常见依赖清单 / 程序类型对照 / **三类死路** / 一页速查 |
| **二十六** | **配置语法、抽象、模块化与 Profiles**（官方 Part II 基础层） | 值类型六种 / `{ config, pkgs, ... }:` 是什么 / 点号语法 ↔ 嵌套 set / `let` + `//` + 函数三层抽象 / `imports` 合并规则 / **官方 11 个 profile** / 六个反模式 |
| **二十七** | **文件系统、磁盘加密与存储**（官方 Part II 存储） | `fileSystems.*` 完整语义（**挂不上 = 掉 shell**）/ `nofail` / `neededForBoot` / **LUKS 官方完整流程** / FIDO2 + `systemd-cryptenroll` / SSHFS / Overlayfs / 七个反模式 |
| **二十八** | **用户、组与账户安全**（官方 Part II 用户） | `users.mutableUsers`（**最重要的一个开关**）/ `hashedPassword` 进 store 的风险 / **`/var/lib/nixos` 与 uid 稳定性** / systemd-sysusers / **userborn（官方推荐）** / timekpr-nExT / **与 agent 用户的配合** |
| **二十九** | **服务管理：systemd · systemctl · 日志 · cgroup**（官方 Part III） | systemd 心智模型 / **`systemctl` 全集** / `systemd.packages` / **用户服务 GC 死链陷阱** / 自定义服务与安全加固 / 模板单元 / **`journalctl` 全集** / `loginctl` / **cgroup 与 `MemoryMax`** / kexec |
| **三十** | **系统状态、GC 与故障排查**（官方 Part III） | **必须持久化的路径清单** / journald 持久化 / **`-d` GC 不可逆** / **`/boot` 满了要两步** / **启动问题内核参数全集** / 维护模式 + `nixos-enter` / **回滚三法** / store 损坏 / 二进制缓存 / 七个反模式 |
| **三十一** | **容器管理：NixOS 原生容器**（官方 Part III） | 原生容器 vs Distrobox 对比 / **「not perfectly isolated」的含义** / `nixos-container` 命令全集 / 声明式容器 / 容器网络与 NAT / 与 Waydroid·Podman 的分工 |
| **三十二** | **图形栈：Wayland 与 GPU 加速三件套**（官方 Part II 图形） | Wayland 现状 / **OpenCL（`rocmPackages.clr.icd`）** / **Vulkan（RADV 在 Mesa 里）** / **VA-API（`VAEntrypointVLD`）** / GPU 权限 / **★ ICD 混版本静默失败** / AMD 八段体检脚本 |
| **三十三** | **内核、引导与「系统切换」的内部机制**（官方 Part IV） | **内核会被移除的硬规则** / `zcat /proc/config.gz` / `extraConfig` / sysctl 引号坑 / **★ `nixos-rebuild switch` 的 12 步动作** / `X-*` 单元标志全集 / activation script / `/etc` overlay / Bootspec / 不可切换系统 |
| **三十四** | **写 NixOS 模块与测试**（官方 Part IV） | **「能判断 Agent 写的模块对不对」** / 模块四段式 / `mkOption` 参数 / `types.*` 合并行为 / **★ 优先级精确数字** / `warnings` vs `assertions` / `meta.doc` / `disabledModules` / freeform / **给 Agent 的模块提示词模板** / NixOS Tests |
| **三十五** | **构建镜像：Live ISO、repart 与 Appliance**（官方 Part I 缺口） | 三类频道与升级 / 自动升级的取舍 / **构建 Live ISO（两条路）** / **`nixos-rebuild build-image`** / **`image.repart`** / Nix Store 分区与 Btrfs 子卷 / **Appliance + UKI（没有 `configuration.nix`）** / 六个反模式 |
| **附录** | A 命令速查 · B 出处汇总（**含 B.10 第二轮复核 · B.11 新增四章 · B.12 第四轮双分支实测 · B.13 Bazzite 对照 · B.14 Aeon 对照 · B.15 二进位包与依赖 · B.16 官方手册骨架核实**） · C 未核实项 · D 姊妹文档 · E 可补充方向 | 备查 |

> [!TIP]
> **时间估算**：全新安装 + 跑通本文全部配置，**约 3–4 小时**（含下载时间）。其中装机约 40 分钟，配置与调试约 2–3 小时。
>
> **如果你只想先跑起来**：读零章 → 第二章装机 → 直接抄第十三章的配置 → 回来补第三到十二章的原理。

---

## 官方手册骨架导航（本指南 ↔ NixOS 26.05 Manual）

本章是**全文的第一入口**，也是第七轮的成果之一。

**你的原话**：**「从官方文档补充资料 / 以官方文档的结构为骨架重新修正你的指南」**。

本章做三件事：

1. **把官方手册的完整骨架搬过来**（5 个 H1 正文部分 + **177 个叙事章节** + 80 个三级节），你可以按官方顺序查
2. **给出「官方章节 ↔ 本指南章节」的逐条对照表**，标出覆盖度
3. **标出缺口，并在第二十六～三十五章补齐**

> [!NOTE]
> **本章的数字是实测的，不是估的。**
>
> 核实方法：把 <https://nixos.org/manual/nixos/stable/> 下载到本地（1,200,007 字节），用脚本统计带 `id` 属性的标题：
>
> | 层级 | 总数 | 其中自动生成（`module-*` / `opt-*`） | **叙事章节（本章骨架）** |
> |---|---|---|---|
> | H1 | 11 | 0 | **10**（含「NixOS Manual」总标题 1 个） |
> | H2 | 491 | 314 | **177** |
> | H3 | 147 | 67 | **80** |
> | H4 | 44 | 10 | **34** |
>
> **`module-*` / `opt-*` 就是官方那句 *"generated from `meta.doc`"* 的产物**（本指南 §34.7）—— 它们不属叙事骨架，是选项参考。
>
> **官方手册 stable 版本 = NixOS 26.05** —— 与本指南同版本，这是本章能逐条对照的前提。

> [!IMPORTANT]
> **一个必须先说清的事实：本指南的章节顺序 ≠ 官方手册的顺序，这是故意的。**
>
> 官方手册是**参考手册**（reference）：按「安装 → 配置 → 管理 → 开发」组织，适合**查**。
> 本指南是**教学指南**（tutorial）：按「先跑起来 → 再理解 → 最后优化」组织，适合**学**。
>
> **两者不冲突，且互补。** 本章的作用是让你在两套结构之间自由跳转 —— **想学就按本指南顺序读，想查就按官方结构跳。**

### 导航 1 · 官方手册的骨架（4 个正文部分）

| 官方 Part | 锚点 | 官方章节数 | 本指南对应 | 缺口 |
|---|---|---|---|---|
| **Preface** | `preface` | 1 | 零章 | — |
| **Part I · Installation** | `ch-installation` | 17 | 第二章 | ⚠️ **5 项**（ISO 构建 / build-image / systemd-repart / Nix Store Paths / Appliance） |
| **Part II · Configuration** | `ch-configuration` | 100+ | 一/三/四/五/六/七/八/九/十三/十四/十五/十六/十七/十八/十九/二十/二十一/二十三/二十四/二十五 | ⚠️ **10 项**（配置语法 / 模块化 / Profiles / 文件系统 / LUKS / 用户管理 / Wayland / GPU 加速 / 内核 / 引导后端） |
| **Part III · Administration** | `ch-running` | 26 | 十一/二十二 | ⚠️ **9 项**（systemctl / 日志 / 用户会话 / cgroup / 系统状态 / GC / boot entries / 容器 / 故障排查五节） |
| **Part IV · Development** | `ch-development` | 30 | —（空白） | ⚠️ **全部**（写模块 / 选项类型 / 断言 / NixOS Tests / 系统切换内部） |
| **Part V · Contributing** | （5 个 H1） | 5 | — | ➖ **不适用**（贡献给 nixpkgs 本身，非用户场景） |

> [!TIP]
> **`module-*` 章节是什么**：官方手册里还有 **300+ 个自动生成的服务文档**（`module-services-*`，如 `module-services-networking-dnsmasq`）。它们由各 NixOS 模块的 `meta.doc` 生成，**不在上面的骨架里**。查它们用 `man configuration.nix` 或 <https://search.nixos.org/options> 更高效。

---

### 导航 2 · 逐条对照表：官方 Part I · Installation

| # | 官方章节（锚点） | 本指南 | 状态 |
|---|---|---|---|
| 1 | Obtaining NixOS（`sec-obtaining`） | §2.1–2.3 | ✅ |
| 2 | Installing NixOS（`sec-installation`） | §2.4–2.9 | ✅ |
| 3 | Booting from the install medium（`sec-installation-booting`） | §2.5 | ✅ |
| 4 | Graphical Installation（`sec-installation-graphical`） | §2.6 | ✅ |
| 5 | Manual Installation（`sec-installation-manual`） | §2.7–2.8 | ✅ |
| 6 | Additional installation notes（`sec-installation-additional-notes`） | §2.9 | ⚠️ 部分 |
| 7 | Changing the Configuration（`sec-changing-config`） | §11.2 + 第十三章 | ✅ |
| 8 | Upgrading NixOS（`sec-upgrading`） | §11.3–11.5 | ✅ |
| 9 | Automatic Upgrades（`sec-upgrading-automatic`） | §11.6 | ✅ |
| 10 | Building a NixOS (Live) ISO（`sec-building-image`） | — | 🆕 **§35.2** |
| 11 | Practical Instructions（`sec-building-image-instructions`） | — | 🆕 **§35.2** |
| 12 | Additional drivers or firmware（`sec-building-image-drivers`） | §2.10 | ⚠️ 部分 |
| 13 | Technical Notes（`sec-building-image-tech-notes`） | — | 🆕 **§35.2** |
| 14 | Building Images with `nixos-rebuild build-image`（`sec-image-nixos-rebuild-build-image`） | — | 🆕 **§35.3** |
| 15 | Building Images via systemd-repart（`sec-image-repart`） | — | 🆕 **§35.4** |
| 16 | Nix Store Paths（`sec-image-repart-store-paths`） | — | 🆕 **§35.5** |
| 17 | Appliance Image（`sec-image-repart-appliance`） | — | 🆕 **§35.6** |

### 导航 3 · 逐条对照表：官方 Part II · Configuration

**基础层（官方 §1–11）**

| # | 官方章节 | 本指南 | 状态 |
|---|---|---|---|
| 1 | Configuration Syntax（`sec-configuration-syntax`） | — | 🆕 **§26.1–26.3** |
| 2 | NixOS Configuration File（`sec-configuration-file`） | 第一章 + 第十三章 | ⚠️ 部分 → 🆕 **§26.2** |
| 3 | Abstractions（`sec-module-abstractions`） | — | 🆕 **§26.4** |
| 4 | Modularity（`sec-modularity`） | 第十九章 | ⚠️ 部分 → 🆕 **§26.5–26.7** |
| 5 | Package Management（`sec-package-management`） | 第十九/二十五章 | ✅ |
| 6 | Declarative Package Management（`sec-declarative-package-mgmt`） | §19.2 | ✅ |
| 7 | Ad-Hoc Package Management（`sec-ad-hoc-packages`） | §19.3 | ✅ |
| 8 | User Management（`sec-user-management`） | 第九章（agent 用户） | ⚠️ 部分 → 🆕 **第二十八章** |
| 9 | systemd-sysusers（`sec-systemd-sysusers`） | — | 🆕 **§28.5** |
| 10 | userborn（`sec-userborn`） | — | 🆕 **§28.6** |
| 11 | Restrict usage time（`sec-restrict-usage-time`） | — | 🆕 **§28.7** |

**存储与图形（官方 §12–29）**

| # | 官方章节 | 本指南 | 状态 |
|---|---|---|---|
| 12 | File Systems（`ch-file-systems`） | 第二章（安装时生成） | ⚠️ 部分 → 🆕 **§27.1** |
| 13 | LUKS-Encrypted File Systems（`sec-luks-file-systems`） | — | 🆕 **§27.2–27.3** |
| 14 | SSHFS File Systems（`sec-sshfs-file-systems`） | — | 🆕 **§27.4** |
| 15 | Overlayfs（`sec-overlayfs`） | — | 🆕 **§27.5** |
| 16 | X Window System（`sec-x11`） | 第六章 | ⚠️ 部分 |
| 17 | Auto-login（`sec-x11-auto-login`） | §6.6 | ✅ |
| 18 | Running X without a display manager（`sec-x11-startx`） | — | ➖ 低相关（你是桌面用户） |
| 19 | Intel Graphics drivers | — | ➖ 不适用（AMD） |
| 20 | Proprietary NVIDIA drivers | — | ➖ 不适用（AMD） |
| 21 | Touchpads（`sec-x11-touchpads`） | §3.8 | ✅ |
| 22 | GTK/Qt themes（`sec-x11-gtk-and-qt-themes`） | §6.7 | ✅ |
| 23 | Custom XKB layouts | — | ➖ 低相关 |
| 24 | **Wayland**（`sec-wayland`） | §6.2 | ⚠️ 部分 → 🆕 **§32.1** |
| 25 | **GPU acceleration**（`sec-gpu-accel`） | §3.3 | ⚠️ 部分 → 🆕 **第三十二章** |
| 26 | OpenCL（`sec-gpu-accel-opencl`） | §3.4（ROCM） | ⚠️ 部分 → 🆕 **§32.2** |
| 27 | Vulkan（`sec-gpu-accel-vulkan`） | §3.3 | ✅ → 🆕 **§32.3** |
| 28 | VA-API（`sec-gpu-accel-va-api`） | §3.5 | ✅ → 🆕 **§32.4** |
| 29 | Common issues（`sec-gpu-accel-common-issues`） | — | 🆕 **§32.5–32.6** |
| 30 | Xfce Desktop Environment（`sec-xfce`） | — | ➖ 低相关（你选 GNOME/KDE） |
| 33 | **Networking**（`sec-networking`） | 第四章 | ✅ |
| 34 | NetworkManager（`sec-networkmanager`） | §4.3 | ✅ |
| 35 | Secure Shell Access（`sec-ssh`） | §4.9 | ✅ |
| 36 | IPv4 Configuration（`sec-ipv4`） | §4.4 | ✅ |
| 37 | IPv6 Configuration（`sec-ipv6`） | §4.4 | ✅ |
| 38 | Firewall（`sec-firewall`） | §4.6 | ✅ |
| 39 | Wireless Networks（`sec-wireless`） | — | ➖ 不适用（你有线） |
| 40 | Ad-Hoc Configuration（`ad-hoc-network-config`） | §4.5 | ✅ |
| 41 | Renaming network interfaces（`sec-rename-ifs`） | §4.7 | ✅ |
| 42 | **Linux Kernel**（`sec-kernel-config`） | 第三章 + 第十四章 | ⚠️ 部分 → 🆕 **§33.1–33.4** |
| 43 | Building a custom kernel（`sec-linux-config-customizing`） | §14.2 | ⚠️ 部分 → 🆕 **§33.3** |
| 44 | Rust（`sec-linux-rust`） | §15.6 | ✅ |
| 45 | Developing kernel modules（`sec-linux-config-developing-modules`） | — | ➖ 官方已移到 Nixpkgs 手册 |
| 46 | ZFS（`sec-linux-zfs`） | — | ➖ 不适用（单盘 ext4） |
| 47 | **GNOME Desktop**（`chap-gnome`） | 第六章 | ✅ |
| 48–53 | GNOME 子节（Flashback / 图标 / 扩展 / GSettings / FAQ） | §6.4–6.8 | ✅ |
| 54–55 | Pantheon Desktop | — | ➖ 低相关 |
| 56–57 | External Bootloader Backends | §33.9（Bootspec） | ⚠️ 部分 |
| 58 | **Profiles**（`ch-profiles`） | — | 🆕 **§26.8** |

**服务类章节（官方 §59+）**：Nextcloud / GotoSocial / Akkoma / Certspotter / Trezor / Mattermost / Kubernetes / Szurubooru / Suwayomi / strfry / Plausible / Pi-hole / Pict-rs / Garage / Clevis / Xen / tpm2-totp 等 **100+ 个**。

> [!NOTE]
> **这一大块本指南不覆盖，且是刻意的。** 它们是**服务器向**的自托管服务，与你「AMD 桌面 + 中文 + 游戏 + Vibe Coding」的画像无关。
>
> **要查它们，直接用 `man configuration.nix` 搜选项名**，比在手册里翻快得多。

### 导航 4 · 逐条对照表：官方 Part III · Administration

| # | 官方章节 | 本指南 | 状态 |
|---|---|---|---|
| 1 | **Service Management**（`sec-systemctl`） | — | 🆕 **§29.1** |
| 2 | Interacting with a running systemd（`sect-nixos-systemd-general`） | — | 🆕 **§29.2** |
| 3 | systemd in NixOS（`sect-nixos-systemd-nixos`） | §10.6（部分） | 🆕 **§29.3–29.5** |
| 4 | Rebooting and Shutting Down（`sec-rebooting`） | §11.8 | ✅ → 🆕 **§29.9** |
| 5 | User Sessions（`sec-user-sessions`） | — | 🆕 **§29.7** |
| 6 | Control Groups（`sec-cgroups`） | §14.9（scx 部分） | ⚠️ 部分 → 🆕 **§29.8** |
| 7 | **Logging**（`sec-logging`） | — | 🆕 **§29.6** |
| 8 | Necessary system state（`ch-system-state`） | — | 🆕 **§30.1–30.2** |
| 9 | NixOS state（`sec-nixos-state`） | §11.3 | ⚠️ 部分 → 🆕 **§30.1** |
| 10 | systemd state（`sec-systemd-state`） | — | 🆕 **§30.1** |
| 11 | ZFS state（`sec-zfs-state`） | — | ➖ 不适用 |
| 12 | **Cleaning the Nix Store**（`sec-nix-gc`） | §11.4 | ⚠️ 部分 → 🆕 **§30.3–30.4** |
| 13 | NixOS Boot Entries（`sect-nixos-gc-boot-entries`） | §11.5 | ✅ → 🆕 **§30.5** |
| 14 | **Container Management**（`ch-containers`） | §23.7（Distrobox） | ⚠️ 不同东西 → 🆕 **第三十一章** |
| 15 | Imperative Container Management（`sec-imperative-containers`） | — | 🆕 **§31.3** |
| 16 | Declarative Container Specification（`sec-declarative-containers`） | — | 🆕 **§31.4** |
| 17 | Container Networking（`sec-container-networking`） | — | 🆕 **§31.5** |
| 18 | **Troubleshooting**（`ch-troubleshooting`） | 第二十二章 | ⚠️ 部分（那章是 agent 向） → 🆕 **第三十章** |
| 19 | Boot Problems（`sec-boot-problems`） | §22.9 | ⚠️ 部分 → 🆕 **§30.6** |
| 20 | Maintenance Mode（`sec-maintenance-mode`） | — | 🆕 **§30.7** |
| 21 | Rolling Back Configuration Changes（`sec-rollback`） | §11.7 | ✅ → 🆕 **§30.8** |
| 22 | Nix Store Corruption（`sec-nix-store-corruption`） | — | 🆕 **§30.9** |
| 23 | Network Problems（`sec-nix-network-issues`） | §4.8 | ✅ → 🆕 **§30.10** |

### 导航 5 · 逐条对照表：官方 Part IV · Development

| # | 官方章节 | 本指南 | 状态 |
|---|---|---|---|
| 1 | Getting the Sources（`sec-getting-sources`） | — | 🆕 **§34.1** |
| 2 | **Writing NixOS Modules**（`sec-writing-modules`） | §10.4（概念） | ⚠️ 部分 → 🆕 **§34.2** |
| 3 | Option Declarations（`sec-option-declarations`） | — | 🆕 **§34.3** |
| 4 | Options Types（`sec-option-types`） | — | 🆕 **§34.4** |
| 5 | Option Definitions（`sec-option-definitions`） | §19.4（优先级） | ⚠️ 部分 → 🆕 **§34.5** |
| 6 | Warnings and Assertions（`sec-assertions`） | §22.4（部分） | ⚠️ 部分 → 🆕 **§34.6** |
| 7 | Meta Attributes（`sec-meta-attributes`） | — | 🆕 **§34.7** |
| 8 | Importing Modules（`sec-importing-modules`） | §19.5 | ✅ |
| 9 | Replace Modules（`sec-replace-modules`） | — | 🆕 **§34.8** |
| 10 | Freeform modules（`sec-freeform-modules`） | — | 🆕 **§34.9** |
| 11 | Options for Program Settings（`sec-settings-options`） | — | 🆕 **§34.10** |
| 12 | Building Specific Parts of NixOS（`sec-building-parts`） | §11.5（部分） | ⚠️ 部分 |
| 13 | **Bootspec**（`sec-bootspec`） | — | 🆕 **§33.9** |
| 17 | **What happens during a system switch?**（`sec-switching-systems`） | — | 🆕 **§33.5** |
| 18 | Unit handling（`sec-unit-handling`） | — | 🆕 **§33.6** |
| 19 | Activation script（`sec-activation-script`） | — | 🆕 **§33.7** |
| 20 | Non Switchable Systems（`sec-non-switchable-system`） | — | 🆕 **§33.10** |
| 21 | `/etc` via overlay filesystem（`sec-etc-overlay`） | — | 🆕 **§33.8** |
| 22–23 | Writing NixOS Documentation / Building the Manual | — | ➖ 贡献向 |
| 24 | **NixOS Tests**（`sec-nixos-tests`） | — | 🆕 **§34.11** |
| 25 | Writing Tests（`sec-writing-nixos-tests`） | — | 🆕 **§34.11** |
| 26 | Running Tests（`sec-running-nixos-tests`） | — | 🆕 **§34.11** |
| 27–32 | Test 驱动开发 / 安装器测试 | — | ➖ 贡献向 |
| 33+ | Modular Services / Portability / Migration | — | ➖ 贡献向 |

### 导航 6 · 缺口汇总（本轮新增的十章）

| 新章节 | 对应官方 Part | 补的是什么 | 对你为什么有用 |
|---|---|---|---|
| **二十六** | Part II 基础层 | 配置语法 / 抽象 / 模块化 / Profiles | **看懂别人的 `configuration.nix`**；把大配置拆开；知道 `mkForce` 什么时候用 |
| **二十七** | Part II 存储 | `fileSystems.*` 语义 / LUKS / SSHFS / Overlayfs | **装机时选错分区方案会丢数据**；想加密时知道官方流程 |
| **二十八** | Part II 用户 | 声明式用户 / `mutableUsers` / userborn | **agent 用户的正确建法**（连第九章） |
| **二十九** | Part III 前半 | systemd / systemctl / 日志 / cgroup | **出问题时知道去哪看**（journalctl 是最常用的诊断入口） |
| **三十** | Part III 后半 | 系统状态 / GC / 故障排查五节 | **开不了机时的完整逃生手册** |
| **三十一** | Part III 容器 | NixOS 原生容器 | 与 Distrobox 的区别；跑服务不污染宿主 |
| **三十二** | Part II 图形 | Wayland / OpenCL / Vulkan / VA-API | **AMD 用户的硬件加速验证**（Blender、视频解码、游戏） |
| **三十三** | Part IV | 内核 / 系统切换内部 / Bootspec | **理解 `nixos-rebuild switch` 到底做了什么**（报错时能读懂） |
| **三十四** | Part IV | 写模块 / 选项类型 / 断言 / 测试 | **让 Agent 帮你写模块的前提**（连第十章） |
| **三十五** | Part I 缺口 | ISO / 镜像 / Appliance / 频道 | 想给别人做装机盘、或做不可变设备时用 |

> [!TIP]
> **阅读建议**：
> - **纯用户** → 只读 **二十九**（日志）和 **三十**（故障排查），这两章日常最常用
> - **想深入** → 加读 **二十六**（语法）和 **三十三**（系统切换内部），这两章解释「为什么」
> - **想改 nixpkgs / 让 Agent 写模块** → 加读 **三十四**
> - **装机前** → 先读 **二十七**（文件系统与加密）

---

---

## 零、怎么用这份指南

### 0.1 你的硬件画像决定了「哪些坑你根本不会踩」

这份指南是**为你的具体配置写的**。市面上大量 NixOS 教程是 NVIDIA 视角写的，里面有一半内容对你**完全不适用**：

| 常见教程内容 | 对你 | 原因 |
|---|---|---|
| `hardware.nvidia.*` 全套配置 | ❌ 完全不需要 | AMD 用内核自带的 `amdgpu` + Mesa |
| `nixpkgs.config.allowUnfree` 为驱动而设 | ⚠️ 仍可能需要 | 但原因是 Steam / 部分软件，**不是显卡驱动** |
| NVIDIA 驱动的「内核模块必须与内核同版本」 | ❌ 不存在这个问题 | amdgpu 在主线内核里，**升级内核不炸显卡** |
| 无线网卡固件 / `hardware.enableRedistributableFirmware` | ⚠️ 视网卡型号 | 你有线连接，但部分 Realtek 仍需固件 |
| 屏幕撕裂的 X11 `TearFree` 配置 | ⚠️ 取决于会话类型 | Wayland 下不需要 |
| 双显卡切换（Optimus / PRIME） | ❌ 不存在 | 单 AMD 显卡 |

> [!TIP]
> **AMD 是 Linux 桌面最省心的选择。** 显卡驱动在主线内核里，不需要 `allowUnfree`，不需要版本配对，升级内核不会把显卡搞挂。你选对了硬件。

**这份指南里所有 AMD 相关内容都基于「单张 AMD 显卡 + AMD CPU + 有线网卡」这个前提。** 如果你后续加了 NVIDIA 独显或换了无线网卡，需要回到姊妹文档 `nixos-ops-guide.md` 补对应章节。

### 0.2 证据分级（全文遵守）

这份指南的**每一条结论都标了来源**。你看到的方括号标记含义如下：

- `[官方]` = nixos.org 手册、nix.dev、官方 API 文档
- `[官方选项]` = search.nixos.org 的选项定义页
- `[官方论坛]` = 官方 Discourse 帖（一手讨论，非官方结论）
- `[Wiki]` = wiki.nixos.org / nixos.wiki 社区 Wiki
- `[仓库]` = 项目自身 GitHub README / issue / 源码
- `[社区]` / `[社区实证]` = 第三方讨论、博客、实测报告
- `[核实]` / `[核实·源码]` = 本文撰写时**实测**或**逐条比对源码**确认
- `[未核实]` / `[未找到]` = 无法从一手来源确认，**已明确标注**

> [!WARNING]
> **NixOS 迭代很快，选项名会变。** 网上 2023 / 2024 年的教程里有相当一部分选项名已经失效或重命名（例如 `hardware.opengl` → `hardware.graphics`，24.11 起）。本指南全部基于 **26.05** 核对。看到老教程时，先到 search.nixos.org 确认选项是否还存在。

### 0.3 三条铁律（先记住，能省你几天时间）

> [!IMPORTANT]
> **铁律 1：`system.stateVersion` 装上是什么就永远是什么。**
> 它记录的是「你**初次安装**时的版本」，不是「当前版本」。官方原文：*"Most users should never change this value after the initial install, for any reason, even if you've upgraded your system."* 改了会触发数据迁移逻辑，可能损坏数据库。

> [!IMPORTANT]
> **铁律 2：flake 的文件必须先 `git add` 才可见。**
> 这是新手第一大坑。`flake.nix` 及同目录下任何文件，如果没被 git 跟踪，Nix 会**当作不存在**。你会看到「明明文件在，却说找不到」的错误。

> [!IMPORTANT]
> **铁律 3：改配置先 `dry-build`，不要直接 `switch`。**
> `sudo nixos-rebuild dry-build` 只做求值和计划，**不碰你的系统**。它是零成本的验证闸门 —— 尤其当配置是 AI 生成的时候。

### 0.4 本指南的阅读路线

| 你是谁 | 建议路线 |
|---|---|
| **全新安装** | 从头顺序读：零 → 一 → 二 → 三 → … |
| **已有 NixOS，只想调某块** | 直接跳到对应章：显卡跳三、中文跳五、桌面跳六、Steam 跳八 |
| **只想抄一份能用的配置** | 直接看**第十三章**的完整配置，回头再补理论 |
| **想让 AI 帮我管系统** | 读**第九、十、十二章**，然后回到零章看铁律 |

---

## 一、NixOS 心智模型速通

初学者 90% 的困惑来自没搞清三个概念。搞清之后，后面所有「为什么跑不起来」「为什么能回滚」都变成自然推论。

### 1.1 derivation —— 构建配方

**是什么**：derivation 是一份「构建配方」，描述「用什么输入、跑什么命令、产出什么路径」。执行后产物被放进 `/nix/store`。

**为什么重要**：产物路径由输入（名字、构建脚本、全部依赖）的哈希决定，所以**同样的输入必然得到同样的路径**。这就是「可复现」的物理基础。

路径格式是 `/nix/store/<32 字符哈希>-<名字>`，例如 `/nix/store/1a2b...-firefox-142.0`。官方明确说这个哈希「应当被当作不透明标识符」，不要试图解读它。

> 出处：[nix.dev · Store Path](https://nix.dev/manual/nix/stable/store/store-path.html) `[官方]`

### 1.2 没有 `/usr/lib` —— 解释你将来遇到的所有报错

**关键事实**：NixOS **不遵循 FHS（Filesystem Hierarchy Standard）**。没有 `/usr/lib`，没有 `/lib64/ld-linux-x86-64.so.2`。

**为什么会导致报错**：Linux 的 ELF 可执行文件把「动态链接器路径」**硬编码在文件头里**。普通发行版的二进制写着 `/lib64/ld-linux-x86-64.so.2`，NixOS 没这个文件 → 运行时报一个极具误导性的错误：

```
bash: ./some-binary: No such file or directory
```

文件明明存在，却报「找不到文件」。这不是文件缺失，是**它依赖的链接器缺失**。

**Nix 的解法**：打包时用 `patchelf` 改写 ELF 的 interpreter 和 RPATH，指向 `/nix/store` 里的 glibc。

> 出处：[NixOS Wiki · Packaging/Binaries](https://wiki.nixos.org/wiki/Packaging/Binaries) `[Wiki]`；[github.com/NixOS/patchelf](https://github.com/NixOS/patchelf) `[仓库]`

> [!NOTE]
> **这个事实直接决定了第九、十章的全部内容。** 任何「官方下载的二进制」（包括 Hermes Agent 下载的 Node / Chromium）都需要某种方式补上 FHS 环境。AMD 显卡不改变这一点 —— 它只影响显卡驱动。

### 1.3 generation —— 回滚能力的来源

每次 `nixos-rebuild switch` 都会：

1. 构建新的系统 closure（一整棵依赖树）
2. 在 `/nix/var/nix/profiles/system` 下追加一个新 generation
3. 往 bootloader 菜单里加一条启动项

**为什么回滚可靠**：`/nix/store` 里的内容不可变且内容寻址，旧 generation 指向的路径在被 GC 之前**始终存在且内容不变**。所以回滚是「原子切换一个符号链接」，不是「重新安装旧版本」。

传统发行版升级会**就地覆盖** `/usr` 下的文件，覆盖后旧版本就没了 → 回滚不可靠。这是 NixOS 最核心的运维红利。

> 出处：[NixOS Wiki · nixos-rebuild](https://wiki.nixos.org/wiki/Nixos-rebuild) `[Wiki]`

```bash
# 列出系统所有 generation
sudo nixos-rebuild list-generations
# 旧写法（仍可用）
sudo nix-env --list-generations --profile /nix/var/nix/profiles/system

# 回滚到上一个 generation 并立即生效
sudo nixos-rebuild switch --rollback
```

### 1.4 nixos-rebuild 的七个子命令（必须分清）

| 子命令 | 构建 | 立即激活 | 进 bootloader 菜单 | 典型用途 |
|---|---|---|---|---|
| `switch` | ✅ | ✅ | ✅ | 日常改配置 |
| `boot` | ✅ | ❌ | ✅ | 改内核/驱动，重启才生效 |
| `test` | ✅ | ✅ | ❌ | **临时试，重启即失效** |
| `build` | ✅ | ❌ | ❌ | 只验证能否构建成功 |
| `dry-build` | ✅(仅求值+计划) | ❌ | ❌ | **验证闸门，AI 改配置后必用** |
| `dry-activate` | ✅ | ❌ | ❌ | 预览「激活会做哪些动作」 |
| `build-vm` | ✅ | — | — | 生成 QEMU 虚拟机，真跑一遍 |

> 出处：[NixOS Wiki · nixos-rebuild](https://wiki.nixos.org/wiki/Nixos-rebuild) `[Wiki]`；[NixOS Manual · Changing the Configuration](https://nixos.org/manual/nixos/stable/#sec-changing-config) `[官方]`

> [!TIP]
> **`test` 是新手的护身符。** 不确定一个改动会不会搞坏系统时，用 `sudo nixos-rebuild test` —— 立即生效，但**重启就恢复原样**。试完确认没问题，再 `switch` 固化。

---

## 二、装机（AMD 平台）

### 2.1 为什么 AMD 平台的装机比 NVIDIA 简单

安装过程本身**与显卡无关** —— NixOS 安装器不装专有驱动，它用的是内核自带的 `amdgpu`。你开机进图形安装器时，桌面已经由 Mesa 驱动起来了。

**AMD 平台装机比 NVIDIA 少做三件事**：

1. 不需要在安装阶段禁用 `nouveau`
2. 不需要事后 `allowUnfree` 来装专有驱动
3. 不需要担心「驱动版本 vs 内核版本」配对

> [!NOTE]
> **唯一的例外**：如果你的 AMD 显卡非常新（RDNA4 及更新，或发布不足一年的型号），安装器的内核可能太旧认不出它。这种情况见 **§3.3 内核选择**。表现为：安装器能进但分辨率不对，或者黑屏。

### 2.2 安装前的准备

| 准备项 | 说明 |
|---|---|
| U 盘 | ≥ 4 GB，会被清空 |
| ISO | 从 https://nixos.org/download 下 **Graphical ISO**（图形版，带安装器） |
| 写盘工具 | Windows 用 **Rufus**（选 DD 模式）或 **balenaEtcher** |
| 备份 | 目标盘上的数据会被清空 |
| 网络 | **有线连接**（你正好是 —— 装完即通，不用配无线） |

> 出处：[NixOS Manual · Installation](https://nixos.org/manual/nixos/stable/#sec-installation) `[官方]`

> [!WARNING]
> **写 U 盘时选 DD 模式（Rufus）或「直接写入」。** ISO 模式写出来的盘在部分主板上无法引导 NixOS。这是最常见的一次性失败原因。

### 2.3 安装过程（图形安装器）

NixOS 的图形安装器（Calamares）流程和别的发行版类似：

1. **语言 / 键盘** —— 选中文或英文都行，**这个选择只影响安装器本身**，装完后系统语言由配置决定（见第五章）
2. **时区** —— 选 `Asia/Shanghai`
3. **键盘布局** —— 中文用户通常选 `English (US)`（物理键盘是美式），中文输入由输入法解决
4. **分区** —— 见下方「分区方案」
5. **用户与密码** —— 创建一个管理员账户，勾选「需要密码登录」之外的选项按需
6. **桌面环境** —— 这一步的选择**装完后可以在配置里改**，但先选一个能进系统的（GNOME 或 KDE Plasma）
7. **确认并安装** —— 约 10–20 分钟

> 出处：[NixOS Manual · Installation](https://nixos.org/manual/nixos/stable/#sec-installation) `[官方]`

**分区方案（单盘推荐）**：

| 挂载点 | 大小 | 类型 | 说明 |
|---|---|---|---|
| `/boot` | 1 GB | FAT32 | EFI 系统分区（ESP） |
| `/` | 剩余 | ext4 | 根分区 |
| swap | = 内存大小 | swap | 可选；有足够内存可省略 |

> [!TIP]
> **不用手工分区，让安装器自动分。** 图形安装器提供「擦除磁盘」选项，它会自动创建上面这套布局。手工分区的价值只在你需要多系统或特殊布局时体现。
>
> **关于 btrfs**：如果你想用 NixOS 的**快照回滚**能力（配合 `nixos-enter` 之外的方案），btrfs + 子卷是进阶选择。但 NixOS 自身的 generation 机制**已经提供了回滚**，所以 ext4 对新手更简单。

### 2.4 首次启动后的第一件事

装完重启，你会看到一个**几乎什么都没有的系统**。这是正常的 —— NixOS 默认只装最基础的东西。

**第一步：确认系统版本和基本状态**

```bash
# 确认版本
nixos-version
# 输出形如：26.05.1234.abcd1234 (Yarara)

# 确认显卡被正确识别（AMD 用户关键一步）
lspci | grep -i vga
# 应该看到你的 AMD 显卡，且驱动是 amdgpu

# 确认网卡
ip link
# 应该看到 enp* 或 eth* 之类的有线网卡，状态 UP
```

**第二步：把你的配置文件纳入版本控制**

NixOS 的配置在 `/etc/nixos/`。**在改任何东西之前先做这一步** —— 它让你随时能对比「改了什么」。

```bash
# 让普通用户能读写配置目录
sudo chown -R $USER:users /etc/nixos
cd /etc/nixos
git init
git add .
git commit -m "initial NixOS 26.05 config"
```

> [!TIP]
> **这一步是「可回滚」的第二层保险。** NixOS 的 generation 能回滚**系统**，git 能回滚**你的配置文本**。两者互补：generation 回滚后你还是想知道「上次改了什么」，答案在 git 里。

**第三步：把配置改成 flake 形式（推荐，见第十一章）**

先不急。**先用 `configuration.nix` 单体把系统跑起来、确认硬件正常**，再考虑迁移到 flake。顺序反了会同时引入两个变量，出问题不好定位。

---

## 三、AMD 硬件配置

> 本章全部结论以 **nixpkgs `nixos-26.05` 分支源码**为准（逐条比对模块文件），而非网上教程。

### 3.1 显卡：AMD 在 NixOS 上几乎开箱即用

**官方 Wiki 原文**：*"For ordinary desktop / gaming usage, AMD GPUs are expected to work out of the box."*

**但有一个反直觉的坑**：`hardware.graphics.enable` **默认是 `false`**，而且 **GNOME 和 KDE 模块都不会自动帮你开**（源码里对 `hardware.graphics` 的引用数 = **0**）。**必须手写。**

```nix
hardware.graphics = {
  enable = true;        # ⚠️ 默认 false，必须显式写
  enable32Bit = true;   # 32 位驱动 —— Steam / Wine 必需（x86_64 专用）
};
```

> [!NOTE]
> **「谁会替你开 `hardware.graphics.enable`」——完整清单（源码级，共 3 处）**
>
> 选项自己的描述写着 *"This option should be enabled by default by the corresponding modules"*（`graphics.nix:62-63`），但**实际做到的只有 3 个模块**，且**都不是桌面环境**：
>
> | 触发条件 | 赋值方式 | 源码位置 |
> |---|---|---|
> | `programs.steam.enable = true` | **硬赋值**（`enable = true; enable32Bit = true;`） | `programs/steam.nix:205-210` |
> | `hardware.amdgpu.opencl.enable = true`（ROCm） | `lib.mkDefault true` + 注入 `rocmPackages.clr` | `services/hardware/amdgpu.nix:62-70` |
> | `hardware.amdgpu.zluda.enable = true`（CUDA on AMD） | `lib.mkDefault true` + 注入 `zluda` | `services/hardware/amdgpu.nix:71-76` |
>
> **GNOME（`services/desktop-managers/gnome.nix`，569 行）与 Plasma 6（`services/desktop-managers/plasma6.nix`，410 行）里，`hardware.graphics` / `hardware.opengl` 的出现次数都是 0。** 这就是「装了 GNOME 却没有硬件加速、而且不报任何错」的根因。
>
> **AMD 用户的实际含义**：即使你开了 `hardware.amdgpu.opencl.enable`（为了 ROCm），它给的也只是 `mkDefault true` —— 你自己的 `hardware.graphics.enable = true` 会正常覆盖它，**不会冲突**。但**桌面环境永远指望不上**，所以 §3.1 的建议（显式写）仍然成立。
>
> 出处：`nixos/modules/hardware/graphics.nix:53-67`、`nixos/modules/services/hardware/amdgpu.nix:47-77`、`nixos/modules/programs/steam.nix:205-210`、`nixos/modules/services/desktop-managers/{gnome,plasma6}.nix`（grep 命中数 0）`[核实·源码]`

> 出处：`nixos/modules/hardware/graphics.nix` `[核实·源码]`；[NixOS Wiki · AMD GPU](https://wiki.nixos.org/wiki/AMD_GPU) `[Wiki]`

**关于 `services.xserver.videoDrivers`**：

> [!DANGER]
> **不要照抄老教程写 `services.xserver.videoDrivers = [ "amdgpu" ];`**
>
> 默认值是 `["modesetting" "fbdev"]`，**`modesetting` 才是现代 AMD 的推荐值**。写 `"amdgpu"` 会切换到**旧的 xf86-video-amdgpu DDX**，反而可能劣化表现。
>
> **唯一的例外**：你需要 X11 的 TearFree 防撕裂时（见 §3.7）—— 因为 TearFree 只有旧 DDX 支持。

> 出处：`nixos/modules/services/x11/xserver.nix:457` `[核实·源码]`

**`hardware.amdgpu.*` 的完整选项清单**（这是 AMD 专属模块，NVIDIA 用户没有对应的东西）：

| 选项 | 默认 | 作用 |
|---|---|---|
| `hardware.amdgpu.initrd.enable` | `false` | 设 `boot.initrd.kernelModules = ["amdgpu"]`，解决**开机初期低分辨率** |
| `hardware.amdgpu.legacySupport.enable` | `false` | 启用 **GCN 1/2 老卡**（HD 7000/8000）的 amdgpu 支持，替代 `radeon` 驱动；会设 `amdgpu.si_support=1` / `amdgpu.cik_support=1` / `radeon.si_support=0` / `radeon.cik_support=0` |
| `hardware.amdgpu.overdrive.enable` | `false` | 设 `amdgpu.ppfeaturemask`，**超频/调风扇的前提** |
| `hardware.amdgpu.overdrive.ppfeaturemask` | `"0xfffd7fff"` | 具体的 feature mask（`example = "0xffffffff"`，但后者更易闪烁） |
| `hardware.amdgpu.opencl.enable` | `false` | 启用 OpenCL（走 ROCm 运行时）；**顺带 `mkDefault` 开 `hardware.graphics.enable`** 并注入 `rocmPackages.clr` |
| `hardware.amdgpu.zluda.enable` | `false` | ZLUDA（CUDA 兼容层），实验性；**顺带 `mkDefault` 开 `hardware.graphics.enable`** |
| `hardware.amdgpu.zluda.package` | `pkgs.zluda` | ZLUDA 的包来源（可覆盖） |

> 出处：`nixos/modules/services/hardware/amdgpu.nix:12-77`（**共 7 个选项**：`legacySupport.enable` / `initrd.enable` / `overdrive.enable` / `overdrive.ppfeaturemask` / `opencl.enable` / `zluda.enable` / `zluda.package`）`[核实·源码]`

> [!NOTE]
> **注意：没有 `amdgpu.dcdebugmask` 和 `amdgpu.gpu_recovery` 这两个模块选项。** 需要它们时必须手写 `boot.kernelParams`。网上说「NixOS 有这个选项」的说法是不准确的。

### 3.2 硬件视频解码（VA-API）—— 你不需要装任何东西

这是 AMD 相对 NVIDIA 的又一个省心之处。

**AMD 的 VA-API 由 Mesa 自带的 `radeonsi` 驱动提供，无需额外安装任何包。** `libva` 已经构建为会搜索 OpenGL 驱动路径，`extraPackages` 里的驱动会被自动发现。

**验证方法**：

```bash
nix-shell -p libva-utils --run vainfo
```

期望看到类似输出：

```
vainfo: Driver version: Mesa Gallium driver 25.x.x for AMD Radeon RX 7xxx
      VAProfileH264ConstrainedBaseline: VAEntrypointVLD
      VAProfileHEVC_Main:               VAEntrypointVLD
      VAProfileAV1Profile0:             VAEntrypointVLD
```

能看到 `VAProfile*` 行就说明硬解可用。**Firefox / Chromium 会自动使用它**，不需要设环境变量。

> [!WARNING]
> **`LIBVA_DRIVER_NAME=radeonsi` 这个环境变量：不必要。** 网上有教程说要设，但官方 26.05 手册与 AMD Wiki **都没有这个要求** —— libva 会自动选择 radeonsi。设了通常无害，但属于多余的「偏方」。`[未核实]`

> 出处：nixpkgs `doc/manual/gpu-accel.chapter.md` `[官方]`

### 3.3 本地跑 LLM（ROCm）—— 可选进阶

如果你想用 AMD 显卡跑 Ollama / PyTorch：

```nix
# 让 Ollama 用 GPU 而不是 CPU
services.ollama = {
  enable = true;
  package = pkgs.ollama-rocm;        # ⚠️ 默认包是 CPU 版，必须显式换成 ROCm 版
  # rocmOverrideGfx = "10.3.0";      # 只在 Ollama 认不出你的卡时才设
};
```

> [!IMPORTANT]
> **`services.ollama.package` 默认是 CPU 版。** 不改成 `pkgs.ollama-rocm` 的话，它会安静地用 CPU 推理 —— 慢几十倍，而且你不会看到明显报错。这是最常见的「为什么我的显卡没用上」原因。
>
> `rocmOverrideGfx` 对应环境变量 `HSA_OVERRIDE_GFX_VERSION`，**只在官方不支持你的 GPU 型号时才需要**。

**ollama 的 4 个加速变体（源码级）**：这些**不是** `pkgs/by-name/ol/` 下的独立目录，而是在 `pkgs/top-level/all-packages.nix:424-427` 用同一个 `package.nix` 加不同 `acceleration` 参数生成的：

```nix
# pkgs/top-level/all-packages.nix:424-427
ollama-cpu    = callPackage ../by-name/ol/ollama/package.nix { acceleration = false; };
ollama-rocm   = callPackage ../by-name/ol/ollama/package.nix { acceleration = "rocm"; };
ollama-cuda   = callPackage ../by-name/ol/ollama/package.nix { acceleration = "cuda"; };
ollama-vulkan = callPackage ../by-name/ol/ollama/package.nix { acceleration = "vulkan"; };
```

| 变体 | 适用 | 说明 |
|---|---|---|
| `pkgs.ollama`（= 无后缀） | **CPU** | 模块默认值就是这个 |
| `pkgs.ollama-rocm` | **AMD 显卡** | 你的场景 |
| `pkgs.ollama-cuda` | NVIDIA | N/A |
| `pkgs.ollama-vulkan` | **跨厂商 GPU**（含 AMD，走 Vulkan） | 比 ROCm 兼容面更广、性能通常略低；**ROCm 跑不起来时可作后备** |

> ⚠️ 旧的 `services.ollama.acceleration` 选项**已被 `mkRemovedOptionModule` 删除**（`ollama.nix:38-39`），现在**只能**通过换 `package` 实现 —— 写了 `acceleration` 会直接报错，提示你改用 `pkgs.ollama[,-vulkan,-rocm,-cuda,-cpu]`。

**让更多软件支持 ROCm/HIP**（如 Blender）：

```nix
# 全局开启（代价：部分包可能在本地重新编译，而非从缓存拉取）
nixpkgs.config.rocmSupport = true;

# 或只对单个包开（更省事）
environment.systemPackages = with pkgs; [
  (ffmpeg-full.override { config.rocmSupport = true; })
];
```

> 出处：`nixos/modules/services/hardware/amdgpu.nix`、`nixos/modules/services/misc/ollama.nix`、`pkgs/top-level/config.nix` `[核实·源码]`；[NixOS Wiki · AMD GPU §Enabling ROCm](https://wiki.nixos.org/wiki/AMD_GPU) `[Wiki]`

**部分软件硬编码 `/opt/rocm` 路径**，NixOS 上需要补一个符号链接：

```nix
systemd.tmpfiles.rules =
  let
    rocmEnv = pkgs.symlinkJoin {
      name = "rocm-combined";
      paths = with pkgs.rocmPackages; [ rocblas hipblas clr ];
    };
  in [ "L+ /opt/rocm - - - - ${rocmEnv}" ];
```

### 3.4 CPU：微码 + 电源管理

**微码更新（建议开）**：

```nix
hardware.cpu.amd.updateMicrocode = true;   # ⚠️ 默认是 false，建议显式开启
```

> [!NOTE]
> `hardware.cpu.amd.updateMicrocode` **默认 false**。AMD 的微码修复涉及安全漏洞（如 Zenbleed、Sinkclose 等），**建议开启**。CPU 微码更新是免费的稳定性与安全性提升。

> 出处：`nixos/modules/hardware/cpu/amd-microcode.nix` `[核实·源码]`

**`amd_pstate`：你不需要手动设**

> [!TIP]
> **老教程常说要加 `boot.kernelParams = [ "amd_pstate=active" ]` —— 在 26.05 上是冗余的。**
>
> 内核 Kconfig 的 `X86_AMD_PSTATE_DEFAULT_MODE` **默认值就是 3 = Active (EPP)**。Zen 3 及更新（且支持 CPPC）的 CPU **默认已经是 active 模式**，无需任何内核参数。
>
> 只有在你**确实想改成 passive/guided** 时才需要写 `amd_pstate=`。

> 出处：内核 `drivers/cpufreq/Kconfig.x86`；[kernel.org · amd-pstate](https://docs.kernel.org/admin-guide/pm/amd-pstate.html) `[官方]`

**电源管理：不要装 TLP**

```nix
# ✅ 什么都不用写 —— GNOME 和 KDE Plasma 6 都会自动开启 power-profiles-daemon
#    （源码里用 mkDefault true 自动设）

# ❌ 不要装 tlp —— 它与 power-profiles-daemon 互斥，同时开会触发断言、构建失败
# services.tlp.enable = true;

# ❌ 不要开 thermald —— 那是 Intel 专用的散热守护，AMD 上无意义
# services.thermald.enable = true;
```

> 出处：`nixos/modules/services/desktop-managers/gnome.nix:332`、`nixos/modules/services/desktop-managers/plasma6.nix:272`（均 `mkDefault true`）、`tlp.nix`（互斥断言）`[核实·源码]`
>
> ⚠️ 这两个模块在 26.05 的路径是 `services/desktop-managers/`（**不是** `services/x11/desktop-managers/`）。旧教程里的 `x11/` 前缀已失效（见附录 B.3）。

> [!DANGER]
> **`services.thermald` 是 Intel 专用。** 网上很多「NixOS 性能优化」清单会无差别地列上它，在 AMD 机器上开了**没有任何作用**，纯属噪音配置。

**调度器（可选）**：

```nix
services.scx = {
  enable = true;
  scheduler = "scx_rustland";   # 默认值
  # package = pkgs.scx.full;    # 默认
};
```

`services.scx` 与 `programs.gamemode` **不冲突** —— 前者是调度器 daemon，后者用 `uaccess` + `cap_sys_nice`，两者可共存。

> [!NOTE]
> **「scx 对 AMD 游戏是否值得开」缺一手基准数据。** 模块与选项已核实存在，但收益属主观判断。**建议先用默认调度器，遇到具体卡顿再试。** `[未核实]`

### 3.5 内核：26.05 默认的 6.18 已经够用

**NixOS 26.05 的默认内核是 6.18**（从 26.05 之前的 6.12 升级而来）。

> [!TIP]
> **RDNA 2 / 3 / 4 的用户不需要 `boot.kernelPackages = pkgs.linuxPackages_latest`。**
>
> 6.18 对主流 AMD 显卡的支持已经完整。**只有当你的显卡是「发布不足半年」的新型号**（内核里还没有对应支持）时，才需要换 `linuxPackages_latest`。

> 出处：`nixos/doc/manual/release-notes/rl-2605.section.md`（6.12 → 6.18）`[官方]`；`nixos/modules/system/boot/kernel.nix`（默认 `pkgs.linuxPackages`）`[核实·源码]`

**AMD 相关的内核参数**（nixpkgs 只暴露了两个，其余需手写）：

```nix
# 由硬件模块自动处理（推荐用选项，别手写）
hardware.amdgpu.overdrive.enable = true;      # → amdgpu.ppfeaturemask=0xfffd7fff
hardware.amdgpu.legacySupport.enable = true;  # → amdgpu.si_support=1 radeon.si_support=0 等

# 需要手写的内核参数（nixpkgs 无对应模块）
boot.kernelParams = [
  # "amdgpu.dcdebugmask=0x10"   # 排查显示问题时用，取值需按具体情况定 [未核实]
  # "amdgpu.gpu_recovery=1"     # GPU 挂起后自动恢复，效果/取值未从一手来源确认 [未核实]
];
```

### 3.6 AMD 显卡控制工具：LACT 与 CoreCtrl

**LACT（Linux AMDGPU Controller）—— 推荐**

```nix
services.lact.enable = true;   # ✅ 是 services.lact，不是 programs.lact
```

LACT 可以超频、降压、调风扇曲线。

> [!IMPORTANT]
> **要超频，还得同时开 `hardware.amdgpu.overdrive.enable = true;`** —— LACT 模块的注释里明确建议 AMD 用户一并开启。不开的话 ppfeaturemask 不允许超频。

**`services.lact` 的全部选项（源码级，共 3 个）**：

| 选项 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `enable` | bool | `false` | 开关；同时装 `environment.systemPackages` + `systemd.packages`，并拉起 `lactd` 服务（`wantedBy = multi-user.target`） |
| `package` | package | `pkgs.lact` | 可覆盖 |
| `settings` | **freeform YAML**（`submodule` + `freeformType`） | `{ }` | 声明式写 LACT 配置 |

> [!WARNING]
> **`settings` 非空时，`/etc/lact/config.yaml` 会变成 Nix store 的符号链接，LACT 的 GUI 将无法再改配置**（模块注释原文：*"the LACT daemon will not be able to modify it through the GUI"*）。
> **实务建议**：先不开 `settings`，用 GUI 调出满意的超频/风扇曲线，再 `cat /etc/lact/config.yaml` 把结果抄回 `settings` 固化。`settings` 变更会触发 `lactd` 重启（`restartTriggers`）。

> 出处：`nixos/modules/services/hardware/lact.nix`（全文 87 行）`[核实·源码]`；[NixOS Wiki · AMD GPU §LACT](https://wiki.nixos.org/wiki/AMD_GPU) `[Wiki]`

**CoreCtrl**

```nix
programs.corectrl.enable = true;   # 会自动创建 corectrl 组 + polkit 规则
```

**`programs.corectrl` 的全部选项（源码级，共 2 个）**：`enable`、`package`。开 `enable` 会做三件事：装包 + 建 `users.groups.corectrl` 组 + 写一条 polkit 规则（允许 `corectrl` 组成员免密执行 `org.corectrl.helper.init`）。**你还需要手动 `sudo usermod -aG corectrl $USER`**（或声明式 `users.users.<name>.extraGroups = [ "corectrl" ]`），否则每次启动都要输密码。

> [!WARNING]
> **CoreCtrl 的旧选项名已迁移。** `programs.corectrl.gpuOverclock.enable` / `.ppfeaturemask` **已重命名为 `hardware.amdgpu.overdrive.*`**。老教程里的写法会报错或无效。

> 出处：`nixos/modules/hardware/corectrl.nix:18-56`（含两条 `mkRenamedOptionModule`）`[核实·源码]`

**两者怎么选**：LACT 更专注 AMD、更新更快；CoreCtrl 支持 AMD + Intel 混合场景。**纯 AMD 单卡用 LACT。**

### 3.7 故障排查

| 症状 | 原因 | 解法 |
|---|---|---|
| **开机初期低分辨率**，之后正常 | initramfs 阶段没加载 amdgpu | `hardware.amdgpu.initrd.enable = true;` |
| **多显示器**排列/分辨率异常 | 连接器自动探测出错 | 手写 `boot.kernelParams = [ "video=DP-1:2560x1440@144" ]`；用 `head /sys/class/drm/*/status` 查连接器名 |
| **X11 下画面撕裂** | modesetting 不支持 TearFree | 需同时把 `services.xserver.videoDrivers = [ "amdgpu" ]`（换旧 DDX）+ `services.xserver.deviceSection` 加 `Option "TearFree" "true"`。**Wayland 不需要** |
| 报 `amdgpu: Failed to get gpu_info firmware` | 缺固件 | `hardware.firmware = [ pkgs.linux-firmware ];` |
| **偶发崩溃**，`dmesg` 有 `page fault` / `GCVM_L2_PROTECTION_FAULT_STATUS` | GPU 自动超频过高、电压不足 | 用 LACT **提高功耗上限 + 降压**（如 7900 XTX 降 -50mV）+ 可选降低最高频率 |
| **Vega 核显 / RX 6600 系统挂起** | 图形与计算上下文切换的已知问题 | 有社区补丁（`amdgpu-stable` / `amdgpu-testing`），需自行打补丁 `[社区]` |
| 某些游戏**帧数腰斩** | 游戏选了 AMDVLK 而非 RADV | `environment.variables.AMD_VULKAN_ICD = "RADV";` 强制走 RADV |

> 出处：[NixOS Wiki · AMD GPU §Troubleshooting](https://wiki.nixos.org/wiki/AMD_GPU) `[Wiki]`；Vulkan 默认走 Mesa RADV（`[Wiki]`）

> [!NOTE]
> **关于 AMDVLK**：官方 Wiki 已标注它**正在停止维护**，只有「RADV 出问题时」才考虑用它。**默认不用装。** 64 位 Vulkan 默认已由 Mesa RADV 提供，无需任何配置。

### 3.8 坑与反直觉（本章汇总）

| 坑 | 事实 |
|---|---|
| `hardware.graphics.enable` 默认值 | **`false`**，且 GNOME/KDE **都不自动开**（源码命中数 0）—— 必须手写。全仓库只有 steam / amdgpu.opencl / amdgpu.zluda 会开 |
| `videoDrivers = [ "amdgpu" ]` | **现代 AMD 不要写**。默认 `modesetting` 才是推荐；写了会换旧 DDX |
| `amd_pstate=active` | **冗余**。26.05 内核默认就是 active 模式 |
| `services.thermald` | **Intel 专用**，AMD 上开了没用 |
| TLP 与 ppd | **互斥**，同开触发断言。桌面已自动开 ppd，别再装 TLP |
| `hardware.cpu.amd.updateMicrocode` | 默认 **false**，建议手动开 |
| VA-API | AMD **不需要额外包**，Mesa 自带 radeonsi |
| `services.ollama.package` | 默认是 **CPU 版**，必须改成 `pkgs.ollama-rocm` |
| LACT 的选项前缀 | 是 **`services.lact`**，不是 `programs.lact` |
| CoreCtrl 超频选项 | 已迁移到 **`hardware.amdgpu.overdrive.*`** |
| `hardware.amdgpu` 里没有 | `dcdebugmask` / `gpu_recovery` —— 需手写 `boot.kernelParams` |
| 内核版本 | 26.05 默认 **6.18**，RDNA2/3/4 无需 `linuxPackages_latest` |

---

## 四、网络（Realtek 螃蟹卡）

### 4.1 驱动选择：先别急着换

> [!TIP]
> **绝大多数 Realtek 有线网卡用内核自带的 `r8169` 就够了。**
>
> 内核的 `r8169` 驱动现在**已经覆盖**：RTL8111 / RTL8168 / RTL8411（千兆）、RTL8125（2.5G）、RTL8126（5G）。
>
> **先确认现状，再决定要不要换。**

```bash
# 看你的网卡型号和当前驱动
lspci -k | grep -A 3 -i ethernet
# 期望看到：Kernel driver in use: r8169

# 看驱动是否已加载
lsmod | grep r8169

# 看是否有报错
dmesg | grep -i -E "r8169|eth"
```

**什么时候才需要换驱动？**

| 症状 | 可能原因 | 解法 |
|---|---|---|
| 随机断连 / 掉线 | RTL8125 的 ASPM 省电问题 | 换 `r8125` 驱动，或关 ASPM（见 §4.2） |
| 速率上不去（只有百兆） | 驱动协商问题 / 网线 | 先换网线，再考虑换驱动 |
| 网卡完全不识别 | 内核太旧（RTL8126 需 6.6+） | 26.05 默认 6.18，应该已支持 |
| 高负载下丢包 | 驱动 bug | 换厂商驱动 |

**换驱动的准确写法**：

```nix
{ config, pkgs, ... }: {
  # RTL8125（2.5G）→ 用 r8125
  boot.extraModulePackages = [ config.boot.kernelPackages.r8125 ];
  boot.blacklistedKernelModules = [ "r8169" ];   # 屏蔽自带驱动

  # RTL8111/8168/8411（千兆）→ 用 r8168
  # boot.extraModulePackages = [ config.boot.kernelPackages.r8168 ];
  # boot.blacklistedKernelModules = [ "r8169" ];
}
```

> [!DANGER]
> **`r8168` 和 `r8125` 是【树外内核模块】，必须和你的内核版本匹配。**
>
> `config.boot.kernelPackages.r8168` 这种写法会自动用**当前内核**去编译，所以内核升级时会自动重编。**但重编需要本地编译工具链，且可能失败** —— 编译失败 = 网卡不可用 = 你可能连不上网去修。
>
> **所以：能用 `r8169` 就别换。** 只有确实遇到问题时才换，并且**换之前先确保有其它联网方式**（手机 USB 共享网络）。

> 出处：nixpkgs `pkgs/os-specific/linux/r8168/default.nix`、`pkgs/os-specific/linux/r8125/default.nix`（均已确认存在于 26.05）`[核实·源码]`

### 4.2 网卡固件与 ASPM

**固件**（Realtek 网卡需要）：

```nix
hardware.enableRedistributableFirmware = true;   # 提供 rtl_nic/*.fw 固件
```

> [!IMPORTANT]
> **Realtek 有线网卡需要 `rtl_nic/*.fw` 固件文件**，这些在 `hardware.enableRedistributableFirmware` 里。**不开的话，某些型号（尤其 RTL8125/8126）可能无法正常工作。**
>
> 这条对**有线**网卡也适用 —— 很多人以为它只跟无线有关。

> 出处：nixpkgs `nixos/modules/hardware/all-firmware.nix`（`hardware.enableRedistributableFirmware` 包含 `linux-firmware`）`[核实·源码]`

**关于 ASPM（省电导致的掉线）**：

> [!DANGER]
> **`r8169.aspm=0` 这个内核参数【不存在】。**
>
> 网上大量教程写 `boot.kernelParams = [ "r8169.aspm=0" ]` —— 这是**错的**。2025-03 有一个提交该参数的提案，**被内核维护者拒绝了**（因为 ASPM 状态应该由 `pcie_aspm` 子系统控制，驱动无权覆盖）。
>
> **正确的做法**：
> - **全局关 ASPM**：`boot.kernelParams = [ "pcie_aspm=off" ]` —— 有效，但会影响**所有** PCIe 设备（包括你的 AMD 显卡和 NVMe），增加功耗
> - **只对网卡关**：用 `setpci` 或 `lspci -vv` 查 ASPM 状态后手动写寄存器，**不是持久化方案**
> - **最省事**：直接换 `r8125` 厂商驱动（它自己处理 ASPM）
>
> 出处：Linux 内核邮件列表 2025-03 的提案被拒记录 `[社区]`

### 4.3 NetworkManager

```nix
networking.networkmanager.enable = true;

# 有线连接走 DHCP（最常见）
networking.interfaces.enp4s0.useDHCP = true;   # ⚠️ 把 enp4s0 换成你的实际网卡名

# 或者让 NetworkManager 全权管理，不在这里写
# networking.networkmanager.unmanaged = [ ];
```

> [!TIP]
> **`enp4s0` 不是固定值 —— 用 `ip link` 查你的实际网卡名。**
>
> 现代 Linux 用「可预测网卡名」（predictable interface names），格式通常是 `enp<bus>s<slot>`（有线）或 `wlp<bus>s<slot>`（无线）。**不要照抄教程里的 `eth0`** —— 那通常是老系统或虚拟机。
>
> **建议**：**不写 `networking.interfaces.*`**，直接让 NetworkManager 接管。它是图形化的，改配置不用 rebuild。

**查看连接状态**：

```bash
nmcli device status
nmcli connection show
ip addr show
```

### 4.4 防火墙

```nix
# 默认状态：networking.firewall.enable = true
# 默认行为：拒绝所有入站，允许所有出站
```

> [!NOTE]
> **NixOS 防火墙默认是开着的**（`networking.firewall.enable` 默认 `true`），且默认**不放行任何入站端口**。
>
> **这意味着**：你在机器上跑的服务（开发服务器、Ollama 等）**默认不能被局域网内其它设备访问**，但本机 `localhost` 访问正常。如果你想让手机/别的电脑访问你的开发服务，需要显式放行：
>
> ```nix
> networking.firewall.allowedTCPPorts = [ 3000 8080 ];
> ```

> [!TIP]
> **注意区分「本机访问」和「局域网访问」。** 很多人在 NixOS 上跑 `ollama serve` 后发现手机连不上，以为是服务坏了 —— 其实是防火墙。**这是设计如此，不是 bug。**

### 4.5 Wake-on-LAN（可选）

```nix
networking.interfaces.enp4s0.wakeOnLan.enable = true;
```

> [!WARNING]
> **Realtek 网卡的 WoL 有个常见坑：Windows 关机后 WoL 失效。**
>
> 原因是 Windows 的驱动在关机时把网卡置于「省电模式」，只监听魔法包但关闭了常规接收。**从 Linux 关机则正常。** 双系统用户需要注意。
>
> **排查**：`ethtool <网卡名>` 看 `Wake-on` 字段是否为 `g`（magic packet）。

### 4.6 国内 Nix 镜像源（显著提速）

这是**中文用户最值得配的一项** —— 不配的话从 `cache.nixos.org` 拉包在国内可能只有几十 KB/s。

```nix
{ ... }: {
  nix.settings.substituters = [
    "https://mirrors.ustc.edu.cn/nix-channels/store"        # 中科大
    "https://mirrors.tuna.tsinghua.edu.cn/nix-channels/store" # 清华
    "https://cache.nixos.org"                                # 官方（保留作回退）
  ];

  # ⚠️ 不需要改 trusted-public-keys！
  # 这两个镜像都使用官方的签名密钥，NixOS 默认配置已经包含。
  # 网上让你额外加 key 的教程是多余的。
}
```

> [!IMPORTANT]
> **镜像源用的是官方签名，所以 `trusted-public-keys` 不用动。**
>
> 这是很多人搞错的地方 —— 他们以为换镜像要换 key。**不需要。** 镜像只是「换个地方下载同样的文件」，签名还是 NixOS 官方的。**Nix 的信任模型基于签名而非来源**，所以镜像无法投毒。

> [!WARNING]
> **`nix.binaryCaches` 这个选项只存在于 NixOS 21.11 及更早。** 网上老教程里的 `nix.binaryCaches = [...]` 在 26.05 上**会导致构建失败**。正确选项是 **`nix.settings.substituters`**。

**验证镜像是否生效**：

```bash
# 看实际使用的 substituter
nix show-config | grep -A5 substituters

# 测试下载速度（拉一个没装过的包）
nix shell nixpkgs#hello
```

> [!NOTE]
> **`nix.settings.trusted-users` 默认是 `["root"]`，不用改。** 只有当你希望普通用户也能添加 substituter 时才需要加。`[核实·源码]`

> 出处：[USTC 镜像帮助 · nix](https://mirrors.ustc.edu.cn/help/nix-channels.html) `[官方]`；[TUNA 镜像帮助 · nix-channels](https://mirrors.tuna.tsinghua.edu.cn/help/nix-channels/) `[官方]`

### 4.7 坑与反直觉（本章汇总）

| 坑 | 事实 |
|---|---|
| `r8169.aspm=0` | **参数不存在**，2025-03 的提案被内核拒绝 |
| 换 `r8168`/`r8125` 的代价 | 树外模块，**内核升级时要重编**，编译失败 = 没网 |
| `hardware.enableRedistributableFirmware` | **有线网卡也需要**（`rtl_nic/*.fw`） |
| `eth0` | 现代系统用 `enp4s0` 这类可预测名，**别照抄** |
| 服务局域网连不上 | **防火墙默认开且不放行入站**，是设计如此 |
| `nix.binaryCaches` | 仅 ≤21.11 存在，26.05 用会**构建失败** |
| 换镜像要改 key？ | **不用**。镜像用官方签名 |
| `trusted-public-keys` | 默认已含官方 key，**不用动** |

---

## 五、中文环境

### 5.1 locale 与时区

```nix
{ ... }: {
  i18n.defaultLocale = "zh_CN.UTF-8";
  time.timeZone = "Asia/Shanghai";

  # 可选：让日期/时间格式跟随中文，但保持其它为英文
  i18n.extraLocaleSettings = {
    LC_TIME = "zh_CN.UTF-8";
    LC_MONETARY = "zh_CN.UTF-8";
  };
}
```

> [!NOTE]
> **`i18n.supportedLocales` 不再需要手动设。**
>
> 旧教程会写 `i18n.supportedLocales = [ "all" ]`。在 26.05 上该选项已**隐藏并弃用**（仅保留以兼容旧配置），替代品是 `i18n.extraLocales`。**你不需要设任何一项** —— `i18n.defaultLocale` 会自动包含所需 locale。

> 出处：nixpkgs `nixos/modules/config/i18n.nix` `[核实·源码]`

> [!TIP]
> **`LC_TIME` 建议保留英文。** 中文的日期格式（`2026年10月12日`）在很多命令行工具和日志里会显得突兀。个人偏好，看你习惯。

### 5.2 字体

```nix
{ pkgs, ... }: {
  # NixOS 默认已经装了 Noto 全家桶（含 CJK 和 emoji）
  fonts.enableDefaultPackages = true;   # 默认值就是 true

  # 补充你想要的
  fonts.packages = with pkgs; [
    noto-fonts                # Noto 基础
    noto-fonts-cjk-sans       # ✅ 中文字体（黑体，无衬线）
    noto-fonts-cjk-serif      # ✅ 中文字体（宋体，衬线）
    noto-fonts-color-emoji    # ⚠️ 注意包名，不是 noto-fonts-emoji
    wqy-zenhei                # 文泉驿正黑（备选，覆盖更全）
    # source-han-sans         # 思源黑体（如果上面找不到）
  ];

  # 字体优先级：拉丁字体在前，中文在后
  fonts.fontconfig.defaultFonts = {
    sansSerif = [ "Noto Sans" "Noto Sans CJK SC" "WenQuanYi Zen Hei" ];
    serif     = [ "Noto Serif" "Noto Serif CJK SC" ];
    monospace = [ "JetBrains Mono" "Noto Sans Mono CJK SC" ];
    emoji     = [ "Noto Color Emoji" ];
  };
}
```

> [!DANGER]
> **emoji 字体的包名是 `noto-fonts-color-emoji`，不是 `noto-fonts-emoji`。**
>
> `noto-fonts-emoji` 这个包**在 nixpkgs 里不存在**（已核实）。写了会导致构建失败。老教程里的这个名字是错的。

> [!IMPORTANT]
> **字体优先级（`defaultFonts`）的排序逻辑：拉丁字体放前面，中文字体放后面。**
>
> 为什么？因为 fontconfig 按顺序匹配 —— **拉丁字体（如 Noto Sans）通常不含中文字形**，遇到中文时会自动 fallback 到下一个字体（Noto Sans CJK SC）。
>
> **如果反过来**（中文放前面），英文也会用中文字体的拉丁字形渲染 —— 那通常比较难看（中文字体的英文字距偏宽）。
>
> **`Noto Sans CJK SC` 里的 `SC`** 指 Simplified Chinese。不写 SC 也能匹配，但显式写更准确。

> 出处：nixpkgs `nixos/modules/config/fonts/fontconfig.nix`（`fonts.packages`、`fonts.fontconfig.defaultFonts.{sansSerif,serif,monospace,emoji}`）`[核实·源码]`

> [!NOTE]
> **`fonts.fonts` 已重命名为 `fonts.packages`。** 旧教程里的 `fonts.fonts = [...]` 仍可用（是别名），但推荐新名字。

**验证字体是否生效**：

```bash
# 看 fontconfig 能否找到中文字体
fc-list :lang=zh | head -20

# 看某个字符实际会用哪个字体渲染
fc-match "sans-serif:lang=zh"
```

### 5.3 输入法 fcitx5（本节是重点）

**基础配置**：

```nix
{ pkgs, ... }: {
  i18n.inputMethod = {
    enable = true;          # ✅ 26.05 的推荐写法
    type = "fcitx5";
    # ⚠️ i18n.inputMethod.enabled = "fcitx5";  ← 已弃用，见下方警告

    fcitx5 = {
      addons = with pkgs; [
        fcitx5-chinese-addons   # ✅ 中文拼音、五笔等
        fcitx5-rime             # ✅ 中州韵（雾凇拼音等方案）
        fcitx5-configtool       # 图形配置工具
        fcitx5-gtk              # GTK 应用支持
        qt6Packages.fcitx5-qt   # Qt 应用支持
      ];

      # Wayland 下建议开启
      waylandFrontend = true;
    };
  };
}
```

> [!DANGER]
> **`i18n.inputMethod.enabled` 已被弃用。**
>
> 源码里的描述原文：*"Deprecated - use `type` and `enable = true` instead"*，并且会产生构建警告：
> *"i18n.inputMethod.enabled will be removed in a future release. Please use .type, and .enable = true instead"*
>
> **老写法仍然能用**（内部做了兼容，`enabled` 的值会自动赋给 `type`），但**将来会移除**。新配置请用 `enable = true` + `type = "fcitx5"`。

> [!DANGER]
> **绝对不要用 `environment.systemPackages = [ pkgs.fcitx5 ];` 装 fcitx5。**
>
> 官方 Wiki 明确警告：这会**干扰 addon 检测**，导致输入法引擎「加载失败 / 使用不可」。
>
> **只通过 `i18n.inputMethod.fcitx5.addons` 添加。** 这是最常见的 fcitx5 故障原因。

> 出处：nixpkgs `nixos/modules/i18n/input-method/default.nix`、`fcitx5.nix` `[核实·源码]`；[NixOS Wiki · Fcitx5](https://wiki.nixos.org/wiki/Fcitx5) `[Wiki]`

### 5.4 Wayland 下的环境变量：**不要乱设**

这是**最容易配错**的地方。很多教程教你设 `GTK_IM_MODULE` / `QT_IM_MODULE` / `XMODIFIERS`，**在 Wayland 下这样做反而会出问题**。

| 变量 | Wayland 下该不该设 | 说明 |
|---|---|---|
| `XMODIFIERS` | **模块自动设** | NixOS 的 input-method 模块会设，你不用管 |
| `GTK_IM_MODULE` | ❌ **不要设** | Wayland 下 GTK 走原生 text-input 协议。设了会导致候选窗定位错误甚至崩溃 |
| `QT_IM_MODULE` | ⚠️ **视情况** | 见下方 |

> [!IMPORTANT]
> **`waylandFrontend = true` 的作用就是「不设 `GTK_IM_MODULE` / `QT_IM_MODULE`」。**
>
> 源码逻辑：当 `waylandFrontend = true` 时，模块**只设 `XMODIFIERS`**，让应用走 Wayland 原生输入协议；当它为 `false` 时，才设 `GTK_IM_MODULE` / `QT_IM_MODULE`。
>
> **所以设了 `waylandFrontend = true` 就不要再去手动设那两个变量** —— 那是自相矛盾，会覆盖掉模块的正确行为。

> [!WARNING]
> **`--enable-wayland-ime` 是 Chromium / Electron 的启动参数，不是 fcitx5 的参数。**
>
> 网上有教程写 `fcitx5 --enable-wayland-ime` —— **这是错的**，fcitx5 没有这个参数。正确的用法是给 Chromium / Electron 应用加这个 flag（但通常 `NIXOS_OZONE_WL = "1"` 就够了）。

> 出处：nixpkgs `nixos/modules/i18n/input-method/fcitx5.nix`（`waylandFrontend` 的环境变量逻辑）`[核实·源码]`

### 5.5 GNOME 与 KDE 下的输入法差异

这是**选桌面环境时值得考虑的一点**。

| | GNOME 50 | KDE Plasma 6.6 |
|---|---|---|
| fcitx5 可用性 | ✅ 可用 | ✅ 可用 |
| **候选窗定位** | ⚠️ 偶发偏移 | ✅ 正常 |
| 需要的额外步骤 | 装 **Kimpanel** 扩展 | 无需额外步骤 |
| 推荐的环境变量 | **不设 `GTK_IM_MODULE`** | **不设 `GTK_IM_MODULE` / `QT_IM_MODULE`** |
| Qt 应用 | 需 `QT_IM_MODULE=fcitx` | 从 KWin「虚拟键盘」启动即可 |

> [!TIP]
> **GNOME 下如果候选窗位置不对，装 Kimpanel 扩展。**
>
> ```nix
> environment.systemPackages = [ pkgs.gnomeExtensions.kimpanel ];
> programs.dconf.profiles.user.databases = [{
>   settings."org/gnome/shell".enabled-extensions = [
>     pkgs.gnomeExtensions.kimpanel.extensionUuid
>   ];
> }];
> ```
> Kimpanel 让输入法的候选窗由 GNOME Shell 自己绘制，位置永远正确。

> [!NOTE]
> **KDE 下**：不要设 `GTK_IM_MODULE` / `QT_IM_MODULE`。Qt 应用通过 KWin 的「虚拟键盘」机制（Virtual Keyboard）与输入法通信，这是 Plasma 6 的原生方式。

### 5.6 首次配置输入法（运行时步骤）

**NixOS 只负责「装好」，具体用哪个输入方案要运行一次图形配置工具**：

```bash
# 启动图形配置工具
fcitx5-configtool
```

在里面：

1. 左侧「输入法」标签 → 点「+」添加
2. 取消勾选「只显示当前语言」
3. 找到 **Pinyin**（拼音）或 **Rime**（中州韵），添加
4. 设置切换热键（默认 `Ctrl+Space`）

> [!TIP]
> **想用雾凇拼音等 Rime 方案？** 装 `fcitx5-rime` 后，把方案文件放到 `~/.local/share/fcitx5/rime/`，然后在 fcitx5 菜单里选「重新部署」。

> [!NOTE]
> **这些设置存在 `~/.config/fcitx5/`，是运行时状态，不在 NixOS 配置里。** 如果你想让输入法配置也「声明式」，可以用 `i18n.inputMethod.fcitx5.settings`，但**更简单的方式是用 GUI 配好，然后把它当作运行时状态**（换机器时重新配一次，成本很低）。

### 5.7 坑与反直觉（本章汇总）

| 坑 | 事实 |
|---|---|
| `i18n.inputMethod.enabled` | **已弃用**，改用 `enable = true` + `type = "fcitx5"` |
| `environment.systemPackages` 装 fcitx5 | **会破坏 addon 检测**，只能用 `i18n.inputMethod.fcitx5.addons` |
| `noto-fonts-emoji` | **包不存在**，正确名是 `noto-fonts-color-emoji` |
| `GTK_IM_MODULE` | Wayland 下**不要设**（`waylandFrontend = true` 就是为了不设它） |
| `QT_IM_MODULE` | KDE 下**不要设** |
| `fcitx5 --enable-wayland-ime` | **参数不存在**，那是 Chromium 的 flag |
| `i18n.supportedLocales` | 已隐藏/弃用，**不用设** |
| `fonts.fonts` | 已重命名为 **`fonts.packages`** |
| 字体优先级 | **拉丁字体在前、中文在后**，顺序反了英文会变难看 |
| `nix.binaryCaches` | 仅 ≤21.11，26.05 用会失败 |

---

## 六、桌面环境：GNOME vs KDE

**26.05 的版本事实**：GNOME **50「Tokyo」**、KDE Plasma **6.6**、Linux **6.18 LTS**。

> 出处：[NixOS 26.05 发布公告](https://nixos.org/blog/announcements/2026/nixos-2605/) `[官方]`

### 6.1 选型：一张表说清

| 维度 | GNOME 50 | Plasma 6.6 |
|---|---|---|
| **Wayland 成熟度** | 高；**GDM 已强制 Wayland**（X11 开关被删除） | 高；SDDM 默认 Wayland + kwin |
| **中文输入法** | fcitx5 可用，但 Wayland 下候选窗定位**偶发偏移** | ✅ **更佳**，原生 kimpanel 集成 |
| **游戏（VRR / HDR）** | 可用；HDR 生态弱 | ✅ **更佳**，KWin 支持 VRR / HDR，配 gamescope |
| **定制性** | 低（要靠扩展 + dconf） | ✅ 极高（系统设置全覆盖） |
| **资源占用** | 中 | 略高（可关特效） |
| **上手难度** | 简单 | 中等，选项多 |
| **Qt 应用主题** | ⚠️ 26.05 有已知问题（见 §6.5） | 原生 |

> [!TIP]
> **对你的配置（AMD + 中文输入法 + Steam 游戏），KDE Plasma 6 是更顺的选择。** 主要理由有两条：**① fcitx5 在 KDE 下的 Wayland 集成明显更好**（原生 kimpanel，候选窗不会跑偏）；**② KWin 的 VRR / HDR 支持更完整**，玩游戏体验更接近 Windows。
>
> **但 GNOME 更省心** —— 如果你不想折腾设置项，GNOME 的默认体验足够好。**两者都是正确选择**，取决于你更在意「省心」还是「可控」。

> [!WARNING]
> **26.05 起，GNOME 无法再切回 X11。** `services.displayManager.gdm.wayland` 这个选项**已被删除** —— 源码里的说明是 *"Disabling this option is no longer supported with GNOME 50"*，即 GDM **恒为 Wayland**。
>
> 写这个选项会**直接构建失败**。老教程里「GNOME 出问题就切 X11」的建议在 26.05 上已经失效。

### 6.2 GNOME 配置

```nix
{ pkgs, ... }: {
  # ── 启用 ──
  services.desktopManager.gnome.enable = true;   # 规范写法
  services.displayManager.gdm.enable = true;
  # ⚠️ services.xserver.desktopManager.gnome.enable 是别名，仍可用，但推荐上面的写法
  # ⛔ services.displayManager.gdm.wayland —— 已在 26.05 删除，写了会构建失败

  # ── 精简臃肿软件 ──
  services.gnome.core-apps.enable = false;              # 默认 true，可关
  services.gnome.core-developer-tools.enable = false;
  services.gnome.games.enable = false;                  # 关掉 GNOME 小游戏
  environment.gnome.excludePackages = with pkgs; [
    gnome-tour          # 首次启动的导览
    gnome-user-docs     # 用户手册（占空间大）
    totem               # 视频播放器
    cheese              # 摄像头
    epiphany            # GNOME 浏览器（你已经有 Firefox）
  ];

  # ── Electron 应用走 Wayland（仍需要手动设）──
  environment.sessionVariables.NIXOS_OZONE_WL = "1";
}
```

> [!NOTE]
> **`NIXOS_OZONE_WL = "1"` 官方明确默认不启用**（因为 Ozone-Wayland 尚未定型）。VS Code、Discord、Obsidian 这类 Electron 应用如果不设它，在 Wayland 下会出现模糊、缩放异常、输入法失效等问题。**建议设上。**
>
> 出处：nixpkgs PR #291051 `[仓库]`

**装 GNOME 扩展（需要两步）**：

```nix
{ pkgs, ... }: {
  # 第 1 步：装扩展包
  environment.systemPackages = with pkgs.gnomeExtensions; [
    appindicator        # 托盘图标支持（很多国产应用需要）
    dash-to-dock        # 类似 Windows 的任务栏
  ];

  # 第 2 步：用 dconf 启用它（Nix 装的扩展默认不激活！）
  programs.dconf.profiles.user.databases = [{
    settings."org/gnome/shell".enabled-extensions = [
      pkgs.gnomeExtensions.appindicator.extensionUuid
      pkgs.gnomeExtensions.dash-to-dock.extensionUuid
    ];
  }];
}
```

> [!IMPORTANT]
> **`programs.gnome-extensions` 这个选项不存在。** 网上有教程这么写，是错的。正确做法是「装包 + dconf 启用」两步。
>
> **`extensionUuid` 是关键** —— 不能用包名。dconf 里要的是扩展的 UUID（如 `appindicatorsupport@rgcjonas.gmail.com`），`pkgs.gnomeExtensions.<x>.extensionUuid` 会取到它。

**GNOME 分数缩放（无 NixOS 选项）**：

```bash
# 只能在运行时用 gsettings 开
gsettings set org.gnome.mutter experimental-features "['scale-monitor-framebuffer']"
```

> [!NOTE]
> **GNOME 的分数缩放没有 NixOS 声明式选项**，只能 gsettings。这意味着它**不在你的配置版本控制里**，换机要重设。`[社区]`

### 6.3 KDE Plasma 6 配置

```nix
{ pkgs, ... }: {
  # ── 启用 ──
  services.desktopManager.plasma6.enable = true;

  # ── 登录器：两种选择 ──
  # A) 什么都不写 → plasma6 模块会自动配置 SDDM，
  #    并把 wayland 默认打开（compositor = kwin）
  # B) 26.05 新增的 Plasma 专用登录器：
  # services.displayManager.plasma-login-manager.enable = true;

  # ── 精简 ──
  environment.plasma6.excludePackages = with pkgs.kdePackages; [
    konsole                      # 终端（你可能想保留）
    elisa                        # 音乐播放器
    plasma-browser-integration   # 浏览器集成
  ];

  # ── Qt 主题 ──
  qt = {
    enable = true;
    platformTheme = "kde";
    style = "breeze";
  };
}
```

> [!TIP]
> **Plasma 下默认已经是 Wayland 会话。** plasma6 模块把 `sddm.wayland.enable` 用 `mkDefault` 设成了 `true`（compositor = kwin），所以你不用手动配。
>
> **想强制 X11？** `services.displayManager.defaultSession = "plasmax11";`（但没必要，Plasma 6.6 的 Wayland 已经很稳）。

> [!WARNING]
> **关于 `plasma-login-manager` 的文档冲突**：26.05 的官方 Wiki 称它是「Plasma 默认登录器」，但 `plasma6.nix` 源码仍以 **SDDM** 为默认。
>
> **以源码为准：默认是 SDDM。** 这是个文档与源码不一致的案例，已记入附录 C。

### 6.4 Wayland 注意事项

**26.05 上，GNOME 和 KDE 都已经默认 Wayland。** 这是好事，但有几个必知项：

| 事项 | 说明 |
|---|---|
| **Electron 应用** | 必须设 `NIXOS_OZONE_WL = "1"`（GNOME/KDE 都需要） |
| **X11 应用兼容** | 由 XWayland 自动处理，一般无感 |
| **屏幕共享 / 录屏** | 需要 `xdg.portal`（Flatpak 那章会配，非 Flatpak 应用也需要） |
| **游戏** | `gamescope` 是 Wayland 合成器，在 Wayland 下体验更好 |
| **输入法** | 见第五章 —— Wayland 下 `GTK_IM_MODULE` / `QT_IM_MODULE` **不需要设** |
| **AMD 显卡** | Plasma 6.6 的 kwin_wayland 由模块打了 `cap_sys_nice`，**无系统性 AMD 问题** |

> 出处：`nixos/modules/services/desktop-managers/plasma6.nix:353-358`（`security.wrappers.kwin_wayland.capabilities = "cap_sys_nice+ep"`）`[核实·源码]`

### 6.5 坑与反直觉（本章汇总）

| 坑 | 事实 | 出处 |
|---|---|---|
| `gdm.wayland` | **已在 26.05 删除**，写了直接构建失败（GNOME 50 强制 Wayland） | `gdm.nix` `[仓库]` |
| `programs.gnome-extensions` | **不存在**。要用「装包 + dconf 启用 extensionUuid」 | `[Wiki]` |
| Nix 装的 GNOME 扩展不激活 | 必须用 dconf 显式列进 `enabled-extensions` | `[Wiki]` |
| GNOME 分数缩放 | **无 NixOS 选项**，只能 gsettings | `[社区]` |
| `qt.platformTheme = "gnome"` | ⚠️ **26.05 下深色模式是坏的**。改用 `qadwaitadecorations` / `qgnomeplatform` | `[Wiki]` |
| Plasma 里 Qt 应用段错误 | 陈旧 QML 缓存导致。删掉 `**/qmlcache` 即可 | `[Wiki]` |
| GNOME 精简软件 | 用 `services.gnome.core-apps.enable = false` + `environment.gnome.excludePackages` | `[仓库]` |
| `services.xserver.*` 前缀 | 都还是**别名**（`mkRenamedOptionModule`），可用但已非推荐写法 | `[仓库]` |

> [!TIP]
> **遇到「Qt 应用在 GNOME 下深色主题显示异常」** —— 这是 26.05 的已知问题，不是你配错了。用 `qadwaitadecorations` 或 `qgnomeplatform` 绕过。

---

## 七、Flatpak

### 7.1 先想清楚：NixOS 上到底该不该用 Flatpak

这是一个**有争议的选择**，先说清利弊：

| | 用 Nix 包 | 用 Flatpak |
|---|---|---|
| 与系统一致性 | ✅ 完全一致，可回滚 | ⚠️ 独立沙箱，独立更新 |
| 版本新鲜度 | 跟随 nixpkgs | ✅ 上游直接发布，通常更新 |
| 装软件的命令 | 改配置 + rebuild | ✅ `flatpak install` 一条命令 |
| 主题 / 字体统一 | ✅ 天然统一 | ⚠️ **沙箱内外不一致，需额外处理** |
| 中文输入法 | ✅ 正常 | ⚠️ **部分应用在沙箱里输入法失效** |
| 磁盘占用 | 共享依赖 | ⚠️ 各自带运行时（每个约 300 MB+） |
| 官方推荐度 | ✅ NixOS 官方推荐 | ⚠️ 官方手册把它当「补充手段」 |

> [!IMPORTANT]
> **务实建议：优先用 Nix 包，Flatpak 只作补充。**
>
> **什么时候值得用 Flatpak**：① 某个软件 nixpkgs 里版本太旧或根本没有；② 你想尝鲜某个应用的最新版，不想等 nixpkgs 更新；③ 应用作者只发 Flatpak（如某些专有软件）。
>
> **什么时候别用**：① 输入法重度使用的中文应用（沙箱内输入法可能失效）；② 需要和系统深度交互的工具。

### 7.2 配置（注意两个硬断言）

```nix
{ pkgs, ... }: {
  services.flatpak.enable = true;

  # ⚠️ 必须同时开 portal，否则 rebuild 直接失败（模块内有硬断言）
  xdg.portal.enable = true;

  # GNOME / KDE 模块会自动填 extraPortals，你不用手写
  # 只有用其它桌面（如 Hyprland、Sway）时才需要：
  # xdg.portal.extraPortals = [ pkgs.xdg-desktop-portal-gtk ];

  # 指定默认的「文件选择器 / 屏幕共享」后端
  xdg.portal.config.common.default = [ "gtk" ];
}
```

> [!DANGER]
> **`services.flatpak.enable = true` 有一个硬断言：`xdg.portal.enable` 必须为 `true`。**
> 只写前者不写后者，`nixos-rebuild` 会**直接失败**并报断言错误。这是新手最常撞的墙。

> [!DANGER]
> **`services.flatpak.remotes`、`services.flatpak.update.onActivation`、`services.flatpak.uninstallUnusedFor` 在 nixpkgs 26.05 里【不存在】。**
>
> 26.05 的 nixpkgs flatpak 模块**只有两个选项**：`enable` 和 `package`。
>
> 上面那三个选项属于**第三方模块 `nix-flatpak`（作者 gmodena）**，需要额外引入 flake input 才能用。**网上大量教程把它们当成 nixpkgs 内置选项，是错的。**

**添加 Flathub（命令式，不是 Nix 声明）**：

```bash
flatpak remote-add --if-not-exists flathub \
  https://dl.flathub.org/repo/flathub.flatpakrepo

# 装应用
flatpak install flathub com.spotify.Client

# 更新全部
flatpak update

# 清理未使用的运行时
flatpak uninstall --unused
```

> [!NOTE]
> **Flatpak 的远程仓库和应用是「命令式」管理的，不在你的 NixOS 配置里。** 这意味着换机器时它们**不会自动带过去** —— 你需要手动重装，或者用 `nix-flatpak` 第三方模块把它声明化。

**portal 的作用**：Flatpak 应用运行在沙箱里，**不能直接访问你的文件系统、屏幕、摄像头**。portal 是「沙箱 → 宿主机」的受控桥梁。GNOME 模块自动加 `xdg-desktop-portal-gnome` + `-gtk`；KDE 模块自动加 `-kde` + `-gtk` + kwallet。

### 7.3 坑与反直觉

| 坑 | 事实 |
|---|---|
| **不开 portal 会构建失败** | `services.flatpak.enable` 有**硬断言**要求 `xdg.portal.enable = true` |
| **`services.flatpak.remotes` 不存在** | 属第三方 `nix-flatpak` 模块，不是 nixpkgs 选项 |
| `xdg.portal.extraPortals` 断言非空 | 开 portal 时必须至少有**一个**后端；GNOME/KDE 自动填，其它桌面要手写 |
| **旧选项被移除** | `xdg.portal.gtkUsePortal` 已删；`services.flatpak.extraPortals` 已重命名为 `xdg.portal.extraPortals` |
| **中文字体** | 模块会自动设 `fonts.fontDir.enable = true`，**系统字体（含中文）通常已可见** —— 不需要额外折腾 |
| **主题不统一** | nixpkgs **无原生解**。用 `flatpak override --filesystem=xdg-config/gtk-3.0:ro` 让沙箱读宿主机 GTK 配置，或在沙箱内单独装主题 |
| **调宿主机命令** | `flatpak-spawn --host` 需要先 `flatpak override --talk-name=org.freedesktop.Flatpak` |
| 中文输入法失效 | 部分 Flatpak 应用在沙箱里读不到输入法。**这是用 Flatpak 跑中文应用的主要代价** |

> [!TIP]
> **中文字体在 Flatpak 里其实不用额外配。** nixpkgs 的 flatpak 模块已经自动设了 `fonts.fontDir.enable = true`，系统字体目录对沙箱可见。网上「Flatpak 里中文变方框」的教程大多针对其它发行版。

---

## 八、Steam 与游戏

### 8.1 基础配置（AMD 版）

```nix
{ pkgs, ... }: {
  programs.steam = {
    enable = true;   # ✅ 会自动开启 hardware.graphics.enable32Bit、steam-hardware、
                     #    以及 32 位 pipewire —— 不用你手动配
    remotePlay.openFirewall = true;        # Remote Play 串流所需端口
    dedicatedServer.openFirewall = true;   # 自建服务器所需端口
    gamescopeSession.enable = true;        # 提供 gamescope 会话（见 §8.4）
    extraCompatPackages = with pkgs; [ proton-ge-bin ];   # 声明式安装 GE-Proton
  };

  # 性能工具
  programs.gamemode.enable = true;                          # 游戏启动时自动提频 / 调 nice
  programs.gamescope = { enable = true; capSysNice = true; };  # 允许 gamescope 自行 renice

  # AMD 用户：Vulkan 默认走 Mesa RADV，无需任何配置
  # 只有在某些游戏错误地选了 AMDVLK 时才需要强制：
  # environment.variables.AMD_VULKAN_ICD = "RADV";
}
```

> [!TIP]
> **`programs.steam.enable = true` 会自动帮你开 32 位图形栈。** 源码里它是**硬赋值**（不是 `mkDefault`）：
>
> ```nix
> # nixos/modules/programs/steam.nix:205-210（在 config = lib.mkIf cfg.enable 之下）
> hardware.graphics = {
>   enable = true;
>   enable32Bit = true;
> };
> ```
>
> 所以你**不需要**在别处再写一遍。**但要注意这是硬赋值**：如果你在别处写 `hardware.graphics.enable32Bit = false`，会直接 **option conflict 构建报错**；反过来你自己写 `= true` 是安全的（同值不冲突，见 §14.7.3）。
>
> **为什么 32 位驱动对 Steam 是必需的？** 大量游戏（尤其老游戏和部分 Proton 组件）是 32 位二进制，需要 32 位的 Vulkan / OpenGL 驱动。

> [!NOTE]
> **AMD 用户不需要装任何专有驱动，也不需要 `allowUnfree`（为显卡）。** 这是 AMD 相对 NVIDIA 的显著优势 —— NVIDIA 用户必须 `allowUnfree = true` 才能装驱动，AMD 用户只在需要某些非自由软件（如 Steam 本身的部分组件、特定游戏）时才需要。

> 出处：`nixos/modules/programs/steam.nix` `[核实·源码]`；[NixOS Wiki · Steam](https://wiki.nixos.org/wiki/Steam) `[Wiki]`

**Steam 为什么能在 NixOS 上跑非 Nix 游戏**：Steam 的 **Steam Runtime 本身就是一个 FHS 容器**。它提供游戏所需的 `/usr`、`/lib` 层级，游戏在里面看到的是「正常 Linux」。所以 Steam 游戏**基本不受 NixOS 无 FHS 的影响**。

`pkgs.steam-run` 就是这个 FHS 环境的独立入口，可以拿来跑别的二进制。

### 8.2 Steam 库放在哪：绝对不要用 NTFS

> [!DANGER]
> **Valve 官方 Proton Wiki 明确写了：*"NOT OFFICIAL - USING NTFS IS NOT RECOMMENDED"***
>
> 原文更具体的表述是：Valve *"discourages"* 这样做，*"may lead to unexpected errors"*，并且 **"You WILL run into problems"**。
>
> 出处：[ValveSoftware/Proton Wiki · Using a NTFS disk with Linux and Windows](https://github.com/ValveSoftware/Proton/wiki/Using-a-NTFS-disk-with-Linux-and-Windows) `[官方]`

**结论**：Steam 库用 **ext4 或 btrfs**。

**如果你必须和 Windows 双系统共享游戏盘**：Proton Wiki 给出的做法是把 `compatdata` 目录**软链接到 Linux 分区**（因为 Proton 的前缀里有大小写敏感的文件，NTFS 的大小写不敏感会导致游戏损坏）。但这仍是「能跑但不推荐」。

### 8.3 反作弊游戏现状

**EAC / BattlEye 是否可用逐游戏而定**，取决于开发者是否开启了 Proton 支持。查询：https://areweanticheatyet.com/ `[社区]`

| 状态 | 代表游戏 |
|---|---|
| ✅ **Supported** | Halo MCC、Back 4 Blood、ARK、DayZ、Dead by Daylight、SMITE |
| ⚠️ **Running**（能跑，可能需额外操作） | Paladins、Black Desert、Fall Guys（需 Proton-GE）、Halo Infinite（需补丁） |
| ❌ **Broken** | PUBG |
| ⛔ **Denied**（开发者明确封禁） | Fortnite、Apex Legends、Valorant、Rainbow Six Siege |

> [!WARNING]
> **不要尝试在「Denied」的游戏里绕过反作弊。** 这会导致账号被封，而且违反服务条款。

### 8.4 gamescope：Wayland 下的游戏合成器

`programs.steam.gamescopeSession.enable = true` 会生成一个 **Wayland 会话**（`steam.desktop`），Exec 大致是：

```
gamescope --steam -- steam -tenfoot -pipewire-dmabuf
```

**它的用途**：提供一个**独立的、全屏的、可精细控制分辨率和刷新率**的游戏会话。类似 Steam Deck 的「游戏模式」。

**怎么用**：

1. 在登录界面（GDM / SDDM）的会话选择里选 **Steam Session / gamescope**
2. 或者在普通桌面里对单个游戏用启动项：`gamescope -W 2560 -H 1440 -r 144 -- %command%`

> 出处：`nixos/modules/programs/steam.nix` `[核实·源码]`

> [!TIP]
> **对 AMD 用户，gamescope 的额外价值是 VRR 控制。** 它能在合成器层面锁定刷新率范围，让 FreeSync 更稳定地工作。

### 8.5 其它游戏工具

| 工具 | 包名 | 用途 |
|---|---|---|
| **MangoHud** | `mangohud` | 游戏内性能覆盖层（FPS / 帧时间 / 温度） |
| **ProtonUp-Qt** | `protonup-qt` | 图形化管理多版本 Proton / GE-Proton |
| **Lutris** | `lutris` | 通用 Wine / 模拟器游戏管理 |
| **Heroic** | `heroic` | Epic / GOG / Amazon 游戏 |
| **Bottles** | `bottles` | 可视化 Wine 前缀管理 |
| **Prism Launcher** | `prismlauncher` | Minecraft 多实例 |
| **RetroArch** | `retroarch` | 模拟器前端 |

> [!DANGER]
> **`programs.mangohud` 在 NixOS 系统层【不存在】。**
>
> 网上大量教程写 `programs.mangohud.enable = true;` 放在 `configuration.nix` 里 —— **这会导致 eval 失败**。该选项**只存在于 Home Manager**。
>
> **NixOS 层的正确用法**：
> ```nix
> environment.systemPackages = with pkgs; [ mangohud ];
> ```
> 然后 Steam 启动项填 `mangohud %command%`，或全局 `environment.sessionVariables.MANGOHUD = "1";`

> 出处：[Home Manager · programs.mangohud](https://nix-community.github.io/home-manager/options/home-manager/programs/mangohud.html) `[官方]`（注意 URL 里的 `home-manager` 前缀）

### 8.6 系统调优（AMD 平台）

```nix
# vm.max_map_count：26.05 默认已是 1048576，一般无需手动设置
# （老教程里的 262144 是过时值）
# boot.kernel.sysctl."vm.max_map_count" = 1048576;

# CPU 调频：台式机可以设 performance，笔记本会耗电
powerManagement.cpuFreqGovernor = "performance";

# 内核：26.05 默认 6.18，RDNA2/3/4 无需换
# boot.kernelPackages = pkgs.linuxPackages_latest;
```

> [!WARNING]
> **`powerManagement.cpuFreqGovernor` 与 `services.tlp` / `power-profiles-daemon` 可能冲突。**
> GNOME / KDE 会自动开 `power-profiles-daemon`。**三个别同时开** —— TLP 与 ppd 之间甚至有互斥断言。

> [!NOTE]
> **`services.thermald` 不要开** —— 那是 Intel 专用的散热守护。AMD 机器上开了没有任何作用（见 §3.4）。

### 8.7 nix-gaming（第三方 flake，可选进阶）

提供 nixpkgs 里没有的游戏工具：`wine-tkg`、`wine-cachyos`、`osu-stable`、`rocket-league`、`star-citizen` 等，以及两个模块：`pipewireLowLatency`、`platformOptimizations`。

```nix
inputs.nix-gaming.url = "github:fufexan/nix-gaming";

# ⚠️ 不配缓存会从源码编译，极慢
nix.settings.substituters = [ "https://nix-gaming.cachix.org" ];
nix.settings.trusted-public-keys = [
  "nix-gaming.cachix.org-1:nbjlureqMbRAxR1gJ/f3hxemL9svRfzI17kGPMBzKAc="
];
```

> [!WARNING]
> **风险**：需要信任第三方 binary cache（理论上可注入内容）；部分包是 unfree；与 nixpkgs 版本可能漂移。**只在你明确需要某个包时引入。**

---

## 九、Vibe Coding 工具链（非 root 部署）

### 9.1 三个工具的分工

| 工具 | 出品方 | 分发方式 | 定位 |
|---|---|---|---|
| **Hermes Agent** | Nous Research | **Python**（`uv` / pip） | 通用 agent，可装 skills、接 MCP |
| **OpenClaw** | OpenClaw 项目 | **Node**（`install-cli.sh` → `~/.openclaw`） | Agent harness，运营 `clawhub.ai` skills 市场 |
| **OpenAI Codex CLI** | OpenAI | **npm**（`@openai/codex`） | 编码专用 CLI agent |

> [!WARNING]
> **一个常见的错误前提：Hermes Agent 不是 npm 包。** 它是 **Python** 分发的（Nous Research 出品），通过 `uv` 或 pip 安装。网上若有人说「`npm install -g hermes-agent`」，那是错的。
>
> 出处：[github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) `[仓库]`

> [!IMPORTANT]
> **本章只讲「怎么把二进制装上」——即 `npm`/`uv`/`pip` 这些包管理器在 NixOS 上的障碍与绕法。**
>
> **如果你要问的是「怎么装成服务、怎么自启、作为服务会不会因为 root 权限导致我改不了配置、能不能用 Home Manager / flake / 官方 bash」——那是另一套问题，见第二十一章。** 两章的分工：
>
> | 你想知道 | 看哪章 |
> |---|---|
> | `npm install -g` 为什么失败、怎么把全局目录改到家目录 | **本章**（第九） |
> | 怎么给 agent 配 skills / MCP / 权限护栏 | 第十章、第十六章 |
> | Hermes / OpenClaw **怎么装、怎么自启、root 权限边界** | **第二十一章** |
> | 它们在 NixOS 上的**坑与故障** | **第二十二章** |
>
> **一句话预告第二十一章的结论**：`nix run` / `nix profile install` 装上就跑（本章的路），**配置完全可写、agent 能自己改**；一旦上了 NixOS / Home Manager 模块，配置就变成声明式**只读**，agent 改不了（但你也**不需要 root**）。**两者不可兼得**（§21.12）。

### 9.2 NixOS 上的三个通用障碍

不管你装哪个 agent，在 NixOS 上都会撞到这三面墙：

**障碍 1：`npm install -g` 必然失败**

`npm install -g` 会往 `/nix/store` 或 `/usr/lib/node_modules` 写东西，而这两处**都是只读的**。你会看到 `EACCES: permission denied`。

> [!DANGER]
> **不要用 `sudo npm install -g` 去「解决」它。** 这会往 Nix 管理的目录里塞文件，导致系统状态与配置不一致 —— 下次 `nixos-rebuild` 可能把它们清掉，或者更糟，留下损坏状态。
>
> **正解：把 npm 全局目录改到你的 home。**

```bash
# 让 npm 的全局安装落到用户目录
npm config set prefix ~/.npm-global
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 现在可以正常全局安装了
npm install -g @openai/codex
```

**障碍 2：官方二进制找不到动态链接器**

见 §1.2。任何「官方下载的二进制」在 NixOS 上都会报 `No such file or directory`（文件明明在）。

**解法：`programs.nix-ld`（最推荐的兜底）**

```nix
programs.nix-ld = {
  enable = true;
  # ⚠️ 这里写的是【追加】项 —— 模块已自带 14 个基础库（zlib/zstd/stdenv.cc.cc/
  #    curl/openssl/attr/libssh/bzip2/libxml2/acl/libsodium/util-linux/xz/systemd）。
  #    因为 libraries 是 listOf，你写的是拼接而非替换（详见 §15.8.3）。
  libraries = with pkgs; [
    stdenv.cc.cc.lib    # libstdc++（与基础集里的 stdenv.cc.cc 同源，冗余但无害）
    libxkbcommon        # GUI 应用常用（基础集没有）
    libglvnd            # OpenGL 调度（基础集没有）
  ];
};
```

> [!NOTE]
> **`nix-ld` 只补链接器，不提供完整 FHS 目录。** 它适合「只缺 libc 和几个 .so」的 CLI 程序。**图形依赖复杂的**（Electron、带 GPU 加速的）不够用 —— 那种需要 `buildFHSEnv`，或者直接用 Nix 打包的版本。

**障碍 3：Python 工具链**

`uv` 是现代 Python 工具链管理器的首选（比 pip/pipx 快得多）。在 NixOS 上：

```bash
# 临时用
nix shell nixpkgs#uv

# 或永久装进用户 profile
nix profile install nixpkgs#uv
```

**用 `uv` 安装 Python 工具（隔离在用户目录）**：

```bash
# 装成「工具」（相当于 pipx install，隔离在 ~/.local）
uv tool install <包名>

# 运行
uv tool run <命令>
# 或直接（因为 ~/.local/bin 已在 PATH）
<命令>
```

> [!TIP]
> **`uv tool install` 是 NixOS 上装 Python CLI 工具最干净的方式。** 它把每个工具隔离在独立虚拟环境里（`~/.local/share/uv/tools/`），互不干扰，也不碰系统 Python。

### 9.3 装到哪里：三种位置的取舍

| 位置 | 命令 | 优点 | 缺点 |
|---|---|---|---|
| **临时** | `nix shell nixpkgs#<pkg>` | 不污染系统 | 退出即消失 |
| **用户 profile** | `nix profile install nixpkgs#<pkg>` | 持久、可 `nix profile list` 管理 | 不在配置里，换机不带走 |
| **系统配置** | `environment.systemPackages = [ pkgs.<pkg> ]` | 在 git 里，可复现 | 每改一次要 rebuild |

**对 agent 工具的推荐**：**用 `~/.npm-global` / `uv tool` / `~/.local/bin`**，不要放进 `environment.systemPackages`。

**为什么**：agent 工具迭代极快，放系统配置里意味着每次升级都要 `nixos-rebuild`。放用户目录可以随时 `npm update -g` / `uv tool upgrade`，**秒级完成，且不碰系统状态**。

> [!IMPORTANT]
> **这正好呼应了你的要求：「不要做成 root 服务，否则用户很难配置」。**
>
> 同一个逻辑适用于**安装位置**：**放用户目录 = 你能随时自己改；放系统配置 = 每次都要走 rebuild 流程。** 对快速迭代的 AI 工具，前者明显更合适。

### 9.4 三个工具的安装步骤

#### Hermes Agent（Python）

**Hermes 是 Python 分发的**（Nous Research 出品），并且**官方提供 Nix flake**。

```bash
# 方式 A：用 uv 装（推荐，隔离在用户目录）
nix shell nixpkgs#uv              # 或 nix profile install nixpkgs#uv
uv tool install hermes-agent

# 方式 B：官方 flake（如果它提供了 NixOS 模块）
nix run github:NousResearch/hermes-agent
```

> [!IMPORTANT]
> **Hermes 需要一个「托管 Python」环境，因此必须开 `programs.nix-ld.enable`。**
>
> 原因：Hermes 会下载并管理自己的 Python 运行时（以及 Node / Chromium 二进制）。这些**预编译二进制**在 NixOS 上找不到动态链接器（见 §1.2），会报 `No such file or directory`。
>
> `programs.nix-ld` 是解决这个问题的标准手段（配置见 §9.2）。

> [!WARNING]
> **Hermes 的 NixOS 模块的确切选项名未能核实。** 官方文档提到它提供 Nix flake，但模块的具体选项（如 `services.hermes.*` 是否存在）**未能从一手来源确认**。已记入附录 C。
>
> **务实建议**：用 `uv tool install` 装在用户目录，不要走 NixOS 模块 —— 这样**改配置不用 rebuild**，正好符合你「不要 root 服务」的要求。

#### OpenClaw（Node）

**OpenClaw 是一个 Node 框架**，运营 `clawhub.ai`（官方 skill 市场）。

```bash
# 官方安装脚本 —— 装到 ~/.openclaw，【不需要 root】
curl -fsSL https://openclaw.ai/install-cli.sh | bash
```

**配置文件**：`openclaw.json`

> [!IMPORTANT]
> **OpenClaw 的安装脚本装到 `~/.openclaw`，是纯用户级安装。** 这正是你要的形态 —— **不要试图把它做成 root 服务。**
>
> **它有自己的 skill 市场（clawhub.ai）**，所以 skills 可以通过 `clawhub` 直接装。

> [!WARNING]
> **关于 OpenClaw 的信息可信度**：本次调研中，OpenClaw 的**公开一手资料相对有限**。安装脚本路径、配置文件名（`openclaw.json`）、以及它与 clawhub.ai 的关系**来自官方站点**，但更细节的部分（如完整的 CLI 子命令、skill 目录结构）**未能从一手来源充分核实**。已记入附录 C。
>
> **建议**：安装前先访问官方站点确认最新的安装方式，不要完全依赖本指南。

#### OpenAI Codex CLI（npm）

```bash
# 先改 npm 全局目录（NixOS 必需，见 §9.2）
npm config set prefix ~/.npm-global
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 安装
npm install -g @openai/codex

# 验证
codex --version
```

**配置文件**：`~/.codex/config.toml`

> [!TIP]
> **Codex 也提供 Rust 原生二进制的 `install.sh` 路线。** 那条路线在 NixOS 上需要 `programs.nix-ld` 兜底（因为是预编译二进制）。**npm 路线更省事。**

### 9.5 API 密钥管理（不要硬编码）

三个工具都需要 API key（OpenAI / Anthropic / 或第三方兼容端点）。**不要把 key 写进 Nix 配置或 git 仓库。**

| 方式 | 安全性 | 说明 |
|---|---|---|
| 环境变量（`~/.bashrc`） | ⚠️ 中 | 简单，但会被子进程继承 |
| `~/.config/<tool>/config.json` | ⚠️ 中 | 注意文件权限 `chmod 600` |
| **系统密钥环（keyring）** | ✅ 高 | 推荐；多数 agent 支持从 keyring 读 |
| `sops-nix` / `agenix` | ✅ 高 | 适合需要进 git 的配置 |

```bash
# 最低要求：如果写在文件里，锁权限
chmod 600 ~/.config/<tool>/config.json

# 确认 .gitignore 覆盖了它
grep -q "^\.env$" ~/.gitignore || echo ".env" >> ~/.gitignore
```

> [!WARNING]
> **如果你打算把 `/etc/nixos` 推到 git 仓库，绝对不要在里面写明文密钥。** Nix 的 store 是**全局可读**的 —— 任何用户都能读 `/nix/store` 里的文件。写进 Nix 配置的密钥等于对全机公开。
>
> 需要密钥进配置时，用 `sops-nix` 或 `agenix`。

### 9.6 让 agent 常驻后台

三个工具都可以作为**用户级服务**常驻（不是 root 服务）。具体写法见 **§10.5 与 §10.6**。

**要点回顾**：

- 用 `systemd.user.services`（NixOS 声明）或 `~/.config/systemd/user/*.service`（原生）
- 加 `NoNewPrivileges = true` 限制提权
- 用 `ReadWritePaths` 白名单限制可写目录
- **永远不要写成 `systemd.services`（root）**

### 9.7 让它们能管理系统

这是第十章的完整内容。**一句话预告**：

> **agent 以普通用户运行，通过 MCP 获得「查询能力」（读），通过 skills 获得「流程知识」（怎么做），通过受限 sudo 获得「验证能力」（跑 dry-build），但「应用变更」这一步永远留给你。**

---

## 十、让 Agent 管理你的系统（skills + MCP）

### 10.1 先立规矩：为什么**不做** root 服务

你的要求是明确的：**Hermes Agent 和 OpenClaw 不要做成 root 权限的服务。** 这个决定是对的，理由有三层：

| 理由 | 说明 |
|---|---|
| **配置难度** | root 服务要写在 `configuration.nix` 里，**每改一次配置就要 `nixos-rebuild` 一次**。用户级服务写在 `~/.config/systemd/user/`，改完 `systemctl --user daemon-reload` 即可，秒级生效 |
| **权限过大** | root 的 agent 能做任何事 —— 包括改 `system.stateVersion`（可能损坏数据库）、删 `/home`、改分区表。**一次幻觉就可能不可逆** |
| **责任边界** | agent 以 root 跑时，你无法分辨「它做的」和「系统做的」。审计日志混在一起 |

> [!IMPORTANT]
> **核心原则：agent 以普通用户运行，通过「受限通道」获得有限系统能力。**
>
> 不是「给它 root 但求它别乱来」，而是「**从架构上让它没有能力乱来**」。这是安全设计的根本区别。

**用户级 vs 系统级服务对照**：

| | 系统级（不要用） | 用户级（推荐） |
|---|---|---|
| 声明位置 | `systemd.services.<name>`（在 `configuration.nix`） | `systemd.user.services.<name>`（NixOS）或 `~/.config/systemd/user/*.service` |
| 运行身份 | root | 你自己 |
| 改配置成本 | 必须 `nixos-rebuild` | `systemctl --user daemon-reload` |
| 能读写的文件 | 整个文件系统 | 只有你的 home + 明确授权的路径 |
| 崩溃影响 | 可能影响系统启动 | 只影响你这个会话 |
| 环境变量 | 需要显式声明 | 继承你的登录环境 |

### 10.2 四种「让 agent 管系统」的方案

这是本章的核心。**按安全性从高到低排列**，建议从方案 1 起步。

| 方案 | 权限范围 | 安全性 | 配置难度 | 适用场景 |
|---|---|---|---|---|
| **1. 只写配置，人工执行** | agent 只能改文件，**不能执行任何特权命令** | ⭐⭐⭐⭐⭐ 最高 | ★ 最低 | **推荐起点**。日常 90% 的场景 |
| **2. 受限 sudoers** | 只能执行**白名单里的具体命令** | ⭐⭐⭐ 中 | ★★ 中 | 想让 agent 自动跑 `dry-build` 验证 |
| **3. polkit 规则** | 按「动作」授权（如「允许管理系统服务」） | ⭐⭐ 偏低 | ★★★ 高 | 需要细粒度但复杂的场景 |
| **4. 用户级 systemd 服务** | 只能管自己的服务 | ⭐⭐⭐⭐ 高 | ★★ 中 | 让 agent 常驻后台、定时任务 |

> [!DANGER]
> **绝对不要给 agent `NOPASSWD: ALL` 的 sudo 权限。** 这等于给了它完整 root。它可能出于「好意」执行破坏性操作（比如「帮你清理磁盘」时跑了 `nix-collect-garbage -d`，删掉你所有回滚点）。
>
> **也不要给 agent 的 sudoers 白名单里放 `nixos-rebuild`（不带参数限制）** —— 因为 `nixos-rebuild` 会执行配置里的任意 activation script，**等价于 root**。

### 10.3 方案 1 的实现：只写配置，人工执行（推荐起点）

**这是最简单也最安全的模式**。agent 的全部能力是「写文件」，你保留「执行」这个动作。

**工作流**：

```
你：「把 Firefox 固定到 154 版本」
  ↓
agent：查 search.nixos.org 确认选项名 → 查 NixHub 拿 commit → 写进 configuration.nix
  ↓
agent：告诉你「改好了，请运行 sudo nixos-rebuild dry-build」
  ↓
你：看一眼 git diff → 运行 dry-build
  ↓
通过 → 你运行 sudo nixos-rebuild switch
不通过 → 把报错贴回给 agent
```

**为什么这个模式足够好用**：NixOS 是**声明式**的。agent 改的是「描述文件」，不是「运行中的系统」。**文件改错了不会立刻出事** —— 只有你执行 rebuild 时才生效。这天然形成了一道人工闸门。

> [!TIP]
> **这个模式的关键配套是 git。** 让 `/etc/nixos` 纳入 git，agent 每次改完你都能 `git diff` 一眼看清它改了什么。**AI 改配置最大的风险不是它改错，而是你没看清它改了什么。**

### 10.4 方案 2 的实现：受限 sudoers

如果你想让 agent **自动跑验证**（不用你每次手动 dry-build），可以给一条**极窄的**白名单。

**NixOS 里的声明方式**：

```nix
security.sudo.extraRules = [
  {
    users = [ "你的用户名" ];
    commands = [
      # 只允许 dry-build，且不给它跑 switch 的能力
      {
        command = "/run/current-system/sw/bin/nixos-rebuild dry-build";
        options = [ "NOPASSWD" ];
      }
    ];
  }
];
```

> [!WARNING]
> **sudo 的命令匹配是「前缀字符串匹配」，很脆弱。** 上面的写法理论上允许 `nixos-rebuild dry-build; rm -rf /` 这类拼接（取决于 sudo 版本与配置）。**更稳的做法是写一个包装脚本**，只接受固定参数：

```nix
# 写一个只做 dry-build 的包装脚本
environment.systemPackages = [
  (pkgs.writeShellScriptBin "nixos-check" ''
    set -euo pipefail
    # 只接受一个可选的 flake 路径参数，其它一律拒绝
    if [ $# -gt 1 ]; then
      echo "用法: nixos-check [flake-path]" >&2
      exit 2
    fi
    exec ${config.system.build.nixos-rebuild}/bin/nixos-rebuild dry-build ''${1:+--flake "$1"}
  '')
];

security.sudo.extraRules = [
  {
    users = [ "你的用户名" ];
    commands = [
      { command = "/run/current-system/sw/bin/nixos-check"; options = [ "NOPASSWD" ]; }
    ];
  }
];
```

**这个模式的价值**：agent 可以「改配置 → 自己跑验证 → 看到报错 → 自己修」形成闭环，**但始终没有 `switch` 的能力**。最后一步永远握在你手里。

### 10.5 方案 4 的实现：用户级 systemd 服务

如果 agent 需要**常驻**或**定时**运行（比如每天检查有没有可更新的包），用用户级服务。

**在 NixOS 里声明**（`systemd.user.services`）：

```nix
systemd.user.services.my-agent = {
  description = "My vibe coding agent";
  wantedBy = [ "default.target" ];
  serviceConfig = {
    Type = "simple";
    ExecStart = "%h/.local/bin/my-agent --daemon";
    Restart = "on-failure";
    RestartSec = 10;
    # 关键：限制它的能力
    NoNewPrivileges = true;
    PrivateTmp = true;
    ProtectHome = "read-only";     # 或 "tmpfs" 更严
    ProtectSystem = "strict";
    ReadWritePaths = [ "%h/.config/my-agent" "%h/.local/share/my-agent" ];
  };
};
```

> [!NOTE]
> **`systemd.user.services` 与 `systemd.services` 的区别**：前者生成的是**用户级** unit（`systemctl --user` 管理，运行身份是你），后者是**系统级**（root 运行）。`%h` 是 home 目录占位符。
>
> 在 NixOS 上，用户级服务由 `systemd.user.services` 声明后会在**用户登录时**启动（`wantedBy = [ "default.target" ]`）。

> [!IMPORTANT]
> **如果你希望 agent 服务「不登录也运行」（比如作为常驻服务），必须开启 lingering。**
>
> **声明式写法**（推荐，进你的配置）：
> ```nix
> users.users.你的用户名.linger = true;
> ```
>
> **命令式写法**（立即生效，重启后仍有效）：
> ```bash
> sudo loginctl enable-linger 你的用户名
> ```
>
> 不开 lingering 的话，你注销登录后用户级服务会被 systemd 停掉。**这是用户级服务最常见的「为什么它半夜没跑」原因。**

**能力限制字段说明**（这是「非 root 但不裸奔」的关键）：

| 字段 | 作用 |
|---|---|
| `NoNewPrivileges = true` | 禁止通过 setuid 提权（**最重要的一条**） |
| `ProtectHome = "read-only"` | home 目录只读，agent 改不了你的文件 |
| `ProtectSystem = "strict"` | 整个 `/usr`、`/boot`、`/etc` 只读 |
| `PrivateTmp = true` | 独立 `/tmp`，看不到其它进程的临时文件 |
| `ReadWritePaths = [...]` | **白名单**：只有这些路径可写 |

> [!TIP]
> **加了 `NoNewPrivileges = true` 之后，即使 agent 被诱导执行 `sudo` 也会失败。** 这是「架构上不给它能力」的具体体现，比任何提示词约束都可靠。

### 10.6 另一种做法：直接写 `~/.config/systemd/user/`

如果你**不想**把 agent 服务写进 NixOS 配置（因为那样每改一次都要 rebuild），可以直接用 systemd 原生方式：

```bash
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/my-agent.service <<'EOF'
[Unit]
Description=My agent
After=default.target

[Service]
Type=simple
ExecStart=%h/.local/bin/my-agent --daemon
Restart=on-failure
NoNewPrivileges=true

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now my-agent
systemctl --user status my-agent
```

> [!NOTE]
> **在 NixOS 上这样做是可行的**，因为 `~/.config/systemd/user/` 是普通目录，不受 Nix 管理。**它不会被 GC 删除**（GC 只清 `/nix/store`），也不会在 `nixos-rebuild` 时被清理。
>
> **取舍**：这种方式「改起来快」，但**不在你的配置版本控制里** —— 换机器时不会自动带过去。**建议**：日常迭代用这种，稳定后再固化到 `systemd.user.services`。

### 10.7 MCP：给 agent 装「眼睛」

**MCP（Model Context Protocol）让 agent 能查询外部数据源。** 对 NixOS 运维，最重要的是 **`mcp-nixos`**。

`mcp-nixos` 聚合了五个查询源里的四个（见第十二章）：

| 数据源 | 内容 |
|---|---|
| nixpkgs 包 | 包名、版本、描述 |
| **NixOS 选项** | 选项名、类型、默认值、示例 |
| **Home Manager 选项** | 同上，HM 专属 |
| nix-darwin / Nixvim / NVF | 其它生态 |
| **FlakeHub / Noogle / NixHub** | 版本历史与函数文档 |
| NixOS Wiki / nix.dev | 文档全文检索 |

> 出处：[github.com/utensils/mcp-nixos](https://github.com/utensils/mcp-nixos) `[仓库]`

**为什么这个 MCP 特别有价值**：**它不需要你本机装 Nix。** 它是纯 HTTP 查询（内部封装了前面那些站点的 API），所以可以在任何地方跑。

> [!IMPORTANT]
> **MCP 是「读」，不是「写」。** `mcp-nixos` 只能**查询**，不能改你的系统。这正是它安全的原因 —— 它给 agent 装的是「眼睛」，不是「手」。
>
> **「手」是 skills 和 shell 工具。** 两者要分开评估风险。

### 10.8 skills：给 agent 装「手」

**skill 是一份写给 agent 看的操作手册。** 它把「这类任务该怎么做」固化下来，避免 agent 每次即兴发挥。

**通用格式**（`SKILL.md` + YAML frontmatter）：

```markdown
---
name: nixos-config-edit
description: 安全地修改 NixOS 配置并验证。当用户要求改 NixOS 设置、装系统包、
  调内核参数时使用。必须遵循「先查选项名 → 再改配置 → dry-build 验证」的流程。
---

# NixOS 配置修改流程

## 铁律
1. **绝不修改 `system.stateVersion`**
2. **绝不直接 `nixos-rebuild switch`**，必须先 dry-build
3. 改之前先 `git -C /etc/nixos diff` 确认当前状态

## 步骤
1. **查选项的准确名字** —— 用 mcp-nixos 或访问
   https://search.nixos.org/options?channel=26.05&show=<选项名>
   **不要凭记忆写选项名。** NixOS 选项是强类型的，写错会在 eval 阶段失败。
2. 读 `/etc/nixos/configuration.nix` 了解现有结构
3. 用最小改动完成需求
4. 运行 `sudo nixos-rebuild dry-build` 验证
5. 如果失败，读报错 → 回到第 1 步
6. **报告给用户**：改了什么文件、为什么、dry-build 结果

## 禁止清单
- `system.stateVersion`
- `boot.loader.*`（改错会开不了机）
- `fileSystems.*`（改错会丢数据）
- `boot.kernelParams`（改错可能无法启动）
- 任何 `nix-collect-garbage -d` 之类的破坏性清理
```

> [!TIP]
> **skill 的真正价值是「把流程固化」。** 没有 skill 时，agent 可能直接改配置然后跑 `switch`；有了 skill，它知道必须走 dry-build 闸门。**skill 是把你的人为约束写成 agent 能读的规则。**

**三个工具的 skills 机制对比**：

| 工具 | skill 格式 | 位置 | 通用性 |
|---|---|---|---|
| **Hermes Agent** | `SKILL.md` | 见官方文档 | ✅ 与 OpenClaw 通用 |
| **OpenClaw** | `SKILL.md` | 通过 `clawhub.ai` 市场分发 | ✅ 与 Hermes 通用 |
| **Codex CLI** | `AGENTS.md` | 项目根目录 / `~/.codex/` | ⚠️ 格式不同 |

> [!IMPORTANT]
> **Hermes 与 OpenClaw 共用 `SKILL.md` 格式 —— 一份 skill 两边都能用。** 这是很实用的发现：你只需要维护一份 NixOS 运维 skill。
>
> **Codex 用的是 `AGENTS.md`**（面向编码任务的项目级指令文件），格式与 `SKILL.md` 不同。**所以你不能把同一份文件直接给 Codex 用**，需要转换。

> [!NOTE]
> **`SKILL.md` 的核心结构是「YAML frontmatter + 正文」**，其中 `name` 和 `description` 是必需的 —— `description` 决定 agent **什么时候**加载这个 skill（模型根据它做触发判断）。所以 `description` 要写清「什么场景下用」。

### 10.9 安全护栏：五条硬规则

> [!DANGER]
> **必须人工确认的四类配置（agent 只能提议，不能自己应用）：**
>
> 1. `system.stateVersion` / `home.stateVersion` —— 改了可能触发数据迁移、损坏数据库
> 2. `boot.loader.*` —— 改错**开不了机**
> 3. `fileSystems.*` —— 改错**丢数据**
> 4. `boot.kernelParams` —— 改错可能**无法启动**（尤其 `amd_pstate`、`pcie_aspm` 这类）

**完整护栏流程**：

```
① agent 生成改动
      ↓
② 你 `git -C /etc/nixos diff` 看它到底改了什么   ← 人工闸门 1
      ↓
③ sudo nixos-rebuild dry-build                   ← 零成本验证闸门
      ↓
④ 涉及 boot / 内核 / 分区？ → sudo nixos-rebuild build-vm 真跑一遍   ← 人工闸门 2
      ↓
⑤ sudo nixos-rebuild switch（或 boot）
      ↓
⑥ 健康检查：systemctl --failed；journalctl -b -p err
      ↓
⑦ 出问题 → sudo nixos-rebuild switch --rollback
```

**为什么这套流程在 NixOS 上特别有效**：

| 特性 | 作用 |
|---|---|
| 声明式 | agent 改的是「描述」，不是「运行中的系统」 |
| 强类型选项 | 幻觉的选项名在 **eval 阶段**就被拒绝，不会悄悄生效 |
| `dry-build` | 零成本验证闸门，等于给 agent 一个沙盒试衣间 |
| generation | 出问题**原子回滚**，不是「重装」 |
| git | 你能看清 agent 改了什么 |

**这四重保险叠加起来，让 NixOS 成为「AI 辅助运维」最安全的发行版。** 传统发行版里，agent 一条 `rm` 或一次错误的 `apt` 操作就可能不可逆。

### 10.10 一个真实闭环：让 agent 每天检查可更新项

**目标**：每天早上 9 点，agent 检查有没有可更新的包，生成一份报告放到 `~/reports/`，**但不自动升级**。

```nix
# 用户级 systemd timer + service
systemd.user.services.agent-daily-check = {
  description = "Agent 每日 NixOS 可更新项检查";
  serviceConfig = {
    Type = "oneshot";
    ExecStart = "%h/.local/bin/daily-nix-check.sh";
    NoNewPrivileges = true;
    ProtectSystem = "strict";
    ReadWritePaths = [ "%h/reports" ];
  };
};

systemd.user.timers.agent-daily-check = {
  description = "每天早上 9 点触发";
  wantedBy = [ "timers.target" ];
  timerConfig = {
    OnCalendar = "09:00";
    Persistent = true;
  };
};
```

`~/.local/bin/daily-nix-check.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail

mkdir -p "$HOME/reports"
OUT="$HOME/reports/nix-check-$(date +%F).md"

{
  echo "# NixOS 可更新项检查 $(date +%F)"
  echo
  echo "## 当前系统"
  nixos-version
  echo
  echo "## flake input 是否有更新"
  cd /etc/nixos
  nix flake metadata --json | head -40
  echo
  echo "## 待更新的包（只列出，不升级）"
  nix store diff-closures /run/current-system "$(nix build --no-link --print-out-paths .#nixosConfigurations.mypc.config.system.build.toplevel 2>/dev/null || echo /run/current-system)" 2>/dev/null | head -60
} > "$OUT" 2>&1

echo "报告已生成: $OUT"
```

**这个闭环体现了本章的全部原则**：

- agent 以**你的身份**运行（不是 root）
- 服务是**用户级**的（改配置不用 rebuild）
- `NoNewPrivileges = true` + `ProtectSystem = "strict"` —— **架构上限制了它的能力**
- 它只能**写报告**，不能改系统
- 你看到报告后**自己决定**要不要升级

> [!TIP]
> **想让它更进一步（自动升级）？** 那就给它方案 2 的受限 sudoers，允许它跑 `nixos-check`（只做 dry-build）。**但仍然不给它 `switch`。** 让它把「验证通过的改动」提交到一个 git 分支，你 review 后合并。

---

## 十一、长期运维与跨版本升级

### 11.1 日常维护：四条配置一次配好

这四条是 NixOS 长期使用的**最低维护配置**，建议装完就加：

```nix
# ── 1. 自动垃圾回收 ──
nix.gc = {
  automatic = true;
  dates = "weekly";
  options = "--delete-older-than 30d";   # ⚠️ 用 30d，不要用 -d
  persistent = true;                      # 错过时间就补跑
};

# ── 2. store 去重（节省磁盘）──
nix.settings.auto-optimise-store = true;

# ── 3. 限制 bootloader 菜单条数（防止 /boot 被撑爆）──
boot.loader.systemd-boot.configurationLimit = 10;

# ── 4. 保留 30 天内的 generation ──
```

> [!DANGER]
> **绝对不要用 `nix-collect-garbage -d`。** `-d` 会删除**所有**旧 generation，包括你的回滚点。用了之后 `nixos-rebuild --rollback` 就无路可退。永远用 `--delete-older-than 30d`。

> [!NOTE]
> **为什么必须同时配 `configurationLimit`？** GC 只管 `/nix/store`，**不管 `/boot`**。`/boot` 是 FAT32 的 EFI 分区，通常只有 512 MB–1 GB，而每个内核 + initrd 约 100 MB。不限制条数，几个月后 `/boot` 满了 → 新内核写不进去 → 升级静默失败。

### 11.2 AMD 平台的「混合版本策略」：比 NVIDIA 宽松得多

这是**你在 AMD 平台上的一大红利**，值得单独说清。

**通用原则**（适用于所有硬件）：**能滚「叶子」，不能滚「根」。**

但「什么是根」**在 AMD 和 NVIDIA 上完全不同**：

| 组件 | NVIDIA 能不能滚 | **AMD 能不能滚** | 原因 |
|---|---|---|---|
| Mesa（图形栈） | ⚠️ 有风险 | ✅ **可以自由滚** | AMD 用 Mesa 驱动，无专有驱动配对 |
| 内核（linux） | ❌ 绝对不行 | ⚠️ **能滚，但没必要**（见下方 §11.2.1） | `amdgpu` 在主线内核里，无配对约束；**但 26.05 的 `linuxPackages_latest` 已是 7.2.9，与 unstable 逐字相同** |
| 浏览器（Firefox/Chromium） | ✅ | ✅ | 纯用户态叶子包 |
| 游戏组件（gamescope / mangohud） | ✅ | ✅ | 不进内核 |
| 系统模块（systemd / glibc） | ❌ | ❌ | 由 `nixosSystem` 决定 |
| **Realtek `r8168`（若在用）** | — | ⚠️ **需与内核同源** | 它是**树外模块**，换内核要重编 |

> [!IMPORTANT]
> **对 AMD 用户，真正的约束只剩两条**：① 系统基础组件（systemd/glibc）不能跨源；② **如果你用 `r8168` 树外驱动，它必须和内核同源**。除此之外，**Mesa 可以放胆用新版**。
>
> **NVIDIA 用户最大的痛点（内核与驱动强配对）在你这里不存在。** 这是 AMD 在 Linux 上运维成本更低的核心原因。
>
> **⚠️ 但「内核可以滚」这条在 2026-10-12 被实测修正了 —— 见下方 §11.2.1。** 技术上可行 ≠ 有收益。

**实现方式：flake 双 input**

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";          # 稳定基座
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable"; # 滚动源
  };
  outputs = { nixpkgs, nixpkgs-unstable, ... }: {
    nixosConfigurations.mypc = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./configuration.nix
        ({ pkgs, ... }: {
          # 把 unstable 挂到 _module.args，供配置里按需引用
          _module.args.pkgsUnstable = import nixpkgs-unstable {
            inherit (pkgs.stdenv.hostPlatform) system;
            inherit (pkgs.config) allowUnfree;   # 让 unstable 的 unfree 包也放行
          };
        })
      ];
    };
  };
}
```

配置里这样用（**只滚你真正需要的叶子包**）：

```nix
{ pkgs, pkgsUnstable, ... }:
{
  # AMD 用户可以放胆滚 Mesa（NVIDIA 用户不要照抄这行）
  hardware.graphics.package   = pkgsUnstable.mesa;
  hardware.graphics.package32 = pkgsUnstable.pkgsi686Linux.mesa;   # 32 位必须一起换

  # 浏览器
  programs.firefox.package = pkgsUnstable.firefox;

  # 内核：❌ 不要写成 pkgsUnstable.linuxPackages_latest（见 §11.2.1）
  boot.kernelPackages = pkgs.linuxPackages_latest;   # ✅ 26.05 上已是 7.2.9，跟基座走
}
```

#### 11.2.1 「内核可以自由滚」这条被实测修正了（2026-10-12）

**原稿（v1.0–v1.4）的表述**：AMD 用户「内核可以自由滚」，示例代码写 `boot.kernelPackages = pkgsUnstable.linuxPackages_latest;`。

**问题**：这句话在「技术上能不能」是对的，但**漏掉了「有没有收益」**。2026-10-12 在两个分支上逐包实测：`[核实·源码]`

| 组件 | 26.05 | nixos-unstable | 差异 |
|---|---|---|---|
| 内核 `linuxPackages_latest` | **7.2.9** | **7.2.9** | **无** |
| 内核 `linuxPackages`（默认） | **6.18.55**（LTS） | **6.18.55**（LTS） | **无** |

**源码依据**：两分支的 `pkgs/top-level/linux-kernels.nix` 里 `packageAliases` **逐字相同**（都是 `linux_default = packages.linux_6_18; linux_latest = packages.linux_7_2;`），且两边 `kernels-org.json` 里 `"7.2" → 7.2.9`、`"6.18" → 6.18.55` 完全一致。**stable 分支会定期把内核 rebase 到最新补丁。**

> [!IMPORTANT]
> **在 26.05 上，跨源拿内核 = 多拉一整份 nixpkgs，换来的版本号一模一样。**
>
> 正确写法是在**同一个 nixpkgs 内**选内核分支：
>
> ```nix
> boot.kernelPackages = pkgs.linuxPackages_latest;   # 26.05 上 = 7.2.9（与 unstable 逐字相同）
> # 或
> boot.kernelPackages = pkgs.linuxPackages_zen;      # 低延迟，仍在 stable 内
> ```
>
> **这一行属于基座 `pkgs`，不跟 unstable。**
>
> **什么时候才真的需要跨源？** 只有当出现「比 26.05 的 7.2 更新的内核主线版本」而 26.05 还没 rebase 时。那时必须**先用 `nixos-rebuild build-vm` 验证、再 `boot` + 重启**，不要用 `switch`。
>
> **仍然不能跨源的情形**：`r8168` 等**树外内核模块**（必须与内核同源）、NVIDIA 闭源驱动、ZFS、VirtualBox。

**为什么跨源换内核真正会炸**（即使你不用树外模块，也该知道机制）：`boot.extraModulePackages` 类型是 `listOf types.package`，NixOS 把它拼进模块树（`nixos/modules/system/boot/kernel.nix:197-202`、`:394`）：

```nix
system.modulesTree = [ (lib.getOutput "modules" kernel) ] ++ config.boot.extraModulePackages;
```

**只要有任何模块往这里塞「来自稳定 nixpkgs」的包，而内核来自 unstable，模块树里就会出现「为 6.18 编译的 .ko」与「7.2 内核」并存。** 这是跨源换内核真正的失败模式 —— 不是内核本身，而是模块树。

> [!WARNING]
> **同一个包不能同时被两份 nixpkgs 定义。** 你选了 `pkgsUnstable.mesa`，就不能再在别处引用 `pkgs.mesa`。混用的真正风险不是「版本太新」，而是「**同一个包有两个来源，导致依赖树撕裂**」。
>
> 社区原帖（2024-08）的编者按原话：**「强烈建议不要混用，这是不受支持的」** `[社区]`
> https://discourse.nixos.org/t/mixing-stable-and-unstable-packages-on-flake-based-nixos-system/50351

**❌ 不推荐的写法：用 overlay 把 unstable 塞进 `pkgs`**

```nix
# 不要这样做
nixpkgs.overlays = [ (final: prev: { inherit (pkgsUnstable) mesa firefox; }) ];
```

官方论坛原话是「完全没必要，很可能拖慢 eval」`[官方论坛]` —— 因为 overlay 会让**所有**包求值时都重新走一遍你的覆盖逻辑。

### 11.3 flake 会「锁版本」吗？能不能自动更新？

这是最常见的误解。**答案：flake 做不到「不锁」，但能做到「自动换锁」。**

| 路线 | 锁版本 | 全自动 | 可复现 |
|---|---|---|---|
| channel + `nixos-rebuild switch --upgrade` | **不锁**（每次拿最新） | ✅ | ❌ 低 |
| flake 手动 `nix flake update` | 锁 | ❌ 要手动 | ✅ 高 |
| flake + 自动换锁 | 锁（但自动刷新） | ✅ | ✅ 高 |

**`flake.lock` 就是「锁」的物理形式。** 它记录每个 input 精确到 commit。**锁是可复现的基础，不是缺点** —— 它保证你今天和三个月后构建出**一模一样**的系统。

自动化有四个层次，按可靠性排序：

**层次 1：`system.autoUpgrade`（官方 Wiki 写法）**

```nix
system.autoUpgrade = {
  enable = true;
  flake = "/etc/nixos";              # 你的 flake 路径
  flags = [ "--commit-lock-file" ];  # 更新后提交 lock
  dates = "04:00";
  allowReboot = false;               # 不自动重启（推荐）
  runGarbageCollection = true;
};
```

> 出处：[NixOS Wiki · Automatic system upgrades](https://wiki.nixos.org/wiki/Automatic_system_upgrades) `[Wiki]`

**层次 2：两段式（社区实测更可靠）** `[社区]`

单独跑 `nix flake update`，再跑 rebuild，用 systemd 依赖串起来：

```nix
systemd.services.flake-update = {
  description = "Update flake inputs";
  path = [ pkgs.nix pkgs.git ];
  script = "nix flake update --flake /etc/nixos";
  serviceConfig.Type = "oneshot";
};

systemd.services.nixos-upgrade = {
  after = [ "flake-update.service" ];
  requires = [ "flake-update.service" ];
};
```

> 出处：[NixOS Discourse · How to automatically update flakes（2025-11 实测有效）](https://discourse.nixos.org/t/how-to-automatically-update-flakes/72426) `[社区]`

**层次 3：GitHub Action 定时提 PR**（在应用前插入人工审查）

用 `DeterminateSystems/update-flake-lock`。适合「我想自动更新，但我要先看一眼」的场景。

> 出处：[github.com/DeterminateSystems/update-flake-lock](https://github.com/DeterminateSystems/update-flake-lock) `[仓库]`

**层次 4：让 agent 接管**（见第十章）

> [!DANGER]
> **`--update-input` 参数已废弃**（nixpkgs #349734）。老教程里的自动升级配置如果用了它，会导致**自动升级静默失败** —— 不报错，但什么也没更新。改用上面的写法。
>
> 出处：[github.com/NixOS/nixpkgs/issues/349734](https://github.com/NixOS/nixpkgs/issues/349734) `[仓库]`

**另外两个必踩的坑**：

```nix
# 坑 1：flake 目录不属 root → 需要给 root 的 git 放行
# /root/.gitconfig 加：
# [safe]
#     directory = /etc/nixos

# 坑 2：root 没有 git 身份 → 提交会失败
# 在 systemd 服务的环境变量里设：
# GIT_AUTHOR_NAME / GIT_AUTHOR_EMAIL / GIT_COMMITTER_NAME / GIT_COMMITTER_EMAIL
```

### 11.4 跨版本升级：26.05 → 26.11

**升级步骤（照做即可）**：

**第 1 步：读 release notes 的 breaking changes**

26.11 的 release notes 在：
https://github.com/NixOS/nixpkgs/blob/master/nixos/doc/manual/release-notes/rl-2611.section.md `[仓库]`

重点看 **Breaking changes** 和 **Deprecations** 两节 —— 这是「升级后开不了机」的主要来源。

**第 2 步：备份**

至少备份 `/etc/nixos`。重要数据单独备份。

**第 3 步：确认磁盘空间**

```bash
df -h /nix /boot
```
升级会下载大量新包。`/nix` 建议留 20 GB 以上，`/boot` 留 500 MB 以上。

**第 4 步：改 source 版本**

```nix
# flake 用户：改 flake.nix 里的分支
inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.11";

# 非 flake 用户：改 channel
sudo nix-channel --add https://nixos.org/channels/nixos-26.11 nixos
sudo nix-channel --update
```

**第 5 步：先 dry-build，再 build-vm**

```bash
sudo nixos-rebuild dry-build
# 通过后，生成虚拟机真跑一遍（强烈推荐）
sudo nixos-rebuild build-vm
./result/bin/run-*-vm
```

**第 6 步：正式升级**

```bash
sudo nixos-rebuild boot     # 用 boot，不要用 switch —— 重启后生效，且自动进 bootloader 菜单
sudo reboot
```

**第 7 步：验证**

```bash
nixos-version                       # 确认已是 26.11
systemctl --failed                  # 看有没有失败的服务
journalctl -b -p err --no-pager     # 看本次启动的错误日志
```

> [!IMPORTANT]
> **升级不需要改 `stateVersion`。** 这是最常见的误解。`stateVersion` 记录「初次安装版本」，升级后保持原值。改了会触发数据迁移逻辑，可能损坏数据库。
>
> 官方 FAQ：https://wiki.nixos.org/wiki/FAQ/When_do_I_update_stateVersion `[Wiki]`

**AMD 用户升级的额外注意**：如果你的内核从 26.05 跳到 26.11，`amdgpu` 会跟着内核一起升级 —— **这对你是好事**（新内核对新显卡支持更好）。但如果你的 Realtek 网卡在用 `r8168` 树外驱动，它会自动对新内核重编译，**编译失败会导致网卡不可用**。升级前先确认：

```bash
# 确认你的网卡用的是内核自带驱动还是树外驱动
lsmod | grep -E "r8168|r8169"
```

### 11.5 回滚：三级逃生通道

出问题时，按严重程度逐级使用：

| 级别 | 命令 | 适用 | 生效方式 |
|---|---|---|---|
| **1 级：临时试** | `sudo nixos-rebuild test` | 不确定的改动 | 重启即恢复 |
| **2 级：回滚 generation** | `sudo nixos-rebuild switch --rollback` | 改完发现问题 | 立即生效 |
| **3 级：进 bootloader 选旧条目** | 开机时按空格选旧 generation | **系统起不来** | 重启时选 |

> [!TIP]
> **第 3 级是终极保险。** 即使你把系统改到完全起不来，只要 bootloader 菜单还在，你就能选回上一个 generation。这就是 NixOS「几乎不可能变砖」的原因 —— **前提是你没配 `configurationLimit = 1` 也没用 `nix-collect-garbage -d`**。

### 11.6 备份策略

NixOS 的备份要分两层看，因为**大部分东西是「可重建的」**：

| 内容 | 需要备份吗 | 为什么 |
|---|---|---|
| `/etc/nixos`（你的配置） | ✅ **必须** | 这是你的全部劳动成果，几十 KB |
| `/home`（个人数据） | ✅ **必须** | 不可重建 |
| `/nix/store` | ❌ 不需要 | 可由配置重新构建 |
| 数据库（PostgreSQL 等） | ✅ 必须 | 在 `/var/lib`，不可重建 |
| `/var/lib/*` 的其它状态 | ⚠️ 视情况 | 如 Docker 镜像、虚拟机磁盘 |

```bash
# 最小备份：配置 + 数据
tar czf nixos-config-$(date +%F).tar.gz -C /etc nixos
```

> [!NOTE]
> **`/etc/nixos` 建议用 git 管理并推到私有仓库。** 这样你的系统配置天然有了版本历史和异地备份。注意：配置里可能有明文密码/密钥，**推私有仓库，且用 `sops-nix` 或 `agenix` 加密敏感值**。

---

## 十二、Nix 生态查询工具链

> NixOS 的痛点从来不是「装不上」，而是**找不到**：包在不在、选项叫什么、这个版本对应哪个 commit、这个 lib 函数怎么用。
> 下面五个站点各解决一块。**它们同时也是喂给 AI 的「地面真值」来源。**

### 12.1 五个工具的分工

| 工具 | 回答什么问题 | 运营方 | 有公开 API | 免费 |
|---|---|---|---|---|
| **search.nixos.org** | 包 / **选项** / 三方 flake 的**当前**状态 | NixOS 官方 | ⚠️ 后端是 ES，凭据非官方公开 | ✅ |
| **NixHub.io** | **历史版本**：某包某版本对应哪个 nixpkgs commit | Jetify | ✅ v2 REST | ✅（限流） |
| **FlakeHub** | flake 的 semver 发布与分发 | Determinate Systems | ✅ 部分 | ⚠️ Cache 需付费 |
| **Noogle** | `lib` / `builtins` / `pkgs` 里的**函数**文档 | nix-community | ✅ 全量 JSON | ✅ |
| **Jetify / Devbox** | 用 Nix 做开发环境，**不写 Nix 语言** | Jetify | — | ✅ |

**一句话记法**：

- 要查**选项** → search.nixos.org（唯一权威）
- 要查**旧版本** → NixHub
- 要**分发 flake** → FlakeHub
- 要写**函数** → Noogle
- 要**避开 Nix 语言** → Devbox

> [!TIP]
> **中文用户最常用的是第一个。** 你 90% 的查询需求是「这个选项到底叫什么名字」—— 直接去 `https://search.nixos.org/options`，搜索框里打关键词（支持模糊匹配描述文字）。

### 12.2 search.nixos.org —— 官方搜索（选项搜索是核心价值）

**地址**：https://search.nixos.org

| Tab | 搜什么 |
|---|---|
| Packages | nixpkgs 里的包 |
| **Options** | **NixOS 模块选项**（子分类：Official / Community(Home Manager) / External(Darwin) / Experimental） |
| Flakes | 三方 flake 及其提供的包/选项 |

**深链接有效**，可以直接分享 / 写进文档：

```
# 查某个选项（把 <选项名> 换掉）
https://search.nixos.org/options?channel=26.05&show=programs.steam.enable

# 查某个包
https://search.nixos.org/packages?channel=26.05&show=firefox
```

> [!NOTE]
> **`channel=26.05` 这个参数很重要。** 不指定的话默认是 unstable，而 unstable 的选项可能和你系统上的**不一致**。查自己系统时永远带上版本号。

**为什么选项搜索比包搜索重要**：NixOS 是声明式配置，**你实际写的是 option，不是 package**。选项文档分散在成百上千个模块里，`man configuration.nix` 浏览效率极低。选项搜索能按名称/描述直达某个模块的**默认值、类型、示例和源码位置**。

**数据来源**：后端是 Elasticsearch（bonsai.io 赞助），由 GitHub Actions 每 **2 小时**重建一次索引。

> 出处：[github.com/NixOS/nixos-search](https://github.com/NixOS/nixos-search) `[官方]`

**和 `nix search` 的区别**：

| | `nix search nixpkgs <name>` | search.nixos.org |
|---|---|---|
| 搜什么 | 可求值的 installable | 预建索引（包 + 选项 + 三方 flake） |
| **搜选项** | ❌ | ✅ |
| 需要本地有 nixpkgs | ✅ | ❌ |
| 输出 | 属性路径 + 版本 + description | 可筛选、可深链接 |

> [!WARNING]
> **`nix search` 搜不到选项。** 这是最常见的困惑。要查选项只有两条路：search.nixos.org 网页，或本机的 `nixos-option`（但后者**只能查已安装系统里存在的选项**，查不到「还没启用的模块」）。

### 12.3 NixHub.io —— 查历史版本（最有实用价值）

**它解决什么问题**：nixpkgs 是滚动的，**查不到「某包在某个月是什么版本」**。NixHub 把每个包的历次版本映射到包含它的 nixpkgs commit。

- 主页：https://www.nixhub.io
- 运营方：**Jetify**（Devbox 的同一家）
- 网页用法：`https://www.nixhub.io/packages/<包名>`

**公开 API（实测可用）**：官方文档只给相对路径，**实际主机是 `https://search.devbox.sh`**。

```bash
# 按名字搜包
curl "https://search.devbox.sh/v2/search?q=firefox"

# 取某包的全部历史版本（含每版对应的 nixpkgs commit）
curl "https://search.devbox.sh/v2/pkg?name=firefox"

# 名字 + 版本 → 解析出 commit 与属性路径（固定版本的关键）
curl "https://search.devbox.sh/v2/resolve?name=firefox&version=latest"
```

**实测返回（2026-10-12 真实抓取）**：

```json
{
  "name": "firefox",
  "version": "154.0.1",
  "systems": {
    "x86_64-linux": {
      "flake_installable": {
        "ref": { "type": "github", "owner": "NixOS", "repo": "nixpkgs",
                 "rev": "c27cdad491a991b11ed731760aa2ef8db0cb0410" },
        "attr_path": "firefox"
      }
    }
  }
}
```

**限流**：每 IP 初始 1000 次配额，每请求 −1，每分钟回补 5 次；耗尽返回 `429`。

**固定单个包到指定版本的完整工作流**：

```bash
# 第 1 步：拿到目标版本的 commit
curl -s "https://search.devbox.sh/v2/resolve?name=firefox&version=154" \
  | grep -o '"rev":"[a-f0-9]*"'
```

```nix
# 第 2 步：只把这一个包固定到旧版 nixpkgs
{ config, pkgs, ... }:
let
  pinned = builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/<commit>.tar.gz";
    # sha256 = "...";   # 生产环境必须加 hash，否则每次 eval 都可能重新下载
  };
  pkgsPinned = import pinned {
    inherit (pkgs.stdenv.hostPlatform) system;
    inherit (config.nixpkgs) config;
  };
in {
  programs.firefox.package = pkgsPinned.firefox;   # ✅ 模块化替换，只影响 Firefox
}
```

> [!WARNING]
> **用 `programs.firefox.package`，不要覆盖 `pkgs.firefox`。** 前者是模块化替换，只影响 Firefox；后者会牵动整个依赖树，可能导致其它包也用上旧版依赖。

> [!DANGER]
> **NixHub 的索引可能滞后。** 本文核实（2026-10-12）时，`hello` 和 `firefox` 的 `latest` 都解析到**同一个 commit**（`date` 字段 = 2026-08-27），说明索引可能滞后数周。
>
> **用它做版本决策前，务必核对返回的 `date` 字段，并与 search.nixos.org 交叉验证。**

**另一种「固定版本」的思路（推荐长期使用）**：不用 NixHub，而是把**整个 nixpkgs 固定到某个 commit** —— 这就是 flake 的 `flake.lock` 在做的事。NixHub 适合**「只回退一个包」**的场景。

### 12.4 FlakeHub —— flake 的语义化版本与分发

**它解决什么问题**：Nix 本身**没有 SemVer 概念**，flake 难以发现、难以复用、更新粒度粗。FlakeHub 给 flake 加上 SemVer 约束。

URL 结构：`https://flakehub.com/f/:org/:project/:version-req`

| 写法 | 含义 |
|---|---|
| `*` | 最高已发布版本 |
| `1.*` | 主版本为 1 的任意版本 |
| `=3.2.1` | 精确锁定 |
| `0.1.1` | 至少 0.1.1，但不会升到 0.2.0 |

**nixpkgs 在 FlakeHub 上的版本映射**：

| FlakeHub 版本 | 对应 nixpkgs |
|---|---|
| `0` / `*` | 最新稳定 |
| `0.2605` | `nixos-26.05` 分支最新 |
| `0.1` | unstable |

```nix
# 等价写法
inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
inputs.nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.2605";   # 同一个东西
```

> 出处：[docs.determinate.systems/flakehub](https://docs.determinate.systems/flakehub/) `[官方]`

**FlakeHub Cache（付费）**：官方原文 *"FlakeHub Cache is available only on paid plans."* Free 层只含公开 flake，**不含 Cache**。Individual $7/月，Team $20/用户/月。

> 出处：[docs.determinate.systems/flakehub/cache](https://docs.determinate.systems/flakehub/cache/) 与 [flakehub.com/pricing](https://flakehub.com/pricing) `[官方]`

> [!WARNING]
> **FlakeHub 有两个必须知道的争议：**
>
> 1. **它是中心化的第三方服务。** 发布时（2023-08-22）在 NixOS Discourse 上有明确批评，有成员认为它「是第三方的、中心化的、专有的，且似乎无意上游化」。`[社区]`
>    https://discourse.nixos.org/t/introducing-flakehub/32044
> 2. **它上面的 nixpkgs 实际由 DetSys 镜像提供**（实测 API 返回的 `repo_url` 指向 `DeterminateSystems/flakehub-mirror`），不是直连上游。这意味着你多了一个中间层和一个停服风险。
>
> **建议：日常用上游 GitHub 源。** 只有当你确实需要「SemVer 约束 + 团队分发 + 细粒度缓存权限」时才引入 FlakeHub。

| | 用 `github:NixOS/nixpkgs/nixos-26.05` | 用 `flakehub.com/f/NixOS/nixpkgs/0.2605` |
|---|---|---|
| 权威性 | 上游官方 | 经 DetSys 镜像 |
| 免费缓存 | `cache.nixos.org` | Cache 需付费 |
| 版本表达 | 分支名（无 semver） | **SemVer 约束** |
| `nix flake update` 行为 | 拉到分支最新 | **只在允许范围内升级** |
| 停服风险 | 无 | 有 |

### 12.5 Noogle —— Nix 函数搜索引擎

**它解决什么问题**：写配置时想「有没有一个把 list 转成 attrs 的函数」，但你不知道它叫什么。

- 地址：https://noogle.dev
- 仓库：https://github.com/nix-community/noogle（MIT）
- 索引范围：`builtins`、`lib`、**以及 `pkgs`** 里的函数

**返回什么**（以 `lib.mkIf` 为例）：类型签名、文档注释、源码位置（文件/行/列）、别名、示例。

**两个最有用的功能**：

1. **按类型签名过滤** —— 搜「从 list 到 list 的函数」：
   `https://noogle.dev/q?term=map&from=list&to=list&limit=20`
2. **别名检测** —— 自动告诉你 `lib.mkIf` 同时也是 `lib.modules.mkIf`

**API**：

> [!DANGER]
> **`noogle.dev/api/v1/search` 不存在** —— 实测返回 **404**。很多教程里写的这个端点都是错的。
>
> **真实存在的公开端点**是全量数据下载：
>
> ```bash
> # 全量数据集（约 4.4 MB JSON，实测 2145 条记录）
> curl -s https://noogle.dev/api/v1/data -o noogle-data.json
> ```

> [!TIP]
> **这是五个工具里唯一能「完全离线」使用的数据源。** 把这份 JSON 下载下来，你可以喂给本地 LLM 或建本地检索 —— 无需联网、无需认证。

### 12.6 Jetify / Devbox —— 不写 Nix 语言用 Nix

**先澄清归属**：**NixHub 是 Jetify 做的**。Jetify 旗下产品：

| 产品 | 是什么 |
|---|---|
| **Testpilot** | **AI QA / 端到端测试 agent —— 现在是 Jetify 的旗舰** |
| **Devbox** | 隔离开发环境 CLI（Apache-2.0） |
| **NixHub** | 包版本注册表 + API |
| **Jetify Cloud** | Jetify Cache（私有 Nix 缓存）、Jetify Secrets |

**Devbox 的定位**（官方原文）：*"an approachable, intuitive interface for creating development environments with the Nix Package Manager, **without the Nix language**"*

在 NixOS 上安装：

```bash
nix profile install nixpkgs#devbox
# 或要最新版
nix profile install github:jetify-com/devbox/latest
```

**杀手功能 —— 固定版本**：

```bash
devbox add python@3.10          # 自动解析并写入 devbox.lock
```

> [!WARNING]
> **两个必须澄清的误解：**
>
> 1. **`devbox generate` 不是 AI 功能。** 它生成 devcontainer / Dockerfile / direnv 脚手架。
> 2. **Jetify 没有官方的 Devbox MCP server。** 网上出现的 `devbox-mcp-server` 是 **Microsoft Dev Box**（Azure 产品），与 Jetify 完全无关。
>
> **Jetify 的 AI 集中在 Testpilot，不在 Devbox。**

### 12.7 串起来：一个真实工作流

**场景**：把 Firefox 固定到某个旧版本，并且**绝不编造选项名**。

```bash
# ① 查选项的准确名字、类型、默认值 —— search.nixos.org（唯一权威）
#    https://search.nixos.org/options?channel=26.05&show=programs.firefox.package

# ② 查历史版本 → 拿到 commit —— NixHub
curl -s "https://search.devbox.sh/v2/resolve?name=firefox&version=154" | grep -o '"rev":"[a-f0-9]*"'

# ③ 查 lib 函数（如果要写条件判断）—— Noogle
#    https://noogle.dev/q?term=mkIf

# ④ 写进 configuration.nix

# ⑤ 验证闸门 —— 这一步不可跳过
sudo nixos-rebuild dry-build
```

**第 ⑤ 步是关键**：前四步都在「查」，只有这一步在「验」。**Nix 的强类型选项系统会让错误的选项名在 eval 阶段立刻失败** —— 这就是为什么「查准」比「猜对」重要得多。

### 12.8 这些工具和 AI 的关系

**`mcp-nixos` 已经把这五个数据源里的四个聚合了。** 它的数据源覆盖：

nixpkgs 包 · **NixOS 选项** · **Home Manager 选项** · nix-darwin · Nixvim · NVF · **FlakeHub** · **Noogle** · NixOS Wiki · nix.dev · **NixHub**

> 出处：[github.com/utensils/mcp-nixos](https://github.com/utensils/mcp-nixos) `[仓库]`

**这意味着两条路径**：

| 路径 | 适合 | 代价 |
|---|---|---|
| 人工查这五个站点 | 你在写配置、需要理解 | 慢，但你能学到东西 |
| 让 agent 通过 `mcp-nixos` 查 | 批量、重复、你不关心细节 | 需要装 MCP server（见第十章） |

> [!IMPORTANT]
> **给 AI 加这些工具的价值（一句话）**：**AI 幻觉在 NixOS 上的代价是「系统起不来」，而这些工具提供的是可验证的地面真值。** 两者是互补的，不是替代的。

### 12.9 坑与反直觉

| 坑 | 事实 |
|---|---|
| `noogle.dev/api/v1/search` | **不存在**（实测 404）。真实端点是 `/api/v1/data`（全量） |
| NixHub API 主机名 | 官方文档**只给相对路径**，实际主机是 `https://search.devbox.sh`（实测） |
| NixHub 索引实时性 | 实测 `latest` 解析到 2026-08-27 的 commit，**可能滞后数周**，用前核对 `date` |
| search.nixos.org 后端 API | 存在但**需要 Basic Auth，凭据从未官方公开**。别自己抓，用 `mcp-nixos` |
| search.nixos.org 筛 broken | **没有这个筛选器**（社区有抱怨帖） |
| `nix search` 搜选项 | **不能**。要搜选项只能用 search.nixos.org |
| FlakeHub 上的 nixpkgs | 实际由 **DetSys 镜像**提供，不是直连上游 |
| FlakeHub 发布 flake | **不是 `fh publish`**，是 GitHub Action `flakehub-push` |
| FlakeHub Cache | **不免费**（Free 层只含公开 flake） |
| `devbox generate` | **不是 AI 功能**，是脚手架生成器 |
| Devbox 的 MCP | **Jetify 无官方 MCP**；`devbox-mcp-server` 是 Microsoft Azure 的 |

---

## 十三、完整配置（可直接复制）

> [!IMPORTANT]
> **下面的配置基于本文全部核实过的选项。** 每一项都在前面的章节解释过「为什么」。
>
> **使用前请改三处**：① `networking.hostName`；② `users.users.你的用户名`；③ 桌面环境二选一（GNOME 或 KDE）。
>
> **第一次用请先 `sudo nixos-rebuild dry-build` 验证**，不要直接 `switch`。

### 13.1 单文件版：`configuration.nix`（起步推荐）

```nix
# ═══════════════════════════════════════════════════════════════════
#  /etc/nixos/configuration.nix
#  AMD 显卡 + AMD CPU + Realtek 有线网卡 · 中文用户
#  GNOME / KDE · Flatpak · Steam · Vibe Coding
#  基准：NixOS 26.05「Yarara」
# ═══════════════════════════════════════════════════════════════════
{ config, pkgs, lib, ... }:

{
  # ─────────── 0. 系统标识（装完就别动）───────────
  system.stateVersion = "26.05";   # ⚠️ 永不修改

  # ─────────── 1. 引导 ───────────
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
  boot.loader.systemd-boot.configurationLimit = 10;   # 防止 /boot 撑爆

  # ─────────── 2. 网络（Realtek 螃蟹卡）───────────
  networking.hostName = "amd-nixos";
  networking.networkmanager.enable = true;

  # Realtek 有线网卡需要 rtl_nic/*.fw 固件
  hardware.enableRedistributableFirmware = true;

  # 不写 networking.interfaces.* —— 交给 NetworkManager 管理
  # 网卡名用 `ip link` 查（现代系统是 enp4s0 这类，不是 eth0）

  # 如果 RTL8125 随机掉线，才考虑换厂商驱动（树外模块，慎用）：
  # boot.extraModulePackages = [ config.boot.kernelPackages.r8125 ];
  # boot.blacklistedKernelModules = [ "r8169" ];

  # ─────────── 3. 中文环境 ───────────
  i18n.defaultLocale = "zh_CN.UTF-8";
  i18n.extraLocaleSettings = { LC_TIME = "zh_CN.UTF-8"; };
  time.timeZone = "Asia/Shanghai";

  fonts = {
    enableDefaultPackages = true;      # 默认已含 Noto CJK
    packages = with pkgs; [
      noto-fonts
      noto-fonts-cjk-sans
      noto-fonts-cjk-serif
      noto-fonts-color-emoji           # ⚠️ 不是 noto-fonts-emoji
      wqy-zenhei
    ];
    fontconfig.defaultFonts = {
      # 拉丁字体在前，中文在后（顺序反了英文会难看）
      sansSerif = [ "Noto Sans" "Noto Sans CJK SC" "WenQuanYi Zen Hei" ];
      serif     = [ "Noto Serif" "Noto Serif CJK SC" ];
      monospace = [ "JetBrains Mono" "Noto Sans Mono CJK SC" ];
      emoji     = [ "Noto Color Emoji" ];
    };
  };

  i18n.inputMethod = {
    enable = true;                     # ✅ 26.05 新写法
    type = "fcitx5";
    # ⚠️ 不要用 environment.systemPackages 装 fcitx5（会破坏 addon 检测）
    fcitx5 = {
      addons = with pkgs; [
        fcitx5-chinese-addons          # 拼音 / 五笔
        fcitx5-rime                    # 中州韵
        fcitx5-configtool              # 图形配置工具
        fcitx5-gtk
        qt6Packages.fcitx5-qt
      ];
      waylandFrontend = true;          # Wayland 下不设 GTK/QT_IM_MODULE
    };
  };

  # ─────────── 4. AMD 硬件 ───────────
  hardware.cpu.amd.updateMicrocode = true;   # 默认 false，建议开

  hardware.graphics = {
    enable = true;        # ⚠️ 默认 false，GNOME/KDE 不会自动开
    enable32Bit = true;   # Steam / Wine 必需
  };

  # ⛔ 不要写 services.xserver.videoDrivers = [ "amdgpu" ]
  #    默认的 modesetting 才是现代 AMD 的推荐值

  # AMD 显卡超频能力（LACT 官方建议一并开启）
  hardware.amdgpu.overdrive.enable = true;

  # AMD 显卡控制工具（超频 / 降压 / 风扇曲线）
  services.lact.enable = true;

  # 内核：26.05 默认 6.18，RDNA2/3/4 无需更换
  # boot.kernelPackages = pkgs.linuxPackages_latest;   # 仅新卡需要

  # ═══════════ 5. 桌面环境：二选一 ═══════════

  # ── 选项 A：GNOME 50 ──
  services.desktopManager.gnome.enable = true;
  services.displayManager.gdm.enable = true;
  services.gnome.core-apps.enable = false;
  services.gnome.games.enable = false;
  environment.gnome.excludePackages = with pkgs; [
    gnome-tour gnome-user-docs totem cheese epiphany
  ];
  # ⛔ services.displayManager.gdm.wayland —— 26.05 已删除，写了构建失败

  # ── 选项 B：KDE Plasma 6.6（把上面 5 行注释掉，启用下面）──
  # services.desktopManager.plasma6.enable = true;
  # environment.plasma6.excludePackages = with pkgs.kdePackages; [ elisa ];
  # qt = { enable = true; platformTheme = "kde"; style = "breeze"; };

  # Electron 应用走 Wayland（VS Code / Discord 等）
  environment.sessionVariables.NIXOS_OZONE_WL = "1";

  # ─────────── 6. Flatpak ───────────
  services.flatpak.enable = true;
  xdg.portal.enable = true;            # ⚠️ 不开会构建失败（硬断言）
  xdg.portal.config.common.default = [ "gtk" ];
  # ⛔ services.flatpak.remotes 在 nixpkgs 26.05 不存在
  #    Flathub 用命令添加：flatpak remote-add --if-not-exists flathub <url>

  # ─────────── 7. Steam 与游戏 ───────────
  programs.steam = {
    enable = true;                     # 自动开 32 位图形栈 / steam-hardware / 32 位 pipewire
    remotePlay.openFirewall = true;
    gamescopeSession.enable = true;
    extraCompatPackages = with pkgs; [ proton-ge-bin ];
  };
  programs.gamemode.enable = true;
  programs.gamescope = { enable = true; capSysNice = true; };

  # ─────────── 8. 日常软件 ───────────
  environment.systemPackages = with pkgs; [
    # 基础
    firefox git vim wget curl htop btop fastfetch unzip
    # 图形诊断（排查 AMD 显卡问题用）
    mesa-demos            # glxinfo
    vulkan-tools          # vulkaninfo
    libva-utils           # vainfo
    clinfo                # OpenCL 信息
    pciutils usbutils     # lspci / lsusb
    # 游戏
    mangohud              # ⚠️ NixOS 无 programs.mangohud，用包 + 启动项
    protonup-qt
    # 开发 / vibe coding 运行时
    uv                    # Python 工具链
    nodejs_22             # Node（给 npm 系工具用）
  ];

  # ─────────── 9. 用户 ───────────
  users.users.你的用户名 = {           # ⚠️ 改成你的用户名
    isNormalUser = true;
    extraGroups = [
      "wheel"           # sudo
      "networkmanager"
      "video" "render"  # AMD 显卡访问
      "input"           # 输入设备
    ];
    linger = true;      # agent 用户级服务「不登录也运行」
  };

  # ─────────── 10. 国内镜像源 ───────────
  nix.settings.substituters = [
    "https://mirrors.ustc.edu.cn/nix-channels/store"          # 中科大
    "https://mirrors.tuna.tsinghua.edu.cn/nix-channels/store" # 清华
    "https://cache.nixos.org"                                 # 官方（回退）
  ];
  # ⚠️ 不需要改 trusted-public-keys —— 镜像用官方签名
  # ⛔ 不要用 nix.binaryCaches（仅 ≤21.11 存在）

  # ─────────── 11. 日常维护 ───────────
  nix.gc = {
    automatic = true;
    dates = "weekly";
    options = "--delete-older-than 30d";   # ⚠️ 不要用 -d
    persistent = true;
  };
  nix.settings.auto-optimise-store = true;

  # ─────────── 12. 非 Nix 二进制兜底 ───────────
  # Hermes Agent / Codex / OpenClaw 下载的预编译二进制靠它运行
  # 注意：libraries 是【追加】—— 模块自带 14 个基础库（见 §15.8.3）
  programs.nix-ld = {
    enable = true;
    libraries = with pkgs; [
      libxkbcommon libglvnd   # GUI 向的补充；CLI 场景可整行删掉
    ];
  };

  # ─────────── 13. 非自由软件 ───────────
  nixpkgs.config.allowUnfree = true;   # Steam 部分组件 / 某些游戏
}
```

### 13.2 flake 版（推荐长期使用）

**`/etc/nixos/flake.nix`**：

```nix
{
  description = "AMD NixOS 配置";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    # 需要滚动组件时才加（见 §11.2）
    # nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs, ... }@inputs: {
    nixosConfigurations.amd-nixos = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      specialArgs = { inherit inputs; };
      modules = [
        ./configuration.nix
        ./hardware-configuration.nix
      ];
    };
  };
}
```

**使用**：

```bash
cd /etc/nixos
git add flake.nix flake.lock configuration.nix hardware-configuration.nix
# ⚠️ 不 git add 的话 Nix 看不到这些文件！

sudo nixos-rebuild switch --flake /etc/nixos#amd-nixos
sudo nixos-rebuild dry-build --flake /etc/nixos#amd-nixos
```

> [!DANGER]
> **flake 的文件必须先 `git add`。** 未跟踪的文件会被 Nix **当作不存在**。这是新手第一大坑，且报错信息极具误导性。

### 13.3 自动更新（可选，加上就省心）

```nix
# 加进 configuration.nix
system.autoUpgrade = {
  enable = true;
  flake = "/etc/nixos";
  flags = [ "--commit-lock-file" ];
  dates = "04:00";
  allowReboot = false;         # 不自动重启
  runGarbageCollection = true;
};
```

> [!NOTE]
> **同时要配好 git 身份，否则自动升级会失败**（root 没有 git 身份时无法提交 lock 文件）。见 §11.3 的两个坑。

### 13.4 配置检查清单

改完配置、`dry-build` 通过后，逐项确认：

```bash
# ① 系统版本
nixos-version                       # 应为 26.05.x

# ② AMD 显卡驱动
lspci -k | grep -A3 -i vga          # 应显示 Kernel driver in use: amdgpu

# ③ 硬件视频解码
vainfo | head -20                   # 应列出 VAProfile*

# ④ Vulkan
vulkaninfo --summary | head -20     # 应显示 AMD RADV

# ⑤ 网卡
lspci -k | grep -A3 -i ethernet     # 应显示 Kernel driver in use: r8169
nmcli device status                 # 应显示 connected

# ⑥ 中文字体
fc-list :lang=zh | head -5          # 应列出中文字体

# ⑦ 输入法
fcitx5-diagnose | head -40          # 检查有无报错

# ⑧ 32 位图形栈（Steam 依赖）
ls /run/opengl-driver-32/lib 2>/dev/null | head -5

# ⑨ 失败的服务
systemctl --failed                  # 应为空

# ⑩ 本次启动的错误日志
journalctl -b -p err --no-pager | head -30
```

---

## 十四、游戏性能榨干（内核 · 调度器 · I/O · Valve 优化）

> 本章所有「默认值」结论都来自 **nixpkgs `nixos-26.05` 分支源码逐行比对**，不是网上教程的转述。带 `[核实·源码]` 的条目你可以自己用文末命令复核。

### 14.1 先搞清楚「什么真正影响帧数」

大部分游戏优化教程在教**收益接近 0** 的东西，却漏掉收益最大的。按实测收益排序：

| 优先级 | 手段 | 典型收益 | 风险 | 本章位置 |
|---|---|---|---|---|
| 🥇 **P0** | **Proton 版本 / 兼容层选对** | 巨大（10–50% 或「能跑/不能跑」） | 无 | §14.7 |
| 🥇 **P0** | **mesa 版本够新**（AMD 全靠它） | 大 | 低 | §14.2 |
| 🥈 P1 | **`hardware.graphics.enable32Bit`** | 巨大（Steam 32 位游戏必需） | 无 | §3.1 |
| 🥈 P1 | **内存是否够 / zram** | 大（掉帧、卡顿主因） | 无 | §14.8 |
| 🥉 P2 | 内核换 `linux_zen` | 中（延迟抖动改善） | 中 | §14.2 |
| 🥉 P2 | `scx` 调度器 | 中（**仅特定负载**） | 中高 | §14.3 |
| P3 | GameMode | 小到中 | 低 | §14.5 |
| P3 | gamescope | 中（**仅掌机/多显示器场景**） | 低 | §14.6 |
| P4 | I/O 调度器 | 小（SSD 上接近 0） | 低 | §14.4 |
| P4 | sysctl / governor | 小 | 低 | §14.9 |

> [!IMPORTANT]
> **结论先说**：AMD 平台上，「换内核」「换调度器」的收益**远小于**「Proton 选对 + mesa 够新 + 内存够」。先把 P0 做完再折腾 P2。

---

### 14.2 内核：默认 6.18 / `linux_zen` / `linux_xanmod` 源码级对比

**26.05 的默认内核已经是 6.18**（`[官方]` release notes：*"The default kernel package has been updated from 6.12 to 6.18."*）。这已经是相当新的内核，**对 AMD 游戏来说默认内核通常是够用的**。

nixpkgs 26.05 里**真实存在**的内核变体（已逐个核对 `pkgs/top-level/linux-kernels.nix`）：

| 属性名 | 状态 | 版本（26.05 快照） | 说明 |
|---|---|---|---|
| `linuxPackages`（= `linux_default`） | ✅ 默认 | **6.18** | `packageAliases.linux_default = packages.linux_6_18` |
| `linuxPackages_latest` | ✅ 存在 | **7.2** | `packageAliases.linux_latest = packages.linux_7_2` |
| `linuxPackages_zen` | ✅ 存在 | **7.2.9-zen1** | 桌面/游戏向补丁集 |
| `linuxPackages_xanmod` | ✅ 存在 | **6.18.55-xanmod1**（`variant = "lts"`） | ⚠️ 反直觉：`xanmod` 是 **LTS 线** |
| `linuxPackages_xanmod_stable` | ✅ 存在 | **7.2.9-xanmod1**（`variant = "main"`） | |
| `linuxPackages_xanmod_latest` | ✅ 存在 | **7.2.9-xanmod1**（`variant = "main"`） | 与 `_stable` **同一个 variant** |
| `linuxPackages_lqx` | ❌ **已删除** | — | `throw "removed due to lack of maintenance"` |
| `linuxPackages_libre` | ❌ **已删除** | — | 同上 |
| `linuxPackages_hardened` | ❌ **已删除** | — | 同上 |
| `linuxPackages_rt` | ❌ **已删除** | — | 同上 |
| `linuxPackages_cachyos` | ❌ **不存在** | — | nixpkgs **从未收录** |

> [!DANGER]
> **`linux_xanmod` 的版本号是反直觉的 —— 这是真实存在的命名陷阱。**
>
> `linux_xanmod` 用的是 `variant = "lts"` → **6.18.55**（LTS 内核）
> `linux_xanmod_stable` 和 `linux_xanmod_latest` 都用 `variant = "main"` → **7.2.9**
>
> 也就是说：**`linux_xanmod` 比 `linux_xanmod_latest` 版本号更低**，而 `_stable` 和 `_latest` 其实是同一个东西。
>
> 出处：`pkgs/top-level/linux-kernels.nix:130-152`、`pkgs/os-specific/linux/kernel/xanmod-kernels.nix`（`lts = 6.18.55`、`main = 7.2.9`）`[核实·源码]`

> [!DANGER]
> **两个最常见的错误前提：**
> 1. **nixpkgs 里没有 `linux_cachyos`。** CachyOS 的内核补丁**没有被 nixpkgs 收录**。想用只能自己 `overrideAttrs` 打补丁或走第三方 flake。网上说「`linuxPackages_cachyos`」的一律是错的。
> 2. **`linux_lqx` / `linux_libre` / `linux_hardened` / `linux-rt` 在 26.05 已全部移除**。老教程里推荐它们的内容已经失效。
>
>    出处的**精度**（这点值得说明）：
>    - `linux_hardened`（`linux-kernels.nix:187`）与 `linux-rt`（`:189-193`、`:748-749` 的 `linux_rt_default` / `linux_rt_latest`）→ **既有 release notes 明文**（`nixos/doc/manual/release-notes/rl-2605.section.md:232`、`:236`，均写 *"has been removed due to a lack of maintenance"*），也有源码 `throw`；
>    - `linux_lqx` / `linux_libre` → **只有源码 `throw`**（`linux-kernels.nix:155-157`：*"has been removed due to lack of maintenance"*），**release notes 未单独列出**。此处原稿把四个都归给 release notes，属于归因过宽，已修正。

> 出处：`pkgs/top-level/linux-kernels.nix:122,130-190,704-716` `[核实·源码]`

#### 三种内核的**编译期配置差异**（这才是「换内核有没有用」的答案）

这是本章最有价值的一张表。**它不是道听途说，是直接读 nixpkgs 里内核的 `structuredExtraConfig` 得出的**：

| 配置项 | 默认内核（6.18） | `linux_zen` | `linux_xanmod` | 对游戏的意义 |
|---|---|---|---|---|
| 抢占模型 | `PREEMPT=no` + **`PREEMPT_LAZY=yes`** | **`PREEMPT=yes`**（强制覆盖），`PREEMPT_LAZY=no` | 6.13+ 用 `PREEMPT_LAZY=yes`，`PREEMPT=no` | zen 是**完全抢占**，延迟最低但吞吐略降 |
| 时钟频率 HZ | 未设置（内核默认 **250**） | **`HZ=1000`** | `HZ=250` | zen 的 1000Hz 让调度更细，抖动更小 |
| I/O 调度器 | `MQ_IOSCHED_DEADLINE=yes`、`MQ_IOSCHED_KYBER=yes`、**`IOSCHED_BFQ=module`** | **`IOSCHED_BFQ=yes`**（内建） | 同默认 | zen **自带 BFQ**，不用额外加载模块 |
| CPU governor | **`CPU_FREQ_DEFAULT_GOV_SCHEDUTIL=yes`** | 继承 | **`GOV_PERFORMANCE=yes`**（强制） | xanmod 默认**性能模式**（更费电） |
| sched_ext（scx 前提） | **`SCHED_CLASS_EXT=yes`**（≥6.12） | 继承 | 继承 | **默认内核就能跑 scx**，不必换 zen |
| **ntsync** | ❌ **未设置**（即未启用） | ✅ **`NTSYNC=yes`** | 未设置 | **只有 zen 开了 ntsync** |
| FUTEX2 | 未设置 | ✅ `FUTEX=yes`、`FUTEX_PI=yes` | 未设置 | zen 明确为 Wine/Proton fsync 开启 |
| 网络拥塞控制 | 未设置 | `DEFAULT_FQ_CODEL=yes` | **`DEFAULT_BBR=yes`** | 对游戏**几乎无影响**（延迟由 fq_codel 管） |
| Zen 交互补丁 | ❌ | ✅ **`ZEN_INTERACTIVE=yes`** | ❌ | zen 的核心卖点 |
| RCU 增强 | 部分 | ✅ 完整（`RCU_BOOST` 等） | ✅ 完整 | 降低突发卡顿 |
| 空闲调度 | `NO_HZ_FULL`（64 位） | 继承 | `NO_HZ_IDLE=yes`、`NO_HZ=no` | 差异微小 |

> 出处：默认内核 `pkgs/os-specific/linux/kernel/common-config.nix:126,262-265,1417-1419,1430`；zen `.../kernel/zen-kernels.nix`；xanmod `.../kernel/xanmod-kernels.nix` `[核实·源码]`

**怎么选？**

```nix
# 方案 A：默认内核（推荐大多数人先用这个）
# 什么都不用写。26.05 的 6.18 已支持 scx、已有 PREEMPT_LAZY。

# 方案 B：linux_zen —— 想要完全抢占 + 1000Hz + 内建 BFQ + ntsync
boot.kernelPackages = pkgs.linuxPackages_zen;

# 方案 C：linux_xanmod —— 想要默认 performance governor + BBR
# boot.kernelPackages = pkgs.linuxPackages_xanmod_latest;
```

> [!WARNING]
> **换内核是有代价的：**
> 1. **编译/下载体积大**：zen 与 xanmod 没有官方缓存时可能需要**本地编译**（30 分钟到数小时）。NixOS 官方 cache 里有 zen/xanmod 的二进制，通常能直接下载。
> 2. **`boot.extraModulePackages` 要跟着换**：你第四章装的 `r8125` 是**内核外模块**，换内核后必须用新内核的 `kernelPackages.r8125`（写 `config.boot.kernelPackages.r8125` 就自动跟随，见 §4.3）。
> 3. **zen 的 `PREEMPT=yes` 会略微降低服务器型吞吐** —— 你是桌面游戏用途，无影响。
> 4. **换内核后先 `nixos-rebuild boot` + 重启验证**，不要直接 `switch`。出问题在 bootloader 里选上一个 generation。

> [!TIP]
> **`ntsync` 值不值得为它换 zen？** ntsync 是内核级的 Windows 同步原语模拟，能让 Proton 在**不用 esync/fsync 变通方案**的情况下获得低延迟同步。但 Proton 目前**默认仍走 fsync**，ntsync 需要显式启用。所以：**现在换 zen 的主要理由是「完全抢占 + 1000Hz + 内建 BFQ」，ntsync 是附带的好处，不是决定性理由。** `[部分未核实]`（Proton 对 ntsync 的默认启用状态未从一手来源确认）

---

### 14.3 `scx` 调度器（sched-ext）—— 26.05 原生支持

这是 26.05 最值得注意的新能力：**内核态可插拔调度器**。以前要打补丁，现在内核里有 `sched_ext`，用户态可以加载自定义调度器。

#### 前提条件

```bash
# 检查你的内核是否支持（有输出即支持）
ls /sys/kernel/sched_ext

# 检查内核版本（scx 要求 ≥ 6.12）
uname -r
```

> [!NOTE]
> **好消息：默认内核就支持。** nixpkgs 默认内核配置里有 `SCHED_CLASS_EXT = whenAtLeast "6.12" (whenPlatformHasEBPFJit yes)` `[核实·源码]`。**你不必换 zen 就能用 scx。**

#### 完整配置

```nix
services.scx = {
  enable = true;

  # 用哪个调度器。默认是 "scx_rustland"
  # 可选项 = pkgs.scx.full.schedulers 里的全部名字（见下表）
  scheduler = "scx_lavd";      # 游戏/桌面常用

  # 传给调度器的额外参数（每个调度器的参数互不兼容，先 --help）
  extraArgs = [ "--performance" ];
};
```

#### `services.scx` 模块的**全部**选项（源码级）

| 选项 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `enable` | bool | `false` | 开关 |
| `package` | package | **`pkgs.scx.full`** | 含全部调度器。可选 `pkgs.scx.rustscheds`（更小）。**改这个不会改默认调度器**，要用 `scheduler` 指定 |
| `scheduler` | **enum of `cfg.package.schedulers`** | **`"scx_rustland"`** | 合法值由 `package` 决定 —— 写错名字**会在求值期报错**（好事，不会静默失效） |
| `extraArgs` | list of str | `[ ]` | 运行时参数 |

> 出处：`nixos/modules/services/scheduling/scx.nix` `[核实·源码]`

#### 模块生成的 systemd 服务（理解它才能排错）

源码里生成的服务有几个**关键细节**：

| 配置 | 值 | 意味着什么 |
|---|---|---|
| `ConditionPathIsDirectory` | `/sys/kernel/sched_ext` | **内核不支持时服务直接不启动**（不报错、不失败，静默跳过） |
| `Restart` | `on-failure` | 调度器崩了会自动重启 |
| `startLimitIntervalSec` / `startLimitBurst` | `30` / `2` | **30 秒内失败 2 次就不再重启** —— 防止崩溃循环 |
| `environment.SCX_SCHEDULER` | `cfg.scheduler` | 服务读这个变量 |
| `environment.SCX_FLAGS` | 拼接后的 `extraArgs` | 同上 |
| `ExecStart` | `''${SCX_SCHEDULER_OVERRIDE:-$SCX_SCHEDULER} ''${SCX_FLAGS_OVERRIDE:-$SCX_FLAGS}` | **支持用环境变量临时覆盖**（调度器**和**参数各有一个覆盖变量），不必改配置 |
| `wantedBy` | `multi-user.target` | 开机自启 |

> [!TIP]
> **临时试另一个调度器，不用改 NixOS 配置**（重启后失效）：
> ```bash
> sudo systemctl set-environment SCX_SCHEDULER_OVERRIDE=scx_bpfland
> sudo systemctl restart scx
> # 用完清掉
> sudo systemctl unset-environment SCX_SCHEDULER_OVERRIDE
> sudo systemctl restart scx
> ```
> 这是**验证「某个调度器在我机器上是否更好」的最快方式**，比反复 `nixos-rebuild` 强得多。
>
> **还有第二个覆盖变量：`SCX_FLAGS_OVERRIDE`。** 源码的 `ExecStart` 实际是
> `exec ${cfg.package}/bin/${SCX_SCHEDULER_OVERRIDE:-$SCX_SCHEDULER} ${SCX_FLAGS_OVERRIDE:-$SCX_FLAGS}`
> —— 也就是说**参数（`extraArgs`）也能临时换**，可以不改配置就试 `--slice-us 5000` 之类的组合：
> ```bash
> sudo systemctl set-environment SCX_FLAGS_OVERRIDE="--slice-us 5000 --performance"
> sudo systemctl restart scx
> ```
> ⚠️ 两个变量都是**空串安全**的（`:-` 是「未设置或为空则取默认」），但如果你设了 `SCX_FLAGS_OVERRIDE=""`，`$SCX_FLAGS` 也不会生效 —— 想恢复默认要先 `unset-environment`。

#### 内核版本断言

模块里有硬断言：

```nix
assertion = lib.versionAtLeast config.boot.kernelPackages.kernel.version "6.12";
message = "SCX is only supported on kernel version >= 6.12.";
```

**内核 < 6.12 时求值期直接报错**，不会等到运行时。`[核实·源码]`

#### 可用调度器全清单（26.05 的 `pkgs.scx.full`，共 26 个）

`pkgs.scx.full` = `scx.cscheds` + `scx.rustscheds` 的 `buildEnv` 合并，`passthru.schedulers` 是两者之和。版本 **1.1.2**，上游 `sched-ext/scx`。

**Rust 调度器（18 个，生产可用）**

| 调度器 | 定位 | 备注 |
|---|---|---|
| `scx_lavd` | **延迟敏感 / 游戏** | 🔑 **Igalia 受 Valve 委托开发，动机就是 Steam Deck 的游戏负载**（见下方说明） |
| `scx_bpfland` | 交互式桌面 | 模块文档给的 `example` 就是它 |
| `scx_rusty` | 通用，最成熟 | 早期主力 |
| `scx_rustland` | **nixpkgs 默认值** | 用户态调度，开销略高 |
| `scx_layered` | 分层策略，可高度定制 | 配置最复杂 |
| `scx_flash` | 低延迟 | |
| `scx_beerland` | 交互式 | |
| `scx_cosmos` | 通用 | |
| `scx_mitosis` | 实验性 | |
| `scx_p2dq` | 每 CPU 双队列 | |
| `scx_tickless` | 无滴答 | |
| `scx_characterize` | **诊断工具**，非调度器 | 用来测量负载特征 |
| `scx_flow` / `scx_forge` / `scx_cake` / `scx_chaos` / `scx_pandemonium` / `scx_rlfifo` | 各类实验/特定场景 | 名字已说明性格 |

**C 语言示例调度器（8 个，教学用，不要在生产用）**

`scx_central`、`scx_flatcg`、`scx_nest`、`scx_pair`、`scx_prev`、`scx_qmap`、`scx_simple`、`scx_userland`

> [!DANGER]
> **`scx_nest` 是 C 示例，不是 Rust 调度器。** 很多中文文章把它列进「推荐调度器」，它是 `scx` 仓库里用来演示嵌套 sched_ext 的**教学代码**。
>
> 出处：`pkgs/os-specific/linux/scx/` `[核实·源码]`

#### 怎么选？（诚实的建议）

> [!WARNING]
> **`scx` 的收益是高度负载相关的，没有「万能最优」。** 我的建议顺序：
> 1. **先不动它。** 默认内核 + 默认 `scx` 关闭状态下，AMD 游戏表现已经很好。
> 2. 如果你**确实**遇到「帧生成时间不稳 / 一核有难多核围观 / 桌面在编译时卡到没法用」，再开 scx。
> 3. 开的时候先试 `scx_bpfland`（模块作者给的 example），再试 `scx_lavd`。
> 4. **用 `systemctl set-environment ..._OVERRIDE` 快速 A/B 对比**，别用「感觉」判断。
> 5. **务必保留退路**：如果开 scx 后系统卡死，在 bootloader 里选上一个 generation（scx 不在 initrd 里，所以救援模式一定能进）。

> [!NOTE]
> **`services.scx` 对 AMD 游戏的具体收益**：本文标注 `[未核实]` —— 我没有找到针对你这类配置的一手基准数据。任何声称「提升 X%」的说法都缺少可复现的测试条件。

#### 🔑 「Valve 做的游戏优化」在 scx 上的直接体现：`scx_lavd`

这一条值得单独说，因为它正面回答「**Valve 到底为 Linux 游戏做了什么调度层面的工作**」：

| 事实 | 内容 |
|---|---|
| `scx_lavd` 是什么 | **L**atency **A**ware **V**irtual **D**eadline 调度器 |
| 谁做的 | **Igalia 受 Valve 委托开发**（不是 Valve 内部，是 Valve 出钱的合同工作） |
| 动机 | **明确为 Steam Deck 的游戏负载设计** —— 在低功耗 AMD APU 上保证游戏帧生成的延迟稳定性 |
| 为什么对你相关 | 你是 **AMD 显卡 + AMD CPU**。Steam Deck 也是 AMD APU。**这是同一条技术路线** |

> 出处：Phoronix 2025-12 报道 `[媒体]`。上游代码在 `sched-ext/scx` 的 `scheds/rust/scx_lavd/` `[仓库]`

> [!TIP]
> **所以「Valve 制作的游戏优化」在 NixOS 上最直接的落点就是 `scx_lavd`。**
>
> ```nix
> services.scx = {
>   enable = true;
>   scheduler = "scx_lavd";
> };
> ```
>
> 但请务必先读下面的冲突警告。

#### ⚠️ 与 `scx` 互斥的东西（这一条很多人踩坑）

> [!DANGER]
> **`services.system76-scheduler` 与 `scx` 冲突。**
>
> `system76-scheduler` 的做法是**调整 CFS（传统内核调度器）的参数**（如 `sched_latency_ns`、nice 值）。而 `scx` 是**把 CFS 整体替换掉**。
>
> **结果：开了 scx 之后，`system76-scheduler` 的所有 CFS 调优都作用于一个已经不生效的调度器 —— 等于白装，甚至可能互相干扰。**
>
> **二选一，不要同时开。**

**其他与性能相关的服务（按需选，注意冲突）**：

| 服务 | 作用 | 备注 |
|---|---|---|
| `services.ananicy` | 按规则自动调进程 nice / ionice | 与 scx 无直接冲突，但效果会重叠 |
| `services.irqbalance` | 中断负载均衡 | 多核有帮助；现代内核的 IRQ affinity 已不错，收益有限 |
| `services.hardware.auto-cpufreq` | 动态调 CPU 频率/功耗 | ⚠️ **与 `power-profiles-daemon` 冲突** |
| `services.power-profiles-daemon` | 电源档位（GNOME/KDE 默认开） | ⚠️ 与 TLP / auto-cpufreq 互斥 |
| `services.thermald` | 温度管理 | ❌ **仅 Intel**，AMD 用户装了也没用 |

---

### 14.4 I/O 调度器：SSD 上收益接近 0，别浪费时间

**先说结论**：NVMe SSD 上现代内核的默认选择已经接近最优，**折腾 I/O 调度器在 SSD 上的收益基本测不出来**。只有 **机械硬盘（HDD）** 或「游戏装在 HDD 上」的场景，BFQ 才有明显意义。

#### 你的内核有哪些可用调度器

| 内核 | 可用调度器 |
|---|---|
| 默认 6.18 | `mq-deadline`、`kyber`、`none`（+ `bfq` 作为**模块**，需先加载） |
| `linux_zen` | 同上 + **`bfq` 内建**（`IOSCHED_BFQ=yes`） |

查看当前设备用的调度器：

```bash
cat /sys/block/nvme0n1/queue/scheduler
cat /sys/block/sda/queue/scheduler
# 方括号里的是当前生效的，例如：
# [none] mq-deadline kyber bfq
```

#### 推荐值（按设备类型）

| 设备 | 推荐 | 原因 |
|---|---|---|
| NVMe SSD | **`none`** | 设备自身队列足够深，内核调度反而增加开销 |
| SATA SSD | `mq-deadline` 或 `none` | 差异很小 |
| HDD（游戏装这里） | **`bfq`** | BFQ 的公平性明显改善「后台 IO 拖累前台游戏」 |
| 外接 USB 硬盘 | `bfq` | 同上 |

#### 怎么设：udev 规则（**源码级验证过的方法**）

NixOS 没有直接的 I/O 调度器选项，正确做法是用 `services.udev.extraRules`：

```nix
services.udev.extraRules = ''
  # 机械盘 / USB 盘用 BFQ（公平性优先）
  ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/rotational}=="1", ATTR{queue/scheduler}="bfq"
  # NVMe 用 none（最低开销）
  ACTION=="add|change", KERNEL=="nvme[0-9]*n[0-9]*", ATTR{queue/scheduler}="none"
  # 其余 SATA SSD 用 mq-deadline
  ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/rotational}=="0", ATTR{queue/scheduler}="mq-deadline"
'';
```

> 出处：`services.udev.extraRules` → 写入 `/etc/udev/rules.d/99-local.rules`，见 `nixos/modules/services/hardware/udev.nix:20-24,266` `[核实·源码]`

> [!DANGER]
> **`boot.kernelParams = [ "elevator=bfq" ]` 是一个「死参数」—— 已经完全无效。**
>
> 内核源码里这个参数的处理函数只剩下一句警告（`block/elevator.c`）：
>
> ```c
> static int __init elevator_setup(char *str)
> {
> 	pr_warn("Kernel parameter elevator= does not have any effect anymore.\n"
> 		"Please use sysfs to set IO scheduler for individual devices.\n");
> 	return 1;
> }
> ```
>
> **内核自己在告诉你「请用 sysfs 给单个设备设置 I/O 调度器」。** 也就是说：**网上所有教你写 `elevator=bfq` 的教程在 Linux 5.0+ 之后都是错的。**
>
> 出处：`torvalds/linux` `block/elevator.c:893-898` `[核实·源码]`
>
> **正确做法只有一个：udev 规则（或直接写 sysfs）—— 就是上面那段配置。**

---

### 14.5 GameMode：nixpkgs 原生模块，一个开关搞定

GameMode（Feral Interactive 出品）是**按需提升性能**的守护进程：游戏启动时通知它，它临时把 CPU governor 切到 performance、调进程优先级、可挂 GPU 性能档。**平时不玩游戏时不影响省电。**

```nix
programs.gamemode = {
  enable = true;        # 装 gamemode + 注册 systemd 用户服务

  enableRenice = true;  # 默认就是 true：给 gamemoded 加 cap_sys_nice 能力

  settings = {
    general = {
      renice = 10;
    };
    # ⚠️ GPU 部分见下面的 DANGER 警告
  };
};
```

**模块帮你自动做的事**（源码级）：

| 动作 | 说明 |
|---|---|
| `environment.systemPackages = [ pkgs.gamemode ]` | 装上 CLI 工具 |
| `etc."gamemode.ini".source = configFile` | 把你的 `settings` 写成 `/etc/gamemode.ini` |
| `security.polkit.enable = true` | 自动开 polkit（GPU 调节需要） |
| `security.wrappers.gamemoded` | 给 `gamemoded` 加 `cap_sys_nice+ep` —— 这样才能降 niceness |
| `systemd.user.services.gamemoded` | 用户级服务，**不需要 root 常驻** |
| `users.groups.gamemode` | 建组 |
| `systemd.packages = [ pkgs.gamemode ]` | 启用包自带的 unit |

> 出处：`nixos/modules/programs/gamemode.nix` `[核实·源码]`

> [!DANGER]
> **`gpu` 段有硬件风险 —— nixpkgs 源码自己写了警告。**
>
> nixpkgs 模块的 `settings` 示例里，GPU 部分带着这行注释：
> ```
> # Warning: GPU optimisations have the potential to damage hardware
> gpu = {
>   apply_gpu_optimisations = "accept-responsibility";
>   gpu_device = 0;
>   amd_performance_level = "high";
> };
> ```
> **`accept-responsibility` 这个值就是字面意思** —— 你要显式声明「出事自己负责」。它会把 AMD 显卡切到 high 性能档（等于自动超频/拉功耗墙）。
>
> **AMD 用户建议**：**不要开 gamemode 的 GPU 优化**，改用 §3.4 的 LACT 做精细、可控、可监控的频率/功耗管理。让 gamemode 只做 CPU 侧的事。

**用法**：

```bash
# 手动跑一个游戏
gamemoderun %command%

# 在 Steam 里：游戏 → 属性 → 启动选项
gamemoderun %command%
```

---

### 14.6 gamescope：什么时候值得用

gamescope 是 Valve 为 SteamOS 写的**微合成器**，在游戏和显示器之间插一层，提供：分辨率/帧率上限控制、FSR 升采样、HDR、多显示器独立游戏画面。

```nix
# 方式一：只装包（自己命令行调）
programs.gamescope = {
  enable = true;
  capSysNice = true;   # 默认 false。让 gamescope 能给自己提优先级
  args = [ ];          # 全局默认参数
  env = { };           # 全局默认环境变量
};

# 方式二：Steam 的 gamescope 会话（掌机 / HTPC 场景）
programs.steam.gamescopeSession = {
  enable = true;
  args = [ "-f" "--adaptive-sync" ];
  env = { };
  steamArgs = [ ];
};
```

**`programs.gamescope` 的完整选项**：`enable`、`package`、`capSysNice`（默认 `false`）、`args`、`env`。`[核实·源码]`

**`programs.steam.gamescopeSession` 的子选项**：`enable`、`args`、`env`、**`steamArgs`（默认 `[ "-tenfoot" "-pipewire-dmabuf" ]`）**。

> [!NOTE]
> `steamArgs` 的默认值很有信息量：**`-tenfoot`**（大屏/手柄 UI）+ **`-pipewire-dmabuf`**（用 PipeWire 做零拷贝屏幕捕获）。这两个正是 SteamOS 游戏模式的基石。
> 出处：`nixos/modules/programs/steam.nix:180-192` `[核实·源码]`

> [!NOTE]
> **`programs.gamescope` 这个模块是存在的**（`nixos/modules/programs/gamescope.nix`）。这一点值得强调，因为很多资料说「gamescope 在 NixOS 只有包没有模块」—— 那是旧信息。
>
> 另外，`programs.steam.enable = true` 时会自动执行 `programs.gamescope.enable = lib.mkDefault cfg.gamescopeSession.enable;` —— 即**只有你开了 gamescopeSession，它才默认开 gamescope**。`[核实·源码]`

**什么时候真的需要 gamescope？**

| 场景 | 需要吗 |
|---|---|
| 普通桌面 + 单个游戏 | ❌ 不需要，直接跑 |
| 掌机 / 客厅 HTPC（要游戏模式 UI） | ✅ **需要** |
| 游戏不支持你的分辨率/宽高比 | ✅ 有用（可用它虚拟一个分辨率） |
| 想要 FSR 升采样（低分辨率渲染 + 高质量放大） | ✅ 有用 |
| 想要给游戏限帧（省电、稳帧） | ✅ 有用 |
| 想要 HDR | ⚠️ 取决于显示器与游戏，链路较复杂 |

> [!WARNING]
> **gamescope 不是「性能增强器」。** 它是**合成器** —— 多一层合成**理论上增加延迟**。它解决的是「分辨率/帧率/HDR/多显示器控制」问题，不是「让帧数变高」。在普通桌面上无脑开 gamescope 通常**降低**体验。

---

### 14.7 Valve 做的优化：你真正该关注的部分

这是 P0 优先级的内容。

#### 14.7.1 Proton 版本选择

**Proton 是 Valve 的 Wine 分支，是「Windows 游戏能不能在 Linux 跑」的决定性因素。** 换 Proton 版本的收益远超换内核。

```nix
programs.steam = {
  enable = true;

  # 挂载额外的兼容层工具 —— 这样 Steam 的「兼容性」下拉菜单里会出现它们
  extraCompatPackages = with pkgs; [
    proton-ge-bin      # Proton-GE（社区增强版，修了很多游戏）
  ];
};
```

| 包 | 26.05 状态 | 说明 |
|---|---|---|
| `pkgs.proton-ge-bin` | ✅ **存在** | Proton-GE，GE-Proton 系列。**装它** |
| `pkgs.proton-ge-custom` | ❌ 404 | 老名字，已不存在 |

> 出处：`pkgs/by-name/pr/proton-ge-bin/package.nix` `[核实·源码]`

> [!TIP]
> **`extraCompatPackages` 的作用是「让 Steam 认得这个兼容层」**，然后你在**每个游戏**的「属性 → 兼容性 → 强制使用特定 Steam Play 兼容性工具」里选它。**不是全局生效** —— 这点很多人搞错。逐个游戏试，哪个跑得好用哪个。

#### 14.7.2 `programs.steam` 的完整实用选项

| 选项 | 默认 | 用途 |
|---|---|---|
| `enable` | `false` | 开关 |
| `package` | `pkgs.steam` | 可换 `steamSmall` 等变体 |
| `extraPackages` | `[ ]` | 塞进 Steam 运行环境的额外包 |
| `extraCompatPackages` | `[ ]` | **额外兼容层（放 proton-ge-bin）** |
| `fontPackages` | `[ ]` | 中文字体 —— **对中文用户很重要，见下** |
| `remotePlay.openFirewall` | `false` | 远程同乐端口 |
| `dedicatedServer.openFirewall` | `false` | 专用服务器端口 |
| `localNetworkGameTransfers.openFirewall` | `false` | 局域网游戏传输端口 |
| `gamescopeSession.*` | — | 见 §14.6 |
| `extest.enable` | `false` | **Wayland 下用 Steam Input 需要它**（X11 输入事件 → uinput 转换） |
| `protontricks.enable` | `false` | 装上 protontricks（Wine 组件管理） |

> [!IMPORTANT]
> **中文用户必看：`fontPackages`。**
>
> Steam 自己的界面和部分游戏在 Linux 下**可能显示方块**（缺中日韩字体）。Steam 运行在它自己的 FHS 环境里，**看不到你 `fonts.packages` 装的字体**。正确做法是把字体塞进 Steam 环境：
>
> ```nix
> programs.steam.fontPackages = with pkgs; [
>   noto-fonts-cjk-sans
>   noto-fonts-color-emoji
> ];
> ```
>
> 出处：`nixos/modules/programs/steam.nix:121-133,212` `[核实·源码]`

#### 14.7.3 `programs.steam.enable` 顺带帮你做的事（一个重要的连锁反应）

源码里 `programs.steam.enable = true` 会**强制**（不是 `mkDefault`）设置：

```nix
hardware.graphics = {
  enable = true;        # ← 硬赋值，不是 mkDefault
  enable32Bit = true;
};
hardware.steam-hardware.enable = true;   # Steam 手柄等设备的 udev 规则
services.pulseaudio.support32Bit = config.services.pulseaudio.enable;
services.pipewire.alsa.support32Bit = config.services.pipewire.alsa.enable;
```

> 出处：`nixos/modules/programs/steam.nix:206-220` `[核实·源码]`

> [!WARNING]
> **这里有一个真实的配置冲突陷阱：**
>
> 因为 Steam 模块是**硬赋值** `hardware.graphics.enable = true`，如果你在别处写 `hardware.graphics.enable = false`，**会直接构建报错（option conflict）**。
>
> 反过来，**你自己写 `hardware.graphics.enable = true` 是安全的**（同值不冲突）。所以 §3.1 的建议仍然成立：**显式写它**，既让配置自解释，也不会和 Steam 打架。
>
> 另外注意：**Steam 会自动把 32 位图形驱动打开** —— 这意味着即使你忘了写 `enable32Bit`，只要开了 Steam 也能跑 32 位游戏。但**别依赖这个副作用**，因为一旦你哪天禁用 Steam，32 位游戏会突然全挂。

#### 14.7.4 SteamOS 上那些「Valve 做的优化」在 NixOS 上还剩什么

| SteamOS 特性 | NixOS 26.05 对应 | 说明 |
|---|---|---|
| **Proton** | ✅ `programs.steam` + `extraCompatPackages` | 完全可用 |
| **gamescope** | ✅ `programs.gamescope` 模块 | 完全可用 |
| **GameMode** | ✅ `programs.gamemode` 模块 | 完全可用 |
| **Fsync / esync** | ✅ Proton 内置，无需配置 | 靠内核 futex 支持 |
| **ntsync** | ⚠️ **需换 `linux_zen`** | 默认内核未启用 `NTSYNC`（见 §14.2） |
| **HDR** | ⚠️ 可用但链路复杂 | 需要 gamescope + 支持的显示器 + 游戏 |
| **VRS / FSR** | ✅ gamescope 提供 | |
| **SteamOS 的「游戏模式」UI** | ⚠️ `gamescopeSession` 近似，但不等同 | SteamOS 的 Gaming Mode 是深度定制的 |
| **只读根 + 原子更新** | ✅ NixOS 做得更彻底 | 这是 NixOS 的强项 |
| **SteamOS 的 TDP 控制** | ❌ 无对应 | 那是掌机专用硬件接口 |

> [!NOTE]
> **诚实结论**：Valve 在 SteamOS 上做的大部分「游戏优化」其实是**上游 Linux 的共同成果**（Proton、gamescope、GameMode、fsync 都是开源且发行版无关的）。**NixOS 能拿到其中绝大部分**。真正拿不到的是掌机硬件相关的部分（TDP 限制、定制 UI、深度内核补丁）。
>
> **补一句**：Valve 还通过**资助 Igalia 开发 `scx_lavd` 调度器**直接影响上游（见 §14.3）。这类贡献是发行版无关的 —— 你在 NixOS 上一样能拿到。

#### 14.7.5 ntsync 怎么用（如果你换了 `linux_zen`）

`ntsync` 是内核级的 Windows NT 同步原语模拟。**只有 `linux_zen` 的编译配置里开了 `NTSYNC=yes`**（默认内核没有，见 §14.2）。

**前提**：`boot.kernelPackages = pkgs.linuxPackages_zen;`

```nix
# 1. 加载内核模块
boot.kernelModules = [ "ntsync" ];

# 2. 给内核 ntsync 设备合适的权限（Proton 需要访问 /dev/ntsync）
services.udev.extraRules = ''
  KERNEL=="ntsync", MODE="0666"
'';
```

```bash
# 3. 让 Proton 用 ntsync（Steam 启动选项）
WINENTSYNC=1 PROTON_USE_NTSYNC=1 %command%
```

> [!WARNING]
> **`WINENTSYNC` / `PROTON_USE_NTSYNC` 这两个环境变量名来自社区（Proton-GE 与 Proton 的 issue 讨论），我没有从 Proton 官方文档确认**，标注 `[社区]` / `[未核实]`。
>
> **更稳的做法**：装上 `proton-ge-bin`（§14.7.1），在 Steam 的兼容性菜单里选 Proton-GE，它对新特性（包括 ntsync）的支持通常更及时。
>
> **验证 ntsync 是否真的在工作**：
> ```bash
> ls -l /dev/ntsync              # 设备存在吗
> lsmod | grep ntsync            # 模块加载了吗
> dmesg | grep -i ntsync         # 有没有报错
> ```
> 注意：**ntsync 是「可能被用到」，不是「一定被用到」** —— 需要 Proton 显式启用。如果 `/dev/ntsync` 存在但游戏没变快，说明 Proton 没走这条路，这不是配置错误。

---

### 14.8 zram：被低估的「消除卡顿」手段

如果你的内存是 16GB 或更少，**zram 的收益可能大于本章其他所有优化之和**。它把一部分内存压缩后当 swap 用，避免「内存压力导致的大卡顿」。

```nix
zramSwap = {
  enable = true;          # 默认 false
  algorithm = "zstd";     # 默认 zstd
  memoryPercent = 50;     # 默认 50（最多用 50% 内存做压缩池）
  swapDevices = 1;        # 默认 1
  priority = 5;           # 默认 5
};
```

> 出处：`nixos/modules/config/zram.nix:30-110` `[核实·源码]`

| 选项 | 默认 | 建议 |
|---|---|---|
| `enable` | `false` | 内存 ≤16GB：**开** |
| `algorithm` | `"zstd"` | 保持（也可选 `lz4`，更快但压缩率低） |
| `memoryPercent` | `50` | 保持 |
| `swapDevices` | `1` | 保持 |
| `priority` | `5` | 保持 |

> [!NOTE]
> **26.05 新增了另外两个 zram 相关模块**（`services/system/zram-generator.nix`、`system/boot/zram-as-tmp.nix`）。`zram-as-tmp` 把 `/tmp` 放内存里，对编译/游戏临时文件有帮助，但**会占用内存**，内存紧张时反而有害。`[核实·源码]`

---

### 14.9 sysctl、电源与 CPU governor

#### CPU governor

**默认是 `schedutil`**（源码：`CPU_FREQ_DEFAULT_GOV_SCHEDUTIL = yes`）。`schedutil` 是内核自带的、与调度器协同的频率调节器，**桌面场景下它通常比 `performance` 更好**（响应快且省电）。

**NixOS 的选项（源码级）**：

| 选项 | 类型 | 默认 |
|---|---|---|
| `powerManagement.cpuFreqGovernor` | `nullOr str` | **`null`**（= 不干预，用内核默认 `schedutil`） |
| `powerManagement.cpufreq.max` | int | `null` |
| `powerManagement.cpufreq.min` | int | `null` |

```nix
powerManagement.cpuFreqGovernor = "schedutil";  # 桌面推荐值（也可保持默认不写）
```

> [!DANGER]
> **不要用 `powerManagement.cpuFreqGovernor = "performance"` 当作「游戏优化」。**
>
> 它会让 CPU 永远跑在最高频，**发热增加 → 更容易撞温度墙降频 → 帧数反而更不稳**。`linux_xanmod` 强制了 performance governor，这是它的编译期特性，但**不代表对你更好**。
>
> **想要「游戏时性能、平时省电」的正确做法**是：
> 1. 保持 `schedutil`（或 `powersave`）
> 2. 用 **`programs.gamemode`**（§14.5）在游戏启动时临时切换 —— 这是**按需**的，而不是永久
> 3. 或者用 **EPP（Energy Performance Preference）** 做更精细的控制（见下）

#### EPP（Energy Performance Preference）—— 比 governor 更现代

**NixOS 没有原生的 EPP 选项。** 需要用 `systemd.tmpfiles` 或 udev 写 sysfs：

```bash
# 先看看支持哪些值
cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference
# performance / balance_performance / balance_power / power
```

```nix
# 声明式写 EPP（用 systemd.tmpfiles 在启动时写）
systemd.tmpfiles.rules = [
  "w /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference - - - - balance_performance"
];
# 注意：这只写了 cpu0，多核需要展开或用脚本
```

> [!NOTE]
> **`amd_pstate` 驱动下 EPP 才可用。** 见下一节确认你的模式是 `active`。
> 这条写法标注 `[部分未核实]` —— `systemd.tmpfiles` 写 sysfs 在启动时序上可能早于 `amd_pstate` 初始化，**建议用 udev 规则或 systemd 服务在 `multi-user.target` 后写**。

#### `amd_pstate`

AMD 现代 CPU（Zen 2+）用 `amd_pstate` 驱动。**内核 Kconfig 的默认值已经是 `active` 模式**，所以：

```nix
# ❌ 不需要 —— 这已经是默认值
# boot.kernelParams = [ "amd_pstate=active" ];
```

> [!NOTE]
> 网上大量 AMD 优化教程让你加 `amd_pstate=active`。**在 6.18 内核上这是冗余的。** 验证当前模式：
> ```bash
> cat /sys/devices/system/cpu/amd_pstate/status
> # active / passive / guided
> ```
> 只有当你**确实**看到不是 `active` 时才需要显式设置。`[核实·源码]`（内核 Kconfig 默认值）

#### `split_lock_mitigate=0` —— 一个真实有效但**有争议**的参数

Intel 在 2019 年引入了 split lock 检测，默认开启时**会让触发 split lock 的程序被强制降速 1000 倍以上**（俗称 "misery mode"）。某些游戏（尤其老游戏、反作弊组件）会触发它。

```nix
# ⚠️ 关闭 split lock 检测 —— 有安全/公平性代价
boot.kernelParams = [ "split_lock_mitigate=0" ];
```

| 收益 | 代价 |
|---|---|
| 消除某些游戏的「间歇性卡成幻灯片」 | 失去对恶意/劣质程序的 split lock 防护 |
| 对不触发 split lock 的程序**零影响** | 在共享机器上可能被一个程序拖慢整体 |

> 出处：`[Wiki]` NixOS Wiki 与 Arch Wiki 的 gaming 页面均有此建议 `[社区]`
>
> **建议**：**先不要加。** 只有当你在**特定游戏**里观察到「帧时间突然暴涨到几十毫秒、且与场景无关」时，才加它做 A/B 对比。不要无脑抄。

#### sysctl：先知道 NixOS **已经**帮你设了什么

**重要**：NixOS 已经在 `nixos/modules/config/sysctl.nix` 里设了一批**比传统发行版更激进**的默认值：

| 参数 | NixOS 26.05 默认 | 说明 |
|---|---|---|
| `vm.max_map_count` | **`1048576`**（`mkDefault`） | ⚠️ **很多「游戏优化教程」教你把 `vm.max_map_count` 调到 262144 或更高 —— NixOS 已经是 1048576，是它们的 4 倍。不用调** |
| `fs.inotify.max_user_instances` | **`524288`**（`mkDefault`） | 传统默认是 8192 |
| `fs.inotify.max_user_watches` | **`524288`**（`mkDefault`） | 传统默认是 8192 |

> 出处：`nixos/modules/config/sysctl.nix:114-120` `[核实·源码]`

> [!IMPORTANT]
> **所以下面这些常见「游戏 sysctl 优化」在 NixOS 上是多余的：**
>
> - ❌ `vm.max_map_count = 2147483642`（抄 SteamOS）—— NixOS 已是 1048576，对 Proton 足够
> - ❌ `fs.inotify.max_user_watches = 524288` —— **已经是这个值**
> - ❌ `vm.swappiness = 1` —— 见下
>
> **先 `sysctl -a | grep 你想改的项` 看当前值，再决定要不要改。**

**真正可能需要调的**：

```nix
boot.kernel.sysctl = {
  # 有 zram 时别设太低（太低会在内存压力下触发 OOM）
  "vm.swappiness" = 10;
  # 桌面交互性
  "vm.vfs_cache_pressure" = 50;
  # 网络缓冲（大文件传输/高带宽）
  "net.core.rmem_max" = 16777216;
  "net.core.wmem_max" = 16777216;
};
```

> [!WARNING]
> **`vm.swappiness = 1` 这类「优化」是反优化的**：它会让内核几乎不用 swap，在内存压力下**直接触发 OOM killer 杀进程**。有 zram 时 `swappiness` 保持默认（60）或 10–20 更合理。

---

### 14.9.1 MangoHud / vkBasalt：**NixOS 没有模块，但有包**

> [!WARNING]
> **`programs.mangohud` 这个选项在 NixOS 里不存在。** 很多教程写 `programs.mangohud.enable = true`，那**是 Home Manager 的选项**，不是 NixOS 的。
>
> NixOS 侧只有**包**：`pkgs.mangohud`、`pkgs.goverlay`、`pkgs.vkbasalt`。`[核实·源码]`

**MangoHud** 是显示帧数/帧时间/温度/频率的覆盖层。**对调优至关重要 —— 没有它你无法做 A/B 对比。**

```nix
# 装包
environment.systemPackages = with pkgs; [
  mangohud
  goverlay     # GUI 配置工具
];

# 用法 1：单个游戏（Steam 启动选项）
#   mangohud %command%

# 用法 2：全局给 Steam 里的所有游戏开（通过 override 注入环境变量）
programs.steam.package = pkgs.steam.override {
  extraEnv = {
    MANGOHUD = "1";
    MANGOHUD_CONFIG = "fps,frametime,cpu_temp,gpu_temp,gpu_fan,cpu_power,gpu_power";
  };
};
```

| 工具 | 作用 |
|---|---|
| **MangoHud** | 帧数 / **帧时间曲线** / 温度 / 功耗 / 频率覆盖层 |
| **vkBasalt** | 后处理（CAS 锐化、SMAA）—— 对 AMD 有用 |
| **goverlay** | MangoHud / vkBasalt 的图形化配置器 |

> [!TIP]
> **调优必须有数据。** 用 MangoHud 看 **frametime graph（帧时间曲线）**，不要只看平均帧 —— 平均帧会完全掩盖卡顿。
>
> 做 A/B 对比时（比如对比 scx 开关、对比内核），固定同一个游戏场景、同一段时长，看**帧时间曲线的毛刺**和 **1% low**，不要靠「感觉」。

---

### 14.10 「不要做」清单（反优化）

按用户要求，我把**明确有害或无收益**的常见做法列出来：

| 做法 | 为什么别做 |
|---|---|
| ❌ 换 `linux_cachyos` | **nixpkgs 里不存在这个包**，写了会报错 |
| ❌ 用 `linux_lqx` / `linux_libre` / `linux_hardened` / `linux-rt` | **26.05 已全部移除**，会 `throw` |
| ❌ `services.xserver.videoDrivers = [ "amdgpu" ]` | 现代 AMD 应保持默认 `modesetting`（§3.1） |
| ❌ `powerManagement.cpuFreqGovernor = "performance"` | 更热、更易降频，帧数更不稳 |
| ❌ `boot.kernelParams = [ "amd_pstate=active" ]` | 已是默认值，冗余 |
| ❌ `vm.swappiness = 1` | 内存压力下触发 OOM |
| ❌ 在 SSD 上折腾 I/O 调度器 | 收益测不出来 |
| ❌ 无脑开 gamescope | 它是合成器，普通桌面场景**增加**延迟 |
| ❌ 开 GameMode 的 `gpu.apply_gpu_optimisations` | 源码自带硬件风险警告，改用 LACT |
| ❌ 用 `services.scx` 却不做 A/B 测试 | 收益负载相关，靠「感觉」判断必然误判 |
| ❌ **同时开 `services.scx` 和 `services.system76-scheduler`** | scx 替换了 CFS，后者的 CFS 调优全部失效。**二选一** |
| ❌ `boot.kernelParams = [ "elevator=bfq" ]` | **内核已明确废弃**（`block/elevator.c` 只剩警告）。用 udev 规则 |
| ❌ 调 `vm.max_map_count` | **NixOS 默认已是 1048576**，抄 SteamOS 的值没有意义 |
| ❌ 调 `fs.inotify.max_user_watches` | **NixOS 默认已是 524288** |
| ❌ 无脑加 `split_lock_mitigate=0` | 有代价。只在特定游戏卡顿时做 A/B |
| ❌ `programs.mangohud.enable` | **NixOS 没这个选项**（那是 Home Manager 的）。用 `pkgs.mangohud` |
| ❌ `LIBVA_DRIVER_NAME=radeonsi` | 不必要（§3.2） |
| ❌ 为了 ntsync 专门换 zen | 目前 Proton 默认不走 ntsync，收益不确定 |

---

## 十五、语言工具链与编译依赖（npm / bun / pnpm / uv / Python / Rust / Go / TS）

> 这一章解决一个高频困惑：**「我到底该用 nixpkgs 的包，还是用官方的包管理器（npm / uv / pip / rustup）？」**
>
> 答案不是二选一，而是**三层策略**。

### 15.1 三层策略：先想清楚你要哪一种

| 层 | 做法 | 适合 | 优点 | 缺点 |
|---|---|---|---|---|
| **L1 系统包** | `environment.systemPackages = [ pkgs.nodejs ]` | 全局工具、长期使用 | 声明式、可回滚、纯 | 版本跟 nixpkgs 走，不能随手切版本 |
| **L2 项目环境** | `devShell` / `nix develop` / direnv | **项目开发（首选）** | 每个项目独立版本、可复现、进 git | 需要写 `shell.nix` / `flake.nix` |
| **L3 官方包管理器** | `npm i -g` / `uv tool install` / `pip install` | 临时试、生态里 nixpkgs 没有的东西 | 和全世界文档一致 | **不受 NixOS 管理**，升级/回滚不受控 |

> [!IMPORTANT]
> **推荐决策顺序：L2 → L1 → L3。**
>
> - **写项目** → L2（`devShell`）。这是 NixOS 最舒服的用法。
> - **装全局工具** → L1（`environment.systemPackages` 或 Home Manager `home.packages`）。
> - **只有 nixpkgs 没有、或只是临时试** → L3。
>
> **L3 是逃生舱，不是主路径。** 用 L3 装的东西**不会出现在你的 `configuration.nix` 里**，换机器时不会自动回来，出问题也无法 `nixos-rebuild rollback`。

---

### 15.2 26.05 语言工具链版本对照表（已核实）

| 工具 | 属性名 | 26.05 版本 / 状态 | 证据 |
|---|---|---|---|
| **Node.js** | `pkgs.nodejs` | **24 LTS**（默认，22→24 升级） | `[核实·源码]` `[官方]` |
| Node.js 22 | `pkgs.nodejs_22` | ✅ 存在 | `[核实·源码]` |
| Node.js 26 | `pkgs.nodejs_26` | ✅ 存在 | `[核实·源码]` |
| Node.js 最新 | `pkgs.nodejs_latest` | = `nodejs_26` | `[官方]` release notes:443 |
| **`nodePackages`** | — | ❌ **已整体删除** | `[官方]` release notes:117 |
| `corepack_latest` | — | ❌ **已删除** | `[官方]` release notes:144 |
| **Python** | `pkgs.python3` | **3.13** | `[核实·源码]` |
| Python 3.14 | `pkgs.python314` | ✅ 存在 | `[核实·源码]` |
| **uv** | `pkgs.uv` | **0.11.21** | `[核实·源码]` |
| **bun** | `pkgs.bun` | **1.3.13** | `[核实·源码]` |
| **deno** | `pkgs.deno` | **2.8.3** | `[核实·源码]` |
| **TypeScript** | `pkgs.typescript` | ✅ 存在 | `[核实·源码]` |
| **tsx** | `pkgs.tsx` | ✅ 存在 | `[核实·源码]` |
| `ts-node` | — | ❌ **不存在**（404） | `[核实·源码]` |
| **esbuild** | `pkgs.esbuild` | ✅ 存在 | `[核实·源码]` |
| `swc-core` | — | ❌ 不存在（404） | `[核实·源码]` |
| **mise** | `pkgs.mise` | ✅ 存在 | `[核实·源码]` |
| **devenv** | `pkgs.devenv` | ✅ 存在 | `[核实·源码]` |
| **ruff** | `pkgs.ruff` | ✅ 存在 | `[核实·源码]` |
| **Rust** | `pkgs.cargo` / `pkgs.rustc` | ✅ 存在（非 by-name 路径） | `[核实·源码]` |
| **Go** | `pkgs.go` | ✅ 存在（非 by-name 路径） | `[核实·源码]` |
| **`pnpm`** | `pkgs.pnpm` | **`= pnpm_11`**（`all-packages.nix:2967`；另有 `pnpm_8/9/10/10_29_2/10_latest/12`） | `[核实·源码]` |
| **`yarn`** | `pkgs.yarn` | ✅ 存在（**by-name：`pkgs/by-name/ya/yarn/package.nix`**；另有 `yarn-berry` / `yarn-zpm` / `yarn-bash-completion`） | `[核实·源码]` |
| **`rustup`** | `pkgs.rustup` | ✅ 存在（`all-packages.nix:4396` → `../development/tools/rust/rustup`） | `[核实·源码]` |

> [!DANGER]
> **两个必须知道的破坏性变更（26.05）：**
>
> 1. **`pkgs.nodePackages.*` 已整体删除。** 老配置里 `pkgs.nodePackages.typescript`、`pkgs.nodePackages.prettier` 之类**全部失效**。官方迁移指引：*"please use the top-level packages instead (i.e `pkgs.package-name` instead of `pkgs.nodePackages.package-name`)."*
>    出处：`[官方]` `doc/release-notes/rl-2605.section.md:117-121`
>
> 2. **`nodejs` 默认从 22 LTS 升到 24 LTS。** 有破坏性变更，见 Node 官方 v22→v24 迁移文档。
>    出处：`[官方]` release notes:47
>
> 另外：**`nodejs-slim` 不再提供 `corepack` 可执行文件**（移到单独的 output），要用得显式引用 `nodejs-slim.corepack`。release notes:445 `[官方]`

---

### 15.3 Node.js 生态：npm 全局安装的正确姿势

#### 15.3.1 全局装一个 CLI 工具（如 `@openai/codex`）

**做法 A（推荐，L1）：nixpkgs 里有就用 nixpkgs**

```nix
environment.systemPackages = with pkgs; [
  nodejs_24
  # 如果 nixpkgs 有这个工具就直接用
];
```

**做法 B（L2，项目内）：`devShell`**

```nix
# shell.nix
{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  packages = [
    pkgs.nodejs_24
    pkgs.typescript
    pkgs.tsx
    pkgs.esbuild
  ];
  shellHook = ''
    echo "node $(node -v) / npm $(npm -v)"
  '';
}
```

**做法 C（L3）：用户级 npm 全局安装 —— 不碰 root**

> [!IMPORTANT]
> **`npm install -g` 在 NixOS 上会失败（`EACCES` / 只读文件系统）。** 这是**设计如此**，不是 bug。
>
> 因为 `/nix/store` 是只读的，而系统级 `node` 的全局 `node_modules` 指向 store。
>
> **正确做法：用用户级前缀。**

```bash
# 一次性设置：把 npm 全局前缀指到你家目录
npm config set prefix ~/.npm-global
export PATH="$HOME/.npm-global/bin:$PATH"   # 加进 ~/.bashrc

# 之后就能正常全局装了，完全不需要 sudo
npm install -g @openai/codex
```

```nix
# 但更 NixOS 的做法：让 NixOS 帮你管 PATH
# 在 configuration.nix（或 Home Manager）里：
environment.sessionVariables = {
  PATH = [ "$HOME/.npm-global/bin" ];   # 注意：这会覆盖而非追加，见下方警告
};
```

> [!WARNING]
> **不要用 `environment.sessionVariables.PATH` 覆盖 PATH。** NixOS 的 `PATH` 由模块系统管理，硬写会**破坏系统 PATH**（命令全找不到）。
>
> 正确做法是改 shell 的 rc 文件（用户级），或用 Home Manager 的 `home.sessionPath`：
> ```nix
> # Home Manager
> home.sessionPath = [ "$HOME/.npm-global/bin" ];
> ```
> 或者直接写进 `~/.bashrc` / `~/.zshrc`（简单直接，但不受 NixOS 管理）。

#### 15.3.2 `npx` —— 临时跑一个 npm 包

`npx` 需要一个可写的缓存目录。在 NixOS 上通常能直接工作（缓存在 `~/.npm/_npx`），但**首次运行会下载**。

> [!WARNING]
> **`npx` 在 NixOS 上的可靠性问题**（详见 §16.1）：`npx some-package` 下载的包是**动态链接到宿主 glibc 的预编译二进制**，在 NixOS 上**可能因找不到动态链接器而失败**。如果失败，用 `nix-ld` 兜底（§15.8）。

#### 15.3.3 corepack / pnpm / yarn

```bash
# nodejs 自带 corepack（注意：nodejs-slim 不自带）
corepack enable
corepack prepare pnpm@latest --activate
```

> [!NOTE]
> `corepack_latest` 这个属性在 26.05 已删除（Corepack 不再随 Node.js 分发）。用 `nodejs`（完整版）自带的 corepack，或 `pkgs.pnpm`。

**三条路径的确切属性（已逐个核实，不再存疑）**：

| 工具 | nixpkgs 属性 | 落点 | 备注 |
|---|---|---|---|
| `pnpm` | **`pkgs.pnpm`** | `all-packages.nix:2967` → `pnpm = pnpm_11;` | by-name 下**没有** `pnpm`（`pkgs/by-name/pn/` 只有 `pnpm-fixup-state-db` / `pnpm-shell-completion` / `pnpmBuildHook`）；可用版本 `pnpm_8` / `pnpm_9` / `pnpm_10` / `pnpm_10_29_2` / `pnpm_10_latest` / `pnpm_11` / `pnpm_12` |
| `yarn` | **`pkgs.yarn`** | **`pkgs/by-name/ya/yarn/package.nix`**（by-name 命中） | 同目录还有 `yarn-berry`（`yarn-berry_3` / `yarn-berry_4`）、`yarn-zpm`、`yarn-lock-converter` |
| `rustup` | **`pkgs.rustup`** | `all-packages.nix:4396` → `../development/tools/rust/rustup` | by-name 下**没有**（`pkgs/by-name/ru/` 无 `rustup`） |

> 出处：`pkgs/top-level/all-packages.nix:2967,4396`、`pkgs/by-name/ya/yarn/package.nix`、`pkgs/by-name/pn/` 目录列表 `[核实·源码]`

**怎么选**：
- 项目要「锁 pnpm/yarn 版本」→ 用 `pkgs.pnpm_10` / `pkgs.yarn-berry_4` 这类**带版本后缀**的属性（可复现）；
- 只想「能跑就行」→ 用 corepack（`nodejs` 自带），但 corepack 下载的 pnpm/yarn 落在 `~/.cache/node/corepack`，**不受 NixOS 管理**；
- ⚠️ **不要混用**：corepack 激活的 pnpm 与 `pkgs.pnpm` 是两个不同来源，`which pnpm` 的解析结果取决于 PATH 顺序。

---

### 15.4 Python：`python313` 是默认，`uv` 是答案

#### 15.4.1 不要 `pip install` 到系统

```bash
pip install requests
# error: externally-managed-environment
```

这是 PEP 668 的**正确行为**。三种解法：

```nix
# 解法 1（推荐）：项目用 devShell，包用 python3.withPackages
{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  packages = [
    (pkgs.python313.withPackages (ps: with ps; [
      requests
      numpy
      pandas
    ]))
  ];
}
```

```nix
# 解法 2：临时用 nix-shell
# nix-shell -p "python3.withPackages(ps: [ps.requests])"
```

```bash
# 解法 3（L3）：venv —— 在项目目录里
python3 -m venv .venv
source .venv/bin/activate
pip install requests        # venv 里可以装
```

> [!TIP]
> **`uv` 是 2026 年最值得换的 Python 工具链。** `pkgs.uv` 版本 **0.11.21**，它比 pip 快一到两个数量级，并且能管理 Python 版本本身：
> ```bash
> # 装一个 CLI 工具（隔离环境，类似 pipx）
> uv tool install ruff
> uv tool install hermes-agent    # 如果它在 PyPI 上
>
> # 项目内
> uv init && uv add requests && uv run python main.py
>
> # 用指定 Python 版本
> uv python install 3.12
> uv venv --python 3.12
> ```
> `uv tool install` 装到 `~/.local/share/uv/tools/`，**完全在用户目录，不需要 root** —— 这正好符合本文第九章的「非 root 部署」原则。

#### 15.4.2 26.05 的 Python 破坏性变更

| 变更 | 说明 | 出处 |
|---|---|---|
| `buildPythonPackage` / `buildPythonApplication` 遇到 `pytestFlagsArray` 会**直接报错** | 以前是警告，现在是硬错误 | release notes:237 `[官方]` |
| `pygame` 重命名为 `pygame-original` | 3.14 起 `pygame` 默认指向 `pygame-ce` | release notes:241 `[官方]` |
| `gradio` 升到 6.0 | 有迁移指引 | release notes:249 `[官方]` |
| `pikepdf` 默认不再带 mupdf 支持 | 需要时 `withMupdf = true` | release notes:251 `[官方]` |

---

### 15.5 Rust：`rustup` 还是 nixpkgs？

| 方式 | 适用 | 说明 |
|---|---|---|
| `pkgs.cargo` + `pkgs.rustc` | 用系统稳定版 | 简单，但**只能装一个版本** |
| **`pkgs.rustPlatform` / `devShell`** | 项目开发（推荐） | 可指定工具链，与 `cargo build` 配合 |
| `rustup` | 需要频繁切 toolchain | ⚠️ `rustup` 装的东西在 `~/.rustup`，**不受 NixOS 管理** |

```nix
# shell.nix：项目用稳定版工具链
{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  packages = with pkgs; [
    cargo
    rustc
    rustfmt
    clippy
    pkg-config      # 编译依赖的关键，见 §15.8
    openssl         # 若依赖 openssl
  ];
}
```

> [!NOTE]
> **`pkgs.rustup` 的属性路径已核实**：`pkgs/top-level/all-packages.nix:4396` → `rustup = callPackage ../development/tools/rust/rustup { };`。它在 **by-name 下确实 404**（`pkgs/by-name/ru/` 里没有它），但**属性名 `pkgs.rustup` 是有效的**，可以直接写进 `environment.systemPackages`。`[核实·源码]`

> [!TIP]
> **Rust 项目在 NixOS 上最常见的坑**：`cargo build` 找不到 `cc` / `pkg-config` / `openssl`。
> **解决**：把 `pkg-config` 和对应的 `-dev` 库加进 `devShell`。Rust 的 `-sys` crate 靠 `pkg-config` 找库。

---

### 15.6 Go

```nix
{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  packages = with pkgs; [ go gopls gotools ];
}
```

> [!WARNING]
> **Go 的 `GOPATH` / 模块缓存默认在 `~/go`**，这个可以正常写（不是只读的）。但：
>
> **`go install` 装出来的二进制在 `~/go/bin`**，需要把它加进 PATH（同 §15.3.1 的 PATH 警告，别用 `environment.sessionVariables.PATH` 硬覆盖）。
>
> 另外：Go 编译时如果需要 cgo，**同样会遇到 `cc` / `pkg-config` 问题**（同 Rust）。

---

### 15.7 TypeScript

```nix
{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  packages = with pkgs; [
    nodejs_24
    typescript     # 提供 tsc
    tsx            # 直接跑 .ts（替代已消失的 ts-node）
    esbuild        # 极快的打包/转译
  ];
}
```

| 工具 | 26.05 | 备注 |
|---|---|---|
| `tsc` | ✅ `pkgs.typescript` | 官方编译器 |
| `tsx` | ✅ `pkgs.tsx` | **替代 `ts-node`** |
| `ts-node` | ❌ 404 | **不在 nixpkgs 里** |
| `esbuild` | ✅ `pkgs.esbuild` | 打包器 |

> [!NOTE]
> **`ts-node` 不在 nixpkgs。** 需要它的话用 `npm i -D ts-node` 装到项目里（局部安装是安全的，写进项目 `node_modules`），或改用 `tsx`。

---

### 15.8 编译依赖：这是 NixOS 新手最容易卡住的地方

**根因**：NixOS **没有 FHS**，所以「先装个 `-dev` 包，然后 `./configure` 就能找到」这套流程**不成立**。

#### 15.8.1 症状 → 原因 → 解法 对照表

| 症状 | 原因 | 解法 |
|---|---|---|
| `fatal error: openssl/ssl.h: No such file or directory` | 缺头文件（nixpkgs 里头文件和库**在同一个包**，不像 Debian 的 `-dev`） | `devShell` 里加 `openssl` |
| `Package 'foo' not found` (pkg-config) | 缺 `pkg-config` 本身，或 `PKG_CONFIG_PATH` 没设 | 加 `pkgs.pkg-config`；`devShell` 会自动设 `PKG_CONFIG_PATH` |
| `cannot find -lfoo` | 缺库 | 加对应包 |
| `cc: command not found` | 缺编译器 | 加 `pkgs.gcc`（或 `stdenv` 已自带） |
| `No such file or directory: /lib64/ld-linux-x86-64.so.2` | **预编译二进制**，动态链接器路径写死 | 用 `nix-ld`（§15.8.3） |
| `error while loading shared libraries: libfoo.so.1` | 运行期找不到库 | `nix-ld` + `programs.nix-ld.libraries` |
| `bash: ./configure: cannot execute` | 缺 shebang 解释器 | `nix-shell -p stdenv` 或用 `patchShebangs` |

#### 15.8.2 `devShell` 的正确写法（关键在 `nativeBuildInputs` 自动设环境）

`pkgs.mkShell` 的 `packages` / `nativeBuildInputs` 会自动设置 **`PKG_CONFIG_PATH`、`CMAKE_PREFIX_PATH`、`NIX_CFLAGS_COMPILE`、`NIX_LDFLAGS`** 等一堆环境变量。这就是为什么**在 `devShell` 里编译通常能直接用**：

```nix
{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  packages = with pkgs; [
    # 构建工具
    pkg-config
    cmake
    ninja
    gnumake
    # 编译期依赖（头文件 + 库，nixpkgs 不区分）
    openssl
    zlib
    libffi
    # 运行时依赖
    # ...
  ];

  # 如果某个库不在标准位置，手动补
  shellHook = ''
    export PKG_CONFIG_PATH="${pkgs.openssl.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
    echo "devShell ready"
  '';
}
```

> [!TIP]
> **用 `pkg-config` 找不到包时的调试命令：**
> ```bash
> pkg-config --list-all | grep -i ssl
> echo $PKG_CONFIG_PATH
> pkg-config --cflags --libs openssl
> ```

#### 15.8.3 `nix-ld` —— 运行**预编译二进制**的官方兜底方案

这是解决「下载来的预编译程序跑不了」的**标准答案**。

```nix
programs.nix-ld = {
  enable = true;
  libraries = with pkgs; [
    # 按需添加。默认会带一批常见库
    stdenv.cc.cc.lib      # libstdc++
    zlib
    openssl
    curl
    # 如果某个程序报缺库，把库名加到这里
  ];
};
```

**源码级事实**：

| 选项 | 类型 | 声明默认 | **实际生效值** |
|---|---|---|---|
| `programs.nix-ld.enable` | bool | `false` | — |
| `programs.nix-ld.libraries` | list of package | `[ ]`（仅**声明**为空） | **14 个基础库**（见下） |

> [!IMPORTANT]
> **`libraries` 的「默认空」是个常见误读 —— 实际生效的是一份 14 个库的基础集合。**
>
> 选项声明里确实写着 `default = [ ]`（`nix-ld.nix:27-32`），但同一文件的 `config` 段在 `enable = true` 时**无条件注入**：
>
> ```nix
> # nixos/modules/programs/nix-ld.nix:47-64
> # We currently take all libraries from systemd and nix as the default.
> programs.nix-ld.libraries = with pkgs; [
>   zlib  zstd  stdenv.cc.cc  curl  openssl  attr  libssh
>   bzip2  libxml2  acl  libsodium  util-linux  xz  systemd
> ];
> ```
>
> 选项自己的 `defaultText` 也承认这点：*"baseLibraries derived from systemd and nix dependencies."*
>
> **关键推论（很多人不知道）**：因为 `libraries` 的类型是 `listOf`，而 NixOS 模块系统对 `listOf` 的合并是**拼接（concatLists）**，所以你写的 `libraries = [ ... ]` 是**追加**到那 14 个之上，**既不会冲突、也不会替换**。
>
> NixOS Wiki 的官方示例把这 14 个显式抄了一遍并注明 `# List by default`，正是这个原因 —— 抄了也无害（`buildEnv` 会去重），不抄也已经在。
>
> **所以「开了 nix-ld 还报找不到库」的正确解释不是「默认是空的」，而是「基础集合只覆盖 CLI/基础场景，GUI 应用还需要补 `libGL` / `libxkbcommon` / `gtk3` / `xorg.*` 等」。**
>
> 出处：`nixos/modules/programs/nix-ld.nix:27-32,47-64`（`[核实·源码]`）；[NixOS Wiki · Nix-ld](https://wiki.nixos.org/wiki/Nix-ld)（`[Wiki]`，原文 *"By default, nix-ld comes with only a few libraries"* + 列表注释 `# List by default`）

**`nix-ld` 能解决什么 / 不能解决什么**：

| 能 | 不能 |
|---|---|
| 预编译的 Linux 二进制（`./myapp`）找不到 `ld-linux` | ❌ **不能**让 AppImage 直接跑（用 `programs.appimage`） |
| 运行时 `libfoo.so.1` 缺失 | ❌ **不能**解决「需要特定版本 glibc」的问题 |
| `npx` / `pip` 下载的预编译 wheel 里的 `.so` | ❌ 不能解决内核/驱动层面的不兼容 |
| 各种「官方二进位」（§9 里的 codex 等） | ❌ 不能给 shell 提供 FHS 布局 |

#### 15.8.4 三者的分工（一张表记住）

| 需求 | 工具 |
|---|---|
| 从源码编译 | **`devShell`**（自动设好一切环境变量） |
| 跑预编译二进制 | **`programs.nix-ld`** |
| 跑 AppImage | **`programs.appimage`**（§17.4） |
| 需要完整 FHS 目录树 | **`buildFHSEnv` / `steam-run`**（§17.4） |
| 就是想「随便装点东西试试」 | **`nix-shell -p`** |

#### 15.8.5 `direnv` —— 让 `devShell` 自动生效

```nix
programs.direnv = {
  enable = true;
  nix-direnv.enable = true;    # 缓存 devShell，切换速度从秒级到毫秒级
  silent = true;               # 不打印加载信息
};
```

**选项（源码级）**：`enable`、`nix-direnv.enable`（默认 `true`）、`direnvrcExtra`（默认 `""`）、`silent`、`package`（默认 `pkgs.nix-direnv`）、`settings`（默认 `{ }`）。

> 出处：`nixos/modules/programs/direnv.nix` `[核实·源码]`

用法：项目目录放一个 `.envrc` 写 `use flake` 或 `use nix`，进入目录自动激活环境。

---

### 15.9 一份能直接用的多语言 `devShell` 模板

```nix
# shell.nix —— 放进项目根目录，然后 nix-shell 或配合 direnv
{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  packages = with pkgs; [
    # ── 通用构建工具 ──
    pkg-config
    cmake
    ninja
    gnumake

    # ── Node / TS ──
    nodejs_24
    typescript
    tsx
    esbuild

    # ── Python ──
    uv
    python313
    ruff

    # ── Rust ──
    cargo
    rustc
    rustfmt
    clippy

    # ── Go ──
    go
    gopls

    # ── 常用编译期依赖（按需删） ──
    openssl
    zlib
    libffi
    sqlite
  ];

  shellHook = ''
    echo "── devShell ──"
    echo "node $(node -v 2>/dev/null) | npm $(npm -v 2>/dev/null)"
    echo "python $(python3 -V 2>/dev/null | cut -d' ' -f2) | uv $(uv --version 2>/dev/null | cut -d' ' -f2)"
    echo "rust $(rustc --version 2>/dev/null | cut -d' ' -f2) | go $(go version 2>/dev/null | cut -d' ' -f3)"
  '';
}
```

> [!TIP]
> **只装你真正需要的。** 上面这份是为了「开箱可用」而全放，代价是**首次进入 devShell 要下载/构建很多**。项目定型后应该删到只剩必需的。

---

### 15.10 语言工具链的「坑与反直觉」汇总

| 坑 | 说明 |
|---|---|
| `npm i -g` 报 `EACCES` | 设计如此。改 `npm config set prefix ~/.npm-global` |
| `pip install` 报 `externally-managed-environment` | PEP 668。用 `devShell` / venv / `uv` |
| `pkgs.nodePackages.*` 找不到 | 26.05 已**整体删除**，改用顶层属性 |
| `ts-node` 不在 nixpkgs | 用 `pkgs.tsx` 或项目内局部安装 |
| `nix-ld` 开了还报缺库 | 基础集合只有 14 个库（CLI 向），GUI 应用要**追加** `libGL` / `libxkbcommon` / `gtk3` / `xorg.*` 等（见 §15.8.3） |
| `environment.sessionVariables.PATH` 覆盖 PATH | **会破坏系统 PATH**。改用 shell rc 或 Home Manager |
| 在 NixOS 上 `./configure && make` 失败 | 缺 FHS。用 `devShell`，不要用系统环境裸编 |
| `nodejs` 默认版本变了（22→24） | 26.05 的破坏性变更，检查 CI 里的 node 版本假设 |
| `corepack` 在 `nodejs-slim` 里没有 | 已移到单独 output，需显式引用 |

---

## 十六、MCP 与 Agent 配套工具（npm 型 MCP · SearXNG · 浏览器自动化）

> 承接第九章（Hermes / OpenClaw / Codex 的非 root 部署）。本章解决**装完 agent 之后，配套的 MCP server 和工具怎么装**。
>
> 前提不变：**全部在用户级，不要做成 root 服务。**

### 16.1 npm 安装的 MCP server 怎么处理？（核心问题）

MCP 生态里**大量 server 是 npm 包**（`npx -y @modelcontextprotocol/server-xxx`）。在 NixOS 上有**四种**处理方式，按推荐度排序。

#### 方式 1：nixpkgs 里有 → 直接用 nixpkgs（最佳）

```nix
# 有些 MCP server 已经进了 nixpkgs
environment.systemPackages = with pkgs; [
  mcp-nixos     # ← 已核实存在于 26.05
];
```

> 出处：`pkgs/by-name/mc/mcp-nixos/package.nix` 返回 200 `[核实·源码]`

**怎么找**：

```bash
# 用第12章的工具链查
nix search nixpkgs mcp
# 或在 search.nixos.org 搜 "mcp"
```

#### 方式 2：`npx` 直接跑 → 最省事，但**有 NixOS 特有的可靠性风险**

大多数 MCP 客户端配置长这样：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/docs"]
    }
  }
}
```

> [!WARNING]
> **在 NixOS 上 `npx` 型 MCP 的失败率明显高于普通发行版。** 原因是多层的：
>
> 1. `npx` 从 npm registry 下载的包，如果带**预编译原生模块**（`.node` 文件），它们是链接到宿主 glibc 的 —— NixOS 上会因动态链接器路径找不到而失败。
> 2. 即使纯 JS，某些包会在 `postinstall` 里调 `cc`/`python` 编译原生依赖，NixOS 上裸环境缺这些。
> 3. `npx` 的缓存目录、`npm` 的全局前缀在只读 store 下需要额外配置。
>
> **先试，失败就上方式 3 或 4。**

**提高成功率的配置**：

```bash
# 1. 设置可写缓存与用户级前缀
npm config set prefix ~/.npm-global
npm config set cache ~/.npm-cache
export PATH="$HOME/.npm-global/bin:$PATH"
```

```nix
# 2. 开 nix-ld 兜住原生模块（§15.8.3）—— 这是关键
programs.nix-ld = {
  enable = true;
  libraries = with pkgs; [
    stdenv.cc.cc.lib
    zlib
    openssl
    libuv            # Node 原生模块常需要
    libsecret
  ];
};
```

#### 方式 3：用户级 npm 全局安装 + 写绝对路径（**推荐给重度用户**）

```bash
# 装到用户目录
npm install -g @modelcontextprotocol/server-filesystem

# 拿到真实路径
which mcp-server-filesystem
# /home/you/.npm-global/bin/mcp-server-filesystem
```

然后 MCP 配置里**不用 `npx`，直接写绝对路径**：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "/home/you/.npm-global/bin/mcp-server-filesystem",
      "args": ["/home/you/docs"]
    }
  }
}
```

**优点**：
- 不依赖 `npx` 每次下载
- 路径确定，报错时好排查
- 完全用户级，不需要 root
- 可以用 `npm ls -g --depth=0` 看到装了什么

**缺点**：不在 `configuration.nix` 里，换机器要重装（但可以用脚本固化，见下）。

#### 方式 4：打成 Nix 包（**最 NixOS 的做法，成本最高**）

用 `buildNpmPackage` 把它包成 derivation，这样它就在 `/nix/store` 里，声明式、可回滚：

```nix
{ pkgs ? import <nixpkgs> { } }:

pkgs.buildNpmPackage rec {
  pname = "mcp-server-filesystem";
  version = "1.0.0";

  src = pkgs.fetchFromGitHub {
    owner = "modelcontextprotocol";
    repo = "servers";
    rev = "v${version}";
    hash = "sha256-...";   # 先填 lib.fakeHash，构建时报错会告诉你真值
  };

  npmDepsHash = "sha256-...";   # 同上

  # 26.05 新特性：npm workspaces 项目需要这个
  # npmDepsFetcherVersion = 2;

  meta.maintainers = [ ];
}
```

> [!TIP]
> **26.05 对 npm 打包的改进**（`[官方]` release notes）：
> - `buildNpmPackage` 新增 `npmDepsFetcherVersion` 选项，设为 `2` 启用 packument 缓存，**修复使用 npm workspaces 的项目的构建**（release notes:396）
> - 新增顶层属性 `fetchPnpmDeps` 和 `pnpmConfigHook`，取代已废弃的 `pnpm.fetchDeps` / `pnpm.configHook`（release notes:387）
> - ⚠️ `pnpm` 的 `fetcherVersion = 1` 和 `2` 已废弃（release notes:389）

#### 四种方式的决策树

```
这个 MCP server 在 nixpkgs 里有吗？
├─ 有 → 方式 1（nixpkgs 包）        ← 首选
└─ 没有
   ├─ 它带原生模块 / 你懒得折腾 → 先试方式 2（npx + nix-ld）
   ├─ 你天天用它 → 方式 3（npm -g + 绝对路径）  ← 推荐
   └─ 你要在多台机器复现 → 方式 4（buildNpmPackage）
```

> [!IMPORTANT]
> **无论哪种方式，都不要把 MCP server 做成 root 系统服务。**
>
> 理由（与第九章一致）：
> 1. 你的 agent 以普通用户身份运行，**没有权限访问 root 服务的 socket**
> 2. MCP server 通常需要读写**你的**文件（家目录、项目），以 root 跑会产生 root 属主的文件，污染你的工作区
> 3. 凭据（API key）以 root 保存会让「改配置」变成每次都要 `sudo`
> 4. 一旦 MCP server 被投毒，root 权限就是全盘沦陷

---

### 16.2 SearXNG：给 agent 一个自托管搜索引擎

> 用户提到的「searng」按上下文理解为 **SearXNG**（自托管元搜索引擎）。这是给 agent 提供「联网搜索」能力最常见的选择 —— **不需要 API key，不泄露查询给第三方**。

#### 16.2.1 模块的全部选项（源码级核实）

`services.searx` 在 26.05 的选项：

| 选项 | 用途 |
|---|---|
| `enable` | 开关 |
| `openFirewall` | 开防火墙端口（**只在本机用就别开**） |
| `domain` | 服务域名 |
| `environmentFile` | 注入环境变量（**放 `SEARX_SECRET_KEY` 用**） |
| `redisCreateLocally` | 本地起一个 Redis/Valkey（限流器需要） |
| `settings` | SearXNG 的 `settings.yml`（attrset，**这是主配置**） |
| `settingsFile` | 直接用文件替代 `settings` |
| `faviconsSettings` | 图标服务配置 |
| `limiterSettings` | 限流器配置 |
| `configureUwsgi` | 是否配置 uwsgi（默认走它） |
| `configureNginx` | 是否配置 nginx 反代 |
| `uwsgiConfig` | uwsgi 参数 |

> 出处：`nixos/modules/services/networking/searx.nix` `[核实·源码]`

#### 16.2.2 只在本机给 agent 用的最小配置

```nix
services.searx = {
  enable = true;

  # ⚠️ 本机自用：不开防火墙，只监听 localhost
  openFirewall = false;

  # 限流器需要 Redis —— 让它本地起一个
  redisCreateLocally = true;

  settings = {
    server = {
      # 只监听本机（默认就是 127.0.0.1）
      bind_address = "127.0.0.1";
      port = 8888;

      # 🔑 密钥：不要写死在配置里，用 environmentFile
      secret_key = "$SEARX_SECRET_KEY";

      # 关掉遥测/统计（自用不需要）
      limiter = true;
      public_instance = false;
    };

    search = {
      # 启用 JSON 输出 —— agent 需要它，见下
      formats = [ "html" "json" ];
      safe_search = 0;
    };

    # 关掉不需要的引擎，减少启动开销
    engines = [
      { name = "Google"; disabled = false; }
      { name = "Bing";   disabled = false; }
      { name = "DuckDuckGo"; disabled = false; }
    ];

    # 关掉会泄露信息的
    outgoing = {
      request_timeout = 6.0;
      max_request_timeout = 10.0;
    };
  };
};
```

**密钥的正确放法**（不要写进 `configuration.nix`，它会进 `/nix/store` 且全局可读）：

```nix
services.searx.environmentFile = "/run/secrets/searx.env";
# 文件内容：
# SEARX_SECRET_KEY=一串随机字符串
# 用 sops-nix / agenix 或手工创建（权限 600，属主 root）
```

> [!DANGER]
> **`secret_key` 绝对不能明文写进 `configuration.nix`。**
>
> `/nix/store` 里的所有文件**全局可读**，而且会进 NixOS generation 永久保留（即使你删掉配置，旧 generation 里还在）。用 `environmentFile` 指向一个 `600` 权限的文件。

#### 16.2.3 关键：让 agent 用上 JSON API

**默认 SearXNG 只输出 HTML。** agent 需要结构化数据，必须显式开 JSON：

```nix
services.searx.settings.search.formats = [ "html" "json" ];
```

验证：

```bash
# 起来之后
curl -s "http://127.0.0.1:8888/search?q=nixos&format=json" | head -c 500
```

> [!NOTE]
> **`settings.search.formats` 必须包含 `"json"`**，否则 agent 调用会拿到 HTML。这是最容易漏的一步。`[核实·源码]`（`settings` 直通 `settings.yml`）

#### 16.2.4 把 SearXNG 接给 agent

MCP 生态里有若干「SearXNG MCP server」，配置思路：

```json
{
  "mcpServers": {
    "searxng": {
      "command": "npx",
      "args": ["-y", "mcp-searxng"],
      "env": {
        "SEARXNG_URL": "http://127.0.0.1:8888"
      }
    }
  }
}
```

> [!WARNING]
> **具体的 SearXNG MCP server 包名/参数各家不同，我这里没有核实到某个确定的包**，标注 `[未核实]`。请以你选用的那个 MCP server 的官方 README 为准。
>
> **更稳的做法**：不依赖 MCP，直接给 agent 一个 shell 工具：
> ```bash
> # 写个小脚本放进 PATH
> cat > ~/.local/bin/searx <<'EOF'
> #!/usr/bin/env bash
> curl -s "http://127.0.0.1:8888/search?q=$(printf '%s' "$*" | jq -sRr @uri)&format=json" | jq '.results[:5]'
> EOF
> chmod +x ~/.local/bin/searx
> ```
> agent 只要能执行 shell 就能用 —— **比装 MCP 少一层故障点**。

#### 16.2.5 26.05 的两个改名坑（源码级）

| 情况 | 事实 |
|---|---|
| `services.searx.configFile` | **已重命名为** `services.searx.settingsFile`（`mkRenamedOptionModule`） |
| `services.searx.runInUwsgi` | **已重命名为** `services.searx.configureUwsgi` |
| `settings.redis` | **已重命名为** `settings.valkey`（旧名会打印废弃警告，但**仍兼容**） |

> 出处：`nixos/modules/services/networking/searx.nix:107,255-256` `[核实·源码]`

---

### 16.3 浏览器自动化（Playwright / 无头 Chrome）

Agent 要「上网操作」时最常见的需求。

#### 16.3.1 Playwright

**核心问题**：Playwright 要下载浏览器二进制，而 NixOS 上这些二进制**不能**用 `npx playwright install` 装（它们需要 FHS + 特定 glibc）。

**解法：用 nixpkgs 的 `playwright-driver`。**

```nix
{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  packages = [
    pkgs.playwright-driver.browsers
    # 或只要 chromium（体积小很多）
    # pkgs.playwright-driver.browsers-chromium
  ];

  shellHook = ''
    export PLAYWRIGHT_BROWSERS_PATH="${pkgs.playwright-driver.browsers}"
    export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
    export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true
  '';
}
```

**源码级事实**（`pkgs/development/web/playwright/driver.nix`）：

| 项 | 值 |
|---|---|
| Playwright 版本 | **1.59.1** |
| `passthru.browsers` | 全部浏览器（`browsers { }`） |
| `passthru.browsers-chromium` | 只要 Chromium |
| `passthru.selectBrowsers` | 函数，可挑 |
| 环境变量 | 二进制里的 wrapper 会 `--set-default PLAYWRIGHT_BROWSERS_PATH` |

> 出处：`pkgs/development/web/playwright/driver.nix:22,162-166,194` `[核实·源码]`

> [!TIP]
> **体积考虑**：`browsers`（全量）含 Chromium + Firefox + WebKit + ffmpeg，**很大**（数 GB）。只用 Chromium 的话用 `browsers-chromium`。
>
> 对 agent 用途（抓页面、填表单），**`browsers-chromium` 通常够**。

#### 16.3.2 其他浏览器自动化方案

| 方案 | 说明 |
|---|---|
| **`agent-browser` / `playwright-cli` skill** | 本机已装的 skill，封装了常见操作 |
| **CDP 接管已有 Chrome** | 让 agent 用你已经登录的浏览器（保留登录态）—— 适合需要登录的场景 |
| **无头 Chromium** | `pkgs.chromium` + `--headless`，最轻量 |

> [!WARNING]
> **不要用 `npx playwright install`。** 它会下载官方预编译浏览器到 `~/.cache/ms-playwright`，在 NixOS 上**大概率因缺少动态链接器而启动失败**。用 `pkgs.playwright-driver`。

---

### 16.4 Agent 常用 CLI 工具清单

这些是「agent 会调用、你需要装上」的工具。**全部走系统包（L1），不要用 npm/pip 全局装**：

```nix
environment.systemPackages = with pkgs; [
  # ── 搜索 / 抓取 ──
  curl
  wget
  jq              # JSON 处理，agent 最常用
  yq              # YAML 处理
  ripgrep         # 高速文本搜索
  fd              # 高速文件查找
  httpie          # 人类友好的 HTTP 客户端

  # ── 文件 / 内容 ──
  pandoc          # 文档格式转换
  poppler-utils   # pdftotext 等
  imagemagick     # 图片处理

  # ── 版本控制 ──
  git
  gh              # GitHub CLI

  # ── 进程 / 系统 ──
  procps
  lsof
  htop
  btop

  # ── 压缩 ──
  unzip
  zip
  p7zip
];
```

> [!TIP]
> **`jq` 是 agent 工作流里最重要的一个工具。** 大量 agent 操作是「调 API → 解析 JSON → 决策」。没有 `jq`，agent 只能用脆弱的文本处理。

---

### 16.5 沙箱与凭据（安全边界）

> 这一节和第十七章互补。这里讲 **agent/MCP 层面的隔离**，第十七章讲**系统层面**。

#### 16.5.1 凭据管理

| 做法 | 评价 |
|---|---|
| ❌ 把 API key 写进 `configuration.nix` | **最危险** —— 进 `/nix/store`，全局可读，永久保留 |
| ❌ 把 key 写进 git 仓库的 MCP 配置 | 会泄露 |
| ✅ 用户级 dotfile（`chmod 600`） | 可接受，最简单 |
| ✅ **`sops-nix` / `agenix`** | 加密后进 git，解密到 `/run/secrets` —— **推荐** |
| ✅ 系统级 systemd `LoadCredential` | 适合服务，不适合交互式 agent |

**sops-nix 思路**（不展开完整配置）：

```nix
# 密文进 git，明文只在 /run/secrets 出现
sops.secrets."mcp/openai_key" = {
  owner = "youruser";     # 关键：属主是你，不是 root
  mode = "0400";
};
```

> [!IMPORTANT]
> **`owner` 必须是你的普通用户**，否则你的非 root agent 读不到。

#### 16.5.2 给 MCP server 划边界

MCP server 是**你信任的代码**，但它可能：
- 被投毒（供应链攻击）
- 有 bug 导致误删文件
- 被 prompt injection 诱导执行危险操作

**降低风险的做法**：

| 措施 | 说明 |
|---|---|
| **用专用工作目录** | 给 filesystem MCP 只暴露 `/home/you/agent-workspace`，**不要暴露整个家目录** |
| **只读挂载** | 能用只读就用只读 |
| **不要在 MCP 环境里放 sudo 凭据** | 别让 agent 有提权路径 |
| **限制网络** | 不需要联网的 MCP 就别给它网络 |
| **`systemd-run` 起沙箱** | `systemd-run --user --scope -p ProtectHome=read-only -p PrivateTmp=yes ...` |

> [!TIP]
> **一个很实用的原则：agent 的「爆炸半径」应该等于「它需要访问的目录」。**
>
> 具体做法：给 agent 建一个专用用户（或至少专用目录），MCP 只暴露那个目录。这样即使 MCP 被完全控制，损失也局限于那个目录。

---

### 16.6 本章的「坑与反直觉」

| 坑 | 说明 |
|---|---|
| `npx` 型 MCP 在 NixOS 上易失败 | 原生模块链接宿主 glibc。开 `nix-ld` + 用户级 npm 前缀 |
| `nix-ld.libraries` 有基础集合但只覆盖 CLI | 14 个库是**基础集**，GUI 应用要追加（`listOf` 是拼接，不冲突） |
| SearXNG 默认不输出 JSON | 必须 `settings.search.formats = [ "html" "json" ]` |
| SearXNG 的 `secret_key` 明文 | 会进 `/nix/store`（全局可读）。用 `environmentFile` |
| `services.searx.configFile` / `runInUwsgi` | 已改名 `settingsFile` / `configureUwsgi` |
| `settings.redis` | 已改名 `settings.valkey` |
| `npx playwright install` | 在 NixOS 上基本不可用。用 `pkgs.playwright-driver` |
| `playwright-driver.browsers` 体积 | 数 GB。只要 Chromium 用 `browsers-chromium` |
| 把 MCP 做成 root 服务 | **不要做**（原因见 §16.1 末尾） |
| `pkgs.nodePackages.*` | 26.05 已整体删除 |
| MCP 的凭据写进 `configuration.nix` | 进 `/nix/store`，永久可读 |

---

## 十七、安全加固、防病毒与 FHS 总表

> 这一章回答三个具体问题：
> 1. **SELinux 之类的需要装吗？**
> 2. **防病毒上，NixOS 是否更好？**
> 3. **FHS 到底怎么处理？**（完整决策树）

### 17.1 SELinux 需要装吗？—— **NixOS 没有 SELinux 模块**

**直接回答：`selinux` 在 NixOS 26.05 中不存在。**

核实方法（你可以自己跑）：在 `nixos/modules/module-list.nix` 里搜 `selinux` —— **匹配数为 0**。`[核实·源码]`

**NixOS 的强制访问控制（MAC）现状**：

| 机制 | NixOS 26.05 状态 | 模块路径 |
|---|---|---|
| **AppArmor** | ✅ **有模块** | `security/apparmor.nix` |
| **SELinux** | ❌ **无模块** | — |
| **audit / auditd** | ✅ 有模块 | `security/audit.nix`、`security/auditd.nix` |
| **systemd 沙箱** | ✅ 内置（无需模块） | systemd 本身 |
| **Landlock** | ⚠️ 内核有，无 NixOS 集成 | — |
| **seccomp** | ⚠️ 内核有，无 NixOS 集成 | — |

> 出处：`nixos/modules/module-list.nix` `[核实·源码]`

```nix
# AppArmor 的正确写法
security.apparmor = {
  enable = true;
  # 需要给特定程序加载 profile 时：
  # packages = [ pkgs.someApp ];   # 带上它的 apparmor profile
  # policies = { ... };
};
```

> [!IMPORTANT]
> **不要试图在 NixOS 上装 SELinux。** 这不是「麻烦」的问题，是**没有集成**：SELinux 需要对整个文件系统打标签（`restorecon`），而 NixOS 的 `/nix/store` 是**内容寻址、只读、多代并存**的 —— 给 store 打标签在语义上就与 Nix 模型冲突（同一个 store path 被不同代际共享，标签无法按「代际」区分）。
>
> **结论：如果你的合规要求必须有 SELinux，NixOS 不是合适的平台。** 用 Fedora / RHEL。

**那 NixOS 靠什么做隔离？**

NixOS 的隔离哲学是**「用 systemd 的沙箱 + 最小权限」**，而不是「一个全局 MAC 策略」：

```nix
# 给一个服务加 systemd 沙箱（NixOS 的「正确姿势」）
systemd.services.myservice.serviceConfig = {
  # 文件系统隔离
  ProtectSystem = "strict";       # /usr /boot 只读
  ProtectHome = "read-only";      # 家目录只读
  PrivateTmp = true;              # 独立 /tmp
  PrivateDevices = true;          # 不给设备访问
  # 内核隔离
  ProtectKernelTunables = true;
  ProtectKernelModules = true;
  ProtectControlGroups = true;
  # 提权隔离
  NoNewPrivileges = true;         # 禁止 setuid
  RestrictSUIDSGID = true;
  # 网络隔离
  RestrictAddressFamilies = [ "AF_UNIX" "AF_INET" "AF_INET6" ];
  # 系统调用过滤
  SystemCallFilter = [ "@system-service" ];
  LockPersonality = true;
  MemoryDenyWriteExecute = true;
  RestrictNamespaces = true;
};
```

> [!TIP]
> **这套 systemd 沙箱比「装个 SELinux」对个人用户更实用**，因为它**按服务粒度**生效、不依赖全局标签、不影响你日常操作，而且是 NixOS 里「本来就该这么写」的东西。

---

### 17.2 防病毒 / 主机防护：NixOS 有没有优势？

**先说结论**：NixOS 在**供应链完整性**上有**结构性的、可验证的**优势；在**传统防病毒**上没有优势（也不需要）。

#### 17.2.1 NixOS 的真实结构性优势（可验证的论据）

| 优势 | 机制 | 为什么是真的 |
|---|---|---|
| **构建可复现 / 可验证** | 同一个 derivation → 同一个 store path（内容寻址） | 你可以**独立重构建并比对 hash**，验证二进制没被篡改。传统发行版做不到 |
| **二进制缓存有签名** | `nix.settings.trusted-public-keys` 校验 | 从 cache 下载的包有签名，且 hash 与 derivation 绑定 |
| **无 `curl \| sh` 文化** | 装东西走 derivation | 传统教程里大量 `curl ... \| bash`（把网络内容直接执行）。NixOS 生态里这是反模式 |
| **无隐藏的 post-install 脚本** | 所有构建步骤在 sandbox 里、可读 | Debian 的 `.deb` 可以在 `postinst` 里做任何事；Nix 的构建在隔离环境且脚本可读 |
| **回滚是原子且彻底的** | generation 切换 | 被入侵后可以**切回已知干净代际**。这是传统发行版做不到的（被改的系统文件无法可靠还原） |
| **没有全局可写系统目录** | `/nix/store` 只读 | 恶意软件无法把 payload 写进系统目录并持久化。**这是防病毒层面非常实际的收益** |
| **状态集中在可审计的地方** | `/etc/nixos`、`/nix/store` | 想找「系统被改了什么」很容易：`nixos-rebuild list-generations` + diff 配置 |

> [!IMPORTANT]
> **最实际的一条：`/nix/store` 只读。**
>
> 传统 Linux 上，恶意软件的标准套路是「把自己复制到 `/usr/bin`、加个 systemd 服务、改 `/etc/ld.so.preload`」—— 这些**在 NixOS 上全都写不进去**（需要 `sudo` + 重建）。这消除了**一整类**持久化手法。
>
> 注意：这只消除「系统级持久化」。**用户目录里的恶意代码照样能跑**（比如被投毒的 npm 包）。

#### 17.2.2 传统防病毒（ClamAV）—— 有必要吗？

```nix
services.clamav = {
  daemon.enable = true;       # 常驻扫描守护进程
  updater.enable = true;      # 自动更新病毒库
  # 也可只装 CLI：
  # upgrade-clamav-db.enable = true;
};
```

`services/security/clamav.nix` 存在。`[核实·源码]`

| 场景 | 需要 ClamAV 吗 |
|---|---|
| 你的 Linux 桌面 | ❌ **基本不需要**。Linux 桌面恶意软件极少，且 NixOS 的只读 store 挡住一大类 |
| **你给 Windows 用户传文件**（U 盘、共享目录） | ✅ **有用** —— 扫的是「别被你的 Linux 机器中转的 Windows 病毒」 |
| 邮件网关 / 文件服务器 | ✅ 需要 |
| 合规要求 | ✅ 看要求 |

> [!NOTE]
> **ClamAV 扫的是「已知 Windows/Linux 恶意软件特征」，不是「行为检测」。** 它对「你刚 npm 装的被投毒包」**毫无帮助** —— 那种包没有特征签名。**防供应链攻击靠的是锁版本 + 审依赖，不是杀毒软件。**

#### 17.2.3 其他主机防护模块

```nix
# fail2ban：防暴力破解（对暴露 SSH 的机器有用）
services.fail2ban = {
  enable = true;
  maxretry = 5;
  bantime = "1h";
};

# auditd：系统调用审计（排查/合规用）
security.auditd.enable = true;
security.audit.enable = true;

# 防火墙（NixOS 默认已开）
networking.firewall = {
  enable = true;              # 默认 true
  allowedTCPPorts = [ ];      # 默认空 = 全部拒绝入站
  allowedUDPPorts = [ ];
};
```

> [!TIP]
> **NixOS 的默认防火墙策略是「拒绝所有入站」**（`allowedTCPPorts` 默认空）。这是个很好的默认值 —— 你不需要额外加固就已经是「白名单模式」。

#### 17.2.4 那「防病毒上 NixOS 是否更好」的诚实答案

| 维度 | NixOS | 传统发行版 | 谁更好 |
|---|---|---|---|
| 系统级持久化 | 极难（只读 store） | 容易 | **NixOS** |
| 供应链完整性 | 内容寻址 + 签名 cache + 可复现 | 有签名但不可复现 | **NixOS** |
| 被入侵后恢复 | generation 原子回滚 | 无法可靠还原 | **NixOS** |
| **用户级恶意代码**（被投毒的 npm/pip 包） | **一样会中招** | 一样会中招 | 打平 |
| **钓鱼 / 社工 / 浏览器漏洞** | 一样会中招 | 一样会中招 | 打平 |
| 内核加固（ASLR 等） | 默认内核配置正常 | 正常 | 打平 |
| 杀毒软件生态 | 少 | 多 | 传统发行版（但对桌面用户无意义） |

> [!IMPORTANT]
> **最诚实的总结：NixOS 让你「更不容易被持久化」，但不会让你「更不容易被钓鱼」。**
>
> 它解决的是**系统完整性**问题，不是**人的判断力**问题。你的最大风险面依然是：浏览器、你运行的脚本、你装的包、你点的链接。

---

### 17.3 FHS 处理的完整决策树

这是本文反复出现的话题（§9、§15.8、§17）。这里给一张**总表**。

#### 17.3.1 为什么 NixOS 没有 FHS

ELF 可执行文件把**动态链接器的绝对路径**写死在文件头里（`/lib64/ld-linux-x86-64.so.2`）。NixOS 的 store 路径是 `/nix/store/<hash>-glibc-.../lib/ld-linux-x86-64.so.2`。所以：

1. **预编译二进制**（从网上下载的）会去找 `/lib64/ld-linux-x86-64.so.2` → 不存在 → 启动失败
2. **需要 FHS 布局的构建系统**（`./configure` 找 `/usr/lib`）→ 找不到

> 出处：本文第一章（心智模型）+ 姊妹文档 `nixos-ops-guide.md`

#### 17.3.2 五种方案对比（总表）

| 方案 | 解决的场景 | 代价 | 何时用 |
|---|---|---|---|
| **`nix-shell -p <pkg>`** | 临时用 nixpkgs 里的工具 | 无 | **默认先试这个** |
| **`devShell` / `nix develop`** | 从源码编译项目 | 需写 `shell.nix` | 开发项目 |
| **`programs.nix-ld`** | 跑**预编译二进制** | 自带 14 库基础集，GUI 应用需**追加** | 官方二进位、npx 原生模块 |
| **`programs.appimage`** | 跑 AppImage | 无（有 `binfmt` 可双击） | 只有 AppImage 的软件 |
| **`buildFHSEnv`** | 需要**完整 FHS 目录树** | 重、启动慢 | 复杂软件、Steam、自定义运行时 |
| **`steam-run`** | 想用 Steam 的 FHS 环境跑任意程序 | 依赖 Steam 运行时 | 临时跑一个需要 FHS 的程序 |

#### 17.3.3 各方案的具体写法

**① `nix-shell -p`（临时）**

```bash
nix-shell -p ffmpeg imagemagick --run "your-command"
```

**② `devShell`（项目）** — 见 §15.8.2

**③ `programs.nix-ld`（预编译二进制）**

```nix
programs.nix-ld = {
  enable = true;
  # 追加项（基础集已有 zlib/openssl/curl/stdenv.cc.cc 等 14 个）
  libraries = with pkgs; [
    libuv
    libsecret
    libGL
    libxkbcommon
  ];
};
```

> ⚠️ `libraries` **默认 `[ ]`**（§15.8.3）

**④ `programs.appimage`（AppImage）**

```nix
programs.appimage = {
  enable = true;      # 装上 appimage-run
  binfmt = true;      # 🔑 注册 binfmt —— 之后 AppImage 可以「双击运行」
  # package = pkgs.appimage-run.override {
  #   extraPkgs = pkgs: [ pkgs.ffmpeg pkgs.imagemagick ];   # 补 AppImage 缺的库
  # };
};
```

**源码级事实**：`binfmt = true` 会注册 **magic-based binfmt**，匹配 AppImage 的 type 1 和 type 2 魔数（`\x7fELF....AI\x01` / `AI\x02`）。

| 选项 | 类型 | 默认 |
|---|---|---|
| `enable` | bool | `false` |
| `binfmt` | bool | `false` |
| `package` | package | `pkgs.appimage-run` |

> 出处：`nixos/modules/programs/appimage.nix` `[核实·源码]`

> [!TIP]
> **`binfmt = true` 是很多人漏掉的关键一步。** 只写 `enable = true` 的话，你得手动 `appimage-run ./foo.AppImage`。开了 `binfmt`，**在文件管理器里双击 AppImage 就能跑**（因为内核会按魔数调用 `appimage-run`）。

**⑤ `buildFHSEnv`（完整 FHS）**

```nix
# 给一个需要 FHS 的软件造一个「伪 FHS 环境」
{ pkgs ? import <nixpkgs> { } }:

(pkgs.buildFHSEnv {
  name = "my-fhs-env";
  targetPkgs = pkgs: with pkgs; [
    # 这里的东西会被放进 FHS 布局
    glibc
    zlib
    openssl
    # ...
  ];
  runScript = "bash";
}).env
```

**⑥ `steam-run`（借 Steam 的 FHS）**

```bash
# 临时跑一个需要 FHS 的程序（不需要 Steam 正在运行，但需要装了 Steam）
steam-run ./some-binary
```

> [!WARNING]
> **`steam-run` 依赖 `programs.steam` 的运行时环境。** 它是「顺手用一下」的工具，**不是长期方案**。长期方案用 `buildFHSEnv`。

#### 17.3.4 决策流程（照着走）

```
你要跑的是什么？
│
├─ nixpkgs 里已经有 → nix-shell -p 或 environment.systemPackages  ✅ 到此为止
│
├─ 从源码编译的项目
│   └─ devShell（shell.nix）                                      ✅ 到此为止
│
├─ 下载来的预编译二进制（./myapp）
│   └─ programs.nix-ld = { enable = true; libraries = [...]; }     ✅ 到此为止
│
├─ AppImage（.AppImage 文件）
│   └─ programs.appimage = { enable = true; binfmt = true; }        ✅ 到此为止
│
├─ 需要完整 /usr /lib /bin 布局的复杂软件
│   └─ buildFHSEnv                                                  ✅ 到此为止
│
└─ 只是临时试一下
    └─ steam-run ./binary（前提：装了 Steam）
```

> [!IMPORTANT]
> **顺序很重要：从上往下试。** 越靠上的方案越「Nix 原生」，越可复现、越可回滚。很多人一上来就用 `buildFHSEnv`，结果把一个本来 `nix-shell -p` 就能解决的问题复杂化了。

#### 17.3.5 一个必须知道的组合

**`nix-ld` + `appimage` 可以同时开**，它们不冲突：

```nix
programs.nix-ld = {
  enable = true;
  libraries = with pkgs; [ stdenv.cc.cc.lib zlib openssl ];
};

programs.appimage = {
  enable = true;
  binfmt = true;
};
```

**为什么可以同时开**：`nix-ld` 处理「动态链接器路径写死」的问题；`appimage` 处理「AppImage 需要挂载+运行」的问题。**AppImage 内部如果又调用别的预编译二进制，`nix-ld` 还能帮上忙。**

---

### 17.4 安全加固速查清单

```nix
# ── 强制访问控制 ──
security.apparmor.enable = true;          # SELinux 在 NixOS 不存在，别找

# ── 审计 ──
security.auditd.enable = true;

# ── 防火墙（默认就是拒绝所有入站） ──
networking.firewall = {
  enable = true;
  allowedTCPPorts = [ ];                  # 需要什么开什么
  allowedUDPPorts = [ ];
};

# ── SSH（如果开） ──
services.openssh = {
  enable = false;                         # 桌面机器建议关掉
  # 如果必须开：
  # settings = {
  #   PasswordAuthentication = false;     # 只用密钥
  #   PermitRootLogin = "no";
  #   KbdInteractiveAuthentication = false;
  # };
};

# ── 暴力破解防护（暴露 SSH 时才有意义） ──
services.fail2ban.enable = true;

# ── 自动安全更新（可选） ──
system.autoUpgrade = {
  enable = true;
  allowReboot = false;                    # 自动重启有风险，建议 false
  dates = "weekly";
};

# ── 内核加固（26.05 默认已不错，这些是额外可选项） ──
boot.kernel.sysctl = {
  "kernel.kptr_restrict" = 2;
  "kernel.dmesg_restrict" = 1;
  "kernel.unprivileged_bpf_disabled" = 1;   # ⚠️ 见下方警告
  "net.core.bpf_jit_harden" = 2;
};
```

> [!DANGER]
> **`kernel.unprivileged_bpf_disabled = 1` 会让 `scx` 和部分 eBPF 工具失效。**
>
> 原因：sched_ext 调度器需要 BPF 能力。**如果你要用 `services.scx`（§14.3），不要设这一条。**
>
> 这是一个真实的「安全加固 ↔ 性能优化」冲突点 —— 本文把它明确标出来，避免你两头踩坑。

> [!WARNING]
> **`system.autoUpgrade.allowReboot = true` 有风险**：它会在更新后自动重启，**可能在你正在工作时重启**。桌面机器建议 `false`，手动选时机。

---

### 17.5 本章的「坑与反直觉」

| 坑 | 说明 |
|---|---|
| 想装 SELinux | **NixOS 没有这个模块**。语义上与 Nix 模型冲突 |
| 以为 NixOS「自带杀毒」 | 不。它有的是**完整性**，不是**检测** |
| 以为 NixOS 能防钓鱼 / 防投毒 npm 包 | **不能**。用户级代码照样跑 |
| 开了 `nix-ld` 还是跑不了 | `libraries` 默认空，必须自己列 |
| AppImage 只能命令行跑 | 加 `binfmt = true` 就能双击 |
| `kernel.unprivileged_bpf_disabled = 1` | **会让 scx 失效** |
| 想用 `steam-run` 当长期方案 | 它依赖 Steam 运行时，长期用 `buildFHSEnv` |
| `services.openssh.enable` 默认 | 桌面机器确认它是关的 |
| 以为「只读 store」= 绝对安全 | 只挡系统级持久化，用户目录照样能中招 |
| `security.audit.enable` 和 `auditd` | 两个不同模块，用途不同 |

---

## 十八、不加任何外部仓库，把 NixOS 调到「接近 CachyOS」

### 18.1 先说结论

**CachyOS 的「优化」是 8 个层叠起来的，不是一件事。** 把它们拆开看，你会发现其中**大部分是普通 Linux 配置**，只有最底层的内核补丁是发行版私有的：

| 层 | CachyOS 的做法 | 不加外部仓库，NixOS 能否复刻 |
|---|---|---|
| ① 内核调度器 | `linux-cachyos`（**BORE** = `CONFIG_SCHED_BORE`）+ POC idle selector | ❌ **拿不到**（见 18.3）。但目标可由 ② 达成 |
| ② 用户态调度器 | `scx-scheds`（`scx_lavd` / `scx_bpfland`） | ✅ **完全可复刻**：`services.scx` |
| ③ 进程优先级 | `ananicy-cpp` + **CachyOS 官方规则集** | ✅ **完全可复刻**：`services.ananicy` + `pkgs.ananicy-rules-cachyos` |
| ④ sysctl 调参 | `70-cachyos-settings.conf` | ✅ 可复刻（逐行翻译，见 18.4） |
| ⑤ udev 设备规则 | I/O 调度器 / zram / SATA / hdparm / 权限 | ✅ 大部分可复刻（见 18.5） |
| ⑥ 内存 | zram（zstd, priority 100）+ THP 调整 + uksmd | ⚠️ **大部分可复刻**；`uksmd` 拿不到，用内核 KSM 替代 |
| ⑦ systemd/limits | limits、journald、timesyncd、delegate | ✅ 可复刻（但有几条**不该抄**，见 18.8） |
| ⑧ 图形 / 游戏 | `mesa-git`、`proton-cachyos`、`game-performance` | ⚠️ mesa-git / proton-cachyos **拿不到**；GE 与 wrapper 可替代 |

> [!IMPORTANT]
> **一句话**：CachyOS 最被称道的「手感」（交互响应、游戏卡顿少），**本质来自 ② ③ 两层**，而这两层在 nixpkgs 里都是**一等公民模块**。
> 反过来说，**唯一真正拿不到的是 BORE 调度器本身**（它需要改内核源码）。但 BORE 想解决的问题（交互任务优先、减少卡顿）在 NixOS 上由 `scx_lavd` 用完全不同的机制解决 —— 而且是**运行时可热切换**的。

> [!WARNING]
> **`pkgs.bore` 不是 BORE 调度器。** nixpkgs 里的 `bore` 是那个 **TCP 隧道工具**（Rust 写的，`bore.pub` 那套）。搜索时看到 `nix shell nixpkgs#bore` 千万别以为是调度器。
>
> ⚠️ **它有两个"家"，别搞混**：CLI 的上游项目是 [`ekzhang/bore`](https://github.com/ekzhang/bore)（GitHub，bore.pub 服务）；而 **nixpkgs 实际打包的源码**是 [`delan/nonymous`](https://bitbucket.org/delan/nonymous)（**Bitbucket**）—— 一个把 `bore` 作为 workspace 成员的仓库。所以 `package.nix` 里写的是 `fetchFromBitbucket { owner = "delan"; repo = "nonymous"; rev = "bore-0.4.1"; }` + `cargoBuildFlags = [ "-p" "bore" ]`。
>
> `[核实·源码]`（`pkgs/by-name/bo/bore/package.nix`，`version = "0.4.1"`，`rustPlatform.buildRustPackage`）

---

### 18.2 两件大事：`scx` 与「CachyOS 官方 ananicy 规则」

这两条是你这次问题的**核心答案**，而且都是 nixpkgs 原生、零外部依赖。

#### （1）ananicy-cpp + **CachyOS 自己的规则仓库**

**关键事实**：nixpkgs 已经收录了 **CachyOS 官方的 ananicy 规则仓库**。

```
pkgs.ananicy-rules-cachyos
  version = "0-unstable-2026-05-19"
  src     = github:CachyOS/ananicy-rules @ 74b314e1c54115623fcb0eea868d1e08a10f84fe
```

`[核实·源码]`（`pkgs/by-name/an/ananicy-rules-cachyos/package.nix`）

这意味着：**你在 NixOS 上用的就是 CachyOS 用户用的那份规则**，不是「社区仿制版」。规则仓库结构已核实为 `00-default/<分类>/*.rules`（Audio-Video / Games / …）+ `00-cgroups.cgroups`。

配置（注意 **package 和 rulesProvider 是两个不同的东西**，这是最容易配错的地方）：

```nix
services.ananicy = {
  enable = true;

  # ① 引擎：ananicy-cpp（CachyOS 用的就是它，不是老的 ananicy）
  package = pkgs.ananicy-cpp;

  # ② 规则来源：CachyOS 官方规则集
  rulesProvider = pkgs.ananicy-rules-cachyos;

  # ③ 可选：覆盖/追加规则（会写成 nixRules.rules）
  # extraRules = [ { name = "my-app"; type = "Game"; } ];
};
```

`services.ananicy` 的完整选项（源码逐条核实）：`enable` / `package` / `rulesProvider` / `settings` / `extraRules` / `extraTypes` / `extraCgroups`。`[核实·源码]`

模块会做这几件事（`nixos/modules/services/misc/ananicy.nix`）：
1. 把 `rulesProvider` 里的规则**复制**到 `/etc/ananicy.d/`（所以规则是只读的、声明式的，不在 home 里）；
2. 自动把 `settings` 的默认值按 **ananicy-cpp** 的口径设好（`apply_nice` / `apply_sched` / `apply_ioclass` / `apply_cgroup` 等全开，`loglevel = "warn"`，`cgroup_realtime_workaround = true`）；
3. 启动名为 **`ananicy-cpp`** 的 systemd 服务（服务名会随 package 变 —— 如果你用 `pkgs.ananicy` 老引擎，服务名是 `ananicy`）。

> [!NOTE]
> **ananicy 与 scx 不冲突，是互补的。** ananicy 调的是**单个进程的 nice / ionice / sched policy / cgroup**；scx 换的是**全局调度算法**。两者可以同时开。
> 唯一真正互斥的是 **`services.system76-scheduler`** —— 它调的是 CFS 内部参数，而 scx 已经把 CFS 整个替换掉了，开了等于没开（见 §14.3）。

#### （2）scx：把「BORE 想要的效果」用用户态调度器拿到

```nix
services.scx = {
  enable = true;
  scheduler = "scx_lavd";   # 游戏/交互向；模块默认是 scx_rustland（保守）
  # extraArgs = [ ];        # 每个调度器参数互不通用，先跑 `scx_lavd --help`
};
```

已核实的关键点（`nixos/modules/services/scheduling/scx.nix`）：

| 事实 | 说明 |
|---|---|
| **硬断言：内核 ≥ 6.12** | 低于此版本构建直接报错，不是静默失败 |
| 有 `ConditionPathIsDirectory = "/sys/kernel/sched_ext"` | 内核不支持时**静默跳过**（服务不启动但不报错）—— 所以你必须自己验一次（见 18.11） |
| `SCX_SCHEDULER_OVERRIDE` / `SCX_FLAGS_OVERRIDE` 环境变量 | **可以在不重建系统的情况下换调度器或换参数**，这是做 A/B 测试最快的方式 |
| 支持 26 个调度器 | 18 个 Rust + 8 个 C 示例；`scx_nest` 属 C 示例（不推荐日常用） |
| 默认内核就支持 | 26.05 默认内核 6.18，`common-config.nix` 里 `SCHED_CLASS_EXT` 自 6.12 起为 `yes` → **不用换内核就能跑 scx** |

> [!TIP]
> **不做 A/B 测试就不要开 scx。** 一行命令切换，用 MangoHud 看 **1% low 帧**（不是平均帧）：
> ```bash
> systemctl set-environment SCX_SCHEDULER_OVERRIDE=scx_bpfland
> sudo systemctl restart scx
> ```
> 切回 `scx_lavd`、`scx_rusty` 各跑同一段场景，再决定留哪个。**别人说好不等于对你好。**

---

### 18.3 内核：别为了「像 CachyOS」换内核；要换就换 zen

#### BORE 拿不到，这是硬事实

| 事实 | 证据 |
|---|---|
| BORE 是 CachyOS 内核的补丁，符号 `CONFIG_SCHED_BORE` | CachyOS `linux-cachyos-rc/config` 第 154 行；CachyOS 变体 `linux-cachyos-bore` / `-hardened` / `-rt-bore` / `-deckify` |
| **nixpkgs 里没有 `linux_cachyos`** | `linux-kernels.nix` + `all-packages.nix` 中 `cachy` 匹配数 **= 0** |
| **`linux_zen` 也不含 BORE** | `zen-kernel` v7.2.9-zen1 的 `kernel/Kconfig.preempt` 里搜 `bore`/`BURST` **零命中**；`kernel/sched/fair.c` 里的 `burst` 是**上游 CFS 的 burst quota**（`cfs_b->burst_time`），不是 BORE |

`[核实·源码]`（以上三条我都直接读了对应仓库的源码文件，不是二手转述）

**结论**：想要真正的 BORE，只能加 overlay / 第三方 flake 去编译 `linux-cachyos` —— 这**超出你「不额外添加仓库」的边界**。所以：**不要在这条路上花时间。**

#### 那要不要换 zen？看这张表

`pkgs.linuxPackages_zen` = **7.2.9-zen1**（26.05 分支）。它到底给你什么，我逐项读了 `zen-kernels.nix`：

| 配置项 | 默认内核 6.18 | `linux_zen` | 对你的意义 |
|---|---|---|---|
| `PREEMPT` | no（配 `PREEMPT_LAZY=yes`） | **yes（强制，`mkOverride 90`）** | 抢占更积极 → 交互延迟更低，代价是吞吐略降 |
| `PREEMPT_LAZY` | yes | **no**（被显式关掉） | 与上面配套 |
| `HZ` | 默认 | **1000** | 调度/定时精度更高 |
| `IOSCHED_BFQ` | `module` | **`yes`（内建）** | 开机即可用 bfq，不需要模块加载 |
| **`NTSYNC`** | **未启用** | **`yes`（内建）** | **这就是 CachyOS 加载 ntsync 模块那件事** —— 见下 |
| `FUTEX` / `FUTEX_PI` | — | yes | Wine/Proton 的 fsync 路径 |
| `ZEN_INTERACTIVE` | — | yes | zen 的交互式调参集合 |
| `DEFAULT_FQ_CODEL` | — | yes | 桌面网络队列算法 |

`[核实·源码]`（`pkgs/os-specific/linux/kernel/zen-kernels.nix` 全文）

> [!IMPORTANT]
> **`linux_zen` 是「不换内核就拿不到的东西」里最值的一项：`NTSYNC` 是编译进去的（`=y`）。**
> CachyOS 靠 `/usr/lib/modules-load.d/ntsync.conf` 加载 `ntsync` 模块；而 NixOS 的**默认内核很可能根本没编这个模块**（`common-config.nix` 里没有 `CONFIG_NTSYNC`，上游默认 `N`）。换到 zen 之后，`/dev/ntsync` 直接存在，**不需要写任何 `boot.kernelModules`**。
> 验证：`ls -l /dev/ntsync`。Proton 侧用 `PROTON_USE_NTSYNC=1`，Wine 侧用 `WINENTSYNC=1`。

**换 zen 的代价**（必读）：

```nix
boot.kernelPackages = pkgs.linuxPackages_zen;
```

- **树外模块必须对新内核重编**：你的 `r8125`（Realtek 2.5G 网卡，见第四章）就是树外模块 → 换内核 = 重新编译 + **失去二进制缓存**（本地编译，慢）。**如果你在用 `r8125`，换内核前先确认能编过，否则会没网。**
- zen 的 `amdgpu` 部分**与默认内核完全一样** —— zen 是调度/延迟补丁，**对 AMD 显卡没有额外收益**。别指望换内核提升帧数。
- `linux_zen` 在 aarch64 上是 `broken`（你是 x86_64，无影响）。

**建议**：先跑默认 6.18 + `services.scx`。**只有当你有具体理由（比如要 ntsync、要 PREEMPT 低延迟）时才换 zen。**

---

### 18.4 sysctl：逐行翻译 CachyOS 的 `70-cachyos-settings.conf`

这是 CachyOS 配置里**最容易抄、收益最确定**的一块。我把它的原始文件逐行读出来后，翻译成 NixOS 写法：

| CachyOS 原值 | NixOS 写法 | 坑 / 说明 |
|---|---|---|
| `vm.swappiness = 100` | `"vm.swappiness" = 100;` | ⚠️ **前提是有 zram**。CachyOS 的 udev 规则在 zram 就绪时还会把它提到 **150**。没有 zram 就设 100 会加剧换页 |
| `vm.vfs_cache_pressure = 50` | `"vm.vfs_cache_pressure" = 50;` | 低风险 |
| `vm.dirty_bytes = 268435456` | `"vm.dirty_bytes" = 268435456;` | 256 MiB 脏页上限；`dirty_bytes` 与 `dirty_ratio` **互斥**（设了一个会清零另一个），NixOS 默认用 ratio |
| `vm.dirty_background_bytes = 67108864` | `"vm.dirty_background_bytes" = 67108864;` | 同上，64 MiB |
| `vm.dirty_writeback_centisecs = 1500` | `"vm.dirty_writeback_centisecs" = 1500;` | 15 秒回写一次（默认 5 秒）→ 更省电、更少 IO 抖动，代价是掉电丢更多数据 |
| `vm.page-cluster = 0` | `"vm.page-cluster" = 0;` | 每次换入 1 页。**配合 zram 才对**（zram 换入便宜）；用物理 swap 反而该调大 |
| `kernel.nmi_watchdog = 0` | `"kernel.nmi_watchdog" = 0;` | 省一点电、少一点抖动。**代价：失去硬锁死检测** |
| `kernel.kptr_restrict = 2` | `"kernel.kptr_restrict" = 2;` | 安全向，可以抄 |
| `kernel.printk = 3 3 3 3` | `"kernel.printk" = "3 3 3 3";` | ⚠️ **是字符串**（NixOS 的 sysctl 接受 bool/int/string，空格分隔的多值只能写字符串） |
| `net.core.netdev_max_backlog = 4096` | `"net.core.netdev_max_backlog" = 4096;` | 低风险 |
| `fs.file-max = 2097152` | `"fs.file-max" = 2097152;` | 低风险 |
| `kernel.sysrq = 1` | `"kernel.sysrq" = 1;` | ⚠️ 这是**放宽**（允许全部 SysRq 功能，方便卡死时 REISUB 重启），与安全默认相反。自己权衡 |
| **`kernel.unprivileged_userns_clone = 1`** | **❌ 不要写** | 这个键是 **Debian/Arch 系的补丁**引入的，**主线内核（NixOS 默认 / zen / xanmod）里不存在**。写了 systemd-sysctl 会报 "No such file or directory"。先 `sysctl -a \| grep userns_clone` 确认 |

可直接粘贴：

```nix
boot.kernel.sysctl = {
  # ── 内存 / IO（CachyOS 70-cachyos-settings.conf 的对应项）──
  "vm.swappiness" = 100;                  # ⚠️ 只在开了 zram 时用这个值
  "vm.vfs_cache_pressure" = 50;
  "vm.dirty_bytes" = 268435456;
  "vm.dirty_background_bytes" = 67108864;
  "vm.dirty_writeback_centisecs" = 1500;
  "vm.page-cluster" = 0;                  # 配合 zram

  # ── 内核行为 ──
  "kernel.nmi_watchdog" = 0;
  "kernel.kptr_restrict" = 2;
  "kernel.printk" = "3 3 3 3";
  # "kernel.sysrq" = 1;                   # 可选：放宽 SysRq（卡死时能 REISUB）

  # ── 网络 / 文件 ──
  "net.core.netdev_max_backlog" = 4096;
  "fs.file-max" = 2097152;

  # ❌ 不要写：主线内核没有这个键
  # "kernel.unprivileged_userns_clone" = 1;
};
```

> [!WARNING]
> **别把 SteamOS 的调优值也一起抄进来。** NixOS **已经**把 `vm.max_map_count` 设为 `1048576`、`fs.inotify.max_user_watches` / `max_user_instances` 设为 `524288`（`config/sysctl.nix`，都是 `mkDefault`）。
> 那些「SteamOS 调优脚本」里的 `vm.max_map_count=2147483642` 在 26.05 上是**多余**的 —— 只有在你实测某个游戏报 `max_map_count` 错误时才需要往上调。

---

### 18.5 udev 规则：CachyOS 的 9 条里，哪几条能抄

CachyOS-Settings 的 `/usr/lib/udev/rules.d/` 共 9 个文件。我逐条读过，分类如下：

| CachyOS 文件 | 能否复刻 | 说明 |
|---|---|---|
| `60-ioschedulers.rules` | ✅ 可抄 | HDD→`bfq`、SATA SSD/eMMC→`mq-deadline`、**NVMe→`kyber`** |
| `50-sata.rules` | ✅ 可抄 | SATA 链路电源管理强制 `max_performance` |
| `69-hdparm.rules` | ✅ 可抄（需改路径） | CachyOS 调 `/usr/bin/hdparm`；NixOS 里必须写 `${pkgs.hdparm}/bin/hdparm` |
| `40-hpet-permissions.rules` | ⚠️ 可抄，收益小 | 把 `rtc0` / `hpet` 归到 `audio` 组 —— 只对 JACK/专业音频有意义 |
| `99-cpu-dma-latency.rules` | ⚠️ 可抄，收益小 | 同上（`cpu_dma_latency` 设备权限） |
| `30-zram.rules` | ⚠️ 部分可抄 | 靠 udev 把 `swappiness` 提到 150 + 关 zswap。NixOS 里更干净的做法是直接用 `zramSwap` + sysctl（见 18.6） |
| `20-audio-pm.rules` | ❌ **抄不了** | 依赖 CachyOS 自研脚本 `/usr/lib/udev/audio-pm-ctl`（不在 nixpkgs）。想复刻得自己写等价脚本 |
| `85-iw-regulatory.rules` | ➖ **N/A** | 无线监管域 —— **你是有线连接**，不需要 |
| `71-nvidia.rules` | ➖ **N/A** | NVIDIA 运行时电源管理 —— 你是 AMD |

可直接粘贴的「可抄部分」：

```nix
services.udev.extraRules = ''
  # ── I/O 调度器（对应 CachyOS 60-ioschedulers.rules）──
  # HDD → bfq
  ACTION=="add|change", KERNEL=="sd[a-z]*", ATTR{queue/rotational}=="1", ATTR{queue/scheduler}="bfq"
  # SATA SSD / eMMC → mq-deadline
  ACTION=="add|change", KERNEL=="sd[a-z]*|mmcblk[0-9]*", ATTR{queue/rotational}=="0", ATTR{queue/scheduler}="mq-deadline"
  # NVMe → kyber
  ACTION=="add|change", KERNEL=="nvme[0-9]*", ATTR{queue/rotational}=="0", ATTR{queue/scheduler}="kyber"

  # ── SATA 链路电源管理（对应 50-sata.rules）──
  ACTION=="add", SUBSYSTEM=="scsi_host", KERNEL=="host*", \
      ATTR{link_power_management_supported}=="1", \
      ATTR{link_power_management_policy}="max_performance"

  # ── 机械盘 hdparm 调优（对应 69-hdparm.rules）──
  # ⚠️ NixOS 没有 /usr/bin/hdparm，必须用 nix store 里的绝对路径
  ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/rotational}=="1", \
      ENV{ID_USB_DRIVER}=="", ENV{ID_BUS}=="ata", \
      RUN+="${pkgs.hdparm}/bin/hdparm -B 254 -S 0 /dev/%k"
'';
```

> [!NOTE]
> **NVMe 该用 `kyber` 还是 `none`？两种说法都对，取决于你在意什么。**
> - CachyOS 选 `kyber`（它是个轻量的多队列调度器，对混合负载有 QoS 保证）；
> - 很多游戏优化指南选 `none`（最短路径，延迟最低，但多进程争抢时没有 QoS）。
>
> 两者都是**合法且经过内核支持**的（NixOS 内核已编入 `MQ_IOSCHED_KYBER=yes`、`MQ_IOSCHED_DEADLINE=yes`、`IOSCHED_BFQ=module`）。**想要哪个就写哪个** —— 别被「必须用 X」的说法绑住。改完用 `cat /sys/block/nvme0n1/queue/scheduler` 看方括号落在哪。

> [!WARNING]
> **`hdparm -B 254` 会关闭磁盘的 APM 省电**，机械盘会更热、更耗电（笔记本上明显）。台式机无所谓，笔记本建议删掉这条。

---

### 18.6 zram、THP、KSM：内存这三块

#### zram：对照 CachyOS 的 `zram-generator.conf`

CachyOS 的原文件：

```ini
[zram0]
compression-algorithm = zstd
zram-size = ram          # ← 100% 物理内存
swap-priority = 100
fs-type = swap
```

NixOS 的对应写法（`zramSwap` 模块，选项已逐条核实）：

```nix
zramSwap = {
  enable = true;
  algorithm = "zstd";        # 默认就是 zstd
  memoryPercent = 75;        # ⚠️ CachyOS 是 100；见下方警告
  priority = 100;            # CachyOS 同值（NixOS 默认只有 5）
  swapDevices = 1;
};
```

| 选项 | NixOS 默认 | CachyOS | 建议 |
|---|---|---|---|
| `algorithm` | `"zstd"` | zstd | 抄，一致 |
| `memoryPercent` | `50` | `ram` = **100** | **别抄 100**，用 50–75 |
| `priority` | `5` | `100` | 抄（让 zram 优先于物理 swap） |
| `swapDevices` | `1` | 1 | 一致 |

> [!WARNING]
> **`zram-size = ram`（100%）在内存紧张的机器上是反效果的。** zram 是**压缩内存**，占用的是真 RAM；压到 100% 时，一旦 zram 里存的是**不可压缩数据**（已压缩的视频、随机数据），实际占用会逼近 1:1，直接把内存吃满 → 触发 OOM。
> CachyOS 敢设 100 是因为它同时配了 OOM 保护和 THP 收缩。**你按 50–75 起步，观察 `zramctl` 的 `DATA`/`COMPR` 列再决定要不要加。**

**关于 zswap**：CachyOS 的 zram udev 规则会**关掉 zswap**（因为 zswap 和 zram 会互相干扰）。NixOS 上你**不需要做这件事** —— 内核的 zswap 默认就是不启用的。验证：`cat /sys/module/zswap/parameters/enabled`（期望 `N`）。

#### THP：CachyOS 的两条 tmpfiles

CachyOS 用 `/usr/lib/tmpfiles.d/thp.conf` 和 `thp-shrinker.conf` 写两个 sysfs 值。NixOS 有现成选项 `systemd.tmpfiles.rules`（`w!` 类型可以写任意路径，包括 sysfs）：

```nix
systemd.tmpfiles.rules = [
  # 对应 CachyOS thp.conf：给用 tcmalloc 的程序改善性能
  "w! /sys/kernel/mm/transparent_hugepage/defrag - - - - defer+madvise"
  # 对应 CachyOS thp-shrinker.conf：内核 6.12+ 才有；默认 511，降到 409
  # 作用：THP 页里超过 80% 是零页就拆掉 → 显著降低 THP=always 下的内存占用
  "w! /sys/kernel/mm/transparent_hugepage/khugepaged/max_ptes_none - - - - 409"
];
```

`[核实·源码]`（`nixos/modules/system/boot/systemd/tmpfiles.nix` 提供 `systemd.tmpfiles.rules`；两个 sysfs 路径与取值来自 CachyOS-Settings 原始文件）

#### KSM：CachyOS 用 uksmd，NixOS 用内核 KSM

- CachyOS 提供 **`uksmd`**（用户态 KSM 管理器，可对不同进程用不同策略）—— **nixpkgs 里没有**（`pkgs/by-name/uk/uksmd` 404）。
- NixOS 有 **`hardware.ksm`** 模块（`nixos/modules/hardware/ksm.nix`，旧名 `hardware.enableKSM` 已重命名）：

```nix
hardware.ksm = {
  enable = true;
  sleep = 100;      # ksmd 扫描间隔（毫秒）；null = 用内核默认
};
```

> [!WARNING]
> **KSM 的代价是实打实的**：它要持续扫描内存页做哈希比对（吃 CPU），而且**页合并本身是侧信道攻击面**（跨进程共享物理页）。它适合「同一份数据被多个 VM/容器重复加载」的场景；**普通桌面 + 游戏的收益很小**。想开就开，但别当成「免费的性能提升」。

---

### 18.7 systemd / limits / journald / timesyncd

| CachyOS 文件 | 内容 | NixOS 写法 | 建议 |
|---|---|---|---|
| `system.conf.d/10-limits.conf` | `DefaultLimitNOFILE=2048:2097152` | `systemd.settings.Manager.DefaultLimitNOFILE = "2048:2097152";` | ✅ 可抄 |
| `user.conf.d/10-limits.conf` | `DefaultLimitNOFILE=1024:1048576` | ❌ **NixOS 无对应选项** | 见下 |
| `system.conf.d/00-timeout.conf` | `DefaultTimeoutStartSec=15s` / `StopSec=10s` | `systemd.settings.Manager.DefaultTimeoutStartSec = "15s";` | ❌ **不要抄**（见下） |
| `journald.conf.d/00-journal-size.conf` | journal 上限 50 MB | `services.journald.extraConfig = "SystemMaxUse=50M";` | ⚠️ 可抄，但 50 MB 很小 |
| `timesyncd.conf.d/10-timesyncd.conf` | Cloudflare + Google NTP | `services.timesyncd.servers = [ "time.cloudflare.com" ];` | ✅ 可抄 |
| `/etc/security/limits.d/20-audio.conf` | `@audio rtprio 99` / `nice -11` | `security.pam.loginLimits = [...]` | ⚠️ 只对专业音频有意义 |
| `user@.service.d/delegate.conf` | `Delegate=cpu cpuset io memory pids` | `systemd.services."user@".serviceConfig.Delegate = [...]` | ⚠️ 先看现状再改 |

```nix
# ── systemd 全局 limits（对应 CachyOS 10-limits.conf）──
systemd.settings.Manager.DefaultLimitNOFILE = "2048:2097152";
# ⚠️ 注意：systemd.extraConfig 在 26.05 已【删除】，必须用 systemd.settings.Manager
#    （源码里是 mkRemovedOptionModule，写了会直接报错让你改）

# ── journal 上限（对应 CachyOS 00-journal-size.conf）──
services.journald.extraConfig = ''
  SystemMaxUse=200M
'';   # CachyOS 是 50M；我建议 200M，见下方说明

# ── NTP（对应 CachyOS 10-timesyncd.conf）──
services.timesyncd.servers = [ "time.cloudflare.com" ];

# ── @audio 实时优先级（对应 CachyOS 20-audio.conf）──
security.pam.loginLimits = [
  { domain = "@audio"; item = "rtprio"; value = "99"; }
  { domain = "@audio"; item = "nice"; value = "-11"; }
];
security.rtkit.enable = true;   # NixOS 默认 false；桌面音频建议开

# ── 把资源委派给用户级服务（对应 CachyOS delegate.conf）──
systemd.services."user@".serviceConfig.Delegate = [ "cpu" "cpuset" "io" "memory" "pids" ];
```

> [!DANGER]
> **`DefaultTimeoutStartSec=15s` 这条千万别抄。** NixOS 的 `nixos-rebuild switch` 会重启大量服务，**慢的单元（数据库、容器、网络）15 秒就会被 systemd 判超时**，导致激活失败或状态不一致。CachyOS 是常规发行版，服务集小；NixOS 的单元依赖图复杂得多。**保持默认（90s）。**

> [!NOTE]
> **`user.conf.d` 那条抄不了**：NixOS 的 `systemd.settings` 只作用于 **system manager**（生成 `/etc/systemd/system.conf`），**没有 user manager 的对应选项**。
> 想复刻得手写 `/etc/systemd/user.conf.d/10-limits.conf`（`environment.etc`）。**这一步我未核实 systemd 的 user.conf.d drop-in 支持范围，标 `[未核实]`** —— 而且对游戏/桌面收益极小，建议直接跳过。

> [!NOTE]
> **journal 50 MB 我改成了 200 MB。** 50 MB 在 NixOS 上尤其危险：`nixos-rebuild` 失败时你要翻 journal 找原因，日志被轮转掉就查不到了。**这个「优化」省的是几 MB 磁盘，代价是排障能力。**

---

### 18.8 你**不该**抄的 CachyOS 设置

这张表比上一张更重要 —— 照抄 CachyOS 会踩的坑都在这里。

| CachyOS 设置 | 为什么你不该抄 |
|---|---|
| `modprobe.d/amdgpu.conf`<br>（`si_support=1 cik_support=1` + 关 radeon） | **只对 GCN 1.0 / 2.x 老卡有意义**。你的卡是新架构，抄了**毫无作用**，而且 `radeon.si_support=0` 在混装老卡时有风险 |
| `modprobe.d/nvidia.conf` | NVIDIA 专用，N/A |
| `modprobe.d/blacklist.conf`<br>（黑名单 `iTCO_wdt` / `sp5100_tco` / `wdat_wdt`） | 抄了能省一点电、少一点抖动，但**代价是失去硬件看门狗**（真锁死时只能硬断电）。**如果你想要，用 `boot.blacklistedKernelModules` 显式写，并且知道自己在放弃什么** |
| `modules-load.d/ntsync.conf` | 前提是内核**有** `ntsync` 模块。NixOS 默认内核很可能没有 → 写了会加载失败。**换 `linux_zen` 后它是内建的，反而不需要这行** |
| `zram-generator.conf` 的 `zram-size = ram` | 见 18.6 的警告，100% 是反效果 |
| `sysctl` 里的 `kernel.unprivileged_userns_clone` | 主线内核没有这个键 |
| `00-timeout.conf` | 见 18.7 的 DANGER 框 |
| `20-audio-pm.rules` | 依赖 CachyOS 自研脚本，抄不了 |
| `/usr/bin/game-performance` | 依赖 `powerprofilesctl launch`（power-profiles-daemon 的 launch 子命令）—— NixOS 可以复刻，但写法不同（见 18.10） |

---

### 18.9 拿不到的（诚实清单）

以下这些**必须**加外部仓库/flake/overlay 才能拿到，**在「不额外添加仓库」的约束下就是拿不到**：

| 拿不到的东西 | 差在哪 | 最近的替代 |
|---|---|---|
| **`linux-cachyos` 内核 / BORE 调度器** | nixpkgs 从未收录；需要编译带补丁的内核 | `scx_lavd`（用户态达成同一目标）+ `linux_zen` |
| BMQ 调度器、POC idle selector | 同上，内核补丁 | `scx_*` |
| **`mesa-git`** | nixpkgs 只有稳定版 `mesa`（`pkgs/development/libraries/mesa`）。`hardware.graphics.package` 可以覆盖，但**只能换成另一个 nixpkgs 里的 mesa**，换不成 git 版 | 稳定 mesa（对 RDNA 卡足够新） |
| **`proton-cachyos`** | 不在 nixpkgs | `pkgs.proton-ge-bin`（GE 是社区最接近的替代） |
| **`uksmd`** | 不在 nixpkgs | `hardware.ksm`（内核 KSM） |
| `cachyos-settings` 包本身、`audio-pm-ctl`、`pci-latency` 脚本 | 不在 nixpkgs | 本文 18.4–18.7 就是**手动复刻它的内容** |
| `scx-scheds`（Arch 包名） | Arch 打包名 | nixpkgs 里叫 `pkgs.scx`（`services.scx` 已内置） |

> [!TIP]
> **注意这个区别**：你拿不到的是「CachyOS 打包的**那一份**」；而它**打包的东西本身**（scx、ananicy-cpp、ananicy 规则）大多是开源且已被 nixpkgs 收录的。
> **唯一真正属于 CachyOS 私有的，只有内核补丁（BORE/BMQ/POC）和几个自研小脚本。**

---

### 18.10 一份可直接粘贴的「CachyOS 近似」模块

新建 `/etc/nixos/cachyos-like.nix`，然后在 `configuration.nix` 的 `imports` 里加上它。

```nix
# /etc/nixos/cachyos-like.nix
# 目标：在不引入任何外部仓库的前提下，用 nixpkgs 原生能力逼近 CachyOS 的优化。
# 每一块都标注了它对应 CachyOS-Settings 的哪个文件。
{ pkgs, lib, ... }:

{
  # ══════════════════════════════════════════════════════════
  # ① 内核：默认 6.18 就够（含 SCHED_CLASS_EXT → 能跑 scx）
  #    想要 NTSYNC / PREEMPT 低延迟 → 换成 zen（代价：树外模块重编）
  # ══════════════════════════════════════════════════════════
  # boot.kernelPackages = pkgs.linuxPackages_zen;   # ← 可选，先别急着开

  # ══════════════════════════════════════════════════════════
  # ② 用户态调度器：对应 CachyOS 的 scx-scheds
  # ══════════════════════════════════════════════════════════
  services.scx = {
    enable = true;
    scheduler = "scx_lavd";        # 游戏/交互向（模块默认是 scx_rustland）
  };

  # ══════════════════════════════════════════════════════════
  # ③ 进程优先级：ananicy-cpp + CachyOS 官方规则集
  # ══════════════════════════════════════════════════════════
  services.ananicy = {
    enable = true;
    package = pkgs.ananicy-cpp;                    # 引擎
    rulesProvider = pkgs.ananicy-rules-cachyos;    # ← CachyOS 官方规则
  };

  # ══════════════════════════════════════════════════════════
  # ④ sysctl：对应 CachyOS 70-cachyos-settings.conf
  # ══════════════════════════════════════════════════════════
  boot.kernel.sysctl = {
    "vm.swappiness" = 100;                # ⚠️ 只在开了 zram 时用
    "vm.vfs_cache_pressure" = 50;
    "vm.dirty_bytes" = 268435456;
    "vm.dirty_background_bytes" = 67108864;
    "vm.dirty_writeback_centisecs" = 1500;
    "vm.page-cluster" = 0;
    "kernel.nmi_watchdog" = 0;
    "kernel.kptr_restrict" = 2;
    "kernel.printk" = "3 3 3 3";
    "net.core.netdev_max_backlog" = 4096;
    "fs.file-max" = 2097152;
  };

  # ══════════════════════════════════════════════════════════
  # ⑤ udev：对应 CachyOS 60-ioschedulers / 50-sata / 69-hdparm
  # ══════════════════════════════════════════════════════════
  services.udev.extraRules = ''
    ACTION=="add|change", KERNEL=="sd[a-z]*", ATTR{queue/rotational}=="1", ATTR{queue/scheduler}="bfq"
    ACTION=="add|change", KERNEL=="sd[a-z]*|mmcblk[0-9]*", ATTR{queue/rotational}=="0", ATTR{queue/scheduler}="mq-deadline"
    ACTION=="add|change", KERNEL=="nvme[0-9]*", ATTR{queue/rotational}=="0", ATTR{queue/scheduler}="kyber"
    ACTION=="add", SUBSYSTEM=="scsi_host", KERNEL=="host*", ATTR{link_power_management_supported}=="1", ATTR{link_power_management_policy}="max_performance"
    ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/rotational}=="1", ENV{ID_USB_DRIVER}=="", ENV{ID_BUS}=="ata", RUN+="${pkgs.hdparm}/bin/hdparm -B 254 -S 0 /dev/%k"
  '';

  # ══════════════════════════════════════════════════════════
  # ⑥ 内存：zram + THP（对应 CachyOS zram-generator.conf / thp*.conf）
  # ══════════════════════════════════════════════════════════
  zramSwap = {
    enable = true;
    algorithm = "zstd";
    memoryPercent = 75;      # CachyOS 是 100，这里保守取 75
    priority = 100;          # CachyOS 同值
  };

  systemd.tmpfiles.rules = [
    "w! /sys/kernel/mm/transparent_hugepage/defrag - - - - defer+madvise"
    "w! /sys/kernel/mm/transparent_hugepage/khugepaged/max_ptes_none - - - - 409"
  ];

  # hardware.ksm.enable = true;   # 可选：内核 KSM（替代 uksmd）。收益小、有代价

  # ══════════════════════════════════════════════════════════
  # ⑦ systemd / limits / journald / 音频
  # ══════════════════════════════════════════════════════════
  systemd.settings.Manager.DefaultLimitNOFILE = "2048:2097152";
  services.journald.extraConfig = "SystemMaxUse=200M";
  services.timesyncd.servers = [ "time.cloudflare.com" ];

  security.pam.loginLimits = [
    { domain = "@audio"; item = "rtprio"; value = "99"; }
    { domain = "@audio"; item = "nice"; value = "-11"; }
  ];
  security.rtkit.enable = true;

  systemd.services."user@".serviceConfig.Delegate = [ "cpu" "cpuset" "io" "memory" "pids" ];

  # ══════════════════════════════════════════════════════════
  # ⑧ 游戏栈：对应 CachyOS 的 proton-cachyos / game-performance
  # ══════════════════════════════════════════════════════════
  programs.steam.extraCompatPackages = [ pkgs.proton-ge-bin ];
  programs.gamemode.enable = true;
  programs.gamescope = {
    enable = true;
    capSysNice = true;        # 对应 CachyOS 给 gamescope 的 cap_sys_nice
  };

  # IRQ 亲和性（对应 CachyOS 的 pci-latency 那类思路；台式机收益小）
  services.irqbalance.enable = true;

  # ══════════════════════════════════════════════════════════
  # ⑨ 「game-performance」等价物：启动游戏时切 performance 电源档
  #    对应 CachyOS 的 /usr/bin/game-performance（它用 powerprofilesctl launch）
  #    用法：在 Steam 启动项里写  game-performance %command%
  #    前提：services.power-profiles-daemon.enable = true（GNOME/Plasma6 自动开）
  # ══════════════════════════════════════════════════════════

  # ⚠️ 注意：整个文件里 environment.systemPackages 只能出现【一次】
  #    （Nix 的属性集不允许重复定义同名属性；下面把所有包合并在一起）
  environment.systemPackages = with pkgs; [
    hdparm            # 上面 udev 规则要用到它的绝对路径
    mangohud          # 看 1% low 帧
    goverlay
    irqbalance
    (writeShellScriptBin "game-performance" ''
      exec systemd-inhibit --why "game-performance is running" \
        ${power-profiles-daemon}/bin/powerprofilesctl launch -p performance -- "$@"
    '')
  ];
}
```

> [!NOTE]
> 上面 ⑨ 的 `game-performance` 是**行为等价**的简化版：CachyOS 原脚本还会先检测 `powerprofilesctl list` 里有没有 `performance:` 档（没有就直接 exec），并且支持 `GAME_PERFORMANCE_SCREENSAVER_ON=1` 跳过抑制屏保。要完全一致就自己补这两个判断。
> 前提是 `services.power-profiles-daemon.enable = true`（GNOME / Plasma6 会自动开，见第三章）。

---

### 18.11 验收：一条一条确认「真的生效了」

```bash
# ── ① scx 是否真的在跑 ─────────────────────────────────
# 关键：内核不支持时服务会「静默跳过」，不报错。所以必须验。
ls /sys/kernel/sched_ext/                        # 目录不存在 = 内核不支持 sched-ext
cat /sys/kernel/sched_ext/root/ops               # 期望看到 scx_lavd（当前生效的调度器名）
systemctl status scx                             # active (running) 才算成功

# ── ② ananicy-cpp + CachyOS 规则 ──────────────────────
systemctl status ananicy-cpp
ls /etc/ananicy.d/                               # 期望看到 00-default/ 目录和 00-cgroups.cgroups
ls /etc/ananicy.d/00-default/ | head             # 期望看到 Audio-Video/ Games/ 等分类
journalctl -u ananicy-cpp -n 20                  # 看有没有规则解析错误

# ── ③ I/O 调度器 ─────────────────────────────────────
for d in /sys/block/*/queue/scheduler; do echo "$d: $(cat $d)"; done
# 方括号标出的是当前生效值，例如： [kyber] mq-deadline bfq none

# ── ④ sysctl ─────────────────────────────────────────
sysctl vm.swappiness vm.page-cluster vm.dirty_bytes kernel.nmi_watchdog kernel.printk
# 注意：如果某个键报 "cannot read"，说明它在这台内核上不存在（不要盲写）

# ── ⑤ zram ───────────────────────────────────────────
zramctl
# 期望看到 zram0，ALGORITHM=zstd，DATA/COMPR 有数值（没数值说明还没被用过）
cat /sys/module/zswap/parameters/enabled          # 期望 N（zswap 不该和 zram 抢）

# ── ⑥ THP ────────────────────────────────────────────
cat /sys/kernel/mm/transparent_hugepage/defrag     # 期望 [defer+madvise]
cat /sys/kernel/mm/transparent_hugepage/khugepaged/max_ptes_none   # 期望 409

# ── ⑦ NTSYNC（只有换到 zen 才可能有）──────────────────
ls -l /dev/ntsync                                 # 存在 = 可用
modinfo ntsync 2>/dev/null | head -3              # 默认内核上大概率 "not found"

# ── ⑧ limits ─────────────────────────────────────────
systemctl show -p DefaultLimitNOFILE              # 期望 2048:2097152

# ── ⑨ 整体 ───────────────────────────────────────────
nixos-rebuild dry-build                           # 永远先干跑
```

> [!TIP]
> **最值得花 2 分钟做的一件事**：`cat /sys/kernel/sched_ext/root/ops`。
> 有输出 = 你的内核支持 sched-ext，**18.2 的 scx 那套能完整用上**；没输出 = 这部分对你这台机器不存在，可以整段跳过，省下所有折腾时间。

---

---

## 十九、三套管理方案的正确定位：configuration.nix / flake / home-manager

这三个名字被放在一起比较，本身就是一个**范畴错误**。它们不是三种"选一个"的方案，而是**三个不同层次的东西**：

```text
┌─────────────────────────────────────────────┐
│  home-manager   管「你这个用户」的东西        │  ← 用户层，独立项目
├─────────────────────────────────────────────┤
│  configuration.nix  管「这台机器」的东西      │  ← 系统层，NixOS 模块
├─────────────────────────────────────────────┤
│  flake.nix     管「上面两者的输入与锁版本」    │  ← 依赖层，不是配置语法
└─────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **`flake` 不是 `configuration.nix` 的替代品。** flake 是一个**输入锁定与依赖分发机制**；`configuration.nix` 是**系统配置的正文**。一个 flake 里通常仍然有一个 `configuration.nix`。真正与 `configuration.nix` 构成"二选一"关系的是 **Home Manager（用户层）**。

### 19.1 Home Manager 不在 nixpkgs 里——这一条决定了它的所有行为

很多教程默认 Home Manager 是 NixOS 的一部分。**它不是。**

我在 nixpkgs `nixos-26.05` 上做了两项核实：`[核实·源码]`

```bash
curl -s https://raw.githubusercontent.com/NixOS/nixpkgs/nixos-26.05/nixos/modules/module-list.nix | grep -i home-manager
# → 无任何输出（匹配数 0）

curl -s https://raw.githubusercontent.com/NixOS/nixpkgs/nixos-26.05/pkgs/top-level/all-packages.nix | grep -i home-manager
# → 只有一行注释提到 "A NixOS/home-manager/arion/... module"
```

Home Manager 是 **`nix-community` 下的独立仓库**，有自己的 release 分支与自己的 flake。`[仓库]` https://github.com/nix-community/home-manager

我核实了它的分支存在性：`release-25.11`、`release-26.05`、`master` 三个 `flake.nix` 均返回 200。`[核实·源码]`

由此推出四个**实务后果**（这是本节的重点）：

| 后果 | 说明 |
|---|---|
| **它可以完全独立于 NixOS 运行** | Home Manager 有 standalone 模式（`home-manager switch` 直接跑，不经 `nixos-rebuild`），**不需要 root**。这也是它能装在 Ubuntu/macOS 上的原因 |
| **它有自己独立的版本兼容矩阵** | HM 的 release 分支要与 nixpkgs 的 release 分支配对。`release-26.05` 配 `nixos-26.05` 是官方配对；不配对会踩模块选项不存在的错 |
| **它不是 NixOS 的"官方组件"** | 出问题不会在 NixOS release notes 里；它的 breakage 由 nix-community 决定 |
| **它不能做需要 root 的事** | 装内核模块、开防火墙端口、管 systemd 系统服务——这些只有 `configuration.nix` 能做 |

### 19.2 能力域对照：谁能管什么

| 对象 | `configuration.nix` | `flake.nix` | Home Manager |
|---|---|---|---|
| 内核、显卡驱动、固件 (`boot.*` `hardware.*`) | ✅ **唯一** | ❌ 不是写配置的地方 | ❌ 不能 |
| systemd **系统**服务（sshd / firewall） | ✅ **唯一** | ❌ | ❌ 不能 |
| systemd **用户**服务 | ⚠️ 可行但要手写 `systemd.user.services.<n>.unit`，很笨 | ❌ | ✅ **正路**（`systemd.user.services.<n>` 一等公民） |
| 用户级 dconf / gsettings（GNOME/KDE 设置） | ⚠️ 可写但绕 | ❌ | ✅ **正路**（`dconf.settings`） |
| Shell / zsh / fzf 主题 | ⚠️ 可以但会污染全系统 | ❌ | ✅ **正路**（`programs.zsh` 等） |
| git / ssh / neovim 配置 | ⚠️ 系统级，所有用户共享 | ❌ | ✅ **正路**（`programs.git`） |
| Flatpak / Steam / 桌面集成 | ✅ **唯一**（见第七、八章） | ❌ | ❌ 不能 |
| **锁定软件版本 / pin nixpkgs** | ❌ channel 粒度，做不到"同一系统两套 nixpkgs" | ✅ **唯一**（`inputs.*` + `flake.lock`） | 有自己的 `flake.lock` |
| 同一份 home 配置跨机器同步 | ❌ | — | ✅ **这正是它的招牌**（含非 NixOS 的 Linux/macOS） |
| 免 root 自主变更 | ❌ 改系统配置必须 root | — | ✅ `home-manager switch` 不需要 root |

> [!WARNING]
> **`environment.systemPackages` 和 `home.packages` 都写同一个包 = 装两遍。** Nix 会为两个 profile 各建一份，`/nix/store` 里出现两个不同 store path，浪费空间且升级时容易只升一边。**这是混合方案最常见的浪费来源**，裁决表见 §19.5。

### 19.3 flake 到底是什么：它解决的是"别人怎么拿到你这份配置"

`configuration.nix` 单独存在时，**它是自包含的**——你把 `/etc/nixos/configuration.nix` 拷到另一台机器 `nixos-rebuild switch` 就能用（前提是那台机器能解析它）。

flake 解决的是另外三件事：

1. **输入的显式声明**：你依赖的每个 nixpkgs / overlay / 模块从哪来，写死在 `inputs` 里，而不是靠机器上的 channel 或 `NIX_PATH`。
2. **可复现锁定**：`flake.lock` 记录每个 input 的**精确 commit + narHash**。任何人拿你的 flake 重建，得到**逐字节相同**的结果。
3. **可分发**：`nixosConfigurations.<host>` 让"装上这台机器的完整配置"变成 `nixos-rebuild switch --flake .#<host>` 一条命令。

> [!NOTE]
> **flake 仍然是实验特性。** 在 26.05 上依然如此——`/etc/nixos/flake.nix` 必须是 **git 仓库里已 `git add` 的文件**，否则 `nixos-rebuild switch --flake .` 会直接报 "path does not exist in flake"。这是第 10 章已记的坑，这里重申因为它决定了你的目录组织方式。

**给 agent 的视角**：flake.lock 是纯文本 JSON，**是 LLM 最容易读、最容易改、也最容易搞坏的东西**。让 hermes 帮你做 `nix flake update` 的**提议**很安全，但让它直接 commit 并 `switch` 就是在赌。

### 19.4 三种落地形态的实测差异

| 形态 | 目录 | 语法 | 升级命令 | 适合谁 |
|---|---|---|---|---|
| **A. 纯 `configuration.nix` + channels** | `/etc/nixos/configuration.nix` | NixOS 模块 | `sudo nix-channel --update && sudo nixos-rebuild switch` | 初学者、单机、不想碰 git |
| **B. `configuration.nix` + Home Manager 作为 NixOS 模块** | `/etc/nixos/`，HM 从 flake 来 | 混合 | `sudo nixos-rebuild switch`（一次升两边） | 想要单命令、能接受 root 操作的 |
| **C. flake + HM standalone** | `~/dotfiles/` 或 `/etc/nixos/` + git | Flake | `nix flake update && nixos-rebuild switch --flake .#host` 与 `home-manager switch` 分两条 | **多机同步 / 不想为改桌面设置而 root / 要把 home 配置带到非 NixOS 机器** |

> [!TIP]
> **你的情况（AMD 桌面 + 中文 + Steam + vibe coding + 不想让 hermes 拿 root）指向形态 C 的变体：flake 管系统，HM 管用户层，hermes 装在家目录由 HM 托管。** 具体裁决见 §21.12。

### 19.5 到底哪些放 system、哪些放 home：按"影响半径"裁决

不要按"包的类型"分，要按**改坏了谁受影响**分：

```text
改坏了会影响 →  系统层 configuration.nix
  ├─ 开机失败 / 没网 / 没显卡驱动
  ├─ 所有用户都能看到的 PATH 和环境变量
  └─ Steam / Flatpak / 输入法（这些必须系统层，见第五～八章）

改坏了只会影响 →  用户层 Home Manager
  ├─ 你的 shell、git、编辑器、配色
  ├─ 你的 agent（hermes / openclaw / codex）与它的配置、凭据、服务
  └─ 你的 dconf / gsettings 桌面偏好
```

**明确必须留在 `configuration.nix` 的**（HM 做不到，别挣扎）：

```nix
# 本指南前面章节的全部内容都属于这里
boot.kernelPackages = pkgs.linuxPackages;            # 内核（第十四章）
hardware.graphics.enable = true;                     # AMD（第三章）
hardware.cpu.amd.updateMicrocode = true;             # 微码
services.udev.extraRules = ''...'';                  # I/O 调度（第十四章）
i18n.inputMethod.enable = true;                      # 中文输入（第五章）
fonts.packages = [ ... ];                            # 字体
services.flatpak.enable = true;                      # Flatpak（第七章）
programs.steam.enable = true;                        # Steam（第八章）
users.users.<name>.linger = true;                    # ★ hermes 用户服务必需
programs.nix-ld.enable = true;                       # nix-ld（第十五、十七章）
```

**可以且建议搬到 Home Manager 的**：

```nix
# home.nix
home.packages = with pkgs; [ ripgrep fd fzf bat eza zoxide jq gh ];
programs.git = { enable = true; userName = "..."; userEmail = "..."; };
programs.zsh.enable = true;
dconf.settings = {
  "org/gnome/desktop/interface" = { color-scheme = "prefer-dark"; };
  "org/gnome/shell" = { enabled-extensions = [ "..." ]; };   # 第六章的 GNOME 扩展激活
};
systemd.user.services.hermes-agent = { ... };        # 第二十一章
home.sessionPath = [ "$HOME/.npm-global/bin" ];      # ★ 第十五章的 npm prefix
```

> [!DANGER]
> **曾经记录过的一条重要警告，在此重申并给出原因**：`environment.sessionVariables.PATH = "..."` 是**覆盖**而不是**追加**系统 PATH。在 `configuration.nix` 里写它会直接把 `/run/current-system/sw/bin` 等关键路径挤掉，表现为"装好的命令突然找不到"。要加 PATH 就用 shell rc 文件，或者 Home Manager 的 `home.sessionPath`。

### 19.6 Home Manager 装"多数软件"：好处与代价（你直接问的）

先给结论：**HM 装得多，好处是真实的，代价也是真实的。建议混合比例约 70/30（用户层 / 系统层），而不是 100% HM。**

#### 好处（按对你这个场景的价值排序）

1. **不需要 root。** `home-manager switch` 一条命令自己就能改完。这直接支撑你的约束："hermes 不要做成 root 服务"——HM 是官方为"一个人的 agent"设计的运行形态（`[官方]` 见 §21.3）。
2. **用户级回滚。** HM 有自己的 generation，`home-manager generations` 可以单独回退，**不会把系统带回起不来的状态**。对"让 agent 大胆试"很有价值。
3. **与 NixOS 版本解耦。** 系统停在 26.05 等 LTS，home 层照样可以用较新的 HM release。
4. **同一份 home 配置可带到非 NixOS。** HM 支持 Linux（非 NixOS）与 macOS。你的 agent 凭据、skills、shell 配置不用重写第二份。
5. **`dconf.settings` 是 GNOME/KDE 唯一舒服的声明式入口。** 本指南第六章的 GNOME 扩展默认不激活问题，在 HM 里是 `dconf.settings."org/gnome/shell".enabled-extensions`，比在系统层用 `environment.etc` 干净得多。

#### 代价（这些才是决定你是否全 HM 的东西）

| # | 代价 | 具体表现 |
|---|---|---|
| 1 | **两份包管理的心智负担** | 每个包都要先问"放系统还是放 home？"——这就是上表的裁决成本，会长期消耗注意力 |
| 2 | **重复安装 = 双倍空间** | 同一个包在两边都写，`/nix/store` 出现两份 profile 条目；`nix store du` 会变大，gc 压力上升 |
| 3 | **profile 数量翻倍** | 见 §A.9 的 `nix-env --list-generations`：每台机器每个用户多一串 generation，`nix-collect-garbage` 日志变长 |
| 4 | **部分模块只有系统层有** | Flatpak、Steam、内核、显卡、固件、flatpak 远端、systemd 系统服务——**这些 HM 一律做不了**。所以 100% HM 从一开始就不可能 |
| 5 | **flake 输入多一个** | `home-manager` input 也要锁、也要 `update`。而 Hermes 自己也拉一个 HM（见 §21.4），**两个 HM input 容易漂** |
| 6 | **双通道排错** | `nixos-rebuild` 报错和 `home-manager switch` 报错的栈不一样，agent 或你都要理解两套 |
| 7 | **system PATH vs home PATH 的先后** | HM 的 `home.sessionPath` 与 `environment.systemPackages` 的 PATH 合并顺序不总是符合直觉，偶发"命令解析到 home 那份但它依赖系统库" |
| 8 | **HM 不能用 root 也能算缺点** | 需要通过 sudo 的（比如某些 `udev` 规则、`setcap`）HM 就是做不了，只能回系统层 |

> [!IMPORTANT]
> **第 2 条和 5 条是真正的隐藏税。** 第 2 条会慢慢吃掉磁盘，第 5 条会在某次 `nix flake update` 后突然让你整个 home 配置打不开（因为 HM 的模块签名变了）。**对策：HM input 与 nixpkgs input 用同一个 ref，且 Hermes 的 HM follow 你的 HM**（§21.4 给了具体写法）。

### 19.7 一页裁决表

| 我想…… | 用哪个 |
|---|---|
| 开机、驱动、内核、固件、网络 | `configuration.nix`（唯一） |
| 输入法、字体、Flatpak、Steam | `configuration.nix`（唯一） |
| 让命令全局可用 | `environment.systemPackages` |
| 只为我自己装 CLI / 编辑器 | **Home Manager** `home.packages` |
| 我的 git / ssh / shell / neovim 配置 | **Home Manager** `programs.*` |
| GNOME/KDE 的桌面偏好、扩展开关 | **Home Manager** `dconf.settings` |
| 跑一个我自己的常驻服务（agent） | **Home Manager** `systemd.user.services` + 系统层 `users.users.<n>.linger = true` |
| 锁住版本、跨机器同步 | **flake**（`inputs` + `flake.lock`） |
| 只让某个包用 unstable | **flake**（第二十章） |

---

## 二十、flake 进阶：多 nixpkgs 输入、overlay 与「只让某个包用 unstable」

第十九章说"flake 是依赖层"。这一章讲**依赖层的实操**——尤其是你最常遇到的那个需求：**系统整体稳在 26.05，但某一个包想用 unstable 的新版本。**

### 20.1 为什么不能"直接在 configuration.nix 里装 unstable"

新手最常见的写法是：

```nix
# ❌ 行不通的直觉写法
environment.systemPackages = [ pkgs.unstable.ripgrep ];
```

`pkgs` 里**没有** `unstable` 这个属性。一个 NixOS 配置在求值时，`pkgs` 这个集合**只来自一个 nixpkgs 实例**——你在 `nixosSystem` 里传进去的那一个。`pkgs.unstable.foo` 报的是 `attribute 'unstable' missing`。

> [!IMPORTANT]
> **「`pkgs.unstable` 写不出来」不等于「没有 flake 就做不到两套 nixpkgs 并存」。**
>
> 这两件事常被混为一谈。真实情况是：
>
> - **flake 只是让「两套 nixpkgs 并存」变得最顺手**（`inputs` 里显式声明两个，各自导出一个 `pkgs` 集合）。
> - **不用 flake 也能做到** —— 在 `configuration.nix` 里用 `import <nixos-unstable> {}`（channel）、`builtins.fetchTarball`、或 `builtins.fetchGit` + 钉死 `rev`，都能在同一个求值里持有第二份 nixpkgs。**唯一的差别是「谁来管那个版本号」**：flake 用 `flake.lock` 自动管，另外三条路要你手工管。
>
> 详见 **§20.5**（本节修正了 v1.0–v1.4 那句过宽的「唯一的位置是 flake」）。

### 20.2 最小可用写法：加一个 unstable input + overlay

```nix
# /etc/nixos/flake.nix
{
  description = "My NixOS config";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";

    home-manager.url = "github:nix-community/home-manager/release-26.05";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";   # ★ 关键，见 §20.6
  };

  outputs = { self, nixpkgs, nixpkgs-unstable, home-manager, ... }@inputs:
    let
      system = "x86_64-linux";

      # 一个"覆盖过"的 pkgs：在稳定 pkgs 之上，把 unstable 的包挂进来
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
        overlays = [
          # ★ 把 unstable 整个集合挂在 pkgs.unstable 下（按需取用）
          (final: prev: {
            unstable = import nixpkgs-unstable {
              inherit system;
              config.allowUnfree = true;
            };
          })
        ];
      };
    in
    {
      nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
        inherit system;
        modules = [
          ./configuration.nix
          home-manager.nixosModules.home-manager
        ];
        specialArgs = { inherit inputs; };
      };
    };
}
```

然后在 `configuration.nix` 里就能这样写：

```nix
{ pkgs, ... }: {
  # 只这一个包用 unstable
  environment.systemPackages = [ pkgs.unstable.ripgrep ];
}
```

> [!TIP]
> **`pkgs.unstable` 这种"整包集挂载"是最省心的做法。** 另一种做法是**逐包替换**（overlay 里只覆盖 `ripgrep = nixpkgs-unstable.legacyPackages.${system}.ripgrep;`），好处是不会误用 unstable 的依赖树，坏处是每加一个包都要改 overlay。**单机自用推荐整包集挂载**，因为它的失败模式更容易理解。

### 20.3 逐包替换：更可控，但更容易踩依赖错配

```nix
# overlay 里逐包覆盖
(final: prev: {
  ripgrep = nixpkgs-unstable.legacyPackages.${prev.stdenv.hostPlatform.system}.ripgrep;
  neovim  = nixpkgs-unstable.legacyPackages.${prev.stdenv.hostPlatform.system}.neovim;
})
```

> [!WARNING]
> **逐包替换有"依赖树混血"的风险。** unstable 的 `neovim` 可能链接 unstable 的 `libuv`、`lua5_1`，而系统里其它包用 26.05 的那份。两者在 `/nix/store` 里是**不同的 store path**，所以**通常不会直接冲突**（这正是 Nix 的设计），但会导致：
> - closure 变大（两份 `libuv`、两份 `lua`）；
> - 偶发 ABI 层面的怪问题（少见，但存在）；
> - 更常见的：unstable 包需要比 26.05 更新的 `glibc`，于是它把 unstable 的 `glibc` 也拉进来 → **两份 glibc**。
>
> **用整包集挂载（`pkgs.unstable.*`）反而更干净**，因为那一份包和它自己的依赖是自洽的。

### 20.4 只让某个包用 unstable 的"第三种写法"：`legacyPackages` 直取

不想要 overlay 的话，可以直接在模块里取：

```nix
{ pkgs, inputs, ... }:
let
  unstable = inputs.nixpkgs-unstable.legacyPackages.${pkgs.stdenv.hostPlatform.system};
in {
  environment.systemPackages = [ unstable.ripgrep ];
}
```

前提是 `specialArgs = { inherit inputs; }`（见 §20.2 的 `nixosSystem`）。这是**改动面最小**的做法——不动 `pkgs`，只在需要的那一行取。

| 写法 | 改动面 | 适合 |
|---|---|---|
| overlay 挂 `pkgs.unstable` | 中（一次配好，全局可用） | 你会经常混用 unstable |
| overlay 逐包覆盖 | 中 | 只有 1–2 个包，且你想让它们"看起来就是 pkgs 的一部分" |
| `legacyPackages` 直取 | **最小** | 临时试一个包；不想污染 `pkgs` |
| **`_module.args.pkgsUnstable`** | 中 | ✅ **本指南推荐**，见下方 §20.4.1 |

#### 20.4.1 官方论坛不推荐 overlay 路线（本指南 v1.5 新增）

上面三种写法里，**overlay 那两种官方论坛明确不推荐**。原话：

> 「我个人反对这个 overlay 方案，因为为此用 overlay 完全没必要，而且很可能拖慢 eval。」

出处：[Discourse · Mixing stable and unstable packages on flake-based NixOS system](https://discourse.nixos.org/t/mixing-stable-and-unstable-packages-on-flake-based-nixos-system/50351) `[官方论坛]`

**推荐的写法是 `_module.args`** —— 它不碰 `pkgs`，只把 unstable 注册成一个「额外参数」，**只为真正用到它的模块求值**：

```nix
# configuration.nix
{ config, pkgs, inputs, lib, ... }:
let
  system = pkgs.stdenv.hostPlatform.system;
  unstable = import inputs.nixpkgs-unstable {
    inherit system;
    inherit (config.nixpkgs) config;   # 继承 allowUnfree 等
  };
in
{
  _module.args.pkgsUnstable = unstable;   # 之后任何模块都能用 pkgsUnstable
  environment.systemPackages = [ unstable.firefox ];
}
```

| 写法 | eval 开销 | 官方态度 |
|---|---|---|
| overlay 挂 `pkgs.unstable` | 较大（整个 `pkgs` 被重建） | ❌ 不推荐 |
| overlay 逐包覆盖 | 中 | ⚠️ 可用但易依赖错配 |
| `legacyPackages` 直取 | 小 | ✅ 可用 |
| **`_module.args.pkgsUnstable`** | **小**（按需求值） | ✅ **推荐** |

**为什么 overlay 更慢**：overlay 的语义是「重建 `pkgs` 这个集合」，Nix 必须把整个 fixpoint 重算一遍；而 `_module.args` 只是把一个已经算好的集合**挂到模块参数上**，谁用谁求值。

### 20.5 不用 flake 也能做到吗？—— 能，有三条路（本指南 v1.5 新增）

**§20.1 那句「唯一的位置是 flake」是过宽的。** 事实是：**不引入 flake，只用 `configuration.nix`，同样能拿到第二份 nixpkgs。** 三条路，锁定程度递增。

#### 路 A：channel（最简单，完全不锁）

```bash
sudo nix-channel --add https://nixos.org/channels/nixos-unstable nixos-unstable
sudo nix-channel --update
```

```nix
# configuration.nix
let
  unstable = import <nixos-unstable> { config.allowUnfree = true; };
in {
  environment.systemPackages = [ unstable.proton-ge-bin ];
}
```

#### 路 B：`builtins.fetchTarball`（不碰 channel、不建 flake）

```nix
{ config, pkgs, lib, ... }:
let
  unstableSrc = builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz";
    # sha256 = "...";   # 建议加：不加则每次求值可能重下，且不可复现
  };
  unstable = import unstableSrc {
    inherit (pkgs.stdenv.hostPlatform) system;
    inherit (config.nixpkgs) config;
  };
in {
  hardware.graphics.package   = unstable.mesa;
  hardware.graphics.package32 = unstable.pkgsi686Linux.mesa;
  environment.systemPackages = [ unstable.proton-ge-bin unstable.gamescope ];
}
```

取 hash：`nix-prefetch-url --unpack https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz`

#### 路 C：`builtins.fetchGit` + 钉死 `rev`（纯 `configuration.nix` 的「准锁定」）

```nix
let
  unstable = import (builtins.fetchGit {
    url = "https://github.com/NixOS/nixpkgs";
    ref = "refs/heads/nixos-unstable";
    rev = "0000000000000000000000000000000000000000";   # ← 钉死一个 commit
  }) {
    inherit (pkgs.stdenv.hostPlatform) system;
    inherit (config.nixpkgs) config;
  };
in { /* 同上 */ }
```

`fetchGit` 带 `rev` 时 Nix 会校验取到的 commit 与 `rev` 一致，**这就是「手工锁」**。

> [!WARNING]
> **把 `mesa` 单独换成 unstable 是有风险的 —— 见 §32.6。**
>
> **官方警告**：OpenCL / Vulkan 用 **`dlopen`** 加载 runtime，**不受 Nix 构建期依赖追踪保护**。loader 与 runtime 来自不同 nixpkgs → glibc 符号缺失 → **loader 不报错**。
>
> **如果你要滚图形栈**：把 `mesa` + `vulkan-loader` + `libdrm` + `libva` **一起**滚（同源）；或者干脆不滚图形栈，改用 **Flatpak 应用**（自带 runtime）。
>
> **只滚一个组件的典型症状**：`vulkaninfo` 里出现 `llvmpipe` / `lavapipe`（= CPU 软渲染），或 `clinfo` 报 `Number of platforms 0`。

#### 四条路对照

| 路 | 需要 channel？ | 需要 flake？ | 锁版本？ | 日常升级 | 适合 |
|---|---|---|---|---|---|
| **A** channel | ✅ | ❌ | ❌ 完全不锁 | 2 步（`--update` + rebuild） | 临时救急 |
| **B** `fetchTarball` | ❌ | ❌ | ⚠️ 加 `sha256` 才锁 | 2 步（**手工查 hash** + rebuild） | 不想碰 channel/flake |
| **C** `fetchGit` + `rev` | ❌ | ❌ | ✅ 手工锁 | 2 步（**手工查 rev** + rebuild） | 要锁定但拒绝 flake |
| **D** flake | ❌ | ✅ | ✅ `flake.lock` | 2 步（`nix flake update` + rebuild） | **长期滚动组件（推荐）** |

> [!IMPORTANT]
> **看清这张表的本质：B/C 的「日常升级」和 D 一样是 2 步，差别只在第 1 步是「你手工改 hash/rev」还是「`nix flake update` 替你改 `flake.lock`」。**
>
> **flake 并没有让升级变简单，它只是把「手工锁」自动化了。** 理解了这一点，你就理解了 flake 在这个场景下的真实价值 —— 以及为什么「不想引入 flake」时，B/C 是完全可以接受的折中。

> [!WARNING]
> **`nixos-unstable.tar.gz` 是一个移动目标。** 它指向 unstable 分支的当前 HEAD，不加 `sha256` 时每次求值都可能拉到不同内容 —— 这等于「用 fetchTarball 实现了 channel 的不锁行为」。**要可复现就必须钉死到具体 commit。**

**⚠️ 内核提醒（与 `nixos-ops-guide.md` §6.0/§6.4 一致）**：无论哪条路，**都不要写 `unstable.linuxPackages_latest`**。2026-10-12 实测，`nixos-26.05` 的 `pkgs.linuxPackages_latest` 已经是 **7.2.9**，与 `nixos-unstable` 的 **7.2.9** 逐字相同（两分支 `kernels-org.json` 完全一致）。纯 AMD 用户直接：

```nix
boot.kernelPackages = pkgs.linuxPackages_latest;   # 26.05 上 = 7.2.9，跟基座走
```

**这一行属于基座 `pkgs`，不跟 unstable。** 详见 `nixos-ops-guide.md` 第六章。

### 20.6 `follows`：flake 里最容易搞错的一行

`follows` 决定"**子 input 用哪个 nixpkgs**"。

```nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  home-manager.url = "github:nix-community/home-manager/release-26.05";
  home-manager.inputs.nixpkgs.follows = "nixpkgs";   # ← 这一行
};
```

**不写这一行会发生什么**：home-manager 会自己拉一个 nixpkgs（它的 release 分支声明的那个 commit），于是你的系统里出现**两个 nixpkgs**：

- 你写的 `pkgs.ripgrep` 来自 26.05 那份；
- home-manager 的 `pkgs.ripgrep`（`home.packages` 里的）来自**它自己那份**。

结果是同一个包在 `/nix/store` 里两份，**且版本可能不同**。这是"我明明在两边写了同一个版本，为什么装出两个"的根因。

> [!IMPORTANT]
> **规则：任何"提供 NixOS / HM 模块的第三方 flake"，其 `nixpkgs` input 都应该 `follows` 你自己的 `nixpkgs`。** 例外只有一个——**那个 flake 明确要求某个 nixpkgs 版本**（例如它用了新版才有的函数）。这时不 follow 反而正确。判断方法：不 follow 之后 `nixos-rebuild dry-build` 是否报"attribute missing"。第二十一章的 Hermes / OpenClaw 都属于"应该 follow"的类型。

### 20.7 目录组织：flakes 的三种放法

| 放法 | 结构 | 评价 |
|---|---|---|
| **A. `/etc/nixos/` 直接放 flake** | `/etc/nixos/flake.nix` + `configuration.nix` | ✅ 最省事，`nixos-rebuild switch --flake /etc/nixos#myhost` 即可。**缺点是 `/etc/nixos` 归 root**，你改配置要 sudo |
| **B. `~/nixos-config/` 放 flake，`/etc/nixos` 只留一个软链** | `~/nixos-config/`（git 仓库）→ `/etc/nixos/flake.nix` 软链过去 | ✅✅ **推荐**。你免 sudo 改配置、免 sudo git commit；`nixos-rebuild` 仍然照常 |
| **C. 多机：一个 flake 多个 `nixosConfigurations.<host>`** | 一个仓库，`hosts/desktop/`、`hosts/laptop/` | ✅ 多机同步的唯一正解；本指南场景单机，用不上 |

**形态 B 的具体做法**：

```bash
# 1) 把你的配置仓库放到家目录（免 sudo）
mkdir -p ~/nixos-config && cd ~/nixos-config
git init
# 放入 flake.nix / configuration.nix / hardware-configuration.nix
git add -A && git commit -m "init"

# 2) 让 /etc/nixos 指向它
sudo mv /etc/nixos/flake.nix /etc/nixos/configuration.nix ~/nixos-config/ 2>/dev/null
sudo rmdir /etc/nixos 2>/dev/null
sudo ln -s ~/nixos-config /etc/nixos

# 3) 之后照常
sudo nixos-rebuild switch --flake /etc/nixos#myhost
```

> [!WARNING]
> **软链方案有一个坑**：flake 要求文件在 **git 仓库里被 `git add` 过**（§19.3）。软链本身不影响这一点，但如果你 `git init` 之后忘了 `git add flake.nix`，`nixos-rebuild` 会说"path does not exist in flake"。**改完配置先 `git add -A`。**

### 20.8 一份可直接抄的进阶 flake

```nix
{
  description = "AMD desktop · NixOS 26.05 · 中文 · Steam · Hermes/OpenClaw";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";

    home-manager.url = "github:nix-community/home-manager/release-26.05";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";

    # 第二十一章会用到（二选一，见 §21.4）
    # hermes-agent.url = "github:NousResearch/hermes-agent";
    # hermes-agent.inputs.nixpkgs.follows = "nixpkgs";
    # nix-openclaw.url = "github:openclaw/nix-openclaw";
    # nix-openclaw.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, nixpkgs-unstable, home-manager, ... }@inputs:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
        overlays = [
          (final: prev: {
            unstable = import nixpkgs-unstable {
              inherit system;
              config.allowUnfree = true;
            };
          })
        ];
      };
    in {
      nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
        inherit system;
        modules = [
          ./configuration.nix
          ./hardware-configuration.nix
          home-manager.nixosModules.home-manager
        ];
        specialArgs = { inherit inputs; };
      };
    };
}
```

> [!TIP]
> **加完 unstable input 后第一次 `nixos-rebuild switch` 会下载一份完整的 nixpkgs 求值缓存，稍慢。** 之后 `nix flake update nixpkgs-unstable` 单独更新它即可，不会动你的稳定 nixpkgs。

---

## 二十一、把 Hermes Agent 与 OpenClaw 落到 NixOS 上（安装 · 管理 · 自启 · 权限边界）

这一章回答你提出的八个问题。先把答案摆出来，再逐条给证据。

### 21.1 先给结论：一张表回答你的八个问题

| 你的问题 | 答案 | 详见 |
|---|---|---|
| 1. 怎么装？ | 两条主路：**nixpkgs 里的包 + 官方 bash 装**（免 root、配置可写），或 **上游官方 flake 的模块**（声明式、配置只读） | §21.5 §21.8 |
| 2. 怎么管理？ | 有官方模块时，**改 Nix 源 → rebuild** 就是管理；没有模块时，用软件自带的 CLI | §21.6 §21.9 |
| 3. 怎么自启？ | 有模块时模块替你建 systemd 单元；**用户级服务必须配 `linger`**，否则一登出就停 | §21.6 §21.9 |
| 4. **作为服务，有没有 root 权限限制导致 user 无法对话改配置？** | **有，而且这是三种部署方式的分水岭。** NixOS 系统模块 → 配置落在 root 拥有的 `/etc/` 下，**改配置必须 root**；HM 模块 → 落在你自己的家目录，**不用 root，但配置是只读符号链接**（改 Nix 源再 switch） | **§21.7 §21.10** |
| 5. 能用 Home Manager 装吗？ | **两个软件都有官方 HM 模块**，而且这是"一个人的 agent"的**官方推荐形态** | §21.3 |
| 6. 用 flake 装有什么差异？ | flake 装的是**上游官方模块**，不是 nixpkgs 包。差异在：声明式 vs 命令式、只读 vs 可写、系统服务 vs 用户服务 | §21.4 |
| 7. 直接官方 bash 装行不行？ | **行，而且是唯一"配置完全可写"的路**。在 NixOS 上多一个 `nix-ld` / FHS 的额外要求 | §21.11 |
| 8. 坑、故障、难点、社区意见 | 单独成章 | **第二十二章** |

### 21.2 先认清「官方支持等级」——这决定了你能指望谁

我在 nixpkgs `nixos-26.05` 和上游仓库上做了逐项核实：`[核实·源码]`

| 软件 | nixpkgs 里的**包** | nixpkgs 里的 **NixOS 模块** | 上游**官方 flake** | 官方支持等级 |
|---|---|---|---|---|
| **OpenClaw** | ✅ `pkgs.openclaw`（`pkgs/by-name/op/openclaw/package.nix`，HTTP 200） | ❌ **无**（`module-list.nix` 里 grep `openclaw` = 0） | ✅ `github:openclaw/nix-openclaw`（712★，first-party） | 上游**官方维护**，但**不接受 PR** |
| **Hermes Agent** | ❌ **不在 nixpkgs**（`pkgs/by-name/he/hermes-agent/package.nix` = 404） | ❌ **无** | ✅ 官方仓库自带 `flake.nix` + `nix/nixosModules.nix` | **官方明说 Tier 2**（best-effort） |

> [!DANGER]
> **Hermes 官方文档把 Nix / NixOS 明确列为 Tier 2 平台，原话是：** *"The flake and NixOS module documented here are maintained on a best-effort basis only. Commits to `main` may break these packages at any point in time."*（`[官方]` `website/docs/getting-started/platform-support.md`）
>
> **翻译成可执行的判断**：**不要**把 Hermes 的 Nix 路径用在你唯一一台工作机上做"不可恢复"的部署。Tier 1 是 macOS / Windows / Ubuntu-WSL2 / Docker。**如果你要的是稳，官方支持的那条路是 Docker 或 FHS 环境**，不是 flake。

> [!NOTE]
> **`pkgs.openclaw` 在 nixpkgs 里被标记为 insecure，这是设计而非疏漏。** 包定义的 `meta` 里带 `knownVulnerabilities`，原文是：*"Project uses LLMs to parse untrusted content, making it vulnerable to prompt injection, while having full access to system by default."* 后果是**安装它会要求你显式在 `permittedInsecurePackages` 里放行**。做法见 §21.5。`[核实·源码: pkgs/by-name/op/openclaw/package.nix]`

### 21.3 官方定位：三个部署层次（§19.6 引用的就是这里）

两个软件的官方文档**都用同一套语言**描述"应该怎么部署"，而且结论一致——**"一个人的 agent"应该跑成用户服务，不是系统服务。**

Hermes 官方原文（`[官方]` `nix-setup.md`）：

| Level | 给谁用 | 你得到什么 |
|---|---|---|
| `nix run` / `nix profile install` | 任何 Nix 用户 | 预构建二进制，然后走标准 CLI 流程 |
| **Home Manager 模块** | **"给一个人的 agent"，任何发行版或 macOS** | **声明式配置 + 用户服务，不需要 root** |
| NixOS 模块（native） | NixOS 服务器部署 | 声明式配置 + 加固的 systemd 服务 + 受管密钥 |
| NixOS 模块（container） | 需要自我修改的 agent | 上面全部 + 一个持久 Ubuntu 容器，agent 可在里面 `apt`/`pip`/`npm install` |

Hermes 官方对 HM 模块的定位原话：*"Hermes is an agent for one person. The credentials, the memory, the sessions and the cron jobs all belong to that person. Thus a user service is the correct shape on a personal machine."* `[官方]`

OpenClaw 官方（`nix-openclaw`）把可部署形态收敂成三条 **Golden Paths**（`[仓库]` `docs/golden-paths.md`）：

| Golden Path | Gateway 跑在哪 | 网络 |
|---|---|---|
| **GP1** 单 Mac | macOS（launchd） | localhost |
| **GP2** VPS Gateway + Mac Node（**官方推荐**） | **Linux VPS（systemd user service）** | **Tailscale** 私有网，不公网暴露 |
| **GP3** 只用笔记本开发 | macOS/Linux 笔记本 | 接受休眠与网络切换带来的停机 |

> [!IMPORTANT]
> **两张表指向同一个结论，这也是本指南给你的核心建议：**
> **你的场景（单机 AMD 桌面 + 你自己是唯一用户）对应 Hermes 的 "Home Manager 模块" 和 OpenClaw 的 GP1/GP3 —— 跑成 `systemd.user.services`，不要跑成系统服务。**
> 直接后果：**你不需要给 hermes / openclaw 任何 root 权限，改配置也不需要一个 root 服务来代劳。** 这正是你在 §19.6 里想要的形态。

### 21.4 flake 输入怎么接（§19.6 引用的是这里）

§19.6 说"Hermes 自己也拉一个 HM，两个 HM input 容易漂"。这里给具体写法。

**OpenClaw（nix-openclaw）**：

```nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  home-manager.url = "github:nix-community/home-manager/release-26.05";
  home-manager.inputs.nixpkgs.follows = "nixpkgs";

  nix-openclaw.url = "github:openclaw/nix-openclaw";
  # ★ 关键三行：让它的 nixpkgs 和 home-manager 都用你的那一份
  nix-openclaw.inputs.nixpkgs.follows = "nixpkgs";
  nix-openclaw.inputs.home-manager.follows = "home-manager";
};
```

**Hermes Agent**：

```nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  home-manager.url = "github:nix-community/home-manager/release-26.05";
  home-manager.inputs.nixpkgs.follows = "nixpkgs";

  hermes-agent.url = "github:NousResearch/hermes-agent";
  hermes-agent.inputs.nixpkgs.follows = "nixpkgs";
  # 如果 Hermes 的 flake 声明了 home-manager input（用 nix flake metadata 查）：
  # hermes-agent.inputs.home-manager.follows = "home-manager";
};
```

> [!TIP]
> **怎么知道一个 flake 有哪些 input、要不要 follow？** 一条命令：
> ```bash
> nix flake metadata github:openclaw/nix-openclaw
> nix flake metadata github:NousResearch/hermes-agent
> ```
> 输出里的 `Inputs:` 段落列出全部 input 名。**凡是你自己也有的（`nixpkgs`、`home-manager`），都 follow 过去。**
>
> **不 follow 的代价是实打实的**：`nix-openclaw` 不 follow nixpkgs 会多拉一整份 nixpkgs，`/nix/store` 里出现两套 glibc、两套 Python；而**不 follow home-manager 更糟**——HM 模块的选项签名必须与 HM 本体同版本，两个 HM 会让你的 `home-manager switch` 直接失败。

### 21.5 OpenClaw 之一：怎么装

**三条路，按"你要不要声明式"选。**

#### 路线 A：nixpkgs 的包 + 官方 bash（配置完全可写）

```nix
# configuration.nix
nixpkgs.config.permittedInsecurePackages = [
  "openclaw-2026.5.7"     # ★ 具体字符串看 nixos-rebuild 报错原文，它会把该填什么直接告诉你
];

environment.systemPackages = [ pkgs.openclaw ];
```

```bash
sudo nixos-rebuild switch
openclaw onboard          # 官方引导，会写 ~/.openclaw/openclaw.json
openclaw gateway install  # 见 §21.6
```

`pkgs.openclaw` 的 `installPhase` 会建**三个同实现的二进制**（`openclaw` / `moltbot` / `clawdbot`，后两个是软链），所以你看到老教程写 `clawdbot` 也不要慌——**是同一个程序**。`[核实·源码]`

> [!WARNING]
> **`permittedInsecurePackages` 里的字符串必须精确匹配，而且会随版本变。** 不要从本文抄 `openclaw-2026.5.7` 就以为一劳永逸——**每次 `nix flake update` 后包版本变了，这个字符串要跟着改**。最稳的做法是：先故意不写，让 `nixos-rebuild` 报错，它会把正确字符串印出来，再抄进去。

#### 路线 B：nix-openclaw 的 Home Manager 模块（单用户，推荐）

```bash
# 1) 从官方模板起一个本地 flake
mkdir -p ~/code/openclaw-local
git clone https://github.com/openclaw/nix-openclaw.git /tmp/nix-openclaw
cp /tmp/nix-openclaw/templates/agent-first/flake.nix ~/code/openclaw-local/flake.nix
cd ~/code/openclaw-local
# 2) 改模板里的占位符（system / home.username / home.homeDirectory / 密钥）
# 3) 应用
home-manager switch --flake .#你的用户名
```

模板 `templates/agent-first` 是 nix-openclaw **唯一**的模板（`[核实·源码]` 目录列表只有一个 `agent-first`）。

模块里的典型配置（`[仓库]` README）：

```nix
programs.openclaw = {
  runtimePlugins = [ "discord" ];                    # 声明式装插件
  environment = { DISCORD_BOT_TOKEN = "/run/agenix/discord-bot-token"; };
  config.channels.discord = {
    enabled = true;
    token = { source = "env"; provider = "default"; id = "DISCORD_BOT_TOKEN"; };
  };
};
```

#### 路线 C：nix-openclaw 的 NixOS 模块（`services.openclaw-gateway`）

```nix
# configuration.nix
services.openclaw-gateway = {
  enable = true;
  port = 18789;
  # user / group / stateDir / configPath 都有默认值，见 §21.7 的表
};
```

**nixpkgs 里没有 `services.openclaw` 模块**——上面这个 `services.openclaw-gateway` **只存在于 nix-openclaw 这个 flake 里**。`[核实·源码: module-list.nix grep = 0]`

### 21.6 OpenClaw 之二：怎么管理与自启

| 部署方式 | 管理入口 | 自启机制 | 开机自启的额外要求 |
|---|---|---|---|
| **A. nixpkgs 包 + bash** | `openclaw` CLI（`onboard` / `configure` / `doctor`） | `openclaw gateway install` **默认渲染 systemd user unit** | **`sudo loginctl enable-linger $(whoami)`**（需 root 设一次） |
| **B. HM 模块** | 改 `programs.openclaw.*` → `home-manager switch` | `systemd.user.services.<unitName>`（`systemd.enable` 默认 `true`） | **同上：`linger`**，且 **HM 自己设不了**（linger 是账户属性，见下） |
| **C. NixOS 模块** | 改 `services.openclaw-gateway.*` → `nixos-rebuild switch` | `systemd.services.openclaw-gateway`（**系统级**，`wantedBy = [ "multi-user.target" ]`） | 不需要 linger（系统服务本来就开机起） |

**OpenClaw 官方 CLI 路的原文**（`[官方]` `docs/gateway/index.md`）：

```bash
openclaw gateway install
systemctl --user enable --now openclaw-gateway.service
openclaw gateway status

# For persistence after logout, enable lingering:
sudo loginctl enable-linger $(whoami)
```

> [!WARNING]
> **`linger` 是"用户级服务能不能开机自启"的唯一开关，而且它必须由 root 设一次。** 这是本指南里**唯一一处**"即便你选了完全免 root 的路线，仍然需要一次性 root 操作"的地方。
>
> 原因：systemd 的用户实例（`user@<uid>.service`）默认**只在你登录期间存在**。你登出，用户管理器被销毁，`systemd.user.services` 里的服务跟着停。`loginctl enable-linger` 让该 uid 的用户管理器**在无登录会话时也保持运行**——这属于账户级属性，写不进你的 home 配置。
>
> **在 NixOS 上正确写法**（写进 `configuration.nix`，一次配好）：
> ```nix
> users.users.<你的用户名>.linger = true;
> ```
> **在非 NixOS 上**（或你不想改系统配置）：
> ```bash
> sudo loginctl enable-linger <你的用户名>
> ```
> 两处都做一遍不冲突。**验证**：`loginctl show-user <你> | grep Linger` 应显示 `Linger=yes`。

> [!TIP]
> **HM 模块自己设不了 linger，这是设计限制不是 bug。** nix-openclaw 的 README 与 Hermes 的 HM 模块文档**都**明确写了这一点（Hermes 原文：*"Home Manager cannot set linger, because linger is a property of the account"*）。所以**"完全免 root"在"开机自启"这一项上会破功**——你仍然需要一次 `users.users.<n>.linger = true`（要 root 跑 `nixos-rebuild`）或一次 `sudo loginctl enable-linger`。
>
> 但请注意这个 root 操作的**性质**：它是**一次性的、与 agent 配置无关的**开关。**它不给 agent 任何 root 能力，也不让 agent 需要 root 才能改自己的配置。**

### 21.7 OpenClaw 之三：作为服务时的 root 权限限制（你问的第 4 问）

**先给答案：有。而且"限制"取决于你选哪条路线——选错了，改一个模型名字都要 root。**

我在 nix-openclaw 的 NixOS 模块源码里逐项核实了权限边界（`[核实·源码]` `nix/modules/nixos/openclaw-gateway.nix`）：

```nix
# 关键断言：配置路径必须在 /etc 下
assertions = [
  { assertion = lib.hasPrefix "/etc/" cfg.configPath;
    message = "services.openclaw-gateway.configPath must be under /etc (got: ${cfg.configPath})."; }
];

# /etc/openclaw 归 root
systemd.tmpfiles.rules = [
  "d ${cfg.stateDir} 0750 ${cfg.user} ${cfg.group} - -"
  "d ${builtins.dirOf cfg.logPath} 0750 ${cfg.user} ${cfg.group} - -"
  "d ${builtins.dirOf cfg.configPath} 0755 root root - -"      # ★ root:root
];

environment.etc.${etcRelPath} = { mode = "0644"; source = configFile; };

systemd.services.${cfg.unitName} = {
  serviceConfig = {
    User  = cfg.user;      # ★ 默认 "openclaw"，非 root
    Group = cfg.group;
  };
};
```

**三条硬事实**：

1. **服务进程本身不是 root** —— 它以自动创建的 `openclaw` 系统用户运行（`user` 默认 `"openclaw"`，`createUser` 默认 `true`，`isSystemUser = true`）。这一点是好的。
2. **但配置文件在 root 手里** —— `configPath` 默认 `/etc/openclaw/openclaw.json`，目录由 tmpfiles 建成 `0755 root root`。**你是普通用户，写不进去。**
3. **而且有一条硬断言** —— `configPath` **必须以 `/etc/` 开头**，你想把它挪到家目录**会被模块直接拒绝**（`assertion` 失败）。

**所以三条路线的权限对照是**：

| 路线 | 服务运行身份 | `openclaw.json` 在哪 | 谁的 | **你（普通用户）能不能直接改配置** | **"对话里让 agent 改配置"能不能生效** |
|---|---|---|---|---|---|
| **A. nixpkgs 包 + bash** | **你自己**（`openclaw gateway install` 建的 user unit） | `~/.openclaw/openclaw.json` | **你** | ✅ **能**（普通文件，随便改） | ✅ **能** —— 这就是唯一"配置完全可写"的路 |
| **B. HM 模块** | **你自己**（`systemd.user.services`） | `~/.openclaw/openclaw.json` | 你 | ⚠️ **不能直接改** —— 它是**指向 `/nix/store` 的只读符号链接** | ❌ **不能** —— 但**不需要 root**，改 Nix 源再 `home-manager switch` |
| **C. NixOS 模块** | `openclaw` 系统用户 | **`/etc/openclaw/openclaw.json`** | **root** | ❌ **不能** | ❌ **不能** —— 而且**必须 root** 改（`sudo nixos-rebuild switch`） |

> [!DANGER]
> **这就是你问题的正面回答：**
>
> **是的，有 root 限制。具体是：**
>
> - 走 **NixOS 系统模块（路线 C）** → **配置在 root 拥有的 `/etc/` 下，普通用户改不了**。你想改模型、改频道、加插件，都必须 `sudo nixos-rebuild switch`。**这是"user 无法对话修改"的严格版本。**
> - 走 **HM 模块（路线 B）** → **不需要 root**，但配置是**只读的 Nix store 符号链接**，且 OpenClaw 在 `OPENCLAW_NIX_MODE=1` 下会**主动拒绝**任何 CLI 侧的配置写入（见下）。**"user 无法对话修改"依然成立，但原因从"权限不够"变成了"程序故意不让"。**
> - 走 **官方 bash（路线 A）** → **没有任何限制**，`~/.openclaw/openclaw.json` 是普通文件，你和 agent 都能改。
>
> **如果你要的是"能对话里让 agent 自己改配置"，那答案只有一个：不要用 NixOS/HM 模块，走 §21.11 的官方 bash 路。**

**`OPENCLAW_NIX_MODE` 是什么**（`[官方]` `docs/install/nix.md`）：

> *When `OPENCLAW_NIX_MODE=1` is set (automatic with nix-openclaw), OpenClaw enters a deterministic mode.*
>
> - *Auto-install and self-mutation flows are disabled.*
> - *`openclaw.json` is treated as immutable. ... config writers (setup, onboarding, mutating `openclaw update`, plugin install/update/uninstall/enable, `doctor --fix`, `doctor --generate-gateway-token`, `openclaw config set`) refuse to edit the file.*
> - *Edit the Nix source instead.*
> - *The UI shows a read-only Nix mode banner.*

非 Nix 场景的等价开关是 `OPENCLAW_CONFIG_READONLY=1`。

> [!NOTE]
> **"配置只读"不等于"agent 什么都改不了"。** 只读的是**配置**；**运行态**（会话、缓存、配对状态、`MEMORY.md`、`skills/`）仍在 `~/.openclaw` 下正常读写。nix-openclaw 官方把这条界线叫 **"Pinned / Nix-managed" vs "Runtime"**，明确列出：
> - **Nix 管**：`openclaw.json`、workspace 引导文件（`AGENTS.md`/`SOUL.md`/`TOOLS.md`/`IDENTITY.md`/`USER.md`）、workspace 路径
> - **运行态**：sessions、caches、pairing state、exec approvals、`BOOTSTRAP.md`、`MEMORY.md` 与 `memory/`
>
> **所以 agent 的记忆与技能仍然会长大**，只是"配置骨架"被冻结。这是设计意图，不是故障。

### 21.8 Hermes 之一：怎么装

Hermes 的安装层次比 OpenClaw 多一档（多了个 container 模式），但**前两档同构**。

#### 路线 A：`nix run` / `nix profile install`（任何 Nix 用户，最快）

```bash
# 跑桌面应用
nix run github:NousResearch/hermes-agent#desktop

# 或装进 profile
nix profile install github:NousResearch/hermes-agent
hermes setup
hermes --tui
```

装完后 `hermes` / `hermes-agent` / `hermes-acp` 都在 PATH 上，之后的流程与标准安装**完全一致**（`hermes setup` 走 provider 选择，`hermes gateway install` 建 launchd/systemd user service，配置在 `~/.hermes/`）。`[官方]`

> [!WARNING]
> **默认包会把整个闭包撑大约 700 MB。** Hermes 官方原文：*"The `default` package adds ~700 MB to the closure. If you only need messaging platforms, `#messaging` adds just ~33 MB."* 如果你只接 Telegram/Discord/Slack，用 `#messaging` 变体。`[官方]`

#### 路线 B：Home Manager 模块（单用户，推荐）

```nix
# home.nix
imports = [ inputs.hermes-agent.homeManagerModules.default ];

services.hermes-agent = {
  enable = true;
  gateway.enable = true;
  settings.model.default = "anthropic/claude-sonnet-4";
  environmentFiles = [ config.sops.secrets."hermes-env".path ];
};
```

```bash
home-manager switch
```

`home-manager switch` 会建 `~/.hermes`、写 `config.yaml`、构建 `.env`、把 gateway 起成**用户服务**。`[官方]`

#### 路线 C：NixOS 模块（`services.hermes-agent`）

```nix
# configuration.nix
{ config, ... }: {
  services.hermes-agent = {
    enable = true;
    settings.model.default = "anthropic/claude-sonnet-4";
    environmentFiles = [ config.sops.secrets."hermes-env".path ];
    addToSystemPackages = true;
  };
}
```

> [!TIP]
> **`addToSystemPackages = true` 做两件事，不只是"加 PATH"。** 官方原文：*"puts the `hermes` CLI on your system PATH **and** sets `HERMES_HOME` system-wide so the interactive CLI shares state (sessions, skills, cron) with the gateway service. Without it, running `hermes` in your shell creates a separate `~/.hermes/` directory."*
>
> **不设它的后果很隐蔽**：你在终端跑 `hermes`，它会在 `~/.hermes` 建一套**全新的** state，而 gateway 服务用的是 `/var/lib/hermes/.hermes`。**两边会话不互通，你会以为"我的历史丢了"。**

#### 路线 D：container 模式（只有 NixOS 模块支持）

```nix
services.hermes-agent = {
  enable = true;
  container.enable = true;      # ★ 自动 mkDefault 打开 virtualisation.docker.enable
  container.hostUsers = [ "你的用户名" ];
  addToSystemPackages = true;
};
```

这是**唯一一条"允许 agent 自我修改环境"的路**：容器是持久 Ubuntu，agent 可以 `apt`/`pip`/`npm install`，装的东西跨重启保留。

> [!DANGER]
> **container 模式的三条代价，官方文档都写了但很容易被忽略：**
> 1. **`/nix/store` 以 `ro` 绑定进容器，容器本身以 root 跑**（NixOS 服务以 root 创建容器，再在容器内降权到非特权用户）。**它需要 Docker socket，所以官方明说 HM 模块不支持它**（*"not supported, because it needs root and the Docker socket"*）。
> 2. **用 Podman 要额外配免密 sudo**：官方原文 *"Podman's rootful containers require sudo"*，并给出 `security.sudo.extraRules` 配 `NOPASSWD` 的写法。**Docker 用户不需要。**
> 3. **writable layer 会丢**：改 `container.image` / `extraVolumes` / `extraOptions` 会触发容器**重建**，`apt`/`pip`/`npm` 装的东西**全部丢失**（`/data` 与 `/home/hermes` 是绑定挂载，保留）。**`nixos-rebuild switch` 升级 Hermes 本身不会重建容器**（只更新一个软链）。

**container 模式的一个硬约束**（`[核实·源码]` `nix/nixosModules.nix:410`）：

```nix
assertion = !(cfg.container.enable && cfg.backend.mode != "none");
message = "services.hermes-agent: backend.mode is not supported together with container.enable — the container runs the gateway only.";
```

**即：container 模式不能和 `backend.mode`（`serve`/`dashboard`，桌面应用与 Web 面板的后端）同时用。** 你要么用容器，要么用桌面/面板，**二选一**。

### 21.9 Hermes 之二：怎么管理与自启

| 部署方式 | 管理入口 | 自启机制 | `linger` 谁负责 |
|---|---|---|---|
| **A. nix profile** | `hermes` CLI | `hermes gateway install` → systemd **user** service | **你自己**：`sudo loginctl enable-linger` |
| **B. HM 模块** | 改 `services.hermes-agent.*` → `home-manager switch` | `systemd.user.services.hermes-agent`（Linux）/ `launchd.agents`（macOS） | **你自己**：HM 设不了（官方明说） |
| **C. NixOS 模块** | 改 `services.hermes-agent.*` → `nixos-rebuild switch` | `systemd.services.hermes-agent`（**系统级**，`wantedBy = [ "multi-user.target" ]`） | **模块自动**（见下） |
| **D. container** | 同 C | 系统级 `hermes-agent`，脚本里管容器生命周期 | 模块自动 |

**Hermes 的 NixOS 模块在 linger 上做得比 OpenClaw 更细**（`[核实·源码]` `nix/nixosModules.nix`）：

```nix
# 第 369 行：createUser 时自动打开 linger
users.users.${cfg.user}.linger = lib.mkDefault (!cfg.container.enable);

# 第 571-578 行：排序在 linger-users.service 之后
after = [ "network-online.target" ] ++ lib.optional lingerEnabled "linger-users.service";
wants = [ ... ] ++ lib.optional lingerEnabled "linger-users.service";

# 第 594-603 行：preStart 轮询用户总线，最多等 10 秒
preStart = lib.mkIf lingerEnabled ''
  for _ in $(seq 1 50); do
    [ -S "/run/user/$(id -u)/bus" ] && break
    sleep 0.2
  done
  if [ ! -S "/run/user/$(id -u)/bus" ]; then
    echo "hermes-agent: no user bus at /run/user/$(id -u)/bus after 10s;" \
         "restart-safe cron dispatch will fail for the life of this process" >&2
  fi
'';
```

> [!IMPORTANT]
> **为什么 Hermes 要在 linger 上做这么多文章？因为它的 cron 依赖用户总线。** 源码注释原文（`:361-365`）：
>
> *"The cron scheduler launches every job in a transient `systemd-run --user --scope` so a gateway restart cannot kill a running job, and that needs a systemd user manager for this uid. A system service has no `/run/user/<uid>` unless the uid lingers, and **the dispatch fails closed — without this, no cron job runs at all**."*
>
> **翻译**：Hermes 的定时任务不是"fork 一个进程"，而是丢给 **systemd 用户实例**去跑（这样 gateway 重启不会杀掉正在跑的 job）。如果 uid 没有 linger，就没有用户实例，**结果是定时任务一个都不跑**——而且是**静默 fail closed**，不报错。
>
> **自查**：`loginctl show-user hermes | grep Linger`。如果你自己声明了 hermes 用户（`createUser = false`），**必须自己加 `linger = true`**，模块的 `mkDefault` 不会生效。

> [!WARNING]
> **官方模块的 `linger` 是 `lib.mkDefault`，可以被你覆盖掉——这是双向的坑。** 一方面你可以关掉它；另一方面**如果你在别处也声明了同一个用户**（`createUser = false` 且自己写 `users.users.hermes`），`mkDefault` 会被你的定义压掉，**linger 就没了，cron 静默失效**。这类"两个地方声明同一个用户"的冲突在 NixOS 里不报错，只是后者覆盖前者。

**HM 模块的自启（Hermes）**（`[核实·源码]` `nix/homeManagerModules.nix`）：

```nix
# Linux
systemd.user.services.hermes-agent = mkUnit { ... };   # 第 397 行
systemd.user.services.hermes-backend = mkUnit { ... }; # 第 404 行
# macOS
launchd.agents.hermes-agent = mkAgent { ... };         # 第 412 行
launchd.agents.hermes-backend = mkAgent { ... };       # 第 419 行
```

官方给的自启验证命令（`[官方]`）：

```bash
# Linux
systemctl --user status hermes-agent
journalctl --user -u hermes-agent -f

# macOS
launchctl list | grep hermes
tail -f ~/Library/Logs/hermes-agent.log
```

### 21.10 Hermes 之三：作为服务时的 root 权限限制（你问的第 4 问）

**和 OpenClaw 同构，但"只读"的实现机制不同——Hermes 用的是"标记 + 守卫"，不是"符号链接 + 权限"。**

Hermes 官方把 CLI 侧的行为叫 **Managed Mode**（`[官方]` `nix-setup.md`）：

| 被阻断的命令 | 原因 |
|---|---|
| `hermes setup` | 配置是声明式的——去改 Nix 里的 `settings` |
| `hermes config edit` | 配置由 `settings` 生成 |
| `hermes config set <key> <value>` | 配置由 `settings` 生成 |
| `hermes gateway install` | systemd 服务由 NixOS 管 |
| `hermes gateway uninstall` | systemd 服务由 NixOS 管 |

**检测用两个信号**（`[官方]`）：

1. **`HERMES_MANAGED` 环境变量** —— 服务设置它，gateway 进程读它。
2. **`HERMES_HOME` 下的 `.managed` 标记文件** —— 激活脚本写它，交互式 shell 读它。**因此它连 `docker exec -it hermes-agent hermes config set ...` 也会拦。**

两个信号都**带上"是谁在管"的名字**，所以拒绝信息会告诉你正确的重建命令：NixOS 模块给 `sudo nixos-rebuild switch`，HM 模块给 `home-manager switch`。`[官方]`

**权限边界对照表**：

| 路线 | 服务运行身份 | `config.yaml` 在哪 | **普通用户能直接改吗** | **对话里让 agent 改能生效吗** | 需要 root 吗 |
|---|---|---|---|---|---|
| **A. `nix profile`** | **你自己** | `~/.hermes/config.yaml` | ✅ 能 | ✅ **能** | ❌ 不用 |
| **B. HM 模块** | **你自己**（`systemd.user.services`） | `~/.hermes/config.yaml`（Nix 写） | ⚠️ 文件本身可写，但**每次 activation 会被 Nix 重新合并覆盖** | ❌ 不能（`HERMES_MANAGED` 拦） | ❌ **不用** |
| **C. NixOS 模块** | **`hermes` 系统用户** | **`/var/lib/hermes/.hermes/config.yaml`**（`0750 hermes:hermes`） | ❌ 不能（**连目录都进不去**） | ❌ 不能 | ✅ **要**（`sudo nixos-rebuild switch`） |
| **D. container** | 系统服务 + 容器内非特权用户 | `/data/.hermes/config.yaml`（容器内） | ❌ 不能 | ❌ 不能 | ✅ 要 |

> [!DANGER]
> **这就是你问题的正面回答（Hermes 版）：**
>
> **是的，有 root 限制。而且 Hermes 的限制比 OpenClaw 更"硬"：**
>
> - **NixOS 系统模块（路线 C）**：state 目录是 `0750 hermes:hermes`，**你连 `ls /var/lib/hermes` 都会 permission denied**。官方 troubleshooting 表里明确写着 *"Permission denied on `/var/lib/hermes` → State dir is `0750 hermes:hermes` → Use `docker exec` or `sudo -u hermes`"*。**改配置只能 `sudo nixos-rebuild switch`。**
> - **HM 模块（路线 B）**：不需要 root，目录是你的，但 **CLI 被 `HERMES_MANAGED` 主动拦住**，而且**每次 `home-manager switch` 都会用 Nix 的 `settings` 重新深合并覆盖一遍**。官方给的原则是：*"Nix-declared keys always win over keys in an existing `config.yaml` on disk, but **user-added keys that Nix doesn't touch are preserved**."*
>   - **这句话很重要**：它意味着 HM 模式下**不是"完全只读"**。你自己手工加进 `config.yaml` 的、Nix 没声明的键（例如 `skills.disabled`、`streaming.enabled`）**会活过 rebuild**。但**Nix 声明过的键，你手改的会被覆盖**。
> - **官方 bash（路线 A）**：**没有任何限制**，`~/.hermes/config.yaml` 完全归你。
>
> **所以：要"能对话改配置"，只有路线 A。**

> [!NOTE]
> **一个值得注意的对比**：Hermes 官方在文档里反复强调"你管理 hermes 的方式和你管理其它 NixOS 服务一样"（*"You manage hermes the same way you manage any other NixOS service."*）。**这句话的潜台词是：选择了 NixOS 模块，就是选择了"用 Nix 管"，放弃了"用 CLI 管"。** 两者不是叠加关系，是替代关系。

### 21.11 直接官方 bash 装：什么时候仍然是对的

**在 NixOS 上，官方 bash 路仍然可行，但多两个前置条件。**

Hermes 官方的 `curl | bash` 安装器（`setup-hermes.sh`）与 OpenClaw 的安装器都是 **Debian/Ubuntu 视角**写的。Hermes 官方原文（`[官方]`）：*"Ubuntu (LTS) is what we test against. Debian works. Arch and NixOS work for people who want them, but the one-line installer assumes a Debian-derived `apt` system."*

在 NixOS 上要让它工作，你需要**两样东西**：

```nix
# configuration.nix
programs.nix-ld.enable = true;      # 让非 Nix 的预编译二进制能跑（见 §15.8.3）
programs.nix-ld.libraries = with pkgs; [ libGL libxkbcommon gtk3 ];  # 按报错补
```

以及**一个 FHS 环境**（如果安装器内部硬编码 `/bin/bash`、`/usr/bin/env` 之类）。本指南第十七章的 FHS 决策树就是为这个准备的。

> [!IMPORTANT]
> **什么时候官方 bash 路才是"对的选择"？三个判据，满足任一即选它：**
>
> 1. **你要 agent 能自己改配置** —— 这是唯一一条能实现的路（§21.7 / §21.10）。
> 2. **你想跟着上游文档走** —— 官方文档的绝大多数内容（`hermes setup`、`openclaw onboard`、插件安装、频道配置）都是**命令式**写的。走模块路，这些命令**全部失效**，你必须把文档"翻译"成 Nix。
> 3. **你要的是"能用"而不是"可复现"** —— 单机、你自己用、不打算复制到第二台机器。
>
> **什么时候不该选它？**
> - 你要**跨机器同步**同一份 agent 配置 → 模块路。
> - 你要**可回滚**（rebuild 失败能退回去）→ 模块路。
> - 你**已经被 NixOS 的"声明式"惯坏了**，受不了"手改一个文件然后忘了改过什么" → 模块路。

> [!TIP]
> **一条折中路：nixpkgs 的包 + 官方 CLI 管配置。** 用 `environment.systemPackages = [ pkgs.openclaw ]` 让 Nix 管**二进制**（可复现、可回滚、跟着 `nixos-rebuild` 升级），用 `openclaw onboard` 让 CLI 管**配置**（可写、可对话修改）。**二进制声明式 + 配置命令式**，这是本指南对"既要又要"的推荐折中。Hermes 侧等价写法是 `nix profile install github:NousResearch/hermes-agent` + `hermes setup`。

### 21.12 一页裁决表（§19.4 引用的就是这里）

| 你的约束 / 目标 | 推荐路线 | 为什么 |
|---|---|---|
| **单机、只有你一个人用**（本指南场景） | **HM 模块**（OpenClaw / Hermes 都有） | 官方为"一个人的 agent"设计的形态；免 root 改配置；用户级回滚 |
| **要 agent 能在对话里自己改配置** | **nixpkgs 包 + 官方 bash**（§21.11） | 唯一配置可写的路 |
| **要跨机器同步同一份 agent 配置** | **HM 模块 + flake** | `home-manager switch` 可复现；配置在 git 里 |
| **要 agent 能自己 `apt`/`pip`/`npm install`** | **Hermes NixOS 模块 + `container.enable`**（§21.8 路线 D） | 唯一有持久可写层的路；代价是丢 writable layer 风险 |
| **多用户 / 真正的服务器常驻** | **NixOS 系统模块**（`services.openclaw-gateway` / `services.hermes-agent`） | 系统服务、开机自启、加固（`ProtectSystem=strict` 等） |
| **只想先跑起来试试** | `nix run github:...`（§21.8 路线 A） | 零安装、零配置，试完即弃 |
| **绝不接受"改配置要 root"** | **HM 模块**（改 Nix 源再 switch，不用 root） | ⚠️ 但**开机自启的 `linger` 仍需一次 root 操作**（§21.6） |

> [!IMPORTANT]
> **给本指南读者的最终建议（对应你的原始约束"不想让 hermes 拿 root"）：**
>
> **走 Hermes / OpenClaw 的 Home Manager 模块，配置放在你的 git 仓库里，`home-manager switch` 应用。**
>
> - ✅ agent 拿不到 root（用户服务，跑在你自己的 uid 下）
> - ✅ 改配置不需要 root（改 Nix 源 + `home-manager switch`）
> - ✅ 有用户级回滚（HM generation）
> - ⚠️ 唯一一次 root 操作：`users.users.<你>.linger = true`（**一次性、与 agent 能力无关**）
> - ⚠️ 代价：**agent 不能在对话里改自己的配置**（`OPENCLAW_NIX_MODE` / `HERMES_MANAGED` 会拦）—— 想清楚这一点能不能接受
>
> **如果你发现"agent 不能自己改配置"这条不能接受**，那就退回 §21.11 的折中路（Nix 管二进制 + CLI 管配置），并接受"配置不在 Nix 里、不可复现"这个代价。**这两者不可兼得，这是这一章最重要的一句话。**

---

## 二十二、坑、故障、难点与社区意见（Hermes / OpenClaw 在 NixOS 上的实测清单）

这一章是你第 8 问的直接答案。**每一条都带可复现的证据**（issue 编号、源码行号、官方原文），不带"我听说"。

### 22.1 先说结论：坑分成四类，代价差别极大

| 类别 | 具体表现 | 有多贵 | 能否绕过 |
|---|---|---|---|
| **① 构建成本类** | 每次 bump nixpkgs 要本地重建 ~666 个 derivation；小机器 OOM | 🔴 **极贵**（数小时 + 可能 OOM） | ⚠️ 只能缓解（加 swap / 限 cgroup / 不常 update） |
| **② NixOS 环境类** | stub-ld：预编译动态 ELF 跑不起来；工具闭包永远"不同步" | 🟠 中（有噪音，但功能可用） | ✅ 用 nixpkgs 提供的工具顶替 |
| **③ 权限与生命周期类** | 无 linger → cron 静默全不跑；无 `User=` 的系统 unit 以 root 跑 | 🔴 **极贵且隐蔽**（不报错） | ✅ 明确配置即可 |
| **④ 版本与身份类** | `hermes --version` 报旧版本 / 报 `0.0.0` | 🟢 低（只影响判断） | ✅ 用 `nix path-info` 之类的旁证 |

### 22.2 【最贵的坑】flake 没有二进制缓存：每次 `nix flake update` 要本地重建 ~666 个 derivation

这是**在 NixOS 上使用 Hermes flake 的最大单点成本**，而且它有完整的社区实测记录。

**证据**（`[仓库]` issue **#130870**，标题原文：*"Publish a binary cache (Garnix/Cachix) for the Nix flake — consumers rebuild ~666 derivations after every nixpkgs bump"*）：

> **实际数据（可复现）**
>
> 在一台 **4 vCPU / 8 GB RAM** 的 VPS 上，仅执行：
> ```
> nix flake update          # 只更新了 7 个输入，其中 nixpkgs
> nixos-rebuild build --flake .#...
> ```
> 调度出 **666 个 derivation 待构建**，其中绝大多数是 Python 依赖（`nix/python.nix` 的 uv2nix 层），外加少数 Rust 组件。
>
> 后果：
> - 构建峰值把 8 GB 内存 + 8 GB swap 吃穿，内核 OOM killer **两次杀掉 `nix-daemon`**，并波及机器上无关的进程（桌面 X 服务被一起杀掉）。
> - 加 12 GB swap + 把 `nix-daemon` 用 cgroup 限到 9 GB 后不再 OOM，但 4 核单线程编译下仍需数小时。
> - 内存刺客主要是带 Rust 内核的包：`pydantic-core`（cargo），以及 `cua-driver`。

**为什么"优先用 wheel"救不了**（同一 issue 的原文分析）：

> `nix/python.nix` 里已经写了 `sourcePreference = "wheel"`，方向是对的 —— 但**优先用 wheel ≠ 不用构建**：uv2nix 仍然要为每个 wheel 生成一个本地的 Nix derivation（解包 + patchelf）。这些结果没有任何地方被缓存，所以每个使用者、每次 nixpkgs 变动都要重算一遍。

> [!DANGER]
> **这条坑的严重性怎么强调都不过分，因为它和你已有的直觉冲突。**
>
> 你已经习惯"改配置 → `nixos-rebuild switch` → 从缓存下载 → 几分钟完事"。**Hermes 的 flake 打破了这个前提**——它的 Python 层没有任何公共缓存（没有 Cachix、没有 Garnix、没有 `nixConfig.extra-substituters`）。
>
> **三条实际后果**：
> 1. **第一次 `nixos-rebuild switch` 就要编译几百个包。** 不是下载，是**编译**。
> 2. **每次 `nix flake update` 后重来一遍**（因为 nixpkgs 变了 → Python 层的推导式全变 → 缓存全失效）。
> 3. **8 GB 内存不够。** 报告里 8 GB + 8 GB swap 被吃穿，`nix-daemon` 被 OOM 杀掉两次。
>
> **缓解手段（按性价比排序）**：
> - **不要频繁 `nix flake update hermes-agent`。** 定一个季度节奏，而不是每次上游发版就升。
> - **把 hermes 的 flake input 单独 pin 住**，不跟 `nixpkgs` 一起 `update`。
> - **构建时给 `nix-daemon` 限内存 + 加 swap**（报告里限到 9 GB 后不再 OOM）。
> - **在强机器上构建，然后推到你自己的 Cachix**（如果你有多个 NixOS 节点，这是唯一真正解决问题的办法）。
> - **或者干脆不用 flake**，走 §21.11 的 `nix profile install` 路——`nix profile install github:...` 同样要构建，但**它只构建一次并进 profile**，不会因为你的 `nixos-rebuild` 而重算。

### 22.3 【NixOS 环境类】stub-ld：预编译动态 ELF 跑不起来，工具闭包永远"不同步"

这是 NixOS 的**结构性特点**，不是 Hermes 的 bug，但 Hermes 的运行时自检把它变成了**每次命令都刷屏的警告**。

**证据**（`[仓库]` issue **#134249**，标题原文：*"NixOS: the tool closure can never be satisfied (check_runtime warns on every start; PM's downloader fails stub-ld)"*）：

> **现象**：在 NixOS 上，**每一次** CLI 调用都打印：
> ```
> ⚠ install out of sync (ffmpeg: not installed or outdated; node: not installed or outdated;
>   npm: not installed or outdated) — this nix-managed install must rebuild the artifact to fix
> ```
>
> **重建修不了它**：打包后的 bundle 的 `manifest.json` 声明了一个工具 store（`"store": "tools"`、`runtime.toolsDir: "tools"`），但**不附带 `tools/` 目录**；artifact 在只读的 `/nix/store` 里。所以这个判定**每次启动都重算，重建 artifact 也改不了它**。
>
> **而且 PM 也填不上**。运行它提示的补救命令：
> ```
> $ hermes pm install --tools-only
>   ffmpeg: unpacking
> ✗ ffmpeg: staged entry failed verification: .../tree/bin/ffmpeg --version exited 127:
>   Could not start dynamically linked executable: .../tree/bin/ffmpeg
>   NixOS cannot run dynamically linked executables intended for generic linux environments out of
>   the box. For more information, see: https://nix.dev/permalink/stub-ld
> ✗ node: staged entry failed verification: ... (same cause)
> ✗ npm: staged entry failed verification (npm stage, same cause)
> ✓ python
> ✓ ripgrep
> ```
>
> 三个剩下的工具都是预编译的通用动态 ELF，**NixOS 拒绝执行它们**：*"PM's own downloader can never satisfy them in this lane — the warning is unwinnable as written."*
>
> 注意 `ripgrep` **成功**了——因为它是**静态链接**的。这正好反证了原因是 stub-ld。

**Hermes flake 自己承认这一点**：它从 nixpkgs 提供 `ffmpeg` 和 `nodejs`（系统层），并说明"这与其自身注释中为打包的 `agent-browser` 二进制所用的 workaround 是同一个 stub-ld 情形"。

> [!IMPORTANT]
> **这条坑的实用含义（对你的实际影响）**：
>
> 1. **你会看到刷屏警告，但它不代表功能坏了。** `ffmpeg` / `node` / `npm` 从 nixpkgs 提供时，功能是正常的——只是 Hermes 的 `check_runtime()` 不认识这种"由 steward 提供"的形态。
> 2. **不要试图用 `hermes pm install` 去"修"它。** 在 NixOS 上这条路**结构性地走不通**（stub-ld）。
> 3. **这条坑是 §17 章 nix-ld 的镜像问题。** nix-ld 解决的是"**你**跑一个非 Nix 二进制"；这里是"**Hermes 自己的 PM** 想跑一个非 Nix 二进制，而 PM 不走 nix-ld 通道"。**`programs.nix-ld.enable = true` 不能修这个**，因为 PM 的验证逻辑不经过 nix-ld 的 `/lib64/ld-linux-x86-64.so.2` 垫片。
> 4. **它是 Tier 2 的直接后果**——Tier 1 的 Ubuntu/Docker 里不存在这个问题（那里 `ffmpeg` 就是系统包）。

### 22.4 【权限与生命周期类】没有 linger → cron 静默全不跑

这条在 §21.9 已从源码层面讲过，这里补上**它是被修出来的**这一层证据——说明它曾经真的坑到人。

**证据**（`[仓库]` 两个已合并的修复 PR 标题）：

> - *"fix(nix): NixOS module lingers the service user so restart-safe cron workers get a user scope (#110628, salvage #110629)"*
> - *"fix(nix): linger the service user so restart-safe cron workers get a user manager"*

**源码注释里的原话**（`[核实·源码]` `nix/nixosModules.nix:361-365`）：

> *"...A system service has no `/run/user/<uid>` unless the uid lingers, and **the dispatch fails closed — without this, no cron job runs at all**."*

> [!DANGER]
> **"fail closed 且静默"是这条坑最恶毒的地方。** 你的 gateway 正常运行、对话正常、日志正常——**只是定时任务一个都不跑**，而且不报错。你会以为是 cron 表达式写错了，或者以为模型忘了。
>
> **必须自查的两处**：
> 1. `loginctl show-user hermes | grep Linger` → 应为 `Linger=yes`
> 2. `ls -l /run/user/$(id -u hermes)/bus` → socket 应存在
>
> **最容易踩的变体**：你在 `configuration.nix` 里**自己声明了 hermes 用户**（`services.hermes-agent.createUser = false; users.users.hermes = {...};`），于是模块的 `linger = lib.mkDefault ...` **被你的定义压掉**。NixOS 对这种"两处声明同一用户"**不报错**，只是后者胜出。**自己声明用户时，务必自己写 `linger = true`。**

### 22.5 【版本与身份类】`hermes --version` 会骗你

小坑，但会浪费你时间——因为你用版本号判断"升级成功没有"。

**证据**（`[仓库]` issue 标题原文）：

| Issue | 现象 |
|---|---|
| **#135217**（open） | *"v0.21.6 shows the v0.21.5 release date (2026.9.24) in `hermes --version` and the banner"* |
| **[Bug]**（标题含 `[Nix]`） | *"`hermes -V` reports version `0.0.0` when installed via `nix profile install`"* |
| **#134988**（closed） | *"Stable release identity checks accept a correct 0.21.6 build (Nix version line, rc.N attempt refs)"* |
| **#134917**（closed） | *"fix(release): build the default flake package in the Nix identity check"* |

> [!TIP]
> **在 NixOS 上判断"Hermes 到底是哪个版本"，不要信 `hermes --version`，信 Nix。**
> ```bash
> # NixOS 模块 / HM 模块
> nix path-info --json $(readlink -f $(which hermes) | sed 's|/bin/.*||') | jq -r '.[].version'
> # 或直接看 flake.lock 里锁的 rev
> nix flake metadata github:NousResearch/hermes-agent | grep -A2 'Locked'
> ```
> 原因：`--version` 读的是打包进 artifact 的版本字符串，而 flake 路下这个字符串的注入时机与 `nix profile install` 路不同（这正是 `0.0.0` 那个 bug 的成因）。

### 22.6 【配置漂移类】"我改了配置但没生效"

这条是**声明式部署的固有代价**，不是 bug，但必须提前知道。

**官方原文**（`[官方]` Hermes `nix-setup.md`）：

> *"Nix-declared keys always win over keys in an existing `config.yaml` on disk, but **user-added keys that Nix doesn't touch are preserved**. This means if the agent or a manual edit adds keys like `skills.disabled` or `streaming.enabled`, they survive `nixos-rebuild switch`."*

OpenClaw 侧更严格（`[官方]` `docs/install/nix.md`）：

> *"`openclaw.json` is treated as immutable. ... config writers (setup, onboarding, mutating `openclaw update`, plugin install/update/uninstall/enable, `doctor --fix`, `doctor --generate-gateway-token`, `openclaw config set`) refuse to edit the file."*

> [!WARNING]
> **三种"改了没生效"的典型场景，以及正确诊断顺序：**
>
> | 你做了什么 | 期望 | 实际 | 正确做法 |
> |---|---|---|---|
> | 直接 `vim ~/.hermes/config.yaml` 改了 Nix 声明过的键 | 生效 | **下次 `home-manager switch` 被覆盖回去** | 改 Nix 源里的 `settings` |
> | 直接改 `~/.hermes/config.yaml` 加了 Nix **没声明**的键 | 生效 | ✅ **会保留**（官方明确保证） | 可以这么干，但记在案 |
> | 跑 `hermes config set ...` / `openclaw config set ...` | 生效 | ❌ **被 `HERMES_MANAGED` / `OPENCLAW_NIX_MODE` 拒绝** | 改 Nix 源 |
> | 跑 `hermes setup` / `openclaw onboard` | 重新配置 | ❌ **被拒绝** | 改 Nix 源 |
> | 跑 `openclaw plugins install ...` | 装插件 | ❌ **被拒绝** | `programs.openclaw.runtimePlugins = [...]` |
>
> **OpenClaw 的插件声明式写法**（`[仓库]` README 的对照表）：
> ```
> openclaw plugins install @openclaw/discord          →  programs.openclaw.runtimePlugins = [ "discord" ];
> openclaw plugins install npm:@openclaw/copilot@X    →  programs.openclaw.runtimePluginSources = [{ id = "copilot"; spec = "npm:@openclaw/copilot@X"; }];
> ```

### 22.7 【容器类】writable layer 丢失与 Podman 的 sudo 要求

Hermes container 模式的两个坑，官方文档都写了（`[官方]` `nix-setup.md`），但都是"事后才看到"的类型。

**坑 1：什么时候 writable layer 会丢**

| 事件 | 容器重建？ | `/data`（state） | `/home/hermes` | writable layer（`apt`/`pip`/`npm`） |
|---|---|---|---|---|
| `systemctl restart hermes-agent` | 否 | 保留 | 保留 | **保留** |
| `nixos-rebuild switch`（代码变化） | **否**（只更新软链） | 保留 | 保留 | **保留** |
| 主机重启 | 否 | 保留 | 保留 | **保留** |
| `nix-collect-garbage` | 否（有 GC root） | 保留 | 保留 | **保留** |
| **改 `container.image`** | **是** | 保留 | 保留 | **丢失** |
| **改 volume / options** | **是** | 保留 | 保留 | **丢失** |
| 改 `environment` / `environmentFiles` | 否 | 保留 | 保留 | **保留** |

重建的触发条件是**身份哈希**变化，哈希覆盖：schema 版本、`image`、`extraVolumes`、`extraOptions`、entrypoint 脚本。**改环境变量、`settings`、`documents`、甚至 hermes 包本身，都不会触发重建。**

> [!WARNING]
> **这条坑的隐蔽性在于：升级 Hermes 本身是安全的（不重建），但"我想把基础镜像从 `ubuntu:24.04` 换成 `ubuntu:26.04`"是破坏性的。** 你 agent 半年里 `apt install` 的东西会在那一刻全没。
>
> **官方给的对策**：把依赖**烤进自定义镜像**（`container.image = "my-registry/hermes-base:latest"`），或者在 agent 的 `SOUL.md` 里写清"启动时自查并重装"。

**坑 2：Podman 用户必须额外配免密 sudo**

官方原文：*"The NixOS service runs the container as root. Docker users get access via the `docker` group socket, but **Podman's rootful containers require sudo**."* 官方给的解法：

```nix
security.sudo.extraRules = [{
  users = [ "你的用户名" ];
  commands = [{
    command = "/run/current-system/sw/bin/podman";
    options = [ "NOPASSWD" ];
  }];
}];
```

**不配的后果**：`hermes chat` 等命令会因权限不足失败，你得手动 `sudo hermes chat`。

> [!NOTE]
> **注意这条的讽刺意味**：container 模式本来是为了"让 agent 能自我修改"，结果它引入了**一个需要给容器运行时开免密 sudo 的配置**。这是"为了自由度付出的权限代价"，和 §21.7 的"为了可复现付出的只读代价"是同一个权衡的两端。

### 22.8 【社区意见】三方态度各不相同——这决定了你出事时能指望谁

这一节是"社区意见"的直接回答。**三个相关方，三种态度，都要知道。**

#### ① nixpkgs 侧：OpenClaw 被标记 insecure，导致自动更新卡死

**证据**（`[官方论坛]` NixOS Discourse 帖 **#76940**，标题 *"Updating insecure package via r-ryantm bot (openclaw)"*，发帖人是 **nixpkgs 里 OpenClaw 的维护者 chrisportela**）：

> *"I've recently merged and become the maintainer for openclaw which has an incredible number of updates (at least a few times a week). **There are also a number of CVEs filed for it routinely** which mean we should keep it updated as quickly as we can.*
>
> *I agreed in my initial PR to mark it insecure because how much control software like OpenClaw has, but **it has made trying to get auto updates working very difficult**. Without properly getting r-ryantm configured correctly I need to rely on those with commit rights to approve any PRs to update OpenClaw."*

**其他维护者的回答**（同帖）：

> *waffle8946: "Is there some way for me to fix this without marking the package not insecure?" → **"No."***
>
> *sternenseemann: "r-ryantm won't perform multiple updates on any package per week since it deprioritizes packages after an update..."*
>
> *waffle8946 引用 nixpkgs README：*"Any security-critical fast-moving package such as Chrome or Firefox (or their forks) must have at least one committer among the maintainers, who actively reviews, merges and backports updates."*

> [!IMPORTANT]
> **从这条社区讨论能读出三件事：**
> 1. **`pkgs.openclaw` 的更新速度受限于"人工批准"**，不是自动的。上游一周发几次版，nixpkgs 里的版本可能滞后。
> 2. **"标记 insecure"是维护者的主动选择，理由充分**（*"how much control software like OpenClaw has"*），而且**社区明确回答"没法既自动更新又不标 insecure"**。
> 3. **实务结论**：**如果你要最新的 OpenClaw，不要依赖 `pkgs.openclaw`，用上游的 `nix-openclaw` flake**（它有自己的版本策略），或者用官方 bash 装。`pkgs.openclaw` 适合"我就要一个能跑的老版本"。

#### ② OpenClaw 官方：**明确不接受 PR，Issue 不监控**

**证据**（`[仓库]` `nix-openclaw` README，标题就是 *"PRs & Contributions (read this first)"*）：

> *"We're **not accepting PRs** right now. ... The best (and only) way to get stuff done: come join us on Discord! Join at https://discord.gg/clawd, then use **#golden-path-deployments**. **GitHub Issues are not actively monitored either.**"*

> [!DANGER]
> **这条对你的"出事时能指望谁"影响极大：**
> - ❌ **不要指望提 PR 修问题。**
> - ❌ **不要指望开 issue 有人回。**
> - ✅ **唯一的支持渠道是 Discord**（`discord.gg/clawd` 的 `#golden-path-deployments` 频道）。
>
> **这是"上游官方维护但不接受社区贡献"的罕见组合**，意味着**这个 flake 的演进方向完全由上游决定**，你的特殊需求不会被采纳。**如果你需要定制，只能 fork。**
>
> 另一个信号：`nix-openclaw` 的 `pushed_at` 是 **2026-09-25**，而主仓库 `openclaw/openclaw` 是 **2026-10-12**（同一天）。**flakes 侧比主仓库滞后约两周**——这也印证了"不监控 issue"。

#### ③ Hermes 官方：**明确降级为 Tier 2，best-effort**

**证据**（`[官方]` `platform-support.md` 原文）：

> *"These platforms are maintained in-tree only as a best effort. **Releases may break them, and we can't promise we'll fix them promptly when they break.** PRs will be accepted to fix issues with them, but they will take precedence below fixing issues with Tier 1 platforms."*

**"Unsupported" 清单里明确排除了什么**（同一文档）：

> *"installs via `pypi` (e.g. `uv tool install hermes-agent`, `pip install hermes-agent`, etc.)"* / *"installs via `brew`"* / *"installs via the AUR (we might upstream patches if it helps out <3)"*

> [!IMPORTANT]
> **和 OpenClaw 对比，Hermes 的态度明显更好：**
> - ✅ **接受 PR**（Tier 2 明说 "PRs will be accepted to fix issues with them"）。
> - ✅ **Nix 相关 issue 数量很大且活跃**（`repo:NousResearch/hermes-agent nix` 命中 **3374** 条），说明有人在用、在报、在修。
> - ⚠️ **但优先级低于 Tier 1**，而且官方原文承认 *"Commits to `main` may break these packages at any point in time"*。
>
> **Hermes 的 Nix 侧维护者明显在认真干活**——从 issue 标题能看出有持续的 fix 流：`fix(nix): extraPythonPackages no longer drops the default package's dependency groups`、`fix(nix): pick up wayland in the desktop app`、`fix(nix): provide PortAudio to voice runtime`、`docs(nix): note the per-module workingDirectory default`……**这是一条"有人在管、但排在后面"的线。**

#### ④ 第三方补充：`0xrsydn/nix-hermes-agent`

**元信息**（`[核实·源码]` GitHub API）：

| 项 | 值 |
|---|---|
| stars | **46** |
| forks | 8 |
| 创建 | 2026-03-15 |
| 最后推送 | **2026-10-11**（活跃） |
| 描述 | *"Nix package and NixOS module for Hermes Agent by Nous Research"* |
| 顶层 | `flake.nix` / `module.nix` / `package.nix` / `nightly.nix` / `checks.nix` / `tests/` / `docs/` |

**它和官方模块的实质差异**（`[核实·源码]` 逐项对比）：

| 维度 | 官方 `NousResearch/hermes-agent` | 第三方 `0xrsydn/nix-hermes-agent` |
|---|---|---|
| 配置选项名 | **`settings`** | **`config`** ← **名字不同！** |
| 配置文件 | `config.yaml` | **`cli-config.yaml`** |
| skills 声明式 | `extraPlugins`（符号链接目录） | **`skills.bundled` / `skills.optional` / `skills.custom`**（更完整） |
| HM 模块 | ✅ 有 | ❌ 无（只有 NixOS 模块） |
| container 模式 | ✅ 有 | ❌ 无 |
| `linger` 处理 | ✅ 有（`mkDefault` + `order after linger-users.service` + 轮询总线） | ⚠️ **本轮核实的版本里未见 linger 处理** |
| 上游版本策略 | 跟 `main`（可能 break） | **"quarantined candidate PRs"**（破坏性版本不会顶掉上一个已知良好版本） |

> [!WARNING]
> **抄配置时最大的坑：选项名不一样。** 官方用 `services.hermes-agent.settings.model.default`，第三方用 `services.hermes-agent.config.model.default`。**把第三方的例子抄到官方模块上，或者反过来，会直接报"选项不存在"。**
>
> **选择建议**：
> - **要 HM 模块 / container 模式 → 只能用官方。**
> - **要稳定的版本策略（不被上游 break）→ 第三方更保守**（它的 README 明确说 *"Upstream pins are promoted through quarantined candidate PRs so a broken Hermes release cannot replace the last-known-good package"*）。
> - **但第三方只有 46★、单人维护、无 HM 模块、且未见 linger 处理**——**如果你用它的 NixOS 模块，自己补 `linger`，否则 cron 会静默失效（§22.4）。**

### 22.9 【OpenClaw 专属】内存压力：官方专门写了一节

OpenClaw 的 Linux 文档把 *"Debugging Linux OOM kills or exit 137 on a VPS or container"* 直接写进了 `read_when` 触发条件——**说明这是高频问题**。`[官方]` `docs/platforms/linux.md`

**OpenClaw 的应对机制**（官方原文摘要）：

> *"For eligible Linux child spawns, OpenClaw wraps the command in a short `/bin/sh` shim that attempts to raise the child's own `oom_score_adj` to `1000`, then `exec`s the real command. This is unprivileged: a process may always raise its own OOM score."*
>
> 覆盖的子进程面：受管的命令子进程、PTY shell 子进程、MCP stdio 子进程、受管的本地模型/嵌入服务子进程、OpenClaw 启动的浏览器进程。
>
> *"The systemd unit's `OOMPolicy=continue` keeps the Gateway service alive when a transient child is selected by the OOM killer instead of marking the whole unit failed and restarting all channels."*

**可以关掉这个保护**：子进程环境设 `OPENCLAW_CHILD_OOM_SCORE_ADJ=0`（官方警告：*"Use this opt-out only for controlled diagnosis"*）。

**验证方法**（官方给的）：

```bash
cat /proc/<child-pid>/oom_score_adj     # 受覆盖的子进程应为 1000
```

> [!TIP]
> **对你的实际意义**：**OpenClaw 是一个会 spawn 很多子进程的软件**（浏览器、MCP server、本地模型）。在一台只有 16 GB 内存的桌面机上，如果你同时开 Steam 游戏 + OpenClaw + 浏览器，**OOM 的概率不低**。
>
> **本指南第十四章的 zram / 第十八章的 sysctl 调优在这里有直接价值**——不是为了跑分，是为了让 OOM killer 别挑到你的 gateway。

### 22.10 【OpenClaw 专属】系统 unit 不给 `User=` 会以 root 跑

**证据**（`[官方]` `docs/gateway/index.md` 原文）：

> *"Replace `<user>` with the non-root account that owns the OpenClaw state and configuration. **A system unit without `User=` runs as root. Running the Gateway and its agent commands as root is unsafe and unsupported for this setup.**"*

同文档还给了两条配套警告：

> *"Do not copy configuration into root's home as a workaround. On a single-user host, the user unit above with `loginctl enable-linger` is the supported way to keep the Gateway running without a login session."*
>
> *"Do not also let `openclaw doctor --fix` install a user-level gateway service for the same profile/port. Doctor refuses that automatic install when it finds a system-level OpenClaw gateway service; use `OPENCLAW_SERVICE_REPAIR_POLICY=external` when the system unit owns the lifecycle."*

> [!DANGER]
> **这条是你"不想让 agent 拿 root"约束的最直接威胁。**
>
> **手写系统 unit 时漏掉 `User=` → 你的 agent 以 root 跑，而且官方明说 "unsafe and unsupported"。**
>
> **nix-openclaw 的 NixOS 模块不会踩这个坑**（它硬编码了 `User = cfg.user`，默认 `"openclaw"`，非 root）。**但如果你手写 unit（跟着老教程走），就很容易踩。**
>
> **自查**：
> ```bash
> systemctl cat openclaw-gateway | grep -E '^\s*(User|Group)='
> ps -o user= -p $(systemctl show -p MainPID --value openclaw-gateway)
> ```
> **第二个命令的答案必须不是 `root`。**

### 22.11 一页故障速查表（含 Hermes 官方给的排查命令）

**Hermes 官方 troubleshooting 表**（`[官方]` `nix-setup.md`，原文摘录）：

| 症状 | 原因 | 修法 |
|---|---|---|
| `Cannot save configuration: managed by NixOS` | CLI 守卫生效 | 改 `configuration.nix` 然后 `nixos-rebuild switch` |
| `No adapter available for discord`（或 telegram/slack） | sealed Nix venv 缺消息平台依赖 | 用 `#messaging` 变体：`nix profile install ...#messaging`；NixOS 模块用 `extraDependencyGroups = [ "messaging" ]` |
| 容器意外重建 | `extraVolumes` / `extraOptions` / `image` 变了 | 预期行为——writable layer 重置 |
| `hermes --version` 显示旧版本 | 容器没重启 | `systemctl restart hermes-agent` |
| **`Permission denied` on `/var/lib/hermes`** | state dir 是 `0750 hermes:hermes` | 用 `docker exec` 或 `sudo -u hermes` |
| `nix-collect-garbage` 删掉了 hermes | GC root 缺失 | 重启服务（`preStart` 会重建 GC root） |
| `no container with name or ID "hermes-agent"`（Podman） | rootful 容器对普通用户不可见 | 给 podman 配免密 sudo（§22.7） |
| `unable to find user hermes` | 容器还在启动 | 等几秒重试（CLI 会自动重试） |
| `extraPackages` 加的工具在终端里找不到 | 需要 rebuild 才更新 per-user profile | `nixos-rebuild switch && systemctl restart hermes-agent` |

**统一的服务诊断命令**：

```bash
# ── NixOS 系统模块 ──────────────────────────────
systemctl status hermes-agent          # 或 openclaw-gateway
journalctl -u hermes-agent -f
sudo -u hermes cat /var/lib/hermes/.hermes/.env      # 验证密钥加载

# ── Home Manager 模块（Linux）────────────────────
systemctl --user status hermes-agent
journalctl --user -u hermes-agent -f
loginctl show-user $USER | grep Linger                # ★ 必须 Linger=yes

# ── Home Manager 模块（macOS）───────────────────
launchctl list | grep hermes
tail -f ~/Library/Logs/hermes-agent.log

# ── container 模式附加 ──────────────────────────
docker ps -a --filter name=hermes-agent
docker exec hermes-agent readlink /data/current-package
docker exec hermes-agent cat /data/.container-identity
docker exec hermes-agent cat /data/.hermes/.env

# ── 强制重建容器（重置 writable layer）──────────
sudo systemctl stop hermes-agent
docker rm -f hermes-agent
sudo rm /var/lib/hermes/.container-identity
sudo systemctl start hermes-agent
```

> [!NOTE]
> **Hermes 官方还提供了一个"密钥是否真的加载了"的验证命令**（这是排"启动正常但认证失败"最快的办法）：
> ```bash
> # native
> sudo -u hermes cat /var/lib/hermes/.hermes/.env
> # container
> docker exec hermes-agent cat /data/.hermes/.env
> ```
> 如果 `.env` 里没有你期望的 key，问题在 `environmentFiles` / sops-nix / agenix 那一层，不在 Hermes。

### 22.12 结论：在 NixOS 上跑这两个 agent 的「最低风险姿势」

把这一章和上一章合起来，给你一份**风险排序明确的行动建议**：

| # | 建议 | 理由 |
|---|---|---|
| 1 | **先用 `nix run` / `nix profile install` 试，不要一上来就上 NixOS 模块** | 零构建成本（profile 只构建一次）、配置完全可写、试错了 `nix profile remove` 就干净了 |
| 2 | **如果决定用 flake 模块，先把"构建 ~666 个 derivation"这件事安排上** | 8 GB 内存不够；不要在你要用电脑的时候 `nix flake update`（§22.2） |
| 3 | **选 HM 模块而不是 NixOS 模块**（单用户场景） | 免 root 改配置；用户级回滚；官方推荐形态（§21.3） |
| 4 | **`users.users.<你>.linger = true` 立刻配上，并验证** | 不配 → cron 静默全不跑（§22.4） |
| 5 | **接受"agent 不能自己改配置"这个代价，或者退回 §21.11 折中路** | 两者不可兼得（§21.12） |
| 6 | **不要频繁 `nix flake update` 这两个 agent 的 input** | 每次都可能触发全量重建（§22.2） |
| 7 | **手写 systemd unit 时，`User=` 一个都不能漏** | 漏了就是 root 跑 agent，官方说 unsafe（§22.10） |
| 8 | **出事时的求助渠道**：Hermes → GitHub issue（活跃）；OpenClaw → **Discord `#golden-path-deployments`**（issue 不监控）（§22.8） |
| 9 | **OpenClaw 用户注意内存**：它 spawn 很多子进程，和 Steam 抢内存（§22.9） | 本指南第十四、十八章的调优在这里派上用场 |
| 10 | **版本判断信 Nix，不要信 `--version`** | 已知会报旧版本 / `0.0.0`（§22.5） |

> [!IMPORTANT]
> **一句话总结这两章：**
>
> **NixOS 上的 agent 部署，本质是在"可复现"和"可对话修改"之间选一边。**
>
> - 选**可复现**（flake 模块）→ 你会得到声明式、可回滚、免 root 改配置的部署；代价是 **agent 改不了自己的配置**、**每次 update 要编译几百个包**、**配置只读**。
> - 选**可对话修改**（官方 bash）→ 你会得到完全自由的配置；代价是**配置不在 Nix 里、不可复现、不跨机器**。
>
> **没有第三条路。** 想清楚你要哪个，然后按上面的表执行。**最糟的选择是"两边都想要但都没配好"**——那会同时得到"配置漂移"和"构建地狱"。

---

## 二十三、把 NixOS 用成「Bazzite 模式」（本章回答你第 8 问的最后一条）

你的原话是：**「如何让 NixOS 做到类似 Fedora Bazzite 的使用模式？」**

这一章把 Bazzite 的每一项「使用模式」拆开，逐条给出 NixOS 的对应物、能不能做到、要付什么代价。**结论先给：能复刻约 80%，剩下 20% 是「开箱即用的整机体验」，那是 Bazzite 的护城河，NixOS 不打算也没必要复刻。**

### 23.1 Bazzite 到底是什么模式：官方给出的六层软件层级

先看 Bazzite 官方文档怎么定义「软件该怎么装」。这段是**原文直译**，因为后面整章的对照都建立在它上面（`[官方]` <https://docs.bazzite.gg/Installing_and_Managing_Software/software-intro/>）：

> **Package formats ranked from most recommended to least recommended for daily usage**：
>
> 1. **Bazzite Portal（`ujust` 命令）** —— 由 Bazzite 与 Universal Blue 贡献者维护的定制脚本，也能安装**一小部分**应用。（优先于其他格式，但因为它只能装很少的软件，被定位成「系统级设置的扩展」而非应用商店。）
> 2. **Bazaar App Store（Flatpak）** —— 基于权限模型的通用包格式，**应当用于大多数图形应用，它是 Bazzite 上获取软件的主要方式**。
> 3. **Homebrew** —— 安装意图在终端里运行的应用（CLI/TUI）。
> 4. **Containers** —— 在隔离环境里跑应用以避免依赖问题。
>    - 4a. **Distrobox 容器** —— 支持 Flatpak 和 Homebrew 都不支持的软件，也用作开发箱。
>    - 4b. **Quadlet** —— 把容器化应用当 systemd 服务跑。
> 5. **AppImage** —— 便携通用格式，依赖宿主系统级库，通常从项目官网获取。
> 6. **`rpm-ostree`** —— 在系统级分层 Fedora 包（**不推荐，作为最后手段**）。

再加上 Bazzite 官网首页对「image based」的定义（`[官方]` <https://bazzite.gg/>）：

> **Bazzite is image based**，意思是每次更新后**上一个版本的操作系统仍保留在你的机器上**。如果更新导致任何问题，**你可以在启动时选择上一个镜像**。操作系统镜像在我们的仓库里保留 **九十天**，可以通过终端切换。（Nvidia 驱动更新弄坏了你要的东西？没问题，**rebase** 回最后一个已知良好的版本并 **pin** 住它。）

以及它的安全声明：

> **Secure by design** —— 开箱即用的 **SELinux**、**Secure Boot** 支持、带 SBOM 与构建溯源的**签名容器镜像**（cosign）、可选 TPM 自动解锁的 **LUKS** 全盘加密。

**这四段就是「Bazzite 模式」的全部内涵。** 下面逐条映射。

### 23.2 总对照表：六层层级 → NixOS 的对应物

| # | Bazzite 的层级 | Bazzite 怎么做 | NixOS 对应物 | 等价度 |
|---|---|---|---|---|
| ① | **Portal / `ujust`** | 维护者脚本一键装/配 | **`programs.nh` + 自写 `justfile` + HM 包装脚本**（§23.5） | ⚠️ **70%**：CLI 能复刻，GUI 门户没有 |
| ② | **Bazaar（Flatpak）** | **主渠道**，图形应用优先 Flatpak | Nix 优先，Flatpak **兜底**（§23.6） | ❌ **顺序相反** |
| ③ | **Homebrew** | CLI 工具 | `environment.systemPackages` / HM / `nix profile` | ✅ **更强**（可复现） |
| ④ | **Containers（Distrobox / Quadlet）** | 装 Flatpak+brew 都没有的包 | **`pkgs.distrobox`（同版本 1.8.2.5）** / `virtualisation.oci-containers`（§23.7） | ✅ **等价** |
| ⑤ | **AppImage** | 便携 GUI | `programs.appimage.binfmt = true`（§17.7） | ✅ **等价** |
| ⑥ | **`rpm-ostree` 分层** | **最后手段** | `environment.systemPackages` —— 但这是**首选**（§23.9） | ❌ **顺序相反** |
| — | **原子更新 + 回滚** | 镜像式，启动菜单选旧镜像 | **generations + 启动菜单 + `--rollback`**（§23.3） | ✅ **更强** |
| — | **Secure Boot** | 出厂支持 + `ujust enroll-secure-boot-key` | **lanzaboote**（外部 flake，要自管密钥）（§23.13） | ⚠️ **50%** |
| — | **Gaming Mode** | gamescope session 深度整合 | `programs.steam.gamescopeSession`（§23.10） | ⚠️ **60%** |
| — | **Waydroid（安卓应用）** | 出厂脚本配置 | `virtualisation.waydroid`（官方模块，§23.12） | ✅ **等价** |
| — | **掌机工具链** | InputPlumber / PowerStation / HHD | **`pkgs.inputplumber` / `pkgs.powerstation` 都在 nixpkgs**（§23.11） | ⚠️ **60%**：有零件，没组装 |
| — | **自动更新** | `ujust update`（系统+Flatpak+容器一次搞定） | `system.autoUpgrade` + 两条补充（§23.14） | ⚠️ **80%** |

> [!IMPORTANT]
> **读这张表要抓的重点不是「哪些能对上」，而是「哪两处顺序是反的」。**
>
> Bazzite 是**镜像只读 → 应用尽量外挂**（Flatpak/brew/容器），系统层能不动就不动。
> NixOS 是**声明式中心化 → 应用尽量进 nixpkgs**，系统层就是应用层。
>
> **这两条哲学是镜像对称的。** 照抄 Bazzite 的层级顺序到 NixOS，会得到最糟的结果（§23.16 专讲四个反模式）。

### 23.3 第一项：「原子更新 + 回滚」—— NixOS 天生就有，而且粒度更细

这是**唯一一项 NixOS 明显强于 Bazzite 的地方**，而且你在第十一章已经全配好了。

| 能力 | Bazzite（rpm-ostree） | NixOS（generations） |
|---|---|---|
| 更新原子性 | 整个镜像一个 deployment | 一次 build 一个 generation |
| 更新失败怎么办 | 启动时选上一个镜像 | 启动菜单选上一个 generation |
| 命令行回滚 | `rpm-ostree rollback` | `nixos-rebuild switch --rollback` |
| 回滚**粒度** | **整个系统**（不能只回滚一个包） | **单个包 / 单个 generation 都行** |
| 历史保留时长 | 镜像仓库保留 90 天 | 本地 generation 永久（直到你 GC） |
| 保留几个 | 上一个 + 当前（可 pin） | `boot.loader.systemd-boot.configurationLimit` 控制 |
| 换基础系统 | `rpm-ostree rebase` 换镜像 | **换 nixpkgs 输入**（§20.2 / §20.5） |

**Bazzite 的 `rebase` 在 NixOS 上就是「换 nixpkgs 输入」。** 你在第二十章学的双 nixpkgs（26.05 稳定 + unstable 只取 mesa/内核），本质就是**只 rebase 一部分**——这是 Bazzite 做不到的（它只能整镜像 rebase）。

一份「Bazzite 式保留策略」的等价配置（全部选项已核实存在）：

```nix
{
  # 启动菜单里最多保留 10 个 generation（≈ Bazzite 的镜像保留，但可精确控制）
  boot.loader.systemd-boot.configurationLimit = 10;
  # ↑ 选项存在，默认 null（= 不限）  [核实·源码: nixos/modules/system/boot/loader/systemd-boot/systemd-boot.nix:233]

  # 自动 GC：保留 30 天 + 至少 5 个（≈ Bazzite 的 90 天镜像保留策略）
  # 注意：programs.nh.clean.enable 与 nix.gc.automatic 互斥，模块会 warning
  programs.nh = {
    enable = true;
    flake = "/etc/nixos";          # 设置 NH_FLAKE，之后 nh os switch 不用带路径
    clean = {
      enable = true;
      dates = "weekly";            # 默认就是 weekly
      extraArgs = "--keep 5 --keep-since 30d";
    };
  };
}
```

> [!WARNING]
> **别同时开 `programs.nh.clean.enable` 和 `nix.gc.automatic`。**
> nixpkgs 的 `programs.nh` 模块里有一条显式 warning（`[核实·源码: nixos/modules/programs/nh.nix]`）：
> *"programs.nh.clean.enable and nix.gc.automatic are both enabled. Please use one or the other to avoid conflict."*
> 两个 GC 服务同时跑不会毁数据，但会互相抢锁、报错刷屏。

> [!NOTE]
> **一个诚实的差距**：Bazzite 的镜像**存在上游仓库里**（90 天），所以「回滚到三个月前」只需要下载；NixOS 的 generation **存在你本地**，一旦 GC 掉就没了。**但反过来说**：NixOS 的 generation 只要还在，回滚**不需要网络**，Bazzite 需要能访问仓库。两者各有取舍。

### 23.4 第二项：「不可变」—— 两个系统说的不是同一件事

「NixOS 是 immutable distro」这句话**经常被误传**。看清楚机制：

| | Bazzite | NixOS |
|---|---|---|
| 底层机制 | rpm-ostree / bootc 镜像 + 部署 | `/nix/store` 只读 + symlink 原子切换 |
| 哪一层只读 | **`/usr` 只读**，其余（`/etc`、`/var`、`/home`）可写 | **只有 `/nix/store` 只读**，其余**全部可写** |
| `/etc` 怎么来的 | `/usr/etc` 覆盖 + `/etc` 可写层 | activation 脚本生成（`environment.etc`） |
| 改系统的动作 | 重新 commit 一个 deployment | 重新 build 一个 generation |
| 卸载包 | 很难（要重新 commit） | 改配置 → 重新 build |
| 手工改 `/usr` | **会被下次更新覆盖** | **不可能**（store 里是哈希路径） |

> [!IMPORTANT]
> **NixOS 除 `/nix` 以外整个根文件系统都是可写的。** 它不是「不可变发行版」，是**「声明式发行版」**。
>
> 区别在于：Bazzite 用**只读**来保证一致性（你改不动，所以不会漂）；NixOS 用**声明**来保证一致性（你可以改，但下次 rebuild 会改回来，而且你改了什么会被 `nix store diff-closures` 记下来）。
>
> **实用推论**：在 NixOS 上你**可以** `sudo` 进去改 `/etc/xxx.conf` 应急 —— 这在 Bazzite 上多半也会成功（因为 `/etc` 可写），但两者都会在下次更新/rebuild 时丢掉。**所以别养成习惯。**

### 23.5 层级 ① 的对应：`ujust` 的动词体系 → `nh` + `just`

Bazzite 的 `ujust` 本质是一个 **`just` recipe 集合**，装在 `/usr/share/ublue-os/just`，动词有明确语义（`[官方]` <https://docs.bazzite.gg/Installing_and_Managing_Software/ujust/>）：

| 动词 | 语义 |
|---|---|
| `install-` | 装程序（目前无卸载/配置命令） |
| `get-` | 装「扩展」（如 Decky 插件） |
| `setup-` | 装程序，**并提供安装后的卸载与配置选项** |
| `configure-` | 配置镜像里**已经默认存在**的东西 |
| `toggle-` | 开/关某个特性 |
| `fix-` | 修复、打补丁或绕过某个问题 |
| `distrobox-` | Distrobox 专用动词 |
| （裸动词） | `ujust update`、`ujust enroll-secure-boot-key` 之类 |

常用命令（`[官方]` 同上）：`update` / `clean-system` / `configure-grub` / `fix-reset-steam` / `fix-proton-hang` / `restart-pipewire` / `bios` / `setup-virtualisation` / `setup-sunshine` / `setup-decky` / `configure-waydroid` / `enable-tailscale` / `logs-last-boot` / `device-info`。

#### NixOS 的对应物：`nh`（官方包 + 官方 NixOS 模块）

**`nh`（Nix Helper）就是 NixOS 生态里最接近 `ujust` 的东西**，而且它在 nixpkgs 里（`pkgs.nh`，**4.4.2**，`[核实·源码: pkgs/by-name/nh/nh/package.nix]`；上游最新 release 也是 **v4.4.2**，2026-07-28）。

官方文档（`[官方]` <https://github.com/nix-community/nh/blob/master/docs/README.md>）的原话：

> NH 是一个现代辅助工具，目标是**整合并重实现** Nix/NixOS 生态中各工具的若干命令与接口。我们的目标是提供一个**内聚的、易理解的**接口，功能更多、人体工学更好，且在很多情况下**更快**。

它的能力域，与 `ujust` 逐条对照：

| `ujust` 的能力 | `nh` 的对应 | 说明 |
|---|---|---|
| `ujust update` | `nh os switch` / `nh home switch` | 重建系统 / home（带 build 树可视化 + 变更 diff + 确认） |
| `ujust clean-system` | `nh clean` | 重实现 `nix-collect-garbage`，**并清理 gcroots**，支持时间保留 |
| `ujust <搜索>`（无此能力） | `nh search packages/options/prs/issues` | **Bazzite 没有的**：搜 nixpkgs 包 / NixOS 选项 / PR / issue |
| 代际管理（rpm-ostree 提供） | `nh os` 内置代际 inspect / rollback | *"Inspect, rollback, and manage system generations with explicit targeting"* |
| `ujust --choose`（TUI 菜单） | `nh` 各子命令的交互确认 | ⚠️ 不是「菜单式」而是「确认式」 |
| `ujust --show <cmd>` | `man 1 nh` / `nh <sub> --help` | 看每个命令做什么 |

`nh` 的子命令（`[官方]` 同上，已核实）：

```
nh search <query>                       # 简写，默认搜包（可用 NH_DEFAULT_SEARCH 改）
nh search packages <query>              # 走 search.nixos.org 的 elasticsearch
nh search options --scope=all <query>   # 搜 nixpkgs / home-manager / nix-darwin 选项
nh search offline --db <PATH> <query>   # 离线搜本地 SPAM 数据库
nh search prs [--days N] <query>        # 搜 nixpkgs PR（需要 GH_TOKEN）
nh search issues [--days N] <query>     # 搜 nixpkgs issue
nh clean [all]                          # 重实现的 GC，含 gcroots 清理
nh os switch / boot / test [flake]      # 重实现 nixos-rebuild-ng
nh home switch                          # Home Manager
nh darwin switch                        # nix-darwin
```

> [!TIP]
> **`nh` 是本文档最推荐你立刻装的一个工具。** 它把「`nixos-rebuild` + `nix-collect-garbage` + 搜索网站 + 代际管理」四件事收进一个命令，并且自带 `nix-output-monitor`（`nom`）的构建树和 `dix` 的变更 diff。
>
> 对 ADHD 友好的点是：**`nh os switch` 会在切换前把「哪些包变了」列出来让你确认**，这比 `nixos-rebuild switch` 一按就切要安全得多。安装只要一行：`programs.nh.enable = true;`。

#### 复刻 `ujust` 的动词体系：一份可抄的 `justfile`

Bazzite 的 `ujust` 命令集本质是 `just` 的 recipe。NixOS 上你可以自己写一份，放进 Home Manager（`[官方]` just 在 nixpkgs 里，`pkgs.just` 已核实存在）：

```nix
# Home Manager 里的一段：装 just + 一份 justfile
{ pkgs, ... }:
let
  # 把你自己的「ujust 等价物」写成一个文件
  myJustfile = pkgs.writeText "justfile" ''
    # 列出所有命令（= ujust）
    default:
      @just --list

    # 更新系统（= ujust update 的 NixOS 版）
    update:
      sudo nh os switch ~/nixos-config

    # 更新 + 清理（= ujust update && ujust clean-system）
    refresh:
      sudo nh os switch ~/nixos-config && nh clean all --keep 5 --keep-since 30d

    # 重启到 BIOS（= ujust bios）
    bios:
      sudo systemctl reboot --firmware-setup

    # 重启 PipeWire（= ujust restart-pipewire）
    fix-audio:
      systemctl --user restart pipewire pipewire-pulse wireplumber

    # 重置 Steam 目录（= ujust fix-reset-steam 的思路）
    fix-steam:
      @echo "先备份 ~/.steam 与 ~/.local/share/Steam 再执行"
      rm -rf ~/.steam/steam/config ~/.local/share/Steam/config

    # 看本次启动日志（= ujust logs-this-boot）
    logs:
      journalctl -b -p warning

    # 收集设备信息（= ujust device-info）
    info:
      nix-shell -p inxi --run 'inxi -FJaz'
  '';
in
{
  home.packages = [ pkgs.just ];

  # 把 justfile 放到固定位置，并用别名 u 调用
  home.file.".config/just/justfile".source = myJustfile;
  home.shellAliases = {
    u  = "just --justfile ~/.config/just/justfile";
    uu = "just --justfile ~/.config/just/justfile --list";
  };
}
```

装好后你的日常就是：

```bash
uu            # 列出所有命令（= ujust）
u update      # 更新系统（= ujust update）
u refresh     # 更新 + 清理
u fix-audio   # 音频爆音
```

> [!NOTE]
> **和 `ujust` 的关键差别**：`ujust` 的脚本是**发行版维护者写好的、随镜像分发的**；你这份是你自己写的。好处是**完全可控、进 git、可回滚**；坏处是**你得自己写**。
>
> 但有个补偿：因为 `justfile` 是纯文本 + 可以放进 Nix 表达式（`pkgs.writeText`），**你的 agent 可以直接改它** —— 这比 Bazzite 上改 `/usr/share/ublue-os/just` 要干净（后者会被镜像更新覆盖）。**这一点和你在第十章、第二十一章想要的「agent 管系统」是配套的。**

### 23.6 层级 ② 的对应：Flatpak —— 在 NixOS 上要「反过来用」

Bazzite 官方把 Flatpak 定为**主渠道**（*"it is primary method of obtaining software on Bazzite"*）。**在 NixOS 上必须反过来**：Nix/nixpkgs 优先，Flatpak 兜底。

原因（第七章已详述，这里只列结论）：

| 维度 | 进 nixpkgs | 走 Flatpak |
|---|---|---|
| 进配置版本控制 | ✅ 是 `.nix` 的一行 | ❌ 不在配置里，rebuild 不管 |
| 可回滚 | ✅ 跟着 generation | ⚠️ 有自己的更新历史 |
| 主题 / 字体 / 输入法 | ✅ 天然一致 | ❌ **要额外打通**（§7 三个坑） |
| 中文字体 | ✅ `fonts.packages` 自动生效 | ⚠️ 沙箱内可能缺 |
| 磁盘占用 | ⚠️ 可能多份依赖 | ✅ runtime 共享 |
| 更新时机 | ✅ 跟 `nix flake update` | ❌ 独立更新，可能不同步 |
| 厂商只发 Flatpak 时 | ❌ 无解 | ✅ 唯一出路 |

**结论：Flatpak 在 NixOS 上的正确位置是「专有软件 / 只发 Flatpak 的软件的收容所」**，不是主渠道。

`services.flatpak` 在 26.05 的选项**只有两个**（`[核实·源码: nixos/modules/services/desktops/flatpak.nix]` 全文已读）：

```nix
services.flatpak = {
  enable = true;          # 唯一需要开的
  package = pkgs.flatpak; # 默认值，一般不用改
};
```

> [!WARNING]
> **`services.flatpak` 只有 `enable` 和 `package` 两个选项。** 网上很多配置里写的 `services.flatpak.remotes = [...]` 或 `uninstallUnmanaged` **在 nixpkgs 26.05 里不存在**（源码全文已核实，无此选项）。
>
> 而且模块里有一条**断言**（`[核实·源码]` 同上）：
> ```nix
> assertion = (config.xdg.portal.enable == true);
> message = "To use Flatpak you must enable XDG Desktop Portals with xdg.portal.enable.";
> ```
> **不开 `xdg.portal.enable` 会直接求值失败。** 第七章已给过完整配置。
>
> **想加 Flathub 要自己动手**（模块不管）：
> ```bash
> flatpak remote-add --if-not-exists --user flathub https://dl.flathub.org/repo/flathub.flatpakrepo
> ```

#### 一个好消息：Bazzite 的图形应用商店「Bazaar」在 nixpkgs 里

Bazzite 用 **Bazaar** 作为图形化的 Flatpak 商店（Bazzite 镜像里的版本是 `bazaar 0.9.3-4`）。**`pkgs.bazaar` 在 nixpkgs 26.05 里存在**（`[核实·源码: pkgs/by-name/ba/bazaar/package.nix]`）：

> `description = "FlatHub-first app store for GNOME";`
> `homepage = "https://github.com/kolunmi/bazaar";`

**想要 Bazzite 那种「点开商店勾选应用」的体验，`environment.systemPackages = [ pkgs.bazaar ];` 就行。** 这是本章少有的「直接对上」的项。

> [!NOTE]
> 上游项目是同一个（`kolunmi/bazaar`），但**版本号可能不同**（Bazzite 用 0.9.3，nixpkgs 26.05 用当时快照的版本）。这类「同一上游、不同打包」的情况，行为一般一致，但**别指望 bug 报告能直接对齐**。

### 23.7 层级 ④ 的对应：Distrobox —— NixOS 上同版本，但要自己接线

**`pkgs.distrobox` 在 nixpkgs 26.05 里是 `1.8.2.5`**（`[核实·源码: pkgs/by-name/di/distrobox/package.nix]`）—— 和 Bazzite 镜像里的 `Distrobox 1.8.2.5-1` **完全同版本**。这是个巧合，但也说明**这条路的成熟度两边是一样的**。

区别在于：**Bazzite 出厂就配好了（`ujust distrobox-` 动词、预置 `bazzite-arch` 容器）；NixOS 给你包，接线要自己来。**

NixOS 上 Distrobox 的三件事：

**① 装它（没有 NixOS 模块，是纯 CLI 包）**

```nix
{
  # distrobox 本身
  environment.systemPackages = [ pkgs.distrobox ];
  # 它需要 podman（或 docker）
  virtualisation.podman = {
    enable = true;
    dockerCompat = true;        # 提供 docker 兼容命令
    defaultNetwork.settings.dns_enabled = true;  # 容器内 DNS，中文环境常用
  };
  # 让普通用户能用 podman
  users.users.<你>.extraGroups = [ "podman" ];
}
```

**② 建容器（这一步和 Bazzite 完全一样）**

```bash
# Arch 容器（Bazzite 的 bazzite-arch 就是这个思路）
distrobox create --name arch --image quay.io/toolbx/arch-toolbox:latest
distrobox enter arch

# 进容器后就是正常的 Arch：
#   sudo pacman -S <你需要的包>
#   exit 回到 NixOS
```

**③ 把容器里的 GUI 应用「导出」到宿主菜单**

```bash
distrobox enter arch
# 容器内：
distrobox-export --app <应用名>          # 导出 GUI 应用（出现在 NixOS 的应用菜单里）
distrobox-export --bin /usr/bin/xxx --export-path ~/.local/bin  # 导出 CLI 命令
```

> [!TIP]
> **Distrobox 在 NixOS 上的价值比在 Bazzite 上更高。** 因为 NixOS 的 FHS 缺失（§17.6）会让某些**预编译二进制**跑不起来，而 **Distrobox 容器内部是完整的 FHS 环境** —— 这正好补上 NixOS 最痛的那块。
>
> 也就是说：`steam-run`（§17.7）解决「单个二进制」，`nix-ld` 解决「动态链接库」，**`distrobox` 解决「整个发行版环境」**。三者是递进关系，不是重复。

### 23.8 层级 ⑤ 的对应：AppImage —— 已在第十七章讲透

Bazzite 把 AppImage 排在第 5 层（*"relies on specific host libraries at a system-level, usually obtained from a project's website"*）。

NixOS 上的做法在 **§17.7** 已完整给出，这里只复述结论：

```nix
{
  programs.appimage = {
    enable = true;
    binfmt = true;   # 关键：注册 binfmt，让 AppImage 能「双击运行」
  };
  # 补上 AppImage 常缺的宿主库（按报错逐步加）
  programs.nix-ld = {
    enable = true;
    # 模块自带 14 个基础库（§15.8.3），GUI 场景按需追加：
    libraries = with pkgs; [
      libGL libxkbcommon gtk3 libgbm vulkan-loader
    ];
  };
}
```

> [!IMPORTANT]
> **`binfmt = true` 是这一项的关键**。不开它，AppImage 只是个普通文件；开了之后内核会识别它并用 `appimage-run` 执行 —— **行为上就和 Bazzite 一样了**（双击能跑）。这一条 NixOS 和 Bazzite 是**等价**的。

### 23.9 层级 ⑥ 的对应：`rpm-ostree` 分层 → `environment.systemPackages`（顺序相反）

这是**最容易照抄错**的一条。

Bazzite 说得很重：*"Layer Fedora packages at a system-level (**not recommended, use as a last resort**)"*，决策树里也写 *"Layer only if no other option works"*。原因在 Bazzite 的架构里是真实的：**每分层一个包，你的 deployment 就离上游镜像远一步** —— 更新变慢、rebase 变难、可能和镜像里的库版本冲突。

**NixOS 上这个理由不成立。** 因为：

| 关注点 | Bazzite 分层 | NixOS `environment.systemPackages` |
|---|---|---|
| 会不会「偏离上游」 | ✅ 会（deployment 变了） | ❌ 不会（build 结果确定、可复现） |
| 更新代价 | 变慢（要重算依赖） | 不变（除非该包本身要编译） |
| 回滚 | 整个 deployment | ✅ 单包 / 整个 generation |
| 可复现 | ❌ 不保证 | ✅ 哈希保证 |
| 冲突风险 | ⚠️ 和镜像库版本打架 | ✅ 无（每个包独立闭包） |

**所以在 NixOS 上，`environment.systemPackages` 是首选，不是最后手段。**

**但**：NixOS 有它自己的「别什么都塞进去」的等价忠告，只是对象不同：

| 该放哪 | 放什么 | 为什么 |
|---|---|---|
| `environment.systemPackages` | 全系统都要用的（bash、git、curl、驱动工具） | 系统级、所有用户可用 |
| **Home Manager `home.packages`** | **你自己的 CLI 工具、编辑器、语言工具链** | **免 root、用户级回滚、不污染系统（§19.4 的 5 项好处）** |
| `nix shell` / `nix run` | **一次性的、试用的** | 零配置、用完即弃 |
| `nix profile install` | ⚠️ **少用** | 命令式、不进配置、容易漂（这是 NixOS 的「真·最后手段」） |

> [!IMPORTANT]
> **把 Bazzite 的「分层是最后手段」直接搬过来会得到一个错误结论**：以为 `environment.systemPackages` 应该尽量少用。
>
> 正确的 NixOS 忠告是：**「命令式安装（`nix profile install`）才是最后手段」**。声明式的 `environment.systemPackages` 和 `home.packages` 都是**首选**，区别只是「系统级还是用户级」。

### 23.10 Gaming Mode：`programs.steam.gamescopeSession`（源码级完整配置）

Bazzite 的招牌功能之一是 **Steam Gaming Mode**（掌机/客厅那种大屏体验），底层是 **gamescope session**。

**NixOS 有官方选项**，源码级核实（`[核实·源码: nixos/modules/programs/steam.nix]`）：

```nix
programs.steam.gamescopeSession = {
  enable = lib.mkEnableOption "GameScope Session";
  args      = [];                          # 传给 gamescope 的参数
  env       = {};                          # 传给 gamescope 的环境变量
  steamArgs = [ "-tenfoot" "-pipewire-dmabuf" ];   # ← 默认值，源码确认
};
```

模块做了什么（源码逐条读出）：

1. 生成一个 `/bin/steam-gamescope` 包装脚本：`gamescope --steam <args> -- steam <steamArgs>`
2. 在 `services.displayManager.sessionPackages` 注册一个 **`steam.desktop`** 会话 → **登录界面会多出一个「Steam」选项**
3. `programs.gamescope.enable = lib.mkDefault cfg.gamescopeSession.enable` —— **自动带上 gamescope**（mkDefault，你可以覆盖）
4. `environment.systemPackages` 加入 `steam-gamescope`
5. 硬赋值 `hardware.graphics.enable = true; enable32Bit = true;`（这是 `programs.steam.enable` 本来就做的）

一份**可直接抄**的 Gaming Mode 配置：

```nix
{
  programs.steam = {
    enable = true;
    gamescopeSession = {
      enable = true;
      # 常见加法（都是 gamescope 的真实参数）：
      args = [
        "--rt"                  # 实时优先级（需要下面 gamescope.capSysNice）
        "-f"                    # 全屏
        "--adaptive-sync"       # 可变刷新率（需要显示器支持）
        # "--hdr-enabled"       # HDR —— 见下方警告
        "-W 2560 -H 1440"       # 内部分辨率（按你显示器改）
        "-r 165"                # 帧率上限
      ];
      env = {
        # AMD 用户常用：让 Vulkan 走 RADV
        # （注意：现代 NixOS + Mesa 通常不需要，见 §14 的「反优化清单」）
      };
      # steamArgs 保持默认即可：["-tenfoot" "-pipewire-dmabuf"]
    };
    # 想要更顺的输入（Wayland 下的手柄映射）
    extest.enable = true;
    # 想要 Proton-GE 一类兼容工具
    # extraCompatPackages = [ pkgs.proton-ge-bin ];
  };

  # gamescope 需要 CAP_SYS_NICE 才能自己 renice（源码选项）
  programs.gamescope.capSysNice = true;

  # HDR / VRR 相关（源码核实存在的选项）
  # hardware.graphics.enable 已由 programs.steam 硬赋值，不用再写
}
```

> [!WARNING]
> **`--hdr-enabled` 与 Bazzite 的差距在这里最大。** Bazzite 镜像里的 `Gamescope 3.16.31` 是**打了补丁的**（Bazzite 自建 spec），并且镜像同时带 `gamescope-session 0~20261002git`。NixOS 用的是 nixpkgs 里的**上游 gamescope**（版本以你的 nixpkgs 快照为准）。
>
> **HDR 是否可用，取决于 `gamescope` 版本 + 你的 Mesa 版本 + 显示器**，不取决于配置写没写对。**别把「配好了」当成「一定亮」。** 这是本文档反复强调的：`[未核实]` 的收益项要自己 A/B。

> [!NOTE]
> **Gaming Mode 与 Bazzite 的完整差距清单**（都是「有零件、没组装」）：
>
> | Bazzite 有 | NixOS | 怎么办 |
> |---|---|---|
> | Gamescope Session（大屏会话） | ✅ `programs.steam.gamescopeSession` | 开就行 |
> | MangoHUD | ✅ `pkgs.mangohud`（已核实） | `programs.steam.extraPackages = [pkgs.mangohud]` |
> | **InputPlumber**（手柄抽象层） | ✅ `pkgs.inputplumber`（见 §23.11） | 有包，要自己写服务 |
> | **SteamOS-Manager**（TDP/风扇 UI） | ❌ nixpkgs 无 | 用 `pkgs.powerstation`（见 §23.11） |
> | **HHD / Handheld Daemon** | ❌ nixpkgs 无 | 无解（`[未找到]`） |
> | HDR 一键开关 | ⚠️ 靠 gamescope 参数 | 自己试 |
> | Decky Loader | ❌ nixpkgs 无（404） | 无解（`[未找到]`） |

### 23.11 掌机工具链：好消息 —— Bazzite 的核心零件大多在 nixpkgs 里

这是本章最有价值的发现。**Bazzite 用来做「掌机体验」的几个核心组件，在 nixpkgs 26.05 里都存在**（全部源码级核实）：

| Bazzite 组件 | nixpkgs 26.05 | 上游 | 证据 |
|---|---|---|---|
| **InputPlumber** | ✅ `pkgs.inputplumber`（**v0.77.1**） | `ShadowBlip/InputPlumber` | `[核实·源码: pkgs/by-name/in/inputplumber/package.nix]` |
| **PowerStation** | ✅ `pkgs.powerstation` | `ShadowBlip/PowerStation` | `[核实·源码: pkgs/by-name/po/powerstation/package.nix]` |
| **Bazaar**（应用商店） | ✅ `pkgs.bazaar` | `kolunmi/bazaar` | `[核实·源码: pkgs/by-name/ba/bazaar/package.nix]` |
| **Distrobox** | ✅ `pkgs.distrobox`（1.8.2.5） | `89luca89/distrobox` | `[核实·源码]` |
| **umu-launcher** | ✅ `pkgs.umu-launcher` | `Open-Wine-Components/umu-launcher` | `[核实·源码]` |
| **Waydroid** | ✅ `pkgs.waydroid` + 官方模块 | `waydroid/waydroid` | `[核实·源码]` |
| Decky Loader | ❌ 404 | — | `[未找到]` |
| HHD（Handheld Daemon） | ❌ 404 | — | `[未找到]` |

**`powerstation` 的官方描述逐字引用**（这是 Bazzite 掌机 TDP 控制的核心）：

> `description = "Open source TDP control and performance daemon with DBus interface";`
> `homepage = "https://github.com/ShadowBlip/PowerStation";`

> [!IMPORTANT]
> **「有零件」≠「有体验」。** Bazzite 的护城河不在这些组件本身（都是开源上游项目），而在**它把这些组件串起来了**：udev 规则、systemd 服务、电源策略、机型数据库、`ujust setup-` 脚本、以及**针对几十种掌机型号的适配测试**。
>
> **在 NixOS 上你要自己接线。** 这是本文档一直强调的判断标准：**NixOS 给你「可复现的积木」，Bazzite 给你「装好的玩具」。** 选哪个取决于你想要什么。

### 23.12 Waydroid：官方模块，而且内核**默认就支持**

Bazzite 用 Waydroid 跑安卓应用，配 `ujust configure-waydroid`。

NixOS 有**官方模块** `virtualisation.waydroid`（`[核实·源码: nixos/modules/virtualisation/waydroid.nix]` 全文已读）：

```nix
{
  virtualisation.waydroid.enable = true;
}
```

模块自动做了这些（源码逐条）：

| 动作 | 内容 |
|---|---|
| 内核参数 | `boot.kernelParams = [ "psi=1" ]`（压力失速信息，Waydroid 需要） |
| LXC | `virtualisation.lxc.enable = true`（自动开） |
| 防火墙 | `networking.firewall.trustedInterfaces = [ "waydroid0" ]` |
| gbinder 配置 | 写 `/etc/gbinder.d/waydroid.conf`（binder/hwbinder/vndbinder 全走 aidl2） |
| systemd 服务 | `waydroid-container.service`（`Type=dbus`，`BusName=id.waydro.Container`） |
| 包选择 | **自动判断**：`networking.nftables.enable` 为真时用 `pkgs.waydroid-nftables`，否则 `pkgs.waydroid` |
| 断言 | 内核版本 ≥ 4.18 |
| 内核配置 | `requiredKernelConfig`：`ANDROID_BINDER_IPC` / `ANDROID_BINDERFS` / `MEMFD_CREATE` |

> [!TIP]
> **这是本章最大的「反直觉好消息」：NixOS 默认内核已经编入了 Waydroid 需要的 binder 支持。**
>
> 我特意去读了 nixpkgs 的内核配置（`[核实·源码: pkgs/os-specific/linux/kernel/common-config.nix:1447-1457]`）：
>
> ```nix
> ANDROID_BINDER_IPC = { optional = true; tristate = "y"; };
> ANDROID_BINDERFS    = { optional = true; tristate = "y"; };
> ANDROID_BINDER_DEVICES = { optional = true; freeform = "binder,hwbinder,vndbinder"; };
> ```
>
> **`tristate = "y"` 意味着编进内核（不是模块）。** 所以模块里的 `requiredKernelConfig` 断言在**默认内核上直接通过** —— 你**不需要**自己 patch 内核或换内核。
>
> 网上很多「NixOS 装 Waydroid 要自定义内核」的说法是**过时的**。至少 26.05 不需要。

**剩下的步骤和任何发行版一样**（模块管到「容器能起来」为止）：

```bash
# 1) 初始化（会下载安卓镜像，需要网络）
sudo waydroid init

# 2) 启动容器
sudo systemctl start waydroid-container

# 3) 启动 UI
waydroid show-full-ui

# 4) 装 APK
waydroid app install /path/to/app.apk
```

> [!WARNING]
> **Waydroid 需要 `binder` 相关的 `/dev` 节点，这在部分内核配置下会被 SELinux/AppArmor 或 `devices cgroup` 挡住。** NixOS 上没有 SELinux 模块（§17.1），所以这一层不是问题；但如果你启用了 AppArmor 的严格策略，可能要放行。**这是 `[未核实]` 项**，真机遇到再处理。

### 23.13 Secure Boot：这是 Bazzite **明显更省事**的唯一一项

Bazzite 出厂就有 Secure Boot 支持（签名镜像 + `ujust enroll-secure-boot-key`）。

NixOS 的情况：

| 项 | 状态 |
|---|---|
| `boot.loader.systemd-boot` 自身签名 | ❌ **不签名**（只能验签，不能签自己） |
| nixpkgs 里的 Secure Boot 方案 | ❌ **没有**（`pkgs.lanzaboote` = 404，已核实） |
| 社区方案 | ✅ **lanzaboote** —— `github:nix-community/lanzaboote` |
| 最新版本 | **v1.2.0**（2026-09-26 发布，`[核实·源码: GitHub API]`） |

**要做 Secure Boot 就得引入 lanzaboote**（这就是本文档里少见的「必须加外部 flake」的场景之一）：

```nix
{
  inputs.lanzaboote = {
    url = "github:nix-community/lanzaboote/v1.2.0";   # 钉版本，别跟 main
    inputs.nixpkgs.follows = "nixpkgs";               # 关键：统一 nixpkgs（§20.6）
  };

  # 然后按 lanzaboote 官方文档配置 boot.lanzaboote.*
}
```

**代价（必须提前知道）：**

1. **要自己管理密钥**（`sbctl`）：生成、签名、enroll
2. **首次要进 BIOS**：清掉厂商 key → 进 setup mode → 才能 enroll 自己的 key
3. **每次内核/引导器更新都要重签**（lanzaboote 的 `nixos-rebuild` 集成会自动做，但这是额外一步）
4. **搞坏了可能开不了机**（引导链断裂）—— 一定要留一个 U 盘救援

> [!DANGER]
> **不要在只有一个系统、没有救援 U 盘、也没备份的情况下折腾 Secure Boot。**
> 引导链一旦破坏，机器可能连启动菜单都进不去。**先做好可启动 U 盘，再动。**
>
> **如果你的目标是「游戏体验」而不是「企业合规」，Secure Boot 的收益接近 0。** 它主要防的是「有人在你不在时物理接触机器改引导器」—— 桌面游戏机的威胁模型里，这条基本不成立。**建议先跳过。**

### 23.14 自动更新：`system.autoUpgrade` 完整选项 + 「Bazzite 式一键更新」

Bazzite 的 `ujust update` **一条命令更新系统 + Flatpak + 容器**。NixOS 的 `system.autoUpgrade` 只管系统，要补齐另两块。

`system.autoUpgrade` 的**全部选项**（`[核实·源码: nixos/modules/tasks/auto-upgrade.nix]`，逐条读出）：

| 选项 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `enable` | bool | `false` | 是否周期性升级 |
| `operation` | enum **`switch` \| `boot`** | `"switch"` | 跑 `nixos-rebuild switch --upgrade` 还是 `boot --upgrade` |
| `flake` | nullOr str | `null` | 例：`"github:kloenk/nix"` |
| `channel` | nullOr str | `null` | 例：`"https://channels.nixos.org/nixos-14.12-small"` |
| `upgrade` | bool | `true` | 是否加 `--upgrade` 参数 |
| `flags` | listOf str | `[]` | 额外参数 |
| `dates` | str | `"04:40"` | 频率或时刻（systemd timer 语法，也可写 `daily`） |
| `allowReboot` | bool | `false` | 是否允许自动重启 |
| `randomizedDelaySec` | str | `"0"` | 随机延迟（例 `45min`），避免多机同时拉 |

**一份「Bazzite 式一键更新」的等价配置：**

```nix
{
  # ① 系统：每天 04:40 自动升级（用 boot 而不是 switch，避免半夜切走正在跑的东西）
  system.autoUpgrade = {
    enable = true;
    operation = "boot";              # enum 只有 switch / boot 两个值
    flake = "/etc/nixos";            # 你的 flake 路径
    dates = "04:40";
    randomizedDelaySec = "30min";
    allowReboot = false;             # 不自动重启（游戏机场景：你不知道它在什么时候被重启）
    flags = [ "--print-build-logs" ];
  };

  # ② Flatpak：也自动更新（Bazzite 的 ujust update 会做）
  systemd.services.flatpak-update = {
    description = "Update all Flatpaks";
    startAt = "daily";
    serviceConfig = {
      Type = "oneshot";
      ExecStart = "${pkgs.flatpak}/bin/flatpak update -y";
    };
  };

  # ③ 容器：让 podman 自动更新带 auto-update label 的容器
  virtualisation.podman.autoPrune.enable = true;
  systemd.services.podman-auto-update = {
    enable = true;                   # podman 自带 timer，启用即可
  };

  # ④ 清理（见 §23.3 的 nh clean 或 nix.gc，二选一）
  nix.gc = {
    automatic = true;
    dates = "weekly";
    options = "--delete-older-than 30d";
  };
}
```

> [!WARNING]
> **`system.autoUpgrade` 有两个真坑**（第十一章 §11.3 已详述，这里复述）：
>
> 1. **`operation = "switch"` 会在半夜把系统切走** —— 如果那时你在跑游戏或编译，会被打断。**游戏机/桌面建议用 `"boot"`**，让你下次重启时自己决定。
> 2. **用 flake 时必须配好 root 的 git 身份**，否则自动升级提交 lock 文件会失败（root 没有 `user.name`/`user.email` 时 `git commit` 直接报错）。第十一章给了配置。
>
> 另外：`allowReboot = true` 在桌面场景**不建议开**。你永远不知道它什么时候重启，正在编译的东西会丢。

### 23.15 层级 ① 里真正没有的东西：Bazzite Portal

**Bazzite Portal** 是一个 GUI 应用（Bazzite 镜像里 `bazzite-portal 0.2.5-1`），勾选式地安装应用、开关特性。**NixOS 没有等价物，也不会有。**

原因是哲学层面的：

| | Bazzite Portal | NixOS |
|---|---|---|
| 用户操作 | 点选 → 立刻生效 | 改 `.nix` → rebuild |
| 状态存在哪 | 镜像 + deployment | **配置文件（git）** |
| 撤销方式 | 再点一次 / 回滚镜像 | `git revert` / 回滚 generation |
| 谁改的 | 任何人（GUI 无门槛） | 会写 Nix 的人 |

**NixOS 的设计目标恰好是「消灭菜单式配置」** —— 因为菜单点出来的状态不在版本控制里，无法审计、无法复现、无法代码审查。**这不是 NixOS 的缺陷，是它的取舍。**

最接近 Portal 的三条路（按接近度排序）：

| # | 方案 | 接近度 | 说明 |
|---|---|---|---|
| 1 | **`nh`（CLI 统一入口）** | ⚠️ 60% | 有交互确认、有代际管理，但是命令行 |
| 2 | **自写 `justfile`（§23.5）** | ⚠️ 55% | 复刻 `ujust` 的动词，但没 GUI |
| 3 | **agent 帮你改配置**（§10、§21） | ⚠️ 50% | 「用自然语言勾选」—— 某种意义上这才是 NixOS 的原生 Portal |

> [!TIP]
> **第 3 条其实是本文档的核心论点。** 你从第一轮就在问「怎么让 LLM 介入管理 NixOS」—— **NixOS 缺的 GUI 门户，正好是 agent 最擅长补的位置**：
>
> - Portal 的「勾选」= 你对 agent 说「我要装 X」
> - Portal 的「立刻生效」= agent 改 `.nix` + 跑 `nh os switch`
> - Portal 的「可撤销」= generation 回滚 + `git revert`（**比 Portal 更强**）
>
> **Bazzite Portal 是「给人用的 GUI」，NixOS 的答案是「给 agent 用的配置层」。** 这也是为什么本文档一直强调 skills + MCP（第十章、第十六章、第二十一章）。

### 23.16 别照抄的地方：Bazzite 模式在 NixOS 上的四个反模式

| # | 照抄会怎样 | 正确做法 |
|---|---|---|
| 1 | **照抄「Flatpak 优先」** | 会把系统拆成两半（Nix 一半、Flatpak 一半），主题 / 字体 / **中文输入法** 都要额外打通（§7、§5）。**NixOS 上必须 Nix 优先，Flatpak 兜底** |
| 2 | **照抄「`rpm-ostree` 分层是最后手段」** | 会误以为 `environment.systemPackages` 该少用。**NixOS 里命令式的 `nix profile install` 才是最后手段**，声明式的 `systemPackages` / `home.packages` 都是首选（§23.9） |
| 3 | **照抄「rebase 换镜像很随意」** | NixOS 换 nixpkgs 输入会**触发重建**（§22.2 的 666 个 derivation）。Bazzite 的 rebase 是**下载**，NixOS 的换源可能是**编译几小时** |
| 4 | **照抄「brew 装 CLI 工具」** | NixOS 上 `brew` 是外来户（需要 FHS + 自管 PATH，且和 nixpkgs 的库版本可能打架）。**用 `home.packages` 或 `nix shell`**（§15） |

> [!IMPORTANT]
> **第 3 条最贵，单独再强调一次。**
>
> Bazzite：`rpm-ostree rebase` → **下载**一个新镜像 → 几十秒。
> NixOS：改 nixpkgs 输入 → **重新 build** → 缓存命中就是下载，缓存没命中就是**本地编译**。
>
> **所以「Bazzite 式随意换镜像」的习惯在 NixOS 上会变成灾难。** 这就是第二十章要讲清「双 nixpkgs 怎么用才对」、第二十二章要讲清「666 个 derivation」的原因 —— **NixOS 的每一次「换源」都要先问：cache 里有吗？**

### 23.17 一页裁决表：你到底该选哪个

| 你真正想要的 | 推荐 | 理由 |
|---|---|---|
| **开箱即用的掌机/客厅体验** | **直接用 Bazzite** | 那些 `ujust setup-` 脚本、机型适配、HDR 一键开关，NixOS 要你自己搭几个月 |
| **声明式 + 可复现 + 可回滚 + 可代码审查** | **NixOS（本文档）** | Bazzite 的 deployment 不可复现、不可 diff、不可 PR |
| **想要「agent 能管系统」** | **NixOS** | Bazzite 的镜像式结构对 agent 不友好（改 `/usr` 会被覆盖）；NixOS 的配置层正是 agent 的用武之地 |
| **既要 Bazzite 体验，又要 Nix** | **Bazzite + Distrobox 里跑 Nix** | 用 §23.7 的 Distrobox，在容器里装 Nix（`nix-portable` 或官方安装器） |
| **既要 NixOS，又要 Bazzite 体验** | **NixOS + 本章映射表** | 复刻约 80%，放弃「开箱即用」，接受「自己接线」 |

> [!IMPORTANT]
> **一句话回答你的第 8 问：**
>
> **NixOS 能复刻 Bazzite 的使用模式约 80%** —— 原子更新与回滚（**更强**）、Flatpak（**顺序要反过来**）、Distrobox（**同版本**）、AppImage（**等价**）、Gaming Mode（**有官方选项**）、Waydroid（**官方模块 + 内核默认支持**）、掌机工具链（**零件都在 nixpkgs**）。
>
> **剩下 20% 复刻不了，而且不该复刻**：
>
> - **Bazzite Portal（GUI 勾选门户）** —— 与「配置即代码」的哲学冲突；**NixOS 的替代品是 agent**（§23.15）
> - **开箱即用的整机体验** —— Bazzite 的价值在「把几十个开源组件针对几十种机型调好」，这是**人力**而非**技术**，NixOS 社区没在做这件事
> - **出厂 Secure Boot** —— 要自己上 lanzaboote 并自管密钥（§23.13）
>
> **所以正确的问题不是「NixOS 怎么变成 Bazzite」，而是「你要的是『装好的玩具』还是『可复现的积木』」。** 想清楚这个，剩下的选择都是推论。

---

## 二十四、openSUSE Aeon 模式：稳定基座 + 最新应用（本章回答「基座是稳定，apps 是最新的，如何做」）

你的原话是：**「要做到类似 openSUSE Aeon，基座是稳定，但 apps 是最新的，如何做」**。

**先纠正一个前提，否则后面全错**：**Aeon 的基座不是「冻结的稳定版」，而是滚动的 openSUSE Tumbleweed。** 它的「稳定」不来自版本冻结，来自**原子性 + 极简 + 隔离**这三件机制。理解这一点之后，「稳定基座 + 最新应用」在 NixOS 上就有**三条**路可走，而不只是一条。

### 24.1 纠正前提：Aeon 的「稳定」是怎么来的

Aeon（前身 openSUSE MicroOS Desktop）的技术栈，LWN 2023 年那篇一手分析写得最清楚（`[媒体·一手]` <https://lwn.net/Articles/927373/>）：

> *"OpenSUSE MicroOS Desktop is one of them, with a **minimal openSUSE Tumbleweed as the base operating system** and applications running as Flatpaks or in containers."*
>
> *"Its biggest benefit is **availability of the newest software releases without sacrificing system stability**."*

注意「Tumbleweed」= **滚动发行版**。所以 Aeon 的基座本身是**追新**的。

LWN 还把这篇文章的核心问题写成了和你一模一样的措辞：

> *"many users want the best of both worlds: **the latest software versions on a stable base operating system**."*

**所以「稳定基座」有两种完全不同的实现方式，Aeon 用的是第二种：**

| 实现方式 | 代表 | 「稳定」的来源 | 基座版本 |
|---|---|---|---|
| **冻结版本集** | Debian stable / RHEL / **NixOS 26.05** | 版本不变，所以行为不变 | 固定 |
| **原子 + 极简 + 隔离** | **Aeon** / MicroOS / Fedora Silverblue / **NixOS** | 变了也能整批回滚，且坏不到基座 | 滚动 |

> [!IMPORTANT]
> **这是本章最重要的一句话：NixOS 两种模式都能给你。**
>
> - 想要**冻结版本集的稳定** → 用 `nixos-26.05`（本文档全篇的做法）。
> - 想要**Aeon 那种「滚动但原子」的稳定** → 用 `nixos-unstable`，靠 generations 回滚。
> - 想要**两者混搭**（基座冻结 + 部分组件滚动 + 应用追新）→ **这是 NixOS 独有的能力，Aeon 做不到。**
>
> 你的问题「基座稳定、apps 最新」在 NixOS 上有 **3 条路**（§24.3），而 Aeon 只有 1 条。

### 24.2 Aeon 技术栈逐条拆解（全部一手出处）

| 层 | Aeon 怎么做 | 出处原话 |
|---|---|---|
| **基座** | **minimal openSUSE Tumbleweed**；Btrfs root，**boot 后挂载为只读** | *"with a minimal openSUSE Tumbleweed as the base operating system"* / *"this filesystem is mounted read-only after boot"* |
| **更新** | systemd timer **每天**跑 `transactional-update`（zypper 的包装脚本）→ **新建 Btrfs snapshot** → 在快照里更新 → 成功则标记为下次启动的默认快照 | *"System updates are done automatically every day. This is implemented as a systemd timer unit that runs the `transactional-update` command, which is a wrapper script around the package manager `zypper`."* |
| **失败处理** | 出错则**丢弃快照**，旧的仍是默认；启动时检测到问题**自动回滚**；手动 `transactional-update rollback` | *"On errors, the snapshot is discarded and the previous one remains as the default."* / *"if the system detects a problem during the reboot, it automatically rolls back"* |
| **GUI 应用** | **全部 Flatpak**，装在用户目录 `~/.local/share/flatpak`，**自动更新**；GNOME Software 被配置成**只装 Flathub** | *"All desktop applications in MicroOS Desktop are installed as Flatpaks in the user's directory and automatically get updated."* / *"it's configured to **only** install Flatpaks from Flathub"* |
| **CLI / 开发** | **Distrobox**（预配 Tumbleweed 容器，>75,000 个 RPM 可用）；`distrobox-export` 把容器里的应用导出到宿主菜单 | *"a simple `distrobox-enter` command in the terminal creates (or enters…) a container running Tumbleweed"* |
| **兜底（往基座装包）** | `transactional-update` 装 RPM —— **只推荐给驱动 / 内核模块 / VPN 客户端这类必须紧耦合的** | *"this is only recommended for drivers, kernel modules, virtual private network (VPN) clients, and other low-level packages that have to integrate tightly with the operating system, because **every extra package in the host incurs extra risk of instability**"* |
| **防火墙** | **默认没有**（官方称是设计，因为与容器运行时冲突） | *"MicroOS also lacks a firewall. According to Brown, this is by design, because they cause problems with container runtimes"* |

Aeon 官网自己的三条卖点（`[官方]` <https://aeondesktop.github.io/>）：

> - **Automated Maintenance**：*"Daily system updates happen automatically while you work. **Your running system is not affected until you reboot**"*
> - **Minimal Yet Functional**：*"The base system is kept small and simple"*
> - **Flatpak**：*"already set up to let you install any app from a vast catalogue available from Flathub"*

> [!TIP]
> **注意最后那句「your running system is not affected until you reboot」** —— 这就是 `system.autoUpgrade` + `operation = "boot"` 的语义（§24.7）。**NixOS 可以做出一模一样的行为，而且还能额外做到「不重启就生效」。**

### 24.3 三条路：NixOS 上「稳定基座 + 最新应用」的三种做法

| 维度 | **路 A：Aeon 式（外挂优先）** | **路 B：双 nixpkgs（Nix 原生）** | **路 C：混合（推荐）** |
|---|---|---|---|
| 基座 | NixOS 26.05，**极简** | NixOS 26.05 | NixOS 26.05 |
| GUI 应用来源 | **Flatpak（Flathub）** | **nixpkgs-unstable** | 按需：Flatpak 或 unstable |
| CLI / 开发工具 | **Distrobox 容器** | **HM + nixpkgs-unstable** | HM + nixpkgs-unstable |
| 系统级滚动组件（mesa/内核） | 不动 | unstable（只取需要的） | unstable（只取 mesa，§20.4） |
| 应用进配置版本控制 | ❌ **不在** | ✅ **全在** | ⚠️ 部分在 |
| 构建成本 | **零**（Flatpak 是下载） | 中（多数命中官方缓存） | 低 |
| 可复现 / 可回滚 | ❌ Flatpak 版本会漂 | ✅ 完全 | ⚠️ Flatpak 部分不保证 |
| 主题 / 字体 / **中文输入法** 一致性 | ❌ **要额外打通**（§7 的三个坑） | ✅ 天然一致 | ⚠️ Flatpak 那部分要打通 |
| 换机器重现 | ❌ 要手动重装 Flatpak | ✅ `nixos-rebuild` 一条命令 | ⚠️ 一半 |
| 最像 Aeon | ✅ **最像** | ❌ 哲学不同 | ⚠️ 折中 |

> [!NOTE]
> **三句话选路：**
>
> - **路 A**：你就是想要 Aeon 的体验，且**接受应用不进配置**。代价是 §7 的三个坑。
> - **路 B**：你要「基座稳定 + 应用最新」**且全部声明式、可复现、可回滚**。这是 NixOS 独有的，Aeon 做不到。
> - **路 C**：两者都要一点。**本文推荐这条** —— 系统级用 Nix（可复现），应用级按需（Flatpak 省构建，HM 省手动）。

### 24.4 路 A：Aeon 式（Flatpak 优先）—— 最像 Aeon，代价是 §7 的三个坑

核心原则：**`environment.systemPackages` 里只放「工具」，不放「应用」。**

```nix
# configuration.nix —— 路 A 的基座
{ config, pkgs, ... }:
{
  # ── 1) 基座只放工具（系统级、所有用户、不常换版本） ──
  environment.systemPackages = with pkgs; [
    git curl wget htop tree jq ripgrep fd unzip p7zip
    # ↑ 这些是「工具」。注意：没有 firefox / chromium / vscode / gimp
  ];

  # ── 2) 应用全部走 Flatpak ──
  xdg.portal = {
    enable = true;
    # extraPortals 断言非空：GNOME/KDE 会自动填，其它桌面要手写（§7）
    # extraPortals = [ pkgs.xdg-desktop-portal-gtk ];
    config.common.default = [ "gtk" ];
  };
  services.flatpak.enable = true;   # ⚠️ 有硬断言要求 xdg.portal.enable = true（§7）

  # ── 3) CLI / 开发走 Distrobox ──
  virtualisation.podman = {
    enable = true;
    dockerCompat = true;
    defaultNetwork.settings.dns_enabled = true;   # 容器内 DNS
  };
  environment.systemPackages = [ pkgs.distrobox ];   # 注意：与上面合并成一个列表
  users.users.<你>.extraGroups = [ "podman" ];
}
```

装应用（**这一步是命令式的，不在配置里** —— 这正是 Aeon 的做法）：

```bash
# 加 Flathub（services.flatpak 模块不管这件事，要自己来 —— §23.6）
flatpak remote-add --if-not-exists --user flathub https://dl.flathub.org/repo/flathub.flatpakrepo

# 装应用（会用上游最新版本，与基座版本无关）
flatpak install --user flathub org.mozilla.firefox
flatpak install --user flathub com.visualstudio.code
flatpak update          # 独立于 nixos-rebuild 更新
```

> [!WARNING]
> **路 A 的三个真实代价（§7 已详述，这里只列结论）：**
>
> 1. **主题 / 字体不一致** —— Flatpak 沙箱看不到宿主的部分字体与主题；CJK 字体要额外配（`fonts.packages` 对 Flatpak 不自动生效）。
> 2. **中文输入法在沙箱内可能失效** —— 这是普遍报告，`[未核实]` 但确实存在（§7、附录 C）。
> 3. **应用不在配置版本控制里** —— 换机器时 `nixos-rebuild` **不会**帮你装回 Flatpak；你要手动重装一遍。
>
> **还有一条 Aeon 有、NixOS 没有的**：Aeon 的 GNOME Software 被**故意配置成只能装 Flatpak**（防止你误装进基座）。NixOS 上没有这种「防呆」，**全靠自律** —— 你随时可以 `environment.systemPackages = [ pkgs.firefox ]` 把它塞回基座。

### 24.5 路 B：双 nixpkgs —— NixOS 原生做法（Home Manager 官方 FAQ 给的写法）

这是**官方文档明文推荐**的做法。Home Manager 的 FAQ 里有一节就叫 *"How do I install packages from Nixpkgs unstable?"*（`[官方]` <https://github.com/nix-community/home-manager/blob/release-26.05/docs/manual/faq/unstable.md>）：

> *"If you are using a stable version of Nixpkgs but would like to install some particular packages from Nixpkgs unstable -- or some other channel -- then you can import the unstable Nixpkgs and refer to its packages within your configuration."*

#### 24.5.1 flake.nix：两个 nixpkgs 输入

```nix
{
  inputs = {
    # 基座：稳定
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    # 应用：最新（注意分支名 —— 官方 FAQ 用的是 nixpkgs-unstable）
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    # Home Manager：分支要和基座对齐，且 follow 基座
    home-manager = {
      url = "github:nix-community/home-manager/release-26.05";
      inputs.nixpkgs.follows = "nixpkgs";   # ← 见 §20.6，漏了会多拉一份 nixpkgs
    };
  };

  outputs = { nixpkgs, nixpkgs-unstable, home-manager, ... }:
  let
    system = "x86_64-linux";
  in {
    nixosConfigurations.desktop = nixpkgs.lib.nixosSystem {
      inherit system;
      modules = [
        ./configuration.nix
        home-manager.nixosModules.home-manager
        ({ config, ... }: {
          # ── 官方 FAQ 的写法：把 unstable 传给 HM ──
          home-manager.extraSpecialArgs = {
            pkgsUnstable = import nixpkgs-unstable {
              inherit system;
              # ★★ 关键两行：把基座的 config / overlays 一起传进去 ★★
              config   = config.nixpkgs.config;
              overlays = config.nixpkgs.overlays;
            };

            # 如果你的 nixpkgs 配置是默认的（没有 allowUnfree 之类），
            # 官方 FAQ 说可以用这一行代替上面整个 import：
            # pkgsUnstable = nixpkgs-unstable.legacyPackages.${system};
          };
        })
      ];
    };
  };
}
```

#### 24.5.2 home.nix：用 `pkgsUnstable` 装应用

```nix
# home.nix —— 应用全部来自 unstable，基座仍是 26.05
{ pkgs, pkgsUnstable, ... }:
{
  # 基座自带的 pkgs（26.05）—— 放「和系统配套」的东西
  home.packages = with pkgs; [
    # 一般不放应用
  ];

  # 应用全部来自 unstable —— 追新
  home.packages = with pkgsUnstable; [
    firefox
    chromium
    vscode
    obs-studio
    gimp
    libreoffice
  ];

  # 想要系统级的（所有用户可见）就放 systemPackages，见 §20.4
}
```

> [!IMPORTANT]
> **`config` 和 `overlays` 那两行是官方 FAQ 明确写的，不是可选项。**
>
> 如果你只写 `import nixpkgs-unstable { inherit system; }`，那么 `pkgsUnstable` 会用**默认**的 nixpkgs 配置 —— 后果是：
>
> - 你的基座开了 `nixpkgs.config.allowUnfree = true`，但 `pkgsUnstable.vscode` 会**求值失败**（因为 unstable 那份没开 unfree）
> - 你基座上的 overlay（比如 §20 的 mesa 覆盖）在 `pkgsUnstable` 里**不存在**
>
> 报错信息通常是 *"Package 'vscode' has an unfree license"*，看到这个就回来检查这两行。

#### 24.5.3 另一种写法：让**整个 Home Manager** 用 unstable

如果你想要「**HM 管的全部应用**都追新」，而不是逐个指定 `pkgsUnstable.xxx`，可以换掉 HM 的 nixpkgs。机制（源码级核实，`[核实·源码: home-manager/release-26.05/modules/modules.nix]`）：

```nix
# HM 内部的默认值（mkDefault，所以你可以覆盖）：
_module.args.pkgsPath = lib.mkDefault (
  if lib.versionAtLeast config.home.stateVersion "20.09" then pkgs.path else <nixpkgs>
);
```

**因为它是 `mkDefault`，所以可以覆盖：**

```nix
({ config, inputs, ... }: {
  home-manager = {
    # ① 必须关掉 useGlobalPkgs —— 否则 nixpkgs.* 选项被禁用（见下方警告框）
    useGlobalPkgs = false;
    # ② 让 HM 用 unstable 的 nixpkgs 源
    sharedModules = [
      { _module.args.pkgsPath = inputs.nixpkgs-unstable.outPath; }
    ];
    # ③ 之后 HM 里的 `pkgs` 就是 unstable 了
    users.<你> = { pkgs, ... }: {
      home.packages = with pkgs; [ firefox vscode ];   # 都来自 unstable
    };
  };
})
```

> [!WARNING]
> **`home-manager.useGlobalPkgs = true` 时，`nixpkgs.*` 选项是被禁用的。**
>
> nixpkgs 的 HM 模块里有一条显式断言 + 警告（`[核实·源码: home-manager/release-26.05/modules/misc/nixpkgs-disabled.nix]`）：
>
> ```
> assertion = cfg.config == null || cfg.overlays == null;
> message = "`nixpkgs` options are disabled when `home-manager.useGlobalPkgs` is enabled.";
> ```
>
> 所以「改 `pkgsPath` 但没关 `useGlobalPkgs`」= **改了没用**，而且你会得到一条 warning。
>
> **代价对比**：
>
> | 写法 | HM 的 `pkgs` | 代价 |
> |---|---|---|
> | `useGlobalPkgs = true` + `extraSpecialArgs.pkgsUnstable`（§24.5.1） | 系统（26.05） | 无额外代价；但要逐个写 `pkgsUnstable.xxx` |
> | `useGlobalPkgs = false` + `pkgsPath = unstable` | unstable | **HM 会自己 `import nixpkgs`** → **多一次 nixpkgs 求值**（内存/时间），且 HM 的包与系统的包**哈希不同、无法共享**（同一个 Firefox 会被 build 两份） |

### 24.6 路 C：混合（本文推荐）

分三层，每层选不同的「新鲜度」：

| 层 | 来源 | 为什么这么选 |
|---|---|---|
| **内核 / 驱动 / systemd / 引导** | **26.05（基座）** | 必须和基座配套；跨源拿这些有配对风险（§11.2） |
| **mesa / Vulkan** | **只这一个取 unstable**（§20.4 的三种写法） | 显卡驱动是唯一「追新有实质收益」的系统级组件（新游戏/新 GPU 需要新 mesa） |
| **系统级应用**（需要所有用户可见） | 26.05 或 `pkgsUnstable`（§20.4） | 声明式、进配置、可回滚 |
| **用户级 GUI 应用** | **Flatpak**（零构建、追新）或 **HM + unstable**（可复现） | 你自己权衡 |
| **CLI / 开发工具** | **HM + nixpkgs-unstable** | 免 root、用户级回滚（§19.4 的 5 项好处） |

> [!WARNING]
> **2026-10-12 第八轮修正：上表第二行的「只把 mesa 取 unstable」有风险，请按下面两种方式之一改。**
>
> **官方在 `sec-gpu-accel-common-issues` 明确警告**（原文见 §32.6）：
> *"The ICD mechanism used by OpenCL and Vulkan loads runtimes into its address space using `dlopen`. **Mixing an ICD loader mechanism and runtimes from different version of nixpkgs may not work.** … **Unfortunately, the loader will generally be quiet about such issues.**"*
>
> **问题**：`dlopen` 是**运行时**加载，**不受 Nix 构建期依赖追踪保护**。只把 `mesa` 换成 unstable，而 `vulkan-loader` / `libdrm` 仍是 26.05 → **glibc 符号缺失 → loader 不报错 → 硬件加速静默失效**。
>
> **两种改法**：
>
> | 改法 | 做法 | 代价 |
> |---|---|---|
> | **① 整条链同源（推荐）** | `mesa` + `vulkan-loader` + `libdrm` + `libva` **一起**取 unstable | 多拉几个包，但**ICD 链完整** |
> | **② 不滚图形栈** | 内核保持基座；**图形栈走 Flatpak 应用**（Flatpak 自带 runtime，不受 nixpkgs glibc 影响） | 系统级 GPU 加速停在 26.05 的 mesa |
>
> **验证命令**（改完必跑）：
> ```bash
> LD_DEBUG=files clinfo 2>&1 | grep -i "cannot\|error"   # 应无输出
> vulkaninfo --summary | head -20                        # 不应出现 llvmpipe / lavapipe
> ```
> **完整分析见 §32.6。**

完整可抄的三层配置：

```nix
# ─────────── flake.nix ───────────
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    home-manager = {
      url = "github:nix-community/home-manager/release-26.05";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  outputs = { nixpkgs, nixpkgs-unstable, home-manager, ... }:
  let system = "x86_64-linux"; in {
    nixosConfigurations.desktop = nixpkgs.lib.nixosSystem {
      inherit system;
      modules = [
        ./configuration.nix
        home-manager.nixosModules.home-manager
        ({ config, ... }: {
          home-manager = {
            useGlobalPkgs = true;
            useUserPackages = true;
            extraSpecialArgs = {
              pkgsUnstable = import nixpkgs-unstable {
                inherit system;
                config   = config.nixpkgs.config;
                overlays = config.nixpkgs.overlays;
              };
            };
          };
        })
      ];
    };
  };
}
```

```nix
# ─────────── configuration.nix（基座：稳定 + 极简）───────────
{ pkgs, pkgsUnstable, ... }:
{
  # 只让 mesa 走 unstable（§20.4.1 推荐的 _module.args 路线）
  _module.args.pkgsUnstable = pkgsUnstable;

  hardware.graphics = {
    enable = true;
    enable32Bit = true;
    package = pkgsUnstable.mesa;                       # ← 系统级 mesa 追新
    package32 = pkgsUnstable.pkgsi686Linux.mesa;       # ← 32/64 必须一起换
  };

  # 基座只放工具
  environment.systemPackages = with pkgs; [
    git curl wget htop jq ripgrep fd
  ];

  # 自动更新：Aeon 式的「每天下载，重启生效」
  system.autoUpgrade = {
    enable = true;
    operation = "boot";          # ← 关键：不影响运行中的系统
    flake = "/etc/nixos";
    dates = "04:40";
    randomizedDelaySec = "30min";
    allowReboot = false;
  };

  # Flatpak 兜底（专有软件 / 只发 Flatpak 的）
  xdg.portal = { enable = true; config.common.default = [ "gtk" ]; };
  services.flatpak.enable = true;
}
```

```nix
# ─────────── home.nix（应用层：追新）───────────
{ pkgs, pkgsUnstable, ... }:
{
  # CLI / 开发工具：unstable
  home.packages = with pkgsUnstable; [
    neovim
    helix
    nodejs_24
    bun
    uv
    rustup
    go
  ];

  # GUI 应用：两条路二选一
  #   ① 想可复现 → 用 unstable 的 nixpkgs
  home.packages = with pkgsUnstable; [ firefox ];
  #   ② 想省构建 → 用 Flatpak（配置见 §24.4，装的时候 flatpak install）
}
```

> [!TIP]
> **路 C 的「稳定」是怎么保证的？**
>
> 三层各自有各自的稳定机制，**互不牵连**：
>
> - **基座**：26.05 冻结 + 官方缓存 → 不会突然坏
> - **mesa**：unstable 但**只影响图形栈** → 坏了 `nixos-rebuild --rollback` 一条命令回去（§11.5）
> - **应用**：Flatpak 或 HM → 坏了单独回滚，**碰不到基座**
>
> **这正是 Aeon 的设计意图**（*"every extra package in the host incurs extra risk of instability"*），只是 NixOS 把「隔离」做得更彻底 —— **Aeon 靠容器隔离，NixOS 靠 store 路径隔离。**

### 24.7 更新与回滚：Aeon 的两条机制在 NixOS 上的对应

| Aeon 机制 | NixOS 对应 | 配置/命令 |
|---|---|---|
| 每天自动跑 `transactional-update` | `system.autoUpgrade.enable = true` + `dates = "04:40"` | §24.6 的配置 |
| 更新**不影响运行中的系统**，重启才生效 | `operation = "boot"`（enum 只有 `switch`/`boot`） | 同上 |
| 更新失败 → 丢弃快照 | build 失败 → 不生成新 generation | 天然 |
| 启动检测到问题 → **自动回滚** | 启动菜单选上一个 generation（**手动**） | `boot.loader.systemd-boot.configurationLimit = 10` |
| `transactional-update rollback` | `nixos-rebuild switch --rollback` | §11.5 |
| Btrfs snapshot 保留策略 | generation 保留（`configurationLimit` + GC） | §23.3 |
| 手动装包进基座 → 需要**重建快照 + 重启** | `environment.systemPackages` → 只需 rebuild（**不用重启**） | — |

> [!IMPORTANT]
> **两条比 Aeon 强、一条比 Aeon 弱：**
>
> ✅ **强 1：不需要重启。** Aeon 的 `transactional-update` 必须重启才能用上新软件；NixOS 的 `switch` 立刻生效（除内核/驱动）。
> ✅ **强 2：回滚粒度。** Aeon 只能整镜像回滚；NixOS 可以**只回滚一个包**（`nixos-rebuild` 到上一个 generation，或临时 `nix shell` 旧版本）。
> ⚠️ **弱 1：没有「启动自动回滚」。** Aeon 在启动检测到失败时会**自动**回到上一个快照；NixOS 需要你**手动**在启动菜单里选（或者用 §11.5 的三级逃生通道）。**这是 NixOS 唯一明显不如 Aeon 的一项。**
>
> 想补上这一条，可以：
> - 用 `systemd-boot` 的 `boot.loader.systemd-boot.configurationLimit` 保证旧 generation 一定在
> - 或者上 **`systemd-boot` + `boot.loader.efi.canTouchEfiVariables`** 配合 `lanzaboote`（§23.13）做更完整的引导链
> - **但真正的「启动失败自动回滚」在 NixOS 上没有开箱实现**（`[未核实]` 是否有第三方方案；已知 nixpkgs 无此模块）

### 24.8 基座该留什么、不该留什么

Aeon 的判据（原文）：*"only recommended for **drivers, kernel modules, VPN clients**, and other low-level packages that **have to integrate tightly with the operating system**"*。

翻译成 NixOS 的判据：

| 该进基座（`environment.systemPackages`） | 不该进基座 |
|---|---|
| 内核 / 内核模块 / 固件 | **GUI 应用**（浏览器、编辑器、IDE、游戏启动器） |
| 图形驱动（mesa / amdgpu / vulkan） | **CLI 工具**（`jq` / `ripgrep` / `neovim` —— 放 HM） |
| 桌面环境本体（GNOME / KDE） | **语言工具链**（node / python / rust / go —— 放 HM 或 `nix shell`） |
| 显示管理器 / 网络管理器 / 音频栈 | **媒体应用**（OBS / GIMP / LibreOffice —— Flatpak 或 HM） |
| 必须全局可见的工具（`git` / `curl` / `htop`） | **一次性的东西**（`nix shell` 用完即弃） |
| `programs.*` 模块启用的东西（`programs.steam` 等） | **`nix profile install` 装的任何东西**（命令式、会漂） |

> [!NOTE]
> **注意 NixOS 的判据和 Aeon 有一处关键差异。**
>
> Aeon 说「不要往基座装包，因为**每次多一个包就多一分不稳定风险**」—— 这个理由在 NixOS 上**只对一半**：
>
> - **对的一半**：基座包越多，`nixos-rebuild` 越慢、闭包越大、`nix flake update` 时重建面越广（§22.2 的 666 个 derivation 就是这么来的）。
> - **不对的一半**：NixOS 的基座包**不会互相污染**（每个包独立闭包、独立 store 路径），所以「装一个包搞坏另一个」在 NixOS 上基本不会发生。
>
> **所以 NixOS 的判据应该是「作用域」而不是「风险」**：全局可见的进基座，个人的进 HM，一次性的进 `nix shell`。

### 24.9 四条反模式

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | **以为「稳定基座」= 冻结版本** | 会误以为必须用 26.05 才能稳定，从而错过「滚动 + 原子回滚」这条路 | 先想清楚你要的是**冻结式稳定**还是**原子式稳定**（§24.1），两者 NixOS 都能给 |
| 2 | **照抄 Aeon 的「Flatpak 是唯一应用渠道」** | 失去 Nix 的可复现性 + 付 §7 的三个坑（主题/字体/**输入法**）+ 换机器要手动重装 | NixOS 上 Flatpak 是**兜底**，不是主渠道（§23.6、§24.3） |
| 3 | **`pkgsUnstable` 不传 `config.nixpkgs.config`** | unfree 包（vscode 等）**求值直接失败**，报 *"has an unfree license"* | 照抄官方 FAQ 的 `config = config.nixpkgs.config; overlays = config.nixpkgs.overlays;`（§24.5.1） |
| 4 | **改 `pkgsPath` 却忘了 `useGlobalPkgs = false`** | 改了没用，还会收到一条 warning：*"`nixpkgs` options are disabled when `home-manager.useGlobalPkgs` is enabled"* | 两者必须成对出现（§24.5.3） |

### 24.10 一页裁决表

| 你真正想要的 | 走哪条路 | 关键配置 |
|---|---|---|
| **就是想要 Aeon 的体验** | **路 A**（Flatpak 优先） | §24.4；基座只放工具 + `services.flatpak` + Distrobox |
| **要「基座稳定 + 应用最新」且全部声明式可复现** | **路 B**（双 nixpkgs） | §24.5；`nixpkgs-unstable` input + `home-manager.extraSpecialArgs` |
| **两者都要一点，且不想付构建成本** | **路 C**（混合，**推荐**） | §24.6；mesa 取 unstable + 应用按需 Flatpak / HM |
| **想要 Aeon 那种「滚动但原子」的稳定** | 用 `nixos-unstable` 做基座 | 靠 generations 回滚（§11.5）；不推荐给新手 |
| **只要最新 mesa，其它都不动** | 最小改动 | §20.4 的三种写法之一 |
| **只想让某个包用最新** | `pkgsUnstable.<包>` 单点取用 | §20.4 |

> [!IMPORTANT]
> **一句话回答你的问题：**
>
> **Aeon 的「稳定基座 + 最新应用」在 NixOS 上有三条路，而 NixOS 比 Aeon 多一个能力 —— 可以让基座、组件、应用各自有各自的新鲜度和回滚粒度。**
>
> - **路 A（Aeon 式）**：基座极简 + Flatpak 装应用 + Distrobox 装 CLI。**最像 Aeon**，代价是应用不进配置、要付 §7 的坑。
> - **路 B（双 nixpkgs）**：基座 26.05 + 第二个 `nixpkgs-unstable` 输入只给应用。**官方 FAQ 明文推荐**，全部声明式可复现。代价是构建/eval 成本。
> - **路 C（混合，推荐）**：基座 26.05 + **只把 mesa 取 unstable** + 应用按需（Flatpak 省构建 / HM 保可复现）。**这是「Aeon 的设计意图」+「NixOS 的可复现性」的结合。**
>
> **还要记住一句前提修正**：Aeon 的基座**本身是滚动的 Tumbleweed**。它的稳定来自**原子 + 极简 + 隔离**，不是来自版本冻结。**你在 NixOS 上真正要复刻的是这三件机制，而不是「用一个冻结的版本」** —— 而这三件机制，NixOS 靠 generations + store 路径隔离，做得比 Aeon 更彻底。

---

## 二十五、二进位包与依赖问题：完整手册（本章回答「NixOS 如何使用二进位包？如何解决依赖问题？」）

你的原话是：**「NixOS 如何使用二进位包？如何解决依赖问题？给出全面的方式，考虑所有的可能和程式类型、常见依赖」**。

这一章是一份**速查手册**，不是教程。结构是：

| 你要做的事 | 跳到这里 |
|---|---|
| 先搞清楚**到底缺什么** | §25.3 诊断表 |
| 看**有几种方案**、按侵入性排序 | §25.4 方案总表 |
| 看**每种方案怎么配** | §25.5 逐方案详解（14 种） |
| 抄一份**常见依赖清单** | §25.6 依赖清单 |
| 按**程序类型**查怎么办 | §25.7 程序类型对照表 |
| 看**哪些问题根本解决不了** | §25.8 三类死路 |
| 避开**六个反模式** | §25.9 |

> [!IMPORTANT]
> **本章有一条 26.05 的时效性事实，必须先说：`xorg` 包集已被弃用，`pkgs.xorg.libX11` 这类写法现在会打弃用警告。** 详见 §25.2。**网上所有 nix-ld 教程（包括大量 LLM 的训练数据）写的都是旧写法。**

### 25.1 先把问题拆开：「二进位包」有 6 种来源，「依赖问题」有 6 类

**二进位包按来源分 6 种**（决定了你用哪种方案）：

| 来源 | 例子 | 典型症状 |
|---|---|---|
| ① **nixpkgs 里就有** | `pkgs.firefox` | 无 —— 直接用 |
| ② **官方预编译二进制** | GitHub Release 里的 `./myapp`、`codex` 的 Rust 二进制 | `No such file or directory` |
| ③ **第三方包管理器下载的** | `npm` 装的原生模块、`pip` 装的 manylinux wheel | `libfoo.so.1: cannot open shared object file` |
| ④ **AppImage** | 只发 AppImage 的软件 | 需要 `appimage-run` |
| ⑤ **安装器 / 归档** | `.run`、`.deb`、`.rpm`、`.tar.gz` | 装不进 `/usr` |
| ⑥ **容器镜像 / 跨架构** | Docker 镜像、aarch64 二进制 | 需要容器或 qemu |

**依赖问题按根因分 6 类**（决定了你能不能修）：

| # | 根因 | 报错长什么样 | 能修吗 |
|---|---|---|---|
| 1 | **动态链接器路径写死** | `No such file or directory`（其实是 `/lib64/ld-linux-x86-64.so.2` 不存在） | ✅ 容易（nix-ld） |
| 2 | **共享库缺失** | `error while loading shared libraries: libfoo.so.1` | ✅ 容易（nix-ld + libraries） |
| 3 | **文件系统布局假设** | 找不到 `/usr/share/xxx`、`/opt/xxx`、`/usr/lib/xxx` | ✅ 中等（FHS env） |
| 4 | **glibc 版本不匹配** | `version 'GLIBC_2.38' not found` | ⚠️ 难（FHS env / 容器） |
| 5 | **运行时外部命令 / shebang** | `#!/bin/bash: bad interpreter`、`python3: command not found` | ✅ 容易（wrapProgram） |
| 6 | **内核接口 / setuid / 驱动** | `modprobe: module not found`、权限失败 | ❌ **不能这么修**（§25.8） |

> [!TIP]
> **第 1 类和第 2 类是 90% 的情况，`programs.nix-ld` 一条配置就解决。** 第 4 类（glibc 版本）是最麻烦的，因为它意味着你连「用 nix-ld 换个链接器」都不够 —— 程序需要**一整套配套的 glibc 环境**。
>
> **判断方法**：看报错里是 `cannot open shared object file`（→ 第 2 类，好办）还是 `version 'GLIBC_2.xx' not found`（→ 第 4 类，难办）。

### 25.2 ★ 26.05 时效性变化：`xorg` 包集已弃用（本章最重要的提醒）

**26.05 的官方 release notes 里有一条**（`[核实·源码: doc/release-notes/rl-2605.section.md:235]`）：

> *"The `xorg` package set has been deprecated, packages have moved to the top level."*

`pkgs/top-level/aliases.nix:2361` 里有对应的弃用别名（`[核实·源码]`，标注日期 **2026-01-29**）：

```nix
xorg = # Added 2026-01-29
  lib.mapAttrs
    (name: value:
      warnAlias "The xorg package set has been deprecated, 'xorg.${name}' has been renamed to '${name}'" value)
    { inherit appres bdftopcf bitmap ... libxcb libxshmfence ... xauth xrandr xdpyinfo ...; };
```

**所有 `libX*`（大写 X）也改名了**（`aliases.nix:1178-1207`，标注 **2026-02-06**）：

| 旧写法（网上教程里的） | **26.05 正确写法** |
|---|---|
| `pkgs.xorg.libX11` | **`pkgs.libx11`** |
| `pkgs.xorg.libXext` | **`pkgs.libxext`** |
| `pkgs.xorg.libXrender` | **`pkgs.libxrender`** |
| `pkgs.xorg.libXi` | **`pkgs.libxi`** |
| `pkgs.xorg.libXcomposite` | **`pkgs.libxcomposite`** |
| `pkgs.xorg.libXdamage` | **`pkgs.libxdamage`** |
| `pkgs.xorg.libXrandr` | **`pkgs.libxrandr`** |
| `pkgs.xorg.libXcursor` | **`pkgs.libxcursor`** |
| `pkgs.xorg.libXfixes` | **`pkgs.libxfixes`** |
| `pkgs.xorg.libXtst` | **`pkgs.libxtst`** |
| `pkgs.xorg.libXScrnSaver` | **`pkgs.libxscrnsaver`** |
| `pkgs.xorg.libXxf86vm` | **`pkgs.libxxf86vm`** |
| `pkgs.xorg.libXft` | **`pkgs.libxft`** |
| `pkgs.xorg.libXinerama` | **`pkgs.libxinerama`** |
| `pkgs.xorg.libXmu` | **`pkgs.libxmu`** |
| `pkgs.xorg.libXpm` | **`pkgs.libxpm`** |
| `pkgs.xorg.libXt` | **`pkgs.libxt`** |
| `pkgs.xorg.libXv` / `libXvMC` | **`pkgs.libxv` / `pkgs.libxvmc`** |
| `pkgs.xorg.libXpresent` / `libXres` / `libXp` | **`pkgs.libxpresent` / `pkgs.libxres` / `pkgs.libxp`** |
| `pkgs.xorg.libXaw` / `libXau` / `libXdmcp` | **`pkgs.libxaw` / `pkgs.libxau` / `pkgs.libxdmcp`** |
| `pkgs.xorg.libXfont` / `libXfont2` | **`pkgs.libxfont_1` / `pkgs.libxfont_2`**（注意下标变了） |
| `pkgs.xorg.libxcb` / `libpciaccess` / `libxshmfence` | **`pkgs.libxcb` / `pkgs.libpciaccess` / `pkgs.libxshmfence`** |
| `pkgs.xorg.pixman` / `libfontenc` / `libxkbfile` / `libxcvt` / `libdmx` | **`pkgs.pixman` / `pkgs.libfontenc` / `pkgs.libxkbfile` / `pkgs.libxcvt` / `pkgs.libdmx`** |
| `pkgs.xorg.xorgproto` | **`pkgs.xorgproto`** |
| `pkgs.xorg.xauth` / `xrandr` / `xdpyinfo` / `xinput` / `xmodmap` / `xprop` / `xrdb` / `xset` | 全部提到顶层：`pkgs.xauth` / `pkgs.xrandr` / … |
| `pkgs.xorg.xinit` / `xkbcomp` / `setxkbmap` / `xkill` / `xeyes` / … | 同样提到顶层 |

> [!WARNING]
> **两条实用推论：**
>
> 1. **旧写法仍然能求值**（是 `warnAlias` 不是 `throw`），但会**打弃用警告**。所以你的 `nixos-rebuild` 会刷屏，而且**未来版本会变成硬错误**。
> 2. **`libXfont` 的下标变了** —— 旧 `libXfont` 现在是 `libxfont_1`，旧 `libXfont2` 是 `libxfont_2`。**照抄旧教程会拿错版本。**
>
> **你如果从网上抄 nix-ld 的 `libraries` 列表，大概率会拿到一堆弃用警告。** 本章 §25.6 的清单已经全部用 26.05 的新名字。

### 25.3 诊断：先搞清楚「缺什么」（所有方案的前提）

**不要猜。按下面顺序跑，每一步都会缩小范围。**

| 症状 / 目的 | 命令 | 看什么 |
|---|---|---|
| **程序是什么类型** | `file ./myapp` | 是否 `ELF 64-bit ... dynamically linked`；是否 `statically linked` |
| **动态链接器路径写死在哪** | `file ./myapp` 或 `patchelf --print-interpreter ./myapp` | 输出 `/lib64/ld-linux-x86-64.so.2` = 第 1 类问题 |
| **缺哪些库**（静态看） | `ldd ./myapp` | 任何 `not found` 就是第 2 类问题 |
| **缺哪些库**（更可靠） | `readelf -d ./myapp \| grep NEEDED` | 列出所有 `NEEDED` 的 SONAME |
| **运行时才加载的库**（dlopen） | `LD_DEBUG=libs ./myapp 2>&1 \| grep -iE "not found\|cannot open"` | dlopen 的库不会出现在 `ldd` 里 |
| **它到底在哪些路径找东西** | `strace -f -e trace=openat ./myapp 2>&1 \| grep -E "\.so\|ENOENT"` | 硬编码的 `/usr/lib`、`/opt/xxx` |
| **有没有硬编码 FHS 路径** | `strings ./myapp \| grep -E "^/(usr\|opt\|lib)"` | `/usr/share/...`、`/opt/...` |
| **是不是 glibc 版本问题** | `./myapp` 报 `version 'GLIBC_2.xx' not found` | 第 4 类问题（难） |
| **反查某个 `.so` 在哪个包** | `nix-locate --top-level libfoo.so.1` | 得到 `pkgs.xxx` |
| **反查某个可执行文件在哪个包** | `nix-locate --top-level bin/mycmd` | 同上 |
| **列出程序需要的全部库（自动）** | `nix-alien-find-libs ./myapp`（§25.5.10） | 自动枚举 + 交互选择 |
| **看链接器实际行为** | `LD_DEBUG=libs ./myapp 2>&1 \| head -50` | 搜索顺序、`trying file=...` |

> [!TIP]
> **`ldd` 在 NixOS 上对预编译二进制经常直接失败**（因为它自己也是脚本，依赖 `/lib64/ld-linux...`）。这种情况用 **`readelf -d`** 或 **`patchelf --print-needed`**，它们不执行程序，只读 ELF 头。
>
> 装 `nix-locate` 需要先建索引：`nix-index`（`pkgs.nix-index`）→ `nix-index` 命令生成 `~/.cache/nix-index/files`。也可以直接用 [nix-index-database](https://github.com/Mic92/nix-index-database) 的预建索引（免生成）。

### 25.4 方案总表：14 种方法，按「侵入性」从低到高

**核心原则：从上往下试。越靠上的越「Nix 原生」，越可复现、越可回滚。**

| # | 方案 | 解决哪几类问题 | 侵入性 | 可复现 | 适用场景 |
|---|---|---|---|---|---|
| 1 | **`nixpkgs` 里找** | 全部 | 无 | ✅ 完全 | **永远先试这个** |
| 2 | `nix run` / `nix shell` | 全部 | 极低（临时） | ✅ | 试一下、跑一次 |
| 3 | `nix profile install` | 全部 | 低（命令式） | ⚠️ 不进配置 | 长期用但不想改配置 |
| 4 | **`programs.nix-ld`** | ①②⑤ | 低 | ✅ | **预编译二进制、npm/pip 原生模块** |
| 5 | **`programs.appimage`** | ①④ | 低 | ✅ | AppImage |
| 6 | **`buildFHSEnv`** | ①②③④⑤ | 中 | ✅ | 需要完整 FHS 目录树 |
| 7 | **`steam-run`** | ①②③④⑤ | 中 | ⚠️ 依赖 Steam | 临时借 Steam 的 FHS |
| 8 | `patchelf` 手工改 | ①②③ | 中 | ⚠️ 改动不持久 | 一次性修、调试 |
| 9 | `autoPatchelfHook` | ①②③ | — | ✅ | **打包时**用（写 derivation） |
| 10 | **`nix-alien`** | ①②③ | 低（自动） | ⚠️ | **自动探测缺失库** |
| 11 | **Distrobox 容器** | ①②③④⑤⑥ | 中 | ⚠️ 容器内不受管 | 复杂软件、开发环境 |
| 12 | Docker / Podman | ①②③④⑤⑥ | 中 | ⚠️ | 服务、隔离环境 |
| 13 | Flatpak | ①④ | 低 | ⚠️ | 有 Flatpak 版的 GUI 软件 |
| 14 | `binfmt` + qemu | ⑥（跨架构） | 低 | ✅ | aarch64 二进制在 x86_64 上跑 |

> [!IMPORTANT]
> **这张表的使用方式是「从上往下排除」，不是「挑一个喜欢的」。**
>
> 最常见的错误：**直接上 `buildFHSEnv`**。它很重（启动要 bwrap + init 脚本），而且有官方列出的三个弱点（§25.5.6）。**一个 `nix-shell -p` 能解决的问题不要用 FHS env。**

### 25.5 逐方案详解

#### 25.5.1 第一优先：先看 nixpkgs 里有没有

```bash
# 命令行搜
nix search nixpkgs firefox

# 网页搜（更好用，有版本历史）
#   https://search.nixos.org/packages
#   https://nixhub.io/            ← 查「某个版本」的包

# 本地装了吗
nix-env -q | grep firefox

# 这个包提供哪些可执行文件
nix-build '<nixpkgs>' -A firefox --no-out-link | xargs -I{} ls {}/bin
```

**判据**：如果 nixpkgs 里有，**不要用后面任何一种方案**。这是唯一 100% 可复现、可回滚、有二进制缓存的路。

#### 25.5.2 `nix run` / `nix shell`（临时，最推荐用来「试」）

```bash
# 跑一次，不装
nix run nixpkgs#firefox
nix run nixpkgs#ffmpeg -- -i in.mp4 out.mkv

# 进一个临时 shell（可以连续跑多条）
nix shell nixpkgs#ffmpeg nixpkgs#imagemagick
# 退出后环境消失

# 旧语法（nix-shell，兼容性更好）
nix-shell -p ffmpeg imagemagick
```

**优点**：零残留、零配置。
**缺点**：每次都要重新求值（有 eval 缓存，通常 1–3 秒）。

#### 25.5.3 `nix profile install`（持久但命令式）

```bash
nix profile install nixpkgs#ffmpeg
nix profile list
nix profile remove ffmpeg
nix profile upgrade --all
```

> [!WARNING]
> **`nix profile` 是 NixOS 上的「最后手段」，不是首选。** 原因（§23.9 已详述）：
>
> - **不进配置** —— `nixos-rebuild` 不管它，换机器不会重现
> - **会漂** —— `nix profile upgrade` 单独更新，与系统版本脱钩
> - **与 `environment.systemPackages` 可能冲突** —— 同名命令两份
>
> **要持久化就用 Home Manager 的 `home.packages`（§19.4）。**

#### 25.5.4 ★ `programs.nix-ld` —— 预编译二进制的官方兜底（最常用）

**它是怎么工作的**（`[核实·源码: nixos/modules/programs/nix-ld.nix]` 全文）：

```nix
config = lib.mkIf config.programs.nix-ld.enable {
  environment.ldso = "${cfg.package}/libexec/nix-ld";       # ★ 关键 1
  environment.systemPackages = [ nix-ld-libraries ];
  environment.pathsToLink = [ "/share/nix-ld" ];
  environment.sessionVariables = {
    NIX_LD = "/run/current-system/sw/share/nix-ld/lib/ld.so";              # ★ 关键 2
    NIX_LD_LIBRARY_PATH = "/run/current-system/sw/share/nix-ld/lib";       # ★ 关键 3
  };
  programs.nix-ld.libraries = with pkgs; [ /* 14 个基础库，见下 */ ];
};
```

**三个关键点连起来看：**

| 机制 | 作用 |
|---|---|
| `environment.ldso = ".../nix-ld"` | 把 nix-ld 装到 **`/lib64/ld-linux-x86-64.so.2`**（FHS 标准位置） |
| `NIX_LD` | 告诉 nix-ld「真正的链接器在 store 里哪个路径」 |
| `NIX_LD_LIBRARY_PATH` | 额外的库搜索路径，**nix-ld 会在调用真实 ld 前把它改写成 `LD_LIBRARY_PATH`** |

`environment.ldso` 的机制值得单独看一眼（`[核实·源码: nixos/modules/config/ldso.nix]`）：

```nix
systemd.tmpfiles.rules =
  (if isNull config.environment.ldso then
     [ "r /${libDir}/${ldsoBasename} - - - - -" ]        # ← 为 null 时【主动删除】这个文件
   else
     [ "d /${libDir} 0755 root root - -"
       "L+ /${libDir}/${ldsoBasename} - - - - ${config.environment.ldso}" ])  # ← 否则建符号链接
```

> [!IMPORTANT]
> **反直觉事实：NixOS 不是「没有」`/lib64/ld-linux-x86-64.so.2`，而是有一条 tmpfiles 规则主动把它删掉**（`r` = remove）。
>
> 这就是为什么预编译二进制的报错是 `No such file or directory` 而不是 `cannot open shared object file` —— **文件管理器看到的是「文件不存在」**。
>
> 也解释了 `programs.nix-ld` 为什么能一行解决：**它只是把这条 `r` 规则换成 `L+`（建链接）。**

**`programs.nix-ld` 的全部选项**（只有三个）：

| 选项 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `enable` | bool | `false` | 开关 |
| `package` | package | `pkgs.nix-ld`（**2.0.6**） | 一般不用改 |
| `libraries` | list of package | **14 个基础库**（见下） | 追加的库 |

**14 个基础库全表**（`[核实·源码]`，模块在 `enable = true` 时无条件注入）：

```nix
programs.nix-ld.libraries = with pkgs; [
  zlib          # libz.so.1        —— 最常缺
  zstd          # libzstd.so.1
  stdenv.cc.cc  # libstdc++.so.6   —— C++ 程序必缺
  curl          # libcurl.so.4
  openssl       # libssl.so.3 / libcrypto.so.3
  attr          # libattr.so.1
  libssh        # libssh.so.4
  bzip2         # libbz2.so.1
  libxml2       # libxml2.so.2
  acl           # libacl.so.1
  libsodium     # libsodium.so.23
  util-linux    # libuuid.so.1 / libblkid.so.1
  xz            # liblzma.so.5
  systemd       # libudev.so.1 / libsystemd.so.0
];
```

**完整配置（推荐写法）：**

```nix
{
  programs.nix-ld = {
    enable = true;
    # libraries 是 listOf，所以这里是【追加】不是覆盖
    libraries = with pkgs; [
      # ── GUI / X11（26.05 新名字，见 §25.2）──
      libx11 libxext libxrender libxi libxcomposite libxdamage
      libxrandr libxcursor libxfixes libxtst libxscrnsaver libxxf86vm
      libxcb libxau libxdmcp libxshmfence
      # ── Wayland ──
      libxkbcommon wayland
      # ── GUI 工具包 ──
      gtk3 gdk-pixbuf cairo pango atk
      # ── 图形 / GPU ──
      libGL libgbm libdrm mesa vulkan-loader
      # ── 字体 ──
      freetype fontconfig
      # ── 音频 ──
      alsa-lib
      # ── 桌面集成 ──
      dbus expat nss nspr cups
    ];
  };
}
```

**`nix-ld` 的环境变量全表**（`[官方: nix-ld README]`）：

| 变量 | 作用 |
|---|---|
| `NIX_LD` | 真实动态链接器的路径 |
| `NIX_LD_{system}` | 同上，按平台指定（如 `NIX_LD_x86_64_linux`） |
| `NIX_LD_LIBRARY_PATH` | 额外库搜索路径（冒号分隔） |
| `NIX_LD_LIBRARY_PATH_{system}` | 同上，按平台 |
| `NIX_LD_LOG` | 日志级别：`error` / `warn` / `info` / `debug` / `trace` |

> [!DANGER]
> **`nix-ld` 有一条官方明确的限制，几乎所有人都踩过：**
>
> > *"Nix-ld is only used by **unpatched executables** that use the link loader at `/lib` or `/lib64`. **If you use for example python from nixpkgs then it will not pick up `NIX_LD_LIBRARY_PATH` and `NIX_LD`** since these types of binaries are configured to use a glibc from the nix store."*
>
> **翻译**：nixpkgs 里的 `python3` / `node` / `ruby` **不走 nix-ld**（它们已经指向 store 里的 glibc）。所以：
>
> - **`pip install` 装的 manylinux wheel 找不到库 → `nix-ld` 帮不了你**
> - **`npm` 装的原生模块加载失败 → 用 nixpkgs 的 `node` 时，`nix-ld` 也帮不了**
>
> 官方给的解法是**包一层 wrapper，显式设 `LD_LIBRARY_PATH`**：
>
> ```nix
> # 官方 README 给的写法
> (pkgs.writeShellScriptBin "pythonld" ''
>   export LD_LIBRARY_PATH=$NIX_LD_LIBRARY_PATH
>   exec -a "$0" ${pkgs.python3}/bin/python "$@"
> '')
> ```
>
> 然后 `pythonld -m venv myvenv` 建虚拟环境。**注意 `-a "$0"` 不能省**（官方原话：*"without the `-a "$0"` argument, your wrapper will be skipped"*）。
>
> **`nix-ld` 只在 x86_64 和 aarch64 上有效**（官方 README 注明）。

**`nix-ld` 不能做什么**（官方 README 明确列出）：

| 不能 | 为什么 |
|---|---|
| ❌ 在非 NixOS 上跑 | *"Normal Linux distributions will have their own link-loader. Replacing those with nix-ld will break the system."* |
| ❌ 让 AppImage 直接跑 | 用 `programs.appimage`（§25.5.5） |
| ❌ 让 nixpkgs 的 python/node 找到 pip/npm 装的库 | 见上方 DANGER |
| ❌ 修 glibc 版本不匹配 | 需要整套 glibc 环境 → FHS env / 容器 |
| ❌ 执行 setuid 二进制 | 见 §25.8 |

#### 25.5.5 `programs.appimage`（AppImage）

```nix
{
  programs.appimage = {
    enable = true;
    binfmt = true;          # ★ 注册 binfmt，双击可运行
    # package = pkgs.appimage-run.override {
    #   extraPkgs = pkgs: [ pkgs.ffmpeg pkgs.imagemagick ];   # 追加运行时依赖
    # };
  };
}
```

**模块做了什么**（`[核实·源码: nixos/modules/programs/appimage.nix]`）：

```nix
boot.binfmt.registrations = lib.mkIf cfg.binfmt (let
  appimage_common = {
    wrapInterpreterInShell = false;
    interpreter = lib.getExe cfg.package;
    recognitionType = "magic";
    offset = 0;
    mask = ''\xff\xff\xff\xff\x00\x00\x00\x00\xff\xff\xff'';
  };
in {
  appimage_type_1 = appimage_common // { magicOrExtension = ''\x7fELF....AI\x01''; };
  appimage_type_2 = appimage_common // { magicOrExtension = ''\x7fELF....AI\x02''; };
});
```

**三个选项**：`enable` / `binfmt` / `package`。

> [!TIP]
> **`binfmt = true` 是很多人漏掉的一步。** 只写 `enable = true` 的话你要手动 `appimage-run ./foo.AppImage`；开了 `binfmt`，内核按 ELF 魔数（`AI\x01` / `AI\x02`）识别并自动调 `appimage-run`，**文件管理器里双击就能跑**。
>
> 注册了 **Type 1 和 Type 2 两种** AppImage 格式（这是 AppImage 的两个版本规范）。

#### 25.5.6 ★ `buildFHSEnv` —— 需要完整 FHS 目录树时

**先记一个 26.05 的变化**（`[核实·源码: pkgs/top-level/all-packages.nix:360-362]`）：

```nix
buildFHSEnv = buildFHSEnvBubblewrap;
buildFHSEnvChroot = callPackage ../build-support/build-fhsenv-chroot { };  # Deprecated; use buildFHSEnv/buildFHSEnvBubblewrap
buildFHSEnvBubblewrap = callPackage ../build-support/build-fhsenv-bubblewrap { };
```

**所以 `pkgs.buildFHSEnv` 现在就是 `buildFHSEnvBubblewrap` 的别名。** 老的 chroot 实现已弃用（bubblewrap 实现不需要 root，是纯用户态）。

**`buildFHSEnv` 的完整参数**（`[核实·源码: pkgs/build-support/build-fhsenv-bubblewrap/buildFHSEnv.nix]`）：

| 参数 | 默认 | 说明 |
|---|---|---|
| `profile` | `""` | 追加到 `/etc/profile` 的 shell 片段 |
| **`targetPkgs`** | `pkgs: [ ]` | **按宿主架构装一次的包**（通常是程序本体） |
| **`multiPkgs`** | `pkgs: [ ]` | **库**；在 x86_64 上**装两次**（64 位 + 32 位） |
| `multiArch` | `false` | 是否包含 32 位包（只在 x86_64 上有效） |
| `includeClosures` | `false` | 是否把包的完整闭包都塞进去（体积换保险） |
| `nativeBuildInputs` | `[ ]` | — |
| `extraBuildCommands` | `""` | 额外构建命令 |
| `extraBuildCommandsMulti` | `""` | 仅多架构时的额外命令 |
| `extraOutputsToInstall` | `[ ]` | — |

**`buildFHSEnvBubblewrap` 额外提供的参数**（`[核实·源码: .../build-fhsenv-bubblewrap/default.nix]`）：

| 参数 | 默认 | 说明 |
|---|---|---|
| `runScript` | `"bash"` | 默认执行的命令 |
| `executableName` | `pname` 或 `name` | 生成的二进制名 |
| `extraInstallCommands` | `""` | 装完之后额外跑的构建命令 |
| `extraPreBwrapCmds` | `""` | bwrap 启动前跑的命令 |
| `extraBwrapArgs` | `[ ]` | 额外传给 bwrap 的参数 |
| `unshareUser` / `unshareIpc` / `unsharePid` / `unshareNet` / `unshareUts` / `unshareCgroup` | 全 `false` | 各命名空间隔离开关 |
| `privateTmp` | `false` | 私有 `/tmp` |
| `chdirToPwd` | `true` | 启动时切到当前目录 |
| `dieWithParent` | `true` | 父进程退出时一起退出 |

**目录布局**（源码注释原文）：

```
/lib32   ← multiPkgs 的 32 位库
/lib64   ← multiPkgs + targetPkgs 的 64 位库
/lib     → 符号链接到 /lib64
```

**永远自动包含的基础包**（不用你写）：

```
glibcLocales  glibc（或 glibc_multi）  gcc.cc.lib  bashInteractiveFHS
coreutils  less  shadow  su  gawk  diffutils  findutils  ...
```

**`/etc` 里从宿主绑进来的东西**（源码里的完整清单，30 项）：

```
static  nix  shells  bashrc  zshenv  zshrc  zinputrc  zprofile
passwd  group  shadow  hosts  resolv.conf  nsswitch.conf  profiles
login.defs  sudoers  sudoers.d  localtime  zoneinfo  machine-id  os-release
pam.d  fonts  alsa  asound.conf  ssl/certs  ca-certificates  pki  dconf
```

> [!NOTE]
> **这张 `/etc` 清单解释了为什么 FHS 环境里能读到你自己的 `/etc/passwd`、能用系统字体、能解析 DNS、能验证 TLS 证书** —— 它把宿主的这些路径 `--ro-bind` 进去了。
>
> **也解释了为什么「FHS 环境里改字体/证书」不会生效** —— 它读的是宿主的那份。

**一个有意思的实现细节**（源码注释原文）：FHS 环境里有个**静态编译的小 shim**（`container-init`）先跑 `ldconfig` 生成初始缓存，再 `exec` 真正的 `/init`。原因：

> *"we need to run bash to run the init script; LD_PRELOAD may be set to another dynamic library, requiring us to discover its dependencies; oops! ldconfig is part of the init script, and it hasn't run yet; everything explodes. In particular, this happens with fhsenvs in fhsenvs, e.g. when running a wrapped game from Steam."*

**用法：**

```nix
# configuration.nix —— 定义一个可复用的 FHS 环境
{ pkgs, ... }:
let
  myapp-fhs = pkgs.buildFHSEnv {
    name = "myapp-fhs";
    targetPkgs = pkgs: with pkgs; [
      # 程序本体（如果它有 Nix 包就优先用 Nix 包）
      # 或者放它需要的工具
      bashInteractive coreutils which
    ];
    multiPkgs = pkgs: with pkgs; [
      # 库（x86_64 上会自动带 32 位版本）
      zlib zstd stdenv.cc.cc openssl curl
      libx11 libxext libxrender libxfixes libxrandr libxcursor libxi
      libxkbcommon libGL libgbm mesa vulkan-loader
      gtk3 gdk-pixbuf cairo pango atk
      alsa-lib dbus expat freetype fontconfig
    ];
    runScript = "bash";
    profile = ''
      export FONTCONFIG_PATH=/etc/fonts
      export XDG_DATA_DIRS=/run/current-system/sw/share
    '';
  };
in
{
  environment.systemPackages = [ myapp-fhs ];
}
```

用的时候：

```bash
myapp-fhs                      # 进 FHS shell
myapp-fhs -c './myapp --foo'   # 直接跑一条命令
```

**`buildFHSUserEnv` 已改名** → 用 `buildFHSEnv`。**`fhsUserEnv` 这个老名字也是。**

> [!WARNING]
> **官方列出的 `buildFHSUserEnv` 三个弱点**（`[官方: nix-ld README]`）—— 这是选型时最容易忽略的：
>
> 1. *"setuid binaries cannot be executed inside a fhsuserenv"*
> 2. *"inside a `buildFHSUserEnv` you can not use other sandbox tools like bwrap or 'nix build'."*
> 3. *"`buildFHSUserEnv` requires a subshell which does not work well with direnv"*
>
> **第 2 条最坑**：在 FHS 环境里**不能再跑 `nix build`**、不能再套 bwrap。所以「在 FHS 里开发 Nix 项目」这条路是堵的 —— 用 Distrobox 或直接 `nix develop`。

#### 25.5.7 `steam-run`（借 Steam 的 FHS 环境）

**它是什么**（`[核实·源码: all-packages.nix:10646-10647]`）：

```nix
steam-run = steam.run;
steam-run-free = steam.run-free;
```

**它就是 `pkgs.steam` 的一个输出**，即「Steam 的 FHS 运行时环境」的独立入口。

```bash
steam-run ./myapp
steam-run bash -c './myapp --foo'
```

> [!NOTE]
> **它是「顺手用一下」的工具，不是长期方案。**
>
> - 依赖 Steam 的运行时闭包（体积大）
> - **`programs.steam.enable = true` 才会带上它**（或者单独 `nix shell nixpkgs#steam-run`）
> - 长期方案用 `buildFHSEnv`（你可以精确控制里面有什么）
>
> **但它有个独特价值**：Steam 的运行时**已经被 Valve 验证过能跑游戏**，所以遇到「游戏相关的外围工具跑不起来」时，`steam-run` 的兼容性往往比自己搭的 FHS env 好。

#### 25.5.8 `patchelf` 手工改（一次性修 / 调试）

```bash
# 看现在写的是什么
patchelf --print-interpreter ./myapp
patchelf --print-rpath ./myapp
patchelf --print-needed ./myapp

# 改动态链接器
patchelf --set-interpreter \
  "$(nix eval --raw nixpkgs#stdenv.cc.bintools.dynamicLinker)" \
  ./myapp

# 设 RPATH（库搜索路径）
patchelf --set-rpath "$(nix eval --raw --impure --expr \
  'with import <nixpkgs> {}; lib.makeLibraryPath [ zlib openssl stdenv.cc.cc ]')" \
  ./myapp

# 追加（不覆盖原有）
patchelf --add-rpath /some/extra/lib ./myapp
```

**`patchelf` 在 nixpkgs 里**（`[核实·源码: all-packages.nix:5594-5596]`）：

```nix
patchelf = callPackage ../development/tools/misc/patchelf { };
patchelfUnstable = lowPrio (callPackage ../development/tools/misc/patchelf/unstable.nix { });
```

> [!WARNING]
> **`patchelf` 改的是「文件本身」，不是配置。**
>
> - 程序**一更新，改动就没了**（要重跑）
> - **改完的文件不在 store 里** → 不受 GC 管理、不进配置版本控制、不能回滚
> - 如果原文件在 `/nix/store` 里（只读），`patchelf` **会失败**
>
> **所以它适合「调试 / 一次性验证」，不适合长期方案。** 长期方案是 §25.5.4 的 nix-ld 或 §25.5.6 的 FHS env。

**什么时候它是对的**：
- 你在**写一个 derivation**，需要修一个上游没修好的二进制 → 用 `autoPatchelfHook`（§25.5.9）
- 你想**验证**「改链接器能不能解决」→ `patchelf` 试一次，成功了再去做正式方案

#### 25.5.9 `autoPatchelfHook`（打包时用）

**位置**：`pkgs/build-support/setup-hooks/auto-patchelf.sh`（`[核实·源码]`），在 `all-packages.nix:287-295` 定义为 `auto-patchelf-hook`。

**它是给「写 derivation 的人」用的**，不是给「跑预编译二进制的人」用的：

```nix
{ lib, stdenv, fetchurl, autoPatchelfHook, zlib, openssl, stdenv.cc.cc }:

stdenv.mkDerivation rec {
  pname = "myapp";
  version = "1.0";
  src = fetchurl { url = "..."; hash = "..."; };

  nativeBuildInputs = [ autoPatchelfHook ];   # ← 挂钩子
  buildInputs = [ zlib openssl stdenv.cc.cc ]; # ← 它要能找到这些库

  # 有些库它自动找不到，手动补
  # autoPatchelfIgnoreMissingDeps = [ "libfoo.so.1" ];
}
```

**它做的事**：构建后自动扫 ELF，把 interpreter 和 RPATH 改成 store 路径。**nixpkgs 里所有闭源二进制包都靠它**（这也是 nix-ld README 开头说的：*"many proprietary packages in nixpkgs have already been patched with `autoPatchelfHook`"*）。

> [!TIP]
> **判断一个包有没有被 `autoPatchelfHook` 处理过**：
> ```bash
> nix-store -q --references $(which someapp) | head
> patchelf --print-interpreter $(which someapp)
> ```
> 如果 interpreter 指向 `/nix/store/...-glibc-.../lib/ld-linux-x86-64.so.2`，说明**已经被修好了**，不需要 nix-ld。

#### 25.5.10 ★ `nix-alien` —— 自动探测缺失库（强烈推荐）

**它做什么**（`[官方: nix-alien README]`）：

> *"You are running nix/NixOS and have ever encountered the following problem?*
> ```
> $ ./myapp
> bash: ./myapp: No such file or directory
> ```
> *Fear not, now there is `nix-alien` which will download necessary dependencies for you."*

**三个命令：**

| 命令 | 作用 |
|---|---|
| `nix-alien ./myapp` | 在 **FHS 环境**里跑，自动带上所有需要的共享库 |
| `nix-alien-ld ./myapp` | 生成一个 wrapper，设好 `NIX_LD` / `NIX_LD_LIBRARY_PATH`（**需要 `programs.nix-ld.enable = true`**） |
| `nix-alien-find-libs ./myapp` | **只列出**需要的库（`--json` 输出 JSON），适合脚本 |

**免安装直接用：**

```bash
nix run github:thiagokokada/nix-alien -- ~/myapp
nix run github:thiagokokada/nix-alien#nix-alien-ld -- ~/myapp
nix run github:thiagokokada/nix-alien#nix-alien-find-libs -- ~/myapp
```

**它怎么做到的**（官方技术说明原文）：

> *"This is achieved by enumerating the shared library dependencies from the ELF header using `ldd` (actually, `pylddwrap`) and then searching for the equivalent library in `nixpkgs`. This is done by querying `nix-locate` locally. To solve possible conflicts, human intervation is needed, but thanks to `fzf` and `pyfzf` this is made easy by showing an interactive list."*

**缓存位置**：`$XDG_CACHE_HOME/nix-alien/<path-uuid>/{fhs-env,nix-ld}/default.nix`（按二进制绝对路径缓存，`--recreate` 强制重建）

**重要局限**（官方原文）：

> *"Binaries loading shared libraries dynamically (e.g.: with `dlopen`) **will probably not work** with this script. However, this can be workarounded using either `--additional-libs/-l` or `--additional-packages/-p` flag."*

```bash
# dlopen 的库要手动指定
nix-alien -l libGL.so.1 -l libz.so.1 ~/myapp      # 按 SONAME 搜
nix-alien -p libGL -p zlib ~/myapp                 # 直接加包（无校验，包名写错会 undefined variable）
```

> [!DANGER]
> **`nix-alien` 不在 nixpkgs 里**（`[核实·源码]`：`pkgs/by-name/ni/nix-alien` = 404，`all-packages.nix` 里也搜不到）。必须通过 **flake input** 或 `builtins.fetchTarball` 引入。
>
> **官方明确警告**：*"Overriding `nix-alien` inputs may cause mismatches between the `nix-index-database` and `nixpkgs`, causing possibly incorrect results, so it is unsupported."*
>
> **意思是**：不要用 `follows` 把 nix-alien 的 nixpkgs 换成你的 —— 它靠 `nix-index-database` 反查库，索引和 nixpkgs 版本必须匹配。
>
> 上游项目：<https://github.com/thiagokokada/nix-alien>（880 stars，最后推送 2026-09-15）

**推荐用法：用 `nix run` 临时跑，不要装进系统。**

#### 25.5.11 Distrobox 容器（整个 FHS 发行版）

**这是解决「复杂软件 + 完整 FHS」最省心的方案**（§23.7 已详述配置）：

```bash
distrobox create --name arch --image quay.io/toolbx/arch-toolbox:latest
distrobox enter arch
# 容器内是完整的 Arch，随便 pacman
sudo pacman -S <anything>
exit

# 把 GUI 应用导出到宿主菜单
distrobox enter arch
distrobox-export --app <应用名>
distrobox-export --bin /usr/bin/xxx --export-path ~/.local/bin
```

**`pkgs.distrobox` 在 nixpkgs 里**（**1.8.2.5**，`[核实·源码]`）。

**什么时候用 Distrobox 而不是 FHS env**：

| 用 Distrobox | 用 buildFHSEnv |
|---|---|
| 你要装**很多东西**、要包管理器 | 你只要**一个程序**能跑 |
| 你要**开发环境**（能编译、能装依赖） | 一次性运行 |
| 你需要**发行版提供的完整生态**（如 AUR） | 你不想引入容器 |
| 你需要**在环境里还能用 nix**（FHS env 里不能，见 §25.5.6 弱点 2） | — |

#### 25.5.12 Docker / Podman 容器

```nix
{
  virtualisation.docker.enable = true;      # 或 virtualisation.podman
  users.users.<你>.extraGroups = [ "docker" ];   # podman 则是 "podman"
}
```

```bash
docker run --rm -it -v "$PWD:/work" -w /work ubuntu:24.04 bash
```

**容器内是完整 FHS + 完整发行版**，所以**所有依赖问题一次解决**。代价是：
- 体积大
- **GUI 要额外配**（`--device /dev/dri`、`DISPLAY` / `WAYLAND_DISPLAY` 挂载、`--ipc=host`）
- 文件权限（容器内 root 创建的文件在宿主上是 root 所有）

> [!TIP]
> **NixOS 上的容器有个额外好处**：`virtualisation.docker` / `podman` 是**声明式配置的**（不像传统发行版要装包），而且 `docker run` 的镜像拉取走的是普通网络，**和 Nix store 完全解耦**。
>
> **注意**：容器镜像里的东西**不受 Nix 管理**，不进配置、不能回滚。这是「用容器换省心」的代价。

#### 25.5.13 Flatpak

**已有专章**（§7、§23.6），这里只放决策位置：

| 用 Flatpak | 不用 Flatpak |
|---|---|
| 软件**只发 Flatpak** | 软件在 nixpkgs 里有 |
| 你要**沙箱隔离** | 你要主题/字体/输入法一致（§7 三个坑） |
| 你接受**应用不进配置** | 你要换机器自动重现 |

#### 25.5.14 `binfmt` + qemu（跨架构二进制）

**nix-ld 的官方 README 就给了这个用法**（`[官方]`）：

```nix
{
  # x86_64-linux, i686-linux, aarch64-linux
  boot.binfmt.emulatedSystems = [ "aarch64-linux" ];
}
```

**它做什么**：注册 binfmt 规则，让内核遇到 aarch64 ELF 时自动用 qemu 执行。**之后你就能直接跑 aarch64 的二进制**，也能 `nix build --system aarch64-linux`。

**代价**：qemu 模拟**慢 5–20 倍**（不是虚拟化，是逐指令翻译）。适合**编译验证**，不适合**长期运行**。

> [!NOTE]
> `boot.binfmt.registrations` 的选项在 26.05 已核实存在（`[核实·源码: nixos/modules/system/boot/binfmt.nix]`），含 `recognitionType` / `magicOrExtension` / `offset` / `mask` / `interpreter` / `preserveArgvZero` 等。`programs.appimage` 的 `binfmt` 就是用这套机制实现的（§25.5.5）。

### 25.6 常见依赖清单：按类别（**全部用 26.05 新属性名**）

> [!IMPORTANT]
> **下面所有 X11 库都用 §25.2 的 26.05 新名字**（`libx11` 而不是 `xorg.libX11`）。从网上抄旧清单会拿到一堆弃用警告。

**① C / C++ 运行时（最常缺）**

```nix
stdenv.cc.cc        # libstdc++.so.6  ★ C++ 程序必缺
glibc               # libc.so.6 / libm.so.6（一般由 nix-ld 自带，不用写）
gcc.cc.lib          # 同上
```

**② 压缩 / 归档**

```nix
zlib zstd xz bzip2 lz4 libarchive
```

**③ 加密 / 网络**

```nix
openssl curl libssh libsodium libxml2 gnutls libgcrypt libgpg-error
```

**④ X11（★ 用新名字）**

```nix
libx11 libxext libxrender libxi libxcomposite libxdamage
libxrandr libxcursor libxfixes libxtst libxscrnsaver libxxf86vm
libxcb libxau libxdmcp libxshmfence
libxft libxinerama libxmu libxpm libxt libxv libxvmc libxpresent libxres
```

**⑤ Wayland**

```nix
libxkbcommon wayland wayland-protocols
```

**⑥ 图形 / GPU**

```nix
libGL libgbm libdrm mesa vulkan-loader
# 32 位（游戏常用）：pkgsi686Linux.libGL 等
```

**⑦ GUI 工具包（Electron / GTK 程序必备）**

```nix
gtk3 gdk-pixbuf cairo pango atk harfbuzz
nss nspr                     # ★ Electron 必备
```

**⑧ 字体**

```nix
freetype fontconfig
noto-fonts noto-fonts-cjk-sans noto-fonts-color-emoji   # 中文/emoji
```

**⑨ 音频**

```nix
alsa-lib libpulseaudio pipewire
```

**⑩ 桌面集成 / 系统**

```nix
dbus expat cups systemd util-linux acl attr
```

**⑪ 一份「万能起步集」（可直接粘贴到 `programs.nix-ld.libraries`）**

```nix
programs.nix-ld.libraries = with pkgs; [
  # C/C++ 运行时
  stdenv.cc.cc
  # 压缩
  zlib zstd xz bzip2 lz4
  # 加密 / 网络
  openssl curl libssh libsodium libxml2
  # 系统
  systemd util-linux acl attr
  # X11（26.05 新名字）
  libx11 libxext libxrender libxi libxcomposite libxdamage
  libxrandr libxcursor libxfixes libxtst libxscrnsaver libxxf86vm
  libxcb libxau libxdmcp libxshmfence
  # Wayland
  libxkbcommon wayland
  # 图形
  libGL libgbm libdrm mesa vulkan-loader
  # GUI 工具包
  gtk3 gdk-pixbuf cairo pango atk harfbuzz nss nspr
  # 字体
  freetype fontconfig
  # 音频
  alsa-lib
  # 桌面集成
  dbus expat cups
]
```

> [!NOTE]
> **这份清单是「覆盖大多数 GUI 场景」的经验集合，不是官方列表。** 模块自带的 14 个库（§25.5.4）是「CLI 向」的基础集；上面这份是**在它基础上追加 GUI 向的部分**。
>
> **用法**：先只开 `programs.nix-ld.enable = true`，跑你的程序；**报什么缺什么**，从上面按类别加。**不要一次性全加上**（闭包会变大，而且你也不知道哪些是真需要的）。

### 25.7 按「程序类型」查表

| 程序类型 | 典型症状 | **首选** | 备选 |
|---|---|---|---|
| **静态链接 ELF**（Go / Rust 默认） | 一般直接能跑 | 直接跑 | — |
| **动态链接 ELF**（需 glibc） | `No such file or directory` | **`programs.nix-ld`** | `patchelf` |
| **C++ 程序** | `libstdc++.so.6: not found` | **nix-ld**（已含 `stdenv.cc.cc`） | — |
| **Electron 应用**（VSCode、Obsidian） | 一堆 X11 + `nss`/`nspr` 缺失 | **nix-ld + §25.6 ⑦ 清单** | 用 Flatpak 版 / `buildFHSEnv` |
| **Java 程序**（JAR） | 需要 JRE | `nix shell nixpkgs#jre` 或 nixpkgs 的 jre | 自带 JRE 的发行包 |
| **Python manylinux wheel** | `.so` 加载失败 | **官方 wrapper + `LD_LIBRARY_PATH`**（§25.5.4 DANGER） | `python3.withPackages` / `uv` 用 nixpkgs 的 python |
| **npm 原生模块** | `node-gyp` 报错 / `.node` 加载失败 | `programs.nix-ld` + 用户级 npm | nixpkgs 的 node + `buildNpmPackage` |
| **AppImage** | 无法执行 | **`programs.appimage.binfmt`** | `appimage-run ./foo.AppImage` |
| **`.run` 安装器**（NVIDIA、CUDA） | 装不进 `/usr` | **拆包 / 用 nixpkgs 版** | `--target=./local` 装到用户目录 |
| **`.deb` / `.rpm`** | 无法安装 | **`pkgs.dpkg` / `rpm` 解包到本地** | Distrobox |
| **`.tar.gz` 二进制** | 同动态链接 ELF | nix-ld | — |
| **游戏（Steam）** | — | `programs.steam`（自带 FHS） | `steam-run` |
| **游戏（非 Steam）** | — | `pkgs.lutris` / `pkgs.heroic` / `pkgs.bottles` | `steam-run` |
| **Windows 程序** | — | `pkgs.wine` / Proton | Bottles |
| **内核模块 / DKMS 驱动** | `modprobe` 失败 | ❌ **不能用上面任何方案** → 见 §25.8 | `boot.extraModulePackages` |
| **需要 setuid 的程序** | 权限失败 | ❌ nix-ld / FHS 都不行 → 见 §25.8 | `security.wrappers` |
| **aarch64 二进制** | `Exec format error` | **`boot.binfmt.emulatedSystems`** | 容器 |
| **Docker 镜像** | — | `virtualisation.docker` / `podman` | Distrobox |
| **闭源 GPU 驱动** | — | nixpkgs 的 `hardware.nvidia` / `hardware.amdgpu` | ❌ 不能装 `.run` |

### 25.8 三类「解决不了」的情况（诚实交代）

#### 25.8.1 内核模块 / DKMS 型驱动

**症状**：`modprobe: FATAL: Module xxx not found`、`.run` 安装器编译驱动失败。

**为什么不能**：内核模块必须**用你当前内核的确切源码和配置编译**。NixOS 的内核在 store 里，有确定的哈希；DKMS 那套「运行时编译」的假设（源码在 `/lib/modules/$(uname -r)/build`）在 NixOS 上**不成立**。

**正确做法**：

```nix
{
  # 树外模块：走 nixpkgs 的机制
  boot.extraModulePackages = with config.boot.kernelPackages; [
    # 例如 r8125（Realtek 2.5G 网卡）
    r8125
  ];
  boot.kernelModules = [ "r8125" ];
}
```

**并且**：跨源取内核会破坏模块配对（§11.2、§20 已详述）。**内核和它的模块必须来自同一份 nixpkgs。**

#### 25.8.2 setuid 二进制

**症状**：程序需要 root 权限（如 `ping`、`mount`、某些游戏反作弊）。

**为什么不能**：nix-ld README 明确列出 —— *"setuid binaries cannot be executed inside a fhsuserenv"*。而且 **nix-ld 也不处理 setuid**（它只换链接器）。

**正确做法**：用 NixOS 的 `security.wrappers`：

```nix
{
  security.wrappers.myapp = {
    source = "${pkgs.myapp}/bin/myapp";
    owner = "root";
    group = "root";
    setuid = true;        # 或 capabilities = "cap_net_raw+ep";
  };
}
```

> [!IMPORTANT]
> **`security.wrappers` 只能包装「已经在 `/nix/store` 里的东西」**（因为 wrapper 要在构建时生成）。**你没法给一个从网上下载的任意二进制加 setuid** —— 这需要它在 store 里，也就是需要它是一个 Nix 包。
>
> **所以「一个需要 setuid 的闭源二进制」在 NixOS 上基本无解**，除非你自己写个 derivation 把它放进 store。

#### 25.8.3 glibc 版本不匹配

**症状**：`./myapp: /lib64/ld-linux-x86-64.so.2: version 'GLIBC_2.38' not found`

**为什么难**：程序需要**一整套配套的 glibc 环境**（不只是链接器）。用 nix-ld 换一个更新的链接器**可能反而更糟**（新旧符号混用）。

**正确做法（按代价排序）**：

| 方案 | 说明 |
|---|---|
| ① 用 `buildFHSEnv` 并提供**一个匹配的 glibc** | `targetPkgs = pkgs: [ pkgs.glibc ]`，但 glibc 版本要和程序要求对齐 |
| ② **Distrobox / 容器**（推荐） | 直接用有合适 glibc 的发行版（如较新的 Ubuntu/Debian） |
| ③ 找该软件的**旧版本** | 如果它之前能在老 glibc 上跑 |
| ④ 找**静态链接**的构建 | 上游若提供 `musl` 静态版最好 |

> [!DANGER]
> **不要用 `LD_LIBRARY_PATH` 指一个不同版本的 glibc。** 这会污染**所有**程序（nix-ld 官方原话：*"LD_LIBRARY_PATH affects all programs, which can inject the wrong libraries in correct build nix application that have an RPATH set in their executable."*），而且 glibc 混版会导致**极难诊断的崩溃**。
>
> **glibc 是「全有或全无」的**：要么整套匹配，要么别动。用容器。

#### 25.8.4 附：需要写 `/usr` 的安装器

**症状**：`.run` / `.deb` / `.rpm` 安装器报 `cannot write to /usr/lib`。

**做法**：

| 方法 | 命令 |
|---|---|
| **解包不安装** | `dpkg -x pkg.deb ./out` / `rpm2cpio pkg.rpm \| cpio -idmv` |
| **装到用户目录** | 很多 `.run` 支持 `--target=$HOME/opt/xxx` |
| **Distrobox** | 容器里 `/usr` 可写 |
| **最好的方法** | 看 nixpkgs 里有没有人已经打包好了 |

### 25.9 六个反模式

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | **全局 `export LD_LIBRARY_PATH=...`** | 污染所有程序，注入错误的库到 RPATH 正确的 Nix 程序里 → 诡异崩溃 | 用 `NIX_LD_LIBRARY_PATH`（nix-ld 会在调用真实 ld 前才改写它） |
| 2 | **一上来就 `buildFHSEnv`** | 启动慢、重、而且有官方列出的三个弱点（§25.5.6） | 从上往下试（§25.4 表），先 nix-ld |
| 3 | **在 26.05 继续写 `pkgs.xorg.libX11`** | 刷弃用警告，未来会变硬错误；`libXfont` 还会拿错版本 | 用 `pkgs.libx11`（§25.2 全表） |
| 4 | **指望 nix-ld 让 pip/npm 装的库能被 nixpkgs 的 python/node 找到** | 不会生效（官方 FAQ 明确说不行） | 用官方 wrapper 设 `LD_LIBRARY_PATH`（§25.5.4 DANGER） |
| 5 | **开 `programs.appimage.enable` 但忘了 `binfmt = true`** | AppImage 不能双击，必须手动 `appimage-run` | 两个都开 |
| 6 | **`patchelf` 改 store 里的文件 / 改完就忘了** | 只读失败；或程序更新后改动丢失 | 调试用 `patchelf`，长期用 nix-ld / FHS env |

### 25.10 决策流程（照着走）

```
你的二进位包跑不起来
│
├─ 0) 先搜 nixpkgs 有没有
│     nix search nixpkgs <名字>      /  https://search.nixos.org
│     ├─ 有 → 【结束】用 nixpkgs 的。不要往下走
│     └─ 没有 → 继续
│
├─ 1) 诊断（§25.3）
│     file ./myapp            → 是 ELF 吗？静态还是动态？
│     readelf -d ./myapp      → 缺哪些 SONAME？
│     报错里有 GLIBC_2.xx?    → 是 → 跳 §25.8.3（容器）
│
├─ 2) 是 AppImage 吗？
│     └─ 是 → programs.appimage = { enable = true; binfmt = true; }   【结束】
│
├─ 3) 缺的库不多、程序是普通动态链接 ELF？
│     └─ programs.nix-ld.enable = true; 按 §25.6 追加 libraries   【多数情况到此结束】
│
├─ 4) 不确定缺什么？
│     └─ nix run github:thiagokokada/nix-alien -- ./myapp   （自动探测）【推荐】
│
├─ 5) 程序需要完整 FHS 目录树（硬编码 /usr/lib、/opt）？
│     └─ buildFHSEnv（§25.5.6）
│
├─ 6) 程序是游戏相关？
│     └─ steam-run ./binary  /  programs.steam
│
├─ 7) 上面都不行 / 要装很多东西 / 要开发环境？
│     └─ Distrobox 容器（§25.5.11）  ← 最省心的兜底
│
├─ 8) 是内核模块 / setuid / 驱动？
│     └─ 【不能用上面任何方案】→ §25.8
│
└─ 9) 是跨架构二进制？
      └─ boot.binfmt.emulatedSystems = [ "aarch64-linux" ]
```

### 25.11 一页速查

| 问题 | 一行答案 |
|---|---|
| `No such file or directory` 但其实文件存在 | **`programs.nix-ld.enable = true;`** —— 缺的是 `/lib64/ld-linux-x86-64.so.2` |
| `libfoo.so.1: cannot open shared object file` | nix-ld + `programs.nix-ld.libraries = [ ... ];` |
| 不知道缺哪个库 | `readelf -d ./myapp \| grep NEEDED`，或 `nix-alien-find-libs ./myapp` |
| 想知道某个 `.so` 属于哪个包 | `nix-locate --top-level libfoo.so.1` |
| 自动搞定 | `nix run github:thiagokokada/nix-alien -- ./myapp` |
| AppImage 双击没反应 | `programs.appimage = { enable = true; binfmt = true; };` |
| 程序硬编码 `/usr/lib` | `pkgs.buildFHSEnv { ... }`（= `buildFHSEnvBubblewrap`） |
| 想借 Steam 的运行时 | `steam-run ./binary` |
| `GLIBC_2.xx not found` | 用容器（Distrobox）—— 别折腾 glibc |
| pip 装的包加载不了 | nixpkgs 的 python **不走 nix-ld** → 官方 wrapper 设 `LD_LIBRARY_PATH` |
| 26.05 里 `pkgs.xorg.libX11` 报弃用 | 改用 **`pkgs.libx11`**（§25.2 全表） |
| 内核模块 | ❌ 不能用 nix-ld / FHS → `boot.extraModulePackages` |
| setuid | ❌ 不能用 nix-ld / FHS → `security.wrappers`（且必须已在 store 里） |
| 跨架构 | `boot.binfmt.emulatedSystems = [ "aarch64-linux" ];` |
| 什么都不想管 | **Distrobox 容器**（整个发行版，一次解决所有依赖） |

---

## 二十六、配置语法、抽象、模块化与 Profiles（官方 Part II 基础层）

本章补的是官方手册 **Part II · Configuration** 的前 11 章：`sec-configuration-syntax`、`sec-configuration-file`、`sec-module-abstractions`、`sec-modularity`、`sec-package-management`（部分）、`ch-profiles`。

**本指南前二十五章教的是「写什么」，这一章教的是「为什么能这么写」。**

> [!IMPORTANT]
> **这一章解决一个具体痛点**：你在网上抄到一段 `configuration.nix`，里面出现 `let ... in`、`//`、`mkForce`、`config.services.xxx`、`imports = [ ... ]` —— **不知道它们是什么，就不敢改**。本章把官方文档里这几个概念的原文全部搬过来，逐条对照。

### 26.1 官方配置语法：值的六种类型

> **官方原文**：*"The NixOS configuration file `/etc/nixos/configuration.nix` is actually a Nix expression, which is the Nix package manager's purely functional language for describing how to build packages and configurations. This means you have all the expressive power of that language at your disposal, including the ability to abstract over common patterns, which is very useful when managing complex systems."* —— `[官方]` `sec-configuration-syntax`

**官方列出的「最重要的类型」**（原文顺序）：

| 类型 | 官方示例 | 你的配置里长什么样 |
|---|---|---|
| **String** | `networking.hostName = "dexter";` | 双引号；`\"` 转义 |
| **多行 String** | `''...''` | **两个单引号**，不是双引号 |
| **Boolean** | `networking.firewall.enable = true;` | `true` / `false` |
| **Integer** | `boot.kernel.sysctl."net.ipv4.tcp_keepalive_time" = 60;` | 注意**键名要加引号** |
| **Set** | `fileSystems."/boot" = { device = ...; fsType = ...; options = [...]; };` | `{ ... }` |
| **List** | `environment.systemPackages = [ pkgs.vim ];` | `[ ... ]`，**空格分隔，不是逗号** |

**官方对多行字符串的说明（原文）**：

> *"The main difference is that it strips from each line a number of spaces equal to the minimal indentation of the string as a whole (disregarding the indentation of empty lines), and that characters like `"` and `\` are not special (making it more convenient for including things like shell code)."* —— `[官方]` `sec-configuration-file`

> [!TIP]
> **这条解释了为什么 NixOS 配置里写脚本都用 `''...''`**：里面可以放心写 `$`、`"`、`\` 而不用转义。你在本指南 §14.x（sysctl 与 udev 规则）和 §29.4（自定义服务）看到的都是这个写法。
>
> **踩坑点**：`''` 会剥掉「整体最小缩进」。如果你把 shell 脚本的某一行**故意多缩进**，那段缩进会被保留 —— 这通常是想要的；但如果你把整个块贴到别处改变了整体缩进，**结果会变**。

**官方对内核参数键名的说明（原文）**：

> *"Note that here the attribute name `net.ipv4.tcp_keepalive_time` is enclosed in quotes to prevent it from being interpreted as a set named `net` containing a set named `ipv4`, and so on. This is because it's not a NixOS option but the literal name of a Linux kernel setting."* —— `[官方]` `sec-configuration-file`

> [!WARNING]
> **这是最容易错的一处**：
> ```nix
> boot.kernel.sysctl."net.ipv4.tcp_keepalive_time" = 120;  # ✅ 正确
> boot.kernel.sysctl.net.ipv4.tcp_keepalive_time = 120;    # ❌ 会被解析成嵌套 set
> ```
> **判据**：**点号是「NixOS 选项路径」还是「字面名字」？** 是字面名字（内核参数、`/etc` 文件名、桌面 ID）就必须加引号。
> 同类的还有 `systemd.services."my-name".serviceConfig`（名字含 `-`）、`environment.etc."foo.conf".text`。

### 26.2 `{ config, pkgs, ... }:` 到底是什么意思

> **官方原文**：*"The first line (`{ config, pkgs, ... }:`) denotes that this is actually a function that takes at least the two arguments `config` and `pkgs`. The function returns a set of option definitions (`{ ... }`)."* —— `[官方]` `sec-configuration-file`

**拆开看**：

| 部分 | 含义 | 官方出处 |
|---|---|---|
| `{ ... }:` | 这是**一个函数**（lambda），不是数据 | `sec-configuration-file` |
| `config` | **合并后**的完整系统配置（所有模块的结果之和） | `sec-modularity` |
| `pkgs` | nixpkgs 包集 | `sec-configuration-file` |
| `...` | 「还有别的参数，我不关心」 | `sec-writing-modules` |
| 函数体 `{ ... }` | **选项定义**（option definitions） | `sec-configuration-file` |

**官方对 `config` 的解释（原文，`sec-modularity`）**：

> *"When using multiple modules, you may need to access configuration values defined in other modules. This is what the `config` function argument is for: it contains the complete, merged system configuration. That is, `config` is the result of combining the configurations returned by every module. (If you're wondering how it's possible that the (indirect) result of a function is passed as an input to that same function: that's because Nix is a "lazy" language — it only computes values when they are needed. This works as long as no individual configuration value depends on itself.)"*

> [!NOTE]
> **「惰性」这一句是理解 NixOS 模块系统的钥匙。** 它意味着：
> - 你**可以**在模块 A 里读模块 B 定义的值（哪怕 B 还没求值）
> - **但不能**让一个值依赖它自己 → 这是「infinite recursion」报错的来源
>
> **实操意义**：写 `if config.services.xserver.enable then ... else ...` 是**完全正常**的官方写法（见 §26.6），不要以为它有什么魔法。

**官方给的完整模块结构**（`Example 14. Structure of NixOS Modules`）：

```nix
{ config, pkgs, ... }:

{
  imports = [
    # paths of other modules
  ];

  options = {
    # option declarations
  };

  config = {
    # option definitions
  };
}
```

> [!IMPORTANT]
> **注意 `options` 和 `config` 是两个不同的东西**，这是官方反复强调的：
> - **`options` = 声明**（declaration）：定义「有这么个选项、它是 bool 类型、文档这么写」—— **写模块的人才用**
> - **`config` = 定义**（definition）：给已声明的选项赋值 —— **普通用户只写这个**
>
> **你的 `/etc/nixos/configuration.nix` 里那个 `{ ... }` 是 `config` 的简写形式。** 官方原文：*"This is actually an abbreviated form of module that only defines options, but does not declare any."*（`sec-writing-modules`）

### 26.3 点号语法 ↔ 嵌套 set（完全等价）

官方给了一对**逐字等价**的写法（`sec-configuration-file`）：

```nix
# 写法 A：点号
{ config, pkgs, ... }:
{
  services.httpd.enable = true;
  services.httpd.adminAddr = "alice@example.org";
  services.httpd.virtualHosts.localhost.documentRoot = "/webroot";
}
```

```nix
# 写法 B：嵌套 set（完全等价）
{ config, pkgs, ... }:
{
  services = {
    httpd = {
      enable = true;
      adminAddr = "alice@example.org";
      virtualHosts = {
        localhost = {
          documentRoot = "/webroot";
        };
      };
    };
  };
}
```

> **官方原文**：*"Sets can be nested, and in fact dots in option names are shorthand for defining a set containing another set."* …… *"which may be more convenient if you have lots of option definitions that share the same prefix."*

**官方还给了两个报错原文**（说明 NixOS 会检查定义的正确性）：

```
The option `services.httpd.enable' defined in `/etc/nixos/configuration.nix' does not exist.
```

```
The option value `services.httpd.enable' in `/etc/nixos/configuration.nix' is not a boolean.
```

> [!TIP]
> **这两条报错你应该记住**：
> - **第 1 条「does not exist」** → 选项名写错了。**去 <https://search.nixos.org/options> 复制准确名字**，不要凭记忆写。
> - **第 2 条「is not a boolean」** → 类型错了。最常见是把字符串写成布尔（`"true"` 而不是 `true`），或反过来。
>
> **这两类错误都在 eval 阶段报出，不会真的改坏系统** —— 这正是 NixOS 比命令式系统安全的地方。

### 26.4 抽象：`let`、`//` 与函数（官方三个例子）

官方用同一段 Apache 配置演示了**三层抽象**（`sec-module-abstractions`）。

**起点（重复三次，很啰嗦）**：

```nix
{
  services.httpd.virtualHosts = {
    "blog.example.org" = {
      documentRoot = "/webroot/blog.example.org";
      adminAddr = "alice@example.org";
      forceSSL = true;
      enableACME = true;
    };
    "wiki.example.org" = {
      documentRoot = "/webroot/wiki.example.org";
      adminAddr = "alice@example.org";
      forceSSL = true;
      enableACME = true;
    };
  };
}
```

**第一层：`let` + `//`（属性集合并）**

```nix
let
  commonConfig = {
    adminAddr = "alice@example.org";
    forceSSL = true;
    enableACME = true;
  };
in
{
  services.httpd.virtualHosts = {
    "blog.example.org" = (commonConfig // { documentRoot = "/webroot/blog.example.org"; });
    "wiki.example.org" = (commonConfig // { documentRoot = "/webroot/wiki.example.org"; });
  };
}
```

> **官方原文**：*"The `let commonConfig = ...` defines a variable named `commonConfig`. The `//` operator merges two attribute sets, so the configuration of the second virtual host is the set `commonConfig` extended with the document root option."*

**第二层：函数**

```nix
{
  services.httpd.virtualHosts =
    let
      makeVirtualHost = webroot: {
        documentRoot = webroot;
        adminAddr = "alice@example.org";
        forceSSL = true;
        enableACME = true;
      };
    in
    {
      "example.org" = (makeVirtualHost "/webroot/example.org");
      "example.com" = (makeVirtualHost "/webroot/example.com");
      "example.gov" = (makeVirtualHost "/webroot/example.gov");
      "example.nl" = (makeVirtualHost "/webroot/example.nl");
    };
}
```

> **官方原文**：*"Here, `makeVirtualHost` is a function that takes a single argument `webroot` and returns the configuration for a virtual host."*

**官方的一条语法限制（很容易踩）**：

> *"You can write a `let` wherever an expression is allowed. Thus, you also could have written: `{ services.httpd.virtualHosts = let commonConfig = {...}; in {...}; }` **but not `{ let commonConfig = ...; in ...; }` since attributes (as opposed to attribute values) are not expressions.**"

> [!WARNING]
> **`let` 只能出现在「值」的位置，不能出现在「属性名」的位置。**
> ```nix
> { let x = 1; in { a = x; }; }   # ❌ 语法错误
> { a = let x = 1; in x; }        # ✅
> let x = 1; in { a = x; }        # ✅（在文件最外层）
> ```

> [!TIP]
> **这一节对「Vibe Coding」用户特别有用**：当 Agent 给你生成一段配置，里面有 `let ... in` 和 `//`，你现在能读懂它在做什么了 —— **它只是在做「复用」，没有副作用**。
>
> **反过来**：如果你想让 Agent 帮你改配置，可以明确告诉它「**用 `let` 抽公共部分，不要复制粘贴**」—— 这样生成的配置更好维护。

### 26.5 模块化：`imports` 与合并规则

**官方对模块化的定义（原文）**：

> *"The NixOS configuration mechanism is modular. If your `configuration.nix` becomes too big, you can split it into multiple files. Likewise, if you have multiple NixOS configurations (e.g. for different computers) with some commonality, you can move the common configuration into a shared file. Modules have exactly the same syntax as `configuration.nix`. **In fact, `configuration.nix` is itself a module.**"* —— `[官方]` `sec-modularity`

```nix
{ config, pkgs, ... }:
{
  imports = [
    ./vpn.nix
    ./kde.nix
  ];
  services.httpd.enable = true;
  environment.systemPackages = [ pkgs.emacs ];
  # ...
}
```

**官方对「多模块定义同一选项」的处理（原文）**：

> *"Note that both `configuration.nix` and `kde.nix` define the option `environment.systemPackages`. When multiple modules define an option, NixOS will try to merge the definitions. In the case of `environment.systemPackages` the lists of packages will be **concatenated**. **The value in `configuration.nix` is merged last, so for list-type options, it will appear at the end of the merged list.** If you want it to appear first, you can use `mkBefore`"*

```nix
{ boot.kernelModules = mkBefore [ "kvm-intel" ]; }
```

> **官方原文**：*"This causes the `kvm-intel` kernel module to be loaded before any other kernel modules."*

**不能合并的情况 —— 官方报错原文**：

```
The unique option `services.httpd.adminAddr' is defined multiple times, in `/etc/nixos/httpd.nix' and `/etc/nixos/configuration.nix'.
```

**官方的解法**：

```nix
{ services.httpd.adminAddr = pkgs.lib.mkForce "bob@example.org"; }
```

> [!IMPORTANT]
> **`mkForce` 的语义是「覆盖别人的定义」，不是「设置值」。**
>
> **优先级从低到高**（本指南 §19.4 已给出完整表，这里只列最常用的四档）：
>
> | 函数 | 语义 | 什么时候用 |
> |---|---|---|
> | `mkDefault v` | **默认值**，被别人覆盖 | 写模块时给合理默认 |
> | （直接赋值） | 普通定义 | 99% 的情况 |
> | `mkForce v` | **强制覆盖**（等价于 `mkOverride 50`） | 官方模块的默认值不合你意，且没有对应选项 |
> | `mkOverride n v` | 自定义优先级（**数字越小越优先**） | 精细控制 |
>
> **`mkForce` 是「最后手段」**：官方原文的用法是「when that happens, it's possible to force one definition take precedence」—— **它是为「两个模块真的冲突」准备的，不是日常工具**。
>
> **本指南 §18.x 用到的 `lib.mkDefault`** 是它的反面：**「我提供一个默认，但允许别人改」**。

**官方的「生成模块」写法**（不用文件也能 import）：

```nix
{ config, pkgs, ... }:

let
  netConfig = hostName: {
    networking.hostName = hostName;
    networking.useDHCP = false;
  };

in
{
  imports = [ (netConfig "nixos.localdomain") ];
}
```

> **官方原文**：*"While abstracting your configuration, you may find it useful to generate modules using code, instead of writing files. The example below would have the same effect as importing a file which sets those options."*

### 26.6 用 `config` 做条件配置（官方例子）

**官方原文**：

> *"For example, here is a module that adds some packages to `environment.systemPackages` only if `services.xserver.enable` is set to true somewhere else"*

```nix
{ config, pkgs, ... }:

{
  environment.systemPackages =
    if config.services.xserver.enable then
      [
        pkgs.firefox
        pkgs.thunderbird
      ]
    else
      [ ];
}
```

> [!TIP]
> **这是「条件化配置」的官方范式**，你会在很多真实配置里看到。**典型用途**：
> - 同一份配置用在台式机和笔记本上（用 `config.networking.hostName` 分支）
> - 只在开了某个服务时才装配套工具
>
> **注意**：`config.` 前缀不能省。写 `services.xserver.enable` 会被当成「定义一个新选项」而不是「读值」。
>
> **本指南 §24.5 的 HM `pkgsUnstable` 写法**、**§21.x 的 Hermes 条件配置**都用了这个模式。

### 26.7 查「某个选项最终是什么值」

**官方给了两个工具**（`sec-modularity`）：

```bash
$ nixos-option services.xserver.enable
true

$ nixos-option boot.kernelModules
[ "tun" "ipv6" "loop" ... ]
```

```bash
$ nix repl -f '<nixpkgs/nixos>'

nix-repl> config.networking.hostName
"mandark"

nix-repl> map (x: x.hostName) config.services.httpd.virtualHosts
[ "example.org" "example.gov" ]
```

> [!IMPORTANT]
> **`nixos-option` 是排查「为什么这个选项是这个值」的官方工具。**
>
> **典型场景**：你设了 `hardware.graphics.enable = true` 但 `glxinfo` 还是软渲染 —— 用 `nixos-option hardware.graphics.enable` 确认它**真的是 true**（而不是被某个模块 `mkForce false` 了）。
>
> **`nix repl -f '<nixpkgs/nixos>'` 更强**：它能让你**在求值后的配置上执行任意 Nix 表达式**。这是「系统管理员级的调试」。
>
> **对 Agent 用户的意义**：当 Agent 说「你的配置里 X 是 Y」，你可以用这两条命令**自己验证**，不用信它。

### 26.8 Profiles：官方预置的 11 套配置

**官方定义（原文）**：

> *"In some cases, it may be desirable to take advantage of commonly-used, predefined configurations provided by nixpkgs, but different from those that come as default. This is a role fulfilled by NixOS's **Profiles**, which come as files living in `<nixpkgs/nixos/modules/profiles>`. That is to say, expected usage is to add them to the `imports` list of your `/etc/configuration.nix`"*

```nix
{ imports = [ <nixpkgs/nixos/modules/profiles/profile-name.nix> ]; }
```

> **官方还有一句很重要**：*"Even if some of these profiles seem only useful in the context of install media, **many are actually intended to be used in real installs.**"*

**官方全表（11 个 profile，逐条原文要点）**：

| Profile | 官方描述要点 | 对你是否有用 |
|---|---|---|
| **all-hardware** | 启用 NixOS 支持的所有硬件：所有 firmware + 所有可引导设备在 initrd 里启用。**主要用途是安装 CD**。含 SATA/PATA、SCSI（部分）、USB、Firewire（未测试）、Virtio、VMware、Hyper-V 的模块；开 `hardware.enableAllFirmware` | ⚠️ **装机盘专用**，日常用会显著增大 initrd |
| **base** | 「最小安装 CD」的软件包集合：文本浏览器、块设备工具、网络工具、硬件诊断、文件系统工具（含对应内核模块） | ⚠️ 恢复介质用 |
| **graphical** | **Plasma 6 桌面**（安装 CD 用）。设 `services.xserver.enable`、`services.displayManager.sddm.enable`、`services.desktopManager.plasma6.enable`、`services.libinput.enable`；装 `glxinfo` 与 `firefox` | ✅ **想一键要 KDE 的可以用** |
| **headless** | 无头机器（如 EC2）：关 vesa、串口控制台、emergency mode、grub splash；**内核 panic 时自动重启** | ✅ **想当服务器用** |
| **minimal** | 极简配置，无图形。**只保留用户选的 locale**，**关闭包的文档** | ✅ **省空间**（但你会失去 `man` 页） |
| **installation-device** | 安装设备（CD）基础配置：可再分发的 firmware + Clone Config + 一份 nixpkgs channel（让 `nixos-install` 开箱可用）；强制启用 Nixpkgs 与 NixOS 文档；**TTY 8 自动显示 NixOS 手册**；禁用 udisks；`nixos` 用户自动登录；root 与 nixos 免密登录；**免密 sudo**；启用 NetworkManager（可用 `nmtui` 交互配置） | ⚠️ **只做装机盘** |
| **docker-container** | 生成 Docker 镜像用的 profile：导入 Minimal + Clone Config，设 `boot.isContainer` 等容器上下文选项 | ✅ 想自己做容器镜像时 |
| **qemu-guest** | QEMU 客户机优化 | ⚠️ 虚拟机用 |
| **demo** | 演示配置 | ➖ 低相关 |
| **clone-config** | 把当前配置复制到新机 | ✅ 装第二台机器时 |
| **perlless** | 去掉 Perl 依赖 | ⚠️ 见下 |
| **image-based-appliance** | **不可切换系统**（见 §33.10） | ✅ 想做「Aeon 式」不可变设备时 |

> [!WARNING]
> **`minimal` profile 会关掉包的文档** —— 这意味着 `man configuration.nix` 可能失效。
>
> **如果你想省空间但保留文档**，不要用这个 profile，改用 §30.3 的 GC 策略。

> [!TIP]
> **`perlless` 与「去 Perl 化」的背景**：官方在三处提到「去掉 Perl 依赖」——`systemd.sysusers`（§28.5）、`services.userborn`（§28.6）、`system.etc.overlay`（§33.8）。**这是 NixOS 近几年的一个明确方向**：把 activation 阶段的 Perl 脚本换成 systemd 原生机制。
>
> **对你的意义**：这三个都是**实验性**的。**日常用户不必开**；但如果你追求「最小闭包」，它们能砍掉 Perl 及其依赖。

> [!NOTE]
> **官方没有说的（本指南补充）**：`imports` 里的 `<nixpkgs/nixos/modules/profiles/...>` 用的是 **`<nixpkgs>` 语法**，它读的是 `NIX_PATH`。**在 flake 配置里这个语法不可用**，要改成 `"${modulesPath}/profiles/xxx.nix"`：
> ```nix
> { modulesPath, ... }:
> {
>   imports = [ "${modulesPath}/profiles/headless.nix" ];
> }
> ```
> 这正是官方在 `sec-non-switchable-system` 和 `sec-image-repart` 里用的写法（见 §33.10 / §35.4）。

### 26.9 六个反模式

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | 凭记忆写选项名 | `does not exist` 求值失败 | 从 <https://search.nixos.org/options> 复制 |
| 2 | 内核参数不加引号 | 被解析成嵌套 set，报「选项不存在」 | `"net.ipv4.tcp_keepalive_time"` |
| 3 | 复制粘贴而不是用 `let` / 函数 | 配置膨胀，改一处漏三处 | §26.4 的两层抽象 |
| 4 | 动不动就 `mkForce` | 覆盖掉别人的合理默认，日后难排查 | **先问「有没有对应选项」**；`mkForce` 是最后手段 |
| 5 | 在 `config.` 能读的地方硬编码 | 换个机器就要改 | 用 `config.xxx` 做条件（§26.6） |
| 6 | 大配置全塞 `configuration.nix` | 2000 行单文件 | `imports` 拆成 `hardware.nix` / `desktop.nix` / `gaming.nix` |

> [!TIP]
> **给「Vibe Coding」用户的一条建议**：让 Agent 改配置时，**明确要求它用 `imports` 分文件**。这样：
> - 每次改动只影响一个文件 → `git diff` 清晰
> - Agent 只读相关文件 → 上下文更小、更不容易出错
> **本指南 §13.x 给的完整配置是单文件的**，那是为了「方便一次抄完」；**你实际维护时应该拆开。**

---

---

## 二十七、文件系统、磁盘加密与存储（官方 `ch-file-systems`）

本章补的是官方手册 **Part II** 的 `ch-file-systems`、`sec-luks-file-systems`、`sec-sshfs-file-systems`、`sec-overlayfs`。

**为什么这一章值得单独写**：本指南第二章的装机流程里，`fileSystems.*` 是 `nixos-generate-config` **自动生成**的 —— 你从来没手写过它。但一旦你要**加一块盘**、**加密一个分区**、或者**改挂载选项**，就必须理解它。**而且这块写错会丢数据。**

### 27.1 `fileSystems.*` 的完整语义

**官方最小例子（原文）**：

```nix
{
  fileSystems."/data" = {
    device = "/dev/disk/by-label/data";
    fsType = "ext4";
  };
}
```

**官方对这一行做了什么的说明（原文，逐句拆）**：

> *"This will create an entry in `/etc/fstab`, which will generate a corresponding `systemd.mount` unit via `systemd-fstab-generator`."*

> *"The filesystem will be mounted automatically **unless `"noauto"` is present in `options`**. `"noauto"` filesystems can be mounted explicitly using `systemctl` e.g. `systemctl start data.mount`."*

> *"**Mount points are created automatically if they don't already exist.**"*

> *"For `device`, it's best to use the **topology-independent device aliases** in `/dev/disk/by-label` and `/dev/disk/by-uuid`, as these don't change if the topology changes (e.g. if a disk is moved to another IDE controller)."*

> *"You can usually omit the file system type (`fsType`), since `mount` can usually detect the type and load the necessary kernel module automatically. However, **if the file system is needed at early boot (in the initial ramdisk) and is not `ext2`, `ext3` or `ext4`, then it's best to specify `fsType`** to ensure that the kernel module is available."*

**官方的一条重要警告（原文）**：

> *"**System startup will fail if any of the filesystems fails to mount, dropping you to the emergency shell.** You can make a mount asynchronous and non-critical by adding `options = [ "nofail" ];`."*

> [!DANGER]
> **这是本章最重要的一条。**
>
> **默认行为是「挂不上就进不去系统」** —— 不是警告，是**直接掉到 emergency shell**。
>
> **最常见的踩坑场景**：
> 1. 你加了一块**移动硬盘**（USB），写了 `fileSystems."/mnt/backup"`，**忘了加 `nofail`**
> 2. 某天拔掉硬盘开机 → **系统卡在 emergency shell**
> 3. 你不知道要输 root 密码进去注释掉配置 → 以为系统坏了
>
> **正确写法**：
> ```nix
> fileSystems."/mnt/backup" = {
>   device = "/dev/disk/by-uuid/xxxx";
>   fsType = "ext4";
>   options = [ "nofail" "x-systemd.device-timeout=10s" ];
> };
> ```
> - **`nofail`**：挂不上也继续启动
> - **`x-systemd.device-timeout=10s`**：等设备最多 10 秒（否则默认 90 秒）
>
> **判据**：**这块盘「没有它系统就不能用」吗？** 不是 → 加 `nofail`。

**`neededForBoot` 选项**（本指南补充，官方在 SSHFS 与 troubleshooting 章节间接提到）：

| 选项 | 含义 | 什么时候要 |
|---|---|---|
| `neededForBoot = true` | 这个文件系统在 **initrd 阶段**就要挂上 | 只有当 `/nix` 或用户数据目录在**另一块盘**上时才需要 |
| （不设，默认） | 在 stage 2 挂载 | **99% 的情况** |

> **官方在 `sec-boot-problems` 里给了一个直接相关的提示**：*"this could be useful if you've forgotten to set `neededForBoot` on a file system"* —— 也就是说，**忘了设它会导致启动失败**，而官方的调试参数 `boot.debug1mounts` 正是用来诊断这个的（见 §30.6）。

**你的 AMD 桌面推荐布局**（本指南综合官方语义给出）：

| 挂载点 | device | fsType | options | 说明 |
|---|---|---|---|---|
| `/` | `/dev/disk/by-uuid/...` 或 `/dev/mapper/crypted` | `ext4` | `[ "defaults" ]` | 根分区 |
| `/boot` | `/dev/disk/by-uuid/...` | `vfat` | `[ "fmask=0077" "dmask=0077" ]` | **UEFI 必须 vfat**；`fmask/dmask` 是官方安装器生成的写法 |
| `/nix` | （可选，同根） | — | — | 只有想给 `/nix` 单独分区时才写 |
| `/mnt/games` | `/dev/disk/by-uuid/...` | `ext4` | `[ "nofail" ]` | 第二块 SSD 放游戏库 |
| `/mnt/backup` | `/dev/disk/by-uuid/...` | `ext4` | `[ "nofail" "x-systemd.device-timeout=10s" ]` | **必须 `nofail`** |

> [!TIP]
> **Steam 游戏库放第二块盘的两种做法**：
> 1. **`fileSystems` 挂载 + Steam 里添加库路径**（推荐，声明式，重启自动挂）
> 2. 只在 Steam 里加路径（不推荐，Steam 可能自己管理挂载）
>
> 选 1 时**务必加 `nofail`** —— 否则那块盘坏了你连桌面都进不去。

### 27.2 LUKS 磁盘加密：官方完整流程

**官方定义（原文）**：

> *"NixOS supports file systems that are encrypted using **LUKS** (Linux Unified Key Setup)."*

**官方给的完整命令序列（逐字照抄）**：

```bash
# cryptsetup luksFormat /dev/disk/by-uuid/3f6b0024-3a44-4fde-a43a-767b872abe5d

WARNING!
========
This will overwrite data on /dev/disk/by-uuid/3f6b0024-3a44-4fde-a43a-767b872abe5d irrevocably.

Are you sure? (Type uppercase yes): YES
Enter LUKS passphrase: ***
Verify passphrase: ***

# cryptsetup luksOpen /dev/disk/by-uuid/3f6b0024-3a44-4fde-a43a-767b872abe5d crypted
Enter passphrase for /dev/disk/by-uuid/3f6b0024-3a44-4fde-a43a-767b872abe5d: ***

# mkfs.ext4 /dev/mapper/crypted
```

> [!DANGER]
> **`luksFormat` 会不可逆地覆盖那块设备上的全部数据。** 官方原文就是 *"This will overwrite data ... irrevocably"*。
>
> **执行前必须做的两件事**：
> 1. `lsblk -f` 确认设备路径**真的是你想加密的那块**（不是你的系统盘）
> 2. 确认里面**没有你要保留的数据**
>
> **不要在 `/dev/sdX` 这种「顺序命名」上写脚本** —— 加一块盘就可能变。用 `/dev/disk/by-id/` 或 `by-uuid`。

**官方给的 NixOS 配置（原文）**：

```nix
{
  boot.initrd.luks.devices.crypted.device = "/dev/disk/by-uuid/3f6b0024-3a44-4fde-a43a-767b872abe5d";
  fileSystems."/".device = "/dev/mapper/crypted";
}
```

**官方关于 GRUB 的补充（原文）**：

> *"Should grub be used as bootloader, and `/boot` is located on an encrypted partition, it is necessary to add the following grub option: `{ boot.loader.grub.enableCryptodisk = true; }`"*

> [!IMPORTANT]
> **注意：你是 systemd-boot 用户（本指南第二章推荐的），所以不需要 `enableCryptodisk`。** 那条只对 GRUB 有效。
>
> **但有一条对你有用的推论**：**systemd-boot 只能读它自己能读的分区**。如果你把 `/boot` 加密了，systemd-boot 就无法加载内核 → **`/boot` 必须是未加密的 ESP（vfat）**。
>
> **所以 AMD 桌面的标准加密方案是**：
> - `/boot`（ESP，vfat，**不加密**）
> - `/`（LUKS + ext4，**加密**）
> - 可选：`/nix` 单独分区（**加密**，需设 `neededForBoot`）
>
> **这是「LUKS 全盘加密」的通常含义** —— 官方原文用的也是这种结构（`/boot` 未加密 + `/` 加密）。

> [!TIP]
> **`nixos-generate-config` 会自动识别 LUKS** —— 官方原文：*"The LUKS volume should be automatically picked up by `nixos-generate-config`, but you might want to verify that your `hardware-configuration.nix` looks correct."*
>
> **所以最省事的做法**：用**图形安装器**（§2.6）在分区界面勾选加密，它会把这一切自动写好。**手写只在你事后加盘时才需要。**

**验证加密是否生效**：

```bash
lsblk -f                                    # 应看到 crypt 类型与 /dev/mapper/xxx
sudo cryptsetup status crypted              # 应显示 type: LUKS2, cipher, key size
sudo dmsetup ls --tree                      # 确认 device-mapper 映射
cat /etc/crypttab                           # NixOS 生成的内容
```

> [!WARNING]
> **LUKS 的两个「备份」提醒（本指南补充）**：
> 1. **LUKS header 必须备份** —— header 损坏 = 数据永久丢失（即使记得密码）。命令：
>    ```bash
>    sudo cryptsetup luksHeaderBackup /dev/sda2 --header-backup-file luks-header.img
>    ```
>    **把 `luks-header.img` 存到另一台机器/离线介质**。
> 2. **至少留一个备用 key slot**（见 §27.3 的 recovery key）—— 只有一个密码时，输错次数过多或忘记 = 数据丢失。

### 27.3 FIDO2 解锁与 systemd-cryptenroll

**官方给了两条路**。

**路 A：不用 systemd stage 1（`fido2luks`）**

官方原文：*"NixOS also supports unlocking your LUKS-Encrypted file system using a FIDO2 compatible token."*

```bash
# export FIDO2_LABEL="/dev/sda2 @ $HOSTNAME"
# fido2luks credential "$FIDO2_LABEL"
f1d00200108b9d6e849a8b388da457688e3dd653b4e53770012d8f28e5d3b269865038c346802f36f3da7278b13ad6a3bb6a1452e24ebeeaa24ba40eef559b1b287d2a2f80b7

# fido2luks -i add-key /dev/sda2 f1d00200108b9d6e849a8b388da457688e3dd653b4e53770012d8f28e5d3b269865038c346802f36f3da7278b13ad6a3bb6a1452e24ebeeaa24ba40eef559b1b287d2a2f80b7
Password:
Password (again):
Old password:
Old password (again):
Added to key to device /dev/sda2, slot: 2
```

对应配置：

```nix
{
  boot.initrd.luks.fido2Support = true;
  boot.initrd.luks.devices."/dev/sda2".fido2.credential =
    "f1d00200108b9d6e849a8b388da457688e3dd653b4e53770012d8f28e5d3b269865038c346802f36f3da7278b13ad6a3bb6a1452e24ebeeaa24ba40eef559b1b287d2a2f80b7";
}
```

**官方的安全提醒（原文）**：

> *"You can also use the FIDO2 **passwordless** setup, but **for security reasons, you might want to enable it only when your device is PIN protected**, such as Trezor."*

```nix
{ boot.initrd.luks.devices."/dev/sda2".fido2.passwordLess = true; }
```

**路 B：systemd stage 1（官方推荐路线）**

> **官方原文**：*"If systemd stage 1 is enabled, it handles unlocking of LUKS-encrypted volumes during boot."*

```nix
{
  boot.initrd = {
    luks.devices.root = {
      crypttabExtraOpts = [ "fido2-device=auto" ];
      device = "/dev/sda2";
    };
    systemd.enable = true;
  };
}
```

> *"All tokens that should be used for unlocking the LUKS2-encrypted volume must first be enrolled using `systemd-cryptenroll`."*

```bash
# systemd-cryptenroll --fido2-device=auto /dev/sda2
```

> *"Existing key slots are left intact, unless `--wipe-slot=` is specified. **It is recommended to add a recovery key that should be stored in a secure physical location** and can be entered wherever a password would be entered."*

```bash
# systemd-cryptenroll --recovery-key /dev/sda2
```

> [!IMPORTANT]
> **官方那句「recommended to add a recovery key」是本章第二重要的提醒。**
>
> **`systemd-cryptenroll --recovery-key` 生成的恢复密钥是「万一 YubiKey 丢了/坏了」的唯一出路。** 把它**打印出来**或写到纸上，放到**物理安全的地方**（不是同一台机器上）。
>
> **这是「你只有一把钥匙」问题的官方解法。**

> [!NOTE]
> **`systemd.enable = true`（systemd stage 1）在 26.05 的状态**：官方文档把它描述为**可用且有专属调试参数**（`rd.systemd.break=` / `rd.systemd.debug_shell`，见 §30.6）。**它不是实验性的**，但官方仍同时保留 scripted stage 1（标记为 deprecated）。
>
> **对你的建议**：**日常不需要开**（除非你要用 FIDO2 或 TPM2 解锁）。默认的 scripted stage 1 更简单，且官方所有调试参数都覆盖它。

### 27.4 SSHFS：把远程目录挂成本地

**官方定义（原文）**：

> *"SSHFS is a FUSE filesystem that allows easy access to directories on a remote machine using the SSH File Transfer Protocol (SFTP). **It means that if you have SSH access to a machine, no additional setup is needed to mount a directory.**"*

**交互式（官方原文）**：

```bash
$ sshfs my-user@example.com:/my-dir /mnt/my-dir
$ fusermount -u /mnt/my-dir
```

**非交互式（开机自动挂载）—— 官方配置原文**：

```nix
{
  fileSystems."/mnt/my-dir" = {
    device = "my-user@example.com:/my-dir/";
    fsType = "sshfs";
    options = [
      # Filesystem options
      "allow_other"           # for non-root access
      "_netdev"               # this is a network fs
      "x-systemd.automount"   # mount on demand

      # SSH options
      "reconnect"                      # handle connection drops
      "ServerAliveInterval=15"         # keep connections alive
      "IdentityFile=/var/secrets/example-key"
    ];
  };
}
```

**官方的前置条件（原文）**：

> *"Mounting non-interactively requires some precautions because sshfs will run at boot and under a different user (**root**). For obvious reason, you can't input a password, so **public key authentication using an unencrypted key is needed**."*

```bash
$ ssh-keygen -t ed25519 -P '' -f example-key
```

> *"To keep the key safe, change the ownership to `root:root` and make sure the permissions are **600**: OpenSSH normally refuses to use the key if it's not well-protected."*

> [!DANGER]
> **官方明确要求「无密码的私钥」+ 「`root:root` 600 权限」—— 这是一个真实的安全权衡。**
>
> **风险**：那把私钥**没有密码保护**，且**放在 `/var/secrets/`**。任何能读 root 文件的人都能拿到它，并能登录那台远程机器。
>
> **官方的替代做法（本指南推荐）**：
> - **用 `x-systemd.automount` + 按需挂载**（官方选项里已有）→ 只在访问时才连
> - **限制那把 key 在远程机器上的权限**：在 `~/.ssh/authorized_keys` 里加 `command=` 或 `from=` 限制
> - **或者干脆不用 SSHFS**，改用 `rsync` / `syncthing`
>
> **不要把 `IdentityFile` 指向你的主力 SSH key。**

**官方给的排错方法（原文）**：

```bash
$ journalctl -u $(systemd-escape -p /mnt/my-dir/).mount
```

> **官方注释**：*"If the mount point contains special characters it needs to be escaped using `systemd-escape`. This is due to the way systemd converts paths into unit names."*

> [!TIP]
> **`systemd-escape -p <路径>` 这个技巧值得记住** —— 它是「路径 → systemd 单元名」的官方转换工具。**任何「这个挂载点/设备的日志在哪」的问题都用它。**
>
> 加 `"debug"` 选项可以拿到 SSHFS 的详细日志（官方原文：*"you can add the option `"debug"`"*）。

### 27.5 Overlayfs：NixOS 的官方抽象

**官方原文**：

> *"NixOS offers a convenient abstraction to create both read-only as well writable overlays."*

```nix
{
  fileSystems = {
    "/writable-overlay" = {
      overlay = {
        lowerdir = [ writableOverlayLowerdir ];
        upperdir = "/.rw-writable-overlay/upper";
        workdir = "/.rw-writable-overlay/work";
      };
      # Mount the writable overlay in the initrd.
      neededForBoot = true;
    };
    "/readonly-overlay".overlay.lowerdir = [
      writableOverlayLowerdir
      writableOverlayLowerdir2
    ];
  };
}
```

> **官方补充**：*"If `upperdir` and `workdir` are not null, they will be created before the overlay is mounted. **To mount an overlay as read-only, you need to provide at least two `lowerdir`s.**"*

> [!NOTE]
> **这个抽象对你大概率用不到** —— 它是给「不可变系统」（§33.8 的 `/etc` overlay、§33.10 的 Appliance）用的。
>
> **但有一个间接相关的用途**：如果你想做「**临时系统**」（rootfs 是 tmpfs，重启清空），官方在 `ch-system-state` 里专门讲了这个（见 §30.1）。**那才是你真正会碰到 overlay 的场景。**

### 27.6 七个反模式

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | 移动盘不写 `nofail` | **拔盘后开不了机**，掉 emergency shell | `options = [ "nofail" ]` |
| 2 | 用 `/dev/sdX` 而非 `by-uuid` / `by-id` | 加盘后设备名漂移 → **挂错盘或挂不上** | `by-uuid` / `by-id` |
| 3 | `/boot` 加密 | systemd-boot 读不到内核 → **开不了机** | `/boot` 保持未加密 vfat |
| 4 | 加密盘不备份 LUKS header | header 坏了数据永久丢失 | `luksHeaderBackup` 到离线介质 |
| 5 | 只留一个 LUKS key slot | 密码忘了 = 数据没了 | `systemd-cryptenroll --recovery-key` |
| 6 | SSHFS 用主力私钥 | 私钥无密码保护地暴露 | 专用受限 key + `x-systemd.automount` |
| 7 | 改 `fileSystems` 后不 `nixos-rebuild dry-build` | 语法错直接生效 → 可能开不了机 | **改存储配置前必跑 `dry-build`** |

> [!TIP]
> **改存储配置的安全流程**（本指南建议）：
> ```bash
> sudo cp -r /etc/nixos /etc/nixos.bak-$(date +%F)   # 1. 备份
> sudo nano /etc/nixos/hardware-configuration.nix    # 2. 改
> sudo nixos-rebuild dry-build                       # 3. 只求值，不切换
> sudo nixos-rebuild test                            # 4. 切换但重启后回滚
> # 确认没问题、且重启过至少一次之后：
> sudo nixos-rebuild switch                          # 5. 固化
> ```
> **`test` 而不是直接 `switch`** —— 因为 `test` 不会写进 bootloader 的默认项，**重启就回到旧配置**。这是官方 `sec-rollback` 思路的主动用法。

---

---

## 二十八、用户、组与账户安全（官方 `sec-user-management`）

本章补的是官方手册 **Part II** 的 `sec-user-management`、`sec-systemd-sysusers`、`sec-userborn`、`sec-restrict-usage-time`。

**为什么这一章值得单独写**：本指南第九章 / 第二十一章反复强调「**agent 不要用 root 跑**」，但一直没讲**声明式用户的完整语义**。这一章补上 —— 特别是 `users.mutableUsers` 这个开关，**它决定了你的用户是「NixOS 管的」还是「你自己管的」**，直接关系到 agent 能不能改自己的账户。

### 28.1 声明式用户：官方标准写法

**官方定义（原文）**：

> *"NixOS supports both **declarative** and **imperative** styles of user management. In the declarative style, users are specified in `configuration.nix`."*

```nix
{
  users.users.alice = {
    isNormalUser = true;
    home = "/home/alice";
    description = "Alice Foobar";
    extraGroups = [
      "wheel"
      "networkmanager"
    ];
    openssh.authorizedKeys.keys = [ "ssh-dss AAAAB3Nza... alice@foobar" ];
  };
}
```

**官方对每一处的解释（原文）**：

> *"Note that `alice` is a member of the `wheel` and `networkmanager` groups, which allows her to use `sudo` to execute commands as root and to configure the network, respectively."*

> *"**Users created in this way do not have a password by default, so they cannot log in via mechanisms that require a password.** However, you can use the `passwd` program to set a password, which is **retained across invocations of `nixos-rebuild`**."*

> [!IMPORTANT]
> **「声明式建的用户默认没有密码」这一条经常让人困惑。**
>
> **表现**：`nixos-rebuild switch` 之后，新用户在登录界面**输什么都进不去**（或者根本没有登录项）。
>
> **官方给的解法**：`passwd` 设一次，**之后 rebuild 不会冲掉**。
>
> **为什么不会冲掉**：因为密码存在 `/etc/shadow` 里，而 `users.mutableUsers` 默认为 `true`（见 §28.2）—— NixOS **不会覆盖**它没声明的字段。

**官方给的 uid 指定方式**：

```nix
{ uid = 1000; }
```

**官方给的组定义**：

```nix
{ users.groups.students.gid = 1000; }
```

> *"As with users, the group ID (gid) is optional and will be assigned automatically if it's missing."*

**官方的命令式对照（原文）**：

```bash
# useradd -m alice      # -m 创建 home
# passwd alice
# userdel -r alice      # -r 删 home
```

> **官方给了一个很多人不知道的细节**：*"To make all nix tools available to this new user use `su - USER` which opens a login shell (== shell that loads the profile) for given user. This will create the `~/.nix-defexpr` symlink."*
>
> ```bash
> # su - alice -c "true"
> ```

> [!TIP]
> **`su - alice -c "true"` 这行命令解决一个真实问题**：用 `useradd` 建的**命令式用户**，`~/.nix-defexpr` 不存在，于是 `nix-env` / `nix profile` 报「找不到 channel」。
>
> **本指南的对应场景**：如果你按第九章用 `useradd` 建了 `hermes` 用户（而不是声明式），**跑一次这条命令**能修好它的 Nix 环境。
>
> **但更好的做法是声明式建用户**（§28.8）—— 那样 NixOS 会自动处理。

### 28.2 `users.mutableUsers`：最重要的一个开关

**官方原文（逐字）**：

> *"If you set `users.mutableUsers` to `false`, then the contents of `/etc/passwd` and `/etc/group` will be **congruent** to your NixOS configuration. For instance, **if you remove a user from `users.users` and run `nixos-rebuild`, the user account will cease to exist.** Also, **imperative commands for managing users and groups, such as `useradd`, are no longer available.** Passwords may still be assigned by setting the user's `hashedPassword` option. A hashed password can be generated using `mkpasswd`."*

**两种模式的完整对比**：

| 维度 | `mutableUsers = true`（**默认**） | `mutableUsers = false` |
|---|---|---|
| `/etc/passwd` 与配置的关系 | 配置是「初始值」，之后可被 `passwd` / `usermod` 改 | **完全一致**（配置是唯一真相） |
| 删掉 `users.users.foo` 后 | 用户**残留**在 `/etc/passwd` | **用户消失** |
| `useradd` / `usermod` | **可用** | **不可用** |
| 密码怎么设 | `passwd`（交互式，存 `/etc/shadow`） | 只能用 `hashedPassword` |
| 声明式程度 | 部分 | **完全** |
| 适合谁 | 桌面用户（默认就好） | 服务器 / 不可变系统 / **追求完全声明式的人** |

> [!IMPORTANT]
> **这个开关直接决定「Agent 能不能改用户」**：
>
> | 你的选择 | Agent 能做到 | 代价 |
> |---|---|---|
> | `mutableUsers = true`（默认） | `useradd` / `passwd` / `usermod` 都能用（需 root） | 声明式不彻底，换机时用户可能不一致 |
> | `mutableUsers = false` | **完全不能改用户** —— 只能改 `configuration.nix` | **换机完全一致**；但忘了 root 密码就麻烦 |
>
> **本指南第九章的「agent 用普通用户跑」建议**：**保持 `mutableUsers = true`**（默认）。因为：
> 1. agent 用户是**一次建好、长期不变**的 → 不需要「完全声明式」带来的好处
> 2. 但你需要 `passwd` 给它设初始密码，或者用 `openssh.authorizedKeys` 走 SSH
> 3. **`mutableUsers = false` 会让「给 agent 用户设密码」变麻烦**（必须先生成 hash 再写进配置）

> [!WARNING]
> **`mutableUsers = false` 的一个真实陷阱**：如果你**在已有系统上**改成 `false`，NixOS 会**用配置覆盖 `/etc/passwd`**。
>
> **后果**：任何**不在配置里**的用户（例如你之前用 `useradd` 建的）**会被删掉**，它的 home 目录**不会被删但会变成无主**。
>
> **正确做法**：改之前先 `cat /etc/passwd | grep -v nologin` 把现有用户全部抄进 `users.users`。

**官方给 `hashedPassword` 生成工具**：`mkpasswd`。

```bash
$ mkpasswd -m sha-512
Password: ********
$6$rounds=...$....        # ← 把这个字符串填进 hashedPassword
```

```nix
{
  users.users.alice.hashedPassword = "$6$rounds=...$...";
}
```

> [!DANGER]
> **`hashedPassword` 会明文出现在 `/nix/store` 里**（因为它在 `configuration.nix` 里，而配置会被复制进 store）。
>
> **hash 本身不是明文密码**，但：
> - 它对**离线爆破**没有保护（`/etc/shadow` 有，因为只有 root 能读；`/nix/store` 是**全局可读**的）
> - 任何人拿到你的 flake 仓库就能对它跑 `hashcat`
>
> **正确做法**：
> - **桌面机** → 用默认的 `mutableUsers = true` + `passwd`（密码只存 `/etc/shadow`）
> - **必须声明式时** → 用 **sops-nix / agenix** 把 hash 加密后再注入（本指南 §21.x 已给出 Hermes 侧的接法）
> - **绝对不要**把 `hashedPassword` 提交到公开 Git 仓库

### 28.3 uid / gid 的稳定性与 `/var/lib/nixos`

> **官方在 `sec-nixos-state` 里的原文**：*"`/var/lib/nixos` should persist: it holds **state needed to generate stable uids and gids for declaratively-managed users and groups**, etc."*

> [!IMPORTANT]
> **这一条解释了「为什么换机时 uid 会变」**：
>
> NixOS 给声明式用户分配 uid 时，会**优先复用之前分配过的值** —— 而这个「之前分配过的记录」就存在 **`/var/lib/nixos`**。
>
> | 场景 | 结果 |
> |---|---|
> | 同一个系统，加一个新用户 | 新用户拿下一个空闲 uid（旧用户 uid **不变**）✅ |
> | **重装系统**（`/var/lib/nixos` 清空） | uid **可能全部重排** ⚠️ |
> | 把 `/var/lib/nixos` 备份并恢复 | uid **保持一致** ✅ |
>
> **为什么 uid 变了是问题**：所有**已存在文件**的属主仍是旧 uid → 显示为数字或错误用户名 → **权限全乱**（典型表现：桌面登录后一堆东西打不开）。
>
> **结论**：**重装前备份 `/var/lib/nixos`**，或者**在配置里显式写 `uid = 1000;`**。后者更简单可靠。

> [!TIP]
> **本指南的推荐**：给**你关心的每个用户都显式写 uid**。
> ```nix
> users.users.yourname = { isNormalUser = true; uid = 1000; };
> users.users.hermes   = { isSystemUser = true; uid = 993; group = "hermes"; };
> ```
> **理由**：uid 一旦固定，`/var/lib/nixos` 丢不丢都无所谓，换机/重装都不会乱。

### 28.4 系统用户 vs 普通用户

官方例子只给了 `isNormalUser = true`。**但 NixOS 还有系统用户的概念**（本指南补充，官方在 `sec-userborn` 提到「normal users (with a GID >= 1000)」）：

| 类型 | 关键选项 | uid 范围 | 有 home | 能登录 |
|---|---|---|---|---|
| **普通用户** | `isNormalUser = true` | ≥ 1000 | ✅ 自动创建 | ✅ |
| **系统用户** | `isSystemUser = true` | < 1000 | ❌（除非写 `home`） | ❌（shell 是 nologin） |

```nix
# 系统用户的标准写法（服务/agent 用）
users.users.hermes = {
  isSystemUser = true;
  group = "hermes";
  home = "/var/lib/hermes";     # 显式给 home
  createHome = true;
  uid = 993;
};
users.groups.hermes = { };
```

> [!IMPORTANT]
> **`isSystemUser = true` 与「agent 不用 root」的关系**（连本指南 §9.4 / §21.7）：
>
> - **`isSystemUser` 不是「低权限」的同义词** —— 它只是「不是人类账户」
> - **真正的权限边界来自**：`User=` 写在 systemd unit 里（§29.4）、`NoNewPrivileges`、`ProtectSystem`、`ReadWritePaths`
> - **`isSystemUser` 给你的是**：不会出现在登录界面、不会有交互式 shell、uid 稳定
>
> **本指南 §21.x 给 Hermes 用的就是这套**（`createUser = false` + 自己声明 + 显式 `linger = true`）。**`linger` 那一条是踩过的坑**（见本指南 §22.x 与坑清单 #44/#45）。

### 28.5 systemd-sysusers（实验性）

> **官方原文**：*"**This is experimental.** Please consider using Userborn over systemd-sysusers as it's more feature complete."*

```nix
{ systemd.sysusers.enable = true; }
```

> **官方说明**：*"Instead of using a custom perl script to create users and groups, you can use systemd-sysusers... The primary benefit of this is to **remove a dependency on perl**."*

### 28.6 userborn（实验性，但官方推荐）

> **官方原文**：*"**This is experimental.** Like systemd-sysusers, Userborn doesn't depend on Perl but offers some more advantages over systemd-sysusers:"*

**官方列出的三个优势（原文）**：

> - *"It can create "normal" users (with a GID >= 1000)."*
> - *"It can update some information about users. Most notably it can **update their passwords**."*
> - *"It will **warn when users use an insecure or unsupported password hashing scheme**."*

> *"Userborn is the **recommended way** to manage users if you don't want to rely on the Perl script. It **aims to eventually replace the Perl script by default**."*

```nix
{ services.userborn.enable = true; }
```

**官方给的额外能力 —— 把密码文件挪出 `/etc`**：

```nix
{ services.userborn.passwordFilesLocation = "/persistent/etc"; }
```

> **官方说明（原文）**：*"This is useful when you store `/etc` on a tmpfs or if `/etc` is immutable (e.g. when using `system.etc.overlay.mutable = false;`). In the latter case the original files are by default stored in `/var/lib/nixos`."*

> **官方给的一个重要行为差异（原文）**：*"Userborn implements immutable users by re-mounting the password files read-only. This means that unlike when using the Perl script, **trying to add a new user (e.g. via `useradd`) will fail right away**."*

> [!NOTE]
> **`userborn` + `passwordFilesLocation` 的组合，正是「Aeon 式不可变系统」在 NixOS 上的实现方式之一**（连本指南第二十四章）。
>
> **对你的建议**：
> - **日常桌面** → 不需要开。默认 Perl 脚本工作良好。
> - **想彻底去掉 Perl** → 开 `services.userborn.enable = true`（官方推荐它而不是 `systemd.sysusers`）。
> - **想做不可变系统** → `userborn` + `system.etc.overlay.mutable = false` + `passwordFilesLocation = "/persistent/etc"`。

### 28.7 屏幕时间管理：timekpr-nExT

> **官方原文**：*"Timekpr-nExT is a screen time managing application that helps optimizing time spent at computer for your subordinates, children or even for yourself."*

```nix
{ services.timekpr.enable = true; }
```

> *"This will install the timekpr package and start the timekpr service. You can then use the `timekpra` application to configure time limits for users."*

> [!NOTE]
> **这是官方手册里**唯一**一个「家长控制 / 自我管理」类工具。** 与你的画像（成人游戏用户）相关度不高，但：
> - 如果你要给家人配一台 NixOS 机器，这是官方方案
> - 如果你自己做「防沉迷」（限制游戏时间），它也能用

### 28.8 与 agent 用户的配合（连本指南第九、二十一章）

**把前面几节串起来，agent 用户的完整声明式写法**：

```nix
{ config, pkgs, ... }:
{
  # ── 1. 组与用户（显式 uid，避免 /var/lib/nixos 丢失后乱序）──
  users.groups.hermes = { gid = 993; };
  users.users.hermes = {
    isSystemUser = true;
    group = "hermes";
    uid = 993;
    home = "/var/lib/hermes";
    createHome = true;
    shell = pkgs.bashInteractive;   # 需要交互式 shell 时显式给
  };

  # ── 2. linger：用户级 systemd 服务能开机自启（本指南坑清单 #44/#45）──
  users.users.hermes.linger = true;

  # ── 3. 保持 mutableUsers 默认 true ──
  #    这样可以用 passwd 给 hermes 设密码；且 agent 不依赖声明式账户
  # users.mutableUsers = true;   # ← 默认值，不用写

  # ── 4. 权限边界不在这里，在 systemd unit 里（见 §29.4）──
  systemd.services.hermes-agent = {
    serviceConfig = {
      User = "hermes";
      Group = "hermes";
      NoNewPrivileges = true;          # 不能提权
      ProtectSystem = "strict";        # / 只读
      ProtectHome = "read-only";       # home 只读
      ReadWritePaths = [ "/var/lib/hermes" ];   # 只允许写这一个目录
      PrivateTmp = true;
    };
  };
}
```

> [!IMPORTANT]
> **这张配置回答了一个常被混淆的问题：「用户权限」和「服务权限」是两回事。**
>
> | 层 | 管什么 | 在哪写 |
> |---|---|---|
> | **账户层** | uid/gid、home、shell、能否登录 | `users.users.*`（本章） |
> | **服务层** | 能读写哪些路径、能否提权、能否看到别的进程 | `systemd.services.*.serviceConfig`（§29.4） |
>
> **`isSystemUser = true` 不等于「被沙箱了」。** 一个 `isSystemUser` 的用户，如果 systemd unit 里**没写** `ProtectSystem` / `ReadWritePaths`，**照样能读写整个文件系统**。
>
> **本指南第九章那句「agent 不要做成 root 权限的服务」的准确含义是**：**在服务层加约束**，而不是「建个系统用户就完事」。

### 28.9 六个反模式

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | 不写 `uid`，指望 NixOS 自动分配 | 重装后 uid 重排 → **文件属主全乱** | 显式写 `uid = 1000;` |
| 2 | 把 `hashedPassword` 提交到公开仓库 | `/nix/store` 全局可读 → 可离线爆破 | 用 `passwd`（默认模式）或 sops-nix |
| 3 | 在已有系统上直接改 `mutableUsers = false` | **非配置内的用户被删** | 先把现有用户全抄进配置 |
| 4 | 以为 `isSystemUser = true` 就等于沙箱 | 服务仍能读写整个 FS | **约束写在 systemd unit 里** |
| 5 | agent 用户忘了 `linger = true` | 用户级服务**开机不启动**，且不报错 | 显式写 `linger = true` |
| 6 | 用 `useradd` 建用户后不管 | `~/.nix-defexpr` 缺失 → Nix 命令报错 | `su - <user> -c "true"`，或改声明式 |

> [!TIP]
> **一句话总结本章**：
> **`users.users` 管「账户存不存在」，`users.mutableUsers` 管「谁说了算」，`systemd.services.*.serviceConfig` 管「能干多少事」。** 三件事，三个地方，不要混。

---

---

## 二十九、服务管理：systemd · systemctl · 日志 · cgroup（官方 Part III 前半）

本章补的是官方手册 **Part III · Administration** 的前 7 章：`sec-systemctl`、`sect-nixos-systemd-general`、`sect-nixos-systemd-nixos`、`sec-rebooting`、`sec-user-sessions`、`sec-cgroups`、`sec-logging`。

**为什么这一章是本轮新增里最实用的一章**：本指南前二十五章讲了「怎么配」，但从没讲「**配好之后怎么查**」。出问题时，**90% 的诊断都从 `systemctl status` 和 `journalctl` 开始**。

### 29.1 systemd 的心智模型（官方原文）

> **官方原文**：*"In NixOS, all system services are started and monitored using the **systemd** program. systemd is the "init" process of the system (i.e. **PID 1**), the parent of all other processes. It manages a set of so-called "**units**", which can be things like system services (programs), but also **mount points, swap files, devices, targets (groups of units) and more**."*

> *"Units can have complex dependencies; for instance, one unit can require that another unit must be successfully started before the first unit can be started. **When the system boots, it starts a unit named `default.target`; the dependencies of this unit cause all system services to be started, file systems to be mounted, swap files to be activated, and so on.**"*

**把这段翻译成「你会在报错里看到的词」**：

| 概念 | 是什么 | 你会看到的形式 |
|---|---|---|
| **unit** | 一个「被管理的东西」 | `xxx.service` / `xxx.mount` / `xxx.timer` / `xxx.target` |
| **`.service`** | 一个服务（进程） | `sshd.service` |
| **`.mount`** | 一个挂载点 | `home.mount`、`mnt-games.mount` |
| **`.timer`** | 定时器（替代 cron） | `nixos-upgrade.timer` |
| **`.target`** | 一组 unit 的集合 | `multi-user.target`、`graphical.target` |
| **`default.target`** | **开机起点** | 所有服务的依赖根 |
| **`wantedBy`** | 「谁需要我」 | `wantedBy = [ "multi-user.target" ];` |
| **`requires`** | 「我硬依赖谁」（失败则我也不启动） | `requires = [ "network-online.target" ];` |
| **`after` / `before`** | **只是顺序**，不是依赖 | `after = [ "network-online.target" ];` |

> [!IMPORTANT]
> **`requires` 和 `after` 经常成对出现，但语义完全不同** —— 这是官方例子里最容易看漏的一点：
> ```nix
> {
>   systemd.services.myservice = {
>     after    = [ "network-online.target" ];   # 顺序：网络起来后我才起
>     requires = [ "network-online.target" ];   # 依赖：网络挂了我就别起
>     before   = [ "multi-user.target" ];       # 顺序：我在 multi-user 之前
>     wantedBy = [ "multi-user.target" ];       # 归属：开机时谁把我拉起来
>     serviceConfig = { ExecStart = "..."; };
>   };
> }
> ```
> **只写 `after` 不写 `requires`** → 网络起不来时，你的服务**照样会尝试启动**（然后失败）
> **只写 `requires` 不写 `after`** → 有依赖但**没有顺序**，可能并行启动然后失败
> **忘了 `wantedBy`** → 服务**根本不会开机自启**（这是最常见的坑）

### 29.2 systemctl 命令全集（官方示例 + 补充）

**官方原文**：*"The command `systemctl` is the main way to interact with systemd."*

**官方给的输出示例（原文）**：

```bash
$ systemctl
-.mount          loaded active mounted   /
swapfile.swap    loaded active active    /swapfile
sshd.service     loaded active running   SSH Daemon
graphical.target loaded active active    Graphical Interface
...
```

```bash
$ systemctl status postgresql.service
postgresql.service - PostgreSQL Server
          Loaded: loaded (/nix/store/pn3q73mvh75gsrl8w7fdlfk3fq5qm5mw-unit/postgresql.service)
          Active: active (running) since Mon, 2013-01-07 15:55:57 CET; 9h ago
        Main PID: 2390 (postgres)
          CGroup: name=systemd:/system/postgresql.service
                  ├─2390 postgres
                  ├─2418 postgres: writer process
                  ...
```

> **官方注释**：*"Note that this shows the status of the unit (active and running), **all the processes belonging to the service**, as well as **the most recent log messages from the service**."*

```bash
# systemctl stop postgresql.service
# systemctl start postgresql.service
# systemctl restart postgresql.service
```

> *"These operations are **synchronous**: they wait until the service has finished starting or stopping (or has failed). Starting a unit will cause the dependencies of that unit to be started as well (if necessary)."*

**完整命令表（本指南在官方基础上补充）**：

| 命令 | 作用 | 常用场景 |
|---|---|---|
| `systemctl` | 列出活动 unit | 快速总览 |
| `systemctl status <unit>` | 状态 + 进程 + **最近日志** | **最常用** |
| `systemctl start/stop/restart <unit>` | 启停重启 | 改配置后 |
| `systemctl reload <unit>` | 重读配置（**不重启进程**） | 支持 reload 的服务 |
| `systemctl enable/disable <unit>` | 开机自启（**NixOS 下慎用**，见下） | — |
| `systemctl is-active <unit>` | 只输出 `active` / `inactive` | **写脚本时用** |
| `systemctl is-enabled <unit>` | 是否开机自启 | 诊断「为什么不启动」 |
| `systemctl is-failed <unit>` | 是否失败 | 诊断 |
| `systemctl list-units --failed` | **列出所有失败的 unit** | **开机后第一件事** |
| `systemctl list-timers` | 列出所有定时器 + 下次触发时间 | 查 `nix.gc` / `autoUpgrade` |
| `systemctl cat <unit>` | **打印 unit 文件内容 + 来源路径** | 看 NixOS 生成了什么 |
| `systemctl show <unit>` | 打印全部属性 | 深度诊断 |
| `systemctl show -p MainPID <unit>` | 只取主进程 PID | **验证服务跑在哪个用户下** |
| `systemctl daemon-reload` | 重读 unit 文件 | 手改 unit 后 |
| `systemctl reset-failed <unit>` | 清掉失败状态 | 修好之后 |

> [!WARNING]
> **在 NixOS 上不要用 `systemctl enable` / `disable`。**
>
> **原因**：NixOS 的 unit 文件在 `/nix/store` 里，是**只读且由配置生成**的。`systemctl enable` 会创建符号链接，但：
> - 下次 `nixos-rebuild switch` 会**覆盖**你的改动
> - 如果它链接到 `/nix/store/...`，**GC 之后符号链接会变成死链**（官方在 `sect-nixos-systemd-nixos` 里专门警告过这一点，见 §29.3）
>
> **正确做法**：在 `configuration.nix` 里写 `wantedBy = [ "multi-user.target" ];`（服务）或 `systemd.timers.<name>.wantedBy = [ "timers.target" ];`（定时器）。

> [!TIP]
> **`systemctl list-units --failed` 应该是你开机后的例行检查。** NixOS 有个特点：**某个服务失败不会阻止系统启动**（除非它被 `requiredBy` 到关键 target）。所以你可能带着一个坏掉的服务用几天都不知道。
>
> **本指南建议**：把它写进你的日常检查（§30.x 会给出完整清单）。

### 29.3 NixOS 特有：`systemd.packages` 与用户服务的 GC 陷阱

**官方原文**：

> *"Packages in Nixpkgs sometimes provide systemd units with them, usually in e.g `#pkg-out#/lib/systemd/`. **Putting such a package in `environment.systemPackages` doesn't make the service available to users or the system.** In order to enable a systemd system service with provided upstream package, use (e.g):"*

```nix
{ systemd.packages = [ pkgs.packagekit ]; }
```

> *"Usually NixOS modules written by the community do the above, plus take care of other details. **If a module was written for a service you are interested in, you'd probably need only to use `services.#name#.enable = true;`.**"*

> [!IMPORTANT]
> **这三句是「为什么我装了包却没有服务」的官方答案。**
>
> **判断顺序**：
> 1. **有没有 NixOS 模块？** → 查 <https://search.nixos.org/options>，有就写 `services.xxx.enable = true;`（**首选**）
> 2. **没有模块，但包自带 unit？** → `systemd.packages = [ pkgs.xxx ];`
> 3. **都没有？** → 自己写 `systemd.services.xxx`（§29.4）

**官方的「用户服务」写法（含一个重要警告）**：

> *"User systemd services on the other hand, should be treated differently. Given a package that has a systemd unit file at `#pkg-out#/lib/systemd/user/`, using `systemd.packages` will make you able to start the service via `systemctl --user start`, **but it won't start automatically on login**."*

```bash
$ mkdir -p ~/.config/systemd/user/default.target.wants
$ ln -s /run/current-system/sw/lib/systemd/user/syncthing.service ~/.config/systemd/user/default.target.wants/
$ systemctl --user daemon-reload
$ systemctl --user enable syncthing.service
```

> **官方给的警告（原文，逐字）**：
> *"Using `systemctl --user enable syncthing.service` instead of the above, **will work, but it'll use the absolute path of `syncthing.service` for the symlink, and this path is in `/nix/store/.../lib/systemd/user/`. Hence garbage collection will remove that file and you will wind up with a broken symlink in your systemd configuration, which in turn will not make the service / timer start on login.**"*

> [!DANGER]
> **这是 NixOS 上一个非常隐蔽的坑，而且官方专门为它写了一整段。**
>
> **陷阱**：你直接 `systemctl --user enable foo.service` → 看起来成功了 → **几周后 GC 跑了一次** → 服务**静默地不再自启**。
>
> **为什么会这样**：符号链接指向 `/nix/store/...`，而 GC 删掉了那个 store path（因为它不在任何 profile 的闭包里）。
>
> **正确做法（官方给的）**：手动创建符号链接指向 **`/run/current-system/sw/lib/systemd/user/`**（这是一个稳定的路径），而不是 `/nix/store/...`。
>
> **对「Vibe Coding」用户的建议**：**不要用 `systemctl --user enable`**。要自启就：
> - **系统级** → 写 `systemd.services.<name>` + `wantedBy`（声明式，GC 安全）
> - **用户级** → 用 **home-manager 的 `systemd.user.services`**（本指南 §19.x），它自动生成正确的符号链接
>
> 本指南 §21.x 的 Hermes / OpenClaw 用户服务，走的就是 home-manager 这条路。

### 29.4 定义自定义服务

**官方最小模板（原文）**：

```nix
{
  systemd.services.myservice = {
    after = [ "network-online.target" ];
    requires = [ "network-online.target" ];

    before = [ "multi-user.target" ];
    wantedBy = [ "multi-user.target" ];

    serviceConfig = {
      ExecStart = "...";
    };
  };
}
```

> **官方补充**：*"If you want to specify a multi-line script for `ExecStart`, you may want to use `pkgs.writeShellScript`."*

**本指南在官方基础上补的「安全加固四件套」**（对应 §28.8 的权限边界）：

```nix
{
  systemd.services.myservice = {
    description = "My Service";
    wantedBy = [ "multi-user.target" ];
    after = [ "network-online.target" ];
    requires = [ "network-online.target" ];

    serviceConfig = {
      ExecStart = "${pkgs.myapp}/bin/myapp";
      User = "myservice";
      Group = "myservice";

      # ── 安全加固 ──
      NoNewPrivileges = true;              # 不能提权（挡住 setuid 提权）
      ProtectSystem = "strict";            # / 与 /usr 只读
      ProtectHome = "read-only";           # /home 只读
      ReadWritePaths = [ "/var/lib/myservice" ];   # 唯一可写目录
      PrivateTmp = true;                   # 私有 /tmp
      ProtectKernelTunables = true;        # 不能改 sysctl
      ProtectControlGroups = true;         # 不能改 cgroup
      RestrictAddressFamilies = [ "AF_UNIX" "AF_INET" "AF_INET6" ];

      Restart = "on-failure";
      RestartSec = 5;
    };
  };
}
```

> [!TIP]
> **`systemd-analyze security <unit>` 会给你的服务打安全分**（0–10，越低越好）。
>
> ```bash
> $ systemd-analyze security myservice.service
> ```
>
> 这是**验证「我的 agent 服务到底有多安全」的官方工具** —— 比读文档直观。本指南第九章建议的加固项，全部能被它量化。

**`systemctl cat` 验证 NixOS 生成了什么**：

```bash
$ systemctl cat myservice.service
# /etc/systemd/system/myservice.service
[Unit]
...
[Service]
...
```

> **官方在 `sec-switching-systems` 里提到**：NixOS 用 `X-*` 前缀的**私有扩展**来控制切换行为（`X-StopIfChanged` / `X-ReloadIfChanged` / `X-RestartIfChanged` 等）。这些**只对 `nixos-rebuild switch` 有效**，systemd 本身不认识。详见 §33.6。

### 29.5 模板单元（`base-unit@instance`）

**官方原文**：

> *"systemd supports templated units where a base unit can be started multiple times with a different parameter. The syntax to accomplish this is `service-name@instance-name.service`... NixOS has support for these kinds of units and for template-specific overrides. **A service needs to be defined twice, once for the base unit and once for the instance. All instances must include `overrideStrategy = "asDropin"` for the change detection to work.**"*

```nix
{
  systemd.services = {
    "base-unit@".serviceConfig = {
      ExecStart = "...";
      User = "...";
    };
    "base-unit@instance-a" = {
      overrideStrategy = "asDropin";        # needed for templates to work
      wantedBy = [ "multi-user.target" ];   # causes NixOS to manage the instance
    };
    "base-unit@instance-b" = {
      overrideStrategy = "asDropin";        # needed for templates to work
      wantedBy = [ "multi-user.target" ];   # causes NixOS to manage the instance
      serviceConfig.User = "root";          # also override something for this specific instance
    };
  };
}
```

> [!IMPORTANT]
> **`overrideStrategy = "asDropin"` 是**必须**的** —— 官方原文说 *"All instances must include `overrideStrategy = "asDropin"` for the change detection to work"*。
>
> **漏了会怎样**：NixOS **检测不到实例配置的变化** → 你改了配置，`nixos-rebuild switch` 之后实例**没更新**。
>
> **`asDropin` 的含义**：把实例配置生成为 **drop-in 文件**（`xxx@instance.service.d/override.conf`），而不是完整替换 unit 文件。这样**实例配置能正确覆盖基础模板**，且 systemd 能识别变化。
>
> **你在哪会碰到模板单元**：`container@foo`（§31.x）、`user@1000`、`getty@tty1`、以及很多服务（`openvpn-server@xxx`）。**自己写服务时，能用普通 unit 就别用模板。**

### 29.6 日志：journalctl（官方 `sec-logging`）

**官方原文**：

> *"System-wide logging is provided by **systemd's journal**, which subsumes traditional logging daemons such as `syslogd` and `klogd`. Log entries are kept in binary files in `/var/log/journal/`. The command `journalctl` allows you to see the contents of the journal."*

```bash
$ journalctl -b
```

> *"shows all journal entries **since the last reboot**. (The output of `journalctl` is piped into `less` by default.)"*

```bash
$ journalctl -u postgresql.service
-- Logs begin at Mon, 2013-01-07 13:28:01 CET, end at Tue, 2013-01-08 01:09:57 CET. --
...
Jan 07 15:44:14 hagbard postgres[2681]: [2-1] LOG:  database system is shut down
-- Reboot --
Jan 07 15:45:10 hagbard postgres[2532]: [1-1] LOG:  database system was shut down at 2013-01-07 15:44:14 CET
```

```bash
$ journalctl -b -p crit
Dec 17 21:08:06 mandark sudo[3673]: pam_unix(sudo:auth): auth could not identify password for [alice]
Dec 29 01:30:22 mandark kernel[6131]: [1053513.909444] CPU6: Core temperature above threshold, cpu clock throttled (total events = 1)
```

> **官方给的权限说明（原文）**：*"The system journal is readable by **root and by users in the `wheel` and `systemd-journal` groups**. All users have a **private journal** that can be read using `journalctl`."*

**完整命令表（本指南在官方基础上补充）**：

| 命令 | 作用 | 典型场景 |
|---|---|---|
| `journalctl -b` | 本次开机以来 | **最常用** |
| `journalctl -b -1` | 上一次开机 | 崩溃后重启查看 |
| `journalctl -u <unit>` | 某个服务 | 服务启动失败 |
| `journalctl -u <unit> -f` | 实时跟踪 | 调试中 |
| `journalctl -b -p crit` | 只看 critical 及以上 | **快速定位严重问题** |
| `journalctl -b -p err` | err 及以上 | 日常巡检 |
| `journalctl -k` | 只看内核消息（等价 `dmesg`） | 驱动问题 |
| `journalctl --since "1 hour ago"` | 时间范围 | 刚出的问题 |
| `journalctl --since today` | 今天 | 日常 |
| `journalctl -n 100` | 最后 100 行 | 快速看尾部 |
| `journalctl -x` | 带「解释性提示」 | **看 systemd 给的修复建议** |
| `journalctl --disk-usage` | 日志占多少空间 | 磁盘满时 |
| `journalctl --vacuum-size=500M` | 清理到 500M | 磁盘满时 |
| `journalctl _UID=993` | 按用户过滤 | 查 agent 用户 |
| `journalctl /dev/sda` | 按设备过滤 | 硬件问题 |
| `journalctl -o json-pretty` | JSON 输出 | 喂给 Agent 分析 |

> [!TIP]
> **`journalctl -x` 的「解释性提示」被严重低估。** systemd 会在日志里插入**加粗的修复建议**，形如：
> ```
> ░░ Subject: Unit failed
> ░░ Defined-By: systemd
> ░░ The unit X has entered the 'failed' state with result 'exit-code'.
> ```
> **它会告诉你失败的原因和下一步。** 先看这个，再 Google。

> [!IMPORTANT]
> **日志的持久化默认是开的吗？**
>
> 官方在 `sec-systemd-state` 里说：*"`systemd-journald` writes the system's journal in binary form to `/var/log/journal/{machine-id}`; if (locally) persisting the entire log is desired, it is recommended to make all of `/var/log/journal` persistent. **If not, one can set `Storage=volatile`** ... which disables journal persistence and causes it to be written to `/run/log/journal`."*
>
> **所以**：默认**持久化到磁盘**（`/var/log/journal`）。如果你想要「重启后日志消失」（省空间 / 隐私），设：
> ```nix
> { services.journald.storage = "volatile"; }
> ```
> **对游戏玩家的意义**：持久化日志会持续占磁盘。**建议加一个大小上限**：
> ```nix
> {
>   services.journald.extraConfig = ''
>     SystemMaxUse=500M
>   '';
> }
> ```
> 或者用 §30.3 的 GC 策略一起管。

### 29.7 用户会话：loginctl（官方 `sec-user-sessions`）

**官方原文**：

> *"Systemd keeps track of all users who are logged into the system (e.g. on a virtual console or remotely via SSH). The command `loginctl` allows querying and manipulating user sessions."*

```bash
$ loginctl
   SESSION        UID USER             SEAT
        c1        500 eelco            seat0
        c3          0 root             seat0
        c4        500 alice
```

> *"This shows that two users are logged in locally, while another is logged in remotely. ("Seats" are essentially the combinations of displays and input devices attached to the system; usually, there is only one seat.)"*

```bash
$ loginctl session-status c3
c3 - root (0)
           Since: Tue, 2013-01-08 01:17:56 CET; 4min 42s ago
          Leader: 2536 (login)
            Seat: seat0; vc3
             TTY: /dev/tty3
         Service: login; type tty; class user
           State: online
          CGroup: name=systemd:/user/root/c3
                  ├─ 2536 .../bin/login --
                  ├─10339 -bash
                  └─10355 w3m nixos.org
```

```bash
# loginctl terminate-session c3
```

> *"Since systemd keeps track of this, you can terminate a session in a way that ensures that all the session's processes are gone."*

**本指南补充的常用命令**：

| 命令 | 作用 | 场景 |
|---|---|---|
| `loginctl` | 列出会话 | 看谁登录了 |
| `loginctl list-users` | 列出用户 | — |
| `loginctl user-status <uid>` | 用户状态 | — |
| **`loginctl show-user <user> \| grep Linger`** | **检查 linger** | **★ 本指南坑清单 #44/#45 的诊断命令** |
| `loginctl enable-linger <user>` | 开启 linger（**NixOS 下用配置代替**） | — |
| `loginctl terminate-session <id>` | 彻底结束会话 | — |

> [!IMPORTANT]
> **`loginctl show-user hermes | grep Linger` 是本指南反复强调的诊断命令。**
>
> **为什么重要**：没有 `Linger=yes` 的用户，**它的 systemd 用户级服务在用户登出后会被全部杀掉**。对 agent 服务来说，这意味着：
> - SSH 断开后，agent 的定时任务**静默停止**
> - 而且**不报错** —— 这是最难查的一类问题
>
> **声明式写法**（NixOS）：
> ```nix
> { users.users.hermes.linger = true; }
> ```
> **注意**：`linger` 是 `mkDefault` 的，如果你用了 `createUser = false` 之类的写法，**可能被压掉** → 必须显式写 `linger = true;`（坑清单 #45）。

### 29.8 cgroup 与资源限制（官方 `sec-cgroups`）

**官方原文**：

> *"To keep track of the processes in a running system, systemd uses **control groups** (cgroups). A control group is a set of processes used to allocate resources such as **CPU, memory or I/O bandwidth**."*

```bash
$ systemd-cgls
├─user
│ └─eelco
│   └─c1
│     ├─ 2567 -:0
│     ├─ 2682 kdeinit4: kdeinit4 Running...
│     └─10851 sh -c less -R
└─system
  ├─httpd.service
  │ ├─2444 httpd -f /nix/store/.../httpd.conf -DNO_DETACH
  │ └─...
  ├─dhcpcd.service
  │ └─2376 dhcpcd --config /nix/store/.../dhcpcd.conf
```

```bash
$ systemd-cgls cpu
```

> **官方对 CPU cgroup 的说明（原文）**：*"By default, **every systemd service gets its own CPU cgroup**, while **all user sessions are in the top-level CPU cgroup**. This ensures, for instance, that a thousand run-away processes in the `httpd.service` cgroup cannot starve the CPU for one process in the `postgresql.service` cgroup. (By contrast, if they were in the same cgroup, then the PostgreSQL process would get 1/1001 of the cgroup's CPU time.)"*

**官方的资源限制示例**：

```nix
{ systemd.services.httpd.serviceConfig.CPUShares = 512; }
```

> *"By default, every cgroup has **1024 CPU shares**, so this will halve the CPU allocation of the `httpd.service` cgroup."*

```nix
{ systemd.services.httpd.serviceConfig.MemoryLimit = "512M"; }
```

> *"There also is a memory hierarchy that controls memory allocation limits; **by default, all processes are in the top-level cgroup, so any service or session can exhaust all available memory**."*

```bash
$ systemd-cgtop
```

> *"shows a continuously updated list of all cgroups with their CPU and memory usage."*

> [!IMPORTANT]
> **「by default, all processes are in the top-level cgroup, so any service or session can exhaust all available memory」—— 这一句解释了 NixOS 上「构建时 OOM」的根本原因。**
>
> **本指南 §22.x 提到的「Hermes 的 666 个 derivation 构建地狱」**：`nix-daemon` 是系统服务，**它有自己的 cgroup，但没设 `MemoryLimit`** → 构建可以吃光全部内存 → OOM killer 杀进程。
>
> **官方给的解法**（本指南推荐的加固）：
> ```nix
> {
>   systemd.services.nix-daemon.serviceConfig = {
>     MemoryMax = "24G";        # 或 MemoryLimit（旧名）
>     MemoryHigh = "20G";       # 软限制，超过会开始回收
>     IOWeight = 50;            # 降低 I/O 优先级（构建时不卡桌面）
>     Nice = 5;                 # 稍低 CPU 优先级
>   };
> }
> ```
> **`MemoryMax` 优于 `MemoryLimit`** —— 前者是 cgroup v2 的名字，后者是 v1 遗留别名。26.05 用的是 cgroup v2。
>
> **对你的实际价值**：**构建大型 flake 时桌面不会卡死，且 OOM 时只杀构建进程而不是整个桌面**。这是「游戏 + 编译」双用途机器上很实用的一条。

**游戏场景的一个额外建议（本指南补充）**：

```nix
# 让游戏进程有更高优先级（配合 §14.x 的 scx / ananicy）
{
  systemd.services."gamescope-session".serviceConfig = {
    Nice = -5;
    IOSchedulingClass = "realtime";
    IOSchedulingPriority = 0;
  };
}
```

> [!NOTE]
> **这一节与 §14.x（游戏性能榨干）的关系**：§14 讲的是**内核调度器层面**（scx / BORE / I/O scheduler）；本节讲的是**systemd cgroup 层面**。两者**互补**：
> - cgroup 管「谁分多少」
> - 调度器管「怎么调度」
>
> **优先级顺序**（本指南 §14.1 的结论仍然成立）：**Proton 选对 + mesa 够新 + 内存够 ≫ 换内核 ≫ 换调度器 ≫ I/O 调度器 ≫ cgroup 微调**。

### 29.9 关机、重启与 kexec

**官方原文**：

```bash
# shutdown          # 等价 systemctl poweroff
# reboot            # 等价 systemctl reboot
# systemctl kexec   # 用 kexec 快速重启，绕过 BIOS
# systemctl suspend   # 挂起到 RAM
# systemctl hibernate # 挂起到磁盘
```

> *"These commands can be run by **any user who is logged in locally**, i.e. on a virtual console or in X11; otherwise, the user is asked for authentication."*

> [!TIP]
> **`systemctl kexec` 值得单独说**：它**跳过 BIOS/UEFI 初始化**，直接把新内核加载进内存。
>
> **省多少时间**：通常**省掉 5–15 秒的固件初始化**（取决于主板）。对频繁重启（调内核参数、测配置）的场景很实用。
>
> **前提**：需要 `boot.kernelPackages` 里有 kexec 支持。NixOS 默认的 `systemd` 包已含 `systemd-kexec`（官方 unit），**通常开箱可用**。
>
> **验证**：`systemctl kexec` 直接跑；不行再看 `systemctl status kexec.service`。

**关于休眠（hibernate）的提醒（本指南补充）**：

| 功能 | 需要什么 | AMD 桌面常见问题 |
|---|---|---|
| `suspend`（挂起到 RAM） | 基本都能用 | — |
| `hibernate`（挂起到磁盘） | **swap ≥ RAM**，且内核参数要指向 swap | 内存大（32G+）时 swap 通常不够 |
| `hybrid-sleep` | 两者结合 | 同上 |

```nix
# 要休眠必须显式指定 resume 设备
{
  boot.kernelParams = [ "resume=UUID=<你的swap分区UUID>" ];
  boot.resumeDevice = "/dev/disk/by-uuid/<swap UUID>";
  swapDevices = [ { device = "/dev/disk/by-uuid/<swap UUID>"; } ];
}
```

> [!WARNING]
> **没有正确配置 `resume` 就 `systemctl hibernate` → 可能丢数据或唤醒失败。**
> **建议**：**桌面 AMD 机器只用 `suspend`**，不要折腾 hibernate。这也是绝大多数发行版的默认策略。

### 29.10 六个反模式

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | 自定义服务忘写 `wantedBy` | 服务**不自启**，且不报错 | `wantedBy = [ "multi-user.target" ];` |
| 2 | 用 `systemctl --user enable` | **GC 后符号链接死掉**，服务静默失效 | home-manager 的 `systemd.user.services` |
| 3 | 用 `systemctl enable` 管系统服务 | rebuild 覆盖 / GC 死链 | 写 `wantedBy` |
| 4 | 只看 `systemctl status` 不看 `journalctl -x` | 错过 systemd 给的修复建议 | `journalctl -x -u <unit>` |
| 5 | 不设 journal 大小上限 | 日志吃满磁盘 | `SystemMaxUse=500M` |
| 6 | agent 用户忘了 `linger` | 登出后用户服务**静默全停** | `users.users.<u>.linger = true;` + 用 `loginctl` 验证 |

> [!TIP]
> **本章的最小可用知识集**（如果只记三件事）：
> 1. **`systemctl status <unit>`** —— 看服务状态 + 最近日志
> 2. **`journalctl -b -p err`** —— 看本次开机的所有错误
> 3. **`systemctl list-units --failed`** —— 找静默失败的服务
>
> 这三条覆盖 90% 的日常诊断。

---

---

## 三十、系统状态、GC 与故障排查（官方 Part III 后半）

本章补的是官方手册 **Part III** 的 `ch-system-state`（含 `sec-nixos-state` / `sec-systemd-state`）、`sec-nix-gc`、`sect-nixos-gc-boot-entries`，以及整个 `ch-troubleshooting`（`sec-boot-problems` / `sec-maintenance-mode` / `sec-rollback` / `sec-nix-store-corruption` / `sec-nix-network-issues`）。

**这一章是「开不了机时的逃生手册」。** 本指南前二十五章从没系统讲过这个 —— 因为正常情况下你不需要。**但一旦需要，就是最需要的时候。**

### 30.1 哪些状态必须持久化（官方 `ch-system-state`）

**官方开场（原文）**：

> *"Normally — on systems with a persistent rootfs — system services can persist state to the filesystem without administrator intervention. However, **it is possible and not-uncommon to create impermanent systems, whose rootfs is either a tmpfs or reset during boot.** While NixOS itself supports this kind of configuration, special care needs to be taken."*

> [!IMPORTANT]
> **这一段是「不可变系统 / 无状态系统」的官方前提。** 即使你**不做**不可变系统，这张表也有用 —— **它告诉你「哪些目录丢了会出问题」**，也就是**备份时该备份什么**。

**官方的完整清单（逐项原文）**：

#### `/nix` —— 必须持久

> *"NixOS needs **the entirety of `/nix`** to be persistent, as it includes:"*
> - *"`/nix/store`, which contains all the system's executables, libraries, and supporting data;"*
> - *"`/nix/var/nix`, which contains: the Nix daemon's database; **roots whose transitive closure is preserved when garbage-collecting the Nix store**; system-wide and per-user profiles."*

#### `/boot` —— 必须持久

> *"`/boot` should also be persistent, as it contains:"*
> - *"the kernel and initrd which the bootloader loads,"*
> - *"**the bootloader's configuration, including the kernel's command-line which determines the store path to use as system environment.**"*

#### 用户与组

> - *"**`/var/lib/nixos`** should persist: it holds **state needed to generate stable uids and gids** for declaratively-managed users and groups, etc."*
> - *"**`users.mutableUsers` should be false, or the following files under `/etc` should all persist**: `passwd(5)` and `group(5)`, `shadow(5)` and `gshadow(5)`, `subuid(5)` and `subgid(5)`."*

> [!TIP]
> **这一条给出了 §28.3 那个 uid 漂移问题的**官方确认**。**
>
> **备份清单里必须包含 `/var/lib/nixos`** —— 它很小（几十 KB），但丢了会让 uid 重排。
>
> **更省事的做法**：按 §28.3 的建议**显式写 `uid`**，这样 `mutableUsers = true`（默认）时 `/etc/shadow` 也不用管。

#### systemd 需要的状态

> **`machine-id(5)`**：*"systemd uses per-machine identifier — `machine-id(5)` — which must be **unique and persistent**; otherwise, **the system journal may fail to list earlier boots**, etc."*
>
> *"systemd generates a random `machine-id(5)` during boot if it does not already exist, and persists it in `/etc/machine-id`. As such, it suffices to make that file persistent."*
>
> *"Alternatively, it is possible to generate a random `machine-id(5)`; while the specification allows for any hex-encoded 128b value, systemd itself uses UUIDv4, i.e. random UUIDs, and it is thus preferable to do so as well, in case some software assumes `machine-id(5)` to be a UUIDv4. Those can be generated with `uuidgen -r | tr -d -`... **NixOS' systemd maintainers discourage** [setting it via kernel command line]."

> **`/var/lib/systemd`**：*"systemd expects its state directory — `/var/lib/systemd` — to persist, for:"*
> - *"`systemd-random-seed(8)`, which loads a 256b "seed" into the kernel's RNG at boot time, and saves a fresh one during shutdown;"*
> - *"`systemd.timer(5)` with `Persistent=yes`, which are then run after boot if the timer would have triggered during the time the system was shut down;"*
> - *"`systemd-coredump(8)` to store core dumps there by default;"*
> - *"`systemd-timesyncd(8)`;"*
> - *"`systemd-backlight(8)` and `systemd-rfkill(8)` persist hardware-related state;"*
> - *"possibly other things, this list is not meant to be exhaustive."*
>
> *"In any case, **making `/var/lib/systemd` persistent is recommended**."*

> **`/var/log/journal/{machine-id}`**：*"if (locally) persisting the entire log is desired, it is recommended to make all of `/var/log/journal` persistent. If not, one can set `Storage=volatile` in `journald.conf(5)` (`services.journald.storage = "volatile";`), which disables journal persistence and causes it to be written to `/run/log/journal`."*

**汇总成一张「备份 / 持久化清单」**（本指南整理）：

| 路径 | 必须持久 | 丢了会怎样 | 大小 |
|---|---|---|---|
| `/nix` | ✅ **必须** | **系统没了** | 数十 GB |
| `/boot` | ✅ **必须** | 开不了机 | 数百 MB |
| `/var/lib/nixos` | ✅ 推荐 | **uid/gid 重排** → 文件属主乱 | KB 级 |
| `/etc/machine-id` | ✅ 推荐 | journal 无法列出历史启动；某些软件异常 | 33 B |
| `/var/lib/systemd` | ✅ 推荐 | 定时器 `Persistent=yes` 失效、随机种子重置、亮度/rfkill 状态丢失 | MB 级 |
| `/etc/{passwd,group,shadow,gshadow,subuid,subgid}` | ⚠️ 仅当 `mutableUsers = true` | 密码丢失、用户残留 | KB 级 |
| `/var/log/journal` | ⚠️ 可选 | 历史日志丢失 | 百 MB |

> [!DANGER]
> **`systemd-random-seed` 那一条值得单独强调**：它保存的是**内核随机数生成器的种子**。
>
> **如果 `/var/lib/systemd/random-seed` 丢失或每次启动都一样** → **早期启动阶段的随机数质量下降** → 影响 **TLS 密钥生成、磁盘加密密钥、SSH host key** 等。
>
> **对普通桌面的实际影响**：小（现代内核有其他熵源）。**但对「无盘工作站」或「克隆出来的多台虚拟机」影响大**（所有机器拿到同一个种子）。
>
> **结论**：如果你做不可变系统，**`/var/lib/systemd` 必须持久化**。

### 30.2 journald 的持久化开关

官方在 §30.1 已给出。**本指南补充配置写法**：

```nix
{
  # 持久化（默认）——日志写 /var/log/journal
  services.journald.storage = "persistent";   # 显式写法

  # 或者：只留内存（省磁盘 / 隐私）
  # services.journald.storage = "volatile";   # 写 /run/log/journal，重启即失

  # 加一个大小上限（强烈建议，配合 §30.3）
  services.journald.extraConfig = ''
    SystemMaxUse=500M
    SystemMaxFileSize=50M
    MaxRetentionSec=1month
  '';
}
```

| `storage` 取值 | 日志位置 | 重启后 | 适合 |
|---|---|---|---|
| `persistent` | `/var/log/journal` | 保留 | **默认，桌面推荐** |
| `volatile` | `/run/log/journal` | 丢失 | 无盘 / 隐私敏感 |
| `auto` | 有 `/var/log/journal` 就持久 | 视情况 | — |
| `none` | 不记录 | — | 极简 |

### 30.3 清理 Nix store：GC（官方 `sec-nix-gc`）

**官方原文**：

> *"Nix has a purely functional model, meaning that **packages are never upgraded in place**. Instead new versions of packages end up in a different location in the Nix store (`/nix/store`). **You should periodically run Nix's garbage collector to remove old, unreferenced packages.**"*

```bash
$ nix-collect-garbage
```

> *"Alternatively, you can use a systemd unit that does the same in the background: `# systemctl start nix-gc.service`"*

```nix
{
  nix.gc.automatic = true;
  nix.gc.dates = "03:15";
}
```

**官方关于「保留回滚能力」的关键说明（原文）**：

> *"**The commands above do not remove garbage collector roots, such as old system configurations. Thus they do not remove the ability to roll back to previous configurations.** The following command deletes old roots, **removing the ability to roll back to them**:"*

```bash
$ nix-collect-garbage -d
```

```bash
$ nix-env -p /nix/var/nix/profiles/per-user/eelco/profile --delete-generations old
```

> *"Note that NixOS system configurations are stored in the profile `/nix/var/nix/profiles/system`."*

**官方的「省 40% 磁盘」技巧（原文）**：

> *"Another way to reclaim disk space (**often as much as 40% of the size of the Nix store**) is to run Nix's **store optimiser**, which seeks out identical files in the store and replaces them with **hard links** to a single copy."*

```bash
$ nix-store --optimise
```

> *"Since this command needs to read the entire Nix store, it can take quite a while to finish."*

> [!IMPORTANT]
> **`nix-collect-garbage` 和 `nix-collect-garbage -d` 的区别是本章最实用的一条。**
>
> | 命令 | 删什么 | 还能回滚吗 |
> |---|---|---|
> | `nix-collect-garbage` | 无人引用的 store path | ✅ **能**（旧 generation 还在） |
> | `nix-collect-garbage -d` | 上述 + **旧 generation 本身** | ❌ **不能回滚到已删的 generation** |
> | `nix.gc.automatic = true` | 等价第一种 | ✅ 能 |
>
> **本指南的推荐组合**（桌面 + 游戏，磁盘紧）：
> ```nix
> {
>   # 自动 GC：每周清一次，保留最近 7 天
>   nix.gc = {
>     automatic = true;
>     dates = "weekly";
>     options = "--delete-older-than 7d";   # ← 注意：这个选项会删旧 generation
>   };
>
>   # 同时限制 systemd-boot 菜单里的启动项数量
>   boot.loader.systemd-boot.configurationLimit = 10;   # 见 §30.5
>
>   # 开启 store 去重（省 40%）
>   nix.settings.auto-optimise-store = true;
> }
> ```
>
> **⚠️ `--delete-older-than 7d` 会删掉 7 天前的 generation** —— 这意味着**你不能回滚到一周前的配置**。**权衡**：
> - 磁盘紧张 → 用 `7d`
> - 想要「随时回滚到任意历史」 → 用 `30d` 或干脆不加这个选项
>
> **本指南 §11.4 给的配置与此一致**，这里补上了「为什么」。

> [!TIP]
> **`nix.settings.auto-optimise-store = true` 是「一次性设置，永久省 40%」的选项。**
>
> 官方原文说手动跑 `nix-store --optimise` 能省 *"as much as 40%"*。**开启 `auto-optimise-store` 之后，Nix 会在每次添加新路径时自动去重** —— 不用手动跑，也不用等那「quite a while」。
>
> **代价**：每次构建/下载时多一点 CPU（做 hard link）。**对 SSD 完全值得。**

### 30.4 手动 GC 的完整操作清单

```bash
# ── 1. 先看占了多少 ──
du -sh /nix/store
nix-store --gc --print-dead | wc -l        # 有多少「死」路径
journalctl --disk-usage                     # 日志占多少

# ── 2. 看有哪些 generation（能回滚到哪些）──
nix-env --list-generations -p /nix/var/nix/profiles/system
ls -l /nix/var/nix/profiles/system-*-link | tail -20

# ── 3. 保守 GC（保留回滚能力）──
sudo nix-collect-garbage

# ── 4. 删旧 generation（⚠️ 失去对应回滚能力）──
sudo nix-collect-garbage --delete-older-than 30d

# ── 5. 全清（⚠️⚠️ 只能回滚到当前 generation）──
sudo nix-collect-garbage -d

# ── 6. 去重 ──
sudo nix-store --optimise
```

> [!DANGER]
> **`nix-collect-garbage -d` 之前，先确认你现在这个 generation 是好的。**
>
> **为什么**：`-d` 会删掉所有旧 generation。如果当前配置有隐藏问题（比如某个服务起不来、某个硬件不工作），你**没有退路**。
>
> **安全流程**：
> 1. 先 `sudo nixos-rebuild switch`
> 2. **重启一次**，确认系统正常
> 3. 再跑 `-d`
>
> **本指南 §11.4 强调过这一条，这里再强调一次** —— 因为这是少数**不可逆**的操作之一。

### 30.5 `/boot` 分区爆满（官方 `sect-nixos-gc-boot-entries`）

**官方原文（整节只有一句，但很重要）**：

> *"If your `/boot` partition runs out of space, after clearing old profiles you must rebuild your system with `nixos-rebuild boot` or `nixos-rebuild switch` to update the `/boot` partition and clear space."*

> [!IMPORTANT]
> **这句话包含一个反直觉的顺序**：
>
> **❌ 错的顺序**：`/boot` 满了 → 删旧 generation → 好了
> **✅ 对的顺序**：`/boot` 满了 → 删旧 generation → **再跑一次 `nixos-rebuild boot/switch`**
>
> **为什么**：删 generation 只是**删掉了 `/nix/var/nix/profiles` 里的符号链接**。**`/boot` 里那些内核和 initrd 文件还在** —— 它们是**由 `nixos-rebuild` 生成 bootloader 配置时清理的**。
>
> **所以**：不重新 rebuild，`/boot` 不会变小。

**预防：限制启动项数量（本指南推荐）**：

```nix
{
  boot.loader.systemd-boot.configurationLimit = 10;
}
```

> **本指南在 §11.5 提到过这个选项**（默认 `null` = 不限制）。**这里补上它和 `/boot` 大小的关系**：
>
> | 每个 generation 占 `/boot` | 数量 | 总占用 |
> |---|---|---|
> | 内核 + initrd ≈ 60–120 MB | 10 个 | 0.6–1.2 GB |
> | 同上 | 30 个 | 1.8–3.6 GB |
>
> **典型的 ESP 是 512 MB–1 GB** —— 所以**不限制的话，很快就会满**。
>
> **`configurationLimit = 10` 是合理的默认**（保留最近 10 个可回滚点）。**如果你 `/boot` 给了 2 GB，可以设 20。**

**诊断命令**：

```bash
df -h /boot
ls -la /boot/loader/entries/ | wc -l     # 有多少个启动项
bootctl list                              # 列出所有启动项
sudo bootctl cleanup                      # 清理无主文件
```

### 30.6 启动问题：内核参数全集（官方 `sec-boot-problems`）

**官方开场（原文）**：

> *"If NixOS fails to boot, there are a number of **kernel command line parameters** that may help you to identify or fix the issue. You can add these parameters in the GRUB boot menu by pressing "e" to modify the selected boot entry and editing the line starting with `linux`."*

> *"`kernel-command-line(7)` documents the kernel parameters accepted by systemd. Those include many that are helpful for debugging boot issues, such as `systemd.debug_shell` and `rescue`. Some also have `rd.`-prefixed variants that apply to stage 1."*

**官方的通用提示**：

> *"If no login prompts or X11 login screens appear (e.g. due to hanging dependencies), you can press **`Alt+ArrowUp`**. If you're lucky, this will start `rescue.target`... (Also note that since **most units have a 90-second timeout** before systemd gives up on them, the agetty login prompts should appear eventually unless something is very wrong.)"*

**`live.nixos.passwd=password`**：

> *"Set the password for the `nixos` live user. This can be used for **SSH access if there are issues using the terminal**."*

**官方的 scripted stage 1 参数表（原文，含 systemd stage 1 的替代）**：

> **⚠️ 官方警告**：*"The scripted implementation of stage 1 is disabled by default and **deprecated**. These parameters have no effect, unless systemd stage 1 is explicitly disabled with `boot.initrd.systemd.enable = false;`."*

| 参数 | 官方描述 | systemd stage 1 替代 |
|---|---|---|
| **`boot.shell_on_fail`** | *"Allows the user to start a root shell if something goes wrong in stage 1... This is disabled by default because **there is no authentication for the root shell**."* | `SYSTEMD_SULOGIN_FORCE=1`（rescue 模式）或 `rd.systemd.debug_shell`（tty9） |
| **`boot.debug1`** | *"Start an interactive shell in stage 1 **before anything useful has been done**. That is, **no modules have been loaded and no file systems have been mounted**, except for `/proc` and `/sys`."* | `rd.systemd.break=pre-udev` |
| **`boot.debug1devices`** | *"Like `boot.debug1`, but runs stage1 until **kernel modules are loaded and device nodes are created**. This may help with e.g. making the keyboard work."* | `rd.systemd.break=pre-mount` |
| **`boot.debug1mounts`** | *"Like `boot.debug1` or `boot.debug1devices`, but runs stage1 until **all filesystems that are mounted during initrd are mounted**... **as a motivating example, this could be useful if you've forgotten to set `neededForBoot` on a file system**."* | `rd.systemd.break=pre-switch-root` |
| **`boot.trace`** | *"Print every shell command executed by the stage 1 and 2 boot scripts."* | `rd.systemd.log_level=debug` |

> **官方的一个行为细节**：*"for `boot.shell_on_fail`, `boot.debug1`, `boot.debug1devices`, and `boot.debug1mounts`, **if you did not select "start the new shell as pid 1", and you exit from the new shell, boot will proceed normally from the point where it failed**, as if you'd chosen "ignore the error and continue"."*

> [!IMPORTANT]
> **这张表是「开不了机」时最有价值的工具，但有一个前提必须先搞清楚：**
>
> **26.05 的默认 stage 1 是哪个？**
>
> 官方说 scripted stage 1 *"is disabled by default and deprecated"* —— 这句话**有歧义**。结合上下文与 `sec-luks-file-systems`（其中 `boot.initrd.systemd.enable = true` 是**显式开启**才有的），**准确理解是**：
>
> - **26.05 默认仍是 scripted stage 1**（所以 `boot.debug1` 这些参数**默认有效**）
> - 官方说「disabled by default」指的是**未来方向**，以及「如果**你开了** systemd stage 1，这些参数就失效了」
>
> **实操建议**：**先用 `boot.debug1mounts` 试**（如果无效，说明你的系统是 systemd stage 1，改用 `rd.systemd.break=pre-switch-root`）。**两条都试一遍，成本很低。**

**在启动菜单里临时加参数的步骤（GRUB 与 systemd-boot 通用）**：

```
1. 开机时进入 bootloader 菜单
2. 选中要启动的 generation
3. GRUB: 按 e  →  找到 linux 开头那行  →  行尾加参数  →  Ctrl+X 启动
   systemd-boot: 按 e  →  同一行  →  加参数  →  Enter 启动
4. ⚠️ 这只对本次启动有效，重启即失效（这是好事——它是「安全实验」）
```

> [!TIP]
> **本指南给你的「开机失败三连」**：
>
> **第 1 步：能不能进 bootloader 菜单？**
> - **能** → 选**上一个 generation** 启动（§30.8）。**大概率立刻恢复。**
> - **不能** → 硬件/固件问题，或 bootloader 损坏 → 用 U 盘启动（§30.7）
>
> **第 2 步：旧 generation 也起不来？**
> → 加 `boot.debug1mounts`（或 `rd.systemd.break=pre-switch-root`）看卡在哪
> → 最常见原因是**改坏了 `fileSystems`**（§27.1）
>
> **第 3 步：什么都不行？**
> → `systemctl rescue`（§30.7）或 U 盘 chroot

### 30.7 维护模式（官方 `sec-maintenance-mode`）

**官方原文**：

> *"You can enter rescue mode by running: `# systemctl rescue`. This will eventually give you a **single-user root shell**. Systemd will **stop (almost) all system services**. To get out of maintenance mode, just exit from the rescue shell."*

**本指南补充的「进不去系统时怎么用」**：

| 场景 | 做法 |
|---|---|
| 系统能启动但图形界面坏了 | `Ctrl+Alt+F3` 切 TTY → 登录 → `systemctl rescue` |
| 系统能启动但登录不上 | 启动参数加 `systemd.unit=rescue.target` |
| 完全进不去 | 用 NixOS U 盘启动 → `nixos-enter --root /mnt`（见下） |

**U 盘救援 + chroot 修复（本指南补充）**：

```bash
# 从 NixOS U 盘启动后：
# 1. 找到根分区
lsblk -f

# 2. 如果是 LUKS，先解锁
sudo cryptsetup luksOpen /dev/nvme0n1p2 crypted

# 3. 挂载
sudo mount /dev/mapper/crypted /mnt
sudo mount /dev/nvme0n1p1 /mnt/boot        # ESP

# 4. 进入 chroot（NixOS 官方提供的工具）
sudo nixos-enter --root /mnt

# 5. 现在可以修配置了
nano /etc/nixos/configuration.nix
nixos-rebuild switch

# 6. 退出并重启
exit
sudo umount -R /mnt
sudo reboot
```

> [!TIP]
> **`nixos-enter` 是 NixOS 特有的救援工具**（其他发行版没有对应物）。它比手写 `chroot` 好得多：
> - 自动绑定 `/proc` / `/sys` / `/dev` / `/nix`
> - 自动设置环境
> - 支持 `--root /mnt` 和 `--system <path>`（进入指定 generation）
>
> **`--system` 参数特别有用**：你可以 chroot 进**一个旧的 generation**，从里面修复：
> ```bash
> sudo nixos-enter --root /mnt --system /nix/var/nix/profiles/system-42-link
> ```

### 30.8 回滚（官方 `sec-rollback`）

**官方给了三种方式（原文）**：

**方式 1：从 bootloader 菜单选旧配置**

> *"First, the GRUB boot manager allows you to boot into **any previous configuration that hasn't been garbage-collected**. These configurations can be found under the GRUB submenu "**NixOS - All configurations**". This is especially useful **if the new configuration fails to boot**."*

```bash
# /run/current-system/bin/switch-to-configuration boot
```

> *"After the system has booted, you can make the selected configuration **the default for subsequent boots**"*

**方式 2：在运行中的系统里回滚**

```bash
# nixos-rebuild switch --rollback
```

> *"This is equivalent to running: `# /nix/var/nix/profiles/system-N-link/bin/switch-to-configuration switch` where N is the number of the NixOS system configuration."*

**方式 3：列出所有可用配置**

```bash
$ ls -l /nix/var/nix/profiles/system-*-link
...
lrwxrwxrwx 1 root root 78 Aug 12 13:54 /nix/var/nix/profiles/system-268-link -> /nix/store/202b...-nixos-13.07pre4932_5a676e4-4be1055
```

> [!IMPORTANT]
> **systemd-boot 用户的菜单名不是「NixOS - All configurations」** —— 那是 GRUB 的子菜单名。
>
> **systemd-boot 的行为**：所有 generation **平铺在主菜单里**，名字形如：
> ```
> NixOS 26.05 (Generation 42) (Linux 6.18.3)
> NixOS 26.05 (Generation 41) (Linux 6.18.2)
> ...
> ```
> **数量由 `boot.loader.systemd-boot.configurationLimit` 决定**（§30.5）。**默认 `null` = 全部显示** —— 这既是「随时能回滚」的优点，也是 `/boot` 爆满的原因。

> [!TIP]
> **「回滚」与「切换 generation」的区别**（本指南补充）：
>
> | 操作 | 效果 | 适合 |
> |---|---|---|
> | `nixos-rebuild switch --rollback` | 切到**上一个** generation | 刚改坏了 |
> | 启动菜单选任意 generation | 切到**任意**保留的 generation | 回滚到很久以前 |
> | `/run/current-system/bin/switch-to-configuration boot` | 把**当前运行的**设为默认启动项 | 从菜单启动旧版后想固化 |
>
> **第三条容易被忽略**：从菜单启动旧 generation 后，**下次重启又会回到新版**（因为默认项没变）。要固化必须跑那条命令。

### 30.9 Nix store 损坏（官方 `sec-nix-store-corruption`）

**官方原文**：

> *"After a system crash, it's possible for files in the Nix store to become corrupted. (For instance, **the Ext4 file system has the tendency to replace un-synced files with zero bytes**.) NixOS tries hard to prevent this from happening: it performs a **sync before switching to a new configuration**, and **Nix's database is fully transactional**. If corruption still occurs, you may be able to fix it automatically."*

```bash
# nixos-rebuild switch --repair
```

> *"This will cause Nix to **check every path in the closure**, and if its **cryptographic hash differs from the hash recorded in Nix's database**, the path is rebuilt or redownloaded."*

```bash
# nix-store --verify --check-contents --repair
```

> *"**Any corrupt paths will be redownloaded if they're available in a binary cache; otherwise, they cannot be repaired.**"*

> [!IMPORTANT]
> **最后那句是重点：`--repair` 只能修「能从缓存重新下载」的路径。**
>
> **修不了的**：
> - 你自己构建的（不在 cache.nixos.org 里）
> - 你 override 过的包
> - 本地 flake 的产物
>
> **怎么办**：删掉再重建。
> ```bash
> nix-store --delete /nix/store/<损坏路径>
> nixos-rebuild switch    # 重新构建
> ```

> [!WARNING]
> **为什么「Ext4 会把未同步的文件变成零字节」值得注意**：
>
> 官方把它当成 store 损坏的**主要原因**。**这解释了为什么 NixOS 在 switch 前会 sync** —— 官方原文：*"it performs a sync before switching to a new configuration"*。
>
> **对你的实际影响**：
> - **正常使用几乎不会碰到**（NixOS 的 sync + 事务性数据库已覆盖大部分情况）
> - **突然断电 / 强制关机时风险上升**
>
> **建议**：**不要用「长按电源键」关机**。用 `systemctl poweroff` 或 `shutdown`。**这对 SSD 尤其重要**。

### 30.10 网络问题：二进制缓存（官方 `sec-nix-network-issues`）

**官方原文**：

> *"Nix uses a so-called **binary cache** to optimise building a package from source into downloading it as a pre-built binary... **The default binary cache is `https://cache.nixos.org/`.** If this cache is unreachable, **Nix operations may take a long time due to HTTP connection timeouts**."*

```bash
# nixos-rebuild switch --option use-binary-caches false
```

> *"If you have an alternative binary cache at your disposal, you can use it instead:"*

```bash
# nixos-rebuild switch --option binary-caches http://my-cache.example.org/
```

> [!IMPORTANT]
> **对国内用户，这一节特别重要。** 官方只讲了「缓存不可达会很慢」，**没讲国内的具体情况**。
>
> **本指南第四章已给国内镜像源配置**（`nix.settings.substituters` + `trusted-public-keys`）。**这里补充官方这两条命令的用途**：
>
> | 场景 | 命令 |
> |---|---|
> | 怀疑缓存慢导致卡住 | `nixos-rebuild switch --option use-binary-caches false`（纯本地构建，不试缓存） |
> | 临时换缓存 | `nixos-rebuild switch --option binary-caches https://mirror.example.org/` |
> | **永久配置镜像** | 写 `nix.settings.substituters`（见 §4.8） |
>
> **一个诊断技巧**：`nixos-rebuild` 卡在 `copying path ...` 很久 → **大概率是缓存在超时**。加 `--option use-binary-caches false` 或换成国内镜像立刻能验证。

**本指南补充的网络诊断命令**：

```bash
# 测缓存可达性
curl -sI https://cache.nixos.org/nix-cache-info

# 看当前配置的 substituters
nix show-config | grep -E 'substituters|trusted-public-keys'

# 看 Nix 的网络日志
journalctl -u nix-daemon -f
```

### 30.11 七个反模式

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | 直接 `nix-collect-garbage -d` | **失去所有回滚点**，不可逆 | 先重启验证，再删；或用 `--delete-older-than 30d` |
| 2 | `/boot` 满了只删 generation 不 rebuild | **`/boot` 不会变小** | 删完必须 `nixos-rebuild boot` |
| 3 | 不设 `configurationLimit` | `/boot` 迅速爆满 | `= 10`（或按 ESP 大小调） |
| 4 | 忘了 `/var/lib/nixos` 备份 | 重装后 **uid 重排** | 显式写 `uid`，或备份该目录 |
| 5 | 长按电源键关机 | store 可能损坏（Ext4 零字节） | `systemctl poweroff` |
| 6 | 不设 journal 上限 | 日志吃满磁盘 | `SystemMaxUse=500M` |
| 7 | 缓存卡住时干等 | 以为系统挂了 | `--option use-binary-caches false` 验证 |

> [!TIP]
> **本章的最小可用知识集**（如果只记三件事）：
> 1. **开不了机 → 进 bootloader 菜单选旧 generation**（90% 的问题这样解决）
> 2. **`nix-collect-garbage -d` 是不可逆的** —— 用之前先重启验证
> 3. **`/boot` 满了要「删 generation + rebuild」两步**
>
> 这三条覆盖「最坏情况」的 90%。

---

---

## 三十一、容器管理：NixOS 原生容器（官方 `ch-containers`）

本章补的是官方手册 **Part III** 的 `ch-containers`、`sec-imperative-containers`、`sec-declarative-containers`、`sec-container-networking`。

**先说清楚一件事：NixOS 原生容器和你在本指南 §23.7 / §25.5 见到的 Distrobox 不是同一个东西。**

| | **NixOS 原生容器**（本章） | **Distrobox / Podman**（本指南 §23.7、§25.5） |
|---|---|---|
| 里面跑什么 | **另一个 NixOS** | 任意发行版（Ubuntu/Fedora/Arch） |
| 共享 Nix store | ✅ 共享（所以创建极快） | ❌ 独立镜像 |
| 配置方式 | 声明式（`containers.<name>`） | 命令式 |
| 主要用途 | **跑隔离的服务** | **跑非 Nix 的软件**（解决依赖问题） |
| 隔离强度 | ⚠️ **不完全隔离**（官方警告） | 标准容器隔离 |

### 31.1 NixOS 原生容器的定位

**官方原文**：

> *"NixOS allows you to easily run **other NixOS instances as containers**. Containers are a **light-weight approach to virtualisation** that runs software in the container **at the same speed as in the host system**. NixOS containers **share the Nix store of the host, making container creation very efficient**."*

**官方警告（原文，逐字）**：

> ⚠️ *"Currently, NixOS containers are **not perfectly isolated from the host system**. This means that **a user with root access to the container can do things that affect the host**. So you should **not give container root access to untrusted users**."*

> [!DANGER]
> **这条警告是本章最重要的内容，必须放在最前面。**
>
> **「root in container ≠ root on host」是 Docker 的常见说法，但官方明确说 NixOS 容器不满足这一点。**
>
> **具体风险**：容器里的 root 可以（在某些配置下）影响宿主 —— 因为容器**共享 Nix store**，且没有完整的用户命名空间隔离。
>
> **结论**：
> - ✅ **可以**用来跑「你自己写的、你自己信任的服务」（如数据库、Web 服务）
> - ❌ **不要**用来跑「不可信的第三方代码」
> - ❌ **不要**给不受信任的人容器 root
>
> **对比**：Docker/Podman 的默认配置隔离更好。**要强隔离，用 Podman（本指南 §23.7）或 microVM（`microvm.nix`，非官方）。**

**官方对两种创建方式的说明（原文）**：

> *"NixOS containers can be created in two ways: **imperatively**, using the command `nixos-container`, and **declaratively**, by specifying them in your `configuration.nix`. **The declarative approach implies that containers get upgraded along with your host system when you run `nixos-rebuild`, which is often not what you want.** By contrast, in the imperative approach, containers are configured and updated independently from the host system."*

> [!IMPORTANT]
> **「declarative 会跟着宿主一起升级」这一点是关键权衡。**
>
> | | 声明式 | 命令式 |
> |---|---|---|
> | 配置在哪 | `configuration.nix` | `/etc/nixos-containers/foo.conf` |
> | 升级时机 | **跟着 `nixos-rebuild`** | 独立（`nixos-container update`） |
> | 版本一致性 | ✅ 容器与宿主同版本 | ⚠️ 可能不一致 |
> | 适合 | **想统一管理**（如自用服务） | **想独立升级**（如跑旧版数据库） |
>
> **本指南的建议**：**桌面用户基本不需要 NixOS 原生容器。** 你的两个真实需求是：
> 1. **跑非 Nix 软件** → 用 **Distrobox**（§23.7）
> 2. **跑 Android 应用** → 用 **Waydroid**（§23.12）
>
> **什么时候才需要本章**：你想在一台机器上跑**多个隔离的 NixOS 服务**（比如自建 Git 服务 + 数据库 + 反向代理，各自独立升级）。**那是服务器场景。**

### 31.2 命令式管理：`nixos-container` 全集

**官方原文（前置条件）**：

> *"Be aware that **container management is currently only possible as root**, and that you need to enable `boot.enableContainers` explicitly."*

```nix
{ boot.enableContainers = true; }
```

> [!WARNING]
> **`boot.enableContainers = true` 是必须的**，否则 `nixos-container` 命令会报错。**这是官方明确要求的前置条件**，不是可选项。

**官方给的完整命令序列（逐字照抄）**：

```bash
# ── 创建 ──
# nixos-container create foo

# ── 创建时就带配置 ──
# nixos-container create foo --config '
  services.openssh.enable = true;
  users.users.root.openssh.authorizedKeys.keys = ["ssh-dss AAAAB3N…"];
'

# ── 指定网络地址 ──
# nixos-container create test --config-file test-container.nix \
    --local-address 10.235.1.2 --host-address 10.235.1.1

# ── 启动（create 不会自动启动）──
# nixos-container start foo

# ── 看状态 ──
# systemctl status container@foo

# ── 登录 ──
# nixos-container root-login foo
[root@foo:~]#

# nixos-container login foo
foo login: alice
Password: ***

# ── 在容器里跑命令 ──
# nixos-container run foo -- uname -a
Linux foo 3.4.82 #1-NixOS SMP Thu Mar 20 14:44:05 UTC 2014 x86_64 GNU/Linux

# ── 更新配置 ──
# nixos-container update foo
# nixos-container update foo --config '
  services.httpd.enable = true;
  services.httpd.adminAddr = "foo@example.org";
  networking.firewall.allowedTCPPorts = [ 80 ];
'

# ── 停/启 ──
# nixos-container stop foo
# nixos-container start foo

# ── 销毁（含文件系统）──
# nixos-container destroy foo
```

**官方给的路径信息（原文）**：

> *"This creates the container's root directory in **`/var/lib/nixos-containers/foo`** and a small configuration file in **`/etc/nixos-containers/foo.conf`**. It also builds the container's initial system configuration and stores it in **`/nix/var/nix/profiles/per-container/foo/system`**."*

> *"By default the next free address in the **`10.233.0.0/16`** subnet will be chosen as container IP."*

> *"On the host, the container runs within a systemd unit called **`container@container-name.service`**."*

> *"Note that **only root on the host** can do [`root-login`] (since there is no authentication)."*

**官方的配置修改提醒（原文）**：

> *"First, on the host, you can edit `/var/lib/nixos-containers/foo/etc/nixos/configuration.nix`, and run `nixos-container update foo`... **However, note that this will overwrite the container's `/etc/nixos/configuration.nix`.**"*

> *"Alternatively, you can change the configuration from within the container itself by running `nixos-rebuild switch` inside the container. **Note that the container by default does not have a copy of the NixOS channel, so you should run `nix-channel --update` first.**"*

### 31.3 声明式容器（官方 `sec-declarative-containers`）

**官方原文**：

> *"You can also specify containers and their configuration in the host's `configuration.nix`."*

```nix
{
  containers.database = {
    config =
      { config, pkgs, ... }:
      {
        services.postgresql.enable = true;
        services.postgresql.package = pkgs.postgresql_14;
      };
  };
}
```

> *"If you run `nixos-rebuild switch`, the container will be built. **If the container was already running, it will be updated in place, without rebooting.** The container can be configured to start automatically by setting `containers.database.autoStart = true` in its configuration."*

**官方给的网络配置**：

```nix
{
  containers.database = {
    privateNetwork = true;
    hostAddress = "192.168.100.10";
    localAddress = "192.168.100.11";
  };
}
```

> *"This gives the container a **private virtual Ethernet interface** with IP address `192.168.100.11`, which is hooked up to a virtual Ethernet interface on the host with IP address `192.168.100.10`."*

**官方的删除说明（原文）**：

> *"To disable the container, just remove it from `configuration.nix` and run `nixos-rebuild switch`. **Note that this will not delete the root directory of the container in `/var/lib/nixos-containers`.** Containers can be destroyed using the imperative method: `nixos-container destroy foo`."*

> *"Declarative containers can be started and stopped using the corresponding systemd service, e.g. `systemctl start container@database`."*

> [!IMPORTANT]
> **「声明式删掉容器 ≠ 数据被删」是一个重要细节。**
>
> **行为**：从 `configuration.nix` 里删掉 `containers.database` → rebuild → 容器**停止并从 systemd 里消失** → 但 **`/var/lib/nixos-containers/database` 还在**（占着磁盘）。
>
> **正确清理步骤**：
> 1. 从配置里删掉
> 2. `nixos-rebuild switch`
> 3. **`sudo nixos-container destroy database`**（或在确认不要数据后手动 `rm -rf`）
>
> **这和 NixOS 的一贯哲学一致**：**声明式管理「配置」，不管理「数据」。** 数据删除永远是显式的。

**本指南补充的「跑一个自用服务」完整模板**：

```nix
{ config, pkgs, ... }:
{
  # 前置条件
  boot.enableContainers = true;

  # 声明式容器
  containers.myservice = {
    autoStart = true;                 # 开机自启
    privateNetwork = true;            # 独立网络命名空间
    hostAddress = "10.100.0.1";
    localAddress = "10.100.0.2";

    # 端口转发（宿主 8080 → 容器 80）
    forwardPorts = [
      { containerPort = 80; hostPort = 8080; protocol = "tcp"; }
    ];

    config = { config, pkgs, ... }: {
      services.nginx = {
        enable = true;
        virtualHosts."localhost".root = "/var/www";
      };
      system.stateVersion = "26.05";   # ⚠️ 容器内也要写
    };
  };

  # 宿主侧：NAT 让容器能出网（见 §31.4）
  networking.nat = {
    enable = true;
    internalInterfaces = [ "ve-+" ];
    externalInterface = "enp4s0";      # ← 换成你的有线网卡名
  };
}
```

> [!WARNING]
> **`system.stateVersion` 在容器配置里也必须写。** 这是最容易漏的一条 —— 漏了会得到「`system.stateVersion` is not set」的求值警告/错误。

### 31.4 容器网络与 NAT（官方 `sec-container-networking`）

**官方原文**：

> *"When you create a container using `nixos-container create`, it gets its own private IPv4 address in the range **`10.233.0.0/16`**."*

```bash
# nixos-container show-ip foo
10.233.4.2

$ ping -c1 10.233.4.2
64 bytes from 10.233.4.2: icmp_seq=1 ttl=64 time=0.106 ms
```

> *"Networking is implemented using **a pair of virtual Ethernet devices**. The network interface **in the container is called `eth0`**, while **the matching interface in the host is called `ve-container-name`** (e.g., `ve-foo`)."*

> *"The container has its **own network namespace** and the **`CAP_NET_ADMIN` capability**, so it can perform arbitrary network configuration such as setting up firewall rules, **without affecting or having access to the host's network**."*

**官方的 NAT 配置（原文）**：

> *"**By default, containers cannot talk to the outside network.** If you want that, you should set up Network Address Translation (NAT) rules on the host to rewrite container traffic to use your external IP address."*

```nix
{
  networking.nat.enable = true;
  networking.nat.internalInterfaces = [ "ve-+" ];
  networking.nat.externalInterface = "eth0";
}
```

> *"where `eth0` should be replaced with the desired external interface. **Note that `ve-+` is a wildcard that matches all container interfaces.**"*

**官方的 NetworkManager 提醒（原文）**：

```nix
{ networking.networkmanager.unmanaged = [ "interface-name:ve-*" ]; }
```

> *"If you are using Network Manager, you need to explicitly prevent it from managing container interfaces... You may need to restart your system for the changes to take effect."*

> [!IMPORTANT]
> **`networking.networkmanager.unmanaged = [ "interface-name:ve-*" ];` 这一条对你特别重要** —— 因为你按本指南第四章用的是 **NetworkManager**。
>
> **不加会怎样**：NetworkManager 会尝试「管理」`ve-foo` 这些虚拟接口，可能给它们乱配 IP / 路由 → **容器网络时通时不通**。
>
> **注意通配符写法是 `interface-name:ve-*`**（NetworkManager 的语法），不是 `ve-+`（那是 nftables/iptables 的语法）。**两者不要混用。**

**本指南补充的诊断命令**：

```bash
# 看容器 IP
sudo nixos-container show-ip foo

# 看虚拟接口
ip link show type veth
ip -br addr | grep ve-

# 从宿主 ping 容器
ping -c1 $(sudo nixos-container show-ip foo)

# 从容器 ping 外网（需先配 NAT）
sudo nixos-container run foo -- ping -c1 1.1.1.1

# 看 NAT 规则
sudo nft list ruleset | grep -A5 nat
```

### 31.5 与 Distrobox / Waydroid / Podman 的分工

**把本指南散落在各章的「容器类方案」汇总成一张表**：

| 方案 | 里面跑什么 | 隔离强度 | 解决什么问题 | 本指南位置 |
|---|---|---|---|---|
| **NixOS 原生容器** | 另一个 NixOS | ⚠️ **不完全**（官方警告） | 隔离的 **NixOS 服务** | 本章 |
| **Distrobox** | 任意发行版 | 标准（Podman/Docker） | **非 Nix 的软件与依赖** | §23.7、§25.5.13 |
| **Waydroid** | Android | LXC + binder | **Android 应用** | §23.12 |
| **Podman / Docker** | 任意镜像 | 标准 | 通用容器 | §23.7 |
| **`systemd-nspawn`** | 任意 | 中 | 底层工具（NixOS 容器基于它） | — |
| **microVM**（`microvm.nix`，非官方） | 完整内核 | **最强** | 强隔离 | — |

> [!TIP]
> **一句话选型**：
> - **跑非 Nix 软件（依赖问题）** → **Distrobox**（§25.5.13）
> - **跑 Android 应用** → **Waydroid**（§23.12）
> - **跑自己的 NixOS 服务、想隔离** → **本章的 `containers.*`**
> - **要强隔离跑不可信代码** → **microVM**（需第三方 flake）
>
> **本指南的立场**：**桌面用户 95% 的场景用前两个就够了。** 本章主要是补全官方结构，并解释「NixOS 原生容器为什么不能当 Docker 用」。

> [!NOTE]
> **为什么 NixOS 容器「不完全隔离」—— 技术原因（本指南推断，`[未核实]`）**
>
> 从官方描述可以推断出至少三个原因：
> 1. **共享 Nix store** —— 容器和宿主读同一份 `/nix/store`。虽然 store 是只读的，但**写入 `/nix/var/nix` 的数据库和 profile 是共享的**。
> 2. **`CAP_NET_ADMIN`** —— 官方明确说容器有这个 capability。
> 3. **没有 user namespace 映射** —— 容器 root 就是 uid 0，不是映射到宿主的高位 uid。
>
> **⚠️ 这是推断，不是官方声明。** 官方只说「not perfectly isolated」，没解释原因。**用之前请自己评估风险。**

### 31.6 五个反模式

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | 把 NixOS 容器当 Docker 用（跑不可信代码） | **官方明确警告**：容器 root 能影响宿主 | 用 Podman / microVM |
| 2 | 忘了 `boot.enableContainers = true` | `nixos-container` 命令报错 | 显式开启 |
| 3 | 用 NetworkManager 不管 `ve-*` | 容器网络时通时不通 | `unmanaged = [ "interface-name:ve-*" ]` |
| 4 | 声明式删容器后不 `destroy` | 磁盘被静默占用 | `nixos-container destroy <name>` |
| 5 | 容器配置里漏 `system.stateVersion` | 求值警告/失败 | 容器 `config` 里也要写 |

> [!TIP]
> **本章的一句话总结**：**NixOS 原生容器是「服务隔离」工具，不是「软件兼容」工具。** 你要的是后者 → 去 §25.5.13 看 Distrobox。

---

---

## 三十二、图形栈：Wayland 与 GPU 加速三件套（官方 `sec-wayland` / `sec-gpu-accel`）

本章补的是官方手册 **Part II** 的 `sec-wayland`、`sec-gpu-accel`、`sec-gpu-accel-opencl`、`sec-gpu-accel-vulkan`、`sec-gpu-accel-va-api`、`sec-gpu-accel-common-issues`。

**为什么这一章值得单独写**：本指南第三章讲了 AMD 显卡的**基础**配置（`hardware.graphics.enable`），但那只是「能出画面」。**这一章补的是「硬件加速到底有没有在工作」** —— 包括 Blender（OpenCL）、游戏（Vulkan）、视频解码（VA-API）三个真实场景。

> [!IMPORTANT]
> **本章与你最相关的一条**：官方在 `sec-gpu-accel-common-issues` 里明确警告 **ICD loader 与 runtime 来自不同 nixpkgs 版本会静默失败**。
>
> **这直接关系到本指南第二十章的「混合版本策略」** —— 如果你只把 mesa 滚到 unstable 而 rest 留在 stable，**Vulkan 可能静默不工作**。

### 32.1 Wayland（官方 `sec-wayland`）

**官方原文（逐句）**：

> *"While X11 (see X Window System) is still the primary display technology on NixOS, **Wayland support is steadily improving**. Where X11 separates the X Server and the window manager, on Wayland those are combined: **a Wayland Compositor is like an X11 window manager, but also embeds the Wayland 'Server' functionality**. This means it is sufficient to install a Wayland Compositor such as sway without separately enabling a Wayland server:"*

```nix
{ programs.sway.enable = true; }
```

> *"This installs the sway compositor along with some essential utilities. Now you can start sway from the TTY console."*

> *"**If you are using a wlroots-based compositor, like sway, and want to be able to share your screen, make sure to configure Pipewire using `services.pipewire.enable` and related options.**"*

> [!IMPORTANT]
> **官方那句「X11 is still the primary display technology on NixOS」是 26.05 的官方立场。**
>
> **对你的实际含义**：
>
> | 桌面 | 26.05 默认会话 | 你需要做什么 |
> |---|---|---|
> | **KDE Plasma 6** | Wayland（**已是默认**） | 无需额外配置 |
> | **GNOME 50** | Wayland（**已是默认**） | 无需额外配置 |
> | sway / Hyprland | Wayland（唯一选项） | `programs.sway.enable = true;` |
> | Xfce | X11 | — |
>
> **所以：你按本指南第六章配 GNOME 或 KDE，就已经在 Wayland 上了。** 官方手册这一节主要是为「用 wlroots 合成器（sway 等）」的人准备的。
>
> **唯一需要你做的**：**确保 PipeWire 开着**（屏幕共享）。本指南第六章的配置已包含，但这里给出官方理由。

**屏幕共享的完整前置条件（本指南综合官方 + 社区）**：

```nix
{
  # 1. PipeWire（官方明确要求）
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    pulse.enable = true;
    jack.enable = true;
  };

  # 2. xdg-desktop-portal（Wayland 屏幕共享的实际实现者）
  xdg.portal = {
    enable = true;
    extraPortals = with pkgs; [
      xdg-desktop-portal-gtk        # GTK 应用
      # KDE 用户加这个：
      # xdg-desktop-portal-kde
    ];
  };
}
```

> [!TIP]
> **本指南 §7.2（Flatpak）已经强调过 `xdg.portal.enable`** —— 因为 `services.flatpak` 有硬断言要求它。**这里补上「它还是 Wayland 屏幕共享的前置条件」。**
>
> **验证**：
> ```bash
> echo $XDG_SESSION_TYPE        # 应为 wayland
> systemctl --user status pipewire
> journalctl --user -u xdg-desktop-portal -n 20
> ```

### 32.2 OpenCL（AMD = `rocmPackages.clr.icd`）

**官方定义（原文）**：

> *"OpenCL is a general compute API. It is used by various applications such as **Blender and Darktable** to accelerate certain operations."*

**官方对机制的说明（原文）**：

> *"OpenCL applications load drivers through the **Installable Client Driver (ICD)** mechanism. In this mechanism, an ICD file specifies the path to the OpenCL driver for a particular GPU family. **In NixOS, there are two ways to make ICD files visible to the ICD loader.**"*

**路 1：环境变量 `OCL_ICD_VENDORS`**

```bash
$ export \
  OCL_ICD_VENDORS=`nix-build '<nixpkgs>' --no-out-link -A rocmPackages.clr.icd`/etc/OpenCL/vendors/
```

**路 2（官方推荐）：`hardware.graphics.extraPackages`**

> *"The second mechanism is to add the OpenCL driver package to `hardware.graphics.extraPackages`. This **links the ICD file under `/run/opengl-driver`**, where it will be visible to the ICD loader."*

**官方给的 AMD 配置（原文）**：

```nix
{ hardware.graphics.extraPackages = [ rocmPackages.clr.icd ]; }
```

> *"Modern AMD **Graphics Core Next (GCN)** GPUs are supported through the `rocmPackages.clr.icd` package."*

**官方的验证命令（原文）**：

```bash
$ clinfo | head -n3
Number of platforms  1
Platform Name        AMD Accelerated Parallel Processing
Platform Vendor      Advanced Micro Devices, Inc.
```

> [!TIP]
> **`clinfo` 的输出你要会读**：
>
> | 字段 | 期望值（你的 AMD 卡） |
> |---|---|
> | `Number of platforms` | **≥ 1**（0 = 没装上） |
> | `Platform Name` | `AMD Accelerated Parallel Processing` |
> | `Platform Vendor` | `Advanced Micro Devices, Inc.` |
> | `Device Name` | 你的显卡型号（如 `AMD Radeon RX 7900 XTX`） |
> | `Device Version` | OpenCL 版本（如 `OpenCL 2.1`） |
>
> **`Number of platforms 0`** → ICD 文件没被找到 → 检查 `hardware.graphics.extraPackages` 和 `/run/opengl-driver/etc/OpenCL/vendors/`。

> [!IMPORTANT]
> **`rocmPackages.clr.icd` 与「完整 ROCm」的区别**：
>
> - **`rocmPackages.clr.icd`** = **只需要 OpenCL 运行时**（Blender / Darktable 用）—— **小，装这个**
> - **完整 ROCm**（`rocmPackages.rocm-runtime` + 一堆库）= 需要跑 PyTorch / TensorFlow 的 GPU 加速 —— **大（数 GB）**
>
> **官方只推荐 `clr.icd`**，因为官方文档假设你用 OpenCL 应用。**如果你要跑 AI 训练**，看本指南 §3.4（`hardware.amdgpu.opencl.enable`）。
>
> **验证「OpenCL 到底有没有用上 GPU」**：
> ```bash
> # Blender：Edit → Preferences → System → 看 Compute Device 能否选到你的 GPU
> # Darktable：darktable -d opencl
> clinfo | grep -E 'Device Name|Max compute units'
> ```

### 32.3 Vulkan（AMD = RADV / Mesa）

**官方定义（原文）**：

> *"Vulkan is a graphics and compute API for GPUs. **It is used directly by games or indirectly through compatibility layers like DXVK.**"*

**官方对默认行为的说明（原文，非常重要）**：

> *"**By default, if `hardware.graphics.enable` is enabled, Mesa is installed and provides Vulkan for supported hardware.**"*

> *"Similar to OpenCL, Vulkan drivers are loaded through the **Installable Client Driver (ICD)** mechanism. ICD files for Vulkan are **JSON files** that specify the path to the driver library and the supported Vulkan version. **All successfully loaded drivers are exposed to the application as different GPUs.**"*

> *"In NixOS, there are two ways to make ICD files visible to Vulkan applications: an environment variable and a module option. The way to do this is to add the Vulkan driver package to `hardware.graphics.extraPackages`. This links the ICD file under `/run/opengl-driver`."*

**官方给的验证命令与输出（原文）**：

```bash
$ vulkaninfo | grep GPU
                GPU id  : 0 (Unknown AMD GPU)
                GPU id  : 1 (AMD RADV NAVI10 (LLVM 9.0.1))
     ...
GPU0:
        deviceType     = PHYSICAL_DEVICE_TYPE_DISCRETE_GPU
        deviceName     = Unknown AMD GPU
GPU1:
        deviceType     = PHYSICAL_DEVICE_TYPE_DISCRETE_GPU
```

> *"A simple graphical application that uses Vulkan is **`vkcube`** from the `vulkan-tools` package."*

**官方给的 AMD 结论（原文）**：

> *"Modern AMD **Graphics Core Next (GCN)** GPUs are supported through the **RADV driver, which is part of mesa**."*

> [!IMPORTANT]
> **对 AMD 用户最重要的一句话：Vulkan 驱动（RADV）就在 Mesa 里，`hardware.graphics.enable = true` 就自动有了。**
>
> **所以你不需要**：
> - ❌ 装 `amdvlk`（那是 AMD 官方驱动，RADV 通常更快）
> - ❌ 手动配 ICD
> - ❌ 加任何 `extraPackages`
>
> **你只需要**：确认 `hardware.graphics.enable = true`（本指南 §3.3 已强调这是**必须手写**的，因为默认是 `false`）。
>
> **注意官方示例里的 `Unknown AMD GPU`** —— 那不是错误。`vulkaninfo | grep GPU` 的输出**混杂了多个平台的设备**，第一行可能是某个 loader 的占位符。**看 `GPU1: deviceName` 或跑完整 `vulkaninfo` 看 `GPU id` 段。**

**验证 Vulkan 是否真的在用 GPU**：

```bash
# 1. 基础验证
vulkaninfo --summary | head -40

# 2. 图形验证（会弹一个小窗口转动的立方体）
vkcube

# 3. 游戏场景（Steam）
#    Steam → 游戏 → 属性 → 启动选项加：
#    DXVK_HUD=fps,devinfo %command%
#    然后看屏幕上是否有 HUD 叠加

# 4. 确认没有落到软件渲染
vulkaninfo | grep -iE 'llvmpipe|lavapipe'
# ↑ 有输出 = 在用 CPU 软件渲染，不正常
```

> [!DANGER]
> **`llvmpipe` / `lavapipe` 出现在 Vulkan 设备列表里 = 你在用 CPU 软渲染。**
>
> **典型症状**：游戏能跑但**帧数极低**（个位数）、`glxinfo` 显示 `llvmpipe`。
>
> **最常见原因**（按概率排序）：
> 1. **`hardware.graphics.enable` 没开**（本指南 §3.3 反复强调）→ `nixos-option hardware.graphics.enable` 验证
> 2. **用户不在 `video` / `render` 组**（见 §32.5）
> 3. **Mesa 与内核 `libdrm` ABI 不匹配**（本指南第二十章「只滚 mesa」的风险，官方在 §32.6 有对应警告）

### 32.4 VA-API（视频硬件解码）

**官方定义（原文）**：

> *"VA-API (Video Acceleration API) is an open-source library and API specification, which provides access to **graphics hardware acceleration capabilities for video processing**."*

> *"VA-API drivers are loaded by `libva`. **The version in nixpkgs is built to search the opengl driver path, so drivers can be installed in `hardware.graphics.extraPackages`.**"*

**官方的验证命令（原文）**：

```bash
$ nix-shell -p libva-utils --run vainfo
```

> [!IMPORTANT]
> **注意官方这一节只给了 Intel 的配置**（`intel-media-driver` / `intel-vaapi-driver`）—— **因为 AMD 的 VA-API 驱动也在 Mesa 里，不需要 `extraPackages`。**
>
> **所以 AMD 用户**：`hardware.graphics.enable = true` 就够了。**本指南 §3.5 已给出 `vainfo` 验证流程。**

**`vainfo` 输出的关键字段**：

| 字段 | 期望值（AMD） | 含义 |
|---|---|---|
| `Driver version` | `Mesa ... ` | 用的是 Mesa（✅ 对） |
| `vainfo: Driver version` | 含 `radeonsi` | **AMD 的正确驱动名** |
| `VAProfileH264...` | `VAEntrypointVLD` | 支持 H.264 解码 |
| `VAProfileHEVC...` | `VAEntrypointVLD` | 支持 H.265 解码 |
| `VAProfileAV1...` | `VAEntrypointVLD` | **支持 AV1 解码（新卡才有）** |

> [!TIP]
> **`VAEntrypointVLD` = 硬件解码（Video LD）**。**你要看到的就是这个。**
>
> **如果只有 `VAEntrypointEncSlice` 没有 `VLD`** → 只支持编码不支持解码（很少见）。
>
> **浏览器验证**：
> - **Firefox**：`about:support` → 搜 `VA-API` → 看 `Hardware Decoding` 是否为 `available` / `enabled`
> - **Chromium**：`chrome://gpu` → 看 `Video Decode` 是否为 `Hardware accelerated`
>
> **播放器验证**：
> ```bash
> # mpv（最直接）
> mpv --hwdec=auto-safe video.mp4      # 播放时按 i 看 hwdec 状态
> ```

### 32.5 用户权限（官方 `sec-gpu-accel-common-issues` 第一节）

**官方原文**：

> *"Except where noted explicitly, **it should not be necessary to adjust user permissions** to use these acceleration APIs. In the default configuration, **GPU devices have world-read/write permissions (`/dev/dri/renderD*`) or are tagged as `uaccess` (`/dev/dri/card*`)**. The access control lists of devices with the `uaccess` tag will be **updated automatically when a user logs in through `systemd-logind`**."*

**官方给的验证命令（原文）**：

```bash
$ getfacl /dev/dri/card0
# file: dev/dri/card0
# owner: root
# group: video
user::rw-
user:alice:rw-          # ← 登录后自动加上的 ACL
group::rw-
mask::rw-
other::---
```

> *"**If you disabled (this functionality of) `systemd-logind`, you may need to add the user to the `video` group and log in again.**"*

> [!IMPORTANT]
> **「默认不需要改权限」是官方的明确结论 —— 这也是 NixOS 比很多发行版省事的地方。**
>
> **但有两个例外（本指南补充）**：
> 1. **你禁用了 `systemd-logind` 的 uaccess**（罕见）→ 加 `video` 组
> 2. **你在容器 / 远程会话里**（如 SSH 里跑 GPU 程序）→ uaccess ACL **不会自动加**（因为不是「本地登录」）→ 需要 `render` / `video` 组
>
> **对 agent 用户的实际意义**：**如果 agent 要跑 GPU 程序（如用 GPU 做推理），必须把 agent 用户加进 `render` 组** —— 因为 agent 不是「本地登录用户」，拿不到 uaccess ACL。
>
> ```nix
> { users.users.hermes.extraGroups = [ "render" "video" ]; }
> ```

### 32.6 ★ ICD 混版本的静默失败（官方明确警告）

**官方原文（逐字，本节最重要的一段）**：

> *"The **Installable Client Driver (ICD) mechanism used by OpenCL and Vulkan loads runtimes into its address space using `dlopen`. Mixing an ICD loader mechanism and runtimes from different version of nixpkgs may not work.** For example, if the ICD loader uses an older version of glibc than the runtime, the runtime may not be loadable due to missing symbols. **Unfortunately, the loader will generally be quiet about such issues.**"*

> *"If you suspect that you are running into library version mismatches between an ICL loader and a runtime, you could run an application with the `LD_DEBUG` variable set to get more diagnostic information. For example, **OpenCL can be tested with `LD_DEBUG=files clinfo`**, which should report missing symbols."*

> [!DANGER]
> **这条官方警告直接关系到本指南第二十章的「混合版本策略」，必须重视。**
>
> **问题**：ICD 机制用 **`dlopen`** 加载驱动。`dlopen` 是**运行时**动态加载 —— 它**不受 Nix 的构建期依赖追踪保护**。
>
> **所以**：
> - 你的 **loader**（如 `libvulkan`）来自 **stable 的 nixpkgs**
> - 你的 **runtime**（如 `mesa` / `rocm`）来自 **unstable 的 nixpkgs**
> - 两者的 **glibc 版本不同** → `dlopen` 时**找不到符号** → **驱动加载失败**
>
> **最恶劣的地方**：*"the loader will generally be quiet about such issues"* —— **不报错，只是不工作**。你会看到「Vulkan 设备列表里没有独显」或「clinfo 报 0 个平台」，但**没有任何错误信息**。
>
> **对第二十章「路 C：只把 mesa 滚到 unstable」的具体风险**：
>
> | 你滚了什么 | 风险 |
> |---|---|
> | 只滚 `mesa`（含 RADV） | ⚠️ **中**：`libvulkan` loader 与 mesa 的 glibc 可能不同 → RADV 静默加载失败 |
> | 滚 `mesa` + `vulkan-loader` | ✅ **低**：两者同源 |
> | 滚 `mesa` + `vulkan-loader` + `libdrm` + `libva` | ✅ **最低**：整条链同源 |
> | **只滚内核** | ✅ **无风险**（内核不参与 `dlopen`） |
>
> **本指南修正建议**：
> ```nix
> # 如果只滚 mesa，把这些一起滚（同源）
> _module.args.pkgsUnstable = import nixpkgs-unstable { inherit system; ... };
>
> hardware.graphics.extraPackages = with config._module.args.pkgsUnstable; [
>   mesa
>   vulkan-loader
>   libva
>   libdrm
> ];
> ```
> **或者更简单**：**不要只滚 mesa**，改为**只滚内核 + Flatpak 里的应用**（本指南 §24.6 路 C 的修正版）。

**诊断命令（本指南补充官方给的 `LD_DEBUG`）**：

```bash
# OpenCL：官方给的命令
LD_DEBUG=files clinfo 2>&1 | grep -iE 'error|not found|cannot'

# Vulkan
LD_DEBUG=files vulkaninfo 2>&1 | grep -iE 'error|not found|cannot'

# 看 loader 找到了哪些 ICD
ls -la /run/opengl-driver/share/vulkan/icd.d/
ls -la /run/opengl-driver/etc/OpenCL/vendors/
cat /run/opengl-driver/share/vulkan/icd.d/*.json

# 对比 glibc 版本（关键诊断）
ldd $(readlink -f $(which clinfo)) | grep libc
strings /run/opengl-driver/lib/libvulkan.so.1 2>/dev/null | grep -i glibc
```

> [!TIP]
> **「`ldd` 对比 glibc」这一招能直接看出官方说的那个问题。**
>
> 如果 loader 和 runtime 链接的 `libc.so.6` **路径不同**（一个在 stable 的 store path，一个在 unstable 的 store path）→ **就是官方警告的那个场景**。

### 32.7 AMD 完整验证清单（本指南整合）

**把本指南散落的验证命令汇总成一份「一次性体检」**：

```bash
#!/usr/bin/env bash
# AMD 图形栈完整体检
echo "===== 1. 内核驱动 ====="
lspci -k | grep -A3 -iE 'vga|3d'          # 期望: Kernel driver in use: amdgpu

echo "===== 2. DRM 设备 ====="
ls -la /dev/dri/                            # 期望: card0, renderD128
getfacl /dev/dri/card0 2>/dev/null | grep "^user:"

echo "===== 3. Mesa / OpenGL ====="
nix-shell -p mesa-demos --run glxinfo | grep -E 'OpenGL renderer|OpenGL version'
# 期望: OpenGL renderer string: AMD Radeon ... (不是 llvmpipe)

echo "===== 4. Vulkan ====="
nix-shell -p vulkan-tools --run vulkaninfo --summary 2>/dev/null | grep -E 'deviceName|driverName'
# 期望: RADV, 不是 lavapipe

echo "===== 5. VA-API ====="
nix-shell -p libva-utils --run vainfo 2>/dev/null | grep -E 'Driver version|VAProfileH264|VAProfileAV1'

echo "===== 6. OpenCL ====="
nix-shell -p clinfo --run clinfo 2>/dev/null | head -3
# 期望: Number of platforms 1, AMD Accelerated Parallel Processing

echo "===== 7. 会话类型 ====="
echo "XDG_SESSION_TYPE=$XDG_SESSION_TYPE"   # 期望: wayland
loginctl show-session $(loginctl | grep $(whoami) | awk '{print $1}') -p Type

echo "===== 8. 硬件加速是否在用（浏览器）====="
echo "Firefox: about:support → 搜 'VA-API' 与 'Compositing'"
```

> [!TIP]
> **把这段存成 `~/bin/amd-check.sh` 并 `chmod +x`。** 每次系统大更新后跑一次 —— **它能在 30 秒内告诉你「图形栈有没有坏」**，比游戏里才发现帧数不对好得多。

**结果对照表**：

| 检查项 | ✅ 正常 | ❌ 异常 | 去本指南 |
|---|---|---|---|
| `lspci -k` | `amdgpu` | `radeon` / 空 | §3.2 |
| `glxinfo` renderer | AMD 型号 | `llvmpipe` | §3.3（`hardware.graphics.enable`） |
| `vulkaninfo` | RADV | lavapipe / 无 | §32.3、§32.6 |
| `vainfo` | `radeonsi` + `VLD` | 报错 | §3.5、§32.4 |
| `clinfo` | 1 platform | 0 platforms | §32.2 |
| `$XDG_SESSION_TYPE` | `wayland` | `x11`（KDE/GNOME 下异常） | §6.2、§32.1 |

### 32.8 六个反模式

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | 装了 `amdvlk` 期望更快 | 通常比 RADV 慢，且可能冲突 | AMD 用 Mesa 的 RADV |
| 2 | 只滚 `mesa` 到 unstable | **Vulkan 静默失效**（官方警告） | 连同 `vulkan-loader`/`libdrm` 一起滚 |
| 3 | agent 用户不加 `render` 组 | agent 跑 GPU 程序拿不到设备 | `extraGroups = [ "render" "video" ]` |
| 4 | 看到 `llvmpipe` 不管 | 游戏/视频全程软渲染，CPU 打满 | 按 §32.7 逐项排查 |
| 5 | 忘了 `xdg.portal` | Wayland 下**无法共享屏幕** | 见 §32.1 |
| 6 | 用 `vulkaninfo \| grep GPU` 看第一行 | 第一行可能是占位符 | 看 `--summary` 或 `deviceName` |

> [!TIP]
> **本章的一句话总结**：
> **AMD 用户的图形栈「开箱即对」—— 前提是 `hardware.graphics.enable = true`（默认是 false）。** 剩下所有问题几乎都来自两件事：**权限**（agent/容器场景）和**混版本**（只滚 mesa）。

---

---

## 三十三、内核、引导与「系统切换」的内部机制（官方 Part II + Part IV）

本章补的是官方手册 **Part II** 的 `sec-kernel-config` / `sec-linux-config-customizing`，以及 **Part IV** 的 `sec-switching-systems` / `sec-unit-handling` / `sec-activation-script` / `sec-non-switchable-system` / `sec-etc-overlay` / `sec-bootspec`。

**为什么这一章值得单独写**：本指南第十一、十四章讲了「怎么升级内核」「怎么换调度器」，但从没讲**「`nixos-rebuild switch` 到底做了什么」**。不理解这一步，你读不懂 `nixos-rebuild` 的输出，也读不懂报错。

### 33.1 `boot.kernelPackages` 与官方的一条硬规则

**官方原文**：

> *"You can override the Linux kernel and associated packages using the option `boot.kernelPackages`."*

```nix
{ boot.kernelPackages = pkgs.linuxKernel.packages.linux_3_10; }
```

> *"Note that this **not only replaces the kernel, but also packages that are specific to the kernel version, such as the NVIDIA video drivers**. This ensures that driver packages are consistent with the kernel."*

> *"While `pkgs.linuxKernel.packages` contains all available kernel packages, you may want to use one of the **unversioned `pkgs.linuxPackages_*` aliases such as `pkgs.linuxPackages_latest`**, that are kept up to date with new versions."*

> [!IMPORTANT]
> **第一句对你很重要**：`boot.kernelPackages` **不只是换内核**，它还换**所有依赖内核版本的包**（NVIDIA 驱动、树外模块、ZFS 等）。
>
> **这对 AMD 用户意味着什么**：**你几乎没有「内核相关包」** —— amdgpu 在主线内核里，Mesa 不依赖内核版本。**所以换内核对你风险很低**（这是本指南反复强调的 AMD 优势）。
>
> **但有一条例外**：如果你装了 `r8168`（Realtek 树外驱动）或 `virtualboxGuestAdditions`，**它们会跟着内核换版本**。本指南第四章建议用内核自带的 `r8169`，正是为了避开这个。

**★ 官方的「内核会被移除」规则（原文，逐字，这一段非常实用）**：

> *"Please note that **the current convention in NixOS is to only keep actively maintained kernel versions on both unstable and the currently supported stable release(s) of NixOS. This means that a non-longterm kernel will be removed after it's abandoned by the kernel developers, even on stable NixOS versions.** If you pin your kernel onto a non-longterm version, **expect your evaluation to fail as soon as the version is out of maintenance.**"*

> *"A kernel will be removed from nixpkgs **when the first batch of stable kernels after the final release is published**. E.g. when 6.15.11 is the final release of the 6.15 series and is released together with 6.16.3 and 6.12.43, **it will be removed on the release of 6.16.4 and 6.12.44**. Custom kernel variants such as `linux-hardened` are also affected by this."*

> *"**Longterm versions of kernels will be removed before the next stable NixOS that will exceed the maintenance period of the kernel version.**"*

> [!DANGER]
> **这一条是本轮发现的最实用的官方规则之一 —— 它解释了本指南第十四章的一个隐患。**
>
> **问题**：如果你写死了 `boot.kernelPackages = pkgs.linuxKernel.packages.linux_6_15;`，**某天 `nixos-rebuild` 会突然报「属性不存在」**。
>
> **为什么**：上游内核开发者放弃 6.15 后，nixpkgs 会在**第一批新稳定内核发布时**删掉它。**即使你在 stable 分支上也会被删。**
>
> **官方给的解法**：**用不带版本号的别名**：
>
> | 写法 | 会不会被删 | 版本行为 |
> |---|---|---|
> | `pkgs.linuxPackages_latest` | ❌ 不会 | **跟随最新**（每次 update 可能跳大版本） |
> | `pkgs.linuxPackages_zen` | ❌ 不会 | zen 分支，跟随上游 |
> | `pkgs.linuxPackages`（默认） | ❌ 不会 | 26.05 的默认（当前 6.18） |
> | `pkgs.linuxPackages_6_18` | ⚠️ **会**（6.18 停止维护后） | 锁定小版本 |
> | `pkgs.linuxKernel.packages.linux_6_15` | ⚠️ **会** | 锁定具体版本 |
>
> **本指南第十四章的建议**：**用 `linuxPackages_zen` 或默认**，不要写死小版本号。**这一节给了官方理由。**

**本指南补充：如何查一个内核版本的维护状态**：

```bash
# 看当前内核
uname -r

# 看 nixpkgs 里有哪些内核（以及是否还是别名）
nix eval --raw nixpkgs#linuxPackages_latest.version
nix eval --raw nixpkgs#linuxPackages_zen.version

# 看内核官方维护状态
# https://www.kernel.org/category/releases.html
# Longterm / Stable / EOL 一目了然
```

### 33.2 看当前内核配置

**官方原文**：

> *"The default Linux kernel configuration should be fine for most users. You can see the configuration of your current kernel with the following command:"*

```bash
zcat /proc/config.gz
```

> [!TIP]
> **`/proc/config.gz` 存在的前提是内核开了 `CONFIG_IKCONFIG_PROC`。** NixOS 的默认内核**开了**，所以这条命令可用。
>
> **常用查法**：
> ```bash
> # 某个特性是否编入
> zcat /proc/config.gz | grep -E 'CONFIG_NTSYNC|CONFIG_SCHED_BORE|CONFIG_ANDROID_BINDER'
>
> # 对比本指南 §14.2 的说法
> zcat /proc/config.gz | grep -E 'CONFIG_HZ|CONFIG_PREEMPT'
> ```
>
> **本指南 §23.12 说过「NixOS 默认内核已编入 binder，装 Waydroid 不需要自定义内核」** —— 验证命令就是这一条：
> ```bash
> zcat /proc/config.gz | grep -E 'CONFIG_ANDROID_BINDER_IPC|CONFIG_ANDROID_BINDERFS'
> # 期望: =y 而不是 =m 或 # CONFIG_... is not set
> ```

### 33.3 用 `extraConfig` 自定义内核

**官方原文**：

> *"If you want to change the kernel configuration, you can use the `packageOverrides` feature."*

```nix
{
  nixpkgs.config.packageOverrides =
    pkgs:
    pkgs.lib.recursiveUpdate pkgs {
      linuxKernel.kernels.linux_5_10 = pkgs.linuxKernel.kernels.linux_5_10.override {
        extraConfig = ''
          KGDB y
        '';
      };
    };
}
```

> *"`extraConfig` takes a list of Linux kernel configuration options, **one per line**. The name of the option should **not include the prefix `CONFIG_`**. The option value is typically **`y`, `n` or `m`** (to build something as a kernel module)."*

**官方给的「用自定义内核」的接法**：

```nix
{ boot.kernelPackages = pkgs.linuxPackagesFor yourCustomKernel; }
```

> [!WARNING]
> **自定义内核 = 每次内核更新都要本地编译（30 分钟到 2 小时，取决于 CPU）。**
>
> **对 AMD 游戏用户的实际建议**：
> - **不要为了「性能」自定义内核** —— 本指南 §14.2 已给出结论：**编译期差异存在，但转化成可感知体验的证据不足**
> - **只在「某个特性确实没编入」时才自定义**（如某个特殊硬件的驱动）
> - **如果只是想换调度器** → 用 `linuxPackages_zen`（本指南 §14.3），**不要自己编**
>
> **`extraConfig` 的常见用途（本指南补充）**：
> ```nix
> extraConfig = ''
>   # 打开某硬件的驱动
>   CONFIG_...
> '';
> ```
> **⚠️ 注意官方说「不要写 `CONFIG_` 前缀」** —— 所以上面那行如果照抄会错。正确写法是 `MY_OPTION y`。

### 33.4 内核模块与 sysctl

**官方原文（三种）**：

```nix
# 1. 强制加载模块（udev 通常会自动加载，这是「保险」）
{
  boot.kernelModules = [
    "fuse"
    "kvm-intel"
    "coretemp"
  ];
}

# 2. 早期就要用的模块（进 initrd）
{ boot.initrd.kernelModules = [ "cifs" ]; }
```

> *"This causes the specified modules and their dependencies to be added to the **initial ramdisk**."*

```nix
# 3. 运行时内核参数
{ boot.kernel.sysctl."net.ipv4.tcp_keepalive_time" = 120; }
```

> *"To see the available parameters, run `sysctl -a`."*

> [!IMPORTANT]
> **`boot.kernelModules` vs `boot.initrd.kernelModules` 的区别**：
>
> | | `boot.kernelModules` | `boot.initrd.kernelModules` |
> |---|---|---|
> | 加载时机 | 系统启动后（udev 阶段） | **initrd 阶段**（挂根文件系统之前） |
> | 什么时候需要 | udev 没自动加载（罕见） | **根文件系统在该模块之上**（如 CIFS / NFS 根、LUKS 的特殊算法） |
> | 代价 | 无 | **增大 initrd** |
>
> **本指南 §14.x 的「内核参数调优」用的是 `boot.kernel.sysctl`**（运行时参数），**不是** `boot.kernelModules`。**两者不要混。**

> [!WARNING]
> **`boot.kernel.sysctl` 的键名必须加引号**（见 §26.1 的官方说明）：
> ```nix
> boot.kernel.sysctl."net.ipv4.tcp_keepalive_time" = 120;   # ✅
> boot.kernel.sysctl.net.ipv4.tcp_keepalive_time = 120;     # ❌
> ```

### 33.5 ★ `nixos-rebuild switch` 到底做了什么（官方 `sec-switching-systems`）

**官方原文（本节是整个 Part IV 里最实用的一段）**：

> *"`nixos-rebuild`, like many deployment solutions, calls **`switch-to-configuration`** which resides in a NixOS system at **`$out/bin/switch-to-configuration`**. The script is called with the action that is to be performed like **`switch`, `test`, `boot`**. There is also the **`dry-activate`** action which does not really perform the actions but rather **prints what it would do if you called it with `test`**. This feature can be used to **check what service states would be changed** if the configuration was switched to."*

> *"If the action is `switch` or `boot`, **the bootloader is updated first** so the configuration will be the next one to boot. Unless `NIXOS_NO_SYNC` is set to `1`, **`/nix/store` is synced to disk**."*

> *"If the action is `switch` or `test`, the currently running system is inspected and the actions to switch to the new system are calculated. This process takes **two data sources** into account: **`/etc/fstab` and the current systemd status**."*

> *"Mounts and swaps are read from `/etc/fstab` and the corresponding actions are generated. If the options of a mount are modified, for example, **the proper `.mount` unit is reloaded (or restarted if anything else changed and it's neither the root mount or the nix store)**."*

> *"The current systemd state is inspected, the difference between the current system and the desired configuration is calculated and actions are generated to get to this state."*

**★ 官方的「动作顺序」（原文，逐条）**：

> *"After calculating what should be done, the actions are carried out. **The order of actions is always the same:**"*

```
1. Stop units                              (systemctl stop)
2. Run activation script                   ($out/activate)
3. See if the activation script requested more units to restart
4. Restart systemd if needed               (systemd daemon-reexec)
5. Forget about the failed state of units  (systemctl reset-failed)
6. Reload systemd                          (systemctl daemon-reload)
7. Reload systemd user instances           (systemctl --user daemon-reload)
8. Reactivate sysinit                      (systemctl restart sysinit-reactivation.target)
9. Reload units                            (systemctl reload)
10. Restart units                          (systemctl restart)
11. Start units                            (systemctl start)
12. Inspect what changed during these actions and print units that failed and that were newly started
```

**官方的调试环境变量（原文）**：

> *"By default, some units are filtered from the outputs to make it less spammy. This can be disabled for development or testing by setting the environment variable **`STC_DISPLAY_ALL_UNITS=1`**. More detailed output can be displayed by setting **`STC_DEBUG=1`**."*

> [!IMPORTANT]
> **这一节解释了你在 `nixos-rebuild switch` 输出里看到的一切。**
>
> **逐条对应你的实际体验**：
>
> | 你看到的输出 | 官方第几步 | 含义 |
> |---|---|---|
> | `activating the configuration...` | **2** | 正在跑 activation script |
> | `setting up /etc...` | 2（etc snippet） | 生成 `/etc` |
> | `reloading user units for <user>...` | **7** | 重载用户级 systemd |
> | `restarting sysinit-reactivation.target` | **8** | 重启「早期启动单元」（见 §33.6） |
> | `restarting the following units: ...` | **10** | 这些服务被重启了 |
> | `the following new units were started: ...` | **11** | 这些是新启动的 |
> | `warning: the following units failed: ...` | **12** | ⚠️ **这些失败了** |
>
> **★ 最有价值的一条**：**最后那行 `warning: the following units failed` 是你必须看的。** 很多人 `nixos-rebuild switch` 完看到「成功」就走了，**漏掉了这行警告**，结果某个服务其实没起来。
>
> **本指南建议**：switch 完立刻跑
> ```bash
> systemctl list-units --failed
> ```

> [!TIP]
> **`dry-activate` 是被严重低估的选项。**
>
> ```bash
> sudo nixos-rebuild dry-activate
> ```
>
> 官方原文：*"does not really perform the actions but rather **prints what it would do**"*。**它告诉你「这次 switch 会重启哪些服务」，但什么都不做。**
>
> **对你的实际用途**：
> - 改配置后先 `dry-activate` → **看看会不会重启你的桌面/网络**
> - 如果会重启网络 → **知道要小心**（远程 SSH 时可能断线）
> - 如果会重启显示管理器 → **知道屏幕会黑一下**
>
> **比 `dry-build` 更进一步**：`dry-build` 只验证**能构建**，`dry-activate` 还告诉你**会动什么**。

### 33.6 单元处理规则（官方 `sec-unit-handling`）

**官方原文（这一段是给模块开发者写的，但读它能理解「为什么某个服务被重启了」）**：

> *"To figure out what units need to be started/stopped/restarted/reloaded, the script first checks the current state of the system... For each of the units, the script goes through the following checks:"*

> - *"**Is the unit file still in the new system?** If not, **stop the service** unless it sets `X-StopOnRemoval` in the `[Unit]` section to false."*
> - *"**Is it a `.target` unit?** If so, start it unless it sets `RefuseManualStart`... Also stop the unit again unless it sets `X-StopOnReconfiguration` to false."*
> - *"**Are the contents of the unit files different?** They are compared by parsing them and comparing their contents. **If they are different but only `X-Reload-Triggers` in the `[Unit]` section is changed, reload the unit.** ... If the unit files differ in any way, the following actions are performed:"*
>   - *"`.path` and `.slice` units are **ignored**."*
>   - *"`.mount` units are **reloaded if only their `Options` changed**. If anything else changed (like `What`), they are **restarted** unless they are the mount unit for `/` or `/nix` **in which case they are reloaded to prevent the system from crashing**."*
>   - *"`.socket` units are currently **ignored**."*
>   - *"The rest of the units (mostly `.service` units) are then **reloaded if `X-ReloadIfChanged`** ... is set to true... A little exception is done for units that were deactivated in the meantime... These are started instead of reloaded."*
>   - *"If the reload flag is not set, some more flags decide if the unit is skipped. These flags are **`X-RestartIfChanged`** ..., **`RefuseManualStop`** ..., and **`X-OnlyManualStart`** ..."*
>   - *"Further behavior depends on the unit having **`X-StopIfChanged`** ... set to true... **This is set to true by default** and must be explicitly turned off if not wanted. If the flag is enabled, **the unit is stopped and then started**. If not, the unit is restarted. **The goal of the flag is to make sure that the new unit never runs in the old environment which is still in place before the activation script is run.**"*
>   - *"The last thing that is taken into account is whether the unit is a service and **socket-activated**..."*

**官方给的「sysinit reactivation」机制（原文）**：

> *"`sysinit.target` is a systemd target that encodes system initialization (i.e. early startup)... Probably the most notable one of these is **`systemd-tmpfiles-setup.service`**."*

> *"'Normal' systemd units, by default, are ordered **AFTER** `sysinit.target`... When restarting both a unit ordered before `sysinit.target` as well as one after, **this presents a problem because they would be started at the same time** as they do not explicitly declare their dependency relations."*

> *"To solve this, NixOS has an artificial **`sysinit-reactivation.target`** which allows you to ensure that services ordered before `sysinit.target` are restarted correctly."*

```nix
{
  systemd.services.my-sysinit = {
    requiredBy = [ "sysinit-reactivation.target" ];
    before = [ "sysinit-reactivation.target" ];
    restartTriggers = [ config.environment.etc."my-sysinit.d".source ];
  };
}
```

> [!IMPORTANT]
> **这一节的核心价值：解释「为什么改了某个配置，某个看起来无关的服务被重启了」。**
>
> **NixOS 的判据是「unit 文件内容变了吗」，不是「你改了哪个选项」。** 所以：
> - 你改了 `environment.systemPackages` → **任何引用 `systemPackages` 的服务，其 unit 文件都变了** → 它们全被重启
> - 你改了 `users.users.foo` → 引用它的服务被重启
>
> **这就是为什么改一点小东西，`nixos-rebuild switch` 会重启十几个服务。**
>
> **官方的 `X-*` 私有标志**（`X-StopIfChanged` / `X-ReloadIfChanged` / `X-RestartIfChanged`）是**模块作者用来控制这个行为的**。**它们只对 `nixos-rebuild switch` 有效**，systemd 本身不认识 —— 所以 `systemctl cat` 能看到它们，但 systemd 会忽略。

> [!TIP]
> **`X-StopIfChanged = true`（默认）为什么重要**（官方原文解释）：
>
> *"The goal of the flag is to make sure that **the new unit never runs in the old environment** which is still in place before the activation script is run."*
>
> **翻译**：`switch` 的顺序是「先停旧服务 → 再跑 activation script → 再起新服务」。如果只 `restart`（而不是 `stop` + `start`），新服务可能**在旧的 `/etc` 环境下启动**。
>
> **所以默认 `stop` + `start` 是**正确性**要求，不是保守。**

### 33.7 activation script（官方 `sec-activation-script`）

**官方原文**：

> *"The activation script is a bash script called to activate the new configuration which resides in a NixOS system in **`$out/activate`**... Please be aware that **the script is executed on every boot and system switch**, so tasks that can be performed in other places should be performed there (for example letting a directory of a service be created by systemd using mechanisms like `StateDirectory`, `CacheDirectory`, … or if that's not possible using `preStart` of the service)."*

```nix
{
  system.activationScripts.my-activation-script = {
    deps = [ "etc" ];
    # supportsDryActivation = true;
    text = ''
      echo "Hallo i bims"
    '';
  };
}
```

> *"This example creates an activation script snippet that is **run after the `etc` snippet**. The special variable **`supportsDryActivation`** can be set so the snippet is also run when `nixos-rebuild dry-activate` is run. To differentiate between real and dry activation, the **`$NIXOS_ACTION`** environment variable can be read which is set to `dry-activate` when a dry activation is done."*

**官方列的「NixOS 默认启用的 snippet」（原文）**：

> - *"**`binsh`** creates `/bin/sh` which points to the runtime shell"*
> - *"**`etc`** sets up the contents of `/etc`, this includes systemd units and **excludes `/etc/passwd`, `/etc/group`, and `/etc/shadow`** (which are managed by the `users` snippet)"*
> - *"**`modprobe`** sets the path to the `modprobe` binary for module auto-loading"*
> - *"**`specialfs`** is responsible for mounting filesystems like `/proc` and `sys`"*
> - *"**`users`** creates and removes users and groups by managing `/etc/passwd`, `/etc/group` and `/etc/shadow`. This also creates home directories"*
> - *"**`usrbinenv`** creates `/usr/bin/env`"*

> [!IMPORTANT]
> **官方那句「executed on every boot and system switch」解释了 activation script 的性能影响。**
>
> **所以**：**不要往 `system.activationScripts` 里塞重活**（比如扫描大目录、下载文件）。每次开机都跑一遍。
>
> **官方给的正确替代**（按优先级）：
> 1. **`StateDirectory` / `CacheDirectory`**（systemd 原生，最快）
> 2. **`preStart`**（服务启动前跑一次）
> 3. **`systemd.tmpfiles.rules`**（创建目录/文件）
> 4. **`system.activationScripts`**（最后手段）
>
> **本指南 §18.x 用的 `systemd.tmpfiles.rules`** 就是官方推荐的路径之一。

**`/bin/sh` 与 `/usr/bin/env` 是 NixOS「假装有 FHS」的两块拼图**（官方原文的 `binsh` 和 `usrbinenv`）—— **这解释了本指南第二十五章「为什么有些脚本能跑」**：`#!/bin/sh` 和 `#!/usr/bin/env bash` 这两种 shebang **在 NixOS 上可用**（因为 activation script 创建了这两个文件）。

### 33.8 `/etc` via overlay（实验性）

**官方原文**：

> ⚠️ *"**This is experimental** and requires a **kernel version >= 6.6** because it uses new overlay features and relies on the new mount API."*

```nix
{ system.etc.overlay.enable = true; }
```

> *"Using an overlay has two benefits:"*
> - *"it **removes a dependency on perl**"*
> - *"it makes **activation faster (up to a few seconds)**"*

```nix
{ system.etc.overlay.mutable = false; }
```

> *"By default, the `/etc` overlay is mounted **writable**... However, you can also mount `/etc` **immutably (read-only)** by setting [the above]."*

> *"**The overlay is atomically replaced during system switch. However, files that have been modified will NOT be overwritten. This is the biggest change compared to the perl-based system.**"*

> *"If you manually make changes to `/etc` on your system and then switch to a new configuration where `system.etc.overlay.mutable = false;`, **you will not be able to see the previously made changes in `/etc` anymore. However the changes are not completely gone, they are still in the upperdir of the previous overlay in `/.rw-etc/upper`.**"*

> [!IMPORTANT]
> **「files that have been modified will NOT be overwritten」是一个重要的行为差异。**
>
> **传统 perl 系统的行为**：`nixos-rebuild switch` 会**覆盖** `/etc` 里的文件（除非是 `mutableUsers` 保护的那几个）。
>
> **overlay 系统的行为**：**你手改过的文件会保留**（因为它在 upperdir 里）。
>
> **这是「更好」还是「更坏」取决于你的立场**：
> - ✅ **好**：手改的临时调整不会被冲掉
> - ❌ **坏**：**你以为配置生效了，其实被 upperdir 里的旧文件盖住了** → 这是很难查的一类问题
>
> **本指南的建议**：**如果你开了 `system.etc.overlay.enable`，请同时开 `mutable = false`** —— 强制只读，就不会有「手改残留」的困惑。这也是 Aeon 式不可变系统的思路（§24.x）。
>
> **⚠️ 但 `mutable = false` 会带来 §28.6 的问题** —— 密码文件写不进去 → 需要 `services.userborn.passwordFilesLocation` 或接受 `users.mutableUsers = false`。

### 33.9 Bootspec

**官方原文**：

> *"**Bootspec** is a feature introduced in **RFC-0125** in order to **standardize bootloader support and advanced boot workflows such as SecureBoot** and potentially more. The reference implementation can be found here. **The creation of bootspec documents is enabled by default.**"*

> [!NOTE]
> **Bootspec 对你的实际意义**：
>
> 它把「这个 generation 的内核在哪、initrd 在哪、命令行是什么」标准化成一个 **JSON 文档**，放在 `/nix/store/.../boot.json`。
>
> **谁在用**：
> - **`lanzaboote`**（Secure Boot，本指南 §23.x 提到过）—— **它依赖 bootspec**
> - 第三方 bootloader（如 `systemd-boot` 的替代品）
> - 高级引导流程（如 UKI 统一内核镜像）
>
> **你需要做什么**：**什么都不用做**（官方说默认开启）。**但如果你想开 Secure Boot，bootspec 是前置条件。**

**查看 bootspec 文档**：

```bash
cat /run/current-system/boot.json | jq . 2>/dev/null || \
  cat $(readlink -f /run/current-system)/boot.json | head -40
```

### 33.10 不可切换系统（官方 `sec-non-switchable-system`）

**官方原文**：

> *"In certain systems, most notably **image based appliances**, updates are handled outside the system. This means that **you do not need to rebuild your configuration on the system itself anymore**."*

```nix
{ modulesPath, ... }:
{
  imports = [ "${modulesPath}/profiles/image-based-appliance.nix" ];
}
```

> *"The most notable deviation of this profile from a standard NixOS configuration is that **after building it, you cannot switch to the configuration anymore**. The profile sets **`config.system.switch.enable = false;`**, which **excludes `switch-to-configuration`**, the central script called by `nixos-rebuild`, from your system. **Removing this script makes the image lighter and slightly more secure.**"*

> [!IMPORTANT]
> **`system.switch.enable = false` 砍掉的正是 §33.5 里那个脚本。**
>
> **这带来的效果**：
> | | 普通 NixOS | image-based-appliance |
> |---|---|---|
> | 能 `nixos-rebuild switch` | ✅ | ❌ |
> | 能 `nixos-rebuild boot` | ✅ | ❌ |
> | 怎么更新 | 本地 rebuild | **替换整个镜像**（A/B 分区或外部工具） |
> | 体积 | 大 | 小 |
> | 攻击面 | 有 `switch-to-configuration` | 无 |
>
> **这正是「Aeon 式」不可变系统的 NixOS 官方实现**（连本指南第二十四章）。
>
> **对你的建议**：**桌面用户不要开这个。** 你失去了 NixOS 最大的优势（本地原子切换 + 回滚）。**它适合的是「设备/固件」场景**（如 kiosk、路由器、专用设备）。

> [!TIP]
> **一个有意思的推论**：`image-based-appliance` 里 **`nixos-rebuild` 还在**（只是 switch 不行），你可以用 `nixos-rebuild build` 生成新镜像。**所以更新流程是**：
> ```
> 开发机：nixos-rebuild build-image → 产出镜像文件
> 目标机：用工具刷入镜像（或 A/B 分区切换）
> ```

### 33.11 六个反模式

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | 写死 `pkgs.linuxPackages_6_15` | 内核 EOL 后**求值失败** | 用 `linuxPackages_zen` / `_latest` / 默认 |
| 2 | 自定义内核只为「性能」 | 每次更新编译 1 小时，收益无证据 | 用现成内核（§14.2 结论） |
| 3 | `switch` 后不看 `units failed` 警告 | 服务静默失败 | `systemctl list-units --failed` |
| 4 | 改配置前不跑 `dry-activate` | 意外重启网络/桌面 | `sudo nixos-rebuild dry-activate` |
| 5 | 往 `activationScripts` 塞重活 | **每次开机都跑** | `StateDirectory` / `tmpfiles` / `preStart` |
| 6 | 开 `etc.overlay` 但不开 `mutable = false` | 手改残留，**以为配置生效其实没有** | 两者成对开 |

> [!TIP]
> **本章的一句话总结**：
> **`nixos-rebuild switch` = 算差异 → 停服务 → 跑 activation → 重载 systemd → 起服务 → 报告失败。** 看懂这五步，你就看懂了 NixOS 的所有输出。
>
> **最实用的两个选项**：`dry-activate`（先看会动什么）和 `STC_DISPLAY_ALL_UNITS=1`（看全部单元）。

---

---

## 三十四、写 NixOS 模块与测试（官方 Part IV · Development）

本章补的是官方手册 **Part IV** 的 `sec-getting-sources`、`sec-writing-modules`、`sec-option-declarations`、`sec-option-types`、`sec-option-definitions`、`sec-assertions`、`sec-meta-attributes`、`sec-importing-modules`、`sec-replace-modules`、`sec-freeform-modules`、`sec-settings-options`、`sec-nixos-tests`、`sec-writing-nixos-tests`、`sec-running-nixos-tests`。

**为什么这一章值得写**（尽管你「只是用户」）：

> [!IMPORTANT]
> **本章的定位不是「让你成为 nixpkgs 贡献者」，而是「让你能判断 Agent 写的模块对不对」。**
>
> **本指南第十章讲「让 Agent 管系统」，第二十一章讲「Agent 的安装方式」。但一直没讲：Agent 给你生成的 `systemd.services.xxx` 或 `mkOption`，你怎么知道它写对了？**
>
> **本章给你三样东西**：
> 1. **模块的语法骨架**（能看出结构错没错）
> 2. **优先级的精确数字**（能看出 `mkForce` 用得对不对）
> 3. **断言机制**（能看出「这个配置会不会在别人机器上炸」）

### 34.1 获取源码

**官方章节名**：`sec-getting-sources`（Getting the Sources）。

**本指南补充的实际做法**（对「不写代码、只想查」的用户）：

```bash
# 方式 1：查某个模块的源码（最快，不用克隆）
#   nixpkgs 在 GitHub 上，直接看：
#   https://github.com/NixOS/nixpkgs/blob/nixos-26.05/nixos/modules/<路径>

# 方式 2：本地已经有源码（在 store 里）
nix eval --raw nixpkgs#path        # 打印 nixpkgs 的 store 路径
# 然后在那个路径下看 nixos/modules/

# 方式 3：完整克隆（想搜索时用）
git clone --depth 1 -b nixos-26.05 https://github.com/NixOS/nixpkgs
# ⚠️ 即使 --depth 1，这个仓库也有几 GB

# 方式 4：只看单个文件（最快）
curl -s https://raw.githubusercontent.com/NixOS/nixpkgs/nixos-26.05/nixos/modules/programs/nix-ld.nix
```

> [!TIP]
> **本指南前二十五章的所有源码核实，用的都是「方式 4」** —— `raw.githubusercontent.com` 直接取单文件，**不需要克隆，秒级返回**。
>
> **给 Agent 的提示词模板**：
> ```
> 请从 https://raw.githubusercontent.com/NixOS/nixpkgs/nixos-26.05/nixos/modules/<路径> 读取源码，
> 逐行核实选项的默认值，不要凭记忆回答。
> ```
> **加「不要凭记忆」这句很关键** —— 否则 Agent 会用训练数据里的旧版本答案（见本指南第二十五章 §25.2 的 `xorg` 改名事件）。

### 34.2 模块的完整结构（官方 Example 14）

**官方原文（回顾 §26.2）**：

```nix
{ config, pkgs, ... }:

{
  imports = [
    # paths of other modules
  ];

  options = {
    # option declarations
  };

  config = {
    # option definitions
  };
}
```

**官方对四个部分的说明（原文）**：

> - *"The first line makes the current Nix expression a function. The variable `pkgs` contains Nixpkgs (by default, it takes the `nixpkgs` entry of `NIX_PATH`)... while `config` contains the full system configuration. **This line can be omitted if there is no reference to `pkgs` and `config` inside the module.**"*
> - *"This `imports` list enumerates the paths to other NixOS modules that should be included in the evaluation of the system configuration. A default set of modules is defined in the file `modules/module-list.nix`. **These don't need to be added in the import list.**"*
> - *"The attribute `options` is a nested set of **option declarations**."*
> - *"The attribute `config` is a nested set of **option definitions**."*

**官方给的完整例子（`locate` 服务）**：

> *"This module declares two options that can be defined by other modules (typically the user's `configuration.nix`): **`services.locate.enable`** (whether the database should be updated) and **`services.locate.interval`** (when the update should be done). It implements its functionality by defining two options declared by other modules: **`systemd.services`** and **`systemd.timers`**."*

**★ 官方的一条 `Exec*` 警告（原文，非常实用）**：

> *"Care must be taken when writing systemd services using `Exec*` directives. By default systemd performs **substitution on `%<char>` specifiers** in these directives, **expands environment variables from `$FOO` and `${FOO}`**, **splits arguments on whitespace**, and **splits commands on `;`**. **All of these must be escaped to avoid unexpected substitution or splitting** when interpolating into an `Exec*` directive, e.g. when using an `extraArgs` option to pass additional arguments to the service. The functions **`utils.escapeSystemdExecArg`** and **`utils.escapeSystemdExecArgs`** are provided for this."*

> [!DANGER]
> **这是「Agent 写的服务为什么启动失败」的最常见原因。**
>
> **具体场景**：Agent 给你生成
> ```nix
> serviceConfig.ExecStart = "${pkgs.myapp}/bin/myapp --arg $VALUE";
> ```
> **结果**：systemd 把 `$VALUE` **当成环境变量展开**（而不是字面传给程序），且**按空格切分参数**。
>
> **正确写法**（三种）：
> ```nix
> # 1. 用官方工具函数（最推荐）
> serviceConfig.ExecStart = lib.concatStringsSep " " [
>   "${pkgs.myapp}/bin/myapp"
>   (lib.utils.escapeSystemdExecArg "--arg=${someValue}")
> ];
>
> # 2. 用 writeShellScript 把逻辑挪进脚本（最省心）
> serviceConfig.ExecStart = pkgs.writeShellScript "start-myapp" ''
>   exec ${pkgs.myapp}/bin/myapp --arg "$VALUE"
> '';
>
> # 3. 用 Environment= 传变量，ExecStart 里用 ${VAR}
> serviceConfig = {
>   Environment = [ "VALUE=${someValue}" ];
>   ExecStart = "${pkgs.myapp}/bin/myapp --arg ''${VALUE}";
>   #                                                  ↑ 注意 Nix 里要写 ''${ 来转义
> };
> ```
>
> **本指南的立场**：**给 Agent 的提示词里加一句「`ExecStart` 请用 `pkgs.writeShellScript` 包裹」** —— 这能避开 90% 的转义问题。

### 34.3 选项声明（`mkOption`）

**官方原文**：

> *"An **option declaration** specifies the name, type and description of a NixOS configuration option. **It is invalid to define an option that hasn't been declared in any module.**"*

```nix
{
  options = {
    name = mkOption {
      type = type specification;
      default = default value;
      example = example value;
      description = "Description for use in the NixOS manual.";
    };
  };
}
```

**官方对命名约定的说明（原文）**：

> *"The attribute names within the name attribute path must be **camel cased** in general but should, **as an exception, match the package attribute name when referencing a Nixpkgs package**. For example, the option `services.nix-serve.bindAddress` references the `nix-serve` Nixpkgs package."*

> [!TIP]
> **这条命名约定解释了一个你早就见过的现象**：
> - `services.nix-serve` **不是** camelCase（因为对应包名 `nix-serve`）
> - 但 `bindAddress` **是** camelCase
>
> **所以看到 `systemd.services."my-name"`（带引号带连字符）不要奇怪** —— 那是「名字不是合法 Nix 标识符」时必须的写法（§26.1）。

**官方对 `mkOption` 各参数的说明（原文要点）**：

| 参数 | 官方说明 | 是否必需 |
|---|---|---|
| `type` | *"The type of the option... **This argument is mandatory for nixpkgs modules.** Setting this is highly recommended for the sake of documentation and type checking. In case it is not set, a fallback type with unspecified behavior is used."* | **nixpkgs 模块必需** |
| `default` | *"The default value used if no value is defined by any module. **A default is not required; but if a default is not given, then users of the module will have to define the value of the option, otherwise an error will be thrown.**"* | 可选（但影响「用户是否必须写」） |
| `defaultText` | *"A textual representation of the default value to be rendered verbatim in the manual. Useful if the default value is a complex expression or depends on other values or packages. Use `lib.literalExpression` for a Nix expression, `lib.literalMD` for a plain English description in Nixpkgs-flavored Markdown format."* | 可选（文档用） |
| `example` | *"An example value that will be shown in the NixOS manual."* | 可选（文档用） |
| `description` | *"A textual description of the option in Nixpkgs-flavored Markdown format that will be included in the NixOS manual."* | **强烈建议** |

**官方给的两个「惯用模式工具」**：

**`mkEnableOption`**：

```nix
lib.mkEnableOption "magic"
  # is like
  lib.mkOption
  {
    type = lib.types.bool;
    default = false;
    example = true;
    description = "Whether to enable magic.";
  }
```

**`mkPackageOption`**：

```nix
mkPackageOption pkgs "name" {
  default = [ "path" "in" "pkgs" ];
  example = "literal example";
}
```

> **官方给 `mkPackageOption` 的理由（原文，很重要）**：
> *"**You should make package options for your modules, where applicable.** While one can always overwrite a specific package throughout nixpkgs by using **nixpkgs overlays, they slow down nixpkgs evaluation significantly and are harder to debug when issues arise.**"*

> [!IMPORTANT]
> **这一段是官方对「overlay vs 选项」的明确表态，直接影响本指南第十九/二十章的写法建议。**
>
> **官方的立场**：
> - ✅ **首选**：用模块暴露的 **package 选项**（如 `services.hermes.package = pkgsUnstable.hermes;`）
> - ⚠️ **次选**：`override` / `overrideAttrs`
> - ❌ **最后**：**`nixpkgs.overlays` / `nixpkgs.config.packageOverrides`**
>
> **官方给的理由**：overlay *"slow down nixpkgs evaluation significantly and are harder to debug"*。
>
> **这修正了本指南第二十章的一个隐含倾向** —— 那里把 overlay 作为「让某个包用 unstable」的方案之一列出。**按官方立场，应该优先用「模块的 package 选项」**：
> ```nix
> # ✅ 官方推荐：用模块的 package 选项
> services.hermes.package = pkgsUnstable.hermes;
>
> # ⚠️ 官方不推荐（但可用）：全局 overlay
> nixpkgs.overlays = [ (final: prev: { hermes = pkgsUnstable.hermes; }) ];
> ```

### 34.4 选项类型（`types.*`）

**官方定义（原文）**：

> *"Option types are a way to **put constraints on the values** a module option can take. **Types are also responsible of how values are merged in case of multiple value definitions.**"*

**官方给的关键类型（原文要点）**：

| 类型 | 官方说明 | 合并行为 |
|---|---|---|
| `types.bool` | *"A boolean... **All definitions must have the same value, after priorities. An error is thrown in case of a conflict.**"* | **冲突即报错** |
| `types.boolByOr` | *"The result is `true` if **any** of multiple definitions is true. In other words, definitions are merged with the **logical OR** operator."* | **OR 合并** |
| `types.path` | *"A filesystem path that **starts with a slash**. Even if derivations can be considered as paths, the more specific `types.package` should be preferred."* | — |
| `types.pathInStore` | *"A path that **is contained in the Nix store**. This can be a top-level store path like `pkgs.hello` or a descendant like `"${pkgs.hello}/bin/hello"`."* | — |
| **`types.externalPath`** | *"A path that is **not contained in the Nix store**. Typical use cases are: **secrets, password or any other external file**."* | — |
| `types.package` | *"A top-level store path. This can be an attribute set pointing to a store path, like a derivation or a flake input."* | — |
| `types.enum l` | *"One element of the list `l`... **Multiple definitions cannot be merged.**"* | **不可合并** |
| **`types.anything`** | *"A type that accepts any value and **recursively merges attribute sets** together. **This type is recommended when the option type is unknown.**"* | **递归合并** |

**★ 官方对 `types.externalPath` 的警告（原文，与安全直接相关）**：

> ⚠️ *"**This type only validates that the path is not currently in the Nix store. It does NOT prevent the value from being copied to the store later** when: Referenced in a derivation; Used in certain path operations (e.g., `${path}` interpolation); Passed to functions that copy to the store. **Users must still be careful about how they reference these paths.**"*

> [!DANGER]
> **这条警告直接关系到本指南反复强调的「凭据不落 Nix store」。**
>
> **官方明确说：`types.externalPath` 只做「当前不在 store 里」的校验，它挡不住你后面把路径插值进 derivation。**
>
> **具体场景**：
> ```nix
> # ❌ 你以为用了 externalPath 就安全了，但这一行会把 secret 复制进 store
> systemd.services.myapp.serviceConfig.EnvironmentFile = "${config.sops.secrets.mykey.path}";
> ```
> 实际上这一行**如果路径指向的是 store 外的文件，systemd 运行时读取，是安全的**。但如果写成：
> ```nix
> # ❌ 这会复制进 store
> systemd.services.myapp.serviceConfig.ExecStart = "${pkgs.myapp}/bin/app --key $(cat ${./my-secret})";
> ```
> **`${./my-secret}` 会把文件内容复制进 store。**
>
> **正确做法**（本指南 §16.4 / §21.x 的结论）：
> - 用 **sops-nix / agenix**，它们在 **activation 阶段**才把明文写到 `/run/secrets/`
> - systemd unit 里用 `EnvironmentFile = "/run/secrets/mykey"`（**运行时路径，不进 store**）
> - **绝不**在 Nix 表达式里 `${}` 插值 secret 文件

**`types.anything` 的官方例子（原文）**：

```nix
{
  str = lib.mkDefault "foo";
  pkg.hello = pkgs.hello;
  fun.fun = x: x + 1;
}
```
```nix
{
  str = lib.mkIf true "bar";
  pkg.gcc = pkgs.gcc;
  fun.fun = lib.mkForce (x: x + 2);
}
```
> *"will get merged to"*
```nix
{
  str = "bar";
  pkg.gcc = pkgs.gcc;
  pkg.hello = pkgs.hello;
  fun.fun = x: x + 2;
}
```

> [!TIP]
> **这个例子是理解「NixOS 选项怎么合并」的最好教材**。注意三件事：
> 1. **`str`**：`mkDefault "foo"`（优先级 1000）vs `mkIf true "bar"`（优先级 100）→ **后者赢**
> 2. **`pkg`**：两个**不同的键**（`hello` 和 `gcc`）→ **合并保留两者**（递归合并）
> 3. **`fun.fun`**：**同一个键**，`mkForce`（优先级 50）vs 普通（100）→ **mkForce 赢**
>
> **所以「合并」和「覆盖」的判据是「键是否相同」**，不是「是不是同一个选项」。**这解释了为什么 `environment.systemPackages` 是「追加」（列表类型）而 `networking.hostName` 是「覆盖」（字符串类型）。**

### 34.5 ★ 选项定义的优先级（精确数字）

**官方原文（逐字，本节最重要）**：

> *"A module can override the definitions of an option in other modules by setting an **override priority**. **All option definitions that do not have the lowest priority value are discarded.** By default, **option definitions have priority 100** and **option defaults have priority 1500**."*

> *"You can specify an explicit priority by using `mkOverride`, e.g. `{ services.openssh.enable = mkOverride 10 false; }`. **This definition causes all other definitions with priorities above 10 to be discarded.**"*

> *"**The function `mkForce` is equal to `mkOverride 50`, and `mkDefault` is equal to `mkOverride 1000`.**"*

**★ 官方给的「顺序优先级」（`mkOrder`，与「覆盖优先级」是两回事）**：

> *"It is also possible to influence **the order in which the definitions for an option are merged** by setting an **order priority** with `mkOrder`. The default order priority is **1000**. The functions **`mkBefore` and `mkAfter` are equal to `mkOrder 500` and `mkOrder 1500`**, respectively."*

**完整优先级表（本指南整理，数字越小越优先）**：

| 函数 | 优先级 | 语义 | 典型用途 |
|---|---|---|---|
| `mkOverride 10 ...` | **10** | 极高 | 罕见（强制覆盖一切） |
| **`mkForce v`** | **50** | **强制覆盖** | 官方模块默认不合意 |
| （普通赋值） | **100** | **默认优先级** | **99% 的情况** |
| `mkOverride 500 ...` | 500 | 中等 | 罕见 |
| **`mkDefault v`** | **1000** | **默认值**（可被覆盖） | 写模块时给合理默认 |
| （`mkOption` 的 `default`） | **1500** | **选项自带的默认** | 选项声明里 |
| `mkOverride 2000 ...` | 2000 | 低于默认 | 罕见 |

**顺序优先级（另一套数字，不要混）**：

| 函数 | 顺序优先级 | 语义 |
|---|---|---|
| **`mkBefore v`** | **500** | **排在前面**（列表合并时） |
| （普通） | **1000** | 默认 |
| **`mkAfter v`** | **1500** | **排在后面** |

> [!IMPORTANT]
> **「覆盖优先级」和「顺序优先级」是两套独立的东西 —— 这是最容易混淆的一点。**
>
> | | 覆盖优先级（`mkOverride` / `mkForce` / `mkDefault`） | 顺序优先级（`mkOrder` / `mkBefore` / `mkAfter`） |
> |---|---|---|
> | 管什么 | **谁的值赢** | **列表里谁在前** |
> | 默认值 | 100 | 1000 |
> | 只对列表类型有意义吗 | 不是（所有类型） | **是**（只影响合并顺序） |
> | 冲突时 | 数字最小的赢 | **不冲突，都保留** |
>
> **`mkBefore` 只影响「顺序」，不影响「是否保留」** —— 两个定义都会在列表里，只是顺序不同。
>
> **本指南 §26.5 引用官方 `mkBefore [ "kvm-intel" ]` 的例子** —— 那是**顺序**问题（内核模块加载顺序），**不是覆盖**问题。

> [!WARNING]
> **官方原文有个容易误读的地方**：*"All option definitions that do not have the lowest priority value are discarded."*
>
> **「lowest priority value」= 「最小的数字」**（因为数字越小越优先）。所以这句话的意思是：**数字最小的那个定义赢，其他的丢弃**。
>
> **不是「优先级最低的赢」** —— 英文的 "priority value" 在这里指「优先级数值」，而数值小 = 优先级高。**中文语境下容易读反。**

### 34.6 断言与警告（官方 `sec-assertions`）

**官方原文**：

> *"When configuration problems are detectable in a module, it is a good idea to write an **assertion or warning**. Doing so provides **clear feedback to the user and prevents errors after the build**."*

> *"Although Nix has the `abort` and `builtins.trace` functions to perform such tasks, **they are not ideally suited for NixOS modules**. Instead of these functions, you can declare your warnings and assertions using the **NixOS module system**."*

**官方的 warnings 例子**：

```nix
{ config, lib, ... }:
{
  config = lib.mkIf config.services.foo.enable {
    warnings =
      if config.services.foo.bar then
        [
          ''
            You have enabled the bar feature of the foo service.
                           This is known to cause some specific problems in certain situations.
          ''
        ]
      else
        [ ];
  };
}
```

**官方的 assertions 例子（来自 syslogd 模块）**：

```nix
{ config, lib, ... }:
{
  config = lib.mkIf config.services.syslogd.enable {
    assertions = [
      {
        assertion = !config.services.rsyslogd.enable;
        message = "rsyslogd conflicts with syslogd";
      }
    ];
  };
}
```

> **官方给的理由**：*"Since there can only be one active syslog daemon at a time, an assertion is useful to **prevent such a broken system from being built**."*

> [!IMPORTANT]
> **`warnings` 和 `assertions` 的区别，决定了你的配置是「能构建但有隐患」还是「根本构建不了」**：
>
> | | `warnings` | `assertions` |
> |---|---|---|
> | 效果 | **打印警告，继续构建** | **失败，拒绝构建** |
> | 适合 | 「你可能不想要这个」 | 「这两个选项互斥」 |
> | 官方例子 | 「开了 bar 特性会有已知问题」 | 「rsyslogd 与 syslogd 冲突」 |
>
> **你在本指南里已经见过几个断言的实际案例**：
> - **`services.flatpak` 要求 `xdg.portal.enable = true`**（§7.2）—— 断言，**直接求值失败**
> - **`home-manager.useGlobalPkgs = true` 时 `nixpkgs.*` 被禁用**（§24.5）—— 有断言 + warning
> - **Hermes 的 container 模式与 `backend.mode` 互斥**（§21.x）—— 硬断言
>
> **对「Agent 写模块」的实用价值**：**让 Agent 加断言，而不是加注释。**
> ```
> 提示词：请在模块里用 assertions 表达「这两个选项不能同时开」的约束，
>         用 warnings 表达「这样配会有已知问题」。
>         不要用 abort 或 builtins.trace。
> ```
> **理由**：断言会**阻止构建**（安全），而注释不会。**这是「把知识编码进配置」的正确方式。**

### 34.7 meta 属性

**官方原文**：

> *"Like Nix packages, NixOS modules can declare **meta-attributes** to provide extra information. Module meta attributes are defined in the `meta.nix` special module. `meta` is a **top level attribute like `options` and `config`**. Available meta-attributes are **`maintainers`, `doc`, and `buildDocsInSandbox`**. **Each of the meta-attributes must be defined at most once per module file.**"*

```nix
{
  config,
  lib,
  pkgs,
  ...
}:
{
  options = {
    # ...
  };
  # meta = { maintainers = [...]; doc = ./my-service.md; };
}
```

> [!TIP]
> **`meta.doc` 就是官方手册里那 300+ 个 `module-services-*` 章节的来源。** 官方在手册里说：*"These services are defined in Nixpkgs' `nixos/modules/` directory"*（`sect-nixos-systemd-nixos`）。
>
> **对你的实际意义**：**如果你自己写了一个模块并想让它有文档**，加 `meta.doc = ./my-service.md;`。这样 `nixos-rebuild` 生成的 manual 会包含它。
>
> **`maintainers`**：填 nixpkgs 的 maintainer 名（在 `maintainers/maintainer-list.nix` 里）。**`buildDocsInSandbox`**：控制文档构建是否在沙箱里跑。

### 34.8 替换模块（`disabledModules`）

**官方原文**：

> *"Modules that are imported can also be **disabled**. The option declarations, config implementation and the imports of a disabled module will be **ignored, allowing another to take its place**. This can be used to **import a set of modules from another channel while keeping the rest of the system on a stable release**."*

> *"`disabledModules` is a top level attribute like `imports`, `options` and `config`. It contains a list of modules that will be disabled. This can either be:"*
> - *"the full path to the module,"*
> - *"or a string with the filename relative to the modules path (eg. `<nixpkgs/nixos/modules>` for nixos),"*
> - *"or an attribute set containing a specific `key` attribute."*

**官方给的第一个例子（换掉 postgresql 模块）**：

```nix
{
  config,
  lib,
  pkgs,
  ...
}:

{
  disabledModules = [ "services/databases/postgresql.nix" ];

  imports = [
    # Use postgresql service from nixos-unstable channel.
    # sudo nix-channel --add https://channels.nixos.org/nixos-unstable nixos-unstable
    <nixos-unstable/nixos/modules/services/databases/postgresql.nix>
  ];

  services.postgresql.enable = true;
}
```

> **官方的重要限定（原文）**：*"This only **overrides the module definition**, this **won't use postgresql from nixos-unstable unless explicitly configured to do so**."*

> [!IMPORTANT]
> **最后那句限定非常重要 —— 它区分了「模块」和「包」。**
>
> | | 来自哪 | 怎么换 |
> |---|---|---|
> | **模块定义**（选项、systemd unit 长什么样） | `nixos/modules/...` | `disabledModules` + `imports` |
> | **包**（实际执行的二进制） | `pkgs` | `services.xxx.package = ...;` |
>
> **官方明确说：换模块不会自动换包。** 两者要**分别**指定。
>
> **对本指南第二十章的意义**：你想「用 unstable 的某个服务」时，**要换两样东西**：
> ```nix
> {
>   # 1. 模块（如果 stable 的模块有 bug 或版本旧）
>   disabledModules = [ "services/xxx.nix" ];
>   imports = [ "${pkgsUnstable.path}/nixos/modules/services/xxx.nix" ];
>
>   # 2. 包（这才是真正跑起来的二进制）
>   services.xxx.package = pkgsUnstable.xxx;
> }
> ```
> **大多数情况你只需要第 2 条。** 第 1 条只在「模块本身有问题」时才需要。

### 34.9 Freeform 模块与 `settings` 子模块

**官方对 freeform 的说明（原文）**：

> *"**Freeform modules** allow you to define values for option paths that have **not been declared explicitly**. This can be used to add attribute-specific types to what would otherwise have to be `attrsOf` options in order to accept all attribute names."*

> *"This feature can be enabled by using the attribute **`freeformType`** to define a freeform type. By doing this, **all assignments without an associated option will be merged using the freeform type** and combined into the resulting config set. **Since this feature nullifies name checking for entire option trees, it is only recommended for use in submodules.**"*

> [!IMPORTANT]
> **「nullifies name checking」—— freeform 会关掉选项名检查。这是它的代价。**
>
> **官方只推荐在 submodule 里用**（比如 `services.xxx.settings.<任意名>`）。
>
> **你在本指南里已经见过它的产物**：官方在 `sec-settings-options` 里讲的就是这个模式 —— 很多服务的 `settings` 选项允许你写任意键名，直接映射到该服务的配置文件格式。
>
> **对本指南第二十五章的意义**：**freeform 是「为什么有些选项写错了不报错」的原因之一。** 如果某个选项树是 freeform 的，你写错名字**不会得到「does not exist」**，而是**静默生成一个错的配置文件**。
>
> **判据**：查选项文档时看它是不是 `attribute set of ...`（freeform 的典型描述）。**是的话，写错名字不报错。**

### 34.10 让 Agent 写模块的正确姿势

**把前面九节串成一份「给 Agent 的提示词模板」**：

```markdown
请帮我写一个 NixOS 模块，要求如下：

1. **结构**：用官方的四段式结构（`imports` / `options` / `config` / 可选 `meta`）
2. **选项声明**：
   - 每个选项必须有 `type` 和 `description`
   - 开关类选项用 `lib.mkEnableOption "..."`
   - 包类选项用 `lib.mkPackageOption pkgs "..." { }`（不要让我用 overlay 换包）
   - 需要默认值的用 `default = ...`，但**不要**在选项声明里写死具体包
3. **选项定义**：
   - 条件逻辑用 `lib.mkIf`（**不要**用裸 `if`，会 infinite recursion）
   - 覆盖别人的默认用 `lib.mkDefault`，**不要用 `mkForce`**（除非我明确要求）
4. **systemd 服务**：
   - `ExecStart` 一律用 `pkgs.writeShellScript` 包裹，避免 `$VAR` 和空格转义问题
   - 必须写 `wantedBy`（否则不自启）
   - 加安全加固：`NoNewPrivileges` / `ProtectSystem` / `ProtectHome` / `ReadWritePaths`
5. **约束**：用 `assertions`（互斥）和 `warnings`（隐患）表达，**不要**用 `abort` / `builtins.trace`
6. **文件路径**：不要 `${}` 插值任何密钥文件

输出后请自己检查：
- 有没有 `if` 而不是 `mkIf`
- 有没有漏 `wantedBy`
- 有没有在 `ExecStart` 里直接写 `$` 变量
```

> [!TIP]
> **这份模板的每一条都对应本章或前文的一个真实坑。** 把它存起来，下次让 Agent 写模块时直接贴。
>
> **本指南第十章讲的「skills」概念，本质上就是把这种提示词固化成可复用的文件。** 本章给的是「写模块」这个具体场景的版本。

### 34.11 NixOS Tests（官方 `sec-nixos-tests`）

**官方原文（`sec-nixos-tests` 全节）**：

> *"NixOS has a **testing framework** that allows you to test the functionality of your NixOS configuration... "*

**官方给的测试结构（`sec-writing-nixos-tests` 的典型形态）**：

```nix
# 官方测试的典型骨架（本指南根据官方文档结构整理）
import ./make-test-python.nix ({ pkgs, ... }: {
  name = "my-test";
  nodes.machine = { ... }: {
    services.my-service.enable = true;
  };
  testScript = ''
    machine.wait_for_unit("my-service.service")
    machine.succeed("curl -s http://localhost/ | grep hello")
  '';
})
```

**官方的运行方式（`sec-running-nixos-tests`）**：

```bash
# 跑单个测试
nix-build nixos/tests/my-test.nix

# 交互式调试
nix-build nixos/tests/my-test.nix -A driverInteractive
./result/bin/nixos-test-driver
```

> [!NOTE]
> **NixOS Tests 对你的实际价值有限，但有一个例外值得知道：**
>
> **它是「在虚拟机里完整跑一遍 NixOS 配置」的官方工具。** 所以你可以：
> ```bash
> # 在 QEMU 里测试你的配置能不能启动（不用真机试错）
> nix-build '<nixpkgs/nixos>' -A vm -I nixos-config=/etc/nixos/configuration.nix
> ./result/bin/run-*-vm
> ```
>
> **这是「改存储/引导配置前先虚拟机验证」的官方方案** —— 比本指南 §27.6 建议的「`test` 而非 `switch`」更彻底（完全不动真机）。
>
> **代价**：需要 QEMU，且要下载/构建 VM 环境。**对「改 `boot.loader.*` 这种高风险配置」值得。**

### 34.12 六个反模式

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | 用裸 `if` 而不是 `mkIf` | **infinite recursion** | `config = lib.mkIf cond { ... };` |
| 2 | 动不动 `mkForce` | 覆盖别人默认，难排查 | 优先 `mkDefault` / 对应选项 |
| 3 | `ExecStart` 直接写 `$VAR` | systemd 展开/切分 → 启动失败 | `pkgs.writeShellScript` 包裹 |
| 4 | 用 overlay 换包 | **显著拖慢求值**，难调试（官方明确不推荐） | 用模块的 `package` 选项 |
| 5 | 用 `abort` / `builtins.trace` | 不适合 NixOS 模块 | `assertions` / `warnings` |
| 6 | 在 Nix 表达式里 `${}` 插值密钥 | **密钥进 store**，全局可读 | sops-nix / agenix + `/run/secrets/` |

> [!TIP]
> **本章的一句话总结**：
> **模块 = `{ config, pkgs, ... }: { imports; options; config; }`。**
> **优先级：`mkForce`(50) < 普通(100) < `mkDefault`(1000) < 选项 default(1500)。**
> **顺序：`mkBefore`(500) < 普通(1000) < `mkAfter`(1500)。**
> **条件用 `mkIf`，约束用 `assertions`，命令用 `writeShellScript`。**
>
> 记住这四行，你就能读懂 90% 的 NixOS 模块。

---

---

## 三十五、构建镜像：Live ISO、repart 与 Appliance（官方 Part I · Installation 缺口）

本章补的是官方手册 **Part I** 的最后一批章节：`sec-upgrading`、`sec-upgrading-automatic`、`sec-building-image`、`sec-image-nixos-rebuild-build-image`、`sec-image-repart`、`sec-image-repart-store-paths`、`sec-image-repart-appliance`。

**为什么把「构建镜像」放在最后一章**：

> [!IMPORTANT]
> **这不是「日常必读」章节。** 本指南前三十四章讲的是「**用** NixOS」；本章讲的是「**造** NixOS」。
>
> **但你有两个真实场景会用到它**：
> 1. **给第二台机器装机，想带上自己的配置** —— 官方 Live ISO 装完还要重跑一遍 `nixos-rebuild`，直接做一张「预装好我的配置」的 U 盘更快。
> 2. **给 Agent 一个可回滚的实验环境** —— 构建一个 QEMU 镜像，让 Agent 在里面随便改配置，炸了重来，不动真机。
>
> **官方在这一块有一个明确的态度**（见 §35.6）：**「NixOS 的 generation 更新机制不适合 appliance」** —— 这句话解释了为什么本章最后一节讲的是「整镜像替换 / A/B 分区」，而不是 `nixos-rebuild`。

---

### 35.1 频道与升级：先把「基座」这件事说清

**官方章节名**：`sec-upgrading`（Upgrading NixOS）、`sec-upgrading-automatic`（Automatic Upgrades）。

**官方原文（`sec-upgrading`）**：

> *"The NixOS channels are updated as soon as possible after a new version is released. … These channels are:*
> - *Stable channels, such as `nixos-26.05`.*
> - *The unstable channel, `nixos-unstable`.*
> - *Small channels, such as `nixos-26.05-small`.*"

**官方对三类频道的完整定义**：

| 频道类型 | 例子 | 官方描述要点 |
|---|---|---|
| **Stable** | `nixos-26.05` | 保守更新。**但 channel 更新仍可能导致内核等组件变化**；一般维护到下一个 stable 发布后一段时间 |
| **Unstable** | `nixos-unstable` | 滚动。官方原文：*"It's not recommended for"* 生产/日常（**更新之间可能有激进变化**） |
| **Small** | `nixos-26.05-small` | 与 stable/unstable **内容完全相同**，只是**更新频率更低**；官方推荐服务器用（**关键安全补丁会更快推送**——注意这句官方原文语义是「小频道会在关键补丁时被单独快推」） |

> [!WARNING]
> **官方原文里有一个反直觉的点**：
> *"These are identical to the stable and unstable channels described above, except that they are only updated … faster than the regular channels (for instance, when a critical security patch …)"*
>
> 这句话在官方手册里读起来像自相矛盾（「更少更新」+「更快」）。**正确的理解是**：小频道**常规节奏更慢**（少收无关变更），**但关键安全补丁会被单独加速推送**。
>
> **对你的实际建议**：**桌面用户不要用小频道**。小频道的价值在「服务器不想天天被无关更新打扰，但安全补丁要及时」。

**查自己当前订阅哪个频道**：

```bash
nix-channel --list | grep nixos
# 输出示例（官方原文给的例子）：
# nixos https://channels.nixos.org/nixos-unstable
```

**切换频道**：

```bash
# 通用格式（★ 末尾的 nixos 参数不能省）
sudo nix-channel --add https://channels.nixos.org/<channel-name> nixos

# 切到 26.05 stable
sudo nix-channel --add https://channels.nixos.org/nixos-26.05 nixos

# 切到 small（服务器）
sudo nix-channel --add https://channels.nixos.org/nixos-26.05-small nixos

# 切到 unstable
sudo nix-channel --add https://channels.nixos.org/nixos-unstable nixos
```

**升级到当前频道最新**：

```bash
sudo nixos-rebuild switch --upgrade
# 官方原文：等价于更啰嗦的
#   sudo nix-channel --update nixos; sudo nixos-rebuild switch
```

> [!NOTE]
> **官方两条关键提醒**：
>
> **① 频道是「按用户」设置的**（*"Channels are set per user"*）：
> *"running `nix-channel --add` as a non root user (or without `sudo`) will not affect configuration in `/etc/nixos/configuration.nix`"*
> → **不加 `sudo` 就只影响你自己的用户频道，不影响系统**。这是个「命令静默成功但没生效」的经典坑。
>
> **② 频道来回切换是安全的，只有一个例外**（官方原文）：
> *"The only exception is that a newer NixOS may also have a newer Nix version, which may involve an upgrade of Nix's database schema. This cannot be undone easily, so in that case you will not be able to go back to your original channel."*
> → **Nix 数据库 schema 升级后不能回退频道**。**升到 unstable 前请三思**。
> → 这条也是本指南 §30.8「回滚」的一个边界：**generation 能回滚，但 Nix DB schema 不能**。

**自动升级**（官方 `sec-upgrading-automatic`）：

```nix
{
  system.autoUpgrade.enable = true;
  system.autoUpgrade.allowReboot = true;
}
```

**官方对这两个选项的完整解释**：

| 选项 | 值 | 官方原文语义 |
|---|---|---|
| `system.autoUpgrade.enable` | `true` | 启用一个**周期性执行的 systemd 服务**，名为 **`nixos-upgrade.service`** |
| `system.autoUpgrade.allowReboot` | `false` | 运行 `nixos-rebuild switch --upgrade` —— 升级到当前频道最新 |
| `system.autoUpgrade.allowReboot` | `true` | **如果新 generation 包含不同的内核、initrd 或内核模块，系统会自动重启** |

**看它什么时候跑**（官方原文提示）：`systemctl list-timers`（本指南 §29.2）。

**显式指定频道**（官方给的例子）：

```nix
{ system.autoUpgrade.channel = "https://channels.nixos.org/nixos-26.05"; }
```

> [!DANGER]
> **`system.autoUpgrade.allowReboot = true` 对桌面用户是有风险的**。
>
> 官方原文只说「如果新 generation 包含不同的内核/initrd/内核模块就自动重启」。**没有说**：
> - 会不会在你有未保存的工作时重启
> - 会不会中断正在进行的游戏/编译
>
> **本指南建议**（结合 §29.8 与 §30.1）：
> ```nix
> system.autoUpgrade = {
>   enable = true;
>   allowReboot = false;        # 只升级，不自动重启
>   # 让它在你不用电脑的时间跑（默认是每天固定时间，可用 flake 或
>   # systemd.services.nixos-upgrade 覆写）
> };
> ```
> **重启这件事交给 `nixos-rebuild boot` + 你自己挑时间。**
> **服务器**（无人值守）才用 `allowReboot = true`。

> [!TIP]
> **一个官方没写、但你会遇到的问题**：`system.autoUpgrade` 在 **flake 模式下语义不同**。
>
> - **channel 模式**：`system.autoUpgrade.enable = true` 会去更新 channel 然后 rebuild。
> - **flake 模式**（`/etc/nixos/flake.nix`）：它会先跑 `nix flake update` 再 rebuild（取决于 `system.autoUpgrade.flake` 选项，默认取当前 flake）。
>
> **如果你用的是 flake，本指南第二十二章的「定时 `flake update` + rebuild」方案更可控** —— 因为它把「更新锁文件」和「应用锁文件」分成两步，你能先看 diff。

---

### 35.2 构建 Live ISO

**官方章节名**：`sec-building-image`（Building a NixOS (Live) ISO）。

**官方原文**：

> *"Default live installer configurations are available inside `nixos/modules/installer/cd-dvd`. For building other system images, see Building Images with nixos-rebuild build-image. **You have two options:***
> - *Use any of those default configurations as is*
> - *Combine them with (any of) your host config(s)*"

**官方原文（关键限制）**：

> *"System images, such as the live installer ones, **know how to enforce configuration settings on which they immediately depend in order to work correctly**. However, if you are confident, you can opt to override those enforced values with `mkForce`."*

> [!IMPORTANT]
> **上面这句官方原文解释了一个很多人踩过的坑**：
>
> **Live ISO 的配置里有一批「它自己强制设定」的值** —— 因为不设就装不起来（比如「必须能联网」「必须有安装器界面」）。
>
> **当你想「把我的 `configuration.nix` 塞进 ISO」时，你的值会和它的强制值冲突**。官方给的路是：**明确用 `mkForce` 覆盖**。
>
> **官方原文的语气是「if you are confident」** —— 意思是**它不推荐你随便覆盖**，覆盖错了 ISO 就不工作。

**两条官方路径的具体做法**：

**路径 A：直接用官方默认配置**（最安全）

```bash
# 官方默认配置在 nixpkgs 里的位置
#   nixos/modules/installer/cd-dvd/
# 典型文件：
#   iso-image.nix          # 完整图形 Live ISO
#   iso-image-new-kernel.nix
#   installation-cd-graphical-*.nix

# 直接构建（channel 模式下）
nix-build '<nixpkgs/nixos>' -A config.system.build.isoImage \
  -I nixos-config='<nixpkgs/nixos/modules/installer/cd-dvd/iso-image.nix>'

# 结果在 ./result/iso/*.iso
```

**路径 B：把自己的配置和官方配置合并**（官方说的 "Combine them with your host config"）

```nix
# my-iso.nix
{ config, pkgs, lib, modulesPath, ... }:

{
  imports = [
    # ① 先引入官方 ISO 配置（提供安装器界面、联网等强制设定）
    "${modulesPath}/installer/cd-dvd/iso-image.nix"

    # ② 再引入你自己的主机配置
    /etc/nixos/configuration.nix
  ];

  # ③ 冲突的地方用 mkForce 明确覆盖（官方原文的 "if you are confident"）
  # 例如：官方 ISO 可能禁用了某些服务，你想开
  # services.openssh.enable = lib.mkForce true;

  # ④ 加上你每次装机后都要手动做的事，让它预置好
  environment.systemPackages = with pkgs; [
    git
    vim
    # ...
  ];
}
```

构建：

```bash
nix-build '<nixpkgs/nixos>' -A config.system.build.isoImage -I nixos-config=./my-iso.nix
```

> [!TIP]
> **给「想预装自己配置」的用户一个更省事的做法**（官方没写，但符合官方机制）：
>
> **不要把自己的 `configuration.nix` 全塞进 ISO。** 而是：
> 1. 构建一个**最小改动**的 ISO（只加 `git` + 你的 SSH 公钥 + 你的 flake 仓库地址）
> 2. 装机时 `git clone` 你的 flake 再 `nixos-rebuild switch --flake`
>
> **理由**：
> - ISO 里的 `configuration.nix` 和你日常维护的那份**会漂移**（ISO 是一次性快照，日常配置在持续更新）
> - 你的配置里如果有 **硬件相关**（`fileSystems`、`boot.loader`），塞进 ISO 会**和装机时探测到的磁盘布局冲突**
> - 这也是官方 `clone-config` profile 的思路（本指南 §26.8）

> [!NOTE]
> **`iso-image.nix` 里的「强制设定」到底有哪些**（本指南的推断，标注为推断）：
>
> 从官方原文 *"know how to enforce configuration settings on which they immediately depend in order to work correctly"* 反推，至少包括：
> - 安装器本身（`services.xserver` / 图形安装器）
> - 网络栈（不联网就装不了）
> - `nixpkgs.config.allowUnfree`（要装闭源固件）
> - 安装器用的 `users`（Live 环境的 `nixos` 用户）
>
> **具体清单请查源码**（§34.1 的方式 4）：
> ```bash
> curl -s https://raw.githubusercontent.com/NixOS/nixpkgs/nixos-26.05/nixos/modules/installer/cd-dvd/iso-image.nix
> ```

---

### 35.3 用 `nixos-rebuild build-image` 构建云/虚拟化镜像

**官方章节名**：`sec-image-nixos-rebuild-build-image`（Building Images with `nixos-rebuild build-image`）。

**官方原文**：

> *"Nixpkgs contains a variety of modules to build custom images for different virtualization platforms and cloud providers, such as e.g. `amazon-image.nix` and `proxmox-lxc.nix`. While those can be imported directly, **`system.build.images` provides an attribute set mapping variant names to image derivations**. Available variants are defined - and extendable - in **`image.modules`**, an attribute set mapping variant names to NixOS modules.*
>
> *All of those images can be built via both, their **`system.build.image`** attribute and the **`nixos-rebuild build-image`** command."*

**官方给的完整例子**（构建 Amazon 镜像）：

```bash
nixos-rebuild build-image --image-variant amazon
# [...]
# Done. The disk image can be found in
#   /nix/store/[hash]-nixos-image-amazon-25.05pre-git-x86_64-linux/nixos-image-amazon-25.05pre-git-x86_64-linux.vpc
```

**列所有可用变体**（官方原文）：*"To get a list of all variants available, run `nixos-rebuild build-image` without arguments."*

```bash
nixos-rebuild build-image
# 不加参数 → 列出全部可用 variant
```

> [!TIP]
> **这是本章最实用的一个命令。** 它让你不写一行 Nix 就能列出：
> - `amazon`（EC2 AMI）
> - `proxmox-lxc`（Proxmox 容器）
> - `azure` / `gce` / `do`（各云）
> - `sd-image`（树莓派等 ARM 单板）
> - `iso`（Live ISO）
> - ……
>
> **先跑这个命令看有什么，再决定要不要自己写。**

**按变体覆写选项**（官方 Example 5，原文标题 *"Customize specific image variants"*）：

> *"The `image.modules` option can be used to set specific options per image variant, in a similar fashion as **`specialisations`** for generic NixOS configurations. E.g. images for the cloud provider **Linode** use **grub2 as a bootloader** by default. If you are using systemd-boot on other platforms and want to disable it for Linode only, you could use the following options:"*

```nix
{
  image.modules.linode = {
    boot.loader.systemd-boot.enable = lib.mkForce false;
  };
}
```

> [!IMPORTANT]
> **官方这段原文里有三个可迁移的概念**：
>
> | 概念 | 含义 | 类比你已知的 |
> |---|---|---|
> | **`image.modules.<variant>`** | 按变体覆写配置 | **`specialisations`**（官方自己做的类比） |
> | **`system.build.images.<variant>`** | 属性集：变体名 → 镜像 derivation | 和 `system.build.toplevel` 同一层级 |
> | **`image.modules`** | 属性集：变体名 → NixOS 模块 | **可扩展**（官方原文 *"extendable"*）—— 你可以加自己的变体 |
>
> **`mkForce` 在这里为什么必须**：官方说 Linode 镜像**默认用 grub2**。如果你只是写 `boot.loader.systemd-boot.enable = false;` 那是对的；但如果你想**在别处已经开了 systemd-boot**，再关就需要 `mkForce`（因为两个都是普通赋值 → 冲突报错，见 §34.5）。
>
> **注意官方例子写的是 `lib.mkForce false`** —— 用的是 **`lib.mkForce`**，不是裸 `mkForce`。在模块函数参数里 `lib` 更明确。

> [!NOTE]
> **`specialisations` 是什么**（本指南的补充说明）：
>
> 它是 NixOS 的「**同一台机器的多个配置变体**」机制 —— 生成多个 boot entry，开机时选。官方原文用「in a similar fashion as specialisations」来做类比，说明 **`image.modules` 的语义就是「同一份配置的多个变体」**，只不过变体不是「开机菜单项」而是「不同的镜像」。
>
> **对游戏玩家的实际用途**：你完全可以用 `specialisations` 做「日常配置」和「纯游戏配置（关掉所有服务、只留 Steam）」两个 boot entry。**这是本指南没有展开、但官方支持的用法。**

---

### 35.4 用 `systemd-repart` 构建磁盘镜像

**官方章节名**：`sec-image-repart`（Building Images via `systemd-repart`）。

**官方原文**：

> *"You can build disk images in NixOS with the **`image.repart`** option provided by the module **`image/repart.nix`**. This module uses **`systemd-repart`** to build the images and **exposes its entire interface via the `repartConfig` option**."*

**官方给的完整骨架**：

```nix
{ config, modulesPath, ... }:
{

  imports = [ "${modulesPath}/image/repart.nix" ];

  image.repart = {
    name = "image";
    partitions = {
      "esp" = {
        contents = {
          # ...
        };
        repartConfig = {
          Type = "esp";
          # ...
        };
      };
      "root" = {
        storePaths = [ config.system.build.toplevel ];
        repartConfig = {
          Type = "root";
          Label = "nixos";
          # ...
        };
      };
    };
  };

}
```

**三个属性的语义**（从官方原文 + 例子反推）：

| 属性 | 官方语义 | 值的形式 |
|---|---|---|
| `image.repart.name` | 镜像名（用于输出文件名） | 字符串，如 `"image"` |
| `image.repart.partitions.<名字>` | **一个分区** | 属性集 |
| `partitions.<n>.contents` | **往分区里放的「文件路径 → 来源」映射** | 属性集，如 `"/EFI/BOOT/BOOTX64.EFI".source = "...";` |
| `partitions.<n>.storePaths` | **往分区里放的 Nix store 路径** | 列表，通常是 `[ config.system.build.toplevel ]` |
| `partitions.<n>.repartConfig` | **直接透传给 `systemd-repart`** | 属性集（官方原文 *"exposes its entire interface"*） |
| `partitions.<n>.nixStorePrefix` | **重写 store 路径前缀**（见 §35.5） | 字符串 |

> [!IMPORTANT]
> **`repartConfig` 是「整个 `systemd-repart` 接口的透传」** —— 这意味着：
>
> **官方手册不会列出所有可用键。** 你要查的是 **`systemd-repart` 自己的文档**：
> ```bash
> man systemd-repart
> # 或
> man repart.d
> ```
>
> **常用键**（从官方各例子里出现的）：
> | 键 | 值示例 | 作用 |
> |---|---|---|
> | `Type` | `"esp"` / `"root"` / `"linux-generic"` | 分区类型（GPT type UUID 的别名） |
> | `Format` | `"vfat"` / `"ext4"` / `"btrfs"` | 文件系统格式 |
> | `Label` | `"nixos"` / `"nix-store"` | 分区标签（**决定 `/dev/disk/by-label/` 的名字**） |
> | `SizeMinBytes` | `"96M"` | 最小尺寸（**字符串，带单位**） |
> | `Minimize` | `"guess"` | 自动缩到最小 |
> | `Subvolumes` | `"/@ /@nix-store"` | Btrfs 子卷（**空格分隔字符串**） |
> | `MakeDirectories` | `"/@ /@nix-store"` | 预先创建目录/子卷 |
>
> **注意 `SizeMinBytes` 是字符串 `"96M"` 而不是数字** —— `systemd-repart` 接受带单位的值，Nix 里必须写成字符串（否则 `96M` 不是合法 Nix 数字）。

**为什么 `root` 分区要 `storePaths = [ config.system.build.toplevel ]`**：

`config.system.build.toplevel` 是**整个系统的闭包根**（本指南 §30.3 讲的 GC root 概念）。把它的 store 路径复制进分区，就等于**把整个系统装进了镜像** —— 不需要 `nixos-install`，开箱即用。

> [!TIP]
> **`image.repart` vs `nixos-rebuild build-image` 的分工**（本指南的归纳）：
>
> | | `nixos-rebuild build-image --image-variant X` | `image.repart` |
> |---|---|---|
> | 面向 | **已有平台的预设变体**（AWS/Proxmox/树莓派…） | **完全自定义的分区布局** |
> | 分区布局 | 变体模块写死 | **你自己写** |
> | 适合 | 「我要一个能上云/能进 Proxmox 的镜像」 | 「我要一个特定分区表的 U 盘/固件镜像」 |
> | 学习成本 | 零（一个命令） | 中（要懂 GPT 分区类型） |
>
> **先用 §35.3 的 `nixos-rebuild build-image` 列变体**，只有「变体列表里没有我想要的」才动手写 `image.repart`。

---

### 35.5 Nix Store Paths：分区与 Btrfs 子卷

**官方章节名**：`sec-image-repart-store-paths`（Nix Store Paths）。

**官方原文（总述）**：

> *"If you want to **rewrite Nix store paths**, e.g., to **remove the `/nix/store` prefix** or to **nest it below a parent path**, you can do that through the **`nixStorePrefix`** option."*

**官方给的两种用法**：

#### 用法 1：Nix Store 独立分区

**官方原文**：

> *"You can define a partition that only contains the Nix store and then mount it under `/nix/store`. Because the `/nix/store` part of the paths is already determined by the mount point, you have to set **`nixStorePrefix = "/"`** so that `/nix/store` is stripped from the paths before copying them into the image."*

```nix
{
  fileSystems."/nix/store".device = "/dev/disk/by-partlabel/nix-store";

  image.repart.partitions = {
    "store" = {
      storePaths = [ config.system.build.toplevel ];
      nixStorePrefix = "/";
      repartConfig = {
        Type = "linux-generic";
        Label = "nix-store";
        # ...
      };
    };
  };
}
```

**为什么必须 `nixStorePrefix = "/"`**（官方原文的逻辑链）：

1. store 路径长这样：`/nix/store/abc123-hello-2.12/bin/hello`
2. 你把分区挂到 `/nix/store`
3. 如果原样复制，分区里会有 `/nix/store/nix/store/abc123-...` —— **多了一层**
4. 所以要把 `/nix/store` 从路径里剥掉 → `nixStorePrefix = "/"` 表示「剥掉 `/nix/store` 后，路径以 `/` 开头」

> [!IMPORTANT]
> **`nixStorePrefix` 的取值语义（本指南的精确化）**：
>
> | 值 | 含义 | 分区里实际路径 |
> |---|---|---|
> | **默认**（不设） | 不重写 | `nix/store/abc123-...` |
> | **`"/"`** | 剥掉 `/nix/store` 前缀 | `abc123-...`（相对挂载点） |
> | **`"/@nix-store"`** | 剥掉 `/nix/store`，改挂到 `@nix-store` 子卷下 | `@nix-store/abc123-...` |
>
> **注意 `Label = "nix-store"` 和 `nixStorePrefix = "/"` 是两件不同的事**：
> - `Label` → 决定 `/dev/disk/by-label/nix-store` 这个名字（**你在 `fileSystems` 里引用的就是它**）
> - `nixStorePrefix` → 决定**复制进分区时路径怎么变**

#### 用法 2：Nix Store 作为 Btrfs 子卷

**官方原文**：

> *"Alternatively, you can create a Btrfs subvolume `/@nix-store` containing the Nix store and mount it on `/nix/store`:"*

```nix
{
  fileSystems."/" = {
    device = "/dev/disk/by-partlabel/root";
    fsType = "btrfs";
    options = [ "subvol=/@" ];
  };

  fileSystems."/nix/store" = {
    device = "/dev/disk/by-partlabel/root";
    fsType = "btrfs";
    options = [ "subvol=/@nix-store" ];
  };

  image.repart.partitions = {
    "root" = {
      storePaths = [ config.system.build.toplevel ];
      nixStorePrefix = "/@nix-store";
      repartConfig = {
        Type = "root";
        Label = "root";
        Format = "btrfs";
        Subvolumes = "/@ /@nix-store";
        MakeDirectories = "/@ /@nix-store";
        # ...
      };
    };
  };
}
```

**逐行解释（本指南的补充）**：

| 行 | 作用 |
|---|---|
| `fileSystems."/"` 用 `subvol=/@` | 根文件系统 = `root` 分区的 `@` 子卷 |
| `fileSystems."/nix/store"` 用 `subvol=/@nix-store` | **同一分区**，但挂 `@nix-store` 子卷 |
| `nixStorePrefix = "/@nix-store"` | 复制时把 `/nix/store/abc` 变成 `@nix-store/abc`（落到对应子卷） |
| `repartConfig.Subvolumes` | **告诉 `systemd-repart` 要建哪些子卷**（**空格分隔**） |
| `repartConfig.MakeDirectories` | 预创建这些目录/子卷（**同上，空格分隔**） |

> [!WARNING]
> **Btrfs 子卷方案里，`Subvolumes` 和 `MakeDirectories` 都必须写，且都写同样的值。**
>
> 官方例子两个都写了 `"/@ /@nix-store"`。**只写一个会导致镜像构建出来但挂不上**（本指南 §27.1 讲过：`fileSystems` 挂不上 = **掉 emergency shell**，不是警告）。
>
> **另外注意是「空格分隔的单个字符串」而不是 Nix 列表** —— `Subvolumes = [ "/@" "/@nix-store" ]` 是**错的**（`systemd-repart` 要字符串）。这和本指南 §26.1 讲的「Nix 列表用空格分隔」是不同层面的两件事：**这里是 `systemd-repart` 自己的配置语法要求字符串**。

> [!TIP]
> **为什么要在镜像里把 Nix store 分出来**（本指南补充的实际理由）：
>
> | 好处 | 说明 |
> |---|---|
> | **A/B 更新更干净** | 系统分区和 store 分区可以独立替换（见 §35.6） |
> | **只读挂载更简单** | store 分区可以整个 `ro` 挂载，防误写 |
> | **重装系统不丢下载** | 换根分区时 store 分区能保留 → 不用重新下载 |
> | **对齐 `system.etc.overlay` 思路** | 本指南 §33.8：NixOS 的「配置与数据分离」哲学一以贯之 |
>
> **对桌面用户的建议**：**默认的「store 和 root 同一分区」就够**。分出来是给「要做 appliance / A/B 更新」的场景用的。

---

### 35.6 Appliance 镜像：UKI + 无 `configuration.nix`

**官方章节名**：`sec-image-repart-appliance`（Appliance Image）。

**官方原文（本节最重要的一段）**：

> *"The `image/repart.nix` module can also be used to build self-contained software appliances. **The generation based update mechanism of NixOS is not suited for appliances.** Updates of appliances are usually either performed by **replacing the entire image** with a new one or by **updating partitions via an A/B scheme**. See the **Chrome OS update process** for an example of how to achieve this. **The appliance image built in the following example does not contain a `configuration.nix` and thus you will not be able to call `nixos-rebuild` from this system.** Furthermore, it **uses a Unified Kernel Image**."*

> [!IMPORTANT]
> **这段官方原文回答了一个你可能一直在想的问题：「为什么有些 NixOS 系统没有 `nixos-rebuild`？」**
>
> 三个关键点：
>
> | 官方原话 | 含义 | 本指南的对应 |
> |---|---|---|
> | *"generation based update mechanism … is not suited for appliances"* | **generation 机制不适合 appliance** | 见 §33.10「不可切换系统」 |
> | *"replacing the entire image"* | 更新 = **换整个镜像** | 类似手机刷固件 |
> | *"updating partitions via an A/B scheme"* | 或 **A/B 分区**（交替写） | 官方点名 **Chrome OS 更新流程** |
> | *"does not contain a `configuration.nix`"* | **没有 `configuration.nix`** | → **不能 `nixos-rebuild`** |
> | *"uses a Unified Kernel Image"* | 用 **UKI** | 内核+initrd+cmdline 打包成单个 EFI 可执行文件 |
>
> **这就是 `image-based-appliance` profile 的实现方式**（本指南 §26.8 提到的官方 11 个 profile 之一）。
>
> **对你的意义**：**不要给你的桌面机做 appliance 镜像**。桌面机要的就是 generation 回滚能力（§30.8）。**appliance 是给「出厂固件的设备」用的**。

**官方给的完整例子（逐字）**：

```nix
let
  pkgs = import <nixpkgs> { };
  efiArch = pkgs.stdenv.hostPlatform.efiArch;
in
(pkgs.nixos [
  (
    {
      config,
      lib,
      pkgs,
      modulesPath,
      ...
    }:
    {

      imports = [ "${modulesPath}/image/repart.nix" ];

      boot.loader.grub.enable = false;

      fileSystems."/".device = "/dev/disk/by-label/nixos";

      image.repart = {
        name = "image";
        partitions = {
          "esp" = {
            contents = {
              "/EFI/BOOT/BOOT${lib.toUpper efiArch}.EFI".source =
                "${pkgs.systemd}/lib/systemd/boot/efi/systemd-boot${efiArch}.efi";

              "/EFI/Linux/${config.system.boot.loader.ukiFile}".source =
                "${config.system.build.uki}/${config.system.boot.loader.ukiFile}";
            };
            repartConfig = {
              Type = "esp";
              Format = "vfat";
              SizeMinBytes = "96M";
            };
          };
          "root" = {
            storePaths = [ config.system.build.toplevel ];
            repartConfig = {
              Type = "root";
              Format = "ext4";
              Label = "nixos";
              Minimize = "guess";
            };
          };
        };
      };

    }
  )
]).image
```

**逐块拆解**：

**① 外层是「用 `pkgs.nixos` 现场求值一个配置」，不是 `nixosSystem`**

```nix
let
  pkgs = import <nixpkgs> { };
  efiArch = pkgs.stdenv.hostPlatform.efiArch;
in
(pkgs.nixos [ /* 模块列表 */ ]).image
```

| 部分 | 作用 |
|---|---|
| `import <nixpkgs> { }` | 取 nixpkgs（**这里没传 `system`，用当前平台**） |
| `pkgs.stdenv.hostPlatform.efiArch` | 取 **EFI 架构名**（x86_64 上是 `"x64"`，aarch64 上是 `"aa64"`）—— **所以文件名是 `BOOTX64.EFI` 或 `BOOTAA64.EFI`** |
| `pkgs.nixos [ ... ]` | **用 nixpkgs 自带的 `nixos` 函数**求值一个 NixOS 配置（不需要 `flake.nix`） |
| `.image` | 取 `system.build.image`（§35.3 讲过）—— 直接得到镜像 derivation |

**② `boot.loader.grub.enable = false;`**

> **为什么关 GRUB**：**UKI 由固件直接引导**（systemd-boot 作为 EFI 程序放在 `BOOTX64.EFI`）。GRUB 在这里是多余的一层。
>
> 这也是本指南 §33.9 讲的 **Bootspec** 的用武之地 —— UKI 路径从 `config.system.boot.loader.ukiFile` 读。

**③ ESP 分区放两个文件**

```nix
contents = {
  "/EFI/BOOT/BOOT${lib.toUpper efiArch}.EFI".source =
    "${pkgs.systemd}/lib/systemd/boot/efi/systemd-boot${efiArch}.efi";

  "/EFI/Linux/${config.system.boot.loader.ukiFile}".source =
    "${config.system.build.uki}/${config.system.boot.loader.ukiFile}";
};
```

| 目标路径 | 来源 | 说明 |
|---|---|---|
| `/EFI/BOOT/BOOTX64.EFI` | `pkgs.systemd` 里的 **systemd-boot** | **UEFI 规范的「fallback 路径」** —— 固件找不到启动项时会自动执行这个 |
| `/EFI/Linux/<ukiFile>` | **`config.system.build.uki`** | **UKI 放在 `/EFI/Linux/` 是 systemd-boot 的约定** —— 会被自动识别为可启动项 |

> [!TIP]
> **`lib.toUpper efiArch` 是为什么**：
> - `efiArch` 的值是**小写**：`"x64"` / `"aa64"`
> - UEFI fallback 文件名要求**大写**：`BOOTX64.EFI` / `BOOTAA64.EFI`
> - 但 `systemd-boot${efiArch}.efi` 的源文件名是**小写**：`systemd-bootx64.efi`
>
> **所以同一个 `efiArch` 变量被用了三次**：大写用于文件名，小写用于源路径。**这是这个例子最容易抄错的地方。**

**④ root 分区**

```nix
"root" = {
  storePaths = [ config.system.build.toplevel ];
  repartConfig = {
    Type = "root";
    Format = "ext4";
    Label = "nixos";
    Minimize = "guess";
  };
};
```

| 键 | 值 | 说明 |
|---|---|---|
| `Format = "ext4"` | ext4 | 最简选择；想 Btrfs 见 §35.5 |
| `Label = "nixos"` | **和 `fileSystems."/".device = "/dev/disk/by-label/nixos"` 对应** | ★ **这两个必须一致** |
| `Minimize = "guess"` | 自动缩到最小 | 镜像体积优化（**`"guess"` 让 `systemd-repart` 自己估算**） |

> [!DANGER]
> **`Label` 和 `fileSystems."/".device` 必须严格对应。**
>
> ```nix
> fileSystems."/".device = "/dev/disk/by-label/nixos";
> #                                     ^^^^^ 必须等于
> repartConfig.Label = "nixos";
> #                    ^^^^^
> ```
>
> **不一致的后果**：镜像构建成功，但**开机挂不上根分区 → 掉 emergency shell**（本指南 §27.1）。
>
> **这是 appliance 例子最危险的一处** —— 因为 `nixos-rebuild build-image` 不会检查这个对应关系，它只保证分区被正确创建。

**构建它**（因为外层是 `pkgs.nixos`，不是一个 NixOS 配置，所以用 `nix-build`）：

```bash
# 存成 appliance.nix，然后
nix-build appliance.nix
# 结果：./result/nixos-image-*.raw（或 .img）
```

> [!NOTE]
> **为什么这个例子「不能 `nixos-rebuild`」**（官方原文 *"does not contain a `configuration.nix`"*）：
>
> `nixos-rebuild` 的工作方式是：
> 1. 读 `/etc/nixos/configuration.nix`
> 2. 求值成一个新的 `toplevel`
> 3. 调 `switch-to-configuration` 切换（§33.5 的 12 步）
>
> **appliance 镜像里这三步的输入（`configuration.nix`）根本不存在** —— 镜像里只有「求值结果」（toplevel）。
>
> **这带来两个后果**：
> | 后果 | 说明 |
> |---|---|
> | **不能原地升级** | 要升级必须**换整个镜像**或 **A/B 分区**（官方原文） |
> | **但更小、更安全** | 没有 Nix 工具链、没有编译器、攻击面小（本指南 §33.10 讲的 `system.switch.enable = false`） |
>
> **类比**：这就像**手机固件 vs 电脑系统** —— 手机固件是整块替换的（appliance），电脑系统是可以打补丁的（NixOS 常规模式）。

> [!TIP]
> **本指南对「什么时候真的要做 appliance」的建议**：
>
> | 场景 | 建议 |
> |---|---|
> | 你的桌面机 / 笔记本 | **不要**。你要 generation 回滚（§30.8） |
> | 家里的软路由 / NAS | **不需要**。这些用常规 NixOS + `system.autoUpgrade` 更好 |
> | 给客户出厂的设备 | **需要**。这是 appliance 的原始场景 |
> | 想学「最小可引导系统」 | **值得试一次**（在 QEMU 里）。这是理解 UKI / Bootspec / repart 的最好方式 |
>
> **QEMU 里试**（不动真机）：
> ```bash
> nix-build appliance.nix
> qemu-system-x86_64 -enable-kvm -m 2048 \
>   -drive file=./result/nixos-image-*.raw,format=raw,if=virtio \
>   -bios /run/libvirt/nix-ovmf/OVMF_CODE.fd   # 需要 OVMF（UEFI 固件）
> ```

---

### 35.7 六个反模式

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | 用 `nix-channel --add` 时忘了末尾的 `nixos` 参数 | 命令成功但**频道没改**（官方原文明确要求） | `sudo nix-channel --add <url> nixos` |
| 2 | 不加 `sudo` 跑 `nix-channel --add` | 只改用户频道，**不影响系统**（官方原文） | 加 `sudo` |
| 3 | `system.autoUpgrade.allowReboot = true` 用在桌面机 | 内核更新后**自动重启**，可能丢工作 | 设 `false`，重启自己挑时间 |
| 4 | 把自己的 `configuration.nix` 整份塞进 Live ISO | ISO 里那份会漂移；硬件相关配置与目标机磁盘冲突 | ISO 只放「git + SSH key + flake 地址」，装机时 clone |
| 5 | `image.repart` 里 `Label` 与 `fileSystems.*.device` 不一致 | **挂不上 → 掉 emergency shell**（不是警告） | 两处字符串**逐字对齐** |
| 6 | 给桌面机做 appliance 镜像 | **失去 `nixos-rebuild` 和 generation 回滚** | 桌面机保持常规 NixOS；appliance 只在 QEMU 里试 |

> [!TIP]
> **本章的四行一句话总结**：
>
> **想装第二台机** → `nixos-rebuild build-image` 先列变体（§35.3）。
> **想给 Agent 一个实验场** → `image.repart` 做 QEMU 镜像（§35.4）。
> **想做预装 U 盘** → 别塞 `configuration.nix`，放 flake 地址（§35.2）。
> **appliance 是另一条路** —— 没有 `nixos-rebuild`，靠换整镜像或 A/B 分区升级（§35.6）。
>
> **本章你至少要记住一条**：`Label` 和 `fileSystems.*.device` 必须一致，否则开机掉 shell。

---

## 附录 A：命令速查

### A.1 系统重建与验证

```bash
# 日常改配置（立即生效）
sudo nixos-rebuild switch

# 改内核/驱动（重启生效，自动进 bootloader 菜单）
sudo nixos-rebuild boot

# 临时试（重启即恢复原样）—— 不确定的改动先用这个
sudo nixos-rebuild test

# 验证闸门：只求值，不碰系统 —— AI 改配置后必用
sudo nixos-rebuild dry-build

# 生成虚拟机真跑一遍（升级前强烈推荐）
sudo nixos-rebuild build-vm
./result/bin/run-*-vm

# flake 用户加上 --flake
sudo nixos-rebuild switch --flake /etc/nixos#mypc
sudo nixos-rebuild dry-build --flake .#mypc
```

### A.2 回滚与 generation

```bash
# 列出所有 generation
sudo nixos-rebuild list-generations

# 回滚到上一个 generation
sudo nixos-rebuild switch --rollback

# 回滚到指定 generation
sudo nixos-rebuild switch --switch-generation 42

# 删除旧 generation（安全版：保留 30 天）
sudo nix-collect-garbage --delete-older-than 30d

# ⛔ 危险：删除所有旧 generation（不要用）
# sudo nix-collect-garbage -d
```

### A.3 磁盘与 store

```bash
# 看磁盘占用
df -h /nix /boot
du -sh /nix/store

# 手动 GC
sudo nix-collect-garbage --delete-older-than 30d

# store 去重（可回收大量空间）
sudo nix-store --optimise

# 检查 store 完整性
sudo nix-store --verify --check-contents

# 看某个包占了多大
nix path-info -Sh /nix/store/<hash>-<name>

# 树状查看依赖大小
nix-tree /run/current-system
```

### A.4 查询

```bash
# 查选项定义（本机已安装系统内）
nixos-option programs.steam.enable

# 查包
nix search nixpkgs firefox

# 命令找不到时定位提供者（需 nix-index）
nix-locate --top-level bin/htop

# 导出当前系统的完整生效配置（给 AI 的地面真值）
nix eval --json .#nixosConfigurations.mypc.config > current-config.json

# 在临时 shell 里试一个包（不污染系统）
nix shell nixpkgs#ffmpeg
nix run nixpkgs#cowsay -- hello
```

### A.5 flake 操作

```bash
# 更新所有 input
nix flake update

# 只更新一个 input
nix flake update nixpkgs-unstable

# 查看 flake 结构
nix flake show

# 检查 flake 是否有问题
nix flake check

# 查看 lock 文件里锁定的版本
nix flake metadata

# ⚠️ 改了 flake.nix 后必须先 git add，否则 Nix 看不到
git add flake.nix flake.lock
```

### A.6 诊断（AMD 平台专用）

```bash
# 显卡是否被识别、用的什么驱动
lspci -k | grep -A 3 -i vga
# 期望看到：Kernel driver in use: amdgpu

# 图形栈信息
glxinfo | grep -E "OpenGL renderer|OpenGL version"    # 需 mesa-demos
vulkaninfo --summary | head -30                        # 需 vulkan-tools

# 硬件视频解码是否可用
vainfo                                                 # 需 libva-utils
# 期望看到 VAProfileH264 / VAProfileHEVC 等

# 网卡驱动
lspci -k | grep -A 3 -i ethernet
lsmod | grep -E "r8168|r8169"

# 内核版本
uname -r

# 看失败的服务
systemctl --failed

# 看本次启动的错误日志
journalctl -b -p err --no-pager

# 看某个服务的日志
journalctl -u nixos-upgrade.service --no-pager
```

### A.7 自动升级

```bash
# 手动触发一次自动升级
sudo systemctl start nixos-upgrade

# 看自动升级日志
journalctl -u nixos-upgrade.service --no-pager

# 看定时器状态
systemctl list-timers | grep -E "nixos|flake"
```

### A.8 游戏 / 性能诊断（第十四章）

```bash
# ── 调度器（scx） ──
ls /sys/kernel/sched_ext                    # 存在 = 内核支持 sched-ext
systemctl status scx                        # 服务状态
journalctl -u scx --no-pager                # 调度器日志（崩了看这里）
cat /sys/kernel/sched_ext/root/ops          # 当前加载的调度器（有输出即生效）

# 临时换调度器做 A/B 测试（重启失效）
sudo systemctl set-environment SCX_SCHEDULER_OVERRIDE=scx_bpfland
sudo systemctl restart scx
sudo systemctl unset-environment SCX_SCHEDULER_OVERRIDE

# ── I/O 调度器 ──
cat /sys/block/sda/queue/scheduler           # 方括号 = 当前生效
cat /sys/block/nvme0n1/queue/scheduler
cat /sys/block/sda/queue/rotational          # 1 = 机械盘

# ── CPU 频率 / 电源 ──
cat /sys/devices/system/cpu/amd_pstate/status              # active / passive / guided
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference
cpupower frequency-info                                     # 需 cpupower

# ── ntsync（仅 linux_zen 有） ──
ls -l /dev/ntsync
lsmod | grep ntsync

# ── 内核编译期配置（看你的内核到底开了什么） ──
zcat /proc/config.gz | grep -E "SCHED_CLASS_EXT|NTSYNC|IOSCHED_BFQ|PREEMPT_|HZ="
# 若没有 /proc/config.gz，用：
nix-shell -p linuxPackages.kernel --run 'cat $kernelBuild/config' 2>/dev/null | head

# ── 内存 / zram ──
zramctl
swapon --show
free -h

# ── NixOS 已设的 sysctl（先看再改） ──
sysctl vm.max_map_count
sysctl fs.inotify.max_user_watches
```

### A.9 语言工具链与 MCP（第十五、十六章）

```bash
# ── 语言版本确认 ──
node -v ; npm -v ; npx -v
python3 -V ; uv --version
rustc --version ; cargo --version
go version
tsc -v ; tsx --version

# ── npm 全局装到用户目录（不要 sudo） ──
npm config set prefix ~/.npm-global
npm config set cache ~/.npm-cache
export PATH="$HOME/.npm-global/bin:$PATH"
npm install -g <package>
npm ls -g --depth=0                          # 看装了哪些全局包
which <package>                              # 拿绝对路径，写进 MCP 配置

# ── uv（Python） ──
uv tool install <cli>                        # 隔离安装 CLI 工具
uv tool list
uv python install 3.12
uv venv --python 3.12

# ── 编译依赖诊断（devShell 里） ──
pkg-config --list-all | grep -i ssl
pkg-config --cflags --libs openssl
echo $PKG_CONFIG_PATH

# ── 预编译二进制跑不起来 → nix-ld ──
# 先看它要什么动态链接器
patchelf --print-interpreter ./some-binary
ldd ./some-binary | grep "not found"
# 然后在配置里 programs.nix-ld.libraries 补对应库

# ── SearXNG JSON API 验证 ──
curl -s "http://127.0.0.1:8888/search?q=nixos&format=json" | jq '.results[:3]'

# ── Playwright（用 nixpkgs 的浏览器） ──
export PLAYWRIGHT_BROWSERS_PATH="$(nix-build '<nixpkgs>' -A playwright-driver.browsers --no-out-link)"
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
```

---

## 附录 B：出处汇总

### B.1 官方文档与手册

| 主题 | URL |
|---|---|
| NixOS 手册（总） | https://nixos.org/manual/nixos/stable/ |
| 安装 | https://nixos.org/manual/nixos/stable/#sec-installation |
| 改配置 | https://nixos.org/manual/nixos/stable/#sec-changing-config |
| 升级 | https://nixos.org/manual/nixos/stable/#sec-upgrading |
| GC | https://nixos.org/manual/nixos/stable/#sec-nix-gc |
| GPU 加速（含 VA-API / Vulkan） | https://nixos.org/manual/nixos/stable/#sec-gpu-accel |
| FHS 环境（nixpkgs 手册） | https://nixos.org/manual/nixpkgs/stable/#sec-fhs-environments |
| Nix store path | https://nix.dev/manual/nix/stable/store/store-path.html |
| `nix search` 手册 | https://nix.dev/manual/nix/latest/command-ref/new-cli/nix3-search |
| NixOS 26.05 发布公告 | https://nixos.org/blog/announcements/2026/nixos-2605/ |
| amd-pstate（内核文档） | https://docs.kernel.org/admin-guide/pm/amd-pstate.html |
| Proton · NTFS 磁盘（Valve 官方 Wiki） | https://github.com/ValveSoftware/Proton/wiki/Using-a-NTFS-disk-with-Linux-and-Windows |

### B.2 NixOS Wiki

| 主题 | URL |
|---|---|
| **AMD GPU**（第三章主要依据） | https://wiki.nixos.org/wiki/AMD_GPU |
| **Fcitx5**（第五章主要依据） | https://wiki.nixos.org/wiki/Fcitx5 |
| Fonts | https://wiki.nixos.org/wiki/Fonts |
| Steam | https://wiki.nixos.org/wiki/Steam |
| Flatpak | https://wiki.nixos.org/wiki/Flatpak |
| GNOME | https://wiki.nixos.org/wiki/GNOME |
| KDE Plasma | https://wiki.nixos.org/wiki/KDE_Plasma |
| Graphics | https://wiki.nixos.org/wiki/Graphics |
| Nix-ld | https://wiki.nixos.org/wiki/Nix-ld |
| Packaging/Binaries | https://wiki.nixos.org/wiki/Packaging/Binaries |
| Linux Kernel | https://wiki.nixos.org/wiki/Linux_Kernel |
| nixos-rebuild | https://wiki.nixos.org/wiki/Nixos-rebuild |
| 自动系统升级 | https://wiki.nixos.org/wiki/Automatic_system_upgrades |
| stateVersion FAQ | https://wiki.nixos.org/wiki/FAQ/When_do_I_update_stateVersion |
| Noogle | https://wiki.nixos.org/wiki/Noogle |
| NixOS search | https://wiki.nixos.org/wiki/NixOS_search |

### B.3 nixpkgs 源码（`nixos-26.05` 分支，逐条比对）

前缀：`https://github.com/NixOS/nixpkgs/blob/nixos-26.05/`

| 模块 | 路径 |
|---|---|
| 图形栈（`enable` 默认 false） | `nixos/modules/hardware/graphics.nix` |
| AMD GPU 专属选项 | `nixos/modules/services/hardware/amdgpu.nix` |
| X11 / `videoDrivers` 默认值 | `nixos/modules/services/x11/xserver.nix` |
| AMD 微码 | `nixos/modules/hardware/cpu/amd-microcode.nix` |
| LACT | `nixos/modules/services/hardware/lact.nix` |
| CoreCtrl | `nixos/modules/hardware/corectrl.nix` |
| 固件 | `nixos/modules/hardware/all-firmware.nix` |
| 用户 / `linger` | `nixos/modules/config/users-groups.nix` |
| locale | `nixos/modules/config/i18n.nix` |
| 字体 | `nixos/modules/config/fonts/fontconfig.nix` |
| **输入法总模块**（`enabled` 弃用） | `nixos/modules/i18n/input-method/default.nix` |
| **fcitx5**（`waylandFrontend`） | `nixos/modules/i18n/input-method/fcitx5.nix` |
| GNOME | `nixos/modules/services/desktop-managers/gnome.nix` |
| Plasma 6 | `nixos/modules/services/desktop-managers/plasma6.nix` |
| GDM | `nixos/modules/services/display-managers/gdm.nix` |
| SDDM | `nixos/modules/services/display-managers/sddm.nix` |
| Flatpak | `nixos/modules/services/desktops/flatpak.nix` |
| xdg portal | `nixos/modules/config/xdg/portal.nix` |
| Steam | `nixos/modules/programs/steam.nix` |
| gamescope | `nixos/modules/programs/gamescope.nix` |
| gamemode | `nixos/modules/programs/gamemode.nix` |
| scx 调度器 | `nixos/modules/services/scheduling/scx.nix` |
| r8168 驱动 | `pkgs/os-specific/linux/r8168/default.nix` |
| r8125 驱动 | `pkgs/os-specific/linux/r8125/default.nix` |
| **zram** | `nixos/modules/config/zram.nix` |
| **zram-generator** | `nixos/modules/services/system/zram-generator.nix` |
| **zram-as-tmp** | `nixos/modules/system/boot/zram-as-tmp.nix` |
| **udev（`extraRules` → `99-local.rules`）** | `nixos/modules/services/hardware/udev.nix` |
| **sysctl（`max_map_count` 等默认值）** | `nixos/modules/config/sysctl.nix` |
| **nix-ld** | `nixos/modules/programs/nix-ld.nix` |
| **appimage** | `nixos/modules/programs/appimage.nix` |
| **direnv** | `nixos/modules/programs/direnv.nix` |
| **SearXNG** | `nixos/modules/services/networking/searx.nix` |
| **ClamAV** | `nixos/modules/services/security/clamav.nix` |
| **fail2ban** | `nixos/modules/services/security/fail2ban.nix` |
| **AppArmor** | `nixos/modules/security/apparmor.nix` |
| **audit / auditd** | `nixos/modules/security/audit.nix` · `security/auditd.nix` |
| **内核变体定义** | `pkgs/top-level/linux-kernels.nix` |
| **内核通用配置**（`PREEMPT_LAZY` / `IOSCHED_BFQ` / `SCHED_CLASS_EXT`） | `pkgs/os-specific/linux/kernel/common-config.nix` |
| **`linux_zen` 补丁集**（`ZEN_INTERACTIVE` / `HZ=1000` / `NTSYNC`） | `pkgs/os-specific/linux/kernel/zen-kernels.nix` |
| **`linux_xanmod` 变体**（`lts`=6.18.55 / `main`=7.2.9） | `pkgs/os-specific/linux/kernel/xanmod-kernels.nix` |
| **scx 包** | `pkgs/os-specific/linux/scx/` |
| **playwright driver** | `pkgs/development/web/playwright/driver.nix` |
| **`nodePackages` 删除等 nixpkgs 层变更** | `doc/release-notes/rl-2605.section.md`（⚠️ **nixpkgs** 发布说明，讲 GCC 15 / glibc 2.42 / `corepack_latest` 删除等） |
| **NixOS 层变更**（内核 6.12→6.18、`linux_hardened`/`linux-rt` 移除、`systemd.extraConfig` 移除等） | `nixos/doc/manual/release-notes/rl-2605.section.md`（⚠️ **NixOS** 发布说明，与上面那个**是两个不同文件**） |

### B.3.1 非 nixpkgs 的上游源码

| 事实 | 出处 |
|---|---|
| **`elevator=` 已是死参数** | `torvalds/linux` `block/elevator.c:893-898` |

### B.4 镜像源

| 镜像 | URL |
|---|---|
| USTC nix 帮助 | https://mirrors.ustc.edu.cn/help/nix-channels.html |
| USTC nix store | https://mirrors.ustc.edu.cn/nix-channels/store |
| TUNA nix 帮助 | https://mirrors.tuna.tsinghua.edu.cn/help/nix-channels/ |
| TUNA nix store | https://mirrors.tuna.tsinghua.edu.cn/nix-channels/store |
| SJTU flathub 镜像 | https://mirror.sjtu.edu.cn/flathub |
| USTC flathub 镜像 | https://mirrors.ustc.edu.cn/flathub |

### B.5 AI agent 工具与 MCP

| 项目 | URL |
|---|---|
| Hermes Agent（Nous Research） | https://github.com/NousResearch/hermes-agent |
| OpenAI Codex CLI | https://github.com/openai/codex |
| OpenClaw / clawhub.ai | https://clawhub.ai |
| **mcp-nixos**（NixOS 查询 MCP） | https://github.com/utensils/mcp-nixos |
| Home Manager · programs.mangohud | https://nix-community.github.io/home-manager/options/home-manager/programs/mangohud.html |

### B.6 生态查询工具（第十二章）

| 工具 | URL |
|---|---|
| search.nixos.org | https://search.nixos.org/ |
| nixos-search 源码 | https://github.com/NixOS/nixos-search |
| NixHub.io | https://www.nixhub.io |
| NixHub API 文档 | https://www.jetify.com/docs/nixhub |
| NixHub API 实测主机 | https://search.devbox.sh |
| FlakeHub 文档 | https://docs.determinate.systems/flakehub/ |
| FlakeHub 定价 | https://flakehub.com/pricing |
| FlakeHub 批评帖 | https://discourse.nixos.org/t/introducing-flakehub/32044 |
| Nix 治理危机（LWN） | https://lwn.net/Articles/970824/ |
| Noogle | https://noogle.dev |
| Noogle 全量数据端点 | https://noogle.dev/api/v1/data |
| Jetify / Devbox | https://www.jetify.com/docs |

### B.7 社区

| 主题 | URL |
|---|---|
| 混用 stable + unstable（官方论坛） | https://discourse.nixos.org/t/mixing-stable-and-unstable-packages-on-flake-based-nixos-system/50351 |
| 自动更新 flakes（实测有效） | https://discourse.nixos.org/t/how-to-automatically-update-flakes/72426 |
| search.nixos.org 无 broken 筛选（抱怨帖） | https://discourse.nixos.org/t/nixos-package-search-does-not-show-when-a-package-is-broken/78488 |
| `--update-input` 废弃 | https://github.com/NixOS/nixpkgs/issues/349734 |
| 反作弊支持状态 | https://areweanticheatyet.com/ |
| nix-gaming | https://github.com/fufexan/nix-gaming |

### B.8 第十四～十七章的新增出处

**游戏 / 内核 / 调度器**

| 主题 | URL |
|---|---|
| sched-ext（scx）上游 | https://github.com/sched-ext/scx |
| scx 各调度器说明 | https://github.com/sched-ext/scx/tree/main/scheds |
| Zen 内核上游 | https://github.com/zen-kernel/zen-kernel |
| XanMod 内核上游 | https://xanmod.org |
| `scx_lavd`（Igalia × Valve）报道 | https://www.phoronix.com |
| split lock 检测（misery mode） | https://www.kernel.org/doc/html/latest/arch/x86/x86_64/boot-options.html |
| MangoHud | https://github.com/flightlessmango/MangoHud |
| vkBasalt | https://github.com/DadSchoorse/vkBasalt |
| are we anti-cheat yet | https://areweanticheatyet.com/ |

**语言工具链**

| 主题 | URL |
|---|---|
| uv | https://docs.astral.sh/uv/ |
| bun | https://bun.sh |
| deno | https://deno.com |
| mise | https://mise.jdx.dev |
| devenv | https://devenv.sh |
| nix-ld（上游） | https://github.com/nix-community/nix-ld |
| Node.js v22→v24 迁移 | https://nodejs.org/en/blog/migrations/v22-to-v24 |
| PEP 668（externally-managed） | https://peps.python.org/pep-0668/ |

**MCP / SearXNG / Agent 工具**

| 主题 | URL |
|---|---|
| SearXNG 上游 | https://github.com/searxng/searxng |
| SearXNG JSON 输出（`formats`） | https://docs.searxng.org/admin/settings/settings_search.html |
| Playwright | https://playwright.dev |
| Model Context Protocol | https://modelcontextprotocol.io |
| sops-nix | https://github.com/Mic92/sops-nix |
| agenix | https://github.com/ryantm/agenix |

**安全 / FHS**

| 主题 | URL |
|---|---|
| NixOS Wiki · AppArmor | https://wiki.nixos.org/wiki/AppArmor |
| ClamAV 上游 | https://www.clamav.net |
| systemd 沙箱指令（`systemd.exec`） | https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html |
| `buildFHSEnv` | https://nixos.org/manual/nixpkgs/stable/#sec-fhs-environments |
| Nix 手册 · 沙箱 | https://nixos.org/manual/nix/stable/command-ref/conf-file.html |


### B.9 第十八章的新增出处（CachyOS 对照）

**CachyOS 官方仓库（一手）**

| 主题 | URL |
|---|---|
| CachyOS-Settings（§18.4–18.7 逐行翻译的原始文件） | https://github.com/CachyOS/CachyOS-Settings |
| ↳ sysctl 原值 | `usr/lib/sysctl.d/70-cachyos-settings.conf` |
| ↳ I/O 调度器规则 | `usr/lib/udev/rules.d/60-ioschedulers.rules` |
| ↳ zram / THP / limits / ntsync 原始文件 | `usr/lib/systemd/zram-generator.conf`、`usr/lib/tmpfiles.d/thp.conf`、`usr/lib/tmpfiles.d/thp-shrinker.conf`、`usr/lib/systemd/system.conf.d/10-limits.conf`、`usr/lib/modules-load.d/ntsync.conf` |
| CachyOS 官方 ananicy 规则仓库（nixpkgs 已打包） | https://github.com/CachyOS/ananicy-rules |
| CachyOS 内核（BORE / EEVDF / BMQ / RT 变体） | https://github.com/CachyOS/linux-cachyos |
| ↳ 调度器技术说明（BORE = `CONFIG_SCHED_BORE`；BMQ 与 sched-ext 不兼容） | https://deepwiki.com/CachyOS/linux-cachyos/3-cpu-schedulers |
| ↳ 构建变量 `_cpusched` / `_preempt` / `_HZ_ticks` | https://github.com/CachyOS/linux-cachyos/blob/master/linux-cachyos/PKGBUILD |
| CachyOS Wiki · sched-ext | https://wiki.cachyos.org/configuration/sched-ext/ |

**nixpkgs 源码（§18 新增核实项）**

| 主题 | 路径 |
|---|---|
| CachyOS ananicy 规则包（`0-unstable-2026-05-19`，rev `74b314e1c54115623fcb0eea868d1e08a10f84fe`） | `pkgs/by-name/an/ananicy-rules-cachyos/package.nix` |
| ananicy 模块（`package` / `rulesProvider` / `settings` / `extraRules` / `extraTypes` / `extraCgroups`） | `nixos/modules/services/misc/ananicy.nix` |
| KSM 模块（`hardware.ksm`，旧名 `hardware.enableKSM`） | `nixos/modules/hardware/ksm.nix` |
| scx 模块（默认 `scx_rustland`；断言内核 ≥ 6.12；`SCX_SCHEDULER_OVERRIDE`） | `nixos/modules/services/scheduling/scx.nix` |
| sysctl 模块（值类型 = bool / int / string / null） | `nixos/modules/config/sysctl.nix` |
| zram 模块（`memoryPercent` 默认 50、`priority` 默认 5） | `nixos/modules/config/zram.nix` |
| tmpfiles 模块（`systemd.tmpfiles.rules`） | `nixos/modules/system/boot/systemd/tmpfiles.nix` |
| systemd 模块（`settings.Manager`；`extraConfig` 已被 `mkRemovedOptionModule` 删除） | `nixos/modules/system/boot/systemd.nix` |
| zen 内核配置（`NTSYNC = yes` / `HZ = 1000` / `IOSCHED_BFQ = yes` / `PREEMPT = yes`） | `pkgs/os-specific/linux/kernel/zen-kernels.nix` |
| 内核默认配置（`SCHED_CLASS_EXT` ≥6.12 / `MQ_IOSCHED_KYBER=yes` / **未设 `CONFIG_NTSYNC`**） | `pkgs/os-specific/linux/kernel/common-config.nix` |
| `pkgs.bore`（**TCP 隧道**，不是 BORE 调度器） | `pkgs/by-name/bo/bore/package.nix` |
| `pkgs.hdparm` / `pkgs.limine` / `pkgs.irqbalance` / `pkgs.proton-ge-bin` | `pkgs/by-name/{hd,li,ir,pr}/…` |

**非 nixpkgs 上游源码（用于否定性核实）**

| 主题 | URL |
|---|---|
| zen-kernel `v7.2.9-zen1`（确认 `kernel/Kconfig.preempt` 无 BORE） | https://github.com/zen-kernel/zen-kernel/tree/v7.2.9-zen1 |

### B.10 本轮复核（2026-10-12 第二轮）新增/修正的出处

> 本轮对全文做了一次**逐条一手复核**：把 22 个 nixpkgs 模块文件 + 内核源码 + 两套 release notes + NixOS Wiki 全部重读一遍。以下是**新发现或修正**的部分。

**① 模块路径修正（原稿写错，本轮改正）**

| 项 | 原稿（❌ 404） | 实际路径（✅ 200） | 交叉验证 |
|---|---|---|---|
| GNOME 模块 | `services/x11/desktop-managers/gnome.nix` | **`services/desktop-managers/gnome.nix`**（569 行） | GitHub contents API 列目录 |
| Plasma 6 模块 | `services/x11/desktop-managers/plasma6.nix` | **`services/desktop-managers/plasma6.nix`**（410 行） | 同上 |
| GDM | `services/x11/display-managers/gdm.nix` | **`services/display-managers/gdm.nix`** | `module-list.nix:626` |
| SDDM | `services/x11/display-managers/sddm.nix` | **`services/display-managers/sddm.nix`** | `module-list.nix:632` |
| xdg portal | `services/x11/xdg-portal.nix` | **`config/xdg/portal.nix`**（167 行） | `module-list.nix:45` |

> 另修正一处正文内的笔误：§3.5 原写 `services/hardware/gnome.nix`，实为 `services/desktop-managers/gnome.nix`。**该处的行号（`gnome.nix:332`、`plasma6.nix:272`）本身是对的**，只有目录错了。

**② 两套 release notes 是两个不同文件（原稿混用）**

| 文件 | 内容 | 本轮核实的关键行 |
|---|---|---|
| `doc/release-notes/rl-2605.section.md`（34965 B） | **nixpkgs** 层：GCC 15、glibc 2.42、`corepack_latest` 删除（`:144`）、`fetchPnpmDeps`（`:387`）、`nodejs` 包装变化（`:445-447`） | 原稿引用的 `:387` / `:389` 在这里 |
| `nixos/doc/manual/release-notes/rl-2605.section.md`（47831 B） | **NixOS** 层：默认内核 6.12→6.18（`:44`）、`linux_hardened` 移除（`:232`）、`linux-rt` 移除（`:236`）、`systemd.extraConfig` 移除 | 原稿引用的「内核升级」在这里 |

**③ 新发现：`hardware.graphics.enable` 的三处自动开启点**

原稿只说「GNOME/KDE 都不开」。本轮把「谁会开」查全了 —— 见 §3.1 的表：`programs/steam.nix:205-210`（硬赋值）、`services/hardware/amdgpu.nix:62-70`（`opencl.enable` → `mkDefault`）、`:71-76`（`zluda.enable` → `mkDefault`）。GNOME/Plasma 模块 grep `hardware.graphics` 命中数 **= 0**（已用全文 grep 复核，非抽样）。

**④ 新发现：`services.scx` 的第二个覆盖变量**

`ExecStart` 实为 `${SCX_SCHEDULER_OVERRIDE:-$SCX_SCHEDULER} ${SCX_FLAGS_OVERRIDE:-$SCX_FLAGS}` —— 原稿只写了前者。见 §14.3。

**⑤ 修正：`programs.nix-ld.libraries` 的「默认空」表述**

- 选项声明 `default = [ ]`，`defaultText` 却写 *"baseLibraries derived from systemd and nix dependencies."*
- `config` 段（`nix-ld.nix:47-64`）**无条件注入 14 个库**：`zlib zstd stdenv.cc.cc curl openssl attr libssh bzip2 libxml2 acl libsodium util-linux xz systemd`
- 因 `listOf` 的合并语义是**拼接**，用户写法是**追加**而非替换
- 一手佐证：[NixOS Wiki · Nix-ld](https://wiki.nixos.org/wiki/Nix-ld) 的示例把同一份列表抄了一遍并注明 `# List by default`，且正文写 *"By default, nix-ld comes with only a few libraries"*

**⑥ 修正：`pkgs.bore` 的上游来源**

nixpkgs 打包的是 **`delan/nonymous`（Bitbucket）**，不是 GitHub 的 `ekzhang/bore`：`fetchFromBitbucket { owner = "delan"; repo = "nonymous"; rev = "bore-0.4.1"; }` + `cargoBuildFlags = [ "-p" "bore" ]`。

**⑦ 内核侧复核结论（原稿正确，本轮加固）**

| 断言 | 源码位置 | 结果 |
|---|---|---|
| `packageAliases.linux_default = packages.linux_6_18` | `pkgs/top-level/linux-kernels.nix:740` | ✅ |
| `packageAliases.linux_latest = packages.linux_7_2` | 同上 `:742` | ✅ |
| `linux_hardened` 移除 | 同上 `:187` | ✅ |
| `linux_rt_default` / `linux_rt_latest` 移除 | 同上 `:748-749` | ✅ |
| `linux_lqx` / `linux_libre` 移除 | 同上 `:155-157` | ✅（**仅源码，release notes 未列**） |
| 默认内核 `PREEMPT=no` + `PREEMPT_LAZY`（≥6.18） | `pkgs/os-specific/linux/kernel/common-config.nix:1417-1419` | ✅ |
| `CPU_FREQ_DEFAULT_GOV_SCHEDUTIL=yes` | 同上 `:126` | ✅ |
| `MQ_IOSCHED_DEADLINE/KYBER=yes`、`IOSCHED_BFQ=module` | 同上 `:262-265` | ✅ |
| `SCHED_CLASS_EXT`（≥6.12） | 同上 `:1430` | ✅ |
| 默认内核**未设** `NTSYNC` / `FUTEX` | 同上（grep 命中数 **0**） | ✅ |
| `linux_zen` = 7.2.9-zen1，含 `NTSYNC` / `HZ=1000` / `IOSCHED_BFQ` / `ZEN_INTERACTIVE` | `pkgs/os-specific/linux/kernel/zen-kernels.nix` | ✅ |
| xanmod `lts=6.18.55` / `main=7.2.9`；6.13+ 用 `PREEMPT_LAZY` | `pkgs/os-specific/linux/kernel/xanmod-kernels.nix` | ✅ |
| `scx.full` = 26 个调度器（18 Rust + 8 C） | `pkgs/os-specific/linux/scx/scx_{full,rustscheds,cscheds}.nix` | ✅ |

**⑧ 包存在性复核（`nixos-26.05` 分支，raw HTTP 状态码）**

| 包 | 结果 | 落点 |
|---|---|---|
| `ananicy-rules-cachyos` | ✅ 200 | `pkgs/by-name/an/ananicy-rules-cachyos/package.nix` |
| `mcp-nixos` | ✅ 200 | `pkgs/by-name/mc/mcp-nixos/package.nix` |
| `proton-ge-bin` | ✅ 200 | `pkgs/by-name/pr/proton-ge-bin/package.nix` |
| `lact` / `corectrl` / `ollama` | ✅ 200 | `pkgs/by-name/{la,co,ol}/…` |
| `bore` | ✅ 200 | `pkgs/by-name/bo/bore/package.nix`（v0.4.1） |
| `hdparm` / `limine` / `irqbalance` | ✅ 200 | `pkgs/by-name/{hd,li,ir}/…` |
| **`yarn`** | ✅ **200**（原稿误记 404） | `pkgs/by-name/ya/yarn/package.nix` |
| `pnpm` | ⚠️ by-name **404**，但 `pkgs.pnpm` 有效 | `all-packages.nix:2967` = `pnpm_11` |
| `rustup` | ⚠️ by-name **404**，但 `pkgs.rustup` 有效 | `all-packages.nix:4396` |
| `r8125` | ⚠️ by-name 404，但属性有效 | `pkgs/os-specific/linux/r8125/default.nix` |
| `ollama-{rocm,cuda,vulkan,cpu}` | ⚠️ 无独立目录 | `all-packages.nix:424-427` 用 `acceleration` 参数生成 |
| `scx` | ⚠️ by-name 404 | `pkgs/os-specific/linux/scx/`（非 by-name） |
| `uksmd` / `proton-cachyos` / `cachyos-settings` / `scx-scheds` | ❌ 404 | 确认不在 nixpkgs |

**⑨ 其它源码级复核**

| 断言 | 源码位置 | 结果 |
|---|---|---|
| `services.ananicy` 7 个选项（`enable`/`package`/`rulesProvider`/`settings`/`extraRules`/`extraTypes`/`extraCgroups`） | `services/misc/ananicy.nix:24-92` | ✅ |
| `systemd.extraConfig` 已删除（`mkRemovedOptionModule`） | `system/boot/systemd.nix:920` | ✅ |
| `services.journald.extraConfig` **仍存在** | `system/boot/systemd/journald.nix:97` | ✅ |
| `services.timesyncd.servers` 存在 | `system/boot/timesyncd.nix:21` | ✅ |
| `security.rtkit.enable` 默认 `false` | `security/rtkit.nix:15` | ✅ |
| `services.lact` 3 个选项 + GUI 无法改配置的警告 | `services/hardware/lact.nix` | ✅ |
| `programs.corectrl` 2 个选项 + 建组 + polkit | `hardware/corectrl.nix:28-56` | ✅ |
| `xdg.portal.extraPortals` 默认 `[ ]`；`enable=true` 时**硬断言**要求非空 | `config/xdg/portal.nix:45-47,134-135` | ✅ |
| GNOME 自动填 `extraPortals`（`gnome.nix:351-356`）、Plasma 6 同样（`plasma6.nix:294-300`） | 两文件 | ✅ |
| `gnome.nix:332` / `plasma6.nix:272` 都是 `services.power-profiles-daemon.enable = mkDefault true` | 两文件 | ✅（行号准确） |
| `plasma6.nix:353-358` 给 `kwin_wayland` 打 `cap_sys_nice+ep` | 同上 | ✅ |
| Home Manager 不在 nixpkgs：`module-list.nix` grep 命中 **0**；`all-packages.nix` 只有 1 行注释 | 两文件 | ✅ |

### B.11 第十九～二十二章的新增出处（2026-10-12 第三轮）

#### B.11.1 nixpkgs / 上游仓库存在性核实（`[核实·源码]`，逐条 HTTP 状态码）

| 核实对象 | 路径 / 端点 | 结果 |
|---|---|---|
| OpenClaw 包**存在** | `pkgs/by-name/op/openclaw/package.nix` | ✅ **200** |
| OpenClaw 包**带 `knownVulnerabilities`** | 同上 `meta` 段 | ✅ 原文：prompt injection + full system access |
| OpenClaw 三个别名二进制 | 同上 `installPhase`：`ln -s $out/bin/openclaw $out/bin/moltbot` / `clawdbot` | ✅ |
| OpenClaw 包默认版本 | 同上 `version ? "2026.5.7"` | ✅ |
| **nixpkgs 无 `services.openclaw` 模块** | `nixos/modules/module-list.nix` grep `openclaw` | ✅ **命中 0** |
| **nixpkgs 无 `hermes-agent` 包** | `pkgs/by-name/he/hermes-agent/package.nix` | ❌ **404** |
| 上游 `openclaw/openclaw` **无 flake.nix** | `raw.../main/flake.nix` | ❌ **404**；无 `nix/` 目录 |
| 上游 `NousResearch/hermes-agent` **有 flake.nix** | `raw.../main/flake.nix` | ✅ **200** |
| Hermes 的 `nix/` 目录（22 个文件） | GitHub contents API | ✅ 含 `nixosModules.nix` / `homeManagerModules.nix` / `moduleCommon.nix` / `overlays.nix` / `packages.nix` / `desktop.nix` / `tui.nix` / `web.nix` / `sandbox.nix` / `configMergeScript.nix` / `checks.nix` / `devShell.nix` / `python.nix` / `pythonLock.nix` / `pm-*.nix` |
| nix-openclaw 三套模块 | `nix/modules/` 下 `darwin` / `home-manager` / `nixos` | ✅ |
| nix-openclaw 的 NixOS 模块**只有一个文件** | `nix/modules/nixos/openclaw-gateway.nix` | ✅ 235 行 |
| nix-openclaw 唯一模板 | `templates/` 下只有 `agent-first` | ✅ |
| nix-openclaw 仓库元信息 | API：712★ / `pushed_at` 2026-09-25 | ✅ |
| 上游 openclaw 仓库元信息 | API：391735★ / `pushed_at` 2026-10-12 | ✅ |
| Hermes 仓库元信息 | API：252937★ / 54783 forks / `open_issues_count` 48043 | ✅ |
| 第三方 `0xrsydn/nix-hermes-agent` | API：46★ / 8 forks / 创建 2026-03-15 / **推送 2026-10-11** | ✅ 活跃 |
| 第三方模块**无 linger 处理** | `module.nix` grep `linger` | ✅ **命中 0** |
| 第三方选项名是 `config` 而非 `settings` | 第三方 README 选项表 + 官方文档选项表 | ✅ 两者不同 |

#### B.11.2 nix-openclaw NixOS 模块的关键实现（`[核实·源码]` `nix/modules/nixos/openclaw-gateway.nix`）

| 事实 | 源码位置 |
|---|---|
| 21 个选项，`user` 默认 `"openclaw"` / `createUser` 默认 `true` / `stateDir` 默认 `/var/lib/openclaw` | `options.services.openclaw-gateway` |
| `configPath` 默认 `/etc/openclaw/openclaw.json` | 同上 |
| **硬断言：`configPath` 必须以 `/etc/` 开头** | `assertions` |
| `/etc/openclaw` 由 tmpfiles 建成 **`0755 root root`** | `systemd.tmpfiles.rules` |
| 服务以 **非 root** 运行（`User = cfg.user`） | `serviceConfig` |
| `wantedBy = [ "multi-user.target" ]`（**系统级**） | `systemd.services.${cfg.unitName}` |
| 创建 `openclaw` 系统用户（`isSystemUser = true` / `shell = bashInteractive`） | `users.users.${cfg.user}` |
| HM 模块的 systemd 是**用户级**（`systemd.user.services`），`systemd.enable` 默认 `true` | `nix/modules/home-manager/openclaw/options-instance.nix` |
| HM 模块 `stateDir` 默认 `~/.openclaw`；`configPath = "${stateDir}/openclaw.json"` | `home-manager/openclaw/options.nix` / `config.nix` |
| HM 模块 activation 里 `openclaw.json` 是**指向 Nix store 的符号链接** | `config.nix`：`ln -sfn ${item.configFile} ${resolvePath item.configPath}` |

#### B.11.3 Hermes Nix 模块的关键实现（`[核实·源码]` `nix/nixosModules.nix` / `nix/homeManagerModules.nix`）

| 事实 | 源码位置 |
|---|---|
| 服务加固：`NoNewPrivileges` / `ProtectSystem = "strict"` / `PrivateTmp` / `ReadWritePaths = [ stateDir workingDirectory ]` | `nixosModules.nix:213-234` |
| `User = cfg.user` / `Group = cfg.group` / `UMask = "0007"`（便于组内用户共享） | 同上 |
| **`linger = lib.mkDefault (!cfg.container.enable)`** | `nixosModules.nix:369` |
| `after`/`wants` 追加 `linger-users.service` | `:571-578` |
| `preStart` 轮询 `/run/user/$(id -u)/bus` 最多 50×0.2s=10s，超时打警告 | `:594-603` |
| **源码注释：无 user manager 时 cron "fails closed — without this, no cron job runs at all"** | `:361-365` |
| container 模式自动 `virtualisation.docker.enable = lib.mkDefault (...)` | `:638` |
| container 模式容器以 `--network=host` + `/nix/store:ro` + `stateDir:/data` 创建 | `:675-690` |
| **硬断言：`container.enable` 与 `backend.mode != "none"` 互斥** | `:410-411` |
| HM 模块 Linux 用 `systemd.user.services.hermes-agent` / `hermes-backend` | `homeManagerModules.nix:397,404` |
| HM 模块 macOS 用 `launchd.agents.hermes-agent` / `hermes-backend` | `:412,419` |
| HM 模块 `managedSystem = "home-manager"`（NixOS 模块给 `sudo nixos-rebuild switch`） | `:70` / `:382` |

#### B.11.4 Hermes 官方文档（`[官方]` `hermes-agent.nousresearch.com/docs/`）

| 事实 | 来源页 |
|---|---|
| **Nix/NixOS 是 Tier 2 平台**，原文 *"maintained on a best-effort basis only. Commits to `main` may break these packages at any point in time."* | `getting-started/platform-support.md` |
| 四层部署表（`nix run` / HM 模块 / NixOS native / NixOS container） | `getting-started/nix-setup.md` |
| HM 模块定位原文 *"Hermes is an agent for one person... Thus a user service is the correct shape on a personal machine."* | 同上 |
| `addToSystemPackages` 同时设 `HERMES_HOME` 系统级（否则 CLI 会建独立 `~/.hermes`） | 同上 |
| **Managed Mode 阻断 5 条命令**（`setup` / `config edit` / `config set` / `gateway install` / `gateway uninstall`） | 同上 |
| 检测用 **`HERMES_MANAGED` 环境变量** + **`HERMES_HOME/.managed` 标记文件** | 同上 |
| **HM 模块不支持 container mode**（*"not supported, because it needs root and the Docker socket"*） | 同上 |
| **NixOS 模块不支持 desktop 应用**（*"a system service cannot own a user session"*） | 同上 |
| Podman rootful 需 sudo，官方给 `security.sudo.extraRules` 配 `NOPASSWD` | 同上 |
| container writable layer 丢失表（改 image / volume / options 触发重建） | 同上 |
| container 身份哈希覆盖：schema 版本 / image / extraVolumes / extraOptions / entrypoint | 同上 |
| 默认包闭包 ~700 MB；`#messaging` 变体 ~33 MB | 同上 |
| 官方 troubleshooting 表（9 条，含 `Permission denied` on `/var/lib/hermes`） | 同上 |
| 官方 `nix/python.nix` 用 **uv2nix**；`sourcePreference = "wheel"` | 同上 |
| **Tier 1**：macOS Apple Silicon / Windows 10-11 / Ubuntu+WSL2 / Docker；**Unsupported**：pypi / brew / AUR / 32 位 x86 macOS | `platform-support.md` |

#### B.11.5 OpenClaw 官方文档（`[官方]` `openclaw/openclaw` 仓库 `docs/`）

| 事实 | 来源页 |
|---|---|
| `OPENCLAW_NIX_MODE=1` 使配置**只读**，禁用所有自变更流程 | `docs/install/nix.md` |
| 非 Nix 场景的等价开关：`OPENCLAW_CONFIG_READONLY=1` | 同上 |
| 三个路径变量：`OPENCLAW_HOME` / `OPENCLAW_STATE_DIR`（默认 `~/.openclaw`）/ `OPENCLAW_CONFIG_PATH` | 同上 |
| 服务 PATH 自动发现：`NIX_PROFILES` 每项按右到左优先级加入；未设时回退 `~/.nix-profile/bin` | 同上 |
| **`openclaw gateway install` 默认渲染 systemd user unit** | `docs/platforms/linux.md:519` |
| **系统 unit 不给 `User=` 会以 root 跑**，原文 *"Running the Gateway and its agent commands as root is unsafe and unsupported for this setup."* | `docs/gateway/index.md:341-343` |
| linger：`sudo loginctl enable-linger $(whoami)` | `docs/gateway/index.md:265` |
| OOM 应对：子进程 `oom_score_adj=1000`（`/bin/sh` shim，非特权）；`OOMPolicy=continue` | `docs/platforms/linux.md:569-630` |
| OOM 自查：`cat /proc/<child-pid>/oom_score_adj` 应为 `1000` | 同上 |
| `OPENCLAW_CHILD_OOM_SCORE_ADJ=0` 可关掉子进程优先被杀 | 同上 |
| **Golden Paths GP1/GP2/GP3**（GP2 = Linux VPS Gateway + Tailscale） | `docs/golden-paths.md` |
| **不接受 PR**，GitHub Issue 不监控，唯一渠道 Discord `#golden-path-deployments` | `README.md` |
| Pinned vs Runtime 清单（`openclaw.json` 与 workspace 引导文件属 Pinned） | `docs/golden-paths.md` |
| OpenClaw 内置 Hermes 迁移器：`openclaw migrate hermes` | `docs/install/migrating-hermes.md` |
| 迁移警告：**不要让 Hermes 与 OpenClaw 共用同一个 refresh grant** | 同上 |

#### B.11.6 社区证据（issue / 论坛，带编号可追溯）

| 证据 | 编号 | 核心内容 |
|---|---|---|
| **flake 无二进制缓存** | `NousResearch/hermes-agent#130870`（open） | 每次 bump nixpkgs **重建 ~666 个 derivation**；4vCPU/8GB VPS 上 **OOM killer 两次杀掉 `nix-daemon`**；`pydantic-core`（cargo）与 `cua-driver` 是内存刺客；`sourcePreference = "wheel"` 救不了（uv2nix 仍为每个 wheel 生成 derivation） |
| **NixOS 工具闭包永远无法满足** | `#134249`（open，2026-10-07） | `check_runtime()` 每次启动警告 ffmpeg/node/npm；重建修不了；`hermes pm install --tools-only` 因 **stub-ld** 失败（`ripgrep` 静态链接反而成功） |
| `--version` 报旧版本日期 | `#135217`（open） | v0.21.6 显示 v0.21.5 的日期 |
| `hermes -V` 报 `0.0.0` | 标题含 `[Nix]` | 仅 `nix profile install` 路复现 |
| linger 修复 PR | `#110628` / salvage `#110629` | *"fix(nix): NixOS module lingers the service user so restart-safe cron workers get a user scope"* |
| dev shell 只读 `VIRTUAL_ENV` | 标题 *"Nix dev shell exports a read-only VIRTUAL_ENV to uv pip"* | 文档里"可写 `.venv`"的说法有误导 |
| `extraPythonPackages` 曾丢弃默认依赖组 | 标题 *"fix(nix): extraPythonPackages no longer drops the default package's dependency groups"* | 已修 |
| OpenClaw 被标 insecure 导致自动更新卡死 | NixOS Discourse **#76940** | 发帖人是 nixpkgs 里 OpenClaw 的维护者 `chrisportela`；原话 *"There are also a number of CVEs filed for it routinely"*；社区回答 *"No"*（无法既自动更新又不标 insecure） |

### B.12 第四轮（2026-10-12）双分支版本实测与第二十章修正

**本轮做了什么**：在 `nixos-26.05` 与 `nixos-unstable` 两个分支上，逐包比对内核 / Mesa / 游戏组件的版本，并复核第二十章的结论。**结论：第二十章 §20.1 有一处过宽表述被修正。**

#### B.12.1 双分支逐包版本比对（2026-10-12 实测）

| 组件 | 26.05 | nixos-unstable | 差异 | 核实文件（两分支同路径） |
|---|---|---|---|---|
| 内核 `linuxPackages_latest` | **7.2.9** | **7.2.9** | **无** | `pkgs/os-specific/linux/kernel/kernels-org.json`（`"7.2"`） |
| 内核 `linuxPackages`（默认） | **6.18.55**（LTS） | **6.18.55**（LTS） | **无** | 同上（`"6.18"`） |
| 内核 LTS 6.12 | 6.12.112 | 6.12.112 | **无** | 同上（`"6.12"`） |
| **Mesa** | **26.1.8** | **26.2.4** | ✅ 有 | `pkgs/development/libraries/mesa/common.nix:8` |
| **proton-ge-bin** | **GE-Proton11-1** | **GE-Proton11-7** | ✅ 有 | `pkgs/by-name/pr/proton-ge-bin/package.nix` |
| **gamescope** | **3.16.23** | **3.16.31** | ✅ 有 | `pkgs/by-name/ga/gamescope/package.nix` |
| **mangohud** | **1.91.6** | **1.91.6** | **无** | `pkgs/by-name/ma/mangohud/package.nix` |

**复验命令**（把 `<branch>` 换成 `nixos-26.05` / `nixos-unstable` 即可）：

```bash
curl -sL "https://raw.githubusercontent.com/NixOS/nixpkgs/<branch>/pkgs/os-specific/linux/kernel/kernels-org.json"
curl -sL "https://raw.githubusercontent.com/NixOS/nixpkgs/<branch>/pkgs/development/libraries/mesa/common.nix"
```

#### B.12.2 `packageAliases` 两分支逐字相同（决定性证据）

```nix
# nixos-26.05  pkgs/top-level/linux-kernels.nix:739-743
packageAliases = {
  linux_default = packages.linux_6_18;
  # Update this when adding the newest kernel major version!
  linux_latest = packages.linux_7_2;
}
// lib.optionalAttrs config.allowAliases { ... };

# nixos-unstable  同文件 :667-671 —— 与上面完全相同
```

`pkgs/top-level/all-packages.nix:8224,8227` 把这两个别名暴露为 `pkgs.linuxPackages` / `pkgs.linuxPackages_latest`。

> **结论：在 26.05 上跨源拿内核，拿不到任何东西。stable 分支会定期把内核 rebase 到最新补丁。**

#### B.12.3 跨源换内核的真正失败模式：模块树

`nixos/modules/system/boot/kernel.nix`：

```nix
:60-62   boot.kernelPackages = mkOption { default = pkgs.linuxPackages; type = types.raw; apply = ...; };
:197-202 boot.extraModulePackages = mkOption { type = types.listOf types.package; default = [ ]; };
:394     system.modulesTree = [ (lib.getOutput "modules" kernel) ] ++ config.boot.extraModulePackages;
```

**失败机制**：只要有模块往 `boot.extraModulePackages` 塞「来自稳定 nixpkgs」的包，而内核来自 unstable，模块树里就会出现「为 6.18 编译的 .ko」与「7.2 内核」并存。

#### B.12.4 Mesa 相关模块选项（26.05 源码位置）

`nixos/modules/hardware/graphics.nix`：

```nix
:38-42   mkRenamedOptionModule [ "hardware" "opengl" "package" ] → [ "hardware" "graphics" "package" ]（及 package32）
:69-75   enable32Bit = lib.mkOption { type = lib.types.bool; default = false; ... };   # ← 默认 false
:78      package   = lib.mkOption { description = "The package that provides the default driver set."; ... };
:85-90   package32 = lib.mkOption { description = "The package that provides the 32-bit driver set. Used when enable32Bit is enabled."; ... };
:144-145 hardware.graphics.package   = lib.mkDefault pkgs.mesa;
         hardware.graphics.package32 = lib.mkDefault pkgs.pkgsi686Linux.mesa;
```

**32/64 位必须一起换**；`pkgsi686Linux` 定义在 `pkgs/top-level/stage.nix:214`。

#### B.12.5 本轮对第二十章的修正

| 位置 | 原表述 | 修正后 |
|---|---|---|
| §20.1 callout | 「要"两套 nixpkgs 并存"，**唯一的位置是 flake 的 `inputs`**」 | ❌ **过宽**。不用 flake 也能做到 —— channel / `fetchTarball` / `fetchGit`+`rev` 三条路。flake 只是「最顺手」且「自动管版本号」 |
| §20.4（新增 §20.4.1） | 推荐「overlay 挂 `pkgs.unstable`」 | ⚠️ 官方论坛**不推荐** overlay（「完全没必要，很可能拖慢 eval」）。**推荐 `_module.args.pkgsUnstable`** |
| §20.5（**新增**） | — | 「不用 flake 也能做到吗？—— 能，有三条路」+ 四条路对照表 + 内核提醒 |

**姊妹文档交叉引用**：`nixos-ops-guide.md` 第六章 §6.0 / §6.2 / §6.4 ③ / §6.6 有同一发现的详版。

### B.13 第五轮（2026-10-12）第二十三章「Bazzite 模式」的新增出处

本章全部断言分两类：**Bazzite 侧的官方文档**（原文引用）与 **NixOS 侧的源码核实**。

#### B.13.1 Bazzite 侧（官方来源）

| 出处 | URL | 用在哪 |
|---|---|---|
| Bazzite 官网首页 | <https://bazzite.gg/> | §23.1 的「image based」原文、90 天镜像保留、rebase/pin、Secure by design（SELinux / Secure Boot / cosign / SBOM / LUKS+TPM）、镜像组件版本表（Kernel 7.2.9-ogc2.1 / Mesa 26.2.4 / Gamescope 3.16.31 / Distrobox 1.8.2.5 / Bazaar 0.9.3 / Waydroid 1.6.3 / InputPlumber 0.82.0 / PowerStation 0.8.4） |
| Bazzite 文档 · Introduction to Installing Software | <https://docs.bazzite.gg/Installing_and_Managing_Software/software-intro/> | §23.1 的**六层软件层级原文**（Portal → Flatpak → Homebrew → Containers → AppImage → rpm-ostree）、决策树表 |
| Bazzite 文档 · `ujust` Commands | <https://docs.bazzite.gg/Installing_and_Managing_Software/ujust/> | §23.5 的**动词体系表**（`install-` / `get-` / `setup-` / `configure-` / `toggle-` / `fix-` / `distrobox-` / 裸动词）、命令示例、recipe 路径 `/usr/share/ublue-os/just`、`ujust --choose` / `--show` |
| Bazzite 文档 · Installing and Managing Applications（索引） | <https://docs.bazzite.gg/Installing_and_Managing_Software/> | §23.1 的文档结构（Bazzite Portal / Bazaar / Homebrew / Containers / AppImage / rpm-ostree / Waydroid / Updates-Rollbacks-Rebasing 全表） |

#### B.13.2 NixOS 侧（本轮源码核实，`nixos-26.05`）

| 断言 | 证据文件 | 核实方式 |
|---|---|---|
| `programs.nh` 模块存在，选项 `enable` / `package` / `flake` / `clean.{enable,dates,extraArgs}`；`nh.clean.enable` 与 `nix.gc.automatic` 同时开会 **warning**；`nh.flake` 必须是目录（assertion） | `nixos/modules/programs/nh.nix` | 全文读取，逐选项核对 |
| `nh` 包版本 **4.4.2**，`nh-unwrapped` 描述 *"Yet another nix cli helper"*，wrapper 注入 `nix-output-monitor` | `pkgs/by-name/nh/nh/package.nix` + `nh-unwrapped/package.nix` | 全文读取 |
| `nh` 子命令全集（`os` / `home` / `darwin` / `search` / `clean`）与 `nh search` 六种调用形式 | 上游 `nix-community/nh` 的 `docs/README.md`（master） | 官方文档全文读取；`nh` 最新 release **v4.4.2**（2026-07-28，GitHub API） |
| `programs.steam.gamescopeSession` 的 `enable` / `args` / `env` / `steamArgs`，默认 `steamArgs = [ "-tenfoot" "-pipewire-dmabuf" ]`；生成 `steam.desktop` 会话；`programs.gamescope.enable` 用 **mkDefault**；`programs.steam.enable` 硬赋值 `hardware.graphics.{enable,enable32Bit}` | `nixos/modules/programs/steam.nix` | 全文读取（§23.10 逐条列出） |
| `programs.gamescope` 选项：`enable` / `package` / `capSysNice`（默认 false）/ `args` / `env` | `nixos/modules/programs/gamescope.nix` | 全文读取 |
| `virtualisation.waydroid` 只有 `enable` + `package`；自动开 `virtualisation.lxc.enable`、写 `boot.kernelParams = ["psi=1"]`、`networking.firewall.trustedInterfaces = ["waydroid0"]`、`/etc/gbinder.d/waydroid.conf`；按 `networking.nftables.enable` 自动选 `waydroid-nftables` | `nixos/modules/virtualisation/waydroid.nix` | 全文读取 |
| **NixOS 默认内核已编入 `ANDROID_BINDER_IPC` / `ANDROID_BINDERFS`（`tristate = "y"`）、`ANDROID_BINDER_DEVICES = "binder,hwbinder,vndbinder"`** | `pkgs/os-specific/linux/kernel/common-config.nix:1447-1457` | 逐行读取（**这是「NixOS 装 Waydroid 要自定义内核」说法的反证**） |
| `services.flatpak` **只有** `enable` + `package`；模块含断言 `xdg.portal.enable == true` | `nixos/modules/services/desktops/flatpak.nix` | 全文读取（证明 `remotes` / `uninstallUnmanaged` 不存在） |
| `system.autoUpgrade` 全部选项：`enable` / `operation`（enum **`switch`\|`boot`**，默认 `switch`）/ `flake` / `channel` / `upgrade`（默认 true）/ `flags` / `dates`（默认 `"04:40"`）/ `allowReboot`（默认 false）/ `randomizedDelaySec`（默认 `"0"`） | `nixos/modules/tasks/auto-upgrade.nix` | 逐选项读取 |
| `boot.loader.systemd-boot.configurationLimit` 存在，默认 `null` | `nixos/modules/system/boot/loader/systemd-boot/systemd-boot.nix:233` | 行号定位 |
| `pkgs.distrobox` = **1.8.2.5**（与 Bazzite 镜像同版本）；**无 NixOS 模块**（`nixos/modules/virtualisation/distrobox.nix` = 404） | `pkgs/by-name/di/distrobox/package.nix` | 版本字段读取 + 模块路径 404 探测 |
| `pkgs.inputplumber` **v0.77.1**（`ShadowBlip/InputPlumber`）、`pkgs.powerstation`（`ShadowBlip/PowerStation`，*"Open source TDP control and performance daemon with DBus interface"*）、`pkgs.bazaar`（`kolunmi/bazaar`，*"FlatHub-first app store for GNOME"*）、`pkgs.umu-launcher` 全部存在 | 各自 `pkgs/by-name/<2字>/<name>/package.nix` | HTTP 200 + 描述/上游字段读取 |
| `pkgs.decky-loader` = **404**、`pkgs.lanzaboote` = **404**、`pkgs.hhd` = 未找到 | by-name 探测 | HTTP 状态码 |
| `pkgs.obs-studio` 在 `pkgs/applications/video/obs-studio/default.nix`（**不在 by-name**） | 路径探测 | HTTP 200 |
| lanzaboote 上游最新 release **v1.2.0**（2026-09-26） | `api.github.com/repos/nix-community/lanzaboote/releases/latest` | GitHub API |

> [!NOTE]
> **本轮的核实方法与前三轮一致**：**Bazzite 侧的每条主张都取自官方文档原文**（不用二手转述），**NixOS 侧的每条主张都直接读 `nixos-26.05` 源码**（不用「我记得」）。两者都给了可直接复验的路径。
>
> 特别值得记下的一条：**`ANDROID_BINDER_IPC = "y"`** —— 这条推翻了社区广泛流传的「NixOS 装 Waydroid 必须自定义内核」。**这类「社区共识其实是过时信息」的案例，是本文档坚持源码核实的主要原因。**

### B.14 第六轮（2026-10-12）第二十四章「Aeon 模式」的新增出处

本章同样是**两边都一手**：Aeon 侧取官方站点与 LWN 的一手技术分析，NixOS 侧直接读 nixpkgs / Home Manager 源码。

#### B.14.1 Aeon / MicroOS Desktop 侧

| 出处 | URL | 用在哪 |
|---|---|---|
| Aeon 官网 | <https://aeondesktop.github.io/> | §24.2 三条卖点原文（Automated Maintenance / Minimal Yet Functional / Flatpak / Distrobox / Transactional Update）；`aeondesktop.org` 为同一站点 |
| **LWN · OpenSUSE MicroOS Desktop: a Flatpak-based immutable distribution**（Koen Vervloesem，2023-03-29） | <https://lwn.net/Articles/927373/> | §24.1 §24.2 的**全部技术细节原文**：基座是 *"minimal openSUSE Tumbleweed"*、Btrfs root *"mounted read-only after boot"*、`transactional-update` = zypper 包装、snapshot 失败丢弃、启动自动回滚、Flatpak 装在 `~/.local/share/flatpak`、GNOME Software *"only install Flatpaks from Flathub"*、Distrobox 容器 >75,000 RPM、`transactional-update` 装包*"only recommended for drivers, kernel modules, VPN clients"* 与 *"every extra package in the host incurs extra risk of instability"*、无防火墙是 by design |
| FOSS Wiki · Aeon | <https://foss.wiki/Aeon> | §24.1 的「Release Model: **Rolling**」、`transactional-update` 为包管理器、TIK 安装器、默认 GNOME（**该站自标「lacks citations」，仅作旁证，不作为主要依据**） |
| openSUSE 中文社区 · 改名公告 | <https://suse.org.cn/社区新闻/2023/05/27/opensuse-aeon.html> | 2023-05-27 MicroOS Desktop → Aeon 的更名背景 |

> [!NOTE]
> **关于 Aeon 的一处信息源质量提示**：openSUSE Wiki 的 `Portal:Aeon` 在本次核实期间**数据库故障**（返回 *"Cannot access the database"*），因此本章的 Aeon 侧主张**全部以 LWN 的一手技术分析 + 官网原文为据**，未使用 Wiki。FOSS Wiki 页面自带 *"little to no citations"* 警告，**只用来旁证「滚动模型」这一条**。

#### B.14.2 NixOS / Home Manager 侧（源码核实）

| 断言 | 证据文件 | 核实方式 |
|---|---|---|
| **官方 FAQ 有专节讲「怎么装 unstable 的包」**，并给出 NixOS 模块下的 `home-manager.extraSpecialArgs` 写法，**明确要求传 `config = config.nixpkgs.config; overlays = config.nixpkgs.overlays;`** | `home-manager/release-26.05/docs/manual/faq/unstable.md` | 全文读取（§24.5.1 照抄官方骨架） |
| `home-manager.useGlobalPkgs` 的语义：*"using the system configuration's `pkgs` argument in Home Manager. This disables the Home Manager options `nixpkgs.*`"* | `home-manager/release-26.05/nixos/common.nix` | 选项描述逐字读取 |
| `useGlobalPkgs = true` 时 `nixpkgs.*` **被禁用**，且有断言 + warning：*"`nixpkgs` options are disabled when `home-manager.useGlobalPkgs` is enabled."* | `home-manager/release-26.05/modules/misc/nixpkgs-disabled.nix` | 全文读取 |
| **HM 的 `pkgsPath` 默认值可覆盖**：`_module.args.pkgsPath = lib.mkDefault (if stateVersion >= "20.09" then pkgs.path else <nixpkgs>)`；且 `_module.args.pkgs = lib.mkDefault pkgs` | `home-manager/release-26.05/modules/modules.nix:119-120, 122` | 行号定位（§24.5.3 的依据） |
| HM 的 `useGlobalPkgs = false` 路径会**自己 `import pkgsPath (...)`**（`_pkgs = import pkgsPath (filterAttrs (_n: v: v != null) config.nixpkgs)`）→ 多一次 nixpkgs 求值、包哈希与系统不同 | `home-manager/release-26.05/modules/misc/nixpkgs.nix:58` | 行号定位 |
| HM 的 `nixpkgs` 模块**只有** `config` / `overlays` / `system` 三个选项（**没有 `nixpkgs.pkgs`**） | 同上，`options.nixpkgs` 段 | 逐选项读取 |
| `home-manager.extraSpecialArgs` / `sharedModules` / `users` / `useUserPackages` / `backupFileExtension` / `overwriteBackup` / `startAsUserService` / `minimal` 全部存在 | `home-manager/release-26.05/nixos/common.nix` | 全文读取 |
| `home-manager/release-26.05` 分支存在；`nixos-26.05` / `nixos-unstable` / **`nixpkgs-unstable`** 三个 nixpkgs 分支均存在（各 HTTP 200） | 分支探测 | HTTP 状态码 |

#### B.14.3 本轮的一条「前提修正」（最重要）

| 位置 | 常见误解 | 事实 |
|---|---|---|
| §24.1 | 「Aeon 的基座是**稳定的冻结版本**（像 Leap）」 | ❌ **Aeon 的基座是滚动的 openSUSE Tumbleweed**（LWN 原文）。它的「稳定」来自**原子 + 极简 + 隔离**，不是版本冻结。**这个前提搞错，后面选路会全错** |

> [!NOTE]
> **为什么这一条值得单列**：用户的问题原话是「基座是稳定，但 apps 是最新的」。这个表述隐含了「稳定 = 冻结」的假设。**而 Aeon 恰好是反例** —— 它证明了「不冻结也能稳定」，靠的是机制而非版本。**把这个前提讲清，用户才可能意识到 NixOS 上有三条路而不是一条。**

### B.15 第七轮（2026-10-12）第二十五章「二进位包与依赖问题」的新增出处

本章是**源码级核实**：全部主张来自 nixpkgs `nixos-26.05` 分支的模块源码与上游项目 README，**不依赖任何二手教程**。

#### B.15.1 nixpkgs 模块源码（逐文件读取）

| 断言 | 证据文件 | 核实方式 |
|---|---|---|
| **NixOS 主动删除 `/lib64/ld-linux-x86-64.so.2`** —— 用 `systemd.tmpfiles.rules` 的 **`r` 规则**（删除），而不是「本来就没有」 | `nixos/modules/config/ldso.nix` | 全文读取（§25.3 §25.5.4 的依据） |
| `environment.ldso` 选项存在；`programs.nix-ld` 启用后把该路径换成 **`L+` 符号链接** 指向 nix-ld 的 loader | 同上 + `nixos/modules/programs/nix-ld.nix` | 全文读取 |
| **`programs.nix-ld` 模块自带 14 个基础库**：`zlib` `zstd` `stdenv.cc.cc` `curl` `openssl` `attr` `libssh` `bzip2` `libxml2` `acl` `libsodium` `util-linux` `xz` `systemd` | `nixos/modules/programs/nix-ld.nix` | 逐项读取 `libraries` 默认值 |
| `programs.nix-ld` 的选项面：`enable` / `package` / `libraries` / `extraLibraries`（**注意没有 `NIX_LD_LIBRARY_PATH` 选项，那是模块自动导出的环境变量**） | 同上 | 逐选项读取 |
| **`pkgs.buildFHSEnv` = `buildFHSEnvBubblewrap`**（`buildFHSEnvChroot` 已弃用） | `pkgs/top-level/all-packages.nix:360-362` | 行号定位 |
| FHS 环境的**目录布局**：`/lib32`（multiPkgs 的 32 位）/ `/lib64`（multiPkgs + targetPkgs 的 64 位）/ **`/lib` → 符号链接到 `/lib64`** | `pkgs/build-support/build-fhsenv-bubblewrap/default.nix` | 源码注释原文 |
| FHS 环境**永远自动包含的基础包**：`glibcLocales` `glibc`（或 `glibc_multi`）`gcc.cc.lib` `bashInteractiveFHS` `coreutils` `less` `shadow` `su` `gawk` `diffutils` `findutils` … | 同上 | 源码原文 |
| FHS 环境的 `/etc` 从宿主 **`--ro-bind` 30 项**：`static` `nix` `shells` `bashrc` `zshenv` `zshrc` `zinputrc` `zprofile` `passwd` `group` `shadow` `hosts` `resolv.conf` `nsswitch.conf` `profiles` `login.defs` `sudoers` `sudoers.d` `localtime` `zoneinfo` `machine-id` `os-release` `pam.d` `fonts` `alsa` `asound.conf` `ssl/certs` `ca-certificates` `pki` `dconf` | 同上 | 逐项读取（§25.5.4 的 NOTE 依据） |
| FHS 环境里有一个**静态编译的 `container-init` shim**，先跑 `ldconfig` 再 `exec` 真正的 `/init`（防止 `LD_PRELOAD` 与 `fhsenv in fhsenv` 场景崩溃） | 同上 | 源码注释原文（§25.5.4 引用） |
| `buildFHSEnv` 参数面：`targetPkgs` / `multiPkgs` / `multiArch` / `includeClosures` / `runScript` / `unshareUser`/`unshareIpc`/`unsharePid`/`unshareNet`/`unshareUts`/`unshareCgroup`（**默认全 `false`**）/ `privateTmp` / `chdirToPwd`（默认 `true`）/ `dieWithParent`（默认 `true`）/ `extraInstallCommands` / `extraPreBwrapCmds` / `extraBwrapArgs` | `pkgs/build-support/build-fhsenv-common.nix` + `build-fhsenv-bubblewrap/default.nix` | 逐参数读取 |
| `programs.appimage` 模块的选项面：`enable` / `package` / `binfmt`（**注意没有 `extraPkgs`**） | `nixos/modules/programs/appimage.nix` | 全文读取 |
| `programs.appimage.binfmt` 注册的 magic 是 **`AI\x01` 与 `AI\x02`** 两种（AppImage type 1 / type 2） | 同上 | 源码原文 |
| `programs.steam` 的 `steam-run` 是 `buildFHSEnv` 的一层包装，可对任意二进制使用 | `pkgs/games/steam/fhsenv.nix` | 源码读取 |

#### B.15.2 ★ 26.05 弃用与改名（本轮最重要的时效性发现）

| 断言 | 证据文件 | 核实方式 |
|---|---|---|
| **`xorg` 包集在 26.05 已弃用** | `nixos/doc/manual/release-notes/rl-2605.section.md:235` + `pkgs/top-level/aliases.nix:2361` | 行号定位（§25.2 全表的依据） |
| **全部 `libX*` 改名为 `libx*`**（小写 x），旧名保留为弃用别名 | `pkgs/top-level/aliases.nix:1178-1207` | 逐行读取（§25.2 表格逐行对照） |
| `libXfont` → **`libxfont_1`**；`libXfont2` → **`libxfont_2`**（**注意数字位置**，不是 `libxfont1`/`libxfont2`） | 同上 | 逐行读取 |
| 弃用公告日期：`rl-2605.section.md` 标记 **2026-01-29**；改名条目标记 **2026-02-06** | 同上 | 文件内日期行 |
| **结论**：网上所有 nix-ld 教程（含大量 LLM 训练数据）写的 `pkgs.xorg.libX11` 这类写法，在 26.05 上**会打弃用警告**，未来版本会移除 | 交叉验证 | §25.2 全表 + 附录 C |

#### B.15.3 上游项目 README（非 nixpkgs）

| 出处 | URL | 用在哪 |
|---|---|---|
| nix-ld 官方 README | <https://github.com/Mic92/nix-ld> | §25.5.4 的三个 FHS 弱点原文、**「nixpkgs 的 python / node 不走 nix-ld」**（已指向 store 里的 glibc）、`pythonld` wrapper 写法、**不支持非 NixOS**、**只支持 x86_64 / aarch64** |
| nix-alien 官方 README | <https://github.com/thiagokokada/nix-alien> | §25.5.9 的三个命令（`nix-alien` / `nix-alien-ld` / `nix-alien-find-libs`）、`-l` / `-p` 参数、**dlopen 局限**、**不在 nixpkgs**、`follows` 不受支持 |
| nix-index / nix-locate | <https://github.com/nix-community/nix-index> | §25.3 诊断表里 `nix-locate --top-level` 的用法与「需要先 `nix-index` 建库」的前置条件 |

> [!NOTE]
> **关于「nix-ld 会不会影响系统自带程序」**：不会。`programs.nix-ld` 只在**默认 loader 路径**（`/lib64/ld-linux-x86-64.so.2`）上放符号链接，而 nixpkgs 构建的程序 ELF 里**硬编码了 store 里的 loader 绝对路径**，不经过这个符号链接。**唯一受影响的是「按 FHS 默认路径找 loader」的第三方二进制。**

---

### B.16 第八轮（2026-10-12）官方手册骨架核实（本指南 v1.9）

**本轮的方法与第七轮不同**：第七轮是「按主题查 nixpkgs 源码」；本轮是「**把官方手册整站拉下来，先建骨架，再按骨架补缺口**」。

**① 一手来源**

| 出处 | URL | 用在哪 |
|---|---|---|
| **NixOS Manual（stable）** | <https://nixos.org/manual/nixos/stable/> | **本轮全部新章节的骨架与原文**。下载为本地副本（1,200,007 字节）后逐节抽取 |
| 本地副本 | `.build/nixos-manual-stable.html` | 离线核查用；抽取器 `.build/extract-sec.mjs` |

**② 骨架实测（脚本统计，非估算）**

| 层级 | 总数（带 `id`） | 自动生成（`module-*` / `opt-*`） | **叙事章节** |
|---|---|---|---|
| H1 | 11 | 0 | **10**（含「NixOS Manual」总标题） |
| H2 | 491 | 314 | **177** |
| H3 | 147 | 67 | **80** |
| H4 | 44 | 10 | **34** |

**核实方法**（可复现）：

```bash
curl -sL https://nixos.org/manual/nixos/stable/ -o manual.html
# 统计带 id 的 h1/h2/h3/h4，排除 id 以 module- / opt- 开头的（= meta.doc 自动生成）
node -e '
const t=require("fs").readFileSync("manual.html","utf8").replace(/<script[\s\S]*?<\/script>/gi,"").replace(/<style[\s\S]*?<\/style>/gi,"");
const g=tag=>[...t.matchAll(new RegExp(`<${tag}[^>]*id="([^"]*)"`,"gi"))].map(m=>m[1]);
for(const tag of ["h1","h2","h3","h4"]){
  const a=g(tag), auto=a.filter(x=>/^module-|^opt-/.test(x));
  console.log(tag, a.length, "auto", auto.length, "narrative", a.length-auto.length);
}'
```

**③ 官方 5 个 Part 锚点**

| 官方 Part | 锚点 | 叙事 H2 数 |
|---|---|---|
| Preface | `preface` | 1 |
| Part I · Installation | `ch-installation` | 17 |
| Part II · Configuration | `ch-configuration` | 100+ |
| Part III · Administration | `ch-running` | 26 |
| Part IV · Development | `ch-development` | 30 |
| Part V · Contributing（5 个 H1） | — | 5 |

**④ 本轮提取的 8 组官方原文**（`.build/official/*.txt`，共约 4,700 行）

| 文件 | 行数 | 覆盖的官方锚点 |
|---|---|---|
| `01-config.txt` | 634 | `sec-configuration-syntax` / `sec-configuration-file` / `sec-module-abstractions` / `sec-modularity` / `sec-package-management` / `sec-declarative-package-mgmt` / `sec-ad-hoc-packages` |
| `02-fs-user.txt` | 477 | `ch-file-systems` / `sec-luks-file-systems` / `sec-sshfs-file-systems` / `sec-overlayfs` / `sec-user-management` / `sec-systemd-sysusers` / `sec-userborn` / `sec-restrict-usage-time` |
| `03-admin.txt` | 525 | `sec-systemctl` / `sect-nixos-systemd-general` / `sect-nixos-systemd-nixos` / `sec-rebooting` / `sec-user-sessions` / `sec-cgroups` / `sec-logging` / `ch-system-state` / `sec-nixos-state` / `sec-systemd-state` / `sec-nix-gc` / `sect-nixos-gc-boot-entries` |
| `04-containers.txt` | 398 | `ch-containers` / `sec-imperative-containers` / `sec-declarative-containers` / `sec-container-networking` / `ch-troubleshooting` / `sec-boot-problems` / `sec-maintenance-mode` / `sec-rollback` / `sec-nix-store-corruption` / `sec-nix-network-issues` |
| `05-graphics.txt` | 337 | `sec-wayland` / `sec-gpu-accel` 及 OpenCL·Vulkan·VA-API·常见问题 / `ch-profiles` + 8 个 profile 子节 |
| `06-kernel-boot.txt` | 421 | `sec-kernel-config` / `sec-linux-config-customizing` / `sec-linux-config-developing-modules` / `sec-switching-systems` / `sec-unit-handling` / `sec-activation-script` / `sec-etc-overlay` / `sec-non-switchable-system` / `sec-bootspec` |
| `07-install.txt` | 848 | `sec-obtaining` …… `sec-image-repart-appliance`（17 个安装相关章节） |
| `08-modules.txt` | 1,045 | `sec-writing-modules` …… `sec-settings-options` / `sec-nixos-tests` / `sec-writing-nixos-tests` / `sec-running-nixos-tests` |

**⑤ 本轮新增的 10 个章节与出处映射**

| 本指南章节 | 主要官方锚点 | 文件 |
|---|---|---|
| 官方手册骨架导航 | 全站骨架 | `ch26-nav.md` |
| 二十六 · 配置语法/抽象/模块化/Profiles | `sec-configuration-syntax` / `sec-configuration-file` / `sec-module-abstractions` / `sec-modularity` / `ch-profiles` | `01-config.txt` `05-graphics.txt` |
| 二十七 · 文件系统与存储 | `ch-file-systems` / `sec-luks-file-systems` / `sec-sshfs-file-systems` / `sec-overlayfs` | `02-fs-user.txt` |
| 二十八 · 用户与账户安全 | `sec-user-management` / `sec-systemd-sysusers` / `sec-userborn` / `sec-restrict-usage-time` | `02-fs-user.txt` |
| 二十九 · systemd/systemctl/日志/cgroup | `sec-systemctl` / `sect-nixos-systemd-*` / `sec-rebooting` / `sec-user-sessions` / `sec-cgroups` / `sec-logging` | `03-admin.txt` |
| 三十 · 系统状态/GC/故障排查 | `ch-system-state` / `sec-nixos-state` / `sec-systemd-state` / `sec-nix-gc` / `sect-nixos-gc-boot-entries` / `ch-troubleshooting` 五节 | `03-admin.txt` `04-containers.txt` |
| 三十一 · 容器 | `ch-containers` / `sec-imperative-containers` / `sec-declarative-containers` / `sec-container-networking` | `04-containers.txt` |
| 三十二 · 图形栈 | `sec-wayland` / `sec-gpu-accel`（含 OpenCL/Vulkan/VA-API/常见问题） | `05-graphics.txt` |
| 三十三 · 内核与系统切换内部 | `sec-kernel-config` / `sec-linux-config-*` / `sec-switching-systems` / `sec-unit-handling` / `sec-activation-script` / `sec-etc-overlay` / `sec-non-switchable-system` / `sec-bootspec` | `06-kernel-boot.txt` |
| 三十四 · 写模块与测试 | `sec-writing-modules` / `sec-option-declarations` / `sec-option-types` / `sec-option-definitions` / `sec-assertions` / `sec-meta-attributes` / `sec-replace-modules` / `sec-freeform-modules` / `sec-settings-options` / `sec-nixos-tests` 等 | `08-modules.txt` |
| 三十五 · 构建镜像 | `sec-upgrading` / `sec-upgrading-automatic` / `sec-building-image` / `sec-image-nixos-rebuild-build-image` / `sec-image-repart` / `sec-image-repart-store-paths` / `sec-image-repart-appliance` | `07-install.txt` |

**⑥ 本轮最高价值的 10 条新事实**（全部有官方原文支撑，已写入对应章节）

| # | 事实 | 官方出处 | 本指南位置 |
|---|---|---|---|
| 1 | **非 longterm 内核在「第一批新稳定内核发布时」从 nixpkgs 删除，即使在 stable 分支** | `sec-kernel-config` | §33.1 |
| 2 | **`nix-collect-garbage -d` 会删掉所有 generation 的 roots → 失去回滚** | `sec-nix-gc` | §30.3 |
| 3 | **`/boot` 满了要「删 generation」+「再 `nixos-rebuild boot/switch`」两步** | `sect-nixos-gc-boot-entries` | §30.5 |
| 4 | **`systemctl --user enable` 会链接到 `/nix/store` → GC 后死链 → 服务静默不自启** | `sect-nixos-systemd-nixos` | §29.3 |
| 5 | **`X-StopIfChanged` 默认为 true**，目的是「新 unit 绝不在旧环境里运行」 | `sec-unit-handling` | §33.6 |
| 6 | **覆盖优先级精确数字**：`mkForce`(50) < 普通(100) < `mkDefault`(1000) < 选项 default(1500) | `sec-option-definitions` | §34.5 |
| 7 | **`types.externalPath` 只校验「当前不在 store」，挡不住后续 `${}` 插值复制进 store** | `sec-option-types` | §34.4 |
| 8 | **官方明确不推荐用 overlay 换包**（*"slow down nixpkgs evaluation significantly and are harder to debug"*） | `sec-option-declarations` | §34.3 |
| 9 | **ICD 混版本静默失败**：OpenCL/Vulkan 用 `dlopen` 加载 runtime，不受构建期依赖追踪保护 | `sec-gpu-accel-common-issues` | §32.6（**并修正了第二十章的一处建议**） |
| 10 | **appliance 镜像不适合 generation 更新机制**，靠「换整镜像」或「A/B 分区」（官方点名 Chrome OS） | `sec-image-repart-appliance` | §35.6 |

**⑦ 一处对既有章节的修正**

**第二十章（flake 进阶）原本建议「只滚 `mesa`」以拿到新图形栈。本轮依据官方 `sec-gpu-accel-common-issues` 的警告修正为**：

- 要么**只滚内核 + 用 Flatpak 版应用**（Flatpak 自带 runtime，不受 nixpkgs glibc 影响）
- 要么**把 `mesa` 连同 `vulkan-loader`、`libdrm` 一起滚**（保持 ICD 链同版本）

**原因**：官方明确警告 *"the loader and the runtime may come from different nixpkgs … the loader will not report an error"* —— **只滚一个组件会产生「看起来正常但硬件加速失效」的静默故障**。

**⑧ 本轮建立的工具**（可复现，留在 `.build/`）

| 工具 | 用途 |
|---|---|
| `.build/extract-sec.mjs` | 按 `id` 从本地官方手册 HTML 抽取正文（`<pre>` 转围栏代码块、`<li>` 转列表项、`</td>` 转表格竖线） |
| `.build/validate.mjs` | 校验新章节：围栏偶数 / 无缩进 callout / callout 分类计数 |
| `.build/splice-26-35.mjs` | 双锚点幂等拼接（导航章 + 十章），含「已存在则中止」断言 |
| `.build/count2.mjs` | 统计官方手册叙事 H2/H3/H4（排除 `module-*` / `opt-*`） |

---


## 附录 C：未核实 / 存疑项

> [!NOTE]
> **本表列出本文无法从一手来源确认的结论。** 按你的要求，这些**没有当成事实写进正文**，而是明确标注。使用时请自行验证。

> [!NOTE]
> **本轮（2026-10-12 复核轮）的状态更新**：本表原有 3 条 `[部分未核实]` 已被**源码级核实解决**，条目标题加了删除线（`~~…~~`）并注明 ✅。同时本轮**新发现并修正**了正文 6 处事实错误（模块路径 5 处 + nix-ld 默认库表述 1 处），详见 §附录 B.3 与 §15.8.3 的更新。
>
> 仍在表内的条目，**要么确实需要真机实测**（如 `amdgpu.gpu_recovery` 取值、`scx` 收益），**要么一手来源不可达**（如 Reddit 被网络策略拦截），并非疏漏。

> [!NOTE]
> **第三轮（2026-10-12 新增四章）的状态更新**：本表原前 3 条关于 Hermes / OpenClaw 的 `[未核实]` 已被**源码级 + 官方文档级核实解决**，条目标题加删除线（`~~…~~`）并注明 ✅。本轮**新增 6 条**与第十九～二十二章相关的存疑项（见表格下部）。

| 项 | 状态 | 说明 |
|---|---|---|
| ~~**Hermes Agent 的 NixOS 模块确切选项名**~~ | ✅ **已核实（第三轮解决）** | 官方仓库自带 `flake.nix` + `nix/nixosModules.nix`，模块名是 **`services.hermes-agent`**（不是 `services.hermes`）。全部选项表见 §21.8 与附录 B.11.4。**原稿「建议用 `uv tool install` 装在用户目录」的结论已被 §21.11 替代** |
| ~~**OpenClaw 的完整细节**~~ | ✅ **已核实（第三轮解决）** | 配置文件确为 **`openclaw.json`**（HM 路在 `~/.openclaw/`，NixOS 路在 `/etc/openclaw/`）；`clawhub.ai` 是**插件目录站**，与 `nix-openclaw` 无关。**nixpkgs 里没有 `services.openclaw` 模块**（grep = 0）；官方的 NixOS 模块只在 `github:openclaw/nix-openclaw` 里。见 §21.5–21.7 |
| ~~**OpenClaw 的 skills 目录路径**~~ | ⚠️ **部分解决** | 已确认：**skills 由 nix-openclaw 的 activation 复制到「per-instance runtime 目录」**，并把那些目录加进 OpenClaw 的 `skills.load.extraDirs`（`[仓库]` README）。**具体绝对路径仍未逐字确认**（源码里是 `openclaw-materialize-workspace-files.sh` 动态算出来的） |
| `amdgpu.dcdebugmask` 的取值 | `[未核实]` | 该参数存在，但具体取值需按显示问题类型定；nixpkgs 无对应模块选项 |
| `amdgpu.gpu_recovery` 的效果与取值 | `[未核实]` | 未从一手来源确认 |
| **`services.scx` 对 AMD 游戏的收益** | `[未核实]` | 模块与选项已核实存在，但**收益属主观判断**，缺一手基准数据。建议先用默认调度器 |
| `LIBVA_DRIVER_NAME=radeonsi` 是否必要 | `[未核实]` | 官方手册与 AMD Wiki **均未要求**，libva 会自动选 radeonsi。属多余偏方 |
| `r8169.aspm=0` 参数 | `[社区]` | **该参数不存在**（2025-03 提案被内核拒绝）。结论来自内核邮件列表讨论，非正式文档 |
| `r8169` 对 RTL8125 的稳定性 | `[社区]` | 「r8169 覆盖 RTL8125 但偶有 ASPM 掉线」来自社区经验，**未找到权威一手出处** |
| `hardware.enableRedistributableFirmware` 对有线网卡的必要性 | `[社区]` | 逻辑上 Realtek 需要 `rtl_nic/*.fw`；**具体哪些型号必需未逐一核实** |
| `plasma-login-manager` 是否已取代 SDDM | **来源冲突** | 26.05 官方 Wiki 称它是「Plasma 默认登录器」，但 `plasma6.nix` 源码仍以 **SDDM** 为默认。**以源码为准** |
| GNOME 分数缩放的声明式方案 | `[社区]` | 只能 gsettings，**无 NixOS 选项**；这意味着它不在配置版本控制内 |
| `qt.platformTheme = "gnome"` 深色模式问题 | `[Wiki]` | 26.05 已知问题，绕过方案（`qadwaitadecorations`）来自 Wiki 而非官方 release notes |
| Flatpak 主题统一的方案 | `[社区]` | nixpkgs **无原生解**；`flatpak override` 方案来自社区实践 |
| **中文输入法在 Flatpak 应用内** | `[未核实]` | 部分应用沙箱内输入法失效是普遍报告，但**未找到系统性的一手测试数据** |
| `hardware.graphics.package` 换 Mesa 版本对 AMD 的影响 | `[未核实]` | 选项存在，但「换成 unstable Mesa 后 AMD 表现如何」缺实测数据 |
| 各启动器包的 license 是否为 unfree | `[未核实]` | 未逐包核实；取决于运行时组件 |
| 中文镜像源的长期可用性 | `[未核实]` | 镜像由高校维护，**可能停服或变更**。已在配置里保留官方源作回退 |
| **`scx_lavd` 对 AMD 桌面游戏的实测收益** | `[未核实]` | 只知道它由 **Igalia 受 Valve 委托**、为 Steam Deck 游戏负载设计（`[媒体]`）。**没有一手基准数据**。任何「提升 X%」的说法都缺可复现条件 |
| **`scx` 各调度器之间的取舍** | `[未核实]` | 上游文档描述的是**设计意图**，不是实测对比。建议自己 A/B |
| **`WINENTSYNC` / `PROTON_USE_NTSYNC` 环境变量名** | `[社区]` | 来自 Proton-GE / Proton issue 讨论，**未从 Proton 官方文档确认** |
| **Proton 是否默认启用 ntsync** | `[未核实]` | 若默认启用，那「为 ntsync 换 zen」的价值更高；否则更低。未确认 |
| **`ntsync` 设备节点名是否为 `/dev/ntsync`** | `[未核实]` | udev 规则里的 `KERNEL=="ntsync"` 来自推断，需 `ls /dev` 实测确认 |
| **EPP 的声明式写法时序** | `[部分未核实]` | `systemd.tmpfiles` 写 sysfs 可能早于 `amd_pstate` 初始化。建议改用 udev 或延后的 systemd 服务 |
| **`split_lock_mitigate=0` 的实际收益** | `[社区]` | 机理明确（关掉 misery mode），但**对具体游戏的收益未实测**。建议 A/B |
| **`services.ananicy` 与 `scx` 的交互** | `[未核实]` | 两者都调优先级，可能重叠。未找到权威说明 |
| **`services.irqbalance` 在 AMD 桌面上的收益** | `[未核实]` | 现代内核 IRQ affinity 已不错，收益可能接近 0 |
| **`linux_zen` 在 AMD 上是否真的优于默认 6.18** | `[未核实]` | 编译期差异已核实（§14.2 表），但**「差异是否转化为可感知的体验提升」没有一手基准** |
| **`mcp-nixos` 之外的 MCP server 在 nixpkgs 的覆盖度** | `[未核实]` | 只核实了 `mcp-nixos` 存在（200）。其余 MCP server 是否已打包未逐一核查 |
| **SearXNG MCP server 的确切包名与参数** | `[未核实]` | 生态里多个实现，参数各异。§16.2.4 给的是**思路**，不是可直接复制的配置 |
| ~~`pkgs.rustup` 的确切属性路径~~ | ✅ **已核实（本轮解决）** | `pkgs/top-level/all-packages.nix:4396` → `rustup = callPackage ../development/tools/rust/rustup { };`。by-name 下确实无（`pkgs/by-name/ru/` 无 `rustup`），但 **`pkgs.rustup` 属性有效、可直接用** |
| ~~`pkgs.pnpm` / `pkgs.yarn` 的确切属性~~ | ✅ **已核实（本轮解决）** | `pkgs.pnpm` = `pnpm_11`（`all-packages.nix:2967`）；**`pkgs.yarn` 就在 by-name**（`pkgs/by-name/ya/yarn/package.nix`，原稿误记为 404）。另有 `pnpm_8/9/10/10_29_2/10_latest/12`、`yarn-berry` / `yarn-zpm` |
| **`programs.nix-ld.libraries` 的「够用集合」** | `[部分核实]` | **模块已自带 14 个基础库**（原稿「默认 `[ ]`」表述已修正，见 §15.8.3）。「哪些额外库能覆盖 90% GUI 场景」仍是经验值 —— Wiki 给了社区维护的长清单（`libGL` / `libxkbcommon` / `gtk3` / `xorg.*` / `vulkan-loader` / `libgbm` …），按报错逐步补 |
| **Reddit 的社区数据** | `[未找到]` | `old.reddit.com` 返回 **Blocked**，无法抓取。已用 NixOS Discourse / Arch BBS / HN 替代并标注 |
| **`hardware.cpu.amd.updateMicrocode` 是否该开** | `[核实·源码]`（默认值）+ `[未核实]`（收益） | **默认 `false`**（已核实源码）。但「开了之后对稳定性/性能的影响」未实测 |
| **NixOS 的 SELinux 支持路线** | `[未找到]` | 26.05 无模块（已核实）。**是否有计划支持**未找到官方声明 |
| **CachyOS 的 `audio-pm-ctl` / `pci-latency` 是否有等价实现** | `[未找到]` | 两者是 CachyOS 自研脚本（`usr/lib/udev/audio-pm-ctl`、`usr/bin/pci-latency`），nixpkgs 无对应包。§18.5 已标为「抄不了」 |
| **`kernel.sysrq` 在 NixOS 默认内核的出厂值** | `[未核实]` | CachyOS 显式设 `1`；NixOS 未设置该项，实际值取决于内核 Kconfig 的 `MAGIC_SYSRQ_DEFAULT_ENABLE`，未逐项核实 |
| **NixOS 上 user manager 的 `DefaultLimitNOFILE` 声明式写法** | `[未核实]` | `systemd.settings` 只作用于 system manager（已核实）。user manager 需 `/etc/systemd/user.conf.d/` drop-in，**该 drop-in 的支持范围未核实** |
| **`systemd.services."user@".serviceConfig.Delegate` 与 NixOS 现有定义的合并行为** | `[未核实]` | 选项路径有效，但与 NixOS 自身对 `user@` 的配置是否冲突未实测。改前先 `systemctl cat user@.service` |
| **CachyOS 是否默认启用 `uksmd`** | `[未核实]` | `uksmd` 是 CachyOS 提供的组件，**是否默认开启未确认**。本文只用 nixpkgs 的 `hardware.ksm` 作等价替代 |
| **`kyber` 与 `none` 在 NVMe 上的实际差异** | `[未核实]` | CachyOS 选 `kyber`，多数游戏指南选 `none`。两者都在内核里可用（编译配置已核实），但**没有一手对比数据** |
| **`hardware.ksm` 在桌面/游戏场景的收益** | `[未核实]` | 模块存在且行为明确（写 `/sys/kernel/mm/ksm/run`），但收益与代价的比例无实测 |
| **`vm.dirty_bytes` 与 NixOS 默认 `dirty_ratio` 的交互** | `[部分未核实]` | 「二者互斥、设一个会清零另一个」为内核文档所述；**NixOS 默认具体用哪个未逐项核实** |
| **nixpkgs 中其它 CachyOS 相关包的覆盖度** | `[未核实]` | 只逐项核实了 `ananicy-rules-cachyos`（200）与若干 404（`uksmd` / `proton-cachyos` / `cachyos-settings` / `scx-scheds`），**未做全仓库穷举**。✅ 本轮复核确认：这 4 个 404 成立；另 `pkgs/by-name/` 下**无** `scx`（scx 在 `pkgs/os-specific/linux/scx/`，是 200） |
| **CachyOS 各 scx 调度器的默认选择** | `[部分未核实]` | 已知 CachyOS 提供 `scx-scheds` 并支持 `scx_lavd` / `scx_rustland`（`[仓库]` DeepWiki），但**「哪个是 CachyOS 默认」未从一手配置确认** |

#### 附录 C 补充：第十九～二十二章的新增存疑项（2026-10-12 第三轮）

| 项 | 状态 | 说明 |
|---|---|---|
| **Hermes flake 在「不 update」情况下的实际构建量** | `[未核实]` | 已知 **update 后**约 666 个 derivation（`#130870`）。**首次安装**的实际构建量、以及「只 `nixos-rebuild switch` 不 update」时的增量，**没有实测数字** |
| **~666 这个数字的机器相关性** | `[未核实]` | 报告来自 4 vCPU / 8 GB VPS。**在 16 核 / 32 GB 机器上是几分钟还是几十分钟，无数据** |
| **`programs.nix-ld` 能否修复 Hermes 的 stub-ld 问题** | ❌ **不能**（逻辑推断） | §22.3 已说明理由：Hermes 的 PM 校验逻辑不经过 nix-ld 的垫片路径。**但这是推断，未实测验证** |
| **`#134249` 的警告在实际使用中是否影响功能** | `[部分未核实]` | issue 里 `ripgrep`（静态）与 `ffmpeg`/`node`/`npm`（动态）行为不同已确认；**「警告刷屏但功能正常」这一结论来自官方给出的 workaround 说明，不是端到端实测** |
| **OpenClaw 的 `runtimePlugins` 完整可选值** | `[未核实]` | §21.5 只给了 `discord` / `copilot` 两个例子（来自 README）。完整目录在 `plugin-catalog.nix` 里，未逐项读出 |
| **Hermes HM 模块与 NixOS 模块共存时的行为** | `[未核实]` | 官方文档说两者选项集相同但**没有说明同时导入会怎样**（例如 `home-manager.users.<n>` 里再开一次 `services.hermes-agent`）。**不建议同时用**，但冲突的具体表现未实测 |
| **`0xrsydn/nix-hermes-agent` 是否真的没有 linger 处理** | `[核实·源码]`（限定版本） | 本轮 grep `module.nix` 命中 0。**这是对 2026-10-11 那一版的结论**，作者可能后续补上。使用前请自己 `grep -n linger` 复验 |
| **Discord `#golden-path-deployments` 里的实际内容** | `[未找到]` | Discord **无法通过 HTTP 抓取**（需登录 + 客户端协议）。§22.8 只能给出「渠道在哪」，**给不出「那里说了什么」** |
| **OpenClaw 的 `openclaw.json` 在 HM 路下是否真是符号链接** | `[核实·源码]`（限定行） | 依据是 `config.nix` 里的 `ln -sfn ${item.configFile} ${resolvePath item.configPath}`。**未在真机上 `ls -l` 确认** |
| **`hermes --version` 报 `0.0.0` 是否已修** | `[未核实]` | issue 标题是 `[Bug]`，本轮未查其 state。**修了与否请自己查 issue 状态** |

#### 附录 C 补充：第四轮（2026-10-12 双分支实测）的新增存疑项

| 项 | 状态 | 说明 |
|---|---|---|
| **26.05 的 `linuxPackages_latest` 是否长期等于 unstable** | `[核实·源码]`（快照）+ `[未核实]`（长期） | **2026-10-12 实测逐字相同（都是 7.2.9）**。但两分支各自 rebase，**下次动手前应重新比对 `kernels-org.json`** |
| **纯 AMD/Intel 跨源取 unstable 内核** | `[未核实]` | 逻辑上无模块配对问题（amdgpu/i915 在主线内核里），但**无收益**（版本相同），故**没有实测案例**，也没有社区先例 |
| **`builtins.fetchTarball` 不加 `sha256` 的实际行为** | `[官方]`（语义）+ `[未核实]`（实测） | Nix 会给出警告并要求确认；「每次求值都重新下载」是文档语义，**未逐次实测** |
| **`builtins.fetchGit` + `rev` 在 `nixos-rebuild` 下的求值开销** | `[未核实]` | `fetchGit` 会克隆仓库到 store；**对 eval 时间的影响未实测**（nixpkgs 仓库很大，可能有明显开销） |
| **`_module.args.pkgsUnstable` 相对 overlay 的实际 eval 时间差** | `[官方论坛]`（定性） | 论坛原话是「很可能拖慢 eval」，**没有基准数字**。定性结论可信，定量未测 |

#### 附录 C 补充：第五轮（2026-10-12 第二十三章 Bazzite 对照）的新增存疑项

| 项 | 状态 | 说明 |
|---|---|---|
| **NixOS 上 `inputplumber` / `powerstation` 是否真能驱动掌机** | `[未核实]` | 包**存在**已源码核实（§23.11）。但「在 NixOS 上装完能像 Bazzite 那样识别各机型手柄 / 控 TDP」**未实测** —— 缺 udev 规则、服务定义、机型数据库这三块接线 |
| **`virtualisation.waydroid` 在 AMD 显卡上的图形性能** | `[未核实]` | 模块选项已源码核实。Waydroid 走的是 `gbinder` + LXC，**渲染路径是否用上 AMD GPU 未验证** |
| **`waydroid` 与 AppArmor / devices cgroup 的冲突** | `[未核实]` | §23.12 已标注。NixOS 无 SELinux 模块（§17.1），但若启用 AppArmor 严格策略可能挡住 `/dev/binder*` |
| **`programs.steam.gamescopeSession` 的 HDR 在 26.05 是否可用** | `[未核实]` | 选项与默认参数已源码核实；**HDR 是否亮取决于 gamescope 版本 + Mesa + 显示器**，与配置正确性无关（§23.10 警告框） |
| **Bazzite 的 `Gamescope 3.16.31` 与 nixpkgs 上游 gamescope 的行为差异** | `[未核实]` | Bazzite 用自建 spec（含补丁），nixpkgs 用上游。**补丁清单未逐项比对** |
| **`nh search` 的 elasticsearch 端点在中国大陆的可达性** | `[未核实]` | `nh search packages` 走 `search.nixos.org` 的 ES API；**未实测是否需要代理**（第十二章测过网站可达，但那是网页不是 API） |
| **`nh` 的 `nh os` 代际管理交互是否满足「Portal 式」需求** | `[主观]` | §23.15 给的「接近度 60%」是**判断**，不是测量 |
| **`pkgs.bazaar` 在 nixpkgs 的版本与 Bazzite 的 0.9.3 是否一致** | `[未核实]` | 上游同为 `kolunmi/bazaar`；**nixpkgs 26.05 快照的具体版本号未读出** |
| **Bazzite 的 90 天镜像保留是否有官方书面承诺** | `[官方]`（措辞）+ `[未核实]`（SLA） | 官网原文是 *"Images of the operating system are retained in our repositories for ninety days"*，**但这是描述现状，不是 SLA** |
| **`hhd`（Handheld Daemon）是否有 nixpkgs 打包计划** | `[未找到]` | by-name 探测未命中；**是否有 PR 在途未查** |

> [!NOTE]
> **本章的存疑项有一个共同特征：全部是「能不能组装起来」的问题，而不是「零件存不存在」的问题。**
>
> 零件存在性是**源码级已核实**的（§23.11 的表）；组装效果需要**真机 + 具体机型**，本文无法替代。**这也是本章与前面各章在证据性质上的区别** —— 前面各章多是「选项存不存在 / 默认值是什么」这类可静态核实的问题，本章的剩余问题都是动态的。

#### 附录 C 补充：第六轮（2026-10-12 第二十四章 Aeon 对照）的新增存疑项

| 项 | 状态 | 说明 |
|---|---|---|
| **NixOS 是否有「启动失败自动回滚」的实现** | `[未核实]` | Aeon 有（LWN 原文：*"if the system detects a problem during the reboot, it automatically rolls back"*）。NixOS 需手动在启动菜单选。**nixpkgs 内未见对应模块**，但**是否有第三方方案未查**（§24.7 已标为本文最弱的一项） |
| **`home-manager.useGlobalPkgs = false` 的实际代价** | `[推断]` | 「多一次 nixpkgs 求值 + 包哈希不同无法共享」是**源码推断**（`_pkgs = import pkgsPath ...`），**没有实测的内存/时间数字** |
| **`pkgsUnstable` 不传 `config` 时的具体报错** | `[推断]` | §24.5.1 写的 *"has an unfree license"* 是**基于 nixpkgs unfree 机制的推断**，未实际触发验证 |
| **`_module.args.pkgsPath` 在 HM 用户级覆盖是否完全无副作用** | `[未核实]` | 机制上 `mkDefault` 可覆盖已核实（`modules.nix:119`），但**与 `useUserPackages` / `users.users.<n>.packages` 的交互未实测** |
| **Aeon 当前的镜像版本 / 组件版本** | `[未核实]` | LWN 那篇是 **2023-03** 的，其中「3,600 个 Flatpak」「75,000 个 RPM」是**当时数字**，现在必然不同。**本章引用时已标注为历史数据** |
| **Aeon 是否仍默认不装防火墙** | `[媒体·2023]` | 来自 2023 年 LWN 转述 Richard Brown 的说法。**2026 年的现状未核实** |
| **Aeon 的「无全盘加密」是否已解决** | `[媒体·2023]` | 2023 年 LWN 说 FDE 不支持、等「停用 YaST 之后」。**现状未核实**（Aeon 已改用 TIK 安装器，可能已支持） |
| **`nixpkgs-unstable` 与 `nixos-unstable` 两个分支的差异** | `[官方]`（存在性）+ `[未核实]`（差异细节） | 两分支均 HTTP 200；HM 官方 FAQ 用的是 **`nixpkgs-unstable`**（HM 开发针对该分支）。**但两者包版本是否逐字相同未实测** |
| **路 C 里「只滚 mesa」的长期风险** | `[未核实]` | mesa 跨大版本可能与基座内核/`libdrm` 有 ABI 约束。§20 已讨论，**无长期跟踪数据** |

> [!NOTE]
> **本章存疑项的分布很集中**：一半是**Aeon 侧信息时效性**（LWN 是 2023 年的，Aeon 已多次迭代），一半是**HM 双 pkgs 的实测空白**（机制已源码核实，效果未量化）。
>
> **Aeon 侧的时效性问题是本章的固有局限** —— 官方 Wiki 在核实期间数据库故障，只能退回 2023 年的一手技术分析。**如果你要用 Aeon 的具体数字（Flatpak 数量、默认配置），请以 aeon 官网/文档的当前版本为准。**

#### 附录 C 补充：第七轮（2026-10-12 第二十五章 二进位包与依赖）的新增存疑项

| 项 | 状态 | 说明 |
|---|---|---|
| **`programs.nix-ld.libraries` 的「万能起步集」是否真能覆盖 90% GUI 程序** | `[经验值]` | §25.6 ⑪ 那份清单是**按类别拼的经验集合**，不是官方列表。**没有「跑 N 个程序、成功 M 个」的实测统计** |
| **nix-ld 的 `NIX_LD_LIBRARY_PATH` 是否对所有 `execve` 场景生效** | `[官方]`（机制）+ `[未核实]`（边界） | 机制明确（模块导出环境变量 + loader 读它）。**但对「程序内部再 `exec` 子进程」「setuid 程序」这两类边界未实测** |
| **`buildFHSEnv` 的 `/etc` 30 项绑定在 26.05 是否已变动** | `[核实·源码]`（快照）+ `[未核实]`（长期） | 30 项来自 `build-fhsenv-bubblewrap/default.nix` 的 2026-10 快照。**上游可能增删**，使用前 `grep -n ro-bind` 复验 |
| **`xorg` 包集的别名会保留到哪个版本** | `[未核实]` | `aliases.nix` 保留了旧名映射，但**未标注移除时间表**。官方 release note 只说「deprecated」 |
| **`libX*` → `libx*` 改名是否影响所有下游包** | `[未核实]` | 改名在 `aliases.nix` 层做了兼容，**理论上不影响已构建的包**。但「用户手写配置里引用旧名」会警告，**长期是否会硬失败未确认** |
| **`programs.appimage.binfmt` 的 `AI\x01` / `AI\x02` 是否覆盖 type 3 AppImage** | `[核实·源码]`（两种 magic）+ `[未核实]`（type 3） | 源码只注册这两种。**AppImage type 3（用 `bsdtar` 容器）是否可用未确认** |
| **nix-alien 在 26.05 上的可用性** | `[未核实]` | 项目 README 描述的是通用行为。**是否已适配 26.05 的 `xorg` 改名（`nix-alien-find-libs` 内部可能引用旧名）未验证** |
| **`steam-run` 对「非游戏二进制」的通用性边界** | `[官方]`（机制）+ `[未核实]`（边界） | 机制上是 `buildFHSEnv` 包装，**理论通用**。但 Steam 的 FHS 环境带了不少游戏向库，**对非游戏程序是否有副作用未实测** |
| **`nix-locate` 数据库的更新频率与体积** | `[未核实]` | 需要 `nix-index` 建库（首次约几分钟、占数百 MB）。**26.05 上的确切体积与耗时未实测** |
| **`pkgs.dpkg` / `pkgs.rpm` 解包 `.deb` / `.rpm` 到用户目录的完整流程** | `[推断]` | §25.5.11 给的思路（解包 + nix-ld）**逻辑成立，但未端到端实测某个真实 `.deb`** |
| **`boot.binfmt.emulatedSystems` 跑 aarch64 二进制的性能代价** | `[官方]`（机制）+ `[未核实]`（性能） | qemu-user 模拟有开销。**具体倍率未测**，且**部分程序（如需要 JIT 的）可能直接不工作** |
| **`programs.nix-ld` 与 `programs.appimage` 同时开启是否冲突** | `[未核实]` | 两者机制不同（loader 符号链接 vs binfmt 注册），**理论不冲突，但未实测共存场景** |

> [!NOTE]
> **本章存疑项的分布特征**：绝大多数是**「机制已核实、边界未实测」**。这一章与前几章不同 —— 它的核心机制（loader 路径、`/etc` 绑定、binfmt magic、`xorg` 改名）**全部是源码级已核实的**；剩下的是「这套机制在具体程序上的覆盖度」，**只能靠真机逐个试**。
>
> **最值得你警惕的一条**：§25.2 的 `xorg` 改名。**这是唯一一条「不知道就会照着旧教程配错」的事实**，而且它影响的是网上绝大多数 nix-ld 教程。

#### 附录 C 补充：第八轮（2026-10-12 官方手册骨架核实）的新增存疑项

| 项 | 状态 | 说明 |
|---|---|---|
| **26.05 默认的 stage 1 是 scripted 还是 systemd** | `[官方措辞有歧义]` | 官方 `sec-boot-problems` 同时给了「scripted stage 1 调试图参数」和「systemd stage 1 替代方案」两套。**官方没有明说 26.05 默认用哪个**。§30.6 已把两套都列出并标注歧义 |
| **NixOS 容器「not perfectly isolated」的具体原因** | `[官方结论]` + `[推断·原因]` | 官方原文只说 *"not perfectly isolated"* 并警告「不可给不受信任用户 root」。**具体是哪几项隔离缺失（共享 store / 共享内核 / 无 user namespace？）官方未列举**。§31.1 的推断已标注 |
| **`image.repart` 的 `repartConfig` 完整键表** | `[官方]`（机制）+ `[未核实]`（全集） | 官方原文只说 *"exposes its entire interface"*，**手册里不列全集**。§35.4 给的 7 个键是从官方各例子里出现的，**不是权威全集** —— 查 `man systemd-repart` |
| **`sec-building-image` 里「强制设定」的确切清单** | `[推断]` | 官方原文只说 *"know how to enforce configuration settings on which they immediately depend"*，**未列出具体哪些选项**。§35.2 的四项是推断 |
| **`nixos-rebuild build-image` 在 26.05 的可用变体清单** | `[官方]`（命令存在）+ `[未核实]`（清单） | 官方原文说「不加参数会列出全部变体」，**但未列出内容**。§35.3 列出的变体名是**举例，不是实测输出** |
| **UKI Appliance 例子的实际可引导性** | `[官方示例]` + `[未核实]` | 官方给的是完整例子，**但本文没有在 QEMU 里实际构建并引导过**。§35.6 的 QEMU 命令是**推断可用** |
| **`image.modules` 的「extendable」具体机制** | `[官方措辞]` + `[未核实]` | 官方原文说变体「defined - and extendable - in `image.modules`」，**但没给「如何加自己的变体」的例子** |
| **`specialisations` 与 `image.modules` 的相似度** | `[官方类比]` | 官方原文用 *"in a similar fashion as specialisations"* 类比，**但两者的求值时机是否真的一致未核实** |
| **`nixStorePrefix` 的完整取值语义** | `[官方示例]`（两种用法）+ `[推断]`（取值表） | 官方只给了 `"/"` 和 `"/@nix-store"` 两个例子。§35.5 的三行取值表**第二行（默认不重写）是推断** |
| **`system.autoUpgrade` 在 flake 模式下的确切行为** | `[推断]` | §35.1 说它会先跑 `nix flake update`。**这是从 `system.autoUpgrade.flake` 选项的存在反推的，未读到官方对该选项的完整描述** |
| **small 频道「更少更新但关键补丁更快」的准确语义** | `[官方原文有歧义]` | 官方原文 *"identical … except that they are only updated … faster than the regular channels"* 读起来自相矛盾。§35.1 的解释是**推断** |
| **本指南「官方顺序 ≠ 本指南顺序」的设计原则** | `[本指南自述]` | 这是本指南的组织决策，**不是官方立场**。官方手册本身没有讨论「教学顺序 vs 参考顺序」 |

> [!NOTE]
> **第八轮存疑项的特征**：**全部集中在「构建镜像」这一章**（§35 占 9 条）与两处**官方原文歧义**（stage 1、small 频道）。
>
> **为什么 §35 存疑项密集**：因为「构建镜像」是本指南**唯一一章完全没有实操验证**的 —— 它需要额外的硬件/虚拟化环境，而本文的其余章节都能在目标机器上直接跑。
>
> **使用建议**：§35 的所有命令**请先在有备份的环境里试**。特别是 §35.6 的 appliance 例子 —— 它是官方示例，但**本文未验证过**。

---


## 附录 D：与姊妹文档的关系

本文是**面向你具体配置的教学指南**。更深的理论推导、NVIDIA 相关内容、以及完整的出处链，见：

| 文档 | 内容 |
|---|---|
| `nixos-ops-guide.md` | 通用深度手册（10 章）：NixOS 心智模型完整推导、三条配置路线对比、NVIDIA 显卡、非 Nix 程序四种方案、混合版本策略、LLM 辅助管理、生态查询工具链 |
| `distro-ai-ops-landscape.md` | 发行版「AI 协同管理」全景调研（哪些发行版真的有 MCP / skills / AI 运维方案） |

**两份文档的分工**：

- **本文** = 「照着我这份配置做」+「为什么这么配」
- **`nixos-ops-guide.md`** = 「NixOS 为什么这样设计」+「换成别的硬件怎么办」

**2026-10-12 第三轮新增四章后的分工补充**：第十九～二十二章（三套管理方案的定位、flake 进阶、Hermes/OpenClaw 落地、坑与社区意见）**只存在于本文**，姊妹文档没有对应章节。原因是这四章都围绕**「AMD 桌面 + 单用户 + 想让 agent 管系统」**这个具体画像写的，属教学指南的职责范围。若你要的是**通用**的「NixOS 上的 agent 部署」方法论（不限于这两个软件），那需要另外一份文档，本文尚未提供。

| 本文新增章 | 与姊妹文档的关系 |
|---|---|
| 十九（三套管理方案定位） | 姊妹文档「三条配置路线对比」的**实操版**：那边讲原理，这边给裁决表 |
| 二十（flake 进阶） | 姊妹文档「混合版本策略」的**可复制实现**（多 nixpkgs input + overlay / `_module.args`；含**不用 flake 的三条路**） |
| 二十一（Hermes/OpenClaw 落地） | **本文独有**。姊妹文档只提了「LLM 辅助管理」的理念，没有具体软件的服务化方案 |
| 二十二（坑与社区意见） | **本文独有**。全部证据来自 2026-10-12 的 issue / 源码 / 论坛核实 |
| 二十三（Bazzite 模式对照） | **本文独有**。这是一份**发行版使用模式映射**（Bazzite → NixOS），姊妹文档的定位是「NixOS 内部原理」，不涉及与其他发行版的对照 |
| 二十四（Aeon 模式：稳定基座 + 最新应用） | **本文独有**，但与姊妹文档的「混合版本策略」章**互补**：那边讲「为什么可以混」，这边讲「怎么组织成稳定基座 + 追新应用」。**HM 官方 FAQ 的 `pkgsUnstable` 写法**是本轮新增的一手材料 |

---

## 附录 E：还可以补充什么（Roadmap）

> 按用户要求「仔细思考还有什么资料可以补充」。以下是**本次没有展开、但对你可能有用**的方向，按价值排序。

### E.1 高价值（建议下一轮补）

> [!NOTE]
> **2026-10-12 第三轮更新**：下表原前四项中的三项已在本轮完成，已加删除线并注明落点。新增"仍未做"的方向见 E.1.1。

> [!NOTE]
> **2026-10-12 第五轮更新（新增第二十三章）**：用户第 8 问的最后一条「如何让 NixOS 做到类似 Fedora Bazzite 的使用模式」已**独立成章**（第二十三章，17 节）。原 E.3 里被判定为「补不了」的两项（**SteamOS 的 Gaming Mode UI**、**掌机 TDP 控制**）已被**部分推翻** —— 见 E.3 的更新标注。

> [!NOTE]
> **2026-10-12 第六轮更新（新增第二十四章）**：新增「**openSUSE Aeon 模式：稳定基座 + 最新应用**」（10 节）。**这是对用户第 8 问之后的新提问的独立成章**，材料来自 **Home Manager 官方 FAQ 的 `unstable.md` 专节**（本轮首次取到）+ nixpkgs / HM 源码。同时**修正了一个前提**：Aeon 的基座是**滚动的 Tumbleweed**，不是冻结版本（见 §24.1 与附录 B.14.3）。

> [!NOTE]
> **2026-10-12 第七轮更新（新增第二十五章）**：新增「**二进位包与依赖问题：完整手册**」（11 节）。这是对用户新提问「NixOS 如何使用二进位包？如何解决依赖问题？给出全面的方式，考虑所有的可能和程式类型、常见依赖」的独立成章。**本轮产生了一条影响面最广的时效性发现**：`xorg` 包集在 26.05 已弃用、`libX*` 全面改名 `libx*`（§25.2 / 附录 B.15.2）—— **网上所有 nix-ld 教程（含大量 LLM 训练数据）用的都是旧写法**。

> [!NOTE]
> **2026-10-12 第八轮更新（以官方手册结构为骨架 + 新增第二十六～三十五章）**：这一轮的性质与前三轮**完全不同**。
>
> **前三轮是「按你的提问补内容」；本轮是「按官方手册的结构系统性找缺口」。**
>
> **做法**：把官方手册 stable（= NixOS 26.05）整站拉下来 → 脚本统计出 **10 个 H1 / 177 个叙事 H2 / 80 个 H3**（排除 314 个 `module-*` 自动生成章节）→ 做成**双向对照表**（新增「官方手册骨架导航」章）→ 逐条标注覆盖度 → **把 10 个缺口写成第二十六～三十五章**。
>
> **本轮的关键决策**（你通过选择确认）：
> - **骨架导航 + 补齐缺口**，而不是物理重排全文 —— **保留现有 25 章编号**，不破坏 §x.y 交叉引用
> - **面向你的画像精选** —— 跳过 ZFS / Xen / Kubernetes / Pantheon / Mattermost / Suwayomi 等服务类章节
>
> **本轮最高价值的 5 条新事实**：
> 1. **非 longterm 内核会从 nixpkgs 删除，即使在 stable 分支**（§33.1）—— 解释了「为什么写死内核小版本号会突然构建失败」
> 2. **ICD 混版本静默失败**（§32.6）—— **并据此修正了第二十章「只滚 mesa」的建议**
> 3. **覆盖优先级精确数字**：`mkForce`(50) < 普通(100) < `mkDefault`(1000) < 选项 default(1500)（§34.5）
> 4. **`systemctl --user enable` 会因 GC 变成死链**（§29.3）—— 一个「静默失效」的经典陷阱
> 5. **`nix-collect-garbage -d` 会删掉所有回滚能力**（§30.3）

| 主题 | 为什么值得补 | 需要什么证据 |
|---|---|---|
| ~~**Hermes Agent 的 Nix flake 确切用法**~~ | ✅ **已完成**（第二十一章 §21.8–21.10；第二十二章 §22.2–22.7） | 已取官方 `nix/nixosModules.nix` + `homeManagerModules.nix` + `nix-setup.md` 全文 |
| **OpenClaw 的 skills 目录结构** | 第十章讲了 skills 概念，但具体路径/加载机制未核实 | 官方仓库文档 |
| ~~**sops-nix / agenix 完整配置**~~ | ⚠️ **部分完成**：第二十一章给了 Hermes 侧的 sops-nix / agenix 接法（`environmentFiles` + `authFile`），但**完整的 age key 生命周期管理仍未展开** | 两个项目的 README + NixOS 集成示例 |
| ~~**Home Manager 完整迁移**~~ | ✅ **已完成**（第十九章全章 + 第二十一章的 HM 模块落地） | HM option 文档 + 官方模块源码 |
| ~~**flake + 混合版本（stable 基座 + rolling 组件）的完整实现**~~ | ✅ **已完成**（第二十章全章，含 `pkgs.unstable` 三种写法、`follows` 的坑、**不用 flake 的三条路**） | nixpkgs-unstable 输入 + overlay / `_module.args` 写法 |
| ~~**Bazzite 使用模式的完整对照**~~ | ✅ **已完成（第五轮，第二十三章）**：六层软件层级逐条映射 + `nh` 与 `ujust` 对照 + 掌机工具链在 nixpkgs 的现状 + 四个反模式 | Bazzite 官方文档全文 + `nixos-26.05` 源码逐条核实（见附录 B.13） |
| ~~**「稳定基座 + 最新应用」的完整组织方式**~~ | ✅ **已完成（第六轮，第二十四章）**：三条路（Flatpak 优先 / 双 nixpkgs / 混合）+ **HM 官方 FAQ 的 `pkgsUnstable` 写法** + 「稳定」两种含义的辨析 | HM 官方 FAQ `unstable.md` + HM/NixOS 源码核实（见附录 B.14） |
| ~~**二进位包与依赖问题的完整方案集**~~ | ✅ **已完成（第七轮，第二十五章）**：6 种来源 × 6 类根因 + 14 种方案按侵入性排序 + 常见依赖清单 + 程序类型对照 + 三类死路 + 一页速查 | nixpkgs 模块源码（`nix-ld.nix` / `ldso.nix` / `build-fhsenv-*` / `appimage.nix` / `aliases.nix`）+ 上游 README（见附录 B.15） |
| ~~**以官方手册结构为骨架重构本指南**~~ | ✅ **已完成（第八轮）**：新增「官方手册骨架导航」章（5 个 Part / 177 个叙事章节双向对照）+ **第二十六～三十五章共 10 章**（配置语法 / 文件系统 / 用户 / systemd / 系统状态 / 容器 / 图形栈 / 内核与系统切换 / 写模块 / 构建镜像） | 官方手册 stable 全文（本地副本）+ 8 组锚点原文提取（见附录 B.16） |
| **实测基准数据** | 本文多处标 `[未核实]` 就是因为缺可复现的基准（scx 收益、内核切换收益） | 你自己的 A/B 测试 |

#### E.1.1 本轮之后**仍未做**的高价值方向

| 主题 | 为什么值得补 | 需要什么证据 |
|---|---|---|
| **Hermes container 模式的实测** | 第二十一章只给了官方文档层面的行为表，**没有实际跑过容器**。writable layer 丢失、Podman sudo、GC root 这些都值得实测一遍 | 一台能跑 Docker 的 NixOS + `container.enable = true` |
| **自建 Cachix 缓存 Hermes flake** | 第二十二章 §22.2 的最大坑（666 个 derivation）**唯一的根治办法**是把构建产物推到自己控制的缓存 | Cachix 账号 + `nix build` 后 `cachix push` |
| **OpenClaw 的 `runtimePlugins` 完整清单** | 第二十一章只给了 discord / copilot 两个例子 | `nix-openclaw` 的 `plugin-catalog.nix` |
| **Hermes 的 `extraDependencyGroups` 全表** | 第二十一章引了官方 15 行表，但 `pyproject.toml` 才是权威 | `NousResearch/hermes-agent` 的 `pyproject.toml` |
| **两个 agent 的凭据轮换流程** | 第十六章讲了"凭据不落 Nix store"，但**轮换**（改 key 后怎么让服务重读）没讲 | sops-nix / agenix 的 rekey 流程 + `systemctl restart` 时序 |
| **`openclaw migrate hermes` 实操** | 两个软件都装了的人会用到；官方有迁移器但**只文档化，未实测** | 一台同时有 Hermes 与 OpenClaw 的机器 |
| **Discord 社区（`#golden-path-deployments`）的实际内容** | 第二十二章 §22.8 说 OpenClaw 的唯一支持渠道是 Discord，但**Discord 无法抓取**，所以那里有什么坑本文不知道 | 你自己进去看（本指南无法代劳） |
| **「启动失败自动回滚」的 NixOS 实现** | 第二十四章 §24.7 已指出这是本文**唯一明显不如 Aeon** 的一项（Aeon 启动检测到失败会自动回滚，NixOS 要手动选 generation）。**是否有第三方方案（如基于 systemd-boot 的健康检查 + 自动 `bootctl set-default`）未查** | 查 nixpkgs / nix-community 是否有对应模块；或自己写一个 boot 计数 + 失败切换的 systemd 服务 |
| **`home-manager.useGlobalPkgs = false` 的实测代价** | §24.5.3 给的「多一次 nixpkgs 求值 + 包哈希不同」是**源码推断**，缺内存/时间数字 | `nixos-rebuild` 加 `--show-trace` 记 eval 时间；或对同一包比较 `nix path-info` 的哈希 |

### E.2 中价值

| 主题 | 说明 |
|---|---|
| **Wayland 下的屏幕共享**（PipeWire + xdg-desktop-portal） | 会议软件常见痛点 |
| **HDR 配置** | AMD + KDE 6.6 的 HDR 链路 |
| **VR（SteamVR / Monado）** | AMD 显卡 + Linux VR 的现状 |
| **音频低延迟**（PipeWire quantum / JACK） | 音乐制作场景 |
| **笔记本特有**（如果换设备）：`services.power-profiles-daemon`、`hardware.amdgpu` 功耗管理 | 本文假设台式 |
| **NixOS 上的容器**（Docker / Podman / systemd-nspawn） | 开发环境隔离 |
| **远程访问**（Tailscale / WireGuard + Sunshine/Moonlight 串流） | 游戏串流 |
| **`nixos-generators`** | 生成 ISO / 云镜像 / SD 卡镜像 |
| **Impermanence（无状态根）** | 进阶：根文件系统每次重启清空 |

### E.3 低价值 / 已知无法补充

| 主题 | 为什么补不了 |
|---|---|
| **`linux_cachyos` 内核 / BORE 调度器** | nixpkgs 从未收录（已核实 grep = 0），`linux_zen` 也不含 BORE（已核实上游源码）。**但 CachyOS 可复刻的部分已在第十八章给出**：`scx` + `ananicy-cpp` + CachyOS 官方 ananicy 规则 + sysctl / udev 逐条翻译 |
| **SELinux on NixOS** | 没有模块，架构上冲突 |
| ~~**SteamOS 的 Gaming Mode UI**~~ | ⚠️ **第五轮部分推翻**：**Gamescope Session 本身 NixOS 有官方选项**（`programs.steam.gamescopeSession`，源码核实，§23.10）。**Valve 深度定制的部分**（SteamOS 的 gamepad UI 外壳、系统级 overlay）仍无对应实现 |
| ~~**掌机 TDP 控制**~~ | ⚠️ **第五轮部分推翻**：**`pkgs.powerstation` 在 nixpkgs 里**（`ShadowBlip/PowerStation`，*"Open source TDP control and performance daemon with DBus interface"*，源码核实，§23.11）。**缺的是机型适配接线**，不是零件 |
| **Reddit 社区数据** | 抓取被拦截（`old.reddit.com` 返回 Blocked）。已用 NixOS Discourse / Arch BBS / HN 替代 |

### E.4 建议你**自己**做的验证（本文无法替代）

因为「优化收益」是**负载与硬件相关**的，以下必须你自己测：

| 要测的 | 怎么测 |
|---|---|
| `scx` 是否对你有益 | `systemctl set-environment SCX_SCHEDULER_OVERRIDE=...` 快速切换，用 `mangohud` 看帧生成时间（frametime）而非平均帧 |
| 换内核是否有益 | `nixos-rebuild boot` 到 zen，同一游戏跑同一场景，对比 1% low 帧 |
| I/O 调度器是否有益 | 只有在游戏装在 HDD 时才值得测 |
| zram 是否有益 | 看 `zramctl` + 是否有 swap 换入换出导致的卡顿 |

> [!TIP]
> **测游戏性能请用「1% low 帧」和「帧生成时间曲线」，不要用平均帧。** 平均帧完全掩盖卡顿 —— 一个 60 平均帧但有 200ms 卡顿的游戏，体验比稳定的 50 帧差得多。MangoHud 可以显示 frametime graph。
