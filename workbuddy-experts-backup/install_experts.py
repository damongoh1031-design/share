#!/usr/bin/env python3
"""Install experts from a source marketplace into my-experts (idempotent).

Usage: install_experts.py <source-marketplace> [--yes]
Example: install_experts.py cb_teams_marketplace
"""
import json
import shutil
import sys
from pathlib import Path

CONFIG = Path(r"C:/Users/Admin/.workbuddy-ai")
MP_ROOT = CONFIG / "plugins" / "marketplaces"
DST_MP = MP_ROOT / "my-experts"
DST_PLUGINS = DST_MP / "plugins"
MANIFEST = DST_MP / ".codebuddy-plugin" / "marketplace.json"


def read_plugin_json(expert_dir: Path):
    for meta in [".codebuddy-plugin", ".workbuddy-plugin"]:
        p = expert_dir / meta / "plugin.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                return {}
    return {}


def main():
    if len(sys.argv) < 2:
        print("usage: install_experts.py <source-marketplace>")
        return 1
    src_mp = sys.argv[1]
    src_plugins = MP_ROOT / src_mp / "plugins"
    if not src_plugins.is_dir():
        print(f"source marketplace not found: {src_plugins}")
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    registered = {p.get("source") for p in manifest.get("plugins", [])}
    installed, skipped, registered_new = [], [], []

    for d in sorted(p for p in src_plugins.iterdir() if p.is_dir() and (p / "agents").is_dir()):
        name = d.name
        dst = DST_PLUGINS / name
        src_key = f"./plugins/{name}"
        if dst.exists():
            skipped.append(name)
            print(f"SKIP (already installed): {name}")
            continue
        shutil.copytree(d, dst)
        installed.append(name)
        print(f"COPIED: {name}")
        if src_key not in registered:
            pj = read_plugin_json(dst)
            manifest.setdefault("plugins", []).append({
                "name": pj.get("name", name),
                "source": src_key,
                "description": pj.get("description", ""),
            })
            registered_new.append(name)
            print(f"REGISTERED: {name}")

    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDone: copied={len(installed)} registered={len(registered_new)} "
          f"skipped_existing={len(skipped)} total_in_my_experts={len(manifest['plugins'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
