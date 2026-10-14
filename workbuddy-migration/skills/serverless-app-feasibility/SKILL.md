---
name: serverless-app-feasibility
description: 评估「某软件能否在 serverless / PaaS 平台零成本部署，且数据与登录态不丢」。当用户问「XX 软件能不能跑在 Vercel / Cloudflare / HF Spaces / Render / Koyeb / Cloud Run 上」「免绑卡免费额度」「会不会丢数据」时使用。提供三问判断法、免卡三档分类、平台规格库与成本口径。
agent_created: true
---

# Serverless / PaaS 部署可行性评估

## 核心结论（先背这三条）

1. **容器磁盘不持久是所有 serverless 平台的共性**，不是某一家的问题——是模型决定的。真持久只有两条路：**真 VM**（Oracle ARM / VPS）或**外置托管数据库**。
2. **判断分界线是「状态」，不是语言。** 常驻进程 + 本地文件写入 = 别用 serverless。
3. **「免卡」厂商官网基本不写**，必须靠第三方实测文章交叉验证。分三档：免卡（邮箱/手机/实名）· 需卡验证（$1 预授权会退）· 需卡计费（超额直接扣款）。

## 三问判断法（评估任何「软件 × 平台」组合）

| # | 问题 | 结论 |
|---|------|------|
| ① | 这软件是常驻还是有状态？ | 常驻 + 有状态 → 排除纯 serverless（Workers / Lambda / Vercel Functions） |
| ② | 它把数据写在哪？ | 写本地文件（SQLite / 向量库 / 上传目录）→ 要么外置，要么换平台 |
| ③ | 磁盘持久吗？ | 不持久 → 数据必须外置，或改真 VM |

## 必须外置的四类状态

1. **登录态签名密钥** → 放平台 Secrets（跨 rebuild/重新部署保留），**生成一次永不更换**。换了 = 所有人被登出 + token 解密报错。
2. **主数据库** → 外置托管 Postgres / Mongo。
3. **向量库** → 外置 pgvector 或换外部向量服务。
4. **上传文件** → S3 兼容对象存储。

## 常用软件的密钥与数据变量

| 软件 | 登录态密钥 | 数据外置变量 |
|------|-----------|-------------|
| Open WebUI | `WEBUI_SECRET_KEY` | `DATABASE_URL`、`VECTOR_DB=pgvector`、`PGVECTOR_DB_URL`、`STORAGE_PROVIDER=s3` + `S3_*` |
| LibreChat | `JWT_SECRET`、`JWT_REFRESH_SECRET`、`CREDS_KEY`、`CREDS_IV` | `MONGO_URI` |
| AnythingLLM | `JWT_SECRET`、`SIG_KEY`、`SIG_SALT` | **必须用 `mintplexlabs/anythingllm:pg` 镜像**（不是默认镜像）+ `DATABASE_URL` |

> AnythingLLM 官方仓库的 HF Dockerfile 注释仍写「用 Persistent Storage」——**已过时**，HF 的 Persistent Storage 已废弃，改为 Storage Buckets（S3 对象存储语义），不能挂 SQLite。

## 平台规格库（2026-09 核查）

