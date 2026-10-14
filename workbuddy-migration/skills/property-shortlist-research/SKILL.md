---
name: property-shortlist-research
description: 按「地点 + 预算 + 租/买」产出一份带来源标注的房产短名单或全量档案。当用户要求「找某地步行可达的公寓/房子」「预算 X 到 Y 之间有什么」「列出这些楼盘所有资讯（户型/设施/卖点/密度/户数）」时使用；也适用于「最大户型有多大、有没有阳台、层高多少、交房给什么设备、管理费多少、能不能养宠物」这类户型内装与管理层调研。解决房产门户页面 JS 渲染抓不到、产权被中介标错、总户数与土地面积口径混乱、层高与管理层信息官方不公开四类常见问题。
agent_created: true
---

# 房产短名单调研

## 何时用
- 用户给出一个地标（商场 / MRT 站 / 学校）+ 步行距离要求
- 用户给出预算区间，要求筛选
- 用户要求「列出所有资讯」= 要项目级档案：户型 / 设施 / 卖点 / 规模 / 密度 / 户数

## 执行顺序

### 1. 先确认三个口径（不要猜）
- **租还是买** —— 决定整套数据来源，猜错整轮白做
- **预算区间** —— 注意：租金档位选项不能套用到购买口径（踩过坑：用户选了「RM4,000 以上」的租金档，实际是要买）
- **户型 / 房间数**

若用户只给一句话，先做一轮通用调研再问，不要空手提问。

### 2. 建项目清单（这一步决定成败）
地标周围项目来源，按可靠性排序：
1. **mudah.my 地区列表页 + 项目页** —— `mudah.my/<地区>/apartment-condominium-for-sale` 列出该区全部在售；卡片里含项目页链接，`grep -o -E 'href="https://www\.mudah\.my/kuala-lumpur[a-z-]*/apartment-condominium-for-sale/[a-z0-9-]+"'` 可一次性抽出该区所有项目 slug。
   ⚠️ 地区列表页只给**最新 ~40 条**，且分页参数无效（`?o=2` / `/2` / `?page=2` / `?start=40` 全部返回空）。价格档位 URL（`price-from-X-below-Y`）只有部分档位存在（如 `price-from-300000-below-400000`），`price-from-1200000-*` 一律 404。**所以不要指望靠列表页覆盖高价段，要按项目逐个抓。**
2. **MyRumahBaru 项目页** —— 距离表（到地标多少米）+ 洪灾/治安 + NAPIC 成交中位。**建"步行可达"清单的最快方式**：逐个抓候选项目页，读 `Mid Valley Megamall\n<距离>` 字段排序。
3. **开发商官网的项目列表页** —— 经常能发现门户网站漏掉的新盘。例：`spsetia.com/property/kl-eco-city/` 一次列出全片区在售业态，含「A pedestrian link bridge provides easy access to The Gardens / Mid Valley City」这类关键连接信息。
4. 门户按项目名搜索（`mudah.my/kuala-lumpur/properties-for-sale?q=<项目名>`，结果脏，需本地过滤）
5. **EdgeProp 项目页（`edgeprop.my/condo/<slug>-<id>`）—— ⭐ 成交价的最佳单一来源**。⚠️ **curl 会被 Cloudflare 拦，但 `WebFetch` 工具能正常访问**（2026-09-28 验证）。给：近 48 个月成交中位 psf + 区间 + **隐含租金回报** + 历史最高/最低 + 户数/开发商/邮编。**必须先用 `WebSearch "edgeprop.my/condo" <项目名>` 拿真实 id** —— 猜 id 会指向完全不同的项目（实测 `bayberry-tropicana-gardens-15377` 实际返回 Arte Plus Ampang、`cyperus-tropicana-gardens-15378` 返回 Ashton Tower Kota Kinabalu）。部分页面数据为 N/A 或 RM0（无成交样本），如实标注即可。

### 3. 抓数据：什么能抓，什么抓不到

**能抓（curl / WebFetch 均可）**
- `starproperty.my/insight/<id>/<slug>` —— ⭐⭐ **软性信息（管理费 / 住户构成 / 社区评价 / 开发商口碑 / 已成交记录）的最佳单一来源，优先级高于 MyRumahBaru 与 mudah**。每篇结构固定：Property Details（Developer / Completion Date / Tenure / No. of Blocks / No. of Units / Land Area / Built-up / **Maintenance Fee** / Launch Price）+ Layouts + Facilities + Market Trends（逐笔 SPA 成交）+ **Analysis（一整段讲优点、抱怨与风险，是全网最直白的负面信息源）**。
  - **insight id 拿法**：`WebSearch "starproperty insight <项目名>"`，结果第 1–2 条通常就是。同片区 id 连号（实测 Seputeh 区：Robson Condominium 120、Bukit Robson 121、Robson Heights 122、Seputih Permai 386、Menara Seputih 385、Robson Court 390、Saville Residence 429、Le Chateau 1226）——**拿到一个就能猜邻居**。
  - 这一页的价值在于**负面信息**：管理维护被批、开发商做工口碑、紧邻义山/寺庙/高压电塔、噪音源、水质、治安、分层地契传言、产权溢价。门户和开发商官网永远不会写这些。
  - 实测抓到的高价值原句：「Most rate the maintenance here quite low」「it seems like the management has done nothing at all」「received loads of complaints from its previous projects due to bad workmanship and low quality material used」「most of the units are facing the cemetery」。
  - ⚠️ 同站另有 `/kuala-lumpur/<区>/<slug>/property-insights/<id>` 形态，与 `/insight/<id>/<slug>` 等价。
  - ⚠️ **不是每一篇都有 Analysis 段**。实测 `insight/8299`（Vogue Suites One）抓下来只有 Property Details + Facilities + Location，没有 Analysis；`insight/107`（Northpoint）与 `property-insights/509`（The Gardens）则有完整 Analysis。抓完先 `grep -i analysis` 确认，没有就换源。
  - ⚠️ 该站是 **JS 渲染 + 服务端也吐文本** 的混合体：`curl` 能拿到全文（约 140–160 KB HTML → 剥离标签后 6–9 KB 纯文本），但 `/property-insights/search?q=<词>` 这类**搜索页纯 JS**，curl 拿不到结果列表（只有分页链接）。要找 insight id 只能靠 WebSearch，不要试图爬站内搜索。
