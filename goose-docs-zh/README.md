# goose 官方文档中文手册

goose 官方文档库（`aaif-goose/goose` → `documentation/docs/`）的简体中文完整翻译。**官方站点没有中文版**（`docusaurus.config.ts` 中 `locales: ["en"]`，无 `i18n/` 目录），本手册是独立翻译成果。

| 项 | 值 |
|---|---|
| 源语料 | goose 官方文档库 173 个 `.md` / `.mdx`，1,351,256 字节 |
| 章节数 | 22 章 |
| 页面节 | 173 个（每页一个 `## ` 节，均带 `> 原文：` 出处） |
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

## 总目录

### 第 01 章　快速开始与安装

> 从零装好 goose：系统要求、各平台安装方式、首次启动与验收。

`goose-zh-01-快速开始与安装.md`　·　2 页

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

`goose-zh-02-模型提供方全览.md`　·　1 页

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

`goose-zh-03-扩展与工具管理.md`　·　7 页

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

`goose-zh-04-上下文工程-一-指令层.md`　·　5 页

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

`goose-zh-05-上下文工程-二-Agent层.md`　·　5 页

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

`goose-zh-06-Recipes可复用工作流.md`　·　5 页

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

`goose-zh-07-会话与任务执行.md`　·　5 页

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

`goose-zh-08-权限安全与数据.md`　·　6 页

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

`goose-zh-09-提供方进阶与多模型.md`　·　5 页

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

`goose-zh-10-CLI命令与配置文件.md`　·　2 页

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

`goose-zh-11-环境变量与运行控制.md`　·　5 页

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

`goose-zh-12-交互界面与实用技巧.md`　·　10 页

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

`goose-zh-13-MCP扩展一-核心内置.md`　·　14 页

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

`goose-zh-14-MCP扩展二-浏览器与自动化.md`　·　9 页

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

`goose-zh-15-MCP扩展三-开发与代码.md`　·　11 页

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

`goose-zh-16-MCP扩展四-数据与云服务.md`　·　12 页

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

`goose-zh-17-MCP扩展五-协作与办公.md`　·　14 页

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

`goose-zh-18-MCP扩展六-搜索与信息获取.md`　·　14 页

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

`goose-zh-19-教程一-扩展与集成实战.md`　·　8 页

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

`goose-zh-20-教程二-工作流与可观测性.md`　·　10 页

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

`goose-zh-21-架构远程部署与GDK.md`　·　11 页

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

`goose-zh-22-排错与实验特性.md`　·　12 页

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

## 关于本手册

- **语料来源**：`https://github.com/aaif-goose/goose` 的 `documentation/docs/`，抓取快照日期 2026-10-15。原文在线地址为 `https://block.github.io/goose/docs/`。
- **图片**：全部改写为 `https://block.github.io/goose/img/...` 绝对地址，随源站更新；`data:image/png;base64,...` 内联图与 `/api/v1/...` 路径示例原样保留。
- **未译内容**：代码块、命令、环境变量名、文件路径、配置键名、产品名与模型名，以及 MDX 渲染型组件（`<GooseDesktopInstaller />` 等）本身。
- **已知偏差**：源站部分页面的多行内容在抽取时被压成一行（表格错位、代码块挤行），译文按语义还原了换行，未增删字符。
- **更新方式**：源站更新后重跑翻译流程即可，章节文件可原地替换。
