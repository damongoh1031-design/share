# 文档索引

| 文件 | 内容 | 读者 | 状态 |
|---|---|---|---|
| [PRD.md](PRD.md) / [prd.html](prd.html) | **产品规划书 v1.0**：范围、角色、流程、83 条功能需求、数据模型、非功能需求、技术方案、里程碑、风险 | 产品 / 研发 / 测试 / 业务方 | 待评审 |
| [UI-KIT.md](UI-KIT.md) | 界面规范：色彩、字号、间距、组件、logo 用法、交互约定、不要做的事 | 前端 / 设计 | 可用 |
| [CODE-MAP.md](CODE-MAP.md) / [code-map.html](code-map.html) | 原型代码图谱：六层结构、数据模型、函数索引、扩展手册、已知债务 | 研发 | 可用 |
| [CRM-OPTIMIZATION.md](CRM-OPTIMIZATION.md) / [crm-optimization.html](crm-optimization.html) | 对标成熟产品的优化建议 v2：能力对照、已实现项、待办项、指标口径 | 产品 / 业务方 | 可用 |
| [build-prd.py](build-prd.py) | PRD.md → prd.html 的编译脚本（含封面与目录） | 研发 | 工具 |

## 阅读顺序

1. **业务方**：PRD.md 第 1–4 章 → 第 10 章开放问题
2. **研发**：PRD.md 第 4–8 章 → CODE-MAP.md → UI-KIT.md
3. **设计**：UI-KIT.md → 原型 `prototype/crm-prototype.html`
4. **测试**：PRD.md 第 4.2 节验收标准 + 第 11.3 节验收清单

## 重新生成

```bash
python docs/build-prd.py        # PRD.md → prd.html
node prototype/_test/cdp.mjs "$PWD/prototype/crm-prototype.html" ./suite.mjs
node prototype/_test/cdp.mjs "$PWD/prototype/crm-prototype.html" ./suite3.mjs
```
