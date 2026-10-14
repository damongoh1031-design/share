---
id: workbuddy-user-skills-migration-bundle
title: WorkBuddy 用户级 skills + GitHub PAT 跨 IDE 迁移打包方法
tags: [workbuddy, skills, migration, github, pat, 备份, 安全]
created: 2026-10-14
updated: 2026-10-14
version: 1.0.0
status: stable
source: 本会话实测（本机 win32 / WorkBuddy AI）
confidence: 已核实
---

## 一句话结论

把 `~/.workbuddy-ai/skills/` 整体拷贝并剔除 `_work` 缓存与 `token.txt`，PAT 单独放 `secrets/`，即得可迁移包；**含活 PAT 的目录绝不能推 public 仓库**，推公网只推 skills 部分。

## 迁移包结构（实测）

```
workbuddy-migration/
├── README.md                  # 恢复手册（新 IDE 5 步恢复）
├── manifest.json              # 清单：技能数/文件数/token 状态
├── skills/                    # 48 个用户级 skill 原样拷贝
│   └── github-sync/           # 已剔除 _work（107M git 克隆）与 token.txt
└── secrets/                   # 仅本地，勿入公网仓库
    ├── github-pat.txt         # PAT 明文（scope=repo）
    └── github-sync-config.json
```

## 关键事实与数据

| 项 | 值（2026-10-14 实测） |
|---|---|
| 用户级 skills 数 | 48 个（`~/.workbuddy-ai/skills/`） |
| skills 文件数 | 690 个，压缩前约 13M |
| 最大单项 | diagram-design 5.7M、last30days 3.2M |
| github-sync/_work 体积 | 107M（持久 git 克隆，**必须剔除**） |
| 打包后 zip | 4.2M（PowerShell `Compress-Archive`） |
| PAT 状态 | classic，scope=repo，2026-10-12 创建，2026-10-14 验证 200 有效，约 2027-01-10 过期 |

## 可复用操作

**1. 打包（Git Bash）**

```bash
MIG="$WS/workbuddy-migration"; SK="C:/Users/Admin/.workbuddy-ai/skills"
mkdir -p "$MIG/skills" "$MIG/secrets"
cp -r "$SK/." "$MIG/skills/"
rm -rf "$MIG/skills/github-sync/_work"          # 注意：find -exec rm 删它会失败，直接 rm -rf 最稳
find "$MIG/skills" -name "token*.txt" -delete
cp "$SK/github-sync/token.txt" "$MIG/secrets/github-pat.txt"
cp "$SK/github-sync/config.json" "$MIG/secrets/github-sync-config.json"
```

**2. 打 zip**

```powershell
Compress-Archive -Path "<MIG>\*" -DestinationPath "<WS>\workbuddy-migration.zip" -Force
```

**3. 新 IDE 恢复（README 5 步）**

1. 解压 zip；
2. `skills/*` 全部复制到新机 `C:\Users\<用户名>\.workbuddy-ai\skills\`；
3. `secrets/github-pat.txt` → `<skills>\github-sync\token.txt`（单行明文）；
4. `secrets/github-sync-config.json` → `<skills>\github-sync\config.json`，`mappings[].src` 改新工作区路径或清空为 `[]`；
5. 校验：`curl -H "Authorization: Bearer $(cat token.txt)" https://api.github.com/user` 返回 200 即正常。

**4. 验证 zip 内容（Python）**

```python
import zipfile
z = zipfile.ZipFile('workbuddy-migration.zip')
assert '_work' not in ' '.join(z.namelist())
assert not any(n.endswith('github-sync/token.txt') for n in z.namelist())
```

**5. PAT 有效性验证（唯一可信方法）**

```bash
curl -H "Authorization: Bearer $TOKEN" https://api.github.com/user
```

返回 200 才有效；`git ls-remote` 对公开仓库无需认证也返回 ref，**假阳性，不能用**。

## 坑与反直觉

- **`find <dir> -type d -name "_work" -exec rm -rf {} +` 删不掉 `_work`**（find 已进入该目录，rm 竞态报 not empty）。对已知路径直接 `rm -rf`。
- **token.txt 会随技能目录拷贝走**：拷完必须删除 skills 里的副本，否则整包外发 = 泄露活凭据。
- **`config.json` 的 mappings 是旧工作区绝对路径**（如 `WorkBuddy AI/2026-10-08-11-47-53/kb`），新 IDE 上不存在，恢复时必须改或清空。
- **PAT 过期时间 GitHub API 不返回**，只能看创建时间 + 90 天估算，或去设置页 `https://github.com/settings/tokens` 人工确认。
- **推送前扫密钥**：`grep -rniE "(ghp_|api[_-]?key|secret|password|cookie)" <dir>`；本机 skills 除 github-sync 外无真实凭据（SKILL.md 里的 token/password 字样均是文档陈述）。
- PowerShell `Add-Type` 和 `Shell.Application` COM 在本环境被安全策略拦截，检查 zip 用 Python `zipfile`。

## 未核实 / 存疑

- ZIP 条目数 696 > 文件数 690 + 6，差值为目录条目，未逐一核对每个技能完整性（抽查结构正确）。
- 新 IDE（非 WorkBuddy）的 skills 加载路径是否同为 `~/.workbuddy-ai/skills/`，目标是 WorkBuddy 则成立；其他 harness 需按其文档调整。
