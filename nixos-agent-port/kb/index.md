# 知识库索引

领域：**MCP 服务器工程与 NixOS agent 运维**。读者：以后要自己写 MCP 或运维 agent 的人。

## concepts/ — 可复用的设计模式

| 页 | 一句话 | 标签 |
|---|---|---|
| [mcp-envelope-protocol](./concepts/mcp-envelope-protocol.md) | 工具回执应该是一个**统一形状的结构化对象**：必回显实际目标与命令、失败时主动预取诊断、记账字段与模型可见字段分离 | mcp-design, protocol |
| [rolling-upstream-cache](./concepts/rolling-upstream-cache.md) | 对接"名字会滚动"的上游时，缓存要处理六种真实故障：代数计数器、失败冷却、rollover 重检、fallback 不 memoize、名字与计数分离、并发锁 | mcp-design, caching |
| [mcp-token-budget](./concepts/mcp-token-budget.md) | 工具元数据是**固定上下文成本**；把 N 个工具合并成少数参数化工具，或用尺寸护栏塌缩返回值，都是主动设计 | mcp-design, context-budget |
| [scoped-sudo-and-pin](./concepts/scoped-sudo-and-pin.md) | 给 agent 开 root 权限的正确形状：**窄 sudoers 是唯一边界**，pin / 白名单 / 提示词都只是防手滑 | mcp-design, permissions |

## comparisons/ — 并排分析

| 页 | 一句话 | 标签 |
|---|---|---|
| [mcp-nixos-vs-nix-agent](./comparisons/mcp-nixos-vs-nix-agent.md) | NixOS 生态两个 MCP 的完整对照：一个是只读知识层（853★，2 工具，不需装 Nix），一个是执行层（16★，7 工具，真改系统 + 写 sudoers） | nixos, project-profile |

## 三层职责

| 层 | 目录 | 谁写 | 可变吗 |
|---|---|---|---|
| Layer 1 原始素材 | （本 port 不含；上游是 `recon/` 与两份研究报告） | 人 | ❌ 不可变 |
| Layer 2 Wiki | `concepts/` `comparisons/` | agent | ✅ 持续更新 |
| Layer 3 Schema | `SCHEMA.md` | 人定，agent 遵守 | 谨慎 |

改动记录见 [`log.md`](./log.md)（追加式）。

## 未核实 / 存疑

| 事项 | 状态 |
|---|---|
| `nix-agent` 的 raw→returned 字节实测（13,500 → 394 等） | `C` 级：作者 2026-07-07 在真实 NixOS 笔记本自采（Nix 2.34），未独立复现 |
| `mcp-nixos` 的 "约 1,030 token" | `C` 级：README 自述，未用 tokenizer 核验 |
| 两个 MCP 的端到端实测 | **未做**：全部结论来自元数据 + 源码直读 + 官方文档 |
| `mcp-nixos` 11 个数据源的当前可用性 | **未做**：端点常量已直读，但未逐个 HTTP 探测 |
| `nix-agent` 的 `flake.nix` 能否实际构建 | **未验证**：未跑 `nix build` |
| `nix-agent` 的 sudoers 生成结果 | **未在真机验证**：源码已直读、CI 断言存在，但本机非 NixOS 无法 evaluate |

## 上游来源

| 项目 | 元数据（抓取于 2026-10-12） |
|---|---|
| `utensils/mcp-nixos` | 853★ / 46 fork / MIT / Python / v3.1.0 / 创建 2025-03-20 / 推送 2026-09-05 / 已进 nixpkgs |
| `JEFF7712/nix-agent` | 16★ / 2 fork / MIT / Python / v0.12.0 / 创建 2026-03-19 / 推送 2026-10-12 / 自述 experimental |