- `mudah.my/property/properties-in-<项目slug>-kuala-lumpur` —— ⭐ **首选的项目概况页**。返回结构化的：Sale Price / Rental Price / Tenure / **Total Units** / **No. of Floors** / Completion Year + 在售房源摘要。
  - **字段藏在 Next.js 的 `__NEXT_DATA__` JSON 里**，直接 grep 键值对比解析 HTML 干净：
    `grep -o '"label":"Total Units","value":"[0-9]*"' x.html`（同理 `No. of Floors` / `Completion Year`）；开发商 `grep -o '"developer_name":"[^"]*"'`。
  - **必须带完整浏览器头**，否则返回 404 空壳：
    `-H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" -H "Accept-Language: en-US,en;q=0.9"`
  - **slug 必须与 mudah 自己的命名完全一致**（不是项目常见名）。猜不中就用「从已知项目页里 grep 邻近项目链接」的办法发现正确 slug：
    `grep -o -E 'href="/property/properties-in-[a-z0-9-]+"' 已成功的项目页.html | sort -u`
    实测差异举例：`viia-residences` ✗ → `viia-residences-kl-eco-city` ✓；`avara-seputeh` ✗ → `avara` ✓；`nadi-bangsar` ✗ → `nadi-bangsar-service-residence` ✓；`southlink` ✗ → `south-link-lifestyle-apartments` ✓；`novum` ✗ → `novum-bangsar-south` ✓；`robson-condominium` 有时 ✓ 有时 ✗，重试即可。
- `mudah.my/<地区>/apartment-condominium-for-sale/<项目slug>` —— 该项目完整在售列表，含面积/房卫/要价
- `mudah.my/kuala-lumpur/properties-for-sale?q=<关键词>` —— 跨区模糊搜索，可用来捞某个项目的全部在售（但结果会混入大量无关条目，需本地过滤价格）
- `myrumahbaru.com/project/<slug>` —— ⭐ **距离 + 洪涝的唯一来源**：到指定商场/地标的分级距离表（`Mid Valley Megamall\n370 m`）、Flood risk（High/Moderate/Low + 河流名 + 最近泛滥日期 + 近两年次数）、治安指数、NAPIC 成交中位 psf、户型表、设施表。
  - slug 从 sitemap 批量拿：`curl -sL myrumahbaru.com/sitemap-<0..25>.xml` → `grep '/project/'`（约 5,600 个项目）
- `sunwayproperty.com/<项目slug>` / `mahsing-realstate.com/projects/<slug>` —— 官方户数、面积区间、竣工年、产权
- `rumavi.com/en|zh/new-developments/malaysia/<区>/<slug>` —— ⭐ **新盘（尤其「建后售 / 未公开发售」的项目）最值得看的一站**。除了「N 座 × M 层，共 X 户，占地 Y 英亩」的密度口径，还给：
  - **独立评估四段**：Investment Highlights / **Pros** / **Considerations** / Recommended For / Not Recommended For / **Risk Assessment（Liquidity / Market / Management 三级打分）** —— 这是全网少见的、敢写「不推荐给谁」的来源，负面信息密度接近 StarProperty 的 Analysis。
  - **Common Area Fee**（如 `Approx. USD 0.10-0.12/sqft/month`）—— 少数会直接给管理费的来源之一。
  - **Available Unit Types 表**：每个户型的 sqm/sf + **具体要价 RM** + 单价 psf。比门户的区间挂牌更可用。
  - Location Highlights 分级距离（Transport / Shopping / Healthcare / Education，含 UMMC、Pantai、Garden International School、UM）。
  - ⚠️ 它的户型表可能与官方口径冲突（实测 Southpoint：Rumavi 说最大 2,680 sf、官方与第三方说最高 5,837 sf 五房顶层）。**Rumavi 用来看评估与风险，不用来看最终面积**。
