---
type: Checklist
---

# 用 Hermes Agent / OpenClaw 做 Arch Linux 运维：MCP / Skills / 软件方案全清单

> 第三轮专项调研 · 调研日期 **2026-10-12**
> 前两轮：`research_report_hermes_openclaw_linux_ops.md`（通用 + 框架机制）、`research_report_nixos_ai_agent_ecosystem.md`（NixOS）
> 证据分级：**A** = 本机源码/官方仓库 API 直读可复现 · **B** = 项目 README/官方文档原文 · **C** = 项目自述未独立复现 · **D** = 本报告推断

---

## §0 TL;DR

**Arch 的 AI 运维生态形状和 NixOS 完全不同，不要套用 NixOS 的结论。**

| | NixOS | Arch |
|---|---|---|
| 系统模型 | 声明式、可原子回滚 | 命令式、靠快照与降级 |
| 社区对 agent 的关注点 | **沙箱**（别给 agent 真系统） | **供应链审计**（别让 AUR 投毒） |
| 最活跃的一层 | 沙箱层 | AUR 安全审计层 |
| 知识层 | `mcp-nixos` 等第三方 | `arch-mcp` + `arch-wiki-mcp` + **官方仓库离线 Wiki 包** |
| 专属 agent skill | `nixos-management-skill` 等 | `herraiz-org/ai-skills`、`enihcam/aur-skills` |
| 官方发行版背书 | 有官方 NixOS module | 无，但官方仓库直接提供运维基座包 |
| 社区情绪 | 怀疑 + 工程化 | 怀疑 + **明显的反 AI slop** |

**Arch 侧最小可行栈**（全部已核验存在）：

1. **MCP**：`arch-mcp`（= PyPI 包 `arch-ops-server`，59★，2026-03 仍在提交）+ `arch-wiki-mcp`（1★，但"反幻觉"设计最贴合运维）
2. **Skills**：`herraiz-org/ai-skills`（Apache-2.0，带 CI + pytest，两个技能覆盖"更新系统"与"装 AUR 包"）
3. **知识库**：**不要上 MCP**。官方仓库直接有 `arch-wiki-lite`（Arch Wiki 去 HTML 版，体积 1/9，console 可搜）+ `llm-wiki` 沉淀本机经验
4. **安全闸门**：`informant`（官方仓库，pacman hook 形式的 Arch News 阅读器）+ `checkupdates`（`pacman-contrib`）+ 自建 PKGBUILD 静态扫描

**Arch 的真实风险不是"agent 权限太大"，是"agent 帮你装了一个被投毒的 AUR 包"。** r/archlinux 正在处理一轮 200+ 恶意 AUR 包收养事件，攻击手法是"孤儿包被恶意者收养 + AUR git commit author 可冒充"。

**社区规范已成型：Arch Wiki 优先，AI 其次。** r/archlinux 原帖里被顶得最高的建议是"想消除幻觉就从 Arch Wiki 开始"；有用户明确给 Claude Code 定了"必须从 wiki.archlinux.org 取引用"的硬规则。

---

## §1 两个 Arch MCP（均已核验，B/A 级）

### 1.1 `arch-mcp` / `arch-ops-server` — 事实上的 Arch 运维 MCP

| 项 | 值 |
|---|---|
| 仓库 | `github.com/nihalxkumar/arch-mcp` |
| **PyPI 包名** | **`arch-ops-server`**（注意：仓库名 ≠ 包名） |
| 当前版本 | **3.4.0** |
| Stars / Forks | 59 / 15 |
| 许可 | **双许可 GPL-3.0-only OR MIT**（可自选） |
| 语言 / 依赖 | Python **≥ 3.11** |
| 创建 / 最后提交 | 2025-10-23 / **2026-03-10**（活跃） |
| 安装 | `uvx arch-ops-server` |
| 定位 | 非官方社区项目，**明确声明与 Arch Linux 无隶属关系** |
| 文档 | `nxk.mintlify.app/arch-mcp` |

**Resources（URI 式只读访问）** — 这是它最被低估的部分，不消耗 tool 名额：

| URI | 返回 |
|---|---|
| `archwiki://Installation_guide` | Markdown 化 Wiki 页 |
| `archrepo://vim` | 官方仓库包详情 |
| `aur://yay/info` · `aur://yay/pkgbuild` | AUR 元数据 / **带安全分析的 PKGBUILD 原文** |
| `pacman://installed` · `orphans` · `explicit` · `groups` · `group/base-devel` · `database/freshness` | 本机包状态 |
| `pacman://log/recent` · `log/failed` | 包事务日志 |
| `system://info` · `disk` · `services/failed` · `logs/boot` | 系统状态 |
| `archnews://latest` · `critical` · `since-update` | Arch News（**含"需要人工干预"的 critical 项**） |
| `config://pacman` · `config://makepkg` | 配置解析 |
| `mirrors://active` · `mirrors://health` | 镜像站状态 |

**Tools**（14 个，**注意含写操作**）：

