---
id: goose-report-api-verification
title: 研究报告的 API 级复核方法论与 goose 权威事实快照
tags:
  - 研究方法论
  - 事实核查
  - GitHub API
  - goose
  - AI Agent
  - 文档复核
  - 官方文档抓取
  - 源码审计
  - 供应链安全
created: 2026-10-15
updated: 2026-10-15
version: 1.2
status: stable
source: 本次会话实测（GitHub REST API + 仓库原文 + 官方文档库全量抓取 + 源码全量文件树枚举 + code search 字符串检索 + LF Insights API）
confidence: 已核实
---

## TL;DR

**对话式研究产出的报告，通病是"数字会漂、排名会算错、产物会被笼统归类"。** 复核一份 GitHub 研究报告的正确姿势不是重读文字，而是**把每个数值当成待验证断言，用 API 重采一遍**。本轮对 goose 报告 v1.1 的复核中，14 个仓库的全部硬指标重采一次，就抓出 3 处实质错误（含 1 处排名算错、1 处口径混淆、1 处重大遗漏）。

**第二类盲点更隐蔽：只查 API 与仓库治理文件，会漏掉整个官方文档站。** goose 的功能层能力（内置扩展清单、CLI 命令表、上下文管理参数、GDK、Roaming）**全部只存在于 `documentation/` 目录**。v2.1 对 173 篇文档做全量抓取后，补出 13 项缺失事实。

**第三类盲点最反直觉：官方文档写的是"设计意图"，源码写的是"实际实现"，两者会不一致。** 典型例子：官方 2026-04 博客宣布"桌面端用 Tauri 重写"，路线图状态 🚧 in progress——**但全仓库检索 `tauri` 只命中 2 个文件，且无任何 Tauri 依赖或构建配置**；`ui/desktop/package.json` 实测仍是 **Electron 43.4.0**。若只读文档，会把"计划"写成"既成事实"。**判定这类落差最有效的手段是字符串级全仓库检索（GitHub code search）**，而不是读文档或读 README。

---

## 一、goose 权威事实快照（2026-10-15 实测）

| 指标 | 值 | 备注 |
|---|---|---|
| 仓库 | `aaif-goose/goose` | 原 `block/goose`，2026-04 迁移 |
| Stars / Forks | 55,293 / 6,437 | 对比组内排第 **9** |
| Contributors | 453 | 与 Codex(478)、OpenHands(461) 同级 |
| Open Issues | 480 | issues/stars = **0.87%**，同量级最优 |
| 主语言 | Rust 10,506,629 B（71.59%）+ TS 3,446,615 B（23.49%） | `rust-toolchain.toml` 锁 1.99.0 |
| 许可证 | Apache-2.0（文档 CC-BY-4.0） | — |
| 创建 / 最后推送 | 2024-08-23 / 2026-10-15 | 日更 |
| 稳定版 | **v1.54.0**（2026-10-08） | 2.0 仍为 beta |
| 治理 | Linux 基金会 AAIF（LF Projects, LLC 的 Series 项目） | 组织 2026-03-25 建 |
| Core Maintainers | **7 人**（区间 3–7，追求奇数） | MAINTAINERS.md 实名 |
| 第三方健康分 | **Healthy** | LF Insights 官方徽章 |
| crates 工作区 | **15 个 crate** | 含 `goose-local-inference`、`goose-context-management` |

### v1.54.0 发布产物构成（40 个）

| 类别 | 数量 | 说明 |
|---|---:|---|
| Linux 原生包 | **12** | 4 RPM + 4 DEB + 4 **Flatpak**（各含 x86_64/arm64 × 普通/vulkan） |
| Linux CLI tarball | **12** | `{x86_64,aarch64}-unknown-linux-{gnu,gnu-vulkan,musl}` × `{tar.gz,tar.bz2}` |
| macOS | 9 | 4 桌面 zip + 4 CLI tarball + 1 更新清单 |
| Windows | 4 | 2 桌面 zip + 2 CLI zip（各含 cuda 变体） |
| 源码 / 脚本 | 2 / 1 | — |
| **Linux 合计占比** | **24 / 40 = 60%** | — |

