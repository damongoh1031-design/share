# 马来西亚电话号码反查：可用管道 / API / 网页清单

> 调研日期：2026-10-02 · 所有接口均已实测，实测结果标注在下文

---

## 结论先行

1. **没有任何合法渠道能"输入号码 → 返回机主姓名"。** 机主姓名只存在于电讯商实名库（预付卡自 2006 年强制登记，2025 年起强制 MyDigital ID 验证），只有 PDRM / MCMC / 法院能依法调取。
2. 公开能合法拿到的只有三类：**①号段与运营商推测 ②当前实际运营商（HLR/MNP） ③是否被举报为诈骗**。
3. 实测目标号码 `010-2261791`：**PDRM Semak Mule 无记录**，junk-call 无用户报告。号段运营商在 libphonenumber 元数据里是 DiGi，在号段表里是 Celcom —— 两者冲突，正好说明号段法不可靠。

---

## 一、四层管道总览

| 层 | 能拿到什么 | 代表渠道 | 费用 | 能否拿到姓名 |
|---|---|---|---|---|
| A 号段解析 | 号码类型、最初分配运营商、地区 | Google libphonenumber（离线库） | 免费 | ❌ |
| B 实时运营商 | 携号转网后的**当前**运营商、线路状态、漫游 | Telnyx / Twilio / Vonage / HLR Lookups | $0.0015–0.01 每次 | ❌ |
| C 官方诈骗库 | 是否被 PDRM 记录为诈骗号码 + 举报次数 | PDRM CCID **Semak Mule** | 免费 | ❌ |
| D 众包来电识别 | 用户通讯录里的名字、标签、骚扰评分 | **busuk.my**（可编程）· junk-call · Truecaller/Whoscall（仅 App） | 免费+订阅 | ⚠️ 众包数据，非实名，可能错 |
| E 姓名级 | 机主实名 | 仅 PDRM / MCMC / 法院程序 | — | ✅ 需法律程序 |

---

## 二、A 层：号段解析（免费，离线，可编程）

### libphonenumber（推荐）

Google 维护，Python 包名 `phonenumbers`，232 个国家号段元数据，无需联网、无调用限额。

```bash
pip install phonenumbers
```

实测 `+60102261791`：

| 字段 | 值 |
|---|---|
| E.164 | +60102261791 |
| 本地格式 | 010-226 1791 |
| 号码类型 | mobile |
| 号段运营商 | **DiGi** |
| 归属地 | Malaysia |

**致命局限：马来西亚 2008-10-01 起实施携号转网（MNP），号段只代表"最初分配方"，不代表当前运营商。** 且 libphonenumber 的元数据与公开号段表本身就有冲突：

| 来源 | 010-2xx 段归属 |
|---|---|
| libphonenumber 元数据 | DiGi |
| Wikipedia 号段表 | Celcom |
| busuk.my | DiGi（但明确写"不能证明当前 telco"） |

→ **A 层只能当参考，不能当结论。**

### 号段表（原分配，仅作粗筛）

| 号段 | 原运营商 | 号段 | 原运营商 |
|---|---|---|---|
| 010 | 混合（Celcom/XOX/UniFi/Maxis/Tune Talk） | 016 | DiGi |
| 011 | 混合（U Mobile/Maxis/XOX/Celcom/redONE…） | 017 | Maxis |
| 012 | Maxis | 018 | U Mobile / Yes 4G |
| 013 | Celcom | 019 | Celcom |
| 014 | 混合（Maxis/DiGi/Tune Talk/Celcom） | 015 | 宽带/VoIP 专用 |

号码长度：`011`、`015` 为 8 位用户号（总 11 位）；其余为 7 位用户号（总 10 位）。

---

## 三、B 层：实时运营商查询 API（付费，能穿透 MNP）

| 服务 | 单价 | 返回字段 | 备注 |
|---|---|---|---|
| **Telnyx** Number Lookup | **$0.0015/次起** | carrier、line type、portability、CNAM | 最便宜；CNAM 主要覆盖美国 |
| **Twilio** Lookup v2 · Line Type Intelligence | **$0.008/次** | carrier name、MCC/MNC、line type | 全球覆盖；Caller Name 包**仅美国**；Identity Match 不含亚洲 |
| **Vonage** Identity Insights | Original Carrier €0.001 / **Current Carrier €0.007** | 原运营商 / 现运营商、SIM swap、Subscriber Match | Current Carrier 才是穿透 MNP 的值 |
| **HLR Lookups** | HLR €0.01 / MNP €0.005 / NT €0.0025（量级 1M 内） | 实时 HLR 连通性、携转、漫游、号段类型 | 预付制，支持加密货币/银行转账 |
| **numverify**（apilayer） | 免费 100 次/月（禁商用）；Basic $14.99/5,000 次 | carrier、line type、location | 基于号段库，**不穿透 MNP** |
| **CallerAPI** | $25/月起 | live HLR carrier、line type、ported 状态与日期 | 订阅制 |
| **Telesign** PhoneID | 按量，需询价 | 号码身份、风险评分 | 企业向 |

