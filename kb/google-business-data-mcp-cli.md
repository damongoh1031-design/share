---
id: google-business-data-mcp-cli
title: 用 GitHub 上的 MCP/CLI 反查 Google 商家数据（电话 → 商家档案）
tags: [mcp, cli, google-maps, places-api, business-profile, lead-gen, scraper]
created: 2026-10-27
updated: 2026-10-27
version: 2
status: active
source: 官方文档 + GitHub API 检索 + 本机编译运行实测（2026-10-27）
confidence: 高（gosom 与 rahul 两个工具已实际跑通并产出数据；电话反查失败已实测确认）
---

## 一句话结论

**gosom/google-maps-scraper 已在本机编译并跑通**，店名+地区查询可拿到 36 字段完整档案（含电话、place_id、评分、评论原文），**不需要 Docker**。但**纯电话号码反查在两个工具上实测全部失败** —— 电话反查只能走 Places API (New) Text Search（需国家码+空格+`regionCode`）。

已封装为可复用 Skill：`~/.workbuddy-ai/skills/google-maps-business-scraper/SKILL.md`，二进制在 `~/.workbuddy-ai/tools/gmaps.exe`。

---

## 一、先排除误区：Google Business Profile API 不能反查别人

| 通道 | 能做什么 | 能否查 `0167238684 Dobi Anggun` |
|---|---|---|
| Google Business Profile API（GBP） | 读/写**你自己已验证**的商家：评价回复、帖子、指标 | ❌ 完全不能。需该 location 的 owner/manager OAuth 授权 |
| Google Places API (New) | 查**全网公开** POI 数据 | ✅ 可以，且支持电话号搜索 |
| Google Maps 网页抓取 | 同 Places，无 key | ✅ 可以（有风控） |

`twominutereports/google-my-business-mcp` 这类 GBP MCP 只服务「自有门店运营」，拿来做线索核验是方向性错误。**结论：社区实证 + 官方文档**

---

## 二、候选工具对比（GitHub 实测星数，2026-10-27）

