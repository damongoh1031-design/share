# -*- coding: utf-8 -*-
r"""
make-def-index.py —— 为全部本地 RimWorld mod 建立「Def / 类名」索引

产出:
  C:\SteamCMDData\def-index.json
    {
      "meta":  {"built": ..., "mods": n, "xml_files": n, "cs_files": n},
      "defs":  { "<defName小写>": [[工坊ID, 相对路径, Def类型], ...] },
      "types": { "<Def类型>": 数量 },
      "classes": { "<类名>": [[工坊ID, 相对路径, 行号, 片段], ...] }
    }

性能要点：用**二进制读 + 字节预筛**（先 `b"defName" in data` 再解码），
比直接文本读快 3-5 倍；跳过 > 2MB 的文件。
下载新 mod 后重跑本脚本即可。
"""
import os, re, io, json, time, sys

C = r"C:\SteamCMDData\steam\steamapps\workshop\content\294100"
OUT = r"C:\SteamCMDData\def-index.json"

SKIP_DIR = {".git", "obj", "bin", ".vs", "__pycache__", "Textures", "Sounds", "Assemblies",
            "Shaders", "Materials", "UI", "Icons", "Meshes", "Animations", "Fonts",
            "Languages", "Keyed", "DefInjected", "Languages"}
MAX_BYTES = 2 * 1024 * 1024

DEFNAME_RX = re.compile(r"<defName>\s*([^<\s]+)\s*</defName>", re.I)
DEFTYPE_RX = re.compile(r"<([A-Za-z_][A-Za-z0-9_]*Def)\b")
CLASS_RX = re.compile(r"\b(?:class|interface|struct|enum)\s+([A-Za-z_][A-Za-z0-9_]*)")


def walk(root, exts):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIR]
        for fn in fns:
            if os.path.splitext(fn)[1].lower() in exts:
                yield os.path.join(dp, fn)


def read_bytes(f):
    try:
        if os.path.getsize(f) > MAX_BYTES:
            return None
        with open(f, "rb") as fh:
            return fh.read()
    except OSError:
        return None


def main():
    t0 = time.time()
    defs, types, classes = {}, {}, {}
    nx = nc = mods = 0
    if not os.path.isdir(C):
        print("mod 目录不存在: %s" % C)
        return
    wids = [w for w in sorted(os.listdir(C)) if os.path.isdir(os.path.join(C, w))]
    for mi, wid in enumerate(wids, 1):
        p = os.path.join(C, wid)
        mods += 1
        for f in walk(p, {".xml"}):
            data = read_bytes(f)
            if data is None or b"defName" not in data:
                continue
            nx += 1
            t = data.decode("utf-8", "ignore")
            rel = os.path.relpath(f, C)
            m = DEFTYPE_RX.findall(t)
            dt = max(set(m), key=m.count) if m else ""
            if dt:
                types[dt] = types.get(dt, 0) + 1
            for dn in DEFNAME_RX.findall(t):
                defs.setdefault(dn.lower(), []).append([wid, rel, dt])
        for f in walk(p, {".cs"}):
            data = read_bytes(f)
            if data is None:
                continue
            nc += 1
            rel = os.path.relpath(f, C)
            for i, line in enumerate(data.decode("utf-8", "ignore").splitlines(), 1):
                mm = CLASS_RX.search(line)
                if mm:
                    classes.setdefault(mm.group(1).lower(), []).append(
                        [wid, rel, i, line.strip()[:160]])
        if mi % 50 == 0:
            print("[%d/%d] defs=%d classes=%d  %.0fs" % (mi, len(wids), len(defs), len(classes), time.time() - t0), flush=True)

    data = {"meta": {"built": time.strftime("%Y-%m-%d %H:%M:%S"), "mods": mods,
                     "xml_files": nx, "cs_files": nc, "defs": len(defs), "classes": len(classes),
                     "seconds": round(time.time() - t0, 1)},
            "defs": defs, "types": types, "classes": classes}
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False)
    print(json.dumps(data["meta"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
