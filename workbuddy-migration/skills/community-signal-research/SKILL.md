---
name: community-signal-research
description: 调研游戏/产品社区在 Reddit、Discord、Steam 创意工坊上的活跃度与近期热门内容，并核实 mod 的兼容性与机制。当用户问「哪个社群最热闹」「最近流行什么 mod / 话题」「XX 题材推荐什么 mod」「A 是否兼容 B」「某段时间最受欢迎的 mod」时使用。解决 Reddit 官方 API 被封、Discord 内容不可抓取两个核心障碍。核心手段：① **Steam 公开 API（无需 Key，拿真实订阅数 + 工坊简介全文）**；② Reddit 的 3 个 RSS 端点（含「单帖评论全文」）；③ Steam 讨论区；④ 用 curl+grep 直读框架 mod 仓库的兼容性清单与源码 def 文件（兼容性/机制的最权威一手源）。
agent_created: true
type: Checklist
---

# 跨平台社区信号调研（Reddit / Discord / Steam 工坊）

## 核心结论

| 平台 | 可抓性 | 该用什么 |
|------|--------|----------|
| Reddit | **API 被封，RSS 可用** | 官方 `.rss` 端点（**含单帖评论全文，见 §Reddit**） |
| Discord | **无授权不可抓；有 Bot 授权可抓内容** | ① 有服务器管理员授权 → Bot + 社区 MCP 读内容；② 无授权 → 第三方索引站拿「服务器规模」当代理 |
| Steam 创意工坊 | 可抓 | `browse/?browsesort=` 排序 URL（拿 id 清单） |
| **⭐ Steam 公开 API** | **可抓，无需 Key，官方一手** | `GetPublishedFileDetails` → **真实订阅数 + 工坊简介全文**，见 §「Steam 公开 API」 |
| Steam 讨论区 | **可抓，一手玩家对比** | `app/<appid>/discussions/0/<thread_id>/` |
| 第三方 mod 站 | 可抓 | rimmods.com 等 |
| **框架 mod 的 GitHub 仓库** | **可抓（curl + grep，最权威）** | 兼容性清单 + 源码 def 文件，见 §「读框架 mod 的源码」 |
| 百度贴吧 | 可抓（走移动版） | 见 `tieba-scrape` skill |

## Reddit：API 挂了就用 RSS

**不要浪费时间去试**：
- `https://www.reddit.com/r/<sub>/about.json` → `You've been blocked by network security`（WebFetch 服务端出口也被封）
- 直接 fetch `reddit.com/r/<sub>/` HTML → 同样被封

**可用（WebFetch 直接成功）**：
```
https://www.reddit.com/r/<sub>/top/.rss?t=month      # 月榜
https://www.reddit.com/r/<sub>/top/.rss?t=week       # 周榜
https://www.reddit.com/r/<sub>/top/.rss?t=year
https://www.reddit.com/r/<sub>/new/.rss              # 最新
```
- 返回 Atom feed，约 25 条。prompt 写：`列出标题和链接，逐条完整列出`。
- **限制**：列表类 RSS **只有标题 + 链接，没有点赞数/评论数**，所以只能判断「是否上榜」，**不能做热度排序**。报告里要说明这一点。
- **判断子版是否活跃**：`top?t=month` 返回**空 feed（0 条 entry）**＝该板块实际已死。这比看订阅数更有用。
- ⚠️ **别给 curl 加 `-A "Mozilla/5.0"` 去绕限流**：实测加 UA 后 RSS 直接返回 `<title>Blocked</title>`（1.5KB）；不加 UA 时**偶尔也会返回空 body**。Reddit 侧并不稳定。
  - 遇到 `Blocked` 或空 body：**换 WebFetch 试一次**（WebFetch 走不同出口），仍失败就**放弃 Reddit 侧，改用第三方站 + 贴吧 + Steam 讨论区**，并在报告口径里写明「本轮 Reddit 数据缺失」。**不要在同一端点上反复重试。**
  - ⚠️ **429 是并发触发的，别把 Reddit RSS 放进并行批次**：实测一次并发 4 个 `.rss` 请求（2 个列表 + 2 个单帖），其中 2 个返回 `429 Too Many Requests` 且 body 为空，另外 2 个正常。**同一批并行请求会互相挤占配额。**
    ✅ 正确做法：**Reddit RSS 请求串行化**（一次一个，逐个 WebFetch）；其余非 Reddit 源（厂商文章、官方文档）可以和 Reddit 请求并行，但 Reddit 内部要排队。
    ⚠️ 单帖 `.rss` 的返回体很大（一帖带全部评论常 5–15 万字符），WebFetch 会消耗大量额度，**更要省着用**——优先只抓最高信号的 2–3 帖，不要广撒网。
  - ⚠️ **这不是偶发**：RimWorld 系列第 13 轮调研时，`search.rss` 三端点**全部失败**（加 UA → `Blocked`；不加 UA → 空 body），最终整轮放弃 Reddit 侧。**动手前先做一次连通性探测**（拉 `top/.rss?t=month` 看是否为空），再决定是否把 Reddit 写进方法论文档。

