---
id: malaysiayp-crawl-supervision-runbook
title: malaysiayp 全量采集 · 无人值守运行手册（常驻守护 + 看门狗 + 告警）
tags: [malaysiayp, 全量采集, 无人值守, 守护进程, 看门狗, 计划任务, supervise, watchdog]
created: 2026-10-13
updated: 2026-10-14
version: 2.2.0
status: stable
source: 本会话多轮实测（2026-10-08 ~ 2026-10-14），2026-10-14 15:55 跨会话巡检复核通过
confidence: 已核实
---

# 一句话结论

采集已改为**完全无人值守**：计划任务每 20 分钟叫醒 `watchdog.py`，看门狗只在常驻守护停摆时把它拉起；**人只在 `logs/ALERT.json` 出现时才介入**。旧版「每 20 分钟由 LLM 推一片」的范式已废弃——它是效率瓶颈（20 分钟周期里只有 ~8 分钟在采集）。

v1.0.0 的每轮人工监督内容保留在文末「旧范式」一节，仅供排查历史日志时参考。

# 架构（2026-10-14 起）

| 层 | 组件 | 职责 | 谁启动 |
|---|---|---|---|
| 调度 | 计划任务 `MalaysiaYP-FullCrawl`（每 20 分钟） | 只叫醒看门狗，自己不采集 | Windows 任务计划程序 |
| 看门狗 | `watchdog.py` | 读心跳判断守护是否停摆，停摆才拉起 | 计划任务 / 开机自启 vbs |
| 守护 | `supervise.py`（无参数，daemon 模式） | 唯一采集驱动者，自己无限循环跑片 | 看门狗 |
| 采集 | `scrape_malaysiayp.py` | 单片采集，断点落 SQLite | 守护 spawn |
| 巡检 | WorkBuddy automation「malaysiayp 全量采集 · 每小时监督」（id `4d9d98ef-99e4-4658-8889-c2468cfaa200`） | **每小时**读一次心跳/告警/四层冗余，健康时只输出一行 | WorkBuddy 调度器 |

三层自愈都不需要 LLM：`watchdog` 每 20 分钟判活自愈 → 守护自己调速续跑 → 出错写 `ALERT.json`。LLM 巡检只是最后一道兜底，**正常时完全不介入**（不写文件、不起进程）。

健康信号（全部只读文件）：

| 文件 | 含义 |
|---|---|
| `logs/heartbeat.json` | 守护心跳。**采集中每 60 秒刷新一次**（含 `pages_done`/`pages_per_min`/`note`） |
| `logs/ALERT.json` / `ALERT.md` | **唯一需要人介入的信号**。出现即守护已停止重试 |
| `logs/STOP` | 人为停止开关，存在时看门狗不介入 |
| `logs/supervise.log` | 每片的 rc、自适应调速、启停 |
| `logs/watchdog.log` | 看门狗每次判定的结论 |

# 为什么旧架构慢（2026-10-14 实测）

| 问题 | 表现 | 后果 |
|---|---|---|
| 双驱动互抢锁 | 计划任务每 20 分钟跑 `--once`，守护 daemon 同时循环；互斥锁让 daemon 长期让步 | 20 分钟周期只有 ~8 分钟真正在采集 |
| 单片预算过小 | `max_chunks=3 × 25 页` | 每片 7–8 分钟就退，进程反复启停（每次重启 Python + 打开 30MB SQLite） |
| stdout 管道悬挂 | 日志已打印 `rc=9`、采集早已结束，但 `supervise` 进程不退出 | 它继续持有互斥锁 → **实测停摆 15 分钟无任何推进** |

改造后：`max_chunks=12 × 40 页`、`max_minutes=50`，单一驱动连续跑。吞吐从 ~110 页/小时升到 ~216 页/小时（有效 done 页，2026-10-14 10:20 实测 `pages_per_min=3.6`）。

# 可复用操作

```bash
DIR="C:/Users/Admin/WorkBuddy AI/2026-10-07-16-32-42/phone-directory"
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"
cd "$DIR"

# 1) 看健康：只需这一条
cat logs/heartbeat.json

# 2) 巡检（给 LLM / 定时任务的判定逻辑）
[ -e logs/ALERT.json ] && echo "NEEDS_HUMAN: $(cat logs/ALERT.json)" || echo "OK"

# 3) 只读状态报告 + 刷新交付物
"$PY" supervise.py --status
"$PY" export_deliverable.py --quiet

# 4) 停止 / 恢复
touch logs/STOP                                   # 停止（守护在下一片结束后退出）
rm -f logs/STOP logs/ALERT.json logs/heartbeat.json   # 恢复
MSYS_NO_PATHCONV=1 schtasks /Run /TN "MalaysiaYP-FullCrawl"   # 立刻叫醒看门狗拉起守护

# 5) 手动拉起守护（等价看门狗做的事）
"$PY" watchdog.py
```

