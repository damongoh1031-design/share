# 近期热门、能和 AI Agent 配合的 CLI 应用（GitHub 实况，2026-10-21）

## 摘要

2026 年 10 月 GitHub 上"给 agent 用的 CLI"已经分化成六个互不重叠的品类，把它们混在一个榜单里排序没有意义。真正工程质量最高的两个是 `vercel-labs/agent-browser`（44,341 star，Rust 单二进制，自研 CDP 客户端，不依赖 Node 和 Playwright）和 `redhat-et/ripwire`（2,461 star，C++23 单二进制，把代码上下文压到 grep 的 5%）。声量最大的 `HKUDS/CLI-Anything`（55,688 star）机制是真的，用 7 阶段流水线把 GIMP、Blender、LibreOffice 这类有源码的软件自动生成 Python CLI，但维护在 2026-09-22 之后停滞，文档也浮夸。最需要警惕的是 `Panniantong/Agent-Reach`：100,321 star 却只有 341 个 watcher 和 231 个 issue，八个月涨十万星但仓库只有 2.7 MB，这是典型的营销驱动增长。最重要的方法论结论是：2026 年 star 已经完全不能当质量指标，要看 fork/star 比、issue/star 比和 `pushed_at`。

## 一、先建立一个分类框架

按"agent 拿这个 CLI 去干什么"来分，比按 star 排序有用得多：

| 品类 | 解决什么 | 代表项目 |
|---|---|---|
| 操作浏览器与网页 | agent 要看见、点击真实页面 | agent-browser、OpenCLI、Agent-Reach |
| 操作专业软件 | agent 要驱动 GUI 软件而非截图点击 | CLI-Anything、OfficeCLI、googleworkspace/cli |
| agent 自己的终端客户端 | 人机交互的主界面 | Codewhale、qwen-code、jcode、DeepSeek-Reasonix、oh-my-pi |
| 压缩上下文 | 少读点 token 就能定位代码 | ripwire、context-mode |
| 连接器与鉴权 | 把 1500 个 SaaS 接进来而不泄露 token | open-connector、mirage |
| 垂直场景 | 招聘、搜索、办公套件 | boss-agent-cli、SearchCLI、larksuite/cli |

## 二、操作浏览器与网页

**`vercel-labs/agent-browser` 是这一批里工程质量最高的。** 44,341 star、3,033 fork、693 个 open issue（1.56%，说明有真实 bug 负载而不是刷出来的）、2026-01-11 建库、今天仍在提交。它的关键设计是**自研 CDP 客户端**，README 明写 "Pure Rust daemon using direct CDP, no Node.js required"，只复用已装的 Chrome 二进制，不是 Playwright 封装。核心交互是 `snapshot` 输出无障碍树并给每个元素打 `@e1` 这类 ref，后续用 ref 操作，daemon 跨命令保持状态（空闲一小时退出）。

`npm i -g agent-browser && agent-browser install && agent-browser open example.com && agent-browser snapshot`

它的 agent 友好特性密度是这一批里最高的：`--json` 的错误带 `code` 字段（`tab_gone`、`outcome_unknown`）；`--delta` 只输出增量快照；`--max-output` 截断；`screenshot --if-changed` 带阈值；`--content-boundaries` 防 prompt injection；`--allowed-domains` 限制域名；Auth Vault 管凭据。最值得学的是它对"假成功"的处理：点击被弹窗遮挡时直接报 "covered by #consent-banner"，而不是假装点到了。

**`jackwener/OpenCLI` 是单人主导但设计相当讲究的项目。** 30,477 star、2026-10-20 更新、Node CLI（不是 MCP），靠"Chrome 扩展 Browser Bridge + 本地 daemon :19825"把网站变命令，复用你已登录的 Chrome profile，内置 100 多个站点 adapter（B 站、知乎、小红书、X、Reddit），另有 `opencli browser` 通用原语操作任意站点。它的输出契约值得抄：**默认 JSON**，成功是 `{ok,data}`、失败是 `{ok,error:{code,message,hint}}`，日志走 stderr，退出码用 `sysexits.h`（66 空结果、69 桥断、75 超时、77 需认证）。`opencli list` 紧凑分页加 `list search --site github` 做命令发现。瑕疵是作者 969 次提交、第二名只有 85 次，单人风险高；topics 里挂着 playwright 与 README"不用 Playwright"矛盾；"Any Website"实际是"100+ 适配器加通用原语"。

