# rebuild / generation / 升级 / 包管理

v2 的主要变化：**原来的纯 CLI 配方改写成 MCP 工具调用**，CLI 只留没有工具覆盖的部分。

## 1. 日常变更（最常见）

```
# 改 .nix 文件（宿主原生 Edit/Write）
nix fmt                                     # Bash —— 没有工具覆盖格式化
check("lint")                               # statix + deadnix → 结构化 findings
check("dry-build")                          # 便宜地抓 eval / build 错误
diff()                                      # 包增删与版本变化 → 给用户看
# 等确认
switch()                                    # 记 rollback_generation，返回 summary
```

**失败时**：读 `first_error` → `error_detail` → `failed_derivation.log_tail`，
**然后停**。不要跑 `nix log`，不要 `full_log=True`。

**成功但有 unit 新失败**：`status: "degraded"` → 读 `summary.health` → 回滚。

## 2. 升级系统（flake 模式 vs channel 模式，路径不同）

**先判断是哪种**：

```bash
ls /etc/nixos/flake.nix 2>/dev/null && echo "flake 模式" || echo "channel 模式"
```

### flake 模式 —— 两步，不要合成一个"upgrade"

```bash
nix flake update                    # 改 flake.lock —— 这一步必须单独给用户看 diff
git diff flake.lock                 # 展示将要更新的 input
```

```
check("dry-build")                  # 看会不会炸
diff()
# 等确认
switch()
```

**`nix flake update` 是独立的一步。** 任何把"更新锁文件 + rebuild"合成单个
"upgrade" 工具的做法，都会掩盖锁文件变更这个决策点。

### channel 模式

```bash
nix-channel --list
nix-channel --update                # 只拉元数据，不改系统，不需确认
```

```
check("dry-build")
# 等确认
switch()                            # 或 Bash: nixos-rebuild switch --upgrade
```

### 查 nixpkgs 版本

```bash
nix registry list | head
nix flake metadata nixpkgs
```

## 3. generation 与回滚

| 想做什么 | 怎么做 |
|---|---|
| 列所有 generation | `generations(action="list")` |
| 回上一代 | `generations(action="rollback")` —— **只回上一代** |
| 回指定代 | `generations(action="rollback", generation=<id 或 path>)` |
| 回这次 switch 之前的 | `generations(action="rollback", generation=<switch 返回的 rollback_generation>)` |
| Home Manager 的 generation | `generations(action="list", mode="home-manager")` |

**NixOS 的 list 条目在 profile 链接存在时会带 `path` 字段** —— 可以拿它做精确回滚目标。

**裸 rollback 的陷阱**：`generations(action="rollback")` 是"上一代"，**不是**
"上次 switch 之前那代"。中间如果有别的 switch，两者不同。**要精确就用
`rollback_generation`。**

**回滚后仍要验证**：回滚是激活操作，回执同样带 `summary` 与 `current_generation`。

## 4. 清理 generation（会丢安全网，必须说清楚）

```bash
nix-collect-garbage --dry-run               # 展示可回收
nix-store --gc --print-roots | head         # 看有哪些 root 挡着
```

**必须告知用户会保留几个。** NixOS 默认保留最近若干代，但 `--delete-older-than` 会
把更早的全删 —— **那些就是回滚目标**。

清理前的标准动作：先 `generations(action="list")`，把列表给用户看，再让他决定保留到哪天。

最适合做成周期任务（见 `no-mcp-coverage.md` §6）：

```nix
# 每周清掉 30 天前的
systemd.timers.nix-gc.timerConfig.Persistent = true;   # 错过（重启）后补跑
```

## 5. 包管理

```
# 查包（防幻觉）—— 走 nixos-query
nix(action="info",   query="ripgrep", source="nixos", type="package")
nix(action="search", query="ripgrep", source="nixos", type="programs")   # 提供哪些可执行文件
```

```bash
# 装了哪些
nix-env -q                                   # 用户级
ls /run/current-system/sw/bin | head -50     # 系统级

# 反查"哪个包提供这个文件"（比 find /nix/store 快一万倍）
nix-locate bin/htop
nix-locate --top-level libssl.so
```

**装包的三档规则**：

| 场景 | 做法 | 确认 |
|---|---|---|
| 系统级（要长期存在） | 改 `environment.systemPackages` → `check("dry-build")` → `switch()` | ✅（**一次确认管多个包**） |
| 用户级一次性试用 | `nix shell nixpkgs#htop` —— 不动系统 | ❌ |
| ❌ 不要 | `nix-env -i` 装系统级包 | 会创建用户 profile，与声明式冲突 |

**批量装包要合并确认**：用户说"装 htop、ripgrep、fd"时，一次改完、一次 dry-run、一次确认。

## 6. 防火墙与网络

```bash
# 状态（只读）
nft list ruleset | head -50
ss -tlnp
ip addr
resolvectl status
ping -c3 1.1.1.1
```

```nix
# 开端口 —— 改配置，不是直接 nft
networking.firewall.allowedTCPPorts = [ 8080 ];
```
→ 改完走 `check("dry-build")` → 确认 → `switch()`。

## 7. 服务与日志

```bash
# 服务（重启不需确认）
systemctl status <unit>
systemctl restart <unit>
systemctl enable/disable <unit>        # 提示：rebuild 后可能被 NixOS 覆盖

# 日志
journalctl -u <unit> -n 100 --no-pager
journalctl -b -p err --no-pager
journalctl --since "1 hour ago" -u nginx
journalctl -k                          # 内核
journalctl --list-boots                # 历次启动
```

**switch 之后不要手动 `systemctl --failed`** —— 读 `summary.health`，里面有前后 diff
和前 5 个新失败 unit 的 journal tail。

## 8. 用户管理

```nix
# 声明式（改配置，需 rebuild + 确认）
users.users.erik = {
  isNormalUser = true;
  extraGroups = [ "wheel" "podman" ];
  shell = pkgs.zsh;
};
```

```bash
# 即时生效（免 rebuild，不需确认）
#   SSH key → 写 ~/.ssh/authorized_keys
#   密码    → passwd erik
#   锁定    → usermod -L erik  /  解锁 usermod -U erik

# 只读查询
getent passwd | grep -v nologin
groups erik
```

**用户名规则**：小写字母数字 + 连字符 + 下划线。`root` 与系统用户不要动。

## 9. 三个必须记住的 NixOS 语义

### 9.1 没有"部分升级"的概念，但有等价陷阱

flake 用户与 channel 用户的升级路径**不同**（见 §2）。**先确认是哪一种再动手。**

### 9.2 内核 / 驱动更新需要 reboot

`switch()` 之后内核模块、NVIDIA 驱动**不一定生效**。涉及内核或驱动的变更，
**明确提示用户需要 reboot**，不要声称"已生效"。

### 9.3 generation 是唯一的安全网

所以：**清理前必须展示、必须告知保留几个、必须确认。**
