# goose 官方文档中文手册

goose 官方资料（仓库 `aaif-goose/goose`）的简体中文完整翻译：**文档站正文 22 章 173 页** + **博客存档 7 章 112 篇** + **Recipe 模板 67 个** + **仓库治理 16 篇** + **文档站工程 29 个文件**。

> 官方站点没有中文版（`docusaurus.config.ts` 中 `locales: ["en"]`，无 `i18n/` 目录），本手册是独立翻译成果。

| 项 | 值 |
|---|---|
| 源语料 | 397 个源文件，2,793,527 字节 |
| 章节数 | 33 章 |
| 页面节 | 397 个（每源文件一个 `## ` 节，均带 `> 原文：` 出处） |
| 覆盖范围 | 文档站 `docs/` 全部页面 · 博客 `blog/` 全部 112 篇 · Recipe 库 67 个 YAML · 仓库根治理文档 · 文档站工程文件 |
| 翻译方式 | 逐页完整翻译；代码、命令、环境变量、路径、配置键名一律保留原文 |
| 生成日期 | 2026-10-15 |

## 阅读建议

| 你的目的 | 建议读 |
|---|---|
| 第一次用 goose | 第 1 → 3 → 2 章 |
| 配好模型就跑 | 第 2 → 10 → 11 章 |
| 把团队规范喂给 goose | 第 4 → 5 章 |
| 把重复劳动做成流水线 | 第 6 → 20 章 |
| 控制 goose 能做什么 | 第 3 → 8 章 |
| 接一个外部系统 | 第 3 章 → 第 13–18 章中对应的一篇 |
| 自己写扩展 | 第 19 章 → 第 13 章 |
| 上下文爆了 / 会话乱了 | 第 7 → 11 章 |
| 出问题了 | 第 22 章 |
| 想读架构 | 第 21 章 |
| 想读官方博客长文 | 第 23–29 章 |
| 找现成 Recipe 直接用 | 第 30 → 31 章 |
| 想参与贡献 / 了解治理 | 第 32 章 |

## 总目录

### 第 01 章　快速开始与安装

> 从零装好 goose：系统要求、各平台安装方式、首次启动与验收。

`goose-zh-01-快速开始与安装.md`　·　2 页　·　源 29,196 B

- **快速开始：goose 五分钟入门**
    - 安装 goose
    - 配置提供方
    - 开始会话
    - 编写提示词
    - 启用扩展
    - 后续步骤
- **安装 goose**
    - 设置 LLM 提供方
    - 更新提供方
    - 运行 goose
    - 共享配置设置
    - 在 CI/CD 中固定 goose 版本
    - 为 Linux 发行版生成 manpage
    - 附加资源

### 第 02 章　模型提供方全览

> 全库最大的单页：30+ 模型提供方的接入方式、鉴权、参数与坑。

`goose-zh-02-模型提供方全览.md`　·　1 页　·　源 90,103 B

- **配置 LLM 提供方**
    - 可用提供方
    - 配置提供方与模型
    - 配置自定义提供方
    - 免费使用 goose
    - OpenRouter 高级参数
    - GitHub Copilot 认证
    - Azure OpenAI 认证
    - 多模型配置
    - Meta Muse Spark 推理强度
    - Gemini 3 思考等级
    - 查看模型推理

### 第 03 章　扩展与工具管理

> 扩展（Extension）如何接入、开关、授权；工具权限三级、四种权限模式、工具输出体积控制与 Code Mode。

`goose-zh-03-扩展与工具管理.md`　·　7 页　·　源 51,518 B

- **使用扩展**
    - 内置扩展
    - 发现扩展
    - 添加扩展
    - 启用/禁用扩展
    - 自动启用的扩展
    - 更新扩展属性
    - 移除扩展
    - 使用扩展启动会话
    - 开发扩展
- **管理工具**
- **管理工具权限**
    - 理解工具与扩展
    - 权限级别
    - 配置工具权限
    - 权限管理的好处
    - 权限配置示例
- **goose 权限模式**
    - 权限模式
    - 配置 goose 模式
    - CLI 提供方权限集成
- **调整工具输出详细程度**
- **Code Mode**
    - Code Mode 如何工作
    - 其他资源
- **Tool Shim**
    - 何时启用
    - 工作原理
    - 配置
    - 用法示例
    - 环境变量参考
    - 故障排查

### 第 04 章　上下文工程（一）：指令层

> 让 goose 记住你的规矩：`.goosehints`、持久指令、Skill（`SKILL.md`）与 8 个可覆盖的系统提示词模板。

`goose-zh-04-上下文工程-一-指令层.md`　·　5 页　·　源 39,108 B

- **上下文工程**
- **向 goose 提供提示**
    - 创建你的提示文件
    - 设置提示
    - 常见用例
    - 最佳实践
    - 自定义上下文文件
- **持久指令**
    - 工作原理
    - 配置
    - 示例
    - 用例
    - 持久指令与 goosehints 的对比
    - 最佳实践
- **Agent Skill**
    - 内置 Skill
    - Skill 位置
    - 创建 Skill
    - 来自插件的 Skill
    - 辅助文件
    - 常见用例示例
    - 最佳实践
    - 附加资源
- **自定义提示词模板**
    - 工作原理
    - 管理提示词模板
    - 附加资源

### 第 05 章　上下文工程（二）：Agent 层

> 角色与自动化：自定义 Agent（`@name` 提及 / 委派）、子代理、Hook 生命周期钩子、插件容器与自定义斜杠命令。

`goose-zh-05-上下文工程-二-Agent层.md`　·　5 页　·　源 60,230 B

- **自定义 Agent**
    - 创建 Agent 文件
    - 使用 Agent
    - 示例 Agent
    - 何时使用 Agent、Skill 还是 Recipe
- **子代理**
    - 如何使用子代理
    - 监控子代理活动
    - 内部子代理
    - 外部子代理
    - 建议的用例
    - 生命周期与清理
    - 配置
    - 安全约束
    - 附加资源
- **Hooks**
    - Hook 存放在哪里
    - 创建一个 Hook
    - Hook 配置
    - 支持的事件
    - Hook Payload
    - 阻止工具调用
    - 示例
    - 试用示例插件
    - 禁用 Hook 插件
    - 疑难排查
    - 附加资源
- **插件**
    - 插件能提供什么
    - 插件结构
    - 插件位置
    - 安装插件
    - 自动更新插件
    - 手动更新插件
    - 禁用插件
    - 插件格式
    - 何时使用插件、Skill 还是 Hook
- **自定义斜杠命令**
    - 创建斜杠命令
    - 使用斜杠命令
    - 限制
    - 附加资源

### 第 06 章　Recipes 可复用工作流

> 可复用工作流：Recipe 的完整 YAML 字段参考、会话型 Recipe、存储与分享、子 Recipe 嵌套。

`goose-zh-06-Recipes可复用工作流.md`　·　5 页　·　源 84,312 B

- **Recipes 可复用工作流**
- **Recipe 参考指南**
    - Recipe 文件格式
    - Recipe 位置
    - Recipe 核心架构
    - 字段规范
    - Desktop 元数据字段
    - 模板支持
    - 验证规则
    - 完整 Recipe 示例
    - 错误处理
    - 了解更多
- **可复用 Recipe**
    - 创建 Recipe
    - 编辑 Recipe
    - 使用 Recipe
    - 验证 Recipe
    - 分享 Recipe
    - 安排 Recipe
    - 核心组件
    - 高级功能
    - 包含的内容
    - 了解更多
- **保存 Recipe**
    - 了解 Recipe 存储
    - 存储 Recipe
    - 查找可用 Recipe
    - 使用已保存的 Recipe
- **用于特定任务的子 Recipe**
    - 子 Recipe 的工作方式
    - 示例
    - 最佳实践
    - 了解更多

### 第 07 章　会话、上下文管理与任务执行

> 会话生命周期、上下文压缩策略、会话内可用动作，以及任务的执行语义。

`goose-zh-07-会话与任务执行.md`　·　5 页　·　源 67,747 B

- **管理会话**
- **会话管理**
    - 启动会话
    - 命名会话
    - 退出会话
    - 搜索会话
    - 恢复会话
    - 复制会话
    - 删除会话
    - 导入会话
    - 导出会话
- **智能上下文管理**
    - goose 如何管理上下文
    - 自动压缩
    - 上下文限制策略
    - 最大轮数
    - Token 使用量
    - 模型上下文限制覆盖
    - 额度余额监控
    - 成本跟踪
- **会话内操作**
    - 编辑消息
    - 消息排队
    - 打断任务
    - 语音听写
    - 拼写检查
    - 在会话中共享文件
    - 会话中途更改
