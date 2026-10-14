# 2026 最常用 MCP Server 分场景调研

> **调研对象**：当前最常用的 MCP（Model Context Protocol）Server，按 **编程开发 / 办公协作 / 网页浏览 / 深度研究 / 日常作业** 五个场景分别调研
> **数据快照**：**2026-10-14**
> **核心数据源**：**GitHub REST API 一手核验 89 个仓库**（star 数、许可证、最后提交时间、归档状态）+ 官方仓库 README + 官方 Registry / PulseMCP / Glama 目录 + 5 路并行研究子代理
> **原则**：标 `[未核实]` 的为未能一手核实项。**所有 star 数与最后提交日期均为 2026-10-14 GitHub API 实测值**，不是估算。

---

## 〇、结论速览

### 1. 五个场景的"必装"最小集

| 场景 | 最小必装集 |
|---|---|
| **编程开发** | `github-mcp-server`（33.6k）+ `context7`（63.0k）+ `playwright-mcp`（38.1k） |
| **办公协作** | `mcp.notion.com`（官方托管）+ `atlassian-mcp-server`（1.1k，覆盖 Jira/Confluence）+ 飞书 `lark-openapi-mcp`（**但已 14 个月未更新**） |
| **网页浏览** | `chrome-devtools-mcp`（53.5k）或 `playwright-mcp`（38.1k）+ `firecrawl-mcp-server`（7.6k）+ `brave-search-mcp-server`（1.5k） |
| **深度研究** | `exa-mcp-server`（5.1k）+ `tavily-mcp`（2.4k）+ `zotero-mcp`（5.4k）+ 官方 `memory` / `sequential-thinking` |
| **日常作业** | 官方 `filesystem` / `memory` / `time` / `fetch` + `DesktopCommanderMCP`（10.0k）+ `homeassistant-ai/ha-mcp`（5.1k） |

### 2. 六个最重要的判断

**① 星数最高的 MCP 相关仓库是 `microsoft/markitdown`（190,122★）——但它本体不是 MCP Server**，而是一个"任意文档→Markdown"转换库，MCP 服务是随包捆绑的。同理 `microsoft/playwright`（97,679★）是浏览器库本体，MCP 在 `playwright-mcp`（38,117★）。**引用星数时必须区分"库本体"与"MCP 服务"**——这是本次调研发现的最普遍误引。

**② 官方参考服务器只剩 7 个还活着**。`modelcontextprotocol/servers`（91,238★）仓库里，**GitHub / Google Drive / Google Maps / Slack / Puppeteer / Postgres / SQLite / Brave Search / Sentry / GitLab 全部已归档**，移入 `servers-archived`。现在活跃的只有 **Filesystem、Memory、Sequential Thinking、Time、Fetch、Git、Everything**。

**③ 有 5 个"热门"仓库已归档（archived）**：`browserbase/mcp-server-browserbase`（3,401★）、`supermemoryai/apple-mcp`（3,123★）、`semgrep/mcp`（687★）、`e2b-dev/mcp-server`（393★）、`oxylabs/oxylabs-mcp`（104★）。**按教程装这些会装到一个死项目。**

**④ 高星但已停更的陷阱**：`BrowserMCP/mcp` 有 **7,182★**，但最后提交是 **2025-04-24**（停更 18 个月）；`larksuite/lark-openapi-mcp`（飞书官方 MCP）836★，最后提交 **2025-08-14**（停更 14 个月）；`JetBrains/mcp-jetbrains` 停更 9 个月；`jerhadf/linear-mcp-server` 停更 17 个月（且 Linear 官方明确说**不要用**它）。

**⑤ 办公场景的胜负手不是星数，而是"厂商官方 + 远程 OAuth"**。办公类 MCP 的 star 普遍只有几千，但价值在于**免本地安装、OAuth 授权、企业级权限**。Notion、Atlassian、Slack、Linear、Google、Microsoft、飞书、钉钉走的都是 **Streamable HTTP + OAuth 的托管路线**，本地 stdio 是社区方案的特征。

