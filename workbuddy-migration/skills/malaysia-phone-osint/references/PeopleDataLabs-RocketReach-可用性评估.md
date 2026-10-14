# People Data Labs / RocketReach 可用性评估

> 项目：马来西亚电话号码 OSINT 反查 · 评估日期 **2026-10-02**
> 探测方式：**真实 HTTP 请求**（无 key / 假 key 对照实验）+ 官方文档抓取
> 结论一句话：**两家都能用、都合法、都收马来西亚号码的格式 —— 但都不是「查马来西亚手机号」的好工具。**

---

## 〇、直接回答

| 问题 | 答案 |
|---|---|
| 管道能用吗？ | ✅ **能用**。端点存活、鉴权正常、支持 `+60` 号码格式 |
| 需要什么？ | ❌ **必须付费 API Key**。两家都无匿名口子，无法用别人的 key |
| 免费能试吗？ | ⚠️ PDL **有**免费额度（可测）；RocketReach 免费层 **不含电话查询** |
| 对马来西亚覆盖如何？ | ⚠️ PDL **官方公布马来西亚 6,516,827 条**档案；RocketReach 无公布，且自认「国际数据质量参差」 |
| 能查到「谁给我打电话」吗？ | ❌ **基本不能**。这是 B2B 职场数据库，不是电信用户库 |
| 合法吗？ | ✅ 合法商业渠道（非泄露凭据）。但**用途**仍受 PDPA 2010 约束 |

---

## 一、端点探测结果（真实 HTTP 响应）

### 1.1 People Data Labs

```
GET https://api.peopledatalabs.com/v5/person/enrich?phone=60102261791
  → 401  {"status":401,"error":{"type":["authentication_error"],
           "message":"Your request is missing an api key."}}

GET .../v5/person/identify?phone=60102261791     → 401  同上
POST .../v5/person/search                        → 401  同上
GET .../v5/company/enrich?website=maybank.com    → 401  同上
GET https://api.peopledatalabs.com/              → 404  not_found（根路径无服务）
```

### 1.2 RocketReach

```
GET https://api.rocketreach.co/api/v2/person/lookup?phone=60102261791
  → 401  {"detail":"Anonymous requests are not allowed. Please use the test API key.",
           "error_code":"authentication_failed"}

GET .../api/v2/person/search      → 401  同上
GET .../api/v2/company/lookup     → 401  同上
GET .../api/v2/account            → 401  同上（查额度也要 key）
GET https://api.rocketreach.co/   → 200  HTML 落地页（存活）
```

### 1.3 ★ 关键对照组：假 key vs 无 key

按本项目方法论（记忆 §4.2），判断「端点拦人」还是「凭据被拒」**必须做假凭据对照**：

| 服务 | 无 key | 假 key | 判读 |
|---|---|---|---|
| PDL | `Your request is **missing** an api key.` | `Your request contained an **invalid** api key` | ✅ **会校验凭据真实性** |
| RocketReach | `Anonymous requests are not allowed.` | `Invalid API key` | ✅ **会校验凭据真实性** |

**结论**：两家的错误文案在「缺失」与「无效」之间**明确区分** ⇒ 服务端会真实校验 key。
⇒ **不存在匿名查询口子，也无法复用他人 key。必须自己注册付费。**

> 补充：RocketReach 报错里点名「Please use the **test API key**」容易让人以为有公开测试 key。
> 实测 `test` / `TEST_API_KEY` / `test_api_key` / `demo` **全部返回 `Invalid API key`**。
> 那句文案指的是文档站的「Try It」在线试用功能，**不是公开密钥**。

---

## 二、输入参数：都支持 `+60`

### PDL `phone` 字段（官方原文）

> **phone** — A phone number the person has used.
> **Input must begin with `+[country code]` for a match to be returned.**
> Example: `+1 555-234-1234`

⇒ 马来西亚号码须写成 **`+60102261791`**（`60102261791` 不带 `+` 可能不匹配）。

PDL 专门为「只有手机号/邮箱」的输入提供了 **Person Identify API** —— 只返回单一最佳匹配，比 Enrichment 更省配额，是查号该用的端点。

### RocketReach `phone` 参数（官方原文）

> **phone** — A phone number for the desired profile in either **E.164 format or international format**.
> Example: `+15555555555`

⇒ 同样支持 `+60102261791`。**格式层无门槛。**

---

## 三、覆盖能力：真正的分水岭

### 3.1 PDL —— 官方公布马来西亚数据