**选型建议**：只要"当前运营商" → Telnyx（$0.0015）最划算；要批量清洗号码库 → HLR Lookups 的 MNP 端点（€0.005）；已在用 Twilio → 直接开 Line Type Intelligence（$0.008）。

> ⚠️ 所有 B 层服务都**不返回姓名**。任何宣称"马来西亚号码查机主"的 API 都是灰产或伪造。

---

## 四、C 层：PDRM 官方诈骗库（免费，已实测可用）

### 4.1 网页版

- **Semak Mule CCID**：https://semakmule.rmp.gov.my
- 支持三类查询：银行账号 / 电话号码 / 公司名
- 完全免费、无需注册、无验证码（当前 `disableCaptcha = true`）

### 4.2 未公开文档的 JSON 接口（已逆向，可直接编程调用）

```
POST https://semakmule.rmp.gov.my/api/mule/get_search_data.php
Content-Type: application/json

{"data": {"category": "telefon", "telNo": "0102261791"}}
```

| category | 对应字段 |
|---|---|
| `bank` | `bankAccount` |
| `telefon` | `telNo` |
| `namasyarikat` | `companyName` |

实测响应：

```json
{"status":1,"status_message":"Success.",
 "table_header":["Tel","Repot"],
 "table_data":[],          // ← 这才是结果
 "count":6,                // ← 这是"该关键词被查询次数"计数器，不是命中数！
 "cat":2,"kw":"0102261791"}
```

命中示例（`0123456789`）：`"table_data":[["0123456789",5]]` = 被举报 5 次。

**三个坑**：
1. **号码格式必须是本地格式**（`0123456789`）。用 `+60123456789` 或 `60123456789` 查会**漏掉命中**——实测同一号码换格式就从"5 条记录"变成"无记录"。
2. `count` 字段是查询计数器，**不是结果数量**，别误读。
3. 接口未公开、无版本承诺，`apikey` 请求头（`j3j389#nklala2`，写在 main.js 里）当前可不带，但随时可能变。

### 4.3 其他官方/半官方

| 渠道 | 用途 |
|---|---|
| NSRC **997** | 已被骗、钱刚转出，紧急止付 |
| MCMC 投诉门户 https://aduan.mcmc.gov.my | 举报骚扰/诈骗号码，MCMC 可对号码与运营商采取行动 |
| CCID Scam Response Centre 03-26101559 / 03-26101599 | 诈骗报案 |
| Sebenarnya.my（MCMC） | 核实网络传言/链接，非号码查询 |
| MCMC Network Investigation Dept（nid.support@mcmc.gov.my） | 执法/调查用途的当前服务网络核实 |

> ⚠️ **MCMC 的 MNP Check 网页（mnpcheck.skmm.gov.my）已于 2026-05-08 正式停运**，官方理由是"无限通话套餐 + OTT 普及后不再相关"。不要再指望这个免费官方查运营商入口。调查用途改走电讯商或 MCMC NID；MNP dipping 查询走清算中心 Talian（inquiry@talian.com.my）。

---

## 五、D 层：众包来电识别 —— 实测「网页版基本是死的」

用无头 Chrome（`--dump-dom` 真渲染 + `--log-net-log` 抓全部网络请求）逐站实测，结论比预期更差：

| 渠道 | 网页可编程？ | 实测证据 |
|---|---|---|
| **Truecaller** | ❌ **完全不可用** | 真渲染后 DOM 里只有搜索表单，**零号码数据**；netlog 里没有任何查询请求。它强制登录（Google/Microsoft/手机号），网页版本质是引流页 |
| **Whoscall** | ❌ **完全不可用** | `whoscall.com/en/number/<号码>` 渲染后页面是**空的**（只剩 cookie 横幅）；68MB netlog 中**没有一条 XHR 到 API 主机**，全是 Next.js RSC 导航。数据只在 App 内 |
| **busuk.my** | ✅ **可直接抓** | 纯静态 HTML：`busuk.my/semak/nombor-telefon/<号码>/` → 返回线路类型 / 运营商 / 风险等级 / 社区报告。**免费、无需注册、无需 Key** |
| **junk-call.com** | ✅ 可抓，但数据薄 | `/my/<号码>` 静态 HTML。实测 `0102261791`、`0123456789` 均 **0 条评论**；站点缓存还报磁盘满 |
| kitajaga.co/semak | ❌ | Nuxt SPA，`/api/*` 全部 404，无公开接口 |
| tellows.my | ❌ | 域名不存在（DNS 失败）；tellows.com 返回 403 |
| shouldianswer.net | ❌ | 无马来西亚覆盖（404） |
| ScamCheck.my / numtrace / Searqle / Scannero | ⚠️ 数据可疑 | 宣称能给 "owner details"，实测多为营销话术 |

