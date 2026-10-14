# 纷享销客 CDP 方案 · 故障排查手册

> 配套脚本：`fx_doctor.mjs`（诊断）、`fx_phone_query.mjs`（批量查询）、`fx_lib.mjs`（共享库）
> 原则：**先诊断，再修；不要盲试。**

---

## 一、快速定位（30 秒决策树）

```
出问题了？
│
├─ 先跑 → node fx_doctor.mjs
│
├─ ❌ CDP 端口 9222 ────────→ §3.1 浏览器没起 / 没开调试端口
├─ ❌ CRM 标签页 ──────────→ §3.2 标签页被关
├─ ❌ 登录态 ──────────────→ §4.1 登录失效，重新扫码
├─ ❌ 接口连通性 ──────────→ §5 / §6 看具体错误码
├─ ⚠️ 窗口可见性 ──────────→ 可忽略，不影响功能
│
├─ 诊断全绿但查询仍失败？
│  └─→ §7 风控 / §8 数据层 / §9 用法
│
└─ 写入 Google Sheets 环节出问题？
   ├─ 数量对不上 / 疑漏判 ──→ §8.5 page_size 漏判
   ├─ 数据整体错位 ────────→ §8.7 区间行偏移
   └─ 读回行数异常 ────────→ §8.8 gog 截断尾部空行
```

**最常用的一条命令**：
```bash
node fx_doctor.mjs
```

---

## 二、故障对照表（按现象查）

| 现象 | 最可能原因 | 跳转 |
|---|---|---|
| `connect ECONNREFUSED 127.0.0.1:9222` | Chrome 没开调试端口 | §3.1 |
| 诊断说「找不到 CRM 标签页」 | 标签页被关了 | §3.2 |
| 报 `NO_FS_TOKEN` / 跳登录页 | 登录失效 | §4.1 |
| 返回 HTML 而不是 JSON | 风控验证页 | §7 |
| 全部号码都「无数据」 | **号码没归一化** | §8.1 |
| 部分号码「无数据」 | 正常现象 | §8.2 |
| 查询变慢 / 大量 429 | 触发限流 | §6.1 |
| 脚本卡住不动 | 页面导航中 / WS 断开 | §6.2 |
| **跑 ~6 分钟后崩，无输出文件** | **CDP 长连接空闲断连** | **§6.3** |
| **「有 PJ2」的数量明显偏少** | **用了 `page_size:1`，漏判** | **§8.5** |
| **progress key 数 < 待查行数** | **表里有重复号码（正常）** | **§8.6** |
| **前 N 行被覆盖 / 标记整体错位** | **区间行偏移 bug** | **§8.7** |
| **读回只有几行，以为读失败** | **gog 截断尾部空行（正常）** | **§8.8** |
| 几十个号码报「异常 / SKIP」 | 多为源数据问题（非 01 段/外国号） | §8.9 |
| 中文乱码 / Excel 打开错列 | CSV 编码 | §8.3 |
| 结果文件比原文件多一行 | 末行换行符 | §8.4 |
| 窗口最小化、看不见 | 窗口隐藏 | §3.3 |
| 扫码后又被踢下线 | 并发登录互顶 | §4.2 |

---

## 三、环境类故障

### 3.1 CDP 端口连不上（最常见）

**现象**
```
Error: connect ECONNREFUSED 127.0.0.1:9222
❌ CDP 端口 9222 — fetch failed
```

**原因**（按概率）
1. Chrome 根本没启动
2. Chrome 启动了，但**没带 `--remote-debugging-port=9222`**
3. Chrome 已经开着，**事后无法追加调试端口**（端口只能在启动时开）
4. 端口被别的程序占用

**诊断**
```bash
curl -s http://127.0.0.1:9222/json/version
# 有 JSON → 正常；Connection refused → 确认是上面 1/2/3
```

**解决**
```bash
# ① 先彻底关掉现有 Chrome（优雅关闭无效，必须 /F）
taskkill /F /IM chrome.exe

# ② 用调试端口重启（后台常驻）
"C:/Program Files/Google/Chrome/Application/chrome.exe" \
  --user-data-dir="C:/Users/Admin/.workbuddy-ai/browser-profiles/manual" \
  --remote-debugging-port=9222 \
  --no-first-run --no-default-browser-check \
  "https://www.fxiaoke.com/XV/UI/Home"
```

⚠️ **不要用日常 profile 目录**（会和你正在用的 Chrome 冲突）。用上面这个专用 profile，登录态会落盘，重启不用重登。

