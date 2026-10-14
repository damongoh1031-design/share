# -*- coding: utf-8 -*-
"""
search-mod.py —— 本地 RimWorld mod 库速查（优先走索引，秒级返回）

★ 回答任何「某 mod 是怎么实现的 / 某 Def 在哪 / 某字段被谁改 / 某类叫什么」，
  先用这个脚本查本地，再考虑联网。

索引模式（快，走 C:\\SteamCMDData\\def-index.json）:
  search-mod.py --def <defName>        精确 defName
  search-mod.py --def-like <片段>       defName 含该片段
  search-mod.py --cls <类名>            精确 C# 类名
  search-mod.py --cls-like <片段>       类名含该片段
  search-mod.py --types [片段]          列出 Def 类型统计（ThingDef / RecipeDef ...）

实时模式（慢，直接扫文件；索引里没有的内容用这个）:
  search-mod.py --grep <关键词> [--cs] [--xml] [--mod <工坊ID>] [--files]

其他:
  search-mod.py --list                  列出全部 mod（工坊ID / 名称 / 源码情况）
  search-mod.py --index-meta            索引构建时间与规模

索引过期（下载了新 mod）→ 重跑 `make-def-index.py`。
"""
import os, re, io, sys, json

C = r"C:\SteamCMDData\steam\steamapps\workshop\content\294100"
IDX = r"C:\SteamCMDData\def-index.json"
SRC_IDX = r"C:\SteamCMDData\source-index.json"

SKIP_DIR = {".git", "obj", "bin", ".vs", "__pycache__", "Textures", "Sounds", "Assemblies",
            "Shaders", "Materials", "UI", "Icons", "Meshes", "Animations", "Fonts"}
MAX_HITS_PER_FILE = 5
MAX_TOTAL = 3000

_IDX_CACHE = None


def idx():
    global _IDX_CACHE
    if _IDX_CACHE is None:
        try:
            _IDX_CACHE = json.load(io.open(IDX, encoding="utf-8"))
        except Exception:
            _IDX_CACHE = {}
    return _IDX_CACHE


def mod_name(wid):
    for depth in ("", "1.6", "1.5", "1.4", "1.3"):
        a = os.path.join(C, wid, depth, "About", "About.xml") if depth else os.path.join(C, wid, "About", "About.xml")
        if os.path.isfile(a):
            try:
                t = io.open(a, encoding="utf-8", errors="ignore").read()
                m = re.search(r"<name>\s*([^<]+?)\s*</name>", t, re.I)
                if m:
                    return m.group(1)
            except OSError:
                pass
    return ""


def group_print(rows, render, header_fmt="    %s"):
    by = {}
    for r in rows:
        by.setdefault(r[0], []).append(r)
    for wid in sorted(by, key=lambda w: -len(by[w])):
        print("### [%s] %s   (%d)" % (wid, mod_name(wid), len(by[wid])))
        for r in by[wid][:30]:
            print(header_fmt % render(r))
        print()


def do_def(key, exact):
    d = idx().get("defs", {})
    if not d:
        print("!! 索引不存在，先跑 make-def-index.py")
        return
    if exact:
        rows = [[w, f, t, key] for w, f, t in d.get(key.lower(), [])]
        key_desc = "defName == %s" % key
    else:
        rows = []
        for k, v in d.items():
            if key.lower() in k:
                rows += [[w, f, t, k] for w, f, t in v]
        key_desc = "defName 含 %s" % key
    print("%s —— 命中 %d 处\n" % (key_desc, len(rows)))
    group_print(rows, lambda r: "%-58s  %-18s  %s" % (r[1], r[2], r[3]))


def do_cls(key, exact):
    d = idx().get("classes", {})
    if not d:
        print("!! 索引不存在，先跑 make-def-index.py")
        return
    if exact:
        rows = d.get(key.lower(), [])
    else:
        rows = []
        for k, v in d.items():
            if key.lower() in k:
                rows += v
    print("类名%s %s —— 命中 %d 处\n" % ("==" if exact else "含", key, len(rows)))
    group_print(rows, lambda r: "%-52s:%-5s %s" % (r[1], r[2], r[3]))