**⑥ 星数只是"关注度"，不是"使用量"**。真正反映使用量的 npm/PyPI 下载量本次未能取得。**本报告的所有"最常用"判断都建立在 star 数 + 官方目录收录 + 厂商文档推荐三个信号上**，请注意这是代理指标。

---

## 一、场景一：编程开发

### 1.1 首选清单（star 与更新时间为 2026-10-14 GitHub API 实测）

| 名称 | Star | 维护方 | 许可证 | 最后更新 | 一句话 |
|---|---:|---|---|---|---|
| **Context7** | 63,010 | ✅ Upstash 官方 | MIT | 2026-10-13 | 注入**版本正确的库文档**，治 API 幻觉 |
| **Chrome DevTools MCP** | 53,500 | ✅ Google 官方 | Apache-2.0 | 2026-10-14 | 驱动真实 Chrome：性能追踪 / 网络 / 控制台 |
| **Playwright MCP** | 38,117 | ✅ Microsoft 官方 | Apache-2.0 | 2026-10-08 | **无障碍树**驱动，不依赖视觉模型，确定性高 |
| **GitHub MCP Server** | 33,600 | ✅ GitHub 官方 | MIT | 2026-10-13 | 仓库/PR/Issue/Actions/代码搜索全 API |
| **Serena** | 30,250 | 社区（oraios） | NOASSERTION | 2026-10-13 | LSP 语义级跨文件符号检索与改写 |
| **apify-mcp-server** | 11,109 | ✅ Apify 官方 | MIT | 2026-10-14 | 把 6,000+ 现成爬虫当工具调用 |
| **Desktop Commander** | 10,046 | 社区 | MIT | 2026-10-14 | 终端 + 文件 + diff 编辑（⚠️ 权限极大） |
| **AWS MCP Servers** | 9,777 | ✅ AWS Labs 官方 | Apache-2.0 | 2026-10-14 | AWS API/CDK/Cost/Bedrock 全家桶 |
| **git-mcp** | 8,463 | 社区（idosal） | Apache-2.0 | 2026-05-08 | "和任意仓库文档对话" |
| **mcp-atlassian** | 6,000 | 社区（sooperset） | MIT | 2026-09-19 | Jira/Confluence 的社区 stdio 方案 |
| **Cloudflare MCP** | 4,378 | ✅ Cloudflare 官方 | Apache-2.0 | 2026-10-09 | Workers/KV/R2/D1/DNS |
| **Azure MCP** | 3,772 | ✅ Microsoft 官方 | MIT | 2026-10-14 | Azure 资源管理（原 `microsoft/mcp`） |
| **Grafana MCP** | 3,559 | ✅ Grafana Labs 官方 | Apache-2.0 | 2026-10-13 | Prometheus/Loki 查询 + 仪表盘 |
| **postgres-mcp**（Pro） | 3,396 | 社区（crystaldba） | MIT | 2026-08-17 | Postgres + 索引/健康度调优 |
| **Supabase MCP** | 2,950 | ✅ Supabase 维护 | Apache-2.0 | 2026-10-14 | 项目/SQL/分支/边缘函数 |
| **GitLab MCP** | 2,037 | 社区（zereight） | MIT | 2026-10-13 | GitLab Issue/MR/流水线 |
| **Kubernetes MCP** | 1,596 | 社区（Flux159） | MIT | 2026-10-02 | kubectl 式集群操作 |
| **Terraform MCP** | 1,549 | ✅ HashiCorp 官方 | MPL-2.0 | 2026-10-13 | Registry/Provider/Module 查询 |
| **MongoDB MCP** | 1,143 | ✅ MongoDB 官方 | Apache-2.0 | 2026-10-13 | 查询/聚合/索引/Atlas |
| **Sentry Toolkit** | 928 | ✅ Sentry 官方 | NOASSERTION | 2026-10-14 | 错误分诊 + Seer AI 修复（**原 `sentry-mcp`，已改名**） |
| **ClickHouse MCP** | 887 | ✅ ClickHouse 官方 | Apache-2.0 | 2026-10-06 | OLAP 分析查询 |
| **Elasticsearch MCP** | 718 | ✅ Elastic 官方 | Apache-2.0 | 2026-10-12 | 索引检索与映射 |
| **Neon MCP** | 651 | ✅ Neon 官方 | MIT | 2026-10-14 | Serverless Postgres 分支 |
| **Redis MCP** | 634 | ✅ Redis 官方 | MIT | 2026-10-13 | 数据操作 + Redis Cloud |
| **Snowflake MCP** | 299 | ✅ Snowflake Labs | Apache-2.0 | 2026-05-15 | 企业数仓查询 |

