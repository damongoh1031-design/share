---
id: rolling-distro-selection-nixos-arch-opensuse
title: 滚动发行版选型：NixOS / Arch Linux / openSUSE Tumbleweed·Slowroll 五维对比
tags: [linux, rolling-release, nixos, arch-linux, opensuse, tumbleweed, slowroll, unattended-ops, distro-selection]
created: 2026-10-12
updated: 2026-10-12
version: 1.0.0
status: stable
source: 官方文档/Wiki/新闻页 + 仓库元数据实测（3 个并行研究子代理），2 项存疑点主调研员二次核实
confidence: 已核实
---

# 滚动发行版选型：NixOS / Arch / openSUSE TW·Slowroll

## TL;DR

三者不是同类：**Arch = 上游直通激进滚动**；**Tumbleweed = 带 openQA 全系统门禁的工程化滚动**；**NixOS unstable = 声明式原子回滚的准滚动**（新鲜度反而可能低于 Arch，且 Hydra 挂掉会连安全修复一起卡）。无人值守只有 **openSUSE MicroOS** 是原生方案。**NixOS 存在 2026-08 nixpkgs 核心团队解散的治理风险。**

---

## 1. 滚动机制（机制差异决定一切）

| | NixOS unstable | Arch | Tumbleweed | Slowroll |
|---|---|---|---|---|
| 单元 | channel（Hydra 全绿后推进） | 单包进 stable 仓 | snapshot（整批） | snapshot（月更） |
| 用户端延迟 | 提交后**数天** | 小时～天 | QA 过即发 | 月 9 日 ±3 天 |
| 实测频率 | channel 推进 | 持续 | 2026-08: 23/31 天；2026-02: 17/28 天 | 月 1 次大版本 bump |
| 稳定版 | 每 6 月（25.11 Xantusia → 26.05 Yarara） | 无版本号 | 无版本号 | 有版本 bump |

**关键机制差异**：
- Tumbleweed 的 snapshot 是**整体交付**，机制上不可能出现 partial upgrade。
- NixOS unstable 是 CI 门控的 curated snapshot，**不是** bleeding edge。
- Arch `community` 仓已于 2023-05 并入 `extra`。

## 2. 打包质量

| | NixOS | Arch | TW |
|---|---|---|---|
| 包数 | 140,000+ / 1.09M commits | 官方「several thousand」；AUR ~107,724（第三方） | 单大 snapshot ~4001 包更新 |
| 贡献者 | 25.11 周期 2742 人 / 59,430 commits | PM 需 2 人担保+投票，新人 junior 2 月 | OBS + devel→staging→Factory |
| PR 门禁 | OfBorg（**非 required check**） | 无全系统门禁，靠 staging 批量重建 | **staging 成组集成测试 + openQA** |
| 法务审查 | 无 | 无 | **legal-auto + 人工法务审查** |
| 破损包 | `mark-broken.sh` 半自动标 broken，长期破损包存在 | 上游 bug 直接继承；AUR 无保证 | 未过门禁的更新被 staging 挡住 |

## 3. 错误汇报

| | NixOS | Arch | TW |
|---|---|---|---|
| 追踪 | GitHub NixOS/nixpkgs | **GitLab**（2023-12 从 Flyspray 迁移） | **Bugzilla** |
| 构建失败公开看板 | hydra + status.nixos.org | 无 | **openqa.opensuse.org（公开可查，三者唯一）** |
| 安全报告 | ⚠️ 邮件给**团队成员个人地址**，非 security@nixos.org | arch-dev-public 列表 | Bugzilla + factory@ 列表 |
| 用户告警 | 无 | **news 的 manual intervention 公告（必须订阅）** | 邮件列表 + 论坛 |

## 4. 长期稳定性

| | NixOS | Arch | TW |
|---|---|---|---|
| 原子性 | ✅ 确定性构建、断电后状态一致 | ❌ | ✅ 事务性 snapshot |
| 回滚 | **generation**：`nixos-rebuild switch --rollback` + boot 菜单选代 | ❌ 无官方快照；靠 ALA `pacman -Syyuu` 整机回退 | **Btrfs+snapper**：GRUB 选只读快照 → `snapper rollback` |
| 结构性风险 | flakes 仍实验性；CA derivations 实验性 | **partial upgrade 被禁**；`.pacnew` 手动合并；内核更新须重启 | NVIDIA 闭源驱动每次内核升级重编；AMDGPU-PRO 不支持；Packman 偶发不兼容 |
| 磁盘 | generation 累积，**必须配 `nix.gc`** | 常规 | Btrfs 快照需清理策略 |
| 长期不升级 | 影响小 | **越久越难升** | 影响小 |

