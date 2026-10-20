#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 docs/PRD.md 编译成可打印的 docs/prd.html（含封面、目录、A4 分页）。
只支持 PRD.md 里实际用到的语法：标题 / 表格 / 代码块 / 列表 / 引用 / 分隔线 / 行内强调。
"""
import re
import sys
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "PRD.md"
OUT = ROOT / "docs" / "prd.html"
PROTO = ROOT / "prototype" / "crm-prototype.html"


def extract_logo() -> str:
    try:
        s = PROTO.read_text(encoding="utf-8")
        m = re.search(r"const LOGO = '(data:image/png;base64,[^']+)'", s)
        return m.group(1) if m else ""
    except Exception:
        return ""


def inline(text: str) -> str:
    """行内：代码 > 粗体 > 链接。先转义再替换，避免注入。"""
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 2:
            out.append("<code>" + html.escape(p[1:-1]) + "</code>")
        else:
            e = html.escape(p)
            e = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", e)
            e = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', e)
            out.append(e)
    return "".join(out)


def slug(text: str, used: dict) -> str:
    base = re.sub(r"[^\w\u4e00-\u9fff]+", "-", text).strip("-").lower()[:40] or "sec"
    used[base] = used.get(base, 0) + 1
    return base if used[base] == 1 else f"{base}-{used[base]}"


def parse(md: str):
    lines = md.split("\n")
    i, n = 0, len(lines)
    blocks, toc = [], []
    used = {}
    in_code = False
    code_buf = []

    while i < n:
        line = lines[i]

        if line.strip().startswith("```"):
            if in_code:
                blocks.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
                code_buf, in_code = [], False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # 标题
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            level, text = len(m.group(1)), m.group(2).strip()
            sid = slug(text, used)
            if level == 1:
                blocks.append(f'<h1 id="{sid}">{inline(text)}</h1>')
            elif level == 2:
                toc.append((2, text, sid))
                blocks.append(f'<h2 id="{sid}">{inline(text)}</h2>')
            elif level == 3:
                toc.append((3, text, sid))
                blocks.append(f'<h3 id="{sid}">{inline(text)}</h3>')
            else:
                blocks.append(f'<h4 id="{sid}">{inline(text)}</h4>')
            i += 1
            continue

        # 分隔线
        if re.match(r"^-{3,}\s*$", line):
            blocks.append('<hr class="rule">')
            i += 1
            continue

        # 表格
        if line.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ['<table><thead><tr>']
            t += [f"<th>{inline(h)}</th>" for h in header]
            t.append("</tr></thead><tbody>")
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table>")
            blocks.append("".join(t))
            continue

        # 引用
        if line.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ").rstrip())
                i += 1
            blocks.append("<blockquote>" + inline(" ".join(buf)) + "</blockquote>")
            continue

        # 列表
        if re.match(r"^\s*([-*]|\d+\.)\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.\s+", line))
            items = []
            while i < n and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                raw = re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i]).rstrip()
                check = re.match(r"^\[( |x)\]\s+(.*)$", raw)
                if check:
                    box = "☑" if check.group(1) == "x" else "☐"
                    items.append(f'<li class="check">{box} {inline(check.group(2))}</li>')
                else:
                    items.append(f"<li>{inline(raw)}</li>")
                i += 1
            tag = "ol" if ordered else "ul"
            blocks.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue

        # 空行
        if not line.strip():
            i += 1
            continue

        # 段落
        buf = []
        while i < n and lines[i].strip() and not re.match(r"^(#{1,4}\s|\||>|```|-{3,}\s*$)", lines[i]) \
                and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
            buf.append(lines[i].strip())
            i += 1
        blocks.append("<p>" + inline(" ".join(buf)) + "</p>")

    return blocks, toc


CSS = """
:root{--brand:#e8622a;--ink:#1f2d3d;--ink2:#5f6f85;--ink3:#93a0b3;--line:#e3e8f0;--bg:#f2f4f7}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:14px/1.75 "Microsoft YaHei","PingFang SC",system-ui,sans-serif}
.page{max-width:940px;margin:0 auto;background:#fff;padding:48px 56px 80px;
  box-shadow:0 2px 20px rgba(16,32,56,.08)}
/* 封面 */
.cover{min-height:92vh;display:flex;flex-direction:column;justify-content:center;
  padding:0 8px 60px;page-break-after:always}
.cover .logo{width:72px;height:72px;border-radius:16px;background:#fff;padding:4px;
  box-shadow:0 2px 10px rgba(16,32,56,.14),0 0 0 1px rgba(16,32,56,.06)}
.cover .brand{display:flex;align-items:center;gap:14px;margin-bottom:36px}
.cover .brand b{font-size:18px;letter-spacing:.5px}
.cover .brand span{display:block;font-size:12px;color:var(--ink3);margin-top:2px}
.cover h1{font-size:38px;line-height:1.25;margin:0 0 10px;letter-spacing:1px;border:none;padding:0}
.cover .sub{font-size:15px;color:var(--ink2);margin-bottom:40px}
.cover .meta{display:grid;grid-template-columns:96px 1fr;gap:8px 16px;font-size:13px;
  border-top:2px solid var(--brand);padding-top:20px;max-width:620px}
.cover .meta b{color:var(--ink3);font-weight:400}
.cover .foot{margin-top:auto;font-size:11.5px;color:var(--ink3);padding-top:40px}
/* 目录 */
.toc{page-break-after:always;padding-bottom:40px}
.toc h2{border:none;padding:0;margin:0 0 18px;font-size:20px}
.toc ol{list-style:none;margin:0;padding:0;counter-reset:t}
.toc li{margin:0;padding:5px 0;border-bottom:1px dotted var(--line);font-size:13.5px}
.toc li.lv3{padding-left:26px;font-size:12.5px;color:var(--ink2);border-bottom:none}
.toc a{color:inherit;text-decoration:none}
.toc .num{display:inline-block;min-width:44px;color:var(--brand);font-weight:600}
.toc li.lv3 .num{min-width:34px;font-weight:400;color:var(--ink3)}
/* 正文 */
h1{font-size:24px;margin:44px 0 14px;padding-bottom:10px;border-bottom:2px solid var(--brand);
  page-break-after:avoid;page-break-before:always}
h1:first-of-type{page-break-before:auto}
h2{font-size:17px;margin:30px 0 10px;page-break-after:avoid}
h3{font-size:14.5px;margin:22px 0 8px;color:#2b3a4d;page-break-after:avoid}
h4{font-size:13.5px;margin:16px 0 6px;color:var(--ink2)}
p{margin:8px 0}
strong{font-weight:600}
code{font-family:Consolas,Menlo,monospace;font-size:12px;background:#f4f6f9;
  border:1px solid var(--line);border-radius:4px;padding:1px 5px;color:#b4451f}
pre{background:#f7f9fc;border:1px solid var(--line);border-radius:8px;padding:14px 16px;
  overflow:auto;page-break-inside:avoid}
pre code{background:none;border:none;padding:0;color:#2b3a4d;font-size:12px;line-height:1.6}
table{width:100%;border-collapse:collapse;margin:12px 0 18px;font-size:12.5px;
  page-break-inside:auto}
th{background:#f7f9fc;text-align:left;font-weight:600;color:#33455c;padding:8px 10px;
  border:1px solid var(--line);white-space:nowrap}
td{padding:7px 10px;border:1px solid var(--line);vertical-align:top}
tr{page-break-inside:avoid}
tbody tr:nth-child(even){background:#fbfcfe}
blockquote{margin:14px 0;padding:10px 16px;background:#fff8f4;border-left:3px solid var(--brand);
  color:#6b5445;font-size:12.5px;page-break-inside:avoid}
ul,ol{margin:8px 0 14px;padding-left:22px}
li{margin:4px 0}
li.check{list-style:none;margin-left:-18px}
hr.rule{border:none;border-top:1px solid var(--line);margin:26px 0}
a{color:var(--brand)}
/* 打印 */
@page{size:A4;margin:16mm 14mm}
@media print{
  body{background:#fff}
  .page{box-shadow:none;max-width:none;padding:0}
  .cover{min-height:auto;padding-bottom:0}
  th{background:#f2f4f7 !important;-webkit-print-color-adjust:exact;print-color-adjust:exact}
  tbody tr:nth-child(even){background:#fafbfd !important;-webkit-print-color-adjust:exact;print-color-adjust:exact}
}
"""


def main():
    md = SRC.read_text(encoding="utf-8")
    # 去掉首个 H1（放到封面）
    md_body = re.sub(r"^#\s+.*?\n", "", md, count=1)
    blocks, toc = parse(md_body)

    logo = extract_logo()
    logo_tag = f'<img class="logo" src="{logo}" alt="CC">' if logo else ""

    toc_html = ['<div class="toc"><h2>目录</h2><ol>']
    c2 = 0
    for lv, text, sid in toc:
        if lv == 2:
            c2 += 1
            toc_html.append(f'<li class="lv2"><a href="#{sid}"><span class="num">{c2}</span>{inline(text)}</a></li>')
        else:
            toc_html.append(f'<li class="lv3"><a href="#{sid}">{inline(text)}</a></li>')
    toc_html.append("</ol></div>")

    out = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>CC CRM 产品规划书 v1.0</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>{CSS}</style></head><body>
<div class="page">
  <div class="cover">
    <div class="brand">{logo_tag}<div><b>CC CRM</b><span>客户与外呼管理</span></div></div>
    <h1>产品规划书</h1>
    <div class="sub">马来西亚本地外呼团队 · 客户名单管理与作业系统</div>
    <div class="meta">
      <b>文档版本</b><span>v1.0</span>
      <b>日期</b><span>2026-10-20</span>
      <b>状态</b><span>待评审</span>
      <b>适用对象</b><span>产品 / 研发 / 测试 / 业务方</span>
      <b>配套资产</b><span>交互原型 v4.0 · 界面规范 · 代码图谱 · 优化建议</span>
      <b>部署场景</b><span>局域网单机，10–30 坐席</span>
    </div>
    <div class="foot">本文档为功能与规则的唯一依据。原型用于确认规则，生产实现以本文档 + 评审纪要为准。</div>
  </div>
  {''.join(toc_html)}
  {''.join(blocks)}
</div>
</body></html>"""
    OUT.write_text(out, encoding="utf-8")
    print(f"wrote {OUT} ({len(out)//1024} KB), toc={len(toc)}")


if __name__ == "__main__":
    main()
