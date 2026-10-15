---
id: opencode-go-third-party-api
title: OpenCode Go API 供第三方客户端调用
tags:
  - opencode
  - opencode-go
  - llm-gateway
  - api
  - x-opencode-session
  - newapi
  - 中转
created: 2026-10-15
updated: 2026-10-15
version: 1.0
status: stable
source: 官方文档 https://opencode.ai/v2/docs/console/go + 本机 curl 实测（2026-10-15）
confidence: 已核实
---

# OpenCode Go API 供第三方客户端调用

## 一句话结论

OpenCode Go 的推理端点对第三方客户端只有一个硬门槛：**每个请求必须带非空的 `x-opencode-session` 请求头**，否则网关在鉴权之前直接返回 `400 MissingSessionID`；`User-Agent` 需自报客户端身份（非通用 SDK/HTTP 库名），但实测不在鉴权路径上拦截。

## 基础事实

| 项 | 值 |
|---|---|
| 计划 | Go `$10/月`；Go Plus `$40/月`（单人 workspace，不能邀请成员） |
| 鉴权 | `Authorization: Bearer <OPENCODE_API_KEY>`（Console 里签发的 Go key） |
| 密钥获取 | https://opencode.ai/console → 订阅 Go → 复制 API key |
| Go 端点根 | `https://opencode.ai/inference/go/v1/` |
| Zen 端点根（按量付费，非订阅） | `https://opencode.ai/inference/v1/` |
| 模型清单（免鉴权可读） | `curl https://opencode.ai/inference/go/v1/models` |
| 限额口径 | 每模型月度美元额度；5 小时 = 20%、周 = 50%、月 = 100% |
| 超额兜底 | Console 里开 `Use balance` 后回落到按量付费余额 |

## 端点按协议分流（关键：不是统一 OpenAI 兼容）

| 模型族 | 端点路径 | 协议 / AI SDK 包 |
|---|---|---|
| GLM-5.3/5.3-Flash/5.2、Kimi K3·K2.7-Code·K2.6、LongCat-2.0、DeepSeek V4.1-Flash/V4-Pro、MiMo-V2.5/-Pro/-V2.6-Flash/-Pro、Hy3、Hy4-preview、Space Bunny、LongCat 2.5 Preview Free、Step 5 Preview Free、Cat Jam Free | `/inference/go/v1/chat/completions` | OpenAI Chat Completions（`@ai-sdk/openai-compatible`） |
| Claude Haiku 5.5、MiniMax M3/M2.7、Qwen3.8 Max/Flash、Qwen3.7 Plus | `/inference/go/v1/messages` | Anthropic Messages（`@ai-sdk/anthropic`） |
| Grok 4.6/4.7、GPT 6 Luna、GPT 5.6 Luna、Muse Spark 1.2/1.3 Contributor | `/inference/go/v1/responses` | OpenAI Responses（`@ai-sdk/openai`） |
| Gemini 4 Argon Contributor | `/inference/go/v1/models/gemini-4-argon-contributor` | Google（`@ai-sdk/google`） |

### Go 端点实测模型清单（37 个，2026-10-15 从 `/inference/go/v1/models` 拉取）

```
deepseek-v4.1-flash  deepseek-v4-pro    glm-5.1              glm-5.2
glm-5.3              glm-5.3-flash       grok-4.6             grok-4.7
gpt-5.6-luna         gpt-6-luna          claude-haiku-5-5     gemini-4-argon-contributor
kimi-k2.6            kimi-k2.7-code      kimi-k3              minimax-m2.5
minimax-m2.7         minimax-m3          qwen3.6-plus         qwen3.7-plus
qwen3.7-max          qwen3.8-max         qwen3.8-flash        muse-spark-1.2-contributor
muse-spark-1.3-contributor               mimo-v2.5            mimo-v2.5-pro
mimo-v2.6-flash      mimo-v2.6-pro       hy3                  hy4-preview
space-bunny          longcat-2.0         longcat-2.5-preview-free
step-5-preview-free  cat-jam-free        omen-alpha
```

在 OpenCode 客户端内选模型用 `opencode-go/<model-id>`：

```jsonc
{ "$schema": "https://opencode.ai/config.json", "model": "opencode-go/kimi-k3" }
```

