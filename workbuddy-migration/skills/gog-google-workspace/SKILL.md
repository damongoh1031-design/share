---
name: gog-google-workspace
description: 用 gog CLI 读写 Google Workspace（Sheets/Drive/Docs/Gmail/Calendar/Slides 等），并可通过 `gog mcp` 接入 WorkBuddy 自定义连接器。当用户要求「连接 Google Drive/Sheets」「安装 gog」「用命令行操作 Google 表格/邮件/日历」，或需要为 Google API 创建 OAuth 客户端时使用。本机已完成安装与授权，优先直接调用，不要重新配置。
agent_created: true
---

# gog CLI — Google Workspace 命令行

## 本机现状（已完成，直接可用）

| 项 | 值 |
|---|---|
| 可执行文件 | `C:\Users\Admin\.workbuddy-ai\bin\gog\gog.exe`（v0.42.0） |
| 已授权账号 | `jsng0819@gmail.com`（services: `drive,sheets`） |
| OAuth 客户端 | `default`，凭据在 `C:\Users\Admin\AppData\Roaming\gogcli\credentials.json` + Windows 凭据管理器 |
| GCP 项目 | `careful-compass-510108-c9`（My Project 40469） |
| MCP 配置 | 已写入 `~/.workbuddy-ai/mcp.json` 的 `gog` 项（stdio） |
| 凭据备份 | `C:\Users\Admin\.workbuddy-ai\bin\gog\client_secret.json` |

**直接用绝对路径调用即可，无需重新授权**：

```bash
GOG="C:/Users/Admin/.workbuddy-ai/bin/gog/gog.exe"
"$GOG" auth doctor --check          # 健康检查，status 应为 ok
"$GOG" sheets get <spreadsheetId> "'表名'!A1:E10"
```

## 常用命令

```bash
# 读取
"$GOG" sheets get <id> "A1:E10"                    # 默认第一个工作表
"$GOG" sheets get <id> "'25/09'!A1:E10"            # 指定表（含 / 的名字要加单引号）

# 写入
"$GOG" sheets update <id> "Sheet1!A1" "值1" "值2"
"$GOG" sheets append <id> "Sheet1!A:A" "新行1" "新行2"
"$GOG" sheets clear <id> "Sheet1!A1:Z100"
"$GOG" sheets batch-update --data-json='[{"range":"Sheet1!A1","values":[["x"]]}]' <id>
"$GOG" sheets insert <id> <sheet> ROWS 5           # 插入 5 行
"$GOG" sheets format <id> "Sheet1!A1:B2" --bold

# 安全开关
"$GOG" sheets update ... --dry-run                 # 只打印将要做的操作
"$GOG" --readonly sheets get ...                   # 运行时阻止所有写请求
"$GOG" --no-input ...                              # CI 模式，不交互

# 其他服务
"$GOG" drive search "name contains 'report'" --json
"$GOG" docs get <docId>
"$GOG" gmail search 'newer_than:7d' --max 10 --json
"$GOG" calendar events --today

# 输出控制
-j / --json     稳定 JSON 信封
-p / --plain    TSV，无颜色
```

## MCP 接入

```bash
"$GOG" mcp --list-tools                              # 列出工具（默认只读）
"$GOG" mcp --list-tools --allow-write                # 含写工具
"$GOG" mcp --account you@x.com --allow-tool "sheets,drive_search" --allow-write
```

工具是**固定 schema 的 typed 工具**，不是通用 shell 桥：`sheets_read_range` / `sheets_update_range` / `drive_search` / `docs_get` / `gmail_search` 等。写工具必须 `--allow-write` 才注册。

`~/.workbuddy-ai/mcp.json` 配置（本机已写入）：

```json
{
  "mcpServers": {
    "gog": {
      "command": "C:\\Users\\Admin\\.workbuddy-ai\\bin\\gog\\gog.exe",
      "args": ["mcp", "--account", "jsng0819@gmail.com",
               "--allow-tool", "sheets,drive_search,drive_get,docs_get",
               "--allow-write"]
    }
  }
}
```

⚠️ 写入 mcp.json 后**不会自动生效**：需在连接器管理页右上角「自定义连接器」入口，对新出现的 `gog` 点「信任」。

## 从零重装 / 换账号

### 1. 安装

```powershell
$zip = "$env:TEMP\gogcli.zip"
Invoke-WebRequest -Uri "https://github.com/openclaw/gogcli/releases/download/v0.42.0/gogcli_0.42.0_windows_amd64.zip" -OutFile $zip -UseBasicParsing
Expand-Archive -Path $zip -DestinationPath "C:\Users\Admin\.workbuddy-ai\bin\gog" -Force
```