- **运行任务**
    - 基本用法
    - 关键功能
    - 常见用例

### 第 08 章　权限、安全与数据

> 安全模型：对抗模式、提示注入检测、内容分类 API、企业白名单与使用数据。

`goose-zh-08-权限安全与数据.md`　·　6 页　·　源 22,719 B

- **与 goose 安全共处**
- **对手模式**
    - 工作原理
    - 启用对手模式
    - 编写好的规则
    - 哪些内容会被审查
    - 另请参阅
- **提示词注入检测**
    - 检测如何工作
    - 启用检测
    - 基于机器学习的增强检测
    - 另请参阅
- **分类 API 规范**
    - 安全与隐私方面的考量
    - 端点
- **goose 扩展白名单**
    - 工作原理
    - 配置
    - 最佳实践
    - 故障排查
- **匿名使用数据**
    - 收集的使用数据
    - 更改你的偏好设置

### 第 09 章　提供方进阶与多模型

> 多模型切换与子代理分工、ACP 与 CLI 型提供方、Azure AI Foundry，以及漫游 Agent（Roaming）。

`goose-zh-09-提供方进阶与多模型.md`　·　5 页　·　源 50,597 B

- **多模型配置**
- **ACP 提供方**
    - 可用的 ACP 提供方
    - 设置步骤
    - 用法示例
    - 配置选项
    - 错误处理
- **CLI 提供方**
    - 为什么要使用 CLI 提供方？
    - 可用的 CLI 提供方
    - 设置步骤
    - 用法示例
    - 配置选项
    - 工作原理
    - 错误处理
- **Azure AI Foundry**
    - 配置
    - 认证
    - 协议路由
    - 模型元数据与定价
    - 故障排查
- **漫游 Agent**
    - 核心思想：漫游是一种 ACP 传输
    - 工作原理：卡片与相互接受
    - 使用 CLI
    - 把漫游嵌入你自己的应用
    - Web 客户端：一个参考浏览器客户端
    - 已保存的对等方
    - 控制谁可以连接
    - 让 agent 能触达其他 agent
    - 说明与限制

### 第 10 章　CLI 命令与配置文件

> CLI 全命令参考与 `config.yaml` / `settings.json` 的完整键位说明。

`goose-zh-10-CLI命令与配置文件.md`　·　2 页　·　源 49,061 B

- **CLI 命令**
    - 标志命名约定
    - 交互式会话功能
    - 导航与控制
- **配置文件**
    - 配置概览
    - 配置文件
    - 提供方配置
    - 全局设置
    - 示例配置
    - 扩展配置
    - 搜索路径配置
    - 可观测性配置
    - Recipe 命令配置
    - 配置优先级
    - 安全注意事项
    - 更新配置
    - 另请参阅

### 第 11 章　环境变量与运行控制

> 全部环境变量、日志、限流应对、升级与离线文档。

`goose-zh-11-环境变量与运行控制.md`　·　5 页　·　源 50,373 B

- **环境变量**
    - 模型配置
    - 会话管理
    - 工具配置
    - 安全与隐私
    - 网络配置
    - 可观测性
    - goose ACP 服务器
    - Recipe 配置
    - 文档配置
    - 开发与测试
    - 由 goose 控制的变量
    - 环境变量透传
    - 企业环境
    - 注意事项
- **goose 日志系统**
    - 命令历史
    - 会话记录
    - 系统日志
- **设置 LLM 速率限制**
- **更新 goose**
- **离线/气隙环境文档**
    - 文档布局
    - 构建本地文档根目录
    - 配置 goose
    - 注意事项

### 第 12 章　交互界面与实用技巧

> MCP Apps 与对话内 UI、侧栏定制、终端集成、文件管理、代码库分析、MCP elicitation / roots 与实用技巧。

`goose-zh-12-交互界面与实用技巧.md`　·　10 页　·　源 35,859 B

- **基于 MCP Apps 的丰富交互式聊天**
- **使用 MCP Apps**
    - 面向扩展开发者
- **自定义侧边栏**
    - 样式
    - 位置
    - 模式
    - 自定义项目
    - 切换侧边栏
- **终端集成**
    - 设置
    - 用法
    - 命名会话
    - 默认处理器
    - 在提示符中显示上下文状态
    - goose 命令的 Shell 补全
    - 故障排除
- **文件访问与管理**
    - 文件访问
    - 文件管理最佳实践
- **代码库分析**
    - 分析模式
    - 常用参数
    - 最佳实践
- **MCP Elicitation**
    - MCP Elicitation 如何工作
    - 面向扩展开发者
- **MCP Roots**
    - MCP Roots 如何工作
    - 使用 MCP Roots
    - 扩展用它做什么
    - 当前限制
    - 面向扩展开发者
- **goose 快速技巧**
- **自定义发行版**
    - 你可以自定义的内容
    - 快速上手
    - 快速示例：随 goose 一起分发本地模型

### 第 13 章　MCP 扩展（一）：核心内置

> goose 自带的核心 MCP 扩展：Developer、Extension Manager、Apps、Auto Visualiser、Code Mode、Summon、Skills、Todo、Memory、Chat Recall、Knowledge Graph、Fetch、PDF。

`goose-zh-13-MCP扩展一-核心内置.md`　·　14 页　·　源 75,834 B

- **{Extension Name} 扩展**
    - 配置
    - 使用示例
- **Developer 扩展**
    - 配置
    - 使用示例
    - 在 Shell 命令中使用环境变量
    - 配置访问控制
    - 其他资源
- **扩展管理器**
    - 配置
    - 为什么要使用扩展管理器？
    - 可用工具
    - 使用示例
- **Apps 扩展**
    - 配置
    - 使用示例
- **Auto Visualiser 扩展**
    - 配置
    - 可视化类型
    - 工作原理
    - 使用示例
    - 故障排查
- **Code Mode 扩展**
    - 配置
    - 使用示例
- **Summon 扩展**
    - 配置
    - 使用示例
    - 常用的 Summon 命令
- **Skills 扩展**
    - 配置
    - 使用示例
- **Todo 扩展**
    - 配置
    - 使用示例
- **Memory 扩展**
    - 配置
    - 存储位置
    - 工具参考
    - 为什么要使用 Memory？
    - 触发词及使用时机
    - 使用示例
- **Chat Recall 扩展**
    - 配置
    - 使用示例
- **知识图谱记忆扩展**
    - 配置
    - 使用示例
- **Fetch 扩展**
    - 配置
    - 使用示例
- **PDF Reader 扩展**
    - 配置
    - 使用示例

### 第 14 章　MCP 扩展（二）：浏览器与自动化

> 浏览器与自动化类 MCP：Playwright、Puppeteer、Selenium、Chrome DevTools、Browserbase、Computer Controller、Container Use、VS Code、JetBrains。

`goose-zh-14-MCP扩展二-浏览器与自动化.md`　·　9 页　·　源 59,634 B

- **Playwright 扩展**
    - 配置
    - 示例用法
- **Puppeteer 扩展**
    - 配置
    - 示例用法
- **Selenium 扩展**
    - 配置
    - 示例用法
- **Chrome DevTools 扩展**
    - 配置
    - 示例用法
- **Browserbase 扩展**
    - 配置
    - 示例用法
- **Computer Controller 扩展**
    - 配置
    - 示例用法
- **Container Use 扩展**
    - 配置
    - 示例用法
- **VS Code 扩展**
    - 配置
    - 示例用法
    - 结果
- **JetBrains 扩展**
    - 配置
    - 示例用法

### 第 15 章　MCP 扩展（三）：开发与代码

> 开发与代码类 MCP：GitHub、GitMCP、Repomix、Context7、Beads、Excalidraw、Figma、Blender、Ophis、Rendex、Nano Banana。

`goose-zh-15-MCP扩展三-开发与代码.md`　·　11 页　·　源 69,206 B

- **GitHub 扩展**
    - 配置
    - 示例用法
- **GitMCP 扩展**
    - 配置
    - 示例用法
    - 入门检查清单
    - 技巧与最佳实践
- **Repomix 扩展**
    - 配置
    - 示例用法
- **Context7 扩展**
    - 配置
    - 示例用法
- **Beads 扩展**
    - 配置
    - 示例用法
- **Excalidraw 扩展**
    - 配置
    - 示例用法
- **Figma 扩展**
    - 配置
    - 示例用法
- **Blender 扩展**
    - 配置
    - 示例用法
- **Ophis 扩展**
    - Ophis 是什么？
    - 配置
    - 示例用法
    - 资源
- **Rendex 扩展**
    - 配置
    - 示例用法
    - 价格
    - 链接
- **Nano Banana 扩展**
    - 配置
    - 示例用法

