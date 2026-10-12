# nixos-agent-port — NixOS 运维 agent 的规范 + 工具面（合并版）

**一句话**：`nixi-port/` 给的是"正确的判断规则"，但那些规则要靠 agent 用 shell 去执行，
**判断和执行之间有缝**。这个 port 把两个真实 MCP 接进那条缝：
`mcp-nixos`（只读知识层，2 工具）负责**防幻觉**，`nix-agent`（执行层，7 工具）负责
**防"我以为改好了"**。判断规则来自 nixi，工具语义来自两个 MCP 的源码。

**它是什么**：一套可加载的 agent 资产（SOUL 片段 + AGENTS.md + 2 个技能包 + 1 个知识库 + 1 份 MCP 配置）。
**它不是什么**：不是可执行程序，不含任何上游源码，**强制力必须由你自己在宿主侧补上**（见 §5）。

---

## 1. 装到哪

### 前置：两个 MCP 都得能跑

```bash
# 知识层 —— 不需要装 Nix，纯 HTTP
nix run github:utensils/mcp-nixos -- --help
# 或非 NixOS：uvx mcp-nixos

# 执行层 —— 必须在 NixOS 上，且要配 sudoers
nix-agent --help        # 由 nix-agent 的 NixOS module 提供
```

> ⚠️ **两者装不进同一个 Python 环境**：`mcp-nixos` 要 `fastmcp>=4.0.0`，
> `nix-agent` 要 `fastmcp>=2.14,<4`，区间不相交。走 `nix run` / 两个 venv 天然隔离。

### Hermes Agent

```bash
# ① 人格（追加，不是替换）
cat nixos-agent-port/SOUL.append.md >> "${HERMES_HOME:-$HOME/.hermes}/SOUL.md"

# ② MCP 配置
#    把 nixos-agent-port/hermes/mcp-servers.snippet.yaml 里的 mcp_servers 段
#    合并进 ~/.hermes/config.yaml（Windows: %LOCALAPPDATA%\hermes\config.yaml）
#    ★ 从"阶段 0 —— 只读试用"开始，跑两周再升级

# ③ 技能包（用户级）
cp -r nixos-agent-port/skills/nixos-query ~/.hermes/skills/
cp -r nixos-agent-port/skills/nixos-ops   ~/.hermes/skills/

# ④ 项目级入口（放进你的 NixOS 配置仓库根目录）
cp nixos-agent-port/AGENTS.md /etc/nixos/AGENTS.md
```

Hermes 项目级优先级：`.hermes.md` > `AGENTS.md` > `CLAUDE.md` > `.cursorrules`。

### OpenClaw

```bash
cp -r nixos-agent-port/skills/* ~/.openclaw/skills/
cp nixos-agent-port/AGENTS.md /etc/nixos/AGENTS.md
# MCP 段同样合并进 OpenClaw 的配置文件（字段名与 Hermes 一致）
```

### OpenAI Codex

```bash
cp nixos-agent-port/AGENTS.md /etc/nixos/AGENTS.md
cp -r nixos-agent-port/skills /etc/nixos/skills/
# MCP：见 nix-agent 仓库自带的 examples/codex-config.toml
```

### Claude Code

```bash
cp -r nixos-agent-port/skills/* ~/.claude/skills/
# MCP：见 nix-agent 仓库自带的 examples/claude-code-mcp.json
```

### 通用（任何读 AGENTS.md 的 agent）

Cursor / Aider / Gemini CLI / Windsurf / Cline / Zed / Amp 都读 `AGENTS.md`。
把它放在 NixOS 配置仓库根目录即可，它会指向 `skills/`。

### 知识库怎么用