> 关键：**Flatpak ID 为 `io.github.block.Goose`**——迁移至 AAIF 后仍保留 block 命名空间，属迁移遗留。Homebrew cask 名同样仍是 `block-goose`。

### goose 官方文档能力快照（2026-10-15 全量抓取 `documentation/docs/`）

| 维度 | 实测值 | 备注 |
|---|---|---|
| 文档总量 | **173 篇** md/mdx · 247 个文件条目 · 约 **1.33 MB** | 密度 ≈ 每千星 3.1 篇 |
| 分区 | `mcp/` 74 · `guides/` 57 · `tutorials/` 18 · `experimental/` 8 · `gdk/` 5 · `troubleshooting/` 4 · `getting-started/` 3 · `goose-architecture/` 3 · `quickstart.md` 1 | 8 个顶层分区 + 1 个根文件 |
| 官方架构 | **三组件**（Interface / Agent / Extensions）+ **六步交互循环** | `goose-architecture.md` |
| Context Revision 机制 | ① 小模型摘要 ② 全量而非语义检索 ③ 算法删除 ④ 操作级优化（find-and-replace / ripgrep / 输出摘要） | 官方明确列出，比"compaction"精确 |
| 错误处理 | 错误**作为 tool response 送回模型**，不中断流程 | 无效 JSON、缺失工具等 |
| 内置扩展 | **14 个** = 5 基础（Developer / Computer Controller / Memory / Tutorial / Auto Visualiser）+ 9 平台（Analyze / Extension Manager / Skills / Summon / Apps / Chat Recall / Code Mode / Todo / Top of Mind） | 前 5 个平台扩展默认启用；内置扩展本身也是可复用的独立 MCP server |
| MCP 扩展目录 | **73 个**（精确化 README 的"70+"） | `mcp/` 74 篇含 1 个模板 |
| CLI 子命令 | 20+ 个，分 6 组：核心维护 / 会话管理 / 任务执行 / 扩展技能本地模型 / 自动化协议 / 终端集成 | **无 `task` 子命令**——社区教程中的 `goose task "..."` 是伪造用法 |
| 斜杠命令 | **15 个**，含 `/mode`、`/compact`、`/skills`、`/t` | `/summarize` 已弃用 |
| 自动压缩触发 | `min(GOOSE_AUTO_COMPACT_THRESHOLD × 上下文窗口, GOOSE_AUTO_COMPACT_TOKEN_LIMIT)` = `min(80%, 225,000)`，先到者为准 | 225,000 是为 OpenAI 长上下文定价档留余量 |
| 上下文超限策略 | 4 种：Summarize / Truncate / Clear / Prompt | Desktop 只用 summarize；CLI 交互默认 prompt、headless 默认 summarize |
| Max Turns 默认 | **1000**（`GOOSE_MAX_TURNS`） | 官方建议：5–10 探索 / 25–50 中等 / 100+ 复杂自动化 |
| 上下文限制解析优先级 | 5 级：全局 env → 显式配置 → provider 运行时发现 → 规范元数据 → 默认 **128,000** | — |
| GDK | SDK（Rust / Python / Kotlin **进程内库**）+ ACP（stdio / HTTP / WebSocket） | goose 是可被嵌入的 agent 运行时，不只是终端产品 |
| Roaming Agents | iroh(QUIC) 点对点 ACP 传输；公钥互认（类比 WireGuard）；**实验性且不含在发布二进制中**，需 `cargo build --features roaming` | 可编译为 wasm，浏览器标签页即 roam peer |
| 实验性功能 | Ollama Tool Shim（为无原生 tool calling 的模型提供工具调用）/ Remote Access / VS Code 扩展 | Tool Shim 默认后端 `ollama` + `mistral-nemo` |

> **官方文档滞后于实际产物**：Linux 桌面安装页只写 DEB（`sudo dpkg -i`），但实际每版同时发布 RPM + DEB + Flatpak。**以 assets 为准，不以文档为准**。

### goose 源码级事实快照（2026-10-15 全量文件树枚举 `main`）

