---
id: hermes-agent-zeabur-vps-deployment
title: Hermes Agent 部署到 Zeabur（ZeaburOS / K3s）的配置清单与聊天平台选型
tags:
  - hermes-agent
  - zeabur
  - zeaburos
  - k3s
  - self-hosting
  - vps
  - messaging-gateway
created: 2026-10-15
updated: 2026-10-15
version: 1.0.0
status: stable
source: 本机 Hermes Agent 源码（C:\Users\Admin\AppData\Local\hermes\hermes-agent）+ Zeabur 官方文档（zeabur.com/docs）+ Web 检索
confidence: 已核实
---

## TL;DR

ZeaburOS 就是 K3s（轻量 Kubernetes）。在 ZeaburOS 上部署 Hermes Agent **不能照搬仓库里的 `docker-compose.yml`**（`network_mode: host` 在 K8s 中无效）。正确做法：在 Zeabur 面板里把 Hermes 当作「自定义 Docker 镜像服务」部署，配 5 项——镜像、持久卷 `/opt/data`、端口 9119/8642、环境变量、启动命令 `gateway run`。

---

## 一、ZeaburOS 是什么（决定部署路径）

| 项 | 事实 |
|---|---|
| 本质 | K3s（轻量 Kubernetes）+ Zeabur 系统组件（部署代理、监控） |
| 曾用名 | 控制台中原本显示为「K3s」，2026 年起更名 ZeaburOS |
| 作用 | 把服务器变成 Zeabur 的**部署节点**，日常通过 Dashboard 管理，无需 SSH |
| 持久存储落盘位置 | `/var/lib/rancher/k3s/storage` |
| systemd 服务名 | `k3s`（未改名） |
| 替代选项 | 标准发行版 Ubuntu 24.04 LTS（Zeabur 不提供技术支持，需完全自管） |
| 双向切换 | 只能靠**重装**，两个方向都会清空磁盘 |
| 支持范围 | Zeabur 仅对 ZeaburOS 提供技术支持；自行安装的面板（1Panel、宝塔）不在支持范围 |

**两条获得服务器的路径**（都会得到 K3s 节点）：

1. **从 Zeabur 购买** — 供应商含 AWS / GCP / Hetzner / Linode / DigitalOcean / Aliyun / Tencent Cloud / Volcengine。购买时选 ZeaburOS 或 Ubuntu 24.04。按月固定费率，Zeabur 全权托管（操作系统更新、基础设施维护都不用管）。
2. **注册自有服务器（BYOH）** — 前置条件：
   - 至少一个公网可达 IP
   - ≥1 CPU 核心、≥2 GB 内存
   - 开放端口 `22`、`80`、`443`、`4222`、`6443`、`30000-32767`
   - 允许 root SSH 登录；非 root 用户所在 sudo 组需带 `NOPASSWD`
   - SSH 密钥必须是 **OpenSSH 格式**（`-----BEGIN OPENSSH PRIVATE KEY-----`）。腾讯云默认的 RSA PEM（`-----BEGIN RSA PRIVATE KEY-----`）会连不上，需转换：`ssh-keygen -p -N "" -f /path/to/key`

---

## 二、要设置的 5 项

### 1. 镜像

路径：`Add Service` → `Docker Images` → `Image`

```
nousresearch/hermes-agent:latest
```

镜像 tag 语义：`latest` / `stable` = 稳定发布门禁通过的镜像；`main` = 开发分支镜像；`X.Y.Z` = 版本化稳定镜像。生产建议锁 digest。

镜像内 Python 环境跟随 `pyproject.toml` / `uv.lock`（当前 Python 3.14），**不含** Electron 桌面应用。

### 2. 持久卷（最关键）

路径：服务页 → `硬盘` 标签 → `Mount Volumes`

| 字段 | 值 |
|---|---|
| Volume ID | `hermes-data` |
| Mount Directory | `/opt/data` |

Hermes 把**全部用户数据**（config、API keys、sessions、skills、memories）放在这一个目录。镜像本身是无状态的，所以升级只需拉新镜像，配置不丢。

