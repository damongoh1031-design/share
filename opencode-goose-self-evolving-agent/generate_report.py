# -*- coding: utf-8 -*-
"""
generate_report.py —— 按 /research-report 规范把 results/*.json 汇总成 report.md
用法: python generate_report.py
特性:
  - 兼容三种结构：分组式（6 组）/ 扁平式（43 字段平铺）/ targets 式（多对象，如先例、现成轮子）
  - 跳过含 [不确定] 的值与 uncertain[] 中列出的字段
  - 目录带锚点与摘要字段
  - 额外字段收集进「其他信息」
  - 报告开头附结论速览（本主题的核心问题：能或不能 / 若能要如何做）
"""
import json
import os
import re
import glob
from collections import OrderedDict

try:
    import yaml
except ImportError:
    yaml = None

BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(BASE, "results")
OUTLINE = os.path.join(BASE, "outline.yaml")
FIELDS = os.path.join(BASE, "fields.yaml")
REPORT = os.path.join(BASE, "report.md")

# 目录里显示的摘要字段（本主题选定：类型 / 成熟度 / 验证等级）
SUMMARY_FIELDS = [
    ("basic", "type"),
    ("basic", "maturity"),
    ("evidence", "verified_on"),
]

CATEGORY_MAPPING = {
    "basic": ["basic", "basic_info", "基本信息"],
    "extension_surface": ["extension_surface", "扩展面", "extension", "technical_features"],
    "self_evolution": ["self_evolution", "自进化", "evolution"],
    "gap_vs_hermes": ["gap_vs_hermes", "与hermes的差距", "gap", "how_to"],
    "evidence": ["evidence", "证据", "sources"],
    "risk": ["risk", "风险", "risks"],
}

GROUP_LABEL = {
    "basic": "基本信息",
    "extension_surface": "扩展面（七项 + 证据）",
    "self_evolution": "自进化（五条轴）",
    "gap_vs_hermes": "与 Hermes 的差距与补法",
    "evidence": "证据与可复核性",
    "risk": "风险与护栏",
    "其他信息": "其他信息",
}