| 平台 | 免费规格 | 磁盘持久 | 卡 | 月成本 | 能跑重型软件 |
|------|---------|---------|----|-------|------------|
| HF Spaces | **⚠️ 2026 起免费档已不能创建 Docker/Gradio Space（需 PRO $9/月）**。免费档只剩 Static Space + 最多 2 个 ZeroGPU Gradio Space。CPU Basic 规格 2 vCPU / 16 GB / 50 GB，容器必须监听 **7860** | 容器 ephemeral | 免卡 | **$0 已不可用**，需 $9/月 | ❌ 免费档跑不了（自定义域名同样需 PRO） |
| Oracle Always Free ARM | **2 OCPU / 12 GB** / 200 GB / 10 TB | ✅ 真 VM | 需实体外币卡 | $0 永久 | ✅。**2026-08-18 从 4 核 24 GB 砍半，超限实例自动终止；租户级池子；PAYG 账户仍保留 4/24** |
| Cloud Run | 180,000 vCPU-秒 + 360,000 GiB-秒 + 200 万请求，**仅按请求计费模式** | 无持久盘（`/tmp` 是 tmpfs 计入内存） | 需卡计费 | $0 起 | ⚠️ **额度只够约 7% 的常驻需求**（1vCPU/1GB 常驻一月 = 2,592,000 vCPU-秒，是免费额度的 14 倍）。只适合按请求伸缩 |
| Koyeb | 512 MB / 0.1 vCPU | 需外挂 DB | **需卡（$29 预授权冻结）** | 转 $29/月 Pro | ❌ **免费档对新用户实际已关闭**，且 512 MB 不够 |
| Northflank | **2 服务 + 1 DB + 2 cron，always-on 不休眠**；DB 类型含 **MongoDB** | 含 1 个托管 DB | **需卡**（多源确认） | $0 | ✅ **结构上与「1 Web + 1 MongoDB」严丝合缝**，是免卡外的首选。但免费服务 CPU/RAM 官方未公开，主定价页已不显式列出该档 |
| VPS（RackNerd 等） | 1核1G/20G/3TB **$21.99/年**；2核2G/35G **$35.99/年**；3核4G/60G **$59.99/年**（2026-09 实价，续费同价） | ✅ 真持久 | 需支付 | $1.83–5.00 | ✅。**1 GB 跑不动 Open WebUI，起点 2 GB**。ctrl 面板内置 LibreChat/Ollama/AnythingLLM 一键部署，支持支付宝 |
| Zeabur | **免费共享集群已取消**；Free 档只剩「托管你自己买的服务器」。Dev $5/月、Pro $19/月各有 14 天试用 | 需外挂 DB | 免卡 | $0 已不可用 | ❌ 免费档已无共享算力 |
| Vercel Hobby | 360 GB-hrs / 4 活跃 CPU-hrs，**已支持 Docker（VCR）** | ❌ 无持久文件系统 | 免卡 | $0（禁商用） | ❌ 函数最长 **300 秒**、空闲 5 分钟缩容，模型不适配常驻服务 |
| Cloudflare Containers | standard-1：1/2 vCPU / 4 GiB | ❌ 每次停止重置 | 需 $5/月 | $31+ | 不推荐 |
| Fly.io | **免费额度 2024-10-07 已取消**；试用仅 2 机器小时 / 7 天 | 付费后可用卷 | 需卡 | 转付费 | ❌ |
| **GitHub Codespaces** | **120 hrs + 15 GB-month / 月**（2 核每小时扣 2 → 实际约 60 小时）；2 核 / **8 GB** | ✅ 卷持久（停后留 30 天） | **免卡**（额度用完直接封禁不扣费） | $0 | ✅ **支持 DinD + compose v2**，端口可设 Public 得公网 URL。但空闲 30 分钟（最长 4h）即停 → 只能临时 |
| **Sealos** | 7 天免费试用 **4 vCPU / 4 GB** | 需外挂 | **免卡**（官网明写） | 试用后 $7/月起 | ✅ 有官方 LibreChat 零参数模板 |
| CodeSandbox | 40 小时/月，4 vCPU / 8GB | ❌ 临时 | 免卡 | $0 | ⚠️ Devbox 支持 compose，但环境会挂起 |
| Railway | Free 档 **$1 额度/月不结转 + 0.5 GB RAM/服务**（跑不动）；Trial **$5 一次性 / 30 天 / 1 GB RAM** | 试用卷 30 天后删 | 免卡 | $0 不可用 | ❌。**另有 `ssh railway.new`：免账号免卡领 2 vCPU/2GB 免费 VM，24h 认领窗口，每 IP 每天 3 台** |

## 自定义域名支持矩阵（决定选型的关键字段）

| 平台 | 免费档能否绑自定义域名 |
|------|---------------------|
| VPS / Oracle ARM / Cloud Run / Vercel / Koyeb / Northflank / Cloudflare | ✅ 支持 |
| **HF Spaces** | ❌ **不支持，需 PRO $9/月 = $108/年**（官方文档：属于 PRO 或 Team & Enterprise 计划） |

**免费二级域名（2026 仍可用）**：EU.org（最稳，支持自定义 NS + DNSSEC，审核 3–7 工作日）、DigitalPlat dpdns.org（即时、官方支持 CF 托管）、ClouDNS Free Zone（**免费区不支持自定义 NS → 用不了 Cloudflare Tunnel/CDN**）、register.us.kg、DuckDNS。
**便宜顶级域**：.xyz / .top 首年 $1–2、**续费 $5–8/年**。**Cloudflare Registrar 只支持转入、不能新注册**（需原注册满 60 天）。

## 按用量选平台：盈亏平衡点公式

Cloud Run（1 vCPU + 4 GiB，Tier 1）月成本 = **0.0936 × H − 3.96**（H = 计费小时/月，H > 50）

| 对比 VPS | 年付价 | 平衡点 |
|---|---|---|
| RackNerd 1核1G | $21.99 | **61.8 h/月** |
| RackNerd 2核2G | $35.99 | **74.4 h/月** |
| RackNerd 3核4G | $59.99 | **95.7 h/月** |

**结论**：60 h/月 → Cloud Run 省；240 h/月 → VPS 省 73%；**720 h/月（24×7）→ VPS 省 92%（$59.99 vs $761.28）**。
**Cloud Run 的省钱前提是「大部分时间不跑」。一旦常驻，按秒租永远比包年租贵。**

## VPS 落地的标准组合（全免费配件）

RackNerd + EU.org 域名 + Cloudflare 免费套餐（DNS/CDN/Universal SSL）+ **Cloudflare Tunnel**（免费、隐藏真实 IP、不用开 80/443、自动 HTTPS）+ Caddy（自动 Let's Encrypt）+ R2 备份（10 GB 免费）。
关键：容器只绑 `127.0.0.1`，端口不暴露公网；SSH 关闭密码登录。

