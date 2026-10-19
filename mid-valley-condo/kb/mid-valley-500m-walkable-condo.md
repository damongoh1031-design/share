---
id: mid-valley-500m-walkable-condo
title: 吉隆坡谷中城 500 米内天桥可步行公寓购买清单
tags:
  - 马来西亚房产
  - 吉隆坡
  - Mid Valley
  - KL Eco City
  - 天桥连通
  - 分层地契
  - 房产调研
created: 2026-10-19
updated: 2026-10-19
version: 1.0
status: stable
source: 本次会话实测（brickz / mudah / MyRumahBaru / spsetia.com / PropertyGuru）
confidence: 已核实（结构数据）；推断（步行距离、回报测算）
---

# 吉隆坡谷中城 500 米内天桥可步行公寓购买清单

## 一句话结论

Mid Valley Megamall（3.1175628, 101.6774073）500 米直线内只有 **6 个可买分层住宅**：真正室内直连的只有 **The Gardens Residences**（永久地契，2007，151 户）和 **Northpoint Residences**（租赁地契，2006，228 户）；KL Eco City 的 **Vogue Suites One / Two、ViiA** 直线 370–450 m，靠有盖天桥跨巴生河接驳，但实际步行 **550–750 m**。半径内 **2021 年后无新盘**。

---

## 全清单（按直线距离升序）

| # | 项目 | 直线距离 | 连通方式 | 竣工 | 产权 | 户数 | 层数 | 户/层 | 判定 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | The Gardens Residences | ≈0 m | 室内直连 | 2007 | **Freehold**·住宅 | 151 | 30 | 5.0 | 符合 |
| 2 | Northpoint Residences | ≈100 m | 室内直连 | 2006 | Leasehold·住宅+办公 | 228(+204 办公) | 22 | 10.4 | 符合 |
| 3 | Vogue Suites One | 370 m | 有盖天桥 | 2013/2017（冲突） | Leasehold·住宅 | 711 | 60 | 11.9 | 步行超 500m |
| 4 | Vogue Suites Two | ≈400 m | 有盖天桥 | 2020 | Leasehold·住宅 | 344（存疑 739） | — | — | 步行超 500m |
| 5 | ViiA Residences | 450 m | 有盖天桥 | 2021 | Leasehold·**商业** | 326 | 40 | 8.2 | 步行超 500m |
| 6 | Boulevard | <200 m | 待核 | 未公开 | Leasehold·服务式 | 未公开 | — | — | 身份待核 |

---

## 成交价（brickz / NAPIC 申报数据）

| 项目 | 中位 psf | 中位总价 | 四分位区间 | 样本 / 期间 |
|---|---|---|---|---|
| Vogue Suites One | **RM1,016** | RM930,000 | 668K–1,230K | 7 笔 / 2025-10–2026-05 |
| Mid Valley City 分区（Boulevard+Northpoint） | RM1,374 | RM1,704,768 | 1,275K–2,409K | 28 笔 / 2025-06–2026-04 |
| Boulevard | RM1,447 | RM2,221,706 | 1,689K–2,759K | 20 笔 / 2025-06–2026-04 |
| ViiA Residences | 1,099–1,318（**挂牌要价**） | 699K–1,650K（SPA） | — | 1 条在挂 |
| Vogue Suites Two | 未取得 | 未取得 | — | 0 |
| The Gardens Residences | 未取得 | 未取得 | — | 0 |

**核心定价结论**：同园区同开发商，Vogue One 成交中位 psf RM1,016 vs ViiA 挂牌 RM1,318 → **单价差 30%，楼龄只差 4 年**。Vogue One 是唯一有真实成交样本支撑的低价入口。

---

## 天桥连通（三档分级）

| 档 | 判定标准 | 项目 | 步行距离 |
|---|---|---|---|
| 🟢 真·室内直连 | 不出楼、不淋雨、不穿马路 | The Gardens、Northpoint | 150–250 m |
| 🟡 有盖但超 500m | 全程有盖，跨河穿两商场 | Vogue One / Two、ViiA | 550–750 m |
| 🔴 看着近不能走 | 无桥，被高速/铁路/河切断 | Bangsar South（The Sphere 1.0km）、The Establishment 1.5km、Aetas Seputeh 1.3km | 只能车行 |

**S P Setia 官方原文**：「A covered pedestrian link bridge that joins the development to the bustling Mid Valley City」（spsetia.com 新闻稿）。

---

## 可复用操作

### 复算距离 / 抓成交价

