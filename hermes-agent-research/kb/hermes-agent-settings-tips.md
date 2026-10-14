---
id: hermes-agent-settings-tips
title: Hermes Agent 设置技巧汇总(官方最佳实践 + Reddit 社区实证 + 本机实测)
tags: [hermes-agent, nousresearch, ai-agent, settings, reddit, cli, memory, skills, mcp, cron]
created: 2026-10-14
updated: 2026-10-14
version: 5
status: active
source: 官方文档 hermes-agent.nousresearch.com + Reddit 社区(r/openclaw、r/better_claw、r/hermesagent、r/LocalLLaMA、r/AI_Agents,经 cnblogs/百家号转引)+ 中文实战社区 + 本机安装实测(2026-10-14)
confidence: high(官方文档、本机实测已核实;Reddit 观点为社区转引,个别数字未能独立复核)
---

# Hermes Agent 设置技巧汇总

**一句话结论**:Hermes Agent(Nous Research,2026-02 开源)的设置核心 = `~/.hermes/`(Windows 原生装在 `%LOCALAPPDATA%\hermes`)下的 `config.yaml` + `.env` + `SOUL.md` 三件套;Reddit 社区口碑最好的点是安装顺滑、token 效率高、学习循环真能沉淀技能,最大的坑是"自我评估永远觉得自己做对了"和手动改的技能会被自动覆盖——所以关键技巧是:用 AGENTS.md 固化项目规则、5 步以上任务就让它建 Skill、终端 backend 对不可信代码切 Docker、消息 bot 必须开白名单。

## 1. 本机现状(2026-10-14 实测)

| 项 | 实测值 |
|---|---|
| 版本 | Hermes Agent vgit.4e74031 (2026.9.24),install method: git |
| HERMES_HOME | `C:\Users\Admin\AppData\Local\hermes`(非文档写的 `~/.hermes`,Windows 原生版如此) |
| terminal backend | `local`(默认) |
| memory | `memory_enabled: true, memory_char_limit: 2200` |
| skills | 14 类目录已装:apple / autonomous-ai-agents / creative / devops / email / media / note-taking / playwriter / productivity / research / social-media / software-development / web |
| SOUL.md | 已自定义(英文,简洁直接风格,约 660 字符) |

## 2. 安装与诊断

| 操作 | 命令/说明 |
|---|---|
| Linux/macOS/WSL2 安装 | `curl -fsSL https://hermes-agent.nousresearch.com/install.sh \| bash` |
| Windows 原生安装(PowerShell) | `iex (irm https://hermes-agent.nousresearch.com/install.ps1)`;官方标注早期测试版,优先 WSL2 |
| 桌面版 | 官网下载 macOS/Windows 安装包,CLI 与桌面同装 |
| 自检(任何配置问题先跑这个) | `hermes doctor` |
| 全量配置向导 | `hermes setup` |
| 版本/状态 | `hermes --version` / `hermes status` |
| 从 OpenClaw 迁移 | `hermes claw migrate` |
| 更新 | `hermes update` |

安装器自动装:uv、Python 3.11、Node.js v22(浏览器自动化/WhatsApp 桥接)、ripgrep、ffmpeg。

## 3. 模型配置

- 200+ 模型随时切换,无厂商锁定:`hermes model`。
- 国内常用:Kimi / GLM / DeepSeek / MiniMax;最省钱的姿势是买 Coding Plan 包月(字节方舟/阿里云 Token Plan),Hermes 里选 Custom endpoint + OpenAI 兼容 Key 即可。
- OpenClaw 用户口碑:Opus 4.7($261/月)vs GLM-5.1($31/月)质量差距主要在边缘场景——日常任务用便宜模型。

## 4. 上下文文件(最被低估的设置)

| 文件 | 作用 | 位置/加载机制 |
|---|---|---|
| SOUL.md | Agent 个性/立场/边界,最先进 system prompt | `~/.hermes/SOUL.md`(或 `$HERMES_HOME/SOUL.md`);Hermes 会自动生成初始文件 |
| AGENTS.md | 项目级规则(编码规范、目录约定) | 项目根目录,每次会话自动加载 |
| .cursorrules / .cursor/rules/ | 兼容读取,无需重写规范 | 工作目录 |
| MEMORY.md / USER.md | Agent 工作笔记 / 用户画像(有字符上限,约 2200/1375) | `~/.hermes/memories/` |

