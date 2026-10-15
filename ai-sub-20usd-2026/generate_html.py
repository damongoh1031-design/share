# -*- coding: utf-8 -*-
"""读取 report.md，转换为带样式的自包含 HTML 报告。"""
import html
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "report.md")
OUT = os.path.join(BASE, "report.html")

CSS = """
:root{--bg:#f6f7f9;--card:#ffffff;--ink:#1a2233;--muted:#5b6474;--line:#e4e8ee;
--accent:#2563eb;--accent2:#7c3aed;--good:#dc2626;--warn:#d97706;--chip:#eef2ff;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.75 -apple-system,"Segoe UI","Microsoft YaHei","PingFang SC",sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:32px 20px 80px}
header.hero{background:linear-gradient(135deg,#1e3a8a,#4f46e5);color:#fff;border-radius:16px;
padding:34px 36px;margin-bottom:26px}
header.hero h1{margin:0 0 10px;font-size:26px;line-height:1.4}
header.hero p{margin:4px 0;opacity:.92;font-size:13.5px}
h2{font-size:21px;margin:38px 0 14px;padding-left:12px;border-left:5px solid var(--accent)}
h3{font-size:16.5px;margin:22px 0 8px;color:#111827}
p{margin:10px 0}
blockquote{margin:12px 0;padding:10px 16px;background:#fff8e6;border-left:4px solid var(--warn);
border-radius:0 8px 8px 0;color:#6b4e00;font-size:13.5px}
table{width:100%;border-collapse:collapse;margin:14px 0;background:var(--card);
border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(16,24,40,.08);font-size:13.5px}
th{background:#eef2ff;color:#1e293b;text-align:left;padding:9px 12px;border-bottom:2px solid var(--line);white-space:nowrap}
td{padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top;color:var(--ink)}
tr:last-child td{border-bottom:none}
tr:hover td{background:#f8faff}
code{background:var(--chip);padding:1px 6px;border-radius:6px;font-size:12.5px}
ul,ol{padding-left:22px}
li{margin:5px 0}
strong{color:#0f172a}
.bar-row{display:flex;align-items:center;gap:10px;margin:7px 0}
.bar-label{width:230px;text-align:right;font-size:13px;color:var(--muted);flex:none}
.bar-track{flex:1;background:#e8ecf3;border-radius:7px;height:22px;position:relative}
.bar-fill{height:100%;border-radius:7px;background:linear-gradient(90deg,#3b82f6,#8b5cf6)}
.bar-fill.top{background:linear-gradient(90deg,#dc2626,#f97316)}
.bar-fill.low{background:linear-gradient(90deg,#94a3b8,#cbd5e1)}
.bar-val{position:absolute;right:8px;top:0;line-height:22px;font-size:12.5px;font-weight:600;color:#0f172a}
.note{font-size:12.5px;color:var(--muted);margin-top:6px}
hr{border:none;border-top:1px solid var(--line);margin:34px 0}
footer{margin-top:44px;font-size:12.5px;color:var(--muted);border-top:1px solid var(--line);padding-top:16px}
.badge{display:inline-block;background:var(--chip);color:#3730a3;border-radius:999px;
padding:1px 10px;font-size:12px;margin-right:6px;font-weight:600}
"""

