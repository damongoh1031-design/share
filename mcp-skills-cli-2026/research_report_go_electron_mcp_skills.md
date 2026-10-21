# Go + Electron 开发中真正有助益的 Skills 与 MCP

**调研时间：2026 年 10 月 20 日** ｜ 数据为检索时点快照，star 与下载量变化很快

## 摘要

截至 2026 年 10 月，MCP 生态已经完成一次明显的退潮：协议在 2026-07-28 版改为无状态模型并把 Tasks 移出核心，同时官方新增了 "Skills over MCP" 扩展；Context7、Chrome DevTools MCP 等头部项目纷纷提供 CLI 模式。这说明社区对"什么都包一层 MCP"的做法已达成否定共识——MCP 装多了不是慢一点，而是把有效上下文吃光。对 Go 和 Electron 这两条链路，真正值得装的东西屈指可数：Go 侧是官方的 `gopls mcp` 加一份 46 个技能的 `samber/cc-skills-golang`；Electron 侧是 `chrome-devtools-mcp` 连 `--remote-debugging-port`，但必须锁版本，因为 Electron 属于它的非官方支持场景。除此之外，绝大多数 Go 和 Electron 专用的第三方 MCP 是几十 star、单次提交的玩具，装了只会增加攻击面和上下文负担。真正的效率提升来自"少量高价值 MCP + 确定性 CLI + 承载判断标准的 Skills"这个三层组合，而不是继续找"Electron 专用 MCP"。

## 一、按开发阶段排的选型表

| 阶段 | 用什么 | 形态 | 结论 |
|---|---|---|---|
| 方案规划 | `github/spec-kit` 或 `Fission-AI/OpenSpec` | Skill | 绿地用 spec-kit，棕地/需求多变用 OpenSpec |
| 编码（Go） | `gopls mcp` | MCP | 必装，官方，唯一有编译器级语义的 |
| 编码（Go 规范） | `samber/cc-skills-golang` | Skill | 必装，46 个原子技能，零运行时风险 |
| 编码（TS 语义） | `mcp-language-server` | MCP | 大型 TS 项目装，中小项目用宿主自带 LSP |
| 查库文档 | Context7 或 `ctx7` CLI | MCP/CLI | 装，但优先试 CLI 模式 |
| 符号级重构 | Serena | MCP | 大仓值得，小仓用 grep |
| 调试（渲染进程） | `chrome-devtools-mcp` + `--browser-url` | MCP | 必装，锁版本 |
| 调试（生产错误） | Sentry MCP | MCP | 有线上环境就装，除错闭环唯一解 |
| 调试（Go 断点） | Delve + 人 | CLI | 不要指望 MCP，现有封装全是 2025 年 3 月的单次提交 |
| 性能（Go） | `pprof-analyzer-mcp` | MCP | 值得装，把火焰图变成 agent 可读的层级 JSON |
| 性能（前端） | `performance_start_trace` | MCP 内置 | Chrome DevTools MCP 自带，不要另装 Lighthouse |
| 验证（端到端） | Playwright `_electron.launch()` + `playwright test` | CLI | 不要用 Playwright MCP 跑 Electron |
| 验证（静态） | `golangci-lint run --out-format=json`、`tsc --noEmit` | CLI | 输出本就结构化，包 MCP 是负收益 |
| 验证（安全） | `electronegativity`、`govulncheck`、Semgrep | CLI/MCP | 扫描交给工具，修复交给 agent |
| 交付 | GitHub MCP（白名单 + 只读） | MCP | 只开 repos/issues/pull_requests/actions |

## 二、2026 年的关键变化：MCP 退潮，Skills 上位

这一轮变化不是观点，是有硬证据的。

协议层面，2026-07-28 版做了自 2024 年以来最大的一次断裂式修改：删除 `initialize` 握手与 `Mcp-Session-Id`，改为每个请求自带 `protocolVersion` 和 `clientCapabilities` 的**无状态模型**，新增强制的 `server/discover` RPC；服务端主动发起的 elicitation、sampling、roots 被"多轮往返请求"（服务端返回 `input_required`、客户端带 `inputResponses` 重试）取代；Tasks 从核心移出、变成官方扩展。同一版里还新增了两个扩展：**Skills over MCP**（把结构化工作流指令通过 MCP 分发）和 **MCP Apps**（对话内联交互 UI）。这两个扩展的存在本身就说明了一件事：协议作者认为"工具调用"不足以承载 agent 的工作流知识，需要给 Skills 让出位置。

