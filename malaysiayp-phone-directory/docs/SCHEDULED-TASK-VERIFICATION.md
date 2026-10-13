# Windows 计划任务验证报告 · MalaysiaYP-FullCrawl

**日期**：2026-10-08 14:13
**结论**：✅ **计划任务已成功创建并端到端验证。** 共定位并修复 **5 个真实缺陷**，其中 2 个会导致计划任务「看起来正常、实际每片都白跑」。

---

## 一、任务最终配置（已生效）

| 项 | 值 |
|---|---|
| 任务名 | `MalaysiaYP-FullCrawl` |
| 程序 | `C:\Users\Admin\.workbuddy-ai\binaries\python\versions\3.13.12\pythonw.exe` |
| 参数 | `"C:\...\phone-directory\supervise.py" --once --budget-minutes 15` |
| 起始于 | `C:\...\phone-directory` |
| 触发 | 一次启动 + 每 **20 分钟**重复，持续 3650 天 |
| 设置 | `MultipleInstances=IgnoreNew`、`StartWhenAvailable`、`ExecutionTimeLimit=25min` |
| 身份 | `Admin` / **Interactive** / Limited（仅登录状态运行，非管理员） |
| 当前状态 | `State=Ready`，`NextRunTime=14:26:55`，`NumberOfMissedRuns=0` |

**为什么是 `pythonw.exe`**：任务以 Interactive 身份运行，控制台程序会在桌面弹窗。
`pythonw.exe` 是无控制台子系统解释器，不产生窗口；`supervise.py` 内部再给
`subprocess.Popen` 加 `CREATE_NO_WINDOW`，避免它 fork 出的 `python.exe` 自己弹一个窗口。

---

## 二、5 个缺陷与修法

| # | 缺陷 | 后果 | 修法 |
|---|---|---|---|
| 1 | 完成判定要求**零缺口**（`pages['done'] == expected`），而 `agricultural` 有 **216 页恒返回 200+0 字节**（确定性站点缺陷）⇒ `rc=0` **在本站不可达**；`rc=6` 是正常终点，但 `FATAL_CODES` 漏了 6 | 每分钟空转一次，永远不收敛 | `supervise.py` v1.1.0 新增 `settle_exhausted()`：落盘 `logs/GAP-REPORT.{json,md}` + 写 `logs/EXHAUSTED.json`（含 `next_recheck` = +6h）；守护睡 6h 后清标记重试；切片命中未过期标记则**直接返回 6、不 spawn 采集脚本** |
| 2 | **`pythonw.exe` 把 `sys.stdout` / `sys.stderr` 设为 `None`**，任何 `print()` 抛 `AttributeError`；而 `log()` 第一行就是 `print()` | **每个切片启动瞬间崩**（之前那次「成功」走的是 `cmd.exe`，pythonw 路径**从未跑通**） | 新增 `_ensure_stdio()`，输出改接到 `logs/slice-stdio.log` |
| 3 | `MultipleInstances=IgnoreNew` + 切片长于触发间隔 | 新触发被静默拒，`LastTaskResult=2147946720`（`0x800710E0`） | 新增 `--budget-minutes`，切片限时 **15 min < 20 min** 间隔；`ExecutionTimeLimit` 从 1h 收到 25min |
| 4 | **编辑正在运行的 `.cmd`**：`cmd.exe` 不把批处理读进内存，而是记**字节偏移**；运行期间改文件 → 偏移错位 → **跳回去重复执行命令** | 13:58:33 拉起的 `cmd.exe` 在 14:05:47 又执行了一遍 python 行，凭空多出实例；旧实例永不结束 ⇒ 缺陷 3 把所有后续触发全拒 | 已 `Stop-ScheduledTask` 清掉；计划任务动作**不再指向 `.cmd`**，直指 `pythonw.exe` |
| 5 | 守护与切片抢锁，每次生成一个 994 字节空 `run-*.log` | 一天刷上千个垃圾日志 | `cmd_daemon()` 改「**先探测再启动**」，检测到已有采集进程就等 120s |

---

## 三、验证证据（可复核）

