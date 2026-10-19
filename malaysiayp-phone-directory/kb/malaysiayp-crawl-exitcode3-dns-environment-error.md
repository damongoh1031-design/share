---
id: malaysiayp-crawl-exitcode3-dns-environment-error
title: malaysiayp 全量采集 · exit_code=3 环境错误（DNS 解析失败）的识别与恢复
tags: [malaysiayp, 全量采集, supervise, exit-code, DNS, robots, 故障排查, STOP开关]
created: 2026-10-13
updated: 2026-10-19T12:25
version: 1.2.0
status: stable
source: 本会话实测（2026-10-13、2026-10-16 停机、2026-10-19 12:22 实际清告警恢复；run log + supervise.log + ALERT.json + socket.gethostbyname 验证）
confidence: 已核实
---

# 一句话结论

`supervise.py --status` 报 `phase=environment_error / exit_code=3` 时，**根因是本采集机 DNS 解析失败**（`getaddrinfo failed` Errno 11001/11002）导致 robots.txt 前置校验取不到，**不是爬虫脚本、不是限流、不是封禁、不是第二调度器**。

**关键修正（2026-10-19）：rc=3 不会自行恢复。** rc=3 属「不重试」类别，supervisor 写 `logs/ALERT.json` 后自身退出，watchdog 见 ALERT.json 即按设计「不介入」，管线永久停摆 —— 实测停 70 小时（10-16 13:54 → 10-19 12:21）。恢复必须人工删 `logs/ALERT.json`（+`logs/STOP`）再拉守护。恢复判据是**最新一片 run log 的 rc**，不是 `nslookup`。

# 判据（2026-10-13 实测）

| 观察点 | 故障态 | 恢复态 |
|---|---|---|
| `supervise.py --status` | `job phase / exit_code = environment_error / 3` | `chunk_paused / 9` |
| run log 末行 | `ERROR environment_error：robots不允许或无法确认：无法获取 robots.txt：<urlopen error [Errno 11001] getaddrinfo failed>；退出码3` | `INFO [全量任务] chunk_paused；退出码9` |
| supervise.log | `本片 rc=3 {"success_ratio": null, "health_ratio": null} \| 本片未发出请求（可能被互斥锁挡住）` | `本片 rc=9 {"attempts": 14, "success_ratio": 0.143, "health_ratio": 1.0}` |
| 产出 | done 停滞、空闲时长持续上涨 | done 1976→1978、入库 25385→25425 |

时间线（2026-10-13）：13:27 / 13:47 / 14:07 三片 rc=3 → **14:26 片恢复 rc=9**。故障持续约 1h20m，跨 4 个调度周期。调度器 `MalaysiaYP-FullCrawl` State=Ready、`LastTaskResult=3`，`WBProbe3`=Disabled，无第二调度器、无 rc=7。

# 停机链条（2026-10-19 复现，已核实）

| 时刻 | 事件 | 证据 |
|---|---|---|
| 10-16 13:26 起 | 站点对深层分页大量返回 200 + 0 字节，单片成功率跌到 0.0 | `supervise.log` 本片 rc=9 `zero_ratio 1.0` |
| 10-16 13:54:07 | 一次瞬时 DNS 失败落在 robots 校验阶段 → `environment_error`，exit 3 | `logs/run-20261016-134200.log` 末行 |
| 10-16 13:54:09 | supervisor 判 rc=3 为致命，不重试，写 `logs/ALERT.json`，守护退出 | `supervise.log`「致命退出码 3…已写入 ALERT.json」 |
| 10-16 14:06 → 10-19 12:06 | watchdog 每 20 分钟跑一次，见 ALERT.json 即跳过 | `watchdog.log`「守护在等人工处理，看门狗不介入」×~200 |
| 10-19 12:13 | 数据零增量，`source_db_mtime` 仍为 10-16 13:54 | `meta.json` |

**设计缺陷**：把瞬时 DNS 抖动判为不可重试的致命错误，且看门狗对 ALERT 采取完全被动策略 → 单次瞬时故障等于永久停机。

# 实际恢复执行（2026-10-19 12:22，已核实）

| 步骤 | 操作 | 结果 |
|---|---|---|
| 1 | 读 `logs/ALERT.json` | 存在，rc=3，ts=2026-10-16 13:54:09，挂起 ~70h |
| 2 | 定位真实原因（run log 末行） | `ERROR environment_error：无法获取 robots.txt：<urlopen error [Errno 11001] getaddrinfo failed>` |
| 3 | 排除磁盘/DB | 磁盘剩 245.67 GB；`data/malaysiayp_full.csv.sqlite3` 存在、71.2 MB、可写 → **非磁盘/DB 损坏** |
| 4 | 验证 DNS 是否已恢复 | Python `socket.gethostbyname('malaysiayp.com')` → `45.32.125.191`，0.10s（**单次解析，非批量探测，不触限流**） |
| 5 | 清告警 | `rm -f logs/ALERT.json`（STOP 本就不存在）；确认文件已消失 |
| 6 | 续跑 | 不手启守护、不动 `data/` 断点；计划任务 `MalaysiaYP-FullCrawl` 每 20 分钟唤醒 watchdog，下一轮（≤20 分钟）自动拉起守护续跑 |
| 7 | 确认恢复（12:26:57） | watchdog 本轮判定停摆并自动拉起守护 `pid=4036`；12:27:01 启动采集片；12:28:02 heartbeat `crawler_alive=true / note="采集中" / idle_minutes=0.0` |