成本层面，Anthropic 在 2025-11-04 的工程博客给出了量化数据：把所有工具定义预加载进上下文，在数千工具规模下可达数十万 token；改用"代码执行 + 按需读工具文件"后，示例从 **150,000 token 降到 2,000 token，降幅 98.7%**；一次 2 小时的会议转录在两次工具调用之间往返，额外消耗约 50,000 token。Cloudflare 的 "Code Mode" 得出相同结论。这就是为什么 Context7 在 2026 年推出了不依赖 MCP 的 `ctx7` CLI，GitHub 官方 MCP 提供了 toolsets 白名单和只读模式，Chrome DevTools MCP 同时提供 CLI 入口。

中文社区的反应更直接。2026 年 2 月到 3 月，公众号上密集出现"Skill 比 MCP 省 99% 的 Token，MCP 不是银弹，是 Token 黑洞""MCP 已死，CLI 当立""SKILL 能解决 MCP 的 token 冗余，但二者是互补而非对立"这类标题，说明"少装 MCP"在中文技术圈已经从小众判断变成了共识。同时 Anthropic 的 Agent Skills 在 2025-12-18 以 agentskills.io 发布为开放标准，SKILL.md 事实上成了跨工具的分发格式。

把这三条放在一起，2026 年的正确姿势已经很清楚了：**能用 CLI 的不用 MCP，能用 Skill 承载的知识不要写成工具，只有"需要持久连接或实时状态"的场景才值得上 MCP。**

## 三、判断准则：什么该是 MCP，什么该是 Skill，什么直接跑 CLI

这是本次调研最想给出的一条可复用结论，比任何清单都重要。

**该做成 MCP 的只有三类。** 第一类是需要**持久连接和实时状态**的：浏览器的 CDP 连接、LSP 会话、调试器会话。这类东西无法用一次性的命令行调用表达，因为它的价值在于"停在那里看"。第二类是需要**平台鉴权代理**的：GitHub、Sentry、Figma 这类有 OAuth、有配额、有权限模型的远端服务，MCP 帮你把鉴权、分页、schema 都封好了。第三类是**需要远程结构化查询**的：Context7 的文档库、pprof 的性能档案，本质是"把一个大知识库按需切片"。

**该直接跑 CLI 的，是那些确定性、幂等、输出本就结构化的命令。** `go build`、`go test -json`、`go vet`、`golangci-lint run --out-format=json`、`tsc --noEmit`、`electron-builder --dir`、`electronegativity -i ./src -o report.csv`，全部属于这一类。给它们套一层 MCP，收益是零，成本是一个进程、一份工具 schema、以及每次调用都要在上下文里过一遍的描述文本。这就是为什么 GitHub 上那些 0 到 1 star 的 `golangci-lint-mcp` 不值得用——不是作者写得差，是这件事本身没有增量价值。

**该用 Skill 承载的，是判断标准和流程纪律。** 比如"Go 里 context 应该怎么传"、"Electron 发布前必须检查哪 12 项"、"TDD 的红绿重构循环怎么走"。这些是知识，不是能力；写进 SKILL.md 让模型按需加载，只在命中时消耗 token，比做成工具让模型每次猜参数高效得多。

## 四、Go 链路：一个官方项目加一份技能包，其余都是噪音

Go 侧有个结构性原因导致 MCP 生态贫瘠：Go 工具链天然 CLI-first、输出确定、退出码可靠，agent 直接执行 `go build` 和 `golangci-lint run` 往往比套一层 MCP 更稳定。所以真正值得装的只有三样。

**`gopls mcp` 是唯一的官方答案，也是必装项。** 它在 gopls v0.20.0（2025 年 7 月）引入，文档在 go.dev/gopls/features/mcp，源码在 `gopls/internal/mcp`，官方明确标注 experimental。安装只需 `go install golang.org/x/tools/gopls@latest`，接入 Claude Code 是 `claude mcp add gopls -- gopls mcp`。它有两种模式，差别很关键：detached 模式（`gopls mcp`，stdio）启动独立 headless 实例，**只能看到已保存到磁盘的文件**；attached 模式（`gopls serve -mcp.listen=localhost:8092`，SSE 端点在 `http://localhost:8092/sessions/1`）能共享 LSP 会话内存，**能看到未保存的 buffer**。如果你的 Cursor 或 VS Code 里已经常驻 gopls，只有 attached 模式才有意义。

