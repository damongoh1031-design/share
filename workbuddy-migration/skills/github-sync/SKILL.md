---
name: github-sync
description: 把本地成果文件同步（commit + push）到 GitHub 仓库。当用户要求「同步到 github」「推送到仓库」「备份成果」「上传结果」「git 上去」，或在产生报告 / 数据集 / 知识库文档 / 脚本等交付物后需要归档时使用。内置 PAT 自动续期脚本，无需 gh CLI。
---

# github-sync · 成果同步到 GitHub

## 用户常驻约定（2026-10-13 确认）

**所有成果一律同步到 GitHub。** 默认仓库：

| 项 | 值 |
|---|---|
| 仓库 | `https://github.com/damongoh1031-design/share` |
| 分支 | `main` |
| 账号 | `damongoh1031@gmail.com`（无 2FA） |
| 可见性 | **public**（含个人数据时要提醒用户是否转私有） |
| 成果落点 | 每个项目一个子目录，如 `malaysiayp-phone-directory/`、`kb/` |

## 快速用法

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"
SK="C:/Users/Admin/.workbuddy-ai/skills/github-sync"

# 1) 同步一个目录到仓库子路径
"$PY" "$SK/scripts/sync.py" --src "D:/proj/out" --dest "my-project/out" -m "update results"

# 2) 同步单个文件
"$PY" "$SK/scripts/sync.py" --src "D:/proj/report.md" --dest "my-project/report.md"

# 3) 用配置里的固定映射（config.json 的 mappings）
"$PY" "$SK/scripts/sync.py" --use-config-mappings

# 4) token 失效时续期（90 天，scope=repo）
"$PY" "$SK/scripts/mint_pat.py" --user damongoh1031@gmail.com --pass 'PASSWORD'
```

`sync.py` 幂等：无变更时不产生空提交。退出码 `0`=成功或无变更，`1`=失败。

**全程非交互，不会弹窗。** 脚本已强制 `credential.helper=""` + `GCM_INTERACTIVE=never`
+ `core.askPass=echo`，push 冲突时自动 `merge -X theirs`（接受远端）→ 二次失败则
`push --force`（本项目单人使用，接受覆盖远端）。详见「坑」第 8 条。

## sync.py 参数

| 参数 | 说明 |
|---|---|
| `--src` | 本地文件或目录（可多次传） |
| `--dest` | 仓库内目标路径（与 `--src` 一一对应；可只传一次则按序配对） |
| `--use-config-mappings` | 用 `config.json` 的 `mappings` |
| `-m/--message` | 提交信息，默认含时间戳 |
| `--repo` | 覆盖仓库（默认 `owner/repo`） |
| `--branch` | 覆盖分支 |
| `--dry-run` | 只显示将要变更的文件，不提交 |
| `--token` | 覆盖 token（不给则读 `token.txt`） |

## 内部机制

1. 在 `config.json` 的 `workdir` 下维护一个**持久克隆**（默认 `<skill>/_work/<repo>`）。
2. 每次先 `git fetch` + `git reset --hard origin/<branch>`，保证与远端一致，再拷文件。
3. `core.autocrlf=false` 克隆；仓库根自动补 `.gitattributes` 含 `*.csv -text`、
   `*.json/*.md/*.py text`，避免 CRLF 规范化破坏预存的 sha256。
4. `git add -A` → 有变更才 commit → push（`http.postBuffer=524288000`）。
5. 结束后从 remote URL 打印结果，token 只存在本地 `token.txt`。

## 坑（照做，别踩）

1. **密码不能用于 git / API** —— 2021-08 起全局禁用，必须用 PAT。
2. **创建 PAT 必须传 `oauth_access[default_expires_at]`**（如 `90`）。
   不传则 token「创建即过期」，页面照样返回 `ghp_...`，但 API 一律 401 `Bad credentials`，
   push 报 `Invalid username or token`。排查看 `https://github.com/settings/tokens/<id>`
   是否显示「This token expired today」。
3. **`git ls-remote` 不能验证 token** —— 公开仓库无需认证也返回 ref，会假阳性。
   必须用 `curl -H "Authorization: Bearer $TOKEN" https://api.github.com/user`。
4. **删除 PAT 的 form POST 返回 422**，清理旧 token 只能手动去
   `https://github.com/settings/tokens`。
5. **大包 push（>10 MB）在沙箱前台会被 SIGTERM**（2 分钟超时）。用后台任务跑。
6. **提交前扫密钥**：`grep -rniE "(password|api[_-]?key|ghp_|secret)" <dir>`。
7. 公开仓库 + 含个人数据（电话 / 邮箱）→ 推送**前**提醒用户是否转私有。
8. **★ 弹窗根因：全局 `credential.helper` 指向 git-credential-manager.exe。**
   `GIT_TERMINAL_PROMPT=0` **拦不住 GCM**（那是独立 GUI 程序，不是终端提示）。
   必须同时设 `GCM_INTERACTIVE=never` + 在仓库内 `git config credential.helper ""`
   + `core.askPass=echo`，并且每条 git 命令都带 `GIT_CONFIG_PARAMETERS="'credential.helper='"`
   才能在子进程级别彻底关掉。只设环境变量不够，因为全局 config 会被 GCM 读走。
9. **push 被拒（远端分叉）时不要再询问用户。** 本仓库单人使用，直接
   `merge -X theirs --no-edit origin/<branch>` → 再 push → 仍失败则 `push --force`。

## 安全自评（自研 skill，P2）

- 纯本地脚本，无第三方代码；网络行为仅限 `github.com` 的 clone / push / 登录。
- `token.txt` 明文存 PAT（scope=`repo`，90 天过期）—— 用户已明确接受此风险。
- 不读取、不外发仓库内容之外的任何本地文件。
