# 确认矩阵（合并版）

v1 继承自 nixi 的 `docs/security.md`；v2 加了 **"走哪个工具"** 列，并把 `nix-agent`
的 `validate` / `degraded` / `rollback_generation` 语义接进来。

## 怎么用

拿不准某个操作要不要等用户确认时查这张表。**"要确认"= 先出 diff / 计划，等用户明确 yes。**

**一次确认管一个工作流。** 用户说 "yes 并且顺便把 X 也做了" 时，合并成一次确认，
不要为每一小步二次确认。

## 矩阵

| 操作类型 | 确认？ | 走哪个工具 / 命令 |
|---|---|---|
| 只读（list / inspect / status / logs） | ❌ | 直接跑 |
| "这个 option 现在是什么值" | ❌ | `eval_config(attr)` |
| "这个 option 在哪配的" | ❌ | `locate_option(attr)` |
| "这个包在不在 / option 叫什么" | ❌ | `nixos-query`（`mcp-nixos`） |
| 启动 / 停止 / 重启服务或容器 | ❌ | `systemctl restart <unit>` |
| 分析一个部署 URL | ❌ | 抓 repo / docs / compose（只读） |
| 列挂载 / 列设备 | ❌ | `mount` / `lsblk` |
| 列 / 状态 / enable / disable timer | ❌ | `systemctl list-timers` |
| 服务 enable / disable | ❌ | `systemctl enable/disable`（提示 rebuild 后可能被覆盖） |
| 列失败服务 | ❌ | 或读 `summary.health` |
| SSH key / 密码 / 锁定 / 解锁 / 列用户 | ❌ | 写 `authorized_keys` / `passwd` / `usermod` |
| NVIDIA / AMD GPU 状态、利用率 | ❌ | `nvidia-smi` / `rocm-smi` / sysfs |
| 更新 channel（`nix-channel --update` 本身，只拉元数据） | ❌ | 不改系统 |
| **`diff()` 预览** | ❌ | 预览是只读的 |
| **`check("lint")` / `check("dry-build")`** | ❌ | 不激活 |
| **`build()`** | ❌ | 构建不改系统状态 |
| 编辑 NixOS 配置（改 `.nix` 文件） | ✅ | 原生 Edit/Write + 出 diff |
| 装 / 删包 | ✅ | 改 `environment.systemPackages` → `check("dry-build")` |
| rebuild / 改配置生效 | ✅ | `check("dry-activate")` → `diff()` → `switch()` |
| **`switch(validate=True)`** | ✅ | 等于"dry-build + 激活" |
| rollback | ✅ | `generations(action="rollback", generation=<id>)` |
| reboot | ✅ | 且提示内核/驱动类变更 |
| 防火墙开 / 关 | ✅ | 改 `networking.firewall.allowedTCPPorts` |
| 防火墙 list | ❌ | |
| 升级系统 | ✅ | 见 `rebuild-and-generations.md` |
| 增 / 删 channel 或 flake input | ✅ | 展示锁文件 diff |
| 清理 generation | ✅ | **必须告知保留几个** |
| **`check("dry-activate")`** | ⚠️ | 用 sudo 但不激活 —— **第一次用先说明它会碰 sudo** |
| unmount / 持久化挂载 | ✅ | |
| 增删用户、改组、改 shell | ✅ | |
| 部署 / 更新 / 删除容器 | ✅ | 数据默认保留在 `/srv/<name>/` |
| 启用 / 禁用 / 配置 NVIDIA 驱动 | ✅ | **提示需 reboot 才加载内核模块** |
| 启用 / 禁用 / 配置 AMD GPU 驱动 | ✅ | 同上 |
| 建 / 删定时任务 | ✅ | systemd timer |
| 删除任何系统路径 | ✅ | **只允许 `/srv/<container>/`** |

## 三条容易搞错的分界

### 1. `check("dry-activate")` 是灰色地带

它**用 sudo**（`sudo -n nixos-rebuild dry-activate`），但**不激活系统**。
在 `nix-agent` 的 sudoers 白名单里它和 `switch` 同级授权。

**处理方式**：默认当只读（❌ 确认），但**第一次使用时明确告诉用户它会调用 sudo**。
如果用户对"AI 碰 sudo"敏感，把它也列为 ✅。

### 2. `switch(validate=True)` 不是"更安全的 switch"，是"两步合一"

它先跑 `check("dry-build")`，不过就**不激活**（返回 `preflight_failed`）。
它**仍然是激活操作**，仍然要确认。别因为名字里有 validate 就当成 dry-run。

### 3. `degraded` 之后的回滚要不要再确认？

**不要。** `degraded` 表示"激活成功但有 unit 新失败"，而回滚是**回到上一个已知可用的
generation** —— 这是恢复动作，不是新变更。

处理方式：**立即回滚，然后在报告里说明做了什么、为什么。** 除非用户明确说
"先别动，我要看那些失败的服务"。

## 用户说了"只看看"之后

如果用户说过 "只看看 / 先别动 / 只出个计划"，**直到他说 yes 之前不要调 `switch()`**。
`diff()` 就是 preview，用它回答。

反过来，**没说过 "只看看" 时默认是 apply**：`diff()` 之后直接 `switch()`，不要为
"要不要执行"再问一次。这是 `nix-agent` 的文档化默认（高信任）。

> 如果你的部署不希望这个默认，改宿主配置：把 `switch` / `generations` 从 MCP 工具的
> 允许列表里去掉，或给服务器设 `trust: untrusted`。见 `hermes/mcp-servers.snippet.yaml`。