- `kaiproperties.my/articles/<slug>` —— ⭐ **中文深度项目梳理**，对「长期不公开发售 / 邀请制」的盘尤其有价值。实测 Southpoint 一文给出：Parcel 编号与「最后一块住宅用地」论断、CCC 实际取得时间与封顶年份的落差、从未公开发售的销售史与业主画像（政界高层、上市公司董事）、装修品牌清单（De Dietrich/Bosch/Toto Neorest）、GreenRE 认证、集中冷冻水系统、**已成交租约的真实租金**（2 房 RM8,500、3 房 RM12,000–19,000）、楼下办公租户名单（Shopee/PayNet/SAP/Knight Frank）、对岸 KL Eco City 的租户（Samsung/Zurich/Zalora/Klook）、片区入驻率 >90%。属营销内容，但事实密度高、可交叉验证。
- `klpropertynavi.com/property/<slug>` —— 层数 / 塔数 / 户数 / 竣工年月 / 设施清单，**外加「分户型 × 售价区间 × 单价」与「分户型 × 租金区间 × 单价」两张表**。这两张表是判断「小户 vs 大户哪个更划算」的最快入口。slug 是站内自命名（实测 `vogue-suite-1`、`north-point-residence`），要 WebSearch 找。
- `stgileshotels.com/<品牌slug>/` 及 `/accommodation/` —— **服务式公寓被酒店品牌运营时**的官方口径：现运营房型名 + **面积（m²）** + 床型配置 + 设施与共用关系（「住宅与酒店共用 5 楼设施、入口大堂独立」这类关键结构信息只有这里写）。
- 开发商官网（`tantan.com/southpoint-residences/`、`spsetia.com` 等）—— 官方户数 / 类型 / 卧室数区间，用于给冲突数据定锚。

**抓不到（JS 动态渲染 / 反爬）**
- ⚠️ **`edgeprop.my` 用 curl 会被 Cloudflare 拦**（`/condo/<slug>` 与 `/buy/...` 都返回 "Just a moment..." 挑战页），**但 `WebFetch` 工具能正常读取 `/condo/<slug>-<id>` 项目页**（2026-09-28 验证）。**不要因为 curl 失败就放弃 EdgeProp —— 它是成交中位 psf 与隐含租金回报的最佳来源。** 抓取前先 `WebSearch "edgeprop.my/condo" <项目名>` 拿真实 id。
- `iproperty.com.my` —— 403 Bot Protection
- `propertyguru.com.my` —— curl 直接连不上；但 **WebSearch 的结果摘要常直接带出整段项目描述**（实测 Vogue Suites Two 的「344 units / 5 种户型 / Type A-C 657–1,119 sf、D-E 1,647–3,993 sf」全部从搜索摘要读到），可当二手源用
- `propertysifu.my` —— 路径格式与旧记录不符，实测 404
- `irumah.co/...` —— ⚠️ **修正：带完整浏览器 UA 的 curl 实际可以成功**（实测 58–77 KB 正常页），只是**字段很薄**（只有 Property Type / Tenure / Developer，Built-up、Total Units、Completion Date、Market Data 全是 `-NA-`）。它的真正价值是「同开发商的其他项目」与「同片区相似项目」两个列表 —— 用来发现遗漏的项目名。
- `residensivogue1.com` —— Cloudflare 挑战页（"Checking your browser"），项目方自建站也拦
- `allyproperties.my` / `sunway-cochrane.com` —— Cloudflare 拦截
- ⚠️ **开发商自建站的 `?page_id=` 链接多数已失效**：Southpoint 官网首页导航给的 5 个 `page_id`（1183/1240/1435/1509/2765/3105）全部返回 "Page Not Found"（站点改版后未清理链接）。官网只剩首页可用，户型/位置页抓不到 —— 直接改用 Rumavi + 第三方文章。

**别信**
- `speedhome.com/rent/<地标>` 的「附近房源」列表 —— 标题写 A 地标，返回的却是全市无关房源
- 中介广告里的产权标注 —— 见第 5 条

### 4. 必须逐项核实的字段
| 字段 | 为什么容易错 |
|---|---|
| 产权 / 地契 | 中介乱标（把 Leasehold 写成 Freehold 极常见）；同一园区不同期产权不同 |
| **Restriction of Interest（土地处分限制）** | **标着 Freehold 也可能不能自由转让 / 出租 / 抵押**。必须翻官方 e-brochure 免责声明页。实例：Sunway Cochrane 官方原文「This land cannot be transferred, leased, or mortgaged without the permission of the Wilayah Persekutuan Kuala Lumpur Land Working Committee and until the Mass Rapid Transit project is completed」。这是 Freehold 项目最容易漏的致命条款，直接影响退出与再融资 |
| 官方备案价 vs 代理宣传价 | 官方广告许可证备案价常远高于代理报价。实例：Sunway Cochrane 官方 Block A RM1,000,000–1,725,000，代理只写「from RM830,000」，差可达 RM170 万。**以 SPA 与官方手册为准** |
| 土地面积 vs 设施平台面积 | 官方常写「4.5 英亩设施平台」，被二手网站当土地面积 |
| 总户数 | 分全盘 / 分期 / 单栋三个口径，官方与门户常不一致 |
| 竣工年份 | 期房项目在不同资料上能差 3 年 |
| 每层户数 | 门户的「units per floor」与「总户数 ÷ 层数」经常对不上。**最可靠的是官方 Tower Layout Plan 的单位编号**（如 Sunway Cochrane 编号 01,02,03,03A,05–13,13A 无 04 = 14 户/层，与「1,296÷108≈12」的推算不符） |
| 到地标距离 | 直线 / 驾车 / 步行三种，中介常混用 |
| **MRT / LRT 线路归属** | **代理站经常写错线路名**。实例：多个站把 Cochrane 写成「MRT Putrajaya Line」，实际是 **Kajang Line（KG21）**。核实方法：Wikipedia `https://en.wikipedia.org/w/index.php?title=<站名>_MRT_station&action=raw`（注意消歧义页要加 `_MRT_station` 后缀），或查站序表。换乘站要单独确认是哪两条线的交点 |

