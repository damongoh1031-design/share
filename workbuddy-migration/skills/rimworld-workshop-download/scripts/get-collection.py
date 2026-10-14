# -*- coding: utf-8 -*-
import urllib.request, re, io, json, sys, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"}

def get_collection(cid):
    url = "https://steamcommunity.com/sharedfiles/filedetails/?id=%s" % cid
    req = urllib.request.Request(url, headers=UA)
    h = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")
    # 合集子项：<div class="collectionItemDetails"><a href="...id=XXX">TITLE</a>
    items = []
    for m in re.finditer(r'class="collectionItemDetails".*?<a href="[^"]*id=(\d+)"[^>]*>(.*?)</a>', h, re.S):
        title = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        items.append((m.group(1), title))
    return items, len(h)

if __name__ == "__main__":
    cids = sys.argv[1:] or ["1781246546", "2063188240", "704181221", "1718190143"]
    allit = {}
    for c in cids:
        try:
            it, n = get_collection(c)
            print("[%s] %d 项 (html %d)" % (c, len(it), n))
            for i, t in it:
                allit.setdefault(i, t)
        except Exception as e:
            print("[%s] ERR %s" % (c, e))
        time.sleep(1)
    print("=== 合计去重 %d ===" % len(allit))
    with io.open(r"C:/SteamCMDData/zh-collections.json", "w", encoding="utf-8") as f:
        json.dump(allit, f, ensure_ascii=False, indent=1)
    for i, t in list(allit.items())[:20]:
        print("   %s  %s" % (i, t))