### 第 16 章　MCP 扩展（四）：数据与云服务

> 数据与云服务类 MCP：Postgres、MongoDB、Supabase、Neon、DataHub、OpenMetadata、Cloudflare、Vercel、Netlify、Cloudinary、VMware AIOps、Linux。

`goose-zh-16-MCP扩展四-数据与云服务.md`　·　12 页　·　源 78,879 B

- **PostgreSQL 扩展**
    - 自定义你的连接
    - 配置
    - 示例用法
- **MongoDB 扩展**
    - 自定义你的连接
    - 配置
    - 可用操作
    - 示例用法
- **Supabase 扩展**
    - 配置
    - 示例用法
    - 其他资源
- **Neon 扩展**
    - 配置
    - 示例用法 1
    - 示例用法 2
    - 示例用法 3
- **DataHub 扩展**
    - 什么是 DataHub？
    - 前提条件
    - 配置
    - 示例用法
    - 能力
    - 资源
    - 故障排查
- **OpenMetadata 扩展**
    - 自定义你的连接
    - 配置
    - 可用操作
    - 示例用法
- **Cloudflare 扩展**
    - 可用的 Cloudflare MCP 服务器
    - 前提条件
    - 配置
    - 示例用法
    - 常见使用场景
    - 最佳实践
    - 故障排查
    - 后续步骤
- **Vercel 扩展**
    - 配置
    - 示例用法
- **Netlify 扩展**
    - 配置
    - 示例用法
    - 部署详情：
    - 部署了什么：
    - 后续步骤：
    - 未来更新：
- **Cloudinary 资产管理扩展**
    - 配置
    - 示例用法
- **VMware AIops 扩展**
    - 配置
    - 示例用法
- **Linux MCP 服务器扩展**
    - 配置
    - 示例用法

### 第 17 章　MCP 扩展（五）：协作与办公

> 协作与办公类 MCP：Asana、Google Drive、Google Maps、Square、Cash App、Alby、Pieces、Tom、GoToHuman、dev.to、Reddit、Nostrbook、Neighborhood、Council of Mine。

`goose-zh-17-MCP扩展五-协作与办公.md`　·　14 页　·　源 83,498 B

- **Asana 扩展**
    - 配置
    - 示例用法
- **Google Drive 扩展**
    - 配置
    - 示例用法
- **Google Maps 扩展**
    - 配置
    - 示例用法
- **Square MCP 扩展**
    - 配置
    - 示例用法
- **Cash App 扩展**
    - 快速安装
    - 配置
    - 你可以做什么
    - 示例提示词
- **Alby 比特币支付扩展**
    - 配置
    - 示例用法
- **Pieces for Developers 扩展**
    - 配置
    - 示例用法
- **Top Of Mind 扩展**
    - 配置
    - 示例用法
- **gotoHuman 扩展**
    - 配置
    - 示例用法
    - 在 gotoHuman 中评审
- **Dev.to 扩展**
    - 配置
    - 示例用法
- **Reddit 扩展**
    - 配置
    - 示例用法
- **Nostrbook 扩展**
    - 配置
    - 示例用法
    - NIP-61：实现 Nutzaps
- **Neighborhood 扩展**
    - 快速安装
    - 配置
    - 示例用法
    - 视频演示
- **Council of Mine 扩展（已退役）**

### 第 18 章　MCP 扩展（六）：搜索与信息获取

> 搜索与信息获取类 MCP：Brave、Exa、Tavily、Firecrawl、Apify、AgentQL、Scholar Sidekick、YouTube Transcript、Kiwi 航班搜索、Speech、ElevenLabs、Prompts.chat、Tutorial、Goose Docs。

`goose-zh-18-MCP扩展六-搜索与信息获取.md`　·　14 页　·　源 96,924 B

- **Brave Search 扩展**
    - 配置
    - 示例用法
- **Exa Search 扩展**
    - 配置
    - 示例用法
- **Tavily 网页搜索扩展**
    - 配置
    - 示例用法
- **Firecrawl 扩展**
    - 配置
    - 示例用法
- **Apify 扩展**
    - 配置
    - 示例用法
- **AgentQL 扩展**
    - 配置
    - 示例用法
- **Scholar Sidekick 扩展**
    - 配置
    - 可选：更高的速率限制
    - 你可以做什么
- **YouTube Transcript 扩展**
    - 配置
    - 示例用法
- **Kiwi 航班搜索扩展**
    - 配置
    - 示例用法
- **Speech 扩展**
    - 配置
    - 示例用法
- **ElevenLabs 扩展**
    - 配置
    - 示例用法
- **prompts.chat 扩展**
    - 配置
    - 示例用法
- **Tutorial 扩展**
    - 配置
    - 可用的教程
    - 使用 Tutorial 扩展
    - 示例用法
    - 后续步骤
- **goose Docs 扩展**
    - 配置
    - 示例用法

### 第 19 章　教程（一）：扩展与集成实战

> 动手实战：自定义扩展、构建 MCP App、Playwright Skill、Spraay MCP、Docker 运行、隔离开发环境、CI/CD、无头 goose。

`goose-zh-19-教程一-扩展与集成实战.md`　·　8 页　·　源 74,652 B

- **构建自定义扩展**
    - 前置条件
    - 第 1 步：初始化你的项目
    - 第 2 步：编写你的 MCP 服务器代码
    - 第 3 步：定义项目配置
    - 第 4 步：测试你的 MCP 服务器
    - 第 5 步：与 goose 集成
    - 第 6 步：在 goose 中使用你的扩展
    - MCP Apps：交互式扩展
- **构建 MCP 应用**
    - 第 1 步：初始化你的项目
    - 第 2 步：创建 MCP 服务器
    - 第 3 步：创建应用 HTML
    - 第 4 步：添加到 goose Desktop
    - 第 5 步：测试你的应用
    - 工作原理
- **使用 Playwright CLI Skill 进行智能体测试**
    - 为什么作为 Skill？
    - 前置条件
    - 配置
    - 生成带视频和 Trace 的测试
    - 查看视频
    - 查看 Trace
    - 多会话的可视化仪表盘
    - 完整能力
    - 结论
    - 资源
- **Spraay x402 扩展**
    - 支持的工具
    - 设置
    - 使用示例
    - 工作原理
    - 资源
- **在 Docker 中运行 goose**
    - 在 Docker 内运行 goose
    - 在 Docker 容器中运行扩展
- **隔离开发环境**
    - 概述
    - 前置条件
    - 设置
    - 用法
    - 优势
    - 常见工作流
    - 故障排除
    - 下一步
- **CI/CD 环境**
    - 在 GitHub Actions 中使用 goose
    - 并行运行多个 goose 实例
    - 安全考量
- **使用无头模式自动化**
    - 什么是无头模式？
    - 交互式 vs. 无头：理解差异
    - 带命令示例的真实用例
    - 无头模式成功的最佳实践
    - 无头模式下的 Recipe 执行
    - 理解局限性
    - 配置和环境设置
    - 自动化开发的未来

### 第 20 章　教程（二）：工作流与可观测性

> 工作流与可观测性：Ralph Loop、RPI（Research→Plan→Implement）、子代理、并行子 Recipe、Recipe 教程，以及 Langfuse / Laminar / MLflow / Clawmetry / Remotion。

`goose-zh-20-教程二-工作流与可观测性.md`　·　10 页　·　源 85,397 B

- **Ralph Loop**
    - 工作原理
    - 使用技巧
- **Research → Plan → Implement 模式**
    - 先决条件
    - RPI 工作流
    - 任务
    - 会话 1：研究
    - 会话 2：规划
    - 会话 3：实施
    - 最终结果
    - 何时使用 RPI
- **使用子代理**
    - 设置
    - 任务
    - 测试完成的应用
    - 故障排除
- **并行运行子 recipes**
    - 工作原理
    - 示例
    - 在执行模式之间进行选择
    - 了解更多
- **Recipes**
    - 最简单的 Recipe
    - 扩展
    - 参数
    - 设置
    - 外部文件
    - 10 天欧洲探险行程
    - 了解更多
- **使用 Langfuse 实现可观测性**
    - 什么是 Langfuse
    - 设置 Langfuse
    - 配置 goose 以连接 Langfuse
    - 使用 Langfuse 集成运行 goose
- **使用 Laminar 实现可观测性**
    - 什么是 Laminar
    - 为什么 goose 适合使用 Laminar
    - 设置 Laminar
    - 配置 goose 将 OTLP 导出到 Laminar
    - 启用 Laminar 后运行 goose
- **使用 MLflow 实现可观测性**
    - 什么是 MLflow
    - 为什么 goose 适合使用 MLflow
    - 设置 MLflow
    - 配置 goose 将 OTLP 导出到 MLflow
    - 启用 MLflow 后运行 goose
    - 了解更多
