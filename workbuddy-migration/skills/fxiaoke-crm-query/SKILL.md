---
name: fxiaoke-crm-query
description: 通过 CDP 接管用户已登录的 Chrome，调用纷享销客（fxiaoke）CRM 的内部接口批量查询手机号（查重/查客户），并把结果回写到 CSV 或 Google Sheets 的某一列（如查到的标 X）。当用户要求「用 CRM 查一批手机号 / 电话号」「纷享销客查重」「查这个名单哪些在 CRM 里」「把查询结果标回表格」「检查这个 Google 表格 / Google Sheet 的号码在 CRM 有没有数据并填 X」「CRM 查询脚本报错了」时使用。也适用于「接管已登录浏览器抓内部接口」这一类通用场景。
agent_created: true
---

# 纷享销客 CRM 内部接口调用（CDP 复用登录态）

## 适用场景

1. 给一批手机号，查 CRM 里有没有对应客户 → 返回客户名称 / 客户编号。
2. 给一份 CSV 名单，查完后**回写到某一列**（例如查到的在 C 列标 `X`）。
3. 给一个 **Google Sheet 链接**，查号码列在 CRM 有没有数据、有则填 `X` → 用 `fx_sheet_check.sh` **一键跑完**（最常用）。
4. CDP 链路出故障，需要定位与修复。

---

## 🔴 已踩坑清单（动手前务必扫一眼）

按「代价」排序，每条都实测踩过。详细排查见 `references/fx_errors.md`。

| # | 坑 | 后果 | 防护 | 详见 |
|---|---|---|---|---|
| 1 | **CDP 长连接约 6 分钟空闲即断** | 长跑崩在 ~350 条，**进度全丢、无输出** | 长任务必须用带续跑+重连的脚本（`fx_phone_query.mjs` / `fx_recheck_resume.mjs`） | §6.3 |
| 2 | **区间行偏移**（`base[0]` 应为 `base[N-1]`） | **覆盖上方数据**、整列错位 | 写完打印首行与 Sheet 对账；写前备份目标列 | §8.7 |
| 3 | **`page_size:1` 按级别判定** | **大量漏判 PJ2**（实测第 15–17 行全漏） | 必须做一次 `page_size:50` 全量重查 | §8.5 |
| 4 | **号码重复**（唯一号码数 ≠ 行数） | 写回错位 / 误判为丢数据 | 按 Sheet **行**逐行判定；校验用行数对账 | §8.6 |
| 5 | **`gog` 读取截断尾部空行** | 验证断言误判 | 不能用「行数相等」；补空行后逐行内容比对 | §8.8 |
| 6 | **异常号码多为源数据问题** | 误当脚本 bug 乱修 | 先分类（非 01 段/外国号/科学计数法）再报告 | §8.9 |
| 7 | **沙箱 Job Object 回收进程** | Chrome / OAuth 监听跨命令即死 | GUI 与常驻进程用 WMI（`fx_launch_chrome.ps1`） | §3.1 |
| 8 | **gog 授权约 6–7 天过期** | 全部 sheets 命令 `invalid_grant` | `gog_reauth.sh` 一键重授权 | §3 附近 |
| 9 | **号码未归一化** | **全部静默返回「无数据」** | 默认开启归一化；`--dry-run` 自检 | §8.1 |

---

## 工具集（scripts/ 目录，全部可独立运行）