| 维度 | 实测值 | 备注 |
|---|---|---|
| 全量文件树 | **3,038 个文件 / 52 个顶层条目** | Git Trees API `?recursive=1`，`truncated: false` |
| 顶层目录体量 | `crates/` 806 · `ui/` 645 · `documentation/` 173 · `bin/` 39 · `.github/workflows/` **43** · `scripts/` 30 · `services/` 29 · `buzz/` 11 · `examples/` 11 · `evals/` 10 · `oidc-proxy/` 8 · `vendor/v8/` 2 | — |
| Rust workspace 版本 | **1.55.0**（工作区） | 最新发布仍是 **v1.54.0** → 存在未发布的 1.55.0 |
| MSRV / 工具链 | `rust-version = "1.94.1"` / `rust-toolchain.toml` channel **1.99.0** | **MSRV ≠ 实际构建工具链**，别混用 |
| 版本双轨制 | 核心 crate 走 workspace `1.55.0`；GDK 系列（`goose-providers` 等 7 个）走 **`0.1.0-alpha.12`** | 由 `release-plz.toml` 的 `version_group = "gdk"` 控制 |
| 核心 crate 模块地图 | `crates/goose/src/` **374 个源文件** | `agents/` 97 · `providers/` 66 · `acp/` 48 |
| 提供方实现 | `providers/` **66 个文件、30+ 家**（直连 + ACP 两类），**7 种 wire format** | README 的 "15+ providers" 是下限 |
| **桌面端** | **Electron 43.4.0** + Electron Forge 7.11.2（`maker-deb`/`rpm`/`flatpak`/`squirrel`/`zip`）+ React 19.2.8 + Vite 8.2.1 | **不是 Tauri**（见下方落差表） |
| npm 分发渠道 | `@aaif/goose-acp`（用户实际安装）+ 5 个平台包 `goose-binary-{darwin,linux,win32}-*` | 官方文档未收录 |
| 体积预算 | `lean` profile：macOS **17,825,792 B** / 其他 **23,068,672 B** | `Justfile` 的 `check-lean-size` 在 CI 里卡 |
| Actions 供应链 | 43 个 workflow **全部钉完整 commit SHA**；OpenSSF Scorecard 每周四 12:19 UTC 运行并 `publish_results: true` | — |
| 自更新验签 | `update = ["dep:sigstore-verify", "dep:snap"]` | `goose update` 走 sigstore 签名校验 |
| CI 免长期密钥 | `oidc-proxy/`（Cloudflare Worker）用 GitHub OIDC token 换上游访问；限速 **2 req/s**、每 token ≤ **200 次**、token ≤ **20 分钟** | — |
| Terminal-Bench 自报（89 任务，sonnet-4-6） | goose+code-mode **57.3%** / goose(developer,todo) **50.6%** / opencode 52.8% / pi 47.2% | **仓库自报内部评测，非第三方榜单** |

### 源码 vs 文档的 8 处落差（2026-10-15）

| # | 文档/README 口径 | 源码口径 | 性质 |
|---|---|---|---|
| 1 | "2.0 beta 起桌面端改用 **Tauri** 重写" | 全仓库仅 2 处提 Tauri、**无任何 Tauri 代码**；实测 **Electron 43.4.0** | **把计划当既成事实** |
| 2 | "works with **15+ providers**" | `providers/` 66 文件、**30+ 家** | 概数下限 |
| 3 | "**70+** 官方扩展（MCP）" | 文档目录 73 个，但 `AGENTS.md` 声明**该目录正在退役**，改用官方 MCP Registry 与 `server.json`（Discussion #10830） | 战略变化 |
| 4 | "2.0 beta：**新 TUI**" | `ui/text/README.md`：该 ACP TUI **已弃用、源码移除**，npm `@aaif/goose` 标记 deprecated | 实验终止 |
| 5 | "第三方平台 **Buzz** 以原生 ACP harness 集成 goose" | `buzz/` 是**仓库自带的 Nostr issue 同步自动化**（目标 `buzz.gdk.so`），不是第三方集成案例 | 误读 |
| 6 | 安全体系"**三件套**" | `security/` 实为 **7 个模块**，含未见于文档的 **`egress_inspector.rs`**；另有 `permission/permission_judge.rs` | 不完整 |
| 7 | 分发渠道（未提 npm） | `ui/goose-binary/` 5 个平台包 + `@aaif/goose-acp` | 遗漏 |
| 8 | `.goosehints` 仍描述 `goose-server`（goosed）与 `goose-bench` crate | 15 个 crate 中**二者均不存在**（已被 ACP 架构取代） | **仓库内文档债** |

