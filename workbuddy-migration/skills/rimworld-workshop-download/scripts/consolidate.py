# -*- coding: utf-8 -*-
import csv, io, json, os, re

OUT = r"C:/Users/Admin/WorkBuddy AI/2026-10-07-11-55-59/outputs/未解析-网络检索结果.csv"
UNRES = r"C:/Users/Admin/WorkBuddy AI/2026-10-07-11-55-59/outputs/未解析清单.csv"
CAND  = r"C:/Users/Admin/WorkBuddy AI/2026-10-07-11-55-59/outputs/候选复核表.csv"

# 1) RMK 精确映射
rmk = {}
for line in io.open(r"C:/SteamCMDData/rmk-hit.txt", encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    if len(p) >= 3: rmk[p[2].lower()] = (p[0], p[1], "RMK 韩化组 ModList.tsv（packageId 精确命中）")

# 2) 汉化包池匹配
zhm = {}
for r in json.load(io.open(r"C:/SteamCMDData/zh-match5.json", encoding="utf-8")):
    zhm[r["pid"].lower()] = r

# 3) 候选复核表
cand = {}
for r in csv.DictReader(io.open(CAND, encoding="utf-8-sig")):
    cand[r["packageId"].lower()] = r

# 4) 人工核定的高确定映射（工坊检索直证）
MAN = {
 "spirit.medieval.overhaul.zht": ("2567264503", "Medieval Overhaul 汉化包"),
 "zh.vanillaexpanded.vgeneticse": ("2809374942", "Vanilla Genetics Expanded - 简&繁中文汉化包"),
 "zh.vanillaexpanded.vieat": ("2722599293", "Vanilla Ideology Expanded - Anima Theme - 简&繁中文汉化包"),
 "zh.mzmgow.vanillaexpanded.vanomalyeinsanity": ("3346128972", "Vanilla Anomaly Expanded - Insanity - 简&繁中文汉化包"),
 "zh.vanillaexpanded.vnutriente": ("2920693602", "Vanilla Nutrient Paste Expanded - 简&繁中文汉化包"),
 "zh.vanillaexpanded.vchemfuele": ("2793091453", "Vanilla Chemfuel Expanded - 简&繁中文汉化包"),
 "zh.vanillaexpanded.vfepropsanddecor": ("2751195975", "VFEArchitect Addon and Patches - 简&繁中文汉化包"),
 "al9000.shiningarmor": ("3482266407", "Tasty Armory - In Shining Armor"),
 "al9000.tastysteppe": ("3472989392", "Tasty Armory - Steppe Warriors"),
 "al9000.sengoku": ("3494429497", "Tasty Armory - Sengoku"),
 "helperkerx.mocompletecomponent": ("3794419683", "[HPK] Medieval Overhaul - Complete component replacement"),
 "ri.rimimmortal.furniture": ("3478098371", "边缘仙路-雕梁画栋 RimImmortal-Furniture[1.6]"),
 "zh.moreslaverystuff": ("2397228125", "Simple Slavery Collars - 简&繁中文汉化包"),
 "edge.outsourcing": ("3804825440", "边缘外包 | Edge Outsourcing"),
 "vr.missilegirl": ("3712928623", "Missile Girl - Performance Mod"),
 "cc.chinese.rimworld.numbers": ("3437601310", "Numbers 汉化"),
 "cc.chinese.rimworld.researchreinvented": ("3559517604", "Research Reinvented - 简中汉化"),
 "diyshanliu.zh.rimpedia": ("2153216140", "Rimpedia 边缘百科 简繁汉化包"),
 "shavius.vbookse.zh": ("2197732970", "Vanilla Books Expanded 原版书籍扩展 简繁汉化包"),
 "athelas.medievaltotalrim.byzantium": ("3594382864", "Medieval Kingdoms: Byzantine Empire"),
 "athelas.medievaltotalrim.hre": ("3595533821", "Medieval Kingdoms: The Holy Roman Empire（简中汉化条目）"),
 "athelas.medievaltotalrim.turks": ("3589982317", "Medieval Kingdoms: The Turks（简中汉化条目）"),
 "athelas.medievaltotalrim.france": ("3806249061", "Medieval Total Rim: The Kingdom of France"),
 "athelas.medievaltotalrim.iberia": ("3597673469", "Medieval Kingdoms: Iberia"),
 "athelas.medievaltotalrim.mongols": ("3806253198", "Medieval Total Rim: The Mongolian Khaganate"),
 "athelas.medievaltotalrim.poland": ("3806251054", "Medieval Total Rim: The Kingdom of Poland"),
 "athelas.medievaltotalrim.russia": ("3806258934", "Medieval Total Rim: Grand Principality of Muscow"),
 "athelas.medievaltotalrim.events": ("3806263602", "Medieval Total Rim: Quests and Incidents"),
 "laiguai.medievaltotalrim.zh": ("3806242927", "Medieval Total Rim: Core"),
 "lotr.core": ("3657496226", "Legacy of The Rim - Core（疑似 LotR 系列）"),
}

rows = list(csv.DictReader(io.open(UNRES, encoding="utf-8-sig")))
out = []
for r in rows:
    pid = (r.get("packageId") or "").strip()
    k = pid.lower()
    rec = {"packageId": pid, "建议检索词": r.get("建议检索词", ""), "状态": "", "置信": "",
           "工坊ID": "", "候选标题": "", "来源": "", "备选": ""}

    if k.startswith("ludeon.rimworld"):
        rec.update(状态="无需工坊条目", 置信="确定", 候选标题="官方本体 / 官方 DLC",
                   来源="Ludeon 官方发行，非创意工坊 mod")
        out.append(rec); continue

    if k in MAN:
        wid, t = MAN[k]
        rec.update(状态="已定位", 置信="高", 工坊ID=wid, 候选标题=t,
                   来源="工坊定向检索直证")
        out.append(rec); continue

    if k in rmk:
        wid, name, src = rmk[k]
        rec.update(状态="已定位", 置信="高", 工坊ID=wid, 候选标题=name, 来源=src)
        out.append(rec); continue

    z = zhm.get(k)
    c = cand.get(k)
    if z and z.get("top") and z["top"]["score"] >= 88:
        rec.update(状态="已定位", 置信="高", 工坊ID=z["top"]["wid"],
                   候选标题=z["top"]["title"], 来源="汉化包索引匹配(%s)" % z["top"]["why"])
        alts = [a for a in z.get("alts", [])][:2]
        rec["备选"] = " | ".join("%s(%s)" % (a["wid"], a["title"]) for a in alts)
        out.append(rec); continue

    if c and c.get("置信") == "高":
        rec.update(状态="已定位", 置信="高", 工坊ID=c["候选工坊ID"],
                   候选标题=c["候选标题"], 来源="工坊检索(%s)" % c.get("来源", ""), 备选=c.get("备选", ""))
        out.append(rec); continue

    if z and z.get("top"):
        rec.update(状态="待人工确认", 置信="中", 工坊ID=z["top"]["wid"],
                   候选标题=z["top"]["title"], 来源="汉化包索引匹配(%s)" % z["top"]["why"])
        rec["备选"] = " | ".join("%s(%s)" % (a["wid"], a["title"]) for a in z.get("alts", [])[:2])
        out.append(rec); continue

    if c:
        rec.update(状态="待人工确认", 置信=c.get("置信", "低"), 工坊ID=c["候选工坊ID"],
                   候选标题=c["候选标题"], 来源="工坊检索(%s)" % c.get("来源", ""), 备选=c.get("备选", ""))
        out.append(rec); continue

    rec.update(状态="未找到", 置信="无", 来源="四路检索均无匹配")
    out.append(rec)

with io.open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["packageId", "状态", "置信", "工坊ID", "候选标题", "来源", "备选", "建议检索词"])
    w.writeheader(); w.writerows(out)

from collections import Counter
print("总计", len(out))
print(Counter(x["状态"] for x in out))
print(Counter(x["置信"] for x in out))
print("有工坊ID:", sum(1 for x in out if x["工坊ID"]))