坑：
- 挂载后该目录**原内容会被清空**
- Volume **仅属于单个服务**，不能跨服务共享；想共享数据要用 MinIO / RustFS 这类对象存储
- 启用 Volume 后服务**失去零停机重启**（先完全关闭再启动，有短暂中断）
- 删除 Volume 即数据永久清空

### 3. 端口

路径：服务页 → `网络` / `Ports`

| Port Name | Port | Port Type | 用途 |
|---|---|---|---|
| `web` | `9119` | HTTP | Web Dashboard |
| `api` | `8642` | HTTP | Gateway 的 OpenAI 兼容 API + health |

- HTTP 类型可用 `xxx.zeabur.app` 域名直连，Zeabur **自动签发 TLS 证书**
- 生成域名：服务页 → 域名区块 → 「生成域名」；也支持自定义域名（需自己加 DNS CNAME 记录；用 Cloudflare 时 SSL/TLS 模式**不能选 Full (Strict)**）
- 服务间通信走私有网络：`<service>.zeabur.internal:<port>`

### 4. 环境变量

路径：服务页 → `Environment Variable`

**Dashboard 必需（公网暴露时不可省）：**

```env
HERMES_DASHBOARD=1
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=<用户名>
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=<强密码>
HERMES_DASHBOARD_BASIC_AUTH_SECRET=<openssl rand -hex 32>
```

**为什么必须设**：Dashboard 里存着所有 API key。2026 年 6 月的安全加固后，绑定非 loopback 地址时**强制要求**注册一个 `DashboardAuthProvider`，旧的 `HERMES_DASHBOARD_INSECURE` 已失效。三种 provider 可选：

| Provider | 触发条件 | 适用 |
|---|---|---|
| 用户名/密码 | 设 `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` + `_PASSWORD` | 可信网络 / VPN 后；**不适合直接暴露公网** |
| OAuth (Nous Portal) | 设 `HERMES_DASHBOARD_OAUTH_CLIENT_ID` | 公开托管 |
| 自托管 OIDC | 设 `HERMES_DASHBOARD_OIDC_ISSUER` + `_CLIENT_ID` | 接入自有 IdP |

**要用 OpenAI 兼容 API 时再加：**

```env
API_SERVER_ENABLED=true
API_SERVER_HOST=0.0.0.0
API_SERVER_KEY=<openssl rand -hex 32>   # 至少 8 字符，强制
API_SERVER_CORS_ORIGINS=*
```

**聊天平台密钥**（`TELEGRAM_BOT_TOKEN` 等）同样填在这里。

**注意**：官方 `docker-compose.yml` 里的 `HERMES_UID` / `HERMES_GID` 是给裸机 Docker 用的，不要照抄到 Zeabur。

### 5. 启动命令

| 项 | 值 |
|---|---|
| Command | `gateway run` |
| Entrypoint | **不要动** |

Zeabur GUI 从界面创建的 Start Command 默认 Command 是 `/bin/sh`，需要改用 Edit TOML 修改。

**为什么不能动 entrypoint**：镜像默认 `ENTRYPOINT ["/init", "/opt/hermes/docker/main-wrapper.sh"]`，`/init` 是 s6-overlay 的 PID 1，负责跑 `cont-init.d`（chown、profile reconcile、dashboard 开关）并建立 supervision 树。绕过它 gateway 无法正常工作。

**s6 托管语义**：官方 s6 镜像里 `gateway run` 被 s6-overlay 自动托管，崩溃后数秒内重启且不丢容器；`gateway run` 的 CMD 进程本身只是个 `sleep infinity` 心跳。可用 `--no-supervise` 或 `HERMES_GATEWAY_NO_SUPERVISE=1` 退回旧语义（仅适合 CI）。

### 首次初始化

服务页的 Web Terminal 里跑一次：

```sh
hermes setup
```

向导把配置写进已挂载的 `/opt/data/.env`，重启不丢。也可以跳过向导直接填环境变量。

---

## 三、资源规格建议

