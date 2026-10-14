# MalaysianOSINT 实测报告：能用吗？返回什么？

> 仓库：`https://github.com/ctkqiang/MalaysianOSINT` · 实测日期 2026-10-02
> 结论一句话：**8 个功能里 4 个可用、3 个半可用、1 个已失效。核心的 Semak Mule 完全可用且返回真实数据。**

---

## 一、项目本身能不能跑？

| 项 | 情况 |
|---|---|
| 语言 / 规模 | **C**（`my_osint.c` 27KB + `src/` 10 个模块），25★，1 fork，MIT |
| 活跃度 | 创建 2025-09-04，最后推送 **2025-09-15** —— **已停更约 1 年** |
| 架构 | 基于 `libmicrohttpd` 的自带 HTTP 服务，默认监听 `localhost:8080` |
| 依赖 | GCC/CMake + libcurl + libmicrohttpd + libcjson + libxml2 + OpenSSL + sqlite3 |
| **本机能否编译** | ❌ **不能** —— 本机**没有 gcc / cmake / docker** |
| **公开 demo 能否查** | ❌ **不能** —— `ctkqiang.xin/.../myosint.html` 是**纯前端**，5 个查询调用全部写死指向 `localhost:8080`，远程只引了 CSS/JS/SVG |
| ✅ 可用替代 | 本工作区的 **Python 移植版** `malaysian_osint.py`（11 个子命令），直接调同一批政府端点 |

**所以：原项目要跑，只能 Docker（`docker pull ctkqiang/malaysianosint:latest`）或自备 C 编译环境。本机走 Python 移植版。**

---

## 二、8 个功能逐项实测（真实返回）

### ✅ 完全可用

#### 1. PDRM Semak Mule（电话）—— **核心功能，返回真实数据**

```
POST https://semakmule.rmp.gov.my/api/mule/get_search_data.php
Header: Content-Type: application/json
        Origin/Referer: https://semakmule.rmp.gov.my/
        apikey: j3j389#nklala2          ← 源码硬编码（实测不带也能出数据）
Body:   {"data":{"category":"telefon","bankAccount":"0123456789",
                 "telNo":"0123456789","companyName":"","captcha":""}}
```

**真实返回**（查询 `0123456789`）：

```json
{
  "status": 1,
  "status_message": "Success.",
  "table_header": ["Tel", "Repot"],
  "table_data": [["0123456789", 5]],
  "count": 1434,
  "cat": 2,
  "kw": "0123456789"
}
```

**字段语义（重要，容易读错）**：

| 字段 | 含义 |
|---|---|
| `table_data` | **真正的命中记录** —— 每行是 `[号码, 被举报次数]`，这里是**被举报 5 次** |
| `count` | ⚠️ **不是命中数**，是「**该关键词被查询过的次数**」（1434 次） |
| `kw` | 关键词回显（可用来确认参数被服务端正确接收） |
| `cat` | 分类编号 |

#### 2. Semak Mule（银行账户）

```json
{"table_header": ["No. Akaun", "Repot"], "table_data": [], "count": 11}
```

#### 3. Semak Mule（公司名）

```json
{"table_header": ["Bil", "Tarikh Repot", "Nama Syarikat"], "table_data": [], "count": 0}
```

#### 4. 本地解码：MyKad（身份证）

无网络依赖，**100% 可用**：

```json
{"birthday": "1990-01-01", "birth_state": "Johor", "gender": "Female", "identifier": "1234"}
```

#### 5. 本地解码：SSM（公司注册号）

```json
{"entity_code": "01", "entity_type": "Local Company"}
```

#### 6. 公司详情搜索（malaysiayp.com）

```
GET https://malaysiayp.com/?s=Maybank&location-address=&a=true
```

**真实返回**：15 条命中，含商家名 + 电话，例如
`Abacus Distribution Systems (M) Sdn. Bhd. (PS/180535-T) Kuala Lumpur 03-2057 0035`、
`ADELCO SDN. BHD. +60 (0)3 9133-1313`、`Aseamlease Bhd 60320784511`

#### 7. 社交媒体用户名探测

