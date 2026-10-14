---
id: discord-content-search-methods
title: 搜索 Discord 内容的所有方式（客户端/导出/数据包/扩展/内部 API/GitHub 代码搜索）
tags:
  - discord
  - search
  - discord-cli
  - sqlite
  - ripgrep
  - github-search
  - osint
created: 2026-10-14
updated: 2026-10-14
version: 1.0
status: stable
source: 本次会话（GitHub REST API 实测 + 各项目 README/官网抓取）
confidence: 已核实
---

# 搜索 Discord 内容的所有方式

## 一句话结论

Discord 官方只提供「登录后、已加入范围内」的客户端搜索，且 bot 完全没有搜索端点；要搜自己的历史或跨频道内容，唯一可靠路径是**导出/同步到本地再全文检索**——首选 `jackwener/discord-cli`（SQLite + FTS + CLI，2026-10-14 实测 133★）或 `Tyrrrz/DiscordChatExporter`（12.2k★，导出后 ripgrep）；找公开服务器用 disboard/top.gg/官方 Discovery；从 GitHub 层面搜 Discord 内容用 REST Search API（免登录）与 `search/code`（需 token）搜消息雪花 ID / `discord.com/channels` 链接镜像。

---

## 1. 方式总览

| 层 | 方式 | 覆盖范围 | 核实状态 |
|---|---|---|---|
| 官方客户端 | Ctrl/F 搜索 + 运算符 | 仅已加入服务器/DM | 已核实 |
| 导出本地 | DiscordChatExporter → ripgrep | 有权限的频道 | 已核实 |
| 本地同步库 | jackwener/discord-cli → SQLite | 同步过的频道 | 已核实 |
| 持续归档 | Discord-History-Tracker / Quark Logger | 事先记录的内容 | 已核实 |
| 数据包 | Data-Package-Tool / discorch.org | 你的消息 + 可访问部分 | 已核实 |
| 客户端增强 | Global-Search（Vencord 插件） | 跨所有 DM/群聊 | 已核实 |
| 非官方 API | POST /api/v9/guilds/{id}/messages-search | 账号可见范围 | 社区实证 |
| selfbot 脚本 | KanekiWeb/Messages-Searcher | 全频道（违反 ToS） | 已核实存在，风险已知 |
| GitHub 代码层 | Search API / search/code / grep.app | 全网镜像引用 | 已实测（2026-10-14） |
| 找服务器 | disboard / top.gg / Discovery | 服务器列表 | 已核实 |

## 2. 官方客户端搜索（已核实）

- 入口：桌面端频道内 Ctrl+F 或右上搜索框；运算符：`from:`、`in:`、`has:link/image/file`、`before:`/`after:`/`during:`/`on:`、`mentions:`、`pinned:`。
- 铁律：**只能搜已加入/可见的内容**；服务端搜索端点不对 bot 开放（2026-10 mcpworld 对 Discord MCP 服务器的说明佐证：搜索只能拉最近 N 条本地过滤）。
- 已删消息客户端无法找回 → 必须提前持续记录（见第 4 节）。

## 3. 工具清单（2026-10-14 GitHub API 实测，star 为当日快照）

