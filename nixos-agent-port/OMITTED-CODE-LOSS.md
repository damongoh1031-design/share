# 省略 Go / Python 实现，损失了什么

> **TL;DR** 损失分两类，**不能混为一谈**：
>
> | | 被省略的代码 | 损失 |
> |---|---|---|
> | `nixi`（Go） | **完全没搬**，13 工具 / 50+ action 全部只剩文字 | 🔴 **大**——所有"代码才能做到的事"全丢 |
> | `mcp-nixos` / `nix-agent`（Python） | **没有省略，是外部依赖**——你装上它就在跑 | 🟢 **小**——功能还在，丢的是"能验证它的东西" |
>
> 一句话：**`nixi-port` 丢的是"能力"，`nixos-agent-port` 丢的是"保障"。**
> 前者需要你自己补实现，后者需要你自己补测试。

标签：`nixos` `project-profile` · 证据等级：`A`（源码/文档直读）+ `D`（部分损失项为推断）

---

## 0. 先把两种"省略"分开

这是回答这个问题的前提，搞混了会得出错误结论。

| 维度 | `nixi`（Go） | 两个 MCP（Python） |
|---|---|---|
| 我们做了什么 | 只读它的 `AGENTS.md` + `docs/`，**一行代码没搬** | 只读源码写文档，**代码由你安装** |
| 交付物是 | 它的**规范的转述** | 它的**使用手册** |
| 代码还在吗 | ❌ 不在任何地方 | ✅ 在你机器上跑着 |
| 丢掉的功能 | 全部 Go 实现的功能 | 无（功能都还在） |
| 丢掉的东西 | — | **上游版本漂移时无人发现** |

所以下面 §1–§3 主要讲 `nixi` 的损失（那是真损失），§4 讲两个 MCP 的隐性损失（不是功能，是可验证性），
§5 讲省略代码换来了什么。

---

## 1. 六个维度的损失

按"代码能做到、文字做不到"的性质分类。每项标损失等级：

- 🔴 **全丢** —— 没有任何补救，功能就是没了
- 🟡 **降级** —— 还能用，但从"确定性/强制"降到"靠 agent 自觉"
- 🟢 **保留** —— 新架构里有等价物（可能更强）

### 维度 1：强制力 —— 代码能"拒绝"，文字只能"请求"

这是最根本的一类。**这是 `nixi-port/README.md` §5 已列的 6 项，这里补上它们的机制性质。**

| `nixi` 的保证 | 机制（Go） | 现在 | 为什么文字做不到 |
|---|---|---|---|
| **工具级确认门** | `confirmed` 参数**不写进 tool schema** → LLM 连"伪造"的接口都没有 | 🔴 | tool schema 由宿主生成，skill 改不了 |
| **`MonitoredExecutor` 硬拒变更** | `isMutatingCommand(cmd)` 判定后**直接返回拒绝**，不看 LLM 说什么 | 🔴 | skill 只能"要求只读"，agent 可以不听 |
| **`/srv/` 边界** | 工具层校验路径，`/srv/` 外直接拒 | 🔴 | 同上 |
| **凭据不进上下文** | 掩码 TTY 输入 → 直传工具参数，**中间不过 LLM** | 🔴 | 需要 TTY + 进程内通道，skill 是纯文本 |
| **输出自动脱敏** | 输出流过滤后才返回 | 🔴 | skill 只能要求 agent"展示前先脱敏" |

**注意这 5 项里有 4 项在 `nixos-agent-port` 里仍然没有对应物** —— 因为两个 MCP 也都不管这些。
只有"确认门"这一项，Hermes 的 `trust: untrusted` + 宿主审批能部分顶上。

### 维度 2：确定性 —— 代码每次一样，文字每轮重新解释

