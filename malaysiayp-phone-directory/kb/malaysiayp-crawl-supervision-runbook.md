---
id: malaysiayp-crawl-supervision-runbook
title: malaysiayp 全量采集 · 无人值守运行手册（常驻守护 + 看门狗 + 告警）
tags: [malaysiayp, 全量采集, 无人值守, 守护进程, 看门狗, 计划任务, supervise, watchdog]
created: 2026-10-13
updated: 2026-10-14
version: 2.0.0
status: stable
source: 本会话多轮实测（2026-10-08 ~ 2026-10-14），2026-10-14 架构改造后复测通过
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

# 未核实项

- 站点返回 `200 + 0 字节` 的比例约 29%（2026-10-14），集中在 `business-services` / `automotive` / `apparel` 等分类的深页（如 `page/265/`），怀疑是「枚举出的页数超过分类实际页数」。未验证，未针对优化——这批空页仍会消耗重试预算，是当前吞吐的主要天花板。
- 「心跳 70 分钟未刷新 = 停摆」是拍的阈值（须 > 单片 50 分钟 + 收尾余量），未在真实停摆场景复核。
- 主机睡眠对计划任务的补跑行为未验证（`StartWhenAvailable=true` 理论上会补）。
