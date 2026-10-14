# workbuddy-migration — 迁移到新 IDE 的恢复手册

打包日期：2026-10-14
更新日期：2026-10-14（补入 mcp-nixos，更新 github-sync）
来源机器：win32 / WorkBuddy AI / 用户级 skills 目录 `C:\Users\Admin\.workbuddy-ai\skills\`

## 包结构

```
workbuddy-migration/
├── README.md                      ← 本文件
├── manifest.json                  ← 清单（技能数、文件数、token 状态）
├── skills/                        ← 50 个用户级 skill 原样拷贝（已剔除 _work 缓存、token、__pycache__）
└── secrets/                       ← 凭据（勿上传公网仓库；本仓库中未包含）
    ├── github-pat.txt             ← GitHub PAT 明文（scope=repo，90 天）
    └── github-sync-config.json    ← github-sync 原始配置（mappings 指向旧工作区，需改）
```

## 恢复步骤（新 IDE / 新机器）

1. 解压 `workbuddy-migration.zip` 到任意目录。
2. 把 `skills/` 下**所有目录**复制到新 IDE 的用户级 skills 目录：
   - Windows：`C:\Users\<用户名>\.workbuddy-ai\skills\`
   - 目录不存在就先新建。
3. 恢复 token：把 `secrets/github-pat.txt` 复制为
   `<skills>\github-sync\token.txt`（单行明文，无换行也行）。
4. 恢复配置：把 `secrets/github-sync-config.json` 复制为
   `<skills>\github-sync\config.json`，然后二选一：
   - 按需修改 `mappings[].src` 里的旧工作区绝对路径为新工作区路径；
   - 或清空 `mappings` 为 `[]`（之后只用命令行 `--src/--dest` 同步）。
5. 校验 token 有效：
   ```bash
   curl -H "Authorization: Bearer $(cat <skills>/github-sync/token.txt)" https://api.github.com/user
   ```
   返回 `200` + 你的 login 即正常；返回 `401` 说明过期，用
   `scripts/mint_pat.py` 续期（见 `skills/github-sync/SKILL.md`）。
6. 新环境验证同步通过后，再到
   `https://github.com/settings/tokens` 手动 revoke 本包内的旧 token。

## 凭据安全提醒

- `secrets/github-pat.txt` 是**可写仓库的活凭据**。仓库 `damongoh1031-design/share`
  是 **public**，本包（含 zip）**不要**整个推上公网。只推 `skills/` 部分即可，
  或先把仓库转 private 再推完整包。
- token 过期时间约 **2027-01-10**（2026-10-12 创建，90 天有效期，以 GitHub 设置页显示为准）。
