# 外呼 CRM 原型 · 代码整理与图谱

> 阅读对象：`prototype/crm-prototype.html`（v2.0）及其周边（`_test/`、`README.md`、`kb/`）。
> 配套可视化图谱：`docs/code-map.html`（点方块看模块详情）。
> 阅读日期：2026-10-20 · 代码版本：v2.0 · 3,195 行 / 228 KB

## TL;DR

一个**单文件、零依赖、全量重渲染**的 HTML 原型：3,195 行里 417 行 HTML+CSS、2,777 行 JS，91 个函数、
12 个页面视图、59 个动作处理器、18 种表单分支、11 张内存表。
架构是「**事件委托 → 动作表 → 改 DB/state → saveDB → render 全量重建 → applyLang**」一条直线，
没有框架、没有虚拟 DOM、没有构建。它验证的是**业务规则**（权限、资产保护、分配、呼叫流程），不是技术架构。

---

## 1. 代码库组成

| 文件 | 规模 | 职责 |
|---|---|---|
| `prototype/crm-prototype.html` | 3,195 行 / 228 KB | 全部产品代码：CSS + 数据 + 视图 + 交互 + i18n |
| `prototype/README.md` | ~230 行 | 需求落点表、账号表、体验路径、权限模型、后端映射、已知限制 |
| `prototype/_test/cdp.mjs` | 90 行 | Chrome DevTools Protocol 驱动（启动 headless、attach、evaluate、捕获异常） |
| `prototype/_test/suite.mjs` | ~200 行 | 51 条回归断言，覆盖 14 条需求 |
| `prototype/_test/shots.mjs` | 70 行 | 14 张截图（含 4 套主题、英文界面） |
| `prototype/screenshots/` | 14 张 PNG | 评审用 |
| `kb/callcenter-crm-interactive-prototype.md` | v3 | 可复用知识沉淀（方法论，不含源码细节） |
| `docs/code-map.html` | 本图谱 | 六层结构图 + 数据模型 + 度量 + 分区索引 |

---

## 2. 分层结构（六层）

| 层 | 位置 | 内容 | 关键约束 |
|---|---|---|---|
| ① 交互入口 | 2738–3182 | 5 个全局委托监听器：click / change / input / submit / keydown | 全部通过 `data-*` 属性路由，不给元素单独绑事件 |
| ② 动作层 | 2414–2736 | `A` 表 59 个处理器 + 18 种表单分支 + 辅助（nextId / expireNotifs / closeModal / logLogin / doLogin） | 签名统一 `(id, task, el)`；收尾统一 `audit → saveDB → render` |
| ③ 渲染管线 | 2387–2413 | `viewHtml()` 路由 → `render()` → `shell()` → 视图函数 → `applyLang()` | 唯一出口；视图是纯函数，只返回字符串 |
| ④ 领域逻辑 | 714–835 / 1872–1981 / 2696–2736 | 权限三件套、体检三规则、呼叫队列与保存、分配、审计 | 不碰 DOM，只读写 DB |
| ⑤ 数据层 | 584–713 | `buildSeed()` 造数、`loadDB()` 每日重建、`saveDB()`、`DB` 11 张表、`state` 30 字段 | DB 持久化、state 不持久化 |
| ⑥ 表现层 | 1–417 | CSS 变量与 4 套主题、`--fs` 字号、i18n 词条与规则、332 条样式规则 | 主题只改变量，不改结构 |

---

## 3. 数据流：一次点击走完的链路

以「呼叫台保存并下一位」为例：

```
click [data-act=call-save]
  → A['call-save'](id, task, el)              // 2455+ 动作表
  → saveCall()                                // 2696
      callQueue()[0]                          // 1873 派生队列
      DB.notes.push(note)                     // 写记事
      task.status = 'completed'               // 完成回访
      结果=号码无效 → c.invalid = true，取消待办
      结果=未接/占线 → 未到上限则建周期任务
      state.callDone.add(c.id)                // 本次已处理
  → audit('呼叫台登记', …)                     // 844
  → saveDB()                                  // 写 localStorage
  → render()                                  // 2404 全量重建
      shell(viewHtml())                       // 外壳 + 当前页
      applyLang()                             // 英文模式整页替换
  → callView() 自动取下一位
```

