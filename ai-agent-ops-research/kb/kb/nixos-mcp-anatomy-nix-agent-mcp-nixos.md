---
slug: nixos-mcp-anatomy-nix-agent-mcp-nixos
title: NixOS 生态两个 MCP 的构建解剖：JEFF7712/nix-agent（执行层）与 utensils/mcp-nixos（知识层）
tags: [MCP, NixOS, nix-agent, mcp-nixos, FastMCP, envelope-protocol, sudoers, ChannelCache, token-budget, source-code-analysis, JEFF7712, utensils]
updated: 2026-10-12
version: v1
status: stable
---

# NixOS 生态两个 MCP 的构建解剖

## 一句话结论

**这两个 MCP 不是竞品，是同一工作流的两端**：`utensils/mcp-nixos` 是**只读知识层**（"存在什么"，不碰你的机器，甚至不需要装 Nix）；`JEFF7712/nix-agent` 是**执行层**（"你的机器实际解析成什么、能不能构建、switch 会改什么"，真的 `nixos-rebuild` + 写 sudoers）。两者都用 Python + FastMCP，但一个把 17 工具**合并成 2** 榨上下文预算，另一个把 7 工具**拆两层**保结构化语义。

## 元数据对照（GitHub API 实测，2026-10-12）

| 维度 | `JEFF7712/nix-agent` | `utensils/mcp-nixos` |
|---|---|---|
| 定位 | 执行层（改系统） | 知识层（只读） |
| stars / forks | 16 / 2 | **853 / 46** |
| 语言 / 许可 | Python / MIT | Python / MIT |
| created → pushed | 2026-03-19 → **2026-10-12** | 2025-03-20 → 2026-09-05 |
| 版本 | `0.12.0` | `3.1.0` |
| 依赖 | **仅 fastmcp**（`>=2.14,<4`） | fastmcp（`>=4.0.0`）+ requests + beautifulsoup4 |
| 构建后端 | setuptools | hatchling |
| 工具数 | 7（两层） | **2**（从 17 合并） |
| 上下文预算 | 未标注 | **约 1,030 token**（自述） |
| 传输 | **仅 stdio** | stdio + **HTTP**（含 stateless） |
| 实现 / 测试代码 | 18 文件 100,076 B / 22 文件 154,166 B（1.5×） | 20 文件 201,659 B / 13 文件 265,650 B（1.3×） |
| 已进 nixpkgs | ❌ | ✅ `pkgs.mcp-nixos` |
| 自带 Agent Skill | ✅ 2 个（`nix-agent` / `nix-agent-init`） | ❌（`.claude/agents/` 是开发自用） |

> ⚠️ **FastMCP 版本不重叠**：`mcp-nixos` 要 `>=4.0.0`，`nix-agent` 要 `>=2.14,<4`。**同一个 Python 环境装不了两个**，必须各自隔离（nix 打包天然隔离）。

## `utensils/mcp-nixos`：只读知识层

### 架构（5 层，20 个 .py）

| 文件 | 大小 | 职责 |
|---|---|---|
| `server.py` | 30,246 B | 2 个 MCP 工具 + action×source 路由 + 传输启动 |
| `caches.py` | 24,122 B | 6 个进程内缓存类（`ChannelCache` 最讲究） |
| `config.py` | 3,830 B | 全部端点常量 + `KNOWN_SOURCES` |
| `utils.py` | 14,053 B | HTML 解析、路径校验、格式化 |
| `sources/` | 15 文件 | 每个数据源一个模块；`home_manager.py`/`darwin.py` 各仅 ~600 B（复用 `base.py`） |

### 工具面（2 个）

```python
nix(action, query, source="nixos", type="packages",
    channel="unstable", limit=20, version="latest", system="") -> str
nix_versions(package, version="", limit=10) -> str
```