| `nixi` 的机制 | 现在 | 说明 |
|---|---|---|
| **`executor.go` 的 `needsSudo`** | 🟡 | 按"命令 / 子命令 / 参数路径"三条规则决定是否前置 sudo。skill 里写成了文字表，**agent 每次自己判断，可能漏、可能过度** |
| **参数逐个 shell-quote** | 🟡 | 代码里是确定性的转义；现在 agent 手拼字符串 → **含空格的参数会被远程 shell 拆错**，也有注入面 |
| **Levenshtein 节点名纠错** | 🟡 | `web-srever` → "did you mean web-server?"。现在靠 agent"发现拼错时给出最接近的真实名"——**它可能不发现** |
| **批量单次确认** | 🟡 | 代码把 N 个操作合成一个确认；现在 agent 可能**重复问**（烦）或**默认已确认**（危险） |
| **退出码 → 语义映射** | 🟢 | `nix-agent` 的 `status` 字段就是干这个的，**比 nixi 更强**（9 种状态） |
| **输出结构化解析** | 🟢 | `nix-agent` 的 envelope 就是干这个的；但 nixi 那 12 个工具（容器/挂载/GPU…）的输出解析**丢了** |

### 维度 3：状态 —— 代码有进程内状态，文字没有

| `nixi` 的状态 | 现在 | 后果 |
|---|---|---|
| **"当前是 monitored 模式"** | 🔴 | 代码里是 Executor 实例的一个字段，**全程不变**。现在没有这个标志，agent 只能靠上下文记住"这台是只读的" → **长对话里会漂移** |
| **"这批操作已确认"** | 🟡 | 代码里是一次状态机迁移；现在靠对话历史 → 可能重复问或误判已确认 |
| **节点配置表**（`config.toml` 的 `[[nodes]]`） | 🟡 | 现在要靠 `MEMORY.md` / `.hermes.md` 承载，**agent 得先读才知道** |
| `nix-agent` 的 `rollback_generation` | 🟢 | **在 MCP 进程里**，不是靠 agent 记 |
| `nix-agent` / `mcp-nixos` 的进程内缓存 | 🟢 | 保留（30s 冷却 / 300s rollover / 目录型缓存） |
| `nixi` 的 SQLite 记忆 | 🟢 | 被 Hermes 自己的记忆机制**替代**（不是丢失） |

**这里有一条重要的推论**：🔴 那一条意味着 —— **"这台机器是只读的"这件事，在 skill 方案里没有任何硬保证**。
它退化成了"agent 记得"。唯一能真正钉住的办法是宿主侧（`ALLOW_COMMANDS` 只放只读命令）。

### 维度 4：只有代码才能做的事（功能本体）

这些**写不出等价 skill** —— 不是"写得不细"，是**介质不支持**。

| 能力 | 为什么 skill 做不到 | 等级 |
|---|---|---|
| **掩码密码输入** | 需要 TTY + 直传通道，密码要绕过 LLM | 🔴 补不了 |
| **硬超时 + kill 挂死进程** | 代码能 `SIGKILL`；agent 只能等或放弃 | 🔴 |
| **并行执行多节点** | Go 的 goroutine；skill 只能写成串行 `for` 循环 | 🔴（部分可外包给 colmena） |
| **原子多步 / 失败隔离** | 代码能回滚半个事务；文字只能"尽量" | 🟡 |
| **流式观察长命令** | 代码能边跑边看边决策；agent 拿到的是一次性回执 | 🟡 |
| **实时拒绝越界路径** | 见维度 1 | 🔴 |
| **并发安全（文件锁 / 连接池）** | 代码里才有；agent 没有并发概念 | 🔴 |
| **类型化返回值** | 🟢 部分保留：`nix-agent` 的 envelope 是类型化的 | 🟢 |

### 维度 5：成本与延迟