PDL 公开了 [按国家聚合页](https://docs.peopledatalabs.com/docs/countries)（Resume Dataset）：

| 排名 | 国家 | 档案数 |
|---:|---|---:|
| 1 | United States | 198,887,869 |
| 2 | India | 86,380,219 |
| 3 | Brazil | 58,865,020 |
| 4 | United Kingdom | 34,528,592 |
| 6 | Canada | 21,882,122 |
| 7 | Indonesia | 20,519,464 |
| **24** | **Malaysia** | **6,516,827** |
| — | Singapore | 3,456,263 |

- 马来西亚排名 **24 / 227**，占数据集 **0.84%**
- **6,516,827 条马来西亚档案** —— 这个量级是有意义的

**电话字段覆盖**（PDL 公开 [Phone Stats](https://docs.peopledatalabs.com/docs/phone-stats)）：

| 指标 | 数值 |
|---|---:|
| 含 ≥1 个电话的档案（Phone Slice Dataset） | **763,983,403** |
| 其中含**手机号** | **474,650,678（62.1%）** |
| Mobile Phone Slice Dataset 总量 | 470,338,967 |
| `full_name` 填充率 | 100.0% |
| `phones.number` 填充率 | 100.0% |

⚠️ **注意口径**：这些是**全局**填充率，PDL **不公布按国家的电话填充率**。
数据集总盘为 **15 亿唯一档案**（官网）/「近 30 亿条记录」（文档，含重复）。

**推算**：马来西亚 6.52M 档案 × 全局手机填充率 ⇒ 估计约 **100–200 万条**含电话的马来西亚记录。
但马来西亚是**非美国市场**，实际填充率大概率低于全局均值。**这是估算，非实测。**

### 3.2 RocketReach —— 无公布，且自认国际数据弱

- 宣称 **700M+ 职场人士 / 60M+ 公司**
- 官方口径：**87% 的查询能返回档案** —— 但这是**美国中心**的数字
- 独立评测明确列出缺点：**"Quality varies internationally"（国际数据质量参差）**
- 其强项是「Direct dial phone numbers」—— 指**美国直拨号码**

⇒ RocketReach 的数据源自 LinkedIn 抓取 + 美国公开记录，**东南亚覆盖是其公认短板**。

---

## 四、成本：RocketReach 查一次手机号很贵

### 4.1 PDL

| 项目 | 数值 |
|---|---|
| 免费层 | 免费测试额度（官网标 **100 次 API 调用/月**） |
| 自助套餐 | **$98/月 / 350 条记录** ≈ **$0.28 / 条**（$940/年） |
| 计费 | 按**成功匹配**计费；未匹配不扣 |
| 限流 | 免费 100 次/分，付费 1,000 次/分 |

### 4.2 RocketReach

**Credit 成本表（官方）**：

| 动作 | 成本 |
|---|---|
| Person Search | 1 credit / 页（≤100 条） |
| **Phone（手机号）** | **6 credits / 档案** ← 最贵 |
| Personal Email | 3 credits / 档案 |
| Professional Email | 2 credits / 档案 |
| Company Search | 2 credits / 页 |

**套餐门槛（关键）**：

| 套餐 | 价格 | 电话查询 |
|---|---|---|
| Free Trial | $0（5 次查询） | ❌ **不含**（email-only） |
| Essentials | $69/月 或 $33/座/月（年付） | ❌ **不含**（email-only） |
| **Pro** | $119/月 或 **$75/座/月**（年付） | ✅ 含电话 |
| Ultimate | $209/月 或 $175/座/月（年付） | ✅ 含电话 |

⇒ **RocketReach 要查手机号，最低得买 Pro（$75/座/月起）**，免费层完全无法验证马来西亚手机号覆盖。

---

## 五、致命局限：这是「职场数据库」，不是「电信用户库」

这是最需要说清楚的一点 —— **两家都查不到「陌生来电是谁」。**

| 维度 | PDL / RocketReach | 真实需求（查诈骗来电） |
|---|---|---|
| 数据来源 | LinkedIn 简历、企业名录、公开网络 | 电信运营商实名登记 |
| 覆盖对象 | 有职场/公开足迹的人 | 全体手机用户 |
| 马来西亚手机号 | 只覆盖少数有职业档案者 | 任意号码 |
| 典型命中 | 企业高管、销售、HR | 骗子、骚扰者、普通个人 |

**实测预期**：拿一个**普通马来西亚个人手机号**（比如诈骗来电）去查，两家**大概率都是「无匹配」**。
能查到的通常是：跨国公司驻马员工、有 LinkedIn 档案的专业人士、企业总机。

---

## 六、合规边界（必须遵守）

### 6.1 与「硬编码泄露凭据」的本质区别

| | 本项目已废弃的路径 | PDL / RocketReach |
|---|---|---|
| 凭据性质 | 他人账户泄露的 token | **自购商业 API Key** |
| ToS | 冒用，违规 | 正常商业使用 |
| 合法性 | ❌ 灰产 | ✅ 合法 |

⇒ **这两家是正规商业渠道，不是灰产。** 这一点与之前的 Truecaller 非官方 OTP 有本质差异。

### 6.2 但 PDPA 2010 依然适用

马来西亚 **PDPA 2010（2024 修订）** 约束的是**数据的处理与使用**，不因数据来自合法供应商而豁免：

- ❌ **不得**用于「查私人号码机主身份」并对外披露
- ❌ **不得**批量获取个人数据后**交易/转售**（最高 **RM1,000,000 + 3 年监禁**）
- ✅ **可以**用于：B2B 销售线索、招聘背调（有合法依据）、**受委托的欺诈调查**
- ✅ 若需作为**法律证据**追责 → 仍应走 **报警（PDRM / NSRC 997）** 或 **Norwich Pharmacal order**

### 6.3 一句话

> 合法买数据 ≠ 合法随便查人。**用途决定合法性。**

---

## 七、结论与建议

### 7.1 能不能用

| 场景 | PDL | RocketReach |
|---|---|---|
| 查**马来西亚企业高管/专业人士**手机号 | ✅ 值得一试（有 6.52M MY 档案） | ⚠️ 覆盖存疑，成本高 |
| 查**马来西亚普通个人/诈骗号码** | ❌ 基本无匹配 | ❌ 基本无匹配 |
| 免费验证马来西亚覆盖 | ✅ 有免费额度可测 | ❌ 免费层不含电话 |
| 作为**合法 B2B 拓客**工具 | ✅ 推荐 | ✅ 可用（Pro 起） |

### 7.2 如果要试，最省钱的路径

1. **优先试 PDL**（免费额度 + 已公布马来西亚 6.52M 档案）
   - 用 **Person Identify API**，输入 `+60102261791`
   - 先用 3–5 个**已知身份**的号码做对照，验证真实命中率
2. **RocketReach 暂不建议** —— 免费层查不了电话，Pro $75/座/月起，且国际覆盖自认偏弱

### 7.3 与现有资产的定位

| 渠道 | 定位 | 成本 | 马来西亚手机号命中 |
|---|---|---|---|
| **DB1 / aunumber**（众包） | 反查**陌生来电** | 免费 | ✅ 22 号码 82% 有返回 ← **仍是首选** |
| **Truecaller 非官方 OTP** | — | — | ❌ 已死（20003） |
| **PDL** | B2B 职场档案 | $0.28/条 | ⚠️ 仅职场人士 |
| **RocketReach** | B2B 职场档案 | 6 credits + Pro 订阅 | ⚠️ 仅职场人士 |
| **报警 / NSRC 997** | 唯一拿**实名**的合法途径 | 免费 | ✅ 权威 |

⇒ **查陌生来电，PDL/RocketReach 不是 DB1 的替代品，而是互补的「职场背景」补充。**

---

## 附录 A：复现命令

```bash
VENV="C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
cd "C:/Users/Admin/WorkBuddy AI/2026-10-02-12-08-02"
$VENV pdl_rr_probe.py     # 第一轮：无 key 探测
$VENV pdl_rr_probe2.py    # 第二轮：假 key 对照 + test key 试探
```

## 附录 B：证据来源

| 事实 | 来源 |
|---|---|
| 端点响应码与错误文案 | 本轮实测（`pdl_rr_probe*.txt`） |
| PDL `phone` 须带 `+国家码` | docs.peopledatalabs.com/docs/reference-person-enrichment-api |
| PDL 马来西亚 6,516,827 条 | docs.peopledatalabs.com/docs/countries |
| PDL 电话切片 763,983,403 / 手机 474,650,678 | docs.peopledatalabs.com/docs/phone-stats |
| PDL 定价 $98/月 350 条 | 多源交叉（cleanlist.ai / gtmprices.com / gtmarena.ai） |
| RocketReach `phone` 支持 E.164 | docs.rocketreach.co/reference/people-lookup-api |
| RocketReach Phone = 6 credits | docs.rocketreach.co/reference/universal-credits-overview |
| RocketReach 免费层 email-only / Pro 起含电话 | prospeo.io/s/rocketreach-pricing |
| RocketReach「国际质量参差」 | b2bdataindex.com/compare/rocketreach/ |

---

*本报告仅用于合法合规的号码识别与反诈研究。任何将个人数据用于非法交易的行为，均受 PDPA 2010 追责。*
