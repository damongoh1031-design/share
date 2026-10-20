# CC CRM 原型 · 代码整理与图谱（v4.0）

> 阅读对象：`prototype/crm-prototype.html`（v4.0，马来西亚场景，浅色默认 + 品牌化）及其周边（`_test/`、`README.md`）。
> 配套可视化图谱：`docs/code-map.html`（点方块看模块详情）。
> 更新：2026-10-20 · 3,745 行 / 288 KB

## TL;DR

单文件、零依赖、全量重渲染。3,745 行 = 477 行 HTML+CSS + 3,268 行 JS；
105 个函数、13 个页面视图、68 个动作处理器、19 种表单分支、12 张内存表、21 个权限点。
架构仍是「**事件委托 → 动作表 → 改 DB/state → saveDB → render 全量重建 → applyLang**」一条直线。

v3 在这条直线上加了三个东西：**角色化首页**（改路由）、**客户池**（加状态与领域函数）、**可调闸门**（加配置项）。

---

## 1. 分层结构

| 层 | 行号 | 内容 |
|---|---|---|
| ① 交互入口 | 3132–3604 | click / change / input / submit / keydown 五个委托监听器 |
| ② 动作层 | 2707–3128 | `A` 表 68 个处理器 + 19 种表单分支 + nextId / closeModal / logLogin |
| ③ 渲染管线 | 2679–2706 | `viewHtml()` 13 个 case → `render()` → `shell()` → 视图 → `applyLang()` |
| ④ 领域逻辑 | 757–929 / 2134–2263 / 3088–3128 | 权限三件套、体检三规则、**客户池四函数**、**频次闸门两函数**、呼叫台、审计 |
| ⑤ 数据层 | 592–737 | `SETTING_DEFAULTS`、`buildSeed()`、`loadDB()`、`saveDB()`、12 张表、`state` 31 字段 |
| ⑥ 表现层 | 1–417 / 989–1200 | 4 套主题变量 + 覆写块、`--fs` 字号、493 条词条 + 48 条正则 |

---

## 2. 数据模型（12 张表）

| 表 | 关键字段 | 说明 |
|---|---|---|
| `users` | id, username, name, role, managerId, active, pwd, extra[], mustChange | 自引用汇报树 |
| `roles` | role → 权限点数组 | admin 由 `PERMS.map` 生成 |
| `teams` | id, name, supervisorId | 组员 = `users.managerId === supervisorId` |
| `customers` | id, name, phone, company, source, category, status, ownerId, remark, dnc, invalid, mergedInto, **pool**, **claimedAt**, lastContactAt, version | `pool: public/private` 是本轮新增的核心状态 |
| `notes` | id, custId, at, result, content, userId, voided | 频次闸门按它计数 |
| `tasks` | id, custId, title, assigneeId, scheduledAt, originalScheduledAt, status, remindBefore, rescheduleCount, completedAt/By, cancelReason | 双人指针 |
| `notifications` | id, userId, taskId, title, body, createdAt, status | unread/read/expired |
| `audit` | id, at, userId, action, detail | 保留 300 条 |
| `logins` | id, userId, username, ok, at, ip, device, note | 失败登录也记 |
| `reveals` | id, userId, custId, at | 号码查看限次 |
| **`requests`** | id, type, custId, fromId, toId, reason, status, createdAt, decidedAt, decidedBy | **本轮新增**：跨组流转审批单 |
| `settings` | cycleDays, cycleMax, maskPhone, exportLimit, revealDailyLimit, theme, fs, lang, **gateOn/gateDays/gateMax/gateStart/gateEnd**, **poolOn/claimLimit/protectDays/autoRecycle/crossApprove** | 单行配置；主题字号语言也在这里 |
| `meta` | seedDay, seq{…, request} | `seedDay ≠ 今天` 触发整库重建 |

**造数三件事**（`buildSeed`）：相对日期 `dAt()` 保证「今天永远有到期数据」；挑「无待办无记事」的客户做 2 个待回收 + 3 个公海样本；号码与公司名按马来西亚本地化。

