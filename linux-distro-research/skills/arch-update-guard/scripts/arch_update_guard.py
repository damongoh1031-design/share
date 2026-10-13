#!/usr/bin/env python3
"""arch-update-guard — Arch Linux 更新前检查闸门（只读）

一条命令完成「更新前全套检查」，输出结构化报告供 agent 解析判断。
零第三方依赖，只用 Python 标准库 + 系统已有工具（pacman-contrib / coreutils）。

子命令:
    check      全套更新前检查（默认）
    news       只看 Arch News 中的「需要人工介入」公告
    snapshot   打 btrfs 快照（需 --yes 确认）
    json       以 JSON 输出 check 结果（便于 agent 解析）
    selftest   用内置样例数据自检解析逻辑（不需要 Arch 环境）

退出码:
    0  一切正常，可以更新
    1  有需要注意的项（见报告 WARN）
    2  有阻塞项，建议先处理（见报告 BLOCK）
    3  环境错误（非 Arch / 缺少依赖）

用法:
    python3 arch_update_guard.py check
    python3 arch_update_guard.py json | jq .
    python3 arch_update_guard.py snapshot --yes
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

NEWS_FEED = "https://archlinux.org/feeds/news/"
UA = "arch-update-guard/1.0 (+local pre-update check)"
TIMEOUT = 20

# 需要人工介入的关键词（Arch News 标题/摘要里出现即视为 BLOCK 级）
CRITICAL_PATTERNS = [
    r"manual intervention",
    r"requires manual",
    r"breaking change",
    r"needs to be restarted",
    r"requires a reboot",
]

# 更新前应关注的「高危包」——这些包更新时值得额外留意
HIGH_RISK_PKGS = {
    "linux", "linux-lts", "linux-zen", "linux-hardened",
    "systemd", "glibc", "pacman", "mkinitcpio", "archlinux-keyring",
    "nvidia", "nvidia-open", "nvidia-dkms", "linux-firmware",
    "plasma-workspace", "kwin", "gnome-shell", "grub", "refind",
}


# ---------------------------------------------------------------- 数据模型

@dataclass
class Finding:
    """单条检查结果。"""
    id: str
    title: str
    level: str            # OK / INFO / WARN / BLOCK
    detail: str = ""
    data: dict = field(default_factory=dict)


@dataclass
class Report:
    is_arch: bool = False
    distro: str = ""
    findings: list = field(default_factory=list)

    def add(self, f: Finding) -> None:
        self.findings.append(f)

    @property
    def level(self) -> str:
        order = {"BLOCK": 3, "WARN": 2, "INFO": 1, "OK": 0}
        return max((f.level for f in self.findings), key=lambda x: order.get(x, 0), default="OK")

    def count(self, level: str) -> int:
        return sum(1 for f in self.findings if f.level == level)


# ---------------------------------------------------------------- 工具函数

def run(cmd: list, timeout: int = 30) -> tuple:
    """执行命令，返回 (returncode, stdout, stderr)。命令不存在返回 (127, '', msg)。"""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except FileNotFoundError:
        return 127, "", f"{cmd[0]}: command not found"
    except subprocess.TimeoutExpired:
        return 124, "", f"{cmd[0]}: timeout after {timeout}s"
    except Exception as e:                                  # noqa: BLE001
        return 1, "", f"{cmd[0]}: {e}"


def read_os_release() -> dict:
    """解析 /etc/os-release。非 Linux / 读不到则返回空 dict。"""
    for p in ("/etc/os-release", "/usr/lib/os-release"):
        try:
            txt = Path(p).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        out = {}
        for line in txt.splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                out[k.strip()] = v.strip().strip('"').strip("'")
        if out:
            return out
    return {}


def fetch_news() -> list:
    """抓取 Arch News RSS，返回 [{title, link, date, summary}]。失败返回 []。"""
    req = Request(NEWS_FEED, headers={"User-Agent": UA})
    with urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    root = ET.fromstring(raw)
    items = []
    for it in root.iter("item"):
        def g(tag):
            el = it.find(tag)
            return (el.text or "").strip() if el is not None and el.text else ""
        items.append({
            "title": g("title"),
            "link": g("link"),
            "date": g("pubDate"),
            "summary": re.sub(r"<[^>]+>", " ", g("description"))[:400],
        })
    return items


def match_critical(text: str) -> Optional[str]:
    """返回命中的关键词，未命中返回 None。"""
    low = text.lower()
    for pat in CRITICAL_PATTERNS:
        if re.search(pat, low):
            return pat
    return None


# ---------------------------------------------------------------- 各项检查

def check_env(rep: Report) -> None:
    osr = read_os_release()
    rep.distro = osr.get("PRETTY_NAME", osr.get("NAME", "unknown"))
    ids = (osr.get("ID", "") + " " + osr.get("ID_LIKE", "")).lower()
    rep.is_arch = "arch" in ids
    if not osr:
        rep.add(Finding("env", "环境检测", "BLOCK",
                        "读不到 /etc/os-release —— 不是 Linux，或权限异常"))
    elif rep.is_arch:
        rep.add(Finding("env", "环境检测", "OK", f"检测到 {rep.distro}"))
    else:
        rep.add(Finding("env", "环境检测", "BLOCK",
                        f"当前系统是 {rep.distro}，本工具只适用于 Arch 系（含 EndeavourOS / CachyOS / Manjaro 等 ID_LIKE=arch 的衍生版）"))


def check_news(rep: Report) -> None:
    try:
        items = fetch_news()
    except (URLError, ET.ParseError, OSError) as e:
        rep.add(Finding("news", "Arch News", "WARN",
                        f"抓取失败：{e} —— 请手动访问 {NEWS_FEED}"))
        return

    if not items:
        rep.add(Finding("news", "Arch News", "WARN", "feed 返回 0 条，格式可能已变"))
        return

    hits = []
    for it in items[:15]:                      # 只看最近 15 条
        hit = match_critical(it["title"] + " " + it["summary"])
        if hit:
            hits.append({"title": it["title"], "link": it["link"],
                         "date": it["date"], "matched": hit})

    latest = items[0]
    if hits:
        rep.add(Finding(
            "news", "Arch News：发现需人工介入的公告", "BLOCK",
            f"最近 15 条中有 {len(hits)} 条命中关键规则 —— 升级前必须逐条阅读",
            {"hits": hits, "latest": latest},
        ))
    else:
        rep.add(Finding("news", "Arch News：无阻塞公告", "OK",
                        f"最近 15 条无「manual intervention」类公告；最新一条：{latest['title'][:80]}",
                        {"latest": latest}))


def check_updates(rep: Report) -> None:
    code, out, err = run(["checkupdates"])
    if code == 127:
        rep.add(Finding("updates", "待更新包", "WARN",
                        "未安装 checkupdates —— 它属于 pacman-contrib：sudo pacman -S pacman-contrib"))
        return
    if code == 2:
        rep.add(Finding("updates", "待更新包", "OK", "系统已是最新，无需更新"))
        return
    if code != 0:
        rep.add(Finding("updates", "待更新包", "WARN",
                        f"checkupdates 返回 {code}：{err or out or '无输出'}"))
        return

    pkgs = [l.split()[0] for l in out.splitlines() if l.strip()]
    risky = sorted(set(pkgs) & HIGH_RISK_PKGS)

    lvl = "INFO"
    detail = f"共 {len(pkgs)} 个包待更新"
    if risky:
        lvl = "WARN"
        detail += f"；其中高危包 {len(risky)} 个：{', '.join(risky)}"
    if "archlinux-keyring" in pkgs:
        lvl = "WARN"
        detail += " ⚠ 含 archlinux-keyring，建议先单独更新它"

    rep.add(Finding("updates", "待更新包", lvl, detail,
                    {"count": len(pkgs), "packages": pkgs[:60], "risky": risky}))


def check_disk(rep: Report) -> None:
    targets = [p for p in ("/", "/var", "/boot", "/boot/efi") if os.path.ismount(p) or os.path.isdir(p)]
    rows, worst = [], None
    for t in targets:
        try:
            u = shutil.disk_usage(t)
        except OSError:
            continue
        pct = u.used / u.total * 100 if u.total else 0
        rows.append({"mount": t, "total_gb": round(u.total / 2**30, 1),
                     "free_gb": round(u.free / 2**30, 1), "used_pct": round(pct, 1)})
        if worst is None or pct > worst["used_pct"]:
            worst = rows[-1]

    if not rows:
        rep.add(Finding("disk", "磁盘空间", "INFO", "无法读取磁盘用量"))
        return

    if worst and worst["used_pct"] >= 95:
        lvl, msg = "BLOCK", f"{worst['mount']} 已用 {worst['used_pct']}% —— 空间不足可能导致更新失败"
    elif worst and worst["used_pct"] >= 85:
        lvl, msg = "WARN", f"{worst['mount']} 已用 {worst['used_pct']}% —— 建议先清理"
    else:
        lvl, msg = "OK", f"空间充足（最紧张：{worst['mount']} {worst['used_pct']}% 已用，剩 {worst['free_gb']} GB）"

    rep.add(Finding("disk", "磁盘空间", lvl, msg, {"mounts": rows}))


def check_pacnew(rep: Report) -> None:
    """扫描 /etc 下遗留的 .pacnew / .pacsave。"""
    roots = [Path("/etc")]
    found = []
    for root in roots:
        if not root.is_dir():
            continue
        try:
            for p in root.rglob("*"):
                if p.suffix in (".pacnew", ".pacsave"):
                    found.append(str(p))
                if len(found) > 200:
                    break
        except (OSError, PermissionError):
            continue

    if found:
        rep.add(Finding("pacnew", "遗留配置文件", "WARN",
                        f"发现 {len(found)} 个 .pacnew/.pacsave —— 用 sudo pacdiff 处理（本次更新前先清掉旧的）",
                        {"files": found[:40], "total": len(found)}))
    else:
        rep.add(Finding("pacnew", "遗留配置文件", "OK", "/etc 下无 .pacnew/.pacsave 遗留"))


def check_services(rep: Report) -> None:
    code, out, _ = run(["systemctl", "--failed", "--no-legend", "--plain"])
    if code == 127:
        rep.add(Finding("services", "失败的服务", "INFO", "无 systemd，跳过"))
        return
    lines = [l for l in out.splitlines() if l.strip()]
    if lines:
        rep.add(Finding("services", "失败的服务", "WARN",
                        f"{len(lines)} 个单元处于 failed 状态 —— 更新前先修好，否则难以区分新旧故障",
                        {"units": [l.split()[0] for l in lines[:20]]}))
    else:
        rep.add(Finding("services", "失败的服务", "OK", "无 failed 单元"))


def check_snapshot(rep: Report) -> None:
    """检查快照能力是否就绪。"""
    has_snapper = shutil.which("snapper") is not None
    has_btrfs = shutil.which("btrfs") is not None
    has_snap_pac = Path("/usr/share/libalpm/hooks").is_dir() and any(
        "snap-pac" in p.name for p in Path("/usr/share/libalpm/hooks").glob("*")
    ) if Path("/usr/share/libalpm/hooks").is_dir() else False

    if has_snapper and has_btrfs:
        code, out, _ = run(["snapper", "-c", "root", "list"], timeout=15)
        n = len([l for l in out.splitlines() if l.strip()]) - 1 if code == 0 else 0
        extra = "，且 snap-pac 已安装（会自动打快照）" if has_snap_pac else "，但未检测到 snap-pac（不会自动打快照）"
        rep.add(Finding("snapshot", "快照兜底", "OK",
                        f"btrfs + snapper 就绪，现有 {max(n,0)} 个快照{extra}",
                        {"snapper": True, "btrfs": True, "snap_pac": has_snap_pac}))
    elif has_snapper:
        rep.add(Finding("snapshot", "快照兜底", "WARN",
                        "装了 snapper 但未检测到 btrfs 工具 —— 确认根文件系统是否为 btrfs"))
    else:
        rep.add(Finding("snapshot", "快照兜底", "WARN",
                        "未检测到 snapper/btrfs —— 无快照兜底。强烈建议：sudo pacman -S snapper snap-pac 并配置 btrfs 快照"))


def check_backup_kernel(rep: Report) -> None:
    """检查是否有备用内核（linux-lts）。"""
    code, out, _ = run(["pacman", "-Qq", "linux-lts"])
    has_lts = code == 0 and bool(out.strip())
    code2, out2, _ = run(["pacman", "-Qq", "linux"])
    has_linux = code2 == 0 and bool(out2.strip())

    if has_lts:
        rep.add(Finding("kernel", "备用内核", "OK", "已装 linux-lts，主内核故障时可从引导菜单回退"))
    elif has_linux:
        rep.add(Finding("kernel", "备用内核", "WARN",
                        "只装了 linux 主内核 —— 内核更新出问题将无法启动。建议：sudo pacman -S linux-lts"))
    else:
        rep.add(Finding("kernel", "备用内核", "INFO", "未检测到 linux / linux-lts 包"))


def check_pkg_cache(rep: Report) -> None:
    """包缓存是降级的弹药库。"""
    d = Path("/var/cache/pacman/pkg")
    if not d.is_dir():
        rep.add(Finding("cache", "包缓存", "INFO", "无 /var/cache/pacman/pkg"))
        return
    try:
        files = [f for f in d.iterdir() if f.is_file()]
        total = sum(f.stat().st_size for f in files)
    except OSError:
        rep.add(Finding("cache", "包缓存", "INFO", "无法读取缓存目录"))
        return

    gb = total / 2**30
    if len(files) == 0:
        rep.add(Finding("cache", "包缓存", "WARN",
                        "缓存为空 —— 无法降级任何包。不要清空 /var/cache/pacman/pkg"))
    else:
        rep.add(Finding("cache", "包缓存", "OK",
                        f"{len(files)} 个包文件 / {gb:.1f} GB —— 可作为降级弹药库",
                        {"files": len(files), "gb": round(gb, 2)}))


def check_keyring(rep: Report) -> None:
    code, out, _ = run(["pacman", "-Qq", "archlinux-keyring"])
    if code != 0:
        rep.add(Finding("keyring", "密钥环", "WARN", "未检测到 archlinux-keyring"))
        return
    ver = out.strip()
    timer = Path("/usr/lib/systemd/system/archlinux-keyring-wkd-sync.timer")
    if timer.exists():
        rep.add(Finding("keyring", "密钥环", "OK",
                        f"{ver}；wkd-sync timer 存在（默认每周自动同步签名）"))
    else:
        rep.add(Finding("keyring", "密钥环", "WARN",
                        f"{ver}；未找到 wkd-sync timer，签名可能过期。可跑 pacman-key --refresh-keys"))


# ---------------------------------------------------------------- 编排

ALL_CHECKS = [
    ("env", check_env),
    ("news", check_news),
    ("updates", check_updates),
    ("disk", check_disk),
    ("pacnew", check_pacnew),
    ("services", check_services),
    ("snapshot", check_snapshot),
    ("kernel", check_backup_kernel),
    ("cache", check_pkg_cache),
    ("keyring", check_keyring),
]

ICON = {"OK": "[ OK ]", "INFO": "[INFO]", "WARN": "[WARN]", "BLOCK": "[BLOCK]"}


def build_report(only: Optional[list] = None) -> Report:
    rep = Report()
    for name, fn in ALL_CHECKS:
        if only and name not in only:
            continue
        try:
            fn(rep)
        except Exception as e:                              # noqa: BLE001
            rep.add(Finding(name, f"{name} 检查异常", "WARN", f"{type(e).__name__}: {e}"))
    return rep


def render(rep: Report) -> str:
    lines = []
    lines.append("=" * 68)
    lines.append(" Arch 更新前检查报告  ·  arch-update-guard")
    lines.append(f" 系统：{rep.distro or '未知'}")
    lines.append("=" * 68)
    for f in rep.findings:
        lines.append(f"{ICON.get(f.level, '[????]')} {f.title}")
        if f.detail:
            for seg in _wrap(f.detail, 62):
                lines.append(f"         {seg}")
        # 关键数据展开
        d = f.data or {}
        if f.id == "news" and d.get("hits"):
            for h in d["hits"]:
                lines.append(f"         - {h['title'][:70]}")
                lines.append(f"           {h['link']}")
        if f.id == "updates" and d.get("packages"):
            shown = d["packages"][:12]
            lines.append(f"         包列表：{', '.join(shown)}"
                         + (f" …共 {d['count']} 个" if d["count"] > len(shown) else ""))
        if f.id == "pacnew" and d.get("files"):
            for p in d["files"][:6]:
                lines.append(f"         - {p}")
        if f.id == "services" and d.get("units"):
            lines.append(f"         单元：{', '.join(d['units'][:8])}")
    lines.append("-" * 68)
    n_ok, n_info = rep.count("OK"), rep.count("INFO")
    n_warn, n_block = rep.count("WARN"), rep.count("BLOCK")
    lines.append(f" 汇总：OK {n_ok} · INFO {n_info} · WARN {n_warn} · BLOCK {n_block}")

    if rep.level == "BLOCK":
        lines.append(" 结论：⛔ 有阻塞项，先处理后更新")
    elif rep.level == "WARN":
        lines.append(" 结论：⚠ 有需注意项，建议处理后更新")
    else:
        lines.append(" 结论：✅ 可以更新（记得 sudo pacman -Syu）")
    lines.append("=" * 68)
    return "\n".join(lines)


def _wrap(text: str, width: int) -> list:
    out, cur = [], ""
    for ch in text:
        cur += ch
        if len(cur) >= width and ch in " ，。；、,)":
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return out or [""]


def exit_code(rep: Report) -> int:
    return {"OK": 0, "INFO": 0, "WARN": 1, "BLOCK": 2}.get(rep.level, 1)


# ---------------------------------------------------------------- 子命令

def cmd_check(args) -> int:
    rep = build_report()
    if args.json:
        print(json.dumps({
            "distro": rep.distro, "is_arch": rep.is_arch,
            "level": rep.level, "exit_code": exit_code(rep),
            "findings": [asdict(f) for f in rep.findings],
        }, ensure_ascii=False, indent=2))
    else:
        print(render(rep))
    return exit_code(rep)


def cmd_news(args) -> int:
    try:
        items = fetch_news()
    except Exception as e:                                  # noqa: BLE001
        print(f"抓取 Arch News 失败：{e}", file=sys.stderr)
        return 3
    hits = [(it, match_critical(it["title"] + " " + it["summary"])) for it in items[:20]]
    crit = [(it, m) for it, m in hits if m]
    if not crit:
        print("最近 20 条 Arch News 中没有「需要人工介入」类公告。")
        print(f"最新一条：{items[0]['title']}  ({items[0]['date']})")
        return 0
    print(f"⚠ 发现 {len(crit)} 条需要人工介入的公告：\n")
    for it, m in crit:
        print(f"  · {it['title']}")
        print(f"    {it['date']}")
        print(f"    {it['link']}")
        print(f"    命中规则：{m}\n")
    return 2


def cmd_snapshot(args) -> int:
    if not args.yes:
        print("将执行：snapper -c root create -d 'pre-update <日期>'")
        print("这是写操作。确认请加 --yes")
        return 3
    if shutil.which("snapper") is None:
        print("未安装 snapper。安装：sudo pacman -S snapper snap-pac", file=sys.stderr)
        return 3
    desc = args.desc or f"pre-update {__import__('datetime').date.today()}"
    code, out, err = run(["sudo", "snapper", "-c", "root", "create", "-d", desc], timeout=60)
    if code != 0:
        print(f"创建快照失败：{err or out}", file=sys.stderr)
        return 1
    print(f"快照已创建：{out or desc}")
    return 0


def cmd_selftest(args) -> int:
    """用样例数据验证解析逻辑，不需要 Arch 环境。"""
    ok = True

    def t(name, cond):
        nonlocal ok
        print(f"  {'PASS' if cond else 'FAIL'}  {name}")
        ok = ok and cond

    print("selftest: 解析逻辑自检\n")

    t("critical 命中 manual intervention",
      match_critical("Mkinitcpio >=42 requires manual intervention for TPM2") == r"manual intervention")
    t("critical 命中 requires manual",
      match_critical("Some package requires manual steps") == r"requires manual")
    t("critical 命中 breaking change",
      match_critical("Breaking changes for varnish") == r"breaking change")
    t("critical 不误报普通新闻",
      match_critical("Arch Linux 2026 Leader Election Results") is None)
    t("critical 不误报包更新",
      match_critical("linux-firmware 20250901 released") is None)

    # 高危包识别
    pkgs = ["linux", "vim", "glibc", "firefox", "nvidia"]
    t("高危包识别", sorted(set(pkgs) & HIGH_RISK_PKGS) == ["glibc", "linux", "nvidia"])

    # os-release 解析（用样例）
    sample = 'NAME="Arch Linux"\nID=arch\nID_LIKE=arch\nPRETTY_NAME="Arch Linux"\n'
    parsed = {}
    for line in sample.splitlines():
        k, _, v = line.partition("=")
        parsed[k] = v.strip('"')
    t("os-release 解析", parsed.get("ID") == "arch" and parsed.get("PRETTY_NAME") == "Arch Linux")

    # 换行函数不丢字符
    text = "这是一段用于测试换行函数的较长的中文说明文字，需要在标点处断行，且不能丢失任何字符。"
    t("换行函数不丢字符", "".join(_wrap(text, 20)) == text)

    # 退出码映射
    r0, r1, r2 = Report(), Report(), Report()
    r0.add(Finding("x", "t", "OK")); r1.add(Finding("x", "t", "WARN")); r2.add(Finding("x", "t", "BLOCK"))
    t("退出码 OK->0", exit_code(r0) == 0)
    t("退出码 WARN->1", exit_code(r1) == 1)
    t("退出码 BLOCK->2", exit_code(r2) == 2)

    # 报告 level 取最严重
    rm = Report(); rm.add(Finding("a", "t", "OK")); rm.add(Finding("b", "t", "BLOCK"))
    t("报告 level 取最严重", rm.level == "BLOCK")

    # 渲染不崩
    try:
        s = render(rm)
        t("渲染报告", "arch-update-guard" in s and "BLOCK" in s)
    except Exception as e:                                  # noqa: BLE001
        print(f"  FAIL  渲染报告抛异常: {e}")
        ok = False

    print(f"\nselftest: {'全部通过' if ok else '有失败项'}")
    return 0 if ok else 1


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(
        prog="arch-update-guard",
        description="Arch Linux 更新前检查闸门（只读）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = ap.add_subparsers(dest="cmd")

    p_check = sub.add_parser("check", help="全套更新前检查（默认）")
    p_check.add_argument("--json", action="store_true", help="以 JSON 输出")
    p_check.set_defaults(func=cmd_check)

    p_news = sub.add_parser("news", help="只看需要人工介入的公告")
    p_news.set_defaults(func=cmd_news)

    p_snap = sub.add_parser("snapshot", help="打 btrfs 快照（需 --yes）")
    p_snap.add_argument("--yes", action="store_true", help="确认执行写操作")
    p_snap.add_argument("--desc", default="", help="快照描述")
    p_snap.set_defaults(func=cmd_snapshot)

    p_json = sub.add_parser("json", help="等同 check --json")
    p_json.set_defaults(func=lambda a: cmd_check(argparse.Namespace(json=True)))

    p_st = sub.add_parser("selftest", help="用样例数据自检解析逻辑")
    p_st.set_defaults(func=cmd_selftest)

    args = ap.parse_args()
    if not getattr(args, "func", None):
        args = argparse.Namespace(cmd="check", json=False, func=cmd_check)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
