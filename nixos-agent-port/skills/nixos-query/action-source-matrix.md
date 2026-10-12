# action × source × type 完整矩阵

`nix` 工具的合法组合。**不在表里的组合会返回明确的错误 + 正确调用示例**（上游刻意把错误信息
做成可直接复制的调用模板）。

## 完整组合表

| action | source | 必填 | 合法 `type` | 说明 |
|---|---|---|---|---|
| `search` | `nixos` | `query` | `packages` / `options` / `programs` / `flakes` | 最常用 |
| `search` | `home-manager` | `query` | — | |
| `search` | `darwin` | `query` | — | |
| `search` | `flakes` | `query` | — | search.nixos.org 的 flake 索引 |
| `search` | `flakehub` | `query` | — | FlakeHub 注册表 |
| `search` | `nixvim` | `query` | — | |
| `search` | `nvf` | `query` | — | |
| `search` | `wiki` | `query` | — | NixOS Wiki |
| `search` | `nix-dev` | `query` | — | nix.dev 官方文档 |
| `search` | `noogle` | `query` | — | Nix 函数 |
| `search` | `nixhub` | `query` | — | 包元数据 |
| `info` | `nixos` | `query` | `package`/`packages` / `option`/`options` | 单复数都接受 |
| `info` | `home-manager` | `query` | — | |
| `info` | `darwin` | `query` | — | |
| `info` | `flakehub` | `query` | — | |
| `info` | `nixvim` | `query` | — | |
| `info` | `nvf` | `query` | — | 路径会自动归一化 |
| `info` | `wiki` | `query` | — | |
| `info` | `nix-dev` | `query` | — | 返回页面 markdown |
| `info` | `noogle` | `query` | — | |
| `info` | `nixhub` | `query` | — | license / homepage / store paths |
| `info` | **`flakes`** | — | — | ❌ **不支持**，只能 `search` |
| `stats` | `nixos` | — | — | 需要 `channel` |
| `stats` | `home-manager` / `darwin` / `flakes` / `flakehub` / `nixvim` / `nvf` / `noogle` | — | — | |
| `stats` | `wiki` / `nix-dev` / `nixhub` | — | — | ❌ **不支持** |
| `browse` | `home-manager` / `darwin` / `nixvim` / `nvf` / `noogle` | `query`=前缀 | — | 前缀为空时列顶层分类 |
| `browse` | **`nixos`** | — | — | ❌ **明确拒绝**（用 `search` + `type=options`） |
| `browse` | `flakes` / `flakehub` / `wiki` / `nix-dev` / `nixhub` | — | — | ❌ 不支持 |
| `channels` | — | — | — | 全局，列出 channel + 索引 commit |
| `flake-inputs` | — | — | `list`(默认) / `ls` / `read` | `source` 位可当 flake 目录用；`ls`/`read` 需要 `query` |
| `cache` | — | `query` | — | 用 `version` + `system` 收窄 |
| `store` | — | `query` | `ls` / `read` | 必须是绝对 `/nix/store/` 路径 |

## 参数细节

### `limit` 的合法区间

| action / type | 区间 | 默认 |
|---|---|---|
| 大多数 | 1–100 | 20 |
| `flake-inputs` + `type=read` | 1–2000 | 20 → 内部提升到 `DEFAULT_LINE_LIMIT`(500) |
| `store` + `type=read` | 1–2000 | 同上 |
| `store` + `type=ls` | 1–2000 | 20 → 内部提升到 500 |
| `nix_versions` 的 `limit` | 1–50 | 10 |

> **注意**：传 `limit=20`（恰好是默认值）时，`store`/`flake-inputs` 的 `read` 会把它
> 当成"用户没传"，提升到 500。想要精确 20 行，传 21 或显式接受 500。

### `source` 位的双用途

`action=flake-inputs` 时，`source` 参数被当作 **flake 目录路径**用（若它不是已知 source 名）。
已知 source 名列表（11 个）之外的字符串都会被当成路径。省略 = 用当前项目目录。

### `channel` 的语义

- `unstable` → 跟随 `nixos-unstable`
- `stable` → **始终指向当前稳定版**（不是固定的某个版本号）
- 具体版本如 `25.05` / `25.11`
- 上游用 **Hydra alias 的 generation 计数器**动态发现（`latest-<gen>-nixos-<channel>`），
  硬编码的 fallback 只在发现失败时用一次，**永不缓存**

## 错误信息即教学（上游设计）

上游刻意让非法组合返回**可直接复制的正确调用**，例如：

- `action=browse` + `source=nixos` →
  > To search NixOS options, use: `{"action": "search", "query": "nginx", "type": "options"}`

- `action=info` + `source=flakes` →
  > Use action=search instead. Example: `{"action": "search", "source": "flakes", "query": "<你传的 query>"}`

- 未知 action / source → 列出全部合法值 + 一个示例 JSON。

**读错误信息时不要只看第一句，后面那句才是解法。**
