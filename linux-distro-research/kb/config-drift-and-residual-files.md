---
id: config-drift-and-residual-files
title: 滚动更新的配置漂移与残余文件：机制、工具与结构性解法
tags: [linux, distro, configuration-drift, pacnew, rpmnew, dpkg-conffile, nixos, rpm-ostree, etckeeper, orphan-packages, sysadmin]
created: 2026-10-12
updated: 2026-10-12
version: 1.0.0
status: stable
source: GitHub API 读 nixpkgs 源码 + Arch 官方包库 API + rpmfind 文件列表 + 各发行版官方文档/man page（2026-10-12 抓取）
confidence: 已核实
---

# 配置漂移与残余文件

## TL;DR

**「配置漂移」是四个不同的问题**：A 文件级冲突（可检测不可自动判定）、B 语义漂移（只有 NixOS 能硬拦截）、C 孤儿包（可全自动）、D 残余文件（可检测需人工判断）。

**三条核心判断**：
1. **没有发行版能自动完成语义级配置合并** —— 工具只说「冲突了」，不说「该留哪个」
2. **三种架构从根上避免**：NixOS（构建期暴露）、Fedora Atomic（`/etc` 三方合并 + `config-diff`）、MicroOS/Aeon（`/etc` 在快照里）
3. **最被低估的通用解是 `etckeeper`** —— 把 `/etc` 变成 git，跨发行版，`git log /etc` 即漂移审计

**最关键的前提**：**只有被声明为「配置文件」的文件才有保护**。Arch 的 `backup=` 数组、RPM 的 `%config`、Debian 的 `DEBIAN/conffiles` —— **没声明的文件升级时直接覆盖，连 `.pacnew` 都不留**。

---

## 1. 冲突文件生成机制

### 声明方式与「没声明会怎样」

| 发行版 | 声明方式 | 没声明 |
|---|---|---|
| Arch | PKGBUILD `backup=()` | **直接覆盖，无 `.pacnew`** |
| Fedora/RHEL | spec `%config` / `%config(noreplace)` | 直接覆盖 |
| Debian | `DEBIAN/conffiles` | 直接覆盖 |
| openSUSE | spec `%config` | 直接覆盖 |

### Arch 三方 MD5 比对

| 比对 | 行为 |
|---|---|
| 你没改，上游改了（X/X/Z） | 静默覆盖 |
| 你改了，上游没改（X/Y/X） | 保留你的，丢弃新版 |
| **都改了（X/Y/Z）** | **保留你的，新版存 `.pacnew` 并告警** |

- 删包时改过的 backup 文件 → `.pacsave`（`-Rns` 的 `-n` 可彻底删）
- 查 backup 列表：`pacman -Qii <pkg>`
- **反直觉**：装**其他**包也可能改到本包文件，导致你没动手却生成 `.pacnew`（FS#77404）
- `NoUpgrade` / `NoExtract` 是另一套机制（pacman.conf 模式列表），与包内 `backup` 无关

### Fedora/RHEL 三后缀

| 后缀 | 条件 | 结果 |
|---|---|---|
| `.rpmnew` | `%config(noreplace)`，双方都改 | 保留你的，新版存 `.rpmnew` |
| `.rpmsave` | `%config`（无 noreplace），双方都改 | 装新版，你的存 `.rpmsave` |
| `.rpmorig` | `rpm -i` 非升级安装且目标文件不属于任何包 | 已有文件改名 `.rpmorig` |

`dnf` 无内建配置合并；`--setopt=tsflags=test` 是事务测试，**与配置文件无关**（常见误传）。

### Debian 唯一默认强制表态