子目录的 AGENTS.md 不预加载,由 `subdirectory_hints.py` 在工具调用时延迟注入。上下文文件每个字符都花 token,保持精简。

## 5. 记忆 vs 技能(设计逻辑)

| | Memory | Skill |
|---|---|---|
| 存什么 | 事实(环境、偏好、项目) | 流程(多步工作流、工具操作指南) |
| 触发 | 自动(FTS5 跨会话检索 + LLM 摘要 + Honcho 用户建模) | 按需加载,`/skill-name` 或自然语言匹配 |

- Skills 是"可复用工作流文档",不是插件;渐进式加载,装 100 个不卡、不多花 token。
- 来源:内置 70+ / 社区 agentskills.io(经 65+ 安全规则扫描)/ 自建 SKILL.md。
- 常用 CLI:`hermes skills list` / `hermes skills search <关键词>` / `hermes skills install <包>`。
- 5 步以上且会重复的任务,直接说"把刚才的保存为 skill"。

## 6. 定时自动化(cron)

```bash
hermes cron create "0 9 * * 1-5" "帮我整理今天的工作优先级,结果发到飞书"
hermes cron create "0 17 * * 5" "根据本周对话记录生成周报初稿"
```

- 自然语言也能建:对话里直接说"每天早上 9 点检查 HN 的 AI 新闻,Telegram 发摘要"。
- 前提:先在 Telegram/Discord 用 `/sethome` 设主频道,否则主动消息没地方发。

## 7. 消息网关与安全

- 一个 gateway 接 20+ 平台:CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Email、SMS、钉钉、飞书、企业微信、微信、QQ Bot、Home Assistant 等。
- 配置:`hermes gateway setup` 或改 `~/.hermes/config.yaml` 的 `gateway.adapters`;Token 放 `.env`。
- **安全红线(官方 tips 明确)**:
  - 永远不要给有终端权限的 bot 设 `GATEWAY_ALLOW_ALL_USERS=true`;用 `TELEGRAM_ALLOWED_USERS` / `DISCORD_ALLOWED_USERS` 白名单,或 DM 配对(`hermes pairing approve telegram <码>`)。
  - 命令审批(once/session/always/deny)别急着选 always;危险命令检查在容器 backend 下会被跳过。
  - 处理不可信仓库:Docker/Daytona backend(`.env` 里 `TERMINAL_BACKEND=docker`),容器内破坏不伤宿主机。

## 8. 性能与成本技巧

- 别破坏 prompt 缓存:会话中不换模型、不改系统 prompt 前缀。
- `/compress` 在上下文爆掉前压缩历史;`/usage` 看消耗,`/insights` 看 30 天模式。
- 并行任务用 `delegate_task` 派子 agent(只有摘要回主对话);批量操作用 `execute_code` 一个脚本跑完,别逐条敲命令。
- CLI 技巧:`hermes -c` 恢复上次会话、`hermes -r "<标题>"` 按名恢复;`/title` 给会话命名;`Ctrl+V` 直接贴图;Alt+Enter 换行;`/verbose` 切工具输出详细度。

## 9. 本地模型(Ollama)离线部署

```
# ~/.hermes/.env
OPENAI_API_KEY="not-needed"
OPENAI_BASE_URL="http://localhost:11434/v1"
LLM_MODEL="llama3.1"
TEMPERATURE=0.2
```

- 硬件建议:8-16GB 内存用 Llama 3.1 8B / Qwen2.5 7B 的 4-bit 量化(Q4 精度损失 <1%,显存降 60%+);24GB+ 再上 70B。
- `memory.persist: true` 保证断网重启记忆还在;`compression.trigger_threshold: 0.6` 防长对话 OOM。
- 社区警告:本地优先目前"challenging",除 CLI 外其他通信方式 token 消耗剧增(token hell)。

## 10. Reddit 社区实证观点(2026-04~05,500+ 互动汇总)

