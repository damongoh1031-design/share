---
id: teleme-doctor-directory-scrape
title: Teleme 医生目录全量抓取：可行性与数据结构
tags: [scraping, teleme, malaysia, healthcare, directory, cloudflare, tos]
created: 2026-10-27
updated: 2026-10-27
version: 3
status: active
source: 实测抓取 https://teleme.co（2026-10-27，1,652 个 profile 页）
confidence: 高（数量/字段/覆盖率均实测）；中（ToS 法律效力、MMC 注册号未独立核验）
---

# Teleme 医生目录全量抓取

## 一句话结论

技术上完全可行且成本极低——Teleme profile 是 SSR HTML，`robots.txt` 仅屏蔽 `/internal/`；实测 1,652 页约 10 分钟可抓完，**1,181 个唯一公开诊所/药房电话**，96.1% 档案带电话。但 Teleme ToS 明文禁止下载/转载站内材料，并禁止绕过平台联系医生做远程问诊；技术可抓不等于获授权复用。

## 一、站点结构（实测）

| 项 | 结果 |
|---|---|
| 技术栈 | Rails + jQuery SSR，非 SPA，前有 Cloudflare |
| 反爬 | curl 默认 UA 403；浏览器 UA 200；无需验证码 |
| robots.txt | `Disallow: /internal/`，Sitemap 指向 `/sitemap.xml` |
| sitemap.xml | 2017 年生成，只有 102 个 profile（实际约 6%） |
| 列表 | `GET /doctors/search?page=N`，12 条/页，共 142 页 |
| 详情 | `GET /doctors/profile/{slug}`，含诊所、地址、Contact 电话、执照号、语言、资质、时间 |
| 分页 | 排序不稳定；多页去重后枚举 1,652 个 profile slug |

### DOM 字段

```
姓名      <h3 class="name">
科室      <p class="specialty">
执照号    <h4>License no.</h4><p>
语言      <h4>Spoken Languages</h4><p>
资质      <div class="awards">
诊所地址  <h4>{诊所名}</h4><p class="grey">{地址}</p>
电话      <h4>Contact</h4><p>+6012…</p>
```

## 二、实测数据统计（2026-10-27）

| 指标 | 数量 |
|---|---:|
| 成功档案 | 1,652 / 1,652（0 失败） |
| 医生-诊所有效号码行 | 1,636 |
| 唯一电话号码 | 1,181 |
| 档案带号率 | 1,588 / 1,652 = 96.1% |
| 手机（+601x） | 532 |
| 固话（+603…+609） | 1,097 |
| 短号 / 垃圾值 / 境外值 | 49 / 15 / 3 |

**目录主体不是医生：** Pharmacist 1,049 条（63.5%），真正医生 443 条（26.8%）。做医疗从业者分析时先按 Specialty 分类，不能把 `/doctors` 当作全是医生。

## 三、ToS 与使用限制

`https://teleme.co/terms` 明确写明不得 “reproduce, distribute, modify, communicate to the public, download or transmit” 站内材料；并要求不绕过平台联系医疗人员进行远程问诊。

- robots.txt 允许公开路径，不代表 ToS 允许批量下载；两者含义不同。
- 公开诊所电话不是私人号码，但大规模复制/再发布仍可能受 ToS、数据库权利和隐私规则约束。
- 已公开到 GitHub 的 Teleme 文件位于 `teleme-directory/`（1,181 个唯一电话、1,636 行 CSV、1,652 行 JSONL；commit `1845de5`）。仓库是 public，任何人可访问或再传播。用户于 2026-10-27 明确确认公开上传含电话及完整 CSV/JSONL；这不等于来源网站授权。

## 四、复用抓取方法（仅限获准来源）

### 1. 枚举列表

不要盲信过期 sitemap；优先检查站点列表分页，翻页直到没有新增 slug，并用集合去重：

```python
seen = set()
page = 1
while True:
    html = get(f"https://example.test/directory?page={page}")
    current = set(re.findall(r"/profile/([a-z0-9-]+)", html))
    if not current - seen:
        break
    seen.update(current)
    page += 1
```

先记录 robots、ToS、站点公开 API/导出方式；若遇 403、验证码或明确挑战页，停止自动化并向站点申请授权，不要伪造浏览器指纹或绕过 WAF。

### 2. 浏览器 UA（仅对允许的公开访问）

```text
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
Accept-Language: en-US,en;q=0.9
```

UA 只用于正常客户端兼容性测试，不是访问许可，也不能用来规避 CAPTCHA/WAF。

### 3. 电话规范化与质检