## 计划任务（2026-10-14 定稿）

- 名称 `MalaysiaYP-FullCrawl`，`SC MINUTE /MO 20`，`Enabled=true`
- 动作：`pythonw.exe "…\phone-directory\watchdog.py"`，起始目录 `…\phone-directory`
- `ExecutionTimeLimit=PT5M`（看门狗秒级完成；旧值 PT25M 是给 `--once` 的）
- 改动作**不要用 `schtasks /Change /TR`**（路径含空格会被 Git Bash 转成 POSIX 路径而失败）。用导出→改 XML→导入：

```bash
MSYS_NO_PATHCONV=1 schtasks /Query /XML /TN "MalaysiaYP-FullCrawl" > _task.xml
# 编辑 <Arguments> / <Enabled> / <ExecutionTimeLimit>
MSYS_NO_PATHCONV=1 schtasks /Create /TN "MalaysiaYP-FullCrawl" /XML _task.xml /F
```

## 开机自启

`start_watchdog.vbs` 已复制到 `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`。开机/登录后自动跑一次看门狗，重启后采集自恢复。

# 坑与反直觉

- **WorkBuddy 的 Bash 工具结束时会杀掉整个子进程树**（2026-10-14 实测：从 bash 里 `pythonw supervise.py &` 启动的守护，命令一结束就没了，日志无任何输出）。**常驻进程必须由计划任务或 `wscript` 启动**，不能从 bash 后台起。
- **判定存活要用心跳，不要只看进程存在**。事故里进程还在，但被 stdout 管道挂住，实际停摆 15 分钟。
- **`pythonw` 无控制台，`sys.stdout` 是 `None`**，任何 `print()` 都会抛 `AttributeError`。`supervise.py` 有 `_ensure_stdio()` 兜底到 `logs/slice-stdio.log`；新增脚本必须自己处理。
- **`build_report()` 返回扁平字段**（`pages_done` / `pages_pending` / `entities_stored` / `effective_pct`），**不是** job.json 的嵌套 `page_coverage.page_states`。按嵌套取会全得到 `None`。
- **`run_chunk` 的日志行曾打印 `TUNABLE` 而非实际生效的 `DAEMON_TUNABLE`**，导致「日志显示 25/3、实际跑 40/12」。看参数以实际启动行为和常量定义为准。
- **Git Bash 会把 `C:\Users\...` 转成 POSIX 路径**，凡是给 `schtasks`/`taskkill` 传 Windows 开关，前面加 `MSYS_NO_PATHCONV=1`。
- **PowerShell 工具在本机返回空 stdout / 沙箱报错**，查进程改用 `tasklist`；需要命令行时改用计划任务或文件落盘。
- **`--status` 的「采集进程存活」在片间空隙显示 False 属正常**，不是故障。
- **主机睡眠会造成跨夜大空档**（Oct 8→9、9→12、12→13，最长 63.5h）。判停滞前先排除睡眠。
- **WorkBuddy 的 automation 调度器表达不了「每半小时」**（2026-10-14 试错）：`FREQ=MINUTELY` 不被识别（返回体没有 `nextRunAt`）；`FREQ=HOURLY;...;BYMINUTE=0,30` 里的 `BYMINUTE` 被忽略（仍按创建时刻的分钟每小时跑一次）；`FREQ=DAILY` 要求 `BYHOUR` 是**单个** 0–23 整数，传列表直接报错。最小粒度就是 `FREQ=HOURLY;INTERVAL=1`。要更密只能到 Windows 计划任务层做（那里没有 LLM）。
- **不要用 `nslookup` 判站点可达性**（实测报 `Server failed` 而脚本同刻正常）。以脚本 rc 为准。

# 旧范式（v1.0.0，已废弃，仅供读历史日志）

判定「是否在推进」不要看 `--status` 的「采集进程存活」，也不要查计划任务。可靠判据是 `logs/supervise.log` 里「启动采集片」的时间戳 + `--status` 的「空闲时长」（<15 min = 推进中）。

