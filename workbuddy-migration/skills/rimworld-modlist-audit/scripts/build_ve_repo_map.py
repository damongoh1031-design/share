# -*- coding: utf-8 -*-
"""从 GitHub 组织拉取全部仓库的 About/About.xml，建立权威 packageId -> 仓库 映射。

为什么不用正则抓 <packageId>：
  About.xml 里 <modDependencies> 也含 <packageId>，正则取第一个会命中依赖 id
  （实测把 VanillaRanchingExpanded 映射成 brrainz.harmony）。必须 XML 解析后取根节点的
  <packageId> 子元素。

用法:
  python build_ve_repo_map.py <org> <out.json>
  python build_ve_repo_map.py Vanilla-Expanded ve_map.json
"""
import json, sys, urllib.request, concurrent.futures as cf
import xml.etree.ElementTree as ET

ORG, OUT = sys.argv[1], sys.argv[2]
UA = {"User-Agent": "Mozilla/5.0"}


def list_repos(org):
    out = []
    for page in (1, 2, 3):
        url = "https://api.github.com/orgs/%s/repos?per_page=100&page=%d" % (org, page)
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
        except Exception:
            break
        if not d:
            break
        out += [(x["name"], x["default_branch"]) for x in d]
    return out


def about(item):
    name, br = item
    for b in (br, "master", "main"):
        for path in ("About/About.xml", "about/About.xml"):
            u = "https://raw.githubusercontent.com/%s/%s/%s/%s" % (ORG, name, b, path)
            try:
                t = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20).read()
            except Exception:
                continue
            try:
                root = ET.fromstring(t.decode("utf-8", "replace").lstrip("\ufeff \t\r\n"))
            except ET.ParseError:
                continue
            pid = (root.findtext("packageId") or "").strip().lower()
            nm = (root.findtext("name") or "").strip()
            return (pid, nm, "%s/%s" % (ORG, name))
    return (None, None, "%s/%s" % (ORG, name))


def main():
    repos = list_repos(ORG)
    res, nomap = {}, []
    with cf.ThreadPoolExecutor(16) as ex:
        for pid, nm, repo in ex.map(about, repos):
            (res.__setitem__(pid, {"repo": repo, "name": nm}) if pid else nomap.append(repo))
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("repos=%d mapped=%d no-about=%d -> %s" % (len(repos), len(res), len(nomap), OUT))
    if nomap:
        print("no About.xml:", nomap)


if __name__ == "__main__":
    main()
