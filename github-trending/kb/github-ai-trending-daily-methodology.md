---
id: github-ai-trending-daily-methodology
title: GitHub AI 趋势日报：抓取方法与判据
tags:
  - github-trending
  - scraping
  - methodology
  - agent-ecosystem
  - dedup
  - automation
created: 2026-10-12
updated: 2026-10-19
version: 1.5.0
status: stable
source: 本工作区 2026-09-17 ~ 2026-10-19 共 22 次自动化运行实测
confidence: 已核实
---

## 一句话结论

**主榜（daily/weekly/monthly）头部已固化，语言维度榜 `/trending/<lang>` 是唯一稳定的新面孔来源；语言榜固定抓 18 个，且 2026-10-16 起「语言 × weekly 全 18 榜」应并入日常抓取（本期 41 榜 / 582 行 / 469 去重 / 358 未推送，10 条详细中 9 条来自语言榜：daily 6 + weekly 3）。同日第二次运行必须换「周期」而不只换「语言」——「语言 × weekly」+「语言 × monthly」+「口语语言榜 zh/en」一次可拿到 270 条未推送仓库。**⚠️ 2026-10-19 推翻一条旧结论：主榜 daily 会日内刷新**——同日 09:30 与 14:00 两次抓取的 13 条**完全不同**（上午 graphify/ASPIRE/OmniRoute，下午 orca +25,115 / VoiceStudio +42,036）。**"同日第二次运行主榜必然 100% 重复"不再成立，每次都必须实测，不能沿用假设。** 抓取必须用"带重试的 curl 落盘 + 本地正则解析"，不要依赖脚本自带的网络层；解析要按 `<article class="Box-row">` 分块，仓库名用 `href="/(owner)/(repo)"[^>]*class="Link"><svg` 命中，且**总 star 数在 `</svg>` 之后**（不在 `/stargazers"` 紧邻处，否则会把"N stars today"的增幅误当总数）。**⚠️ 跨榜口径污染已被两次实测：`fetch_trending.py` 的 `merge()` 会跨榜取 max 增幅，同一仓库不同周期可差一个数量级（rea daily +32,314 / weekly +239,477；VoiceStudio daily +3,024 / monthly +38,181；ECC daily +1,013 / monthly +22,953）。报告必须逐条标注来源榜与周期，绝不可把合并后的单一数字当"当日增幅"使用。**

---

## 1. 数据源与优先级

| 优先级 | 来源 | URL | 说明 |
|---|---|---|---|
| 1 | 语言维度榜 | `https://github.com/trending/<lang>?since=daily` | **固定抓 18 个**：python / typescript / rust / go / c / c++ / javascript / java / swift / vue / html / cuda / jupyter-notebook / csharp / kotlin / ruby / shell / php（低增幅榜 java/swift/vue/html/cuda/csharp/kotlin/ruby/php 也必抓——2026-10-13 实测新增 5 个榜贡献 8 个有效新面孔） |
| 1 | **语言 × weekly / monthly** | `.../<lang>?since=weekly` / `?since=monthly` | **同日第二次运行的唯一出路**：同一语言的 daily/weekly/monthly 是**完全不同**的三批仓库 |
| 1 | **口语语言榜** | `?spoken_language_code=zh\|en&since=daily\|weekly` | 主榜与语言榜都看不到的中文/英文项目（WeFlow / Bili23 / TikTokDownloader / tvbox） |
| 1 | 主榜 monthly | `https://github.com/trending?since=monthly` | 新面孔第二来源（10-12 上午 4/10 来自 monthly） |
| 2 | 主榜 daily / weekly | `?since=daily` / `?since=weekly` | 头部固化，新面孔率 <20%（10-12 已是 0%） |
| 3 | 仓库 README | `raw.githubusercontent.com/<o>/<r>/{HEAD,main,master}/README.md` | 三支兜底 |
| 3 | 发布记录 | `https://github.com/<o>/<r>/releases.atom` | 判断"已推送仓库是否有重大新版本" |

**实测数据**：
- 2026-10-12 上午（语言 × daily）主榜 daily 8 / weekly 12 / monthly 22，14 语言榜去重 181 条；**同日下午（语言 × weekly + monthly + 口语语言）主榜 42 条 100% 重复**，26 个榜去重 353 条、其中 **270 条从未推送**。
- 2026-10-15（相隔 2 天，语言 × daily）主榜 daily 12 / weekly 12 / monthly 22 = **46 条中仅 3 条新面孔**；18 语言榜 = 259 条；**合计 305 行 → 去重 282 个仓库**；21 榜并发**0 次重试一次全过**。新面孔在 `csharp`（Llama-Windows / dotnet-skills / unity-mcp）、`go`（agentmesh / anubis / pentagi）、`c++`（ESP32-Bit-Pirate / FinceptTerminal）三榜最集中。
- 2026-10-16（相隔 1 天，语言 × daily + **语言 × weekly 全量**）主榜 daily 13 / weekly 11 / monthly 22 = **46 条中仅 3 条新面孔**（LibreSpark/LibreTV、lightseekorg/tokenspeed、boykopovar/AnyPS5，其中 AnyPS5 在 10-13 曾以纯文本被提过一次）；18 语言榜 × daily + 18 语言榜 × weekly + 口语语言榜 zh/en = **41 榜、582 行 → 去重 469 个仓库、358 个未推送**；**41 榜并发 0 次重试一次全过**。新面孔最集中在 `go`（beads / filebrowser）、`python`（OpenViking / KittenTTS / ida-pro-mcp）、`rust`（jcode / OpenResearch / ZLUDA）、`java`（skillhub / agentscope-java / spring-ai-alibaba）四榜。**结论：语言 × weekly 收益为正，建议固定抓。**
- **2026-10-19 两次运行对照（同日第二期的正确姿势）**：上午 09:30（主榜 + 18 语言 × daily）= 19 榜 293 行 / 269 去重 / 205 首见，周榜 10 条与月榜 20 条**零新面孔**；下午 14:00（主榜 daily + 18 语言 × weekly + 9 语言 × monthly + 口语 zh daily/weekly + en weekly）= **31 榜 487 行 / 418 去重 / 289 未推送**，31 榜并发**0 次重试一次全过**。**关键：下午的主榜 daily 13 条与上午完全不同**（下午为 orca / VoiceStudio / claude-plugins-official / ai-job-search / CLI-Anything / cursor-plugins / ruflo / opencode / android-skills / ai-memory / ComfyUI / jasna / llm-course）。**结论：主榜会在日内刷新，同日第二期不必先假设"必然全重复"。**