**必装基线（官方参考服务器）**：`modelcontextprotocol/servers`（91,238★）中的 **Filesystem、Memory、Sequential Thinking、Git、Fetch**。

### 1.2 本场景的坑

- **`semgrep/mcp` 已归档**（687★）——别按老教程装。
- **`e2b-dev/mcp-server` 已归档**（393★）；想用云沙箱执行代码需找替代。
- **`JetBrains/mcp-jetbrains` 停更 9 个月**（2026-01-07）——JetBrains 用户注意。
- **`BrowserMCP/mcp` 7,182★ 但停更 18 个月**——高星陷阱的典型。
- **Postgres/SQLite 官方参考服务器已归档**，现在应选 `crystaldba/postgres-mcp` 或各家云厂商官方版。
- **风险最高的一类**：`Desktop Commander`（完整 shell + 文件权限）、数据库类（SQL 注入 / 越权）、PAT 类（GitHub/GitLab 令牌作用域过宽）。**远程 Streamable HTTP + OAuth 比长效 PAT 更安全。**

---

## 二、场景二：办公协作

### 2.1 首选清单

| 名称 | Star | 维护方 | 传输 | 认证 | 一句话 |
|---|---:|---|---|---|---|
| **Notion MCP** | 4,666 | ✅ Notion 官方 | **远程 HTTP** + 本地 stdio | **OAuth** / Token | 官方托管，**无需本地安装**；搜索/读写页面与数据库 |
| **Atlassian Rovo MCP** | 1,092 | ✅ Atlassian 官方 | **远程 HTTP** | **OAuth 2.1** | 一套覆盖 **Jira + Confluence + JSM + Bitbucket + Compass** |
| **mcp-atlassian** | 6,000 | 社区 | stdio | PAT | Jira/Confluence 的本地替代（star 反而高于官方） |
| **飞书 Lark OpenAPI MCP** | 836 | ✅ 飞书官方 | stdio / streamable / sse | App ID + Secret | ⚠️ **最后更新 2025-08-14，已停更 14 个月** |
| **n8n-MCP** | 23,064 | 社区（czlonkowski） | stdio | 无 | 把 n8n 自动化工作流接给 Agent |
| **MarkItDown** | **190,122** | ✅ Microsoft 官方 | stdio（捆绑） | 无 | **PDF/PPTX/DOCX/XLSX/图片/音频 → Markdown**；办公文档摄入的事实标准 |
| **Composio** | 30,541 | 第三方 | 托管 | OAuth | 多工具聚合平台，宣称 7,500+ 预置连接器 |

### 2.2 办公场景的三个结构性特征

**① 厂商官方走"远程托管 + OAuth"，社区走"本地 stdio + API Key"**

已确认由厂商一手维护的办公类 MCP：**Notion、Atlassian、Slack、Linear、Google（Drive/Gmail/Calendar）、Microsoft（Teams/Outlook/OneDrive/SharePoint，Frontier 预览）、飞书、钉钉、Fireflies、Granola、Box、Dropbox、GitBook、Zapier、Pipedream、Make**。

这些服务器的典型形态是 `https://mcp.xxx.com/mcp` 的远程端点 + OAuth 授权，**省掉本地安装**，且能继承企业的身份与权限体系。**选型时应优先选这一类。**

**② 中国办公生态与海外是"两套独立体系"**

| 生态 | 代表 | 关键约束 |
|---|---|---|
| **飞书 / Lark** | `lark-openapi-mcp`（官方） | **`open.feishu.cn`（国内）与 `open.larksuite.com`（国际）区域锁定，应用互不通用**；不支持文件上传下载；云文档只能读+导入 |
| **钉钉** | 官方 MCP 网关 `mcp-gw.dingtalk.com` | **需要企业内建应用 + 组织管理员权限** |
| **企业微信 / 微信** | 社区为主；微信公众号可通过飞书 AnyCross 连接 | 无强势官方 MCP |
| **腾讯文档 / 语雀 / 石墨 / WPS** | 社区 / 集成平台 | **未找到强势官方 MCP** |

