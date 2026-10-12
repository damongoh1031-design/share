# 反模式清单（每次任务结束前自查）

> 来源：nixi `docs/` + `nixos-management-skill/anti-patterns.md` +
> NixOS Discourse #80199 社区反馈。**这是本 skill 里最该熟记的一份。**

## A. 查找与诊断

| ❌ 错误 | ✅ 正确 |
|---|---|
| `find /nix/store/*something* -iname libfoo.so` | `nix-locate libfoo.so`（nix-index） |
| 猜 `pkgs.foo` 存在就写进配置 | `nix search nixpkgs foo` 查证 |
| 猜 `services.foo.enable` 是个选项 | `nix eval nixpkgs#nixosConfigurations…` 或用 `mcp-nixos` 查 |
| 凭记忆写 Nix 语法 | 让 `nixd` LSP 或 `nix flake check` 先验 |

## B. 装包

| ❌ 错误 | ✅ 正确 |
|---|---|
| `nix-env -i foo` 装系统级包 | 改 `environment.systemPackages` + rebuild |
| `nix profile install nixpkgs#foo` 装系统级包 | 同上 |
| 三个包分三次 rebuild | 一次改配置、一次 rebuild、一次确认 |
| 装完不问是系统级还是用户级 | 系统级 → 配置；一次性 → `nix shell nixpkgs#foo` |

## C. rebuild 与升级

| ❌ 错误 | ✅ 正确 |
|---|---|
| 直接 `nixos-rebuild switch` 不 dry-run | 先 `dry-activate`，把 diff 给用户看 |
| rebuild 失败原地反复重试 | 先 `--rollback` 回可用状态，再分析错误 |
| flake 模式下把 `nix flake update` 和 `switch` 合成一步 | 分两步，锁文件 diff 单独给用户看 |
| 假设 switch 后内核/驱动已生效 | 提示需要 reboot |
| 声称"已完成"其实只跑了 dry-run | 明确说这是 dry-run |
| 跳过 `git diff flake.lock` | 升级前必看，这是"到底升了什么"的唯一答案 |
| `systemctl enable foo` 后以为 rebuild 也不会丢 | 提醒：NixOS 管理的服务会被配置覆盖 |

## D. 凭据与安全

| ❌ 错误 | ✅ 正确 |
|---|---|
| 密码 / token / API key 写进 `configuration.nix` 或 flake | `agenix` / `sops-nix` 加密引用 |
| `POSTGRES_PASSWORD=xxx` 明文进 compose | secret 文件注入 |
| `chpasswd` 带明文参数 | `passwd <user>` 交互式 |
| 把 SMB 凭据写进配置或命令行 | `/srv/.credentials/` root 600 |
| 给 agent 用户免密 `rm` / `cp` / `mv` | 只给 `secrets-sudo-scope.md` 列出的命令 |
| 把包含密码的命令行贴给用户看 | 脱敏后再展示 |
| 读 NixOS 配置时整文件 raw 输出 | 过滤 `password`/`secret`/`token`/`key` 行 |

## E. 容器与数据

| ❌ 错误 | ✅ 正确 |
|---|---|
| 容器数据放 `/var/lib/xxx` 或家目录 | 强制 `/srv/<container-name>/` |
| 删容器默认连带删数据 | 默认保留，purge 才删且需显式确认 |
| 跨节点容器用容器名互访 | 跨节点用节点 IP |
| 挂 NAS 不写 `x-systemd.automount` | 必须写，否则 NAS 离线时开机卡住 |
| `rm -rf /srv/<name>` 前不问 | 必须显式确认 |

## F. 用户与权限

| ❌ 错误 | ✅ 正确 |
|---|---|
| 改 `system.stateVersion` | 除非用户明确要求，否则不动 |
| 动 `root` 或系统用户 | 受保护，不要碰 |
| 加个用户就 rebuild | SSH key / 密码 / 锁定 都不需要 rebuild |
| 用户名用大写或特殊字符 | 小写字母数字 + 连字符 + 下划线 |

## G. 沟通方式

| ❌ 错误 | ✅ 正确 |
|---|---|
| "我会修改配置" 然后直接改 | 给出**具体 diff** 再问 |
| 一次确认拆成三次 | 批量合并成一次 |
| 用户说 "yes 顺便做 X" 还二次确认 | 合并成一个工作流 |
| 静默失败（命令报错不报告） | 报错原因 + 建议修法 |
| dry-run 结果说成"已完成" | 区分"已预览"与"已应用" |

## H. devShell（agent 最容易搞错的）

| ❌ 错误 | ✅ 正确 |
|---|---|
| 在宿主机 `pip install` / `npm i -g` | 用 `nix develop` 进 flake 的 devShell |
| `nix-shell -p python3` 一次性用完就走 | 项目有 `flake.nix` 就用 `nix develop` |
| 把 devShell 的包当系统包用 | devShell 只在当前 shell 会话有效 |
| 假设 `nix develop` 等价于 venv | 不是；`nix develop` 是完整闭包环境 |

**社区原话**：*"not understanding devShells"* 是 AI 在 Nix 上最常犯的错之一。