| 主题 | 社区结论 |
|---|---|
| 为什么选 Hermes | "从安装开始就比 OpenClaw 顺畅";token 效率高;$5 VPS 可跑;截至汇总时无公开 CVE |
| 学习循环 | "东西坏了它真会记住并自动建排障 skill"(38 票);自建技能使 prompt injection 风险更低 |
| 致命坑 1 | 自我评估过度自信:"它自己判断做得好不好,永远觉得自己做得好"(u/CustomMerkins4u) |
| 致命坑 2 | 手动编辑的 skill 会被"自我改进"覆盖——重要 skill 要有自己的备份 |
| 生态差距 | 内置工具约 40+ vs OpenClaw 5700+ 扩展 |
| 合作用法(18% 双用率) | OpenClaw 负责网关/编排/cron,Hermes 负责对话与复杂执行,经 MCP 桥接或 agentskills.io 共享技能 |
| 信任争议 | 有用户质疑 Reddit/X 上存在 Hermes 的 astroturfing 营销(r/openclaw 等),也有用户认为口碑是真实的——评估时保持批判 |

## 11. 可复用操作清单

1. 装完先 `hermes doctor`,全绿再往下。
2. 写 SOUL.md + 3 次教学对话(最高频场景),每次后 `hermes memory consolidate` 启动学习循环。
3. 项目根目录放 AGENTS.md(规范一次写入永久生效)。
4. 5 步以上重复任务 → 让它建成 skill。
5. 消息平台设主频道 `/sethome` + 白名单;cron 自动化日报/周报/备份。
6. 记忆与 skills 不跨设备同步:换机手动打包 `~/.hermes/{skills,memory,memories}`。
7. 成本敏感:简单任务切便宜模型;`/usage` 常看;批量操作走 `execute_code`。

## 12. 坑与反直觉

- 文档写的 `~/.hermes` 在 Windows 原生安装下实际是 `%LOCALAPPDATA%\hermes`,别照抄路径。
- Skill 装得多不会卡(渐进式加载)——但上下文文件(SOUL/AGENTS)会进每条消息,越长越贵。
- 记忆是"冻结快照":会话中途改记忆,要下次会话才生效。
- `hermes doctor` 红字没解决就装 skill,会白装。
- Windows 上写文件 Unicode 报错:显式 `encoding="utf-8"`,PowerShell 先 `[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)`。

## 13. SOUL.md 专章(v2 补充,2026-10-14 深调研,官方文档 + 本机源码 v2026.9.24 实测)

### 13.1 定位与位置

- SOUL.md = Agent 的**主要身份标识**,占 system prompt **第 1 槽位**,**完全替换**内置默认身份;内容不加包装语言原样注入。
- 路径:`$HERMES_HOME/SOUL.md`(通常 `~/.hermes/SOUL.md`;Windows 原生版 = `%LOCALAPPDATA%\hermes\SOUL.md`)。Hermes **只在 HERMES_HOME 找,不在 cwd 找**——仓库里放 SOUL.md 无效(那是社区常见误用)。
- 首次运行自动生成初始文件;已有文件不覆盖;**空文件 = 回退内置默认身份**。
- 注入前经过:提示词注入模式扫描 + 过长截断。SOUL.md 不会在上下文文件部分重复出现。

### 13.2 写什么 / 不写什么

| 写入 SOUL.md | 写入 AGENTS.md |
|---|---|
| 语气、个性、沟通风格、直接程度 | 代码规范、文件路径、命令、端口 |
| 如何应对不确定性/分歧/模糊 | 项目架构、部署说明 |
| "所有地方都生效"的规则 | "只属于某项目"的规则 |

判断原则:随你到处适用 → SOUL.md;属于某个项目 → AGENTS.md。

### 13.3 建议结构与官方 4 个风格模板

```markdown
# Identity   你是谁
# Style      说话什么风格
# Avoid      不该做什么
# Defaults   遇到模糊时怎么行为
```

