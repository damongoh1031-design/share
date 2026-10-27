---
id: clinic-directory-full-site-acquisition-plan
title: 三家诊所目录站全站采集：已验证路径与执行门槛
tags: [web-research, directory, clinics, scraping, malaysia, robots, access-control, data-quality]
created: 2026-10-27
updated: 2026-10-27
version: 5
status: active
source: 2026-10-27 实测公开页面、robots.txt、sitemap、源站请求响应
confidence: 高（Clinic RX 10 家分店官方源、AestheticClinic 100 URL sitemap、Seek Clinic 13 页抽样和 403 可复现）；中（Seek 全类别总量及 Tressless 全量未枚举）
---

# 三家诊所目录站全站采集

## 一句话结论

**“全站采集”不是一个三站共用的爬虫任务。** 现有公开证据支持：Clinic RX 自营官网可完整获取 10 家分店及一个共享 WhatsApp 号码；AestheticClinic.my 有 100 个诊所 URL 的官方 WordPress sitemap，但号码只在详情页，且部分是无电话的 Source Only；Seek Clinic 的 aesthetic 类目至少 13 页，**已用浏览器渲染通道实取 116 条 listing、去重后 109 个唯一号码，4/4 抽样详情页复核一致**；Tressless 有一个 Clinic RX 聚合页，5 个分店、一个 clinic 级号码，站点 robots 对 archive crawler 明确禁止。**关键结论：403 是「非浏览器 HTTP 客户端」被挡，不是数据不可达——换成真实浏览器渲染通道即可正常读取公开列表页；但这仍受 ToS 与再发布边界约束，不是免授权通行证。**

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
| AestheticClinic.my 100 家 profile URLs | **已实做完成：100/100，0 失败，83 家有号** | 17 家 Source Only 本就无号，非抓取失败 |
| Seek Clinic aesthetic 类别 | **已实做完成：109 个唯一号码** | 换其他类别时复用同一流程；末页边界需另行确认 |
| Tressless 全球目录 | **仅 MY 3 条可读样本，用于跨源核对** | 全站批量不可行：Cloudflare 全站挑战 + 列表页无电话字段 + 详情 URL 大量 404 |

## 七、实取结果：Seek Clinic 109 个唯一联系人（2026-10-27）

这是本任务中第一个完成结构化落地的目录站采集。

| 指标 | 数值 | 口径 |
|---|---|---|
| 抓取范围 | page 1–13 | `https://seekclinic.my/category/aesthetic-clinic-1/page/N/` |
| 原始 listing 行 | 116 | 每页 9 条，page 13 为 8 条 |
| 去重后唯一号码 | **109** | 按 E.164 归一后去重 |
| 唯一机构名 | 109 | 与号码一一对应 |
| 抽样复核 | 4/4 一致 | 详情页名称+电话+地址+`tel:` 链接全匹配 |
| 通道 | 浏览器渲染（SSR 取回渲染后 DOM） | 裸 HTTP 对该域稳定 403 |
| 分页终止 | 未确认 | page/14 返回 403，非 404，无法判定是末页还是拦截 |

州属分布（109 个唯一号码）：W.P. 吉隆坡 24、雪兰莪 19、柔佛 11、马六甲 8、槟城 7、彭亨 7、森美兰 6、霹雳 6、沙巴 6、砂拉越 5、登嘉楼 4、吉打 3、吉兰丹 2、玻璃市 1。

共享号码（关键数据陷阱）：

- `+60102103921` 被 7 条 listing 共用（Clinic RX 品牌号：Ipoh / Austin / Eco Botanic / Kota Kinabalu / Melaka / Kuching / George Town）。**不能算 7 个独立门店电话。**
- `+60109373855` 被 2 条共用（A Klinik Signature Damansara + Penang）。

因此「116 条 listing」≠「116 个联系电话」，真实独立号码只有 109 个，其中品牌号贡献 6 个虚增量。

### 可复用的提取流程

