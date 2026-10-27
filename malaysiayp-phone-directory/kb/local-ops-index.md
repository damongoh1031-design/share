# 知识库索引

| id | 文件 | 主题 | 版本 | 更新 |
|---|---|---|---|---|
| malaysiayp-crawl-ops | [malaysiayp-crawl-ops.md](./malaysiayp-crawl-ops.md) | MalaysiaYP 全量采集 · 无人值守运维与巡检手册（四层冗余、缺陷分类、退出码语义、双守护去重、休眠-唤醒根因、ALERT 误报与保护真空、守护静默死亡与「心跳新≠进程活」盲区、DNS 抖动→rc=3→ALERT 连锁、Task Scheduler 宿主重启法、速率采样法、吞吐归因、状态快照） | v12 | 2026-10-27 |

| malaysiayp-dns-recovery | [malaysiayp-dns-recovery.md](./malaysiayp-dns-recovery.md) | DNS 有限重试修复、118项测试通过、计划任务恢复与进度验收 | v4 | 2026-10-27 |

## 待决事项

- 本工作区 `kb/` 未纳入 `github-sync/config.json` 映射（映射源指向 `2026-10-08-11-47-53/kb`）。仓库内 `malaysiayp-phone-directory/kb/malaysiayp-crawl-supervision-runbook.md`（v2.2.0）与本手册（v11）同主题不同 id，需人工决定合并口径。
- **看门狗判活只看心跳年龄**（已产生三类事故）：① 10-20 `ALERT.json` 误报致 4h 保护真空；② 10-23 守护+采集同时静默死亡、心跳仅停 6 分钟 → 判「健康」不介入；③ 10-27 同样因心跳 3.5 分钟新鲜而空转（守护已死）。建议 `watchdog.py` 改为「心跳新鲜度 + 守护进程数」双判，并给 ALERT 加 TTL / 心跳交叉校验。
- **重启必须走 Task Scheduler 宿主**（10-27 新增硬约束）：从 Agent/IDE shell spawn 的 pythonw 会被 job object 连带回收，表现为无 traceback 静默消失；`schtasks /Run /TN "MalaysiaYP-FullCrawl"` 是唯一可靠路径（需先删心跳让看门狗必定介入）。
- **守护静默死亡根因**：10-27 这批已归因于宿主 job object 回收；10-23 那批仍无解释（无 traceback、无事件日志、三件套全绿）。建议给 `supervise.py` 加 `faulthandler` + 退出钩子写 `logs/daemon-exit.json`。
- **双守护根因未修复**（已复发三轮：10-15 / 10-16 / 10-20）。建议给 `supervise.py` 加守护单例锁，或让 `watchdog.py` 在拉起前统计守护进程数。修复前每次长时间休眠后需手工去重。
- **`rc=3` 分类误导**：`robots.txt` 瞬时网络失败（WinError 10065 / Errno 11004 getaddrinfo）被判为「环境/DB/磁盘错误」并触发致命退出 + ALERT。建议将 robots 获取失败单列为可重试类别（退避 2–3 次）。
- `data/deliverable` 同时是 `github-sync` 同步源 → 非终态期间误跑 export 会把未完成数据公开（已复发 4 次：10-14 / 10-15 / 10-20）。建议在 export 脚本内加 `completion/rc` 前置断言。
- 「高缺陷分类可预测性」：`construction` 遍历前未进缺陷榜、遍历中近 100% 0B —— 现有榜单纯属事后统计，是否值得加抽样预判以整类跳过，待人工评估。
- **0B 缺陷延期阶梯尚未大规模生效**：`defer_defects.py` 设计为 attempts≥3 → +25h，但 10-27 实测 `attempts` 最大值仅 2，13007 个 0B 待处理页仍在热路径上。下次巡检观察 `attempts_hist` 是否出现 `"3"`。