**注意**：`github-ai-trends` 技能自带的 `fetch_trends.py` 走 **GitHub Search API 按 star 排序**，返回的是"AI 关键词 + 高星"列表（如 openclaw 391.7k / n8n 207.0k），**不是 trending 的日增幅榜**，不能当趋势数据用。仅可用于取"AI 相关仓库的高星背景板"。

---

## 2. 可复用操作

### 2.1 带重试的抓取（必须，trending 会大面积 504）

```bash
OUT="C:/Users/Admin/AppData/Local/Temp/ght-<date>"   # 真实 Windows 路径，勿用 /tmp
mkdir -p "$OUT"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36"

grab() {  # $1=url $2=filename
  local i=0
  while [ $i -lt 8 ]; do
    i=$((i+1))
    code=$(curl -sL -A "$UA" --max-time 45 -o "$OUT/$2" -w "%{http_code}" "$1")
    size=$(stat -c %s "$OUT/$2" 2>/dev/null || echo 0)
    [ "$code" = "200" ] && [ "$size" -gt 100000 ] && { echo "OK $2"; return 0; }
    sleep 3
  done
  echo "FAIL $2"
}
```

判据：`code==200 && size>100000`。**并发抓 + `wait`**，14 个榜一次跑完约 8 秒。

### 2.2 解析（正确姿势）

```python
arts = re.split(r'<article class="Box-row', html)[1:]   # 分块（注意：不要带结尾引号，属性后可能还有内容）
# 仓库名：h2 内的 <a> 带 data-hydro-click 前置属性；用 class="Link"><svg 作右边界最稳
m = re.search(r'href="/([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+)"[^>]*class="Link"><svg', a)
owner, repo = m.group(1), m.group(2)
if owner in ('login','sponsors','orgs'): continue        # 过滤非仓库链接
desc  = txt(re.search(r'<p class="col-9 color-fg-muted my-1 pr-4">\s*(.*?)\s*</p>', a, re.S).group(1))
lang  = re.search(r'itemprop="programmingLanguage">([^<]+)<', a).group(1)
# 关键：star/forks 数字在 </svg> 之后，不在 /stargazers" 紧邻处
total = num(re.search(r'/stargazers"[^>]*>.*?</svg>\s*([\d,]+)\s*<', a, re.S).group(1))
forks = num(re.search(r'/forks"[^>]*>.*?</svg>\s*([\d,]+)\s*<', a, re.S).group(1))
gain  = num(re.search(r'([\d,]+)\s*stars?\s*(today|this week|this month)', a).group(1))
```

字段名（自建 dict）：`name / lang / desc / total / forks / gain / board`。**`gain` 的口径随榜而变**——daily 是"今日"，weekly 是"本周"，monthly 是"本月"；合并去重时**不要跨榜取 max 后当同一口径使用**。

### 2.3 去重清单

```bash
grep -ohE '\[[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\]\(https://github.com' github-trending-*.md \
  | sed 's/^\[//; s/\](.*$//' | tr 'A-Z' 'a-z' | sort -u > pushed.txt
```

按小写比对。**"速览里只提过一行"也算已推送**——判断标准取严。

### 2.4 发布记录取正文

```python
ents = re.findall(r'<entry>(.*?)</entry>', atom, re.S)[:3]
for e in ents:
    t = re.search(r'<title>(.*?)</title>', e, re.S)
    u = re.search(r'<updated>(.*?)</updated>', e, re.S)   # 注意：<updated> 在 <title> 之前
    c = re.search(r'<content[^>]*>(.*?)</content>', e, re.S)
    body = html.unescape(re.sub(r'<[^>]+>', ' ', c.group(1)))
```

### 2.5 同日第二次运行的维度选择（本期新增，重要）

同一天跑第二次时，**先实测主榜 daily 是否已刷新**（2026-10-19 实测：09:30 与 14:00 的 13 条完全不同，Orca +25,115 与 VoiceStudio +42,036 都只在下午出现）。若已刷新，主榜 daily 直接可用；未刷新时按下列顺序换维度：

| 顺序 | 维度 | URL 形态 | 实测产出 |
|---|---|---|---|
| 0 | **主榜 daily（先重抓一次）** | `/trending?since=daily` | **2026-10-19 实测日内会刷新，1 个请求即可确认** |
| 1 | **语言 × weekly（全 18 榜）** | `/trending/<lang>?since=weekly` | **2026-10-16 起并入日常抓取**：与语言 × daily 合起来 36 榜贡献 9/10 条详细；10-19 下午场 18 榜贡献 7/10 |
| 2 | 语言 × monthly（9 语言） | `/trending/<lang>?since=monthly` | 高增幅新面孔（10-19 下午场贡献 orca 之外的 2 条） |
| 3 | 口语语言榜 × daily/weekly | `?spoken_language_code=zh\|en&since=daily` | 中文项目（LinkSwift / awesome-zhuiju-free / tubatools / DeskBox，与主榜零重叠） |
| 4 | trending developers | `/trending/developers?since=daily` | 只看人不看仓库，价值最低 |

**核心认知：`since` 是比 `lang` 更强的"换榜"开关** —— 同一语言的 daily/weekly/monthly 是**互不重叠**的三批仓库。

### 2.6 本工作区已固化的脚本（2026-10-16 更新，放 `<workspace>/.workbuddy-ai/scripts/`）

| 脚本 | 用途 | 关键点 |
|---|---|---|
| `fetch_trending.py` | 主榜三榜合并输出 markdown 表；**被 `parse_*.py` 以 `importlib` 复用 `parse_board(html, period)`** | **不支持 `--lang`**；`merge()` 跨榜取 max gain（见坑表），需要当日数据时别用它 |
| `grab_1016.sh <outdir>` | 并发抓 **3 主榜 + 18 语言 × daily + 18 语言 × weekly + 口语语言 zh/en daily = 41 榜** | 每 URL 最多 8 次重试、判据 `code==0 && size>100000`；`xargs -P` + `&`/`wait`；实测 41 榜一次全过 |
| `parse_1016.py` | 解析 41 个榜 → `all.tsv` / `all.json`（字段 `gain / total / lang / name / boards / desc`） | 按文件名前缀区分榜：`main_*` / `lang_daily_*` / `lang_weekly_*` / `spoken_*`；`board` 字段必须保留用于标注口径 |
| `atoms_1016.sh <outdir>` | 并发抓 30 个仓库的 `releases.atom` | `xargs -P 10`，用于"已推送仓库是否有新版本" |
| `readmes_1016.sh <outdir>` | 并发抓 27 个 README，`HEAD` → `main` → `master` 三支兜底 | 27 个全部一次成功 |
| `grab_1019b.sh <outdir>` | 同日第二期：主榜 daily + **18 语言 × weekly** + **9 语言 × monthly** + 口语 zh daily/weekly + en weekly = **31 榜** | `xargs`/`&`+`wait` 并发，每 URL 8 次重试；**31 榜一次全过** |
| `parse_1019b.py` | 解析 31 个榜 → `all.json`，自动按 `pushed_clean.txt` 过滤输出未推送项 | 榜前缀 `main_` / `lang_weekly_*` / `lang_monthly_*` / `spoken_*`；**保留 `boards` 字段** |
| `readmes_1019b.sh <outdir>` | 并发抓 18 个 README（4 文件名 × 3 分支兜底）+ 18 个 `releases.atom` | `xargs -P 8`；18 个 README 全部 HEAD 分支一次成功 |

