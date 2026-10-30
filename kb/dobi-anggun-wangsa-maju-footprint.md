---
id: dobi-anggun-wangsa-maju-footprint
title: Dobi Anggun Wangsa Maju 数字足迹盘点（哪些网站收录了这家马来西亚洗衣店）
tags: [osint, google-maps, malaysia, laundry, business-footprint, due-diligence, directory-scraping]
created: 2026-10-27
updated: 2026-10-27
version: 2
status: active
source: 直连各平台实测 + 目录站结构枚举 + Brave/DDG/Bing RSS/Nominatim 交叉验证（2026-10-27）
confidence: 高（6 个收录平台均已抓到页面实体；方法论缺陷已修正）
---

## 一句话结论

至少 **6 个平台**有收录：一手源 4 个（Google Maps / Facebook / TikTok / Milkshake 官网）+ **数据镜像目录 2 个**（WorldOrgs / Cleaners10）。v1 版判定"无第三方目录收录"是**错的** —— 错在把「搜索引擎搜不到」当成「不存在」。

---

## 一、实体确认

| 项 | 值 |
|---|---|
| Google Maps 官方名 | **Dobi Anggun (Full Service)** |
| WorldOrgs 名 | **Dobi Anggun** |
| Cleaners10 名 | **Dobi Anggun Wangsa Maju** |
| 类别 | Laundry / Perkhidmatan Dobi（洗衣服务） |
| 地址 | No 1, Block CS-B, Jalan 3/27A, Section 1, Wangsa Maju, 53300 Kuala Lumpur, Malaysia |
| 电话 | +60 16-723 8684（= 0167238684 = +60167238684） |
| 营业时间 | 周一至周日 10:00–19:00 |
| 评分 | **4.7 / 10 条评价**（WorldOrgs 镜像自 Google，v1 未取到） |
| 坐标 | 3.202669, 101.729197 |
| 服务范围 | Section 1 Wangsa Maju 半径 10 km 上门取送 |
| 服务项 | wash/dry/fold、熨烫、干洗、手洗、被褥清洗、地毯清洗 |

---

## 二、确认收录（全部已抓到页面实体）

### A. 一手源

| # | 平台 | 地址 | 关键内容 |
|---|---|---|---|
| 1 | **Google Maps** | `Dobi Anggun (Full Service)` | 地址、电话、营业时间、类别 |
| 2 | **Facebook** | facebook.com/dobianggun.wmaju | 514 likes；简介 "Laundry & Dry Cleaning Pick Up & Delivery Service. 10Km radius from Section 1"；**page id = 715451805515008** |
| 3 | **TikTok** | tiktok.com/@dobi.anggun.wangsa.maju | oEmbed 返回 "Dobi Anggun Wangsamaju's Creator Profile" |
| 4 | **Milkshake** | msha.ke/dobianggunwm | 自建单页站，服务清单 + WhatsApp 预订 |

### B. 数据镜像目录（v1 漏检）

| # | 平台 | 地址 | 数据源 | 关键内容 |
|---|---|---|---|---|
| 5 | **WorldOrgs MY** | my.worldorgs.com/katalog/kuala-lumpur/perkhidmatan-dobi/**dobi-anggun** | Google Maps | 4.7 分 / 10 条评价 + **3 条马来语评论原文**；地址、电话、坐标 |
| 6 | **Cleaners10** | cleaners10.com/MY/Kuala-Lumpur/**715451805515008**/Dobi-Anggun-Wangsa-Maju | Facebook Page | 地址、+60167238684、全周 10:00–19:00、简介、Call/Directions 按钮 |

**两站的 URL 构造规律（可复用）**

```
WorldOrgs : /katalog/{city-slug}/{category-slug}/{name-slug}
            城市 slug 用马来语，洗衣 = perkhidmatan-dobi / kedai-dobi / kedai-cucian-kering
Cleaners10: /MY/{City-Slug}/{facebook_page_id}/{Name-Slug}
            页面 id 就是 FB page id —— 拿到 FB id 即可直接拼 URL
```

---

## 三、漏检根因（v1 为什么错）