> 另有一项非错误但值得记录的发现：仓库根有 `MERGE_FIXES.md`（针对 `unroll-agent-loop` 分支的内部合并修复笔记，自称"合并前应删除"），意外披露了状态机重构进度与测试现状（`cargo test -p goose` 仅剩 4 个 jsonwebtoken 库测试 + 6 个依赖网络的 provider 测试失败）。

---

## 二、竞品实时硬数据（2026-10-15）

| 排名 | 产品 | 仓库 | Stars | 贡献者 | Open Issues | 许可证 |
|---:|---|---|---:|---:|---:|---|
| 1 | opencode | `anomalyco/opencode` | 213,573 | 454 | 4,265 | MIT |
| 2 | Dify | `langgenius/dify` | 158,511 | 456 | 1,131 | NOASSERTION |
| 3 | Claude Code | `anthropics/claude-code` | 150,923 | 57 | 15,014 | **无（专有）** |
| 4 | Codex | `openai/codex` | 129,272 | 478 | 22,620 | Apache-2.0 |
| 5 | Pi Agent | `earendil-works/pi` | 115,237 | 291 | 342 | MIT |
| 6 | Gemini CLI | `google-gemini/gemini-cli` | 107,372 | 443 | 745 | Apache-2.0 |
| 7 | OpenHands | `OpenHands/OpenHands` | 90,928 | 461 | 996 | MIT |
| 8 | Cline | `cline/cline` | 70,339 | 340 | 1,664 | Apache-2.0 |
| **9** | **goose** | `aaif-goose/goose` | **55,293** | **453** | **480** | **Apache-2.0** |
| 10 | Aider | `Aider-AI/aider` | 49,554 | 172 | 1,920 | Apache-2.0（**2026-05-22 停更**） |
| 11 | Continue | `continuedev/continue` | 36,226 | 393 | 851 | Apache-2.0 |
| 12 | OpenWork | `different-ai/openwork` | 24,109 | 71 | 629 | NOASSERTION |
| 13 | Octop | `TencentCloud/Octop` | 9,362 | 62 | 825 | MIT |

### 两个被低估的派生指标

- **issues ÷ stars**（越低越好）：goose **0.87%** / Gemini CLI 0.69% / opencode 2.0% / Claude Code 9.9% / Codex 17.5%。
- **月均新增 stars**（stars ÷ 存续月数）：opencode ≈11,865 / Pi ≈8,230 / Octop ≈3,121 / OpenWork ≈2,679 / **goose ≈2,127**。

> 结论：goose「开源最早」未转化为「声量最大」，月均增速仅为 Pi 的 1/3.9。

---

## 三、可复用操作

### 3.1 一份 GitHub 研究报告的复核清单

