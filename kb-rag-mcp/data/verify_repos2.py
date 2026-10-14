"""第二轮核验：新发现的 RAG / 知识库 MCP 候选"""
import json, urllib.request, urllib.error, time

TOKEN_PATH = r"C:/Users/Admin/.workbuddy-ai/skills/github-sync/token.txt"
with open(TOKEN_PATH, "r", encoding="utf-8") as f:
    tok = f.read().strip()

REPOS = [
    # ===== 直接做「知识库 RAG MCP」的（本轮核心发现）=====
    "lyonzin/knowledge-rag",
    "ggozad/haiku.rag",
    "olafgeibig/knowledge-mcp",
    "nduckmink/arkon",
    "docsagent/docsagent",
    "benmaster82/Kwipu",
    "Scisaga/qwen3-retrieval-server",
    "TadMSTR/searxng-mcp",
    "mathomhaus/guild",
    "jaredrhod/ai-memory-vault",
    "okf-memory/okf-agent-memory",
    "0xK3vin/MegaMemory",
    "forloopcodes/contextplus",
    "shaneholloman/mcp-knowledge-graph",
    "GreatScottyMac/context-portal",
    "iwe-org/iwe",
    "kwanLeeFrmVi/mcp-rag-server",
    "bekirdag/docdex",
    "Xevos117/mcp-zotero",
    "Lyellr88/marm-memory",
    "opendatalab/MinerU-Document-Explorer",
    "Citadel-Cloud-Management/mcp-server-vector-db",
    # ===== 星数需重点确认的（疑似异常）=====
    "Graphify-Labs/graphify",
    "DeusData/codebase-memory-mcp",
    "headroomlabs-ai/headroom",
    "rocketride-org/rocketride-server",
    # ===== 代码库 / 企业知识库 RAG =====
    "xerrors/Yuxi",
    "vitali87/code-graph-rag",
    "FlowElement-xinliuyuansu/m_flow",
    "zylon-ai/private-gpt",
    "giancarloerra/SocratiCode",
    "CodeBendKit/codeseek",
    "rush-db/rushdb",
    "orneryd/NornicDB",
    "scrypster/muninndb",
    "ctxpipe-ai/ctxpipe",
    "vsov/okfy",
    # ===== 评测 / 工程化 =====
    "Kiln-AI/Kiln",
    "unclecode/crawl4ai",
    "chunxiaoxx/nautilus-compass",
    # ===== 补齐缺失 =====
    "chonkie-inc/chonkie",
    "chonkie-ai/chonkie",
    "BAAI/bge-reranker-v2-m3",
    "xlang-ai/ModelScope",
    "smithery-ai/reference-servers",
    "smithery-ai/mcp-servers",
    "modelcontextprotocol/ext-apps",
    "pymupdf/RAG",
    "run-llama/llama_parse",
    "embedchain/embedchain",
    "pathwaycom/pathway",
    "huggingface/text-embeddings-inference",
]

def get(repo):
    repo = repo.strip().rstrip("/")
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}",
        headers={"Authorization": f"Bearer {tok}",
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "research-bot"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            d = json.load(resp)
        return {"query": repo, "repo": d.get("full_name"),
                "stars": d.get("stargazers_count"), "forks": d.get("forks_count"),
                "license": (d.get("license") or {}).get("spdx_id"),
                "pushed_at": (d.get("pushed_at") or "")[:10],
                "created_at": (d.get("created_at") or "")[:10],
                "archived": bool(d.get("archived")),
                "language": d.get("language"),
                "topics": (d.get("topics") or [])[:12],
                "description": (d.get("description") or "")[:200],
                "html_url": d.get("html_url")}
    except urllib.error.HTTPError as e:
        return {"query": repo, "error": f"HTTP {e.code}"}
    except Exception as e:
        return {"query": repo, "error": str(e)[:120]}

out = []
for r in REPOS:
    res = get(r)
    out.append(res)
    if "stars" in res:
        print(f"{res['repo']:<50} {res['stars']:>7}  {str(res['license']):<14} {res['pushed_at']}  arch={res['archived']}")
    else:
        print(f"{res['query']:<50} {res.get('error')}")
    time.sleep(0.3)

with open(r"C:/Users/Admin/WorkBuddy AI/2026-10-14-15-31-23/kb-rag-mcp/data/github-verified-2.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

ok = [x for x in out if "stars" in x]
print(f"\n=== OK {len(ok)} / {len(out)} ===")
print("FAILED:", [x["query"] for x in out if "error" in x])
