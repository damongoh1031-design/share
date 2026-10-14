#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass 2: filter + score + classify collected items."""
import json, os, re, collections

OUT = os.path.dirname(os.path.abspath(__file__))

AI_TERMS = [
    r"\bllm\b", r"\bgpt\b", r"chatgpt", r"claude", r"\bcodex\b", r"copilot",
    r"gemini", r"deepseek", r"\bqwen\b", r"mistral", r"ollama", r"openai",
    r"anthropic", r"\bmcp\b", r"model context protocol", r"cursor",
    r"\bcline\b", r"\baider\b", r"windsurf", r"vibe.?cod", r"ai coding",
    r"ai.?(assistant|agent|powered|generated|driven|workflow|tool)",
    r"local ai", r"ai.?assisted", r"continue\.dev", r"roo\b",
    r"\bagents?\b",
]
NIX_TERMS = [
    r"\bnix\b", r"nixos", r"flake", r"nixpkgs", r"home.?manager", r"nix.?darwin",
    r"nixos.?rebuild", r"nix.?shell", r"nix.?env", r"nix.?channel", r"nix.?store",
    r"devshell", r"nix.?develop", r"nix flake", r"configuration\.nix",
]

CATS = [
    ("A. 用 AI 写/改 NixOS 配置", [r"configuration\.nix", r"write.*nix", r"nix.*(config|module).*(ai|llm|gpt|claude)", r"generate.*nix", r"ai.*(write|edit|fix).*(nix|config)", r"flake.*(ai|llm|claude|gpt)", r"(ai|llm|claude|gpt).*flake"]),
    ("B. AI Agent 运维 NixOS 服务器", [r"ai agent", r"agentic", r"nixos.?agent", r"agent.*nixos", r"nixos.*agent", r"autonomous", r"self.?host.*ai.*nixos", r"ai.*(manage|manage|operate|admin).*nixos", r"ssh.*(claude|codex|ai)", r"(claude|codex|ai).*ssh"]),
    ("C. MCP × NixOS", [r"\bmcp\b", r"model context protocol"]),
    ("D. 用 Nix 打包/运行 AI 工具", [r"llm.?agents\.nix", r"nixified", r"nixify", r"package.*(claude|codex|ai|llm)", r"(claude|codex|ai|llm).*packag", r"nixpkgs.*(ai|llm)", r"derivation.*(ai|llm)", r"nix run.*(ai|llm)"]),
    ("E. AI 教学/答疑 NixOS", [r"learn.*nix", r"nix.*(tutorial|learn|beginner|newbie|new user|teach)", r"understand.*nix", r"documentation.*(ai|agent)", r"agent.*documentation", r"explain.*nix"]),
    ("F. AI 生成配置的坑/翻车", [r"hallucinat", r"wrong.*option", r"made up", r"doesn'?t exist", r"broken.*build", r"fails?.*(build|eval)", r"garbage", r"nonsense", r"outdated.*option", r"wrong.*(syntax|attribute)"]),
    ("G. 安全与信任边界", [r"security", r"sandbox", r"isolat", r"permission", r"root access", r"sudo", r"prompt inject", r"trust", r"dangerous", r"read.?only"]),
    ("H. 本地推理 / GPU", [r"gpu", r"cuda", r"rocm", r"vram", r"local model", r"inference", r"nvidia", r"amd"]),
    ("I. 反对/怀疑 AI 用于 NixOS", [r"don'?t.*(use|trust|like).*(ai|llm|gpt|claude)", r"(ai|llm|gpt|claude).*(suck|terrible|useless|bad)", r"anti.?ai", r"hate.*ai", r"against.*ai", r"overhyped", r"ai slop"]),
]

def text_of(x):
    return " ".join(str(x.get(k, "")) for k in
                    ("topic_title", "title", "blurb", "text", "body")).lower()

def has_any(t, pats):
    return any(re.search(p, t) for p in pats)

def classify(t):
    hits = []
    for name, pats in CATS:
        if has_any(t, pats):
            hits.append(name)
    return hits

# ---------------- Discourse ----------------
d = json.load(open(os.path.join(OUT, "raw_discourse.json"), encoding="utf-8"))
disco_keep = []
for x in d:
    t = text_of(x)
    if not has_any(t, AI_TERMS):
        continue
    if not has_any(t, NIX_TERMS):
        continue
    if x.get("matched_kw") in ("continue dev",):
        continue
    x["cats"] = classify(t)
    x["ai_hit"] = has_any(t, AI_TERMS)
    disco_keep.append(x)
print("discourse kept %d / %d" % (len(disco_keep), len(d)))

# ---------------- HN ----------------
h = json.load(open(os.path.join(OUT, "raw_hn.json"), encoding="utf-8"))
hn_keep = []
for x in h:
    t = text_of(x)
    if not has_any(t, AI_TERMS) or not has_any(t, NIX_TERMS):
        continue
    x["cats"] = classify(t)
    hn_keep.append(x)
print("hn kept %d / %d" % (len(hn_keep), len(h)))

# ---------------- GitHub ----------------
g = json.load(open(os.path.join(OUT, "raw_github.json"), encoding="utf-8"))
gh_keep = []
for x in g:
    t = text_of(x)
    if not has_any(t, AI_TERMS) or not has_any(t, NIX_TERMS):
        continue
    x["cats"] = classify(t)
    gh_keep.append(x)
print("github kept %d / %d" % (len(gh_keep), len(g)))

# ---------------- search results ----------------
s = []
sp = os.path.join(OUT, "raw_search.json")
if os.path.exists(sp):
    s = json.load(open(sp, encoding="utf-8"))
s_keep = []
for x in s:
    t = text_of(x)
    if not has_any(t, AI_TERMS):
        continue
    if not has_any(t, NIX_TERMS):
        continue
    x["cats"] = classify(t)
    s_keep.append(x)
print("search kept %d / %d" % (len(s_keep), len(s)))

json.dump(disco_keep, open(os.path.join(OUT, "f_discourse.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(hn_keep, open(os.path.join(OUT, "f_hn.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(gh_keep, open(os.path.join(OUT, "f_github.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(s_keep, open(os.path.join(OUT, "f_search.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------- stats ----------------
allk = disco_keep + hn_keep + gh_keep + s_keep
print("\n=== TOTAL KEPT: %d ===" % len(allk))
cc = collections.Counter()
for x in allk:
    for c in x.get("cats") or ["(未分类)"]:
        cc[c] += 1
print("\n--- categories ---")
for k, v in cc.most_common():
    print("  %-34s %d" % (k, v))
sc = collections.Counter(x["source"] for x in allk)
print("\n--- sources ---")
for k, v in sc.most_common():
    print("  %-26s %d" % (k, v))

# Discourse topic dedupe
tops = {}
for x in disco_keep:
    tops.setdefault(x["topic_id"], []).append(x)
print("\ndiscourse unique topics after filter: %d" % len(tops))
