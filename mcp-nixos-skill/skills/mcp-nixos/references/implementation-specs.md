# mcp-nixos 实现规范

来源：AGENTS.md + .github/copilot-instructions.md + pyproject.toml + server.py（v3.1.0，2026-10-14 提炼）。改造或仿写一个同类 MCP server 时逐条对照。

## 1. 架构规范

- FastMCP 4.x（MCP SDK 2.x，协议修订版 2026-07-28），Python 3.11+，全 async。
- 模块划分：`server.py`（工具与路由）/ `sources/`（一个数据源一个模块）/ `config.py`（常量）/ `caches.py`（进程内缓存）/ `utils.py`（HTML 解析、格式化、文件 I/O）。
- **只暴露 2 个工具**（v1.0 的 17 个合并而来）：`nix` 统一查询 + `nix_versions` 版本历史。合计约 1,030 tokens。上下文预算优先。
- 所有阻塞 HTTP / 文件 I/O 包 `asyncio.to_thread()`，不阻塞事件循环。
- 无持久缓存、无数据库；目录类 source（Home Manager、darwin、Nixvim、NVF、Noogle、nix.dev）在进程生命周期内内存缓存，其余实时查 API。

## 2. 输出规范

1. **所有工具响应是 plain text**，禁裸 JSON/XML 泄漏。结构化数据用人类可读排版（`Package: x\nVersion: y`）。
2. 测试必须断言纯文本输出。

```python
# ✅ 正确
return f"Package: {name}\nVersion: {version}\nDescription: {desc}"
# ❌ 错误
return json.dumps({"name": name, "version": version})
```

## 3. 错误规范

- 统一 `error()` helper：`return error("Query required for search", "INVALID_INPUT")`。
- 错误信息 plain text、人类可读、可操作，附可复制的 JSON 示例。
- API 失败优雅降级，不把异常抛给客户端。

## 4. Channel 解析规范

- 启动时经 ES `_cat/aliases` 动态发现全部 `latest-<gen>-nixos-<channel>` 别名。
- 每 channel 取最高 generation（unstable 永远解析到最新索引，滚动切换也不漂移）。
- `stable` 永远映射当前 stable 版本；`FALLBACK_CHANNELS` 兜底（发现失败时）。
- `ELASTICSEARCH_URL` 环境变量可覆盖后端做本地测试。
- channels 输出的 commit 标签：索引 commit 标 `Revision (indexed): <sha>`（可与 nix_versions 对比）；GitHub 分支尖端标 `Branch HEAD: <sha> (upstream; may be ahead of indexed data)`，每分支缓存 10 分钟，非 JSON 200 响应时回落旧缓存值。

## 5. NVF 路径归一化规范

- 唯一规范名 `vim.*`；`programs.nvf.vim.*`（简写）与 `programs.nvf.settings.vim.*`（NixOS/Home Manager 模块路径）在 search/info/browse 前统一归一化。
- info 对包装路径返回时显示规范名（如 `NVF Option: vim.languages.nix.enable`）+ Documentation 链接。

## 6. limit 规范

| 场景 | 范围 |
|---|---|
| `flake-inputs` read | 1–2000 |
| `store` read | 1–2000 |
| 其余全部 action | 1–100 |

## 7. 安全规范

- flake-inputs / store 路径必须校验位于 `/nix/store/` 内（参考 `_validate_store_path()`），越界拒绝。
- GitHub API 调用带 `User-Agent: mcp-nixos/<version>`（可追溯 + 限流诊断）。

## 8. 测试规范

- pytest + pytest-asyncio（auto 模式，function-scoped event loop），async 测试是标准写法。
- 标记 `@pytest.mark.unit` 或 `@pytest.mark.integration`；integration 打真实 API（禁 mock）。
- 默认开 coverage（`--cov=mcp_nixos`）；网络抖动用例 `@pytest.mark.flaky(reruns=3)`。
- 测试断言纯文本输出；另测 instructions 存在性与 JSON 调用形状一致性。

## 9. 代码风格规范

- ruff：行宽 120，target py311，规则集 E/W/F/I/B/C4/UP，ignore E402/E203。
- mypy strict（tests 与 fastmcp 豁免）。
- snake_case 函数/变量、PascalCase 类、测试文件 `test_*.py`。
- **禁止跳过 lint**：不得 `# noqa` / `# type: ignore` / `# pylint: disable`；规则真有问题就改 `pyproject.toml` 配置。
- 提交信息 `type: summary`（feat/fix/docs/refactor/test/chore…）。

## 10. 已知坑与反直觉（按 issue 编号）

1. **#125**：action 名 `options` 让模型混淆 → 改名 `browse`，`options` 仅作静默别名。
2. **#118**：带点/命名空间的属性路径（`kdePackages.qt6ct` 等）曾搜不到 → 已有回归测试。
3. **#146**：`action=info` 对 pname 粘连（firefox/firefox-esr/firefox-mobile）曾非确定性返回 → 现在「属性路径优先 > pname 精确 > 规范属性（attr==pname）> 属性名排序」，并显式提示消歧。
4. **#190**：选项搜索排序曾让 `*.enableGitIntegration` 之类子串匹配压过精确前缀 → 精确匹配优先。
5. **#159**：channel 曾 memoize 陈旧 fallback → 动态发现 + 取最高 generation。
6. **#213**：首次 HTML 目录加载需串行化（并发首查会互相踩）。
7. **Nix 侧**：包自带 FastMCP 4 / MCP SDK 2 栈（含 ≥1.0.1 的 starlette 安全底线），即使 nixpkgs 还ship FastMCP 3 也不污染全局 Python 包集；要全局升级再叠加 `mcp-nixos.overlays.fastmcp4`。
8. **3.0.0 breaking**：移除 Intel macOS（x86_64-darwin）flake 输出（坏的传递依赖挡了 FlakeHub 发布）；Apple Silicon 与 Linux 保留。

## 11. 打包与分发要点

- nixpkgs 已有 `pkgs.mcp-nixos`（unstable）；flake 提供 `overlays.default`（仅加 `pkgs.mcp-nixos`）。
- 分发矩阵：PyPI、Docker Hub `utensils/mcp-nixos`、GHCR `ghcr.io/utensils/mcp-nixos`（均 amd64+arm64）、FlakeHub。
- HTTP 部署：`MCP_NIXOS_TRANSPORT=http` + `MCP_NIXOS_HOST/PORT/PATH`，`MCP_NIXOS_STATELESS_HTTP=1` 关会话状态。
- Pi Coding Agent 不原生讲 MCP：推荐 `pi-mcp-adapter`（`lifecycle: "lazy"`），或仓库内 `.pi/extensions/mcp-nixos.ts` 项目级扩展（直接 import `mcp_nixos.server` 调工具函数）。
