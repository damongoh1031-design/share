# 滚动更新的配置漂移：机制、工具与结构性解法

**调研日期**：2026-10-12
**问题**：滚动更新长期运行后如何解决配置漂移？新旧配置怎么合并？残余文件怎么办？
**方法**：3 个并行子代理（命令式合并机制 / 声明式与不可变架构 / 残余文件与孤儿包）+ 主调研员对关键矛盾点二次核实（GitHub API 读源码、Arch 官方包库 API、rpmfind 文件列表）
**核实口径**：GitHub / Arch 包库数据来自官方 API，抓取时间 2026-10-12

---

## 0. 结论先行

**「配置漂移」不是一个问题，是四个问题。它们需要的解法完全不同：**

| 类型 | 是什么 | 能否自动解决 |
|---|---|---|
| **A. 文件级冲突** | 升级时你的改动与上游改动撞车（`.pacnew` / `.rpmnew` / `.dpkg-dist`） | 能检测，**不能自动判定谁对** |
| **B. 语义漂移** | 你的配置一个字没改，但上游改了默认值/废弃了选项，含义变了 | **只有 NixOS 能硬拦截**，其他发行版靠公告 |
| **C. 孤儿包** | 不再被任何包依赖的包 | 能全自动 |
| **D. 残余文件** | 不属于任何包的文件 / 包删除后残留的目录 | 能检测，清理需人工判断 |

**三条核心判断**：

1. **没有任何发行版能自动完成「语义级」配置合并。** 工具只能告诉你「这里冲突了」，不能告诉你「该保留哪个」。
2. **三种架构从根上避免漂移**：NixOS（声明式，漂移在**构建期**暴露）、Fedora Atomic（`/usr` 只读 + `/etc` **三方合并** + `config-diff`）、MicroOS/Aeon（**/etc 也在快照里**，回滚即回滚配置）。
3. **最被低估的通用解法是 `etckeeper`** —— 把 `/etc` 变成 git 仓库，跨发行版、跨包管理器，`git log /etc` 就是漂移审计日志。

---

## 1. 机制层：冲突文件是谁生成的、什么时候生成

### 1.1 关键前提：**只有「被声明为配置文件」的文件才有保护**

这是最容易被误解、也最关键的机制。四个发行版都一样：

| 发行版 | 声明方式 | **没声明会怎样** |
|---|---|---|
| Arch | PKGBUILD 的 `backup=()` 数组 | **直接覆盖，不生成 `.pacnew`** |
| Fedora/RHEL | spec 的 `%config` / `%config(noreplace)` | 直接覆盖 |
| Debian | `DEBIAN/conffiles` 文件 | 直接覆盖 |
| openSUSE | spec 的 `%config` | 直接覆盖 |

**含义**：一个包如果把某个文件从「配置文件」改成「普通文件」（或反过来），你的本地修改会**静默消失**，连 `.pacnew` 都不会留。这是「残余文件」问题的反面 —— **文件不见了，而不是多出来了**。

### 1.2 Arch：三方 MD5 比对

pacman 对 `backup=` 数组里的文件做**三方比对**（原始 / 你的当前 / 新版）：

| 比对结果 | pacman 行为 |
|---|---|
| 你没改，上游改了（`X/X/Z`） | **静默覆盖** |
| 你改了，上游没改（`X/Y/X`） | 保留你的，丢弃新版 |
| **都改了（`X/Y/Z`）** | **保留你的，新版存为 `.pacnew` 并告警** |

- 删除包时，被改过的 backup 文件存为 `.pacsave`（`pacman -Rns` 的 `-n` 可彻底删除、不生成）
- 查某包的 backup 列表：`pacman -Qii <pkg>`
- **反直觉**：安装**其他**包也可能改到本包的文件，导致你根本没动手却生成 `.pacnew`（Arch FS#77404）
- `pacman.conf` 的 `NoUpgrade` / `NoExtract` 是另一套机制（模式列表），与包内 `backup` 无关

### 1.3 Fedora / RHEL：三种后缀

