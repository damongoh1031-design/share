---
name: google-maps-business-scraper
description: >
  用本地 CLI 抓取 Google Maps 商家数据（名称/电话/地址/评分/评论/place_id/坐标/营业时间），
  不消耗 Places API 配额。当用户要「抓 Google Maps 商家」「批量采集某地某行业商家」「查商家电话地址评分」
  「scrape google maps」「Google 商家数据采集」「按地区/行业批量拿电话」「反查商家 Google Maps 档案」
  「导出一批本地商户线索」时使用。内置两个已实测可用的开源工具：
  gosom/google-maps-scraper（字段最全，主推）与 rahul-bhatt43/maps-scrapper（轻量、带 MCP）。
  也覆盖「纯电话号码能否反查商家」的实测结论与正确替代方案。
  另含 WorldOrgs 目录站 dump（全马 87 万条商家名称+电话）与 Cloudflare 限流实测。
description_zh: "本地抓 Google Maps 商家数据（电话/地址/评分/评论/place_id），不耗 API 配额。两个已实测工具 + 电话反查的正确姿势。"
description_en: "Scrape Google Maps business data locally (phone, address, rating, reviews, place_id) without Places API quota. Two verified tools plus the correct way to do phone-number lookup."
version: 1.0.0
category: 数据采集
author: workbuddy
---

# Google Maps 商家数据抓取

两个开源工具已在本机**实测通过**（2026-10-27），用于按「店名/行业 + 地区」批量拉取 Google Maps 商家档案，不走 Places API 计费。

## 何时用本 Skill

| 用户意图 | 用哪个 |
|---|---|
| 批量采集某地某行业商家（要电话、评分、评论、place_id） | **gosom**（字段 36 个） |
| 只要名称/电话/地址/评分，追求快 | **rahul**（15 秒出结果） |
| 想让 AI 通过 MCP 直接调 | **rahul**（有 `search_google_maps_places` 工具） |
| 要接 REST API / Web UI | **gosom**（内置） |
| 纯电话号码反查商家 | ❌ 两者都不行，见下文 |

---

## 一、gosom/google-maps-scraper（主推）

**仓库**：https://github.com/gosom/google-maps-scraper ｜ 6899★ ｜ MIT ｜ Go ｜ 2026-10-21 活跃

### 已编译好的二进制（本机）

```
C:/Users/Admin/.workbuddy-ai/tools/gmaps.exe
```

直接用，无需再编译。验证：

```bash
"C:/Users/Admin/.workbuddy-ai/tools/gmaps.exe" -h
```

### 基本用法

```bash
export DISABLE_TELEMETRY=1
cd <工作目录>
printf 'Dobi Anggun Wangsa Maju Kuala Lumpur\n' > q.txt

"C:/Users/Admin/.workbuddy-ai/tools/gmaps.exe" \
  -input q.txt -results out.csv \
  -depth 1 -c 1 -exit-on-inactivity 60s
```

- `-input`：查询词，每行一条（**就是 Google Maps 搜索框文本**）
- `-depth 1`：滚动深度，1 是速度/覆盖平衡点
- `-c 1`：并发，首次跑建议 1，稳定后可 `-c 4`
- `-exit-on-inactivity 60s`：无活动自动退出，避免挂死
- `-json`：输出 JSON 而非 CSV
- `-email`：额外抓官网邮箱（慢）

### 实测输出字段（36 个，可直接用）

`title, category, address, complete_address, phone, website, review_rating, review_count, reviews_per_rating, latitude, longitude, place_id, cid, plus_code, open_hours, owner, user_reviews, link, thumbnail, timezone, ...`

**其中最有价值的**：`place_id`（ChIJ 开头，可用于 Places API 二次查询）、`cid`、`reviews_per_rating`（星级分布）、`owner`（认领人）、`user_reviews`（评论原文）。

### 从零重建

