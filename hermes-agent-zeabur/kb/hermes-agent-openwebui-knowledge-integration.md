---
id: hermes-agent-openwebui-knowledge-integration
title: Hermes Agent + Open WebUI 共部署：模型调用、知识库边界与 1C4G 资源可行性
tags:
  - hermes-agent
  - open-webui
  - api-server
  - rag
  - knowledge-base
  - memory
  - resource-planning
created: 2026-10-15
updated: 2026-10-15
version: 1.0.0
status: stable
source: 本机 Hermes Agent 源码（C:\Users\Admin\AppData\Local\hermes\hermes-agent）website/docs/user-guide/{messaging/open-webui.md, features/api-server.md, features/memory.md, features/memory-providers.md}、gateway/ 源码 grep、Zeabur 官方文档、Web 检索
confidence: 已核实
---

## TL;DR

1. **能装，1C4G 上别跑 K3s**。Hermes + Open WebUI 两个容器在 1C4G 的纯 Ubuntu 上勉强够用；叠 ZeaburOS（K3s 要预留约 1GB）会 OOM。
2. **调用「模型」**：Open WebUI 的 OpenAI 连接指向 Hermes 的 `:8642/v1`。拿到的是**完整 agent**，不是纯 LLM 代理。
3. **调用「知识库」要分清两层**：
   - **Open WebUI 的知识库能用** —— RAG 在 Open WebUI 侧完成检索，把片段拼进 prompt 再发给 Hermes，所以 Hermes 不支持 `/v1/embeddings` 完全不影响。
   - **Hermes 自己的记忆/会话调不到** —— MEMORY.md / USER.md / state.db 只在 agent 内部使用，**没有任何外部接口**（已 grep 源码确认）。

---

## 一、Hermes 的 API server 到底暴露了什么

官方文档明确：`API_SERVER_ENABLED` 默认 `false`，`API_SERVER_HOST` 默认 `127.0.0.1`。

### 端点清单（已核实）

| 端点 | 用途 |
|---|---|
| `POST /v1/chat/completions` | OpenAI 兼容对话（推荐） |
| `POST /v1/responses` | Responses 格式，支持 `previous_response_id` 链式 |
| `GET /v1/models` | 模型列表（只给名字，是「廉价兼容面」） |
| `GET /api/model/options` | 更丰富的模型元数据 |
| `GET /v1/capabilities` | 能力发现（runs / streaming / cancellation / session continuity） |
| `GET /health`、`GET /v1/health`、`GET /health/detailed` | 健康检查 |
| `POST /v1/runs`、`GET /v1/runs/{id}`、`/events`、`/stop`、`/approval` | 长任务订阅式 API |
| `GET/POST /api/jobs`、`/api/jobs/{id}`、`/pause` | 定时/后台任务 CRUD |
| `POST /api/sessions/{id}/chat`、`/chat/stream` | 会话级对话 |
| `GET /api/sessions/{id}/messages` | 会话消息 |
| `POST /v1/browser-control/register`、`GET /v1/browser-control/ws` | 浏览器控制 WebSocket |

### 关键结论：没有 embeddings，也没有知识库端点

- `grep -rn "v1/embeddings|/embeddings" gateway/ hermes_platform/ agent/` → **无结果**
- `api-server.md` 全文无 "embedding" 字样

所以任何依赖 `/v1/embeddings` 的客户端（把 Hermes 当 embedding provider）会失败。Open WebUI 不受影响，因为它的 embedding 走独立配置。

### 安全：API server = 完整工具链

官方原文警告：

> The API server gives full access to hermes-agent's toolset, **including terminal commands**. `API_SERVER_KEY` is **required for every deployment**, including the default loopback bind on `127.0.0.1`.

即：key 泄露 = 服务器被接管（终端命令可执行）。CORS 默认关闭，需要时收窄 `API_SERVER_CORS_ORIGINS`。

**运行时位置提示**（官方 `:::important`）：API server 是 **agent runtime，不是纯 LLM 代理**。每个请求会在 API server 所在主机上创建服务端 `AIAgent`，工具调用（`pwd`、文件、浏览器、本地 MCP）都在**那台机器**上跑，不是在你的电脑上。「远端大脑、本地双手」的 split-runtime 仍在 issue #18715 里，**当前版本没有这个行为**。

---

## 二、如何让 Open WebUI 调用 Hermes

Hermes 仓库里有一份官方文档专门讲这件事：`website/docs/user-guide/messaging/open-webui.md`。

### 架构

```
Open WebUI (浏览器 UI, :3000)
    │  POST /v1/chat/completions
    ▼
hermes-agent gateway API server (:8642)
    │  SSE streaming response
    ▲
```

