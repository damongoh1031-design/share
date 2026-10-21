# 2026 年「CLI 替代 MCP」的 GitHub 实况盘点

**调研时间：2026 年 10 月 21 日** ｜ star 与更新时间为 GitHub API 实时查询快照

## 摘要

"CLI 替代 MCP"在 2026 年已经不是口号，而是分成了三条互不相同的技术路线，很多人把它们混为一谈。第一条是**桥接层**：把任意 MCP server（甚至 OpenAPI、GraphQL）在运行时转成 CLI 命令，代表项目是 `knowsuchagency/mcp2cli`（2.4k star）和 `openclaw/mcporter`（5.1k star）。第二条是 **Code Mode**：不转 CLI，而是给 agent 一个代码沙箱，让它写代码 import 工具，代表是 `universal-tool-calling-protocol/code-mode`（1.6k star）和 Cloudflare 已产品化的 `codemode`。第三条是**厂商官方 CLI 上位**，也是这一轮最被低估的变化：飞书 `larksuite/cli` 已经 17.7k star、200+ 命令、自带 24 个 Agent Skills，钉钉 `dws` 3.7k star、159 条命令，企业微信 `wecom-cli` 3.2k star，微软 `playwright-cli` 14.4k star，Cloudflare 干脆用全新的 `cf` CLI 取代自家 Wrangler。真正被验证的收益是上下文成本：mcp2cli 自测在 120 工具/25 轮场景下从 362,350 token 降到 5,181，降幅 99%。代价是鉴权流程被压平、结构化输出退化、权限粒度变粗。

## 一、先分清三条路线

这三条路线经常被中文文章混为一谈，但它们丢的东西不一样。

**桥接层（MCP → CLI）**把工具 schema 转成命令行参数，agent 通过 `--help` 按需发现。它省的是"把全部 schema 预加载进上下文"的那份开销，保留了子进程隔离，但把 JSON-RPC 的语义压成了退出码加 stdout。

**Code Mode（MCP → 代码）**保留工具的可编程性，让 agent 写一段 TypeScript 把多个工具调用串起来，只在沙箱里跑。它省的是"每一轮工具往返都要重新灌一遍中间结果"的开销，且数据不经过模型。Cloudflare 的说法是"AI 写不出泄露密钥的代码"，因为凭据在 supervisor 侧注入、沙箱默认断网。

**厂商官方 CLI** 则是另一个维度：不是把别人的 MCP 转过来，而是厂商自己判断"我的用户主要是 agent，那就直接给 agent 一个 CLI"。

## 二、桥接层：GitHub 上的真项目

| 项目 | Star | 最近更新 | 技术路线 | 一句话 |
|---|---|---|---|---|
| `openclaw/mcporter` | 5,079 | 2026-10-20 | MCP → TypeScript Proxy / 可生成独立 CLI | 进程内 `await proxy.toolName({...})`，不是代码生成 |
| `knowsuchagency/mcp2cli` | 2,423 | 2026-10-12 | MCP / OpenAPI / GraphQL → CLI，运行时零构建 | 覆盖面最广，量化数据最扎实 |
| `apify/mcpc` | 1,063 | 2026-10-20 | TS 编写的 MCP CLI 客户端 | 协议覆盖最全（prompts、tasks、skills、OAuth、x402） |
| `postrv/forgemax` | 155 | 2026-10-21 | Rust + deno_core，固定 search + execute 两个工具 | 工具集再大也只占约 1,100 token |

`mcporter` 的机制需要澄清一下，因为很多二手文章写错了。它**不是**在运行时把工具写成 `.ts` 文件再让 agent `import`。真正的做法是 `createServerProxy()`——把 MCP 工具名映射成 camelCase 可调用属性的**动态 Proxy 对象**，在进程内直接调用。想要静态类型得另外跑 `mcporter emit-ts` 生成 `.d.ts`。CLI 用法是完整的：`mcporter list <url> --brief` 打印 TS 风格签名，`mcporter call <url>.<tool> k=v` 直接调，`mcporter auth` 管 OAuth。最简一条命令：`npx mcporter list https://mcp.context7.com/mcp --brief`。注意作者**没有给任何 token 量化数据**，中文圈流传的"mcporter 省 X%"都找不到一手出处。

`mcp2cli` 的"zero codegen、runtime"也不是字面意思上的零反射——它不落地任何文件、不改你的代码，但运行时确实在内存里用 JSON Schema 动态构建 argparse 子命令。它的真正差异点是**覆盖面**：`--mcp`、`--mcp-stdio`、`--spec`（OpenAPI）、`--graphql` 四选一，同一套 `--list`、`--auth-header`、`--oauth`、`--json` 语义。所以它不只是 MCP 的替代品，而是一个通用的"API → CLI"层。

