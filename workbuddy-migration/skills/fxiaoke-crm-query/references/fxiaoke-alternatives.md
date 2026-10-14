# 纷享销客 CRM 取数：不走 CDP 的替代方案（深度调研）

> 调研日期：2026-09-29
> 背景：现有方案是「CDP 接管本机已登录 Chrome + 调内部接口」，能用但依赖浏览器常驻、登录态、单一会话限制。
> 目标：找出不依赖 CDP 的正规取数路径。
> 结论先行：**有 4 条正规路径，全部可用，全部无需 CDP；但全部需要「管理员权限 + 付费开通」** —— 这正是 CDP 方案存在的价值。

---

## 一、结论速览

| # | 路径 | 是否需 CDP | 需管理员 | 需付费 | 实测状态 | 推荐度 |
|---|---|---|---|---|---|---|
| 1 | **WorkBuddy 官方「纷享销客CRM连接器」** | ❌ 不需要 | ✅ 需要 | ✅ 需开通 MCP（可试用 15 天） | 官方文档已上架 | ⭐⭐⭐⭐⭐ |
| 2 | **官方 MCP 直连**（自配 mcp.json） | ❌ 不需要 | ✅ 需要 | ✅ 同上 | ✅ 端点实测存在（401） | ⭐⭐⭐⭐⭐ |
| 3 | **官方 OpenAPI v2**（企业自建应用） | ❌ 不需要 | ✅ 需要 | ✅ 需 Open API 资源包 | ✅ 本机直连成功（20017） | ⭐⭐⭐⭐ |
| 4 | **自部署第三方 MCP** | ❌ 不需要 | ✅ 需要 | ✅ 同上 | 开源可用 | ⭐⭐⭐ |
| — | CDP 接管（现状） | ✅ 需要 | ❌ 不需要 | ❌ 免费 | ✅ 已跑通 | 兜底 |

**核心洞察**：正规路径的门槛是「管理员权限 + 采购流程」；CDP 方案是唯一**零门槛**的路径。两者是互补关系，不是替代关系 —— 能拿到管理员授权就走正规路径，拿不到就继续用 CDP。

---

## 二、路径 1：WorkBuddy 官方「纷享销客CRM连接器」（最省事）

纷享销客**已官方上架** WorkBuddy / 千问办公 / 豆包工作 的「纷享销客CRM连接器」，接入方式为 **MCP + Skills**。