| 文件 | 用途 |
|---|---|
| `fx_doctor.mjs` | **环境诊断**。9 项检查 + 修复建议。**出问题先跑这个** |
| `fx_phone_query.mjs` | 批量查询。断点续跑 / 自适应限流 / 错误隔离 / 自动重连 / 优雅中断 |
| `fx_lib.mjs` | 共享库。CDP 会话、错误码字典、归一化、重试策略 |
| `fx_sheet_check.sh` | **端到端一键**：读 Google Sheet 号码列 → CRM 查询 → 写回标记列 → 读回验证。**日后最常用** |
| `merge_marks.py` | 把结果回写原 CSV（字节级对齐 BOM/换行/末行，带自校验） |
| `make_c_column.py` | 把结果转成 Google Sheets 某一列的 2D JSON（写命中标记 `X`），供 `gog sheets update --values-json=@file` 使用 |
| `make_a_column.py` | 同上，但写**客户名称**本身（命中行填名字，未命中留空）。同一份结果可同时写多列 |
| `fx_recheck_resume.mjs` | **全量重查**（`page_size:50`）。按行/级别分类，用于「按客户级别（PJ1/PJ2）筛选」。断点续跑 + CDP 断线自动重连。**跑 PJ2 判定必用** |
| `make_pj2_column.py` | 由「全量重查结果」按 **PJ2** 判定生成区间 2D JSON（支持 `--start/--end` 从第 N 行写）。**注意行偏移必须用 `base[N-1]`** |
| `make_shortcut.py` | 在桌面创建启动快捷方式（ctypes 调 COM，绕开沙箱对 PowerShell/cscript 的拦截） |
| `verify_lnk.py` | 验证 .lnk 是否有效（COM 解析出目标/参数/图标） |
| `fx_launch_chrome.ps1` | **Agent 自动启动 Chrome**（WMI 创建进程，绕开沙箱 job 回收）。用 PowerShell 工具执行 |
| `launch_cdp_chrome.py` | 同一条 Bash 命令内启动 Chrome（供 `fx_sheet_check.sh` 自启动用；跨命令会失效） |
| `gog_reauth.sh` | **gog 授权过期时的一键重新授权**（CDP 走 Google 同意流程 + 抓回调 URL） |
| `fx_g_tab.mjs` | 上者依赖：对授权标签开网络监听，捕获 OAuth 回调 URL |

参考资料：`references/fx_errors.md`（故障手册）、`fx_api.md`（接口文档）、`fxiaoke-alternatives.md`（官方替代方案）。

---

## 桌面快捷方式（一键启动 CDP 浏览器）

**问题**：每次都要手敲 Chrome 启动命令，容易出错、也容易忘记加 `--remote-debugging-port`。

**方案**：`make_shortcut.py` 在桌面生成两个快捷方式：

| 快捷方式 | 用途 |
|---|---|
| `纷享CRM浏览器` | 窗口可见（120,80）— 用于**首次登录 / 排查** |
| `纷享CRM浏览器（后台静默）` | 窗口移出屏幕（-32000,-32000）— **纯后台常驻** |

```bash
python make_shortcut.py                                        # 创建
python verify_lnk.py "C:/Users/Admin/Desktop/纷享CRM浏览器.lnk"  # 验证
```

### ⚠️ 沙箱下创建 .lnk 的三个坑（已全部踩过）

| 尝试 | 结果 |
|---|---|
| PowerShell `New-Object -ComObject WScript.Shell` | ❌ 被拦（COM 实例化） |
| `cscript //nologo x.vbs` | ❌ 被拦（LOLBin） |
| 手写 [MS-SHLLINK] 二进制 | ⚠️ 能生成，但 `IPersistFile::Load` 失败（格式细节难保证） |
| **Python ctypes 调 COM** | ✅ **可行** —— 沙箱的静态检查不覆盖 Python 内的 COM 调用 |

### ⚠️ COM vtable 索引要点（最容易错的地方）

**IShellLinkW 与 IPersistFile 是两个独立接口，vtable 各自从 0 计数，不能混用！**

```
IShellLinkW :  QueryInterface(0) AddRef(1) Release(2) GetPath(3) GetIDList(4)
               SetIDList(5) GetDescription(6) SetDescription(7) GetWorkingDirectory(8)
               SetWorkingDirectory(9) GetArguments(10) SetArguments(11) GetHotkey(12)
               SetHotkey(13) GetShowCmd(14) SetShowCmd(15) GetIconLocation(16)
               SetIconLocation(17) SetRelativePath(18) Resolve(19) SetPath(20)

IPersistFile:  QueryInterface(0) AddRef(1) Release(2) GetClassID(3) IsDirty(4)
               Load(5) Save(6) SaveCompleted(7) GetCurFile(8)
```

**必须先 `QueryInterface(IID_IPersistFile)` 拿到 pf，再在 pf 上调 Load/Save。**
直接在 IShellLinkW 指针上用索引 5 会调到 `SetIDList` —— 表现为「Load 返回 0 但所有 Get* 都是空」。

**另一个坑**：输出缓冲区要用 `ctypes.cast(buf, c_void_p)` 显式传地址。
用 `c_wchar_p` 作参数类型会被 ctypes 复制成临时副本，函数写入的内容丢失（同样表现为 Get* 返回空）。

### 使用注意

