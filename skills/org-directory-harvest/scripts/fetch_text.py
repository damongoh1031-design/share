# -*- coding: utf-8 -*-
"""抓网页并转纯文本（curl 优先，urllib 兜底）。

skill 内多个脚本共用；不依赖第三方库。
"""
import html
import re
import subprocess
import urllib.request

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/131.0 Safari/537.36')


def get(url, timeout=30):
    """返回 HTML 字符串。curl 优先——urllib 走代理常被 Tunnel 502 挡。"""
    try:
        r = subprocess.run(['curl', '-sL', '--max-time', str(timeout),
                            '-A', UA, '-H', 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8', url],
                           capture_output=True, timeout=timeout + 10)
        raw = r.stdout
        if len(raw) > 200:
            for enc in ('utf-8', 'gb18030', 'big5'):
                try:
                    return raw.decode(enc)
                except Exception:
                    continue
    except Exception:
        pass
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    for enc in ('utf-8', 'gb18030', 'big5'):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode('utf-8', 'ignore')


def to_lines(h):
    """HTML → 逐行文本（去 script/style，去空行）"""
    h = re.sub(r'<script.*?</script>', ' ', h, flags=re.S | re.I)
    h = re.sub(r'<style.*?</style>', ' ', h, flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', '\n', h)
    t = html.unescape(t).replace('\xa0', ' ')
    return [re.sub(r'\s+', ' ', x).strip() for x in t.split('\n') if x.strip()]