工具集在 v0.20 时期是 12 个：`go_workspace`、`go_search`、`go_file_context`、`go_file_metadata`、`go_package_api`、`go_context`、`go_symbol_references`、`go_references`、`go_rename_symbol`、`go_diagnostics`、`go_file_diagnostics`、`go_vulncheck`。注意它**没有**跳转定义、hover、补全、格式化——定位是"只读的代码理解 + 诊断 + 漏洞扫描"，不是 IDE 能力镜像。真正的价值其实在配套的模型指令上：用 `gopls mcp -instructions > GEMINI.md` 可以导出官方定义的工作流，里面强制要求"先 `go_workspace` 建立全局认知，改代码前必须 `go_symbol_references` 查引用，改完必须 `go_diagnostics` 确认无错，通过后才跑 `go test`"。这套 prompt 本身就是最值钱的部分，比工具本身更值钱。已知的坑是 `go_search` 和 `go_symbol_references` 走大小写不敏感模糊匹配，在中等规模仓库里一次返回的噪声偏多，需要模型自己再筛。

**`samber/cc-skills-golang` 是 Go 侧真正成熟的那一块，强烈建议装。** 3.5k star、MIT、18 天前仍在更新，作者是 samber/lo 的作者 Samuel Berthe。约 46 个原子化技能，覆盖 code style、错误处理、并发、context、testing、benchmark、performance、observability、troubleshooting、lint、security、modernize、project layout，以及 grpc、swagger、cobra、viper、uber-fx、google-wire、testify 等库的专属规范。装法是 `/plugin marketplace add samber/cc` 然后 `/plugin install cc-skills-golang@samber`，或用 `npx skills add https://github.com/samber/cc-skills-golang --all` 走通用 Agent Skills 通道。设计上是渐进披露：推荐集启动只加载约 1,100 token 的描述，单个技能正文 1,000 到 2,500 token。作者自报评测通过率 3348/3439（97%）对比无技能的 1957/3439（57%），这个数字是自报、未经第三方复现，应当打折看；但即便效果只有一半，作为纯 prompt 资产它也是零运行时风险——最坏情况是没效果，而不是搞坏你的构建。

**`pprof-analyzer-mcp` 是性能这一类里唯一值得装的。** 50 star 但更新极勤（检索当天仍在提交），已迁移到官方 MCP Go SDK。七个工具里最有用的是 `generate_flamegraph`（输出 SVG）、`compare_profiles`（基线对比目标）、`detect_memory_leaks`（两份 heap diff）和 `analyze_heap_time_series`（三份以上 heap 的时间序列）。它的价值在于把火焰图变成 agent 可读的层级 JSON，这确实是 MCP 该干的事——不是包一层命令行，而是做一次数据结构转换。坑是 `generate_flamegraph` 依赖 Graphviz 的 `dot` 在 PATH 里，交互式 pprof 只支持 macOS。

**明确不要装的。** 所有 `golangci-lint` 相关 MCP：`wavilen/golangci-lint-mcp`（1 star）、`vinaycharlie01/mcp-golangci-lint`（0 star）、`afshinator/mcp-server-go-quality`（1 star，设计最合理——把三个工具统一成带 file:line:column 的 `Diagnostic[]` 数组——但单人维护，不能进生产依赖）。所有 Delve 封装：`dwisiswant0/delve-mcp` 和 `xhd2015/dlv-mcp` 都是 21 star，且**全部文件都在 2025 年 3 月的一次提交里**，之后零更新，功能清单写得很漂亮（breakpoint、step、variables、evaluate、DAP），但本质是 demo。工程上也不建议：dlv 是长会话状态机，MCP 的请求-响应模型对"停在断点后反复 inspect"很不友好，超时和会话恢复都是坑。Go 的调试目前还是交给人，或者让 agent 用 `dlv test --headless` 配合日志与 panic 栈定位。

顺带说一个反向结论：sqlc、mockery、ent、oapi-codegen、staticcheck 都**没有** MCP，而且这是合理的。它们是一次性确定性代码生成，agent 直接执行命令即可，MCP 化没有增量价值。找不到不是你的问题，是这类工具不该有。