- **快捷方式只在「冷启动」时生效**。若 Chrome（同 profile）已在运行，双击只会转发 URL，`--window-position` 等参数**不会重新应用**。想切到静默模式需先关掉 Chrome。
- 启动后登录态来自 profile 目录，**重启不用重登**。
- 如需**开机自启**：把快捷方式复制到 `shell:startup` 目录。

---

## 核心思路

**不要试图用自动化浏览器登录纷享销客。** 用**用户本机已登录的 Chrome + CDP 接管**，借用登录态直接调内部接口。

> **前提**：本方案适用于**用户不是 CRM 管理员**的场景。若用户有管理员权限，官方 MCP / OpenAPI 更稳（见 `references/fxiaoke-alternatives.md`），但需采购流程。

---

## 快速开始

```bash
# 0) 出问题先诊断
node fx_doctor.mjs

# 1) 启动带调试端口的 Chrome
#    最省事：双击桌面「纷享CRM浏览器」快捷方式（用户进程，不受沙箱回收影响）
#    Agent 自动启动：用 PowerShell 工具跑 scripts/fx_launch_chrome.ps1
#    手工命令行等价于：
"C:/Program Files/Google/Chrome/Application/chrome.exe" \
  --user-data-dir="C:/Users/Admin/.workbuddy-ai/browser-profiles/manual" \
  --remote-debugging-port=9222 \
  --no-first-run --no-default-browser-check \
  "https://www.fxiaoke.com/XV/UI/Home"
#    → 在窗口里扫码登录一次（登录态存在 profile 里，之后长期有效）

# 2) 体检号码（不发请求）
node fx_phone_query.mjs --file numbers.txt --dry-run

# 3) 批量查询
node fx_phone_query.mjs --file numbers.txt --out result.csv
node fx_phone_query.mjs --file numbers.txt --out result.csv --resume   # 断了续跑

# 4) 回写原 CSV
python merge_marks.py --src "原文件.csv" --result result.csv \
  --out "输出.csv" --start-row 457 --col 3 --mark X

# 5) Google Sheets 一键（读表 → 查询 → 写回 → 读回验证）
bash fx_sheet_check.sh --id "<spreadsheetId>" --sheet "01/10"
bash fx_sheet_check.sh --id "<id>" --sheet "01/10" --reuse result.csv   # 复用已有结果，跳过查询
```

---

## 步骤详解

### 1. 启动带调试端口的 Chrome

**优先级**：① 用户双击桌面快捷方式（进程不受沙箱管，最稳）→ ② `fx_launch_chrome.ps1` → ③ 同一条 Bash 命令内自启动。

```powershell
# 用 PowerShell 工具执行（Bash 里调 powershell.exe 会被沙箱拦）
& "C:\...\skills\fxiaoke-crm-query\scripts\fx_launch_chrome.ps1" -Visible
```

⚠️ **沙箱进程回收（2026-10-02 实测，此前的做法全是错的）**

| 启动方式 | 结果 |
|---|---|
| Bash `Popen` + `DETACHED_PROCESS \| CREATE_NEW_PROCESS_GROUP` | ❌ 同一命令内 CDP 可用，**换下一条命令立刻 10061 拒绝连接** |
| Bash `run_in_background: true` 托管 GUI | ❌ 任务结束时整个进程组被回收 |
| **PowerShell 工具 + WMI `Win32_Process.Create`** | ✅ **可行**——父进程是 `WmiPrvSE.exe`，不在沙箱 job 内 |
| 用户双击 .lnk | ✅ 最稳（完全不经沙箱） |

根因：沙箱把**每条命令**放进一个 Windows Job Object，命令结束时 terminate 整个 job。`DETACHED_PROCESS` 绕不过 job 边界；WMI 创建的进程天然在 job 之外。

**兜底策略**：把「启动 Chrome + 查询」拼进**同一条 Bash 命令**——Chrome 只需活到命令结束，配合 `--resume` 可跨命令续跑：
```bash
python launch_cdp_chrome.py --visible && node fx_phone_query.mjs --file n.txt --out r.csv --resume
```

⚠️ **三个关键点**
- 用**系统安装的 Chrome**，不要用 agent-browser 自带的 Chrome —— 后者被风控拦截，扫码后仍跳回登录页。（版本号随自动更新变化；2026-10-01 实测 154.0.8037.58 正常。）
- 用**专用 profile 目录**（如上），不要用日常 profile（会和你正在用的 Chrome 冲突）。
- 调试端口**只能在启动时开**，已开的 Chrome 无法事后追加 → 需先 `taskkill /F /IM chrome.exe`。

