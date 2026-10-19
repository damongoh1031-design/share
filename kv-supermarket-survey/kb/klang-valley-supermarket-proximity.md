---
id: klang-valley-supermarket-proximity
title: 雪隆区近距离超级市场盘点（OSM 全量+官网复核法）
tags: [马来西亚, 雪隆, 超市, AEON, Lotus's, Econsave, Mydin, OpenStreetMap, Overpass, 地理分析]
created: 2026-10-19
updated: 2026-10-19
version: 1.2.1
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

- NSK Trade City Setapak（OSM 标 Jalan Usahawan 7）——**已解（v1.2.1）**：即 NSK Trade City Wangsa Maju（aka Pasaraya Topzeller，Rampai Business Park；MyCen 专页 + 坐标 N3°11.971' E101°43.552' 与 OSM 建筑 way 吻合）。与 Giant Setapak（Jalan 5/23H）相距约 344m。
- Mydin Seksyen 16（Jalan Padang Jawa）、Mydin Seksyen U8（Jalan Pelapik U8/C）、Mydin Mart SEC 13 的官方冠名（Emporium/Mart/Hypermarket 体系复杂）。
- OSM 漏店风险：AEON AU2、AEON MALL Taman Maluri、AEON Bandaraya、AEON Metro Prima 未进近距离对，若其邻街有第二超市可能漏统计。
- 数据时点：OSM 快照 2026-10-19；门店状态以当日为准。


## 高端版（v1.1.0 增补，2026-10-19）

**剔除 Mydin/NSK/Giant/Econsave/AEON BIG 等平价线后的高端近距离对共 12 组（≤550m）**，交付 `klang-valley-nearby-premium-supermarkets.html/.csv`。

高端品牌全名单：Jaya Grocer（OSM 36 点，旗舰 Sunway Pyramid Oasis 翼 2024-11 重开、The Gardens LG-229）、Village Grocer（20 点）、Mercato（Gourmet 精品，5 点：Great Eastern Mall/TRX/Solaris Mont Kiara 等）、Cold Storage（OSM 覆盖不全，仅 2 点）、Isetan 食品馆（3 点）、Don Don Donki（OSM 无点，手工补：Fahrenheit88 在营、Sunway Pyramid 2024-12 新开、Nu Sentral 2025-05 已关、Tropicana Gardens 已确认在营、MyTown 无在营证据）、AEON MaxValu Prime（AEON 精品线，Kerinchi）。

| 高端对 | 距离 | 关系 |
|---|---|---|
| Cold Storage + Mercato（Great Eastern Mall） | 34m | 同商场 |
| Jaya Grocer + Isetan 食品馆（The Gardens） | 55m | 同商场 |
| Cold Storage + Isetan（Suria KLCC） | 127m | 同商场 |
| Don Don Donki Sunway Pyramid + Jaya Grocer（ pyram 场址点） | ~140m | 同商场 |
| Jaya Grocer Sunway 163 + Village Grocer Plaza Mont Kiara | 176m | 同一条 Jalan Kiara |
| DDD Fahrenheit88 + Isetan The Japan Store | ~170m | 同商圈（Isetan 址待核） |
| Village Grocer Avenue K + Isetan Suria KLCC | 247m | 隔 Jalan Ampang |
| Village Grocer Avenue K + Cold Storage Suria KLCC | 370m | 步行 5 分钟 |
| Village Grocer Sunway Square + Jaya Grocer Oasis 翼 | 381m | 同商圈 |
| Jaya Grocer Empire Shopping Gallery（Jalan SS16/1，已确认）+ Village Grocer Subang Parade | 432m | 相邻商场 |
| Mercato TRX + Isetan Japan Store | 439m | 同金融区 |
| Jaya Grocer SS15 Courtyard（已确认）+ Village Grocer Subang Parade | 540m | 同商圈 |

**对比结论**：高端「近距离对」12 组 vs 平价带 39 组——平价讲扎堆抢客、高端讲分区覆盖；Mont Kiara 是唯一高端密集区（3 家 400m 内）；Danau Kota/USJ Summit/Setia Alam 三个平价扎堆区均无高端店；Sunway City 因 Jaya Grocer（2024-11）+ DDD（2024-12）双双进驻成为新高端点。

## 非清真邻近度（v1.2.0 增补，2026-10-19）

**命题：超市有没有靠近非清真区 / 猪肉店的。** 用 109 个巴刹 + pork POI（Nominatim 56 条分区查询 + 15 条 pork 查询）与 257 个已识别超市做 haversine 匹配，得 **18 组 ≤500m**。交付 `klang-valley-supermarket-nonhalal.html/.csv`。

### 三个分层结论

| 层 | 结论 | 代表 |
|---|---|---|
| A 店内 | 品牌超市内部猪肉区：Jaya Grocer / Village Grocer / Mercato / Cold Storage / AEON/BiG / Giant / Lotus's / NSK / The Store **均有**；Econsave 推断多数有；HeroMarket / Checkers / TF Value-Mart / Billion **未核实**；**Mydin 全清真无猪肉**（NST 2020-12 官方声明官网可查） | 全表 |
| B 周边 | 18 组 ≤500m，近的是「品牌超市 ↔ 老巴刹/猪肉面」点对点，**没有**「平价大卖场 + 猪肉档扎堆带」 | Jaya Grocer SS15 Courtyard ↔ Omega Pork Noodle 55m（同街 Jalan SS 15/4G；四重确认：OSM 节点+ecentral 门店表+百度图片库+同商场 Rakuzen）；HeroMarket Sungai Besi ↔ Pasar Sungai Besi 103m；Mydin Kajang ↔ Pasar Kajang 150m；Danau Kota 双林批发超市 351m 贴五巨头商圈（Econsave/AEON BiG/Giant/Mydin） |
| C 反向 | 8 个老华人巴刹 1.5km 内**零品牌超市**：PJ Old Town 猪肉档（OSM 唯一 Pork section 节点，最近 My Mydin 1.6km）、Pasar Besar Cheras（1.6km AEON）、Sentul（1.4km NSK Grocer）、Kepong（1.5km AEON）、Pandamaran（1.4km Econsave）、Sungai Buloh（1.45km Econsave）、MPAJ Pandan Jaya（1.1km Lotus's）、Wah Fong Puchong（668m Checkers OUG） | 见 HTML 第五节 |

### 可复用操作

1. 巴刹普查：Nominatim search `q="Pasar X"` viewbox `101.25,3.35,101.95,2.85` bounded=0，countrycodes=my，限流 1.1s；滤掉 `Pasar Ekonomi Econsave`（清真大卖场附属市场，无信号）、`Pasar Malam`（夜市）、`Jalan/Lorong Pasar`（街名）。
2. 猪肉普查：`q="pork"` 同 viewbox → 15 个 POI 多为猪肉面餐厅；**真正的猪肉零售档只有市场节点**（如 `Pork section PJ Old Town Wet Market`），餐厅只作「非清真街区」信号。
3. 判定巴刹有无猪肉档：华人区老湿巴刹（Sentul/Kepong/Pandamaran/OUG/TTDI/Kuchai/Kajang/Rawang/Klang/Selayang/Sungai Besi/Sri Petaling/Wangsa Maju）按社区常识标「有」；马来区巴刹（Raja Bot/Chow Kit、Kampung Baru）标「弱」。
4. 距离代码与 v1 相同（haversine R=6371000），改匹配源即可。

### 坑与反直觉（本节新增）

1. **Nominatim "pork" 搜到的是面馆不是猪肉铺**：15 个命中里 14 个是 restaurant/fast_food；唯一零售档是 `Pork section PJ Old Town Wet Market` 节点 → 别把面馆当猪肉店算距离，只能当街区信号。
2. **Pasar Ekonomi Econsave 会伪装成巴刹**：它是 Econsave 店内经济市场，属清真大卖场，剔掉。
3. **OSM 幽灵点又抓两个 Mydin**：`Mydin, Jalan Tun Tan Siew Sin（Medan Pasar 旁 289m）` 与 `Mydin, Jalan Tuanku Abdul Rahman（Chow Kit 208m）` 官网无此店 → 剔除匹配（v1 报告的幽灵点方法复用有效）。
4. **Giant @ Dataran Sunway 幽灵点再次现形**：Kota Damansara Omega 猪肉面 445m 的 Giant 即该幽灵点，实际只有 Village Grocer 390m。
5. **老华人巴刹=品牌超市真空区**：直觉上「超市靠近非清真」应多在 Sentul/Kepong/PJ Old Town/Pandamaran 找，但这些区恰恰没有品牌超市；反之 Danau Kota/OUG/Sungai Besi 这种「巴刹+品牌店同圈」的极少。
6. **Jaya Grocer SS15 Courtyard 已四重确认**（v1.2.1 补证）：OSM 节点（2022-08 建）+ ecentral.my 2024 门店列表 + 百度图片库 233 张 + 同商场 Rakuzen（Tripadvisor 址 G-01 Courtyard Jalan SS15/4G）。连带纠正：Subang Jaya 有**两家** Jaya Grocer——SS15 Courtyard 与 Empire Gallery（SS16，685m 相距，官网 jgsj.jayagrocer.com），VG Subang Parade 夹在中间。

### 未核实 / 存疑（本节新增）

- Jaya Grocer SS15 Courtyard：v1.2.1 已确认在营（见上坑 6），从待核列表移除。DDD MyTown 仍无在营证据。
- Billion Port Klang（OSM area 字段错写 Pandamaran，点位近巴生港巴刹 300m）。
- Checkers OUG（OSM 无地址便民小超市）。
- HeroMarket / Checkers / TF Value-Mart 店内猪肉柜分布（挂牌清真生鲜的 HeroMarket 可能无）。
- 巴刹/猪肉档「有非清真」是社区常识级标注，未逐档核实；穆斯林读者请以店内 JAKIM 认证为准。

## 门店确认纪要（v1.2.1，2026-10-19）

| 门店 | 状态变化 | 证据链 |
|---|---|---|
| Jaya Grocer SS15 Courtyard | 待核 → **确认在营** | ecentral.my 2024-09-29 门店列表含 SS15 Courtyard；百度图片库 233 张；OSM 节点 9939836987（2022-08-08 建）；同商场 Rakuzen Tripadvisor 址 G-01 Courtyard, Jalan SS15/4G |
| Jaya Grocer Empire Shopping Gallery（SS16） | 待核 → **确认在营** | 官网门店子域 jgsj.jayagrocer.com 标题「Subang Jaya – Empire Shopping Gallery」；MyCen/马蜂窝址 Jalan SS16/1 |
| NSK Trade City Wangsa Maju | Setapak 命名待核 → **确认，正名 Wangsa Maju** | MyCen 专页「NSK Wholesale Supermarket, Wangsa Maju」（aka Pasaraya Topzeller，Rampai Business Park）坐标 N3°11.971' E101°43.552' = 3.19952,101.72587，与 OSM building way 506774302（branch=Wangsa Maju, source=openstreetcam）完全吻合 |
| Don Don Donki Tropicana Gardens | 待核 → **确认在营** | 2024-12 探店文「Tropicana Garden Mall 的 Don Don Donki 旁边」 |
| Don Don Donki MyTown | 待核 → **无在营证据** | 多轮检索无结果 |
| Mydin「Jalan Tun Tan Siew Sin」「Jalan TAR」两个 OSM 点 | → **判幽灵点** | 官网门店列表无此二址，反向编码仅给出街名 |

**连带修正**：v1 全品牌表中「NSK Trade City Setapak ↔ Giant Setapak Jalan 5/23H」应更名为「NSK Trade City Wangsa Maju ↔ Giant Setapak」（OSM area 字段写 Setapak 是邮区，branch 名 Wangsa Maju 才是店名）；Subang Jaya 出现「JG SS15 Courtyard + JG Empire Gallery 685m 同品牌对 + VG Subang Parade 夹中间」的三明治结构。
