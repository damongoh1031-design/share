#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""中国报雪隆版 · 通过站内搜索 API 全量扫描文章并提取联系人+电话"""
import json, os, re, sys, time, threading, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.environ.get("SITE", "kl")
API = f"https://search.chinapress.com.my/full-search-{SITE}"
OUT = os.path.join(ROOT, f"{SITE}_articles.jsonl")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
PAGE = 10
MAX_FROM = 9990

KEYWORDS = sys.argv[1].split(",") if len(sys.argv) > 1 else [
    "电话", "联络", "联系", "热线", "洽询", "询问", "报名", "详情", "致电", "查询",
    "手机", "传真", "电邮", "秘书处", "报名处", "询问处", "号码", "拨电", "来电",
    "咨询", "谘询", "专线", "联络处", "联络人", "负责人", "WhatsApp", "whatsapp",
]

lock = threading.Lock()
seen_ids = set()
if os.path.exists(OUT):
    for line in open(OUT, encoding="utf-8"):
        try:
            seen_ids.add(json.loads(line)["post_id"])
        except Exception:
            pass

def post(q, frm, retries=3):
    body = json.dumps({"id": "a1", "params": {"query_string": q, "query_from": frm}}).encode()
    for i in range(retries):
        try:
            req = urllib.request.Request(API, data=body, headers={
                "Content-Type": "application/json; charset=utf-8",
                f"Origin": f"https://{SITE}.chinapress.com.my",
                f"Referer": f"https://{SITE}.chinapress.com.my/",
                "User-Agent": UA})
            r = urllib.request.urlopen(req, timeout=30)
            return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == retries - 1:
                return None
            time.sleep(1 + i)
    return None

def total_of(q):
    d = post(q, 0)
    if not d:
        return 0
    return d.get("hits", {}).get("total", {}).get("value", 0)

tasks = []
print("探测各关键词命中量 ...", flush=True)
for q in KEYWORDS:
    t = total_of(q)
    pages = min((t + PAGE - 1) // PAGE, MAX_FROM // PAGE + 1)
    print(f"  {q:<10} total={t:<6} pages={pages}", flush=True)
    for p in range(pages):
        tasks.append((q, p * PAGE))

print(f"总任务 {len(tasks)} 次请求", flush=True)
fout = open(OUT, "a", encoding="utf-8")
cnt = [0, 0, 0]
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
                    fout.write(json.dumps({
                        "post_id": pid,
                        "post_date": s.get("post_date", ""),
                        "post_title": re.sub(r"<[^>]+>", "", s.get("post_title", "")),
                        "post_content": (s.get("post_content") or "")[:6000],
                        "tax_id": s.get("tax_id", ""),
                        "tax": s.get("tax", []),
                    }, ensure_ascii=False) + "\n")
                    cnt[2] += 1
            if cnt[0] % 200 == 0:
                fout.flush()
                el = time.time() - t0
                print(f"  {cnt[0]}/{len(tasks)} 请求, 新文章 {cnt[2]}, 失败 {cnt[1]}, {el:.0f}s", flush=True)

fout.close()
print(f"完成：请求 {cnt[0]}，失败 {cnt[1]}，新文章 {cnt[2]}，累计 {len(seen_ids)}")
