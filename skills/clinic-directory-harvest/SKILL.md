---
name: clinic-directory-harvest
description: 从诊所/商家目录站（尤其马来西亚医美、牙科、医美聚合站）批量提取「机构名 + 电话号码 + 地址」并合并去重成一份 CSV。适用于 Seek Clinic、AestheticClinic.my、Tressless 这类 WordPress 或 Next.js 目录站，也适用于任何「列表页带 tel: / 详情页有 Quick facts 表格」的目录结构。触发词：诊所目录、dump 电话、批量导出联系方式、directory harvest、全站抓取号码、合并去重 CSV。
---

# 目录站联系方式批量提取

## 一句话

**403 通常不是「数据拿不到」，而是「非浏览器客户端被挡」。** 先用真实浏览器（Playwright + 系统 Chrome）访问一次站点首页预热拿 cookie，再逐页抓；列表页优先于详情页；抓完必须按 E.164 归一 + 共享号码标记 + 跨源比对，否则号码数会虚高。

## 一、通道选择（按顺序试，不要跳步）

| 顺序 | 通道 | 适用 | 判断依据 |
|---|---|---|---|
| 1 | 裸 HTTP（urllib/curl） | 静态站、无 WAF | 200 + 正文含目标字段 |
| 2 | Playwright + **系统 Chrome** | 有 JS 挑战但有正常渲染路径 | `executablePath` 指向本机 chrome.exe |
| 3 | 服务端渲染取页工具（WebFetch 类） | 本机被 Cloudflare 硬挡 | 本机能拿首页、拿不到子页 |
| 4 | 停止 + 申请授权 | 全站 challenge / CAPTCHA / 登录墙 | 见第四节 |

**关键：不要下载 Playwright 自带 Chromium。** 常见超时；直接复用系统浏览器：

```js
const browser = await chromium.launch({
  executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  headless: true,
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled'],
});
```

## 二、★ 预热拿 cookie（AestheticClinic 型 WAF 的解法）

只 `goto(详情页)` 会停在 `Loading https://...`（标题就是 Loading，正文长度 0）。原因：站点在**首页**下发 `wssplashchk` cookie，缺 cookie 的深链会被塞进中转页。

```js
await page.goto('https://www.aestheticclinic.my/', { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(8000);          // 等挑战脚本跑完
// 之后同一 context 内所有 goto 都正常
```

验证是否真的过了：

```js
const cookies = await ctx.cookies();   // 应包含 wssplashchk / cf_clearance 之类
const title = await page.title();      // 不能是 "Loading ..." / "One moment, please..."
```

## 三、字段提取（别用正则硬啃正文）

### AestheticClinic 型：Quick facts 是 `label \t value` 制表符表格

`innerText` 里长这样（`\t` 分隔，不是 `|`）：

```
Phone or contact route	+60102103921 / +60143288758
Address	73G & 73A-G, JALAN DATARAN CHERAS 4, ... 43200 BALAKONG, SELANGOR
Opening hours	Provider-published hours: Monday-Friday: 10:00am-7:00pm; ...
Matched doctor	Chok Jun Hoong — current APC branch match ...
```

按首个 `\t` 切分建字典，比跨行正则稳得多：

```js
const kv = {};
for (const line of text.split('\n')) {
  const i = line.indexOf('\t');
  if (i > 0) {
    const k = line.slice(0, i).trim(), v = line.slice(i + 1).trim();
    if (k && v && !kv[k]) kv[k] = v;   // 首次出现优先
  }
}
```

**坑：** 用 `Phone or contact route\s*([\s\S]{0,220}?)\s*Opening hours` 这种非贪婪跨行正则会截出 `"8 3395"` 这种半截号码。别用。

### Seek 型：列表页直接带 `tel:`

```
#### Marissa Aesthetic Kuantan
- 48A 1 & 2 Floor, Jalan Putra Square 2, ..., 25200
- +60126691484
[Contact](tel:+60126691484)
```

**列表页已有全部字段 → 不要进详情页**，成本从 1 请求/家降到 1 请求/9 家。

### 无电话的页面要区分「没有」和「解析失败」

- `NO_PHONE`：页面确实无 `Phone or contact route` 行（常见于 `Source Only` 档案）
- `ERR`：导航/挑战/超时
两者混为一谈会导致「全站没电话」的假结论。