| 项 | 值 | 依据 |
|---|---|---|
| 内存 | **≥4 GB** | ZeaburOS 是 K3s，默认给 Kubernetes 预留 500m CPU / 512Mi，System Reserved 再预留 500m / 512Mi。2 GB 机器实际只剩约 1 GB 给 Hermes |
| 磁盘 | ≥20 GB | 镜像内含 Python 3.14 + Node + venv |
| 注册自有服务器硬门槛 | ≥1 核 / ≥2 GB | Zeabur 官方前置条件 |

资源预留可调：`Settings` → `Advanced Settings` → `Resource Reservation`，分 Kubernetes Reserved 与 System Reserved 两类。建议保留默认值。

**OOM 恢复**：服务器内存不足时 K3s 状态灯变红、服务不可访问。`Settings` → `Reboot Server` → **Deselect All** → Reboot（约 3–5 分钟）。避免重启后立刻再次 OOM。

---

## 四、聊天平台选型（35 个适配器）

Hermes 的 messaging gateway 是**单进程连所有平台**，在 VPS 上最关键的区分是**要不要公网回调**。

### A. 主动出站（不需要公网域名，最省事）

| 平台 | 连接方式 | 备注 |
|---|---|---|
| Telegram | 长轮询 | Dashboard/桌面端有 `Create with QR` 按钮，扫码自动建 bot 并写入 `TELEGRAM_BOT_TOKEN` |
| 飞书 / Lark | `websocket`（推荐）或 `webhook` | websocket 模式由 Hermes 主动出站，无需公网 webhook |
| 钉钉 | Stream 模式（长连接 WebSocket） | 无需公网 URL；回复走 session webhook API，markdown 格式 |
| 企业微信 WeCom | AI Bot WebSocket 网关 | 实时双向，无需公网端点 |
| Slack | Socket Mode（`slack-bolt`） | 经典 App（RTM API）2025 年 3 月已完全弃用 |
| Discord | Gateway WebSocket | 需 `DISCORD_FREE_RESPONSE_CHANNELS` 才能免 @ |
| QQ | 官方 Bot API v2，WebSocket | 需在 q.qq.com 注册应用并开启 C2C / 群 @ / 频道 intents |
| 微信个人号 | iLink Bot API，长轮询 | ⚠️ 见下方坑 |
| Matrix / Mattermost / IRC / Simplex / Relay | 各有长连接或轮询 | — |

### B. 需要公网 HTTPS 回调

WhatsApp Cloud API、LINE、Microsoft Teams、Google Chat、SMS、通用 Webhooks、WeCom Callback、MS Graph webhook、teams-meetings。

Zeabur 生成的 `xxx.zeabur.app` 域名 + 自动 TLS 即可满足回调需求。

### C. 其它入口

> 补充：把 Hermes 当 OpenAI 兼容后端接 Open WebUI / LibreChat / LobeChat 等前端，见 [hermes-agent-openwebui-knowledge-integration.md](./hermes-agent-openwebui-knowledge-integration.md)。

- 内置 TUI（`hermes` 命令）
- Web Dashboard（`:9119`）
- OpenAI 兼容 API（`:8642`）→ 可接 Open WebUI、LibreChat 等任意前端
- Email、ntfy、Home Assistant、BlueBubbles（iMessage）、A2A、Photon、Buzz、Raft、Yuanbao

### 中文用户推荐

1. **Telegram** — 最省事，扫码自动建 bot，纯长轮询无需公网
2. **飞书 / Lark** — websocket 模式，企业内最好用
3. **钉钉** — Stream 模式，同样免公网

---

## 五、坑与反直觉

