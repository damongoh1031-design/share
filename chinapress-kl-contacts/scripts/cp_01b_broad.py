#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""中国报雪隆版 · 第二轮广度扫描（高频字 + 活动类关键词），只保留含疑似电话的文章"""
import json, os, re, sys, time, threading, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
API = "https://search.chinapress.com.my/full-search-kl"
OUT = os.path.join(ROOT, "cp_articles.jsonl")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
PAGE = 10
MAX_FROM = 9990

PHONE_PRE = re.compile(
    r"(?<![\d/.\-])(?:\+?60[\s\-]?|0)(?:1[0-9]|[2-9])(?:[\s\-]?\d{3,4}){1,2}[\s\-]?\d{3,4}(?![\d])")

KEYWORDS = sys.argv[1].split(",")
MAX_PAGES = int(sys.argv[2]) if len(sys.argv) > 2 else 1000

lock = threading.Lock()
seen_ids = set()
if os.path.exists(OUT):
    for line in open(OUT, encoding="utf-8"):
        try:
            seen_ids.add(json.loads(line)["post_id"])
        except Exception:
            pass
print(f"已有 {len(seen_ids)} 篇", flush=True)

def post(q, frm, retries=3):
    body = json.dumps({"id": "a1", "params": {"query_string": q, "query_from": frm}}).encode()
    for i in range(retries):
        try:
            req = urllib.request.Request(API, data=body, headers={
                "Content-Type": "application/json; charset=utf-8",
                "Origin": "https://kl.chinapress.com.my",
                "Referer": "https://kl.chinapress.com.my/",
                "User-Agent": UA})
            r = urllib.request.urlopen(req, timeout=30)
            return json.loads(r.read().decode("utf-8"))
        except Exception:
            if i == retries - 1:
                return None
            time.sleep(1 + i)
    return None

tasks = []
for q in KEYWORDS:
    d = post(q, 0)
    t = d.get("hits", {}).get("total", {}).get("value", 0) if d else 0
    pages = min((t + PAGE - 1) // PAGE, MAX_PAGES, MAX_FROM // PAGE + 1)
    print(f"  {q:<8} total={t:<6} pages={pages}", flush=True)
    for p in range(pages):
        tasks.append((q, p * PAGE))

print(f"任务 {len(tasks)} 次请求", flush=True)
fout = open(OUT, "a", encoding="utf-8")
cnt = [0, 0, 0, 0]
t0 = time.time()

def work(t):
    q, frm = t
    d = post(q, frm)
    if not d:
        return None
    return d.get("hits", {}).get("hits", [])

with ThreadPoolExecutor(max_workers=24) as ex:
    futs = [ex.submit(work, t) for t in tasks]
    for f in as_completed(futs):
        hits = f.result()
        with lock:
            cnt[0] += 1
            if hits is None:
                cnt[1] += 1
            else:
                for h in hits:
                    s = h.get("_source", {})
                    pid = s.get("post_id")
                    if not pid or pid in seen_ids:
                        continue
                    seen_ids.add(pid)
                    cnt[3] += 1
                    content = s.get("post_content", "") or ""
                    if not PHONE_PRE.search(content):
                        continue
                    fout.write(json.dumps({
                        "post_id": pid,
                        "post_date": s.get("post_date", ""),
                        "post_title": re.sub(r"<[^>]+>", "", s.get("post_title", "")),
                        "post_content": content[:6000],
                        "tax": s.get("tax", []),
                    }, ensure_ascii=False) + "\n")
                    cnt[2] += 1
            if cnt[0] % 500 == 0:
                fout.flush()
                el = time.time() - t0
                print(f"  {cnt[0]}/{len(tasks)} 请求, 新看到 {cnt[3]}, 含电话保存 {cnt[2]}, 失败 {cnt[1]}, {el:.0f}s", flush=True)

fout.close()
print(f"完成：请求 {cnt[0]}，失败 {cnt[1]}，新看到 {cnt[3]}，含电话保存 {cnt[2]}")