1. **务实工程师**:"You are a pragmatic senior engineer. Be direct, concise unless complexity requires depth, say when something is a bad idea. Avoid: sycophancy, hype language, overexplaining obvious things."
2. **研究伙伴**:"curious, honest about uncertainty, distinguish speculation from evidence, ask clarifying questions when underspecified."
3. **教师**:"patient technical teacher, understanding not performance, build from intuition to details."
4. **严格审阅者**:"rigorous reviewer, point out weak assumptions directly, correctness over harmony, blunt clarity over vague diplomacy."

优质 = 稳定、宽泛、风格具体;劣质 = 堆项目细节、自相矛盾、微观管理每句回复格式、满篇"要有帮助/要清晰"(Hermes 本来就会)。

### 13.4 三层个性机制(对应"不同智能体"需求)

| 层 | 机制 | 粒度 | 命令/配置 |
|---|---|---|---|
| 1. 多实例 | **profile**(多个隔离 Hermes 实例,各带独立 SOUL.md/config/skills/memories/cron) | 长期、完全隔离 | `hermes profile create` / `use` / `list` / `delete` / `alias` / `export` / `import` |
| 2. 会话覆盖 | `/personality` 预设 + `config.yaml` 的 `agent.personalities` 自定义 | 单会话 | `/personality teacher`、`/personality codereviewer`(自定义) |
| 3. 子代理 | `delegate_task` 派隔离子 agent | 任务级 | 子代理**不继承 SOUL.md**(回退默认身份),模型可单独覆盖 |

内置 13 种 `/personality`:helpful / concise / technical / creative / teacher / kawaii / catgirl / pirate / shakespeare / surfer / noir / uwu / philosopher / hype。SOUL.md 是持久默认,`/personality` 是临时切换,互补。

### 13.5 profile 实操(v2026.9.24 CLI 实测)

```bash
hermes profile create work --clone        # 克隆活跃 profile:config.yaml/.env/SOUL.md/skills 跟过来,消息 bot token 不带
hermes profile create research --clone --no-alias
hermes profile use work                   # 设粘性默认 profile
hermes profile list
hermes profile show work
hermes profile describe work "擅长代码审查" # 描述供 kanban 编排器按角色路由任务
hermes profile alias                      # 管理 wrapper 脚本(给 profile 起别名命令)
hermes profile export work -o work.tar.gz # 备份/迁移
```

- `--clone` 复制 config.yaml/.env/SOUL.md/skills;`--clone-all` 全量(除历史与消息通道);`--clone-channels` 才复制 bot token(⚠ 两个 profile 持同一 bot token 会冲突,系统拒绝)。
- `--clone --sync-imports` 让新 profile 继续注册在同一 Claude Code/Codex 树上。
- 源码确认(profiles.py docstring):"Profile management for multiple isolated Hermes instances";每 profile 含独立 memories/sessions/skills/logs/cron/home;**`_CLONE_CONFIG_FILES` 含 SOUL.md**。
- **profile = 官方推荐的多智能体答案**:不同 SOUL.md 就要建不同 profile。

### 13.6 SOUL.md 编辑工作流与排错

1. 从自动生成的默认文件开始 → 2. 删掉不合意的 → 3. 加 4–8 行定语气 → 4. 用一段时间 → 5. 迭代。比一次设计完美人设有效。
- 编辑后要**新开会话**才生效(文件中改,重启或 /new)。
- "改了没变化"排查:编辑的是不是 HERMES_HOME 下的、文件是否为空、是否被 `/personality` 覆盖层主导。
- "部分内容被忽略"原因:更高优先级指令覆盖、自相矛盾、过长被截断、被注入扫描器改写。
- `display.skin` / `/skin` 管终端外观,与对话个性(SOUL.md)独立。

## 14. 多模型配置专章(v2 补充,官方 configuration + 本机 config.yaml 实测)