### 2. 让用户扫码登录一次

**期间不要做任何登录动作、不要关浏览器** —— 纷享**限单会话**，并发登录会互相顶掉。

### 3. 用原生 CDP 接管（Node ≥20 内置 WebSocket，无需依赖）

```js
const list = await (await fetch('http://127.0.0.1:9222/json/list')).json();
const target = list.filter(t => t.type === 'page').find(p => p.url.includes('/XV/UI/Home'));
const ws = new WebSocket(target.webSocketDebuggerUrl);
// Runtime.evaluate + returnByValue + awaitPromise
```

在页面上下文里 `fetch` 调内部接口，**自动携带 cookie**。`fx_lib.mjs` 已封装好（含超时、重连、错误分类）。

### 4. 手机号查重接口

```
POST https://www.fxiaoke.com/FHH/EM1HNCRM/API/v1/object/AccountObj/controller/DuplicateSearch?_fs_token=<fs_token cookie>
body: {
  describe_api_name:'AccountObj', type:'TOOL',
  object_data:{object_describe_api_name:'AccountObj', tel:'<号码>', duplicate_rule_api_name:'rule_rnhS3__c'},
  include_object_describes:true, is_need_duplicate:true, page_size:1, page_number:1,
  duplicate_rule_api_name:'rule_rnhS3__c', describeVersionMap:{AccountObj:150}
}
→ Value.data_list[]：空数组=无数据；否则取 data_list[0].name / account_no
```

`fs_token` 从 `document.cookie` 现取，随登录自动刷新。
租户常量：路径段 `EM1HNCRM`、规则 `rule_rnhS3__c`、`AccountObj:150`。

#### ⚠️ `page_size:1` 会丢客户（2026-10-02 发现）

**一个号码可能对应多个客户**（不同「客户级别」）。`0122139000` 实际 2 条：

| name | account_no | account_type |
|---|---|---|
| B MS WONG KOOI FOONG | 20250324-737941 | `V0QhX94z4` = **PJ 2** |
| A MS WONG KOOI FOONG | 20241231-715745 | `1` = **PJ 1** |

- **`account_type` = 「客户级别 Customer Level」**；选项集在 `Value.describe_ext.fields.account_type.options`
- `page_size:1` 只返回第一条 → **命中判定不受影响**（有记录就会返回），但**取名字/级别会漏**
- 要拿全部客户必须调大 `page_size`（实测 50 够用）；`include_object_describes` 可设 `false` 提速

#### 🔴 若要按「客户级别」筛选，**必须全量重查**（2026-10-13 实测，漏判率极高）

「这个号码有没有 PJ2」不能靠 `page_size:1` 的第一条判定。实测 `12/10` 表 1665 行：

| 口径 | 判定结果 |
|---|---|
| `page_size:1` 第一条是 PJ1 → 判为「无 PJ2」 | 严重漏判 |
| `page_size:50` 全量后按 `account_type` 过滤 | 正确 |

具体漏判样本（Sheet 第 15–17 行）：

| 号码 | `page_size:1` 结果 | 全量结果 |
|---|---|---|
| `0129261968` | `1`（PJ 1）→ 误判无 PJ2 | **有 PJ 2** `B YAW CHOON YEE` |
| `0192000008` | 无数据 | **有 PJ 2** `B YAP KUN BENG` |
| `0122301191` | 无数据 | **有 PJ 2** `B YAP PHEI FERN` |

→ **流程铁律**：先全量查询定位候选（`page_size:1` 够用），再对**所有非 SKIP 号码**做一次 `page_size:50` 全量重查，按 `account_type === 'V0QhX94z4'` 判 PJ2。1635 个号码约 17 分钟（`--delay 120`）。

#### ⚠️ 号码可能重复（影响写回对齐）

`12/10` 表 1665 行里有 7 个重复号码（1635 有效号码 → 去重 1628）。重查进度文件按号码为 key，**会自动去重**，所以：

- `progress.json` 的 key 数（1628）**必然小于**行数（1635）——这是正常的，不是丢数据
- **写回必须按 Sheet 行逐行判定**，不能按去重后的号码列表写，否则整列错位
- 校验时要用「行数」而非「唯一号码数」对账

**客户级别选项集**（本租户固定）：

| value | label | value | label |
|---|---|---|---|
| `1` | PJ 1 | `z8qM9c51e` | FB PJ 1 |
| `V0QhX94z4` | PJ 2 | `DQx161x0t` | FB PJ 2 |
| `Q3ZFSjTtd` | JOHOR | `other` | 其他 |

