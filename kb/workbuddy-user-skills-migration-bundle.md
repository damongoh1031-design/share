---
id: workbuddy-user-skills-migration-bundle
title: WorkBuddy 用户级 skills + GitHub PAT + 专家包跨 IDE 迁移打包方法
tags: [workbuddy, skills, migration, github, pat, experts, agents, 备份, 安全]
created: 2026-10-14
updated: 2026-10-15
version: 1.1.0
status: stable
source: 本会话实测（本机 win32 / WorkBuddy AI）
confidence: 已核实
type: Checklist
---

## 一句话结论

三类资产分开打包：① skills 目录剔 `_work` 与 `token.txt`；② PAT 单独放 `secrets/`，**含活 PAT 的目录绝不能推 public 仓库**，公网只推 skills 部分；③ 专家包取 `plugins/cache/<market>/<包>/<版本>/` + `marketplaces/my-experts/` + 注册表，**剔除 `.in_use/<pid>`，`marketplaces/experts/plugins/`（208M 应用自播种目录）不进包**。

## 资产落点（WorkBuddy 本机实测）

| 资产 | 路径 | 迁移要点 |
|---|---|---|
| 用户级 skills（48 个） | `~/.workbuddy-ai/skills/` | 剔 `_work`（107M git 克隆）与 `token.txt` |
| github-sync PAT | `skills/github-sync/token.txt` | 单独放 `secrets/`，勿入公网 |
| 专家/专家团（6 包 26 agents） | `~/.workbuddy-ai/plugins/cache/{experts,my-experts}/` | 剔 `.in_use/<pid>` 运行时标记 |
| 自建专家市场 | `~/.workbuddy-ai/plugins/marketplaces/my-experts/` | rimworld-mod-guardian 随包走 |
| experts 市场目录 | `~/.workbuddy-ai/plugins/marketplaces/experts/`（208M） | **不进包**：应用启动自动播种/更新，深层 dotnet 路径超 MAX_PATH |
| 专家注册表 | `~/.workbuddy-ai/experts/custom/<user-id>/experts.json` | 内容为 `["rimworld-mod-guardian"]`，按新账号 user-id 落位 |
| 安装记录 | `~/.workbuddy-ai/plugins/installed_plugins.json` | 提取 6 个专家条目合并进新机 |
| 市场定义 | `~/.workbuddy-ai/plugins/known_marketplaces.json` | `experts`/`my-experts` 两条，`source.path` 改新机绝对路径 |

## 专家包清单（2026-10-14 实测）

| 包 | 版本 | 市场 | agents | skills | 安装日 |
|---|---|---|---|---|---|
| deep-research | 1.0.0 | experts | 1 | 1 | 2026-09-24 |
| gpt-researcher-team（专家团） | 2.0.0 | experts | 7 | 0 | 2026-09-24 |
| operations-customer-experts | 1.0.0 | experts | 5 | 8 | 2026-10-12 |
| education-training-experts | 1.0.0 | experts | 4 | 5 | 2026-10-12 |
| quality-testing-experts | 1.0.0 | experts | 8 | 4 | 2026-10-13 |
| rimworld-mod-guardian（自建） | 1.0.0 | my-experts | 1 | 0 | 2026-10-06 |

自建专家只能随包迁移（市场里没有）；5 个市场专家包在新机也可从专家市场重装，包是离线兜底。
新机恢复后需重启 IDE 再到 Expert Center 验证。

## skills 包结构与关键数据（实测）

```
workbuddy-migration/
├── README.md / manifest.json
├── skills/                    # 48 个用户级 skill 原样拷贝（690 文件，13M）
│   └── github-sync/           # 已剔除 _work 与 token.txt
└── secrets/                   # 仅本地，勿入公网仓库
    ├── github-pat.txt         # PAT 明文（scope=repo）
    └── github-sync-config.json
```

| 项 | 值 |
|---|---|
| skills 数 / 文件数 | 48 个 / 690 个 |
| 最大单项 | diagram-design 5.7M、last30days 3.2M |
| skills zip | 4.2M（PowerShell `Compress-Archive`，696 条目） |
| experts-bundle zip | 4.6M（368 条目，350 文件） |
| PAT 状态 | classic，scope=repo，2026-10-12 创建，2026-10-14 验证 200 有效，约 2027-01-10 过期 |

## 可复用操作

**1. skills 打包（Git Bash）**

```bash
MIG="$WS/workbuddy-migration"; SK="C:/Users/Admin/.workbuddy-ai/skills"
mkdir -p "$MIG/skills" "$MIG/secrets"
cp -r "$SK/." "$MIG/skills/"
rm -rf "$MIG/skills/github-sync/_work"          # 注意：find -exec rm 删它会失败，直接 rm -rf 最稳
find "$MIG/skills" -name "token*.txt" -delete
cp "$SK/github-sync/token.txt" "$MIG/secrets/github-pat.txt"
cp "$SK/github-sync/config.json" "$MIG/secrets/github-sync-config.json"
```

**2. experts 打包（镜像新机落位）**

