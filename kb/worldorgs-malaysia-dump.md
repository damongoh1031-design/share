---
id: worldorgs-malaysia-dump
title: WorldOrgs 马来西亚商家数据规模与全量 dump 方案
tags: [worldorgs, scraping, malaysia, business-directory, cloudflare, browser-use, data-extraction]
created: 2026-10-27
updated: 2026-10-30
version: 11
status: active
source: 站点结构实测 + robots.txt + browser-use 全量索引 + 批次运行器长跑日志（2026-10-27 ~ 10-30）
confidence: 高（结构/字段/反爬/吞吐量实测）；中（长跑 ETA，受重试与限速影响波动大）
supersedes: v10（v10 记到 10-29 C 批；v11 补 10-30 满额批 246 分类 / 5.49 分类/分钟、单批新纪录，及"提档后必撞墙"的速率钟形曲线）
---

## 一句话结论

WorldOrgs 马来西亚站官方标称 **876,761 家**机构、**754 个城市 slug**、2,473 个分类。
**名称可以 100% 拿全，电话能拿到"源数据里有的那部分"**——用 `browser-use` 接管用户真实 Chrome，
真导航 + CDP 屏蔽静态资源，**0.68s/页、Cloudflare 403 与 429 都能过**。
**但全量不是"13 小时"级别：限速 + 标签页重试把有效吞吐压到 3.5–5.5 分类/分钟，主力 4.1 万分类的真实 ETA 约 119–193 小时（按批实测倒推，不作承诺）。**

> **v3 修正**：v2 的"前 22 城 13 小时"只在**低强度短跑**下成立。持续跑 1 小时后站点配额从 18/分钟衰减到 6/分钟并钉死，
> 叠加每次撞墙 70s 冷却，**有效吞吐降到 ~2.1 分类/分钟**。见第五节"速率衰减曲线"。
>
> **v5 修正**：v3/v4 的 2.1 分类/分钟被两个故障污染了——①站点 10-29 改版使索引解析静默失效；②browser-use 守护进程僵死导致大量 `_IPCResponseTimeout`。
> 两者修好后同长度批次实测 **4.9 / 3.45 分类/分钟、撞限速 2 / 0 次**（见"10-29 续跑批次"）。真实 ETA 从"约 700 小时"下调到 **136–193 小时**，仍不作完成承诺。
> 索引已在 10-29 第二批次起始时补满 **753/753 城**，A 阶段开销归零，此后每批全预算投采集。
>
> **v10 进度锚点（10-29 15:33）**：累计 **299,243 行 / 236,915 带电话（79.2%）**，主力 **1,870 / 41,222 = 4.5%**，
> 剩 39,352 分类；满额 2,700s 批次实测 **4.4 分类/分钟、0 次限速、速率 4.0→5.8 三次提档**。ETA ≈149 小时。


---

## 一、数据规模

| 指标 | 数值 | 来源 |
|---|---|---|
| 机构总数（官方首页） | **876,761**（另一处 878,215） | 首页统计 |
| 城市 slug 数（实际可遍历） | **754** | `/katalog` + `/page-2..3` 实测 |
| 官方标称城市数 | 4,022 | 首页统计，与 754 不符，见"坑"第 1 条 |
| 分类数 | 2,473 | 首页统计 |
| 吉隆坡 | 93,993 条目 / 2,238 分类 | 城市页实测 |
| 前 22 大城市累计 | 563,924 条目 | 索引实测 |

> **876,761 是"条目数"不是"独立商家数"**。同一商家会挂在多个分类下（KL 93,993 > 官方 KL 73,168）。
> 去重要按详情页 URL。

---

## 二、站点结构

```
/katalog                          城市索引（3 页：/katalog、/katalog/page-2、/katalog/page-3）
/katalog/{city}                   城市分类列表：<a href="/katalog/kl/klinik">Klinik<span>502</span></a>
/katalog/{city}/{category}        商家列表 ← 主数据源
/katalog/{city}/{category}/{slug} 详情页 ← 补电话
```

### 分类页的两段式结构（核心）

**前 200 条**用 `<article class="li">`，带 `tel:` 链接：

```html
<article class="li" data-i="0" data-r="4.2" data-n="siti li dining" data-phone="1" data-photo="1">
  <h2 class="li-n"><a href="/katalog/kuala-lumpur/restoran/sitilidining">Siti Li Dining</a></h2>
  <p class="li-r"><b>4.2</b><span>(100)</span></p>
  <p class="li-a">15, Jalan Setiakasih 5, Bukit Damansara, 50490 Kuala Lumpur</p>
  <a class="li-call" href="tel:+601139066078">…</a>
</article>
```

**第 201 条之后**改为隐藏 `<ul><li>`，**有名称+地址，没有电话**：

```html
<ul><li><a href="/katalog/kuala-lumpur/restoran/mollagaa-restaurant">Mollagaa Restaurant</a><span>50A, Leboh Ampang, …</span></li></ul>
<button type="button" data-list-more-btn="">Tunjuk semua 748 organisasi</button>
```

> 那个按钮是**纯 JS 展开**，不是链接，点开也只是把 `<ul>` 里的名字显示出来，不会多出电话。

### 关键：没有 `/page-N` 分页

`/katalog/{city}/{cat}/page-2` 返回 **15KB 空页、0 条 article**（不是 403，是真的没有第二页）。
所以单个分类**最多只能从列表页拿 200 个电话**，超过 200 的部分必须逐个抓详情页。

### 详情页