### 2. 创建 OAuth 客户端（关键步骤）

必须自己建，gog 无内置 client。**整个流程可用 CDP 接管已登录 Chrome 自动完成**（见 `scripts/` 下的工具）。

| 步骤 | 操作 | URL |
|---|---|---|
| 1 | 创建/选择 GCP 项目 | `console.cloud.google.com/projectcreate` |
| 2 | 启用 Sheets + Drive API | `console.cloud.google.com/flows/enableapi?apiid=sheets.googleapis.com,drive.googleapis.com&project=<PID>` |
| 3 | 配置 OAuth 同意屏幕 | `console.cloud.google.com/auth/overview?project=<PID>` → 点「开始」→ 填应用名 + 支持邮箱 → 受众群体选**外部** |
| 4 | ⚠️ **添加测试用户** | `console.cloud.google.com/auth/audience?project=<PID>` → 「Add users」→ 填自己的邮箱 → 保存 |
| 5 | 创建客户端 | `console.cloud.google.com/auth/clients/create?project=<PID>` → 应用类型选**桌面应用** → 创建 |
| 6 | 提取凭据 | 弹窗里读 `client_id`（`\d{12}-...apps.googleusercontent.com`）和 `client_secret`（`GOCSPX-...`） |

**第 4 步绝对不能漏** —— 应用处于「测试」状态时，未列入测试用户的账号授权会直接返回 `403 access_denied`（页面提示"尚未完成 Google 验证流程"）。

### 3. 导入凭据并授权

```bash
# 生成 credentials.json（installed 格式）
cat > client_secret.json <<'JSON'
{"installed":{"client_id":"...","client_secret":"GOCSPX-...",
"auth_uri":"https://accounts.google.com/o/oauth2/auth",
"token_uri":"https://oauth2.googleapis.com/token",
"auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
"redirect_uris":["http://localhost"]}}
JSON

"$GOG" auth credentials set ./client_secret.json

# 无浏览器授权：分两步
"$GOG" auth add you@gmail.com --services sheets,drive --remote --step=1
#   → 打印 auth_url，用已登录的 Chrome 打开
#   → 点「继续」→ 授权完成后浏览器跳到 http://127.0.0.1:<port>/oauth2/callback?code=...
#   → 该地址无服务监听会显示 ERR_CONNECTION_REFUSED，但 URL 里有 code
#   → 从 CDP 的 /json/list 读出完整回调 URL
"$GOG" auth add you@gmail.com --services sheets,drive --remote --step=2 --auth-url "<回调URL>"

"$GOG" auth doctor --check     # 应全 ok，含 refresh token exchange succeeded
```

## 踩坑记录

| 坑 | 现象 | 处理 |
|---|---|---|
| **未加测试用户** | 授权页 `403 access_denied`「尚未完成 Google 验证流程」 | 去 auth/audience 加测试用户 |
| 窗口失焦 | 点击/输入静默失效，不报错 | CDP 必须先 `Page.bringToFront` + `Emulation.setFocusEmulationEnabled` |
| 按钮在视口外 | 按文本找不到元素 | 先 `scrollIntoView({block:'center'})` 再取 rect |
| 回调页连接被拒 | `127.0.0.1:<port>` ERR_CONNECTION_REFUSED | **这是正常的**，code 在 URL 里，从 `/json/list` 读 |
| 客户端密钥只显示一次 | 弹窗关闭后无法再查看 secret | 关闭前必须提取；丢失只能重建客户端 |
| 中文表名 | 参数传不进 | 用单引号包裹：`"'25/09'!A1:E10"` |
| 凭据明文落盘 | — | `gog auth credentials set` 会把 secret 存进系统凭据管理器；工作区副本用完即删 |

## 配套工具（scripts/）

通用 CDP 浏览器自动化，用于 Google Cloud Console 这类复杂 SPA：

| 脚本 | 用途 |
|---|---|
| `cdp.mjs` | 通用 CDP 执行器：`node cdp.mjs <urlSubstr> <exprFile> [--nav u] [--front] [--shot p]` |
| `click_text.mjs` | 按文本找按钮/链接并真实点击（自动滚动到视口内）`node click_text.mjs <urlSubstr> "<正则>"` |
| `type_into.mjs` | 真实键盘输入：`node type_into.mjs <urlSubstr> css:<选择器>\|idx:N <文本>` |
| `press_key.mjs` | 真实按键：`node press_key.mjs <urlSubstr> Enter\|Tab\|Escape` |
| `probe.js` | 诊断：列出可见输入框/按钮及坐标（含 shadow DOM） |

Node 22+ 零依赖（内置 `WebSocket`）。