这组数据是目前全篇最可信的一组（作者自测 + 测试套件，cl100k_base 计数）：30 工具/10 轮从 36,310 降到 1,734（95.2%）；80 工具/20 轮从 193,360 降到 3,897（98%）；120 工具/25 轮从 362,350 降到 5,181（99%）。但作者自己承认三个前提：基线假设每轮全量重发 schema（没算 prompt caching）、假设 120 个工具里只用 10 个、不含工具输出的 token。而且 OpenAPI 只有 5 个端点的场景降幅只有 68%——工具少的时候固定开销会吃掉收益。

## 三、Code Mode：Anthropic 和 Cloudflare 那条线的落地

Anthropic 在 2025-11 提出的 "Code execution with MCP" 在 2026 年有了开源实现，但不是最有名的那个。

`mcp-use`（很多人误以为是这条路线）其实是 MCP Apps 全栈框架，README 里通篇没有 code mode。真正的实现是 `universal-tool-calling-protocol/code-mode`（1,601 star，2026-08-25，MPL-2.0）：`npm i @utcp/code-mode`，把 MCP/HTTP/File/CLI 四种源注册成命名空间，`callToolChain(code)` 在 isolated-vm 里跑 TypeScript，另有 `@utcp/code-mode-cli` 和 `-mcp` 两种接入形态。它宣称的 67%/75%/88% 加速来自一份独立的 Python benchmark（16 个场景，Haiku/Flash），年省 9,536 美元是基于"每天 1000 场景"的外推，不是实测。

Cloudflare 已经产品化但还没 GA：`agents/codemode` 里的 `codemode({system, tools})` 可用，本地 workerd 完整可用，但 Worker Loader API 在生产环境仍是封闭 beta。官方博文没给任何 token 数字。

最强的产品化信号反而来自网关：`maximhq/bifrost`（8,972 star，2026-10-21 仍在更新）已经把 "MCP Code Mode" 做进了商业开源的 AI 网关。

## 四、厂商官方 CLI 上位：这一轮最被低估的变化

这条线不是"转换"，是"厂商自己下场"。而且国内三家办公套件几乎同步做了同一件事。

**飞书 `larksuite/cli`：17,748 star，官方 org 明示 "official Lark/飞书 CLI, maintained by the larksuite team"，MIT，2026-03-28 开源，最新 v1.0.98（2026-10-13），1198 commits。** 200+ 命令、18 个业务域、24 到 26 个 Agent Skills，覆盖 IM、云文档、云空间、电子表格、多维表格、日历、会议、邮件、任务、Wiki、通讯录、审批、OKR、考勤、幻灯片、搜索。安装 `npx @larksuite/cli@latest install`。它和 `larksuite/lark-openapi-mcp`（845 star，2025-08 后基本停更）是并存关系，但资源重心明显已经转向 CLI。

**钉钉 DingTalk Workspace CLI（`dws`）：3,752 star，Go 1.25+ 编写，2026-10-20 更新。** 官方称其为连接 Agent 与钉钉生态的"核心基础设施"，13 个产品、159 条命令——AI 表格 41、群聊 23、文档 21、听记 19、日历 14、审批 9、日志 7、通讯录/待办/钉盘各 6、考勤 4、DING 2。授权走 `dws auth login` OAuth（支持设备码），管理员要在开发者后台"CLI 访问管理"里开启，支持最小权限、全链审计、`--dry-run` 预览。

**企业微信 `wecom-cli`：3,227 star，MIT © 2026 WeCom，npm 包 `@wecom/cli`。** 11 类能力：消息（机器人主动推送）、邮件、文档、在线表格、智能表格、智能文档、待办、日程、会议（含纪要转写）、微盘、通讯录。`wecom-cli auth init` 扫码授权。

**微软 `playwright-cli`：14,427 star，2026-10-19 更新。** 定位是"CLI for common Playwright actions"，能录制并生成 Playwright 代码、检查选择器、截图。这个项目对上一份报告的结论有直接影响：Electron 端到端验证可以用它替代 Playwright MCP，更省 token。