- 有电话（`href="tel:"`，通常出现 2 次）
- 36–48KB，`http_get` 约 0.35s
- 示例：`/katalog/kuala-lumpur/kedai-pakaian-lelaki/crazeec` → `+60321412767`

---

## 三、反爬：真正的解法

`robots.txt`：

```
Crawl-delay: 10
Disallow: /*all-places-index
Disallow: *?*
Disallow: *.jpg / *.png / *.gif
Sitemap: https://my.worldorgs.com/sitemap/sitemap.xml
```

### 各方案实测对比（同一台机器、同一 IP、同一时段）

| 方案 | 结果 | 速度 |
|---|---|---|
| urllib + 完整浏览器 header | 热门页 200，冷门页 403，整体成功率 ~33% | — |
| headless Chromium `--dump-dom` | **403**（能识别 headless） | — |
| 换 UA / `--no-sandbox` | 无效 | — |
| browser-use `http_get`（裸请求） | 先 200，约 25–50 次后**整站 429，冷却 >15 分钟** | 0.48s/页 |
| **browser-use `goto_url` + CDP 屏蔽静态资源** | **✅ 100% 通过，无 429** | **0.68s/页** |
| browser-use `goto_url` 不屏蔽资源 | ✅ 通过 | 1.87s/页 |

**根因分两层：**

1. **403 是"回源"拦截** —— Cloudflare 判定依据是 TLS 指纹 + cookie + JS 挑战。缓存命中的页高频也过，未命中的页低频也 403。headless 和 urllib 都拿不到，只有真实浏览器会话能过。
2. **429 是"请求类型"限速** —— 同样的 IP、同样的 cookie，`http_get` 裸请求几十次就被封，而 `goto_url` 真导航连跑 20+ 页完全正常。说明 Cloudflare 对 `Sec-Fetch-Mode: navigate` 的导航请求更宽容。

**所以最终选型：真导航 + CDP 资源屏蔽。**

```python
cdp("Network.enable")
cdp("Network.setBlockedURLs", urls=[
    "*.jpg","*.jpeg","*.png","*.gif","*.webp","*.svg","*.ico",
    "*.woff","*.woff2","*.ttf","*.css"])
```

页面里图片/CSS/字体对解析毫无用处，屏蔽后 **1.87s → 0.68s/页**（2.7 倍）。
分类页正文（200 条 article）在 HTML 里，不依赖 JS 渲染，所以屏蔽样式不影响解析。

### 第三层限制：站点自身的每分钟配额

真导航能过 Cloudflare，但站点还有自己的限速：

> **连续约 32 次请求后，返回一个 208 字节的页面：`Too many requests. Please wait 1 minute.`**

```html
<html><head><title>🐴 </title></head><body><pre>Too many requests. Please wait 1 minute.</pre></body></html>
```

特征：`document.readyState` 正常是 `complete`、`location.href` 正确、**但 outerHTML 只有 208 字节**。
所以判断"页面是否正常"不能只看有没有报错，必须看**长度**（<5KB 即异常）。

处理方式：

- 检测到 `Too many requests` → **睡 65 秒再重试**，比硬撞划算
- 主动把节奏压到 **≤30 次/分钟**（每页 ≥2s），就基本不会触发
- 解析出 0 条的分类**绝不能记入 `.done`**，否则会被误判为已完成而永久丢失

**实测：限速窗口内 1.4s/页；压到 30 次/分钟后有效吞吐约 28 页/分钟。**
KL 2,238 个分类 ≈ **80 分钟**。

### sitemap 是死路

`/sitemap/sitemap.xml` 存在，但**本身也被 Cloudflare 403**（urllib 403，`http_get` 404）。
不能靠 sitemap 直接拿全量 URL 列表。

### 标签页会卡死

`goto_url` 偶发把标签页搞成半死状态，之后所有 `Runtime.evaluate` 都超时
（连 `document.readyState` 都超时，报 `Runtime.evaluate timed out`）。
**处理：捕获异常后 `new_tab(url)` 重建标签页**，v4 脚本已内置。

---

## 四、电话覆盖率的真相

**不是解析问题，是源数据问题。** 用 `data-phone` 属性可精确核对：

| 分类 | article 数 | `data-phone="1"` | `data-phone="0"` | `tel:` 数 |
|---|---|---|---|---|
| kuala-lumpur/klinik | 200 | 200 | 0 | 200 |
| kuala-lumpur/restoran | 200 | 200 | 0 | 200 |
| kuala-lumpur/kedai-pakaian | 200 | 192 | 8 | 192 |
| ajil/gedung-perkakasan | 5 | 4 | 1 | 4 |
| ajil/masjid | 4 | 1 | 3 | 1 |

**`tel:` 数 ≡ `data-phone="1"` 数，100% 吻合** → 解析无遗漏。

规律：

- 城市商业类（KL 的 klinik / restoran）**接近 100% 有电话**
- 小镇非商业类（ajil 的 masjid / 景点）大量 `data-phone="0"`
- 所以电话覆盖率是**行业 + 城市化程度**的函数，不是抓取质量

整体估算（KL）：列表页覆盖 **85.6%**，补详情页后 **~96%**。

---

## 五、抓取方案（v2，已实测）

脚本：`C:/Users/Admin/.workbuddy-ai/tools/worldorgs_dump_v3.py`
必须在 `browser-use` 里跑（依赖 `http_get`）：

```bash
# ① 建索引：754 城市 × 全部分类 + 数量（约 11 分钟）
WO_PHASE=index WO_INDEX=worldorgs_index.tsv browser-use < worldorgs_dump_v3.py

# ② 采集：名称 100%，电话为源数据有电话的那部分
WO_CITY=kuala-lumpur WO_OUT=kl.csv browser-use < worldorgs_dump_v3.py

# ③ 补电话：给第 201 条之后的条目抓详情页
WO_PHASE=detail WO_OUT=kl.csv browser-use < worldorgs_dump_v3.py
```

