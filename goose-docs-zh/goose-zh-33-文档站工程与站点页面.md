# goose 官方文档中文手册：第 33 章　文档站工程与站点页面

## 文档写作风格指南

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/AGENTS.md

### 品牌规范

**重要**：在本文档目录内的所有文档、博客文章以及任何内容中，产品名 "goose" 必须始终使用小写字母 "g"。

- ✅ 正确："goose"、"using goose"、"goose provides"
- ❌ 错误："Goose"、"using Goose"、"Goose provides"

这是一条必须严格遵守的品牌规范。

### 适用范围

该规则适用于：

- `/docs/` 下的所有 markdown 文件
- `/blog/` 下的所有博客文章
- README 文件
- 含面向用户文本的配置文件
- 任何其他文档内容

在本文档目录中编辑或创建内容时，请始终确保 "goose" 使用小写 "g"。

### MCP 扩展目录

goose 正在停用其项目专属的 MCP 服务器目录，转而采用[官方 MCP Registry](https://github.com/modelcontextprotocol/registry)及其 `server.json` 格式。

- 不要通过把新的第三方服务器加入 `static/servers.json` 来记录它们；不再接受新的目录提交。
- 引导 MCP 服务器作者发布到官方 MCP Registry。
- 不要仅为支持目录提交而创建新的服务器专属教程。
- 现有条目与教程可在迁移过程中继续维护或迁移。

关于该决定与迁移方向，参见 [Discussion #10830](https://github.com/aaif-goose/goose/discussions/10830)。

---

## CLAUDE.md（引用 AGENTS.md）

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/CLAUDE.md

```
@AGENTS.md
```

---

## 文档站点（Website）

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/README.md

本站点使用 [Docusaurus](https://docusaurus.io/) 构建，它是一个现代静态网站生成器。

请在 `documentation/` 目录下运行所有命令。

#### 安装

```
$ npm i
```

#### 本地开发

```
$ npm run start
```

该命令会启动一个本地开发服务器并打开浏览器窗口。大多数改动会实时生效，无需重启服务器。

#### 构建

```
$ npm run build
```

该命令会把静态内容生成到 `build` 目录，可用任何静态内容托管服务来提供。

#### 部署

使用 SSH：

```
$ USE_SSH=true npm run deploy
```

不使用 SSH：

```
$ GIT_USER=<Your GitHub username> npm run deploy
```

如果你使用 GitHub Pages 托管，该命令可以方便地构建网站并推送到 `gh-pages` 分支。
<!-- trigger deployment -->

---

## 文档自动化

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/automation/README.md

该目录包含用于让 goose 文档与代码变更保持同步的自动化流水线。

### 概览

每个自动化项目跟踪特定类型的变更并更新相应文档：

| 项目 | 状态 | 跟踪 | 更新 |
|---------|--------|--------|---------|
| cli-command-tracking | 🔮 计划中 | CLI 命令与选项 | CLI 文档 |
| provider-tracking | 🔮 计划中 | 支持的 AI 提供方 | 提供方文档 |
| extension-tracking | 🔮 计划中 | 内置扩展 | 扩展文档 |

### 架构

每个自动化项目遵循一致的模式：

```
project-name/
├── README.md             # Project-specific documentation
├── TESTING.md            # How to test this automation
├── config/               # Configuration files
├── scripts/              # Deterministic extraction/diff scripts
└── recipes/              # AI-powered synthesis/update recipes
```

#### 设计原则

1. **模块化**：每个项目自包含
2. **可测试**：每个阶段都有清晰的输入/输出
3. **透明**：中间文件可供检查
4. **可复用**：跨项目复用通用模式

#### 混合方案

- **Shell 脚本**：确定性的抽取与比较
- **AI Recipe**：综合与文档更新

### GitHub Actions 集成

自动化项目可通过 `.github/workflows/` 中的 GitHub Actions 工作流触发。

各工作流用法参见各项目自己的 TESTING.md 文件。

### 新增自动化

创建新的自动化项目时：

1. 创建一个子目录：`documentation/automation/your-project/`
2. 遵循标准结构（README、TESTING、config、scripts、recipes）
3. 创建对应的 GitHub Actions 工作流（如需要）
4. 用新项目更新本 README

### 有问题？

项目专属问题请参见各项目目录中的 README。

---

## CLI 命令追踪

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/automation/cli-command-tracking/README.md

用于检测并记录 goose 各版本之间 CLI 命令变更的自动化流水线。

### 概览

该自动化通过以下步骤，让 [CLI Commands Guide](https://goose-docs.ai/docs/guides/goose-cli-commands) 与代码变更保持同步：

1. **抽取** goose 二进制的 CLI 结构（使用 `--help` 输出，确定性）
2. **检测** 版本之间的变更（确定性差异比对）
3. **综合** 生成人类可读的变更文档（AI 驱动）
4. **更新** CLI Commands Guide（AI 驱动）

该自动化会在新版本发布时通过 GitHub Actions 自动运行，也可手动运行以进行测试。

### 快速开始

#### 自动化（GitHub Actions）

新版本发布时该自动化会自动运行。测试说明参见 [TESTING.md](https://github.com/aaif-goose/goose/blob/main/documentation/automation/cli-command-tracking/TESTING.md)。

#### 手动（本地测试）

```bash
# Set the goose repository path
export GOOSE_REPO=/path/to/goose

# Run the complete pipeline with auto-detected versions
./scripts/run-pipeline.sh

# Or specify versions explicitly
./scripts/run-pipeline.sh v1.17.0 v1.19.0

# Or run individual steps:
# 1. Extract CLI structures
./scripts/extract-cli-structure.sh v1.17.0 > output/old-cli-structure.json
./scripts/extract-cli-structure.sh v1.19.0 > output/new-cli-structure.json

# 2. Detect changes
python3 scripts/diff-cli-structures.py output/old-cli-structure.json \
                                       output/new-cli-structure.json \
                                       > output/cli-changes.json

# 3. Generate human-readable change documentation
cd output && goose run --recipe ../recipes/synthesize-cli-changes.yaml

# 4. Update goose-cli-commands.md
cd output && goose run --recipe ../recipes/update-cli-commands.yaml
```

#### 版本检测

未指定版本时，流水线会自动检测版本：

- **旧版本**：倒数第二个最近的发布标签（通过 `gh release list`）
- **新版本**：最近的发布标签，或 `RELEASE_TAG` 环境变量（用于 CI）
- **回退**：如果 `gh` CLI 不可用，则使用 git 标签

要测试未发布的变更，显式传入 `HEAD`：

```bash
./scripts/run-pipeline.sh v1.19.0 HEAD
```

### 架构

#### 模块化流水线设计

该自动化采用**混合方案**：用确定性脚本做数据抽取/差异比对，用 AI Recipe 做分析与文档更新。

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTRACTION (Deterministic)                    │
├─────────────────────────────────────────────────────────────────┤
│  extract-cli-structure.sh → extract-cli-structure.py             │
│  ↓                                                               │
│  cli-structure.json (commands, options, subcommands, aliases)    │
└─────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DIFFING (Deterministic)                       │
├─────────────────────────────────────────────────────────────────┤
│  diff-cli-structures.py                                          │
│  ↓                                                               │
│  cli-changes.json (added, removed, modified commands/options)    │
└─────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                    SYNTHESIS (AI-Powered)                        │
├─────────────────────────────────────────────────────────────────┤
│  synthesize-cli-changes.yaml                                     │
│  ↓                                                               │
│  cli-changes.md (human-readable)                                 │
└─────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                    UPDATE (AI-Powered)                           │
├─────────────────────────────────────────────────────────────────┤
│  update-cli-commands.yaml                                        │
│  ↓                                                               │
│  goose-cli-commands.md (updated) + update-summary.md             │
└─────────────────────────────────────────────────────────────────┘
```

#### 为什么这样设计？

**脚本处理确定性任务：**

- 从特定 git 标签构建 goose
- 运行 `--help` 命令并解析输出
- JSON 结构比较
- 不做解释或推断——直接抽取

**AI Recipe 处理综合与更新：**

- 分析变更并解释其影响
- 生成迁移指引与示例
- 以恰当的格式与上下文更新文档

**好处：**

- **可靠性**：抽取是确定性且可复现的
- **可测试性**：每个阶段都有清晰的输入/输出
- **可维护性**：易于更新单个组件
- **透明性**：中间文件可供检查

#### 数据流

所有阶段通过 `output/` 目录中的 JSON/Markdown 文件通信：

| 文件 | 生产者 | 消费者 | 用途 |
|------|----------|----------|---------|
| `old-cli-structure.json` | `extract-cli-structure.sh` | `diff-cli-structures.py` | 上一版本的 CLI 结构 |
| `new-cli-structure.json` | `extract-cli-structure.sh` | `diff-cli-structures.py` | 当前版本的 CLI 结构 |
| `cli-changes.json` | `diff-cli-structures.py` | `synthesize-cli-changes.yaml` | 检测到的变更（结构化） |
| `cli-changes.md` | `synthesize-cli-changes.yaml` | `update-cli-commands.yaml` | 人类可读的变更文档 |
| `update-summary.md` | `update-cli-commands.yaml` | 人工审查 | 文档更新摘要 |

### 配置

#### 环境变量

| 变量 | 必需 | 默认值 | 说明 |
|----------|----------|---------|-------------|
| `GOOSE_REPO` | 是（本地） | - | goose 仓库根目录路径 |
| `CLI_COMMANDS_PATH` | 否 | `$GOOSE_REPO/documentation/docs/guides/goose-cli-commands.md` | 目标文档文件的完整路径 |
| `RELEASE_TAG` | 否 | - | GitHub Actions 用于指定新版本 |

**示例：**

```bash
export GOOSE_REPO=/Users/you/goose
# CLI_COMMANDS_PATH is auto-constructed from GOOSE_REPO
```

#### 跳过的命令

有些命令被有意排除在抽取与文档跟踪之外。这些在 `config/skip-commands.json` 中配置：

```json
{
  "description": "Commands to skip during extraction (not documented intentionally)",
  "skip_commands": [
    {
      "name": "term",
      "reason": "Terminal integration documented via @goose/@g aliases"
    }
  ]
}
```

要增删被跳过的命令，编辑配置文件即可——无需改动代码。

### 脚本

#### `extract-cli-structure.sh`

从特定 git 标签构建 goose，并使用 `--help` 输出抽取 CLI 结构。

**用法：**

```bash
./scripts/extract-cli-structure.sh [version] > output/cli-structure.json
```

**参数：**

- `version`（可选）：要抽取的 git 标签或提交（默认：HEAD）

**输出：** 包含完整命令树的 JSON，含选项、子命令、别名

**示例：**

```bash
# Extract from current code
./scripts/extract-cli-structure.sh HEAD > output/new-cli-structure.json

# Extract from specific version
./scripts/extract-cli-structure.sh v1.15.0 > output/old-cli-structure.json
```

#### `diff-cli-structures.py`

比较两个 CLI 结构文件并输出检测到的变更。

**用法：**

```bash
python3 scripts/diff-cli-structures.py <old-file> <new-file> > output/cli-changes.json
```

**参数：**

- `old-file`：旧 CLI 结构 JSON 的路径
- `new-file`：新 CLI 结构 JSON 的路径

**输出：** 分类后的变更 JSON：

- `commands.added`：新增命令
- `commands.removed`：删除的命令
- `commands.modified`：变更的命令（选项、描述、别名）
- `breaking_changes`：分类后的破坏性变更

**示例：**

```bash
python3 scripts/diff-cli-structures.py \
  output/old-cli-structure.json \
  output/new-cli-structure.json \
  > output/cli-changes.json
```

### Recipes

#### `synthesize-cli-changes.yaml`

分析检测到的变更并生成人类可读的文档。

**输入：**

- `output/cli-changes.json` - 来自 diff 脚本的检测变更
- `output/old-cli-structure.json` - 上一版本结构
- `output/new-cli-structure.json` - 当前版本结构

**输出：**

- `output/cli-changes.md` - 人类可读的变更文档，包含：
  - 破坏性变更及其迁移指引
  - 新命令及用法示例
  - 变更的命令及细节
  - 非破坏性变更摘要

**用法：**

```bash
cd output
goose run --recipe ../recipes/synthesize-cli-changes.yaml
```

#### `update-cli-commands.yaml`

基于综合出的变更更新 CLI Commands Guide。

**输入：**

- `output/cli-changes.md` - 来自综合 Recipe 的变更文档
- `goose-cli-commands.md` - 目标文档文件（路径来自 `CLI_COMMANDS_PATH` 或 `GOOSE_REPO` 环境变量）

**输出：**

- 已应用变更的更新版 `goose-cli-commands.md`
- `output/update-summary.md` - 供审查的变更摘要

**用法：**

```bash
export CLI_COMMANDS_PATH=/path/to/goose-cli-commands.md
cd output
goose run --recipe ../recipes/update-cli-commands.yaml
```

### 目录结构

```
cli-command-tracking/
├── README.md                           # This file
├── TESTING.md                          # Testing guide for GitHub Actions workflow
├── .gitignore                          # Excludes output/ directory
├── config/                             # Configuration files
│   └── skip-commands.json              # Commands to exclude from tracking
├── scripts/                            # Extraction and diff scripts
│   ├── extract-cli-structure.sh        # Wrapper that builds goose and runs Python
│   ├── extract-cli-structure.py        # Python script to parse --help output
│   ├── diff-cli-structures.py          # Compare structures and detect changes
│   └── run-pipeline.sh                 # End-to-end pipeline runner
├── recipes/                            # AI recipes
│   ├── synthesize-cli-changes.yaml     # Generate change docs
│   └── update-cli-commands.yaml        # Update documentation
├── .github/workflows/                  # GitHub Actions workflow
│   └── docs-update-cli-ref.yml         # Workflow definition
└── output/                             # Generated files (gitignored)
    ├── old-cli-structure.json          # Previous version structure
    ├── new-cli-structure.json          # Current version structure
    ├── cli-changes.json                # Detected changes (structured)
    ├── cli-changes.md                  # Change documentation (human-readable)
    ├── update-summary.md               # Documentation update summary
    └── pipeline.log                    # Pipeline execution log
```

### GitHub Actions 工作流

该自动化通过 `.github/workflows/docs-update-cli-ref.yml` 运行：

- **触发**：新版本发布时自动触发，或为测试手动触发
- **过程**：为两个版本构建 goose，抽取 CLI 结构，检测变更，更新文档
- **输出**：如检测到变更，则创建一个包含更新后 `goose-cli-commands.md` 的 PR
- **测试**：详细测试说明参见 [TESTING.md](https://github.com/aaif-goose/goose/blob/main/documentation/automation/cli-command-tracking/TESTING.md)

### 跟踪的内容

#### 命令

- ✅ 命令的新增/删除
- ✅ 命令描述变更
- ✅ 命令别名的新增/删除
- ✅ 子命令的新增/删除

#### 选项

- ✅ 选项的新增/删除
- ✅ 选项帮助文本变更
- ✅ 默认值变更
- ✅ 可能取值变更（枚举）
- ✅ 短/长标志变更

#### 破坏性变更（自动分类）

- 命令被删除（高严重度）
- 选项被删除（高严重度）
- 选项被重命名（高严重度）
- 默认值变更（中严重度）
- 枚举取值被删除（高严重度）
- 别名被删除（中严重度）

### 维护

修改该自动化时：

1. **先在本地测试**：用测试版本运行 `./scripts/run-pipeline.sh`
2. **验证输出**：将生成的文件与实际 CLI 变更对照
3. **在 fork 中测试**：以 dry-run 模式使用 GitHub Actions 工作流
4. **记录变更**：用设计决策更新本 README

### 相关文档

- [TESTING.md](https://github.com/aaif-goose/goose/blob/main/documentation/automation/cli-command-tracking/TESTING.md) - 如何测试 GitHub Actions 工作流
- [Automation Overview](https://github.com/aaif-goose/goose/blob/main/documentation/automation/README.md) - 所有自动化项目
- [CLI Commands Guide](https://github.com/aaif-goose/goose/blob/main/documentation/docs/guides/goose-cli-commands.md) - 目标文档

---

## 测试指南（CLI 命令追踪）

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/automation/cli-command-tracking/TESTING.md

本指南说明如何在本地和 GitHub Actions 中测试 CLI 命令追踪自动化。

### 前置条件

- Python 3.7+
- Rust 工具链（用于构建 goose）
- jq（用于 JSON 处理）
- 已安装 goose CLI（用于运行 Recipe）
- 可访问 goose 仓库的 Git

### 本地测试

#### 步骤 1：搭建环境

```bash
cd /path/to/cli-command-tracking

# Set the goose repository path
export GOOSE_REPO=/path/to/goose

# Create output directory
mkdir -p output
```

#### 步骤 2：测试抽取脚本

用特定版本测试抽取：

```bash
# Test with a release version
./scripts/extract-cli-structure.sh v1.19.0 > output/test-extraction.json

# Verify output
jq '.version, .commands | length' output/test-extraction.json

# Inspect a specific command
jq '.commands[] | select(.name == "session")' output/test-extraction.json

# Verify skipped commands are excluded
jq '.commands[].name' output/test-extraction.json | grep -v term
```

**预期输出：**

- 合法的 JSON 结构
- 版本号被正确抽取
- 捕获所有命令（14+ 个命令，排除像 `term` 这类被跳过的命令）
- 子命令正确嵌套
- 选项连同所有字段被解析

**常见问题：**

- 未安装 Rust：通过 rustup 安装
- 构建失败：检查 Cargo.toml 依赖
- 超时错误：如需要，增大脚本中的超时
- 钥匙串提示：见下文「钥匙串访问」一节

#### 步骤 3：测试 diff 脚本

比较两个 CLI 结构：

```bash
# Extract from two versions
./scripts/extract-cli-structure.sh v1.14.0 > output/old-cli-structure.json
./scripts/extract-cli-structure.sh v1.15.0 > output/new-cli-structure.json

# Run diff
python3 scripts/diff-cli-structures.py \
  output/old-cli-structure.json \
  output/new-cli-structure.json \
  > output/cli-changes.json

# Check results
jq '.has_changes, .summary' output/cli-changes.json

# View specific changes
jq '.changes.commands.added' output/cli-changes.json
jq '.changes.commands.modified[0]' output/cli-changes.json
jq '.breaking_changes' output/cli-changes.json
```

**预期输出：**

- 若版本不同，则 `has_changes: true`
- 含变更计数的摘要
- 结构化格式的详细变更
- 破坏性变更已分类

#### 步骤 4：测试 AI 综合 Recipe

生成人类可读的文档：

```bash
cd output

# Run synthesis recipe
goose run --recipe ../recipes/synthesize-cli-changes.yaml

# Check output
ls -lh cli-changes.md
head -50 cli-changes.md
```

**预期输出：**

- 创建 `cli-changes.md` 文件
- Markdown 格式正确
- 破坏性变更列在最前
- 为复杂变更提供示例
- 测试 AI 工作流时，确保通过 `store_comment` 工具发送的任何内容都不包含三反引号代码围栏（```），尽管像 `cli-changes.md` 这类 markdown 文件中的普通反引号是允许的。

#### 步骤 5：测试文档更新 Recipe

更新实际文档：

```bash
cd output

# Set path to documentation file
export CLI_COMMANDS_PATH=/path/to/goose/documentation/docs/guides/goose-cli-commands.md

# Run update recipe
goose run --recipe ../recipes/update-cli-commands.yaml

# Check outputs
ls -lh update-summary.md
cat update-summary.md

# Verify documentation was updated
git diff $CLI_COMMANDS_PATH
```

#### 步骤 6：测试完整流水线

运行完整的端到端流水线：

```bash
cd /path/to/cli-command-tracking

# Set documentation path (optional - only needed for update step)
export CLI_COMMANDS_PATH=/path/to/goose/documentation/docs/guides/goose-cli-commands.md

# Run pipeline
./scripts/run-pipeline.sh v1.14.0 v1.15.0

# Check all outputs
ls -lh output/
```

**预期输出：**

- 创建所有中间文件
- 流水线无错误完成
- 摘要显示检测到变更
- 生成 `cli-changes.md`

### GitHub Actions 测试

#### 在 fork 中测试

1. **Fork 仓库**（如尚未完成）

2. **把自动化文件复制**到你的 fork：

   ```bash
   cp -r /path/to/cli-command-tracking \
         /path/to/forked-goose/documentation/automation/
   
   cp /path/to/goose/.github/workflows/docs-update-cli-ref.yml \
      /path/to/forked-goose/.github/workflows/
   ```

3. **在你的 fork 中设置 secret**：

   - 进入 Settings → Secrets and variables → Actions
   - 添加 `ANTHROPIC_API_KEY` secret

4. **设置变量**（可选）：

   - 添加 `GOOSE_PROVIDER` 变量（默认：anthropic）
   - 添加 `GOOSE_MODEL` 变量（默认：claude-opus-4-5）

5. **手动触发工作流**：

   - 进入 Actions → "Update CLI Documentation"
   - 点击 "Run workflow"
   - 设置 `dry_run: true` 以进行测试
   - 可选择指定要比较的版本

#### Dry Run 模式

在不创建 PR 的情况下测试：

1. 以 `dry_run: true` 触发工作流
2. 在工作流日志中查看输出
3. 下载 artifact 以检查生成的文件
4. 验证变更是否正确

#### 工作流输入

| 输入 | 说明 | 默认值 |
|-------|-------------|---------|
| `old_version` | 上一版本标签 | 从 release 自动检测 |
| `new_version` | 新版本标签 | HEAD |
| `dry_run` | 生成文件但不创建 PR | true |

#### 查看 Artifacts

工作流运行后：

1. 进入工作流运行页面
2. 下载 artifacts ZIP
3. 解压并查看：
   - `old-cli-structure.json` - 上一版 CLI 结构
   - `new-cli-structure.json` - 新版 CLI 结构
   - `cli-changes.json` - 检测到的变更
   - `cli-changes.md` - 人类可读的文档
   - `pipeline.log` - 执行日志

### 用已知变更测试

要验证自动化是否正确工作，请用有已知 CLI 变更的版本进行测试。

#### 寻找测试版本

```bash
cd /path/to/goose

# Check git history for CLI changes
git log --oneline --all -- crates/goose-cli/src/cli.rs | head -20

# Look for commits that added/removed/modified commands
git show <commit-hash>:crates/goose-cli/src/cli.rs | grep "enum Command" -A 30
```

#### 测试用例：新增命令

如果你知道某个版本新增了命令：

```bash
./scripts/run-pipeline.sh v1.13.0 v1.14.0
jq '.changes.commands.added' output/cli-changes.json
```

#### 测试用例：选项被修改

如果你知道某个版本修改了选项：

```bash
./scripts/run-pipeline.sh v1.14.0 v1.15.0
jq '.changes.commands.modified' output/cli-changes.json
```

#### 测试用例：无变更

用相同版本测试（应显示无变更）：

```bash
./scripts/run-pipeline.sh v1.14.0 v1.14.0
jq '.has_changes' output/cli-changes.json
# Should output: false
```

### 验证清单

在认为该自动化完成之前：

#### 抽取脚本

- [ ] 处理所有命令类型（简单、含子命令、含别名）
- [ ] 解析所有选项类型（短、长、带值、标志）
- [ ] 捕获默认值与可能取值
- [ ] 对没有描述的命令也能工作
- [ ] 处理嵌套子命令（2 层及以上）
- [ ] 能正确从 git 标签构建 goose

#### Diff 脚本

- [ ] 检测新增命令
- [ ] 检测删除的命令
- [ ] 检测修改的选项
- [ ] 检测变更的帮助文本
- [ ] 检测变更的默认值
- [ ] 检测变更的可能取值
- [ ] 正确分类破坏性变更

#### AI Recipes

- [ ] 生成可读的文档
- [ ] 提供迁移指引
- [ ] 使用正确的 markdown 格式
- [ ] 避免反引号（安全约束）
- [ ] 包含相关示例
- [ ] 使用 text_editor 工具写入文件

#### 流水线

- [ ] 端到端运行无错误
- [ ] 处理「无变更」情形
- [ ] 创建所有预期的输出文件
- [ ] 正确过滤 goose 会话输出

#### GitHub Actions

- [ ] 工作流正确触发
- [ ] 为两个版本构建 goose
- [ ] 上传 artifacts
- [ ] 检测到变更时创建 PR
- [ ] 遵循 dry_run 模式
- [ ] 在 fork 中可用（获取上游标签）

### 故障排查

#### 钥匙串访问（macOS）

在 macOS 上，运行 `goose --help` 或 `goose --version` 可能会提示钥匙串访问。这是因为 goose 在启动时会尝试访问已存储的凭据。

**本地变通：** 在提示时允许钥匙串访问。

**CI 注意事项：** GitHub Actions runner 没有钥匙串，因此这可能需要处理。查看现有 goose 工作流中的模式——可能存在 `keyring: false` 配置项或环境变量来禁用凭据加载。

**TODO：** 调查这是否会阻塞 CI 执行并记录解决方案。

#### 旧版本构建失败

有些旧版本可能有不同的依赖：

```bash
# Check if version exists
git tag | grep v1.14.0

# Try building manually
git worktree add /tmp/goose-test v1.14.0
cd /tmp/goose-test
cargo build --release
```

#### 抽取超时

增大 `extract-cli-structure.py` 中的超时：

```python
result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)  # Increase from 10
```

#### Diff 显示意外变更

检查帮助文本格式是否变化：

```bash
# Compare raw help output
./old-goose session --help > old-help.txt
./new-goose session --help > new-help.txt
diff old-help.txt new-help.txt
```

#### AI Recipe 失败

检查输入文件存在且合法：

```bash
ls -lh output/cli-changes.json output/old-cli-structure.json output/new-cli-structure.json
jq empty output/cli-changes.json  # Validates JSON
```

#### 工作流在 fork 中失败

确保：

- `ANTHROPIC_API_KEY` secret 已设置
- 已获取上游标签（工作流会自动完成）
- Rust 工具链可用

### 人工验证

自动化运行后，手动验证：

1. **准确性**：检测到的变更是否与实际 CLI 变更一致？
2. **完整性**：是否捕获了所有变更？
3. **文档**：更新后的文档是否准确清晰？
4. **示例**：所有示例是否仍然可用？
5. **风格**：格式是否与现有文档一致？

### 测试数据

保留测试数据用于回归测试：

```bash
# Save known-good outputs
mkdir -p test-data
cp output/cli-changes.json test-data/v1.14.0-to-v1.15.0-changes.json
cp output/cli-changes.md test-data/v1.14.0-to-v1.15.0-changes.md
```

用这些数据验证未来的变更不会破坏现有功能。

---

## 为 goose 撰写博客文章

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/blog/README.md

本指南说明如何为 goose 文档站撰写和组织博客文章。

### 快速开始

1. 克隆 goose 仓库：

```bash
git clone https://github.com/aaif-goose/goose.git
cd goose
```

2. 安装依赖：

```bash
cd documentation
npm install
```

### 目录结构

博客文章按日期组织，格式如下：

```
YYYY-MM-DD-post-title/
├── index.md
└── images/
```

示例：

```
2025-05-22-llm-agent-readiness/
├── index.md
└── llm-agent-test.png
```

### Frontmatter

每篇博客文章必须以 YAML frontmatter 开头，其中包含：

```yaml
---
title: Your Blog Post Title
description: A brief description of your post (1-2 sentences)
authors: 
    - your_author_id
---
```

`authors` 字段应与 `authors.yml` 文件中你的 ID 匹配。可以列出多位作者。[作者信息详见此处](#author-information)。

### 头图

在 frontmatter 之后，用 Markdown 包含一张头图：

```markdown
![blog cover](your-image.png)
```

头图应满足：

- 与文章内容相关
- 高质量（推荐尺寸：1200 x 600 px）
- 存放在文章目录中
- 命名具有描述性

### 内容结构

#### 引言

在 truncate 标签之前，用 1-2 段话介绍主题。这将是博客索引页上显示的内容。

#### Truncate 标签

在引言之后添加 truncate 标签，以创建「阅读更多」的截断：

```markdown
<!-- truncate -->
```

#### 标题

用标题分层组织内容：

- `#`（H1）- 仅用于 frontmatter 中的文章标题
- `##`（H2）- 主要小节
- `###`（H3）- 子小节
- `####`（H4）- 次要小节（这些不会显示在右侧导航栏上）

#### 代码块

使用带语言标注的围栏代码块：

````markdown
```javascript
// Your code here
```
````

#### 图片

用 Markdown 包含额外图片：

```markdown
![descriptive alt text](image-name.png)
```

### 社交媒体标签

在文章末尾，包含以下用于社交媒体分享的 meta 标签：

```html
<head>
  <meta property="og:title" content="Your Blog Post Title" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/blog/YYYY/MM/DD/post-slug" />
  <meta property="og:description" content="Your blog post description" />
  <meta property="og:image" content="https://goose-docs.ai/assets/images/your-image.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta name="twitter:title" content="Your Blog Post Title" />
  <meta name="twitter:description" content="Your blog post description" />
  <meta name="twitter:image" content="https://goose-docs.ai/assets/images/your-image.png" />
</head>
```

### 作者信息

要把自己添加为作者：

1. 编辑博客目录中的 `authors.yml`
2. 按以下格式添加你的信息：

```yaml
your_author_id:
  name: Your Full Name
  title: Your Title
  image_url: https://avatars.githubusercontent.com/u/your_github_id?v=4
  url: https://your-website.com  # Optional
  page: true
  socials:
    linkedin: your_linkedin_username
    github: your_github_username
    x: your_twitter_handle
    bluesky: your_bluesky_handle  # Optional
```

### 最佳实践

1. **写作风格**
   - 使用清晰简洁的语言
   - 拆分长段落
   - 在相关处包含代码示例
   - 用图片说明复杂概念

2. **技术内容**
   - 包含可运行的代码示例
   - 说明前置条件
   - 链接到相关文档
   - 发布前测试代码片段

3. **格式**
   - 使用一致的间距
   - 为图片包含 alt 文本
   - 用小标题拆分内容
   - 在合适处使用列表与表格

4. **审查流程**
   - 校对拼写与语法
   - 验证所有链接可用
   - 检查图片路径
   - 测试代码示例
   - 校验 frontmatter 语法

### 预览博客文章

要在本地预览博客文章：

1. 确保你在 documentation 目录中：

```bash
cd documentation
```

2. 启动开发服务器：

```bash
npm start
```

3. 打开浏览器并访问：

```
http://localhost:3000/blog
```

开发服务器特性：

- 热重载（改动立即生效）
- 完整站点导航预览
- 移动端响应式测试
- 社交媒体预览测试

如果你在服务器运行期间修改了博客文章，页面会自动刷新以显示更新。

#### 预览故障排查

如果遇到问题：

1. 确保所有依赖已安装：

```bash
npm install
```

2. 清除缓存并重启：

```bash
npm run clear
npm start
```

3. 校验你的 frontmatter 语法正确（无制表符、缩进正确）
4. 检查所有图片路径相对于文章目录是否正确

---

## Dockerfile（Docker 镜像构建）

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/docker/Dockerfile

该文件是 goose 文档中 Docker 相关页面引用的镜像构建文件，采用多阶段构建：

- **构建阶段**（基于 `rust:bullseye`）：安装 Node.js 与 `protobuf-compiler`，把整个项目复制到 `/usr/src/goose`，随后执行 `cargo build --release`。
- **运行时阶段**（基于 `ubuntu:22.04`）：安装运行时库（含 DBus 与 keyring 支持）、Node.js 以及常用开发工具，并从构建阶段把编译好的 `goose` 二进制复制到 `/usr/local/bin/`。
- 还创建了 `/usr/local/bin/entrypoint.sh` 包装脚本以初始化 DBus 会话与 keyring，并配置了 git 默认分支、默认编辑器以及若干 shell 别名。

完整原文如下：

```dockerfile
# Build stage
FROM rust:bullseye AS builder

SHELL ["/bin/bash", "-c"]

# Install Node.js and any missing dependencies
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get update && apt-get install -y \
    nodejs \
    libdbus-1-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a new directory for the app
WORKDIR /usr/src/goose

# Copy the entire project
COPY . .

RUN apt-get update && apt-get install -y protobuf-compiler

# Build the project
RUN cargo build --release

# Runtime stage
FROM ubuntu:22.04

# Configure non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install runtime libraries with DBus and keyring support
RUN apt-get update && apt-get install -y \
    # Runtime dependencies
    ca-certificates \
    curl \
    gnupg \
    # DBus and keyring
    dbus \
    dbus-x11 \
    gnome-keyring \
    libsecret-1-0 \
    libsecret-tools \
    # Other dependencies
    libssl3 \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get update && apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install common development tools
RUN apt-get update && apt-get install -y \
    # Version control
    git \
    # Text processing and search
    ripgrep \
    fd-find \
    fzf \
    # File manipulation
    jq \
    # Network tools
    wget \
    # Process management
    htop \
    # System utilities
    sudo \
    # Text editors
    nano \
    vim \
    # Archive tools
    zip \
    unzip \
    # Build essentials
    build-essential \
    # Python
    python3 \
    python3-pip \
    # Java
    openjdk-17-jdk \
    # Additional tools
    tree \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Install uv using curl
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Install JBang using curl
RUN curl -Ls https://sh.jbang.dev | bash -s - app setup

# Copy the built binaries
COPY --from=builder /usr/src/goose/target/release/goose /usr/local/bin/

# Create a wrapper script to initialize DBus and keyring
RUN echo '#!/bin/bash\n\
# Start DBus session daemon if not running\n\
if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then\n\
  eval $(dbus-launch --sh-syntax)\n\
  export DBUS_SESSION_BUS_ADDRESS\n\
fi\n\
\n\
# Initialize keyring if needed\n\
if [ -z "$GNOME_KEYRING_CONTROL" ]; then\n\
  eval $(gnome-keyring-daemon --start)\n\
  export GNOME_KEYRING_CONTROL SSH_AUTH_SOCK\n\
fi\n\
\n\
' > /usr/local/bin/entrypoint.sh && \
chmod +x /usr/local/bin/entrypoint.sh

# Set up some basic git config
RUN git config --global init.defaultBranch main && \
    git config --global core.editor "vim"

# Add some helpful aliases
RUN echo 'alias ll="ls -la"' >> ~/.bashrc && \
    echo 'alias fd=fdfind' >> ~/.bashrc

# Add JBang to PATH
RUN echo 'export PATH="$HOME/.jbang/bin:$PATH"' >> ~/.bashrc
```

---

## docker-compose.yml（Docker Compose 配置）

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/docker/docker-compose.yml

该文件是 goose 文档中 Docker 相关页面引用的 Docker Compose 配置，用于把 goose 作为容器化的 CLI 运行。

- **服务 `goose-cli`**：以仓库根目录为构建上下文、`documentation/docs/docker/Dockerfile` 为 Dockerfile 构建镜像；把宿主机仓库目录挂载到 `/root/workspace`，并挂载 `goose-config` 卷、`~/.gitconfig` 与 `~/.ssh`。
- **环境变量**：设置 `GOOSE_HOME`、`EDITOR`、git 作者信息，以及 `GOOGLE_API_KEY`、`GOOSE_PROVIDER=google`、`GOOSE_MODEL=gemini-2.0-flash-exp`；并透传 DBus、keyring 与 SSH agent 相关变量。
- **交互**：开启 `stdin_open` 与 `tty`，入口点为 `/bin/bash`。

完整原文如下：

```yaml
services:
  goose-cli:
    build:
      context: ../../..
      dockerfile: documentation/docs/docker/Dockerfile
      args:
        USER_ID: ${UID:-1000}
    volumes:
      # Mount user's directory with read-write access
      - ../../..:/root/workspace
      - goose-config:/root/.goose
      # Mount git config
      - ~/.gitconfig:/root/.gitconfig:ro
      # Mount SSH keys
      - ~/.ssh:/root/.ssh:ro
    working_dir: /root/workspace
    environment:
      - GOOSE_HOME=/root/.goose
      # Set default editor
      - EDITOR=vim
      # Preserve git author info
      - GIT_AUTHOR_NAME=${GIT_AUTHOR_NAME:-Goose User}
      - GIT_AUTHOR_EMAIL=${GIT_AUTHOR_EMAIL:-goose@example.com}
      # Set GOOGLE_API_KEY to your own API key
      - GOOGLE_API_KEY="XXX"
      - GOOSE_PROVIDER=google
      - GOOSE_MODEL=gemini-2.0-flash-exp
      - DBUS_SESSION_BUS_ADDRESS
      - GNOME_KEYRING_CONTROL
      - SSH_AUTH_SOCK
    stdin_open: true
    tty: true
    entrypoint: ["/bin/bash"]

volumes:
  goose-config:
```

---

## _category_.json：experimental

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/experimental/_category_.json

该目录在侧栏中的显示名为「实验性」（`label: "Experimental"`），排序位置为 8，链接类型为 `doc`，指向文档 `experimental/index`。

```json
{
  "label": "Experimental",
  "position": 8,
  "link": {
    "type": "doc",
    "id": "experimental/index"
  }
}
```

---

## _category_.json：gdk

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/gdk/_category_.json

该目录在侧栏中的显示名为「GDK」（`label: "GDK"`，产品名不译），排序位置为 3，链接类型为 `doc`，指向文档 `gdk/index`。

```json
{
  "label": "GDK",
  "position": 3,
  "link": {
    "type": "doc",
    "id": "gdk/index"
  }
}
```

---

## _category_.json：gdk/acp

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/gdk/acp/_category_.json

该目录在侧栏中的显示名为「ACP」（`label: "ACP"`，产品名不译），排序位置为 2，链接类型为 `doc`，指向文档 `gdk/acp/index`。

```json
{
  "label": "ACP",
  "position": 2,
  "link": {
    "type": "doc",
    "id": "gdk/acp/index"
  }
}
```

---

## _category_.json：gdk/sdk

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/gdk/sdk/_category_.json

该目录在侧栏中的显示名为「SDK」（`label: "SDK"`，产品名不译），排序位置为 1，链接类型为 `doc`，指向文档 `gdk/sdk/index`。

```json
{
  "label": "SDK",
  "position": 1,
  "link": {
    "type": "doc",
    "id": "gdk/sdk/index"
  }
}
```

---

## _category_.json：getting-started

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/getting-started/_category_.json

该目录在侧栏中的显示名为「快速开始」（`label: "Getting Started"`），排序位置为 2，链接类型为 `generated-index`，其描述为「Get up to speed quickly with goose」（快速上手 goose）。

```json
{
  "label": "Getting Started",
  "position": 2,
  "link": {
    "type": "generated-index",
    "description": "Get up to speed quickly with goose"
  }
}
```

---

## _category_.json：goose-architecture

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/goose-architecture/_category_.json

该目录在侧栏中的显示名为「架构概览」（`label: "Architecture Overview"`），排序位置为 7，链接类型为 `generated-index`，其描述为「Extend goose functionalities with extensions and custom configurations」（通过扩展与自定义配置来扩展 goose 功能）。

```json
{
    "label": "Architecture Overview",
    "position": 7,
    "link": {
      "type": "generated-index",
      "description": "Extend goose functionalities with extensions and custom configurations"
    }
  }
```

---

## _category_.json：guides

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/guides/_category_.json

该目录在侧栏中的显示名为「指南」（`label: "Guides"`），排序位置为 4，链接类型为 `generated-index`，其描述为「Learn essential tips and recommendations for using goose」（了解使用 goose 的关键技巧与建议）。

```json
{
  "label": "Guides",
  "position": 4,
  "link": {
    "type": "generated-index",
    "description": "Learn essential tips and recommendations for using goose"
  }
}
```

---

## _category_.json：guides/context-engineering

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/guides/context-engineering/_category_.json

该目录在侧栏中的显示名为「上下文工程」（`label: "Context Engineering"`），排序位置为 3，链接类型为 `doc`，指向文档 `guides/context-engineering/index`。

```json
{
  "label": "Context Engineering",
  "position": 3,
  "link": {
    "type": "doc",
    "id": "guides/context-engineering/index"
  }
}
```

---

## _category_.json：guides/interactive-chat

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/guides/interactive-chat/_category_.json

该目录在侧栏中的显示名为「MCP 应用」（`label: "MCP Apps"`），排序位置为 55，链接类型为 `doc`，指向文档 `guides/interactive-chat/index`。

```json
{
  "label": "MCP Apps",
  "position": 55,
  "link": {
    "type": "doc",
    "id": "guides/interactive-chat/index"
  }
}
```

---

## _category_.json：guides/managing-tools

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/guides/managing-tools/_category_.json

该目录在侧栏中的显示名为「管理工具」（`label: "Managing Tools"`），排序位置为 4，链接类型为 `doc`，指向文档 `guides/managing-tools/index`。

```json
{
  "label": "Managing Tools",
  "position": 4,
  "link": {
    "type": "doc",
    "id": "guides/managing-tools/index"
  }
}
```

---

## _category_.json：guides/multi-model

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/guides/multi-model/_category_.json

该目录在侧栏中的显示名为「多模型配置」（`label: "Multi-Model Config"`），排序位置为 100，其描述为「Configure multiple models and providers for model-switching strategies.」（为模型切换策略配置多个模型与提供方）。

```json
{
  "label": "Multi-Model Config",
  "position": 100,
  "description": "Configure multiple models and providers for model-switching strategies."
}
```

---

## _category_.json：guides/recipes

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/guides/recipes/_category_.json

该目录在侧栏中的显示名为「Recipe」（`label: "Recipes"`，术语保留英文），排序位置为 3，链接类型为 `doc`，指向文档 `guides/recipes/index`。

```json
{
  "label": "Recipes",
  "position": 3,
  "link": {
    "type": "doc",
    "id": "guides/recipes/index"
  }
}
```

---

## _category_.json：guides/security

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/guides/security/_category_.json

该目录在侧栏中的显示名为「安全」（`label: "Security"`），排序位置为 43，链接类型为 `doc`，指向文档 `guides/security/index`。

```json
{
  "label": "Security",
  "position": 43,
  "link": {
    "type": "doc",
    "id": "guides/security/index"
  }
}
```

---

## _category_.json：guides/sessions

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/guides/sessions/_category_.json

该目录在侧栏中的显示名为「管理会话」（`label: "Managing Sessions"`），排序位置为 1，链接类型为 `doc`，指向文档 `guides/sessions/index`。

```json
{
  "label": "Managing Sessions",
  "position": 1,
  "link": {
    "type": "doc",
    "id": "guides/sessions/index"
  }
}
```

---

## _category_.json：mcp

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/mcp/_category_.json

该目录在侧栏中的显示名为「MCP 服务器」（`label: "MCP Servers"`），排序位置为 6，链接类型为 `generated-index`，其描述为「How to integrate and use MCP servers as goose extensions」（如何将 MCP 服务器作为 goose 扩展来集成与使用）。

```json
{
  "label": "MCP Servers",
  "position": 6,
  "link": {
    "type": "generated-index",
    "description": "How to integrate and use MCP servers as goose extensions"
  }
}
```

---

## _category_.json：troubleshooting

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/troubleshooting/_category_.json

该目录在侧栏中的显示名为「故障排查」（`label: "Troubleshooting"`），排序位置为 40，其描述为「Get help, report issues, and troubleshoot common problems with goose.」（获取帮助、报告问题并排查 goose 的常见问题）。

```json
{
  "label": "Troubleshooting",
  "position": 40,
  "description": "Get help, report issues, and troubleshoot common problems with goose."
}
```

---

## _category_.json：tutorials

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/docs/tutorials/_category_.json

该目录在侧栏中的显示名为「教程」（`label: "Tutorials"`），排序位置为 5，链接类型为 `generated-index`，其描述为「How to use goose in various ways」（如何以多种方式使用 goose）。

```json
{
  "label": "Tutorials",
  "position": 5,
  "link": {
    "type": "generated-index",
    "description": "How to use goose in various ways"
  }
}
```

---

## Community All Stars 月度更新指南

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/src/pages/community/data/README.md

该目录包含社区页面上 Community All Stars 版块的数据文件。

### 月度更新流程

#### 步骤 1：创建新的月份数据文件

1. 复制 `template.json`，创建一个名为 `MONTH-YEAR.json` 的新文件（例如 `june-2025.json`）
2. 更新新文件中的数据：

```json
{
  "month": "June 2025",
  "featuredContributors": [
    {
      "name": "John Doe",
      "handle": "johndoe"
    }
  ],
  "risingStars": [
    {
      "name": "Jane Smith", 
      "handle": "janesmith"
    }
  ],
  "leaderboard": [
    { "handle": "johndoe", "rank": 1, "medal": "🥇" },
    { "handle": "janesmith", "rank": 2, "medal": "🥈" },
    { "handle": "contributor3", "rank": 3, "medal": "🥉" },
    { "handle": "contributor4", "rank": 4 }
  ]
}
```

#### 步骤 2：更新配置

1. 打开 `config.json`
2. 把新月份加入 `availableMonths` 数组：

```json
{
  "availableMonths": [
    {
      "id": "june-2025",
      "display": "June 2025", 
      "file": "june-2025.json"
    }
  ],
  "defaultMonth": "june-2025"
}
```

3. 把 `defaultMonth` 更新为新月份的 ID

#### 步骤 3：更新代码导入

1. 打开 `../pages/community.tsx`
2. 为新数据文件添加导入：

```typescript
import june2025Data from "../data/community/june-2025.json";
```

3. 把新数据加入 `communityDataMap`：

```typescript
const communityDataMap = {
  "june-2025": june2025Data,
  // ... other months
};
```

### 数据格式

#### Community Stars 与 Team Stars

- `name`：完整显示名
- `handle`：GitHub 用户名（不含 @）

#### Monthly Leaderboard

- `handle`：GitHub 用户名（不含 @）
- `rank`：名次编号（1、2、3 等）
- `medal`：仅用于前三名（"🥇"、"🥈"、"🥉"）

### 版块映射

JSON 数据映射到以下页面版块：

- `featuredContributors` → **Community Stars** 版块
- `risingStars` → **Team Stars** 版块
- `leaderboard` → **Monthly Leaderboard** 版块

### 提示

- 头像图片会根据 GitHub 用户名自动生成
- GitHub 链接会根据 handle 自动创建
- medal 字段可选——只为前三名包含
- leaderboard 条目数量不限
- 名称与 handle 区分大小写

### 文件结构

```
community/
├── config.json          # Main configuration
├── template.json        # Template for new months
├── april-2025.json     # April 2025 data
├── may-2025.json       # May 2025 data
└── README.md           # This file
```

### 月度快速清单

- [ ] 把 template.json 复制为新的月份文件
- [ ] 填写 Community Stars 的贡献者数据
- [ ] 填写 Team Stars 的贡献者数据
- [ ] 更新 Monthly Leaderboard 排名
- [ ] 用新月份更新 config.json
- [ ] 向 community.tsx 添加导入
- [ ] 加入 communityDataMap
- [ ] 在本地测试页面

---

## goose 资助计划

> 原文：https://block.github.io/goose/grants

![](https://block.github.io/goose/img/goose-grant-program.png)

我们设立了一项资助计划，以加速 goose 在开源社区中的发展。如果你相信智能体 AI 应当是开放且人人可用的未来，我们邀请你与我们一起塑造这一未来。

<Link to="https://forms.gle/psHBhj8xFY8q1nHP7" target="_blank" rel="noopener noreferrer">
    ##  → 申请 goose 资助
</Link>

<br/>
### 什么样的提案算是好提案
<br/>

我们在寻找清晰、有说服力且雄心勃勃的想法，它们要与 goose 的价值观一致：开放、模块化、赋能用户。

我们很希望看到探索与 AI 智能体交互新方式的提案。以下只是一些示例：

- **新的交互范式：** 通过草图（白板！）、摄像头、关注情绪的语音交互或其他多模态交互来与 goose 互动
- **自飞行：** 通过加入长时间运行的后台模式、试验新的中间状态、深度规划以及支持此类操作的工具来提升自主性
- **自我改进的智能体：** absolute zero、godel Darwin machine 与 alphaevolve 等工作展示了智能体如何自我改进。帮助 goose 重写它的系统提示词、它的 MCP 服务器，也许还有它自己的代码
- **自动化一切：** 给 goose 提供与真实世界交互的工具，用于家庭自动化、机器人或 3D 打印。

最重要的是，我们想资助与这些价值观一致、并展现出开源优先心态的工作。


<br/>
### 资助细节
<br/>

- **项目周期：** 12 个月
- **资助金额：** 每笔资助 100,000 美元
- **结构：** 资助以里程碑为基础，包含定期检查、交付物与付款

_受适用法律约束_

<br/>
### 常见问题
<br/>
**提案何时被受理？**

我们滚动审查提案。没有固定截止日期，不过更早提交会增加你被纳入当前审查周期的机会。

**你们会受理多少份提案？**

在资源允许的范围内，我们会支持尽可能多的、与使命一致的有力项目。

**我的资助在 12 个月后可以续期吗？**

有可能可以。我们可能会根据进展、影响力与契合度来延长或续期资助。续期并不保证，将逐案评估。

**获得资助会带来在 goose 或 AAIF 的工作机会吗？**

不会。资助不是雇佣关系，也不意味着未来会录用。不过，与 goose 或 AAIF 团队的合作可能会因有影响力的工作而自然产生。

**工作如何被审查？**

每个资助项目都会定义清晰的交付物与里程碑。进展将由 goose 团队及选定的外部评审人按季度审查。

**付款如何安排？**

付款以里程碑为基础，按季度发放，前提是进展更新令人满意。

**资助在全球范围内可用吗？**

是的。我们接受来自全球个人与团队的提案。付款以美元进行，但在可行的情况下，我们会与你配合以适配你当地的货币与支付偏好。

**我可以提出多个项目吗？**

可以。只要项目之间差异显著，你可以提交多份申请。

**谁可以申请？**

任何人都可以。我们欢迎个人或小团队，前提是该工作尚未由雇主或客户资助，且受适用法律约束。有开源经验是加分项，但非必需。如果你对开源充满热情并有一个想法——哪怕只是一个草图——我们都鼓励你联系我们。

**我该如何申请？**

[在此提交你的申请](https://forms.gle/psHBhj8xFY8q1nHP7)


<br/>
### 联系我们
<br/>

如果你还有其他问题，欢迎在 [Discord](https://discord.com/channels/1287729918100246654/1397943505216868444) 的 #goose-grants 论坛中联系我们。

<head>
  <meta property="og:title" content="goose grant program" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://goose-docs.ai/grants" />
  <meta property="og:description" content="$100K grants for open source devs building the future of agentic AI." />
  <meta property="og:image" content="https://goose-docs.ai/img/goose-grant-program.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta property="twitter:domain" content="goose-docs.ai" />
  <meta name="twitter:title" content="goose grant program" />
  <meta name="twitter:description" content="$100K grants for open source devs building the future of agentic AI." />
  <meta name="twitter:image" content="https://goose-docs.ai/img/goose-grant-program.png" />
</head>

---

## 社区 Recipe Cookbook

> 原文：https://github.com/aaif-goose/goose/blob/main/documentation/src/pages/recipes/data/recipes/README.md

该目录包含 [Recipe Cookbook](https://goose-docs.ai/recipes) 中展示的 Recipe。它仍作为存档保留，但公开提交流程已结束，我们不再接受新的社区 Recipe 提交。

你仍然可以创建、使用并分享你自己的 Recipe。详见 [Recipe 文档](https://goose-docs.ai/docs/guides/recipes)。
