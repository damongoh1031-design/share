#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把深度研究报告 markdown 转为自包含的精美 HTML。"""
import html as _html
import pathlib
import re

import markdown
from markdown.extensions.toc import slugify_unicode

SRC = pathlib.Path(r"C:/Users/Admin/WorkBuddy AI/2026-10-12-10-07-33/reports/linux-distro-deep-research-2026-10.md")
OUT = SRC.with_suffix(".html")

text = SRC.read_text(encoding="utf-8")

md = markdown.Markdown(
    extensions=["extra", "toc", "sane_lists"],
    extension_configs={
        "toc": {
            "permalink": False,
            "toc_depth": "1-2",
            # 默认 slugify 会丢弃全部非 ASCII 字符，中文标题会退化成纯数字
            "slugify": slugify_unicode,
        }
    },
)
body = md.convert(text)


def build_toc(tokens, depth=0):
    """从 toc_tokens 递归生成侧边栏目录。"""
    if not tokens:
        return ""
    out = []
    for t in tokens:
        cls = f"toc-l{depth}"
        out.append(
            f'<li class="{cls}"><a href="#{t["id"]}">{_html.escape(t["name"])}</a>'
        )
        if t.get("children"):
            out.append(build_toc(t["children"], depth + 1))
        out.append("</li>")
    return "<ul>" + "".join(out) + "</ul>"


toc_html = build_toc(md.toc_tokens)

# 统计（跳过代码块，避免把 bash 注释当成标题）
def count_headings(src: str):
    in_code = False
    h1 = h2 = 0
    for line in src.split("\n"):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.startswith("# "):
            h1 += 1
        elif line.startswith("## "):
            h2 += 1
    return h1, h2


n_h1, n_h2 = count_headings(text)
n_tbl = 0
in_code = False
for line in text.split("\n"):
    if line.lstrip().startswith("```"):
        in_code = not in_code
        continue
    if not in_code and line.startswith("|") and line.endswith("|"):
        n_tbl += 1

