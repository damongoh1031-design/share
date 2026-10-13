---
id: malaysiayp-crawl-supervision-runbook
title: malaysiayp 全量采集 · 每轮监督运行手册（判活、判停滞、读状态）
tags: [malaysiayp, 全量采集, 监督自动化, 计划任务, 断点库, supervise]
created: 2026-10-13
updated: 2026-10-13
version: 1.0.0
status: stable
source: 本会话多轮实测（2026-10-08 ~ 2026-10-13）
confidence: 已核实
---

# 一句话结论

判定采集「是否在推进」**不要看 `supervise.py --status` 的「采集进程存活」字段，也不要用 PowerShell 查计划任务**（两者都不可靠）。可靠判据只有两个：`logs/supervise.log` 里「启动采集片」的时间戳，以及 `--status` 的「空闲时长」相对 15 分钟阈值。

# 判活三法（按可靠性排序）

| 方法 | 可靠性 | 用法 |
|---|---|---|
| `grep "启动采集片" logs/supervise.log \| tail -3` | ✅ 最可靠 | 计划任务每 20 分钟在 `:06/:26/:46:55` 触发一片。看到连续时间戳即调度器在岗 |
| `--status` 的「空闲时长」+「最后一页落盘时间」 | ✅ 可靠 | 空闲 <15 min = 推进中；≥15 min 且无新片 = 停滞 |
| `--status` 的「采集进程存活」 | ❌ 常误报 | 片跑完退出、下一片未启动时会显示 False，实际完全正常 |

## 验证新片的实操（跨触发点等待法）

```bash
DIR="C:/Users/Admin/WorkBuddy AI/2026-10-07-16-32-42/phone-directory"
cd "$DIR"
# 若当前时间接近 :06/:26/:46 的 :55，等 45 秒即可确认新片落盘
sleep 45
grep "启动采集片" logs/supervise.log | tail -2
ls -t logs/run-*.log | head -1     # 应出现 run-YYYYMMDD-HHMMSS.log
```

# 各状态字段的真实口径

| 打印字段 | 真实含义 | 坑 |
|---|---|---|
| `分类 已索引/待索引 1243 / 62` | 实际是 **总分类 / 待索引** | 已索引 = 1243 − 62 = **1181**；不要直接读第一个数 |
| `已完成 / 预期页数` | done / `pages_queued_known` | 会**低估**总量（只含已索引分类），必须同时报 `estimated_true_pct` |
| `有效进度（剔除延期页）` | done / (总 − 延期) | 这是最诚实的进度口径 |
| `其中已延期(缺陷页)` | B 型坏缓存页，按阶梯推迟 | 单轮 +>50 才告警扩散 |
| `页缺口 / 页数不一致` | 索引完整性 | >0 才告警 |

# 每轮固定动作（顺序不可换）

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"
DIR="C:/Users/Admin/WorkBuddy AI/2026-10-07-16-32-42/phone-directory"
cd "$DIR"

# 0) 停止开关
[ -e logs/STOP ] && echo "STOP_EXISTS → 只简报，不推进"

# 1) 优先级维护（只写 pages.not_before，设计内可逆）
"$PY" prioritize.py --apply

# 2) 缺陷页分层延期（幂等，不会无限推后）
"$PY" defer_defects.py --apply      # 阶梯 1→+30min / 2→+6h / ≥3→+25h

# 3) 只读报告 + 刷新交付物
"$PY" supervise.py --status
"$PY" export_deliverable.py --quiet
cat data/deliverable/meta.json      # 取 estimated_true_pct + 各文件行数
```

## 分支决策

| 条件 | 动作 |
|---|---|
| `completion=True` | 收工，报导出行数 |
| 未完成 + 空闲 <15 min | **不启动第二实例**（互斥锁只返回 rc=8，纯浪费配额） |
| 未完成 + 空闲 ≥15 min + 无新片 | 查 `logs/EXHAUSTED.json`：存在且未过期 → rc=6 正常收敛，只简报；否则后台拉起 `supervise.py` |
| 可抓取 =0 且延期 >0 | 正常延期等待态，**不拉起守护** |

# 坑与反直觉

- **PowerShell / `schtasks` 查计划任务在本机返回空 stdout**（`Get-ScheduledTask`、`Get-ScheduledTaskInfo`、`schtasks /query` 均失效，加 `dangerouslyDisableSandbox` 也一样）。**不要**据此判定「计划任务层失效」，改看 supervise.log。
- **`logs/scheduled.log` 是 Oct 8 的历史残留**（末尾 rc=7），不代表当前状态，别当证据。
- **不要用 `nslookup` 判站点可达性**：实测 nslookup 报 `Server failed` 而同刻脚本跑出 rc=9。以脚本 rc 为准。
- **rc=3 时 `supervise.log` 的「可能被互斥锁挡住」是误导文案**，真因在同分钟 run log 的 `ERROR environment_error` 行（如 DNS `getaddrinfo failed`）。
- **根因消除后务必删 `logs/STOP`**，否则后续轮次按「STOP=只简报」会掩盖真实恢复。
- **`--status` 的「速率 / ETA」在片间空隙会显示 `0.0 页/分 · 未知`**，不是故障。
- **主机睡眠会造成跨夜大空档**（已发生 3 次：Oct 8→9、Oct 9→12、Oct 12→13，最长 63.5h）。判停滞前先排除睡眠。

# 未核实项

- 计划任务查询工具为何返回空 stdout（怀疑沙箱/权限限制），未深究； supervise.log 替代法已足够。
- 「空闲 15 分钟」阈值为任务设定值，未在站点侧验证过最优解。