| 类别 | 工具 |
|---|---|
| 查询 | `search_archwiki`、`search_aur`、`get_official_package_info` |
| 更新 | `check_updates_dry_run`、`check_database_freshness`、`fetch_news` |
| **写操作 ⚠️** | `install_package_secure`、`remove_packages`、`manage_orphans`、`manage_install_reason`、`optimize_mirrors` |
| 分析 | `audit_package_security`（含 `pkgbuild_analysis` / `metadata_risk` 两个 action）、`analyze_pkgbuild_safety`（**50+ 红旗**）、`analyze_package_metadata_risk` |
| 诊断 | `diagnose_system`、`query_package_history`、`run_system_health_check` |
| 配置 | `analyze_pacman_conf`、`analyze_makepkg_conf`、`verify_package_integrity` |

**Prompts（引导式工作流，4 个）**：`troubleshoot_issue`、`audit_aur_package`、`analyze_dependencies`、`safe_system_update`。

**配置（Claude / Cursor / 任何 STDIO 客户端）**：

```json
{
  "mcpServers": {
    "arch-linux": {
      "command": "uvx",
      "args": ["arch-ops-server"]
    }
  }
}
```

> ⚠️ **它有写操作，不要默认信任。** 在 Hermes 里必须 `trust: untrusted` + `tools.include` 白名单，把 `install_package_secure` / `remove_packages` / `manage_orphans` / `optimize_mirrors` 排除在自动执行之外。详见 §8.3。

**已知文档瑕疵（本报告核实，A 级）**：`herraiz-org/ai-skills` 的 `references/arch-mcp.md` 把 server 链接写成 `github.com/iht/arch-mcp`。经 GitHub API 核验，`iht/arch-mcp` 是 2026-08-08 创建的 **fork**（0★，当日即停更），上游是 `nihalxkumar/arch-mcp`。**工具名本身与上游一致**（已在 `src/arch_ops_server/tool_metadata.py` 中逐字确认 `fetch_news` / `audit_package_security` / `diagnose_system` / `query_package_history` / `run_system_health_check` / `check_database_freshness` 均存在），所以该 skill 可直接用，只需把链接改成上游。

### 1.2 `arch-wiki-mcp` — "让 AI 无法在 Arch Wiki 上撒谎"的引用引擎

| 项 | 值 |
|---|---|
| 仓库 | `github.com/egarcia74/arch-wiki-mcp` |
| PyPI | `arch-wiki-mcp`，当前 **2.1.0** |
| Stars | **1**（采用度极低，注意） |
| 许可 | MIT |
| 创建 / 最后提交 | 2026-01-10 / 2026-07-15 |
| 安装 | `pipx install arch-wiki-mcp`（Arch: `pacman -S python-pipx`） |
| 依赖 | **零依赖**，default branch 是 `master` 不是 `main` |

**设计主张（原文）**：

> "This is not 'AI that knows Linux.' This is Linux that won't let AI lie about it."
> "**citability engine**" / "**truth perimeter**" / **fail-closed**

机制：每个可引用的片段都带 **SHA-256 指纹 + 钉到具体 revision 的 URL**（`revid`）。AI 若编造，就必须**可见地**编造——拿不出能校验通过的引用。

**三档证据分层（这是它的核心设计，值得抄）**：

| 档位 | 工具 | 是否带 revid | 是否带 hash | 语义 |
|---|---|---|---|---|
| 证据 | `page`、`section`、`commands`、`warnings` | ✅ | ✅ | 可引用、可复算 |
| 半证据 | `links` | ✅ | ❌ | 是目标，不是引文 |
| 指针 | `search`、`sections` | ❌ | ❌ | **拒绝伪装成证据** |

> **"There is deliberately no tool that infers commands from prose."** —— 刻意不提供"从散文里推断命令"的工具。

`commands` 返回结构（节选）：

```json
{
  "content": "# grub-install --target=x86_64-efi --efi-directory=<esp> --bootloader-id=GRUB",
  "content_raw": "# grub-install --target=x86_64-efi --efi-directory=''esp'' --bootloader-id=GRUB",
  "content_hash": "8b8dfad439a8fb73f328ec9c2da75cf575e7a24ad945d3890ddc626f180b7a44",
  "placeholders": ["esp"],
  "revision_url": "https://wiki.archlinux.org/index.php?oldid=858930#Installation",
  "revid": 858930
}
```

注意 `content` 里 `<esp>` **故意保留尖括号**——"so a thoughtless paste fails at the shell instead of acting on the wrong path"（无脑粘贴会在 shell 报错，而不是作用到错误路径）。这个设计细节值得放进任何运维 skill 的规范里。

**它为什么值得装（尽管只有 1★）**：它精确对上了 §6 里 r/archlinux 的社区规范——"先查 Wiki"。它把"查 Wiki"从一句提示词变成了**结构性约束**。

---

## §2 Arch 专属 Agent Skills（三个真实仓库，均已核验）

### 2.1 `herraiz-org/ai-skills` ⭐ 质量最高，建议直接抄结构

| 项 | 值 |
|---|---|
| Stars | 0（但工程质量远超 star 数） |
| 许可 | **Apache-2.0** |
| 创建 / 最后提交 | 2026-08-08 / 2026-09-05 |
| 亮点 | **带 CI + pytest 测试套件**（`tests/update_arch_system/test_scan_aur_recipe.py` 等） |

**两个技能**：

| 技能 | 体积 | 作用 |
|---|---|---|
| `skills/update-arch-system` | 10.8 KB | 安全地全量更新 Arch（官方仓库 + AUR） |
| `skills/install-aur-package` | 12.6 KB | 安全地安装单个 AUR 包 |

