---
id: malaysiayp-dns-recovery
title: MalaysiaYP DNS 瞬时失败与告警闭锁恢复
tags: [malaysiayp, dns, recovery, watchdog]
created: 2026-10-27
updated: 2026-10-27
version: 4
status: implemented-runtime-verification-in-progress
source: local-job-heartbeat-alert-code-and-live-network-probes
confidence: high
---

# 一句话结论
已核实：按用户16:58修复授权，已实施有限网络重试与守护退避，21项新增回归及97项原有自检全部通过；实际UA robots预检允许，旧告警和心跳先备份再归档，经现有计划任务拉起单守护与采集进程。17:08心跳持续更新，实际页面增量仍需验收，不能仅凭进程存在称数据恢复。

## 分节正文

| 证据（2026-10-27） | 结论 | 口径 |
|---|---|---|
| job.json：getaddrinfo failed、exit_code=3、completion=false | 当次 robots 获取发生解析错误；不等于 robots 明确禁止 | 已核实 |
| Windows Resolve-DnsName 与 Python socket 返回 45.32.125.191 | 当前可解析目标域名 | 已核实，单轮探测 |
| Python urllib robots.txt 返回 HTTP 200，432 字节 | 当前同款解释器能完成 DNS/TLS/HTTP | 已核实，单次请求 |
| ALERT.json 仍保留 15:08 rc=3，heartbeat 仍停在 15:08 且 crawler_alive=false | 守护已停止，历史告警触发 watchdog 闭锁 | 已核实，2026-10-27 16:57 |
| 本轮只读进程枚举未发现匹配的 Python 采集/守护进程；MalaysiaYP-FullCrawl 状态 Ready | 没有证据显示守护当前运行；任务 Ready 不等于在跑 | 已核实，2026-10-27 16:57 |
| `check_robots()` 对 DNS/连接/超时做最多3次重试并加 transient-network 标记；`supervise.py` 匹配标记才退避 | 代码有修复逻辑；这不代表修复后已通过运行时采集验证 | 已核实，代码检查 |
| 离线自测记录称 97 项通过 | 仅证明自测；不能验证网络分支或守护恢复路径 | 已核实，零网络测试 |
| 本次 ALERT 与 heartbeat 仍显示 14020 done、20327 pending、218384 entities | 状态仍冻结在故障时快照 | 已核实，非实时数据 |

无法归因到路由器、运营商、休眠唤醒、代理或系统 DNS 缓存；需要故障当时的对照测量。不能把瞬时错误称为已定位的底层根因。

## 可复用操作

1. 使用采集解释器复测（PowerShell）：

```powershell
& "C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -c "import socket,urllib.request; print(socket.getaddrinfo('malaysiayp.com',443)); r=urllib.request.urlopen('https://malaysiayp.com/robots.txt',timeout=20); print(r.status,len(r.read()))"
```

2. 本次 16:57 只读复核显示 ALERT 仍存在，心跳历史停在 15:08，当前未发现匹配守护/采集进程，任务 `MalaysiaYP-FullCrawl` 为 Ready。停止证据文件不得由巡检自动清除；先确认文件版本与实际 robots 策略、磁盘可用空间，并确认无活进程。
3. 仅在用户明确授权恢复后，备份并归档旧 `ALERT.json`（与 STOP 如存在），再通过计划任务宿主启动，避免从 Agent shell 直接 spawn；然后检查新心跳、进程单例与实际进度。不要直接使用 `Start-ScheduledTask`，先核实任务动作确实对应有效恢复入口。
4. 永远不手改、移动或删除 data 下的 .sqlite3、.parts、.job.json、.lock。

## 坑与反直觉

- 当前 DNS 已成功，不应先改全局 DNS、固定 hosts/IP、关闭 TLS 或跳过 robots。
- 已核实代码：check_robots 对临时 DNS/超时/连接异常最多请求3次，间隔约2/4秒并带抖动；耗尽返回 [transient-network]。HTTP错误、证书错误、无效正文与明确拒绝不放行。
- 已核实代码：supervise.py 仅在 rc=3 且 job phase=environment_error、last_error 含稳定标记时做60/120/240秒退避；第4次仍失败才告警。此逻辑尚无本次运行日志证明已在常驻进程中生效。
- 已核实：ALERT 是持久闭锁；网络恢复不会自动移除它。
- 明确 robots 拒绝保持停止；DB/磁盘错误保留人工告警。只有经过分类且预检通过的网络告警才能自动恢复，不能一律清告警。
- 建议为网络错误保留解析目标、异常链、重试次数、下次探测时间，避免全部折叠为 rc=3。
- 上一次同步确实产生提交，只是 CSV 无变化；“没有新增数据”和“没有提交”是不同概念。

## 未核实项

- DNS 故障的底层来源与持续时间；历史单次探测不能代表当前网络稳定。
- 17:01左右实际采集UA robots检查允许；17:05已备份归档ALERT.json、ALERT.md与heartbeat.json，STOP不存在且未清除任何人工STOP。
- 17:06进程核实：单守护PID1868，采集PID6452；17:08心跳crawler_alive=true。当前进程状态不是长期存活保证，实际页面增量需后续验收。
- 未修改系统DNS/hosts/TLS，未手工编辑断点；采集程序正常更新自身断点属于恢复后的预期行为。
- 长时间网络中断在预算耗尽后仍需人工告警处理；本次不实现无限重试或自动清所有ALERT。