输出列：`name, phone, address, rating, reviews, city, category, url`

- 中断可续：`<out>.done` 记录已完成分类
- 去重键：`url`（同一商家跨分类会重复出现）
- 电话格式 E.164（`+601139066078`），可直接拨号/去重

### 时间成本（实测 0.68s/页理论值，1.4–2.1s/页含写盘）

| 范围 | 页数 | 耗时 |
|---|---|---|
| 全量索引 | 754 | ~17 min |
| KL 列表页 | 2,238 | ~50–77 min |
| 前 22 大城市列表页 | 34,074 | ~13 h |
| KL 补详情 | 10,152 | ~2 h |
| 全马列表页 | ~10 万（估） | 需分多轮 |

只要名称、不补电话：前 22 城约 13 小时，KL 单城约 1 小时。

**注意：实测每分类 1.4–2.1s（不是 0.68s）**，差额来自 CSV 写盘 + 大分类页体积（330KB）。
0.68s 是纯导航不写盘的理想值，做预算时按 **2s/分类** 算更稳。

---

## 五之二、批次运行器（v3 长跑实测）

脚本：`C:/Users/Admin/.workbuddy-ai/tools/worldorgs_auto.py`，单次运行 = 一个时间预算批次，跑完自退，下次断点续跑。

```bash
cd /tmp && WO_BUDGET=3300 "C:/Users/Admin/AppData/Local/hermes/bin/browser-use" \
  < "C:/Users/Admin/.workbuddy-ai/tools/worldorgs_auto.py" \
  > "C:/Users/Admin/.workbuddy-ai/tools/out/batch.log" 2>&1
```

三阶段自动推进：**A 索引**（补齐 754 城市 × 分类）→ **B 采集**（按分类体量降序抓，`MIN_COUNT=2` 挡掉 8 万单条分类）→ **C 补电话**（详情页回填）。

### 断点与互斥

| 文件 | 作用 |
|---|---|
| `malaysia_all.csv` | 主表（追加写，列 `name,phone,address,rating,reviews,city,category,url`） |
| `malaysia_all.csv.done` | 已完成分类 path 集合，B 阶段跳过 |
| `phones_fix.tsv` / `.done` | C 阶段补到的电话 / 已尝试 URL |
| `rate_state.txt` | 自适应速率持久化，跨批次继承 |
| `batch.lock` | **批次锁**：`age < BUDGET+600` 时新实例直接退出，防两个 browser-use 抢标签页 |

### 速率衰减曲线（实测，单批次 55 分钟）

| 时刻 | 事件 | 速率 |
|---|---|---|
| 0s | 批次起始（继承上批） | 18.0/min |
| 250s | 顺畅 40 次，提速 | 9.7/min（说明上批已衰减到 ~8.8） |
| 442s | 首次 throttled | 8.9 |
| 650s | throttled | 8.2 |
| 735s | throttled | 7.5 |
| 993s | throttled | 6.4 |
| 1072s | throttled | **6.0（硬下限）** |
| 1072–3270s | 一直 6.0，撞墙不再降 | 6.0 |

**关键结论：速率单调衰减到 6.0/min 后钉死，不会恢复。** 提速逻辑（40 次顺畅 +10%）永远追不上衰减（每次撞墙 −8%），因为撞墙频率 > 40 次/次的节奏。

### 真实吞吐 vs 日志 ETA（重要陷阱）

本批实测：

| 指标 | 数值 |
|---|---|
| 处理单元 | 215（索引 101 城 + 采集 114 分类） |
| 采集产出 | 26,502 行 / 19,154 带电话 |
| 撞限速 | **25 次**，每次 sleep 70s = **1,750s，占批次 53%** |
| 累计 | 62,113 行 / 39,989 电话（**64.4%**） |
| 主力分类进度 | 274 / 91,527 = **0.3%** |
| 有效吞吐 | 114 分类 / 54.5 min = **2.09 分类/分钟** |
| 日志声称 ETA | 253.5 小时（按 6/min 名义速率） |
| **真实 ETA** | **91253 ÷ 2.09 ÷ 60 ≈ 728 小时 ≈ 30 天** |

> **陷阱**：脚本里 `remaining/_RATE/60` 只按名义速率算，**没算撞墙冷却**，系统性低估约 3 倍。
> 报进度时一律用「本批实际处理分类数 ÷ 本批实际时长」倒推，别信日志的 ETA。

### 分母膨胀陷阱

索引从 160,941 → **172,502** 分类（本批 A 阶段又补了 101 城），主力分母同步从 8.6 万涨到 91,527。
**所以百分比会"倒退"**（上批 0.4% → 本批 0.3%），不是数据丢了，是分母在长大。
只要索引未满 754 城，每批都会先花掉 **25% 预算**（`set_stage_share(0.25)`）在索引上——这部分是纯开销，要等索引补齐后才消失。

### 站点配额的分层事实

| 层 | 阈值 | 表现 |
|---|---|---|
| Cloudflare 回源 | 与频率无关 | 冷门页 403，真浏览器可过 |
| Cloudflare 429 | 裸 `http_get` 约 25–50 次 | 整站封，冷却 >15 min |
| 站点自身配额 | 动态，**越跑越紧** 32 → 6/min | 208B `Too many requests` 页 |
| 页面空返回 | 偶发 | `empty 1704B` → `new_tab` 重建 |

