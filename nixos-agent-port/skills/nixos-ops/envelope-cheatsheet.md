# 回执速查：哪些字段已经替你预取了

`nix-agent` 的每个工具返回**统一形状的 JSON envelope**。读它，**不要自己重跑命令**。

## envelope 的标准形状

```jsonc
{
  "status": "ok",                  // 见下表
  "resolved_target": "...",        // 实际解析到的目标 —— 绝不隐含
  "command": ["sudo","-n","/nix/store/.../nixos-rebuild","switch","--flake","..."],
  "output": "...",                 // 默认已裁剪
  "first_error": "...",            // 仅 failed：第一行像 error 的 stderr
  "error_detail": {...},           // 仅 failed：{message, file, line, column, trace}
  "failed_derivation": {...},      // 仅构建失败：{drv, log_tail} —— 已跑过 nix log
  "summary": {...},                // 仅 switch 成功
  "rollback_generation": "...",    // 仅 switch
  "current_generation": "...",     // 仅 switch / generations
  "privilege": {...},              // 仅 sudo 失败
  "generations": [...],            // 仅 generations(action="list")
  "findings": [...],               // 仅 check("lint")
  "truncated": true,               // 仅值超过尺寸护栏时
  // raw_bytes / returned_bytes 不在 MCP 回执里（记账字段被剥离）
}
```

**两个必回显的字段**：`resolved_target` 和 `command`。上游设计原则是
"**nothing is silently implicit**" —— 如果这两个字段看起来不对，**先停**，别继续。

## status 全表

| status | 什么时候出现 | 命令跑了吗 |
|---|---|---|
| `ok` | 成功 | ✅ |
| `degraded` | **激活成功但有 systemd unit 新失败** | ✅ |
| `failed` | 命令非零退出 | ✅ |
| `no_target` | 找不到 flake / 不是目录 / 缺 flake.nix | ❌ |
| `unknown_host` | flake 里的主机名对不上（回执带 `hosts` 全列表） | ❌ |
| `unknown_generation` | generation id 不存在 | ❌ |
| `target_locked` | 设了 pin 但指到了别的目录 | ❌ |
| `remote_ref_rejected` | 特权工具拒收远程 flake ref | ❌ |
| `preflight_failed` | `switch(validate=True)` 的 dry-build 没过 | ❌（从未激活） |
| `not_an_option` | 该 attr 不是 option（是普通配置值） | ❌ |
| `not_applicable` | 如独立式 HM 没有 dry-activate | ❌ |
| `tool_missing` | `check("lint")` 找不到 statix/deadnix | ❌ |
| `invalid_level` / `invalid_action` | 参数非法 | ❌ |

**后 9 个都是早退：没有命令被执行过。** 不要"重试"，要先修输入。

## `switch()` 的 `summary` 里有什么

成功激活后**不要**再跑 `systemctl --failed` 或第二次 `diff()` —— 都在这里：

```jsonc
"summary": {
  "derivations_built": 12,
  "units": {
    "stopped":   ["old.service"],
    "started":   ["new.service"],
    "restarted": ["nginx.service"],
    "reloaded":  ["dbus.service"],
    "new":       ["foo.timer"]
  },
  "changed": true,
  "packages": {"added": [...], "removed": [...], "changed": [...]},   // vs rollback generation
  "health": {
    "newly_failed": [{"unit": "...", "log_tail": "..."}],  // 只前 5 个带 journal tail
    "resolved":     ["..."],   // 之前失败现在好了
    "still_failed": ["..."]    // 一直失败
  }
}
```

- `derivations_built > 0` 或 `units` 非空 → `changed: true`
- **`newly_failed` 非空 → `status` 是 `degraded`，不是 `ok`**，并且回执带一条 `hint` 建议回滚
- `summary.health` 缺失时会有 `health_note` 说明为什么（如 `systemctl` 快照不可用）

## 三道截断（知道它们存在，就不会误判"输出丢了"）

| 机制 | 触发 | 表现 |
|---|---|---|
| 输出截断 | 输出 > **64 KB** | 保留**头一半 + 尾一半**，中间 `... [nix-agent: N bytes truncated] ...` |
| 成功日志裁尾 | `switch` 成功且未传 `full_log=True` | 只留最后 **2 KB** + `log_truncated: true` |
| 值尺寸护栏 | 单个值 > **2 KB** JSON | dict → `attr_names` 列表；list → `length`；标量 → 头切片；都带 `truncated: true` + `hint` |

**`truncated: true` 的正确反应**：eval 一个**子 attr** 拿你真正需要的那部分。
**不是**重试要全量输出。

## 失败时读三个字段然后停

```
first_error              → 可操作的那一行
error_detail             → {message, file, line, column, trace} = 直接的编辑目标
failed_derivation.log_tail → 失败 builder 的日志（已替你跑过 nix log）
```

**别做**：在字段存在时再跑 `nix log`、为了看全量传 `full_log=True`、用 `--verbose` 重跑。

## `full_log=True` 是"刻意的最后手段"

`full_log` 和原始 `output` 字段存在，是为了**罕见情况下裁剪视图确实不够用**。
默认就去用它，等于把这个服务器存在的理由抹掉了。

## 记账字段在哪

`raw_bytes` / `returned_bytes` **不在 MCP 回执里** —— 它们在工具返回给模型之前就被剥掉了。
它们只进本地 usage log（`NIX_AGENT_USAGE_LOG=1`，然后 `nix-agent usage`）。

**别去 MCP 结果里找这两个字段。**