| 项 | 说明 |
|---|---|
| **代码干活不烧 token** | `nixi` 的工具把"找对文件 / 拼对命令"在 Go 里做完；现在这部分变成 LLM 的推理 → **token 更多、更慢、方差更大** |
| **但两块是净赚** | ① `mcp-nixos` 的查询层 —— `nixi` **完全没有**，用 `nix search` 的原始输出会贵一个数量级；② `nix-agent` 的 64 KB / 2 KB / 2048 三道截断 —— 实测 `eval_config("environment.systemPackages")` **13,500 B → 394 B** |
| **容器 / 挂载 / GPU / 多节点** | 🔴 **净亏**：这几块现在要 agent 自己拼 shell，每次都重新付"想命令"的成本，且 `nixi` 原本有结构化输出 |

### 维度 6：可验证性 —— 一个最容易被忽略的损失

见 §4 展开。一句话：**`nixi` 有 Go 测试，`nix-agent` 有 CI 断言 sudoers，skill 什么都没有。**

---

## 2. 逐条清单：`nixi` 的 13 个工具现在谁负责

`nixi` 是"13 个硬编码工具 / 50+ action"。
下表把能逐条对上的列出来（`kb/nixi-to-agent-skill-port.md` §2 的映射表口径；
`users`/`network`/`logs`/`files`/`clock`/`system_info` 六项在原映射表里被合并成一行）。

| `nixi` 工具 | action 数 | 现在谁负责 | 损失 |
|---|---|---|---|
| `nixos` | 20 | ✅ **`nix-agent` 7 工具**（build/diff/switch/generations/check/eval_config/locate_option） | 🟢 **升级**：结构化 envelope + 先记回滚点 + 字节护栏 |
| `container` | 11 | ⚠️ agent 自己敲 `podman`（`no-mcp-coverage.md` §1） | 🔴 丢结构化输出 + 丢 `/srv/` 边界强制 |
| `mount` | 5 | ⚠️ agent 自己敲 `mount` / `umount`（§2） | 🔴 丢路径边界强制 |
| `nvidia` | 4 | ⚠️ 改配置 + 敲 `nvidia-smi`（§3） | 🟡 配方保留了，检测/解析丢了 |
| `amdgpu` | 4 | ⚠️ 同上（§4） | 🟡 同上（含 APU 的 ROCm/GTT 处理） |
| `scheduler` | 6 | ⚠️ 写 systemd timer（§6） | 🟡 配方保留 |
| `users` | ? | ⚠️ 改 `users.users.*` / `usermod` | 🟡 |
| `network` | ? | ⚠️ 改 `networking.firewall.*` | 🟡 |
| `logs` | ? | ⚠️ `journalctl` | 🟡 |
| `files` | ? | ⚠️ 宿主原生 Read/Edit/Write | 🟡 **其实更好**（有 diff 预览） |
| `clock` | ? | ⚠️ `timedatectl` | 🟡 |
| `system_info` | ? | ⚠️ `nixos-version` / `lscpu` | 🟡 |
| **（`nixi` 的 agent 本体）** | — | ❌ LLM 客户端 / TUI / Web UI / SQLite 记忆 | 🟢 **被 Hermes 替代**，不算丢失 |

**读法**：
- 🟢 1 项：`nixos` 那 20 个 action —— 这是 `nixi` 的**核心价值**，而它在新架构里**被 `nix-agent` 做得更好**。
- 🔴 2 项：`container` / `mount` —— 这两块丢了"工具层的边界强制"，是真损失。
- 🟡 9 项：配方都在，丢的是"确定性 + 结构化输出 + 每次省下的 token"。
- 🟢 1 项：`nixi` 的 agent 本体（LLM 客户端/TUI/SQLite）—— **这不是损失，是替代**。

**净结论**：`nixi` 最值钱的 1 个工具被**升级**了，11 个被**降级成配方**，
只有 `container` / `mount` 这 2 个丢了安全强制。

---

## 3. 被省略的还有 `nixi` 的"非工具"代码

`kb/nixi-to-agent-skill-port.md` §5 记了刻意没搬的三件事，这里补上它们各自的损失：

