# 运维手册 — malaysiayp 采集脚本

> 目标：**脱离 LLM 也能长期运行、排错、维护**。
> 本手册覆盖：怎么跑、怎么判断成败、出错怎么办、站点改版怎么办。
>
> 最后更新：2026-10-08

---

## v3.0.0 分段全量模式（2026-10-08，优先于下文旧抽样教程）

- 无 `--n/--preset` 时默认全量，已取消默认100条/30页/每类10条的截断；显式 `--n` 仍选择旧抽样模式。
- 推荐：`run.cmd --all --chunk-pages 25 --chunk-pause 30 --max-minutes 120`。到预算返回9；重复同一命令自动续跑，不需要 `--append` 或 `--resume`。
- `run.cmd --all --max-chunks 1`：本次只处理一段，逐页事务提交，段尾输出CSV分片。
- 默认导出01X手机号；`--phone-scope all --out data/directory_all.csv` 导出全部列表记录（含座机与无电话）。SQLite始终保留列表原始记录。
- 全量使用独立 `<out>.sqlite3` 任务/记录账本、`<out>.job.json` 状态报告和CSV分片目录；不复用旧 `cache/state.json` 或旧CSV，不覆盖现有 `malaysiayp_100.csv`。
- `run.cmd --full-verify --out data/malaysiayp_full.csv` 检查数据库完整性、页缺口、CSV分片哈希及最终汇总；不要用旧 `--coverage` 来验收新全量作业。
- 全量业务键是“详情URL + 电话”，不是只按电话去重。不同企业共用号码不会被误删。Unicode中文合法；公式样式文本会转义。
- 分段上限只是负载控制，不代表全站已完成。只有任务范围全部页面成功并验收后返回0；失败页耗尽次数返回6；遇封禁/验证页立即4；结构变更5；环境/磁盘/数据库错误3；互斥锁8；中断130。
- 该站是Next.js服务端渲染目录，普通HTTP可读取列表；无浏览器、无LLM、无第三方Python依赖。
- 全量指“分类列表可见记录”，不包含下载图片、详情页所有字段、登录/API数据。网站动态变化，不能承诺永久无错误；先运行自检，再小段启动并查看状态。
- `--manual` 开头提供最新全量说明。下文旧输出路径、按手机号去重及默认100条的说明只适用于显式抽样模式。

---

## 一、文件地图

| 文件 | 作用 | 需要改吗 |
|---|---|---|
| `scrape_malaysiayp.py` | 主脚本（抓取 / 自检 / 校验 / 覆盖率 / 内置手册 五合一） | 站点改版时才改 |
| `supervise.py` | **自适应守护 + 监督报告**：按每片健康率自动调 `--delay`/冷却，输出 `logs/status.json` | 调速策略不合适时才改 |
| `defer_defects.py` | **缺陷页可逆剔除**：把「已到期且仍失败」的页 `not_before` 推后 6 小时；`--apply` / `--rollback` | 一般不用改 |
| `SITE-STRUCTURE-AUDIT.md` | **站点结构审核报告**：技术栈、缺陷形态、五种假设的证伪证据 | 只读参考 |
| `SCHEDULED-TASK-VERIFICATION.md` | 计划任务验证报告：配置、5 个缺陷与修法、证据 | 只读参考 |
| `ERROR-AUDIT.md` | 错误情况审计：无法收集 / 限流 / 污染 / 脚本质量四维结论 | 只读参考 |
| `supervisor.cmd` | 简单守护循环（批处理版，无自适应；保留作为最小依赖兜底） | 一般不用改 |
| `task_slice.cmd` | **计划任务切片入口**（跑 `supervise.py --once` 一片就退出，带日志重定向） | 一般不用改 |
| `scheduled_crawl.cmd` | 备用的裸采集切片入口（直接调 `run.cmd`，无自适应） | 一般不用改 |
| `start_supervisor.vbs` | 无窗口拉起 `supervise.py`（常驻守护）；副本放启动文件夹实现开机自启 | 路径变了才改 |
| `run_slice_hidden.vbs` | 无窗口运行一次切片的 VBS（备用；当前任务直接用 `pythonw.exe` 更简单） | 一般不用改 |
| `inject_samples.py` | **看板注入器**：把 CSV 样本幂等注入 `index.html`（零网络、零 LLM） | 改 `index.html` 结构时才改 |
| `run.cmd` | Windows 启动器（双击 / 计划任务） | 换 Python 时改 |
| `run.sh` | Linux/macOS 启动器（cron 可用） | 一般不用改 |
| `extract_malaysiayp.py` | 离线解析器（**不联网**，只读本地 HTML） | 不用改 |
| `cache/index.json` | 站点结构索引（分类 + 每类页数） | 自动生成 |
| `cache/manifest.json` | **抓取账本**：每个已抓页的记录（顺序检验的数据来源） | 自动生成 |
| `cache/html/*.html` | 页面缓存（按 `sha1(url)[:16]` 命名） | 自动生成 |
| `cache/state.json` | 断点（中断后 `--resume` 用） | 自动生成 |
| `cache/.lock` | 互斥锁（防计划任务重叠） | 自动生成 |
| `logs/run-*.log` | **每次运行的完整日志** | 自动生成，排错看这里 |
| `logs/scheduled.log` | 计划任务切片日志（仅当动作指向 `task_slice.cmd` 时才有） | 自动生成 |
| `logs/slice-stdio.log` | `pythonw.exe` 下的 stdout 落盘（`sys.stdout` 为 `None` 时的接管目标） | 自动生成 |
| `logs/supervise.log` | 守护循环日志（每片一行摘要） | 自动生成 |
| `logs/status.json` | 机器可读监督报告（供计划任务 / 看板 / 自动化消费） | 自动生成 |
| `logs/supervise-state.json` | 自适应状态（当前 `delay` / 冷却 / 历史 200 条） | 自动生成 |
| `logs/GAP-REPORT.json` | **`rc=6` 时的逐页缺口清单**（分类 / 页码 / 尝试次数 / 错误） | 自动生成 |
| `logs/GAP-REPORT.md` | 同上，人类可读版（含按分类汇总与处置建议） | 自动生成 |
| `logs/DEFECT-PAGES.json` | **缺陷页清单**（分类/页码/尝试次数/错误）—— 缺陷证据，勿删 | 自动生成 |
| `data/malaysiayp_full.defer-backup-*.json` | 延期前快照 —— **回滚依据**，勿删（保留最近 12 个） | 自动生成 |
| `logs/EXHAUSTED.json` | 耗尽标记；未过期时守护与切片都不再发起请求 | 自动生成 |
| `logs/STOP` | **手动急停开关**：创建这个空文件，守护在下一轮退出 | 手动创建 |
| `data/*.csv` | 产出数据 | — |
| `data/*.meta.json` | 产出的元信息（参数 / 条数 / 退出码 / **脚本指纹**） | 自动生成 |

> **脚本自带手册**：`--manual`（完整）、`--examples`（示例）、`--print-api`（函数接口速查）。
> 不用翻本文档也能查到用法。

---

## 二、怎么运行（都不需要 LLM）

### 方式 A：Windows 双击 / 命令行

```bat
run.cmd                              :: 默认抓 100 条
run.cmd --n 200 --seed 42            :: 抓 200 条
run.cmd --resume                     :: 接着上次中断处继续
run.cmd doctor                       :: 运行前环境自检
run.cmd verify data\malaysiayp_100.csv   :: 校验已有产出
run.cmd --check-robots               :: 只看 robots.txt
run.cmd --dry-run                    :: 只建索引，不抓条目页
```

`run.cmd` 会自动找 Python（顺序：`%MYP_PYTHON%` → 本机托管解释器 → PATH 上的 `python.exe`）。
找不到就报错并返回 **退出码 3**。

### 方式 B：Linux / macOS

```bash
./run.sh --n 100
./run.sh doctor
./run.sh verify data/malaysiayp_100.csv
```