⚠️ **必须用系统安装的 Chrome（153），不要用 agent-browser 自带的 Chrome 154** —— 154 + 自动化模式会被纷享风控拦截，扫码后仍跳回登录页。

**预防**：把启动命令做成后台常驻任务，别每次手动开。

---

### 3.2 找不到 CRM 标签页

**现象**
```
❌ CRM 标签页 — 找不到 CRM 标签页
E_NO_TARGET: 找不到 CRM 标签页
```

**原因**：CRM 标签页被关闭；或 URL 不含 `/XV/UI/Home`。

**解决**：脚本已内置**自动新建标签页**（`findCrmTarget({create:true})`）。若仍失败：
1. 手动在 Chrome 里打开 `https://www.fxiaoke.com/XV/UI/Home`
2. 确认已登录
3. 重跑 `node fx_doctor.mjs`

**注意**：新建的标签页共用同一 profile 的 cookie，**通常无需重新登录**。若新标签页跳到登录页 → 说明登录态已过期 → §4.1。

---

### 3.3 窗口不可见 / 最小化

**现象**
```
⚠️ 窗口可见性 — visibility=hidden outerWidth=1050
```

**结论：不影响功能。** 实测窗口 hidden 时接口调用完全正常（`fetch` 不受后台标签页节流影响）。

若确实需要窗口可见：
```js
// 通过 CDP 执行
window.focus()
```

---

### 3.4 Chrome 进程「疑似死了」（重要误判）

**现象**：PowerShell 查进程返回空，误以为浏览器挂了。

**原因**：PowerShell 的 `Get-CimInstance ... ExecutablePath` 在沙箱环境下**读不到** agent-browser 托管的 Chrome 进程详情，恒返回空。

**正确诊断**：用 Git Bash
```bash
ps -W | grep -i chrome | head -20
```

**教训**：不要用 PowerShell 判断浏览器死活。

---

## 四、登录类故障

### 4.1 登录失效（第二常见）

**现象**
- 脚本报 `E_NO_FS_TOKEN`（cookie 里没 `fs_token`）
- 或 `E_REDIRECTED`（请求被 302 到登录页）
- 或诊断显示 `fs_token=无` / `url=.../login`

**原因**
- 会话超时（纷享有闲置超时）
- 在别处登录，把当前会话顶掉
- 手动退出登录

**解决**
1. 切到 Chrome 窗口
2. 用微信扫码 / 账号密码重新登录
3. **登录期间不要跑脚本、不要关浏览器**
4. 登录成功后重跑 `node fx_doctor.mjs` 确认

**关键**：`fs_token` 存在 cookie 里，**脚本每次运行时现取**，所以只要浏览器保持登录，脚本无需维护 token。

---

### 4.2 扫码后又被踢下线（踩过的坑）

**原因**：纷享**限制单会话**。如果在用户扫码期间，脚本/其他程序也在提交登录，两边互相顶掉。

**解决**
- **用户登录期间，不做任何登录动作、不关浏览器**
- 不要并发多端登录

**血泪教训**：之前出现过「用户扫码 → 我同时尝试登录 → 互相顶掉 → 用户以为扫码失败」。**让用户自己登，全程不要干预。**

---

### 4.3 平台单一登录限制

**背景**：纷享限制同一账号单点登录。

**CDP 方案的优势**：复用**已登录的浏览器会话**，不产生新登录，**不会顶掉用户当前的会话**。这也是 CDP 方案相对「脚本直接登录」的核心优势。

---

## 五、接口类故障（错误码字典）

### 5.1 错误码速查

| errorCode | 含义 | 处理 |
|---|---|---|
| `0` | 成功 | — |
| `10006` | 参数缺失/非法（appSecret 等） | 检查请求体 |
| `20016` | token 需刷新 | 重新取 token |
| `20017` | **corpAccessToken 为必填项，不能为空** | 内部接口：检查 `_fs_token`；官方 API：检查 token |
| `30003` | **未购买 Open API 资源包** | 仅官方 OpenAPI 路径会遇到，联系客服采购 |
| `41001` | 参数错误（如 redirectUrl） | 检查参数名 |

> `20017` 是 CDP 方案下最可能见到的接口错误码。它表示请求没带上有效凭证 —— 通常是 `fs_token` 失效，回 §4.1。

### 5.2 响应解析失败