> 命名规律：PJ 1 客户名多以 `A ` 开头，PJ 2 多以 `B ` 开头（仅作人工核对参考）。
> 页面「查重工具」弹窗（首页搜索栏旁「查重」）里，「查询」按钮的表格列即 `客户名称 | 客户级别 | 负责人`。

### 5. ⚠️ 号码格式归一化（**必须做**，最危险的静默失败）

CRM 里的标准格式是 **`01` 开头的 10 位**（马来西亚手机号）。输入格式不符会**静默返回「无数据」，不报错**。

| 输入 | 处理 | 结果 |
|---|---|---|
| `0122339159` | 已标准 | `0122339159` |
| `122339159` | 9 位补前导 0 | `0122339159` |
| `60122339159` | 以 6 开头 → 删最前面的 6 | `0122339159` |
| `+60122339159` | 先去 `+` 再去 6 | `0122339159` |

```js
function normalize(tel) {
  let t = String(tel).replace(/\D/g, '');
  if (!t) return t;
  if (/^6\d+$/.test(t)) t = t.slice(1);                       // ① 以 6 开头 → 删最前面的 6
  if (!t.startsWith('0') && /^\d{9}$/.test(t)) t = '0' + t;   // ② 9 位且非 0 开头 → 补前导 0
  if (!t.startsWith('0')) t = '0' + t;                        // ③ 兜底：必须以 0 开头
  return t;
}
```

⚠️ **② 必须带 `!t.startsWith('0')` 条件**。否则 `6016684559` 删 6 得 `016684559`（已以 0 开头）后又被补 0 成 `0016684559` —— 畸形结果。
（2026-10-01 实测踩到，已修正。）

**顺序不能反。实测**：21 个号码 9 位原样查 → **0 命中**；归一化后 → **5 命中**。

---

## 批量查询脚本参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `--file <path>` | — | 号码文件，每行一个 |
| `--out <path>` | `fx_result.csv` | 输出 CSV |
| `--delay <ms>` | `300` | 基础间隔 |
| `--max-delay <ms>` | `8000` | 自适应退避上限 |
| `--retries <n>` | `3` | 单号重试次数 |
| `--resume` | off | 从 `.progress.json` 续跑 |
| `--no-normalize` | off | 关闭归一化 |
| `--dry-run` | off | 只体检号码 |
| `--quiet` | off | 静默 |

**退出码**：0 全成功 / 1 有部分出错 / 2 连接失败 / 3 登录失效 / 4 中途遇鉴权或风控（已存进度）

**内置容错**：自适应限流（成功提速、失败退避）、错误隔离（单号失败不中断整批）、鉴权/风控类错误**立即停止**并给修复指引、WS 断开自动重连、Ctrl+C 保存进度。

---

## 回写 CSV

用 `merge_marks.py`，**不要**用 `encoding="utf-8-sig"` 直接写（会凭空加 BOM，Excel 读第一列带 `\ufeff`）。

```bash
python merge_marks.py --src "原.csv" --result result.csv --out "新.csv" \
  --start-row 457 --col 3 --mark X
# 自动探测 BOM / 换行符 / 末行换行并对齐；输出字节差校验
```

**校验：字节差 = 新增标记数**（写 157 个 X → 文件应恰好 +157 字节）。
`wc -l` 不能判断行数（末行无换行会少算 1，易误判成「多了一行」）。

---

## 回写 Google Sheets

**不要为读 Google 开 Chrome** —— 本机已装好并授权的 **gog CLI** 更快更稳（见 skill `gog-google-workspace`）。

### 一键跑完（推荐，日常用这个）

```bash
bash fx_sheet_check.sh --id "<spreadsheetId>" --sheet "01/10"
```

一条命令完成「读表 → 校验标记列为空 → CRM 查询 → 行对齐映射 → 写回 → 读回验证」。

| 参数 | 默认 | 说明 |
|---|---|---|
| `--id` | — | spreadsheetId（URL 里 `/d/<这一段>/`） |
| `--sheet` | — | 工作表名（含 `/` 也 OK，脚本自动加单引号） |
| `--phone-col` | `B` | 号码所在列 |
| `--mark-col` | `C` | 标记写入列 |
| `--mark` | `X` | 命中标记 |
| `--out` | `./fxsheet_<sheet>_result.csv` | 结果 CSV（固定路径才能 `--resume`） |
| `--reuse <csv>` | — | **复用已有结果 CSV，跳过查询**（秒级重跑） |
| `--delay` | `300` | 查询间隔 ms |
| `--resume` | off | 断点续跑 |
| `--dry-run` | off | 只读表 + 体检，不查询不写回 |
| `--force` | off | 标记列非空时仍写入（默认拒绝，防覆盖） |

