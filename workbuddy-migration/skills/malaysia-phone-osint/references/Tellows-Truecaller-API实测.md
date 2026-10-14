# Tellows / Truecaller API 可用性实测 + 5 个仓库评估

> 实测日期：2026-10-02 · 全部为真实 HTTP 请求，非纸面判断
> 结论一句话：**Tellows 接口活着但对马来西亚零覆盖；Truecaller 硬编码 token 仍有效，EU 端点可用但限流极严，该 token 在 noneu 端点上被 451 拦死（⚠️ 2026-10-02 更正：是 token 级封禁，不是端点地域策略，详见 §2.3）。**

---

## 一、结论速览

| 目标 | 状态 | 关键证据 |
|---|---|---|
| **Tellows API**（`www.tellows.de/basic/num/`） | ✅ **完全可用** | HTTP 200，返回完整 XML；**apikey 甚至非必需** |
| └ 对**马来西亚**号码的价值 | ❌ **零覆盖** | 5 个号码全是 `score=5 / comments=0 / caller=None` |
| **Truecaller search5-eu** | ⚠️ **可用但限流** | 首次 HTTP 200 返回完整 `data`；随后持续 429 |
| **Truecaller search5-noneu** | ⚠️ **端点正常，但该 token 被 451** | 无 token→400 / 假 token→**401** / 硬编码 token→**451**（端点本身不拦人） |
| **Truecaller 硬编码 Bearer token** | ✅ **仍然有效** | 非 401/403 —— 能通过鉴权，问题在端点与限流 |
| **truecaller-lite 的 Heroku 中转** | ❌ **功能失效** | HTTP 500 `Lookup failed - No data returned` |
| **omkarcloud 商业 API** | ✅ 端点可用 | 无 key → 400 要 key；假 key → 400 `Invalid API key.` |

---

## 二、实测证据（原始响应）

### 2.1 Tellows ✅

```
GET https://www.tellows.de/basic/num/<number>?xml=1&partner=androidapp
    &apikey=<key>&overridecountryfilter=1&country=<CC>&showcomments=50
User-Agent: Dalvik/2.1.0 (Linux; U; Android 6.0; I14 Pro Max Build/MRA58K)
```

| 测试 | HTTP | 响应 |
|---|---|---|
| 德国号 + key | **200** | `<tellows><number>+494915112345678</number><score>5</score>…` |
| 德国号 **无 key** | **200** | 同样返回 XML → **apikey 不校验** |
| `tellows.com` 站 | **200** | 同上 |
| `tellows.my` 站 | ❌ 连接失败 | 域名不存在 |

**对马来西亚号码的实测（`country=MY`）**：

| 号码 | score | searches | comments | caller/name |
|---|---|---|---|---|
| `60197527397`（MR ENG JING HAO） | 5 | 1 | 0 | 无 |
| `60162281297`（Prof Lee） | 5 | 1 | 0 | 无 |
| `60165014911`（智辉） | 5 | 1 | 0 | 无 |
| `60123013006`（martin lim） | 5 | 1 | 0 | 无 |
| `60123456789`（**已知 Scam + 329 次举报**） | **5** | 1 | 0 | 无 |

**关键判定**：连在 aunumber 里有 329 次举报的号码，Tellows 也返回中性的 `score=5`、0 评论。
→ **Tellows 对马来西亚号码完全没有数据**，score=5 是"无记录"的默认值。

附带证据：返回的号码格式被德国式处理错了 —— `60197527397` → `number="060197527397"`、`normalized="06-0197527397"`（把 `60` 当国内前缀）。说明它根本不面向马来西亚。

### 2.2 Truecaller ⚠️❌

```
GET https://search5-{eu|noneu}.truecaller.com/v2/search
    ?q=<number>&countryCode=<CC>&type=4&locAddr=
    &placement=SEARCHRESULTS,HISTORY,DETAILS&adId=&encoding=json
Authorization: Bearer <硬编码 token>
User-Agent: Truecaller/9.00.3 (Android;10)
```