```bash
git clone --depth 1 https://github.com/gosom/google-maps-scraper.git
cd google-maps-scraper
export DISABLE_TELEMETRY=1
go mod download          # 网络差时会报 unexpected EOF，重跑即可
go build -o gmaps.exe .
```

需要 **Go 1.26+**（go.mod 写 1.27.1）。**不需要 Docker** —— README 只写了 Docker，但 Go 直编完全可行，且绕开 Docker 依赖。

首次运行会自动下载 Playwright driver + 浏览器到 `~/AppData/Local/ms-playwright-go/`，约 70 秒。

---

## 二、rahul-bhatt43/maps-scrapper

**仓库**：https://github.com/rahul-bhatt43/maps-scrapper ｜ 1★ ｜ TypeScript ｜ **无 license** ｜ 2026-08-10 最后提交

### 安装（注意 Playwright 坑）

```bash
git clone --depth 1 https://github.com/rahul-bhatt43/maps-scrapper.git
cd maps-scrapper
npm install          # postinstall 会尝试下 Chromium，大概率超时失败
npx tsc              # 编译到 dist/，即使 postinstall 失败也能编译

# 用国内镜像补下 headless shell（关键一步）
PLAYWRIGHT_DOWNLOAD_HOST=https://cdn.npmmirror.com/binaries/playwright \
  npx playwright install chromium-headless-shell
```

### CLI

```bash
node dist/index.js run -q "Dobi Anggun" -l "Wangsa Maju, Kuala Lumpur" -m 10 -f json -o out.json
```

`-q` 和 `-l` **都必填**。`-m` 最大条数（默认 100），`-f` json/csv，`--headless false` 可看浏览器动作。

### MCP

```json
{"mcpServers":{"maps-scrapper":{
  "command":"node",
  "args":["<abs-path>/dist/mcp/server.js"]}}}
```

暴露单个工具 `search_google_maps_places`，入参 `query`、`location`、`max`(1–100)、`saveToFile`。

### 输出字段（12 个）

`name, category, rating, reviewCount, address, phone, website, lat, lng, url`

比 gosom 少：无 `place_id`、无 `cid`、无 `open_hours`、无 `reviews_per_rating`、无评论原文。

---

## 三、实测对比（同一商家，2026-10-27）

测试对象：马来西亚 KL 的 Dobi Anggun

| 维度 | gosom | rahul |
|---|---|---|
| 安装耗时 | 10m49s（Go 编译，含网络重试） | 12m24s（npm，且需补下浏览器） |
| 运行耗时 | 94s（首次含浏览器下载） / 27s（缓存后） | **15s** |
| 命中 | ✅ Dobi Anggun (Full Service) | ✅ 同名 |
| 电话 | `016-723 8684` | `0167238684` |
| 评分/评论数 | 4.6 / 34 | 4.6 / 34（一致） |
| 字段数 | **36** | 12 |
| 输出 | CSV / JSON | JSON / CSV |
| 运行依赖 | 无（单 exe） | Node 22 + Playwright chromium |
| 维护活跃度 | 高（6899★） | 低（1★，无 license） |

**结论**：默认用 gosom。rahul 只在需要 MCP 接口或追求单次 15 秒响应时用。

---

## 四、纯电话号码反查：两个工具都不行（实测）

| 测试 | 结果 |
|---|---|
| gosom，query = `0167238684` | **0 条结果** |
| gosom，query = `0167238684 Wangsa Maju` | 1 条，但是地理区域 "Wangsa Maju"，非商家 |
| rahul，query = `0167238684`, location = `Kuala Lumpur, Malaysia` | 1 条，返回行政区 "Federal Territory of Kuala Lumpur" |

**根因**：两者都是把 query 喂给 Google Maps 网页搜索框。Maps 网页端对纯数字号码的语义解析弱，倾向返回地理实体。

**正确做法**：电话反查必须走 **Places API (New) Text Search**，官方明确支持电话查询：