**结论：D 层唯一真正可编程的入口是 busuk.my（+ junk-call 作补充），而它们都不提供机主姓名。** Truecaller / Whoscall 想要数据只能装 App。

**本质局限**：众包名字来自用户通讯录，不是实名数据。可能显示"某某公司"、可能是别人的备注名、可能过期。**不能作为身份认定依据。**

### 5.1 本机要不要装 App？

| 目标 | 要不要装 App | 怎么做 |
|---|---|---|
| 查"是不是诈骗号" | **不用** | 用 C 层 Semak Mule（免费 API）+ D 层 busuk.my |
| 查"线路类型 / 运营商" | **不用** | A 层 libphonenumber + busuk.my |
| 查"Truecaller / Whoscall 上的标签" | **要** | 见下表三条路 |
| 查"机主姓名" | **装什么 App 都没用** | 走报警 / 法院 |

要拿 Truecaller / Whoscall 的数据，只有三条路：

| 路线 | 具体做法 | 评价 |
|---|---|---|
| ① 官方企业接口 | Whoscall → Gogolook **Asi**（API/SDK，商务洽谈）；Truecaller → **Truecaller for Business** | 唯一合规、稳定；个人拿不到，需公司主体 |
| ② 手机装 App | Android 装 Truecaller / Whoscall，手动查 | 最省事。Whoscall App 已内置 PDRM Semak Mule 数据 |
| ③ 本机跑 Android | BlueStacks / Genymotion 模拟器 + APK，用 `adb` 做 UI 自动化 | ⚠️ Windows Subsystem for Android 已停更；方案可行但重，且违反 App ToS |
| ④ 非官方 Python 库 | `pip install truecallerpy` | ❌ **不推荐**：最后提交 2023-08，需真实手机号收 OTP + `installationId`，随时失效 |

> 判断依据：既然 D 层拿不到姓名、而 C 层（Semak Mule）免费且稳定，**在 D 层投入的性价比极低**。要名字就直接走法律程序。

### 5.2 「如何拿到接口」方法论（可复用）

按页面类型分四种情况：

**① 静态 HTML → curl 直接抓**

```bash
curl -s "https://busuk.my/semak/nombor-telefon/0102261791/" | grep -o "Carrier.*"
```

**② JS 渲染 → 读前端源码逆出接口**（Semak Mule 就是这么逆出来的）

```bash
# 1. 找配置里的 endpoint 常量
curl -s "https://semakmule.rmp.gov.my/config.js"
#   → var apiEndPointMule = "https://semakmule.rmp.gov.my/api/mule/";

# 2. 下载主 bundle，搜 endpoint 字典
curl -s -o main.js "https://semakmule.rmp.gov.my/static/js/main.<hash>.js"
grep -o 'Go={[^}]*}' main.js
#   → searchData:"get_search_data.php"

# 3. 找调用点，读出请求体字段名
#    搜 'Go.searchData' 附近 → 得 {data: t}；搜 '[^a-zA-Z0-9_]sa(' → 得表单 state 的 key
#   → category / telNo / bankAccount / companyName
```

**③ JS 渲染 → 无头浏览器真渲染后读 DOM**

```bash
chrome --headless=new --dump-dom --virtual-time-budget=15000 "<url>"
```

**④ 想知道"到底调了哪个接口" → 抓 netlog**

```bash
chrome --headless=new --dump-dom \
  --log-net-log="C:\Users\Admin\AppData\Local\Temp\nl.json" \
  --net-log-capture-mode=Everything "<url>"
# 然后从 netlog 里筛非静态资源 URL
grep -o -E "https://[a-z.]*目标域[a-z.]*/[a-zA-Z0-9._/?=&%~-]*" nl.json \
  | grep -v -E "\.(js|css|png|jpg|svg|woff2?)$" | sort -u
```

本文对 Whoscall / Truecaller 的"没有可调 API"这个结论，就是这样证伪出来的。

**⑤ 需要登录态 → CDP 接管已登录的浏览器**