**去重与筛选固定流程**：
```bash
# 1) 生成已推送清单（链接式 + 粗体式都要抓，标准取严）
grep -ohE '\[[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\]\(https://github\.com' github-trending-*.md | sed 's/^\[//; s/\](.*$//' > pushed.txt
grep -ohE '\*\*[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\*\*' github-trending-*.md | sed 's/^\*\*//; s/\*\*$//' >> pushed.txt
tr 'A-Z' 'a-z' < pushed.txt | sort -u > pushed_clean.txt
# 2) 过滤（小写比对）
python -c "import json;rows=json.load(open('all.json'));p=set(l.strip() for l in open('pushed_clean.txt'));print(len([r for r in rows if r['name'].lower() not in p]))"
```
**核实用仓库归属时**用 `curl -o /dev/null -w "%{http_code} %{redirect_url}" https://github.com/<old-owner>/<repo>` 看 301 跳转（本期据此确认 `sst/opencode → anomalyco/opencode`、`steveyegge/beads → gastownhall/beads`），必要时用 `api.github.com/repos/<o>/<r>` 取 `stargazers_count` / `pushed_at`（本期据此确认 `HexRaysSA/ida-mcp` 存在）。

解析一律用内联 Python `importlib` 加载 `fetch_trending.py` 复用 `parse_board(html, period)`；语言榜只需换 URL 与本地 HTML 文件，字段名同为 `name / lang / desc / total / gain / forks`（自建 `board` 字段标注来源）。

---

## 3. 输出结构（固定）

1. 头部：数据源构成 + 主榜固化程度说明 + 口径声明（"trending 排序 ≠ 增幅排序"；**"不同榜的周期不可互相比较"，每条必须标注来源榜**）
2. 榜单速览表（# / 仓库 / 语言 / 总 star / 增幅 / **来源榜** / 一句话）
3. 10 条详细：**事件**（何时上榜、增幅、版本号）→ **核心内容**（bullet，带具体数字与命令）→ **值得关注的原因**（技术判断 + 与前期的关联）
4. 其他趋势速览（大厂官方 / 运行时沙箱 / 中文生态 / 工具基础设施 / 已推送仓库新版本）
5. 已推送仓库新版本与重大动态（数据源 = 各仓库 `releases.atom`，**只列上次运行日之后的条目**）
6. 当日主线判断（8–12 条编号结论）
7. 方法论脚注（本期新增的坑与抓取统计）

**筛选口径**：当日新增 star 高 + 技术方向有代表性 + 工程参考价值。10 条中尽量 9 条全新面孔 + 1 条已推送仓库重大新版本；若已推送仓库无重大事件，则 10 条全新。

---

## 4. 坑与反直觉

| 坑 | 表现 | 处置 |
|---|---|---|
| trending 大面积 504 | daily/monthly/多个语言榜首轮全 504 | 带重试 curl 落盘；**不要用脚本自带网络层**（单次失败即放弃） |
| h2 结构变了 | `<h2 class="h3 lh-condensed">` 内 `<a>` 带 `data-hydro-click` 前置 | 用 `href="/(owner)/(repo)"[^>]*class="Link"><svg` 作右边界 |
| **总 star 数解析为 0** | `/stargazers"` 后紧跟的是 `<svg ...>` 图标，数字在 `</svg>` 之后 | 用 `/stargazers"[^>]*>.*?</svg>\s*([\d,]+)\s*<`（`re.S`）；否则会把 "45,327 stars today" 的增幅误当总数 |
| 分块正则匹配不上时 | 解析结果静默为 0 条 | 先 `grep -o 'Box-row' file \| wc -l` 确认条数，再排查 `if not m: continue` 这类静默跳过 |
| 主榜条数远少于 25 | 实测 daily 8~9 / weekly 11~12 / monthly 22~25 | 正常现象，不要当抓取失败 |
| `releases.atom` 无正文 | 只有 `<updated>` 无 `<entry>`/`<content>` | 常见于新仓库首发、atom 未生成正文、artifact 型仓库（diagram-design/openmontage 实测 0 entry）；改从 README 取 |
| README 过大 | 99KB~112KB（tinyjsapp 99K / ai-engineering 112K / obsidian-mind 50K / diagram-design 52K） | 一律 `curl` 落盘 + `grep -n '^#\+ '` 先看章节再 `sed -n 'A,Bp'` 定点读 |
| `/tmp` 不可用 | Windows 环境 | 用真实路径 `C:/Users/<user>/AppData/Local/Temp/...` |
| 用 `python3` 调用 | PowerShell 里是 WindowsApps 存根 | 用托管 Python 绝对路径 |
| 主榜三榜 42 条全重复 | 同日第二次运行；2026-10-13 实测 42 条里仅 3 条全新 | 换 `since` 周期 + 扩语言榜 + 口语语言榜，见 2.5 |
| **合并后增幅被跨榜污染** | `fetch_trending.py` 的 `merge()` 对同一仓库取**跨榜最大** gain；2026-10-15 实测 rea 显示 "+214,837"（实为 weekly，daily 仅 +41,034）；2026-10-16 再实测三例：rea daily **+32,314** / weekly **+239,477**、VoiceStudio daily +3,024 / monthly +38,181、ECC daily +1,013 / monthly +22,953 | **不要用合并后的单一数字描述"当日表现"**；需要当日数据时回到 `main_daily.html` / `lang_daily_*.html` 单独取数（`parse_*.py` 保留 `boards` 字段即为此）。报告速览表必须带"来源榜"列 |
| **仓库改名/迁移后旧链接失效** | `sst/opencode`、`steveyegge/beads` 均已 301 到新组织；报告里写旧名会让读者找不到 | 抓取后对可疑仓库跑 `curl -o /dev/null -w "%{http_code} %{redirect_url}" https://github.com/<o>/<r>` 确认；去重时**新旧名都算已推送** |
| **`releases.atom` 的 `<updated>` 在 `<title>` 之前** | 用 `grep -oE '<title>…|<updated>…'` 顺序读会整体错位一格 | 一律按 `<entry>` 块 `re.findall` 切分，再在块内分别取 `<title>` / `<updated>` / `<content type="html">`；正文用 `html.unescape` + `re.sub(r'<[^>]+>','')` |
| **主榜会日内刷新**（2026-10-19 推翻旧结论） | 同日 09:30 与 14:00 的 daily 13 条**完全不同**；此前 10-12 实测为"100% 重复" | **不要预判"必然全重复"**，每次第二期都重新抓主榜 daily，成本仅 1 个请求 |
| **star 尖峰没有 release** | VoiceStudio 今日 +42,036，但最新 release 仍是 26 天前的 v0.5.6 | 报"事件"前先查 `releases.atom` 首条时间 + `pushed_at`；无版本就写"纯 star 尖峰，无产品事件" |
| **release 正文只有版本号** | orca v1.4.230 的 release body 只有 `v1.4.230` 一行 | 改从 README 功能面 + 上一条有内容的 release（v1.4.229）取信息，不要编造变更 |
| **仓库无 LICENSE 文件** | BuilderIO/agent-native 的 API `license` 为 `null`，README 只说"你建的东西归你" | 商业公司的"开源框架"要单独看 npm 包授权，报告里必须标"无 LICENSE" |
| **`license.spdx_id` 为 `NOASSERTION`** | Unity-Technologies/unity-agent-plugin | 标"许可证待确认"，不要写 MIT/Apache |

