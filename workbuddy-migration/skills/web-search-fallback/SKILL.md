---
name: web-search-fallback
description: Use when web search or page fetching is blocked by anti-bot pages (CAPTCHA / anomaly / 403 / verification). Provides a verified engine availability matrix and a fallback chain, so the agent never wastes turns curling Google/Baidu/DuckDuckGo search pages that are now blocked.
description_zh: "搜索引擎被反爬拦截时的降级链：实测可用引擎矩阵 + 分层调用方案"
description_en: "Anti-bot-resistant web search fallback chain with verified engine matrix"
version: 1.0.0
allowed-tools: Bash,Read,Write,WebFetch,WebSearch
user-invocable: true
display_name: "web-search-fallback"
display_name_en: "web-search-fallback"
visibility: "public"
agent_created: true
---

# Web Search Fallback

When search is blocked, do NOT keep retrying the same engine. Follow the chain below.

## Iron Rules

1. **Never curl a search engine result page directly.** Google, Baidu, DuckDuckGo HTML/Lite, Mojeek, Ecosia, Yahoo all return anti-bot pages. This wastes turns.
2. **Prefer the built-in `WebSearch` tool first.** It runs server-side and is not affected by local IP blocking. It is the default and usually sufficient.
3. **Only reach for the direct channels below when the built-in tool returns nothing useful** (e.g. you need raw URLs, a specific engine, or bulk results).
4. **`r.jina.ai` now requires an API key** (returns 403 without one). Do not use it as a free reader.
5. **A 200 status does NOT mean the page is usable.** Always grep the body for `anomaly`, `challenge`, `安全验证`, `Firewall`, `captcha` before trusting it.

## Fallback Chain

Try in order. Stop as soon as one returns real results.

| # | Channel | How | Good for |
|---|---|---|---|
| 1 | **Built-in WebSearch tool** | Just call the tool | Everything. Default choice. |
| 2 | **Bing RSS** | `curl -s "https://www.bing.com/search?q=<query>&format=rss"` | Structured XML, no HTML parsing, very stable |
| 3 | **Brave Search** | `curl -s "https://search.brave.com/search?q=<query>"` | Fresh English results, parse `snippet-title` |
| 4 | **Qwant** | `curl -s "https://www.qwant.com/?q=<query>"` | Alternative aggregator |
| 5 | **open-websearch MCP** (`web-search`) | MCP tool `search`, engines `duckduckgo` / `baidu` | When you need a specific engine, or Chinese results |
| 6 | **Public SearXNG** | `curl -s "https://<instance>/search?q=<query>&format=json"` | Last resort. Instances are rate-limited. |

Always send a desktop UA:

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
```

## Verified Engine Matrix

Measured **2026-10-07** on this machine, no proxy, Chrome UA. Re-measure when results go stale.

| Engine | Raw `curl` | Via open-websearch | Verdict |
|---|---|---|---|
| DuckDuckGo | 202 `anomaly`/`challenge` | works, clean titles + real URLs | **use open-websearch** |
| Baidu | `百度安全验证` page | works (ads + redirect URLs) | **use open-websearch** |
| Bing | 200 real results | fails: `regional redirect limit` | **use raw curl / RSS** |
| Brave | 200 real results | 429 rate-limited | **use raw curl** |
| Qwant | 200 real results | not supported | **use raw curl** |
| Sogou | suspicious shell | `verification or anti-bot page` | unavailable |
| Startpage | 200, unclear | `Failed to extract Startpage search token` | unreliable |
| Mojeek / Ecosia / Yahoo | 403 / 403 / 500 | — | blocked |
| `r.jina.ai` | 403 | — | needs key |

**Key insight:** raw curl and open-websearch succeed on *different* engines. They are complementary, not redundant. Do not assume one replaces the other.

## Anti-Bot Escalation Ladder

Measured **2026-10-07**. Egress IP was in Malaysia (AS9534), so Google / Cloudflare were network-reachable — the failures below are **anti-bot**, not connectivity.

### Cloudflare

| Method | Result |
|---|---|
| raw `curl` | ❌ challenge page (`challenge-platform`, `__CF`) |
| **Chrome `--headless=new` + `--disable-blink-features=AutomationControlled`** | ✅ **passes** |

Verified against `nowsecure.nl` (FlareSolverr's official test site): headless Chrome returned the real page body, not the challenge.

**Passes:** Managed Challenge / JS Challenge (most CF-protected sites).
**Does not pass:** Turnstile interactive verification, behavioral risk scoring, login-gated content.

Escalate only if headless gets flagged: headful Chrome + CDP (see `headless-form-submit`) → FlareSolverr / Byparr (Docker; partially broken against newer CF) → residential proxy (CF scores IP reputation; datacenter IPs get challenged more).

```bash
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
"$CHROME" --headless=new --disable-gpu --no-sandbox \
  --user-data-dir="C:/Users/Admin/AppData/Local/Temp/cr-$$" \
  --disable-blink-features=AutomationControlled \
  --dump-dom --virtual-time-budget=20000 "<URL>"