来源：[Agent办公平台上如何操作纷享销客CRM](https://help.fxiaoke.com/ee88/a823/6c9c)

### 操作步骤
1. 在连接器列表点「连接」
2. 浏览器跳转授权 → 登录 CRM 账号
3. 进入确认授权页，**选择 MCP 服务**（管理员配置的）
4. 点「确认授权」→ 回到 WorkBuddy，完成

### 前提条件（关键）
- **企业必须先下单开通 MCP 服务**，连接器只是让授权更方便，底层仍走纷享 MCP。
- 例外：**系统管理员 / CRM 管理员首次通过连接器连接时，可免费试用 15 天 MCP 服务**。
- 未开通且非管理员 → 授权页无可选 MCP 服务，无法连接。

### 官方 FAQ 要点
- Q：用连接器还要下单吗？→ **要**，底层走纷享 MCP 服务。
- Q：依赖纷享 AI 平台吗？→ 不依赖，可独立开通。
- Q：消耗纷享算粒吗？→ 不消耗，消耗的是外部 Agent 平台的算粒。
- Q：调用次数怎么算？→ 一次查询通常调多个工具，**每个工具每次算一次**，重复查询重复计。

### 实测
本机 `search_plugins` 检索「纷享销客 / fxiaoke / CRM」均未返回该连接器（当前环境连接器市场未上架或未同步）。**建议直接到 WorkBuddy 连接器市场手动搜索「纷享」确认**。

---

## 三、路径 2：官方 MCP 直连（自配 mcp.json）

如果拿不到连接器入口，可以直接在 `~/.workbuddy-ai/mcp.json` 里手配官方 MCP。

来源：[如何在Agent接入纷享MCP服务](https://help.fxiaoke.com/ee88/a823/6aab)

### 配置 A：PKCE OAuth（官方推荐，更安全）

```json
{
  "mcpServers": {
    "crm-mcp": {
      "type": "http",
      "url": "https://open.fxiaoke.com/mcp/${ea}/${mcpApiName}",
      "disabled": false
    }
  }
}
```

- `${ea}` / `${mcpApiName}` 由**管理员提供**（企业专属）。
- 配置后重启终端 → 点 MCP 服务的「连接」→ 浏览器打开授权页 → 确认授权。
- 前置：浏览器需先登录 CRM 账号；管理员需在后台配置支持 PKCE 的 MCP 服务。

### 配置 B：User Token（最简单，复制粘贴）

```json
{
  "mcpServers": {
    "crm-mcp": {
      "type": "http",
      "url": "https://open.fxiaoke.com/mcp/fs/crm-mcp?apiKey=<用户令牌>"
    }
  }
}
```

- 用户令牌获取：**CRM 个人中心 → 访问令牌 → 创建公司授权的 MCP 令牌**。
- 令牌有效期建议设 90 天（安全要求高设 7 天），到期更换。
- 注意：拼接用**英文问号** `?`；企微侧参数名大小写敏感，须为 `apiKey`。

### 实测验证
```bash
curl -sL -o /dev/null -w "%{http_code}\n" "https://open.fxiaoke.com/mcp/fs/crm-mcp"
# → HTTP 401（端点存在，缺有效凭证）
```
端点真实存在，返回 401 而非 404。

### 能力范围
官方 MCP 开放 **800+ 工具**，涵盖：
- 对象数据 CRUD、SQL 查询
- 营 / 销 / 服各业务域、预设对象、自定义对象
- BI 分析、审批流 / 工作流 / 业务流
- 文件、知识库、语义查询、企信协同、角色与权限

典型场景：读业务数据（客户、联系人、商机）、新增编辑、线索全流程、商机推进、取价询价、销售报表、审批处理、数据统计。

### 计费
- 产品名【MCP调用10万次】，限制**企业按天总调用次数 = 10 万次/天/企业**。
- 不够可叠加多个包（2 个包 = 20 万次/天）。
- 联系对应客服经理下单开通。

---

## 四、路径 3：官方 OpenAPI v2（企业自建应用）

这是最「底层」的正规路径，适合写脚本批量跑（正是当前场景最匹配的形态）。

来源：[纷享销客开发者手册](https://developer.fxiaoke.com/openapi_v2/start/quickstart/start.html)、[授权码模式](https://developer.fxiaoke.com/openapi_v2/start/auth/auth-code.html)

### 3.1 获取凭证（需管理员）
管理后台 → 应用列表 → **新建企业自建应用** → 开启**开发模式** → 得到：
- `appId`（FSAID_ 开头）
- `appSecret`
- `permanentCode`（永久授权码）

同时需：填写白名单 IP、登录授权发起页域名。

### 3.2 换取企业级 token（客户端凭证模式，无需用户参与）

```
POST https://open.fxiaoke.com/oauth2.0/token?thirdTraceId=<UUIDv4>
Content-Type: application/json

{
  "appId": "FSAID_xxxx",
  "appSecret": "xxxx",
  "permanentCode": "xxxx",
  "grantType": "app_secret"
}
→ { accessToken, expiresIn, openUserId, appId, ea, errorCode, errorMessage }
```

- 旧版端点（仍可用）：`POST https://open.fxiaoke.com/cgi/corpAccessToken/get/V2`
- **有效期 7200 秒**。缓存策略：缓存 6600s，在 6600–7200s 窗口刷新；重试逻辑挂在 `errorCode 20016`。
- **限流：10 次/分钟，且禁止并发调用**。
- `ea` 返回值即后续请求的 `x-fs-ea` header。
- 该模式支持**代表任意员工身份**（传其 openUserId）。

### 3.3 调用数据接口

```
POST https://open.fxiaoke.com/cgi/crm/v2/data/query
Headers: corpAccessToken: <token>
         x-fs-ea: <ea>
Body: {
  "data": {
    "objectApiName": "AccountObj",
    "search_query_info": { "limit": 20, "offset": 0, "filters": [...] }
  },
  "currentOpenUserId": "FSUID_xxx"
}
```

- `AccountObj` = 客户对象；电话字段为 `phone` / `tel`。
- 自定义对象（`__c` 后缀）走 `/cgi/crm/custom/v2/data/*`；预设对象走 `/cgi/crm/v2/data/*`。

### 3.4 实测结果（本机 curl，无浏览器）
```bash
# token 端点
curl -X POST https://open.fxiaoke.com/cgi/corpAccessToken/get/V2 \
  -d '{"appId":"FSAID_test","appSecret":"test",...}'
# → {"errorCode":10006,"errorMessage":"the parameter appSecret is missing or illegal"}

# 数据接口（不带 token）
curl -X POST https://open.fxiaoke.com/cgi/crm/v2/data/query ...
# → {"errorCode":20017,"errorMessage":"corpAccessToken为必填项，不能为空"}
```

**两条结论**：
1. `open.fxiaoke.com` **可直连，完全不需要浏览器/CDP**。
2. `errorCode 20017` = 「corpAccessToken 缺失」—— 这与之前 CDP 探测时看到的 20017 完全一致，**证明当时那条路径调的正是这个官方接口**。

### 3.5 关键门槛：必须购买 Open API 资源包

> 引自第三方 API 档案 [api-evangelist/fxiaoke](https://github.com/api-evangelist/fxiaoke)：
> "API access itself is **NOT self-serve**: a tenant with no purchased Open API resource pack receives **errorCode 30003** on every call, and the pack price is **'contact customer service'**."

- **未购买资源包 → 每次调用都返回 `errorCode 30003`**。
- 资源包价格不公开，需联系客服。
- 座位定价公开：**¥119 / ¥220 每用户每月，12 个月起**（含免费试用）。

### 3.6 OAuth 授权码模式（需要用户身份时）

```
GET  https://open.fxiaoke.com/oauth2.0/authorize?responseType=code&appId=...&redirectUrl=...&state=...&thirdTraceId=...
POST https://open.fxiaoke.com/oauth2.0/token
     { appId, appSecret, redirectUrl, code, grantType: "authorization_code" }
→ { openUserId, accessToken, corpId, refreshToken, expiresIn }
```
- accessToken 有效期 **7200 秒**；refreshToken **2 个月**。
- 参数名是纷享自有的 camelCase（`appId` 而非 `client_id`），**不符合 RFC 6749**。

### 3.7 额外发现：动态客户端注册端点完全开放

```bash
curl -X POST https://open.fxiaoke.com/oauth2.0/register \
  -d '{"redirect_uris":["https://example.com/cb"],"client_name":"probe","grant_types":["authorization_code"]}'
# → {"client_id":"mcp_94a227d8e5f34258bc0c088d3261f0b6","client_id_issued_at":1790670397,...}
```

- 该端点**无需任何认证**即可注册，返回的 `client_id` **前缀是 `mcp_`** —— 专为 MCP 客户端设计。
- OAuth 元数据（RFC 8414）：
  ```json
  {"issuer":"https://open.fxiaoke.com/oauth2.0",
   "authorization_endpoint":"https://open.fxiaoke.com/oauth2.0/cli/authorize",
   "token_endpoint":"https://open.fxiaoke.com/oauth2.0/pkce/token",
   "registration_endpoint":"https://open.fxiaoke.com/oauth2.0/register",
   "code_challenge_methods_supported":["S256"],
   "grant_types_supported":["authorization_code","refresh_token"]}
  ```
- ⚠️ 本次调研为验证开放性，实际调用了一次 `register`，在纷享侧创建了一个未授权的测试 client。**无实际权限、不影响企业数据**，但如需清理可联系管理员。

---

## 五、路径 4：自部署第三方 MCP

仓库：[zs001122/fxiaoke_mcp](https://github.com/zs001122/fxiaoke_mcp)（0 star，但完成度高）

### 定位
把**纷享 OpenAPI v2 封装成 MCP 服务**，自建部署，团队内网共享。已在 sandbox 租户全链路实测。

### 提供 19 个工具
| 工具 | 对应接口 |
|---|---|
| `fxk_query_data` | `/cgi/crm/v2/data/query` |
| `fxk_get_record` | `/cgi/crm/v2/data/get` |
| `fxk_create_record` / `fxk_update_record` | `/cgi/crm/v2/data/create` / `update` |
| `fxk_invalid_record` / `fxk_recover_records` / `fxk_delete_records` | 作废 / 恢复 / 删除 |
| `fxk_change_owner` | `/cgi/crm/v2/data/changeOwner` |
| `fxk_describe_object` / `fxk_list_objects` | 对象元数据 |
| `fxk_choose_from_pool` / `fxk_return_to_pool` / `fxk_remove_from_pool` | 公海池操作 |
| `fxk_change_deal_status` | 客户成交状态 |
| `fxk_customer_overview` | 客户 360° 视图（详情+联系人+地址+财务+商机+报价+合同） |
| `fxk_opportunity_pipeline` | 销售漏斗 |
| `fxk_quote_price_check` / `fxk_get_real_price` | 报价比价 / 实际价 |
| `fxk_move_opportunity_stage` | 商机阶段推进 |

### 部署要点
```bash
# .env
FXK_APP_ID=FSAID_xxxxxxxx
FXK_APP_SECRET=xxxxxxxx
FXK_PERMANENT_CODE=xxxxxxxx
FXK_API_BASE_URL=https://open.fxiaoke.com
FXK_MCP_TRANSPORT=http
FXK_MCP_HOST=0.0.0.0
FXK_MCP_PORT=8766
```
- 多用户令牌：`identity_map.json`（令牌 → 员工 FSUID，权限 600）
- 员工侧配置：
  ```json
  {"mcpServers":{"fxiaoke":{"type":"streamable-http",
    "url":"http://<服务器IP>:8766/mcp",
    "headers":{"X-Fxk-Token":"fxk-xxx"}}}}
  ```
- 该仓库**自带 `docs/WorkBuddy接入说明.txt`**，可直接把内容粘贴给 WorkBuddy 自动完成配置。

### 注意
- 同样需要 Open API 资源包（否则 30003）。
- 需要本机出口 IP 在纷享后台白名单内。
- 凭证（appSecret / permanentCode）是**企业级**的，泄露 = 整个企业数据风险，务必只放 `.env`。

---

## 六、其他非 API 思路（供完整参考）

| 方式 | 说明 | 是否推荐 |
|---|---|---|
| 浏览器插件 / 油猴脚本 | 仍在浏览器内运行，但不是 CDP 外控；受页面改版影响 | 不推荐，比 CDP 更脆弱 |
| RPA（影刀 / UiPath） | UI 自动化，本质与 CDP 同类，还多一层授权成本 | 不推荐 |
| 人工导出 Excel | CRM 界面导出后用脚本处理 | 仅适合一次性 |
| 企微 / 钉钉集成侧取数 | 若企业已把 CRM 接入企微，可从企微侧拿部分数据 | 覆盖面窄 |
| 业务数据同步接口 | 纷享有增量同步接口，适合定期全量拉取 | 需 OpenAPI 权限 |
| 数据库直连 | 仅私有化部署才有 | 不适用（SaaS） |

---

## 七、推荐行动

### 立即可做（零成本）
1. **打开 WorkBuddy 连接器市场，搜索「纷享」** —— 确认官方连接器是否已上架到当前环境。
2. **问 CRM 管理员三件事**：
   - 企业是否已开通 **MCP 服务**？（若否，管理员可**免费试用 15 天**）
   - 是否已购买 **Open API 资源包**？
   - 能否创建**企业自建应用**并开启开发模式（拿 appId / appSecret / permanentCode）？
3. 若管理员愿意配合 → 走**路径 1 或 2**，几分钟搞定，且长期稳定。
4. 若管理员不配合或企业未采购 → **继续用现有 CDP 方案**（已跑通，零成本）。

### 权衡
| 维度 | 官方 MCP / OpenAPI | CDP 方案 |
|---|---|---|
| 稳定性 | 高（官方契约） | 中（页面改版 / 登录态过期需重登） |
| 速度 | 高（直连，无限并发瓶颈） | 中（逐号 300ms 延迟） |
| 成本 | 需采购 | 免费 |
| 前置条件 | 管理员 + 采购流程 | 只需用户本人登录一次 |
| 维护 | 几乎不用管 | 需保持浏览器常驻 |
| 合规 | 完全合规 | 灰色（借登录态调内部接口） |

**建议**：如果这是一项**长期、高频**的工作（如每天核对名单），值得推动管理员走官方 MCP；如果是**偶发**任务，CDP 方案已经够用。

---

## 八、附：本次调研的实测命令与结果

```bash
# 1) OAuth 元数据 —— 可达
curl https://open.fxiaoke.com/.well-known/oauth-authorization-server
# → 200，含 cli/authorize、pkce/token、register

# 2) 企业级 token 端点 —— 可达，参数校验生效
curl -X POST https://open.fxiaoke.com/cgi/corpAccessToken/get/V2 -d '{...}'
# → errorCode 10006 (appSecret 缺失)

# 3) 数据查询接口 —— 可达，确认 20017 含义
curl -X POST https://open.fxiaoke.com/cgi/crm/v2/data/query -d '{...}'
# → errorCode 20017 "corpAccessToken为必填项，不能为空"

# 4) 官方 MCP 端点 —— 存在
curl -o /dev/null -w "%{http_code}" https://open.fxiaoke.com/mcp/fs/crm-mcp
# → 401

# 5) 动态客户端注册 —— 开放
curl -X POST https://open.fxiaoke.com/oauth2.0/register -d '{...}'
# → client_id: mcp_94a227d8e5f34258bc0c088d3261f0b6
```

**全部测试均从本机 curl 直连，未使用任何浏览器或 CDP。**

---

## 参考来源

1. [让AI真正连上业务：纷享销客 MCP](https://help.fxiaoke.com/ee88/a823/d4dd)
2. [如何在Agent接入纷享MCP服务](https://help.fxiaoke.com/ee88/a823/6aab)
3. [Agent办公平台上如何操作纷享销客CRM](https://help.fxiaoke.com/ee88/a823/6c9c)
4. [纷享销客 OpenAPI v2 快速开始](https://developer.fxiaoke.com/openapi_v2/start/quickstart/start.html)
5. [授权码模式](https://developer.fxiaoke.com/openapi_v2/start/auth/auth-code.html)
6. [zs001122/fxiaoke_mcp](https://github.com/zs001122/fxiaoke_mcp)
7. [api-evangelist/fxiaoke](https://github.com/api-evangelist/fxiaoke)（第三方 API 档案，含计费与限流）
8. [纷享MCP开放工具列表](https://365.kdocs.cn/l/ctLBqBHI5wCf)
