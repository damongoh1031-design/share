# 研究报告：NixOS 生态两个 MCP 的构建解剖 —— `JEFF7712/nix-agent` 与 `utensils/mcp-nixos`

**版本** v1
**成稿日期** 2026-10-12
**检索方式** GitHub REST API（仓库元数据 + `git/trees?recursive=1` 全量文件树）+ `raw.githubusercontent.com` 源码直读（28 个文件，约 250 KB）+ 仓库内官方文档（README / AGENTS.md / docs/ / CHANGELOG）
**判定口径** A = 源码或官方文档直读已核实 · B = GitHub API 元数据实测 · C = 仓库自述未独立复核 · D = 本报告推断

---

## 摘要（TL;DR）

**这两个 MCP 不是竞品，是同一套工作流的两端。**

- `utensils/mcp-nixos` 是**只读知识层**：回答"**存在什么**"——某个包在不在 unstable？这个 option 是什么意思？这个版本是哪个 commit 发的？它**不碰你的机器**，甚至不需要装 Nix。
- `JEFF7712/nix-agent` 是**执行层**：回答"**你的机器实际解析成什么、能不能构建、这次 switch 会改什么**"——它直接 `nixos-rebuild`、写 sudoers、管 generation 回滚。

两者都用 **Python + FastMCP**，但设计哲学几乎相反：前者把 17 个工具**合并成 2 个**以榨干上下文预算；后者把 7 个工具**拆成两层**以保住结构化语义。前者的安全模型是"**不执行**"，后者的安全模型是"**窄 sudo 白名单 + 结构化回执**"。

| 维度 | `utensils/mcp-nixos` | `JEFF7712/nix-agent` |
|---|---|---|
| 定位 | 知识层（只读查询） | 执行层（操作真实配置） |
| 星标 / Fork | **853★ / 46** | 16★ / 2 |
| 语言 / 许可 | Python / MIT | Python / MIT |
| 创建 → 最近推送 | 2025-03-20 → **2026-09-05** | 2026-03-19 → **2026-10-12** |
| 当前版本 | `3.1.0` | `0.12.0` |
| 依赖面 | fastmcp + requests + beautifulsoup4 | **仅 fastmcp** |
| 工具数 | **2**（从 17 合并） | **7**（两层） |
| 上下文预算 | 约 **1,030 token** | 未标注（7 工具，回执按字节计费） |
| 传输 | stdio + **HTTP**（含 stateless） | **仅 stdio** |
| 是否改系统 | ❌ 从不 | ✅ 会（`switch` / `rollback`） |
| 是否需装 Nix | ❌ 不需要 | ✅ 必须（NixOS 上） |
| 安全模型 | 路径白名单 + 不执行 | sudoers 窄白名单 + 结构化回执 + 防呆 |
| 测试 / 实现 代码比 | 265 KB / 202 KB ≈ 1.3× | 154 KB / 100 KB ≈ 1.5× |
| 配套 Agent Skill | ❌ 无（只有 `.claude/agents/` 内部开发用） | ✅ `nix-agent` + `nix-agent-init` 两个 |

**一句话选型**：要"AI 别瞎编包名和 option 名" → 装 `mcp-nixos`，零风险；要"AI 真的帮你改配置并重建" → 加 `nix-agent`，但要接受它**默认高信任**（无提示 switch + 免密 sudo）。

---

## 第 1 章 元数据与项目定位

### 1.1 仓库元数据（GitHub API 实测，B 级，抓取于 2026-10-12）

| 字段 | `JEFF7712/nix-agent` | `utensils/mcp-nixos` |
|---|---|---|
| full_name | `JEFF7712/nix-agent` | `utensils/mcp-nixos` |
| description | `Agent MCP server + skill for managing your NixOS system` | `MCP-NixOS - Model Context Protocol Server for NixOS resources` |
| language | Python | Python |
| license | MIT | MIT |
| stars / forks | 16 / 2 | 853 / 46 |
| open_issues | 1 | 1 |
| created_at | 2026-03-19 | 2025-03-20 |
| pushed_at | **2026-10-12** | 2026-09-05 |
| archived | False | False |
| default_branch | `main` | `main` |
| size (KB) | 1,315 | 2,747 |
| homepage | `https://nix-agent.rupan.dev/` | `https://mcp-nixos.io/` |
| topics | claude-code, claude-skills, mcp, mcp-server | 19 个，含 fastmcp, nixos, nix-packages, nix-options, sre-tools |

> ⚠️ **`nix-agent` 的 README 首段自我声明**（C 级）："**Experimental and a work in progress.** Feedback and contributions welcome."——它不是稳定项目。`mcp-nixos` 的 `pyproject.toml` 分类器则是 `Development Status :: 4 - Beta`。

### 1.2 定位差异的源码证据

`nix-agent` 的 `README.md` 第 9–10 行**主动说明了分工**（A 级，源码直读）：