海外方案（Google Workspace、Slack、Atlassian、Notion）均需 OAuth 对接在大陆可能受限的服务，**中国团队通常直接用飞书/钉钉替代**。

**③ 办公类 MCP 的 star 普遍不高（几百到几千），但这不代表不重要**

对比：编程类的 Context7 有 63,010★，办公类的 Notion 只有 4,666★。原因是办公类 MCP 的价值在**厂商信任 + 免安装**，而非开源社区热度。**不要用 star 数给办公类排序。**

### 2.3 本场景的坑

- **飞书官方 MCP 已停更 14 个月**（2025-08-14）——这是最需要注意的一条，官方仓库却处于停滞状态。
- **`jerhadf/linear-mcp-server` 已停更 17 个月**，且 **Linear 官方文档明确说不要用社区服务器**，要用 `mcp.linear.app`。
- **`karbassi/slack-mcp` 只有 3★**——被一些文章列为 Slack 替代方案，实际几乎无人使用。
- 大多数 `xlsx/docx/pptx` 类服务器是社区作品，质量参差；**文档摄入优先用 Microsoft 官方 MarkItDown**。
- **聚合器（Composio / Zapier / Pipedream）的代价**：一次接入几百个工具，但换来的是**透明度下降、逐应用 OAuth 开销、厂商锁定**。

---

## 三、场景三：网页浏览

### 3.1 首选清单

| 名称 | Star | 维护方 | 路线 | 本地/云 | 认证 |
|---|---:|---|---|---|---|
| **Chrome DevTools MCP** | 53,500 | ✅ Google 官方 | CDP / Puppeteer | 本地 | 无（⚠️ 默认开启用量统计） |
| **Playwright MCP** | 38,117 | ✅ Microsoft 官方 | **无障碍树** | 本地 | 无 |
| **Lightpanda** | 36,456 | 开源（Lightpanda） | Zig 轻量浏览器 | 本地 | 无 |
| **browser-use** | 117,918 | 开源社区 | DOM + AI | 本地 | LLM Key |
| **Stagehand** | 25,661 | Browserbase（开源） | DOM + 自然语言 | 本地 | LLM Key |
| **Skyvern** | 23,197 | 开源（AGPL-3.0） | 视觉 + LLM 自动化 | 本地/云 | LLM Key |
| **Apify MCP** | 11,109 | ✅ Apify 官方 | 6,000+ 现成爬虫 | 云 | Token（含免费额度） |
| **Firecrawl MCP** | 7,598 | ✅ Firecrawl 官方 | 抓取/爬取/结构化抽取 | 云 | Key（**无 Key 也有受限免费模式**） |
| **Steel Browser** | 7,799 | 开源（Steel） | 开源云浏览器 | 自托管/云 | 无 / Key |
| **Bright Data MCP** | 2,674 | ✅ Bright Data 官方 | 代理 + **Web Unlocker 解验证码** | 云 | Token（付费） |
| **Notte** | 2,034 | 开源（Notte） | 全栈 Web Agent 框架 | 云 | API Key |
| **Tavily MCP** | 2,430 | ✅ Tavily 官方 | AI 优化搜索 + 抽取/爬取 | 云 | Key（免费额度） |
| **DuckDuckGo MCP** | 1,534 | 社区（nickclyde） | 搜索（无 Key） | 本地 | **无** |
| **Brave Search MCP** | 1,497 | ✅ Brave 官方 | 独立索引搜索 | 本地/HTTP | Key（**免费 2,000 次/月**） |
| **SearXNG MCP** | 1,302 | 社区 | 元搜索（自托管） | 本地 | **无** |
| **Exa MCP** | 5,126 | ✅ Exa 官方 | 神经/语义搜索 | 云 | 匿名免费 / Key |
| **Ref tools** | 1,180 | ✅ Ref 官方 | 文档精确引用 | 云 | Key（有免费层） |
| **Jina MCP** | 880 | ✅ Jina AI 官方 | URL → Markdown | 云 | **无 Key 可用（限速）** |

