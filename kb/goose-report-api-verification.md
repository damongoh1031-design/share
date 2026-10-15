---
id: goose-report-api-verification
title: 研究报告的 API 级复核方法论与 goose 权威事实快照
tags:
  - 研究方法论
  - 事实核查
  - GitHub API
  - goose
  - AI Agent
  - 文档复核
created: 2026-10-15
updated: 2026-10-15
version: 1.0
status: stable
source: 本次会话实测（GitHub REST API + 仓库原文 + LF Insights API）
confidence: 已核实
---

## TL;DR

**对话式研究产出的报告，通病是"数字会漂、排名会算错、产物会被笼统归类"。** 复核一份 GitHub 研究报告的正确姿势不是重读文字，而是**把每个数值当成待验证断言，用 API 重采一遍**。本轮对 goose 报告 v1.1 的复核中，14 个仓库的全部硬指标重采一次，就抓出 3 处实质错误（含 1 处排名算错、1 处口径混淆、1 处重大遗漏）。

---

## 一、goose 权威事实快照（2026-10-15 实测）

| 指标 | 值 | 备注 |
|---|---|---|
| 仓库 | `aaif-goose/goose` | 原 `block/goose`，2026-04 迁移 |
| Stars / Forks | 55,293 / 6,437 | 对比组内排第 **9** |
| Contributors | 453 | 与 Codex(478)、OpenHands(461) 同级 |
| Open Issues | 480 | issues/stars = **0.87%**，同量级最优 |
| 主语言 | Rust 10,506,629 B（71.59%）+ TS 3,446,615 B（23.49%） | `rust-toolchain.toml` 锁 1.99.0 |
| 许可证 | Apache-2.0（文档 CC-BY-4.0） | — |
| 创建 / 最后推送 | 2024-08-23 / 2026-10-15 | 日更 |
| 稳定版 | **v1.54.0**（2026-10-08） | 2.0 仍为 beta |
| 治理 | Linux 基金会 AAIF（LF Projects, LLC 的 Series 项目） | 组织 2026-03-25 建 |
| Core Maintainers | **7 人**（区间 3–7，追求奇数） | MAINTAINERS.md 实名 |
| 第三方健康分 | **Healthy** | LF Insights 官方徽章 |
| crates 工作区 | **15 个 crate** | 含 `goose-local-inference`、`goose-context-management` |

### v1.54.0 发布产物构成（40 个）

| 类别 | 数量 | 说明 |
|---|---:|---|
| Linux 原生包 | **12** | 4 RPM + 4 DEB + 4 **Flatpak**（各含 x86_64/arm64 × 普通/vulkan） |
| Linux CLI tarball | **12** | `{x86_64,aarch64}-unknown-linux-{gnu,gnu-vulkan,musl}` × `{tar.gz,tar.bz2}` |
| macOS | 9 | 4 桌面 zip + 4 CLI tarball + 1 更新清单 |
| Windows | 4 | 2 桌面 zip + 2 CLI zip（各含 cuda 变体） |
| 源码 / 脚本 | 2 / 1 | — |
| **Linux 合计占比** | **24 / 40 = 60%** | — |

> 关键：**Flatpak ID 为 `io.github.block.Goose`**——迁移至 AAIF 后仍保留 block 命名空间，属迁移遗留。

---

## 二、竞品实时硬数据（2026-10-15）

