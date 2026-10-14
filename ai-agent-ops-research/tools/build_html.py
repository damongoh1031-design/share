# -*- coding: utf-8 -*-
"""通用 MD → 自包含 HTML 渲染器。

用法:
    python build_html.py <src.md> <dst.html> [body_start_marker] [description]

body_start_marker: 正文字符串标记，从此处开始渲染正文（其前的标题/元信息进入 hero 区）。
                   省略时从文档开头渲染。
"""
import html
import os
import re
import sys

import markdown

SRC = sys.argv[1]
DST = sys.argv[2]
MARKER = sys.argv[3] if len(sys.argv) > 3 else None
DESC = (
    sys.argv[4]
    if len(sys.argv) > 4
    else "研究报告 · 自包含 HTML · 证据分级标注 · 全部事实可复现"
)

with open(SRC, "r", encoding="utf-8") as f:
    raw = f.read()

# ── 1. 抽出文档标题与前言元信息块（用于 hero 区） ──────────────────
lines = raw.split("\n")
doc_title = lines[0].lstrip("# ").strip()

meta_lines = []
for ln in lines[1:12]:
    if re.match(r"^\*\*(版本|成稿日期|检索方式|判定口径|方法|覆盖)", ln):
        meta_lines.append(ln)
    if ln.startswith("---"):
        break

# 一行里可能有多个 "**键** 值"，用 " · " 拆开逐对解析
meta_pairs = []
for ln in meta_lines:
    for part in re.split(r"\s+·\s+", ln):
        m = re.match(r"\*\*(.+?)\*\*\s*(.*)", part.strip())
        if m:
            meta_pairs.append((m.group(1), m.group(2).strip()))

# ── 2. Markdown → HTML ────────────────────────────────────────────
if MARKER:
    _cut = raw.find(MARKER)
    body_raw = raw[_cut:] if _cut != -1 else raw
else:
    body_raw = raw
body_raw = re.sub(r"^\s*---\s*$\n?", "", body_raw, count=1, flags=re.M)

try:
    import pygments  # noqa: F401

    code_ext = ["codehilite"]
    code_cfg = {"codehilite": {"guess_lang": False, "css_class": "hl"}}
except Exception:
    code_ext = []  # extra 已含 fenced_code
    code_cfg = {}

# 注意：'extra' 已包含 tables / fenced_code / attr_list / def_list / footnotes /
# abbr / md_in_html，重复注册会抛 ValueError，故此处只补 extra 未含的扩展。
md = markdown.Markdown(
    extensions=["extra", "sane_lists", "toc"] + code_ext,
    extension_configs=dict(
        {"toc": {"toc_depth": "2-3", "permalink": False, "anchorlink": False}},
        **code_cfg,
    ),
)
body = md.convert(body_raw)
toc_html = md.toc

# ── 3. 后处理 ─────────────────────────────────────────────────────
# 3z. 去掉正文里的 H1（标题已在 hero 区展示，避免重复）
body = re.sub(r"^\s*<h1[^>]*>.*?</h1>\s*", "", body, count=1, flags=re.S)

# 3a. 表格包一层，便于横向滚动 + 生成表头 sticky
def wrap_table(m):
    return '<div class="table-wrap">' + m.group(0) + "</div>"


body = re.sub(r"<table>.*?</table>", wrap_table, body, flags=re.S)

# 3b. 标题加锚点
def anchor(m):
    lvl, attrs, inner = m.group(1), m.group(2), m.group(3)
    mid = re.search(r'id="([^"]+)"', attrs)
    if not mid:
        return m.group(0)
    hid = mid.group(1)
    return (
        f'<h{lvl}{attrs}>{inner}'
        f'<a class="anchor" href="#{hid}" aria-label="锚点">#</a></h{lvl}>'
    )


body = re.sub(r"<h([1-6])([^>]*)>(.*?)</h\1>", anchor, body, flags=re.S)

# 3c. 证据等级徽章：把正文中的独立 **A** / **B** / **C** / **D** 转成徽章
body = re.sub(r"<strong>([ABCD])</strong>", r'<span class="badge g-\1">\1</span>', body)

# 3d. 高亮 "⭐" 开头的段落
body = body.replace("⭐", '<span class="star">★</span>')

# 3e. 以 ⚠ 开头的整段转为警示块
body = body.replace("<p>⚠️", '<p class="warnbox">⚠️').replace(
    "<p>⚠", '<p class="warnbox">⚠'
)

