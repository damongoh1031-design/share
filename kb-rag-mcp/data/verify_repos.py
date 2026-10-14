"""知识库 / RAG / 召回 / 重排 场景 MCP 与相关项目 —— GitHub API 一手核验"""
import os, json, urllib.request, urllib.error, time

TOKEN_PATH = r"C:/Users/Admin/.workbuddy-ai/skills/github-sync/token.txt"
with open(TOKEN_PATH, "r", encoding="utf-8") as f:
    tok = f.read().strip()

REPOS = [
    # ===== 向量数据库 / 检索后端 MCP =====
    "qdrant/mcp-server-qdrant",
    "chroma-core/chroma-mcp",
    "zilliztech/mcp-server-milvus",
    "weaviate/mcp-server-weaviate",
    "pinecone-io/pinecone-mcp",
    "elastic/mcp-server-elasticsearch",
    "redis/mcp-redis",
    "neo4j-contrib/mcp-neo4j",
    "FalkorDB/falkordb-mcpserver",
    "crystaldba/postgres-mcp",
    "modelcontextprotocol/servers",
    "timescale/pgai",
    "pgvector/pgvector",
    "opensearch-project/opensearch-mcp-server-py",
    "meilisearch/meilisearch",
    "typesense/typesense",
    "vespa-engine/vespa",
    # ===== RAG 平台 / 框架（自带 MCP 或 MCP 集成） =====
    "infiniflow/ragflow",
    "langgenius/dify",
    "HKUDS/LightRAG",
    "microsoft/graphrag",
    "run-llama/llama_index",
    "deepset-ai/haystack",
    "explodinggradients/ragas",
    "topoteretes/cognee",
    "mem0ai/mem0",
    "getzep/graphiti",
    "getzep/zep",
    "weaviate/Verba",
    "Cinnamon/kotaemon",
    "open-webui/open-webui",
    "Mintplex-Labs/anything-llm",
    "khoj-ai/khoj",
    "pathwaycom/pathway",
    "stanfordnlp/dspy",
    "embedchain/embedchain",
    "neuml/txtai",
    # ===== 文档解析 / 切分（RAG 前置） =====
    "docling-project/docling",
    "Unstructured-IO/unstructured",
    "opendatalab/MinerU",
    "chonkie-ai/chonkie",
    "microsoft/markitdown",
    "pymupdf/RAG",
    "VikParuchuri/marker",
    "VikParuchuri/surya",
    "run-llama/llama_parse",
    "firecrawl/firecrawl",
    # ===== 重排 / Embedding 服务 =====
    "AnswerDotAI/rerankers",
    "huggingface/text-embeddings-inference",
    "michaelfeil/infinity",
    "ollama/ollama",
    "vllm-project/vllm",
    "UKPLab/sentence-transformers",
    "FlagOpen/FlagEmbedding",
    "BAAI/bge-reranker-v2-m3",
    "mixedbread-ai/mgrep",
    "xlang-ai/ModelScope",
    # ===== 云厂商知识库检索 MCP =====
    "awslabs/mcp",
    "googleapis/mcp-toolbox",
    "Azure/azure-mcp",
    "cloudflare/mcp-server-cloudflare",
    # ===== 混合搜索 / 一体化检索 =====
    "devflowinc/trieve",
    "lancedb/lancedb",
    "lancedb/vectordb-recipes",
    "weaviate/weaviate",
    "qdrant/qdrant",
    "chroma-core/chroma",
    "milvus-io/milvus",
    "facebookresearch/faiss",
    "spotify/annoy",
    "nmslib/hnswlib",
    # ===== 记忆 / 个人知识库 =====
    "basicmachines-co/basic-memory",
    "doobidoo/mcp-memory-service",
    "MemTensor/MemOS",
    "memodb-io/memobase",
    "microsoft/kernel-memory",
    "Tencent/WeKnora",
    "zilliztech/deep-searcher",
    "nashsu/FreeAskInternet",
    # ===== 中文 / 国产 RAG =====
    "dataelement/bisheng",
    "netease-youdao/QAnything",
    "chatchat-space/Langchain-Chatchat",
    "THUDM/ChatGLM3",
    "modelscope/ms-swift",
    "infiniflow/infinity",
    "alibaba/spring-ai-alibaba",
    "langchain-ai/langchain",
    "langchain-ai/langgraph",
    # ===== MCP 聚合 / 目录（知识库分类） =====
    "punkpeye/awesome-mcp-servers",
    "modelcontextprotocol/registry",
    "smithery-ai/reference-servers",
]

def get(repo):
    repo = repo.strip().rstrip("/")
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
            "language": d.get("language"),
            "topics": (d.get("topics") or [])[:10],
            "description": (d.get("description") or "")[:200],
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
    time.sleep(0.3)

with open(r"C:/Users/Admin/WorkBuddy AI/2026-10-14-15-31-23/kb-rag-mcp/data/github-verified.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

ok = [x for x in out if "stars" in x]
print(f"\n=== OK {len(ok)} / {len(out)} ===")
print("FAILED:", [x["query"] for x in out if "error" in x])
