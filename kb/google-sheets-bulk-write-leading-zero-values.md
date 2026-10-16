---
id: google-sheets-bulk-write-leading-zero-values
title: Google Sheets 批量写入保留前导零的编号
tags: [Google Sheets, gog, 批量写入, 编号, 前导零]
created: 2026-10-16
updated: 2026-10-16
version: 1
status: stable
source: 本次会话（gog CLI 实测）
confidence: 已核实
---

# 一句话结论

向 Google Sheets 批量写入电话号码、邮编等带前导零的编号时，先生成字符串二维数组，再用 `--input RAW` 写入指定 A1 区间，并核对写入数量及首尾值。

## 可复用操作

1. 确认目标表与范围；写入前读取目标首尾单元格，避免覆盖已有内容。
2. 生成连续、定宽的字符串值。`WIDTH` 设为编号位数，`START` 和 `END` 是去掉前导零后的整数边界，且 `END` 包含在内：

   ```bash
   python -c "import json; start=START; end=END; width=WIDTH; print(json.dumps([[f'{n:0{width}d}'] for n in range(start,end+1)]))" \
   | gog sheets update SPREADSHEET_ID "'工作表名'!B10001:B20000" --values-json @- --input RAW -j
   ```

   将 `START`、`END`、`WIDTH`、`SPREADSHEET_ID`、工作表名和 A1 区间替换为实际值；生成数量须与目标区间行数一致。
3. 检查返回的 `updatedCells` / `updatedRange`，再读取区间首尾，确认前导零、起止编号与行号正确。

## 坑与反直觉

- 默认 `USER_ENTERED` 可能把编号解析为数字并丢掉前导零；写编号用 `--input RAW`。
- API 接收二维数组；单列数据形如 `[["编号1"],["编号2"]]`，不能只传一维列表。
- 范围地址的行号从 1 开始；底层 `sheetId` 请求则使用从 0 开始的索引，二者不要混用。
- 写入前确认目标单元格为空或已获准覆盖；批量更新通常会覆盖指定区间。

## 未核实项

- 不同 gog CLI 版本的参数兼容性需以本机 `gog sheets update --help` 为准。
