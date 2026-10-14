# -*- coding: utf-8 -*-
"""生成 mod 源码索引：工坊ID / packageId / 名称 / 源码路径 / DLL 路径 / 版本。"""
import os, re, csv, io, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modlib import C, load_user, read_mod

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
OUT = r"C:\Users\Admin\WorkBuddy AI\2026-10-07-11-55-59\outputs\mod源码索引.csv"
SKIP = {".git", "obj", "bin", ".vs", "node_modules", "packages"}


def scan(mod_dir):
    srcs, dlls, vers = [], [], set()
    # 版本目录：mod 根下直接叫 1.4 / 1.5 / 1.6 的文件夹
    for d in os.listdir(mod_dir):
        if re.fullmatch(r"1\.\d", d) and os.path.isdir(os.path.join(mod_dir, d)):
            vers.add(d)
    for root, dirs, files in os.walk(mod_dir):
        dirs[:] = [d for d in dirs if d.lower() not in SKIP]
        rel = os.path.relpath(root, mod_dir).replace("\\", "/")
        base = os.path.basename(root).lower()
        if base == "source":
            cs = sum(1 for r2, d2, f2 in os.walk(root)
                     for f in f2 if f.lower().endswith(".cs"))
            if cs:
                srcs.append((rel, cs))
        if base == "assemblies":
            for f in files:
                if f.lower().endswith(".dll"):
                    dlls.append(os.path.join(rel, f).replace("\\", "/"))
    return srcs, dlls, sorted(vers)


user = load_user()
rows = []
for d in sorted(os.listdir(C), key=lambda x: (not x.isdigit(), x)):
    p = os.path.join(C, d)
    if not os.path.isdir(p):
        continue
    pids, name, size = read_mod(p)
    srcs, dlls, vers = scan(p)
    hit = sorted(user[k] for k in {x.lower() for x in pids} & set(user))
    rows.append([
        d, name,
        "; ".join(sorted(pids)) or "(无 packageId)",
        "; ".join(hit) or "",
        os.path.join(p, srcs[0][0]).replace("/", "\\") if srcs else "",
        sum(n for _, n in srcs),
        "; ".join(os.path.join(p, x).replace("/", "\\") for x in dlls[:3]),
        len(dlls),
        ",".join(vers),
        "%.1f" % (size / 1024 / 1024),
    ])

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["工坊ID", "Mod名称", "packageId(自身)", "命中的用户packageId",
                "源码目录", ".cs文件数", "程序集DLL", "DLL数", "支持版本", "大小(MB)"])
    w.writerows(rows)

json.dump(rows, open(r"C:\SteamCMDData\source-index.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

nsrc = sum(1 for r in rows if r[4])
ndll = sum(1 for r in rows if r[6])
print("已写出:", OUT)
print("总 mod:", len(rows))
print("带 C# 源码:", nsrc)
print("带程序集 DLL:", ndll)
print("两者都无（纯 XML/贴图 mod）:", sum(1 for r in rows if not r[4] and not r[6]))
print()
print("=== 源码最多的 8 个 mod ===")
for r in sorted(rows, key=lambda x: -x[5])[:8]:
    print("  %-12s %-38s %3d 个 .cs" % (r[0], r[1][:36], r[5]))
