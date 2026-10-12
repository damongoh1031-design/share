# 操作日志（追加式）

格式：`日期 | 动作 | 对象 | 备注`

---

2026-10-12 | 建立 | `SCHEMA.md` `index.md` | 定域（MCP 服务器工程 + NixOS agent 运维）、定证据等级 A/B/C/D、定标签表

2026-10-12 | 新建 | `concepts/mcp-envelope-protocol.md` | 从 `nix-agent` 的 `runner.py` / 各 tool 回执提炼 5 条原则：回显 `resolved_target`、回显 `command`、失败时预取诊断、`summary` 分档、状态机 9 值

2026-10-12 | 新建 | `concepts/rolling-upstream-cache.md` | 从 `mcp_nixos/caches.py` 提炼六件套：代数计数器（`_ALIAS_RE`）、`_DISCOVERY_RETRY_COOLDOWN=30.0`、`_ROLLOVER_RECHECK=300.0`、fallback 不 memoize、名字与计数分离、并发锁

2026-10-12 | 新建 | `concepts/mcp-token-budget.md` | 从 `mcp-nixos` v3 的 17→2 工具重构与 `nix-agent` 的 2048 值护栏提炼；含反例（合并会推高参数复杂度）

2026-10-12 | 新建 | `concepts/scoped-sudo-and-pin.md` | 从 `privilege.py` / `target.py` / `nix/module.nix` / `docs/privileged-automation.md` 提炼 3.5 层权限模型；逐字保留上游 "anti-footgun, not a security boundary" 的表述

2026-10-12 | 新建 | `comparisons/mcp-nixos-vs-nix-agent.md` | 两个 MCP 的完整对照：元数据、工具面（2 vs 7）、配对工作流 9 步、FastMCP 版本互斥的三个解、两种设计签名

2026-10-12 | 核实 | `mcp-nixos` 工具签名 | 直读 `mcp_nixos/server.py`：确认**只有 2 个** `@mcp.tool()`（`nix` / `nix_versions`），`nix` 有 8 个参数、`source` 11 个取值；修正了早期"11 个数据源 = 11 个工具"的潜在误读

2026-10-12 | 核实 | FastMCP 版本区间 | 直读两个 `pyproject.toml`：`mcp-nixos` 要 `>=4.0.0`、`nix-agent` 要 `>=2.14,<4`，**区间不相交**，确认无法共存于一个 venv

---

## 待办（下次抓取时）

- [ ] 端点可用性：逐个 HTTP 探测 `config.py` 里的 11 个上游
- [ ] `nix-agent` 端到端：在真 NixOS 上跑 `build` → `diff` → `check(dry-activate)` → `switch` → `generations(rollback)`
- [ ] token 实测：用真 tokenizer 核验"约 1,030 token"与"13,500 → 394"两个自述数字
- [ ] 两者同时注册进 Hermes 的实际行为（工具名冲突？审批提示？）
- [ ] 更新页内所有"抓取于"日期