**`Panniantong/Agent-Reach` 需要单独提醒。** 100,321 star 是全批最高，但它的机制其实很薄：Python 薄层加一个 SKILL.md，**不做抓取**，只负责选型、安装、体检、路由——每个平台维护一个有序后端候选（twitter 走 twitter-cli 优先、其次 OpenCLI、再其次 bird），启动时探测第一个可用的，坏了给修复处方，实际读取交给 agent 自己调 yt-dlp/gh/OpenCLI。功能是真的，但 100,321 star / 8,835 fork / 231 issue（0.23%）/ **341 watcher**，仓库只有 2.7 MB，贡献者约 40 人且第二名只有 9 次提交，2026 年 2 月建库八个月涨十万星——这个增速在 GitHub 历史上没有对应体量的先例。可以当工具目录用，不宜当基础设施依赖。

## 三、操作专业软件

**`HKUDS/CLI-Anything`（55,688 star）机制是真的，但需要正确理解它是什么。** 它不是 CLI 集合也不是 MCP server，而是"LLM 代码生成器 + CLI-Hub 包管理器 + 50 多个 agent-harness 成品包"三件套。核心是 7 阶段流水线（Analyze → Design → Implement → Plan/Write Tests → Document → Publish），读**源码**把 GUI 操作映射成 API，生成 Python Click CLI（带 REPL、undo/redo、`--json`、自动生成 SKILL.md），然后调用真实软件后端（GIMP、Blender、LibreOffice、ffmpeg）渲染，不做重实现。

`pip install cli-anything-hub && cli-hub install gimp`；造新 CLI 用 `/cli-anything ./gimp`。

它的限制写在 README 里：需要强模型（弱模型产出残缺 CLI）、依赖源码（纯二进制软件效果大幅下降）、单次生成常需多次 `/refine`。工程是真的（5,024 fork、100+ 贡献者、top 贡献者 290 次提交），但 `pushed_at` 停在 2026-09-22，README 里测试数有 2280/2461/2464 三个版本、"18 apps"与表内 50+ 不一致。**工程真、文档浮夸、维护已减速。**

**`googleworkspace/cli`（31,741 star，Rust，2026-03-02）和 `iOfficeAI/OfficeCLI`（32,233 star，C#，2026-03-15）** 是另一条路：不生成，直接由厂商或团队做一个覆盖办公套件的 CLI。前者一条命令管 Drive、Gmail、Calendar、Sheets；后者自称"第一个为 AI agent 打造的 Office 套件"。这类项目的价值在于官方 schema 稳定，缺点是覆盖面永远追不上真实 API。

## 四、agent 自己的终端客户端

这一类的竞争在 2026 年极其激烈，且几乎全是今年新建的仓库：

| 项目 | Star | 语言 | 建库 | 特点 |
|---|---|---|---|---|
| `codewhale-hq/Codewhale` | 41,100 | Rust | 2026-01-19 | agent engine + 终端客户端，多 provider |
| `can1357/oh-my-pi` | 36,063 | TypeScript | 2025-12-31 | IDE 接进终端的编码 agent，**3,987 个 open issue** |
| `esengine/DeepSeek-Reasonix` | 35,882 | **Go** | 2026-04-21 | 面向复杂软件工程任务的编码 agent |
| `QwenLM/qwen-code` | 28,608 | TypeScript | 2025-06-26 | 阿里官方，终端里的编码 agent |
| `1jehuang/jcode` | 21,073 | Rust | 2026-01-05 | 高性能 harness，主打重度多 agent 并行 |
| `Twigpine/openclaude` | 34,047 | TypeScript | 2026-04-01 | "runs anywhere, uses anything"，fork 9,143 |

注意 `oh-my-pi` 的 3,987 个 open issue 与 36,063 star 的比例（11%）异常高，这通常意味着两类情况之一：用户基数真的极大且问题反馈积极，或者 issue 被当作讨论区滥用。`openclaude` 的 fork/star 比达到 26.8%（9,143/34,047）却只有 78 个 issue，更像是被大量 fork 当模板用，而不是被深度使用。

