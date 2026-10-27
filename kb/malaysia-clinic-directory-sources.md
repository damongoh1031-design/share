---
id: malaysia-clinic-directory-sources
title: 马来西亚医美诊所目录站：联系方式可采集性对比
tags: [scraping, malaysia, healthcare, aesthetic-clinic, cloudflare, waf, directory]
created: 2026-10-27
updated: 2026-10-27
version: 2
status: active
source: 实测 https://www.aestheticclinic.my · https://seekclinic.my · https://tressless.com（2026-10-27）
confidence: 高（已访问页面字段、公开号码与浏览器自动化限制）；中（目录量级推断）
---

# 马来西亚医美诊所目录站：联系方式可采集性对比

## 一句话结论

三站均公布诊所联系方式，但当前环境下**仅能通过网页渲染获取少量页面内容，不能安全/合规地全量绕过其 WAF 做批量 dump**。Playwright JS 包已装入隔离 Node 环境，但浏览器下载源超时，且已有 headless Chrome 在沙箱中被 SIGTERM。更重要的是，tressless 明确说明其档案页对非浏览器访问加挑战并主动阻挡 archive crawler；不应规避这些访问控制。可确认的 3 个示例联系方式已导出。

## 一、三个目标页面的公开字段

| 站点 / 目标 | 姓名 / 机构 | 电话 | 其他字段 | 当前可访问性 |
|---|---|---|---|---|
| aestheticclinic.my · Clinic RX Dataran Cheras | CLINIC RX（Dataran Cheras） | +60102103921；+60143288758 | CKAPS item 5476；地址；营业时间；关联医生 Chok Jun Hoong（APC 分店匹配、LCP 已检查） | WebFetch 可读；curl 返回 JS challenge；robots 仅禁 `/wp-admin/` |
| seekclinic.my · MZ Clinic | MZ Clinic (Aesthetic & Wellness) 医美皮肤诊所 | +60129115975 | 地址、网站、服务、营业时间、评分 | WebFetch 可读；curl 403 nginx，即使补浏览器常见请求头仍 403 |
| tressless.com · Clinic RX | Clinic RX | +60102103921 | 5 个马来西亚分店地址；语言；官网链接；无具名执业者 | WebFetch 可读；curl Cloudflare 403；robots 注释说明 profile challenge 与 archive WAF 拦截意图 |

号码均为诊所公开业务联系号码，不是私人号码。

## 二、自动化安装/访问测试（2026-10-27）

| 项目 | 结果 |
|---|---|
| 隔离 Node.js | 22.22.2 |
| Playwright npm 包 | 已安装到 `C:/Users/Admin/.workbuddy-ai/binaries/node/workspace`，版本 1.64.1 |
| 配套 Chromium | 下载失败：`cdn.playwright.dev` 多次连接超时；当前缓存只有旧版 Chromium 1228，与该 Playwright 版本不匹配 |
| 系统 Chrome headless | 本地 `--dump-dom` 在当前沙箱执行时被 SIGTERM；未成功渲染 |
| 反爬挑战处理 | 未尝试规避 Cloudflare、nginx WAF、CAPTCHA 或访问限制 |
| 全量抓取 | **未运行**。仅导出 3 条页面级样本，避免将少量公开查询扩展为未经许可的批量复制 |

## 三、量级估算与可采集路径

| 站点 | 估算量级 | 页面数据形态 | 预期成本 |
|---|---:|---|---|
| aestheticclinic.my | 100 条 premises 记录（站点自述） | `/clinics/` 索引页列出记录；联系方式需逐个详情页读取；`Source Only` 条目没有号码 | 若有许可并有正常浏览器会话，约 100 个详情页请求 |
| seekclinic.my | 约 100–150 条（推断） | 分类页每页 9 条，号码直接出现在列表页 `tel:` 链接 | 若站点允许，约 12–17 个分类页请求；当前 WAF 拒绝脚本请求 |
| tressless.com | 全球数千（站点列表未显示总数） | clinic 详情页可见 clinic 级号码；分店页不一定有独立号码 | 全球目录不适合作为马来西亚黄页；站点明确阻挡归档抓取 |

