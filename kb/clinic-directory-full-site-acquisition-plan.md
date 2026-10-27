---
id: clinic-directory-full-site-acquisition-plan
title: 三家诊所目录站全站采集：已验证路径与执行门槛
tags: [web-research, directory, clinics, scraping, malaysia, robots, access-control, data-quality]
created: 2026-10-27
updated: 2026-10-27
version: 1
status: active
source: 2026-10-27 实测公开页面、robots.txt、sitemap、源站请求响应
confidence: 高（Clinic RX 10 家分店官方源、AestheticClinic 100 URL sitemap、Seek Clinic 13 页抽样和 403 可复现）；中（Seek 全类别总量及 Tressless 全量未枚举）
---

# 三家诊所目录站全站采集

## 一句话结论

**“全站采集”不是一个三站共用的爬虫任务。** 现有公开证据支持：Clinic RX 自营官网可完整获取 10 家分店及一个共享 WhatsApp 号码；AestheticClinic.my 有 100 个诊所 URL 的官方 WordPress sitemap，但号码只在详情页，且部分是无电话的 Source Only；Seek Clinic 的 aesthetic 类目至少有 13 页、每页 9 条公开电话，但普通 HTTP 可复现 403，WebFetch 的分页读取只是点页查看，不构成全站程序化权限；Tressless 有一个 Clinic RX 聚合页，5 个分店、一个 clinic 级号码，站点 robots 对 archive crawler 明确禁止。**实际可行方案是官方源优先 + 授权/导出，不是绕过 WAF。**

## 一、实测依据

检查日期：2026-10-27。所有联系方式均为公开业务联系字段。

| 站点 | 已确认可用范围 | 具体实测 | 访问限制/缺口 |
|---|---|---|---|
| Clinic RX 官方站 `clinicrx.com.my` | **10/10 分店完整可读** | `/contact/` 列 10 个分店；每家 `/our-clinics/{slug}`；每页有 `WhatsApp Us` 链接，号码均 `+60102103921`；共 10 个地址、营业时间 | `robots.txt` 允许公开内容，禁止 `/api/`、`/studio/`、`/preview/`、`/draft-mode/`；无公开 bulk export/API。官方源是最优、范围明确方案 |
| AestheticClinic.my | **100 个 clinic profile URL 有 sitemap** | `wp-sitemap-posts-ac_clinic-1.xml` 声称 100 URL；记录含 URL/最后修改时间；`/clinics/` 索引可浏览 | 联系方式不在 sitemap；须逐一 profile。`Source Only` 明确无电话。普通请求挑战页；robots 仅禁 `/wp-admin/`，不等于许可全量复制 |
| Seek Clinic | **aesthetic-clinic 类目至少 13 页** | 抽查 page 1–13 均有内容，每页 9 条；page 14 返回 Page Not Found；列表直接有姓名、地址、`tel:` 电话、详情 URL。**本次一共从页面读取了这些分页，已有当前类别的可见数据** | robots 可读，Disallow `/wp-admin/`；sitemap index 有 95 个 child sitemaps。普通 curl 分类页返回 403（548B nginx shell），无法用本地 HTTP 批跑；未知其他类目数量。Terms 页面为模板占位文本 |
| Tressless | **Clinic RX 单页 5 个 MY 分店 + 1 个品牌电话** | profile 写 `5 locations · Malaysia`，电话 +60102103921；无医生姓名；分店页只列地址 | Cloudflare 403。robots 注释明确 profile challenge-gated，并说明 WAF 阻止 archive crawlers；不进行全站枚举 |

### Clinic RX 官方来源中直接读到的 10 个分店

- Bukit Jalil
- Publika
- Bangsar
- Cheras
- Puchong
- Southkey JB
- Austin JB
- Eco Botanic JB
- Georgetown
- Kota Kinabalu

官方 Branch URL 与号码已逐页核对；CSV：`outputs/clinic-directories/clinicrx_official_branches.csv`。

## 二、已验证可执行路径

### A. Clinic RX：可完成自营站分店全量

1. 打开官方 `/contact/`，把 10 个分店链接当作预期全集。
2. 逐页访问 `https://www.clinicrx.com.my/our-clinics/{slug}`，提取 branch、address、WhatsApp `phone` 参数、hours、source URL。
3. 按 branch 保留 10 行；另建唯一号码表，品牌 WhatsApp 共用一个号码，不能误写成 10 个独立电话。
4. 与 AestheticClinic / Seek / Tressless 的 Clinic RX 档案对比时，用地址/分店名匹配，明确记录冲突，不以品牌号替代分店专线。

**本步骤本轮已实际完成，见 CSV。**

### B. AestheticClinic.my：公开 URL 集合可完整获取，号码全集须逐档核验

1. 使用提供的 WordPress sitemap `https://www.aestheticclinic.my/wp-sitemap-posts-ac_clinic-1.xml`，完整取得 100 个详情 URL。
2. sitemap 只含 URL 和 lastmod；没有电话字段或批量导出。
3. 只有在正常页面访问/网站许可成立后，逐一抽取 profile 的 completeness、phone/contact route、branch address、verification cut-off。
4. `Source Only` 且明示 contact details unavailable/not verified 的记录标为 `no_public_contact`，不能补造电话。
5. 最后检查 100 个 URL 去重后成功数、Complete/Source Only 数、缺电话数和号码唯一数。