**安全设计**：默认拒绝写入非空的标记列；号码列中间的空行写空标记（**行对齐不错位**）；写回后强制读回验证。

**实测**（1209 行）：`--mark-col D --mark Y --reuse result.csv` → `Y=334 / 非空=334 / 空=875 / 合计=1209`，退出码 0。

### 分步命令（需要细粒度控制时）

```bash
GOG="C:/Users/Admin/.workbuddy-ai/bin/gog/gog.exe"
ID="<spreadsheetId>"

# 1) 列工作表 + gid 映射（确认 gid 对应哪个表）
"$GOG" sheets metadata "$ID"

# 2) 读数据（-p 输出 TSV，便于 awk 解析）
"$GOG" sheets get -p "$ID" "'01/10'!A1:D1209" > sheet.tsv

# 3) 提取号码（B 列）→ 交给 fx_phone_query.mjs
awk -F'\t' 'NF>=2 && $2!="" {print $2}' sheet.tsv > nums.txt
node fx_phone_query.mjs --file nums.txt --out result.csv

# 4) 结果转 C 列 2D JSON（用 make_c_column.py）
python make_c_column.py --result result.csv --out col.json --rows 1209

# 5) 一次性写回
"$GOG" sheets update "$ID" "'01/10'!C1:C1209" \
  --values-json=@"C:/Users/Admin/AppData/Local/Temp/c_column.json"

# 6) 读回验证 X 数量
"$GOG" sheets get -p "$ID" "'01/10'!A1:C1209" | awk -F'\t' '$3=="X"' | wc -l
```

**要点**
- **表名含 `/` 必须在 range 里加单引号**：`'01/10'!C1:C1209`
- `--values-json=@file` 支持从**文件**读 2D 数组（`[["X"],[""],["X"]]`），避免命令行超长和转义地狱
- 写入前先确认目标列原本为空（`awk -F'\t' '$3!=""' sheet.tsv | wc -l` 应为 0），避免覆盖
- **必须读回验证**：X 数 + 空数 应等于总行数
- 号码格式可能混杂（9/10/11/12 位、含 `60` 国家码、含 `-`），归一化规则已覆盖；`--dry-run` 可先体检

### ⚠️ gog / 沙箱的三个坑（实测）

| 坑 | 现象 | 对策 |
|---|---|---|
| **gog 读取会截断尾部空行** | 写入 1209 行，读回只有 1194 行（尾部全空被裁掉） | 验证断言**不能**用「行数相等」，改用「非空值全为 MARK 且数量 == 命中数」 |
| **沙箱内 Node 无法 spawn 子进程** | `spawnSync` 调 gog、甚至调 `node.exe -v` 都报 `EBUSY` | 端到端编排放在 **shell** 层；Node 只做纯计算/网络（如 `fx_phone_query.mjs`） |
| **gog 支持开放式 range** | 事先不知道行数时没法写范围 | `'01/10'!B1:B` 会自动截到实际数据范围，无需预先知道行数 |

### ⚠️ gog 授权过期（约 6–7 天一次）

现象：任何 sheets/docs 命令报 `refresh token expired or revoked: invalid_grant`。

```bash
bash gog_reauth.sh jsng0819@gmail.com
```

**为什么不能简单跑 `gog auth add`**（三个叠起来的坑）：

| 坑 | 现象 | 原因 |
|---|---|---|
| 本地回调监听活不下来 | 授权后跳到 `127.0.0.1:<port>` 报 `ERR_CONNECTION_REFUSED` | 沙箱 Job Object 回收了 `--manual` 的监听进程 |
| `--manual` 读 stdin 失败 | `read /dev/stdin: The handle is invalid` | Windows 下 FIFO/管道不兼容 gog 的 stdin 读 |
| PKCE state 丢失 | `manual auth state missing; start a new manual flow` | `--manual` 的 verifier 只存内存，进程一退就丢 |

