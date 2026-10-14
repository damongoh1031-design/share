# mcp-nixos 工具 API 完整规范

依据：上游 README.md + website/usage.md + mcp_nixos/server.py 工具 docstring（v3.1.0，2026-10-14 提炼）。

## 1. `nix` 工具参数

```
nix(action, query, source, type, channel, limit, version, system)
```

| 参数 | 规范 | 默认 |
|---|---|---|
| `action` | 八选一：`search`（关键词查找）、`info`（特定名详情）、`stats`（计数）、`browse`（按前缀遍历选项树）、`channels`（列 channel）、`flake-inputs`（本地 flake inputs）、`cache`（二进制缓存状态）、`store`（读 /nix/store 文件或列目录）。`options` 是 `browse` 的静默遗留别名 | 必填 |
| `query` | search=搜索词；info=精确名；browse=前缀路径；flake-inputs=`input_name` 或 `input:path`；store=绝对 `/nix/store/` 路径；stats/channels 留空 | `""` |
| `source` | `nixos`（默认）、`home-manager`、`darwin`、`flakes`、`flakehub`、`nixvim`、`nvf`、`wiki`、`nix-dev`、`noogle`、`nixhub`。`action=flake-inputs` 时可传 flake 目录路径（省略=当前项目）。`action=store` 忽略此参数 | `nixos` |
| `type` | source=nixos 搜索：`packages`/`options`/`programs`/`flakes`；source=nixos info：`package`/`option`；flake-inputs：`list`/`ls`/`read`；store：`ls`/`read`；其余 source 忽略 | `packages` |
| `channel` | `unstable`（默认）/ `stable` / 具体版本号如 `25.05` | `unstable` |
| `limit` | 1–100；`flake-inputs` read 与 `store` read 为 1–2000 | `20` |
| `version` | 仅 `action=cache` 使用 | `latest` |
| `system` | 仅 `action=cache` 使用，如 `x86_64-linux`；空=全部平台 | `""` |

## 2. action × source 支持矩阵

| action | nixos | home-manager | darwin | flakes | flakehub | nixvim | nvf | wiki | nix-dev | noogle | nixhub |
|---|---|---|---|---|---|---|---|---|---|---|---|
| search | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| info | ✅ | ✅ | ✅ | ❌（改用 search） | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| stats | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ "Stats not available" | ❌ | ✅ | ❌ |
| browse | ❌ | ✅ | ✅ | — | — | ✅ | ✅ | ❌ | ❌ | ✅ | — |
| channels | ✅（source 无关） | | | | | | | | | | |
| cache | ✅（source 无关） | | | | | | | | | | |
| flake-inputs | ✅（本地，需 Nix） | | | | | | | | | | |
| store | ✅（本地，需 Nix） | | | | | | | | | | |

`search` 的 `type` 仅 source=nixos 时有意义：`packages` / `options` / `programs` / `flakes`。`info` 的 `type` 仅 source=nixos 时有意义：`package` / `option`。

## 3. 官方示例全集

