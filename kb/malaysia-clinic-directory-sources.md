---
id: malaysia-clinic-directory-sources
title: 马来西亚医美诊所目录站：联系方式可采集性对比
tags: [scraping, malaysia, healthcare, aesthetic-clinic, cloudflare, waf, directory]
created: 2026-10-27
updated: 2026-10-27
version: 1
status: active
source: 实测 https://www.aestheticclinic.my · https://seekclinic.my · https://tressless.com（2026-10-27）
confidence: 高（反爬表现、号码位置、分页边界均实测）；中（seekclinic 总页数为区间推断；tressless 总量未穷举）
---

# 马来西亚医美诊所目录站：联系方式可采集性对比

## 一句话结论

**三家都有联系电话，但全部需要「真浏览器」才能拿到**——纯 `curl` 一律被挡（两家 Cloudflare 挑战、一家 nginx 403）。性价比排序：`seekclinic.my`（号码直接在列表页）> `aestheticclinic.my`（字段最全但仅部分记录有号）> `tressless.com`（全球分散、只有 clinic 级单号、且站点明文反对抓取）。**这三家与 Teleme 完全不是一个难度层级**：Teleme 是裸奔的 SSR，这三家都有 WAF。

## 一、反爬与可达性（实测）

| 站点 | 纯 curl | robots.txt | 拦截类型 | 绕过方式 |
|---|---|---|---|---|
| aestheticclinic.my | **挑战页**（`<title>One moment, please...`，5s 后 JS 自动 reload） | 宽松：仅 `Disallow: /wp-admin/` | 全站 JS challenge（连 `/robots.txt`、`/wp-sitemap.xml` 都返回挑战页） | 执行 JS 的渲染器 |
| seekclinic.my | **403 Forbidden**（nginx，168 字节空壳） | 不可读（同样 403） | TLS/指纹级 WAF，补全 `Accept`/`Sec-Fetch-*`/HTTP2 仍 403 | 真实浏览器指纹 |
| tressless.com | **403**（Cloudflare `Attention Required`） | 全站 `Allow: /`，但**明文注释说明 profile 页对所有非浏览器挑战门禁**，并禁 `ia_archiver`/`archive.org_bot` | Cloudflare WAF + 挑战 | 渲染器（且违背站点明示意图） |

> 关键对比：Teleme 只需换浏览器 UA 即 200。这三家换 UA 无效，必须过 JS 挑战。

## 二、号码在哪一层（决定采集成本）

| 站点 | 号码位置 | 每页请求数 | 附加字段 |
|---|---|---|---|
| **seekclinic.my** | **列表页直接内嵌 `<a href="tel:+60...">`** | **1 请求 / 9 家** | 名称、完整地址、电话、评分、分类 |
| aestheticclinic.my | 详情页 `Phone or contact route`（可 1–2 个号） | 1 请求 / 1 家 | 地址、营业时间、CKAPS premises ID、坐标、关联医生 MMC APC 链接、核验日期 |
| tressless.com | 详情页 clinic 级 **1 个号**；分店页无号 | 1 请求 / 1 家 | 5 个分店地址、语言、网站 |

**seekclinic 是唯一「列表页即含号」的站**——这是它性价比最高的根本原因。

## 三、规模

| 站点 | 量级 | 依据 |
|---|---|---|
| aestheticclinic.my | **100 条** premises 记录 | `/clinics/` 自述 "100 published premises records"，全部链接在单页内 |
| seekclinic.my | **约 130 家**（aesthetic-clinic 分类） | 9 条/页；`page/12` 有内容、`page/18` 与 `page/25` 均 404 → 13–17 页 |
| tressless.com | **数千**（全球） | 覆盖 US / BR / IN / CA / MY 等，列表无总数 |

## 四、号码覆盖率——最容易踩的坑

`aestheticclinic.my` 的 100 条**不是都有电话**，分两种状态：

| 状态 | 字段 | 有无电话 |
|---|---|---|
| **Complete**（如 Clinic RX Dataran Cheras） | 地址 + 电话 + 营业时间 + 坐标 + 关联医生 | **有**（实测 +60102103921 / +60143288758） |
| **Source Only**（如 Clinic RX Penang 3723） | 仅 CKAPS 法定名称 + 地址 | **无**（明写 "Contact details, coordinates, doctors, hours and treatments are not yet independently verified"） |