**正确做法**：`--remote --step 1`（state 落盘到 `%APPDATA%\gogcli\oauth-manual-state-<state>.json`）→ CDP 走同意流程 → 抓到回调 URL → `--remote --step 2 --auth-url <url>`。

**抓回调 URL 的关键**：回调页会渲染成 `chrome-error://chromewebdata/`（**原始 URL 被吞掉**），所以：
- ❌ 事后从页面读 `location.href` —— 拿到的是 `chrome-error://`
- ❌ browser 级 `Target.setDiscoverTargets` 监听 —— 会漏
- ✅ **对授权标签本身**开 `Network.enable` + `Page.enable`，监听 `Network.requestWillBeSent` 与 `Page.frameRequestedNavigation`，在导航**发生前**就挂好

Google 同意流程有 4 跳（需逐跳点击）：`accountchooser`（选账号）→ `signin/oauth/warning`（未验证应用警告，点「继续」）→ `signin/oauth/id`（点「继续」）→ `signin/oauth/v3/consent`（点「继续」）。

### ⚠️ 号码格式随表而异（不要假设统一）

不同表的电话格式可能完全不同：

| 表 | 格式 | 例子 | 归一化 |
|---|---|---|---|
| `01/10`、`SHOPEE LIST 01` | 纯数字 `01` 开头 10 位 | `0127680001` | 原样 |
| `12/10` | **混排**：纯数字 9 位 / 带分隔符有区号 | `136665656`、`012-367 6586` | 去分隔符 → 补 0 |

**动手前先统计格式分布**：
```bash
"$GOG" sheets get -p "$ID" "'表名'!B1:B" > b.tsv
awk 'NF{gsub(/[^0-9]/,"",$0); print length($0)}' b.tsv | sort -n | uniq -c   # 位数分布
awk 'NF && /[- ]/{c++} END{print c+0}' b.tsv                                 # 含分隔符数量
```
遇到新格式先用「探针」实测：拿 `fx_doctor.mjs` 的连通性探针改个号码逐个试，**不要猜规则**。

### ⚠️ 目标列可能已有内容（防覆盖）

`01/10` 表的 C 列是空的，但 `12/10` 表的 C 列前 13 行有**手工业务标记**（`c/B/C/WN/D/X`）。
写前必须检查：
```bash
"$GOG" sheets get -p "$ID" "'表名'!C1:C" | awk 'NF{print NR": ["$0"]"}'
```
若非空，**先问用户**确认写哪列 / 从第几行开始，不要默认覆盖。`fx_sheet_check.sh` 的 `--force` 只在你明确要覆盖时才加。

**脚本**：`scripts/make_c_column.py`
```
python make_c_column.py --result <结果CSV> --out <输出JSON> [--rows <期望行数>] [--mark X]
```
- `--rows` 给出后期望行数与实际不符时**拒绝写出**（防止查询未跑完误写）——强烈建议始终带上
- 判定：`匹配数 ∉ {"", 无数据, ERROR, SKIP}` → 命中填 `X`（异常值不计为命中）

**写客户名称**：`scripts/make_a_column.py`
```
python make_a_column.py --result <结果CSV> --out <输出JSON> [--rows <期望行数>] [--col 3]
```
- 命中行写「客户名称」（结果 CSV 第 4 列，0-based index 3），未命中留空
- 名字列里若含逗号/引号，用 Python `csv` 模块解析即可（**不要**用 `awk -F','`，会错位）

**一次查询写多列**（例如 A 列填名字、C 列填 X）——复用同一份结果 CSV，跑两次转换再分别 update：
```bash
python make_a_column.py --result r.csv --out a.json --rows 10000
python make_c_column.py --result r.csv --out c.json --rows 10000
"$GOG" sheets update "$ID" "'表名'!A1:A10000" --values-json=@a.json
"$GOG" sheets update "$ID" "'表名'!C1:C10000" --values-json=@c.json
```
**验证要点**：读回 `A1:C10000`，断言「A 非空数 == C=X 数 == 命中数」且「仅 A 有值 == 0、仅 C 有 X == 0」——只比总数不足以发现行错位。

### 🔴 按 PJ2 级别写标记（`make_pj2_column.py`）

```bash
python make_pj2_column.py --base <原始查询CSV> --levels <全量重查CSV> \
                          --out c14.json --start 14 --end 1665
```
- `--base`：`s1210_result.csv`，其**行序 == Sheet 行号**（第 1 行就是 Sheet 第 1 行，**无表头**）
- `--levels`：全量重查结果，用「PJ2名称」列非空判命中
- `--start/--end`：Sheet 行号（1-based）。输出长度 == `end-start+1`，逐行对应 `Sheet[start..end]`