| 脚本错误码 | 含义 | 处理 |
|---|---|---|
| `E_BAD_JSON` | 响应不是合法 JSON | 页面导航中或网关异常 → 脚本自动重试 |
| `E_RISK_HTML` | 返回 HTML（风控页） | §7 |
| `E_FETCH` | 页面内 fetch 抛错 | 网络抖动 → 自动重试 |
| `E_API_ERROR` | 接口返回非 0 errorCode | 看 detail 里的码 |

---

## 六、网络 / 连接类故障

### 6.1 触发限流

**现象**：出现 `E_HTTP_429`，查询变慢，重试增多。

**脚本已内置**：
- 自适应限流：连续成功 → 间隔 ×0.8（下限 `--delay`）；出错 → 间隔 ×1.5（上限 `--max-delay`）
- 指数退避重试：`baseDelay × 2^attempt`

**手动调优**
```bash
# 更保守（慢但稳）
node fx_phone_query.mjs --file n.txt --out r.csv --delay 800 --retries 5

# 更激进（快，但风控风险高）
node fx_phone_query.mjs --file n.txt --out r.csv --delay 150 --max-delay 3000
```

**建议**：默认 300ms 已实测稳定。大批量（>1000）建议 500ms。

### 6.2 脚本卡住不动

**原因**
- 页面正在导航 → 执行上下文失效（`E_CTX_DESTROYED`）
- WebSocket 断开（标签页关闭 / Chrome 崩溃）

**脚本已内置**
- 所有 CDP 命令带超时（默认 30s），超时抛错而非永久挂起
- WS 断开自动重连（`ensureSession({force:true})`）

**手动处理**：Ctrl+C 中断 → 进度已保存 → 修好环境后 `--resume` 继续。

### 6.3 CDP WebSocket 断开（⚠️ 2026-10-13 实测：**长跑必断**）

**现象**：`E_WS_CLOSED: CDP WebSocket 已断开`

#### 🔴 关键实测：**长连接约 6 分钟空闲即被 Chrome 侧断开**

2026-10-13 对 `12/10` 表 1635 个号码做全量重查时实测：

| 脚本 | 结果 |
|---|---|
| `fx_recheck.mjs`（原版，一次性长连接、无重连、无续跑） | 跑到 **~350/1635**（约 6 分钟）崩，**无输出文件，进度全丢** |
| `fx_recheck_resume.mjs`（新版，续跑 + 重连） | 跑满 **16分56秒 / 1635 条**，0 错误 0 重连 |

崩溃特征：`at Socket.onSocketClose (node:net:...)` → `code: 'E_WS_CLOSED', kind: 'env'`
→ **是 Chrome 主动断开 WebSocket，不是 Chrome 崩了**（崩后 CDP 端口会连不上，实测端口一直正常）。

#### 判别：是「Chrome 死了」还是「WS 空闲断了」

```bash
curl -s -m 5 http://127.0.0.1:9222/json/version     # 有 JSON → Chrome 活着 → 是 WS 断了
curl -s -m 5 http://127.0.0.1:9222/json/list | grep fxiaoke   # 标签页还在 → 直接重连即可
```

#### 解法（已固化为脚本）

**任何预计超过 5 分钟的批量任务，必须用带「断点续跑 + 自动重连」的脚本**：

- 批量查询 → `fx_phone_query.mjs`（已内建）
- 全量重查 → `fx_recheck_resume.mjs`（2026-10-13 新建，`--chunk 20` 每 20 条落盘）

```bash
node fx_recheck_resume.mjs --file tels.txt --out levels.csv --delay 120 --chunk 20
# 中断后重跑同一条命令即自动续跑（读 <out>.progress.json）
```

**重连实现要点**：捕获 `E_WS_CLOSED` / `E_CTX_DESTROYED` / `E_WS_TIMEOUT` →
`session.close()` → `findCrmTarget()` 重新找标签 → `CdpSession.connect()` → **重试当前号码**（最多 4 次）。

**手动处理**：Ctrl+C 中断 → 进度已保存 → 修好环境后重跑同命令续跑。

#### 其他导致 WS 断开的情况

1. Chrome 崩溃（此时 CDP 端口也不通）→ 重启 Chrome，登录态保留
2. 标签页被关 → 脚本自动新建
3. 页面导航中 → `E_CTX_DESTROYED`，自动重试

---

## 七、风控

**现象**
- `E_RISK_HTML`：响应是 HTML 而不是 JSON
- 接口突然全部失败
- 页面出现验证码 / 滑块

**原因**：请求频率过高、行为特征异常、IP 异常。

