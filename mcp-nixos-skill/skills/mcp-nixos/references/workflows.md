# mcp-nixos 工作流

来源：`mcp_nixos/server.py` 的 `_SERVER_INSTRUCTIONS` + 工具 docstring、`.claude/commands/test-tools.md`、`.claude/commands/release.md`、AGENTS.md（v3.1.0，2026-10-14 提炼）。

## 工作流 A：查询路由（把用户意图映射成一次调用）

上游把这段做成 server-level `instructions`（经 MCP InitializeResult 下发给客户端）+ `nix` 工具 docstring 里的 INTENTS → CALLS 配方，**原样复制调用形状**，不要改写参数名：

```
"is package X in channel Y?"         → nix {"action":"info","query":"X","channel":"Y"}
"search for package X"               → nix {"action":"search","query":"X"}
"which channels are available?"      → nix {"action":"channels"}
"which commit did channel X index?"  → nix {"action":"channels"}   # 看 Revision (indexed) 标签
"search NixOS options for X"         → nix {"action":"search","query":"X","type":"options"}
"get option details for X"           → nix {"action":"info","query":"X","type":"option"}
"home-manager option for X"          → nix {"action":"search","query":"X","source":"home-manager"}
"darwin option for X"                → nix {"action":"search","query":"X","source":"darwin"}
"nixvim option for X"                → nix {"action":"search","query":"X","source":"nixvim"}
"NVF option for X"                   → nix {"action":"search","query":"X","source":"nvf"}
"what programs does pkg X provide?"  → nix {"action":"search","query":"X","type":"programs"}
"count packages/options"             → nix {"action":"stats"}
"browse hm option tree under P"      → nix {"action":"browse","query":"P","source":"home-manager"}
"does X have a binary cache?"        → nix {"action":"cache","query":"X"}
"search the NixOS wiki for X"        → nix {"action":"search","query":"X","source":"wiki"}
"search nix.dev docs"                → nix {"action":"search","query":"X","source":"nix-dev"}
"read a nix.dev page"                → nix {"action":"info","query":"tutorials/nix-language","source":"nix-dev"}
"list inputs of current flake"       → nix {"action":"flake-inputs"}
"ls inside flake input X"            → nix {"action":"flake-inputs","type":"ls","query":"X"}
"read /nix/store/... file"           → nix {"action":"store","type":"read","query":"/nix/store/..."}
"ls /nix/store/... dir"              → nix {"action":"store","type":"ls","query":"/nix/store/..."}
"which commit shipped X version Y?"  → nix_versions {"package":"X","version":"Y"}
```

触发条件（server instructions 原文口径）：任何涉及 nixpkgs 包、NixOS/home-manager/nix-darwin/nixvim/NVF 选项、flakes、FlakeHub、channel、二进制缓存、store 路径、NixOS wiki、nix.dev、Noogle 的提问——**即使你认为自己知道答案也要用**，训练数据比 nixpkgs 落后数月。优先于 `nix search`、手爬 search.nixos.org、`gh api` 查 NixOS/nixpkgs。

优先级规则：版本历史类问题（哪个 commit 含某版本）走 `nix_versions`，不要用 `nix`。

## 工作流 B：/test-tools 八组并行验收

上游 `.claude/commands/test-tools.md` 定义的 QA 工作流。**必须并行派发 8 个子代理，每组跑完全部用例，禁止跳过**，最后汇总一张表。

| 组 | 覆盖 | 关键用例（节选） |
|---|---|---|
| 1 | 核心 NixOS | search packages/options/programs/flakes、`channel=stable`、不存在的包（期望 "No packages found"）；**带点属性路径**（`kdePackages.qt6ct`、`python314Packages.matplotlib`、`rocmPackages.clang`、`llvmPackages_22.systemLibcxxClang`，issue #118 回归）；info package/option、不存在（NOT_FOUND）；stats；channels |
| 2 | Home Manager & Darwin | search git（期望 `programs.git.*` 排最前，issue #190 排序回归）、精确名 `programs.git.enable` 排第一；info；stats（HM 总选项 > 5,000）；options/browse；darwin `dock`→`system.defaults.dock.*` 排最前 |
| 3 | Flakes & FlakeHub | flakes search/stats；flakes info 期望报错（"flakes don't support info"）；flakehub search/info/stats；flake-inputs list/ls/read（需 Nix）、错误路径（缺 query、缺文件路径、不存在 input → NOT_FOUND） |
| 4 | Nixvim / NVF / Wiki | nixvim search/info/stats/browse；NVF 规范路径 `vim.*` 与包装路径 `programs.nvf.settings.vim.*` 均可查、归一化提示；NVF stats 期望 "Documentation track: unstable" 且 > 2,000；wiki search（含不存在项）/info/错误路径（stats/browse 不支持） |
| 5 | Noogle | search（mapAttrs/concatStrings/filter/hasAttr/builtins.map/mkDerivation…）；info 含**别名查找**（`builtins.mapAttrs`、`lib.mapAttrs`）；stats；options 列类目；空 query 报错 |
| 6 | nix-dev & NixHub | nix-dev search（多关键词、不存在项）；info 期望 NOT_FOUND（`nix.dev page not found: test`）；stats/options 不支持；nixhub search/info（ripgrep 期望 license/homepage/programs/store paths）/错误路径 |
| 7 | cache action | 基础（hello/ripgrep/firefox/python/nodejs）；version 指定（`latest`/`3.12.0`/`20.0.0`）；system 指定（四种平台 + `invalid-system` 期望 NOT_FOUND）；组合；空 query 报错；**输出校验**：Store path / Status CACHED / Download size / Unpacked size / Compression |
| 8 | nix_versions | 基础（python/nodejs/ripgrep/git/hello limit=3）；指定版本；不存在（NOT_FOUND）；**输出校验**：包名/license/homepage/programs/总版本数/逐版本号/更新日期/平台摘要/commit hash；平台摘要期望 "Platforms: Linux and macOS" 之类 |