- `action` ∈ search / info / stats / browse / channels / flake-inputs / cache / store
- `source` ∈ nixos / home-manager / darwin / flakes / flakehub / nixvim / nvf / wiki / nix-dev / noogle / nixhub
- **返回纯文本，不是 JSON**（测试有断言禁止 JSON/XML 泄漏）
- `action=options` 是 `browse` 的**静默别名**（因 GitHub #125 小模型混淆）

### 11 个数据源各自的取数策略（这是技术含量所在）

| source | 端点 | 方式 | 缓存 |
|---|---|---|---|
| `nixos` | `search.nixos.org/backend` | **ES `_search` + 手写 query DSL + rescore** | 无 |
| `home-manager` | `.../home-manager/print.html` | 抓 **1 个 4.3 MB 单页**再 BeautifulSoup | `HtmlOptionsCache` |
| `darwin` | `.../nix-darwin/manual/index.html` | 同上 | `HtmlOptionsCache` |
| `nixvim` | `.../nixvim/search/data/options/chunks/N.json` | **按 chunk 拉到 404**（~60 chunk / 17K option） | `NixvimCache` |
| `nvf` | `nvf.notashelf.dev/options.html` | HTML 解析 | `NvfCache` |
| `noogle` | `noogle.dev/api/v1/data` | 一次拉 **4.46 MB JSON** | `NoogleCache` |
| `nix-dev` | `nix.dev/searchindex.js` | 读 **Sphinx 搜索索引** | `NixDevCache` |
| `wiki` | `wiki.nixos.org/w/api.php` | MediaWiki API | 无 |
| `flakehub` | `api.flakehub.com` | REST | 无 |
| `nixhub` | `search.devbox.sh` | REST（版本史 + store path） | 无 |
| `cache` | `cache.nixos.org` | NixHub 解析 store path → 查 `.narinfo` | 无 |
| `store` / `flake-inputs` | **本地 `/nix/store`** | `store` 直接读盘（**不需 Nix**）；`flake-inputs` 需 `nix flake archive` | 无 |

**⭐ ES rescore 复刻上游**（`sources/nixos.py`）：

```python
"rescore_query": {"function_score": {"script_score": {
    "script": {"source": "1.0 / doc['package_attr_name'].value.length()"}}}},
"rescore_query_weight": 20.0,
```
主名越短越优先 → `firefox` 排在 `firefox-esr` 前面。注释说明是复刻上游 `rescoreQuery`（索引里没有等价的"主名长度"信号）。

### ⭐ `ChannelCache`：对接"会滚动的上游"的教科书案例

NixOS channel 名随 Hydra 发布滚动（`latest-<gen>-nixos-<channel>`），硬编码必然腐化。六种真实故障处理：

| 机制 | 常量 | 解决的问题 |
|---|---|---|
| 代数计数器解析 | `_ALIAS_RE = ^latest-(\d+)-nixos-(unstable\|\d+\.\d+)$` | 用 generation 数字判断最新 alias，不硬编码 |
| flake 索引同源发现 | `_FLAKE_ALIAS_RE = ^latest-(\d+)-group-manual$` | 旧 generation 会退休 |
| 失败重试冷却 | `_DISCOVERY_RETRY_COOLDOWN = 30.0` | 避免并发调用者排队各等 10s 超时 |
| rollover 重检 | `_ROLLOVER_RECHECK = 300.0` | Hydra 先建 alias 再填数据，空 alias 结论 5 分钟后过期 |
| **fallback 不 memoize** | `FALLBACK_CHANNELS` | 退休 alias 会 404，fallback 结果**永不缓存**，下次重新发现 |
| 名字/计数分离 | `alias_names` vs `available_channels` | 一次 `_count` 失败不该缩小可解析集合 |
| 线程锁 | `threading.Lock()` | 首请求并发竞争（每次调用过 `asyncio.to_thread`） |

原文注释："These generations **bit-rot**: Hydra retires old aliases, and a retired alias 404s on every query. The cache therefore **never memoizes a fallback result**."

### 安全边界（`/nix/store` 路径，四道防线）