## Oracle Cloud Always Free 实操要点（成功率决定一切）

**主区域（Home Region）选定不可更改，免费实例只能在主区域创建。**
- 避开（竞争比可达 1:50）：`ap-seoul-1` 首尔、`ap-tokyo-1` 东京、`ap-osaka-1` 大阪、`us-sanjose-1` 圣何塞、`eu-frankfurt-1` 法兰克福
- 推荐：`ap-singapore-1` 新加坡、`ap-mumbai-1` 孟买、`ca-toronto-1` 多伦多、`eu-amsterdam-1` 阿姆斯特丹

**必须升级到 PAYG**：非 PAYG 只有 2 OCPU/12 GB；PAYG 保留 4 OCPU/24 GB，且抢机优先级更高。只要不超额账单仍是 $0 → **升级后立刻设 $1 预算告警**。

**Ampere A1 弹性比例 1 OCPU : 6 GB** → 免费额度内可拆成 1 台 4/24、2 台 2/12、或 4 台 1/6。**先抢 1 OCPU/6 GB（成功率高得多），跑起来再扩容。** x86 微实例 1 GB 跑不动 Open WebUI。

**抢机**：手动刷新几乎没戏，用轮询脚本 `hitrov/oci-arm-host-capacity` 或 `zhengxiongzhao/oracle-arm-freetier`。**必须用指数退避**避免 API 限流封 IP。亚太区资源释放高峰在凌晨 2–4 点。

**降配额需 terminate 而非 stop**（stop 通常不释放 ARM 配额）。

**注册**：实体卡 + 姓名地址与账单完全一致；虚拟卡/预付卡拒绝；失败别用同一身份反复试（进风控）。

## 真 VM vs serverless 的架构差异（选型时最重要的隐性收益）

真 VM + 真持久盘 → **不需要外置数据库、不需要对象存储**。数据放宿主机目录，备份 = tar 一个目录。
serverless 容器磁盘不持久 → 必须外接 Postgres + 对象存储，外部依赖从 1 个变成 4–5 个。

**因此：有实体外币卡 + 能接受轻量运维时，Oracle ARM 不只是最便宜，架构还最简单。**

## 自建硬件（SBC / 迷你主机）评估：2026 年不要买树莓派

**⚠️ 树莓派 5 在 2026 年五个月内三轮涨价**（2025-12-01 / 2026-02-02 / 2026-04-01），原因：AI 基础设施抢 LPDDR4 产能，**一年内 LPDDR4 DRAM 涨 7 倍**。

| 版本 | 上市价 | 2026-04 现价 | 涨幅 |
|---|---|---|---|
| 1 GB | — | **$45** | 0%（豁免） |
| 4 GB | $60 | **$110** | +83% |
| 8 GB | $80 | **$175** | +119% |
| **16 GB** | $120 | **$305** | **+154%** |

价格被保护的型号：1GB Pi4（$35）、1GB Pi5（$45）、Pi Zero 系列、Pi 400（$60）、Pi 3+ 及更早。官方称涨价「暂时性」，成本缓解后取消，**未给时间表 → 不急就等**。
**所有内存档位的 Pi5 硬件规格完全相同，加内存不增加任何硬件能力。**

**该买的硬件是 N100 迷你主机**（2026-08 国内实测）：准系统 480–550 元（**低于 450 有暗病**）+ 16GB DDR4 约 380 元 + 512GB SSD 约 360 元 = **配齐 900–1100 元（约 $125–155）**。待机 5–7W，年电费 16–50 元。优势：x86_64 兼容性完美、原生 M.2 NVMe、常见双 2.5G 网口、自带散热。劣势：单通道内存。

### 为什么 SBC 在 2026 年集体失守（核心机制）

| | SBC | 迷你主机 |
|---|---|---|
| 内存形态 | **板载 LPDDR，焊死** | **标准 DDR4 SODIMM 插槽** |
| 涨价传导 | **100% 到板价，无法规避** | 准系统不含内存，价格稳定 |
| 用户选择权 | 无 | 可等降价 / 买二手 / 换更大 |

结果：**N100 16GB 约 $140 vs 树莓派 5 16GB $305**。

### SBC 型号速查（2026-09）

| 型号 | 规格 | 价格 | 跑 Open WebUI |
|---|---|---|---|
| **Orange Pi 5 Plus** | RK3588, 8–32GB, **原生 PCIe 3.0 x4 NVMe**, 双 2.5G, 6 TOPS | **约 $120 起** | ✅ **SBC 里最优** |
| NanoPi R6C | RK3588S, 8GB, 32–64GB eMMC, 2.5G+千兆 | 约 800–1000 元 | ✅ 偏软路由 |
| Radxa Rock 5B+ | RK3588, 3× M.2, 双 2.5G | 约 $150+ | ✅ |
| Orange Pi 6 Plus | 12核 ARMv9, 45 TOPS | $199 起 | ⚠️ 性能过剩 |
| Banana Pi BPI-M7 | RK3588, 8–32GB, 64–128GB eMMC | 约 1000–2000 元 | ❌ **比 N100 贵，无代差** |
| 树莓派 4 **2GB** | BCM2711 | **$45（未涨）** | ⚠️ 偏紧，需 swap |
| 树莓派 4 8GB | BCM2711 | 约 $125 | ❌ 太贵 |
| 树莓派 5 16GB | BCM2712 | **$305** | ❌ 不要买 |
| 树莓派 Zero 2W | BCM2710A1, 512MB | $15 | ❌ 跑不了 |
| **Jetson Orin Nano Super** | **67 TOPS, 8GB LPDDR5** | **$249** | ✅ **唯一能本地跑模型** |

