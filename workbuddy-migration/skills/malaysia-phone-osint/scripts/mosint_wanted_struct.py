#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析 PDRM 通缉页结构，找真实条目特征（当前实现命中大量导航文字）"""
import re

import requests
import urllib3

urllib3.disable_warnings()
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
URL = "https://www.rmp.gov.my/orang-dikehendaki"

r = requests.get(URL, headers={"User-Agent": UA, "Accept": "*/*"},
                 timeout=35, verify=False)
html = r.text
print(f"HTTP {r.status_code}  len={len(html)}")

print()
print("=" * 78)
print("1) 'TAN' 出现在哪些上下文（前 12 处）")
print("=" * 78)
for i, m in enumerate(re.finditer(r"TAN", html, re.I)):
    if i >= 12:
        break
    seg = re.sub(r"\s+", " ", html[max(0, m.start() - 60):m.start() + 60])
    print(f"  [{i+1}] …{seg}…")

print()
print("=" * 78)
print("2) 是否有详情页链接（通缉人员条目）")
print("=" * 78)
links = re.findall(r'href="([^"]*orang-dikehendaki[^"]*)"', html, re.I)
print(f"  找到 {len(links)} 个相关链接")
for l in sorted(set(links))[:15]:
    print(f"     {l}")

print()
print("=" * 78)
print("3) 页面主要区块（找列表容器）")
print("=" * 78)
for pat in [r'<table[^>]*>', r'class="[^"]*(?:list|grid|card|item)[^"]*"',
            r'id="[^"]*(?:list|grid|content)[^"]*"']:
    found = re.findall(pat, html, re.I)
    print(f"  {pat[:40]:<42} -> {len(found)} 个")
    for f in sorted(set(found))[:5]:
        print(f"       {f[:110]}")

print()
print("=" * 78)
print("4) 文本化后 'TAN' 的上下文（判断是否导航）")
print("=" * 78)
txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
for i, m in enumerate(re.finditer(r"\bTAN\b", txt, re.I)):
    if i >= 10:
        break
    print(f"  [{i+1}] …{txt[max(0, m.start()-70):m.start()+70]}…")
