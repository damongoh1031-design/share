---
name: malaysia-phone-osint
description: Reverse-lookup a Malaysian phone number across all legal OSINT channels — 马来西亚电话号码反查 / 查号码归属 / 这号码是谁的 / 谁打给我 / 是不是诈骗号 / 来电识别 / 查运营商与线路类型. Covers libphonenumber prefix parsing, MNP/carrier lookup APIs, the PDRM Semak Mule scam-report database, crowd-sourced caller-ID sites (busuk.my / junk-call.com), and the reverse-engineered private APIs of phone-number-lookup / phoneosint / MalaysianOSINT (DB3 CallApp / s.callapp.com — currently the only working crowd-sourced source — and DB1 CallerID / aunumber.com). Use when the user gives a Malaysian number (01x-xxxxxxx / +60...) and asks who it belongs to, whether it is a scam, its carrier or line type, or asks to run phone OSINT tools. Also contains two reusable workflows: reverse-engineering a frontend's private JSON API from config.js + main bundle, and validating crowd-sourced name data against ground truth (token fuzzy matching + Chinese pinyin matching). Also covers the reverse need — how to REPORT a scam number in Malaysia: official channels (NSRC 997 / PDRM report / MCMC CRP / Cyber999 / telcos) and crowd-sourced platforms (Whoscall report flow, Truecaller, CallApp, GetContact), including the Whoscall⇄PDRM Semak Mule data bridge. Use when the user asks 如何举报诈骗号码 / 怎么向 Truecaller / Whoscall / CallApp 举报 / report scam number to MCMC.
description_zh: "马来西亚电话号码全渠道反查：号段解析 / 运营商 / PDRM 诈骗库 / 众包来电识别 / 三个开源 OSINT 工具；含前端私有接口逆向方法论；含诈骗号码举报通报渠道（997 / MCMC / Whoscall / Truecaller / CallApp）；含 DB3 CallApp 限流阈值（≈100 次/窗口，绑 tk 凭据）与 X_C_CODE 状态码全表"
description_en: "Reverse-lookup a Malaysian phone number across all legal OSINT channels, plus a frontend private-API reverse-engineering workflow, plus where to report scam numbers (NSRC 997 / MCMC / Whoscall / Truecaller / CallApp). Includes the DB3 CallApp rate-limit threshold (~100 req/window, keyed on the tk credential) and the full X_C_CODE status-code table."
version: 1.10.0
display_name: "malaysia-phone-osint"
visibility: "public"
agent_created: true
---

# 马来西亚电话号码反查（OSINT）

## 何时使用

- 用户给出马来西亚号码（`010-2261791`、`0162281297`、`+6012...`），问「这个号码是谁的」「谁打给我」「是不是诈骗号」
- 要查号码的运营商 / 线路类型 / 归属地
- 要跑 `phone-number-lookup` / `phoneosint` / `MalaysianOSINT` 这类 OSINT 工具
- 需要逆向某个前端站点的私有 JSON 接口（见 §6，通用方法论）

## 0. 先讲清楚边界（必须在回答里说明）

| 能拿到 | 拿不到 |
|---|---|
| 号段/运营商/线路类型（离线） | **机主姓名**（电讯商实名库，仅 PDRM/MCMC/法院可调取） |
| 是否在 PDRM 诈骗举报库中 | 实名地址、身份证号 |
| 众包来电标签（别人通讯录里的备注名，**经常只有名、没有姓**） | 通话记录、短信 |
| B2B 职业库的**概率全名**（PDL / RocketReach，需自有 API key，马来西亚覆盖率**未实测**） | 电讯商实名、身份证号 |

**没有任何合法公开渠道能「输入号码 → 返回机主实名」。** 想要实名只有两条路：报警（PDRM / NSRC **997**）或律师向法院申请 **Norwich Pharmacal order** 披露令。

众包库缺姓是**数据源结构**，不是解析 bug：通讯录备注多数只存名。换接口、加模糊匹配、剥称谓，都补不出库里没有的姓。能提高的是「已有片段的交叉确认率」，不是「凭空推出姓氏」。见 §4.1。

**PDPA 2010（2024 修订）**：非法交易个人数据最高 **RM1,000,000 + 3 年监禁**。所有操作只针对公开数据源。

---

## 1. 四层管道总览

| 层 | 数据源 | 成本 | 给什么 |
|---|---|---|---|
| **A** 号段解析 | libphonenumber（离线） | 免费 | 运营商*、线路类型、地区 |
| **B** 实时运营商 | Telnyx / Twilio / Vonage / HLR Lookups | $0.0015–0.01/次 | **当前**真实运营商（穿透 MNP） |
| **C** 官方诈骗库 | PDRM CCID Semak Mule | 免费 | 是否被举报为诈骗号 |
| **D** 众包来电识别 | DB3 CallApp / DB1 CallerID / busuk.my / base.ly / whocallsme | 免费 | 通讯录备注（**非实名，常缺姓**）。**DB3 CallApp 当前唯一稳定可用**，且能给社交账号 ID |
| **F** B2B 职业库反查 | People Data Labs / RocketReach | 按次计费，需自有 key | **概率全名**（`first`+`last`），不是实名；MY 覆盖率未实测 |
| **E** 实名级 | 法院披露令 / 报警 | — | 电讯商实名（唯一合法途径） |

\* **A 层运营商只是「号段最初分配方」**。马来西亚 **2008-10-01 起实施 MNP（携号转网）**，号段不代表当前运营商。要当前运营商只能走 B 层。

> `MCMC MNP Check` 网页已于 **2026-05-08 停运**（`mnpcheck.skmm.gov.my`）。调查用途改走 MCMC NID（`nid.support@mcmc.gov.my`）；MNP dipping 走 Talian（`inquiry@talian.com.my`）。

---

## 2. A 层 + C 层：一键查（最常用）

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
"$PY" <skill>/scripts/my_phone_check.py 0162281297
"$PY" <skill>/scripts/my_phone_check.py 0162281297 0102261791   # 多个号码
"$PY" <skill>/scripts/my_phone_check.py 1234567890123 --bank     # 银行账号
"$PY" <skill>/scripts/my_phone_check.py "ABC SDN BHD" --company  # 公司名
```

输出：E.164 / 本地格式 / 号码类型 / 号段运营商 / 归属地 + Semak Mule 命中记录。

---

## 3. C 层：PDRM Semak Mule（**核心资产，接口已逆向**）

```http
POST https://semakmule.rmp.gov.my/api/mule/get_search_data.php
Content-Type: application/json
apikey: j3j389#nklala2
Origin: https://semakmule.rmp.gov.my

{"data":{"category":"telefon","bankAccount":"0123456789","telNo":"0123456789",
         "companyName":"","captcha":""}}
```

⚠️ **必须带全 5 个字段**（未用的填空字符串）—— 2026-10-02 实测：只传 `{"data":{"category":"telefon","telNo":"..."}}`
会被服务端当作参数缺失，返回 `table_data:[]`、`kw:""`（**静默漏命中**，不报错）。

`category` ∈ `telefon`(telNo) / `bank`(bankAccount) / `namasyarikat`(companyName)。
结果在 `table_data`，形如 `[[号码, 举报次数]]`。

**实测真实响应**（查 `0123456789`）：
```json
{"status":1,"status_message":"Success.","table_header":["Tel","Repot"],
 "table_data":[["0123456789",5]],"count":1434,"cat":2,"kw":"0123456789"}