## 五、Electron 链路：只有一层被照亮，而这一层恰好最痛

Electron 的痛点是四层架构：主进程、渲染进程、preload、IPC。AI 改代码"看起来对但跑不起来"，本质是它看不见运行时。2026 年的现状是：**现有工具只照亮了渲染进程这一层，主进程仍然是盲区。**

**`chrome-devtools-mcp` 是唯一建议作为基础设施安装的，但必须锁版本。** 由 Chrome DevTools 团队官方维护，53.9k star、周下载 174 万、Apache-2.0，检索当天仍在提交。能力覆盖性能 trace（`performance_start_trace` / `analyze_insight`，能给 LCP、INP、CLS 的洞察）、网络（`list_network_requests` 含响应体落盘）、控制台（`list_console_messages`，**带 source map 的堆栈**——这条对"改完代码看真实报错"价值最高）、DOM 快照、截图、录屏、`evaluate_script`、Lighthouse 审计（注意 `lighthouse_audit` 明确不含 performance，性能必须走 trace）、CPU 降频与 Slow 3G 模拟。

接 Electron 的方式已经核实：先 `electron . --remote-debugging-port=9222` 启动应用，再在 MCP 配置里写 `args: ["chrome-devtools-mcp@latest", "--browser-url=http://127.0.0.1:9222"]`，然后用 `list_pages` 选中 renderer 页面。但这里有三个必须知道的事实。其一，README 明确写"officially supports Google Chrome and Chrome for Testing only"，其他 Chromium 内核"may work, but not guaranteed"——Electron 属于非官方支持场景。其二，仓库里已有 25 条 Electron 相关 issue：v0.20.1 曾因 `Target.getDevToolsTarget` 在 Electron 中不存在导致**所有工具全挂**（#1197，随后紧急回滚）；Electron 频繁重启时 page id 会静默绑错页面（#2304、#2339）；两次"增加 Electron 官方支持"的 PR 均未合并。其三，主进程用 `--inspect=5858` 开的 Node inspector **连不上**，因为它走的是 Puppeteer 的 browser CDP 而不是 Node target。所以实操建议是：不要用 `@latest`，锁一个已验证可用的版本；每次热重启后重新 `list_pages`；主进程只能靠日志落盘，或自己用 `chrome-remote-interface` 包一层薄 MCP（目前没有现成方案）。隐私方面，trace 默认会把 URL 上传到 Google CrUX，可用 `--no-performance-crux` 关闭。

**Playwright MCP 很强，但不是 Electron 方案。** 微软官方，38.4k star、周下载 346 万。它是 a11y 快照驱动（省 token、不需要视觉模型），工具覆盖点击、表单、上传、多标签、网络路由、storage、trace、video，`--cdp-endpoint` 也能挂到已开调试端口的 Electron renderer 上。但**官方不支持 Electron 启动**：#994 功能请求已关闭，配套 PR #1291（`--browser=electron`、`--electron-app`、`electron_ipc_send`）当天关闭未合并。它无法调用 Playwright 的 `_electron.launch()`，因此拿不到 `app` 对象、做不了主进程 evaluate、碰不到原生对话框和菜单。

Electron 最稳的验证方式其实不是任何 MCP：**写一个用 `_electron.launch()` 的 Playwright 测试文件，让 agent 跑 `npx playwright test`**。这样主进程、IPC、原生窗口都能断言，失败时给出的是确定性堆栈而不是"agent 觉得应该没问题"。微软自己也建议高吞吐的编码 agent 用 Playwright CLI + Skills 而不是 MCP，理由是省 token。分工因此很清楚：Chrome DevTools MCP 管诊断（性能、网络、console、DOM），Playwright CLI 管端到端回归。

**TypeScript 语义层用 `mcp-language-server`，但先看宿主有没有内置。** 1.6k star、Go 编写，通过任意 LSP 暴露 `definition`、`references`、`rename`、`diagnostics`、`hover`、`completion`，解决"grep 找不全引用、跨文件重命名漏改、类型错误要等 `tsc` 跑完"三个痛点。配置要点是 `--workspace` 指向仓库根、`--lsp typescript-language-server --stdio`；Electron 的三套 tsconfig（main / preload / renderer）建议分别起 server 或配 project references，否则 preload 里 `contextBridge` 的类型会丢。缺点是 2026-03-01 之后没再更新。**如果 Cursor 或 Claude Code 自带 LSP 语义检索，优先用内置的**，不要重复装。各种个人写的 ts-morph MCP 不建议碰：多是单人项目、周下载个位数，重命名时对 path alias 和 barrel file 的处理不如 LSP 稳。