```bash
chrome --remote-debugging-port=9333 --remote-allow-origins=* \
       --user-data-dir="<已登录的 profile>"
# 再用 websocket 连 ws://127.0.0.1:9333/devtools/page/<id>
```

> ⚠️ 踩坑记录：用 Python `subprocess.Popen` 拉起 Chrome 再连 CDP websocket，在本机沙箱里会被整个进程组回收（无输出、SIGTERM）。**改用单条前台命令 + `--dump-dom` / `--log-net-log` 最稳**；CDP websocket 必须加 `--remote-allow-origins=*`，否则握手 403。

---

## 六、E 层：真要拿到姓名，只有合法程序

### 法律红线

- **PDPA 2010（2024 修订）**：未经授权处理/贩卖个人数据违法，最高 **RM1,000,000 罚款 + 3 年监禁**。
- **TM 已于 2014 年停掉 103 查号台**（固话查号服务），理由正是 PDPA 合规。所以**固话也没有官方查号渠道了**。
- Telegram/暗网上"查马来西亚机主"的服务：数据来自盗卖，在马来西亚属刑事犯罪，且大量为伪造。

### 可行路径

| 场景 | 做法 |
|---|---|
| 诈骗电话 | 报警 PDRM（CCID）+ NSRC 997；警方可向电讯商调取实名信息 |
| 骚扰 / 诽谤 | 委托律师向法院申请 **Norwich Pharmacal order**，强制电讯商披露 |
| 核实"来电者是否代表某机构" | **挂断，自己回拨该机构官网公布的号码** ← 最实用、零成本 |
| 号码属于商家/公司 | 用 **SSM**（公司注册局）查公司主体；或 Google Maps / Yellow Pages 反查商家电话 |
| 想批量做风控/号码清洗 | 用 B 层 API（Telnyx/Twilio/HLR Lookups）拿运营商与线路类型，别碰姓名 |

---

## 七、针对 `010-2261791` 的实测汇总

| 渠道 | 结果 |
|---|---|
| libphonenumber 离线解析 | `+60102261791`，类型 mobile，号段运营商 **DiGi**，归属 Malaysia |
| Wikipedia 号段表 | 010-2xx 段 → **Celcom**（与上冲突，见 §2） |
| busuk.my | 类型 Mudah Alih，**运营商 Digi**，风险等级 Tidak Diketahui，无社区报告 |
| **PDRM Semak Mule** | **无记录**（`table_data` 空）→ 未被举报为诈骗号 |
| junk-call.com | 页面存在，**0 条用户报告** |
| Truecaller 网页版 | 无头浏览器真渲染后 **DOM 里没有任何号码数据**（强制登录） |
| Whoscall 网页版 | `/en/number/60102261791` 渲染后为空，**无任何 API 请求** |

**结论**：这个号码在所有公开渠道都查不到机主信息；唯一有意义的结论是"**未被 PDRM 举报过**"——但这**不等于安全**，未被举报的号码一样可能是新号段诈骗。号段归属上 libphonenumber 与 busuk.my 一致（Digi），Wikipedia 的 Celcom 应属过时或错误。

---

## 八、配套脚本

| 脚本 | 作用 | 依赖 |
|---|---|---|
| `my_phone_check.py` | A 层 + C 层：离线号段解析 + PDRM Semak Mule 举报库 | `phonenumbers`、`requests` |
| `crowd_lookup.py` | D 层：busuk.my + junk-call 众包数据（无需 App、无需 Key） | `requests` |
| `cdp_capture.py` | 无头浏览器抓 JS 渲染页面的真实接口与渲染后文本 | `websocket-client`、`requests` |

```bash
python my_phone_check.py 0102261791        # 号段 + Semak Mule
python crowd_lookup.py 0102261791          # busuk.my + junk-call
python cdp_capture.py "https://whoscall.com/en/number/60102261791" 15   # 抓接口
```

实测输出（`0102261791`）：号段 mobile / DiGi；Semak Mule 无记录；busuk.my 运营商 Digi、无社区报告。
实测输出（`0123456789`）：Semak Mule 命中 1 条，被举报 5 次。

> `cdp_capture.py` 在本机沙箱下可能被进程组回收；若失败，改用文档 §5.2 的单条前台 `--dump-dom` / `--log-net-log` 命令。

---

## 附：一句话选型

- 只想查"是不是诈骗号" → **Semak Mule**（免费，本文已给接口）
- 只想查"现在归哪家运营商" → **Telnyx**（$0.0015/次）
- 想查"众包标签/评论" → **busuk.my**（静态 HTML，直接抓）；Truecaller/Whoscall 只能装 App
- 想查"机主是谁" → **没有合法 API**，走报警或法院