```python
# ---- NixOS 包与选项 ----
nix(action="search", query="firefox", source="nixos", type="packages")
nix(action="info", query="firefox", source="nixos", type="package")
nix(action="search", query="nginx", source="nixos", type="options")
nix(action="info", query="services.nginx.enable", source="nixos", type="option")
nix(action="search", query="vim", source="nixos", type="programs", limit=3)
nix(action="search", query="firefox", source="nixos", channel="stable", limit=3)
nix(action="stats", source="nixos", channel="stable")
nix(action="channels")

# 带点/命名空间的属性路径（issue #118 回归覆盖）
nix(action="search", query="kdePackages.qt6ct", source="nixos", type="packages")
nix(action="search", query="python314Packages.matplotlib", source="nixos", type="packages")
nix(action="search", query="rocmPackages.clang", source="nixos", type="packages")
nix(action="search", query="llvmPackages_22.systemLibcxxClang", source="nixos", type="packages")

# ---- Home Manager / nix-darwin ----
nix(action="search", query="git", source="home-manager")
nix(action="info", query="programs.git.enable", source="home-manager")
nix(action="browse", source="darwin", query="system.defaults")
nix(action="search", query="dock", source="darwin")
nix(action="info", query="system.defaults.dock.autohide", source="darwin")

# ---- Flakes / FlakeHub ----
nix(action="search", query="atuin", source="flakes")
nix(action="search", query="nixpkgs", source="flakehub")
nix(action="info", query="NixOS/nixpkgs", source="flakehub")

# ---- Nixvim / NVF ----
nix(action="search", query="telescope", source="nixvim")
nix(action="info", query="plugins.telescope.enable", source="nixvim")
nix(action="search", query="vim.languages.nix", source="nvf")
nix(action="info", query="programs.nvf.settings.vim.languages.nix.enable", source="nvf")  # 模块包装路径
nix(action="browse", query="programs.nvf.vim.languages.nix", source="nvf")              # 包装前缀

# ---- Wiki / nix.dev ----
nix(action="search", query="nvidia", source="wiki")
nix(action="info", query="Flakes", source="wiki")
nix(action="search", query="packaging tutorial", source="nix-dev")
nix(action="info", query="tutorials/nix-language", source="nix-dev")   # 也接受完整 URL 或 .html URL

# ---- Noogle ----
nix(action="search", query="mapAttrs", source="noogle")
nix(action="info", query="lib.attrsets.mapAttrs", source="noogle")
nix(action="browse", source="noogle", query="lib.strings")

# ---- NixHub ----
nix(action="search", query="nodejs", source="nixhub")
nix(action="info", query="python", source="nixhub")                    # license/homepage/programs/store paths

# ---- 二进制缓存 ----
nix(action="cache", query="hello")
nix(action="cache", query="python", version="3.12.0")
nix(action="cache", query="firefox", system="x86_64-linux")

# ---- 本地 flake inputs / store（需 Nix）----
nix(action="flake-inputs", type="list")
nix(action="flake-inputs", type="ls", query="nixpkgs:pkgs/by-name")
nix(action="flake-inputs", type="read", query="nixpkgs:flake.nix")
nix(action="store", type="ls", query="/nix/store/<hash>-<name>")
nix(action="store", type="read", query="/nix/store/<hash>-<name>/flake.nix")

# ---- 版本历史 ----
nix_versions(package="python", limit=5)
nix_versions(package="nodejs", version="20.0.0")
```

## 4. 错误约定

- 统一走 `error()` helper，返回 plain text、人类可读、带可操作示例。
- 错误码风格：`INVALID_INPUT`（参数缺失/不合法）、`NOT_FOUND`（查无此项）。
- 典型错误信息：
  - `Query required for search. Example: {"action": "search", "query": "firefox"}`
  - `Name required for info. Example: {"action": "info", "query": "firefox"}`
  - `Package name required`（cache 空 query）
  - `Limit must be 1-100` / `Limit must be 1-2000 for flake-inputs read` / `for store read`
  - `For source=nixos, type must be one of: packages, options, programs, flakes. Example: {"action": "search", "query": "nginx", "type": "options"}`
  - `For source=nixos, type must be 'package' or 'option'. Example: {"action": "info", "query": "services.nginx.enable", "type": "option"}`
  - `action=info is not supported for source=flakes. Use action=search instead. Example: {"action": "search", "source": "flakes", "query": "X"}.`
  - `Unknown source: 'X'. Must be one of: nixos, home-manager, darwin, flakes, flakehub, nixvim, nvf, wiki, nix-dev, noogle, nixhub.`
- 可选项**不要传空字符串**（omit parameters you don't need）。

## 5. 已知边界行为

1. **info 精确匹配优先**：先精确属性路径，再精确 pname；pname 撞车时规范属性（attr == pname）胜出，非规范并列时按属性名排序保证确定性，并在响应中显式提示消歧 + 给出可复制的 JSON 重试形状。
2. **NVF 路径归一化**：唯一规范名 `vim.*`；`programs.nvf.vim.*`（简写）与 `programs.nvf.settings.vim.*`（NixOS/Home Manager 模块路径）在 search/info/browse 前统一归一化。
3. **channels 修订版标签**：`Revision (indexed): <sha>` = 索引构建时的精确 commit（可与 `nix_versions` 对比）；`Branch HEAD: <sha> (upstream; may be ahead of indexed data)` = 尽力而为的 GitHub 分支尖端，每分支缓存 10 分钟。
4. **search.nixos.org 对齐**：ES 查询语义与 search.nixos.org 前端对齐；选项/HTML 目录类 source 有精确匹配优先的排序修复（issue #190）。
5. **flake-inputs/store 安全**：路径必须位于 `/nix/store/` 内，越界拒绝。
