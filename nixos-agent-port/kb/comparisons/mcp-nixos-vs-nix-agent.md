# NixOS 生态两个 MCP：一个只读知识层，一个执行层

> **TL;DR** 它们**不竞争，是两层**。
> `mcp-nixos` 回答"nixpkgs 里有什么"——纯 HTTP，**不需要装 Nix**，2 个工具，853★。
> `nix-agent` 回答"我这台机器现在变成什么样"——要 NixOS + sudoers，7 个工具，16★。
> **判断规则：任何"查"走前者，任何"改"走后者，中间用 `check` 做桥。**
> 两者的 FastMCP 版本要求**互斥**，装不进同一个 Python 环境——这不是 bug，是分层信号。

标签：`nixos` `project-profile` · 证据等级：`A`（源码直读）+ `B`（GitHub API 元数据）

## 0. 元数据对照（抓取于 2026-10-12）

| | `utensils/mcp-nixos` | `JEFF7712/nix-agent` |
|---|---|---|
| 星 / fork | **853** / 46 | **16** / 2 |
| 许可 | MIT | MIT |
| 语言 | Python | Python |
| 版本 | v3.1.0 | v0.12.0 |
| 创建 | 2025-03-20 | 2026-03-19 |
| 最后推送 | 2026-09-05 | 2026-10-12 |
| 仓库体积 | 2,747 KB | 1,315 KB |
| 工具数 | **2** | **7** |
| 已进 nixpkgs | ✅ 是 | ❌ 否（自述 experimental） |

**读法**：853★ 对 16★ 的差距不说明质量差距，说明**受众规模差距**。前者对任何 Linux 用户
（甚至 macOS 的 nix-darwin 用户）都有用；后者只对"愿意给 agent 开 sudoers 的 NixOS 用户"有用。
后者的 `pushed_at` 比前者新一个月，且仍在 0.x，属于**活跃但未定型**。

## 1. 根本区别：一个不碰你的机器，一个只碰你的机器

| 维度 | `mcp-nixos` | `nix-agent` |
|---|---|---|
| 数据来源 | **上游 HTTP API**（search.nixos.org、NixHub、Wiki…） | **本机 `nix` 二进制 + `/etc/nixos`** |
| 需要装 Nix 吗 | ❌ 不需要（除 `flake-inputs` / `store` 两个 action） | ✅ 必须 NixOS + Nix + sudoers |
| 会改系统吗 | ❌ **绝不**（只读） | ✅ **会**（`switch` 直接激活配置） |
| 需要 root 吗 | ❌ 不需要 | ✅ 需要，窄 NOPASSWD 规则 |
| 答案是关于 | **全世界**的 nixpkgs | **这一台**机器的当前状态 |
| 离线可用吗 | ❌ 纯网络 | ✅ 本地执行 |
| 缓存压力 | 大（上游 11 个数据源都会漂移） | 小（本机 `nix` 自己缓存） |

**这就是分层的本质**：`mcp-nixos` 是"图书馆员"，`nix-agent` 是"住在你家的人"。
图书馆员知道所有书的书名和版本，但不知道你书架上现在摆了哪本。

## 2. 工具面对照

### `mcp-nixos`：2 个工具，靠参数塌缩

v3 的重构把原来 17 个工具**合并成 2 个**，参数从 0 个涨到 8 个。这是刻意的上下文预算取舍
（见 [mcp-token-budget](../concepts/mcp-token-budget.md)）。

| 工具 | 参数 | 干什么 |
|---|---|---|
| `nix` | `action` / `query` / `source` / `type` / `channel` / `limit` / `version` / `system` | 八个 action：`search` `info` `stats` `browse` `channels` `flake-inputs` `cache` `store` |
| `nix_versions` | `package` / `version` / `limit`(1–50) | 包**版本历史**：哪个 commit 发布了哪个版本 |

`source` 的 11 个取值（源码 `config.py` 的 `KNOWN_SOURCES` 直读）：

