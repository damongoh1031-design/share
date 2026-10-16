# goose 官方文档中文手册：第 26 章　博客（四）：2025-08

## MCP Jupyter：AI 驱动的机器学习与数据科学

> 原文：https://block.github.io/goose/blog/2025-08-04-mcp-jupyter-server

![MCP Jupyter Server](https://block.github.io/goose/img/data-goose.png)

机器学习和数据科学工作流本质上是迭代式的。你加载数据、探索模式、构建模型，并基于结果改进你的方法。但传统 AI 助手会在交互之间丢失上下文，迫使你反复重新加载数据、重建上下文——让数据密集型的开发变得缓慢而昂贵。

[**MCP Jupyter Server**](https://github.com/block/mcp-jupyter) 通过让 Goose 这样的 AI 智能体直接与你的 Jupyter notebook 协作来解决这个问题：它在多次交互之间维持持久记忆与状态，同时让 AI 通过代码执行而非原始数据传输来与你的数据交互。

<!--truncate-->

<iframe class="aspect-ratio" src="https://www.youtube.com/embed/0i6gB_mWaRM" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### 记忆与上下文问题

传统 AI 编程助手面临一个根本性限制：它们会在交互之间丢失上下文。这在一定程度上源于它们的设计目标——完成描述清晰的单个任务，比如重构一段代码、编译并运行其测试、把结果提交到版本控制。相比之下，数据科学工作流往往是开放式的，需要大量探索与交互。这为在数据密集型的 ML 工作流中使用 AI 带来了若干挑战：

- **不断重新加载数据**：每次交互都需要重新加载或描述你的数据集
- **迭代成本高昂**：大型数据集反复处理既慢又贵
- **上下文大小**：原始数据可能太大，无法塞进上下文
- **并非为交互式工作而设计**：让助手完成一些步骤后再把控制权交回人类（反之亦然）比较困难

为应对这些挑战，我们创建了 MCP Jupyter Server。

### 更好的方法：持久状态

MCP Jupyter Server 采取了不同的思路。它不在交互之间丢失上下文，而是维持持久记忆，并让 AI 通过执行 Jupyter 代码单元来与你的数据交互。这造就了一个强大的范式：

- **持久记忆**：变量和状态在多次交互之间得以保持
- **高效迭代**：无需重新加载数据或重建上下文
- **基于代码的数据交互**：AI 通过执行来探索数据，而不是把原始数据塞进上下文
- **真正的结对编程**：在同一个 notebook 上下文中无缝协作

### 变革 ML 工作流

#### 探索性数据分析

不必再描述你的数据集，而是让 AI 直接探索它：

> <span style={{color: '#2563eb', fontWeight: 'bold'}}>用户：</span>「帮我理解一下这个客户数据集」
> 
> <span style={{color: '#059669', fontWeight: 'bold'}}>AI：</span>「我先来探索一下你的数据结构」
> 
> *<span style={{color: '#6b7280', fontStyle: 'italic'}}>[AI 执行：df.info()、df.describe()、df.head()]</span>*
> 
> <span style={{color: '#059669', fontWeight: 'bold'}}>AI：</span>「我看到你有 50,000 名客户、12 个特征。数据包含人口统计信息（age、income）、行为指标（purchase_frequency、avg_order_value），以及 'phone_number' 列中的一些缺失值。要不要我为关键关系（比如年龄与收入、或购买模式）创建可视化？」
> 
> <span style={{color: '#2563eb', fontWeight: 'bold'}}>用户：</span>「好，给我看年龄和收入的分布，以及任何相关性」
> 
> <span style={{color: '#059669', fontWeight: 'bold'}}>AI：</span>「好！我会为 age 和 income 创建直方图，再加一个相关性热力图」
> 
> *<span style={{color: '#6b7280', fontStyle: 'italic'}}>[AI 生成并显示可视化]</span>*

AI 能看到你实际的列名、数据类型和分布——从而给出相关性高得多的建议。

#### 交互式模型开发

AI 成为你建模过程中真正的协作者：

> <span style={{color: '#2563eb', fontWeight: 'bold'}}>用户：</span>「这个模型表现不太好」
> 
> <span style={{color: '#059669', fontWeight: 'bold'}}>AI：</span>「我来检查一下当前的指标和特征重要性」
> 
> *<span style={{color: '#6b7280', fontStyle: 'italic'}}>[AI 执行你现有的模型评估代码]</span>*
> 
> <span style={{color: '#059669', fontWeight: 'bold'}}>AI：</span>「我看到准确率是 72%，最重要的特征是 'price' 和 'location'。模型似乎过拟合了——要不要我试试正则化或减少特征集？」
> 
> <span style={{color: '#2563eb', fontWeight: 'bold'}}>用户：</span>「先试试正则化」
> 
> <span style={{color: '#059669', fontWeight: 'bold'}}>AI：</span>「我会加入 L2 正则化，并测试不同的 alpha 值」
> 
> *<span style={{color: '#6b7280', fontStyle: 'italic'}}>[AI 迭代地实现并测试改动]</span>*
> 
> <span style={{color: '#059669', fontWeight: 'bold'}}>AI：</span>「很好！当 alpha=0.1 时，准确率提升到了 78%，验证曲线也好看多了。要我继续调参，还是试试集成方法？」

#### 实时调试

当出现错误时，助手拥有完整上下文：

> <span style={{color: '#2563eb', fontWeight: 'bold'}}>用户：</span>「我在第 5 个单元遇到了 KeyError」
> 
> <span style={{color: '#059669', fontWeight: 'bold'}}>AI：</span>「我来看看你的 dataframe 里有哪些列」
> 
> *<span style={{color: '#6b7280', fontStyle: 'italic'}}>[AI 执行：df.columns、df.info()]</span>*
> 
> <span style={{color: '#059669', fontWeight: 'bold'}}>AI：</span>「我看到问题了——你试图访问 'customer_id'，但实际的列名是带大写字母的 'CustomerID'。另外，我注意到你的 'purchase_date' 是字符串——要不要我在修复 KeyError 的同时把它转换成 datetime？」
> 
> <span style={{color: '#2563eb', fontWeight: 'bold'}}>用户：</span>「好，两个问题都修」
> 
> <span style={{color: '#059669', fontWeight: 'bold'}}>AI：</span>「搞定！我已经更新了列引用，并把 purchase_date 转换成了 datetime。这个单元现在应该能正常运行了。」

#### 持续协作

想象这样一个场景：你正在处理一个新的数据集：

> <span style={{color: '#2563eb', fontWeight: 'bold'}}>用户：</span> *<span style={{color: '#6b7280', fontStyle: 'italic'}}>[执行：df = pd.read_csv('sales_data.csv')]</span>*
> 
> <span style={{color: '#2563eb', fontWeight: 'bold'}}>用户：</span>「我来检查一下数据类型，看看有没有异常」
> 
> <span style={{color: '#059669', fontWeight: 'bold'}}>AI：</span>「我来分析你的销售数据结构」
> 
> *<span style={{color: '#6b7280', fontStyle: 'italic'}}>[AI 执行：df.info()、df.describe(include='all')]</span>*
> 
> <span style={{color: '#059669', fontWeight: 'bold'}}>AI：</span>「我发现几个问题：'CustomerID' 存成了文本，但它应该是数值；另外 'SalesAmount' 中有 847 个缺失值。要不要我把 'CustomerID' 转成数值，并用中位数填充缺失的 'SalesAmount'？」
> 
> <span style={{color: '#2563eb', fontWeight: 'bold'}}>用户：</span>「好，请照做，然后给我看更新后的信息」
> 
> <span style={{color: '#059669', fontWeight: 'bold'}}>AI：</span>「搞定！CustomerID 现在是数值，SalesAmount 的空缺也填好了。你的数据集已经干净，可以开始建模了。」

*<span style={{color: '#6b7280', fontStyle: 'italic'}}>[会话稍后，在你训练完一个模型之后……]</span>*

> <span style={{color: '#2563eb', fontWeight: 'bold'}}>用户：</span>「我的模型表现如何？」
> 
> <span style={{color: '#059669', fontWeight: 'bold'}}>AI：</span>「我来为你训练好的模型生成关键指标」
> 
> *<span style={{color: '#6b7280', fontStyle: 'italic'}}>[AI 访问现有的模型变量并生成评估指标]</span>*
> 
> <span style={{color: '#059669', fontWeight: 'bold'}}>AI：</span>「你的 Random Forest 达到了 0.84 的精确率和 0.81 的召回率。混淆矩阵显示在高价值销售类别中有一些误报。要不要我调整决策阈值，或者试试特征工程？」

这种流畅的一来一回——助手理解并在现有 notebook 状态之上继续构建——让无缝协作成为可能，无需不断重建上下文或重新加载数据。

### 示例 notebook

这里你可以看到一个由 MCP Jupyter Server 处理的示例 notebook。该服务器

**[📓 查看完整的演示 Notebook](https://github.com/block/mcp-jupyter/blob/main/demos/demo.ipynb)**

该演示走查了一个典型的数据科学工作流：
- **安装缺失的库**：为 notebook 安装缺失的库
- **数据生成**：创建用于分析的合成数据
- **模型训练**：用 scikit-learn 拟合一个线性回归模型
- **结果分析**：提取模型系数和性能指标
- **可视化**：用 seaborn 创建图表

### 快速开始

MCP Jupyter Server 能无缝集成到现有工作流中，也可以配合基于 VS Code 的 IDE 中的 notebook 查看器使用。

有关详细的安装与配置，请查看[完整文档](https://aaif-goose.github.io/mcp-jupyter/)。


<head>
  <meta property="og:title" content="MCP Jupyter Server: Bringing Notebook Intelligence to AI Agents" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/06/24/mcp-jupyter-server" />
  <meta property="og:description" content="A powerful MCP server that enables AI agents to interact with Jupyter notebooks while preserving kernel state and variable context" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/data-goose-7fc60ab0a13a9e9b6c22172d6ac166ab.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="MCP Jupyter Server: Bringing Notebook Intelligence to AI Agents" />
  <meta property="twitter:description" content="A powerful MCP server that enables AI agents to interact with Jupyter notebooks while preserving kernel state and variable context" />
  <meta name="twitter:image" content="https://goose-docs.ai/assets/images/data-goose-7fc60ab0a13a9e9b6c22172d6ac166ab.png" />
</head>

---

## 7 个 AI 智能体如何在一小时内协作构建出一个应用

> 原文：https://block.github.io/goose/blog/2025-08-10-vibe-coding-with-goose-building-apps-with-ai-agents

![blog cover](https://block.github.io/goose/img/header-image.png)

如果我告诉你，你可以只用 AI 智能体、在一小时内构建出一个完整可运行的 Web 应用呢？不是简单的「Hello World」应用，而是一个全栈应用，包含后端 API、响应式前端、单元测试和文档？

这正是我们在 [Berkeley 智能体 AI 峰会](https://www.youtube.com/live/_w5m3h9jY-w?t=5310)的 Vibe Coding 工作坊中做到的事。我在那里演示了如何使用 Goose 的子代理编排（subagent orchestration）来拉起一整支由 AI 智能体组成的开发团队。每个智能体承担特定角色——从产品规划到 QA 测试——并协作构建出「AI BriefMe」，一个可以为任意主题生成高管风格简报的 Web 应用。

<!-- truncate -->

### 多智能体开发的力量

传统 AI 编程助手很擅长帮你编写单个函数或调试具体问题。但如果你需要从零构建某个东西呢？如果你想模拟整个软件开发生命周期呢？

这正是 Goose 的子代理功能大放异彩的地方。你不必事必躬亲，而是可以编排一支由专业 AI 智能体组成的团队，每个都有自己的专长：

- 🧠 **Planner（规划者）**——定义产品愿景和 MVP 范围
- 📋 **Project Manager（项目经理）**——拆解任务并协调执行
- 🏗️ **Architect（架构师）**——搭建项目结构和技术栈
- 🎨 **Frontend Developer（前端开发者）**——构建界面
- 🧩 **Backend Developer（后端开发者）**——构建 API 逻辑
- 🧪 **QA Engineer（QA 工程师）**——编写测试并识别生产阻断项
- 📝 **Tech Writer（技术写作者）**——撰写安装、用法和 API 文档

### 工作坊体验

在直播工作坊中，参与者跟随我们一步步构建 AI BriefMe。这种方式的美妙之处在于，你不只是在看别人写代码，而是在学习如何有效地提示（prompt）和编排 AI 智能体。

下面是整个工作流的展开过程：

#### 第 1 步：产品规划

首先，我们拉起一个 Planner 智能体来定义我们要构建的东西。Planner 没有一头扎进代码，而是先创建了一份清晰的产品定义：

<details>
<summary>产品计划</summary>

```md
# AI BriefMe MVP - 40-Minute Build Plan

## Goals
Build a functional web app that generates daily briefings on any topic in **40 minutes**. Users input a topic and get an instant, well-formatted briefing.

## Core MVP Features (Must-Have)
1. **Simple web interface** with topic input field and generate button
2. **AI-powered briefing generation** that returns:
   - Title
   - Today's date
   - 2-3 bullet-point takeaways
   - Optional code snippet or chart for technical topics
3. **Clean display** of the generated briefing
4. **Basic error handling** for API failures

## Technical Stack (Keep It Simple)
- **Frontend**: Single HTML page with vanilla JS (no frameworks)
- **Backend**: Python Flask app with single endpoint
- **AI**: Headless Goose as an LLM service
- **Deployment**: Local development server (no cloud deployment)

## Team Responsibilities

### PM
- Define exact briefing format and user flow
- Create sample topics for testing

### Architect  
- Design simple API contract between frontend/backend
- Choose AI prompt structure for consistent output

### Frontend Dev
- Build single-page interface with form and results display
- Handle loading states and basic error messages

### Backend Dev
- Create Flask app with `/generate-briefing` endpoint
- Integrate with AI API and format response
- Add basic input validation

### QA
- Test with 3-5 different topic types
- Verify error handling works
- Check output format consistency

### Tech Writer
- Write brief README with setup instructions
- Document the API endpoint

## Design Considerations
- **Mobile-friendly** but desktop-first
- **Fast response time** - show loading indicator
- **Copy-friendly output** - users should be able to easily copy/share
- **Graceful failures** - clear error messages when AI is unavailable

## Success Criteria
✅ User can enter any topic and get a formatted briefing  
✅ App handles both technical and non-technical topics  
✅ Clean, readable output format  
✅ Works locally without deployment complexity  

## Out of Scope (Save for Later)
- User accounts or login
- Email delivery or scheduling  
- Historical briefings or dashboard
- Advanced formatting or customization
- Mobile app or PWA features
- Analytics or usage tracking

---
**Timeline**: 40 minutes total  
**Demo ready**: Functional app running locally with 2-3 example briefings generated
```
</details>


#### 第 2 步：项目管理

接下来，Project Manager 智能体把工作拆解成具体任务，并识别出哪些可以并行、哪些必须串行。

<details>
<summary>项目看板</summary>

```md
# AI BriefMe - Project Board

## Sprint Overview
**Duration**: 40 minutes  
**Goal**: Functional MVP with topic input → AI briefing generation → display

---

## 🏗️ ARCHITECT (Start First - 5 minutes)
**Dependencies**: None - blocks all other dev work

### Tasks:
- [ ] **API Contract Design** (3 min)
  - Define `/generate-briefing` POST endpoint structure
  - Specify request/response JSON format
  - Document error response codes
- [ ] **AI Prompt Template** (2 min)
  - Create consistent prompt structure for briefing generation
  - Define output format requirements (title, date, bullets, optional code)

**Deliverables**: `api_spec.md` with endpoint docs and prompt template

---

## 🔧 BACKEND DEV (After Architect - 15 minutes)
**Dependencies**: API contract from Architect

### Tasks:
- [ ] **Flask App Setup** (3 min)
  - Create `app.py` with basic Flask structure
  - Add CORS for frontend integration
- [ ] **Generate Briefing Endpoint** (8 min)
  - Implement `/generate-briefing` POST route
  - Format AI response to match API contract
- [ ] **Error Handling** (2 min)
  - Add try/catch for API failures
  - Return appropriate error responses
- [ ] **Basic Validation** (2 min)
  - Validate topic input (not empty, reasonable length)
  - Sanitize input before sending to AI

**Deliverables**: Working Flask backend ready for frontend integration

---

## 🎨 FRONTEND DEV (Parallel with Backend - 15 minutes)
**Dependencies**: API contract from Architect (can start with mock data)

### Tasks:
- [ ] **HTML Structure** (3 min)
  - Create `index.html` with form and results sections
  - Add basic semantic structure
- [ ] **CSS Styling** (5 min)
  - Style input form and results display
  - Add loading spinner/state
  - Make mobile-friendly
- [ ] **JavaScript Logic** (5 min)
  - Handle form submission
  - Make API call to backend
  - Display results and handle loading states
- [ ] **Error UI** (2 min)
  - Show user-friendly error messages
  - Handle network failures gracefully

**Deliverables**: Complete frontend ready to connect to backend

---

## 🧪 QA (After Backend + Frontend Ready - 8 minutes)
**Dependencies**: Working backend and frontend integration

### Tasks:
- [ ] **Happy Path Testing** (3 min)
  - Test 3 different topic types: business, technical, general
  - Verify output format consistency
- [ ] **Error Scenarios** (3 min)
  - Test empty input, very long input
  - Test with backend down/API key issues
  - Verify error messages display correctly
- [ ] **Cross-browser Check** (2 min)
  - Quick test in Chrome and Safari
  - Verify mobile responsiveness

**Deliverables**: Bug report and sign-off for demo readiness

---

## 📝 TECH WRITER (Parallel with Development - 10 minutes)
**Dependencies**: API spec from Architect, can work in parallel

### Tasks:
- [ ] **README Creation** (5 min)
  - Setup instructions for local development
  - Required dependencies and API keys
  - How to run the application
- [ ] **API Documentation** (3 min)
  - Document the `/generate-briefing` endpoint
  - Include request/response examples
- [ ] **Sample Topics List** (2 min)
  - Create 5-10 example topics for demo
  - Mix of technical and non-technical subjects

**Deliverables**: `README.md`, `API.md`, and `sample_topics.md`

---

## 📋 PM COORDINATION TASKS
**Ongoing throughout sprint**

### Tasks:
- [ ] **Define Exact Briefing Format** (2 min)
  - Specify title format, bullet structure
  - Decide on code snippet criteria
- [ ] **Create Test Topics** (3 min)
  - Prepare demo scenarios
  - Include edge cases for QA
- [ ] **Integration Coordination** (5 min)
  - Ensure frontend/backend connection works
  - Coordinate final testing and demo prep

---

## ⏱️ TIMELINE & DEPENDENCIES

### Phase 1 (0-5 min): Foundation
- **Architect**: API design and prompt template
- **Tech Writer**: Start README and documentation

### Phase 2 (5-20 min): Parallel Development  
- **Backend Dev**: Build Flask app and endpoint
- **Frontend Dev**: Build UI (can use mock data initially)
- **Tech Writer**: Continue documentation

### Phase 3 (20-32 min): Integration & Testing
- **Frontend/Backend**: Connect and test integration
- **QA**: Begin testing as soon as integration works
- **PM**: Coordinate final pieces

### Phase 4 (32-40 min): Final Polish & Demo Prep
- **All**: Bug fixes and demo preparation
- **QA**: Final sign-off
- **PM**: Demo script and presentation

---

## 🎯 CRITICAL PATH
1. Architect completes API spec → Backend can start
2. Backend completes endpoint → Frontend integration can happen  
3. Frontend + Backend working → QA can test
4. QA passes → Demo ready

## ⚠️ RISK MITIGATION
- **Integration Problems**: Frontend dev should test with mock data first
- **Time Overruns**: Cut optional features (code snippets, advanced styling) if needed
```

</details>


#### 第 3 步：技术架构

Architect 智能体确立了技术基础：

- **技术栈**：原生 HTML/CSS/JS 前端，Express.js 后端
- **API 设计**：一个简单的 POST 端点，接受 `{"topic": "string"}`
- **文件结构**：组织良好的项目，关注点清晰分离
- **依赖**：Express、CORS，以及用于调用 Headless Goose 的 child_process

Architect 还定义了 API 契约，这使得下一步前端与后端开发者智能体可以并行工作。

#### 第 4 步：并行开发

这里开始变得非常有意思。我们同时拉起两个开发者智能体：

**Frontend Developer** 创建了：
- 干净、响应式的界面，使用现代 CSS
- 带加载状态的表单处理
- 错误处理和用户反馈
- 复制到剪贴板功能

**Backend Developer** 实现了：
- 带完善错误处理的 Express 服务器
- `/api/briefing` 端点，使用 Headless Goose 进行 AI 生成
- 响应解析和 JSON 格式化
- 超时处理和 CORS 配置

##### Headless Goose 的魔力

这个项目最酷的一点，是后端如何通过以编程方式调用 Goose 来使用 [Headless Goose](https://block.github.io/goose/docs/tutorials/headless-goose) 生成 AI 简报：

```javascript
const gooseProcess = spawn('goose', [
  'run', '-t', prompt, 
  '--quiet', '--no-session', '--max-turns', '1'
]);
```

这创造了一个迷人的递归场景：我们在用 Goose 构建一个使用 Goose 生成内容的应用。这是一路往下都是 AI 智能体！

#### 第 5 步：测试与文档

最后，我们并行运行了 QA 和 Tech Writer 智能体：

**QA Engineer** 交付了：
- 使用 Jest 编写的全面单元测试套件
- 模拟外部依赖，确保测试可靠
- 对生产就绪阻断项的详细分析
- 安全与性能建议

**Tech Writer** 产出了：
- 含安装说明的完整 README
- 带示例的 API 文档
- 故障排查指南
- 用法示例与最佳实践

### 实时得到的真实结果

到这一小时结束时，参与者拥有了一个功能完备的 Web 应用。最终产品交付了这些：

- **干净的 UI**：专业外观的界面，在桌面和移动端都能用
- **AI 驱动的内容**：生成带有标题、日期和关键要点的结构化简报
- **代码示例**：对技术类主题，附带相关代码片段
- **生产洞察**：QA 分析揭示了部署前需要关注的若干具体领域
- **完整文档**：运行、修改和扩展该应用所需的一切

但重要的是：这并不是生产就绪的代码。QA 智能体对此说得很清楚，标记了安全、性能和可扩展性问题。

<details>
<summary>QA 分析要点</summary>

```md
  ## 🔍 QA Analysis Highlights

  ### Critical Issues Identified
  - **Security**: Command injection risk, no authentication, missing rate limiting
  - **Performance**: Blocking operations, memory leaks, inefficient parsing
  - **Scalability**: Single-threaded bottleneck, no horizontal scaling support

  ### Risk Assessment
  - **Overall Risk Level**: HIGH ⚠️
  - **Production Readiness**: Not recommended without addressing critical issues
  - **Timeline for Production**: 2-3 weeks for P0 items, 4-6 weeks for full readiness

  ### Testing Quality Assessment
  - **Test Coverage**: Excellent (91%+ across all metrics)
  - **Edge Case Handling**: Comprehensive
  - **Error Scenarios**: Well covered
  - **Resilience Testing**: Implemented
```

</details>

### 人类依然重要

这个工作坊完美地展示了 AI 辅助开发的当前状态。Goose 及其子代理绝对可以加速原型开发，帮你快速构建出可运行的应用。但人类开发者仍然掌握着关键判断：

- **架构决策**：这是解决该问题的正确方法吗？
- **安全考量**：我们需要缓解哪些风险？
- **生产就绪度**：在真实用户上手之前，哪些地方需要加固？
- **业务逻辑**：这真的解决了用户的问题吗？

### 开发的未来

我们在这个工作坊中演示的东西，暗示了软件开发一个迷人的未来：我们或许会发现自己正在编排 AI 智能体团队。重要的技能变成了：

- **提示词工程**：你如何向 AI 智能体清晰地传达需求？
- **系统设计**：你如何把复杂问题拆解成适合智能体处理的任务？
- **质量保证**：你如何验证和测试 AI 生成的代码？
- **集成**：你如何把多个智能体的产出组合成协调一致的解决方案？

### 开始使用子代理

想自己试一试吗？你需要这些：

1. **安装并配置 Goose**：按照[快速入门指南](https://goose-docs.ai/docs/quickstart)操作
2. **从小处着手**：先尝试构建一个简单的应用，熟悉工作流

:::note
从 1.10.0 版本起，子代理不再处于实验阶段，也无需启用任何特性开关。
:::

[完整的工作坊材料](https://gist.github.com/angiejones/60ff19c08c5a3992e42adc8de3e96309)可供获取，包含分步说明和速查提示词。

关键在于学会如何有效地提示。每个智能体都需要关于其角色、约束和交付物的清晰指令。

请记住，这是关于原型开发和探索，而非生产部署。用它快速验证想法、创建演示或学习新技术。然后用人类判断来决定哪些值得打磨成生产级软件。

---

*想看看实际效果吗？查看完整的工作坊视频，看我们现场构建 AI BriefMe：*

<iframe class="aspect-ratio" src="https://www.youtube.com/embed/_w5m3h9jY-w?start=5310" title="Vibe Coding with Goose Workshop" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

<head>
  <meta property="og:title" content="How 7 AI Agents Worked Together to Build an App in One Hour" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/08/10/vibe-coding-with-goose-building-apps-with-ai-agents" />
  <meta property="og:description" content="Learn how to build a full-stack AI app in under an hour using Goose's multi-agent orchestration, from planning to QA testing." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/header-image-b685ea475ff7b8ae3563317b347fddb0.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta name="twitter:title" content="How 7 AI Agents Worked Together to Build an App in One Hour" />
  <meta name="twitter:description" content="Learn how to build a full-stack AI app in under an hour using Goose's multi-agent orchestration, from planning to QA testing." />
  <meta name="twitter:image" content="https://goose-docs.ai/assets/images/header-image-b685ea475ff7b8ae3563317b347fddb0.png" />
</head>

---

## LLM 组队：谁规划，谁执行？

> 原文：https://block.github.io/goose/blog/2025-08-11-llm-tag-team-lead-worker-model

:::danger 已过时
Lead/Worker 模式已从 goose 中移除，取代它的 Planning Mode 也已被移除。当前的工作流请参见[多模型指南](https://block.github.io/goose/docs/guides/multi-model/)。
:::

![blog cover](https://block.github.io/goose/img/header-image.png)

有没有想过，让两个 AI 模型像组队接力一样协作会发生什么？这正是我们在最近一次直播中测试的内容——让 Goose 的 Lead/Worker 模型在一个真实项目上工作。剧透一下：效果其实相当不错。

Lead/Worker 模型就是那种听起来简单、但在实践中能带来惊艳收益的特性。把它想象成一位项目经理和一位开发者完美协作——一个做战略思考，另一个撸起袖子做实际实现。

<!-- truncate -->

### 这个 Lead/Worker 到底是怎么回事？

Lead/Worker 不是让一个 LLM 包办一切，而是让你分摊负载。你的 lead 模型负责思考、决策和大局规划，而 worker 模型专注于执行——写代码、运行命令、把计划变成现实。神奇之处在于平衡：你可以把一个更强大（有时也更贵）的模型放在 lead 位，让一个更快、更省钱的模型承担繁重的工作。

人们喜欢的流行模型搭配：

  - GPT-4 + Claude Sonnet – 均衡的智能与效率。
  - Claude Opus + GPT-3.5 – 创造性规划搭配快速执行。
  - GPT-4o + 本地模型 – 以隐私为先的构建，数据留在内部。

### 为什么你会喜欢这套配置

- 💰 成本优化
用更便宜的模型做执行，同时把高端模型留给战略规划。你的钱包会感谢你。

- ⚡ 速度提升
从强大的模型得到扎实的计划，然后让优化过的执行模型飞速完成实现。

- 🔄 混合搭配提供方
这才是真正酷的地方——你可以用 Claude 做推理、用 OpenAI 做执行，或者任何适合你工作流的组合。

- 🏃‍♂️ 应对漫长的开发会话
非常适合那种需要持续性能又不想烧钱的马拉松式编码会话。

### 配置方法

上手 Lead/Worker 模型出乎意料地简单。在 Goose 桌面应用中，你只需要：

1. **启用该特性**——在设置里找到启用按钮
2. **选择你的 lead 模型**——挑一个强大的做规划（比如 GPT-4）
3. **选择你的 worker 模型**——选一个高效的做执行（比如 Claude Sonnet）
4. **配置行为**——设置 worker 在咨询 lead 之前可以跑多少轮

默认设置对大多数人来说都很好用，但你可以自定义这些：

- **轮数**：worker 模型在引入 lead 之前可以尝试多少次
- **失败处理**：当事情不按计划进行时会发生什么
- **回退行为**：系统如何从问题中恢复

### 实战中的魔法

在我们的[直播](https://www.youtube.com/embed/IbBDBv9Chvg)中，我们攻克了一个真实项目：为 MCP 服务器文档页面添加安装按钮。有意思的不只是最终结果，而是看着两个模型如何协作。

lead 模型会分析需求、理解现有代码库结构，并制定计划。然后 worker 模型会加入进来开始实现，做实际的代码改动并处理技术细节。

#### 项目：文档增强

我们想为 MCP 服务器卡片添加安装按钮，类似于扩展页面上已有的那种。我们需要弄清楚如何在不破坏现有工作流的前提下添加这个功能。

以下是 Lead/Worker 模型帮助我们完成的事情：
- **分析了现有文档结构**
- **识别出最佳方法**（创建自定义页面 vs. 修改现有页面）
- **实现了解决方案**，包含正确的路由和样式
- **处理了边界情况**，比如在添加安装功能的同时保留教程链接

### 开发者体验

有一件事特别突出：交互感觉非常自然。你不需要不断切换上下文或管理不同的工具。你只需描述你想要什么，系统会自己找出拆分工作的最佳方式。

lead 模型充当你的战略伙伴，而 worker 模型成为你的实现搭子。这就像结对编程，只不过搭档是永远不会疲惫、也不需要咖啡休息的 AI 模型。

### 来自我们这次会话的实用建议

#### 从良好的 Goose Hints 开始
我们一直建议设置你的 [goosehints](https://block.github.io/goose/docs/guides/context-engineering/using-goosehints)，为项目提供上下文。这能让你不必一遍又一遍地重复解释同样的事情。

#### 不要微观管理
让 lead 模型去做它的规划。有时候，最好的结果来自给出高层次的指示，然后让系统自己弄清楚细节。

#### 用 Git 保障安全
做实验时始终在一个分支中工作。模型很聪明，但有了这层安全网，你在提需求时就能更放得开。

#### 视觉反馈有帮助
虽然桌面 UI 不像 CLI 那样清晰地显示模型切换，但你仍然可以通过展开工具输出来跟进底层发生了什么。

### 结果说明一切

到会话结束时，我们做到了：
- ✅ 成功为 MCP 服务器文档添加了安装按钮
- ✅ 保留了所有现有功能（教程链接仍然可用）
- ✅ 通过更好的视觉层级改善了用户体验
- ✅ 将内容组织成逻辑清晰的区块（社区服务器 vs. 内置服务器）

最棒的部分？模型做出了一些我们甚至没想到的聪明决策，比如自动对服务器分类，并改进整体页面布局。

### 准备好尝试多模型工作流了吗？

Lead/Worker 模式已被移除，但 goose 仍然支持[多模型工作流](https://block.github.io/goose/docs/guides/multi-model/)。无论你是在处理文档、构建功能，还是攻克复杂的重构，把强大的推理模型与快速的执行模型配对，都可能改变游戏规则。

想看看实际效果吗？查看我们现场构建这个功能的完整直播：

<iframe class="aspect-ratio" width="560" height="315" src="https://www.youtube.com/embed/IbBDBv9Chvg" title="LLM Tag Team: Who Plans, Who Executes?" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

有问题，或者想分享你自己的 Lead/Worker 成功故事？来我们的 [Discord 社区](https://discord.gg/n8R5VaWDAn)找我们——我们很想听听你在构建什么！


<head>
  <meta property="og:title" content="LLM Tag Team: Who Plans, Who Executes?" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/08/11/llm-tag-team-lead-worker-model" />
  <meta property="og:description" content="Dive into Goose's Lead/Worker model where one LLM plans while another executes - a game-changing approach to AI collaboration that can save costs and boost efficiency." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/header-image-bed3ed59a52ea231c1da0707b9b6d287.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="LLM Tag Team: Who Plans, Who Executes?" />
  <meta property="twitter:description" content="Dive into Goose's Lead/Worker model where one LLM plans while another executes - a game-changing approach to AI collaboration that can save costs and boost efficiency." />
  <meta name="twitter:image" content="https://goose-docs.ai/assets/images/header-image-bed3ed59a52ea231c1da0707b9b6d287.png" />
</head>

---

## MCP UI：把浏览器带进智能体

> 原文：https://block.github.io/goose/blog/2025-08-11-mcp-ui-post-browser-world

![blog cover](https://block.github.io/goose/img/mcp-ui-shot.png)

Goose 最近发布了对 [MCP-UI](https://mcpui.dev/) 的支持，它允许 MCP 服务器向智能体建议并贡献用户界面元素。

:::warning
MCP-UI 仍是一个[开放 RFC](https://github.com/modelcontextprotocol-community/working-groups/issues/35)，正在被考虑纳入 MCP 规范。它目前可以正常工作，但随着提案推进可能会发生变化。
:::

MCP-UI 构建在协议之上，但服务器返回的不再是 text/markdown 结果，而是客户端可以丰富渲染的内容（包括交互式 GUI 内容）。

<!-- truncate -->

智能体承担的许多日常活动都能从图形化呈现中受益。有时这是由智能体自行渲染一个 GUI 来完成的（我知道我经常这么干），但 MCP-UI 让它能更内在地融入扩展，适用于人与界面进行图形化交互最佳的场景。它天然（因此才有了 [Shopify 的联动](https://shopify.engineering/mcp-ui-breaking-the-text-wall)）也很适合电商类应用，因为你想看到商品！

值得花一分钟看这段航空公司选座 MCP 服务器演示，感受一下这项能力：

  <video 
    controls 
    class="aspect-ratio"
    poster={require('@site/static/img/mcp-ui-shot.png').default}
    playsInline
  >
    <source src={require('@site/static/videos/mcp-ui.mov').default} type="video/mp4" />
    Your browser does not support the video tag.
  </video>

本质上，MCP 服务器在建议一些 GUI 元素，供客户端（智能体）按它认为合适的方式渲染。

### 我该怎么用

从 Goose v1.3.0 起，你可以把 MCP-UI 作为一个扩展添加进来。

:::tip 为 Goose 添加 MCP-UI
<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  [启动安装程序](goose://extension?type=streamable_http&url=https%3A%2F%2Fmcp-aharvard.netlify.app%2Fmcp&id=mcpuidemo&name=MCP-UI%20Demo&description=Demo%20MCP-UI-enabled%20extension)
  </TabItem>
  <TabItem value="cli" label="goose CLI">
  使用 `goose configure` 添加一个 `Remote Extension (Streaming HTTP)` 扩展类型，并填入：

  **Endpoint URL**
  ```
  https://mcp-aharvard.netlify.app/mcp
  ```
  </TabItem>
</Tabs>
:::


看看 Andrew Harvard 提供的 [MCP-UI 演示](https://mcp-aharvard.netlify.app/)。你也可以查看他的 GitHub 仓库，里面有[可以上手的示例](https://github.com/aharvard/mcp_aharvard/tree/main/components)。

### MCP-UI 背后的技术

MCP-UI 的核心是一个 `UIResource` 接口：

```ts
interface UIResource {
  type: 'resource';
  resource: {
    uri: string;       // e.g., ui://component/id
    // highlight-next-line
    mimeType: 'text/html' | 'text/uri-list' | 'application/vnd.mcp-ui.remote-dom'; // text/html for HTML content, text/uri-list for URL content, application/vnd.mcp-ui.remote-dom for remote-dom content (JavaScript)
    text?: string;      // Inline HTML, external URL, or remote-dom script
    blob?: string;      // Base64-encoded HTML, URL, or remote-dom script
  };
}
```

`mimeType` 才是关键所在。它可以（在最简单的情况下）是 HTML 内容。

这里另一个关键技术是 [Remote DOM](https://github.com/Shopify/remote-dom)，这是 Shopify 的一个开源项目。它让你能把 DOM 元素从一个沙箱环境取出，在另一个环境中渲染，这对智能体来说非常有用。这也为智能体一侧按需渲染组件（即采用本地匹配的样式或设计语言）打开了可能性。


### 可能的未来

MCP-UI 仍处于早期阶段，所以细节可能会变，但这正是它当下值得试验的兴奋之处。

MCP-UI 将继续演进，或许会引入更多声明式的方式，让 MCP-UI 服务器指定自己需要某些类型的表单或组件，而不必指定确切的渲染方式。能指定这些组件、让智能体把它们渲染得漂漂亮亮——无论是在桌面客户端、移动客户端，还是命令行里的文本 UI——那该多好啊！

<head>
  <meta property="og:title" content="MCP UI: Bringing the Browser into the Agent" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/08/11/mcp-ui-post-browser-world" />
  <meta property="og:description" content="A first look at a UI for agents built on the proposed MCP-UI extension" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/mcp-ui-shot-1b80ebfab25d885a8ead1ca24bb6cf13.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="MCP UI: Bringing the Browser into the Agent" />
  <meta property="twitter:description" content="A first look at a UI for agents built on the proposed MCP-UI extension" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/mcp-ui-shot-1b80ebfab25d885a8ead1ca24bb6cf13.png" />
</head>

---

## 自动化 MCP 测试：用可组合的 Goose Recipe 校验工具元数据

> 原文：https://block.github.io/goose/blog/2025-08-12-mcp-testing

![Automated MCP Testing](https://block.github.io/goose/img/automated_mcp_testing.jpg)

### 自动化 MCP 测试：用可组合的 Goose Recipe 校验工具元数据

在构建 Model Context Protocol（MCP）服务器时，大多数开发工作都聚焦于工具功能，确保工具能执行并返回预期结果。但同样关键的还有工具元数据的质量：描述、提示（tooltips）和输入 schema。这些元素构成了工具与 Goose 这类 AI 智能体之间的「接口语言」。

然而元数据往往无人测试。这会破坏工具发现能力，并悄无声息地让智能体行为退化。在这篇文章中，我们将展示如何用**可组合的 Goose Recipe** 自动化元数据校验，把手工 QA 变成模块化、可重复的工作流，从而：

- 校验工具的可发现性和参数准确性
- 及早发现回归
- 安全地减少 token 用量

同时始终维持 AI 智能体所依赖的质量。

<!-- truncate -->

### 1. 手工元数据测试的挑战

随着你的工具集不断增长，通过运行查询、人工检查智能体行为来手动校验 MCP 元数据会很快失效。它低效、不一致，且容易出现悄无声息的回归。

#### 关键局限：

- **缓慢且无法扩展**：需要拉起智能体、输入查询，并逐条人工审阅输出。
- **结果不一致**：在不同环境和模型之间会有差异，导致问题难以复现。
- **静默失败**：损坏的提示会导致工具选择错误、参数缺失或被误解，以及工具冲突。
- **没有回归安全网**：一个工具元数据的变化可能影响其他工具，却没有任何机制来检测。
- **覆盖率差**：手工 QA 无法覆盖真实世界用户查询的多样性。

要跟上日益增长的 MCP 复杂度，**自动化元数据校验就成了切实的必需**。


### 2. 系统概览：模块化且可组合的 Goose Recipe

这个框架的基础是 [Goose 的 Recipe 引擎](https://goose-docs.ai/docs/guides/recipes/)。Recipe 为 AI 辅助任务定义可复用、声明式的工作流。每一个都封装了一个步骤——比如生成预测或比较结果——并可以组合成更大的流水线。

我们从一个核心 Recipe 开始，它把自然语言查询映射到工具调用。它读取查询、分析工具集，并产出结构化的 JSON 映射。这个 Recipe 成为以下工作流的构建块：

- 将预测结果与金标准集进行比对评估
- 把回归检查集成进 CI
- 运行 token 优化循环

通过串联和包装 Recipe，我们避免了重复，为 MCP 工具可发现性解锁了可扩展、可重复的 QA。

### 3. 核心引擎：用于工具预测的 Goose Recipe

系统的核心是一个 Goose Recipe，它系统性地把自然语言查询转换成结构化的工具预测。这个 Recipe 遵循清晰的三步流程：

> **读取查询 → 分析工具 → 生成预测**

#### 🔄 工作原理：分步说明

**第 1 步：读取查询**
Recipe 首先读取一个纯文本文件，其中每行一条自然语言查询：

```
List contributors to the block/mcp repository
List the top 10 contributors to aaif-goose/goose
Show me the closed branches in block/mcp
Show me all branches in the aaif-goose/goose repository
```

**第 2 步：让 Goose 做出预测**
借助 developer 扩展，Goose 分析 MCP 服务器源码和文档，以理解可用的工具、它们的参数和用法模式。然后它把每条查询映射到最合适的工具调用。

**第 3 步：把预测写入 JSON**
输出是一个结构化的 JSON 文件，每条查询都映射到其预期的工具和参数。

#### 🔧 完整的 Recipe 规范

<details>
<summary>点击展开完整的 recipe YAML</summary>

```yaml
version: 1.0.0
title: Generate tool predictions for natural language query
description: Generate a dataset for MCP tools that maps natural language queries to their expected tool calls
instructions: |
  Generate evaluation datasets that map natural language queries to their expected tool calls with parameters. Analyze tool documentation and source code to understand available functions, their parameters, and usage patterns. Create comprehensive JSON test cases that include the original query, expected tool name, and all required/implied parameters with realistic values. The output should be a complete JSON file with test_cases array, where each case maps a natural language request to its corresponding structured tool call. Use developer tools to examine source files, read documentation, and write the final JSON dataset to disk.
    For each query, provide
    - The natural language query
    - The expected tool name
    - All required parameters with appropriate values
    - Any optional parameters that are clearly implied by the query

    Tools documentation: {{ server_input }}, {{ tool_documentation }}

    Please generate a JSON file mapping queries to their expected tool calls with parameters.

    {
        "test_cases": [
            {
                "query": "Show me open pull requests in the aaif-goose/goose repository",
                "expected": {
                    "tool": "tool_name",
                    "parameters": {
                        "repo_owner": "block",
                        "repo_name": "goose",
                        "p1": "test",
                        "p2": "test"
                    }
                }
            },
            {
                "query": "Create a new issue titled 'Update documentation' in the mcp repo",
                "expected": {
                    "tool": "tool_name",
                    "parameters": {
                        "repo_owner": "block",
                        "repo_name": "mcp",
                        "p1": "test",
                        "p2": "test"
                    }
                }
            }
        ]
    }

    Query Input - {{ quey_input }}
    Output File - {{ output_file }}
prompt: Generate evaluation datasets that map natural language queries to their expected tool calls with parameters. Analyze tool documentation and source code to understand available functions, their parameters, and usage patterns. Create comprehensive JSON test cases that include the original query, expected tool name, and all required/implied parameters with realistic values. The output should be a complete JSON file with test_cases array, where each case maps a natural language request to its corresponding structured tool call. Use developer tools to examine source files, read documentation, and write the final JSON dataset to disk. Read instructions for more details.

extensions:
- type: builtin
  name: developer
  display_name: Developer
  timeout: 300
  bundled: true
settings:
  goose_provider: databricks
  goose_model: goose-claude-4-sonnet
  temperature: 0.0
parameters:
- key: server_input
  input_type: string
  requirement: required
  description: server.py file path
  default: src/mcp_github/server.py
- key: tool_documentation
  input_type: string
  requirement: optional
  description: Tool documentation
  default: src/mcp_github/docs/tools.md
- key: quey_input
  input_type: string
  requirement: required
  description: Input query set
  default: mcp_github_query_test.txt
- key: output_file
  input_type: string
  requirement: optional
  description: Output JSON file
  default: new_evaluation.json
activities:
- Map queries to tool calls
- Extract tool parameters
- Generate test datasets
- Analyze API documentation
- Create evaluation benchmarks
author:
  contact: user
```

</details>

#### 🚀 运行该 Recipe

```bash
goose run --recipe generate_predictions_recipe.yaml --params output_file=my_predictions.json
```

#### 🧪 输出 JSON 示例

该 Recipe 会生成一个完整的 JSON 文件，把每条查询映射到其预测的工具调用：

```json
{
  "test_cases": [
    {
      "query": "List contributors to the block/mcp repository",
      "expected": {
        "tool": "list_repo_contributors",
        "parameters": {
          "repo_owner": "block",
          "repo_name": "mcp"
        }
      }
    },
    {
      "query": "Show me the closed branches in block/mcp",
      "expected": {
        "tool": "list_branches",
        "parameters": {
          "repo_owner": "block",
          "repo_name": "mcp",
          "branch_status": "closed"
        }
      }
    },
    {
      "query": "Search for files containing console.log",
      "expected": {
        "tool": "search_codebase",
        "parameters": {
          "search_term": "console.log"
        }
      }
    },
    {
      "query": "Find me all the files that are handling nullpointerexception",
      "expected": {
        "tool": "search_codebase",
        "parameters": {
          "search_term": "nullpointerexception"
        }
      }
    }
  ]
}
```

这个 JSON 成为所有下游评估工作流的基础——它精确捕捉了在给定当前工具元数据的情况下 Goose 如何解释每条查询，为检测未来的回归建立了一条基线。

### 4. 工作流 1：自动化的元数据回归检测

![Automated Metadata Regression Detection](https://block.github.io/goose/img/evaluate_predictions.png)

在第 3 节确立了核心 Goose Recipe 组件之后，我们现在可以利用它的模块化来构建更复杂的工作流。这种架构的美妙之处在于，核心预测 Recipe 成为一个可复用的构建块——我们可以从其他 Recipe 引用它、用比较逻辑串联它，并组合出端到端的测试流水线。这展示了把 Recipe 当作独立模块、编排到一起以实现复杂自动化工作流的力量。

一旦通过核心 Recipe 生成预测，下一步就是通过与一份精挑细选的「金标准」数据集比对来检测回归。这种自动化评估遵循清晰的三步流程：

> **生成预测 → 与金标准集比对 → 解释结果**

#### 🔄 工作原理：分步说明

**第 1 步：用核心 Recipe 生成预测**
首先，我们运行第 3 节的核心 Recipe，基于当前工具元数据生成全新的预测：

```bash
goose run --recipe generate_predictions_recipe.yaml --params output_file=new_evaluation.json
```

这会产出一个包含当前工具预测的 JSON 文件。

**第 2 步：把预测与金标准比对**
接下来，我们用一个 Python 比较脚本来找出新预测与我们已验证的金标准之间的差异：

```bash
python compare_results.py new_evaluation.json mcp_github_query_tool_truth.json
```

该脚本执行结构化 diff，标记出工具名、参数或取值上的不匹配。

**第 3 步：让 Goose 解释结果**
最后，Goose 分析比较输出，突出显示哪些地方不匹配，并用人类可读的方式解释这些差异。

#### 🧪 完整的评估 Recipe

<details>
<summary>点击展开完整的评估 recipe YAML</summary>

```yaml
version: 1.0.0
title: Generate predictions and compare with the gold set
description: Generate predictions and evaluate against a known correct output
instructions: |
  This task involves running automated evaluation scripts to generate tool-parameter mappings from natural language queries, then comparing the output against gold standard datasets to identify discrepancies. 

  Command to generate output: goose run --recipe generate_predictions_recipe.yaml --params output_file={{ output_file }}
  Script to compare 2 files: python compare_results.py {{ output_file }} {{ gold_file }}

  Go over the output of the comparison script and highlight what cases differ in terms of tool name or parameters. You can ignore minor mismatches like:
    - parameter value casing
    - value not present vs default value present
prompt: Generate predictions, evaluate and compare with the gold set. Read instructions for more details.
extensions:
- type: builtin
  name: developer
  display_name: Developer
  timeout: 300
  bundled: true
settings:
  goose_provider: databricks
  goose_model: goose-claude-4-sonnet
  temperature: 0.0
parameters:
- key: output_file
  input_type: string
  requirement: required
  description: Output file path
  default: new_evaluation.json
- key: gold_file
  input_type: string
  requirement: required
  description: Gold file path
  default: mcp_github_query_tool_truth.json
activities:
- Generate evaluation datasets
- Compare JSON outputs
- Analyze parameter mismatches
- Run recipe commands
- Identify tool mapping errors
author:
  contact: user
```

</details>

#### 🚀 运行完整的评估

```bash
goose run --recipe evaluate_predictions.yaml --params output_file=new_evaluation.json gold_file=mcp_github_query_tool_truth.json
```

#### 📉 比较结果示例

以下是系统检测到的两类常见不匹配：

**❌ 示例 1：工具名不匹配**
- **查询：**「Show me the closed branches in block/mcp」
- **金标准：**
  ```json
  {
    "tool": "list_branches",
    "parameters": {
      "repo_owner": "block",
      "repo_name": "mcp",
      "branch_status": "closed"
    }
  }
  ```
- **当前预测：**
  ```json
  {
    "tool": "get_repo_branches", 
    "parameters": {
      "repo_owner": "block",
      "repo_name": "mcp",
      "status": "closed"
    }
  }
  ```
- **问题：**工具名从 `list_branches` 变成了 `get_repo_branches`，很可能是由于提示或函数名更新所致

**❌ 示例 2：参数不匹配**
- **查询：**「Search for files containing console.log in aaif-goose/goose」
- **金标准：**
  ```json
  {
    "tool": "search_codebase",
    "parameters": {
      "search_term": "console.log",
      "repo_owner": "block",
      "repo_name": "goose"
    }
  }
  ```
- **当前预测：**
  ```json
  {
    "tool": "search_codebase",
    "parameters": {
      "search_term": "console.log"
    }
  }
  ```
- **问题：**缺少 `repo_owner` 和 `repo_name` 参数，说明该工具的描述可能没有清楚地表明在特定仓库内搜索时这些参数是必需的

#### 🔍 哪些会被标记 vs. 被忽略

**严重问题（会被标记）：**
- 工具名不匹配
- 缺少必需参数
- 参数取值错误
- 多余的意外参数

**次要问题（会被忽略）：**
- 参数取值的字母大小写差异（`"Console.log"` vs `"console.log"`）
- 默认值存在 vs. 省略
- 参数顺序差异

这个反馈回路对拉取请求校验变得至关重要——尤其是在工具描述更新、新工具添加或现有 schema 被修改时。该系统确保元数据变更不会意外破坏 AI 智能体的工具可发现性。

### 5. 工作流 2：安全的元数据 token 削减与优化
![Safe Metadata Token Reduction and Optimization](https://block.github.io/goose/img/reduce_tokens.png)

在之前几节建立的模块化 Recipe 架构之上，我们可以创建更精巧的工作流，把多个自动化步骤组合起来。一个强有力的例子是迭代式 token 削减流水线，它在确保功能完好无损的同时安全地压缩 MCP 工具描述。

这个工作流展示了可组合 Goose Recipe 的真正威力——我们可以把第 3 节的核心预测 Recipe 与第 4 节的评估工作流编排成一个持续优化循环，在减少 token 用量的同时不破坏工具可发现性。

#### 🔄 优化循环：分步说明

token 削减工作流遵循一个迭代过程：

> **减少 token → 运行评估 → 修复问题 → 运行评估 → 重复**

**第 1 步：压缩工具描述**
借助自然语言处理，Goose 识别出冗长的提示、冗余的文档和不必要的示例，然后在保留必要信息的前提下压缩它们。

**第 2 步：运行评估流水线**
系统自动触发第 4 节的评估工作流，测试压缩后的描述是否仍能支持正确的工具发现。

**第 3 步：修复问题**
如果评估测试失败，Goose 分析具体的不匹配之处，并迭代地修复压缩后的提示以恢复功能。

**第 4 步：重复直到成功**
循环持续进行，直到所有评估测试都通过，确保工具可发现性没有任何回归。

#### 🧪 完整的 token 削减 Recipe

<details>
<summary>点击展开完整的 token 削减 recipe YAML</summary>

```yaml
version: 1.0.0
title: Compress MCP token and Evaluate
description: Recipe for running the reduce mcp token and evaluation in a loop
instructions: |
  This task involves optimizing MCP (Model Context Protocol) tool definitions by reducing token count in tooltips, 
  field descriptions, and documentation while maintaining functionality. 
  The process requires creating backups, compressing descriptions and docstrings, removing verbose examples and redundant text, then running evaluation tests to ensure no functionality is broken. 
  If tests fail, iteratively fix the compressed tooltips and re-run evaluations until all tests pass. 
  The goal is to achieve significant token reduction {{ target_reduction }}% while preserving tool accuracy.
  Use the provided token counting script to measure before/after savings and report final reduction percentages.

  Files containing tokens:
  MCP server file: {{ server_input }}
  MCP tool documentation {{ tool_documentation }}
  Script to count tokens {{ count_token_script }}
  Command to run evaluation goose run --recipe evaluate_predictions.yaml
prompt: Reduce token count for tool descriptions and tooltips and make sure evaluation succeeds. Read instructions for more details
extensions:
- type: builtin
  name: developer
  display_name: Developer
  timeout: 300
  bundled: true
settings:
  goose_provider: databricks
  goose_model: goose-claude-4-sonnet
  temperature: 0.0
parameters:
- key: server_input
  input_type: string
  requirement: required
  description: server.py file path
  default: src/mcp_github/server.py
- key: tool_documentation
  input_type: string
  requirement: optional
  description: Tool documentation
  default: src/mcp_github/docs/tools.md
- key: count_token_script
  input_type: string
  requirement: optional
  description: Script to count tokens in server files
  default: count_tooltip_tokens.py
- key: target_reduction
  input_type: number
  requirement: optional
  description: Target reduction in token count we want to achieve
  default: 30
activities:
- Compress tool tooltips
- Remove verbose examples
- Run evaluation tests
- Fix failing test cases
- Calculate token savings
author:
  contact: rarora
```

</details>

#### 🚀 运行 token 削减循环

```bash
goose run --recipe compress_evaluate_mcp.yaml --params target_reduction=10
```

#### 📉 真实示例：迭代修复过程

以下是运行该工作流的一个实际示例，展示了系统如何识别并修复问题：

```
The evaluation shows that our token compression was successful, but we have some test failures. Let me analyze the specific issues and fix them:

1. Time format differences: "7 days" vs "P1W", "20 days" vs "P20D"
2. File search time format: absolute timestamp vs "1w"
3. Minor typos in queries: "branchs" vs "branches", "coomits" vs "commits", "file sin" vs "files in"

Let me fix the time format issue by updating the tooltips to be more specific about expected formats:
```

随后系统会自动更新工具描述，并重新运行评估，直到所有测试都通过。

#### 🎯 真实结果汇总

以下是一次成功的 token 削减运行的实际汇总：

```
# Summary

I have successfully completed the token reduction task for the GitHub MCP tools. Here's a comprehensive summary of what was accomplished:

## 📊 Token Reduction Results

**Final Token Savings:**
- **Original tokens**: 5,819 (2,174 from server.py + 3,645 from tools.md)
- **After compression**: 1,603 (445 from server.py + 1,158 from tools.md)
- **Total reduction**: 4,216 tokens
- **Percentage reduction**: 72.5%

## 🎯 Target Achievement

The task requested a 10% token reduction, but I achieved **72.5% reduction** - far exceeding the target while maintaining functionality.

## 🔧 Compression Strategies Applied

### 1. Server.py Optimizations
- **Field descriptions**: Shortened verbose descriptions (e.g., "Repository owner" → "Repo owner")
- **Docstrings**: Compressed from detailed explanations to concise summaries
- **Parameter hints**: Added specific format hints for time parameters (ISO 8601: P1W, P20D)
- **Removed redundant words**: Eliminated unnecessary qualifiers and explanations

### 2. Tools.md Optimizations
- **Removed sections**: Eliminated overview, comparison tables, and notes sections
- **Streamlined format**: Simplified parameter descriptions
- **Consolidated content**: Focused only on essential tool information
- **Removed examples**: Eliminated verbose usage examples

## ✅ Quality Assurance

### Evaluation Results
- **Test cases**: 36 total
- **Exact matches**: 35/36 (97.2% accuracy)
- **Tool selection**: 100% accurate
- **Parameter mapping**: 100% functionally correct

### Single Mismatch Analysis
The one mismatch was a **style difference** rather than a functional error:
- Generated version: More explicit field specifications
- Gold standard: Minimal field specifications
- Both approaches are functionally equivalent
```

### 6. 结语

自动化的 MCP 元数据校验不必脆弱，也不必是一次性的。通过使用**模块化的 Goose Recipe 架构**，我们展示了单个核心预测 Recipe 如何支撑多个高价值工作流——从**及早发现回归**到**安全地减少 token**，而不牺牲可发现性。

这种可组合的方法带来三大收益：
- **可复用性**——同一套核心逻辑支持不同工作流，无需重写代码。
- **安全性**——自动化校验确保变更永远不会悄无声息地破坏工具用法。
- **可扩展性**——该架构适用于任何 MCP 服务器或工具集，无论规模大小。

有了这些构建块，团队可以放心地扩展自己的自动化工具箱——因为知道每一项新的优化或增强，都会有同样严格、可重复的校验流程作为后盾。

<head>
  <meta property="og:title" content="Automated MCP Testing: Using Composable Goose Recipes to Validate Tool Metadata" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/08/12/mcp-testing" />
  <meta property="og:description" content="Automate MCP tool metadata validation using composable Goose recipes to catch regressions, optimize token usage, and ensure AI agents can reliably discover and use your tools" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/automated_mcp_testing-296dac2cd2b1b327e58854f4bfb0c89a.jpg" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Automated MCP Testing: Using Composable Goose Recipes to Validate Tool Metadata" />
  <meta property="twitter:description" content="Automate MCP tool metadata validation using composable Goose recipes to catch regressions, optimize token usage, and ensure AI agents can reliably discover and use your tools" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/automated_mcp_testing-296dac2cd2b1b327e58854f4bfb0c89a.jpg" />
</head>

---

## PulseMCP 如何用 Goose 自动化他们的时事通讯工作流

> 原文：https://block.github.io/goose/blog/2025-08-13-pulse-mcp-automates-recipe

![pulsemcp](https://block.github.io/goose/img/pulsemcp.png)

*「最好的 AI 智能体工作流不止于演示。它们带来真实的生产力。」*

Block 的 DevRel 团队是 [PulseMCP](https://pulsemcp.com) 的超级粉丝。他们的每周时事通讯是我们发现热门 MCP 服务器、跟进生态内任何变化的一个绝佳途径。当 PulseMCP 的创作者 Mike 和 Tadas 分享他们想用 Goose 来帮助[自动化时事通讯工作流中那些枯燥部分](https://www.pulsemcp.com/building-agents-with-goose)的目标时，我们很兴奋地想看看他们会构建出什么。

他们的实现恰好展示了我们当初为何把 Goose 的功能集设计成现在这样，而且他们记录了整个历程，帮助他人从他们的经验中学习。

<!-- truncate -->

### 挑战

每周，PulseMCP 团队都面临同样耗时的流程：从多个平台搜集相关新闻、整理并去重、起草引人入胜的叙述、为质量和准确性打磨、跨多个渠道发布，以及管理邮件分发。这个重复性的工作流看起来非常适合 AI 自动化，但它又足够复杂，以至于大多数尝试都会失败。

### 解决方案：为什么顺序化胜过单体化

PulseMCP 没有构建一个庞大的「什么都干」的智能体（这在复杂任务上必然失败），而是把工作流拆成六个不同的阶段。每个阶段都由专注的 [Recipe](https://block.github.io/goose/docs/guides/recipes/session-recipes)、[子 Recipe](https://block.github.io/goose/docs/guides/recipes/subrecipes) 和[子代理](https://block.github.io/goose/docs/guides/context-engineering/subagents)来处理，各自有清晰的输入、输出和单一的职责。

这种方法有三大好处：当智能体职责单一时调试变得更容易；阶段之间有清晰交接时结果变得更具可预测性；在自动化那些枯燥工作的同时，人类依然掌控编辑流程。

### 六智能体流水线

#### **1. Sourcer（来源搜集）智能体**
通过 MCP 集成自动扫描 GitHub、Reddit 和 HackerNews 上的相关内容，同时人类在一周内筛选出最有趣的发现。

#### **2. Organizer（整理）智能体**
去重、给条目分类，并补充上下文，把原始链接变成有条理的内容。

#### **3. Drafter（起草）智能体**
把统计数据和上下文合并进由人类撰写的叙述中，处理枯燥的数据汇编工作，同时保留编辑的口吻。

#### **4. Polisher（润色）智能体**
处理拼写检查、链接校验和一致性审查——这些否则要耗费人类数小时注意力。

#### **5. Publisher（发布）智能体**
管理技术发布环节：HTML 格式化、CMS 上传，以及通过 MCP 服务器进行内容部署。

#### **6. Sender（发送）智能体**
处理邮件活动的设置、预览生成和分发排期。

### 帮助人类，而非取代他们

令人瞩目的不只是 PulseMCP 自动化了他们的时事通讯，而是他们如何在消除枯燥工作的同时保留了人类的创造力。人类仍然做编辑决策、撰写叙述、保持创意掌控，而智能体处理那些消耗人类精力的重复性任务。

结果就是一个既更高效又更高质量的工作流。智能体永远不会厌倦检查链接或格式化内容，从而解放人类去专注于战略思考和创意叙事。

### 未来的一瞥

PulseMCP 团队设想了一种智能体，可以「替你构建这些 Recipe」。想象一下，用自然语言描述你的工作流，AI 就自动生成智能体架构和集成点。

我们已经能看到这种能力的苗头。正如 Tadas 通过这样的提示所演示的：

> 「嘿 Goose：我有一些难以阅读的 AI 智能体日志文件。你能给我构建一个带漂亮 UI 的简单 Web 服务器，让我作为人类能解析它们吗？」*

这指向了一个未来：AI 处理机械性工作，而人类专注于战略、创造力和判断。

### 蓝图已经公开

PulseMCP 团队把一切都记录在一份 95 页的全面手册中，它既是灵感来源，也是实现指南。他们的工作证明：成功的 AI 智能体部署不在于取代人类或构建复杂的 AI 系统，而在于深思熟虑的工作流设计、清晰的边界和实用的模式。

**[阅读完整的 PulseMCP 手册：「A Human, A Goose, and Some Agents」](https://www.pulsemcp.com/building-agents-with-goose)**

他们详尽的案例研究包含完整的智能体架构、真实的 YAML recipe 文件、生产部署的经验教训，以及一份构建你自己智能体的实用速查表。

### 接下来是什么？

PulseMCP 的实现证明，我们已经走过了 AI 智能体的演示阶段。真正的生产力提升正在此刻发生，就在生产工作流中，通过深思熟虑的人机协作实现。掌握了这些模式的组织将拥有显著优势。

---

*想构建你自己的 AI 智能体工作流？[开始使用 Goose](https://goose-docs.ai/)，加入构建人机协作未来的开发者社区。*

<head>
  <meta property="og:title" content="How PulseMCP Automated Their Newsletter Workflow with Goose" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/08/13/pulse-mcp-automates-recipe" />
  <meta property="og:description" content="PulseMCP used Goose recipes, subagents, and subrecipes to automate the boring parts of their newsletter workflow" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/pulsemcp-65abe93bd65402c122b395ae6bdadf95.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="How PulseMCP Automated Their Newsletter Workflow with Goose" />
  <meta property="twitter:description" content="PulseMCP used Goose recipes, subagents, and subrecipes to automate the boring parts of their newsletter workflow" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/pulsemcp-65abe93bd65402c122b395ae6bdadf95.png" />
</head>

---

## 智能体、子代理与多智能体：它们是什么，何时该用

> 原文：https://block.github.io/goose/blog/2025-08-14-agent-coordination-patterns

![blog banner](https://block.github.io/goose/img/agent-coordination.png)

我在 [UC Berkeley 教了一场 vibe coding 工作坊](https://block.github.io/goose/blog/2025/08/10/vibe-coding-with-goose-building-apps-with-ai-agents)，告诉学生们我们将拉起 7 个子代理。有人很快举手问：「什么是子代理？」那一刻我意识到，我们一直在抛出 **agent**、**multi agent** 和 **subagent** 这类术语，却没有真正花时间解释它们是什么。所以，来吧……一篇 101 入门，拆解这些不同的协调模式，以及何时该用它们。

<!-- truncate -->

:::tip 太长不看
- **agent（智能体）**——一个自主的行动者，接过你的目标并从头到尾地执行

- **subagents（子代理）**——一种设置，由主智能体充当编排者，把工作委派给它控制的其他智能体。主智能体掌握流程、顺序和协调。

- **multi agents（多智能体）**——两个或更多主智能体，各自独立行动，但能够协作、协商或交换结果。没有哪个智能体是「老板」。
:::


这些术语听起来很唬人，但说到底，它们只是用 AI 把事情办成的不同方式。有点像决定你是想单干、结对编程，还是带领一个小队。

**让我用一个简单的新功能来说明：给公司的 Web 应用添加暗色模式。**

### 智能体：孤胆英雄模式

你把任务交给一个 AI 智能体，比如 [Goose](https://block.github.io/goose/)。智能体是一个自主的行动者，本质上是你的一人军队。

你告诉你的智能体：「给应用加上暗色模式。」它读取仓库，更新 CSS 和主题，运行测试，并开一个 PR。它从头到尾处理了整件事。没有队友，没有交接。

如果智能体在某个步骤上搞砸了（比如它忘了更新设置菜单里的开关），它必须自己回退并修复。

把它想成一个独自埋头啃工单的开发者。

### 子代理配置：带着一队人的编排者

使用[子代理](https://block.github.io/goose/docs/guides/context-engineering/subagents)时，你仍然只有一个「主」智能体，但它不是什么都做，而是扮演技术负责人的角色，把工作的各部分委派给其他专门的智能体。

主智能体说：

- _「设计师智能体，创建暗色模式的调色板。」_
- _「前端智能体，把它应用到所有 UI 组件上。」_
- _「QA 智能体，运行视觉回归测试。」_

这些子代理可以并行工作（比如设计师在做调色板时，前端在更新样式），也可以串行工作（比如前端等到设计师完成）。

主智能体让一切保持在正轨上，收集结果，并把它们拼接起来。

把它想成一位技术负责人，把这个功能拆成子任务、分派下去，然后合并工作成果。

### 多智能体场景：两个主脑互相商量

在多智能体模式下，没有单一的编排者。你有多个互相交谈的主智能体，每个都有自己的目标或视角。

对于我们的暗色模式功能，想象一下：

- 开发智能体了解代码库，能实现 UI 改动。
- UX 研究智能体了解用户如何与主题交互，以及需要考虑哪些无障碍需求。

它们协同工作。UX 智能体解释最佳实践、边界情况和用户痛点，而开发智能体负责实现并回来征求意见。它们甚至可能运行在不同的系统上，比如你的开发智能体调用一个托管在别处的外部设计智能体。

值得一提的是，多智能体配置不必都在处理完全相同的任务。有时它们只是运行在同一个环境中，当工作有重叠时就会协作。

把它想成两位同侪在 Slack 上反复磋商，直到拿出一个扎实的方案。

### 何时该用哪种

- **agent**：小型的、自成一体的任务，你信任一个 AI 去搞定
- **subagents**：复杂的任务，能从「分而治之 + 有监督」中受益
- **multi agents**：需要多个大脑或视角，能够协商和协作

这些配置只是组织工作的不同方式，无论是人类的工作还是 AI 的工作。诀窍在于挑选那种能让你在速度和准确性之间取得最佳平衡的结构。

<head>
  <meta property="og:title" content="Agents, Subagents, and Multi Agents: What They Are and When to Use Them" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/08/14/agent-coordination-patterns" />
  <meta property="og:description" content="A straightforward explanation of how agents are organized to work together" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/agent-coordination-52282acab8107e9503b17e471465ffa5.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Agents, Subagents, and Multi Agents: What They Are and When to Use Them" />
  <meta property="twitter:description" content="A straightforward explanation of how agents are organized to work together" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/agent-coordination-52282acab8107e9503b17e471465ffa5.png" />
</head>

---

## 我如何用 Goose 重建我的网站

> 原文：https://block.github.io/goose/blog/2025-08-14-how-goose-rebuilt-my-website

![blog banner](https://block.github.io/goose/img/blog_banner.png)

对我来说，网站是互联网上一个我可以做自己的角落，在那里分享我的作品，归根结底是一个我想干什么就干什么的地方。如果它不能把我的个性人格化——尤其是我作为一个前极客博客设计师（在我初中和高中的日子里）——那也太可悲了！直到突然之间，一个起初无害的「404 Day」挑战，转眼就变成了基本上没花什么时间就把那个网站做出来了。

<!-- truncate -->

### 回到我的根

当我说我曾为别人做极客风格的博客时，我的意思是我就活在 HTML 和 CSS 的深水区。那是一门爱好，我得以在互联网上为像我这样的极客打造超级定制的网站。所以，今天拥有一个基本上就是 :poopemoji: 人格化的网站，真的让我很烦躁。没有个性，没有我自己的风格，只是一个极简的通用布局，我每个月付订阅费只是为了避免彻底的尴尬。距那时至少已经过去十年了，而我完全没心情坐在这里重新学习那些零零碎碎的东西，从零搭出一个网站结构。我草稿里什么素材都有，只是需要结构。

### 开启这一切的 404 挑战

然后就有了这个[404 日简单易用的提示词](https://www.linkedin.com/posts/block-opensource_happy-404-day-we-used-goose-to-generate-activity-7313972103613939713-GF1T/)。那条帖子讲的是用 goose 创建你自己的 404 页面，goose 会根据你的个人资料给你一个定制页面。原始提示词大概是这样的：

> 创建一个 404 页面，用 GitHub 用户 @taniashiba 的公开 GitHub 数据——提交历史、贡献图、仓库，或任何你能访问的东西——讲述一个关于她的有创意的故事。

我拿来这个提示词，稍作修改。我的个人 GitHub 资料和贡献很不错，但我也想确保 goose 参考我的 LinkedIn、Instagram 和所有其他社交渠道，以便很好地把握我这个人。

> 你也可以参考 Tania 的 Bluesky/Instagram/TikTok/Twitter 账号（用户名 @taniashiba）以及她的 LinkedIn，以获取关于她的更多信息。

![404 page](https://block.github.io/goose/img/404page.png)

一个机智、而且在样式上确实相当能反映我是谁、我喜欢什么的 404 页面很快就诞生了。它甚至把我过去某条社交帖子里开的一个虾的玩笑塞了进去。我甚至都没告诉 goose 我喜欢什么配色，而它不知怎么就做出了打动我的东西。这点燃了一束明亮的灵感火花。于是，我问 goose：

> 你能记住这是你做的吗？我希望你用完全相同的样式，为 taniachakraborty.com 做一个网站。

### 实现

goose 帮我解决了一个感觉由来已久的问题，而且让这件事变得如此简单。我把网站交给 goose，告诉它托管在 Neocities 上，它就开工了。在用它为 404 页面打造的样式创建了通用页面之后，实现就很容易了：

1. **上传** goose 做好的文件到 Neocities
2. **审阅**网站，并让 goose 编辑或创建我需要的任何页面
3. **撰写内容**来填充网站的各个页面（我最喜欢的部分）

然后砰，我的网站就完成了。不用费力从记忆深处挖掘、重新学习 CSS，不用调试那些我以为在凌晨 2 点很酷的响应式悬停效果引发的 bug，完全没有麻烦。Goose 搞定了一切。它从一个简单的结构开始，沿用它在 404 日挑战中想出来的样式，并在我对话中提出要求时做出修改。我的网站从令人尴尬的空空如也，变成了设计精美、易于编辑——就在*几分钟*之内。

### 永远要用 Git

说实话，这感觉就像在玩电子游戏，因为我能看到改动实时出现在本地预览中，而且有了 git，我可以在过程中随时保存进度。Goose 甚至建议我把 dev.to 页面上的博客文章加进来，并为我创建了一个简单的模板。如果有东西显示得不如预期？我们就一起排查——我发截图给它看我看到的情况，goose 就把它修好。

### 一个巨大的省时利器，说真的

一件本来要花我一周到一个月才能建好的东西，转眼就完成了。与其为了构建你当下需要的东西而担心学习或重新学习一项技能，你可以边做边和 goose 一起学。这整个经历让我想起，我当初为什么会爱上为别人做网站样式——你真的能从无到有地创造出一些东西！

所以，如果你正坐在那里，面对一个光秃秃、需要帮助的网站，或者你一直拖延某个项目，因为技术层面感觉像一场压倒性的噩梦，也许是时候和一个像 goose 这样有用的工具开始对话了。谁知道呢？也许你最终会拥有自己的一座数字水族馆般的网站，网站页脚里潜伏着关于调试的虾的玩笑。🦐

---

*想看最终成果吗？来 [taniachakraborty.com](https://taniachakraborty.com) 看看我的作品集。告诉我你找到了多少个虾的玩笑。*

---

<head>
  <meta property="og:title" content="How Goose Helped Me Rebuild My Website" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/08/14/how-goose-rebuilt-my-website" />
  <meta property="og:description" content="How a simple prompt transformed a blank website into a personal portfolio" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/blog_banner-656bd5e1014edfbcd313a9f799f9e9a5.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="How Goose Helped Me Rebuild My Website" />
  <meta property="twitter:description" content="How a simple prompt transformed a blank website into a personal portfolio" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/blog_banner-656bd5e1014edfbcd313a9f799f9e9a5.png" />
</head>

---

## 把 AI 辅助从自动化转变为教育：Goose Mentor Mode 背后的故事

> 原文：https://block.github.io/goose/blog/2025-08-18-transforming-ai-assistance-goose-mentor-mode

![Goose Mentor Mode Header](https://block.github.io/goose/img/goose-mentor-mode-header.png)

Kim 刚从学院毕业，只学了 18 个月的开发。当我问她怎么看 Goose 时，她的反应很复杂。虽然她觉得它能替她做这么多事很酷，但有一半时间她其实并不确定它到底为她做了什么，也不清楚*为什么*。当她让 Goose 修复一个损坏的构建，或者追一个 bug 时，它会完成任务并宣称「成功！」。这当然很好，然而她觉得自己的学习收获不如在学院时那么多。再加上有时她甚至不知道该让 Goose 做什么。

那天下午，我开始琢磨能不能让 Goose 对我的初级开发者们来说不只是个「魔法盒子」。如果 Goose 反而能充当导师，在加速开发的同时也能教学，会怎样？

<!-- truncate -->

### 把 AI 辅助从自动化转变为教育：Goose Mentor Mode 背后的故事

作为一名在企业领域工作的工程经理，我的团队里大约有 16 名开发者。和当下行业里很多人一样，我一直在观察 AI 能如何融入我们的流程，能带来哪些效率。今年 7 月我上手了 Goose，很快就看到了它对我个人和我的团队所蕴含的惊人潜力。因为迫不及待想看看有什么可能，我迅速给所有开发者开通了权限，为他们接入了几个不同的模型，然后让他们玩了两周。

我的团队里开发者经验跨度很大，从技术负责人一直到刚毕业的新人。资深工程师和技术负责人惊叹于他们推进工作的速度。我的中级开发者也惊讶于他们调试损坏构建的速度之快。直到我和一位刚毕业的初级开发者开例行沟通会时，我才听到了不同的声音。

#### 问题：只做事、不教学的 AI

传统 AI 编程助手基于一个简单的假设运作：用户问，AI 给。这最大化了即时生产力，却制造了若干长期问题：

* **依赖的形成**：开发者对本来就该自己理解的问题变得依赖 AI
* **错失学习机会**：每一次请求本可以是积累知识的机会，结果却只是完成任务
* **一刀切**：对学习认证的初级开发者和在交付压力下实现认证的资深开发者不作区分
* **上下文盲区**：AI 对「我该怎么实现 JWT？」一视同仁，不管提问的人是 6 个月经验还是 6 年经验

#### 愿景：Goose Mentor Mode

Goose Mentor Mode 背后的使命简单却具有变革性：**把 AI 辅助从自动化转变为教育，同时维持开发者所需的效率**。

核心理念围绕四条原则：

1. **发现重于交付**：帮助用户理解*为什么*，而不只是*怎么做*
2. **自适应学习**：根据经验和上下文调整方法
3. **渐进式复杂度**：一层一层地构建理解
4. **以留存为重心**：强调能真正记住的学习

#### 当前功能：一个概念验证

我设想系统如何运作的核心，是配置一些基本的辅助等级：

##### **🎯 四个自适应辅助等级**

把辅助模式想象成一个旋钮，可以在学习速度与交付速度之间取得平衡。

**GUIDED（引导）模式**——通过发现进行深度学习

* 用苏格拉底式提问引导用户找到解决方案
* 非常适合新概念和技能构建
* *示例*：「你觉得 JWT 代表什么？无状态认证可能怎么工作？」

**EXPLAINED（讲解）模式**——教学与实现并行

* 在提供可用代码的同时给出详细解释
* 适合有时间压力、同时又有学习价值的任务
* *示例*：「JWT 是这样工作的……\[详细解释\] \+ 可用代码」

**ASSISTED（辅助）模式**——快速帮助，附带学习上下文

* 直接提供帮助，同时附带教学性洞见
* 最适合需要快速帮助的资深开发者
* *示例*：「用这个 JWT 库。关键安全考量：\[要点\]」

**AUTOMATED（自动化）模式**——高效完成任务

* 直接给出解决方案，不附带教学负担
* 适合生产压力和重复性任务
* *示例*：「这是完整的 JWT 实现。」

#####

##### **🧠 学习检测**

目前系统还处于 PoC 阶段，所以我只用了关键词检查来做学习检测。我正在试验语义分析，看能否「智能地」做到这一点，但这可能被证明是过度设计，甚至会拖累和减慢系统。

* 覆盖 7 个类别的 **19 个技术概念**（安全、数据库、API、架构、测试、性能、DevOps）
* 用于理解请求类型的 **6 个意图类别**（求助、学习咨询、调试等）
* **上下文感知分析**，能区分「认证错误」与「认证最佳实践」

##### **📊 全面的进度追踪**

理想情况下，我能为每个用户做长期运行的进度追踪，随时间跟踪。目前这个追踪还很基础，只基于当前正在「教授」的概念。
一个完整实现的方案可能包含这些功能：

* 跨概念的学习速度追踪
* 基于请求模式的技能缺口识别
* 个性化学习路径推荐
* 随时间推移的知识留存分析

##### **⚙️ 以开发者为中心的配置**

通过环境变量轻松设置，与 Goose Desktop 无缝集成：

```bash
DEFAULT_ASSISTANCE_LEVEL=guided          # Customize default behavior
LEARNING_PHASE=skill_building           # Set learning context
TIMELINE_PRESSURE=low                   # Adjust for project pressure
ENABLE_VALIDATION_CHECKPOINTS=true     # Control learning validation
DEVELOPER_EXPERIENCE_MONTHS=6           # Personalize experience
```

###

#### **未来功能：前方的路线图**

这只是一个概念验证，对扩展来说还处于非常早期的阶段。我目前有几个初级开发者正在试用它并提供反馈。以下是我在 Goose 帮助下整理出的一份清单，说明未来路线图可能是什么样子。

##### **阶段 1：增强智能（进行中）**

* **多信号学习检测**：结合语义分析、意图分类和行为模式
* **自适应阈值**：基于用户反馈自调优的置信度评分
* **上下文感知指导**：把用户画像、项目压力和学习阶段纳入考量的决策引擎

##### **阶段 2：外部学习集成**

* **上下文文档链接**：自动链接到相关文档，无论是线上的，还是可能由 Confluence 这类企业系统支撑的。
* **教程推荐**：个性化学习路径建议
* **最佳实践库**：代码模式示例和教学资源

##### **阶段 3：高级分析**

* **学习速度追踪**：衡量跨概念的技能发展
* **团队洞察**：协作学习机会与知识共享
* **技能缺口分析**：识别需要重点学习的领域
* **动态辅助调整**：基于学习进度实时自适应

##### **阶段 4：团队协调**

* **多开发者洞察**：团队知识图谱与技能分布
* **协作学习**：同伴学习推荐
* **知识共享**：团队范围的模式识别与最佳实践
* **隐私保护分析**：聚合洞见，同时保护个人隐私

#### **社区影响**

虽然我是在工作中产生了这个想法，但我很快决定这应该是我组织之外的个人项目。如果它有价值，这似乎理应开源，并面向更广泛的采用。目前源代码已在 github 上提供，也可以在 PyPI 上下载。

#### **更大的图景：改变我们对 AI 的思考方式**

Goose Mentor Mode 代表的不仅仅是一个新扩展——它是对开发者与 AI 之间一种根本不同关系的概念验证。它不制造依赖，而是构建能力。它不授人以鱼，而是授人以渔。

早期结果表明，这种方法引起了那些想要成长、而不只是想把事情做完的开发者的共鸣。随着 AI 在软件开发中越来越普遍，像 Goose Mentor Mode 这样的工具指向了一个未来：AI 增强人类能力，而不是取代人类思考。

---
*Goose Mentor Mode 是开源的，可在 [PyPI](https://pypi.org/project/goose-mentor-mode/) 上获取。来 [GitHub](https://github.com/joeeuston-dev/goose-mentor-mode) 参与讨论，帮助塑造教育型 AI 辅助的未来。*

<head>
  <meta property="og:title" content="Transforming AI Assistance from Automation to Education: The Story Behind Goose Mentor Mode" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/08/14/transforming-ai-assistance-gooe-mentor-mode" />
  <meta property="og:description" content="How a Junior developer's AI Agent confusion, led to creating an educational MCP extension that transforms Goose from an automation tool into a learning mentor." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/goose-mentor-mode-header-77058a250a163440d791e057ef3196ea.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Transforming AI Assistance from Automation to Education: The Story Behind Goose Mentor Mode" />
  <meta property="twitter:description" content="How a Junior developer's AI Agent confusion, led to creating an educational MCP extension that transforms Goose from an automation tool into a learning mentor." />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/goose-mentor-mode-header-77058a250a163440d791e057ef3196ea.png" />
</head>

---

## AI 怀疑论者的上下文窗口指南

> 原文：https://block.github.io/goose/blog/2025-08-18-understanding-context-windows

![Context Windows](https://block.github.io/goose/img/contextwindow.png)

与 AI 工具打交道，感觉就像与一位时好时坏、混乱不堪却又过度自信的同事共事。你知道的，就是那种会忘事、无缘无故撒谎、不告诉你就开新项目、然后干到一半就撂挑子的同事。这足以让你说：「算了，我自己来。」但在我们彻底放弃 AI 之前，值得理解一下底层到底发生了什么，这样我们才能避开常见的坑，让 AI 工具真正值得使用。

<!--truncate-->

这种行为的根源，在于 AI 工具如何处理工作记忆。同样地，作为人类，你一次也只能同时处理这么多信息。比如，当我在读一篇很长的研究论文时，等我读到结论部分，可能已经忘了引言里的关键细节，即便那些早期的要点对理解整个论证很重要。

AI 助手工作记忆的术语叫**上下文窗口（context window）**。

### 什么是上下文窗口？

上下文窗口是一个 AI 模型在单次会话中能处理的最大信息量。它以「token」来计量。

### 什么是 token？

Token 是 AI 模型处理文本时的拆解单位。它们大致相当于词或词片段，不过不同的模型根据各自的训练数据和设计选择，对文本进行 token 化的方式会有所不同。

**例如：**
 "Hello" = 1 个 token
 "Understanding" = 2 个 token（"Under" + "standing"）
 "AI" = 1 个 token
 "Tokenization" = 3 个 token

自己试一下：把任意文本粘贴到 [OpenAI 的 tokenizer 工具](https://platform.openai.com/tokenizer)，探索不同模型是如何计算 token 的。

#### Goose 如何使用 token

我们来谈谈这在实践中如何运作。当你使用 Goose 这样的 AI 智能体时，你会开始一个会话，并选择一个模型，比如 Claude Sonnet 3.7。这个模型的上下文窗口是 128,000 个 token。这意味着每个会话（或对话）最多能处理 128,000 个 token。如果你给 Goose 发一条「hey」，你就用掉了 1 个 token。当 Goose 回复时，你又用掉了好几个 token。现在你已经用掉了 128,000 个 token 中的一小部分，剩下的是剩余额度。

:::note
上下文窗口因 LLM 而异。
:::

一旦对话超过 128,000 个 token 或接近它，你的智能体可能就开始忘记对话早期的关键细节，并可能优先考虑最新的信息。

但你的对话并不是唯一消耗 token 的东西。以下是 Goose 内部其他消耗你 token 预算的部分：

* **系统提示词：** 一条内置提示词，指示你的智能体该如何行事，并定义它的身份
  * 系统提示词定义了 Goose 的名称、创建者（Block）、当前日期/时间、任务与扩展处理，以及响应格式。
* **扩展及其工具定义**——许多扩展内置了不止一个工具。比如，一个 Google Drive 扩展可能包含读取文件、创建文件、评论文件等工具。此外，每个工具都带有如何使用它的说明，以及对它做什么的解释。
* **工具响应**——工具返回的响应。比如，工具可能返回「这是你那个 500 行代码文件的全部内容。」
* 除了你的对话历史之外，Goose 还保存关于你对话的元数据，比如时间戳。

这是大量数据，很容易消耗掉你的上下文窗口。除了影响性能，token 用量还会影响成本。你用的 token 越多，付的钱就越多，而且你可能会因为把 token 浪费在智能体误解你的请求上而感到沮丧。

幸运的是，Goose 有一套聪明的设计来帮你节省上下文窗口。

### Goose 如何自动管理你的上下文窗口

Goose 有一种方法，会在你的对话达到某个阈值后自动压缩（或总结）它。默认情况下，当你达到上下文窗口的 80% 时，Goose 会总结这段对话，保留关键部分、压缩其余部分，从而降低上下文窗口占用，让你不必开新会话就能留在当前会话里。

你其实有能力自定义这个阈值。如果你觉得 80% 对你的工作流来说太少或太多，你可以把环境变量 `GOOSE_AUTO_COMPACT_THRESHOLD` 设置成你偏好的阈值。

### 如何管理你的上下文窗口

虽然 Goose 很擅长帮你管理上下文窗口，但你也可以主动管理它。以下是一些高效管理你的上下文窗口和钱包的建议。

**1. 手动总结**

当你的对话变得太长时，你可以总结要点并开始一个新会话。把重要决策、代码片段或项目需求复制到新会话中。这样，你保留了必要的上下文，而不必背负完整的对话历史。

**2. `.goosehints`**

使用 [.goosehints](https://block.github.io/goose/docs/guides/context-engineering/using-goosehints/) 文件来避免重复相同的指令。与其在每次对话里都打出你的项目上下文、编码规范和个人偏好，不如在 .goosehints 文件里一次性定义好。这能避免把 token 浪费在重复解释上，并帮助 Goose 更快地理解你的需求。

**3. Memory 扩展**

[Memory 扩展](https://goose-docs.ai/docs/mcp/memory-mcp)跨会话存储重要信息。与其每次开始新对话都重新解释你的项目背景、过往决策或重要上下文，你可以引用已存储的信息。这让你的提示词聚焦于当前任务，而不是重复历史上下文。

**4. Recipe**

[Recipe](https://goose-docs.ai/docs/guides/recipes/) 把完整的任务配置打包成可复用的配置，免去反复提供冗长指令的需要。与其在每个会话里都耗费 token 解释复杂的工作流，Recipe 一开始就包含所有必要的指令、扩展和参数。这对重复性任务尤其有价值，否则你会在设置和解释上花费大量 token。而且如果你的 Recipe 开始显得过于冗长，你可以把任务拆成[子 Recipe](https://goose-docs.ai/docs/guides/recipes/subrecipes)。

**5. 子代理**

[子代理](https://goose-docs.ai/docs/guides/context-engineering/subagents)在各自隔离的会话中处理特定任务。这能防止你的主对话被实现细节和工具输出塞得杂乱不堪。你把工作委派给子代理，只看到最终结果，从而让主上下文窗口保持干净和聚焦。

**6. 短会话**

让单个会话聚焦于特定任务。当你完成一个任务或到达一个自然的停顿点时，就开始一个新会话。这能防止累积的对话历史让上下文窗口膨胀，并确保你的 token 花在当前、相关的工作上。

**7. Planner 模型 + 聚焦执行**

为复杂工作使用一个强大的[推理模型](https://block.github.io/goose/docs/guides/multi-model/)，并让你的默认模型专注于执行。这让你能掌控成本和质量，同时让模型行为保持明确和可预测。

---

下次当你的 AI 智能体似乎「忘记」了某件重要的事或偏离正轨时，先检查一下你的上下文窗口用量。解决方案可能是一个更好的提示词，或者一个更干净的上下文窗口。时好时坏与专注之间的差别，往往只是几个 token。

<head>
  <meta property="og:title" content="The AI Skeptic’s Guide to Context Windows" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/08/18/understanding-context-windows" />
  <meta property="og:description" content="Why do AI agents forget? Learn how context windows, tokens, and Goose help you manage memory and long conversations." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/contextwindow-fa46f7a54cfb23a538d62f0e4502e19e.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="The AI Skeptic’s Guide to Context Windows" />
  <meta property="twitter:description" content="Why do AI agents forget? Learn how context windows, tokens, and Goose help you manage memory and long conversations." />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/contextwindow-fa46f7a54cfb23a538d62f0e4502e19e.png" />
</head>

---

## 我让 Goose 构建了它自己的安全 Recipe 扫描器

> 原文：https://block.github.io/goose/blog/2025-08-25-goose-became-its-own-watchdog

![Goose Recipe Safety](https://block.github.io/goose/img/goose-security-scanner.png)

> **更新：** 本文为历史存档而保留。公开的 Recipe Cookbook 提交项目已经结束，我们不再接受新的 recipe 提交。

还记得人们通过邻里间传递手写卡片来分享食谱的年代吗？你信任奶奶的苹果派食谱，因为你认识奶奶。但当陌生人开始在线上分享食谱时会发生什么？你需要有人先替你尝一尝。

这正是我们在 Goose recipe 上面临的挑战。我们在构建一本社区食谱集，让你可以放心地尝试其他用户的 Goose recipe，确信它们是安全的。但我们需要一种方式来确保每一份 recipe 都可以安全运行。

<!--truncate-->

### Headless 方案

我问 Goose：「你能构建一个系统来分析你自己的 recipe 吗？」

这种美妙的讽刺我并没有错过。我本质上是在要求我们的 AI 成为它自己的看门狗。

我给了它多得多的方向：我希望扫描器能从 GitHub Actions 运行，而且我希望扫描在 Docker 容器内完成，这样它就能在隔离环境中检查 recipe。

在对概念及其运作方式进行几轮高层次的迭代之后，Goose 构建出了一个完整的安全分析系统。它把自己容器化了，搭建了 GitHub Actions 工作流，并开始自动扫描 recipe 提交。

#### 更好的提示词带来更好的结果

我的第一次构建有点过度工程化。后来我简化了，只是给 Goose 一条「你是一名安全专家」的提示词，但如果不引导它该寻找哪些类型的东西，效果并不好。我不得不提升自己的提示词水平，加入*一定*量的具体内容，同时仍然给 Goose 灵活性去学习和成长，并在 Docker 容器内下载它认为完成任务所需的任何工具。

最后我精心构造了一系列 recipe，有些是安全的，有些可能有点风险，还有些是彻头彻尾危险的，并告诉 Goose 一些我们需要注意的必要事项。

### 它是如何运作的

这个过程乍看之下出奇地简单，但其实相当复杂——想象一只优雅的鹅在水面上游动，但水面之下它的脚正在拼命扑腾，干着大量的活儿！

当有人通过我们的 GitHub issue 模板提交 recipe 时，就会启动一次自动扫描。goose 在一个隔离的 Docker 容器中运行，运用它自己的安全专业能力加上我们的一些指引来分析该 recipe，为它打出风险评分，并把结果回帖到那个 GitHub issue 上。

整个过程只需几分钟而非几天，提交者能立即收到关于其 recipe 安全性的、透明的反馈。如果有哪里看起来不对劲，我们的团队可以复查发生了什么并采取适当的行动。

### Headless 模式下的 Goose

我们在[教程](https://goose-docs.ai/docs/tutorials/headless-goose/)和[视频](https://www.youtube.com/@goose-oss/search?query=headless)里都讲过 headless 模式，但这里快速回顾一下：headless 模式让 Goose 无需图形用户界面即可运行，使它在自动化任务中更快、更高效。它在服务器环境中表现出色——只要我们*非常*清楚地说明要遵循的指令，或者说明在无法遵循指令时的回退方案——我们不希望 Goose 卡在不知道该做什么时，留下一个半成品或损坏的结果。

我们像这样启动 Docker 容器：

```bash
docker run --rm \
    -e AIMODEL_API_KEY="$AIMODEL_API_KEY" \
    -v "$PWD/$RECIPE_FILE:/input/recipe.yaml:ro" \
    -v "$RECIPE_OUT:/output" \
```

我们传进 Docker 的第一样东西，是我们所用 AI 模型的 API key。我这里只用了「AIMODEL_API_KEY」作为占位符，但你会根据想在容器里让 Goose 使用哪个 LLM，把它改成 OPENAI_API_KEY 或 GEMINI_API_KEY 等等。

接下来，我们传入从 GitHub 拿到的用户 recipe，然后我们有用于日志和分析的「output」。

#### 看看容器内部

在容器内部，我们安装 Goose，并传入一个配置文件，说明我们想用哪个 AI 提供方和模型，再加上一份「base」recipe，告诉 Goose 如何分析用户的 recipe。那份 recipe 也在强化 Goose 作为安全专家的角色。

### 学习曲线

仅仅告诉 Goose「你是一名安全专家」是不够的。经过一番来回磨合，才教会它区分：一份 recipe 是下载了一个有用的开发工具，还是下载了某个来路不明的东西到你主目录去寻找敏感数据。

我们不得不在安全性和可用性之间微调平衡。太严格，合法的 recipe 会被标记；太宽松，危险的 recipe 会溜过去。要把握好这个平衡，需要给 Goose 展示大量安全和有风险模式的示例。我们把这些也传进 Docker 容器，而我们的「base」recipe 告诉 Goose 把它们当作灵感。

然后我们进入「headless」模式：

```bash
goose run --recipe base_recipe.yaml --no-session --params recipe_path="user_recipe.yaml" > /logs/results.txt
```

这会运行我们的「base」recipe，并跳过保存会话，因为这本来就是一次性的 GitHub action。我们的 base recipe 会寻找一个参数，指明去哪里找到用户的 recipe 文件，所以我们把这个参数传进 headless 模式，然后记录结果。这些结果随后会被我们的 GitHub action 取走，用来填充 GitHub issue 或 pull request 上的一条评论。

### 构建社区信任

真正的收获不只是这一切的自动化，而是透明度。每一次分析都是可见的、一致的，并且有解释的。社区成员可以确切看到一份 recipe 为什么通过或失败，这既建立了对系统的信任，也建立了对 recipe 本身的信任。

Goose 能捕捉人类可能漏掉的边界情况，比如微妙的混淆手法，或者只有在你分析了几十份 recipe 之后才会变得明显的模式。这就像拥有一位注重细节到完美、永远不会疲惫的安全专家。

### 用 AI 审查 AI，来审查提交

有时候，解决一个潜在 AI 问题的最好办法就是用更多 AI。Goose 比任何人类审查者都更理解 Goose 的行为模式。它知道自动化任务的合法方式，并能发现某样东西何时偏离了这些模式。用 Goose 来构建这个扫描器，不仅为制作这个工具节省了时间，也让我们团队不必再亲手审查每一份 recipe，是一次生产力上的胜利。

在当时，任何人都可以提交 recipe，并且知道它会得到公正、彻底的审查。而当一份 recipe 获得安全批准时，批准它的是 goose 本身。

<iframe class="aspect-ratio" src="https://www.youtube.com/embed/Jtw_FxF3Iug" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<head>
  <meta property="og:title" content="I had Goose Build its Own Secure Recipe Scanner" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/kljaslkjasd" />
  <meta property="og:description" content="Goose headless mode runs a containerized scanner for community recipe submissions." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/goose-security-scanner-7fbe93f4a738fed2002e656fe66e715f.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="I had Goose Build its Own Secure Recipe Scanner" />
  <meta property="twitter:description" content="Goose headless mode runs a containerized scanner for community recipe submissions." />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/goose-security-scanner-7fbe93f4a738fed2002e656fe66e715f.png" />
</head>

---

## MCP-UI：智能体界面的未来

> 原文：https://block.github.io/goose/blog/2025-08-25-mcp-ui-future-agentic-interfaces

![mcp ui](https://block.github.io/goose/img/mcpui-goose.png)

AI 智能体对话中无尽文字墙的日子已经屈指可数了。如果不用读一大段产品描述，而是可以浏览一个精美的交互式商品目录，会怎样？如果预订航班座位就像在你偏好的位置上点击一张可视化座位图那样简单，会怎样？这不是科幻。它正随着 MCP-UI 发生。

在最近一期 [Wild Goose Case 节目](https://www.youtube.com/live/GS-kmreZDgU)中，我们与 MCP-UI 的创作者、来自 Monday.com 的 Ido Salomon 和 Liad Yosef，以及 Block 自家的 Andrew Harvard 一起深入探讨了 MCP-UI，探索这项开创性技术如何重塑智能体界面的未来。

<!-- truncate -->

### 纯文本界面的问题

说实话，我们都有过这种经历。你让 AI 智能体帮你买鞋，结果收到一大段文字，里面是产品名、价格和描述。然后你不得不复制粘贴 URL、打开多个标签页，基本上所有活儿都得你自己干。这从一开始就违背了拥有 AI 助手的初衷。

正如 Ido 在我们的对话中所说：「我想每个人都遇到过那种一大堆文字的情况，然后想这太糟糕了，我为什么得把那些全打出来，然后差不多就愤而弃用 ChatGPT 了。」

现实是，基于文本的界面对早期采用者和技术用户来说没问题，但它们不是未来。它们当然也不会适合所有人——包括我们的妈妈们，她们越来越多地使用 AI 助手，但不该被迫去应对复杂的文本响应。

### MCP-UI 登场：弥合鸿沟

MCP-UI（Model Context Protocol User Interface）代表了我们思考 AI 智能体交互方式的一次根本性转变。MCP-UI 不强迫用户通过文本消费一切，而是让丰富的交互式 Web 组件可以直接嵌入到智能体对话中。

其核心理念的精妙之处在于简单：**既然我们能用 AI 增强数十年的 Web UI/UX 专业积累，为什么要抛弃它？**

正如 Liad 所解释的：「我们在 Web 上拥有十多年面向人类的界面，它们是为人类的认知局限和需求而构建并不断完善的，智能体让我们把这一切都扔掉，这不合理。」

### MCP-UI 如何运作

MCP-UI 的核心既是一个协议，也是一个 SDK，它使以下成为可能：

1. **丰富的 UI 组件**：不再是文本描述，你得到的是交互式目录、座位图、预订表单等等
2. **品牌保留**：像 Shopify 这样的公司可以保持其品牌和用户体验完好无损
3. **无缝集成**：UI 组件通过安全、沙箱化的 iframe 与智能体通信
4. **跨平台兼容**：同一个 UI 可以跨不同的 AI 智能体和平台工作

魔法通过 MCP 规范中的嵌入式资源发生。当你与一个支持 UI 的 MCP 服务器交互时，它不再只是返回文本，而是可以返回直接在你的智能体界面中渲染的丰富 UI 组件。

### 实战中的真实示例

在我们的演示中，我们看到了一些令人难以置信的 MCP-UI 实战示例：

#### 购物变得可视化
用户不再需要读产品描述，而是看到一个带有图片、价格和交互元素的精美 Shopify 目录。点击商品就能把它们加入购物车，就像常规的电商体验一样，但无缝嵌入在 AI 对话中。

#### 旅行规划焕然一新
我们看到用户可以通过点击一张可视化座位图来选择飞机座位，然后让智能体自动查询目的地城市的天气信息——全程都不用离开对话，也不用输入额外命令。

#### 餐厅发现
演示展示了用户如何浏览本地餐厅，卡片上带有照片、评分和菜单，然后直接通过交互式界面下单，同时始终保持与 AI 智能体的对话流。

### 技术基础

从技术角度看，MCP-UI 优先考虑安全性和隔离性。UI 组件在沙箱化的 iframe 中渲染，只能通过 post message 与宿主通信。这确保了第三方 UI 代码无法访问或操控父应用。

当前实现支持几种内容类型：
- **外部 URL**：嵌入 iframe 中的现有 Web 应用
- **原始 HTML**：带 CSS 和 JavaScript 的自定义 HTML 组件
- **Remote DOM**：在独立 worker 中渲染的 UI，以增强安全性

对开发者来说，上手出奇地简单。正如 Andrew 所演示的，你可以从这样基础的东西开始：

```javascript
return createUIResource({
  type: 'html',
  content: '<h1>Hello World</h1>'
});
```

### 利益相关方生态

MCP-UI 的成功取决于几个关键利益相关方：

1. **智能体开发者**（比如 Goose 团队）：需要在其平台中实现 MCP-UI 支持
2. **MCP 服务器开发者**：构建 UI 组件并将它们与现有服务集成
3. **服务提供方**（比如 Shopify、Square）：为其平台创建丰富的界面
4. **终端用户**：从更直观、更可视化的 AI 交互中受益

这种方法的妙处在于，它创造了一种网络效应。一旦实现，一个 Shopify MCP-UI 组件就能在所有兼容的智能体上工作——从 Goose 到 VS Code 扩展，再到未来的移动 AI 助手。

### 展望未来：未来是可视化的

MCP-UI 的影响远不止于更漂亮的界面。我们正在看到：

#### 无障碍革命
正如 Ido 指出的：「还有什么比一个了解你、并按照你的偏好构建 UI 的智能体更无障碍的呢？你不需要依赖世界上的每一个 Web 应用去支持或构建那个东西。」

#### 生成式 UI
未来的版本可能会超越静态 HTML，转向为单个用户的需求、偏好和无障碍要求量身定制的 AI 生成界面。

#### 多模态体验
该协议并不局限于可视化界面——它可以延伸到语音交互、移动原生组件，甚至是我们尚未想象出的全新交互范式。

#### 跨平台标准化
与其每家公司为每个 AI 平台构建独立的集成，MCP-UI 创建了一个到哪都能用的标准。

### 采用方面的挑战

技术已经就绪，但采用是下一个前沿。正如团队所强调的，现在这更多是一个采用问题，而不是技术问题。好消息呢？主要玩家已经加入了。Shopify 已经为其所有店铺上线了 MCP 支持，为电商体验提供了一个巨大的真实世界试验场。当然，MCP-UI 在 Goose 中也得到支持。

对有兴趣贡献的开发者来说，重点在于：
- 构建解决实际用户问题的真实应用
- 基于真实世界需求扩展规范
- 创建更好的工具和 SDK，以降低入门门槛

### 快速开始

如果你对 MCP-UI 感到兴奋，想开始试验，可以从这里入手：

1. **查看文档**：MCP-UI 团队创建了[全面的文档和示例](https://mcpui.dev/)
2. **加入社区**：有一个活跃的 [Discord 服务器](https://discord.gg/4ww9QnJgCp)用于协作和讨论
3. **从简单开始**：拿一个现有的 MCP 服务器，给它加上 UI 资源
4. **用 Goose 试验**：试试[在 Goose 中使用 MCP-UI](https://block.github.io/goose/docs/guides/interactive-chat/mcp-ui)，看看实际效果

### 底线

MCP-UI 代表着从文字繁重的 AI 交互，向丰富、可视化、直观体验的一次根本性转变。

当你浏览商品时，你想看到图片并与目录交互。当你预订旅行时，你想看到可视化的座位图和行程。当你管理日历的时候，你想看到熟悉、直接能用的界面模式。

MCP-UI 让这一切成为可能，同时保留了 AI 智能体的对话特性。它是我们所知的 Web 与我们所构建的智能体未来之间的桥梁。

与 AI 交互的未来，依赖于更聪明的界面。而有了 MCP-UI，那个未来已经到来。

---

*想看看 MCP-UI 的实际效果吗？查看下面的完整 Wild Goose Chase 节目，并加入我们的社区，开始构建智能体界面的未来。*

<iframe src="https://www.youtube.com/embed/GS-kmreZDgU" title="MCP-UI: The Future of Agentic Interfaces" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen class="aspect-ratio"></iframe>

*来 [Discord](https://discord.gg/n8R5VaWDAn) 参与讨论，并跟随我们的进展，看我们如何继续拓展 AI 智能体的可能性边界。*

<head>
  <meta property="og:title" content="MCP-UI: The Future of Agentic Interfaces" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/08/25/mcp-ui-future-agentic-interfaces" />
  <meta property="og:description" content="Discover how MCP-UI is revolutionizing AI agent interactions by bringing rich, interactive web components directly into agent conversations, making AI more accessible and intuitive for everyone." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/mcpui-goose-44f248ede0eb5d2e0bddccf76e98b07e.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="MCP-UI: The Future of Agentic Interfaces" />
  <meta property="twitter:description" content="Discover how MCP-UI is revolutionizing AI agent interactions by bringing rich, interactive web components directly into agent conversations, making AI more accessible and intuitive for everyone." />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/mcpui-goose-44f248ede0eb5d2e0bddccf76e98b07e.png" />
</head>

---

## 用 MCP-UI 实现自动可视化

> 原文：https://block.github.io/goose/blog/2025-08-27-autovisualiser-with-mcp-ui

![blog banner](https://block.github.io/goose/img/autovis-banner.png)

数据可视化在 Goose 中迎来了一次重大升级。有了新的 MCP-UI 自动可视化（auto visualiser）功能，你不再需要手动请求图表、图形或数据的可视化呈现。Goose 现在会自动检测数据何时适合可视化，并直接在你的对话中渲染交互式可视组件。


<!-- truncate -->

### 什么是 Auto Visualiser？

[Auto Visualiser](https://block.github.io/goose/docs/mcp/autovisualiser-mcp) 是一个内置扩展，它与 [Goose 的 MCP-UI 系统](https://block.github.io/goose/docs/guides/interactive-chat/)集成，在你工作时自动生成数据的可视化呈现。

![switch](https://block.github.io/goose/img/switch.png)

一旦开启，一大批可视化工具就会作为工具提供出来，它们会在合适的时候被自动调用，比如把东西展示成雷达图，或「桑基」图：

![sankey](https://block.github.io/goose/img/sankey.png)

你也可以显式地要求可视化，甚至指定你想要的风格，Goose 会尝试塑造你的数据，然后把它内联渲染出来。这由 [MCP-UI](https://mcpui.dev/) 这一新兴标准驱动，它让 MCP 服务器能够构建一个可视化（在这个例子里使用了 d3.js 之类的库）并将其内联渲染。

autovisualiser 会分析数据模式，并自动建议最合适的可视化类型。我最喜欢的是 treemap（矩形树图），它是一种查看事物相对大小的绝佳方式，而饼图在这方面可能会产生误导。它还具有交互性，你可以逐层下钻。

![tree map](https://block.github.io/goose/img/treemap.png)


当然，如果你愿意，也可以诉诸「想象力匮乏者的最后避难所」，去把天气画成图：

![weather](https://block.github.io/goose/img/weather.png)

注意这是一个早期功能，其功能可能会变化、也可能差异很大（就像 MCP-UI 一样）。这是正在兴起的生成式 UI 的一个早期例子，尽管在这个例子里，模板是预先生成的，数据被动态匹配到当前会话然后（从本地资源）显示出来。


### 可视化类型

目前它可以展示几大类东西：

* 桑基图（sankey diagrams）
* 雷达图（radar charts）
* 弦图（chord diagrams）
* 环形图/饼图（donut/pie charts）
* 条形图和通用图表
* treemap 可视化（瓦片）
* 地图（把东西放到地理地图上）

---

*准备好看看你的数据了吗？在 Goose 中[启用 Auto Visualiser 扩展](https://block.github.io/goose/docs/mcp/autovisualiser-mcp#configuration)。*

<head>
  <meta property="og:title" content="Auto Visualiser with MCP-UI" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/08/27/autovisualiser-with-mcp-ui" />
  <meta property="og:description" content="How Goose now automatically renders visual representations of data as you interact with it, powered by the new MCP-UI feature" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/autovis-banner-c6e34e561b2fad329ea00024c301e910.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Auto Visualiser with MCP-UI" />
  <meta property="twitter:description" content="How Goose now automatically renders visual representations of data as you interact with it, powered by the new MCP-UI feature" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/autovis-banner-c6e34e561b2fad329ea00024c301e910.png" />
</head>

---

## 你的第一次 goose 体验，我们请客

> 原文：https://block.github.io/goose/blog/2025-08-27-get-started-for-free-with-tetrate

![](https://block.github.io/goose/img/tetrate-header.png)

你不该需要一张信用卡才能用 goose 玩 vibe coding。虽然 goose 完全免费使用，但现实是大多数高性能的 LLM 并不是。你想在不烧钱、不折腾的情况下体验 goose 的实际效果。我们一直在思考，如何让 goose 新用户的这第一步更轻松。

正因如此，我们对最新的提供方集成感到非常兴奋：[Tetrate 的 Agent Router Service](https://router.tetrate.ai)。新的 goose 用户可以获得 10 美元额度，在 Tetrate 平台上用任意模型配合 goose 使用。

<!--truncate-->

我们升级了引导流程。Tetrate Agent Router 现在作为新用户的[推荐安装选项](https://block.github.io/goose/docs/getting-started/installation#set-llm-provider)出现。选择 Tetrate 会带你走一遍 OAuth 账号创建流程，然后把你送回 goose，10 美元额度已经就绪。

![fresh install](https://block.github.io/goose/img/welcome.png)


这项集成为 goose 用户带来：
* **即时访问**模型，无需手动设置
* **10 美元额度**，无需付费墙即可开始构建
* **统一的模型层**，由 Tetrate 提供支持
* **稳定的路由**，构建于 [Envoy](https://www.envoyproxy.io/) 之上——一个面向大规模系统的开源代理


### Tetrate 的 Agent Router Service

Tetrate 的 Agent Router Service 提供对一大批 AI 模型的统一访问，涵盖从开源选项到 GPT-5、Sonnet-4 和 Grok-4 这类前沿模型。

#### 从云基础设施到 AI 模型路由

Tetrate 把多年在路由和基础设施方面的专长带到了 AI 领域。作为 Istio 和 Envoy 等开源项目的重要贡献者，他们懂得如何构建可靠、可扩展的路由系统。现在，他们正把同样的专长应用到 LLM 流量管理上。

LLM 请求本质上是无状态的，这使它们非常适合跨多个提供方和模型的智能路由。这让你可以针对成本、速度、可用性或质量进行优化，甚至使用多个模型来交叉验证结果。这个领域的术语仍在沉淀。goose 为了一致性把 Tetrate 称为「提供方」，尽管底层它是一个连接其他提供方的路由服务。那一层抽象掉了模型选择、认证和主机配置，让你的设置保持干净。

### 为什么这次合作很重要

我们的目标很简单：让 goose 立即对所有人可用。这意味着移除入门门槛。Tetrate 慷慨的额度提供和无缝集成，恰好帮我们实现了这一点。

它也反映了 Tetrate 对开源、以及让全球开发者更容易进行 AI 开发的持续承诺。

### 探索完整的模型目录

虽然 goose 默认自动配置为 Sonnet-4，但你可以通过界面访问 Tetrate 的整个模型目录：

![providers](https://block.github.io/goose/img/providers.png)
![gpt5](https://block.github.io/goose/img/gpt5.png)

浏览并从各种选项中挑选，包括：
- **开放权重模型**（比如 Kimi/K2），已托管、开箱即用
- 来自各提供方的**前沿模型**
- 为不同用例优化的**专用模型**

:::tip 实用技巧
 想兼得两者之长？用强大的推理模型处理复杂策略，用更快的默认模型做执行。参见[多模型指南](https://block.github.io/goose/docs/guides/multi-model/)，只在需要时获得强大推理能力，同时省下时间和额度。
:::

---

感谢 Tetrate 支持开源，让 AI 开发更容易触达！

**你还在等什么？**[开始使用 goose](https://block.github.io/goose/)

*有问题？* 浏览我们的[文档](https://block.github.io/goose/docs/category/guides)，看看[博客](https://block.github.io/goose/blog)，或者来我们的 [Discord](https://discord.gg/n8R5VaWDAn) 和 [GitHub Discussions](https://github.com/aaif-goose/goose/discussions) 参与讨论。我们很欢迎你加入。

<head>
  <meta property="og:title" content="Your First goose Experience Is On Us" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/08/27/get-started-for-free-with-tetrate" />
  <meta property="og:description" content="New goose users receive $10 in Tetrate Agent Router credits for instant access to multiple models including GPT-5 and Sonnet-4." />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/tetrate-header-9e2afbf5d1ce961d5f25547a7439c65f.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="Your First goose Experience Is On Us" />
  <meta property="twitter:description" content="New goose users receive $10 in Tetrate Agent Router credits for instant access to multiple models including GPT-5 and Sonnet-4" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/tetrate-header-9e2afbf5d1ce961d5f25547a7439c65f.png" />
</head>

---

## 当 AI 成为你的新团队成员：Goose Janitor 的故事

> 原文：https://block.github.io/goose/blog/2025-08-28-ai-teammate

![blog banner](https://block.github.io/goose/img/goose-janitor.png)

多年来，Block 的 iOS 工程师们一直感受到技术债务不断累积的痛苦。功能开关（feature flag）就是一个具体的例子。即使成功上线，它们也往往滞留在代码库中，每一个都是一份拖慢开发的小小负担。

2025 年初，随着对开发者加速的重新聚焦，Foundation iOS 团队决定组织「功能开关清除月」——让这个大型 iOS 单体仓库中的各团队聚到一起，删除*可能多达数十万行的死代码*。

随着 Goose recipe 恰好在同一时间发布，团队琢磨着：一个专门的 recipe 能不能助力这项努力？团队里一位较新的 iOS 工程师 [Gemma Barlow](https://www.linkedin.com/in/gemmakbarlow/) 想一探究竟。


<!-- truncate -->


### 阶段 1：让知识可被 AI 访问

Gemma 的第一步，是利用现有的 `.mdc`、`.goosehints` 以及其他符号链接的上下文文档体系，来记录如何安全地从仓库中移除功能开关。

她添加了文档，让 AI 智能体能够获取足够的上下文，以准确地完成移除工作。

### 阶段 2：跨代际的验证

鉴于 AI 文档被设计为能与 Block 使用的各种工具配合工作，还需要进一步的迭代和验证。经过数周的测试和试验，最终确认这种方法准确到足以有用，*而且*它能处理已经累积下来的三代不同的功能开关实现：

- 团队很久很久以前使用的超级遗留开关
- 较新但如今已算旧的遗留开关
- 当前的功能开关实现

仅这份文档本身就能帮助团队更快地清理。但现在，AI 在大多数场景下也能理解并安全地驾驭真实世界遗留系统的复杂性，这是开发者速度的一次胜利！🎉

### 阶段 3：构建一个 AI 团队成员

这是很大的进展。Gemma 本可以到此为止。

但她没有，而是利用 Goose recipe 创建了 **Goose Janitor**。


Goose Janitor 扮演一位新的 AI 团队成员，其职责是在我们实验完成后整理代码。它深受现有 [Goose recipe](https://block.github.io/goose/recipes/detail/?id=clean-up-feature-flag) 以及 Block 其他地方的内部讨论和实验的启发。它是这样运行的：

```bash
goose run \
--recipe .goose/recipes/goose-janitor-flag-removal.yaml \
--params feature_flag_key=log-observer-is-enabled \
--params variant_to_remain=true \
--params create_pr=false
```

这份 recipe：
- 完全自主运行（无需人工干预）
- 处理复杂度各异的不同开关实现
- 尝试为过时的代码路径做重构
- 可以通过 GitHub CLI 自动创建草稿拉取请求
- 集成 [Xcode Index MCP](https://github.com/block/xcode-index-mcp)，以深入理解 iOS 项目
- 在本地规划、实现、构建和测试，以提高开关移除结果的准确性


### 更大的图景：AI 优先的开发

像 Goose Janitor 这样的 recipe，代表了我们对软件开发中 AI 的思考方式的一次根本性转变。它们可以被部署来：

- 理解复杂的遗留代码库
- 做出安全的重构决策
- 与现有开发工作流无缝集成
- 带来开发者速度的提升
- 在大型代码库中扩展

Block 的团队有信心，Goose Janitor 会在生产规模的清理工作中派上用场。

这正是 AI 应该处理的那类工作：枯燥、重复，但需要深厚的代码库知识。通过自动化他们工作中的一部分，开发者可以专注于他们最擅长的事，也就是构建新功能和解决新问题，同时让 AI 保持代码库干净、可维护。


### AI 优先的心态

这个故事展示了面向遗留代码库的 AI 优先方法在实践中是什么样子。

从让部落知识可被 AI 访问开始。测试并验证 AI 确实能以足够高的准确性处理这种复杂性，证明它有用。即便复杂情况需要人工干预，由 AI 完成的第一遍也能成为生产力的有用助推。构建能跨团队扩展的自动化，把人的精力集中在高价值的创造性工作上。


### 接下来是什么？

Goose Janitor 的成功打开了迷人的可能性。还有哪些形式的技术债务能从这种方法中受益？我们还能构建哪些其他「AI 团队成员」来处理常规但知识密集型的工作？

当我们迈向 AI 优先的未来时，像 Gemma 这样的故事为我们指明了道路。不只是使用 AI 工具，而是系统性地思考如何让我们的代码库和流程为 AI 做好准备。

软件开发的未来是混合团队，AI 智能体是自主的贡献者，处理那些让系统保持健康的维护工作，而人类专注于构建未来。

---

想根据自己的需求调整这份 base recipe 吗？来看看我们 Recipe Cookbook 中的 [Clean up feature flag](https://block.github.io/goose/recipes/detail/?id=clean-up-feature-flag)！

<head>
  <meta property="og:title" content="When AI Becomes Your New Team Member: The Story of Goose Janitor" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/2025/08/28/ai-teammate" />
  <meta property="og:description" content="How an engineering team is trialling autonomous AI-powered technical debt cleanup" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/goose-janitor-129889884d9265d001fe12cbfde03d57.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta property="twitter:title" content="When AI Becomes Your New Team Member: The Story of Goose Janitor" />
  <meta property="twitter:description" content="How an engineering team is trialling autonomous AI-powered technical debt cleanup" />
  <meta property="twitter:image" content="https://goose-docs.ai/assets/images/goose-janitor-129889884d9265d001fe12cbfde03d57.png" />
</head>
