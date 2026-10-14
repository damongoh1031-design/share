#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 truecallerpy 的安装状态与源码关键参数（只读，不联网）"""
import importlib.metadata as md
import inspect
import os
import sys

print("=" * 70)
print("1) 安装状态")
print("=" * 70)
try:
    v = md.version("truecallerpy")
    dist = md.distribution("truecallerpy")
    print(f"version  : {v}")
    print(f"location : {dist.locate_file('truecallerpy')}")
    print(f"requires : {dist.requires}")
except Exception as e:
    print(f"未安装 -> {e}")
    sys.exit(0)

print()
print("=" * 70)
print("2) 源码文件清单 + clientsecret / 端点")
print("=" * 70)
try:
    import truecallerpy
    pkg_dir = os.path.dirname(inspect.getfile(truecallerpy))
    print(f"pkg_dir: {pkg_dir}\n")
    for root, dirs, files in os.walk(pkg_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in sorted(files):
            if f.endswith((".py", ".json")):
                p = os.path.join(root, f)
                rel = os.path.relpath(p, pkg_dir)
                print(f"  {os.path.getsize(p):>7}  {rel}")
except Exception as e:
    print(f"import 失败: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("3) 关键常量（clientsecret / URL / UA）")
print("=" * 70)
import re
for root, dirs, files in os.walk(pkg_dir):
    dirs[:] = [d for d in dirs if d != "__pycache__"]
    for f in sorted(files):
        if not f.endswith(".py"):
            continue
        p = os.path.join(root, f)
        src = open(p, encoding="utf-8", errors="ignore").read()
        hits = []
        for pat, tag in [
            (r'clientsecret["\']?\s*[:=]\s*["\']([^"\']+)["\']', "clientsecret"),
            (r'https://[a-zA-Z0-9\.\-]+truecaller\.com[a-zA-Z0-9/\.\-_]*', "URL"),
            (r'Truecaller/[\d\.]+ ?\(Android;[\d]+\)', "UA"),
            (r'["\'](search5-[a-z]+)["\']', "search host"),
        ]:
            for m in re.finditer(pat, src):
                hits.append(f"{tag}: {m.group(1) if m.groups() else m.group(0)}")
        if hits:
            print(f"\n--- {os.path.relpath(p, pkg_dir)} ---")
            for h in sorted(set(hits)):
                print(f"   {h}")