---

## 3. 权限模型（21 个权限点）

```
can(p)            = admin ? true : extra.includes(p) || roles[role].includes(p)
scopeIds()        = admin ? 所有人 : supervisor ? [自己 + 直属下属] : [自己]
canSeeCustomer(c) = can('customer.view') && (c.pool === 'public' || scopeIds().includes(c.ownerId))
```

`c.pool === 'public'` 那一行是本轮的关键改动：**公海对所有能看客户的人开放**，这是公海能成立的前提。
其余判定不变——数据范围永远不随权限点变化。

| 角色 | 客户池权限 |
|---|---|
| 员工 | `customer.claim` 领取 |
| 主管 | 领取 + `customer.recycle` 退回/回收 + `customer.approve` 审批 |
| 管理员 | 全部 |

---

## 4. 客户池领域函数（本轮新增）

| 函数 | 行号 | 职责 |
|---|---|---|
| `ownerName(c)` | 801 | 公海显示「公海」，否则取负责人名 |
| `myCustomers()` / `privateCount(uid)` | 806 / 807 | 我的私海 / 某人私海数量（用于领取上限） |
| `poolList()` | 818 | 公海客户 |
| `lastFollowTs(c)` / `protectLeft(c)` | 822 / 827 | 最后一次有效跟进 / 剩余保护期（负数=超期） |
| `isRecyclable(c)` | 829 | 超期 + 无待办 + 未禁呼 + 未合并 |
| `runAutoRecycle(silent)` | 837 | 批量回收并写审计 |
| `gateInfo(c)` / `gateCheck(c)` | 850 / 855 | 近 N 天联系次数 / 时段+次数双校验 |
| `pendingRequests()` | 864 | 待审批单 |

> 这些函数全部**不碰 DOM**，只读写 DB，所以能被列表、详情、呼叫台、KPI 看板共用。

---

## 5. 视图索引（13 个）

| view | 函数 | 行号 | 说明 |
|---|---|---|---|
| `dashboard` | `dashboardView` | 1336 | **主管/管理员首页**：4 KPI + 客户池三格 + 资产待处理 + 今日/逾期 |
| `calendar` | `calendarView` | 1728 | **员工首页**：4 个人 KPI + 月历 + 今日/逾期列表 |
| `customers` | `customersView` | 1457 | 三个页签：客户 / 公海 / 待回收；行内领取、退回 |
| `customer` | `customerView` | 1560 | 详情 + 频次提示 + 申请转组 + 退回公海 |
| `call` | `callView` | 2134 | 呼叫台（手动拨号 + 登记），队列已排除频次满与公海客户 |
| `approvals` | `approvalsView` | 2274 | **本轮新增**：待审批 + 审批历史 |
| `datahealth` | `datahealthView` | 1660 | 重复 / 无效 / 周期重呼 |
| `board` / `notes` / `users` / `perms` / `settings` / `logs` | — | — | settings 涨到 112 行（两张新卡） |

覆盖层：`modalHtml`（2382，19 种弹窗）、`drawerHtml`（2338，4 种抽屉）。

---

## 6. 动作索引（68 个，新增 9 个）

| 新增分组 | 动作 |
|---|---|
| 客户池（6） | `pool-tab` `pool-claim` `bulk-claim` `pool-release` `bulk-release` `run-recycle` |
| 跨组审批（3） | `req-cross` `req-approve` `req-reject` |

其余沿用 v2：会话/导航/资产保护/客户流转/记事回访/导入导出/体检/通知/日历/外观/呼叫台/账号密码/小组/系统。

表单新增 1 种：`cross`（申请跨组流转），共 19 种。

---

## 7. 角色化首页的实现

```js
function homeView() { return state.user.role === 'agent' ? 'calendar' : 'dashboard'; }

// 登录、切换用户、boot 恢复会话都走 homeView()
state.view = homeView();

// 员工手动改成 dashboard 也回不去
case 'dashboard': return state.user.role === 'agent' ? calendarView() : dashboardView();
```

