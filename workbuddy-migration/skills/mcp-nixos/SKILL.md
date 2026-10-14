---
name: mcp-nixos
description: "NixOS / nixpkgs 生态权威查询技能，源自 GitHub utensils/mcp-nixos（MCP server，853 stars，MIT）。当任务涉及 NixOS 包名与属性路径、NixOS/home-manager/nix-darwin/nixvim/NVF 选项、flakes 与 FlakeHub、NixOS channel、二进制缓存 cache.nixos.org、/nix/store 路径、NixOS wiki 与 nix.dev 文档、Noogle Nix 函数签名、包版本历史（哪个 commit 发布了某版本）时使用。即使用户只是提到一个包名（如 firefox、python314Packages.matplotlib）或选项路径（如 services.nginx.enable、programs.git.enable），也应触发。核心价值：防止凭训练数据幻觉包名/选项名——训练数据比 nixpkgs 落后数月。触发词：nixos、nixpkgs、nix、flake、home-manager、darwin、nixvim、nvf、noogle、flakehub、nix store、nixos channel、nixos 包、nixos 选项、nix 函数、binary cache、包版本历史。"
description_zh: "NixOS/nixpkgs 生态权威查询：包、选项、flakes、channel、缓存状态、版本历史，替代幻觉与手爬 search.nixos.org"
description_en: "Authoritative NixOS/nixpkgs queries: packages, options, flakes, channels, binary cache, version history — replaces hallucinated package names and manual scraping"
version: 1.0.0
allowed-tools: Read,Bash,Glob,Grep
display_name: "mcp-nixos"
display_name_en: "mcp-nixos"
visibility: "private"
metadata:
  tags: "nixos,nixpkgs,nix,flake,home-manager,mcp,package-search,options"
  category: "developer-tools"
---

# mcp-nixos Skill

MCP-NixOS 是 utensils/mcp-nixos 仓库提供的 MCP server：把 NixOS 生态的**实时数据**（130K+ 包、23K+ 系统选项、5K+ Home Manager 选项、1K+ nix-darwin 选项、5K+ Nixvim、2.4K+ NVF、600+ FlakeHub flakes、2K+ Noogle 函数）通过 **2 个工具**暴露给 AI，全部返回 **plain text**。本 skill 是其完整知识沉淀：工具规范、数据源、工作流、实现规范。

**为什么用它**：LLM 训练数据比 nixpkgs 落后数月，包名/选项名幻觉率高。它直连官方 API，比 `nix search`、手爬 search.nixos.org、`gh api` 更快更新。两个工具合计约 1,030 tokens 上下文开销。

**本机实测（2026-10-14，Windows）**：`uvx mcp-nixos@latest` 可直跑，无需装 Nix；MCP 握手返回 serverInfo `mcp-nixos v3.1.0`，`tools/list` 返回 `['nix', 'nix_versions']`，`action=channels` 实时返回 25.11 / 26.05（stable）/ unstable。

---

## 1. 先决条件：本机有没有这个 MCP

按顺序检查，命中即用：

1. 当前环境工具列表里有 `mcp__nixos__nix` / `mcp__nixos__nix_versions` → 直接调用。
2. 没有 → 本机有 uvx（`which uvx`）就能跑，零安装 Nix：

```bash
# 冒烟测试（约 10 秒，装完即用）
uvx mcp-nixos@latest --help
```

3. 写进客户端配置（任选其一）：

```json
{"mcpServers": {"nixos": {"command": "uvx", "args": ["mcp-nixos"]}}}
```

```json
{"mcpServers": {"nixos": {"command": "nix", "args": ["run", "github:utensils/mcp-nixos", "--"]}}}
```

4. MCP 不可用且无法启动时：用 `references/data-sources.md` 里的 curl 直查端点降级（第 5 节）。

## 2. 两个工具速查

### `nix` — 统一查询工具

```
nix(action, query, source, type, channel, limit, version, system)
```

| 参数 | 取值 | 默认 |
|---|---|---|
| action | `search` / `info` / `stats` / `browse` / `channels` / `flake-inputs` / `cache` / `store`（`options` 是 `browse` 的遗留别名） | 必填 |
| query | 搜索词 / 精确名 / 前缀路径；flake-inputs 用 `input` 或 `input:path`；store 用绝对 `/nix/store/...` 路径；stats/channels 留空 | `""` |
| source | `nixos` `home-manager` `darwin` `flakes` `flakehub` `nixvim` `nvf` `wiki` `nix-dev` `noogle` `nixhub` | `nixos` |
| type | nixos 搜索：`packages`/`options`/`programs`/`flakes`；nixos info：`package`/`option`；flake-inputs：`list`/`ls`/`read`；store：`ls`/`read` | `packages` |
| channel | `unstable` / `stable` / 具体版本如 `25.05` | `unstable` |
| limit | 1–100（flake-inputs/store read 为 1–2000） | `20` |
| version | 仅 `action=cache` 用 | `latest` |
| system | 仅 `action=cache` 用，如 `x86_64-linux` | `""`（全部） |

### `nix_versions` — 包版本历史

```
nix_versions(package, version, limit)
```

返回：license / homepage / programs 元数据、逐版本平台可用性（Linux/macOS）、**nixpkgs commit hash**（可复现构建）、属性路径。