**处理（重要）**
1. **立即停止脚本**（脚本检测到 `risk` 类错误会自动中止整批）
2. 切到 Chrome 窗口，**手动完成验证**
3. 确认页面能正常访问后，再降速重跑：`--delay 800`
4. 若持续被拦 → 暂停几小时再试

**预防**
- 不要低于 300ms 间隔
- 不要并发（本方案是串行的，不要改成多线程）
- 不要 24 小时不间断跑

⚠️ **绝对不要**尝试绕过风控（换 IP、伪造指纹等）—— 会导致账号被封。

---

## 八、数据层故障

### 8.1 全部「无数据」（最危险的静默失败）

**现象**：一批号码全部返回「无数据」，但你知道其中有些是存在的。

**原因**：**号码格式没归一化**。

CRM 里的标准格式是 **`01` 开头的 10 位**（马来西亚手机号），如 `0122339159`。输入 9 位（`122339159`）会**静默返回无数据**，不报错。

**实测数据**：21 个号码用 9 位原样查 → **0 命中**；归一化后 → **5 命中**。

**归一化规则**（顺序不能反）
| 输入 | 处理 | 结果 |
|---|---|---|
| `0122339159` | 已标准 | `0122339159` |
| `122339159` | 9 位补前导 0 | `0122339159` |
| `60122339159` | 以 6 开头 → 删最前面的 6 | `0122339159` |
| `+60122339159` | 先去 `+` 再去 6 | `0122339159` |

**脚本默认开启归一化**，并同时输出「输入号码」和「查询号码」两列，便于核对。

**自检**
```bash
node fx_doctor.mjs          # 含归一化 5 用例自检
node fx_phone_query.mjs --file n.txt --dry-run   # 只体检不发请求
```

**误关了归一化？** 检查是否传了 `--no-normalize`。

### 8.2 部分号码「无数据」

**正常。** CRM 里确实没有这个客户。已用历史数据验证：「X」标记的行 97.6% 能查到，剩余是客户已删除/改名。

### 8.3 CSV 中文乱码 / Excel 打开错列

**原因**：编码问题。脚本输出 **UTF-8 无 BOM**。

- Excel 打开中文乱码 → 用「数据 → 从文本/CSV」导入并选 UTF-8，或用记事本/VSCode 打开
- 如果下游要求带 BOM → 转一次：
  ```bash
  python -c "p='r.csv';d=open(p,'rb').read();open(p,'wb').write(b'\xef\xbb\xbf'+d)"
  ```

### 8.4 结果文件比原文件多一行

**原因**：原文件**末行没有换行符**，脚本写出时补了一个。这是 `wc -l` 的计数差异，**不是多了一条记录**。

**验证方法**：比字节数，而不是比行数。
```bash
# 记录数应一致
python -c "
import csv,io
a=list(csv.reader(io.StringIO(open('原.csv',encoding='utf-8-sig').read())))
b=list(csv.reader(io.StringIO(open('新.csv',encoding='utf-8').read())))
print('原',len(a),'新',len(b))
"
```

**回写原 CSV 时**：用 `merge_marks.py`（字节级对齐 BOM / 换行 / 末行），不要用 `utf-8-sig` 直接写 —— 那会凭空加 BOM，导致 Excel 读第一列带 `\ufeff`。

### 8.5 🔴 按级别筛选时大量漏判 PJ2（2026-10-13 实测）

**现象**：用 `page_size:1` 查询后按第一条记录的级别判定，结果「有 PJ2」的数量明显偏少。

**原因**：**一个号码可对应多个客户**（不同「客户级别」）。`page_size:1` 只返回第一条：

- **命中判定不受影响**（有记录就会返回）
- **但级别/名字会错** —— 第一条是 PJ1 时，会误判为「无 PJ2」

**实测漏判样本**（`12/10` 表 Sheet 第 15–17 行）：

| Sheet 行 | 号码 | `page_size:1` | 全量（`page_size:50`） |
|---|---|---|---|
| 15 | `0129261968` | `1`（PJ 1）→ 判「无 PJ2」 | **有 PJ 2** `B YAW CHOON YEE` |
| 16 | `0192000008` | 无数据 | **有 PJ 2** `B YAP KUN BENG` |
| 17 | `0122301191` | 无数据 | **有 PJ 2** `B YAP PHEI FERN` |

> 第 16、17 行连「无数据」都出现了 —— 说明取到的可能是完全不同的记录，不只是级别取错。

**正确流程（铁律）**：

