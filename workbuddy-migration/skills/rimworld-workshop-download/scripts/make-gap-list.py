# -*- coding: utf-8 -*-
import os, csv, io, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modlib import C, load_user, read_mod

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
MAPF = r"C:\SteamCMDData\mapping-final.csv"
MAP2 = r"C:\SteamCMDData\mapping-round2.csv"
REVIEW = r"C:\SteamCMDData\review-needed.csv"
OUT = r"C:\Users\Admin\WorkBuddy AI\2026-10-07-11-55-59\outputs\未解析清单.csv"

user = load_user()
matched = set()
for d in os.listdir(C):
    p = os.path.join(C, d)
    if not os.path.isdir(p):
        continue
    pids, _, _ = read_mod(p)
    matched |= {x.lower() for x in pids} & set(user)
missing = sorted(user[k] for k in user if k not in matched)

q = {}
for path in (MAPF, MAP2):
    if not os.path.exists(path):
        continue
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            pid = (row.get("packageId") or "").strip()
            if not pid:
                continue
            v = row.get("query") or row.get("best_title") or ""
            if v:
                q.setdefault(pid.lower(), v)

rev = {}
if os.path.exists(REVIEW):
    with open(REVIEW, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            pid = (row.get("packageId") or "").strip()
            if pid:
                rev[pid.lower()] = row

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["packageId", "建议检索词", "状态", "备注"])
    for pid in missing:
        k = pid.lower()
        query = q.get(k, "")
        if not query:
            parts = [p for p in pid.split(".") if p.lower() not in ("zh", "zhcn", "cn", "chs", "lib")]
            query = " ".join(parts[1:] if len(parts) > 1 else parts)
        if k in rev:
            w.writerow([pid, query, "曾映射到低置信候选", rev[k].get("说明", "")])
        else:
            w.writerow([pid, query, "未映射到任何工坊 ID", "需在 RimSort 工坊浏览器手搜"])

print("已写出:", OUT)
print("未命中总数:", len(missing))
print("有建议检索词:", sum(1 for p in missing if p.lower() in q))