| 排名 | 产品 | 仓库 | Stars | 贡献者 | Open Issues | 许可证 |
|---:|---|---|---:|---:|---:|---|
| 1 | opencode | `anomalyco/opencode` | 213,573 | 454 | 4,265 | MIT |
| 2 | Dify | `langgenius/dify` | 158,511 | 456 | 1,131 | NOASSERTION |
| 3 | Claude Code | `anthropics/claude-code` | 150,923 | 57 | 15,014 | **无（专有）** |
| 4 | Codex | `openai/codex` | 129,272 | 478 | 22,620 | Apache-2.0 |
| 5 | Pi Agent | `earendil-works/pi` | 115,237 | 291 | 342 | MIT |
| 6 | Gemini CLI | `google-gemini/gemini-cli` | 107,372 | 443 | 745 | Apache-2.0 |
| 7 | OpenHands | `OpenHands/OpenHands` | 90,928 | 461 | 996 | MIT |
| 8 | Cline | `cline/cline` | 70,339 | 340 | 1,664 | Apache-2.0 |
| **9** | **goose** | `aaif-goose/goose` | **55,293** | **453** | **480** | **Apache-2.0** |
| 10 | Aider | `Aider-AI/aider` | 49,554 | 172 | 1,920 | Apache-2.0（**2026-05-22 停更**） |
| 11 | Continue | `continuedev/continue` | 36,226 | 393 | 851 | Apache-2.0 |
| 12 | OpenWork | `different-ai/openwork` | 24,109 | 71 | 629 | NOASSERTION |
| 13 | Octop | `TencentCloud/Octop` | 9,362 | 62 | 825 | MIT |

### 两个被低估的派生指标

- **issues ÷ stars**（越低越好）：goose **0.87%** / Gemini CLI 0.69% / opencode 2.0% / Claude Code 9.9% / Codex 17.5%。
- **月均新增 stars**（stars ÷ 存续月数）：opencode ≈11,865 / Pi ≈8,230 / Octop ≈3,121 / OpenWork ≈2,679 / **goose ≈2,127**。

> 结论：goose「开源最早」未转化为「声量最大」，月均增速仅为 Pi 的 1/3.9。

---

## 三、可复用操作

### 3.1 一份 GitHub 研究报告的复核清单

```bash
export TOKEN=<your_github_pat>   # 需 repo 读权限；匿名限流 60 次/小时

R=aaif-goose/goose

# ① 硬指标：stars / forks / issues / license / language / 创建 / 推送
curl -s -H "Authorization: Bearer $TOKEN" https://api.github.com/repos/$R

# ② 贡献者数：读 Link header 的最后一页（比 /contributors 全量拉取省额度）
curl -sI -H "Authorization: Bearer $TOKEN" \
  "https://api.github.com/repos/$R/contributors?per_page=1" | grep -i '^link:'

# ③ 语言字节数（用于精确占比，而非 GitHub 首页的模糊百分比）
curl -s -H "Authorization: Bearer $TOKEN" https://api.github.com/repos/$R/languages

# ④ 单版发布产物逐条清单（复核"N 个产物"类断言的关键）
curl -s -H "Authorization: Bearer $TOKEN" \
  https://api.github.com/repos/$R/releases/tags/v1.54.0 \
  | python -c "import sys,json;[print(a['name']) for a in json.load(sys.stdin)['assets']]"

# ⑤ 治理文件原文（不要引用二手转述）
for f in GOVERNANCE.md MAINTAINERS.md README.md rust-toolchain.toml; do
  curl -s -H "Authorization: Bearer $TOKEN" \
    "https://raw.githubusercontent.com/$R/main/$f"
done

# ⑥ 文件存在性批量校验（用于核实"仓库内有 X 文件"类断言）
for f in RISCV_SETUP.md flake.nix CUSTOM_DISTROS.md; do
  echo "$f -> $(curl -s -o /dev/null -w '%{http_code}' \
    -H "Authorization: Bearer $TOKEN" https://api.github.com/repos/$R/contents/$f)"
done

# ⑦ 组织信息（核实"何时迁入某组织"）
curl -s -H "Authorization: Bearer $TOKEN" https://api.github.com/orgs/aaif-goose

# ⑧ 第三方权威健康分（Linux 基金会）
curl -s "https://insights.linuxfoundation.org/api/badge/health-score?project=goose"
```

### 3.2 排名类断言的正确算法

不要手数。**先按指标降序排出完整表，再用行号定位**。本轮 v1.1 的"第 7 位"错误，正是因为报告表格里 goose 实际在第 9 行，而摘要凭印象写了第 7。

```bash
# 用 API 结果直接排序定位
curl -s -H "Authorization: Bearer $TOKEN" https://api.github.com/repos/$R \
  | python -c "import sys,json;d=json.load(sys.stdin);print(d['stargazers_count'])"
# 然后与全部对比对象的值一起排序，看 goose 落在第几行
```

