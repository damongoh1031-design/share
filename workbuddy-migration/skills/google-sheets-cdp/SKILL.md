---
name: google-sheets-cdp
description: 通过 CDP 接管用户本机已登录的 Chrome，读写 Google Drive / Google Sheets（表格、文档）。当用户给出 docs.google.com/spreadsheets 链接、要求「连接 Google Drive/Sheets」「读取/修改某个 Google 表格」，或 WorkBuddy 缺少 Google 官方连接器而需要绕过登录时使用。也适用于任何「接管已登录浏览器操作 Google 系产品」的场景。
agent_created: true
---

# Google Sheets / Drive 读写（CDP 复用登录态）

> ⚡ **先试 gog CLI，别一上来就开 Chrome。** 本机 gog 已授权（`jsng0819@gmail.com`），
> 读写 Google Sheets 全流程可纯命令行完成，无需 CDP / 无需 Chrome 常开。
> 只有 gog 覆盖不到的场景（需要浏览器 UI、Docs API 未启用的接口）才回落到 CDP 方案。
> gog 实战速查见文末「gog CLI 速查」。

## 何时用

WorkBuddy **没有 Google 官方连接器**。接入 Google 系有 4 类路径，**先选路径再动手**：

| 路径 | 适用 | 成本 | 数据路径 |
|---|---|---|---|
| **CDP 接管本机 Chrome**（本 skill） | 零配置、临时/一次性任务、不想装东西 | 无，但需 Chrome 常开 | 本机 → Google |
| **gog CLI** ✅ **已配置完成** | 长期反复读写，数据不经第三方 | 已完成，直接调用 | 本机 → Google 官方 |
| **Maton api-gateway**（市场 skill `api-gateway`，skillId `skill_2053081339211579392`） | 最快上手，不碰 GCP | 注册 Maton；免费档 30 连接 / 无限请求 | 本机 → **Maton** → Google |
| **Service Account / Google 官方 MCP** | 无人值守定时任务 | GCP 配置较重 | 本机 → Google 官方 |

**默认走本 skill 的 CDP 方案**（零依赖，立刻可用）。若用户明确要「长期稳定接入」或「不想每次开浏览器」，**直接用 gog CLI —— 本机已装好并授权，详见 skill `gog-google-workspace`**：

```bash
GOG="C:/Users/Admin/.workbuddy-ai/bin/gog/gog.exe"
"$GOG" sheets get <spreadsheetId> "'表名'!A1:E10"
```

要点速查：
- **gog**：`gog auth credentials set client_secret.json` → `gog auth add you@gmail.com --services sheets,drive` → `gog sheets ...`。MCP 模式：`gog mcp --allow-tool sheets_read_range`（写工具需额外 `--allow-write`）。
- **Maton**：`npm i -g @maton/cli` → `maton login --oauth` → `maton google-sheets values get <id> --range 'Sheet1!A1:D10'`。远程 MCP 端点 `https://mcp.maton.ai`。
- **Google 官方 MCP**：端点 `https://sheetsmcp.googleapis.com/mcp/v1`，Streamable HTTP + OAuth 2.0，工具 `get_values` / `get_spreadsheet` / `update_spreadsheet` / `update_values` / `update_formulas` / `insert_dimension`。需加入 Google Workspace 开发者预览版计划。

不要试图：
- ❌ 用 agent-browser / Playwright 自带的 Chromium 登录 Google —— 风控几乎必然拦截。
- ❌ 用 `export?format=csv` 匿名抓取 —— 私有表格返回 `HTTP 401`。

## 核心前提

Chrome 必须以 `--remote-debugging-port=9222` 启动。检查：

```bash
curl -s --max-time 3 http://127.0.0.1:9222/json/version
```

已有实例就直接复用；没有则启动（**必须 `run_in_background: true`**，GUI 进程随命令结束会被回收）：

```bash
"C:/Program Files/Google/Chrome/Application/chrome.exe" \
  --user-data-dir="<固定 profile 目录>" \
  --remote-debugging-port=9222 \
  --no-first-run --no-default-browser-check \
  "https://docs.google.com/spreadsheets/d/<ID>/edit"
```

用**用户本机 Chrome + 用户自己的 profile**，登录态可长期复用。

## 登录 Google（关键坑集中区）

### 坑 1：窗口不在前台 → 所有 JS 交互静默失效

`element.click()`、`element.focus()` 在窗口失焦时**完全不生效**，且不报错。
症状：`document.activeElement` 不是目标元素、按钮点了没反应、URL 不变。

**必须先激活**：

```js
await send('Page.enable');
await send('Page.bringToFront');
await send('Emulation.setFocusEmulationEnabled', { enabled: true });
```

之后 `document.hasFocus()` 应为 `true`。

