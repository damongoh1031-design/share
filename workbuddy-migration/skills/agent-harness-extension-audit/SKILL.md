---
name: agent-harness-extension-audit
description: 审计本机已安装的 AI agent 框架（Hermes Agent、DeepSeek Harness/DSH、WorkBuddy、OpenClaw 等）的「扩展面」——MCP 目录、内置/可选技能、插件目录、记忆提供方、搜索后端——先读本地源码与文档建立权威能力图谱，再体检用户实际配置，最后映射到用户目标给出落地方案。当用户问「XX agent 要装什么 MCP / 技能」「怎么提升 XX 的搜索/记忆/知识库能力」「我的 XX 配置有什么问题」时使用。核心价值：**不靠模型记忆猜能力，而是从本机仓库读出精确的条目清单与数量**。
agent_created: true
type: Checklist
---

# 本地 Agent 框架扩展面审计

## 为什么需要这个 skill

模型对任何具体 agent 框架的「有哪些 MCP / 技能 / 插件」都只有模糊记忆，而这类信息**就在用户本机**。猜 = 编造不存在的条目名。本 skill 的顺序是：**先读源码建图谱 → 再体检实际配置 → 最后给方案**。

## 第一步：定位框架根目录

先别猜路径，直接找。常见落点：

| 框架 | 典型根目录 | 关键特征文件 |
|------|-----------|-------------|
| Hermes Agent (Nous Research) | `%LOCALAPPDATA%/hermes/` | `config.yaml`、`SOUL.md`、`hermes-agent/`（git 仓库） |
| DeepSeek Harness (DSH) | `~/.dsh/profiles/<profile>/` | `pnpm-workspace.yaml` |
| WorkBuddy / CodeBuddy | `~/.workbuddy-ai/`、`~/.codebuddy/` | `mcp.json`、`skills/`、`settings.json` |
| OpenClaw / 其他 | `~/.<name>/` | 看 `config.yaml` / `*.json` |

```bash
# 一次列出候选
ls -la "$HOME" | grep -i -E "hermes|dsh|workbuddy|codebuddy|openclaw|\.agents"
ls -la "$LOCALAPPDATA" 2>/dev/null | grep -i -E "hermes|dsh|workbuddy"
```

⚠️ 别用 `find /` 全盘扫——慢且会被沙箱拦。

## 第二步：确认「这就是官方仓库」+ 读能力图谱

```bash
cd <根>/<repo 子目录>
git remote -v          # 确认 owner/repo，别把 fork 当官方
git log --oneline -5   # 记下 commit，报告里要写版本基准
```

### ⭐ 四类目录 = 四层扩展面（几乎每个框架都是这个结构）

```bash
# 1) 官方已审 MCP 目录
ls optional-mcps/ | wc -l          # 条目数
for d in optional-mcps/*/; do
  n=$(basename "$d"); d2=$(grep -m1 -E "^description:" "$d/manifest.yaml" 2>/dev/null | sed 's/description: *//')
  echo "$n | $d2"
done

# 2) 内置技能（已装）+ 可选技能（未装）
ls skills/                          # 按分类分目录
cat skills/.bundled_manifest        # 内置清单
find optional-skills -name SKILL.md | wc -l

# 3) 插件目录（社区 + 官方）
ls plugin-catalog/*.yaml | wc -l

# 4) 内置的 provider 实现（记忆 / 搜索后端常在这里）
ls plugins/memory/ plugins/web/
```

**要抓的量**：每层条目数 + 目标相关分类的逐条名称与描述。这些数字是报告可信度的锚点。

### 读官方文档而不是靠猜

```bash
ls website/docs/user-guide/features/    # 功能文档
ls website/docs/reference/              # 目录/清单类文档（最有价值）
```

优先级最高的几份（Hermes 为例）：
- `features/mcp.md` — MCP 配置、工具过滤、信任模型
- `features/memory.md` + `features/memory-providers.md` — 记忆机制与全部提供方
- `features/web-search.md` — 搜索后端对照表
- `features/document-extraction.md` — 哪些格式能自动转文本
- `reference/optional-skills-catalog.md` — 可选技能全表（含一行描述）

⚠️ **大文件用 `sed -n '/^## 目标分类/,/^## 下一个分类/p'` 精确切片**，别 `cat` 整份。

## 第三步：体检用户的「实际配置」（这一步最容易被跳过）

**源码里有 ≠ 用户装了。** 必须分开查：

