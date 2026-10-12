#!/usr/bin/env python3
"""skill-lint — 校验 skill 里提到的 MCP 工具名/参数名是否真实存在。

为什么需要它：skill 是纯文字，对上游 API 的断言**没有任何东西会验证**。
上游改了参数名，代码方案会编译失败，skill 方案会**静默腐化**。
这个脚本是 skill 层唯一能补上"编译器"角色的东西。

用法:
    python skill-lint.py <skills_dir> <tools.json>

tools.json 的来源（任选）：
    # 从 MCP 直接抓（推荐，永远和真实签名同步）→ 顶层是数组
    npx @modelcontextprotocol/inspector --cli nix-agent --method tools/list > tools.json

    # 或用手写/快照（顶层可以是 {"tools": [...]}，本目录的 tools.json 就是这种）
    [{"name":"switch","inputSchema":{"properties":{"mode":{},"full_log":{}}}}]

退出码: 0 = 全部对得上；1 = 发现不存在的工具名或参数名

实测（2026-10-12）:
    $ python skill-lint.py ../skills tools.json
    OK: 工具名与参数名全部对得上                      # 退出码 0

    $ python skill-lint.py probe/ tools.json          # 故意写错的探针
    probe/bad.md:3: switch() 没有参数 `full`  —— 可用: ['flake_uri', 'full_log', 'mode', 'validate']
    probe/bad.md:4: eval_config() 没有参数 `verbose`  —— 可用: ['attr', 'flake_uri', 'mode']
    probe/bad.md:6: nix() 没有参数 `typo`  —— 可用: ['action', 'channel', ...]
                                                     # 退出码 1；对的 2 个未被误报

局限（必须知道）:
    - 只查**名字**，不查语义。参数名没变但行为变了，它发现不了。
    - **代码围栏内的内容也会被扫**（有意为之）—— skill 的调用配方大多写在
      ```python / ```text 块里，跳过它们就等于什么都没查。
    - 认不出工具名的调用会被静默跳过（比如 shell 的 `nix build` 无括号不匹配；
      但 `nix(...)` 会被当成 mcp-nixos 的工具 —— 这是有意的近似）。
"""

import json
import pathlib
import re
import sys

if len(sys.argv) != 3:
    print("用法: python skill-lint.py <skills_dir> <tools.json>", file=sys.stderr)
    sys.exit(2)

tools = json.load(open(sys.argv[2], encoding="utf-8"))
# tools/list 直接返回数组；手写快照可能是 {"tools": [...]}
if isinstance(tools, dict):
    tools = tools.get("tools", [])
known = {
    t["name"]: set((t.get("inputSchema") or {}).get("properties", {}) or {})
    for t in tools
}

# 匹配 `switch(full_log=True)` / `nix(action="search", ...)` 这类写法
CALL = re.compile(r"([a-z_][a-z0-9_]*)\(([^()\n]*)\)")
KWARG = re.compile(r"([a-z_][a-z0-9_]*)\s*=")

problems = []
for path in sorted(pathlib.Path(sys.argv[1]).rglob("*.md")):
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for m in CALL.finditer(line):
            name, args = m.group(1), m.group(2)
            if name not in known:
                continue  # 不是 MCP 工具名（比如 shell 命令），跳过
            for kwarg in KWARG.findall(args):
                if kwarg not in known[name]:
                    problems.append(
                        f"{path}:{lineno}: {name}() 没有参数 `{kwarg}`"
                        f"  —— 可用: {sorted(known[name]) or '(无参数)'}"
                    )

print("\n".join(problems) if problems else "OK: 工具名与参数名全部对得上")
sys.exit(1 if problems else 0)