**回环**：`saveDB → render` 是全站唯一的状态回流路径。任何动作只要漏掉 `render()`，界面就不会变；
漏掉 `saveDB()`，刷新就丢。这条约定让「可复现」成为默认属性——任何页面都能从 DB 直接重建。

**唯一例外**：表格勾选走局部更新（`tr.classList.toggle` + 重绘底部批量条），
因为全量重渲染会导致复选框闪烁、滚动跳位、连点丢选。

---

## 4. 数据模型（11 张表 + meta）

| 表 | 字段 | 关系 / 约束 |
|---|---|---|
| `users` | id, username, name, role, managerId, active, pwd, extra[], mustChange | `managerId → users.id`（自引用，构成汇报树） |
| `roles` | role → 权限点数组 | 3 条；admin 由 `PERMS.map` 生成 |
| `teams` | id, name, supervisorId | `supervisorId → users.id`；组员 = `users.managerId === supervisorId` |
| `customers` | id, name, phone, company, source, category, status, ownerId, remark, dnc, invalid, invalidReason, mergedInto, lastContactAt, archived, version, createdAt | `ownerId → users.id`；`mergedInto → customers.id`（合并后隐藏）；`phone` 应唯一（标准化后） |
| `notes` | id, custId, at, result, content, userId, voided | `custId → customers.id`，`userId → users.id` |
| `tasks` | id, custId, title, assigneeId, scheduledAt, originalScheduledAt, status, remindBefore, rescheduleCount, completedAt/By, completionNoteId, cancelReason, version | 双人指针：`custId` 客户 + `assigneeId` 执行人 |
| `notifications` | id, userId, taskId, title, body, createdAt, status | `status: unread / read / expired` |
| `audit` | id, at, userId, action, detail | 保留最近 300 条 |
| `logins` | id, userId, username, ok, at, ip, device, note | `userId` 可为空（登录失败时只有 username） |
| `reveals` | id, userId, custId, at | 查看完整号码流水，`revealQuota()` 按当日计数 |
| `settings` | cycleDays, cycleMax, maskPhone, exportLimit, revealDailyLimit, theme, fs, lang | 单行配置，主题/字号/语言也存这里 |
| `meta` | seedDay, seq{customer, note, task, notif, audit, user, login, team} | `seedDay ≠ 今天` 触发整库重建 |

**造数策略**：`dAt(offset, h, m)` 生成相对今天的日期，`buildSeed()` 里所有时间都是偏移量。
这保证「今天永远有到期/逾期数据」，评审时不会看到一片空白。代价是每天首次打开会重置演示数据。

**字段设计的三处讲究**：

1. `originalScheduledAt` 与 `scheduledAt` 分开存 → 改期次数与「原本该什么时候打」可追溯。
2. `mergedInto` 而非删除 → 合并可回溯，且不破坏 notes/tasks 的外键。
3. `version` 字段预留给乐观锁，原型未使用（真实系统必做）。

---

## 5. 权限模型（三层叠加）

```
can(p)              = admin ? true : (user.extra 包含 p) || (roles[user.role] 包含 p)
scopeIds()          = admin ? 所有人 : supervisor ? [自己 + 直属下属] : [自己]
canSeeCustomer(c)   = can('customer.view') && scopeIds().includes(c.ownerId) && !c.mergedInto
```

| 层 | 可改？ | 作用 |
|---|---|---|
| 权限点（18 个） | 界面可勾选，即时生效 | 决定「能不能做某个动作」 |
| 数据范围（3 档） | 按角色写死 | 决定「能看到谁的数据」 |
| 个人额外授权 `user.extra` | 界面可勾选 | 临时加权限，授权/撤销都进审计 |

