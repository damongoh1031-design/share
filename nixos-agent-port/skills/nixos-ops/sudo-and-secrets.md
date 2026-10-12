# sudo 与凭据

**这一节是整个 port 里最值钱的部分** —— 因为 sudoers 是**唯一真正以 root 运行的边界**，
其余（pin、宿主白名单、skill 规则）都只是"防手滑"。

## 1. 先记住这句话

`nix-agent` 的作者自己在文档里写（`docs/privileged-automation.md`）：

> `$NIX_AGENT_FLAKE` ... is an **anti-footgun, not a security boundary**. The agent can still
> edit the pinned tree and, if it can edit MCP config, the pin in `.mcp.json`.
> **The privilege boundary that actually runs as root is sudoers.**

翻译：**pin 防的是"指错目录"，不是"越权"。** 别把 pin 当沙箱。

## 2. 可直接落地的 NixOS 模块（推荐）

`nix-agent` 自带 `nixosModules.default`。**优先用它，而不是手写 `extraRules`**：

```nix
programs.nix-agent.enable = true;
programs.nix-agent.flake = /home/alice/nixos;   # 配置 flake 工作树的绝对路径
programs.nix-agent.privilegedAutomation.enable = true;
programs.nix-agent.privilegedAutomation.user = "alice";
```

它做什么：

| 行为 | 说明 |
|---|---|
| 把二进制 wrap 起来注入 `NIX_AGENT_FLAKE` | 当 `flake` 设了的时候 |
| 生成 **NOPASSWD** sudoers 规则 | 见下一节的精确内容 |
| `flake` 未设时**降级** | 只发 rollback / switch-generation 规则，**不发 rebuild/switch**，并产生一条 `warnings` |
| `usageLog.enable = true`（可选） | 注入 `NIX_AGENT_USAGE_LOG=1`，每次调用追加一行 JSON 到 `$XDG_STATE_HOME/nix-agent/usage.jsonl` |

> **注意默认值**：`privilegedAutomation.enable` 在 Nix 侧默认 **`false`**（避免已有配置
> 悄悄长出 sudoers），但 `nix-agent` 的**文档化推荐默认是开启**（高信任）。
> 你要自己决定走哪边。

## 3. 生成的 sudoers 规则（注意窄到什么程度）

```nix
# generation / rollback —— 无 flake ref
{ command = "${nixosRebuild} switch --rollback";                                    options = [ "NOPASSWD" ]; }
{ command = "${nixEnv} -p /nix/var/nix/profiles/system --switch-generation *";       options = [ "NOPASSWD" ]; }
{ command = "/nix/var/nix/profiles/system/bin/switch-to-configuration switch";       options = [ "NOPASSWD" ]; }

# flake 相关 —— 仅当 programs.nix-agent.flake 已设
{ command = "${nixosRebuild} dry-activate --flake ${flakeDir}*";                     options = [ "NOPASSWD" ]; }
{ command = "${nixosRebuild} switch --flake ${flakeDir}*";                           options = [ "NOPASSWD" ]; }
```

**三条硬约束**（原文）：

1. **`--flake` 钉死在 `<flakeDir>*`。** 原文：*"Do not grant a wildcard flake ref."*
2. **绝不授权 store 路径二进制。** 原文：*"Never grant NOPASSWD on a store-path binary,
   and never write a sudoers wildcard over `/nix/store/*/bin/switch-to-configuration`."*
   → 走 **profile 路径** `/nix/var/nix/profiles/system/bin/switch-to-configuration`
   （稳定符号链接），**不是** `/nix/store/<hash>-.../bin/...`（每次构建都变）。
3. **`flake` 未设时只发 rollback 规则**，别为了"方便"把 flake 参数放宽。

### 为什么 `build` / `diff` / `check("dry-build")` 不需要 sudo

它们只跑 `nix build`。**只有 `switch` 和 `check("dry-activate")` 走 sudo。**

## 4. 一个容易踩的坑：sudoers 必须匹配 `realpath` 后的路径

`nix-agent` 调用的是：

```python
sudo -n <realpath(shutil.which("nixos-rebuild"))> switch --flake <dir>#<host>
```

即 **`os.path.realpath()` 之后的 store 路径**，不是 PATH 上的名字。原因是
**sudoers 的 NOPASSWD 规则匹配的是解析后的路径**。

**手写 sudoers 时最容易踩这个。** 如果你自己写规则而不走模块，用
`readlink -f $(which nixos-rebuild)` 拿到真实路径再写。

失败时工具会返回结构化 `privilege` 诊断，里面明确说了这一点：