```bash
export TOKEN=<your_github_pat>   # 需 repo 读权限；匿名限流 60 次/小时

R=aaif-goose/goose

# ① 硬指标：stars / forks / issues / license / language / 创建 / 推送
curl -s -H "Authorization: Bearer $TOKEN" https://api.github.com/repos/$R

# ② 贡献者数：读 Link header 的最后一页（比 /contributors 全量拉取省额度）
curl -sI -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/$R/contributors?per_page=1" | grep -i '^link:'

# ③ 语言字节数（用于精确占比，而非 GitHub 首页的模糊百分比）
curl -s -H "Authorization: Bearer $TOKEN" https://api.github.com/repos/$R/languages

# ④ 单版发布产物逐条清单（复核"N 个产物"类断言的关键）
curl -s -H "Authorization: Bearer $TOKEN" \
  https://api.github.com/repos/$R/releases/tags/v1.54.0 \
  | python -c "import sys,json;[print(a['name']) for a in json.load(sys.stdin)['assets']]"

# ⑤ 治理文件原文（不要引用二手转述）
for f in GOVERNANCE.md MAINTAINERS.md README.md rust-toolchain.toml; do
  curl -s -H "Authorization: Bearer $TOKEN" \
    "https://raw.githubusercontent.com/$R/main/$f"
done

# ⑥ 文件存在性批量校验（用于核实"仓库内有 X 文件"类断言）
for f in RISCV_SETUP.md flake.nix CUSTOM_DISTROS.md; do
  echo "$f -> $(curl -s -o /dev/null -w '%{http_code}' \
    -H "Authorization: Bearer $TOKEN" https://api.github.com/repos/$R/contents/$f)"
done

# ⑦ 组织信息（核实"何时迁入某组织"）
curl -s -H "Authorization: Bearer $TOKEN" https://api.github.com/orgs/aaif-goose

# ⑧ 第三方权威健康分（Linux 基金会）
curl -s "https://insights.linuxfoundation.org/api/badge/health-score?project=goose"
```

### 3.2 排名类断言的正确算法

不要手数。**先按指标降序排出完整表，再用行号定位**。本轮 v1.1 的"第 7 位"错误，正是因为报告表格里 goose 实际在第 9 行，而摘要凭印象写了第 7。

```bash
# 用 API 结果直接排序定位
curl -s -H "Authorization: Bearer $TOKEN" https://api.github.com/repos/$R \
  | python -c "import sys,json;d=json.load(sys.stdin);print(d['stargazers_count'])"
# 然后与全部对比对象的值一起排序，看 goose 落在第几行
```

### 3.3 发布物分类清点

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  https://api.github.com/repos/$R/releases/tags/v1.54.0 \
  | python -c "
import sys,json,collections
d=json.load(sys.stdin); c=collections.Counter()
for a in d['assets']:
    n=a['name'].lower()
    for ext,k in (('.rpm','rpm'),('.deb','deb'),('.flatpak','flatpak'),
                  ('.dmg','macos'),('.msi','windows'),('.tar.gz','tarball')):
        if n.endswith(ext): c[k]+=1; break
    else: c['other']+=1
print('total',len(d['assets'])); print(dict(c))
"
```

### 3.4 官方文档库全量抓取（v2.1 新增方法）

**动机**：只查 API 与仓库治理文件，会系统性地漏掉功能层能力。文档站的正文在仓库里，用 Git Trees API 一次拿到全量清单。

```bash
export TOKEN=<your_github_pat>
R=aaif-goose/goose

# ① 全量枚举文档清单（Git Trees API，一次请求拿整棵树）
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/$R/git/trees/main?recursive=1" \
  | python -c "
import sys,json
for t in json.load(sys.stdin)['tree']:
    p=t['path']
    if p.startswith('documentation/docs/') and p.endswith(('.md','.mdx')):
        print(p)
"

# ② 批量下载正文（raw.githubusercontent 直取，不走 API 额度）
#    单篇：https://raw.githubusercontent.com/$R/main/documentation/docs/<path>

# ③ 提取 frontmatter + 一级标题 + 字数，做分区归类
#    统计口径：篇数 / 分区 / 正文总字节 → 文档密度（篇 ÷ 千星）
```

**分区计数方法**：按 `documentation/docs/` 之后的第一级目录名分组，根目录文件单列。

**产出**：173 篇 → 8 个顶层分区 + 1 个根文件；正文约 1.33 MB。据此把 README 的"70+ 扩展"精确到 **73 个**，并发现 14 个内置扩展、20+ CLI 子命令、15 个斜杠命令等此前完全缺失的能力清单。

### 3.5 源码维度复核（v2.2 新增方法）

**动机**：文档是"设计意图"，源码是"实际实现"。要判定某能力"已落地 / 仍在计划中"，唯一硬证据是源码。

```bash
export TOKEN=<your_github_pat>
R=aaif-goose/goose