Open WebUI 与 Hermes 是**服务端到服务端**通信，所以这个集成**不需要** `API_SERVER_CORS_ORIGINS`。

### 步骤 1：Hermes 侧开 API server

```bash
hermes config set API_SERVER_ENABLED true
hermes config set API_SERVER_KEY your-secret-key
hermes gateway stop && hermes gateway
```

`hermes config set` 会自动把开关路由到 `config.yaml`、把密钥路由到 `~/.hermes/.env`。

容器/Zeabur 部署则用环境变量：

```env
API_SERVER_ENABLED=true
API_SERVER_HOST=0.0.0.0
API_SERVER_KEY=<openssl rand -hex 32>
```

### 步骤 2：验证

```bash
curl -s http://127.0.0.1:8642/health
# {"status": "ok", ...}

curl -s -H "Authorization: Bearer your-secret-key" http://127.0.0.1:8642/v1/models
# {"object":"list","data":[{"id":"hermes-agent", ...}]}
```

排查口诀：`/health` 失败 → gateway 没读到 `API_SERVER_ENABLED`，重启它；`/v1/models` 返回 401 → `Authorization` 头与 `API_SERVER_KEY` 不匹配。

### 步骤 3：Open WebUI 侧

```bash
docker run -d -p 3000:8080 \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8642/v1 \
  -e OPENAI_API_KEY=your-secret-key \
  -e ENABLE_OLLAMA_API=false \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

- `ENABLE_OLLAMA_API=false` 抑制默认 Ollama 后端，否则模型选择器里会多出一个空的 Ollama 分组
- 首次启动 15–30 秒：会下载 sentence-transformer 嵌入模型（约 150MB）

**Linux 无 Docker Desktop** 时 `host.docker.internal` 不解析，三种解法：

```bash
docker run --add-host=host.docker.internal:host-gateway ...
docker run --network=host -e OPENAI_API_BASE_URL=http://localhost:8642/v1 ...
docker run -e OPENAI_API_BASE_URL=http://172.17.0.1:8642/v1 ...
```

**同项目内（Zeabur / Docker Compose）** 走内网，不要绕公网：

```env
OPENAI_API_BASE_URL=http://<hermes 服务名>.zeabur.internal:8642/v1
```

### 步骤 4：API 类型选择

| 模式 | 格式 | 何时用 |
|---|---|---|
| Chat Completions（默认） | `/v1/chat/completions` | 推荐，开箱可用 |
| Responses（实验） | `/v1/responses` | 需要结构化事件流（`function_call` / `function_call_output`）时 |

注意：Open WebUI 目前在 Responses 模式下**仍然客户端管理历史**，每轮都发完整消息列表，不走 `previous_response_id`。Responses 模式的现实收益主要是结构化事件流，不是服务端会话状态。

### 请求生命周期（决定了为什么"慢"）

1. Open WebUI 发 `POST /v1/chat/completions`（含完整历史）
2. Hermes 用 API server 所属 profile 的模型/记忆/技能/工具集创建服务端 `AIAgent`
3. agent 执行，可能调用工具（终端、文件、web 搜索）
4. 工具执行期间，**内联进度消息流式推到 UI**（如 `` `💻 ls -la` ``、`` `🔍 Python 3.12 release` ``）
5. 最终文本流式返回
6. Open WebUI 渲染

**多用户隔离**：用 Hermes profiles，每个 profile 跑独立 API server 端口，模型名默认就是 profile 名。端口要避开 `8644`（webhook adapter）、`8645`（wecom-callback）、`8646`（msgraph-webhook），建议 `8650+`。

```bash
hermes profile create alice
cat >> ~/.hermes/profiles/alice/.env <<EOF
API_SERVER_ENABLED=true
API_SERVER_PORT=8650
API_SERVER_KEY=alice-secret
EOF
hermes -p alice gateway &
```

自定义模型名：`hermes -p alice config set API_SERVER_MODEL_NAME "Alice's Agent"`

---

## 三、知识库：两层，只有一层能被"调用"

### 第一层：Hermes 自己的"知识" —— 无外部接口

| 机制 | 存储位置 | 容量 | 外部可调用 |
|---|---|---|---|
| `MEMORY.md` | `~/.hermes/memories/` | **2,200 字符**（约 800 token） | ❌ |
| `USER.md` | `~/.hermes/memories/` | **1,375 字符**（约 500 token） | ❌ |
| `session_search` | `~/.hermes/state.db`（SQLite **FTS5** 全文索引） | 全量 CLI + 消息平台会话 | ❌ |

三个反直觉点：

1. **容量极小**。2,200 + 1,375 字符是硬上限。写超了 `memory` 工具**报错**而不是静默丢弃，agent 得自己腾地方。所以 MEMORY.md 不是知识库，是「便签」。
2. **快照是冻结的**。会话开始时把 memory 渲染进 system prompt，之后**本会话内不再变**（为了保住 LLM 的 prefix cache）。本次会话写的条目，**下一个会话**才看得到。
3. **快照机制需要会话边界**。消息平台上的聊天是一个跨重启、跨宕机的**连续会话**，可能跑几周不结束 —— 这样「忘记 → 从记忆回忆 → 搜历史会话」的学习闭环几乎不会触发。**实践**：在自然边界（任务结束、换话题、每天开始）手动 `/new`。

**想让 Hermes 有真正的长期知识库** → 挂外部 memory provider。官方内置 7 个插件 + 插件目录里更多：

Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover、Supermemory

```bash
hermes memory setup      # 交互式选择 + 配置
hermes memory status
hermes memory off
```

或写进 `~/.hermes/config.yaml`：

```yaml
memory:
  provider: openviking