**`update-arch-system` 的六道闸门（这是整轮调研里最有价值的流程资产）**：

1. **Preconditions** — `test -r /etc/arch-release`；`command -v pacman yay git curl`
   - 硬规则：**永不 `pacman -Sy`**、**永不部分升级**、**永不关签名校验**、**永不改 pacman 信任设置**
2. **checkupdates 引导** — 从 `pacman-contrib` 装（**绝不允许从 AUR 满足此依赖**）；先查 `check_database_freshness` 判断数据库是否已超前于已装包 → 决定"立即装"还是"并入全量升级"（避免部分升级）
3. **Arch News 闸门（阻塞式）** — `fetch_news(action='critical')` + `fetch_news(action='since_update')`；无 MCP 时 `curl https://archlinux.org/feeds/news/` 并读 `/var/log/pacman.log` 里最后一次 `pacman -Syu` 之后的全部条目
   - 诚实边界：**RSS 只有约 10 条**。若上次全量升级早于最旧条目 → 必须**报告这个盲区**，而不是当作"没有新闻"
   - 命中待升级包 → **停下要人工批准**
4. **Discover** — `checkupdates`（免 sudo）；AUR 用 `yay -Qua`（两条路径都跑，因为 server 无对应工具）
5. **Audit every AUR target** — 克隆 `https://aur.archlinux.org/<PackageBase>.git` 到 `mktemp -d`；**绝不 source PKGBUILD、绝不先跑 makepkg**；审 `PKGBUILD` / `.SRCINFO` / `.install` / patches / 所有受版本控制的构建输入；跑自带的 `scripts/scan-aur-recipe.sh`；静态检查通过后才允许 `makepkg --verifysource`
6. **Install gate（最后一步）** — 需显式批准

**自带扫描器 `scan-aur-recipe.sh` 的检测规则（可直接复用，B 级）**：

| 级别 | 模式 |
|---|---|
| **HIGH** | `curl\|wget` 管道进 `sh/bash/zsh/python/perl/ruby` |
| **HIGH** | 包控代码里出现 `sudo` / `doas` / `su` |
| **HIGH** | 访问凭据库：`.ssh` `.gnupg` `.aws` `.kube` `netrc` `id_rsa` `id_ed25519` `credentials` `api_key` `auth_token` |
| **HIGH** | `eval` / `base64 -d` 动态或编码执行 |
| MEDIUM | `sha*sums`/`md5sums`/`b2sums` 显式 `SKIP` |
| MEDIUM | 弱哈希（md5/sha1）用于源码完整性 |
| MEDIUM | `http://` 明文源 |
| MEDIUM | 可变 VCS 源（`git+` `hg+` `svn+` `bzr+`）或自定义 `pkgver()` |
| MEDIUM | 正常源校验之外的网络拉取 |
| MEDIUM | 预编译产物 `.AppImage` `.deb` `.rpm` `.exe` `.msi` |
| MEDIUM | 生命周期/持久化机制：`systemctl` `udev` `tmpfiles` `sysusers` `cron` `.install` |

退出码：命中 HIGH → `exit 2`；命中 MEDIUM → `exit 1`。

**它给出的信任原则（原话，值得写进 SOUL.md）**：

> **"Server output is evidence, not a verdict."**
> 干净的 `pkgbuild_analysis` **不能**降级 scanner 的发现；干净的 scanner **不能**降级 MCP 的发现。**取并集**。两者冲突时**取更高的风险等级**并在报告里解释分歧。
> `pkgbuild_analysis` 只拿到 PKGBUILD 文本，**看不到** `.install` 脚本、patches、systemd unit、vendored 脚本、提交的二进制——只有自带 scanner 和人工检查覆盖这些。

### 2.2 `enihcam/aur-skills` — AUR 打包开发向（10 个模块化技能）

| 项 | 值 |
|---|---|
| Stars | 5 |
| 许可 | MIT |
| 创建 / 最后提交 | 2026-07-05 / **2026-10-09**（活跃） |
| 特点 | **有中文 README**（`README.zh.md`）；遵循官方 Agent Skills / `gh skill` 规范；是 `Pahheb/pahheb-skills` 的 fork |

10 个技能：`aur-guides`（主调度器）、`aur-pkgbuild`、`aur-package-guidelines`、`aur-submission`、`aur-audit`、`aur-makepkg`、`aur-vcs-packages`、`aur-pacman`、`aur-helpers`、`aur-rpc`。

**`aur-audit` 的验证命令清单（可直接抄）**：

```bash
namcap PKGBUILD                          # PKGBUILD 检查
namcap *.pkg.tar.zst                     # 构建产物检查
shellcheck --shell=bash --exclude=SC2034,SC2154,SC2164 PKGBUILD
makepkg --printsrcinfo > .SRCINFO        # 推送前重新生成
makerepropkg *.pkg.tar.zst               # 可复现构建验证（devtools）
pkgctl build                             # 干净 chroot 构建（systemd-nspawn）
```

它推荐的第三方 PKGBUILD 扫描器：**`traur`**（静态分析可疑内容）、**`ks-aur-scanner`**（KDE 集成）。原文提醒：**"These are aids, not substitutes for manual review."** 以及 **"signed code can still be malicious — review the content, not just the signature."**

**安装路径表（跨 agent 通用，A 级，来自该仓库 README）**：

