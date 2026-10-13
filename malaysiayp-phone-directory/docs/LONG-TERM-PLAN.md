# malaysiayp 全量采集 · 长期运行计划

> 版本 v1.0 · 2026-10-08 15:15
> 适用脚本 `scrape_malaysiayp.py` v3.0.0（指纹 `18fdf3ef9ae54dc8`）
> 配套：`supervise.py` v1.1.0 / `defer_defects.py` / `prioritize.py` / `export_deliverable.py`

---

## 一、目标定义（先把"完成"说清楚）

| 维度 | 可验证的判据 | 当前是否达成 |
|---|---|---|
| **采集全面** | `pages['done'] == expected` 且 `category_page_gaps == 0` 且 `header_total_mismatches == 0` | ❌ 281 / ≈6313（4.5%） |
| **内容正确** | 四者对账零差额 + 号码 100% 过正则 + 抽样复核一致率 ≥ 95% | ✅ 当前零差额 |
| **目标质量** | 每份交付物带 `README.md` + `meta.json`（行数/字节/SHA256/覆盖度） | ✅ 已建立 |
| **避免封禁** | 封禁指纹 = 0，且健康率 ≥ 85% | ✅ 指纹 0 / ⚠️ 健康率待测 |

**必须提前接受的事实**：因源站存在**永久性坏缓存页**（详见 `SITE-STRUCTURE-AUDIT.md`），
`rc=0`（EXIT_OK）**不可达**。任务的正常终点是 **`rc=6`（EXIT_INSUFFICIENT）**，
交付形态固定为：

> **全量 CSV 分片 + 成品交付 CSV + 残余缺口清单（GAP-REPORT）**

---

## 二、现状基线（2026-10-08 15:12）

| 指标 | 值 |
|---|---:|
| 已完成页 / 已入队页 | 281 / 2379（11.81%） |
| 分类总数 | 1243 |
| 已索引分类 / 未索引分类 | 58 / **1185** |
| 已索引分类展开的页数 | 1192 |
| 估计真实总页数 | 2377 – 11430（中值 **6313**） |
| **估计真实覆盖率** | **≈ 4.5%** |
| 入库实体 / 手机号 / 隔离 | 4770 / 890 / 84 |
| 报错页（其中 0 字节） | 412 / 403 |
| CSV 分片 | 43 |
| 自适应 `--delay` | 3.0 s |

**结构性结论**：58 个已索引分类的页数分布是 `1页×34, 2页×9, 3页×2, 4页×3, 5页×2, 6~83页×6, 275页×1, 675页×1`。
即**约 60% 的分类只有 1 页**，页数由少数巨型分类主导。因此总页数对外推方法极敏感 —— 唯一可靠的办法是**把 1185 个分类全部索引一遍**。

---

## 三、四种响应形态（决定全部策略的前提）

实测（`probe_recover.py` / 手工 curl 对照）确认，站点对"坏"响应有**四种**形态，处置方式完全不同：

| 形态 | 特征 | 恢复时间 | 判定手段 | 处置 |
|---|---|---|---|---|
| **正常** | 36.5–43.0 KB，含 `</html>` | — | — | 入库 |
| **A 型：短时限流** | `HTTP 200` + **0 字节**，`Content-Length` 缺失 | **分钟级**（实测 < 4 min 自愈） | 静默后重测**会恢复** | **降速重试**，不可延期 |
| **B 型：坏缓存** | `Content-Length: 32768`（=2¹⁵）截断，或持续 0 字节，`X-Nextjs-Cache: HIT` | ≥ 24 h（`s-maxage=86400`） | 静默后重测**仍坏** | **延期 25 h** 后复检 |
| **C 型：不存在** | `301` / `404` | 永久 | 状态码 | 标记 `gone`，从队列摘除 |

