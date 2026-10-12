# 多节点管理

> 来源：nixi `docs/content/multi-node.md` + `internal/tools/executor.go` 的 Executor 分层设计。
> nixi 的 Executor 抽象被还原成**「本地 / SSH / 只读」三档指令约定**。

## 1. 三档执行模式

| 模式 | nixi 里的实现 | 通用 agent 里怎么做 |
|---|---|---|
| **local** | `LocalExecutor` → `os/exec` | 直接跑本地命令 |
| **ssh** | `SSHExecutor` → `ssh` + 按需前置 `sudo` | `ssh -o BatchMode=yes <user>@<host> '<cmd>'` |
| **monitored** | `MonitoredExecutor` → **拒绝一切变更命令** | **只跑只读命令**；见下方红线 |

## 2. 节点配置

nixi 用 `config.toml` 的 `[[nodes]]`：

```toml
[[nodes]]
name = "web-server"
host = "192.168.1.10"
user = "admin"
mode = "managed"        # managed = 完全控制；monitored = 只读

[[nodes]]
name = "monitoring"
host = "192.168.1.30"
user = "admin"
mode = "monitored"
```

**通用 agent 侧**：把这张表放在你的 NixOS 配置仓库或 agent 的 `MEMORY.md` / 项目
`.hermes.md` 里，让 agent 每次先读。

## 3. SSH 安全参数（原样照抄）

```bash
ssh -o BatchMode=yes \
    -o StrictHostKeyChecking=accept-new \
    -o ConnectTimeout=10 \
    admin@192.168.1.10 '<remote command>'
```

三条各自的作用：
- `BatchMode=yes` —— **永不提示密码**（没有 key 就失败，不会卡住）
- `StrictHostKeyChecking=accept-new` —— 首次接受新 host key，**host key 变了则拒绝**（防 MITM）
- `ConnectTimeout=10` —— 不可达节点 10 秒失败，不挂起

**参数逐个 shell-quote 后再拼成字符串**传给 ssh，否则含空格的参数会被远程 shell 拆错。

## 4. sudo 前置规则（哪些命令远程要 sudo）

**永远要 sudo**：`nixos-rebuild`、`reboot`、`shutdown`、`passwd`、`chpasswd`、
`useradd`、`usermod`、`userdel`、`groupadd`、`groupmod`、`groupdel`、`nix-channel`、`nix-env`

**按子命令要 sudo**：`systemctl start|stop|restart|enable|disable|daemon-reload`

**按路径要 sudo**：`mkdir` / `rm` / `cp` / `mv` / `chmod` / `chown` 的参数中只要有一个落在
`/srv/`、`/etc/`、`/var/`、`/mnt/` 下，就加 sudo

**永不加 sudo**：`sudo` 本身（不要双重包裹）

## 5. monitored 节点的红线（比 sudo 规则更宽）

`isMutatingCommand` 判定为变更的命令，**在 monitored 节点上无论 LLM 要求什么都拒绝**：

| 类别 | 命令 |
|---|---|
| 一律拒 | `sudo`、`nixos-rebuild`、`reboot`、`shutdown`、`passwd`、`chpasswd` |
| 一律拒 | `useradd`、`usermod`、`userdel`、`groupadd`、`groupmod`、`groupdel` |
| 一律拒 | `tee`、`mkdir`、`rm`、`cp`、`mv`、`chmod`、`chown` |
| 一律拒 | `nix-channel`、`nix-env`、`ssh-keygen`、`ssh-copy-id` |
| 按子命令拒 | `podman run\|rm\|stop\|start\|restart\|create\|pull\|rmi\|network\|volume` |
| 按子命令拒 | `systemctl start\|stop\|restart\|enable\|disable\|daemon-reload\|mask\|unmask` |

> **这是 nixi 最有价值的安全设计之一**：read-only 不是"约定"，是执行器层的硬拒。
> 在通用 agent 里，等价的强制手段是 `tumf/mcp-shell-server` 的 `ALLOW_COMMANDS` 只放只读命令，
> 或 MCP 的 `--read-only`。**只在 skill 里写"请只读"是不够的。**

## 6. 批量与错误处理

```bash
# 按节点改 hosts，然后对每个节点跑同一组命令
for h in web-server db-1 cache-2; do
  echo "=== $h ==="
  ssh -o BatchMode=yes -o ConnectTimeout=10 admin@$h 'nixos-version; systemctl --failed --no-pager'
done
```

**节点名模糊匹配**：nixi 用 Levenshtein 距离做建议（`web-srever` → "did you mean web-server?"）。
在 skill 里照做：发现节点名拼错时**给出最接近的真实节点名**，不要静默失败。

## 7. 远程 rebuild

```bash
# 从控制机推到远端（推荐，构建在远端）
nixos-rebuild switch --flake /etc/nixos#web-server \
  --target-host admin@192.168.1.10 --use-remote-sudo

# 集群部署用 colmena（无状态、并行、失败隔离）
colmena apply
colmena apply --on @web-servers

# deploy-rs：flake + 自动回滚
deploy .#web-server
```

**多机部署优先用 colmena / deploy-rs，不要手写 for 循环**——它们有并行、失败隔离、原子性。