| Agent | 技能目录 |
|---|---|
| **Hermes** | `~/.hermes/skills/` |
| Claude Code | `~/.claude/skills/` |
| OpenCode | `~/.config/opencode/skills/` |
| Gemini CLI | `~/.gemini/skills/` |
| Codex CLI | `~/.agents/skills/` |
| Cursor | `~/.cursor/skills/` |
| Windsurf | `~/.codeium/windsurf/skills/` |

> ⚠️ 该 README 自己提醒：**不要把克隆目录放 `/tmp`**（很多系统把 `/tmp` 挂成 tmpfs，重启即清）。用 `~/.local/share/aur-skills` 再 symlink。

### 2.3 `IPauloGermano/arch-agent-skill` — 桌面环境向（不是运维向）

Stars 0，MIT，2026-08-31 创建。覆盖 Hyprland / Sway / i3 / KDE Plasma / GNOME / Niri / Waybar / 主题 / 截屏 / hooks 的 `references/` 分层文档。**如果你要管的是桌面配置而非系统运维，这个比前两个更对口。**

---

## §3 官方仓库自带的 Arch 运维基座 ⭐（本轮最有价值的发现）

**Arch 的知识库和更新安全闸门不需要第三方，官方 `extra` 仓库直接提供。** 全部经 `archlinux.org/packages/search/json/` 核验（A 级）：

| 包 | 仓库 | 版本（核验日） | 作用 |
|---|---|---|---|
| **`arch-wiki-lite`** | `extra/any` | `20261003-1` | **Arch Wiki 去 HTML 版，体积 1/9，console 可搜可读** |
| `arch-wiki-docs` | `extra/any` | `20261003-1` | Arch Wiki 离线浏览优化版 |
| **`informant`** | `extra/any` | `0.6.0-2` | **Arch News 阅读器 + pacman hook**（更新前强制读新闻） |
| `arch-audit` | `extra/x86_64` | `0.2.0-5` | 基于 Arch Security Team 数据的 CVE 审计（类似 `pkg-audit`） |
| `pacman-contrib` | `extra/x86_64` | `1.13.1-1` | 提供 `checkupdates`（免 sudo 查更新） |
| `downgrade` | **AUR** | 910 票 / pop 7.95 | 从缓存或 Arch Linux Archive 降级包 |
| `paru` | **AUR** | 1260 票 / pop 19.83 | 功能最全的 AUR helper |

**结论：Arch 的知识库方案不需要 MCP，也不需要 RAG。**

```
pacman -S arch-wiki-lite informant arch-audit pacman-contrib
# arch-wiki-lite → 本地全文可 grep 的 Wiki  → 喂给 llm-wiki 的 raw/
# informant      → 更新前自动拦下让你读新闻 → 天然的安全闸门
# arch-audit     → CVE 扫描                 → 可做定期自动巡检
```

`arch-wiki-lite` 尤其关键：它把"让 agent 有 Arch Wiki 可查"这件事从"依赖第三方 MCP 联网"降级成"本地一个包"。**离线、确定、无网络依赖、不会被投毒。**

---

## §4 AUR 供应链安全 —— Arch 真正的风险面（A/B 级）

### 4.1 事件：200+ 恶意 AUR 包收养（r/archlinux `1vaxtcs`）

**原帖标题**："Another wave - 200+ malicous AUR packages adoptions that are overwhelming my scanner. Be 100% careful when trying to update AUR packages now."

**攻击手法（原帖原文）**：

> "Same old way, **the maintainer got pwned, or orphaned packages are adopted by the bad actor**. **AUR's git commit author is easily impersonated** so you can see the commit comes from the same person, but in fact it's not. Stay safe. The malicious packages are **info stealers**."

三个关键点：

1. **维护者账号被攻陷**，或**孤儿包被恶意者收养**（AUR 允许任何人收养 orphan）
2. **git commit author 可冒充** —— 所以"提交者看起来还是原作者"**不构成证据**
3. 载荷是**信息窃取器**（info stealer）

**已知受害者包名（部分，来自原帖）**：`1panel`、`1panel-git`、`archutil`、`cinnamon-no-nemo`、`icloudpd`、`stirling-pdf-desktop-bin`、`windscribe-cli-v2-bin`、`pandoc-eisvogel-template`、`python-chatterbot`、`instawow-bin`、`pylnker-git`、`wiki-go`、`gitarbor-bin`、`boringssl-git` 等。

**社区给出的检测手段（可直接用）**：

| 手段 | 用法 |
|---|---|
| **aurwatch.org API** | `curl -fsS "https://aurwatch.org/api/v1/check?pkg=$pkg" \| jq -r '.status'` → `clean` / `low` / `medium` / `high` |
| **批量自查脚本**（原帖提供） | `pacman -Qqm \| parallel -j16 check_pkg`（`pacman -Qqm` = 仅列出外来/AUR 包） |
| **aur-audit.wtako.net** | `curl 'https://aur-audit.wtako.net/packages?filter=red&limit=200'` 取红色标记包清单 |
| **恶意样本哈希** | dropper `e73a35b3e75e94746428d1a207703d6335933deadee7d1d9c9d0328df7b9df77` |

**政策层面的讨论**：社区在问"是否应该限制或禁止孤儿包被收养"（"It seems like a pretty basic, effective reform"）。有人主张"根本不该允许改包的推送者，维护者跑路就停止更新，想接手就 fork 成新包名"。