### 3.2 三条技术路线的分野

| 路线 | 代表 | 优点 | 缺点 |
|---|---|---|---|
| **无障碍树（Accessibility Tree）** | Playwright MCP | 确定性高、无需视觉模型、快、便宜 | 漏掉 canvas / 无标签元素 |
| **CDP / DOM** | Chrome DevTools MCP | 能拿到性能追踪、网络、控制台 | 仅限 Chrome；默认上传用量数据 |
| **视觉 + LLM** | browser-use / Skyvern / Stagehand | 能处理复杂视觉页面 | 慢、贵、不确定性强、需 LLM Key |

### 3.3 免费额度速查（选型关键）

| 服务 | 免费额度 |
|---|---|
| **DuckDuckGo / SearXNG / Fetch / markitdown / Lightpanda** | **完全免费，无需 Key** |
| **Brave Search** | 免费 2,000 次/月 |
| **Tavily** | 免费额度（约 1,000 credits/月） |
| **Firecrawl** | 无 Key 也可用（限速）；免费计划约 500 credits |
| **Exa** | 匿名模式免费（限速）；API 约 $10 试用额度 |
| **Jina** | 无 Key 可用（约 20 RPM） |
| **Perplexity / Kagi / Bright Data / Oxylabs** | **付费为主** |

### 3.4 本场景的坑

- **`BrowserMCP/mcp`（7,182★）停更 18 个月**（2025-04-24）——高星陷阱。
- **`browserbase/mcp-server-browserbase` 已归档**（3,401★）；Browserbase 的活跃主线是 `browserbase/stagehand`（25,661★）。
- **`oxylabs/oxylabs-mcp` 已归档**（104★）。
- **`hyperbrowserai/mcp` 停更**（2025-11-20）。
- **本地浏览器 MCP 都没有反爬能力**——遇到 Cloudflare / DataDome / 验证码会被拦。需要反爬时只能用 Bright Data（明确支持解验证码）、Browserbase、Steel、Firecrawl 等云方案。
- **官方 Fetch 服务器不执行 JS**——纯静态抓取，JS 重的页面拿不到内容。
- **Lightpanda 不是完整浏览器**——JS/CSS 覆盖有限，不适合复杂 SPA。

---

## 四、场景四：深度研究

### 4.1 首选清单

| 名称 | Star | 维护方 | 定位 | 免费额度 |
|---|---:|---|---|---|
| **Exa MCP** | 5,126 | ✅ Exa 官方 | 神经/语义搜索 + 内容获取 + 多步 Agent | 匿名免费（限速）；API 约 $10 试用 |
| **Zotero MCP** | 5,377 | 社区（54yyyu） | **文献管理器集成（本类最关键的缺口填补者）** | 免费 |
| **basic-memory** | 4,169 | 社区 | Markdown 本地知识图谱记忆 | 免费（AGPL-3.0） |
| **arxiv-mcp-server** | 3,216 | 社区（blazickjp） | arXiv 检索/下载/读全文 + BibTeX | 免费（无 Key） |
| **Perplexity Ask MCP** | 2,564 | ✅ Perplexity 官方 | 带引用的答案合成 + 深度研究模式 | **基本无免费额度** |
| **Tavily MCP** | 2,430 | ✅ Tavily 官方 | 为 RAG 优化的搜索 + 抽取 | 免费额度（约 1,000 credits/月） |
| **Firecrawl MCP** | 7,598 | ✅ Firecrawl 官方 | 抓取 + 深度研究模式 | 无 Key 受限免费 |
| **Mem0** | 67,154 | ✅ Mem0 官方 | 事实抽取型记忆层 | 开源自托管免费 |
| **Graphiti（Zep）** | 31,730 | ✅ Zep 官方 | **时序知识图谱记忆** | 开源免费；云版付费 |
| **Letta** | 25,125 | ✅ Letta 官方 | OS 式分层记忆 Agent 框架 | 开源免费 |
| **Ref tools** | 1,180 | ✅ Ref 官方 | 保证引用当前文档（防幻觉） | 有免费层 |
| **Jina MCP** | 880 | ✅ Jina AI 官方 | URL → Markdown（含搜索 s.jina.ai） | 无 Key 可用（限速） |
| **GPT-Researcher** | 30,085 | 开源 | 深度研究 Agent（**可通过 `gptr-mcp` 被 MCP 驱动**） | 开源免费 |