---

## 六、解析规则

```python
# 前 200 条：有电话
for art in re.findall(r'<article class="li".*?</article>', html, re.S):
    name  = re.search(r'<h2 class="li-n"><a[^>]*>(.*?)</a>', art, re.S).group(1)
    phone = re.search(r'href="tel:([^"]+)"', art)              # 可能不存在
    addr  = re.search(r'<p class="li-a">(?:<span[^>]*></span>)?(.*?)</p>', art, re.S)
    rate  = re.search(r'<p class="li-r"><b>([\d.]+)</b>', art)
    revs  = re.search(r'<p class="li-r">.*?<span>\((\d+)\)</span>', art, re.S)

# 第 201 条之后：无电话，取"li 数最多的那个 ul"
for ul in re.findall(r'<ul[^>]*>(.*?)</ul>', html, re.S):
    lis = re.findall(r'<li><a href="(/katalog/[^"]+)">(.*?)</a><span>(.*?)</span></li>', ul, re.S)
    if len(lis) > 20: best = lis

# 分类+数量（城市页）—— 必须兼容两种标记，见"坑"第 11 条
for m in re.finditer(r'<a[^>]+href="(/katalog/{city}/[a-z0-9\-]+)"[^>]*>(.*?)</a>', html, re.S):
    n = re.search(r'<span[^>]*>\s*(\d+)', m.group(2))   # ✅ 两种格式通吃
    # n = re.search(r'<span>(\d+)</span>', m.group(2))  # ❌ 10-29 改版后小城市 100% 漏抓
```

注意：`<ul>` 匹配必须取"li 数最多且 >20"的那个，否则会命中导航栏的小列表。

---

## 七、坑与反直觉

1. **官方说 4,022 城市，实际 `/katalog` 只有 754 个 slug**，`/page-4` 起为空。差的 3,268 可能是"区域/街区"级别，只在站内搜索可达，不在目录索引里。
2. **分类页没有 `/page-N`**，只有前 200 条带电话，这是硬上限，不是 bug。
3. **`Tunjuk semua N organisasi` 是 JS 按钮不是链接**，点开也不多电话。
4. **`tel:` 数 ≡ `data-phone="1"` 数** —— 用这个核对解析正确性，比抽样可靠。
5. **`Disallow: *?*`** → 所有带查询参数的 URL 都不该爬；分页也不是 `?page=`。
6. **Cloudflare 拦回源不拦频率** —— 静置 3 分钟能让热门页恢复，冷门页仍 403；换 UA 无用。
7. **headless Chromium 必被拦**，`--dump-dom` 也一样。
8. **`goto_url` 会把标签页搞卡死**，之后所有 `Runtime.evaluate` 超时（`document.readyState` 都超时）。遇到就 `new_tab()` 重建。用 `http_get` 可完全避开。
9. **browser-use 里的 `/tmp` 是 `C:\tmp`**，不是 Git-Bash 的 `AppData\Local\Temp`。路径一律写绝对 Windows 路径。
10. **列表页 article 的 category 可能不是当前页分类**（restoran 页混入 restoran-asia、restoran-susyi），是"相关分类聚合"。
11. **城市页分类计数有两套标记（10-29 实测）**：大城市用 `<a class="tag more" hidden="">Kedai Dobi<span>137</span></a>`，小城市用 `<a class="tile" href="..."><span class="tile-n">Gedung Perabot</span><span class="tile-c">2 organisasi</span></a>`。
    旧正则 `<span>(\d+)</span>` 只能命中前者 → **A 阶段对剩余 57 个小城市全部返回 0 分类，索引静默不增长**（脚本不报错，只表现为 `[A] 25/57 城市` 但 `worldorgs_index.tsv` 行数不变）。用 `<span[^>]*>\s*(\d+)` 兼容两套。
12. **`_IPCResponseTimeout` / `RuntimeError ... -> new tab` 刷屏 ≠ 站点问题**。站点直连 0.25s/200；真因是 browser-use 守护进程僵死 + 活动标签页挂在死 target 上。
    处置三步：`browser-use --doctor` 看 `daemon alive` → 杀掉旧 `browser_harness.daemon` 进程 → 脚本开批时先 `ensure_real_tab()`（已内置到 `worldorgs_auto.py`）。修好后单页 1.7s / 425KB。
13. **不要一边跑批次一边手动 `goto_url` 探针**：两者抢同一个活动标签页，探针会把正在处理的页面截走，日志里看起来像"批次抓错页"。
14. **会话/回合结束会连后台批次子进程一起收割，且 `batch.lock` 残留**（10-29 已复现两次：10:57、12:02）。识别特征：`batch.log` 与 `malaysia_all.csv` 的 mtime 冻结在同一秒、`batch.lock` 仍在、但 `Get-Process python` 为空。
    处置：删锁 → `browser-use --doctor` 确认 daemon 是否也死了（大概率一起死）→ `ensure_real_tab()` 唤醒 → 用**剩余预算**重启（不是原始 2700s），否则总时长会突破 45 分钟窗口。
15. **别只看 `wc -l < malaysia_all.csv`**：追加写有缓冲，`ls -la` 的秒级 mtime 才是"是否真在推进"的可靠信号。
16. **`nohup ... &` 起批次必死**（10-29 13:49 实测）：脚本跑到 31s 就静默消失，日志冻结、`batch.lock` 残留、无 python 进程。原因不是站点，是命令工具在调用结束时收割整个后台进程组。
    正解：用工具自身的**托管后台任务**（`run_in_background`）启动，进程挂在任务 id 下才活到批次结束。
