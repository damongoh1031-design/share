# 让 opencode / goose 具备自进化能力 —— 可执行落地手册

> 结论先行：**能**。而且比预期便宜——**opencode 只需 1 个插件文件，goose 只需 1 个插件目录（无需改任何配置）**。
> 本目录是按本机实测（2026-10-16）产出的实物，不是建议。

---

## 0. 先说清楚「自进化」到底是什么

Hermes Agent 的「自进化」不是一个开关，而是 **7 件工程件**。本手册只补 opencode/goose 真正缺的部分。

| # | 工程件 | Hermes 怎么做 | opencode | goose |
|---|---|---|---|---|
| ① | 技能自动创建 | `skills.creation_nudge_interval: 15`（每 15 次工具调用提醒） | ✗ 需自建 | ✗ 需自建 |
| ② | 回合后后台自审 | `background_review` fork 一个 daemon 线程 | ✗ 需自建 | ✗ 需自建 |
| ③ | 技能库 curator | `hermes curator`（provenance + archive/prune/pin） | ✗ 需自建（最小版） | ✗ 需自建（最小版） |
| ④ | 有界持久记忆 | `MEMORY.md` + `USER.md`（2200/1375 字符）+ 每会话注入 | ✗ 需外挂 | △ 有 memory extension |
| ⑤ | **可测量的进化（reward signal）** | `curator usage` 遥测 + idle prune | ✗ 需自建 | ✗ 需自建 |
| ⑥ | 定时/心跳调度 | `hermes cron` | ✗ 用 Windows 任务计划程序 | ✓ 原生 `goose schedule --cron` |
| ⑦ | 跨 harness 共享技能目录 | `skills.external_dirs` → `~/.agents/skills` | ✓ 读 `~/.agents/skills` | ✓ 读 `~/.agents/skills` |
| — | 生命周期钩子 | shell hooks + **首次使用同意名单** | ✓ 26 个事件 | ✓ 8 个事件，`PreToolUse` 可阻断 |

**被推翻的两个常见假设**：
- ❌「opencode/goose 缺 hooks」→ **都缺不了**。opencode 有 `session.idle` / `tool.execute.before|after`；goose 的 `PreToolUse` 甚至能 Deny 工具调用。
- ❌「goose 没有 skills 概念」→ **有**。`~/.agents/skills` 就是它的全局可写技能根（源码注释原文 `Canonical writable location for global user skills`）。

**⑦ 是最大红利**：两家都读 `~/.agents/skills`，所以**一次沉淀，两家复用**。

**⑤ 是分水岭**：只有「自动写技能 + 记忆」而没有成败反馈，那叫**采集**，不叫**进化**。本手册把 ⑤ 列为必做项。

---

## 1. 落地前的 3 个认知（避免踩坑）

1. **安装侧默认放行，是最大的注入面**
   goose 会自动发现 `~/.agents/plugins/<name>/` 的新插件并写入 `config.yaml` 的 `plugins` map（`enabled: true`）——**没有首次使用确认**。Hermes 在这一点上更保守（shell hooks 必须进 `~/.hermes/shell-hooks-allowlist.json`）。所以：**插件目录本身必须列入护栏**。

2. **自动写技能 + 无闸门 = 提示注入的自我放大回路**
   抓取内容 → 写入技能 → 后续会话自动加载并遵从 → 再抓取…… 本手册的两个方案都**刻意把「自动写技能」降级为「写待办队列」**，把最后一段留给人工或子代理。队列清空是安全的，技能被污染不是。

3. **先把「观察」跑通，再打开「行动」**
   每个方案都有 `TODO(verify)` 标记（2 处 API 签名待对照本地 v2 schema 确认）。第 1 步只放文件、看日志有没有产出；确认了再往下走。

---

## 2. 方案 A：opencode（1 个插件文件 + 一段配置）

### 2.1 安装

```powershell
# ① 插件（已产出）
Copy-Item .\opencode\plugins\self-evolve.ts `
  "$env:USERPROFILE\.config\opencode\plugins\self-evolve.ts" -Force

# ② 配置：把 opencode\opencode.jsonc.snippet 的段落合并进
notepad "$env:USERPROFILE\.config\opencode\opencode.jsonc"
```

> 注意：本机 `opencode.jsonc` 现在全文只有 `{"shell":"powershell"}`，直接合并即可。
> `permission` 段的 schema 请以本地 v2 为准（`TODO verify`），先只加 `mcp` 与插件目录。

### 2.2 验证（按顺序，每步都有可观察的产出）

| 步骤 | 命令 / 动作 | 期望看到 |
|---|---|---|
| 1 | 重启 opencode，正常干 20 次以上工具调用的活 | `C:\Users\Admin\.config\opencode\self-improve\` 目录出现 |
| 2 | `ls "$env:USERPROFILE\.config\opencode\self-improve"` | `distill_queue.md`（待判定队列）与 `skill_outcomes.json`（reward） |
| 3 | 用一次任意 skill | `skill_outcomes.json` 里出现该技能的 `use` 计数 |
| 4 | `ls "$env:USERPROFILE\.agents\skills"` | 共享技能根可见（opencode 与 goose 共用） |

### 2.3 它落到哪个状态目录

```
~/.config/opencode/self-improve/
├── skill_outcomes.json   # ⑤ reward：{"<skill>":{"use":n,"fail":n,"last":ISO}}
├── distill_queue.md      # ① 待判定队列（不自动写技能）
├── MEMORY.md             # ④ 记忆（压缩时注入前 2000 字符）
├── curator_report.md     # ③ 最小 curator：use>=2 且 fail>=1 → 建议重写
└── backups/              # 改技能前的带时间戳副本（可回滚）
```

### 2.4 加定时（opencode 无原生调度）

```powershell
# 示例：每天 09:00 跑一次整理（子命令名以本地 CLI 为准）
schtasks /create /tn "opencode-distill" /tr "opencode run --agent distill" /sc daily /st 09:00
```

---

## 3. 方案 B：goose（1 个插件目录，**零配置改动**）

### 3.1 安装

```powershell
# goose 会自动发现 ~/.agents/plugins/<name>/hooks/hooks.json
# 并把新插件写入 config.yaml 的 plugins map（enabled: true）——不需要手工改配置
Copy-Item -Recurse -Force .\goose\.agents\plugins\task-distiller `
  "$env:USERPROFILE\.agents\plugins\task-distiller"
```