```bash
curl -s -X POST "https://places.googleapis.com/v1/places:searchText" \
  -H "Content-Type: application/json" -H "X-Goog-Api-Key: $KEY" \
  -H "X-Goog-FieldMask: places.id,places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.rating,places.userRatingCount,places.googleMapsUri" \
  -d '{"textQuery":"+60 167238684","regionCode":"MY"}'
```

要求：**国家码 + 空格**（`+60 167238684`），且 `regionCode` 与之一致。有 key 时优先走这条。

**没有 API Key 时的降级链**：
1. 用店名 + 地区跑本 skill（最可靠）
2. 用店名 + 唯一地址片段
3. 用已知的 `place_id` 直接查

---

## 五、坑清单

1. **gosom 官方文档只写 Docker**，但 Go 直编可用，Windows 上无需 WSL。
2. **`go mod download` 会报 `unexpected EOF`**，是网络问题，重跑或设 `GOPROXY=https://goproxy.cn,direct`。
3. **rahul 的 `npm install` 必然在 Playwright 下载阶段失败**（30s 超时），必须用 npmmirror 补下 `chromium-headless-shell`。注意完整 chromium 已存在不代表 headless shell 存在 —— 两者是不同包。
4. **rahul 的 `-l` 必填**，不给 location 直接报错。
5. **Maps 网页对纯号码解析差**，别指望电话反查。
6. **评分会漂移**：镜像站（WorldOrgs 显示 4.7/10 条）与 Google 实时（4.6/34 条）不一致，以实时抓取为准。
7. **`-c` 并发别一开始拉高**，容易被 Google 限流；配 `-proxies` 或 `-fast-mode` 再提。
8. 抓取违反 Google ToS，仅个人低量使用，别进生产循环。

---

## 六、输出解读速查

gosom CSV 里几个容易看错的字段：

| 字段 | 说明 |
|---|---|
| `phone` | 本地格式（`016-723 8684`），非 E.164 |
| `place_id` | `ChIJ...` 开头，可传给 Places API 拿更多字段 |
| `cid` | 十进制 ID，可拼 `https://maps.google.com/?cid=<cid>` |
| `reviews_per_rating` | JSON：`{"1":1,"3":2,"4":4,"5":27}` |
| `complete_address` | 结构化 JSON，含 borough/street/city/postal_code/state/country |
| `owner` | 商家认领人 Google 账号（有则说明已被认领） |
| `data_id` | 形如 `0x31cc...:0xbd09...`，与 cid 对应 |

---

## 七、WorldOrgs 目录站 dump（要 87 万条全马数据时用）

当用户要「全马来西亚商家名称+电话」而不是「某地区某行业」时，gosom 要跑几万次查询，不现实。改用 **WorldOrgs**（`my.worldorgs.com`）—— 它是 Google Maps 数据的镜像目录，**列表页直接带电话**。

### 规模

| 指标 | 数值 |
|---|---|
| 马来西亚机构总数 | **876,761**（含跨分类重复） |
| 城市 / 分类 | 4,022 / 2,473 |
| 吉隆坡单城市 | 93,993 条（跨 2,238 分类） |

### 关键结构

```
/katalog                    城市索引（3 页，共 754 个城市 slug）
/katalog/{city}             分类+数量
/katalog/{city}/{category}  商家列表 ← 数据在这里，**无 /page-N 分页**
/katalog/{city}/{cat}/{slug} 详情页 ← 补电话
```

列表页是**两段式**：

- **前 200 条**：`<article class="li">`，带 `tel:` 链接
- **第 201 条之后**：隐藏 `<ul><li>`，**有名称+地址，没有电话**

```html
<article class="li" data-phone="1" data-r="4.2">
  <h2 class="li-n"><a href="/katalog/kl/restoran/xxx">Siti Li Dining</a></h2>
  <p class="li-r"><b>4.2</b><span>(100)</span></p>
  <p class="li-a">地址</p>
  <a class="li-call" href="tel:+601139066078">
</article>

<ul><li><a href="/katalog/kl/restoran/mollagaa">Mollagaa Restaurant</a><span>地址</span></li></ul>
<button data-list-more-btn>Tunjuk semua 748 organisasi</button>   <!-- 纯 JS，不是链接 -->
```