### 5. 密度计算（自己算，别抄）
```
户/英亩 = 总户数 ÷ 土地面积（英亩）
户/层   = 总户数 ÷ 住宅楼层数
```
两个指标一起看：户/英亩反映社区拥挤，户/层反映电梯等待时间。高户/英亩 + 低户/层 = 超高层塔楼（如 468 户/英亩、17 户/层）；低户/英亩 + 低户/层 = 真低密度。

### 6. 价格数据分级（必须标来源）
1. **开发商官网 / S&P** —— 一手价，无议价
2. **EdgeProp / NAPIC 成交数据** —— 最可信的二手价（成交 ≠ 要价）
3. **门户在挂要价** —— 通常可议 3%–7%
4. **中介口头报价** —— 最后考虑

**要价 ≠ 成交价**，报告里必须区分。租金同理：在挂要价 vs 实际成交租金。

### 7. 必查的四个风险层
- **洪灾风险**：MyRumahBaru 项目页有「Flood risk」模块，会标出河流名、最近泛滥日期、近两年次数。低洼区（沿河、旧工业区）必查。
  - ⚠️ **必须区分「建筑本体风险」与「区域风险」**。实测 Establishment / Alila Bangsar 标 Moderate，但页面同时给出「建筑地面约 32m、河面约 26m，高出河面约 6m」——即河流要上涨约 2 层楼高才可能影响本建筑。**只报等级不报高差，会把低风险项目写成高风险。**
  - 马来西亚标准火险**默认不含洪水**，需加保 Special Perils（Bangsar 区约 0.086%/年，RM1.5M 保额约 RM1,290/年）。报告里要写这条。
- **土崩 / 边坡风险（丘陵片区必查，最常被漏）**：吉隆坡的 Seputeh / Bukit Bandaraya / Pantai Hill Park / Bukit Gasing 一带都是丘陵地形。查法：`WebSearch "<片区名> landslide OR 土崩 OR 山坡 崩塌"`。实测 2025-11-24 Taman United / Jalan Sepadu 6（Seputeh）发生约 60m 长边坡崩塌，104 户被令疏散。山上盘必须查边坡与 JMB/MC 的斜坡维护责任。
- **外国人门槛**：马来西亚各州不同，吉隆坡为 RM1,000,000。低于此价的盘外籍买不了 —— 这条会直接砍掉整份名单，必须早问
- **商业地契（commercial title）**：服务式公寓常见。三个后果必须写进报告：① 水电默认商业费率（可经 myTNB 申请转住宅费率）；② 公务员不能用 LPPSA 贷款；③ 部分州对外籍买家的门槛与贷款成数不同。识别方法：mudah 的 `title_type` 或门户写「Commercial under HDA」。
- **「服务式住宅 / 服务式公寓」不是共管公寓**：看到门户标 `Service Residence` 或 `Serviced Residences`，必须换一套问题清单问：
  - 谁在运营？（实测 The Gardens Residences 由 **St Giles Hotels** 以酒店品牌运营，可官网直接按晚预订 —— 住宅楼的实际人口是**流动的**）
  - 住宅分层产权与同楼酒店/服务式部分**如何在 JMB/MC 里划分表决权与费用分摊**？这决定业主的实际控制力，也决定公共费用是否被摊到住宅业主头上。
  - 设施是「住宅专用」还是「与酒店共用」？共用意味着拥挤与磨损速度不同。
  - 单元内配置是否全装全配（含厨具/洗衣机/宽带）？服务式盘常如此，影响买入后的出租弹性与装修成本。
  - 短租是否就是产品本身？若是，未来政策收紧会打断收入模型。
- **混合业态（住宅 + 办公/商业同塔或同综合体）**：实测 Northpoint（228 住宅 + 204 办公同盘）、Southpoint（办公至 Level 36，住宅在 41–59 层）。要额外问：① 住宅与办公是否共用电梯/水泵/消防/电力主干？② 住宅业主是否要为商业部分的运营成本买单？③ 商业租户（实测 Shopee/PayNet/SAP）带来的是稳定租客池还是人流与噪音？④ 分层门禁从哪里开始（Southpoint 是从办公楼层之前就开始，属高标准）。
- **「从未公开发售 / 邀请制」的盘**：这类盘（实测 Southpoint Residences，172 户，钥匙以邀请制给开发商家族与关联方）没有任何成交序列可查。别写「无数据」就结束 —— 要写清：业主画像（政界高层、上市公司董事）、二手流动性极低（172 户）、真实成交价不透明、且**可能长期不对外放盘**。对买家而言，「买不到」本身就是结论。

### 8. 输出格式
- **短名单**：一张主表按单价 psf 升序排（不是按总价），另附「这个档位最大的发现」
- **全量档案**：总览总表（每项目一行）+ 密度排行 + 洪涝汇总 + **管理费与住户构成一览** + **短租活跃度一览** + 项目索引（锚点目录）+ 逐项目卡片（基本资料 / 户型 / 设施 / 11 个定性字段）+ **数据冲突清单** + **数据缺口清单** + 买家现场必做清单 + 来源可靠性分级
- **专项深度档案**（用户点名 3–5 个项目「全面调研」时）：一句话结论（每项目一句 + 三个硬风险）+ 两张横向对比表（① 结构与产权：开发商/竣工/产权/类型/户数/层数/户层/面积/户型数；② 价格距离与风险：在售在租库存/挂牌区间/中位 psf/三个距离/洪涝/短租/天桥）+ 逐项目深度卡（身份卡 15–20 行 + 价格与租金表 + 户型全表 + 设施全表 + 距离表 + **9–10 个定性 block**：住户构成/社区评价/管理层规矩/房屋质量/卖点/步行连通/洪涝/短租/一句话定位）+ 冲突清单 + 缺口清单 + **按主题分组的现场核查清单**（产权与地契 / 管理与费用 / 洪涝 / 房屋本体 / 短租与住户结构 / 价格与流动性）+ 来源清单。
  - 深度卡里的「一句话定位」必须写「适合谁、不适合谁」，不要只罗列优点。
  - 洪涝那一栏要写「无数据 ≠ 无风险」，并说明同片区其他项目的评级作为参照。