---

## 5. 主题追踪（跨期累积的判据）

写"值得关注的原因"时，与前期条目做关联，可复用以下已确立的判断轴：

- **边界可审计成入场券**：文件级数据边界、凭据边界清单、Host 头白名单、安全默认值
- **控制平面失效常常无声**：hook 不覆盖、档位静默失效、评论丢失、配置未写回；**正面解法** = 能力协商写进 `/health`（engram）+ 不支持的动作返回显式错误（moli）+ 更新前检测"谁拥有这个二进制"（tuios）
- **诚实披露四级**：修正数值（RuView 撤回 100%）→ 修正口径（rtk 拆穿自家标题）→ 修正能力边界（colibri 写 0.05 tok/s）→ **连文档声称的行为都先否掉**（webcodex "不声称跨平台行为一致"、ninfer "没有 install target"）
- **成本战场五层**：不产生中间结果（e2e 录制回放）→ 不读取（claude-mem 读取门）→ 不调用模型（context-mode）→ 不让会话启动等待（claude-mem 索引 4ms）→ **不渲染**（moli 结构优先、布局按需；73 MiB vs Chrome 773 MiB）
- **Agent 产出溯源**：checkpoint 把 commit 挂回会话（prompt/工具调用/推理/patch），链接穿过 amend/rebase、真歧义孤儿化而不猜（atlas）
- **用户数据跨 harness 流动**：导入清单（atomic-agent 六家）+ 跨 Agent 共享记忆（atlas）+ 多 CLI 统一控制面（cc-switch）
- **反向量化 / 压缩向量并存**：拒绝 float32 + HNSW 默认；记忆层四条路线（服务化 LLM / 文件化零 LLM / 图谱本地小模型 / FTS5 单文件）star 数无明显高下
- **上一代项目成为下一代地基**：cloudflare-os 依赖 pi-agent-core、PI-Desktop 建在 pi Agent Harness 上、omnigent 依赖 OpenShell/hindsight
- **先建基线再做产品**：ADR-Bench、AACR-Bench、SkillSpector 漏洞基线、atomic-agent 的 GAIA L1 控制变量对照（69.8% vs Hermes 58.5%，唯一变量是 agent loop）
- **厂商官方落点是"接已有系统"而非模型**：插件市场 / 门户接入 / 合规免责前置
- **推理引擎按场景切片**：ninfer 单卡专用（1,000+ tok/s）/ colibri 磁盘流式（8GB RAM，0.05 tok/s）/ uzu 四语言绑定进 App / ds4 刻意窄化；"能跑"与"能用"的差距明码标价
- **存算分离下沉**：图数据库建在对象存储上（hydradb，查询节点只保留可丢弃状态）+ 分布式 Durable Objects 长期状态在 bucket（celld）
- **技能赛道分野 = "是否接管你的流程"**（2026-10-13 确立）：mattpocock/skills（20 技能，**小而可改、明确不接管流程**，README 直接点名批评 GSD/BMAD/Spec-Kit）vs Donchitos/Game-Studios（49 agents 重度编排）vs deanpeters/PM-Skills（77 框架，功能+教学双目标）vs ECC（71 agents）。**user-invoked 只能调 model-invoked、不得嵌套 user-invoked** 是可复用架构规则
- **多 Agent 编排的负面实证**（2026-10-13 首次）：Game Studios 自曝四档 rigor 对照——`standard`（写代码前 30 篇文档 / 58 分钟）在**双盲评 + 人类试玩中排名最后**，`minimal`（1 篇 brief / 0 分钟）反而被偏好。**多出的文档买到可追溯性，不是更好的游戏**
- **质量门按产物类型定制**（2026-10-13）：视觉产物必须以**截图证据**闭环（Game Studios `production/qa/evidence/`，"解析通过≠跑过"）+ 渲染后强制自审 ffprobe/抽帧/音频（OpenMontage）+ 交付承诺阻断"像幻灯片"的渲染
- **隔离层三层同时下注**（2026-10-13 微软）：策略面 mxc（委托 bubblewrap/seatbelt/microVM）→ 编排面 agent-sandbox（K8s CRD）→ **内核面 litebox（library OS，削减宿主接口面；"任意 North 配任意 South"）**
- **记忆层第五条路线 = 把笔记应用本体当存储**（obsidian-mind）：记忆 schema 复用**人已有的知识结构**（人物页/决策记录/Brag Doc），写作目标从"给 Agent 读"扩展到"给人做绩效与 1:1 用"
- **跨平台运行别人平台的软件是最热类目**：Madeira（iPhone 无越狱跑 Windows 游戏，FEX-Emu + ARM64EC Wine + DXMT/D3D12-on-Metal）/ winlator / GameNative / AnyPS5 / quiver-launcher。**共同点：翻译层+兼容层+图形层三段解耦，且不掩饰合法绕行路径（如 Madeira 因 JIT 需调试器 → 明确放弃上架）**
- **教学项目技能化 + 证据化**（ai-engineering-from-scratch）：用 9 个 agent skill 分发 528 课，要求真实主机的可发现性/调用/脚本/卸载证据，缺 preflight 就明说证据待补；**Build It（裸实现）/ Use It（生产库）二分**是可复用课程脊柱
- **诚实披露第五级 = 主动交出对自己不利的对照数据**：Game Studios 盲评排名 / diagram-design 自曝"没有可 diff 的源格式，文档改动频繁就该用 Mermaid" / ghostlock 偏移提取器"从不猜值、输出一律标注未验证候选" / Madeira "预期粗糙边缘"
- **诚实披露第六级 = 主动拆解自家最漂亮的数字**（2026-10-15 确立）：Soup 自述 layer streaming 的 1.74× 原始增益"**来自时钟而非加速**"，并说明连折算比例也不是同类比较（59% vs 68% GEMM 上限占比，且内存访问模式已变）；PentAGI 把 **Current Capability Boundaries 单列一节**（"不是 CALDERA 式 BAS""JSON flow-report 导出今天不算受支持格式"）；Anubis 在正文写自己"像核弹式响应、会误伤 Internet Archive、多数情况用 Cloudflare 就够"
- **"配置被接受却从未生效"必须变成加载期硬错误**（2026-10-15，当前最彻底的解法）：Soup v0.76.0 对"被校验、被文档化、但目标路径上没有任何代码读取"的选项**在加载时直接拒绝并点名字段与改法**（如 `training.quantization_aware: true` 从未真的跑过量化感知训练），其余未读旋钮先警告并**点名哪个版本开始拒绝**；同时把"一直切分却从未被评估"的 val split 改成真的评估。同病样本：ponytail 一行 plugin.json 让规则静默失效 / claude-mem 异步 hook 拦不住任何东西 / engram 的能力协商 / openrig 的 daemon 重启 / **ponytail v5.2.0 档位在上下文压缩后回落** / **claude-mem v13.39.0 子代理线程压缩后丢记忆** / **gpui-kit 重建二进制后文档与下载物不一致**
- **"Agent 之间的网络层"成为独立品类**（2026-10-15，google/agentmesh）：此前同类都在单机（mxc 策略）或单集群（agent-sandbox 编排）内，agentmesh 补跨机器/跨网络/跨组织的发现与授权。两条可复用判断：**授权绑服务名不绑地址**（地址会漂移，服务名是意图）、**控制平面签发的凭证必须能离线验证**（否则网络分区即全线瘫痪）
- **技能/插件分发四层产业链成型**（2026-10-15）：分发工具（vercel-labs/skills，79 个 agent，凭据不落地 + 下载/解压三档上限）→ 领域内容（K-Dense 177 技能 + arXiv 论文；twostraws 的 SwiftUI/SwiftData/Concurrency/Testing 四个 Pro）→ 厂商市场（anthropics/claude-plugins-official、aws/agent-toolkit-for-aws GA、dotnet/skills）→ 托管平台（apify-mcp-server 接 agentic payments：AGI token / direct x402 / Skyfire）
- **插件 slug 不可变 + `renames` 自动迁移**（2026-10-15，claude-plugins-official）：插件 `name` 是不可变 slug，改名会让用户端报 `plugin-not-found`；改 UI 显示用 `displayName`；确需改名必须在顶层 `renames` map 登记，加载器下次同步时**透明重写旧 slug**。另有 **skill-bundle 插件**：源仓库只有 `SKILL.md` 而无 `plugin.json` 时，市场条目用 `strict: false` + 显式 `skills` 数组声明
- **"技能价值"开始有公开量化面板**（2026-10-15，dotnet/skills 的 Skill Value dashboard）：按插件/技能/executor 模型/judge 模型列出 **token 用量、耗时、激活率、未通过率**。接续 09-30 SkillSpector 的"26.1% 技能含漏洞"安全基线，技能生态从安全基线走到价值基线
- **本地推理最后一公里从 CLI 挪到操作系统界面**（2026-10-15，ggml-org/Llama-Windows）：托盘应用 + `Alt+Space` 全局浮层（隐藏而非关闭，会话保留）+ **下载前按 GGUF header 给每个上下文长度档位的内存估算**。披露粒度为**字段级**（只带 `llama-win/<ver> (<build>; <arch>)` 这一个 UA，无遥测），对照 10-07 ChromeDevTools MCP 的"三处默认开启遥测需逐项关闭"
- **防御侧与访问侧同期上榜**（2026-10-15）：过去数期记的都是"Agent 如何访问互联网"，本期 **TecharoHQ/anubis**（PoW 挑战式 Web AI 防火墙）以 23,412 star 上榜，代表内容方"我如何决定谁可以访问我"。攻防两端同时出现是存量博弈的标志
- **改名/品牌迁移 = 摆脱上游宿主品牌**（2026-10-15）：Claude Flow → **Ruflo**、KrillinAI → **OpenCreator**、Claude Scientific Skills → **Scientific Agent Skills**、Agent Mesh（刚改名）。共同动机：当 Claude Code / Codex 成为宿主，能力层项目只能靠能力立足；但分发入口仍高度集中在 Anthropic 插件市场（`/plugin marketplace add`）
- **两条互斥的 harness 哲学并存**（2026-10-15 再次确认）：ruflo 的"全都要"（314 个 MCP 工具 / 26 个 CLI 命令 / 100+ Agent / 需 Claude Code 2.1.287+）vs mattpocock/skills 的"少而精、绝不接管你的流程"。**harness 层远未收敛**
- **垂类免责写到技能颗粒度**（2026-10-15，K-Dense）：临床技能只做"来源绑定的报告草稿结构"，动物实验技能写明"是严重度评估的辅助、**永远不是决策规则**"，法规技能写明"供合格评审、**永远不是认证/认可/方法放行决定**"。配合 09-23 financial-services 的"人工签核前置"，"我做到哪一步、由谁签字"正成为垂类 Agent 入场券
- **记忆层第六条路线 = 把记忆做成文件系统**（2026-10-16，volcengine/OpenViking）：`viking://` 虚拟文件系统 + `ls/tree/read/write/grep` + **目录级摘要 L0/L1/L2**（先读摘要再读全文）+ 目录作用域检索（TrieHI）+ 会话归档成可读 Markdown。前五条：服务化 LLM（claude-mem）/ 文件化零 LLM / 图谱+本地小模型（cognee）/ FTS5 单文件（engram）/ 笔记应用当存储（obsidian-mind）。**六条路线 star 数仍无明显高下 = 记忆层未收敛**
- **云厂商同周落子 Agent 记忆**（2026-10-16）：火山引擎 OpenViking（存储形态入手）与腾讯云 TencentDB Agent Memory（组织形态入手：团队命名空间 + private/team/restricted/agent 四级可见性 + Owner 管理权）同日出现在语言榜。**记忆从个人工具升级为云厂商产品线**
- **接入方式本身成为竞争点**（2026-10-16）：TencentDB 走"**改 base URL 零代码**"（把记忆做成模型 API 中间层，绕开插件/hook 适配地狱，与 cc-switch 的本地路由同构）vs OpenViking 走"安装脚本 + 插件安装器"vs beads 走"CLI + `bd setup` 写 AGENTS.md/hooks"。**在协议层插桩明显比在每个客户端里装东西省事**
- **成本战场第六层 = 进程模型**（2026-10-16，1jehuang/jcode）：moli 量"渲染"（73 MiB vs Chrome 773 MiB）→ jcode 量"进程"（10 并发 PSS 66.7MB vs Claude Code 1749.7MB；每多一会话 ~3.1MB vs ~164MB；首帧 14.0ms vs 3436.9ms）。差距来自**共享 daemon vs 每会话一进程**的架构选择，不是语言。**"能跑几个 Agent"从模型成本问题变成进程模型问题**
- **厂商收编社区实现**（2026-10-16，mrexodia/ida-pro-mcp）：Hex-Rays 官方发 IDA MCP 后，最流行的社区实现（x64dbg 作者）在 README 第一行主动让位。与 10-09 微软 mxc 委托 bubblewrap/seatbelt、10-08 agent-sandbox 委托 RuntimeClass 同构：**能力层不重复造，让位给拥有产品的厂商**
- **技能生态进入"有 CI"阶段**（2026-10-16）：dotnet/skills 建**价值仪表盘**（token/耗时/激活率/未通过率）→ darwin-skill 建**优化循环**（评分→改进→回归→棘轮，只保留可测量改进）。关键实证：**LLM 自评准确率仅 46.4%**（微软 SkillLens, arXiv:2605.23899），这是"禁止自己改自己评"从直觉变成数据
- **厂商官方技能市场口径高度一致**（2026-10-16，Google Android + 微软 Azure）：① 只做"**评测显示 LLM 表现差**"的场景（android/skills 原话："不优先做 LLM 已经擅长的领域，如基础 Jetpack Compose 最佳实践"）；② **技能与 MCP 执行层打包成一个安装单元**（微软明说"这不是 prompt pack"，Azure MCP 40+ 服务 200+ 工具）；③ 多宿主分发（APM 一条命令装 6 个宿主 / marketplace 双路）；④ 都声明 AI 会犯错。可复用判据：**"不要重复 LLM 已知的东西，那会白烧 token"**（twostraws 10-15 + android/skills 10-16 独立得出）
- **技能分发三层光谱**（2026-10-16）：公共市场（anthropics/claude-plugins-official、aws GA）→ 官方垂直技能（Google Android、微软 Azure、dotnet）→ **企业内网注册中心（讯飞 SkillHub：命名空间 + Owner/Admin/Member + 审计日志 + 内容安全 + ClawHub 风格兼容层）**。三层同期都有动作
- **"控制平面失效必须响亮"的最佳样本**（2026-10-16，gastownhall/beads）：**Schema Version Guard** 在库比二进制新时直接退出，点名原因（v45 vs v42，3 migrations ahead）、说明后果（"查询被删/改名的列会以晦涩 SQL 错误失败"）、给三条修法 + 带风险的逃生口（`BD_IGNORE_SCHEMA_SKEW=1`）。同 repo 的 **HTTP divergence ledger** 把"HTTP 模式被拒/退化的操作"做成**生成的、可测试的清单**（与 diagram-design 的"保真台账"同构）
- **"给 Agent 装上眼睛"从纪律变成基础设施**（2026-10-16，iOfficeAI/OfficeCLI）：把高保真 HTML 渲染引擎放进单二进制，于是 render → look → fix 闭环可在 CI / Docker / 无显示器服务器上跑（`view html` / `view screenshot` 逐页 PNG / `watch` 实时预览）。配套 `merge` 模板合并把"贵的设计（设计一次）"与"便宜的填充（填 N 次、零 token）"切开，直击"Agent 每次从头重生成 N 份报告 → N 种版式"的失败模式
- **改名/迁移持续高频**（2026-10-16 再添两例）：`sst/opencode` → `anomalyco/opencode`（301 已核实）、`steveyegge/beads` → `gastownhall/beads`（301 已核实）、chatgpt-on-wechat → **CowAgent**（品牌重定位为 Agent Harness）。动机一致：摆脱上游宿主品牌；但分发入口仍集中在少数几家市场
- **推理引擎的新差异化轴 = 治理结构**（2026-10-16，lightseekorg/tokenspeed）：由**非营利 LightSeek Foundation** 支撑、"因此是开源的 Switzerland"，同时有 NVIDIA/AMD 硬件与工程支持。技术差异点是**控制面（C++ 有限状态机，编译期类型保证 KV 资源复用）/ 执行面（Python）分离**。注意口径：685 tok/s 是**每用户**吞吐，不是总吞吐
- **Agent 接口从 MCP 回摆到 CLI + Skills**（2026-10-19，厂商首次自我否定）：`microsoft/playwright-cli` README 第一节直接写取舍——**高频编码场景 CLI + Skills 更省 token**（不把庞大工具 schema 与冗长无障碍树塞进上下文）；**MCP 只在需要持久状态、丰富内省、对页面结构反复推理的循环里才值**（探索式自动化、自愈测试、长跑流程）。同日 `HKUDS/CLI-Anything` +5,051（"Making ALL Software Agent-Native"，`cli-hub matrix` 一条命令装完整个多 CLI 工作流）。**可复用判据：一次性、可脚本化 → CLI；有状态、要反复内省 → MCP**
- **"权限面"是 Agent 隔离的第四层**（2026-10-19，github/gh-aw）：已有策略面（mxc）→ 编排面（agent-sandbox）→ 内核面（litebox），GitHub 补上**权限面**：Agent job **默认只读 + 沙箱**，写操作先缓冲进 `safe-outputs`，校验后在**单独 job 用受限权限**落地。同一抽象在应用层由 `BuilderIO/agent-native` 实现（action 层是 UI 与 Agent 的唯一入口，*"The agent does not click through the UI"*）
- **确定性归 CI、推理归 Agent**（2026-10-19，gh-aw 的官方分工表述）：*"Use conventional GitHub Actions for deterministic builds, tests, linting, deployments… Add an agentic workflow when a task needs reasoning or interpretation."* 可直接抄进团队规范；同 repo 另有**整段版本撤回**的诚实样本（`>= 0.83.3, < 0.85.4` 因 GHSA-8h78-hpm7-29gg 全部标记不可用，当前 v0.92.0）
- **控制面从"配置"上移到"调度"**（2026-10-19 三例）：cc-switch（10-12）管 10 个 CLI 的 endpoint 切换 → **Orca** 管 33 个 CLI 的**并行 worktree 执行 + 结果择优**（一个 prompt 扇出 5 个 Agent 各占一个 worktree）+ 手机端遥控 + 额度热切换 → **Coder Agents** 把 Agent 循环放进控制平面、**工作区里没有 API key**、每动作带用户身份。**共同判断：Agent 不该住在工作区里**
- **"Agent 花钱"闭环补齐**（2026-10-19，devaccuracy/ledgerforge）：10-15 apify 解决"怎么付"（x402 / AGI token / Skyfire），ledgerforge 解决"**付多少、谁批、怎么查**"——每 API key 独立币种/精度上限 + 余额与账本白名单 + 每日预算 + **审批挂起由服务端强制**，派生 key 继承限制并共享祖先预算，**审批人凭据必须在 Agent 权限之外**；`ledgerforge verify` 只读重放，`audit verify --anchor` 对独立保存的根锚定。**缺"服务端强制 + 凭据分离"等于没护栏**
- **记忆层问题定义从"Agent 查得到"变成"人查得到"**（2026-10-19，claude-mem v14.0.0）：My Work 是**工作台账**不是检索器（Cards/List/Agents 三视图 + Attention first 排序 + 状态机 In progress/Needs you/No recent update/Ready to check/Checked）。核心约束原文：*"an agent reporting 'done' is never mistaken for a person confirming it"*。**与"解析通过≠跑过"（Game Studios）、"配置被接受≠生效"（Soup）同族：系统状态不能自我认证**。商业化 = 开源部分免费 + TeamBrain **$50/席/月**
- **厂商官方插件开始跨 harness 分发**（2026-10-19，Unity）：`unity-agent-plugin` 同一份插件同时上 **Claude Code / Codex / Grok**（`0.1.8-beta`，`/unity:` 前缀暴露 skills）；Orca 支持列表里出现 **CodeBuddy / DeepSeek Harness / Kimi / Qwen Code / MiMo Code / ZCode**。**单押 Claude Code 的时代结束**
- **移动端自动化定型为"读结构不读像素"**（2026-10-19，mobile-next/mobile-mcp）：从原生**无障碍树**驱动，**不用视觉模型、不消耗图像 token**，必要时才退截图+坐标；一套工具打 iOS/Android 模拟器与真机；30+ 工具含 `mobile_batch_commands`（一次调用串多步）、`mobile_fold_device`、`mobile_set_location`。同期 Google 发官方 `android/skills`
- **文件边界漏洞的通用模式 = 路径先解析再判权**（2026-10-19，mobile-mcp v1.0.11）：输出路径**逐级解析 symlink 后**再校验白名单（此前符号链接可把截图/日志/录像重定向到白名单外），symlink 成环或层数过多直接拒绝。同类：claude-mem"每次读取绑定根内已校验的确切文件"、gods-eye-view"凭据走服务端代理"。**只校验字面路径等于没校验**
- **star 尖峰 ≠ 趋势事件**（2026-10-19，debpalash/VoiceStudio）：主榜 daily **+42,036**（总 76,013）为当日全站最大增幅，但 `releases.atom` 最新仍是 **v0.5.6（09-23）**，停更 26 天。与 claude-quickstarts 的"最后提交 10-07 仍 +370"同类：**必须先查 release/commit 时间，再决定是否当新闻**
- **数据新鲜度被明码标价**（2026-10-19，Open-Dev-Society/OpenStock）：社区版报价**每小时**、Cloud **$5/月 15 秒**、自托管可 `NEXT_PUBLIC_OPENSTOCK_DATA_MODE=realtime` 自带 Finnhub key。比"实时行情"四个字有用，属诚实披露的细分（第七级：**把延迟写成价格表**）
- **"技能 + 已生成语料"双层结构**（2026-10-19，xbtlin/ai-berkshire）：20 个投研 skill 给流程，**2,246 份已生成报告 / 108 家公司 / 26 个专题**给基线，让用户先看输出长什么样再决定是否用。可迁移方法：**每条论断 3 个独立 Agent 对抗验证，3 票中 2 票证伪才剔除**（实战例：106 个检索/验证 Agent、23 条论断三票制）。**注意实盘收益为自报、README 有公众号导流、建议 `--dangerously-skip-permissions` 属高风险**

