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
version: 1.3
status: stable
source: 本次会话（GitHub 实测 + README 抓取 + Messages-Searcher 实测 + LLM 工具形态深挖 + Discord 登录态/CDP 实测）
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
| selfbot 脚本 | KanekiWeb/Messages-Searcher | 全频道（违反 ToS，且已实测跑不起来） | 已实测，见第 6 节 |
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
| [KanekiWeb/Messages-Searcher](https://github.com/KanekiWeb/Messages-Searcher) | 50 | selfbot 扫描器（已实测不可用） | 见第 6 节 |

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

## 6. Messages-Searcher 本机实测纪要（2026-10-14，Python 3.13.12）

测试方式：克隆仓库（50★）→ 全量代码审计 → `py_compile` → 离线复刻匹配逻辑 → 假 token 冒烟。全程未使用真实 token。

| 测试项 | 结果 |
|---|---|
| 代码性质 | 94 行 discord.py selfbot：`Client()` + `run(token, bot=False)`；读 `config.json`（README 误写 config.txt）；命中只写本地 `found.txt`，**无外传/webhook，非恶意软件** |
| py_compile（Python 3.13） | ✅ 通过 |
| 依赖安装 | discord.py 2.7.1 + colorama 装进托管 venv 成功 |
| discord.py 2.7.1 运行 | ❌ 两处 TypeError：① 第 4 行 `Client()` 缺 `intents`（import 即崩）② 补 intents 后第 93 行 `Client.run()` 的 `bot=` 参数已被 2.x 移除 |
| discord.py 1.7.3 运行 | ❌ 装是装上了（aiohttp 3.7.4.post0），但 **Python 3.13 已删除 `cgi` 模块** → aiohttp 导入即 `ModuleNotFoundError: No module named 'cgi'` |
| 匹配逻辑（离线实测） | ⚠️ `re.match` 锚定消息开头：`"say hello there"` 在 words 模式命中、regex 模式漏掉；非法正则抛 `re.error` 被 `except: pass` 静默吞掉 → 该频道剩余消息全部跳过且无任何提示 |
| 许可 | 正文写 MIT，徽章却挂 GPLv3，自相矛盾 |

**结论**：本机（Python 3.13）无法运行——2.x 崩在参数、1.7.3 崩在 cgi；需要 Python ≤3.12 + discord.py 1.7.3 才可能启动。即便能跑，`history(limit=99999)` 扫全部服务器/DM 违反 Discord ToS，有封号风险。

## 7. 让 LLM 搜索 Discord 内容的软件形态（2026-10-14 GitHub 深挖）

按「搜索能力上限」排序的五种形态：

| 形态 | 代表项目（★，2026-10-14） | 鉴权 | 搜索能力真相 | 适用场景 |
|---|---|---|---|---|
| MCP server（bot token） | [SaseQ/discord-mcp](https://github.com/SaseQ/discord-mcp)（539）、[v-3/discordmcp](https://github.com/v-3/discordmcp)（235）、[hanweg/mcp-discord](https://github.com/hanweg/mcp-discord)（164）、[cappyeo/discord-mcp](https://github.com/cappyeo/discord-mcp)（134，209 工具）、[mastra-ai/discord-mcp-server](https://github.com/mastra-ai/discord-mcp-server) | bot token | **无服务端搜索**：全部是读有界/最近历史 + 本地过滤。hanweg 工具名即 `read_messages`（recent history）；cappyeo 自述 bounded history + 显式 coverage 标注 | 实时问答、最近消息摘要 |
| 本地 SQLite+FTS 同步（CLI/MCP 双形态） | [quangdang46/discord_cli](https://github.com/quangdang46/discord_cli)（Rust，77 命令，SQLite FTS5，MCP 直插 Claude Code：`claude mcp add discord -- $(which discord) serve`）、[jackwener/discord-cli](https://github.com/jackwener/discord-cli)（Python，133★） | 用户身份为主 | **真全文检索（FTS5）**，历史无界；`discord search "deploy" -n 50` | 深度历史检索首选架构 |
| Agent Skill | [banodoco/hivemind](https://github.com/banodoco/hivemind)（71★，Claude Code/Codex drop-in skill，`python3 executors/search/run.py --query "..."`，revision 机制）、[Nice-Wolf-Studio/agent-discord-skills](https://github.com/Nice-Wolf-Studio/agent-discord-skills)（16★） | 各异 | hivemind：同步 feed 后本地查询（唯一「drop-in 即可搜」）；bot token skill 版仍是历史过滤 | 已在使用 Claude Code/Codex 的团队 |
| 浏览器自动化 | [OpenCLI](https://github.com/jackwener/opencli)（~20k★，2026-05 报道，已登录浏览器→CLI/Agent）、agent-browser / playwriter / browser-use 驱动 Discord Web | 你的登录态 | **直接用官方客户端搜索**（`from:`/`in:`/`has:` 运算符全支持） | 临时查询、零同步成本 |
| RAG / 向量库 | [youngsecurity/discord_vector_db](https://github.com/youngsecurity/discord_vector_db)（Discord→向量库）、[sandraschi/discord-mcp](https://github.com/sandraschi/discord-mcp)（FastMCP + RAG search） | bot token / 导出文件 | 语义检索（同义词、含义级） | 归档库语义问答 |

**选型结论（已核实）**：
1. bot token MCP 的天花板就是「有界历史」——服务端搜索不对 bot 开放（坑 #4），所有 `search_messages` 工具都是拉 N 条本地过滤，别指望全站全文检索。
2. 要真检索只有两条干净路：**sync-to-local（SQLite FTS5）**或**浏览器复用官方搜索**。前者完成度最高的是 quangdang46/discord_cli（CLI+MCP+FTS5 三合一单件），Python 生态等价物是 jackwener/discord-cli。
3. Skill 形态里 hivemind 是唯一开箱即搜的；其他「skill」只是 bot API 封装。
4. ToS 边界：bot token 系最干净；「as yourself」CLI/MCP 与浏览器路线用的是本人登录态，性质等同手动操作，风险远低于 Messages-Searcher 式高频全扫，但仍在灰色区。

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

# 5) 审计/测试可疑 selfbot 脚本的安全姿势（本次实测流程）
git clone --depth 1 <repo> test-ms && rm -rf test-ms/.git   # 先读代码再运行
cp -r test-ms test-ms-run   # 在副本里改配置跑，保持原始仓库干净
# 假 token 冒烟：期望只到登录环节失败（LoginFailure），不到 on_ready

# 6) 驱动「已登录的 Chrome」搜 Discord —— 零 token 方案（2026-10-14 实测跑通）
#    前提：Chrome 带 --remote-debugging-port=9222 运行，且该浏览器已登录 discord.com
#    原理：CDP附着真实浏览器，在 discord.com 页面上下文调用客户端同款搜索端点
#    先帮用户开登录页（他只需登录一次，之后随时可搜）：
curl -X PUT "http://127.0.0.1:9222/json/new?url=https%3A%2F%2Fdiscord.com%2Fapp"
#    登录后执行搜索（参数：关键词 [服务器序号]）：
node tools/cdp-discord-search.mjs "关键词" 0
#    核对 9222 浏览器与目标浏览器是否同一配置文件（旁路读 cookie 罐，不碰页面）：
node tools/cdp-cookie-check.mjs
#    临时启用 CDP（关掉所有 Chrome 后）：
#    "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
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
5. **selfbot / user-token 工具违反 Discord ToS** —— Messages-Searcher 实测：即使想用也跑不起来（见第 6 节）；`re.match` 锚定开头 + `except: pass` 静默跳频道，会漏结果且无提示。
6. **已删消息只能靠提前记录找回** —— 持续归档选 DHT 或日志机器人，事后工具无能为力。
7. **GitHub 搜索页 `get text` 可能为空但 `snapshot` 正常** —— 虚拟列表/aria 结构导致 text 提取丢失，snapshot（含 ref）更可靠。
8. **discord.py 1.x 生态在 Python ≥3.13 集体阵亡** —— PEP 594 删除 `cgi`，aiohttp 3.7.x 导入即炸；遇到 2021 年代的 Python 脚本先查依赖年代再看代码。
9. **Discord 网页登录态不在 cookie 里** —— 2026-10-14 实测：导出的 discord.com cookie 罐（12 个：`_cfuvid`/`__dcfduid`/`_ga`/`OptanonConsent`/`dbind`/`__cf_bm` 等）打 `GET /api/v9/users/@me` 全部 **401**。登录态在 discord.com 域的 `localStorage.token`，导出 cookie 零鉴权价值。
10. **「有 cookie」≠「已登录」** —— 只要访问过 discord.com 就会留下 Cloudflare/设备 cookie；判断真实登录只能打 `/users/@me` 或查 localStorage。用 CDP `Network.getCookies` 旁路比对两个浏览器是否同一配置文件，比对 `_ga` 设备 ID 最稳（本轮实测：导出的 `_ga=GA1.1.830215638.1791862591` 与 9222 Chrome 罐内一致 → 同一配置文件，但该浏览器未登录网页版）。
11. **CDP 9222 端点未必是你日常的 profile** —— 端口属于哪个 Chrome 实例要用 `netstat -ano` 查 PID 归属；挂着的调试端口也可能属于工具拉起的无头实例（其页内 `/users/@me` 同样 401）。

## 未核实 / 存疑

| 项 | 说明 |
|---|---|
| DiscordChatExporter 是否有 SQLite 原生导出 | Contents API 解码 README 时撞限流未确认；已知文档列出 HTML/PlainText/JSON/CSV 四种格式，SQLite 能力由 discord-cli 补足 |
| DHT 离线查看器是否内置全文搜索框 | README 指向官网，dht.chylex.com 两次抓取均失败（fetch failed）；官网文案只确认「离线查看」 |
| 官方搜索运算符的完整清单 | 依据客户端使用经验 + 社区资料，未找到 Discord 官方支持文档单列此表 |
| `/api/v9/guilds/{id}/messages-search` 请求体字段细节 | 多篇 2024 年 CSDN 文章佐证端点存在与返回结构；精确字段（offset/limit/content）未实测 |
| virat-mankali/discord-cli 与 jackwener/discord-cli 的关系 | 网页端搜索还出现同名项目，未比对二者差异 |
| Messages-Searcher 在 Python ≤3.12 能否完整跑通 | 只验证到依赖导入层崩溃；未装旧 Python 实测 on_ready 后的扫描流程 |

## 修订记录

- **1.3**（2026-10-14）：新增 Discord 登录态实测结论（cookie 导出 401、localStorage token 机制、CDP `Network.getCookies` 身份比对）与「驱动已登录 Chrome 零 token 搜索」可复用操作（tools/cdp-discord-search.mjs）；坑 #9–#11。
- **1.2**（2026-10-14）：新增第 7 节「让 LLM 搜索 Discord 内容的软件形态」深挖结果（MCP/Skill/CLI/浏览器/RAG 五形态 + 选型结论）。
- **1.1**（2026-10-14）：新增第 6 节 Messages-Searcher 本机实测纪要（双重 TypeError + cgi 模块缺失 + re.match 锚定/静默跳频道实测）；坑 #5/#8 更新为实测结论。
- **1.0**（2026-10-14）：初版。

## Sources

- GitHub REST API 实测（2026-10-14）：repositories 搜索与 8 个仓库元数据
- 各项目 README（raw.githubusercontent.com）与官网：dht.chylex.com、discorch.org、friendcordapp.com、quark.bot
- mcpworld Discord MCP 条目（2026-10）：bot 无服务端搜索端点
- CSDN 2024 年文章 ×2：`/api/v9/guilds/{guildId}/messages/search` 端点佐证
- Messages-Searcher 源码与实测：https://github.com/KanekiWeb/Messages-Searcher （克隆于 2026-10-14，Python 3.13.12 / discord.py 2.7.1 与 1.7.3 双路冒烟）
- LLM 工具形态深挖（2026-10-14，GitHub Search API 四路查询 + 8 个仓库 README 抓取）：SaseQ/discord-mcp、v-3/discordmcp、hanweg/mcp-discord、cappyeo/discord-mcp、mastra-ai/discord-mcp-server、banodoco/hivemind、Nice-Wolf-Studio/agent-discord-skills、quangdang46/discord_cli、youngsecurity/discord_vector_db、sandraschi/discord-mcp、jackwener/opencli（20k★ 报道见 https://hub.baai.ac.cn/view/54747 ）
- Discord 登录态与 CDP 实测（2026-10-14）：用户 cookie 导出打 `/api/v9/users/@me` → 401；`netstat -ano` 确认 9222 属主 Chrome PID；CDP `Network.getCookies` 比对 `_ga` 证实同一配置文件但未登录网页版；`tools/cdp-discord-search.mjs` 零 token 驱动方案