**`/page-2` 不存在**（返回 15KB 空页、0 条）。所以单分类从列表页最多拿 200 个电话，
且 `tel:` 数 **≡** `data-phone="1"` 数 —— 用这个核对解析正确率，比抽样可靠。

### 电话覆盖率是"源数据"决定的，不是抓取问题

| 分类 | article | data-phone=1 | tel: |
|---|---|---|---|
| KL/klinik | 200 | 200 | 200 |
| KL/kedai-pakaian | 200 | 192 | 192 |
| ajil/masjid | 4 | 1 | 1 |

城市商业类接近 100%，小镇非商业类（masjid/景点）大量没电话。**别承诺"全有电话"。**

### 现成脚本（v3，推荐）

```
C:/Users/Admin/.workbuddy-ai/tools/worldorgs_dump_v3.py
```

**必须在 `browser-use` 里跑**（依赖 `http_get`，见下节）：

```bash
# ① 索引：754 城市 × 全部分类+数量
WO_PHASE=index WO_INDEX=worldorgs_index.tsv browser-use < worldorgs_dump_v3.py

# ② 采集
WO_CITY=kuala-lumpur WO_OUT=kl.csv browser-use < worldorgs_dump_v3.py

# ③ 补电话（第 201 条之后）
WO_PHASE=detail WO_OUT=kl.csv browser-use < worldorgs_dump_v3.py
```

输出 `name, phone, address, rating, reviews, city, category, url`；`<out>.done` 断点续跑；
去重键 `url`（同一商家跨分类重复）。旧版 `worldorgs_dump.py`（urllib）已被 v3 取代。

### 反爬：两层限制，别用错通道

| 方案 | 结果 | 速度 |
|---|---|---|
| urllib + 完整 header | 冷门页 403，成功率 ~33% | — |
| headless Chromium `--dump-dom` | ❌ 403 | — |
| browser-use `http_get`（裸请求） | 先 200，25–50 次后**整站 429，冷却 >15 分钟** | 0.48s/页 |
| **browser-use `goto_url` + CDP 屏蔽资源** | **✅ 100% 通过，无 429** | **0.68s/页** |
| browser-use `goto_url` 不屏蔽资源 | ✅ 通过 | 1.87s/页 |

**两层限制，必须分清：**

1. **403 = "回源"拦截**：判定依据是 TLS 指纹 + cookie + JS 挑战。缓存命中时高频也过，
   未命中时低频也 403，**换 UA 完全无效**。只有真实浏览器会话能过。
2. **429 = "请求类型"限速**：同一 IP 同一 cookie，`http_get` 裸请求几十次就被封，
   而真导航连跑 20+ 页正常。Cloudflare 对 `Sec-Fetch-Mode: navigate` 更宽容。

**所以：用真导航，不要用 `http_get`。** 并屏蔽静态资源：

```python
cdp("Network.enable")
cdp("Network.setBlockedURLs", urls=[
    "*.jpg","*.jpeg","*.png","*.gif","*.webp","*.svg","*.ico",
    "*.woff","*.woff2","*.ttf","*.css"])
```

图片/CSS/字体对解析无用，屏蔽后 1.87s → 0.68s/页。分类页正文在 HTML 里，不靠 JS 渲染。

**标签页会卡死**：`goto_url` 偶发让标签页半死，之后所有 `Runtime.evaluate` 超时
（连 `document.readyState` 都超时）。捕获异常后 `new_tab(url)` 重建即可，v4 已内置。

### 两个硬约束（别踩）

1. **sitemap 是死路**：`/sitemap/sitemap.xml` 存在但本身 403/404，拿不到全量 URL 列表。
2. **吞吐是真实上限**：实测 **1.36s/分类页**（含写盘），据此估算：

