# goose 官方文档中文手册：第 02 章　模型提供方全览

## 配置 LLM 提供方

> 原文：https://block.github.io/goose/docs/getting-started/providers

goose 兼容种类繁多的 LLM 提供方，你可以选择并集成自己偏好的模型。

:::tip 模型选择
<ModelSelectionTip/>
[Berkeley Function-Calling Leaderboard][function-calling-leaderboard] 可以作为选择模型时的良好参考。
:::

### 可用提供方

| 提供方                                                                    | 描述                                                                                                                                                                                                               | 参数                                                                                                                                                                          |
|-----------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [AI/ML API](https://aimlapi.com/)                                           | 一个 API key 即可使用来自众多提供方的 300+ 聊天、图像、视频、音频和嵌入模型，兼容 OpenAI。 | `AIMLAPI_API_KEY` |
| [Amazon Bedrock](https://aws.amazon.com/bedrock/)                           | 提供多种基础模型，包括 Claude、Jurassic-2 等。**AWS 环境变量必须提前设置，不能通过 `goose configure` 配置**                                           | 凭证认证：`AWS_PROFILE`，或 `AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`、`AWS_REGION`<br /><br />Bearer token 认证：`AWS_BEARER_TOKEN_BEDROCK` 以及 `AWS_REGION`、`AWS_DEFAULT_REGION` 或 `AWS_PROFILE` |
| [Amazon SageMaker TGI](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html) | 通过 Amazon SageMaker 端点运行 Text Generation Inference 模型。**AWS 凭证必须提前配置。** | `SAGEMAKER_ENDPOINT_NAME`、`AWS_REGION`（可选）、`AWS_PROFILE`（可选）  |
| [Anthropic](https://www.anthropic.com/)                                     | 提供 Claude，一款用于自然语言任务的先进 AI 模型。                                                                                                                                                           | `ANTHROPIC_API_KEY`、`ANTHROPIC_HOST`（可选）                                                                                                                                                                 |
| [Atomic Chat](https://github.com/AtomicBot-ai/Atomic-Chat)                | 使用 Atomic Chat 的 OpenAI 兼容服务器运行本地模型。**由于该提供方在本地运行，你必须先[下载模型](#local-llms)。** | 无需配置。默认连接位于 `localhost:1337` 的本地服务器。 |
| [Avian](https://avian.io/)                                                   | 高性价比的推理 API，提供 DeepSeek、Kimi、GLM 和 MiniMax 模型。兼容 OpenAI，支持流式传输和函数调用。                                                                                  | `AVIAN_API_KEY`、`AVIAN_HOST`（可选）                                                                                                                                            |
| [Azure AI Foundry](https://block.github.io/goose/docs/guides/azure-foundry-provider) | 访问通过 Azure AI Foundry 项目或 MaaS 端点部署的 OpenAI、Anthropic、Microsoft、Meta、Mistral、DeepSeek、GLM、Kimi 及其他模型。 | `AZURE_FOUNDRY_ENDPOINT`、`AZURE_FOUNDRY_API_KEY`（可选）、`AZURE_FOUNDRY_AD_TOKEN`（可选）、`AZURE_FOUNDRY_API_VERSION`（可选） |
| [Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/) | 访问 Azure 托管的 OpenAI 模型，包括 GPT-4 和 GPT-3.5。支持 API key、Entra ID bearer token 和 Azure 凭证链认证。                                                                                          | `AZURE_OPENAI_ENDPOINT`、`AZURE_OPENAI_DEPLOYMENT_NAME`、`AZURE_OPENAI_API_KEY`（可选）、`AZURE_OPENAI_AD_TOKEN`（可选）                                                                                           |
| [ChatGPT Codex](https://chatgpt.com/codex) | 访问针对代码生成与理解优化的 GPT-5 Codex 模型。**需要 ChatGPT Plus/Pro 订阅。** | 无需手动配置 key。CLI 和 Desktop 均使用基于浏览器的 OAuth 认证。 |
| [Databricks](https://www.databricks.com/)                                   | 用于构建和部署模型的统一数据分析与 AI 平台。                                                                                                                                                 | `DATABRICKS_HOST`、`DATABRICKS_TOKEN` |
| [Docker Model Runner](https://docs.docker.com/ai/model-runner/)                             | 在 Docker Desktop 或 Docker CE 中运行、提供 OpenAI 兼容 API 端点的本地模型。**由于该提供方在本地运行，你必须先[下载模型](#local-llms)。**                     | `OPENAI_HOST`、`OPENAI_BASE_PATH`   |
| [EmpirioLabs AI](https://empiriolabs.ai/)                                      | 通过一个兼容 OpenAI 且支持流式传输的 API 提供前沿的开源与专有聊天模型（Qwen、DeepSeek、GLM、Kimi、MiniMax）。目录见 `https://api.empiriolabs.ai/v1/models`。        | `EMPIRIOLABS_API_KEY`                                                                                                                                                              |
| [Friendli AI](https://friendli.ai/)                                            | Friendli Model API 提供对一组精选模型的即时访问，由名为 [Friendli Engine](https://friendli.ai/why-friendliai) 的专有推理栈驱动，实现高性能、低成本的推理。               | `FRIENDLI_API_KEY`                                                                                                                                                                  |
| [FuturMix](https://futurmix.ai/)                                            | 统一的 AI 网关，通过兼容 OpenAI 的 API 提供对 Anthropic、Google、OpenAI 和 DeepSeek 模型的访问。                                                                          | `FUTURMIX_API_KEY`                                                                                                                                                                  |
| [Gemini](https://ai.google.dev/gemini-api/docs)                             | Google 提供的高级 LLM，具备多模态能力（文本、图像）。Gemini 3 模型支持可配置的[思考等级](#gemini-3-thinking-levels)。                                                                                                | `GOOGLE_API_KEY`、`GEMINI3_THINKING_LEVEL`（可选）                                                                                                                              |
| [GCP Vertex AI](https://cloud.google.com/vertex-ai)                         | Google Cloud 的 Vertex AI 平台，支持 Gemini 和 Claude 模型。**凭证必须[提前配置](https://cloud.google.com/vertex-ai/docs/authentication)。** 根据组织策略（如已配置）过滤允许使用的模型。 | `GCP_PROJECT_ID`、`GCP_LOCATION`，以及可选的 `GCP_MAX_RATE_LIMIT_RETRIES`（5）、`GCP_MAX_OVERLOADED_RETRIES`（5）、`GCP_INITIAL_RETRY_INTERVAL_MS`（5000）、`GCP_BACKOFF_MULTIPLIER`（2.0）、`GCP_MAX_RETRY_INTERVAL_MS`（320_000）。 |
| [GitHub Copilot](https://docs.github.com/en/copilot/using-github-copilot/ai-models) | 通过 GitHub 的 Copilot 基础设施访问来自 OpenAI、Anthropic、Google 及其他提供方的 AI 模型。**需要具有 Copilot 访问权限的 GitHub 账号。** | 无需手动配置 key。CLI 和 Desktop 均使用[设备流认证](#github-copilot-authentication)。 |
| [Gondola](https://gondola-ai.com/guides)                                     | 通过 Venice AI 按请求付费的推理，以 Base 上的 USDC 结算。无需订阅或最低消费。包含保护隐私的 TEE 模型（`e2ee-*`）。兼容 OpenAI。                                                      | `GONDOLA_API_KEY`、`GONDOLA_HOST`（可选）                                                                                                                                        |
| [Groq](https://groq.com/)                                                   | 面向 LLM 的高性能推理硬件与工具。                                                                                                                                                                   | `GROQ_API_KEY`                                                                                                                                                                      |
| [iFlytek Spark](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html) | 通过兼容 OpenAI 的 HTTP API 访问 iFlytek Spark（讯飞星火）模型（4.0Ultra、generalv3.5、max-32k）。最适合聊天：Spark 需要 `tool_calls_switch=true`（此处无法注入）才能返回 OpenAI 风格的工具调用。 | `SPARK_API_PASSWORD` |
| [iFlytek Astron MaaS](https://maas.xfyun.cn/)                               | iFlytek Astron MaaS（讯飞星辰）通过兼容 OpenAI 的 API 托管 Spark X2、DeepSeek、GLM、Kimi、MiniMax、Qwen 及 Astron 编码模型。设置 `ASTRON_BASE_URL` 可在 Token Plan 与 Coding Plan 端点之间切换。 | `ASTRON_API_KEY`、`ASTRON_BASE_URL`（可选） |
| [IO Intelligence](https://io.net/) | 通过 io.net 兼容 OpenAI 的 API 为开放权重模型（DeepSeek、Qwen、Llama、GLM、Kimi、gpt-oss 等）提供推理。 | `IONET_API_KEY` |
| [LiteLLM](https://docs.litellm.ai/docs/) | LiteLLM 代理，支持多个模型，具备自动提示词缓存与统一 API 访问。 | `LITELLM_HOST`、`LITELLM_BASE_PATH`（可选）、`LITELLM_API_KEY`（可选）、`LITELLM_CUSTOM_HEADERS`（可选）、`LITELLM_TIMEOUT`（可选） |
| [LM Studio](https://lmstudio.ai/)                                          | 使用 LM Studio 的 OpenAI 兼容服务器运行本地模型。**由于该提供方在本地运行，你必须先[下载模型](#local-llms)。**                                                           | 无需配置。默认连接位于 `localhost:1234` 的本地服务器。                                                                                                             |
| [Meta](https://dev.meta.ai/)                                                | Meta 的 Model API，Muse Spark 模型之家。                                                                                                                                | `META_MODEL_API_KEY`                                                                                                                                                                |
| [Mistral AI](https://mistral.ai/)                                           | 提供对 Mistral 模型的访问，包括通用模型、专用编码模型（Codestral）和多模态模型（Pixtral）。                                                                   | `MISTRAL_API_KEY`                                                                                                 |
| [NEAR AI Cloud](https://cloud.near.ai/)                                     | 通过兼容 OpenAI 的 API 提供 TEE 支持的私有推理，支持动态模型发现。                                                                                                                   | `NEARAI_API_KEY`                                                                                                                                                                  |
| [Novita AI](https://novita.ai/)                                             | 90+ 开源模型，提供兼容 OpenAI 的 API 和有竞争力的价格。支持 Kimi K2.5、DeepSeek、GLM、MiniMax、Qwen 等。                                                                       | `NOVITA_API_KEY`                                                                                                  |
| [Ollama](https://ollama.com/)                                               | 本地模型运行器，支持 Qwen、Llama、DeepSeek 及其他开源模型。**由于该提供方在本地运行，你必须先[下载并运行模型](#local-llms)。**  | `OLLAMA_HOST`                                                                                                                                                                       |
| [Ollama Cloud](https://ollama.com/)                                         | 通过兼容 OpenAI 的 API 访问 ollama.com 上的托管模型。需要 Ollama 账号和 API key。  | `OLLAMA_CLOUD_API_KEY`                                                                                                                                                                       |
| [OpenAI](https://platform.openai.com/api-keys)                              | 提供 gpt-4o、o1 及其他高级语言模型。也支持兼容 OpenAI 的端点（例如自托管的 LLaMA、vLLM、KServe）。**不支持 o1-mini 和 o1-preview，因为 goose 使用工具调用。** | `OPENAI_API_KEY`、`OPENAI_HOST`（可选）、`OPENAI_ORGANIZATION`（可选）、`OPENAI_PROJECT`（可选）、`OPENAI_CUSTOM_HEADERS`（可选）                                       |
| [OpenRouter](https://openrouter.ai/)                                        | 用于统一访问各类模型的 API 网关，具备速率限制管理等功能。                                                                                                                             | `OPENROUTER_API_KEY`、`OPENROUTER_HOST`（可选）、`OPENROUTER_PARAMETERS`（可选）                                                                                              |
| [Perplexity](https://www.perplexity.ai/)                                    | 内置实时网页搜索依据的聊天模型。OpenAI 兼容的 chat completions API 位于 `https://api.perplexity.ai`。                                                                                          | `PERPLEXITY_API_KEY`                                                                                                                                                                |
| [OVHcloud AI](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/)       | 通过 AI Endpoints 服务提供对 Qwen、Llama、Mistral 和 DeepSeek 等开源模型的访问。                                                       | `OVHCLOUD_API_KEY`                                                                                                                                                                  |
| [Ramalama](https://ramalama.ai/)                                            | 使用原生 [OCI](https://opencontainers.org/) 容器运行时、[CNCF](https://www.cncf.io/) 工具并将模型作为 OCI 工件支持的本地模型。Ramalama API 是 Ollama 的兼容替代方案，可与 goose 的 Ollama 提供方一起使用。支持 Qwen、Llama、DeepSeek 及其他开源模型。**由于该提供方在本地运行，你必须先[下载并运行模型](#local-llms)。**  | `OLLAMA_HOST`                                                                                                                                                                       |
| [Routstr](https://routstr.com/)                                             | 兼容 OpenAI 的聚合器，将数十个上游提供方（Anthropic、OpenAI、Google、DeepSeek、Llama……）汇聚在单个 API 之后。使用你的 Routstr 实例签发的 `sk-...` bearer 进行认证——支付在 goose 之外处理。                                                                                                                                                                       | `ROUTSTR_API_KEY`、`ROUTSTR_HOST`（可选，默认 `https://api.routstr.com`）                                                                                                     |
| [SayGM](https://saygm.com/)                                                 | 通过兼容 OpenAI 的 API 提供 TEE 支持的私有推理，支持动态模型路由。价格在每次请求时于运行时确定。                                                                           | `SAYGM_API_KEY`                                                                                                   |
| [SaladCloud AI Gateway](https://salad.com/)                                 | 兼容 OpenAI 的方式访问 SaladCloud 托管的开源模型，包括 Qwen、Gemma 等。                                                                                                          | `SALAD_CLOUD_API_KEY`                                                                                                                                                              |
| [Scaleway](https://www.scaleway.com/en/generative-apis/)                    | 欧洲云服务，提供对 Mistral、Qwen 等模型及开源权重的 OpenAI 兼容访问。确保数据驻留与 GDPR 合规。                                                                                                                                                                                                                                                                | `SCW_SECRET_KEY`      |
| [Snowflake](https://docs.snowflake.com/user-guide/snowflake-cortex/aisql#choosing-a-model) | 使用 Snowflake Cortex 服务访问最新模型，包括 Claude 模型。**需要 Snowflake 账号和编程访问令牌（PAT）。**                                                     | `SNOWFLAKE_HOST`、`SNOWFLAKE_TOKEN`                                                                                                                                                                 |
| [VMware Tanzu Platform](https://techdocs.broadcom.com/us/en/vmware-tanzu/platform/ai-services/10-3/ai/index.html) | 通过 VMware Tanzu Platform 上的 AI Services 提供企业托管的 LLM 访问。模型从端点动态获取。 | `TANZU_AI_API_KEY`、`TANZU_AI_ENDPOINT` |
| [Tetrate Agent Router Service](https://router.tetrate.ai)                   | 面向 AI 模型（包括 Claude、Gemini、GPT、开放权重模型等）的统一 API 网关。支持 PKCE 认证流程以安全生成 API key。                                                                                | `TETRATE_API_KEY`、`TETRATE_HOST`（可选）                                                                                                                                        |
| [TrustedRouter](https://trustedrouter.com)                                  | 通过 TrustedRouter 兼容 OpenAI 的 API 访问来自 OpenAI、Anthropic、Google、DeepSeek 等提供方的模型，具备按请求路由与故障转移。                                                                                                     | `TRUSTEDROUTER_API_KEY`                                                                                                                                                             |
| [Venice AI](https://venice.ai/home)                                         | 提供对 Llama、Mistral、Qwen 等开源模型的访问，同时优先保护用户隐私。**需要账号和 [API key](https://docs.venice.ai/overview/guides/generating-api-key)。**                 | `VENICE_API_KEY`、`VENICE_HOST`（可选）、`VENICE_BASE_PATH`（可选）、`VENICE_MODELS_PATH`（可选）                                                                          |
| [Cerebras](https://cerebras.ai/)                                            | 在 Cerebras 晶圆级引擎上快速推理 Llama、Qwen 等模型。                                                                                                                                  | `CEREBRAS_API_KEY`                                                                                                                                                                  |
| [xAI](https://x.ai/)                                                        | 访问 xAI 的 Grok 模型，包括 grok-3、grok-3-mini 和 grok-3-fast，具有 131,072 token 上下文窗口。                                                                                                            | `XAI_API_KEY`、`XAI_HOST`（可选）                                                                                                                                                |

:::tip Claude 模型的提示词缓存
当通过 Anthropic、Amazon Bedrock、Databricks、OpenRouter 和 LiteLLM 提供方使用 Claude 模型时，goose 会自动启用 Anthropic 的[提示词缓存](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)。这会向请求添加 `cache_control` 标记，通过缓存常用上下文来降低较长对话的成本。技术细节见[提供方实现](https://github.com/aaif-goose/goose/tree/main/crates/goose/src/providers)。
:::

#### CLI 提供方

| 提供方                                                                    | 描述                                                                                                                                                                                                               | 要求                                                                                                                                                                          |
|-----------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Cursor Agent](https://docs.cursor.com/en/cli/overview)（`cursor-agent`）   | 使用 Cursor 的 AI CLI 工具，配合你的 Cursor 订阅。通过 cursor-agent 命令行界面提供对 GPT-5、Claude 4 及其他模型的访问。                                              | 已安装并完成认证的 cursor-agent CLI                                                                                                         |

#### ACP 提供方

goose 支持把 [Agent Client Protocol（ACP）](https://agentclientprotocol.com/) 代理作为提供方。ACP 提供方会把 goose 扩展作为 MCP 服务器传递给该代理。

| 提供方                                                                    | 描述                                                                                                                                                                                                               | 要求                                                                                                                                                                          |
|-----------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Claude ACP](https://github.com/agentclientprotocol/claude-agent-acp)（`claude-acp`） | 通过 ACP 使用 Claude Code。将 goose 扩展作为 MCP 服务器传递给该代理。 | `npm install -g @agentclientprotocol/claude-agent-acp`、有效的 Claude Code 订阅 |
| [Codex ACP](https://github.com/agentclientprotocol/codex-acp)（`codex-acp`） | 通过 ACP 使用 OpenAI Codex。将 goose 扩展作为 MCP 服务器传递给该代理。 | `npm install -g @agentclientprotocol/codex-acp`、有效的 ChatGPT Plus/Pro 订阅或 OpenAI API 额度 |

:::tip ACP 提供方
详细设置说明见 [ACP 提供方指南](https://block.github.io/goose/docs/guides/acp-providers)。
:::

#### Z.AI Coding Plan

在 goose Desktop 中，打开 **Settings → Models**，选择 **Z.AI Coding Plan**，然后输入你的 Coding Plan API key。模型选择器会从你的 Coding Plan 端点发现可用模型；使用 **Refresh** 更新列表。
Z.AI 可能列出你的订阅无法使用的模型；在你发送请求时才会检查访问权限。

在 CLI 中，在 `goose configure` 里选择 **Z.AI Coding Plan** 并提供你的 Coding Plan API key，或者设置 `GOOSE_PROVIDER=zai_coding_plan`、`GOOSE_MODEL=glm-5.3` 和
`ZAI_CODING_PLAN_API_KEY`。当端点不支持模型发现时，GLM-5.3 和 GLM-5.3-Flash 是回退选项。

该提供方使用专用的 OpenAI 兼容端点
`https://api.z.ai/api/coding/paas/v4`。它为流式请求（包括新发现的模型）同时启用 `stream` 和 `tool_stream`，因此工具参数会增量到达，并在工具结果轮次之间保留
`reasoning_content`。现有的 **Z.AI** 提供方继续使用 Anthropic 兼容端点。

参见 Z.AI 的 [Coding Plan 模型可用性](https://docs.z.ai/devpack/overview)、
[工具流式传输](https://docs.z.ai/guides/capabilities/stream-tool)和
[思考保留](https://docs.z.ai/guides/capabilities/thinking-mode)文档。

### 配置提供方与模型

要配置你所选的提供方、查看可用选项或选择模型，请访问 goose Desktop 中的 `Models` 标签页，或在 CLI 中运行 `goose configure`。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  **首次使用的用户：**

  在第一次打开 goose 时的欢迎界面上，你有以下选项：

  <OnboardingProviderSetup />

  <Tabs groupId="setup">
    <TabItem value="apikey" label="快速设置" default>
    1. 选择 `Quick Setup with API Key`。
    2. 输入来自你的提供方的 API key（例如 OpenAI、Anthropic 或 Google）。
    3. goose 会自动检测你的提供方并配置连接。
    4. 设置完成后，你就可以开始你的第一个会话。
    </TabItem>

    <TabItem value="chatgpt" label="ChatGPT 订阅">
    1. 选择 `ChatGPT Subscription`。
    2. goose 会打开一个浏览器窗口，让你用有效的 ChatGPT Plus 或 Pro 订阅凭证登录。
    3. 授权 goose 访问你的 ChatGPT 订阅。
    4. 当你返回 goose Desktop 时，你就可以开始你的第一个会话。
    </TabItem>
    <TabItem value="tetrate" label="Agent Router">
    我们建议新用户从 Tetrate 的 Agent Router 开始。Tetrate 提供对多个 AI 模型的访问，内置速率限制和自动故障转移。

    :::info 免费额度优惠
    当你第一次通过 goose 自动向 Tetrate 认证时，你将获得 $10 免费额度。该优惠对新的和现有的 Tetrate 用户均可用。
    :::
    1. 选择 `Agent Router by Tetrate`。
    2. goose 会打开一个浏览器窗口，让你向 Tetrate 认证，如果你还没有账号则会创建一个新账号。
    3. 当你返回 goose Desktop 时，你就可以开始你的第一个会话。
    </TabItem>

    <TabItem value="openrouter" label="OpenRouter">
    1. 选择 `Automatic setup with OpenRouter`。
    2. goose 会打开一个浏览器窗口，让你向 OpenRouter 认证，如果你还没有账号则会创建一个新账号。
    3. 当你返回 goose Desktop 时，你就可以开始你的第一个会话。
    </TabItem>

    <TabItem value="others" label="其他提供方">
    1. 如果你有想在 goose 中使用的特定提供方，并拥有来自该提供方的 API key，请选择 `Other Providers`。
    2. 找到你想要的提供方并点击其 `Configure` 按钮。如果你在列表中看不到你的提供方，请点击窗口底部的 `Add Custom Provider` 来[配置自定义提供方](#configure-custom-provider)。
    3. 根据你的提供方，你需要输入 API Key、API Host 或其他可选的[参数](#available-providers)。点击 `Submit` 按钮完成认证并开始你的第一个会话。

    :::info Ollama 模型检测
    对于 Ollama 用户，所有本地安装的模型都会自动显示在模型选择下拉菜单中。
    :::

    </TabItem>
  </Tabs>
  **更新你的 LLM 提供方和 API key：**
  1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏
  2. 点击侧边栏上的 `Settings` 按钮
  3. 点击 `Models` 标签页
  4. 点击 `Configure providers`
  5. 在列表中点击你的提供方
  6. 添加你的 API key 和其他必需配置，然后点击 `Submit`

  **更改当前模型：**
  1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏
  2. 点击侧边栏上的 `Settings` 按钮
  3. 点击 `Models` 标签页
  4. 点击 `Switch models`
  5. 在下拉菜单中从已配置的提供方中选择，或选择 `Use other provider` 来配置一个新的提供方
  6. 从可用选项中选一个模型，或选择 `Use custom model` 输入特定模型名
  7. 点击 `Select model` 确认你的选择

  :::tip 快捷键
  为了更快地访问，点击应用底部的当前模型名并选择 `Change Model`。
  :::

  **重新开始提供方和模型配置：**
  1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏
  2. 点击侧边栏上的 `Settings` 按钮
  3. 点击 `Models` 标签页
  4. 点击 `Reset Provider and Model` 清除当前设置并返回欢迎界面
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    1. 在你的终端中运行以下命令：

```sh
goose configure
```

    2. 从菜单中选择 `Configure Providers` 并按 `Enter`。

```
┌   goose-configure
│
◆  What would you like to configure?
// highlight-start
│  ● Configure Providers (Change provider or update credentials)
// highlight-end
│  ○ Custom Providers
│  ○ Add Extension
│  ○ Toggle Extensions
│  ○ Remove Extension
│  ○ goose Settings
└
```
    3. 选择一个模型提供方并按 `Enter`。使用方向键（↑/↓）在选项中移动，或开始输入以筛选列表。

```
┌   goose-configure
│
◇  What would you like to configure?
│  Configure Providers
│
◆  Which model provider should we use?
│  ○ Amazon Bedrock
│  ○ Amazon SageMaker TGI
// highlight-start
│  ● Anthropic (Claude and other models from Anthropic)
// highlight-end
│  ○ Azure OpenAI
│  ○ Claude Code CLI
│  ○ ...
└
```
    4. 在提示时输入你的 API key（以及任何其他配置细节）。

```
┌   goose-configure
│
◇  What would you like to configure?
│  Configure Providers
│
◇  Which model provider should we use?
│  Anthropic
│
◆  Provider Anthropic requires ANTHROPIC_API_KEY, please enter a value
// highlight-start
│  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
// highlight-end
└
```

       如果你只是更改模型，请跳过任何更新提供方配置的提示。

    5. 输入你想要的 `ANTHROPIC_HOST`，或按 `Enter` 使用默认值。

```
◆  Provider Anthropic requires ANTHROPIC_HOST, please enter a value
// highlight-start
│  https://api.anthropic.com (default)
// highlight-end
```
    6. 选择你想使用的模型。根据提供方的不同，你可以：
       - 从列表中选择模型
       - 按名称搜索模型
       - 直接输入模型名

```
│
◇  Model fetch complete
│
◇  Select a model:
// highlight-start
│  claude-sonnet-4-5 (default)
// highlight-end
│
◒  Checking your configuration...
└  Configuration saved successfully
```

       此更改会在你下次启动会话时生效。

  :::note
  `goose configure` 不支持输入自定义模型名。要使用不在提供方列表中的模型，请使用 goose Desktop 或直接编辑你的 [`config.yaml`](https://block.github.io/goose/docs/guides/config-files) 中的 `GOOSE_MODEL` 变量。
  :::

  :::tip
  使用 [`run` 命令](https://block.github.io/goose/docs/guides/goose-cli-commands#run-options)为单个会话设置模型：

```bash
goose run --model claude-sonnet-4-0 -t "initial prompt"
```
  :::

  </TabItem>
</Tabs>

#### 使用自定义 OpenAI 端点

内置的 OpenAI 提供方可以连接到 OpenAI 的官方 API（`api.openai.com`）或任何兼容 OpenAI 的端点，例如：
- 使用 vLLM 或 KServe 的自托管 LLM（例如 LLaMA、Mistral）
- 私有的 OpenAI 兼容 API 服务器
- 需要数据治理和安全合规的企业部署
- OpenAI API 代理或网关

:::tip 自定义提供方选项
需要连接多个 OpenAI 兼容端点？请改为[配置自定义提供方](#configure-custom-provider)，以便更轻松地切换、更好地组织，并获得自定义命名和可共享的配置。
:::

:::note 指向 LiteLLM 代理
你可以通过以下两种方式之一访问 [LiteLLM](https://docs.litellm.ai/) 代理——任选其一，不要混用：

- 使用 **OpenAI 提供方**：将 `OPENAI_HOST` 设置为代理的根地址（不带尾随路径），将 `OPENAI_BASE_PATH` 设置为其提供的路径（通常是 `v1/chat/completions`）。`404` 通常意味着 `OPENAI_BASE_PATH` 对你的代理来说是错的。`401` 且带有 `No api key passed in` 是另一个问题——API key 没有被加载（例如，把 key 放在 `config.yaml` 中，而它会被忽略）；参见[提供方 API key 与 `config.yaml`](https://block.github.io/goose/docs/guides/config-files#security-considerations)。
- 使用专用的 **LiteLLM 提供方**，它使用自己的 `LITELLM_HOST`、`LITELLM_BASE_PATH` 和 `LITELLM_API_KEY` 变量进行配置，而不是 `OPENAI_*` 那些变量。
:::

##### 配置参数

| 参数 | 必需 | 描述 |
|-----------|----------|-------------|
| `OPENAI_API_KEY` | 是 | 用于 API 的认证 key |
| `OPENAI_HOST` | 否 | 自定义端点 URL（默认为 api.openai.com） |
| `OPENAI_BASE_PATH` | 否 | 追加到 host 后面的请求路径（默认为 `v1/chat/completions`）。当你的端点在不同的路径上提供 chat completions API 时设置此项——大多数代理期望 `v1/chat/completions`，但有些挂载在 `chat/completions`（没有 `v1`）。 |
| `OPENAI_ORGANIZATION` | 否 | 用于用量跟踪和治理的组织 ID |
| `OPENAI_PROJECT` | 否 | 用于资源管理的项目标识符 |
| `OPENAI_CUSTOM_HEADERS` | 否 | 要包含在请求中的额外请求头。可以通过环境变量、配置文件或 CLI 设置，格式为 `HEADER_A=VALUE_A,HEADER_B=VALUE_B`。 |
| `OPENAI_STORE` | 否 | 是否持久化生成的 Responses API 响应以便稍后通过 API 检索。默认为 `false`。 |

##### 示例配置

<Tabs groupId="deployment">
  <TabItem value="vllm" label="vLLM 自托管" default>
    如果你使用 vLLM 并启用 OpenAI 兼容来运行 LLaMA 或其他模型：
```sh
OPENAI_HOST=https://your-vllm-endpoint.internal
OPENAI_API_KEY=your-internal-api-key
```
  </TabItem>
  <TabItem value="kserve" label="KServe 部署">
    对于使用 KServe 部署在 Kubernetes 上的模型：
```sh
OPENAI_HOST=https://kserve-gateway.your-cluster
OPENAI_API_KEY=your-kserve-api-key
OPENAI_ORGANIZATION=your-org-id
OPENAI_PROJECT=ml-serving
```
  </TabItem>
  <TabItem value="enterprise" label="企业版 OpenAI">
    对于带治理的企业 OpenAI 部署：
```sh
OPENAI_API_KEY=your-api-key
OPENAI_ORGANIZATION=org-id123
OPENAI_PROJECT=compliance-approved
```
  </TabItem>
  <TabItem value="custom-headers" label="自定义请求头">
    对于需要自定义请求头的 OpenAI 兼容端点：
```sh
OPENAI_API_KEY=your-api-key
OPENAI_ORGANIZATION=org-id123
OPENAI_PROJECT=compliance-approved
OPENAI_CUSTOM_HEADERS="X-Header-A=abc,X-Header-B=def"
```
  </TabItem>
</Tabs>

##### 设置说明

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏
    2. 点击侧边栏上的 `Settings` 按钮
    3. 点击 `Models` 标签页
    4. 点击 `Configure providers`
    5. 在提供方列表中点击 `OpenAI`
    6. 填写你的配置细节：
       - API Key（必需）
       - Host URL（用于自定义端点）
       - Organization ID（用于用量跟踪）
       - Project（用于资源管理）
    7. 点击 `Submit`
  </TabItem>
  <TabItem value="cli" label="goose CLI">
    1. 运行 `goose configure`
    2. 选择 `Configure Providers`
    3. 选择 `OpenAI` 作为提供方
    4. 在提示时输入你的配置：
       - API key
       - Host URL（如果使用自定义端点）
       - Organization ID（如果使用组织跟踪）
       - Project identifier（如果使用项目管理）
  </TabItem>
</Tabs>

:::tip 企业部署
对于企业部署，你可以使用环境变量或配置文件预配置这些值，以确保整个组织内一致的治理。
:::

### 配置自定义提供方

创建自定义提供方以连接[尚未支持](#available-providers)的服务，或自定义你连接它们的方式。自定义提供方会出现在 goose 的提供方列表中，可以像任何其他提供方一样被选择。

**优点：**
- **多个端点**：在不同服务之间切换（例如 vLLM、企业代理、OpenAI）
- **预配置模型**：存储一个首选模型列表
- **可共享配置**：JSON 文件可以跨团队共享或检入代码仓库
- **自定义命名**：在 UI 中显示「Corporate API」而不是「OpenAI」
- **独立凭证**：为每个提供方分配自己的 API key

自定义提供方必须使用 OpenAI、Anthropic 或 Ollama 兼容的 API 格式。它们可以包含用于额外认证、API key、令牌或租户标识符的自定义请求头。每个自定义提供方映射到一个 JSON 配置文件。

**添加自定义提供方：**
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏
    2. 点击侧边栏上的 `Settings` 按钮
    3. 点击 `Models` 标签页
    4. 点击 `Configure providers`
    5. 点击窗口底部的 `Add Custom Provider`
    6. 填写提供方细节：
       - **Provider Type**：
         - `OpenAI Compatible`（最常见）
         - `Anthropic Compatible`
         - `Ollama Compatible`
       - **Display Name**：提供方的一个友好名称
       - **API URL**：API 端点的基 URL
       - **Authentication**：
         - **API Key**：API key，通过自定义环境变量访问，并存储在钥匙串中（如果钥匙串被禁用或无法访问，则存储在 `secrets.yaml` 中）
            - 对于不需要授权的提供方（例如 Ollama、vLLM 或内部 API 等本地模型），取消勾选 **"This provider requires an API key"** 复选框
       - **Available Models**：可用模型名的逗号分隔列表
       - **Streaming Support**：API 是否支持流式响应（点击切换）
    7. 点击 `Create Provider`

    :::info 自定义请求头
    目前，无法在 goose Desktop 中定义自定义请求头。作为一种变通方法，请在创建后编辑提供方配置文件。
    :::

  </TabItem>
  <TabItem value="cli" label="goose CLI">
    1. 在你的终端中运行以下命令：

```sh
goose configure
```

    2. 选择 `Custom Providers`。使用方向键（↑/↓）在选项中移动。

```sh
┌   goose-configure
│
◆  What would you like to configure?
│  ○ Configure Providers
// highlight-start
│  ● Custom Providers (Add custom provider with compatible API)
// highlight-end
│  ○ Add Extension
│  ○ Toggle Extensions
│  ○ Remove Extension
│  ○ goose Settings
└
```

    3. 选择 `Add A Custom Provider`

```sh
┌   goose-configure
│
◇  What would you like to configure?
│  Custom Providers
│
◆  What would you like to do?
// highlight-start
│  ● Add A Custom Provider (Add a new OpenAI/Anthropic/Ollama compatible Provider)
// highlight-end
│  ○ Remove Custom Provider
└
```

    4. 按照提示输入提供方细节：
       - **API Type**：
         - `OpenAI Compatible`（最常见）
         - `Anthropic Compatible`
         - `Ollama Compatible`
       - **Name**：提供方的一个友好名称
       - **API URL**：API 端点的基 URL
       - **Authentication Required**：如果你的提供方需要 API key，回答「Yes」；如果不需要认证，回答「No」
         - 如果选 Yes：选择 goose 应如何获取凭证：
           - **Static API key**：系统会提示你输入 **API Key**（安全地存储在钥匙串中；如果钥匙串被禁用或无法访问，则存储在 `secrets.yaml` 中）
           - **Command (refreshable)**：系统会提示你输入一个 **command**（以及可选参数），goose 运行它来获取凭证，还会提示一个以秒为单位的 **refresh interval**。用于由 IdP 或密钥保管库签发的短期凭证，这样 goose 可以自动刷新它们，而不必在它们过期时要求重启。见下方的[基于命令的认证](#command-based-authentication)。
         - 如果选 No：会跳过 API key 提示
       - **Available Models**：可用模型名的逗号分隔列表
       - **Streaming Support**：API 是否支持流式响应
       - **Custom Headers**：任何额外的请求头名称和值

    :::info 自定义请求头
    目前，在 CLI 中只能为 OpenAI 兼容提供方定义自定义请求头。对于 Anthropic 或 Ollama 兼容提供方，请在创建后编辑提供方配置文件。
    :::

  </TabItem>
  <TabItem value="config" label="配置文件">

    首先在 `custom_providers` 目录中创建一个 JSON 文件：
    - macOS/Linux：`~/.config/goose/custom_providers/`
    - Windows：`%APPDATA%\Block\goose\config\custom_providers\`

    示例 `custom_corp_api.json` 配置文件：
```json
{
  "name": "custom_corp_api",
  "engine": "openai",
  "display_name": "Corporate API",
  "description": "Custom Corporate API provider",
  "api_key_env": "CUSTOM_CORP_API_API_KEY",
  "base_url": "https://api.company.com/v1/chat/completions",
  "models": [
    {
      "name": "gpt-4o",
      "context_limit": 128000
    },
    {
      "name": "gpt-3.5-turbo",
      "context_limit": 16385
    }
  ],
  "headers": {
    "x-origin-client-id": "YOUR_CLIENT_ID",
    "x-origin-secret": "YOUR_SECRET_VALUE"
  },
  "supports_streaming": true,
  "requires_auth": true
}
```

    然后使用 `api_key_env` 为你的会话设置 key。例如：
```bash
export CUSTOM_CORP_API_API_KEY="your-api-key"
goose session start --provider custom_corp_api
```

    :::tip 钥匙串中的 key 存储
    如果你想将 API key 存储在 `goose` 钥匙串中，请在 goose Desktop 中更新提供方并输入该 key。这会提供安全、持久的存储，并允许 goose 原生连接到该提供方。
    :::

  </TabItem>
</Tabs>

#### 基于命令的认证

自定义提供方可以配置为运行一个命令来获取其凭证，而不是使用静态的 `api_key_env`。这对于由 IdP 或密钥保管库签发的短期凭证很有用：当凭证过期时，goose 会重新运行该命令来刷新凭证，而不要求重启。

在提供方的 JSON 配置中添加一个 `auth` 对象来替代 `api_key_env`（二者互斥）：

```json
{
  "name": "custom_corp_api",
  "engine": "openai",
  "display_name": "Corporate API",
  "base_url": "https://api.company.com/v1/chat/completions",
  "models": [{ "name": "gpt-4o", "context_limit": 128000 }],
  "requires_auth": true,
  "auth": {
    "command": "/path/to/get-token.sh",
    "args": [],
    "refresh_interval": 3600,
    "timeout_seconds": 10
  }
}
```

- **`command`**：要运行的可执行文件。它会被直接启动，不经过 shell——`command`/`args` 都不会进行 shell 插值。如果你的脚本需要 shell 特性（管道、变量展开），请显式调用解释器，例如 `"command": "/bin/bash", "args": ["-c", "..."]`。裸名称（无路径分隔符，例如 `"get-token"`）会在 `PATH` 上查找；相对路径（例如 `"./scripts/get-token.sh"`）会相对于 `cwd` 解析。
- **`args`**（可选）：传递给 `command` 的参数。
- **`refresh_interval`**（可选，默认为 `3600`）：获取到的凭证在被缓存多久（以秒为单位）之后重新运行命令。设为 `0` 可完全禁用主动刷新——此后该命令仅在提供方 API 因认证错误拒绝请求之后被动地重新运行。
- **`timeout_seconds`**（可选，默认为 `10`）：在将命令视为失败之前等待的时长。
- **`cwd`**（可选）：命令的工作目录，也是相对 `command` 路径解析所依据的基准。默认为 goose 的当前目录。

命令去除首尾空白后的标准输出被用作凭证。它必须成功退出并打印非空值；失败时，goose 会报错，而不是静默地复用过期凭证。该命令会继承 goose 的完整环境，因为配置 goose 和编写脚本的是同一个用户。

<Tabs groupId="interface">
  <TabItem value="cli" label="goose CLI" default>

    在 `goose configure` 中，当被问及如何为自定义提供方获取凭证时，选择 **Command (refreshable)**（见[上文](#configure-custom-provider)）。

  </TabItem>
  <TabItem value="config" label="配置文件">

    将上面所示的 `auth` 对象添加到提供方的 JSON 文件中，而不是设置 `api_key_env`。

  </TabItem>
</Tabs>

**更新自定义提供方：**

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏
    2. 点击侧边栏上的 `Settings` 按钮
    3. 点击 `Models` 标签页
    4. 点击 `Configure providers`
    5. 在列表中点击你的自定义提供方
    6. 更新你想更改的字段
    7. 点击 `Update Provider`

  </TabItem>
  <TabItem value="cli" label="goose CLI">

    1. 在你的终端中运行以下命令：

```sh
goose configure
```

    2. 从菜单中选择 `Configure Providers` 并按 `Enter`。

```sh
┌   goose-configure
│
◆  What would you like to configure?
// highlight-start
│  ● Configure Providers (Change provider or update credentials)
// highlight-end
│  ○ Custom Providers
│  ○ Add Extension
│  ○ Toggle Extensions
│  ○ Remove Extension
│  ○ goose Settings
└
```

    3. 选择你想更新的自定义提供方并按 `Enter`。使用方向键（↑/↓）在选项中移动，或开始输入以筛选列表。

```sh
┌   goose-configure
│
◇  What would you like to configure?
│  Configure Providers
│
◆  Which model provider should we use?
│  ○ Amazon Bedrock
│  ○ Amazon SageMaker TGI
│  ○ Anthropic
│  ○ Azure OpenAI
│  ○ Claude Code CLI
// highlight-start
│  ● Corporate API (Custom Corporate API provider)
// highlight-end
│  ○ Cursor Agent
│  ○ ...
└
```

    4. 按照提示更新字段。

  </TabItem>
  <TabItem value="config" label="配置文件">

    在 `custom_providers` 目录中打开自定义提供方配置文件：
    - macOS/Linux：`~/.config/goose/custom_providers/`
    - Windows：`%APPDATA%\Block\goose\config\custom_providers\`

    更新你想更改的字段并保存你的更改。
  </TabItem>
</Tabs>

你的更改会在你的下一个 goose 会话中生效。

**移除自定义提供方：**

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏
    2. 点击侧边栏上的 `Settings` 按钮
    3. 点击 `Models` 标签页
    4. 点击 `Configure providers`
    5. 在列表中点击你的自定义提供方
    6. 点击 `Delete Provider`
    7. 点击 `Confirm Delete` 确认你想永久移除该自定义提供方及其存储的 API key（如适用）

  </TabItem>
  <TabItem value="cli" label="goose CLI">

    1. 在你的终端中运行以下命令：

```sh
goose configure
```

    2. 选择 `Custom Providers`。使用方向键（↑/↓）在选项中移动。

```sh
┌   goose-configure
│
◆  What would you like to configure?
│  ○ Configure Providers
// highlight-start
│  ● Custom Providers (Add custom provider with compatible API)
// highlight-end
│  ○ Add Extension
│  ○ Toggle Extensions
│  ○ Remove Extension
│  ○ goose Settings
└
```

    3. 选择 `Remove Custom Provider`。

```sh
┌   goose-configure
│
◇  What would you like to configure?
│  Custom Providers
│
◆  What would you like to do?
│  ○ Add A Custom Provider
// highlight-start
│  ● Remove Custom Provider (Remove an existing custom provider)
// highlight-end
└
```

    4. 选择你想移除的自定义提供方。

    提供方配置文件会从 `custom_providers` 目录中移除，key 会从钥匙串中移除。

  </TabItem>
  <TabItem value="config" label="配置文件">

    :::tip
    如果提供方的 API key 存储在钥匙串中，请使用 goose CLI 来移除自定义提供方。这也会移除存储的 API key。
    :::

    删除 `custom_providers` 目录中的自定义提供方配置文件：
    - macOS/Linux：`~/.config/goose/custom_providers/`
    - Windows：`%APPDATA%\Block\goose\config\custom_providers\`

  </TabItem>
</Tabs>

### 免费使用 goose

goose 是一个免费开源的 AI 代理，你可以立即开始使用，但并非所有受支持的 [LLM 提供方][providers]都提供免费额度。

下面，我们列出几个免费选项以及如何开始使用它们。

:::warning 限制
这些免费选项是开始使用 goose 并探索其能力的好方法。不过，为了获得更好的性能，你可能需要升级你的 LLM。
:::


#### Groq
Groq 免费提供对开源（开放权重）模型的高速推理访问。要在 goose 中使用 Groq，你需要一个来自 [Groq Console](https://console.groq.com/keys) 的 API key。

Groq 提供多个支持工具调用的开源模型，包括：
- **moonshotai/kimi-k2-instruct-0905** - 具有 1 万亿参数的混合专家模型，针对代理智能和工具使用优化
- **qwen/qwen3-32b** - 具有高级推理和多语言能力的 328 亿参数模型
- **llama-3.3-70b-versatile** - Meta 的 Llama 3.3 模型，适用于多种应用
- **llama-3.1-8b-instant** - Meta 的 Llama 3.1 模型，用于快速推理

受支持的 Groq 模型完整列表见 [groq.json](https://github.com/aaif-goose/goose/blob/main/crates/goose-providers/src/declarative/definitions/groq.json)。

要在 goose 中设置 Groq，请按以下步骤操作：

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  **更新你的 LLM 提供方和 API key：**

    1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏。
    2. 点击侧边栏上的 `Settings` 按钮。
    3. 点击 `Models` 标签页。
    4. 点击 `Configure Providers`
    5. 从列表中选择 `Groq` 作为提供方。
    6. 点击 `Configure`，输入你的 API key，然后点击 `Submit`。
    7. 选择你想要的 Groq 模型。

  </TabItem>
  <TabItem value="cli" label="goose CLI">
    1. 运行：
```sh
goose configure
```
    2. 从菜单中选择 `Configure Providers`。
    3. 按照提示选择 `Groq` 作为提供方。
    4. 在提示时输入你的 API key。
    5. 选择你想要的 Groq 模型。
  </TabItem>
</Tabs>

#### EmpirioLabs AI
[EmpirioLabs AI](https://empiriolabs.ai/) 通过一个兼容 OpenAI 且支持流式传输的 API 提供对前沿的开源与专有聊天模型的访问。要在 goose 中使用 EmpirioLabs，你需要一个来自 [EmpirioLabs](https://platform.empiriolabs.ai/dashboard/api-keys) 的 API key。

EmpirioLabs 提供支持工具调用的模型，包括：
- **qwen3-7-plus** - Qwen3.7 Plus，具有 1M 上下文窗口
- **qwen3-7-max** - Qwen3.7 Max，具有 1M 上下文窗口
- **deepseek-v4-pro** - DeepSeek V4 Pro，具有 1M 上下文窗口
- **deepseek-v4-flash** - DeepSeek V4 Flash，具有 1M 上下文窗口
- **glm-5-1** - GLM-5.1，具有 202K 上下文窗口
- **kimi-k2-7-code** - Kimi K2.7 Code，具有 256K 上下文窗口
- **minimax-m3** - MiniMax M3，具有 524K 上下文窗口

完整的实时目录见 `https://api.empiriolabs.ai/v1/models`。goose 中配置的 EmpirioLabs 模型完整列表见 [empiriolabs.json](https://github.com/aaif-goose/goose/blob/main/crates/goose-providers/src/declarative/definitions/empiriolabs.json)。更多细节见 [EmpirioLabs 文档](https://docs.empiriolabs.ai)。

要在 goose 中设置 EmpirioLabs，请按以下步骤操作：

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  **更新你的 LLM 提供方和 API key：**

    1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏。
    2. 点击侧边栏上的 `Settings` 按钮。
    3. 点击 `Models` 标签页。
    4. 点击 `Configure Providers`
    5. 从列表中选择 `EmpirioLabs AI` 作为提供方。
    6. 点击 `Configure`，输入你的 API key，然后点击 `Submit`。
    7. 选择你想要的 EmpirioLabs 模型。

  </TabItem>
  <TabItem value="cli" label="goose CLI">
    1. 运行：
```sh
goose configure
```
    2. 从菜单中选择 `Configure Providers`。
    3. 按照提示选择 `EmpirioLabs AI` 作为提供方。
    4. 在提示时输入你的 API key。
    5. 选择你想要的 EmpirioLabs 模型。
  </TabItem>
</Tabs>

#### FuturMix
[FuturMix](https://futurmix.ai/) 是一个统一的 AI 网关，通过兼容 OpenAI 的 API 提供对来自 Anthropic、Google、OpenAI 和 DeepSeek 的模型的访问。要在 goose 中使用 FuturMix，你需要一个来自 [FuturMix](https://futurmix.ai/) 的 API key。

FuturMix 提供支持工具调用的模型，包括：
- **claude-sonnet-4-20250514** - Anthropic Claude Sonnet 4，具有 200K 上下文
- **gpt-4o** - OpenAI GPT-4o，具有 128K 上下文
- **gemini-2.5-pro** - Google Gemini 2.5 Pro，具有 1M 上下文
- **deepseek-chat** - DeepSeek V3，具有 131K 上下文
- **claude-haiku-4-20250514** - Anthropic Claude Haiku 4，具有 200K 上下文

受支持的 FuturMix 模型完整列表见 [futurmix.json](https://github.com/aaif-goose/goose/blob/main/crates/goose-providers/src/declarative/definitions/futurmix.json)。

要在 goose 中设置 FuturMix，请按以下步骤操作：

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  **更新你的 LLM 提供方和 API key：**

    1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏。
    2. 点击侧边栏上的 `Settings` 按钮。
    3. 点击 `Models` 标签页。
    4. 点击 `Configure Providers`
    5. 从列表中选择 `FuturMix` 作为提供方。
    6. 点击 `Configure`，输入你的 API key，然后点击 `Submit`。
    7. 选择你想要的 FuturMix 模型。

  </TabItem>
  <TabItem value="cli" label="goose CLI">
    1. 运行：
```sh
goose configure
```
    2. 从菜单中选择 `Configure Providers`。
    3. 按照提示选择 `FuturMix` 作为提供方。
    4. 在提示时输入你的 API key。
    5. 选择你想要的 FuturMix 模型。
  </TabItem>
</Tabs>

#### Novita AI
[Novita AI](https://novita.ai/) 通过兼容 OpenAI 的 API 以有竞争力的价格提供对 90+ 开源模型的访问。要在 goose 中使用 Novita AI，你需要一个来自 [Novita AI](https://novita.ai/settings#key-management) 的 API key。

Novita AI 提供许多支持工具调用的模型，包括：
- **moonshotai/kimi-k2.5** - Moonshot 的最新模型，具有 262K 上下文窗口
- **minimax/minimax-m2.7** - MiniMax M2.7，具有 205K 上下文
- **zai-org/glm-5.1** - 智谱的 GLM-5.1，具有 205K 上下文
- **deepseek/deepseek-v3.2** - DeepSeek V3.2，具有 164K 上下文
- **google/gemma-4-31b-it** - Google Gemma 4 31B，具有 262K 上下文

受支持的 Novita AI 模型完整列表见 [novita.json](https://github.com/aaif-goose/goose/blob/main/crates/goose-providers/src/declarative/definitions/novita.json)。

要在 goose 中设置 Novita AI，请按以下步骤操作：

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  **更新你的 LLM 提供方和 API key：**

    1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏。
    2. 点击侧边栏上的 `Settings` 按钮。
    3. 点击 `Models` 标签页。
    4. 点击 `Configure Providers`
    5. 从列表中选择 `Novita AI` 作为提供方。
    6. 点击 `Configure`，输入你的 API key，然后点击 `Submit`。
    7. 选择你想要的 Novita AI 模型。

  </TabItem>
  <TabItem value="cli" label="goose CLI">
    1. 运行：
```sh
goose configure
```
    2. 从菜单中选择 `Configure Providers`。
    3. 按照提示选择 `Novita AI` 作为提供方。
    4. 在提示时输入你的 API key。
    5. 选择你想要的 Novita AI 模型。
  </TabItem>
</Tabs>

#### Routstr
[Routstr](https://routstr.com/) 是一个兼容 OpenAI 的聚合器，将数十个上游提供方汇聚在单个 API 之后。支付由 Routstr 实例本身处理，因此 goose 只需要该实例签发给你的 `sk-...` bearer。要在 goose 中使用 Routstr，请选择一个实例（默认为 `https://api.routstr.com`）并从其支付流程中获取 API key。

Routstr 聚合来自许多上游提供方的模型，包括：
- **claude-opus-4.7** — Anthropic 的 Claude opus 4.7
- **deepseek-v4-pro** — DeepSeek V4 Pro
- **gemini-3.1-pro-preview** — gemini-3.1 Pro Preview

`/v1/models` 会在配置时查询，因此你的 Routstr 实例暴露的完整目录都会在模型选择器中可用。goose 随附的静态默认值见 [routstr.json](https://github.com/aaif-goose/goose/blob/main/crates/goose-providers/src/declarative/definitions/routstr.json)。

要在 goose 中设置 Routstr，请按以下步骤操作：

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  **更新你的 LLM 提供方和 API key：**

    1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏。
    2. 点击侧边栏上的 `Settings` 按钮。
    3. 点击 `Models` 标签页。
    4. 点击 `Configure Providers`
    5. 从列表中选择 `Routstr` 作为提供方。
    6. 点击 `Configure`，输入你的 `ROUTSTR_API_KEY`（可选地覆盖 `ROUTSTR_HOST` 以指向不同的 Routstr 实例），然后点击 `Submit`。
    7. 选择你想要的 Routstr 模型。

  </TabItem>
  <TabItem value="cli" label="goose CLI">
    1. 运行：
```sh
goose configure
```
    2. 从菜单中选择 `Configure Providers`。
    3. 按照提示选择 `Routstr` 作为提供方。
    4. 在提示时输入你的 API key（可选地覆盖 `ROUTSTR_HOST`）。
    5. 选择你想要的 Routstr 模型。
  </TabItem>
</Tabs>

#### SayGM
[SayGM](https://saygm.com/) 通过兼容 OpenAI 的 API 提供 TEE 支持的私有推理。模型路由和价格在每次请求时于运行时确定。要在 goose 中使用 SayGM，你需要一个来自 [SayGM](https://saygm.com/) 的 API key。

SayGM 支持许多模型，包括：
- **Qwen/Qwen3-235B-A22B-Thinking-2507-TEE** — Qwen3 235B 思考模型（TEE 支持）
- **deepseek-ai/DeepSeek-V3.2-TEE** — DeepSeek V3.2（TEE 支持）
- **moonshotai/Kimi-K3-TEE** — Kimi K3（TEE 支持）
- **zai-org/GLM-5.2-TEE** — GLM-5.2（TEE 支持）

`/v1/models` 会在配置时查询，因此 SayGM 暴露的完整目录都会在模型选择器中可用。

要在 goose 中设置 SayGM，请按以下步骤操作：

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  **更新你的 LLM 提供方和 API key：**

    1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏。
    2. 点击侧边栏上的 `Settings` 按钮。
    3. 点击 `Models` 标签页。
    4. 点击 `Configure Providers`
    5. 从列表中选择 `SayGM` 作为提供方。
    6. 点击 `Configure`，输入你的 API key，然后点击 `Submit`。
    7. 选择你想要的 SayGM 模型。

  </TabItem>
  <TabItem value="cli" label="goose CLI">
    1. 运行：
```sh
goose configure
```
    2. 从菜单中选择 `Configure Providers`。
    3. 按照提示选择 `SayGM` 作为提供方。
    4. 在提示时输入你的 API key。
    5. 选择你想要的 SayGM 模型。
  </TabItem>
</Tabs>

#### Google Gemini
Google Gemini 提供免费额度。要开始配合 goose 使用 Gemini API，你需要一个来自 [Google AI studio](https://aistudio.google.com/app/apikey) 的 API Key。

要在 goose 中设置 Google Gemini，请按以下步骤操作：

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  **更新你的 LLM 提供方和 API key：**

    1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏。
    2. 点击侧边栏上的 `Settings` 按钮。
    3. 点击 `Models` 标签页。
    4. 点击 `Configure Providers`
    5. 从列表中选择 `Google Gemini` 作为提供方。
    6. 点击 `Configure`，输入你的 API key，然后点击 `Submit`。

  </TabItem>
  <TabItem value="cli" label="goose CLI">
    1. 运行：
```sh
goose configure
```
    2. 从菜单中选择 `Configure Providers`。
    3. 按照提示选择 `Google Gemini` 作为提供方。
    4. 在提示时输入你的 API key。
    5. 输入你想要的 Gemini 模型。

```
┌   goose-configure
│
◇ What would you like to configure?
│ Configure Providers
│
◇ Which model provider should we use?
│ Google Gemini
│
◇ Provider Google Gemini requires GOOGLE_API_KEY, please enter a value
│▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
│
◇ Enter a model from that provider:
│ gemini-2.0-flash-exp
│
◇ Hello! You're all set and ready to go, feel free to ask me anything!
│
└ Configuration saved successfully
```
  </TabItem>
</Tabs>


#### 本地 LLM

goose 是一个本地 AI 代理，通过使用本地 LLM，你可以保持数据私密、完全掌控自己的环境，并完全离线工作，无需依赖云端访问。不过请注意，本地 LLM 需要稍多一点设置，才能与 goose 一起使用。

:::warning 对不支持工具调用的模型的支持有限
goose 大量使用工具调用，因此不支持工具调用的模型只能做聊天补全。如果使用不支持工具调用的模型，所有 goose [扩展必须被禁用](https://block.github.io/goose/docs/getting-started/using-extensions#enablingdisabling-extensions)。
:::

以下是我们支持的一些本地提供方：

<Tabs groupId="local-llms">
  <TabItem value="ollama" label="Ollama" default>
    <Tabs groupId="ollama-models">
      <TabItem value="ramalala" label="Ramalala">
        1. [下载 Ramalama](https://github.com/containers/ramalama?tab=readme-ov-file#install)。
        2. 在终端中，运行任意一个[支持工具调用的 Ollama 模型](https://ollama.com/search?c=tools)或 [GGUF 格式的 HuggingFace 模型](https://huggingface.co/search/full-text?q=%22tools+support%22+%2B+%22gguf%22&type=model)：

          `--runtime-args="--jinja"` 标志是 Ramalama 与 goose Ollama 提供方配合工作所必需的。

          示例：

```sh
ramalama serve --runtime-args="--jinja" ollama://qwen2.5
```

          3. 在另一个终端窗口中，用 goose 进行配置：

```sh
goose configure
```

          4. 选择 `Configure Providers`

```
┌   goose-configure
│
◆  What would you like to configure?
│  ● Configure Providers (Change provider or update credentials)
│  ○ Toggle Extensions
│  ○ Add Extension
└
```

          5. 选择 `Ollama` 作为模型提供方，因为 Ramalama 在 API 上兼容，可以使用 goose 的 Ollama 提供方

```
┌   goose-configure
│
◇  What would you like to configure?
│  Configure Providers
│
◆  Which model provider should we use?
│  ○ Anthropic
│  ○ Databricks
│  ○ Google Gemini
│  ○ Groq
│  ● Ollama (Local open source models)
│  ○ OpenAI
│  ○ OpenRouter
└
```

          6. 输入你的模型所运行的 host

          :::info 端点
          对于 Ollama 提供方，如果你不提供 host，我们会把它设置为 `localhost:11434`。在构造 URL 时，如果 scheme 不是 `http` 或 `https`，我们会前置 `http://`。由于 Ramalama 默认提供服务所用的端口是 8080，我们设置 `OLLAMA_HOST=http://0.0.0.0:8080`
          :::

```
┌   goose-configure
│
◇  What would you like to configure?
│  Configure Providers
│
◇  Which model provider should we use?
│  Ollama
│
◆  Provider Ollama requires OLLAMA_HOST, please enter a value
│  http://0.0.0.0:8080
└
```


          7. 输入你正在运行的模型

```
┌   goose-configure
│
◇  What would you like to configure?
│  Configure Providers
│
◇  Which model provider should we use?
│  Ollama
│
◇  Provider Ollama requires OLLAMA_HOST, please enter a value
│  http://0.0.0.0:8080
│
◇  Enter a model from that provider:
│  qwen2.5
│
◇  Welcome! You're all set to explore and utilize my capabilities. Let's get started on solving your problems together!
│
└  Configuration saved successfully
```

          :::tip 上下文长度
          如果你注意到 goose 在使用扩展时遇到问题，或者忽略了 [.goosehints](https://block.github.io/goose/docs/guides/context-engineering/using-goosehints)，很可能是该模型默认的 2048 token 上下文长度太低了。使用 `ramalama serve` 将 `--ctx-size, -c` 选项设置为一个[更高的值](https://github.com/containers/ramalama/blob/main/docs/ramalama-serve.1.md#--ctx-size--c)。
          :::

      </TabItem>
      <TabItem value="deepseek" label="DeepSeek-R1">
        原生的 `DeepSeek-r1` 模型不支持工具调用，不过我们有一个可以配合 goose 使用的[自定义模型](https://ollama.com/michaelneale/deepseek-r1-goose)。

        :::warning
        注意，这是一个 70B 大小的模型，需要强大的设备才能流畅运行。
        :::


        1. [下载 Ollama](https://ollama.com/download)。
        2. 在终端窗口中，运行以下命令来安装自定义的 DeepSeek-r1 模型：

```sh
ollama run michaelneale/deepseek-r1-goose
```

        3. 在另一个终端窗口中，用 goose 进行配置：

```sh
goose configure
```

        4. 选择 `Configure Providers`

```
┌   goose-configure
│
◆  What would you like to configure?
│  ● Configure Providers (Change provider or update credentials)
│  ○ Toggle Extensions
│  ○ Add Extension
└
```

        5. 选择 `Ollama` 作为模型提供方

```
┌   goose-configure
│
◇  What would you like to configure?
│  Configure Providers
│
◆  Which model provider should we use?
│  ○ Anthropic
│  ○ Databricks
│  ○ Google Gemini
│  ○ Groq
│  ● Ollama (Local open source models)
│  ○ OpenAI
│  ○ OpenRouter
└
```

        6. 输入你的模型所运行的 host

```
┌   goose-configure
│
◇  What would you like to configure?
│  Configure Providers
│
◇  Which model provider should we use?
│  Ollama
│
◆  Provider Ollama requires OLLAMA_HOST, please enter a value
│  http://localhost:11434
└
```

        7. 输入上面安装的模型

```
┌   goose-configure
│
◇  What would you like to configure?
│  Configure Providers
│
◇  Which model provider should we use?
│  Ollama
│
◇   Provider Ollama requires OLLAMA_HOST, please enter a value
│  http://localhost:11434
│
◇  Enter a model from that provider:
│  michaelneale/deepseek-r1-goose
│
◇  Welcome! You're all set to explore and utilize my capabilities. Let's get started on solving your problems together!
│
└  Configuration saved successfully
```
      </TabItem>
      <TabItem value="others" label="其他模型" default>
        1. [下载 Ollama](https://ollama.com/download)。
        2. 在终端中，运行任意一个[支持工具调用的模型](https://ollama.com/search?c=tools)

          示例：

```sh
ollama run qwen2.5
```

        3. 在另一个终端窗口中，用 goose 进行配置：

```sh
goose configure
```

        4. 选择 `Configure Providers`

```
┌   goose-configure
│
◆  What would you like to configure?
│  ● Configure Providers (Change provider or update credentials)
│  ○ Toggle Extensions
│  ○ Add Extension
└
```

        5. 选择 `Ollama` 作为模型提供方

```
┌   goose-configure
│
◇  What would you like to configure?
│  Configure Providers
│
◆  Which model provider should we use?
│  ○ Anthropic
│  ○ Databricks
│  ○ Google Gemini
│  ○ Groq
│  ● Ollama (Local open source models)
│  ○ OpenAI
│  ○ OpenRouter
└
```

        6. 输入你的模型所运行的 host

        :::info 端点
        对于 Ollama，如果你不提供 host，我们会把它设置为 `localhost:11434`。
        在构造 URL 时，如果 scheme 不是 `http` 或 `https`，我们会前置 `http://`。
        如果你在不同的服务器上运行 Ollama，你必须设置 `OLLAMA_HOST=http://{host}:{port}`。
        对于 ollama.com 上的托管模型，请改用 **Ollama Cloud** 提供方。
        :::

```
┌   goose-configure
│
◇  What would you like to configure?
│  Configure Providers
│
◇  Which model provider should we use?
│  Ollama
│
◆  Provider Ollama requires OLLAMA_HOST, please enter a value
│  http://localhost:11434
└
```


        7. 输入你正在运行的模型

```
┌   goose-configure
│
◇  What would you like to configure?
│  Configure Providers
│
◇  Which model provider should we use?
│  Ollama
│
◇  Provider Ollama requires OLLAMA_HOST, please enter a value
│  http://localhost:11434
│
◇  Enter a model from that provider:
│  qwen2.5
│
◇  Welcome! You're all set to explore and utilize my capabilities. Let's get started on solving your problems together!
│
└  Configuration saved successfully
```

        :::tip 上下文长度
        如果你注意到 goose 在使用扩展时遇到问题，或者忽略了 [.goosehints](https://block.github.io/goose/docs/guides/context-engineering/using-goosehints)，很可能是该模型默认的 4096 token 上下文长度太低了。将 `OLLAMA_CONTEXT_LENGTH` 环境变量设置为一个[更高的值](https://github.com/ollama/ollama/blob/main/docs/faq.mdx#how-can-i-specify-the-context-window-size)。
        :::

      </TabItem>
    </Tabs>
  </TabItem>
  <TabItem value="lmstudio" label="LM Studio">
    [LM Studio](https://lmstudio.ai/) 让你通过一个兼容 OpenAI 的 API 服务器在本地运行开源模型。

    1. 下载并安装 LM Studio。
    2. 打开 LM Studio 并下载一个支持工具调用的模型（例如 Qwen、Llama 或 Mistral 变体）。
    3. 在 LM Studio 中启动本地服务器。该服务器默认运行在 `http://localhost:1234`

    4. 配置 goose 使用 LM Studio：

    <Tabs groupId="interface">
      <TabItem value="ui" label="goose Desktop" default>
        1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏。
        2. 点击侧边栏上的 `Settings` 按钮。
        3. 点击 `Models` 标签页。
        4. 点击 `Configure providers`。
        5. 从提供方列表中选择 `LM Studio` 并点击 `Configure`。
        6. 点击 `Submit`（不需要 API key）。
        7. 选择你在 LM Studio 中加载的模型。
      </TabItem>
      <TabItem value="cli" label="goose CLI">
        1. 运行：
```sh
goose configure
```
        2. 从菜单中选择 `Configure Providers`。
        3. 选择 `LM Studio` 作为提供方。
        4. 输入与 LM Studio 中加载的模型相匹配的模型名。

```
┌   goose-configure
│
◇  What would you like to configure?
│  Configure Providers
│
◇  Which model provider should we use?
│  LM Studio
│
◇  Enter a model from that provider:
│  qwen2.5-7b-instruct
│
└  Configuration saved successfully
```
      </TabItem>
    </Tabs>

    :::tip 模型名
    请确保你在 goose 中输入的模型名与 LM Studio 服务器面板中显示的模型标识符相匹配。
    :::
  </TabItem>
  <TabItem value="atomic-chat" label="Atomic Chat">
    [Atomic Chat](https://github.com/AtomicBot-ai/Atomic-Chat) 让你通过一个兼容 OpenAI 的 API 服务器在本地运行开源模型。

    1. 从 [atomic.chat](https://atomic.chat/) 或 [GitHub Releases](https://github.com/AtomicBot-ai/Atomic-Chat/releases) 下载并安装 Atomic Chat。
    2. 打开 Atomic Chat 并下载一个支持工具调用的模型（例如 Qwen、Llama 或 Mistral 变体）。
    3. 在 Atomic Chat 中启动本地服务器。该服务器默认运行在 `http://localhost:1337`

    4. 配置 goose 使用 Atomic Chat：

    <Tabs groupId="interface">
      <TabItem value="ui" label="goose Desktop" default>
        1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮打开侧边栏。
        2. 点击侧边栏上的 `Settings` 按钮。
        3. 点击 `Models` 标签页。
        4. 点击 `Configure providers`。
        5. 从提供方列表中选择 `Atomic Chat` 并点击 `Configure`。
        6. 点击 `Submit`（不需要 API key）。
        7. 选择你在 Atomic Chat 中加载的模型。
      </TabItem>
      <TabItem value="cli" label="goose CLI">
        1. 运行：
```sh
goose configure
```
        2. 从菜单中选择 `Configure Providers`。
        3. 选择 `Atomic Chat` 作为提供方。
        4. 输入与 Atomic Chat 中加载的模型相匹配的模型名。

```
┌   goose-configure
│
◇  What would you like to configure?
│  Configure Providers
│
◇  Which model provider should we use?
│  Atomic Chat
│
◇  Enter a model from that provider:
│  qwen2.5-7b-instruct
│
└  Configuration saved successfully
```
      </TabItem>
    </Tabs>

    :::tip 模型名
    请确保你在 goose 中输入的模型名与 Atomic Chat 中为你的服务器显示的模型标识符相匹配。如果 API 监听的 origin 不是 `http://localhost:1337`，请在 goose 中设置 `ATOMIC_CHAT_HOST` 与之匹配（仅包含 scheme、host 和 port）。
    :::
  </TabItem>
  <TabItem value="docker" label="Docker Model Runner" default>
    1. [获取 Docker](https://docs.docker.com/get-started/get-docker/)
    2. [启用 Docker Model Runner](https://docs.docker.com/ai/model-runner/#enable-dmr-in-docker-desktop)
    3. [拉取一个模型](https://docs.docker.com/ai/model-runner/#pull-a-model)，例如从 Docker Hub [AI 命名空间](https://hub.docker.com/u/ai)、[Unsloth](https://hub.docker.com/u/unsloth)或[从 HuggingFace](https://www.docker.com/blog/docker-model-runner-on-hugging-face/)拉取

    示例：

```sh
docker model pull hf.co/unsloth/gemma-3n-e4b-it-gguf:q6_k
```

    4. 配置 goose 使用 Docker Model Runner，使用 OpenAI API 兼容端点：

```sh
goose configure
```

    5. 选择 `Configure Providers`

```
┌   goose-configure
│
◆  What would you like to configure?
│  ● Configure Providers (Change provider or update credentials)
│  ○ Toggle Extensions
│  ○ Add Extension
└
```

    6. 选择 `OpenAI` 作为模型提供方：

```
┌   goose-configure
│
◇  What would you like to configure?
│  Configure Providers
│
◆  Which model provider should we use?
│  ○ Anthropic
│  ○ Amazon Bedrock
│  ○ Claude Code
│  ● OpenAI (GPT-4 and other OpenAI models, including OpenAI compatible ones)
│  ○ OpenRouter
```

    7. 将 Docker Model Runner 端点配置为 `OPENAI_HOST`：

```
┌   goose-configure
│
◇  What would you like to configure?
│  Configure Providers
│
◇  Which model provider should we use?
│  OpenAI
│
◆  Provider OpenAI requires OPENAI_HOST, please enter a value
│  https://api.openai.com (default)
└
```

    Docker Model Runner 在 host 侧端口的默认值是 12434，因此 `OPENAI_HOST` 的值可以是：
    `http://localhost:12434`。

    8. 配置 base path：

```
◆  Provider OpenAI requires OPENAI_BASE_PATH, please enter a value
│  v1/chat/completions (default)
└
```

    Docker model runner 使用 `/engines/llama.cpp/v1/chat/completions` 作为 base path。

    9. 最后配置 Docker Model Runner 中可用的模型以供 goose 使用：`hf.co/unsloth/gemma-3n-e4b-it-gguf:q6_k`

```
│
◇  Enter a model from that provider:
│  gpt-4o
│
◒  Checking your configuration...
└  Configuration saved successfully
```
  </TabItem>
</Tabs>



### OpenRouter 高级参数

OpenRouter 接受提供方特定的请求参数，例如 `verbosity`、`reasoning`、`plugins`、`require_parameters` 以及其他受支持的字段。在你的 `config.yaml` 中设置 `OPENROUTER_PARAMETERS`，即可将这些字段添加到每个 OpenRouter chat completion 请求中。

你可以使用 YAML 对象：

```yaml
OPENROUTER_PARAMETERS:
  verbosity: xhigh
  reasoning:
    effort: high
  plugins:
    - id: web
```

或者 JSON 字符串：

```yaml
OPENROUTER_PARAMETERS: '{"verbosity":"xhigh","plugins":[{"id":"web"}]}'
```

goose 会忽略它已经管理的保留请求字段，例如 `model`、`messages`、`stream` 和 `stream_options`。其他 OpenRouter 特定的顶层字段会通过共享的 OpenAI 兼容请求参数处理逻辑传递。

### GitHub Copilot 认证

GitHub Copilot 使用设备流进行认证，因此不需要 API key：

1. 运行 [`goose configure`](#configure-provider-and-model) 并选择 **GitHub Copilot**
2. 一个八字符的代码会自动复制到你的剪贴板
3. 浏览器会打开到 GitHub 的设备激活页面
4. 粘贴该代码以授权该应用
5. 当你返回 goose 时，GitHub Copilot 会在 CLI 和 Desktop 中作为提供方可用。

### Azure OpenAI 认证

goose 支持 Azure OpenAI 的三种认证方法：

1. **Entra ID Bearer Token** - 使用从 `AZURE_OPENAI_AD_TOKEN` 预先获取的 Microsoft Entra 访问令牌，以 `Authorization: Bearer <token>` 发送。goose 完全跳过 Azure CLI 和令牌获取，这适合只有短期令牌暴露给运行时的企业部署（例如通过 `az account get-access-token --resource https://cognitiveservices.azure.com --query accessToken --output tsv` 获取）
2. **API Key Authentication** - 使用 `AZURE_OPENAI_API_KEY` 进行直接认证
3. **Azure Credential Chain** - 自动使用 Azure CLI 凭证，不需要 API key

当配置了不止一个时，`AZURE_OPENAI_AD_TOKEN` 优先于 `AZURE_OPENAI_API_KEY`，后者优先于凭证链。

要使用 Azure 凭证链：
- 确保你已使用 `az login` 登录
- 拥有 Azure OpenAI 服务的适当 Azure 角色分配
- 使用 `goose configure` 进行配置并选择 Azure OpenAI，将 API key 字段留空

此方法简化了认证并增强了企业环境的安全性。

### 多模型配置

除了单模型设置之外，goose 还支持[多模型配置](https://block.github.io/goose/docs/guides/multi-model/)，可以为专门任务使用不同的模型和提供方：

- **子代理** - 将限定范围的任务委派给隔离的会话，以保持你的主工作流专注高效

### Meta Muse Spark 推理强度

Meta 的 Muse Spark 模型支持可配置的推理强度，它映射到 Meta 的 `reasoning_effort` 请求参数：
- **Low** - 更快的响应，更轻量的推理
- **Medium** - 平衡的推理深度与延迟
- **High** - 更深入的推理，更高的延迟
- **Max** - 作为 `xhigh` 发送，这是 Meta 支持的最深推理等级

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    在选择 Muse Spark 模型时，会自动出现一个「Thinking Effort」下拉菜单。选择你的偏好，该设置会跨会话持续保留。
  </TabItem>

  <TabItem value="cli" label="goose CLI">
    当你运行 `goose configure` 并选择一个 Muse Spark 模型时，会提示你选择一个思考强度：

```
◆  Select thinking effort:
│  ● Off - No extended thinking
│  ○ Low - Better latency, lighter reasoning
│  ○ Medium - Moderate thinking
│  ○ High - Deep reasoning
│  ○ Max - No constraints on thinking depth
```

    你也可以使用 `GOOSE_THINKING_EFFORT` 环境变量全局设置它（`off`、`low`、`medium`、`high` 或 `max`）。
  </TabItem>
</Tabs>

:::note
Muse Spark 总是进行推理，无法禁用它，因此选择 `off` 会被限制为 `low`（Meta 支持的最轻等级），而不是省略 `reasoning_effort` 参数。
:::

### Gemini 3 思考等级

Gemini 3 模型支持可配置的思考等级，以平衡响应延迟与推理深度：
- **Low**（默认）- 更快的响应，更轻量的推理
- **High** - 更深入的推理，更高的延迟

:::tip
当思考被启用时，你可以查看模型的推理过程。详见[查看模型推理](#viewing-model-reasoning)。
:::

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    在选择 Gemini 3 模型时，会自动出现一个「Thinking Level」下拉菜单。选择你的偏好，该设置会跨会话持续保留。
  </TabItem>

  <TabItem value="cli" label="goose CLI">
    **交互式配置：**

    当你运行 `goose configure` 并选择一个 Gemini 3 模型时，会提示你选择一个思考等级：

```
◆  Select thinking level for Gemini 3:
│  ● Low - Better latency, lighter reasoning
│  ○ High - Deeper reasoning, higher latency
```
  </TabItem>
</Tabs>

:::info 优先级顺序
思考等级按以下顺序确定（从最高到最低优先级）：
1. 模型配置中的 `request_params.thinking_level`
2. `GEMINI3_THINKING_LEVEL` 环境变量
3. 默认值：`low`
:::

### 查看模型推理

有些模型会将其内部推理或「思维链」作为响应的一部分暴露出来。goose 会自动捕获这些推理输出并提供给你。以下模型和提供方支持推理输出：

| 提供方 / 模型 | 工作原理 |
|---|---|
| **DeepSeek-R1**（通过 OpenAI、Ollama、OpenRouter、OVHcloud 等） | 从 API 响应中的 `reasoning_content` 字段捕获推理内容 |
| **Kimi**（通过 Groq 或其他 OpenAI 兼容端点） | 从 API 响应中的 `reasoning_content` 字段捕获推理内容 |
| **Gemini CLI**（启用思考的 Google Gemini 模型） | 从流式响应中捕获思考块 |
| **Claude**（Anthropic，启用 [Claude thinking](https://block.github.io/goose/docs/guides/environment-variables#claude-thinking-configuration)） | 从 API 响应中捕获思考块 |

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
    推理输出会自动出现在模型响应上方一个可折叠的 **「Show reasoning」** 切换项中。点击它即可展开并查看模型的思考过程。
  </TabItem>

  <TabItem value="cli" label="goose CLI">
    推理输出在 CLI 中**默认隐藏**。要显示它，请设置 `GOOSE_CLI_SHOW_THINKING` 环境变量：

```bash
export GOOSE_CLI_SHOW_THINKING=1
```

    启用后，推理会以暗淡的文字出现在模型主响应之前的一个「Thinking:」标题下。

    :::note
    这要求 stdout 是一个终端（当把输出通过管道传给文件或另一个命令时，推理输出不会出现）。
    :::
  </TabItem>
</Tabs>

:::tip
推理输出对于理解模型如何得出答案、调试意外行为或从模型的问题解决思路中学习都很有用。不过，它也可能很冗长——只在需要时开启它。
:::

---

如果你对某个特定提供方有任何疑问或需要帮助，欢迎在 [Discord](https://discord.gg/n8R5VaWDAn) 或 [goose 仓库](https://github.com/aaif-goose/goose)上联系我们。


[providers]: https://block.github.io/goose/docs/getting-started/providers
[function-calling-leaderboard]: https://gorilla.cs.berkeley.edu/leaderboard.html