| 没搬的东西 | 损失 |
|---|---|
| **Web UI / TUI** | 🟢 无 —— 你用 Hermes 的界面 |
| **SQLite 记忆** | 🟢 无 —— 用 Hermes 的记忆；**但里面已有的历史记忆内容丢了** |
| **LLM 客户端** | 🟢 无 —— 用宿主 |
| **Go 测试套件** | 🔴 **有** —— 见 §4 |
| **`config.toml` 的节点表** | 🟡 要靠 `MEMORY.md` 承载 |

---

## 4. 最隐蔽的损失：skill 没有编译器

这一条独立成节，因为它是**唯一一类"看不见"的损失**。

### 问题

skill 里写了大量对上游 API 的**断言**：

```markdown
switch(flake_uri?, mode?, validate?, full_log?)
eval_config(attr, flake_uri?, mode?)
nix(action="search", query="X", type="options", source="nixos")
```

这些**没有任何东西会验证**。如果 `nix-agent` v0.13 把 `full_log` 改名成 `full`，
或者 `mcp-nixos` v4 把 `action="browse"` 去掉：

- 代码方案：**编译器/测试报错**，CI 拦住
- skill 方案：**静默腐化** —— 文档继续自信地教 agent 调一个不存在的参数，
  直到某次真实任务失败，而且失败原因看起来像"Nix 报错"而不是"文档过期"

### 为什么这块特别危险

| 对比 | `nixi`（Go） | 两个 MCP（Python） | **skill** |
|---|---|---|---|
| 有测试吗 | ✅ Go 测试套件 | ✅ `nix-agent` 154 KB 测试 / `mcp-nixos` 有 pytest | ❌ **无** |
| 有 CI 断言吗 | ✅ | ✅ **`checks.nixos-module` 断言 sudoers 内容** | ❌ **无** |
| 上游变了会怎样 | 编译失败 | 测试失败 | **没人知道** |

**`nix-agent` 的 CI 断言 sudoers 那件事，恰好就是 skill 做不到的范例** ——
它把"安全设计"从文档承诺变成了机器可验证的约束。而我们的 skill 里
`sudo-and-secrets.md` 给的 sudoers 模块，**只靠人照抄**。

### 补救：给 skill 写一个 linter（**已实测，随 port 一起交付**）

这是**唯一能补上"编译器"这一角色的办法**：把 skill 里提到的工具名 / 参数名，
和 MCP 实际暴露的 `tools/list` 对一遍。

脚本落在 **`tools/skill-lint.py`**（可执行，已跑通）。核心逻辑：

```python
#!/usr/bin/env python3
"""skill-lint — 校验 skill 里提到的 MCP 工具名/参数名是否真实存在。

用法: python skill-lint.py <skills_dir> <tools.json>
退出码: 0 = 全部对得上；1 = 发现不存在的工具名或参数名
"""
import json, pathlib, re, sys

tools = json.load(open(sys.argv[2], encoding="utf-8"))
# tools/list 直接返回数组；手写快照可能是 {"tools": [...]}
if isinstance(tools, dict):
    tools = tools.get("tools", [])
known = {
    t["name"]: set((t.get("inputSchema") or {}).get("properties", {}) or {})
    for t in tools
}

# 匹配 `switch(full_log=True)` / `nix(action="search", ...)` 这类写法
CALL = re.compile(r"([a-z_][a-z0-9_]*)\(([^()\n]*)\)")
KWARG = re.compile(r"([a-z_][a-z0-9_]*)\s*=")

problems = []
for path in sorted(pathlib.Path(sys.argv[1]).rglob("*.md")):
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for m in CALL.finditer(line):
            name, args = m.group(1), m.group(2)
            if name not in known:
                continue  # 不是 MCP 工具名（比如 shell 命令），跳过
            for kwarg in KWARG.findall(args):
                if kwarg not in known[name]:
                    problems.append(
                        f"{path}:{lineno}: {name}() 没有参数 `{kwarg}`"
                        f"  —— 可用: {sorted(known[name]) or '(无参数)'}"
                    )

print("\n".join(problems) if problems else "OK: 工具名与参数名全部对得上")
sys.exit(1 if problems else 0)
```