**为什么分开**：如果数据范围跟着权限点走，就会出现「给了查看权限 → 看到全公司客户」的越权。
两者分离后，权限点只决定动作，范围只决定行，越权面收敛到「同一个人的客户」。

`can()` 被 15 个函数调用（扇入第 4），`scopeIds()` 被 8 个函数调用 —— 说明它是真的在取数层生效，
而不是只挂在按钮显隐上。

---

## 6. 视图索引（12 个）

| view | 函数 | 行号 | 行数 | 主要依赖 |
|---|---|---|---|---|
| `dashboard` | `dashboardView` | 1216–1296 | 81 | kpiCard, taskState, cycleLists, dupGroups, invalidList |
| `customers` | `customersView` | 1320–1384 | 65 | filteredCustomers, maskPhone, nextCallback, attemptsOf |
| `customer` | `customerView` | 1395–1470 | 76 | custNotes, attemptsOf, nextCallback, custBadge |
| `datahealth` | `datahealthView` | 1473–1553 | 81 | dupGroups, invalidList, cycleLists |
| `calendar` | `calendarView` | 1556–1599 | 44 | visibleTasks, taskState, ymd/addDays |
| `notes` | `notesView` | 1602–1625 | 24 | visibleNotes, scopeIds |
| `board` | `boardView` | 1628–1697 | 70 | scopeIds, visibleCustomers/Notes/Tasks, kpiCard |
| `users` | `usersView` | 1700–1753 | 54 | teamOfUser, teamName, getUser |
| `perms` | `permsView` | 1756–1838 | 83 | PERMS, DB.roles, DB.teams, assignOptions |
| `settings` | `settingsView` | 1841–1870 | 30 | DB.settings, DB.audit |
| `call` | `callView` | 1889–1981 | 93 | callQueue, custNotes, attemptsOf, nextCallback |
| `logs` | `logsView` | 1984–2025 | 42 | scopeIds, DB.logins, DB.audit |

外加两个覆盖层函数：`modalHtml`（2105–2384，280 行，18 种弹窗）、`drawerHtml`（2028–2102，75 行，4 种抽屉）。

---

## 7. 动作索引（59 个，按用途分组）

| 分组 | 数量 | 动作 |
|---|---|---|
| 会话与演示 | 4 | login, fill-login, logout, reset |
| 导航与覆盖层 | 8 | nav, page, open-customer, open-task, open-day, open-agent, close-drawer, close-modal |
| 客户资产保护 | 1 | reveal |
| 客户与流转 | 9 | new-customer, edit-customer, transfer, bulk-assign, bulk-invalid, toggle-invalid, toggle-dnc, sel-all, clear-sel |
| 记事与回访 | 4 | new-note, new-task, reschedule, cancel-task |
| 导入导出 | 2 | import, export |
| 客户体检 | 4 | dh-tab, merge, cycle-create, cycle-create-all |
| 通知 | 3 | toggle-notif, open-notif, read-all |
| 日历 | 4 | cal-prev, cal-next, cal-today, cal-mode |
| 外观 | 4 | toggle-prefs, set-theme, set-fs, set-lang |
| 呼叫台 | 5 | call-result, call-skip, call-reset, call-save, call-dnc |
| 账号与密码 | 6 | new-user, edit-user, toggle-user, reset-pwd, change-pwd, set-pwd |
| 小组与分配 | 3 | assign-plan, team-edit, new-team |
| 系统 | 2 | backup, log-tab |

## 8. 表单索引（18 种 `data-form`）

`login` · `note` · `task` · `customer` · `reschedule` · `cancel-task` · `transfer` · `bulk-assign` ·
`merge` · `import` · `export` · `user` · `edit-user` · `change-pwd` · `set-pwd` · `assign-plan` · `team` · `move-member`

统一模式：**校验失败 → `toast(...,'warn'|'err')` 并 return；成功 → 改数据 → `audit` → `saveDB` → `render` → `toast` 成功**。
`import` / `export` / `merge` 三个分支额外带预览与二次确认。

---

## 9. 领域函数（业务规则所在）

