# goose 官方文档中文手册：第 20 章　教程（二）：工作流与可观测性

## Ralph Loop

> 原文：https://block.github.io/goose/docs/tutorials/ralph-loop

Ralph Loop 基于[Geoffrey Huntley 的 Ralph Wiggum 技巧](https://ghuntley.com/ralph/)，是一种迭代式开发模式：它会让 goose 持续处理任务，直到任务真正完成。

标准 Agent 循环会受到上下文累积的影响。每次失败的尝试都会留在对话历史中，因此迭代几轮后，模型必须先处理一大段噪声历史，才能专注于任务。Ralph Loop 通过在每次迭代开始时提供全新上下文解决了这个问题，这正是 Geoffrey 方法的核心洞见。此实现进一步加入跨模型审查：一个模型负责工作，另一个模型负责审查，循环持续到任务可以交付为止。

每轮迭代结束后，工作模型和审查模型会将摘要与反馈存入文件。这些文件会在不同迭代之间保留，但对话历史不会保留。这样，新会话启动后，下一个模型便可读取文件，准确接续上一次迭代的进度。

本教程将使用 Ralph Loop 构建一个简单的 Electron 浏览器，并观察迭代循环如何在交付前发现遗漏的功能。

#### 先决条件

- [安装 goose CLI](https://block.github.io/goose/docs/getting-started/installation)，因为 Ralph Loop 通过终端运行。
- [配置两个模型](https://block.github.io/goose/docs/getting-started/providers)，分别作为工作模型和审查模型。建议使用不同模型以获得更高质量的审查；两个角色使用同一个模型时，循环仍然可以运行。

<details>
<summary>下载 Ralph Loop Recipes</summary>

将以下内容复制并粘贴到终端，即可下载 Ralph Loop Recipes：

```bash
mkdir -p ~/.config/goose/recipes

curl -sL https://raw.githubusercontent.com/aaif-goose/goose/main/documentation/src/pages/recipes/data/recipes/ralph-loop.sh -o ~/.config/goose/recipes/ralph-loop.sh
curl -sL https://raw.githubusercontent.com/aaif-goose/goose/main/documentation/src/pages/recipes/data/recipes/ralph-work.yaml -o ~/.config/goose/recipes/ralph-work.yaml
curl -sL https://raw.githubusercontent.com/aaif-goose/goose/main/documentation/src/pages/recipes/data/recipes/ralph-review.yaml -o ~/.config/goose/recipes/ralph-review.yaml

chmod +x ~/.config/goose/recipes/ralph-loop.sh
```

</details>

:::warning 成本警告
Ralph Loop 会让 Agent 在循环中运行多次（默认最多 10 轮）。请监控用量，并根据需要调整 `RALPH_MAX_ITERATIONS`。
:::

#### 第 1 步：启动循环

要启动流程，请在终端运行脚本，并将提示词放在引号中。该命令会触发工作模型与审查模型循环的第一轮迭代：

```bash
~/.config/goose/recipes/ralph-loop.sh "Create a simple browser using Electron and React"
```

:::tip 复杂任务
你可以传入文件路径，而不是字符串。这种方式适用于 PRD、详细规格说明，或任何适合迭代开发的多步骤任务：

```bash
~/.config/goose/recipes/ralph-loop.sh ./prd.md
```
:::

#### 第 2 步：配置模型

脚本会提示你为本次会话设置环境变量：

```
Worker model [gpt-4o]: 
Worker provider [openai]: 
Reviewer model (should be different from worker): claude-sonnet-4-20250514
Reviewer provider: anthropic
Max iterations [10]: 

⚠️  Cost Warning: This will run up to 10 iterations, each using both models.
    Estimated token usage could be significant depending on your task.

Continue? [y/N]: y
```

| 变量 | 说明 |
|--------|-------------|
| Worker model | 执行实际编码工作的模型。若已设置 `GOOSE_MODEL`，则默认使用该值。 |
| Worker provider | 工作模型的提供方（例如 `openai`、`anthropic`）。若已设置 `GOOSE_PROVIDER`，则默认使用该值。 |
| Reviewer model | 审查工作的模型。为了获得最佳效果，应该与工作模型不同。 |
| Reviewer provider | 审查模型的提供方。 |
| Max iterations | 放弃前执行多少轮工作/审查循环。默认值为 10。 |

:::tip 直接设置环境变量
你可以直接设置环境变量，跳过交互式提示：

```bash
RALPH_WORKER_MODEL="gpt-4o" \
RALPH_WORKER_PROVIDER="openai" \
RALPH_REVIEWER_MODEL="claude-sonnet-4-20250514" \
RALPH_REVIEWER_PROVIDER="anthropic" \
~/.config/goose/recipes/ralph-loop.sh "Create a simple browser using Electron and React"
```
:::

#### 第 3 步：观察运行过程

终端会显示 goose 在工作阶段和审查阶段之间切换。每轮迭代都会从一个全新会话开始，以保持上下文清晰。一次成功运行的示例如下：

```
═══════════════════════════════════════════════════════════════
  Ralph Loop - Multi-Model Edition
═══════════════════════════════════════════════════════════════

  Task: Create a simple browser using Electron and React
  Worker: gpt-4o (openai)
  Reviewer: claude-sonnet-4-20250514 (anthropic)
  Max Iterations: 10

───────────────────────────────────────────────────────────────
  Iteration 1 / 10
───────────────────────────────────────────────────────────────

▶ WORK PHASE
... (goose creates initial implementation) ...

▶ REVIEW PHASE
... (goose reviews the work) ...

↻ REVISE - Feedback for next iteration:
Missing error handling for invalid URLs. Also needs back/forward navigation buttons.

───────────────────────────────────────────────────────────────
  Iteration 2 / 10
───────────────────────────────────────────────────────────────

▶ WORK PHASE
... (goose addresses feedback) ...

▶ REVIEW PHASE
... (goose reviews again) ...

═══════════════════════════════════════════════════════════════
  ✓ SHIPPED after 2 iteration(s)
═══════════════════════════════════════════════════════════════
```

### 工作原理

```
Iteration 1:
  WORK PHASE  → Model A does work, writes to files
  REVIEW PHASE → Model B reviews the work
    → SHIP? Exit successfully ✓
    → REVISE? Write feedback, continue to iteration 2

Iteration 2:
  WORK PHASE  → Model A reads feedback, fixes things (fresh context!)
  REVIEW PHASE → Model B reviews again
    → SHIP? Exit successfully ✓
    → REVISE? Continue...

... repeats until SHIP or max iterations
```

#### 状态文件

Ralph Loop 使用 `.goose/ralph/` 中的文件，在不同迭代之间持久化状态。这样，即使每轮迭代都从全新上下文开始，工作模型也知道要做什么，审查模型也知道已完成哪些工作。

| 文件 | 用途 |
|------|---------|
| `task.md` | 任务说明 |
| `iteration.txt` | 当前迭代轮次 |
| `work-summary.txt` | 工作模型本轮执行的内容 |
| `work-complete.txt` | 工作模型声明完成时创建 |
| `review-result.txt` | `SHIP` 或 `REVISE` |
| `review-feedback.txt` | 提供给下一轮迭代的反馈 |
| `.ralph-complete` | 成功完成时创建 |
| `RALPH-BLOCKED.md` | 工作模型陷入阻塞时创建 |

#### Recipe 文件

Ralph Loop 使用三个文件：一个负责编排工作/审查循环的 bash 脚本、一个指导工作模型如何推进任务的 work recipe，以及一个指导审查模型如何评估工作的 review recipe。下面列出每个文件的内容。你可以[下载](#先决条件)这些文件，也可以直接从这里复制。

<details>
<summary>Bash 封装脚本（`ralph-loop.sh`）</summary>

```bash
#!/bin/bash
#
# Ralph Loop - Multi-Model Edition
#
# Fresh context per iteration + cross-model review
# Based on Geoffrey Huntley's technique
#
# Usage: ./ralph-loop.sh "your task description here"
#    or: ./ralph-loop.sh /path/to/task.md
#
# Environment variables:
#   RALPH_WORKER_MODEL    - Model for work phase (prompts if not set)
#   RALPH_WORKER_PROVIDER - Provider for work phase (prompts if not set)
#   RALPH_REVIEWER_MODEL  - Model for review phase (prompts if not set)
#   RALPH_REVIEWER_PROVIDER - Provider for review phase (prompts if not set)
#   RALPH_MAX_ITERATIONS  - Max iterations (default: 10)
#   RALPH_RECIPE_DIR      - Recipe directory (default: ~/.config/goose/recipes)
#

set -e

INPUT="$1"
RECIPE_DIR="${RALPH_RECIPE_DIR:-$HOME/.config/goose/recipes}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ -z "$INPUT" ]; then
    echo -e "${RED}Error: No task provided${NC}"
    echo "Usage: $0 \"your task description\""
    echo "   or: $0 /path/to/task.md"
    exit 1
fi

# Function to prompt for settings
prompt_for_settings() {
    local default_model="${GOOSE_MODEL:-}"
    local default_provider="${GOOSE_PROVIDER:-}"
    
    # Worker model
    if [ -n "$default_model" ]; then
        echo -ne "${BLUE}Worker model${NC} [${default_model}]: "
        read -r user_input
        WORKER_MODEL="${user_input:-$default_model}"
    else
        echo -ne "${BLUE}Worker model${NC}: "
        read -r WORKER_MODEL
        if [ -z "$WORKER_MODEL" ]; then
            echo -e "${RED}Error: Worker model is required${NC}"
            exit 1
        fi
    fi
    
    # Worker provider
    if [ -n "$default_provider" ]; then
        echo -ne "${BLUE}Worker provider${NC} [${default_provider}]: "
        read -r user_input
        WORKER_PROVIDER="${user_input:-$default_provider}"
    else
        echo -ne "${BLUE}Worker provider${NC}: "
        read -r WORKER_PROVIDER
        if [ -z "$WORKER_PROVIDER" ]; then
            echo -e "${RED}Error: Worker provider is required${NC}"
            exit 1
        fi
    fi
    
    # Reviewer model
    echo -ne "${BLUE}Reviewer model${NC} (should be different from worker): "
    read -r REVIEWER_MODEL
    if [ -z "$REVIEWER_MODEL" ]; then
        echo -e "${RED}Error: Reviewer model is required${NC}"
        echo "The reviewer should be a different model to provide fresh perspective."
        exit 1
    fi
    
    # Reviewer provider
    echo -ne "${BLUE}Reviewer provider${NC}: "
    read -r REVIEWER_PROVIDER
    if [ -z "$REVIEWER_PROVIDER" ]; then
        echo -e "${RED}Error: Reviewer provider is required${NC}"
        exit 1
    fi
    
    # Same model warning
    if [ "$WORKER_MODEL" = "$REVIEWER_MODEL" ] && [ "$WORKER_PROVIDER" = "$REVIEWER_PROVIDER" ]; then
        echo -e "${YELLOW}Warning: Worker and reviewer are the same model.${NC}"
        echo "For best results, use different models for cross-model review."
        echo -ne "Continue anyway? [y/N]: "
        read -r confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            exit 1
        fi
    fi
    
    # Max iterations
    echo -ne "${BLUE}Max iterations${NC} [10]: "
    read -r user_input
    MAX_ITERATIONS="${user_input:-10}"
}

# Initialize from environment variables
WORKER_MODEL="${RALPH_WORKER_MODEL:-}"
WORKER_PROVIDER="${RALPH_WORKER_PROVIDER:-}"
REVIEWER_MODEL="${RALPH_REVIEWER_MODEL:-}"
REVIEWER_PROVIDER="${RALPH_REVIEWER_PROVIDER:-}"
MAX_ITERATIONS="${RALPH_MAX_ITERATIONS:-10}"

# If any required setting is missing, prompt for all settings
if [ -z "$WORKER_MODEL" ] || [ -z "$WORKER_PROVIDER" ] || [ -z "$REVIEWER_MODEL" ] || [ -z "$REVIEWER_PROVIDER" ]; then
    prompt_for_settings
fi

# Cost warning and confirmation loop
while true; do
    echo ""
    echo -e "${YELLOW}⚠️  Cost Warning:${NC} This will run up to ${MAX_ITERATIONS} iterations, each using both models."
    echo "    Estimated token usage could be significant depending on your task."
    echo ""
    echo -ne "Continue? [y/N]: "
    read -r confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        break
    else
        echo ""
        prompt_for_settings
    fi
done

STATE_DIR=".goose/ralph"
mkdir -p "$STATE_DIR"

if [ -f "$INPUT" ]; then
    cp "$INPUT" "$STATE_DIR/task.md"
    echo -e "${BLUE}Reading task from file: $INPUT${NC}"
else
    echo "$INPUT" > "$STATE_DIR/task.md"
fi

TASK=$(cat "$STATE_DIR/task.md")

rm -f "$STATE_DIR/review-result.txt"
rm -f "$STATE_DIR/review-feedback.txt"
rm -f "$STATE_DIR/work-complete.txt"
rm -f "$STATE_DIR/work-summary.txt"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Ralph Loop - Multi-Model Edition${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Task: ${YELLOW}$TASK${NC}"
echo -e "  Worker: ${WORKER_MODEL} (${WORKER_PROVIDER})"
echo -e "  Reviewer: ${REVIEWER_MODEL} (${REVIEWER_PROVIDER})"
echo -e "  Max Iterations: $MAX_ITERATIONS"
echo ""

for i in $(seq 1 "$MAX_ITERATIONS"); do
    echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}  Iteration $i / $MAX_ITERATIONS${NC}"
    echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
    
    echo "$i" > "$STATE_DIR/iteration.txt"
    
    echo ""
    echo -e "${YELLOW}▶ WORK PHASE${NC}"
    
    GOOSE_PROVIDER="$WORKER_PROVIDER" GOOSE_MODEL="$WORKER_MODEL" goose run --recipe "$RECIPE_DIR/ralph-work.yaml" || {
        echo -e "${RED}✗ WORK PHASE FAILED${NC}"
        exit 1
    }
    
    if [ -f "$STATE_DIR/RALPH-BLOCKED.md" ]; then
        echo ""
        echo -e "${RED}✗ BLOCKED${NC}"
        cat "$STATE_DIR/RALPH-BLOCKED.md"
        exit 1
    fi
    
    echo ""
    echo -e "${YELLOW}▶ REVIEW PHASE${NC}"
    
    GOOSE_PROVIDER="$REVIEWER_PROVIDER" GOOSE_MODEL="$REVIEWER_MODEL" goose run --recipe "$RECIPE_DIR/ralph-review.yaml" || {
        echo -e "${RED}✗ REVIEW PHASE FAILED${NC}"
        exit 1
    }
    
    if [ -f "$STATE_DIR/review-result.txt" ]; then
        RESULT=$(cat "$STATE_DIR/review-result.txt" | tr -d '[:space:]')
        
        if [ "$RESULT" = "SHIP" ]; then
            echo ""
            echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
            echo -e "${GREEN}  ✓ SHIPPED after $i iteration(s)${NC}"
            echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
            echo "COMPLETE: $(date)" > "$STATE_DIR/.ralph-complete"
            exit 0
        else
            echo ""
            echo -e "${YELLOW}↻ REVISE - Feedback for next iteration:${NC}"
            if [ -f "$STATE_DIR/review-feedback.txt" ]; then
                cat "$STATE_DIR/review-feedback.txt"
            fi
        fi
    else
        echo -e "${RED}✗ No review result found${NC}"
        exit 1
    fi
    
    rm -f "$STATE_DIR/work-complete.txt"
    rm -f "$STATE_DIR/review-result.txt"
    echo ""
done

echo -e "${RED}✗ Max iterations ($MAX_ITERATIONS) reached${NC}"
exit 1
```

</details>

<details>
<summary>Work 阶段 Recipe（`ralph-work.yaml`）</summary>

```yaml
version: 1.0.0
title: Ralph Work Phase
description: Single iteration of work - fresh context each time

instructions: |
  You are in a RALPH LOOP - one iteration of work.
  
  Your work persists through FILES ONLY. You will NOT remember previous iterations.
  
  STATE FILES (in .goose/ralph/):
  - task.md = The task you need to accomplish (READ THIS FIRST)
  - iteration.txt = Current iteration number
  - review-feedback.txt = Feedback from last review (if any)
  - work-complete.txt = Create when task is DONE (reviewer will verify)
  
  FIRST: Check your state
  1. cat .goose/ralph/task.md (YOUR TASK)
  2. cat .goose/ralph/iteration.txt 2>/dev/null || echo "1"
  3. cat .goose/ralph/review-feedback.txt 2>/dev/null
  4. ls -la to see existing work
  
  THEN: Make progress
  - If review-feedback.txt exists, ADDRESS THAT FEEDBACK FIRST
  - Read existing code/files before modifying
  - Make meaningful incremental progress
  - Run tests/verification if applicable
  
  FINALLY: Signal status
  - If task is complete: echo "done" > .goose/ralph/work-complete.txt
  - Always write a summary: echo "what I did" > .goose/ralph/work-summary.txt

prompt: |
  ## Ralph Work Phase
  
  Read your task from: .goose/ralph/task.md
  
  1. Read the task: `cat .goose/ralph/task.md`
  2. Check iteration: `cat .goose/ralph/iteration.txt 2>/dev/null || echo "1"`
  3. Check for review feedback: `cat .goose/ralph/review-feedback.txt 2>/dev/null`
  4. List existing files: `ls -la`
  5. Do the work (address feedback if any, otherwise make progress)
  6. Write summary: `echo "summary" > .goose/ralph/work-summary.txt`
  7. If complete: `echo "done" > .goose/ralph/work-complete.txt`

extensions:
  - type: builtin
    name: developer
    timeout: 600
```

</details>

<details>
<summary>Review 阶段 Recipe（`ralph-review.yaml`）</summary>

```yaml
version: 1.0.0
title: Ralph Review Phase
description: Cross-model review of work - returns SHIP or REVISE

instructions: |
  You are a CODE REVIEWER in a Ralph Loop.
  
  Your job: Review the work done and decide SHIP or REVISE.
  
  You are a DIFFERENT MODEL than the worker. Your fresh perspective catches mistakes.
  
  STATE FILES (in .goose/ralph/):
  - task.md = The original task (READ THIS FIRST)
  - work-summary.txt = What the worker claims to have done
  - work-complete.txt = Exists if worker claims task is complete
  
  REVIEW CRITERIA:
  1. Does the code/work actually accomplish the task?
  2. Does it run without errors?
  3. Is it reasonably complete, not half-done?
  4. Are there obvious bugs or issues?
  
  BE STRICT but FAIR:
  - Don't nitpick style if functionality is correct
  - DO reject incomplete work
  - DO reject code that doesn't run
  - DO reject if tests fail
  
  OUTPUT:
  If approved: echo "SHIP" > .goose/ralph/review-result.txt
  If needs work: 
    echo "REVISE" > .goose/ralph/review-result.txt
    echo "specific feedback" > .goose/ralph/review-feedback.txt

prompt: |
  ## Ralph Review Phase
  
  1. Read the task: `cat .goose/ralph/task.md`
  2. Read work summary: `cat .goose/ralph/work-summary.txt`
  3. Check if complete: `cat .goose/ralph/work-complete.txt 2>/dev/null`
  4. Examine the actual files created/modified
  5. Run verification (tests, build, etc.)
  6. Decide: SHIP or REVISE
  
  If SHIP: `echo "SHIP" > .goose/ralph/review-result.txt`
  If REVISE: 
    `echo "REVISE" > .goose/ralph/review-result.txt`
    `echo "specific feedback" > .goose/ralph/review-feedback.txt`

extensions:
  - type: builtin
    name: developer
    timeout: 300
```

</details>

### 使用技巧

#### 适合使用 Ralph Loop 的场景

Ralph Loop 最适用于：

- **适合迭代的复杂多步骤任务**
- **具有明确完成标准的任务**（测试通过、构建成功）
- **交付前需要质量门槛的场景**

以下情况使用它会显得过度：

- 简单的一次性任务
- 交互式/探索性工作
- 没有可验证完成标准的任务

#### 重置

如果你要开始一个全新的任务，或者之前的运行陷入停滞、你想从头开始，可以清除状态目录：

```bash
rm -rf .goose/ralph
```

---

## Research → Plan → Implement 模式

> 原文：https://block.github.io/goose/docs/tutorials/rpi

大多数人使用 AI Agent 时会直接跳到执行阶段：“重构这段代码”“移除此功能”“添加这个新功能”。有时这种做法效果不错，尤其是改动或代码库较小时；但面对复杂改动时，它往往会失效。

由 HumanLayer 提出的**[RPI（Research、Plan、Implement，研究、规划、实施）](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md)**，为使用 AI Agent 提供了另一种工作方式。这种方法以速度换取清晰度、可预测性和正确性。

本教程通过一个真实演示，逐步介绍 RPI 的工作方式。完成后，你就可以在自己的代码库中运行同样的工作流。

### 先决条件

<details>
<summary>1. 导入 RPI Recipes</summary>

复制下面的代码片段并粘贴到终端。它会下载主要的 RPI recipes 及其子 recipes，并将它们保存到全局 recipe 目录。

```sh
mkdir -p ~/.config/goose/recipes/subrecipes

curl -sL https://raw.githubusercontent.com/aaif-goose/goose/main/documentation/src/pages/recipes/data/recipes/rpi-research.yaml -o ~/.config/goose/recipes/rpi-research.yaml
curl -sL https://raw.githubusercontent.com/aaif-goose/goose/main/documentation/src/pages/recipes/data/recipes/rpi-plan.yaml -o ~/.config/goose/recipes/rpi-plan.yaml
curl -sL https://raw.githubusercontent.com/aaif-goose/goose/main/documentation/src/pages/recipes/data/recipes/rpi-implement.yaml -o ~/.config/goose/recipes/rpi-implement.yaml
curl -sL https://raw.githubusercontent.com/aaif-goose/goose/main/documentation/src/pages/recipes/data/recipes/rpi-iterate.yaml -o ~/.config/goose/recipes/rpi-iterate.yaml

curl -sL https://raw.githubusercontent.com/aaif-goose/goose/main/documentation/src/pages/recipes/data/recipes/subrecipes/rpi-codebase-locator.yaml -o ~/.config/goose/recipes/subrecipes/rpi-codebase-locator.yaml
curl -sL https://raw.githubusercontent.com/aaif-goose/goose/main/documentation/src/pages/recipes/data/recipes/subrecipes/rpi-codebase-analyzer.yaml -o ~/.config/goose/recipes/subrecipes/rpi-codebase-analyzer.yaml
curl -sL https://raw.githubusercontent.com/aaif-goose/goose/main/documentation/src/pages/recipes/data/recipes/subrecipes/rpi-pattern-finder.yaml -o ~/.config/goose/recipes/subrecipes/rpi-pattern-finder.yaml
```
</details>

<details>
<summary>2. 添加自定义 Slash Commands</summary>

导入 recipes 后，要在会话中快速调用它们，请为以下每个 recipe[添加自定义 Slash Command](https://block.github.io/goose/docs/guides/context-engineering/slash-commands)：

| Recipe | Slash Command |
|--------|---------------|
| RPI Research Codebase | `research_codebase`|
| RPI Create Plan | `create_plan` |
| RPI Implement Plan | `implement_plan` |
| RPI Iterate | `iterate_plan` |
</details>

### RPI 工作流

在 goose 中，我们使用基于 recipes 的结构化 RPI 工作流，系统地处理复杂的代码库改动。该工作流由 Slash Commands 组成，引导 goose 按照严谨的阶段开展工作：

1. `research_codebase` – 记录当前已有的内容，不作评价。
2. `create_plan` - 设计改动，明确阶段和成功标准。
3. `implement_plan` - 按步骤执行计划并进行验证。
4. `iterate_plan` –（可选）必要时调整计划。

```md
┌─────────────────────────────────────────────────────────────────────────────-┐
│                           RPI WORKFLOW                                       │
├─────────────────────────────────────────────────────────────────────────────-┤
│                                                                              │
│  /research_codebase "topic"                                                  │
│       │                                                                      │
│       ├──► Spawns parallel sub-agents:                                       │
│       │    • find_files (rpi-codebase-locator)                               │
│       │    • analyze_code (rpi-codebase-analyzer)                            │
│       │    • find_patterns (rpi-pattern-finder)                              │
│       │                                                                      │
│       └──► Output: thoughts/research/YYYY-MM-DD-HHmm-topic.md                │
│                                                                              │
│  /create_plan "feature/task"                                                 │
│       │                                                                      │
│       ├──► Reads research docs                                               │
│       ├──► Asks clarifying questions                                         │
│       ├──► Proposes design options                                           │
│       │                                                                      │
│       └──► Output: thoughts/plans/YYYY-MM-DD-HHmm-description.md             │
│                                                                              │
│  /implement_plan "plan path"                                                 │
│       │                                                                      │
│       ├──► Executes phase by phase                                           │
│       ├──► Runs verification after each phase                                │
│       ├──► Updates checkboxes in plan                                        │
│       │                                                                      │
│       └──► Working code                                                      │
│                                                                              │
│  /iterate_plan "plan path" + feedback                                        │
│       │                                                                      │
│       ├──► Researches only what changed                                      │
│       ├──► Updates the plan surgically                                       │
│       │                                                                      │
│       └──► Updated plan                                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────-┘
```

所有 RPI 输出都保存在可预测的位置：

```md
thoughts/
├── research/
│   └── YYYY-MM-DD-HHmm-topic.md
└── plans/
    └── YYYY-MM-DD-HHmm-description.md
```

### 任务

在本教程中，我想从一个大型代码库中移除现有功能。

这不是一个小改动。该功能涉及：

- 核心 Rust 代码
- TypeScript
- 配置
- 测试
- 文档

这类任务经常让 Agent 举步维艰，并不是因为它们能力不足，而是因为工作涉及的上下文太多，无法安全地“直接动手”。

因此，我们不会直接开始实施，而是使用 RPI。

### 会话 1：研究

在实施前先规划，已经成为广受认可的做法。但如果没有研究就开始规划，臆测可能会给后续带来麻烦。因此，RPI 从研究开始。

我先输入 `/research_codebase` 命令，再用自然语言写出研究主题：

```
/research_codebase "look through the cloned goose repo and research how the LLM Tool Discovery is implemented"
```

该命令会调用**[RPI Research Codebase](https://raw.githubusercontent.com/aaif-goose/goose/refs/heads/main/documentation/src/pages/recipes/data/recipes/rpi-research.yaml)** recipe，其职责非常严格：

- 记录现有内容
- 不提出改动建议
- 不作批评
- 不做规划

使用这个 recipe 时，goose 会自动启动三个并行子代理：

- `find_files`：使用代码库定位器，找出相关文件的位置。
- `analyze_code`：完整读取这些文件，并记录它们的工作方式。
- `find_patterns`：在代码库其他位置查找类似功能或惯例。

这些子代理独立运行并返回结果。你不必亲自编排它们。

:::info 修正方向
goose 开始研究后，我发现它研究的是泛指的“工具发现”。但我真正想移除的是一个名为 Tool Selection Strategy 的具体功能。于是我停止了 goose，并用更准确的主题重新运行研究。

这并不算失败。实际上，这正是研究阶段存在的意义。如果我直接告诉 goose“移除 LLM Tool Discovery 功能”，它可能会连其他工具发现方法也一并移除。幸运的是，及早发现这类错误，纠正起来既简单，成本也低。
:::

`/research_codebase` 会话生成了一份详细的研究文档：

<details>
<summary>./thoughts/research/2025-12-22-llm-tool-selection-strategy.md</summary>

<CodeBlock language="markdown">
{researchDoc}
</CodeBlock>

</details>

这是一个大型结构化文件，内容包括：
- Git 元数据
- 文件与行号引用
- 流程说明
- 关键组件
- 待解问题

你可以把它看作这项功能当前状态的技术地图。此时还没有任何内容被修改，这是有意为之。唯一目标是建立共同理解。

作为 human-in-the-loop 的参与者，请务必审阅研究结果！后续计划会以此为依据，因此你需要确认内容准确。

### 会话 2：规划

研究完成后，就进入规划阶段。

:::tip 会话
每个阶段都应在新会话中执行，以便让 LLM 全神贯注于当前任务。每个会话只设定一个目标！
:::

```
/create_plan a removal of the Tool Selection Strategy feature
```

**[RPI Create Plan](https://raw.githubusercontent.com/aaif-goose/goose/refs/heads/main/documentation/src/pages/recipes/data/recipes/rpi-plan.yaml)** recipe 首先会读取 goose 生成的研究文档。

随后，它做了三件关键的事：

1. **提出澄清问题**

    例如：
    - 是彻底移除还是弃用？
    - 配置清理应该如何处理？
    - 是否应该重新生成 OpenAPI 产物？
    - 相关测试位于哪里？

2. **提供设计选项**

    对于存在多种合理方案的地方，goose 会列出各方案并请我选择。

3. **生成分阶段实施计划**

计划输出如下：

<details>
<summary>thoughts/plans/2025-12-23-remove-tool-selection-strategy.md</summary>

<CodeBlock language="markdown">
{planDoc}
</CodeBlock>

</details>

该计划包含：
- 10 个明确阶段
- 精确的文件路径
- 指明要移除内容的代码片段
- 自动化成功标准
- 手动验证步骤
- 用于跟踪进度的复选框

从这一步开始，计划成为事实来源。关键变化是，我们已经从理解进入决策，但仍未触碰代码。

计划足够明确，其他人也可以照此执行。这并非偶然。请记住，实施将在一个全新的会话中进行，因此计划必须包含足够的上下文，才能真正执行。

同样，你作为人类需要在此介入，审阅计划并确认它足够可靠。如果发现问题，不必从头开始；你可以通过 `/iterate_plan` 运行 **[RPI Iterate Plan](https://raw.githubusercontent.com/aaif-goose/goose/refs/heads/main/documentation/src/pages/recipes/data/recipes/rpi-iterate.yaml)**，并说明哪里不妥。goose 随后会读取现有计划，只研究需要重新思考的部分，有针对性地提出修改，并相应编辑计划。

### 会话 3：实施

只有在研究和规划都完成后，才应进入实施阶段。传入计划文档即可。

```
/implement_plan thoughts/plans/2025-12-23-remove-tool-selection-strategy.md
```

**[RPI Implement Plan](https://raw.githubusercontent.com/aaif-goose/goose/refs/heads/main/documentation/src/pages/recipes/data/recipes/rpi-implement.yaml)** recipe 刻意设计得很机械。事实上，goose 执行时我都睡着了。实施本来就应该像机械流程；如果它显得需要创造性，说明前序阶段还有缺漏。不过，既然你已经有一个非常扎实的计划，我建议你趁 goose 工作时去做点别的（除非计划中包含手动步骤）。

它会完整读取计划，按顺序执行各阶段，在每个阶段后运行验证，并随着进度直接更新计划文件中的复选框。

最后一点非常有帮助，因为我的上下文窗口在执行到一半时就满了，而 goose 借助计划里的状态更新完成了压缩，并从中断处继续执行。

### 最终结果

这项工作分为 10 个阶段，涉及 32 个文件；Research 阶段用了 9 分钟，Plan 阶段用了 4 分钟，Implement 阶段用了 39 分钟。总计略少于一小时，准确地说是 52 分钟。这包括 goose 的工作与测试，以及我回答问题所花的时间。

这显然不是快速流程。不过！我提交[这个 PR](https://github.com/aaif-goose/goose/pull/6250)时，构建顺利通过，独立的 Code Review Agent 也没有提出任何意见。工作质量就是这么好。

如果不借助 AI，我可能要花好几个小时，因为这项功能复杂且深度集成。如果让 AI 直接开始实施，我毫不怀疑它会偏离目标并弄坏某些东西。

因此，虽然 RPI 比让 AI 立即开始工作更慢，但成果质量一流。这种取舍非常值得。

### 何时使用 RPI

对于基础任务，RPI 可能有些大材小用，尤其是它并非一个快速流程。不过，如果你要处理涉及多个文件的复杂任务，它就是很好的选择。

你可以将 RPI 用于：
- 重构
- 迁移
- 添加功能
- 大型升级
- 事件清理
- 文档全面改版

亲自试试看！

---

## 使用子代理

> 原文：https://block.github.io/goose/docs/tutorials/subagents

本教程将带你启动一组 AI[子代理](https://block.github.io/goose/docs/guides/context-engineering/subagents/)，并引导它们构建一个功能完备的应用。

你将构建 **AI BriefMe**，一款可根据任意主题生成结构化高管简报的应用。

你将使用 goose 编排一支完整的软件团队，团队由多个子代理组成：

- 🧠 **规划师**——定义产品与 MVP 范围  
- 📋 **项目经理**——拆分任务并协调执行  
- 🏗️ **架构师**——搭建项目结构并选择技术栈  
- 💻 **前端与后端开发者**——构建界面和 API 逻辑  
- 🧪 **QA**——编写测试并指出缺陷或上线阻碍  
- 📝 **技术写作者**——编写设置、使用方法和 API 说明

完成本教程后，你将得到一个可运行的原型，并清楚了解如何在实际工作流中使用 AI Agent。

### 设置

1. [安装 goose](https://block.github.io/goose/docs/getting-started/installation)
2. 在 goose 中选择工作目录。建议在新建目录中工作。
3. 将以下内容添加到 [.goosehints](https://block.github.io/goose/docs/guides/context-engineering/using-goosehints/#local-hints-file)：

```plaintext
Create apps in html, javascript, and css when possible.
NEVER run blocking server commands (node server.js, npm start, etc.) - provide commands for user to run separately.
```

4. （可选）安装 [goose docs extension](https://block.github.io/goose/docs/mcp/goose-docs-mcp)，以便在需要时询问 goose 关于它自身的问题。

### 任务

你将通过启动一组子代理，构建一个 AI 驱动的简报应用。每个 Agent 都有明确角色。你的任务是想好如何提示 goose，将工作委派出去。

> 🛟 如果遇到困难，可以查看提示词示例。

---

#### 1. 🧠 规划师

让规划师定义产品愿景和范围。规划师应决定：
- 应用是什么
- 面向谁
- 要解决什么问题
- MVP 的核心功能

输出应是清晰的产品定义，而不是代码。

<details>
  <summary>规划师 Agent 提示词</summary>
  
```md
  You're the Planner agent for a hands-on AI app building session using goose and subagents. We are building the MVP *right now*.

  The app is called **AI BriefMe**. It generates a daily briefing on any given topic. A user inputs a topic like “Apple earnings” or “AI in DevOps,” and the app returns:
  - A title
  - Today's date
  - 2–3 bullet-point takeaways
  - (Optional) a code snippet or chart, if the topic is technical

  You're working with a team of subagents — PM, Architect, Frontend Dev, Backend Dev, QA, and Tech Writer — who will immediately begin executing your plan.

  Write a short, focused **Markdown file (`plan.md`)** that outlines:
  - The goals of the MVP
  - Only the features that can be built in a 40 minute session
  - Any helpful design considerations

  ✅ DO: Keep it lean and actionable  
  ❌ DON'T: Include long-term features like email delivery, user accounts, dashboards, analytics, personalization, mobile optimization, or 8-week timelines
```
</details>

---

#### 2. 📋 项目经理

请项目经理将产品拆分为开发任务。输出应当：
- 定义所需角色（例如前端、后端）
- 列出具体任务并分配负责人
- 指出哪些任务可以并行执行，哪些必须按顺序执行

<details>
  <summary>PM Agent 提示词</summary>
  
```md
  You're the PM agent. A Planner has just created `plan.md` for a 1-hour build session of an app called "AI BriefMe."

  Your job is to:
  - Break the work into tasks for each subagent: Architect, Backend Dev, Frontend Dev, QA, Tech Writer
  - Group tasks by agent
  - Decide what work can be done in parallel vs what must be sequential
  - Output the task breakdown in Markdown and save it as `project_board.md`

  Be realistic and concise — this is a sprint, not a roadmap.
```
</details>

---

#### 3. 🏗️ 架构师

让架构师规划技术设置。他们应当：
- 选择技术栈（前端与后端框架及所需库）
- 描述文件夹结构和文件组织方式
- 标出需要安装的内容（可选：提供安装命令）

<details>
  <summary>架构师 Agent 提示词</summary>
  
```md
  You are the Architect. Based on the project plan and `project_board.md`, set up the project scaffolding.

  Do the following:
  - Create the folder structure and all placeholder files (e.g. `index.html`, `server.js`, `style.css`, etc.)
  - Generate a `package.json` file that includes `express`, `cors`, and `child_process` as dependencies
  - Add a `.gitignore` that excludes `node_modules` and any temporary files
  - Define the API contract for the `/api/briefing` endpoint in Markdown

  ✅ Do NOT include or reference any API keys  
  ✅ Do NOT install packages — just scaffold the structure  
  ✅ DO list the output files and folders at the end

```
</details>

---

#### 4. 💻 前端与后端开发者（并行）

同时启动两个开发者子代理，构建应用核心。一位负责 Express 服务器和后端逻辑，另一位负责 UI 并接入表单。goose 应同时执行两个 Agent，而不是先后执行。

- 使用架构师提供的文件结构和 API 契约
- 后端使用 Headless goose 编写 API 逻辑
- 前端构建响应式 UI 并调用 API
- 确保 Agent 不会同时写入同一个文件

<details>
  <summary>开发者 Agent 提示词</summary>
  
```md
  Use **parallel execution** to run two subagents:

  - A 🛠️ Backend Developer
  - A 💻 Frontend Developer

  Both should work simultaneously — not sequentially — to build the AI BriefMe MVP.

  🛠️ **Backend Developer** should:
  - Implement `server.js` with Express
  - Add POST `/api/briefing` endpoint accepting `{ "topic": "string" }`
  - Use **Headless goose** to generate the summary:
    - `goose run -t "YOUR_PROMPT_HERE" --quiet --no-session --max-turns 1`
  - Use `child_process.spawn()` instead of `exec()`
  - Clean response: remove ANSI codes, markdown blocks, and extract JSON
  - Handle timeouts (max 60s) and errors
  - Serve frontend files from `express.static`
  - Add CORS
  - Do not require any API keys

  💻 **Frontend Developer** should:
  - Create `index.html`, `style.css`, and `script.js`
  - Build a form for entering a topic
  - Call the `/api/briefing` endpoint and display the result
  - Handle loading states and errors
  - Include a copy-to-clipboard button
  - Make it mobile-friendly
  - Do not interfere with backend files

  ⚠️ Important: These agents must not write to the same files. Keep their work isolated.

```
</details>

---

#### 5. 🧪📝 QA 与技术写作者（并行）

开发完成后，再启动最后两个子代理：**QA 工程师**和**技术写作者**。它们将协同评估应用质量并编写使用文档。你的任务是提示 goose，让两个 Agent 协作，同时避免工作重叠或重复。

##### QA Agent 任务：
- 使用 Jest 等框架为 `/api/briefing` endpoint 编写单元测试套件
- 创建 `QA_NOTES.md` 文件：
  - 标出缺陷或边缘情况
  - 找出阻碍产品上线的问题（例如安全性、错误处理）
  - 给出提升可靠性的后续建议

##### 技术写作者任务：
- 与 QA 协作，了解应用当前状态
- 创建 `README.md` 文件，其中包括：
  - 应用的用途（通俗易懂的说明）
  - 安装与运行方法
  - API 使用示例

⚠️ 重要事项：
- **QA 不应手动启动服务器**——只需编写测试文件并模拟交互

<details>
  <summary>QA Agent 与 📝 技术写作者 Agent 提示词（并行）</summary>
  
```md
  The development phase is complete. Now it's time for quality assurance and documentation.

  Use **parallel execution** to run two subagents simultaneously:

  - 🧪 A **QA Agent** who will:
    - Write a unit test for the `/api/briefing` endpoint in `tests/briefing.test.js` using Jest
    - **Mock the child_process module** using `jest.mock('child_process')` at the top of the test file
    - Create a simple mock that returns fake data instead of calling the real goose CLI
    - Assert that the response includes: `title`, `date`, and 2–3 `takeaways`
    - Include tests for:
      - Valid topic input
      - Missing or invalid input
      - goose CLI timeout or error
    - **Do not start or run the server manually.** Only write test files.
    - **Do not execute `npm test` or run any tests.** Only create the test file.
    - Save a full QA analysis report in `QA_NOTES.md` with:
      - Critical issues
      - Security or performance gaps
      - Recommendations for production readiness
    - **When all files are created, immediately state: "QA Agent Sign-off: ✅ COMPLETE" and finish.**

  - 📝 A **Tech Writer Agent** who will:
    - Create a `README.md` that includes:
      - Project overview
      - How to run the app locally
      - API endpoint documentation
      - Example request/response
      - Troubleshooting section
    - **When documentation is complete, immediately state: "Tech Writer Sign-off: ✅ COMPLETE" and finish.**

  Both agents should work in parallel, not sequentially.
```
</details>

---

### 测试完成的应用

所有 Agent 完成后，你应该会得到一个可运行的原型。以下是查看运行效果的方法：

#### 第 1 步：安装依赖
```bash
cd your-project-folder
npm install
```

#### 第 2 步：启动服务器
**重要：**请在**单独的终端窗口**中运行（不要在 goose 中运行）：
```bash
npm start
```

你应该会看到：
```
AI BriefMe server running on port 3000
Health check: http://localhost:3000/health
Briefing endpoint: http://localhost:3000/api/briefing
```

#### 第 3 步：打开应用
打开浏览器并访问：
```
http://localhost:3000/
```

**注意：**使用根 URL（`/`），不要使用 `/ai-briefme/`

#### 第 4 步：测试应用
1. 输入一个主题，例如“JavaScript frameworks”或“climate change”
2. 点击“Get Briefing”
3. 观察 AI 生成简报！

你应该能看到：
- 简洁、响应式的界面
- 包含标题、日期和要点的 AI 生成简报
- 面向技术主题的代码示例
- 复制到剪贴板功能

:::tip 保持服务器运行
- **不要关闭**运行服务器的终端
- **不要在 goose 中运行服务器**——它会卡住
- 如果要停止服务器：在服务器终端中按 `Ctrl+C`
- 如果需要 goose 修复或添加内容，直接告诉它！完成后重新启动服务器
:::

**恭喜！你已使用 goose 子代理构建了一个全栈 AI 应用！** 🎉

:::warning
不要期待应用可以直接用于生产。本次练习展示了 goose 辅助 Vibe Coding 如何加速原型制作，但判断与打磨仍由人负责。
:::

---

### 故障排除

#### Cannot POST /api/briefing（404 错误）
**原因：**路由未注册，或服务器没有重启。
**解决方案：**
1. **停止服务器**（在终端中按 Ctrl+C）
2. **重新启动服务器：**`node server.js`
3. **使用 curl 测试：**
```bash
   curl -X POST http://localhost:3000/api/briefing -H "Content-Type: application/json" -d '{"topic":"test"}'
```
4. **应该返回 JSON，而不是 HTML**

---

#### Unexpected token

**原因：**前端收到的是 HTML，而不是 JSON（通常是 404 页面）。
**解决方案：**
1. **先直接测试 API：**
```bash
   curl -X POST http://localhost:3000/api/briefing -H "Content-Type: application/json" -d '{"topic":"test"}'
```
2. **如果返回 HTML：**API 路由无法正常工作（参见问题 1）
3. **如果返回 JSON：**检查浏览器 Network 标签页，确认前端实际调用的 URL
4. **常见修复方法：**确保访问应用的地址是 `http://localhost:3000/`，而不是 `/ai-briefme/`

---

#### 进程超时
**原因：**goose 耗时过长或挂起。
**解决方案：**
1. **检查 goose 命令参数：**
```javascript
   ['run', '-t', prompt, '--quiet', '--no-session', '--max-turns', '1']
```
2. **手动测试 goose：**
```bash
   goose run -t "Return JSON: {\"test\": \"value\"}" --quiet --no-session --max-turns 1
```
3. **如果手动测试正常：**检查你的 spawn() 实现
4. **如果手动测试挂起：**先尝试更简单的提示词

---

#### JSON 解析错误
**原因：**goose 返回带格式的输出，其中含有颜色代码。
**解决方案：**
1. 在 `JSON.parse()` 之前添加以下清理代码：
```javascript
   // Remove ANSI color codes
   jsonString = jsonString.replace(/\x1b\[[0-9;]*m/g, '');
   // Remove markdown formatting
   jsonString = jsonString.replace(/```json\s*/, '').replace(/```\s*$/, '');
   jsonString = jsonString.replace(/```\s*/, '');
```
2. **添加调试日志，查看实际收到的内容：**
```javascript
   console.log('Raw goose response:', aiResponse);
   console.log('Cleaned JSON string:', jsonString);
```

---

#### 端口已被占用（EADDRINUSE）
**解决方案：**
1. **查找占用 3000 端口的进程：**
```bash
   lsof -ti:3000
```
2. **结束该进程：**
```bash
   lsof -ti:3000 | xargs kill -9
```
3. **或者使用其他端口：**
```javascript
   const PORT = process.env.PORT || 3001;
```
---

#### 应用显示空白页
**解决方案：**
1. **确认访问的是正确 URL：**`http://localhost:3000/`（而不是 `/ai-briefme/`）
2. **检查浏览器控制台**是否有 JavaScript 错误
3. **确认静态文件已提供服务：**
```javascript
   app.use(express.static(__dirname));
```
4. **分别测试文件：**
   - `http://localhost:3000/index.html`
   - `http://localhost:3000/style.css`
   - `http://localhost:3000/script.js`

---

## 并行运行子 recipes

> 原文：https://block.github.io/goose/docs/tutorials/subrecipes-in-parallel

goose recipes 可以使用相互隔离的工作进程，并发执行多个 [subrecipe](https://block.github.io/goose/docs/guides/recipes/subrecipes) 实例。此功能支持高效的批量操作、不同任务的并行处理，并能更快完成复杂工作流。

:::warning 实验性功能
并行运行 subrecipes 是一项仍在积极开发中的实验性功能。其行为与配置在未来版本中可能会有所变化。
:::

以下是一些常见用例：

- **Monorepo 构建失败**：当 Monorepo 构建中有 3 个服务失败时，可以为每个构建 URL 使用“诊断失败”subrecipe，并行诊断所有失败。
- **文档摘要**：处理包含文档链接的 CSV 文件，为每个链接同时运行“文档摘要”subrecipe。  
- **跨代码库分析**：同时对多个代码库运行安全性、质量和性能分析。

### 工作原理

并行执行 subrecipe 使用隔离的工作进程系统，自动管理并发任务执行。goose 会为每个 subrecipe 实例创建独立任务，并将任务分发给最多 10 个并发工作进程。

| 场景 | 默认行为 | 覆盖选项 |
|----------|------------------|------------------|
| **不同的 subrecipes** | 顺序执行 | 在提示词中添加“in parallel” |
| **同一个 subrecipe**，参数不同 | 并行执行 | • 设置 `sequential_when_repeated: true`<br />• 在提示词中添加“sequentially” |

#### 不同的 Subrecipes

运行不同的 subrecipes 时，goose 根据以下内容决定执行模式：
1. 提示词中的**用户明确要求**（“in parallel”“sequentially”）
2. **默认按顺序执行**：不同的 subrecipes 会依次运行，除非明确要求并行运行。

调用不同的 subrecipes 时，只需在提示词中提到“in parallel”：

```yaml
prompt: |
  run the following subrecipes in parallel:
    - use weather subrecipe to get the weather for Sydney
    - use things-to-do subrecipe to find activities in Sydney
```

#### 相同的 Subrecipe

使用不同参数运行同一个 subrecipe 时，goose 根据以下内容决定执行模式：
1. **[Recipe 级别的配置](#在执行模式之间进行选择)**（`sequential_when_repeated` 标志）——设置为 true 时强制顺序执行
2. 提示词中的**用户请求**（使用“sequentially”覆盖默认并行行为）
3. **默认并行执行**：同一个 subrecipe 的多个实例会并发运行。

如果提示词暗示要多次执行同一个 subrecipe，goose 会自动创建并行实例：

```yaml
prompt: |
  get the weather for three biggest cities in Australia
```

在此示例中，goose 会识别出“三个最大城市”意味着需要对不同城市多次运行 weather subrecipe，因此会并行执行。

如果你希望它们按顺序运行，只需告诉 goose：

```yaml
prompt: |
  get the weather for three biggest cities in Australia one at a time
```

#### 实时进度监控

通过 CLI 并行运行多个任务时，执行期间会自动显示实时仪表板，你可以借此跟踪进度。仪表板提供：
- **实时进度跟踪**：实时监控任务完成情况，并显示已完成、运行中、失败和待处理任务的数量统计。
- **任务详情**：任务从 Pending → Running → Completed/Failed 状态变化时，查看唯一任务 ID、参数集、执行时间、输出预览和错误信息。

### 示例

#### 并行运行不同的 Subrecipes

本例将并行运行 `weather` 和 `things-to-do` subrecipes：

```yaml
# plan_trip.yaml
version: 1.0.0
title: Plan Your Trip
description: Get weather forecast and find things to do for your destination
instructions: You are a travel planning assistant that helps users prepare for their trips.
prompt: |
  run the following subrecipes in parallel to plan my trip:
    - use weather subrecipe to get the weather forecast for Sydney
    - use things-to-do subrecipe to find activities and attractions in Sydney
sub_recipes:
- name: weather
  path: "./subrecipes/weather.yaml"
  values:
    city: Sydney
- name: things-to-do
  path: "./subrecipes/things-to-do.yaml"
  values:
    city: Sydney
    duration: "3 days"
extensions:
- type: builtin
  name: developer
  timeout: 300
  bundled: true
```

#### 并行运行相同的 Subrecipe（参数不同）

本例针对不同城市并行运行三个 `weather` subrecipe 实例：

```yaml
# multi_city_weather.yaml
version: 1.0.0
title: Multi-City Weather Comparison
description: Compare weather across multiple cities for trip planning
instructions: You are a travel weather specialist helping users compare conditions across cities.
prompt: |
  get the weather forecast for the three biggest cities in Australia 
  to help me decide where to visit
sub_recipes:
- name: weather
  path: "./subrecipes/weather.yaml"
extensions:
- type: builtin
  name: developer
  timeout: 300
  bundled: true
```

**Subrecipes：**

<details>
  <summary>weather</summary>
```yaml
    # subrecipes/weather.yaml
    version: 1.0.0
    title: Find weather
    description: Get weather data for a city
    instructions: You are a weather expert. You will be given a city and you will need to return the weather data for that city.
    prompt: |
      Get the weather forecast for {{ city }} for today and the next few days.
    parameters:
      - key: city
        input_type: string
        requirement: required
        description: city name
    extensions:
      - type: stdio
        name: weather
        cmd: uvx
        args:
          - mcp_weather@latest
        timeout: 300
```
</details>

<details>
  <summary>things-to-do</summary>
```yaml
    # subrecipes/things-to-do.yaml
    version: 1.0.0
    title: Things to do in a city
    description: Find activities and attractions for travelers
    instructions: You are a local travel expert who knows the best activities, attractions, and experiences in cities around the world.
    prompt: |
      Suggest the best things to do in {{ city }} for a {{ duration }} trip. 
      Include a mix of popular attractions, local experiences, and hidden gems.
      {% if weather_context %}
      Consider the weather conditions: {{ weather_context }}
      {% endif %}
    parameters:
      - key: city
        input_type: string
        requirement: required
        description: city name
      - key: duration
        input_type: string
        requirement: required
        description: trip duration (e.g., "2 days", "1 week")
      - key: weather_context
        input_type: string
        requirement: optional
        default: ""
        description: weather conditions to consider for activity recommendations
```
</details>

### 在执行模式之间进行选择

虽然并行执行可以提升速度，但有时顺序执行才是必要或更合适的选择。可按以下方式判断：

**适合顺序执行的情况：**
- 任务会修改共享资源
- 执行顺序很重要
- 存在内存或 CPU 资源限制
- 调试并行模式下的复杂故障

**适合并行执行的情况：**
- 任务相互独立
- 希望更快完成
- 系统资源足以支持最多 10 个并行工作进程同时执行
- 处理大型数据集或多个文件

**Recipe 级别配置：**

对于绝不应并行运行的 subrecipes，设置 `sequential_when_repeated: true`，即可覆盖用户请求：

```yaml
sub_recipes:
  - name: database-migration
    path: "./subrecipes/migrate.yaml"
    sequential_when_repeated: true  # Always sequential
```

### 了解更多

请查看 [Recipes](https://block.github.io/goose/docs/guides/recipes) 指南，了解更多帮助你掌握 goose recipes 的文档、工具和资源。

---

## Recipes

> 原文：https://block.github.io/goose/docs/tutorials/recipes-tutorial

Recipe 是包含完成某一特定任务所需全部细节的文件。因为内容仅保存在一个文件中，所以很容易通过常见方式共享，包括使用 git 等版本管理系统。我们先从最简单的 Recipe 开始。

### 最简单的 Recipe

最简单的 Recipe 基本上就是一个提示词。这看起来似乎没什么用——毕竟，我可以直接在 Slack 或电子邮件里分享提示词——但事实证明，用户无法让 Agent 按预期工作的最重要原因，是提示词太短，而且没有充分迭代优化提示词。将提示词保存在文本文件中，有助于解决这两个问题。

下面是一个用于规划欧洲旅行的 Recipe：

```yaml
title: Trip planner
description: Plan your next trip
prompt: |
 Help the user plan a trip to Europe for 14 days.
 Create a detailed itinerary that includes:
  - places to visit
  - activities to do
  - local cuisine to try
  - a rough budget estimate
```

你可以在命令行中这样运行：

```sh
goose run --recipe trip.yaml
```

### 扩展

goose Recipe 中有一个部分，可用于指定 goose 执行时能使用哪些[扩展](https://block.github.io/goose/docs/guides/recipes/recipe-reference#extensions)。goose 只会使用你指定的扩展。

假设我们希望欧洲旅行期间天气良好。只需在 Recipe 中添加一个 weather 扩展（本例使用 TuanKiri 根据 MIT License 发布的 [weather-mcp-server](https://github.com/TuanKiri/weather-mcp-server)），稍微修改提示词，goose 就会在将城市加入行程前查询天气。

```yaml
title: Trip planner
description: Plan your next trip
prompt: |
 Help the user plan a trip to Europe for 14 days. Create a detailed itinerary that includes:
  - places to visit
  - activities to do
  - local cuisine to try
  - a rough budget estimate
 Ensure that the user has good weather throughout their trip. Optimize their trip based on the forecast in potential locations.
extensions:
  - type: stdio
    name: weathermcpserver
    cmd: /Users/svega/Development/weather-mcp-server/weather-mcp-server
    args: []
    timeout: 300
    description: "Weather data for trip planning"
    env_keys:
      - WEATHER_API_KEY
```

### 参数

你可以通过添加参数，让 Recipe 动态变化。参数是由 Recipe 使用者提供的变量。每个参数都有数据类型及 requirement 字段，用来定义参数是必填、可选，还是由使用者提供。我们可以给旅行 Recipe 添加目的地和旅行时长参数，使其更加通用：

```yaml
parameters:
  - key: destination
    input_type: string
    requirement: required
    description: Destination for the trip. Should be a large region with multiple climates.
  - key: duration
    input_type: number
    requirement: required
    description: Number of days for the trip.
```

Recipe 使用模板系统，让你通过 `{{ destination }}` 这样的变量插入内容，运行时会用你提供的实际值替换这些变量。更新提示词、填入合适的细节后，就可以像下面这样运行新 Recipe，规划一次为期 14 天的非洲旅行：

```sh
goose run --recipe trip.yaml --params destination=Africa --params duration=14
```

### 设置

默认情况下，goose 使用你已选定的 `temperature` 和 `model`，通常这就足够了。不过，有时你可能需要更多控制。例如，规划旅行这类主观任务，可以适当调高 `temperature` 设置。你可以把 temperature 理解为创造力旋钮——数值越高，结果越多样、越出人意料。如果第一次的建议不太合适，使用者可以再次运行 Recipe 获取新的建议。

你也可以指定某个 Recipe 要使用的 AI 提供方和模型：

```yaml
settings:
  goose_provider: "anthropic"
  goose_model: "claude-sonnet-4-20250514"
  temperature: 0.8
```

可用设置如下：
- `goose_provider`：AI 提供方（例如 "anthropic"、"openai"）
- `goose_model`：具体模型名称
- `temperature`：控制创造性/随机性（0.0-1.0，数值越高，创造性越强）

这些设置会在运行此 Recipe 时覆盖 goose 的默认配置。

### 外部文件

有时，你希望 Agent 能访问额外信息，但又不想把所有数据都塞进提示词。与其粘贴所有内容，不如把数据放在单独的文件中，然后让 Recipe 指向它。

为此，Recipe 内置了一个名为 `{{ recipe_dir }}` 的变量，可用于引用与 Recipe 一起存储的文件。例如，你可以从 [Kaggle](https://www.kaggle.com/datasets/ramjasmaurya/unesco-heritage-sites2021?resource=download) 下载 UNESCO 名录，并在旅行规划 Recipe 中使用。

然后，在提示词中这样引用该文件：

```yaml
prompt: |
 You can use the \{\{ recipe_dir \}\}/unesco.csv file to 
 check information on UNESCO world heritage sites to
 include in your travel plan.
```

我们还需要指定一个用于读取文件的扩展：

```yaml
extensions:
 - type: builtin
   name: developer
   display_name: Developer
   timeout: 300
   bundled: true
```

这里添加了 [Developer 扩展](https://block.github.io/goose/docs/mcp/developer-mcp)，它可以读取文件并获取相关信息。

:::info Recipe 输出示例

<details>
<summary>查看详细的 10 天欧洲行程</summary>

根据 UNESCO 世界遗产地信息和当前天气预报，以下是一份详细的 10 天欧洲行程：

### 10 天欧洲探险行程

这份行程将带你游览欧洲最美丽、文化底蕴最深厚的三个国家：法国、意大利和捷克共和国。你将体验世界级博物馆、UNESCO 世界遗产、美味佳肴和活力十足的当地文化。

##### 第 1–3 天：法国巴黎 🇫🇷

**第 1 天：抵达巴黎**
- **上午**：抵达戴高乐机场，前往酒店
- **下午**：沿塞纳河悠闲漫步，参观巴黎圣母院（因正在重建，仅从外部观赏）
- **晚上**：在拉丁区用餐（预算：€30-40）
  - 尝试经典法式洋葱汤和红酒炖鸡

**天气预报**：气温宜人，约 27°C（81°F），局部多云

**第 2 天：巴黎精华游**
- **上午**：参观卢浮宫（预算：€17）
- **下午**：游览杜乐丽花园和香榭丽舍大街
- **晚上**：登上埃菲尔铁塔欣赏日落（登顶门票预算：€26.80）
  - 在夏乐宫附近用餐（预算：€35-45）
  - 尝试蜗牛和勃艮第炖牛肉

**天气预报**：温暖，31°C（88°F），晴朗

**第 3 天：凡尔赛一日游**
- **上午**：前往 UNESCO 世界遗产凡尔赛宫（宫殿门票预算：€21）
- **下午**：游览壮丽的花园
- **晚上**：返回巴黎，在蒙马特用餐（预算：€30-40）
  - 尝试可丽饼和油封鸭

**天气预报**：温暖，30°C（86°F），有小概率降雨

##### 第 4–6 天：意大利罗马 🇮🇹

**第 4 天：前往罗马**
- **上午**：从巴黎飞往罗马（预算：€100-150）
- **下午**：办理酒店入住，游览西班牙台阶和特雷维喷泉
- **晚上**：在特拉斯提弗列街区用餐（预算：€25-35）
  - 尝试正宗的奶酪胡椒意面和培根蛋面

**天气预报**：炎热，35°C（95°F），晴朗

**第 5 天：古罗马**
- **上午**：参观斗兽场和古罗马广场（联票预算：€16）
- **下午**：游览帕拉蒂尼山和大竞技场
- **晚上**：在鲜花广场附近用餐（预算：€30-40）
  - 尝试罗马风味披萨和罗马式牛肉卷

**天气预报**：炎热，35°C（95°F），大部分时间晴朗

**第 6 天：梵蒂冈城**
- **上午**：参观梵蒂冈博物馆和西斯廷教堂（预算：€17）
- **下午**：游览圣彼得大教堂和广场（UNESCO 世界遗产）
- **晚上**：在普拉蒂区用餐（预算：€30-40）
  - 尝试 suppli（炸饭团）和意式炖牛膝

**天气预报**：炎热，34°C（93°F），局部多云

##### 第 7–10 天：捷克共和国布拉格 🇨🇿

**第 7 天：前往布拉格**
- **上午**：从罗马飞往布拉格（预算：€100-150）
- **下午**：办理酒店入住，游览老城广场
- **晚上**：在老城区用餐（预算：€20-30）
  - 尝试传统炖牛肉和 svíčková（腌制牛肉）

**天气预报**：气温宜人，29°C（84°F），局部多云

**第 8 天：布拉格城堡和小城区**
- **上午**：参观布拉格城堡建筑群（UNESCO 世界遗产）（预算：250 CZK/€10）
- **下午**：游览小城区和查理大桥
- **晚上**：在伏尔塔瓦河景观餐厅用餐（预算：€25-35）
  - 尝试 trdelník（甜酥卷）和配饺子的烤鸭

**天气预报**：较凉爽，22°C（72°F），可能有雷暴

**第 9 天：犹太区与文化景点**
- **上午**：参观犹太区（Josefov）和犹太会堂
- **下午**：游览市民会馆和火药塔
- **晚上**：参加传统捷克民俗晚宴并观看表演（预算：€35-45）
  - 尝试捷克啤酒和 kolache 酥饼

**天气预报**：气温宜人，24°C（75°F），大部分时间晴朗

**第 10 天：离开**
- **上午**：最后逛逛布拉格精品店
- **下午**：前往机场，乘坐返程航班

**天气预报**：气温宜人，24°C（75°F），大部分时间晴朗

##### 预算明细（每人）

**住宿（9 晚）**
- 巴黎：€120/晚 × 3 晚 = €360
- 罗马：€100/晚 × 3 晚 = €300
- 布拉格：€80/晚 × 3 晚 = €240
- **住宿合计**：€900

**交通**
- 往返欧洲的国际航班：€600-800（视出发地而定）
- 巴黎飞罗马：€100-150
- 罗马飞布拉格：€100-150
- 当地交通（地铁、巴士、有轨电车）：€15/天 × 10 天 = €150
- **交通合计**：€950-1,250

**景点与活动**
- 巴黎博物馆和景点：€100
- 罗马博物馆和景点：€80
- 布拉格博物馆和景点：€70
- **景点合计**：€250

**餐饮**
- 早餐：€10/天 × 10 天 = €100
- 午餐：€15/天 × 10 天 = €150
- 晚餐：€35/天 × 10 天 = €350
- 零食和饮料：€10/天 × 10 天 = €100
- **餐饮合计**：€700

**其他**
- 旅行保险：€50
- 纪念品和购物：€200
- 应急备用金：€150
- **其他合计**：€400

**总计**
- **每人 €3,200-3,500**（不含往返欧洲的国际航班）

##### 行程中的 UNESCO 世界遗产
- 凡尔赛宫及其园林（法国）
- 罗马历史中心（意大利）
- 梵蒂冈城（意大利）
- 布拉格历史中心（捷克共和国）

##### 旅行提示
1. **天气**：根据天气预报，所有目的地都需要准备适合暖和天气的衣物，气温约为 20-35°C（68-95°F）。布拉格夜晚较凉，带一件薄外套。
2. **货币**：法国和意大利使用欧元（€），捷克共和国使用捷克克朗（CZK）。
3. **交通**：在每个城市购买地铁/公共交通通票可节省开支。
4. **预订**：提前预订热门景点，避免长时间排队，尤其是卢浮宫、梵蒂冈博物馆和埃菲尔铁塔。
5. **饮水**：随身携带可重复使用的水瓶，尤其是气温炎热的罗马。
6. **语言**：学习几句当地语言的基础表达；不过，旅游区普遍使用英语。

这份行程将历史、文化和美食完美融合，带你探索欧洲三个风格迥异的地区。天气应当非常适合观光，大部分时间晴朗温暖。祝你欧洲之旅愉快！

</details>

:::

### 了解更多

请查看 [Recipes](https://block.github.io/goose/docs/guides/recipes) 指南，了解更多帮助你掌握 goose recipes 的文档、工具和资源。

---

## 使用 Langfuse 实现可观测性

> 原文：https://block.github.io/goose/docs/tutorials/langfuse

goose 官方文档中的本教程介绍如何将 goose 与 Langfuse 集成，以监控 goose 请求并了解 Agent 的运行表现。

### 什么是 Langfuse

[Langfuse](https://langfuse.com/) 是一个[开源](https://github.com/langfuse/langfuse) LLM 工程平台，支持团队协作监控、评估和调试 LLM 应用。

### 设置 Langfuse

[注册 Langfuse Cloud](https://cloud.langfuse.com)，或者使用 [Docker Compose 自托管 Langfuse](https://langfuse.com/self-hosting/local)，以获取 Langfuse API keys。

### 配置 goose 以连接 Langfuse

设置环境变量，让使用 Rust 编写的 goose 能够连接 Langfuse 服务器。

```bash
export LANGFUSE_INIT_PROJECT_PUBLIC_KEY=pk-lf-...
export LANGFUSE_INIT_PROJECT_SECRET_KEY=sk-lf-...
export LANGFUSE_URL=https://cloud.langfuse.com # EU data region 🇪🇺

# https://us.cloud.langfuse.com if you're using the US region 🇺🇸
# https://localhost:3000 if you're self-hosting
```

默认情况下，trace 不包含模型消息、工具参数和工具结果。若要包含这些内容，请明确启用内容捕获：

```bash
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
```

只有在遥测数据存储适合保存可能包含敏感信息的内容时，才启用内容捕获。

### 使用 Langfuse 集成运行 goose

现在，你可以运行 goose，并通过 Langfuse 监控 AI 请求与操作。

goose 正在运行且环境变量已设置时，Langfuse 就会开始捕获 goose 活动的 trace。

_[Langfuse 中的 trace 示例（公开）](https://cloud.langfuse.com/project/cloramnkj0002jz088vzn1ja4/traces/cea4ed38-0c44-4b0a-8c20-4b0b6b9e8d73?timestamp=2025-01-31T15%3A52%3A30.362Z&observation=7c8e5807-3c29-4c28-9c6f-7d7427be401f)_

![Langfuse 中的 goose trace](https://langfuse.com//images/docs/goose-integration/goose-example-trace.png)

---

## 使用 Laminar 实现可观测性

> 原文：https://block.github.io/goose/docs/tutorials/laminar

本教程介绍如何将 goose 与 Laminar 集成，以跟踪 goose 会话并了解 Agent 的运行表现。

### 什么是 Laminar

[Laminar](https://laminar.sh/) 是一个专为 AI Agent 打造的开源可观测性平台。它可以跟踪 LLM 调用、工具执行和自定义函数，帮助你调试、评估并改进 Agent 行为。

### 为什么 goose 适合使用 Laminar

- 为 LLM 调用、工具和子代理提供高信号 trace。
- 在 Playground 中重放任意 span，对比提示词和模型。
- 根据生产 trace 构建数据集并运行评估。
- 使用自然语言查询和仪表板分析 trace 模式。

### 设置 Laminar

在 [laminar.sh](https://laminar.sh) 注册 Laminar Cloud，或者从[开源仓库](https://github.com/lmnr-ai/lmnr)自托管 Laminar。获取项目 API key。

### 配置 goose 将 OTLP 导出到 Laminar

goose 通过 OTLP/HTTP 导出 OpenTelemetry 数据。将 exporter 指向 Laminar，并通过 authorization header 提供 API key。

#### Laminar Cloud

```bash
export LMNR_PROJECT_API_KEY=lmnr_proj_...
export OTEL_EXPORTER_OTLP_ENDPOINT="https://api.lmnr.ai"
export OTEL_EXPORTER_OTLP_HEADERS="authorization=Bearer ${LMNR_PROJECT_API_KEY}"
export OTEL_EXPORTER_OTLP_TIMEOUT=10000
```

#### 自托管 Laminar

```bash
export LMNR_PROJECT_API_KEY=lmnr_proj_...
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:8000"
export OTEL_EXPORTER_OTLP_HEADERS="authorization=Bearer ${LMNR_PROJECT_API_KEY}"
```

如果你的自托管实例不需要身份验证，可以省略 `OTEL_EXPORTER_OTLP_HEADERS`。

:::tip
如果没有看到 trace，请尝试将 endpoint 设置为明确的 OTLP 路径，例如 `https://api.lmnr.ai/v1/traces` 或 `http://localhost:8000/v1/traces`。
:::

### 启用 Laminar 后运行 goose

正常启动 goose。设置好 OTLP 环境变量后，Laminar 就会捕获 goose 会话和工具执行的 trace。

_[Laminar 中的 trace 示例（公开）](https://laminar.sh/shared/traces/63010af0-cf31-b8b6-0d77-fc9924bcaa4c)_

![Laminar 中的 goose trace](https://block.github.io/goose/docs/assets/guides/laminar.png)

---

## 使用 MLflow 实现可观测性

> 原文：https://block.github.io/goose/docs/tutorials/mlflow

本教程介绍如何将 goose 与 MLflow 集成，以跟踪 goose 会话并了解 Agent 的运行表现。

### 什么是 MLflow

[MLflow](https://mlflow.org/) 是一个[开源](https://github.com/mlflow/mlflow)平台，用于管理端到端的机器学习和 AI 生命周期。MLflow Tracing 能够详细观察 AI Agent 的执行过程，通过丰富的可视化界面捕获 LLM 调用、工具使用和 Agent 决策。

### 为什么 goose 适合使用 MLflow

- **详细的 trace 可视化**：在分层 trace 视图中检查每一次 LLM 调用、工具执行和 Agent 决策。
- **Token 用量跟踪**：监控不同会话的输入/输出 token 数量与成本。
- **评估框架**：使用内置 LLM judges 和自定义 scorer 评估 Agent 输出。
- **提示词管理**：对 AI 应用中使用的提示词进行版本管理。
- **开源**：完全开源，不会被供应商锁定，可自行托管在任何位置。

### 设置 MLflow

安装 MLflow 并启动 tracking server：

```bash
pip install mlflow
mlflow server --port 5000
```

MLflow UI 将在 `http://localhost:5000` 提供服务。

:::tip
生产环境中，请使用 SQL backend store（PostgreSQL、MySQL），不要使用默认的 SQLite。详情请参阅 [MLflow 文档](https://mlflow.org/docs/latest/self-hosting/architecture/backend-store.html)。
:::

### 配置 goose 将 OTLP 导出到 MLflow

goose 通过 OTLP/HTTP 导出 OpenTelemetry 数据。将 exporter 指向 MLflow 的 OTLP endpoint：

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:5000"
export OTEL_EXPORTER_OTLP_HEADERS="x-mlflow-experiment-id=0"
```

`x-mlflow-experiment-id` header 用于指定将 trace 记录到哪个 MLflow experiment。使用 `0` 表示默认 experiment，或者创建一个专用 experiment：

```bash
pip install mlflow
mlflow experiments create --experiment-name "goose-traces"
# Use the returned experiment ID in the header
```

若只导出 trace（禁用 metrics 和 logs 导出）：

```bash
export OTEL_TRACES_EXPORTER=otlp
export OTEL_METRICS_EXPORTER=none
export OTEL_LOGS_EXPORTER=none
```

要在 trace 中包含模型消息和工具参数/结果，请明确启用 GenAI 消息内容捕获：

```bash
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
```

:::warning
消息内容可能包含敏感数据，并导致 trace 体积增大。除非遥测存储适合保存这类数据，否则请保持此设置禁用。
:::

### 启用 MLflow 后运行 goose

正常启动 goose。设置好 OTLP 环境变量后，goose 会自动向 MLflow 导出 trace：

```bash
goose session
```

打开 MLflow UI `http://localhost:5000`，进入 **Traces** 标签页，即可查看 goose 会话的详细 trace，包括 LLM 调用、工具执行和 token 用量。

![MLflow 中的 goose trace](https://block.github.io/goose/docs/assets/guides/mlflow-goose-tracing.png)

### 了解更多

- [MLflow Tracing 文档](https://mlflow.org/docs/latest/genai/tracing/)
- [MLflow OpenTelemetry 集成](https://mlflow.org/docs/latest/genai/tracing/app-instrumentation/opentelemetry.html)
- [MLflow goose 集成指南](https://mlflow.org/docs/latest/genai/tracing/integrations/listing/goose.html)

---

## 使用 ClawMetry 实现可观测性

> 原文：https://block.github.io/goose/docs/tutorials/clawmetry

本教程介绍如何使用 ClawMetry 查看 goose 会话执行了哪些操作、使用了哪些模型以及产生了多少费用。与 trace 集成不同，ClawMetry 无需任何配置：它会读取 goose 已经写入的会话存储。

### 什么是 ClawMetry

[ClawMetry](https://clawmetry.com/) 是面向 AI Agent 的[开源](https://github.com/vivekchand/clawmetry)（MIT）可观测性仪表板。它在你的机器上运行，读取 Agent 已生成的本地文件，并在 `http://localhost:8900` 提供仪表板。在这个开源应用中，goose 是免费的运行时，且软件包内置 goose adapter。

### 为什么 goose 适合使用 ClawMetry

- **无需插桩**：无需环境变量、exporter 或 SDK。ClawMetry 直接读取 `sessions.db`，因此以前的会话也会显示出来。
- **默认本地运行**：仪表板在你的机器上运行，不会向任何地方发送数据。虽然支持云同步，但这是可选功能，默认关闭。
- **只读**：goose 拥有自己的会话存储。ClawMetry 始终以只读方式打开它，不会写入数据。
- **真实 token 数量**：goose 会将用量记录到磁盘，因此 token 总数来自你的会话，而非估算值。
- **开源**：采用 MIT License，goose adapter 的源代码也可在仓库中查看。

### 设置 ClawMetry

```bash
pip install clawmetry
clawmetry
```

然后打开 `http://localhost:8900`。

设置就全部完成了。无需在 goose 侧进行配置，因为 ClawMetry 不处于请求路径中。

### 运行 goose

照常使用 goose：

```bash
goose session
```

ClawMetry 会通过与 goose 相同的方式解析其数据目录，自动检测[会话存储](https://block.github.io/goose/docs/guides/logs#session-records)：

| 平台 | 会话存储 |
| --- | --- |
| macOS 和 Linux | `$XDG_DATA_HOME/goose/sessions/sessions.db`；默认路径为 `~/.local/share/goose/sessions/sessions.db` |
| Windows | `%APPDATA%\Block\goose\data\sessions\sessions.db` |

如果设置了 [`GOOSE_PATH_ROOT`](https://block.github.io/goose/docs/guides/environment-variables)，ClawMetry 会在所有平台上改为读取 `$GOOSE_PATH_ROOT/data/sessions/sessions.db`。在 macOS 上，它还会最后检查 `~/Library/Application Support/Block/goose/`，因此仍将数据保存在此处的旧版安装也能被识别。

安装 ClawMetry 之前运行的会话也会显示。

### 你可以看到的内容

- **会话**：每个 goose 会话的开始时间、消息数量和工作目录。
- **对话记录**：完整的逐轮对话，包括工具调用及其结果。
- **模型**：每个会话使用的模型，以及不同模型间的用量分布。
- **Token 和成本**：每个会话的输入、输出及 token 总数；若 goose 记录了成本，则一并显示。

:::note
goose 只会为能够报告成本的提供方填入成本数值。对于 Ollama 这类本地提供方，没有成本可记录，因此 ClawMetry 会显示 token 数量，并将成本留空，而不会捏造数字。
:::

:::tip
如果你运行了多个 Agent，可使用仪表板顶部的运行时切换器，将所有视图限定为仅显示 goose。
:::

### 了解更多

- [ClawMetry 仓库](https://github.com/vivekchand/clawmetry)
- [goose adapter 源码](https://github.com/vivekchand/clawmetry/blob/main/clawmetry/adapters/goose.py)
- [ClawMetry 文档](https://clawmetry.com/docs)

---

## 使用 Remotion Skills 创建视频

> 原文：https://block.github.io/goose/docs/tutorials/remotion-video-creation

goose 可以使用 [Remotion](https://www.remotion.dev/) 创建程序化视频。Remotion 是一个使用 React 创建视频的框架。加载 [Remotion Agent Skills](https://www.remotion.dev/docs/ai/skills) 后，goose 就能掌握动画、合成、文字效果和视频渲染方面的最佳实践。

#### 先决条件

- [Node.js](https://nodejs.org/) 18 或更高版本
- 在终端中运行 `npx skills add remotion-dev/skills`，安装 [Remotion Agent Skills](https://www.remotion.dev/docs/ai/skills)

:::note Remotion License
Remotion 对个人和小型团队免费，但员工人数达到 3 人或以上的公司需要[商业许可证](https://www.remotion.dev/license)。
:::

### 配置

启用 [Summon 扩展](https://block.github.io/goose/docs/mcp/summon-mcp)，以允许 goose 加载并使用 Agent Skills。

<Tabs groupId="interface">
  <TabItem value="ui" label="goose Desktop" default>
  <GooseBuiltinInstaller
    extensionName="Summon"
  />
  </TabItem>
  <TabItem value="cli" label="goose CLI">

  1. 运行 `configure` 命令：
```sh
  goose configure
```

  2. 选择 `Toggle Extensions`
```sh
  ┌   goose-configure 
  │
  ◇  What would you like to configure?
  │  Toggle Extensions 
  │
  ◆  Enable extensions: (use "space" to toggle and "enter" to submit)
  // highlight-start    
  │  ● summon
  // highlight-end
  |
  └  Extension settings updated successfully
```
  </TabItem>
</Tabs>

### 使用示例

在本例中，我们将让 goose 创建一段终端风格的视频，演示 git 工作流。视频将包含打字机效果、逼真的终端输出，以及结尾的庆祝动画。

:::info LLM
本示例使用了 Anthropic 的 Claude Opus 4.5。
:::

#### goose 提示词

```
Create a terminal-style video showing a git workflow: type out git add ., 
then git commit -m 'feat: add new feature', then git push origin main. 
Each command should appear with a typewriter effect, followed by realistic output. 
End with 'Deployed to production 🚀'
```

#### goose 输出

```
─── load | summon ───────────────────────────────────────
source: remotion-best-practices

reading ~/.agents/skills/remotion-best-practices/rules/animations.md

─── shell | developer ─────────────────────────────────────────
mkdir -p git-terminal-video && cd git-terminal-video && npm init -y

─── shell | developer ─────────────────────────────────────────
npm install remotion @remotion/cli react react-dom typescript @types/react

─── text_editor | developer ───────────────────────────────────
writing git-terminal-video/src/GitTerminal.tsx

─── text_editor | developer ───────────────────────────────────
writing git-terminal-video/src/Root.tsx

─── text_editor | developer ───────────────────────────────────
writing git-terminal-video/remotion.config.ts

─── shell | developer ─────────────────────────────────────────
npx remotion render GitTerminal out/git-workflow.mp4

✓ Video rendered successfully

✅ Git Terminal Video Created
Location: git-terminal-video/out/git-workflow.mp4

Video Details
├── Duration: 14 seconds (420 frames @ 30fps)
├── Resolution: 1280x720 (HD)
├── Size: ~875 KB
└── Codec: H.264

What the Video Shows
├── Terminal Window - macOS-style with traffic light buttons
├── Command Sequence with Typewriter Effect:
│   ├── ~/my-project ❯ git add .
│   ├── ~/my-project ❯ git commit -m 'feat: add new feature'
│   │   └── Shows realistic output with files changed
│   └── ~/my-project ❯ git push origin main
│       └── Shows push output (enumerating, compressing, writing)
└── Final Message - "Deployed to production 🚀" with bounce animation

Features
├── Blinking cursor while typing
├── Staggered output reveal (each line appears with delay)
├── Color-coded syntax (prompts, commands, output)
├── Spring animations for success message
└── Animated rocket that floats and bounces
```

---