**打包、签名、自动更新：没有 MCP，也不需要有。** 检索未发现维护活跃的 electron-builder 或 electron-forge MCP。正确姿势是 CLI 加 skill：快速验证产物用 `electron-builder --dir`（不打安装包，几十秒出 unpacked 目录，agent 可直接跑起来）；macOS 公证用 `notarytool` 配 `APPLE_ID` / `APPLE_APP_SPECIFIC_PASSWORD` / `TEAM_ID`，Windows 用 `signtool` 或 Azure Trusted Signing，但**证书、钥匙串、2FA 必须人工**，agent 只能改配置和读报错；自动更新排查先看 `latest.yml` 里的 version、sha512、path 是否与产物一致，`autoUpdater.checkForUpdates()` 失败多半是 channel 或 feed URL 写错。常见坑是 arm64/x64 双架构、`asarUnpack` 原生模块、`afterSign` 钩子里 notarize 没 await。

**Electron 安全审计：有工具、无 MCP，建议自己写一个 skill。** `doyensec/electronegativity`（1.05k star，Apache-2.0，最后提交 2025-08）能静态扫描 `contextIsolation`、`nodeIntegration`、`webSecurity`、CSP、`allowRunningInsecureContent`、危险 IPC 暴露面、缺失的 `setPermissionRequestHandler`，输出 CSV/JSON 可直接被 agent 解析，缺点是误报不少、新 API 覆盖滞后。配合官方的 `@electron/fuses`，发布前必须关掉 `RunAsNode` 和 `EnableNodeCliInspectArguments`，否则 `ELECTRON_RUN_AS_NODE` 可以绕过整个沙箱。没有现成 skill，建议自写 `.claude/skills/electron-security/SKILL.md`：跑 electronegativity，读 fuses 状态，对照官方 security checklist 逐条核，只报告带文件行号的发现。

**明确不要装的。** `TheDarkSkyXD/debug-electron-mcp`（npm 上叫 `@debugelectron/debug-electron-mcp`）：1 star、**周下载 1 次**、17 个 open issue，思路其实正确（按端口注册项目、只控 renderer、日志有界读取），但要求客户端支持 2026-07-28 无状态协议（`server/discover`、无 initialize），多数客户端还不兼容，且依然看不到主进程。可以读源码借鉴，不要进生产工具链。`punkpeye/electron-mcp-server` 仓库已 404。MCP 目录站上标"优质认证"的 Electron MCP 属于营销标签，不是质量证明。

## 六、跨语言通用层：五个留，其余砍掉

**留下 Context7。** 63.3k star，解决"训练数据过期 + API 幻觉"，只暴露两个工具（`resolve-library-id`、`query-docs`），上下文占用极低。2026 年新增的 `ctx7` CLI + Skills 模式值得优先试——作者自己都认为不是所有场景都值得开一个 MCP。注意文档由社区贡献、后端闭源，冷门库和私有库覆盖差。

**留下 Serena。** 30.4k star，基于 LSP，官方语言列表明确包含 Go（走 gopls），共 40 多种语言。核心价值不是"更聪明的 grep"，而是 `find_symbol`、`find_referencing_symbols`、`replace_symbol_body` 这类**符号级原子操作**：跨文件重命名、移动、引用查找从"8 到 12 步易错的文本手术"变成一次调用。差异在大仓才显著，小文件和纯文本仍该用 grep。短板是 LSP 后端没有 type hierarchy、move、inline（需要 JetBrains 后端），且主体 GPL-3.0，商用分发要注意。

**留下 GitHub 官方 MCP。** 33.8k star、Go 编写、更新活跃，覆盖 repos、issues、PR、Actions、code security、discussions、notifications。**正确用法是开 toolsets 白名单加 read-only 模式**，只放 `repos`、`issues`、`pull_requests`、`actions` 四个，这是同时控制上下文和爆炸半径的做法。不要给 agent 全开写权限。