def do_types(frag):
    t = idx().get("types", {})
    items = sorted(t.items(), key=lambda kv: -kv[1])
    if frag:
        items = [x for x in items if frag.lower() in x[0].lower()]
    print("Def 类型统计（共 %d 种）\n" % len(items))
    for k, v in items[:60]:
        print("  %-42s %d 个文件" % (k, v))


def do_index_meta():
    m = idx().get("meta")
    print(json.dumps(m, ensure_ascii=False, indent=1) if m else "索引不存在")


def walk(root, exts):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIR]
        for fn in fns:
            if os.path.splitext(fn)[1].lower() in exts:
                yield os.path.join(dp, fn)


def do_grep(kw, exts, only, files_only):
    roots = []
    for wid in sorted(os.listdir(C)):
        if not os.path.isdir(os.path.join(C, wid)):
            continue
        if only and only not in (wid, mod_name(wid).lower()):
            continue
        roots.append(wid)
    if not roots:
        print("没有匹配的 mod。")
        return
    rx = re.compile(re.escape(kw), re.I)
    by = {}
    total = 0
    for wid in roots:
        for f in walk(os.path.join(C, wid), exts):
            try:
                with io.open(f, encoding="utf-8", errors="ignore") as fh:
                    n = 0
                    for i, line in enumerate(fh, 1):
                        if rx.search(line):
                            n += 1
                            total += 1
                            by.setdefault(wid, []).append([wid, os.path.relpath(f, C), i, line.strip()[:200]])
                            if n >= MAX_HITS_PER_FILE or total > MAX_TOTAL:
                                break
            except OSError:
                continue
    print("实时检索 %r（%d 个 mod，%s）—— 命中 %d 处\n" % (kw, len(roots), ",".join(sorted(exts)), total))
    if files_only:
        for wid in sorted(by):
            print("### [%s] %s" % (wid, mod_name(wid)))
            for r in sorted({x[1] for x in by[wid]}):
                print("    %s" % r)
        return
    group_print([r for v in by.values() for r in v],
                lambda r: "%s:%s  %s" % (r[1], r[2], r[3]))


def do_list():
    si = {}
    try:
        si = json.load(io.open(SRC_IDX, encoding="utf-8"))
    except Exception:
        pass
    for wid in sorted(os.listdir(C)):
        if not os.path.isdir(os.path.join(C, wid)):
            continue
        e = si.get(wid) or {}
        src = "SRC(%s cs)" % e.get("cs_count") if e.get("source_dir") else ""
        print("%-12s %-52s %s" % (wid, mod_name(wid)[:50], src))


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return
    cmd = a[0]
    rest = a[1:]
    if cmd == "--list":
        do_list()
    elif cmd == "--index-meta":
        do_index_meta()
    elif cmd == "--types":
        do_types(rest[0] if rest else "")
    elif cmd == "--def":
        do_def(rest[0], True)
    elif cmd == "--def-like":
        do_def(rest[0], False)
    elif cmd == "--cls":
        do_cls(rest[0], True)
    elif cmd == "--cls-like":
        do_cls(rest[0], False)
    elif cmd == "--grep":
        exts = {".cs", ".xml", ".txt", ".json"}
        only = None
        files_only = False
        kws = []
        i = 0
        while i < len(rest):
            x = rest[i]
            if x == "--cs":
                exts = {".cs"}
            elif x == "--xml":
                exts = {".xml"}
            elif x == "--files":
                files_only = True
            elif x == "--mod":
                i += 1
                only = rest[i] if i < len(rest) else None
            else:
                kws.append(x)
            i += 1
        if not kws:
            print("缺少关键词")
            return
        do_grep(" ".join(kws), exts, only, files_only)
    else:
        print("未知参数 %r，用 --help" % cmd)


if __name__ == "__main__":
    main()
