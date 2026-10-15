# goose 官方文档中文手册：第 07 章　会话、上下文管理与任务执行

## 管理会话

> 原文：https://block.github.io/goose/docs/guides/sessions

<h1 className={styles.pageTitle}>管理会话</h1>
<p className={styles.pageDescription}>
  会话是你与 goose 之间持续的交互。每个会话都维护着上下文和对话历史，使 goose 能够理解你正在进行的工作并提供相关的协助。
</p>

<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>📚 文档与指南</h2>
  <div className={styles.cardGrid}>
    <Card 
      title="会话管理"
      description="了解如何启动、恢复或搜索会话，以及执行其他会话管理任务。"
      link="https://block.github.io/goose/docs/guides/sessions/session-management"
    />
    <Card 
      title="会话内操作"
      description="探索你可以在会话期间用来分享信息并与 goose 沟通的功能。"
      link="https://block.github.io/goose/docs/guides/sessions/in-session-actions"
    />
    <Card 
      title="智能上下文管理"
      description="使用有助于管理上下文和对话限制的功能，保持高效的会话。"
      link="https://block.github.io/goose/docs/guides/sessions/smart-context-management"
    />
  </div>
</div>
<div className={styles.categorySection}>
  <h2 className={styles.categoryTitle}>📝 精选博客文章</h2>
  <div className={styles.cardGrid}>
    <Card
      title="与 goose 协作的 6 个必备技巧"
      description="了解专注的会话、循序渐进的指导以及打磨你的提示词，如何带来更高效的会话。"
      link="https://block.github.io/goose/blog/2025/03/06/goose-tips"
    />
    <Card
      title="AI 提示词入门 101：如何从你的 AI Agent 获得最佳回复"
      description="通过为你的提示词增加结构，让你的会话更有效。"
      link="https://block.github.io/goose/blog/2025/03/19/better-ai-prompting"
    />
    <Card
      title="AI 怀疑论者的上下文窗口指南"
      description="了解上下文窗口、token 以及 goose 如何帮助你管理记忆和长对话。"
      link="https://block.github.io/goose/blog/2025/08/18/understanding-context-windows"
    />
  </div>
</div>

---

## 会话管理

> 原文：https://block.github.io/goose/docs/guides/sessions/session-management

会话是你与 goose 之间单次、连续的交互，为你提供一个提问和提示操作的空间。本指南介绍如何管理会话的生命周期。

### 启动会话