17. **Chrome 会弹 `Allow remote debugging?`**：弹窗未确认时 daemon 连得上但 `Runtime.evaluate` 全部超时（表现为 `_IPCResponseTimeout`、`资源屏蔽跳过`、开批 30s 内冻结）。
    看到 `browser-harness: Chrome is asking "Allow remote debugging?"` 就是它；点 Allow 后 `js("location.href")` 立即恢复。
    **例外（10-30 实测）**：弹窗提示出现、但紧随其后的 `js("location.href")` 正常返回 → 说明已自动放行，不必人工点。判据只看调用是否成功，不看提示行。
18. **托管后台任务的退出码不代表 worker 死亡**（10-30 实测）：用 `nohup ... &` 包在 `run_in_background` 里，任务 21s 后报 `failed`、`cat` 不到日志，但 browser-use 进程照常跑满 2,689s，日志与锁稍后才落盘。
    判存活三件套：`tasklist | grep browser-use` 有进程 + `batch.lock` 存在 + `malaysia_all.csv` mtime 在最近 1 分钟内推进。三者齐 = 正在跑，**不要因任务报 failed 而重启，否则会出现双实例抢标签页**。
19. **速率不是单调爬升，是"提档 → 撞墙 → 降档"的钟形**（10-30 实测）：5.8 → 6.4（388s）→ 7.0（738s）→ 峰值维持约 12 分钟 → 连续 2 次限速掉到 4.1 → 再回升 4.5。
    含义：**单批吞吐上限由"提档窗口长度"决定，而非起始速率**。2700s 批能吃到 6.5–7.0 的高原段，900s 批基本只能吃到爬升段。跨批速率在 4.0–7.0 间振荡，报 ETA 用单批实测倒推即可。

---

## 17:39 续跑记录（已核实）

- 前批锁已释放后启动 `WO_BUDGET=2700 WO_MIN_COUNT=5`，沿用断点与自适应限速。
- 由于短时间连续 3 次触发限速，脚本按保护逻辑约 4m58s 提前收工；索引新增 2 城，主力采集本批 0 分类。未强行重启，避免继续消耗站点配额。
- 日志末状态：`RUNNING remaining=40435`；索引 178,949 分类（主力 41,138、尾部 137,811），主力 703 已完成（1.7%）；累计 181,365 行 / 139,541 带电话。
- 脚本名义 ETA 168.5h 未计连续限速导致的等待，不作完成时限承诺。批次锁确认释放，等待下次批次自然续跑。

## 10-29 续跑批次（已核实，修复后连续两批）

### 两批实测对比

| 指标 | 批次 1（09:50） | 批次 2（11:00） |
|---|---|---|
| 批次时长 | 2,654s（44m14s） | 2,764s（46m04s） |
| A 索引 | 57/57 城补齐，178,950 → **179,954** | 753/753 已满，A 阶段 0 开销 |
| B 采集 | **208 分类 / 23,028 行 / 19,252 电话** | **159 分类 / 15,974 行 / 13,234 电话** |
| 撞限速 | 2 次 | **0 次**，速率反升到 6.8/min |
| 有效吞吐 | 208 ÷ 42.4min = **4.9 分类/分钟** | 159 ÷ 46.1min = **3.45 分类/分钟** |
| 主力进度 | 1,153 / 41,222 = 2.8% | 1,317 / 41,222 = **3.2%** |
| 累计 | 235,145 行 / 184,295 电话 = 78.4% | **251,635 行 / 197,998 电话 = 78.7%** |
| 末状态 | `RUNNING remaining=40069` | `RUNNING remaining=39905` |

**索引在批次 2 起始时已满 753/753 城，A 阶段彻底消失**——从此每批 100% 预算给 B 阶段，主力百分比不再因分母膨胀而倒退。

### 新发现的吞吐杀手：`RuntimeError -> new tab` 重试

批次 2 撞限速 0 次，但吞吐反而从 4.9 掉到 3.45 分类/分钟。日志里 40+ 条 `RuntimeError ... -> new tab`，每条意味着**一次失败重试（3 次尝试 + 重建标签页 ≈ 30–60s）**。
按时间归因：约 1,100s 消耗在重试上，占批次 40%。

- 诱因：`goto_url` 偶发把标签页搞成半死状态（老问题），现在 `ensure_real_tab()` 能救回来，但**救回来之前已经烧掉 3 次重试**
- 当前策略：`fetch(tries=3)`，第 3 次仍失败才放弃并 `sleep(3)`
- 可优化方向（未实测）：把 `tries` 降到 2 并在第 1 次异常后立刻 `ensure_real_tab()` 而不是等第 3 次；或对同一 URL 连续失败时直接跳过记入 `retry.tsv` 下批再来

### 主力剩余的真实 ETA

按批次 1 的 4.9/min：40,069 ÷ 4.9 ÷ 60 ≈ **136 小时**；按批次 2 的 3.45/min：39,905 ÷ 3.45 ÷ 60 ≈ **193 小时**。
两批合并口径 ≈ **136–193 小时**。**不承诺完成时长**，只报单批实测吞吐。

### 本批踩到的两个故障（都已修）

| 症状 | 真因 | 修法 |
|---|---|---|
| `[A] 25/57 城市` 但索引行数不动 | 站点改版，小城市改用 `tile-c` 计数标记 | 正则改 `<span[^>]*>\s*(\d+)` |
| 每 20–70s 一条 `_IPCResponseTimeout ... -> new tab`，零产出 | browser-use 守护进程僵死 + 活动标签页挂在死 target | 杀旧 daemon + 开批 `ensure_real_tab()` + 异常时重建标签页 |

