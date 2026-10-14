"""GitHub API 一手核验：个人助理/Agent 框架 + 个人助理场景 MCP 服务器"""
import os, json, urllib.request, urllib.error, time

TOKEN_PATH = r"C:/Users/Admin/.workbuddy-ai/skills/github-sync/token.txt"
with open(TOKEN_PATH, "r", encoding="utf-8") as f:
    tok = f.read().strip()

REPOS = [
    # ---- 个人助理 / Agent 框架本体 ----
    "openclaw/openclaw",
    "steipete/openclaw",
    "NousResearch/hermes-agent",
    "deepseek-ai/dsh",
    "deepseek-ai/DeepSeek-Harness",
    "block/goose",
    "openinterpreter/open-interpreter",
    "microsoft/autogen",
    "OpenBMB/AgentVerse",
    "frdel/agent-zero",
    "FoundationAgents/OpenManus",
    "letta-ai/letta",
    "kortix-ai/suna",
    "Significant-Gravitas/AutoGPT",
    "khoj-ai/khoj",
    "danielmiessler/fabric",
    "All-Hands-AI/OpenHands",
    "e2b-dev/E2B",
    # ---- MCP 官方 / 参考 ----
    "modelcontextprotocol/servers",
    "modelcontextprotocol/python-sdk",
    "modelcontextprotocol/typescript-sdk",
    "modelcontextprotocol/registry",
    "modelcontextprotocol/inspector",
    # ---- 通用核心必装 MCP ----
    "wonderwhy-er/DesktopCommanderMCP",
    "modelcontextprotocol/servers/tree/main/src/filesystem",
    "exa-labs/exa-mcp-server",
    "brave/brave-search-mcp-server",
    "mendableai/firecrawl-mcp-server",
    "getzep/graphiti",
    "doobidoo/mcp-memory-service",
    "upstash/context7",
    "github/github-mcp-server",
    "microsoft/playwright-mcp",
    "executeautomation/mcp-playwright",
    "browserbase/mcp-server-browserbase",
    "cloudflare/mcp-server-cloudflare",
    "supabase-community/supabase-mcp",
    # ---- 笔记 / 知识 / 办公 ----
    "suekou/mcp-notion-server",
    "makenotion/notion-mcp-server",
    "smithery-ai/notion-mcp",
    "MarkusPfundstein/mcp-obsidian",
    "StevenStavrakis/obsidian-mcp",
    "calclavia/mcp-obsidian",
    "taylorwilsdon/google_workspace_mcp",
    "GongRzhe/Gmail-MCP-Server",
    "zapier/zapier-mcp",
    "melanie-schneider/mcp-gsuite",
    # ---- IM / 沟通 ----
    "modelcontextprotocol/servers/tree/main/src/slack",
    "korotovsky/slack-mcp-server",
    "larksuite/lark-openapi-mcp",
    "varunneal/spotify-mcp",
    "adhikasp/mcp-gitlab",
    # ---- 地图 / 中国生态 ----
    "amap-maps/mcp",
    # ---- 浏览器 / 抓取 ----
    "BrowserMCP/mcp",
    "hyperbrowserai/mcp",
    "apify/apify-mcp-server",
    "oxylabs/oxylabs-mcp",
    # ---- 其他常被推荐 ----
    "sooperset/mcp-atlassian",
    "sentry-mcp",
    "getsentry/toolkit",
    "perplexityai/modelcontextprotocol",
    "supermemoryai/apple-mcp",
    "semgrep/mcp",
    "e2b-dev/mcp-server",
    "JetBrains/mcp-jetbrains",
    "jerhadf/linear-mcp-server",
    "microsoft/markitdown",
    "microsoft/playwright",
    # ---- MCP 客户端 ----
    "lobehub/lobe-chat",
    "CherryHQ/cherry-studio",
    "danny-avila/LibreChat",
    "Mintplex-Labs/anything-llm",
    "nbonamy/witsy",
    "mcp-router/mcp-router",
    "mcpjam/inspector",
    "punkpeye/awesome-mcp-servers",
    "wong2/awesome-mcp-servers",
    "modelcontextprotocol/awesome-mcp-clients",
    "punkpeye/fastmcp",
    "jlowin/fastmcp",
    "chatboxai/chatbox",
]

def get(repo):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}",
        headers={
            "Authorization": f"Bearer {tok}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "research-bot",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            d = json.load(resp)
        return {
            "query": repo,
            "repo": d.get("full_name"),
            "stars": d.get("stargazers_count"),
            "forks": d.get("forks_count"),
            "license": (d.get("license") or {}).get("spdx_id"),
            "pushed_at": (d.get("pushed_at") or "")[:10],
            "created_at": (d.get("created_at") or "")[:10],
            "archived": bool(d.get("archived")),
            "open_issues": d.get("open_issues_count"),
            "description": (d.get("description") or "")[:180],
            "html_url": d.get("html_url"),
        }
    except urllib.error.HTTPError as e:
        return {"query": repo, "error": f"HTTP {e.code}"}
    except Exception as e:
        return {"query": repo, "error": str(e)[:120]}

out = []
for r in REPOS:
    res = get(r)
    out.append(res)
    print(json.dumps(res, ensure_ascii=False))
    time.sleep(0.35)

with open(r"C:/Users/Admin/WorkBuddy AI/2026-10-14-15-31-23/personal-assistant-mcp/data/github-verified.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

ok = [x for x in out if "stars" in x]
print(f"\n=== OK {len(ok)} / {len(out)} ===")
print("FAILED:", [x["query"] for x in out if "error" in x])