| 层级 | 机制 | 说明 |
|---|---|---|
| 主模型 | `config.yaml` 的 `model.default` + `model.provider`;CLI `hermes model` 向导选择;`--model`/`--provider` 单次覆盖;会话内 `/model` 随时切换 | 200+ 模型,无厂商锁定;`hermes model` OAuth 登录 Nous Portal/Codex/Anthropic |
| 辅助模型(auxiliary) | `config.yaml` 的 `auxiliary:` 段(标注 Advanced—Experimental) | 轻量模型跑 side tasks:vision(图像分析)、web_extract(网页摘要)、compression(上下文压缩)、tts_audio_tags;每任务独立 provider+model 可混,默认 auto(Gemini Flash via OpenRouter/Nous);`reasoning_effort` 可按任务调思考深度省钱 |
| 子代理模型 | `config.yaml` 的 `delegation.model` / `delegation.provider` | 覆盖 delegate_task 子 agent 用的模型;官方 cost tip:父代理留前沿模型保规划质量,子代理钉便宜模型(子代理扛绝大部分 token) |
| provider 列表(本机 config.yaml 实测) | openrouter / nous / anthropic / openai-codex / copilot / gemini / zai(GLM) / kimi-coding / minimax(-cn) / huggingface / nvidia / xiaomi / arcee / ollama-cloud / deepinfra / kilocode / ai-gateway / azure-foundry / lmstudio / custom(任何 OpenAI 兼容端点,含 Ollama/vLLM/llama.cpp) | streaming 可全局关(自建 OpenAI 兼容服务流式 tool-call 坏时) |

**本机现状**(2026-10-14 实测):provider = `custom:local`,base_url = `http://127.0.0.1:8788/v1`(本地代理),default model = `deepseek-v4.1-flash`;auxiliary 段全部注释(走默认 auto);`agent.personalities: {}`(未定义自定义个性)。

**多模型策略建议**:主模型按任务质量要求选;auxiliary 显式钉本地端点(压缩/摘要不需要多模态,省云端费用);delegation.model 钉便宜模型+父留前沿模型,是省钱最大杠杆。

## 15. 社区数据抓取与反爬调教(v3 补充,2026-10-14 社区调研)

**合规边界(先说)**:只抓公开数据 + 用本人账号登录态 + 遵守频率限制;不集成验证码破解/打码服务;遇到人机验证页面的正确处理是停下报告、降频或换官方 API/OAuth,而不是对抗风控。社区主流做法是换合规出口(住宅代理云浏览器)而非"攻破"验证。

### 15.1 目标站点 → 社区推荐路径

| 目标 | 推荐路径 | 依据 |
|---|---|---|
| 百度贴吧 | 移动版端点 `tieba.baidu.com/mo/q/m?kw=<kw>&pn=<N>` + WebFetch;**不要 curl**(数据中心 IP 一律 403;单帖 URL curl 会拿到「百度安全验证」2.5KB 空壳,同 URL 用 WebFetch 却能返回正文);吧内搜索端点全部被验证码拦截,只能深翻 + 关键词聚合 | 本机 tieba-scrape skill 实测(2026-09,rimworld 吧 130-200 帖/天,pn=6000≈47 天前,pn 可到 14000) |
| 知乎 | zhuanlan 详情页时抓时空(反爬),走浏览器工具或缓存;anysearch extract 可提取正文 | 本轮实测(同域 5 篇 2 篇抓到) |
| Reddit | reddit.com/search.json 与 old.reddit 对本机网络出口直接 block(403 页面);redlib 公共镜像多已关闭(2026-08 起);可行路:住宅代理云浏览器出口 / 免 key 源(last30days skill 自动配 Reddit 源)/ 官方 API(需账号) | 本机 2026-10-14 实测 |
| Discord | **Hermes 原生 gateway Discord adapter**(bot 身份,最稳);读频道历史让 agent 在服务器内操作 | 官方文档 |
| 通用网页 | 浏览器工具链(47 内置工具):`browser_navigate` / `browser_snapshot`(可访问性树 + `@e1` ref 定位)/ `browser_click` / `browser_type` / `browser_press` / `browser_scroll` / `browser_vision`(视觉兜底)/ `execute_code`(像素级操作) | 社区(实在智能 2026-08) |

### 15.2 搜索与提取配置

```bash
hermes config set web_search.provider bing        # 免 key 直接用
hermes config set web_search.provider google      # 需 CSE key,免费 100 次/天
hermes config set web_search.search_engine_id <id>
hermes config set tavily.api_key <key>            # 1000 次/月免费,结果已清洗
hermes skills install anysearch                    # 免费,含百度源,支持 batch_search/extract
```