**证据链**：
- `automotive` 首次 42990 B → 密集请求后 0 B → **静默 4 分钟后恢复 42990 B** ⇒ A 型存在
- `agricultural/page/6` 静默 4 分钟后仍 0 B；`page/3` 稳定 32768 B，`Etag` 不变 ⇒ B 型存在
- 绕过尝试全部失效：`?cb=<rand>`、`Cache-Control: no-cache`、`no-store`、`Pragma`、`Accept-Encoding: identity/gzip/br`、`RSC: 1`、无尾斜杠、双斜杠、URL 编码 —— **字节数一律不变** ⇒ 缓存键不含 query，客户端无法绕过
- **限流阈值已实测**：3s（20 请求/分钟）与 8s（7.5 请求/分钟）间隔请求同一批 URL，**响应字节数完全一致**（`architectural-services` 两轮都是 26814 B）⇒ **20 请求/分钟安全**；触发限流需 ~280 请求/分钟（探测循环漏 `sleep` 那次）

**⚠️ 必须避免的误判**：「页面短」≠「页面坏」。`art-schools` 19533 B 但含 `</html>`，
**只有 1 条记录**，完全正常；`auditing` 33338 B 有 13 条记录，也正常。
正确判据只有 **`< 3000 字节` 或 缺 `</html>`**（脚本 `fetch()` 已实现）。

> **这条推翻了旧策略**：`defer_defects.py` 把 337 页一律延期 6 小时，其中相当比例实为 A 型限流误判。
> 新策略必须先区分 A/B，再分别处置。

---

## 四、分阶段路线图

### 阶段 1 · 分类索引（当前优先，预计 3–8 小时）

**为什么最先做**：1185 个未索引分类的首页是**信息密度最高**的页 —— 每页同时产出
① ~20 条新记录 ② 该分类的真实页数。索引完成后：
- `categories.pages` 全部落地 ⇒ **总量从"估计"变成"事实"**
- 预计新增 **≈ 23,700 条记录**（1185 × 20）

**动作**：
```bash
python prioritize.py --apply     # 把 1185 个首页提到队首
python supervise.py --once       # 驱动采集
```

**完成判据**：`categories.index_state='done'` 的数量 = 1243。

### 阶段 2 · 全页抓取（预计 2–5 天）

按 `not_before, category, number` 顺序推平剩余队列。
**关键调优**：把速率压到**不触发 A 型限流**的安全区（阈值待实测，见第七节）。

### 阶段 3 · 缺口收敛（预计 1–2 天）

- B 型页满 25 h 后批量复检，成功的回填
- 连续 3 轮复检仍失败的页 → 记入 `GAP-REPORT` 终态清单，不再消耗预算
- C 型页直接摘除

### 阶段 4 · 交付（随时可出，终版在阶段 3 后）

```bash
python export_deliverable.py
```
产出 `data/deliverable/` 下 4 个 CSV + `README.md` + `meta.json`。

---

## 四·补 跳过 62 个缺陷首页决策（2026-10-12，已执行）

**背景**：62 个未索引分类首页被 B 型坏缓存（Content-Length: 32768 截断 / 持续 0 字节，Etag 恒定，
绕过手段全失效，恢复 ≥ s-maxage=86400）锁死，自 Oct 9 起每轮被 `prioritize.py` 强制拉回队首、
每 20 分钟重试一次，永坐不满 25h 复检窗，导致「索引停滞」（已索引分类卡在 1181）。

**只读核查结论**：这 62 个分类在 `pages` 表中**仅有 number=1 首页、全部带 error、无任何子页**
（子页须在首页成功读取页数后才入队，故从未入队）。跳过后这 62 分类数据不可回收，接受为永久缺口。

**处置（用户 2026-10-12 指令「跳过缺陷首页」）**：
1. 备份 `prioritize.py` → `prioritize.py.bak-skipdefect-20261012`。
2. 编辑 `prioritize.py` 队首查询，加 `AND error=''`：
   已带 error 的首页不再每轮强制置顶；改由 `defer_defects.py` 按 attempts 阶梯
   （+30min / +6h / +25h）延期复检。若缓存恢复、抓取成功 → `index_state` 变 `done` → 自然退出。
3. 这是硬约束内唯一合规写法：只动 `pages.not_before`（经 prioritize 写入），不改 `categories` /
   `status` / `attempts`。
4. 验证：编辑后 `prioritize --apply` 队首 0 页；62 首页 `not_before` 全部落到未来（最近 15:38 回可抓取），0 个在队首。

**回滚**：`cp prioritize.py.bak-skipdefect-20261012 prioritize.py` 即恢复原行为（重新每轮拉首页）。

