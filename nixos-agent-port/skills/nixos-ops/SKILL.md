---
name: nixos-ops
description: "Operate a NixOS or Home Manager configuration with the nix-agent MCP tools — build, diff, switch, generations/rollback, eval_config, locate_option, check. Use when changing packages, options, or modules; diagnosing a failed build or switch; rolling back a generation; or asking what the live config currently resolves to. Covers the areas the MCPs do NOT cover (containers, mounts, GPU, multi-node) as CLI recipes."
version: 2.0.0
author: 合并自 codeberg.org/ewrogers/nixi 的规范（AGPL-3.0）与 JEFF7712/nix-agent 的工具面（MIT）
license: 转换产物 —— 规范来源见 README.md 的许可章节
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [NixOS, Home-Manager, nix-agent, rebuild, rollback, generations, sudoers, systemd, containers, GPU, multi-node]
    category: devops
    related_skills: [nixos-query]
    requires_toolsets: [mcp, terminal]
prerequisites:
  commands: [nix]
  mcp_servers: [nix-agent]
---

# nixos-ops — 在 NixOS 上安全地做变更

> **v2.0.0 是合并版**：v1 是纯规范（来自 nixi），v2 把 `JEFF7712/nix-agent` 的 7 个 MCP 工具
> 接进执行路径，并保留两个 MCP 都不覆盖的区域。合并映射见 `README.md`。

## 0. 开始前必读（五条铁律）

1. **先查证，再动手。** 包名 / 选项名 / attribute path 用 `nixos-query` 技能（`mcp-nixos`）
   查证。查不到就说查不到，不要编。
2. **先 dry-run，再 apply。** 变更前 `check("dry-build")` 或 `check("dry-activate")`，
   把 diff 给用户看。
3. **绝不自我批准。** rebuild / rollback / reboot / 装包 / 删容器 / 改防火墙 / 清 generation
   —— 全部要用户明确 yes。用户说 "yes 并且顺便做 X" 时，合并成一个工作流**一次确认**。
4. **`degraded` ≠ 成功。** `switch()` 返回 `status: "degraded"` = 激活成功但有 unit 新失败。
   报告 `summary.health`，默认回滚。
5. **有工具就别用 shell。** 见 `tool-map.md`。绕过 MCP 会重新付一遍它替你省掉的上下文成本。

## 1. 七个工具（两个层次）

### 操作核心 —— 改机器的

| 工具 | 签名 | 干什么 |
|---|---|---|
| `build` | `(flake_uri?, mode?)` | 构建闭包，**不激活**。失败带 `failed_derivation{drv, log_tail}` |
| `diff` | `(flake_uri?, mode?)` | 新闭包 vs **运行中的系统**：包增删与版本变化。**这就是 preview** |
| `switch` | `(flake_uri?, mode?, validate?, full_log?)` | 激活。**先记 `rollback_generation`**，成功后返回结构化 `summary` |
| `generations` | `(action="list"\|"rollback", mode?, generation?)` | 列 / 回滚 generation |

### 配置内省 —— 只看不改的

| 工具 | 签名 | 干什么 |
|---|---|---|
| `eval_config` | `(attr, flake_uri?, mode?)` | **这台机器上**某属性的最终合并值。`attr` 传 **list 可批量** |
| `locate_option` | `(attr, flake_uri?, mode?)` | 某 option 由哪些文件声明/定义、各贡献什么值 |
| `check` | `(level, flake_uri?, mode?)` | 验证阶梯：`lint` → `dry-build` → `dry-activate` |

## 2. 决策表：用户意图 → 该做什么