- 社区实测排序(2026-06):anysearch > Bing(5000 次/月免费)> Google CSE > Tavily > DuckDuckGo(中文弱);Brave 英文最强。
- 网页提取 4 后端:**Firecrawl(默认)/ Parallel / Tavily / Exa**,`hermes setup --portal` 一条命令配好 provider + 4 个 tool gateway。
- **调教关键**:把工具优先级写进 MEMORY.md("日常搜 anysearch,挂了退 Bing……"),比每次口头交代有效。

### 15.3 反爬三条社区路线

| 路线 | 配置 | 特点 |
|---|---|---|
| Browser Use 云浏览器 | `hermes setup` → Browser Automation 步骤选 Browser Use,粘 API Key | 195 国住宅代理 + 反检测指纹,免本地 Chromium |
| Scrapeless CDP | `config.yaml` 加一行 `browser: cdp_url: "wss://browser.scrapeless.com/api/v2/browser?token=${KEY}&proxyCountry=US&sessionTTL=600"`;临时用 `/browser connect "<wss-url>"` | 一行接入;所有 browser_* 工具自动走云浏览器;`sessionName` 保登录态/cookie,`sessionRecording=true` 可回放视频排错 |
| 本地拟人化 | snapshot+vision 双模定位 → 输入拆单字符+随机间隔(均值 450ms 正态)→ 每次 press 后必须 snapshot 校验结果渲染 → 失败截图留证 | 零成本,成功率看站点;某教程提到 Camofox 本地伪装(localhost:8080),仅单篇来源,**未在官方文档/本机 config 见到,未核实** |

### 15.4 "调教"= 把技巧固化到三层

1. **SOUL.md**(仅 HERMES_HOME 生效):写抓取行为规范,如"browser_press 后必须 browser_snapshot 校验结果节点,未命中立即终止报错"、"提交前停下等人类确认"。⚠ 纠偏:有教程让把此规则放"项目根目录 SOUL.md + soul_path",与官方文档矛盾——SOUL.md 只在 HERMES_HOME 加载,项目级规则应放 AGENTS.md。
2. **MEMORY.md**(上限 2200 字符,倒逼高密度):记失败教训与工具优先级,如"贴吧单帖不用 curl""reddit 直连走不通"。
3. **Skill**:5 步以上重复流程让 Hermes 固化为 skill(学习循环:打分→改写→择优;离线进化走轨迹压缩);或手动 `hermes skills install`。
4. 学习循环会把失败经验自动沉淀(MEMORY.md 存事实、SKILL 存流程),这是"越用越聪明"的兑现路径。

## 17. 深度研究技能栈(v4 补充,2026-10-14)

### 17.1 三层栈:搜索底座 → 研究编排 → 知识沉淀