| 后缀 | 触发条件 | 结果 |
|---|---|---|
| `.rpmnew` | 文件标记为 `%config(noreplace)`，你改过、上游也改了 | **保留你的**，新版存 `.rpmnew` |
| `.rpmsave` | 文件标记为 `%config`（无 noreplace），你改过、上游也改了 | **装新版**，你的存 `.rpmsave` |
| `.rpmorig` | 用 `rpm -i`（非升级）安装，目标文件已存在且**不属于任何包** | 已有文件改名为 `.rpmorig` |

- `dnf` **没有**内建的配置合并功能，完全依赖 rpm 的 `%config` 行为
- `--setopt=tsflags=test` 是**事务测试**，与配置文件无关（常见误传）

### 1.4 Debian / Ubuntu：唯一「默认强制你表态」的机制

dpkg 对 `conffiles` 列出的文件做 MD5 三方比对，**只有维护者和用户都改了才交互提示**：

| 你的选择 | 结果 |
|---|---|
| `Y` / `I` 装维护者版本 | 你的改动存为 `.dpkg-old` |
| `N` / `O` 保留本地版本 | 新版存为 `.dpkg-dist` |
| `D` | 查看 diff |
| `Z` | 开 shell 手动处理 |

- `.dpkg-new` 是**解包过程中的临时名**（新版落位前的中间态），不是给你处理的
- 非交互场景：`--force-confold`（保留旧）、`--force-confnew`（装新）、`--force-confdef`
- `ucf`（Update Configuration File）：给**不由 dpkg conffile 管理**的 /etc 文件（如 postinst 生成的）做类 conffile 处理，生成 `.ucf-new/.ucf-dist/.ucf-old`，**支持 diff3 合并**

### 1.5 openSUSE：唯一自带 systemd service 的

- 文件后缀机制与 Fedora 相同（rpm 的 `.rpmnew` / `.rpmsave`）
- **独有**：rpm 包自带 `/usr/lib/systemd/system/rpmconfigcheck.service`（**已核实**，见 rpmfind 对 `rpm-4.20.1-11.1` 的文件列表）
  - 脚本 `/usr/sbin/rpmconfigcheck` 扫描未处理的 `.rpmnew/.rpmsave/.rpmorig`，输出到 `/var/adm/rpmconfigcheck`
  - ⚠️ **但没有配套的 `.timer`**（已核实文件列表里只有 `.service`）→ **它不会自动运行**，需要 `systemctl start rpmconfigcheck` 或自建 timer
- zypper 没有独立的 conffile 交互，直接走 rpm

### 1.6 横向对比

| 机制 | 默认自动检测 | 官方合并工具 | **三方合并** | 升级时默认提示 |
|---|---|---|---|---|
| Arch `.pacnew` | ⚠️ 仅升级时 warning | `pacdiff` | ✅ **是**（`-3`，需缓存有 base 包） | 否 |
| Fedora `.rpmnew` | ❌ | `rpmconf`（Fedora 官方仓库） | ❌ 仅两方 | 否 |
| Debian `.dpkg-dist` | ✅ | dpkg 内建 + `ucf` | ⚠️ dpkg 非三方；**ucf 支持** | ✅ **是（唯一）** |
| openSUSE | ⚠️ 有 service，无 timer | `rpmconf` | ❌ 仅两方 | 否 |

**三方合并能力上 Arch 的 `pacdiff -3` 与 Debian 的 `ucf` 最完整。** dpkg 是唯一默认强制用户表态的机制 —— 这也是为什么 Debian 的 `.dpkg-dist` 堆积问题比 Arch 的 `.pacnew` 轻。

---

## 2. 工具层：可直接粘贴的命令

### 2.1 Arch