| 仓库 | ★ | 形态 | 需 Key | 电话反查 | 关键限制 |
|---|---|---|---|---|---|
| [gosom/google-maps-scraper](https://github.com/gosom/google-maps-scraper) | 6899 | Go CLI / Web UI / REST | ❌ 否 | ❌ 实测失败 | **Go 直编可用，无需 Docker**；36 字段 |
| [rahul-bhatt43/maps-scrapper](https://github.com/rahul-bhatt43/maps-scrapper) | 1 | CLI + MCP | ❌ 否 | ❌ 实测失败 | 12 字段；`-l` 必填；无 license |
| [cablate/mcp-google-map](https://github.com/cablate/mcp-google-map) | 484 | MCP + CLI (`exec`) | ✅ Google Maps Platform | ✅ 透传 textQuery | `search_places` 不返电话，须链式 `place_details` |
| [omkarcloud/google-maps-scraper](https://github.com/omkarcloud/google-maps-scraper) | 3825 | Python 包 | ❌ 否 | ⚠️ 未声明 | 50+ 数据点，偏营销 SaaS 引流 |
| [Mahanaicoach/google-maps-scraper-kit](https://github.com/Mahanaicoach/google-maps-scraper-kit) | 1941 | Python | ❌ 否 | ⚠️ 未声明 | 导出 CSV 含电话/邮箱/社媒 |
| [HasData/google-maps-mcp](https://github.com/HasData/google-maps-mcp) | 8 | 托管 MCP | HasData key | ✅ | 免 Google Cloud 项目，按量付费 |
| [outscraper/outscraper-mcp-server](https://github.com/outscraper/outscraper-mcp-server) | 4 | 托管 MCP | Outscraper key | ✅ | 商业 API，富化能力强 |
| [twominutereports/google-my-business-mcp](https://github.com/twominutereports/google-my-business-mcp) | — | MCP (GBP) | OAuth | ❌ | 仅自有商家 |

> ⚠️ 检索时遇到的 `batteryshark/mcp-google-maps` 已 404，网搜结果里的仓库名不可直接信，一律用 GitHub API 复核。

---

## 三、可复用操作

### 方案 A：官方 Places API，最准，一行 curl

号码 `0167238684`（马来）→ E.164 `+60167238684` → 查询串须 **`+60 167238684`（国家码 + 空格）**，并设 `regionCode: MY`。

```bash
export KEY="AIza..."
curl -s -X POST "https://places.googleapis.com/v1/places:searchText" \
  -H "Content-Type: application/json" \
  -H "X-Goog-Api-Key: $KEY" \
  -H "X-Goog-FieldMask: places.id,places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.internationalPhoneNumber,places.rating,places.userRatingCount,places.googleMapsUri,places.businessStatus,places.types,places.regularOpeningHours" \
  -d '{"textQuery":"+60 167238684","regionCode":"MY"}'
```

号码搜不到时的降级链：
1. `{"textQuery":"Dobi Anggun","regionCode":"MY"}`
2. 加 `locationBias: {"circle":{"center":{"latitude":3.1,"longitude":101.6},"radius":30000}}`
3. 名称 + 城市：`{"textQuery":"Dobi Anggun Kuala Lumpur"}`

**计费**：`nationalPhoneNumber` / `rating` 属 Enterprise SKU；`googleMapsUri` 属 Pro SKU。带电话字段 = 按 Enterprise 计费。

### 方案 B：cablate MCP（让 AI 直接调）

```bash
# 自检（不耗 API 调用）
npx -y @cablate/mcp-google-map doctor

# CLI 直接搜
npx -y @cablate/mcp-google-map exec search-places '{"query":"+60 167238684"}'

# 拿到 place_id 后取电话/网址/地图链接
npx -y @cablate/mcp-google-map exec place-details '{"placeId":"ChIJ..."}'
```

MCP 配置：
```json
{"mcpServers":{"google-maps":{
  "command":"npx","args":["-y","@cablate/mcp-google-map","--stdio"],
  "env":{"GOOGLE_MAPS_API_KEY":"AIza..."}}}}
```
需 Node 22+；启用 Places API (New) + Routes API + 计费账号。

### 方案 C：gosom 批量跑线索表（免 Key）

```bash
# queries.txt 每行一条，可直接写号码或 Maps URL
printf '0167238684 Dobi Anggun\nhttps://www.google.com/maps/search/0167238684\n' > queries.txt

docker run --rm \
  -v gmaps-playwright-cache:/opt \
  -v "$PWD/queries.txt:/queries.txt:ro" \
  -v "$PWD/out:/out" \
  gosom/google-maps-scraper \
  -input /queries.txt -results /out/r.csv -json -depth 1 -c 4 -exit-on-inactivity 3m
```

输出字段（36 个）直接可用：`title, category, address, complete_address, phone, website, review_rating, review_count, latitude, longitude, place_id, cid, open_hours, link`。加 `-email` 抓邮箱。

---

## 四、坑与反直觉

1. **GBP ≠ Places**。想「查别人的商家」只能用 Places / 抓取；GBP 只读自有门店。这是最高频踩坑点。
2. **电话号码必须带国家码 + 空格**，否则命中率骤降；`regionCode` 要与国家码一致。E.164 也受支持。
3. **cablate 的 `maps_search_places` 不返回电话号码**，字段名也是简化版（`place_id`/`total_ratings`/`address`），必须 `maps_place_details` 二次调用。只搜一次会以为「查不到电话」。
4. **gosom 的 query 就是 Google Maps 搜索框文本，但纯号码会被解析成地理实体** —— 实测 3 次全失败，别再假设"能跑"。
5. **Places 电话字段按 Enterprise SKU 计费**，比只取名称/地址贵一档。批量核验成本要按 Enterprise 算。
6. 带字母的号码按 **E.161 键盘映射**转数字（如 1-800-FLOWERS），马来纯数字号不受影响。
7. `-depth 1` 是速度/覆盖的平衡点；`-c 8 -depth 1` 约 120 places/分钟。
8. **gosom README 只写 Docker 是误导**，Go 直编在 Windows 上可用且更快。
9. **rahul 的 `npm install` 必然在 Playwright 下载阶段超时失败**，必须用 `PLAYWRIGHT_DOWNLOAD_HOST=https://cdn.npmmirror.com/binaries/playwright` 补下 `chromium-headless-shell`。完整 chromium 已存在 ≠ headless shell 已存在。
10. **镜像站的评分是陈旧的**：WorldOrgs 显示 4.7/10 条，Google 实时是 4.6/34 条。核验数据以实时抓取为准。

---

## 五、实测验证（2026-10-27，本机 Windows）

测试对象：马来西亚 KL 的 Dobi Anggun

### 5.1 命中结果

| 工具 | 查询 | 耗时 | 结果 |
|---|---|---|---|
| gosom | `Dobi Anggun Wangsa Maju Kuala Lumpur` | 94s（首次含下载）/ 27s | ✅ 命中，36 字段 |
| rahul | `-q "Dobi Anggun" -l "Wangsa Maju, Kuala Lumpur"` | **15s** | ✅ 命中，12 字段 |
| gosom | `0167238684` | 27s | ❌ 0 条 |
| gosom | `0167238684 Wangsa Maju` | 27s | ❌ 返回地理区域 "Wangsa Maju" |
| rahul | `-q "0167238684" -l "Kuala Lumpur, Malaysia"` | 19s | ❌ 返回行政区 "Federal Territory of Kuala Lumpur" |

### 5.2 gosom 实际输出（关键字段）

| 字段 | 值 |
|---|---|
| title | Dobi Anggun (Full Service) |
| category | Laundry |
| phone | `016-723 8684` |
| review_rating / review_count | **4.6 / 34** |
| reviews_per_rating | `{"1":1,"3":2,"4":4,"5":27}` |
| place_id | `ChIJz_aL1Bc4zDERw1qMs7aWCb0` |
| cid | `13621584259399310019` |
| plus_code | `6P3H+3M Kuala Lumpur` |
| lat/lng | 3.202669, 101.729197 |
| website | https://msha.ke/dobianggunwm/ |
| owner | Dobi Anggun (Full Service) (Owner)，已认领 |
| user_reviews | 5 条评论原文（含作者、星级、时间） |

### 5.3 安装成本实测

| 工具 | 耗时 | 卡点 |
|---|---|---|
| gosom | 10m49s | `go mod download` 报 `unexpected EOF`，重跑即过；首次运行额外下载 Playwright driver+browser 68s |
| rahul | 12m24s | `npm install` 的 postinstall 下 Chromium 超时 30s 必失败，需镜像补下 headless shell |

---

## 六、结论修正（相对 v1）

| v1 说法 | v2 实测结论 |
|---|---|
| gosom「电话反查 ✅ 间接」 | ❌ **错误**。纯号码 0 结果，加地区词返回地理实体 |
| gosom「需 Docker」 | ❌ **不准确**。Go 1.26+ 直编可用，Windows 无需 WSL |
| 推荐 cablate/mcp-google-map 为主 | ⚠️ 降级。需 Google Maps Platform key + 计费，且 `search_places` 不返电话；免 key 场景应主推 gosom |
| 「Dobi Anggun 是否存在未核实」 | ✅ 已核实存在，Google 评分 4.6/34 条 |

---

## 七、未核实项

- Places API (New) Text Search 用电话号的实际召回率（本次无 API Key，未能实测）。
- gosom 在大批量（`-c 8`、`-depth 3`）下的限流阈值与代理必要性。
- rahul 的 MCP server 在真实客户端下的稳定性（仅验证了 CLI 路径）。