# ── 4. HTML 模板 ──────────────────────────────────────────────────
CSS = """
:root{
  --bg:#f7f8fa; --panel:#ffffff; --ink:#1a1d24; --ink-2:#4a5262; --ink-3:#7b8494;
  --line:#e3e6ec; --line-2:#eef1f5;
  --accent:#1f5fd6; --accent-soft:#eaf1fd;
  --code-bg:#f4f6f9; --code-ink:#243040;
  --warn:#b45309; --warn-bg:#fef7e6;
  --danger:#b91c1c; --danger-bg:#fdf0ef;
  --ok:#15803d; --ok-bg:#eef8f1;
  --gA:#15803d; --gB:#1f5fd6; --gC:#b45309; --gD:#7b8494;
  --radius:10px; --maxw:1180px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei","Source Han Sans SC",sans-serif;
  font-size:15.5px; line-height:1.78; -webkit-font-smoothing:antialiased;
  text-rendering:optimizeLegibility;
}
.layout{display:flex; gap:0; max-width:var(--maxw); margin:0 auto; align-items:flex-start}

/* ── 侧栏目录 ── */
.sidebar{
  position:sticky; top:0; flex:0 0 292px; max-height:100vh; overflow-y:auto;
  padding:26px 14px 40px 20px; font-size:13.2px; line-height:1.62;
  border-right:1px solid var(--line);
  scrollbar-width:thin;
}
.sidebar::-webkit-scrollbar{width:6px}
.sidebar::-webkit-scrollbar-thumb{background:#cfd5df; border-radius:3px}
.sidebar .toc-title{
  font-size:11.5px; letter-spacing:.14em; text-transform:uppercase;
  color:var(--ink-3); font-weight:700; margin:0 0 12px 4px;
}
.sidebar ul{list-style:none; margin:0; padding:0}
.sidebar li{margin:1px 0}
.sidebar a{
  display:block; padding:3.5px 8px; border-radius:6px; color:var(--ink-2);
  text-decoration:none; border-left:2px solid transparent; transition:background .12s,color .12s;
}
.sidebar a:hover{background:var(--accent-soft); color:var(--accent)}
.sidebar ul ul{margin-left:0; padding-left:10px}
.sidebar ul ul a{font-size:12.5px; color:var(--ink-3); padding:2.5px 8px}
.sidebar ul ul a:hover{color:var(--accent)}

/* ── 主体 ── */
.main{flex:1 1 auto; min-width:0; padding:0 40px 90px}
.hero{
  padding:52px 0 30px; border-bottom:1px solid var(--line); margin-bottom:34px;
}
.hero h1{
  font-size:31px; line-height:1.32; margin:0 0 18px; letter-spacing:-.4px; font-weight:800;
}
.hero .meta{display:flex; flex-direction:column; gap:7px; font-size:13.5px; color:var(--ink-2)}
.hero .meta .row{display:flex; gap:9px; flex-wrap:wrap; align-items:baseline}
.hero .meta .k{
  flex:0 0 auto; font-weight:700; color:var(--ink-3); font-size:12px;
  letter-spacing:.06em; padding-top:1px;
}
.hero .meta .v{flex:1 1 auto; min-width:0}
.grades{display:flex; gap:8px; flex-wrap:wrap; margin-top:4px}

/* ── 排版 ── */
h2{
  font-size:23px; margin:56px 0 18px; padding:0 0 12px; font-weight:750;
  border-bottom:2px solid var(--ink); letter-spacing:-.2px; scroll-margin-top:16px;
}
h3{
  font-size:18px; margin:36px 0 13px; font-weight:700; color:var(--ink);
  scroll-margin-top:16px;
}
h4{font-size:15.5px; margin:26px 0 10px; font-weight:700; color:var(--ink-2)}
p{margin:0 0 15px}
a{color:var(--accent); text-decoration:none}
a:hover{text-decoration:underline}
.anchor{
  opacity:0; margin-left:9px; font-size:.72em; color:var(--ink-3);
  font-weight:400; text-decoration:none; transition:opacity .12s;
}
h2:hover .anchor,h3:hover .anchor{opacity:1}
hr{border:0; border-top:1px solid var(--line); margin:44px 0}

/* ── 列表 ── */
ul,ol{margin:0 0 16px; padding-left:25px}
li{margin:5px 0}
li>ul,li>ol{margin-top:5px; margin-bottom:6px}

/* ── 引用块 ── */
blockquote{
  margin:20px 0; padding:14px 18px; background:var(--panel);
  border-left:3px solid var(--accent); border-radius:0 var(--radius) var(--radius) 0;
  color:var(--ink-2); font-size:14.6px;
}
blockquote p:last-child{margin-bottom:0}

/* ── 表格 ── */
.table-wrap{
  overflow-x:auto; margin:20px 0 26px; border:1px solid var(--line);
  border-radius:var(--radius); background:var(--panel);
  box-shadow:0 1px 2px rgba(16,24,40,.04);
}
table{border-collapse:collapse; width:100%; font-size:13.9px; min-width:520px}
thead th{
  background:#f0f3f8; text-align:left; font-weight:700; color:var(--ink);
  padding:11px 14px; border-bottom:1.5px solid var(--line); white-space:nowrap;
  font-size:13.2px; letter-spacing:.01em;
}
tbody td{padding:10px 14px; border-bottom:1px solid var(--line-2); vertical-align:top; line-height:1.65}
tbody tr:last-child td{border-bottom:0}
tbody tr:nth-child(even){background:#fbfcfe}
tbody tr:hover{background:var(--accent-soft)}
td code,th code{font-size:12.6px}

/* ── 代码 ── */
code{
  font-family:"SFMono-Regular",Consolas,"Liberation Mono","Cascadia Mono",Menlo,monospace;
  font-size:13.2px; background:var(--code-bg); color:var(--code-ink);
  padding:1.5px 5.5px; border-radius:5px; border:1px solid var(--line-2);
  word-break:break-word;
}
pre{
  background:var(--code-bg); border:1px solid var(--line); border-radius:var(--radius);
  padding:16px 18px; overflow-x:auto; margin:18px 0 24px; line-height:1.62;
}
pre code{
  background:none; border:0; padding:0; font-size:13px; color:var(--code-ink);
  white-space:pre; word-break:normal;
}
pre::-webkit-scrollbar{height:8px}
pre::-webkit-scrollbar-thumb{background:#cfd5df; border-radius:4px}

/* pygments 浅色配色（codehilite） */
.hl .k,.hl .kd,.hl .kn,.hl .kc{color:#a626a4}
.hl .s,.hl .s1,.hl .s2,.hl .sb,.hl .sd{color:#0a7d3e}
.hl .c,.hl .c1,.hl .cm{color:#8a93a3; font-style:italic}
.hl .nf,.hl .fm{color:#1f5fd6}
.hl .nc,.hl .nn{color:#b45309}
.hl .mi,.hl .mf{color:#0b7285}
.hl .nt{color:#1f5fd6}
.hl .o,.hl .ow{color:#4a5262}

/* ── 徽章 ── */
.badge{
  display:inline-block; min-width:19px; text-align:center;
  font-size:11.5px; font-weight:800; line-height:17px; height:18px;
  border-radius:5px; padding:0 5px; vertical-align:1.5px; margin:0 1px;
}
.badge.g-A{background:var(--ok-bg); color:var(--gA); border:1px solid #c9e6d4}
.badge.g-B{background:var(--accent-soft); color:var(--gB); border:1px solid #c9dcf8}
.badge.g-C{background:var(--warn-bg); color:var(--gC); border:1px solid #f2ddb0}
.badge.g-D{background:#f1f3f6; color:var(--gD); border:1px solid #dde1e8}
.star{color:#e0a800; font-size:.95em}

/* 强调块：含"⚠"或"❗"的段落 */
.warnbox{
  background:var(--danger-bg); border:1px solid #f3d0cd; border-left:3px solid var(--danger);
  border-radius:0 var(--radius) var(--radius) 0; padding:13px 17px; margin:20px 0;
}

/* ── 返回顶部 ── */
#top{
  position:fixed; right:26px; bottom:26px; width:42px; height:42px; border-radius:50%;
  background:var(--panel); border:1px solid var(--line); color:var(--ink-2);
  display:flex; align-items:center; justify-content:center; font-size:17px;
  cursor:pointer; box-shadow:0 3px 12px rgba(16,24,40,.13); text-decoration:none;
  opacity:0; pointer-events:none; transition:opacity .2s;
}
#top.show{opacity:1; pointer-events:auto}
#top:hover{background:var(--accent); color:#fff; border-color:var(--accent)}

/* ── 页脚 ── */
.foot{
  margin-top:60px; padding-top:22px; border-top:1px solid var(--line);
  font-size:12.6px; color:var(--ink-3); text-align:center; line-height:1.9;
}

/* ── 移动端 ── */
.mobile-toc{display:none}
@media (max-width:1000px){
  .layout{display:block}
  .sidebar{display:none}
  .main{padding:0 20px 70px}
  .hero{padding:34px 0 24px}
  .hero h1{font-size:24px}
  .mobile-toc{
    display:block; background:var(--panel); border:1px solid var(--line);
    border-radius:var(--radius); padding:10px 14px; margin:0 0 24px; font-size:14px;
  }
  .mobile-toc summary{cursor:pointer; font-weight:700; color:var(--ink-2); outline:none}
  .mobile-toc .toc-inner{padding-top:10px}
  .mobile-toc a{display:block; padding:3px 0; font-size:13.2px; color:var(--ink-2)}
}

/* ── 打印 ── */
@media print{
  body{background:#fff; font-size:10.5pt}
  .sidebar,#top,.mobile-toc{display:none!important}
  .layout{display:block; max-width:none}
  .main{padding:0}
  .hero{padding-top:0}
  h2{page-break-after:avoid; font-size:15pt; margin-top:22pt}
  h3{page-break-after:avoid; font-size:12.5pt}
  .table-wrap,pre,blockquote{page-break-inside:avoid}
  .table-wrap{box-shadow:none}
  a{color:var(--ink)}
  .anchor{display:none}
}
"""