| # | 错误 | 具体表现 | 性质 |
|---|---|---|---|
| 1 | **把"搜不到"等同于"不存在"** | 结论写"没有任何第三方商家目录收录"，实际只是"搜索引擎没返回" | 逻辑错误，最严重 |
| 2 | **单一引擎依赖，失败即停** | Brave 429 后未切换策略，直接收尾 | 执行缺陷 |
| 3 | **垂直目录清单不全** | 只想到 yellowpages/cybo/hotfrog 这类传统黄页，漏了「行业+数字」模板站（cleaners10）和「多国聚合站」（worldorgs）两类 | 认知盲区 |
| 4 | **没用站点自身信息架构** | 两站都有 城市→分类→商家 三级静态导航，可直接枚举；却只试了 `?q=` 搜索参数，404 就放弃 | 方法错误 |
| 5 | **URL 猜错后不换路径** | 猜 `/MY/Kuala-Lumpur` 得 404 就判死，没去 `/MY` 首页找 `/MY/cities/W` 的城市索引 | 韧性不足 |
| 6 | **没做"数据源→镜像站"反查** | 已知有 FB page，就应想到 FB 数据镜像生态；已知有 Google 商家，就应想到 Google Maps 镜像站 | 缺推理链 |
| 7 | **结论措辞过强** | 用"有否定证据"包装"我没找到"，误导读者 | 表述失实 |

**核心教训**：搜索引擎是**发现工具**，不是**存在性证明工具**。小目录站 SEO 权重低、收录慢，恰恰是最容易被搜索引擎漏掉的一类 —— 而它们又最可能收录长尾商家。

---

## 四、改进方案：三层扫描法

```
L1 发现层（搜索引擎）—— 只用来找线索，不用来下结论
   Brave（唯一稳定）/ DDG html（一次性）/ Mojeek
   查询顺序：店名+区域 → 唯一地址 → 电话裸查 → site:{已知目录} 店名

L2 直连层（平台验证）—— 拿权威数据
   Google Maps（必须带 JS 渲染，curl 拿不到）
   TikTok oEmbed / FB graph picture 跳转（拿 page id）
   Nominatim（OSM 收录判定）

L3 枚举层（目录站结构爬取）—— 不依赖搜索引擎，这是补全的关键
   对每个目录站：找国家页 → 城市索引 → 分类页 → 分页遍历 → 关键词匹配
   关键技巧：先拿 FB page id，可直接拼 Cleaners10 类站的 URL
```

### 判定分级（替代原来的二分法）

| 等级 | 定义 | 表述 |
|---|---|---|
| ✅ 已确认收录 | 抓到页面实体，含该商家数据 | "收录，URL=..." |
| ❌ 确认未收录 | 该站同类目已穷举，无此条目 | "已枚举 N 条同类，无此商家" |
| ⚠️ 索引残留 | 搜索引擎有 URL，页面已失效 | 单列，不算收录 |
| ❓ 无法验证 | 反爬/登录/付费阻断 | 明确写"未验证"，**不写"未收录"** |

---

## 五、可复用脚本

### 5.1 Cleaners10 类站：用 FB page id 直拼 URL

```bash
# 从 FB 头像跳转拿 page id（头像 URL 里的数字不是 page id，需用 mbasic 或页面源码）
# 更稳：直接遍历分类页找 urlPath
for p in 1 2 3; do
  curl -s "https://www.cleaners10.com/MY/Kuala-Lumpur/1453453/genre/133148010085253/Dry+cleaner/$p" \
  | grep -o "urlPath:'[^']*[Aa]nggun[^']*'"
done
```

城市索引在 `/MY/cities/{A-Z}`，城市页 `/MY/{City-Slug}/{city_id}`，分类页在 `/genre/{genre_id}/{Name}/{page}`。

### 5.2 WorldOrgs 类站：城市→分类→商家 三级枚举

```bash
# 1. 城市页列出全部分类（马来语 slug）
curl -s "https://my.worldorgs.com/katalog/kuala-lumpur" \
  | grep -o '/katalog/kuala-lumpur/[a-z0-9-]*dobi[a-z0-9-]*' | sort -u
# → kedai-dobi / perkhidmatan-dobi / kedai-dobi-layan-diri

# 2. 分类页含商家卡片 + 地图 JSON（lat,lng,title,path 三元组）
curl -s "https://my.worldorgs.com/katalog/kuala-lumpur/perkhidmatan-dobi" \
  | grep -o '\[3\.[0-9]*,101\.[0-9]*,"[^"]*"' | head
# 地图 JSON 是最好用的批量提取点，一次拿到全部坐标+名称+路径
```

### 5.3 判定"确认未收录"的穷举标准

必须同时满足：① 该站分类页已遍历完所有分页；② 该城市下同类目条目数已核对；③ 关键词做过大小写/连字符/空格变体匹配。否则只能标 ❓。

