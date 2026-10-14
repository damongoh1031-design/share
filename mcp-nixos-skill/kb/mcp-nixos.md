---
id: mcp-nixos
title: "mcp-nixos：NixOS 生态 MCP server 工具规范、数据源与工作流（含 skill 化沉淀）"
tags: ["nixos", "nixpkgs", "nix", "mcp", "fastmcp", "home-manager", "flakehub", "noogle"]
created: 2026-10-14
updated: 2026-10-14
version: 1.0.0
status: stable
source: "github.com/utensils/mcp-nixos (MIT) 全量文档+源码提炼 + 本机 uvx 实跑验证"
confidence: "已核实"
---

# mcp-nixos：NixOS 生态 MCP server 工具规范、数据源与工作流

**一句话结论**：mcp-nixos（v3.1.0，2026-09-05）用 2 个工具（`nix` + `nix_versions`，约 1,030 tokens）把 NixOS 生态实时数据（130K+ 包 / 23K+ 选项 / HM 5K+ / darwin 1K+ / Nixvim 5K+ / NVF 2.4K+ / FlakeHub 600+ / Noogle 2K+）暴露给 LLM；已整体转化为用户级 skill `~/.workbuddy-ai/skills/mcp-nixos/`（SKILL.md + 5 个 references），本机 uvx 直跑与关键上游端点均已于 2026-10-14 实测验证。

## 1. 定位与触发

- 解决 LLM 幻觉 NixOS 包名/选项名：训练数据比 nixpkgs 落后数月，它直连官方 API。
- 触发词（任何提及即用）：nixpkgs 包名、属性路径、NixOS/home-manager/darwin/nixvim/NVF 选项、flakes、FlakeHub、channel（unstable/stable/25.05）、二进制缓存、`/nix/store` 路径、wiki/nix.dev、Noogle 函数、版本历史。
- 优先于 `nix search`、手爬 search.nixos.org、`gh api` 查 NixOS/nixpkgs。

## 2. 工具规范（核心）

`nix(action, query, source, type, channel, limit, version, system)`

| 维度 | 取值 |
|---|---|
| action | search / info / stats / browse / channels / flake-inputs / cache / store（`options`=browse 遗留别名） |
| source | nixos(默认) / home-manager / darwin / flakes / flakehub / nixvim / nvf / wiki / nix-dev / noogle / nixhub |
| type | nixos: packages/options/programs/flakes（search）、package/option（info）；flake-inputs: list/ls/read；store: ls/read |
| channel | unstable(默认) / stable / 25.05 式版本号 |
| limit | 1–100；flake-inputs/store read 为 1–2000 |
| version/system | 仅 action=cache 用 |

`nix_versions(package, version, limit)`：NixHub 版本历史，返回 license/homepage/programs、逐版本平台、**nixpkgs commit hash**、属性路径。

## 3. 数据源与真实端点（2026-10-14 取自 config.py）

| source | 端点 | 备注 |
|---|---|---|
| nixos | `https://search.nixos.org/backend`（ES `_search`/`_count`/`_cat/aliases`） | basic auth 用 config.py 内置站点公开值；✅实跑 |
| home-manager | `https://nix-community.github.io/home-manager/print.html` | HTML 解析，进程内缓存 |
| darwin | `https://nix-darwin.github.io/nix-darwin/manual/index.html` | 同上 |
| nixvim | `https://nix-community.github.io/nixvim/search/data/options/chunks/<id>.json` | NuschtOS 静态索引 |
| nvf | `https://nvf.notashelf.dev/options.html` | 规范名 `vim.*` |
| flakehub | `https://api.flakehub.com/search?q=` 等 | ✅实跑 |
| noogle | `https://noogle.dev/api/v1/data` | 整库 bulk + 本地过滤 |
| wiki | `https://wiki.nixos.org/w/api.php`（MediaWiki） | ✅实跑；查询词连字符会被替换为空格 |
| nix-dev | `https://nix.dev/searchindex.js` + `/_sources/<doc>.md` | info 接受 docname/URL/.html |
| nixhub | `https://search.devbox.sh/v2/search`、`/v2/resolve`、`/v1/pkg` | Jetify |
| cache | `https://cache.nixos.org/<hash>.narinfo` | HEAD 探活再 GET |
| flake-inputs/store | 本地 `nix flake archive --json` + /nix/store 读取 | 需本机 Nix |