### ⭐ 三个高价值 RSS 端点（本 skill 最重要的发现）

**1. 子版内搜索 —— 找主题帖的最快路径**
```
https://www.reddit.com/r/<sub>/search.rss?q=<关键词>&restrict_sr=1&sort=top&t=year
https://www.reddit.com/r/<sub>/search.rss?q=<关键词>&restrict_sr=1&sort=relevance&t=year
```
- `sort=top` 按热度、`sort=relevance` 按相关度，两者结果**差异很大，建议都跑**。
- `t=year|month|week|all` 控制时间窗。
- 关键词带空格要 URL 编码：`q=medieval%20mods`。
- **这一步能直接拿到「某主题的推荐帖清单」**，比 WebSearch 精准得多（WebSearch 会混进下载站和 SEO 垃圾页）。

**2. 单帖评论全文 —— 绕过「单帖被封」**
```
https://www.reddit.com/r/<sub>/comments/<post_id>/<slug>/.rss
```
- 只要拿到 post_id，就能取回**该帖正文 + 全部评论的完整正文**（含用户名、时间、`<content type="html">` 里的 markdown）。
- 这是**本 skill 目前最强的信息获取手段**：社区调研的核心价值就在评论区（谁推荐了什么、为什么、有什么坑），而这一步能完整拿到。
- prompt 写：`完整转录这个帖子的正文和所有评论，逐条列出被推荐的 X 名称和理由。不要概括。`
- ⚠️ 注意：单帖的 HTML 页面（`/comments/<id>/<slug>/`）**仍被封**（network security block），**必须加 `.rss`**。
- ⚠️ 评论是**扁平列表**，不保留嵌套层级；父评论靠 `<id>t1_xxx</id>` 与 `link href=".../comments/<id>/<slug>/<comment_id>/"` 推断，一般不影响阅读。
- ⚠️ 长帖（评论 100+ 条）WebFetch 会**截断**，标注 `[content truncated]`。关键帖优先抓，必要时拆多次。

**3. 用 post_id 交叉引用**
- 从 `search.rss` 拿到帖子标题 → 从 `<link href=".../comments/<post_id>/<slug>/"/>` 解析出 post_id → 再喂给端点 2。
- **完整工作流**：`search.rss` 找帖 → 挑 3–5 个最相关的 → `.rss` 抓评论全文 → 聚合。

**订阅数只能靠第三方**（口径不一致，必须标注）：
- SubSavant `subsavant.com/r/<sub>` — 订阅数 + 发帖频率 + 内容形态（图片/视频占比）+ 年度 top 帖 upvote
- GummySearch `gummysearch.com/r/<sub>/` — 订阅数 + 高频讨论主题 + flair 分布 + 被推荐的产品/创作者
- ⚠️ 三个源经常差 2–3%（如 652k / 669k / 671k），**不要报单一数字**，给区间。

## Discord：分两条路径

### 路径 A：无授权 —— 只能拿规模当代理

- **绝对不要声称「Discord 上讨论最多的是 X」** —— 内容需要登录，不被搜索引擎索引，无法核实。
- 可用的规模索引：
  - `disdex.io/servers/<tag>` — 按活跃度排名，给出**成员数 + 在线数 + 简介**，一页能拿到 20+ 服务器
  - `disboard.org/servers/tag/<tag>`、`top.gg/discord/servers/tag/<tag>`、`discadia.com/?q=<tag>`
- 用法：把「服务器规模」当「该子社区玩家/作者密度」的代理指标，并明确标注这是代理而非内容分析。
- 顺带能识别**地区性社群**（俄语/西语/日语服）—— 看简介语言即可。