```bash
# 找所有未处理的配置冲突
find /etc -name '*.pacnew' -o -name '*.pacsave'

# 交互式处理（三方合并，需要缓存里有旧版本包）
sudo pacdiff -3 --sudo

# 指定 diff 工具
DIFFPROG=meld sudo -E pacdiff
# 指定合并工具（默认 diff3 -m，可换成 git merge-file）
MERGEPROG='git merge-file -p' sudo -E pacdiff -3

# 查某包哪些文件受 backup 保护
pacman -Qii <pkg> | grep -A20 BACKUP

# 孤儿包（无任何包依赖）→ 一次性清理
sudo pacman -Rns $(pacman -Qtdq)

# 外来包 / AUR 包
pacman -Qm

# 校验包文件是否缺失/被改
pacman -Qk <pkg>      # 快速
pacman -Qkk <pkg>     # 含属性（权限/时间戳）

# 找「不属于任何包」的文件（lostfiles 已在官方 extra 仓库）
sudo lostfiles            # 默认输出
sudo lostfiles -s         # 严格模式
sudo lostfiles -z         # 按大小排序

# 清理包缓存（保留最近 3 版）
paccache -r
paccache -rk1    # 只保留 1 版
paccache -ruk0   # 删除所有未安装版本的缓存
```

**可选的自动化**：社区有 `pacdiff-pacman-hook-git`（pacman hook 自动跑 pacdiff）、`p3wm`（专做三方合并）、`pacnews-git`、`dotpac`。**Arch 官方不提供自动处理**。

### 2.2 Fedora / RHEL

```bash
# 扫描并交互处理所有 .rpmnew/.rpmsave
sudo rpmconf -a

# 非交互 diff（适合升级后审计 / 脚本化）
rpmconf -D

# 只检测，有文件待处理则退出码 5（适合做告警）
rpmconf -t && echo "clean" || echo "有配置冲突待处理"

# 无人值守策略
rpmconf -u use_maintainer   # 一律采用上游版本
rpmconf -u use_your         # 一律保留自己的

# 清理孤儿 .rpmnew/.rpmsave
rpmconf -c

# 校验所有已安装文件（9 项属性比对，能发现缺失和被改）
sudo rpm -Va

# 孤儿/多余包
sudo dnf autoremove
dnf repoquery --unused          # 无依赖的包
sudo dnf repoquery --extras     # 不在任何已配置仓库的包（= 旧 package-cleanup --orphans）
```

⚠️ **Fedora/RHEL 没有官方工具找「不属于任何 RPM 的文件」**，只能 `rpm -qf` 反查 + 自建 find。

### 2.3 Debian / Ubuntu

```bash
# 找残留的配置副本
find /etc -name '*.dpkg-old' -o -name '*.dpkg-dist' -o -name '*.ucf-*'

# 找「已卸载但配置残留」的包（deborphan 的 -find-config）
deborphan --find-config

# 孤儿库
deborphan --guess-all

# 全盘扫描不属于任何包的文件（cruft 已被取代，用 cruft-ng）
sudo cruft-ng

# 校验已安装文件
debsums -c        # 只列出校验失败的
sudo dpkg -V      # dpkg 内建校验

# 清理
sudo apt autoremove
sudo apt --purge autoremove    # 连配置一起删
```

⚠️ 老的 `cruft` 包**已从 Debian testing 移除**，继任是 **`cruft-ng`**（现由 Debian Security Tools 团队维护在 salsa.debian.org，2026-10 仍活跃）。

⚠️ **`needrestart` 与配置漂移无关** —— 它只处理「库升级后哪些服务需要重启」，属于另一类「运行时陈旧」问题。常见混淆。

### 2.4 openSUSE

```bash
# 手动运行配置检查（有 service，但没有 timer，不会自动跑）
sudo systemctl start rpmconfigcheck
sudo systemctl status rpmconfigcheck
cat /var/adm/rpmconfigcheck        # 输出位置

# 自建定时器（openSUSE 不自带）
# 需要自己写 rpmconfigcheck.timer

# 用 rpmconf 处理
sudo rpmconf -a

# 校验
sudo rpm -Va

# 孤儿包（注意：这里指「不在任何已配置仓库」，不是「无依赖」）
zypper packages --orphaned

# 清理缓存
zypper clean --all
```

### 2.5 跨发行版通用（强烈推荐）

```bash
# etckeeper：把 /etc 变成 git 仓库，跨发行版
# Arch 官方 extra 仓库有（1.18.23-3，2026-04-14）；Debian/Fedora/openSUSE 也有

sudo etckeeper init
sudo etckeeper commit "初始状态"

# 之后每次 apt/dnf/pacman/zypper 操作会自动 commit（通过包管理器 hook）
# 查看 /etc 的变更历史 = 漂移审计日志
sudo etckeeper vcs log --oneline -20
sudo etckeeper vcs diff HEAD~5..HEAD

# 检测是否有未提交的本地改动（可直接做漂移告警）
etckeeper unclean && echo "有未记录的 /etc 改动" || echo "干净"

# 回滚某个文件到某次提交
sudo etckeeper vcs checkout <commit> -- /etc/nginx/nginx.conf
```