dpkg 对 `conffiles` 做 MD5 三方比对，**只有双方都改才提示**：`Y/I` 装维护者版（你的存 `.dpkg-old`）／`N/O` 保留本地（新版存 `.dpkg-dist`）／`D` 看 diff／`Z` 开 shell。
- `.dpkg-new` 是解包中间态，不是给你处理的
- 非交互：`--force-confold` / `--force-confnew` / `--force-confdef`
- `ucf`：给非 conffile 管理的 /etc 文件做类 conffile 处理（`.ucf-new/.ucf-dist/.ucf-old`），**支持 diff3 合并**

### openSUSE 唯一自带 systemd service

- 后缀机制同 Fedora
- **`/usr/lib/systemd/system/rpmconfigcheck.service` 确实存在于 rpm 包**（已核实，rpmfind 对 `rpm-4.20.1-11.1` 的文件列表）
- 脚本 `/usr/sbin/rpmconfigcheck` → 输出 `/var/adm/rpmconfigcheck`
- ⚠️ **没有 `.timer`**（已核实）→ **不会自动运行**，需手动 `systemctl start` 或自建 timer

### 横向对比

| 机制 | 默认自动检测 | 官方工具 | **三方合并** | 升级时提示 |
|---|---|---|---|---|
| Arch `.pacnew` | ⚠️ 仅 warning | `pacdiff` | ✅ `-3`（需缓存有 base 包） | 否 |
| Fedora `.rpmnew` | ❌ | `rpmconf`（Fedora 官方仓库） | ❌ 仅两方 | 否 |
| Debian `.dpkg-dist` | ✅ | dpkg + `ucf` | ⚠️ dpkg 非三方；**ucf 支持** | ✅ **唯一** |
| openSUSE | ⚠️ 有 service 无 timer | `rpmconf` | ❌ 仅两方 | 否 |

---

## 2. 可复用操作

### Arch

```bash
find /etc -name '*.pacnew' -o -name '*.pacsave'
sudo pacdiff -3 --sudo                        # 三方合并
DIFFPROG=meld sudo -E pacdiff
MERGEPROG='git merge-file -p' sudo -E pacdiff -3
pacman -Qii <pkg> | grep -A20 BACKUP          # 查 backup 列表
sudo pacman -Rns $(pacman -Qtdq)              # 清孤儿包
pacman -Qm                                    # 外来/AUR 包
pacman -Qkk <pkg>                             # 校验文件（含属性）
sudo lostfiles -z                             # 找不属于任何包的文件（官方 extra）
paccache -r                                   # 缓存保留 3 版
```

### Fedora / RHEL

```bash
sudo rpmconf -a                # 交互处理全部
rpmconf -D                     # 非交互 diff（审计用）
rpmconf -t                     # 有冲突则退出码 5（做告警）
rpmconf -u use_maintainer      # 无人值守：一律用上游版
rpmconf -c                     # 清孤儿 .rpmnew/.rpmsave
sudo rpm -Va                   # 校验全部文件（9 项属性）
sudo dnf autoremove
dnf repoquery --unused         # 无依赖的包
sudo dnf repoquery --extras    # 不在任何仓库的包
```

⚠️ 无官方工具找「不属于任何 RPM 的文件」。

### Debian / Ubuntu

```bash
find /etc -name '*.dpkg-old' -o -name '*.dpkg-dist' -o -name '*.ucf-*'
deborphan --find-config        # 已卸载但配置残留的包
deborphan --guess-all          # 孤儿库
sudo cruft-ng                  # 全盘扫描（cruft 已被取代）
debsums -c                     # 只列校验失败
sudo dpkg -V
sudo apt --purge autoremove
```

⚠️ `cruft` **已从 testing 移除**，继任 `cruft-ng`（salsa.debian.org/pkg-security-team/cruft-ng，2026-10 活跃）。
⚠️ `needrestart` **与配置漂移无关**（只管库升级后哪些服务需重启）。

### openSUSE

```bash
sudo systemctl start rpmconfigcheck     # 有 service 无 timer，需手动
cat /var/adm/rpmconfigcheck
sudo rpmconf -a
zypper packages --orphaned              # 注意：指"不在任何仓库"，非"无依赖"
zypper clean --all
```