**留下 Sentry MCP。** 官方仓库，支持 remote 和 stdio。价值独特：从生产错误和堆栈直接反查代码与最近提交，是"除错"环节少有的真需求，其他工具替代不了。

**留下 Semgrep MCP 或 Snyk。** 官方提供，正确用法是**把扫描结果结构化喂给 agent 去修**，而不是让 agent 自己"感觉安全"。

**砍掉 Sequential Thinking。** 本质是把 CoT 写进工具调用，对 2026 年的推理模型基本是负收益：每一步思考都要一次工具往返、把整段思考文本重新灌回上下文、还得手动维护 `thoughtNumber`。只在两个场景有价值：小模型，或需要可审计的思考留痕。

**砍掉通用 Memory MCP。** 宿主自带的 memory 或 AGENTS.md 已经覆盖，多装一个是纯冗余。

**砍掉 Task Master / Shrimp Task Manager 这类任务分解工具。** 一份 `TODO.md` 加 spec 文档加宿主自带的 plan mode 能达到 80% 的效果，且不占工具位。这类工具解决的是"模型不够强时的脚手架问题"，模型变强后它们最先被淘汰。

**砍掉 Puppeteer MCP、Brave Search MCP、各类 everything/all-in-one 演示服务器。** 前者被 Playwright 取代，中者宿主自带联网，后者是文档示例不是产品。

**Skills 侧的选择。** 官方 `anthropics/skills`（182k star）必读，但主要是"怎么写"而非"直接用"，里面的 docx/xlsx/pptx/pdf 和 skill-creator 是真能用的。`obra/superpowers`（302k star）把 TDD、头脑风暴、子代理开发固化成技能和斜杠命令，工程纪律最强，适合有明确 TDD 习惯的团队，缺点是流程重、对探索型任务束缚大。`github/spec-kit`（142k star）是官方 SDD 工具链（constitution → specify → plan → tasks → implement），绿地项目和需要交付物留痕时值得，小改动用它纯属自找麻烦。`Fission-AI/OpenSpec`（72.5k star）轻量、工具无关，棕地项目和需求频繁变更时体感最好。`BMAD-METHOD`（54.4k star）模拟完整敏捷团队角色，角色扮演成分重，适合教学和从零搭建，资深工程师多半嫌吵。

## 七、Go 后端 + Electron 前端的组合场景

如果你的项目是 Go 写后端逻辑、Electron 做壳和 UI（这是"Go 和 Electron"最典型的组合），有三件事值得单独说。

**工具配置要按层分工，不要指望一个 MCP 通吃。** 仓库根目录同时装 `gopls mcp`（attached 模式，指向 Go module 根）和 `chrome-devtools-mcp`（指向 9222 端口），再在 `frontend/` 子目录装 `mcp-language-server` 走 typescript-language-server。三个 server 各自只管自己那层的语义，模型需要跨层时会自己切换。不要试图用 Serena 一个顶三个——它能同时索引 Go 和 TS，但 LSP 后端切换会拖慢首次索引。

**IPC 边界是最容易出静默错误的地方，必须用测试锁住。** Go 侧通常通过 HTTP 或 stdio 子进程与 Electron 主进程通信，preload 再用 `contextBridge` 暴露给渲染进程。这条链路上任何一层改了字段名，运行时才会炸。建议在 Playwright 的 `_electron.launch()` 测试里直接断言：启动真实 Go 二进制（或 `go run`），调 `window.api.xxx()`，校验返回值。这一步做扎实之后，Chrome DevTools MCP 只需要负责 UI 层和性能，不必再替 IPC 兜底。

**打包要把 Go 二进制当资源管。** 常见做法是把编译好的 Go 可执行文件放进 `extraResources` 或用 `asarUnpack` 解出，主进程启动时 `spawn` 它，退出时确保子进程被杀掉（否则 Windows 上会留下孤儿进程占端口）。多架构要分别交叉编译（`GOOS=darwin GOARCH=arm64` 等），命名要和 `process.arch` 对得上。这些步骤没有 MCP 能替你做，但值得写成一个 skill，把"交叉编译 → 校验架构 → 打进包 → 冒烟启动"固化成流程。

## 八、成本与安全：装之前必须知道的四件事

