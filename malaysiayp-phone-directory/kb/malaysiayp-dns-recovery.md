---
id: malaysiayp-dns-recovery
title: MalaysiaYP DNS 瞬时失败与告警闭锁恢复
tags: [malaysiayp, dns, recovery, watchdog]
created: 2026-10-27
updated: 2026-10-27
version: 1
status: verified-diagnosis-proposed-fix
source: local-job-heartbeat-alert-code-and-live-network-probes
confidence: high
---

# 一句话结论
已核实：15:08 的域名解析错误是当次失败点，不能证明 DNS 持续故障；2026-10-27 16:47 左右同机 DNS 与 Python HTTPS 已恢复，当前恢复障碍是历史 ALERT 导致看门狗拒绝拉起。

## 分节正文

| 证据（2026-10-27） | 结论 | 口径 |
|---|---|---|
| job.json：getaddrinfo failed、exit_code=3、completion=false | 当次 robots 获取发生解析错误；不等于 robots 明确禁止 | 已核实 |
| Windows Resolve-DnsName 与 Python socket 返回 45.32.125.191 | 当前可解析目标域名 | 已核实，单轮探测 |
| Python urllib robots.txt 返回 HTTP 200，432 字节 | 当前同款解释器能完成 DNS/TLS/HTTP | 已核实，单次请求 |
| ALERT.json 保留 15:08 环境错误；watchdog.py 遇 ALERT 直接返回 | 网络恢复后仍被人工告警闭锁 | 已核实 |
| 心跳 alive=true 但 crawler_alive=false，时间为15:08 | 历史心跳不能证明当前存活 | 已核实 |
| 计划任务最近触发，但不证明采集进程运行 | Ready/任务返回码不能替代进程与数据增量检查 | 已核实 |

无法归因到路由器、运营商、休眠唤醒、代理或系统 DNS 缓存；需要故障当时的对照测量。不能把瞬时错误称为已定位的底层根因。

## 可复用操作

1. 使用采集解释器复测（PowerShell）：

```powershell
& "C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -c "import socket,urllib.request; print(socket.getaddrinfo('malaysiayp.com',443)); r=urllib.request.urlopen('https://malaysiayp.com/robots.txt',timeout=20); print(r.status,len(r.read()))"
```

2. 复核当前 robots 对实际 User-Agent 和目标路径允许；网络连续探测成功后，备份并归档历史 logs/ALERT.json、logs/STOP（如存在）。核实无存活守护，再失效旧心跳并走计划任务恢复。以下仅为后续恢复入口，不是本次已执行动作：

```powershell
Start-ScheduledTask -TaskName 'MalaysiaYP-FullCrawl'
```

3. 检查新心跳时间、守护单实例、crawler_alive 与页面完成数；页面计数因旧失败页重试暂不增长时，应查看新日志的实际请求与退出原因。
4. 永远不手改、移动或删除 data 下的 .sqlite3、.parts、.job.json、.lock。

## 坑与反直觉

- 当前 DNS 已成功，不应先改全局 DNS、固定 hosts/IP、关闭 TLS 或跳过 robots。
- 建议修复：将 robots 获取失败（DNS/超时）与明确拒绝、DB/磁盘错误分别分类；前者限定次数退避并带抖动，失败仍保持不抓取，不能默认放行。
- 明确 robots 拒绝保持停止；DB/磁盘错误保留人工告警。只有经过分类且预检通过的网络告警才能自动恢复，不能一律清告警。
- 建议为网络错误保留解析目标、异常链、重试次数、下次探测时间，避免全部折叠为 rc=3。
- 上一次同步确实产生提交，只是 CSV 无变化；“没有新增数据”和“没有提交”是不同概念。

## 未核实项

- DNS 故障的底层来源与持续时间；当前成功不保证长期稳定。
- 本次没有清告警、重启采集、修改系统网络或修改采集代码；自动恢复方案尚未实施。
- 重新采集前需复核实际 User-Agent 的 robots 判定与调度单例。
