---
id: goose-docs-zh-translation-pipeline
title: goose 官方文档中文手册 —— 全量翻译流水线、围栏感知审计与 8 条坑
tags:
  - goose
  - documentation
  - translation
  - pipeline
  - subagent
  - audit
  - markdown
  - docusaurus
created: 2026-10-15
updated: 2026-10-15
version: 1.2
status: stable
source: 本项目实测（2026-10-15，22 章 / 173 页全量翻译 + 审计 + GitHub 同步）
confidence: 已核实
---

# goose 官方文档中文手册 —— 全量翻译流水线

## 一句话结论

goose 官方资料（仓库 `aaif-goose/goose`）**397 个源文件 / 2,793,527 字节**已全量译为简体中文：**33 章 / 397 页面节 / 2,764,724 字节（99%）**，五项审计全绿。覆盖 **文档站正文 173 页 + 博客 112 篇 + Recipe 模板 67 个 + 仓库治理 16 篇 + 文档站工程 29 个文件**，已推送 `damongoh1031-design/share` 的 `goose-docs-zh/`。

---

## 1. 产出清单（2026-10-15 实测）

| 项 | 值 |
|---|---|
| 源语料 | `aaif-goose/goose`，**397 个文件 / 2,793,527 B**，分两批：<br>① `documentation/docs/` 173 个 `.md`/`.mdx`（1,351,256 B）<br>② 其余 224 个文件（1,442,271 B）：博客 112 + Recipe yaml 67 + 仓库根 md 16 + 文档站工程 29 |
| 章节 | **33 章**（第 1–22 章 `groups.json`，第 23–33 章 `groups_extra.json`），覆盖 397/397 文件，无重复无遗漏 |
| 页面节 | 397 个 `## ` 节，每节带 `> 原文：<裸 URL>` 出处行 |
| 译文体积 | 2,764,724 B / 源 2,793,527 B = **99%** |
| 内容量 | 图片 220 · 代码块 1,579 · 表格行 1,351 · 标题 译 2,685 / 源 2,636 |
| 交付文件 | 33 个章节 md + `README.md`（1,936 行总目录）+ `goose-zh-完整版.md`（2,453,287 B 单文件）+ 两个 groups 索引 |
| 审计脚本 | `_verify/audit_zh.py`（**多源版**，围栏感知，五项判据） |
| GitHub | `goose-docs-zh/`（commit 见 git log） |

章节目录（章号 → 页数 / 体积）：

| 章 | 主题 | 页 | 字节 |
|---|---|---|---|
| 01 | 快速开始与安装 | 2 | 26,779 |
| 02 | 模型提供方全览 | 1 | 84,957 |
| 03 | 扩展与工具管理 | 7 | 49,462 |
| 04 | 上下文工程（一）：指令层 | 5 | 36,940 |
| 05 | 上下文工程（二）：Agent 层 | 5 | 59,217 |
| 06 | Recipes 可复用工作流 | 5 | 79,172 |
| 07 | 会话、任务执行 | 5 | 65,130 |
| 08 | 权限、安全与数据 | 6 | 21,971 |
| 09 | 提供方进阶与多模型 | 5 | 49,977 |
| 10 | CLI 命令与配置文件 | 2 | 48,006 |
| 11 | 环境变量与运行控制 | 5 | 48,813 |
| 12 | 交互界面与实用技巧 | 10 | 34,019 |
| 13 | MCP 扩展（一）：核心内置 | 14 | 71,452 |
| 14 | MCP 扩展（二）：浏览器与自动化 | 9 | 56,450 |
| 15 | MCP 扩展（三）：开发与代码 | 11 | 64,225 |
| 16 | MCP 扩展（四）：数据与云服务 | 12 | 73,104 |
| 17 | MCP 扩展（五）：协作与办公 | 14 | 78,901 |
| 18 | MCP 扩展（六）：搜索与信息获取 | 14 | 91,471 |
| 19 | 教程（一）：扩展与集成实战 | 8 | 71,825 |
| 20 | 教程（二）：工作流与可观测性 | 10 | 83,360 |
| 21 | 架构、远程部署与 GDK | 11 | 47,708 |
| 22 | 排错与实验特性 | 12 | 44,697 |
| 23–29 | **博客存档 112 篇**（2024-11 ~ 2026-09） | 112 | 977,567 |
| 30 | Recipe 模板库（一）：顶层 Recipe | 44 | 206,530 |
| 31 | Recipe 模板库（二）：子 Recipe | 23 | 91,495 |
| 32 | 仓库治理文档 | 16 | 118,749 |
| 33 | 文档站工程与站点页面 | 29 | 47,930 |