```bash
# 1) MCP 是否真的配了（注意：配置模板里的大段 mcp_servers 常是注释）
grep -n "^mcp_servers" -A 20 config.yaml

# 2) 记忆提供方是否激活（provider 键）
sed -n '/^memory:/,/^# ===/p' config.yaml | grep -v "^ *#"

# 3) 搜索后端是否钉住（有没有 web: 段）
sed -n '/^web:/,/^[a-z_]*:$/p' config.yaml

# 4) 有哪些 API key（只列键名，绝不打印值）
grep -o -E "^[A-Z0-9_]+=" .env | sed 's/=$//' | grep -i -E "EXA|TAVILY|FIRECRAWL|BRAVE|SEARXNG|PARALLEL|PERPLEXITY|OPENVIKING|HONCHO|MEM0" | sort -u

# 5) 实际装了多少技能 / 插件
find skills -name SKILL.md | wc -l
ls installs/ plugins/ 2>/dev/null
```

⚠️ **只输出键名，绝不输出值**。`.env` 含密钥，用 `grep -o -E "^[A-Z0-9_]+="` 而不是 `cat`。

**产出「体检表」**：每一层 → 实测状态 → 判断（✓ / ✗ / △）。用户看到「你其实 0 个 MCP、0 个外部记忆」比看到一堆推荐更有行动力。

## 第四步：区分「原生已有」和「需要额外装」

这是避免过度推荐的关键。很多用户以为要装 MCP 的能力，框架其实原生就有：

| 用户诉求 | 先查原生是否已有 | 常见真相 |
|---------|----------------|---------|
| 更好的网页搜索 | `features/web-search.md` 的后端表 | 原生已内置 5–11 个后端 + 无 key 免费轮转，**不需要装 MCP** |
| 读 PDF / Word / Excel | `features/document-extraction.md` | `read_file` 已自动转换，**唯一真缺口是扫描版 PDF**（无文字层会静默转空白） |
| 更长的记忆 | `features/memory.md` 的字符上限 | 内置通常只有 2000–3000 字符，**这一项才是真的必须换外部提供方** |
| 知识库 | 是否已有 wiki / note 类技能 | 常已内置（如 `llm-wiki`），缺的只是**落点路径**（`WIKI_PATH` 未设） |

**结论模板**：「这四个目标里，N 个不需要装 MCP，靠原生 + 可选技能就能解决。」

## 第五步：社区意见（转交 community-signal-research）

不要用 WebSearch 泛搜代替。社区实证走 `community-signal-research` skill：
- Reddit 用 `.rss` 端点拿**正文 + 全部评论全文**（列表 RSS 无互动数，不能做热度排序）
- ⚠️ **Reddit RSS 请求必须串行**，并行会互相挤占配额触发 429
- 优先搜 `r/<框架名>` 子版：`/search.rss?q=<关键词>&restrict_sr=1&sort=top&t=year`

**厂商自撰的「最佳 XX 榜单」要打折**：核查它是否披露利益关系（如 Parallel 写「最佳搜索 MCP」时会自述 we make Parallel）。**并检查它的覆盖范围**——实测有榜单号称「Top 21 MCP」却完全没覆盖搜索/记忆/知识库类别，此时只能引用其性能/安全建议，不能当选型来源。

## 第六步：报告结构（用户偏好密集表格，忌长散文）

```
§0 结论速览（最小可行清单 + 3 条反直觉结论）
§1 现状体检（本机实测，逐层 ✓/✗/△）
§2 扩展层概念澄清（技能/可选技能/插件/MCP/社区 —— 成本与隔离性完全不同）
§3–§6 逐个目标：原生已有 → 可选技能 → 插件 → MCP → 社区实证
§7 社区原声（原话引用 + 必写踩坑与争议）
§8 三档方案 + 可直接粘贴的 config.yaml / .env 片段 + 落地顺序
§9 口径与可信度说明（证据分级 A已核实/B社区/C厂商/D未验证 + 抓取失败清单）
§10 References（每条给完整 URL）
```

## 硬规则

1. **每个数字都要能追溯到命令输出**，不要「大约几十个」。
2. **证据分级**：本机源码 = 已核实；Reddit 用户原话 = 社区实证；厂商自述 = 未独立核实；提及但无反馈 = 未验证。三者在报告里必须视觉可分。
3. **抓取失败必须显式列出**，不要静默省略——读者需要知道覆盖边界。
4. **Discord 无授权就完全不写内容结论**，只能拿服务器规模当代理，并明确标注是代理而非内容分析。
5. **推荐第三方项目时标注「未在官方目录中，安装前自行审阅」**。
6. **落地顺序：先零成本（配置/路径）→ 再技能 → 最后才 MCP**，且 MCP 必须 `tools.include` 收窄。理由：MCP 工具每轮都占上下文，且框架通常对 MCP 结果有更严的溢出阈值。