| source | 后端 | 类型 |
|---|---|---|
| `nixos`（默认） | `search.nixos.org` Elasticsearch API | packages / options / programs / flakes |
| `home-manager` | HTML 文档解析 | options |
| `darwin` | HTML 文档解析 | options |
| `nixvim` | 已发布 option 目录 | options |
| `nvf` | NVF options URL | options |
| `noogle` | Noogle API（Nix 函数搜索引擎） | options |
| `wiki` | NixOS Wiki API | 全文 |
| `nix-dev` | nix.dev 文档 | 页面 markdown |
| `nixhub` | NixHub API | 版本 |
| `flakes` | 本地 flake 目录 | inputs |
| `flakehub` | FlakeHub API | flakes |

**注意**：`flakes` / `flake-inputs` / `store` 三个会调用本机 `nix` 二进制（源码有
`_check_nix_available` 门）。所以"不需要装 Nix"是**主要路径**的事实，不是全部。

### `nix-agent`：7 个工具，按"能不能回滚"分档

源码 `_TOOLS` 列表的注释把 7 个工具**自己分了两类**：

| 档 | 工具 | 上游注释原文 |
|---|---|---|
| **运维核心**（结构化信号 + 回滚安全） | `build` | 构建完整闭包但不激活，返回 store 路径；失败带 `failed_derivation{drv, log_tail}` |
| | `diff` | 构建新闭包并与运行系统对比（nvd，退化到 `nix store diff-closures`）：增/删/改版本 |
| | `switch` | `sudo -n nixos-rebuild switch`；**先记 `rollback_generation`**；返回结构化 `summary` |
| | `generations` | `action='list'` 枚举；`action='rollback'` 回退 |
| **配置内省**（"每一条都在为宿主省原始输出"） | `eval_config` | `nix eval` 求最终合并值，支持批量 attrs |
| | `locate_option` | **桥**：某选项在哪些文件被声明/定义，各贡献了什么值 |
| | `check` | 验证阶梯 `lint` → `dry-build` → `dry-activate` |

上游原话（`server.py` 第 17–20 行）：

> Operational core: structured operational signal + rollback safety, the work that can't be
> reproduced reliably from ad-hoc shell.
> Config introspection: kept because each caps or structures Nix output the host would otherwise
> pay for in raw context.

**这句话是整个项目最值得抄的一句**：它承认了"我为什么要保留内省工具"的理由不是功能，
而是**它替宿主省了 token**。

## 3. 配对使用：一个真实的工作流

用户说："帮我把 `firefox` 换成 `firefox-esr`。"

| 步 | 用哪个 | 调用 |
|---|---|---|
| 1. 确认包存在、属性路径正确 | `mcp-nixos` | `nix(action="info", query="firefox-esr", type="package")` |
| 2. 确认在哪个 channel | `mcp-nixos` | 同上带 `channel="25.05"` |
| 3. 找到当前在哪声明 | `nix-agent` | `locate_option(attr="environment.systemPackages")` |
| 4. 确认现在的合并值 | `nix-agent` | `eval_config(attr="environment.systemPackages")` |
| 5. 改文件（宿主的 Edit 工具） | — | — |
| 6. 静态检查 | `nix-agent` | `check(level="lint")` |
| 7. 预览激活影响 | `nix-agent` | `check(level="dry-activate")` |
| 8. 看包增删 | `nix-agent` | `diff()` |
| 9. 用户确认后激活 | `nix-agent` | `switch()` |

**关键点在第 3–4 步**：`locate_option` 的 docstring 自称
"**The bridge from mcp-nixos discovery to editing the right file**"——
上游**自己**把这两个 MCP 定义成了前后两段。

**反过来说**：如果只有 `nix-agent`，第 1 步会变成 `nix search` 的原始输出（几 KB 噪声）；
如果只有 `mcp-nixos`，第 3–9 步一步都做不了。

## 4. ⚠️ 它们装不进同一个 Python 环境

| | 依赖声明（`pyproject.toml` 直读） |
|---|---|
| `mcp-nixos` | `fastmcp>=4.0.0` |
| `nix-agent` | `fastmcp>=2.14,<4` |

**区间不相交**。这不是笔误，是 FastMCP 4.x 的 API 变更造成的真实分叉。