- **使用 ClawMetry 实现可观测性**
    - 什么是 ClawMetry
    - 为什么 goose 适合使用 ClawMetry
    - 设置 ClawMetry
    - 运行 goose
    - 你可以看到的内容
    - 了解更多
- **使用 Remotion Skills 创建视频**
    - 配置
    - 使用示例

### 第 21 章　架构、远程部署与 GDK

> 架构总览、扩展设计、错误处理，远程 goose 服务器、Tanzu AI Services，以及 GDK（ACP / SDK）。

`goose-zh-21-架构远程部署与GDK.md`　·　11 页　·　源 48,778 B

- **goose 架构**
    - goose 组件
    - 与扩展的互操作性
    - Agent Client Protocol (ACP)
    - 交互循环
    - goose 中的错误处理
    - 上下文修订：token 管理
- **扩展设计**
    - 核心概念
    - 架构
    - 最佳实践
    - 测试
- **错误处理**
    - 传统错误
    - 代理错误
- **运行远程 goose 服务器**
    - 初始设置
    - 将 `goose serve` 作为后台服务运行（macOS）
    - 故障排查
    - 相关
- **VMware Tanzu Platform**
    - 前提条件
    - 第 1 步：检查可用计划
    - 第 2 步：创建服务实例
    - 第 3 步：创建服务密钥
    - 第 4 步：确定你的端点和 API 密钥
    - 第 5 步：配置 goose
    - 第 6 步：选择模型
    - 故障排查
- **VMware Tanzu Platform - CLI 测试指南**
    - 前提条件
    - 定位 CLI 二进制文件
    - 测试 1：配置 VMware Tanzu Platform 提供方
    - 测试 2：启动会话（单模型计划）
    - 测试 3：启动会话（多模型计划）
    - 测试 4：验证流式传输
    - 测试 5：验证动态模型获取
    - 测试 6：验证错误消息
    - 测试 7：在计划之间切换
    - 快速 Curl 验证
- **GDK 概览**
- **将 goose 用作 ACP Agent**
    - 安装
    - 运行代理
    - ACP 客户端示例
- **在 Zed 中设置 goose**
    - 从 ACP Registry 安装 goose
    - 手动配置 goose
    - 覆盖提供方和模型
    - 将 Zed MCP 服务器与 goose 一起使用
- **SDK**
    - 你可以做什么
    - 安装
    - 快速开始
    - Kotlin 惯用法
    - 声明式提供方
    - 流式模型
- **SDK 参考**

### 第 22 章　排错与实验特性

> 排错与实验特性：已知问题、诊断与上报、桌面端启动调试，以及 goose Mobile、Ollama、VS Code 扩展、Telegram 网关等实验功能。

`goose-zh-22-排错与实验特性.md`　·　12 页　·　源 47,631 B

- **排错**
- **已知问题**
    - goose 会编辑文件
    - 中断 goose
    - 陷入循环或无响应
    - 防止长时间运行的命令
    - 上下文长度超限错误
    - 使用 Ollama 提供方
    - 处理速率限制错误
    - Hermit 错误
    - API 错误
    - GitHub Copilot 提供方配置
    - 新 Recipe 警告
    - 卸载 goose 或移除缓存数据
    - 钥匙串/密钥环错误
    - 无法访问密钥环（自动回退）
    - 包运行器
    - Node.js 扩展在 Windows 上无法激活
    - 检测到恶意包
    - macOS 权限问题
    - WSL 上 Ollama 提供方的连接错误
    - 企业代理或防火墙问题
    - 隔离/离线环境问题
    - 需要更多帮助？
- **诊断与上报**
    - 诊断系统
    - 使用诊断数据
    - 缺陷报告
    - 功能请求
    - 使用「Ask goose」进行错误恢复
    - 其他调试
- **调试桌面版启动失败**
    - 找到启动诊断日志
    - 需要分享什么
    - 启动日志包含什么
    - 相关诊断
- **实验特性**
- **goose Mobile**
    - 它能做什么
    - 安装
    - 扩展 goose Mobile
    - 贡献
- **通过安全隧道进行移动端访问**
- **Ollama Tool Shim**
- **goose for VS Code 扩展**
    - 安装扩展
    - 与 goose 共享上下文
    - 用法示例
- **远程访问**
- **通过安全隧道进行移动端访问**
- **Telegram 网关**
    - 工作原理
    - 前置条件
    - 设置
    - 你能做什么
    - 排错
    - 其他资源

### 第 23 章　博客（一）：2024-11 ~ 2025-03

> 官方博客存档（一）：2024-11 ~ 2025-03 共 20 篇。goose 起源、MCP 入门、企业级 MCP、Vibe Coding、社区访谈。

`goose-zh-23-博客一.md`　·　20 页　·　源 148,619 B

- **截图驱动的开发**
    - 开始使用截图驱动的开发
    - 了解更多
- **预览 goose v1.0 Beta**
    - goose 1.0 Beta 的激动人心的特性
- **用 MCP 把 AI Agent 连接到你的系统**
- **用 goose 解决 CI 问题：一次实战演练**
    - 快速上手
    - 用 goose 解决 CI 失败
    - 使用 goose 的好处
- **介绍 codename goose**
    - goose 如何工作
    - goose 实战
    - 快速上手
    - 加入 goose 社区
- **Agentic AI 与 MCP 生态**
    - 什么是 AI Agent？
    - AI Agent 如何与 LLM 协同工作
    - MCP 生态
    - 开始使用 AI Agent
- **让一支 AI Agent 团队替你干活**
    - 最初的协议
    - gooseTeam MCP 服务器
    - 使用 goose 的新方式
    - 让你的贡献获得展示
- **使用 goose 的 6 条必备技巧**
    - 1. 让会话保持专注且简短
    - 2. 尽量减少启用的扩展
    - 3. 用 .goosehints 文件教 goose
    - 4. 为你的工作流选择合适的模式
    - 5. 用分步执行引导 goose
    - 6. 为更好的回答而打磨与迭代
- **用 goose 自动拨打电话**
    - 用 AI 驱动的电话扩展 goose 的触达范围
    - 工作原理
    - 现场演示：AI 通话实战
    - 开始使用 goose 与 VOYP
- **用 goose 把 Figma 设计稿变成代码**
    - 工作原理
    - 现场教学：goose 现场构建
    - 开始使用 goose 与 Figma
- **AI，但要本地化：goose 与 Ollama**
    - 快速上手
    - 为什么要本地化？
    - 我的机器能扛得住吗？
    - 结构化输出的魔力
    - 关键在于选择的自由
- **goose 如何借助 Langfuse 捕获 AI 错误**
    - 什么是 Langfuse
    - Langfuse 如何与 goose 协作
    - 实际收益
    - AI 可观测性的未来
- **AI 提示词入门：如何从你的 AI Agent 获得最佳回答**
    - 基于指令的提示
    - 思维链提示
    - 少样本提示
    - 迭代式改进提示
    - 零样本提示
    - 基于礼貌的提示
    - 最好的提示词感觉自然
- **我如何用 goose 结合 Asana 与 Google Calendar MCP 规划一周**
- **Codename Goose 走进波士顿**
    - 我们为什么举办这次聚会
    - 如果你错过了
    - 我们喜爱的瞬间
    - 影响与下一步
- **用 VS Code MCP 破解编码难题**
    - 什么是 VSCode MCP？
    - 关键特性
    - VSCode MCP 的下一步是什么？
    - 社区与贡献
- **如何判断一个 MCP 服务器是否安全**
    - 我在接入之前如何审查 MCP 服务器
    - 在信任一个 MCP 服务器之前我会做的事
    - Glama 评什么分
- **用 Goose 与 Speech MCP 进行 vibe coding**
    - Speech MCP 服务器
    - 现场演示亮点
    - 快速上手
    - 加入开发
- **社区启发的基准测试：Goose Vibe Check**
    - 排行榜
    - 开源模型详情
    - 关键结果
    - 方法与论
    - 开源模型的技术挑战
    - 给本地模型用户的实用建议
    - 运行你自己的基准测试
    - 未来工作
    - 结果评估示例
- **保护 Model Context Protocol 的安全**
    - 什么是 Model Context Protocol（MCP）
    - 关于 MCP 的误解
    - 我们如何着手让它变得安全？
    - 结论

### 第 24 章　博客（二）：2025-04 ~ 2025-05

> 官方博客存档（二）：2025-04 ~ 2025-05 共 18 篇。Top 5 MCP Server、视觉化 MCP 指南、Recipe 实践、负责任 Vibe Coding。

`goose-zh-24-博客二.md`　·　18 页　·　源 140,081 B