子代理输出格式（强制）：`## [组名] Test Results` → Summary（Total/Passed/Failed）→ 明细表 `| # | Test | Expected | Actual | Status |` → Failed Tests Detail。

最终汇总格式（强制）：`# MCP NixOS Tools Test Report` → 八组通过率表 → Failed Tests 表 → Issues Discovered（Critical/High/Medium/Low）→ Recommendations。收尾核对：8 组全部并行发起、每组全用例、格式合规、失败项有期望 vs 实际。

## 工作流 C：/release 发布（Release Please 自动化）

正常路径禁止手改版本、手建 tag、手建 GitHub Release。

1. **Review release PR**：
   ```bash
   gh pr list --search 'release: in:title is:open' --json number,title,url,headRefName
   gh pr view <PR_NUMBER> --json files,commits,reviews,statusCheckRollup
   git log "$(git describe --tags --abbrev=0)..origin/main" --oneline
   ```
   确认：SemVer 升级与改动匹配；`RELEASE_NOTES.md` 完整且标注 breaking；`pyproject.toml` 与 `.release-please-manifest.json` 版本一致；CI 绿。
2. **合并**：`gh pr merge <PR_NUMBER> --squash --delete-branch`（squash 信息 `release: vX.Y.Z`）。Release Please 拥有 tag 与 GitHub Release；其 `release.published` 事件触发 Publish Package 工作流，负责 PyPI / Docker Hub / GHCR / FlakeHub 全量发布。
3. **盯发布**：`gh run list --workflow release-please.yml --limit 3` + `gh run watch <RUN_ID>`；失败时只对**不可变 tag** 重跑恢复工作流：`gh workflow run publish.yml -f tag=vX.Y.Z -f docker_only=true` / `gh workflow run deploy-flakehub.yml -f tag=vX.Y.Z`。PyPI 上传失败必须在原 run 的失败 job 重试（确认无部分版本存在后）。
4. **独立验证每个公开注册表**（绿 workflow ≠ 传播成功）：
   ```bash
   VERSION=X.Y.Z
   gh release view "v$VERSION" --json tagName,isDraft,isPrerelease,publishedAt,url,targetCommitish
   curl --fail --silent "https://pypi.org/pypi/mcp-nixos/$VERSION/json" | jq -r .info.version
   uvx "mcp-nixos@$VERSION" --help
   docker buildx imagetools inspect "utensils/mcp-nixos:$VERSION"
   docker buildx imagetools inspect "ghcr.io/utensils/mcp-nixos:$VERSION"
   curl --fail --silent https://api.flakehub.com/f/utensils/mcp-nixos | jq -r .version
   nix flake metadata "https://flakehub.com/f/utensils/mcp-nixos/$VERSION"
   ```
   验证点：tag 指向 release PR 合并 commit；PyPI 版本精确匹配；两个容器 manifest 含 `linux/amd64` + `linux/arm64` 且能启动；FlakeHub 版本精确匹配。

版本规则：`fix:`→patch、`feat:`→minor、`!` 或 `BREAKING CHANGE:`→major；`ci:/docs:/test:/refactor:/build:/chore:` 不触发发布。

Guardrails：tag 与包版本视为不可变（不删除、不改指向修复）；不在脏工作树/未合并分支发布；release PR 笔记不全或版本不匹配不合并。

## 工作流 D：日常开发

```bash
nix develop   # 进 dev shell（自动激活 venv，提供菜单命令）
run           # 启动 MCP server
run-tests     # 跑全部测试（CI 带 coverage）
lint          # ruff check
format        # ruff format
typecheck     # mypy
build         # 构建包/发行物
```

无 Nix 的 Python-only 路径：

```bash
uv pip install -e ".[dev]"
uv run mcp-nixos          # 或 python -m mcp_nixos.server
pytest tests/test_server.py -v
```
