# mcp-nixos 数据源登记表（参考来源）

依据：上游 AGENTS.md / README / website/about.md / copilot-instructions（2026-10-14 提炼）。

## 1. 总表

| source | 上游 | 端点 / 方式 | 鉴权 | 进程内缓存 | 规模（上游口径） |
|---|---|---|---|---|---|
| `nixos` | search.nixos.org | `https://search.nixos.org/backend`（ES `_search`/`_count`/`_cat/aliases`） | HTTP basic auth（`config.py` 内置站点公开值） | 仅 channel 别名 | 130K+ 包、23K+ 选项 |
| `home-manager` | 官方选项文档 | `https://nix-community.github.io/home-manager/print.html`（HTML 解析） | 无 | 进程生命周期 | 5K+ 选项 |
| `darwin` | nix-darwin 官方文档 | `https://nix-darwin.github.io/nix-darwin/manual/index.html`（HTML 解析） | 无 | 进程生命周期 | 1K+ 选项 |
| `nixvim` | NuschtOS search | `https://nix-community.github.io/nixvim/search/data/options/chunks/<id>.json`（分页 JSON） | 无 | 进程生命周期 | 5K+ 选项 |
| `nvf` | NVF 发布的 unstable 文档 | `https://nvf.notashelf.dev/options.html`（HTML 解析） | 无 | 进程生命周期 | 2.4K+ 选项 |
| `flakehub` | FlakeHub（Determinate Systems） | `https://api.flakehub.com`（`/search?q=`、`/version/<org>/<project>/*`、`/flakes`） | 无 | 无 | 600+ flakes |
| `flakes` | search.nixos.org flake 索引 | 同 nixos ES 后端 | 同上 | 无 | 社区 flakes |
| `noogle` | noogle.dev | `https://noogle.dev/api/v1/data`（整库 bulk） | 无 | 进程生命周期 | 2K+ Nix 函数 |
| `wiki` | wiki.nixos.org | `https://wiki.nixos.org/w/api.php`（MediaWiki API） | 无 | 无 | 社区文档 |
| `nix-dev` | nix.dev | 检索：`https://nix.dev/searchindex.js`；正文：`https://nix.dev/<docname>` 或 `/_sources/<docname>.md` | 无 | 进程生命周期 | 官方教程 |
| `nixhub` | NixHub.io（Jetify） | `https://search.devbox.sh`（`/v2/search`、`/v2/resolve`、`/v1/pkg`） | 无 | 无 | 版本/元数据/store paths |
| `cache`（action） | cache.nixos.org | `https://cache.nixos.org/<store_hash>.narinfo`（HEAD 探活再 GET） | 无 | 无 | 二进制缓存状态 |
| `flake-inputs` / `store`（action） | 本地 /nix/store | `nix flake archive --json` + 文件读取 | 无 | 无 | 需本机 Nix |
| channel 修订版 | GitHub | `https://api.github.com/repos/NixOS/nixpkgs/commits/<branch>`（branch HEAD，尽力而为，10 分钟 TTL；带 `User-Agent: mcp-nixos/<version>`） | 无 | 每分支 10 分钟 | 仅 channels action |

channel 解析：启动时通过 ES `_cat/aliases` 动态发现 `latest-<gen>-nixos-<channel>` 别名，每 channel 取最高 generation（unstable 永取最新一代）；发现失败时回落 `FALLBACK_CHANNELS`；可用 `ELASTICSEARCH_URL` 覆盖后端做本地测试。

## 2. 各源能回答什么

| source | 擅长问题 |
|---|---|
| `nixos` | 包是否存在、属性路径、描述、版本、channel 差异；系统选项名与默认值 |
| `home-manager` | 用户级选项路径（如 `programs.git.enable`） |
| `darwin` | macOS `system.defaults.*` 等 1K+ 设置 |
| `nixvim` | Neovim 配置选项（`plugins.telescope.enable` 等） |
| `nvf` | NVF 的 `vim.*` 选项（含模块包装路径查询） |
| `noogle` | Nix 函数签名与文档（`lib.attrsets.mapAttrs`、`builtins.map`、别名查找） |
| `flakehub` / `flakes` | flake 检索与详情 |
| `wiki` / `nix-dev` | 社区教程与官方文档检索、页面全文 |
| `nixhub` | license / homepage / programs / store paths / 版本历史 |
| `cache` | 某包某版本某平台是否已预构建、下载大小、解包大小、压缩方式 |
| `flake-inputs` / `store` | 读取自己 pin 住的 flake 输入与 /nix/store 文件 |