## 3. 查询路由工作流（核心）

用户一句话 → 一个 JSON 调用。原样复制调用形状：

| 用户意图 | 调用 |
|---|---|
| 包 X 在 channel Y 里吗 | `nix {"action":"info","query":"X","channel":"Y"}` |
| 搜包 X | `nix {"action":"search","query":"X"}` |
| 有哪些 channel | `nix {"action":"channels"}` |
| channel X 索引到哪个 commit | `nix {"action":"channels"}`（看 `Revision (indexed)` 标签） |
| 搜 NixOS 选项 | `nix {"action":"search","query":"X","type":"options"}` |
| 选项 X 详情 | `nix {"action":"info","query":"X","type":"option"}` |
| home-manager 选项 | `nix {"action":"search","query":"X","source":"home-manager"}` |
| darwin 选项 | `nix {"action":"search","query":"X","source":"darwin"}` |
| nixvim 选项 | `nix {"action":"search","query":"X","source":"nixvim"}` |
| NVF 选项 | `nix {"action":"search","query":"X","source":"nvf"}` |
| 包 X 提供哪些程序 | `nix {"action":"search","query":"X","type":"programs"}` |
| 包/选项总数 | `nix {"action":"stats"}` |
| 浏览选项树前缀 P | `nix {"action":"browse","query":"P","source":"home-manager"}` |
| X 有二进制缓存吗 | `nix {"action":"cache","query":"X"}` |
| 搜 wiki | `nix {"action":"search","query":"X","source":"wiki"}` |
| 搜 nix.dev | `nix {"action":"search","query":"X","source":"nix-dev"}` |
| 读 nix.dev 页面 | `nix {"action":"info","query":"tutorials/nix-language","source":"nix-dev"}` |
| 查 Nix 函数签名 | `nix {"action":"search","query":"mapAttrs","source":"noogle"}` 或 `nix {"action":"info","query":"lib.attrsets.mapAttrs","source":"noogle"}` |
| 当前 flake 的 inputs | `nix {"action":"flake-inputs"}` |
| 读 /nix/store 文件 | `nix {"action":"store","type":"read","query":"/nix/store/..."}` |
| 哪个 commit 发布了 X 的 Y 版本 | `nix_versions {"package":"X","version":"Y"}` |

**决策规则**（按序判断）：

1. 问的是「某个名字/选项存不存在、详情」→ `info`；问「有哪些」→ `search`；问「有多少/什么版本」→ `stats`/`channels`。
2. 问「哪个 nixpkgs commit 含某版本、什么时候加入的」→ `nix_versions`，不要用 `nix`。
3. NixOS **选项搜索**用 `action=search, type=options`；`browse` 只用于 home-manager/darwin/nixvim/nvf/noogle 的前缀树遍历，**source=nixos 不支持 browse**。
4. 拿不准包名时先 `search` 再 `info`；`info` 对包按「精确属性路径 > 精确 pname」匹配，pname 撞车（firefox/firefox-esr/firefox-mobile）时返回规范属性并在响应里显式提示消歧。

## 4. 关键规范速览（完整版见 references/implementation-specs.md）

1. 所有输出是 **plain text**，禁裸 JSON/XML。
2. `limit` 默认 1–100；仅 `flake-inputs`/`store` 的 read 允许 1–2000。
3. NVF 选项规范名是 `vim.*`；`programs.nvf.vim.*` 和 `programs.nvf.settings.vim.*` 自动归一化。
4. `stable` 永远指向当前 stable（2026-10-14 实测为 26.05）；`unstable` 始终取最新一代索引。
5. flake-inputs / store 需要本机装 Nix；路径强制校验必须在 `/nix/store/` 内。
6. `action=info` 对 `source=flakes` 不支持，改用 `search`。

## 5. 无 MCP 时的直查降级

`references/data-sources.md` 给了每个上游的 curl 直查方式（search.nixos.org Elasticsearch、NixHub、FlakeHub、Noogle、cache.nixos.org narinfo 等）。

## 6. 参考文件索引

| 文件 | 内容 |
|---|---|
| `references/tool-api.md` | `nix` / `nix_versions` 完整参数规范 + 全部官方示例 + 错误约定 |
| `references/data-sources.md` | 11 个数据源登记表：URL、协议、鉴权、缓存、能回答什么；无 MCP 时 curl 降级方案 |
| `references/workflows.md` | 查询路由工作流、/test-tools 八组并行验收工作流、/release 发布工作流、日常开发工作流 |
| `references/implementation-specs.md` | 架构/输出/错误/channel/NVF/limit/安全/测试/风格/发布全套实现规范 + 已知坑 |
| `references/agent-personas.md` | nix-expert / python-expert / mcp-server-architect 三角色定义 |

## 来源与许可

- 上游：https://github.com/utensils/mcp-nixos （MIT，作者 James Brink，最新 release 3.1.0 / 2026-09-05）
- 本文档由上游 README.md、AGENTS.md、.github/copilot-instructions.md、.claude/agents/*.md、.claude/commands/*.md、website/usage.md、mcp_nixos/server.py instructions 块于 2026-10-14 提炼，并经本机 uvx 实跑验证。