BARS = """
<h2>Artificial Analysis 智能指数（2026年10月）</h2>
<div class="bar-row"><div class="bar-label">Claude Opus 5.5（Claude Pro $20）</div><div class="bar-track"><div class="bar-fill top" style="width:96.7%"></div><div class="bar-val">58 · 第1名</div></div></div>
<div class="bar-row"><div class="bar-label">Claude Sonnet 5.5（Pro / Antigravity）</div><div class="bar-track"><div class="bar-fill top" style="width:93.3%"></div><div class="bar-val">56</div></div></div>
<div class="bar-row"><div class="bar-label">Meta Muse Wonder Full（非订阅对照）</div><div class="bar-track"><div class="bar-fill" style="width:93.3%"></div><div class="bar-val">56</div></div></div>
<div class="bar-row"><div class="bar-label">GPT-6 Astra（ChatGPT $100+ / Antigravity）</div><div class="bar-track"><div class="bar-fill" style="width:88.3%"></div><div class="bar-val">53</div></div></div>
<div class="bar-row"><div class="bar-label">Gemini 4 Argon（AI Pro $19.99）</div><div class="bar-track"><div class="bar-fill" style="width:88.3%"></div><div class="bar-val">53</div></div></div>
<div class="bar-row"><div class="bar-label">GPT-6.1 Sol（Plus 的 Work/Codex）</div><div class="bar-track"><div class="bar-fill" style="width:86.7%"></div><div class="bar-val">52</div></div></div>
<p class="note">指数为 Artificial Analysis Intelligence Index（0–100 相对分），2026-10 口径。Grok 4.7 存在 46 与 61 的信源冲突，未列入。编码智能体指数另计。数据截至 2026-10-15。</p>
"""

BARS2 = """
<h2>AA-Omniscience 幻觉率（越低越好，2026-10）</h2>
<div class="bar-row"><div class="bar-label">Gemini 4 Argon</div><div class="bar-track"><div class="bar-fill top" style="width:15%;background:linear-gradient(90deg,#16a34a,#4ade80)"></div><div class="bar-val">15% · 最低</div></div></div>
<div class="bar-row"><div class="bar-label">GPT-6 Astra</div><div class="bar-track"><div class="bar-fill" style="width:51%;background:linear-gradient(90deg,#2563eb,#60a5fa)"></div><div class="bar-val">45–51%</div></div></div>
<div class="bar-row"><div class="bar-label">Claude Opus 5.5（最高推理档）</div><div class="bar-track"><div class="bar-fill" style="width:59%;background:linear-gradient(90deg,#7c3aed,#a78bfa)"></div><div class="bar-val">59%</div></div></div>
<div class="bar-row"><div class="bar-label">Claude Fable 5.1（最高推理档）</div><div class="bar-track"><div class="bar-fill low" style="width:73%;background:linear-gradient(90deg,#dc2626,#f87171)"></div><div class="bar-val">73%</div></div></div>
<div class="bar-row"><div class="bar-label">GPT-5.5（2026-08 旧口径）</div><div class="bar-track"><div class="bar-fill low" style="width:86%;background:linear-gradient(90deg,#dc2626,#f87171)"></div><div class="bar-val">86%</div></div></div>
<p class="note">口径：模型答错问题中仍硬答的比例（承认不知道不计入）。该指标奖励克制。学术引用实测（2026-06，50 篇）：Perplexity Pro 4% &lt; Gemini 16% &lt; ChatGPT Plus 24%。旧版"Claude 幻觉最低"基于 Opus 4.7（2026-04），已被推翻。</p>
"""

BARS3 = """
<h2>GraphWalks 长上下文命中（256K–1M，越高越好）</h2>
<div class="bar-row"><div class="bar-label">Gemini 4 Argon</div><div class="bar-track"><div class="bar-fill top" style="width:84.2%"></div><div class="bar-val">84.2% · 第一</div></div></div>
<div class="bar-row"><div class="bar-label">GPT-6 Astra</div><div class="bar-track"><div class="bar-fill" style="width:71.8%"></div><div class="bar-val">71.8%</div></div></div>
<div class="bar-row"><div class="bar-label">Claude 系（约）</div><div class="bar-track"><div class="bar-fill" style="width:65%"></div><div class="bar-val">约 65%</div></div></div>
<p class="note">MRCR v2 @1M 口径：GPT-5.5 约 74.x &gt; Opus 4.6 78.3%→4.7 32.2%（迭代回退）&gt; GPT-5.4 36.6%。注意：MRCR 高分多为固定针位下取得，与真实文档检索有差距。</p>
"""