**为什么它是最被低估的解法**：它不解决冲突，但它让**所有漂移都可追溯、可回滚、可审计**。装完当天就见效，且不挑发行版。

```bash
# systemd-delta：找被覆盖或扩展的 systemd unit（跨发行版）
systemd-delta

# 输出类别：
#   masked      被屏蔽
#   equivalent  被覆盖但内容相同
#   redirected  重定向
#   overridden  被覆盖且内容改变  ← 这才是漂移
#   extended    drop-in .conf 扩展
#   unchanged   未变

# 只看真正有差异的
systemd-delta --type=overridden
systemd-delta --diff=diff
```

---

## 3. 结构层：三种「从根上不产生漂移」的架构

### 3.1 NixOS —— 漂移在构建期暴露，不可能静默

**核心机制**：系统状态由 `configuration.nix` 完全描述，`/etc` 下的文件是**由声明生成**的（多为指向 `/nix/store` 的符号链接）。手工改 `/etc` 会被下次 `nixos-rebuild` 覆盖 —— 漂移被**强制回正**，而不是累积。

**上游废弃选项时会发生什么（已从 nixpkgs 源码核实）**：

| 函数 | 行为 |
|---|---|
| `mkRenamedOptionModule` | 只 **warning**，并把旧值转发到新选项 |
| `mkAliasOptionModule` | 静默转发，**不警告** |
| **`mkRemovedOptionModule`** | **硬报错 —— `throw`，直接中断 rebuild** |

nixpkgs `lib/modules.nix` 第 1863 行原文：

