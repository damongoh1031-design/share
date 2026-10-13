# Linux 发行版深度研究（2026-10）

> 11 份专题报告 · 11 份知识库文档 · 17 个维度 · 16 个子代理 · 40+ 处数据纠错
> 研究对象：**Arch · NixOS · openSUSE (Tumbleweed/Slowroll) · Fedora · Debian · Ubuntu**（+ Gentoo / Alpine / CachyOS 参照）
> 数据时点：**2026-10-13** ｜ 方法：多子代理并行调研 + 主调研员 API/HTTP 独立实测复核

---

## 从哪读起

| 你想知道 | 读这份 |
|---|---|
| **只看一份，看这个** | [`reports/linux-distro-deep-research-2026-10.html`](./reports/linux-distro-deep-research-2026-10.html) — 综合报告，19 章 / 96 节，带侧边导航（[md 版](./reports/linux-distro-deep-research-2026-10.md)） |
| 按主题找 | [`kb/`](./kb/) 目录 —— 11 份可复写知识库文档，[索引在这](./kb/README.md) |
| 只想知道选哪个 | 下面「一句话选型」表 |

---

## 一句话选型

| 你的需求 | 选它 | 关键依据 |
|---|---|---|
| **滚动 + 生态成熟** | **openSUSE Tumbleweed** | 唯一 openQA 门禁（650 测试套件 / 114 机器），snapshot 可回滚 |
| **滚动 + 最新软件** | **Arch**（ISO 2026.10.01） | 仓库新鲜度 **86.5%**（全榜第一） |
| **技术最优 + 可回滚** | **NixOS** | 唯一 generation 原子回滚 + 天然多版本共存（但组织风险高） |
| **图形桌面最稳** | **Fedora** | 唯一 SELinux enforcing + firewalld 默认启用 |
| **服务器 / 无人值守** | **Debian** | 1,039 DD 社区，无单点故障 |
| **企业级安全 + 商业支持** | **RHEL / SUSE** | 唯一有 CNA + 专职安全团队 + SLA |
| **LLM 介入运维** | **Fedora / openSUSE** | 日志结构化、公告机制完善、OSV 之外有自建数据 |
| **自动化安全流水线** | **Debian / Ubuntu** | 唯一 OSV 覆盖 + 可执行 JSON API |
| **避免** | **Arch 做无人值守** | tracker 停摆 + 4 人安全团队 + 无 CNA + 三连击事故 |

---

## 五条核心结论

1. **没有全能冠军** —— 17 个维度分属不同发行版，且「文档最好」与「安全最好」是**两个不同的发行版**（ArchWiki vs Ubuntu/Red Hat）。
2. **NixOS 是「技术最优、组织最危」** —— 技术上唯一从架构上消灭配置漂移与孤儿包；组织上 2025 年至今连续三次治理事件（版主 5/7 辞职 → nixpkgs 核心团队解散 → 基金会连亏两年）。
3. **「哪个发行版补丁更快」没有可信答案** —— 唯一公开跨发行版 time-to-patch 数据的服务已主动撤回全部数字（算法缺陷：把未修复 CVE 直接丢弃）。
4. **安全的分水岭是「有没有拿薪水的安全团队」** —— Ubuntu / SUSE 专职团队 vs Arch 4 名志愿者。
5. **滚动版真正的痛点是配置漂移，不是「不可控」** —— 可控性已被 openQA 门禁和声明式重建解决；漂移需靠 `etckeeper` / `ostree admin config-diff` / NixOS 声明式各自应对。

---

## 报告清单（reports/）