`kb/` 是 [llm-wiki](https://github.com/karpathy/llm-wiki) 格式（三层：素材 / wiki 页 / schema）。
它**不喂给运维 agent**（那是 `skills/` 的事），而是给**以后要自己写 MCP 或运维 agent 的人**看。
`kb/SCHEMA.md` 定义了标签表、证据等级（A/B/C/D）与写页规则，agent 可以按它继续追加。

---

## 2. 目录结构

```
nixos-agent-port/
├── AGENTS.md                          # 跨 agent 入口：5 铁律 + 两 MCP 分工 + 关键词表
├── README.md                          # 本文件
├── OMITTED-CODE-LOSS.md               # 省略 Go/Python 实现损失了什么（六维分析 + 逐条去向 + 补法）
├── SOUL.append.md                     # 追加到 SOUL.md 的运维人格（英文，4 条 postures）
├── tools/
│   └── skill-lint.py                  # 校验 skill 里的工具名/参数名是否与 MCP 真实签名一致（已实测）
├── hermes/
│   └── mcp-servers.snippet.yaml       # 三阶段 MCP 配置 + 从源码核对的 trust/tools 语义
├── skills/
│   ├── nixos-query/                   # 知识层（mcp-nixos）
│   │   ├── SKILL.md                   # 2 工具、8 action × 11 source、调用配方
│   │   ├── action-source-matrix.md    # 完整组合矩阵 + limit 区间
│   │   └── sources-and-endpoints.md   # 11 数据源的端点/取数/缓存策略
│   └── nixos-ops/                     # 执行层（nix-agent）+ 两 MCP 都不覆盖的区域
│       ├── SKILL.md                   # 决策表 + 12 步执行序 + 失败处理 + mode 选择
│       ├── tool-map.md                # shell 命令 → MCP 工具（绕过 MCP 的代价）
│       ├── envelope-cheatsheet.md     # 回执形状 + 9 种 status + 三种截断
│       ├── confirmation-matrix.md     # 30+ 操作逐条判定 + "用哪个工具"
│       ├── rebuild-and-generations.md # rebuild / generation / 升级 / 包管理
│       ├── sudo-and-secrets.md        # 窄 sudoers 模块 + 凭据处理
│       ├── no-mcp-coverage.md         # 容器/挂载/GPU/多节点/定时任务
│       └── anti-patterns.md           # 反模式 + 任务结束前 6 问
└── kb/                                # llm-wiki 三层知识库
    ├── SCHEMA.md                      # 域、约定、标签表、写页规则
    ├── index.md                       # 目录 + 一句话摘要 + 未核实表
    ├── log.md                         # 追加式操作日志
    ├── concepts/                      # 4 个可复用设计模式
    └── comparisons/                   # 1 个并排分析
```

---

## 3. 转换映射：源码里的什么 → 这里的什么

### 3.1 来自 `utensils/mcp-nixos`（MIT，v3.1.0）

| 上游部件 | 转成 | 说明 |
|---|---|---|
| `server.py` 的 `@mcp.tool()` × 2 + 长 docstring | `skills/nixos-query/SKILL.md` §1–§3 | 2 个工具的 8 参数 + 调用配方 |
| `server.py` docstring 里的 `INTENTS → CALLS` 表 | `SKILL.md` §3 配方 | 上游**自己**写的意图映射，原样保留 |
| `config.py` 的 `KNOWN_SOURCES` / 端点常量 | `sources-and-endpoints.md` | 11 个数据源逐个：端点 / 取数方式 / 缓存 |
| `sources/nixos.py` 的 `_PACKAGE_RESCORE` | `sources-and-endpoints.md` | `1.0 / len(package_attr_name)`，权重 20.0 |
| `caches.py` 的 `ChannelCache` 六件套 | `kb/concepts/rolling-upstream-cache.md` | 代数计数器 / 冷却 / rollover / fallback 不 memoize |
| `caches.py` 的 `_ALIAS_RE` | 同上 | `latest-<gen>-...` 别名生成 |
| `utils.py` 的 `_validate_store_path` | `SKILL.md` §4.6 + `sources-and-endpoints.md` | `/nix/store/` 边界、拒二进制、拒 >1 MB |
| `action` × `source` 的实际支持情况 | `action-source-matrix.md` | **从源码分支逐条核出**，不是抄 README |
| v3 的 17→2 工具重构 | `kb/concepts/mcp-token-budget.md` | 约 1,030 token 的工具面成本 |

### 3.2 来自 `JEFF7712/nix-agent`（MIT，v0.12.0）

| 上游部件 | 转成 | 说明 |
|---|---|---|
| `server.py` 的 `_TOOLS` 列表 + 每条的 description | `skills/nixos-ops/SKILL.md` §1 | 7 工具，**按上游自己的两档分类**（运维核心 / 配置内省） |
| `runner.py` 的 `OUTPUT_CAP=64_000` / `TAIL_CAP=2_000` | `envelope-cheatsheet.md` | 三种截断机制 |
| `runner.py` 的 `strip_accounting()` | `kb/concepts/mcp-envelope-protocol.md` | **记账字段在模型看到前被剥掉** |
| `runner.py` 的 `resolve_binary()` | `kb/concepts/scoped-sudo-and-pin.md` | `os.path.realpath()` —— 手写 sudoers 最容易踩的坑 |
| `privilege.py` 的 `sudo_argv = ["sudo","-n",*cmd]` | `sudo-and-secrets.md` + 上页 | `-n` = 缺规则立即失败，不挂在密码提示上 |
| `target.py` 的 `_REMOTE_PREFIXES` / `prepare_privileged_target` | `kb/concepts/scoped-sudo-and-pin.md` | 拒远程 flake ref（confused deputy） |
| `tools/switch.py` 的 `rollback_generation` + `degraded` | `SKILL.md` §4 + `envelope-cheatsheet.md` | **先记回滚点，再激活** |
| `tools/check.py` 的验证阶梯 | `SKILL.md` §2–§3 | `lint` → `dry-build` → `dry-activate` |
| `nix/module.nix` 的 sudoers 生成 | `sudo-and-secrets.md` | 可直接落地的 NixOS module |
| `docs/privileged-automation.md` | 上页 + `kb/concepts/scoped-sudo-and-pin.md` | **逐字保留** "anti-footgun, not a security boundary" |
| `health.py` / `hostattr.py` | `SKILL.md` §4 `summary.health` | `degraded` 的判据 |
| `skills/nix-agent/SKILL.md` | `SKILL.md` 骨架 | 上游自己的 skill，作为结构参考 |

### 3.3 来自 `codeberg.org/ewrogers/nixi`（AGPL-3.0）—— 即 `nixi-port/`

见 §4 的合并映射表。

---

## 4. 合并映射：`nixi-port/` 的每个文件去哪了

原则：**按层合并，不按项目合并。** nixi 给"该不该做"，MCP 给"怎么做"，
两者**不是替代关系**，所以是叠一层，不是换一层。

| `nixi-port/` 的文件 | 在 `nixos-agent-port/` 里 | 动作 | 具体改了什么 |
|---|---|---|---|
| `AGENTS.md` | `AGENTS.md` | **扩写** | 3 铁律 → **5 铁律**（加"先查证"、"有工具就别用 shell"）；新增 §3 两 MCP 分工表 |
| `skills/nixos-ops/SKILL.md` | 同路径 | **重写** | 决策表加"用哪个工具"列；新增 §1 七工具、§4 envelope 失败处理与 9 种 status、§5 `mode` 选择（改 HM 前必读） |
| `confirmation-matrix.md` | 同路径 | **扩写** | 30+ 行**原样保留**，加"用哪个工具"列；新增 3 个灰色地带（`check("dry-activate")`、`switch(validate=True)`、降级回滚） |
| `rebuild-generations-upgrades.md` | `rebuild-and-generations.md` | **改名 + 重写** | 从 CLI 命令改写为 **MCP 工具调用**；裸 `rollback` 只回上一代这个坑写明 |
| `secrets-sudo-scope.md` | `sudo-and-secrets.md` | **改名 + 合并** | 并入 `nix-agent` 的 sudoers NixOS module、`realpath` 坑、三级降级方案、宿主对齐表 |
| `containers-mounts-gpu.md` | `no-mcp-coverage.md` §1–§4 | **并入** | 保留配方，**补上判定**："为什么这里没有 MCP 覆盖" |
| `multi-node.md` | `no-mcp-coverage.md` §5 | **并入** | 明确 `nix-agent` **只操作本机** |
| `anti-patterns.md` | 同路径 | **扩写** | 原 8 类保留；新增 MCP 时代 5 类（绕过工具 / 误读回执 / NixOS 语义 / 权限 / 流程）；结尾 6 问自查 |
| `README.md` | `README.md` | **重写** | 加 MCP 层、转换映射、合并映射、失效清单 |
| — | `OMITTED-CODE-LOSS.md` | **新增** | 回答"省略 Go/Python 实现损失了什么"：两种省略的区分、六维损失、13 工具去向、`skill-lint.py` |
| — | `tools/skill-lint.py` | **新增** | skill 层唯一的"编译器"：把 skill 里的工具名/参数名与 MCP 真实签名对账 |
| — | `skills/nixos-query/**` | **新增** | 来自 `mcp-nixos`，nixi 完全没有对应物 |
| — | `skills/nixos-ops/tool-map.md` | **新增** | nixi 里"用 shell"是唯一选项，这里必须给出对照 |
| — | `skills/nixos-ops/envelope-cheatsheet.md` | **新增** | nixi 没有结构化回执这个概念 |
| — | `SOUL.append.md` | **新增** | nixi-port 只给了 AGENTS.md，没有给人格层 |
| — | `hermes/mcp-servers.snippet.yaml` | **新增** | nixi-port 完全没提 MCP 怎么配 |
| — | `kb/**` | **新增** | nixi-port 只有 skills，没有知识库层 |

### 退役（`nixi-port` 里被替换掉的东西）

| 退役项 | 为什么 |
|---|---|
| 文件名 `rebuild-generations-upgrades.md` | 改名为 `rebuild-and-generations.md`（去掉 `-upgrades`，因为升级已并入正文） |
| 文件名 `secrets-sudo-scope.md` | 改名为 `sudo-and-secrets.md`（sudo 是重点，提前） |
| 文件名 `containers-mounts-gpu.md` / `multi-node.md` | 并入 `no-mcp-coverage.md` —— **判定标准从"主题"变成"有没有工具覆盖"**，这是合并带来的认知升级 |
| "用 shell 命令"作为默认执行方式 | 改为 **MCP 优先，shell 兜底**；`tool-map.md` 是这条规则的执法者 |
| 3 铁律的措辞 | 扩到 5 条；原 3 条内容全部保留 |

**没有文件被丢弃。** 每一条 nixi 的判断规则都在新 port 里有落点。

### 为什么要合

| | `nixi-port`（v1） | `nixos-agent-port`（v2） |
|---|---|---|
| 判断规则 | ✅ 完整 | ✅ 完整（保留） |
| 执行手段 | ⚠️ "用 shell 敲这些命令" | ✅ 15 个 MCP 工具 + shell 兜底 |
| 防幻觉 | ❌ 无 | ✅ `nixos-query` |
| 回执语义 | ❌ 无 | ✅ `envelope-cheatsheet.md` |
| 权限落地代码 | ✅ 有 | ✅ 有 + `realpath` 坑 + CI 断言 |
| 人格层 | ❌ 无 | ✅ `SOUL.append.md` |
| MCP 配置 | ❌ 无 | ✅ 三阶段 + 源码核对的语义 |
| 知识沉淀 | ❌ 无 | ✅ `kb/` 4 概念 + 1 对照 |

---

## 5. ⚠️ 转换后失效的部分（必须由宿主持平）

> 本节从**"宿主如何补齐"**的角度列失效项。
> 想知道**"到底损失了什么"**（六维损失分析 + `nixi` 13 工具的逐条去向 + 能补/补不了对照表），
> 看 **[`OMITTED-CODE-LOSS.md`](./OMITTED-CODE-LOSS.md)**。

这是**两个 port 共同的**结构性问题：**skill 是文字，没有强制力。**
nixi 用 Go 代码强制的保证，在 skill 里退化成"请求"。

### 5.1 来自 nixi（Go 代码强制的）

| nixi 的保证 | 为什么在 skill 里失效 | 宿主持平方案 |
|---|---|---|
| **工具级确认门**（`confirmed` 参数不出现在 tool schema，LLM 无法伪造） | 通用 agent 的 tool schema 由宿主生成，skill 改不了 | Hermes `trust: untrusted` + 宿主审批；Codex approval mode |
| **`MonitoredExecutor` 硬拒变更** | skill 只能"要求"agent 只读 | `tumf/mcp-shell-server` 的 `ALLOW_COMMANDS` 只放只读命令 |
| **`/srv/` 边界在工具层拒绝** | 同上 | `ALLOW_PATTERNS` 把路径写进正则 |
| **凭据永不进 LLM 上下文** | 靠宿主的 secret 管理 | 宿主 secret 注入，或手动输入 |
| **输出自动脱敏** | skill 只能要求 | 宿主输出过滤 + agent 自觉 |
| **Levenshtein 节点名纠错 / 批量单次确认 / executor 自动 sudo 前置** | 纯 Go 便利功能 | 由 agent 按 skill 里的规则**模拟** |

### 5.2 来自 `nix-agent`（MCP 代码强制的）—— **这层可以补上**

好消息：这一层的强制力**本来就在 MCP 服务器里**，所以接进宿主后**大部分是真的**：

| 保证 | 状态 | 说明 |
|---|---|---|
| 先记 `rollback_generation` 再 switch | ✅ **真的** | 在 `switch.py` 里，不是提示词 |
| `sudo -n` 缺规则立即失败 | ✅ **真的** | `privilege.py` 硬编码 |
| 拒远程 flake ref | ✅ **真的** | `target.py` 的 `_REMOTE_PREFIXES` |
| pin 目录校验（`target_locked`） | ✅ **真的** | 但**不是安全边界**（见下） |
| 输出截断（64 KB / 2 KB tail） | ✅ **真的** | `runner.py` |
| 记账字段不进模型上下文 | ✅ **真的** | `strip_accounting()` |
| `degraded` 状态的正确语义 | ⚠️ **半失效** | 服务器会报 `degraded`，但**是否回滚由 agent 决定** —— 所以 `SKILL.md` 铁律 #4 必须存在 |
| **真正的 root 边界** | ✅ **在 sudoers 里** | 不在 MCP 里，也不在 skill 里。**你自己写的 NixOS module 就是边界本身** |

### 5.3 ⚠️ 一个必须知道的坑：`trust: untrusted` 会挡住一切

判"写能力"的依据是 MCP annotations 的 `readOnlyHint === true`（**严格等于**）。
`nix-agent` 用 `Tool.from_function` 注册，**不带 annotations** → 7 个工具**全部**被当成写能力
→ `trust: untrusted` 下**连 `diff()` 都弹窗**。

**这是安全换摩擦的取舍，不是 bug。** 三个应对：

1. 用**阶段 0**（`tools.include` 白名单只放 5 个只读工具，`switch`/`generations` 根本不注册）。
   **比 `trust: untrusted` 更有效，且零摩擦** —— 因为模型连"想调"都做不到。
2. 用**阶段 1**（全部 7 个 + `trust: full`），靠**系统侧的 sudoers** 做真边界。
3. 只有在你**确实需要每次人工点击**时才用阶段 2。

**推荐组合：阶段 0 起步 → 稳定后升阶段 1 → 靠 sudoers 兜底。**

### 5.4 结论

> 这个 port 给你的是**正确的判断规则** + **真实的执行工具**。
> **唯一真正以 root 运行的边界是 sudoers**，而 sudoers 要你自己写 ——
> `sudo-and-secrets.md` 给了可直接落地的 module，但**要不要装、装多窄，是你的决定**。

最省力的完整组合：
`AGENTS.md`（判断）+ 两个 MCP（执行）+ **窄 sudoers**（边界）+ `tools.include` 白名单（收窄）。

---

## 6. 许可证

本 port 是**转换产物**，不是任何上游源码的复制品（**未复制任何 Go 或 Python 源码**）。

| 来源 | 许可 | 本 port 用了什么 |
|---|---|---|
| `utensils/mcp-nixos` | **MIT** | 工具签名、端点常量、缓存策略的**事实**与设计说明 |
| `JEFF7712/nix-agent` | **MIT** | 工具签名、envelope 语义、sudoers 设计 |
| `ewrogers/nixi` | **AGPL-3.0** | **仅**其文档中的判断规则与配置片段 |
| NixOS Manual / Home Manager / nix-darwin | MIT | 配置配方 |
| Nix Manual | LGPL-2.1 | 命令语义 |
| NixOS Wiki | MIT | 配置配方 |

**关于 AGPL 的判断**（与 `nixi-port/README.md` 一致）：
本 port 不含 nixi 的 Go 源码，只含从其文档转述的**规范**（确认矩阵、sudo 白名单形态、反模式）。
文档中的事实与规则不受 AGPL 的衍生作品条款约束。**故本 port 不继承 AGPL。**

**建议**：商业或分发前把本 port 整体标为 **MIT**，并保留上表作为来源声明。

---

## 7. 上游来源

| 项目 | 元数据（抓取于 2026-10-12） |
|---|---|
| `utensils/mcp-nixos` | 853★ / 46 fork / MIT / Python / v3.1.0 / 创建 2025-03-20 / 推送 2026-09-05 / 2,747 KB / 已进 nixpkgs |
| `JEFF7712/nix-agent` | 16★ / 2 fork / MIT / Python / v0.12.0 / 创建 2026-03-19 / 推送 2026-10-12 / 1,315 KB / 自述 experimental |
| `ewrogers/nixi` | 0★ / 0 fork / AGPL-3.0 / Go / 仅 v0.1.0 / 最后提交 2026-03-31 / 无测试 |

**转换与合并日期**：2026-10-12

**证据**：本目录的所有事实来自三处 —— ① `../recon/` 里的源码直读与 GitHub API 元数据；
② `../研究报告_NixOS_MCP双项目构建解剖_nix-agent_mcp-nixos.md`（含 31 条坑与证据分级）；
③ 上游官方文档。**两个 MCP 的端到端实测未做**（本机非 NixOS），详见
`kb/index.md` 的"未核实 / 存疑"表。