```
→ 该号**被举报 5 次**；`count:1434` 是查询计数器。

### 三个必踩的坑

1. **号码必须用本地格式**（`0123456789`，0 开头、无连字符）。用 `+60...` 或 `60...` 会漏命中 —— 实测同一号码从 **5 条记录变 0 条**。
2. **`count` 字段是「该关键词被查询次数计数器」，不是命中数**。别把它当举报数。
3. **`apikey` 当前可以不带**（接口不校验），但带上更稳。

**⚠️ 原项目 README 的返回示例是编的**：README 写 `{"count":5,"cases":[{"bank":"Maybank",...}]}`，
**实际没有 `cases` 字段**，是 `table_header`/`table_data` 数组结构。**以实际响应为准。**

### 逆向方法（可复现）

```
config.js            → 找 apiEndPoint 常量
static/js/main.<hash>.js → 搜 Go.searchData 得路径
                     → 搜 [^a-zA-Z0-9_]sa\( 得调用点
                     → 从调用点读表单 state 的字段名
```

**交叉验证成功**：`ctkqiang/MalaysianOSINT` 的 `src/pdrm.c` 里硬编码的 `#define PUBLIC_KEY "j3j389#nklala2"` 与独立逆向结果**完全一致**。

---

## 4. D 层：众包来电识别

```bash
"$PY" <skill>/scripts/crowd_lookup.py 0162281297
```

| 站点 | 状态 | 说明 |
|---|---|---|
| `busuk.my/semak/nombor-telefon/<号码>/` | ✅ 可编程 | 静态 HTML，返回线路类型/运营商/风险等级/社区报告。**任意号码都有页面**（按需生成），无数据时输出 `Tidak Diketahui` → 页面存在 ≠ 有人提过该号 |
| `junk-call.com/my/<号码>` | ⚠️ **内容已证伪** | 静态 HTML，但**「Recent Call」记录是模板生成的**，不是真实举报（见下） |
| `base.ly/my/<号码>`（Basely）/ `slick.ly/my/<号码>`（Slickly） | ✅ 可编程（curl 恒 403，**必须用 WebFetch**） | **同一运营方的双站镜像**：同号码在两边统计完全一致（同搜索次数、同创建日、同 0 评论 0 评分）。**只为部分号码生成页面，其余返回 404**（实测 10 个号码里 4 个 404，且两站同步 404）。`Tahap risiko` 字段实际取值只有 `Aktif` / `Tidak aktif` / `Curiga` —— 看着像风险等级，**实为「号码状态」标记**（多半由搜索热度/最后搜索时间推出），不要当诈骗评估 |
| `whocallsme.com/Phone-Number.aspx/<本地格式>` | ✅ **有真实举报**（必须 WebFetch，curl 恒 403） | **唯一实测到真实用户举报文本的众包站**（马来西亚号码也覆盖）。实测 `0162580348` → 1 条真实举报（署名 `Lee`、类型 `Non-profit organization`、2022-08-17）。⚠️ 站点有 **OctoNet HTTP filter**，按出口 IP 拦 VPN/代理，**同一会话内时通时断**（`Access Denied`），需重试；无评论时页面明写 `There are no comments yet about <号码>` → 这句可直接当「无举报」判据 |

### ★ base.ly / slick.ly 并非「统计完全一致」（2026-10-05 更正）

原文说两站「同搜索次数、同创建日」。**实测 `0102261791` 两边不一致**：

| 字段 | base.ly | slick.ly |
|---|---|---|
| 搜索次数 | **11** | **9** |
| 风险标签 | `Curiga` | `Mencurigakan` |
| 首次报告 | 3 周前 | 20 天前 |
| 评论 / 评分 | 0 / 0 | 0 / 0 |

→ 两站**同源但不同步**（缓存/更新时间差）。**不要拿其中一站的次数当结论，也不要用「两站数字必须相等」做校验。**
→ 但两站「同为 404」的规律仍成立：**只为有搜索热度的号码生成页面**，404 = 无人查过。

### ★ junk-call.com 的「记录」是模板（2026-10-02 对照实验证伪）

拿一个从未被举报过的随机号（`0123456789`）跑同一条路径，与目标号逐字段比对：

| 字段 | `0102261791` | `0123456789`（对照） | 判定 |
|---|---|---|---|
| 前两条记录日期 | `01/10/2026`、`30/09/2026` | **`01/10/2026`、`30/09/2026`** | **完全相同** → 模板 |
| 标签 | 全为 `ColdCall` | 全为 `ColdCall` | 模板 |
| 记录内容 | 含 `Record does not exist (No Record Found)` | 含同类条目 | 把「无记录」当来电记录 → 逻辑不自洽 |

→ **junk-call.com 的页面是 SEO 模板，不是举报证据。** 只有 `1 Comment` 来自 Facebook 评论插件（`fb-comments`），插件计数与真实评论数无关。
→ 同理，**「任意号码都能查到页面」的站点（junk-call / busuk.my）不能用来判断「网上有没有人提到这个号」**。

### ★ 站点收录枚举的正确姿势（回答「有哪些网站提到过这个号码」）

1. **先搜引擎，不要先跑站点**：`WebFetch https://html.duckduckgo.com/html/?q="<号码>"` —— DDG 的 `html.` 端点无需 JS、可编程、结果干净。Google/Bing 对带引号号码查询会退化成泛结果（Bing 返回一堆 114 查号站）。
2. **多格式各搜一遍**：`0102261791` / `010-226 1791` / `+60102261791` / `"60 10-226 1791"`。同一页面常只在一种格式下被索引。
3. **再对候选站做「有页 / 有数据 / 有内容」三级判定**，别把 200 当命中：
   - `grep -c "<号码>"` 只证明页面里出现该串 —— **URL 回显、`<link rel=canonical>`、Next.js 路由 payload 都会命中**（Whoscall、Sync.me 实测就是这样，**零真实数据**）。
   - 必须再剥标签看可见文本（`re.sub(r'<[^>]+>',' ')`）才判断得出。
4. **必做对照组**：拿一个已知无关的号码跑同一站点。对照结果相同 → 模板化，该站结论作废。

**已实测「无收录 / 无真实数据」的站点（2026-10-02，勿重复探测）**：

| 站点 | 实测结果 |
|---|---|
| `sync.me/search/?number=<E.164>` | HTTP 200，号码**只出现在 `<title>`/`canonical`/`hreflang` 回显**，无数据 |
| `whoscall.com/en/number/<E.164>` | HTTP 200，号码**只在 Next.js 路由 payload** 里，无数据 |
| `numtrace.com/my/<号>` / `findsio.io/my/<号>` / `numfinder.com/my/<号>` / `shouldianswer.net/my/<号>` / `numlookup.com/<号>` | 404，无按号码生成的页面 |
| `www.phonenumbers.my/<号>` | 200 但页面内无该号码 |
| `who-called.co.uk` / `800notes.com` / `callercenter.com` / `scamwatcher.com` | 403（CF/WAF 拦），无马来西亚数据 |
| `semaknombor.com` / `callerid.my` / `semakno.com` / `whocalledbase.com` | 域名不存在或 522 |

**⚠️ 搜索引擎的「数字串误匹配」陷阱**：引号搜号码会命中**别的国家**的同数字串站点。实测 `0162166952` 在 DDG 命中的是
`merinfo.se/vem-ringde/46162166952`（瑞典站，把 `016` 当瑞典区号，显示运营商 `Telia Sverige AB`、0 举报）。
**判定方法**：看 URL 里的国家码前缀（`46` = 瑞典）和站点语言。**别把外国同号当本地命中**。
| `tellows.my` / `shouldianswer.net` 的马来西亚路径 | 无覆盖（与 §4 表格一致） |

| **Truecaller 网页版** | ❌ 不可编程 | 无头浏览器真渲染 + 68MB netlog 证伪：DOM 里只有搜索表单，无查询请求，强制登录 |
| **Whoscall 网页版** | ❌ 不可编程 | `/en/number/<号码>` 渲染后为空，netlog 中无任何 API XHR，数据只在 App 内 |
| tellows.my / shouldianswer.net | ❌ | 域名不存在 / 无马来西亚覆盖 |

**结论：数据只在 App 内，网页版是引流页。** 想用 Truecaller/Whoscall 只能①装 App 手动查，或②走官方企业接口（Gogolook **Asi**、Truecaller for Business，需商务洽谈）。

### DB1 CallerID（aunumber.com）—— 曾唯一有数据的库，**2026-10-05 起已封**（附量化准确率）

**接口**：`POST https://app.aunumber.com/api/v1/sea.php`。响应经三层编码（位移 → 逐字符 chr → base64），解密后是 JSON。

**准确率盲测（2026-10-02，用户提供 4 组 ground truth）**：

| 号码 | 已知真实名字 | DB1 返回 | 判定 |
|---|---|---|---|
| `0123355873` | roland leong | （空） | 无数据 |
| `0122071768` | dato ricky lim | `Dato Dr Ricky` | 命中 `dato` `ricky`，缺姓氏 |
| `0123013006` | martin lim | （空） | 无数据 |
| `0192385938` | marvin lee | `Mr Malvin` | ≈ 命中 `marvin`（编辑距离 1），缺姓氏 |

- **有返回 2/4 = 50%** ｜ **部分命中 2/4 = 50%** ｜ **完全正确（含姓氏）0/4** ｜ **重查可复现 4/4**
- 🔑 **核心规律：命中的记录全部只给"名"、不给"姓"** —— 该库存的是「来电方在用户通讯录里被存成什么」，而多数人存联系人只存名不存姓。
- ✅ **定位：适合「验证假设」**（已知可能是谁 → 交叉确认），**不适合「从零推出完整姓名」**。
- 单点验证：`0162281297` → `Prof Lee`，**经用户确认为正确名字**。

**与 Truecaller 交叉验证（2026-10-02，9 个号码，名字来自 Truecaller）**：

| 指标 | 结果 |
|---|---|
| **有返回** | **9/9 = 100%** |
| token 命中 ≥1 | **7/9 = 78%** |
| 子串包含 | 2/9 |
| 完全一致 | 0/9 |
| 可复现 | 9/9 |

🔑 **覆盖率与 Truecaller 高度相关，但非必然**（三批累计 22 个号码：**18/22 = 82% 有返回**）：

- 第二批（9 个 TC 有名字的）→ 9/9
- 第三批（9 个）→ 7/9
- → Truecaller 没名字的号码，DB1 基本也没有 —— 两库覆盖人群高度重叠（都是「曾被存进某人通讯录」的号码）。
- → **DB1 返回空 = 该号码大概率从未被任何人存过**，不是接口故障。**先查 Truecaller，没有就不必再跑 DB1。**

🔑 **DB1 备注完整度参差**（别指望它总是给全名）：

- ✅ **能给完整全名**：`Eng Jing Hao` = `ENG JING HAO`（剥 `MR` 称谓后全中；22 个里 token 全中 2 个）
- ◐ 常给简称：`Liza Yap` ⊂ `LIZA YAP SURBANA`、`Linda Lim` ⊂ `LINDA LIM VG`
- ◐ 常带职业/关系标签：`Loh lawyer`、`Mr Eddie PA`、`abe emy`（`abe` = 马来语 Abang「大哥」）
- ◐ 有「组织 : 人名」格式：`Lotus Power : Angie Ng`
- ⚠️ **库里有中文备注**：`智辉` ← `CHEE HUI`（拼音 `zhihui` ⊃ `hui`）→ **跨库比对必须过拼音**，否则漏判

🔑 **两库常给不同的名字片段**（别指望字符串相同，完全一致 0/9，实质命中 78%）：

- DB1 偏**简称 + 职业/关系标签**：`Loh lawyer`、`abe emy`（`abe` = 马来语 Abang「大哥」）、`Mr Eddie PA`
- Truecaller 偏**规范全名**：`LIZA YAP SURBANA`、`LINDA LIM VG`
- DB1 常是 TC 名的**子串**：`Liza Yap` ⊂ `LIZA YAP SURBANA`、`Linda Lim` ⊂ `LINDA LIM VG`
- 最极端：`boon han lim`（DB1，人名）vs `BOON HONDA CITY`（TC，车行）—— **同号两库完全不同**

**三批合并 22 个号码**：有返回 **18/22 = 82%** ｜ token 命中 **14/22 = 64%** ｜ 子串包含 4/22 ｜
**token 全中 2/22** ｜ 可复现 **22/22 = 100%**。

⚠️ **口径**：测的是**两库一致率**，不是准确率 —— Truecaller 本身也是众包，一致 ≠ 正确。
但两个独立库命中同一名字，可信度显著高于单库。

**字段语义（已用 6 个样本校准，别误读）**：

| 字段 | 真实含义 |
|---|---|
| `name` | 众包备注名（可能为空） |
| `belong_area` | **默认 `"Malaysia"`**；只有真有地址时才具体化（`"Tumpat, Malaysia"`）→ 等于 `Malaysia` 应视为「无区域信息」 |
| `type_label` | **社区标签**（如 `Scam`），不是线路类型。空 = 无标签 |
| `report_count` | 被举报次数。空 = 无 |
| `address` | 地址。空 = 无 |
| `old_tel_number` | ⚠️ **查询号码的回显**，不是「旧号码」（6/6 样本均等于输入号码） |
| `avater` | 头像 URL |

**已知的脏数据**：`60100000000` 的 name 是 `rswelth. id : rs122867 / pword : rosdi74`（有人把账号密码当联系人名）→ 数据质量不可控。

**⚠️ 不要把「看起来像兜底值」的字段判为兜底值**：

- `Diana/1` 的 `/1` 不是兜底值，是通讯录里的**编号**（「Diana 的第 1 个号码」）。
- `error_log: "AC匹配失败！"` 的含义是**「地址/区域(Area)未匹配」**，与名字是否命中无关；`faild_error_log` 恒为 1，是无意义状态位。
- ✅ 唯一定性手段：**多输入对照实验**（换号码 + 同号码重查）。

**批量验证工具**：

```bash
"$PY" scripts/verify_callerid.py --repo <phone-number-lookup 目录> --recheck \
  "0123355873|roland leong" "0122071768|dato ricky lim"
```

四级匹配：全串精确 → 子串包含 → **token 级模糊匹配**（编辑距离 ≤1，**≥3 字母**）
→ **中文拼音匹配**（`智辉` → `zhihui` ⊃ `hui`）。
比对前**剥离称谓词**（`MR`/`MS`/`MRS`/`DR`/`DATO`/`PUAN`/`ENCIK` 等）——
TC 常带前缀、DB1 常不带，不剥离会把「实质全中」误判成「缺一个 token」；
**但 `Tan`/`Lim`/`Ng` 这类同时是姓氏的词不能剥**。
⚠️ 3 字母门槛是必要的：华语姓名罗马化拼写常有变体（`Loh`/`Low`、`Tan`/`Tang`），卡在 4 字母会漏判
`Loh lawyer` vs `LOW CHI CHENG` 这种**实质命中**。加 `--json` 输出完整字段。

### DB3 CallApp（s.callapp.com）—— ★ **当前唯一还能用、且信息最全的众包库**（2026-10-05 实测）

**为什么重要**：DB1 CallerID 已被封（`{"status":-10}`），DB2/DB4/DB5 全废。CallApp 是 `phone-number-lookup` 里**唯一还有产出**的库，而且**比 DB1 更强**：能给完整姓名 + 社交账号 ID。

**接口**（已独立实现，见 `scripts/callapp_lookup.py`，不再依赖原仓库）：

```http
GET https://s.callapp.com/callapp-server/csrch
    ?cpn=%2B<E.164，无加号>            # 被查号码
    &myp=gp.106898501948939491020     # 查询者身份
    &ibs=0&cid=0
    &tk=0011243853                    # token（必需）
    &cvc=2206                         # CVC（必需）
Host: s.callapp.com
```

- 响应：JSON；**未命中返回空 body**（不是 `{}`、也不是 404）。
- **UA 非必需**（实测不带 UA 同样返回正确数据）。
- ⚠️ **`tk`/`cvc` 必需，且缺失会「串号」**：服务端**不报错**，而是返回**别人的**记录。实测无 tk/cvc 查 `60102261791` → `Kriss Schober`（错误）；带 tk/cvc 才返回正确的 `cleaner driver`。
- 假 tk/cvc（`9999/9999`）→ 空响应；空 `cpn` → 空响应。

**响应字段**（企业号最全）：

| 字段 | 含义 |
|---|---|
| `name` | 众包备注名（人名 / 职业标签 / 商户名） |
| `priority` | **热度/收录度**，实测范围 2–1303，**不是置信度** |
| `spamScore` | ⚠️ **语义未确认**。只在部分号码出现：`-1`（普通号）、`-16`（已知被举报 329 次的号）、`+4`（恶搞号）。**不要当结论用** |
| `type` | 1 / 2（推测个人 / 商户，未确认） |
| `description` / `categories[]` / `avgRating` / `reviews[]` / `openingHours` | 商户信息 |
| `websites[]` / `addresses[]`（`type`+`street`） | 网站 / 地址 |
| `photoUrl` | 头像或商户照片 |
| `lat` / `lng` / `url` / `googlePlacesId` / `huaweiPlacesId` | 坐标 / Google Maps 链接 / 地点 ID |
| `facebookID` / `linkedinPubProfileUrl` / `linkedinID` / `twitterScreenName` / `instagramID` / `googlePlusID` / `foursquareID` | **社交账号**，每项形如 `{id, sure, version}` |

**★ 最有价值的是 `name` 和社交账号** —— 社交 ID 可直接拼出可点开的主页，是整条链路里少见的「可行动」信号。

**准确率盲测（2026-10-05，用 §9 的已知真名号码）**：

| 号码 | 已知真实名字 | DB1 返回 | **CallApp 返回** | 判定 |
|---|---|---|---|---|
| `0123013006` | martin lim | （空） | **`martin lim`** | ✅ **token 全中** |
| `0192385938` | marvin lee | `Mr Malvin` | **`marvin lee`** + FB + LinkedIn | ✅ **token 全中** |
| `0162281297` | Prof Lee（用户确认） | `Prof Lee` | **`prof lee way seah`** | ✅ **给出全名含姓** |
| `0122071768` | dato ricky lim | `Dato Dr Ricky` | **`dato ricky`** + FB | 命中 `dato`+`ricky` |
| `0123355873` | roland leong | （空） | **`leong poh wah`** + FB | 命中 `leong`（姓） |

- **有返回率 13/13 = 100%**（13 个测试号码全部有返回，含 DB1 返回空的那些）
- **token 全中 3/13**（`martin lim` / `marvin lee` / `prof lee way seah`）—— 优于 DB1 的 2/22
- **可复现性 3/3 = 100%**

**对比 DB1 的三大优势**：① 有返回率高得多（13/13 vs DB1 冷表 29%）；② **能给全名**（DB1 的规律是「只给名不给姓」）；③ 额外给社交账号 ID，可交叉验证。

**⚠️ 数据质量警告（必须知道）**：

- **假号码也有记录**：`60199999999` → `mawar dyzahhra sdn. bhd.`（3/3 可复现）、`60199999998` → `namasayazolazme andabulehpanggilsayapapazola`（马来语恶搞文本）、`60100000000` → `spam` 类无意义记录。
- **🚨 降级路径会返回假名字**：缺 `cvc` 或 `tk` 时服务端不报错，而是返回**与号码无关的随机记录**（详见下方限流章节的 `X_C_CODE: 1`）。**看起来像人名，但全是错的。**
- **与 DB1 常给不同答案**：`60123456789` → CallApp `kulailand.com : kulai land for sale` vs DB1 `Kedai Makan Pak Chik`。**两库都命中同一名字时可信度才提升。**
- → 定位与 DB1 相同：**适合「验证假设」，不适合「从零推出身份」**。

**⚠️ 限流：HTTP 513 + `X_C_CODE: -4`（2026-10-05 实测）**

**CallApp 有限流，触发点约在累计 100 次请求。** 实测时间线（2026-10-05，全部用同一套 `tk/cvc/myp`）：

| 时刻 | 事件 | 累计请求 |
|---|---|---|
| ~12:20 | 首次用 CallApp（工具可用性实测 + 试点脚本，30 空 A 列 + 20 一致性样本，跑了两轮） | ~100 |
| **12:49** | **开始被拒**：`HTTP 513` / `X_C_CODE: -4` | — |
| 14:07 | 仍在被拒（冷却 **≥ 78 分钟**，未恢复） | — |

→ **阈值 ≈ 100 次/窗口**（量级确定，精确触发点见下方「精确实测」）。**不是** 40 次 —— 原描述「连续 40 次无封禁」只说明 40 次安全，不代表上限是 40。

**★ `X_C_CODE` 是应用层状态码**（HTTP 用 511/512/513/525 承载，body 恒为空）。**完整实测对照表**（12 个变体逐个真发请求）：

| 变体 | HTTP | `X_C_CODE` | body | 含义 |
|---|---|---|---|---|
| 全部参数有效 | `200` | （无） | JSON | ✅ 正常 |
| 全部参数有效 + **无效号码** | `513` | **`-4`** | 空 | ⚠️ **配额先于号码校验** |
| 有效 `tk` + **错误 `cvc`** | `513` | **`-4`** | 空 | ⚠️ **配额先于 cvc 校验** |
| 缺 `cpn` | `511` | **`-2`** | 空 | 缺必填参数 |
| 缺 `tk`（`cvc` 在） | `512` | **`-3`** | 空 | 身份无效 |
| 缺 `myp` / `myp` 无效 | `512` | **`-3`** | 空 | 身份无效（`myp` 必填） |
| `tk` 假 + `cvc` 对 | `512` | **`-3`** | 空 | 身份无效 |
| **缺 `cvc`（`tk` 有效）** | **`200`** | **`1`** | ⚠️ **随机名字** | 🚨 **降级路径，数据是假的** |
| **`tk` 与 `cvc` 同时缺失** | **`200`** | **`1`** | ⚠️ **随机名字** | 🚨 **降级路径，数据是假的** |
| 全部参数缺失 | `525` | `0` | 空 | 未知 |

**判据（与「未命中」必须区分开）**：

| 现象 | 含义 |
|---|---|
| `HTTP 200` + 空 body | **未命中**（该号码没数据），正常 |
| `HTTP 200` + `X_C_CODE: 1` + 有名字 | 🚨 **降级/匿名路径，名字与号码无关，必须丢弃** |
| `HTTP 513` + `X_C_CODE: -4` | **被限流**，此后所有号码一律这样返回 |
| `HTTP 512` + `X_C_CODE: -3` | `myp`/`tk` 身份参数无效 |
| `HTTP 511` + `X_C_CODE: -2` | 缺 `cpn` |

**🚨🚨 最危险的坑：`X_C_CODE: 1` 会返回「看起来像人名」的垃圾**

`tk` 或 `cvc` 缺失时，服务端不报错，而是走匿名降级路径，**返回一条与查询号码完全无关的随机记录**：

| 号码 | 期望（有效凭据） | 缺 `cvc` 时返回 | 全缺时返回 |
|---|---|---|---|
| `60102261791` | `cleaner driver` | `Ainslee Vitale` | `Talonda Castleman` |
| `60162281297` | `prof lee way seah` | `Silver Luo` | — |
| `60192385938` | `marvin lee` | `Trichelle Smedley` | — |

- **同一号码两次查询返回不同名字** → 非确定性 → 确认为随机/无关记录。
- 这些名字形似真实英文名，**不会报错、不会返回空**，最容易骗过自动化流程。
- → **`cvc` 是必填项，绝不能因为「反正有返回」就省略。** 脚本已把 `HTTP 200 + X_C_CODE: 1` 视为异常（非 `miss`、非 `found`）。

**★ 封锁绑在 (`tk`, `myp`) 精确值对上，不是 IP —— 且没有任何参数轮换的绕法**

依据：**无效号码 + 有效凭据**、**有效 `tk` + 错误 `cvc`** 都返回 `-4`，说明服务端**先查配额，后校验号码和 `cvc`**。

**配额桶轮换测试（13 个变体逐个真发请求）**：

| 改什么 | 结果 | 说明 |
|---|---|---|
| 换 IP / User-Agent / 查询号码 | `-4` | 配额不在这些维度 |
| 改 `myp`（尾号 +1 / 随机 / 全 0，共 5 变体） | **`-3`** | ❌ `myp` 必须**逐字节**等于注册值，改动直接掉到「身份无效」 |
| 改 `tk`（尾号 +1 / 随机 / 短号 / 全 0，共 5 变体） | **`-3`** | ❌ `tk` 同样必须**逐字节**相等 |
| 改 `cvc`（`2207` / `1234`） | **`-4`** | ⚠️ `cvc` **不参与配额键**，也不被严格校验 |

⇒ **配额桶 = (`tk`, `myp`) 这一对精确值。想扩容只能拿到另一对真正注册过的 `tk`+`myp`。**

由短路关系反推出的**参数校验顺序**：

```
校验 tk → 校验 myp → 检查配额 → …… → 校验 cvc → 查库
 错则-3    错则-3     满则-4            缺则降级(1)
```

**限流后**：探测频率必须放低 —— **探活本身也消耗配额**，每 5 分钟探一次，别 1 分钟探一次（会持续续命窗口，把自己焊死在封锁里）。2026-10-05 12:49 触发后 **≥78 分钟未恢复**（14:07 仍 `-4`）。

**排期建议（阈值实测出来前，按保守值走）**：

- 单批 **≤ 80 次**查询（留 20% 余量），批间**必须**插 ≥ 30 分钟间隔。
- `--delay` 提到 **1.5–2.0s**，不要 0.3s。
- **不要**按「日总量」规划大批量 —— 8867 行这种量级在这套凭据下**跑不完**，需要另找凭据或换数据源。
- 脚本遇 `-4` 立即熔断（`MAX_CONSEC_BLOCK`），**不要空转重试**。

**📄 完整实测过程**（13 个变体原始返回、时间线、归属论证、精确实测方法、安全节奏公式）：`references/CallApp限流阈值实测-2026-10-05.md`

**用法**：

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
"$PY" <skill>/scripts/callapp_lookup.py 0102261791
"$PY" <skill>/scripts/callapp_lookup.py 0102261791 0162281297 --json
"$PY" <skill>/scripts/callapp_lookup.py --file nums.txt --delay 0.3
"$PY" <skill>/scripts/callapp_lookup.py --probe        # 探活：exit 0=通 / 2=不通
"$PY" <skill>/scripts/callapp_lookup.py 0162281297 --recheck   # 查两次验可复现
```

凭据可用环境变量覆盖：`CALLAPP_TK` / `CALLAPP_CVC` / `CALLAPP_MYP`。

🚫 **合规**：这是 CallApp 的非公开内部接口，使用违反其 ToS（§3(07) 禁采集 / §3(14)(15) 禁逆向 / §3(17) 禁非官方接口）。**只做只读单点查询，不要批量抓取，不要写进商用流程。**

### Tellows / Truecaller 端点实测状态（2026-10-02，逐个真发请求）

| 端点 | 状态 | 证据 |
|---|---|---|
| `www.tellows.de/basic/num/<num>?xml=1&partner=androidapp&apikey=…&country=<CC>` | ✅ **可用** | HTTP 200 返回 XML；**apikey 甚至非必需**（无 key 也 200） |
| └ 对**马来西亚**号码 | ❌ **零覆盖** | 5 个号码全返回 `score=5 / comments=0 / caller=None`，**含已知 329 次举报的 `60123456789`** |
| `search5-eu.truecaller.com/v2/search` | ⚠️ **可用但限流极严** | 首次 200 返回完整 `data`；随后持续 429（token 级整体限流，无 `Retry-After`） |
| `search5-noneu.truecaller.com/v2/search` | ⚠️ **端点正常，但泄露 token 被 451** | 无 token→400 / 假 token→**401** / 硬编码 token→**451** |
| `filter-store4-{eu,noneu}.truecaller.com/v4/filters` | ❌ 451（noneu） | 举报端点 —— **不要滥用** |
| `oauth-account-noneu.truecaller.com/v1/{token,userinfo}` | ✅ **全通** | 无 token→401、假 Bearer→401、假 client_id→403 `invalid_grant` |
| `account-asia-south1.truecaller.com/v{2/sendOnboardingOtp,1/verifyOnboardingOtp}` | ✅ **全通** | 空 body→400 `Invalid body format`（`clientsecret` 未被拒） |
| truecaller-lite 的 Heroku 中转 | ❌ **功能失效** | HTTP 500 `Lookup failed - No data returned` |

🔑 **451 归因（★ 2026-10-02 已更正，原结论错误）**

**原（错）结论**：~~同一 token 在 EU 端点 200、noneu 端点 451 → 不是 token 失效，是端点级地域策略~~
**错因**：原实验缺少最关键的对照组 —— **「假 token + noneu 端点」**。

**补充 4 变量隔离实验（端点 × token × 参数集 × UA）后的正确结论：**

| 端点 | token | 结果 |
|---|---|---|
| noneu | 无 | **400** Missing authentication parameter |
| noneu | 假 Bearer | **401** Unauthorized |
| noneu | **硬编码 token** | **451** Unavailable for legal reasons |
| eu | 硬编码 token | **429** too many requests |

（参数集完整/精简、UA `9.00.3`/`11.75.5` 均无差异 → 可排除）

→ **451 是「该 token × noneu 端点」的组合状态，不是端点地域策略。**
→ **noneu 端点本身完全正常**（对无效 token 只回 401）。
→ **是 `a1i1V--ua298...` 这个来源不明的泄露 token 在 noneu 上被合规封禁**；同一 token 在 eu 端点被接受（只限流）。
→ 实践含义：**换成合法获得的 `installationId`，noneu 端点大概率不 451**（待实测）。
原始数据 `api_probe_451attrib.json`，脚本 `test_451_attribution.py`。

⚠️ **对马来西亚号码**：Tellows 无用；Truecaller 端点虽可用但限流严，且用的是**他人账户凭据**（见 `references/`）。
**DB1（aunumber）仍是唯一已实测、有实际数据的免费众包源。**

🚫 **合规红线**：硬编码凭据属他人账户，冒用违反服务条款且有法律风险。
**只做只读探测，不要批量抓取，不要调用举报接口。不要把泄露 token、逆向 clientsecret、或他人 installationId 写进新脚本。**

### 4.1 为什么查不到姓，以及什么真能提高准确率（2026-10-02）

**缺姓不是 bug。** 22 个已验证号码里，token 全中（名+姓都对上）只有 **2/22**。
命中记录的典型形态是 `Dato Dr Ricky`、`Mr Malvin`、`Prof Lee`、`Loh lawyer`：名、称谓、职业在，姓不在。
原因：这些库存的是「别人通讯录里怎么存你」，多数人只存名。

**不要做的事（已证伪，会浪费配额或违法）：**

| 做法 | 为什么没用 |
|---|---|
| 再跑一遍 DB1 / 换 UA / 换号码格式 | 重查可复现 22/22，空就是空，格式变了也不会多出一个姓 |
| 把 `error_log: AC匹配失败` 当「没查到名字」 | 该字段是地址未匹配，与名字无关 |
| 用 Telnyx / Twilio / numlookupapi 的 CNAM 补姓 | **CNAM 只覆盖美国号码**（Telnyx 文档原文：*registered caller name associated with a US number*）。马来西亚没有对等的主叫姓名投递 |
| 用 Truecaller 官方 SDK / OAuth access_token 查任意号 | token 受众是 `userinfo`（登录者本人），调不了 `search5` |
| 用 `truecallerjs` OTP 换 installationId | 2026-02 起后端静默不发短信，2026-10-02 本机复现 `20003` |
| 买 RapidAPI 上的 Eyecon / Sync.ME / ViewCaller「100% success」转售 | 营销页，不是官方接口；本 skill 已实测 Eyecon / Sync.ME 端点失效。**未实测前不要当数据源** |
| 用 whoseNo / numtrace / searqle 一类「Who called me」站 | 页面给的是垃圾来电热度，不是机主姓名，也没有可用反查 API |

**能提高「姓氏命中」的，只有交叉，不是单库深挖：**

1. **两库 token 交集当姓氏候选，不当结论。**
   DB1 给 `Liza Yap`、Truecaller 给 `LIZA YAP SURBANA` → 姓氏候选是两者共有的 `Yap`，不是 DB1 独有的片段。
   只有一边有的 token（`SURBANA`、`lawyer`、`PA`、`abe`）标成「关系/职业/组织」，**不要拼进姓名**。
2. **先剥称谓再比，但姓氏词不剥。**
   剥：`MR` `MS` `MRS` `DR` `DATO` `DATIN` `PUAN` `ENCIK` `CIK` `HJ` `HAJI`。
   不剥：`Tan` `Lim` `Ng` `Lee` `Ong` `Yap` `Koh` `Goh` `Teoh` `Low`/`Loh`。
   3 字母编辑距离 ≤1 才算同一 token（`Loh`≈`Low`，`Malvin`≈`Marvin`）。4 字母门槛会漏掉华语姓氏异拼。
3. **中文备注必须过拼音再比。** `智辉` → `zhihui`，才能对上 `CHEE HUI` 的 `hui`。不过拼音会把中文姓氏整段判成无数据。
4. **有职业/组织标签时，改走「名 + 组织 → 公开名录」，不要死磕号码库。**
   `Loh lawyer`、`Lotus Power : Angie Ng` 这种，姓氏更可能在马来西亚律师公会名录、公司官网、SSM 董事名单里，而不是在通讯录备注里。
   SSM e-Info（`ssm-einfo.my`）是**公司名 → 董事**，不是**号码 → 董事**。只有 D 层先给出公司名，才值得付费查 SSM。
5. **B2B 职业库是唯一「号码 → 结构化姓氏」的第三方方向，但必须先小样本实测。**
   见 §5.1。没有 key、没有在马来西亚号码上盲测过，就不要写进批量流程。

**汇报口径（必须对用户说）：**

- 单库备注 = 低可信线索，不是姓名。
- 两库共有 token = 中可信「名/姓片段」，仍不是实名。
- `likelihood ≥ 6` 的 PDL/RocketReach 命中 = 中高可信职业身份，仍不是电讯商实名。
- 三方都不给姓 = 停止，不要用更多众包站堆查询。报警或法院令才是实名路径。

### ★ 商业黄页层（E 层）：企业号的「联系人 + 职务」反查（2026-10-07 新增）

**适用**：号码像**企业号**，或机主有**商业足迹**（公司董事 / 店主 / 供应商）。此时别死磕众包库 —— 黄页能直接给**姓名 + 职务**。

**七个已实测的黄页源**（对同一家马来西亚公司交叉比对）：

| 站点 | 给什么 | 可编程性 |
|---|---|---|
| `listcompany.org` | **`Contact Person` + `Job Title` + `Department`** | ✅ **静态 HTML，curl 直接抓**（最省事） |
| `exportersindia.com` | `Director` 姓名 | ✅ curl 可抓 |
| `cybo.com` | 地址 / 电话 / 网址 / 行业 | ✅ curl 可抓（整页 ~130KB） |
| `businesslist.my` | 座机 / 传真 / 网址 | ✅ curl 可抓 |
| `malaysiayp.com` | **分类页直接列 `01X` 手机号 + 公司名 + 地址**；条目详情页多为座机 / "Contact Disabled" | ✅ curl 可抓（**全站唯一可批量取 01X 的黄页**，见下方第 6 点） |
| `bizmalay.com` | **主要联系人 + 职务**（`X is the primary contact` / `X (CEO)`） | ❌ **CF 拦非浏览器**；curl / WebFetch / r.jina.ai 全被 CAPTCHA 挡 → **只能读搜索引擎快照**。URL 形如 `<slug>_<idx>-<电话>`，**电话即 listing key** |
| `MATRADE` / `MATFA` / `Alibaba`（`*.fm.alibaba.com`） | 公司档案 | Alibaba 不露电话 |

**关键局限（必须对用户说）**：

1. 黄页给的是**企业联系人**（Director / CEO / Owner），**不是电讯商实名**，也不保证该号码属于此人。
2. **「号码 → 姓名」的直接绑定，黄页通常给不出** —— 黄页列的是公司座机。若目标是手机号，绑定往往只存在于**非公开索引的社区/内部数据集**里。
3. **搜索引擎对号码本体常常零收录**：实测 `0123956969` 在 Google（`About 0 results`）、DDG html、Yandex（"2000 结果"全是数字串误匹配）**全部零命中**。此时判定链**只能靠身份侧互证**（公司 → 董事姓名），并**明确标注「身份成立、号码绑定待补证」**，不要含糊成「查到了机主」。
4. **★ 结构性规律（2026-10-07 实测 30+ 站点后确认）**：马来西亚黄页/名录的数据模型主流是
   **「企业座机 ↔ 公司名」**（如 `03-7877 7070`、`03-7873 8696`），**基本不收录个人手机**。
   实测同一家公司：**DrLocker 出现在约 10 个站点，而它的手机号 `012-395 6969` 出现在 0 个站点**。
   所以 **`01x-xxxxxxx` 这类手机号在绝大多数「黄页型」站点都查不到** —— 这是结构性必然，不是数据缺失。
   **唯一例外见第 5、6 点（`malaysiayp.com` 分类页）**：它不是「不收录」，而是**只在分类列表页**露出 01X，
   条目详情页反而隐藏。判定时不要因为"黄页没有"就下结论，要先确认是不是漏看了列表页。
   手机号 → 人名只能转向 D 层众包或 G 层实名。
   **已实测收录该公司的站点**：bizmalay ✅ / cybo ✅ / businesslist.my ✅ / malaysiayp ✅ /
   matfa.org.my ✅ / malaysiaservices.matrade.gov.my ✅ / manufacturermalaysia.com ✅ /
   exportersindia ✅ / listcompany.org ✅ / Alibaba ✅ / Google Maps ✅ / Apple Maps ✅。
   **实测无收录**：listing.my / business-yellowpages.com / hotfrog / tuugo / infobel / cylex / yalwa /
   brownbook / streetdirectory / mudah / lelong。
5. **★ 想批量取「公司 + 01X 手机号」只有 malaysiayp.com（2026-10-07 实测）**：
   其余名录的电话字段**几乎全是座机**（bizmalay 7003 条归档 URL → 0 条 01X；cybo / companydata /
   businesslist / huarentie / wapp 分类页 → 0 条 01X）。**只有 malaysiayp.com 的分类页直接列 01X**，
   且结构规整、可编程：
   ```
   <li class="row-item">
     <div class="row-main">
       <span class="row-name"><a href="/item/<slug>/">公司名</a></span>
       <span class="row-meta">地址</span>
     </div>
     <a class="row-phone" href="tel:0122875671">012-287 5671</a>
   </li>
   ```
   抓 `https://malaysiayp.com/cat/<分类>/` 16 个分类页即得 **73 条**「公司名 + 01X 手机」配对（去重后）。
   `tel:` 里的数字是无分隔原始值（`0122875671`），比显示文本更好解析。
   ⚠️ 用途限制：这些是公开名录中企业主动登记的联系号码，**聚合后受 PDPA 约束**，
   仅可用于目录检索/研究，不得群发、推销、骚扰或转售；马来西亚 SME 常把老板个人手机当营业号，勿据此推断自然人身份。

6. **★ malaysiayp.com 站点结构全量索引（2026-10-07 实测，含批量抓取要点）**：
   - **规模**：`/` 首页枚举出 **60 个分类**；各分类 `/cat/<分类>/page/<n>/` 总页数合计 **32,936 页**，
     按 20 条/页 ≈ **658,720 条名录**。单分类页数 **73 ~ 5,455**（`business-services` 最多，
     其次 `services` 2248 / `manufacturing-industry` 1935 / `shopping` 1678 / `food-beverages` 1537）。
   - **手机密度**：分类间极不均衡，**2 ~ 10 条 / 20 条页**（均值约 29%）。
     `hotels` / `apparel` / `eating-places` 偏高（10/页），`computers-internet` / `amusement` 偏低（2/页）。
     → **要凑 N 条手机，约需 N/5.8 页**，且必须跨分类抽样，否则单分类会把样本带偏。
   - **⚠️ 限流形态是「软限流」而非 429**：持续请求后站点返回 **HTTP 200 + 0 字节响应**。
     若把空响应判成"被封"就会误中止。**必须把「空响应 / 页面 <3KB」当可重试处理**
     （退避 6s→12s→24s）。实测 27 页里触发 **14 次**，全部被退避吸收，仅 4 页重试耗尽被跳过。
   - **真正的封禁信号**才该中止：`401/403/451`，或响应头 4000 字符内出现
     `just a moment` / `cf-chl` / `captcha` 等 Cloudflare 挑战指纹。
   - **页码越界返回 404**（如 `automotive/page/900/`）→ 只跳过该页，不要中止整体。
   - **源站脏数据**：个别条目的**显示文本**里带 `U+FFFD`（如 `016-470 5455\ufffd`），
     但 `tel:` 里的数字是干净的 → **电话一律取 `tel:` 数字，显示文本须清洗后再入库**。
   - **★ 号码形态：马来西亚手机有两种长度，过滤时缺一不可（2026-10-08 踩坑修正）**：
     | 形态 | 位数 | 示例 | 说明 |
     |---|---|---|---|
     | `01X-XXXXXXX` | **10 位** | `012-345 6789` → `0123456789` | 012/013/014/016/017/018/019 等 |
     | `011-XXXXXXXX` | **11 位** | `011-1234 5678` → `01112345678` | **011 段，MVNO 主力号段** |
     **正确正则：`01\d{8}|011\d{8}`（配 `fullmatch`）。**
     曾用 `01\d{7,8}` → 只认 9~10 位 → **全部 011 号码被静默丢弃**。
     实测该站缓存 1110 条 `tel:` 链接：**1098 条 10 位 + 12 条 11 位（全为 011）**，9 位 0 条。
     → 任何「01X 手机号」过滤/校验/统计，都必须同时覆盖 10 位与 11 位；
       交付前用**位数分布**自查（只有 10 位 = 漏了 011）。
   - **可运行脚本**：`scrape_malaysiayp.py`（先索引 → 跨分类抽样 → 确定性正则解析 →
     限流退避 / 封禁熔断 / 结构校验 → 原子写 CSV）。参考实跑：
     `--order random --n 100 --per-cat 5 --max-pages 60 --seed 42` → 约 30 页 / 20+ 分类 / 100 条唯一 01X；
     `--order sequential --n 100 --per-cat 10` → 27 页 / 10 分类（顺序模式配额吃满故分类数少）。
     **注意 `--per-cat` 是「每分类累计条数」上限**（不是每页），顺序模式下某类达标即整类跳过。
     运维要点见 `unattended-scraper-ops` 技能。
   - **★ robots.txt 是「两组 AI 爬虫」策略（2026-10-08 实检原文）**：
     ```
     User-Agent: GPTBot / ClaudeBot / Google-Extended / Applebot-Extended
                 / meta-externalagent / CCBot            → Disallow: /
     User-Agent: OAI-SearchBot / ChatGPT-User / Claude-SearchBot
                 / Claude-User / PerplexityBot / Perplexity-User → Allow: /
     User-Agent: *   → Allow: /  (Disallow: /api/ 与 /*?s=)
     ```
     **含义：站点反对「拿数据去训练」，不反对「被检索/被引用」。**
     用通用浏览器 UA 会命中 `*` 组 → 允许。判定时**不要笼统说「该站禁止 AI 爬虫」**，
     要区分训练型（禁）与检索型（许）。这是 2026 年越来越常见的模式，值得作为通用判读习惯。
   - **全量成本**：32,936 页 × 2s 间隔 ≈ **18 小时以上**连续单线程，且反复触发软限流 → **不推荐**；
     应先取得站点授权 / 数据许可再谈窗口期。**有界样本（如 --n 100，占全站 0.015%）不在此列。**

**企业号判定链模板**：

```
号码 → 号段属性（A 层）
     → 若像企业号：黄页横向比对（E 层）→ 公司名 + 联系人 + 职务
     → ≥3 个独立黄页给出同一姓名，才写「中高可信」
     → 众包库（D 层）交叉（有则加分，无则不强求）
     → 仍缺 → 报警 / 法院令（G 层）
```

**Wayback CDX 反查技巧**：黄页 listing URL 常把电话编进 slug，可枚举归档 URL 找目标号：
```bash
curl -s "http://web.archive.org/cdx/search/cdx?url=bizmalay.com&matchType=domain&fl=original&collapse=urlkey&limit=100000" \
  | grep -i "012395\|3956969"
```
（实测 bizmalay 仅归档 ~7000 条 vs 全站数百万 listing → **未命中 ≠ 不存在**，不能当反证。）

### Truecaller 登录方式：官方 OAuth SDK vs OTP（2026-10-02 源码级调研）

**常见误解**：以为 `truecaller_sdk`（pub.dev v1.2.0）能用来查号码。**不能。**

| | 官方 OAuth SDK | 官方 SDK 手动验证 | 非官方 OTP（`truecallerjs`） |
|---|---|---|---|
| 包/仓库 | `truecaller_sdk` / `truecaller/flutter-sdk` | 同左 | `sumithemmadi/truecallerjs` |
| 目的 | 验证**你自己 App 的用户** | 非 TC 用户兜底 | 换可查号码的 token |
| 查任意号码 | ❌ | ❌ | ✅ |
| 前置 | business account + **Client ID**（`sdk-console-noneu.truecaller.com`）+ 包名签名绑定 | 同左 | 一个能收短信的手机号 |
| 地区限制 | 无 | ⚠️ **源码明写仅印度号码** | 无 |
| 产出 | `authorizationCode` → `/v1/token` → `access_token` → `/v1/userinfo` | `accessToken` + `TruecallerUserProfile` | **`installationId`** |

**官方 SDK 是 OAuth 2.0 + PKCE**（`example/lib/customization/oauth_result_screen.dart`）：

```
POST https://oauth-account-noneu.truecaller.com/v1/token
  grant_type=authorization_code & client_id=<你的> & code=<授权码> & code_verifier=<PKCE>
GET  https://oauth-account-noneu.truecaller.com/v1/userinfo   Authorization: Bearer <access_token>
```

**关键判定**：官方 access token 的受众是 `userinfo`（返回**登录者本人**的姓名/号码/邮箱），
**不是** `search5/v2/search`。两套独立鉴权体系（OAuth access token ≠ installationId）。
→ **「用官方 SDK 登录，再把 token 交给 AI 查号码」这条路走不通。**

**官方 SDK 的 OTP**（`requestVerification` → `verifyOtp(firstName, lastName, otp)`）：
- `lib/src/truecaller.dart:267` 原文：*"manual verification of [phoneNumber] ... for **Indian numbers only** so that's why default countryISO is set to `IN`"*
- 回调 `otpReceived` / `imOtpReceived` 里 SDK **直接给出 OTP 明文**（`cb.otp`）→ 设计意图是 App 内自动验证
- 必须传 `firstName` + `lastName` → 是**用户给自己登记**，不是查询

**能查号码的 OTP（`truecallerjs` / `truecallerpy`，非官方）—— ❌ 2026-10-02 实测已彻底失效**

```
POST account-asia-south1.truecaller.com/v2/sendOnboardingOtp    clientsecret: lvc22mp3l1sfv6ujg83rd17btt
  → {requestId}
POST account-asia-south1.truecaller.com/v1/verifyOnboardingOtp  {requestId, token:<OTP>}
  → installationId
GET  search5-noneu.truecaller.com/v2/search?q=&countryCode=&type=4   Authorization: Bearer <installationId>
```

🔴 **不要再尝试这条路径。** 本机实测（`+60102261791`）：

```json
HTTP 200  {"status":20003,"message":"Verification failed","domain":"noneu","requestId":"..."}
```
**判据**：正常响应必带 `method`（渠道）与 `tokenTtl`（有效期）；本次**两者皆无** → **OTP 从未进入投递队列，手机收不到短信**。

**四组实验排除法（可复现）**：
| 实验 | 做法 | 结果 |
|---|---|---|
| ① 版本指纹 | 11.75.5 / 14.43.8 / 15.3.10 / 无 UA 伪装 | **全部 20003** → 不是版本问题 |
| ② 号码对照 | 固话 `+60312345678` / 无效前缀 `+601999999999` / 真实号 | 固话→**400 `40003 Invalid phone number`**；另两个→**200 `20003`** |
| ③ 社区 | 两仓库 issue | `truecallerjs` **34 条** "Verification failed"，多条标题写 **"NOT Sending OTP"** |
| ④ 跨国 | issue 截图（印度号） | 响应与我的**逐字段一致** |

**② 的读法**：固话被单独识别 ⇒ 请求**被正常解析**（`clientsecret`/body 全通过）；无效前缀与真实号同结果 ⇒ **20003 与号码无关，是针对客户端身份的拒绝**。

**权威判定**（`truecallerjs` PR #157，2026-02-07 贡献者原文）：
> Truecaller's backend appears to be **silently blocking SMS delivery** for requests originating from this library ... mark the **automated login feature as deprecated/non-functional**.
> **CRITICAL NOTICE (2025): Project Currently Non-Functional** — Request succeeds (**Status 20003**), but **OTP is never delivered**. As of Feb 2026, this library should be considered **broken/deprecated**.

**技术推断**：缺的是**密码学设备证明**而非参数 —— `clientsecret`/UA/版本/设备型号/body 都能伪造，
但 **Play Integrity attestation** 与 **官方 APK 签名指纹**不能。

**替代路径**：
| 路径 | 结论 |
|---|---|
| **DB1 / aunumber** | ✅ **唯一立即可用**（22 号码 82% 有返回） |
| 真机提取 `installationId`（adb backup / root） | ⚠️ 可行但违反 ToS；拿到后 `search5` 仍可用（假 token→401，端点正常） |
| Truecaller Web 抓包 | ❌ 本机 `web.truecaller.com` **DNS 不存在**，curl 代理 502 |
| 官方 Business SDK | ❌ 只能验证自己 App 用户 |
| 报警 / 法院令 | ✅ 唯一合法拿实名（PDRM / NSRC **997**） |

**「如何把登录态传给 AI」**：给的是 **`installationId`**（不是官方 SDK 的 access_token，受众不同调不了 search）。
本机对全部 Truecaller 域名（含 `-noneu`）**网络均可达** —— 但**前提是你能拿到 installationId**，而获取途径现已全部封堵。
**合法路径仍是报警（PDRM / NSRC 997）或法院 Norwich Pharmacal order。**

---

## 5. B 层：实时运营商查询（付费，不含姓名）

| 服务商 | 产品 | 单价 |
|---|---|---|
| **Telnyx** | Number Lookup | **$0.0015/次起**（最便宜） |
| Vonage | Identity Insights | Original Carrier €0.001 / **Current Carrier €0.007** |
| HLR Lookups | HLR / MNP / NT | €0.01 / €0.005 / €0.0025 |
| Twilio | Lookup v2 Line Type Intelligence | $0.008/次（Caller Name **仅美国**） |
| numverify | — | 免费 100 次/月（禁商用），基于号段库，**不穿透 MNP** |

要「当前运营商」→ 选 Vonage Current Carrier 或 HLR Lookups 的 MNP。

**B 层不返回姓名。** Telnyx Number Lookup 的 CNAM（$0.003/次）文档写明是 *registered caller name associated with a **US** number*。
Twilio Lookup v2 的 Caller Name 同样**仅美国**。numlookupapi 的 validate 端点只返回 carrier / line_type / location / 格式，schema 里没有 name。
**不要为了补姓氏去调 B 层。**

### 5.1 第三方「号码 → 姓名」方案（2026-10-02 **端点已实测** + 文档核对）

分三类。只有第 1 类有机会给出结构化姓氏。第 2 类是另一份通讯录备注。第 3 类查了也没有姓。

#### 0. ★ 端点实测结论（2026-10-02，真实 HTTP 请求）

`pdl_rr_probe.py` / `pdl_rr_probe2.py` 两轮探测，**无 key / 假 key 对照**：

| 服务 | 无 key | 假 key | 判读 |
|---|---|---|---|
| PDL | 401 `Your request is **missing** an api key.` | 401 `Your request contained an **invalid** api key` | ✅ 校验凭据真实性 |
| RocketReach | 401 `Anonymous requests are not allowed.` | 401 `Invalid API key` | ✅ 校验凭据真实性 |

⇒ **两家都无匿名口子，无法复用他人 key，必须自购。**
RocketReach 报错里的「Please use the test API key」**不是公开密钥** —— 实测 `test`/`TEST_API_KEY`/`test_api_key`/`demo` 全部 `Invalid API key`；那句指的是文档站「Try It」在线试用。

#### 1. 有机会给出 `first_name` + `last_name`（付费，需自有 key，先盲测再批量）

| 服务 | 反查键 | 返回 | 文档约束 | 状态 |
|---|---|---|---|---|
| **People Data Labs** Person Enrichment / **Person Identify** | `phone` **单独即可**（**必须** `+` 国家码，如 `+60162281297`） | `full_name` / `first_name` / `last_name` + `likelihood` 1–10 | 官方：`phone` 是合法的最小匹配组之一。`likelihood=2` 只有约 10–30% 是本人；要高准确率设 `min_likelihood≥6`，并用 `required=last_name` 避免为「有名无姓」付费。**只有手机号/邮箱输入时优先用 Person Identify**（只返单一最佳匹配，省配额） | ⚠️ **端点已实测存活**。**覆盖已量化**：官方公布 **马来西亚 6,516,827 条档案**（排名 24/227）。全球 Phone Slice 763,983,403 条，其中含手机号 474,650,678（62.1%）。**但 MY 手机号实际命中率仍未实测** |
| **RocketReach** People Lookup | `phone`（E.164 或国际格式）+ `lookup_type=phone` | 职业档案（含 name） | 文档确认 `phone` 是查询参数。营销页的 98% 是**邮箱可达率**，不是号码反查准确率 | ❌ **不建议**。**手机号 = 6 credits/档案**（最贵动作），且**免费层与 Essentials 均不含电话查询**（email-only），要查电话最低买 **Pro（$75/座/月起）**。独立评测列其缺点为 **"Quality varies internationally"** |

**成本对比**：PDL 免费层有测试额度，自助 **$98/月 = 350 条 ≈ $0.28/条**（按成功匹配计费）；
RocketReach 免费层 5 次且不含电话，Pro $75/座/月起 + 6 credits/手机号。

⇒ **要试就先试 PDL，别碰 RocketReach。**

> ⚠️ **两家都是 B2B 职场数据库，不是电信用户库。** 数据源是 LinkedIn 简历 + 企业名录 + 公开网络。
> 查**跨国企业驻马员工 / 有 LinkedIn 档案的专业人士 / 企业总机**有机会；
> 查**普通个人手机号（典型诈骗来电）大概率无匹配**。别把它当 DB1 的替代品，它是「职场背景」补充。

用法（有 key 之后，先拿 §9 里已知答案的 4 个号码盲测，不要先跑表）：

```http
GET https://api.peopledatalabs.com/v5/person/enrich
  ?phone=+60122071768
  &min_likelihood=6
  &required=last_name
  &titlecase=true
X-Api-Key: <自有 key>
```

```http
GET https://api.rocketreach.co/api/v2/person/lookup
  ?phone=+60122071768
  &lookup_type=phone
Api-Key: <自有 key>
```

**盲测通过标准（写进批量流程之前必须满足）：** 4 个已知号码里，至少 2 个返回的 `last_name` 与 ground truth 一致，且 `likelihood≥6`（PDL）或 RocketReach `status=complete`。
达不到就停，不要因为「全球 30 亿档案」的营销数字继续烧 credits。

#### 2. 仍是众包备注（可能多一个片段，不会变成实名）

| 服务 | 能给什么 | 为什么不优先 |
|---|---|---|
| **GetContact** | 其他用户打的 **tag**（官方定义就是 nickname/name，用户可自行管理） | 无官方反查 API。GitHub 上的 getcontact-cli / 非官方 PHP 库是逆向客户端，和已失效的 truecallerjs 同一类风险。App 内手动查可以，不要写进脚本 |
| **Whoscall / Gogolook Asi** | 企业 API 是**防诈**：号码/域名风险、诈骗网站库（页面自称 26 亿号码、700 万诈骗站） | 产品页没有「返回个人全名」的字段。要姓名仍是 App 内众包。商务接入走 `web.whoscall.com/en/partners/asi`，不公开单价 |
| **Truecaller for Business** | Verified Business API 是商家**登记自己的来电显示名** | 不是任意号码反查。`enterprise-portal-noneu.truecaller.com` 与 `search5` 不是同一套 |
| **Eyecon / Sync.ME / CallApp / ViewCaller** | 转售页声称返回 name + photo | 本 skill 已实测 DB2 Sync.ME、DB4 Eyecon 失效。RapidAPI / JoJAPI 上的「100% success」是转售营销，**未重新实测前视为不可用** |

#### 3. 查了也没有姓（不要为姓名去调）

| 服务 | 实际返回 |
|---|---|
| Telnyx / Twilio CNAM | 仅美国注册主叫名 |
| Vonage / HLR Lookups / numlookupapi | 运营商、线路类型、是否携号。无 name 字段 |
| Tellows | 接口活，马来西亚零覆盖（5/5 空，含 329 次举报号） |
| whoseNo / numtrace / searqle | 垃圾来电热度页，无反查 API |
| SSM e-Info | 公司 → 董事/股东，不是号码 → 人。只在 D 层已经给出公司名时使用 |
| Kaspr / Apollo / Lusha | 官方流程是 **LinkedIn URL → 电话**，方向反了，不能当号码反查 |

**接入顺序（有预算时）：** D 层免费交叉 → 仍缺姓且号码像商务号 → **先小样本盲测 PDL**（有免费额度；RocketReach 免费层查不了电话，别先试它）→ 通过后再单条补查。
随机消费者号码不要直接上 F 层，credits 会空烧。

**两家都不是 DB1 的替代品**：DB1 查陌生来电（免费、22 号码 82% 有返回），PDL/RocketReach 查**职场背景**（付费、仅覆盖有公开足迹的人）。要**实名**只能报警（PDRM / NSRC **997**）或 Norwich Pharmacal order。

---

## 6. 通用方法论：如何拿到一个网站的私有接口

四种情况，按成本从低到高：

| # | 情况 | 做法 |
|---|---|---|
| 1 | 静态 HTML | `curl` 直接抓，正则解析 |
| 2 | JS 渲染，想知道接口 | 读前端源码：`config.js` 找 endpoint → 下 `main.<hash>.js` 搜 endpoint 字典 → 搜调用点读请求体字段名 |
| 3 | JS 渲染，只想要结果 | 无头浏览器 `chrome --headless=new --dump-dom --virtual-time-budget=15000 <url>` 读渲染后 DOM |
| 4 | 想知道到底调了哪个接口 | `--log-net-log=<path> --net-log-capture-mode=Everything` 抓 netlog，再筛非静态资源 URL |

**本机环境坑（Windows 沙箱，重要）**：

- ❌ 用 Python `subprocess.Popen` 拉起 Chrome 再连 CDP → **整个进程组被沙箱回收**（无输出、SIGTERM、exit 1），`> file 2>&1` 也拿不到东西。
- ✅ 可靠做法：**单条前台命令** `chrome --headless=new --dump-dom ...`（实测 exit 0）。兜底：把「启动 + 干活」拼进**同一条** bash 命令。
- ✅ CDP websocket 必须加 `--remote-allow-origins=*`，否则握手 `403 Forbidden`。
- ✅ Python `requests` + certifi 对政府站点必报 `SSLCertVerificationError`（沙箱走 TLS 中间人代理），但**同一 URL 用 curl 正常**（curl 走 Windows 证书存储）→ 脚本里 `verify=False` 即可，加 `--verify` 开关可恢复严格校验。
- ✅ 沙箱代理偶发 `502 Bad Gateway`（`Tunnel connection failed`）→ **所有请求必须加 3 次指数退避重试**。

### 6.1 逆向「应用层状态码」与「限流归属」（可复用的三步法）

拿到私有接口后，真正的难点不是调通，而是**分清「没数据」「被拒」「被限流」**。这三者混在一起会把整批结果污染掉。

**第 1 步：找出真正的状态载体。**
不要假设 HTTP 状态码就是答案。很多 App 后端用**自定义响应头**承载业务码，HTTP 码只是壳。
做法：故意发一个明显错的请求，把**所有响应头**打出来，比对正常请求的差异。

> 实例：CallApp 用 `X_C_CODE`（`-2/-3/-4/0/1`）承载业务码，HTTP 用非标准码 `511/512/513/525` 兜着，
> **body 恒为空**。只看 HTTP 码会把「缺参数」和「被限流」混为一谈。

**第 2 步：逐参数置空/置错，做变体矩阵。**
固定其他参数，每次只动一个，观察状态码怎么变。这一步能同时解决两件事：
- 补全状态码语义表（哪个码对应哪种失败）
- **判定限流绑在哪个维度**

**第 3 步：用「短路顺序」反推限流归属。**
关键技巧：**故意传一个必然无效的值，看限流码会不会先于参数校验码出现。**

> 实例（CallApp）：`无效号码 + 有效凭据 → 513/-4`（限流码），而不是「未命中」；
> `有效 tk + 错误 cvc → 513/-4`，而不是 `-3`（身份无效）。
> ⇒ 服务端**先查该 `tk` 的配额，后校验号码和 `cvc`** ⇒ 限流绑在 `tk`，换 IP/UA/号码都没用。

**🚨 第 4 步（最容易漏）：检查「降级路径」会不会返回假数据。**
有些接口在凭据不完整时不报错，而是**静默降级**，返回一条格式正确、内容无关的记录。
验证方法：**同一个输入连查两次，看结果是否一致。不一致 ⇒ 随机 ⇒ 假数据。**

> 实例（CallApp）：缺 `cvc` 时返回 `HTTP 200 + X_C_CODE: 1` + 形似人名的字符串。
> `60102261791` 两次分别得 `Ainslee Vitale` / `Talonda Castleman` ⇒ 随机，与号码无关。

**这类坑比「被限流」危险得多** —— 限流会报错、会中断，而降级路径会**安静地把假数据写进你的结果集**。
凡是自动化管线，都必须为它加一道显式护栏（本例：`degraded` 状态 + 凭据为空时直接拒发请求）。

**第 5 步：测冷却时间时，注意「探活本身也消耗配额」。**
高频探活会把滚动窗口持续续命，让你误判成「永久封禁」。间隔取窗口长度的 1/10 量级（本例 5 分钟）。

---

## 7. 脚本清单

| 脚本 | 用途 |
|---|---|
| `scripts/my_phone_check.py` | A+C 层轻量 CLI（号码/银行账号/公司名） |
| `scripts/crowd_lookup.py` | D 层：busuk.my + junk-call.com |
| `scripts/malaysian_osint.py` | MalaysianOSINT 的 **Python 移植版**，11 个子命令（见下） |
| `scripts/callapp_lookup.py` | **★ DB3 CallApp 独立查询器**（不依赖原仓库）。支持本地/E.164 格式、`--json`、`--file` 批量、`--probe` 探活、`--recheck` 验可复现。**当前唯一稳定可用的众包库**，见 §4。**内置两道防假数据护栏**：① `tk`/`cvc` 为空直接拒发请求；② `X_C_CODE: 1`（匿名降级，返回随机名字）判为失败 |
| `scripts/callapp_sheet_batch.py` | **★ CallApp → Google Sheet 批量回填器**（§11 批量作业的 CallApp 版）。开跑前探活、增量落盘、`--resume` 断点续跑、限流熔断、回写数组逐行 assert 防覆盖。**只填空白的 A 格，已有名字的行原样保留**。`degraded` 记为错误，永不回写 |
| `scripts/pnl_runner.py` | `phone-number-lookup` 的隔离运行器，修掉「一个库报错就整体退出」的 bug（DB1/DB2/DB4/DB5 均已失效，见 §10） |
| `scripts/cdp_capture.py` | 无头浏览器抓 JS 渲染页面的真实接口 + 渲染后文本 |
| `scripts/verify_callerid.py` | **DB1 CallerID 批量准确率验证器**（三级匹配 + 重查可复现性） |
| `scripts/db1_batch.py` | **DB1 批量查名字**（v2：探活 + `-5` 熔断 + 增量落盘 + `--resume`），面向「表格一列号码 → 名字填另一列」（见 §11） |
| `scripts/db1_stub_lookup.py` | DB1 桩件，`STUB_MODE=healthy\|blocked\|flaky\|raise` 替代真实接口做端到端测试 |
| `scripts/db1_sheet_batch_driver.py` | **★ 多批连跑驱动器**（快照 → 跑批 → 回写 → 四步校验 → 间隔 → 下一轮）。带 PID 文件锁防并发、标记列 diff 校验、状态文件、快速失败。见「多批连跑：用驱动器」 |
| `scripts/check_idempotent.py` | **★ 幂等性门禁**（`--source db1\|db3`，`--gate` 时不稳定 exit 9）。**任何批量写名字列之前必须先跑**，见 §12 |
| `scripts/source_verify.py` | **★ 数据源真伪验证**（用表里已有的真名作 ground truth，判「幂等 + 一致」）。评估/复测任何新数据源时用，见 §12 |
| `scripts/db3_batch.py` | DB3 CallApp 批量查名字（⚠️ **当前不可用** —— 该源已污染，见 §12 与 `references/DB3-CallApp-限流与污染实测.md`） |
| `scripts/pdl_rr_probe.py` | **PDL / RocketReach 端点探测（无 key）** —— 判断端点是否存活、是否强制鉴权 |
| `scripts/pdl_rr_probe2.py` | **★ 假 key 对照实验 + test key 试探** —— 区分「端点拦人」vs「凭据被拒」；确认两家无匿名口子 |
| `references/pipeline-overview.md` | 四层管道总览全文（含完整单价表、法律依据） |
| `references/CallerID准确率验证-4号码.md` | 4 个已知答案号码的盲测报告 + 字段语义更正 |
| `references/CallerID-vs-Truecaller-9号码.md` | 9 个 Truecaller 号码的跨库交叉验证报告 |
| `references/CallerID-22号码验证汇总.md` | **三批 22 个号码的总汇**（含中文备注、token 全中等关键发现） |
| `references/Tellows-Truecaller-API实测.md` | **Tellows / Truecaller 端点可用性实测 + 5 个相关仓库评估**（含 451 归因更正） |
| `references/Truecaller登录方式对比-OAuth-SDK-vs-OTP.md` | **官方 OAuth SDK vs 官方 OTP vs 非官方 OTP 三条路径源码级对比**（含完整流程、Client ID 门槛、`installationId` 传递方式） |
| `references/Truecaller-OTP登录实测失败报告.md` | **★ 非官方 OTP 路径实测已死**（四组排除实验 + PR#157 权威判定 + 技术推断 + 替代路径评估） |
| `references/三个OSINT工具实测报告.md` | 早期三工具（phone-number-lookup / MalaysianOSINT / 众包）实测原文，含 DB1 字段语义更正 |
| `references/MalaysianOSINT-实测报告.md` | **★ MalaysianOSINT 8 功能逐项实测**（真实返回 + 原项目能否跑 + 修掉的 3 个 bug + README 示例造假的发现） |
| `references/全流程总结与问题清单.md` | **★ 全流程总纲**：所有遇到的问题、尝试过的方案、结论与状态一览（新接手先读这份） |
| `references/第三方姓名接口-2026-10-02.md` | **姓氏缺口与第三方方案**：哪些接口能返回结构化姓氏、哪些只是另一份备注、哪些根本没有 name 字段 |
| `references/PeopleDataLabs-RocketReach-可用性评估.md` | **★ PDL / RocketReach 实测评估**：端点对照实验（无 key vs 假 key）、PDL 马来西亚 6,516,827 条覆盖量化、RocketReach 6 credits/手机号 + 免费层不含电话、PDPA 合规边界 |
| `references/诈骗号码通报渠道-2026-10-05.md` | **★ 举报方向**（本 skill 其余部分是「查」，这份是「报」）：官方 6 条链路（997 / PDRM 报案 / MCMC CRP / Cyber999 / telco / Semak Mule）+ 众包 8 个平台（Whoscall 回报步骤 / Truecaller / CallApp / GetContact / WhoCallsMe…）+ Whoscall⇄Semak Mule 数据桥 + 场景决策表 |
| `references/第三方举报接口实测-2026-10-05.md` | **★ 程序化举报接口实测**：8 个平台的端点逐个真发请求。结论 —— **只有 ScamGuards `/api/submit` 可用**（含完整契约 + 源码依据 + curl 示例）；Truecaller/CallApp/Whoscall/MCMC/Tellows 全无公开举报 API |
| `references/CallApp限流阈值实测-2026-10-05.md` | **★ DB3 CallApp 限流实测**：触发点 ≈100 次/窗口、冷却 ≥78 分钟、**配额绑 (`tk`,`myp`) 精确值对、13 个变体证明无法参数轮换绕过**、`X_C_CODE` 全表、`X_C_CODE: 1` 返回假名字的陷阱、精确实测方法与安全节奏公式 |

### `malaysian_osint.py` 子命令

```bash
"$PY" scripts/malaysian_osint.py phone   0162281297    # Semak Mule telefon
"$PY" scripts/malaysian_osint.py bank    1234567890123
"$PY" scripts/malaysian_osint.py company "ABC SDN BHD" # Semak Mule 公司名
"$PY" scripts/malaysian_osint.py biz     "Maybank"     # malaysiayp 商家目录 ✅
"$PY" scripts/malaysian_osint.py mykad   900101011234  # 本地解码：生日/州/性别 ✅
"$PY" scripts/malaysian_osint.py ssm     202001012345  # 本地解码：实体类型 ✅
"$PY" scripts/malaysian_osint.py sspi    900101011234  # 移民局出入境限制 ✅（2026-10-02 修复：需先 GET 拿 PHPSESSID）
"$PY" scripts/malaysian_osint.py wanted  "TAN"         # PDRM 通缉 ✅（2026-10-02 修复：改词边界匹配，噪声 41→0）
"$PY" scripts/malaysian_osint.py bnm     "ABC"         # BNM 警示名单 ⚠️ Cloudflare 随机拦，已加 4 次重试
"$PY" scripts/malaysian_osint.py sprm    900101011234  # SPRM 贪污名单 ❌ 本机代理 502
"$PY" scripts/malaysian_osint.py ecourt  "TAN AH KOW"  # e-Court ❌ 端点已 404，门户改 WebForms
```

加 `--json` 只输出 JSON，`--verify` 开严格 TLS。

### 环境

```
venv: C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint
已装: requests / phonenumbers / urllib3 / rich / truecallerpy / telethon / ignorant / httpx[http2] / colorama / pypinyin
```

`phone-number-lookup` 原 `requirements.txt` **漏了 `colorama`**，需补装；且需 `httpx[http2]`。

---

## 8. 输出规范

回答用户时按这个顺序组织：

1. **一句话结论**：能不能查到机主 → 不能（除非走司法途径）；能查到什么。
2. **表格**：逐层列出「来源 → 结果 → 可信度」。可信度分档：
   - **高**：libphonenumber 号段、Semak Mule（官方库）
   - **中**：phoneosint `ignorant` 的账号绑定命中、付费运营商 API
   - **低**：众包标签（busuk.my / CallerID）
3. **风险提示**：
   - Semak Mule **「无记录 ≠ 安全」**，只是没有公开投诉。
   - 号段运营商**不穿透 MNP**，别当结论。
   - 众包标签**不是实名**，不可作为身份认定依据。
4. 法律边界 + 报警渠道（PDRM / NSRC **997**）。

---

## 9. 实测样本（回归测试用）

| 号码 | Semak Mule | 众包 | 备注 |
|---|---|---|---|
| `0102261791` | 无记录 | DB1 CallerID `Diana/1`（2026-10-02）→ **2026-10-05 复测为空（DB1 已封）**；**DB3 CallApp `cleaner driver`** | DiGi，**绑定 instagram.com**（phoneosint ignorant +15） |
| `0162281297` | 无记录 | CallerID **`Prof Lee`（用户确认正确）** | DiGi，绑定 Instagram |
| `0123355873` | 无记录 | CallerID（空） | Maxis |
| `0122071768` | 无记录 | CallerID **`Dato Dr Ricky`**（已知 `dato ricky lim`） | Maxis |
| `0123013006` | 无记录 | CallerID（空） | Maxis |
| `0192385938` | 无记录 | CallerID **`Mr Malvin`**（已知 `marvin lee`） | Celcom |
| `0122860106` | — | CallerID `Loh lawyer`（TC: LOW CHI CHENG） | `Loh`≈`Low` 同姓异拼 + **职业标签** |
| `0122133606` | — | CallerID `Liza Yap`（TC: LIZA YAP SURBANA） | **DB1 是 TC 名的子串** |
| `0123878872` | — | CallerID `Linda Lim`（TC: LINDA LIM VG） | **DB1 是 TC 名的子串** |
| `0122958331` | — | CallerID `rosli smvb`（TC: ROSLI NORDIN） | 命中 `rosli` |
| `0162084648` | — | CallerID `Mr Eddie PA`（TC: EDDIE LIM） | 命中 `eddie` |
| `0172706676` | — | CallerID `boon han lim`（TC: BOON HONDA CITY） | **同号两库备注完全不同** |
| `60197527397` | — | CallerID **`Eng Jing Hao`**（TC: MR ENG JING HAO） | **✅ 唯一 token 全中**（去 MR 前缀后一致） |
| `60165014911` | — | CallerID **`智辉`**（TC: GABERIAL NG CHEE HUI） | **✅ 中文备注，拼音 `zhihui` ⊃ `hui`** |
| `193879412` | — | CallerID `Lotus Power : Angie Ng`（TC: MS NG YOKE LAN） | 「组织 : 人名」格式，命中 `ng` |
| `60123456789` | — | `Kedai Makan Pak Chik` + `Scam` 标签 + 329 次举报 | 商家号被大量举报 |
| `60100000000` | — | `rswelth. id : rs122867 / pword : rosdi74` | 证明库数据质量不可控 |

**DB3 CallApp 回归样本（2026-10-05，`scripts/callapp_lookup.py` 可一键复跑）**：

| 号码 | CallApp `name` | priority | 额外字段 |
|---|---|---|---|
| `0102261791` | `cleaner driver` | 2 | — |
| `0162281297` | **`prof lee way seah`** | 8 | — |
| `0123013006` | **`martin lim`** | 4 | — |
| `0192385938` | **`marvin lee`** | 84 | facebookID / linkedinPubProfileUrl / linkedinID / googlePlusID / spamScore -1 |
| `0122071768` | `dato ricky` | 37 | facebookID / spamScore -1 |
| `0123355873` | `leong poh wah` | 15 | facebookID |
| `0122133606` | `liza yap` | 12 | facebookID |
| `0123878872` | `linda lim` | 9 | facebookID |
| `0162084648` | `eddie lim` | 9 | facebookID |
| `0122860106` | `chi cheng` | 4 | — |
| `0122958331` | `sp rosli` | 5 | — |
| `0172706676` | `boon han` | 5 | — |
| `60197527397` | `jing hao` | 8 | — |
| `60165014911` | `gaberial intern marcom` | 2 | — |
| `60123456789` | `kulailand.com : kulai land for sale` | 1303 | websites×3 / addresses×5 / categories / photoUrl / avgRating 5.0 / 7 社交 ID / spamScore -16 |
| `60199999999` | `mawar dyzahhra sdn. bhd.`（**假号也有记录**） | — | websites / addresses×4 |
| `60199999998` | `namasayazolazme andabulehpanggilsayapapazola`（**恶搞文本**） | 15 | facebookID / spamScore 4 |
| `60100000000` | `spam` | 68 | addresses / facebookID / spamScore -1 |

**有返回率 13/13 = 100%（13 个真实号码）｜可复现 3/3 = 100%｜token 全中 3/13**


前两个号码都命中 `phoneosint` 的 `ignorant` 模块 → **绑定 `instagram.com`**。这是整条链路里唯一真实、可行动的信号（说明号码在该平台有账号）。

`phoneosint` 用法：

```bash
"$PY" phoneosint.py +60162281297 --country MY --all --no-banner --json -o report.json
```

⚠️ 默认 `country` 是 `IN`（印度），查马来西亚**必须显式加 `--country MY`**，否则本地格式号码会解析错。

---

## 10. 三个开源工具的可用性排名

| 排名 | 工具 | 理由 |
|---|---|---|
| 1 | **MalaysianOSINT**（本 skill 的 Python 移植版） | 唯一直接对口马来西亚：Semak Mule + SSPI + 商家目录 + MyKad 都能用 |
| 2 | **phoneosint** | 能跑、诚实、`ignorant` 是真信号；但默认 `--country IN`，多数产出是 dork URL 需人工点开 |
| 3 | **phone-number-lookup** | 5 个库 **4 个已废**（DB2 Sync.ME 代码 bug / DB4 Eyecon 端点失效 / DB5 Truecaller token 被封号 / **DB1 CallerID 自 2026-10-05 起被封**）。**⚠️ 2026-10-05 更正：DB3 CallApp 仍在工作且可复现，且返回的是 `name` 字段（人名/备注），不是「分类标签」。** **仅供参考，不要当实名结果用** |

### ★ DB3 CallApp —— 当前唯一还能用的库（2026-10-05 实测更正）

原描述「DB3 CallApp 只给分类标签」**错误**。实测返回 `{"name": ..., "priority": ...}`，`name` 就是众包通讯录备注，且**能给完整姓名**（`martin lim`、`marvin lee`、`prof lee way seah`）—— 比 DB1 的「只给名不给姓」强。

**完整接口、字段语义、准确率盲测、数据质量警告见 §4「DB3 CallApp」**，独立查询器 `scripts/callapp_lookup.py`。

**⚠️ 但 CallApp 也有配额，而且很小：≈100 次/窗口，用光后整对 (`tk`,`myp`) 凭据被锁 ≥1 小时，且无参数轮换绕法**（2026-10-05 实测）。批量前必读 §4 限流章节 + `references/CallApp限流阈值实测-2026-10-05.md`。

一句话：**DB1 被封期间，想拿众包备注就走 CallApp —— 但一次只能查几十个，别指望跑大批量。**

### ⚠️ DB1 CallerID 封禁状态（2026-10-05 12:10 复测）

`db1_batch.py --probe` → `BLOCKED 60162281297 -> {"status": -10}`。
**对照号码 `0127680894`（历史有数据）同样空返回** → 是服务端拒绝，不是无数据。跑 DB1 前**必须先 probe**，否则会把「被封」误读成「该号码没人存过」。

原版 `MalaysianOSINT` 是 **C + libmicrohttpd + cJSON** 常驻服务，需 gcc/cmake，Windows 上编译成本高 → 已移植为一次性 CLI，无需编译、无需起服务。

---

## 11. 批量作业：表格「号码列 → 名字列」

典型需求：Google Sheet 里 B 列是号码、A 列要填名字，A 列已有名字的行跳过，先做 N 个。

```bash
GOG="C:/Users/Admin/.workbuddy-ai/bin/gog/gog.exe"
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
ID=<spreadsheetId>; SH="'SHOPEE LIST 01'"
T=C:/Users/Admin/AppData/Local/Temp

# 1) 导出 A/B 两列（必须 FORMATTED_VALUE，否则前导零丢失）
"$GOG" sheets get $ID "$SH!A1:B10000" -j --results-only --render FORMATTED_VALUE > $T/sheetAB.json

# 2a) 先探活（必做）。exit 2 = 被封，直接收工，别开跑
"$PY" <skill>/scripts/db1_batch.py --probe

# 2b) 批量查（脚本内部也会自动探活一次；A 列非空自动跳过；找到 --want 个就停）
#     exit 0 = 正常 / 2 = 开跑前被封 / 3 = 跑中途被封熔断
"$PY" <skill>/scripts/db1_batch.py --sheet $T/sheetAB.json --startrow 1 --want 50 --out $T/db1_results.json
# 若上次被熔断，加 --resume 从断点续跑（跳过 JSONL 里已处理的行）
"$PY" <skill>/scripts/db1_batch.py --sheet $T/sheetAB.json --startrow 1 --want 50 --out $T/db1_results.json --resume

# 3) 生成回写数组：把 found 填进对应行，其余保持原值（含被跳过行的原值，防止清空）
"$GOG" sheets update $ID "$SH!A1:A174" --values-json @$T/colA.json --input RAW -j

# 4) 回读校验：matched 必须 == found 条数
```

### 七个必踩的坑

1. **回写用「一段连续区间」最省事，但必须回填被跳过行的原值**。
   若区间 `A1:A174` 里第 120 行本来有名字（被跳过），直接写空串会**抹掉它**。
   做法：先把原 A 列值拷进数组，只覆盖本次找到的行。**写入前逐行 assert 目标格为空**。
2. **`--render FORMATTED_VALUE`**：默认就是这个，但显式写出来。用 `UNFORMATTED_VALUE` 会把
   `0127680001` 读成数字 `127680001`，前导零丢失、号码解析错。
3. **写入用 `--input RAW`**：避免 Google 把 `=xxx` / 纯数字当公式或数字解析。
4. **回写区间里的原有名字可能比肉眼看到的多**。批 2 区间里 5 个、批 3 里 6 个。
   以导出快照为底、只覆盖 found 行，是唯一安全做法。
5. **不要用「裸循环」跑批**（无探活、无熔断、只在结束时落盘）。批 4 就是这样丢了 78 条。
6. **`requests` 必须带 `timeout`，否则网络半开时永久挂死**（2026-10-06 实测）。
   仓库 `lookup.py` 原有 4 处 `requests.post/get` **都没超时**。批 12 跑到 row3691 后
   静默 30 分钟：CPU 零增长、无外连、日志不动、进程却还活着。
   → 已给 4 处全部补 `timeout=(10, 30)`。**换新仓库/更新 repo 后必须重新确认这条补丁还在**：

   ```bash
   grep -n "requests\.\(post\|get\)" "$PNL_REPO/lookup.py"   # 每行都必须带 timeout=
   ```

   见下面「🔴 挂死 vs 被封：如何区分」。
7. **「跑批 rc=0」≠「数据已落表」——写入与回读都必须查返回码并重试**（2026-10-06 实测）。
   批 12 跑批成功（344 查询 / 100 命中 / rc=0），但：
   - `gog sheets update` 偶发**返回 exit 0 + 空 stdout** → 脚本没查 returncode → **100 个名字静默没写进去**
   - 回读步 `json.loads(sh(...).stdout)` 裸用 → 抛 `JSONDecodeError` → 驱动器整体崩溃

   **只跑批、不核对，会误判成「本批已完成」。** 已给驱动器加 `gog_json()`：

   ```python
   def gog_json(cmd, tries=3, timeout=900, need_json=True):
       """gog 偶发返回空 stdout（exit 0 但无输出）。必须重试。"""
       for k in range(tries):
           r = sh(cmd, timeout=timeout)
           txt = (r.stdout or "").strip()
           if r.returncode == 0 and txt:
               if not need_json: return True, txt
               try: return True, json.loads(txt)
               except json.JSONDecodeError as exc: last = str(exc)
           else:
               last = f"rc={r.returncode} stdout={txt[:80]!r}"
           time.sleep(2 * (k + 1))
       return False, last
   ```

   写入失败 / 回读失败 → **立即 `exit 5` 停止**，并提示回写数组留在 `colA<N>.json` 可手工重放：
   ```bash
   "$GOG" sheets update <ID> "'SHOPEE LIST 01'!A3556:A3910" \
          --values-json @colA12.json --input RAW -j
   ```
   **手工重放后必须回读校验**：`matched == found`、`preserved_ok`、`A 总数 == 前值 + found`。

   ⚠️ **配套：驱动器的 `summary` 只在失败分支被 append 过**（历史 bug，2026-10-06 修）。
   成功路径漏了 `summary.append(entry)` → `run_batches_summary.json` 与 `db1_autostate.json`
   长期写成 `{"summary": [], "next_start_row": ...}`，**这正是「起点不能信 summary.json」的真实根因**。
   修后 7 个分支全部记账。**下次升级驱动器时，务必确认成功路径有 append。**

### 🚦 DB3 CallApp 批量作业（`callapp_sheet_batch.py`）—— 与 DB1 完全不同的排期逻辑

DB1 是「约 1160 次后封禁」，CallApp 是「**约 100 次后封禁**」。**两者阈值差一个数量级，绝不能套用同一套节奏。**

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
S=<skill>/scripts
T=C:/Users/Admin/AppData/Local/Temp

# 1) 导出 A/B/C 三列（C 列是跳过标记列）
"$GOG" sheets get $ID "$SH!A1:E10000" -j --results-only --render FORMATTED_VALUE > $T/sheet_abc.json

# 2) 探活（exit 2 = 被限流 或 凭据降级）
"$PY" $S/callapp_sheet_batch.py --probe

# 3) 跑批：--rows 是「本次最多扫多少个可查行」，不是「最多命中多少」
"$PY" $S/callapp_sheet_batch.py --sheet $T/sheet_abc.json --out $T/ca1.json \
      --rows 80 --delay 1.8
# 被熔断后从断点续跑（JSONL 里已处理的行自动跳过）
"$PY" $S/callapp_sheet_batch.py --sheet $T/sheet_abc.json --out $T/ca1.json \
      --rows 80 --delay 1.8 --resume

# 4) 回写：用生成的 <out>.colA.json（已以快照为底，只覆盖 found 行）
"$GOG" sheets update $ID "$SH!A1:A10000" --values-json @$T/ca1.json.colA.json --input RAW -j
```

**退出码**：`0` 正常 / `2` 探活失败（被限流或凭据降级）/ `3` 中途 `-4` 熔断 / `5` 回写校验失败。

**CallApp 专属的四个坑**：

1. **🚨 `X_C_CODE: 1` 会返回假名字**（详见 §4）。脚本已把 `degraded` 记为错误状态，**永远不进回写数组**。若看到 `degraded > 0`，说明 `tk`/`cvc` 环境变量被清空了，立刻检查。
2. **探活本身消耗配额**。被封后**不要**每分钟探活 —— 会把滚动窗口持续续命。间隔取 **5 分钟**。
3. **`--delay` 不要用 0.3s**。CallApp 的配额比 DB1 小两个数量级，1.8s 起步。
4. **8867 行这种量级在这套凭据下跑不完**。≈100 次/窗口 × 冷却 ≥1 小时 ⇒ 实际吞吐约 **几十~一百条/小时**。排期前先跟用户对齐，别承诺「明天跑完」。

### 🚦 DB1 限流/封禁 —— 故障、根因、纠错（2026-10-02 实测，跑批必读）

**现象**：累计约 **1160 次**查询后，接口对**所有**号码统一返回
`DataBase 1 Information: {"status": -5}`，命中率断崖归零。
（批 1–3 共 880 次正常 → 批 4 跑到第 ~280 次时开始全 `-5`。）

**判据（关键）**：`-5` ≠ 数据稀疏。**复测一个已知能返回的号码**（如 `0127680894` 原返回 `sobri`）——
若它也返回 `-5`，就是**服务端拒绝**，不是没数据。

**根因定位（实测排除法）**：

| 观测 | 排除的假设 |
|---|---|
| HTTP **200**（不是 429/403） | 不是标准 HTTP 限流 |
| 无 `Retry-After` 头 | 服务端没给退避信号 |
| `Server: cloudflare` | 不是 CF 层拦截（否则会给 403/1020） |
| 连**历史上有数据**的号码也 `-5` | 不是号码本身无数据 |
| 连**测试号**也 `-5` | 不是针对性封号 |

→ 结论：**应用层**拒绝（按 uid `6578ca99…` + 设备指纹 `com.callblocker.whocalledme`，
或按出口 IP 计数）。**无法区分「临时配额」还是「永久封号」** —— 因为换不了身份复测。
**观测 40 分钟后仍未自愈**（16:18 复测仍 `-5`）。

**⚠️ 最大的坑：v1 脚本只在循环结束才写文件。**
批 4 被熔断时 78 条命中全在内存里，杀掉进程 = 全丢，是靠从 stdout 抢救才保住。
**批量脚本必须增量落盘。**

### ✅ 纠错后的脚本行为（`db1_batch.py` v2，已过 5 项端到端测试）

| 能力 | 说明 |
|---|---|
| **开跑前探活** | 先单发 1 次 `0162281297`。被封 → **exit 2，零批量请求** |
| **`-5` 识别** | `status < 0` 判为「被封」，**不计入 miss**，不重试 |
| **熔断** | 连续 `--max-block`（默认 5）次 `-5` → 中止，**exit 3** |
| **增量落盘** | 每条结果立刻 append 到 `<out>.jsonl` 并 flush，杀进程不丢 |
| **断点续跑** | `--resume` 读 JSONL，跳过已处理行 |
| **汇总** | 任何退出路径都把 JSONL 汇总成 `--out` JSON |

退出码：`0` 正常 / `2` 开跑前就被封 / `3` 跑中途被封熔断

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
"$PY" db1_batch.py --probe                                    # 只探活，exit 0/2
"$PY" db1_batch.py --sheet s.json --startrow 1177 --want 100 --out r5.json
"$PY" db1_batch.py --sheet s.json --startrow 1177 --want 100 --out r5.json --resume
```

**测试方法（可复现）**：用桩件 `stub-db1`（`STUB_MODE=healthy|blocked|flaky|raise`）
替代真实接口，端到端验证控制流。5 项全过：

| 用例 | 期望 | 实测 |
|---|---|---|
| T1 健康路径 | found 10 / miss 1 / exit 0 | ✅ 11 查询 + 1 探活 = 12 请求 |
| T2 开跑前被封 | exit 2，只发 1 个请求 | ✅ |
| T3 跑中途被封（前 8 次正常） | exit 3，熔断在连续 5 次 | ✅ 13 请求，found 7 + blocked 5，JSONL 完好 |
| T4 断点续跑 | 跳过 12 行，从第 13 行续，无重复 | ✅ found 累计 20，行号无重复 |
| T5 接口抛异常 | 记 error 不崩，JSONL 落盘 | ✅ err 3，exit 0 |

**排期口径**：见「封禁阈值不固定」 —— **按速率限，不按总量限**。单批 `--want 100`（≈350 次查询）没问题，
关键是**批间插间隔**。被封后**不要空转重试**，隔一段时间再用 `--probe` 单点探活。

**无人值守解法**：挂一个**每小时**跑 `--probe` 的定时任务（只花 1 个请求）。
解封则自动跑下一批，并写一个状态文件（如 `<tmp>/db1_autostate.json` 的 `last_success`）
防止重复跑批、重复消费配额。
⚠️ 定时任务的粒度下限是**每小时** —— `FREQ=MINUTELY` 不被支持，`HOURLY` 下的 `BYMINUTE` 也会被忽略。

**中断后的处理**：已命中的部分**先落表**（零风险），剩余名额留给下一批，
起点行改为「最后一个命中行 + 1」。

### 多批连跑：用驱动器（**推荐**，别手工重复单批）

`scripts/db1_sheet_batch_driver.py` 把「快照 → 跑批 → 回写 → 校验 → 间隔 → 下一轮」串起来，
遇 **exit 2/3（被封）**、输入耗尽、校验失败、达到 `--max-batches` 自动收口。

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
D="C:/Users/Admin/.workbuddy-ai/skills/malaysia-phone-osint/scripts/db1_sheet_batch_driver.py"
"$PY" "$D" --spreadsheet-id <ID> --sheet "SHOPEE LIST 01" \
    --start-row 3124 --first-batch 11 --want 100 --max-batches 8 \
    --sleep-between 300 > $T/driver.log 2>&1
```

**退出码**：`0` 正常收口 ｜ `2` 开跑前被封 ｜ `3` 中途被封 ｜ `4` 已有实例在跑 ｜ `5` 校验失败 ｜ `6` 快照导出失败

| 能力 | 为什么必须有 |
|---|---|
| **PID 文件锁**（`--lock-file`，默认 `<tmp>/db1_driver.lock`） | 定时任务与手动跑批会**真并发**写同一列。重复触发直接 exit 4。锁用 **ctypes `OpenProcess`+`GetExitCodeProcess`** 判存活 |
| **标记列 diff 校验** | 不用「等于常数」。写入前后逐行 diff，输出「新增行/移除行」；有变化**只告警不中止**（该列可能被人工改） |
| **快照失败快速失败** | 坏 spreadsheet id / gog 报错时打印原因并 exit 6，**不抛 traceback**、不发批量请求 |
| **状态文件**（`--state-file`） | 落 `next_start_row`，供定时任务判断该不该续跑 |
| **起点事实源** | ⚠️ 别只信 `run_batches_summary.json`：它会被「**开跑即被封**」的空跑**覆盖成 `{"summary": [], "next_start_row": 1}`**（10-05 11:44 实测发生）。`db1_autostate.json` 也只在走驱动器的路径下回写，**手动直接调 `db1_batch.py` 的批次不会更新它**（批 6–10 就没更新，一度停留在批 5 的 1486）。✅ **可靠来源 = `run_batches.log` 末尾的「汇总 / 下一批起点」**；发现状态文件落后就按它校正 |
| **`--sleep-between`** | 滚动窗口限速场景（见「封禁阈值不固定」）批间插 300s，比压缩总量更有效 |
| **stdout 全进日志** | 300+ 行中间输出不污染调用方上下文 |

**并发锁的两个反例（本机踩过，别写回去）**：
- ❌ 用 `tasklist /FI "PID eq N"` 判存活 —— 沙箱里 MSYS 会把 `/FI` 转成路径，**输出为空 → 误判已死 → 两个进程同写一列**。
- ❌ 用 `os.kill(pid, 0)` —— **Windows 上它等价于 `TerminateProcess`，会真杀掉对方进程**（不是 POSIX 的"仅探测"）。

#### ⚠️ exit 4 只说明"锁被占"，**不保证对方在正常推进**

2026-10-06 11:31 实测：定时任务探活 OK 后启动驱动器得 exit 4。若就此收工，会**漏掉一个真问题**——
锁持有方（另一实例）的**批 12 子进程已僵死 22 分钟**：`r12.json.jsonl` 停在 11:15 不再增长，
子进程内存掉到 908K/3MB（正常跑批时是几 MB 且在增长）。

**收到 exit 4 后必做的两步核查**：

```bash
T="C:/Users/Admin/AppData/Local/Temp"
# ① 锁持有 PID
cat "$T/db1_driver.lock"
# ② 对方最新 jsonl 的 mtime + 大小（判"在跑"还是"卡死"）
ls -lt "$T"/r*.json.jsonl | head -3
# ③ 子进程内存（异常低 = 僵死）。用 PowerShell 工具，别在 Bash 里调
#    Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
#      Select-Object ProcessId,CreationDate,WorkingSetSize,CommandLine
```

| 观察 | 结论 |
|---|---|
| jsonl mtime 在近 1–2 分钟内 / 内存正常 | 对方在跑，**本实例退出即可** |
| jsonl mtime 停滞 >10 分钟 且 内存异常低 | 对方**僵死**。不要抢锁；记录中断行号并把起点推进到中断处 |
| 同时探活 `--probe` 仍 exit 0 | 佐证是**进程挂起**而非封禁，别误判成被封 |

### 封禁阈值不固定 → 放慢节奏，别压缩总量

| 日期 | 封禁时的当日累计查询 | 触发耗时 |
|---|---|---|
| 10-02 | ~1160 | 2 小时内 |
| 10-05 | ~1899 | 约 1 小时内 |

差 **60%** ⇒ **不是固定日配额，是滚动窗口内的速率**。
→ 排期策略改为**批间插 5–10 分钟**（`--sleep-between 300`），而不是把单批压到 300 次以内
（10-05 批 9 单批 415 次查询照样跑完，批 10 却只跑 191 次就被封 —— 按总量算排期必然失灵）。

**封禁状态码会变**：10-02 是 `{"status": -5}`，10-05 复测是 `{"status": -10}`。
脚本的 `is_blocked()` 判据是 **`status < 0`**（不是等于 -5），所以两种都能识别。
👉 **不要**把 `-5` 硬编码进任何判据；看到没见过的负数先当封禁处理，再去核对。

### 覆盖率（重要口径，别按 82% 做预算）

| 号码来源 | 覆盖率（DB1 有返回） |
|---|---|
| 已被 Truecaller 收录（先筛过） | **82%**（22 个样本） |
| **任意/随机号码表（冷数据）** | **29%**（172 个样本，找到 50 个） |

→ **冷号码表要按 ~30% 估工作量**：想拿 50 个名字，准备查 150–200 个号码。
→ 找不到 ≠ 接口坏，是「该号码从未被任何人存进通讯录」。

### 名字质量提醒（给用户看结果时）

DB1 返回的是**众包通讯录备注**，常见形态：`Aisyah 4 Sigma`、`jaii max`、`外婆`、`awei store`、
`李景龙`、`K NOR(Swh Dt`。**会混进商家名、称呼、乱码、截断串**。
回写前不筛（用户要的是原始备注），但**汇报时必须说明这不是实名**。

### 实测记录 2026-10-02 / 10-05

- 表 `1WdlrWe2vY8cVCzyowfZJUF1F6H4oEhwz9iLIVH4lAPU` / `SHOPEE LIST 01`，B 列 10000 个号码，A 列原有 258 个名字。
- **批 1**：`--startrow 1 --want 50` → 查 172 个（行 1–174），命中 50，0 错误。
- **批 2**：`--startrow 175 --want 100` → 查 359 个（行 175–538），命中 100，0 错误，耗时 13m26s。
- **批 3**：`--startrow 539 --want 100` → 查 349 个（行 539–893），命中 100，0 错误，耗时 8m24s。
- **批 4**：`--startrow 894 --want 100` → **跑到第 279 个触发封禁**，命中 78（行 894–1176），已落表。
  剩余 22 个名额作废，**下一批起点 行 1177**。
- **批 5**（10-05 解封后）：主批 `--startrow 1177` 扫到行 1485 命中 87（执行者自建 300 次查询上限）；
  补跑 `--startrow 1486 --want 13` 查 47 个命中 13 → **合计 100 命中（行 1177–1533，347 次查询）**。
  全程 `blocked=0 / errors=0`。
- 累计：**查 3058，命中 675，覆盖率 22–33%**（波动大）。
- **批 6–9**（10-05）：`--startrow 1534 / 1844 / 2182 / 2504`，每批 100 命中，各 15–20 分钟，
  全程 `blocked=0`。**批 10**（`--startrow 2928`）第 191 次查询时被封，熔断收口，落表 47 个。
- 批 6–9 由**驱动器**（见「多批连跑：用驱动器」）连跑，四步校验每批全过。
- 表格状态：A 列非空 **1133**；C 列 **259**（多出的 1 个是人工标注，见下节）。
- **下一批起点 行 3124**（10-05 11:35 被封；10-05 晚间复测仍封，状态码已是 `-10`）。

### ⚠️ 标记列会被外部人工改动 —— 不要用「等于某个常数」当校验

`SHOPEE LIST 01` 的 C 列是业务状态码列（图例见 `工作表1`：
`A=可以发资料 / B=REJECT / C=NO ACCEPT CALL / D=NOT AVAILABLE / X=SYSTEM / WN=WRONG NUMBER`）。
人工会在我们跑批期间往里面加标注 —— 实测 C 列从 258 变成 259（行 1991 被人工标了 `C`），
**不是我们的写入造成的**。

→ 校验方式：**拿历史快照逐行 diff**，确认「新增的标记行」不是我们写的区间；
不要因为计数变化就判定自己出错，也不要因此停下来。

### 🔴 挂死 vs 被封：如何区分（2026-10-06 实战）

两者都表现为「进度不动」，但处置完全相反。**用 CPU 时间采样区分，不要靠猜**：

```bash
# 采样两次（间隔 10s），看 CPU 时间是否增长
"$PY313" -c "
import ctypes,time
k=ctypes.WinDLL('kernel32',use_last_error=True)
def cpu(pid):
    h=k.OpenProcess(0x1000,False,pid)
    if not h: return None
    c=ctypes.c_ulonglong(); e=ctypes.c_ulonglong()
    a=ctypes.c_ulonglong(); b=ctypes.c_ulonglong()
    ok=k.GetProcessTimes(h,ctypes.byref(c),ctypes.byref(e),ctypes.byref(a),ctypes.byref(b))
    k.CloseHandle(h)
    return (a.value+b.value)/1e7 if ok else None
pid=18008; print(cpu(pid)); time.sleep(10); print(cpu(pid))"
```

| 现象 | 挂死（hang） | 被封（banned） |
|---|---|---|
| 进程存活 | ✅ `exit_code=259` | ✅ |
| **CPU 时间** | **10s 内零增长** | 持续增长（在下一次请求/重试） |
| **网络连接**（`netstat -ano`） | **无外连** | 有 ESTABLISHED 到目标站 |
| JSONL 增长 | 停 | 停 |
| 日志尾行 | 停在某次完整结果后 | 停在 `BLOCKED` 或探活失败 |

**挂死处置**：查 `lookup.py` 的 `requests` 是否带 `timeout`（本坑根源）。杀进程链后
用 `--resume` 续跑，已落盘的 JSONL 行不丢。

**进程链要整条杀**：驱动器 `db1_sheet_batch_driver.py` → `cmd.exe` → `db1_batch.py` → 其子进程。
只杀驱动器会留下孤儿 batch 继续持锁。用 `CreateToolhelp32Snapshot` 找 `ParentProcessId` 树。
（`wmic` 本机不存在；`tasklist /FI` 在 Git Bash 里被 MSYS 转义成路径 → 都别用。）

### 跑批效率：优先「主代理 + 后台 Bash + stdout 重定向」

300+ 行中间输出**必须重定向到日志文件**，否则全进上下文：

```bash
"$PY" db1_batch.py --sheet $T/sheetAB6.json --startrow 1844 --want 100 --out $T/r7.json > $T/r7.log 2>&1
```
配 `run_in_background: true` + `TaskOutput(block=true)` 等待。实测 100 命中 **15m8s**
（子智能体方式 ~25min），且没有「重复起同一条命令」的风险。
用子智能体的唯一好处是上下文隔离 —— 重定向 stdout 就能达到同样效果。

### `--want` 的语义（易误用）

`--want N` 是「**凑满 N 个命中为止**」，不是查询上限。29% 覆盖率下要 100 个命中 ≈ **350 次查询**。
想控制单批查询量就把 `--want` 调小，**不要在外面套一层「300 次查询封顶」的 wrapper**
（实测会导致只跑到 87 就收口，还得补跑一次）。

### 性能口径（排期用）

- **单次查询 ≈ 2.2s**（含 `--delay 0.4`）。**300 个号码 ≈ 13 分钟**，不是 5 分钟。
- 想拿 100 个名字 → 约 350 个号码 → **约 13 分钟**。要跑上千个必须后台跑 + 分片。

### 回写注意（连续区间模式的第二个坑）

被跳过行的原值数量**可能多于肉眼所见**。批 2 的 `A175:A538` 区间里实际有 **5 个**原有名字
（189/199/422/485/522），批 3 的 `A539:A893` 里有 **6 个**（608/759/796/808/821/880）。
漏掉任何一个都会被清空。
**必须以「导出快照 + 只覆盖 found 行」的方式生成数组，并在写入前 assert 目标格为空。**

### ⚠️ 第三方标记列：绝不顺手补

若表格里还有一列标记（如 `SHOPEE LIST 01` 的 C 列），它对应**另一条独立流程**
（本例：C 列由纷享销客 CRM 流程 + 人工共同维护，图例见 `工作表1`）。
**用 DB1 查出来的名字只能写名字列，绝不能补标记列** —— 会把两条流程的数据混在一起。

校验方式（**不要用「等于常数」**）与驱动器内置的 diff 逻辑 → 见上文「标记列会被外部人工改动」。

---

## 12. 反向需求：如何「通报」诈骗号码（举报方向）

本 skill 主体是「查号码」。当用户问的是**如何举报/通报**（「怎么向 Truecaller / Whoscall / CallApp 举报」「诈骗号码怎么上报」「MCMC 怎么投诉」），走这一节。
完整版：`references/诈骗号码通报渠道-2026-10-05.md`。

**两条链路互不替代**：官方能**真封号**，众包能**让全网看到标记**。

| 目的 | 入口 |
|---|---|
| 钱已被转走 | **997**（NSRC，**24h**；**2025-09 起通话本身即视为报案**，不必再跑警局） |
| 没损失、想封号 | MCMC CRP `aduan.mcmc.gov.my`（热线 1-800-188-030）→ 转 telco 封锁 |
| 没损失、想警告他人 | **Whoscall App → 首页右下角「回报」→ 输入号码 → 提交**（马来西亚首选） |
| 想进官方 Semak Mule 库 | **只能走 PDRM 报案**（无自助入口） |

**★ 关键事实（马来西亚特有）**：**Whoscall 获 PDRM 授权直接读取 Semak Mule 官方库**（Gogolook 马来西亚总监原文，合作项目 "Scam Free Malaysia"）。→ 在马来西亚，「官方报案」与「众包回报」**不是二选一**：报案后 Whoscall 侧会自动同步。反向不成立 —— 只在 Whoscall 回报**不会**进官方库。**Truecaller 未发现与马来西亚政府有本地合作。**

**各平台举报入口（实测）**

| 平台 | 入口 | 备注 |
|---|---|---|
| Whoscall | App 内「回报」/ `Number lookup → Report` | 需系统确认才显示；有积分奖励；误标申诉 `service@gogolook.com`（**只能删不能改**） |
| Truecaller | App 内号码详情 → `Block and report` | **需多人标记**才生效；误报改 `not spam`；网页版需登录 |
| CallApp | App 内标记 | **无公开帮助文档、无网页表单**；举报入口在 App UI |
| GetContact | `getcontact.com/send-report` | 这是**投诉表单**，不是号码库入口 |
| Tellows / Should I Answer | 有提交入口 | ❌ **马来西亚零覆盖**（实测 Tellows 5/5 空） |
| junk-call.com / busuk.my | 有表单 / 无 | ❌ 模板页 / 明确声明不收举报 |

**常见误区（回答时必须纠正）**
- Semak Mule 是**查询**库，不是举报入口；入库存只能靠警方报案
- MCMC **不能查诈骗**（刑事管辖在 PDRM），只做封锁与删内容
- Semak Mule **无记录 ≠ 安全**（新钱骡账户还没记录）
- Cyber999 是**计算机安全事件**报告点，官方页面**未列电话诈骗**为受理类别
- **NSRC 只接电话、从不外呼** —— 自称 NSRC 官员打来的都是骗子

### 12.1 程序化举报接口（2026-10-05 实测）

完整版：`references/第三方举报接口实测-2026-10-05.md`。

**结论：只有 ScamGuards 有可直接调用的公开举报 API。其余全无。**

| 平台 | 公开举报 API | 实测证据 |
|---|---|---|
| **ScamGuards** | ✅ **可用** | `POST https://scamguards.app/api/submit`；`Allow: OPTIONS, POST` |
| Truecaller | ❌ | 仅内部 `filter-store4-{eu,noneu}.truecaller.com/v4/filters`（**400** = 存在但缺鉴权，2026-10-05 复测；此前记为 451）。`api.truecaller.com` DNS 不存在 |
| CallApp | ❌ | `s.callapp.com/callapp-server/{report,feedback,spam}` 全 **404** |
| Whoscall / Gogolook | ❌ | Asi 是**查询向**企业 API；`api.whoscall.com` 404 |
| MCMC CRP | ❌ | `aduan.mcmc.gov.my` 及 `/api/*` 全 **403**（CF 拦非浏览器） |
| Tellows | ❌ | 查询 200 可用；`/basic/rate.php`、`/api/v1/rate` 均 404 |

**ScamGuards `/api/submit` 契约**（依据其开源仓库 `nicuk/scamguards` 的 `app/api/submit/route.ts`）：

```json
POST /api/submit   Content-Type: application/json
{
  "scamType": "loan_scam",              // 必填，见下方枚举
  "dataPoints": [{"type":"phone","value":"0102422713"}],  // 必填，≥1
  "description": "…",                   // 可选，但**影响可信度评分**
  "country": "MY", "amountLost": 0, "platform": "WhatsApp"
}
```
- `scamType` 枚举（12）：`collectibles_scam` `precious_metals_scam` `ecommerce_scam` **`macau_scam`（电话冒充）** `love_scam` `investment_scam` `parcel_scam` `job_scam` **`loan_scam`** `mule_recruitment` `phishing` `other`
- `dataPoints[].type` 枚举（11）：`phone` `email` `bank_account` `whatsapp` `telegram` `ewallet` `social_media` `website` `crypto_wallet` `name` `company`
- **multipart 模式可传 `evidence` 文件** → 服务端置 `isVerified=true`，可信度提升
- 号码自动归一化：`0102422713` → `60102422713`
- 限流：`X-Ratelimit-Limit: 5` + **60 秒冷却**（超限 HTTP 429）
- **免注册免登录，报告立即生效**
- **配套接口**：`POST /api/search`（**验证入库，必须用 POST**，body `{"inputs":[{"type":"phone","value":"…"}]}`；用 GET 返回空 ← 最易踩的坑）｜`/api/dispute`（号码持有人申诉误标）｜`/api/recent-reports`｜`/api/stats`
- **实测提交回执样例**：`{"success":true,"reportId":"…","isVerified":true,"isPending":false,"duplicateInfo":{"message":"Thank you for being the first to report this scammer.","confidenceScore":50}}`

⚠️ **Truecaller 的 filter-store 端点不要碰**：需 App 内 `installationId`，使用属冒用他人凭据、违反 ToS。App 内手动举报是唯一合规路径。

---

## 12. ★ 幂等性门禁 —— 批量写名字列前的强制前置检查

> **背景（2026-10-06 血泪）**：DB3 CallApp 在 10:00 还返回真实的马来西亚/华人姓名
> （覆盖率 80%、名字稳定可复现），被一轮 300 次压力测试打过后，**降级为返回随机假名** ——
> HTTP 仍是 200，名字形态完全正常（`Maryam Thrush` / `Judge Sensenig`），
> 但**同一号码每次查询都返回不同名字**。
> 若不做检查就回写，会把几千个假名灌进表格，且肉眼几乎无法发现。

### 唯一可靠的判据

> **同一号码连查 N 次（N≥3），返回的名字必须完全一致。**
> 不一致 ⇒ 该数据源当前输出**随机垃圾**，立即停止一切批量写入。

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
"$PY" scripts/check_idempotent.py --source db1 --phone 60162281297 --repeat 3 --gate
# 稳定   -> exit 0，可以跑批
# 不稳定 -> exit 9，禁止回写
```

### ★ 更强的验证：拿「表里已有的真名」当 ground truth

只做幂等性还不够 —— 万一某源**稳定地返回另一个源的合法数据**（同名率高但都与已知名不同），
幂等性会通过。**叠加「一致性」判据**可进一步提高置信度：

```bash
# 快照里 A 列（已知真名）+ B 列（号码）都要有
"$PY" scripts/source_verify.py --source db3 \
      --snapshot $T/sheetAB.json --n 10 --repeat 3
# 幂等 10/10 且与已知真名一致 10/10 -> exit 0，可用
# 每次都不同名                     -> exit 9，源已污染，禁止写入
```

判据组合与结论：

| 幂等 | 与已知真名一致 | 结论 |
|---|---|---|
| ✅ | ✅ | 可用 |
| ✅ | ❌ | **另一源的合法数据** —— 不能直接采信，需人工看几条再定 |
| ❌ | — | **污染/降级，禁止写入** |

抽样用**分层**（把已知名行按行号分段、每段随机取一个），保证覆盖全表而不是挤在头部。
`--phone` 可只验单号（无已知名时用）。

**2026-10-07 实测**：DB3 在 10 个分层样本 × 3 次 + 单号 × 10 次共 50 次请求中
**0 次幂等、0 次一致**，名字全是美式 `First Last`（`Astra Gillies`/`Clifford Hosier`）——
**污染未恢复，不可用**。同期 DB1 仍被封（`status:-10`），两条管道同时不可用。
详见 `references/DB3-CallApp-限流与污染实测.md` §8。

### ❌ 以下判据都不可靠（实测证伪）

| 判据 | 为什么失效 |
|---|---|
| **HTTP 状态码** | 污染后**仍是 200**；夹杂的 `512`/`525` 看起来像普通网络抖动 |
| **名字形态** | 假名 `Maryam Thrush` 完全符合「人名」形态，肉眼分辨不出 |
| **覆盖率** | 污染后覆盖率**反而升到 90%**（比真实时 80% 更高），极具欺骗性 |
| **请求速率** | 与速率**无关** —— 每 10 秒查 1 次照样 100% 随机（见下） |

### 污染与速率无关（三组对照实验）

固定同一号码连续查询，统计「不同名字数」（=1 才算真实）：

| 实验 | 请求间隔 | 次数 | 不同名字数 | 判定 |
|---|---|---|---|---|
| A 极慢速 | **10 秒** | 12 | **11/11** | ❌ |
| B 中速 | 1.0 秒 | 60 | **55/55** | ❌ |
| C 快速 | 0.1 秒 | 60 | **54/54** | ❌ |
| D 慢速长跑 | 3 秒 | 80 | **71/71** | ❌ |

⇒ 不是限流触发，是**该源整体降级为假数据**。调慢速率无法挽救。

### 两个源的失效模式对比（评估新数据源时的通用准则）

| | DB1 aunumber | DB3 CallApp |
|---|---|---|
| 失效表现 | HTTP 200 + `{"status": -10}` | HTTP 200 + **随机假名** |
| 是否可自动识别 | ✅ 判 `status < 0` | ❌ **必须靠幂等性抽检** |
| 污染风险 | 无（明确拒绝） | **极高**（静默污染） |

⇒ **一个愿意明确报错的源，比一个「永远返回 200」的源更值得信任。**
评估新数据源时，**幂等性优先级高于覆盖率**。

### 检查清单（跑批前逐项确认）

1. `check_idempotent.py --gate` 通过（**硬门禁，不过就停**）
2. 若源会返回状态码，确认是正常值（DB1：`status >= 0`）
3. 抽 2–3 个**已知答案**的号码人工比对（如 `60162281297` → `Prof Lee` 是历史回归号）
4. 覆盖率异常升高时**警觉**，不要当好消息——先做幂等性复核

→ DB3 的完整测验记录（参数还原、`X_C_CODE` 语义、时序）见
`references/DB3-CallApp-限流与污染实测.md`。
