---
name: dsh-market-plugin-research
description: Crawl and search the full plugin catalog of dsh-market (DeepSeek Harness plugin marketplace, 4000+ plugins), then recommend plugins for a given capability need. Use when the user asks to find/search/browse DSH plugins, wants plugin recommendations for DSH (DeepSeek Harness), or asks for the full plugin list / plugin categories / plugin install commands.
description_zh: "抓取并检索 dsh-market（DeepSeek Harness 插件市场）全量插件，按需求推荐插件"
description_en: "Crawl and search the full dsh-market plugin catalog for recommendations"
version: 1.0.0
display_name: "dsh-market-plugin-research"
visibility: "public"
agent_created: true
---

# dsh-market 插件检索与推荐

## 何时使用

- 用户要给 DSH（DeepSeek Harness）找插件、装插件、问「有没有能做 X 的插件」
- 用户要 dsh-market 的全量插件清单 / 分类 / 安装命令
- 用户提到 `dshmarket.com`

## 关键事实（已验证，2026-09）

| 事实 | 说明 |
|---|---|
| 站点性质 | dsh-market 是 **DeepSeek Harness（DSH）** 的插件市场，静态站 |
| **全量数据源** | `https://dshmarket.com/zh/browse/` —— **单页静态 HTML（约 1.4MB），含全部 4382 个插件，无 JS 渲染、无分页** |
| 首页 `/zh/` | 只有 ~65 条精选，**不要**用它枚举 |
| `sitemap.xml` | 只含 browse/privacy 等页面，**不含**插件详情页 URL，别依赖 |
| 分类 | 23 个，锚点 id：`agi ui usage theme model identity session memory tools wsl browser vision voice docs skill workflow git notify dev security remote market fun` |
| 详情页 URL | `/zh/p/{owner}/{slug}/`；仓库子目录的 `/` 和 `#` 都改写成 `--`（例 `dsh-web#packages/dsh-ssh` → `dsh-web--packages-dsh-ssh`） |
| 安装命令 | `dsh plugin --profile web add <包名>`；来源有两种：npm 包名（`dsh-bill`、`@weiboohui/dsh-tasks`）或 GitHub 源（`github:owner/repo`）。**含 `#` 时必须用双引号包裹** |

## 步骤 1：抓全量目录

```bash
curl -sL --max-time 60 "https://dshmarket.com/zh/browse/" -o /tmp/dsh_browse.html
```

用 Python 解析（HTML 结构固定）：

```python
import re, json, html
h = open('dsh_browse.html', encoding='utf-8').read()
secs = re.findall(
    r'<section class="cat" id="([a-z-]+)">\s*<h2>(.*?)<small>(\d+)</small></h2>\s*<ul class="list">(.*?)</ul>',
    h, re.S)
items = []
for sid, title, cnt, body in secs:
    lis = re.findall(r'<li><a href="([^"]*)"><span class="owner">([^<]*)</span>([^<]*)</a><p>(.*?)</p></li>', body, re.S)
    for url, owner, name, desc in lis:
        items.append({
            'cat_id': sid, 'cat': html.unescape(title),
            'owner': html.unescape(owner).rstrip('/'),
            'name': html.unescape(name),
            'desc': html.unescape(re.sub(r'<[^>]+>', '', desc)).strip(),
            'url': 'https://dshmarket.com' + url,
        })
json.dump(items, open('plugins_raw.json', 'w', encoding='utf-8'), ensure_ascii=False)
```

**校验**：解析出的条数应等于各 `<small>` 数量之和（4382）。若不等，说明页面结构变了。

## 步骤 2：抓详情页拿准确安装命令

```python
raw = re.findall(r'dsh plugin --profile web add\s+&quot;?([A-Za-z0-9@/_.:\-#]+)', h)
raw += re.findall(r'dsh plugin --profile web add\s+"?([A-Za-z0-9@/_.:\-#]+)', h)
bad = ('dshmarket', 'link', 'https', 'github:owner', '...')
cmds = [c.rstrip('"&') for c in raw if not any(b in c for b in bad) and len(c) > 4]
```

- **必须同时匹配 `&quot;` 和裸引号两种形式**，否则带 `#` 的命令会被截断成 `github`。
- 详情页还会给出**版本要求**（`<code>^0.1.7</code>` 这类），推荐时一并带上。
- 抓取间隔 `sleep 0.25`，49 个页面约 20 秒。

## 步骤 3：按能力维度检索

给每个维度定义 `strong`（高权重，+6）和 `weak`（低权重，+1）关键词，命中后按 `得分 + min(描述长度,400)/120` 排序，并对描述 < 25 字的条目减分（过滤水插件）。

已验证有效的维度分组：提示词与人设 / 知识库与检索 / 技能系统 / 工作流与自动化 / 多代理协作 / 长期记忆 / 文档与办公 / 连接器与集成 / 浏览器与联网 / 沙箱与权限 / 会话与上下文。

## 输出规范

1. **交付 Excel/CSV 全量明细**（分类 / 作者 / 插件名 / 用途 / 链接），用 `utf-8-sig` 保证 Excel 不乱码。
2. **推荐清单按「用户需求 → 插件」映射**，每个插件给：一句话能力、与同类插件的差异、**核实过的安装命令**。
3. **同名插件有多个作者**（`dsh-cron`、`dsh-memory`、`dsh-skill-manager` 等都重名），标注作者 + 直接用安装命令区分。
4. 可附一个单文件离线搜索 HTML（数据内嵌 JSON），用户后续可自行检索。

## 坑

- 首页的 `#count` 是 JS fetch 出来的，静态 HTML 里是构建时的旧值，别用。
- 市场里大量插件是低质/玩具（描述 < 25 字），推荐时务必按描述详细度和功能具体性过滤。
- 部分插件的 GitHub owner 与市场页标注的 owner 不一致（作者改名/fork），**以详情页的安装命令为准**。