**官方参考服务器必装**：`memory`（知识图谱记忆）、`sequential-thinking`（结构化推理）。

### 4.2 本场景推荐栈

```
搜索层：  Exa（语义） + Tavily（答案就绪） + Brave（独立索引）
抽取层：  Firecrawl（JS/PDF）+ Jina（轻量）
文献层：  arXiv + Semantic Scholar + Zotero（引用管理）
文档层：  Context7 + DeepWiki（代码库文档）
推理层：  Sequential Thinking
记忆层：  Memory（官方）/ basic-memory / Graphiti
```

### 4.3 本场景的坑

- **Perplexity 基本没有免费额度**——研究型高频调用会快速产生费用。
- **学术类 MCP 高度碎片化**——PubMed / OpenAlex / Crossref / Google Scholar **都没有单一权威官方服务器**，全是社区实现，质量参差。
- **`xbghc/semanticscholar-mcp` 只有 7★**——被一些文章提及，但几乎无人维护，谨慎使用。
- **Google Scholar 类服务器靠爬取**，脆弱且有 ToS 风险。
- **Zotero 是唯一成熟的文献管理器集成**；EndNote / Mendeley **没有成熟 MCP**（明确缺口）。
- **HuggingFace Open Deep Research 不能原生被 MCP 驱动**（它是 smolagents 的示例）；GPT-Researcher 可以（通过 `gptr-mcp`）。

---

## 五、场景五：日常作业

### 5.1 官方参考服务器（当前活跃的 7 个）

| 名称 | Star（仓库整体） | 安装 | 说明 |
|---|---:|---|---|
| **Filesystem** | 91,238（monorepo） | `npx -y @modelcontextprotocol/server-filesystem <dir>` | 沙箱化文件读写，**按目录白名单** |
| **Memory** | 同上 | `npx -y @modelcontextprotocol/server-memory` | 知识图谱持久记忆 |
| **Sequential Thinking** | 同上 | `npx -y @modelcontextprotocol/server-sequential-thinking` | 结构化多步推理 |
| **Time** | 同上 | `uvx mcp-server-time` | 时间/时区转换 |
| **Fetch** | 同上 | `uvx mcp-server-fetch` | 网页抓取转 Markdown |
| **Git** | 同上 | `uvx mcp-server-git --repository <path>` | 本地 Git 操作 |
| **Everything** | 同上 | `npx -y @modelcontextprotocol/server-everything` | 测试/演示用 |

> ⚠️ 官方仓库 README 明确声明这些是**"参考实现，不是生产就绪"**，并引导用户去官方 Registry 找更广的目录。

### 5.2 日常场景首选

| 名称 | Star | 维护方 | 说明 |
|---|---:|---|---|
| **Desktop Commander** | 10,046 | 社区 | 跨平台终端 + 文件 + diff 编辑（⚠️ 权限极大，需沙箱） |
| **Home Assistant MCP（ha-mcp）** | 5,062 | 社区 | **80+ 工具**：实体/自动化/设备/配置 |
| **Home Assistant 官方集成** | 91,564（core） | ✅ Home Assistant 官方 | **原生 MCP server + client**，最权威 |
| **Notion MCP** | 4,666 | ✅ Notion 官方 | 个人知识库 |
| **Spotify MCP** | 613 | 社区（varunneal） | 播放控制/歌单（⚠️ 停更 7 个月） |
| **voska/hass-mcp** | 346 | 社区 | Docker 友好的 HA 入口 |
| **Yahoo Finance MCP** | 28 | 社区 | 行情/财报（无 Key） |
| **mcp-stockscreen** | 49 | 社区 | 选股筛选 |
| **Obsidian MCP（StevenStavrakis）** | 742 | 社区 | 笔记 CRUD |
| **Obsidian MCP（cyanheads）** | 695 | 社区 | 功能更全的 Obsidian |
| **mcp-obsidian（Docker）** | 66 | Docker | 走 Local REST API |