- 数据冲突和缺口必须写出来。用户要的是「确保没有遗漏」，把找不到的字段列成表比假装完整更有价值
- 每个数字标来源，并在文末注明可靠性分级
- **总览表的距离列必须标口径**（直线 / 路径 / 驾车）。**MyRumahBaru 给的距离是「直线距离」，不是路径距离**（2026-09-28 用页面内嵌 JSON-LD 的 geo 坐标反算验证：项目坐标与 POI 坐标的球面直线距离与页面文字逐条吻合到 1–2%）。实际步行/车行路径距离 ≥ 直线，一般 ×1.2–1.4。**但直线距离不等于可步行**；必须另设一栏或加脚注说明「只有 X 组有桥可走」。
- **总览表必须从分组定义生成，不要从合并主表生成**——合并主表里的项目名是门户原始标题（如「The Park Residences 1」「Inalfa in Bangsar」），与卡片锚点对不上，会生成一堆死链。

### 8b. 多代理并行调研（项目数 > 30 时）

按地理片区切 3–4 份，每份 15–25 个项目，一个子代理一份。**四条硬规则**：

1. **第一句就要求子代理用 `Write` 工具把完整报告写入指定绝对路径，回复只报「已写入 + 字节数」**。不要把报告正文塞进回复——主代理收到的可能是被压缩的摘要，甚至上下文一压缩就全丢。
   ```
   用 Write 工具把完整报告写入 C:\Users\<user>\AppData\Local\Temp\<proj>\report_gpN.md
   （Git Bash 里就是 /tmp/<proj>/report_gpN.md，目录已存在）
   完成后只回复一句「已写入，N 字节」，不要在回复里贴正文。
   ```
2. **统一字段名与项目显示名**。把「必须使用的二级标题名称列表」原样写进 prompt（一字不差），否则回来要人工对齐锚点。
3. **每个项目强制 11 个字段**，查不到写「未找到」，**不允许省略字段**——否则回来会发现一半项目缺管理费栏。
4. **主代理要能自己兜底**：把已验证的检索渠道（StarProperty insight 拿法、mudah 头、myrumahbaru slug）写进 prompt，并附已知线索（「某项目开发商被指做工差」「某项目有 40% 单位卖给外国人」），让子代理去核实而不是从零找。

⚠️ **团队会被中途重置**：出现 `SendMessage` 报 `Not in a team`、且 `TaskList` 变成一份全新列表时，旧 teammate 的上下文已经没了，**只能用 `Agent` 重新派发**，不要试图恢复。

⚠️ **主代理不要干等**。子代理在跑时，主代理应并行做：主代理自己抓最高价值的那几个项目（StarProperty insight 一抓就有 80% 的字段）、构建渲染脚本与 HTML 骨架、整理冲突/缺口清单。实测主代理自查 7 个 B 组项目的时间，刚好填满等待窗口。

### 8c. 渲染脚本的常见坑
- 卡片锚点 `id` 由项目显示名正则化得到（`re.sub(r'[^a-zA-Z0-9]+','-',name)`）；总览表、目录、卡片三处必须用**同一个函数**生成锚点。
- 生成 HTML 时**每行 `<td>` 用 `'\n'.join()` 拼接会导致整行跨多行**，肉眼没问题，但正则解析会失败。要机器校验就改成 `''.join()`。
- **分类汇总表不要用关键词启发式**。实测用「含『活跃』」判定短租，会把「间接提示短租不活跃」的项目误判为活跃。**用显式集合**（`SHORT_ACTIVE = {...}`）。
- 数据源缺项时（如某项目在门户无独立页），**主代理要自己补抓**，不要留空：实测 The Gardens Residences 在 MyRumahBaru 无页，但 mudah 项目页有完整字段（151 户 / 30 层 / 2007 年 / Freehold / 开发商 IGB），补进去后 A 组旗舰项目的卡片才有内容。


### 9. 找「单价倒挂」
同一园区内，大户型 / 复式顶楼常比小户型单价低 30% 以上（小户型溢价来自「总价低好出租」）。按 psf 排序能立刻看出来，这是给用户最有价值的单条结论。

### 10. 户型内装 / 层高 / 阳台（用户问「最大户型有多大、有没有阳台、有多高」时）

**层高（ceiling height）—— 全行业最难拿的字段，先看这条避免白做**
- **开发商官方手册结构上不写层高**。规格表的 CEILING 一栏只写材料，永远不写高度。已核实的三种官方原文形态：
  - `Ceiling — Paint Finish / Plaster Ceiling (where applicable)`
  - `CEILING — Skim Coat / Plaster Ceiling Where Applicable`
  - `CEILING — Skim Coat with Paint and/or Plasterboard Ceiling with Paint`
- **层高只出现在第三方项目评测博客**。最有效的是 `propcafe.net`，它的项目评测会写「The ceiling height of 3.3meter (near to 10 feet)」。**该站需要 User-Agent 才能 curl**，无 UA 返回空：
  ```bash
  curl -sL --max-time 45 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36" \
    "https://propcafe.net/propcafe-<项目>-<地区>-by-<开发商>/" -o /tmp/x.html
  ```
  站内检索：`https://propcafe.net/?s=<关键词>`，用 `grep -o 'entry-title"><a href="[^"]*"'` 提取文章 URL 列表