---

## 六、同类"数据镜像站"清单（下次直接扫）

| 数据源 | 镜像站 | 已知可用性 |
|---|---|---|
| Google Maps | **WorldOrgs**（19 国，马来 87 万条） | ✅ 无拦截，可枚举 |
| Google Maps | Cybo / Nicelocal / Placebrowse / Yellow.place / Infobel | ⚠️ 多数 403/需正确 URL |
| Facebook Page | **Cleaners10**（行业+数字模板站群） | ✅ 无拦截，可枚举 |
| 用户签到 | Foursquare | ❓ 登录墙 |

> 注意：Cybo、Nicelocal、Infobel 等站 URL 猜测几乎必失败，必须从首页导航或 sitemap 进入，不能拼 `?q=`。

---

## 七、索引残留 / 疑似失效

| 平台 | 状态 | 证据 |
|---|---|---|
| **Waze** | ⚠️ SEO slug 被索引，页面失效 | Brave 收录 `waze.com/kn/live-map/directions/dobi-anggun-jalan-327a-kuala-lumpur`，直连返回 "That location wasn't found" |
| **Instagram** | ⚠️ 疑似已删/改名 | 官网仍链 `instagram.com/dobi.anggun.wangsa.maju`；IG 返回 "Profile isn't available"；imginn 镜像无数据 |

---

## 八、同名不同店（检索干扰源）

| 实体 | 位置 | 来源 |
|---|---|---|
| Dobi Anggun | Guar Chempedak, **Kedah** | Course Hero 学生创业计划书，2018-04-01 开业 |
| Cuci Karpet Seri Iskandar - Dobi Anggun | Seri Iskandar, **Perak** | Facebook 页，5 likes |

---

## 九、明确未收录（已穷举验证）

| 平台 | 验证方式 | 结果 |
|---|---|---|
| OpenStreetMap / Nominatim | API 查询店名与电话 | 返回 `[]` |
| Mudah.my | 搜索页 | 标题 "0 Dobi Anggun For Sale"，零结果 |
| Hotfrog Malaysia | 搜索页 200 | 无命中 |
| Bing Maps | 搜索页 | 无结果面板 |
| WorldOrgs `kedai-dobi` / `kedai-cucian-kering` 分类 | 分类页枚举 | 无（仅在 `perkhidmatan-dobi` 下） |
| Cleaners10 `Wangsa-Maju` 城市页 | 全页 7 条枚举 | 无（实际挂在 Kuala Lumpur 城市下） |

---

## 十、无法验证（不写"未收录"）

yellowpages.my（Cloudflare 403）、Cybo（403）、Nicelocal（连接失败）、Foursquare（登录墙）、Apple Maps / Google 网页搜索（纯 JS）、SSM e-Search（付费）、Yelp（马来无运营）。

---

## 十一、坑与反直觉

1. **curl 抓 Google Maps 永远拿不到数据**（SPA + JS 渲染），但带渲染的抓取可以。
2. **Cleaners10 的页面 id = Facebook page id**，不是头像 URL 里的数字。
3. **WorldOrgs 城市 slug 用马来语**，`dobi` 不是有效分类，正确是 `perkhidmatan-dobi`。
4. **WorldOrgs 分类页内嵌地图 JSON**（`[lat,lng,"name","path"]`），是最省力的批量提取点。
5. **"Panggung"（戏院）含 "anggun" 子串**，关键词匹配会假阳性，需整词匹配。
6. **同一商家在不同站的城市归属不同**：Cleaners10 归 Kuala Lumpur，不是 Wangsa Maju。按城市找不到时，往上一级城市找。
7. **评分/评论数据在镜像站反而比 Google Maps 页面好抓** —— v1 抓 Maps 拿不到 4.7/10 条，WorldOrgs 直接给了。
8. Mudah 的 "0 xxx For Sale" 是零结果 SEO 页，标题带 "0 " 前缀。

---

## 十二、未核实项

- Instagram 是"已删除"还是"已改名"（IG 对未登录统一返回 not available）。
- Waze 地点是否曾真实存在，还是仅由 Google 数据自动生成的 slug。
- yellowpages.my / Cybo / Nicelocal 是否收录（被 WAF 拦截）。
- 是否存在其他未枚举的镜像站（本次只覆盖 WorldOrgs + Cleaners10 两类模板）。
- 该店是否在 SSM 注册。
