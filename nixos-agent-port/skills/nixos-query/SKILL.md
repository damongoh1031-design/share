---
name: nixos-query
description: "Query nixpkgs/NixOS facts with the mcp-nixos MCP server — packages, options, Home Manager, nix-darwin, Nixvim, NVF, flakes, FlakeHub, Noogle, the binary cache, store paths, and package version history. Use before writing any package name, option path, or version into a config; and when asked whether something exists, what it is called, or which commit shipped it."
version: 1.0.0
author: 从 utensils/mcp-nixos 的源码与官方文档转换而来（Hermes Agent 适配）
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [NixOS, nixpkgs, mcp-nixos, package-search, option-search, version-history, binary-cache, anti-hallucination]
    category: devops
    related_skills: [nixos-ops, fastmcp]
    requires_toolsets: [mcp]
prerequisites:
  commands: [uvx]
  mcp_servers: [nixos]
---

# nixos-query — 用 mcp-nixos 查证 Nix 世界的事实

> 由 `utensils/mcp-nixos`（853★ / MIT / v3.1.0）的源码与文档转换而来。
> 上游只暴露 **2 个工具**，把 17 个工具合并以压低上下文成本（约 1,030 token）。

## 0. 什么时候用（以及为什么必须用）

**在任何把一个包名、选项路径、版本号写进配置之前。** 你的训练数据落后 nixpkgs 几个月，
写错的 `services.xxx.yyy` 不会报"我不认识"，它会报一个更难查的 eval 错误。

用它的三种情况：

1. **确认存在性** —— "这个包在 unstable 里吗？这个 option 叫什么？"
2. **确认含义** —— "这个 option 的类型和描述是什么？默认值？"
3. **确认可复现性** —— "哪个 nixpkgs commit 发的这个版本？有二进制缓存吗？"

**不需要用它的**：本机实际解析成什么值 → 用 `eval_config`（`nixos-ops` 技能）；
某 option 在哪个文件设置 → 用 `locate_option`。

## 1. 两个工具

### 1.1 `nix` — 统一查询

```text
nix(action, query, source, type, channel, limit, version, system)
```

| 参数 | 取值 | 默认 |
|---|---|---|
| `action` | `search` \| `info` \| `stats` \| `browse` \| `channels` \| `flake-inputs` \| `cache` \| `store` | — |
| `query` | search 的关键词 / info 的精确名 / browse 的前缀 / store 的绝对路径 | `""` |
| `source` | `nixos`(默认) \| `home-manager` \| `darwin` \| `flakes` \| `flakehub` \| `nixvim` \| `nvf` \| `wiki` \| `nix-dev` \| `noogle` \| `nixhub` | `nixos` |
| `type` | nixos: `packages`/`options`/`programs`/`flakes`；flake-inputs 与 store: `list`/`ls`/`read` | `packages` |
| `channel` | `unstable` \| `stable` \| 版本号如 `25.05` | `unstable` |
| `limit` | 1–100（flake-inputs/store 的 read 可到 2000） | `20` |
| `version` / `system` | **仅 `action=cache` 用** | `latest` / `""` |

### 1.2 `nix_versions` — 版本史

```text
nix_versions(package, version, limit)   # limit 1-50，默认 10
```

返回：license、homepage、programs、总版本数，以及**每条版本的 nixpkgs commit hash +
attribute path + 平台可用性**。

## 2. action × source 可用性矩阵（别猜，按这个表）

| action \ source | nixos | home-manager | darwin | flakes | flakehub | nixvim | nvf | wiki | nix-dev | noogle | nixhub |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `search` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `info` | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `stats` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| `browse` | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |

`channels` / `flake-inputs` / `cache` / `store` 是**全局 action**，不看 source。

**两个必须记住的边界**：

- **`browse` 对 `source=nixos` 是明确拒绝的。** 要查 NixOS option 用
  `{"action":"search","query":"nginx","type":"options"}`。`browse` 只用于
  home-manager / darwin / nixvim / nvf / noogle 这类预索引的 option 树。
- **`action=info` 不支持 `source=flakes`**，只能 `search`。
- `action=options` 是 `browse` 的**静默别名**（历史遗留），不要主动用。

## 3. 常用调用配方