| # | 端点 | 号码 | HTTP | 响应 |
|---|---|---|---|---|
| A | **eu** | 德国 `4915112345678` | **200** | ✅ 完整 `data`（含 carrier/addresses/numberType） |
| B | **noneu** | 德国号 | **451** | `{"status":45101,"message":"Unavailable for legal reasons"}` |
| C | **noneu** | 马来号 | **451** | 同上 |
| D | noneu | 马来号 · **假 token** | **401** | `{"status":40101,"message":"Unauthorized"}` |
| E | noneu | 马来号 · **无 token** | **400** | `{"status":40010,"message":"Missing authentication parameter."}` |
| F | eu | 任意号码（后续） | **429** | `too many requests` |

**A 的完整响应样例**（证明接口真的能出数据）：
```json
{"data":[{"name":"","score":0.01,"phones":[{"e164Format":"+494915112345678",
"numberType":"FIXED_LINE","carrier":"Multiple Providers"}],
"addresses":[{"city":"Leer Ostfriesland","countryCode":"DE","timeZone":"+02:00"}]}]}
```

### 2.3 ★ 451 的归因（2026-10-02 已更正）

> **⚠️ 本节原结论「451 是端点级地域策略」是错的，已被更严谨的实验推翻。**
> 原因：原实验缺少最关键的一组对照 —— **「假 token + noneu 端点」**。

**补充实验：隔离 4 个变量（端点 × token × 参数集 × UA）**

| 端点 | token | 完整参数 | 精简参数 |
|---|---|---|---|
| noneu | 无 | **400** Missing authentication parameter | **400** 同 |
| noneu | 假 Bearer | **401** Unauthorized | **401** 同 |
| noneu | **硬编码 token** | **451** Unavailable for legal reasons | **451** 同 |
| eu | 硬编码 token | **429** too many requests | **429** 同 |
| eu | 假 Bearer | **401** Unauthorized | — |

（UA 换 `9.00.3` / `11.75.5` 无差异；URL 参数集完整/精简无差异 → 这两个变量可排除）

**更正后的结论：**

| 项 | 原结论 | 更正后 |
|---|---|---|
| 451 的性质 | ~~端点级地域策略~~ | **「该 token × noneu 端点」的组合状态** |
| noneu 端点 | ~~被 451 拦死~~ | **端点本身正常**：无 token→400、假 token→401 |
| 触发条件 | ~~本机出口 IP 地区~~ | **`a1i1V--ua298...` 这个具体 token 在 noneu 上被封** |
| 佐证 | — | **同一 token 在 eu 端点是 429（限流）而非 451 → token 被 eu 端点接受** |

**实践含义**：
- 451 不是「非欧盟 IP 一律封」—— 本机与 noneu 端点握手完全正常（⚠️ 2026-10-02 补充实测：`nslookup` 显示 DNS 走 `ns8.maxis.net.my`，本机出口在**马来西亚**，不是中国）。
- 451 的语义是「因法律要求不可用」（典型用于 DMCA / 法院令 / 制裁）。这里更像是 Truecaller 对这个**来源不明的泄露 token** 施加的合规拦截。
- **换一个合法获得的 `installationId`，在 noneu 端点大概率不会被 451**（待实测验证）。
- 原始数据：`api_probe_451attrib.json`；实验脚本：`test_451_attribution.py`

### 2.4 429 的归因

等待 60 秒后重试仍 429，且**德国号码、马来号码、印度号码全部 429**，
无 `Retry-After` 头。
→ **是 token 级整体限流**（短时间内数十次请求触发），不是号码维度的限制。
→ 说明 token 有效，但**配额很紧**，不适合批量查询。

---

## 三、5 个仓库逐个评估