:::info 首次设置
在你的首次会话中，goose 会提示你[设置 LLM（大型语言模型）提供方](https://block.github.io/goose/docs/getting-started/installation#set-llm-provider)。
:::

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
        打开 goose 后，你会看到会话界面已准备就绪。只需在输入框中输入&mdash;[或说出](https://block.github.io/goose/docs/guides/sessions/in-session-actions#voice-dictation "了解如何启用语音听写")&mdash;你的问题、请求或指令，goose 会立即开始工作。

        要开始一个新的聊天会话：

        1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮以打开侧边栏
        2. 在侧边栏中点击 `Home` 或 `Chat`
        3. 从聊天框中发送你的第一条提示词

        goose Desktop 支持在同一窗口中处理多个活动聊天会话。你的新会话会添加到侧边栏的 `Chat` 部分，因此你可以在最近 10 个会话之间快速切换。只需点击某个会话即可在该会话中[继续工作](#resume-session)。
        
        要更改工作目录，请点击应用底部的 <FolderDot className="inline" size={16} /> 目录切换器。

        :::info 在新窗口中启动会话
        要在新窗口中启动会话，请点击左上角的 <AppWindow className="inline" size={16} /> 按钮。在你发送第一条提示词后，新会话会添加到侧边栏的 `Chat` 部分。

        在 macOS 上，你还可以使用 goose 的 Dock 图标快速启动会话：
            - **拖放**一个文件夹到 goose 图标上，即可在该目录中打开一个新会话
            - **右键点击**goose 图标并选择 `New Window`，即可在你最近使用的目录中打开一个新会话
        :::
        
        #### 键盘快捷键
        
        你也可以使用键盘快捷键来启动新会话或管理 goose 窗口。
        
        | 操作 | macOS | Windows/Linux |
        |--------|-------|---------------|
        | 使用[快速启动器](#quick-launcher)新建会话 | `Cmd+Option+Shift+G` | `Ctrl+Alt+Shift+G` |
        | 在当前目录中新建会话 | `Cmd+N` | `Ctrl+N` |
        | 在当前目录中新建会话（同一窗口） | `Cmd+T` | `Ctrl+T` |
        | 在不同目录中新建会话 | `Cmd+O` | `Ctrl+O` |
        | 切换侧边栏 | `Cmd+B` | `Ctrl+B` |
        | 打开设置 | `Cmd+,` | `Ctrl+,` |
        | 聚焦 goose 窗口 | `Cmd+Option+G` | `Ctrl+Alt+G` |
        | 保持 goose 窗口始终置顶 | `Cmd+Shift+T` | `Ctrl+Shift+T` |
        
        #### 自定义键盘快捷键
        
        你可以在**设置**菜单中自定义这些键盘快捷键：
        1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮以打开侧边栏
        2. 点击 `Settings`
        3. 点击 `Keyboard` 标签页
        
        对全局快捷键（聚焦窗口、快速启动器）的更改会立即生效。对应用快捷键（新建聊天、设置等）的更改需要重启 goose。
        
        #### 快速启动器
        通过在弹出框中输入提示词来启动一个新会话：
        1. 按 `Cmd+Option+Shift+G`（macOS）或 `Ctrl+Alt+Shift+G`（Windows/Linux）打开弹出框
        2. 输入你的提示词并按 `Enter`

        会话会在新的 goose 窗口中打开你最近打开过的目录。

    </TabItem>
    <TabItem value="cli" label="goose CLI">
        在终端中，导航到你想从中启动的目录，并运行 [session](https://block.github.io/goose/docs/guides/goose-cli-commands#session-options) 命令：
        ```sh
        goose session 
        ```

    </TabItem>
</Tabs>

### 命名会话
<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
        会话的显示名称会根据你初始提示词的上下文自动生成。会话名称有助于你识别 goose 会话，从而在活动会话之间切换或[恢复会话](#resume-session)。

        你可以在会话创建后编辑会话名称：

        1. 在侧边栏中点击 <History className="inline" size={16} /> `Session History`
        2. 将鼠标悬停在你想要重命名的会话上
        3. 点击会话卡片上出现的 <Edit2 className="inline" size={16} /> 按钮
        4. 在打开的 "Edit Session Description" 模态框中：
           - 输入新的会话描述（最多 200 个字符）
           - 按 `Enter` 保存，或按 `Escape` 取消
           - 或者点击 `Save` 或 `Cancel` 按钮
        5. 成功提示通知会确认此次更改

        会话名称会出现在侧边栏的 `Chat` 部分、`Window` 菜单，以及 Dock（macOS）或任务栏（Windows）菜单中。

    </TabItem>
    <TabItem value="cli" label="goose CLI">
        goose 会话会根据你初始提示词的上下文被赋予一个自动生成的名称。

        如果你想提供特定的会话名称，可以在启动会话时指定。例如，要把会话命名为 "react-migration"，请运行：

        ```sh
        goose session --name react-migration
        ```

        要重命名一个现有会话，请使用 `session rename` 子命令：

        ```sh
        goose session rename --session-id 20260213_9 --new-name my-new-name
        ```

        如果你省略会话 ID，goose 会以交互方式提示你选择一个会话：

        ```sh
        goose session rename --new-name my-new-name
        ```

        如果你想确认会话名称，请运行：

        ```sh
        goose session list -l 1
        ```

        示例结果：
        
        ```text
        Available sessions:
        20260213_9 - react-migration - 2026-02-13 16:20:37 UTC
        ```

        在上面的输出中，`20260213_9` 是会话 ID。会话 ID 使用 `YYYYMMDD_<COUNT>` 格式。许多 [goose CLI 命令](https://block.github.io/goose/docs/guides/goose-cli-commands)允许你通过名称（`--name` / `-n`）来标识会话，作为 `--session-id` 的替代方案。
    </TabItem>
</Tabs>

:::tip 禁用 AI 生成的会话命名
使用 [`GOOSE_DISABLE_SESSION_NAMING`](https://block.github.io/goose/docs/guides/environment-variables#session-management) 来保留默认名称，而不是调用模型来生成名称（在 CI/无头工作流中很有用）。goose Desktop 中的默认名称是 "New Chat"，goose CLI 中的默认名称是 "CLI Session"。
:::

### 退出会话
请注意，会话在你退出时会自动保存。
<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
    要退出会话，只需关闭应用即可。
    </TabItem>    
    <TabItem value="cli" label="goose CLI">
        要退出会话，请输入 `exit`。或者，你也可以按住 `Ctrl+C` 来退出会话。

        你的会话将存储在 goose 的[本地 SQLite 数据库](https://block.github.io/goose/docs/guides/logs#session-records)中。
    </TabItem>
</Tabs>

### 搜索会话

搜索允许你在会话中查找特定内容，或查找特定的会话。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

    你可以使用键盘快捷键和搜索栏按钮在 goose Desktop 中搜索会话。

    | 操作 | macOS | Windows/Linux |
    |--------|-------|---------------|
    | 打开搜索 | `Cmd+F`  | `Ctrl+F`  |
    | 下一个匹配项 | `Cmd+G` 或 `↓` | `Ctrl+G` 或 `↓` |
    | 上一个匹配项 | `Shift+Cmd+G` 或 `↑` | `Shift+Ctrl+G` 或 `↑` |
    | 使用所选内容进行查找 | `Cmd+E` | n/a |
    | 切换区分大小写 | `Aa` | `Aa` |
    | 关闭搜索 | `Esc` 或 `X` | `Esc` 或 `X` |

    :::tip 自定义搜索快捷键
    你可以在**设置** → **Keyboard** 标签页中[自定义](#keyboard-shortcuts)查找、查找下一个和查找上一个的键盘快捷键。
    :::

    :::info 不支持正则表达式或操作符
    不支持在搜索文本中使用正则表达式或搜索操作符。
    :::

    支持以下场景：

    #### 在当前会话中搜索
    
    要在你当前会话中查找特定内容：

    1. 使用 `Cmd+F` 打开搜索栏
    2. 输入你的搜索词
    3. 使用快捷键和搜索栏按钮来浏览结果

    #### 跨会话搜索
    
    要跨你所有的会话搜索对话历史：

    1. 在侧边栏中点击 <History className="inline" size={16} /> `Session History`
    2. 使用 `Cmd+F`（或 `Ctrl+F`）打开搜索栏
    3. 输入你的搜索词
    4. 使用键盘快捷键和搜索栏按钮来浏览结果（不支持 `Cmd+E`）

    这会搜索你对话中消息的内容。搜索仅限于跨会话最近 10 条匹配的消息。如果你的搜索词出现在许多消息中，搜索只会返回一部分会话。

    :::tip 直接询问 goose
    你也可以使用内置的 [Chat Recall 扩展](https://block.github.io/goose/docs/mcp/chatrecall-mcp)来让 goose 搜索你的对话历史：
    - "Find my earlier conversation about React hooks from last week"
    - "Show me sessions where I worked on database migrations"
    :::

  </TabItem>
  <TabItem value="cli" label="goose CLI">

    #### 在当前会话中搜索

    搜索功能由你的终端界面提供。请使用适合你环境的快捷键：

    | 终端 | 操作系统 | 快捷键 |
    |----------|-----------------|-----------|
    | iTerm2 | macOS | `Cmd+F` |
    | Terminal.app | macOS | `Cmd+F` |
    | Windows Terminal | Windows | `Ctrl+F` |
    | Linux Terminal | Linux | `Ctrl+F` |

    要在你当前会话中查找特定内容：

    1. 使用该快捷键打开搜索栏
    2. 输入你的搜索词
    3. 使用快捷键和搜索栏按钮来浏览结果

    :::info
    你特定的终端模拟器可能使用不同的键盘快捷键。请查看你终端的文档或设置以了解搜索命令。
    :::

    #### 搜索所有会话内容
    
    要跨你所有的会话搜索对话内容，请启动一个 goose 会话并直接询问：

    - "Find my earlier conversation about React hooks from last week"
    - "Show me sessions where I worked on database migrations"

    goose 会搜索你的会话历史，并展示相关对话以及来自匹配会话的上下文。
    
    :::info
    此功能需要启用内置的 [Chatrecall 扩展](https://block.github.io/goose/docs/mcp/chatrecall-mcp)。
    :::

    #### 直接搜索会话数据
    
    [`session list`](https://block.github.io/goose/docs/guides/goose-cli-commands#session-list-options) 子命令搭配支持的选项，对某些搜索操作会很有用。

    你也可以直接查询 SQLite 数据库：

    ```bash
    # Search session descriptions
    sqlite3 ~/.local/share/goose/sessions/sessions.db \
      "SELECT id, description FROM sessions WHERE description LIKE '%your search term%';"

    # Search by working directory
    sqlite3 ~/.local/share/goose/sessions/sessions.db \
      "SELECT id, description, working_dir FROM sessions WHERE working_dir LIKE '%project-name%';"

    # List recent sessions
    sqlite3 ~/.local/share/goose/sessions/sessions.db \
      "SELECT id, description, created_at FROM sessions ORDER BY created_at DESC LIMIT 10;"
    ```

    :::info 会话存储迁移
    从 1.10.0 版本开始，goose 使用 SQLite 数据库（`sessions.db`）而不是单独的 `.jsonl` 文件。旧版 `.jsonl` 文件仍保留在磁盘上，但不再由 goose 管理。
    :::

  </TabItem>
</Tabs>

### 恢复会话

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
    
    你可以在侧边栏中的活动会话之间切换，或从历史记录中恢复任何会话。
    
    #### 在活动会话之间切换

    goose Desktop 允许你在同一窗口中的多个聊天会话之间切换。你可以在一个会话中开始一项任务，切换到另一个会话做一些工作，并在任务完成时返回到第一个会话。

    你最近的会话（最多 10 个）可在侧边栏中快速访问：

    1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮以打开侧边栏
    2. 在 `Chat` 部分中，点击任意会话即可切换到它
    
    视觉指示器可帮助你跟踪会话状态：
    - **蓝色旋转图标** - 会话正在主动处理请求
    - **绿点** - 会话在你查看其他会话期间完成了一项任务
    - **红点** - 会话遇到了错误

    此外，从 Recipe 启动的会话会显示 <ChefHat className="inline" size={16} /> 图标。

    :::tip
    你可以[重命名会话](#name-session)，以便更容易地识别特定的会话。
    :::

    #### 从会话历史中恢复

    要查找并恢复超出你最近 10 个的会话：

    1. 在侧边栏中点击 <History className="inline" size={16} /> `Session History`
    2. 找到你想恢复的会话。goose 提供[搜索功能](#search-sessions)来帮助你找到该会话。
    3. 选择恢复方式：
       - 点击 `Resume` 在当前窗口中继续
       - 点击 `New Window` 在新窗口中打开

    </TabItem>
    <TabItem value="cli" label="goose CLI">
        要恢复你最近的会话，可以运行以下命令：

        ```
         goose session -r
        ```

        要恢复一个特定的会话，请运行以下命令：

        ```
        goose session -r --name <name>
        ```
        例如，要恢复名为 `react-migration` 的会话，你可以运行：

        ```
        goose session -r --name react-migration
        ```
    </TabItem>
</Tabs>

在 goose Desktop 中创建的会话可以在 CLI 中恢复，反之亦然。所有会话都存储在[同一个数据库](https://block.github.io/goose/docs/guides/logs#session-records)中。

:::tip 为新任务创建新会话
虽然你可以恢复会话，但我们建议为新任务创建新会话，以减少[陷入死循环](https://block.github.io/goose/docs/troubleshooting/known-issues#stuck-in-a-loop-or-unresponsive)的可能性。
:::

### 复制会话

创建任意会话的完整副本，以复用配置、试验各种变体或保留重要的工作。

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
        
        从会话列表中复制会话：

        1. 在侧边栏中点击 <History className="inline" size={16} /> `Session History`
        2. 找到你想复制的会话
        3. 将鼠标悬停在会话卡片上以显示操作按钮
        4. 点击出现在右上角的 <Copy className="inline" size={16} /> 按钮

        复制出的会话包括：
        - 完整的对话历史
        - 所有会话元数据和设置
        - 提供方和模型配置
        - 扩展数据和配置
        - Recipe 信息（如果适用）

        新会话的名称与原会话相同，并出现在你会话列表的顶部。

        :::tip 复制与分叉会话
        - **复制**（会话列表中的 Copy 按钮）：创建整个会话的完整副本。用于保留一个正在使用的会话或复用其配置。
        - **[分叉会话](https://block.github.io/goose/docs/guides/sessions/in-session-actions#fork-session)**（消息上的 Edit 按钮）：创建一个新会话，其对话历史截止到某条被编辑的消息。当你在编辑消息以从该点探索不同方法时使用此功能。
        :::

    </TabItem>
    <TabItem value="cli" label="goose CLI">
        
        通过 `--fork` 标志搭配 `--resume`，复制上一个会话的所有消息来创建一个新会话。

        ```bash
        # Fork the most recent session
        goose session --resume --fork

        # Fork a specific session by name
        goose session --resume --fork --name my-project

        # Fork a specific session by ID
        goose session --resume --fork --session-id 20251108_3

        # Fork and show message history
        goose session --resume --fork --history
        ```

        分叉出的会话包括：
        - 来自原会话的完整对话历史
        - 所有会话元数据和设置
        - 提供方和模型配置
        - 扩展数据和配置
        - Recipe 信息（如果适用）
    </TabItem>
</Tabs>

### 删除会话

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
        你可以直接从 Desktop 应用中删除会话：

        1. 在侧边栏中点击 <History className="inline" size={16} /> `Session History`
        2. 找到你想删除的会话
        3. 将鼠标悬停在会话卡片上以显示操作按钮
        4. 点击出现的 <Trash2 className="inline" size={16} /> 按钮
        5. 在出现的模态框中确认删除

        :::warning 永久删除
        从 goose Desktop 中删除会话也会将其从 CLI 中删除。此操作无法撤销。
        :::

        该会话将立即从你的会话历史中移除，底层的会话记录将从本地存储中删除。
    </TabItem>
    <TabItem value="cli" label="goose CLI">
        你可以使用 CLI 命令移除会话。有关会话移除的详细说明，请参阅 [CLI 命令文档](https://block.github.io/goose/docs/guides/goose-cli-commands#session-remove-options)。
    </TabItem>
</Tabs>

### 导入会话

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
        从 JSON 文件导入完整会话，以便在 goose 实例之间恢复、共享或迁移会话。导入会创建一个带有新 ID 的新会话，而不是覆盖现有会话。

        1. 在侧边栏中点击 <History className="inline" size={16} /> `Session History`
        2. 点击右上角的 <Upload className="inline" size={16} /> `Import Session` 按钮
        3. 选择一个之前从 goose 导出的 `.json` 会话文件
        4. 该会话将以一个新的会话 ID 被导入
        5. 成功通知会确认此次导入

    </TabItem>
    <TabItem value="cli" label="goose CLI">
        会话导入目前仅可通过 Desktop 应用进行。
    </TabItem>
</Tabs>

### 导出会话

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
        将完整会话导出为 JSON 文件，以便备份、共享、迁移或归档。导出的文件会保留所有会话数据，包括对话历史、元数据和设置。

        1. 在侧边栏中点击 <History className="inline" size={16} /> `Session History`
        2. 找到你想导出的会话
        3. 将鼠标悬停在会话卡片上以显示操作按钮
        4. 点击出现的 <Download className="inline" size={16} /> 按钮
        5. 该会话将下载为一个以会话描述命名的 `.json` 文件

    </TabItem>
    <TabItem value="cli" label="goose CLI">
        导出会话以用于备份、共享、迁移或文档用途。你可以导出为 JSON 文件，以保留完整的会话数据（包括对话历史、元数据和设置），也可以导出为 Markdown 文件，以获取格式化、可读的对话版本。

        在终端中，运行 [`session export`](https://block.github.io/goose/docs/guides/goose-cli-commands#session-export-options) 子命令：
        
        ```bash
        goose session export
        ```

    </TabItem>
</Tabs>

---

## 智能上下文管理

> 原文：https://block.github.io/goose/docs/guides/sessions/smart-context-management

在使用[大型语言模型（LLM）](https://block.github.io/goose/docs/getting-started/providers)时，它们一次能处理的对话历史量是有限制的。goose 提供智能上下文管理功能，帮助处理上下文和对话限制，从而让你保持高效的会话。以下是一些关键概念：

- **上下文长度（Context Length）**：LLM 可以考虑的对话历史量，也称为上下文窗口
- **上下文限制（Context Limit）**：模型能够处理的最大 token 数量
- **上下文管理（Context Management）**：goose 如何处理接近这些限制的对话
- **轮（Turn）**：goose 与 LLM 之间一次完整的提示词-回复交互

### goose 如何管理上下文
goose 使用一种双层方法来管理上下文：

1. **自动压缩（Auto-Compaction）**：在接近 token 限制时主动压缩对话历史
2. **上下文策略（Context Strategies）**：如果在自动压缩后仍超出上下文限制时使用的后备策略

这种分层方法让 goose 能够从容地处理 token 和上下文限制。

### 自动压缩
当接近 token 限制时，goose 会自动将你对话中较旧的部分压缩为摘要，让你无需手动干预即可维持长时间运行的会话。
在 goose Desktop 和 goose CLI 中，当你达到 token 限制的 80% 或 225,000 个 token（以先到者为准）时，会自动触发自动压缩。
实际触发条件是 `min(GOOSE_AUTO_COMPACT_THRESHOLD × model context window, GOOSE_AUTO_COMPACT_TOKEN_LIMIT)`。它会根据当前模型的上下文窗口重新计算。用 `GOOSE_AUTO_COMPACT_TOKEN_LIMIT` 更改 token 上限。

默认上限在 OpenAI 的长上下文价格档位（超过 272,000 个输入 token）之下留出了余量。它控制压缩何时开始，而非一个保证的最大请求大小：在两次检查之间，新消息、工具输出以及压缩请求本身都可能超出触发条件。

使用 `GOOSE_AUTO_COMPACT_THRESHOLD` [环境变量](https://block.github.io/goose/docs/guides/environment-variables.md#session-management)来控制自动压缩行为。
将该值设为 `0.0` 可禁用此功能；token 上限不会重新启用已禁用的自动压缩。

```
# Automatically compact sessions when 60% of available tokens are used
export GOOSE_AUTO_COMPACT_THRESHOLD=0.6
```

当你达到自动压缩阈值时：
  1. goose 会自动开始压缩对话以腾出空间。
  2. 完成后，你会看到一条确认消息，说明对话已被压缩并总结。
  3. 继续会话。你之前的对话仍然可见，但只有被压缩后的对话会被包含在 goose 的活动上下文中。

:::tip 自定义压缩
你可以通过编辑 `compaction.md` [提示词模板](https://block.github.io/goose/docs/guides/context-engineering/prompt-templates)来自定义 goose 在压缩期间总结对话的方式。
:::

:::tip 工具输出摘要化
为了帮助维持高效的上下文使用，goose 会在后台对较早的工具调用输出进行摘要，同时完整保留最近的调用。默认情况下，goose 根据模型上下文限制和自动压缩阈值来计算截止点。有关高级调优，请参阅 [`GOOSE_TOOL_CALL_CUTOFF`](https://block.github.io/goose/docs/guides/environment-variables#session-management)。
:::

#### 手动压缩
你也可以在达到上下文或 token 限制之前手动触发压缩：

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

  1. 指向应用底部模型名称旁边的 token 使用量指示圆点
  2. 在出现的上下文窗口中点击 <ScrollText className="inline" size={16} /> `Compact now`
  3. 完成后，你会看到一条确认消息，说明对话已被压缩并总结。
  4. 继续会话。你之前的对话仍然可见，但只有被压缩后的对话会被包含在 goose 的活动上下文中。

  :::info 
  你必须先在聊天中发送至少一条消息，`Compact now` 按钮才会启用。 
  :::

</TabItem>
<TabItem value="cli" label="goose CLI" default>

要在达到上下文限制之前主动压缩对话，请使用 `/compact` 命令：

```sh
( O)> /compact
◇  Are you sure you want to compact this conversation? This will condense the message history.
│  Yes 
│
Compacting conversation...
Conversation has been compacted.
Key information has been preserved while reducing context length.
```

`/summarize` 仍然作为 `/compact` 的已弃用别名可用，但在新的文档和工作流中，应使用 `/compact` 命令。

</TabItem>
</Tabs>

### 上下文限制策略

当自动压缩被禁用，或者对话仍超出上下文限制时，goose 提供不同的处理方式：

| 功能 | 说明 | 最适合 | 可用性 | 影响 |
|---------|-------------|-----------|-----------|---------|
| **摘要化（Summarization）** | 在保留要点的同时压缩对话 | 长时间、复杂的对话 | Desktop 和 CLI | 保留大部分上下文 |
| **截断（Truncation）** | 移除最旧的消息以腾出空间 | 简单、线性的对话 | 仅 CLI | 丢失旧上下文 |
| **清空（Clear）** | 在保持会话活动的同时重新开始 | 对话的新方向 | 仅 CLI | 丢失所有上下文 |
| **提示（Prompt）** | 让用户从以上选项中挑选 | 在交互式会话中对每个决策的控制 | 仅 CLI | 取决于所做的选择 |

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

goose Desktop 专门通过压缩对话来使用摘要化以管理上下文，在减小规模的同时保留关键信息。

  </TabItem>
  <TabItem value="cli" label="goose CLI">

CLI 支持所有上下文限制策略：`summarize`、`truncate`、`clear` 和 `prompt`。

默认行为取决于你所运行的模式：
- **交互模式**：提示用户选择（等同于 `prompt`）
- **无头模式**（`goose run`）：自动摘要化（等同于 `summarize`）

你可以通过设置 `GOOSE_CONTEXT_STRATEGY` 环境变量来配置 goose 处理上下文限制的方式：

```bash
# Set automatic strategy (choose one)
export GOOSE_CONTEXT_STRATEGY=summarize  # Automatically summarize (recommended)
export GOOSE_CONTEXT_STRATEGY=truncate   # Automatically remove oldest messages
export GOOSE_CONTEXT_STRATEGY=clear      # Automatically clear session

# Set to prompt the user
export GOOSE_CONTEXT_STRATEGY=prompt
```

当你触及上下文限制时，行为取决于你的配置：

**使用默认设置（未设置 `GOOSE_CONTEXT_STRATEGY`）**时，你会看到以下提示以选择一种管理选项：

```sh
◇  The model's context length is maxed out. You will need to reduce the # msgs. Do you want to?
│  ○ Clear Session   
│  ○ Truncate Message
// highlight-start
│  ● Summarize Session
// highlight-end

final_summary: [A summary of your conversation will appear here]

Context maxed out
--------------------------------------------------
goose summarized messages for you.
```

**配置了 `GOOSE_CONTEXT_STRATEGY`** 时，goose 会自动应用你所选的策略：

```sh
# Example with GOOSE_CONTEXT_STRATEGY=summarize
Context maxed out - automatically summarized messages.
--------------------------------------------------
goose automatically summarized messages for you.

# Example with GOOSE_CONTEXT_STRATEGY=truncate
Context maxed out - automatically truncated messages.
--------------------------------------------------
goose tried its best to truncate messages for you.

# Example with GOOSE_CONTEXT_STRATEGY=clear
Context maxed out - automatically cleared session.
--------------------------------------------------
```
  </TabItem>
</Tabs>

### 最大轮数
`Max Turns` 限制是 goose 在无用户输入的情况下可以连续执行的最大轮数（默认：1000）。当达到该限制时，goose 会停下并提示："I've reached the maximum number of actions I can do without user input. Would you like me to continue?" 如果用户回答是，goose 会继续执行直到再次达到该限制，然后再次提示。

此功能让你能够控制 Agent 的自主性，并防止无限循环和失控行为，这些行为在生产环境中可能带来重大的成本后果或破坏性影响。你可以在以下场景中使用它：

- 在自动化任务中防止无限循环以及过度的 API 调用或资源消耗
- 在自主操作期间启用人工监督或交互
- 在测试和调试 Agent 行为时控制循环

此设置作为 `GOOSE_MAX_TURNS` 环境变量存储在你的 [config.yaml 文件](https://block.github.io/goose/docs/guides/config-files)中。你可以使用 Desktop 应用或 CLI 来配置它。

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>

      1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮以打开侧边栏
      2. 点击侧边栏上的 `Settings` 按钮
      3. 点击 `Chat` 标签页
      4. 滚动到 `Conversation Limits` 并为 `Max Turns` 输入一个值
        
    </TabItem>
    <TabItem value="cli" label="goose CLI">

      1. 运行 `configuration` 命令：
      ```sh
      goose configure
      ```

      2. 选择 `goose settings`：
      ```sh
      ┌   goose-configure
      │
      ◆  What would you like to configure?
      │  ○ Configure Providers
      │  ○ Add Extension
      │  ○ Toggle Extensions
      │  ○ Remove Extension
      // highlight-start
      │  ● goose settings (Set the goose mode, Tool Output, Tool Permissions, Experiment, goose recipe github repo and more)
      // highlight-end
      └ 
      ```

      3. 选择 `Max Turns`：
      ```sh
      ┌   goose-configure
      │
      ◇  What would you like to configure?
      │  goose settings
      │
      ◆  What setting would you like to configure?
      │  ○ goose mode 
      │  ○ Router Tool Selection Strategy 
      │  ○ Tool Permission 
      │  ○ Tool Output 
      // highlight-start
      │  ● Max Turns (Set maximum number of turns without user input)
      // highlight-end
      │  ○ Toggle Experiment 
      │  ○ goose recipe github repo 
      │  ○ Scheduler Type 
      └ 
      ```

      4. 输入最大轮数：
      ```sh
      ┌   goose-configure 
      │
      ◇  What would you like to configure?
      │  goose settings 
      │
      ◇  What setting would you like to configure?
      │  Max Turns 
      │
        // highlight-start
      ◆  Set maximum number of agent turns without user input:
      │  10
        // highlight-end
      │
      └  Set maximum turns to 10 - goose will ask for input after 10 consecutive actions
      ```

      :::tip
      除了持久的 `Max Turns` 设置外，你还可以通过 `goose session --max-turns` 和 `goose run --max-turns` [CLI 命令](https://block.github.io/goose/docs/guides/goose-cli-commands)为特定会话或任务提供运行时覆盖值。
      :::

    </TabItem>
    
</Tabs>

**选择合适的值**

合适的最大轮数值取决于你的用例以及对自动化的接受程度：

- **5-10 轮**：适合探索性任务、调试，或者当你希望频繁检查时。例如，"analyze this codebase and suggest improvements"，此时你想审查每一步
- **25-50 轮**：对于定义明确、复杂度适中的任务很有效，例如 "refactor this module to use the new API" 或 "set up a basic CI/CD pipeline"
- **100+ 轮**：更适合你信任 goose 独立工作的复杂、多步骤自动化，例如 "migrate this entire project from React 16 to React 18" 或 "implement comprehensive test coverage for this service"

请记住，即使看似简单的任务也常常需要多轮。例如，让 goose "fix the failing tests" 可能涉及分析测试输出（1 轮）、确定根本原因（1 轮）、进行代码更改（1 轮）以及验证修复（1 轮）。

### Token 使用量
发送第一条消息后，goose Desktop 和 goose CLI 会显示 token 使用量。

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
    Desktop 会在会话窗口底部模型名称旁边显示一个彩色圆圈。颜色为你的会话 token 使用量提供视觉指示。
      - **绿色**：正常使用 - 有充足的上下文空间
      - **橙色**：警告状态 - 接近限制（容量的 80%）
      - **红色**：错误状态 - 已达到上下文限制
    
    将鼠标悬停在此圆圈上会显示：
      - 已使用的 token 数量
      - 已使用可用 token 的百分比
      - 可用的 token 总量
      - 显示你当前 token 使用量的进度条
        
    </TabItem>
    <TabItem value="cli" label="goose CLI">
    CLI 会在每个命令提示符上方显示一个上下文标签，展示：
      - 使用圆点（●○）和颜色的视觉指示器，表示你的 token 使用量：
        - **绿色**：使用量低于 50%
        - **黄色**：使用量在 50-85% 之间
        - **红色**：使用量高于 85%
      - 使用百分比
      - 当前 token 数量和上下文限制

    </TabItem>
</Tabs>

### 模型上下文限制覆盖

上下文限制会根据你的模型名称自动检测，但 goose 提供了覆盖默认限制的设置：

| 模型 | 说明 | 最适合 | 设置 |
|-------|-------------|----------|---------|
| **主模型（Main）** | 为主模型设置上下文限制（同时作为其他模型的后备） | LiteLLM 代理、名称非标准的自定义模型 | `GOOSE_CONTEXT_LIMIT` |

:::info
此设置仅影响显示的 token 使用量和进度指示器。实际的上下文管理由你的 LLM 处理，因此无论显示如何，你的实际使用量可能会多于或少于你所设置的限制。
:::

此功能在以下场景中特别有用：

- **LiteLLM 代理模型**：当你使用带有自定义模型名称的 LiteLLM，而这些名称与 goose 的模式不匹配时
- **企业部署**：名称非标准的自定义模型部署
- **微调模型**：与其基础版本具有不同上下文限制的自定义模型
- **开发/测试**：为测试目的临时调整上下文限制

goose 按以下优先级（从高到低）解析上下文限制：

1. 全局环境变量（`GOOSE_CONTEXT_LIMIT`）
2. 显式的声明式或自定义提供方模型配置
3. 提供方运行时发现
4. 规范模型元数据
5. 全局默认值（128,000 个 token）

**配置**

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

     goose Desktop 应用中尚不支持模型上下文限制覆盖。

  </TabItem>
  <TabItem value="cli" label="goose CLI">

    上下文限制覆盖仅作为[环境变量](https://block.github.io/goose/docs/guides/environment-variables#model-context-limit-overrides)生效，而不能在配置文件中使用。

    ```bash
    export GOOSE_CONTEXT_LIMIT=1000
    goose session
    ```

  </TabItem>
    
</Tabs>

**场景**

1. 带有自定义模型名称的 LiteLLM 代理

```bash
# LiteLLM proxy with custom model name
export GOOSE_PROVIDER="openai"
export GOOSE_MODEL="my-custom-gpt4-proxy"
export GOOSE_CONTEXT_LIMIT=200000  # Override the 32k default
```

### 额度余额监控

goose 会监控你的 API 提供方余额，并在额度即将耗尽或已耗尽时向你发出警告。发生这种情况时，你会看到一条 **Insufficient Credits** 通知。

对于支持该功能的提供方（例如 [Tetrate Agent Router Service](https://router.tetrate.ai)），该通知会包含一个 **Add credits** 按钮，可直接将你带到提供方的账单页面。

**该怎么做：**
1. 点击 **Add credits** 按钮（如果可用）为你的账户充值
2. 或者手动访问提供方的仪表盘来添加额度
3. 添加额度后，重新发送你的消息以继续对话

:::tip
goose 会自动检测低余额状况，因此你不会丢失对话上下文——只需添加额度，然后从你中断的地方继续即可。
:::

**支持的提供方：** Tetrate Agent Router Service、OpenRouter，以及通过 HTTP 402 响应报告余额信息的其他提供方。

### 成本跟踪
显示你会话的实时预估成本。

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
要管理实时成本跟踪：
  1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮以打开侧边栏
  2. 点击侧边栏上的 `Settings` 按钮
  3. 点击 `App` 标签页
  4. 打开/关闭 `Cost Tracking`

会话成本显示在 goose 窗口的底部，并随着 token 被消耗而动态更新。将鼠标悬停在成本上可查看 token 使用量的详细明细。如果会话中使用了多个模型，这会包含按模型划分的成本明细。Ollama 和本地部署始终显示 $0.00 的成本。

定价数据会定期从 OpenRouter API 获取并在本地缓存。`Advanced settings` 标签页会显示数据上次更新的时间，并允许你刷新。

这些成本仅为公开价格估算，并非发票，也不代表你实际的提供方账单。显示的金额根据 token 数量和公开目录费率近似计算使用量；当提供方报告的成本可用时，以提供方报告的成本为准。
</TabItem>
    <TabItem value="cli" label="goose CLI">
    通过设置 `GOOSE_CLI_SHOW_COST` [环境变量](https://block.github.io/goose/docs/guides/environment-variables.md#session-management)，或将其包含在[配置文件](https://block.github.io/goose/docs/guides/config-files.md)中，来在 goose CLI 中显示预估成本。

  ```
  # Set environment variable
  export GOOSE_CLI_SHOW_COST=true

  # config.yaml
  GOOSE_CLI_SHOW_COST: true
  ```
  </TabItem>
</Tabs>

---

## 会话内操作

> 原文：https://block.github.io/goose/docs/guides/sessions/in-session-actions

goose 提供的功能可让你在会话期间管理对话和分享信息。

### 编辑消息

编辑你之前发送的消息，以完善对话、纠正方向或尝试不同的方法。

**示例消息流：**

你的原始对话有五条消息。在编辑消息 3 后，来自消息 4 和 5 的所有消息和回复上下文都会被删除。

```
┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐
│  1  │ → │  2  │ → │  3  │ → │  4  │ → │  5  │
└─────┘   └─────┘   └─────┘   └─────┘   └─────┘
           
                   Edit here
                       ↓
┌─────┐   ┌─────┐   ┌─────┐    continue from here in
│  1  │ → │  2  │ → │  3  │ →  current session, or
└─────┘   └─────┘   └─────┘    copy to new session
```

你可以选择在当前会话中继续工作，或在新会话中创建一个分叉：

- [就地编辑](#edit-in-place)，以更新当前会话，并删除被编辑消息之后的所有消息和回复上下文。这让你可以从某个给定的点重新开始对话。
- [分叉会话](#fork-session)，以创建一个新会话，其中包含截至并包括被编辑消息在内的所有对话历史。这让你可以探索不同的方法，同时保留你的原始对话。

#### 就地编辑

就地编辑让你通过覆盖被编辑消息之后的所有上下文，来完全掌控对话历史。你的更改可以简单到修正上一条消息中的一个路径，也可以是从某个给定点完全重新开始。

在以下情况中，就地编辑很有用：

- 你意识到自己发送的提示词不清晰或不完整
- goose 误解了你的意图并走错了方向

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>

        1. 将鼠标悬停在你之前的任意消息上
        2. 点击出现的 <Edit2 className="inline" size={16} /> `Edit` 按钮
        3. 在内联编辑器中进行更改
        4. 点击 `Edit in Place` 保存更改并重新提示 goose

        goose 会移除被编辑消息之后的所有对话历史，并从该点起根据上下文进行回复。

        :::warning 已删除的上下文
        使用就地编辑时，后续的对话历史会从会话中永久删除，并从 goose 的上下文中移除。仅当你不需要 goose 记住被编辑消息之后的上下文时，才使用此选项。
        :::

    </TabItem>
    <TabItem value="cli" label="goose CLI">
        将 `--edit` 标志与 `goose session` 搭配使用，以 YAML 形式在你的编辑器中打开会话的对话：

        ```bash
        goose session --resume <session-id> --edit
        ```

        这会用 `$VISUAL` / `$EDITOR` / `vi` 打开序列化为 YAML 的对话。编辑并保存后，goose 会从编辑后的对话继续该会话。你留在 YAML 中的任何后续消息都会保留在会话和 goose 的上下文中；如果你想让 goose 忘记它们，请从 YAML 中移除这些消息。

    </TabItem>
</Tabs>

#### 分叉会话

分叉会话会使用你编辑后的消息创建一个新会话，同时保留原始对话。你可以试验各种变体并比较结果，同时将原始会话保留为参照点。

分叉会话在以下情况下很有用：
- 并排比较同一问题的不同方法
- 测试不同的提示词如何影响 goose 的回复

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
        1. 将鼠标悬停在你之前的任意消息上
        2. 点击出现的 <Edit2 className="inline" size={16} /> `Edit` 按钮
        3. 在内联编辑器中进行更改
        4. 点击 `Fork Session` 保存更改并启动一个新会话（或使用 `Cmd+Enter`（macOS）或 `Ctrl+Enter`（Windows/Linux））

        goose 会创建一个新会话，其对话历史截止到并包括你编辑后的消息。新会话命名为 "(edited)"，原始会话保持不变。

        :::tip 分叉与复制
        - **分叉会话**（消息上的 Edit 按钮）：创建一个新会话，其历史截止到某条被编辑的消息。用于从对话中某个特定点探索不同的方法。
        - **[复制会话](https://block.github.io/goose/docs/guides/sessions/session-management#duplicate-sessions)**（会话列表中的 Copy 按钮）：创建整个会话的完整副本。用于保留一个正在使用的会话或复用其配置。
        :::
</TabItem>
    <TabItem value="cli" label="goose CLI">
        将 `--edit` 和 `--fork` 标志搭配使用，以编辑会话的对话并根据结果创建一个新会话：

        ```bash
        goose session --resume <session-id> --fork --edit
        ```

        这会用 `$VISUAL` / `$EDITOR` / `vi` 打开序列化为 YAML 的对话。编辑并保存后，goose 会使用编辑后的对话创建一个新会话并从中继续。原始会话保持不变。

        你也可以在不使用 `--edit` 的情况下，使用 `--fork` 来[复制整个会话](https://block.github.io/goose/docs/guides/sessions/session-management#duplicate-sessions)。
    </TabItem>
</Tabs>

#### 编辑场景技巧

- **迭代式提示词打磨**：从一个基础提示词开始，然后根据 goose 的回复进行编辑和打磨。这通常比从一开始就试图精心打造一个完美的提示词效果更好。
- **何时编辑与何时打断**：当对话偏离正轨时，编辑较早的消息可能比试图用新消息或[打断](#interrupt-task)来纠正方向更有效。通过编辑消息，你重写了历史。而通过打断，你只影响从当前消息往后的对话。
- **保留进度**：当你已取得良好进展但想尝试不同方法时，使用分叉会话。这样，如果新方向不奏效，你总能回到原始会话。

### 消息排队

在 goose 处理任务时将消息排队，以管理你的工作流。这在以下情况中很有用：

- 你想在 goose 工作时准备下一步
- 你有一系列相关的任务要完成
- 你正在使用[语音听写](#voice-dictation)并需要快速记录想法

:::tip
当把复杂任务拆分为子任务时，goose 可能表现更好，这种技术称为[*提示词链（prompt chaining）*](https://www.promptingguide.ai/techniques/prompt_chaining)。这种结构化方法既能提高准确性，也能让你对流程有更多控制。
:::

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
      将一条消息添加到队列：
      1. 在 goose 正在处理回复时，输入你的下一条消息
      2. 按 `Enter` 将其添加到队列（如果使用了[打断关键词](#interrupt-task)，则会打断）
      
      排队的消息会以显示队列顺序的编号卡片形式出现。当 goose 完成每条回复时，队列中的第一条消息会被自动发送。
      
      :::info 相关功能
      - 一般而言，在 goose 处理任务时按 `Enter` 会将消息排队，但点击 `Send` 会立即发送任务并[打断该任务](#interrupt-task)
      - 当你在排队消息中输入 "stop"、"wait" 或 "hold on" 等常见打断关键词时，goose 会暂停，直到你输入或发送下一条消息，然后继续处理队列
      :::

      #### 队列管理控件
    
      排队消息会在 goose 完成每项任务时按顺序自动运行，但你可以管理队列：
      - **编辑消息**：点击消息文本以显示编辑控件，然后输入你的更改并点击 `Save`
      - **重新排列消息**：将鼠标悬停在消息卡片上以显示 <GripVertical className="inline" size={16} /> 按钮，然后抓取它并将消息向上或向下拖动
      - **发送消息**：点击 <Send className="inline" size={16} /> 按钮立即发送消息并打断当前任务
      - **删除消息**：点击 <X className="inline" size={16} /> 按钮以删除该消息
      - **清空队列**：在 **Message Queue** 卡片上点击 `Clear All`
      - **折叠或展开队列**：在 **Message Queue** 卡片上点击 <ChevronUp className="inline" size={16} /> 或 <ChevronDown className="inline" size={16} /> 按钮

      #### 示例消息流

      **不使用排队：**

      你发送："Can you refactor our authentication code to support OAuth 2.0 and add proper error handling? Also include unit tests for the OAuth flow, update the API documentation to reflect these changes, and create a migration script to help existing users transition to the new system."

      这种方法可能导致回复信息量过大，重要细节被遗漏或任务被草率处理。即使发送一个带有清晰顺序步骤的单一提示词，也无法让 goose 单独专注于每项任务或逐步构建上下文。

      **使用排队：**

      1. 你发送："Refactor the authentication code to support OAuth 2.0"
      2. 在 goose 工作时，你将以下消息排队：
         - "And add proper error handling"
         - "Add unit tests for the OAuth flow"
         - "Update the API documentation" 
         - "Create migration script for existing users"
      
      每项任务都建立在前一项的基础上。

    </TabItem>
    <TabItem value="cli" label="goose CLI">
        goose CLI 中不提供消息排队功能。
    </TabItem>
</Tabs>

### 打断任务

在 goose 处理任务时打断它，以掌控对话。这在以下情况中很有用：

- goose 正朝着错误的方向前进
- 你意识到需要添加重要的上下文
- 你想切换到一项完全不同的任务

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
        
        有两种方式可以打断任务：

        #### 发送打断关键词
        1. 输入一条包含常见打断关键词的提示词，例如 `stop`、`wait`、`hold on`、`actually` 或 `instead`。单独使用关键词，或将其放在句子开头，最有利于可靠检测。
        2. 点击 `Send`
        
        goose 会停止处理当前任务并询问更多信息。
        
        #### 提供即时重定向
        1. 输入一条包含更多上下文和澄清，或改变方向的提示词。例如：
           - "I forgot to mention this is for a mobile app"
           - "Let's focus on React instead of TypeScript"
        2. 点击 `Send`
        
        goose 会停止处理当前任务，并转向新的请求上下文。
        
        :::info 相关功能
        - 在 goose 处理任务时点击 `Send` 会打断任务，但按 `Enter` 会[将消息排队](#queue-messages)
        - 在排队消息中输入停止或暂停关键词也会阻止 goose 处理当前任务
        - 你也可以[编辑已发送的消息](#edit-message)，在会话期间提供更多上下文和澄清，或改变方向
        :::

        <details>
          <summary>打断关键词列表</summary>

          **高优先级关键词**（在任何上下文中都会打断）：
          ```
          stop, halt, cease, quit, end, abort, cancel, wait, hold, pause, hold on, wait up, hold up
          ```

          **中优先级关键词**（仅在精确匹配或位于句子开头时打断）：
          ```
          no, nope, nah, wrong, incorrect, not right, actually, instead, rather, better idea, change of plans, nevermind, never mind, forget it, ignore that, disregard
          ```

          **检测规则**：
          - **精确匹配**（100% 置信度）：词/短语完全匹配时始终打断
          - **句子开头**（非常高的置信度）：词/短语位于你的消息开头时始终打断
          - **仅限短消息**（高置信度）：在 ≤20 个字符的消息中，只有高优先级关键词会打断
          - **不区分大小写**：所有检测都不区分大小写

          **示例**：
          - ✅ "stop" 会打断（精确匹配）
          - ✅ "Wait, I meant something else" 会打断（句子开头）
          - ✅ "no" 会打断（短消息，高优先级）
          - ❌ 短消息中的 "actually" 不会打断（短消息中的中优先级）
          - ✅ "Actually, let's try React instead" 会打断（句子开头）

        </details>

    </TabItem>
    <TabItem value="cli" label="goose CLI">
        1. 按 `Ctrl+C` 打断当前任务
        2. 输入提供更多上下文或改变方向的提示词
        3. 按 `Enter`

        goose 会根据你的新请求做出相应的回复。
        
    </TabItem>
</Tabs>

### 语音听写
直接对 goose 说话，而不是输入你的提示词。

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
    要启用语音听写：
        1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮以打开侧边栏
        2. 在侧边栏中点击 `Settings`
        3. 点击 `Chat` 标签页
        4. 对于 `Voice Dictation Provider`，从下拉列表中选择你的提供方：
           - Local — 使用本地 whisper 模型进行设备端转写，无需 API 密钥。首次使用时，系统会提示你下载该模型。
           - [Elevenlabs](https://elevenlabs.io/)
           - [Groq](https://groq.com/)
           - [OpenAI](https://platform.openai.com/api-keys)
        5. 如果系统提示，请输入你所选提供方的 API 密钥

    要使用语音听写：
        1. 在侧边栏的 `Chat` 下点击你的聊天会话
        2. 点击聊天框右侧的麦克风按钮并开始说话
        3. 要发送消息，请执行以下操作之一：
           - 说 "submit" 以发送消息并继续录制下一条。要停止录制，请点击麦克风按钮。
           - 点击麦克风按钮停止录制，然后点击 `Send` 或按 `Enter`。此选项允许你在发送前编辑消息。
        
        首次使用语音听写时，goose 会请求访问你的麦克风。录制时，你会看到 `Listening` 和 `Transcribing` 状态指示器。goose 会在自然停顿期间转写你的语音，并将文本添加到聊天框中。

        **如果你没有看到麦克风**，请检查[你已配置的模型](https://block.github.io/goose/docs/getting-started/providers.md)。例如，使用 OpenAI 作为语音听写提供方，需要你在 goose 中配置了一个 OpenAI 模型，即使你使用另一个 LLM 提供方进行聊天也是如此。

       #### 重要说明
        * 你最多可以录制 50MB 的音频
        * ElevenLabs、Groq 和 OpenAI 会将音频录制发送到它们的服务器进行处理。本地提供方完全在你的设备上处理音频——不会有任何数据离开你的电脑。
        * 语音输入会追加到文本输入字段中已有的任何文本之后
        * 转写后，录制不会在本地存储
        * 要禁用语音听写，请从提供方下拉列表中选择 `Disabled`

  </TabItem>
    <TabItem value="cli" label="goose CLI">
        goose CLI 中不提供语音听写功能。
    </TabItem>
</Tabs>

### 拼写检查

拼写检查在 goose Desktop 聊天输入字段中默认启用。

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
    要禁用或重新启用拼写检查：
        1. 点击左上角的 <PanelLeft className="inline" size={16} /> 按钮以打开侧边栏
        2. 在侧边栏中点击 `Settings`
        3. 点击 `Chat`
        4. 向下滚动到 `Enable Spellcheck` 并将其打开或关闭
        5. 重启 goose 以使更改生效
        
    </TabItem>
    <TabItem value="cli" label="goose CLI">
        goose CLI 中不提供拼写检查功能。
    </TabItem>
</Tabs>

### 在会话中共享文件

向 goose 提供来自你的代码库、文档和其他文件的上下文，以获得更相关、更准确的协助。

<Tabs groupId="interface">
    <TabItem value="ui" label="goose Desktop" default>
        通过多种方式与 goose 共享文件：

        1. **拖放**：只需从你电脑的文件资源管理器/Finder 中拖动文件，并将其放到聊天窗口中的任意位置。文件路径会自动添加到你的消息中。

        2. **文件浏览器**：点击应用底部的 <Paperclip className="inline" size={16} /> 按钮，打开系统的文件浏览器并选择文件

        3. **手动路径**：直接在聊天输入框中输入或粘贴文件路径

        4. **快速文件搜索**：使用 [`@` 快捷键](https://block.github.io/goose/docs/guides/file-management#quick-file-search-in-goose-desktop)快速查找并包含文件
    </TabItem>
    <TabItem value="cli" label="goose CLI">
        你可以在消息中直接通过路径引用文件。由于你已经处于终端中，你可以使用标准 shell 命令来帮助处理文件路径：

        ```bash
        # Reference a specific file
        What does this code do? ./src/main.rs

        # Use tab completion
        Can you explain the function in ./src/lib<tab>

        # Use shell expansion
        Review these test files: ./tests/*.rs
        ```
    </TabItem>
</Tabs>

### 会话中途更改

你可以在会话期间更改某些设置，它们会立即生效，而无需你启动新会话。这让你在与 goose 交互时对上下文和能力有更多控制。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>

  使用应用底部的工具栏在会话中途更改受支持的设置：

  | 设置 | 工具栏项 | 持久性* |
  |---------|--------------|-------------|
  | **工作目录** | <FolderDot className="inline" size={16} /> 目录切换器 | 新会话（重启后） |
  | [**已启用的扩展**](https://block.github.io/goose/docs/getting-started/using-extensions#change-extensions-mid-session) | <Puzzle className="inline" size={16} /> 图标 | 仅当前会话 |
  | [**模型**](https://block.github.io/goose/docs/getting-started/providers#configure-provider-and-model) | <Bot className="inline" size={16} /> 模型切换器 | 新会话 |
  | [**goose 模式**](https://block.github.io/goose/docs/guides/managing-tools/goose-permissions#configuring-goose-mode) | <Tornado className="inline" size={16} /> 模式切换器 | 新会话 |

  </TabItem>
  <TabItem value="cli" label="goose CLI">

  使用斜杠命令在会话中途更改受支持的设置：

  | 设置 | 斜杠命令 | 持久性* |
  |---------|--------------|-------------|
  | [**已启用的扩展**](https://block.github.io/goose/docs/getting-started/using-extensions#change-extensions-mid-session) | `/extension` 或 `/builtin` | 仅当前会话 |
  | [**goose 模式**](https://block.github.io/goose/docs/guides/managing-tools/goose-permissions#configuring-goose-mode) | `/mode [options]` | 新会话 |

  :::info
  CLI 支持[额外的斜杠命令](https://block.github.io/goose/docs/guides/goose-cli-commands#slash-commands)，但不支持在会话中途更改工作目录或模型。
  :::

  </TabItem>
</Tabs>

*持久性表示更改是仅适用于你当前的会话，还是会延续到新会话

---

## 运行任务

> 原文：https://block.github.io/goose/docs/guides/running-tasks

使用 goose CLI 时，你可以将文件和指令传递给 `goose run` 命令，以执行任务和工作流。这可以是一条简单的单行命令，也可以是存储在文件中的一组复杂指令。

### 基本用法

`goose run` 命令会启动一个新会话，使用所提供的任何参数开始执行，并在任务完成后自动退出会话。

使用 goose 运行任务有多种方式；请查看[选项列表](https://block.github.io/goose/docs/guides/goose-cli-commands.md#run-options)。

#### 命令中的文本
```bash
goose run -t "your instructions here"
```

使用 `-t` 标志，你可以将一条文本指令直接传递给命令。这非常适合快速的一次性命令，你无需与 goose 进行交互式会话。指令将被执行，然后会话结束。一个示例用法是在 CI/CD 流水线中使用，或与其他脚本一起运行。

#### 使用指令文件
如果你有一组复杂的指令或一个想要自动化的工作流，你可以将它们存储在文件中并传递给 `goose run` 命令：

```bash
goose run -i instructions.md
```

以下是一个对项目依赖运行安全审计的指令文件示例：

```md
# Dependency Security Audit

1. Analyze project dependencies:
   - Check package.json and requirements.txt files
   - List all dependencies with versions
   - Identify outdated packages

2. Security check:
   - Run npm audit (for JavaScript packages)
   - Check for known vulnerabilities in Python packages
   - Identify dependencies with critical security issues

3. Create an upgrade plan:
   - List packages requiring immediate updates
   - Note breaking changes in latest versions
   - Estimate impact of required updates

Save findings in 'security_audit.md' with severity levels highlighted.
```

#### 使用 stdin
你也可以通过 `-i -` 使用标准输入将指令传递给 goose。当你想把来自另一个工具或脚本的命令通过管道输入 goose 时，这很有用。

##### 简单的 echo 管道

```bash
echo "What is 2+2?" | goose run -i -
```

##### 多行指令
```bash
cat << EOF | goose run -i -
Please help me with these tasks:
1. Calculate 15% of 85
2. Convert 32°C to Fahrenheit
EOF
```

### 关键功能

#### 交互模式

如果你不希望 goose 在任务结束时退出，可以传递 `-s` 或 `--interactive` 标志，以在处理完你的初始命令后启动一个交互式会话：

```bash
goose run -i instructions.txt -s
```

当你希望在初始命令处理完后继续与 goose 协作时，这很有用。

#### 会话管理

你可以命名和管理你的会话：

```bash
# Start a new named session
goose run -n my-project -t "initial instructions"

# Resume a previous session
goose run -n my-project -r
```

你也可以使用 `--no-session` 标志在不创建或存储会话文件的情况下运行命令。这对于自动化脚本，或不需要维护对话历史或状态的一次性任务很有用。此标志会将会话输出路由到一个临时的空路径（Unix 上为 `/dev/null`，Windows 上为 `NUL`），并在完成时将其丢弃。

```bash
# Run a command without creating a session file
goose run --no-session -t "your command here"
```
#### 设置提供方和模型
你可以使用特定的提供方和模型来运行 goose 会话，这会覆盖你[环境变量](https://block.github.io/goose/docs/guides/environment-variables.md)中的提供方和模型设置。

```bash
goose run --provider anthropic --model claude-4-sonnet -t "initial prompt"
```

#### 使用扩展

如果你想确保在运行任务时特定的扩展可用，可以通过参数指明。这可以使用 `--with-extension`、`--with-remote-extension`、`--with-streamable-http-extension` 或 `--with-builtin` 标志来完成：

- 使用内置扩展，例如 developer 和 computercontroller 扩展

```bash
goose run --with-builtin "developer,computercontroller" -t "your instructions"
```

- 使用自定义扩展

```bash
goose run --with-extension "ENV1=value1 custom-extension-args" -t "your instructions"
```

- 使用可流式 HTTP 扩展

```bash
goose run --with-streamable-http-extension "https://example.com/streamable" -t "your instructions"
```

#### 调试模式

在排查问题或开发复杂工作流时，你可以启用调试模式以获取关于工具执行的更详细信息。`--debug` 标志提供：

- 完整的工具响应
- 详细的参数值
- 完整的文件路径

调试模式在以下情况中很有用：
- 开发新的自动化脚本
- 排查扩展行为问题
- 验证工具参数和响应

```bash
# Run a task with debug output enabled
goose run --debug -t "your instructions"

# Debug a recipe execution
goose run --debug --recipe recipe.yaml
```

#### JSON 输出格式

对于自动化、脚本编写和 CI/CD 集成，你可以使用 `--output-format` 标志从 `goose run` 获取结构化输出：

- `json` - 执行完成后输出完整 JSON（最适合 CI 流水线、日志记录）
- `stream-json` - 随着事件发生实时输出结构化内容（最适合进度监控、长时间运行的任务）

```bash
# Run with JSON output for automation
goose run --output-format json -t "your instructions"

# Stream JSON events in real-time
goose run --output-format stream-json -t "your instructions"

# Run a recipe with JSON output
goose run --output-format json --recipe recipe.yaml

# Combine with other options
goose run --output-format json --no-session -t "automated task"
```

JSON 输出包括：
- 会话元数据和执行结果
- 工具输出和任何错误
- 适合脚本和 CI/CD 流水线解析的结构化数据

### 常见用例

#### 运行脚本文件

创建一个指令文件（例如 `build-script.txt`）：
```text
Check the current branch
Run the test suite
Build the documentation
```

然后运行它：
```bash
goose run -i build-script.txt
```

#### 快速命令

对于一次性命令，使用文本选项：
```bash
goose run -t "Create a CHANGELOG.md entry comparing current git branch with main"
```

#### 开发工作流

使用特定扩展启动一个会话：
```bash
goose run --with-builtin "developer,git" -n dev-session -s
```

#### 组合选项

你可以组合多个选项来创建强大的工作流：

```bash
# Complex example combining multiple options
goose run \
  --with-builtin "developer,git" \
  --with-extension "API_KEY=xyz123 custom-tool" \
  -n project-setup \
  -t "Initialize project" 
```

此命令：
1. 加载 developer 和 git 内置扩展
2. 添加一个带有 API 密钥的自定义扩展
3. 将会话命名为 "project-setup"
4. 以 "Initialize project" 指令开始
5. 在处理完命令后自动退出。
