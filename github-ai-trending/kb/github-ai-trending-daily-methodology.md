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
updated: 2026-10-13
version: 1.2.0
status: stable
source: 本工作区 2026-09-17 ~ 2026-10-13 共 18 次自动化运行实测
confidence: 已核实
---

## 一句话结论

**主榜（daily/weekly/monthly）头部已固化，语言维度榜 `/trending/<lang>` 是唯一稳定的新面孔来源；语言榜应固定抓 18 个（新增 csharp/kotlin/ruby/shell/php 收益为正，本期 5 个新榜贡献 8 个新面孔）。同日第二次运行必须换「周期」而不只换「语言」——「语言 × weekly」+「语言 × monthly」+「口语语言榜 zh/en」一次可拿到 270 条未推送仓库。抓取必须用"带重试的 curl 落盘 + 本地正则解析"，不要依赖脚本自带的网络层；解析要按 `<article class="Box-row">` 分块，仓库名用 `href="/(owner)/(repo)"[^>]*class="Link"><svg` 命中，且**总 star 数在 `</svg>` 之后**（不在 `/stargazers"` 紧邻处，否则会把"N stars today"的增幅误当总数）。**

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

**实测数据**：2026-10-12 上午（语言 × daily）主榜 daily 8 / weekly 12 / monthly 22，14 语言榜去重 181 条；**同日下午（语言 × weekly + monthly + 口语语言）主榜 42 条 100% 重复**，26 个榜去重 353 条、其中 **270 条从未推送**。

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

---

## 3. 输出结构（固定）

1. 头部：数据源构成 + 主榜固化程度说明 + 口径声明（"trending 排序 ≠ 增幅排序"）
2. 榜单速览表（# / 仓库 / 语言 / 总 star / 增幅 / 来源 / 一句话）
3. 10 条详细：**事件**（何时上榜、增幅、版本号）→ **核心内容**（bullet，带具体数字与命令）→ **值得关注的原因**（技术判断 + 与前期的关联）
4. 其他趋势速览（大厂官方 / 运行时沙箱 / 中文生态 / 工具基础设施 / 已推送仓库新版本）
5. 当日主线判断（8–10 条编号结论）
6. 方法论脚注

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