### 3.2 验证

| 步骤 | 命令 / 动作 | 期望看到 |
|---|---|---|
| 1 | 起一个 goose 会话，随便说句话后结束 | `.agents\plugins\task-distiller\state\last-event.log` 出现事件 JSON |
| 2 | 同上，看队列 | `state\distill_queue.md` 增长 |
| 3 | 触发一次技能调用 | `state\skill_outcomes.json` 出现 `use` 计数 |
| 4 | `goose plugin --help` / 看 config.yaml 的 `plugins` map | `task-distiller` 已出现且 `enabled: true` |
| 5 | `goose skills` | 能看到共享技能根里的技能**及其 token 数**（opencode 无此能力） |

### 3.3 goose 的独有优势

```powershell
# 原生 cron 驱动 recipe —— 不需要 Windows 任务计划程序
goose schedule add --schedule-id daily-curate --cron "@daily" --recipe-source curate.yaml
```

### 3.4 把护栏从「只记录」切成「真拦截」

`scripts/guard.ps1` 默认输出 `{"decision":"allow"}`（安全起步）。
确认 goose 期望的决策 JSON 结构后（对照 `hooks/mod.rs` 的 `PreToolUseResultPayload`），改成：

```powershell
'{"decision":"deny","reason":"受保护文件：自我指令/自进化脚本须人工修改"}'; exit 0
```

受保护清单已经写好：`AGENTS.md`、`CLAUDE.md`、`SOUL.md`、`\.agents[\\/]plugins[\\/]task-distiller`。

---

## 4. 共用部分：让「一次沉淀，三家复用」成立

```powershell
# 技能落在这里 → opencode 与 goose 都能看到
$env:USERPROFILE\.agents\skills\<skill-name>\SKILL.md
```

写入时必须满足两条硬约束（`self-evolve.ts` 已内置校验，不合格直接抛错并回滚）：
1. frontmatter 必须含 `name` 与 `description`
2. **`name` 必须等于目录名**（opencode 官方 troubleshooting 明确要求）

共享根的本机现状：`C:\Users\Admin\.agents\skills\playwriter` + `.skill-lock.json`。

---

## 5. 回滚

| 对象 | 回滚方式 |
|---|---|
| opencode 插件 | 删 `~/.config/opencode/plugins/self-evolve.ts`，重启 |
| opencode 技能改动 | 从 `~/.config/opencode/self-improve/backups/` 取回带时间戳的副本 |
| goose 插件 | 删 `~/.agents/plugins/task-distiller/`，并在 config.yaml 的 `plugins` map 里清掉该条 |
| 共享技能 | 从 `~/.agents/skills/` 移除该目录（纯 Markdown，无副作用） |
| 全部 | 上述产物全在 `~/.agents/` 与 `~/.config/opencode/` 两处，都不在应用安装目录内，**升级不会冲掉** |

---

## 6. 尚待实测的 4 件事（诚实清单）

1. `self-evolve.ts` 里 `"tool.execute.after"` 拿到 skill 名时的**入参字段名**（`args.name` 还是 `args.skill`）——需对照本地 `skill.ts` schema。
2. `experimental.session.compacting` 的**注入字段名**（`output.context` / `output.parts` / `output.prompt`）。
3. goose `PreToolUse` 的**决策 JSON 结构**（`{"decision":"deny",...}` 的准确形态）。
4. `dependencies`：若插件要引三方 npm 包，需在 `~/.config/opencode/` 放 `package.json`（opencode 启动时 `bun install`）。

这 4 条都能在 10 分钟内用一次实跑问出来——放文件、看日志，不需要读文档。

---

## 7. 风险收益小结

**收益**：把 ②③④⑤ 五件补齐后，opencode 与 goose 在「能力面」上基本追平 Hermes（goose 在 hooks、原生 cron、token 计量上甚至更好）。

**仍缺**：③ 的 provenance 机制（Hermes 用 `bundled`/`hub`/`agent` 三类标记保护既有技能永不被自动改动）——本手册的最小 curator 没有这一层，所以**归档动作必须人工确认**。

**最大风险不是技术，是时点**：goose 正处在平台扩展重构（Discussion #7675 / PR #6160）、治理刚迁 AAIF；opencode 官方已上线 v2。本手册刻意只依赖两家**最稳的接口**——`~/.agents/` 目录约定与 `hooks.json` 的 Open Plugins 规范——把升级破坏面压到最小。