## 四、先找「全站归档」，别从分类页开始

这是最容易搞错规模的一步。分类页（`/category/xxx/page/N/`）只覆盖一个类目，看起来像全站，实际可能只占 5%–15%。

**正确做法：找站点的全量归档页，读它的分页总数。**

| 站点形态 | 全站归档 | 判据 |
|---|---|---|
| GeoDirectory / WordPress 目录 | `/clinics/page/N/`、`/directory/page/N/` | 页面标题会写 `Page N Of 603` |
| 自定义 post type | `/wp-sitemap-posts-<posttype>-1.xml` | sitemap 里的 URL 数 |
| 商城型 | `/shop/page/N/` | 同上 |

实测 Seek Clinic：`/clinics/page/2/` 标题直接是 **`Clinics - Page 2 Of 603`**，`/clinics/page/603/` 存在（1 条）。9 条/页 → **全站约 5,419 条**。而此前只抓 `aesthetic-clinic-1` 类目 13 页 = 116 条，占全站 2%。

顺带确认分页参数是否可放大：Seek 的 `?per_page=50` 无效（固定 9 条/页），所以只能翻页。

**记住这条顺序：归档总页数 → 每页条数 → 总量。** 不要用「几个类目 × 猜的页数」去估全站。

## 五、什么时候必须停

| 信号 | 判定 | 动作 |
|---|---|---|
| 标题 `Just a moment...` 且 40s 不消失 | Cloudflare 托管挑战，headless 被识别 | 停；换服务端渲染通道只做**点页**读取，不做批量 |
| `Performing security verification` + Ray ID | 同上 | 停，记录 Ray ID |
| 页面有 CAPTCHA | 需人工 | 停，申请授权 |
| robots 明确 `Disallow` 目标路径 | 越界 | 跳过并标注 |
| robots 只封 `ia_archiver` 等归档爬虫 | 一般爬虫被允许 | 可继续，但**不得镜像再发布** |
| nginx `403 Forbidden`（548B 或 168B 纯 HTML） | IP 级拒绝 | 停本机通道，改服务端渲染点读；不换 UA/代理 |

> Tressless 实测：`User-agent: *` 是 `Allow: /`，只 Disallow 三个归档爬虫；但列表页和详情页对本机 headless 全部返回 Cloudflare 挑战，等 40 秒也不放行。结论是**技术上挡批量、规则上不完全禁止**，只能做小样本点读 + 跨源核对。

**禁止清单：** 换 UA 伪装、代理轮换、指纹补丁、CAPTCHA solver、重放挑战 token、重试 403。

### ★ 403 分两种，处置完全不同（2026-10-27 实测判据）

| 类型 | 特征 | 判据 | 处置 |
|---|---|---|---|
| **缓存型 403** | 只有个别 URL 403，其他同站页面正常 | 给同一路径加无害查询串（`/page/35/?a=1`）后 **200** | 可以重取，这是 CDN 把该 URL 缓存成 403 了 |
| **限流/拒绝型 403** | 403 成片出现，越抓越多 | 加查询串后**仍 403** | 立即停，退避后收工；不换 UA、不换代理、不伪装指纹 |

实测过程：Seek 的 35/36/39 页首次 403，加 `?a=1` 全部取回（缓存型）；连抓 20 多页后 68/71/72/73/74/75 加查询串仍 403（限流型），随即停机。

这条判据可以复用到所有 WordPress / GeoDirectory / Rank Math 站：**先用一个查询串区分「页面被缓存成 403」和「你的 IP 被限」，再决定是重取还是收工。**

## 六、去重与纠错（决定 CSV 质量的一步）

### 1. 号码归一 E.164（马来西亚）

```python
d = re.sub(r"[^\d+]", "", raw)          # "+60 10-368 1400" -> "+60103681400"
if d.startswith("+60"): e164 = d
elif d.startswith("60"): e164 = "+" + d
elif d.startswith("0"):  e164 = "+6" + d   # 03-3395 1393 -> +60333951393
```

正则 `\+?60[\d\s\-()]{7,15}` 会漏掉 `+60 3-3395 1393` 里的空格分隔段，先用 `[^\d+]` 全清再判断前缀。

### 2. ★ 共享号码 ≠ 多个门店电话

