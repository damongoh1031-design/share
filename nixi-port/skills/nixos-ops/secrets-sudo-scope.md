# 凭据处理与 sudo 边界

> 来源：nixi `docs/security.md` 的 Sensitive Data Handling + Permissions Model 两节。
> 这两节是 nixi 里**最值钱、且完全可以脱离 nixi 复用**的部分。

## 1. 凭据绝不进上下文

nixi 的做法（转换后仍适用）：

| 场景 | 正确做法 | 错误做法 |
|---|---|---|
| SMB 密码 | 运行时通过掩码输入传给 `mount`，**不写进配置、不进对话历史** | 把密码写进 `configuration.nix` 或 flake |
| API key / token | 用 `agenix` / `sops-nix` 加密后由配置引用 | 明文写在 `configuration.nix` |
| 数据库密码 | 容器 env 由 secret 文件注入，不写进 compose | 明文 `POSTGRES_PASSWORD=xxx` |
| 用户密码 | `passwd <user>` 交互式输入 | `chpasswd` 带明文参数 |
| SSH 私钥 | `~/.ssh/` 600 权限 | 放在仓库里 |

**规则**：
1. **永远不要把密码 / token / 凭据作为命令参数传给会记录日志的东西**
2. 输出中包含密码 / token 的行，**向用户展示前先脱敏**
3. SMB 凭据落地位置：`/srv/.credentials/`，root 所有，mode 600
4. 读 NixOS 配置时，自动过滤含 `password` / `secret` / `token` / `key` 的行再展示

## 2. scoped sudo 白名单（原样继承）

**只给这些命令 NOPASSWD，别的都不给：**

| 命令 | 用途 |
|---|---|
| `nixos-rebuild` | 系统重建 |
| `systemctl` | 服务管理 |
| `podman` / `docker` | 容器管理 |
| `nix-env` | generation 管理 |
| `nix-channel` | channel 管理 |
| `nix-store` | 垃圾回收 |
| `reboot` | 重启 |
| `tee` | 写 `/etc/nixos/` 配置文件 |
| `nft` / `iptables` | 防火墙检查 |
| `mkdir -p /srv/*` | 建 `/srv/` 子目录 |
| `rm -rf /srv/*` | 清容器数据（**仅用户明确要求时**） |
| `mount` / `umount` | 挂载 |
| `mkdir -p /mnt/*` | 建挂载点 |
| `chmod` | 凭据文件权限 |
| `passwd` / `chpasswd` | 用户密码与锁定 |
| `chown` | 修 SSH key 目录属主 |
| `mkdir -p /home/*` | 建用户 `.ssh` 目录 |
| `systemd-run` | 一次性 systemd timer |

**明确不给 sudo 的：`rm` / `cp` / `mv`** —— 这三个在 `/srv/` 之外的一切破坏都靠它们，
开免密就等于给 root。

## 3. NixOS 落地方案

```nix
# 假设 agent 跑在专用用户 agentuser 下
users.users.agentuser = {
  isSystemUser = true;
  group = "agentuser";
};

security.sudo.extraRules = [
  {
    users = [ "agentuser" ];
    commands = [
      { command = "/run/current-system/sw/bin/nixos-rebuild"; options = [ "NOPASSWD" ]; }
      { command = "/run/current-system/sw/bin/systemctl";     options = [ "NOPASSWD" ]; }
      { command = "/run/current-system/sw/bin/nix-collect-garbage"; options = [ "NOPASSWD" ]; }
      { command = "/run/current-system/sw/bin/tee";                        options = [ "NOPASSWD" ]; }
      # ⚠️ 不要加 rm / cp / mv
    ];
  }
];
```

**改完必须校验：**

```bash
visudo -cf /etc/sudoers
# 或 NixOS: nixos-rebuild dry-build && 看 sudoers 是否被正确生成
```

## 4. `/srv/` 所有权模型

- `/srv/` 归 agent 用户所有 → 容器数据与文件操作在 `/srv/` 下**不需要 sudo**
- 容器数据**强制**在 `/srv/<container-name>/`
- volume mount 只接受 `/srv/`（容器数据）和 `/mnt/`（外部 NFS/SMB/USB）
- `/srv/` 之外的挂载在工具层直接拒

## 5. Hermes / OpenClaw 侧对应物

| nixi 机制 | 通用 agent 对应 |
|---|---|
| scoped sudo 白名单 | **直接复用上面的 NixOS 配置**，与 agent 无关 |
| 凭据不进上下文 | 宿主的 secret 管理 / 手动输入；skill 只能"要求"不能强制 |
| 输出脱敏 | 靠 agent 自觉 + 宿主的工具输出过滤 |
| `/srv/` 边界 | 用 `tumf/mcp-shell-server` 的 `ALLOW_PATTERNS` 把路径写进正则 |