# ① 全量文件树（一次请求拿整棵树；务必检查 truncated 字段，为 true 时结果不完整）
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/$R/git/trees/main?recursive=1" \
  | python -c "
import sys,json
d=json.load(sys.stdin)
print('truncated=',d.get('truncated'),' files=',len(d['tree']))
print('top-level=',len(set(t['path'].split('/')[0] for t in d['tree'])))
"

# ② 字符串级全仓库检索 —— 判定「计划 vs 既成事实」的关键手段
#    搜 tauri 只命中 2 个文件且无构建配置 ⇒ Tauri 重写未落地
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/search/code?q=tauri+repo:$R" \
  | python -c "import sys,json;d=json.load(sys.stdin);print(d['total_count']);[print(' -',i['path']) for i in d.get('items',[])]"

# ③ 依赖树真相（框架版本只能从 package.json / Cargo.toml 读，README 会滞后）
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://raw.githubusercontent.com/$R/main/ui/desktop/package.json" \
  | python -c "
import sys,json
d=json.load(sys.stdin); dd=d.get('devDependencies',{})
for k in ['electron','@electron-forge/cli','vite']: print(k,'=',dd.get(k))
print('react =',d.get('dependencies',{}).get('react'))
"

# ④ 工作区版本 vs 最新发布（判断是否存在「已 bump 未发布」）
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://raw.githubusercontent.com/$R/main/Cargo.toml" | head -20
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/$R/releases/latest" \
  | python -c "import sys,json;print('latest tag =',json.load(sys.stdin)['tag_name'])"

# ⑤ 发布产物版本间 diff（定位「何时新增了什么」，比读 CHANGELOG 可靠）
for v in v1.51.0 v1.52.0; do
  curl -s -H "Authorization: Bearer $TOKEN" \
    "https://api.github.com/repos/$R/releases/tags/$v" \
    | python -c "import sys,json;print('\n'.join(sorted(a['name'] for a in json.load(sys.stdin)['assets'])))" > /tmp/$v.txt
done
diff /tmp/v1.51.0.txt /tmp/v1.52.0.txt
```

**用 Git Trees 做体量统计的固定口径**（直接可复用）：

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/$R/git/trees/main?recursive=1" \
  | python -c "
import sys,json,collections
t=json.load(sys.stdin)['tree']
c=collections.Counter(x['path'].split('/')[0] for x in t)
for k,v in c.most_common(15): print('%-42s %7d' % (k,v))
print('TOTAL %d files / %d top-level' % (len(t), len(c)))
"
```

**产出**：15 个 crate 的真实职责与版本双轨制、374 个核心源文件模块地图、66 个提供方文件、桌面端 Electron 真相、43 个 workflow 的质量体系、安全与供应链源码口径、Terminal-Bench 自报数据；**并纠正 4 处"把计划当既成事实"的表述**（Tauri / Buzz / providers / `.goosehints`）。

**输出格式注意**：`print('%-42s %7d B' % ...)` 这类**纯 ASCII 格式串**比带中文的模板更稳——中文宽度不定，且容易触发 locale 编码问题。

---

## 四、坑与反直觉

1. **"N 个产物"是最容易错的断言类型。** 总数 ≠ 某平台数。goose 的 40 个产物里 Linux 只占 24 个。凡是看到"每版发布约 N 个 X 相关产物"，必须逐条清点。
2. **排名会因漏看中间项而整体偏移。** 报告表格里明明排在第 9 行，摘要却写"第 7 位"——**摘要与表格不一致是高频错误**，复核时要交叉比对同一数值在全文的所有出现位置。
3. **新格式容易被忽略。** Flatpak / DEB 这类"后来加的"分发渠道，对话式研究时不会主动去找。**只有清点 assets 才会发现**。
4. **`license: null` ≠ 不开源。** Claude Code 源码可见但无 OSI 许可证，准确表述是"源码公开可见但无 OSI 许可证"，不能说"不开源"（v1.1 已修此点）。
5. **`pushed_at` 是判断"停更"的唯一硬证据。** Aider 4.96 万星看着很活跃，但 `pushed_at = 2026-05-22`——星数是历史存量，推送时间才是当前状态。
6. **`created_at` 决定增速分母。** 说"一年内涨到 X"前先查创建日：opencode 创建于 2025-04-30，到 2026-10 是约 18 个月，不是一年。
7. **官方组织建立时间早于迁入公告。** `aaif-goose` 组织 2026-03-25 建，博客 2026-04-07 才宣布迁入——"宣布"与"落地"是两个时间点，别混用。
8. **同名仓库是干扰项。** `synix/pi-mono`（2 星）vs 真身 `earendil-works/pi`（115,237 星，原 `badlogic/pi-mono` 301 重定向）。查仓库前先确认重定向后的 `full_name`。