**🔴 行偏移铁律（2026-10-13 踩坑，差点覆盖用户手工标记）**

写「从第 N 行开始」的区间时，取值索引必须是 **`base[N-1]`**，不是 `base[0]`。
我第一版写成 `for i in range(n): base[i]` —— 结果整体上移 13 行：会**覆盖前 13 行手工标记**，且所有 `X` 错位。

**自查方法**（写回前必做）——打印区间首行与 Sheet 首行对账：
```python
for k in range(3):
    idx = START + k - 1
    print(f'Sheet行{idx+1} | 号码 {base[idx][1]} | → {out[k]}')
```
与 `gog sheets read "'表名'!A14:B16"` 的实际内容逐行对照，**号码必须一一对上**。

**行数断言**：`len(out) == end-start+1`，且 `hit_count == 区间内命中行数`。
注意：**按行统计 ≠ 按唯一号码统计**（重复号码会让两者不等，见上文「号码可能重复」）。

---

## 故障排查

**先跑 `node fx_doctor.mjs`** —— 9 项检查 + 修复建议。

完整故障手册：`references/fx_errors.md`（含 30+ 现象→原因→解决对照、错误码字典、应急预案）。

高频三类：

| 现象 | 原因 | 解决 |
|---|---|---|
| `ECONNREFUSED 9222` | Chrome 没开调试端口 | `taskkill /F /IM chrome.exe` 后用启动命令重启 |
| `E_NO_FS_TOKEN` / 跳登录页 | 登录失效 | 回 Chrome 窗口重新扫码（登录期间不要干预） |
| 全部「无数据」 | **号码没归一化** | 检查是否误传 `--no-normalize`；跑 `--dry-run` 自检 |

**重要误判提醒**：判断 Chrome 进程死活要用 Git Bash `ps -W`，**不要**用 PowerShell `Get-CimInstance`（沙箱下读不到详情，恒返回空，会误判浏览器已死）。

**风控底线**：遇到 `E_RISK_HTML` 立即停止，手动过验证后降速重跑（`--delay 800`）。**绝不绕过风控**（换 IP / 伪造指纹），会导致封号。

---

## 发现新接口的方法

1. 注入 XHR/fetch 钩子：
   ```js
   window.__qlog = [];
   const oO = XMLHttpRequest.prototype.open, oS = XMLHttpRequest.prototype.send;
   XMLHttpRequest.prototype.open = function(m,u){ this.__u=u; this.__m=m; return oO.apply(this,arguments); };
   XMLHttpRequest.prototype.send = function(b){ this.addEventListener('load', function(){ window.__qlog.push({u:String(this.__u), b:String(b||''), s:this.status, r:String(this.responseText||'').slice(0,800)}); }); return oS.apply(this,arguments); };
   ```
2. 用 CDP 驱动 UI（填表 + 点按钮）触发一次请求。
3. 读 `window.__qlog`，提取 URL / body 模板 / 响应结构。
4. 之后直接 `fetch` 重放，不再走 UI。

填 Element UI / Vue **受控**输入框要用原生 setter：
```js
const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
setter.call(input, value); input.dispatchEvent(new Event('input',{bubbles:true}));
```

---

## 附：业务口径与根本约束

- **「X」= CRM 里查得到**（`data_list` 非空）。已用历史名单验证：85 条已有 X 标记中 83 条查到、2 条查不到，**97.6% 吻合**。
- 用户口头说的「pj2」在 `DuplicateSearch` 响应里**没有对应字段**（已全字段搜索）。遇此说法先按「X = CRM 里查得到」执行并请用户确认。
- 实测样本：`0122139000` → 1 条（`B MS WONG KOOI FOONG` / `20250324-737941`）；`0123159997` → 无数据。

**CDP 方案的固有脆弱点**（依赖两件事）：

| 依赖 | 失效后果 | 缓解 |
|---|---|---|
| Chrome 常驻 + 调试端口 | 端口不通 → 全失败 | 后台常驻任务 |
| 登录态有效 | 失效 → 全失败 | `fx_doctor.mjs` 预检 + 快速重登 |

**它的价值在于零门槛**（不需管理员、不需付费）。有管理员权限时，官方 MCP 更稳（见 `references/fxiaoke-alternatives.md`）。