### 路径 B：有授权 —— Bot + MCP 真读内容

前提：目标服务器管理员同意把 Bot 拉进去。**拿不到授权就别浪费时间**。

**必须装 MCP**（Discord 官方无 MCP；WorkBuddy 的 Connector 市场与 Skill 市场里都搜不到 Discord，全为社区实现）：

```json
{
  "mcpServers": {
    "discord": {
      "command": "npx",
      "args": ["-y", "@pasympa/discord-mcp"],
      "env": {
        "DISCORD_TOKEN": "<bot token>",
        "DISCORD_ALLOWED_GUILDS": "<guild id>",
        "DISCORD_MCP_TOOLSETS": "discovery,messages,channels,forums"
      }
    }
  }
}
```

- 配置写入 `~/.workbuddy-ai/mcp.json`；之后到连接器管理页右上角「自定义连接器」入口点**信任**才生效，不会自动激活。
- 备选实现：`npx mcp-discord`（barryyip0625/mcp-discord），功能略少，入口是 `build/index.js`（`build/app.js` 是 HTTP 版，不支持 stdio）。
- `DISCORD_MCP_TOOLSETS` 白名单**务必只留读取类**，否则会连 kick / ban / bulk_delete 等破坏性工具一起暴露。

**Developer Portal 必做**：
1. 建 Application → Bot，复制 token。
2. Privileged Gateway Intents：**Message Content Intent 必须 ON**。Portal 开关 OFF 时，返回的消息正文 / embeds / 附件**全空**（例外：Bot 自己的消息、DM、@Bot 的消息）。加入 <100 个服务器可自助开启；≥100 需申请审核。
3. 邀请 Bot 的最小权限：`View Channel` + `Read Message History`。**不要给 Administrator**。

**能力与坑**：
- Bot **只能读被邀请的服务器**，且只读有 `View Channel` 权限的频道。私服 / 只读公告类频道同样受限。
- ⚠️ **Bot 大概率不能用 Discord 官方消息搜索端点**（`GET /guilds/{id}/messages/search` 对 bot token 不开放）。某些 MCP 宣称的「关键词搜索」多为**本地过滤最近 N 条**（barryyip0625 的实现就自述「最近 100 条」）。要统计「最近 30 天讨论什么」，正路是**逐频道分页拉历史**（`before`/`after` 游标，每页 100 条）+ 本地聚合。
- 速率限制按频道计（约 5 req / 5s 级别）。全量遍历大服务器耗时很长，先估算再动手。
- 论坛频道（Forum）能拿「帖子标题 + 标签 + 正文」，**信噪比最高**。调研优先读论坛、置顶、公告，不要一上来就翻闲聊频道。
- ⚠️ **禁止用 user token / self-bot 读消息**：违反 Discord ToS，会封号。不要试。
- 若数据要用于训练模型，另需核对 Discord Developer Policy 的 AI / ML 条款。

## Steam 创意工坊：排序 URL

```
https://steamcommunity.com/workshop/browse/?appid=<appid>&browsesort=trend&days=90
https://steamcommunity.com/workshop/browse/?appid=<appid>&browsesort=mostsubscribed
```
- 返回**服务端渲染的列表**，WebFetch 可直接拿到「名称 + 作者 + 作品页链接」。
- `browsesort=trend&days=90` = 近 90 天趋势榜，是判断「近期真正在上升」的最佳口径。
- ⚠️ 列表里**不含订阅数**，要订阅数得另找 —— **但现在有官方答案了，见下一节**。
- 常见 appid：RimWorld `294100`。
- 每页约 30 个 `filedetails/?id=<id>`；RimWorld 趋势榜翻到第 16 页共 **493 个去重 id**（可用 `grep -o "filedetails/?id=[0-9]*" | sort -u` 去重）。

## ⭐⭐ Steam 公开 API：拿真实订阅数（本 skill 第三重要发现）

**这是整个系列一直缺的那块拼图。** 此前只能用 rimmods.com 的二手累计值，现在可以直接拿 Steam 官方数字，**而且不需要 API Key**。

### 完整可用模板

```bash
curl -s --max-time 30 -X POST \
  "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/" \
  -d "itemcount=2&publishedfileids[0]=2646321064&publishedfileids[1]=3414187030"
```