- **`WebSearch` 对层高完全无效**：会返回美国天花板建材厂商页面。`html.duckduckgo.com` 与 `lite.duckduckgo.com` 对 curl 返回空；`bing.com/search` 能返回页面但**引号搜索被降级**（搜 `"M Vertica"` 返回 M Resort & Hotel）。冷门字段只能靠「定向抓已知站点的文章全文 + 正则提关键词上下文」
- 拿不到时的正确做法：标注「未公开」+ 给**行业惯例区间**（2000–2010 竣工约 9 ft / 2013–2020 约 10 ft / 2020 后新盘 3.0–3.3 m），并注明这是推断不是实测。**不要编数字**

**阳台**
- 官方手册的图例会写「All units come with balcony」这类总括句，比逐个户型图看更快
- 反例要抓：有的项目小户型是「With Yard · Without Balcony」——要阳台的用户必须排除小户型
- 阳台细节加分项：配水龙头（清洁/浇花）、yard 连阳台（晾衣）、阳台门材质（铝框玻璃推拉门）

**室内交付标准（三级，必须区分）**
1. **裸装**：无厨房无电器（原文常写 `The unit is bare i.e. no kitchen or electrical items`），可能只给空调 + 热水器
2. **给点位不给家电**：给灯点/风扇点/插座点/空调点位/hob & hood 点位/热水器点位 + 厨柜 + 地板 + 数字门锁。**马来西亚新盘多数属这一级**，买家需自购 4–5 台空调（约 RM8,000–15,000）
3. **含家电**：多为**前业主自装**，中介房源写的「含 AC×4 + 全厨柜 + 全房衣柜」不是开发商交付
- 看房必问四件事：厨柜是开发商给的还是前业主装的？空调是点位还是实物？热水器是点位还是实物？有没有**每房独立分表（sub-meter）**（决定能否按实际用电跟租客结算）

### 11. 管理层调研（用户问「管理层的管理方式」时）

**管理费** —— 相对好拿，但要标口径
- 好源：`propertysifu.my`、`affirmplus.com`、`kaiproperties.my`、`klproperty.cc`、`propcafe.net` 评测
- 多数报价**已含 10% 储备金（sinking fund）**，要写清是否含
- 必须换算成**实例月费**（费率 × 最大户型面积），因为用户关心的是实际付多少钱
- 按建筑面积算，不是实用面积

**JMB / MC 公司全名** —— 公开网络基本不可得，别浪费时间
- 已试且失败：DBKL JMB 名录（页面只有标题的空壳）、`hba.org.my/help/COB-LIST.htm`（2012 年旧页，只有 COB 办公室地址）、MBDK senarai JMB PDF（**只覆盖巴生，不含吉隆坡**）、`etps.kpkt.gov.my`、分层仲裁庭记录
- **唯一可能拿到的例外**：大型综合发展区的园区级管理机构，会出现在开发商新闻稿里。例：Sunway Velocity 全区由 JMB 治理 + 多个 component 共用 1 个 MC + sub-MC，共用基础设施由 **Sunway Property & Facility Management Sdn Bhd（SPFM）** 管 —— 这条来自 sunwayproperty.com 的获奖新闻稿
- 正确做法：明确写「未公开」，并告诉用户只能向管理处索取管理费账单或年度大会（AGM）通知

**保安层级**：搜「3-tier security」「multi-tier security」+ 项目名，比搜「管理」有效

### 12. 宠物政策调研（用户问「是否养宠物」时）

**法律基线（马来西亚，可套用到所有分层物业）**
- 依据《2015 年分层管理（维护与管理）条例》第三附表 **By-Law 14**：住宅单位业主不得饲养「造成他人烦扰或滋扰 / 危及他人安全健康 / 违反任何成文法或地方政府规章」的动物
- 关键定性：**By-Law 14 不是全面禁养，它设的是滋扰与安全标准**（`does not ban pets outright`）
- JMB / MC **可以禁养**，但必须经**特别决议**通过附加附例（additional by-laws）并向建筑专员（COB）注册
- **最重要的坑**：从未经程序通过的告示牌或委员会通告**不能作为罚款依据**
- 罚则：警告 → 委员会决议罚款（每次上限 **RM200**）→ 分层管理仲裁庭（SMT）；By-Law 14(2) 可发书面通知要求 3 天内移走动物，但**无权在无法院或 SMT 命令下扣押宠物**
- **DBKL（吉隆坡）**：允许养宠但**每户限 1 只**，且只限小型犬种，须领狗牌、附 JMB/MC 同意函

**逐项目核实方法**
- 最好的证据是**开发商官方明文**：官方手册地面层图例里的「Pet-friendly Park」、官网 Features 列表里的「Pet-friendly」
- ⚠️ **民宿平台的「No pets」≠ JMB 附例**。已发现同一项目在不同民宿平台一个写 allowed 一个写 not allowed —— 那是短租房东的个人政策，完全不可作证据
- `speedhome.com` 的 pet-friendly 筛选页是 SEO 营销页，正文常常没有一条带 pet 标签的房源，**不可作证据**（但可作为弱旁证）
- `oyen.my` 有 pet-friendly 公寓名单，可用来反查（目标项目不在列 ≠ 禁养）
- 找不到明文时的正确结论：「无明文，回落 By-Law 14 默认允许」，并给出「买前向管理处索取附加附例副本」的实操建议