### 坑 2：`offsetParent === null` ≠ 不可见

Google 登录页用 `position: fixed` 布局，可见元素的 `offsetParent` 也是 `null`。
判断可见性用 `getBoundingClientRect()`：

```js
const r = el.getBoundingClientRect();
const inView = r.width > 0 && r.height > 0;
```

### 坑 3：页面上有隐藏的模板 input

Google 登录页同时存在**可见的真实输入框**和**隐藏的同名模板元素**。
`document.querySelector('input[name=Passwd]')` 可能命中隐藏副本，填了值但界面无变化。

**正确做法：用坐标真实点击 + CDP 原生输入事件**，不要依赖选择器：

```js
// 1. 取目标元素中心坐标
const { x, y } = await evalJs(`(() => {
  const el = document.querySelector('input[name=Passwd]');
  const r = el.getBoundingClientRect();
  return JSON.stringify({ x: r.x + r.width/2, y: r.y + r.height/2 });
})()`);

// 2. 真实鼠标点击
await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y });
await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });

// 3. 真实键盘输入（modifiers: 2 = Ctrl）
await send('Input.insertText', { text: '要输入的内容' });
// 或逐字符：
for (const ch of text) {
  await send('Input.dispatchKeyEvent', { type: 'keyDown', text: ch, unmodifiedText: ch, key: ch });
  await send('Input.dispatchKeyEvent', { type: 'keyUp', key: ch });
}

// 4. Enter 提交（Google 登录表单支持）
await send('Input.dispatchKeyEvent', { type: 'rawKeyDown', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13 });
await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13 });
```

### 登录页元素速查

| 步骤 | 选择器 | 备注 |
|---|---|---|
| 邮箱输入 | `#identifierId` | |
| 邮箱下一步 | `#identifierNext button` | 容器是 div，按钮在内层 |
| 密码输入 | `input[name=Passwd]` | 有隐藏同名副本，必须按坐标点 |
| 密码下一步 | `#passwordNext button` | 同上 |
| 提交成功标志 | 标签页 URL 变成 `drive.google.com` 或目标文档 | |

**不要用明文密码**：通过环境变量传给脚本，表达式里用占位符替换，避免落盘。
密码字段填完后用 `el.value.length` 校验长度，不要打印值。

## 读取表格

### 列出所有工作表名

```js
[...document.querySelectorAll('[id^="sheet-button-"]')].map(el => (el.innerText || '').trim())
```

### 导出某个工作表为 CSV

**用工作表名，不要用 gid** —— gid 在 DOM 里拿不到（`sheet-button-` 的 id 不含 gid），但 `gviz` 支持 `sheet=` 参数：

```js
const csv = await fetch(
  `https://docs.google.com/spreadsheets/d/${ID}/gviz/tq?tqx=out:csv&sheet=${encodeURIComponent(name)}`,
  { credentials: 'include' }        // 关键：复用页面 cookie
).then(r => r.text());
```

在**页面上下文里 fetch** 会自动携带登录 cookie，这是整个方案的关键。

其他 gviz 格式：`tqx=out:json`（带类型信息）、`tqx=out:html`。
单表也可用 `gid=`：`.../gviz/tq?tqx=out:csv&gid=<gid>`（gid 从表格 URL 的 `#gid=` 拿）。

### 全量导出脚本

见本 skill 同目录 `scripts/dump_all.mjs`（改 `ID` 和 `OUT_DIR` 即可）。

## 写入表格

gviz 是只读的。写入按复杂度选：

| 方案 | 适用 | 说明 |
|---|---|---|
| CDP 点击单元格 + 键盘输入 | 少量、精确修改 | 最直接。点单元格 → `Input.insertText` → Enter |
| 逆向 `batchexecute` 内部接口 | 批量 | Sheets 前端编辑走 `POST /spreadsheets/d/<ID>/batchexecute`，body 是嵌套数组。用 XHR 钩子抓一次真实编辑请求即可拿到模板 |
| 服务账号 + Sheets API v4 | 长期、大量 | 需要用户在 Google Cloud Console 建服务账号，并把表格共享给服务账号邮箱。**最稳，但需要用户配置** |

抓内部接口的钩子：

```js
const oO = XMLHttpRequest.prototype.open, oS = XMLHttpRequest.prototype.send;
XMLHttpRequest.prototype.open = function (m, u) { this.__u = u; this.__m = m; return oO.apply(this, arguments); };
XMLHttpRequest.prototype.send = function (b) {
  this.addEventListener('load', function () {
    if (String(this.__u).includes('batchexecute')) window.__qlog.push({ u: String(this.__u), b: String(b || ''), s: this.status, r: String(this.responseText || '').slice(0, 1500) });
  });
  return oS.apply(this, arguments);
};
window.__qlog = window.__qlog || [];
```