GRADE_LEGEND = (
    '<div class="grades">'
    '<span class="badge g-A">A</span><span class="legend">官方文档原文 / 源码树直读，可复现</span>'
    '<span class="badge g-B">B</span><span class="legend">项目 README / 官方功能页原文</span>'
    '<span class="badge g-C">C</span><span class="legend">项目自述未独立复现</span>'
    '<span class="badge g-D">D</span><span class="legend">本报告推断</span>'
    "</div>"
)

meta_html = []
for k, v in meta_pairs:
    meta_html.append(
        f'<div class="row"><span class="k">{html.escape(k)}</span>'
        f'<span class="v">{html.escape(v)}</span></div>'
    )
meta_html = "\n".join(meta_html)

doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(doc_title)}</title>
<meta name="description" content="{html.escape(DESC)}">
<style>{CSS}</style>
</head>
<body>
<a id="top" href="#" title="返回顶部">↑</a>
<div class="layout">

<nav class="sidebar" aria-label="目录">
  <div class="toc-title">目录</div>
  {toc_html}
</nav>

<main class="main">
  <header class="hero">
    <h1>{html.escape(doc_title)}</h1>
    <div class="meta">
      {meta_html}
      <div class="row"><span class="k">证据分级</span><span class="v">{GRADE_LEGEND}</span></div>
    </div>
  </header>

  <details class="mobile-toc" open>
    <summary>目录</summary>
    <div class="toc-inner">{toc_html}</div>
  </details>

  {body}

  <div class="foot">
    本报告由 WorkBuddy AI 生成 · 六项能力 × 19 个候选 × 官方文档逐条取证 · 成稿 2026-10-12<br>
    所有事实均可通过「附录 B」中的命令复现 · 证据分级见「附录 A」· 未核实项见第 8 章
  </div>