**树莓派 4 现价（2026-04-01 第三轮涨价后）**：1GB $35 未涨 / **2GB $45 未涨** / **3GB $83.75 新增** / 4GB 约 $80 / 8GB 约 $125。3GB 版是用**库存 1.5GB 颗粒 × 2 拼接**出来的（4GB 单颗价格失控）。**2GB 是唯一没涨的实用档。**

**Jetson Orin Nano Super 实测（2026-07-21，Ollama）**：llama3.2:1b **44.9 tok/s**、gemma2:2b 25.6、qwen2.5:3b 22.6、phi3:mini 3.8B 22.0；峰值 19.2W / 平均 11.4W；结温 61.8°C 无降频；**推理占 4.8/7.6 GB → 8GB 上限是 3–4B 模型，7B/8B 跑不了**。人眼阅读速度 5–8 tok/s，所以 22–45 tok/s 全部够用；N100/树莓派跑 7B 只有 2–3 tok/s。

**⚠️ RISC-V 板子（VisionFive 2 / BPI-F3）目前不要碰**，软件生态不成熟。

**硬件选型最终排序**：Oracle ARM $0 ＞ N100 迷你主机 约 1000 元 ＞ Orange Pi 5 Plus 约 $120 ＞ NanoPi R6C 约 800–1000 元 ＞ 树莓派 4 2GB $45 ＞ Jetson Orin Nano Super $249（仅当确定要本地跑 1–4B 模型）＞ ❌ 树莓派 5、Banana Pi M7、Zero 2W。

**三年 TCO 对比**：Oracle ARM **$0** ＜ N100 整机 约 $155 ＜ Pi5 4GB 全套 约 $159 ＜ Pi5 16GB 全套 **约 $354**。
**结论：买硬件在任何成本口径下都不占优。**

**本地跑 LLM 这条路走不通**：N100 / Pi5 跑 7B Q4 只有 **2–3 tok/s，不可用**；4B 勉强；1.5B 流畅。要舒服跑 7B+ 需 $400–600 硬件（N305 / Ryzen 8845HS）。**正确做法：本地小模型（1.5B–4B）处理隐私敏感轻量任务 + 云端免费 API 处理复杂任务。**

**硬件的真正价值不在省钱**：① 数据主权（不受云厂商政策摆布）② 一机多用（双 2.5G 兼软路由、NVMe 兼 NAS）③ 一次性买断无账单焦虑。
**代价**：① 家宽通常**无公网 IPv4** → 必须 Cloudflare Tunnel ② 断电即停服，要可用得加 UPS（200–400 元）③ 硬件会坏（Pi 的 microSD 是可靠性杀手；N100 常见杂牌内存 + SATA 渣盘）④ 运维全在自己身上。

**推荐路径**：先上云（Oracle ARM $0），用一年再决定是否买硬件。迁移成本几乎为零（同一份 compose + data 目录 scp），且等一年内存涨价可能已缓解。

## 软件选型速查

| 软件 | 内存 | 数据存储 | 备份 | 适用 |
|---|---|---|---|---|
| **Open WebUI** | ~600 MB | SQLite 单文件 `webui.db` + 上传目录 | 复制一个目录 | 通用聊天前端，多模型聚合，多用户权限完善 |
| AnythingLLM | ~1.5 GB | SQLite + LanceDB（两处） | 要备两处 | 文档 RAG 工作区，拖文件就能问 |
| LibreChat | **官方最低 1 GiB / 1 vCPU，实用下限 2 GB**；api+mongo 两容器约 1.5 GB | MongoDB | 要 dump | 多模型。**官方 HF 模板路径已失效**（HF 免费档不能建 Docker Space）。详见下节最小化配方 |

**自用默认选 Open WebUI**（单容器 + 单文件备份）。核心需求是「一堆 PDF 直接问答」才选 AnythingLLM。

### Open WebUI vs LibreChat 八维选型速查（2026-09 核实，v0.11.4 vs v0.8.8-rc4）

**本质差异**：Open WebUI = 可深度改造成任何形态的 Agent Harness（官方原文「Every agent is a thin wrapper」，
**没有独立 Agent 对象**，Agent 就是模型预设）；LibreChat = 面向生产的多智能体平台（真 Agent + ACL + 编排 + 分布式可靠性）。