导航也按角色生成：员工菜单是 `我的日程 / 呼叫台 / 客户 / 呼叫记事`，没有 KPI 看板、体检、看板、用户管理。
**不是隐藏按钮，是菜单里就没有**——这比 `display:none` 更诚实，也少一个越权入口。

---

## 8. 可调闸门：参数怎么生效

| 参数 | 读取点 | 效果 |
|---|---|---|
| `gateOn` | `gateCheck` / `callQueue` | 关掉后完全不校验 |
| `gateDays` / `gateMax` | `gateInfo` | 统计窗口与次数上限 |
| `gateStart` / `gateEnd` | `gateCheck` | 当前小时不在区间即拦截 |
| `poolOn` | `isRecyclable` / 客户页页签 | 关掉后不显示公海机制 |
| `claimLimit` | `pool-claim` / `bulk-claim` | 达到上限拒绝或跳过 |
| `protectDays` | `protectLeft` | 改完立即影响「待回收」列表 |
| `autoRecycle` | `isRecyclable` | 关掉后只能手动退回 |
| `crossApprove` | `cross` 表单分支 | 关掉后申请直接生效 |

全部走同一个 `data-set` 处理器写 `DB.settings` + `saveDB()`，没有第二套配置路径。

---

## 9. 代码度量

| 指标 | v2.0 | v3.0 |
|---|---|---|
| 行数 / 体积 | 3,195 / 228 KB | **3,745 / 288 KB** |
| 函数 | 91 | **105** |
| 视图 | 12 | **13** |
| 动作 | 59 | **68** |
| 表单分支 | 18 | **19** |
| 数据表 | 11 | **12** |
| 权限点 | 18 | **21** |
| i18n | 451+43 | **496+52** |
| 回归断言 | 51 | **81**（suite 51 + suite3 30） |

---

## 10. 已知债务（v3 后）

| # | 问题 | 严重度 | 建议 |
|---|---|---|---|
| 1 | 自动回收只在打开客户页时扫描，不是定时任务 | 中 | 后端加每日 cron |
| 2 | 公海全公司共享，不按小组隔离 | 中 | 需要时给 customer 加 `poolScope` |
| 3 | `protectLeft` 只看最后一次记事，不区分「有效跟进」 | 中 | 加 `note.effective` 标记 |
| 4 | 6 处 `prompt()` 输入原因 | 中 | 换统一弹窗 |
| 5 | `modalHtml` 已 290 行 | 中 | 拆成 `MODALS[type]` 映射 |
| 6 | i18n 漏词条无自动检测 | 中 | 把「英文模式残留中文」做成断言 |
| 7 | 审批单只支持单级、无超时升级 | 低 | 需要时加 `level` / `escalateAt` |
| 8 | 号码只校验格式，不判断运营商与空号 | 低 | 加 `my_prefixes` 表 |

---

## 11. 扩展手册

**加一个页面**：写 `xxxView()` → `viewHtml()` 加 case → `navItems()` 加项（要权限就 `if (can(...))`）。
**加一个权限点**：`PERMS` 加一行 → 角色默认值里决定给谁 → 视图用 `can()` 守卫。
**加一个客户池规则**：写在 `isRecyclable()` 里，所有入口（列表、看板、定时）自动一致。
**加一个可调参数**：`SETTING_DEFAULTS` 加默认值 → `settingsView` 加 `data-set="key"` 输入 → 领域函数读 `DB.settings.key`。
**加一种语言**：复制 `EN` 为 `MS`（马来语），`applyLang()` 按 `DB.settings.lang` 选字典。

---

## 12. 一句话评价

**作为 MVP 原型仍然合格**：业务规则（权限分层、客户池流转、频次控制、角色化首页）都落到可执行代码里，
81 条断言兜底，改坏了立刻能发现。

**仍然不是产品代码**：没有后端、密码明文、权限只在前端、回收不是真定时。
正确用法是拿它跟业务方确认规则，确认完按 README 第 10 节的映射重写成 Go + SQLite。
