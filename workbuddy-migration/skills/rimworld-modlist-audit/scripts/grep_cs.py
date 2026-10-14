# -*- coding: utf-8 -*-
"""对已映射仓库做定向 C# 取证：forced 事件、改叙述者的 Harmony 补丁、自定义 IncidentWorker。
用法: python grep_cs.py <modlist.xml> <map.json> <out.json>
"""
import io, json, re, sys, tarfile, urllib.request
from collections import defaultdict

MODLIST, MAPJSON, OUTJSON = sys.argv[1], sys.argv[2], sys.argv[3]
UA = {"User-Agent": "Mozilla/5.0"}
PATS = {
    "forced": re.compile(r"\.forced\s*=\s*true"),
    "patch_storyteller": re.compile(r"\[HarmonyPatch[^\]]*Storyteller"),
    "patch_incident": re.compile(r"\[HarmonyPatch[^\]]*Incident"),
    "patch_storytellercomp": re.compile(r"\[HarmonyPatch[^\]]*StorytellerComp"),
    "add_incident_queue": re.compile(r"incidentQueue\.Add"),
    "class_incidentworker": re.compile(r"class\s+(\w+)\s*:\s*IncidentWorker"),
    "class_storytellercomp": re.compile(r"class\s+(\w+)\s*:\s*StorytellerComp\b"),
}


def fetch(repo):
    for br in ("master", "main"):
        try:
            u = "https://codeload.github.com/%s/tar.gz/refs/heads/%s" % (repo, br)
            d = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=300).read()
            if len(d) > 2000:
                return d
        except Exception:
            pass
    return None


def ver_segs(rel):
    return {s for s in rel.split("/") if re.match(r"^\d+\.\d+$", s)}


def main():
    import xml.etree.ElementTree as ET
    root = ET.parse(MODLIST).getroot()
    node = root.find("activeMods")
    pids = [e.text.strip() for e in (node if node is not None else root).iter("li") if e.text]
    raw = json.load(open(MAPJSON, encoding="utf-8"))
    m = {k.lower(): (v["repo"] if isinstance(v, dict) else v) for k, v in raw.items()}
    seen, todo = set(), []
    for p in pids:
        r = m.get(p.lower())
        if r and r not in seen:
            seen.add(r)
            todo.append((p, r))
    out = {}
    for pid, repo in todo:
        d = fetch(repo)
        if d is None:
            print("  !!", pid, repo, flush=True)
            continue
        hits = defaultdict(list)
        with tarfile.open(fileobj=io.BytesIO(d), mode="r:gz") as tf:
            members = [mm for mm in tf.getmembers() if mm.isfile() and mm.name.lower().endswith(".cs")]
            allv = set()
            for mm in members:
                allv |= ver_segs("/".join(mm.name.split("/")[1:]))
            for mm in members:
                rel = "/".join(mm.name.split("/")[1:])
                if "1.6" in allv and ver_segs(rel) and "1.6" not in ver_segs(rel):
                    continue
                f = tf.extractfile(mm)
                if f is None:
                    continue
                txt = f.read().decode("utf-8", "replace")
                for k, pat in PATS.items():
                    for mo in pat.finditer(txt):
                        if k.startswith("class_"):
                            hits[k].append((mo.group(1), rel))
                        else:
                            ln = txt.count("\n", 0, mo.start()) + 1
                            line = txt.splitlines()[ln - 1].strip()[:110]
                            hits[k].append((rel, ln, line))
        out[pid] = {"repo": repo, **{k: v for k, v in hits.items()}}
        nf = len(hits.get("forced", []))
        print("  %-42s forced=%-2d patchSt=%d patchInc=%d queueAdd=%d"
              % (pid, nf, len(hits.get("patch_storyteller", [])),
                 len(hits.get("patch_incident", [])), len(hits.get("add_incident_queue", []))),
              flush=True)
        del d
    json.dump(out, open(OUTJSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("written", OUTJSON)


if __name__ == "__main__":
    main()
