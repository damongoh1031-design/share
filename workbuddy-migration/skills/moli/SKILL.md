---
name: moli
description: Windows 本机无头浏览器 moli（CLI，已安装于 C:\Users\Admin\.workbuddy-ai\tools\moli\moli.exe）。当需要抓取网页并输出 markdown/HTML/JSON/截图/PDF、在页面中执行 JS、或启动 CDP/WebDriver 服务端时使用。适用于无 Docker、无 Playwright、无编译工具链的轻量渲染场景。2026-10-13 本机实测：fetch、markdown、--eval、--layout 截图全部通过。
agent_created: true
type: Checklist
---

# Moli 无头浏览器（本机已安装）

## Overview

moli v1.1.17，Rust 单体可执行文件（107MB），零依赖零工具链，已安装在本机固定路径。本机环境无 Docker / cargo / go，且 agent-browser（新旧两版）实测挂起不可用、lightpanda 无 Windows release——moli 是本机首选的命令行无头浏览器。

## 快速开始

```bash
MOLI="/c/Users/Admin/.workbuddy-ai/tools/moli/moli.exe"
"$MOLI" --version                                            # moli 1.1.17
"$MOLI" fetch --dump markdown https://example.com            # 抓取为 markdown
"$MOLI" fetch --layout --dump screenshot https://example.com > out.png   # 截图
```

## 核心命令

### fetch — 抓取单个 URL

| 参数 | 作用 |
|---|---|
| 无 `--dump` | 输出渲染后的完整 HTML |
| `--dump markdown` | LLM 友好的正文 markdown |
| `--dump json` / `html` / `semantic_tree` / `semantic_tree_text` | 结构化/树形输出 |
| `--dump screenshot` / `screenshot_full` / `pdf` | 视口 PNG / 整页 PNG / 分页 PDF——**必须同时加 `--layout`**，否则 exit 1 报 `requires --layout or MOLI_LAYOUT=true` |
| `--eval "<JS>"` | 页面就绪后执行 JS（Promise 会 await），字符串按文本输出、其他值按 JSON 输出 |
| `--eval-file <path>` | 从文件/stdin 读取 JS，绕开命令行长度限制 |
| `-H "K: V"` | 自定义请求头 |
| `--fail` | 主文档 HTTP ≥400 时 exit 22 并抑制输出 |
| `--disable-js` | 关闭 JS |

### serve — 浏览器服务端

启动 CDP / WebDriver Classic / WebDriver BiDi 服务，供 Playwright / Puppeteer 等以标准协议对接（本机未实测 serve 模式，fetch 全通过）。

## 实测记录（2026-10-13，本机）

| 命令 | 结果 |
|---|---|
| `--version` | moli 1.1.17 |
| `fetch https://example.com` | 200，渲染后 HTML |
| `fetch --dump markdown https://example.com` | 正确 markdown |
| `fetch --eval "document.title + ' \| ' + location.host"` | `Example Domain \| example.com` |
| `fetch --dump markdown https://en.wikipedia.org/wiki/Web_scraping` | 真实站点渲染正常 |
| `fetch --layout --dump screenshot https://example.com` | 83,709 字节合法 PNG |

## 坑与反直觉

1. **screenshot / screenshot_full / pdf 必须加 `--layout`**：不开时 engine 用确定性兼容几何、不构造布局，直接报错 exit 1。
2. **大输出先重定向到文件再 `head`**：直接管道到 head 可能丢输出。
3. **exit code 语义**：1 = 就绪/输出错误；22 = HTTP ≥400（配合 `--fail`）。
4. **升级/重装**：GitHub `lexmount/moli` releases → `moli-x86_64-pc-windows-msvc.zip`，解压取 `moli.exe` 覆盖 `~/.workbuddy-ai/tools/moli/`。

## 何时不用本技能

- 需要登录态或过 Cloudflare 类强反爬 → 用 Playwriter（真实 Chrome 扩展）或有头 Chrome + CDP（`--disable-blink-features=AutomationControlled`）。
- 需要 Python 生态批量抓取与选择器解析 → 用 scrapling 技能。
- 需要跨平台/Linux 环境 → 直接用 Playwright/Puppeteer。