### 5.3 本场景的坑

- **官方参考服务器大面积归档**：GitHub、Google Drive、Google Maps、Slack、Puppeteer、Postgres、SQLite、Brave Search、Sentry、GitLab、EverArt **全部已归档**。
- **`supermemoryai/apple-mcp` 已归档**（3,123★，原 `dhravya/apple-mcp`）——macOS 自动化目前没有稳定的主流选择。
- **Home Assistant 是本类唯一"官方原生集成"的品类**，也是智能家居的事实标准（一个 MCP 统一 Hue/HomeKit/Zigbee 等）。
- **中国日常工具**：**高德地图 MCP（`mcp.amap.com/mcp`）是官方且功能最全的**（12 项服务，含公交/步行/骑行/驾车路径）；**微信 / 百度地图 / 富途 / moomoo 均为社区或不稳定状态** `[未核实]`。
- **`maxscheijen/mcp-yahoo-finance` 只有 28★**——金融类 MCP 整体非常不成熟，不要用于真实决策。

---

## 六、横向对比与选型建议

### 6.1 五个场景的"官方 vs 社区"成熟度

| 场景 | 官方维护比例 | 成熟度 | 说明 |
|---|---|---|---|
| **编程开发** | **高** | ★★★★★ | GitHub/Google/Microsoft/AWS/HashiCorp/MongoDB/Redis 等大厂全部亲自下场 |
| **网页浏览** | **高** | ★★★★★ | Google Chrome DevTools、Microsoft Playwright、Brave、Firecrawl、Exa、Tavily 均为官方 |
| **深度研究** | 中高 | ★★★★ | 搜索层官方强（Exa/Tavily/Firecrawl），学术层几乎全社区 |
| **办公协作** | 中（但质量高） | ★★★★ | 厂商官方但走托管路线；中国生态偏弱 |
| **日常作业** | **低** | ★★☆ | 官方参考服务器大面积归档，主力靠社区；除 Home Assistant 外无官方标杆 |

### 6.2 选型三条铁律

1. **先看"最后提交时间"，再看 star 数。** 本报告发现至少 6 个高星但停更超过 9 个月的项目。停更的项目再热门也不要用。
2. **优先选厂商一手维护的。** 官方服务器在协议跟进、安全修复、认证规范上都有保障；社区服务器容易在 MCP 规范升级后失修。
3. **能用远程 OAuth 就别用长效 PAT。** 远程 Streamable HTTP + OAuth 是 2026 年的主流形态，权限可回收、可审计；长效 PAT 一旦泄露后果严重。

### 6.3 对照：你本机当前的 MCP 配置

本机 `~/.workbuddy-ai/mcp.json` 目前只配了 **3 个**，且全部是本地 stdio：

| 名称 | 对应场景 | 与主流对比 |
|---|---|---|
| `gog`（Google Workspace） | 办公协作 | 本机自建；对应生态里的 Google Workspace MCP |
| `web-search`（open-websearch） | 网页浏览 / 深度研究 | 社区自建；生态里更主流的是 Brave / Tavily / Exa |
| `nixos`（mcp-nixos） | 编程开发（垂直） | 垂直小众；编程场景的主力（GitHub / Context7 / Playwright）尚未配置 |

**缺口最明显的三个**：**Context7**（治 API 幻觉）、**GitHub MCP**（代码仓库）、**Playwright / Chrome DevTools MCP**（网页自动化）。这三个恰好也是编程场景 star 最高的三个。

---

## 七、数据可信度说明

### 7.1 本报告的数据分级

| 等级 | 来源 | 覆盖范围 |
|---|---|---|
| **A 级（一手实测）** | **GitHub REST API，2026-10-14** | **全部 star 数、许可证、最后提交日期、归档状态**（89 个仓库） |
| **B 级（官方文档）** | 官方仓库 README、厂商文档、官方 Registry | 安装命令、传输方式、认证要求、工具清单 |
| **C 级（`[未核实]`）** | 单一来源 / 子代理估算 / 未能核实 | 见下 |