### 3.3 发布物分类清点

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  https://api.github.com/repos/$R/releases/tags/v1.54.0 \
  | python -c "
import sys,json,collections
d=json.load(sys.stdin); c=collections.Counter()
for a in d['assets']:
    n=a['name'].lower()
    for ext,k in (('.rpm','rpm'),('.deb','deb'),('.flatpak','flatpak'),
                  ('.dmg','macos'),('.msi','windows'),('.tar.gz','tarball')):
        if n.endswith(ext): c[k]+=1; break
    else: c['other']+=1
print('total',len(d['assets'])); print(dict(c))
"
```

---

## 四、坑与反直觉

1. **"N 个产物"是最容易错的断言类型。** 总数 ≠ 某平台数。goose 的 40 个产物里 Linux 只占 24 个。凡是看到"每版发布约 N 个 X 相关产物"，必须逐条清点。
2. **排名会因漏看中间项而整体偏移。** 报告表格里明明排在第 9 行，摘要却写"第 7 位"——**摘要与表格不一致是高频错误**，复核时要交叉比对同一数值在全文的所有出现位置。
3. **新格式容易被忽略。** Flatpak / DEB 这类"后来加的"分发渠道，对话式研究时不会主动去找。**只有清点 assets 才会发现**。
4. **`license: null` ≠ 不开源。** Claude Code 源码可见但无 OSI 许可证，准确表述是"源码公开可见但无 OSI 许可证"，不能说"不开源"（v1.1 已修此点）。
5. **`pushed_at` 是判断"停更"的唯一硬证据。** Aider 4.96 万星看着很活跃，但 `pushed_at = 2026-05-22`——星数是历史存量，推送时间才是当前状态。
6. **`created_at` 决定增速分母。** 说"一年内涨到 X"前先查创建日：opencode 创建于 2025-04-30，到 2026-10 是约 18 个月，不是一年。
7. **官方组织建立时间早于迁入公告。** `aaif-goose` 组织 2026-03-25 建，博客 2026-04-07 才宣布迁入——"宣布"与"落地"是两个时间点，别混用。
8. **同名仓库是干扰项。** `synix/pi-mono`（2 星）vs 真身 `earendil-works/pi`（115,237 星，原 `badlogic/pi-mono` 301 重定向）。查仓库前先确认重定向后的 `full_name`。

### 文档产出侧的坑（本轮实测）

9. **HTML 分块写入会导致 head/body 重复闭合。** 分块写长 HTML 时，若某片段的开头/结尾边界落在 `</head><body>` 上，合并后会出现两个。**合并后必须跑标签配对自检**：
   ```python
   # 基于 html.parser 的轻量检查：入栈出栈，最后栈空且无孤立闭合标签即通过
   ```
10. **公开仓库推送前必须清理本地路径。** 附录命令里的 `cat ~/.workbuddy-ai/skills/.../token.txt` 虽不含凭据，但暴露本机目录结构，应泛化为 `export TOKEN=<your_github_pat>`。
11. **同步多会话共用仓库时推单文件而非目录。** `sync.py` 对目录执行 `rmtree + copytree`（镜像覆盖），会静默删除或回退别人的文件。`--src file --dest path/file` 走 `copy2`，零风险。

---

## 五、未核实 / 存疑

| 事项 | 状态 |
|---|---|
| goose 2.0 GA 时间 | 未公布，稳定线仍为 1.x |
| Flatpak 是否已正式上架 Flathub 商店 | 产物已发布，未核验商店条目 |
| `goose-cli` 在主流发行版官方源的收录范围 | repology 有收录，范围未逐一核实 |
| Pi 在 Terminal-Bench 的具体排名 | 单一社区来源，未见官方榜单 |
| WorkBuddy Linux GUI 成熟度 | 2026-06 来源与 2026-10 官方教程矛盾，需实测 |
| AAIF 成员公司完整名单 | 部分来自百科 / 媒体转述 |
| 订阅 OAuth 用于第三方客户端的合规性 | 判断项，非事实 |
