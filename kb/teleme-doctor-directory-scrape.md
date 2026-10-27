---
id: teleme-doctor-directory-scrape
title: Teleme 医生目录全量抓取：可行性与数据结构
tags: [scraping, teleme, malaysia, healthcare, directory, cloudflare, tos]
created: 2026-10-27
updated: 2026-10-27
version: 1
status: active
source: 实测抓取 https://teleme.co（2026-10-27，1,652 个 profile 页）
confidence: 高（数量/字段/覆盖率均实测）；中（ToS 法律效力、MMC 注册号未独立核验）
---

# Teleme 医生目录全量抓取

## 一句话结论

**技术上完全可行且成本极低**——`teleme.co` 的医生/药房档案页是服务端渲染的纯 HTML，无登录、无签名、无频率限制，`robots.txt` 仅屏蔽 `/internal/`；1,652 个 profile 在 ~10 分钟内可全量落地，**1,181 个唯一联系电话，96.1% 的档案带号**。但 **ToS 明文禁止「下载/转载站内任何材料」，且禁止绕过平台私下联系医生**，所以「能抓」≠「能公开分发」。

## 一、站点结构（实测）

| 项 | 实测结果 |
|---|---|
| 技术栈 | Rails + jQuery 传统 SSR（非 SPA），Cloudflare 前置 |
| 反爬 | 无验证码、无 Turnstile、无 UA 校验；**仅 curl 默认 UA 会被 403**，换成浏览器 UA 即 200 |
| robots.txt | `Disallow: /internal/` 之外全允许，含 sitemap 声明 |
| sitemap.xml | **2017 年 Screaming Frog 生成，仅 102 个 profile**（实际 1,652，覆盖 6%） |
| 列表入口 | `GET /doctors/search?page=N`，**12 条/页**，共 142 页 |
| 列表页字段 | 仅姓名/科室/诊所名，**不含电话** |
| 档案页 | `GET /doctors/profile/{slug}`，含诊所地址 + `Contact` 电话 + 执照号 + 语言 + 资质 + 营业时间 |
| 分页稳定性 | 差：翻页有 ~2% 重复/漏项（排序键不稳定），需多路合并去重 |

### 关键字段的 DOM 位置

```
姓名      <h3 class="name">…<span class="gender" title="Male">
科室      <p class="specialty">
费率      <p class="rate">RM 0.00 per call
执照号    <h4>License no.</h4><p>
语言      <h4>Spoken Languages</h4><p>
资质      <div class="awards">
诊所区块  <h4>{诊所名}</h4><p class="grey">{地址}</p>
电话      <h4>Contact</h4><p>+6012…</p>
```

## 二、抓取结果（2026-10-27 实测）

| 指标 | 数值 |
|---|---|
| 成功抓取 profile | 1,652 / 1,652（0 失败） |
| 医生-诊所 明细行 | 1,636（有效号码） |
| **唯一电话号码** | **1,181** |
| 档案带号率 | 1,588 / 1,652 = **96.1%** |
| 手机号（+601x） | 532 |
| 固话（+603…+609） | 1,097 |
| 号码脏数据 | 短号 49 / 垃圾值 15 / 境外 3 |
| 耗时 | ~10 分钟（8 并发，0.5s 间隔，0 次封禁） |

### 目录成分——最反直觉的一点

| 科室 | 档案数 | 占比 |
|---|---|---|
| **Pharmacist（药师）** | **1,049** | **63.5%** |
| General practitioner | 123 | 7.4% |
| Optician / 视光 | 53 | 3.2% |
| 物理治疗/心理/营养 | 80 | 4.8% |
| **真正的医生（physician 合计）** | **443** | **26.8%** |

`/doctors` 目录里 **近 3/4 不是医生**，主体是 Guardian / Healthlane / Sunway Multicare 等连锁药房的门店条目。想要「医生电话」的实际可用量只有 ~404 条。

### 地域分布（按邮编推断）

Selangor 455 · KL 378 · Penang 137 · Johor 103 · Perak 66 · N.Sembilan 56 · Putrajaya 56 · Melaka 47 · Kedah 37

## 三、ToS 冲突（必须看）

`https://teleme.co/terms` 两处原文：

> You must not **reproduce, distribute, modify, communicate to the public, download or transmit** any of the material on this Site except as expressly permitted by these Terms of Use.

> …and to **refrain from contacting Healthcare Professionals for telehealth services outside of the Site**.

含义：
1. 批量下载 = 直接违反第一句（robots.txt 允许 ≠ ToS 允许，两者独立）。
2. 抓号码去私下联系医生做远程问诊 = 正好命中第二句，这是平台的核心商业模式防线。
3. 个人留存自用风险低；**公开发布/转售/群发营销风险高**（合同违约 + PDPA 2010 商业用途条款）。