| 防线 | 实现 |
|---|---|
| 绝对路径 | `path.startswith("/")` |
| 逃逸防护 | `os.path.realpath(path).startswith("/nix/store/")`（**先解析再判断**） |
| 大小上限 | `MAX_FILE_SIZE = 1 MB` → `FILE_TOO_LARGE` |
| 二进制拒绝 | 读 8 KB 找 `\x00`；读不了就当二进制（fail-closed） |
| 行数上限 | `DEFAULT_LINE_LIMIT=500` / `MAX_LINE_LIMIT=2000` |

### 工程化

hatchling · mypy `strict` · ruff · pytest(+asyncio/xdist/rerunfailures，默认 coverage) · **集成测试打真实 API 不打 mock** · **release-please** 自动发布（PyPI + 多架构 Docker GHCR/Docker Hub + FlakeHub）· VitePress 文档站 · 5 条安装路径（uvx / nix run / Docker / HTTP / nixpkgs 声明式）

## `JEFF7712/nix-agent`：执行层

### 架构（两层，18 个 .py）

| 文件 | 大小 | 职责 |
|---|---|---|
| `tools/switch.py` | 13,832 B | `switch` + `generations` |
| `metrics.py` | 16,915 B | usage log（**全项目最大文件**） |
| `target.py` | 9,118 B | flake 目标解析 + 防呆 |
| `logparse.py` | 7,010 B | 解析 nvd / diff-closures / Nix 错误 |
| `runner.py` | 5,732 B | 子进程执行 + 截断 + envelope |
| `server.py` | 5,262 B | **只做工具注册 + 计时/记账插桩** |
| `tools/{check,eval,inspect_flake,locate,build}.py` | 4.8–6.7 KB | 各工具 |
| `health.py` / `hostattr.py` / `privilege.py` / `bootstrap.py` | 1.4–2.5 KB | 支撑 |

**核心原则：没有工具直接调 `os/exec`，全走 `runner.run(argv)`；所有工具先 `resolve_target()`。**

### 7 个工具，两层

**Operational core**：`build` / `diff` / `switch` / `generations`
**Config introspection**：`eval_config` / `locate_option` / `check`

```python
build(flake_uri=None, mode="nixos")
diff(flake_uri=None, mode="nixos")
switch(flake_uri=None, mode="nixos", validate=False, full_log=False)
generations(action="list", mode="nixos", generation=None)
eval_config(attr, flake_uri=None, mode="nixos")          # attr 可为 list 批量
locate_option(attr, flake_uri=None, mode="nixos")
check(level, flake_uri=None, mode="nixos")               # lint|dry-build|dry-activate
```

**`switch` 默认没有校验门**（docstring 原文："no implicit validation gate; the agent composes check → diff → switch itself"）。要门就 `validate=True`。

### ⭐ envelope 协议：统一回执抽象

```python
{
  "status": "ok|degraded|failed|no_target|unknown_host|unknown_generation|
             target_locked|remote_ref_rejected|preflight_failed|invalid_level|
             tool_missing|not_applicable",
  "resolved_target": "...",    # 绝不隐含
  "command": ["sudo","-n","/nix/store/.../nixos-rebuild","switch",...],
  "output": "...",             # 默认裁剪
  "first_error": "...",        # 失败时自动填
  "error_detail": {...},       # {message, file, line, column, trace}
  "raw_bytes": N, "returned_bytes": N,   # 记账，插桩剥离，模型看不到
}
```

三条原则：① **绝不隐含**（回显 `resolved_target` + `command`）② **失败时主动预取**（自动填 `first_error` / `error_detail`）③ **记账字段不进上下文**（usage log 看完整版，模型看精简版）。

### ⭐ 上下文预算：三道截断 + 一个护栏