**工具投毒和 rug pull 是真实攻击面。** Invariant Labs 在 2025-04-01 公开的实证是：一个伪装成 `add` 的工具在 Cursor 中读取了 `~/.ssh/id_rsa` 和 `mcp.json` 并外传；跨服务器影子攻击能让"所有邮件改发攻击者地址"而界面上完全不显示。官方随后发布了 MCP-Scan。2026-07-28 规范已经把这条写进安全原则：**工具描述和 annotations 一律视为不可信，除非来自可信服务端**。实操上就是：不装来源不明的 server，不 `npx` 直接跑未经审计的包，不用要求全盘文件权限的 server。

**上下文成本是硬约束。** 前面那组 150,000 降到 2,000 的数字不是修辞。一个典型的"装了 15 个 MCP"的配置，光工具定义就可能吃掉三到五万 token，直接压缩你真正能用来读代码的窗口。判断方法很简单：如果你发现自己经常触发上下文压缩，先数工具数量，而不是换更大的模型。

**只读默认、白名单优先。** GitHub MCP 开 read-only 和 toolsets 白名单；Chrome DevTools MCP 用 `--slim` 精简模式；`--browser-url` 打开的调试端口是**任何本机程序都能连**的，不要在开着它的时候浏览敏感网站，Chrome 也强制要求用非默认的 `--user-data-dir`。

**协议版本要留意。** 2026-07-28 之后的 SDK 是破坏性升级，老客户端可以回退兼容 2025-11-25，但新写的 server 不要再基于 initialize 握手模型。装第三方 MCP 时如果发现它只支持旧协议，要么等作者更新，要么别装——这次变更的适配成本不低。

## 九、最小可落地配置

如果只想花半小时，配这些就够了：`gopls mcp`（detached 起步，IDE 常驻后改 attached）、`samber/cc-skills-golang`、`chrome-devtools-mcp` 锁版本加 `--browser-url`、Context7 或 `ctx7`、GitHub MCP 只开四个 toolset 且只读。Go 侧再加 `pprof-analyzer-mcp`，有线上环境再加 Sentry，有设计稿再加 Figma 官方 MCP（`https://mcp.figma.com/mcp`，remote 模式不需要桌面端），有组件库再加 Storybook MCP（`npx storybook add @storybook/addon-mcp`，端点在 `http://localhost:6006/mcp`，真正的价值是"生成组件 → 写 story → 跑 test-run → 修 a11y"这个闭环）。

其余的，等你确实撞上对应的墙再装。装工具的顺序应该是"先有痛，再找药"，而不是"先囤药，再找病"。

## 十、结论

回到最初的问题：Go 和 Electron 开发中有什么 skills 或 MCP 有实际助益？

Go 侧的答案是官方 `gopls mcp` 加 `samber/cc-skills-golang` 这一 MCP 一 Skills 的组合，加一个 `pprof-analyzer-mcp` 处理性能。除此之外的 Go 专用 MCP 基本是玩具，而 sqlc、mockery 这类工具本来就不该有 MCP。

Electron 侧的答案是 `chrome-devtools-mcp` 连 `--remote-debugging-port`，锁版本、容忍它对 Electron 的非官方支持、接受主进程是盲区；端到端验证改用 Playwright 的 `_electron.launch()` 写测试而不是 MCP；类型安全靠 LSP，安全审计靠 electronegativity 加自写 skill。

通用层的答案是 Context7、Serena、GitHub、Sentry、Semgrep 五个，规划类工具按项目性质在 spec-kit 和 OpenSpec 之间二选一，Sequential Thinking 和各种 task manager 可以放心删掉。

比清单更重要的是那条准则：**需要持久连接或实时状态的才做成 MCP，确定性命令直接跑 CLI，判断标准和流程纪律写成 Skill。** 2026 年的生态已经在用脚投票证明这一点——协议把 Tasks 移出核心、新增 Skills over MCP 扩展，头部项目集体补上 CLI 入口，中文社区在讨论"MCP 已死，CLI 当立"。顺着这个方向配置，你的 agent 会更准、更便宜，也更容易排查。

## 局限