第 23–29 章博客分批（每章 ≤ 20 篇 / ≤ 180 KB）：23=2024-11~2025-03（20 篇）、24=2025-04~05（18）、25=2025-06~07（10）、26=2025-08（15）、27=2025-09~12（19）、28=2026-01~02（15）、29=2026-03~09（15）。

---

## 2. 流水线（7 步）

| 步 | 做什么 | 关键脚本 / 产物 |
|---|---|---|
| 1 | 抓源语料 | Git Trees API `?recursive=1` 枚举 → 过滤 `documentation/docs/**/*.{md,mdx}` → 逐篇走 `raw.githubusercontent.com` 落盘（不耗 API 额度）。脚本 `_verify/fetch_docs.py` + `dl_docs.py` |
| 2 | 分章 | 按 `documentation/docs/` 后第一级目录归并成 22 章，写 `groups.json`（章号 / 章名 / 文件列表 / 源字节数） |
| 3 | 立契约 | `goose-docs-zh/_写作规范.md` —— 唯一规范，每个译者开工第一步必须完整读 |
| 4 | 并行翻译 | 每章一个子代理，**7 章可同时跑**（429 恢复后实测无冲突） |
| 5 | 审计 | `_verify/audit_zh.py` 五项判据，围栏感知 |
| 6 | 生成总目录 / 完整版 | `_verify/build_readme.py --merge` → `README.md` + `goose-zh-完整版.md` |
| 7 | 同步 + 复核 | github-sync 推目录 → `git ls-tree -r -z` 拿远端 blob SHA，与本地 `git hash-object` 逐一比对 |

### 翻译契约的核心红线（`_写作规范.md`）

| 项 | 规则 |
|---|---|
| 完整性判据 | **译文体积 = 英文源的 90%–130%**（中文 UTF-8 单字 3 字节）。**明令禁止**用「中文应为英文 40%–60%」当判据 |
| 标题映射 | 源 frontmatter `title` → 译文 `## `；源 `##`→`###`、`###`→`####`… 不跳级、不合并、不删节 |
| 不译 | 代码块 / 行内代码 / 命令 / 参数 / 环境变量 / 路径 / URL / JSON·YAML / 产品名·扩展名·模型名 |
| 图片 | `/img/x.png` → `https://block.github.io/goose/img/x.png`（绝对化，一张不删） |
| 站内链 | `](/docs/foo)` → `](https://block.github.io/goose/docs/foo)`，锚点保留 |
| 提示块 | `:::note` 等**保留 `:::` 语法本身**，只译冒号后标题（`:::info Desktop Only` → `:::info 仅桌面版`） |
| MDX | `import` 行整行删；`<Tabs>`/`<TabItem>` 保留标签只译 `label` 自然语言；纯渲染组件整块原样 |
| 围栏 | 开闭成对，**语言标记必须在第 0 列** |
| 文体 | 简体中文技术文档语体，第二人称「你」，中英文之间不加空格，中文用全角标点 |

---

## 3. 审计器设计（`audit_zh.py`）

### 五项判据（每章必须全过）

| # | 判据 | 说明 |
|---|---|---|
| 1 | 页面节数 == 源文件数 | 围栏感知计数 |
| 2 | `> 原文：` 条数 == 源文件数 | 逐页出处 |
| 3 | 无相对资源 | `](/img`、`](/assets`、`](/docs` 残留为 0 |
| 4 | 代码围栏为偶数 | 配对完整 |
| 5 | 体积 ≥ 源 × 0.9 | 完整性 |

### 围栏感知解析（`split_code`）—— 全流程最核心的 20 行

闭围栏必须**同时满足三个条件**，缺一不可：