| 机制 | 常量 | 行为 |
|---|---|---|
| 输出截断 | `OUTPUT_CAP = 64_000` | 头一半 + 尾一半，中间插 `... N bytes truncated ...` |
| 成功日志裁尾 | `TAIL_CAP = 2_000` | `switch` 成功只回尾部 + `log_truncated`；全量需 `full_log=True` |
| eval 护栏 | `GUARD_CAP = 2048` | dict 降级成 attr 名 / list 降级成长度 / 标量降级成头切片 |
| health 限流 | `JOURNAL_TAIL_UNITS = 5` | 只给前 5 个新失败 unit 抓 journal tail |

实测（作者 2026-07-07 在真实 NixOS 笔记本，C 级）：

| 操作 | raw | returned |
|---|---|---|
| `eval_config("environment.systemPackages")` | **13,500** | **394** |
| `diff` | 338 | 1,431 |
| `locate_option("environment.systemPackages")` | 24,066 | 20,396 ← **诚实反例，省得少** |

### ⭐ 权限模型（最值钱的资产）

**`resolve_binary()` 是地基**：sudoers NOPASSWD 匹配的是**解析后的 store 路径**，不是 PATH 名。

```python
def resolve_binary(name): 
    found = shutil.which(name)
    return os.path.realpath(found) if found else None
# → sudo_argv = ["sudo", "-n", *cmd]
```

**NixOS module 生成的 sudoers（全部 NOPASSWD，注意窄度）**：

```nix
# generation / rollback（无 flake ref）
"${nixosRebuild} switch --rollback"
"${nixEnv} -p /nix/var/nix/profiles/system --switch-generation *"
"/nix/var/nix/profiles/system/bin/switch-to-configuration switch"
# flake 相关（仅当 flakeDir 已设）
"${nixosRebuild} dry-activate --flake ${flakeDir}*"
"${nixosRebuild} switch --flake ${flakeDir}*"
```

**三条硬约束**：① `--flake` 钉死在 `<flakeDir>*`，**禁止通配 flake ref** ② **绝不授权 store 路径二进制**，走 profile 路径（`/nix/var/nix/profiles/system/bin/...` 是稳定符号链接，store 路径每次构建都变）③ `flake` 未设时**只发 rollback/switch-generation 规则**，不发 rebuild/switch。

**作者自己承认 pin 不是安全边界**（原文）："This pin is an **anti-footgun** for privileged activation, **not a security boundary**. ... The privilege boundary that **actually runs as root is sudoers**."

### 防呆（`target.py`）

| 检查 | status | 说明 |
|---|---|---|
| 远程 flake ref | `remote_ref_rejected` | `github:`/`gitlab:`/`git+`/`http(s)://`/`ssh://`/`flake:` 全拒（"not the confused-deputy path to root activation"） |
| pin 不匹配 | `target_locked` | `NIX_AGENT_ALLOW_REMOTE=1` **跳不过**它 |
| 相对路径 | `no_target` | 特权操作要求绝对路径 |
| **cwd 刻意不搜索** | — | "MCP server's cwd is usually the caller's project dir (may carry an **unrelated flake.nix**) → wrong-flake hazard" |

### 其他亮点

- **`health.py`**：switch 前后 failed unit 快照 diff → `newly_failed` / `resolved` / `still_failed`。**switch 成功但有 unit 新失败 → `status: "degraded"`**（不是 ok），把"部分成功"显式建模。降级链：JSON → 文本 → `(None, note)`，**永不因健康检查失败而让 switch envelope 失败**。
- **`metrics.py`（16.9 KB，最大文件）**：不是普通日志，是**采纳度度量系统**。记录 `client`（opencode/claude-code/codex/cursor）/`host`/`cwd`/`session`/`params`/`first_error`。`nix-agent usage --compare-shell` **扫 fish/bash/zsh 历史，算 MCP share**——回答"agent 到底用没用 MCP，还是绕过去敲命令"。
- **`bootstrap-rebuild`**：首次特权 switch，`sudo -n` 失败时**打印一条一次性 TTY 命令**而非挂死在密码提示（退出码 2 = needs_bootstrap）。
- **`inspect-flake`（CLI，非 MCP 工具）**：仓库体检——hosts / HM 集成类型 / module 目录 / import-tree / formatter / lint 工具 / CI / `.mcp.json`。原则："Facts that cannot be determined are `None`/`'unknown'`, **never guessed**."
- **CI 断言 sudoers**（v0.11.0）：`checks.nixos-module` 实际 evaluate module，断言"无 `--flake *`、无 store 路径通配符"。**把安全约束写成 CI 检查**。

