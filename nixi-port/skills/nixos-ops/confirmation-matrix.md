# 确认矩阵详解

> 来源：nixi `docs/security.md`。**在通用 agent 里这套矩阵是"建议"而不是"强制"**——真正的
> 强制必须靠宿主的审批机制或受限 MCP。见 `../README.md` 的「转换后失效的部分」。

## 为什么读这个文件

nixi 的确认是在 **Go 工具层**强制的：`confirmed` 参数不出现在 tool schema 里，LLM 无法
伪造。通用 agent 没有这个保证，所以**你必须自己在每次变更前停下来问**。

## 完整矩阵

| 操作 | 确认 | 说明 |
|---|---|---|
| 只读查询 | ❌ | list / inspect / status / logs / 版本 / 端口列表 |
| 分析部署 URL | ❌ | 抓 GitHub repo / docs 页 / docker-compose.yml 并提取配置 |
| 服务 start/stop/restart | ❌ | `systemctl restart nginx` |
| 服务 enable/disable | ❌ | 但要提示：NixOS 管理的服务 rebuild 后会被配置覆盖 |
| 列失败服务 | ❌ | `systemctl --failed` |
| SSH key 增删 | ❌ | 写 `~/.ssh/authorized_keys`，即时生效免 rebuild |
| 用户密码 / 锁定 / 解锁 | ❌ | `passwd` / `usermod -L/-U`，不需要 rebuild |
| 列用户 | ❌ | |
| 更新 channel 本身 | ❌ | `nix-channel --update` 只拉元数据，不改系统 |
| 挂载 / 列挂载 / 列设备 | ❌ | |
| 列 / 状态 / enable / disable timer | ❌ | |
| **装 / 删包** | ✅ | 改 `environment.systemPackages` + rebuild |
| **防火墙开 / 关** | ✅ | 改 `networking.firewall.*` |
| **编辑 NixOS 配置** | ✅ | 任何写 `configuration.nix` / module / flake |
| **rebuild / rollback / reboot** | ✅ | |
| **升级系统** | ✅ | channel update + rebuild，含内核与驱动 |
| **增 / 删 channel** | ✅ | 改变包来源 |
| **增 / 删 flake input** | ✅ | 改变锁文件 |
| **清理 generation** | ✅ | 必须先告知保留几个 |
| **unmount / 持久化挂载** | ✅ | unmount 可能影响正在运行的服务 |
| **增删改组、改 shell** | ✅ | 改 `users.users.<n>.extraGroups` / `shell` |
| **NVIDIA 驱动 enable/disable/configure** | ✅ | 且必须提示需要 reboot |
| **AMD GPU 驱动 enable/disable/configure** | ✅ | 且必须提示需要 reboot |
| **部署 / 更新 / 删除容器** | ✅ | 删除默认**保留** `/srv/<name>/` 数据，purge 才删 |
| **建 / 删定时任务** | ✅ | systemd timer |

## 批量操作只确认一次

装 `nginx, redis, git` 三个包：**改一次配置、rebuild 一次、确认一次**。
不要把三个包拆成三次确认。批量删除容器同理：一次列出所有目标，一次确认。

## "yes 并且顺便做 X" 的处理

用户说 "yes，顺便把 redis 也装上"：
- 合并成一个工作流
- **不要二次确认**

## 确认时应该给什么信息

一个好的确认请求包含：
1. **将要变更的具体内容**（配置 diff，不是"我会修改配置"）
2. **影响范围**（要不要 reboot、会不会短暂断服务、动哪些包）
3. **如何撤销**（rollback 到哪个 generation）

坏例子：*"我需要重建系统，可以吗？"*
好例子：
```
将要变更：
  + environment.systemPackages = [ pkgs.nginx pkgs.redis ]
影响：nginx 会监听 80 端口（防火墙已放行）；需要 rebuild，预计 30s-2min
撤销：nixos-rebuild switch --rollback
继续？
```