- **面向非开发者的 MCP 讲解**
    - 什么是 MCP？
    - 你现在就该试试的 MCP 服务器
    - 示例 MCP 提示词
    - 可能性无穷无尽
- **作为开发者，我最常与 Goose 搭配使用的 5 个 MCP 服务器**
    - GitHub MCP Server：GitHub 的一切
    - Knowledge Graph Memory：开了外挂的上下文
    - Fetch 扩展：网络尽在掌握
    - Memory 扩展：我的习惯与偏好
    - VS Code 扩展：你最喜欢的编辑器，已接入
    - 集成的力量
- **如何负责任地进行 Vibe Coding（借助 goose）**
    - Vibe Coding 的阴暗面
    - 用 goose 更好地 Vibe Code
    - 观看 Vibe Coding 实战
    - 最后感想
- **MCP 生态系统的可视化指南**
    - 用大白话解释 MCP 是什么？
    - 都有哪些角色？
    - 它们如何通信？
    - 来个类比
    - 轮到你了
- **为工具调用微调 Toolshim 模型**
    - 为什么工具调用很重要
    - 背景：使用本地模型作为「toolshim」
    - 提案：微调一个轻量级 toolshim 模型（最高 12b）
    - 关于当前工具调用生成挑战的关键观察
    - 实验方法
    - 未来方向
- **ATrueLight4 如何帮助 Goose 适配 Windows**
    - Windows 支持
    - ATrueLight4 的 Goose4Win
    - 争取你自己的高光时刻
- **Codename Goose 登陆纽约**
    - 我们为什么把 Goose 带到纽约
    - 万一你错过了
    - 大家怎么说
    - 我们喜欢的瞬间 ❤️
    - 下一站：Goose 南下 🛫
    - 衷心感谢 🙌
- **MCP 在企业中：Block 的真实落地实践**
    - 我们为什么在 Block 选择 MCP
    - 我们如何配置和保护 MCP
    - 真实的故事，真实的影响
    - 到目前为止我们学到了什么
    - 接下来
    - 想了解更多？
- **我在不丢失真实感的前提下使用 AI Agent 的 11 种实用方式**
    - 1. 🙌🏿 免手编码
    - 2. 🎤 准备播客议程
    - 3. 🖼 调整图片尺寸
    - 4. 📝 对照职位列表审阅简历
    - 5. 🧠 理解习语
    - 6. 📊 查询关系型数据库
    - 7. 🗓 规划我的大会演讲策略
    - 8. 🐞 追查引入 bug 的提交
    - 9. 👩🏾‍🏫 学习新技术
    - 10. 💼 对比法规文档
    - 11. 🛠 快速制作想法原型
    - 想找更多例子？
- **一次贡献如何激起一连串的成果**
    - BestCodes 是如何发现 Goose 的
    - 积攒势头
    - 成为顶级贡献者
- **MCP 正在改写 API 集成的规则**
    - 引言：你的 API 的智能化演进
    - 从静态端点到智能交互
    - 集成 AI 与 MCP：驾驭这一格局
    - 衡量成功：量化影响
    - 我们接下来往哪走？
    - TL;DR 常见问题
- **使用 Goose 前你*实际上*需要了解的 4 件事**
    - 等等——Goose 到底是什么？
    - 1. 选择合适的 LLM
    - 2. 理解 MCP 服务器是什么
    - 3. 可能*会*有成本
    - 4. 融入社区
- **成功的 Recipe：烹制可复用的 Agentic 工作流**
    - Remy 与 Linguini 的互动关系
    - 传统 AI Agent
    - Linguini 的成长
    - 天生不同
    - Goose 作为统筹者
    - 用 Recipe 扩展 Agentic 工作流
    - 可复用的 Agentic 工作流
- **冠军级驱动开发：你团队的 AI 战术手册，助你达到巅峰表现**
    - 开发者的战术手册：用 AI 提升团队效率
    - 理解现代开发团队面临的挑战
    - 使用 AI 战术手册的好处
    - AI 战术：标准化你团队的工作流
    - Goose Recipe：你战术手册的构建模块
    - 给你的团队的入门 AI 战术包
    - 你的团队可以自动化哪些类型的任务？
- **用 Goose 与 Qwen3 实现本地执行**
    - 本地工作流与本地 agent
    - Qwen3 的推理
    - 进阶技巧
- **Goose 拿到驾照啦！**
    - 我教会了 Goose 开车（一辆漫游车）
    - MQTT 入门
    - 设置 mbot2
    - 设置本地 MCP 服务器
    - Goose 学开车！
    - 为视频所做的 Goose 改动
    - 鸣谢
- **测试 Agent 就绪度的 3 个提示词**
    - 工具调用
    - 记忆感知
    - 文件系统推理
- **我如何用 AI Agent 管理 localhost 端口冲突**
    - Localhost 端口囤积
    - 传统的端口管理
    - 把 Goose 当作我的端口管理器
    - 为什么要用 AI 做简单的任务

### 第 25 章　博客（三）：2025-06 ~ 2025-07

> 官方博客存档（三）：2025-06 ~ 2025-07 共 10 篇。多模型协作、隔离开发环境、子代理编排、本地模型、社区运营。

`goose-zh-25-博客三.md`　·　10 页　·　源 136,732 B

- **在 Block 让检测工程大众化：与 Goose 和 Panther MCP 一同起飞**
    - 检测工程的挑战
    - 愿景
    - 认识 Panther MCP
    - 用 Goose 加速检测创建
    - 打破壁垒
    - 简洁背后的智能
    - 大众化实践
    - 早期成效与经验教训
    - 下一步是什么？
- **我的 .goosehints 文件里有什么（以及为什么它多半不该有这些）**
    - AI Agent 与记忆
    - .goosehints 与 Memory 扩展在 Goose 中如何使用？
    - .goosehints 与 Memory 扩展的差异意味着什么
    - 我在 .goosehints 上犯的错
    - 其余一切都搬进了 Memory 扩展
    - 要不要用 hint？
- **把 LLM 当作工具箱里的工具：通往更聪明 AI Agent 的多模型方案**
    - 单模型会话的问题
    - 设计 Lead/Worker 系统
    - 多模型设计的价值
    - 试一试
- **我为什么用 Goose 打造一个混乱的情绪检测应用**
    - 我的策略
    - 结果
    - 玩玩没什么不好
    - 试一试
- **Goose 中借助 container-use 的隔离开发环境**
    - 纯本地开发的问题
    - 更安全的替代方案：隔离开发环境
    - 快速上手
    - 真实使用场景
    - 指南
- **我今天交给 AI Agent 的 5 项枯燥任务（它们为我省下了好几个小时）**
    - 1️⃣ 把 GitHub 活动汇总为可付诸行动的洞见
    - 2️⃣ 从冗长的 Slack 线程里提取行动项
    - 3️⃣ 从社区反馈中制定路线图
    - 4️⃣ 修好我的 CSS 断点（因为我放弃了）
    - 5️⃣ 在大型文档重构后修复失效链接
- **编排 6 个子代理，为孩子们打造一个协作式 API 游乐场**
    - 认识这些子代理
    - 给我的团队下指令
    - 我的并行提示词翻车了
    - 更好的提示词策略
    - 最后的思考
- **当 AI 遇见 AI：Goose Desktop 与 CLI 协作**
    - 对话亮点
    - 两个 Goose 实例之间的对话
    - Angie's Diner 销售报告
- **用 Goose Recipe 精简检测开发**
    - 什么是 Recipe？
    - 架构
    - 数据流与状态管理
    - 智能优化：条件执行
    - 深入剖析：关键子 Recipe
    - 错误处理与快速失败设计
    - 实用示例
    - 标准合规与质量保证
    - 收益与影响
    - 结论
    - 最佳实践与经验教训
- **OpenRouter 如何为我们的工作坊策略打开局面**
    - LLM 成本问题
    - 我们考虑过的既有方案
    - 发现 OpenRouter
    - 构建 Web 应用
    - 即将到来的丹佛工作坊
    - 未来的改进
    - 为什么这种方式很重要

### 第 26 章　博客（四）：2025-08

> 官方博客存档（四）：2025-08 共 15 篇。MCP UI 系列、上下文窗口原理、Mentor Mode、Auto Visualiser、Agent 协作模式。

`goose-zh-26-博客四.md`　·　15 页　·　源 136,286 B

- **MCP Jupyter：AI 驱动的机器学习与数据科学**
    - 记忆与上下文问题
    - 更好的方法：持久状态
    - 变革 ML 工作流
    - 示例 notebook
    - 快速开始
