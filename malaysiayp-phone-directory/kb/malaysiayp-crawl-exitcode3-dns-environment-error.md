---
id: malaysiayp-crawl-exitcode3-dns-environment-error
title: malaysiayp 全量采集 · exit_code=3 环境错误（DNS 解析失败）的识别与恢复
tags: [malaysiayp, 全量采集, supervise, exit-code, DNS, robots, 故障排查, STOP开关]
created: 2026-10-13
updated: 2026-10-13
version: 1.0.0
status: stable
source: 本会话实测（2026-10-13 13:27–14:29，run log + supervise.log + 调度器核对）
confidence: 已核实
---

# 一句话结论

`supervise.py --status` 报 `phase=environment_error / exit_code=3` 时，**根因是本采集机 DNS 解析失败**（`getaddrinfo failed` Errno 11001/11002）导致 robots.txt 前置校验取不到，**不是爬虫脚本、不是限流、不是封禁、不是第二调度器**；它会自行恢复。恢复判据是**最新一片 run log 的 rc**，不是 `nslookup`；确认恢复后必须删除 `logs/STOP`，否则采集语义停在「只简报不推进」。

# 判据（2026-10-13 实测）

| 观察点 | 故障态 | 恢复态 |
|---|---|---|
| `supervise.py --status` | `job phase / exit_code = environment_error / 3` | `chunk_paused / 9` |
| run log 末行 | `ERROR environment_error：robots不允许或无法确认：无法获取 robots.txt：<urlopen error [Errno 11001] getaddrinfo failed>；退出码3` | `INFO [全量任务] chunk_paused；退出码9` |
| supervise.log | `本片 rc=3 {"success_ratio": null, "health_ratio": null} \| 本片未发出请求（可能被互斥锁挡住）` | `本片 rc=9 {"attempts": 14, "success_ratio": 0.143, "health_ratio": 1.0}` |
| 产出 | done 停滞、空闲时长持续上涨 | done 1976→1978、入库 25385→25425 |

时间线（2026-10-13）：13:27 / 13:47 / 14:07 三片 rc=3 → **14:26 片恢复 rc=9**。故障持续约 1h20m，跨 4 个调度周期。调度器 `MalaysiaYP-FullCrawl` State=Ready、`LastTaskResult=3`，`WBProbe3`=Disabled，无第二调度器、无 rc=7。

# 可复用操作

```bash
DIR="C:/Users/Admin/WorkBuddy AI/2026-10-07-16-32-42/phone-directory"
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"

# 1) 定位真实原因：rc=3 时 success_ratio=null，必须看 run log（supervise.log 的提示是误导）
ls -t "$DIR/logs"/run-*.log | head -1
grep -E "ERROR|environment_error|退出码" "$(ls -t "$DIR/logs"/run-*.log | head -1)"

# 2) 确认是否已恢复（只看脚本，不看 nslookup）
tail -4 "$DIR/logs/supervise.log"          # 期望最新一片 rc=9
"$PY" "$DIR/supervise.py" --status | grep -E "exit_code|最后一页|空闲时长"

# 3) 根因消除后删除 STOP，交回调度器（每 20 分钟自动续跑）
rm -f "$DIR/logs/STOP"

# 4) 恢复常规维护
"$PY" "$DIR/prioritize.py" --apply
"$PY" "$DIR/defer_defects.py" --apply
"$PY" "$DIR/export_deliverable.py" --quiet
```

# 坑与反直觉

- **`supervise.log` 的「本片未发出请求（可能被互斥锁挡住）」是误导文案**。rc=3 且 `success_ratio=null` 时不要按互斥锁/抢锁排查，真实原因写在同分钟 run log 的 `ERROR environment_error` 行里。
- **不要用 `nslookup` 单点判断站点可达性**。实测 `nslookup malaysiayp.com` 报 `Server failed`（走 `ns8.maxis.net.my` 的 IPv6 解析失败），而同一时刻 Python urllib 却能取到 robots.txt 并跑出 rc=9。以脚本 rc 为准。
- **Errno 11001 与 11002 处置相同**：11001（无法解析主机）与 11002（解析器超时/服务器失败）都在本次故障中出现，均属 DNS 环境错误，不区分处理。
- **STOP 不是硬停机**。STOP 存在期间 14:26 片仍跑出 rc=9（单次观测，机制推断为其检查点在监督流程而非 `--once` 采集路径）。但根因消除后仍要删 STOP，否则后续轮次按「STOP 存在=只简报」误判，掩盖真实恢复。
- **恢复后不要手动拉守护**。调度器每 20 分钟自触发，手动起第二个实例只会抢锁返回 rc=8，白耗配额。

# 未核实项

- DNS 失败的具体触发源未定位（本机网络切换 / ISP DNS 抖动 / IPv6 优先解析失败均可能），仅知持续约 80 分钟后自愈。
- 是否周期性复发未验证（本日仅观测到一次）。
- STOP 对 `--once` 路径的确切拦截逻辑未读源码确认，仅为 14:26 单次观测的推断。