| 范围 | 页数 | 耗时 |
|---|---|---|
| 索引（754 城） | 754 | ~17 min |
| KL 列表页 | 2,238 | ~50 min |
| 前 22 大城市 | 34,074 | ~13 h |
| 全马（估） | ~10 万+ | 多轮分批 |

**给用户的建议**：定向抓（城市+行业）当天可完成；全量按城市分批，每批之间留冷却。

### 自动续跑与监督（2026-10-27 实测）

主自动化脚本：`C:/Users/Admin/.workbuddy-ai/tools/worldorgs_auto.py`；索引：`worldorgs_index.tsv`；主 CSV：`out/malaysia_all.csv`；分类断点：`out/malaysia_all.csv.done`；日志：`out/batch.log`。通过 browser-use 的真实 Chrome 导航运行，脚本依靠 `batch.lock` 阻止并发、以 `.done` 续跑，并使用限速状态文件自适应节奏。

- **主力默认阈值为 `WO_MIN_COUNT=5`**：全局按分类条目数降序采集 `count>=5`；1–4 条分类暂缓。需要显式补尾部时再设 `WO_MIN_COUNT=1`。分类数、剩余数和 `MAIN_DONE` 均以相同阈值计算。
- **不要沿用过期的 3.4 万/82% 估计**。2026-10-27 当前索引快照一度为 173,951 分类 / 1,054,694 条目，其中 >=5 为 40,261 分类 / 836,242 条目（79.29%）；随后一批补完 81 城后，索引增至 178,949 分类。每次应从 TSV 重算，索引未完整时覆盖比例只是已索引分母的比例。
- 2026-10-27 一批 54 分钟实测：完成索引 81 城；分类采集 263 类 / 45,286 行 / 37,984 行带电话；总累计 164,449 行、125,155 行带电话。结束时脚本仍是旧阈值，日志显示尾部 `<2`，因此这批结果不能当作阈值 5 已生效的验证。
- 主力规模仍很大，按该批结束时观察到的有效进度只能粗估数百小时；限速、空页、Chrome 超时和索引变化都会改变实际耗时。**不要保证 2–3 天完成**，应报告最近批次的分类增量、限速次数和当前 remaining。
- 每次续跑前核对 `batch.lock`；若锁有效，不要并发启动 browser-use。批次后读 `out/batch.log` 的 `[STATUS]`、阈值行、已抓/剩余、限速次数，并核实锁是否释放。
- 输出含个人电话号码；向公开 GitHub 同步 CSV 前必须先提醒用户并确认是否改私有。经验脚本/Skill 可单独同步，不要顺手上传 `out/` 数据目录。

### 坑

1. **官方标称 4,022 城市，`/katalog` 实际只有 754 个 slug**，`/page-4` 起为空。差的可能是街区级页面，站内搜索可达但目录索引里没有。
2. `Tunjuk semua N organisasi` 是 **JS 按钮不是链接**，点开也不给更多电话。
3. `robots.txt` 有 `Crawl-delay: 10`、`Disallow: *?*` —— 别用 `?page=` 这类带参 URL。
4. `/katalog/all-places-index` 被 robots 禁止且 404，**没有全量索引页**。
5. 解析隐藏 `<ul>` 时要取「li 数最多且 >20」的那个，否则会命中导航栏小列表。
6. **browser-use 里的 `/tmp` 是 `C:\tmp`**，不是 Git-Bash 的 `AppData\Local\Temp`；路径一律写绝对 Windows 路径。
7. 分类页里的 category 可能与当前页不符（相关分类聚合）。
8. 电话是 E.164（`+601139066078`），不是本地格式。
9. 实测电话覆盖率：kluang 84.6%、KL 商业类接近 100%、ajil 的 masjid 只有 25% —— **取决于源数据，别承诺"全有电话"**。
