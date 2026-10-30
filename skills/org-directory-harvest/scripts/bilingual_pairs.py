#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽取中总（ACCCIM）的中英双语人员对照表。

中总为每位理事/名誉会长/历届会长建了两套页面：
  英文站 https://acccim.org.my/en/pic-member/<slug>/
  中文站 https://acccim.org.my/pic-member/<中文名>/
两套列表顺序一致，按序号配对即得「英文名 ↔ 中文名」。

输出：_raw/cc/bilingual.jsonl
"""
import html
import io
import json
import re

from fetch_text import get

TYPES = ['pic-member', 'honorary-president', 'past-presidents']


def lst(base, t):
    try:
        return json.loads(get('%s/wp-json/wp/v2/%s?per_page=100&_fields=id,link,title' % (base, t)))
    except Exception as e:
        print('  ERR', base, t, e)
        return []


def title(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', '', x['title']['rendered']))).strip()


HONOR = re.compile(r'^(拿督斯里|拿督威拉|拿督巴杜卡|拿督|丹斯里|敦|准拿督|皇室|已故|甲必丹|太平局绅)+')
SUF = re.compile(r'(先生|女士|小姐|局绅|博士|硕士|教授|医生|医师|律师|爵士|太平绅士|上议员)$')


def cn_parts(s):
    p = re.sub(r'\s+', '', s)
    hon = ''
    for _ in range(3):
        m = HONOR.match(p)
        if not m:
            break
        hon = (hon + ' ' + m.group(1)).strip()
        p = p[m.end():]
    p = SUF.sub('', p)
    return hon, p


def main():
    rows = []
    for t in TYPES:
        en = lst('https://acccim.org.my/en', t)
        zh = lst('https://acccim.org.my', t)
        print('%-20s en=%d zh=%d' % (t, len(en), len(zh)))
        for a, b in zip(en, zh):
            name_en = title(a)
            name_cn_raw = title(b)
            hon, nm = cn_parts(name_cn_raw)
            rows.append(dict(
                org='马来西亚中华总商会 ACCCIM', kind=t,
                name_en=name_en, name_cn=nm, honor=hon,
                name_cn_raw=name_cn_raw,
                url_en=a['link'], url_cn=b['link']))
    with io.open('_raw/cc/bilingual.jsonl', 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('合计 %d 条' % len(rows))
    for r in rows[:8]:
        print('  %-42s %-10s %s' % (r['name_en'][:42], r['honor'] + r['name_cn'], r['kind']))


if __name__ == '__main__':
    main()