| 模块 | 函数 | 行号 | 规则 |
|---|---|---|---|
| 权限 | `can` / `scopeIds` / `canSeeCustomer` | 729–749 | 见第 5 节 |
| 体检 | `dupGroups` | 798–816 | 标准化手机号相同，或姓名+公司相同 → 分组 |
| 体检 | `invalidList` | 817–819 | 人工标记或格式不符 `1[3-9]\d{9}` |
| 体检 | `cycleLists` | 820–834 | 最近未接/占线且无待办：未接 < cycleMax 待重呼，≥ 待回收 |
| 呼叫 | `callQueue` | 1873–1888 | 待办回访 → 待联系 → 其他在跟客户；排除已成交/无意向/禁呼/无效；减去本次跳过与已处理 |
| 呼叫 | `saveCall` | 2696–2736 | 五件事：写记事、完成回访、标无效停呼、自动排下次、审计跳转 |
| 分配 | `assignTargets` / `assignOptions` | 751–766 | 主管只到直属下属；员工排前，默认第一个下属 |
| 审计 | `audit` / `logLogin` / `revealQuota` | 844 / 2420 / 767 | 写流水；号码查看按当日限次 |
| 资产 | `maskPhone` / `normPhone` / `isMobile` | 451–453（`esc` 在 448） | 脱敏、标准化（去非数字 + 去 86）、手机号校验 |

**扇入最高的 6 个函数**：`esc`(20) · `ts`(16) · `now`(15) · `can`(15) · `getUser`(14) · `visibleCustomers`(9)。
除了 `esc` 是安全函数，其余全是「取数 + 权限过滤」——说明这个原型的数据访问确实收敛在少数几个入口。

---

## 10. 表现层机制

| 维度 | 机制 | 要点 |
|---|---|---|
| 主题 | `html[data-theme="dark\|light\|contrast\|eye"]` → 4 组 CSS 变量 | 老代码里写死的颜色用**追加覆写块**修正（346–407），不逐个改变量 |
| 字号 | `html[data-fs="sm\|md\|lg\|xl"]` → `--fs` 系数 0.92/1/1.12/1.26 | 所有字号写 `calc(Npx * var(--fs))`，300+ 处 |
| 语言 | `EN` 字典 451 条 + `EN_RULES` 43 条正则 → `applyLang()` 遍历文本节点 | 只翻界面不翻数据；`placeholder` / `title` 属性单独遍历 |
| 持久化 | 三个设置项也存在 `DB.settings` | 换主题后刷新仍是该主题 |

---

## 11. 代码度量

| 指标 | 值 |
|---|---|
| 总行数 | 3,195（HTML+CSS 417 / JS 2,777） |
| 函数数 | 91（平均 19.3 行，中位数约 12 行） |
| 最大函数 | `modalHtml` 280 行（18 种弹窗） |
| 次大 | `buildSeed` 102 · `callView` 93 · `permsView` 83 |
| CSS | 408 行 / 332 条规则 |
| 注释 | 28 个分区标题，无行内注释堆砌 |
| 外部依赖 | 0（无 CDN、无字体、无网络请求） |
| 回归覆盖 | 51 条断言 / 0 页面异常 |

**复杂度分布是健康的**：超过 80 行的三个函数都是纯字符串拼接的视图/弹窗，
真正的业务分支被拆成 15–40 行的小函数（`dupGroups` 19、`cycleLists` 15、`callQueue` 16、`saveCall` 41）。

---

## 12. 扩展手册

**加一个页面**（3 步）
1. 写 `xxxView()`，返回 HTML 字符串（只读 `DB` 与 `state`）。
2. `viewHtml()` 加一行 `case 'xxx': return xxxView();`。
3. `navItems()` 加一项 `{ id:'xxx', label:'…', ic:'…' }`，需要权限就在前面加 `if (can('…'))`。

**加一个权限点**（2 步）
1. `PERMS` 加 `{ id:'xxx.yyy', g:'分组', n:'名称', d:'说明' }`。
2. 在 `DB.roles.supervisor/agent` 里决定默认给谁；视图里用 `can('xxx.yyy')` 守卫。