```
① 全量查询（page_size:1 够用）   → 定位「哪些号码有记录」
② 对「所有非 SKIP 号码」全量重查   → page_size:50，取全部匹配
③ 按 account_type 过滤          → 'V0QhX94z4' = PJ2
④ 按 Sheet 行逐行判定 → 写回
```

脚本：`fx_recheck_resume.mjs`（`--delay 120` 实测 1635 条约 17 分钟）

**漏判率不容忽视**：不能为了省时间跳过第 ② 步。

### 8.6 ⚠️ 号码重复 → 唯一号码数 ≠ 行数（写回会错位）

**现象**：`progress.json` 的 key 数（1628）小于待查行数（1635），以为丢了数据。

**原因**：**表里存在重复号码**。`12/10` 表 1665 行里有 **7 个重复号码**（1635 有效 → 去重 1628）。

`progress.json` 以「号码」为 key → 天然去重。**这不是丢数据。**

**影响与对策**：

- ✅ 查询层面：去重是好事，省请求
- 🔴 写回层面：**必须按 Sheet 行逐行判定**。若按去重后的号码列表生成 2D JSON，整列会错位
- ✅ 校验层面：**用「行数」对账，不能用「唯一号码数」**，否则 `303` vs `305` 会误判为出错

**自查**

```python
want = [l.strip() for l in open('tels.txt')]
prog = json.load(open('levels.csv.progress.json'))
print('待查行数', len(want), '唯一号码', len(set(want)), 'progress', len(prog))
miss = [t for t in want if t not in prog]      # 应为 0（无缺失）
print('缺失', len(miss))
```

### 8.7 🔴 区间行偏移 → 覆盖上方数据（2026-10-13 自己踩的坑）

**现象**：要求「从第 14 行开始写」，结果**前 13 行被覆盖**，所有标记整体上移 13 行。

**原因**：转换脚本写成 `for i in range(n): base[i]` —— 从 `base[0]` 取值。但 `--start 14` 要求从**第 14 行**（= `base[13]`）开始。

**发现方式**：输出「PJ2 命中 307」与手工核算的 `303` 不符 → 差值 `4` 定位到偏移（前 13 行里有 4 个 PJ2 命中）。

**铁律**：写「从第 N 行开始的区间」时，取值索引 = **`base[N-1]`**。

```python
lo = START - 1                    # ✅ 正确
hi = END
out = [judge(base[idx]) for idx in range(lo, min(hi, len(base)))]
assert len(out) == END - START + 1
```

❌ 错误写法：`for i in range(n): ...base[i]...`（从 0 起，整体上移）

**写回前必须对账**（2 分钟，能挡住这类事故）：

```python
for k in range(3):
    idx = START + k - 1
    print(f'Sheet行{idx+1} | 号码 {base[idx][1]} | → {out[k]}')
```
与 `gog sheets read "$ID" "'表名'!A14:B16"` 的实际内容**逐行对照，号码必须一一对上**。

**写回后必须断言**：

```python
assert len(out) == END - START + 1
assert sum(1 for x in out if x == ['X']) == expected_hit_rows
assert after[:START-1] == backup[:START-1]        # 上方未动
assert all(after[START-1+k].strip() == out[k][0].strip() for k in range(len(out)))
```

**保护措施**：写区间前先备份目标列 ——
```bash
"$GOG" sheets read "$ID" "'表名'!C1:C1665" > c_backup.txt
```

### 8.8 gog 读取截断尾部空行（验证断言会误判）

**现象**：读 `C1:C1665` 只回 13 行（因为 14–1665 全空），以为读失败。

**原因**：gog 不回尾部纯空行。这是正常行为。

**影响**：**验证断言不能用「行数相等」**。

```bash
"$GOG" sheets read "$ID" "'表名'!C1:C1665" | wc -l     # 可能只有 13，不代表失败
```

**正确做法**：把读回结果按需补空行到预期长度，再做**逐行内容比对**（见 §8.7 断言）。

### 8.9 异常号码是真实数据问题，不要当脚本 bug 修

**现象**：一批里有几十个返回「异常 / SKIP」。

**先分类，再判断**。`12/10` 表 30 个异常实测全部是**源数据问题**：

| 数量 | 样例 | 原因 |
|---|---|---|
| 25 | `65xxxxxxxx` | 新加坡号码（+65），非马来西亚 |
| 3 | `4.48E+11` | **Excel 科学计数法**，原号码已永久丢失，需回源头修 |
| 1 | `00-447818506299` | 英国号码（+44） |
| 1 | `6095666188` → `095666188` | 马来西亚但非 `01` 段 |