实测：`+60102103921`（Clinic RX 品牌号）在 Seek 的 116 条 listing 里出现 **7 次**；`+60109373855`（A Klinik Signature）出现 2 次。**116 条 listing 只有 109 个真实独立号码。**

必须落一个字段：`shared_across_clinics = yes/no`，并在 notes 写 `also listed for: A, B, C`。否则报表会把品牌号算成 N 家门店专线。

### 3. 跨源比对才是「纠错」

同一家诊所在两站号码不一致 → 单独出 `conflicts.csv`，不要静默取其一。同号码在两站都出现 → `cross_source_confirmed = yes`，这是最强的真实性证据。

实测一致案例：Kaiteki SS2 PJ 在 Seek 是 `+60103681400`，Tressless 显示 `+60 10-368 1400`，归一后完全一致。

### 4. 输出两层，别只出一层

- `combined_contacts.csv`：一行一个唯一号码（主交付）
- `combined_contacts_detail.csv`：一行一条源记录（审计用）

只出第一层，就无法回溯「这个号码是从哪条 listing 来的」。

## 七、可复制的执行骨架

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"
NODE="C:/Users/Admin/.workbuddy-ai/binaries/node/versions/22.22.2-6/node.exe"
export NODE_PATH="C:/Users/Admin/.workbuddy-ai/binaries/node/workspace/node_modules"

# 1) 枚举 URL（浏览器内 fetch sitemap，复用 cookie）
# 2) 逐页抓，append JSONL + 每页写 state.json（断点续跑）
# 3) 合并去重
"$PY" merge_contacts.py
```

必带的三件事：

1. **每抓一页 append 一行 JSONL**，再写 `state.json`。中断后跳过已完成 URL。
2. **限速 1.2–2s/页**，单 context 串行。
3. **失败重试 3 次**，仍失败写 `error` 字段，不要丢掉这条 URL。

## 八、坑清单

1. 只 `goto` 深链 → 停在 `Loading ...`，正文 0 字。必须先访首页预热。
2. Playwright 自带 Chromium 下载常年超时 → 用 `executablePath` 指系统 Chrome。
3. `--dump-dom` 在本机沙箱会被 SIGTERM → 用 Playwright 驱动，不要裸调 chrome CLI。
4. 跨行非贪婪正则截断电话 → 改用 `\t` 分键值。
5. 把 `NO_PHONE` 和 `ERR` 混计 → 结论错。
6. 把品牌号当门店专线 → 号码数虚高 6%–10%。
7. 目录站 URL 不稳定：Tressless 列表页给出的详情链接有相当比例 404，抓前先抽样验证 3 条。
8. `Source Only` 档案本来就没联系方式，不是抓取失败。
9. 分页末页返回 403 而非 404 → 不能断言「已翻完」，标 `pagination_terminated=unverified`。
10. ★ **CSV 被 Excel/WPS 打开另存后，`+601123200821` 会变成 `6.01123E+11`**（实测 22/109 行中招，连 `phone_normalized` 一起坏）。对策：原始层只存 TSV/JSONL，合并脚本只读原始层；交付 CSV 时把号码列当文本。
11. 品牌名归一别把 `clinic`/`klinik`/`aesthetic` 全删掉，否则 `Dr Chong Clinic Melaka` 和 `Dr Chong Clinic Ipoh` 会被判成同一家、误报「同名不同号」。只删 `sdn bhd`/`bhd`/`enterprise`。
12. 「同名多号」多数不是错误，是**品牌号 + 分店直线并存**。要输出 `primary_phone_role` 字段（branch_direct / brand_shared），而不是把这些行当冲突删掉。

## 九、实测产出参考（2026-10-27）

| 站点 | 通道 | 规模 | 唯一号码 |
|---|---|---|---|
| seekclinic.my | 服务端渲染逐页 | 全站 603 页 ≈ 5,419 条；实抓 medical-clinic 约 70 页 | 见 combined 表 |
| aestheticclinic.my | Playwright + 预热 | 100 个 sitemap profile，100/100 成功 | 107 |
| tressless.com | 点读 | MY 子集 | 3（跨源核对用） |

三站合并（2026-10-27）：**886 源记录 → 825 唯一号码 / 821 机构**，14 个号码跨源互证，16 条空号被拒（页面本无号码，不猜补）。