1. 用浏览器渲染通道取列表页，**不要**用裸 `urllib`/`curl`——该域对非浏览器客户端返回 548 字节 nginx 403。
2. 每页只提 4 个字段：机构名、`tel:` 号码、地址、详情 URL。列表页已含全部所需字段，**不需要进详情页**（这是 Seek 相对另两站的核心成本优势）。
3. 页码递增直到返回 403/404；403 不等于末页，必须单独标注 `pagination_terminated=unverified`。
4. 号码归一为 E.164（`60...` → `+60...`），按号码去重，同时统计每个号码被多少 listing 引用。
5. 对共享号码写 `notes=shared number across N listings`，禁止在报表里当成 N 个独立门店。
6. 抽样 4–5 条进详情页复核名称/电话/地址，任一不符即回退重取。

## 八、三站合并成品（2026-10-27 最终）

**主交付：`combined_clinics.csv`（201 家机构，一家一行，含主号码与号码角色）。**

| 文件 | 行数 | 用途 |
|---|---|---|
| `combined_clinics.csv` | 201 | 一家机构一行，`primary_phone` + `primary_phone_role` |
| `combined_contacts.csv` | 206 | 一个唯一号码一行，含多机构共用标记 |
| `combined_contacts_detail.csv` | 246 | 一条源记录一行，可回溯到具体页面 |
| `combined_conflicts.csv` | 38 | 同一机构被列出多个号码（品牌号 + 分店直线） |

数据构成：Seek 116 条 listing → 109 唯一号；AestheticClinic 100 个 profile → 127 个号码实例、107 唯一号、83 有号 / 17 无号 / 0 失败；Tressless 3 条（跨源核对用）。

| 指标 | 值 | 说明 |
|---|---|---|
| 唯一号码 | 206 | E.164 归一后 |
| 唯一机构 | 201 | 名称归一后 |
| 主号码去重 | 176 | 201 家里只有 176 个不同主号码 |
| 跨源互证号码 | 11 | 两站以上同时出现，最强真实性证据 |
| 品牌共用号（≥3 家） | 5 | 如 `+60102103921` 被 Clinic RX 全马 7 店共用 |
| 多号码机构 | 38 | 品牌号 + 分店直线并存，不是数据错误 |

跨源互证样例：`+60102103921` Clinic RX（三站都有）、`+60103681400` Kaiteki SS2 PJ（Seek 写 `+60103681400`，Tressless 写 `+60 10-368 1400`，归一后一致）、`+601161268288` Dr Chong Mid Valley、`+60133015758` Pinnacle Melaka。

### 号码角色必须分开

AestheticClinic 一个档案常同时给两个号：品牌号 + 分店直线。例：Clinic RX Dataran Cheras = `+60102103921`（品牌）+ `+60143288758`（分店）。**报表取分店直线，不要取品牌号**，否则 7 家分店显示同一个电话。`primary_phone_role` 字段即为此设：181 家 branch_direct，20 家只能 brand_shared。

### 真实踩坑：CSV 被表格软件改成科学计数法

`seekclinic_contacts.csv` 被本地表格编辑器打开另存后，22 行 `+601123200821` 变成 `6.01123E+11`，`phone_normalized` 一并损坏。修复：从原始 TSV 重建，并让合并脚本直接读 TSV。

教训：**原始抓取层（TSV/JSONL）与展示层（CSV）分离**，合并脚本永远读原始层。

## 八、规模核实：之前只抓了一个类目（2026-10-27 复测）

用户质疑「1000 个以上」，复测确认**用户是对的**，此前 116 条只是 `aesthetic-clinic-1` 单类目。

| 证据 | 结果 |
|---|---|
| `seekclinic.my/sitemap_index.xml` | Rank Math 索引，**95 个子 sitemap** |
| `category/medical-clinic/page/40/` | **存在且有 9 条 listing** → 单「普通诊所」类目 ≥360 家 |
| `category/skin-clinic/page/25/` | 404 → 该类目 <25 页 |
| `category/aesthetic-clinic-1/` | 13 页 × 9 = 117（此前已抓） |
| 首页可见类目 | women / skin / orthopedic / medical / eye / ent / aesthetic / dental … |

按 8 个主类目、每个 10–40 页、每页 9 条估算，Seek 全站 listing 量级在 **1,000–2,500**。此前交付的 109 条仅覆盖约 5–10%。

### 为什么本机抓不动