---

## 6. 未核实 / 存疑

- 各仓库 star 数、forks 数为抓取时点数值，随时间变化；增幅口径（今日/本周/本月）不可跨榜比较。
- 仓库 README 中的自述指标（如 ECC 的 277k star、open-code-review 的"两年服务数万开发者"、billion-context 的 174,327 次调用实证、atomic-agent 的 GAIA L1 69.8%）均为**项目自述**，未独立复核。
- billion-context 的论文级实证数据与其自身 `Status: Early / mock 测试通过` 的成熟度口径**不同**，引用时需分开标注。
- **mimic（重放 App 认证 token）与 opencode/uniterm 类"内置 Agent 执行 shell"的项目未在 README 提供伦理/授权边界声明**，使用前需自行判断合规性。
- 2026-10-12 为跨周末三天后的首次运行，daily 榜新面孔率 0；同日第二次运行进一步证明主榜已彻底固化，**语言榜的 `since` 维度是唯一稳定出口**。
- 2026-10-13 主榜 42 条中仅 3 条全新面孔（ai-engineering-from-scratch / mattpocock/skills / diagram-design），10 条详细中 7 条来自语言榜。**扩至 18 个语言榜后新增 5 个榜贡献 8 个新面孔，收益为正，建议保留。** 抓取 21 榜 0 次重试一次全过（对比 10-09 大面积 504）——**504 是间歇性问题，重试机制仍必须常备**。
- Game Studios 的 rigor 对照数据、diagram-design 的"不可 diff"自述、yuE2 的 WildSongBench 分数均为**项目自述**，未独立复核。
- YuE2 声称"与 Suno v5/v6 有竞争力"、6.9632 SongBench Avg 为**自建基准上的自报最优均值**，评测协议与对手版本未独立验证。
- Madeira 依赖 iOS 26+ 且 JIT 需调试器附着，**其"无越狱"路径的实际可持续性（每周重签、未来 iOS 版本策略）未经独立验证**。
- **2026-10-15**：主榜 46 条中仅 3 条新面孔（vxcontrol/pentagi、K-Dense-AI/scientific-agent-skills、twostraws/SwiftUI-Agent-Skill），10 条详细中 7 条来自语言榜。**相隔 2 天（10-13 → 10-15）后主榜仍未刷新出新面孔，说明头部固化不是"日内现象"而是持续状态。**
- **2026-10-15 抓取统计**：主榜 3 个 + 语言榜 18 个 = 21 榜并发，**0 次重试一次全过**（10-09 曾 21 榜大面积 504）→ **504 确认为间歇性问题，重试机制必须常备但不必预判失败**。
- **2026-10-15 数据异常需存疑**：rea 的 weekly +214,837 与 daily +41,034 均直接取自 GitHub trending HTML（属榜单官方口径），但**从 10-07 的 10,401 到 10-15 的 249,843（8 天约 24 倍）幅度极端**，是否为真实增长、是否有非自然因素（推广、刷星、榜单计算口径变化）**未独立验证**。引用时应保留该保留态度。
- **2026-10-15 项目自述未复核**：Soup 的 119.6 / 208.6 tok/s 与 3.32 / 2.40 GB 峰值（含"逐位一致"主张）、PentAGI 的 20+ 工具与 10+ 供应商清单、Project NOMAD 的 5 GB / <1 GB 内存与 25 GB 装机量、K-Dense 的 177 技能与 100+ 数据库、ruflo 的 314 MCP 工具 / 26 命令 / 100+ Agent、dotnet/skills 的 Skill Value 面板指标、apify 的"数千 Actor"**均为项目自述，未独立复核**。
- **google/agentmesh 的"pre-1.0 + 非 Google 官方支持产品 + 不在 Google OSS 漏洞奖励计划内"是 README 自述**；其"两个公开 testnet 已验证身份与策略模型"的说法未独立验证，`bananas.sam-mesh.dev` 是**无可用性承诺的共享开发 testnet**，不应作为生产依赖。
- **Anubis 的"会挡住 Internet Archive 等好机器人"为作者自述**，实际误伤范围取决于 bot policy 配置，未独立测试。
- **twostraws/SwiftUI-Agent-Skill 的 `total=6,001` / `forks=218` 取自 main weekly 榜**；其语言字段在榜单中为 `-`（技能类仓库无 `programmingLanguage`），报告中标为 Markdown 属推断，**非榜单原值**。
- **`ggml-org/Llama-Windows` 总星仅 128（forks 17）**，属全新仓库；README 中"无遥测、只带 UA"为自述，未抓包验证。
- **2026-10-16 主榜仍只 3 条新面孔**（daily 13 / weekly 11 / monthly 22 = 46 条），且 weekly 唯一新面孔 AnyPS5 在 10-13 结论里以纯文本被提过一次。**"速览里只提过一行也算已推送"的严格标准必须保留。**
- **2026-10-16 项目自述未复核**：OpenViking 的 LoCoMo 24–57%→80–83% 与 tau2-bench +6.87/+11.87pp（自建 benchmark 目录，评测用 Doubao 2.0 Pro + Doubao-embedding-vision-251215）；TencentDB Agent Memory 的 PersonaMem 48%→76%；tokenspeed 的 685 tok/s/用户（GB300）与 580 TPS（Qwen3.5-397B-A17B）；jcode 的全部内存与首帧数字（自测于 2026-09-29，jcode v0.89.19-dev vs Claude Code 2.1.267，脚本 `scripts/bench_headless_memory.py`）；darwin-skill 的 80.8→91.5→91.65 与 86.05→92.05→92.7；iflytek SkillHub 的"企业级/被企业信任"；OfficeCLI 的"世界第一个且最好的 Office suite for AI agents"与 350+ 函数覆盖度；KittenTTS 的"CPU 实时"；Hy-MT2 的"超过 DeepSeek-V4-Pro / Kimi K2.6 / 微软与豆包商用 API"。**均为项目自述，未独立复核。**
- **2026-10-16 授权/许可需注意**：OpenViking 主项目 AGPLv3 **并附附加条款**——禁止"整体重写后再开源"，且"把全部或大部分代码翻译成另一种语言需书面授权"；KittenTTS 为 Apache-2.0 但提供商业支持与自定义音色（音色克隆的合规边界未在 README 展开）；AnyPS5 为 GPL-2.0，免责声明写明不含/不分发/不要求受版权保护的软件、固件、密钥或专有库。
- **2026-10-16 需要保留怀疑态度的数据**：morluto/rea 的 weekly **+239,477**（10-07 为 10,401 → 10-15 总 249,843 → 10-16 总 276,337），极端幅度是否为真实增长、有无非自然因素（推广、刷星、榜单口径变化）**未独立验证**；`LibreSpark/LibreTV` 的 forks（28,795）**超过** stars（18,264），属罕见比例，未核查原因。
- **2026-10-16 归属变更已核实但影响未评估**：`sst/opencode` → `anomalyco/opencode`（301 确认，README 安装入口与 brew tap 同步改名）；`steveyegge/beads` → `gastownhall/beads`（301 确认）。**功能面是否随组织变更发生调整（治理、维护者、路线）未评估。**
- **Hex-Rays 官方 IDA MCP 的成熟度未评估**：`HexRaysSA/ida-mcp` 存在（1,194 star，"Official Hex-Rays IDA MCP Server"，最后推送 2026-10-08）为 REST API 核实；但 mrexodia 的"官方版更好"是**作者单方面建议**，两者功能覆盖度未做对比测试。
- **2026-10-19（14:00 场）自述未复核**：Orca 的"33 家 Agent"与"一个 prompt 扇出 5 个 worktree"、rakazo 的"对标 7 家产品"、ledgerforge 的会计保证与"测试/漏洞/模糊测试门禁"、mobile-mcp 的"fast and cheap"、ai-berkshire 的实盘收益（2024 +69.29% / 2025 +66.38%）与 2,246 份报告、claude-mem 的 My Work 交互细节，**均为项目 README / release 自述，未独立复核**。
- **2026-10-19（14:00 场）未查明**：VoiceStudio 今日 **+42,036** 的具体原因（无新版本、未找到外部推荐源，仅能确认 release 停在 09-23）；orca v1.4.230 的实际变更（release body 为空）。
- **2026-10-19 已核实**：gh-aw 安全公告区间 `>= 0.83.3, < 0.85.4` 与最新版 v0.92.0（10-15）；mobile-mcp v1.0.11 的 symlink 逐级解析修复条目；claude-mem v14.0.0（10-17 15:50 UTC）/ v14.0.1（16:25 UTC）时间戳；各仓库 license（agent-native `null`、unity-agent-plugin `NOASSERTION`、其余 Apache-2.0 / MIT）。