然后手工在 UI 里改一个单元格，读 `window.__qlog` 拿到 body 模板，之后重放。

## 通用 CDP 执行器

`scripts/cdp.mjs` 支持：

```bash
node cdp.mjs <urlSubstring> <exprFile> [--nav <url>] [--front] [--shot <png>]
```

- `urlSubstring`：匹配标签页 URL 的子串
- `exprFile`：要执行的 JS 表达式文件（写文件避免 shell 转义地狱），传 `-` 表示只做导航/截图
- `--front`：激活标签页 + 启用焦点模拟
- `--shot`：截图存 PNG（用 Read 工具查看，是判断页面真实状态最快的方式）
- 环境变量 `CDP_TIMEOUT`：evaluate 超时毫秒数（默认 25000）
- 占位符：表达式里的 `__GPWD__` / `__GMAIL__` 会被 `$GPWD` / `$GMAIL` 替换（避免明文落盘）

## 排错速查

| 症状 | 原因 | 处理 |
|---|---|---|
| `no google tab` / 找不到标签页 | 页面已跳转 | 重新 `curl 127.0.0.1:9222/json/list` 看真实 URL |
| evaluate 无输出、进程被 SIGTERM | 页面导航导致 execution context 销毁，promise 永不 resolve | 加 `CDP_TIMEOUT`；导航后重新探测 |
| 点击/输入无反应 | 窗口失焦 | `--front` |
| 填了值但界面没变 | 命中了隐藏模板元素 | 改用坐标真实点击 |
| 401 / 登录页 | 该 profile 未登录 Google | 走上面登录流程 |

## 脚本清单（scripts/）

| 脚本 | 用途 | 用法 |
|---|---|---|
| `google_login.mjs` | 完整登录流程（自动判断是否已登录） | `GMAIL=x GPWD=y node google_login.mjs [目标URL]` |
| `cdp.mjs` | 通用 CDP 执行器 | `node cdp.mjs <urlSubstring> <exprFile> [--nav u] [--front] [--shot p]` |
| `probe.js` | 诊断：列出所有可见输入框/按钮及坐标 | `node cdp.mjs "google.com" probe.js` |
| `read_sheet.mjs` | 读单个工作表为 CSV | `SHEET_ID=x SHEET_NAME=y node read_sheet.mjs` |
| `dump_all.mjs` | 导出全部工作表到本地目录 | `OUT_DIR=./data node dump_all.mjs` |

运行环境：Node 22+（内置 `WebSocket`，无需任何依赖）。

## 标准作业顺序

```bash
# 0. 确认 Chrome 调试端口在
curl -s --max-time 3 http://127.0.0.1:9222/json/version

# 1. 登录（已登录会自动跳过）
GMAIL='you@gmail.com' GPWD='***' node scripts/google_login.mjs \
  "https://docs.google.com/spreadsheets/d/<ID>/edit"

# 2. 导航到目标表并截图确认
node scripts/cdp.mjs "docs.google.com/spreadsheets" - \
  --nav "https://docs.google.com/spreadsheets/d/<ID>/edit" --front \
  --shot ./shot.png

# 3. 全量导出
OUT_DIR=./data node scripts/dump_all.mjs
```

## 实战验证

2026-09-29 首次跑通，记录关键参数供参考：

- Chrome `153.0.8010.53`，本机真实实例（非 `--enable-automation`），`navigator.webdriver === false`
- 登录页为**两步式**（`/signin/identifier` → `/signin/challenge/pwd`），邮箱与密码分页
- 登录成功后 Chrome 会额外弹出 `chrome://signin-dice-web-intercept` 标签页，**可忽略**
- 目标表：`DAMON LIST`，4 个工作表，最大 1267 行，全量导出耗时 < 10s
- **易错点**：`Page.bringToFront` 之前做的一切点击/输入都无效且不报错。本次卡了 4 轮才发现窗口失焦，务必第一步就激活。

---

## gog CLI 速查（本机已授权，优先路径）

```bash
GOG="C:/Users/Admin/.workbuddy-ai/bin/gog/gog.exe"
"$GOG" auth status          # 确认 account 与 credentials_exists=true
```

gog 只暴露 4 个 sheets 子命令：`get` / `update` / `batch-update` / `batch-request`。
**没有 `spreadsheets.get`**，所以拿不到「工作表名 ↔ gid」映射，需要下面的探测技巧。

### 读

```bash
# 不带表名 = 第一个工作表
"$GOG" sheets get <ID> "A1:H8" -j --results-only
# 带表名（含空格/斜杠必须单引号包裹）
"$GOG" sheets get <ID> "'SHOPEE LIST 01'!A1:F4" -j --results-only
# 渲染选项：FORMATTED_VALUE（默认）/ UNFORMATTED_VALUE / FORMULA
"$GOG" sheets get <ID> "'X'!B1:B3" -j --render UNFORMATTED_VALUE
```

