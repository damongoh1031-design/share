#!/usr/bin/env python3
"""Regenerate experts-backup README.md from manifest.json (experts + skills)."""
import json
from pathlib import Path

OUT = Path(r"C:/Users/Admin/WorkBuddy AI/2026-10-20-11-35-29/experts-backup")
m = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
total = sum(e["size_kb"] for e in m)
exp = [e for e in m if e["type"] == "expert"]
skl = [e for e in m if e["type"] == "skill"]

MP_ZH = {"my-experts": "我的专家", "experts": "内置市场", "cb_teams_marketplace": "专家团市场", "codebuddy-plugins-official": "官方插件市场"}

L = []
L.append("# WorkBuddy 专家与 Skills 备份")
L.append("")
L.append("- 更新时间：2026-10-20（第四次刷新，首版含 skills）")
L.append(f"- 备份 zip 总数：{len(m)} 个（专家 {len(exp)} + skills {len(skl)}），总体积 {total/1024:.1f} MB")
L.append("- 覆盖 4 个市场：my-experts / experts / cb_teams_marketplace / codebuddy-plugins-official")
L.append("- 分类规则：agents/ → 专家；skills/ 或根 SKILL.md 或 rules/ → skill；纯 CLI 工具（commands//hooks/，如各 LSP、supabase）不备份")
L.append("")
L.append("## 一、专家（按市场）")
for mp in ["my-experts", "experts", "cb_teams_marketplace", "codebuddy-plugins-official"]:
    rows = sorted([e for e in exp if e["marketplace"] == mp], key=lambda x: x["dir"])
    if not rows:
        continue
    L.append("")
    L.append(f"### {MP_ZH[mp]}（{mp}，{len(rows)} 个）")
    L.append("")
    L.append("| 专家 | 角色数 | 体积(KB) |")
    L.append("|---|---|---|")
    for e in rows:
        L.append(f'| {e["dir"]} | {e["agents"]} | {e["size_kb"]} |')
L.append("")
L.append("## 二、Skills（46 个）")
for mp in ["cb_teams_marketplace", "codebuddy-plugins-official"]:
    rows = sorted([e for e in skl if e["marketplace"] == mp], key=lambda x: x["dir"])
    if not rows:
        continue
    L.append("")
    L.append(f"### {MP_ZH[mp]}（{mp}，{len(rows)} 个）")
    L.append("")
    L.append("| Skill | 体积(KB) |")
    L.append("|---|---|")
    for e in rows:
        L.append(f'| {e["dir"]} | {e["size_kb"]} |')
L.append("")
L.append("## 三、文件清单")
L.append("")
L.append("- dist/：134 个 zip，命名 `<市场>__<插件名>.zip`，内容为该插件目录完整原样打包")
L.append("- manifest.json：逐插件元数据（类型、来源、体积、角色/skill 数）")
L.append("- my-experts-marketplace.json：我的专家注册清单快照")
L.append("- backup_all.py：重新生成本备份（覆盖式，全量重打）；backup_experts.py 为旧版脚本")
L.append("- install_experts.py / install_builtin_experts.py：安装专家到 my-experts（幂等）")
L.append("")
L.append("## 四、敏感数据提示")
L.append("")
L.append("- experts 与 my-experts 下的 malaysia-* 系列专家（hr-admin/legal/finance-tax/marketing）含商业电话号数据集（CSV/duckdb，源自 OSINT 项目），推送 public 仓库已获用户确认。")
L.append("- 删除超过 50 个文件的操作会被沙箱安全策略拦截（fail-closed），更新备份用覆盖式，不要整目录 rm。")

(OUT / "README.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"README regenerated: {len(m)} zips ({len(exp)} experts + {len(skl)} skills), {total/1024:.1f} MB")