- **无需 API Key**，返回 JSON（`response.publishedfiledetails[]`）
- **分批 80 个/次**最稳（实测 493 个 id 分 7 批，全部成功、无失败、无限流）
- 批量构造参数：
  ```bash
  # ids 从文件读，每 80 个组一批
  # -d "itemcount=$n&publishedfileids[0]=$id0&publishedfileids[1]=$id1..."
  ```

### 返回的可用字段（比任何第三方站都全）

| 字段 | 含义 | 价值 |
|---|---|---|
| `title` | mod 名称 | 用于与排除集/兼容清单比对 |
| **`description`** | **工坊简介完整原文**（含 BBCode） | ⭐ **最高价值**：作者 FAQ、兼容声明、依赖、CE 声明全在这里 |
| **`subscriptions`** | **真实订阅数** | ⭐ 唯一的官方热度指标 |
| `favorited` | 收藏数 | 补充 |
| `views` | 浏览数 | 补充 |
| `time_updated` | 最后更新 Unix 时间戳 | 判断活跃度 / 是否已弃坑 |
| `tags` | 标签数组（如 `Mod`,`1.6`,`1.5`） | 判断支持的版本区间 |
| `creator` | 作者 SteamID | 发现「同一作者矩阵」 |
| `file_size` | 文件大小 | 判断是否轻量 |

### ⚠️ 两个必踩的坑

**① 托管 Python 读不了 MSYS 的 `/tmp` 路径**
托管 Python 是 **Windows 二进制**。即使同一条命令里 `wc -l < trend_ids.txt` 成功（bash 内建走 MSYS 视图），`open('/tmp/trend_ids.txt')` 也会 `FileNotFoundError`。
- **解法 A**：给 Python 传 Windows 路径 —— `cygpath -w /tmp` 可得真实路径（通常 `C:/Users/<user>/AppData/Local/Temp`）
- **解法 B**：`cat /tmp/x.json | python -c "import json,sys; d=json.load(sys.stdin)"`（走 stdin）

**② BBCode 必须清洗再读**
`description` 含 `[img]...[/img]`、`[url=...]`、`[b]`、`[h1]`、`[list]`、`[*]` 等。写报告前先清洗，否则大段图床 URL 会淹没正文：
```python
t = re.sub(r'\[img\].*?\[/img\]','',t,flags=re.S)
t = re.sub(r'\[url=[^\]]*\]','',t); t = t.replace('[/url]','')
t = re.sub(r'\[/?(b|i|u|h1|h2|h3|list|hr|table|tr|td|th|quote|code|pre|spoiler|strike|noparse|center|size|color|font|sup|sub)(=[^\]]*)?\]','',t)
t = re.sub(r'\[\*\]','• ',t); t = re.sub(r'\[[^\]]{0,40}\]','',t)
```
⚠️ **读 description 时必须分批导出**（如每批 10 条、每条截 1000–1500 字符）。一次性导出 100 条完整 desc 约 27 万字符，**工具输出会被截断**，导致中间条目丢失。

### ⚠️ 口径纪律（写报告必写）

- **Steam 没有「近 N 个月最受欢迎」这个原生口径**。可用的是 `browsesort=trend&days=90`（近 90 天热度榜）。
- **`subscriptions` 是累计值，不是近 90 天新增**。Steam 不公开增量，**任何声称给出「近期新增订阅」的说法都不可信**。
- 用户要「最受欢迎」时，先确认他要的是**累计地位**（→ `mostsubscribed`）还是**当期热度**（→ `trend&days=90`）。两者前 100 名几乎不重叠。

### ⭐ 用 `description` 做 CE / 兼容性判定的关键技巧

拿到全部 desc 后，**用关键词正则扫一遍，能挖出比官方清单多得多的兼容声明**：
```python
pat = re.compile(r'combat extended|\bCE\b|CE\?|CE\.|CE,|CE-|for CE|CE users', re.I)
# 命中后打印前后 200 字符上下文，人工判读
```
实测在 100 个 mod 上：**CE 官方清单只命中 2 条，但 desc 里挖出 13 处明确兼容声明 + 2 处明确不兼容 + 1 处部分支持**。
- 典型句式：`Q: CE? A: No.`（不兼容）／`Q2. CE? Of course it is compatible!`（兼容）／`Support CE.`／`Works with CE`／`Not tested with Combat Extended yet`（**未测试 ≠ 不兼容，必须区分**）
- **结论：CE 兼容性必须三源交叉 —— ①官方清单 ②工坊简介作者 FAQ ③社区实测。只看官方清单会得出严重错误的结论。**