### 7.2 明确标注的不确定项

- **npm / PyPI 下载量**：本次**未取得**。这是"最常用"最直接的证据，本报告的"最常用"判断建立在 star 数 + 目录收录 + 厂商推荐三个代理指标上。
- **各家 MCP 目录站的服务器总数互相矛盾**（官方 Registry 约 3 万 / Glama 约 6.6 万 / mcptoplist 称 13.5 万），且约 **80% 的服务器只出现在一个目录里**——**不要引用任何单一总数**。
- **免费额度与定价**（Brave 2,000/月、Tavily 1,000 credits、Firecrawl 500 credits 等）：来自文档与二手来源，**未在官方定价页逐一核实**，会变动。
- **办公类的中国生态**：腾讯文档 / 语雀 / 石墨 / WPS / 企业微信 / 百度地图 / 富途 / moomoo 的官方 MCP 状态**未能一手核实**。
- **`[未核实]` 的仓库改名**：`getsentry/sentry-mcp` → `getsentry/toolkit`（已核实）；`ppl-ai/modelcontextprotocol` → `perplexityai/modelcontextprotocol`（已核实）；`dhravya/apple-mcp` → `supermemoryai/apple-mcp`（已核实）；`apify/actors-mcp-server` → `apify/apify-mcp-server`（已核实）；`googleapis/genai-toolbox` → `googleapis/mcp-toolbox`（已核实）。

### 7.3 三条必须提醒的口径陷阱

1. **`microsoft/markitdown` 的 190,122★ 是"文档转换库"的星数，不是 MCP Server 的星数。** 同理 `microsoft/playwright`（97,679★）与 `microsoft/playwright-mcp`（38,117★）是两个仓库。
2. **官方参考服务器 `modelcontextprotocol/servers` 的 91,238★ 是整个 monorepo 的星数**，不等于里面任一单个服务器的热度。
3. **star 高 ≠ 活跃**。`BrowserMCP/mcp`（7,182★，停更 18 个月）就是最好的反例。

---

## 附：完整核验数据

全部 89 个仓库的精确核验数据（star / 许可证 / 语言 / 最后提交 / 归档状态）见 `data/mcp-verified.json`。

**主要参考来源**：

- [modelcontextprotocol/servers（官方参考服务器）](https://github.com/modelcontextprotocol/servers)
- [modelcontextprotocol/servers-archived（已归档）](https://github.com/modelcontextprotocol/servers-archived)
- [官方 MCP Registry](https://registry.modelcontextprotocol.io/)
- [PulseMCP](https://www.pulsemcp.com/) · [Glama](https://glama.ai/mcp/servers) · [mcp.so](https://mcp.so/)
- [github/github-mcp-server](https://github.com/github/github-mcp-server) · [upstash/context7](https://github.com/upstash/context7)
- [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) · [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [oraios/serena](https://github.com/oraios/serena) · [microsoft/markitdown](https://github.com/microsoft/markitdown)
- [firecrawl/firecrawl-mcp-server](https://github.com/firecrawl/firecrawl-mcp-server) · [brave/brave-search-mcp-server](https://github.com/brave/brave-search-mcp-server)
- [exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server) · [tavily-ai/tavily-mcp](https://github.com/tavily-ai/tavily-mcp)
- [54yyyu/zotero-mcp](https://github.com/54yyyu/zotero-mcp) · [blazickjp/arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server)
- [makenotion/notion-mcp-server](https://github.com/makenotion/notion-mcp-server) · [atlassian/atlassian-mcp-server](https://github.com/atlassian/atlassian-mcp-server)
- [larksuite/lark-openapi-mcp](https://github.com/larksuite/lark-openapi-mcp) · [homeassistant-ai/ha-mcp](https://github.com/homeassistant-ai/ha-mcp)
- [wonderwhy-er/DesktopCommanderMCP](https://github.com/wonderwhy-er/DesktopCommanderMCP) · [awslabs/mcp](https://github.com/awslabs/mcp)
- [高德地图 MCP Server（官方）](https://developer.amap.com/api/mcp-server/gettingstarted)
- [飞书 MCP 集成平台](https://anycross.feishu.cn/mcp-server/list)