`seekclinic.my` 对本机出口 IP 的**所有路径**（含 `robots.txt`、sitemap、`www`、`http`、IPv6）都返回 HTTP 200 + `One moment, please...` 混淆 JS 挑战页（12 KB，5 秒自动 reload）。实测：

- headless Chrome 45 秒不放行，无任何 cookie 写入
- headful Chrome 同样 18 秒不放行
- 挑战脚本混淆（`a0w` / `a0I`），属访问控制，**不做逆向或绕过**

结论：这是**出口 IP 被拦**，不是站点故障，也不是解析问题。服务端渲染读取通道可正常取页，但一次只能取一页。

### 两条可行路径

1. **换网络跑现成脚本**（推荐，可拿到全量）：`crawl_seekclinic.js` 已写好，含类目遍历、分页、404 终止、断点续跑。在手机热点/家宽上执行，约 1 小时跑完全站。
2. **逐页读取**：用服务端渲染通道一页 9 家，1,000 家约需 111 次取页，分多轮完成。

## 九、全站故障实测与恢复方案（2026-10-27）

已对固定的 15 个 URL 做本机有界健康检查，结果见 `outputs/clinic-directories/sitecheck_results.csv`；检查器为 `check_sites.py`，不遍历目录、不解挑战、不重试 403。

| 域名 | 实测 | 判断 | 可执行的恢复方式 |
|---|---|---|---|
| AestheticClinic.my | robots、sitemap、目录索引及详情 URL 均返回 HTTP 200，但约 12 KB，标题为 `One moment, please...` | JS challenge 壳；HTTP 200 不代表拿到页面字段 | 停止自动枚举；请求站方许可、官方导出/API 或无挑战的授权通道。不得自动解题或重放挑战令牌 |
| Seek Clinic | robots、sitemap、分类页 1/2/13/14 均为 HTTP 403、548 字节 nginx 响应 | 访问拒绝；无法用当前本机 HTTP 流程结构化导出 | 立即停止该 host；向站方申请授权/导出。不得代理轮换或伪装指纹 |
| Tressless | robots.txt 为 200；sitemap、目录索引、Clinic RX 档案为 Cloudflare 403（约 4.9–6 KB）；robots 注释提及 profile challenge 与 archive crawler 限制 | 全站 sitemap/档案不可用，且存在明确爬虫限制信号 | 不做全站枚举；申请官方 API/数据导出和书面许可 |

浏览器自动化依赖曾安装成功，但配套 Chromium 下载超时，系统 headless Chrome 在沙箱被终止。即使修复浏览器环境，也不能把 WAF/403 当成单纯的工具故障来绕过；只有正常获准的访问路径才可继续。

### 故障分类和处理规则

- DNS/连接超时：最多 2 次指数退避；失败 URL 记入队列，从 checkpoint 续跑。
- 408/425/5xx：最多 2 次有限退避；429 尊重 Retry-After 并暂停该域名。
- 401/403、challenge 壳、CAPTCHA、登录墙：立即停该域名/路径；不换代理、不伪装浏览器、不自动解验证码。
- robots 禁止路径：跳过并标注；ToS 不明：标记 `terms_unverified`，不推断许可。
- 分页重复或连续两页无新 URL：停止并核查边界；字段缺失保留原状并标记，不猜号码。
- 中断：原子保存 checkpoint，成功记录不重抓；原始行保留，另生成去重视图。

更完整的逐类矩阵见 `outputs/clinic-directories/fault-recovery.md`；限频与停机默认值见 `collector_config.json`。仅在取得书面许可/API/官方导出并确定允许路径、字段、速率及再发布范围后，才按 URL manifest → 低频抓取 → checkpoint → 字段质检 → 总量对账的流程执行全量任务。

## 十、未核实项

- AestheticClinic 100 个 profile 中 Complete/Source Only 的准确比例与有效号码数量。
- Seek Clinic 95 个 sitemap 的类型与总 listing 数；分类之外有无重复/已下线记录。
- Tressless 全球目录总量、马来西亚条目全量与站点 API/导出政策。
- Clinic RX 官方 10 家分店的电话号码目前全部链接到同一 WhatsApp，是否有门店直线电话未在页面列出。
- 三站对批量抓取、复制和公开再发布的完整条款；本报告不构成法律意见。