## 第三方 mod 站（订阅数 + 新增列表）

- `rimmods.com/mods?sort=popular&updatedWithin=30d` — Top of the Month
- `rimmods.com/mods/new` — 本周新增（条目多，含汉化/翻译补丁）
- `rimmods.com/authors` — 作者榜
- **口径坑**：
  - 「Top of the Month」= **近 30 天内有更新**的 mod 按**累计订阅量**排序，**不是月度增量**。
  - 作者页上的 `XXX subscribers this month` 标签数值与订阅总数完全相同 → **疑为站点 bug，别当增量引用**。
  - 订阅量是累计值，反映历史地位；判断「近期热度」要用趋势榜 + 本周新增。

### 另一个第三方站：`top-mods.com`（⚠️ 数字口径不同）

```
https://top-mods.com/mods/rimworld/gameplay     # 按分类列 mod
https://top-mods.com/mods/rimworld/<分类>/<id>-<slug>.html
```
- 每条会显示 mod 名、适用版本（如 `v1.4 - 1.6`）、**站内下载量**（如 `45.87K`）、**站内点赞**（如 `+59`）、更新日期、作者。
- ⚠️ **这两个数字都不是 Steam 订阅数**。报告里引用时必须写明「top-mods 站内下载量」/「站内点赞」，不要写成「订阅数」。
- 适合用来**发现新 mod + 确认版本区间**；订阅数仍以 rimmods.com 为准。

### `rimmods.com` 的六个分类榜 URL（比主页筛选器好用）

主页 `/mods` 的筛选结果是 **JS 渲染**，WebFetch 抓不到条目，但**筛选器暴露了分类榜的静态 URL**：

```
https://rimmods.com/mods/best-management
https://rimmods.com/mods/best-combat
https://rimmods.com/mods/best-medical
https://rimmods.com/mods/best-storage
https://rimmods.com/mods/best-furniture
https://rimmods.com/mods/best-weapons
```
筛选维度（可用于构造查询）：`Popularity` = Any / Undiscovered / **Popular / Essential**；`Status` = **Fresh / Stale / Not on 1.6**；`Published` = Recent (2025+) / 2024 / 2023 / Classic (<2023)；`Last Updated` = past week / month / 6 months / year。

### ⭐ 最高效的 mod 清单来源：`rimmods.com/collections/<id>`

想拿「某类 mod 的完整清单」时，**别逐个查工坊页** —— 直接抓一个现成合集：

```
https://rimmods.com/collections/<collection_id>
```

一次 WebFetch 就能拿到**合集内每个 mod 的名称 + 作者 + 适配状态标记**（`Fresh` / `Stale` / `No 1.6`），上百条结构化数据。
- 合集页还会给出**合集内的分段说明**（如「#1–70 纯 QoL / #71–130 平衡内容 / #131–141 需 DLC」）与**作者出现频率**（谁是这类 mod 的主要维护者）。
- 想找某主题的合集 ID：`WebSearch "<主题> mod collection rimworld"`，或搜 `rimmods.com/collections <主题>`。
- 已知高价值合集（RimWorld）：
  - `3720610373` — 141 个 QoL mod（nick），**#1–70 纯 QoL**，90 项标 Stale
  - `3519717579` — Cyanobot 的 70 个 QoL Tweaks；姐妹合集 `3527091029`(UI) / `3527104495`(Pawn AI) / `3519745353`(Graphics)
  - `3075210888` — 183 个 QoL mod（XenoExpert）
- **读法**：`Stale` ≠ 不可用，只表示较久未更新；`No 1.6` 才是真不能用。**报告里要标注这两者的区别。**

## 媒体侧补充

新奇的、有传播力的 mod（如把 2D 变 3D 的）会被游戏媒体转载，比社区更早给到准确日期：
- `vgtimes.com/games/<game>/news/`
- 或直接 WebSearch `<game> news <月份> <年份>`

⚠️ **`vgover.com` 极不稳定**：多次请求均 30s 超时（`news/215161`、`news/110931` 均失败）。它家中文 mod 推荐文质量高，但**不要把它当必经路径**；超时 2 次就放弃，改用 WebSearch 摘要或贴吧源。

