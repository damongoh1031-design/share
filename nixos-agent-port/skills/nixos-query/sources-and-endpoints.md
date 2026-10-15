---
type: Checklist
---

# 11 个数据源：端点、取数方式与缓存

理解这些的价值：**知道每个 source 背后是什么，就能预判延迟、失败模式与可信度**——
以及知道"为什么这个服务器只有 2 个工具却覆盖这么多东西"。

## 总表

| source | 端点 / 机制 | 取数方式 | 缓存 | 需要网络 | 需要 Nix |
|---|---|---|---|---|---|
| `nixos` | `search.nixos.org/backend` | **Elasticsearch `_search` + 手写 query DSL + rescore** | ❌ 实时 | ✅ | ❌ |
| `home-manager` | `nix-community.github.io/home-manager/print.html` | 抓 **1 个约 4.3 MB 的单页 HTML** 再解析 | ✅ 进程内 | ✅ | ❌ |
| `darwin` | `nix-darwin.github.io/nix-darwin/manual/index.html` | 同上 | ✅ 进程内 | ✅ | ❌ |
| `nixvim` | `nix-community.github.io/nixvim/search/data/options/chunks/N.json` | **按 chunk 顺序拉到 404 为止**（约 60 chunk / 17,000 option） | ✅ 进程内 | ✅ | ❌ |
| `nvf` | `nvf.notashelf.dev/options.html` | HTML 解析（最新 unstable 文档） | ✅ 进程内 | ✅ | ❌ |
| `noogle` | `noogle.dev/api/v1/data` | 一次拉 **约 4.46 MB JSON** | ✅ 进程内 | ✅ | ❌ |
| `nix-dev` | `nix.dev/searchindex.js` | 读 **Sphinx 搜索索引** | ✅ 进程内 | ✅ | ❌ |
| `wiki` | `wiki.nixos.org/w/api.php` | **MediaWiki API** | ❌ | ✅ | ❌ |
| `flakehub` | `api.flakehub.com` | REST | ❌ | ✅ | ❌ |
| `nixhub` | `search.devbox.sh` | REST（版本史 + store path） | ❌ | ✅ | ❌ |
| `flakes` | search.nixos.org 的 flake 索引 | 走 NixOS 那条 ES 通道 | ❌ | ✅ | ❌ |
| `cache`（action） | `cache.nixos.org` | NixHub 解析出 store path → 查 `.narinfo` | ❌ | ✅ | ❌ |
| `store`（action） | **本地 `/nix/store`** | **直接读盘** | ❌ | ❌ | ❌ |
| `flake-inputs`（action） | 本地 `/nix/store` | `nix flake archive --json` | ❌ | ❌ | ✅ |

## 三个值得理解的设计决策

### 1. NixOS 源：手写 ES query + 复刻上游的 rescore

上游的搜索索引是 Elasticsearch，但**不是简单 `match` 就完事**。查询构造里包含：

- 对多词查询的 phrase 字段加权：`package_description^3`、`package_longDescription^1`
- **rescore 阶段**用脚本打分 `1.0 / doc['package_attr_name'].value.length()`，权重 `20.0`

意思是 **主名越短越优先** —— 搜 `firefox` 时 `firefox` 排在 `firefox-esr` / `firefox-mobile`
前面。注释说明这是**复刻 search.nixos.org 自己的 `rescoreQuery`**（因为索引里没有等价的
"主名长度"信号）。

**对你的意义**：`action=info` 遇到同名多包（firefox / firefox-esr / firefox-mobile）时，
规范 attribute 会胜出，并且**响应里会显式标注这个歧义**。

### 2. HTML 源：抓"print 单页"而不是爬多页

Home Manager 的 option 文档分散在 mdBook 的几百个页面里。上游的选择是抓
**`print.html`（把全部 option 目录合在一页）**，一次请求换全量目录，然后本地搜索/浏览/统计。

**对你的意义**：Home Manager / darwin 的首次查询会有一次较大的下载（秒级），之后进程内缓存。
**如果第一次查 home-manager 感觉慢，那是正常的。**

### 3. Nixvim：按 chunk 拉到 404

NuschtOS 的搜索基础设施把 option 切成约 300 个一组的 chunk（`chunks/N.json`）。
上游**从 0 开始顺序拉，直到 404**，然后在 Python 里搜。注释说当前约 60 chunk / 17,000 option，
"fits comfortably in memory"。

**对你的意义**：这是一次性全量加载，首次调用偏慢，之后走缓存。路径在 2026 年中重组过
（旧的 `search/meta/N.json` 已移除），所以**这类 source 的上游路径是会漂移的**。

## channel 解析：为什么"stable"永远对

NixOS 的 channel 名随 Hydra 发布滚动（`latest-<gen>-nixos-<channel>`）。硬编码必然腐化，
所以上游用**代数计数器**动态发现：

- 匹配 `^latest-(\d+)-nixos-(unstable|\d+\.\d+)$`，**generation 数字最大的就是最新**
- flake 索引同源发现（`^latest-(\d+)-group-manual$`），因为旧 generation 会被退休
- **fallback 结果永不缓存**——退休 alias 会 404，所以只覆盖单次上游抖动
- 空 alias（Hydra 先建 alias 再填数据）的结论 **5 分钟后过期**，避免进程钉在旧 generation

**对你的意义**：`action=channels` 里看到 `WARNING: Using fallback channels` 说明发现失败了，
结果可能不是最新，**别把那一轮的 commit 当成权威**。

## revision 的两种来源（重要）

`action=channels` 输出里：

| 标签 | 含义 | 能拿来干什么 |
|---|---|---|
| `Revision (indexed)` | **搜索索引就是从这**个 commit 构建的 | ✅ **可以安全地与 `nix_versions` 对比** |
| `Branch HEAD` | 上游分支当前 HEAD（GitHub best-effort 抓取，进程内缓存 10 分钟） | ⚠️ 只是指针，**可能领先索引几个 commit**，或几分钟陈旧 |

**别把 `Branch HEAD` 当成"这个 channel 的数据版本"** —— 它只是分支尖。

## 本地访问的两个 action（不需要网络）

| action | 需要 Nix | 能力 |
|---|---|---|
| `store` | ❌ | `ls` / `read` 任意 `/nix/store/` 路径。**这是唯一"不需要装 Nix 就能读本机 store"的路径** |
| `flake-inputs` | ✅ | `list` / `ls` / `read` flake inputs（用 `nix flake archive --json` 发现） |

两者的共同安全边界：**路径必须落在 `/nix/store/` 内**（`realpath` 后判前缀，能挡 `..` 与符号链接），
二进制文件与 >1 MB 的文件被拒。

## 缓存总览

- **没有持久化缓存、没有数据库。** 全部是进程内。
- 目录型 source（home-manager / darwin / nixvim / nvf / noogle / nix-dev）**首次加载后常驻内存**。
- channel 解析有自己的 TTL 与冷却（30 s 失败冷却 / 300 s rollover 重检）。
- GitHub 分支 HEAD 查询有 10 分钟进程内 TTL。
- **服务器重启 = 缓存全清。**