**结论**：本次与 10-13 同源（瞬时 DNS 抖动），但 10-16 那次被 supervisor 判致命 + 写 ALERT → 永久停摆 70h。环境已恢复，清告警即完成修复，watchdog 在下一轮（4 分钟后）自动拉起守护，全程无需手启守护。

**确认恢复的判据**：`heartbeat.crawler_alive=true` + `note="采集中"` + `idle_minutes≈0` + `ALERT.json` 未复现。注意 `phase` / `exit_code` 是上一片的残留字段，本片跑完前仍显示 `environment_error / 3`，**不要据此误判为又坏了**——以 `crawler_alive` 为准。

# 可复用操作

```bash
DIR="C:/Users/Admin/WorkBuddy AI/2026-10-07-16-32-42/phone-directory"
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"

# 0) 先确认停机原因：有无 ALERT.json（有 = rc=3 停机，不是普通 idle）
cat "$DIR/logs/ALERT.json" 2>/dev/null

# 1) 定位真实原因：rc=3 时 success_ratio=null，必须看 run log（supervise.log 的提示是误导）
ls -t "$DIR/logs"/run-*.log | head -1
grep -E "ERROR|environment_error|退出码" "$(ls -t "$DIR/logs"/run-*.log | head -1)"

# 2) 确认是否已恢复（只看脚本，不看 nslookup）
tail -4 "$DIR/logs/supervise.log"          # 期望最新一片 rc=9
"$PY" "$DIR/supervise.py" --status | grep -E "exit_code|最后一页|空闲时长"

# 3) 根因消除后：删 ALERT.json + STOP 即可；watchdog 仍活着，下一轮（≤20 分钟）会自动拉起守护
rm -f "$DIR/logs/ALERT.json" "$DIR/logs/STOP"
# 仅当 watchdog 也不在跑时才需要手动起：cscript //nologo "$DIR/start_watchdog.vbs"

# 4) 恢复常规维护
"$PY" "$DIR/prioritize.py" --apply
"$PY" "$DIR/defer_defects.py" --apply
"$PY" "$DIR/export_deliverable.py" --quiet
```

# 坑与反直觉

- **「rc=3 会自愈」是错的**。2026-10-13 那次是调度器每 20 分钟重试新片、恰好 DNS 已恢复才「自愈」；若 supervisor 判为致命并写 ALERT.json，重试链断掉，等 3 天也不会动。判断是否已死：`ls logs/ALERT.json`。
- **watchdog 见 ALERT.json 就不介入是硬编码行为**，不是故障。它只解决「进程崩了」，不解决「进程按设计停了」。停机超过 1 小时先查 ALERT.json，别查网络。
- **`supervise.log` 的「本片未发出请求（可能被互斥锁挡住）」是误导文案**。rc=3 且 `success_ratio=null` 时不要按互斥锁/抢锁排查，真实原因写在同分钟 run log 的 `ERROR environment_error` 行里。
- **不要用 `nslookup` 单点判断站点可达性**。实测 `nslookup malaysiayp.com` 报 `Server failed`（走 `ns8.maxis.net.my` 的 IPv6 解析失败），而同一时刻 Python urllib 却能取到 robots.txt 并跑出 rc=9。以脚本 rc 为准。但 2026-10-19 实测：**Python `socket.gethostbyname('malaysiayp.com')` 返回 `45.32.125.191`（0.10s）是有效的 DNS 恢复正信号**——它走 happy-eyeballs，不受 nslookup 那条 IPv6 解析路径的干扰。即「nslookup 不可信」≠「DNS 一定没恢复」；用 socket 解析成功可确认环境已好。
- **Errno 11001 与 11002 处置相同**：11001（无法解析主机）与 11002（解析器超时/服务器失败）都在本次故障中出现，均属 DNS 环境错误，不区分处理。
- **STOP 不是硬停机**。STOP 存在期间 14:26 片仍跑出 rc=9（单次观测，机制推断为其检查点在监督流程而非 `--once` 采集路径）。但根因消除后仍要删 STOP，否则后续轮次按「STOP 存在=只简报」误判，掩盖真实恢复。
- **深层分页的 200+0 字节是站点侧缺陷，不是本机限流**。2026-10-19 实测同分类不同页：`page/2` 稳定 36,635 B；`page/900` 两次请求 0 B → 37,446 B（抖动可重试）；`page/10` 两次都是 0 B（稳定空页）。降 delay 无用，只有换页/跳过才有效。

# 未核实项

- DNS 失败的具体触发源未定位（本机网络切换 / ISP DNS 抖动 / IPv6 优先解析失败均可能），仅知 10-13 那次约 80 分钟后自愈。
- 站点 0 字节页的生成规律未建模：已知 `page/2` 正常、`page/10` 恒空、`page/900` 抖动，尚不清楚是按分页槽位缓存空还是源站数据缺失。
- 是否周期性复发：10-13 与 10-16 各一次，间隔 3 天，样本不足。
- STOP 对 `--once` 路径的确切拦截逻辑未读源码确认，仅为单次观测的推断。