```jsonc
"privilege": {
  "cause": "sudo could not authenticate non-interactively",
  "detail": "... nix-agent invokes sudo -n with the resolved store path of the binary so a
             missing NOPASSWD rule fails immediately; a NOPASSWD rule must match that exact
             argv (without the sudo -n prefix).",
  "command_form": ["sudo", "-n", "/nix/store/.../nixos-rebuild", "switch", "--flake", "..."],
  "fixes": [
    "Enable programs.nix-agent.privilegedAutomation for this user and flake (documented default),
     or add a NOPASSWD sudoers rule for this command's store path.",
    "Lower trust: set SUDO_ASKPASS and run with sudo -A, or run from an interactive session."
  ]
}
```

**读 `command_form`** —— 那就是没匹配上的那条 argv。照着它写规则。

## 5. 降低信任（"降级"三档）

| 想要 | 怎么做 |
|---|---|
| **要 sudo 密码**（每次人工认证） | 不启用 `privilegedAutomation`（Nix 侧默认就是 `false`）。特权工具会 `sudo -n` 立即失败并返回 `privilege` |
| **要宿主在激活前弹窗** | 把 `switch` / `generations` 从宿主的 MCP 工具允许列表里去掉；Hermes 侧见 `hermes/mcp-servers.snippet.yaml` 的"只读阶段" |
| **完全不碰 sudo** | 只注册 `build` / `diff` / `eval_config` / `locate_option` / `check`（`tools.include` 白名单） |

**注意 `check("dry-activate")` 也用 sudo** —— 它和 `switch` 同级授权。只读阶段想彻底
不碰 sudo，就别把它放进白名单（用 `check("dry-build")` 代替）。

## 6. 凭据处理（继承自 nixi，并补上 MCP 侧的现状）

### 6.1 铁律

- **绝不把密码 / token / 私钥写进 `configuration.nix` 或 flake。**
- 用 **`sops-nix`** 或 **`agenix`**；agent 只编辑**引用**，不碰明文。
- 需要明文凭据时，**直接传给工具，不经过对话上下文**。

### 6.2 声明式 secret 的最小骨架

```nix
# sops-nix 示例
sops.defaultSopsFile = ./secrets/secrets.yaml;
sops.age.keyFile = "/var/lib/sops-nix/key.txt";
sops.secrets."smb/password" = { owner = "root"; mode = "0400"; };
```

然后在服务里引用 `config.sops.secrets."smb/password".path`，**而不是**写明文。

### 6.3 凭据文件的落盘规则（沿用 nixi 的做法）

| 项 | 规则 |
|---|---|
| 位置 | `/srv/.credentials/` |
| 权限 | **`0600`，root 所有** |
| 协议协商 | SMB 依次试 3.0 → 2.1 → 2.0 |
| 依赖 | SMB 需 `cifs-utils`，NFS 需 `nfs-utils` 在系统包里 |

### 6.4 ⚠️ 转换后的失效点（重要）

nixi 有两条保证是**在 Go 代码里强制**的，本 port **没有强制力**：

| nixi 的保证 | skill 侧现状 | 怎么补 |
|---|---|---|
| **凭据走掩码输入直传工具，永不进 LLM 上下文** | 只能"要求"，无法强制 | 宿主支持 secret 注入就用；否则**用户手动输入**，或让用户自己改 sops 文件 |
| **工具输出自动脱敏** | 只能"要求" | 宿主的工具输出过滤 + agent 自觉 |

**结论**：**不要让 agent 经手明文凭据。** 让它改 `sops` 引用、告诉你该填哪个 key，
由人来填。

## 7. `/srv/` 所有权模型（继承自 nixi）

- `/srv/` 归 agent 用户所有 → 容器数据与文件操作在 `/srv/` 下**不需要 sudo**
- 容器数据**强制**在 `/srv/<container-name>/`
- volume mount 只接受 `/srv/`（容器数据）和 `/mnt/`（外部 NFS/SMB/USB）
- **`/srv/` 之外的挂载在 nixi 工具层直接拒** —— 本 port 没这层，只能靠规则 + 你的
  宿主 `ALLOW_PATTERNS` 兜

## 8. 宿主持平对照（合并 nixi-port 与本 port 的结论）

| 需要强制的 | nixi 的机制 | Hermes 侧的对应物 |
|---|---|---|
| 变更命令不许跑 | `MonitoredExecutor` 在 executor 层硬拒 | **`tools.include` 只放只读工具**（真正的白名单） |
| 写能力工具要审批 | 工具级确认门（`confirmed` 参数从 schema 隐藏） | **`trust: untrusted`** → 对写能力工具逐个弹审批 |
| 路径边界 | `/srv/` 在工具层拒 | 宿主 `ALLOW_PATTERNS` 正则 |
| root 边界 | scoped sudo 白名单 | **`programs.nix-agent.privilegedAutomation`**（可直接抄，无差距） |
| 凭据不进上下文 | 掩码输入 | ❌ 无等价物，靠流程 |

**最省力的组合**：`AGENTS.md`（判断）+ `nixos-ops` skill（规则）+ **`tools.include` 白名单
（强制）** + **`programs.nix-agent.privilegedAutomation`（root 边界）**。