```bash
B="$WS/workbuddy-migration/experts-bundle"; PC="C:/Users/Admin/.workbuddy-ai/plugins"
for name in deep-research gpt-researcher-team operations-customer-experts education-training-experts quality-testing-experts; do
  mkdir -p "$B/cache-experts/$(dirname ...)"   # 按 <name>/<version> 层级拷，dest 勿预建同名目录
  cp -r "$PC/cache/experts/<name>/<ver>" "$B/cache-experts/<name>/<ver>"
done
cp -r "$PC/cache/my-experts/rimworld-mod-guardian/1.0.0" "$B/cache-my-experts/rimworld-mod-guardian/1.0.0"
cp -r "$PC/marketplaces/my-experts/." "$B/marketplace-my-experts/"
rm -rf "$B"/*/.in_use                            # 逐个删，find -exec 不可靠
```

注册表提取（Python）：

```python
import json, os
inst = json.load(open(r'C:\Users\Admin\.workbuddy-ai\plugins\installed_plugins.json', encoding='utf-8'))
keys = [k for k in inst['plugins'] if k.endswith('@experts') or k.endswith('@my-experts')]
json.dump({'plugins': {k: inst['plugins'][k] for k in keys}},
          open('installed-entries.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
```

**3. 新机恢复（顺序）**

1. 解压 zip；
2. skills 包：`skills/*` → `C:\Users\<用户名>\.workbuddy-ai\skills\`；`secrets/github-pat.txt` → `<skills>\github-sync\token.txt`（单行明文）；
3. experts 包：按缓存/市场/注册三个目录对等复制到 `.workbuddy-ai/plugins/` 与 `.workbuddy-ai/experts/custom/<新账号user-id>/`；
4. 合并 `installed-entries.json` 进新机 `plugins/installed_plugins.json`，`installPath` 里 `C:\Users\Admin\` 按新用户名替换；
5. 合并 `marketplace-defs/*.json` 进新机 `plugins/known_marketplaces.json`；
6. 校验：`curl -H "Authorization: Bearer $(cat token.txt)" https://api.github.com/user` 返回 200；重启 IDE 后到 Expert Center 验证 6 个专家可见。

**4. 验证 zip 内容（Python）**

```python
import zipfile
z = zipfile.ZipFile('experts-bundle.zip')
assert '.in_use' not in ' '.join(z.namelist())
assert not any(n.endswith('github-sync/token.txt') for n in z.namelist())
```

**5. PAT 有效性验证（唯一可信方法）**

```bash
curl -H "Authorization: Bearer $TOKEN" https://api.github.com/user
```

返回 200 才有效；`git ls-remote` 对公开仓库无需认证也返回 ref，**假阳性，不能用**。

## 坑与反直觉

- **`find <dir> -type d -name "_work" -exec rm -rf {} +` 删不掉 `_work`**（find 已进入该目录，rm 竞态报 not empty）。对已知路径直接 `rm -rf`；`.in_use` 同理逐个删。
- **`cp -r src <dest>` 时 dest 已存在同名目录 → 内容被拷进子目录形成双层嵌套**（实测踩到 `1.0.0/1.0.0/` 和 `pkg/pkg/`）。拷前确保 dest 不存在，或拷到父目录。
- **`shutil.copytree` 遇超长路径报 `[WinError 3]`**：`marketplaces/experts/` 内 minimax-docx 的 dotnet 源文件路径深度超 Windows MAX_PATH(260)，git 推送同步时必崩——这是把 208M 目录排除出包的直接原因。
- **sync.py 对多 `--src/--dest` 是逐个 commit**：中途 copytree 崩掉时，前面的 src 已推、后面的没推；重试显示 `NO_CHANGES` 属正常，不代表全部推完，要按仓库 API 核对清单。
- **PAT 过期时间 GitHub API 不返回**，只能创建时间 + 90 天估算，或去 `https://github.com/settings/tokens` 人工确认。
- **`config.json` 的 mappings 是旧工作区绝对路径**（如 `WorkBuddy AI/2026-10-08-11-47-53/kb`），新 IDE 上不存在，恢复时必须改或清空为 `[]`。
- **推送前扫密钥**：`grep -rniE "(ghp_|api[_-]?key|secret|password|cookie)" <dir>`；专家包里命中的 `password/apiKey` 字样均为文档示例占位（`'YOUR_SEARCH_API_KEY'`、`'secure_password'`），非真实凭据。
- PowerShell `Add-Type` 和 `Shell.Application` COM 在本环境被安全策略拦截，检查 zip 用 Python `zipfile`。
- PowerShell 执行 git 后 stdout 偶发丢失但命令实际成功——以 `git log` 或 GitHub API 核对为准。

## 未核实 / 存疑

- ZIP 条目数与文件数差值为目录条目，未逐一核对每个专家文件完整性（抽查结构正确）。
- 新 IDE 若是非 WorkBuddy harness，`~/.workbuddy-ai/` 路径与注册表机制需按其文档调整；本包按 WorkBuddy→WorkBuddy 迁移编写。
- `experts/custom/<user-id>` 在新机的 user-id 需登录 Expert Center 后从实际目录名确认（本机两个账号 5c1d716f…、cb99ad4c… 内容相同）。