- **7 个 AI 智能体如何在一小时内协作构建出一个应用**
    - 多智能体开发的力量
    - 工作坊体验
    - 实时得到的真实结果
    - 人类依然重要
    - 开发的未来
    - 开始使用子代理
- **LLM 组队：谁规划，谁执行？**
    - 这个 Lead/Worker 到底是怎么回事？
    - 为什么你会喜欢这套配置
    - 配置方法
    - 实战中的魔法
    - 开发者体验
    - 来自我们这次会话的实用建议
    - 结果说明一切
    - 准备好尝试多模型工作流了吗？
- **MCP UI：把浏览器带进智能体**
    - 我该怎么用
    - MCP-UI 背后的技术
    - 可能的未来
- **自动化 MCP 测试：用可组合的 Goose Recipe 校验工具元数据**
    - 自动化 MCP 测试：用可组合的 Goose Recipe 校验工具元数据
    - 1. 手工元数据测试的挑战
    - 2. 系统概览：模块化且可组合的 Goose Recipe
    - 3. 核心引擎：用于工具预测的 Goose Recipe
    - 4. 工作流 1：自动化的元数据回归检测
    - 5. 工作流 2：安全的元数据 token 削减与优化
    - 6. 结语
- **PulseMCP 如何用 Goose 自动化他们的时事通讯工作流**
    - 挑战
    - 解决方案：为什么顺序化胜过单体化
    - 六智能体流水线
    - 帮助人类，而非取代他们
    - 未来的一瞥
    - 蓝图已经公开
    - 接下来是什么？
- **智能体、子代理与多智能体：它们是什么，何时该用**
    - 智能体：孤胆英雄模式
    - 子代理配置：带着一队人的编排者
    - 多智能体场景：两个主脑互相商量
    - 何时该用哪种
- **我如何用 Goose 重建我的网站**
    - 回到我的根
    - 开启这一切的 404 挑战
    - 实现
    - 永远要用 Git
    - 一个巨大的省时利器，说真的
- **把 AI 辅助从自动化转变为教育：Goose Mentor Mode 背后的故事**
    - 把 AI 辅助从自动化转变为教育：Goose Mentor Mode 背后的故事
- **AI 怀疑论者的上下文窗口指南**
    - 什么是上下文窗口？
    - 什么是 token？
    - Goose 如何自动管理你的上下文窗口
    - 如何管理你的上下文窗口
- **我让 Goose 构建了它自己的安全 Recipe 扫描器**
    - Headless 方案
    - 它是如何运作的
    - Headless 模式下的 Goose
    - 学习曲线
    - 构建社区信任
    - 用 AI 审查 AI，来审查提交
- **MCP-UI：智能体界面的未来**
    - 纯文本界面的问题
    - MCP-UI 登场：弥合鸿沟
    - MCP-UI 如何运作
    - 实战中的真实示例
    - 技术基础
    - 利益相关方生态
    - 展望未来：未来是可视化的
    - 采用方面的挑战
    - 快速开始
    - 底线
- **用 MCP-UI 实现自动可视化**
    - 什么是 Auto Visualiser？
    - 可视化类型
- **你的第一次 goose 体验，我们请客**
    - Tetrate 的 Agent Router Service
    - 为什么这次合作很重要
    - 探索完整的模型目录
- **当 AI 成为你的新团队成员：Goose Janitor 的故事**
    - 阶段 1：让知识可被 AI 访问
    - 阶段 2：跨代际的验证
    - 阶段 3：构建一个 AI 团队成员
    - 更大的图景：AI 优先的开发
    - AI 优先的心态
    - 接下来是什么？

### 第 27 章　博客（五）：2025-09 ~ 2025-12

> 官方博客存档（五）：2025-09 ~ 2025-12 共 19 篇。子 Recipe、ACP 协议、Code Mode、Agent Skills vs MCP、移动端终端、MCP sampling。

`goose-zh-27-博客五.md`　·　19 页　·　源 176,703 B

- **如何让 MCP 服务器兼容 MCP-UI**
    - 我为什么想要这个
    - 通用模式
    - 第 3 步：我的 Cloudinary UI
    - 第 4 步：看看这个 diff 有多小
    - Filesystem：同样的模式
    - 走在前面
    - 自己动手试试
- **用 goose 中的子 Recipe 自动化你的复杂工作流**
    - 为什么子 Recipe 很重要
    - 一个真实案例：项目搭建自动化
    - 为不同任务定制专用子 Recipe
    - 子 Recipe 的调试技巧
    - 更多子 Recipe 工作流
    - 编排式 AI 的未来
    - Recipe 提交已关闭
- **goose 正在庆祝 Hacktoberfest 2025！**
    - 📌 什么是 Hacktoberfest？
    - 🎉 我能如何为 goose 做贡献？
    - 📝 goose x Hacktoberfest 2025 指南
- **如何在 goose 中选择子代理与子 Recipe**
    - 核心区别：要不要复用
    - 子代理：快速而灵活
    - 子 Recipe：结构化且可复用
    - 决策框架
    - 两种方案的共同优点与局限
    - 开始使用
    - 由你决定
- **为 goose 构建你自己的 Recipe Cookbook 生成器**
    - 手动创建 Recipe 的问题
    - 什么是 Cookbook 生成器 Recipe？
    - Vibe 提示过程
    - 生成器的核心特性
    - 真实效果
    - 元自动化的优势
    - 增量更新
    - 元编程的未来
    - Recipe 提交已关闭
    - 我自己的 Cookbook 生成器 Recipe
- **为用户而设计 AI，而不只是为 LLM**
- **Agent Client Protocol（ACP）入门：AI Agent 与编辑器集成的标准**
    - 三应用难题
    - 常见的变通方案
    - 引入 Agent Client Protocol
    - 恢复开发者的心流
    - 看 ACP 实际运行
- **如何用 AI Agent 成功迁移你的应用**
    - 我为什么需要重构
    - 我的提示词策略
    - 经验教训
- **构建一个社交媒体 Agent**
    - 计划
    - 构建内容抓取器
    - Sprout Social 这一侧
    - 试一试
    - 那我们要怎么真正实现自动化？
    - 写得像个人
    - 遇到的小问题
    - 下一步
    - 感受
    - 观看完整直播
- **写给觉得自己不需要 MCP 的开发者**
    - GitHub：不只是 CLI
    - Context7：不烂的文档
    - Repomix：不读代码也能了解整个代码库
    - Chrome DevTools MCP：边写代码边做 Web 测试
- **宣布 Advent of AI**
    - 你的任务
    - 面向所有技能水平
    - 运作方式
    - 准备好动手了吗？
- **MCP Sampling：当你的工具需要思考时**
    - Sampling 如何工作
    - 真实案例：Council of Mine
    - Sampling 的好处
    - 何时使用 Sampling
    - 机制细节
    - 安全考量
- **如何阻止你的 AI Agent 做出不想要的代码改动**
    - 1. 配置版本控制
    - 2. 先建分支
    - 3. 在上下文文件中设置规则
    - 4. 放心协作
    - 结果
- **goose 中的 Code Mode MCP**
    - Code Mode MCP
    - 方法
    - 在 goose 中
    - 帮我们评估它
- **你的 AI Agent 需要一个计划吗？**
    - 你的 AI Agent 需要一个计划吗？
    - 选择你的策略
    - 你是哪种风格？
- **goose 移动端访问与原生终端支持**
    - 使用 goose 的 2 种新方式
    - goose iOS 应用
    - 原生终端支持
    - 按你的方式使用 goose
- **Code Mode 并不会取代 MCP（它实际做了什么）**
    - 「扩展太多」的问题
    - 让扩展动态化
    - Code Mode 详解
    - Code Mode 并不会取代 MCP
    - 用 Code Mode 与不用 Code Mode
    - Code Mode 的价值
    - 改进 goose 中的 Code Mode 支持
- **Skill 杀死了 MCP 吗？**
- **我们如何用 goose 维护 goose**
    - 在 GitHub Action 之前
    - 用 GitHub Action 实现规模化
    - 幕后揭秘

### 第 28 章　博客（六）：2026-01 ~ 2026-02

> 官方博客存档（六）：2026-01 ~ 2026-02 共 15 篇。MCP Apps、上下文工程、RPI 方法论、设计品味、8 个 Code Mode 冷知识。

`goose-zh-28-博客六.md`　·　15 页　·　源 154,945 B

- **我如何教会我的 Agent 我的设计品味**
    - 灵感来源
    - Harness 对比 Skills
    - 关于品味
    - 扩展视觉反馈循环
    - 我学到了什么
    - 查看代码