VERDICT = """## 结论速览

**问题：能否让 opencode / goose 通过安装 skills 与 MCP，变成和 Hermes Agent 一样的自进化 agent？**

### 能。而且分工不对称：

- **「装 skills 与 MCP」根本不是瓶颈**——两家都已具备，且 goose 在 hooks（`PreToolUse` 可阻断工具调用）、plugins（git 一键装 + 自动启用）、原生 cron 调度（`goose schedule --cron`）、技能 token 计量上**比 Hermes 更完整**。opencode 也已有 26 个插件事件与技能权限 deny。
- **真正的缺口只有一件**：没有任何一方把「收尾 → 沉淀 → 复用」的闭环接起来。缺的是 Hermes 的 ②回合后自审 ③技能库 curator ④有界记忆 **⑤可测量的进化（reward signal）** ⑦状态目录约定。
- **轴4（reward signal）是分水岭**：十件现成「自进化轮子」里，能在会话内自动落盘成败信号的只有启发式代理（工具报错 + 用户纠正正则）；真 reward（held-out verifier）全都需要离线数据集，不能自动触发。**「只有采集没有淘汰」正是采集 ≠ 进化之处。**
- **最大红利是共享根**：opencode 与 goose **共读同一个 `~/.agents/skills`**，且都符合 Agent Skills 规范 → **一次沉淀、两家复用**。这把改造成本从「两边各做一套」压到「做一套」。

### 如何做（本目录已产出实物，不是建议）

| 目标 | 最小改动 | 实物位置 |
|---|---|---|
| opencode 自进化 | **1 个插件文件 + 一段 jsonc**，无需改上游 | `deliverables/opencode/` |
| goose 自进化 | **1 个插件目录，零配置改动**（自动发现 + 自动 enabled） | `deliverables/goose/` |
| 两家复用同一技能库 | 技能写入 `~/.agents/skills/<name>/SKILL.md` | 两方案共用 |
| 定时整理 | goose 用原生 `goose schedule`；opencode 用 Windows 任务计划程序 / `opencode-scheduler` | 见手册 §2.4 / §3.3 |

完整步骤、逐项验证命令与回滚方式见 **`deliverables/README.md`**。

### 判定「像不像 Hermes」的尺子（五条轴，缺一不可）

轴1 技能习得 · 轴2 记忆写入 · 轴3 后台复审/curator · **轴4 可测量的进化（reward signal）** · 轴5 自我配置改写（带人工闸门）

> 只有轴1+轴2 而没有轴4 的「自我改进」是**采集**，不是**进化**。本手册两套方案都把轴4（`skill_outcomes.json` 的 use/fail 计数）列为必做项。

### 三个必须知道的风险

1. **安装侧默认放行**是最大注入面：goose 新插件自动 `enabled: true`，**无首次使用确认**（Hermes 有 shell-hooks allowlist 兜底）。
2. **自动写技能 + 无闸门 = 提示注入的自我放大回路**（抓取内容 → 技能 → 后续会话遵从；且技能落在共享根 → 一次污染两家）。两套方案都刻意把「自动写技能」降级为「写待办队列」。
3. **地基不稳（本轮最重要的更正）**：
   - goose 启动时会**静默改写你的 `config.yaml`**（`run_migrations` → `save_values`，不经确认），且对不在 `PLATFORM_EXTENSIONS` 的扩展条目**静默丢弃**；
   - goose 仓库已整体迁到 **`aaif-goose/goose`**（`block/goose` 仅 301 重定向）；重构 PR **#6160 实际未合并**（`state=closed`、`merged_at=null`）；
   - opencode **v1 → v2 是确认的破坏性变更**（`mcp.<name>` → `mcp.servers.<name>`、`enabled` → `disabled` 语义反转、`tools` glob → `permissions` 数组）。
   方案因此刻意只依赖最稳的接口（`~/.agents/` 目录约定 + Open Plugins hooks 规范），其余全部锁版本 + 升级前快照。

### 三条关键口径更正（贯穿全报告的横向对齐基准）

| 项 | 普遍误传 | 实测口径 |
|---|---|---|
| 工具结果 spillover 阈值 | 「5 万字符」当成两家通用 | **Hermes** = `tool_budget.mcp_result_size_chars: 50000`（落 `$HERMES_HOME/cache/spillover`）；**goose** = 200,000（`GOOSE_MAX_TOOL_RESPONSE_SIZE`）；**opencode = 无** |
| goose 扩展事件数 | 文档写的 8 种 | 源码 `HookEvent` 实为 **12 种** |
| goose 非交互审批 | 「会自动批准」 | 非交互 + Approve/SmartApprove **直接报错退出**（fail-closed）；Auto 模式下才自动放行并记 warn |

---

"""