```python
d = re.sub(r"[^\d+]", "", raw)
if d.startswith("+"):
    e = "+" + re.sub(r"\D", "", d)
elif d.startswith("60"):
    e = "+" + d
elif d.startswith("0"):
    e = "+6" + d
else:
    e = "+" + d
```

规范化后必须验证国家码、长度和可疑占位值；不要把 `+60`、`none`、`NA` 或截断号码计入有效电话。另存原始值与规范化值，避免丢失证据。

### 4. 运行参数

本次实测 8 workers + 0.5s 间隔；约 6–10 分钟，0 失败。只对明确允许且规模适当的目录使用。遇到 403、429、验证码或站点不欢迎信号，停止，不加大并发或切代理。

## 五、目录研究通用技巧与常见坑

| 技巧/坑 | 做法 |
|---|---|
| sitemap 可能陈旧 | 和列表页分页总量交叉验证，不要直接当全集 |
| 首页可能只是 landing page | 找站内分类页、搜索页、robots/Sitemap 声明，不靠首页推断 |
| 电话常只在详情页 | 先看列表是否有 `tel:`；若无，估算详情页请求量与授权范围 |
| 分页排序漂移 | 每页去重并记录 slug；翻页到连续无新增后再停止 |
| HTTP 200 可能是挑战壳 | 检查 `<title>`、正文、关键字段，不能只看状态码 |
| 号码需来源溯源 | 每条记录保留来源 URL、检查日期、原始电话、标准化电话 |
| 目录混有非医生 | 按职业/专业标签分类，区分 physician、pharmacist、optician 等 |
| 营业时间可能陈旧 | 与诊所官网/官方社媒交叉核对，标注冲突，不把单一目录当事实 |
| 号码重复不一定错误 | 连锁门店可能共用总机；同时保留 branch 行和唯一号码视图 |

## 六、三站浏览器自动化复盘（2026-10-27）

对 aestheticclinic.my、seekclinic.my、tressless.com 测试：普通 curl 分别遇到 JS challenge、nginx 403、Cloudflare 403。WebFetch 能读取具体公开页面，但不等于能或应当绕过访问控制批量遍历。

- 隔离 Node 22.22.2 中安装 Playwright 1.64.1 成功。
- 配套 Chromium 下载多次超时；系统 Chrome headless 在沙箱里被 SIGTERM。
- 未尝试代理轮换、challenge token、指纹伪装或其他 WAF 绕过。
- 如需全量研究，先拿书面许可或官方导出/API。工具恢复只解决浏览器运行，不改变许可边界。
- 这三站公开样本共 3 行，位于 `outputs/clinic-directories/sample_extracted_contacts.csv`；数据集没有被全量抓取。

## 七、GitHub 归档技巧（可复用）

1. 同主题 KB 更新原文件，递增 frontmatter `version`，同步更新索引，不创建日期碎片文件。
2. 推共享目录前先 fetch/reset 到远端最新版，确认目标树和本地差异；共享 `kb/` 使用**单文件同步**，避免镜像误删别人的文档。
3. `github-sync` 的目录模式是镜像覆盖，并可能不递归子目录。大目录改用清晰的目标文件映射，检查 dry-run 列表。
4. 公开仓库会暴露所有电话、邮箱、脚本和原始档案；核对数据敏感度与站点条款后再发布。
5. 同步后用 `git ls-tree`、远端 API 或文件链接核验，而不只依赖 push 输出。
6. 提交前扫描密钥只是最低限度；还要人工检查个人数据、条款、来源和目标可见性。

## 八、目标医生样本：Dr Samuel Wong

| 项 | 值 | 来源/置信度 |
|---|---|---|
| 职务 | Chief Aesthetic Physician, GEM Clinic | GEM Clinic 官网 |
| 电话 | +6012-200 4035 | Teleme + medical.my + ContactOut 交叉出现 |
| 官方客服 | +6012-200 7035 | GEM Clinic 官网 |
| 地址 | Unit 1-1 Mezzanine, The Boulevard, Mid Valley City, 59200 KL | Teleme/GEM 官网 |
| 学历 | MBBS (Malaya, 2005) | GEM Clinic 官网 |
| 执照号 | 42977 | Teleme 标注；MMC 未独立核验 |

## 九、未核实项

- 执照号 42977 未通过 MMC 官方注册查询核验；`mmc.gov.my/register/` 当前路径 404。
- Teleme 页面营业时间、问诊费率等可能陈旧，使用前应向诊所确认。
- 站点 ToS 的法律适用解释未做法律意见；需要大规模再利用时，应向平台取得授权并咨询适用规则。
