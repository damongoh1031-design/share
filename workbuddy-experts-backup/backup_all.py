#!/usr/bin/env python3
"""Comprehensive backup: zip ALL expert and skill plugins across marketplaces.

Classification per plugin dir:
- expert: has agents/
- skill:  has skills/ OR root SKILL.md OR rules/
- tool:   everything else (commands//hooks/ CLI tools) -> excluded from scope
"""
import json
import zipfile
from pathlib import Path

BASE = Path(r"C:/Users/Admin/.workbuddy-ai/plugins/marketplaces")
OUT = Path(r"C:/Users/Admin/WorkBuddy AI/2026-10-20-11-35-29/experts-backup")
DIST = OUT / "dist"

MARKETPLACES = ["my-experts", "experts", "cb_teams_marketplace", "codebuddy-plugins-official"]


def classify(d: Path) -> str:
    if (d / "agents").is_dir():
        return "expert"
    if (d / "skills").is_dir() or (d / "SKILL.md").is_file() or (d / "rules").is_dir():
        return "skill"
    return "tool"


def read_plugin_json(d: Path):
    for meta in [".codebuddy-plugin", ".workbuddy-plugin"]:
        p = d / meta / "plugin.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                return {}
    return {}


manifest, excluded_tools = [], []
for mp in MARKETPLACES:
    plugins_dir = BASE / mp / "plugins"
    if not plugins_dir.is_dir():
        continue
    for d in sorted(plugins_dir.iterdir()):
        if not d.is_dir():
            continue
        kind = classify(d)
        if kind == "tool":
            excluded_tools.append(f"{mp}/{d.name}")
            continue
        zip_path = DIST / f"{mp}__{d.name}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(d.rglob("*")):
                if f.is_file():
                    zf.write(f, f.relative_to(d.parent))
        pj = read_plugin_json(d)
        n_agents = len(list((d / "agents").glob("*.md"))) if kind == "expert" else 0
        n_skills = 0
        if (d / "skills").is_dir():
            n_skills = len([p for p in (d / "skills").iterdir() if p.is_dir()])
        elif (d / "SKILL.md").is_file():
            n_skills = 1
        manifest.append({
            "marketplace": mp, "dir": d.name, "type": kind,
            "zip": zip_path.name, "size_kb": round(zip_path.stat().st_size / 1024, 1),
            "agents": n_agents, "skills": n_skills,
            "description": (pj.get("description") or "")[:120],
        })
        print(f"OK [{kind:6s}] {mp}__{d.name}  {zip_path.stat().st_size//1024}KB")

(OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

my_manifest = BASE / "my-experts" / ".codebuddy-plugin" / "marketplace.json"
if my_manifest.exists():
    (OUT / "my-experts-marketplace.json").write_text(my_manifest.read_text(encoding="utf-8"), encoding="utf-8")

exp = sum(1 for e in manifest if e["type"] == "expert")
skl = sum(1 for e in manifest if e["type"] == "skill")
print(f"\nTotal: {len(manifest)} zips ({exp} expert + {skl} skill), excluded tools: {len(excluded_tools)}")
for t in excluded_tools:
    print("  tool-skip:", t)
