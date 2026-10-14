# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, re, io, json, time, os

OUT = r"C:/SteamCMDData/zh-packs.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"}

def fetch(q, page=1, num=30):
    url = ("https://steamcommunity.com/workshop/browse/?appid=294100"
           "&searchtext=" + urllib.parse.quote(q) +
           "&browsesort=textsearch&section=readytouseitems&numperpage=%d&p=%d" % (num, page))
    req = urllib.request.Request(url, headers=UA)
    h = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")
    out = []
    for m in re.finditer(r'\\"publishedfileid\\":\\"(\d+)\\"(.*?)\\"title\\":\\"(.*?)\\"', h):
        out.append((m.group(1), m.group(3)))
    # 总页数
    tot = re.search(r'(\d+)\s*results match your search', h)
    return out, (int(tot.group(1)) if tot else -1)

TERMS = ["汉化", "简中", "简繁", "汉化包", "汉化补丁", "中文化", "中文", "汉化组", "翻译"]
allitems = {}
for t in TERMS:
    for p in range(1, 21):
        try:
            items, tot = fetch(t, p)
        except Exception as e:
            print("[ERR] %s p%d %s" % (t, p, e)); break
        if p == 1:
            print("[%s] 约 %d 条" % (t, tot))
        if not items: break
        for i, ti in items:
            allitems.setdefault(i, ti)
        if len(items) < 30: break
        time.sleep(0.6)

print("=== 去重后中文包/含中文标题条目: %d ===" % len(allitems))
with io.open(OUT, "w", encoding="utf-8") as f:
    json.dump(allitems, f, ensure_ascii=False, indent=1)
