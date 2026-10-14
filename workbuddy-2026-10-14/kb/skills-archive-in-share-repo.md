---
id: skills-archive-in-share-repo
title: 用户级 skills 归档位置与增量更新方法
tags: [skills, 归档, github-sync, share仓库]
created: 2026-10-14
updated: 2026-10-14
version: 1
status: active
source: 本次归档实操（2026-10-14）
confidence: 已核实
---

# 一句话结论

本机全部用户级技能（50 个 skill 目录）归档在 GitHub 仓库 `damongoh1031-design/share` 的 `workbuddy-migration/skills/` 下；新增/更新技能时只需用 github-sync 按差异文件推送，无需整包重传。

# 归档现状（2026-10-14）

| 项 | 值 |
|---|---|
| 仓库路径 | `workbuddy-migration/skills/`（50 个 skill 目录 + `malaysia-phone-osint.zip`） |
| 元数据 | 同目录 `workbuddy-migration/manifest.json`、`README.md`（含计数与 changelog） |
| 已排除 | `github-sync/_work`（git clone）、`token.txt`、`__pycache__` |
| 最新 commit | `afa1601`（新增 mcp-nixos；更新 github-sync；刷新计数） |

# 增量更新操作

单个技能新增或改动后，一条命令推送（支持多组 `--src/--dest` 配对，一次一个 commit）：

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"
SK=".workbuddy-ai/skills/github-sync"
# 新技能整体入库
"$PY" "$SK/scripts/sync.py" --src "C:/Users/Admin/.workbuddy-ai/skills/<新技能>" --dest "workbuddy-migration/skills/<新技能>" -m "add <新技能>"
# 技能内文件更新（示例：github-sync 的 SKILL.md）
"$PY" "$SK/scripts/sync.py" --src "<skill>/SKILL.md" --dest "workbuddy-migration/skills/<skill>/SKILL.md" -m "update <skill>/SKILL.md"
```

推送前两步检查：
1. `find <src> -name "token.txt" -o -name "*_work*" -o -name "__pycache__"` 必须为空。
2. `grep -rniE "(ghp_[A-Za-z0-9]{20,}|password.*[:=])" <src>` 无真实凭据命中（代码里的 `password` 参数名不算）。

# 坑与反直觉

- `rm -rf` 大目录（>50 文件）会被工作区安全策略拦截，别用整包暂存再删的做法；按差异文件推送最稳。
- 整包 copytree 会在 2 分钟沙箱超时被杀，须后台任务。
- 归档里 `malaysia-phone-osint/references/*` 含第三方号码探测记录，仓库 public，已在库中，新增同类数据前先提醒用户。

# 未核实项

- 用户级 skills 与归档的差异仅在需要时逐目录 `diff -rq` 比对（本次已全量比对，仅 github-sync 有差异）。