**可确定的是 100 个 profile URL；当前没有从这些 URL 构成全站电话表。**

### C. Seek Clinic：当前类别有可直接读的电话字段，但本机被 403 拦截

1. 目标类别 URL：`https://seekclinic.my/category/aesthetic-clinic-1/page/N/`。
2. 页内每条记录直接含名称、地址、电话、详情 URL；抽样确认每页 9 条。
3. 在可正常访问的授权浏览器/API 环境中，从 page 1 开始存档，遇首个 Page Not Found 停止；抽样边界是 page 13 有、page 14 404。
4. 本次本地 `curl` 重测 page 1 返回 403 + 548 字节 nginx 页面；不尝试代理、指纹伪造或挑战绕过。需网站授权/恢复正常访问通道后再让脚本遍历。
5. 目录数据质量检查：同号码多分店保留多行；电话号码标准化；重复详情 URL 合并；每行存来源页 URL 和日期。

**本次可复用的已读页面集合：page 1–13，合计最多 117 个 listing slot，实际每页显示约 8–9 条；这只是已读类别页面，不代表完成稳定的结构化全集导出。**

### D. Tressless：不做全站爬取

1. robots.txt 对一般 user-agent 虽有 `Allow: /`，但注释明确说明 profile 对非浏览器 challenge-gated，并提到 Cloudflare WAF 阻挡 archive crawler。
2. 可读取单条公开页面用于研究，不把单条可访问等同于允许全站镜像。
3. 若确实需要目录级数据，向 Tressless 请求授权、官方数据导出或 API；不做绕过 Cloudflare/挑战的方案。

## 三、数据模型（避免“号码=门店专线”的错误）

推荐最少字段：

| 字段 | 用途 |
|---|---|
| source_site | 来源站 |
| source_url | 来源 URL |
| record_type | clinic / branch / doctor / directory listing |
| name | 页面显示的机构或个人姓名；没有具名医生时留空 |
| branch | 门店名称 |
| address | 原文地址 |
| phone_raw | 页面原始电话 |
| phone_normalized | E.164 规范化值 |
| contact_type | call / WhatsApp / contact route / unknown |
| verification_status | complete / source-only / not-verified / blocked |
| checked_at | 检查日期 |
| notes | 共用品牌号、地址冲突、过期等 |

注意：Tressless 与 Clinic RX 官方站都显示**一个品牌 WhatsApp 覆盖多个分店**。这是同一号码的多 branch 联系入口，不等于每个分店有独立电话。

## 四、停机条件和授权门槛

出现以下任一情况，自动化立即停止该站：HTTP 403/429、Cloudflare/nginx 挑战、CAPTCHA、登录墙、robots 对目标路径明确 Disallow、页面提示挑战门禁、站点要求申请访问。换 UA、换代理、浏览器指纹伪装、抓取 challenge token 均不属于解决方案。

在规模化采集和再发布前，取得网站书面许可或官方 API/导出。用户的研究用途声明不等同于来源网站授权；公开号码也仍涉及平台 ToS、数据库复用和个人数据保护边界。

## 五、质量验证清单

- URL 全集：来源 sitemap/category index；检查页数边界，不能靠搜索引擎索引代替。
- 每条记录：页面存在、名称非空、来源 URL 可追溯。
- 联系方式：保留原文、类型和分店；不将品牌号复制成独立门店号码。
- 电话校验：国家码、长度、占位符；记录无号码状态，不猜测。
- 状态差异：Complete / Source Only / blocked 分开计数。
- 对账：成功数 + 失败数 = URL 总数；若不等，列出失败 URL 并经允许重试。
- 输出字段：CSV 使用 UTF-8 BOM 便于 Excel；另存 JSONL 原始记录可用于后续审计。
- 公开归档：确认仓库 public/private；电话属于可识别业务联系信息，必须记录来源与许可状态。

## 六、结论状态

| 目标 | 状态 | 下一步 |
|---|---|---|
| Clinic RX 官方官网 10 家分店 | **已实做完成** | 使用本地 CSV；若要扩展到所有诊所品牌，逐个官方站点分别建来源 |
| AestheticClinic.my 100 家 profile URLs | **URL 可完整枚举；电话未全量提取** | 获得许可/正常访问通路后逐条读取 |
| Seek Clinic aesthetic 类别 | **本次读取 page 1–13；本机程序化访问受 403** | 有许可的正常浏览器/API 通道后解析全部分类页 |
| Tressless 全球目录 | **未全量枚举** | 先申请官方数据授权；不绕过其明确 WAF/归档限制 |

## 七、未核实项

- AestheticClinic 100 个 profile 中 Complete/Source Only 的准确比例与有效号码数量。
- Seek Clinic 95 个 sitemap 的类型与总 listing 数；分类之外有无重复/已下线记录。
- Tressless 全球目录总量、马来西亚条目全量与站点 API/导出政策。
- Clinic RX 官方 10 家分店的电话号码目前全部链接到同一 WhatsApp，是否有门店直线电话未在页面列出。
- 三站对批量抓取、复制和公开再发布的完整条款；本报告不构成法律意见。
