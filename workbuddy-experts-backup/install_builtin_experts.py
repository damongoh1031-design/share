#!/usr/bin/env python3
"""Download (install) all built-in marketplace experts into my-experts."""
import json
import shutil
from pathlib import Path

CONFIG = Path(r"C:/Users/Admin/.workbuddy-ai")
SRC_MP = CONFIG / "plugins" / "marketplaces" / "experts" / "plugins"
DST_MP = CONFIG / "plugins" / "marketplaces" / "my-experts"
DST_PLUGINS = DST_MP / "plugins"
MANIFEST = DST_MP / ".codebuddy-plugin" / "marketplace.json"

# 1. enumerate built-in marketplace experts (dirs with agents/)
src_experts = sorted([d for d in SRC_MP.iterdir() if d.is_dir() and (d / "agents").is_dir()])
print(f"Built-in marketplace experts found: {len(src_experts)}")

# 2. copy each into my-experts/plugins
copied = []
for d in src_experts:
    dst = DST_PLUGINS / d.name
    if dst.exists():
        print(f"SKIP (already installed): {d.name}")
    else:
        shutil.copytree(d, dst)
        print(f"COPIED: {d.name}")
    copied.append(d.name)

# 3. register in my-experts/marketplace.json (same format as register_expert.py / app reconcile)
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
entries = {p["source"]: p for p in manifest.get("plugins", [])}
added = []
for name in copied:
    pj_path = DST_PLUGINS / name / ".codebuddy-plugin" / "plugin.json"
    if not pj_path.exists():
        # try .workbuddy-plugin
        alt = DST_PLUGINS / name / ".workbuddy-plugin" / "plugin.json"
        pj_path = alt if alt.exists() else None
    pj = json.loads(pj_path.read_text(encoding="utf-8")) if pj_path else {}
    src_key = f"./plugins/{name}"
    if src_key in entries:
        print(f"ALREADY REGISTERED: {name}")
        continue
    manifest.setdefault("plugins", []).append({
        "name": pj.get("name", name),
        "source": src_key,
        "description": pj.get("description", ""),
    })
    added.append(name)
    print(f"REGISTERED: {name}")

MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nDone: copied={len(copied)} added={len(added)} total_in_my_experts={len(manifest['plugins'])}")