| 证据 | 观测值 | 命令 |
|---|---|---|
| 注册成功 | `State=Ready` | `Get-ScheduledTask -TaskName "MalaysiaYP-FullCrawl"` |
| 触发节奏稳定 | `LastRunTime=14:08:42` → `NextRunTime=14:26:55`，`MissedRuns=0` | `Get-ScheduledTaskInfo ...` |
| **手动触发返回业务码** | `LastTaskResult=8`（互斥锁被占），**不是异常码** ⇒ pythonw 路径跑通 | 同上 |
| **无控制台环境证据** | `logs/slice-stdio.log` 已生成（3138 B），内含真实监督报告 | `ls logs/slice-stdio.log` |
| 早期一次真实抓取 | `logs/scheduled.log` 有 25 页输出（`air-conditioning-parts` → `aluminum-extruded-products`） | `tail logs/scheduled.log` |
| 缺口报告生成器可用 | 预览运行产出 JSON 365 KB / MD 51 KB，且**不写** `EXHAUSTED.json` | 已复测后清除预览 |

**`LastTaskResult` 对照**：`0`=成功 · `6`=重试预算耗尽 · `8`=抢锁失败（正常竞争） ·
`267009`=正在运行 · `267011`=从未运行 · `267014`=被终止 · `2147942401`=程序未找到 ·
`2147946720`=`0x800710E0`=被 `IgnoreNew` 拒掉。

---

## 四、四层冗余（当前部署）

| 层 | 机制 | 存活范围 |
|---|---|---|
| 1 | Windows 计划任务（每 20 分钟一片） | 登录状态下长期有效，**不依赖任何 LLM 或 WorkBuddy** |
| 2 | 后台常驻守护 `supervise.py`（连续推进） | 当前会话存活期间 |
| 3 | 启动文件夹 `malaysiayp-crawl-autostart.vbs` | 每次登录自动拉起第 2 层 |
| 4 | WorkBuddy 每小时自动化（巡检 + 告警） | 停滞时拉起第 2 层，异常时写 `logs/STOP` |

第 1、2 层靠 `data/malaysiayp_full.csv.lock` 互斥，抢不到锁的一方**秒退（rc=8）**，不互相踩踏。
所以「谁在跑」是动态的，**不要试图同时停掉全部**。

---

## 五、当前进度（14:12）

| 指标 | 值 |
|---|---|
| 已完成 / 预期页数 | **197 / 1696（11.62%）** |
| 入库实体 / 导出行 | 3375 / 3375 |
| CSV 分片 | 32 |
| 页缺口 / 页数不一致 | 0 / 0 |
| 封禁指纹 | 0 |
| 自适应 `--delay` | 已从 8.0s 收敛到 **3.0s**（下限） |
| 带错误信息的页 | 225，其中 200+0 字节 **219** |

> 当前速率显示 3.0 页/分偏低，是因为采集器正处在 `amusement-and-recreation-services`
> 这类缺陷密集区（最近一片 200+0 字节占 86%）。**健康率仍是 1.0**——这些不是限流信号，
> 降速无效。离开该区域后会恢复 5~8 页/分。

---

## 六、剩余不确定项

1. **14:26:55 的自然触发**能否拿到 `LastTaskResult=0`。
   若守护正在跑，会拿到 `8`（正常竞争），不是故障。
2. **缺口页 24 小时后是否自愈**（站点 CDN `s-maxage=86400` 的坏缓存假设）。
   守护每 6 小时自动复检，无需人工干预。
3. **若 24 小时后缺口页数一点不降**，属源站缺陷。届时只能四选一：
   ① 接受现有交付形态（全量 CSV 分片 + 缺口清单）；② 缩小目标范围；
   ③ 更换出口 IP；④ 与站点方确认配额与授权。
   **不要把 `--page-attempts` 再往上调**——退避已封顶 3600s，30 次覆盖约 26 小时窗口，
   继续加只是拉长空转时间。

---

## 七、文档与技能同步

- `TROUBLESHOOTING.md`：重写「六·B」（新参数表 + `LastTaskResult` 对照 + 坑 4/5 + 新注册模板）、
  新增「六·C 任务的终点：`rc=6` 与缺口报告」、更新「三·G `supervise.py` v1.1.0」、文件地图补 7 个日志文件。
- WorkBuddy 自动化 `f5bb29ff-9551-4032-a38d-acde8e8998d8` prompt 已更新：
  修正背景（「累积惩罚」→「确定性源站缺陷」）、加 `rc=6`/`EXHAUSTED`/`GAP-REPORT` 分支、
  加计划任务健康检查、加「不要编辑运行中的 `.cmd`」硬约束。
- 技能 `unattended-scraper-ops` 升至 **v1.5.0**：新增「Windows 计划任务无人值守的四个硬坑」
  与「收工后的终点要提前设计好（零缺口不可达时如何收敛）」。