```

启用后 Hermes 会自动：注入 provider 上下文到 system prompt / 每轮前预取相关记忆（后台非阻塞）/ 每轮后同步对话 / 会话结束时抽取记忆 / 镜像内置 memory 写入 / 增加 provider 专属工具（search、store、manage）。

**同一时间只能启用一个**外部 provider，内置 memory 始终并行生效。

### 第二层：Open WebUI 的知识库 —— 能用，且不依赖 Hermes

这是关键机制：**Open WebUI 的 RAG 是客户端侧的**。

```
上传文档 → Open WebUI 切块 → 向量化 → 存本地向量库
                                        ↓
用户提问 → 检索命中片段 → 拼进 messages/system prompt
                                        ↓
                        POST /v1/chat/completions → Hermes
```

检索发生在 Open WebUI 内部，Hermes 收到的已经是一个「带上下文的 prompt」。所以：

- Hermes **不需要**支持 `/v1/embeddings`（它确实不支持）
- Hermes 不需要知道知识库的存在
- 知识库的效果取决于 Open WebUI 的检索质量 + 你塞进去的文档

### 坑 1：默认 embedding 在本地算，吃内存吃 CPU

Open WebUI 默认 `RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2`，缓存在容器内 `/app/backend/data/cache/embedding/models`（对应 `SENTENCE_TRANSFORMERS_HOME`）。首次启动下载约 150MB，加载时要把 torch 拉进内存。

**1C4G 上这是最大的内存负担，也是 1 vCPU 下最慢的环节。** 改成远程 embedding：

```env
RAG_EMBEDDING_ENGINE=openai
RAG_OPENAI_API_BASE_URL=https://api.siliconflow.cn/v1
RAG_OPENAI_API_KEY=<你的 key>
RAG_EMBEDDING_MODEL=BAAI/bge-m3
```

把 embedding 算力挪出 VPS，同时把约 400–800MB 内存和 CPU 峰值一起挪走。

### 坑 2：Open WebUI 的「任务模型」会偷偷起 agent run

Open WebUI 会额外调模型做：标题生成、标签生成、追问建议、RAG 查询改写。

如果这些也指向 Hermes，**每一条都会在服务器上创建一个完整 `AIAgent` 并可能触发工具调用** —— 又慢又烧 token，而且会在你的会话库里留下大量垃圾会话。

**解法**：Admin Settings → Models → 把 **Task Model** 单独设成一个便宜的纯 LLM（DeepSeek / Qwen / gpt-4o-mini 之类），只有真实对话走 Hermes。

### 坑 3：环境变量只在首次启动生效

Open WebUI 首次启动后把 OpenAI 连接配置存进**自己的数据库**。之后改环境变量无效，必须：

- Admin Settings → Connections → OpenAI API → Manage → 改连接，或
- 删掉 volume / 数据目录重来

### 坑 4：连接测试通过 ≠ 模型列表能加载

几乎总是 URL 少了 `/v1` 后缀。Open WebUI 的连接测试只做基础连通性检查，不验证模型列表。正确写法：`http://host.docker.internal:8642/v1`（不是 `:8642`）。

### 坑 5：Docker 里 `localhost` 指容器自己

用 `host.docker.internal`、`--network=host`，或直接写 bridge IP `172.17.0.1`。

---

## 四、1C4G 资源可行性

### 内存账（**估算**，非官方规格）