以上估算不等于已核验总量。Seek Clinic 页数边界仅抽查了第 12、18、25 页；AestheticClinic 的 100 条中 Complete 与 Source Only 的具体比例尚未统计。

## 四、访问控制与边界

- `robots.txt` 只是爬虫声明，不等于对大规模复制的授权。
- `aestheticclinic.my` 的 robots 相对宽松，但实际全站有 JS challenge；challenge 本身不是建议去对抗的目标。
- `seekclinic.my` 返回 nginx 403；不要更换代理、伪装指纹或做绕过。
- `tressless.com` robots 注释明确提到 profile challenge 与 archive crawler 的 WAF 阻挡意图；全站批量复制前应取得书面许可。
- 三站 ToS 本轮未能逐一完整核读；规模化采集前应检查条款并向网站确认许可。
- 用途限定为个人查找公开诊所业务联系方式；不要用于群发营销或对公众再发布未经许可的目录副本。

## 五、坑与反直觉

| 坑 | 说明 |
|---|---|
| HTTP 200 不代表拿到页面 | aestheticclinic 的 HTTP 200 内容是 `One moment, please...` 自动重载挑战壳 |
| robots 允许不等于可以全量复制 | WAF / 服务条款 / 数据库权利是独立因素 |
| 记录数不等于号码数 | AestheticClinic 的 Source Only 记录只有 CKAPS 名称、地址，无电话 |
| 连锁分店不能合并成单一号码 | Clinic RX 多个地址都重复一个品牌号码；仍需保留分店层级 |
| 联系号码可能过时 | 目录数据需与诊所官网或官方联系页核验 |
| 营业时间有异常 | Seek Clinic 的 MZ Clinic 周二同时列 `12 to 7 AM` 和 `10 AM to 7 PM`，需向诊所核实 |
| 浏览器自动化被阻不代表可以绕过 | 浏览器只用于正常页面渲染；若触发挑战或拒绝访问，应停止并寻求许可 |

## 六、可复用操作

### 1. 先做单页可达性检查

```bash
curl -sS -L --max-time 20 \
  -A "Mozilla/5.0 ... Chrome/131.0.0.0" \
  -o page.html -w "%{http_code} %{size_download} %{content_type}\n" \
  "https://target.example/page"
```

检查响应标题与正文；挑战页即使 HTTP 200 也视为未访问到内容。

### 2. 只从公开页面提取业务号码

```python
phones = re.findall(r'href="tel:([^"]+)"', html)
```

把号码、页面 URL、抓取日期和分店地址一起保存；不得把重复的品牌号码误当作分店独立号码。

### 3. Playwright 安装路径

```bash
NODE="C:/Users/Admin/.workbuddy-ai/binaries/node/versions/22.22.2-6/node.exe"
NPM="C:/Users/Admin/.workbuddy-ai/binaries/node/versions/22.22.2-6/node_modules/npm/bin/npm-cli.js"
cd "C:/Users/Admin/.workbuddy-ai/binaries/node/workspace"
"$NODE" "$NPM" install playwright
"$NODE" "$NPM" exec --yes -- playwright install chromium
```

安装成功也不代表能访问被 WAF 拦截的页面；不应使用代理轮换、伪造挑战令牌或其他绕过机制。

## 七、已提取样本

样本 CSV：`outputs/clinic-directories/sample_extracted_contacts.csv`。包含上述三条机构记录、号码、地址、来源 URL 和检查日期。

## 八、未核实项

- 三站各自的 ToS 对自动化访问、批量复制和复用数据的完整规定。
- Seek Clinic 精确总页数和跨分类去重后的总诊所数。
- AestheticClinic 100 条记录中可用电话的准确条数。
- Tressless 的马来西亚诊所总量和各分店独立号码。
- 当前 Playwright Chromium 下载源是否可恢复；不影响本轮遵守访问限制的结论。