```python
# 存在性：这个包在不在？
nix(action="info", query="firefox", source="nixos", type="package")

# 搜索包
nix(action="search", query="ripgrep", source="nixos", type="packages")

# 搜 NixOS option（注意 type=options）
nix(action="search", query="nginx", source="nixos", type="options")

# 某个 option 的详情
nix(action="info", query="services.openssh.enable", source="nixos", type="option")

# 这个包提供哪些可执行程序
nix(action="search", query="ripgrep", source="nixos", type="programs")

# Home Manager option
nix(action="search", query="git", source="home-manager")
nix(action="info",  query="programs.git.enable", source="home-manager")

# nix-darwin：按前缀浏览
nix(action="browse", query="system.defaults", source="darwin")

# Nixvim / NVF（Neovim 配置）
nix(action="search", query="telescope", source="nixvim")
nix(action="info",   query="vim.languages.nix.enable", source="nvf")

# Nix 函数签名（写 lib.xxx 之前查一下）
nix(action="info", query="lib.attrsets.mapAttrs", source="noogle")

# NixOS Wiki / nix.dev 文档
nix(action="search", query="nvidia", source="wiki")
nix(action="info",   query="tutorials/nix-language", source="nix-dev")

# channel 列表 + 各自索引到哪个 commit
nix(action="channels")

# 二进制缓存：有没有预编译？（决定要不要本地编译几小时）
nix(action="cache", query="firefox")
nix(action="cache", query="python", version="3.12.0", system="x86_64-linux")

# 统计
nix(action="stats", source="nixos", channel="stable")

# 本地 flake inputs（需要本机有 Nix）
nix(action="flake-inputs", type="list")
nix(action="flake-inputs", type="read", query="nixpkgs:flake.nix")

# 直接读 /nix/store（不需要 Nix）
nix(action="store", type="ls",   query="/nix/store/<hash>-<name>")
nix(action="store", type="read", query="/nix/store/<hash>-<name>/flake.nix")

# 版本史
nix_versions(package="python", limit=5)
nix_versions(package="nodejs", version="20.0.0")
```

## 4. 输出与语义注意点

1. **返回是纯文本，不是 JSON。** 别按 JSON 解析。
2. **`nix_versions` 的 commit 是"可复现锚点"** —— 想固定某个版本，用它的
   `attribute path` + commit hash。
3. **`action=channels` 会区分两种 revision**：
   - `Revision (indexed)` = **搜索索引就是从这**个 commit 构建的 → **可以安全地与
     `nix_versions` 对比**。
   - `Branch HEAD` = 上游分支当前 HEAD，**可能领先索引几个 commit**（best-effort 抓取，
     进程内缓存 10 分钟）→ 只是指针，不是关于索引数据的断言。
4. **NVF 的 option 路径会自动归一化**：`vim.*` 是规范形式，`programs.nvf.vim.*` 与
   `programs.nvf.settings.vim.*` 都接受。
5. **`store` 不需要装 Nix**（直接读盘）；`flake-inputs` 才需要。
6. **`store` / `flake-inputs` 的路径被限制在 `/nix/store/`**，二进制文件与 >1 MB 的文件会被拒。

## 5. 参考文件

| 文件 | 内容 |
|---|---|
| `action-source-matrix.md` | 完整的 action × source × type 组合与参数细节 |
| `sources-and-endpoints.md` | 11 个数据源各自的端点、取数方式与缓存策略（含"为什么这么设计"） |

## 6. 这个服务器本身的坑（用之前该知道）

- **`browse` 不是通用层级浏览器** —— 对 `source=nixos` 直接报错。
- **`limit` 的合法区间随 action 变**：普通 1–100，`flake-inputs`/`store` 的 `read` 到 2000。
- **非 UTF-8 的 `.env` 会让服务器在 stdio 握手前崩溃**（上游 FastMCP 的
  pydantic-settings 会 eager 读 CWD 的 `.env`）。客户端只会看到"启动失败"，没有错误信息。
  规避：环境变量 `FASTMCP_ENV_FILE=/dev/null`。
- **进程内缓存，没有持久化。** Home Manager / darwin / Nixvim / NVF / Noogle / nix.dev
  这几类目录型数据在服务器进程生命周期内缓存；其他查询每次打实时 API。
- **集成测试打真实 API**（不打 mock），所以上游抖动会体现为偶发失败。