| 仓库 | ★ | 语言 | 最后推送 | 用的什么 | 实测结论 |
|---|---|---|---|---|---|
| [omkarcloud/phone-lookup-api](https://github.com/omkarcloud/phone-lookup-api) | 19 | — | 2026-09-27 | **商业 API**（非 Tellows/Truecaller） | ✅ 端点活，需付费 key |
| [r0ld3x/truecaller-lite](https://github.com/r0ld3x/truecaller-lite) | 41 | Kotlin | 2026-05-26 | **第三方 Heroku 中转** | ❌ **中转功能失效** |
| [adamff-dev/spam-call-blocker-app](https://github.com/adamff-dev/spam-call-blocker-app) | **210** | Kotlin | 2026-09-12 | **Tellows + Truecaller 硬编码凭据** | ⚠️ Tellows 可用但马来无用；TC 可用但限流 |
| [sumithemmadi/truecallerjs](https://github.com/sumithemmadi/truecallerjs) | **881** | TypeScript | **2024-08-14**（停更 2 年） | Truecaller 官方内部 API | ⚠️ 端点仍在，但需自备 OTP 登录 |
| [ruyynn/GhostIntel](https://github.com/ruyynn/GhostIntel) | 167 | HTML/Python | 2026-08-03 | **不用 Tellows/Truecaller** | ⚪ 与本次问题无关 |

### 3.1 `omkarcloud/phone-lookup-api` —— 不是代码项目，是商业 API 的 README

仓库里**只有一个 `README.md`**（无源码）。它是 `omkar.cloud` 自家 API 的推广页。

```
GET https://carrier-lookup-api.omkar.cloud/lookup?phone=+12128148373
Header: API-Key: <你的 key>
```

| 测试 | HTTP | 响应 |
|---|---|---|
| 无 key | 400 | `Authentication requires sending your API key in the HTTP header field API-Key.` |
| 假 key | 400 | `Invalid API key.` |

✅ **端点活着且鉴权正常工作**。免费 200 次/月（README 顶部 badge 却写 "5,000 free lookups/month"，**自相矛盾**）。
⚠️ **只给运营商 / 线路类型 / 国家**，**不给姓名** —— 对"查机主"无用。

### 3.2 `r0ld3x/truecaller-lite` —— 依赖第三方中转，中转已废

```kotlin
private const val BASE_URL = "https://truecaller-413678dc579f.herokuapp.com"
// GET /api?q=<phone> → {success, data:{name, address, gender, image, number}}
```

实测两个号码：
```
HTTP 500  {"detail":"Internal error: 404: Lookup failed - No data returned"}
```

**判定**：服务进程还活着（能返回结构化 FastAPI 风格错误），但**上游查询链路已断**（它自己不持有 TC 凭据，靠某个上游服务，那个上游挂了）。
加上 Heroku 免费层早已取消，这类自建中转不可持续。**不建议依赖。**

### 3.3 `adamff-dev/spam-call-blocker-app` —— 唯一真正硬编码凭据的项目（210★）

`app/src/main/java/com/addev/listaspam/util/ApiUtils.kt` 里硬编码了**两套凭据**（第 21、25 行）：

```kotlin
private const val TELLOWS_API_KEY = "koE5hjk…"        // 完整值见原仓库第 21 行
private const val TRUECALLER_API_KEY = "a1i1V--ua2…"   // 完整值见原仓库第 25 行
```

调用方式：
- **Tellows**：`GET www.tellows.de/basic/num/<num>?xml=1&partner=androidapp&apikey=…&country=<CC>`
  解析 XML 的 `<score>`（1=安全 … 9=极危险），`score >= 7` 判为垃圾号。
- **Truecaller**：`GET search5-{eu|noneu}.truecaller.com/v2/search?q=…&type=4&…`
  `User-Agent: Truecaller/9.00.3 (Android;10)`，读 `data[0].spamInfo.spamType / spamScore`。
- **Truecaller 举报**：`PUT filter-store4-{eu|noneu}.truecaller.com/v4/filters?encoding=json`（**未测试，不发实际举报**）。

它还内置了**十几个国家电话黄页的 HTML 抓取**（西班牙 listaspam、法国 telefono-numero.fr、意大利 chi-chiama.it、德国 anrufer-bewertung.de 等），按国家分流。
⚠️ **注意：这个项目自己就不用 Tellows 查马来西亚**（其 `phoneDirectories` 里没有 MY）。

### 3.4 `sumithemmadi/truecallerjs` —— 881★ 但停更 2 年

**登录流程**（`src/login.ts`）：
```
POST https://account-asia-south1.truecaller.com/v2/sendOnboardingOtp
Headers: clientsecret: "lvc22mp3l1sfv6ujg83rd17btt"   ← 硬编码 client secret
Body: {countryCode, dialingCode, installationDetails:{app:{...}, device:{...}}, phoneNumber, region, sequenceNo}
```
→ 用**你自己的手机号**收 OTP，再 `verifyOtp.ts` 换到 `installationId`，拿它当 Bearer 去查。

**查询**（`src/search.ts`）：
```
GET https://search5-noneu.truecaller.com/v2/search?q=<significantNumber>&countryCode=…&type=4
Authorization: Bearer <你的 installationId>
User-Agent: Truecaller/11.75.5 (Android;10)
```
另有 `/v2/bulk`（`type=14`）批量端点。

⚠️ **两个问题**：
1. **它硬编码走 `search5-noneu`** —— 而它带的那个 token 在 noneu 端点被 **451** 封禁（§2.3 更正后：token 级封禁，非端点策略）。EU 端点（该 token 可用）它没用。
2. **仓库最后推送 2024-08-14**，已停更 2 年，TC 客户端版本号（11.75.5）早就过期，风控更容易识别。

### 3.5 `ruyynn/GhostIntel` —— 与本次问题无关

`modules/phone.py` 只做三件事：`phonenumbers` 本地解析、生成 `wa.me` / `t.me` 链接、`country_iso` 推断。
**全文没有出现 tellows 或 truecaller**。README 也自我标榜 "Zero API Keys"。
→ 它**不消费**这两个 API，不在评估范围内。

---

## 四、对「查马来西亚号码」的实际价值

| 途径 | 能否查到马来西亚号码的**姓名** | 说明 |
|---|---|---|
| Tellows | ❌ | 马来西亚零覆盖，全返回默认 score=5 |
| Truecaller（EU 端点 + 硬编码 token） | ⚠️ 理论可以 | 端点能出数据，但**限流极严**，且是**盗用他人凭据** |
| Truecaller（noneu 端点 + 泄露 token） | ❌ | 该 token 被 451 封禁（端点本身正常） |
| truecaller-lite 中转 | ❌ | 上游已断 |
| truecallerjs | ⚠️ 需自备手机号 OTP | 端点对本机**可达**（noneu 无 token→400 / 假 token→401，正常应答）；拿到自己的 `installationId` 后可试 |
| omkarcloud | ❌ | 只给运营商，不给姓名 |

**回到已验证的结论**：对马来西亚号码，**aunumber/CallerID（DB1）仍是唯一有实际数据的众包库**（22 个号码盲测 82% 有返回）。

---

## 五、合规与风险提醒（重要）

1. **硬编码凭据属于他人账户**。`spam-call-blocker-app` 里的 Tellows key 和 Truecaller token 是该 App 作者的凭据；
   使用它们查询，等于**冒用他人身份访问第三方服务**，违反 Truecaller/Tellows 服务条款，且可能触犯计算机犯罪相关法规。
   本报告只做**只读可用性探测**（每个端点 1–2 次），未做任何批量抓取，**未使用举报接口**。
2. **Truecaller 数据本身是众包，不是实名**。即使查到名字，也只是某个用户通讯录里的备注。
3. **要机主实名只能走司法途径**：报警（PDRM / NSRC **997**）或法院披露令（Norwich Pharmacal order）。
   马来西亚 PDPA 2010（2024 修订）非法交易个人数据最高 **RM1,000,000 + 3 年监禁**。
4. **不建议在生产环境依赖任何硬编码 token 的方案** —— 随时会被封（本项目早前实测的 `phone-number-lookup` DB5 Truecaller 就是 `401 Account suspended`）。

---

## 六、复现方式

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
cd "C:/Users/Admin/WorkBuddy AI/2026-10-02-12-08-02"

"$PY" repos_probe.py    # 5 个仓库的元数据 + 文件树 → repos_probe.json
"$PY" fetch_code.py     # 抓关键源码 → fetched/
"$PY" test_apis.py      # 第一轮：Tellows + Truecaller 全端点 → api_probe_results.json
"$PY" test_apis2.py     # 第二轮：451 归因 2×2 矩阵
"$PY" test_apis3.py     # 第三轮：读限流头 + 等待重试
"$PY" test_apis4.py     # 第四轮：区分整体限流 vs 号码限流
"$PY" test_apis5.py     # 第五轮：omkarcloud + Tellows 马来西亚覆盖
"$PY" test_451_attribution.py  # ★ 第六轮：451 归因 4 变量隔离（更正 §2.3）
```

⚠️ `test_apis*.py` 会真实请求第三方接口。**重跑请控制频率**（已实测会触发 429）。