本次调研有几处未能完全核实，需要说明：`hloiseau/mcp-gopls` 的 star 数未取到；gopls 在 2026 年最新版本的工具集是否仍为上述 12 个，官方文档页未列清单，12 个来自 v0.20 时期的第三方对比；staticcheck 是否存在专用 MCP 未能确认，检索结果全是无关内容；`samber/cc-skills-golang` 的 97% 对 57% 评测数据是作者自报，无第三方复现；GitLab MCP 的工具清单、ref.tools 与 DeepWiki MCP 的维护状态未逐项核实。所有 star 数和下载量都是 2026-10-20 的快照，这类数字在几个月内可能翻倍或腰斩，选型时请以仓库最近提交时间为准，而不是 star 数。

## 参考文献

1. [MCP Specification 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)
2. [MCP Extensions 概览（Tasks / Skills over MCP / MCP Apps）](https://modelcontextprotocol.io/extensions/overview)
3. [Gopls: Model Context Protocol support（官方文档）](https://go.dev/gopls/features/mcp)
4. [gopls v0.20.0 release issue #74655](https://github.com/golang/go/issues/74655)
5. [samber/cc-skills-golang](https://github.com/samber/cc-skills-golang)
6. [cxuu/golang-skills](https://github.com/cxuu/golang-skills)
7. [ZephyrDeng/pprof-analyzer-mcp](https://github.com/ZephyrDeng/pprof-analyzer-mcp)
8. [dwisiswant0/delve-mcp](https://github.com/dwisiswant0/delve-mcp)
9. [xhd2015/dlv-mcp](https://github.com/xhd2015/dlv-mcp)
10. [wavilen/golangci-lint-mcp](https://github.com/wavilen/golangci-lint-mcp)
11. [afshinator/mcp-server-go-quality](https://github.com/afshinator/mcp-server-go-quality)
12. [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp)
13. [chrome-devtools-mcp Advanced Usage（--browser-url 连接已运行实例）](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/advanced-usage.md)
14. [chrome-devtools-mcp Tool Reference](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md)
15. [Issue #1197：v0.20.1 破坏 Electron 场景](https://github.com/ChromeDevTools/chrome-devtools-mcp/issues/1197)
16. [Issue #2304：Electron 重启后 page id 错绑](https://github.com/ChromeDevTools/chrome-devtools-mcp/issues/2304)
17. [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp)
18. [playwright-mcp Issue #994：Electron support 已关闭](https://github.com/microsoft/playwright-mcp/issues/994)
19. [playwright-mcp PR #1291：Electron 支持（未合并）](https://github.com/microsoft/playwright-mcp/pull/1291)
20. [Playwright Electron API（_electron.launch）](https://playwright.dev/docs/api/class-electron)
21. [TheDarkSkyXD/debug-electron-mcp](https://github.com/TheDarkSkyXD/debug-electron-mcp)
22. [isaacphi/mcp-language-server](https://github.com/isaacphi/mcp-language-server)
23. [doyensec/electronegativity](https://github.com/doyensec/electronegativity)
24. [Electron Fuses 官方文档](https://www.electronjs.org/docs/latest/tutorial/fuses)
25. [Electron Security Checklist](https://www.electronjs.org/docs/latest/tutorial/security)
26. [Electron 命令行开关（--remote-debugging-port / --inspect）](https://www.electronjs.org/docs/latest/api/command-line-switches)
27. [Figma MCP Server 官方指南](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Dev-Mode-MCP-Server)
28. [Storybook MCP Server 文档](https://storybook.js.org/docs/ai/mcp/overview)
29. [upstash/context7](https://github.com/upstash/context7)
30. [oraios/serena](https://github.com/oraios/serena)
31. [github/github-mcp-server](https://github.com/github/github-mcp-server)
32. [getsentry/sentry-mcp](https://github.com/getsentry/sentry-mcp)
33. [Anthropic: Introducing Agent Skills（2025-10-16）](https://www.anthropic.com/news/skills)
34. [Anthropic: Code execution with MCP（2025-11-04）](https://www.anthropic.com/engineering/code-execution-with-mcp)
35. [Cloudflare: Code Mode](https://blog.cloudflare.com/code-mode/)
36. [Invariant Labs: MCP Tool Poisoning Attacks（2025-04-01）](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)
37. [anthropics/skills](https://github.com/anthropics/skills)
38. [obra/superpowers](https://github.com/obra/superpowers)
39. [github/spec-kit](https://github.com/github/spec-kit)
40. [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)
41. [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)