CSS = r"""
:root{
  --bg:#ffffff; --bg-alt:#f7f8fa; --bg-code:#f4f5f7; --bg-side:#fbfbfc;
  --fg:#1a1d21; --fg-2:#4a5058; --fg-3:#7b828b;
  --bd:#e3e6ea; --bd-2:#d0d5db;
  --accent:#1f5fa8; --accent-2:#0f6e56; --accent-warm:#a3520a; --accent-red:#a32d2d;
  --radius:10px;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans SC","PingFang SC","Microsoft YaHei",Roboto,Helvetica,Arial,sans-serif;
}
@media (prefers-color-scheme:dark){
  :root{
    --bg:#15171a; --bg-alt:#1b1e22; --bg-code:#1e2226; --bg-side:#191c20;
    --fg:#e8eaed; --fg-2:#b3b9c0; --fg-3:#868d95;
    --bd:#2c3138; --bd-2:#3a4048;
    --accent:#6fa8e8; --accent-2:#5dcaa5; --accent-warm:#e0a45c; --accent-red:#e08585;
  }
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--bg); color:var(--fg);
  font-family:var(--sans); font-size:16px; line-height:1.78;
  -webkit-font-smoothing:antialiased;
}
.layout{display:flex; align-items:flex-start; max-width:1400px; margin:0 auto}
/* ── 侧边栏 ── */
nav.side{
  position:sticky; top:0; flex:0 0 300px; height:100vh; overflow-y:auto;
  background:var(--bg-side); border-right:1px solid var(--bd);
  padding:28px 20px 60px; font-size:13.5px;
}
nav.side .brand{
  font-size:14px; font-weight:600; color:var(--fg); letter-spacing:.01em;
  margin:0 0 4px; line-height:1.4;
}
nav.side .brand-sub{font-size:12px; color:var(--fg-3); margin:0 0 18px; line-height:1.5}
nav.side ul{list-style:none; margin:0; padding:0}
nav.side li{margin:0}
nav.side a{
  display:block; padding:3.5px 10px; border-radius:6px;
  color:var(--fg-2); text-decoration:none; line-height:1.45;
  border-left:2px solid transparent;
}
nav.side a:hover{background:var(--bg-alt); color:var(--fg)}
.toc-l0 > a{font-weight:600; color:var(--fg); margin-top:9px; font-size:13.5px}
.toc-l1 > a{padding-left:20px; font-size:13px}
/* ── 正文 ── */
main{flex:1 1 auto; min-width:0; padding:56px 60px 140px; max-width:1000px}
main > h1:first-child{
  font-size:30px; line-height:1.3; margin:0 0 8px; font-weight:700; letter-spacing:-.01em;
}
h1{
  font-size:24px; font-weight:650; margin:64px 0 18px; padding-top:26px;
  border-top:2px solid var(--bd); letter-spacing:-.005em; line-height:1.35;
}
h2{font-size:19px; font-weight:620; margin:38px 0 14px; line-height:1.4}
h3{font-size:16.5px; font-weight:600; margin:28px 0 10px; color:var(--fg)}
p{margin:13px 0}
a{color:var(--accent); text-decoration:none}
a:hover{text-decoration:underline}
strong{font-weight:640; color:var(--fg)}
hr{border:0; border-top:1px solid var(--bd); margin:44px 0}
/* ── 表格 ── */
.table-wrap{overflow-x:auto; margin:20px 0; border:1px solid var(--bd); border-radius:var(--radius)}
table{border-collapse:collapse; width:100%; font-size:14px; line-height:1.6}
th,td{padding:9px 13px; text-align:left; border-bottom:1px solid var(--bd); vertical-align:top}
thead th{
  background:var(--bg-alt); font-weight:620; color:var(--fg);
  white-space:nowrap; border-bottom:1.5px solid var(--bd-2); font-size:13.5px;
}
tbody tr:last-child td{border-bottom:0}
tbody tr:nth-child(even){background:var(--bg-alt)}
tbody tr:hover{background:var(--bg-code)}
td code,th code{font-size:12.5px; padding:1px 5px}
/* ── 代码 ── */
code{
  font-family:var(--mono); font-size:13px;
  background:var(--bg-code); padding:2px 6px; border-radius:5px;
  color:var(--accent-2); border:1px solid var(--bd);
}
pre{
  background:var(--bg-code); border:1px solid var(--bd); border-radius:var(--radius);
  padding:16px 18px; overflow-x:auto; margin:18px 0; line-height:1.6;
}
pre code{background:none; border:0; padding:0; font-size:13px; color:var(--fg); display:block}
/* ── 引用块 ── */
blockquote{
  margin:20px 0; padding:12px 20px; background:var(--bg-alt);
  border-left:3px solid var(--accent); border-radius:0 var(--radius) var(--radius) 0;
  color:var(--fg-2);
}
blockquote p{margin:7px 0}
blockquote strong{color:var(--fg)}
/* ── 列表 ── */
ul,ol{padding-left:26px; margin:13px 0}
li{margin:5px 0}
li > ul,li > ol{margin:5px 0}
/* ── 首屏 ── */
.lede{
  background:var(--bg-alt); border:1px solid var(--bd); border-radius:var(--radius);
  padding:4px 22px; margin:24px 0 12px;
}
.lede table{margin:16px 0; font-size:14.5px}
.lede table td:first-child{white-space:nowrap; color:var(--fg-2); font-weight:560; width:130px}
/* ── 页脚 ── */
footer{
  margin-top:70px; padding-top:24px; border-top:1px solid var(--bd);
  font-size:13px; color:var(--fg-3);
}
/* ── 响应式 ── */
@media (max-width:1080px){
  nav.side{display:none}
  main{padding:40px 24px 100px}
}
@media print{
  nav.side{display:none}
  main{padding:0; max-width:none}
  h1{page-break-after:avoid}
  table,pre,blockquote{page-break-inside:avoid}
  body{font-size:11pt}
}
"""

# 给表格套 wrap（便于横向滚动）
body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")

doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Linux 发行版深度研究报告（2026-10）</title>
<meta name="description" content="Arch / NixOS / openSUSE / Fedora / Debian / Ubuntu 十七维深度对比研究报告">
<style>{CSS}</style>
</head>
<body>
<div class="layout">
<nav class="side">
  <p class="brand">Linux 发行版<br>深度研究报告</p>
  <p class="brand-sub">Arch · NixOS · openSUSE<br>Fedora · Debian · Ubuntu<br>2026-10-12</p>
  {toc_html}
</nav>
<main>
{body}
<footer>
  <p><strong>数据截止</strong> 2026-10-12 ｜ <strong>报告版本</strong> 1.0.0 ｜ <strong>章节</strong> {n_h1} 章 / {n_h2} 节 ｜ <strong>表格</strong> {n_tbl} 行</p>
  <p>标记体系：✅ 已核实（官方 API / 源码验证）｜ ◐ 子代理报告 ｜ ⚠️ 二手来源 ｜ ❌ 无公开数据</p>
  <p>本报告基于公开数据整理。Linux 生态变化迅速，关键决策前请以官方最新公告为准。</p>
</footer>
</main>
</div>
</body>
</html>
"""

OUT.write_text(doc, encoding="utf-8")
print(f"OK -> {OUT}")
print(f"   h1={n_h1}  h2={n_h2}  table-rows={n_tbl}  html={len(doc):,} bytes")