**Cloudflare `cf`：2026-09-28 发布，`npm i -g cf`，开源在 `cloudflare/cf`。** 这是唯一一家明确要**换掉自己旧工具**的：`cf` 覆盖 3,000+ API 操作，Wrangler 只有约 280 条。默认输出 JSON（对人类 pretty print、对 agent 压缩），`cloudflare.config.ts` 用 TypeScript 写配置让 LSP 能帮 agent 补全，`cf cli search` 允许 agent 用自然语言找命令。官方计划 beta 结束后发布 Wrangler 的最后一个大版本并引导用户迁移，之后提供 18 个月维护期。博文里最关键的一个数字是：2026 年 3 月 agent 占 Wrangler 使用量的四分之一，到发布前一周已经达到 **48%**，且 agent 每天用的命令种类几乎是人类的两倍。

## 五、那个被反复引用的"Perplexity 弃用 MCP"

需要泼一点冷水。这件事在中文圈传播极广，但一手证据很薄。

多个中文来源称 Perplexity 联合创始人兼 CTO Denis Yarats 在 2026 年 3 月内部宣布"正在放弃 MCP，转而使用 API 和 CLI"。但时间与场合在转译链里已经分叉：早期稿件说"3 月 12 日公司内部"，后续多篇改称"3 月 11 日 Ask 2026 开发者大会台上"。英文逐字原话、X 原帖、官方博客都未找到。较严谨的一篇（墨天轮）指出 Yarats 强调的是"**内部**降低优先级"，主要针对 stdio 形态的 MCP，并非号召全行业弃用，且 Perplexity 官方文档当时仍挂着 MCP server 接入页。

Garry Tan 的 "MCP sucks honestly. It eats too much context window." 同样是个人 X 发言、语境是转发 Yarats 的表态，不是 YC 公司政策，原帖 URL 也未检索到。

结论：**"大厂集体抛弃 MCP"是传播放大，不是事实。** 事实是"几家厂商把 CLI 升为一等公民，MCP 降为并存选项"，这个判断有官方仓库和官方文档双证，足够硬。

## 六、代价：CLI 不是免费午餐

**鉴权被压平。** OAuth 设备码、elicitation、sampling 在 CLI 里退化成"人先 login 一次"。`mcpc` 明确写着"从不提示"，遇到 `input_required` 直接报错。

**结构化输出退化。** 默认人类可读文本，要 `--json` 才拿回 `structuredContent` 和 `isError`。`mcp2cli` 的 changelog 暴露了这个 bug 面：直到 3.6 才修"isError 时仍 exit 0""resource_link 被静默丢弃""structuredContent 非空但 content 为空时结果丢失"。在 CLI 层重建 MCP 语义，等于把协议重写一遍。

**错误处理降维。** JSON-RPC 错误码变成退出码加 stderr 文本，`mcp2cli` 还得专门把 anyio 的 ExceptionGroup 拍平才能给出一行干净报错。

**生命周期没消失，只是转移了。** 冷启动 `npx` 加握手太贵，于是 mcporter 上了 daemon、mcpc 上了 bridge 进程、mcp2cli 上了 session daemon——绕一圈又回到常驻进程。

**权限粒度更粗。** MCP 可以按 tool 授权，给了 Bash 就等于给了全部工具，白名单只能按命令前缀做。只有 `mcpc` 的 `--proxy` 认真处理了"不把原始 token 暴露给沙箱"。

**新攻击面。** `--auth-header` 走 argv 会出现在 `ps` 里（mcp2cli 用 `env:`/`file:` 缓解）；自动发现 `.mcp.json` 里的 `${VAR}` 可以被恶意仓库用来偷 token。

## 七、反向声音：MCP 在自己内部解决了上下文问题

最强的反方不是博客，是 Anthropic 自己。2025-11-24 的 Advanced Tool Use 给了两条在 MCP 内部解决问题的路：**Tool Search Tool**（`defer_loading`，77K 降到 8.7K，85%）和 **Programmatic Tool Calling**（43,588 降到 27,297，37%）。官方明确定位这两者与"代码执行"是互补关系，而且**保留完整 schema、不破坏 prompt caching**。言下之意很清楚：上下文问题不必通过降级成 CLI 来解决。

Cloudflare 也提供了反证：CLI 派说"CLI 复用系统认证所以更安全"，但 CLI 把凭据放进环境变量和 argv，恰恰是泄露面；Code Mode 把 token 留在 supervisor、沙箱断网，安全边界反而更清晰。

## 八、结论：对你这个 Go + Electron 项目的实际建议

**CLI 赢的是发现成本**（`--help` 按需加载，不用预载 schema）和**复用既有认证**；**Code Mode 赢的是上下文恒定**和**数据不过模型**。这两件事被中文圈大量混为一谈，而它们的适用场景完全不同。