**注意它扫代码围栏内的内容**（有意为之）—— skill 的调用配方大多写在
```python / ```text 块里，跳过它们就等于什么都没查。

**放进 CI**（每次上游发版就跑一遍）：

```yaml
# .github/workflows/skill-lint.yml
- run: npx @modelcontextprotocol/inspector --cli nix-agent --method tools/list > /tmp/tools.json
- run: python skill-lint.py nixos-agent-port/skills /tmp/tools.json
```

**它补上的是**：上游改了参数名 → CI 红。
**它补不上的是**：语义变化（参数名没变但行为变了）、sudoers 内容是否仍然安全、
"agent 是否真的按 skill 做"。

**这个脚本已实测过**（2026-10-12）。用 `nix-agent` / `mcp-nixos` 的**真实签名**
（从 `tools/*.py` 的函数定义直读）建 `tools.json`：

```
$ python skill-lint.py nixos-agent-port/skills tools.json
OK: 工具名与参数名全部对得上          # 退出码 0
```

再用故意写错的探针验证它**不是空转**：

```
$ python skill-lint.py probe/ tools.json
probe/bad.md:3: switch() 没有参数 `full`  —— 可用: ['flake_uri', 'full_log', 'mode', 'validate']
probe/bad.md:4: eval_config() 没有参数 `verbose`  —— 可用: ['attr', 'flake_uri', 'mode']
probe/bad.md:6: nix() 没有参数 `typo`  —— 可用: ['action', 'channel', ...]
                                      # 退出码 1；5 个探针里对的 2 个未被误报
```

> 顺带：`nix-agent` 自己的 CI 断言 sudoers，这是**值得抄的第三件事**（前两件是
> envelope 协议与窄 sudoers）。我们的 `sudo-and-secrets.md` 里的模块，
> 也应该在配置仓库里用 `checks` 断言一遍。

---

## 5. 反向：省略代码换来了什么

不做"损失"的单边叙事。省略实现有实打实的收益：

| 收益 | 说明 |
|---|---|
| **无构建 / 无依赖 / 无测试维护** | 23 个 markdown 文件，`cp -r` 就装完。没有 `go build`，没有 venv |
| **能处理 `nixi` 没预料的场景** | 13 个硬编码工具之外的任何事（比如"分析一个部署 URL"），agent 都能做 |
| **能跟着上游升级** | `nix-agent` 在更新（推送 2026-10-12）；`nixi` **最后提交 2026-03-31，仅 v0.1.0，无测试** —— 绑死 nixi 才是风险 |
| **可审计** | 人可以直接读、改、否决每一条规则；Go 代码不能 |
| **跨宿主** | 同一份 skill 给 Hermes / OpenClaw / Codex / Claude Code 用；`nixi` 只能自己用 |
| **获得 `nixi` 完全没有的能力** | 知识层（`mcp-nixos` 的 11 数据源）是**纯增量**，`nixi` 一个都没有 |

**最关键的一条**：`nixi` 是 0★ / 最后提交半年前 / 无测试的项目。
**把规范搬出来、把实现换成两个活跃维护的 MCP，是升级不是降级。**
损失分析的意义不是"后悔"，而是**知道哪几个洞必须自己补**。

---

## 6. 能补 / 补不了 对照表