| 用户说 | 第一步 | 确认？ |
|---|---|---|
| 看版本 / 状态 / 日志 / 端口 / 服务列表 | 只读命令直接跑 | ❌ |
| "这个 option 现在是什么值" | `eval_config(attr)`（多个传 list） | ❌ |
| "这个 option 在哪配的" | `locate_option(attr)` | ❌ |
| "这个包在不在 / 叫什么" | 走 `nixos-query`（`mcp-nixos`） | ❌ |
| 装 / 删包 | 改 `environment.systemPackages` → `check("dry-build")` | ✅ |
| 开 / 关防火墙端口 | 改 `networking.firewall.allowedTCPPorts` → dry-run | ✅ |
| 启动 / 停止 / 重启服务 | `systemctl restart <unit>` | ❌ |
| enable / disable 服务 | `systemctl enable/disable`（提示 rebuild 后可能被覆盖） | ❌ |
| 重建系统 / 改配置 | `check("dry-activate")` → `diff()` → 等确认 → `switch()` | ✅ |
| 只看这次会改什么 | `diff()` | ❌ |
| 回滚 | `generations(action="list")` → 等确认 → `generations(action="rollback", generation=<id>)` | ✅ |
| 升级系统 | 先判 flake/channel → 见 `rebuild-and-generations.md` | ✅ |
| 清理 generation | 展示可回收 → 确认 → **告知保留几个** | ✅ |
| 增删 channel / flake input | 展示将要改的锁文件 diff | ✅ |
| 加 / 删用户、改组、改 shell | 改 `users.users.<name>` → dry-run | ✅ |
| 加 SSH key | 直接写 `~/.ssh/authorized_keys`（免 rebuild） | ❌ |
| 设密码 / 锁 / 解锁用户 | `passwd` / `usermod -L/-U`，**不要 rebuild** | ❌ |
| 装 NVIDIA / AMD 驱动 | 读 `no-mcp-coverage.md` §3-§4 → dry-run → **提示需 reboot** | ✅ |
| 部署 / 更新 / 删除容器 | 读 `no-mcp-coverage.md` §1（**无 MCP 覆盖**） | ✅ |
| 挂载 NFS / SMB / USB | 读 `no-mcp-coverage.md` §2 | unmount/持久化 ✅，mount/list ❌ |
| 建 / 删定时任务 | systemd timer（`no-mcp-coverage.md` §6） | 建/删 ✅，list/status ❌ |
| 管多台机器 | 读 `no-mcp-coverage.md` §5 —— **`nix-agent` 只操作本机** | ✅ |

## 3. 执行顺序（每个变更请求都按这个走）

```
1. 查证        nixos-query 查包名/option（防幻觉）
2. 定位        eval_config 看当前值 / locate_option 看该改哪个文件
3. 读配置      读相关 .nix 文件
4. 改文件      宿主原生 Read/Edit/Write
5. 格式化      nix fmt 或 nixfmt（Bash —— 没有工具覆盖）
6. lint        check("lint")
7. dry-build   check("dry-build")        ← 便宜地抓 eval/build 错误
8. 出 diff     diff()                    ← 把 changeset 给用户看
9. 等确认      用户明确 yes
10. 激活       switch()
11. 验结果     读 summary（units/derivations/packages/health）
12. 失败即退   见 §5
```

**第 6–8 步是判断题，不是闸门。** 琐碎改动（改一个字符串、加一个包）直接 `switch()` 也可以。
但**第 9 步永远是闸门**。

## 4. 失败处理：读三个字段然后停

工具失败时，**按顺序读这三个，不要自己重跑命令**：

1. **`first_error`** —— 第一个像 error 的 stderr 行。这就是可操作的那句。
2. **`error_detail`** —— 当 Nix 抛 eval 错误时是 `{message, file, line, column, trace}`。
   **这是直接的 file:line:column 编辑目标。**
3. **`failed_derivation.log_tail`** —— 失败的 builder 日志，**已经替你跑过 `nix log` 了**。

**不要**在字段存在时再跑 `nix log`，也不要为了看全量而传 `full_log=True`。

### 几种 status 的含义

| status | 含义 | 该做什么 |
|---|---|---|
| `preflight_failed` | `switch(validate=True)` 的 dry-build 没过，**从未激活** | 修嵌套的 `preflight`，**不要重试激活** |
| `privilege` | sudo 认证失败，**不是 Nix 错误** | 见 `sudo-and-secrets.md` |
| `degraded` | 激活成功但 unit 新失败 | 报告 `summary.health`，默认回滚 |
| `unknown_host` | flake 里的主机名对不上（`hosts` 字段列了全部） | 传显式 `flake_uri`（`.../repo#realhost`）或设 `$NIX_AGENT_FLAKE` |
| `unknown_generation` | generation id 不存在 | **没跑任何命令**；先 `generations(action="list")` |
| `target_locked` | 设了 pin 但指到了别的目录 | **没跑任何命令**；改回 pin 目录 |
| `remote_ref_rejected` | 特权工具拒收远程 flake ref | **没跑任何命令**；先 clone 到本地 |
| `not_an_option` | 该 attr 不是 option（是普通配置值） | 改用 `eval_config` |
| `tool_missing` | `check("lint")` 找不到 statix/deadnix | 装进 `environment.systemPackages` |