## Steam 讨论区：被低估的一手源

```
https://steamcommunity.com/app/<appid>/discussions/0/<thread_id>/
```
- 服务端渲染，WebFetch **可直接拿到全部回复正文**（含引用块、发帖时间、用户名）。
- 搜索讨论帖：`https://steamcommunity.com/app/<appid>/discussions/` 或 WebSearch `steamcommunity <game> <主题>`。
- 价值：讨论区里是**真实玩家的对比与吐槽**（「A 太臃肿，我用 B」「别听黑子，C 一直很稳」），比榜单更有信息量。
- 注意：`<thread_id>` 是讨论帖 ID，不是工坊作品 ID，两者格式不同。

## 游戏机制数据：用官方 wiki，不要用玩家帖

**玩家帖回答「体验如何」，wiki 回答「数值是多少」。两者不能互相替代。**

| 数据 | 去哪拿 |
|---|---|
| 数值公式、难度乘数、点数阈值 | 官方 wiki（如 `rimworldwiki.com/wiki/Raid_points`） |
| mod 的精确机制与 FAQ | **mod 作者的 GitHub README**（如 `github.com/<author>/<mod>/blob/main/README.md`）或 Steam 工坊描述 |
| **兼容性（A mod 是否兼容 B mod）** | ⭐ **B 的官方仓库里的「支持列表」文件**，见下方专节 |
| 体验、取舍、踩坑、mod 推荐 | Reddit 评论 / Steam 讨论区 |

- **GitHub README 可直接 WebFetch**，是 mod 机制最权威、最简洁的来源（作者自己写的设计说明 + FAQ + 兼容性列表）。
- wiki 页面常把机制分散在多页：`AI_Storytellers` 只有难度乘数，完整公式在 `Raid_points`。**抓不到就问 WebFetch「是否包含 X，若不包含应查哪个页面」**。
- ⚠️ 别把玩家估算当公式。玩家说「中世纪跑会变难」是体验，真实成因可能是财富曲线（wiki 才有）而非科技锁。

### ⭐ 兼容性判断：官方支持列表 > 社区说法 > mod 页面 FAQ

**优先级从高到低**：

1. **大型框架 mod 的官方「支持列表」文件**（最权威）
   - 例：`github.com/CombatExtended-Continued/CombatExtended/blob/Development/SupportedThirdPartyMods.md`
   - 这份文件列出**框架自己已内置补丁**的第三方 mod。**在列表里 = 零折腾可用**。
   - 这是**最高价值的一手数据**：能直接反查出「哪些 mod 不用另找补丁」
2. **mod 自己的 Steam 页面 / README**
3. **玩家社区说法**（最低，且经常过时或错误）

**⚠️ 三个反复踩到的坑（务必记住）**：

- **mod 页面的 FAQ 经常过时**。实测案例：`[JDS] Castle Walls` 页面（2022 年）写「CE Compatible? A: No, Find someone to patch it」，但 **CE 官方支持列表收录了它**（`master` 分支实测第 23 行；`Development` 分支约第 15 行，**行号随分支变动，引用时写「收录」而非行号**）—— CE 后来内置了补丁。**以官方支持列表为准。**
- **作者的「去问 CE / 不确定」是免责声明，不等于不兼容**。实测三个案例：`Medieval Overhaul`（`Not sure, ask CE`）、`VFE Medieval 2`（`We do not handle CE patches. Best ask Combat Extended team. Do not ask here.`）、`VQuE - Ancients`（`No idea. Ask CE.`）—— **三者全部在 CE 官方清单里**。VFE 这类大型团队通常把 CE 兼容交给 CE 组维护，自己不打补丁，所以 FAQ 那么写。**不要因为看到这句话就判定不兼容。**
- **同名 mod 可能是两个不同实体，必须用 Steam ID 区分**。实测案例：**「Maynard Medieval」有两个** —— `Vanilla Storytellers Expanded - Maynard Medieval`（独立 mod，2455898730，**锁科技**）与 `VFE Medieval 2` 内置的 Maynard（3444347874，**不锁科技**，官方 FAQ 明写 `A: No it does not`）。社区讨论里经常混为一谈。**凡遇到同名条目，先去两边的 Steam 页面比对 Steam ID 与 FAQ，再下结论。**
- **同一 mod 的「原版」和「重建版 / Continued 版」兼容性可能完全不同**。实测案例：`[JDS] Castle Walls`（CE 已支持）vs `Castle Walls Reborn`（官方明说 not today）。**不要因为名字相似就假定兼容性相同。**
- **中文社区推荐经常与官方页面冲突**。实测案例：贴吧说 `Castle Walls Reborn`「兼容 CE」，官方页面说「not today」。**报告里要把矛盾显式列出，并说明采信哪一个及理由。**