`DeepSeek-Reasonix` 值得单独说一句：它是这一批里唯一用 **Go** 写的编码 agent，35,882 star、417 个 issue、2026-04-21 建库、今天仍在更新。如果你在写 Go，它的实现方式（进程模型、工具调用的并发编排）比 Rust 那批更好读。

## 五、压缩上下文

**`redhat-et/ripwire`（2,461 star，C++23）是这一批里最"硬"的小项目。** 单二进制、零运行时依赖、离线、无 daemon、无 embedding，CLI 为主、MCP server 只是可选子集。机制是 tree-sitter 提符号 → 建调用图 → Personalized PageRank 排序 → stdout 输出压缩 XML，三路 router（name-exact、subtoken+body、mention anchor）按查询形态选路并在输出里披露 `route=`。索引 0.25 到 0.45 秒，索引体积 6.6 MB。

`ripwire . --for="incremental cache invalidation"`

它给的量化是目前最诚实的一组：整体消耗是 grep-and-read 方式的 **5.0% token**，`--callers` 场景省 69 到 208 倍，`--from-trace` 省 87 到 209 倍，且明确标注"省 token 随冷启动增长"这个结论是**预注册但未运行**的假设。输出默认 XML 而非 JSON，根节点自报 `est_tokens`，被截断时给 `capped=` / `unserved_total=` / `next=` 三个字段，不假装完整。

**`mksglu/context-mode`（31,381 star，TypeScript，2026-02-23）** 走另一条路：把工具输出在沙箱里过一遍再交给模型，宣称 98% 削减，同时持久化会话记忆、通过 MCP 和 hooks 在 17 个平台间做路由。它的定位是"上下文窗口优化层"而不是工具，适合已经装了太多 MCP 的人。

## 六、连接器与鉴权

`oomol-lab/open-connector`（6,056 star，2026-06-29）是开源的鉴权网关，把 1500 多个 SaaS provider 接到 agent 上，对标 Composio、Nango、Merge.dev、Arcade。`strukto-ai/mirage`（3,700 star，2026-05-06）自称"给 AI agent 的第一个虚拟终端"。这两个的 star 不算高，但解决的是真问题——agent 要访问第三方服务时的 OAuth 与 token 隔离，这恰恰是 CLI 派最容易被攻击的地方（凭据进 argv 会出现在 `ps` 里）。

## 七、国内场景

`can4hou6joeng4/boss-agent-cli`（2,116 star，Python）把 BOSS 直聘封装成 CLI 给 agent 用，支持搜索、福利筛选、打招呼；`volcengine/SearchCLI`（1,189 star，火山引擎官方）做 AI 搜索与推荐检索。这两个体量小但真实。

办公套件那条线上一轮已经查过，这里补一句量级对比：飞书 `larksuite/cli` 17,748 star（200+ 命令、24 个 Agent Skills）、钉钉 `dws` 3,752 star（159 条命令）、企业微信 `wecom-cli` 3,227 star。它们的共同点是官方出品、自带 OAuth、自带命令检索，比第三方 wrapper 可靠得多。

## 八、star 已经不能当质量指标

这一轮扫下来最实用的方法论，是怎么在 2026 年识别刷星和营销。

看 **fork/star 比**：健康值在 5% 到 10%。`openclaude` 26.8% 说明被大量 fork 当模板；`Agent-Reach` 8.8% 看似正常，但结合下面两条就露馅了。

看 **issue/star 比**：`agent-browser` 1.56%、`ripwire` 2.7% 是健康区间，说明有人真的在用并且真的在报 bug。`Agent-Reach` 0.23% 意味着十万 star 几乎没人提 issue——要么没人真用，要么用了但不反馈。反过来 `oh-my-pi` 11% 属于过高，需要看 issue 内容判断是真实反馈还是当论坛用。

看 **watcher 数**：`Agent-Reach` 341 个 watcher 对 100,321 star，比例 0.34%。真正被当基础设施用的项目，watch 比例通常在 1% 以上。`CLI-Anything` 222 watcher / 55,688 star 也是 0.4%。

看 **`pushed_at`**：`CLI-Anything` 停在一个月前，`googleworkspace/cli` 停在 10-06，这两个都要打折。