所以「100 条记录」≠「100 个号码」。抓之前必须先按 `Profile completeness` 字段过滤，否则会拿到大量空号记录。

`tressless.com` 同理：一家 5 个分店只给 1 个 clinic 级号码，分店页无独立号码。

## 五、可复用操作

### 1. 判断站点是否可用纯 HTTP 采集（30 秒判定）

```bash
curl -sS -L --max-time 20 -A "Mozilla/5.0 ... Chrome/131.0.0.0" -o /dev/null \
  -w "%{http_code} %{size_download}\n" "https://target/robots.txt"
```

- `200` + 正常文本 → 可纯 HTTP
- `200` + `<title>One moment, please...` → JS challenge
- `403` + 极小体积（<600B）→ WAF 直接拒
- `403` + Cloudflare 页 → Cloudflare WAF

### 2. 三站的枚举路径

```
seekclinic.my   /category/aesthetic-clinic-1/page/N/      9 条/页，N=1..~17
aestheticclinic.my  /clinics/  （单页含全部 100 条链接）
                    /clinics/{slug}-{postcode}-{ckapsId}/  详情
tressless.com   /hair-loss-specialists/clinics             分页列表
                /hair-loss-specialists/clinics/{cc}/{state}/{city}/{slug}
```

### 3. 号码提取（三站通用）

```python
# 最稳：先取 tel: 链接，再退回正则
phones = re.findall(r'href="tel:([^"]+)"', html)
if not phones:
    phones = re.findall(r'\+60\d{8,10}', re.sub(r'[\s\-]', '', html))
```

`seekclinic.my` 与 `tressless.com` 都用标准 `tel:` 链接，提取零歧义。

### 4. 无浏览器环境下的退路

本机 `chrome --headless=new --dump-dom` 在当前沙箱会被 SIGTERM，不可用。可行路径只有两条：
1. 服务端渲染型抓取工具（本会话中 WebFetch 可过三站全部挑战，实测 3/3 成功）。
2. 本机 Playwright/agent-browser + 关闭沙箱限制。

## 六、坑与反直觉

| 坑 | 说明 |
|---|---|
| robots.txt 宽松 ≠ 可抓 | aestheticclinic.my 的 robots 只禁 `wp-admin`，但全站挂 JS 挑战；`seekclinic.my` 的 robots 本身都 403 读不到。**robots 与 WAF 是两套独立机制** |
| tressless 明文反对抓取 | robots.txt 注释原文：profile 页对所有非浏览器「challenge-gated」，并说 WAF 规则会兜底封禁 archive 爬虫。这是**明确表达的不欢迎**，绕过属于主动规避 |
| 「记录数」≠「号码数」 | aestheticclinic.my 100 条里 Source Only 的记录完全没有联系方式 |
| 同名连锁多分店 | Clinic RX 在 aestheticclinic 有 6+ 个分店记录，同一品牌不同 premises ID，必须按 `{postcode}-{CKAPS id}` 区分 |
| 号码可能是「联系路径」而非号码 | aestheticclinic 的字段名叫 "Phone **or contact route**"，个别记录填的是 WhatsApp 或表单链接 |
| seekclinic 营业时间自相矛盾 | MZ Clinic 列表页写 "Tuesday: 12 to 7 AM, 10 AM to 7 PM"（两个时间段叠在一起），**时间字段不可直接使用** |
| 全球站不适合做本地黄页 | tressless 是 hair-loss 专科全球目录，马来西亚只有零星几条，且无分店号 |

## 七、合规提示

- `seekclinic.my` / `aestheticclinic.my`：robots 未禁止，但 WAF 存在本身是技术性意愿表达；个人少量查询可，规模化采集需自行承担风险。
- `tressless.com`：**明确反对**。若要采集，建议先向其申请，而非绕过 WAF。
- 所有号码均为诊所对外公布的接诊电话，非个人私人号码；不得用于群发营销。

## 八、未核实项

- `seekclinic.my` 精确总页数（实测 `page/12` 有、`page/18` 无，落在 13–17 页区间）。
- `seekclinic.my` 其他分类（skin-treatment / hifu / botox 等）的条目数与去重后的诊所总数。
- `tressless.com` 马来西亚条目总数未穷举。
- `aestheticclinic.my` 100 条中 Complete / Source Only 的确切比例未逐条统计。
- 三站的 ToS 正文未逐条阅读（`seekclinic.my/terms` 同样受 403 保护，需渲染器才能读取）。
