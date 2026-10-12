# Wiki Schema

## Domain

**MCP 服务器工程与 NixOS agent 运维** —— 具体覆盖两块：

1. **可复用的 MCP 设计模式**：从一个会漂移的上游取数怎么缓存、工具回执协议怎么设计、
   上下文预算怎么当一等约束、权限边界怎么划。
2. **NixOS agent 运维的事实**：两个真实 MCP（`nix-agent` / `mcp-nixos`）的能力边界与用法。

这个 wiki 的**读者是"以后要自己写 MCP 或运维 agent 的人"**，不是"今天要修一台机器的人"
（后者去看 `skills/`）。

## Conventions

- 文件名：小写 + 连字符，无空格（如 `mcp-envelope-protocol.md`）
- 每页开头一行 **TL;DR**（`> ` 引用块），然后分节
- **表格优先于散文**
- 每个事实标 **证据等级**：
  - `A` = 源码或官方文档直读已核实
  - `B` = 平台 API（GitHub）元数据实测
  - `C` = 仓库自述，未独立复核
  - `D` = 推断
- **数字必须带抓取日期**，否则半年后全部过期
- **不写"未核实"当结论** —— 要么标等级，要么进 `未核实` 节

## Tag taxonomy

| 标签 | 含义 |
|---|---|
| `mcp-design` | MCP 服务器的通用设计模式 |
| `caching` | 缓存 / 上游漂移处理 |
| `context-budget` | 上下文 / token 预算 |
| `permissions` | 权限模型、sudo、沙箱 |
| `protocol` | 回执协议、错误语义 |
| `nixos` | NixOS 特有事实 |
| `project-profile` | 单个项目的档案 |

## 目录结构

```
kb/
├── SCHEMA.md               # 本文件（Layer 3）
├── index.md                # 分节目录 + 一句话摘要
├── log.md                  # 追加式操作日志
├── concepts/               # Layer 2：概念页
└── comparisons/            # Layer 2：并排分析
```

## 写页规则

- **概念页写"模式"，不写"某项目怎么做"** —— 项目细节进 `comparisons/` 或档案页
- 概念页必须能脱离原项目读懂：先讲问题，再讲模式，最后举原项目当例子
- 跨页引用用相对路径，**按引用者所在目录算**：
  - `kb/` 根下的页 → `./concepts/xxx.md`、`./comparisons/xxx.md`
  - `concepts/` 下的页 → `./同目录页.md`、`../comparisons/xxx.md`
  - `comparisons/` 下的页 → `../concepts/xxx.md`

## 更新规则

- 同一主题**复写同一文件**，不建 `-v2`
- 每次实质修改在 `log.md` 追加一行
- 抓取日期变了要更新页内的"抓取于"标注
