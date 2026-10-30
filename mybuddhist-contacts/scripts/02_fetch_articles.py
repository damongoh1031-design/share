#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段2: 并发抓取全部文章页，抽取正文，写 articles.jsonl"""
import re, os, json, time, gzip, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
BASE = "https://www.mybuddhist.net"

urls = json.load(open(os.path.join(HERE, "urls.json"), encoding="utf-8"))["articles"]
OUT = os.path.join(ROOT, "articles.jsonl")

done_set = set()
if os.path.exists(OUT):
    for line in open(OUT, encoding="utf-8"):
        try:
            done_set.add(json.loads(line)["url"])
        except Exception:
            pass
todo = [a for a in urls if a["url"] not in done_set]
print(f"total={len(urls)} done={len(done_set)} todo={len(todo)}", flush=True)

lock = threading.Lock()
fout = open(OUT, "a", encoding="utf-8")
cnt = [0, 0]
t0 = time.time()

def fetch(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip",
                                                       "Referer": BASE + "/cms/shishidongtai/"})
            r = urllib.request.urlopen(req, timeout=45)
            d = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                d = gzip.decompress(d)
            return d.decode("gb18030", "ignore")
        except Exception:
            if i == retries - 1:
                return None
            time.sleep(0.8 * (i + 1))
    return None

def clean(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</(p|div|tr|td|li|h\d)>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = (s.replace("&nbsp;", " ").replace("&ldquo;", "“").replace("&rdquo;", "”")
          .replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
          .replace("&hellip;", "…").replace("&mdash;", "—"))
    s = re.sub(r"[ \t\u3000]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()

def parse(h, meta):
    title = ""
    m = re.search(r"<title>(.*?)</title>", h, re.S | re.I)
    if m:
        title = clean(m.group(1)).replace(" - 马来西亚佛教资讯网", "").strip()
    date = ""
    m = re.search(r"发布时间[：:]\s*([\d\-/\.]{6,12})", h)
    if not m:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", h)
    if m:
        date = m.group(1)
    source = ""
    m = re.search(r"来源[：:]\s*([^<\n]{1,60})", h)
    if m:
        source = clean(m.group(1)).strip()

    # 正文：最后一个"点击："之后 到 "【 加入收藏夹 】"
    end_m = re.search(r"【\s*加入收藏夹\s*】", h)
    end = end_m.start() if end_m else len(h)
    starts = [mm.end() for mm in re.finditer(r"点\s*击[：:]", h) if mm.end() < end]
    if starts:
        start = starts[-1]
    else:
        bm = list(re.finditer(r"时势动态\s*</a>", h))
        start = bm[-1].end() if bm else 0
        if start >= end:
            start = 0
    body = clean(h[start:end])
    # 去掉正文开头的重复标题/面包屑残渣
    return {"url": meta["url"], "classid": meta["classid"], "id": meta["id"],
            "title": title or meta["title"], "date": date, "source": source,
            "from_cat": meta["from_cat"], "body": body}

def work(meta):
    h = fetch(meta["url"])
    if not h:
        return None
    try:
        return parse(h, meta)
    except Exception:
        return None

with ThreadPoolExecutor(max_workers=40) as ex:
    futs = {ex.submit(work, a): a for a in todo}
    for f in as_completed(futs):
        r = f.result()
        with lock:
            cnt[0] += 1
            if r is None:
                cnt[1] += 1
            else:
                fout.write(json.dumps(r, ensure_ascii=False) + "\n")
            if cnt[0] % 500 == 0:
                fout.flush()
                el = time.time() - t0
                print(f"  {cnt[0]}/{len(todo)} fail={cnt[1]} {el:.0f}s eta={el/cnt[0]*(len(todo)-cnt[0]):.0f}s", flush=True)

fout.close()
print(f"完成 {cnt[0]}, 失败 {cnt[1]}")