| 损失项 | 能补吗 | 怎么补 |
|---|---|---|
| 工具级确认门 | ✅ | Hermes `trust: untrusted` + 宿主审批；或 `tools.include` 白名单直接不注册变更工具 |
| `MonitoredExecutor` 硬拒变更 | ✅ | `tumf/mcp-shell-server` 的 `ALLOW_COMMANDS` 只放只读命令；或 MCP `--read-only` |
| `/srv/` 路径边界 | ✅ | `ALLOW_PATTERNS` 把 `/srv/` 写进正则 |
| 节点名模糊纠错 | 🟡 | skill 里写明规则（已写），agent 模拟 —— **会漏** |
| 批量单次确认 | 🟡 | skill 里写明规则（已写），agent 模拟 |
| 自动 sudo 前置 | 🟡 | skill 里写成三档表（已写），agent 判断 |
| 参数 shell-quote | 🟡 | 靠 agent 小心；**无强制** |
| **"这台是只读的"状态** | ⚠️ | **只能靠宿主**（`ALLOW_COMMANDS`）；skill 层无解 |
| **掩码密码输入** | ❌ | **补不了** —— 需要宿主支持 secret 注入，否则只能手动输入 |
| **硬超时 + kill** | ❌ | 补不了（MCP 服务器可以，但那是上游的事） |
| **并行多节点** | 🟡 | 外包给 `colmena` / `deploy-rs`（它们有并行与失败隔离） |
| **原子多步 / 失败隔离** | 🟡 | 同上 |
| **skill 无编译器** | ✅ | **`tools/skill-lint.py`**（已交付、已实测）+ CI |
| **sudoers 无断言** | ✅ | 抄 `nix-agent`：在配置仓库写 `checks` 断言 sudoers 内容 |
| 容器/挂载/GPU 的结构化输出 | ❌ | 补不了（除非自己写 MCP）；只能接受"agent 读文本" |
| 每次省下的 token | ❌ | 补不了；这部分成本永久转移到 LLM |

**统计**：16 项里 ✅ 可补 6 项、🟡 部分可补 6 项、❌ 补不了 4 项。
**补不了的 4 项全部集中在"需要宿主/OS 层配合"或"需要自己写代码"两类。**

---

## 7. 结论

1. **`nixi` 的损失是真损失，但方向是对的** —— 它的核心（`nixos` 工具 20 action）
   在新架构里被 `nix-agent` **做得更好**（结构化回执 + 回滚点 + 字节护栏 + 9 种状态）。
   丢的是周边 11 个工具的"确定性"与 2 个工具的"边界强制"。

2. **两个 MCP 的代码没有被省略** —— 它们是依赖。所以
   "功能损失"这个问题在 `nixos-agent-port` 上**几乎不成立**；
   真正的损失是**可验证性**（skill 没有编译器、sudoers 没有断言）。

3. **必须自己补的只有 4 件事**，而且都不难：
   - `tools.include` 白名单（不注册变更工具）—— 比 `trust: untrusted` 更有效
   - 窄 sudoers（`sudo-and-secrets.md` 已给模块）
   - `tools/skill-lint.py` 进 CI（§4，**脚本已交付并实测**）
   - `checks` 断言 sudoers（抄 `nix-agent`）

4. **一件事补不了，必须接受**：凭据的掩码输入。skill 只能规范"别写进配置"，
   **做不到"密码不进 LLM 上下文"**。这是这套方案唯一的安全降级，写在这里以免被忘记。

---

## 相关

- [`README.md`](./README.md) §5 —— 转换后失效清单（从"宿主如何补齐"角度）
- [`skills/nixos-ops/no-mcp-coverage.md`](./skills/nixos-ops/no-mcp-coverage.md) —— 两个 MCP 都不覆盖的 6 个区域
- [`kb/concepts/scoped-sudo-and-pin.md`](./kb/concepts/scoped-sudo-and-pin.md) —— 为什么 sudoers 是唯一边界
- [`kb/concepts/mcp-token-budget.md`](./kb/concepts/mcp-token-budget.md) —— 省下的 token 从哪来
- `../nixi-port/README.md` —— v1 的失效清单（6 项）
- `../kb/nixi-to-agent-skill-port.md` —— nixi 转换的完整映射与 5 个坑
