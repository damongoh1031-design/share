---
id: db1-driver-jsonl-duplicate-recovery
title: DB1 反查驱动器因残留 JSONL 重复行导致写前 assert 中止与幂等恢复
tags: [db1, osint, google-sheets, automation, recovery, 故障排查]
created: 2026-10-09
updated: 2026-10-09
version: 1
status: stable
source: 实测（2026-10-09 批 24 恢复）
confidence: 已核实
---

## 一句话结论

DB1 反查驱动器（`db1_sheet_batch_driver.py`）在写回 A 列前会对每个 found 行 `assert 目标格为空`；如果同批号的 `rN.json.jsonl` 残留了上一轮后台实例的结果，`db1_batch.py` 会把新结果**追加**进去造成重复行，写回循环第二次遇到同一行就触发 `AssertionError: 目标格非空` 整批中止——但实时 A 列该格其实为空（误报），名字并未落表。处置：读实时 A 列确认空格 → 按行号去重得唯一名字 → 只对空目标格幂等补写（C 列不动）→ 回读双校验。

## 现象与根因

| 项 | 内容 |
|---|---|
| 触发条件 | 同一批号 N 的 `rN.json.jsonl` 未被清掉，上一轮后台实例中途被杀后残留 |
| 直接原因 | `db1_batch.py` 向该 jsonl **追加**写入，同一行出现 2 次（实测 100 条命中里 46 行重复） |
| 失败点 | `db1_sheet_batch_driver.py` 写回循环：`vals[i][0]` 第一次已被设成名字，第二次同行动 assert 失败 |
| 退出码 | `exit 1`（**非文档列出的 0/2/3/4/5/6**，是未捕获的 AssertionError） |
| 误导信息 | 报错 `目标格非空 row=7198 ['某名字']` 让人误以为 Sheet 已被写；实测该格为空 |
| 真实后果 | 查询成功、名字**未落表**，autostate/summary 未更新 |

## 可复用操作（恢复步骤）

```powershell
# 0) 探活（1 请求）
"$PY" "$S/db1_batch.py" --probe          # exit 0=解封, exit 2=仍封

# 1) 读实时 A 列目标区间，确认目标格确为空（用真实 Sheet，不用旧快照）
"$GOG" sheets get <ID> "'SHOPEE LIST 01'!A<START>:<LAST>" -j --results-only --render FORMATTED_VALUE > liveA.json

# 2) 对 rN.json.jsonl 按行号去重，得唯一 (row->name)
python -c "import json,collections; ... uniq={f['row']:f['name'] for f in json.loads_lines if f.get('name')}"

# 3) 构造 vals：found 行填名字(仅当实时为空)，其余保留既有值；写盘 colA_recovery.json
# 4) 幂等补写（全区间写，匹配驱动器语义；C 列完全不动）
"$GOG" sheets update <ID> "'SHOPEE LIST 01'!A<START>:<LAST>" --values-json @colA_recovery.json --input RAW -j

# 5) 校验：回读 A 区间 54/54 命中 + 全局 A 非空计数 = 旧值 + 补写数 + C 列逐行 diff 全空
```

## 根治（每次启动驱动器前）

```powershell
Remove-Item "$T/r$batch.json.jsonl" -ErrorAction SilentlyContinue   # 清掉同批号残留
# 再启动驱动器，避免重复行再次触发 assert 中止
```

## 坑与反直觉

- **assert 报「目标格非空」≠ Sheet 真有数据**：这里是同批 jsonl 重复行造成的自命中，实时格为空。
- **驱动器 exit 1 不在文档退出码表**（0/2/3/4/5/6），属于未捕获断言，需手动识别。
- **写前快照（`sheetABN.json`）可能比实时旧**：上一轮后台实例在快照之后才把数据写进 Sheet，故以「实时 gog 读取」为准，不要信启动快照。
- **恢复补写不算「跳过驱动器自己拼命令」的常规绕过**：驱动器本身因重复行无法完成本批，补写是等价的幂等回写（只写空格、保留既有、C 不动）。
- C 列校验必须**逐行 diff**，不能 `== 常数`（已被人工改过 258→264→492）。

## 未核实 / 存疑

- `db1_batch.py` 究竟是「追加」还是「覆盖」写入 jsonl 未源码确认，但残留+本次结果共存的现象表明是追加（或驱动器复用 out 路径未清）。下次清文件后观察一次即可确认。
- 批 24 实际只挖到 54 命中（183 行），疑似该区段号码密度骤降，非 bug；有待继续观察批 25+。