## 4. 关键行为口径

- `stable` 永远指向当前 stable；2026-10-14 实测为 26.05（另有 25.11、beta、unstable，unstable 183,323 documents）。
- `info` 匹配序：精确属性路径 > 精确 pname > 规范属性（attr==pname）> 属性名排序；pname 撞车显式消歧。
- channels 的 commit 标签：`Revision (indexed)` = 索引 commit（可与 nix_versions 对比）；`Branch HEAD` = GitHub 分支尖端（可能超前，10 分钟缓存）。
- `source=flakes` 不支持 info；wiki/nix-dev 不支持 stats/options。
- 所有输出 plain text；错误走 `error(msg, CODE)`，带可复制 JSON 示例。

## 5. 可复用操作

```bash
# 零安装直跑（无需 Nix；本机 Windows 实测 2026-10-14）
uvx mcp-nixos@latest --help
# MCP 客户端配置（三选一）
#   {"mcpServers":{"nixos":{"command":"uvx","args":["mcp-nixos"]}}}
#   {"mcpServers":{"nixos":{"command":"nix","args":["run","github:utensils/mcp-nixos","--"]}}}
#   {"mcpServers":{"nixos":{"command":"docker","args":["run","--rm","-i","ghcr.io/utensils/mcp-nixos"]}}}
# HTTP 模式
MCP_NIXOS_TRANSPORT=http MCP_NIXOS_HOST=127.0.0.1 MCP_NIXOS_PORT=8000 mcp-nixos
# 无 MCP 时直查（✅已验证）
curl -s -u "aWVSALXpZv:X8gPHnzL52wFEekuxsfQ9cSh" "https://search.nixos.org/backend/_cat/aliases"
curl -s "https://api.flakehub.com/search?q=nixpkgs"
curl -s "https://wiki.nixos.org/w/api.php?action=query&list=search&srsearch=flakes&format=json&utf8=1&srlimit=5"
```

minimal MCP 握手探针（Python 标准库即可驱动 uvx 起的 server，用于验证/调试）：initialize → notifications/initialized → tools/list → tools/call，stdio 换行分隔 JSON。

## 6. 坑与反直觉

1. **browse 不是万能选项搜索**：只支持 home-manager/darwin/nixvim/nvf/noogle；NixOS 选项搜索必须 `action=search, type=options`。
2. **NVF 三种路径**：规范 `vim.*`；`programs.nvf.vim.*` 与 `programs.nvf.settings.vim.*` 会自动归一化。
3. **可选参数不要传空串**：omit 优于空字符串。
4. **`options` 是遗留别名**（曾因混淆模型改名 browse，#125）。
5. **flake-inputs/store 需本机 Nix** 且路径强制 `/nix/store/` 内校验。
6. **ES basic auth 凭据是站点公开值**（前端同款），非机密但勿外泄滥用。
7. 上游 FastMCP 4 要求 starlette ≥1.0.1 安全底线；Nix 侧用 scoped package set 避免污染全局 Python 包集。

## 7. 未核实 / 存疑

- 未逐条实跑：nixhub / noogle / nix-dev / home-manager / darwin / nixvim 各端点（仅从源码取路径）。
- HTTP 传输模式与 Pi adapter 未在本机验证（无对应客户端）。
- 上游文档称 17→2 工具合并发生在 v1.0；本文以 v3.1.0 为准。

## 8. 落地物

- Skill：`~/.workbuddy-ai/skills/mcp-nixos/`（SKILL.md、references/tool-api.md、data-sources.md、workflows.md、implementation-specs.md、agent-personas.md）
- 上游：https://github.com/utensils/mcp-nixos（MIT，作者 James Brink；853 stars / 46 forks；最新 push 2026-09-05）
