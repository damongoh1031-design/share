# WorkBuddy 约束提示词（可直接粘贴）

## 标准版（推荐）

```
每次给出实质性回答后，除正文外再额外产出一份「可入库知识库」文档：

- 位置：工作区根目录的 kb/（不存在则创建）
- 命名：稳定英文 slug（小写+连字符），按主题命名不按日期命名
- 复写：同主题先检索 kb/，有则原地 Edit 更新并递增 frontmatter 的 version，无则新建。
  绝不产生 -v2 / -2026-10-09 之类的碎片文件
- frontmatter 必备：id / title / tags / created / updated / version / status / source / confidence
- 结构固定：一句话结论 → 分节正文（表格优先）→ 可复用操作 → 坑与反直觉 → 未核实项
- 提炼而非复制：去掉对话痕迹与客套，只留结论、数据、可粘贴的命令与配置
- 数字带口径与日期；结论标注 已核实 / 社区实证 / 推断
- 同步更新 kb/README.md 索引
- 跳过：机械性/重复回复、寒暄、简单查询
- 回复结尾给出 KB 文件路径
```

## 极简版（约束字符有限时用）

```
每次实质性回答后，另出一份可复写知识库文档到 kb/<稳定slug>.md：
带 YAML frontmatter（id/title/tags/created/updated/version/status/source/confidence），
同主题原地更新并递增 version（不建 -v2），结构为 一句话结论→分节正文→可复用操作→坑与反直觉→未核实项，
提炼不复制、数字带口径、同步更新 kb/README.md 索引、回复结尾给路径。
跳过机械性/重复/寒暄/简单查询。
```

## 单行版（塞进一句话约束）

```
每次实质性回答后另出一份可复写 KB 文档到 kb/<slug>.md（带 YAML frontmatter，同主题原地更新并递增 version，结构：结论→正文→可复用操作→坑→未核实项），并同步 kb/README.md；机械性/重复/寒暄回复跳过。
```

## 配套技能

细节流程见技能 `kb-distill`（`~/.workbuddy-ai/skills/kb-distill/SKILL.md`）。
约束提示词只负责「常驻触发」，技能负责「怎么做」。