## 第三方客户端的三条要求（官方原文口径）

> 1. Send typical coding agent traffic
> 2. Identify itself with its own user agent, such as `my-coding-agent/1.0`, rather than a generic SDK or HTTP-library name.
> 3. Send a stable session ID in `x-opencode-session` for each conversation so we can optimize routing and prompt caching.

`x-opencode-session` 的语义：**同一对话内固定不变，不同对话之间不同**。用于把同一对话的多轮请求路由到同一 GPU，复用 prompt cache。

## 实测结果（2026-10-15，本机 curl 直连 `opencode.ai`）

| 场景 | 结果 |
|---|---|
| `GET /inference/go/v1/models` 无任何 header | **200**，返回 37 个模型 |
| `POST /inference/go/v1/chat/completions` 无 `x-opencode-session` | **400** `{"type":"error","error":{"type":"MissingSessionID","message":"Request is missing x-opencode-session and cannot be routed efficiently..."}}` |
| 同上，`x-opencode-session: `（空字符串） | **400** 同上 |
| 同上，`x-opencode-session: abc`（非 UUID） | **401** `Upstream request failed: Invalid credential` → 已过 session 校验 |
| 同上，UUID v4 + `User-Agent: curl/8.5.0` | **401** 同上 → UA 未在鉴权前拦截 |
| Zen 端点 `/inference/v1/chat/completions` 不带 session | **401**（直接鉴权失败，**不要求** session） |

结论：当前 session 校验**只做非空判断**，不校验 UUID 格式；但官方明确说未来会收紧。UA 要求未在鉴权路径上强制（风控可能事后判定）。

## 已验证 / 已知有问题的第三方客户端（官方列表）