### 方式 C：直接调 Python（最可控）

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"
"$PY" scrape_malaysiayp.py --n 100 --seed 20261007
```

### 常用参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `--n` | 100 | 目标手机号条数 |
| `--preset` | medium | 规模预设 `tiny`(20) / `small`(50) / `medium`(100) / `large`(500) |
| `--order` | random | `sequential` = 按分类顺序 + 页码升序（可校验完整性） |
| `--categories` | 全部 | 只抓指定分类，逗号分隔 |
| `--from-page` / `--to-page` | 1 / 末页 | 页码范围 |
| `--max-pages` | 30 | 最多抓多少页（**安全阀**） |
| `--per-cat` | 10 | 单分类上限，强制跨类型 |
| `--delay` | 2.0 | 请求间隔秒（**被限流就调大**） |
| `--jitter` | 0.5 | 间隔随机抖动上限，避免固定间隔被识别 |
| `--max-minutes` | 不限 | 时间预算，超时停止并保存断点 |
| `--seed` | 20261007 | 随机种子，同 seed 同结果 |
| `--out` | `data/malaysiayp_100.csv` | 输出路径 |
| `--force` | 关 | **已存在时允许覆盖（默认拒绝）** |
| `--append` | 关 | 增量追加到已有 CSV（按 phone 去重） |
| `--no-backup` | 关 | 覆盖前不备份 `.bak` |
| `--resume` | 关 | 断点续跑 |
| `--reindex` | 关 | 强制重建索引 |
| `--no-cache` | 关 | 忽略缓存全部重抓 |
| `--no-lock` | 关 | 不获取互斥锁 |
| `--allow-low-yield` | 关 | 条数不足也算成功（退出码 0） |
| `--skip-robots-check` | 关 | 跳过 robots 检查（**仅在已获授权时用**） |
| `-v` | 关 | 调试日志 |

### 六个只读模式

| 模式 | 用途 |
|---|---|
| `--doctor` | 环境自检（10 项），出问题先跑这个 |
| `--self-test` | **离线自检（96 项断言，零网络）** — 改过代码后先跑这个 |
| `--verify <csv>` | 校验产出质量（含号段分布 / 位数分布 / 分类集中度） |
| `--coverage` | 报告下载覆盖与缺口 |
| `--check-robots` | 只看 robots.txt |
| `--manual` / `--examples` / `--print-api` | 脚本内查手册 / 示例 / 接口 |

### `--self-test` 与 `--doctor` 的分工（重要）

| | `--doctor` | `--self-test` |
|---|---|---|
| 检查对象 | **环境**：Python / 目录可写 / 网络 / robots / 锁 / 缓存 | **代码语义**：解析、调度、配额、输出保护 |
| 需要联网 | 默认需要（可 `--skip-net`） | **不需要** |
| 能发现 | 环境坏了、被墙了、robots 变了 | 逻辑写错了、正则漏了号段、配额算错 |
| 发现不了 | 逻辑 bug | 环境问题 |

**教训**：本项目曾出现「`--per-cat` 被误实现成每页上限」和「正则漏抓全部 011 号码」两个 bug，
`--doctor` 与 `--verify` 都报「一切正常」——因为它们只看环境与数据格式，不看**语义**。
`--self-test` 就是为补这个盲区而加的：**任何改动 `ROW_RE` / `MOBILE_RE` / `iter_plan` /
`scrape` 之后，先跑 `--self-test`，通过再联网。**

---

## 三、退出码对照表 ⭐

**无人值守时只看退出码，不要解析 stdout。**

| 码 | 含义 | 该做什么 |
|---|---|---|
| **0** | 成功且达标 | 无 |
| **2** | 参数错误 | 检查 `--n/--max-pages/--per-cat/--retries/--from-page` 是否为正、`--delay/--jitter` 是否非负；`--force` 与 `--append` 不能同用 |
| **3** | 环境错误 | 跑 `run.cmd doctor`。常见：目录不可写 / 网络不通 / **robots.txt 不允许本 UA** |
| **4** | 被站点封禁 | **立即停手**。等几小时，把 `--delay` 调大到 5~10 再试 |
| **5** | 站点结构变更 | 站点改版了，**需要更新 `ROW_RE`**（见第七节） |
| **6** | 条数不足目标 / 校验不通过 | 数据已写出但不够数。调大 `--max-pages` 或调小 `--n`。**`--coverage` 有缺口、`--verify` 发现质量问题、`--verify --against` 发现旧号码丢失时也返回 6** |
| **7** | **输出文件已存在** | 防误覆盖。加 `--force` 覆盖（会自动备份）、或 `--append` 追加、或改 `--out` |
| **8** | **已有实例在运行** | 互斥锁生效。等它跑完；确认没有残留进程时可用 `--no-lock` |
| **130** | 被中断（Ctrl-C / kill） | 断点已保存，`run.cmd --resume` 续跑 |

在 Windows 计划任务里用 `%ERRORLEVEL%`，在 shell 里用 `$?` 读取。

---

## 三·B、顺序下载与完整性校验（避免「找不到资料」）

**问题**：随机抽样跑完，你不知道哪些页抓过、哪些没抓，无法判断资料是否齐全。

**解法**：`--order sequential` + `cache/manifest.json` + `--coverage`。

```bat
:: 按站点结构顺序抓（分类顺序 → 页码升序），确定性、可复现
run.cmd --order sequential --n 200 --max-pages 60 --out data\seq.csv

:: 看已抓了哪些页、有哪些缺口
run.cmd --coverage
```

`--coverage` 输出示例：

```
  分类                                     总页    已下载    覆盖  缺口
  hotels                                    110        3   2.73%  4-110(未抓)
  office                                    361        1   0.28%  2-361(未抓)