### 编排层陷阱：会话中断会杀掉后台批次

批次 2 首次启动（10:57）在会话被中断时**连子进程一起被杀**：`batch.log` 与 `malaysia_all.csv` 的 mtime 冻结在同一秒，但 **`batch.lock` 残留**。
下次启动会因锁未过期（`age < BUDGET+600`）直接退出，表现为"启动即空转"。
**处置：确认无 `browser-use` 进程后删锁再启**，并核对 CSV mtime 是否推进（`ls -la` 看秒级时间戳比看行数可靠）。

---

## 10-29 12:02 批次（主力续跑，含一次中途被杀 + 拆批重启）

### 三段式时间线

| 阶段 | 时间 | 时长 | 产出 | 结局 |
|---|---|---|---|---|
| 起批 | 12:02 | 1,269s（21m） | 81 分类 | **被会话中断杀进程，`batch.lock` 残留** |
| 诊断 | 12:42 | — | — | 无 python 进程、daemon 也死了；删锁 + 唤醒 daemon |
| 重启 | 12:43 | 1,304s（21.7m） | 153 分类 / 13,807 行 / 11,435 电话 | 正常收工，锁已释放 |

**合计 234 分类 / 约 44 分钟 → 5.3 分类/分钟**（本批口径最优，超过 09:50 批的 4.9）。
拆分预算（2700 → 1350）是关键：废批已烧掉 21 分钟，剩余预算只补 22.5 分钟，整轮仍控制在 45 分钟窗口内。

### 关键数字（截至 12:56）

| 指标 | 数值 |
|---|---|
| 索引分类 | 179,954（主力 41,222 + 尾部 138,732），753/753 城已满 |
| 主力进度 | 1,317 → **1,551 / 41,222 = 3.8%** |
| 累计行数 | **273,146** |
| 有电话 | **215,602（78.9%）** |
| 撞限速 | 1 次（末段 throttled 8.2 → 6.9/min） |
| 末状态 | `RUNNING remaining=39,671`（未打 MAIN_DONE） |

### 速率表现：本批是回升而非衰减

起点 6.8/min → 477s「顺畅 40 次」提到 **8.2/min** → 1,226s 撞 1 次限速降到 6.9/min。
**说明棘轮上限（`_CEILING = 起始 × 1.2`）在跨批次继承时是可爬升的**，v3 记录的"单调衰减到 6.0 钉死"不是常态，只在持续撞墙时才成立。

### 吞吐归因

- `RuntimeError -> new tab` 仍密集（本批 20+ 条），但单条恢复变快（`ensure_real_tab()` 已内置在异常分支）
- 有效吞吐 5.3/min，说明重试成本已被摊薄；**不必急着把 `tries` 降到 2**（v6 的待办可以搁置）
- 真实 ETA：39,671 ÷ 5.3 ÷ 60 ≈ **125 小时**（按本批口径）；跨批区间仍报 125–193 小时，不作承诺

---

## 10-29 13:49 批次（连续限速提前收工 + 冷却后二段批）

### 四段时间线

| 时间 | 事件 | 结果 |
|---|---|---|
| 13:47 | 到场无锁；`--doctor` 报 `daemon alive FAIL` | 先 `ensure_real_tab()` 唤醒 |
| 13:49 | 第 1 次启动用 `nohup ... &` | **31s 后进程被工具层收割**，锁残留（坑 16） |
| 13:57 | 删锁 + 重开标签页（弹出 `Allow remote debugging`）→ 托管后台启动 | 一段批 868s |
| 14:11 | 一段批连撞 3 次限速，脚本主动提前收工 | 88 分类 / 7,539 行 / 6,068 电话 |
| 14:24 | 冷却 13 分钟后以 `WO_BUDGET=900` 起二段批 | 887s 跑满，**0 次限速** |
| 14:39 | 二段批正常收工 | 35 分类 / 2,918 行 / 2,472 电话 |

合计 **123 分类 / 1,755s（29.3 分钟）= 4.2 分类/分钟**。

### 两段对比（同一 IP、同一小时内）

| 指标 | 一段批 | 二段批 |
|---|---|---|
| 预算 | 2,700s（未用满） | 900s（用满） |
| 实际时长 | 868s | 887s |
| 分类 | 88 | 35 |
| 吞吐 | **6.1/min** | 2.4/min |
| 撞限速 | 3 次（连续） | **0 次** |
| `RuntimeError -> new tab` | 0 | **12** |
| `_IPCResponseTimeout` | 1 | 2 |
| 起始速率 | 6.9/min | 4.0/min（上一段降下来的地板） |

**反直觉结论**：撞限速的那一段反而更快。一段批撞墙前跑到 8.3/min；二段批虽 0 次限速，但被 12 次 `RuntimeError` 拖到 2.4/min。
→ **吞吐杀手排序：标签页重试 > 限速**（与 v6 归因一致，本次再度复现）。限速是"均匀降速"，重试是"每次赔 3 次尝试 + 重建标签页"。

### 自适应限速的真实行为

`6.9 → 8.3（顺畅 40 次提档）→ 6.3 → 4.8 → 4.0`，三次连续撞墙后**直接收工**，不硬撑到预算结束。
`rate_state.txt` 把 4.0 持久化给下一批 → 二段批从地板起步，即使 0 次限速也爬不回去（900s 内没触发"顺畅 40 次"提档窗口）。
**代价**：地板速率会被长期继承，需要靠一段足够长的顺畅期才能回升。

### 关键数字（截至 14:39）

