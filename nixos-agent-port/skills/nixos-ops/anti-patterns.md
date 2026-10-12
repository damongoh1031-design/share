# 反模式清单（任务结束前自查）

v2 在 nixi 的 8 类之上，加了 **MCP 时代的反模式**（绕过工具、误读回执、把 pin 当沙箱）。

## A. 绕过工具类（v2 新增，最容易犯）

| 反模式 | 后果 | 正确做法 |
|---|---|---|
| 自己跑 `nix eval <attr>` 而不是 `eval_config` | 把 13,500 B 的原始值塞回上下文（护栏本来塌缩到 394 B） | `eval_config(attr)`；多个传 list 批量 |
| grep 整个仓库找"这个 option 在哪设的" | 慢且噪音大 | `locate_option(attr)` |
| 失败后跑 `nix log <drv>` | 白跑 —— 回执里 `failed_derivation.log_tail` 已经有 | 读那个字段 |
| switch 后跑 `systemctl --failed` | 白跑 —— `summary.health` 已经有前后 diff | 读 `summary.health` |
| 为了"看全"传 `full_log=True` | 等于抹掉这个服务器存在的理由 | 只在裁剪视图确实不够时用 |
| 直接敲 `nixos-rebuild switch` | 丢掉 `rollback_generation`、`summary`、日志裁尾 | `switch()` |

**自查问句**：这次任务里我敲的每一条 nix 命令，`tool-map.md` 主表里有对应工具吗？

## B. 误读回执类（v2 新增）

| 反模式 | 后果 | 正确做法 |
|---|---|---|
| 把 `status: "degraded"` 当成功 | 激活成功但有 unit 新失败 —— 那是问题 | 读 `summary.health`，默认回滚 |
| 裸 `generations(action="rollback")` 当"回这次 switch 之前" | 只回**上一代**，中间有别的 switch 就不是你要的 | 用 `rollback_generation` 或显式 `generation=` |
| 看到 `truncated: true` 就重试要全量 | 徒劳 | eval 一个**子 attr** |
| 忽略 `resolved_target` / `command` | 它们就是为了让你发现"目标错了" | **先看这两个字段** |
| 把 `first_error` 之外的部分当错误 | 噪音 | 读三个字段就停 |
| 在 MCP 回执里找 `raw_bytes` | 已被剥离，找不到 | 只看 usage log |
| 重试 `unknown_host` / `target_locked` / `remote_ref_rejected` | 这三个是**早退**，没跑任何命令 | 改输入（显式 `flake_uri` / pin 目录 / 先 clone） |

## C. NixOS 语义类（继承自 nixi）

| 反模式 | 后果 | 正确做法 |
|---|---|---|
| 把"更新锁文件 + rebuild"合成一步 | 掩盖 `flake.lock` 变更这个决策点 | `nix flake update` **单独**给用户看 diff，再 rebuild |
| 改完配置就说"已生效" | 内核/驱动要 reboot 才加载 | 明确提示需 reboot |
| 清理 generation 不说保留几个 | 把回滚目标删了 | 展示列表 + 说明保留范围 + 确认 |
| 假设 `nix develop` 等价于 venv | 不是；它是完整闭包环境 | 知道区别 |
| 把 devShell 的包当系统包用 | devShell 只在当前 shell 会话有效 | 要长期存在就进 `environment.systemPackages` |
| 在宿主机 `pip install` / `npm i -g` | 污染非声明式状态 | 用 `nix develop` |
| `nix-shell -p python3` 一次性用完就走 | 项目有 flake 就该 `nix develop` | |
| 手写 `/etc/` 下的文件期望永久生效 | 下次 rebuild 就被覆盖 | 改配置 |

**社区原话**：*"not understanding devShells"* 是 AI 在 Nix 上最常犯的错之一。

## D. 权限与安全类

| 反模式 | 后果 | 正确做法 |
|---|---|---|
| 把 `$NIX_AGENT_FLAKE` 当沙箱 | 它只是 anti-footgun；agent 能改被 pin 的树，也能改 `.mcp.json` | **真正的边界是 sudoers** |
| sudoers 写 `--flake *` | 等于给任意 flake 免密 root 激活 | 钉死 `<flakeDir>*` |
| sudoers 授权 `/nix/store/*/bin/switch-to-configuration` | store 路径每次构建都变，通配等于全放 | 走 profile 链接 `/nix/var/nix/profiles/system/bin/...` |
| 手写 sudoers 用 PATH 名字 | 规则不匹配（要匹配 `realpath` 后的 store 路径） | 用 `nixosModules.default`，或 `readlink -f $(which ...)` |
| 给 agent 用户免密 `rm` / `cp` / `mv` | 等于给了任意文件操作 | 明确不给这三条 |
| 让 agent 经手明文凭据 | nixi 的"掩码直传"保证在本 port **已失效** | 只改 sops/agenix **引用**，明文由人填 |
| 把密码写进 `configuration.nix` | 明文进 `/nix/store`（全世界可读） | `sops-nix` / `agenix` |

## E. 流程类

| 反模式 | 后果 | 正确做法 |
|---|---|---|
| rebuild 失败原地反复重试同一配置 | 浪费轮次 | 先 `generations(action="rollback")` 回可用状态，再分析 |
| 说"已完成"而实际只跑了 dry-run | 最严重的信任破坏 | 区分"已验证"与"已应用" |
| 用户说"只看看"时调 `switch()` | 越权 | `diff()` 就是 preview |
| 反过来，没说过"只看看"还反复问要不要执行 | 摩擦 | 默认 apply：`diff()` 后直接 `switch()` |
| 每一小步都二次确认 | 摩擦 | 用户说 "yes 并且顺便做 X" 时合并成一个工作流**一次确认** |
| 编包名 / option 名 | 最难查的错误 | `nixos-query` 查证；查不到就说查不到 |
| 在 `/srv/` 之外挂载或写容器数据 | 越过 nixi 的边界（本 port 无工具层强制） | 强制 `/srv/<name>/` |

## 结束前自查（30 秒）

1. **工具**：我绕过了 `tool-map.md` 里的任何一条吗？
2. **回执**：我读过 `resolved_target` / `command` 吗？有 `degraded` 或 `truncated` 被忽略吗？
3. **确认**：用户明确 yes 了吗？还是我自己批准的？
4. **回滚**：我记下 `rollback_generation` 了吗？用户知道怎么退吗？
5. **诚实**：我报告的是"已验证"还是"已应用"？有没有把 dry-run 说成完成？
6. **凭据**：有没有明文凭据经过我的上下文？