具体到你的项目，我建议这样用：

Go 和 Electron 的工具链本来就是 CLI-first（`go test`、`golangci-lint --out-format=json`、`electron-builder --dir`、`playwright test`），所以这条趋势对你几乎零迁移成本——你不需要"转向"，你本来就是对的。

值得马上试的三个：`microsoft/playwright-cli` 替代 Playwright MCP 跑 Electron 端到端测试；`npx mcporter list --brief` 把 Context7 这类需要常驻的 MCP 转成按需查询，省掉每次会话预载的工具 schema；如果你的项目碰 Cloudflare，`cf cli search` 那种"让 CLI 自带命令检索"的设计是目前最值得抄的交互模式。

不建议现在投入的：`mcp2cli` 的 OpenAPI 模式（小工具集下收益只有 68%，且鉴权和错误语义都要你自己兜）；各类 20 到 200 star 的 code-mode 小项目（这个赛道死亡率很高，`superradcompany/tool-cli` 已经 archived，`mKeRix/toolscript` 已停更）。

终局大概率是混合体：**MCP 提供鉴权与 schema 契约，代码沙箱做执行层，CLI 做发现与调试界面。** `apify/mcpc` 的 `--proxy`、`forgemax` 的固定双工具、Cloudflare 的 `codemode` 都是这个形状。现在就把 MCP 全删掉换成 CLI，只是把一种成本换成了另一种。

## 局限

Perplexity 与 Garry Tan 的原始出处未能核实，仅有中文二手转译，本报告已标注证据强度为 D。`mcporter` 是否支持"多个 server 合并进同一个 CLI"未能完全核实。`forgemax` 文档里 76 工具场景的 15,000 与 33,100 两个数字自相矛盾，未采信其百分比。中文博客流传的"CLI 比 MCP 便宜 17 倍""3 个 server 143K token 占 72% 上下文""工具选择准确率 43% 降到 14%"均无原始出处，不予引用。所有 star 数为 2026-10-21 快照。

## 参考文献

1. [openclaw/mcporter](https://github.com/openclaw/mcporter)
2. [knowsuchagency/mcp2cli](https://github.com/knowsuchagency/mcp2cli)
3. [mcp2cli: One CLI for Every API](https://www.orangecountyai.com/blog/mcp2cli-one-cli-for-every-api-zero-wasted-tokens)
4. [apify/mcpc](https://github.com/apify/mcpc)
5. [postrv/forgemax](https://github.com/postrv/forgemax)
6. [universal-tool-calling-protocol/code-mode](https://github.com/universal-tool-calling-protocol/code-mode)
7. [Anthropic — Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
8. [Anthropic — Advanced tool use（Tool Search / Programmatic Tool Calling）](https://www.anthropic.com/research/advanced-tool-use)
9. [Cloudflare — Code Mode](https://blog.cloudflare.com/code-mode/)
10. [Cloudflare — Introducing cf: the agentic CLI for the entire Cloudflare API](https://blog.cloudflare.com/cloudflare-cf-cli-launch/)
11. [cloudflare/cf](https://github.com/cloudflare/cf)
12. [larksuite/cli 官方仓库](https://github.com/larksuite/cli)
13. [飞书 CLI 官网](https://www.feishu.cn/feishu-cli)
14. [larksuite/lark-openapi-mcp](https://github.com/larksuite/lark-openapi-mcp)
15. [钉钉开放平台：DingTalk CLI 文档](https://open.dingtalk.com/document/development/dingtalk-cli-performing-tasks-within)
16. [DingTalk-Real-AI/dingtalk-workspace-cli](https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli)
17. [WecomTeam/wecom-cli](https://github.com/WecomTeam/wecom-cli)
18. [microsoft/playwright-cli](https://github.com/microsoft/playwright-cli)
19. [cli/cli（GitHub 官方 CLI）](https://github.com/cli/cli)
20. [github/github-mcp-server](https://github.com/github/github-mcp-server)
21. [maximhq/bifrost](https://github.com/maximhq/bifrost)
22. [墨天轮：MCP 彻底被抛弃了吗（Yarats / Garry Tan 引述与限定）](https://www.modb.pro/db/2043953028391833600)
23. [InfoQ：Cloudflare 推出面向 AI 代理的 CLI 并逐步停用 Wrangler](https://www.infoq.cn/article/Ddda0DF68laqfoqa4Lju)
24. [Stripe Docs: Agents and AI on Stripe](https://docs.stripe.com/agents)
