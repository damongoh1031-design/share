#!/usr/bin/env python3
"""Regenerate experts-backup README.md from manifest.json."""
import json
from pathlib import Path

OUT = Path(r"C:/Users/Admin/WorkBuddy AI/2026-10-20-11-35-29/experts-backup")
m = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
total = sum(e["size_kb"] for e in m)
my = [e for e in m if e["marketplace"] == "my-experts"]
ex = [e for e in m if e["marketplace"] == "experts"]
cb = [e for e in m if e["marketplace"] == "cb_teams_marketplace"]

L = []
L.append("# WorkBuddy 专家备份")
L.append("")
L.append("- 更新时间：2026-10-20（第三次刷新）")
L.append(f"- 备份 zip 总数：{len(m)} 个，总体积 {total/1024:.1f} MB")
L.append("- 覆盖三个市场：my-experts（我的专家，29 个）/ experts（内置市场，23 个）/ cb_teams_marketplace（专家团市场，7 个专家）")
L.append("")
L.append("## 我的专家（my-experts，已安装 29 个）")
L.append("")
L.append("由内置市场 22 个 + 专家团市场 6 个 + 自建 1 个组成；内置市场 trading-agent（13 角色）因目录名被专家团版占用，未单独装入。")
L.append("")
L.append("| # | 专家 | 角色数 | 来源市场 |")
L.append("|---|---|---|---|")
EXPERTS_SRC = Path(r"C:/Users/Admin/.workbuddy-ai/plugins/marketplaces/experts/plugins")
CB_SRC = Path(r"C:/Users/Admin/.workbuddy-ai/plugins/marketplaces/cb_teams_marketplace/plugins")
def src_of(name):
    if name == "rimworld-mod-guardian":
        return "自建"
    if name == "trading-agent":
        return "专家团市场（内置版重名跳过）"
    if (EXPERTS_SRC / name).is_dir():
        return "内置市场"
    if (CB_SRC / name).is_dir():
        return "专家团市场"
    return "-"
for i, e in enumerate(sorted(my, key=lambda x: x["dir"]), 1):
    L.append(f'| {i} | {e["dir"]} | {e["agent_count"]} | {src_of(e["dir"])} |')
L.append("")
L.append("## 本次新增（2026-10-20 内置市场刷新）")
L.append("")
L.append("内置市场今日新增 9 个专家，已全部装入我的专家并备份：")
L.append("")
L.append("| 专家 | 角色数 | 体积(KB) |")
L.append("|---|---|---|")
NEW = ["data-ai-experts", "design-experts", "engineering-workflow-skills", "industry-service-experts",
       "openspec-doc-team", "product-experts", "product-strategy-team", "spatial-computing-experts", "trading-agent"]
for name in NEW:
    e = next((x for x in ex if x["dir"] == name), None)
    if e:
        L.append(f'| {name} | {e["agent_count"]} | {e["size_kb"]} |')
L.append("")
L.append("## 文件清单")
L.append("")
L.append("- dist/：59 个 zip，命名为 `<市场>__<专家名>.zip`，内容为该专家目录完整原样打包")
L.append("- manifest.json：逐专家元数据（来源、体积、角色、安装状态）")
L.append("- my-experts-marketplace.json：我的专家注册清单快照（恢复时需放回 my-experts/.codebuddy-plugin/）")
L.append("- install_experts.py：从指定市场安装专家到 my-experts（幂等）")
L.append("- install_builtin_experts.py：首轮内置市场安装脚本（历史留存）")
L.append("- backup_experts.py：重新生成本备份")
L.append("")
L.append("## 敏感数据提示")
L.append("")
L.append("- my-experts 与 experts 下的 malaysia-hr-admin / malaysia-legal 各含一份商业电话号数据集（CSV/duckdb，源自 OSINT 项目），推送 public 仓库已获用户确认。")

(OUT / "README.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"README.md regenerated: {len(m)} zips, {total/1024:.1f} MB, my-experts={len(my)}")