def md_inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def convert(md_text):
    lines = md_text.split("\n")
    out = []
    i = 0
    in_ul = in_ol = False
    hero_mode = False
    while i < len(lines):
        ln = lines[i]
        stripped = ln.strip()
        # 表格
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:\-|]+\|$", lines[i + 1].strip()):
            if in_ul:
                out.append("</ul>"); in_ul = False
            if in_ol:
                out.append("</ol>"); in_ol = False
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ["<table><thead><tr>"] + ["<th>%s</th>" % md_inline(h) for h in header] + ["</tr></thead><tbody>"]
            for r in rows:
                t.append("<tr>" + "".join("<td>%s</td>" % md_inline(c) for c in r) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue
        # 标题
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            if in_ul: out.append("</ul>"); in_ul = False
            if in_ol: out.append("</ol>"); in_ol = False
            lvl = len(m.group(1))
            if lvl == 1:
                out.append('<header class="hero"><h1>%s</h1>' % md_inline(m.group(2)))
                hero_mode = True
            else:
                # hero 区块只包裹标题+元信息，遇到第一个二级标题即闭合，避免白色字体渗入后续内容
                if hero_mode and lvl == 2:
                    out.append("</header>")
                    hero_mode = False
                out.append("<h%d>%s</h%d>" % (lvl, md_inline(m.group(2)), lvl))
            i += 1
            continue
        # 引用
        if stripped.startswith(">"):
            if in_ul: out.append("</ul>"); in_ul = False
            if in_ol: out.append("</ol>"); in_ol = False
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote>%s</blockquote>" % md_inline(" ".join(buf)))
            continue
        # 列表
        m = re.match(r"^[-*]\s+(.*)$", stripped)
        if m:
            if in_ol: out.append("</ol>"); in_ol = False
            if not in_ul:
                out.append("<ul>"); in_ul = True
            out.append("<li>%s</li>" % md_inline(m.group(1)))
            i += 1
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m:
            if in_ul: out.append("</ul>"); in_ul = False
            if not in_ol:
                out.append("<ol>"); in_ol = True
            out.append("<li>%s</li>" % md_inline(m.group(2)))
            i += 1
            continue
        if stripped in ("", "---"):
            if in_ul: out.append("</ul>"); in_ul = False
            if in_ol: out.append("</ol>"); in_ol = False
            if stripped == "---":
                out.append("<hr>")
            i += 1
            continue
        if in_ul: out.append("</ul>"); in_ul = False
        if in_ol: out.append("</ol>"); in_ol = False
        out.append("<p>%s</p>" % md_inline(stripped))
        i += 1
    if in_ul: out.append("</ul>")
    if in_ol: out.append("</ol>")
    if hero_mode: out.append("</header>")
    return "\n".join(out)


def main():
    with open(SRC, encoding="utf-8") as f:
        md = f.read()
    body = convert(md)
    # 在对应章节前插入条形图
    body = body.replace("<h2>三、模型与智力（Artificial Analysis，2026-10）</h2>",
                        BARS + "<h2>三、模型与智力（Artificial Analysis，2026-10）</h2>")
    body = body.replace("<h3>4.1 AA-Omniscience 幻觉率（2026-10，越低越好）</h3>",
                        BARS2 + "<h3>4.1 AA-Omniscience 幻觉率（2026-10，越低越好）</h3>")
    body = body.replace("<h2>五、长上下文命中（法律场景第二指标）</h2>",
                        BARS3 + "<h2>五、长上下文命中（法律场景第二指标）</h2>")
    # 目录锚点小节转为卡片式提示
    doc = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>20美元档 AI 订阅深度横评 · 法律条文场景（2026-10）</title>
<style>%s</style>
</head>
<body><div class="wrap">
%s
<footer>本报告由 DeepResearch 工作流生成：6 个调研对象 × 10 个字段，数据经 20+ 次联网检索交叉验证（官方帮助中心 / Artificial Analysis / LMArena / IT之家 / 知乎 / 什么值得买 / CSDN 等）。标注 [不确定] 或列入“数据缺口”的字段为未获权威证据项。价格与权益随时可能调整，购买前请以官网实时页面为准。</footer>
</div></body></html>""" % (CSS, body)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(doc)
    print("written:", OUT)


if __name__ == "__main__":
    main()
