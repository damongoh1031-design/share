---
name: nixos-ops
description: NixOS 系统运维操作规范——rebuild/generation 回滚/包管理/防火墙/升级/容器/挂载/用户/定时任务/GPU 的安全操作手册与确认矩阵。当需要在 NixOS 上做系统级变更、排查故障、或给出 NixOS 配置建议时使用。
version: 1.0.0
source: 从 codeberg.org/ewrogers/nixi 的 AGENTS.md 与 docs/ 转换而来
license: 转换产物，遵循原规范来源的许可（NixOS Manual MIT / Home Manager MIT / nix-darwin MIT / devenv Apache-2.0 / Nix Manual LGPL-2.1）
---

# NixOS 运维操作规范（nixos-ops）

> 本 skill 由 `nixi`（AGPL-3.0 的 NixOS 垂直 agent）的规范转换而来，剥离了它的 Go 工具实现，
> 只保留**决策规则、确认矩阵、命令配方与安全边界**，供 Hermes Agent / OpenClaw / Codex /
> Claude Code 等通用 agent 直接加载。

## 0. 开始前必读（三条铁律）

1. **先读配置，再动手。** 任何变更前先跑 `nixos-rebuild dry-activate` 或
   `nix flake check`，把 diff 给用户看，再问要不要 apply。
2. **绝不自我批准。** 你只能**提议**变更；写入、rebuild、rollback、reboot 必须由用户明确说
   "yes / ok / go" 之后才执行。用户说 "yes 并且顺便做 X" 时，合并成一个工作流一次确认，
   不要二次确认。
3. **绝不猜包名 / 选项名。** 用 `nix search nixpkgs <term>`（或 `mcp-nixos`）查证，不要凭
   记忆写 `pkgs.xxx` 或 `services.xxx.yyy`。查不到就说查不到。

## 1. 决策表：用户意图 → 该做什么

| 用户说 | 第一步 | 是否要确认 |
|---|---|---|
| 看版本 / 状态 / 日志 / 端口 / 服务列表 | 直接跑只读命令 | ❌ |
| 装 / 删包 | 改 `environment.systemPackages` → `nixos-rebuild dry-activate` 展示 diff | ✅ |
| 开 / 关防火墙端口 | 改 `networking.firewall.allowedTCPPorts` → dry-run | ✅ |
| 启动 / 停止 / 重启服务 | `systemctl restart <unit>` | ❌ |
| enable / disable 服务 | `systemctl enable/disable` | ❌（但提示 rebuild 后可能被 NixOS 覆盖） |
| 重建系统 / 改配置 | dry-run 展示 → 等确认 → `nixos-rebuild switch` | ✅ |
| 回滚 | `nixos-rebuild list-generations` → 等确认 → `nixos-rebuild switch --rollback` | ✅ |
| 升级系统 | `nix-channel --update` 或 `nix flake update` → dry-run → 等确认 → switch | ✅ |
| 清理旧 generation | 列出现有 generation 与可回收空间 → 等确认 → `nix-collect-garbage` | ✅ |
| 增删 channel / flake input | 展示将要改的锁文件 diff | ✅ |
| 加 / 删用户、改组、改 shell | 改 `users.users.<name>` → dry-run | ✅ |
| 加 SSH key | 直接写 `~/.ssh/authorized_keys`（免 rebuild，即时生效） | ❌ |
| 设密码 / 锁 / 解锁用户 | `passwd` / `usermod -L/-U`，**不要 rebuild** | ❌ |
| 装 NVIDIA / AMD 驱动 | 改 nixos 配置 → dry-run → 提示需要 reboot 才加载内核模块 | ✅ |
| 部署 / 更新 / 删除容器 | `podman` 全流程，数据默认保留在 `/srv/<name>/` | ✅ |
| 挂载 NFS / SMB / USB | `mount` + 可选 `fileSystems` 持久化 | unmount/persist 要 ✅，mount/list 不要 |
| 建 / 删定时任务 | systemd timer | create/remove ✅，list/status 不要 |
| 分析一个部署 URL | 抓 GitHub repo / docs / compose 文件并提取配置 | ❌（只读） |

## 2. 确认矩阵（原样继承自 nixi `docs/security.md`）