**副作用**：阶段 1 完成判据 `categories.index_state='done'=1243` 不再可达；实际天花板 =
**1181 已索引 + 62 跳过 = 1243（含 62 永久缺口）**。终态仍走 `rc=6` + `GAP-REPORT`，
其中 62 首页 + 其所属深层页（若有）记入缺口清单，原因标注「B 型坏缓存（首页跳过）」。

## 五、四个目标维度的落地机制

### ① 采集全面

| 机制 | 位置 | 作用 |
|---|---|---|
| 三源对账 `_full_coverage()` | `scrape_malaysiayp.py` | 首页声明 / 分类表 / 实际页数三者互证 |
| 分类索引优先 | `prioritize.py` | 先展开 1185 个未索引分类，消除"总量未知" |
| 缺口报告 | `supervise.py::write_gap_report()` | 落盘 `logs/GAP-REPORT-*.json`，列明每个未采页及原因 |
| 分片提交 | `_full_commit_part()` | 每片 SHA256 + schema 落库，可校验可续传 |

### ② 内容正确

**五道校验（全部在脚本内，`--self-test` 97 项覆盖）**：

1. 号码正则：`_FULL_PHONE_ALL = 0\d{7,10} | 1[38]00\d{6,8}`，不合格 → `phone_status='invalid'` 入隔离区
2. 唯一约束：DB 层 `UNIQUE(detail_url, phone)`，同公司多号码保留多行，重复零容忍
3. 同源校验：`detail_url` 必含 `/item/`、`source_page` 必含 `/cat/` 且同域
4. CSV 行校验：`_full_check_row()` 在 `csv_input=True` 时拒绝未加保护的公式字段
5. **公式注入防护**：`= + - @` 开头一律加前导撇号（导出器已复刻同一逻辑）

**四者对账（每次导出后核）**：
```
entries 表行数  ==  exported 行数  ==  分片账本行数  ==  磁盘 CSV 行数
```
当前：`4770 == 4770 == 4770 == 4770` ✅

**抽样复核**：失败记录 20/20 一致；成功记录 14/15 一致（1 例为站点后续改号，非采集错误）。

### ③ 目标质量

| 交付物 | 必备元数据 |
|---|---|
| `malaysiayp_all.csv` | 行数 / 字节数 / SHA256 |
| `malaysiayp_mobile.csv` | 同上 |
| `malaysiayp_all_extended.csv` | 同上，含 `raw_phone` / `phone_status` / `entry_id` |
| `malaysiayp_quarantine.csv` | 同上，84 行待排查 |
| `README.md` | 列定义、覆盖度、合规声明、更新方式 |
| `meta.json` | 覆盖度三档估计、来源 DB 时间戳、脚本版本 |

**编码规范**：UTF-8 **带 BOM** + CRLF —— Excel 双击不乱码、中文正常。

### ④ 避免封禁

| 层 | 机制 | 参数 |
|---|---|---|
| 合规 | 启动即校验 `robots.txt`，通用 UA 组 `Allow: /`（仅禁 `/api/`、`/*?s=`） | 实时 |
| 速率 | 自适应 `--delay`，**由健康率驱动**（非成功率） | 3.0 – 120 s |
| 突发 | 片间冷却 | 60 – 3600 s |
| 指纹 | 每页延迟加随机抖动 | 0 – jitter s |
| 监测 | 封禁指纹检测（403 / 429 / 验证页 / 连接重置 / 连续 0 字节） | 每片 |
| 退避 | `wait = max(min(3600, 30·2^min(attempts-1,7)), retry_after)` | 连续 3 次失败触发 |

**健康率定义**（关键修正）：
```
健康率 = 1 − (硬错误 + 0.5 × 截断) / 尝试数
```
**0 字节的 A/B 型页不计入分母** —— 否则会把"站点缺陷"误读成"我们太快了"，导致无意义降速。

---

## 六、运行机制（四层冗余 + 自愈）

```
第 1 层  Windows 计划任务  MalaysiaYP-FullCrawl     每 20 分钟，切片 15 分钟
第 2 层  后台守护          supervise.py --daemon    常驻，自适应调速 + 延期感知长睡
第 3 层  启动文件夹         start_supervisor.vbs     开机自启
第 4 层  WorkBuddy 自动化   每小时一次               跨会话监督 + 缺陷复检
```