## 常见坑
- 别用 `WebFetch` 抓 JS 渲染的列表页，浪费一轮；直接用 `mudah.my/<项目slug>` 的静态列表页
- ⚠️ **「步行可达」是整份报告最容易被中介文案污染的一项，必须自己判定**。实测规律：**门户/中介写的「步行 5 分钟到 <地标>」通常指该地标旁边的枢纽区（如 Abdullah Hukum），不是山上/对岸的盘**。正确做法是分三级明写：
  - 🟢 有盖步道 / 天桥直连（唯一可称「步行」）
  - 🟡 步行到 LRT/KTM 站可行，再 1–3 站轨道到目的地
  - 🔴 直线距离 <2 km 但无桥可走 → **实际不可步行**，只能车行
  同时**必须查该步行路径的治安**：实测 StarProperty 记载某片区「一名日本女士从商场步行回公寓途中被摩托匪抢劫，步行道一带发生多起案件」。
- ⚠️ **同一个楼盘可能以两个名字出现在两份名单里，且门户字段完全相同（同一份数据被复制）**。实测 Robson Condominium 与 Bukit Robson Condominium 在 mudah 上都是「160 户 / 15 层 / 1996 年」，但 StarProperty 明确是两栋不同的楼（前者 2 栋带双层会所+网球场，后者 1 栋 16 层 Tudor 风格）。**门户字段全同 = 高度可疑的复制粘贴，必须用 StarProperty 拆开。**
- ⚠️ **门户的项目字段会整体错配到同名/近名项目上**。实测 mudah 把「Robson Condominium」的户数层数同时写给了 Bukit Robson；把「Le Chateau」（StarProperty 称 5–6 层低层公寓）写成 17 层 30 户（那其实是 Le Chateau 2）。**户数/层数/竣工年这三项，门户与 StarProperty 冲突时优先信 StarProperty。**
- ⚠️ **名单里会出现「名称对不上」的项目，不要硬找**。实测两例：`Bayu Angkasa` 在 Bangsar South 检索只找到柔佛 Iskandar Puteri 的同名盘（实际在 Bangsar 的 Jalan Kapas 确实存在，但两个片区代理各自只找到自己那边）；`Putra Ria Apartment` 本区只有 `PPR Pantai Ria`（廉价组屋，1,264 户，约 RM350 psf）。**处理方式：写进「名称对不上」小节，给出最可能的对应项目，并注明与预算是否匹配，不要编造字段。**
- ⚠️ **项目名里的地标名可能是误导，必须靠「Transport stations」字段判定**：实测 `Surian Condominium` 与 `Surian Residences` 的最近站都是 **KG08 Mutiara Damansara（909 m）**，距 `Surian` 站（KG07）约 1.6 km、距 IOI Mall Damansara 2.3 km —— **名字带「Surian」但不在 Surian 站旁**。同理 `The Havre` 实为 Bukit Jalil 项目、`Taman Kasturi` 在 Cheras。**不要靠项目名推断位置，逐个读页面的「Transport stations」模块确认最近站。**
- ⚠️ **同一栋楼可能以两个项目名出现在名单里**（如 `Establishment Bangsar (Menara Teguh)` 与 `Alila Bangsar` 实为同一栋，EdgeProp 项目名是「The Establishment (Alila Bangsar)」，原名 Menara Teguh Bangsar）。**合并处理，在卡片里说明。**
- ⚠️ **性质不符的项目要单独标出**：名单里的「公寓」可能是 ① 有地联排别墅（Westbank Terraces，38 户 freehold landed townhouse）；② 廉价 flat（Putra Ria / PPR Pantai Ria）；③ 服务式公寓 / SOHO（商业地契）；④ 不在该片区的项目（Merc Residence 实际在 Taman Bukit Desa，不在 Bangsar）。**这四类要单独说明，否则买家会按公寓口径评估。**
- ⚠️ **mudah 的「<地标>」地区分类页极度脏**：`mudah.my/kuala-lumpur-mid-valley-city/apartment-condominium-for-sale` 里 41 条有 38 条是中介广告（标题写「10 Mins to Mid Valley」「Near Midvalley」），实际项目在 Sungai Besi / Salak Selatan / Kuchai Lama / Taman Desa。**必须逐条核对项目名，不能直接采信地区分类。**
- ⚠️ **MyRumahBaru 的「Median PSF」在部分项目上是区级回退值，不是项目级成交中位**。判别方法：如果几个不相关项目出现**完全相同**的数字（实测 Setia Sky Seputeh 与 Seputeh Permai 均为 420.69；Tivoli Villas 与 Palmyra Bangsar 均为 873.83），就是回退值。**不能直接用于估值**，报告里要标出来。
- ⚠️ **同一开发商的相邻两栋楼也可能共享同一份成交数据**。实测 Vogue Suites One 与 Vogue Suites Two（同属 KL Eco City、同为 S P Setia）在 MyRumahBaru 上**中位 psf 都是 RM1,282.43、成交笔数都是 22**，且近期成交明细（L39A 958 sf、L39 904 sf）逐条相同 —— 两栋不同楼不可能有完全一样的成交序列。**判别法：把两个项目的「中位 psf + 成交笔数 + 近期成交明细」三者对照，只要有两项相同就判为疑复制**，报告里明写「至少有一个项目的市场价锚不可信」，并建议向估价师分别核实。
- ⚠️ **门户的「Total Units」可能与官方差 2 倍以上**。实测 Vogue Suites Two：mudah / PropertyGuru / PropertyGenie 三源都是 344 户，但 PropertyGuru 的马来文页另标 **739 户**（疑为 Vogue 1+2 合计）。**多源一致时取多数，但要在冲突清单里保留异常值** —— 739 这个数一旦被中介引用，就会污染买家的密度判断。
- ⚠️ **同名项目跨区**：`V Residence / V Residence Suites / V Residence 2 / V Residence 3` 是 **Sunway Velocity（Cheras）** 的项目，与 **KL Eco City（Bangsar）** 无关。KL Eco City 的住宅叫 **Vogue Suites One / Vogue Suites Two / ViiA Residences**。搜索时必须带区名，否则整份名单错位。
- ⚠️ **门户挂牌面积可能是错的**：实测 Pantai Panorama 一条 RM1.4M / 5,037 sf 的挂牌（=RM278 psf），但同盘其他单位全在 1,108–1,250 sf。**离群面积必须与同盘其他挂牌交叉核对**，否则会得出「单价倒挂 5 倍」的假结论。
- ⚠️ **挂牌总价区间常被误读为在售价**：`myrumahbaru` 的「Price Range SPA Price Before Rebate」对期房是**全盘户型区间**（如 Vogue Suites One RM649,000–RM3,990,000），不是当前在售价。
- 距离字段一定要标明口径：**MyRumahBaru 给的是「直线距离」**（2026-09-28 用内嵌 geo 坐标反算验证，非路径），中介广告给的多是**驾车**或直线距离，两者能差 2 倍。**口径复核方法**：抓页面内嵌 JSON-LD 的 geo 坐标（项目 + POI 各自一个），自己做球面直线距离，与页面文字对比即可确认是直线还是路径。
- `irumah.co` 403 时改试 `myrumahbaru.com` 同名项目页，数据更全（**注：带完整 UA 的 curl 其实能打开 irumah.co，只是字段多为 -NA-，价值在「同开发商/同片区相似项目」列表**）
- 门户的「Freehold」标注与开发商官网冲突时，**以开发商官网 / 地契为准**
- 同一园区常有 4–5 个名字相近的楼栋（如 V Residence / V Residence Suites / V Residence 2 / V Residence 3），户数面积单价都不同，别混着写
- 高价段（>RM1M）的库存**不在**门户列表页的首页 40 条里。必须按项目名逐个抓，否则会得出「这个价位没货」的错误结论。
- **层高、JMB 公司全名、阳台尺寸、宠物附例**这四个字段公开网络基本拿不到。提前预判、直接标「未公开」并列出已试来源，比反复搜更省时间，也更能体现调研的完整性
- 已确认 403 / 空壳的源：`irumah.co`、`allyproperties.my`、`malaysiahome.my`、`newpropmy.com`、`edgeprop.my/buy/*` 列表页、`dbkl.gov.my` JMB 名录页
- 写报告时对每个字段标三级可信度（已确认 / 推断 / 未公开）。用户看到「未公开 + 已试 N 个源」比看到一个编出来的数字有价值得多