**加一种语言**
复制 `EN` 为 `JA`，`applyLang()` 里按 `DB.settings.lang` 选字典即可 —— 因为是渲染后替换，不需要改模板。

**加一张表**
`buildSeed()` 里加数组、`loadDB()` 的校验条件加上该数组、`meta.seq` 加一个自增键。

**加一个动作**
`A` 表加方法（签名 `(id, task, el)`），元素上写 `data-act="…"`，收尾记得 `saveDB(); render();`。

---

## 13. 已知债务与风险

| # | 问题 | 位置 | 严重度 | 建议 |
|---|---|---|---|---|
| 1 | `A.login()` 是空实现（占位） | 2456 | 低 | 删掉，或注释说明为何保留 |
| 2 | 6 处 `prompt()` 输入原因（标记无效/禁呼/解除） | 2528–2660 | 中 | 换成统一弹窗，`prompt` 在无头/移动端体验差且会阻塞 |
| 3 | `modalHtml` 280 行单体函数 | 2105–2384 | 中 | 拆成 `modals/` 映射表：`MODALS[type](m)` |
| 4 | i18n 靠渲染后替换，漏词条就残留中文，且**没有自动化检测** | 1059–1083 | 中 | 把「英文模式残留中文」做成一条回归断言（本轮靠一次性脚本核对） |
| 5 | 全量重渲染，输入框靠 state 回填 | render 2404 | 中 | 演示够用；搜索框已加 260ms 防抖规避光标跳位 |
| 6 | 没有 URL 路由，刷新回工作台 | boot 3183 | 低 | 加 `location.hash` 同步 `state.view`，方便评审分享深链 |
| 7 | 号码查看限次存在浏览器里 | `reveals` | 高（业务） | 真实系统必须服务端计数 + 按 IP/账号限速 |
| 8 | 权限只在前端生效 | `can()` | 高（业务） | 后端每个查询强制拼 `scopeIds`，否则改个变量就绕过 |
| 9 | 密码明文存在 `DB.users.pwd` | 584 | 高（业务） | bcrypt + 服务端会话；强制改密也要服务端拦 |
| 10 | 单文件 228 KB 接近维护上限 | 全局 | 低 | 再加功能建议拆 data / views / app 三个文件 |

> 7–9 三条不是「原型的 bug」，而是原型刻意保留的模拟边界，已在 README「明确模拟」表中标注；
> 这里列出是为了在交接给后端时不被当成已实现。

---

## 14. 与 Go 后端的映射（摘要）

| 原型 | 后端 |
|---|---|
| `can` / `scopeIds` / `canSeeCustomer` | `internal/access`：权限点常量 + 角色表 + 数据范围中间件 |
| `DB.users` / `sessions` / `mustChange` | `internal/auth` + `users` 表 + `must_change_password` |
| `DB.teams` | `teams` 表（或直接复用 `manager_id` 层级） |
| `DB.customers` | `customers` 表（`phone_normalized` 唯一索引） |
| `dupGroups` / `invalidList` / `cycleLists` | `internal/customers` 体检服务 + 定时任务 |
| `callQueue` / `saveCall` | `internal/notes` + `callbacks` + 周期任务生成 |
| `audit` / `logLogin` / `reveals` | `audit_logs` / `login_logs` / `reveal_logs` |
| `buildSeed` / `loadDB` / `saveDB` | SQLite（WAL + foreign_keys + busy_timeout）+ 迁移脚本 |

---

## 15. 一句话评价

**作为 MVP 原型它是合格的**：业务规则（权限分层、资产保护、分配语义、呼叫闭环）都落到了可执行的代码里，
而且有 51 条自动断言兜底，改坏了能立刻发现。

**作为产品代码它不合格**：没有后端、没有并发控制、密码明文、权限只在前端。
它的正确用法是「拿它跟业务方确认规则」，确认完就按第 14 节的映射重写成 Go + SQLite，而不是在它上面继续加功能。