| 维度 | 胜出 | 关键事实 |
|---|---|---|
| 系统需求 / RAG 峰值 | **Open WebUI** | OWU 空闲 380–500MB、**本地嵌入 500MB × worker 数**（8 worker ≈ 4GB 仅嵌入）、单容器；LC 全栈空闲 ~1.2GB、6 容器、2GB 只是勉强下限 / 4GB 舒适。MongoDB 缓存默认 `max(0.5×(RAM−1GB), 256MB)`，**必须限流** |
| 知识库 | **Open WebUI** | OWU 真知识库：嵌套目录 + SHA-256 增量同步 + **混合检索(BM25+向量+重排)** + 13 向量库 + 8 解析引擎；LC 无独立 KB，纯向量，默认 top 4 |
| 记忆 | **Open WebUI** | OWU `ENABLE_MEMORIES` **默认 True**，结构化 + type/path，模型可自主增删改（8 个工具）；LC 需显式配置，键/值存储，自动抽取 opt-in，向量召回还在 roadmap |
| Agent 能力 | **LibreChat** | LC 有 **Handoffs(≤10) / Agent Chain MoA(≤10,beta) / Subagents** 三套编排；Max Agent Steps 默认 25 + 两级配置 + 步数用尽给「Keep going」。OWU 只有单层 `delegate_task`，无递归、无 peer 调用 |
| Skills / Tools | 分裂 | OWU 胜在**进程内 Python Tools + Valves + 四类 Functions**（Pipe/Filter/Action/Event，可做中间件和 UI 按钮）；LC 官方**劝退自写代码**（只给 MCP + OpenAPI Actions），但 Skills 体系更成熟（4 来源 / GitHub Sync / 版本校验） |
| MCP | **LibreChat** | OWU **仅 Streamable HTTP**（stdio/SSE 需 mcpo）+ **管理员专属**（用户不能自建）+ **无工具爆炸治理**（每调用发全量 schema，实测 29k tokens/次）。LC 三种传输全支持 + 每用户 MCP + ACL + **Deferred Tools/Tool Search 默认开启** |
| 定时任务 | **Open WebUI**（成熟度） | OWU **Automations 默认开启**，RRULE，UI 完整，执行历史，Import/Export，**可从聊天创建**，另有 Timers 一次性定时 + webhook 外发链路。LC Scheduled Chats **实验性 + 默认关闭 + 需 Redis**，但设计更工程化（MongoDB leases/幂等/MCP 预检） |
| 长程任务 | **LibreChat** | LC 有 **Background Tool Calls**（`check_background_task` + 自动唤醒 + 协作取消）+ **Resumable Streams**（断线/换设备/跨副本续跑）+ Stateful Code Sessions。OWU 无通用后台任务状态查询与断点续跑 |
| 办公处理 | 分裂 | Excel/数据分析 → **OWU**（Open Terminal：Docker、任意包、**可联网**、文件浏览器）；文档解析清晰度 → **LC**（Mistral OCR 默认、格式清单明确）；Artifacts → **LC**（支持 React/shadcn/Markdown，OWU 只渲染 HTML/SVG/JS） |

**一句话选型**：要省资源 / 贴 Python 扩展 / 开箱定时 / 深做知识库 / 给 AI 一台真电脑 → **Open WebUI**；
要多智能体编排 / 挂大量 MCP / 每用户 MCP / 长任务断线续跑 / 企业级 ACL 与 SSO → **LibreChat**。

### 把外部 Agent 接进聊天前端（2026-09 核实）

**核心结论：走「自定义 OpenAI 兼容端点」，不要走 MCP。** 两个主流自托管 agent 都暴露 OpenAI 兼容 `/v1`：

| Agent | 端口 | 填进前端的 URL | 模型名 | 认证 | 默认状态 |
|---|---|---|---|---|---|
| **OpenClaw**（原 Clawdbot，多渠道 Agent 网关） | 18789 | `http://localhost:18789/v1` | `openclaw/default` 或 `openclaw/<agentId>` | Gateway Bearer token | ❌ 端点**默认禁用**，需 `gateway.http.endpoints.chatCompletions.enabled=true` |
| **Hermes Agent**（Nous Research 自主智能体框架，MIT） | 8642 | `http://localhost:8642/v1` | `hermes-agent` | `API_SERVER_KEY` | 需 `API_SERVER_ENABLED=true` |

**两个前端都能接，但 Open WebUI 明显更方便**：
- Open WebUI 官方文档有专门的 **`/getting-started/quick-start/connect-an-agent/`** 文档区，**同时收录 OpenClaw 和 Hermes Agent**，含分步步骤 + 排错章节 + 官方 docker-compose
- 配置走**管理界面**（`Settings > Admin > Connections > Add Connection`），填 URL + Key → 验证 → 保存，**不碰文件、不重启**
- LibreChat 需手写 `librechat.yaml` 的 `endpoints.custom` + 挂载 + 重启，且**两个 agent 都没有官方教程**
- 只有 Open WebUI 支持「agent 作为机器人参与 Channels」（社区插件）

