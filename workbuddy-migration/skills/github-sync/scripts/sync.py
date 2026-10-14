#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""github-sync: copy local result files into a persistent GitHub clone and push.

Idempotent: no empty commits. Exit 0 = pushed or nothing to do; 1 = failure.
"""
import argparse
import filecmp
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_DIR / "config.json"


def load_config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def read_token(cfg, override=None):
    if override:
        return override.strip()
    tf = SKILL_DIR / cfg.get("token_file", "token.txt")
    if not tf.exists():
        die("token file not found: %s (run scripts/mint_pat.py)" % tf)
    return tf.read_text(encoding="utf-8").strip()


def die(msg):
    print("ERROR:", msg, file=sys.stderr)
    sys.exit(1)


def _git_env():
    """完全禁用一切交互式凭据提示（GCM GUI / 终端 / askpass）。"""
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "never"          # 关掉 Git Credential Manager 的 GUI 弹窗
    env["GCM_PROVIDER"] = "generic"
    env["GIT_ASKPASS"] = "echo"               # 兜底：任何 askpass 调用直接返回空
    env["SSH_ASKPASS"] = "echo"
    env["GIT_CONFIG_PARAMETERS"] = "'credential.helper='"  # 本次命令内清空 credential.helper
    return env


def run(args, cwd=None, check=True):
    p = subprocess.run(args, cwd=cwd, env=_git_env(), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if check and p.returncode != 0:
        die("cmd failed: %s\n%s\n%s" % (" ".join(args), p.stdout[-2000:], p.stderr[-2000:]))
    return p


def ensure_clone(cfg, token):
    workdir = SKILL_DIR / cfg.get("workdir", "_work")
    repo = cfg["repo"]
    branch = cfg.get("branch", "main")
    clone_dir = workdir / repo.split("/")[-1]
    url = "https://%s:%s@github.com/%s.git" % (repo.split("/")[0], token, repo)
    workdir.mkdir(parents=True, exist_ok=True)

    if (clone_dir / ".git").exists():
        run(["git", "fetch", "--prune", "origin"], cwd=clone_dir)
        run(["git", "checkout", "-q", branch], cwd=clone_dir, check=False)
        run(["git", "reset", "-q", "--hard", "origin/%s" % branch], cwd=clone_dir)
    else:
        if clone_dir.exists():
            shutil.rmtree(clone_dir)
        run(["git", "-c", "core.autocrlf=false", "clone", "-q", url, str(clone_dir)])

    # 每次都强制覆盖本地凭据/合并策略，确保非交互、直接接受远端版本
    run(["git", "config", "core.autocrlf", "false"], cwd=clone_dir)
    run(["git", "config", "http.postBuffer", "524288000"], cwd=clone_dir)
    run(["git", "config", "user.email", "damongoh1031@gmail.com"], cwd=clone_dir)
    run(["git", "config", "user.name", "damongoh1031"], cwd=clone_dir)
    run(["git", "config", "credential.helper", ""], cwd=clone_dir)   # 禁掉 GCM
    run(["git", "config", "pull.rebase", "false"], cwd=clone_dir)     # 接受 merge
    run(["git", "config", "merge.ours.driver", "true"], cwd=clone_dir, check=False)
    run(["git", "config", "core.askPass", "echo"], cwd=clone_dir)     # askpass 兜底
    run(["git", "config", "advice.detachedHead", "false"], cwd=clone_dir)
    return clone_dir


def ensure_gitattributes(cfg, clone_dir):
    ga = clone_dir / ".gitattributes"
    if ga.exists():
        return False
    lines = ["# 保持 CSV 字节精确（meta.json 里的 sha256 按原始字节计算）"]
    for pat, mode in cfg.get("gitattributes", {}).items():
        lines.append("%s %s" % (pat, mode))
    ga.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def copy_src(src: Path, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    else:
        shutil.copy2(src, dest)


def main():
    cfg = load_config()
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", action="append", default=[])
    ap.add_argument("--dest", action="append", default=[])
    ap.add_argument("--use-config-mappings", action="store_true")
    ap.add_argument("-m", "--message", default=None)
    ap.add_argument("--repo", default=None)
    ap.add_argument("--branch", default=None)
    ap.add_argument("--token", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.repo:
        cfg["repo"] = args.repo
    if args.branch:
        cfg["branch"] = args.branch
    token = read_token(cfg, args.token)

    pairs = []
    if args.use_config_mappings:
        for m in cfg.get("mappings", []):
            pairs.append((Path(m["src"]), m["dest"]))
    if args.src:
        if len(args.dest) == 1 and len(args.src) > 1:
            base = args.dest[0]
            for s in args.src:
                pairs.append((Path(s), "%s/%s" % (base.rstrip("/"), Path(s).name)))
        else:
            if len(args.dest) != len(args.src):
                die("--src 与 --dest 数量不匹配（%d vs %d）" % (len(args.src), len(args.dest)))
            pairs.extend((Path(s), d) for s, d in zip(args.src, args.dest))
    if not pairs:
        die("nothing to sync: use --src/--dest or --use-config-mappings")

    missing = [str(s) for s, _ in pairs if not s.exists()]
    if missing:
        die("source(s) not found: %s" % ", ".join(missing))

    clone_dir = ensure_clone(cfg, token)
    branch = cfg.get("branch", "main")
    added_ga = ensure_gitattributes(cfg, clone_dir)

    for src, dest in pairs:
        copy_src(src, clone_dir / dest)
        print("  copied %s -> %s" % (src, dest))

    run(["git", "add", "-A"], cwd=clone_dir)
    st = run(["git", "status", "--porcelain"], cwd=clone_dir).stdout.strip()
    if not st:
        print("NO_CHANGES (already up to date)")
        return 0

    changed = [l[3:].strip().strip('"') for l in st.splitlines() if len(l) > 3]
    print("CHANGED (%d):" % len(changed))
    for c in changed[:40]:
        print("   ", c)
    if len(changed) > 40:
        print("    ... and %d more" % (len(changed) - 40))

    if args.dry_run:
        print("DRY_RUN: not committing")
        return 0

    msg = args.message or ("Sync results %s" % time.strftime("%Y-%m-%d %H:%M"))
    run(["git", "commit", "-q", "-m", msg], cwd=clone_dir)
    print("pushing ...")
    p = run(["git", "push", "origin", branch], cwd=clone_dir, check=False)
    if p.returncode != 0:
        # 远端有分叉：直接拉取合并（接受远端），再推一次，不询问
        print("push rejected, fetching + merging (keep remote) ...")
        run(["git", "fetch", "origin", branch], cwd=clone_dir, check=False)
        run(["git", "-c", "core.mergeOptions=", "merge", "-X", "theirs",
             "--no-edit", "origin/%s" % branch], cwd=clone_dir, check=False)
        p = run(["git", "push", "origin", branch], cwd=clone_dir, check=False)
        if p.returncode != 0:
            # 二次兜底：强制推（本仓库单人使用，接受覆盖远端）
            print("merge push failed, forcing push ...")
            p = run(["git", "push", "--force", "origin", branch], cwd=clone_dir, check=False)
            if p.returncode != 0:
                die("push failed:\n%s\n%s" % (p.stdout[-1500:], p.stderr[-1500:]))

    head = run(["git", "rev-parse", "--short", "HEAD"], cwd=clone_dir).stdout.strip()
    print("PUSHED %s -> https://github.com/%s/commit/%s" % (head, cfg["repo"], head))
    return 0


if __name__ == "__main__":
    sys.exit(main())