| 客户端 | 状态 |
|---|---|
| Hermes | 含 [PR #101864](https://github.com/NousResearch/hermes-agent/pull/101864) 的构建会发该头；v0.21.0 本身**不含** |
| Claude Code | 识别其原生 session 头，无需额外包装 |
| Codex | 识别原生 session 头；部分版本/代理会丢，转发时需保留 |
| ZCode | 识别原生 session 头；不必强发 `x-opencode-session` |
| Pi | 新版会发；老版本需更新 |
| jcode | 需 **≥ v0.81.6** |
| Kilo Code CLI | 含 [PR #13752](https://github.com/Kilo-Org/kilocode/pull/13752) 的构建；不含 VS Code 扩展 |
| DeepSeek Harness | ⚠️ 部分模型路径缺 session（[Discussion #5495](https://github.com/deepseek-ai/deepseek-harness/discussions/5495)） |
| GitHub Copilot Chat | ⚠️ 无自动 session 头（[VS Code #334186](https://github.com/microsoft/vscode/issues/334186)） |
| Kimi Code | ⚠️ 无自动 session 头（[#3506](https://github.com/MoonshotAI/kimi-code/issues/3506)） |
| MiMo Code | ⚠️ 修复未合并（[#2317](https://github.com/XiaomiMiMo/MiMo-Code/issues/2317) / [#2327](https://github.com/XiaomiMiMo/MiMo-Code/pull/2327)） |

## 可复用操作

### 1. 最小可用的 curl（OpenAI Chat Completions 路径）

```bash
OPENCODE_API_KEY="sk-你的-go-key"
SESSION="$(uuidgen)"   # 同一对话复用同一个值；换对话换新值

curl https://opencode.ai/inference/go/v1/chat/completions \
  -H "Authorization: Bearer $OPENCODE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: my-coding-agent/1.0" \
  -H "x-opencode-session: $SESSION" \
  -d '{"model":"glm-5.3","messages":[{"role":"user","content":"hi"}],"stream":true}'
```

### 2. Anthropic Messages 路径

```bash
curl https://opencode.ai/inference/go/v1/messages \
  -H "x-api-key: $OPENCODE_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -H "User-Agent: my-coding-agent/1.0" \
  -H "x-opencode-session: $SESSION" \
  -d '{"model":"claude-haiku-5-5","max_tokens":1024,"messages":[{"role":"user","content":"hi"}]}'
```

### 3. 通用 OpenAI 兼容客户端

- `base_url` = `https://opencode.ai/inference/go/v1`
- `api_key` = Go key
- 额外静态 header：`x-opencode-session: <uuid>`、`User-Agent: <你的客户端名>`

注意：若客户端只支持静态 header，则所有对话共用一个 session，会失去 prompt cache 路由收益（功能可用，效率打折）。

### 4. NewAPI / One-API 类中转：请求头覆盖

渠道 → 编辑 → 请求头覆盖：

```json
{
  "User-Agent": "{client_header:user-agent}",
  "X-Opencode-Session": "{client_header:x-conversation-id}"
}
```

若客户端没有等价会话头，用「参数覆盖」把常见别名映射过来：

```json
{
  "operations": [
    { "mode": "copy_header", "keep_origin": true, "from": "Session-Id", "to": "X-Opencode-Session" },
    { "mode": "copy_header", "keep_origin": true, "from": "X-Conversation-Id", "to": "X-Opencode-Session" },
    { "mode": "copy_header", "keep_origin": true, "from": "X-Claude-Code-Session-Id", "to": "X-Opencode-Session" }
  ]
}
```

已知可作为 session 源的客户端头：`x-conversation-id`（WorkBuddy 等 ACP 客户端，UUID v4、同对话稳定、重启不变）。

### 5. Claude Code 接入

```bash
export ANTHROPIC_BASE_URL="https://opencode.ai/inference/go"
export ANTHROPIC_AUTH_TOKEN="$OPENCODE_API_KEY"
```

Claude Code 自带原生 session 头，Go 能识别，无需额外包装（官方口径）。

### 6. 快速自检

```bash
# 无鉴权也能拉模型表，先确认通道通不通
curl -s https://opencode.ai/inference/go/v1/models | head -c 300

# 缺 session 的报错就是这一条
# {"type":"error","error":{"type":"MissingSessionID", ...}}
```

## 坑与反直觉

1. **session 不是静态密钥。** 写死一个值 → 并行任务在上游看来像"多人共用同一对话"，属高风险特征。必须做到「同对话固定、跨对话唯一」。
2. **但也不能每轮换新值。** 每请求换 UUID 会让 prompt cache 完全失效，等于主动放弃 Go 的核心优化。
3. **session 校验目前只判非空**（`abc` 也放行），但官方说未来会严格要求格式 → 现在就用 UUID v4，别图省事。
4. **`User-Agent` 不要用通用库名**（`python-requests/2.x`、`curl/8.x`、`OpenAI/Python 1.x`）。官方明确要求自报客户端身份。
5. **Go 与 Zen 是两套路径**，模型 ID 也不同。Go 的 Claude 只有 Haiku 5.5，Gemini 只有 Argon Contributor；走错路径会变成按量扣费。
6. **端点协议不统一**：GLM/DeepSeek/Kimi 走 `/chat/completions`，Claude/MiniMax/Qwen 走 `/messages`，Grok/GPT Luna/Muse 走 `/responses`。做中转时要按模型分流，不能一个 base_url 全接。
7. **Go/Go Plus 只能用于单人 workspace**，有 Go 订阅的 workspace 无法邀请成员。
8. **`/v1/models` 完全免鉴权**，可用来做存活探针，但别拿它判断 key 是否有效。
9. **超额不报错而是回落到按量付费**（前提：Console 里开了 `Use balance`）—— 会静默花钱。
10. **中转层测速会暴露通用 UA**，测试请求用默认 Go HTTP client 头，容易触发风控判定。

## 未核实 / 存疑

- `x-opencode-session` 是否在**鉴权成功后**还有格式/一致性校验（无真实 key，无法测）。
- `User-Agent` 是否由异步风控事后判定并封禁，以及白名单粒度（文档只说"traffic is monitored for abuse"）。
- 2026-09-06 之前社区流传的"session 是带签名和时效的 JWT"说法（CSDN 个别文章）**与实测矛盾** —— 实测非空字符串即通过。该说法标记为**不可信**。
- Go 端点的速率/并发限制未在文档中给出具体数值。
- `omen-alpha`（出现在 `/models` 返回中，37 个模型之一）在官方文档模型表中未列出，用途未知。