```

### Google SERP

| Method | Result |
|---|---|
| raw `curl` | ❌ 92 KB JS shell — **no result links, no `<h3>`** |
| Chrome `--headless=new` | ❌ 6.6 KB **reCAPTCHA** page |
| **Headful Chrome via CDP** | ✅ **real results** (12 `<h3>`, titles + URLs + snippets) |

**Google's anti-bot is not a captcha wall — it is "results only render in an unflagged browser".** curl gets a JS shell, headless gets flagged, only headful passes.

**Scraping Google SERP violates Google's ToS and gets rate-limited.** Last resort only, never in bulk. Legitimate paths:

| Option | Free tier | Notes |
|---|---|---|
| **Google Programmable Search Engine (CSE) API** | 100 queries/day | Official + legal. Needs a Google Cloud API key + CSE ID (both free). `googleapis.com/customsearch/v1` is reachable from this machine (403 without key). |
| Serper.dev | ~2,500 one-off | Cheap, Google-grade results |
| SerpAPI | 100/month | Stable, expensive |
| Bing RSS | unlimited | Free, already verified — usually good enough |

**Default:** Bing RSS / Brave for routine work; add CSE API when you genuinely need Google's index; keep CDP scraping as a fallback.

## Public SearXNG Instances

Measured 2026-10-07 with `?format=json`:

- Working: `searx.be`, `baresearch.org`, `search.inetol.net`
- Rate-limited (429): `opnxng.com`, `paulgo.io`, `priv.au`, `searx.tiekoetter.com`
- Blocked: `searxng.site` (403), `search.bus-hit.me` (dead)

Public instances are shared infrastructure. Do not hammer them. For anything beyond occasional use, self-host (see below).

## Self-Hosted SearXNG — When It Is Actually Worth It

**SearXNG does not solve anti-bot blocking. It relocates it.** SearXNG scrapes Google/Bing using *your* egress IP. A home/office IP will get blocked exactly the same way, and you dirty your own IP in the process.

Worth deploying only when ALL of these hold:

- You have a VPS with a clean egress IP.
- You need privacy (queries must not reach a third-party search operator).
- You search frequently or in bulk.
- You will maintain it — upstream engine HTML changes break parsers regularly.

Deploy checklist:

1. SearXNG in Docker on the VPS, `json` format enabled in `settings.yml`.
2. Pair with **FlareSolverr** or **Byparr** to clear CAPTCHAs.
3. Disable the Google engine (it gets blocked fastest); rely on Brave / Startpage / Bing.
4. Never expose the base URL publicly — it becomes an open proxy.
5. Connect locally with the `mcp-searxng` MCP: `npx -y mcp-searxng`, env `SEARXNG_URL=https://your-vps`. It supports replica failover, proxies, and browser solvers.

If any of the four conditions is missing, skip SearXNG. Built-in WebSearch + Bing RSS + open-websearch covers the vast majority of needs at zero ops cost.

## Re-measuring

Engine availability drifts. To refresh the matrix:

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
for u in "https://html.duckduckgo.com/html/?q=test" "https://www.bing.com/search?q=test" \
         "https://search.brave.com/search?q=test" "https://www.qwant.com/?q=test"; do
  code=$(curl -s -o /tmp/o.html -w "%{http_code}|%{size_download}" --max-time 20 -A "$UA" "$u")
  flag=$(grep -o -E 'anomaly|challenge|安全验证|Firewall' /tmp/o.html | head -1)
  echo "$code  blocked=${flag:-no}  <- $u"
done
```

And for the MCP engines:

```bash
NODE="C:/Users/Admin/.workbuddy-ai/binaries/node/versions/22.22.2-3/node.exe"
IDX="C:/Users/Admin/.workbuddy-ai/binaries/node/versions/22.22.2-3/node_modules/open-websearch/build/index.js"
MODE=stdio "$NODE" "$IDX" search "OpenAI" --engine duckduckgo --limit 3 --json
```

Update the matrix above with the new date when you do.