**⚠️ MCP 是陷阱，不要走**：`openclaw mcp serve` 和 `hermes mcp serve` **都只有 stdio**，且暴露的是**消息通道工具**（conversations_list / messages_read / messages_send / permissions_*），**不是聊天模型**。
所以「LibreChat 支持 stdio MCP」这个通用优势在这里空转。想要「前端 LLM 把 agent 当工具调」只能靠第三方桥（`freema/openclaw-mcp`，Streamable HTTP + `/mcp` + OAuth 2.1）。

**⚠️ 安全**：OpenClaw 官方原文——该端点等同 **full operator access**，「Keep it on loopback/tailnet/private ingress only. **Do not expose it to the public internet.**」前端与 agent 必须同机或同私有网络。

**两个通用坑**：① URL 的 **`/v1` 后缀必须带**（不带则连接测试通过但模型列表加载不出）；② Docker 里用 `host.docker.internal`，Linux 无 Docker Desktop 需 `--add-host=host.docker.internal:host-gateway`。

**信息质量警告**：Hermes Agent 的官方源只有 `hermes-agent.nousresearch.com` 和 `github.com/NousResearch/hermes-agent`。
网上有大量 SEO 镜像站（`hermesagentai.cn`、`hermes-agent.org`、`hermesagent.agency` 等）自称官方且数据互相矛盾。
另注意 **Hermes Agent（框架，MIT）≠ Hermes 3/4（模型，Llama Community License）**，搜索时务必区分。

## LibreChat 最小化部署配方（2026-09 一手核实）

**官方最低要求原文**（librechat.ai/docs/remote）：**1 GiB RAM + 1 vCPU**，「everything enabled 时建议 2GB」。1 GB 是理论下限，实际取决于跑几个容器。

**官方仓库有两个 compose，别混**：
- `docker-compose.yml` — 开发向，**6 个容器**：api、admin-panel、mongodb、meilisearch、vectordb(pgvector)、rag_api
- `deploy-compose.yml` — 部署向，同上 **+ nginx 反代容器**，api 挂载 `librechat.yaml`

**能砍到只剩 api + mongodb 两个容器**，只丢「文件问答(RAG)」和「全文搜索」，聊天本身不受影响。官方支持用 override 的 `profiles: [donotstart]` 禁用：

```yaml
# docker-compose.override.yml
services:
  api:
    depends_on: [mongodb]      # ⚠️ 必改：默认是 [mongodb, rag_api]，不禁用会报依赖错误
  meilisearch: { profiles: [donotstart] }
  rag_api:     { profiles: [donotstart] }
  vectordb:    { profiles: [donotstart] }
  admin-panel: { profiles: [donotstart] }
  mongodb:
    deploy: { resources: { limits: { memory: 512M } } }   # ⚠️ 必加，见下
```

**三个必踩的坑**：
1. **MongoDB 默认吃宿主机 50% 内存**（WiredTiger 缓存策略）→ 不限流，2 GB 机器必 OOM。**必须 `limits: memory: 512M`**。这是低配机器「莫名其妙 OOM」的头号原因。
2. **`api` 的 `depends_on` 默认含 `rag_api`**，只加 profile 不禁依赖 → `docker compose up` 直接失败。
3. **Apple Silicon（M 系列）Mac 本地跑**：默认 `mongo:8.x` 需要 AVX 指令，MongoDB 启动即崩 → override 指定 `image: mongo:4.4.18`。

**密钥机制**：`CREDS_KEY`(64 hex) / `CREDS_IV`(32 hex) / `JWT_SECRET` / `JWT_REFRESH_SECRET` **留空也能启动**（会生成随机值写入 `/app/data/.env.temp`），但重建容器会变 → 生产必须固定，用官方 Credentials Generator 或 `openssl rand -hex 32`。
**关搜索**：`.env` 默认 `SEARCH=false`，`MEILI_MASTER_KEY` 留空即可，`MEILI_HOST` 不用删。**注册控制**：自己注册完（首个账号即管理员）后设 `ALLOW_REGISTRATION=false`。

**数据库**：MongoDB 是硬依赖，**不支持 SQLite**。可用 Atlas M0 免费版（512MB）外置（改 `MONGO_URI` + override 禁本地 mongodb）；FerretDB（Postgres 后端）虽然可行但**不省内存**。

**⚠️ 国内镜像坑（LibreChat 特有，比通用坑更严重）**：镜像来自 `registry.librechat.ai`（官方自建）和 `ghcr.io`。**`registry.librechat.ai` 没有任何公共镜像加速**，内地服务器直连大概率超时。且 `daemon.json` 的 `registry-mirrors` **只对 docker.io 生效**，加速不了 ghcr。对策：选香港/新加坡节点，或 `docker save`/`load` 转运。

