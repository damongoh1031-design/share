"""从 OCR 缓存筛出「疑似含联系人」的海报，做成可交付的证据包
用法:
  python curate_posters.py --slugmap _raw/slug_map.json --out 海报证据 \
      [--src _raw/fb_out] [--cache _raw/ocr_cache.jsonl] \
      [--csv poster_hits.csv] [--zip 海报证据.zip] [--exclude "伊斯兰|清真|masjid"]

产出:
  海报证据/<机构名>/<序号>_<号码>.jpg   按机构分文件夹，文件名前缀就是识别到的号码
  poster_hits.csv                       一图一行，含号码/邮箱/原图路径/来源页面
  海报证据.zip

判定规则（宁严勿滥，人工复核成本高）:
  - 必须识别出合法马来西亚号码
  - 且满足其一：图上有「联络/报名/洽询/whatsapp」等字样，或号码本身是 01x 手机
  - org_slug 必须在 slugmap 里（= 已进入通讯录的机构），避免把无关页面的图混进来
"""
import os
import re
import json
import csv
import zipfile
import shutil
import argparse

LOOSE = re.compile(r'(?:\+?6?0)\s?\d[\d\s\-\.]{7,14}\d')
MOB = re.compile(r'\+60 1\d-\d{3,4} \d{4}')
KEY = ('联络', '联系', '詢問', '询问', '报名', '報名', '洽询', '洽詢', '電話', '电话',
       '致电', '撥電', '拨电', 'whatsapp', 'whatapps', 'wa.me', 'hubungi', '手机',
       '手提', 'sms', '热线', '熱線', '详情', '詳情', '查询', '查詢', 'contact')
MOB_PREFIX = {'10', '11', '12', '13', '14', '15', '16', '17', '18', '19'}


def norm(d):
    d = re.sub(r'[^\d+]', '', d)
    if d.startswith('+60'):
        e = d
    elif d.startswith('60'):
        e = '+' + d
    elif d.startswith('0'):
        e = '+6' + d
    else:
        return None
    return e if 9 <= len(re.sub(r'\D', '', e)) <= 12 else None


def fmt(e):
    s = re.sub(r'\D', '', e)[2:]
    if s.startswith('1'):
        area, rest = s[:2], s[2:]
    elif s[0] == '8' and len(s) >= 8:
        area, rest = s[:2], s[2:]
    else:
        area, rest = s[0], s[1:]
    body = rest[:4] + ' ' + rest[4:] if len(rest) == 8 else (rest[:3] + ' ' + rest[3:] if len(rest) >= 6 else rest)
    return '+60 %s-%s' % (area, body)


def valid(f):
    s = re.sub(r'\D', '', f)
    if not s.startswith('60'):
        return False
    n = s[2:]
    if n.startswith('1'):
        return len(n) in (9, 10) and n[:2] in MOB_PREFIX
    if n[0] == '3':
        return len(n) == 9
    if n[0] in '45679':
        return len(n) == 8
    if n[:2] in ('82', '83', '84', '85', '86', '87', '88', '89'):
        return len(n) == 8
    return False


def rescrub(t):
    out = []
    for m in LOOSE.findall(t or ''):
        n = norm(m)
        if n:
            f = fmt(n)
            if valid(f) and f not in out:
                out.append(f)
    return out


def rmtree(p):
    """沙箱里 shutil.rmtree 会被重定向到回收站并报 SHFileOperationW 0x2，手动删更稳"""
    if not os.path.isdir(p):
        return
    for root, dirs, files in os.walk(p, topdown=False):
        for f in files:
            os.remove(os.path.join(root, f))
        for d in dirs:
            os.rmdir(os.path.join(root, d))
    os.rmdir(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--slugmap', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--src', default='_raw/fb_out')
    ap.add_argument('--cache', default='_raw/ocr_cache.jsonl')
    ap.add_argument('--csv', default='poster_hits.csv')
    ap.add_argument('--zip', default='')
    ap.add_argument('--exclude', default='')
    a = ap.parse_args()

    sm = json.load(open(a.slugmap, encoding='utf-8'))
    if not sm:
        print('! slugmap 为空')
        return
    EXCL = re.compile(a.exclude, re.I) if a.exclude else None
    if not os.path.exists(a.cache):
        print('! 无 OCR 缓存:', a.cache)
        return

    rmtree(a.out)
    os.makedirs(a.out, exist_ok=True)

    rows = []
    for l in open(a.cache, encoding='utf-8'):
        try:
            d = json.loads(l)
        except Exception:
            continue
        slug = d.get('org_slug') or ''
        if slug not in sm:
            continue
        text = d.get('ocr_text') or ''
        org = sm[slug]
        if EXCL and (EXCL.search(text) or EXCL.search(org)):
            continue
        ph = rescrub(text)
        if not ph:
            continue
        has_key = any(k in text.lower() for k in KEY)
        mob = [p for p in ph if MOB.match(p)]
        if not has_key and not mob:
            continue
        src = os.path.join(a.src, d['file'].replace('\\', os.sep))
        if not os.path.exists(src):
            continue
        sub = os.path.join(a.out, re.sub(r'[\\/:*?"<>|]', '_', org)[:40])
        os.makedirs(sub, exist_ok=True)
        name = '%02d_%s.jpg' % (len(rows) + 1, ph[0].replace(' ', '').replace('+', ''))
        dst = os.path.join(sub, name)
        try:
            shutil.copy2(src, dst)
        except Exception as e:
            print('!', e)
            continue
        rows.append(dict(org=org, slug=slug, phones=' / '.join(ph),
                         mobile=mob[0] if mob else '', emails=d.get('emails') or '',
                         keyword='Y' if has_key else '', file=dst,
                         page='https://www.facebook.com/' + slug))

    cols = ['org', 'slug', 'phones', 'mobile', 'emails', 'keyword', 'file', 'page']
    with open(a.csv, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    zpath = a.zip or (a.out.rstrip('/\\') + '.zip')
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for r in rows:
            z.write(r['file'], os.path.relpath(r['file'], a.out))

    orgs = {r['org'] for r in rows}
    mobs = {r['mobile'] for r in rows if r['mobile']}
    print('海报 %d 张 | 机构 %d 个 | 含手机 %d 个 | %d KB' % (
        len(rows), len(orgs), len(mobs), os.path.getsize(zpath) // 1024))
    print('->', a.csv)
    print('->', zpath)


if __name__ == '__main__':
    main()
