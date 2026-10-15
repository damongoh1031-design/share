# goose 官方文档中文手册：第 15 章　MCP 扩展（三）：开发与代码

## GitHub 扩展

> 原文：https://block.github.io/goose/docs/mcp/github-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/TbmQDv3SQOE" />

本教程介绍如何将 [GitHub MCP 服务器](https://github.com/github/github-mcp-server)添加为 goose 扩展，以启用文件操作、仓库管理、搜索功能等。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
   [启动安装程序](goose://extension?type=streamable_http&url=https%3A%2F%2Fapi.githubcopilot.com%2Fmcp%2F&id=github-mcp&name=GitHub&description=GitHub%20repository%20management%20and%20operations&header=Authorization%3DBearer%20YOUR_GITHUB_PERSONAL_ACCESS_TOKEN)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  添加一个 `Remote Extension (Streamable HTTP)` 扩展类型，配置如下：

  **Endpoint URL**
```
https://api.githubcopilot.com/mcp/
```
  </TabItem>
</Tabs>

  **Custom Request Header**
```
Authorization: Bearer <YOUR_GITHUB_PERSONAL_ACCESS_TOKEN>
```
:::

### 配置

这些步骤配置的是 Remote MCP 服务器。其他部署选项请参阅 [GitHub MCP 服务器官方文档](https://github.com/github/github-mcp-server)。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="github-mcp"
      extensionName="GitHub"
      description="GitHub repository management and operations"
      type="http"
      url="https://api.githubcopilot.com/mcp/"
      envVars={[
        { name: "Authorization", label: "Bearer YOUR_GITHUB_PERSONAL_ACCESS_TOKEN" }
      ]}
      apiKeyLink="https://github.com/settings/personal-access-tokens"
      apiKeyLinkText="GitHub Personal Access Token"
    />

  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="github"
      description="GitHub repository management and operations"
      type="http"
      url="https://api.githubcopilot.com/mcp/"
      timeout={300}
      envVars={[
        { key: "Authorization", value: "Bearer ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" }
      ]}
      infoNote={
        <>
          Obtain your <a href="https://github.com/settings/personal-access-tokens" target="_blank" rel="noopener noreferrer">GitHub Personal Access Token</a> and paste it in as the <code>Bearer</code> token.
        </>
      }
    />

  </TabItem>
</Tabs>

### 示例用法

在创建我的 [GitHub Personal Access Token](https://github.com/settings/personal-access-tokens)时，我授予了以下访问权限：
* 仓库：[goose-demo](https://github.com/angiejones/goose-demo)
* 对 metadata 的读取权限
* 对 code、commit status、issues 和 pull requests 的读写权限

#### goose 提示词
```
create a new branch called hello-world in my angiejones/goose-demo repository. Update the README.md file to say "this was written by goose" and commit it. Open a pull request with your changes.
```

#### goose 输出

```
I'll help you create a new branch, update the README, and open a pull request. Let me break this down into steps:

1. First, let's create the new branch called "hello-world" in your repository
2. Then update the README.md file
3. Finally, create a pull request

Let me execute these steps:

1. Creating the new branch:

─── create_branch | github ──────────────────────────
branch: hello-world
owner: angiejones
repo: goose-demo

2. Now, updating the README.md file in the new branch:

─── create_or_update_file | github ──────────────────────────
branch: hello-world
content: this was written by goose
message: Update README.md with goose message
owner: angiejones
path: README.md
repo: goose-demo



3. Finally, creating the pull request:

─── create_pull_request | github ──────────────────────────
base: main
body: ...
head: hello-world
owner: angiejones
repo: goose-demo
title: Update README.md



Great! I've completed all the requested tasks:
1. Created a new branch called "hello-world"
2. Updated the README.md file with the text "this was written by goose"
3. Created a pull request to merge these changes into the main branch

You can view the pull request at: https://github.com/angiejones/goose-demo/pull/1

The pull request is now ready for your review. Would you like me to do anything else with it?
```

---

## GitMCP 扩展

> 原文：https://block.github.io/goose/docs/mcp/gitmcp-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/6aV8pinnUS8" /> 

本教程介绍如何将 [Git MCP 服务器](https://github.com/idosal/git-mcp)添加为 goose 扩展，让 LLM 实时访问 GitHub 仓库，从而实现智能文档搜索、代码探索和准确的项目洞察。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?cmd=npx&arg=mcp-remote&arg=https%3A%2F%2Fgitmcp.io%2Fdocs&id=gitmcp&name=GitMCP&description=Remote%20MCP%20server%20from%20gitmcp.io)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
npx -y mcp-remote https://gitmcp.io/docs

```
  </TabItem>
</Tabs>
:::

### 配置

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
        extensionId="gitmcp"
        extensionName="GitMCP"
        description="Git MCP server for up-to-date docs and project insights"
        command="npx"
        args={["-y", "mcp-remote" , "https://gitmcp.io/docs"]}
    />
 </TabItem>
  <TabItem value="cli" label="goose CLI">
      <CLIExtensionInstructions
        name="Git MCP"
        description="Git MCP server for up-to-date docs and project insights"
        command="npx -y mcp-remote https://gitmcp.io/docs"
        timeout={300}
      />
  </TabItem>
</Tabs>

### 示例用法

在本示例中，goose 使用 GitMCP 从 `openai/whisper` GitHub 仓库拉取实时文档，探索该语音转文本模型的工作原理，并给出准确的安装说明和命令行用法——全部直接来自源头。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
   1. 在 goose Desktop 中打开一个新会话
  </TabItem>
  <TabItem value="cli" label="goose CLI">

  1. 打开终端并启动一个新的 goose 会话：

```sh
goose session
```

  </TabItem>
</Tabs>

#### goose 提示词
```
  Can you help me understand how the OpenAI Whisper speech-to-text model works?

  Use the GitHub repository `openai/whisper` to find accurate information.

  Please:
  - Summarize what the model does and its key features
  - Show an example of how to run it from the command line
  - Explain what files or models are needed to get started
  - Include any useful code snippets or setup instructions you find in the repo

  Give me the response in a Markdown guide format.
```
#### goose 输出

:::note 桌面版

我将通过浏览 OpenAI Whisper 的 GitHub 仓库来帮你理解它。让我先获取文档和相关信息。

`─── owner | repo ──────────────────────────`

现在让我搜索一些具体的安装和使用信息：

`─── owner | query ──────── repo ────────────`

让我搜索更多技术细节和示例：

`─── owner | query ──────── repo ────────────`

很好！现在我已经从 OpenAI Whisper 仓库获得了所需的全部信息。让我为你创建一份全面的 Markdown 指南。

OpenAI Whisper 语音转文本模型指南

概述
Whisper 是 OpenAI 开发的通用语音识别模型。它是一个强大的多任务神经网络，可以执行：

- 多语言语音识别（99+ 种语言）
- 语音翻译（将外语语音转换为英文文本）
- 语种识别（检测正在说的是哪种语言）
- 语音活动检测（识别何时存在语音）

主要特性：

- ✅ 稳健的性能：在 680,000 小时多样化、多语言的音频数据上训练
- ✅ 零样本迁移：无需微调即可适用于多种语言
- ✅ 多种模型规模：从 tiny（39M 参数）到 large（1.55B 参数）
- ✅ 易于使用：简单的命令行界面和 Python API
- ✅ 开源：MIT 许可，模型权重可自由获取

架构
Whisper 使用 Transformer 序列到序列模型，以 30 秒为一块处理音频。它将音频转换为 log-Mel 频谱图，并使用特殊 token 来指定任务（转写、翻译、语种识别等）。

命令行用法
基础转写

### 入门检查清单

1. **✅ 安装 Python 3.8-3.11**
2. **✅ 安装 FFmpeg**（对应你的操作系统）
3. **✅ 安装 Whisper**：`pip install -U openai-whisper`
4. **✅ 测试安装**：`whisper --help`
5. **✅ 尝试基础转写**：`whisper your_audio_file.mp3`

#### 首次运行

首次运行时，Whisper 会自动下载模型权重：
- `tiny`：约 39 MB 下载
- `base`：约 142 MB 下载  
- `small`：约 461 MB 下载
- `medium`：约 1.42 GB 下载
- `large`：约 2.87 GB 下载
- `turbo`：约 1.5 GB 下载

模型会缓存在本地，因此后续运行会快得多。


### 技巧与最佳实践

#### 🎯 **模型选择**
- **仅英文**：使用 `.en` 模型（`base.en`、`small.en` 等）
- **快速转写**：使用 `tiny` 或 `base` 模型
- **高准确率**：使用 `medium` 或 `large` 模型
- **翻译任务**：使用 `medium` 或 `large`（不要用 `turbo`）

#### 🎵 **音频质量**
- 干净、清晰的音频会产生更好的结果
- Whisper 可处理多种音频格式（MP3、WAV、FLAC、M4A 等）
- 背景噪声可能影响准确率

#### 🌍 **语言支持**
- 支持 99+ 种语言
- 某些语言的表现优于其他语言
- 查看仓库中的[语言性能细分](https://github.com/openai/whisper#available-models-and-languages)

#### 💾 **资源管理**
- 更大的模型需要更多 VRAM/RAM
- 选择模型时考虑你的硬件限制
- 实时应用使用较小的模型

Whisper 在 **MIT 许可**下发布，可免费用于个人和商业项目。

:::

---

## Repomix 扩展

> 原文：https://block.github.io/goose/docs/mcp/repomix-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/69h4LLkIg_E" />


本教程介绍如何将 [Repomix MCP 服务器](https://github.com/yamadashy/repomix)添加为 goose 扩展，以实现自动化仓库打包、代码库分析、架构摘要、测试生成和代码探索，同时压缩代码库以最小化 token 用量并保持在你的 LLM 上下文限制之内。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?cmd=npx&arg=-y&arg=repomix&arg=--mcp&id=repomix-mcp&name=Repomix&description=Pack%20repositories%20into%20AI-friendly%20formats%20for%20goose)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
npx -y repomix --mcp
```
  </TabItem>
</Tabs>
:::

### 配置

:::info
注意，运行此命令需要在你的系统上安装 [Node.js](https://nodejs.org/)，因为它使用 `npx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="repomix-mcp"
    extensionName="Repomix"
    description="Pack repositories into AI-friendly formats for goose"
    command="npx"
    args={["-y", "repomix", "--mcp"]}
  />
</TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Repomix"
      description="Pack repositories into AI-friendly formats for goose"
      command="npx -y repomix --mcp"
    />
  </TabItem>
</Tabs>

### 示例用法

在本示例中，我将向你展示如何配合 Repomix 扩展使用 goose 来分析压缩后的 Axios 仓库。goose 将聚焦于 `lib/core/Axios.js` 文件，解释它在架构中的作用，找出缺失的测试，编写新的单元测试，并就测试策略和代码可维护性提出改进建议。

通过将整个代码库压缩为对 AI 友好的格式，Repomix 帮助 goose 在 token 限制内提供针对具体文件的详细洞察。

#### goose 提示词

> Review the file lib/core/Axios.js from the Axios repository and identify any missing unit tests needed to thoroughly cover its core functions and classes. Explain the role this file plays in the overall Axios architecture, how it integrates with other modules, and how well it is currently tested. Write new unit tests to improve coverage, and recommend improvements to the testing strategy or refactoring opportunities to make the code more maintainable.


#### goose 输出

:::note CLI

我将帮你分析 Axios.js 核心文件及其测试覆盖情况。让我们分步骤进行：

1. 首先，使用 repomix 获取并检查 Axios 仓库
2. 然后分析该特定文件及其相关测试
3. 最后给出建议和新的单元测试

让我们先从获取仓库开始：

--- 打包远程仓库 ---

现在让我们读取核心的 Axios.js 文件及其相关测试文件：

--- 读取 Repomix 输出 ---

基于我对 Axios 代码库的分析，我将为你提供项目结构的全面概览，并创建一份改进的 README。让我分节说明：

**在 Axios 架构中的作用**

`Axios.js` 文件是 Axios 库最核心的组件之一。它有以下几个关键作用：

1. 请求处理：它包含处理并派发 HTTP 请求的主 `Axios` 类
2. 配置管理：处理默认配置与请求特定配置的合并
3. 拦截器管理：管理请求和响应拦截器
4. HTTP 方法便捷调用：为不同的 HTTP 动词（get、post 等）提供便捷方法

该文件通过以下方式与其他核心模块集成：

- `InterceptorManager` 用于处理请求/响应拦截器
- `dispatchRequest` 用于发起实际的 HTTP 请求
- `mergeConfig` 用于配置处理
- `buildFullPath` 用于 URL 解析
- `AxiosHeaders` 用于请求头管理

**当前测试覆盖分析**

Axios.js 目前的测试覆盖相当不错，但仍有一些缺口。查看测试文件：

1. `test/unit/core/Axios.js` —— 主要关注错误处理场景，尤其是不可写的错误堆栈
2. `test/specs/api.spec.js` —— 测试公开 API 表面
3. `test/specs/interceptors.spec.js` —— 测试拦截器功能
4. `test/specs/instance.spec.js` —— 测试实例创建与配置

**缺失的测试覆盖**
1. 错误处理：

```js
// Missing tests for error propagation in request chain
_request(configOrUrl, config) {
  // Error handling here needs more coverage
}
```

2. 配置处理：

```js
// Missing edge cases for config validation
request(configOrUrl, config) {
  // Config validation edge cases not fully tested
}
```

3. 方法别名：

```js
// Missing tests for all HTTP method aliases with various parameter combinations
utils.forEach(['post', 'put', 'patch'], function forEachMethodWithData(method) {
  // Missing tests for these methods with different data types
});
```

4. 拦截器链：

```js
// Missing tests for complex interceptor chains and error scenarios
const chain = [dispatchRequest.bind(this), undefined];
chain.unshift.apply(chain, requestInterceptorChain);
chain.push.apply(chain, responseInterceptorChain);
```

**新的单元测试**
以下是一些用于提升覆盖率的新单元测试：

```js
describe('core::Axios', function() {
  describe('request method', function() {
    it('should handle null/undefined config values', function(done) {
      const instance = new Axios({});
      
      instance.request({
        url: '/foo',
        params: null,
        data: undefined
      }).then(function(response) {
        expect(response.config.params).toBeNull();
        expect(response.config.data).toBeUndefined();
        done();
      }).catch(done);
    });

    it('should properly merge nested config objects', function(done) {
      const instance = new Axios({
        headers: {
          common: {
            'X-Common': 'common'
          },
          get: {
            'X-Method': 'get'
          }
        }
      });

      instance.request({
        method: 'get',
        headers: {
          'X-Custom': 'custom'
        }
      }).then(function(response) {
        expect(response.config.headers['X-Common']).toBe('common');
        expect(response.config.headers['X-Method']).toBe('get');
        expect(response.config.headers['X-Custom']).toBe('custom');
        done();
      }).catch(done);
    });
  });

  describe('interceptor chain', function() {
    it('should handle async interceptors correctly', async function() {
      const instance = new Axios({});
      const order = [];

      instance.interceptors.request.use(async function(config) {
        await new Promise(resolve => setTimeout(resolve, 100));
        order.push(1);
        return config;
      });

      instance.interceptors.request.use(async function(config) {
        await new Promise(resolve => setTimeout(resolve, 50));
        order.push(2);
        return config;
      });

      instance.interceptors.response.use(async function(response) {
        await new Promise(resolve => setTimeout(resolve, 100));
        order.push(3);
        return response;
      });

      await instance.request('/foo');
      expect(order).toEqual([2, 1, 3]); // Interceptors should execute in correct order
    });

    it('should handle interceptor errors properly', function(done) {
      const instance = new Axios({});
      const error = new Error('Interceptor Error');

      instance.interceptors.request.use(function() {
        throw error;
      });

      instance.request('/foo').catch(function(e) {
        expect(e).toBe(error);
        done();
      });
    });
  });

  describe('HTTP method aliases', function() {
    it('should handle various data types in post/put/patch', function(done) {
      const instance = new Axios({});
      const testCases = [
        {method: 'post', data: {foo: 'bar'}},
        {method: 'put', data: 'string data'},
        {method: 'patch', data: new URLSearchParams('foo=bar')},
        {method: 'post', data: new FormData()},
        {method: 'put', data: new Blob(['test'])},
        {method: 'patch', data: null}
      ];

      Promise.all(testCases.map(({method, data}) => {
        return instance[method]('/foo', data).then(response => {
          expect(response.config.data).toEqual(data);
          return response;
        });
      })).then(() => done()).catch(done);
    });
  });
});
```

**测试策略建议**

1. 模块化测试：

- 将测试拆分为更小、更聚焦的单元
- 分别测试每个 HTTP 方法别名
- 为配置处理、拦截器和错误处理创建专门的测试套件

2. 模拟集成点：

- 使用依赖注入以获得更好的隔离
- 一致地模拟外部依赖
- 创建可复用的 mock 工厂

3. 错误处理：

- 为错误场景添加更多测试
- 测试错误在拦截器链中的传播
- 验证错误对象的属性和继承关系

4. 配置处理：

- 测试复杂的配置合并场景
- 验证默认值被正确应用
- 测试配置校验的边界情况

5. 拦截器测试：

- 测试复杂的拦截器链
- 验证异步拦截器行为
- 测试拦截器错误处理

**重构机会**

1. 错误处理：
```js
// Current
_request(configOrUrl, config) {
  try {
    return this.request(configOrUrl, config);
  } catch (err) {
    // Error handling
  }
}

// Suggested
async _request(configOrUrl, config) {
  try {
    return await this.request(configOrUrl, config);
  } catch (err) {
    if (err instanceof AxiosError) {
      throw err;
    }
    throw AxiosError.from(err);
  }
}
```
2. 配置处理：

```js
// Current
request(configOrUrl, config) {
  // Config processing
}

// Suggested
request(configOrUrl, config) {
  const normalizedConfig = this._normalizeConfig(configOrUrl, config);
  this._validateConfig(normalizedConfig);
  return this._processRequest(normalizedConfig);
}
```

3. 拦截器链：

```js
// Current
// Interceptor chain building mixed with request logic

// Suggested
class InterceptorChain {
  constructor(request, config) {
    this.request = request;
    this.config = config;
    this.chain = [];
  }

  addRequestInterceptors(interceptors) {
    // Add request interceptors
  }

  addResponseInterceptors(interceptors) {
    // Add response interceptors
  }

  execute() {
    // Execute chain
  }
}
```

这些改进将使代码更易维护、更易测试，同时改进错误处理和关注点分离。

目前的测试覆盖不错，但可以在这些具体方面加以改进，以确保功能更加健壮。建议的新测试和重构机会有助于捕获边界情况，并使代码更易维护。
:::

---

## Context7 扩展

> 原文：https://block.github.io/goose/docs/mcp/context7-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/LNmPi6YCocI" /> 


本教程介绍如何将 [Context7 MCP 服务器](https://github.com/upstash/context7)添加为 goose 扩展，以拉取最新的、特定版本的代码和文档，让 goose 能够基于真实上下文进行 vibe coding，而不是给出幻觉或过时的答案。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?cmd=npx&arg=-y&arg=%40upstash%2Fcontext7-mcp&id=context7&name=Context7&description=Context7%20MCP%20server%20for%20up-to-date%20code%20and%20docs)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
npx -y @upstash/context7-mcp
```
  </TabItem>
</Tabs>
:::

### 配置

:::info
注意，运行此命令需要在你的系统上安装 [Node.js](https://nodejs.org/)，因为它使用 `npx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="context7"
      extensionName="Context7"
      description="Context7 MCP server for up-to-date code and docs"
      command="npx"
      args={["-y", "@upstash/context7-mcp"]}
    />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Context7"
      description="Context7 MCP server for up-to-date code and docs"
      command="npx -y @upstash/context7-mcp"
    />
  </TabItem>
</Tabs>

### 示例用法

在本示例中，goose 使用 Context7 拉取实时文档、比较工具，并仅使用最新的官方实现模式来搭建一个现代应用。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
   1. 在 goose Desktop 中打开一个新会话
  </TabItem>
  <TabItem value="cli" label="goose CLI">

  1. 打开终端并启动一个新的 goose 会话：

```sh
goose session
```

  </TabItem>
</Tabs>

#### goose 提示词

我需要帮助构建一个现代 Web 应用。你能：

1. 使用 Context7 分析和比较：

- Next.js App Router 与 Pages Router
- Prisma 与其他 ORM
- 不同的身份验证方案
- 状态管理方案

2. 对每项选定的技术：

- 展示最新的官方实现模式
- 提供类型定义和接口
- 分享文档中的相关代码片段
- 解释最佳实践和常见陷阱

3. 帮助实现：

- 遵循官方指南的项目结构
- 数据库 schema 与类型安全
- 具备适当安全性的身份验证流程
- 带错误处理的 API 路由
- 性能优化

请引用具体的文档章节，并解释为什么某些方案比其他方案更受推荐。

#### goose 输出

:::note 桌面版

1. 技术分析
Next.js App Router 与 Pages Router
首先，让我们获取最新的 Next.js 文档：


-------- Resolve-library-id -------

让我们获取关于 Next.js 的详细文档，重点关注路由：


------ Get-library-docs ---------

让我分析 Next.js 文档，并拆解 App Router 与 Pages Router 之间的关键差异：

------ code structure comparison -----

让我们获取 Prisma 和其他 ORM 的信息：


------- Resolve-library-id ---------- 

让我们获取 Prisma 的文档：


------ Get-library-docs ----------


关键决策与最佳实践：

1. App Router 与 Pages Router：

选择 App Router 的理由：
默认使用服务端组件（性能更好）
内置支持流式数据获取
通过 Route Handlers 简化 API 路由
更好的 TypeScript 集成

2. 使用 Prisma 作为 ORM：

优势：
类型安全的数据库查询
自动生成的客户端
Schema 迁移
丰富的查询 API
使用 Prisma Accelerate 获得更好性能

3. 身份验证：

使用 NextAuth.js 的理由：
内置安全特性
多种身份验证提供方
会话管理
JWT 处理

4. 性能优化：

使用服务端组件减少 JavaScript
使用 Route Handlers 处理 API 端点
使用 Prisma Accelerate 提升数据库性能
全栈类型安全

你想让我更详细地解释某一部分，或者帮你实现某些具体功能吗？

:::

---

## Beads 扩展

> 原文：https://block.github.io/goose/docs/mcp/beads-mcp

本教程介绍如何将 [Beads MCP 服务器](https://github.com/steveyegge/beads)添加为 goose 扩展。Beads 是一款为 AI 代理设计的分布式、基于 git 的问题跟踪器。它支持带依赖管理的持久化任务跟踪，因此多个 goose 会话可以在复杂项目上协同工作。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?cmd=uvx&arg=beads-mcp&id=beads&name=Beads&description=Git-backed%20issue%20tracker%20for%20AI%20agent%20task%20management)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
uvx beads-mcp
```
  </TabItem>
</Tabs>
:::

### 配置

:::info
注意，运行此命令需要在你的系统上安装 [uv](https://docs.astral.sh/uv/#installation)，因为它使用 `uvx`。
:::

:::note 故障排查
如果扩展启动失败并报 `ModuleNotFoundError: No module named 'packaging'`（已在 0.49.1 之后的版本修复），请运行：
```sh
uv tool install beads-mcp --with packaging
```
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="beads"
      extensionName="Beads"
      description="Git-backed issue tracker for AI agent task management"
      type="stdio"
      command="uvx"
      args={["beads-mcp"]}
    />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="beads"
      description="Git-backed issue tracker for AI agent task management"
      type="stdio"
      command="uvx beads-mcp"
      timeout={300}
    />
  </TabItem>
</Tabs>

### 示例用法

在本示例中，我们将使用 Beads 在**多个并行会话**中协同构建一个记账 Web 应用。这展示了 Beads 如何让多个 goose 实例在同一个项目上无冲突地工作。

#### 概览

我们将运行 **4 个 goose 会话**：
1. **步骤 1**：创建所有任务及其依赖关系
2. **步骤 2**：构建前端任务
3. **步骤 3**：构建后端任务（与步骤 2 并行）
4. **步骤 4**：等待阻塞项解除，然后把所有内容串联起来

---

#### 步骤 1：规划项目

创建一个新目录并启动一个 goose 会话。

##### goose 提示词
```
I want to build an expense tracker web app. Initialize beads and create all tasks with dependencies:

Frontend tasks:
- "HTML Structure" - create form, expense list, total display (no dependencies)
- "CSS Styling" - style the app (depends on "HTML Structure")
- "Wire Up UI" - connect buttons to functions (depends on "CSS Styling" AND all backend tasks)

Backend tasks:
- "Storage Setup" - localStorage helpers to save/load expenses (no dependencies)
- "Add Expense" - function to add expense to storage (depends on "Storage Setup")
- "Calculate Total" - function to sum all expenses (depends on "Storage Setup")
- "Delete Expense" - function to remove expense (depends on "Storage Setup")

Show me all tasks and which ones are ready to work on.
```

##### goose 输出
```
I'll initialize beads and create all the tasks with their dependencies.

─── context | beads ──────────────────────────
action: init

─── create | beads ──────────────────────────
title: HTML Structure
description: Create form, expense list, and total display for the expense tracker app
labels: frontend

─── create | beads ──────────────────────────
title: Storage Setup
description: Create localStorage helpers to save/load expenses
labels: backend

─── create | beads ──────────────────────────
title: CSS Styling
deps: ultimate-beads-test-987
description: Style the expense tracker app with CSS
labels: frontend

─── create | beads ──────────────────────────
title: Add Expense
deps: ultimate-beads-test-6gs
description: Function to add expense to storage
labels: backend

─── create | beads ──────────────────────────
title: Calculate Total
deps: ultimate-beads-test-6gs
description: Function to sum all expenses
labels: backend

─── create | beads ──────────────────────────
title: Delete Expense
deps: ultimate-beads-test-6gs
description: Function to remove expense from storage
labels: backend

─── create | beads ──────────────────────────
title: Wire Up UI
deps: ultimate-beads-test-vt2, ultimate-beads-test-5x5, ultimate-beads-test-29u, ultimate-beads-test-ae4
description: Connect buttons to functions - wire up the complete UI
labels: frontend

Here's the complete overview of your expense tracker tasks:

## 📋 All Tasks

### Frontend Tasks
| ID | Task | Status | Blocked By |
|----|------|--------|------------|
| `987` | **HTML Structure** | ✅ Ready | - |
| `vt2` | CSS Styling | 🚫 Blocked | HTML Structure |
| `m7i` | Wire Up UI | 🚫 Blocked | CSS Styling, Add Expense, Calculate Total, Delete Expense |

### Backend Tasks
| ID | Task | Status | Blocked By |
|----|------|--------|------------|
| `6gs` | **Storage Setup** | ✅ Ready | - |
| `5x5` | Add Expense | 🚫 Blocked | Storage Setup |
| `29u` | Calculate Total | 🚫 Blocked | Storage Setup |
| `ae4` | Delete Expense | 🚫 Blocked | Storage Setup |

## 📊 Dependency Graph

HTML Structure (987)          Storage Setup (6gs)
       │                      /      |      \
       ▼                     ▼       ▼       ▼
  CSS Styling (vt2)    Add Expense  Calculate  Delete Expense
       │                  (5x5)    Total (29u)    (ae4)
       │                    \        |         /
       └────────────────────────────┼────────┘
                                    ▼
                            Wire Up UI (m7i)

## 🚀 Ready to Work On

Two tasks have no blockers and can be started immediately:

1. **HTML Structure** (frontend)
2. **Storage Setup** (backend)

These two foundation tasks can be worked on **in parallel** since they're independent of each other!
```

---

#### 步骤 2：构建前端

在同一目录中打开一个**新终端**并启动一个新的 goose 会话。

##### goose 提示词
```
Check beads for the expense tracker project.

Build the "HTML Structure" task.

When done, mark it complete in beads, then build "CSS Styling" and mark it complete.
```

##### goose 输出
```
─── ready | beads ──────────────────────────

📋 Ready work (2 issues with no blockers):
1. [● P2] [task] ultimate-beads-test-987: HTML Structure
2. [● P2] [task] ultimate-beads-test-6gs: Storage Setup

I'll build the HTML Structure task first.

─── text_editor | developer ──────────────────────────
path: index.html
command: write

HTML Structure is complete. Now let me mark it as complete in beads:

─── shell | developer ──────────────────────────
command: bd close ultimate-beads-test-987 -m "Created index.html with expense form, expense list, and total display"

✓ Closed ultimate-beads-test-987

Now let me build the CSS Styling task:

─── text_editor | developer ──────────────────────────
path: styles.css
command: write

─── shell | developer ──────────────────────────
command: bd close ultimate-beads-test-vt2 -m "Created styles.css with responsive design"

✓ Closed ultimate-beads-test-vt2

Let me verify the current state:

─── shell | developer ──────────────────────────
command: bd ready

📋 Ready work (2 issues with no blockers):
1. [● P2] [task] ultimate-beads-test-29u: Calculate Total
2. [● P2] [task] ultimate-beads-test-ae4: Delete Expense

## ✅ Completed Tasks

### 1. HTML Structure (`ultimate-beads-test-987`)
Created `index.html` with:
- **Expense Form** - Input fields for expense name, amount, category, and date
- **Total Display** - Section showing the total expenses amount
- **Expense List** - Table layout with headers for Name, Category, Date, Amount, and Action

### 2. CSS Styling (`ultimate-beads-test-vt2`)
Created `styles.css` with:
- **Modern design** using CSS custom properties for consistent theming
- **Responsive grid layout** for the expense list
- **Mobile-responsive design** with breakpoints

## 📋 Next Ready Tasks
The dependency chain has unblocked new work:
1. Calculate Total
2. Delete Expense
```

---

#### 步骤 3：构建后端

在同一目录中打开**第三个终端**并启动另一个 goose 会话。与步骤 2 并行运行。

##### goose 提示词
```
Check beads for the expense tracker project.

Build the "Storage Setup" task and mark it complete.

Then build "Add Expense", "Calculate Total", and "Delete Expense", marking each complete as you go.
```

##### goose 输出
```
─── ready | beads ──────────────────────────

📋 Ready work (2 issues with no blockers):
1. [● P2] [task] ultimate-beads-test-987: HTML Structure
2. [● P2] [task] ultimate-beads-test-6gs: Storage Setup

I'll start with Storage Setup.

─── update | beads ──────────────────────────
issue_id: ultimate-beads-test-6gs
status: in_progress

─── text_editor | developer ──────────────────────────
path: storage.js
command: write

─── close | beads ──────────────────────────
issue_id: ultimate-beads-test-6gs
reason: Implemented localStorage helpers: getExpenses, saveExpenses, clearExpenses, generateId

Now let me build "Add Expense":

─── text_editor | developer ──────────────────────────
path: addExpense.js
command: write

─── close | beads ──────────────────────────
issue_id: ultimate-beads-test-5x5
reason: Implemented addExpense() function

Now "Calculate Total":

─── text_editor | developer ──────────────────────────
path: calculateTotal.js
command: write

─── close | beads ──────────────────────────
issue_id: ultimate-beads-test-29u
reason: Implemented calculateTotal() and calculateTotalByCategory()

And finally "Delete Expense":

─── text_editor | developer ──────────────────────────
path: deleteExpense.js
command: write

─── close | beads ──────────────────────────
issue_id: ultimate-beads-test-ae4
reason: Implemented deleteExpense() and deleteExpensesByCategory()

## ✅ Completed Tasks

| Task | ID | File Created |
|------|-----|--------------|
| **Storage Setup** | `6gs` | `storage.js` |
| **Add Expense** | `5x5` | `addExpense.js` |
| **Calculate Total** | `29u` | `calculateTotal.js` |
| **Delete Expense** | `ae4` | `deleteExpense.js` |

All backend tasks complete! The "Wire Up UI" task should now be unblocked.
```

---

#### 步骤 4：把所有内容串联起来

在同一目录中打开**第四个终端**。该会话会等待并行工作完成后再继续。

##### goose 提示词
```
Check beads for the expense tracker "Wire Up UI" task.

If blocked, tell me what it's waiting on and keep checking every minute.

If ready, implement it - connect the UI buttons to the backend functions.

When done, mark the task complete in beads.
```

##### goose 输出
```
─── blocked | beads ──────────────────────────

Found it! The **"Wire Up UI"** task (`ultimate-beads-test-m7i`) is currently **blocked** by 4 dependencies:

| Blocker ID | Title | Status |
|------------|-------|--------|
| `29u` | Calculate Total | blocked |
| `5x5` | Add Expense | blocked |
| `ae4` | Delete Expense | blocked |
| `vt2` | CSS Styling | blocked |

## 🔄 Status: BLOCKED

The **"Wire Up UI"** task is waiting on:
1. **Add Expense** - Function to add expense to storage
2. **Calculate Total** - Function to sum all expenses
3. **Delete Expense** - Function to remove expense from storage
4. **CSS Styling** - Style the expense tracker app with CSS

I'll check again in 1 minute to see if these blockers have been completed...

─── shell | developer ──────────────────────────
command: sleep 60

─── show | beads ──────────────────────────
issue_id: ultimate-beads-test-m7i

🎉 **All blockers are now CLOSED!** The "Wire Up UI" task is now **READY** to work on!

| Blocker | Title | Status |
|---------|-------|--------|
| `29u` | Calculate Total | ✅ closed |
| `5x5` | Add Expense | ✅ closed |
| `ae4` | Delete Expense | ✅ closed |
| `vt2` | CSS Styling | ✅ closed |

─── update | beads ──────────────────────────
issue_id: ultimate-beads-test-m7i
status: in_progress

─── text_editor | developer ──────────────────────────
path: app.js
command: write

─── close | beads ──────────────────────────
issue_id: ultimate-beads-test-m7i
reason: Implemented app.js to wire up UI - connected form submission to addExpense, delete buttons to deleteExpense, total display to calculateTotal

## ✅ Task Complete: Wire Up UI

**Created `app.js`** that:
- Connects form submission to `addExpense()`
- Renders expenses from storage on page load
- Wires delete buttons to `deleteExpense()`
- Updates total display using `calculateTotal()`

To test it, run: open index.html

Or start a local server: python3 -m http.server 8000 and visit http://localhost:8000
```

---

## Excalidraw 扩展

> 原文：https://block.github.io/goose/docs/mcp/excalidraw-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/REc5IvWvI5s" />

本教程介绍如何将 [Excalidraw MCP App](https://github.com/excalidraw/excalidraw-mcp)添加为 goose 扩展，使 goose 能够实时绘制手绘风格的 Excalidraw 图表。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
   [启动安装程序](goose://extension?cmd=http&id=excalidraw&name=Excalidraw&url=https%3A%2F%2Fexcalidraw-mcp-app.vercel.app%2Fmcp&description=Excalidraw%20MCP%20App%20for%20AI-powered%20diagramming)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  添加一个 `Remote Extension (Streamable HTTP)` 扩展类型，配置如下：

  **Endpoint URL**
```
https://excalidraw-mcp-app.vercel.app/mcp
```
  </TabItem>
</Tabs>
:::

### 配置

这些步骤配置的是 Remote MCP 服务器。其他部署选项请参阅 [Excalidraw MCP App 文档](https://github.com/excalidraw/excalidraw-mcp)。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="Excalidraw"
      extensionName="Excalidraw MCP App"
      description="Excalidraw MCP App for diagramming"
      type="http"
      url="https://excalidraw-mcp-app.vercel.app/mcp"
      envVars={[]}
    />

  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Excalidraw"
      description="Excalidraw MCP App for diagramming"
      type="http"
      url="https://excalidraw-mcp-app.vercel.app/mcp"
      timeout={300}
    />

  </TabItem>
</Tabs>

### 示例用法

在本示例中，我们使用 Excalidraw MCP App 让 Goose 实时可视化它自己的自动化流水线。这展示了 Goose 如何连接实时工具、对工作流进行推理，并逐个元素地生成结构化图表。

#### goose 提示词
```
Hey Goose review my video automation recipe and create a visual of the automation pipeline for me. I want clean lines and clear labels.
```

#### goose 输出

```

─── reading /Users/ebonyl/Desktop/plug-and-play-video.yaml ──────────────────────────

─── Create View elements: [ {"type":"cameraUpdate","width":600}, ...] ──────────────────────────

```
![excalidraw 图片](https://block.github.io/goose/img/excalidrawImage.png)

---

## Figma 扩展

> 原文：https://block.github.io/goose/docs/mcp/figma-mcp

本教程介绍如何将 [Figma Dev Mode MCP 服务器](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Dev-Mode-MCP-Server)添加为 goose 扩展，以支持与 Figma 文件、设计和组件交互。

:::info
该 MCP 服务器需要在 Professional、Organization 或 Enterprise Figma 套餐中拥有 Dev 或 Full 席位。
:::

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    [启动安装程序](goose://extension?type=streamable_http&url=http%3A%2F%2F127.0.0.1%3A3845%2Fmcp&id=figma&name=Figma&description=Convert%20Figma%20designs%20into%20code%20and%20extract%20design%20context)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    使用 `goose configure` 添加一个 `Remote Extension (Streamable HTTP)` 扩展类型，配置如下：
    
    **Endpoint URL**
    
```
http://127.0.0.1:3845/mcp
```
  </TabItem>
</Tabs>

**必需设置**

必须在 [Figma 桌面应用](https://www.figma.com/downloads/)中启用 Dev Mode MCP 服务器
:::

### 配置

1. 按照 Figma 的[Dev Mode MCP 服务器指南](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Dev-Mode-MCP-Server)中的说明启用 MCP 服务器。

   你的服务器现在将运行在 `http://127.0.0.1:3845/mcp`

   :::info 备选设置
   如果你在桌面应用中看不到说明中所述的 `Preferences` 菜单，可以试试这样：
   1. 点击设计文件底部的 `</>` 开关
   2. 在右侧面板中，打开 `Enable MCP server` 开关
   :::

2. 将 Figma 扩展添加到 goose：
   <Tabs groupId="interface">
     <TabItem value="ui" label="goose Desktop" default>
       <GooseDesktopInstaller
         extensionId="figma"
         extensionName="Figma"
         description="Convert Figma designs into code and extract design context"
         type="http"
         url="http://127.0.0.1:3845/mcp"
       />
     </TabItem>
     <TabItem value="cli" label="goose CLI">
       <CLIExtensionInstructions            
         name="figma"
         description="Convert Figma designs into code and extract design context"
         type="http"
         url="http://127.0.0.1:3845/mcp"
         timeout={300}
       />
     </TabItem>
   </Tabs>

### 示例用法

goose 中的 Figma 扩展与 Figma 桌面应用配合工作。你可以使用该扩展来：
- 将 Figma 设计转换为可直接上线的代码（React、Vue、HTML/CSS 等）
- 提取设计 token、变量，并生成设计系统规则
- 捕获你的设计的视觉参考

让我们试着把一份 Figma 设计转换为 React 代码。首先，复制链接：
  1. 在已启用 MCP 服务器的 [Figma 桌面应用](https://www.figma.com/downloads/)中打开一个设计文件
  2. 在图层面板中，右键点击任意画板或组件，选择 `Copy link to selection`

:::tip
你可以向 goose 提供 Figma 链接，也可以直接在 Figma 桌面应用中选择某个元素。
:::

#### goose 提示词

```
Convert this to React: https://www.figma.com/design/B6IFM1qjwxJw5fOYJYKRl5/Buttons-?node-id=351-8&m=dev
```

#### goose 输出

:::note 桌面版

我将帮你把那份 Figma 设计转换为 React。让我先检查 Figma 文件，了解设计结构和组件。

```
manage_extensions action, extension_name
```

我将帮你把那份 Figma 设计转换为 React。让我先从 URL 中提取 node ID，然后为你生成 React 代码。

```
get_code nodeId, clientLanguages, clientFrameworks
```

```
get_image nodeId, clientLanguages, clientFrameworks
```

我已成功将你的 Figma 设计转换为 React！以下是生成的组件：

```jsx
const imgImage1 = "http://localhost:3845/assets/e0e0f6accb741cb6cacec2697cef047a7eea7e30.png";

function Component1() {
  return (
    <div className="relative size-full" data-name="Component 1" data-node-id="351:8">
      <div className="absolute bg-[#d9d9d9] inset-0 rounded-lg" data-node-id="351:2" />
      <div
        className="absolute font-['Inter:Black',_sans-serif] font-black inset-[23.33%_2.56%_22.22%_56.41%] leading-[normal] not-italic text-[#333b43] text-[20px]"
        data-node-id="351:3"
      >
        <p className="block mb-0">ask</p>
        <p className="block">goose</p>
      </div>
      <div
        className="absolute aspect-[92/90] bg-center bg-cover bg-no-repeat left-0 right-[52.82%] rounded-lg top-0"
        data-name="image 1"
        data-node-id="351:6"
        style={{ backgroundImage: `url('${imgImage1}')` }}
      />
    </div>
  );
}

export default function Component2() {
  return (
    <div className="relative size-full" data-name="Component 1" data-node-id="351:8">
      <Component1 />
    </div>
  );
}
```

##### 生成组件的主要特性：

- **Tailwind CSS 样式**：使用 Tailwind 类实现响应式设计和样式
- **图片资源**：goose logo 作为背景图从 localhost 服务器加载  
- **排版**：对 "ask goose" 文本使用 Inter Black 字体
- **布局**：使用绝对定位和精确的 inset 值来匹配 Figma 设计
- **响应式**：使用相对定位和基于百分比的 inset 以实现可伸缩性

##### 组件结构：
- **背景**：浅灰色圆角容器（#d9d9d9）
- **Logo**：位于左侧的 goose 剪影图片
- **文本**：位于右侧、深灰色（#333b43）的 "ask goose" 文本

该组件保持了与你 Figma 设计完全一致的视觉层级和样式，同时完全响应式，可直接集成到使用 Tailwind CSS 的 React 应用中。

:::

---

## Blender 扩展

> 原文：https://block.github.io/goose/docs/mcp/blender-mcp

<YouTubeShortEmbed videoUrl="https://www.youtube.com/embed/izoQatKtJ2I" />

本教程介绍如何将 [Blender MCP 服务器](https://github.com/ahujasid/blender-mcp)添加为 goose 扩展，以创建 3D 场景、用自然语言控制 Blender、生成模型、应用材质等。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?cmd=uvx&arg=blender-mcp&id=blender-mcp&name=Blender&description=Blender%203D%20scene%20creation%20integration)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
uvx blender-mcp
```
  </TabItem>
</Tabs>
:::

**要求**

下载 [Blender 应用](https://www.blender.org/download/)和 [Blender MCP 插件文件](https://github.com/ahujasid/blender-mcp/blob/main/addon.py)

### 配置

:::info
注意，运行此命令需要在你的系统上安装 [uv](https://docs.astral.sh/uv/#installation)，因为它使用 `uvx`。
:::

1. 下载 [Blender 应用](https://www.blender.org/download/)
2. 添加 Blender MCP 插件
    - 从 [Blender MCP 仓库](https://github.com/ahujasid/blender-mcp/blob/main/addon.py)下载 `addon.py` 文件。
    - 打开 Blender
    - 依次进入 `Edit` > `Preferences` > `Add-ons`。
    - 点击下拉箭头，选择 `install from disk`，添加你下载的 `addon.py` 文件。
    - 安装完成后，勾选以启用 `Blender MCP`。
3. 启动 Blender MCP 服务器 
    - 在 Blender 中，按 N 打开侧边栏。
    - 切换到 Blender MCP 选项卡。
    - 点击 `connect to MCP server`

#### 添加 Blender MCP 服务器

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseDesktopInstaller
    extensionId="blender-mcp"
    extensionName="Blender"
    description="Blender 3D scene creation integration"
    command="uvx"
    args={["blender-mcp"]}
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Blender"
      description="Blender 3D scene creation integration"
      command="uvx blender-mcp"
    />
  </TabItem>
</Tabs>

### 示例用法

在本示例中，我将向你展示如何配合 Blender 扩展使用 goose 从零构建一个完整的 3D 篝火场景。通过用自然语言自动化 Blender 控制，goose 可以创建原木和火球等对象、应用逼真的材质、添加灯光效果、为火花生成粒子、创建细微的烟雾，甚至让火焰随时间轻柔跳动。

在本示例中，我将向你展示如何配合 Blender 扩展使用 goose，仅通过描述你想要的效果，就构建一个完整的 3D 篝火场景，包括原木、火球、灯光和细微的火焰动画。

#### goose 提示词

> Build a cozy campfire scene. Add a ground plane, place a few logs in a circle, and add a glowing fireball in the middle. Set the lighting to a warm tone like a sunset, and angle the camera for a dramatic shot. Give the logs a rough wood texture and make the fireball emit light.


#### goose 输出

:::note CLI

我将帮你用 Blender 创建一个温馨的篝火场景。让我们分步骤进行，结合使用基础对象、来自 PolyHaven 的纹理和恰当的灯光。首先，让我们看看当前的场景情况。

─── **获取场景信息** ───

让我们一步步构建场景：

首先，删除默认立方体并设置地平面：

─── **执行 Blender 代码** ───

2. 现在让我们把原木摆成一圈：

─── **执行 Blender 代码** ───

3. 让我们在中间创建发光的火球：

─── **执行 Blender 代码** ───

让我修正火球的材质：

─── **执行 Blender 代码** ───

4. 最后，让我们为戏剧性的日落镜头设置灯光和相机：

─── **执行 Blender 代码** ───

我已经创建了一个温馨的篝火场景，包含以下元素：

1. 一个带有深棕色材质的大型地平面
2. 5 根摆成一圈的原木，使用粗糙木质材质
3. 中间一个使用自发光材质的发光火球
4. 一盏点光源以营造火光效果
5. 调整主太阳光以营造温暖的日落氛围
6. 将相机定位到戏剧性的角度
7. 使用 Cycles 设置场景以获得更好的渲染效果

场景营造出温暖、温馨的氛围，原木自然地围绕发光的火球摆放。灯光以暖色调模拟日落，相机的位置则从有趣的角度捕捉场景。

如果你想做任何调整，例如：

- 更改任何元素的尺寸或位置
- 调整灯光强度
- 修改相机角度
- 添加更多细节，如小石块或额外的原木

只要告诉我，我就会帮你进一步完善这个场景！
:::

##### Blender 图片

![Blender MCP 场景](https://block.github.io/goose/img/blender.png)

---

## Ophis 扩展

> 原文：https://block.github.io/goose/docs/mcp/ophis-mcp

本教程介绍如何将 [Ophis](https://ophis.fi)添加为 goose 扩展，让 goose 能够把自然语言的兑换请求转换为跨受支持链的可执行订单。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    [启动安装程序](goose://extension?type=streamable_http&url=https%3A%2F%2Fmcp.ophis.fi%2Fmcp&id=ophis&name=Ophis&description=Natural-language%20intent%20DEX%20aggregator%20with%20a%20keyless%20MCP%20server%20for%20AI%20agents)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    使用 `goose configure` 添加一个 `Remote Extension (Streamable HTTP)` 扩展类型，配置如下：

    **Endpoint URL**
```
https://mcp.ophis.fi/mcp
```
  </TabItem>
</Tabs>
:::

### Ophis 是什么？

Ophis 是一个基于意图的 DEX 聚合器，带有一层自然语言层，并为 AI 代理提供无需密钥的 MCP 服务器。它是非托管的、免 gas 的，并具备 MEV 保护，还会将兑换盈余返还给交易者。Ophis 是 CoW Protocol 的一个分支。它在 Optimism 和 Unichain 上部署自己的结算合约，并在其他受支持的链（Ethereum、Base、Arbitrum、Polygon、BNB Chain、Gnosis、Avalanche、Linea、Plasma 和 Ink）上通过 CoW Protocol 路由。

该 MCP 服务器无需密钥，也不需要 API key 或环境变量。它暴露十四个工具：`parse_intent`、`resolve_token`、`list_chains`、`get_quote`、`expected_surplus`、`build_order`、`validate_order`、`submit_order`、`lookup_tier`、`get_integrator_earnings`、`get_balances`、`get_portfolio`、`get_gas` 和 `get_token_chart`。交易由用户自己的钱包签名，因此服务器从不持有密钥或资金。

### 配置

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="ophis"
      extensionName="Ophis"
      description="Natural-language intent DEX aggregator with a keyless MCP server for AI agents"
      type="http"
      url="https://mcp.ophis.fi/mcp"
    />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Ophis"
      description="Natural-language intent DEX aggregator with a keyless MCP server for AI agents"
      type="http"
      url="https://mcp.ophis.fi/mcp"
    />
  </TabItem>
</Tabs>

### 示例用法

配置好 Ophis 后，你可以用通俗的语言描述一笔兑换，并让 goose 准备订单。以下是一些示例：

**解析意图**
```
Parse this swap intent: "swap 100 USDC for ETH on Base".
```

**获取报价**
```
Get a quote to swap 0.5 WETH for USDC on Arbitrum.
```

**列出受支持的链**
```
Which chains does Ophis support?
```

服务器返回报价和未签名订单。实际交易由你自己的钱包签名，因此密钥或资金永远不会与扩展共享。

### 资源

- 网站：[ophis.fi](https://ophis.fi)
- 应用：[swap.ophis.fi](https://swap.ophis.fi)
- 文档：[docs.ophis.fi](https://docs.ophis.fi)
- 面向具备 shell 能力的代理的 Agent skills：[ophis.fi/.well-known/agent-skills](https://ophis.fi/.well-known/agent-skills/index.json)
- 源码：[github.com/ophis-fi/ophis](https://github.com/ophis-fi/ophis)

---

## Rendex 扩展

> 原文：https://block.github.io/goose/docs/mcp/rendex-mcp

本教程介绍如何将 [Rendex MCP 服务器](https://github.com/copperline-labs/rendex-mcp)添加为 goose 扩展，以从任意网页或原始 HTML 截取屏幕截图、生成 PDF 并将 HTML 渲染为图片——适用于归档 UI、生成发票和报告、制作 OG 图片，以及为 goose 提供可靠的「看网页」能力，而无需启动完整的浏览器自动化栈。

### 配置

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?type=streamable_http&url=https%3A%2F%2Fmcp.rendex.dev%2Fmcp&id=rendex-mcp&name=Rendex&description=Capture%20screenshots%2C%20generate%20PDFs%2C%20and%20render%20HTML%20to%20images%20via%20AI%20agents&header=Authorization%3DBearer%20YOUR_RENDEX_API_KEY)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  添加一个 `Remote Extension (Streamable HTTP)` 扩展类型，配置如下：

  **Endpoint URL**
```
https://mcp.rendex.dev/mcp
```
  </TabItem>
</Tabs>

  **Custom Request Header**
```
Authorization: Bearer <YOUR_RENDEX_API_KEY>
```
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="rendex-mcp"
      extensionName="Rendex"
      description="Capture screenshots, generate PDFs, and render HTML to images via AI agents"
      type="http"
      url="https://mcp.rendex.dev/mcp"
      envVars={[
        { name: "Authorization", label: "Bearer YOUR_RENDEX_API_KEY" }
      ]}
      apiKeyLink="https://rendex.dev/dashboard/keys"
      apiKeyLinkText="Rendex API key"
    />
  </TabItem>

  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Rendex"
      description="Capture screenshots, generate PDFs, and render HTML to images via AI agents"
      type="http"
      url="https://mcp.rendex.dev/mcp"
      timeout={300}
      envVars={[
        { key: "Authorization", value: "Bearer rdx_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" }
      ]}
      infoNote={
        <>
          Obtain your <a href="https://rendex.dev/dashboard/keys" target="_blank" rel="noopener noreferrer">Rendex API key</a> and paste it in as the <code>Bearer</code> token. Free tier includes 500 calls/month, no credit card required.
        </>
      }
    />
  </TabItem>
</Tabs>

### 示例用法

让我们使用 Rendex 扩展从原始 HTML 生成一份发票 PDF，并归档一个产品页面。

#### goose 提示词

```
1. Render this HTML as an A4 PDF with 1cm margins:

   <!doctype html>
   <html>
     <body style="font-family: system-ui; padding: 40px;">
       <h1>Invoice #0042</h1>
       <p>Bill to: Acme Corp</p>
       <table>
         <tr><td>MCP server listing</td><td>$500.00</td></tr>
         <tr><td>Total</td><td><b>$500.00</b></td></tr>
       </table>
     </body>
   </html>

2. Then take a full-page screenshot of https://news.ycombinator.com in dark mode

3. Return both results so I can save them
```

#### goose 输出

```
I'll generate the invoice PDF first, then capture the HN page.

[rendex_screenshot: format=pdf, pdfFormat=A4, pdfMargin={top: 1cm, ...}, html=<invoice markup>]
✓ PDF captured successfully (12,344 bytes)
  width: 1280  height: 800  capturedAt: 2026-04-15T12:34:56Z

[rendex_screenshot: url=https://news.ycombinator.com, fullPage=true, darkMode=true]
✓ Screenshot captured (PNG, 847KB)
  width: 1280  height: 4,321  waitStrategy: networkidle2

Both renders completed. You have:
  1. Invoice PDF (A4, 12.3KB) — base64 in result 1
  2. Dark-mode full-page screenshot of Hacker News (PNG, 847KB) — base64 in result 2
```

### 价格

Rendex 可免费试用——免费套餐无需信用卡。

| 套餐 | 每月调用次数 | 速率限制 |
|---|---|---|
| 免费 | 500 | 10/分钟 |
| 入门 | 10,000 | 60/分钟 |
| 专业 | 100,000 | 300/分钟 |
| 企业 | 自定义 | 1,000/分钟 |

在 [rendex.dev](https://rendex.dev)获取 API key。

### 链接

- **网站**：[rendex.dev](https://rendex.dev)
- **GitHub**：[copperline-labs/rendex-mcp](https://github.com/copperline-labs/rendex-mcp)
- **npm**：[`@copperline/rendex-mcp`](https://www.npmjs.com/package/@copperline/rendex-mcp)
- **Smithery**：[smithery.ai/server/copperline/rendex-mcp](https://smithery.ai/server/copperline/rendex-mcp)
- **官方 MCP Registry**：`io.github.copperline-labs/rendex-mcp`

---

## Nano Banana 扩展

> 原文：https://block.github.io/goose/docs/mcp/nano-banana-mcp

本教程介绍如何将 [Nano Banana MCP 服务器](https://github.com/ConechoAI/Nano-Banana-MCP)添加为 goose 扩展，它使用 Google 的 Gemini Image API 提供 AI 图像生成和编辑能力。

:::tip 快速安装
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?cmd=npx&arg=nano-banana-mcp&id=nano-banana-mcp&name=Nano%20Banana&description=Image%20generation%20with%20Gemini)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  **命令**
```sh
npx nano-banana-mcp
```
  </TabItem>
</Tabs>
  **环境变量**
```
GEMINI_API_KEY: <YOUR_API_KEY>
```
:::

### 配置

:::info
注意，运行此命令需要在你的系统上安装 [Node.js](https://nodejs.org/)，因为它使用 `npx`。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    <GooseDesktopInstaller
      extensionId="nano-banana-mcp"
      extensionName="Nano Banana"
      description="Image generation with Gemini"
      type="stdio"
      command="npx"
      args={["nano-banana-mcp"]}
      envVars={[
        { name: "GEMINI_API_KEY", label: "Gemini API Key" }
      ]}
      apiKeyLink="https://aistudio.google.com/api-keys"
      apiKeyLinkText="Gemini API Key"
    />
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    <CLIExtensionInstructions
      name="Nano Banana"
      description="Image generation with Gemini"
      type="stdio"
      command="npx nano-banana-mcp"
      timeout={300}
      envVars={[
        { key: "GEMINI_API_KEY", value: "▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪" }
      ]}
      infoNote={
        <>
          Get your API key from <a href="https://aistudio.google.com/api-keys" target="_blank" rel="noopener noreferrer">
            Google AI Studio
          </a> and paste it in.
        </>
      }
    />
  </TabItem>
</Tabs>

### 示例用法

使用 Nano Banana，你可以用自然语言生成新图像并编辑现有图像。只需描述你想要创建或修改的内容，goose 就会把它转成详细的提示词提供给 Nano Banana。

#### 图像创建示例
通过描述你想要的内容从零创建图像：

- 「创建一张山间日落的图像」
- 「为一家名为 Bean There 的咖啡店生成一个 logo」
- 「画一条守护宝藏的奇幻巨龙」

#### 图像迭代示例
在生成或编辑图像后，你可以不断细化它：

- 「把天空调得更紫一些」
- 「在角落里加一只猫」
- 「移除文字」
- 「让它更卡通风格一些」

#### goose 提示词

> use nano banana to create an image of a fantasy ice mage crafting ice sculptures in a frozen workshop

#### goose 输出

:::note 桌面版

🎨 已用 nano-banana（Gemini 2.5 Flash Image）生成图像！


提示词："一位奇幻冰法师在冰封工坊里雕刻冰雕。法师身着带有霜纹的飘逸长袍，双手散发着蓝色魔法能量，正在塑造精巧的冰雕。工坊里满是美丽的冰封造物——冰动物、水晶般的花朵和精致的雕像。冰柱从天花板垂下，霜覆盖着石墙，魔幻的蓝光照亮了整个空间。雪花在空中轻轻飘落。细节丰富的奇幻艺术风格，充满魔幻氛围。"

✨ **完成！** 这是你的奇幻冰法师图像！

图像效果很美——它包含：

- **冰法师**：一位身着优雅深蓝色长袍的戴兜帽人物，长袍上有精巧的霜和雪花刺绣，双手散发着蓝色魔法能量
- **冰雕**：一尊正在被雕刻的惊艳独角兽、背景中的一匹飞马、水晶般的玫瑰花束，以及小骑士雕像
- **冰封工坊**：一个宏伟的、类似冰教堂的空间，拱形天花板上垂着壮观的冰柱，覆盖着霜的柱子，以及几何形状的冰纹
- **魔幻氛围**：彩虹般的折射光、飘落的雪粒，以及无处不在的空灵蓝色光晕

图像已保存至：
`generated_imgs/generated-2025-12-04T04-15-47-907Z-3grhec.png`

![](https://block.github.io/goose/img/nano-banana-generated-img.png)

你想让我对这张图像做任何修改吗？我可以调整法师的外观等元素、添加更多雕塑、更改灯光，或使用 `continue_editing` 功能微调任何其他细节！

:::
