---
id: research-results-github-sync-spec
title: 规范：所有研究结果一律 push 到 GitHub share 仓库
tags: [规范, github-sync, 研究成果, 归档, 常驻约定]
created: 2026-10-14
updated: 2026-10-14
version: 1
status: active
source: 用户指定（2026-10-14）
confidence: 已核实
---

# 一句话结论

自 2026-10-14 起，**所有研究结果完成后一律立即 `git push` 到 `damongoh1031-design/share`（main 分支）**，不等用户提醒；该约定已写入 github-sync 技能的「用户常驻约定」，对所有后续会话生效。

# 适用范围

| 类别 | 示例 | 是否强制 push |
|---|---|---|
| 调研报告 | 市场/竞品/技术调研 md 报告 | 是 |
| KB 文档 | `kb/` 下所有入库文档 | 是 |
| 数据集 | csv/json/tsv 产出 | 是 |
| 脚本与工具 | 采集/分析/转换脚本 | 是 |
| 可视化 | SVG/HTML 图表、dashboard | 是 |
| 临时文件、缓存、`_work` 克隆 | — | 否 |

# 仓库与落点规范

| 项 | 值 |
|---|---|
| 仓库 | `https://github.com/damongoh1031-design/share` |
| 分支 | `main` |
| 可见性 | public |
| 目录命名 | 每个项目/主题一个子目录，kebab-case，如 `malaysiayp-phone-directory/`、`kb/`、`workbuddy-2026-10-14/kb` |
| 配置映射 | 技能 `config.json` 的 `mappings` 按工作区维护 |

# 标准操作流程

1. 研究/任务完成 → 成果落盘到本地（工作区内）。
2. 提交前扫密钥：`grep -rniE "(password|api[_-]?key|ghp_|secret)" <dir>`，有命中先清理。
3. public 仓库 + 含个人数据（电话/邮箱）→ push **前**提醒用户是否转私有。
4. 推送：`python .workbuddy-ai/skills/github-sync/scripts/sync.py --src <本地> --dest <仓库子路径> -m "<说明>"`，或 `--use-config-mappings`。
5. 校验：exit 0 = 成功或无变更；输出中的 commit URL 可在浏览器打开确认。

# 红线（不可绕过）

- `token.txt`、`secrets/` 等凭据文件**永不入仓**；它们必须位于同步映射之外。
- 单次 push >10 MB 在沙箱前台会被 2 分钟超时 SIGTERM，用后台任务跑。
- push 被拒时单人仓库直接 `merge -X theirs` → 再 push → 仍失败 `--force`，不再询问。
- Windows 下 clone 报 `Filename too long` → `git config --global core.longpaths true`。

# 未核实项

- 仓库后续是否转 private 未定；若转私，本规范中 public 相关提醒同步作废。
- 旧 token 到期日（约 2027-01-10）以 GitHub 设置页为准。