| 层 | 技能 | 来源/热度 | 作用 |
|---|---|---|---|
| 搜索底座 | `sn-search`(聚合 arXiv/Semantic Scholar/PubMed/GitHub/SO/HN/HuggingFace/**Reddit/Twitter/YouTube/B站/知乎/抖音**,学术+开发者+中英文社交) | SenseNova-Skills,开源 MIT,4 位数 star | 一套打通多源检索,替代反复切搜索引擎 |
| 搜索底座 | `anysearch` | 社区(免费,含百度源) | 免 key 搜索+extract,batch_search |
| 搜索底座 | 内置 `web_search` + Firecrawl/Parallel/Tavily/Exa 四提取后端 | 官方 | Bing 免 key;Firecrawl 默认 |
| 搜索底座 | `last30days` | 社区 skill | 拉 Reddit/X/YouTube/TikTok 近 30 天真实讨论,配免 key 源+扫浏览器 cookie(X) |
| **研究编排** | **`autoresearch`**(爆款 9.8/10) | 社区 | 深度联网搜索,自动访问数十个数据源,整合多源信息生成结构化研究报告,引用标注+来源追溯 |
| **研究编排** | **`sn-deep-research`** | SenseNova(GitHub) | 6 子 skill:规划→分维度取证→综合→成稿→格式发现→HTML 转换;中间产物持久化,**断点可续** |
| 研究编排 | `agent-team-orchestration`(9.7) | 社区 | 多 agent 角色(项目经理/研究员等)并行+汇总 |
| 学术 | `arxiv` / `arxiv-reader`(9.5) | 本机已装 arxiv | 按领域/关键词/作者搜 arXiv,自动摘要+核心要点+图表结论+多篇对比+文献综述 |
| 学术 | Hermes `skills/research/`、`mlops/ml-paper-writing`(模板+引用管理) | 源码内置 | 文献综述、论文写作 |
| 知识沉淀 | `grounded-citations`(本机已装) | 内置 | 结论强制带引用 |
| 知识沉淀 | `llm-wiki`(本机已装) | 内置 | 构建/查询 Markdown 个人知识库(Karpathy 式) |
| 知识沉淀 | `competitor-news-monitor`(本机已装) | 内置 | 持续监控竞品/主题动态 |
| 知识沉淀 | `blocked-page-recovery`(web 类,本机已装) | 内置 | 抓取被拦时的恢复流程(配合 15 章反爬) |

### 17.2 安装方式

```bash
# 社区 skill(agentskills.io hub)
hermes skills install anysearch
hermes skills search deep-research       # 检索更多

# SenseNova-Skills(MIT):让 Hermes 自己装,或克隆后拷入 ~/.hermes/skills/
# 对话里说:"请帮我把 https://github.com/OpenSenseNova/SenseNova-Skills 安装到你的 Skills 目录"
# 或用官搭 agent_pack(Hermes+OpenClaw+全套 Skills)
```

skill 是 SKILL.md 声明触发条件(何时用/何时不用),agent 自动选择编排,无需手动指定。渐进式加载,装多不卡。

### 17.3 本机现状与缺口(2026-10-14 实测)

已装:`research/{arxiv, competitor-news-monitor, grounded-citations, llm-wiki}`、`web/blocked-page-recovery`、productivity 全家桶。
缺口(按杠杆排序):①多源聚合搜索(sn-search/anysearch,免 key 起步);②研究编排(autoresearch 或 sn-deep-research,断点续研对长任务关键);③社区实时观点源(last30days)。

### 17.4 配套调教(衔接第 13/15 章)

- SOUL.md 加研究规范:"每个结论必须带来源;区分事实/推断/未核实;不确定就说不确定"(本机 SOUL 已有相关基因,补一句引用要求即可)。
- MEMORY.md 记:"搜索顺序 sn-search > anysearch > bing;研究任务用 sn-deep-research 断点续跑"。
- 多 profile 分工:研究 profile(排队列长任务+cron 晨报)+ 日常 profile,或单 profile 用 `/personality` 切研究模式。
- 长研究用 cron + 主频道投递:每天定时跑 arXiv 新论文摘要/竞品监控,结果发 Telegram/飞书。

## 19. 知识库方案专章(v5 补充,2026-10-14 官方文档+本机 CLI/skill 实测)

### 19.1 需求 → 方案矩阵

| 需求 | 官方方案 | 社区方案 |
|---|---|---|
| 管理 md/pdf 文件 | **llm-wiki skill**(本机已装,v2.1.0):三层结构 raw/(papers/PDF 不可变源)→ entities/concepts/comparisons/queries(agent 维护的互链 md)→ SCHEMA.md;`WIKI_PATH` 环境变量(默认 `~/wiki`);纯 markdir 无数据库,Obsidian/VS Code 直接开 | Obsidian skill(note-taking/obsidian,本机已装):`OBSIDIAN_VAULT_PATH` 配好后全文搜索+新建+**自动双向链接**,读写文件与 Obsidian app 无关 |
| 嵌入/语义召回 | **外部记忆提供商**:`hermes memory setup`(bundled: honcho/openviking/mem0/holographic/retaindb/byterover;catalog 如 hindsight/supermemory;仅一个可激活;与内置 MEMORY.md/USER.md 并行)——带语义搜索、知识图谱、自动事实提取 | pdf 解析走 `auxiliary.vision`(Gemini Flash 类多模态);自建向量库走 MCP(community:Qdrant/Chroma/Milvus) |
| 召回 | 三层:①MEMORY.md/USER.md 冻结快照(即时)②`session_search` FTS5 全文(约 20ms,含历史会话)③外部 provider 语义召回;llm-wiki `index.md` 查询 | rag.hybrid_search 混合检索(第三方 skill,见 19.3 纠偏) |
| 去重 | 内置记忆**重复防护**(自动拒绝完全重复条目);memory 工具 replace/整合;llm-wiki raw 层不可变+log 追加制 | rag import `--upsert` 增量更新(第三方) |
| 重排 | ⚠ 原生无 rerank;provider 自带相关性排序 | rag.enable_rerank(第三方 skill) |

### 19.2 官方核心:llm-wiki(RAG-alternative)

skill 原版思路:传统 RAG 每次查询从零重新发现知识,llm-wiki **编译一次、持续保鲜**,交叉引用预先建好、矛盾预先标记。分工:人类策展源+指导分析,agent 做总结/交叉引用/归档/维护一致性。文件树:SCHEMA.md / index.md / log.md / raw/(articles,papers,transcripts,assets) / entities+concepts+comparisons+queries。接入 arXiv/PDF 归 raw/papers/,查询结果归档 queries/。

### 19.3 ⚠ 实测纠偏(2026-10-14,本机 v2026.9.24)

- **`hermes rag` 子命令不存在**(`hermes: 'rag' is not a command`);`hermes knowledge` 也不存在;config.yaml 无 `rag.*` 配置节。⇒ 社区热传的 "hermes-rag skill + hermes rag create/import/status + rag.embedding_model/enable_rerank/hybrid_search"(CSDN 2026-04 文)与 PHP 文(2026-05)里的 `hermes knowledge init/compile`**均无法在本机版本复现**,判定为旧版或第三方 skill,引用需谨慎,列入未核实。
- **`hermes memory --help` 实测**:bundled providers = honcho, openviking, mem0, holographic, retaindb, byterover;"Only one external provider can be active at a time";Built-in memory always active。官方文档称 8 家(bundled 6 + catalog)。
- 本机已装:`research/llm-wiki`(v2.1.0)、`note-taking/obsidian`、`research/arxiv`、`grounded-citations`、`competitor-news-monitor`。

### 19.4 推荐落地路线(三步,零外部依赖起步)

1. **第一步(今天就能做)**:配 Obsidian——对话里说“把 OBSIDIAN_VAULT_PATH 设成 <vault路径> 写进 .env”,重启会话;PDF/md 归档由 arxiv/pdf skill 摄入。
2. **第二步**:`WIKI_PATH` 指向 wiki 目录,启用 llm-wiki,喂第一批 PDF/文章进 raw/,让它建 index/entities;配 cron 每周 lint + 归档本周会话精华。
3. **第三步(需要语义召回时)**:`hermes memory setup` 选 mem0(或 supermemory),与内置记忆并行;大库再考虑 MCP 接 Qdrant(需自建)。
4. **效果组合拳**:wiki 管结构化知识、MEMORY.md 管高频事实、session_search 管历史回溯、provider 管模糊语义召回,四层互补,不重复建设。

## 20. 未核实项(v1 原有,续 v2/v3/v4/v5)

- Reddit 具体帖子链接未能直接抓取(reddit.com 与 redlib 镜像均被网络策略拦截),社区引述经 cnblogs/百家号 2026-05-08 汇总转引,原帖用户名/票数以该汇总为准。
- "Reddit 7 月汇总 276 用例"来自知乎文章(含明显营销内容),仅作背景参考,未逐条核实。
- 本机 version 2026.9.24,官方文档为最新版;个别 CLI 细节以 `hermes --help` 为准。
- 40+ 内置工具 / 70+ skills 数字来自不同时点的资料,可能随版本变化。
- v2 新增未核实:内置 personality 列表与 delegation 参数来自官方文档 + 本机 `--help` 实测;auxiliary models 官方自标 Experimental;profile 的 kanban orchestrator 路由细节未实测(需多 profile + gateway 环境)。