```

**要点**：
- 每次成功抓取都会记入 `cache/manifest.json`（URL / 分类 / 页码 / 字节数 / 解析条数 / sha1 / 时间）。
- 缺口 = 已抓页码区间内缺失的页 + 尚未抓到的页段。
- **有缺口时 `--coverage` 返回退出码 6**，可直接被监控捕获。
- 补齐缺口：再跑一次 `--order sequential`，已抓的页会被跳过（三层去重），只补没抓的。
- 想只看已抓过分类的明细，加 `-v`。

---

## 三·C、输出保护（防误写 / 误覆盖）

**默认拒绝覆盖已存在的 CSV。** 这是刻意的 —— 一次手滑不该毁掉几百条数据。

| 场景 | 行为 |
|---|---|
| 输出文件不存在 | 正常写入 |
| 输出文件已存在，未给 `--force` | **拒绝，退出码 7**，不写任何文件 |
| 输出文件已存在，给了 `--force` | 先备份为 `<名>.<时间戳>.bak`，再覆盖 |
| 新结果 < 已有行数 × 50% | **缩水守卫：拒绝**（防止一次失败运行覆盖掉好数据） |
| 给了 `--append` | 读旧文件 + 合并新记录，**按 phone 去重**，不丢旧数据；**合并前也自动备份** |
| `--force` + 缩水 | 仍执行，但日志里打警告 |
| 输出文件被 Excel 占用 | 降级写 `<名>_new.csv`，不抛异常 |

```bat
run.cmd --n 100 --out data\run1.csv            :: 第二次跑 → 退出码 7
run.cmd --n 100 --out data\run1.csv --force    :: 显式覆盖（自动备份）
run.cmd --n 100 --out data\run1.csv --append   :: 增量合并去重
```

### `--append` 的三条铁律（v2.2.0 加固）

`--append` 仍然是**整文件重写**（读旧 + 合并 + 原子写），所以有三个坑必须堵死：

| 铁律 | 为什么 | 违反的后果 |
|---|---|---|
| **① 读不到旧数据 → 中止，不当成「没有旧数据」** | `read_existing_rows(strict=True)` 一旦失败（Excel 独占 / 编码坏了 / 列名变了）直接抛错返回退出码 7 | 否则 `old=[]`，合并只剩新行 → **追加静默变成覆盖，旧数据全丢** |
| **② 列名与 schema 不符 → 中止** | 旧文件是别的 schema（如 `no,nama,telefon`）时盲目合并会写出半空的行 | 产出「看起来正常但字段是空的」CSV |
| **③ 新增 0 条 → 不写文件** | 抓到的号码全部与旧数据重复 | 白白重写一次文件（还有被占用/中断的风险） |

另外：**条数判定看「本次新增」而不是「合并后总数」** —— 否则 `--n 200` 在追加模式下
永远「达标」（旧 100 + 新 1 = 101 也可能糊弄过去），告警形同虚设。

```bat
:: 追加 200 条到已有文件（旧 100 条必须完好）
run.cmd --n 200 --out data\malaysiayp_100.csv --append --order sequential --per-cat 3
:: 完成后核对（--against 传追加前生成的 .bak，机器证明旧号码一条没丢）
run.cmd verify data\malaysiayp_100.csv --against data\malaysiayp_100.20261008-104218.bak
```

### 追加后自证：`--verify --against <基线>`

三条铁律防的是「**写入时**把旧数据弄丢」。但用户真正关心的是结果 ——
**跑完之后，怎么用机器证明「那 100 条老数据还在」？**

`--verify --against` 就是答案：拿追加前的 `.bak` 当基线，逐一核对。

```bat
run.cmd verify data\malaysiayp_100.csv --against data\malaysiayp_100.20261008-104218.bak
```

判定规则（**只认超集关系**）：

| 检查 | 通过条件 | 不通过的后果 |
|---|---|---|
| 基线号码保留 | 基线里**每一个**手机号都仍存在于新文件 | 报「旧号码丢失 N 个」，**退出码 6** |
| 总行数 | 新文件行数 ≥ 基线行数 | 报「总行数减少」，退出码 6 |
| 基线可读 | 基线文件必须存在且能解析 | 报「基线文件不存在 / 读取失败」，退出码 6 |

> **为什么必须比「号码」而不是比「行数」**：行数相同也可能是「丢了 50 条 + 多了 50 条」。
> 只有逐号码做集合包含判断，才能证明**没有覆盖**。
>
> 这也是**唯一的、可脱离 LLM 复现的证据** —— 计划任务里跑完追加后接一句
> `--verify --against`，退出码非 0 就报警，人不用盯着看。

```bat
:: 计划任务里的标准收尾：追加 → 自证 → 失败即告警
run.cmd --n 200 --out data\malaysiayp_100.csv --append --order sequential
if errorlevel 1 goto :fail
run.cmd verify data\malaysiayp_100.csv --against data\malaysiayp_100.<上一次的>.bak
if errorlevel 1 goto :fail
```

---

## 三·D、限流上限实测（`--stress-test`）

**问题**：`--delay` 到底设多少？拍脑袋设 2s 可能太慢（浪费时间）也可能太快（被限流）。

**解法**：让脚本自己去撞一次墙，把上限和恢复时间量出来。

```bat
run.cmd --stress-test
:: 保守跑法（请求更少）
run.cmd --stress-test --stress-burst 15 --stress-rates 2,5 --stress-rate-n 8
```

四个阶段：

| 阶段 | 测什么 | 关键指标 |
|---|---|---|
| **A 突发** | 固定小间隔连发，看限流何时出现、以什么形态出现 | 软限流比例、最长连续次数、**形态（分散 vs 连续）** |
| **B 冷却** | 撞墙后按递增间隔重探 | **连续 N 次成功**才算恢复（单次成功只是运气） |
| **C 稳态** | 各候选间隔各发 N 次，间隔之间插入冷却 | 每个间隔的成功率（消除「先测的占便宜」） |
| **D 退避** | 复现脚本内置的 6s→12s→24s 重试 | **吸收率** —— 这套修复方案到底管不管用 |

结论会打印「生产建议 `--delay X`」，并写入 `data/ratelimit-report.json`。

**两个必须理解的要点**：

1. **软限流的形态是「分散随机丢弃」，不是「跑满 N 次就封」。**
   实测 30 次连发 @0.3s：**20 次正常、10 次 0 字节（33.3%）**，且**交错出现**
   （`S O SS OOO S O S OO O S OOOO S SS`），**最长连续只有 2 次**。
   所以「第一次出现 0B」这个指标本身没有意义 ——
   真正有意义的是**软限流比例**和**退避吸收率**。

2. **不要把软限流当封禁中止。** 软限流是 200 + 0B，可重试；
   真封禁是 401/403/451 或挑战页指纹。脚本已分开处理，探针也分开统计。

**实测结论（2026-10-08，共 77 次探测请求）**：

| 指标 | 实测值 | 含义 |
|---|---|---|
| 软限流比例 | 33.3%（10/30 @0.3s） | 概率性丢弃，非硬计数 |
| 最长连续丢弃 | 2 次 | **不存在「越试越封」的雪崩** |
| 硬封禁 | **0 次** | 该站不用 429/403 惩罚 |
| 稳定恢复时间 | **≈41 秒**（连续 3 次成功才算） | 5s 时成功 0 次；15s 才出现第 1 次成功 |
| 各间隔成功率 | 1s=70% · 2s=70% · 3s=80% | **几乎不随间隔变化** → 瓶颈是**配额回补**，不是请求速率 |
| 退避吸收率 | **100%**（4/4，平均 1.75 次尝试） | **6s→12s→24s 这套方案完全够用，不需要并发/代理** |

> **最重要的一条**：既然成功率对 `--delay` 不敏感，那么**把 `--delay` 从 2s 调到 10s
> 并不会让限流变少，只会让总耗时变 5 倍**。正确做法是**保持 2s + 靠退避吸收**，
> 而不是一味拉长间隔。这是「实测」而非「拍脑袋」才能得到的结论。

> ⚠️ **上述结论来自短时探测。长时间抓取中出现的 `200 + 0 字节` 是另一回事 ——
> 已查明是源站应用层的确定性缺陷，与速率无关。详见三·F。**

---

## 三·F、⚠️ `HTTP 200 + 0 字节` 的真相：**两类**坏响应（A 型限流 / B 型坏缓存）

> **2026-10-08 15:20 第二次更正。** 本节经历三次修订：
> ① 最早叫「累积限流惩罚态」→ ② 14:47 改为「源站确定性缺陷」→
> ③ **现在**：**两类并存**，恢复时间差两个数量级，处置方式完全不同。
>
> **方法论教训（最重要的一条）**：早先的「五种外部假设证伪」用的是**当时还正常**的页，
> 所以实验全部无效 —— 它只证明了「好页加参数还是好页」。
> **要证伪，必须拿「已经坏掉的页」做实验。** 重做后结论才可靠。

### 一、两类坏响应

| | **A 型 · 短时限流** | **B 型 · 坏缓存** |
|---|---|---|
| 表现 | `200` + **0 字节**，无 `Content-Length` | `Content-Length: 32768`(2¹⁵) 截断，或持续 0 字节 |
| 恢复 | **分钟级**（实测 < 4 分钟） | ≥ **24 小时**（`s-maxage=86400`） |
| 判据 | 静默后重测**会恢复** | 静默后重测**仍坏**，`Etag` 恒定 |
| 触发 | 请求过密 | 与速率无关 |
| 分布 | **分类首页**为主 | **深层分页**为主 |
| 处置 | **降速重试**，不要延期 | **延期 25 小时**后复检 |

### 二、决定性证据

**A 型存在**：`/cat/automotive/` 首次 **42990 B** → 密集请求后 **0 B** →
**静默 4 分钟后重测恢复 42990 B**。

**B 型存在**：`/cat/agricultural/page/6/` 静默 4 分钟后**仍 0 B**；
`/cat/agricultural/page/3/` 稳定 **32768 B**，`Etag: "15n1s0qgy4tp9y"` 恒定。

**抽样复测**（`python probe_recover.py --n 30 --gap 10`）：

```
复测结果：OK=0  截断=1  0B=29   恢复率=0.0%
```

⇒ **深层分页以 B 型为主**（延期是对的）；**分类首页以 A 型为主**（降速重试即可）。

**限流阈值实测**：对同一批 URL 分别用 3s（20 请求/分钟）与 8s（7.5 请求/分钟）间隔请求，
**响应字节数完全一致**（例：`architectural-services` 两轮都是 26814 B，
`asian-restaurant` 两轮都是 39144 B）⇒ **20 请求/分钟是安全的**。
触发限流的那次是 **~280 请求/分钟**（探测循环里漏了 `sleep`）。

> **结论：`--delay 3.0` 安全，不需要降速。** 旧版「降速对失败无效」的观察是对的，
> 但原因不是「确定性缺陷」，而是**当时观测的失败本来就与速率无关**（B 型）。

### 三、⚠️ 重要澄清：「页面短」≠「页面坏」

早先把「< 34000 字节」当作截断判据，**这是错的**。实测对照：

| 分类首页 | 字节 | 含 `</html>` | 记录数 | 正确判定 |
|---|---:|---|---:|---|
| `art-schools` | 19533 | ✅ | **1** | **正常**（该分类只有 1 条记录） |
| `architectural-metalwork` | 22757 | ✅ | 3 | **正常** |
| `auditing` | 33338 | ✅ | 13 | **正常** |
| `asian-restaurant` | 39144 | ✅ | 20 | 正常 |
| `asphalt-felts-and-coatings` | 36864 | ❌ | 19 | **真截断** |

**正确的判据只有两条**（脚本 `fetch()` 第 470 行已实现，无需改动）：

```python
MIN_PAGE_BYTES = 3000
if len(body) < MIN_PAGE_BYTES or "</html>" not in body.lower():
```

即 **`< 3000 字节` 或 缺 `</html>`**。**不要**用「正常页 36–37 KB」当阈值 ——
那是「每页 20 条记录」时的尺寸；分类只有 1 条记录时，页面自然只有 19 KB 且**完全正常**。

> 这条澄清很关键：它排除了「大量正常短页被误杀」的可能，把缺陷范围锁定在
> **真 0 字节 + 真缺 `</html>`** 两类上。

### 四、五种外部假设已全部证伪（**用坏页**重做）

| 假设 | 实验 | 结果 |
|---|---|---|
| 限流（对 B 型） | 3s vs 8s 间隔对照 | ❌ 字节数完全一致 |
| 封禁 | 查 403 / 429 / 验证页 / 挑战指纹 | ❌ 0 条 |
| 缓存键含 query | `?cb=123456789`、`?cb=987654321&x=1` | ❌ 仍 0 B / 32768 B |
| 强制回源 | `Cache-Control: no-cache` / `no-store` / `Pragma` | ❌ 仍坏 |
| 传输层协商 | `Accept-Encoding: identity / gzip / br`、`RSC: 1` | ❌ 仍坏 |

补充：无尾斜杠 → `301`；双斜杠 → `308`；`page%2F6` → `404`；
`?page=6` 被忽略（返回首页 42516 B）。
⇒ **客户端无法绕过 B 型坏缓存，只能等 `s-maxage=86400` 过期。**

**站点技术栈**：`Via: 1.1 Caddy` +
`Vary: rsc, next-router-state-tree, next-router-prefetch, next-router-segment-prefetch` +
`X-Nextjs-Cache: HIT` + `X-Nextjs-Prerender: 1` + `X-Nextjs-Stale-Time: 300`
⇒ **Next.js App Router（ISR 预渲染）+ Caddy 缓存**。
坏缓存条目由源站在预渲染/回源时产生，随后被 CDN 固化 24 小时。

### 五、正确处置

```bat
:: 1) 分层延期缺陷页（attempts 1→30分钟 / 2→6小时 / ≥3→25小时）
python defer_defects.py --apply

