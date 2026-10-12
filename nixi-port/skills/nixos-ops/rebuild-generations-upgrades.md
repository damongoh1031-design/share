# rebuild / generation / 升级 命令配方

> 来源：nixi `docs/content/tools.md` 的 `nixos` 工具段 + `docs/content/multi-node.md`。
> nixi 的 13 个 Go 工具在这里被还原成**可直接执行的 CLI 命令**。

## 1. 环境判断（每次先做）

```bash
# flake 模式还是 channel 模式？
[ -f /etc/nixos/flake.nix ] && echo "FLAKE" || echo "CHANNEL"

# 配置在哪？
ls -la /etc/nixos/

# 当前版本与 generation
nixos-version
nixos-rebuild list-generations | tail -5

# 是否有失败服务
systemctl --failed --no-pager
```

## 2. rebuild 全流程

```bash
# ① dry-run（永远的第一步，不写任何东西）
nixos-rebuild dry-activate

# ② 用户可以接受的效果（不切换）
nixos-rebuild build

# ③ 真正切换（需要用户确认后）
nixos-rebuild switch

# ④ flake 用户要指定 flake 目录
nixos-rebuild switch --flake /etc/nixos#hostname

# ⑤ 远程节点
nixos-rebuild switch --flake /etc/nixos#web-server \
  --target-host admin@192.168.1.10 --use-remote-sudo
```

**失败处理**：

```bash
nixos-rebuild switch --rollback      # 回到上一个 generation
nixos-rebuild list-generations       # 确认状态
journalctl -u nixos-rebuild -b       # 看错误
```

## 3. generation 管理

```bash
# 列出
nixos-rebuild list-generations

# 回滚到上一个
nixos-rebuild switch --rollback

# 回滚到指定 generation
nixos-rebuild switch --profile-name system -P 42

# 看某个 generation 的启动项
ls /nix/var/nix/profiles/system-*-link

# 清理（先 dry-run 看能回收多少）
nix-collect-garbage --dry-run
nix-collect-garbage --delete-older-than 30d
# 或保留最近 N 个
nix-env --list-generations --profile /nix/var/nix/profiles/system
```

**告诉用户**：
- 清理是不可逆的，回滚不到已删的 generation
- 默认只保留最近 5 个
- 清理前必须展示可回收空间

## 4. 升级（flake 与 channel 两条路）

```bash
# --- flake 模式 ---
cd /etc/nixos
nix flake update                    # 改 flake.lock —— 这一步必须单独给用户看 diff
git diff flake.lock                 # 展示将要更新的 input
nixos-rebuild dry-activate          # 看会不会炸
# 等确认
nixos-rebuild switch --flake /etc/nixos#hostname

# --- channel 模式 ---
nix-channel --list
nix-channel --update                # 只拉元数据，不改系统，不需确认
nixos-rebuild dry-activate
# 等确认
nixos-rebuild switch --upgrade

# --- nixpkgs 版本查询 ---
nix registry list | head
nix flake metadata nixpkgs
```

## 5. 包管理

```bash
# 搜索（flake）
nix search nixpkgs htop
# 搜索（无 flake 时回退）
nix-env -qaP htop | head -20

# 装了哪些
nix-env -q                          # 用户级
ls /run/current-system/sw/bin | head -50   # 系统级

# 反查"哪个包提供这个文件"（比 find /nix/store 快一万倍）
nix-locate bin/htop
nix-locate --top-level libssl.so

# 装系统级包：改 configuration.nix
#   environment.systemPackages = with pkgs; [ htop ];
# 然后 rebuild —— 不是 nix-env -i
```

**装包的规则**：
1. 系统级 → `environment.systemPackages` + rebuild（**一次确认管多个包**）
2. 用户级一次性 → `nix shell nixpkgs#htop`（不动系统，最安全）
3. **不要** `nix-env -i` 装系统级包——会创建用户 profile，与 NixOS 声明式冲突

## 6. 防火墙与网络

```bash
# 状态
systemctl status firewall
nft list ruleset | head -50

# 开端口（改配置，不是直接 nft）
# networking.firewall.allowedTCPPorts = [ 8080 ];

# 快速诊断
ss -tlnp
ip addr
resolvectl status
ping -c3 1.1.1.1
```

## 7. 服务与日志

```bash
# 服务
systemctl status <unit>
systemctl restart <unit>
systemctl enable/disable <unit>
systemctl --failed

# 日志
journalctl -u <unit> -n 100 --no-pager
journalctl -b -p err --no-pager
journalctl --since "1 hour ago" -u nginx
journalctl -k                               # 内核
journalctl --list-boots                     # 历次启动
```

## 8. 定时任务（systemd timer）

```bash
# 一次性（2 小时后重启）
sudo systemd-run --on-active=2h --unit=delayed-reboot systemctl reboot

# 周期性（每天 03:00）—— 写成 NixOS systemd.timers 更符合声明式
systemctl list-timers --all --no-pager
```

## 9. 用户管理

```bash
# 声明式（改 configuration.nix，需 rebuild）
# users.users.erik = { isNormalUser = true; extraGroups = [ "wheel" "podman" ]; shell = pkgs.zsh; };

# 即时生效（免 rebuild）
#   SSH key  → 写 ~/.ssh/authorized_keys
#   密码     → passwd erik
#   锁定     → usermod -L erik / 解锁 usermod -U erik

# 只读查询
getent passwd | grep -v nologin
groups erik
```

**用户名规则**：小写字母数字 + 连字符 + 下划线。`root` 与系统用户受保护，不要动。