1. **`docker-compose.yml` 在 ZeaburOS 上不可用** — 它用 `network_mode: host`，K8s 不支持。
2. **别在浏览器 VPS 控制台粘贴安装命令** — 官方明确警告：某些控制台（Hetzner Cloud 等）会错误传输特殊字符，`:` 可能变成 `;`、`@` 可能被错误渲染，导致 `-v`、`-e` 参数和 API key 静默损坏。用 SSH 连接。
3. **微信个人号群聊基本不可用** — 扫码连的是 **iLink bot 身份**（如 `a5ace6fd482e@im.bot`），不是普通个人微信号。后果：iLink bot 一般**无法被拉进普通微信群**；iLink 通常**不下发普通微信群的群事件**；`WEIXIN_GROUP_POLICY` / `WEIXIN_GROUP_ALLOWED_USERS` 只有在 iLink 真的返回群事件时才生效。个人私聊可用。要企业场景用 WeCom；要普通微信群得靠社区方案（HermesClaw，可在同一微信号上跑 Hermes + OpenClaw）。
4. **Dashboard 认证是强制的** — 非 loopback 绑定 + 注册了 auth provider 才启动认证门。老的 `HERMES_DASHBOARD_INSECURE` 已是 no-op。
5. **Volume 与零停机重启互斥** — 挂 Volume 后每次重启都会先关后起。
6. **arm64 镜像会部署失败** — 在 Apple Silicon 本地构建的镜像默认 `linux/arm64`，Zeabur 服务器是 `linux/amd64`，会报 `no match for platform in manifest`。构建时加 `--platform linux/amd64`。官方 `nousresearch/hermes-agent` 镜像有 amd64/arm64 双架构，无此问题。
7. **Zeabur 防火墙只管入站** — 采用白名单策略（默认封锁）。必要端口 `22`、`80`、`443`、`4222`、`6443`、`30000-32767` 不可封锁，否则服务器会失去 Zeabur 管理。
8. **想在 ZeaburOS 上跑别的 Docker Compose** — 可 `sudo systemctl disable --now k3s containerd`，但 Zeabur 上已部署的服务会一起停止，且无法再从控制台创建项目。重新启用：`sudo systemctl enable --now k3s containerd`。彻底卸载：`/usr/local/bin/k3s-uninstall.sh`。
9. **服务器过期宽限期因供应商而异** — AWS Lightsail / GCP / Hetzner / Linode / DigitalOcean：到期后 1 天关机、5 天最后通知、7 天删除；Tencent Cloud / Aliyun / Volcengine：到期即关机、约 15 天后删除。

---

## 六、可复用操作

### 裸机 Docker 快速验证（不经过 Zeabur，用于确认镜像可用）

```sh
mkdir -p ~/.hermes
docker run -it --rm -v ~/.hermes:/opt/data nousresearch/hermes-agent setup
```

```sh
docker run -d --name hermes --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 -p 9119:9119 \
  -e HERMES_DASHBOARD=1 \
  -e HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin \
  -e HERMES_DASHBOARD_BASIC_AUTH_PASSWORD="$(openssl rand -hex 16)" \
  -e HERMES_DASHBOARD_BASIC_AUTH_SECRET="$(openssl rand -hex 32)" \
  nousresearch/hermes-agent gateway run
```

### 生成密钥

```sh
openssl rand -hex 32
```

### Zeabur 服务器 SSH / K3s 维护

```sh
# 禁用 Zeabur 服务（腾出机器跑别的）
sudo systemctl disable --now k3s containerd
# 重新启用
sudo systemctl enable --now k3s containerd
# 清理未使用的镜像
sudo k3s crictl rmi --prune
# 改 DNS nameserver
sudo vi /etc/resolv.kubelet.conf && sudo systemctl restart k3s
```

### 进入服务容器 Shell（在服务器 SSH 内）

```sh
kubectl get pods -n <Namespace>
kubectl exec -it <Pod 名称> -n <Namespace> -- /bin/sh
```

PVC 命名格式 `<volume-id>-service-<service-id>`，Namespace 为 `environment-<environment-id>`。

---

## 七、未核实 / 存疑

- Zeabur 服务器各档位的**具体月费数字**未逐一核实（官方文档只给了订阅方案：Free $0 / Dev $5 / Pro $19 / Team $79 含 3 席位；服务器为固定月费、按方案定价，需在 zeabur.com/pricing 或购买页实时查看）。
- 未实测在 ZeaburOS 上跑 Hermes 全流程（本次为文档 + 源码核实，非实机验证）。
- Zeabur 服务页 Web Terminal 是否能正常交互跑 `hermes setup` 向导未实测；若 TTY 不支持，退路是直接填环境变量。
- Hermes 是否完整读取进程环境变量（而不仅是 `/opt/data/.env`）未逐行核实源码；本机部署走的是 `.env` 路径。