### 配套 Skill 的几条判断规则（值得抄）

- **"用 MCP 工具别用 shell"对照表**：`nixos-rebuild switch`→`switch()`、`nix eval <attr>`→`eval_config(attr)`、`statix/deadnix`→`check("lint")`、`nvd diff`→`diff()`、`nix log <drv>`→读 `failed_derivation.log_tail`、`systemctl --failed`→读 `summary.health`。
- **`mode` 选择**："**Do NOT reflexively switch to `home-manager` just because the task touches Home Manager options. That is the most common way to operate on the wrong config.**" → integrated HM 用 `mode="nixos"`。
- **token 纪律**："On failure, read three fields **in order and stop**"（`first_error`→`error_detail`→`failed_derivation.log_tail`）；"After a switch, read `summary`, **do not re-probe**"。
- **`full_log=True` 是 "deliberate last resort"**。

## 两者如何配合

```
1. Discovery   → mcp-nixos 查包/option；eval_config 查机器实际值；locate_option 查该改哪个文件
2. Edit        → 宿主原生 Read/Edit/Write 改 .nix
3. Format+Lint → nix fmt（Bash）+ check("lint")
4. dry-build   → check("dry-build")
5. diff        → diff()
6. switch      → switch()，保留 rollback_generation
7. 失败        → first_error → error_detail → failed_derivation.log_tail
```

SKILL.md 补的边界："Steps 3–5 are **judgment calls, not gates**. For a trivial change, going straight to `switch` is fine."

## 可复用操作

1. **`ChannelCache` 的"滚动上游"六件套**可直接搬到任何对接会滚动 API 的项目：代数计数器解析 alias、失败冷却、rollover 重检、fallback 不 memoize、名字/计数分离、线程锁。
2. **"print 单页"抓全量文档**：mdBook/Sphinx 类文档站优先找 print/single-page 视图，一次请求换全量目录。
3. **sudoers 用解析后的 store 路径**（`os.path.realpath(shutil.which(...))`），且**绝不通配 store 路径**，走 profile 符号链接。
4. **把"部分成功"建模成第三态**（`degraded`），而不是塞进 ok/fail。
5. **记账字段与回执字段分离**：同一个对象，日志看完整版，模型看精简版（插桩剥离）。
6. **envelope 统一协议 + 失败时主动预取 `first_error`**，替 agent 省一次调用。
7. **错误信息即教学**：拒绝非法参数时把正确调用形状（含用户传的 query）回填进错误文本。
8. **把安全约束写成 CI 断言**（evaluate module 断言 sudoers 窄度），而不是写在文档里靠人记。
9. **采纳度度量**：记录 client 并把 MCP 调用数与 shell 历史对比，得到"MCP share"。
10. **MCP 的 `instructions` 字段（InitializeResult）用来做前置提示工程**——塞"意图→调用"JSON 样例，并明确"即使你觉得你知道答案也要调用"。

## 坑与反直觉

