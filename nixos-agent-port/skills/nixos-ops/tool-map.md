# shell 命令 → MCP 工具对照表

**敲任何 nix 命令之前先查这张表。** 直接 shell 会重新付一遍 `nix-agent` 替你省掉的上下文成本。

## 主表

| 你本来想敲 | 改用 | 为什么 |
|---|---|---|
| `nixos-rebuild switch` / `boot` / `test`（本机） | `switch()` | 结构化 `summary` + 自动记 `rollback_generation` + 日志裁尾 |
| `home-manager switch`（本机、独立式） | `switch(mode="home-manager")` | 同上 |
| `nix build ...#...toplevel` | `build()` | 失败带 `failed_derivation.log_tail`（已跑过 `nix log`） |
| `nix build ...#....activationPackage` | `build(mode="home-manager")` | |
| `nixos-rebuild dry-activate`（本机） | `check("dry-activate")` | 同样走远程 ref / pin 分类器 |
| `nix build --dry-run` | `check("dry-build")` | |
| `statix check` / `deadnix` | `check("lint")` | 返回结构化 `findings`（不是原始输出） |
| `nvd diff` / `nix store diff-closures` | `diff()` | 结构化 `packages{added,removed,changed}` |
| `nixos-rebuild list-generations` | `generations(action="list")` | |
| `nixos-rebuild switch --rollback` | `generations(action="rollback")` | 但**只回上一代**；精确回滚传 `generation=` |
| `nix-env -p /nix/var/nix/profiles/system --switch-generation N` + `switch-to-configuration switch` | `generations(action="rollback", generation=N)` | 两步合一 |
| `nix eval <config>#...attr` | `eval_config(attr)` | **2 KB 尺寸护栏**：13,500 B → 394 B |
| 在仓库里 grep "这个 option 在哪设的" | `locate_option(attr)` | 一次调用回答，不用 grep 整个树 |
| 失败后 `nix log <drv>` | 读 `failed_derivation.log_tail` | **已经替你跑了** |
| switch 后 `systemctl --failed` | 读 `summary.health` | 含前后 diff + journal tail |
| 想知道"这个包在不在 / option 叫什么" | `nixos-query` 技能（`mcp-nixos`） | 防幻觉 |

## 必须留在 Bash 的（没有工具覆盖）

| 事情 | 命令 | 为什么不在 MCP 里 |
|---|---|---|
| 格式化 | `nix fmt` 或 `nixfmt <files>` | `nix-agent` 明确不做格式化（用 flake 自己的 formatter） |
| 文件编辑 | 宿主原生 Read/Edit/Write | `nix-agent` 的工具**不读不写文件** |
| **远程部署** | `nixos-rebuild switch --flake ...#host --target-host admin@ip --use-remote-sudo` | **特权工具按设计拒绝远程 ref** |
| 集群部署 | `colmena apply` / `deploy .#host` | 见 `no-mcp-coverage.md` §5 |
| 容器 / 挂载 / GPU / 定时任务 | 见 `no-mcp-coverage.md` | 两个 MCP 都不覆盖 |
| 升级时的锁文件操作 | `nix flake update` | 见 `rebuild-and-generations.md` |
| 垃圾回收 | `nix-collect-garbage` | 没有工具覆盖 |

## 一个真实的边界

`nix-agent` 的 `switch` **只操作本机**。SKILL 原文：

> Reach for Bash only for what has no tool: formatting (`nix fmt`), file edits, and
> remote-target deploys (`--target-host`, `--use-remote-sudo`), which **privileged tools
> reject by design**.

所以"给 web-server 那台机升级"这类请求，**不要**试 `switch()` —— 会得到
`remote_ref_rejected`。走 Bash + `--target-host`，或 colmena。

## 为什么值得这么较真

`nix-agent` 的 `docs/usage.md` 里有一段实测（作者在真实 NixOS 笔记本上采集）：

| 操作 | 原始字节 | 回执字节 |
|---|---|---|
| `eval_config("environment.systemPackages")` | **13,500** | **394** |
| `diff`（近乎空的 diff） | 338 | 1,431 |
| `locate_option("environment.systemPackages")` | 24,066 | 20,396 |

第一行是最典型的：原始值是一大串 store 路径，护栏把它塌缩成"长度 + 头切片"。
**你绕过工具自己跑 `nix eval`，就是把那 13 KB 全部塞回上下文。**

> ⚠️ 第三行是**诚实的反例**：`locate_option` 在这个 option 上省得很少（那个 option 定义在
> 95 个文件里）。它进工具集的理由是"**一次调用回答哪个文件**"，不是"封顶一个 firehose"。
> 别指望它一定省 token。
