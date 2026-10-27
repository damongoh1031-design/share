---
id: malaysia-clinic-directory-sources
title: 马来西亚医美诊所目录站：联系方式可采集性对比
tags: [scraping, malaysia, healthcare, aesthetic-clinic, cloudflare, waf, directory]
created: 2026-10-27
updated: 2026-10-27
version: 4
status: active
source: 实测 https://www.aestheticclinic.my · https://seekclinic.my · https://tressless.com（2026-10-27）
confidence: 高（页面字段与访问限制实测）；中（目录规模推断）
---

# 马来西亚医美诊所目录站：联系方式可采集性对比

## 一句话结论

三站均有公开业务电话，但访问特性不同：Seek Clinic 类别列表页每页示例 9 条，列表内容直接有 `tel:` 号码；AestheticClinic.my 提供 100 条 premises 记录（部分 Source Only 无电话）；Tressless 的 Clinic RX 页展示一个 clinic 级电话和 5 个分店。普通脚本请求遇 JS challenge / nginx 403 / Cloudflare 403；**不应绕过这些访问门槛进行全量采集**。已验证并导出 3 条样本。

## 一、页面和字段（实测）

| 站点 / 页面 | 机构名 | 业务电话 | 其他字段 | 访问限制 |
|---|---|---|---|---|
| aestheticclinic.my · Clinic RX Dataran Cheras | CLINIC RX | +60102103921；+60143288758 | CKAPS item 5476、地址、营业时间、关联医生 Chok Jun Hoong APC/LCP 核验 | WebFetch 可读；curl 是 JS challenge；robots 只禁 `/wp-admin/` |
| seekclinic.my · MZ Clinic | MZ Clinic (Aesthetic & Wellness) 医美皮肤诊所 | +60129115975 | 地址、网站、服务、时间、评分 | WebFetch 可读；curl nginx 403；补常见导航头仍 403 |
| tressless.com · Clinic RX | Clinic RX | +60102103921 | 5 个马来西亚分店、语言、网站；没有具名执业者 | WebFetch 可读；curl Cloudflare 403；robots 注释明确提及 profile challenge 和 archive WAF |

全部号码来自诊所公开业务联系字段，并非私人号码。

## 二、规模估算（非全量核验）

| 站点 | 公开页面量级 | 结构 | 可信度 |
|---|---:|---|---|
| AestheticClinic.my | 100 条 premises 记录 | 单页索引 + 详情页 | 站点自述 100 条 |
| Seek Clinic | 约 100–150 家 | 9 条/页；page 12 有内容、page 18 和 25 返回 404 | 区间推断，精确页数未核验 |
| Tressless | 全球数千条 | 全球目录，无总量；详情页 clinic 级联系电话 | 粗略观察，未穷举 |

## 三、为什么没有全量导出

- `aestheticclinic.my` 普通 HTTP 返回 `<title>One moment, please...</title>` 挑战页，虽状态码为 200；必须执行 JS 才可能获得内容。
- `seekclinic.my` 普通 HTTP 对目标详情页、分类页和 robots.txt 均返回 nginx 403；不是解析器问题。
- `tressless.com` 返回 Cloudflare `Attention Required`。其 robots 注释特别指出档案页 challenge-gated，并防止 archive crawler。
- Playwright 1.64.1 已装在隔离 Node workspace；配套 Chromium 下载持续超时，系统 Chrome headless 在沙箱以 SIGTERM 结束。
- 没有尝试代理轮换、challenge token、指纹伪装或其他绕过方式。**浏览器自动化能运行也不代表网站授权全量复制。**
- 适当路径：向网站申请书面许可、官方导出或 API；获得许可后再按低频、可审计方式运行。

## 四、采集成本结构（仅作为获准后的规划）

| 站点 | 字段位置 | 许可后预计请求量 | 前置过滤 |
|---|---|---:|---|
| Seek Clinic | 列表中含 `tel:`、名称、地址、详情 URL | 每类目约 9 家/页；约 12–17 页（估算） | 类目需定义；跨类目 URL/号码去重 |
| AestheticClinic.my | 详情页 `Phone or contact route`，可能多个号或非电话联系路径 | 约 100 个详情页 | 先分 `Complete` / `Source Only`；后者无联系方式 |
| Tressless | Clinic 详情页有 clinic 级电话；分店页通常无独立号码 | 逐 clinic 页访问，量级未统计 | 只限 hair-loss 专科和国家范围；先取得授权 |

## 五、常见陷阱与技巧

| 观察 | 处理 |
|---|---|
| HTTP 200 可能是 JS challenge 壳 | 检查页面 title、正文和目标字段；不要只看状态码 |
| robots 宽松不等于 ToS 授权 | robots、WAF、服务条款、数据库复用权分别核对 |
| 站点返回 403 | 停止脚本访问；不要换代理或伪装指纹继续请求 |
| 记录数不等于号码数 | Complete 有联系方式，Source Only 仅有 CKAPS 名称/地址 |
| 诊所连锁多分店共用号码 | 保留 branch/premises ID 和地址，同时另建唯一号码表 |
| 联系号码是旧数据 | 保留来源 URL、核验日；用诊所官方渠道交叉验证 |
| 营业时间会自相矛盾 | MZ Clinic 周二同时列 00–07 与 10–19；标注冲突，不自行判定 |
| Tressless clinic 级联系 ≠ 每分店专线 | 不把品牌号复制成每家分店的独立号码 |
| WebFetch 可读取 ≠ 可无限量自动化 | 阅读能力只支持当前访问；不代表平台授权枚举全站或镜像数据 |

## 六、已提取样本

本地 `outputs/clinic-directories/sample_extracted_contacts.csv` 有 3 行：

1. Clinic RX Dataran Cheras — +60102103921 / +60143288758
2. MZ Clinic — +60129115975
3. Clinic RX（Tressless clinic 级）— +60102103921

## 七、归档 GitHub 的可复用技巧

- 同主题更新现有 KB，不创建日期后缀文件；递增 `version` 并维护 `kb/README.md`。
- `github-sync` 目录模式是镜像覆盖，可能删除远端独有文件；共享 `kb/` 用单文件同步。
- 先 fetch/reset 远端最新版，再核对 diff/dry-run；推完用 `git ls-tree` 或 GitHub API 核验。
- public 仓库中的业务电话任何人可见；公开前确认仓库可见性和来源条款。用户确认公开不等于来源网站授权。
- 完整 Teleme 数据已在 `teleme-directory/` 公开：1,181 唯一号码、1,636 行明细、1,652 JSONL 档案；commit `1845de5`。用户于 2026-10-27 明确确认上传完整 CSV/JSONL。

## 八、未核实项

- Seek Clinic 精确分页数、跨类目去重后的全站诊所总量。
- AestheticClinic.my 100 条中 Complete 与 Source Only 的实际数量比例。
- Tressless 马来西亚条目总量及分店专属联系电话。
- 三站 ToS 对自动化访问和批量复用数据的完整规定；Seek Clinic 当前 Terms 页面是模板占位文本。