### 文档产出侧的坑（本轮实测）

9. **HTML 分块写入会导致 head/body 重复闭合。** 分块写长 HTML 时，若某片段的开头/结尾边界落在 `</head><body>` 上，合并后会出现两个。**合并后必须跑标签配对自检**：
   ```python
   # 基于 html.parser 的轻量检查：入栈出栈，最后栈空且无孤立闭合标签即通过
   ```
10. **公开仓库推送前必须清理本地路径。** 附录命令里的 `cat ~/.workbuddy-ai/skills/.../token.txt` 虽不含凭据，但暴露本机目录结构，应泛化为 `export TOKEN=<your_github_pat>`。
11. **同步多会话共用仓库时推单文件而非目录。** `sync.py` 对目录执行 `rmtree + copytree`（镜像覆盖），会静默删除或回退别人的文件。`--src file --dest path/file` 走 `copy2`，零风险。

### 文档站侧的坑（v2.1 实测）

12. **API + 治理文件 ≠ 完整能力图谱。** `repos` / `contributors` / `releases` / `GOVERNANCE.md` 拿到的全是"项目健康度"维度；功能维度（内置扩展、CLI 命令、上下文参数、SDK/协议）**只在文档目录里**。只查前者会把报告写成"只有规模数据、没有能力细节"。
13. **README 的概数要回落到文档目录去精确化。** "70+ extensions" 的真实值是文档目录下的 73 篇扩展文档；"15+ providers" 同理。**概数是下限，不是事实值。**
14. **社区教程会伪造 CLI 用法。** 某评测文章里的 `goose task "..."` 在官方 20+ 子命令中不存在——对应能力由 `session` 与 `run` 提供。**凡引用社区命令，先回官方 CLI 文档核对**。
15. **官方文档会滞后于发布产物。** Linux 桌面安装页只写 DEB，实际同时发 RPM 与 Flatpak。**发布渠道以 release assets 为准**。
16. **文档正文可能有动态渲染组件。** Docusaurus 的 `<RateLimits />`、`<OnboardingProviderSetup />`、各平台安装按钮组件，其最终内容在 Markdown 源中不可见——抓 Markdown 会漏掉这部分，需标注为不确定性。
17. **品牌迁移会在多处留下旧命名空间。** Flatpak ID `io.github.block.Goose`、Homebrew cask `block-goose` 都仍是 `block`。**别只查一处就断言"已完全迁移"**。
18. **HTML 报告加指标带时注意项数与列数的整除关系。** 7 项塞进 6 列网格会剩 5 个空槽（背景色透出，视觉上像坏块）。宽屏用 `repeat(7,minmax(0,1fr))`，中屏回落到 4 列、窄屏 2 列，并注意 `.hero .kpis` 的特异性会盖过媒体查询里的 `.kpis`。（v2.2 增至 8 项时同步把宽屏列数改为 `repeat(8,…)`。）

### 源码侧的坑（v2.2 实测）

