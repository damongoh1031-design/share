#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量探测商会/社团站点的「理事名表」页面。

对 WordPress 站直接走 REST API 列页面，按标题关键词筛选；
非 WP 站退化为常见路径爆破。

输出：_raw/cc/wp_pages.json  {domain: [{id,link,title}]}
"""
import json
import re
import ssl
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/124.0 Safari/537.36'}

SITES = [
    'https://jaccci.org.my',
    'https://www.cccbp.org.my',
    'http://ktccc.org',
    'https://pccci.org.my',
    'https://nsccci.org.my',
    'https://pccc.org.my',
    'https://www.dongzong.my',
    'https://klscah.org.my',
    'https://pcth.org.my',
    'https://pcah.org.my',
    'https://tccci.org.my',
    'https://kedahccci.org.my',
    'https://acccim.org.my',
    'https://mrca.org.my',
    'https://www.fmm.org.my',
    'https://rehda.com',
    'https://www.mca.org.my',
]

KEY = re.compile(r'理事|董事|委员会|名表|委员|会长|领导|组织|执委|committee|board|council|'
                 r'leadership|organization|director|office.?bearer|exco', re.I)


def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read().decode('utf-8', 'ignore')


def probe(base):
    out = []
    for route in ('/index.php?rest_route=/wp/v2/pages&per_page=100&_fields=id,link,title',
                  '/?rest_route=/wp/v2/pages&per_page=100&_fields=id,link,title',
                  '/wp-json/wp/v2/pages?per_page=100&_fields=id,link,title'):
        try:
            txt = get(base + route)
            data = json.loads(txt)
            if not isinstance(data, list):
                continue
            for p in data:
                t = re.sub(r'<[^>]+>', '', (p.get('title') or {}).get('rendered', ''))
                t = re.sub(r'&[a-z]+;', ' ', t).strip()
                out.append(dict(id=p.get('id'), link=p.get('link'), title=t))
            if out:
                break
        except Exception:
            continue
    return base, out


def main():
    res = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        for base, pages in ex.map(probe, SITES):
            res[base] = pages
            hits = [p for p in pages if KEY.search(p['title'] or '')]
            print('%-34s pages=%-4d hits=%d' % (base, len(pages), len(hits)))
            for p in hits:
                print('     %-30s %s' % (p['title'][:30], p['link']))
    with open('_raw/cc/wp_pages.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