</main>

</div>
<script>
(function(){{
  var t=document.getElementById('top');
  function onScroll(){{ if(window.scrollY>520) t.classList.add('show'); else t.classList.remove('show'); }}
  window.addEventListener('scroll',onScroll,{{passive:true}}); onScroll();
  // 侧栏目录当前章节高亮
  var links=[].slice.call(document.querySelectorAll('.sidebar a[href^="#"]'));
  var map={{}};
  links.forEach(function(a){{ var el=document.getElementById(decodeURIComponent(a.hash.slice(1))); if(el) map[el.id]=a; }});
  var targets=Object.keys(map).map(function(id){{return document.getElementById(id);}});
  if('IntersectionObserver' in window && targets.length){{
    var io=new IntersectionObserver(function(es){{
      es.forEach(function(e){{
        if(e.isIntersecting){{
          links.forEach(function(a){{a.classList.remove('active');}});
          var a=map[e.target.id]; if(a){{a.classList.add('active'); a.style.background='var(--accent-soft)'; a.style.color='var(--accent)';}}
        }}
      }});
    }},{{rootMargin:'-8% 0px -78% 0px'}});
    targets.forEach(function(t){{io.observe(t);}});
  }}
}})();
</script>
</body>
</html>
"""

with open(DST, "w", encoding="utf-8") as f:
    f.write(doc)

print("OK ->", DST)
print("bytes:", os.path.getsize(DST))
print("body html length:", len(body))
