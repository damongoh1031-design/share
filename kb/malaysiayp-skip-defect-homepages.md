---
id: malaysiayp-skip-defect-homepages
title: malaysiayp 全量采集 · 跳过缺陷首页的合规机制
tags: [malaysiayp, 全量采集, 缺陷页, 优先级重排, 断点库]
created: 2026-10-12
updated: 2026-10-12
version: 1.0.0
status: stable
source: 本会话实测（2026-10-12）+ 脚本源码核对
confidence: 已核实
---

# 一句话结论

malaysiayp 全量采集里，被 B 型坏缓存锁死的未索引分类首页会每轮被 `prioritize.py` 强制拉回队首、每 20 分钟空耗一次重试。**跳过它们唯一合规的做法是给 `prioritize.py` 的队首查询加 `AND error=''`**——只动 `pages.not_before`，不碰 `categories`/`status`/`attempts`，可逆。

# 背景与判据

| 项 | 结论 |
|---|---|
| 缺陷类型 | B 型坏缓存：Content-Length: 32768 截断 / 持续 0 字节，Etag 恒定，绕过手段全失效，恢复 ≥ `s-maxage=86400`（24h） |
| 卡死表现 | 62 个未索引分类首页 `number=1` 全部带 `error`，`index_state<>'done'`；每轮被 prioritize 置顶 `-1000` 重试，坐不满 25h 复检窗 |
| 子页现状 | 这 62 个分类在 `pages` 表**只有首页、无子页**（子页须首页成功读页数后才入队）→ 跳过后数据不可回收，接受为永久缺口 |
| 终态影响 | 阶段1 判据 `index_state='done'=1243` 不可达；实际天花板 = 1181 已索引 + 62 跳过 |

# 关键机制（脚本核对，2026-10-12）

- `supervise.py` **只读** `not_before`，不自行拉首页；首页置顶**只由 `prioritize.py` 做**。
- `prioritize.py` 原队首查询：`status='pending' AND number=1 AND attempts<? AND category IN (SELECT name FROM categories WHERE index_state<>'done')`，**不看 error** → 缺陷首页每轮被拉回。
- `defer_defects.py` 只把 `not_before` 推到未来（attempts 阶梯 +30min/+6h/+25h），是设计内的延期复检，不是删除。

# 可复用操作

```bash
DIR="C:/Users/Admin/WorkBuddy AI/2026-10-07-16-32-42/phone-directory"
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"

# 1) 备份（改前必做）
cp "$DIR/prioritize.py" "$DIR/prioritize.py.bak-skipdefect-YYYYMMDD"

# 2) 编辑 prioritize.py 队首查询，加 AND error=''
#    原：WHERE status='pending' AND number=1 AND attempts<?
#        AND category IN (SELECT name FROM categories WHERE index_state<>'done')
#    改：WHERE status='pending' AND number=1 AND attempts<? AND error=''
#        AND category IN (SELECT name FROM categories WHERE index_state<>'done')

# 3) 应用并验证
"$PY" "$DIR/prioritize.py" --apply      # 期望「未索引分类首页（提前）0 页」
"$PY" "$DIR/defer_defects.py" --apply   # 缺陷页按阶梯延期

# 4) 回滚（恢复每轮拉首页的旧行为）
cp "$DIR/prioritize.py.bak-skipdefect-YYYYMMDD" "$DIR/prioritize.py"
```

回滚后 `prioritize --apply` 会再次把 62 首页拉回队首——如需重新尝试这 62 个分类，先回滚再跑。

# 坑与反直觉

- **`not_before` 单次改写不持久**：即便手动把 62 首页推到未来，`prioritize.py` 下一轮仍会因 `nb > EPOCH_TOP` 把它们重新置 `-1000`。要真正「跳过」，必须改 `prioritize.py` 查询本身，不能只靠一次性 UPDATE。
- **硬约束只放行 `pages.not_before` 经 prioritize/defer 写入**：直接改 `categories.index_state`、改 `pages.status`/attempts 均属越权，会导致断点损坏、且不可回滚。
- **编辑 `prioritize.py` 不触发计划任务批处理跳字节**：被计划任务执行的批处理是 `scheduled_crawl.cmd`/`task_slice.cmd`，`prioritize.py` 仅由监督自动化调用，可安全编辑（仍先备份）。
- **「跳过」≠「删除」**：62 首页仍 `pending` 带 `error`，`defer_defects` 继续按 25h 阶梯延期；若缓存某天恢复、抓取成功 → `index_state` 变 `done` → 自动退出跳过态。

# 未核实项

- 62 个 B 型坏缓存首页是否会在 24h 后批量恢复（历史 `probe_recover` 恢复率 0–10%，倾向「不恢复」）。若后续复检恢复率 >30%，可考虑放宽延期阶梯或回滚本跳过策略。
- 站点是否对这 62 分类在源站侧已下架/更名（C 型不存在），需 `probe_recover` + 状态码核对后方能定性。