看**仓库体积与贡献者分布**：`Agent-Reach` 2.7 MB、第二名贡献者只有 9 次提交，说明代码量撑不起十万 star 的声量。

## 九、对 Go + Electron 项目的落地建议

`agent-browser` 是这一批里唯一真正能驱动 Electron 的。Electron 的渲染进程就是 Chromium，用 `electron . --remote-debugging-port=9222` 起应用，再 `agent-browser --cdp 9222 open ...` 就能 `snapshot` 和 `click @e2`。README 明确把 Electron apps 和 WebView2 列为 CDP 可控对象。但要注意两点：只能操作渲染进程的 DOM，主进程的 Node API 碰不到，得靠应用自己暴露 IPC；`--allowed-domains` 这类隔离特性在 `--cdp` 模式下会被拒绝。

`ripwire` 是接入成本最低的——单二进制扔进 PATH 就能用，无运行时依赖，适合放进 Go 项目的 agent 工作流里做代码定位。但它对 Go 语言的解析覆盖需要你实测 `ripwire .` 是否真的列出 `.go` 文件。

`CLI-Anything` 生成的是 Python Click 包，Go 侧只能 shell out，对 Electron 没有直接帮助。`OpenCLI` 依赖 Chrome 扩展，装不进 Electron，也不适合。

如果只装一个，装 `agent-browser`；如果只想省 token，装 `ripwire`。其余按需。

## 局限

`CLI-Anything` 的建库时间与 arXiv 编号（2606.03854）未交叉核实；`Agent-Reach` 是否刷星只能从 fork/watcher/issue 比例推断，无直接证据，判断为"高度可疑"而非定论；`oh-my-pi` 的 3,987 个 open issue 未逐条查看内容；`Agent-Reach` 与 `CLI-Anything` 的 watcher 数据来自 GitHub API 的 `subscribers_count` 或页面显示，两者口径可能略有差异。所有 star、fork、issue、日期均为 2026-10-21 的 GitHub API 快照。

## 参考文献

1. [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser)
2. [agent-browser README](https://raw.githubusercontent.com/vercel-labs/agent-browser/main/README.md)
3. [redhat-et/ripwire](https://github.com/redhat-et/ripwire)
4. [ripwire README](https://raw.githubusercontent.com/redhat-et/ripwire/main/README.md)
5. [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything)
6. [CLI-Anything README](https://raw.githubusercontent.com/HKUDS/CLI-Anything/main/README.md)
7. [jackwener/OpenCLI](https://github.com/jackwener/OpenCLI)
8. [OpenCLI README](https://raw.githubusercontent.com/jackwener/OpenCLI/main/README.md)
9. [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach)
10. [Agent-Reach README](https://raw.githubusercontent.com/Panniantong/Agent-Reach/main/README.md)
11. [codewhale-hq/Codewhale](https://github.com/codewhale-hq/Codewhale)
12. [QwenLM/qwen-code](https://github.com/QwenLM/qwen-code)
13. [esengine/DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix)
14. [1jehuang/jcode](https://github.com/1jehuang/jcode)
15. [can1357/oh-my-pi](https://github.com/can1357/oh-my-pi)
16. [Twigpine/openclaude](https://github.com/Twigpine/openclaude)
17. [googleworkspace/cli](https://github.com/googleworkspace/cli)
18. [iOfficeAI/OfficeCLI](https://github.com/iOfficeAI/OfficeCLI)
19. [mksglu/context-mode](https://github.com/mksglu/context-mode)
20. [oomol-lab/open-connector](https://github.com/oomol-lab/open-connector)
21. [strukto-ai/mirage](https://github.com/strukto-ai/mirage)
22. [can4hou6joeng4/boss-agent-cli](https://github.com/can4hou6joeng4/boss-agent-cli)
23. [volcengine/SearchCLI](https://github.com/volcengine/SearchCLI)
24. [larksuite/cli](https://github.com/larksuite/cli)
25. [DingTalk-Real-AI/dingtalk-workspace-cli](https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli)
26. [WecomTeam/wecom-cli](https://github.com/WecomTeam/wecom-cli)
27. [GitHub Trending（weekly）](https://github.com/trending?since=weekly)
28. [GitHub Search API](https://api.github.com/search/repositories)