**PaaS 真实成本（2026-09）**：Railway 官方一键（5 服务，密钥自动生成）实际 **$20–26/月**（RAM $10/GB/月是大头，Free 档仅 $1 额度跑不动，Hobby 卷总量只有 5 GB）；**Zeabur 官方模板密钥硬编码**（`JWT_SECRET=secret`）必须手改；Elestio 全托管 **$16/月起**；Sealos 有零参数官方模板；**RackNerd ctrl 面板内置 LibreChat 一键部署**（全网唯一确认有官方级一键的 VPS 商家）；**腾讯云轻量香港 2核2G ¥55/月，免备案、200Mbps 无限流量**，是国内访问首选。

## 免费 LLM API 接入（Open WebUI 用 OpenAI 兼容端点）

| 提供商 | 端点 | 免费额度 |
|---|---|---|
| Google AI Studio | `https://generativelanguage.googleapis.com/v1beta/openai/` | 15 RPM / 1M TPM，Gemini 2.5 Flash |
| Groq | `https://api.groq.com/openai/v1` | 30K TPM / 14,400 RPD |
| Cerebras | `https://api.cerebras.ai/v1` | 1,000,000 tokens/天 |
| OpenRouter | `https://openrouter.ai/api/v1` | 13+ 个 `:free` 模型 |

## 部署检查清单（自建 AI 面板通用）

1. 容器只绑 `127.0.0.1:PORT:PORT`，公网入口全走 Cloudflare Tunnel
2. 数据必须挂宿主机目录（`-v /opt/xxx/data:/app/backend/data`）
3. `WEBUI_SECRET_KEY` / `JWT_SECRET` 生成一次**永不更换**
4. **首次注册后立刻关 `ENABLE_SIGNUP`**，否则任何人都能注册
5. SSH 关闭密码登录；Oracle 需同时放行**安全列表 + 本地 iptables/firewalld**
6. 备份用 `rclone` → R2（10 GB 免费），crontab 每天跑
7. 升级用 `docker compose pull && up -d`，先备份

## 平台硬约束速查

**Vercel（2026-06 起）**：支持 Docker（`Dockerfile.vercel`）+ Vercel Services（`vercel.json` 的 services/rewrites）；WebSocket **Beta 支持所有计划**（此前确实不支持，旧结论已过时），但连接在 max duration 关闭（Hobby 300s / Pro 800s）；容器默认监听 **80**；请求体上限 **4.5MB**；内存 Hobby 2GB 不可调；计费含**预置内存按实例生命周期持续计费**，Hobby 只有 360 GB-hours/月 → 2GB 实例约 **180 小时 ≈ 7.5 天**耗尽。

**Cloudflare 三层，别混用**：
- Workers = V8 isolate，**非容器**，无文件系统，跑不了重型软件，免费档 CPU 10ms/请求。
- Containers = OCI 镜像，2026-04-13 GA，**无免费层**（需 Workers Paid $5/月），磁盘每次停止重置为镜像初始状态，内存按预置层级持续计费 $0.009/GiB-小时。跑 Open WebUI 需 standard-1（4 GiB）→ 常驻内存费 4×720×$0.009 = **$25.92/月**，总计 **$31+/月**。
- Agents SDK + Durable Objects = **写代码而非装软件**，但这是免费层里唯一能同时解决「有状态 + 长连接 + 定时任务」的方案（内置 SQLite、原生 WebSocket、`schedule()`、agent 间 RPC）。

**Cloudflare Containers 踩坑点**：WebSocket 必须用 `fetch()` 而非 `containerFetch()`（后者静默失败）；启动必须用 `startAndWaitForPorts()`（20s 超时），用 `start()` 会在端口就绪前返回导致 `ECONNREFUSED`；`sleepAfter` 按**外部请求活动**计时，长任务会被误杀；无自动扩缩容，需手动 `getRandom()`；仍是 Beta 无 SLA。

**HF Spaces 踩坑点（2026 重大变化）**：**免费档已不能创建 Docker / Gradio Space**——官方原文「Gradio and Docker Spaces run on compute and require a paid plan to create: PRO for personal accounts」，即需 **PRO $9/月**；免费个人账号只剩 Static Space + 最多 2 个 ZeroGPU Gradio Space。**LibreChat 官方部署文档仍标注 HF 为免费，该文档已过时。** 其余：容器磁盘 ephemeral；Persistent Storage 已废弃，改为 Storage Buckets（$12/TB/月公有、$18/TB/月私有，需 `canPay`）；容器必须监听 **7860**；Docker Space 单容器跑不了 compose；免费 Space 无自定义域名。

**免费外部数据服务**：Neon（100 项目 / 每个 0.5GB / 100 CU-h/月，空闲 5 分钟挂起）、Supabase（2 项目 500MB，空闲 1 周暂停）、MongoDB Atlas M0（512MB）、Cloudflare R2（**10GB + 零出站费**，Cloudflare 最值钱的一环）。

## 零成本体验 / 试用路径（2026-09 核实，按「是否需要信用卡」分档）

**⚠️ 免费托管市场在 2025–2026 系统性收紧。搜索到的「教程」大量已失效，必须先查官方公告。**

### 不需要信用卡（国内用户的主战场）