覆盖 400+ 平台（`https://<platform>/<username>`）。**本质是 HTTP 200/404 判定**，不是数据查询。
实测 GitHub / X / Reddit 三个探测点均正常返回。

### ⚠️ 可用但有保留

#### 8. SSPI 移民局出入境限制

```
GET  https://sspi.imi.gov.my/sspi/index.php?page=sspi/bm    ← 必须先 GET 拿 PHPSESSID
POST 同址  txtIcNo=<12位IC>&btnSemak=Semak
```

**真实返回**（结果在 `<span id="lblStatuscode">` 里）：

| 输入 | 返回 |
|---|---|
| `900101011234`（格式合法） | `Keputusan semakan: Tiada halangan`（无禁止） |
| `123`（太短） | `Keputusan semakan: Masukan No. Kad Pengenalan 12 Digit` |
| `90010101123A`（含字母） | `Masukan No. Kad Pengenalan 12 Digit` |

**✅ 有区分度，接口真在查。** 但两个重要限制：
1. **原项目 README 说要浏览器，实际纯 POST 就行** —— 但**必须先 GET 拿 `PHPSESSID`**，否则返回「请输入身份证号」
2. ⚠️ **`000000000000`（全 0）也返回「Tiada halangan」** → 服务端**只校验 12 位数字格式**，不校验真实性。
   → 结果只能作**线索**，**不能**作为「此人可自由出境」的证明

#### 9. PDRM 通缉名单

```
GET https://www.rmp.gov.my/orang-dikehendaki
```

**⚠️ 能抓但无有效命中**。实测关键词 `TAN`：
- **原实现（无词边界）**：41 处命中 —— **100% 是噪声**（CSS 的 `!important`、马来语导航词 `Keselamatan` 都含 "tan"）
- **改用词边界 `\bTAN\b` 后**：**0 处命中** ✅（已修复）
- 页面为 Sitefinity 门户，通缉条目**没有独立详情页链接**（实测仅 1 个链接指向自身）→ 无法纯 HTML 区分「人名」与「导航词」

#### 10. BNM 金融消费者警示名单

```
GET https://www.bnm.gov.my/financial-consumer-alert-list
```

**⚠️ 极不稳定**（Cloudflare WAF 随机拦截）：

| 请求 | 结果 |
|---|---|
| 第 1 次 | **403**（`Just a moment...` Cloudflare 挑战页） |
| 第 2 次 | **200**，352,063 字节（正常页面，含 16 处名单关键词） |
| 第 3 次 | **200**，349,994 字节 |

→ 独立请求约 2/3 能过；但**连续重试会被持续拦截**（实测连发 4 次全 403）。
→ 建议：**间隔较长时间再试**，或改用无头浏览器（`chrome --headless=new --dump-dom`）。

### ❌ 已失效

#### 11. E-Court 法庭记录

```
POST https://efs.kehakiman.gov.my/EJudgmentWeb/Search   → 404
```

**原项目用的端点已 404 失效。** 现行门户是：

```
https://ejudgment.kehakiman.gov.my/ejudgmentweb/searchpage.aspx?JurisdictionType=ALL   → 200
```

但它是个 **ASP.NET WebForms** 页面（含 `__VIEWSTATE`），需模拟完整表单提交或用浏览器自动化。
→ **纯 HTTP 抓不到结果**。

#### 12. SPRM 反贪记录

```
GET https://www.sprm.gov.my/index.php?page_id=96
```

**❌ 本机不可达**：`ProxyError: Tunnel connection failed: 502 Bad Gateway`（本机代理连不上该域名）。

---

## 三、顺手修掉的 3 个 bug

实测中发现移植版有 3 个缺陷，已修正 `malaysian_osint.py`：

| # | 缺陷 | 症状 | 修法 |
|---|---|---|---|
| 1 | `sspi` **假阳性** | 用宽泛正则，总匹配到提示区文本，不同输入都返回同一个值 | ① 加 `requests.Session()` 先 GET 拿 `PHPSESSID`；② 精确取 `id="lblStatuscode"` 结果区；③ 区分「格式不符」与真实结果 |
| 2 | `wanted` **导航噪声** | `TAN` 命中 41 处，全是 `!important` / `Keselamatan` | 剥离 script/style + nav 容器，改用**词边界** `\b` 匹配 → 41 → **0** |
| 3 | `bnm` **缺重试** | Cloudflare 随机 403，单次失败即放弃 | 加 4 次重试（识别挑战页特征，指数退避） |

