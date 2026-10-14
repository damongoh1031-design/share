# -*- coding: utf-8 -*-
import os, csv, io, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modlib import C, load_user, read_mod

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
OUT = r"C:\Users\Admin\WorkBuddy AI\2026-10-07-11-55-59\outputs\已下载mod清单.csv"

user = load_user()
rows = []
for d in sorted(os.listdir(C), key=lambda x: (not x.isdigit(), x)):
    p = os.path.join(C, d)
    if not os.path.isdir(p):
        continue
    pids, name, size = read_mod(p)
    hit = sorted(user[k] for k in {x.lower() for x in pids} & set(user))
    rows.append([d, name, "; ".join(sorted(pids)) or "(无 packageId)",
                 "是" if hit else "否", "; ".join(hit), "%.1f" % (size / 1024 / 1024)])

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["工坊ID", "Mod 名称", "packageId(自身)", "在用户列表中", "命中的用户 packageId", "大小(MB)"])
    w.writerows(rows)

json.dump(rows, open(r"C:\SteamCMDData\manifest-rows.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("已写出:", OUT, "共", len(rows), "行")
print("命中:", sum(1 for r in rows if r[3] == "是"), " 未命中:", sum(1 for r in rows if r[3] == "否"))