### 官方 e-brochure PDF 是最有价值的一手源 —— 要主动去找直链
它比官网 HTML 信息密度高一个量级，通常含：**法定备案价、土地限制条款、完整设施分层图例、逐型户型图与尺寸、交付规格表、许可证号与有效期**。官网 HTML 上找不到的「Restriction of Interest」「Bumiputera 折扣」「Sales Permit 有效期」都在这一页。
```bash
# 已知可直下的例子
curl -sL --max-time 45 -A "<UA>" "https://sunwaycochrane.com/pdf/Sunway-Cochrane-Full-Brochure-EN.pdf" -o brochure.pdf
# ippstatic 镜像（新盘手册常放这里）
curl -sL --max-time 45 "<https://newlaunch-my.ippstatic.com/live/MY/brochure/...>" -o brochure.pdf
```
提取文本（**注意路径要用工作区目录，见下方平台坑**）：
```
C:\Users\Admin\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe -c "import pypdf; r=pypdf.PdfReader(r'brochure.pdf'); print('\n'.join((p.extract_text() or '') for p in r.pages))"
```
找不到直链时试 `<项目站>/pdf/` 下的常见命名，或查 Wayback CDX 列举历史 URL。

### 平台坑
- ⚠️ **MSYS 的 `/tmp/...` 字面路径对 Windows 原生 Python 不可见**（`open('/tmp/x')` 报 `FileNotFoundError`）。两个可行做法：① 用 Windows 形式 `C:\Users\<user>\AppData\Local\Temp\<proj>\`（`cygpath -w /tmp/<proj>` 可查）；② **先 `cd /tmp/<proj>` 再用相对路径**——这样 Windows Python 能正常读写。实测 `cd /tmp/mv && python final.py`（脚本内部全用相对路径）完全可用。
- ⚠️ **`Read` 工具读不了 `/tmp/...`**（MSYS 路径映射），要用 Windows 形式路径或 `cat`。
- `klmetro.org` 对 curl 返回空；Wikipedia 消歧义页（如 `Cochrane_station`）无用，要用 `?action=raw` 抓准确条目（`Cochrane_MRT_station`）。
- `propcafe.net` 需要 User-Agent 才能 curl（无 UA 返回空），是少数会写**层高**的公开源。
- **`WebSearch` 会偶发 524 超时**，重试或换更短的关键词即可，不要因一次失败就放弃该源。
