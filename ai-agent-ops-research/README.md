# AI Agent 管理 Linux / NixOS 运维 · 多轮调研汇总

> **规模**：10 轮调研 · 5 份正式报告（md + html）· 10 份知识库文档 · 2 个可安装技能包 · **979 条社区贴文取证**
> **时间**：2026-10-12 ~ 2026-10-13 ｜ **方法**：API/HTTP 实测 + 源码阅读 + 社区原话取证
> **证据分级**：`已核实`（抓到原文/元数据）· `社区实证`（多源一致）· `推断`（本人归纳）

---

## 1. 轮次与产物

| # | 日期 | 主题 | 产物 |
|---|---|---|---|
| A | 10-12 | 用 AI Agent 管 Linux 运维（全发行版） | [`reports/研究报告_AI_Agent_Linux运维_全发行版.md`](./reports/) + html |
| B | 10-12 | 通用 Agent 工作台六项能力选型 | [`reports/研究报告_通用Agent工作台选型_六项能力.md`](./reports/) + html |
| C | 10-12 | NixOS MCP 双项目解剖（nix-agent vs mcp-nixos） | [`reports/研究报告_NixOS_MCP双项目构建解剖_nix-agent_mcp-nixos.md`](./reports/) + html |
| 4 | 10-12 | 包管理器 MCP 选型（apt/dnf/zypper/pacman/nix） | [`reports/研究报告_包管理器MCP选型_五发行版.md`](./reports/) + html |
| 5 | 10-12 | GitHub 官方 MCP Server 核查 | `kb/github-mcp-server-official.md` |
| 6 | 10-12 | nixi 项目剖析（能否被通用 agent 平替） | `kb/nixi-nixos-agent-vs-general-agents.md` |
| 7 | 10-12 | NixOS × LLM 工具四层调研 | `kb/nixos-llm-tooling-layers.md` |
| 8 | 10-12 | nixi 规范 → agent 技能包移植 | [`../nixi-port/`](../nixi-port/) + `kb/nixi-to-agent-skill-port.md` |
| 9 | 10-13 | **社区如何用 AI 管理 NixOS（979 条贴文）** | [`reports/研究报告_社区用AI管理NixOS经验_全网调研.md`](./reports/) + `kb/nixos-ai-usage-community-survey.md` |
| 10 | 10-13 | 总结整理 + GitHub 同步 | 本 README |

技能包 [`../nixos-agent-port/`](../nixos-agent-port/)（26 文件）为第 C 轮配套产物。

## 2. 从哪读起

| 你想知道 | 读这份 |
|---|---|
| **只看一份** | `reports/研究报告_AI_Agent_Linux运维_全发行版.html` — 主报告（浏览器打开，带导航） |
| 社区真实经验与态度 | `reports/研究报告_社区用AI管理NixOS经验_全网调研.md` |
| 给 agent 选 MCP 的决策 | `kb/package-manager-mcp-apt-dnf-zypper-pacman.md` + `kb/github-mcp-server-official.md` |
| 让 AI 安全碰 NixOS | `kb/nixos-llm-tooling-layers.md` + [`../nixi-port/`](../nixi-port/) |
| 全部 KB 入口 | [`kb/README.md`](./kb/README.md) |

## 3. 目录结构

```
ai-agent-ops-research/
├── README.md            ← 本文件（总结）
├── reports/             ← 5 份正式报告（9 文件，md + html）
│   └── early-drafts/    ← 4 份早期分主题草稿（证据留存）
├── kb/                  ← 10 份知识库文档（含 README 索引）
├── tools/               ← 采集/构建脚本 + 运行日志 + 线程摘录
├── data/                ← 原始抓取数据（13 个 JSON，4.4 MB）
└── recon/               ← 早期轮次的采集脚本与源码快照（含渲染校验截图）
```

## 4. 跨轮次收敛的五条结论

1. **能用官方 MCP 就不自建**——GitHub 官方 MCP Server 33,534★ / 24 toolsets / remote endpoint 全用户可用（含免费档），旧 TS 参考实现已归档；自建只在「官方没有 + 需要定制强制策略」时才值得。
2. **「只出 diff → 人工确认 → 回滚」是三侧独立收敛的同一答案**——用户设想（Discourse 72275）、`mcp-nixos-ops`（ZFS 预检门 + dry-run first）、`clawnix`（evolve 自动回滚 overlay）给出同一闭环。
3. **回滚有边界**——generation 只回滚**配置**，不回滚数据库与分布式状态（`cafkafk`：*"a bit of a lie we tell to kids"*）；真实安全网是 ZFS/Btrfs 快照，让 agent 动手前先拍。
4. **强制力必须落在工具层，skill 只是判断规则**——nixi 有 6 项安全保证是 Go 代码强制的（确认门 / MonitoredExecutor 硬拒 / 凭据排除 / 输出脱敏…）；移植成 skill 后必须宿主侧补齐（`ALLOW_PATTERNS` / `--read-only` / scoped sudo）。
5. **事实源 > 模型能力**——最大痛点不是模型笨而是没事实源（`mcp-nixos` 853★ 的诞生动机：*"keeps AI from hallucinating packages and options"*）；教 `nix-index`、给本地 nixpkgs checkout + 手册副本。反例存疑：`cafkafk` 实测「搜索工具让幻觉更多」。

## 5. 复现

```bash
# 重跑社区调研采集（Discourse + HN + GitHub 三源）
python tools/pass1_api.py
# 回取指定 Discourse 主题全文
python tools/fetch_topics.py 78964 80179 72275
# 由 md 重新生成 html 报告
python tools/build_html.py
```

原始证据在 `data/`：`raw_discourse.json`（1,600 帖）/ `raw_hn.json`（1,148 条）/ `raw_github.json`（553 条）/ `topics_full.json`（60 主题全文 636 帖）。

## 6. 已知缺口

| 缺口 | 状态 |
|---|---|
| Reddit / X / Discord 一手内容 | **零采集**——本机出口 IP 被 403 / anomaly / captcha 标记；补采需换 IP 或 Reddit API 凭据 |
| `mcp-nixos-ops` / `nixo` / `nixos-ai-skill` | README 自称 MIT 但仓库无 LICENSE 文件，商用前需作者确认 |
| 979 条贴文的社群代表性 | 仅覆盖三个可编程源，Reddit 缺失会影响模式分布权重 |

---
*本目录由 github-sync 技能自动同步（幂等，无变更不提交）。*
