# MCP 的上下文预算

> **TL;DR** 工具元数据（tool schema）是**每一轮对话都要付的固定成本**。工具越多、描述越长，
> 这个成本越高。两个正交的手段：① **合并工具**（N 个工具 → 少数参数化工具）；
> ② **护栏返回值**（把大输出塌缩成"形状摘要"）。两者都不是"少做点事"，是主动设计。

标签：`mcp-design` `context-budget` · 证据等级：`A`（源码直读）+ `C`（自述数字）

## 问题

一个 MCP 服务器暴露 17 个工具，每个带一段描述和参数 schema。这些元数据**每轮都在上下文里**，
与当前任务是否相关无关。

```
成本 = 工具数 × (名字 + 描述 + 参数 schema)
```

工具越多 → 固定成本越高 → 留给实际内容的窗口越小。而"工具多"通常**不是设计选择，
是设计缺失**：每个新功能加一个工具，是最省事的做法。

## 手段一：合并工具（N → 少数参数化工具）

把"按功能拆"改成"按**维度**拆"：

| 反例（17 个工具） | 正例（2 个工具） |
|---|---|
| `search_packages` / `search_options` / `search_flakes` / `info_package` / `info_option` / `stats_packages` / … | `nix(action, query, source, type, channel, limit, version, system)` + `nix_versions(package, version, limit)` |

**维度化**：`action`（做什么）× `source`（对谁做）× `type`（子类型）覆盖了 17 个工具的组合空间。

> 例（`mcp-nixos`）：README 自述从 17 个工具合并成 2 个，总量"约 1,030 token"（`C` 级，未独立核验）。
> 上游的实现方式是把 11 个数据源 × 8 个 action 压进一个参数矩阵。

### 合并的代价（必须知道）

1. **模型必须学会参数组合** —— 所以要给一张可用性矩阵（哪些组合合法）。
2. **非法组合变多了** —— 所以要**把错误信息做成可直接复制的正确调用**：

   > 上游的做法：`action=browse` + `source=nixos` 被拒时，回执里直接给出
   > `{"action": "search", "query": "nginx", "type": "options"}`；
   > 并且会把用户传的 `query` 回填进示例里。

3. **需要给"意图 → 调用"的样例** —— 上游在 MCP 的 `instructions` 字段（`InitializeResult`）
   里塞了 8 条 `"意图" → {"action": ..., "query": ...}` 的 JSON 形状，并要求
   "**即使你觉得你知道答案也要调用**"（对抗训练数据滞后）。

## 手段二：返回值护栏

工具**返回**的东西同样要管。三种机制：

| 机制 | 触发 | 行为 |
|---|---|---|
| 输出截断 | 输出 > N KB | 保留**头一半 + 尾一半**，中间标 `... N bytes truncated ...` |
| 成功时裁尾 | 长日志 + 成功 | 只留最后 N KB + `log_truncated: true`；全量要显式开开关 |
| 值尺寸护栏 | 单个值 > N KB | **按类型降级**：dict → 键名列表；list → 长度；标量 → 头切片 |

**值护栏按类型降级**是这里最巧的一点 —— 不是粗暴截断字符串，而是保留"形状"：

```python
# 超过 2 KB 时
dict  → {"attr_names": [...], "truncated": true, "hint": "eval a child attr"}
list  → {"length": 1234,      "truncated": true, "hint": "eval a narrower attr or index"}
```

调用方拿到的是**可操作的提示**（"去 eval 子属性"），不是一堆被砍断的字符。

### 关键：`truncated` 的正确反应

**看到 `truncated: true` 应该缩小请求范围，不是重试要全量。** 所以 `hint` 字段必须
把这件事说明白。

## 实测效果（`C` 级，作者自采）

`nix-agent` 的 `docs/usage.md` 记录（2026-07-07，真实 NixOS 笔记本，Nix 2.34）：

| 操作 | 原始字节 | 回执字节 | 倍数 |
|---|---|---|---|
| `eval_config("environment.systemPackages")` | **13,500** | **394** | **34×** |
| `diff`（近乎空 diff） | 338 | 1,431 | 0.24×（变大了） |
| `locate_option("environment.systemPackages")` | 24,066 | 20,396 | 1.18×（几乎没省） |

**后两行是诚实反例，值得单独学：**

- `diff` 在近乎空的时候**回执比原始输出大** —— 因为 envelope 元数据与结构化 breakout
  占主导。**收益随 diff 规模增长，小 diff 时是负收益。**
- `locate_option` 在这个 option 上只省了 18% —— 因为那个 option 定义在 **95 个文件**里，
  每个文件的值都已经接近各自的护栏。作者自己在文档里承认了这一点，并说明这个工具
  进工具集的理由是"**一次调用回答哪个文件**"，不是"封顶一个 firehose"。

**教训**：护栏不是万能的。**报收益时要把反例一起报出来**，否则"平均省 X%"是误导。

## 判据：这个工具值得存在吗

问三个问题：

1. **它封顶了什么？** 没有封顶的只读工具可能不值得占一个工具位（用通用 shell 工具代替）。
2. **它结构化了什么？** 把自由文本变成稳定字段，价值在"可编程消费"。
3. **它预取/预计算了什么？** 把调用方必然会做的下一步提前做掉。

`nix-agent` 的工具注释把这个框架写得很清楚：

> Operational core: structured operational signal + rollback safety, **the work that can't be
> reproduced reliably from ad-hoc shell**.
> Config introspection: kept because **each caps or structures Nix output the host would
> otherwise pay for in raw context**.

## 反面清单

- ❌ 每个功能加一个工具（工具数线性增长，固定成本线性增长）
- ❌ 工具描述写成长文档（描述每轮都付钱）
- ❌ 返回值不设上界
- ❌ 护栏只做字符串截断，丢掉结构
- ❌ `truncated` 没有 `hint`，调用方只能猜
- ❌ 只报平均收益，不报负收益的反例

## 相关

- [mcp-envelope-protocol](./mcp-envelope-protocol.md)
- [mcp-nixos-vs-nix-agent](../comparisons/mcp-nixos-vs-nix-agent.md)
