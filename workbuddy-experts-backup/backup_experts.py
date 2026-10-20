#!/usr/bin/env python3
"""Backup all WorkBuddy expert packages (plugins with agents/) into zips + manifest."""
import json
import zipfile
from pathlib import Path

BASE = Path(r"C:/Users/Admin/.workbuddy-ai/plugins/marketplaces")
OUT = Path(r"C:/Users/Admin/WorkBuddy AI/2026-10-20-11-35-29/experts-backup")
DIST = OUT / "dist"
DIST.mkdir(parents=True, exist_ok=True)

MARKETPLACES = ["my-experts", "experts", "cb_teams_marketplace"]

def read_plugin_json(expert_dir: Path):
    pj = expert_dir / ".codebuddy-plugin" / "plugin.json"
    if not pj.exists():
        return {}
    try:
        return json.loads(pj.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_parse_error": str(e)}

def pick(d: dict, *keys, default=""):
    for k in keys:
        v = d.get(k)
        if isinstance(v, dict):
            v = v.get("zh") or v.get("en")
        if v:
            return str(v)
    return default

manifest = []
for mp in MARKETPLACES:
    plugins_dir = BASE / mp / "plugins"
    if not plugins_dir.is_dir():
        continue
    for expert_dir in sorted(plugins_dir.iterdir()):
        if not expert_dir.is_dir() or not (expert_dir / "agents").is_dir():
            continue
        name = expert_dir.name
        zip_name = f"{mp}__{name}.zip"
        zip_path = DIST / zip_name
        # raw zip of the whole directory
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(expert_dir.rglob("*")):
                if f.is_file():
                    zf.write(f, f.relative_to(expert_dir.parent))
        pj = read_plugin_json(expert_dir)
        agent_files = [p.name for p in sorted((expert_dir / "agents").glob("*.md"))]
        skills = [p.name for p in sorted((expert_dir / "skills").glob("*")) if p.is_dir()] if (expert_dir / "skills").is_dir() else []
        manifest.append({
            "marketplace": mp,
            "dir": name,
            "zip": zip_name,
            "size_kb": round(zip_path.stat().st_size / 1024, 1),
            "agents": agent_files,
            "agent_count": len(agent_files),
            "skills": skills,
            "name": pick(pj, "name"),
            "displayName": pick(pj, "displayName"),
            "profession": pick(pj, "profession"),
            "expertType": pick(pj, "expertType", default="agent"),
            "displayDescription": pick(pj, "displayDescription"),
            "categoryId": pick(pj, "categoryId"),
            "version": pick(pj, "version"),
            "author": pick(pj, "author", default="marketplace"),
        })
        print(f"OK {zip_name}  agents={len(agent_files)}  {zip_path.stat().st_size//1024}KB")

(OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

# snapshot of my-experts registration manifest (what makes an expert appear in 我的专家)
my_manifest = BASE / "my-experts" / ".codebuddy-plugin" / "marketplace.json"
if my_manifest.exists():
    (OUT / "my-experts-marketplace.json").write_text(my_manifest.read_text(encoding="utf-8"), encoding="utf-8")
    print("snapshot: my-experts-marketplace.json")

print(f"\nTotal: {len(manifest)} experts backed up to {DIST}")
