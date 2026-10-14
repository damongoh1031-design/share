---
name: windows-longrun-ai-service
description: 在 Windows 11 上把自托管 AI/Web 服务（Open WebUI、Ollama、ComfyUI 等）做成常年常驻、可无人值守、并可通过 Tailscale 异地访问的服务时，用于方案选型与落地检查。当用户问「XX 桌面版和容器版哪个稳定」「怎么让服务开机自启/崩溃自愈」「怎么用 Tailscale 访问自建服务」「Windows 上怎么 7×24 跑」时使用。
agent_created: true
---

# Windows 11 长期常驻 AI/Web 服务：选型与落地清单

## 一、判定顺序（不要搞反）

**无人值守自愈能力 > 稳定性 > 隔离性 > 安装便利**

关键分水岭：**服务是否需要"有人登录"才能起来？**
- Windows 服务（NSSM/WinSW/`sc`）→ ✅ 不需要登录
- 任务计划程序「系统启动时」+「不管用户是否登录都要运行」→ ✅ 不需要登录
- 「登录时自启」/ 启动文件夹 / 桌面应用自启 → ❌ **需要用户登录**（重启停在登录界面即失效）

## 二、三档方案模板

| 档位 | 做法 | 自启 | 崩溃自愈 | 隔离 |
|---|---|---|---|---|
| 最省心 | 原生运行时 + **NSSM** 注册服务 | ✅ SERVICE_AUTO_START | ✅ `AppExit=Restart` | ❌ |
| 最干净 | **WSL2 发行版 + Docker Engine**，`--restart unless-stopped` | ✅ | ✅ Docker 策略 | ✅ |
| 折中 | **wslc**（WSL 容器） | ❌ 需自建任务计划 | ❌ 无 restart policy，需看门狗 | ✅ |

NSSM 必备三连（很多教程漏掉）：
```bat
nssm set <Svc> AppExit Default Restart
nssm set <Svc> AppRestartDelay 5000
nssm set <Svc> AppThrottle 5000
```

## 三、wslc（WSL 容器）专属要点

**容器 → 宿主机：用 `host.wslc.internal`**（wslc 版的 `host.docker.internal`，但更强）。

- 来源：`%LOCALAPPDATA%\wslc\settings.yaml` 的 `session.hostLoopback`（默认 `host.wslc.internal`）。
- **实测（2026-10-02）**：宿主机服务**仅绑 `127.0.0.1`** 时，容器经该名字**仍能访问**（解析到 `169.254.73.254`）。
  而 `172.x.x.1`（vEthernet WSL）、宿主局域网 IP、`127.0.0.1`、`host.docker.internal` **全部失败**。
- 因此：宿主机服务**不必绑 0.0.0.0**、**不必加防火墙规则**、**地址不会漂移**。

**`settings.yaml` 必调项**：

| 项 | 默认 | 注意 |
|---|---|---|
| `session.idleTimeout` | **30 秒** | 空闲即拆 VM；容器一停，30 秒后 VM 没了 |
| `session.memorySize` | 可用内存一半 | 桌面机务必显式限制 |
| `session.defaultBindingAddress` | `127.0.0.1` | 发布端口默认只绑回环 |
| `session.storagePath` | `%LOCALAPPDATA%` | VHD 默认在 C 盘 |

**容器 ↔ 容器：用自定义网络 + 容器名即可**（实测可用）。
`wslc network create <net>` → 各容器 `--network <net>`（可加 `--network-alias`）→ 同网络内直接 `http://<容器名>:<port>`。
内嵌 DNS 在 `127.0.0.11`，实测 `nslookup <容器名>` 与 `<别名>` 均能解析。
⚠️ 但**只在默认网络上的容器** DNS 是宿主机所在网段的路由器（consomme 模式），解析不了容器名；多网络并存时的 DNS 合并行为**未验证**。

**可用参数（实测 `wslc run --help`）**：`--shm-size`（Playwright 必需）、`--health-cmd`、`--cpus`、`--memory`、`--gpus`、`--mount`、`--ip`、`--network-alias`。
**没有 `--restart`** —— 无重启策略，必须外部补。