每轮固定动作（顺序不可换）：`prioritize.py --apply` → `defer_defects.py --apply` → `supervise.py --status` → `export_deliverable.py --quiet`。

状态字段口径：

| 打印字段 | 真实含义 | 坑 |
|---|---|---|
| `分类 已索引/待索引 1243 / 62` | 总分类 / 待索引 | 已索引 = 1243 − 62 = 1181 |
| `已完成 / 预期页数` | done / `pages_queued_known` | 低估总量，须同时报 `estimated_true_pct` |
| `有效进度（剔除延期页）` | done / (总 − 延期) | 最诚实的进度口径 |

# 巡检快照（2026-10-14 15:55，跨会话复核）

| 项 | 实测值 | 判定 |
|---|---|---|
| 已完成 / 预期页数 | 3213 / 34347（9.35%） | 推进中 |
| 有效进度（剔延期页） | 3213 / 34342（9.36%） | — |
| 入库实体 / 导出行 | 48,793 / 48,793 | 零差额 ✅ |
| CSV 分片数 | 314 | — |
| 分类 已索引 / 待索引 | 1243 / 62（62 为已决策跳过） | 阶段 1 已收尾 |
| 页缺口 / 页数不一致 | 0 / 0 | ✅ |
| 最近一片（run-20261014-154016） | attempts 169 / 失败 57 / 0 字节 56（33%）/ 截断 1 / 硬错误 0 | 健康 |
| 总成功率 / 健康率 | 0.663 / 0.997 | 优秀 |
| 封禁指纹 | 0 | ✅ |
| 自适应 delay / 片间冷却 | 3.0 s / 60 s | 维持 |
| 速率 / ETA | 7.6 页/分 · **68.3 小时** | — |
| 采集进程 / 守护进程 | 均存活（pythonw.exe） | ✅ |
| `logs/ALERT.json` / `STOP` / `EXHAUSTED.json` | 均不存在 | 无需人介入 ✅ |
| 心跳 `logs/heartbeat.json` | ts 与当前差 < 1 min | ✅ |

四层冗余逐层核验（2026-10-14 15:55）：

| 层 | 实测 | 状态 |
|---|---|---|
| 1 计划任务 `MalaysiaYP-FullCrawl` | State=Ready，LastRun 15:46:56，LastTaskResult=0，NextRun 16:06:55，Missed=0 | ✅ |
| 2 常驻守护 `supervise.py` | PID 10548 存活；采集进程 PID 11540 存活 | ✅ |
| 3 启动文件夹 | `malaysiayp-crawl-autostart.vbs` + `start_watchdog.vbs` 均在 | ✅ |
| 4 WorkBuddy automation | **本次巡检时 `automation_update list` 返回空** → 已新建「malaysiayp 全量采集 · 每小时监督」补齐 | 已修复 |

交付物已于 15:56 刷新：`data/deliverable/` 4 CSV（all 48,853 行 / mobile 6,917 行 / extended 48,853 行 / quarantine 1,845 行）+ `README.md` + `meta.json`。

# 未核实项

- 站点返回 `200 + 0 字节` 的比例在 2026-10-14 15:53 那片为 **33%**（全量累计：带错误页 2245，其中 2157 为 0 字节；`business-services` 989 页报错 / 988 页 0 字节，`automotive` 445/440，`apparel` 424/420），集中在深页（如 `business-services/page/1950+`）。怀疑是「枚举出的页数超过分类实际页数」。未验证，未针对优化——这批空页仍会消耗重试预算，是当前吞吐的主要天花板。
- **「4 层冗余」中的 WorkBuddy automation 层是否真缺失未定论**：KB v2.1.0 记载存在「malaysiayp 采集健康检查」automation，但 2026-10-14 15:54 在本会话 `automation_update list` 返回空数组。可能是该 automation 属于另一 workspace 作用域（本工具列表按作用域过滤），也可能是已被删除。本次已新建一个补齐；若两者同时生效，会产生两条每小时的只读巡检（幂等、无害，但重复）。待下次巡检确认是否只有一条。
- 「心跳 70 分钟未刷新 = 停摆」是拍的阈值（须 > 单片 50 分钟 + 收尾余量），未在真实停摆场景复核。
- 主机睡眠对计划任务的补跑行为未验证（`StartWhenAvailable=true` 理论上会补）。
- ETA 68.3 小时（7.6 页/分 × 31,134 待处理页）是**按当前 0 字节缺陷比例外推**；若站点持续劣化（0 字节比例上升），ETA 会被系统性低估。