---

## 四、两个必须知道的坑

### 坑 1：Semak Mule **必须用本地格式号码**

| 输入 | `table_data` |
|---|---|
| `0123456789`（本地 10 位） | **`[["0123456789", 5]]`** ← 命中！ |
| `60123456789`（国际格式） | `[]` ← **空，漏命中** |
| `+60123456789` | `[]` ← 空 |

**国际格式会静默漏掉记录**，不报错、不提示 —— 最危险的坑。

### 坑 2：README 的返回示例是**编的**

README 写的是：

```json
{"count": 5, "cases": [{"bank": "Maybank", "account": "1234567890", "reported": 3}]}
```

**实际返回**是 `table_header` / `table_data` 数组结构，没有 `cases` 字段。
→ **以实际响应为准，别按 README 写解析代码。**

---

## 五、返回内容的边界（务必对用户说明）

| 能拿到 | 拿不到 |
|---|---|
| 该号码/账户**是否被举报过**、被举报**几次** | ❌ 举报人是谁 |
| 该公司名是否在 Semak Mule 里 | ❌ 案件详情、时间、金额 |
| 身份证的生日/出生州/性别（本地解码） | ❌ **机主姓名** |
| 公司注册号的实体类型（本地解码） | ❌ 公司股东、董事 |
| 商家名 + 电话（malaysiayp） | ❌ 私人号码机主 |

**Semak Mule 只返回 `[号码, 被举报次数]`，没有举报人、没有案件详情、没有机主姓名。**
任何渠道都拿不到「号码 → 机主实名」，要实名只能走报警（PDRM / NSRC **997**）。

---

## 六、复现命令

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
cd "C:/Users/Admin/WorkBuddy AI/2026-10-02-12-08-02"

"$PY" mosint_probe.py         # 仓库元数据 + 文件树 + README
"$PY" mosint_endpoints.py     # 提取全部外部端点 + 测 demo 存活
"$PY" mosint_src.py           # 抓 src/*.c 看真实参数名（apikey 就在这里找到的）
"$PY" mosint_test_all.py      # 8 个功能全量实测 → mosint_test_results.json
"$PY" mosint_mule_fixed.py    # ★ 用正确 apikey + body 结构重测 Semak Mule
"$PY" mosint_clarify.py       # BNM 稳定性 + SSPI 文本性质
"$PY" mosint_sspi_diff2.py    # ★ SSPI 区分度终测（精确取 lblStatuscode）
"$PY" mosint_wanted_struct.py # 通缉页噪声来源分析

# 移植版逐个子命令
"$PY" malaysian_osint.py phone 0123456789
"$PY" malaysian_osint.py bank  1234567890123
"$PY" malaysian_osint.py company Maybank
"$PY" malaysian_osint.py biz   Maybank
"$PY" malaysian_osint.py mykad 900101011234
"$PY" malaysian_osint.py ssm   202001012345
"$PY" malaysian_osint.py sspi  900101011234
"$PY" malaysian_osint.py wanted TAN
"$PY" malaysian_osint.py bnm
"$PY" malaysian_osint.py ecourt TAN
"$PY" malaysian_osint.py sprm  900101011234
```

---

## 七、总评

| 维度 | 评价 |
|---|---|
| **原项目可用性** | ⚠️ 代码思路正确，但**停更 1 年**，8 个功能里 1 个端点已 404 失效；本机无 C 编译环境，需 Docker |
| **核心价值** | ✅ **Semak Mule 的调用方式（含 apikey、body 结构、本地格式要求）是真实有效的** —— 这是本仓库最大的贡献 |
| **数据质量** | Semak Mule 返回**真实**举报计数；SSPI 有区分度但仅格式层校验；其余多为页面抓取，噪声大 |
| **建议** | 用它的**端点情报**，别用它的**实现**（C 服务需 Docker，且部分模块已失效）。本工作区的 Python 移植版已修正 3 个 bug，可直接用 |
