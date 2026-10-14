---
id: github-sync-skill-migration
title: github-sync 技能与 GitHub PAT 跨工作区迁移
tags: [github-sync, skill-migration, pat, workbuddy, 凭据管理]
created: 2026-10-14
updated: 2026-10-14
version: 2
status: active
source: 旧工作区 2026-10-14-10-26-42/workbuddy-migration 迁移包实测
confidence: 已核实
---

# 一句话结论

`github-sync` 技能 + 经典 PAT（scope=repo）可从旧工作区的 `workbuddy-migration` 包整体迁入新工作区 `.workbuddy-ai/skills/github-sync/`，改 `config.json` 的 `mappings[].src` 指向新工作区后用 `curl /user` 验 token、`sync.py` 验同步，即可恢复「成果一律同步 GitHub」的约定。

# 背景与来源

| 项 | 值 |
|---|---|
| 源 | `C:/Users/Admin/WorkBuddy AI/2026-10-14-10-26-42/workbuddy-migration/` |
| 目标 | `C:/Users/Admin/WorkBuddy AI/2026-10-14-14-38-20/.workbuddy-ai/skills/github-sync/` |
| 仓库 | `damongoh1031-design/share`（public） |
| 账号 | damongoh1031-design / damongoh1031@gmail.com |
| token | 经典 PAT，scope=repo，2026-10-12 创建，约 2027-01-10 过期（90 天） |

# 迁移操作

```bash
SRC=".../2026-10-14-10-26-42/workbuddy-migration"
DST=".../2026-10-14-14-38-20/.workbuddy-ai/skills/github-sync"
mkdir -p "$DST"
cp "$SRC/skills/github-sync/SKILL.md" "$DST/"
cp -r "$SRC/skills/github-sync/scripts" "$DST/"
cp "$SRC/skills/github-sync/config.json" "$DST/"
cp "$SRC/secrets/github-pat.txt" "$DST/token.txt"   # token 文件名必须与 config 的 token_file 一致
```

然后把 `config.json` 的 `mappings` 改为新工作区路径（旧映射指向已不存在的旧工作区目录，必须改或清空）：

```json
"mappings": [
  { "src": "<新工作区>/kb", "dest": "workbuddy-2026-10-14/kb" }
]
```

# 验证

| 检查 | 命令 | 通过标准 |
|---|---|---|
| token 有效 | `curl -H "Authorization: Bearer $(cat token.txt)" https://api.github.com/user` | 200 + login=damongoh1031-design |
| 同步可用 | `python scripts/sync.py --use-config-mappings` | exit 0，远端出现新目录 |

# 坑与反直觉

- **Windows clone 报 `Filename too long`**：仓库里曾推过超长路径文件（dotnet 示例，260+ 字符）时，git 默认 checkout 失败。修复：`git config --global core.longpaths true`（已在本机执行），之后删除 `_work` 重跑。
- `git ls-remote` **不能**验 token：公开仓库无认证也返回 ref，假阳性；必须打 `api.github.com/user`。
- 创建 PAT 不传 `oauth_access[default_expires_at]` 会「创建即过期」但仍返回 `ghp_` 串，API 一律 401。
- 迁移包 `secrets/` 含活 PAT，目标仓库是 public，**不要把含 token 的目录推上公网**（本技能目录在 `.workbuddy-ai/skills/` 下，通常不在同步映射内）。
- GitHub 网页删 PAT 的 form POST 返回 422，清理旧 token 只能手动去 settings/tokens。
- 同步大包（>10MB）在沙箱前台会触发 2 分钟超时 SIGTERM，用后台任务跑。

# 未核实项

- 旧迁移包中 `github-pat.txt` 的确切过期日以 GitHub 设置页显示为准（manifest 估计 2027-01-10）。
- 仓库 `damongoh1031-design/share` 后续是否转 private 未定；含个人数据的推送前需提醒。