:: 2) 未索引分类首页提到队首（信息密度最高，且多为 A 型，成功率高）
python prioritize.py --apply

:: 3) 抽样复测，区分 A / B
python probe_recover.py --n 30 --gap 10

:: 4) 看有效进度（自动剔除延期页，否则进度条被永远抓不到的页压住）
python supervise.py --status

:: 5) 需要撤销时
python defer_defects.py --rollback
python prioritize.py --rollback
```

**`supervise.py` 的自适应规则（注意：按「健康率」而非「成功率」）**

| 健康率 | 动作 |
|---|---|
| ≥ 95% | `--delay` × 0.85（下限 3s），片间冷却 60s |
| 85%–95% | 保持，冷却 60s |
| 60%–85% | `--delay` × 1.5，冷却 ×1.5（下限 120s） |
| < 60% | `--delay` × 2（上限 120s），冷却 ×3（上限 3600s） |

其中 **健康率 = 1 − (硬错误 + 0.5×截断) / 尝试数**，
**0 字节缺陷页不参与调速** —— 否则会被误导成「站点在压我们」而白白降速。

**代价提示**：全量任务的终点是 `rc=6`（重试预算耗尽 + 缺口清单），
**不是 `rc=0`**。正确验收口径是「全量 CSV 分片 + `logs/DEFECT-PAGES.json` 缺口清单」。
不要指望 `rc=0`，也不要为此把 `--page-attempts` 调大。
---

## 三·H、缺陷页的识别与可逆剔除（`defer_defects.py`）

**为什么不能永久删除**：实测 `agricultural/page/213` 由成功变为失败，
证明缺陷状态**会随时间变化**。永久标 `failed` 会丢失自愈机会。

**做法：只改 `pages.not_before`，把缺陷页推后 6 小时。**

```sql
UPDATE pages SET not_before = :now_plus_6h
WHERE status='pending' AND error<>'' AND not_before <= :now
--                                        ^^^^^^^^^^^^^^^^^^
-- 关键：只延期「已经到期」的页，否则定时执行会把已延期的页重复推后，
--       让它们永远回不来。加了这个条件后，第二次执行会输出「已延期 0 页」。
```

**为什么这样改是安全的**

| 校验 | 是否受影响 |
|---|---|
| `_full_coverage()`（完成判定） | ❌ 不看 `not_before` |
| `_full_verify_db()` | ❌ 只校验 `status='done'` 的页 |
| 采集脚本选页 `not_before<=?` | ✅ 自然跳过，正是我们要的效果 |
| `status` / `attempts` / `error` / `rows` | ❌ 完全不动 |

**为什么是 6 小时**：站点 CDN 缓存期 `s-maxage=86400`（24h），
我们的复检周期 6h（一天 4 次）。无效请求比脚本默认退避（上限 1h）**减少约 6 倍**，
同时保留一天 4 次自愈捕捉。30 次重试预算对应 **7.5 天** 窗口。

**产物与回滚**

| 文件 | 作用 |
|---|---|
| `logs/DEFECT-PAGES.json` | 缺陷页清单（分类/页码/尝试次数/错误）—— **缺陷证据** |
| `data/malaysiayp_full.defer-backup-*.json` | 延期前快照 —— **回滚依据**（保留最近 12 个） |
| `logs/status.json` | 新增 `deferred_pages` / `deferred_next_at` / `ready_pages` / `effective_pct` |

```bat
python defer_defects.py              :: 干跑：只统计与备份，不改库
python defer_defects.py --apply      :: 执行延期
python defer_defects.py --rollback   :: 用最近备份恢复 not_before
```

**硬剔除（仅在前述方案失败时才用）**：把缺陷页 `status` 直接标 `failed`，
任务会立刻收敛到 `rc=6`。代价是**永久放弃这些页**。


---

## 三·G、`supervise.py` —— 自适应守护与监督报告（v1.1.0）

**它解决什么**：全量任务要跑几天，`run.cmd`/`supervisor.cmd` 只会「退出就再来一次」，
不会判断「现在是不是该停」。`supervise.py` 补上判断力。

```bat
python supervise.py                        :: 守护：一直推进到完成（自适应调速）
python supervise.py --status               :: 只读：打印监督报告（进度/速率/ETA/限流/重试预算）
python supervise.py --once                 :: 只推进一片，打印报告后退出
python supervise.py --once --budget-minutes 15
                                           :: 单片限时 15 分钟；计划任务必须用它把切片压进触发窗口