### 跨发行版通用（推荐）

```bash
sudo etckeeper init && sudo etckeeper commit "初始状态"
sudo etckeeper vcs log --oneline -20
etckeeper unclean && echo "有未记录的 /etc 改动"   # 可直接做漂移告警
systemd-delta --type=overridden        # 只看真正有差异的 unit
systemd-delta                          # masked/equivalent/redirected/overridden/extended
```

---

## 3. 结构性解法

### NixOS：漂移在构建期暴露

`/etc` 由声明生成（多为指向 `/nix/store` 的符号链接），手工改会被下次 rebuild 覆盖 —— **强制回正而非累积**。

**上游废弃选项时的行为（已从 nixpkgs 源码核实）**：

| 函数 | 行为 |
|---|---|
| `mkRenamedOptionModule` | 只 warning + 转发 |
| `mkAliasOptionModule` | 静默转发，不警告 |
| **`mkRemovedOptionModule`** | **硬 `throw`，中断 rebuild** |

`lib/modules.nix` 第 1863 行原文：
```nix
throw "The option `${showOption optionName}' can no longer be used since it's been removed. ${replacementInstructions}";
```

⚠️ **官方文档说 "warning"，实现是 `throw`** —— 文档与实现不一致，以源码为准。第三方佐证：mobile-nixos issue #731。

**NixOS 仍有漂移的例外**：`/var`、`/home`（有状态数据不受管）、`nix-env -i` 装的包、手工 systemd unit、home-manager 只撤自己创建的符号链接、`/nix/store` 无限增长。

```nix
nix.gc = { automatic = true; dates = "weekly"; options = "--delete-older-than 30d"; };
nix.settings.auto-optimise-store = true;
```
```bash
sudo nix-collect-garbage -d
nix store diff-closures before after
nixos-rebuild build --dry-activate
```

### Fedora Atomic / rpm-ostree

`/usr` 只读；**唯一可写是 `/etc` 和 `/var`**。

```bash
ostree admin config-diff
# 打印当前 /etc 与默认 /usr/etc 的差异
# A = 新增  M = 修改  D = 删除
```

**升级时 `/etc` 走三方合并**（当前 /etc × 其默认 × 新 /usr/etc）：本地改过的永久保留，未改的升到新默认。**不用 `.rpmnew` 机制**。

### MicroOS / Aeon / Kalpa

只读根 + btrfs 快照，**`/etc` 是快照的一部分，回滚即回滚配置**。`health-checker` 在 legacy grub2 下首次启动失败自动回滚。⚠️ 无 `config-diff` 等价物。

---

## 4. 语义漂移：无解的一类

配置一字未改，行为却变了（上游改默认值 / 废弃选项 / 拆分配置）。

| 发行版 | 应对 | 效果 |
|---|---|---|
| **NixOS** | `mkRemovedOptionModule` 硬 `throw` | ✅ 最强 |
| Arch | 无机制，靠 news 公告（含 manual intervention） | ⚠️ 靠人读 |
| Fedora | FESCo Changes + Bodhi | ⚠️ 靠人读 |
| openSUSE | openSUSE News + snapshot 公告 | ⚠️ 靠人读 |
| Debian | `NEWS.Debian` + 交互提示 | ⚠️ 半自动 |

**除 NixOS 外无自动拦截手段。**

---

## 5. 包重命名 / 合并（易忽略的漂移源）

| 案例 | 日期 |
|---|---|
| Arch `[community]` → `[extra]` | 2023-05-19 |
| **Arch `vlc` 拆包**（拆为 `vlc` + `vlc-plugin-*` + `vlc-gui-*`） | **2025-08-12** |
| Fedora `dnf5` Obsolete `dnf` | Fedora 41（2024-10） |
| Debian `libwmf0.2-7` 拆分 | ~2020 |

机制：Arch `replaces`+`provides`／Debian `Replaces`+`Provides`／RPM `Obsoletes`+`Provides`。

⚠️ **拆包不能靠 `replaces` 自动解决** —— 新版包名不覆盖旧包名，用户须手动装新增子包。Arch VLC 拆包即典型。

---

## 6. 坑与反直觉

1. **只有声明为配置文件的文件才有 `.pacnew` 保护**。没声明的文件升级时**直接覆盖**，静默丢失本地修改。
2. **`mkRemovedOptionModule` 文档说 warning，实际是 `throw`** —— 以源码为准。
3. **openSUSE 的 `rpmconfigcheck` 有 service 但没有 timer**，不会自动跑，得自己建 timer。
4. **`needrestart` 不管配置漂移** —— 它只管库升级后的服务重启。
5. **Fedora/openSUSE 的 "orphan" ≠ Debian/Arch 的 "orphan"**：前者指「仓库里没有了」，后者指「没有包依赖它」。
6. **`dnf --setopt=tsflags=test` 与配置文件无关**，是事务测试。
7. **装其他包可能触发本包的 `.pacnew`**（Arch FS#77404）。
8. **NixOS 的残余是 `/nix/store` 增长**，不是 `/etc` 堆积；必须配 GC。
9. **NixOS 也有漂移**：`/var`、`/home`、`nix-env -i`、手工 systemd unit 都不受声明式管理。
10. **`cruft` 已死**，Debian 上要用 `cruft-ng`。
11. **Fedora/RHEL/openSUSE 都没有官方工具找「不属于任何包的文件」**，Arch 有 `lostfiles`（官方 extra），Debian 有 `cruft-ng`。
12. **`etckeeper` 不解决冲突，但让所有漂移可追溯、可回滚、可审计** —— 装完当天见效，不挑发行版。

---

## 7. 未核实 / 存疑

- `rpmconfigcheck.service` 的**内容**（Type、扫描路径）：build.opensuse.org 有 PoW 反爬，未取到原文
- MicroOS `transactional-update` 处理 `/etc` 冲突的官方原文：manpages.opensuse.org 返回空
- 通用 `rpm-ostree reset` / `ostree admin reset` 重置 /etc 的确切语义：未核实
- `xsuchy/rpmconf` GitHub 最后推送 2025-07-08，但 Fedora 包为 1.1.12-7.fc45 —— 存在小矛盾，可能开发已转 Fedora dist-git
- `.rpmorig` 精确触发条件：二手来源，未逐字核实 rpm 源码
- `nix-diff`（第三方）：未取到官方文档

### 抓取失败
`wiki.archlinux.org`（Anubis PoW）、`build.opensuse.org`（PoW）、`manpages.opensuse.org`、`docs.fedoraproject.org` 均不可程序化抓取。已改用 Arch 官方包库 API、rpmfind 文件列表、GitHub API 读源码等等价来源。

---

## 8. 速查表

| 目的 | 命令 |
|---|---|
| Arch 处理冲突 | `sudo pacdiff -3 --sudo` |
| Fedora 审计 | `rpmconf -D` |
| Fedora 处理 | `sudo rpmconf -a` |
| openSUSE 检查 | `sudo systemctl start rpmconfigcheck` |
| Atomic 看 /etc 漂移 | `ostree admin config-diff` |
| 看 /etc 变更历史 | `sudo etckeeper vcs log --oneline` |
| 看 unit 漂移 | `systemd-delta --type=overridden` |
| Arch 找残余 | `sudo lostfiles -z` |
| Debian 找残余 | `sudo cruft-ng` |
| Arch 清孤儿 | `sudo pacman -Rns $(pacman -Qtdq)` |
| Fedora 清孤儿 | `sudo dnf autoremove` |
| NixOS 清 generation | `sudo nix-collect-garbage -d` |
| 校验完整性 | `rpm -Va` / `pacman -Qkk` / `debsums -c` |