**正确上报渠道**：`aur-general@lists.archlinux.org`（原帖评论区多人纠正：Reddit 不是上报渠道，但作为公众预警是合理的）。

### 4.2 这轮事件的"元教训"：r/archlinux 的反 AI slop 情绪

原帖本身是 AI 生成的（格式混乱、含 emoji、出现未来日期 `20260725`），评论区**大量火力集中在这一点**，而不是恶意包本身：

> **u/LeeHide**："Please just say when you used AI to do all of this, it's very tiring to read through only to realize you have no idea and neither does the AI. … **You're diluting the signal, making it less likely for real issues to be taken seriously.**"
> **u/edparadox**："Could you just go straight to the point instead of that verbose **LLM-generated stupid post**? The worst part is you could have alerted aur-general@lists.archlinux.org directly."
> **u/KaptainSaki**："Wouldn't mind if they banned using AI on this sub"
> **u/Malsententia**（重排了原帖的乱列表）："what's with the emojis, did you run this through chatgpt or some crap?"

**这是运维场景下必须知道的社会约束**：你在 Arch 社区用 AI 生成的报告，**信息是对的也可能被忽视**，因为格式会暴露来源。要报安全事件，**写简洁的事实 + 链接 + 包清单，并直接发 `aur-general@lists.archlinux.org`**。

---

## §5 社区实证：Arch 用户实际怎么用 AI（r/archlinux `1orwi2b`）

原帖："Arch for Beginners with Claude CLI-Code = Very Useful"（作者 `u/MysticFoxPaws`，Arch 用了近一个月）

**作者的实际做法（最有参考价值的一条）**：

> "I still have **strict rules for Claude Code that it should retrieve references specifically via wiki.archlinux.org**, but also document carefully and clearly in **Obsidian**."

即：**硬性要求 agent 从 wiki.archlinux.org 取引用 + 用 Obsidian 沉淀**。这正好是 §1.2 的 `arch-wiki-mcp` 想结构化的那件事。

**社区共识（按被认可程度）**：

| 立场 | 代表原话 |
|---|---|
| 可以用，但必须回查 Wiki | **u/_sLLiK**："if you want to remove the chance of hallucinations, **start with Arch's wiki first. It really is that good.** It's a lot of reading, but it's worth it." |
| 幻觉会把人带进坑 | **u/Sea-Promotion8205**："They can throw a lot of red herrings and lead you down very deep unnecessary rabbit holes, and **their information isn't always actually up to date**." |
| 但会制造"照着 AI 装崩"的求助潮 | **u/aldyr**："many Linux subreddits are full of pleading for help with their Linux install, **that isn't working after they followed some AI generated instructions**. Shortcuts without understanding, and no new skills learnt." |
| 给日志/截图效果更好 | **u/ExplanationMobile399**："give them clear, concise information, **share terminal outputs and screenshots** with it … The more data it has with a current subject, the better it really does get." |
| 非平凡配置必须回查 | **u/archover**："for Arch config, I am very careful, **usually confirming it in the wiki for non trivial stuff**." |

**其它相关帖子（同一搜索簇）**：

- `u/felixbrockm` — i3blocks widget 显示 Claude Code / Codex 的速率限制（说明有人已经在 Arch 桌面里常驻 AI 工具）
- `u/Suspicious-Bee-2638` — "What is everyones opinion on claude coding everything"
- `u/FullWizard` — "It's never been this easy to use Arch"（明确说自己要谈 AI）

---

## §6 技能市场实测：Arch 在市场上几乎不存在（A 级）

| 市场 | 查询 | 结果 |
|---|---|---|
| **clawhub.ai** | `q=arch` | **全部是 architecture（软件架构）技能**，与 Arch Linux 无关。唯一的 Arch Linux 品牌项是 `j3ffyang/arch-sign-off`（往文件末尾追加 `btw, i use arch`，591 安装量）——**是个玩笑技能** |
| **clawhub.ai** | `q=pacman` | **只有 1 个结果且无关**：`chris0x88/pacman-hedera`（Hedera 上的 DeFi 交易 agent） |
| **AUR** | `search/mcp` | 282 个结果，但**热度极低**（榜首 `engram-bin` pop 仅 1.76）。有 `github-mcp-server` / `github-mcp-server-bin`（MIT，维护者 vitaliikuzhdin）、`python-fastmcp`、`serena`、`codebase-memory-mcp-bin`、`ai-memory-bin` 等 |
| **skills.sh** | `q=arch` | JS 渲染，无可用结果（第二轮已实测其榜单前 55 名无任何运维类技能） |

**结论**：**Arch 的 AI 运维能力不在技能市场里，在 GitHub 小仓库 + 官方仓库包里。** 市场搜索会给你一堆架构（architecture）噪音，别浪费时间。

---

## §7 非 AI 的软件方案（同样解决 Arch 更新安全问题）

如果不想让 AI 碰系统，这些工具单独就够用（均核验存在）：