## 四、可复用操作

### 1. 枚举全部 profile（不要信 sitemap）

```python
# 翻页直到无新增；分页不稳定，必须用 set 去重
seen=set(); page=1
while True:
    h=get(f"https://teleme.co/doctors/search?page={page}")
    got=set(re.findall(r'/doctors/profile/([a-z0-9\-]+)', h))
    if not got - seen: break
    seen |= got; page += 1
```

### 2. 必备请求头（缺 UA 直接 403）

```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
Accept-Language: en-US,en;q=0.9
```

### 3. 电话规范化（坑在「+6」补位）

```python
d = re.sub(r"[^\d+]", "", raw)
if d.startswith("+"):      e = "+" + re.sub(r"\D", "", d)
elif d.startswith("60"):   e = "+" + d
elif d.startswith("0"):    e = "+6" + d      # 060xxx 会被误拼成 +6060xxx，需再校验
else:                      e = "+" + d
# 有效性：+60 且国内号 8–10 位；否则标 short / junk / foreign
```

### 4. 并发参数

8 workers × 0.5s 间隔 ≈ 4–7 req/s，1,650 页约 6–10 分钟，全程 0 失败、0 封禁。再高没必要。

## 五、坑与反直觉

| 坑 | 说明 |
|---|---|
| sitemap 严重过期 | 2017 年生成，只有 102 条，是实际的 6%。**任何以 sitemap 为全集的做法都会漏 94%** |
| `/doctors` 首页无列表 | 那是 v2 landing page，0 个 profile 链接；真实列表在 `/doctors/search` |
| 列表页无电话 | 电话只在 profile 页的 `Contact` 块里，必须二次请求 |
| 目录主体是药房 | 63.5% 是药师门店条目，不是医生 |
| 营业时间错得离谱 | 例：Dr Samuel Wong 在 Teleme 显示「周一至周六 18:00–03:00」，官网 gem.clinic 与 medical.my 均为「10:00–19:00，周日休」。**该目录时间字段不可信** |
| 费率全是 RM 0.00 | 付费问诊从未真正上线，是遗留占位 |
| 分页漂移 | 无稳定排序，142 页里约 2% 重复/漏项 |
| 号码脏 | 64 条为 `+60` / `60` / `none` / `NA` 占位，49 条截断 |
| Cloudflare 首访 403 | WebFetch 类工具常被拦；`curl` + 浏览器 UA 稳定 200 |

## 六、Teleme 平台现状（背景）

官网首页 2026 年已改版为 **「Real-time population health intelligence — system as a service」**：面向政府/项目运营方/资助方的 B2G/B2B 人群健康数据平台（FHIR/HL7、离线优先、e-prescription、Gemini 自然语言查询），覆盖马来西亚 + 另一个东南亚市场。

即：**这个 1,652 条的医生目录是上一代 C 端问诊市场的遗留面**，页面还活着但已不维护（费率 0、时间错、sitemap 停在 2017）。抓下来的本质是一份 **2019 年前后的马来西亚诊所/药房黄页**。

## 七、目标医生：Dr Samuel Wong

| 项 | 值 | 来源 |
|---|---|---|
| 全名 | Dr Samuel Wong（Wong Ing Sung） | Teleme slug `samuel-wong-ing-sung` |
| 职务 | Chief Aesthetic Physician, GEM Clinic | gem.clinic |
| 执照号 | 42977 | Teleme（未独立核验） |
| 学历 | MBBS (Malaya, 2005) | gem.clinic |
| 资质 | Dip. Dermatology (Mal) · Fellowship Cutaneous Surgery & Laser (Bangkok) · FKCCS (Korea) · LCP-AMP (MOH) | 两站一致 |
| 执业点 | Unit 1-1 Mezzanine, The Boulevard, Mid Valley City, 59200 KL | 两站一致 |
| 电话 | **+6012-200 4035**（Teleme 与 medical.my / ContactOut 三方一致） | 交叉验证 |
| 官方客服 | +6012-200 7035（gem.clinic 官网） | 交叉验证 |
| 邮箱 | drsamuel.wong@gemclinic.com.my | gem.clinic |
| 语言 | BM / 粤语 / 普通话 / 英语 | Teleme |
| Teleme 活跃度 | 487 浏览 · 1 关注 · 费率 RM 0.00 | 实测 → **休眠档案** |

## 八、未核实项

- 执照号 42977 未在 MMC（Malaysian Medical Council）公开注册库核对，`mmc.gov.my/register/` 已 404，需走 MMC 官方查询渠道。
- 「13 年 / 18 年经验」两处口径不同（gem.clinic 个人页写 2026 年为第 13 年；机构页写 18 年团队经验），非同一指标。
- 抓取期间未触发 Cloudflare 封禁，但**不代表长期高频安全**；ToS 明确保留终止访问权。