```
mk[0] == open_ch        # 同种符号（``` 只能被 ``` 关，不能跨 ~）
len(mk) >= open_len     # 不短于开围栏
rest.strip() == ""      # 开围栏行除语言标记外无其他内容
```

只有闭围栏三个条件全中才算关；否则行内容仍属代码块。`body_idx` 收集"不在代码块内"的行号，所有标题 / 表格 / 页面节计数都基于它。

---

## 4. 可复用操作

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"
WS="C:/Users/Admin/WorkBuddy AI/2026-10-15-12-57-23"

# 审计全量
"$PY" "$WS/_verify/audit_zh.py"

# 生成 README + 单文件完整版
"$PY" "$WS/_verify/build_readme.py" --merge

# 同步到 GitHub（目录同步，先 dry-run）
SK="C:/Users/Admin/.workbuddy-ai/skills/github-sync"
"$PY" "$SK/scripts/sync.py" --src "$WS/goose-docs-zh" --dest "goose-docs-zh" --dry-run
"$PY" "$SK/scripts/sync.py" --src "$WS/goose-docs-zh" --dest "goose-docs-zh" -m "..."
```

远端哈希复核（**必须带 `-z`**）：

```bash
"$PY" - <<'EOF'
import subprocess, os
CLONE=r'C:/Users/Admin/.workbuddy-ai/skills/github-sync/_work/share'
LOCAL=r'<本地目录>'
raw=subprocess.run(['git','-C',CLONE,'ls-tree','-r','-z','HEAD','--','goose-docs-zh'],
                   capture_output=True).stdout
for e in [x for x in raw.split(b'\x00') if x]:
    meta,path=e.split(b'\t',1)
    sha=meta.split()[2].decode()
    rel=path.decode('utf-8').split('goose-docs-zh/',1)[1]
    lp=os.path.join(LOCAL,rel)
    h=subprocess.run(['git','-C',CLONE,'hash-object',lp],
                     capture_output=True).stdout.decode().strip()
    print('OK' if h==sha else 'DIFF', rel)