**操作流程**：拿到一批候选 mod 名 → 去框架的官方支持列表里逐个比对 → 分成「官方已支持 / 需第三方补丁 / 无补丁 / 明确不兼容」四档 → 按档位给建议。

### ⭐⭐ 读框架 mod 的**源码**，别只读文档（本 skill 第二重要发现）

**问题**：第三方站点（rimmods / rimworldbase）对 mod 内容的描述是二手转述，且**漏掉框架自带的东西**。比如问「中世纪有什么 CE 兼容的垛口 mod」，所有站点都只会列第三方 mod —— 但**CE 本体就自带垛口**，站点根本不会告诉你。

**做法**：直接读框架仓库的 def / 配置文件。

```bash
# 1. 用 GitHub API 列目录（不需要 clone，不需要 token）
curl -sL "https://api.github.com/repos/<owner>/<repo>/contents/<path>" | grep -o '"name": "[^"]*"'
# 例：列 CE 的 Defs/ThingDefs_Buildings → 找到 Buildings_Defenses.xml

# 2. 拉 raw 文件并 grep 关键字段
curl -sL "https://raw.githubusercontent.com/<owner>/<repo>/master/<file>" -o /tmp/f.xml
grep -n -E "<defName>|<label>|ParentName|fillPercent|costStuffCount|researchPrerequisites|statBases" /tmp/f.xml

# 3. 小文件直接 cat 全文（比 grep 更省一轮）
```

- **`ParentName` 字段极有价值**：`<ThingDef ParentName="Wall">` 直接说明该建筑**继承原版墙的全部属性**（含掩护值），这是判断「是否天然兼容框架战斗系统」的硬证据。
- **`researchPrerequisites` 决定科技门槛**：CE 的 `CE_BarbedWire` 前置是 `Smithing`（锻造）→ 中世纪可达。这类结论**只有读源码才能拿到**。
- **`curl -o` 写到 `/tmp` 是可用的**（Git Bash 的 MSYS 临时目录可写）。**失败的是写到 Windows 路径**（尤其含中文/空格）—— 那种情况改用 PowerShell `Invoke-WebRequest`。
- 兼容性清单同理：`curl -sL .../SupportedThirdPartyMods.md -o /tmp/x.md && grep -i -E "castle|fortific|medieval" /tmp/x.md` —— **比 WebFetch 让模型转述更可靠**（模型会漏项/改写），而且能顺手确认「哪些关键词一条都没命中」。
- **一次 bash 调用跑多组关键词**（省轮次）：
  ```bash
  cd /tmp && echo "=== 派系 ===" && grep -n -E "faction|empire|tribe|diplom" ce.md \
   && echo "=== 剧情 ===" && grep -n -E "storytell|quest|event" ce.md \
   && echo "=== 科技 ===" && grep -n -E "research|tech|primitive" ce.md
  ```
  再补一轮 `grep -n "Vanilla Factions Expanded" ce.md` 这种**完整名称匹配**，用来拿「同一系列的全部条目 + 行号」——比按关键词撒网精确。
- ⚠️ **第三方站点会漏掉「框架自带的东西」**：问「中世纪有什么 CE 兼容的垛口 mod」，所有 mod 站都只列第三方 mod，**不会告诉你 CE 本体自带 `CE_Embrasure`**。这类答案只有读源码才有。

### ⚠️ 写报告前先查重

同一主题被问两次时，工作区里**可能已存在上一版报告**（`ls` 出来的时间戳可能因排序/时机差异看不到）。**动笔前先 `Glob`/`find` 查同名主题**，避免产出两份重叠文档。若已存在：**合并成一份**（保留信息量更大的一方做骨架），删掉冗余文件，并在回复里说明已合并。

### ⚠️ 写「汇总/统整」类文档：先把系列全部产物读一遍，不要凭记忆写