## 3. 无 MCP 时的 curl 直查降级

MCP 起不来时，按源直查。端点取自 `mcp_nixos/config.py` 与各 source 模块（v3.1.0）；标注 ✅ 的已于 2026-10-14 本机实跑验证。

```bash
# ✅ search.nixos.org Elasticsearch（站点公开 basic auth，与前端同款）
#    查 channel 别名（mcp-nixos 动态发现的同款数据）
curl -s -u "aWVSALXpZv:X8gPHnzL52wFEekuxsfQ9cSh" \
  "https://search.nixos.org/backend/_cat/aliases"
#    搜包（index 名从上面的别名取，如 latest-52-nixos-unstable）
curl -s -u "aWVSALXpZv:X8gPHnzL52wFEekuxsfQ9cSh" \
  -X POST "https://search.nixos.org/backend/latest-52-nixos-unstable/_search" \
  -H "Content-Type: application/json" \
  -d '{"query":{"match":{"package_pname":"firefox"}},"size":5}'
#    计数
curl -s -u "aWVSALXpZv:X8gPHnzL52wFEekuxsfQ9cSh" \
  -X POST "https://search.nixos.org/backend/latest-52-nixos-unstable/_count" \
  -H "Content-Type: application/json" -d '{"query":{"match_all":{}}}'

# ✅ FlakeHub（Determinate Systems）
curl -s "https://api.flakehub.com/search?q=nixpkgs"
curl -s "https://api.flakehub.com/version/NixOS/nixpkgs/*"

# ✅ NixOS Wiki（MediaWiki API；查询词中的连字符在上游会被替换成空格再检索）
curl -s "https://wiki.nixos.org/w/api.php?action=query&list=search&srsearch=flakes&format=json&utf8=1&srlimit=5"

# NixHub.io（Jetify）
curl -s "https://search.devbox.sh/v2/search?q=python&limit=3"        # 版本检索
curl -s "https://search.devbox.sh/v2/resolve?name=python&version=3.12.0"  # 版本→store path
curl -s "https://search.devbox.sh/v1/pkg?name=python"               # 包元数据

# Noogle（整库 bulk 拉取，进程内缓存；按名检索在本地做）
curl -s -m 60 "https://noogle.dev/api/v1/data" | head -c 500

# cache.nixos.org 二进制缓存（先经 NixHub resolve 拿 store path/hash）
curl -s "https://cache.nixos.org/<store_hash>.narinfo"              # HEAD 先探，再 GET

# nix.dev（检索走本地 searchindex.js；正文有 raw markdown 源）
curl -s "https://nix.dev/searchindex.js" | head -c 300
curl -s "https://nix.dev/_sources/tutorials/nix-language.md"        # 页面 raw markdown

# 静态 HTML/JSON 目录（HTML 解析类 source 的上游）
curl -s "https://nix-community.github.io/home-manager/print.html" | head -c 300   # Home Manager
curl -s "https://nix-darwin.github.io/nix-darwin/manual/index.html" | head -c 300 # nix-darwin
curl -s "https://nvf.notashelf.dev/options.html" | head -c 300                    # NVF
curl -s "https://nix-community.github.io/nixvim/search/data/options/chunks/0.json" | head -c 300  # Nixvim chunk
```

注意：ES 凭据为上游 `config.py` 内置的站点公开值；端点若失效，以上游 `mcp_nixos/config.py` 为准。nix.dev 的 `action=info` 还接受完整 URL（`https://nix.dev/tutorials/nix-language`）或 `.html` URL 作为 query。

## 4. 致谢的上游项目

- NixHub.io（Jetify）— 包版本历史
- search.nixos.org — 官方 NixOS 检索
- FlakeHub（Determinate Systems）— flake 注册表
- Noogle — Nix 函数检索引擎
- NuschtOS/search — Nixvim 选项索引基础设施
- nix-community/nixvim、NotAShelf/nvf — Neovim 配置框架
