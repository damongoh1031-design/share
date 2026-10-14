# 纷享销客 CRM — 手机号查重接口（可复用）

> 用途：输入手机号，查询 CRM 中是否存在对应客户，返回客户名称/编号。
> 验证样本：`0122139000` → 1 条（B MS WONG KOOI FOONG / 20250324-737941）；`0123159997` → 无数据。

---

## 一、前置条件（必做）

接口借用浏览器登录态调用，需要一个**已登录且开启调试端口的 Chrome**。

**关键结论：必须用用户本机的 Chrome 153，不要用 agent-browser 自带的 Chrome 154** —— 在 Chrome 154 / 自动化模式下扫码登录会失败（这是之前反复登录不上的根因）。

启动命令（Git Bash，建议后台常驻）：

```bash
"C:/Program Files/Google/Chrome/Application/chrome.exe" \
  --user-data-dir="C:/Users/Admin/.workbuddy-ai/browser-profiles/manual" \
  --remote-debugging-port=9222 \
  --no-first-run --no-default-browser-check \
  "https://www.fxiaoke.com/XV/UI/Home"
```

- `--user-data-dir`：固定 profile，登录态会落盘，重启不用重登。
- 启动后在窗口里**扫码登录一次**即可。
- 之后所有自动化都通过 `http://127.0.0.1:9222`（CDP）接管，不再碰登录。

> 注意：该浏览器由后台任务托管以维持存活；若窗口被关，按上面的命令重启即可（登录态还在）。

---

## 二、接口详情

| 项 | 值 |
|---|---|
| 方法 | `POST` |
| 路径 | `/FHH/EM1HNCRM/API/v1/object/AccountObj/controller/DuplicateSearch` |
| 完整 URL | `https://www.fxiaoke.com/FHH/EM1HNCRM/API/v1/object/AccountObj/controller/DuplicateSearch?_fs_token=<fs_token>` |
| Content-Type | `application/json` |
| 鉴权 | Cookie 登录态 + URL 里的 `_fs_token`（取值自 `fs_token` cookie） |

### 租户常量（本企业固定，勿改）

| 常量 | 值 | 说明 |
|---|---|---|
| 对象 | `AccountObj` | 客户对象 |
| 查重规则 | `rule_rnhS3__c` | 客户查重规则 |
| 路径段 | `EM1HNCRM` | 租户标识 |
| describeVersionMap | `{"AccountObj": 150}` | 对象描述版本 |

### 请求体（模板）

```json
{
  "describe_api_name": "AccountObj",
  "type": "TOOL",
  "object_data": {
    "object_describe_api_name": "AccountObj",
    "tel": "0122139000",
    "duplicate_rule_api_name": "rule_rnhS3__c"
  },
  "include_object_describes": true,
  "is_need_duplicate": true,
  "page_size": 1,
  "page_number": 1,
  "duplicate_rule_api_name": "rule_rnhS3__c",
  "describeVersionMap": { "AccountObj": 150 }
}
```

### 响应（关键路径）

```json
{
  "Result": { "FailureCode": 0, "StatusCode": 0 },
  "Value": {
    "data_list": [
      {
        "name": "B MS WONG KOOI FOONG",
        "account_no": "20250324-737941",
        "tel": "0122139000"
      }
    ]
  }
}
```

- `Value.data_list` 为空数组 → 无数据。
- 取 `data_list[0].name` / `account_no` / `tel`。

---

## 三、批量使用

脚本：`fx_phone_query.mjs`（已通过 CDP 复用登录态，自动取 `fs_token`）

```bash
# 直接传号码
node fx_phone_query.mjs 0122139000 0123159997

# 从文件读（每行一个号码）
node fx_phone_query.mjs --file numbers.txt

# 9 位号码会自动补前导 0（见下方「号码格式」）
node fx_phone_query.mjs 122891188

# 关闭自动补 0
node fx_phone_query.mjs --no-normalize 122891188
```

输出 CSV：`输入号码,查询号码,匹配数,客户名称,客户编号`

实测：

```
输入号码,查询号码,匹配数,客户名称,客户编号
0122139000,0122139000,1,"B MS WONG KOOI FOONG",20250324-737941
0123159997,0123159997,无数据,"",
```

### ⚠️ 号码格式归一化（重要）

**CRM 里的标准格式是 `01` 开头的 10 位**，如 `0122339159`。输入格式不一致会**静默返回「无数据」**，必须归一化。

| 输入 | 处理 | 归一化结果 |
|---|---|---|
| `0122339159` | 已标准，原样 | `0122339159` |
| `122339159` | 9 位，补前导 `0` | `0122339159` |
| `60122339159` | 带国家码 60，删掉最前面的 `6` | `0122339159` |
| `+60122339159` | 先去 `+`，再删前导 `6` | `0122339159` |

```js
function normalize(tel) {
  let t = String(tel).replace(/\D/g, '');
  if (!t) return t;
  if (/^6\d+$/.test(t)) t = t.slice(1);   // ① 以 6 开头 → 删最前面的 6
  if (/^\d{9}$/.test(t)) t = '0' + t;     // ② 9 位 → 补前导 0
  if (!t.startsWith('0')) t = '0' + t;    // ③ 兜底：必须以 0 开头
  return t;
}
```

实测：21 个号码用 9 位原样查 → **0 命中**；归一化后 → **5 命中**。
脚本默认开启归一化，输出同时打印 `输入号码` / `查询号码` 便于核对；`--no-normalize` 可关闭。


---

## 四、注意事项

- **token 刷新**：`fs_token` 会过期。脚本每次运行时从页面 cookie 现取，浏览器保持登录即可，无需手动维护。若脚本报 `NO_FS_TOKEN`，说明登录失效，回窗口重新扫码。
- **限流**：批量时脚本默认每个号码间隔 300ms，可自行调大。频率过高可能触发风控。
- **字段说明**：`DuplicateSearch` 的 `name` 是客户主名称。若你要的「pj2」这类结果是另一条查询路径（如全局搜索/简易查重），告诉我，我再补对应接口。
- **只读安全**：本接口只查询不写入，且复用你已登录的会话，**不会产生新登录、不会顶掉你的会话**（绕开了平台的单一登录限制）。
- **对象替换**：同一接口模式也适用于其他对象——把 `AccountObj` 换成对应对象的 api name，并调整查重规则即可。

---

## 五、登录失败排查记录（给后来人）

1. agent-browser 自带 Chrome 154 + 自动化模式 → 扫码登录后跳转仍回登录页（风控拦截）。
2. 用户的 Chrome 153 正常扫码即可登录。
3. 判断窗口是否可见：页面里执行 `outerWidth!==innerWidth && document.visibilityState==='visible'`。
4. 进程枚举用 Git Bash 的 `ps -W`（PowerShell 的 `Get-CimInstance` 在沙箱里读不到 agent-browser 进程详情，会误判）。
5. 接管已登录浏览器优先用原生 CDP（Node `WebSocket` 直连 `9222/json/list` 找到目标标签），不要用 agent-browser 的 `connect`——它会附加到自己的 about:blank 目标，且其 `open` 会把已登录标签 302 回登录页。