| 组件 | 空闲 | 峰值 | 说明 |
|---|---|---|---|
| 操作系统 | 300–500 MB | — | Ubuntu Server 基准 |
| K3s（仅 ZeaburOS） | ~1,000 MB | — | K8s 预留 500m CPU/512Mi + System 预留 500m/512Mi |
| Hermes Agent | 400–700 MB | 1.0–1.5 GB | Python 3.14 + Node + s6；工具调用时上涨 |
| Open WebUI | 400–700 MB | 1.2–1.8 GB | 本地 embedding 加载 torch 时最高 |
| **合计（纯 Docker，无 K3s）** | **1.1–1.9 GB** | **2.2–3.3 GB** | 1C4G 勉强，需关掉本地 embedding |
| **合计（ZeaburOS / K3s）** | **2.1–2.9 GB** | **3.2–4.3 GB** | **会 OOM** |

结论：
- **1C4G + ZeaburOS + 两个服务 → 会 OOM**（K3s 白白吃掉约 1GB）
- **1C4G + 标准 Ubuntu + Docker + 两个服务 + 远程 embedding → 可行但紧**
- **1 vCPU 是另一个硬伤**：本地 embedding、文档切块都在抢这 1 个核

> Hermes 官方 README 只声称「$5 VPS」可跑，未给 RAM 硬指标。Open WebUI 也未在本次核实中找到官方最低内存规格。上表为基于组件构成的估算，标注为**推断**。

### 三种方案（按推荐度排序）

**方案 A（推荐）：2C8G 的 ZeaburOS 机器，两个服务都进 Zeabur 面板**
- 走内网 `http://<hermes>.zeabur.internal:8642/v1`，**不需要**把 8642 暴露公网
- 面板统一管日志、指标、重启、防火墙
- 成本换稳定，不会半夜 OOM

**方案 B：1C4G 只跑 Hermes，Open WebUI 放别处**
- Open WebUI 跑在你本地电脑（`docker run` 一行）或另一个免费/便宜的容器平台
- 通过 `https://<hermes 域名>:8642/v1` 连过来，必须强 `API_SERVER_KEY`
- ⚠️ 这样 8642 就暴露在公网了，等于把你的服务器终端暴露给持有 key 的人

**方案 C：1C4G 用标准 Ubuntu 发行版（放弃 Zeabur 面板）**
- 省下 K3s 的约 1GB
- `docker compose` 直接跑 Hermes + Open WebUI，Hermes 的 8642 只绑 `127.0.0.1` 不对外
- 代价：失去面板管理，SSH 运维；Zeabur 对标准发行版不提供技术支持

---

## 五、可复用操作

### Hermes 容器（Zeabur / Docker）

```env
HERMES_DASHBOARD=1
API_SERVER_ENABLED=true
API_SERVER_HOST=0.0.0.0
API_SERVER_KEY=<openssl rand -hex 32>
```

Ports：`9119` HTTP（Dashboard）、`8642` HTTP（API，同项目内走内网则不必绑公网域名）

### Open WebUI 容器

```env
OPENAI_API_BASE_URL=http://hermes.zeabur.internal:8642/v1
OPENAI_API_KEY=<与 API_SERVER_KEY 完全一致>
ENABLE_OLLAMA_API=false
RAG_EMBEDDING_ENGINE=openai
RAG_OPENAI_API_BASE_URL=https://api.siliconflow.cn/v1
RAG_OPENAI_API_KEY=<embedding key>
RAG_EMBEDDING_MODEL=BAAI/bge-m3
```

### 验证链路

```bash
curl -s http://127.0.0.1:8642/health
curl -s -H "Authorization: Bearer <key>" http://127.0.0.1:8642/v1/models
curl -s -H "Authorization: Bearer <key>" http://127.0.0.1:8642/v1/capabilities
```

### Hermes 记忆运维

```bash
cat ~/.hermes/memories/MEMORY.md
cat ~/.hermes/memories/USER.md
hermes memory setup      # 配置外部 memory provider
hermes memory status
hermes profile list      # 确认 profile 与记忆归属
```

---

## 六、未核实 / 存疑

- 上文内存表为**推断**（基于组件构成估算），非官方规格。Hermes 与 Open WebUI 均未在本次核实中找到官方 RAM 硬指标。
- Open WebUI 的「Task Model」具体设置项名称与路径未逐项核实（属通用已知行为，未读源码）。
- `RAG_EMBEDDING_ENGINE=openai` 的具体参数名（`RAG_OPENAI_API_BASE_URL` 等）来自社区文档与镜像环境变量输出，**未在官方文档逐项核实**。
- 未实测在 Zeabur 同项目内用 `*.zeabur.internal` 打通 Hermes ↔ Open WebUI 的完整链路。
- Hermes 是否完整读取进程环境变量（而不仅是 `/opt/data/.env`）未逐行核实源码。
- 「远端大脑、本地双手」split-runtime 仍是 issue #18715，**当前版本不存在该行为**——这一点官方文档已明确，属已核实。
