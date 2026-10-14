---
id: workbuddy-write-tool-large-content-failure
title: Write 工具大 content 参数被丢弃的故障模式与修复
tags: [workbuddy, 工具调用, Write, 故障排查, 分块写入]
created: 2026-10-13
updated: 2026-10-13
version: 1.0.0
status: stable
source: 本会话实测
confidence: 已核实
---

# TL;DR

WorkBuddy 的 Write 工具在 `content` 参数体积过大（约 >10KB 的 HTML/长文本）时，参数会在序列化阶段被整体丢弃，报错 `missing required parameter(s): content`。**这不是文件系统问题，也不是路径问题。** 修复方式：分块写入 + cat 拼接。

# 故障现象

- 连续调用 Write：`file_path` 有值，`content` 缺失 → `Error: Invalid arguments for Write: missing required parameter(s): file_path, content`
- 用小 content（如 `test`）同路径调用**成功** → 证明工具本身正常，是内容体积触发
- 同会话内反复出现，用户反馈「不是第一次出现」

# 根因判定

1. 先确认是参数缺失而非路径错误：反复出现 `missing ... content` 而非权限/路径错误。
2. 小内容对照实验成功 → 定位到 content 体积阈值。
3. 结论：大 payload 在工具调用序列化/传输中被截断丢弃。

# 可复用操作

```bash
# 1) 分成 4 块各 ~7KB 以内，分别 Write 到 _p1.._p4
# 2) 拼接 + 清理
cat _p1.html _p2.html _p3.html _p4.html > final.html && rm _p1.html _p2.html _p3.html _p4.html
# 3) 校验
wc -c final.html
```

经验阈值：单块 ≤ ~10KB（本次 27.8KB 报告分 4 块，每块 6–9KB，全部成功）。

# 坑与反直觉

- 报错信息只说「缺参数」，完全不提示「内容过长」——容易误判为自己漏传参数，进而反复无脑重试触发循环检测。
- 分块时**后续块不能重复** `<html><head>` 等骨架标签，否则拼接出两份；第 1 块带完整骨架，后续块只写 body 片段。
- Edit 工具同样可能被大字符串影响，修 HTML 优先用分块重写而非大段 Edit。

# 未核实 / 存疑

- 确切的字节阈值未测（未在 8KB/12KB 等边界逐一试探）。
- 是否同样影响其他带长 content 的工具（如 Edit）未实测。
