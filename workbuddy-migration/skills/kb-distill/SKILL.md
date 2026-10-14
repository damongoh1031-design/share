---
name: kb-distill
description: "After every substantive answer, additionally produce a re-writable knowledge-base document that distills the session's knowledge into a stable, ingestible artifact. Use whenever a turn produced new conclusions, data, procedures, or pitfalls — and skip purely mechanical, repetitive, greeting, or simple-lookup replies. Trigger phrases: '沉淀知识库', 'kb', '整理成知识库文档', 'distill to kb', or any standing instruction to produce a knowledge-base doc after each answer."
description_zh: "每次实质性回答后，额外产出一份可入库、可复写的知识沉淀文档"
description_en: "Produce a re-writable knowledge-base document after every substantive answer"
version: 1.0.0
allowed-tools: Read,Write,Edit,Glob,Grep,Bash
display_name: "kb-distill"
display_name_en: "kb-distill"
visibility: "private"
metadata:
  tags: "knowledge-base, distillation, markdown, documentation, memory"
  category: "productivity"
---

# KB Distill — 知识库沉淀

## 核心规则

**每一次实质性回答之后，除正文外还要额外产出一份「可入库知识库」文档。**

正文是**交付物**（面向当下这个问题），KB 文档是**沉淀物**（面向未来的检索与复用）。两者内容可以不同长度、不同侧重，但 KB 文档**不是正文的复制**。

---

## 一、触发判定

### 要写

出现以下任一，即产出 KB 文档：

| 信号 | 例子 |
|---|---|
| 新结论 / 新判断 | 「推荐 X 而不是 Y，因为…」 |
| 新数据 / 新口径 | 价格、配额、版本号、实测数值 |
| 新流程 / 新操作 | 安装步骤、配置模板、可粘贴命令 |
| 新踩坑 | 反直觉行为、报错成因、规避方法 |
| 新对比 | 方案 A vs B 的维度表 |
| 对既有 KB 文档的修订 | 同一主题出现增量信息 → 原地更新 |

### 跳过

| 情形 | 说明 |
|---|---|
| 机械性回复 | 纯确认、格式转换、无新信息的转述 |
| 重复性回复 | 上一轮已沉淀过的同一结论，且无增量 |
| 寒暄 / 闲聊 | 打招呼、感谢、情绪回应 |
| 简单查询 | 单词、单数字、单命令即可回答，且无复用价值 |
| 纯执行汇报 | 「文件已生成」「命令已跑完」，无知识增量 |

> 拿不准时倾向**不写**。KB 的价值来自密度，不来自数量。

---

## 二、落点与命名

### 目录

- 默认：**当前工作区根目录下的 `kb/`**（不存在则创建）。
- 若工作区已有约定的 KB 根目录（写入 `MEMORY.md` 或用户指定），以约定为准。
- 跨项目通用知识、或用户指定了全局 KB 根：放全局根。

### 文件名 = 稳定 slug

- 格式：**英文小写 + 连字符**，2–6 个词，如 `hermes-workbuddy-mcp-extension-audit.md`。
- **按主题命名，不按会话命名** —— 这是「可复写」的前提。
  - ✗ `2026-10-09-回答整理.md`
  - ✓ `hermes-workbuddy-mcp-extension-audit.md`

### ★ 复写规则（最关键）

同一主题再次出现时：

1. **先 `Glob` 或 `Grep` 检查 `kb/` 下是否已有同主题文件。**
2. 有 → 用 **Edit 原地更新**该文件：
   - 刷新 frontmatter 的 `updated`
   - **递增 `version`**（`1.0` → `1.1` → `2.0`；小修 +0.1，结构性重写 +1.0）
   - 修订/替换过时章节，**追加**新章节
   - 在「修订记录」节留一行变更说明
3. 无 → 新建。

**绝不**产生 `-v2` / `-2026-10-09` / `-final` 之类的碎片文件。碎片会破坏知识库的检索与去重。

### 索引同步

每次新增或更新后，**同步更新 `kb/README.md`** 的条目表：

| slug | 标题 | tags | version | updated | status |
|---|---|---|---|---|---|
| [`slug`](./slug.md) | 标题 | tag1, tag2 | 1.0 | YYYY-MM-DD | stable |

---

## 三、文档结构（必须）

### 1. YAML frontmatter

```yaml
---
id: <slug>                      # 与文件名一致
title: <人类可读标题>
tags:                           # 3–8 个，供检索
  - tag1
  - tag2
created: YYYY-MM-DD
updated: YYYY-MM-DD
version: 1.0                    # 复写时递增
status: draft | stable | deprecated
source: <本次会话 / 本机实测 / 官方文档 / 外部来源>
confidence: 已核实 | 社区实证 | 推断
---
```

字段说明：

