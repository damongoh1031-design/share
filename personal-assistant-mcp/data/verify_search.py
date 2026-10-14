"""补充核验：用 GitHub Search API 定位中国生态 MCP 与缺失仓库"""
import json, urllib.request, urllib.parse, time

TOKEN_PATH = r"C:/Users/Admin/.workbuddy-ai/skills/github-sync/token.txt"
with open(TOKEN_PATH, "r", encoding="utf-8") as f:
    tok = f.read().strip()

def search(q, per_page=5):
    url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
        {"q": q, "sort": "stars", "order": "desc", "per_page": per_page}
    )
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {tok}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "research-bot",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            d = json.load(resp)
        return [{
            "repo": i["full_name"], "stars": i["stargazers_count"],
            "license": (i.get("license") or {}).get("spdx_id"),
            "pushed_at": (i.get("pushed_at") or "")[:10],
            "archived": i.get("archived"),
            "desc": (i.get("description") or "")[:130],
        } for i in d.get("items", [])]
    except Exception as e:
        return [{"error": str(e)[:100]}]

QUERIES = [
    "amap mcp server",
    "高德地图 mcp",
    "mcp-server amap",
    "feishu mcp server",
    "wecom mcp server",
    "tencent docs mcp",
    "caiyun weather mcp",
    "weread mcp",
    "mcp obsidian",
    "mcp home assistant",
    "mcp calendar",
    "mcp email imap",
    "mcp rss",
    "mcp translation",
    "mcp finance stock",
    "personal assistant mcp",
    "mcp server awesome list",
    "clawhub",
    "mcp registry china",
]

out = {}
for q in QUERIES:
    r = search(q)
    out[q] = r
    print(f"\n### {q}")
    for i in r:
        print("   ", json.dumps(i, ensure_ascii=False))
    time.sleep(2.5)  # search API 限速更严

with open(r"C:/Users/Admin/WorkBuddy AI/2026-10-14-15-31-23/personal-assistant-mcp/data/github-search.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("\n=== done ===")