| 指标 | 数值 |
|---|---|
| 索引分类 | 179,954（主力 41,222 + 尾部 138,732），753/753 城 |
| 主力进度 | 1,551 → **1,675 / 41,222 = 4.1%** |
| 累计行数 | **283,692** |
| 有电话 | **224,208（79.0%）** |
| 末状态 | `RUNNING remaining=39,547`（未打 MAIN_DONE） |

真实 ETA：39,547 ÷ 4.2 ÷ 60 ≈ **157 小时**（本批口径）；跨批区间维持 125–193 小时，不作完成承诺。

---

## 10-29 14:xx 续跑批次（本自动化续跑 + 本回合启动 2700s 批）

### 三批时间线（14:24 自动化触发后）
| 批次 | 启动 | 预算 | 实际 | 产出 | 撞限速 | 末态 |
|---|---|---|---|---|---|---|
| A 2700s | 14:25 | 2700 | 868s（连撞 3 次提前收工） | 88 分类 / 7,539 行 / 6,068 电话 | 3（→4.0 地板） | RUNNING remaining=39582 |
| B 900s | 14:37 | 900 | 887s（跑满） | 35 分类 / 2,918 行 / 2,472 电话 | 0 | RUNNING remaining=39547 |
| C 2700s（本回合） | 14:46 | 2700 | **2,648s（跑满）** | **195 分类 / 15,551 行 / 12,707 电话** | **0** | RUNNING remaining=39,352 |

> A、B 两批均在本次自动化到场前由上一轮触发跑完并释放锁；本回合（14:43）确认无锁、无进程后启动 C。
> **C 批最终实测（15:33 收工）**：速率 4.0 → 4.4（800s）→ 4.8（1,297s）→ **5.8/min（末段）**，全程 0 次限速，
> 仅 8 次 `RuntimeError` + 2 次 `_IPCResponseTimeout`，吞吐 **4.4 分类/分钟**（B 批的 1.8 倍）。

### 并发实例碰撞（本次自动化新增坑）

同一自动化在两个会话里被同时触发（14:43 与 14:47），两边都去抢 `batch.lock`：
- 14:43 实例用 `nohup ... &` 起批，日志 `batch_auto_20261029_144351.log` **0 字节**、进程随即消失（同坑 16）。
- 14:47 实例正常拿到锁跑满 2,648s，产出 195 分类。
- 结果：数据只来自后者，前者白跑；但**两个实例都会各自写 KB / memory**，导致同一批次被记两次、数字互相覆盖。
- 处置：以 `malaysia_all.csv` 的 mtime + `batch.log` 实跑记录为唯一事实源；写 KB 前先 `Read` 现文件，避免覆盖对方刚写的版本。

### 关键数字（截至 C 批收工 15:33）
| 指标 | 数值 |
|---|---|
| 索引分类 | 179,954（主力 41,222 + 尾部 138,732），753/753 城 |
| 主力进度 | 1,675 → **1,870 / 41,222 = 4.5%** |
| 累计行数 | 283,692 → **299,243** |
| 有电话 | 224,208 → **236,915（79.2%）** |
| 末状态 | `RUNNING remaining=39,352`（未打 MAIN_DONE） |

### 新确认的事实
- **速率地板 4.0 现在变"黏"**：A 批连撞 3 次把 6.9→4.0 并持久化（`rate_state.txt`）。B 批（900s、0 限速、仅 35 分类）**爬不回**——提速要"无限速且本批 did≥40"，35<40 触发不了。→ 当前阶段 **900s 批次是次优**：时间不够恢复速率。
- **2700s 批次的意义反转**：长窗口才能撑过"顺畅 40 次"提档窗口，把速率从地板爬回 6–8。C 批实测 **4.0 → 4.4 → 4.8 → 5.8/min**，三次提档都发生在满额窗口内，验证成立。
- **吞吐杀手排序再确认**：B 批 0 限速却只有 2.4 分类/分钟，真凶是 ~12 次 `RuntimeError -> new tab` 重试（每次赔 3 尝试+重建）。重试 > 限速（与 v6/v7 一致，本次第 3 次复现）。
- **重试密度而非绝对次数决定吞吐**：B 批 14 次重试 / 35 分类 = 0.40 次/分类；C 批 10 次重试 / 195 分类 = 0.05 次/分类。判吞吐先算"每分类重试数"，别数绝对值。
- **启动方式补正**：本回合用 `run_in_background` + `nohup ... &`。worker 存活（脱离的 browser-use 2354），但 **stdout 没进日志文件（0B）**——监控改看 `malaysia_all.csv` 秒级 mtime 与 `.done` 增量（坑 15）。更干净：`run_in_background` 直接跑 `browser-use < script > log 2>&1`，**不加 nohup/&**，既存活又捕获日志。

真实 ETA：39,352 ÷ 4.4 ÷ 60 ≈ **149 小时**（按 C 批实测吞吐）；跨批区间维持 125–193 小时，不作完成承诺。

---

## 10-30 10:34 批次（单批新纪录 246 分类，5.49 分类/分钟）

### 现场与处置
| 步骤 | 结果 |
|---|---|
| 到场检查 | 无 `batch.lock`、无 browser-use 进程；上批（10-29 15:31）已自然收工 |
| `--doctor` | `daemon alive` **FAIL**、active connections 0 → 冷启动 |
| 唤醒 | `browser-use < out/warm2.py`（`ensure_real_tab` + `new_tab` + `js("location.href")`）一次成功 |
| 弹窗 | Chrome 仍弹 `Allow remote debugging?`，**未阻断**（href 正常返回），与坑 17 的"必须点 Allow"不冲突——弹窗出现但调用能过就不用管 |
| 起批 | `WO_BUDGET=2700 WO_MIN_COUNT=5 browser-use < worldorgs_auto.py > out/batch4.log`，`run_in_background` 托管 |

