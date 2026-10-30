#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓各商会/社团官网首页，列出导航里所有「名表/董事/理事/联络」类链接。

用于发现像吉打中总 about-kccci-cm.php 那样**带电话栏的名表页**。
"""
import html
import io
import re
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from fetch_text import get

SITES = [
    'https://jaccci.org.my', 'http://ktccc.org', 'https://pccc.org.my',
    'https://pcth.org.my', 'https://kedahccci.org.my', 'https://mrca.org.my',
    'https://www.fmm.org.my', 'https://acccim.org.my', 'https://nsccci.org.my',
    'https://pccci.org.my', 'https://www.cccbp.org.my', 'https://tccci.org.my',
    'https://klscah.org.my', 'https://pcah.org.my', 'https://www.dongzong.my',
    'https://huazong.my', 'https://www.jbccci.org.my', 'https://mccci.org.my',
    'https://www.pahangchamber.org.my', 'https://sabahchinese.org.my',
]

KEY = re.compile(r'名表|名錄|名录|董事|理事|委员会|委員會|执委|執委|组织|組織|'
                 r'committee|board|council|director|contact|联络|聯絡|secretariat', re.I)


def links(base):
    try:
        h = get(base, 25)
    except Exception as e:
        return base, [('ERR', str(e)[:60])]
    out, seen = [], set()
    for m in re.finditer(r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>', h, re.S | re.I):
        href = html.unescape(m.group(1)).strip()
        txt = re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', m.group(2)))).strip()
        if not href or href.startswith(('mailto:', 'tel:', 'javascript:')):
            continue
        u = urllib.parse.urljoin(base + '/', href)
        if urllib.parse.urlparse(u).netloc.replace('www.', '') != \
                urllib.parse.urlparse(base).netloc.replace('www.', ''):
            continue
        if not KEY.search(txt):
            continue
        k = (u, txt)
        if k in seen:
            continue
        seen.add(k)
        out.append((txt[:24], u))
    return base, out


def main():
    allrows = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for base, ls in ex.map(links, SITES):
            print('==', base, len(ls))
            for t, u in ls:
                print('   %-24s %s' % (t, u[:110]))
                allrows.append(dict(site=base, text=t, url=u))
    with io.open('_raw/cc/nav_links.jsonl', 'w', encoding='utf-8') as f:
        for r in allrows:
            f.write(__import__('json').dumps(r, ensure_ascii=False) + '\n')
    print('合计 %d 条' % len(allrows))


if __name__ == '__main__':
    main()
