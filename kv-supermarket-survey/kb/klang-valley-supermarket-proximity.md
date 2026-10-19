---
id: klang-valley-supermarket-proximity
title: 雪隆区近距离超级市场盘点（OSM 全量+官网复核法）
tags: [马来西亚, 雪隆, 超市, AEON, Lotus's, Econsave, Mydin, OpenStreetMap, Overpass, 地理分析]
created: 2026-10-19
updated: 2026-10-19
version: 1.0.0
status: stable
source: 本次会话实测（Overpass API + Nominatim + 各品牌官网/商场官网交叉核实）
confidence: 已核实（门店存在性与地址）/ 待核（个别冠名，见「未核实项」）
---

## 一句话结论

用 OpenStreetMap Overpass API 全量抓雪隆 1,534 个超市/百货 POI → 19 个品牌过滤出 1,056 个点 → haversine 两两距离 → Nominatim 反向编码 → 官网复核，得到 **39 组跨品牌近距离超市对（27 个商圈）**：最密集的是 **Mid Valley/The Gardens（3 超市 220m 内）**、**Danau Kota/翠湖园 Setapak（5 大卖场 1km 内）**、**USJ 1 Summit（Giant+Mydin+NSK 200-360m）**、**Setia Alam/Klang Sentral（Lotus's+NSK+Giant）**、**Mont Kiara（Jaya Grocer+Village Grocer 176m 同一条 Jalan Kiara）**。

## 分距离档次总表（36 对 ≤500m，另 3 对 500–610m）

| 档次 | 距离口径 | 对数 | 代表组合 |
|---|---|---|---|
| 同商场/同栋/同排 | <150m | 8 | Cold Storage+Mercato（Great Eastern Mall, 34m）、Econsave+Mydin Semenyih（40m）、Giant+HeroMarket Kelana Jaya（51m）、Mydin Mart+HeroMarket SEC 13（117m）、NSK+Giant Klang Sentral（124m） |
| 隔马路/邻栋 | 150–350m | 13 | AEON BIG Wangsa Maju+Lotus's Wangsa Maju（337m，即用户 sri rampai 例，归本档）加入 Jaya+Village Grocer Mont Kiara（176m）、Giant+Mydin Mall USJ Summit（182m）、Giant+NSK Summit（194m）、AEON BIG+Village Grocer Subang SS16（224m）、Village Grocer Avenue K+Cold Storage KLCC（247m）、Jaya Grocer+HeroMarket Melawati（285m）、AEON BIG Danau Kota+Mydin Danau Kota（315m）、NSK Klang Sentral+Lotus's Setia Alam（380m）、Jaya Grocer BBCC+NSK BTS（349m） |
| 同商圈 5 分钟 | 350–550m | 16 | AEON BIG The Gardens+Jaya Grocer（210m）、Giant Setapak+Econsave Setapak Central（442m）、Billion+Econsave Pandamaran（448m）等 |

## 五强超市集群

| 集群 | 门店（品牌+距离） | 说明 |
|---|---|---|
| Mid Valley City（59200 KL） | AEON Megamall ↔ AEON BIG The Gardens 216m；Jaya Grocer The Gardens ↔ Isetan 55m；AEON BIG ↔ Jaya Grocer 210m | 两商场天桥相连，谷中城片区 3 超市+1 百货 |
| Danau Kota / 翠湖园（Setapak 北 53300） | AEON BIG Danau Kota（Jalan Danau Saujana）↔ Mydin Danau Kota（Jalan Langkawi）315m；Giant Setapak（Jalan 5/23H）↔ Econsave Setapak Central（KL Festival City）442m；Mydin↔Econsave 519m；AEON BIG↔Econsave 574m | 留學生圈知名性价比区，5 大卖场 1km 圈 |
| USJ 1 Summit（47610/47600） | Giant USJ Summit（1 Persiaran Subang Permai）↔ Mydin Mall Subang 182m；↔ NSK Grocer Summit USJ 194m | 老牌三巨头，全部步行 3 分钟 |
| Setia Alam / Klang Sentral（40170/41050） | NSK Klang Sentral ↔ Giant Klang Sentral 124m；Lotus's Setia Alam（Jalan Setia Prima）↔ NSK 380m | Setia Alam 镇 + Klang Sentral 商圈 |
| Kelana Jaya SS6/SS7（47301） | Giant Kelana Jaya（33 Jalan SS6/12）↔ HeroMarket（119 Jalan SS6/12）51m；Lotus's Kelana Jaya = Paradigm Mall 锚定店 444-492m | SS6/SS7 交界三超市 |

## 可复用操作

```bash
# 1) Overpass 全量抓取（UA 必带，否则 406）
curl -sS -A "survey/1.0" -X POST "https://overpass-api.de/api/interpreter" \
  --data-urlencode 'data=[out:json][timeout:150];(nwr["shop"~"supermarket|department_store|wholesale"](2.85,101.25,3.35,101.95););out center tags;' \
  -o overpass_raw.json

# 2) 品牌过滤 + haversine 两两距离（除便利店 99 Speedmart）
#    python 脚本模式：json.load → 过滤 name 命中品牌正则 → dedupe 40m → double loop hav() ≤600m

# 3) Nominatim 反向编码补区域名（限流 1 req/s，zoom=18/20）
curl -A "survey/1.0" "https://nominatim.openstreetmap.org/reverse?lat=3.2046&lon=101.7162&format=jsonv2&zoom=18&addressdetails=1&accept-language=en,ms"
```

复核门店存在性的可靠源：品牌官网 store sitemap（giant.com.my/store_location/…、econsave.com.my/store/<slug>）> 商场官网 > Samsung/HSBC/AmBank 商户名录 PDF > MR.D.I.Y 门店 PDF（NSK 地址最全）> OSM 本身。

## 坑与反直觉

1. **OSM 有已关店的幽灵点**：Giant @ Berjaya Times Square（已关，同场 LG 层现为 NSK Grocer）、AEON Sunway Pyramid（2025-01 撤店）。OSM name≠现况，必须官网复核。
2. **AEON Sunway Pyramid**：2025-01 关闭，Jaya Grocer Oasis 翼旗舰店 2024-11 重开接手——「同商场双超市」曾成立，现单边失效。
3. **直线距离 ≠ 步行距离**：隔高速路/铁路/河流时差数倍；雪隆商场普遍只许驾车进出。
4. **99 Speedmart 是便利店**：OSM 里 797 个点，混进来会淹没大卖场信号，先剔除再算距离。
5. **同名不同店**：Lotus's（前 Tesco）门店邮编地址常与 OSM POI 不一致；「Lotus's Kelana Jaya」实为 Paradigm Mall 内店；「翠湖园」= Taman Danau Kota（Setapak 53000/53300），中文名只在 name:zh。
6. **Overpass 406**：不带 User-Agent 会被 nginx 拒；超时查询用 POST + `[timeout:150]`。
7. **Nominatim 对商场名无感**：display_name 只给街道/邮编号；判断「同商场」要靠门店名+邮编号+路名三件套。

## 未核实项

- NSK Trade City Setapak（OSM 标 Jalan Usahawan 7）——两轮官网检索未确认地址，339m 对 Giant Setapak 待实地核。
- Mydin Seksyen 16（Jalan Padang Jawa）、Mydin Seksyen U8（Jalan Pelapik U8/C）、Mydin Mart SEC 13 的官方冠名（Emporium/Mart/Hypermarket 体系复杂）。
- OSM 漏店风险：AEON AU2、AEON MALL Taman Maluri、AEON Bandaraya、AEON Metro Prima 未进近距离对，若其邻街有第二超市可能漏统计。
- 数据时点：OSM 快照 2026-10-19；门店状态以当日为准。