**对策**：报告给用户，**不要在脚本里「修」**（如强行归一化外国号码会产生错误查询）。
科学计数法丢失的号码，脚本层面无法还原 —— 必须回原始来源补。

---

## 九、脚本用法与参数

```bash
# 环境诊断（出问题先跑这个）
node fx_doctor.mjs
node fx_doctor.mjs --quick          # 只查 CDP + 登录态

# 批量查询
node fx_phone_query.mjs 0122139000 0123159997
node fx_phone_query.mjs --file numbers.txt --out result.csv
node fx_phone_query.mjs --file numbers.txt --out result.csv --resume   # 断点续跑
node fx_phone_query.mjs --file numbers.txt --dry-run                   # 只体检
node fx_phone_query.mjs --file numbers.txt --delay 500 --retries 5     # 调参
node fx_phone_query.mjs --no-normalize 122891188                       # 关归一化
```

| 参数 | 默认 | 说明 |
|---|---|---|
| `--file <path>` | — | 号码文件，每行一个 |
| `--out <path>` | `fx_result.csv` | 输出 CSV |
| `--delay <ms>` | `300` | 基础间隔 |
| `--max-delay <ms>` | `8000` | 自适应退避上限 |
| `--retries <n>` | `3` | 单号重试次数 |
| `--resume` | off | 从进度文件续跑 |
| `--no-normalize` | off | 关闭号码归一化 |
| `--dry-run` | off | 只体检号码，不发请求 |
| `--quiet` | off | 静默模式 |

**退出码**
| 码 | 含义 |
|---|---|
| 0 | 全部成功 |
| 1 | 有部分号码出错（结果仍已写出） |
| 2 | 连接失败（CDP/标签页） |
| 3 | 登录失效 |
| 4 | 中途遇鉴权/风控，已保存进度 |

---

## 十、应急预案

### 场景 A：跑到一半断了

```bash
# 1) 先诊断
node fx_doctor.mjs
# 2) 按提示修复（多数是重新登录）
# 3) 续跑（不会重复请求已完成的号码）
node fx_phone_query.mjs --file numbers.txt --out result.csv --resume
```

进度文件：`<out>.progress.json`。任务正常跑完会自动删除。

### 场景 B：登录态反复失效

1. 确认没有其他端在登录同一账号（§4.2）
2. 检查系统时间是否准确（时间偏差会导致 token 校验失败）
3. 换用扫码登录而非密码登录
4. 登录后先跑 `fx_doctor.mjs --quick` 确认稳定，再跑批量

### 场景 C：风控拦截

1. **停**。不要重试、不要换 IP、不要加速
2. 手动在浏览器完成验证
3. 降速到 `--delay 800` 重跑
4. 仍不行 → 停几小时

### 场景 D：Chrome 崩溃

```bash
taskkill /F /IM chrome.exe
# 用 §3.1 的启动命令重启（登录态保留在专用 profile 里）
node fx_doctor.mjs
```

---

## 十一、预防性维护

| 频率 | 动作 |
|---|---|
| 每次跑批量前 | `node fx_doctor.mjs --quick` |
| 每次跑批量前 | `--dry-run` 体检号码格式 |
| 大批量（>500）前 | 先抽 20 个试跑，确认命中率合理再全量 |
| 每周 | 检查 Chrome 是否还在运行（`ps -W \| grep -i chrome`） |
| 遇失败 | 记下错误码 + 场景，补充到本手册 |

### 关键设计原则（为什么这样写）

1. **串行 + 间隔** —— 避免风控，宁可慢
2. **自适应限流** —— 成功提速、失败退避，自动找平衡点
3. **错误隔离** —— 单号失败不中断整批，但鉴权/风控**立即停**
4. **断点续跑** —— 长任务不怕中断
5. **预检优先** —— 开跑前验登录态，避免整批白跑
6. **不绕过风控** —— 合规底线，宁可慢

---

## 附：本方案的根本约束

CDP 方案依赖两件事，这是它的**固有脆弱点**：

| 依赖 | 失效后果 | 缓解 |
|---|---|---|
| Chrome 常驻 + 调试端口 | 端口不通 → 全部失败 | 后台常驻任务 |
| 登录态有效 | 失效 → 全部失败 | 预检 + 快速重登 |

**如果用户能拿到管理员授权**，官方 MCP / OpenAPI 路径更稳（见 `fxiaoke-alternatives.md`）。
但在**非管理员**的前提下，CDP 是唯一可行方案 —— 它的价值就在于**零门槛**。