| # | 文件 | 主题 |
|---|---|---|
| 1 | rolling-distros-2026-10.md | 滚动发行版五维对比（策略 / 打包 / 报错 / 稳定 / 无人值守） |
| 2 | linux-gaming-perf-2026-10.md | 游戏性能优化六层模型 |
| 3 | kde-vs-gnome-2026-10.md | KDE vs GNOME 六维对比 |
| 4 | new-software-smooth-distros-2026-10.md | 新软件（≤1 月滞后）+ 平滑升级 |
| 5 | llm-sysadmin-distro-2026-10.md | LLM 介入系统运维选型（七维） |
| 6 | ai-collaborative-distro-practice-2026-10.md | MCP / Skills / AI-native OS 全景 |
| 7 | config-drift-rolling-update-2026-10.md | 配置漂移四类型与解法 |
| 8 | distro-community-comprehensive-2026-10.md | 社区七维（打包 / 规范 / 治理 / 规模 / 维护 / 漏洞 / 前景） |
| 9 | **linux-distro-deep-research-2026-10.md / .html** | **综合报告（主交付物）** |
| 10 | distro-operations-analysis-2026-10.md | 运营五维（社区规模 / 现状 / 套件源 / 包管理 / 漏洞修复） |
| 11 | arch-anti-breakage-guide-2026-10.md | **Arch 防滚挂**：预警 / 提醒 / 检查 / Agent 一站式 |
| 12 | other-rolling-distros-2026-10.md | **其他滚动发行版全景**：CachyOS / Omarchy / KDE Linux / AerynOS / Void / Gentoo 等 40+ |

## 知识库（kb/）

可复写文档，每篇含 YAML frontmatter（id / tags / version / confidence）+ 结论 + 表格 + **可复用操作** + **坑与反直觉** + **未核实**。

索引：[`kb/README.md`](./kb/README.md)

---

## 本次研究中最该记住的 10 个坑

1. **`pacman -Sy pkg` 会毁系统** —— 必须 `-Syu`，partial upgrade 是 Arch 用户最常见的自伤方式。
2. **pacman 没有原子性** —— 事务中止时已执行的 remove 不回滚，可损坏 pacman 自身。
3. **只有被声明为「配置文件」的文件才有保护** —— Arch `backup=()`、RPM `%config`、Debian `conffiles`；没声明的文件升级时**直接覆盖，连 `.pacnew` 都不留**。
4. **OSV.dev 有「假覆盖」** —— openSUSE/SUSE 返回 200 但 body 是空 `{}`；Fedora/Arch/NixOS 直接 400。脚本不检查 body 会误判。
5. **Arch 安全数据「在场但已死」** —— JSON 仍返回 2444 条，实际公告 2025-06 停发，覆盖率 <0.3%。
6. **AUR 不是二进制仓库** —— 是 PKGBUILD 脚本库、无官方审核，这是 2026 供应链事件的结构性原因。
7. **`mkRemovedOptionModule` 是 `throw` 不是 warning** —— 官方文档与实现不一致（读 nixpkgs 源码确认）。
8. **markdown 库默认 slugify 丢弃全部非 ASCII 字符** —— 中文标题 id 会退化成纯数字导致死链；解法是用 `slugify_unicode`。
9. **Repology API 返回 403** —— 必须抓 `repositories/statistics` 的 HTML 且带 UA。
10. **Arch 的 DDoS 公告被主流忽略** —— 2025-08-21 官方公告持续 DDoS，是理解 2025-2026 Arch 服务不稳的关键背景。

---

## 工具

- [`tools/md2report.py`](./tools/md2report.py) — Markdown → 精美 HTML 报告转换器
  侧边导航目录 / 表格横向滚动 / 深色模式适配 / 打印友好 / 中文锚点（`slugify_unicode`）
  ```bash
  python tools/md2report.py   # 改脚本内 SRC 路径
  ```

## Skill

- [`skills/arch-update-guard/`](./skills/arch-update-guard/) — **Arch 更新前检查闸门**（零第三方依赖）
  ```bash
  python3 skills/arch-update-guard/scripts/arch_update_guard.py check    # 全套检查
  python3 skills/arch-update-guard/scripts/arch_update_guard.py news     # 只看需人工介入的公告
  python3 skills/arch-update-guard/scripts/arch_update_guard.py selftest # 自检（不需 Arch 环境）
  ```
  10 项检查 · 退出码语义化（0 正常 / 1 注意 / 2 阻塞）· 只读 + 快照需 `--yes`

---

*全部结论标注了 `已核实` / `二手来源` / `未找到` 三级可信度。数据时点 2026-10-13。*