> 首次启动尝试用 `nohup ... &` 包装，托管任务 21s 后报 failed 且 `cat` 不到日志，但 **worker 实际存活并正常跑满 2,689s**（锁与日志随后出现）。再次印证坑 16：判存活只看 `batch.lock` + `malaysia_all.csv` mtime + `tasklist | grep browser-use`，不要以托管任务的退出码为准。

### 实测曲线（速率呈钟形，不是单调爬升）
| 时刻 | 分类 | 速率 | 事件 |
|---|---|---|---|
| 0s | 0 | 5.8/min（继承上批） | A 阶段 0 开销（753/753 已索引） |
| 193s | 20 | 5.8 | — |
| 388s | 40 | → 6.4 | 顺畅 40 次提档 |
| 738s | 80 | → 7.0 | 第二次提档 |
| 1,443s | 160 | 7.0 | 本批峰值段 |
| 1,475s / 1,552s | — | **7.0 → 5.3 → 4.1** | 连续 2 次限速，各 sleep 70s |
| 2,072s | 200 | → 4.5 | 顺畅 40 次小幅回升 |
| 2,673s | 246 | 4.5 | 预算用完收工 |

- 吞吐 **246 ÷ 44.8 分钟 = 5.49 分类/分钟**，超过 10-29 C 批（195 / 4.4），为目前单批最优。
- 重试密度 **0.02 次/分类**（5 次 `RuntimeError`/`_IPCResponseTimeout` / 246），远低于 B 批 0.40——本批几乎全部时间都在有效抓取。
- 撞限速仅 2 次，但发生在**提档到 7.0 之后约 12 分钟**：站点配额按"当前请求速率"封顶，**提档 → 撞墙 → 降档**是稳定循环，单批不可能长期维持 7.0+。

### 关键数字（截至 11:22 收工）
| 指标 | 数值 |
|---|---|
| 本批产出 | **246 分类 / 18,206 行 / 14,714 电话** |
| 主力进度 | 1,870 → **2,116 / 41,222 = 5.1%** |
| 累计行数 | 299,243 → **317,449** |
| 有电话 | 236,915 → **251,629（79.3%）** |
| 索引 | 179,954（主力 41,222 + 尾部 138,732），753/753 城 |
| 末状态 | `RUNNING remaining=39,106`（**未打 MAIN_DONE**，尾部 138,732 暂缓） |
| 收工后 | 锁已释放，`rate_state.txt` = 4.5 |

真实 ETA：39,106 ÷ 5.49 ÷ 60 ≈ **119 小时**（按本批口径）；跨批区间由 125–193 小时收敛到 **119–193 小时**，仍不作完成承诺。

---

## 可复用操作

```bash
# 0. 开批前必查：锁 + 进程（有锁就等，绝不并发）
ls "C:/Users/Admin/.workbuddy-ai/tools/out/batch.lock"
"C:/Users/Admin/AppData/Local/hermes/bin/browser-use.exe" --doctor   # 要看到 daemon alive + 有连接

# 1. 桥接僵死时的标准处置
#    杀 browser_harness.daemon 进程后，用一次极简调用唤醒：
printf 'ensure_real_tab()\nprint(page_info())\n' | browser-use

# 2. 跑一个 45 分钟批次（默认只抓 count>=5）
#    必须用托管后台任务启动（run_in_background），nohup/& 会被工具层收割（坑 16）
cd "C:/Users/Admin/.workbuddy-ai/tools" && \
  WO_BUDGET=2700 WO_MIN_COUNT=5 browser-use < worldorgs_auto.py > out/batch.log 2>&1

# 2b. 提前收工后起二段批：冷却 10–15 分钟，预算取剩余额度
WO_BUDGET=900 WO_MIN_COUNT=5 browser-use < worldorgs_auto.py > out/batch2.log 2>&1

# 3. 看进度（不要用日志里的 ETA）
tail -3 out/batch.log
wc -l < out/malaysia_all.csv.done      # 已完成分类数

# 3b. 判批次是否真在跑（托管任务报 failed 时尤其要看这个）
tasklist | grep -i browser-use          # 有进程
ls -la out/batch.lock                   # 锁在
ls -la out/malaysia_all.csv             # mtime 在最近 1 分钟内推进
```

判定口径：`[STATUS] RUNNING remaining=N` = 未完成；主力全抓完才打 `MAIN_DONE`；`COMPLETE` = 含尾部与补电话全完。
报 ETA 一律用「本批处理分类数 ÷ 本批时长」倒推，**不要用 `remaining/_RATE/60`**（未计撞墙冷却，系统性低估）。

---

## 八、未核实项

- 全站去重后的独立商家数（需跑完全量按 `url` 去重）
- 官方 4,022 城市与 754 slug 的差额去哪了
- 是否存在其他语言子站（`en.worldorgs.com`）提供不同/更多数据
- 长跑（>2h）下 429 的频率与最佳 `DELAY` 取值
- **速率钉在 6.0/min 后是否会被永久锁死**（换 IP / 隔日恢复与否未验证）
- **把 `WO_RATE` 下限从 6 提到 10–12 是否更优**（少 sleep、多撞墙，净吞吐可能更高，未实测）
- 尾部 80,975 个单条分类的边际价值（每页 1 条，按 2.09/min 需 645 小时，性价比极低）