**端口写法**：用 `-p 127.0.0.1:PORT:PORT`，**绝不写 `-p 0.0.0.0:...`**（会建通配监听器，踩 WSL #41691：握手成功但转发 0 字节）。

**wslc 无 restart policy / 无官方开机自启** → 任务计划程序「系统启动时」+「不管用户是否登录都要运行」+ 看门狗（探活失败则 `wslc system session terminate` 后重建容器）。

## 四、Tailscale 侧的两个必修项（Windows 独有，极易漏）

1. **Run unattended**：托盘图标 → Preferences → Run unattended。
   Windows 版 Tailscale **默认跑在用户登录会话内**，注销或重启后**断开直到有人登录**。（Linux 默认是 system daemon，macOS 不支持，只有 Windows 需要这个开关。）
   验证：注销后从别的设备 `tailscale ping <host>`；不通就查 `services.msc` 里 Tailscale 服务是否为「自动」+「正在运行」。
2. **Disable key expiry**：admin console → Machines → ⋯ → Disable key expiry。
   默认 **180 天**节点密钥过期需交互重新认证 —— 常驻设备必关。

## 五、`tailscale serve` 的硬约束

- **反向代理目标只支持 `http://127.0.0.1`** → 后端服务**只需绑 loopback**，这同时是安全最佳实践（避免绕过 trusted header 认证）。
- **必须加 `--bg`**，否则重启或 `tailscale down/up` 后 Serve 不会自动恢复。
- Windows 上：端口转发**不需要**管理员终端；serve 文件/目录**需要**。
- `tailscale funnel` = 暴露到公网，默认不要开。
- 开 SSO（`WEBUI_AUTH_TRUSTED_EMAIL_HEADER=Tailscale-User-Login`）时必须配 ACL 只放行 443，否则可直连绕过认证。

## 六、Windows 11 电源与网络坑（每次都要检查）

```powershell
powercfg /change standby-timeout-ac 0   # 接电源永不睡眠
powercfg -h off                         # 关休眠
```
- 关闭**快速启动**（控制面板 → 电源选项 → 选择电源按钮的功能）。
- **WSL 2.6.0+ 空闲回收**：约 1 分钟无交互即关停整个 WSL VM → 常驻服务必须保活
  （`wsl --exec dbus-launch true`，或 WSL 内 `nohup sleep infinity &`，或把 WSL 本身用 NSSM 注册成服务）。
  `.wslconfig` 的 `vmIdleTimeout=-1` **不可靠**，别单独依赖。
- **WSL mirrored 网络模式**与容器端口转发有冲突史，必要时 `.wslconfig` 切 `networkingMode=nat`。
- 服务只绑 loopback 时**不需要**开防火墙入站规则。

## 七、调研方法学（重要）

1. **子代理摘要一律回源核实**。实测中并行子代理给出的结论曾与源码相反；另一批子代理则贡献了主代理漏掉的关键 open bug。
2. 核实优先用 `WebFetch` 抓 **GitHub raw 源码**（`raw.githubusercontent.com/<owner>/<repo>/main/<path>`），比二手博客可靠得多。
3. 查项目"是否还活着"看三处：**最后提交日期**、**release 列表**、**issue 里的"是否废弃"帖是否有维护者回复**。
4. 查"能不能长期跑"必查 GitHub issue 搜索：`restart policy`、`port forwarding`、`autostart`、`idle`。
5. 并行子代理**每批 3 个**，超过会触发 429。

## 八、常见误判（踩过的）

- ❌ "桌面应用关窗就停服" —— 不一定，先查有没有 `runInBackground` / 托盘设置。
- ❌ "有开机自启 = 无人值守" —— 要区分**登录时自启**和**系统服务**。
- ❌ "GA 了就稳了" —— GA 早期常带一批开放 bug，必须去 issue 里翻。
- ❌ "容器版一定比原生稳" —— 若容器方案缺 restart policy / 自启，反而不如 NSSM 服务。