**自愈点**：
- `pythonw.exe` 下 `sys.stdout is None` → `_ensure_stdio()` 兜底
- 切片超时撞 `MultipleInstances=IgnoreNew` → 切片 15 min < 触发间隔 20 min
- 队列里只剩延期页 → 守护长睡到 `min(not_before)`，不做无效请求
- 命中 `rc=6` → 落 `EXHAUSTED.json` + `GAP-REPORT`，6 小时后自动复检

---

## 七、未决问题与预案

| # | 问题 | 影响 | 预案 |
|---|---|---|---|
| 1 | ~~A 型限流阈值未知~~ **已实测关闭** | — | **20 请求/分钟安全**（3s 与 8s 间隔响应字节完全一致）；触发限流需 ~280 请求/分钟。`--delay 3.0` 保持不变 |
| 2 | B 型缺陷在扩散（14:19 260 页 → 15:12 412 页） | 覆盖率天花板下降 | 25 h 后批量复检；若复检恢复率 < 30%，说明源站在持续劣化，需下调目标 |
| 3 | B 型缓存 `stale-while-revalidate` 长达 1 年 | "24 h 后自愈"不保证 | 以复检实测为准，不假设自愈 |
| 4 | 未索引分类页数未知 | 总量估计区间宽（2377–11430） | 阶段 1 完成后消除 |
| 5 | 计划任务身份 `Interactive / Limited`（非管理员） | 需用户登录态 | 已由启动文件夹 + WorkBuddy 自动化兜底 |
| 6 | 磁盘 / DB 损坏 | 全量重来 | WAL 模式 + 每片 SHA256 + `data/*.bak` 快照 |
| 7 | 站点改版 | 解析全失效 | 结构指纹（`row-item` / `/page/N/` / 分页器）每次运行校验，异常即 `EXIT_STRUCTURE` |

---

## 八、验收清单（终版交付前逐项打勾）

- [ ] `categories.index_state='done'` = 1243（全部分类已索引）— 注：2026-10-12 起 62 个 B 型缺陷首页按决策「跳过」，实际天花板 = 1181 已索引 + 62 跳过；验收以 `rc=6` + GAP-REPORT 含 62 缺口为准
- [ ] `category_page_gaps` = 0
- [ ] `header_total_mismatches` = 0
- [ ] 四者对账零差额
- [ ] 号码正则通过率 100%（不合格全部入 `quarantine`）
- [ ] 抽样复核一致率 ≥ 95%
- [ ] 所有分片 SHA256 校验通过
- [ ] `GAP-REPORT` 中每个残余页都有明确原因（B 型 / C 型）
- [ ] 交付目录含 4 CSV + `README.md` + `meta.json`
- [ ] `meta.json` 中 `estimated_true_pct` 已用**实测总页数**替换估计值

---

## 九、日常运维命令

```bash
cd "C:/Users/Admin/WorkBuddy AI/2026-10-07-16-32-42/phone-directory"

python supervise.py --status              # 看进度、缺陷分布、ETA
python supervise.py --once --budget-minutes 15   # 手动跑一片
python supervise.py --probe               # 只读探针，不抓取
python prioritize.py                      # 干跑：看优先级重排计划
python prioritize.py --apply              # 执行重排
python prioritize.py --rollback           # 回滚
python defer_defects.py                   # 干跑：看缺陷页延期计划
python defer_defects.py --apply           # 执行延期
python defer_defects.py --rollback        # 回滚
python probe_recover.py --n 30 --gap 10   # 抽样复测：A 型 vs B 型
python export_deliverable.py              # 产出交付 CSV
python scrape_malaysiayp.py --self-test   # 97 项自检
```

---

## 十、合规声明（写入每份交付物）

数据来源为公开商业目录。记录含**个人数据**（公司名 + 手机号），受马来西亚
**PDPA 2010（2024 修订）** 约束。仅限目录检索 / 研究用途；
**禁止群发、推销、骚扰、转售**。采集遵守站点 `robots.txt`。
