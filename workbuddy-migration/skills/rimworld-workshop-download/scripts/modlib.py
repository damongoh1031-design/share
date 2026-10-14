# -*- coding: utf-8 -*-
"""共用解析：只取 mod 自身 packageId，剔除依赖声明块。"""
import os, re

DEP_BLOCKS = [
    "modDependencies", "modDependenciesByVersion", "loadAfter", "loadBefore",
    "forceLoadAfter", "forceLoadBefore", "incompatibleWith",
    "modOptionalDependencies", "modOptionalDependenciesByVersion", "modRequirements",
]
DEP_RE = re.compile(r"<(%s)\b[^>]*>.*?</\1>" % "|".join(DEP_BLOCKS), re.S | re.I)
PID_RE = re.compile(r"<packageId>\s*([^<\s]+)\s*</packageId>", re.I)
NAME_RE = re.compile(r"<name>\s*([^<]+?)\s*</name>", re.I)
C = r"C:\SteamCMDData\steam\steamapps\workshop\content\294100"
USER_XMLS = [r"C:\Users\Admin\Downloads\Medieval.xml", r"C:\Users\Admin\Downloads\ce0906.xml"]


def load_user():
    u = {}
    for p in USER_XMLS:
        for m in re.findall(r"<li>([^<]+)</li>", open(p, encoding="utf-8", errors="ignore").read()):
            m = m.strip()
            if m:
                u.setdefault(m.lower(), m)
    return u


def top_abouts(mod_dir):
    base = mod_dir.rstrip("\\/")
    out = []
    for root, dirs, files in os.walk(base):
        rel = os.path.relpath(root, base).replace("\\", "/")
        depth = 0 if rel == "." else rel.count("/") + 1
        if depth > 2:
            dirs[:] = []
            continue
        for f in files:
            if f.lower() == "about.xml":
                out.append(os.path.join(root, f))
    return out


def read_mod(mod_dir):
    """返回 (self_pids, name, size_bytes)。"""
    pids, name, size = set(), "", 0
    for root, dirs, files in os.walk(mod_dir):
        dirs[:] = [x for x in dirs if x.lower() not in
                   ("source", "obj", "bin", "references", ".git", ".vs", "node_modules")]
        for f in files:
            fp = os.path.join(root, f)
            try:
                size += os.path.getsize(fp)
            except Exception:
                pass
    for a in top_abouts(mod_dir):
        t = open(a, encoding="utf-8", errors="ignore").read()
        t2 = DEP_RE.sub("", t)
        m = PID_RE.search(t2)
        if m:
            pids.add(m.group(1).strip())
        if not name:
            nm = NAME_RE.search(t2)
            if nm:
                name = nm.group(1).strip()
    return pids, name, size