**三个可行解**（按推荐度）：

1. **分开两个进程**（推荐）：各自 venv / 各自 `uvx` / 各自 flake。Hermes 里注册成两个 MCP
   server，互不干扰。这也是"分层"在工程上的自然落地。
2. 用 `nix run` 各自跑各自的 flake（`mcp-nixos` 仓库自带 `.mcp.json` 就是这么做的：
   `nix run .#mcp-nixos`）。
3. 强行降级 `mcp-nixos` 到 3.0 之前的版本去迁就 `fastmcp<4` —— **不推荐**，会丢掉 v3 的
   工具合并收益。

## 5. 两个项目各自的"设计签名"

对比着读能看出两种不同的工程性格：

| | `mcp-nixos` 的签名 | `nix-agent` 的签名 |
|---|---|---|
| 最在意的事 | **上游会漂移**（channel 名字滚动、HTML 会改版） | **别把用户的机器搞坏** |
| 最重的机制 | `ChannelCache` 的代数计数器 + rollover 重检 | `rollback_generation` 先记录 + `degraded` 状态 |
| 最有创意的设计 | ES rescore：`1.0 / len(package_attr_name)`，让短名排前 | `strip_accounting()`：记账字段在模型看到前被剥掉 |
| 最诚实的文档 | `indexed` vs `branch_head` 两种 revision **必须标注清楚** | "pin 是 anti-footgun，**不是** security boundary" |
| 最大风险 | 上游 API 改了就坏 | 给错 sudoers 就等于给 root |

**共同点**（都值得抄）：两者都选择**把工具数量压到最低**，把复杂度从"工具数量"移到
"参数矩阵"和"回传协议"里。

## 6. 该用哪个？决策表

| 你的问题 | 用 |
|---|---|
| "nixpkgs 里有 X 吗 / X 的版本历史" | `mcp-nixos` |
| "NixOS 选项 `services.openssh.enable` 怎么配" | `mcp-nixos`（`type="options"`） |
| "home-manager / darwin / nvf 的选项" | `mcp-nixos` |
| "Nix 语言怎么用 / NixOS Wiki 上怎么说" | `mcp-nixos`（`source="nix-dev"` / `"wiki"`） |
| "这个包有 binary cache 吗" | `mcp-nixos`（`action="cache"`） |
| "读 `/nix/store/...` 里的文件" | `mcp-nixos`（`action="store"`，需本机 nix） |
| "我这台机器现在装了什么" | `nix-agent`（`eval_config`） |
| "这个选项在我的配置里是哪几行" | `nix-agent`（`locate_option`） |
| "改完会有什么变化" | `nix-agent`（`check("dry-activate")` / `diff()`） |
| "切换 / 回滚 / 看 generation" | `nix-agent` |
| "给 agent 开 root" | 两个都不用，去看 [scoped-sudo-and-pin](../concepts/scoped-sudo-and-pin.md) |

**兜底规则**：**分不清的时候问自己"这个答案会不会因为换了台机器而变"**。
会变 → `nix-agent`；不会变 → `mcp-nixos`。

## 7. 未核实

| 事项 | 状态 |
|---|---|
| 两者的端到端实测 | **未做**：本机非 NixOS，结论全部来自源码直读 + 元数据 |
| `mcp-nixos` 的 11 个上游端点当前可用性 | **未逐个 HTTP 探测** |
| `nix-agent` 的 `flake.nix` 能否实际 build | **未跑 `nix build`** |
| 两者同时注册进 Hermes 后的实际表现 | **未实测**：分层判断来自源码与文档，非运行验证 |

## 相关

- [mcp-envelope-protocol](../concepts/mcp-envelope-protocol.md) — `nix-agent` 的回执形状
- [rolling-upstream-cache](../concepts/rolling-upstream-cache.md) — `mcp-nixos` 的缓存六件套
- [mcp-token-budget](../concepts/mcp-token-budget.md) — 为什么 17 个工具会变成 2 个
- [scoped-sudo-and-pin](../concepts/scoped-sudo-and-pin.md) — `nix-agent` 的权限模型