| 操作类型 | 需要确认 |
|---|---|
| 只读（list / inspect / status / logs） | ❌ |
| 启动 / 停止 / 重启服务或容器 | ❌ |
| 分析部署 URL | ❌ |
| 部署 / 更新 / 删除容器 | ✅ |
| 编辑 NixOS 配置 | ✅ |
| rebuild / rollback / reboot | ✅ |
| 防火墙开 / 关 | ✅ |
| 防火墙 list | ❌ |
| 装 / 删包 | ✅ |
| 搜索 / 列包 | ❌ |
| 升级系统 | ✅ |
| 更新 channel（`nix-channel --update` 本身） | ❌ |
| 增 / 删 channel | ✅ |
| 清理 generation | ✅ |
| 挂载 / 列表挂载 / 列设备 | ❌ |
| unmount / 持久化挂载 | ✅ |
| 增删改组、改 shell | ✅ |
| SSH key / 密码 / 锁定 / 解锁 / 列用户 | ❌ |
| 启用 / 禁用 / 配置 NVIDIA 驱动 | ✅ |
| NVIDIA 状态 / 利用率 | ❌ |
| 启用 / 禁用 / 配置 AMD GPU 驱动 | ✅ |
| AMD GPU 状态 / 利用率 | ❌ |
| 服务 enable / disable | ❌ |
| 列失败服务 | ❌ |
| 建 / 删定时任务 | ✅ |
| 列 / 状态 / enable / disable timer | ❌ |

## 3. 执行顺序（每个变更请求都按这个走）

```
1. 读配置        nix flake check / nixos-rebuild dry-activate
2. 出 diff       把将要变更的内容给用户看（不要只说"我会改 X"）
3. 等确认        等用户明确 yes；不要自己 approve
4. 执行          nixos-rebuild switch
5. 验结果        列 generation、查失败服务、必要时提示 reboot
6. 失败即回退     rebuild 失败 → nixos-rebuild switch --rollback + 说明原因
```

**铁律：rebuild 失败不要反复重试同一个配置。** 先 `nixos-rebuild switch --rollback`
回到可用状态，再分析错误。

## 4. NixOS 特有的三个必须记住的语义

### 4.1 `zypper update` vs `dup` 的 NixOS 对应物
NixOS **没有部分升级**概念，但有等价陷阱：

- **flake 用户与 channel 用户的升级路径不同**，先确认是哪一种：
  ```bash
  ls /etc/nixos/flake.nix 2>/dev/null && echo "flake 模式" || echo "channel 模式"
  cat /nix/var/nix/profiles/per-user/root/channels 2>/dev/null | head
  ```
- **flake 模式**：`nix flake update` 改的是 `flake.lock` → `nixos-rebuild switch`。
  这是两步，不要合成一个"upgrade"。
- **channel 模式**：`nix-channel --update` → `nixos-rebuild switch --upgrade`。

### 4.2 内核 / 驱动更新需要 reboot
`nixos-rebuild switch` 之后内核模块、NVIDIA 驱动不一定生效。**涉及内核或驱动的变更，
明确提示用户需要 reboot**，不要声称"已生效"。

### 4.3 generation 是唯一的安全网
- `nixos-rebuild list-generations` 列所有 generation
- `nixos-rebuild switch --rollback` 回到上一个
- 默认清理保留最近 5 个，**用户说清理时必须告知会保留几个**
- 清理前用 `nix-collect-garbage --dry-run` 或 `nix-store --gc --print-roots` 展示可回收空间

## 5. 禁止事项

- ❌ **禁止** `find /nix/store/* -iname libxxx.so` —— 用 `nix-locate`（`nix-index`）反查
- ❌ **禁止** `rm -rf` 任何系统路径 —— 删除只允许 `/srv/<container>/`，且必须显式确认
- ❌ **禁止** `nix-env -i` / `nix profile install` 装系统级包 —— 走 `environment.systemPackages`
- ❌ **禁止** 改 `system.stateVersion` 除非用户明确要求
- ❌ **禁止** 在用户没说的情况下增删 channel / flake input
- ❌ **禁止** 把密码 / token / 凭据写进 `configuration.nix` 或 flake —— 用 `agenix` / `sops-nix`
  或运行时文件
- ❌ **禁止** 声称某个操作"已完成"而实际只是 dry-run

## 6. 参考文件

| 文件 | 什么时候读 |
|---|---|
| `confirmation-matrix.md` | 拿不准某个操作要不要确认时 |
| `secrets-sudo-scope.md` | 涉及密码、凭据、sudo、`/srv` 权限时 |
| `containers-mounts-gpu.md` | 部署容器、挂 NAS、配 GPU 时 |
| `multi-node.md` | 一次管多台机器时 |
| `anti-patterns.md` | **每次任务结束前自查一遍** |

## 7. 加载本 skill 时的第一句话建议

```text
我在管 NixOS。先读我的配置（/etc/nixos 或 flake 目录），告诉我你发现了什么，
把变更作为 diff 提议给我。不要 rebuild、不要装东西、不要跑容器，等我批准。
```