- **Agent 护栏与控制：将 CORS 模型应用于 Agent**
    - 威胁模型 {#threat-model}
    - 既有的技术与控制
    - 提议的设计
    - 注意事项与局限
    - 结论与后续步骤
- **goose 支持 MCP Apps**
    - 本次发布的内容
    - 什么是 MCP Apps？
    - 这是实验性的
    - MCP-UI 的过渡
    - 试用
- **为什么工具描述还不够**
    - 真正改变了我理解的东西
    - Council of Mine 在其中扮演的角色
    - 我的结论
- **goose 移动应用与 agent 客户端**
    - 移动客户端路线图
- **从 MCP-UI 到 MCP Apps：演进交互式 Agent UI**
    - 为什么我决定更进一步
    - MCP Apps 实际改变了什么
    - 我如何处理迁移
    - 模式转变：UI 不再内联
    - 从 MCP-UI 迁移到 MCP Apps 时的 4 个关键变化
    - 自己试试
- **构建可用 MCP Apps 的 5 个技巧**
    - MCP Apps 的 UI 渲染方式概览
    - 技巧 1：适配宿主环境
    - 技巧 2：控制模型看到什么、View 看到什么
    - 技巧 3：正确处理加载状态和错误状态
    - 技巧 4：让模型保持在回路中
    - 技巧 5：控制谁可以触发工具
    - 用 goose 和 MCPJam 开始构建
- **关于 Code Mode 你不知道的 8 件事**
    - 1. Code Mode 不是 MCP 杀手
    - 2. goose 支持 Code Mode
    - 3. Code Mode 让你的上下文窗口保持干净
    - 4. Code Mode 把操作批量合并成单次工具调用
    - 5. Code Mode 做出更聪明的工具选择
    - 6. Code Mode 跨编辑器可移植
    - 7. Code Mode 在不同 LLM 上表现不同
    - 8. Code Mode 并非适用于所有任务
    - 试一试
- **用 rp-why 提升你的 AI 游戏**
    - 什么是 rp-why？
    - 问题
    - 两个维度
    - 象限图
    - 输出看起来是什么样
    - 提示词的即时升级
    - 每周工作流整合
    - 把你的成长游戏化
    - 现在就开始
    - FAQ
    - 署名
- **我如何使用 RPI 构建一个 OpenClaw 替代品**
    - 选择 RPI
    - 收获
    - 试一试
- **一次性提示词已死**
    - 那篇比燕麦奶过期还快的博客文章
    - 那个崩坏的抽象
    - 我实际该怎么做？
    - 对于思考超越代码的人来说这是好消息
    - 真正的技能是编排
- **Gas Town 详解：如何用 Goosetown 进行并行 agentic 工程**
    - Agentic 工程的范式转变
    - Gas Town 详解
    - 介绍 Goosetown
    - 来自创建者的一段话
    - 开始使用
- **goose v1.25.0：沙箱化、精简且更安全**
    - 🔒 macOS 沙箱化
    - 🧩 统一的 Summon 扩展
    - 🖼️ MCP Apps UI 集成
    - 📝 从 GUI 编辑 Recipe 的模型与提供方
    - 🤖 Agentic CLI 提供方升级
    - ✨ CLI 中的流式 Markdown
    - 🛡️ SLSA 构建溯源
    - 开始使用
- **资助获得者：Goose In A Pond**
    - 什么是 Goose In A Pond？
    - 他们正在构建的 MCP
    - 认识 Jarida 团队
    - 接下来是什么
- **不离开你的 AI Agent 就能点午餐**
    - 设置 Neighborhood 扩展
    - 找到真正适合你的餐厅
    - 在聊天中浏览带图片的菜单
    - 组建订单
    - 结账，你唯一离开 goose 的时刻
    - 为什么这很重要
    - 自己试试
    - 观看完整演示

### 第 29 章　博客（七）：2026-03 ~ 2026-09

> 官方博客存档（七）：2026-03 ~ 2026-09 共 15 篇。WebMCP 入门、订阅式接入、对抗模式、Agent 状态机、AAIF 迁移、自改进 Agent。

`goose-zh-29-博客七.md`　·　15 页　·　源 84,201 B

- **WebMCP 入门**
    - 什么是 WebMCP？
    - WebMCP 不是 MCP
    - WebMCP 为什么存在
    - WebMCP 不是 Playwright MCP Server
    - WebMCP 实践
    - 为什么这很重要
    - 构建一个 WebMCP 网站
    - 定义工具的两种方式
    - 把 goose 连接到 WebMCP
    - 资源
- **使用你的 AI 订阅来使用 goose**
    - 为什么要用订阅？
    - Claude Code——通过 ACP
    - ChatGPT——用你的账户登录
    - Gemini——通过 OAuth
    - 那旧的 CLI provider 呢？
    - 速查表
- **对手 Agent：用一个隐藏的 Agent 守护主 Agent 的安全**
    - 什么是对手模式？
    - 它是如何工作的
    - 开启它
    - 为什么不干脆用模式匹配？
    - 接下来
- **goose 有了新家——Agentic AI Foundation（AAIF）**
    - 新的文档站点
    - 更新后的 GitHub 仓库
    - 更新你的 remote
    - 迁移进行中
    - 了解更多
- **goose 2.0 beta——全新架构与客户端**
    - 底层：ACP
    - 新的 goose TUI
    - 立即试用新的 TUI
    - 桌面版正在迁往 Tauri
    - 参与进来
- **如何与你的 Agent「分手」**
    - 集成问题
    - 在 Goose 中使用任何编辑器
    - 在 Goose 中使用任何 Agent
    - ACP 目前止步于何处
    - 下一步走向何处
    - 试一试
- **goose 中的 Mesh LLM：跨模型路由**
    - 什么是 Mesh LLM？
- **默认私密：goose 内置的本地推理模型**
    - 它是如何工作的
    - 这与 Ollama 有何不同
    - 会有怎样的体验
    - 充分利用它的技巧
- **走出终端：goose 用 Peekaboo 掌控你的桌面**
    - 看 → 点 → 输入 的循环
    - goose 实际上能用它做什么？
    - 完整的命令工具箱
    - 获得最佳效果的技巧
    - 当前的局限
    - 试一试
- **以三十分之一的成本逼近前沿性能**
- **用 goose 跨多个 Agent 编排复杂工作流**
    - 什么是编排？
    - 自己试试
    - 它如何建立在已有基础之上
    - 分阶段工作流：研究 → 构建 → 验证
    - 编排 + ACP：混合 Agent
    - 最佳实践
    - 开始使用
- **Hooks：在每个 goose 事件上运行你自己的脚本**
    - 它是如何工作的
    - 几个可以尝试的东西
    - 试试这个示例
    - 为什么这很重要
- **自我改进的 Agent 仍需要人类**
- **转向以 issue 作为新的 PR**
- **Agentic 状态机**

### 第 30 章　Recipe 模板库（一）：顶层 Recipe

> Recipe 模板库（一）：44 个顶层 Recipe 的中文导读（用途 / 参数表 / 所需扩展）+ 完整 YAML 原文，可直接取用。

`goose-zh-30-Recipe模板库一.md`　·　44 页　·　源 206,530 B

- **A/B 测试框架生成器**
- **分析 PR**
- **从 Git 提交生成变更日志**
- **CI/CD 流水线生成器**
- **清理功能开关**
- **代码文档生成器**
- **代码评审导师**
- **创建 Kafka 主题**
- **CSV 文件合并器**
- **每日站会报告生成器**
- **数据分析流水线**
- **依赖更新器**
- **开发指南迁移（从指定文件或目录）**
- **Flutter PR 代码评审**
- **软件项目生成器**
- **生成提交信息**
- **JavaScript/React PR 代码评审**
- **代码静态检查**
- **Maverick — 行为适配**
- **混乱列修复器**
- **将 Cypress 测试迁移到 Playwright**
- **从 poetry 迁移到 uv**
- **OpenAPI 转 Locust 负载测试生成器**
- **PHP PR 代码评审**
- **PR 演示规划器**
- **PR 生成器**
- **Ralph 评审阶段**
- **Ralph 工作阶段**
- **README 机器人**
- **重构函数**
- **Python 去 AI 痕迹**
- **RPI 实现计划**
- **RPI 迭代计划**
- **RPI 创建计划**
- **RPI 代码库调研**
- **搜索 DataHub**
- **安全审计与修复流水线**
- **智能任务整理器**
- **Sunno 歌曲格式生成器**
- **技术文章讲解器**
- **技术债跟踪器**
- **测试覆盖率优化器**
- **使用 OpenMetadata**
- **Web 无障碍审计器**

### 第 31 章　Recipe 模板库（二）：子 Recipe

> Recipe 模板库（二）：23 个子 Recipe 的中文导读 + 完整 YAML 原文，供被顶层 Recipe 调用。

`goose-zh-31-Recipe模板库二.md`　·　23 页　·　源 91,495 B

- **A/B 测试仪表盘生成器**
- **A/B 测试统计分析器**
- **OpenAPI 规范分析器**
- **图表生成器**
- **代码安全分析器**
- **代码复杂度分析器**
- **合规检查器**
- **数据清洗器**
- **数据校验器**
- **依赖健康分析器**
- **文档质量分析器**
- **代码重复检测器**
- **实验追踪器**
- **主 Locustfile 生成器**
- **支撑文件生成器**
- **Locust TaskSet 生成器**
- **代码库分析器**
- **代码库定位器**
- **模式查找器**
- **密钥检测器**
- **统计分析器**
- **测试覆盖率分析器**
- **漏洞扫描器**

### 第 32 章　仓库治理文档

> 仓库治理文档：README、CONTRIBUTING、GOVERNANCE、SECURITY、RELEASE、I18N、MAINTAINERS、各平台构建说明等 16 篇。

`goose-zh-32-仓库治理文档.md`　·　16 页　·　源 118,749 B

- **AGENTS 指南**
    - 贡献工作流
    - MCP 服务器目录
    - GitHub 沟通
    - 环境搭建
    - 命令
    - 目录结构
    - 开发循环
    - 规则
    - 代码质量
    - 绝不
    - 入口点
- **使用 Docker 构建并运行 goose**
    - 快速开始
    - 从源码构建
    - 在 Docker 中运行 goose
    - 配置
    - CI/CD 集成
    - 镜像详情
    - 故障排查
    - 进阶用法
    - 为生产环境构建
    - 贡献
    - 相关文档
- **在 Linux 上构建 goose 桌面版**
    - 前置条件
    - 构建流程
    - 故障排查
    - 开发工作流
    - 创建系统集成
    - 贡献
- **Claude 配置**
- **行为准则**
    - Contributor Covenant 3.0 行为准则
    - 我们的承诺
    - 鼓励的行为
    - 受限制的行为
    - 报告问题
    - 处理与修复伤害
    - 适用范围
    - 归属
- **贡献指南**
    - Issue 工作流
    - 如何贡献
    - LLM 提供方集成
    - 从 Issue 到 Pull Request
    - AI 代码评审
    - 负责任地使用 AI 的快速提示
    - 前置条件
    - 开发环境搭建
    - 创建 fork
    - 保持你的 Fork 最新
    - 环境变量
    - 使用[本地托管的 Langfuse](https://langfuse.com/docs/deployment/self-host)在 goose 中启用 trace
    - 约定式提交
    - 其他贡献方式
- **goose 技术治理与监管**
    - 核心价值观
    - 角色
    - 决策流程
    - 维护者的选拔与罢免
    - 沟通
    - 工作实践
    - 治理变更
    - 现任成员
    - 小结
    - 一般项目政策
- **goose 自定义发行版**
    - 概览
    - 架构一览
    - 关键定制点
    - 快速开始
    - 重要注意事项
    - 附录：自定义发行版场景
    - A. 预配置本地模型的发行版
    - B. 带托管 API Key 的企业发行版
    - C. 面向内部数据源的自定义工具
    - D. 自定义品牌与 UI
    - E. 构建新界面（Web、移动端等）
    - F. 面向特定人群的发行版（法务、设计等）
    - G. 添加自定义 AI 提供方
    - H. 用 Recipe 预配置工作流
    - I. 带子 Recipe 与子代理的复杂工作流
- **国际化（i18n）——Goose 桌面版 UI**
    - 概览
    - 标记待翻译的字符串
    - 提取消息
    - Locale 检测
    - 日期与数字格式化
    - 添加新语言
    - 测试
    - 架构小结
- **维护者**
    - 核心维护者
    - 维护者
- **unroll-agent-loop 的合并修复**
    - 针对 `unroll-agent-loop` 的合并修复
    - 发生了什么
    - 1. 从 `origin/main` 重建 —— 已完成
    - 2. 直接回退 —— 已完成
    - 3. 重新落地被后续合并丢弃的分支工作 —— 已完成
    - 4. 简化 —— 仍未完成
    - 5. Scheduler 工具重命名 —— 已接受
    - 其他待办
    - 验证
- **goose（README）**
    - goose
    - 开始使用
    - 快速链接
    - 一点 goose 幽默 🪿
    - 和我们一起 goose 一下
- **发布流程**
    - 制作发布
    - 次版本发布
    - 补丁版本发布
    - 高层发布流程：
- **goose 发布人工测试清单**
    - goose 发布人工测试清单
    - 使用以下脚本创建风险评估与测试计划：
    - 运行 goose 自测 recipe
    - 让 goose 产出一份测试计划
- **为 RISC-V 构建 goose**
    - 为 RISC-V 构建 goose（riscv64gc-unknown-linux-gnu）
    - 前置条件
    - 概览
    - 设置步骤
    - 完整补丁脚本
    - 已知问题
    - 替代方案：条件编译
    - 验证
- **安全**

### 第 33 章　文档站工程与站点页面

> 文档站工程与站点页面：文档站自身 README/AGENTS/CLAUDE、自动化脚本说明、Docker 示例、侧栏分类元数据、grants 页等 29 个文件。

`goose-zh-33-文档站工程与站点页面.md`　·　29 页　·　源 47,930 B

- **文档写作风格指南**
    - 品牌规范
    - 适用范围
    - MCP 扩展目录
- **CLAUDE.md（引用 AGENTS.md）**
- **文档站点（Website）**
- **文档自动化**
    - 概览
    - 架构
    - GitHub Actions 集成
    - 新增自动化
    - 有问题？
- **CLI 命令追踪**
    - 概览
    - 快速开始
    - 架构
    - 配置
    - 脚本
    - Recipes
    - 目录结构
    - GitHub Actions 工作流
    - 跟踪的内容
    - 维护
    - 相关文档
- **测试指南（CLI 命令追踪）**
    - 前置条件
    - 本地测试
    - GitHub Actions 测试
    - 用已知变更测试
    - 验证清单
    - 故障排查
    - 人工验证
    - 测试数据
- **为 goose 撰写博客文章**
    - 快速开始
    - 目录结构
    - Frontmatter
    - 头图
    - 内容结构
    - 社交媒体标签
    - 作者信息
    - 最佳实践
    - 预览博客文章
- **Dockerfile（Docker 镜像构建）**
- **docker-compose.yml（Docker Compose 配置）**
- **_category_.json：experimental**
- **_category_.json：gdk**
- **_category_.json：gdk/acp**
- **_category_.json：gdk/sdk**
- **_category_.json：getting-started**
- **_category_.json：goose-architecture**
- **_category_.json：guides**
- **_category_.json：guides/context-engineering**
- **_category_.json：guides/interactive-chat**
- **_category_.json：guides/managing-tools**
- **_category_.json：guides/multi-model**
- **_category_.json：guides/recipes**
- **_category_.json：guides/security**
- **_category_.json：guides/sessions**
- **_category_.json：mcp**
- **_category_.json：troubleshooting**
- **_category_.json：tutorials**
- **Community All Stars 月度更新指南**
    - 月度更新流程
    - 数据格式
    - 版块映射
    - 提示
    - 文件结构
    - 月度快速清单
- **goose 资助计划**
    - 什么样的提案算是好提案
    - 资助细节
    - 常见问题
    - 联系我们
- **社区 Recipe Cookbook**

## 关于本手册

- **语料来源**：`https://github.com/aaif-goose/goose`，抓取快照日期 2026-10-15。
  - 文档站正文（第 1–22 章）：`documentation/docs/`，原文在线地址 `https://block.github.io/goose/docs/`。
  - 博客存档（第 23–29 章）：`documentation/blog/`，原文在线地址 `https://block.github.io/goose/blog/`。
  - Recipe 模板（第 30–31 章）：`documentation/src/pages/recipes/data/recipes/`，中文导读 + 完整 YAML 原文，出处为 GitHub blob 地址。
  - 仓库治理（第 32 章）与文档站工程（第 33 章）：仓库根 `*.md` 与 `documentation/` 下工程文件。
- **图片**：文档站图片改写为 `https://block.github.io/goose/img/...` 绝对地址；博客相对图片同样绝对化；badge 与外链原样保留。
- **未译内容**：代码块、命令、环境变量名、文件路径、配置键名、产品名与模型名、Recipe YAML 的字段值，以及 MDX 渲染型组件（`<GooseDesktopInstaller />` 等）本身。
- **已知偏差**：源站部分页面的多行内容在抽取时被压成一行（表格错位、代码块挤行），译文按语义还原了换行，未增删字符。
- **更新方式**：源站更新后重跑翻译流程即可，章节文件可原地替换。