**Arch 近 3 年人工介入事件（archlinux.org/news）**：2024-03-29 xz 后门 / 2024-03-04 mkinitcpio microcode / 2024-07-01 openssh sshd 重启 / 2024-09-14 pacman 7.0.0 / 2025-02-03 glibc 2.41 损坏 Discord / 2025-06-21 linux-firmware / 2026-09-22 mkinitcpio≥42 TPM2 LUKS。**至少 7 次。**

## 5. 无人值守

| | NixOS | Arch | TW |
|---|---|---|---|
| 官方自动升级 | ✅ `system.autoUpgrade`（nixos-upgrade.timer） | ❌ 无 | 无内置；可 zypper dup + timer |
| 自动重启 | 仅 `allowReboot=true`（默认 false） | — | transactional-update + 重启 |
| **失败自动回滚** | ❌ 需手动选 bootloader 旧项（~3 键） | ❌ | ✅ **MicroOS 的 health-checker** |
| 钉版本 | flake.lock / 换 channel | — | **tumbleweed-cli** 钉 snapshot |
| 官方无人值守方案 | 无 | 无 | **MicroOS**（只读根+事务更新+health-checker）；每 TW snapshot 自动出对应 MicroOS |
| 社区共识 | 服务器可开 autoUpgrade（用 stable/`-small`，**别用 unstable**） | **不适合全自动**（作者本人明说：无 partial-upgrade 支持、无仅安全仓库） | 官方推荐无人值守用 MicroOS/Leap Micro |

**就绪度排序**：MicroOS > NixOS > Tumbleweed > Slowroll >>> Arch

---

## 可复用操作

### NixOS 无人值守自动升级（stable 频道）
```nix
system.autoUpgrade = {
  enable = true;
  channel = "https://nixos.org/channels/nixos-25.11";  # 别用 unstable
  dates = "04:00";
  randomizedDelaySec = "45min";
  allowReboot = true;          # 需要自动重启才开
  operation = "switch";        # 或 "boot"
};
nix.gc = {
  automatic = true;
  dates = "weekly";
  options = "--delete-older-than 30d";   # 必须配，否则 generation 撑满磁盘
};
```
回滚：`nixos-rebuild switch --rollback`；或重启时在 boot 菜单选旧 generation。

### openSUSE Tumbleweed / Slowroll 无人值守
```bash
# 手动推进 / 钉住 snapshot（避免盲跟）
tumbleweed-cli status
tumbleweed-cli list
tumbleweed-cli switch <snapshot-id>

# 回滚
sudo snapper list
# 重启 → GRUB 选 "Start Bootloader from a read-only snapshot" → 选快照 → 登录后：
sudo snapper rollback
```

### Arch 降级（无官方快照，用 ALA）
```bash
# 降单个包
pacman -U https://archive.archlinux.org/packages/<...>.pkg.tar.zst
# 整机回退：pacman.conf 的 Server 指向 archive.archlinux.org/repos/<日期>/ 后
pacman -Syyuu
```
⚠️ 严禁混用 ALA 与最新镜像（会再次变成 partial upgrade）。

---

## 坑与反直觉

1. **NixOS unstable 不是「最新」**：提交进 master 后要等数天 Hydra 全绿才推进 channel，新鲜度可能低于 Arch。且 Hydra 构建失败会**连安全修复一起卡住**。
2. **NixOS 安全报告邮箱是个人地址**，不是 `security@nixos.org`——运维流程需提前记下。
3. **NixOS 的 autoUpgrade 不会自动回滚**：失败后要人手动在 boot 菜单按 3 下键。所谓「NixOS 自动回滚」是误解。
4. **Arch 的 `pacman -Sy <pkg>` 是毁系统操作**（partial upgrade），不是「先刷新再装」。
5. **AUR 有真实供应链攻击历史**：2025-06 约 400+ 包被污染，2026-06-12 又有恶意包事件。
6. **Tumbleweed 的「稳」来自 openQA 门禁**，不是来自保守——它照样每天发 snapshot。
7. **Slowroll 项目热度低**：官方专题新闻停在 2025-01-09，但镜像仍在产出（2026-10-01）。Wiki 仍标 experimental。
8. **NixOS 治理风险**：2026-08-08 nixpkgs 核心团队解散（官方 Discourse 确认），原话「该团队管辖事务目前无直接负责人」。这是一年内第二次核心治理团队集体退出。

## 未核实 / 存疑

| 项 | 状态 |
|---|---|
| Arch 上游→stable 精确延迟 | 官方无量化数字 |
| Arch 官方包精确数量 | 官方仅写 "several thousand" |
| Tumbleweed 包总量 | 未获官方数字 |
| Arch↔TW 升级失败率量化对比 | **不存在公开数据**，任何百分比说法都是推断 |
| Slowroll 是否已脱离 experimental | Wiki 仍标 experimental |
| `transactional-update.timer` 在 TW 的原文依据 | 未直接读到 TW 文档原文 |
| NixOS 治理事件的长期影响 | 2026-08 刚发生，尚无 3–5 年数据 |