| 字段 | 规则 |
|---|---|
| `id` | 必须等于文件名去扩展名 |
| `tags` | 3–8 个，中英混用可，倾向英文小写连字符 |
| `version` | 新建从 `1.0` 起；复写递增 |
| `status` | 信息完整且已核实 → `stable`；有缺口 → `draft`；被取代 → `deprecated` |
| `confidence` | 只能取三值之一；混合时取最低 |
| `source` | 写清证据类型，便于回溯 |

### 2. 一句话结论（TL;DR）置顶

frontmatter 之后，第一个正文块必须是 `## 一句话结论`，一段话说清「是什么 / 该怎么做」。

### 3. 正文分节

- 按主题分节，**表格优先**，其次列表，最后才是段落。
- 数字必须带**口径与日期**（如「2000 次/月，2026-10 官方定价页」）。
- 结论必须带**核实状态**（已核实 / 社区实证 / 推断）。

### 4. 「可复用操作」一节

**必须存在**。内容为可直接粘贴的命令、配置块、步骤清单。

```bash
# 直接可跑的完整命令，不要伪代码
```

```yaml
# 直接可粘贴的配置，不要省略号占位
```

### 5. 「坑与反直觉」一节

**必须存在**（没有则写「无」）。只收「按直觉做会错」的条目。

### 6. 「未核实 / 存疑」一节

**必须存在**（没有则写「无」）。列出未验证的假设、缺失的证据、待补的信息。

### 7. 修订记录（可选）

仅当 `version > 1.0` 时添加：

```markdown
## 修订记录

- **1.1**（2026-10-10）：补充 X 平台的实测数据；修正 Y 的配额口径。
- **1.0**（2026-10-09）：初版。
```

---

## 四、提炼要求

| 要 | 不要 |
|---|---|
| 结论、数据、命令、坑 | 对话痕迹（「你问的」「上一轮说」） |
| 带口径与日期的数字 | 「大概」「可能」「差不多」 |
| 表格化对比 | 长篇散文 |
| 可验证的引用（来源 + 日期） | 无出处的断言 |
| 明确的核实状态标注 | 把推断当已核实写 |

**长度不是目标。** 一篇 40 行的 KB 文档如果能完整承载结论，胜过 400 行的复述。

---

## 五、格式选择

| 场景 | 输出 |
|---|---|
| 默认 | `.md` |
| 用户明确要 HTML | `.md` + `.html` |
| 主题天然需要可视化（架构图、流程、象限、时间线） | 另出 `.html`（自包含，内联 SVG/CSS），或在正文中用可视化组件 |
| 主题为纯文本知识（选型对比、配置、坑） | 仅 `.md` |

HTML 版本命名与 slug 一致，同目录，扩展名不同。

---

## 六、执行清单

每轮结束时自查：

1. ☐ 这一轮有实质知识增量吗？没有 → 跳过，不写。
2. ☐ 检索 `kb/` 下是否已有同主题文件？
3. ☐ 有 → 原地更新 + 递增 `version`；无 → 新建。
4. ☐ frontmatter 九个字段齐全？
5. ☐ 有「一句话结论」？
6. ☐ 有「可复用操作」？
7. ☐ 有「坑与反直觉」？
8. ☐ 有「未核实 / 存疑」？
9. ☐ 去掉了对话痕迹与客套？
10. ☐ 同步更新了 `kb/README.md`？
11. ☐ 在回复结尾给出了 KB 文件的相对路径？

---

## 七、模板

```markdown
---
id: <slug>
title: <标题>
tags:
  - <tag1>
  - <tag2>
created: YYYY-MM-DD
updated: YYYY-MM-DD
version: 1.0
status: draft
source: 本次会话
confidence: 推断
---

# <标题>

## 一句话结论

<一段话讲清是什么 / 该怎么做。>

---

## 1. <主题一>

<表格优先。数字带口径与日期，结论带核实状态。>

## 2. <主题二>

...

---

## 可复用操作

```bash
<可直接粘贴的命令>
```

```yaml
<可直接粘贴的配置>
```

---

## 坑与反直觉

1. **<反直觉结论>** —— <成因与规避方法>。

---

## 未核实 / 存疑

| 项 | 说明 |
|---|---|
| <项> | <为什么未核实、需要什么才能核实> |
```

---

## 八、反模式

| 反模式 | 为什么错 |
|---|---|
| 把正文原样复制成 KB 文档 | 没有提炼，只是重复；检索时命中率低 |
| 每个会话建一个新文件 | 碎片化，同一主题的知识被切散 |
| 用日期做文件名 | 无法复写，第二次必然新建 |
| 省略「未核实项」 | 读者无法区分已核实与推断，会误用 |
| 只写结论不写操作 | 沉淀物无法直接复用，等于没沉淀 |
| 为了凑格式写空章节 | 「无」比编造内容好 |
| 对寒暄/简单查询也写 | 稀释知识库密度 |
