---
id: github-mcp-server-official
title: GitHub 官方 MCP Server（github/github-mcp-server）能力、接法与是否需要自建
tags:
  - MCP
  - GitHub
  - github-mcp-server
  - MCP-Registry
  - toolsets
  - read-only
  - lockdown-mode
  - agent-tooling
created: 2026-10-12
updated: 2026-10-12
version: 1
status: stable
source: 本次会话实测（GitHub API 元数据 + 官方 README 直读 + GitHub Docs/Changelog 检索）
confidence: 已核实
---

# GitHub 官方 MCP Server

## TL;DR

**GitHub 有官方专用 MCP：`github/github-mcp-server`（33,534★，Go，MIT，GitHub 官方维护），不需要自己写。** 远程端点 `https://api.githubcopilot.com/mcp/`（GitHub 托管，OAuth 或 PAT，**所有 GitHub 用户可用、不限套餐**）；本地走 Docker `ghcr.io/github/github-mcp-server`。**老的 TypeScript 参考实现 `@modelcontextprotocol/server-github` 已归档，不要再用。**

---

## 1. 仓库元数据（2026-10-12 实测）

| 项 | 值 |
|---|---|
| 全名 | `github/github-mcp-server` |
| 描述 | *"GitHub's official MCP Server"* |
| 星标 / Fork | **33,534** / 5,134 |
| 语言 / 许可 | Go / **MIT** |
| 创建 / 最后推送 | 2025-03-04 / 2026-10-08 |
| 归档 | 否 |
| Open issues | 354 |
| Topics | `github`, `mcp`, `mcp-server` |
| Go module | `github.com/github/github-mcp-server/v2` |

> ⚠️ README 明确提示：`v2.0.0` tag 早于 module-path 修正，**不能作为 Go module 使用**；需等 `v2.0.1` 之类的重新打 tag。

## 2. 两种部署方式

| 方式 | 端点 / 命令 | 认证 | 适用 |
|---|---|---|---|
| **远程**（GitHub 托管） | `https://api.githubcopilot.com/mcp/` | OAuth 或 PAT（`Authorization: Bearer <PAT>`） | 最省事；VS Code 1.101+、Claude Desktop/Code、Cursor、Windsurf、Codex、OpenCode、Zed、Rovo Dev CLI、Copilot CLI |
| **本地**（Docker） | `ghcr.io/github/github-mcp-server` | `GITHUB_PERSONAL_ACCESS_TOKEN` | **GitHub Enterprise Server 只支持本地** |

补充：
- 远程有 **Insiders 版**：URL 加 `/insiders`，或 header `X-MCP-Insiders: true`（提前试用新工具）。
- **GitHub Enterprise Cloud with data residency（ghe.com）**：远程地址换成 `https://copilot-api.<org>.ghe.com/mcp`。
- 官方文档：*"GitHub MCP 服务器对所有 GitHub 用户均可使用，无论其计划类型如何"*（个别工具遵循其对应产品的权限）。

## 3. 工具集（Toolsets）—— 24 个分组

**工具集是分组不是工具数。** 不指定时用默认工具集。

| 工具集 | 说明 |
|---|---|
| `context` | 当前用户 / 上下文信息 |
| `repos` | 仓库操作（读代码、搜索文件、分析 commit、目录树） |
| `git` | 低层 Git API（refs、commits、trees） |
| `issues` | Issues |
| `pull_requests` | PR |
| `actions` | Actions workflows 与 CI/CD |
| `code_security` | 代码安全（Code Scanning） |
| `code_quality` | Code Quality |
| `secret_protection` | Secret Scanning |
| `security_advisories` | 安全公告 |
| `dependabot` | Dependabot 告警 |
| `discussions` | Discussions |
| `gists` | Gist |
| `labels` | Labels |
| `notifications` | 通知 |
| `orgs` | 组织 |
| `projects` | Projects |
| `governance` | rulesets / custom properties（仓库·组织·企业级） |
| `stargazers` | Star 相关 |
| `users` | 用户 |
| `copilot` | Copilot（如 Coding Agent） |
| `copilot_issue_intents` | 带意图元数据（rationale / confidence / suggestion）的 opt-in issue 指派工具 |
| `copilot_spaces` | Copilot Spaces |
| `github_support_docs_search` | 搜 GitHub 产品与支持文档 |

**工具集配置示例**：

```bash
# 本地二进制
github-mcp-server --toolsets repos,issues --tools get_gist      # 组合：工具集 + 单个工具（叠加）
github-mcp-server --read-only                                   # 只读

# Docker
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=<pat> \
  -e GITHUB_TOOLSETS="repos,issues,pull_requests,actions,code_security" \
  ghcr.io/github/github-mcp-server
```

**规则（官方原文要点）**：
- 工具与工具集可叠加使用。
- **`--read-only` 优先级最高：即使 `--tools` 显式要求写工具，写工具也会被跳过。**
- 工具名必须精确匹配（`get_file_contents`，不是 `getFileContents`）；名字错会让服务器启动失败。
- 工具改名后旧名保留为 alias（见 `docs/tool-renaming.md`）。

## 4. 两个安全开关（重要）

| 开关 | 作用 | 官方明说的边界 |
|---|---|---|
| `--read-only` / `GITHUB_READ_ONLY=1` | 只提供只读工具，阻止对仓库/issue/PR 的修改 | — |
| `--lockdown-mode` / `GITHUB_LOCKDOWN_MODE=1` | 只展示**对仓库有 push 权限者**写的内容；私有仓库不受影响 | *"best-effort content filter... It is **not** an authorization boundary"* |