python supervise.py --reset-state          :: 重置自适应状态（delay/冷却）
```

**v1.1.0 相对 v1.0.0 的四项修正（都是 2026-10-08 实测踩出来的）**

| # | 修正 | 不改会怎样 |
|---|---|---|
| 1 | `_ensure_stdio()`：`sys.stdout is None` 时把输出改接到 `logs/slice-stdio.log` | `pythonw.exe` 下 `print()` 抛 `AttributeError`，**计划任务每个切片启动即崩** |
| 2 | 新增 `--budget-minutes`，切片时长可控 | `IgnoreNew` 会因上一实例未结束而拒掉下一次触发（`0x800710E0`） |
| 3 | `rc=6` 专门收敛：落盘缺口报告 + `logs/EXHAUSTED.json` + 6 小时复检 | 每分钟空转一次，永远不收敛，还会刷满日志 |
| 4 | `read_exhausted()` 命中时切片直接返回 6，**不 spawn 采集脚本** | 计划任务每 20 分钟生成一个 994 字节的空 `run-*.log` |

**产物**：`logs/status.json`（机器可读，供计划任务/看板消费）、
`logs/supervise.log`（每片一行摘要）、`logs/supervise-state.json`（自适应状态与历史）、
`logs/slice-stdio.log`（`pythonw` 下的 stdout 落盘）、
`logs/GAP-REPORT.{json,md}`（rc=6 时的缺口清单）、`logs/EXHAUSTED.json`（耗尽标记）。

**与 `scrape_malaysiayp.py` 的边界**：`supervise.py` **只读**断点库，
只通过命令行参数驱动采集，**不修改** `.sqlite3` / `.parts` / `.job.json`。
`--out` / `--phone-scope` / `--page-attempts` 属于**与断点库绑定的冻结参数**，
一旦任务开跑就不能改（改了会触发输出保护）；`--delay` / `--jitter` /
`--chunk-pages` / `--chunk-pause` 可随时调整。

**`rc=6` 的语义与收敛行为**见「六·C」。

---

## 三·E、看板同步（`inject_samples.py`）

**问题**：`index.html` 的样本表、分类数、号段分布这些数字，是**手工贴进去的**。
数据一追加，HTML 还停在上一次的数字上 —— 看板开始撒谎，而且没人会察觉。

**解法**：把「CSV → 看板」变成幂等、可重复执行的脚本动作。

```bat
python inject_samples.py                 :: 默认 data\malaysiayp_100.csv → index.html
python inject_samples.py --dry-run       :: 只看会改什么，不写文件
python inject_samples.py --check         :: 幂等检查：HTML 是否已与 CSV 一致
```

**工作原理**：只替换 `index.html` 里成对的注入标记之间的内容，**不做任何猜测**。

| 标记 | 管什么 |
|---|---|
| `INJECT:SAMPLES_HEADING` | §7 标题（条数 / 分类数） |
| `INJECT:SAMPLES_STATS` | §7 统计卡片（样本量 / 分类数 / 最大分类占比 / 号段 / 位数） |
| `INJECT:SAMPLES_JS` | §7 表格数据源 `const SAMPLES = [...]`（位于 `<script>` 内，用 `/* */` 注释标记） |
| `INJECT:SAMPLES_NOTE` | §7 合规提示（条数） |
| `INJECT:SAMPLES_INTRO` | §7 引言（条数 / 分类数） |

**安全设计**：

1. **标记必须各出现恰好 1 次**，否则拒绝执行（退出码 5）—— 防止「静默改错地方」。
2. **缩水守卫**：CSV 行数 < 看板现有行数 × 50% 时**拒绝**（退出码 5），
   防止「`--csv` 指错文件把看板从 286 条改成 1 条」。确认无误加 `--force`。
3. **注入后自检**：标记数量、`SAMPLES` 是否为合法 JSON、行数是否等于 CSV 行数、
   统计卡片是否含关键数字。**任一不通过就不落盘。**
4. **先备份**：`index.html.<时间戳>.bak`。
5. **原子写**：`.tmp` → `os.replace`。
6. **幂等**：连跑两次 sha256 不变，第二次直接报「已是最新」。
7. **退出码**：0 成功 / 2 参数错 / 3 文件缺失 / 5 标记缺失、缩水拦截、或自检不通过。

> ⚠️ **注意**：`inject_samples.py` 自己的版本号会写进生成的注释头。
> **改了 `__version__` 之后要重跑一次注入**，否则 `--check` 会报「HTML 与 CSV 不一致」
> （这不是 bug，是版本号变了导致生成内容变了）。

**新增分类怎么办**：脚本内置 `CAT_ZH`（slug → 中文标签）映射表。
遇到未收录的分类会**打印警告并原样显示 slug**，提醒你补表 —— 不会静默出错。

```bat
:: 计划任务里的标准收尾：抓取 → 追加 → 自证 → 同步看板
run.cmd --append --order sequential --n 200 --per-cat 5
run.cmd verify data\malaysiayp_100.csv --against <上一次的>.bak
python inject_samples.py
```

---

## 四、故障处置表（现象 → 根因 → 处置）

| 现象 | 根因 | 处置 |
|---|---|---|
| 日志出现 `[响应过短(0B)] 疑似软限流` | 站点对高频请求返回 **200 + 0 字节**（不是 429） | **正常现象**，脚本会自动退避重试（6s→12s→24s）。频繁出现就把 `--delay` 调到 3~5 |
| `– xxx p258: 抓取失败（响应过短(0B)）→ 跳过该页` | 该页重试 3 次仍被软限流 | 无害，跳过即可。若大量出现 → 调大 `--delay` 或 `--retries` |
| 退出码 **4** + `被封禁 HTTP 403` | IP / UA 被拉黑 | 停止运行数小时；调大 `--delay`；确认没有并发 |
| 日志出现 `出现验证页/拦截指纹` | 命中 Cloudflare 挑战页 | 同上。**不要试图绕过验证码** |
| 退出码 **5** + `连续 3 页解析为空` | 站点改了 HTML 结构 | 见第七节「站点改版怎么修」 |
| 退出码 **6** | 抓到的条数不够 | 调大 `--max-pages`（如 30→60）；或调小 `--n` |
| 退出码 **7** | 输出文件已存在 | 加 `--force` 覆盖（自动备份）/ `--append` 追加 / 改 `--out` |
| 退出码 **8** | 有另一个实例在跑 | 等它结束。若确认无残留进程 → `--no-lock` |
| `--coverage` 报大量缺口 | 只抽样抓了部分页 | 正常。用 `--order sequential` 补齐 |
| `--coverage` 说「尚无下载记录」 | `cache/manifest.json` 为空 | 先跑一次抓取；旧版本脚本不写 manifest |
| `--force` 后找不到旧数据 | 已自动备份 | 找同目录 `<名>.<时间戳>.bak` |
| `--append` 报「没有新记录可写」 | 抓到的号码全已存在 | 正常（去重生效）。可换分类或调大范围 |
| `--append` 报「读取已有 CSV 失败」+ 退出码 7 | 旧文件被占用 / 编码坏了 / 列名不符 | **这是保护，不是故障**。关掉 Excel；确认列名是 8 列标准 schema |
| `--append` 后旧数据没了 | 不可能（v2.2.0 起读不到旧数据会中止） | 若真发生，说明在用 v2.1.0 以前版本 → 升级；并从 `.bak` 恢复。**事后核对用 `--verify --against <旧.bak>`** |
| `--verify --against` 报「旧号码丢失」 | 真的发生了覆盖，或基线传错了文件 | **立刻停下**：从 `.bak` 恢复，检查是否用了 `--force` 或旧版本脚本 |
| `--verify --against` 报「基线文件不存在」 | `.bak` 路径写错 / 被清理 | 用 `ls data/*.bak` 找到正确的备份名；**不要跳过这一步** |
| `--stress-test` 报「已达总请求硬上限」 | 触发了 `--stress-max-requests`（默认 400） | 正常保护。需要更长测试就调大该值 |
| 输出变成 `*_new.csv` | 目标文件被占用 | 关掉 Excel/编辑器，重跑即可 |
| 退出码 **3** + `robots.txt 不允许` | 站点改了 robots 规则 | 先 `run.cmd --check-robots` 看原文。若确实禁止 → 停手；若你已获授权 → `--skip-robots-check` |
| `PermissionError: ...csv` | CSV 被 Excel/编辑器占用 | 脚本已自动降级写成 `*_new.csv`。关掉占用程序即可 |
| 退出码 **3** + `目录不可写` | 权限问题 | 换目录或修权限 |
| 退出码 **3** + `网络连通 FAIL` | 断网 / DNS / 代理 | 检查网络；公司网络可能需代理 |
| 索引损坏 | `index.json` 被写坏 | **脚本会自动改名保留为 `index.json.corrupt` 并重建**，无需人工干预 |
| 缓存文件损坏 | 上次运行被杀留下半截文件 | **脚本会自动丢弃该缓存并重新抓取** |
| 中文乱码 | 控制台编码 | 脚本已强制 UTF-8 输出；`run.cmd` 已 `chcp 65001` |
| CSV 里出现 `�` | **源站数据本身**带 U+FFFD | 脚本已清洗。若仍有 → 跑 `run.cmd verify` 会报出具体行号 |
| **产出全是一个分类** | `--per-cat` 曾按「每页」而非「每分类」生效（v2.0.0 bug，v2.1.0 已修） | 升级到 v2.2.0；`verify` 会报「分类过度集中」。自检：`--self-test` |
| **CSV 里没有 011 开头的号码** | `MOBILE_RE` 曾只认 9~10 位，漏掉 11 位的 011 段（v2.0.0 bug，v2.1.0 已修） | 升级到 v2.2.0；`verify` 会打印「号段分布 / 位数分布」 |
| `inject_samples.py` 报「标记出现次数异常」+ 退出码 5 | `index.html` 里的 `INJECT:*:START/END` 被误删/重复 | 补回成对标记（各 1 次）。**脚本故意不猜、不兜底**，避免改错位置 |
| `inject_samples.py` 报「注入后自检不通过」 | 生成的内容与 CSV 对不上 | **脚本未写入任何文件**。看它列出的具体问题（行数不符 / JSON 非法 / 统计卡片缺数字） |
| `inject_samples.py` 报「缩水守卫」+ 退出码 5 | `--csv` 指向了行数少得多的文件（测试文件 / 未追加完的旧文件） | **这是保护，不是故障**。确认要改小就加 `--force`；否则检查 `--csv` 路径 |
| `inject_samples.py --check` 报「HTML 与 CSV 不一致」但刚注入过 | 改了 `inject_samples.py` 的 `__version__`（版本号写在生成的注释头里） | 重跑一次 `python inject_samples.py` 即可 |
| `inject_samples.py` 警告「未收录中文标签的分类」 | 出现了 `CAT_ZH` 里没有的新分类 slug | 在新分类下正常现象。把 slug → 中文标签补进 `inject_samples.py` 的 `CAT_ZH` 再重跑 |
| 看板数字与 CSV 不一致 | 忘了跑注入器（HTML 里的数字是上次注入的） | `python inject_samples.py --check` 会直接报不一致；重跑注入器即可 |
| 条数超发（目标 100 却写出 109） | 旧版只在换页时判总量，单页多出的条目全收 | v2.1.0 起 `--n` 是硬上限，达标即停 |
| **`--manual` 抛异常、退出码 1** | 手册正文含正则 `{7,8}`，被 `str.format()` 当占位符（v2.1.0 开发中修掉） | 升级到 v2.1.0；自检第 9 组会断言文档可渲染 |

---

## 五、怎么判断一次运行是否健康

**四步：**

```bat
:: 0) 离线自检（零网络；只有改过脚本才需要，30 秒内跑完）
run.cmd --self-test

:: 1) 运行前体检
run.cmd doctor

:: 2) 运行（建议顺序模式，便于后续校验完整性）
run.cmd --order sequential --n 100

:: 3) 产出校验（追加模式下加 --against 传上一次的 .bak，自证旧数据没丢）
run.cmd verify data\malaysiayp_100.csv

:: 4) 下载完整性（可选，看有没有缺口）
run.cmd --coverage

:: 5) 看板同步（可选，把新数字注入 index.html）
python inject_samples.py
```

`verify` 会检查：行数、唯一号码数、格式异常（非 01X）、**号段分布**、**号码位数分布**、
**分类集中度**、可疑字符、空关键字段、来源留痕完整度。
全部通过返回 **0**，否则返回 **6** 并列出问题。

> **怎么读这三项新指标**
> - **号段分布**：应能看到多个 010/012/013/…/019。若整段缺失（尤其 **011**）→ 正则或过滤有问题。
> - **号码位数分布**：应同时有 `10位` 和 `11位`。**只有 10 位 → 011 段被漏抓了。**
> - **分类集中度**：最大分类占比应远低于 90%。若某分类占 ≥90% → 配额没生效，页预算被单分类吃光。

想额外确认来源页还活着（会联网，抽样 3 条）：

```bat
run.cmd verify data\malaysiayp_100.csv --probe 3
```

**看日志**：每次运行都会在 `logs/run-<时间戳>.log` 留下完整记录，包括每一次重试的原因。
这是无人值守时唯一可靠的排错依据。

**看 meta**：`data/malaysiayp_100.meta.json` 记录了本次运行的全部参数、条数、覆盖分类、退出码。
长期追溯时先看它。

---

## 六、无人值守（Windows 计划任务）

1. 打开「任务计划程序」→ 创建基本任务
2. **程序或脚本**：`C:\Users\Admin\WorkBuddy AI\2026-10-07-16-32-42\phone-directory\run.cmd`
3. **添加参数**：`--n 100 --out data\scheduled.csv` （**不要留空**，留空会触发 pause 挂住任务）
4. **起始于**：`C:\Users\Admin\WorkBuddy AI\2026-10-07-16-32-42\phone-directory`
5. 勾选「不管用户是否登录都要运行」+「如果任务失败，按以下频率重新启动」

**Linux cron：**

```cron
0 3 * * * cd /path/to/phone-directory && ./run.sh --n 100 --out data/scheduled.csv >> logs/cron.log 2>&1
```

**监控建议**：用退出码判断，不要 grep 日志。
- `0` → 正常
- `6` → 数据偏少，值得看一眼
- `7` → 忘了加 `--force`/`--append`，或改了输出名
- `4` / `5` / `8` → 需要人工介入，应告警

**定时任务的输出策略（重要）**：
- 想要「每天一份新文件」→ 在参数里带上日期，或让脚本用 `--out data\scheduled.csv --force`
- 想要「持续累积」→ 用 `--append`（按 phone 去重，不会重复）
- **不要**在计划任务里省掉 `--out` 参数（见上一节说明：会触发 pause）
- 计划任务重叠时**不会互相踩踏**：第二个实例会被互斥锁挡住并返回退出码 8

### 六·B、全量任务的计划任务（2026-10-08 已实测注册并端到端验证）

当前机器上已注册任务 **`MalaysiaYP-FullCrawl`**，每 **20 分钟**推进一个采集切片：

| 项 | 值 |
|---|---|
| 程序 | `C:\Users\Admin\.workbuddy-ai\binaries\python\versions\3.13.12\pythonw.exe` |
| 参数 | `"C:\...\phone-directory\supervise.py" --once --budget-minutes 15` |
| 起始于 | `C:\...\phone-directory` |
| 触发器 | 一次启动 + 每 20 分钟重复，持续 3650 天 |
| 设置 | `MultipleInstances=IgnoreNew`、`StartWhenAvailable`、`ExecutionTimeLimit=25min` |
| 身份 | 当前用户 / **Interactive** / Limited（因此只在登录状态下运行） |

**为什么用 `pythonw.exe` 而不是 `.cmd`**：任务以 Interactive 身份运行时，控制台程序会在桌面弹出窗口。
`pythonw.exe` 是无控制台子系统的解释器，不产生窗口。
配套地，`supervise.py` 里给 `subprocess.Popen` 加了 `CREATE_NO_WINDOW`，
否则它 fork 出来的 `python.exe` 会自己新建一个控制台窗口弹出来。

**⚠️ 但 `pythonw.exe` 有一个必须自己兜的坑**（2026-10-08 实测）：
`pythonw.exe` 会把 `sys.stdout` / `sys.stderr` **显式设成 `None`**。
任何 `print()` 立刻抛 `AttributeError`，而 `supervise.py` 的 `log()` 第一行就是 `print()`，
**整个切片会在启动瞬间崩掉**，`LastTaskResult` 变成异常码而不是业务码。
`supervise.py` 里的 `_ensure_stdio()` 负责把输出改接到 `logs/slice-stdio.log`。
判据：**只要 `logs/slice-stdio.log` 有内容，就说明任务确实是在无控制台环境下跑的**。
如果它一直不存在，说明任务实际走的是 `.cmd`/`python.exe`（有控制台），不是 `pythonw.exe`。

**查询 / 手动触发 / 删除**

```powershell
Get-ScheduledTask -TaskName "MalaysiaYP-FullCrawl" | Select-Object TaskName,State
Get-ScheduledTaskInfo -TaskName "MalaysiaYP-FullCrawl" | Select-Object LastRunTime,LastTaskResult,NextRunTime
Start-ScheduledTask  -TaskName "MalaysiaYP-FullCrawl"     # 立即跑一片
Stop-ScheduledTask   -TaskName "MalaysiaYP-FullCrawl"     # 终止当前实例（连子进程一起）
Unregister-ScheduledTask -TaskName "MalaysiaYP-FullCrawl" -Confirm:$false   # 收工后删掉
```

`LastTaskResult` 对照：

| 值 | 十六进制 | 含义 | 要做什么 |
|---|---|---|---|
| `0` | — | 切片正常结束（rc=0 或 9） | 无 |
| `6` | — | 重试预算已耗尽，缺口已落盘 | 看 `logs/GAP-REPORT.md`，等自动复检 |
| `8` | — | 互斥锁被占（守护正在跑） | 无，属正常竞争 |
| `267009` | `0x41301` | 正在运行 | 无 |
| `267011` | `0x41303` | 从未运行 | 检查触发器 `StartBoundary` |
| `267014` | `0x41306` | 被终止 | 检查是否被 `Stop-ScheduledTask` |
| `2147942401` | `0x80070001` | 程序未找到 | `pythonw.exe` 路径失效 |
| **`2147946720`** | **`0x800710E0`** | **「操作员或管理员拒绝了请求」——上一个实例还在跑，`IgnoreNew` 拒了新触发** | **把 `--budget-minutes` 压到小于触发间隔** |

**⚠️ 创建任务的两个致命坑（都踩过）**

1. **`-RepetitionDuration ([TimeSpan]::MaxValue)` 会失败。**
   它序列化成 `P99999999DT23H59M59S`，任务计划程序报
   `任务 XML 包含格式不正确或超出范围的值。(8,42):Duration:P99999999DT23H59M59S`。
   **改用 `-RepetitionDuration (New-TimeSpan -Days 3650)`**。

2. **这个错误是「非终止错误」，不加 `-ErrorAction Stop` 就会被 `| Out-Null` 吞掉**，
   表现为「注册返回了对象、但 `Get-ScheduledTask` 查不到」。
   **注册语句必须写 `-ErrorAction Stop` 并放在 try/catch 里**。

**⚠️ 如果是在 WorkBuddy 沙箱里操作，还有第三个坑**：
沙箱会把对系统受保护位置的写入**虚拟化后丢弃**——同一个命令内 `Test-Path` 返回 True，
换一条命令就查不到。**必须用 `dangerouslyDisableSandbox` 执行注册，并且从「另一条命令」复核**。

**⚠️ 第四个坑：不要编辑正在运行的 `.cmd`（2026-10-08 实测，很隐蔽）**

`cmd.exe` 执行批处理文件时**不把文件读进内存**，而是记住一个**字节偏移**，
每执行完一条命令就从该偏移继续读下一行。如果你在它运行期间编辑了这个 `.cmd`，
文件长度一变，偏移就落到错误的位置，**cmd.exe 会跳回去重复执行某些行**。

实测经过：`task_slice.cmd` 在 13:58:33 被计划任务拉起，13:58:35 执行到 python 行；
我在 14:05 给它加了 `--budget-minutes 15`（文件变长），结果那个**还活着的 cmd.exe 在 14:05:47
跳回去把 python 行又执行了一遍**，凭空多出一个切片实例。

后果不只是多跑一次：它会让计划任务的旧实例**永远不结束**，
于是 `MultipleInstances=IgnoreNew` 把后续所有触发全部拒掉（`0x800710E0`）。

**规避办法（任选其一，推荐第 1 条）：**
1. 改完 `.cmd` 后，立刻 `Get-CimInstance Win32_Process -Filter "Name='cmd.exe'"` 检查
   有没有还挂着 `task_slice.cmd` 的进程，有就 `Stop-ScheduledTask` 清掉。
2. 计划任务的动作**不要指向 `.cmd`**，直接指向 `pythonw.exe <脚本> <参数>`（当前就是这么做的）。
3. 需要改 `.cmd` 时，先 `Stop-ScheduledTask`，改完再让它自己触发。

**第五个坑：切片时长必须短于触发间隔**

`MultipleInstances=IgnoreNew` 的语义是「上一个实例没结束，就拒掉新触发」。
所以 `supervise.py --once` 的 `--budget-minutes` **必须严格小于 `RepetitionInterval`**。
当前：`--budget-minutes 15` < 20 分钟间隔，安全。
另外 `ExecutionTimeLimit` 也要大于切片预算（当前 25min > 15min），
否则任务计划程序会在切片跑完前强杀它。

**建议的注册模板（可直接改用）**

```powershell
$dir = "C:\Users\Admin\WorkBuddy AI\2026-10-07-16-32-42\phone-directory"
$pyw = "C:\Users\Admin\.workbuddy-ai\binaries\python\versions\3.13.12\pythonw.exe"
# --budget-minutes 必须 < RepetitionInterval，否则下一次触发会被 IgnoreNew 拒掉
$a = New-ScheduledTaskAction -Execute $pyw `
       -Argument ('"' + $dir + '\supervise.py" --once --budget-minutes 15') `
       -WorkingDirectory $dir
$t = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
       -RepetitionInterval (New-TimeSpan -Minutes 20) `
       -RepetitionDuration (New-TimeSpan -Days 3650)          # ← 不能用 MaxValue
$s = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable `
       -ExecutionTimeLimit (New-TimeSpan -Minutes 25) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$p = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName "MalaysiaYP-FullCrawl" -Action $a -Trigger $t -Settings $s -Principal $p `
  -Force -ErrorAction Stop                                     # ← 必须 Stop
```

**四层冗余（当前实际部署）**

| 层 | 机制 | 存活范围 |
|---|---|---|
| 1 | Windows 计划任务 `MalaysiaYP-FullCrawl`（每 20 分钟一片） | 登录状态下长期有效，**不依赖任何 LLM 或 WorkBuddy** |
| 2 | 后台常驻守护 `supervise.py`（连续推进） | 当前会话存活期间；用「先探测再启动」避免与第 1 层抢锁 |
| 3 | 启动文件夹 `malaysiayp-crawl-autostart.vbs` | 每次登录自动拉起第 2 层 |
| 4 | WorkBuddy 定时自动化（每小时巡检） | 停滞时拉起第 2 层，出现封禁/结构变更/环境错误时写 `logs/STOP` 并告警 |

第 1、2 层之间靠 `data/malaysiayp_full.csv.lock` 与站点级 `cache/.lock` 互斥：
抢不到锁的一方**秒退**（退出码 8），不会互相踩踏。所以「谁在跑」是动态的，**不要试图同时停掉全部**。

---

### 六·C、任务的「终点」长什么样：`rc=6` 与缺口报告（2026-10-08 补）

**必须先接受一个事实**：本站有**确定性缺陷页**。`/cat/agricultural/page/N/` 这类分页 URL
对特定 N 恒返回 `HTTP 200 + 0 字节`，多次请求结果一致，加 Referer / 换 UA / 加
`no-cache` / 直连不走代理**全部无效**（实测证据见「三·F」）。

脚本的完成判定是：

```python
complete = (home done) and (catalog done) and (无未完成索引) and (gaps == 0)
           and (actual == expected) and (pages['done'] == expected) and (无 total 不一致)
```

要求 `pages['done'] == expected`，**零缺口**。而 `agricultural` 有 216 页永远取不到，
所以 **`rc=0` 在本站不可达**。这不是 bug，是目标函数与站点现实不匹配。

**脚本自己的终止信号是 `rc=6`（`EXIT_INSUFFICIENT`）**：

```python
pending = SELECT min(not_before) FROM pages WHERE status='pending' AND attempts < 30
if pending is None:                      # 所有待处理页的重试预算都烧完了
    code, phase = EXIT_INSUFFICIENT, "incomplete"
    error = "存在失败页、索引失败或页面总数/实体总数缺口，需要人工诊断修复"
```

注意 `rc=6` **不会自愈**——`attempts` 只增不减，重跑只会立刻再拿一个 6。
所以 `supervise.py` v1.1.0 起对它做了专门收敛处理：

| 动作 | 说明 |
|---|---|
| 落盘 `logs/GAP-REPORT.json` | 逐页清单（分类 / 页码 / 尝试次数 / 错误），机器可读 |
| 落盘 `logs/GAP-REPORT.md` | 同上，含按分类汇总表与处置建议，人类可读 |
| 写 `logs/EXHAUSTED.json` | 耗尽标记，含 `next_recheck`（+6 小时） |
| 守护 | 睡 6 小时后清标记重试；期间每 30 秒查一次 `logs/STOP` |
| 切片（`--once`） | 标记未过期就**直接返回 6，不 spawn 采集脚本** |

**为什么是 6 小时**：站点 CDN 的 `s-maxage=86400` 意味着坏响应最多缓存 24 小时，
一天 4 次复检足以在站点恢复后第一时间接上，又不会刷出垃圾日志。

**`rc=6` 时的实际交付形态**（这才是本任务的正确验收口径）：

- `data/malaysiayp_full.parts/part-*.csv` —— 全量 CSV 分片，逐片有 SHA256 账本
- `data/malaysiayp_full.csv.sqlite3` —— 可复查的断点库
- `logs/GAP-REPORT.md` —— 残余缺口清单，逐页可追溯

**什么时候该人工介入**：若 24 小时后缺口页数**一点没降**，说明是源站缺陷而非缓存问题。
此时只有四条路：① 接受上面的交付形态；② 缩小目标范围；
③ 更换出口 IP；④ 与站点方确认配额与授权。
**不要把 `--page-attempts` 再往上调**——单页退避已封顶 3600s，30 次覆盖约 26 小时重试窗口，
继续加只会拉长空转时间。

---

## 七、站点改版怎么修（退出码 5）

站点改版是**唯一必须人工介入**的故障。脚本会在连续 3 页解析为空时中止并返回 5。

**修复步骤：**

1. **看现在的 HTML 长什么样**

   ```bash
   PY="C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"
   # 抓一页存下来
   curl -sL -A "Mozilla/5.0 ... Chrome/120" "https://malaysiayp.com/cat/automotive/" -o /tmp/probe.html
   # 看一条记录的原始结构
   grep -o '<li class="row-item">.\{0,900\}' /tmp/probe.html | head -1
   ```

2. **对照脚本里的 `ROW_RE`**（在 `CONFIG` 区）

   ```python
   ROW_RE = re.compile(
       r'<li class="row-item">'
       r'[\s\S]*?<a href="(/item/[^"]+)"[^>]*>([^<]+)</a>'      # 1=详情链接 2=公司名
       r'[\s\S]*?<span class="row-meta">([^<]*)</span>'          # 3=地址
       r'[\s\S]*?<a[^>]*class="row-phone"[^>]*href="tel:(\d+)"'  # 4=电话数字
       r'[^>]*>([^<]*)</a>',                                     # 5=电话显示
       re.I,
   )
   ```

   5 个捕获组顺序必须保持：**详情链接 → 公司名 → 地址 → 电话数字 → 电话显示**。

3. **改完立刻验证**

   ```bat
   run.cmd --doctor          :: 选择器自检会直接告诉你改对没
   ```

   `doctor` 的第 8 项「选择器自检 ROW_RE」会抓一页跑正则，报告解析出多少条。**>0 就是改对了。**

4. 若连分类结构也变了，检查 `CAT_RE` 和 `PAGES_RE`，然后 `run.cmd --reindex`。

---

## 八、长期维护清单

| 频率 | 动作 |
|---|---|
| 每次运行前 | `run.cmd doctor`（自动任务可省略，但出问题先跑它） |
| 每次运行后 | 看退出码；非 0 时看 `logs/run-*.log` 尾部 |
| **追加运行后** | **`run.cmd verify <csv> --against <本次生成的 .bak>`** —— 机器证明旧数据没丢 |
| 每周 | `run.cmd verify <最新csv>` 确认产出质量没退化 |
| 改过脚本后 | **`run.cmd --self-test`**（零网络，30 秒），通过再联网 |
| 数据更新后 | **`python inject_samples.py`** 同步 `index.html` 看板（幂等，可重复跑） |
| 每月 | `run.cmd --coverage` 看下载缺口；检查 `logs/` 体积，清理 30 天前的日志 |
| 每季 | `run.cmd --reindex` 重建索引（站点分类会增减） |
| 每季 | `run.cmd --stress-test` 复核限流形态是否变了（站点可能换策略） |
| 站点改版时 | 按第七节修 `ROW_RE` |

**互斥锁说明**：脚本默认获取 `cache/.lock`。这是 **OS 级文件锁**，进程结束/被杀时由内核自动释放，
**不会留下需要手动删除的死锁文件**。若看到退出码 8 但确认没有进程在跑，用 `--no-lock` 跳过即可。

**日志清理（PowerShell）：**

```powershell
Get-ChildItem logs\*.log | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item
```

**缓存清理**：`cache/html/` 可安全删除，删掉只会让下次运行重新抓（变慢，但结果相同）。

---

## 九、已知缺陷与修正记录（v2.0.0 → v2.2.0）

这些 bug 都是**静默**的：脚本退出码 0、日志正常、`--doctor` 全绿，但数据是错的（或没了）。
记在这里，因为同类错误还会再犯。

### 缺陷 1：`--per-cat` 按「每页」而非「每分类」生效

| 项 | 内容 |
|---|---|
| 现象 | `--order sequential --n 100 --per-cat 10 --max-pages 30` → 14 页全花在 `agricultural`，产出 **109 条只覆盖 1 个分类** |
| 根因 | 内层循环写的是 `if got >= per_cat: break`，`got` 是**本页**计数。换页时归零，配额形同虚设 |
| 为何没被发现 | `--doctor` 只查环境；`--verify` 只查格式 —— 109 条格式完全合法 |
| 修正 | 引入 `cat_counts` 字典按分类累计；`iter_plan` 接收该字典，达标分类整类跳过（惰性生成器每次恢复都读最新值） |
| 防复发 | `--self-test` 第 4 组「调度 iter_plan」用 3 分类 × 5 页的假索引断言「配额吃满后必须跨 3 个分类」；`--verify` 新增「分类集中度 ≥90% 报警」 |

### 缺陷 2：`MOBILE_RE` 漏掉 11 位的 011 号段

| 项 | 内容 |
|---|---|
| 现象 | CSV 里**一条 011 开头的号码都没有** |
| 根因 | 正则 `01\d{7,8}` 只能匹配 9~10 位。马来西亚 `011-XXXXXXXX` 是 **11 位**，全部被静默丢弃 |
| 实测影响 | 缓存 HTML 里 `tel:` 链接共 1110 条：**1098 条 10 位 + 12 条 11 位（全为 011）**，9 位一条都没有 → 旧正则漏掉 12 条，且 `{7}` 分支纯属空转 |
| 为何没被发现 | 丢数据不报错。退出码 0，条数照样够 |
| 修正 | 改为 `01\d{8}\|011\d{8}`（精确 10 位 或 精确 11 位 011） |
| 防复发 | `--self-test` 第 2 组同时断言「接受 10 位 01X」「接受 11 位 011」「拒绝 9 位」；`--verify` 新增「号段分布 / 号码位数分布」，**只有 10 位就是漏了 011** |

### 缺陷 3：`--manual` 崩溃（`str.format()` 吃掉正则花括号）

| 项 | 内容 |
|---|---|
| 现象 | `run.cmd --manual` 直接抛异常、退出码 **1**（不是语义化退出码） |
| 根因 | 手册正文里写了正则 `01[0-9]{7,8}`，而渲染用的是 `MANUAL.format(ver=...)` —— `{7,8}` 被当成格式字段 → `KeyError: '7,8'` |
| 何时引入 | 就是修缺陷 2 时把这条正则写进手册的那一刻（**改 A 处炸 B 处**） |
| 修正 | 渲染改用 `MANUAL.replace("{ver}", __version__)`，彻底消除 `.format()` 与正则花括号的冲突 |
| 防复发 | `--self-test` 第 9 组「内置文档」：复现 `main()` 的渲染路径并断言不抛异常、版本已注入、无残留 `{ver}`、关键章节齐全 |

### 缺陷 4：`--append` 可能静默退化成「覆盖」

| 项 | 内容 |
|---|---|
| 现象 | 理论上：用户要「追加」，结果旧数据全没了，退出码仍是 0 |
| 根因 | 旧 `read_existing_rows()` 读失败时 `return []`。于是 `append_merge([], 新行)` 只剩新行 → 随后**整文件重写** → 旧的几百条被抹掉 |
| 触发条件 | 旧 CSV 被 Excel 独占 / 编码坏了 / 列名与 schema 不符。**任何一个都会静默触发** |
| 为何最危险 | 用户以为在做「加法」，实际做的是「替换」，而且**日志看起来一切正常** |
| 修正 | ① 加 `strict=True`，读失败/列不符直接抛 `IOError` → `main()` 返回**退出码 7**，一个字节都不写；② `--append` 也自动备份；③ 条数判定改看「本次新增」而非「合并后总数」；④ meta 记录 `old_rows / appended / total_rows` |
| 防复发 | `--self-test` 第 6 组用坏编码文件、错 schema 文件断言「strict 必须抛错」；并加**反例**：造一个真的丢了旧号码的 CSV，断言 `--verify --against` 必须报错（退出码 6） |
| 事后自证 | `--verify <新CSV> --against <追加前的.bak>`：基线号码必须 100% 保留，否则退出码 6 |

### 教训（写给自己）

> **`--doctor` 查环境，`--verify` 查格式，都不查语义。**
> 调度逻辑、正则边界、配额计算这类错误，只能靠**对语义本身写断言**来拦。
> 所以 `--self-test` 不是可选装饰，是必备件。改完代码 → 先自检 → 再联网。
>
> 另一条：**改一处可能炸另一处**（缺陷 3 就是修缺陷 2 时引入的）。
> 所以自检里也要覆盖「文档能不能正常渲染」这种看似无关的东西 ——
> 只要它是**用户会直接执行的路径**，就该有断言。

---