> It pairs with [`mcp-nixos`](https://github.com/utensils/mcp-nixos). nix-agent operates on your actual configuration, `mcp-nixos` handles package and option discovery.

`nix-agent` 的配套 Skill `skills/nix-agent/SKILL.md` 把它写成三分法（A 级）：

| 角色 | 负责 |
|---|---|
| 宿主 agent 原生工具（Read/Edit/Write） | 编辑 `.nix` 文件 |
| `mcp-nixos` | **发现**包和 option（存在什么、什么意思） |
| `nix-agent` | **操作**用户真实配置（机器解析成什么、能否构建、switch 会改什么） |

### 1.3 规模与工程成熟度

| 指标 | nix-agent | mcp-nixos |
|---|---|---|
| 全部文件（blob） | 133 | 111 |
| 仓库总字节 | 992,608 B（≈0.95 MB，含 164 KB banner.png + 前端站点） | 1,388,032 B（≈1.32 MB，含 274 KB 网站图标与截图） |
| 实现 `.py` | **18 文件 / 100,076 B** | **20 文件 / 201,659 B** |
| 测试 `.py` | **22 文件 / 154,166 B** | **13 文件 / 265,650 B** |
| 文档 `.md` | 9 文件 / 86,389 B | 10 文件 / 114,896 B |
| `.nix` | 3 文件 / 12,683 B | 13 文件 / 31,806 B |

两者**测试代码量都超过实现代码量**（1.3–1.5 倍）。`mcp-nixos` 的单个 `tests/test_tools.py` 就有 **79,737 B**，`tests/test_server.py` 64,818 B——测试比实现更重，这是判断"能不能信这个 MCP"的一个硬信号。

---

## 第 2 章 `utensils/mcp-nixos`：只读知识层怎么建

### 2.1 技术栈与依赖面

`pyproject.toml`（A 级）：

```toml
[project]
name = "mcp-nixos"
version = "3.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastmcp>=4.0.0",
    "requests>=2.32.4",
    "beautifulsoup4>=4.13.4",
]
[project.scripts]
mcp-nixos = "mcp_nixos.server:main"
```

- **构建后端**：`hatchling`（不是 setuptools）。
- **运行时依赖只有 3 个**：FastMCP 4.x、requests、BeautifulSoup4。没有 ORM、没有数据库驱动、没有向量库。
- **类型检查是 strict**：`[tool.mypy] strict = true`，且 `warn_return_any = true`。
- **lint 用 ruff**，`line-length = 120`，规则集含 `B`（bugbear）、`C4`、`UP`。
- **`fastmcp>=4.0.0` 是有意为之**：AGENTS.md 说明当前跑在 MCP SDK 2.x 上，协议版本 **2026-07-28**。

### 2.2 代码架构（5 层）

```
mcp_nixos/
├── server.py     30,246 B   ← MCP 工具定义 + action×source 路由 + 传输启动
├── caches.py     24,122 B   ← 6 个进程内缓存类（ChannelCache 等）
├── config.py      3,830 B   ← 全部端点常量 + 异常类 + KNOWN_SOURCES
├── utils.py      14,053 B   ← 共享工具（HTML 解析、路径校验、格式化）
└── sources/                 ← 每个数据源一个模块（15 个文件）
    ├── base.py          14,219 B  ← 通道解析 + ES 查询 + browse 公共逻辑
    ├── nixos.py         20,100 B  ← search.nixos.org Elasticsearch
    ├── nixhub.py        15,966 B  ← NixHub 版本史 + 二进制缓存
    ├── noogle.py        12,415 B
    ├── flake_inputs.py  11,492 B  ← 本地 /nix/store
    ├── nvf.py           10,401 B
    ├── nixdev.py         8,018 B
    ├── nixvim.py         6,462 B
    ├── flakehub.py       6,194 B
    ├── flakes.py         6,315 B
    ├── store.py          6,038 B
    ├── wiki.py           5,200 B
    ├── home_manager.py     648 B  ← 只是对 base.py 的薄封装
    ├── darwin.py           598 B
    └── __init__.py       3,856 B  ← 只做 re-export，向后兼容
```

**设计要点**：`home_manager.py` / `darwin.py` 各只有 ~600 B——因为它们复用了 `base.py` 里的 `HtmlOptionsCache` + `_search_html_options` / `_info_html_options` / `_browse_options` 通用实现。**"同形状的数据源抽公共实现"是这套架构省代码的关键**。

### 2.3 只暴露 2 个工具：把上下文预算当一等约束

`server.py` 顶部注释（A 级）：

```python
# =============================================================================
# MCP Tools (only 2 exposed)
# =============================================================================
```

README 的原话（C 级，但语气很直白）：

> **Just two.** We consolidated 17 tools into 2 because your AI's context window isn't infinite.
> **~1,030 tokens total.** ... While other MCP servers are hogging your context like it's Black Friday, we're sipping minimalist tea in the corner.

**这是一个明确的架构决策**：把 11 个数据源 × 多个动作压进**两个工具的参数矩阵**里，而不是暴露 17 个工具名。代价是模型必须学会 `action`/`source`/`type` 的组合；收益是**工具元数据（tool schema）的固定上下文成本降到约 1,030 token**。

`server.py` 还通过 MCP 的 `instructions` 字段（`InitializeResult`）主动给模型"喂招"——注释原文（A 级）：

> The `instructions` string is surfaced to clients via the MCP `InitializeResult` and is how hosts prime the model on when to reach for this server versus Bash/web search. Keep it short, intent-focused, and explicit about triggers; see GH #146.

`_SERVER_INSTRUCTIONS` 里塞了 **8 条 "意图 → 调用" 的 JSON 形状样例**（如 `"does X have a binary cache?" → nix {"action":"cache","query":"X"}`），并要求"**即使你觉得你知道答案也要调用**，你的训练数据落后 nixpkgs 几个月"。这是**对抗幻觉的前置提示工程**。

### 2.4 `nix` 工具：action × source 二维矩阵

工具签名（A 级，源码直读）：

```python
async def nix(
    action: str = ...,   # search | info | stats | browse | channels | flake-inputs | cache | store
    query: str = "",
    source: str = "nixos",  # nixos | home-manager | darwin | flakes | flakehub | nixvim | nvf | wiki | nix-dev | noogle | nixhub
    type: str = "packages",
    channel: str = "unstable",
    limit: int = 20,
    version: str = "latest",   # 仅 action=cache
    system: str = "",          # 仅 action=cache
) -> str
```

8 个 action × 11 个 source 的可用组合（源码路由实测，A 级）：

| action \ source | nixos | home-manager | darwin | flakes | flakehub | nixvim | nvf | wiki | nix-dev | noogle | nixhub |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `search` | ✅ packages/options/programs/flakes | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `info` | ✅ package/option | ✅ | ✅ | ❌ 明确报错 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `stats` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| `browse` | ❌ **明确拒绝** | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| `channels` | 全局（不分 source） | | | | | | | | | | |
| `flake-inputs` | 全局（`type` = list/ls/read） | | | | | | | | | | |
| `cache` | 全局（用 `version` + `system`） | | | | | | | | | | |
| `store` | 全局（`type` = ls/read） | | | | | | | | | | |

**几处刻意的"报错即教学"**（A 级，源码原文）：

- `action=browse` + `source=nixos` 被**显式拒绝**，并直接给出替代写法：
  > `action=browse is not for NixOS. To search NixOS options, use: {"action": "search", "query": "nginx", "type": "options"}.`
- `action=info` + `source=flakes` 也**显式拒绝**，并把 `query` 回填进示例 JSON 里返回——错误信息本身是可直接复制的调用模板。
- `action=options` 作为**静默别名**保留（代码注释：`The action=options name was confusing small models (GitHub #125)`）——说明这个项目**按小模型的失败模式迭代过**。

**返回格式是纯文本，不是 JSON**。AGENTS.md 第 177 行（A 级）："All responses are formatted as human-readable plain text. **Never return raw JSON or XML to users.**" 测试里还有一条约束："Tests ensure plain text output (**no XML/JSON leakage**)"。

### 2.5 `nix_versions`：版本史工具

```python
async def nix_versions(package: str, version: str = "", limit: int = 10) -> str
```

- `limit` 硬校验 1–50；`package` 用正则 `^[a-zA-Z0-9\-_.]+$` 白名单校验（防注入）。
- 取数走 `asyncio.to_thread(_fetch_nixhub_pkg, package)`——**所有阻塞 IO 都在线程池里**，不阻塞事件循环。
- 输出含：license、homepage、programs、总版本数、以及每条版本的 **nixpkgs commit hash + attribute path + 平台可用性**。
- README 定位："Which nixpkgs commit shipped version X, what attribute path, which platforms"。

### 2.6 11 个数据源各自的取数方式

这是这个项目**技术含量最集中的地方**——它没有"一个 API 打天下"，而是对每种数据源用了不同的取数策略（A 级，`config.py` + `sources/*` 源码直读）：

| source | 端点 / 机制 | 取数方式 | 缓存 |
|---|---|---|---|
| `nixos` | `https://search.nixos.org/backend`（Elasticsearch） | **ES `_search` + 自建 query DSL + rescore** | 无（实时） |
| `home-manager` | `nix-community.github.io/home-manager/print.html` | **抓 1 个 4.3 MB 的 print 单页 HTML 再 BeautifulSoup 解析** | `HtmlOptionsCache` |
| `darwin` | `nix-darwin.github.io/nix-darwin/manual/index.html` | 同上 | `HtmlOptionsCache` |
| `nixvim` | `nix-community.github.io/nixvim/search/data/options/chunks/N.json` | **按 chunk 顺序拉到 404 为止**（约 60 chunk / 17,000 option） | `NixvimCache` |
| `nvf` | `nvf.notashelf.dev/options.html` | HTML 解析（unstable 文档） | `NvfCache` |
| `noogle` | `https://noogle.dev/api/v1/data` | **一次性拉 4.46 MB JSON** | `NoogleCache` |
| `nix-dev` | `https://nix.dev/searchindex.js` | **读 Sphinx 搜索索引** | `NixDevCache` |
| `wiki` | `https://wiki.nixos.org/w/api.php` | **MediaWiki API** | 无 |
| `flakehub` | `https://api.flakehub.com` | REST（带 `User-Agent: mcp-nixos/<ver>`） | 无 |
| `nixhub` | `https://search.devbox.sh` | REST（版本史 + store path） | 无 |
| `flakes` | search.nixos.org 的 flake 索引 | 走 `_search_flakes` | 无 |
| `cache` | `https://cache.nixos.org` | **NixHub 解析出 store path → 查 `.narinfo`** | 无 |
| `flake-inputs` / `store` | **本地 `/nix/store`** | 直接读盘（不需要 Nix）/ `nix flake archive --json`（需要 Nix） | 无 |

**值得单独抄的两个做法**：

1. **`nixos` 源的 ES query 是手写的，含 rescore**。`sources/nixos.py` 里 `_PACKAGE_RESCORE`（A 级）：
   ```python
   "rescore_query": {"function_score": {"script_score": {
       "script": {"source": "1.0 / doc['package_attr_name'].value.length()"}}}},
   "rescore_query_weight": 20.0,
   ```
   即"**主名越短越优先**"——`firefox` 排在 `firefox-esr` / `firefox-mobile` 前面。注释说明这是**复刻上游 search.nixos.org 的 rescoreQuery**（因为索引里没有等价的"主名长度"信号）。
2. **HTML 源用"print 单页"而不是爬多页**。`config.py` 注释（A 级）：
   > Home Manager's option docs are split across mdBook pages. **The print view keeps the complete option catalogue in one document** for search, info, browse, and stats.
   一次请求换全量目录，比爬几百页便宜一个数量级。

### 2.7 缓存设计：`ChannelCache` 是整个仓库最讲究的一段

NixOS channel 名会随 Hydra 发布滚动（`latest-<gen>-nixos-<channel>`），硬编码必然腐化。`caches.py` 里的 `ChannelCache` 处理了四种真实故障（A 级，源码注释直读）：

| 机制 | 常量 | 解决的问题 |
|---|---|---|
| **代数计数器解析** | `_ALIAS_RE = ^latest-(\d+)-nixos-(unstable\|\d+\.\d+)$` | 用 generation 数字判断哪个 alias 最新，**不硬编码** |
| **flake 索引同源发现** | `_FLAKE_ALIAS_RE = ^latest-(\d+)-group-manual$` | 旧 generation 会被退休，所以也从同一探测里发现 |
| **失败重试冷却** | `_DISCOVERY_RETRY_COOLDOWN = 30.0` | 探测失败后 30s 内不再打，避免并发调用者排队等 10s 超时 |
| **rollover 重检** | `_ROLLOVER_RECHECK = 300.0` | Hydra 发布中会先建 alias 再填数据，**空 alias 的结论 5 分钟后过期**，否则进程永远钉在旧 generation |
| **fallback 不 memoize** | `FALLBACK_CHANNELS` | 退休 alias 会 404，所以 fallback 结果**永不缓存**，下次调用重新发现 |
| **线程锁** | `threading.Lock()` | 每次工具调用都过 `asyncio.to_thread`，首请求会竞争，锁保证填充决策原子 |
| **名字与计数分离** | `alias_names` vs `available_channels` | 一次 `_count` 失败不该缩小"可解析的 channel 集合" |

`config.py` 里对 `FALLBACK_CHANNELS` 的注释把这个取舍讲得很透（A 级）：

> These generations **bit-rot**: Hydra retires old `latest-<gen>-nixos-*` aliases, and a retired alias 404s on every query. The cache therefore **never memoizes a fallback result** — it retries discovery on the next call — so this map only has to cover a single request during an upstream blip.

**这是"面对一个会持续漂移的上游，怎么写缓存"的教科书级案例**，跟 NixOS 无关，任何对接会滚动的 API 的项目都能直接抄。

### 2.8 安全边界：`/nix/store` 路径校验

`store` 和 `flake-inputs` 两个 action 能读本地文件，所以有路径校验。`utils.py`（A 级）：

```python
def _validate_store_path(path: str) -> bool:
    """Validate that a path is within /nix/store/ and doesn't escape."""
    try:
        real_path = os.path.realpath(path)      # 解析符号链接与 ..
        return real_path.startswith("/nix/store/")
    except (OSError, ValueError):
        return False
```

四道防线（A 级）：

| 防线 | 实现 | 说明 |
|---|---|---|
| 绝对路径 | `path.startswith("/")` | 拒绝相对路径 |
| 逃逸防护 | `os.path.realpath()` 后再判前缀 | **先解析再判断**，能挡住 `..` 与符号链接 |
| 大小上限 | `MAX_FILE_SIZE = 1024 * 1024`（1 MB） | 超限返回 `FILE_TOO_LARGE` |
| 二进制拒绝 | `_is_binary_file()` 读 8 KB 找 `\x00` | 读不了就当二进制（fail-closed） |
| 行数上限 | `DEFAULT_LINE_LIMIT=500` / `MAX_LINE_LIMIT=2000` | `ls` 也截断（"a caller passing `limit=1` against a large store directory doesn't get the entire listing back"） |

> ⚠️ **注意一个细节**：`store` 的 `ls`/`read` **不需要 Nix**（直接读盘），只有 `flake-inputs` 才需要 `nix flake archive`。README 把这个能力点写成了"requires Nix"，实际上 `store` 不需要——**文档比实现更保守**。

### 2.9 传输与部署面（比 nix-agent 宽）

`server.py::main()`（A 级）支持两种传输：

```bash
# stdio（默认）
MCP_NIXOS_TRANSPORT=stdio mcp-nixos
# HTTP（Remote MCP），端点默认 /mcp
MCP_NIXOS_TRANSPORT=http MCP_NIXOS_HOST=127.0.0.1 MCP_NIXOS_PORT=8000 mcp-nixos
# 自定义路径
MCP_NIXOS_TRANSPORT=http MCP_NIXOS_PATH=/api/mcp mcp-nixos
# 无状态 HTTP（关闭 per-client session）
MCP_NIXOS_TRANSPORT=http MCP_NIXOS_STATELESS_HTTP=1 mcp-nixos
```

端口校验做得比一般项目细：`1 <= port <= 65535`、`path` 必须非空、必须 `/` 开头、**不允许 `//`**。

**安装路径有 5 条**（README，C 级）：

| 方式 | 命令 | 特点 |
|---|---|---|
| uvx（推荐） | `uvx mcp-nixos` | 无需安装、无需 Nix |
| Nix | `nix run github:utensils/mcp-nixos` | |
| Docker | `ghcr.io/utensils/mcp-nixos` | |
| HTTP 远程 | 见上 | |
| Pi Coding Agent | `pi-mcp-adapter` 或仓库内 `.pi/extensions/mcp-nixos.ts` | Pi 不原生支持 MCP，仓库自带适配器 |
| **nixpkgs 声明式** | `environment.systemPackages = [ pkgs.mcp-nixos ];` | **已进 nixpkgs**（这是"能不能长期用"的强信号） |

`flake.nix` 暴露面（A 级）：`packages.mcp-nixos`、`apps`、`overlays.default`（只加 `pkgs.mcp-nixos`）、`overlays.fastmcp4`（升级整套 `python3Packages.fastmcp`）、以及已弃用的 `overlays.fastmcp3`（带 `lib.warn`）。

> 一个值得注意的工程细节：`overlays.default` **故意不替换调用方的 `python3Packages.fastmcp`**，因为那可能破坏其他依赖 `mcp` 的包。flake 里甚至有 `checks.fastmcp4-overlay` 用 `assert` 断言"`overlays.default` 不会替换消费者包集里的 fastmcp"（A 级）。**这是把"不破坏别人的环境"写成 CI 断言**。

### 2.10 工程化：一个相当标准的现代 Python OSS 流水线

| 环节 | 工具 / 配置 |
|---|---|
| 构建 | hatchling |
| 测试 | pytest + pytest-asyncio（auto 模式）+ pytest-xdist + pytest-rerunfailures，默认 `--cov=mcp_nixos` |
| 测试标记 | `unit` / `integration` / `slow` / `not_integration` / `flaky(reruns=3)` |
| **集成测试打真实 API，不打 mock**（AGENTS.md 原文："Integration tests hit real APIs (no mocks)"） | |
| Lint / Format | ruff |
| 类型 | mypy `strict = true` |
| 发布 | **release-please**（`release-please-config.json` + `.release-please-manifest.json`），自动开 `release: vX.Y.Z` PR |
| 发布后 | 认证 release 事件 → 发 PyPI + 多架构 Docker（GHCR + Docker Hub）+ 打 tag 的 flake 到 FlakeHub |
| CI | flake check、Nix build、Python 分发包构建、twine 校验、lint、typecheck、测试 |
| 文档站 | VitePress（`website/`，含 favicon 全套、og-image、`netlify.toml`） |
| 编码规范 | commit 用 `type: summary`（feat/fix/docs/refactor/test/chore） |

**仓库内还带了自己的 Claude Code 开发用 agent 定义**（`.claude/agents/`）：`mcp-server-architect.md`、`nix-expert.md`、`python-expert.md`，以及 `.claude/commands/release.md`、`.claude/commands/test-tools.md`（15 KB）。**注意：这些是"开发这个 MCP 用的"，不是给用户的运维 skill**——跟 `nix-agent` 的 `skills/` 性质不同。

### 2.11 一个真实的上游踩坑（很有代表性）

`mcp_nixos/__init__.py` 开头有一段注释（A 级）：

> **Sidestep an upstream crash**: fastmcp's top-level import constructs a pydantic-settings `Settings()`, which eagerly reads `.env` from the caller's CWD via python-dotenv. A **non-UTF-8 `.env`** (git-crypt ciphertext, sops-encrypted dotenv, any binary blob) takes the whole server down with a `UnicodeDecodeError` *before* the MCP stdio handshake ever runs — the client just sees mcp-nixos fail to start.

修法是 `os.environ.setdefault("FASTMCP_ENV_FILE", os.devnull)`。**这是个很典型的 MCP 故障模式**：MCP 服务器在 stdio 握手**之前**崩溃，客户端只能看到"启动失败"，没有任何错误信息。任何写 MCP server 的人都该知道这个坑。

---

## 第 3 章 `JEFF7712/nix-agent`：执行层怎么建

### 3.1 技术栈与依赖面（刻意极简）

`pyproject.toml`（A 级）：

```toml
[project]
name = "nix-agent"
version = "0.12.0"
requires-python = ">=3.11"
dependencies = [
    "fastmcp>=2.14,<4",
]
[project.scripts]
nix-agent = "nix_agent.__main__:main"
```

- **构建后端**：`setuptools`（不是 hatchling）。
- **只有一个依赖：FastMCP**。没有任何 HTTP 客户端、没有 HTML 解析库——因为它**只操作本地机器**。
- **`fastmcp>=2.14,<4`**：与 `mcp-nixos` 的 `>=4.0.0` **正好不重叠**。两者要同时装，得靠各自的隔离环境（nix 打包或独立 venv）。
- `[tool.setuptools.packages.find] where = ["src"]`——标准 src 布局。

### 3.2 代码架构（两层）

```
src/nix_agent/
├── __main__.py     3,198 B   ← CLI 入口：子命令 + 启动 MCP stdio
├── server.py       5,262 B   ← 只做「工具注册 + 计时/记账插桩」
├── runner.py       5,732 B   ← 子进程执行 + 截断 + envelope 构造
├── target.py       9,118 B   ← flake 目标解析 + 防呆（最复杂的单文件之一）
├── metrics.py     16,915 B   ← usage log（最大文件）
├── logparse.py     7,010 B   ← 解析 nvd / diff-closures / Nix 错误
├── health.py       2,448 B   ← switch 前后 failed unit 快照 diff
├── hostattr.py     2,495 B   ← 隐式主机名绑定 + 候选 attr 推导
├── bootstrap.py    1,390 B   ← 首次特权 switch（无 TTY 时打印一次性命令）
├── privilege.py    1,529 B   ← sudo -n + sudo 失败诊断
└── tools/
    ├── switch.py      13,832 B  ← switch + generations（最大工具）
    ├── check.py        6,711 B  ← lint / dry-build / dry-activate 三级阶梯
    ├── eval.py         6,745 B  ← nix eval + 2 KB 尺寸护栏
    ├── inspect_flake.py 6,527 B ← 仓库体检（CLI 子命令，非 MCP 工具）
    ├── locate.py       6,077 B  ← 某 option 在哪个文件被设置
    ├── build.py        4,854 B  ← build + diff（共享 build_closure）
    └── __init__.py         0 B
```

**架构核心是"分层收敛"**：所有工具都走 `runner.run(argv)` → `runner.envelope(...)`，所有工具都先 `resolve_target()` 再决定能不能跑。**没有工具直接调 `os/exec`**。

### 3.3 七个工具，两层

`server.py` 的 `_TOOLS` 列表（A 级，含作者写的定位注释）：

**第一层 · Operational core（"结构化运行信号 + 回滚安全，无法从临时 shell 可靠复现的工作"）**

| 工具 | 签名 | 干什么 |
|---|---|---|
| `build` | `(flake_uri?, mode?)` | 构建整个 system/HM 闭包，**不激活**。返回 store path；失败带 `failed_derivation{drv, log_tail}` |
| `diff` | `(flake_uri?, mode?)` | 构建新闭包并与**运行中的系统**对比（`nvd`，回退 `nix store diff-closures`），返回包增删与版本变化 |
| `switch` | `(flake_uri?, mode?, validate?, full_log?)` | 激活（`sudo -n nixos-rebuild switch`）。**先记 `rollback_generation`**，成功后返回结构化 `summary`（变更的 unit、构建的 derivation 数、包 delta、systemd 健康），日志裁成 tail |
| `generations` | `(action="list"\|"rollback", mode?, generation?)` | 列 generation / 回滚到上一代或指定代 |

**第二层 · Config introspection（"每个都能封顶或结构化 Nix 输出，否则宿主会在原始上下文里付这个钱"）**

| 工具 | 签名 | 干什么 |
|---|---|---|
| `eval_config` | `(attr, flake_uri?, mode?)` | 求**这台机器上**某配置属性的最终合并值（经过所有 module/overlay）。支持**传 list 批量** |
| `locate_option` | `(attr, flake_uri?, mode?)` | 某 option 由哪些文件声明、哪些文件定义、各贡献什么值——**从 mcp-nixos 的"发现"到"改哪个文件"的桥** |
| `check` | `(level, flake_uri?, mode?)` | 验证阶梯，由快到慢：`lint`（statix + deadnix）→ `dry-build` → `dry-activate`（仅 NixOS） |

> **注意 `switch` 默认没有校验门**。作者的选择是"**让 agent 自己组合 check → diff → switch**"（`switch` 的 docstring 原文：`Switch with no implicit validation gate; the agent composes check -> diff -> switch itself`）。只有显式传 `validate=True` 才先用 `check("dry-build")` 挡一道。这是**把编排权交给模型**的设计取向。

### 3.4 统一 envelope 协议：这个项目的核心抽象

`runner.envelope()`（A 级，源码直读）产出的回执形状：

```python
{
  "status": "ok" | "degraded" | "failed" | "no_target" | "unknown_host"
            | "unknown_generation" | "target_locked" | "remote_ref_rejected"
            | "preflight_failed" | "invalid_level" | "tool_missing" | "not_applicable",
  "resolved_target": "...",     # 实际解析到的目标，绝不隐含
  "command": ["sudo", "-n", "/nix/store/.../nixos-rebuild", "switch", ...],  # 实际跑的命令
  "output": "...",              # 默认裁剪过的日志
  "first_error": "...",         # 失败时：第一行像 error 的 stderr
  "error_detail": {...},        # 失败时：logparse 解出的 {message, file, line, column, trace}
  "raw_bytes": N,               # 记账（会被插桩剥离，模型看不到）
  "returned_bytes": N,          # 记账（同上）
}
```

**三个设计原则**（源码可验证）：

1. **绝不隐含**。`resolved_target` 和 `command` 一定回显。`docs/usage.md` 原文（A 级）："Responses that resolve a target and run one command echo `resolved_target` and the exact `command` run, **so nothing is silently implicit**."
2. **失败时主动预取**。`envelope()` 在 `status == "failed"` 时**自动**填 `first_error`（`runner.extract_first_error`，找第一个 `error:` / `error (` / `error[` 开头的行）和 `error_detail`（`logparse.extract_error_detail`）。**这是替 agent 省掉一次额外调用**。
3. **记账字段不进上下文**。`account()` 写入 `raw_bytes` / `returned_bytes`，`server.py` 的 `instrument()` 在返回给模型前 `strip_accounting()` 剥掉。`runner.py` 注释原文（A 级）：
   > Attach returned_bytes: the serialized size of the envelope minus the accounting fields themselves. **MCP instrument strips both before the model sees the envelope; the usage log reads them first.**

   即**同一个回执对象，usage log 看到完整版，模型看到精简版**。

### 3.5 命令执行：argv 数组 + `resolve_binary`（配合 sudoers 的关键）

`runner.run()`（A 级）：

```python
proc = subprocess.run(
    argv,                       # ← list，不是字符串
    capture_output=True,
    text=True,
    errors="replace",
    cwd=cwd,
    timeout=effective_timeout,  # 默认 30 分钟，可用 NIX_AGENT_COMMAND_TIMEOUT 覆盖
)
```

- **`argv` 是 list，全程无 shell 解释** → 没有命令注入面。
- `FileNotFoundError` 和 `TimeoutExpired` 都被**捕获并转成结构化 RunResult**，而不是抛异常。
- **`resolve_binary()` 是整套 sudo 设计的地基**（A 级，源码注释原文）：
  ```python
  def resolve_binary(name: str) -> str | None:
      """Realpath of a binary on PATH, or None. Sudo NOPASSWD rules match
      the resolved store path, not the PATH name, so sudo'd commands must
      use this."""
      found = shutil.which(name)
      return os.path.realpath(found) if found else None
  ```
  因为 NixOS 上 `nixos-rebuild` 实际是 `/nix/store/<hash>-nixos-rebuild/bin/nixos-rebuild`，**sudoers 规则必须匹配解析后的 store 路径**，否则 NOPASSWD 不生效。所以 `switch` 里是：
  ```python
  nixos_rebuild = runner.resolve_binary("nixos-rebuild") or "nixos-rebuild"
  argv = sudo_argv([nixos_rebuild, "switch", "--flake", target.flake_ref])
  ```
  而 `sudo_argv`（`privilege.py`）就是 `["sudo", "-n", *cmd]`。

### 3.6 上下文预算：三道截断 + 一个护栏

作者对"token 成本"的在意程度体现在四处（A 级）：

| 机制 | 常量 / 位置 | 行为 |
|---|---|---|
| **输出截断** | `OUTPUT_CAP = 64_000`（runner.py） | 超限则保留**头一半 + 尾一半**，中间插 `... [nix-agent: N bytes truncated] ...` |
| **成功日志裁尾** | `TAIL_CAP = 2_000` | `switch` 成功后只回最后 2000 字符 + `log_truncated: true`；要全量得传 `full_log=True` |
| **eval 尺寸护栏** | `GUARD_CAP = 2048`（tools/eval.py） | 超 2 KB 的 JSON：**dict 降级成 attr 名列表**、**list 降级成长度**、标量降级成头切片，都带 `truncated: true` + `hint` |
| **health 日志限流** | `JOURNAL_TAIL_UNITS = 5`（health.py） | 新失败的 unit 只给前 5 个抓 journal tail，避免 mass-failure 时烧 token |

**实测效果**（`docs/usage.md`，作者 2026-07-07 在真实 NixOS 笔记本上采集，C 级但给了具体环境 `Nix 2.34` / `/home/rupan/nixos#laptop`）：

| 操作 | raw bytes | returned bytes | 说明 |
|---|---|---|---|
| `diff` | 338 | 1,431 | 近乎空 diff 时 envelope 元数据占主导；diff 越大收益越大 |
| `eval_config("environment.systemPackages")` | **13,500** | **394** | 原始值是巨大的 store path 列表，护栏塌缩成"长度 + 头切片" |
| `locate_option("environment.systemPackages")` | 24,066 | 20,396 | **95 个定义文件**，每个都接近各自的 per-entry 护栏；这个 option 本来就定义在很多地方，所以省得少 |

> **注意第 3 行是个诚实的反例**：作者自己在文档里承认 `locate_option` 在这个 option 上"省得有限"，它进工具集的理由是"**一次调用回答'哪个文件设置了它'**"，而不是"封顶一个 firehose"。

### 3.7 权限模型：`sudo -n` + NixOS module 的窄 sudoers（本项目最值钱的资产）

`nix/module.nix`（A 级，全文件 4,392 B）——这是**可以直接抄到任何 NixOS 配置里**的部分：

**四个 option**：

| option | 类型 | 默认 | 说明 |
|---|---|---|---|
| `programs.nix-agent.enable` | bool | — | 安装 MCP server 包 |
| `programs.nix-agent.package` | package | flake 的 default | |
| `programs.nix-agent.flake` | nullOr path | `null` | 配置 flake 工作树的**绝对路径**；设置后 wrap 二进制注入 `NIX_AGENT_FLAKE` |
| `programs.nix-agent.privilegedAutomation.enable` | bool | **`false`** | 免密 sudo 的开关 |
| `programs.nix-agent.privilegedAutomation.user` | str | — | 被授权的用户 |
| `programs.nix-agent.usageLog.enable` | bool | `false` | 注入 `NIX_AGENT_USAGE_LOG=1` |

**生成的 sudoers 规则（全部 `NOPASSWD`）**——注意**窄到什么程度**（A 级，源码直读）：

```nix
generationCommands = [
  { command = "${nixosRebuild} switch --rollback"; options = [ "NOPASSWD" ]; }
  { command = "${nixEnv} -p /nix/var/nix/profiles/system --switch-generation *"; options = [ "NOPASSWD" ]; }
  { command = "/nix/var/nix/profiles/system/bin/switch-to-configuration switch"; options = [ "NOPASSWD" ]; }
];
flakeCommands = lib.optionals (flakeDir != null) [
  { command = "${nixosRebuild} dry-activate --flake ${flakeDir}*"; options = [ "NOPASSWD" ]; }
  { command = "${nixosRebuild} switch --flake ${flakeDir}*";        options = [ "NOPASSWD" ]; }
];
```

**三条硬约束**（`docs/privileged-automation.md` 原文，A 级）：

1. **`--flake` 参数被钉死在 `<flakeDir>*`**。原文："Do not grant a wildcard flake ref."
2. **绝不授权 store 路径二进制**。原文："Never grant NOPASSWD on a store-path binary, and never write a sudoers wildcard over `/nix/store/*/bin/switch-to-configuration`."——而是走**profile 路径** `/nix/var/nix/profiles/system/bin/switch-to-configuration`（这是稳定的符号链接，而 store 路径每次构建都变）。
3. **`flake` 未设置时降级**：只发 rollback / generation-switch 规则，**不发 rebuild/switch 规则**，并产生一条 `warnings`。源码里的 warning 文本（A 级）明确说明这一点。

**作者自己承认这个 pin 不是安全边界**（`module.nix` 的 option description 原文，A 级）：

> This pin is an **anti-footgun** for privileged activation, **not a security boundary**.

`docs/privileged-automation.md` 把话说得更透（A 级）：

> `$NIX_AGENT_FLAKE` ... is an **anti-footgun, not a security boundary**. The agent can still edit the pinned tree and, if it can edit MCP config, the pin in `.mcp.json`. **The privilege boundary that actually runs as root is sudoers.**

**这是本项目最诚实、也最值得学的一句**：pin 防的是"手滑指错目录"，真正的 root 边界只有 sudoers。

**`privilege.py` 的失败诊断**（A 级）：`sudo -n` 失败（无 TTY / 无 askpass）时匹配 `sudo: (a terminal is required|a password is required|no askpass program|no tty present)`，返回结构化诊断：

```python
{
  "cause": "sudo could not authenticate non-interactively",
  "detail": "...nix-agent invokes sudo -n with the resolved store path of the binary
             so a missing NOPASSWD rule fails immediately; a NOPASSWD rule must match
             that exact argv (without the sudo -n prefix).",
  "command_form": argv,
  "fixes": ["Enable programs.nix-agent.privilegedAutomation ...", "Lower trust: set SUDO_ASKPASS ..."],
}
```

**"失败时告诉你哪个 argv 没匹配上、怎么修"**——这比"permission denied"有用得多。

### 3.8 目标解析与防呆（`target.py`）

`switch` / `check("dry-activate")` 会跑 `prepare_privileged_target()`，做四道防呆（A 级）：

| 检查 | 返回 status | 说明 |
|---|---|---|
| **远程 flake ref 拒绝** | `remote_ref_rejected` | `github:` / `gitlab:` / `sourcehut:` / `git+` / `http(s)://` / `ssh://` / `flake:` 前缀全拒。原文注释："an anti-footgun so the MCP server is not the **confused-deputy path to root activation**" |
| **pin 不匹配拒绝** | `target_locked` | 设了 `$NIX_AGENT_FLAKE` 时，指到别的目录就拒（`NIX_AGENT_ALLOW_REMOTE=1` 只能跳过 remote 检查，**跳不过 target_locked**） |
| **相对路径要求** | `no_target` | 特权操作要求绝对路径；`.` / `./` 在设了 pin 时解析成 pin 目录 |
| **`flake.nix` 存在性** | `no_target` | 目录里必须有 `flake.nix` |

**还有一个刻意的"不搜索"决策**（A 级，源码注释原文）：

> cwd walk-up is **deliberately NOT searched**: an MCP server's cwd is usually the caller's project dir (which may carry an **unrelated `flake.nix`**), so it is a **wrong-flake hazard**.

即：**宁可报错要求显式指定，也不猜**。搜索顺序是 env 覆盖 → `/etc/nixos` → `~/nixos` / `~/.config/nixos` / `~/nix-config` / `~/nixos-config`。

`hostattr.py` 处理"flake 里的主机名跟本机 hostname 对不上"：`matched_hosts()` 支持唯一前缀/后缀/FQDN 匹配，**有歧义就返回空** → 工具返回 `unknown_host` 并**列出 flake 里的全部 host 名**（`unknown_host_envelope`），而不是瞎试。

### 3.9 健康检查：switch 前后的 failed unit diff

`health.py`（A 级，2,448 B，作者在文件头写明设计原则）：

> Failed-unit snapshots around a switch. **Everything degrades to a note; health probing must never fail a switch envelope.**

`switch` 流程：switch 前 `failed_units()` 快照 → 跑 switch → `health_report(before, mode)` 对比，输出：

```python
{
  "newly_failed": [{"unit": "...", "log_tail": "..."}],  # 只前 5 个带 journal tail
  "resolved": [...],        # 之前失败现在好了
  "still_failed": [...],    # 一直失败
}
```

**如果 switch 成功但有 unit 新失败，`status` 变成 `"degraded"`**（不是 `ok`），并附 `hint` 建议回滚。这是一个**把"部分成功"显式建模**的例子——大多数工具只有 ok/fail 两态。

`failed_units()` 自己也有降级链：先试 `systemctl --failed --output=json`，JSON 解析失败退到 `--plain --no-legend` 文本解析，再失败返回 `(None, "systemctl --failed unavailable; health check skipped")`。

### 3.10 Usage log：把"采纳率"做成可测量的

`metrics.py`（16,915 B，**全项目最大文件**）——这不是普通的日志，而是一个**采纳度度量系统**。

`v0.12.0` CHANGELOG（A 级）说明它记录：

> Usage events now record the calling `client` (from `NIX_AGENT_CLIENT`, else inferred: opencode / claude-code / codex / cursor / parent process), `host`, `cwd`, `session`, the full sanitized request `params`, and outcome details (`command` / `op`, `first_error`, `error_message`, `failed_drv`, `output_bytes`, truncation flag).

CLI 侧：

```bash
nix-agent usage                      # 从 JSONL usage log 汇总
nix-agent usage --json               # JSON 输出
nix-agent usage --compare-shell      # ★ 扫交互式 shell 历史（fish/bash/zsh），对比 MCP 工具调用 vs 直接 nix 命令
```

`--compare-shell` 会算出 **MCP share**（"adoption vs shell bypass"）——**回答"agent 到底用没用我的 MCP，还是绕过去直接敲命令"**。这是一个很少见的、把"AI 工作流采纳率"变成可测指标的设计。

### 3.11 配套 Agent Skill 与 CLI 子命令

`nix-agent` **带两个 Skill**（`skills/`，这是它跟 `mcp-nixos` 最大的产品差异）：

| Skill | 大小 | 作用 |
|---|---|---|
| `skills/nix-agent/SKILL.md` | 12,789 B | 完整工作流：7 工具的用法、`mode` 选择（**NixOS vs standalone HM 的判断**）、7 步执行序、token 纪律、5 条硬规则 |
| `skills/nix-agent-init/SKILL.md` | 7,821 B | 仓库 onboarding：跑一次 `inspect-flake`，生成 `AGENT_MAP.md` / `CLAUDE.md` / `AGENTS.md` 符号链接 / `.mcp.json` |

SKILL.md 里几条**判断规则**值得单列（A 级）：

- **"用 MCP 工具，别用 shell"硬规则 + 对照表**（`nixos-rebuild switch` → `switch()`、`nix eval <attr>` → `eval_config(attr)`、`statix`/`deadnix` → `check("lint")`、`nvd diff` → `diff()`、`nix log <drv>` → 读 `failed_derivation.log_tail`、`systemctl --failed` → 读 `summary.health`）。
- **`mode` 选择**（原文："**Do NOT reflexively switch to `home-manager` just because the task touches Home Manager options. That is the most common way to operate on the wrong config.**"）——integrated HM 用 `mode="nixos"`（HM 作为 NixOS module 随系统闭包一起激活），standalone HM 才用 `mode="home-manager"`。
- **token 纪律**："On failure, read three fields in order and **stop**"（`first_error` → `error_detail` → `failed_derivation.log_tail`），"After a switch, read `summary`, do not re-probe"，"**Batch attr checks**"。
- **`full_log=True` 是"deliberate last resort"**，默认用会"defeat the server"。

CLI 子命令（`__main__.py`，A 级，注意这些**不是 MCP 工具**）：

| 子命令 | 作用 | 退出码 |
|---|---|---|
| `nix-agent inspect-flake [flake_uri]` | 打印配置仓库的结构化事实（JSON）——onboarding 用 | |
| `nix-agent bootstrap-rebuild [flake_uri] [--mode]` | 首次特权 switch：先试 `sudo -n`，失败则**打印一条一次性 TTY 命令** | `2`=needs_bootstrap，非 ok/degraded=`1` |
| `nix-agent usage [--path] [--json] [--compare-shell]` | usage 汇总 | |
| （无子命令） | `build_server().run(transport="stdio")` | |

`inspect_flake.py` 的体检项（A 级）：hosts、home_configurations、HM 集成类型（standalone/integrated/unknown/none）、module 目录、是否用 `import-tree`、formatter（treefmt/nixfmt）、lint 工具是否在 PATH、是否有 justfile / CI / `.mcp.json`。**原则写得很清楚**："Facts that cannot be determined are `None`/`'unknown'`, **never guessed**."

### 3.12 安装路径与版本演进

**安装方式**：README 推荐的是一句"把 URL 丢给 coding agent 让它自己装"（A 级原文）：

```
Read https://raw.githubusercontent.com/JEFF7712/nix-agent/main/docs/agent-install.md
and follow every step to install nix-agent on this NixOS system, install the companion
skills, and register nix-agent in my MCP settings for this machine.
```

`docs/agent-install.md` 有 **16,661 B**——一份写给 agent 读的安装说明书。**仓库还提供 4 个宿主的现成配置**（A 级，`examples/`）：

| 宿主 | 配置要点 |
|---|---|
| Claude Code | `mcpServers.nix-agent`，`command: "nix-agent"`，env 开 usage log |
| Codex | `[mcp_servers.nix-agent]` + **`default_tools_approval_mode = "approve"`** |
| Cursor CLI | **`permissions.allow` 逐条列 7 个 `Mcp(nix-agent, ...)` + 3 条 `Shell(sudo nixos-rebuild ...)`** |
| opencode | `mcp.nix-agent`，`type: "local"` |

> **Cursor 那份配置很值得看**：它把 7 个 MCP 工具**和**3 条对应的 shell 命令都加进 allowlist——因为 SKILL.md 的硬规则说"别绕过 MCP 用 shell"，但如果 agent 真绕了，至少那条 shell 也在白名单里（而不是被拒后卡住）。**这是"规则 + 兜底"的双写**。

**版本演进**（CHANGELOG，A 级，节选）：

| 版本 | 日期 | 关键变更 |
|---|---|---|
| `v0.12.0` | 2026-10-02 | usage log 记录 client/host/cwd/session/params；`--compare-shell`；module 加 `usageLog.enable` |
| `v0.11.0` | 2026-08-22 | 首次 rebuild 用 `sudo -n`，失败则打印 TTY 命令而非挂死；Cursor/Codex 显式高信任白名单；**CI 会 evaluate NixOS module 的 sudoers**（断言窄 flake ref、无 `--flake *`、无 store 路径通配符） |
| `v0.10.0` | 2026-08-22 | 把"高信任"定为**文档化默认**：无提示 switch + 免密 sudo |

> **`v0.11.0` 那条 CI 断言值得单独记**：`checks.nixos-module` 会**实际 evaluate module 生成的 sudoers**并断言"没有 `--flake *`、没有 store 路径通配符"。**把安全约束写成 CI 检查**，而不是写在文档里靠人记。

---

## 第 4 章 两者如何配合

### 4.1 标准工作流（`SKILL.md` 的 7 步，A 级）

```
1. Discovery   → mcp-nixos 查包/option（存在什么）
                 eval_config 查机器当前解析成什么
                 locate_option 查该改哪个文件
2. Edit        → 宿主原生文件工具改 .nix
3. Format+Lint → nix fmt（Bash）+ check("lint")
4. dry-build   → check("dry-build")    ← 便宜地抓 eval/build 错误
5. diff        → diff()                ← 展示 changeset
6. switch      → switch()              ← 报告结果 + 保留 rollback_generation
7. 失败处理    → first_error → error_detail → failed_derivation.log_tail
```

`SKILL.md` 补了一句**关键的判断边界**（A 级）：

> Steps 3 through 5 are **judgment calls, not gates**. For a trivial change, going straight to `switch` is fine.

### 4.2 上下文预算的分工

`nix-agent` 的 SKILL.md 里有一段实测说明（A 级）：

> 原生 `nix eval environment.systemPackages` 是 **~13 KB**，尺寸护栏塌缩到 **~400 B**。
> Reach for Bash only for what has no tool: formatting (`nix fmt`), file edits, and remote-target deploys (`--target-host`, `--use-remote-sudo`), which **privileged tools reject by design**.

即三者各守一段：**mcp-nixos 管"世界知识"，nix-agent 管"本机事实 + 变更"，宿主 Bash 管"格式化 + 远程部署"**。

### 4.3 同时安装的注意点

| 冲突点 | 详情 | 处理 |
|---|---|---|
| **FastMCP 版本不重叠** | `mcp-nixos` 要 `fastmcp>=4.0.0`；`nix-agent` 要 `fastmcp>=2.14,<4` | 必须**各装各的环境**（nix 打包天然隔离，或各自 venv）。同一个 Python 环境里装不了两个 |
| **一个只读、一个会写** | 建议先只装 `mcp-nixos` 跑一段，再上 `nix-agent` | |
| **`nix-agent` 默认高信任** | 无提示 switch + 免密 sudo | 不想这样就**不启用** `privilegedAutomation`（Nix option 默认就是 `false`） |

---

## 第 5 章 能做什么：能力清单

### 5.1 `mcp-nixos` 能回答的问题（按 source 归类）

| 你会问 | 调用 | 返回 |
|---|---|---|
| "`firefox` 在 unstable 里吗？" | `nix {action:"info", query:"firefox"}` | 包详情 |
| "有哪些 channel？各自索引到哪个 commit？" | `nix {action:"channels"}` | channel + `Revision (indexed)` / `Branch HEAD` |
| "找 NixOS option 里的 nginx" | `nix {action:"search", query:"nginx", type:"options"}` | option 列表 |
| "home-manager 里配 git 的 option 叫什么？" | `nix {action:"search", query:"git", source:"home-manager"}` | |
| "nix-darwin 的 `system.defaults` 下有什么？" | `nix {action:"browse", query:"system.defaults", source:"darwin"}` | 前缀树 |
| "nixvim 的 telescope 怎么配？" | `nix {action:"search", query:"telescope", source:"nixvim"}` | |
| "NVF 里 `vim.languages.nix` 怎么开？" | `nix {action:"info", query:"vim.languages.nix.enable", source:"nvf"}` | 支持 `programs.nvf.vim.*` 与 `programs.nvf.settings.vim.*` 归一化 |
| "`lib.attrsets.mapAttrs` 的类型签名？" | `nix {action:"info", query:"lib.attrsets.mapAttrs", source:"noogle"}` | |
| "NixOS Wiki 上有 nvidia 的文章吗？" | `nix {action:"search", query:"nvidia", source:"wiki"}` | |
| "nix.dev 的 packaging 教程在哪？" | `nix {action:"search", query:"packaging tutorial", source:"nix-dev"}` | |
| "FlakeHub 上有 nixpkgs 吗？" | `nix {action:"info", query:"NixOS/nixpkgs", source:"flakehub"}` | |
| "`hello` 有二进制缓存吗？" | `nix {action:"cache", query:"hello"}` | narinfo 状态 + 下载大小 |
| "我 flake 的 inputs 有哪些？" | `nix {action:"flake-inputs", type:"list"}` | 需本地 Nix |
| "读一下 `/nix/store/<hash>-<name>/flake.nix`" | `nix {action:"store", type:"read", query:"/nix/store/..."}` | **不需要 Nix** |
| "哪个 commit 发的 firefox 150？" | `nix_versions {package:"firefox", version:"150"}` | commit hash + attr path + 平台 |
| "python 有哪些历史版本？" | `nix_versions {package:"python", limit:5}` | 版本列表 + license + homepage |

### 5.2 `nix-agent` 能做的事

| 你会说 | 会发生什么 |
|---|---|
| "加个 `ripgrep` 到系统包，然后重建" | agent 改配置 → `check("dry-build")` → `diff()` → `switch()` → 报告 `summary`（变更的 unit、构建数、包 delta、systemd 健康） |
| "这次改动会删掉什么包？" | `diff()` → 结构化 `packages`（added/removed/changed） |
| "只检查能不能构建，先别激活" | `check("dry-build")` |
| "激活会改哪些 systemd unit？" | `check("dry-activate")`（仅 NixOS） |
| "`services.openssh.enable` 现在实际是什么值？" | `eval_config(attr="services.openssh.enable")` |
| "一次性告诉我 A、B、C 三个 option 的值" | `eval_config(attr=[...])` → 批量，per-attr `results` |
| "这个 option 在哪个文件设置的？" | `locate_option(attr=...)` → `declarations` + `definitions[{file, value}]` |
| "配完先 lint 一下" | `check("lint")` → statix + deadnix 结构化 `findings` |
| "看看历史 generation" | `generations(action="list")` |
| "上一个 generation 是什么？回滚" | `generations(action="rollback")`（仅上一代） |
| "回滚到第 42 代" | `generations(action="rollback", generation=42)` |
| "这次 switch 之后有服务挂了吗？" | 读 `summary.health`（`newly_failed` / `resolved` / `still_failed`，前 5 个带 journal tail） |
| "构建失败，日志呢？" | 读 `failed_derivation.{drv, log_tail}`——**已经替你跑过 `nix log` 了** |
| "这是什么仓库？" | `nix-agent inspect-flake`（CLI）→ hosts / HM 集成类型 / module 目录 / formatter / lint 工具 |
| "agent 到底用没用 MCP，还是自己敲命令？" | `nix-agent usage --compare-shell` |

### 5.3 两者都不能做的

- **不能部署到远程主机**。`nix-agent` 的 `switch` **只操作本机**（SKILL.md 明说远程部署 `--target-host` / `--use-remote-sudo` 要回退到 Bash，"privileged tools reject by design"）。
- **不能改文件**。`nix-agent` 的工具**不读不写文件**（唯一的读者是 `inspect-flake` CLI 子命令）。
- **不能格式化**。要 `nix fmt` / `nixfmt`，走 Bash。
- **不能替你审 sudoers**。`mcp-nixos` 不碰系统；`nix-agent` 生成 sudoers 但**你得自己检查**（虽然它有 CI 断言）。

---

## 第 6 章 安全模型对比

### 6.1 两套模型的形状

| | `mcp-nixos` | `nix-agent` |
|---|---|---|
| 根本策略 | **不执行**——攻击面只有"读文件 + HTTP 出站" | **窄授权 + 结构化回执**——真的会以 root 跑命令 |
| 输入校验 | `/nix/store` realpath 前缀 + 二进制拒绝 + 大小/行数上限 | argv 数组（无 shell）+ 正则校验（`nix_versions` 包名等） |
| 权限 | 进程本身权限（通常非 root） | `sudo -n` + NOPASSWD 窄白名单 |
| 网络 | 出站 HTTP 到 13 个已知端点 | **无网络**（只跑本地 nix 命令） |
| 关键约束 | 路径不能逃出 `/nix/store/` | `--flake` 钉死在 `<flakeDir>*`；绝不通配 store 路径 |
| 默认值 | 无写能力 | `privilegedAutomation.enable` 默认 **`false`**；但**文档化默认推荐开启** |
| 审计 | 无 | **usage log（JSONL）** + `raw_bytes`/`returned_bytes` 记账 |
| 对"AI 越权"的态度 | 无此问题 | 承认 `$NIX_AGENT_FLAKE` **不是安全边界**，只有 sudoers 是 |

### 6.2 双方各自最诚实的一句话

- `mcp-nixos`（AGENTS.md，A 级）：
  > There is **no persistent cache or database**.
- `nix-agent`（`docs/privileged-automation.md`，A 级）：
  > The privilege boundary that **actually runs as root is sudoers**.

### 6.3 `nix-agent` 的风险面（要清楚知道）

| 风险 | 具体 | 缓解 |
|---|---|---|
| **默认高信任** | 文档化默认 = 无提示 switch + 免密 sudo；`agent-install.md` 让 agent 自己装 | 不启用 `privilegedAutomation`；或从宿主的 `permissions.allow` 里去掉 `switch`/`generations` |
| **宿主 allowlist 看不见 `flake_uri`** | 原文："Host MCP allowlists are tool-name-level and **cannot see `flake_uri`**" | 靠 `target_locked` 防呆 + sudoers 钉死目录 |
| **agent 能改 pin** | 原文："if it can edit MCP config, the pin in `.mcp.json`" | sudoers 才是边界 |
| **实验性** | README 自述 experimental；`v0.x` | 先只读跑 |
| **无许可证风险** | MIT，无此问题 | |

---

## 第 7 章 反直觉与坑

### 7.1 关于 `mcp-nixos`

1. **"需要 Nix"是文档的过度保守**。`store` action（`ls`/`read` 任意 `/nix/store` 路径）**直接读盘，不需要 Nix**；只有 `flake-inputs` 才需要 `nix flake archive`。README 把整个能力区写成"requires Nix"。
2. **只暴露 2 个工具不是"功能少"，是"上下文预算优先"**。17 → 2 的合并是**主动设计**，代价是模型要学会参数矩阵。
3. **`browse` 对 `source=nixos` 是明确拒绝的**，且 `action=options` 是静默别名。不要以为"browse 是通用的层级浏览"。
4. **`action=info` + `source=flakes` 也不支持**，只能 `search`。
5. **返回的是纯文本，不是 JSON**。测试里有断言禁止 JSON/XML 泄漏。如果你在写客户端解析，别按 JSON 解。
6. **`ChannelCache` 的 fallback 结果永不缓存**——这是故意的，不是 bug。
7. **`FALLBACK_CHANNELS` 里的 generation 数字（`latest-50-` / `latest-48-` / `latest-51-`）会腐化**。注释自己承认 "These generations **bit-rot**"。
8. **`.env` 不是 UTF-8 会让整个 server 起不来**（FastMCP 上游问题），且**在 MCP 握手前崩溃**，客户端只看到"启动失败"。仓库用 `FASTMCP_ENV_FILE=os.devnull` 规避。
9. **`overlays.default` 故意不升级调用方的 `python3Packages.fastmcp`**（只加 `pkgs.mcp-nixos`）。想全套升级要额外应用 `overlays.fastmcp4`。有 CI 断言保证这个行为。
10. **`overlays.fastmcp3` 已弃用**，调用会触发 `lib.warn`。
11. **集成测试打真实 API，不打 mock**——所以跑测试需要网络，且会被上游限流/波动影响。
12. **`.claude/agents/` 是开发这个 MCP 用的**，不是给用户的运维 skill。别误以为是产品能力。

### 7.2 关于 `nix-agent`

13. **`switch` 默认没有校验门**。"Switch with no implicit validation gate; the agent composes check → diff → switch itself." 想要门就传 `validate=True`。
14. **`sudoers` 必须匹配解析后的 store 路径**，不是 PATH 名字。所以 `resolve_binary()` 用 `os.path.realpath()`。手写 sudoers 时最容易踩这个。
15. **绝不授权 `/nix/store/*/bin/switch-to-configuration` 通配**——要走 profile 路径 `/nix/var/nix/profiles/system/bin/switch-to-configuration`。
16. **`$NIX_AGENT_FLAKE` 不是安全边界**，作者自己说的。它是防手滑，不是防越权。
17. **`NIX_AGENT_ALLOW_REMOTE=1` 只能跳过远程 ref 拒绝，跳不过 `target_locked`**。
18. **cwd 是刻意不搜索的**——因为 MCP server 的 cwd 常是调用者的项目目录，可能带无关的 `flake.nix`。**这是个 wrong-flake 隐患**，所以设计上拒绝搜索。
19. **`mode` 默认 `nixos`，不要因为任务涉及 HM 就改成 `home-manager`**。SKILL.md 说这是"最常见的操作错配置的方式"。
20. **`locate_option` 对"定义在 95 个文件"的 option 省不了多少 token**（24 KB → 20 KB）。作者自己在文档里承认了。它的价值是"一次调用回答哪个文件"。
21. **`failed_derivation.log_tail` 已经替你跑过 `nix log` 了**，别再跑一次。
22. **`raw_bytes` / `returned_bytes` 不在 MCP 回执里**（被插桩剥离），只在 usage log 里。别去 MCP 结果里找。
23. **`status: "degraded"` ≠ 成功**。它表示"激活成功但 unit 新失败"，SKILL.md 要求"treat that as a problem, not success"。
24. **裸 `generations(action="rollback")` 只回上一代**，不是回 `rollback_generation`。要精确回滚必须显式传 `generation=<id 或 path>`。
25. **`fastmcp>=2.14,<4` 与 `mcp-nixos` 的 `>=4.0.0` 不重叠**——同一个 Python 环境装不了两个。
26. **`nix-agent` 的 `check("dry-activate")` 在 standalone HM 下返回 `not_applicable`**（HM 没有 dry-activate）。
27. **`inspect-flake` 不是 MCP 工具**，是 CLI 子命令。模型看不到它。
28. **`bootstrap-rebuild` 是"首次特权 switch"的兜底**：NOPASSWD 尚未生效时，它打印一条**一次性 TTY 命令**而不是挂死在密码提示上。

### 7.3 关于两者关系

29. **它们不是替代关系**。`nix-agent` 的 README 主动说"它**配合** `mcp-nixos`"。想只装一个的话：只读需求装 `mcp-nixos`，会改配置才加 `nix-agent`。
30. **`nix-agent` 的星标只有 16，但代码质量不低**（154 KB 测试 / 100 KB 实现、CI 断言 sudoers、envelope 协议统一）。**星标在这里严重低估了工程投入**——它太新（2026-03 创建）且面向 NixOS 窄人群。
31. **`mcp-nixos` 已进 nixpkgs**（`pkgs.mcp-nixos`），`nix-agent` 没有。这是"长期可维护性"的一个实际差别。

---

## 第 8 章 未核实 / 存疑

| # | 事项 | 状态 |
|---|---|---|
| 1 | `nix-agent` 的 `raw_bytes` / `returned_bytes` 实测数字（13,500 → 394 等） | **C 级**：来自 `docs/usage.md`，作者 2026-07-07 在 NixOS 笔记本（Nix 2.34）自采，未独立复现 |
| 2 | `mcp-nixos` 的 "~1,030 tokens total" | **C 级**：README 自述，未用 tokenizer 独立核验 |
| 3 | 两个 MCP 的**端到端实测**（真的部署、真的 switch） | **未做**：本报告全部结论来自元数据 + 源码直读 + 官方文档，**未实际运行任一 MCP** |
| 4 | `mcp-nixos` 11 个数据源的**当前可用性** | **未做**：未逐个 curl 验证端点在线（端点常量已从 `config.py` 直读，但未做 HTTP 探测） |
| 5 | `nix-agent` 的 `flake.nix` 是否能实际构建 | **未验证**：未跑 `nix build` |
| 6 | `nix-agent` 的 sudoers 生成结果 | **未在真机验证**：`module.nix` 源码已直读，CI 断言存在，但本机非 NixOS，无法 evaluate |
| 7 | 两项目的**许可证兼容性**（同时装） | MIT × MIT，无冲突，但 FastMCP 版本不重叠是**实际障碍**（非法律障碍） |
| 8 | `mcp-nixos` 的 `RELEASE_NOTES.md`（50,767 B）内容 | 未细读，只从 `pyproject.toml` 确认版本 `3.1.0` |
| 9 | `nix-agent` 的 `site/`（Next.js 文档站，含 GLSL shader 雪花动画） | 未细看，与本报告主题无关 |

---

## 附录 A · 完整工具签名

### A.1 `mcp-nixos`

```python
# 工具 1
nix(action: str = ..., query: str = "", source: str = "nixos",
    type: str = "packages", channel: str = "unstable",
    limit: int = 20, version: str = "latest", system: str = "") -> str

# 工具 2
nix_versions(package: str, version: str = "", limit: int = 10) -> str
```

### A.2 `nix-agent`

```python
build(flake_uri: str | None = None, mode: str = "nixos") -> dict
diff(flake_uri: str | None = None, mode: str = "nixos") -> dict
switch(flake_uri: str | None = None, mode: str = "nixos",
       validate: bool = False, full_log: bool = False) -> dict
generations(action: str = "list", mode: str = "nixos",
            generation: int | str | None = None) -> dict
eval_config(attr: str | list[str], flake_uri: str | None = None,
            mode: str = "nixos") -> dict
locate_option(attr: str, flake_uri: str | None = None,
              mode: str = "nixos") -> dict
check(level: str, flake_uri: str | None = None, mode: str = "nixos") -> dict
# level ∈ {lint, dry-build, dry-activate};  mode ∈ {nixos, home-manager}
```

CLI（非 MCP）：

```bash
nix-agent inspect-flake [flake_uri]
nix-agent bootstrap-rebuild [flake_uri] [--mode nixos|home-manager]
nix-agent usage [--path P] [--json] [--compare-shell]
nix-agent                      # 无子命令 → 启动 stdio MCP server
```

## 附录 B · `mcp-nixos` 端点常量表（`config.py` 直读，A 级）

| 常量 | 值 |
|---|---|
| `NIXOS_API` | `https://search.nixos.org/backend` |
| `NIXOS_AUTH` | `("aWVSALXpZv", "X8gPHnzL52wFEekuxsfQ9cSh")`（**硬编码的只读凭据**） |
| `BASE_CHANNELS` | `unstable → nixos-unstable`、`25.05`、`25.11` |
| `FALLBACK_CHANNELS` | `unstable → latest-50-nixos-unstable`、`stable → latest-50-nixos-26.05`、`25.11 → latest-48-nixos-25.11`、`beta → latest-50-nixos-26.05` |
| `HOME_MANAGER_URL` | `https://nix-community.github.io/home-manager/print.html` |
| `DARWIN_URL` | `https://nix-darwin.github.io/nix-darwin/manual/index.html` |
| `FLAKE_INDEX` | `latest-51-group-manual`（fallback，正常从 `_cat/aliases` 发现） |
| `FLAKEHUB_API` | `https://api.flakehub.com` |
| `NIXVIM_OPTIONS_CHUNKS_BASE` | `https://nix-community.github.io/nixvim/search/data/options/chunks` |
| `NVF_OPTIONS_URL` | `https://nvf.notashelf.dev/options.html` |
| `WIKI_API` | `https://wiki.nixos.org/w/api.php` |
| `NIXDEV_SEARCH_INDEX` | `https://nix.dev/searchindex.js` |
| `NOOGLE_API` | `https://noogle.dev/api/v1/data` |
| `NIXHUB_API` | `https://search.devbox.sh` |
| `CACHE_NIXOS_ORG` | `https://cache.nixos.org` |
| `MAX_FILE_SIZE` | `1024 * 1024`（1 MB） |
| `DEFAULT_LINE_LIMIT` / `MAX_LINE_LIMIT` | `500` / `2000` |
| `KNOWN_SOURCES` | 11 个 source 名（用于区分 flake 路径与 source 名） |

## 附录 C · 关键常量速查

| 项目 | 常量 | 值 |
|---|---|---|
| `mcp-nixos` | `ChannelCache._DISCOVERY_RETRY_COOLDOWN` | `30.0` s |
| `mcp-nixos` | `ChannelCache._ROLLOVER_RECHECK` | `300.0` s |
| `mcp-nixos` | `_BRANCH_REV_TTL`（base.py） | `600.0` s |
| `mcp-nixos` | `_BROWSE_DISPLAY_LIMIT` | `100` |
| `mcp-nixos` | `_MAX_QUERY_LEN` | `200` |
| `mcp-nixos` | ES rescore weight | `20.0`（`1.0 / len(package_attr_name)`） |
| `nix-agent` | `runner.OUTPUT_CAP` | `64_000` |
| `nix-agent` | `runner.TAIL_CAP` | `2_000` |
| `nix-agent` | `runner.COMMAND_TIMEOUT` | `30 * 60` s |
| `nix-agent` | `eval.GUARD_CAP` | `2048` |
| `nix-agent` | `health.JOURNAL_LINES` / `JOURNAL_TAIL_UNITS` | `20` / `5` |
| `nix-agent` | `_BRANCH_REV_TTL` | — |

---

*本报告全部事实来自 GitHub REST API 元数据、仓库全量文件树、以及 28 个源文件的直接读取。证据等级在正文中逐处标注。所有数字均可用本报告所述方法复现。*
