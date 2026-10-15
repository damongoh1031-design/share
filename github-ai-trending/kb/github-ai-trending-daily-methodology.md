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
updated: 2026-10-15
version: 1.3.0
status: stable
source: 本工作区 2026-09-17 ~ 2026-10-15 共 19 次自动化运行实测
confidence: 已核实
---

## 一句话结论

**主榜（daily/weekly/monthly）头部已固化，语言维度榜 `/trending/<lang>` 是唯一稳定的新面孔来源；语言榜固定抓 18 个（2026-10-13 新增 csharp/kotlin/ruby/shell/php 后收益持续为正：10-15 期 10 条详细中 7 条来自语言榜，csharp / go / c++ 三榜最集中）。同日第二次运行必须换「周期」而不只换「语言」——「语言 × weekly」+「语言 × monthly」+「口语语言榜 zh/en」一次可拿到 270 条未推送仓库。抓取必须用"带重试的 curl 落盘 + 本地正则解析"，不要依赖脚本自带的网络层；解析要按 `<article class="Box-row">` 分块，仓库名用 `href="/(owner)/(repo)"[^>]*class="Link"><svg` 命中，且**总 star 数在 `</svg>` 之后**（不在 `/stargazers"` 紧邻处，否则会把"N stars today"的增幅误当总数）。**⚠️ 2026-10-15 新增关键坑：`fetch_trending.py` 的 `merge()` 会跨榜取 max 增幅，导致同一仓库的 weekly 增幅被当成当日增幅（rea 实测 weekly +214,837 掩盖了 daily +41,034）。报告必须逐条标注来源榜与周期，绝不可把合并后的单一数字当"当日增幅"使用。**

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

同一天跑第二次时，**主榜必然 100% 重复**（trending 日内不刷新候选池），语言 × daily 也已用尽。可用维度按性价比排序：

| 顺序 | 维度 | URL 形态 | 实测产出 |
|---|---|---|---|
| 1 | 语言 × weekly | `/trending/<lang>?since=weekly` | 14 语言 → 多数条目全新 |
| 2 | 语言 × monthly | `/trending/<lang>?since=monthly` | 7 语言 → 高增幅新面孔（hydradb +10,029 / PI-Desktop +4,031） |
| 3 | 口语语言 × daily/weekly | `?spoken_language_code=zh\|en&since=daily` | 中文项目（WeFlow / Bili23 / TikTokDownloader / tvbox） |
| 4 | trending developers | `/trending/developers?since=daily` | 只看人不看仓库，价值最低 |

**核心认知：`since` 是比 `lang` 更强的"换榜"开关** —— 同一语言的 daily/weekly/monthly 是**互不重叠**的三批仓库。

### 2.6 本工作区已固化的四个脚本（2026-10-15）

放在 `<workspace>/.workbuddy-ai/scripts/`，可直接复用：

| 脚本 | 用途 | 关键点 |
|---|---|---|
| `fetch_trending.py` | 主榜三榜合并输出 markdown 表 | **不支持 `--lang`**；`merge()` 跨榜取 max gain（见坑表），需要当日数据时别用它 |
| `grab.sh <outdir>` | 并发抓 3 主榜 + 18 语言榜（daily），每 URL 最多 8 次重试、判据 `code==0 && size>100000` | 21 榜一次跑完；`xargs -P` + `&`/`wait` |
| `atoms.sh <outdir>` | 并发抓 30+ 仓库的 `releases.atom` | `xargs -P 10`，用于"已推送仓库是否有新版本" |
| `readmes.sh <outdir>` | 并发抓 README，`HEAD` → `main` → `master` 三支兜底 | 27 个仓库全部一次成功 |

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
| **合并后增幅被跨榜污染** | `fetch_trending.py` 的 `merge()` 对同一仓库取**跨榜最大** gain；2026-10-15 实测 rea 显示 "+214,837"，实为 **weekly** 增幅，其当天 daily 仅 +41,034 | **不要用合并后的单一数字描述"当日表现"**；需要当日数据时回到 `main_daily.html` / `lang_daily_*.html` 单独取数。报告速览表必须带"来源榜"列 |
| **`releases.atom` 的 `<updated>` 在 `<title>` 之前** | 用 `grep -oE '<title>…|<updated>…'` 顺序读会整体错位一格 | 一律按 `<entry>` 块 `re.findall` 切分，再在块内分别取 `<title>` / `<updated>` / `<content type="html">`；正文用 `html.unescape` + `re.sub(r'<[^>]+>','')` |

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
