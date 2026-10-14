# -*- coding: utf-8 -*-
"""真实口径校验：只取 mod 自身的 packageId（剔除依赖声明块）。

关键：About.xml 里 <modDependencies> / <modDependenciesByVersion> / <loadAfter>
等块内也含 <packageId>，那是依赖，不是本 mod 的 ID。必须先剥离再取。
"""
import os, re, io, sys, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
C = r"C:\SteamCMDData\steam\steamapps\workshop\content\294100"
USER_XMLS = [r"C:\Users\Admin\Downloads\Medieval.xml", r"C:\Users\Admin\Downloads\ce0906.xml"]

DEP_BLOCKS = [
    "modDependencies", "modDependenciesByVersion", "loadAfter", "loadBefore",
    "forceLoadAfter", "forceLoadBefore", "incompatibleWith",
    "modOptionalDependencies", "modOptionalDependenciesByVersion",
    "modRequirements",
]
DEP_RE = re.compile(
    r"<(%s)\b[^>]*>.*?</\1>" % "|".join(DEP_BLOCKS), re.S | re.I)
PID_RE = re.compile(r"<packageId>\s*([^<\s]+)\s*</packageId>", re.I)


def self_pid(about_path):
    t = open(about_path, encoding="utf-8", errors="ignore").read()
    t = DEP_RE.sub("", t)                       # 剥离依赖声明块
    m = PID_RE.search(t)
    return m.group(1).strip() if m else None


def top_abouts(mod_dir):
    """<mod>/About/About.xml 或 <mod>/<ver>/About/About.xml（深度 <= 2）。"""
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


user = {}
for p in USER_XMLS:
    for m in re.findall(r"<li>([^<]+)</li>", open(p, encoding="utf-8", errors="ignore").read()):
        m = m.strip()
        if m:
            user.setdefault(m.lower(), m)

matched = {}
unmatched_folders = []
for d in sorted(os.listdir(C)):
    p = os.path.join(C, d)
    if not os.path.isdir(p):
        continue
    pids = {x for x in (self_pid(a) for a in top_abouts(p)) if x}
    hit = {x.lower() for x in pids} & set(user)
    if hit:
        for h in hit:
            matched.setdefault(h, d)
    else:
        unmatched_folders.append((d, sorted(pids)))

miss = sorted(user[k] for k in user if k not in matched)
res = {
    "folders": len(os.listdir(C)),
    "user_total": len(user),
    "matched": len(matched),
    "missing_count": len(miss),
    "missing": miss,
    "folders_not_in_user_list": unmatched_folders,
}
json.dump(res, open(r"C:\SteamCMDData\true-verify.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("真实口径（剔除依赖块）")
print("  下载文件夹:", res["folders"])
print("  用户 packageId:", len(user))
print("  命中:", len(matched), "(%d%%)" % (len(matched) * 100 // len(user)))
print("  未命中:", len(miss))
print("  下载了但不在用户清单:", len(unmatched_folders))
for d, p in unmatched_folders[:15]:
    print("    ", d, p)
