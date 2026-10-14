---
name: scrapling
description: Python 抓取框架 Scrapling（已装在本机托管 venv default）。当需要用 Python 批量抓取网页并用 CSS/XPath 选择器解析（标题、链接、表格、字段提取）时使用。2026-10-13 本机实测：HN、Wikipedia、httpbin、example.com 全部 200 且解析正确。含安装必须项、Fetcher 用法与 DynamicFetcher 前置条件。
agent_created: true
---

# Scrapling 抓取框架（本机已安装）

## Overview

Scrapling 0.4.15（+ curl_cffi / patchright / browserforge 全家桶）已安装在本机托管 venv `default`。Fetcher（curl_cffi 内核）无需浏览器即可抓取并解析，自带请求指纹伪装，是「装了就能用」的 Python 抓取入口。本机无 Docker，agent-browser 挂起不可用；需要纯命令行渲染时用 moli 技能，需要 Python 选择器解析时用本技能。

## 快速开始

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/envs/default/Scripts/python.exe"
"$PY" -c "from scrapling import Fetcher; print(Fetcher().get('https://example.com').status)"
```

## 安装（若环境重置后重装）

```bash
# 必须带 [all]，裸装缺 curl_cffi/playwright/patchright，import 连环 ModuleNotFound
"C:/Users/Admin/.workbuddy-ai/binaries/python/envs/default/Scripts/python.exe" -m pip install "scrapling[all]"
```

## 核心用法

### Fetcher（curl_cffi 内核，无需浏览器，首选）

```python
from scrapling import Fetcher
f = Fetcher()
page = f.get('https://news.ycombinator.com')
print(page.status)                          # 200
titles = page.css('.titleline a::text').getall()[:5]
links  = page.css('.titleline a::attr(href)').getall()
rows   = page.xpath('//table//tr')          # XPath 同样支持
```

### DynamicFetcher / StealthyFetcher（真实浏览器 + 指纹伪装）

前置条件（本机未执行未测）：`"$PY" -m playwright install chromium`（约 170MB）。装好后即可抓 JS 渲染页与强指纹检测站点。

## 实测记录（2026-10-13，本机）

| 目标 | 结果 |
|---|---|
| example.com | 200，title=Example Domain |
| news.ycombinator.com | 200，`.titleline a::text` 提取 top5 标题全部正确 |
| en.wikipedia.org/wiki/Web_scraping | 200，35 个 `<p>` 解析正常 |
| httpbin.org/html | 200，h1 提取正常 |

## 坑与反直觉

1. **安装必须 `scrapling[all]`**：裸 `pip install scrapling` 装出的包 import 时报 `No module named 'curl_cffi'` → 补装后继续报 `playwright` → 再报 `patchright`，连环缺依赖；一步 `[all]` 全解决。
2. **venv 解释器路径是 `Scripts\python.exe`**（Windows venv 布局），不是 Linux 的 `bin/python`；写错路径报 No such file。
3. **日志走 stderr**：`INFO: Fetched (200) <GET ...>` 会混在终端输出里，管道给下游命令时用 `2>/dev/null` 或只认 stdout。
4. **`css('h1::text')` 对嵌套结构可能返 None**（Wikipedia 实测如此），换 `.get('')`、父选择器或 textContent 类写法；`:text` 只取直接文本节点。

## 何时不用本技能

- 只要渲染后的页面/截图/PDF，不需要 Python 解析 → 用 moli 技能（更轻，一条命令）。
- 需要登录态或过 Cloudflare → Playwriter（真实 Chrome 扩展）或有头 Chrome + CDP。
- 生产级大规模采集 → 评估 Apify / Bright Data 等托管通道（见工作区调研报告）。