```nix
throw "The option `${showOption optionName}' can no longer be used since it's been removed. ${replacementInstructions}";
```

**这是本报告最重要的发现之一**：NixOS 的官方文档说 `mkRemovedOptionModule` 会产生 "warning"，但**实现是 `throw`**。也就是说，如果你的配置用了已被移除的选项，`nixos-rebuild` 会**直接失败**，而不是带着错误配置继续跑。第三方佐证：mobile-nixos issue #731「The option \`sound' can no longer be used since it's been removed」。

**语义漂移在 NixOS 上是「编译错误」，在别的发行版上是「运行时的沉默行为变化」。** 这是结构性差异。

**但 NixOS 不是没有漂移**：

| 例外 | 说明 |
|---|---|
| `/var`、`/home` | **有状态数据不受声明式管理**，会正常漂移 |
| `nix-env -i` 装的包 | 游离于 `configuration.nix` 之外，是真正的漂移 |
| 手工 systemd unit | 同上 |
| `/nix/store` 增长 | 追加式存储，删包不删文件，**必须 GC** |
| home-manager | 只撤自己创建的符号链接，**不追踪它没创建的文件** |

**NixOS 的「残余文件」是 `/nix/store` 无限增长**，不是 `/etc` 堆积：

```nix
# configuration.nix
nix.gc = {
  automatic = true;
  dates = "weekly";
  options = "--delete-older-than 30d";
};
nix.settings.auto-optimise-store = true;   # 硬链接去重
```

```bash
sudo nix-collect-garbage -d                    # 删除所有旧 generation
sudo nix-collect-garbage --delete-older-than 30d
nix store diff-closures before after           # 比较两个闭包的差异
nixos-rebuild build --dry-activate             # 预览变更但不激活
```

### 3.2 Fedora Atomic / rpm-ostree —— `/etc` 三方合并 + 内置漂移检测器

**架构**：`/usr` 是常驻只读 bind mount；**唯一可写的目录是 `/etc` 和 `/var`**。

**`ostree admin config-diff`（本报告最实用的命令之一）**：

```
作用：打印当前 /etc 与默认 /usr/etc 的差异
输出前缀：A = 新增   M = 修改   D = 删除
示例：M shadow
```

**这等于一个内置的、逐文件的漂移检测器** —— 一条命令列出「我的系统相对出厂状态改了哪些配置」。

**升级时上游改了 /etc 默认值怎么办**：采用**三方合并**（当前 `/etc` × 其默认 × 新部署的 `/usr/etc`）：
- 被你本地改过的文件 → **永久保留**
- 你没改过的文件 → **升级到新默认**

**注意**：它**不使用 `.rpmnew` 机制** —— 靠覆盖层语义而非 RPM 的文件冲突机制。这是架构级的差异。

### 3.3 MicroOS / Aeon / Kalpa —— `/etc` 也在快照里

- 只读根 + btrfs 快照，**`/etc` 的配置是快照的一部分，回滚即回滚配置**
- 回滚 = 重启到旧快照（"No changes on disk"）
- `health-checker`：legacy grub2 下，transactional update 后首次启动失败会**自动回滚到最近可用快照**
- ⚠️ **没有 `config-diff` 的等价物**，定位配置差异仍靠 `rpmconf` + 手动对比快照
- 配置冲突仍走 RPM 的 `%config` 机制

**为什么这个架构对漂移特别友好**：别的发行版处理「配置改坏了」是**逐文件修**；MicroOS 是**整体快照回滚**。后者出错概率低得多。

---

## 4. 语义漂移：真正无解的那一类

这是用户问题的深水区。**你的配置一个字没改，系统行为却变了** —— 因为上游改了默认值、废弃了选项、或拆分了配置文件。

| 发行版 | 应对方式 | 效果 |
|---|---|---|
| **NixOS** | `mkRemovedOptionModule` 硬 `throw` | ✅ **最强**：rebuild 直接失败 |
| Arch | 无专门机制；靠 `archlinux.org/feeds/news/` 的公告（含专门的 manual intervention 条目） | ⚠️ 靠人读 |
| Fedora | 靠 FESCo Changes 页 + Bodhi 更新说明 | ⚠️ 靠人读 |
| openSUSE | 靠 openSUSE News + snapshot 公告 | ⚠️ 靠人读 |
| Debian | 靠 NEWS.Debian 文件 + 交互提示 | ⚠️ 半自动 |

**结论：除了 NixOS，语义漂移没有任何自动拦截手段。** 只能靠订阅公告 + 人（或 LLM）阅读。这也是为什么在上一份调研（LLM 运维发行版选型）中，「AI 可通过官方公告预警」这一条只有订阅 RSS 这一种解法 —— **公告预警不需要跟发行版绑定**。

---

## 5. 残余文件的第四类：包重命名 / 包合并

这是最容易被忽略的漂移来源。真实案例：

| 案例 | 日期 | 影响 |
|---|---|---|
| Arch `[community]` 并入 `[extra]` | 2023-05-19 | 仓库级迁移，需更新镜像配置 |
| Arch `vlc` 拆包 | **2025-08-12** | `vlc` 拆为 `vlc` + `vlc-plugin-*` + `vlc-gui-*`，**依赖与安装路径改变，用户报告故障** |
| Fedora `dnf5` Obsolete 掉 `dnf` | Fedora 41（2024-10） | `/usr/bin/dnf` 被接管 |
| Debian `libwmf0.2-7` 拆分 | ~2020 | 建议保留空过渡包 |

**机制**：各发行版用「替代」声明自动处理：

| 发行版 | 机制 |
|---|---|
| Arch | `replaces` + `provides` |
| Debian | `Replaces` + `Provides`（过渡包，靠描述含 "dummy"/"transitional" 识别） |
| RPM | `Obsoletes` + `Provides`（Fedora 重命名流程强制要求设置） |

**⚠️ 坑**：拆包（一个包变多个）**不能靠 `replaces` 自动解决** —— 因为新版包名不覆盖旧包名，用户必须手动安装新增的子包。Arch VLC 拆包就是典型。

---

## 6. 推荐工作流（按发行版）

### Arch
1. `etckeeper` 打底（一次性）
2. 升级前：`checkupdates` 看有什么要升；读 `archlinux.org/feeds/news/`
3. 升级后立刻：`pacdiff -3 --sudo`（**不要拖**）
4. 每周：`sudo lostfiles -z` 看残余、`pacman -Qtdq` 看孤儿
5. 把 `pacdiff` 挂到 pacman hook 里自动跑（社区包 `pacdiff-pacman-hook-git`）

### Fedora / RHEL
1. `etckeeper` 打底
2. 升级后：`rpmconf -D` 审计（非交互）；有冲突再 `rpmconf -a`
3. 脚本化告警：`rpmconf -t` 退出码非 0 就告警
4. 定期：`sudo rpm -Va` 校验文件完整性
5. ⚠️ 找不属于任何包的文件只能自建脚本

### Debian / Ubuntu
1. `etckeeper` 打底
2. 升级时留意 dpkg 的交互提示（**别直接回车**）
3. 定期：`deborphan --find-config`、`cruft-ng`
4. `apt --purge autoremove` 而不是 `apt autoremove`

### openSUSE
1. `etckeeper` 打底
2. **自建 `rpmconfigcheck.timer`**（官方只给了 service，没给 timer）
3. `zypper packages --orphaned` 定期检查

### NixOS
1. **不需要 etckeeper**（系统本身就是声明式 + 版本控制）
2. 用 `nixos-rebuild build --dry-activate` 预览
3. 配好 `nix.gc.automatic` + `auto-optimise-store`
4. ⚠️ 别用 `nix-env -i` 装系统包（那才是漂移源）

---

## 7. 存疑 / 未核实

| 项 | 状态 |
|---|---|
| openSUSE 的 `rpmconfigcheck.service` **内容**（是否 Type=oneshot、扫描路径） | 未取到原文（build.opensuse.org 有 PoW 反爬）；仅从 rpmfind 文件列表确认文件存在 |
| openSUSE **是否有发行版自带的 timer** | **已核实：没有**（`rpm-4.20.1-11.1` 文件列表中无 `.timer`） |
| MicroOS `transactional-update` 处理 `/etc` 冲突的官方原文 | 未取到（manpages.opensuse.org 多次返回空） |
| 通用 `rpm-ostree reset` / `ostree admin reset` 重置 /etc 的确切语义 | 未核实到官方文档 |
| `nix-diff`（第三方工具） | 未取到官方文档 |
| `xsuchy/rpmconf` GitHub 仓库最后推送 2025-07-08，但 Fedora 包是 1.1.12-7.fc45 | **存在小矛盾**，可能开发已转入 Fedora dist-git |
| `.rpmorig` 的精确触发条件 | 二手来源，未逐字核实 rpm 源码 |
| Fedora/RHEL 的 `rpmconf` 是否支持三方合并 | **已核实：不支持**（仅两方 + 可视化前端） |

### 抓取失败说明
`wiki.archlinux.org`（Anubis PoW）、`build.opensuse.org`（PoW）、`manpages.opensuse.org`（返回空）、`docs.fedoraproject.org`（返回空）在本环境均不可程序化抓取。相关结论已改用等价来源（Arch 官方包库 API、rpmfind 文件列表、GitHub API 读源码、man page 镜像站）并逐条标注可靠性。

---

## 附：一句话速查

| 你想做什么 | 命令 |
|---|---|
| Arch 处理配置冲突 | `sudo pacdiff -3 --sudo` |
| Fedora 审计配置冲突 | `rpmconf -D` |
| Fedora 处理配置冲突 | `sudo rpmconf -a` |
| openSUSE 检查配置冲突 | `sudo systemctl start rpmconfigcheck` |
| Fedora Atomic 看 /etc 漂移 | `ostree admin config-diff` |
| 任意发行版看 /etc 变更历史 | `sudo etckeeper vcs log --oneline` |
| 任意发行版看 unit 漂移 | `systemd-delta --type=overridden` |
| Arch 找残余文件 | `sudo lostfiles -z` |
| Debian 找残余文件 | `sudo cruft-ng` |
| Arch 清孤儿包 | `sudo pacman -Rns $(pacman -Qtdq)` |
| Fedora 清孤儿包 | `sudo dnf autoremove` |
| NixOS 清旧 generation | `sudo nix-collect-garbage -d` |
| 校验文件完整性 | `rpm -Va` / `pacman -Qkk` / `debsums -c` |
