#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段1: 抓取所有栏目列表页，收集文章 URL"""
import re, os, json, time, urllib.request, gzip, io
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://www.mybuddhist.net"
OUT = os.path.join(os.path.dirname(__file__), "urls.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

CATS = {
    "bendihuodong": 388,
    "bendixinwen": 181,
    "bendizhuanfang": 6,
    "haiwaidongtai": 160,
    "localbaodao": 1,
    "zhuantipinglun": 4,
}

def fetch(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip",
                                                       "Referer": BASE + "/cms/shishidongtai/"})
            r = urllib.request.urlopen(req, timeout=40)
            d = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                d = gzip.decompress(d)
            return d.decode("gb18030", "ignore")
        except Exception as e:
            if i == retries - 1:
                return None
            time.sleep(1 + i)
    return None

def page_url(cat, p):
    if p == 1:
        return f"{BASE}/cms/shishidongtai/{cat}/"
    return f"{BASE}/cms/shishidongtai/{cat}/index_{p}.html"

tasks = []
for cat, npages in CATS.items():
    for p in range(1, npages + 1):
        tasks.append((cat, p, page_url(cat, p)))

found = {}   # key "classid_id" -> dict
lock_errors = []
done = 0
t0 = time.time()

def work(t):
    cat, p, url = t
    h = fetch(url)
    if not h:
        return (cat, p, None, [])
    items = []
    # 匹配 <a href="...ShowInfo/?classid=X&id=Y" ...>标题</a>
    for m in re.finditer(r'<a[^>]+href=["\']?(https?://[^"\'>]*?ShowInfo/\?classid=(\d+)&(?:amp;)?id=(\d+))["\']?[^>]*>(.*?)</a>', h, re.S | re.I):
        href, cid, aid, title = m.group(1), m.group(2), m.group(3), m.group(4)
        title = re.sub(r"<[^>]+>", "", title).strip()
        items.append((cid, aid, title))
    # 兼容相对链接
    for m in re.finditer(r'<a[^>]+href=["\']?(/cms/e/action/ShowInfo/\?classid=(\d+)&(?:amp;)?id=(\d+))["\']?[^>]*>(.*?)</a>', h, re.S | re.I):
        href, cid, aid, title = m.group(1), m.group(2), m.group(3), m.group(4)
        title = re.sub(r"<[^>]+>", "", title).strip()
        items.append((cid, aid, title))
    return (cat, p, items, [])

with ThreadPoolExecutor(max_workers=12) as ex:
    futs = {ex.submit(work, t): t for t in tasks}
    for f in as_completed(futs):
        cat, p, items, _ = f.result()
        done += 1
        if items is None:
            lock_errors.append((cat, p))
            continue
        for cid, aid, title in items:
            k = f"{cid}_{aid}"
            if k not in found:
                found[k] = {"classid": cid, "id": aid, "title": title,
                            "url": f"{BASE}/cms/e/action/ShowInfo/?classid={cid}&id={aid}",
                            "from_cat": cat}
        if done % 50 == 0:
            print(f"  {done}/{len(tasks)} pages, {len(found)} articles, {time.time()-t0:.0f}s", flush=True)

print(f"列表页完成: {done}/{len(tasks)}, 失败 {len(lock_errors)}, 文章 {len(found)}")
json.dump({"articles": list(found.values()), "failed_pages": lock_errors},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", OUT)