| 工具 | Star | 定位 | 关键能力 |
|---|---|---|---|
| [Tyrrrz/DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) | 12.2k | 导出器 | HTML/PlainText/JSON/CSV；GUI+CLI；批量频道；主题含 archival |
| [chylex/Discord-History-Tracker](https://github.com/chylex/Discord-History-Tracker) | 589 | 持续归档 | 桌面 app（.NET 9）+ 浏览器脚本，后台存历史 + 离线查看器 |
| [jackwener/discord-cli](https://github.com/jackwener/discord-cli) | 133 | 本地优先 CLI | `discord search "rust" -c general --json`；SQLite 存储；可喂 AI agent |
| [pratherbytecraft/discrub](https://github.com/pratherbytecraft/discrub) | 121 | 浏览器扩展 + Web App | 消息流/搜索/过滤/导出/清理；按 ID 打开已关闭 DM |
| [aamiaa/Data-Package-Tool](https://github.com/aamiaa/Data-Package-Tool) | 176 | 数据包浏览器 | C# GUI，按服务器/频道/DM 搜索消息 |
| [Qubzy/DiscordSearchExporter](https://github.com/Qubzy/DiscordSearchExporter) | 3 | BetterDiscord 插件 | 把官方搜索结果逐页导出（绕速率限制） |
| [Atom1cByte/Global-Search](https://github.com/Atom1cByte/Global-Search) | 16 | Vencord 插件 | 跨所有 DM/群聊全局搜索 |

## 4. 数据与边界口径

- 官方数据包入口：Settings → Privacy & Safety → Request Data，解压后 `Messages/` 目录是 Data-Package-Tool / [discorch.org](https://discorch.org/)（纯前端、离线运行）的输入。
- **数据包不是全量备份**：含你的消息与 DMs，不等于所有可读历史。
- 商业件：[Friendcord](https://friendcordapp.com/)（闭源，自称 2.7 万用户，本地恢复/搜索历史与已删 DM）；[Quark Logger](https://quark.bot/)（日志机器人，删消息/编辑历史取证，需事先部署）。

## 5. 从 GitHub 搜 Discord 内容（2026-10-14 实测路径）

| 渠道 | 限额/条件 | 实测结果 |
|---|---|---|
| `api.github.com/search/repositories` | 免登录 10 次/分 | `q=discord+messages+search` → 145 个仓库，与网页端一致 |
| `api.github.com/search/code` | 需登录 token | 搜 `discord.com/channels` / 雪花 ID，命中 issue、机器人配置、支持日志 |
| grep.app | 免登录（有盾） | 2026-10-14 实测：curl 与无头浏览器均被 Vercel Security Checkpoint 拦截 |
| GH Archive | BigQuery | 查 commit message 中的 Discord 链接 |
| GitHub 网页搜索页 | JS 渲染 | WebFetch 直抓返回空 → 用无头浏览器 `open` + `snapshot` |

---

## 可复用操作

```bash
# 1) GitHub 仓库搜索（免登录，按 star 排序）
curl -s -H "Accept: application/vnd.github+json" \
  "https://api.github.com/search/repositories?q=discord+messages+search&sort=stars&order=desc&per_page=10"

# 2) GitHub 代码搜索（需 token；搜 Discord 消息链接镜像）
curl -s -H "Authorization: Bearer $GH_TOKEN" \
  "https://api.github.com/search/code?q=%22discord.com%2Fchannels%22+in:file"

# 3) discord-cli：本地 SQLite 同步 + 全文搜索 + JSON 导出
discord search "rust" -c general --json

# 4) DiscordChatExporter 导出后 ripgrep 全文检索
./DiscordChatExporter.Cli export -c <CHANNEL_ID> -t <TOKEN> -f Json
rg -i "关键词" --glob "*.json" .
```

```text
# 官方搜索运算符速查
from:某人           按作者过滤
in:#频道或服务器名  限定范围
has:link/image/file/sound/sticker/embed
before:/after:/during:/on:  日期过滤
mentions:@我
pinned:            只看置顶
```

---

## 坑与反直觉

1. **WebFetch 抓 GitHub 仓库页/搜索页返回空** —— 全 JS 渲染；改用 `raw.githubusercontent.com/<repo>/HEAD/README.md`、Contents API（base64 解码）或无头浏览器。
2. **GitHub core API 未登录限额 60 次/小时** —— 批量验证仓库前先列好清单，一次循环跑完；超限返回 `{"message":"API rate limit exceeded"}`（含 message 无 content）。
3. **grep.app 对自动化访问挂 Vercel 盾** —— 2026-10-14 curl 与无头浏览器均吃 Security Checkpoint；代码搜索优先 GitHub `search/code`。
4. **bot 没有消息搜索端点** —— 各类 MCP 服务器的 `search_messages` 均为拉最近 N 条本地过滤（默认 200 条），不能当服务端搜索用。
5. **selfbot / user-token 工具违反 Discord ToS** —— KanekiWeb/Messages-Searcher 把用户 token 写进 config.txt 扫全频道，有封号风险；仅用于自账号并降频率。
6. **已删消息只能靠提前记录找回** —— 持续归档选 DHT 或日志机器人，事后工具无能为力。
7. **GitHub 搜索页 `get text` 可能为空但 `snapshot` 正常** —— 虚拟列表/aria 结构导致 text 提取丢失，snapshot（含 ref）更可靠。

## 未核实 / 存疑

| 项 | 说明 |
|---|---|
| DiscordChatExporter 是否有 SQLite 原生导出 | Contents API 解码 README 时撞限流未确认；已知文档列出 HTML/PlainText/JSON/CSV 四种格式，SQLite 能力由 discord-cli 补足 |
| DHT 离线查看器是否内置全文搜索框 | README 指向官网，dht.chylex.com 两次抓取均失败（fetch failed）；官网文案只确认「离线查看」 |
| 官方搜索运算符的完整清单 | 依据客户端使用经验 + 社区资料，未找到 Discord 官方支持文档单列此表 |
| `/api/v9/guilds/{id}/messages-search` 请求体字段细节 | 多篇 2024 年 CSDN 文章佐证端点存在与返回结构；精确字段（offset/limit/content）未实测 |
| virat-mankali/discord-cli 与 jackwener/discord-cli 的关系 | 网页端搜索还出现同名项目，未比对二者差异 |

## Sources

- GitHub REST API 实测（2026-10-14）：repositories 搜索与 7 个仓库元数据
- 各项目 README（raw.githubusercontent.com）与官网：dht.chylex.com、discorch.org、friendcordapp.com、quark.bot
- mcpworld Discord MCP 条目（2026-10）：bot 无服务端搜索端点
- CSDN 2024 年文章 ×2：`/api/v9/guilds/{guildId}/messages/search` 端点佐证