19. **"路线图 in progress" ≠ "已落地"。** 官方博客/路线图写的功能，若源码里搜不到实现，就**不能写成已具备**。判定方法：`/search/code?q=<关键字>+repo:<R>` + 检查 `Cargo.toml` / `package.json` 是否有对应依赖。goose 的 Tauri 就是典型案例。
20. **README 的能力概数一律是下限，且可能已过期。** "15+ providers" 实际 30+ 家；"70+ extensions" 实际 73 个且**目录正在退役**。概数要回落到源码/目录去精确化，并顺手核对"是否仍在维护"。
21. **`rust-version` ≠ 实际工具链。** `Cargo.toml` 的 `rust-version` 是 MSRV（声明下限），`rust-toolchain.toml` 的 channel 才是 CI 实际用的版本。goose 是 1.94.1 vs 1.99.0。**两个数都对，但回答的是不同问题。**
22. **同一 workspace 可能有多个版本号。** goose 的核心 crate 走 workspace `1.55.0`，GDK 系列 7 个 crate 走独立的 `0.1.0-alpha.12`（`release-plz.toml` 的 `version_group = "gdk"`）。**看到"版本号"先问是哪个包。**
23. **发布产物 diff 能定位"何时新增了什么"。** 对比相邻 tag 的 asset 名集合即可：goose v1.48–v1.51 均为 37 个，**v1.52.0 起 40 个**（新增 2 个 macOS zip + `mac-update-requirements.json`）。这比读 CHANGELOG 可靠，也解释了"为什么某版本后数量变了"。
24. **仓库内文档本身会滞后于架构。** `.goosehints` 仍描述已被 ACP 架构取代的 `goose-server`（goosed）与 `goose-bench` crate——这两个 crate 在 15 个 crate 里**根本不存在**。**仓库内的 agent 提示文件不是可信来源。**
25. **自研评测数据要标"自报"。** goose 仓库内 `evals/harbor/README.md` 给出 Terminal-Bench 读数（89 任务，goose+code-mode 57.3%），但 harness 由 goose 团队自维护、各任务模型参数不完全等同。**可作"官方给出的对标读数"引用，不可当中立排名。**
26. **无头浏览器整页截图有像素预算上限。** 报错形如 `RGBA image 1920x23456 requires 180142080 bytes, exceeding the 134217728-byte decoded image budget`。解法：用 JS 把无关 section `remove()` 掉逐节渲染。另两个必踩点：① `file://` 被拒（需起本地 http 服务，且**必须用后台任务启动**，`(… &)` 子 shell 会被回收）；② 删掉 sidebar 后主内容被压成窄条——因为 `.shell{grid-template-columns:264px minmax(0,1fr)}` 仍保留首列，需显式 `gridTemplateColumns='1fr'`。

---

## 五、未核实 / 存疑

| 事项 | 状态 |
|---|---|
| goose 2.0 GA 时间 | 未公布，稳定线仍为 1.x；Tauri 迁移亦未落地 |
| Flatpak 是否已正式上架 Flathub 商店 | 产物已发布，未核验商店条目 |
| `goose-cli` 在主流发行版官方源的收录范围 | repology 有收录，范围未逐一核实 |
| ~~Pi 在 Terminal-Bench 的具体排名~~ | **部分解决（v2.2）**：官方第三方榜单仍未出现，但 goose 仓库内有同模型对标数据（89 任务，pi 47.2% vs goose 50.6%），**属仓库自报** |
| ~~goose 桌面的实现框架~~ | **已解决（v2.2）**：源码实测 **Electron 43.4.0 + Forge 7.11.2**，Tauri 未落地 |
| WorkBuddy Linux GUI 成熟度 | 2026-06 来源与 2026-10 官方教程矛盾，需实测 |
| AAIF 成员公司完整名单 | 部分来自百科 / 媒体转述 |
| 订阅 OAuth 用于第三方客户端的合规性 | 判断项，非事实 |
| 部分官方文档由 Docusaurus 组件动态渲染 | `<RateLimits />` 等组件的最终内容在 Markdown 源中不可见 |
| Roaming Agents 的正式可用时间 | 官方标记实验性且不含在发布二进制中，无 GA 计划 |
| `goose serve` 的生产可用性 | 官方要求 `GOOSE_SERVER__SECRET_KEY`，未给多租户指引 |
| MCP 扩展目录退役的具体时间表 | `AGENTS.md` 只声明"正在退役"，未给截止日 |