def load_fields_structure():
    if yaml is None:
        return OrderedDict(), set()
    with open(FIELDS, encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    groups = OrderedDict()
    for g in spec.get("field_groups", []):
        groups[g["group"]] = [fld["name"] for fld in g["fields"]]
    declared = set()
    for names in groups.values():
        declared.update(names)
    return groups, declared


def find_value(data, group, field):
    """顶层 -> category 映射 -> 遍历所有嵌套 dict"""
    if field in data:
        return data[field]
    for key in CATEGORY_MAPPING.get(group, [group]):
        sub = data.get(key)
        if isinstance(sub, dict) and field in sub:
            return sub[field]
    for value in data.values():
        if isinstance(value, dict) and field in value:
            return value[field]
    return None


def skip(value):
    if value is None:
        return True
    if isinstance(value, str):
        s = value.strip()
        if not s or "[不确定]" in s or s in ("[不确定]",):
            return True
    if isinstance(value, (list, dict)) and not value:
        return True
    return False


def fmt(value):
    if isinstance(value, dict):
        return "；".join(f"**{k}**：{fmt(v)}" for k, v in value.items() if not skip(v))
    if isinstance(value, list):
        if all(not isinstance(x, (dict, list)) for x in value):
            joined = "；".join(str(x) for x in value)
            return joined if len(joined) <= 160 else "\n" + "\n".join(f"  - {x}" for x in value)
        out = []
        for i, item in enumerate(value, 1):
            if isinstance(item, dict):
                out.append(f"  {i}. " + " | ".join(f"{k}: {fmt(v)}" for k, v in item.items()))
            else:
                out.append(f"  {i}. {fmt(item)}")
        return "\n" + "\n".join(out)
    s = str(value)
    return s if len(s) <= 300 else s.replace("。", "。\n  ")


def anchor(text):
    a = re.sub(r"[^\w\u4e00-\u9fff\- ]", "", text)
    return a.strip().lower().replace(" ", "-")


def render_targets(lines, targets, groups_spec, declared, uncertain):
    """targets 式：每个对象一节，按六组顺序展开字段。"""
    for ti, t in enumerate(targets, 1):
        tname = t.get("name") or t.get("item_name") or f"对象 {ti}"
        lines.append(f"### {ti}. {tname}\n")
        for group, fields in groups_spec.items():
            rows = []
            for fld in fields:
                if f"{group}.{fld}" in uncertain:
                    continue
                v = find_value(t, group, fld)
                if skip(v):
                    continue
                rows.append(f"- **{fld}**：{fmt(v)}")
            if rows:
                lines.append(f"**{GROUP_LABEL.get(group, group)}**\n")
                lines.extend(rows)
                lines.append("")
        extra = [f"- **{k}**：{fmt(v)}" for k, v in t.items()
                 if k not in declared and k not in ("name",) and not skip(v)]
        if extra:
            lines.append("**其他**\n")
            lines.extend(extra)
            lines.append("")


def main():
    groups_spec, declared = load_fields_structure()
    files = sorted(glob.glob(os.path.join(RESULTS, "*.json")))
    items = []
    for path in files:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        name = None
        for g in ("basic", "basic_info", "基本信息"):
            if isinstance(data.get(g), dict) and data[g].get("name"):
                name = data[g]["name"]
                break
        if not name:
            name = data.get("name") or data.get("item_name")
        if not name:
            name = os.path.basename(path).replace(".json", "")
        items.append((name, path, data))

    # ---------- 目录 ----------
    lines = [VERDICT, "## 目录\n"]
    for i, (name, path, data) in enumerate(items, 1):
        bits = []
        for g, fld in SUMMARY_FIELDS:
            v = find_value(data, g, fld)
            if not skip(v) and len(str(v)) <= 60:
                bits.append(f"{fld}: {v}")
        suffix = (" — " + " | ".join(bits)) if bits else ""
        lines.append(f"{i}. [{name}](#{anchor(name)}){suffix}")
    lines.append("\n---\n")

    # ---------- 详细 ----------
    for i, (name, path, data) in enumerate(items, 1):
        lines.append(f"## {name}\n")
        uncertain = data.get("uncertain", [])
        if uncertain:
            if len(uncertain) > 12:
                head = "、".join(uncertain[:12])
                lines.append(f"> 未确定字段（共 {len(uncertain)} 项，列出前 12）：{head} …\n")
            else:
                lines.append(f"> 未确定字段：{'、'.join(uncertain)}\n")

        targets = data.get("targets") or data.get("candidates")
        if isinstance(targets, list) and targets and isinstance(targets[0], dict):
            render_targets(lines, targets, groups_spec, declared, uncertain)
            item_extra = []
            for k, v in data.items():
                if k in ("uncertain", "targets", "candidates", "item_name", "name") or skip(v):
                    continue
                item_extra.append(f"- **{k}**：{fmt(v)}")
            if item_extra:
                lines.append("### 其他信息\n")
                lines.extend(item_extra)
                lines.append("")
            lines.append("---\n")
            continue

        used = set()
        if groups_spec:
            for group, fields in groups_spec.items():
                rows = []
                for fld in fields:
                    if f"{group}.{fld}" in uncertain:
                        continue
                    v = find_value(data, group, fld)
                    if skip(v):
                        continue
                    used.add(fld)
                    rows.append(f"- **{fld}**：{fmt(v)}")
                if rows:
                    lines.append(f"### {GROUP_LABEL.get(group, group)}\n")
                    lines.extend(rows)
                    lines.append("")
        # 额外字段
        extras = []
        for k, v in data.items():
            if k in ("uncertain",) or k in used or k in declared:
                continue
            if isinstance(v, dict) and k in groups_spec:
                continue
            if skip(v):
                continue
            extras.append(f"- **{k}**：{fmt(v)}")
        if extras:
            lines.append("### 其他信息\n")
            lines.extend(extras)
            lines.append("")
        lines.append("---\n")

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("# 如何让 opencode / goose 安装 skills 与 MCP，变成和 Hermes Agent 一样的自进化 agent\n\n")
        f.write(f"> 生成日期：2026-10-16 ｜ 共 {len(items)} 个调研对象 ｜ 数据源：`results/*.json`\n\n")
        f.write("\n".join(lines))
    print(f"OK -> {REPORT}  ({len(items)} items)")


if __name__ == "__main__":
    main()