Lockdown 模式的意图例外：`github-actions[bot]` 与 `copilot` 的产出**始终视为安全**，避免过滤常规自动化输出。

> 官方明确警告：被过滤掉的内容**仍可能通过其他工具或直接用同一凭据访问 GitHub API 拿到**。

## 5. 生态位置（谁被替代了）

| 项 | 状态 |
|---|---|
| `modelcontextprotocol/servers/src/github`（TS 参考实现） | **已归档**，移入 `modelcontextprotocol/servers-archived` |
| `github/github-mcp-server`（Go） | **当前唯一主线**，GitHub 官方维护 |
| **GitHub MCP Registry**（`github.com/mcp`） | 2025-09-16 上线；按 GitHub star 与社区活跃度排序；VS Code 一键安装；与 Anthropic / MCP Steering Committee 共建 OSS Registry |

## 6. 可复用操作

### 6.1 只读起步配置（推荐起点）

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "-e", "GITHUB_TOOLSETS=repos,issues,pull_requests,actions,code_security",
        "-e", "GITHUB_READ_ONLY=1",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "<你的 PAT>" }
    }
  }
}
```

### 6.2 远程接法（OAuth）

```json
{ "servers": { "github": { "type": "http", "url": "https://api.githubcopilot.com/mcp/" } } }
```

### 6.3 远程接法（PAT）

```json
{
  "servers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": { "Authorization": "Bearer ${input:github_mcp_pat}" }
    }
  }
}
```

### 6.4 最小权限 PAT 建议

按需勾选：`repo`（私有仓库读写）、`public_repo`（公开仓库写）、`read:org`、`workflow`（改 Actions）、`security_events`。**先只给只读 scope + `GITHUB_READ_ONLY=1`，跑通再开写。**

## 7. 坑与反直觉

1. **老包已死**：`@modelcontextprotocol/server-github`（npm，TS 版）**已归档**。用它会拿到一个不再维护、工具集远少于官方版的实现。
2. **`v2.0.0` tag 不能当 Go module 用**——module path 修正后需要重新打 tag（如 `v2.0.1`），期间只能用 commit 伪版本。
3. **`--read-only` 会覆盖 `--tools`**——你显式点名一个写工具也照样被跳过，不是报错。排查「为什么工具不见了」先看这个。
4. **工具名必须精确匹配**，写错不是忽略而是**服务器启动失败**。
5. **工具集不是工具数**——24 个工具集，每个下面有多个工具。只看「24」会低估实际能力。
6. **Lockdown 模式不是授权边界**——它只是内容过滤器，凭据能读到的东西没变。别把它当权限控制用。
7. **GitHub Enterprise Server 不支持远程托管**，只能本地跑。
8. **远程端点域名是 `api.githubcopilot.com`**（不是 `api.github.com`），别被名字误导以为必须买 Copilot——官方文档明确说所有用户可用，不限套餐。

## 8. 需要自己写吗？

**不需要。** 官方版覆盖仓库 / issue / PR / Actions / 代码扫描 / Dependabot / Projects / Discussions / Gist / 通知 / 组织 / 治理。

**只有三种情况才值得自建**：
1. 要把「读 GitHub + 本地决策」合成**一个原子工具**（如「检查 flake 更新 → 开 PR」）；
2. 官方没覆盖的内部系统（自建 Git / Gerrit）；
3. 需要**复合审批策略**——官方只给 read-only / lockdown 两档。

**真要写就用官方 SDK**：`github.com/modelcontextprotocol/go-sdk`（Go）、TS / Python / Rust 等 SDK（见 `modelcontextprotocol/*-sdk`），**不要从零实现协议**。

## 9. 与包管理器那 4 个缺口的判断标准

上一份报告（`kb/package-manager-mcp-apt-dnf-zypper-pacman.md`）确认 snap / flatpak / Arch 全量升级 / zypper dup **没有专用 MCP**。

**判断标准**：
- **只是「把一条命令包一层」→ 不值得自己写**，用 `tumf/mcp-shell-server` 的 `ALLOW_PATTERNS` 就够。
- **要「多步 + 回滚 + 审计账本」→ 才值得自建**（参照 `brianlechthaler/apt-mcp` 的 scope 分层 + `confirm: true` 模式）。

## 10. 未核实 / 存疑

| 项 | 状态 |
|---|---|
| 远程服务端的限流具体数值 | 未核实（文档未给明确 QPS） |
| 默认工具集**具体包含哪些** | 未核实（README 有 `#default-toolset` 锚点，本次未展开读） |
| 各工具集下的工具总数 | 未核实（README 的 Tools 章节未逐条计数） |
| GitHub MCP Registry 收录总数 | 未核实 |
| 与 WorkBuddy / Hermes 等具体宿主的一键安装支持度 | 未核实（官方列的是 VS Code / Claude / Cursor / Windsurf / Codex / OpenCode / Zed / Rovo Dev / Copilot CLI） |

## 11. 相关文件

| 文件 | 说明 |
|---|---|
| `kb/package-manager-mcp-apt-dnf-zypper-pacman.md` | 包管理器 MCP 选型（apt/dnf/zypper/pacman/nixos-rebuild/snap/flatpak） |
| `kb/hermes-openclaw-linux-ops-agent-stack.md` | Hermes / OpenClaw Linux 运维栈 |
| `kb/general-agent-workbench-alternatives.md` | 通用 Agent 工作台六项能力选型 |
| https://github.com/github/github-mcp-server | 官方仓库 |
| https://github.com/mcp | GitHub MCP Registry |
