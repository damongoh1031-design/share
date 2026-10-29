"""增量离线 OCR：只处理没跑过的图，结果累积到 JSONL 缓存
用法:
  python ocr_inc.py <图片目录> [--cache _raw/ocr_cache.jsonl] [--max 0]

设计要点:
  - 以 sha1 做去重键：同一张图换个目录/文件名也不会重复跑（跨项目共用缓存）。
  - org_slug 取相对路径的第一段，因此图片必须按 <slug>/<img>.jpg 组织。
  - 全程本地推理（rapidocr-onnxruntime），不联网、不上传。
  - 中文+英文混排识别效果远好于 tesseract，海报上的「联络 012-345 6789」能整段出来。
"""
import os
import re
import sys
import json
import hashlib

IMG = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
PHONE_RE = re.compile(r'(?:\+?60|0)\s?\d{1,2}[\s\-\.]?\d{3,4}[\s\-\.]?\d{3,4}')
MAIL_RE = re.compile(r'[\w\.\-\+]+@[\w\-]+\.[\w\.\-]{2,}')


def sha1(p):
    h = hashlib.sha1()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(65536), b''):
            h.update(c)
    return h.hexdigest()


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


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    root = args[0]
    cache_path = '_raw/ocr_cache.jsonl'
    limit = 0
    for i, a in enumerate(args):
        if a == '--cache' and i + 1 < len(args):
            cache_path = args[i + 1]
        if a == '--max' and i + 1 < len(args):
            limit = int(args[i + 1])

    os.makedirs(os.path.dirname(os.path.abspath(cache_path)), exist_ok=True)
    cache = {}
    if os.path.exists(cache_path):
        for l in open(cache_path, encoding='utf-8'):
            try:
                r = json.loads(l)
                cache[r['sha1']] = r
            except Exception:
                pass

    todo = []
    for dp, _, fs in os.walk(root):
        for fn in sorted(fs):
            if not fn.lower().endswith(IMG):
                continue
            p = os.path.join(dp, fn)
            h = sha1(p)
            if h in cache:
                continue
            todo.append((h, os.path.relpath(p, root), p))
    if limit:
        todo = todo[:limit]
    print('待处理', len(todo), '已缓存', len(cache), flush=True)
    if not todo:
        return

    from rapidocr_onnxruntime import RapidOCR
    eng = RapidOCR()
    out = open(cache_path, 'a', encoding='utf-8')
    for i, (h, rel, p) in enumerate(todo, 1):
        try:
            res, _ = eng(p)
            txt = ' '.join(r[1] for r in res) if res else ''
        except Exception:
            txt = ''
        # OCR 常把「012-345 6789」粘成「0123456789」或「012 3456789」，补一次切分
        txt2 = re.sub(r'(?<=[0-9])(?=[+0])', ' ', txt)
        ph = []
        for m in PHONE_RE.findall(txt2):
            n = norm(m)
            if n:
                f = fmt(n)
                if f not in ph:
                    ph.append(f)
        rec = {
            'sha1': h,
            'file': rel,
            'org_slug': rel.split(os.sep)[0] if os.sep in rel else '',
            'phones': ' / '.join(ph),
            'emails': ' / '.join(dict.fromkeys(MAIL_RE.findall(txt2))),
            'ocr_text': re.sub(r'\s+', ' ', txt)[:2000],
        }
        cache[h] = rec
        out.write(json.dumps(rec, ensure_ascii=False) + '\n')
        if i % 20 == 0:
            out.flush()
            print('  %d/%d' % (i, len(todo)), flush=True)
    out.close()
    hit = sum(1 for r in cache.values() if r['phones'] or r['emails'])
    print('完成 累计 %d 张，其中含号码 %d 张' % (len(cache), hit))


if __name__ == '__main__':
    main()
