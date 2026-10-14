# -*- coding: utf-8 -*-
import csv, io, os, json, re

RMK = r"C:/SteamCMDData/rmk-modlist.tsv"
UNRES = r"C:/Users/Admin/WorkBuddy AI/2026-10-07-11-55-59/outputs/未解析清单.csv"

rmk = {}          # lower(pid) -> (wid, name, path)
name2wid = {}     # lower(name) -> (wid, pid)
with io.open(RMK, encoding="utf-8-sig", errors="ignore") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) < 4: continue
        wid, name, path, pid = p[0].strip(), p[1].strip(), p[2].strip(), p[3].strip()
        if not wid.isdigit() or not pid: continue
        rmk.setdefault(pid.lower(), (wid, name, path))
        name2wid.setdefault(name.lower(), (wid, pid))

print("RMK 映射条数:", len(rmk))

rows = list(csv.DictReader(io.open(UNRES, encoding="utf-8-sig")))
print("未解析条数:", len(rows))

hit, miss = [], []
for r in rows:
    pid = (r.get("packageId") or "").strip()
    if not pid: continue
    if pid.lower() in rmk:
        wid, name, path = rmk[pid.lower()]
        hit.append((pid, wid, name))
    else:
        miss.append(pid)

print("命中:", len(hit), " 未命中:", len(miss))
for pid, wid, name in hit[:25]:
    print("  OK %-42s -> %s  %s" % (pid, wid, name))
print("...")
with io.open(r"C:/SteamCMDData/rmk-hit.txt", "w", encoding="utf-8") as f:
    for pid, wid, name in hit:
        f.write("%s\t%s\t%s\n" % (wid, name, pid))
with io.open(r"C:/SteamCMDData/rmk-miss.txt", "w", encoding="utf-8") as f:
    for pid in miss:
        f.write(pid + "\n")