### 拿到全部工作表名（不需要 gid）

```bash
"$GOG" drive download <ID> --format xlsx --out /tmp/book.xlsx --overwrite
python -c "import openpyxl;print([w.title for w in openpyxl.load_workbook('book.xlsx',read_only=True).worksheets])"
```

⚠️ **xlsx 导出会按 Excel 命名规则净化工作表名**：Google 里叫 `04/09` 的标签，导出后变成 `0409`；
`1509`/`2509`/`0110` 同理。**API range 必须用 Google 里的原名** `'04/09'!A1`，
用净化后的 `'0409'!A1` 会报 `Unable to parse range`（Google 对「表名不存在」就是这条报错，别误判成语法问题）。
判断依据：导出名里若有一串纯数字，先猜 `/` 分隔的日期。

### gid → 工作表名（gog 没有 spreadsheets.get，用探测法）

**有效：`duplicateSheet` 探测 + 立刻 `deleteSheet`**。reply 里 `properties.title` 就是 `原名 +（副本）`。

```bash
# 1) 探测（会短暂创建一个副本工作表）
"$GOG" sheets batch-request <ID> --force -j \
  --requests-json '[{"duplicateSheet":{"sourceSheetId":1424829532}}]'
#    → replies[0].duplicateSheet.properties.title = "SHOPEE LIST 01（副本）"
#    → 同时记下新 sheetId
# 2) 删掉副本
"$GOG" sheets batch-request <ID> --force -j \
  --requests-json '[{"deleteSheet":{"sheetId":2064218054}}]'
```

`--requests-json` 必须传**裸数组** `[{...}]`，传 `{"requests":[...]}` 会报
`cannot unmarshal object into Go value of type []jsontext.Value`。

**无效：`updateSheetProperties` 探测** —— reply 恒为 `{}`，不回显 title，别浪费时间。

其他坑：
- `gog docs list-tabs` 需要 Docs API，本 OAuth 项目未启用 → 直接报错，不可用。
- `drive download --tab=<gid>` 只支持 pdf|docx|txt|md|html，**不支持 csv/xlsx**。
- `drive download --format csv` 只导出第一个工作表，且导出名同样被净化。
- `drive raw <ID>` 是 Files.Get，**不含工作表信息**。

### 写（批量）

```bash
# 生成 2D 数组 JSON（@file 或 @- 从 stdin）
python -c "
import json
vals=[[f'{n:010d}'] for n in range(127680001,127690001)]
json.dump(vals,open(r'C:/Users/Admin/AppData/Local/Temp/vals.json','w'))"

"$GOG" sheets update <ID> "'SHOPEE LIST 01'!B1:B10000" \
  --values-json @C:/Users/Admin/AppData/Local/Temp/vals.json --input RAW -j
# → {"updatedCells":10000,...}
```

- `--input RAW`（默认 USER_ENTERED）：RAW 不解析、按字符串存，**前导零不丢**。
- 想彻底保险（防止后续有人用 USER_ENTERED 覆写），先整列设文本格式：

```bash
"$GOG" sheets batch-request <ID> --force -j --requests-json \
'[{"repeatCell":{"range":{"sheetId":1424829532,"startRowIndex":0,"endRowIndex":10000,
"startColumnIndex":1,"endColumnIndex":2},"cell":{"userEnteredFormat":{"numberFormat":{"type":"TEXT"}}},
"fields":"userEnteredFormat.numberFormat"}}]'
```

- 结构类操作（增删表、格式、冻结行…）统一走 `batch-request`；`repeatCell`/`duplicateSheet`/`deleteSheet`
  的 range 用 **sheetId（gid）+ 0-based 行列索引**，不是 A1 记法。

### 验证

```bash
"$GOG" sheets get <ID> "'SHOPEE LIST 01'!B9998:B10000" -j --results-only --render FORMATTED_VALUE
```

### 实战记录 2026-10-02

- 表 `1WdlrWe2vY8cVCzyowfZJUF1F6H4oEhwz9iLIVH4lAPU`，URL gid `1424829532`
  → 探测得 `SHOPEE LIST 01`（空表，1000 行 × 26 列）。
- 其他标签实际名：`工作表1`、`SHOPEE LIST 01`、`04/09`、`15/09`、`25/09`、`01/10`
  （xlsx 导出显示为 `0409`/`1509`/`2509`/`0110`，踩坑点）。
- 写入 10000 个电话号码 `0127680001`–`0127690000` 到 `B1:B10000`，前导零保留。
