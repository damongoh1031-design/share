# -*- coding: utf-8 -*-
"""report.md -> report.html（深色主题 + 侧边导航）
用法: python md2html.py [输入.md] [输出.html]
"""
import re
import sys
from pathlib import Path

import markdown

BASE = Path(__file__).resolve().parent
MD = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "report.md"
HTML = Path(sys.argv[2]) if len(sys.argv) > 2 else MD.with_suffix(".html")
if not MD.is_absolute():
    MD = BASE / MD
if not HTML.is_absolute():
    HTML = BASE / HTML
TITLE = MD.stem

md_text = MD.read_text(encoding="utf-8")
body = markdown.markdown(
    md_text,
    extensions=["tables", "attr_list", "sane_lists", "nl2br"],
)

# 提取所有 h2 / h3 / h4 生成侧边导航
nav = []
for m in re.finditer(r"<h([234])>(.*?)</h\1>", body):
    level, text = int(m.group(1)), m.group(2)
    anchor = re.sub(r"<[^>]+>", "", text).strip()
    slug = re.sub(r"[^\w\s\u4e00-\u9fff-]", "", anchor.lower())
    slug = re.sub(r"\s+", "-", slug)
    nav.append((level, anchor, slug))

nav_html = []
for level, text, slug in nav:
    cls = f"nav-h{level}"
    nav_html.append(f'<a class="{cls}" href="#{slug}">{text}</a>')
nav_html = "\n".join(nav_html)

# 给 h2/h3/h4 加 id
def add_id(m):
    level, text = m.group(1), m.group(2)
    plain = re.sub(r"<[^>]+>", "", text).strip()
    slug = re.sub(r"[^\w\s\u4e00-\u9fff-]", "", plain.lower())
    slug = re.sub(r"\s+", "-", slug)
    return f'<h{level} id="{slug}">{text}</h{level}>'

body = re.sub(r"<h([234])>(.*?)</h\1>", add_id, body)

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>全球邮轮的主要航线 — 深度调研报告</title>
<style>
  :root {{
    --bg: #0f1115; --panel: #161a21; --panel-2: #1c2230; --line: #2a3140;
    --fg: #e6eaf2; --fg-dim: #a3adc2; --accent: #5aa9ff; --accent-2: #7ee0c0;
    --warn: #ffb454;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--bg); color: var(--fg);
    font-family: -apple-system, "Segoe UI", "Microsoft YaHei", "PingFang SC", Roboto, sans-serif;
    font-size: 15px; line-height: 1.75;
  }}
  .wrap {{ display: flex; align-items: flex-start; max-width: 1500px; margin: 0 auto; }}
  aside {{
    position: sticky; top: 0; flex: 0 0 290px; height: 100vh; overflow-y: auto;
    padding: 22px 14px 40px 22px; border-right: 1px solid var(--line);
    background: var(--panel);
  }}
  aside h4 {{ margin: 0 0 12px; font-size: 13px; letter-spacing: .12em; color: var(--fg-dim); text-transform: uppercase; }}
  aside a {{ display: block; padding: 5px 10px; border-radius: 6px; color: var(--fg-dim);
    text-decoration: none; font-size: 13px; line-height: 1.5; }}
  aside a:hover {{ background: var(--panel-2); color: var(--fg); }}
  aside a.nav-h2 {{ color: var(--accent); font-weight: 600; margin-top: 10px; }}
  aside a.nav-h3 {{ padding-left: 18px; }}
  aside a.nav-h4 {{ padding-left: 30px; font-size: 12.5px; opacity: .88; }}
  main {{ flex: 1 1 auto; min-width: 0; padding: 34px 44px 90px; }}
  h1 {{ font-size: 30px; margin: 0 0 10px; letter-spacing: .01em; }}
  h2 {{ font-size: 22px; margin: 46px 0 14px; padding-bottom: 8px; border-bottom: 1px solid var(--line); }}
  h3 {{ font-size: 17px; margin: 30px 0 12px; padding: 9px 14px; border-radius: 8px;
        background: linear-gradient(90deg, var(--panel-2), transparent); border-left: 3px solid var(--accent); }}
  blockquote {{ margin: 14px 0; padding: 10px 16px; border-left: 3px solid var(--accent-2);
    background: var(--panel); color: var(--fg-dim); border-radius: 0 8px 8px 0; font-size: 14px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 14px 0 20px; font-size: 13.5px; }}
  th, td {{ border: 1px solid var(--line); padding: 7px 10px; text-align: left; vertical-align: top; }}
  th {{ background: var(--panel-2); color: var(--fg); font-weight: 600; }}
  tr:nth-child(even) td {{ background: rgba(255,255,255,.017); }}
  a {{ color: var(--accent); }}
  ul {{ margin: 10px 0; padding-left: 22px; }}
  li {{ margin: 4px 0; }}
  li strong {{ color: var(--accent-2); font-weight: 600; }}
  hr {{ border: none; border-top: 1px dashed var(--line); margin: 34px 0; }}
  code {{ background: var(--panel-2); padding: 1px 5px; border-radius: 4px; font-size: 13px; }}
  @media (max-width: 900px) {{ aside {{ display: none; }} main {{ padding: 22px 16px 60px; }} }}
</style>
</head>
<body>
<div class="wrap">
  <aside>
    <h4>目录导航</h4>
    {nav}
  </aside>
  <main>
{body}
  </main>
</div>
</body>
</html>
"""

HTML.write_text(TEMPLATE.format(nav=nav_html, body=body), encoding="utf-8")
print(f"已生成 {HTML}  ({len(body):,} 字符正文)")
