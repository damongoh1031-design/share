#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass 3: consolidate curated dataset -> markdown appendix + stats."""
import json, os, re, collections

OUT = os.path.dirname(os.path.abspath(__file__))

CATNAME = {
    "A. 用 AI 写/改 NixOS 配置": "写配置",
    "B. AI Agent 运维 NixOS 服务器": "Agent运维",
    "C. MCP × NixOS": "MCP",
    "D. 用 Nix 打包/运行 AI 工具": "打包AI工具",
    "E. AI 教学/答疑 NixOS": "教学",
    "F. AI 生成配置的坑/翻车": "翻车",
    "G. 安全与信任边界": "安全",
    "H. 本地推理 / GPU": "本地推理",
    "I. 反对/怀疑 AI 用于 NixOS": "反对",
}

def catstr(cats):
    if not cats:
        return "综合"
    return "/".join(CATNAME.get(c, c) for c in cats[:2])

# ---- topics with full text ----
topics = json.load(open(os.path.join(OUT, "topics_full.json"), encoding="utf-8"))
topics.sort(key=lambda x: -x["like_count"])

# ---- filtered individual posts ----
d = json.load(open(os.path.join(OUT, "f_discourse.json"), encoding="utf-8"))
h = json.load(open(os.path.join(OUT, "f_hn.json"), encoding="utf-8"))
g = json.load(open(os.path.join(OUT, "f_github.json"), encoding="utf-8"))
sl = json.load(open(os.path.join(OUT, "f_search.json"), encoding="utf-8"))

_tcat = {}
for _x in d:
    _tcat.setdefault(_x["topic_id"], set()).update(_x.get("cats") or [])
for _t in topics:
    _t["cats"] = sorted(_tcat.get(_t["topic_id"], []))

md = []
md.append("## 附录：贴文明细（精选）\n")
md.append("### A. NixOS Discourse 主题（按赞数排序，共 %d 个主题已读全文）\n" % len(topics))
md.append("| # | 赞 | 回复 | 日期 | 主题 | 分类 | 链接 |")
md.append("|---|---|---|---|---|---|---|")
for i, x in enumerate(topics, 1):
    dt = (x["created_at"] or "")[:10]
    t = (x["title"] or "").replace("|", "/")[:78]
    md.append("| %d | %d | %d | %s | %s | %s | [link](%s) |" % (
        i, x["like_count"], x["posts_count"], dt, t, catstr(x.get("cats")), x["url"]))
md.append("")

# HN
st = sorted([x for x in h if x["kind"] == "story"], key=lambda x: -x["points"])
cm = [x for x in h if x["kind"] == "comment" and len(x.get("text", "")) > 250]
md.append("### B. Hacker News 条目（共 %d 条匹配：%d 故事 + %d 评论）\n" % (len(h), len(st), len(h) - len(st)))
md.append("| # | 分 | 评论 | 日期 | 标题 | 分类 | 链接 |")
md.append("|---|---|---|---|---|---|---|")
for i, x in enumerate(st[:40], 1):
    dt = (x["created_at"] or "")[:10]
    md.append("| %d | %d | %d | %s | %s | %s | [link](%s) |" % (
        i, x["points"], x["num_comments"], dt, x["title"].replace("|", "/")[:70],
        catstr(x.get("cats")), x["url"]))
md.append("")
md.append("**HN 高信息量评论摘选**（%d 条超过 250 字符的匹配评论）：\n" % len(cm))
for x in cm[:12]:
    md.append("- @%s（%s）：%s [link](%s)" % (
        x["author"], (x["created_at"] or "")[:10], x["text"][:280].replace("\n", " "), x["url"]))
md.append("")

# GitHub
_NOISE = re.compile(r"flake\.lock|automated updates|rotate .*token|as an A2A hub peer|"
                    r"health path|Update lock|dependabot|renovate|\[bot\]", re.I)
_gh = [x for x in g if not _NOISE.search(x["title"])]
g_sorted = sorted(_gh, key=lambda x: -x["comments"])
md.append("### C. GitHub 条目（共 %d 个匹配 / 去自动化噪声后 %d 条，来自 %d 个仓库）\n" % (
    len(g), len(_gh), len({x["repo"] for x in g})))
md.append("| # | 仓库 | 类型 | 评论 | 日期 | 标题 | 链接 |")
md.append("|---|---|---|---|---|---|---|")
for i, x in enumerate(g_sorted[:45], 1):
    dt = (x["created_at"] or "")[:10]
    md.append("| %d | `%s` | %s | %d | %s | %s | [link](%s) |" % (
        i, x["repo"][:38], x["kind"], x["comments"], dt,
        x["title"].replace("|", "/")[:58], x["url"]))
md.append("")

# stats
md.append("### D. 匹配规模统计\n")
md.append("| 来源 | 原始抓取 | 通过 AI×Nix 双关键词过滤 | 说明 |")
md.append("|---|---|---|---|")
md.append("| NixOS Discourse | 1,600 帖 | %d 帖 / %d 主题 | 23 个关键词 × 3 页 |" % (
    len(d), len({x["topic_id"] for x in d})))
md.append("| Hacker News (Algolia) | 1,148 条 | %d 条 | 13 组查询，故事+评论 |" % len(h))
md.append("| GitHub issues/PRs/discussions | 553 | %d | 3 组查询 |" % len(g))
md.append("| 搜索引擎（DDG/Bing/内置） | %d | %d | Reddit/X/Discord 受反爬限制，覆盖率低 |" % (
    len(sl) + 4, len(sl)))
md.append("| **合计** | **%d** | **%d** | 全部为「AI × Nix」双命中 |" % (
    1600 + 1148 + 553 + 4, len(d) + len(h) + len(g) + len(sl)))
md.append("")

cc = collections.Counter()
for x in d + h + g + sl:
    for c in x.get("cats") or ["(未分类)"]:
        cc[c] += 1
md.append("### E. 使用模式分布（按主题归类，可多属）\n")
md.append("| 模式 | 命中贴文数 |")
md.append("|---|---|")
for k, v in cc.most_common():
    md.append("| %s | %d |" % (k, v))
md.append("| **合计命中** | **%d** |" % sum(cc.values()))
md.append("")

open(os.path.join(OUT, "appendix.md"), "w", encoding="utf-8").write("\n".join(md))
print("appendix written: %d lines" % len(md))
print("discourse topics:", len(topics), " posts read:", sum(len(x['posts']) for x in topics))
print("hn stories:", len(st), " hn comments:", len(h) - len(st))
print("github:", len(g))
