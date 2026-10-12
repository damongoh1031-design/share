# 给 agent 开 root：窄 sudo 与 pin 的真实作用

> **TL;DR** 一个会改系统的 agent，它的权限边界**只有一处是真的：sudoers**。
> pin（钉死目标目录）、宿主工具白名单、提示词禁令都只是"防手滑"。
> 把它们混为一谈，是这类项目最常见的安全误判。**最诚实的做法是：代码里承认这一点，
> 文档里写清楚，CI 里断言它。**

标签：`mcp-design` `permissions` · 证据等级：`A`（源码与官方文档直读）

## 问题

让 AI agent 执行 `nixos-rebuild switch` 这类操作，必然要过 sudo。四种常见做法及其真实强度：

| 做法 | 真实强度 | 挡得住什么 |
|---|---|---|
| 提示词说"不要乱改" | ❌ 无 | 什么都挡不住（模型可以不听） |
| 宿主把工具从白名单去掉 | ⚠️ 中 | 挡"调用这个工具"，**不挡** agent 改用 shell |
| pin 钉死目标目录 | ⚠️ 中 | 挡"指错目录"，**不挡**越权 |
| **窄 sudoers 规则** | ✅ **强** | **真正的 root 边界** |

## 模式：三层要分开命名，不要混

### 第 1 层：提示词 / skill 规则（"防手滑"，不是边界）

写在 skill 与 AGENTS.md 里的规则。**它们的作用是让 agent 做对的事，不是阻止它做错的事。**

### 第 2 层：宿主工具白名单（"防误调"，不是边界）

宿主（Hermes / Codex / …）可以按**工具名**过滤 MCP 工具。

> 例（Hermes）：`mcp_servers.<name>.tools.include` 是白名单，支持 fnmatch glob，
> **`include: []` 表示一个工具都不注册**；`include` 优先于 `exclude`。

**⚠️ 已知局限（源码里明说的）**：宿主白名单**看不见工具参数**。所以"允许 `switch`" =
"允许它 switch 到任何目标"。这就是为什么第 3 层必须存在。

### 第 3 层：sudoers（**唯一的真边界**）

把 NOPASSWD 规则**窄到具体命令形态**：

```nix
# ✅ 钉死 flake 目录
{ command = "${nixosRebuild} switch --flake ${flakeDir}*"; options = [ "NOPASSWD" ]; }
# ✅ 无参数的固定形态
{ command = "${nixosRebuild} switch --rollback";           options = [ "NOPASSWD" ]; }
```

两条**硬禁令**：

| 禁令 | 为什么 |
|---|---|
| **不通配 `--flake *`** | 等于给任意 flake 免密 root 激活 |
| **不授权 store 路径二进制** | store 路径每次构建都变，通配 `/nix/store/*/bin/switch-to-configuration` 等于全放。**走 profile 符号链接**（稳定路径） |

### 第 3.5 层：pin（"防手滑"，刻意不叫边界）

pin = 把目标目录写进环境变量，让"省略参数"时有个确定答案。

> 例（`nix-agent`）：`programs.nix-agent.flake = /home/alice/nixos` 会 wrap 二进制注入
> `NIX_AGENT_FLAKE`。

**它为什么不是边界**（上游文档原文，值得逐字读）：

> `$NIX_AGENT_FLAKE` ... is an **anti-footgun, not a security boundary**. The agent can still
> edit the pinned tree and, if it can edit MCP config, the pin in `.mcp.json`.
> **The privilege boundary that actually runs as root is sudoers.**

即：pin 挡不住"改被 pin 的那棵树"，也挡不住"改 pin 本身"。**它只挡"指错目录"。**

## 三个配套设计（都很值得抄）

### ① `realpath` 匹配

sudoers 的 NOPASSWD 规则匹配的是**解析后的真实路径**，不是 PATH 上的名字。

```python
found = shutil.which("nixos-rebuild")          # /run/current-system/sw/bin/nixos-rebuild
resolved = os.path.realpath(found)             # /nix/store/<hash>-nixos-rebuild/bin/nixos-rebuild
argv = ["sudo", "-n", resolved, "switch", ...] # ← 用解析后的
```

**手写 sudoers 时最容易踩这个。** 要用 `readlink -f $(which ...)`。

### ② `sudo -n` + 结构化失败诊断

用 `sudo -n`（non-interactive）：**缺规则时立即失败，而不是挂在一个 MCP 服务器无法回答的
密码提示上**。然后把失败转成结构化诊断：

```jsonc
{
  "cause": "sudo could not authenticate non-interactively",
  "command_form": ["sudo","-n","/nix/store/.../nixos-rebuild","switch","--flake","..."],
  "fixes": ["Enable <the privileged-automation option> ...",
            "Lower trust: set SUDO_ASKPASS and run with sudo -A ..."]
}
```

**`command_form` 就是没匹配上的那条 argv** —— 照着它写规则。比 "permission denied" 有用一个数量级。

### ③ 把安全约束写成 CI 断言

不要只写在文档里靠人记。上游的做法是**在 CI 里 evaluate 配置模块，断言生成的 sudoers**：

> 例（`nix-agent` v0.11.0）：`checks.nixos-module` 实际 evaluate NixOS module，
> 断言"窄 flake ref、有 rollback、有 switch-generation、有 profile `switch-to-configuration`；
> **没有 `--flake *`、没有 store 路径通配符**"。

**这是把"安全设计"从文档承诺变成机器可验证的约束。**

## 远程引用与"混淆代理"（confused deputy）

一个会 root 的工具如果接受**远程引用**（`github:` / `https://` / `git+`），它就成了一条
"让远程内容变成 root 激活"的路径。所以特权工具应该**默认拒绝远程引用**：

```
status: "remote_ref_rejected"
error: "privileged operations do not accept remote flake refs"
hint:  "clone the repository locally and pin that directory"
```

**并且要有一个只能由人打开的开关**（环境变量），**不要把它写进给 agent 的错误提示里**
（否则 agent 会自己打开它）。

## 顺带：目录自动搜索是隐患

如果工具会在若干"常见位置"里自动找配置文件，而**当前工作目录**也在搜索路径里，
那么"agent 在别的项目目录下运行"就可能操作到**无关的配置**。

> 上游的做法是**刻意不搜索 cwd**，注释原文：
> "an MCP server's cwd is usually the caller's project dir (which may carry an **unrelated**
> config file), so it is a **wrong-flake hazard**."

**宁可报错要求显式指定，也不要猜。** 这是"防手滑"设计的正确形态。

## 检查清单

给一个会 root 的 agent 做权限设计时问：

1. **真正的边界写在哪？** 如果不是 sudoers / polkit / capabilities，那就是没有边界。
2. sudoers 规则**窄到具体命令形态**了吗？有没有通配参数？有没有通配 store 路径？
3. 用的是**解析后的真实路径**吗？
4. 用 `-n` 了吗？（还是让 agent 挂在密码提示上？）
5. 失败时给的是"permission denied"还是**具体的 argv + 修法**？
6. 接受远程引用吗？默认拒了吗？开关只由人开吗？
7. **pin / 白名单 / 提示词有没有被误当成边界？** 文档里说清楚了吗？
8. 安全约束进 CI 了吗？

## 相关

- [mcp-envelope-protocol](./mcp-envelope-protocol.md)
- [mcp-nixos-vs-nix-agent](../comparisons/mcp-nixos-vs-nix-agent.md)
