# -*- coding: utf-8 -*-
"""RimWorld ModsConfig.xml 审计：解析 / 重复 / 依赖 / 加载顺序。

用法：
  1. 改下面 XML 路径（或命令行第一个参数）
  2. 首次运行会自动下载 RimSort 社区工坊数据库（约 49MB）到 DB 路径
  3. python resolve_modlist.py [ModsConfig.xml]
"""
import json
import os
import re
import sys
import urllib.request
from collections import defaultdict

XML = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Admin\Downloads\ce0906.xml"
DB = os.path.join(os.environ.get("TEMP", "/tmp"), "steamDB.json")
DB_URL = "https://raw.githubusercontent.com/RimSort/Steam-Workshop-Database/main/steamDB.json"


def ensure_db():
    if os.path.exists(DB) and os.path.getsize(DB) > 10_000_000:
        return
    print("[*] 下载 RimSort 社区工坊数据库 ...", file=sys.stderr)
    urllib.request.urlretrieve(DB_URL, DB)


def norm(s):
    """归一化模组名：去掉非字母数字，用于跨库模糊匹配。"""
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def main():
    ensure_db()
    d = json.load(open(DB, encoding="utf-8"))["database"]

    # workshopId -> entry, packageId -> [entry...]
    by_wid, by_pid = {}, defaultdict(list)
    for wid, e in d.items():
        if not isinstance(e, dict):
            continue
        by_wid[str(wid)] = e
        pid = e.get("packageId") or e.get("packageid")
        if pid:
            by_pid[str(pid).lower()].append((str(wid), e))

    raw = open(XML, encoding="utf-8").read()
    order, seen = [], set()
    for i in re.findall(r"<li>([^<]+)</li>", raw):
        if i not in seen:            # DLC 会在 knownExpansions 重复登记
            seen.add(i)
            order.append(i)

    def pick(pid):
        """同一 packageId 可能有多条工坊条目（如 CE 的 1.5/1.6），优先 1.6。"""
        lst = by_pid.get(pid.lower())
        if not lst:
            return None
        for wid, e in lst:
            if "1.6" in (e.get("gameVersions") or []):
                return wid, e
        return lst[0]

    ver = re.search(r"<version>([^<]+)</version>", raw)
    print("游戏版本:", ver.group(1) if ver else "?")
    print("启用模组: %d" % len(order))
    print()

    # ---------- 1) 解析 ----------
    print("=" * 78)
    print("1) 解析结果")
    print("=" * 78)
    for pid in order:
        r = pick(pid)
        if r:
            print("  %-46s %-50s %s" % (pid, (r[1].get("name") or "")[:50], r[0]))
        else:
            print("  %-46s %s" % (pid, "-- 社区库未收录 --"))

    # ---------- 2) 同名重复 ----------
    print()
    print("=" * 78)
    print("2) 同名重复")
    print("=" * 78)
    names = defaultdict(list)
    for pid in order:
        r = pick(pid)
        if r and r[1].get("name"):
            names[r[1]["name"].strip().lower()].append((pid, r[1]["name"]))
    hit = {k: v for k, v in names.items() if len(v) > 1}
    if hit:
        for v in hit.values():
            print("  !! %s" % v[0][1])
            for pid, _ in v:
                print("       %s" % pid)
    else:
        print("  （未发现同名重复）")

    # ---------- 3) 依赖缺失（dependencies 存的是工坊ID！） ----------
    print()
    print("=" * 78)
    print("3) 依赖缺失（已把工坊ID 映射回 packageId）")
    print("=" * 78)
    installed = {p.lower() for p in order}
    missing = defaultdict(list)
    for pid in order:
        r = pick(pid)
        if not r:
            continue
        for dep in (r[1].get("dependencies") or []):
            de = by_wid.get(str(dep))
            if de is None:
                missing["工坊ID %s（库中无记录）" % dep].append(pid)
                continue
            dpid = de.get("packageId") or de.get("packageid")
            if dpid and str(dpid).lower() not in installed:
                missing["%s (%s)" % (de.get("name", ""), dpid)].append(pid)
    if missing:
        for k, v in sorted(missing.items(), key=lambda x: -len(x[1])):
            print("  缺 %-56s <- %d 个: %s" % (k, len(v), ", ".join(v[:5])))
        print()
        print("  ⚠️ 注意：社区库 dependencies 混入了 loadAfter（软排序）。")
        print("     软排序目标缺失【无害】，不是报错。只有 About.xml 的 modDependencies 缺失才会报错。")
    else:
        print("  （无）")

    # ---------- 4) 加载顺序逆序 ----------
    print()
    print("=" * 78)
    print("4) 加载顺序逆序（依赖方排在被依赖方之前）")
    print("=" * 78)
    pos = {p.lower(): i for i, p in enumerate(order)}
    bad = []
    for pid in order:
        r = pick(pid)
        if not r:
            continue
        for dep in (r[1].get("dependencies") or []):
            de = by_wid.get(str(dep))
            if not de:
                continue
            dpid = de.get("packageId") or de.get("packageid")
            if dpid and str(dpid).lower() in pos and pos[str(dpid).lower()] > pos[pid.lower()]:
                bad.append((pid, str(dpid), pos[pid.lower()], pos[str(dpid).lower()]))
    if bad:
        for a, b, pa, pb in bad:
            print("  !! %-44s (#%d) 排在其依赖 %-40s (#%d) 之前" % (a, pa, b, pb))
    else:
        print("  （未发现逆序）")

    # ---------- 5) 未解析 ----------
    un = [p for p in order if not pick(p)]
    print()
    print("=" * 78)
    print("5) 社区库未收录（%d 个，绝大多数是汉化包）" % len(un))
    print("=" * 78)
    for p in un:
        print("  ", p)


if __name__ == "__main__":
    main()