EOF
```

---

## 5. 坑与反直觉（8 条，全部实测）

| # | 坑 | 症状 | 根因 | 处置 |
|---|---|---|---|---|
| 1 | **4 空格缩进的围栏不被识别** | 审计报「页面节 8≠9 + 围栏奇数 + 标题偏少」三项同时出现 | 围栏正则 `^ {0,3}(```\|~~~)` 允许 0–3 空格；4 空格行不算围栏 → 该行成了普通内容 → 后续围栏全部错位配对，**把下一个页面节标题吞进"代码块"** | 把该行缩进降到 2 空格（与同块其他围栏一致），配对立即恢复 |
| 2 | 「围栏奇数」与「页面节偏少」是**同一根因的两个症状** | 只看到页面节少会误以为漏译 | 配对错位使标题被围栏感知判为代码块内 | 先修围栏，再谈页数 |
| 3 | **纯行计数 ≠ 配对计数** | 审计报 97（奇），手工配对数到 96 | 错位状态下，代码块内部的 `  ```sh` 会被 `findall` 计入行数，但不参与配对 | 判断"是否真有问题"要看**配对结果**（是否 unclosed），不能只看奇偶 |
| 4 | **模板页的 `](/)` 占位链接** | 审计报「相对链 1」 | `mcp/_template_.mdx` 原文就写 `[{Extension Name} MCP Server](/)`，译文照抄 | 绝对化为 `](https://block.github.io/goose/)`——语义不变且消除相对链 |
| 5 | **体积判据绝不能是「中文比英文短」** | 早期若按 40%–60% 判据，会为凑指标而删内容 | 中文 UTF-8 单字 3 字节，逐句完整翻译后体积与英文**基本持平** | 硬性区间 **90%–130%**；实测全量 95% |
| 6 | **`git ls-tree` 中文文件名是八进制转义** | 哈希复核全部报 DIFF | 默认 `core.quotePath=true`，输出 `"goose-zh-13-MCP\346\211\251..."`；用 `sed` 去引号无法解码 | 用 `git ls-tree -r -z` + Python `split(b'\x00')` 解析；或 `-c core.quotePath=false` |
| 7 | **目录同步是镜像覆盖**（github-sync 坑 10） | 会静默删除仓库里多出的文件、把新版本回退 | `sync.py` 对目录执行 `rmtree(dest)` + `copytree(src,dest)` | 推前必跑 `--dry-run` 看 CHANGED 列表；**确认没有意外删除**再推。能拆单文件就拆单文件 |
| 8 | **429 限流会阻塞整批翻译** | 子代理返回 `429 too many requests / usage exceeds frequency limit` | 日额度 / 频率限制 | 额度恢复后**并行 7 章一次性跑通**；受阻时如实记录恢复时间，**绝不用摘要或猜测填充未产出章节** |
| 9 | **YAML 里嵌缩进围栏会让 Markdown 提前闭合**（**真实渲染缺陷**，不只是审计误报） | 审计报「页面节 43≠44」「20≠23」；渲染时 YAML 块被截断、后续页面节标题落进代码块 | Recipe 的 `prompt:` 字段里写了 2 空格缩进的 ` ``` ` 示例。**闭围栏允许 ≤3 空格缩进**，于是它合法地关闭了外层 ` ```yaml ` 块 | **把外层围栏升级为 4 个反引号** ` ````yaml ` `（闭围栏必须 ≥ 开围栏长度，内部 3 反引号不再闭合它）。脚本 `_verify/fix_extra.py`，本次修 10 块 |
| 10 | **围栏计数也必须走围栏感知** | 升级为 4 反引号后，用 `^ {0,3}``` 正则计数仍会把块内缩进围栏算进去 → 奇偶判断失真 | 正则只看行首，不看上下文 | 让 `split_code` 同时返回「被识别为围栏的行集合」，计数用它 |
| 11 | **子代理会留下分片临时文件** | 推送时把 `_p23_2.md`、`_tmp27_p1.md` 一起推上 GitHub | 大章分片写临时文件后忘记删除 | 推前 `ls` 确认无 `_tmp*` / `_p*`；dry-run 的 CHANGED 列表里也能看到 |

### 其他值得记的

- **HTML 章节重编号必须倒序替换**（v2.1 期踩坑）：`s9→s10 … s3→s4` 与 `h2n`、`h3` 全部要从大到小，否则连锁覆盖。断言式替换（每步 `assert s.count(old)==cnt`）是唯一可靠做法。
- **整页截图有像素预算**：超 134,217,728 字节报错；改为逐节渲染 + JS 移除无关 section，并记得把 `.shell` 的 `grid-template-columns` 改成 `1fr`（删掉 sidebar 后 `.main` 会落进 264px 第一列被压窄）。
- **截图验证要用 `127.0.0.1` 而非 `file://`**（后者被浏览器能力门拒绝），后台服务用 `run_in_background` 启动。

---

## 6. 覆盖范围（2026-10-15 已全量覆盖）

### 覆盖结果

| 批次 | 路径 | 文件 | 字节 | 章节 |
|---|---|---|---|---|
| 一 | `documentation/docs/**/*.{md,mdx}` | 173 | 1,351,256 | 1–22 |
| 二 | `documentation/blog/**/index.{md,mdx}` | 112 | 977,567 | 23–29 |
| 二 | `documentation/src/pages/recipes/data/recipes/**.yaml` | 67 | 298,025 | 30–31 |
| 二 | `<repo-root>/*.md` | 16 | 118,749 | 32 |
| 二 | 文档站工程：`documentation/{README,AGENTS,CLAUDE}.md`、`documentation/automation/**`、`blog/README.md`、`src/pages/grants.md`、`src/pages/**/README.md`、`docs/docker/*`、`docs/**/_category_.json` | 29 | 47,930 | 33 |
| **合计** | | **397** | **2,793,527** | **33 章** |

### 第一批为什么会漏（根因）

立项时把抓取范围写死为 `documentation/docs/`。`documentation/` 顶层实际结构：
`docs`(224 文件) / `blog`(332) / `src`(163) / `static`(87) / `automation`(12) / `scripts`(9) / `plugins`(3)。

**教训：定抓取范围前先枚举目标目录的顶层结构**，否则会系统性漏掉整类内容——此处漏掉的量与正文等量（1.37 MB）。

### 第二批的特殊处理（非 Markdown 文件）

| 类型 | 处理方式 |
|---|---|
| Recipe YAML（67） | **中文导读 + 完整 YAML 原文代码块**：`## 中文标题` → `> 原文：<GitHub blob>` → 用途 → 参数表（参数名/说明/默认值）→ 所需扩展 → 完整 YAML 原文（一字不改）。既让中文读者看懂，又保证 Recipe 可直接取用 |
| Dockerfile / docker-compose.yml | 同上：中文导读 + 完整原文代码块 |
| `_category_.json`（17） | 中文说明（侧栏显示名 + 排序）+ 原文 JSON 代码块 |

### 博客章的出处 URL 规则（与 docs 章不同）

源 `documentation/blog/2025-03-06-goose-tips/index.md` → `> 原文：https://block.github.io/goose/blog/2025-03-06-goose-tips`
即：去掉 `documentation/` 前缀 → 去掉结尾 `/index.md|mdx` → 拼 `https://block.github.io/goose/`。
仓库内非站点文件（Recipe YAML / 仓库根 md / Dockerfile / `_category_.json`）用 `https://github.com/aaif-goose/goose/blob/main/<路径>`。

### 核查方法（可复用）

```bash
# 用 Git Trees API 一次拿全树，按路径模式分组统计（含 size 字段）
# 关键：不要只看 documentation/docs/，要枚举 documentation/ 的全部子目录
# 实测 documentation/ 顶层 = docs(224) / blog(332) / src(163) / static(87) / automation(12) / scripts(9) / plugins(3)
```

判定「译文是否漏译」的三项检查（本项目实测结论：无漏译）：

| 检查 | 方法 | 结果 |
|---|---|---|
| 源覆盖 | 磁盘源文件集 ↔ `groups.json` ↔ 译文 `> 原文：` URL 集，三方求差 | 173 / 173 / 173，无差 |
| 逐页体积比 | 每页 `译文节字节 / 源文件字节` | 中位 **94%**；仅 4 页 <80%，均为 300–600 B 极短页（中文/英文字节比在小样本上波动），最低 60% |
| 逐页指标 | 图片 / 围栏行 / 标题 / 表格行 逐页比对 | 围栏行 **2331 : 2331 完全一致**；图片 29 : 29；其余差异经逐条目视确认为**源文件压行 / 缩进代码块导致的统计假阳性**，非译文缺失 |

---

## 7. 未核实项

| 项 | 说明 |
|---|---|
| 官方是否会出中文版 | 截至 2026-10-15，`docusaurus.config.ts` 为 `locales: ["en"]`、无 `i18n/` 目录；未来是否加中文未验证 |
| 源站页面后续更新 | 本手册是 2026-10-15 快照；源站改动后需重跑流水线（章节文件可原地替换） |
| 部分源页面的换行还原 | 源站少量页面的多行内容在抽取时被压成一行（表格错位、代码块挤行），译文按语义还原换行，未增删字符——还原度未逐页人工核对 |

---

## 修订记录

- **1.2**（2026-10-15）：**补全 `docs/` 之外的全部 224 个文件 / 1,442,271 B** —— 新增第 23–33 章（博客 7 章 112 篇、Recipe 模板 2 章 67 个 YAML、仓库治理 16 篇、文档站工程 29 个），全手册达 **33 章 / 397 页面节 / 99% 体积**。新增坑 9–11（YAML 内嵌缩进围栏致 Markdown 提前闭合、围栏计数须围栏感知、子代理分片临时文件）；第 6 节改为「已全量覆盖」并补第二批非 Markdown 文件的处理策略。
- **1.1**（2026-10-15）：补第 6 节「覆盖范围与未覆盖清单」——用 Trees API 全树枚举发现 `docs/` 之外尚有 **1,435,014 B / 约 200 个文件**未覆盖（博客 112 篇 977,567 B 为主）；补「译文是否漏译」三项核查方法与实测结论；修正 `tutorials/subagents.md` 一处 frontmatter `image:` 泄漏为正文图。
- **1.0**（2026-10-15）：首次沉淀。记录 22 章 / 173 页全量完成、流水线 7 步、审计五项判据、围栏感知解析规则、8 条坑。