| 工具 | Stars | 许可 | 能力 |
|---|---|---|---|
| **`indyfive11/archward`** | 1 | GPL-3.0 | **快照 · 风险分级 · pacman+AUR · pacnew 策略 · 逐包取消选择 · 粒度+批量回滚 · 自定义 hook · 更新后校验**。CLI + PySide6 GUI。支持 Arch / EndeavourOS / Manjaro / CachyOS / Garuda / Artix（靠 `ID_LIKE`） |
| `codexspidey/archsafe`（原名 `Ayush-sinha44/archsafe`） | 3 | 无 | "CLI safety analysis tool for Arch Linux updates and AUR packages **powered by AI**"。⚠️ **2026-06-24 后无提交，无许可证 → 视为弃坑，不要依赖** |

`archward` 的功能集（快照 + 逐包取消 + 回滚 + pacnew 策略）正好是 NixOS 用声明式天生解决、而 Arch 必须靠工具补上的那块。

---

## §8 推荐栈：Arch 版可直接抄的配置

### 8.1 `SOUL.md` —— Arch 安全底线（追加到你的 persona 文件）

```markdown
## Arch 运维红线（不可协商）

### 更新纪律
- 永不执行 `pacman -Sy`（部分升级是 Arch 最常见的自毁方式）
- 永不执行部分升级；仓库包永远整批升级
- 永不关闭签名校验，永不修改 pacman 信任设置
- 更新前必须先读 Arch News 的 critical 项；命中待升级包则停下报告，等人工决定

### AUR 纪律
- AUR 是用户提交内容，不是受信软件源。装 AUR 包前必须：
  1. 克隆 `https://aur.archlinux.org/<PackageBase>.git` 到 `mktemp -d`
  2. 静态检查 PKGBUILD / .SRCINFO / .install / patches / 所有受版本控制的构建输入
  3. **绝不 source PKGBUILD，绝不先跑 makepkg**
  4. 跑静态扫描；HIGH 级发现直接阻断
  5. 检查该包是否已进入官方仓库（进了就改用官方包）
- "git commit author 看起来是原作者" **不构成任何信任证据**（可冒充）
- 孤儿包被收养 / 维护者变更，一律视为需要重新审计
- 需要 `sudo` 的包控代码 = HIGH 风险

### 输出纪律
- 每个命令引用必须能回溯到 wiki.archlinux.org 的具体 revision
- 不确定时报告不确定，不猜。宁可说"我查不到"也不给可能砖机的命令
- 报告用简洁事实 + 链接 + 包清单，不要生成冗长格式化文本（Arch 社区对 AI slop 容忍度极低）
```

### 8.2 `AGENTS.md` —— 项目级（放在 `~/ops-arch/` 或你的运维仓库根）

```markdown
# Arch 运维项目

## 环境
- 发行版：Arch Linux（滚动）
- AUR helper：paru（或 yay）
- 快照：<你的方案：snapper / timeshift / btrfs subvolume>

## 标准更新流程
1. `informant` 或读 `https://archlinux.org/feeds/news/` → 逐条核对 critical
2. `checkupdates` → 列出官方仓库待更新
3. `yay -Qua` → 列出 AUR 待更新
4. 对每个 AUR 待更新包执行 AUR 审计流程（见 SOUL.md）
5. 快照 → 全量升级 → 更新后校验（`systemctl --failed`、`arch-audit`）
6. 把本次的坑与结论写入 kb/ 知识库

## 知识库
- 离线 Wiki：`/usr/share/doc/arch-wiki-lite/`（来自 arch-wiki-lite 包）
- 本机经验：`~/ops-arch/kb/`（llm-wiki 结构）
- 禁止把 Arch Wiki 内容复制进知识库（体积爆炸）——只存"本机特有的结论与坑"
```

### 8.3 `~/.hermes/config.yaml` —— MCP 配置

```yaml
mcp_servers:
  # ── 只读引用引擎：最安全，建议默认开 ──
  arch-wiki:
    command: "arch-wiki-mcp"          # pipx install arch-wiki-mcp
    lazy: true
    trust: untrusted
    tools:
      include: ["page", "section", "commands", "warnings", "search"]

  # ── Arch 运维：含写操作，必须收窄 ──
  arch-ops:
    command: "uvx"
    args: ["arch-ops-server"]
    lazy: true
    trust: untrusted                  # ⚠️ 有写操作，绝不放行
    tools:
      include:
        # 只读查询
        - "search_archwiki"
        - "search_aur"
        - "get_official_package_info"
        - "check_updates_dry_run"
        - "check_database_freshness"
        - "fetch_news"
        - "audit_package_security"
        - "analyze_pkgbuild_safety"
        - "analyze_package_metadata_risk"
        - "diagnose_system"
        - "query_package_history"
        - "verify_package_integrity"
      exclude:
        # 写操作一律不自动执行（列出来是为了"显式说明为什么没有它们"）
        - "install_package_secure"
        - "remove_packages"
        - "manage_orphans"
        - "manage_install_reason"
        - "optimize_mirrors"

# 危险命令永久白名单：只放只读查询
command_allowlist:
  - "checkupdates"
  - "pacman -Q*"
  - "yay -Qu*"
  - "systemctl --failed"
  - "journalctl -u *"
  - "arch-audit"
  - "df -h"
  # ⚠️ 绝不加入：rm / dd / mkfs / pacman -Syu / pacman -R / yay -S