| 途径 | 免费规格 | 期限 | 备注 |
|------|---------|------|------|
| **本机 Docker** | 自己的电脑 | 无限 | **纯体验场景永远的第一选择**，无需账号/实名/额度 |
| **腾讯云免费试用** | 轻量 2核2G / 2核4G | 1 个月 | **只需实名，不要卡**。个人可领 2核2G；2核4G 个企同享；企业认证可领 4核8G（每日限量）。CVM 蜂驰型 2核4G 仅 7 天 |
| **阿里云免费试用** | ECS **300 元额度**（个人）/660（企业），最高 4核8G | 额度 3 个月内用完 | 只需实名。额度制，**超额自动转按量扣余额**，到期不自动释放 |
| **京东云免费试用** | 轻量 2核4G 5M / CVM 2核4G | **15 天** | 只需实名，每账号限一次 |
| **华为云免费试用** | Flexus 2核2G / 2核4G | 1 个月 | 只需实名，**每日 9:30 限量抢** |
| **GitHub Codespaces** | 2 核 / **8 GB**，120 hrs + 15 GB-month | 每月重置 | **免卡**，支持 DinD + compose v2，端口可 Public。空闲 30min 停（最长 4h）→ 只能临时 |
| **Railway `ssh railway.new`** | 2 vCPU / **2 GB** | 24h 认领窗口 | **免账号免卡**，每 IP 每天 3 台。认领后落入 Free 档 |
| **Sealos** | 4 vCPU / 4 GB | 7 天 | 免卡，有官方 LibreChat 零参数模板 |
| **Azure for Students** | $100，B2pts v2 Arm 2核8G | **12 个月** | **官方明确无需信用卡**，仅限在读学生（国内可用学信网英文学籍报告验证，提交时须关代理） |

**四家国内云轮着领 ≈ 2 个月以上的 ≥2GB 机器，全程只需实名、零绑卡。**

### 需要信用卡（但真免费且能长期挂）

- **Northflank 免费 Sandbox** — 2 服务 + 1 DB + 2 cron、**always-on 不休眠**，DB 含 MongoDB。**与「1 Web + 1 MongoDB」结构严丝合缝**。缺点：必须绑卡，免费 CPU/RAM 未公开。
- **Oracle Cloud Always Free** — 2 OCPU / 12 GB 永久免费，可自建 MongoDB。缺点：需实体卡、抢机难、**负载长期 <20% 有回收风险**。

### 已失效避坑名单（网上教程仍在流传）

| 方案 | 状态 |
|------|------|
| **HF Spaces 免费 Docker Space** | ❌ **需 PRO $9/月**（官方原文：Gradio and Docker Spaces require a paid plan） |
| **ClawCloud Run** | ❌ **2026-05-11 停服**（曾给 $5/月免费额度） |
| **Gitpod** | ❌ 免费档取消，转型 Ona，$20/月起 |
| **Play with Docker** | ❌ 2026-03-01 下线 |
| **Katacoda** | ❌ 已下线（Killercoda 是替代，但单场景仅 1 小时） |
| **Koyeb 免费档** | ❌ 对新用户实际关闭，需卡 + $29 预授权 |
| **Fly.io 免费档** | ❌ 2024-10-07 取消 |
| **Heroku / Adaptable.io** | ❌ 2022-11 取消 / 2025 关停 |
| **Render 免费档** | ❌ 512MB（低于最低要求）+ 15 分钟休眠 + 无持久盘 |
| **Zeabur 免费档** | ❌ 共享集群已取消 |
| **Vercel Hobby / Replit 免费档** | ❌ 函数模型/不支持 compose，不适配常驻服务 |
| **Google Cloud Run / IBM Code Engine** | ❌ 常驻额度差 7–14 倍，且需卡 |

## 推荐组合（个人自用 $0）

- **没有外币卡** → 本机 Docker 跑通 → GitHub Codespaces 随时访问 → 国内云免费试用做真实部署
- **有外币卡** → **Northflank**（结构最匹配、不休眠）或 **Oracle Cloud ARM**（12 GB 永久）
- **是学生** → Azure for Students $100 / 12 个月（免信用卡）+ Namecheap 免费 .me 域名
- Open WebUI / AnythingLLM 比 LibreChat 更容易蹭到免费额度（**不需要 MongoDB**，单容器 + SQLite）
- Cloudflare 的角色 → **只放 R2、域名和 Tunnel**，不跑容器

## 工作方法

1. **先用三问法筛掉不可能的组合**，再谈细节。
2. 厂商官网查规格与定价；**「是否需卡」查第三方实测**（InfraFree、站长百科、APIRank、VPS SOS、HostAdvice 等）。
3. 报成本必须报口径：单价（$/GiB-小时）+ 是否含基础费 + 是否含 CPU 费 + 是否含请求费。
4. **主动回溯修正旧结论**：平台能力变化快（Vercel WebSocket、HF Persistent Storage、Cloudflare Containers GA 都变过），发现过时就改旧文件并告知用户。
5. 交付物用暗色主题单文件 HTML（用户偏好），表格优于散文。