1. **`mcp-nixos` 的 "requires Nix" 是文档过度保守**：`store` action（`ls`/`read` 任意 `/nix/store`）**直接读盘不需要 Nix**；只有 `flake-inputs` 需要。
2. **`browse` 对 `source=nixos` 是明确拒绝**；`action=info` + `source=flakes` 也不支持（只能 search）。`action=options` 是静默别名。
3. **`mcp-nixos` 返回纯文本不是 JSON**。写客户端别按 JSON 解。
4. **`FALLBACK_CHANNELS` 里的 generation 数字会腐化**，注释自认 "bit-rot"。fallback 结果永不缓存是**故意的**。
5. **非 UTF-8 的 `.env` 会让整个 MCP server 起不来**（FastMCP 上游 pydantic-settings 问题），且**在 stdio 握手前崩溃**，客户端只看到"启动失败"。规避：`FASTMCP_ENV_FILE=os.devnull`。**任何写 MCP server 的人都该知道这个故障模式。**
6. **`mcp-nixos.overlays.default` 故意不升级调用方的 `python3Packages.fastmcp`**（只加 `pkgs.mcp-nixos`），有 CI 断言保证。想全套升级需额外应用 `overlays.fastmcp4`。`overlays.fastmcp3` 已弃用。
7. **`nix-agent` 的 `switch` 默认无校验门**——不是 bug 是设计。
8. **`nix-agent` 手写 sudoers 最容易踩的坑**：规则必须匹配 `realpath` 后的 store 路径。
9. **`$NIX_AGENT_FLAKE` 不是安全边界**，作者自己说的。
10. **`NIX_AGENT_ALLOW_REMOTE=1` 只能跳过远程 ref 拒绝，跳不过 `target_locked`。**
11. **`nix-agent` 的 cwd 刻意不搜索**（避免捡到无关 flake.nix），所以非标准布局必须显式设 `NIX_AGENT_FLAKE` 或传 `flake_uri`。
12. **`mode` 默认 `nixos`**，不要因为涉及 HM 就改 `home-manager`——SKILL.md 说这是最常见的操作错配置方式。
13. **`locate_option` 对定义在 95 个文件的 option 省不了 token**（24 KB → 20 KB），作者自己承认。它的价值是"一次调用回答哪个文件"。
14. **`raw_bytes`/`returned_bytes` 不在 MCP 回执里**，只在 usage log。
15. **`status: "degraded"` ≠ 成功**——"activation succeeded but units newly failed"，要当问题处理。
16. **裸 `generations(action="rollback")` 只回上一代**，不是回 `rollback_generation`。
17. **`fastmcp>=2.14,<4` 与 `mcp-nixos` 的 `>=4.0.0` 不重叠**，同环境装不了两个。
18. **`inspect-flake` 不是 MCP 工具**（是 CLI 子命令），模型看不到。
19. **`nix-agent` 的星标（16）严重低估工程投入**（测试/实现 = 1.5×，CI 断言 sudoers，envelope 协议统一）——太新（2026-03 创建）+ 面向 NixOS 窄人群。
20. **`mcp-nixos` 已进 nixpkgs，`nix-agent` 没有**——长期可维护性的实际差别。

## 未核实 / 存疑

| # | 事项 | 状态 |
|---|---|---|
| 1 | `nix-agent` 的 raw→returned 实测数字 | **C 级**：作者自采（2026-07-07，Nix 2.34），未独立复现 |
| 2 | `mcp-nixos` 的 "~1,030 tokens total" | **C 级**：README 自述，未用 tokenizer 核验 |
| 3 | 两个 MCP 的**端到端实测** | **未做**：全部结论来自元数据 + 源码直读 + 官方文档，未实际运行任一 MCP |
| 4 | `mcp-nixos` 11 个数据源**当前可用性** | **未做**：端点常量已直读，但未逐个 HTTP 探测 |
| 5 | `nix-agent` 的 `flake.nix` 能否实际构建 | **未验证**：未跑 `nix build` |
| 6 | `nix-agent` sudoers 生成结果 | **未在真机验证**：源码已直读、CI 断言存在，但本机非 NixOS 无法 evaluate |

## 证据分级

- **A 级**（源码/官方文档直读）：架构、工具签名、常量、envelope 形状、sudoers 规则、缓存机制、`/nix/store` 校验、Skill 内容
- **B 级**（GitHub API 实测）：star/fork/日期/许可/文件树/字节数
- **C 级**（仓库自述）：token 预算、实测字节数、README 能力描述
- **D 级**（推断）：本报告中的判断性结论