**后四个是早退：没有命令被执行过。**

### 回滚

```
switch() → 记住 rollback_generation
generations(action="rollback", generation=<rollback_generation 或具体 id>)
```

- **裸 `generations(action="rollback")` 只回上一代**，不是回 `rollback_generation`。
  只有当之后没有任何东西再 switch 过，它才是对的默认。
- 目标不确定时先 `generations(action="list")` 拿 id。

## 5. `mode` 怎么选（**改 HM 前必读**）

`mode` 默认 `"nixos"`。**不要因为任务涉及 Home Manager 就反射性地改成 `"home-manager"`**
—— 这是最常见的"操作错配置"方式。

| 布局 | 特征 | 用什么 |
|---|---|---|
| **集成式 HM** | 通过 `home-manager.nixosModules.home-manager` + `home-manager.users.*` 挂在 NixOS 上；**没有独立的 `home-manager switch`** | `mode="nixos"`（默认），switch 整个系统 |
| **独立式 HM** | 自己的 flake 暴露 `homeConfigurations.*`，用 `home-manager switch` 应用 | `mode="home-manager"` |

两种都存在时，**独立的那份往往是历史遗留**。动手前先确认哪个真正生效
（对两者各跑一次 `eval_config`，或看当前 generation 是从哪个构建的）。拿不准就选 `nixos`。

非标准 / 多 flake 布局：**不要依赖自动解析**，显式设 `NIX_AGENT_FLAKE`（独立 HM 用
`NIX_AGENT_HM_FLAKE`），或传 `flake_uri` 如 `/home/you/nixos#host`。

集成式 HM 的 option 查询用 `eval_config(attr="home-manager.users.<user>.<attr>")`
（`mode="nixos"`）。传不带前缀的 attr 时工具会自动重试这个写法（回执带 `hm_rewritten: true`）。

## 6. 明确禁止

- ❌ `find /nix/store/* -iname lib*.so` —— 用 `nix-locate`（`nix-index`）
- ❌ `nix-env -i` / `nix profile install` 装系统包 —— 走 `environment.systemPackages`
- ❌ 把密码 / token 写进 `configuration.nix` 或 flake —— 用 `agenix` / `sops-nix`
- ❌ 给 agent 用户免密 `rm` / `cp` / `mv`
- ❌ sudoers 通配 `--flake *`，或通配 `/nix/store/*/bin/switch-to-configuration`
- ❌ 改 `system.stateVersion`（除非用户明确要求）
- ❌ rebuild 失败原地反复重试 —— 先 rollback
- ❌ 说"已完成"而实际只跑了 dry-run
- ❌ 在宿主机 `pip install` / `npm i -g` —— 用 `nix develop`
- ❌ 用户说"只看看 / 先别动"时调 `switch()`

## 7. 参考文件

| 文件 | 什么时候读 |
|---|---|
| `tool-map.md` | **每次要敲 nix 命令前** —— shell 命令 → MCP 工具对照 |
| `envelope-cheatsheet.md` | 工具返回后 —— 哪些字段已替你预取，别重复取 |
| `confirmation-matrix.md` | 拿不准某个操作要不要确认时 |
| `rebuild-and-generations.md` | 重建 / 升级 / generation / 包管理配方 |
| `sudo-and-secrets.md` | 涉及 sudo、权限、凭据时（含可直接落地的 NixOS 模块） |
| `no-mcp-coverage.md` | **两个 MCP 都不覆盖**：容器 / 挂载 / GPU / 多节点 / 定时任务 |
| `anti-patterns.md` | **每次任务结束前自查一遍** |

## 8. 加载本 skill 时的第一句话建议

```text
我在管 NixOS。先读我的配置（/etc/nixos 或 flake 目录），用 eval_config 看当前实际值，
告诉我你发现了什么，把变更作为 diff 提议给我。不要 switch、不要装东西、不要跑容器，等我批准。
```