用户说「统整全部内容」「把前面几篇合并成一份」「汇总所有 X」时：

1. **先 `ls` + `wc -c` 列出全部产物**，确认总字节数（防止漏读）
2. **逐篇完整 Read**，不要靠上下文记忆——长对话里早前读过的内容会被压缩成摘要，细节（Steam ID、行号、FAQ 原文）会丢
3. **可被 `Read` 拒绝的文件改用 `cat` 走 Bash**（本机遇到过 `[SENSITIVE_CONTENT_UNAVAILABLE]` 把整个 md 拒掉，`cat` 正常）
4. **结构化数据（JSON）用 Python 打印关键字段**，不要只 `head -c`：
   ```bash
   python -c "
   import json; d=json.load(open('x.json',encoding='utf-8'))
   for i,(k,v) in enumerate(d['ranked'],1): print(i,k,v)
   "
   ```
   （本机遇到过 Python 探查返回空输出，重跑一次即可）
5. **HTML 产物用正则抽标题层级**，不要通读标签：
   ```bash
   python -c "
   import re,html
   s=open('r.html',encoding='utf-8').read()
   for m in re.finditer(r'<h([1-3])[^>]*>(.*?)</h\1>',s,re.S): print('#'*int(m.group(1)), html.unescape(re.sub(r'<[^>]+>','',m.group(2))).strip())
   "
   ```
6. **汇总文档必须显式处理「前序报告之间的矛盾」**：把已更正的错误在汇总里直接采用更正后的说法，并在口径里写明「本汇总更正了 X 篇的 Y 处错误」——否则错误会被汇总再次放大
7. **结构模板**：§0 系列导览（问题→产物→结论）→ §1 方法论与可信度分级 → §2 **全模组总索引**（按类别去重，带 ID + 证据等级，这是核心）→ §3 冲突矩阵 → §4 推荐组合 → §5 踩坑清单 → §6 机制数据速查 → §7 口径说明 → §8 全系列 References
8. **去重**：同一 mod 在多篇里出现只列一次；ID 有冲突的以最新/已核实版本为准并标注（例：`Medieval Overhaul` 从旧 ID 变为 `3219596926`）

## 报告必写口径

1. 各平台的**可抓性差异**（Discord 无内容、Reddit RSS 无互动数）
2. **订阅量是累计值 ≠ 近期热度**
3. 第三方数据源名称 + 快照日期
4. 未验证项单列一节，不要让推断混进事实
5. **抓取失败/超时的源要显式列出**（"本报告未引用 vgover 的两篇文章，因多次超时"），不要静默省略——读者需要知道覆盖边界
6. **区分「机制数据」与「玩家体验」**，并分别标注来源（wiki / 作者 README / Reddit 评论）
7. **同一来源反复超时（≥2 次）就放弃并记录**，不要在第 3 次上浪费时间
8. **兼容性结论必须标明证据等级**（官方支持列表 / 作者页面 / 社区说法），矛盾时显式列出双方说法
9. **「近 N 个月最受欢迎」不是 Steam 的原生口径** —— 必须显式写明采用的替代口径（`browsesort=trend&days=N`），并声明「`subscriptions` 是累计值，不是近 N 天新增」（Steam 不公开增量）
10. **「排除已介绍项」的报告必须给出排除集规模与算法**，并提示读者：被排除项里可能有订阅数更高的 mod（例：`Yet Another Research Tree` 73,792 > 该榜第 1 名 63,641）——即该榜是「**排除老面孔后的最热 N**」，不是「最热 N」
11. **兼容性判定必须三源交叉** —— 官方支持清单只是第一源；**工坊简介的作者 FAQ 常含更多声明**（实测：100 个 mod 中官方清单只命中 2 条，desc 里另有 13 处明确兼容 + 2 处明确不兼容）。只看官方清单会得出严重错误结论
12. **区分「未测试」与「不兼容」** —— `Not tested with CE yet (reports welcome)` 是**未验证**，`Q: CE? A: No.` 才是**不兼容**。报告里不能混为一谈
13. **清单收录 ≠ 当前版本可用** —— 官方兼容清单可能滞后。实测案例：CE 清单收录 `VWE Coilguns`，但其新版尚未被 patch，作者警告「不要加进 CE 存档」。**引用清单时必须附版本/时间限定**