```

### 8.4 知识库落地（Arch 版）

```bash
# 1) 离线 Wiki 作为只读原始层
sudo pacman -S arch-wiki-lite arch-wiki-docs
ls /usr/share/doc/arch-wiki-lite/          # 确认路径
# 2) 建 llm-wiki 结构，raw/ 软链到离线 Wiki（只读），其余目录让 agent 写
export WIKI_PATH=~/ops-arch/kb
mkdir -p "$WIKI_PATH"/{raw,entities,concepts,comparisons,queries}
ln -sfn /usr/share/doc/arch-wiki-lite "$WIKI_PATH/raw/arch-wiki-offline"
# 3) 装 informant 让更新前强制读新闻
sudo pacman -S informant
informant check
```

### 8.5 装 Arch 专属 skill（三个来源）

```bash
# ① herraiz-org/ai-skills —— 更新系统 + 装 AUR 包（质量最高）
git clone https://github.com/herraiz-org/ai-skills.git ~/.local/share/ai-skills
for s in ~/.local/share/ai-skills/skills/*; do
  ln -sfn "$s" ~/.hermes/skills/"$(basename "$s")"
done

# ② enihcam/aur-skills —— AUR 打包开发（10 个模块）
git clone https://github.com/enihcam/aur-skills.git ~/.local/share/aur-skills
for s in ~/.local/share/aur-skills/skills/*; do
  ln -sfn "$s" ~/.hermes/skills/"$(basename "$s")"
done

# ③ 或走官方 gh skill（需要 gh CLI ≥ 2.90.0）
gh skill install enihcam/aur-skills --all --agent claude-code --scope user
```

### 8.6 AUR 自查（把 §4 的社区脚本固化下来）

```bash
# 一次性检查所有外来（AUR）包的风险等级
check_pkg() {
  local pkg=$1 status
  status=$(curl -fsS "https://aurwatch.org/api/v1/check?pkg=$pkg" | jq -r '.status' 2>/dev/null)
  printf '%-32s %s\n' "$pkg" "${status:-unknown}"
}
export -f check_pkg
pacman -Qqm | xargs -P16 -I{} bash -c 'check_pkg "$@"' _ {}
```

---

## §9 坑与反直觉

1. **`arch-mcp` 的仓库名 ≠ 安装名。** 仓库叫 `nihalxkumar/arch-mcp`，PyPI 包叫 **`arch-ops-server`**，命令是 `uvx arch-ops-server`。搜 "arch-mcp pip install" 会找不到。
2. **`arch-mcp` 有写操作，别当只读用。** 14 个工具里 `install_package_secure` / `remove_packages` / `manage_orphans` / `manage_install_reason` / `optimize_mirrors` 都会改系统。必须 `trust: untrusted` + `tools.include` 白名单。
3. **`arch-wiki-mcp` 只有 1★，但设计比 59★ 的那个更该学。** 它的三档证据分层（证据/半证据/指针）和 `<esp>` 占位符防误粘设计，是可以直接搬进任何运维 skill 的通用模式。
4. **`herraiz-org/ai-skills` 的文档把 arch-mcp 链接指向了一个 fork。** `iht/arch-mcp` 是 2026-08-08 的 fork（0★，当日停更）。工具名与上游一致，所以技能能用，但把链接改成 `nihalxkumar/arch-mcp`。
5. **Arch News 的 RSS 只有约 10 条。** 任何"检查更新前新闻"的工作流都有一个盲区：上次全量升级早于最旧条目时，中间期间的公告**不可达**。必须显式报告这个盲区，而不是当作"没有新闻"。
6. **`checkupdates` 不在 `pacman` 里，在 `pacman-contrib`。** 而引导安装它时**绝不能从 AUR 满足这个依赖**——那等于用不可信源装一个"用于检查不可信源"的工具。
7. **"commit author 是原作者"不是信任证据。** AUR 的 git commit author 可冒充。唯一的信任来源是你自己读了那次的 PKGBUILD diff。
8. **孤儿包被收养 = 需要重新审计。** AUR 允许任何人收养 orphan，这是本轮 200+ 恶意包的入口之一。把"maintainer 变更"和"orphan 被收养"当作审计触发器。
9. **Arch 知识库不需要 MCP。** `arch-wiki-lite` 一个包给你离线全文 Wiki，体积只有 HTML 版的 1/9。上 MCP 联网查 Wiki 是**把确定性换成不确定性**。
10. **clawhub.ai 搜 "arch" 全是架构（architecture）噪音。** 唯一 Arch Linux 相关的是个玩笑 skill。技能市场对 Arch 运维零覆盖，别在那浪费时间。
11. **r/archlinux 有明显的反 AI slop 情绪。** AI 生成的冗长报告即使内容正确也会被社区忽视甚至围攻。报安全事件要写简洁事实 + 链接 + 包清单，并直发 `aur-general@lists.archlinux.org`。
12. **`informant` 是官方仓库的包，不是 AUR。** 它把"更新前读新闻"从"agent 记得要做"变成"pacman 强制拦你"——**用机制替代提示词**，这比写进 AGENTS.md 可靠。
13. **`archsafe` 已弃坑。** `codexspidey/archsafe`（原 `Ayush-sinha44/archsafe`）2026-06-24 后无提交、无许可证。同类需求用 `archward`（GPL-3.0，2026-08 仍在更新）或自建。
14. **Arch 没有声明式回滚，必须靠快照补。** 这是与 NixOS 最大的结构性差异：NixOS 的"回滚"是系统能力，Arch 的"回滚"要靠 btrfs snapshot / timeshift / `downgrade`。**AI 运维 Arch 时，快照必须发生在升级之前，且这一步不能交给 agent 判断。**

---

## §10 未核实 / 存疑

- `arch-mcp`（arch-ops-server）的**实际工具体验**、`audit_package_security` 的 50+ 红旗命中率、`install_package_secure` 的拦截有效性——**均未独立复现**（C 级，来自 README 与源码结构）。
- `arch-wiki-mcp` 的 hash 稳定性、`test_contract.py` 的实际覆盖面未复现（C 级）。
- `herraiz-org/ai-skills` 的 pytest 套件**未实际运行**（仓库有 CI 配置与测试文件，A 级确认存在，但未验证其通过状态）。
- `traur` / `ks-aur-scanner` 两个第三方 PKGBUILD 扫描器未核验维护状态与检出能力。
- **aurwatch.org / aur-audit.wtako.net 的可用性、准确性、数据更新频率未核验**——它们来自 Reddit 原帖评论，是第三方个人服务（C 级）。生产环境使用前请自行评估其可信度（**让一个第三方服务告诉你"哪些包是恶意的"本身就是一个新的信任依赖**）。
- `archward` 的实际可靠性、快照机制在不同文件系统上的表现未实测（C 级）。
- AUR 上 `github-mcp-server` 等 MCP 包的**安全性未审计**（0 票、个人维护）。
- **本轮未做**：r/archlinux 关于 AUR 事件的后续帖（是否有限制孤儿收养的正式决议）、Arch Linux 官方对 AI 生成 bug report 的政策、`paru`/`yay` 的 `--news` 实际行为差异。

**抓取失败清单（本轮）**：`github.com/nihalxkumar/arch-mcp` 与 `github.com/egarcia74/arch-wiki-mcp` 的 HTML 页面经 WebFetch 返回空内容 → 改用 `api.github.com` + `raw.githubusercontent.com` 成功。`github.com/ranicharradi/arch-maintenance-skill` 返回 **404** —— 该仓库**不存在**，但被搜索结果（mcpmarket.com 聚合页）当作真实技能列出。**教训：聚合站点的技能列表必须逐个回 GitHub 核验。**

---

## §11 参考来源

**MCP 服务器**
1. `github.com/nihalxkumar/arch-mcp` — Arch Linux MCP Server（59★，GPL-3.0-only OR MIT，v3.4.0）
2. `pypi.org/project/arch-ops-server/` — PyPI 包名核验
3. `github.com/egarcia74/arch-wiki-mcp` — Arch Wiki MCP / Truth Perimeter（1★，MIT，v2.1.0）
4. `github.com/iht/arch-mcp` — 2026-08-08 fork（0★，用于核实文档链接漂移）

**Agent Skills**
5. `github.com/herraiz-org/ai-skills` — `update-arch-system` + `install-aur-package`（Apache-2.0，带 CI/pytest）
6. `github.com/enihcam/aur-skills` — 10 个 AUR 打包技能（MIT，有中文 README）
7. `github.com/IPauloGermano/arch-agent-skill` — 桌面环境向 Arch skill
8. `github.com/Pahheb/pahheb-skills` — `aur-skills` 的上游 fork 来源

**软件方案**
9. `github.com/indyfive11/archward` — 安全更新工具（GPL-3.0，快照/回滚/pacnew）
10. `github.com/codexspidey/archsafe` — AI 安全分析 CLI（已弃坑）
11. `aur.archlinux.org/packages/downgrade` — 降级工具（910 票）
12. `aur.archlinux.org/packages/paru` — AUR helper（1260 票）

**官方仓库包（经 archlinux.org API 核验）**
13. `arch-wiki-lite` `20261003-1`（extra/any）— Arch Wiki 无 HTML 版
14. `arch-wiki-docs` `20261003-1`（extra/any）— Arch Wiki 离线浏览版
15. `informant` `0.6.0-2`（extra/any）— Arch News 阅读器 + pacman hook
16. `arch-audit` `0.2.0-5`（extra/x86_64）— CVE 审计
17. `pacman-contrib` `1.13.1-1`（extra/x86_64）— `checkupdates`

**社区**
18. r/archlinux `1vaxtcs` — "Another wave - 200+ malicous AUR packages adoptions"（含 aurwatch.org 自查脚本）
19. r/archlinux `1orwi2b` — "Arch for Beginners with Claude CLI-Code = Very Useful"
20. r/archlinux `1vd5mg3` / `1vk2lwx` — AI 使用态度讨论簇
21. `aur-general@lists.archlinux.org` — AUR 安全问题上报渠道
22. `aurwatch.org/api/v1/check?pkg=<name>` — AUR 包风险查询 API（第三方）
23. `aur-audit.wtako.net/packages?filter=red` — 恶意包清单（第三方）

**技能市场**
24. `clawhub.ai/skills?q=arch` / `?q=pacman` — 实测无 Arch 运维覆盖
25. `aur.archlinux.org/rpc/v5/search/mcp` — AUR MCP 生态（282 结果，热度极低）

**前两轮报告**
26. `research_report_hermes_openclaw_linux_ops.md` — 框架机制、五文件分工、MCP 上下文税、CVE-2026-84289
27. `research_report_nixos_ai_agent_ecosystem.md` — NixOS 四层生态、沙箱共识