```bash
# 1. 短链解析出真实地名与坐标
curl -sIL "https://maps.app.goo.gl/<id>" | grep -i "^location"

# 2. MyRumahBaru 项目页（直线距离 + 洪涝 + 户型 + 管理费）
curl -sL -A "Mozilla/5.0 ..." "https://myrumahbaru.com/project/<slug>" -o p.html

# 3. brickz 项目成交（NAPIC 逐笔，需 Referer + 浏览器 UA）
curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ..." \
  -H "Referer: https://www.brickz.my/" \
  "https://www.brickz.my/transactions/residential/kuala-lumpur/bangsar/<project-slug>/" -o b.html

# 4. mudah 项目概况（字段在 HTML 的 label/value 键值里）
curl -sL -A "Mozilla/5.0 ..." "https://www.mudah.my/property/properties-in-<slug>-kuala-lumpur" \
  | grep -o '"label":"[^"]*","value":"[^"]*"'
```

### brickz 分区页挖「被漏掉的项目」

分区页的项目表是 JS 渲染抓不到，**但页脚链接暴露了项目 slug**：

```bash
curl -sL -A "<UA>" "https://www.brickz.my/transactions/residential/kuala-lumpur/mid-valley-city/" \
  | grep -o 'href="https://www.brickz.my/transactions/residential/kuala-lumpur/mid-valley-city/[^"]*"'
# → 发现 boulevard、northpoint 两个此前完全没被门户列出的项目
```

这是本次调研最关键的一步：**门户网站漏掉的住宅项目，用 NAPIC 分区的项目链接反查**。

---

## 坑与反直觉

1. **MyRumahBaru 的中位 psf 是分区回退值，不是项目值。** 实测 Vogue One / Vogue Two / ViiA 三栋全部显示 `RM1,282.43`、中位总价 `RM1M`、样本 `4 笔`。三栋不同楼不可能同价同笔数 → 一律弃用，改用 brickz 逐项目成交。
2. **mudah 的竣工年与 MyRumahBaru 冲突时不能默认信一方。** Vogue Suites One：mudah 2013 / MyRumahBaru 2017，差 4 年，直接影响楼龄判断与贷款年限。
3. **门户漏项目。** Mid Valley City 园区的 Northpoint（228 户住宅 + 204 办公）与 Boulevard（20 笔成交、中位 RM2.22M）在 mudah 项目库和 MyRumahBaru 都没有独立页，只在 brickz 分区页的项目链接里出现。**只查门户会漏掉整个园区一半的住宅供给。**
4. **「步行 5 分钟到 Mid Valley」是开车口径。** KL Eco City 三栋直线 370–450 m，实际天桥步程 550–750 m。中介文案统一这么写，必须自己按路径重算。
5. **外国人门槛会直接砍掉半份名单。** 吉隆坡 RM1,000,000。Vogue One 成交中位 RM930K → 外籍买家只能买 RM1M 以上单位。
6. **服务式住宅的「社区」是流动的。** Vogue Suites One、ViiA、The Gardens Residences 三个项目在 Agoda / 携程 / TripAdvisor 都以酒店形态收录 → 短租密集。JMB 一旦收紧短租附例，租金模型立刻失效。
7. **标准火险不含洪水。** 马来西亚标准 fire policy 默认排除 flood，需加保 Special Perils（Bangsar 一带约 0.086%/年）。
8. **商业地契三个后果**：水电默认商业费率（可申请转住宅）、公务员不能用 LPPSA、转售买家池更小且银行估值更保守。

---

## 未核实 / 存疑

| 项 | 状态 | 建议 |
|---|---|---|
| The Gardens Residences 成交价 | brickz / EdgeProp 均无该项目页；唯一挂牌 RM528K/730sf（RM723 psf）与产品定位不符，判为异常 | 持牌估价师 valuation report |
| Vogue Suites Two 成交价 | brickz 检索无对应项目页（登记名可能为 Residensi Vogue 2） | 索取同栋 SPA 副本 |
| Vogue Suites Two 户数 | 344 vs 739（疑为 Vogue 1+2 合计） | 向管理处索取分层地契总户数 |
| Gardens / Northpoint / Vogue Two / Boulevard 洪涝评级 | 无项目级数据 | 向管理处索取历史淹水记录 |
| Boulevard 是否可作为住宅持有 | 公开资料几乎为零 | 律师调取分层地契与用途批文 |
| 各项目 JMB / MC 公司全名 | DBKL 名录、COB 名单、分层仲裁庭均无公开版本 | 索取 AGM 通知 |
| 层高 | 开发商手册只写材料不写高度 | 现场激光测距仪实测 |

---

## 数据源分级

| 级别 | 来源 | 用途 |
|---|---|---|
| A 一手 | spsetia.com 官方新闻稿 | 跨河有盖天桥的存在与性质 |
| A 一手 | brickz.my（NAPIC 逐笔申报） | 中位 psf、总价、四分位区间 |
| B 结构化门户 | mudah.my / MyRumahBaru / PropertyGuru 项目页 | 户数、层数、竣工、面积、户型、管理费 |
| C 营销二手 | 挂牌描述、OTA 收录 | 短租活跃度旁证 |
| D 推断 | 本报告自算 | 户/层密度、步行距离、租金回报 |
