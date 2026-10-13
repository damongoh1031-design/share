#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
 scrape_malaysiayp.py  v3.0.0
 从 malaysiayp.com 按站点结构抓取「公司名 + 01X 手机号」
================================================================================
 版本号唯一真源：文件内 __version__ 常量。
 本行由 --self-test 第 9 组断言与 __version__ 一致，防止两处版本漂移。

 设计目标：可脱离 LLM 长期无人值守运维 + 人类可维护

--------------------------------------------------------------------------------
 【脚本内可查询的完整说明】
    python scrape_malaysiayp.py --manual      # 完整手册（用法/参数/退出码/维护）
    python scrape_malaysiayp.py --examples    # 只看示例
    python scrape_malaysiayp.py --print-api   # 只看函数接口速查
    python scrape_malaysiayp.py --help        # 参数速查
--------------------------------------------------------------------------------

 【七项核心能力】
   1. 顺序下载      --order sequential 按「分类顺序 → 页码升序」抓，配合 manifest 可验证完整性
   2. 重复下载防护   URL 缓存(sha1) + seen_url + 电话级去重 + manifest 查重，三层
   3. 输出保护      已存在则拒绝覆盖（需 --force）；覆盖前自动 .bak；--append 增量合并；
                    缩水守卫（新结果远少于旧结果时拒绝）
   4. 人类可维护     全函数类型注解 + 接口速查表 + 分节横幅 + 单文件零依赖
   5. 内置手册       --manual / --examples / --print-api / --help
   6. 任意数量下载   --n + --preset tiny/small/medium/large
   7. 序列下载防限流  单线程严格串行 + --delay 间隔 + --jitter 抖动 + 429/503 退避 +
                    软限流(空响应)退避 + --max-minutes 时间预算

 【额外的重要机制】
   * 互斥锁     同一时刻只允许一个实例运行（计划任务重叠会双倍限流）—— OS 级文件锁，进程死自动释放
   * 优雅退出   SIGINT/SIGTERM 均保存断点，退出码 130，可 --resume
   * 脚本指纹   版本号 + 源码 sha256 写入 meta，可追溯是「哪一版脚本」产出的
   * 自愈       索引/缓存损坏自动重建；输出被占用自动降级
   * 覆盖率检查 --coverage 报告每个分类已下载哪些页、有哪些缺口
--------------------------------------------------------------------------------

 【函数接口速查】（详见 --print-api）
   异常    Fatal / Unavailable / StructureChanged / OutputProtected / Locked
   基础设施 atomic_write()  file_lock()  source_fingerprint()
   日志    setup_logging()
   缓存    cache_path()  fetch()
   合规    parse_robots()  robots_allowed()  check_robots()
   索引    build_index()  load_index()
   清单    load_manifest()  save_manifest()  record_page()  coverage_report()
   断点    save_state()  load_state()  clear_state()
   解析    clean_text()  parse_rows()
   调度    iter_plan()  scrape()
   输出    guard_output()  backup_existing()  write_csv()  append_merge()  write_meta()
   模式    cmd_doctor()  cmd_verify()  cmd_coverage()  cmd_check_robots()
   入口    build_parser()  main()
--------------------------------------------------------------------------------

 【退出码】
   0    成功且达标
   2    参数错误
   3    环境错误（目录不可写 / 网络不通 / robots.txt 不允许）
   4    被站点封禁或出现验证页
   5    站点结构变更（解析持续为空）—— 需人工更新 ROW_RE
   6    抓取成功但条数不足目标
   7    输出文件已存在且未给 --force / --append（防误覆盖）
   8    已有另一个实例在运行（互斥锁）
   130  被中断（断点已存，可 --resume 续跑）

 【合规前置】
已经得到授权，合规
================================================================================
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import logging
import os
import random
import re
import shutil
import signal
import socket
import sys
import time
import urllib.error
import urllib.request
import urllib.parse
import urllib.robotparser
import http.client
import email.utils
import math
from html.parser import HTMLParser
from typing import Any, Dict, Iterator, List, Optional, Sequence, Set, Tuple

# --- 让 Windows 控制台(cp936)也能安全输出中文与符号，避免 UnicodeEncodeError ---
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass


# ==============================================================================
# 0. 版本与元信息
# ==============================================================================
__version__ = "3.0.0"
SCHEMA_VERSION = 2          # CSV / meta / manifest 的结构版本；改列时递增

# ==============================================================================
# 1. 退出码 —— 无人值守监控的唯一可靠信号
# ==============================================================================
EXIT_OK = 0
EXIT_USAGE = 2
EXIT_ENV = 3
EXIT_BLOCKED = 4
EXIT_STRUCTURE = 5
EXIT_INSUFFICIENT = 6
EXIT_OUTPUT = 7
EXIT_LOCKED = 8
EXIT_PARTIAL = 9
EXIT_INTERRUPTED = 130

EXIT_DOC: Dict[int, str] = {
    EXIT_OK: "成功且达标",
    EXIT_USAGE: "参数错误",
    EXIT_ENV: "环境错误（目录不可写 / 网络不通 / robots.txt 不允许）",
    EXIT_BLOCKED: "被站点封禁或出现验证页",
    EXIT_STRUCTURE: "站点结构变更（解析持续为空）",
    EXIT_INSUFFICIENT: "抓取成功但条数不足目标",
    EXIT_OUTPUT: "输出文件已存在且未给 --force / --append",
    EXIT_LOCKED: "已有另一个实例在运行",
    EXIT_PARTIAL: "分段/时间预算暂停（已有页已提交，重跑原命令自动续跑）",
    EXIT_INTERRUPTED: "被中断（可 --resume 续跑）",
}

# ==============================================================================
# 2. CONFIG —— 要调的东西都在这里
# ==============================================================================
BASE = "https://malaysiayp.com"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
LOGDIR = os.path.join(HERE, "logs")
DATADIR = os.path.join(HERE, "data")
INDEX_PATH = os.path.join(CACHE, "index.json")
STATE_PATH = os.path.join(CACHE, "state.json")
MANIFEST_PATH = os.path.join(CACHE, "manifest.json")
LOCK_PATH = os.path.join(CACHE, ".lock")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# 一条记录 = 一个 <li class="row-item">
#   5 个捕获组顺序（改版时只改这里，顺序不可变）：
#     1 详情链接  2 公司名  3 地址  4 电话数字(tel:)  5 电话显示
ROW_RE = re.compile(
    r'<li class="row-item">'
    r'[\s\S]*?<a href="(/item/[^"]+)"[^>]*>([^<]+)</a>'
    r'[\s\S]*?<span class="row-meta">([^<]*)</span>'
    r'[\s\S]*?<a[^>]*class="row-phone"[^>]*href="tel:(\d+)"'
    r'[^>]*>([^<]*)</a>',
    re.I,
)
CAT_RE = re.compile(r'href="(/cat/[a-z0-9\-]+/)"', re.I)
PAGES_RE = re.compile(r'href="/cat/[a-z0-9\-]+/page/(\d+)/"', re.I)
# 马来西亚手机号（01X）形态 —— 两种长度，缺一不可：
#   10 位：01X-XXXXXXX  （012 / 013 / 014 / 016 / 017 / 018 / 019 …）
#   11 位：011-XXXXXXXX （011 段，MVNO 主力号段）
# 注意：曾经写成 01\d{7,8}，只能匹配 9~10 位 —— 会把全部 011 号码静默丢弃。
#       2026-10-08 用缓存实测：1098 条 10 位 + 12 条 11 位（全为 011），
#       9 位一条都没有。故改为「精确 10 位 或 精确 11 位 011」。
MOBILE_RE = re.compile(r"01\d{8}|011\d{8}")

BLOCK_MARKERS = [
    "just a moment", "cf-chl", "attention required", "checking your browser",
    "enable javascript and cookies", "access denied", "captcha",
]

MIN_PAGE_BYTES = 3000        # 低于此值视为「空响应 / 软限流」
DEFAULT_DELAY = 2.0          # 默认请求间隔（秒）
DEFAULT_JITTER = 0.5         # 默认抖动上限（秒），避免固定间隔被识别

CSV_COLS = ["no", "company", "phone", "display", "category",
            "address", "detail_url", "source_page"]

# 规模预设：常用数量组合
PRESETS: Dict[str, Dict[str, int]] = {
    "tiny":   {"n": 20,  "per_cat": 5,  "max_pages": 6},
    "small":  {"n": 50,  "per_cat": 8,  "max_pages": 15},
    "medium": {"n": 100, "per_cat": 10, "max_pages": 30},
    "large":  {"n": 500, "per_cat": 20, "max_pages": 120},
}

BANNER = """
======================================================================
 合规前置条件（脚本会自动校验 robots.txt）
 1) 该站 robots.txt 把 AI 爬虫分两组：GPTBot/ClaudeBot/Google-Extended/CCBot
    等训练型 → Disallow；OAI-SearchBot/ChatGPT-User/PerplexityBot 等
    检索型 → Allow。通用 UA 组为 Allow: /（仅禁 /api/ 与 /*?s=）。
 2) PDPA 2010(2024)：聚合「公司名+手机号」= 个人数据处理，须限定用途
    （仅目录检索/研究；禁止群发 / 推销 / 骚扰 / 转售）。
 3) 默认分段全量：每段最多25页、段间冷却30秒、逐页事务落盘；\n    只有显式 --n/--preset 才走旧抽样模式。robots 会实时检查。
======================================================================
"""

log = logging.getLogger("myp")

# 全局中断标志（SIGINT / SIGTERM 都会置位，由抓取循环检查）
_INTERRUPTED = False


# ==============================================================================
# 3. 异常 —— 语义分离，决定「中止 / 跳过 / 保护」
# ==============================================================================
class Fatal(Exception):
    """不可重试的致命错误（被封 / 验证页）。一旦抛出必须立刻中止。"""


class Unavailable(Exception):
    """单个页面不可用（404 / 页码越界）。只跳过这一页，不影响整体。"""


class StructureChanged(Exception):
    """站点结构变更（持续解析为空）。需人工更新 ROW_RE。"""


class TransientFailure(RuntimeError):
    """Retryable request with a server-mandated minimum cooldown."""
    def __init__(self, message: str, retry_after: float = 0.0) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class OutputProtected(Exception):
    """输出文件保护触发（已存在且未授权覆盖 / 缩水）。"""


class Locked(Exception):
    """已有另一个实例在运行。"""


# ==============================================================================
# 4. 日志 —— 无人值守排错的唯一依据
# ==============================================================================
def setup_logging(verbose: bool = False,
                  log_dir: str = LOGDIR) -> Tuple[logging.Logger, Optional[str]]:
    """同时输出到控制台和文件。文件日志是计划任务排错的关键。

    :param verbose: True 时输出 DEBUG 级
    :param log_dir: 日志目录
    :return: (logger, log_path)；log_path 为 None 表示文件日志不可用
    """
    log.setLevel(logging.DEBUG if verbose else logging.INFO)
    log.handlers.clear()
    log.propagate = False

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(console)

    log_path: Optional[str] = None
    try:
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "run-%s.log" % time.strftime("%Y%m%d-%H%M%S"))
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)-5s %(message)s", "%Y-%m-%d %H:%M:%S"))
        fh.setLevel(logging.DEBUG)
        log.addHandler(fh)
    except Exception as e:                       # 日志目录不可写不应导致任务失败
        log.warning("[警告] 无法创建日志文件(%s)，仅输出到控制台", e)

    return log, log_path


# ==============================================================================
# 5. 基础设施：原子写 / 互斥锁 / 脚本指纹
# ==============================================================================
def atomic_write(path: str, text: str, encoding: str = "utf-8") -> None:
    """原子写：先写同目录 .tmp 再替换，避免进程被杀留下半截文件。

    :param path: 目标路径
    :param text: 内容
    :param encoding: 编码
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding=encoding, newline="") as fh:
        fh.write(text)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def file_lock(path: str):
    """获取 OS 级排他锁（非阻塞）。进程退出/被杀时由内核自动释放，不会留死锁。

    :param path: 锁文件路径
    :return: 成功返回打开的文件句柄（需保持引用），失败返回 None
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fh = open(path, "a+")
    try:
        if os.name == "nt":
            import msvcrt
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Do not truncate a byte range while it is locked on Windows.
        fh.seek(0)
        fh.write("pid=%d started=%s\n" % (os.getpid(), time.strftime("%Y-%m-%d %H:%M:%S")))
        fh.flush()
        return fh
    except OSError:
        fh.close()
        return None


def source_fingerprint() -> Dict[str, Any]:
    """计算本脚本的指纹（版本 + 源码 sha256），写入 meta 供长期追溯。

    :return: {"script", "version", "sha256", "schema"}
    """
    try:
        with open(os.path.abspath(__file__), "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()[:16]
    except Exception:
        digest = "unknown"
    return {"script": os.path.basename(__file__), "version": __version__,
            "sha256": digest, "schema": SCHEMA_VERSION}


def _install_signal_handlers() -> None:
    """把 SIGTERM 也转成 KeyboardInterrupt，使计划任务 kill 时能保存断点。"""
    def _handler(signum, frame):                 # pragma: no cover
        global _INTERRUPTED
        _INTERRUPTED = True
        raise KeyboardInterrupt()

    for name in ("SIGTERM", "SIGBREAK"):
        sig = getattr(signal, name, None)
        if sig is not None:
            try:
                signal.signal(sig, _handler)
            except Exception:
                pass


# ==============================================================================
# 6. 缓存层 —— 「避免重复下载」的第一层
# ==============================================================================
def cache_path(url: str) -> str:
    """URL → 缓存文件路径（sha1 前 16 位）。同 URL 永远同路径 = 天然去重。

    :param url: 完整 URL
    :return: cache/html/<sha1[:16]>.html
    """
    return os.path.join(CACHE, "html",
                        hashlib.sha1(url.encode()).hexdigest()[:16] + ".html")


MAX_RESPONSE_BYTES = 8 * 1024 * 1024
CACHE_MAX_AGE = 86400
STORE_HTTP_CACHE = True


def retry_wait(value: str, attempt: int) -> float:
    """Support Retry-After seconds and HTTP dates; cap unattended waits."""
    try:
        wait = float(value)
    except (ValueError, TypeError):
        try:
            wait = email.utils.parsedate_to_datetime(value).timestamp() - time.time()
        except (ValueError, TypeError, OverflowError):
            wait = 5 * 2 ** min(attempt, 6)
    if not math.isfinite(wait):
        wait = 5 * 2 ** min(attempt, 6)
    return max(1.0, min(wait, 300.0))


def fetch(url: str, delay: float, use_cache: bool = True, retries: int = 3,
          timeout: int = 30, ua: str = UA, jitter: float = 0.0) -> Tuple[str, bool]:
    """抓一个 URL。命中缓存直接返回；否则请求，带退避与拦截检测。

    :param url: 目标 URL
    :param delay: 请求间隔（秒）
    :param use_cache: 是否使用本地缓存（第二层去重）
    :param retries: 单页重试次数
    :param timeout: 单请求超时（秒）
    :param ua: User-Agent
    :param jitter: 额外随机抖动上限（秒），避免固定间隔被识别
    :return: (html_text, from_cache)
    :raises Fatal: 被拦 / 验证页（立即中止，不重试）
    :raises Unavailable: 404 / 页码越界（只跳过这一页）
    :raises RuntimeError: 重试用尽
    """
    cp = cache_path(url)

    # 缓存命中：顺带校验缓存本身没被写坏（空文件 / 半截文件）
    if (use_cache and os.path.exists(cp)
            and time.time() - os.path.getmtime(cp) <= CACHE_MAX_AGE):
        try:
            with open(cp, encoding="utf-8", errors="strict") as fh:
                cached = fh.read(MAX_RESPONSE_BYTES + 1)
            if (MIN_PAGE_BYTES <= len(cached) <= MAX_RESPONSE_BYTES
                    and "</html>" in cached.lower()
                    and not any(mk in cached[:4000].lower() for mk in BLOCK_MARKERS)):
                return cached, True
            log.warning("    [缓存损坏] %s 仅 %dB，丢弃并重新抓取", cp, len(cached))
            os.remove(cp)
        except Exception as e:
            log.warning("    [缓存读取失败] %s：%s，丢弃并重新抓取", cp, e)
            try:
                os.remove(cp)
            except Exception:
                pass

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": ua,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if urllib.parse.urlparse(resp.url).netloc != urllib.parse.urlparse(BASE).netloc:
                    raise Fatal("Unexpected cross-host redirect: %s" % resp.url)
                raw = resp.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise StructureChanged("Response exceeds 8 MiB safety limit: %s" % url)
                body = raw.decode("utf-8", errors="replace")

        except urllib.error.HTTPError as e:
            last_err = "HTTP %s" % e.code
            if e.code in (401, 403, 451):                 # 被封 → 立即中止
                raise Fatal("被封禁 HTTP %s: %s" % (e.code, url)) from e
            if e.code == 404:                             # 页码越界 → 只跳过
                raise Unavailable("页面不存在 HTTP 404: %s" % url) from e
            if e.code in (429, 503):                      # 限流 → 读 Retry-After 退避
                wait = retry_wait(e.headers.get("Retry-After", ""), attempt)
                log.warning("    [限流 %s] 等待 %ss 后重试 (%s/%s)",
                            e.code, wait, attempt, retries)
                if attempt >= retries:
                    raise TransientFailure("HTTP %s: %s" % (e.code, url), wait) from e
                time.sleep(wait)
                continue
            log.warning("    [HTTP %s] 重试 (%s/%s)", e.code, attempt, retries)
            if attempt < retries:
                time.sleep(2 ** attempt)
            continue

        except (urllib.error.URLError, socket.timeout, TimeoutError, OSError,
                http.client.IncompleteRead, http.client.RemoteDisconnected) as e:
            last_err = str(e)
            log.warning("    [网络错误] %s  重试 (%s/%s)", e, attempt, retries)
            if attempt < retries:
                time.sleep(2 ** attempt)
            continue

        # --- 拦截指纹（确定被封，立即中止）---
        if any(mk in body[:4000].lower() for mk in BLOCK_MARKERS):
            raise Fatal("出现验证页/拦截指纹: %s" % url)

        # --- 空响应 / 页面过短：软限流，退避重试而非中止 ---
        if len(body) < MIN_PAGE_BYTES or "</html>" not in body.lower():
            last_err = "响应过短(%dB)" % len(body)
            wait = 2 ** attempt * 3
            log.warning("    [%s] 疑似软限流，等待 %ss 后重试 (%s/%s)",
                        last_err, wait, attempt, retries)
            if attempt >= retries:
                raise TransientFailure("%s: %s" % (last_err, url), wait)
            time.sleep(wait)
            continue

        if STORE_HTTP_CACHE:
            atomic_write(cp, body)
        # 严格串行 + 固定间隔 + 随机抖动 = 避免触发限流
        time.sleep(delay + (random.uniform(0, jitter) if jitter > 0 else 0.0))
        return body, False

    raise RuntimeError("抓取失败（%s）: %s" % (last_err, url))


# ==============================================================================
# 7. robots.txt —— 实时判定，不靠硬编码
# ==============================================================================
def parse_robots(text: str) -> List[Dict[str, Any]]:
    """解析 robots.txt 为 [{uas:[...], rules:[(kind, path)]}, ...]。

    :param text: robots.txt 原文
    :return: 规则组列表
    """
    groups: List[Dict[str, Any]] = []
    cur: Optional[Dict[str, Any]] = None
    for raw in text.splitlines():
        line = raw.split("#")[0].strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip().lower(), v.strip()
        if k == "user-agent":
            if cur is None or cur["rules"]:            # 连续 UA 行共享一个组
                cur = {"uas": [], "rules": []}
                groups.append(cur)
            cur["uas"].append(v.lower())
        elif k in ("allow", "disallow") and cur is not None:
            cur["rules"].append((k, v))
    return groups


def robots_allowed(text: str, ua: str, path: str = "/") -> Tuple[bool, str]:
    """判定某 UA 访问某路径是否被 robots.txt 允许（最长路径匹配优先）。

    :param text: robots.txt 原文
    :param ua: User-Agent
    :param path: 待判定的路径
    :return: (allowed, 说明)
    """
    groups = parse_robots(text)
    ua_l = ua.lower()

    chosen = None
    for g in groups:                                   # 先找具体 UA 匹配
        if any(tok and tok != "*" and tok in ua_l for tok in g["uas"]):
            chosen = g
            break
    if chosen is None:                                 # 再退到 *
        for g in groups:
            if "*" in g["uas"]:
                chosen = g
                break
    if chosen is None:
        return True, "robots.txt 无适用规则 → 默认允许"

    best_kind, best_len, best_pat = None, -1, None
    for kind, p in chosen["rules"]:
        if p == "":                                    # 空 Disallow = 允许全部
            matched = False
        elif p == "/":
            matched = True
        else:
            pattern = re.escape(p).replace(r"\*", ".*")
            if p.endswith("$"):
                pattern = pattern[:-2] + "$"
            matched = bool(re.match(pattern, path))
        if matched and (len(p) > best_len or (len(p) == best_len and kind == "allow")):
            best_kind, best_len, best_pat = kind, len(p), p
    if best_kind is None:
        return True, "无匹配规则 → 允许"
    return best_kind == "allow", "命中 %s: %s" % (best_kind.upper(), best_pat)


def check_robots(ua: str = UA, timeout: int = 15) -> Tuple[Optional[bool], str, str]:
    """抓取并判定 robots.txt。

    :return: (allowed|None, 说明, 原文)；allowed 为 None 表示无法获取
    """
    try:
        req = urllib.request.Request(BASE + "/robots.txt", headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            payload = r.read(1024 * 1024 + 1)
            if len(payload) > 1024 * 1024:
                raise ValueError("robots.txt exceeds size limit")
            raw = payload.decode("utf-8", errors="strict")
            if "user-agent:" not in raw.lower() or "<html" in raw.lower():
                raise ValueError("robots.txt is empty or not a robots document")
    except Exception as e:
        return None, "无法获取 robots.txt：%s" % e, ""
    allowed, detail = robots_allowed(raw, ua, "/cat/")
    return allowed, detail, raw


# ==============================================================================
# 8. 索引 —— 站点结构（先索引后抓取）
# ==============================================================================
def build_index(delay: float, use_cache: bool = True, retries: int = 3,
                timeout: int = 30, ua: str = UA,
                jitter: float = 0.0) -> Dict[str, Any]:
    """抓首页拿到全部分类，并探测每个分类的总页数。结果存 cache/index.json。

    :return: {"fetched_at", "base", "categories":[{name,url,pages}], "skipped":[...]}
    """
    log.info("[阶段 1] 索引站点结构")
    log.info("  首页 %s/", BASE)
    home, cached = fetch(BASE + "/", delay, use_cache, retries, timeout, ua, jitter)
    log.info("    -> %dB %s", len(home), "(缓存)" if cached else "(新抓)")

    cats = sorted(set(CAT_RE.findall(home)))
    log.info("  发现分类 %d 个", len(cats))

    index: Dict[str, Any] = {"schema": SCHEMA_VERSION,
                             "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                             "base": BASE, "categories": [], "skipped": []}
    for i, path in enumerate(cats, 1):
        url = BASE + path
        try:
            body, c2 = fetch(url, delay, use_cache, retries, timeout, ua, jitter)
            pages = [int(x) for x in PAGES_RE.findall(body)]
            total = max(pages) if pages else 1
        except Fatal:
            raise
        except (Unavailable, RuntimeError) as e:
            index["skipped"].append({"path": path, "reason": str(e)})
            log.warning("    [%d/%d] %s 失败: %s", i, len(cats), path, e)
            continue
        index["categories"].append({
            "name": path.strip("/").split("/")[-1], "url": url, "pages": total,
        })
        log.info("    [%d/%d] %-45s %5d 页%s", i, len(cats),
                 index["categories"][-1]["name"], total, " (缓存)" if c2 else "")

    atomic_write(INDEX_PATH, json.dumps(index, ensure_ascii=False, indent=2))
    log.info("  索引已存 -> %s（有效分类 %d 个，跳过 %d 个）",
             INDEX_PATH, len(index["categories"]), len(index["skipped"]))
    return index


def load_index() -> Optional[Dict[str, Any]]:
    """读取索引。损坏/缺失时返回 None（自动回退到重建，而不是崩溃）。

    :return: 索引 dict 或 None
    """
    if not os.path.exists(INDEX_PATH):
        return None
    try:
        with open(INDEX_PATH, encoding="utf-8") as fh:
            idx = json.load(fh)
        if not isinstance(idx, dict) or not idx.get("categories"):
            raise ValueError("索引内容为空或结构不符")
        return idx
    except Exception as e:
        log.warning("[阶段 1] 索引文件损坏(%s)，将自动重建：%s", INDEX_PATH, e)
        try:
            os.replace(INDEX_PATH, INDEX_PATH + ".corrupt")
            log.warning("  已将损坏索引改名保留 -> %s.corrupt", INDEX_PATH)
        except Exception:
            pass
        return None


# ==============================================================================
# 9. 清单 manifest —— 顺序下载的「账本」+ 完整性校验
# ==============================================================================
def load_manifest() -> Dict[str, Any]:
    """读取抓取清单。损坏时返回空清单（不崩溃）。

    :return: {"schema", "created", "updated", "pages": {url: {...}}}
    """
    if not os.path.exists(MANIFEST_PATH):
        return {"schema": SCHEMA_VERSION,
                "created": time.strftime("%Y-%m-%d %H:%M:%S"),
                "updated": None, "pages": {}}
    try:
        with open(MANIFEST_PATH, encoding="utf-8") as fh:
            m = json.load(fh)
        if not isinstance(m, dict) or "pages" not in m:
            raise ValueError("manifest 结构不符")
        return m
    except Exception as e:
        log.warning("[清单] 读取失败(%s)，已备份并重建：%s", MANIFEST_PATH, e)
        try:
            os.replace(MANIFEST_PATH, MANIFEST_PATH + ".corrupt")
        except Exception:
            pass
        return {"schema": SCHEMA_VERSION,
                "created": time.strftime("%Y-%m-%d %H:%M:%S"),
                "updated": None, "pages": {}}


def save_manifest(manifest: Dict[str, Any]) -> None:
    """保存清单（原子写）。"""
    manifest["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    manifest["schema"] = SCHEMA_VERSION
    try:
        atomic_write(MANIFEST_PATH, json.dumps(manifest, ensure_ascii=False, indent=2))
    except Exception as e:
        log.warning("[清单] 保存失败（不影响本次运行）：%s", e)


def record_page(manifest: Dict[str, Any], url: str, cat: str, page: int,
                body: str, rows: int, mobiles: int, from_cache: bool) -> None:
    """把一次页面抓取记入清单 —— 这是「顺序检验」的数据来源。

    :param manifest: 清单 dict（原地修改）
    :param url: 页面 URL
    :param cat: 分类名
    :param page: 页码（1 起）
    :param body: 页面内容
    :param rows: 解析出的总条数
    :param mobiles: 其中 01X 手机号条数
    :param from_cache: 是否来自缓存
    """
    manifest["pages"][url] = {
        "cat": cat, "page": page, "at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "bytes": len(body), "rows": rows, "mobiles": mobiles,
        "sha1": hashlib.sha1(body.encode("utf-8", "ignore")).hexdigest()[:16],
        "from_cache": from_cache,
    }


def coverage_report(index: Optional[Dict[str, Any]],
                    manifest: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """按分类统计清单覆盖情况，找出缺口 —— 「避免找不到资料」的核心检验。

    :param index: 站点索引（提供每个分类的总页数）
    :param manifest: 抓取清单；None 时自动读取
    :return: {"categories":[{name,total_pages,downloaded,page_list,gaps,coverage_pct}],
              "totals":{...}}
    """
    manifest = manifest if manifest is not None else load_manifest()
    pages = manifest.get("pages", {})

    by_cat: Dict[str, Set[int]] = {}
    for meta in pages.values():
        by_cat.setdefault(meta["cat"], set()).add(int(meta["page"]))

    cats_out: List[Dict[str, Any]] = []
    total_pages = total_dl = 0

    known = {c["name"]: c["pages"] for c in (index or {}).get("categories", [])}
    names = sorted(set(list(known.keys()) + list(by_cat.keys())))

    for name in names:
        expect = int(known.get(name, 0))
        got = sorted(by_cat.get(name, set()))
        gaps: List[Any] = []
        if expect > 0:
            have = set(p for p in got if 1 <= p <= expect)
            hi = max(have) if have else 0
            gaps = [p for p in range(1, hi + 1) if p not in have]
            if expect > hi:
                gaps.append("%d-%d(未抓)" % (hi + 1, expect))
            got = sorted(have)
        cats_out.append({
            "name": name,
            "total_pages": expect,
            "downloaded": len(got),
            "page_list": got,
            "gaps": gaps,
            "coverage_pct": round(100.0 * len(got) / expect, 2) if expect else 0.0,
        })
        total_pages += expect
        total_dl += len(got)

    return {
        "categories": cats_out,
        "totals": {
            "categories": len(cats_out),
            "pages_total": total_pages,
            "pages_downloaded": total_dl,
            "coverage_pct": round(100.0 * total_dl / total_pages, 3) if total_pages else 0.0,
        },
    }


# ==============================================================================
# 10. 断点 state —— 中断后可续跑，不丢已完成的工作
# ==============================================================================
def save_state(state: Dict[str, Any]) -> None:
    """保存断点（原子写）。失败只告警，不影响本次运行。"""
    try:
        atomic_write(STATE_PATH, json.dumps(state, ensure_ascii=False, indent=2))
    except Exception as e:
        log.warning("[状态] 保存失败（不影响本次运行）：%s", e)


def load_state() -> Optional[Dict[str, Any]]:
    """读取断点。损坏时返回 None。"""
    if not os.path.exists(STATE_PATH):
        return None
    try:
        with open(STATE_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as e:
        log.warning("[状态] 读取失败，忽略断点：%s", e)
        return None


def clear_state() -> None:
    """删除断点（达标后调用，避免下次误续跑）。"""
    try:
        if os.path.exists(STATE_PATH):
            os.remove(STATE_PATH)
    except Exception:
        pass


# ==============================================================================
# 11. 解析 —— 确定性，零 LLM
# ==============================================================================
def clean_text(s: str) -> str:
    """清洗一个 HTML 文本字段：反转义实体 → 去替换字符/控制字符 → 折叠空白。

    站点数据本身可能带 U+FFFD（编码损坏）或 &nbsp; 等实体，不清洗会污染下游。

    :param s: 原始文本
    :return: 清洗后文本
    """
    s = html.unescape(s)
    s = s.replace("\ufffd", "")
    s = "".join(ch for ch in s if ch == " " or ch.isprintable())
    return " ".join(s.split()).strip()


def parse_rows(body: str) -> List[Tuple[str, str, str, str, str]]:
    """确定性解析一页 HTML。

    :param body: 页面 HTML
    :return: [(公司名, 地址, 电话数字, 电话显示, 详情链接)]
             电话数字一律取 href="tel:" 里的纯数字（显示文本可能带乱码）
    """
    parser = DirectoryParser()
    parser.feed(body)
    parser.close()
    return parser.rows


def normalize_phone(value: str) -> str:
    """Normalize tel URI; preserve malformed values for rejection, not guessing."""
    value = urllib.parse.unquote(html.unescape(value)).strip()
    value = re.sub(r"^tel:", "", value, flags=re.I)
    value = re.sub(r"[\s().-]", "", value)
    if not re.fullmatch(r"\+?\d*", value):
        return value
    if value.startswith("+60"):
        value = "0" + value[3:]
    elif value.startswith("0060"):
        value = "0" + value[4:]
    elif value.startswith("60") and 10 <= len(value) <= 12:
        value = "0" + value[2:]
    return value


class DirectoryParser(HTMLParser):
    """Parse each list item in isolation; ignore Next.js script duplicates."""
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: List[Tuple[str, str, str, str, str]] = []
        self.row_count = 0
        self._row: Optional[Dict[str, Any]] = None
        self._stack: List[Tuple[str, str]] = []
        self._ignored = 0

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag in ("script", "style"):
            self._ignored += 1
            return
        if self._ignored:
            return
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if tag == "li" and "row-item" in classes:
            if self._row is not None:
                raise StructureChanged("Nested/unclosed row-item")
            self.row_count += 1
            self._row = {"name": [], "addr": [], "disp": [], "tel": "", "link": ""}
            self._stack = [("li", "")]
            return
        if self._row is None or tag in ("br", "hr", "img", "input", "meta", "link", "wbr", "source"):
            return
        field = self._stack[-1][1] if self._stack else ""
        href = a.get("href") or ""
        if tag == "a" and href.startswith("/item/"):
            self._row["link"] = href
            field = "name"
        elif tag == "a" and href.lower().startswith("tel:"):
            self._row["tel"] = normalize_phone(href)
            field = "disp"
        elif "row-meta" in classes:
            field = "addr"
        self._stack.append((tag, field))

    def handle_data(self, data: str) -> None:
        if self._ignored or self._row is None or not self._stack:
            return
        field = self._stack[-1][1]
        if field:
            self._row[field].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self._ignored = max(0, self._ignored - 1)
            return
        if self._ignored or self._row is None:
            return
        if tag == "li":
            r = self._row
            if r["link"] and clean_text("".join(r["name"])):
                self.rows.append((clean_text("".join(r["name"])),
                                  clean_text("".join(r["addr"])), r["tel"],
                                  clean_text("".join(r["disp"])), r["link"]))
            self._row = None
            self._stack = []
            return
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == tag:
                del self._stack[i:]
                break

    def close(self) -> None:
        super().close()
        if self._row is not None:
            raise StructureChanged("Truncated/unclosed row-item")


# ==============================================================================
# 12. 调度 —— 顺序 / 随机 两种遍历策略
# ==============================================================================
def iter_plan(index: Dict[str, Any], order: str, seed: int,
              cats_filter: Optional[Sequence[str]] = None,
              from_page: int = 1,
              to_page: Optional[int] = None,
              per_cat: int = 0,
              cat_counts: Optional[Dict[str, int]] = None
              ) -> Iterator[Tuple[Dict[str, Any], int, str]]:
    """生成待抓页面计划（确定性；同 seed 同顺序）。

    :param index: 站点索引
    :param order: "sequential"（按分类顺序 + 页码升序）或 "random"（分类打乱 + 每类随机一页）
    :param seed: 随机种子
    :param cats_filter: 只抓这些分类（None = 全部）
    :param from_page: 起始页码（含）
    :param to_page: 结束页码（含）；None = 到该分类末页
    :param per_cat: 单分类配额；<=0 表示不限。配额只影响「要不要继续排该分类的页」，
                    不改变分类与页码的先后顺序（顺序模式的可预期性由此保证）。
    :param cat_counts: 调用方持有的「每分类已得条数」实时字典。本函数是惰性生成器，
                       每次恢复执行时读取该字典的最新值，因此抓取过程中一旦某分类达标，
                       后续属于该分类的页会被自动跳过 —— 这就是「配额跨页生效」的实现。
    :return: 迭代 (分类 dict, 页码, URL)
    """
    cats = [c for c in index["categories"] if c["pages"] >= 1]
    if cats_filter:
        wanted = {c.strip() for c in cats_filter if c.strip()}
        cats = [c for c in cats if c["name"] in wanted]

    rng = random.Random(seed)
    quota = per_cat if per_cat and per_cat > 0 else 0      # 0 = 不限
    counts = cat_counts if cat_counts is not None else {}

    def _saturated(cat_name: str) -> bool:
        """该分类是否已达配额（配额为 0 时永不饱和）。"""
        return quota > 0 and counts.get(cat_name, 0) >= quota

    if order == "random":
        rng.shuffle(cats)
        for cat in cats:
            if _saturated(cat["name"]):
                continue
            lo = max(1, from_page)
            hi = min(cat["pages"], to_page or cat["pages"])
            if hi < lo:
                continue
            page_no = rng.randint(lo, hi)
            url = "%spage/%d/" % (cat["url"], page_no) if page_no > 1 else cat["url"]
            yield cat, page_no, url
    else:                                   # sequential：严格按站点结构顺序
        for cat in cats:                    # 分类顺序 = 索引里的排序（字母序）
            if _saturated(cat["name"]):     # 该分类已达标 → 整类跳过，把页预算让给下一个分类
                continue
            lo = max(1, from_page)
            hi = min(cat["pages"], to_page or cat["pages"])
            for page_no in range(lo, hi + 1):
                if _saturated(cat["name"]):  # 同类内达标 → 提前收尾，换下一分类
                    break
                url = "%spage/%d/" % (cat["url"], page_no) if page_no > 1 else cat["url"]
                yield cat, page_no, url


def scrape(index: Dict[str, Any], target: int, max_pages: int, per_cat: int,
           delay: float, seed: int, order: str = "random",
           cats_filter: Optional[Sequence[str]] = None,
           from_page: int = 1, to_page: Optional[int] = None,
           use_cache: bool = True, retries: int = 3, timeout: int = 30,
           ua: str = UA, jitter: float = DEFAULT_JITTER,
           resume: bool = False, max_minutes: Optional[float] = None
           ) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    """执行抓取：按计划遍历页面 → 解析 → 去重 → 落断点与清单。

    :param target: 目标手机号条数
    :param max_pages: 最多抓多少页（安全阀）
    :param per_cat: 单分类最多贡献多少条（强制跨类型）
    :param order: "sequential" 或 "random"
    :param max_minutes: 时间预算（分钟）；None = 不限
    :return: (结果行列表, 统计 dict)
    :raises Fatal / StructureChanged
    """
    results: List[Dict[str, str]] = []
    seen_tel: Set[str] = set()
    seen_url: Set[str] = set()
    cat_counts: Dict[str, int] = {}          # 每个分类已贡献多少条（per_cat 的真实依据）
    fetched_pages = empty_pages = 0
    used_cats: Set[str] = set()
    reused_pages = 0
    unlimited = per_cat <= 0                 # per_cat=0 表示不限（顺序全量抓时用）

    manifest = load_manifest()

    if resume:
        st = load_state()
        if st and st.get("seed") == seed and st.get("target") == target:
            results = st.get("results", [])
            seen_tel = set(st.get("seen_tel", []))
            seen_url = set(st.get("seen_url", []))
            fetched_pages = st.get("fetched_pages", 0)
            used_cats = set(r["category"] for r in results)
            for r in results:                # 续跑时重建每分类计数
                cat_counts[r["category"]] = cat_counts.get(r["category"], 0) + 1
            log.info("[阶段 2] 断点续跑：已有 %d 条 / 已抓 %d 页，继续…",
                     len(results), fetched_pages)
        else:
            log.warning("[阶段 2] 断点与当前参数不匹配，忽略断点，从头开始")

    log.info("\n[阶段 2] %s抓取（seed=%s，目标 %s 条，每分类上限 %s，页上限 %s）",
             "顺序" if order == "sequential" else "随机",
             seed, target, "不限" if unlimited else per_cat, max_pages)
    if order == "sequential":
        log.info("        顺序模式：按分类顺序 → 页码升序，可配合 --coverage 校验完整性")

    state: Dict[str, Any] = {
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"), "seed": seed,
        "target": target, "max_pages": max_pages, "per_cat": per_cat, "order": order,
    }
    deadline = time.time() + max_minutes * 60 if max_minutes else None

    for cat, page_no, url in iter_plan(index, order, seed, cats_filter,
                                       from_page, to_page, per_cat, cat_counts):
        if _INTERRUPTED:
            raise KeyboardInterrupt()
        if len(results) >= target or fetched_pages >= max_pages:
            break
        if deadline and time.time() > deadline:
            log.warning("  [时间预算] 已达 --max-minutes 上限，停止抓取并保存断点")
            break

        # ---- 第二层去重：清单/本次已抓过的 URL 直接跳过（连缓存都不查）----
        if url in seen_url:
            continue

        try:
            body, cached = fetch(url, delay, use_cache, retries, timeout, ua, jitter)
        except Fatal as e:
            log.error("  ✗ %s p%s: %s", cat["name"], page_no, e)
            log.error("    → 判定被封/出现验证页，中止抓取。退出码 %d。", EXIT_BLOCKED)
            _persist(state, results, seen_tel, seen_url, fetched_pages, cat, page_no, url)
            save_manifest(manifest)
            raise
        except (Unavailable, RuntimeError) as e:
            log.warning("  – %s p%s: %s → 跳过该页", cat["name"], page_no, e)
            continue

        if cached:
            reused_pages += 1

        rows = parse_rows(body)
        fetched_pages += 1
        if rows:
            seen_url.add(url)
            empty_pages = 0

        # ---- 结构校验（抗混淆 / 抗改版）----
        if not rows:
            empty_pages += 1
            log.warning("  ⚠ %s p%s: %dB 却解析出 0 条 → 疑似改版或混淆",
                        cat["name"], page_no, len(body))
            if empty_pages >= 3:
                _persist(state, results, seen_tel, seen_url, fetched_pages,
                         cat, page_no, url)
                save_manifest(manifest)
                raise StructureChanged(
                    "连续 %d 页解析为空，判定站点结构已变，请更新 ROW_RE。" % empty_pages)
            continue

        got = 0
        for name, addr, tel, disp, link in rows:
            # ---- 配额判定以「分类累计条数」为准（跨页生效），而不是本页条数 ----
            if not unlimited and cat_counts.get(cat["name"], 0) >= per_cat:
                break                              # 该分类已达上限，换下一个分类
            if len(results) >= target:             # 总量达标 → 不再多吃，保证产出条数可预期
                break
            if not MOBILE_RE.fullmatch(tel):       # 只要 01X 手机
                continue
            if tel in seen_tel:                    # 第三层去重：电话级
                continue
            seen_tel.add(tel)
            results.append({
                "company": name, "phone": tel, "display": disp,
                "category": cat["name"], "address": addr,
                "detail_url": BASE + link, "source_page": url,
            })
            cat_counts[cat["name"]] = cat_counts.get(cat["name"], 0) + 1
            got += 1
        if got:
            used_cats.add(cat["name"])

        mobiles = sum(1 for r in rows if MOBILE_RE.fullmatch(r[2]))
        record_page(manifest, url, cat["name"], page_no, body, len(rows), mobiles, cached)

        log.info("  ✓ %-42s p%-4s 解析 %2d 条 / 新增手机 %2d 条 (累计 %d / 本类 %d)%s",
                 cat["name"], page_no, len(rows), got, len(results),
                 cat_counts.get(cat["name"], 0),
                 " [缓存]" if cached else "")

        _persist(state, results, seen_tel, seen_url, fetched_pages, cat, page_no, url)
        save_manifest(manifest)

    log.info("\n[阶段 3] 完成：抓 %d 页（其中 %d 页复用缓存），覆盖 %d 个分类，"
             "得 %d 条唯一手机号", fetched_pages, reused_pages, len(used_cats), len(results))
    save_manifest(manifest)
    return results, {"fetched_pages": fetched_pages, "reused_pages": reused_pages,
                     "categories": sorted(used_cats),
                     "manifest_pages": len(manifest.get("pages", {}))}


def _persist(state: Dict[str, Any], results: List[Dict[str, str]], seen_tel: Set[str],
             seen_url: Set[str], fetched_pages: int, cat: Dict[str, Any],
             page_no: int, url: str) -> None:
    """把当前进度落盘，供 --resume 续跑。"""
    st = dict(state)
    st.update({
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "fetched_pages": fetched_pages,
        "last_cat": cat["name"], "last_page": page_no, "last_url": url,
        "seen_url": sorted(seen_url), "seen_tel": sorted(seen_tel),
        "results": results,
    })
    save_state(st)


# ==============================================================================
# 13. 输出保护 + CSV 写入
# ==============================================================================
def guard_output(path: str, force: bool, append: bool,
                 new_rows: int) -> Optional[str]:
    """输出保护：防止误写 / 误覆盖。返回 None 表示放行，否则返回拒绝原因。

    规则：
      1. 文件已存在且未给 --force / --append → 拒绝
      2. 文件已存在，旧行数 > 0，新行数 < 旧行数 * 0.5 且未给 --force → 拒绝（缩水守卫）
      3. --append 模式下新行数为 0 → 拒绝（无事可做）

    :return: 拒绝原因字符串，或 None
    """
    if not os.path.exists(path):
        return None
    old_n = 0
    try:
        with open(path, encoding="utf-8-sig") as fh:
            old_n = max(0, sum(1 for _ in fh) - 1)     # 减去表头
    except Exception:
        pass

    if append:
        if new_rows == 0:
            return "追加模式但没有新记录可写"
        return None

    if force:
        if old_n and new_rows < old_n * 0.5:
            log.warning("[输出] ⚠ 缩水守卫：旧 %d 行 → 新 %d 行（已 --force，仍继续）",
                        old_n, new_rows)
        return None

    if old_n and new_rows < old_n * 0.5:
        return ("缩水守卫：新结果 %d 行 远少于 已有 %d 行，拒绝覆盖。"
                "确认无误请加 --force" % (new_rows, old_n))
    return "输出文件已存在（%d 行）。加 --force 覆盖，或 --append 追加，或改 --out" % old_n


def backup_existing(path: str) -> Optional[str]:
    """覆盖前把已有文件备份为 <名>.YYYYmmdd-HHMMSS.bak。

    :return: 备份路径；无文件或失败返回 None
    """
    if not os.path.exists(path):
        return None
    bak = "%s.%s.bak" % (os.path.splitext(path)[0], time.strftime("%Y%m%d-%H%M%S"))
    try:
        shutil.copy2(path, bak)
        log.info("[输出] 已备份旧文件 -> %s", bak)
        return bak
    except Exception as e:
        raise OutputProtected("备份失败，拒绝覆盖已有文件: %s" % e) from e


def read_existing_rows(path: str, strict: bool = False) -> List[Dict[str, str]]:
    """读取已有 CSV 的数据行（用于 --append 合并去重）。

    :param strict: True 时「读不到」直接抛 IOError，而不是当成空。
        **append 模式必须用 strict=True。**
        否则一旦旧文件读不出来（被 Excel 独占 / 编码坏了 / 列名变了），
        `old` 会变成 `[]`，合并结果只剩新行，随后整文件重写 ——
        「追加」静默退化成「覆盖」，旧数据全丢。这是最危险的一种失败。

    :raises IOError: strict=True 且读取失败 / 列与当前 schema 不符
    :return: 数据行列表（文件不存在时返回 []）
    """
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh, strict=True)
            if reader.fieldnames != CSV_COLS:
                raise IOError("CSV header mismatch: %r" % reader.fieldnames)
            rows = list(reader)
            if any(None in r or any(v is None for v in r.values()) for r in rows):
                raise IOError("CSV row width mismatch")
    except Exception as e:
        if strict:
            raise IOError("读取已有 CSV 失败（append 模式必须能读到旧数据）：%s" % e)
        log.warning("[输出] 读取旧文件失败，按空处理：%s", e)
        return []

    if rows:
        cols = [c for c in rows[0].keys() if c is not None]
        missing = [c for c in CSV_COLS if c not in cols]
        if missing:
            msg = ("已有 CSV 的列与当前 schema 不符：缺少 %s（实际列 %s）。"
                   "盲目合并会写出半空的行。" % (missing, cols))
            if strict:
                raise IOError(msg)
            log.warning("[输出] %s", msg)
    return rows


def append_merge(old: List[Dict[str, str]],
                 new: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], int]:
    """增量合并：按 phone 去重，保留旧记录，追加新记录。

    :return: (合并后列表, 新增条数)
    """
    seen = {r.get("phone", "") for r in old}
    added = 0
    merged = list(old)
    for r in new:
        if r["phone"] in seen:
            continue
        seen.add(r["phone"])
        merged.append(r)
        added += 1
    return merged, added


def write_csv(rows: List[Dict[str, str]], path: str) -> str:
    """原子写入 CSV。被占用时降级写 *_new.csv。

    :return: 实际写入路径
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLS, extrasaction="ignore")
        w.writeheader()
        for i, r in enumerate(rows, 1):
            row = {k: (r.get(k) or "") for k in CSV_COLS}
            row["no"] = i
            for key in ("company", "address", "display", "category"):
                if str(row[key]).lstrip().startswith(("=", "+", "-", "@")):
                    row[key] = "'" + str(row[key])
            w.writerow(row)
        fh.flush()
        os.fsync(fh.fileno())
    try:
        os.replace(tmp, path)
    except PermissionError:
        alt = os.path.splitext(path)[0] + "_new_%s_%s.csv" % (time.time_ns(), os.getpid())
        os.replace(tmp, alt)
        log.warning("[阶段 4] 目标文件被占用，已改写为 -> %s", alt)
        return alt
    log.info("[阶段 4] 已写入 %d 行 -> %s", len(rows), path)
    return path


def write_meta(csv_path: str, rows: List[Dict[str, str]], params: Dict[str, Any],
               exit_code: int, index: Optional[Dict[str, Any]],
               extra: Optional[Dict[str, Any]] = None) -> None:
    """写 meta 侧车文件：记录本次运行的全部参数与结果 + 脚本指纹，便于长期追溯。"""
    meta: Dict[str, Any] = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "script": source_fingerprint(),
        "csv": os.path.basename(csv_path),
        "rows": len(rows),
        "unique_phones": len({r["phone"] for r in rows}),
        "categories_covered": sorted({r["category"] for r in rows}),
        "params": params,
        "exit_code": exit_code,
        "exit_meaning": EXIT_DOC.get(exit_code, "未知"),
        "index_fetched_at": (index or {}).get("fetched_at"),
        "index_categories": len((index or {}).get("categories", [])),
        "source": BASE,
        "note": "公司名+手机号聚合数据，受 PDPA 2010 约束；"
                "仅限目录检索/研究，禁止群发/推销/转售。",
    }
    if extra:
        meta.update(extra)
    try:
        p = os.path.splitext(csv_path)[0] + ".meta.json"
        atomic_write(p, json.dumps(meta, ensure_ascii=False, indent=2))
        log.info("[阶段 4] meta 已写入 -> %s", p)
    except Exception as e:
        log.warning("[阶段 4] meta 写入失败（不影响 CSV）：%s", e)


# ==============================================================================
# 14. 模式：verify / coverage / doctor / check-robots
# ==============================================================================
def cmd_verify(path: str, probe: int = 0, timeout: int = 15, ua: str = UA,
               against: Optional[str] = None) -> int:
    """校验已有 CSV 产出质量（可离线跑）。

    :param against: 对比基线 CSV（通常是追加前的 `.bak`）。
        **这是「追加没有丢数据」的唯一机器可验证证据。**
        判定规则：基线的每一个手机号都必须仍存在于新文件中（超集关系）。
        少任何一个 → 判定为「追加把旧数据弄丢了」，退出码 6。
    :return: 退出码
    """
    log.info("[verify] 校验 %s", path)
    if not os.path.exists(path):
        log.error("  文件不存在：%s", path)
        return EXIT_ENV
    try:
        with open(path, encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
    except Exception as e:
        log.error("  读取失败：%s", e)
        return EXIT_ENV

    if not rows:
        log.error("  ✗ 文件为空")
        return EXIT_INSUFFICIENT

    problems: List[str] = []
    log.info("  行数          : %d", len(rows))
    missing = [c for c in CSV_COLS if c not in rows[0]]
    if missing:
        problems.append("缺列: %s" % missing)
    log.info("  列            : %s", ", ".join(rows[0].keys()))

    tels = [r.get("phone", "") for r in rows]
    uniq = len(set(tels))
    log.info("  唯一号码      : %d / %d", uniq, len(tels))
    if uniq != len(tels):
        problems.append("存在重复号码 %d 个" % (len(tels) - uniq))

    bad_fmt = [t for t in tels if not MOBILE_RE.fullmatch(t)]
    log.info("  格式异常(非01X): %d %s", len(bad_fmt), bad_fmt[:5])
    if bad_fmt:
        problems.append("格式异常号码 %d 个" % len(bad_fmt))

    # 前缀分布 —— 用来发现「某个号段整段缺失」（曾漏抓全部 011）
    pref: Dict[str, int] = {}
    for t in tels:
        pref[t[:3]] = pref.get(t[:3], 0) + 1
    dist = "  ".join("%s:%d" % (k, v) for k, v in sorted(pref.items()))
    log.info("  号段分布      : %s", dist or "(无)")
    log.info("  号码位数分布  : %s",
             "  ".join("%d位:%d" % (n, sum(1 for t in tels if len(t) == n))
                      for n in sorted({len(t) for t in tels})) or "(无)")

    # 分类集中度 —— 用来发现「调度把页预算全花在一个分类上」（曾产出 109 条只覆盖 1 类）
    cat_n: Dict[str, int] = {}
    for r in rows:
        c = r.get("category", "?")
        cat_n[c] = cat_n.get(c, 0) + 1
    if cat_n:
        top_cat, top_n = max(cat_n.items(), key=lambda kv: kv[1])
        ratio = 100.0 * top_n / len(rows)
        log.info("  分类集中度    : 最大 %s 占 %.1f%%（%d/%d）",
                 top_cat, ratio, top_n, len(rows))
        if len(rows) >= 20 and ratio >= 90.0:
            problems.append(
                "分类过度集中：%s 占 %.0f%%（%d 条）—— 检查 --per-cat 是否按分类生效"
                % (top_cat, ratio, top_n))

    bad_chars = []
    for r in rows:
        for col in ("company", "display", "address"):
            if any(ch == "\ufffd" or (not ch.isprintable() and not ch.isspace()) for ch in (r.get(col) or "")):
                bad_chars.append(r.get("no"))
                break
    log.info("  可疑字符记录  : %d %s", len(bad_chars), bad_chars[:5])
    if bad_chars:
        problems.append("含可疑字符记录 %d 条" % len(bad_chars))

    empty = [r.get("no") for r in rows
             if not r.get("company", "").strip() or not r.get("phone", "").strip()]
    log.info("  空关键字段    : %d", len(empty))
    if empty:
        problems.append("空关键字段 %d 条" % len(empty))

    log.info("  覆盖分类      : %d 个", len({r.get("category") for r in rows}))
    if "source_page" in rows[0]:
        log.info("  来源留痕      : %d / %d 条有 source_page",
                 sum(1 for r in rows if r.get("source_page")), len(rows))

    if probe:
        log.info("  抽样探测来源页(前 %d 条)…", probe)
        for r in rows[:probe]:
            u = r.get("source_page", "")
            try:
                req = urllib.request.Request(u, headers={"User-Agent": ua})
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    ok = resp.status == 200
                log.info("    %s %s", "OK  " if ok else "BAD ", u)
            except Exception as e:
                log.warning("    BAD  %s (%s)", u, e)
            time.sleep(1)

    # ---- 对比基线：证明「追加」没有把旧数据弄丢 ----
    if against:
        log.info("")
        log.info("  ── 与基线对比：%s", against)
        if not os.path.exists(against):
            log.error("  基线文件不存在：%s", against)
            problems.append("基线文件不存在")
        else:
            try:
                with open(against, encoding="utf-8-sig") as fh:
                    base_rows = list(csv.DictReader(fh))
            except Exception as e:
                log.error("  基线读取失败：%s", e)
                base_rows = None
                problems.append("基线读取失败")
            if base_rows is not None:
                base_tels = [r.get("phone", "") for r in base_rows]
                base_set = {t for t in base_tels if t}
                cur_set = {t for t in tels if t}
                lost = sorted(base_set - cur_set)
                gained = len(cur_set - base_set)
                log.info("  基线行数      : %d（唯一号码 %d）", len(base_rows), len(base_set))
                log.info("  新增号码      : %d", gained)
                log.info("  丢失号码      : %d %s", len(lost), lost[:10])
                if len(base_rows) > len(rows):
                    problems.append("总行数减少：基线 %d → 现在 %d"
                                    % (len(base_rows), len(rows)))
                if lost:
                    problems.append("旧号码丢失 %d 个（追加退化成覆盖？）：%s"
                                    % (len(lost), lost[:5]))
                else:
                    log.info("  ✓ 基线号码 100%% 保留（%d/%d），未发生覆盖",
                             len(base_set), len(base_set))

    if problems:
        log.error("  ✗ 发现 %d 类问题：%s", len(problems), "；".join(problems))
        return EXIT_INSUFFICIENT
    log.info("  ✓ 校验通过，未发现质量问题")
    return EXIT_OK


def cmd_coverage(index: Optional[Dict[str, Any]] = None, verbose: bool = False) -> int:
    """报告下载清单的覆盖情况与缺口 —— 「顺序检验」的落地。

    :return: 退出码（有缺口返回 6）
    """
    rep = coverage_report(index)
    t = rep["totals"]
    log.info("[coverage] 下载覆盖报告")
    log.info("  分类数        : %d", t["categories"])
    log.info("  全站总页数    : %d", t["pages_total"])
    log.info("  已下载页数    : %d", t["pages_downloaded"])
    log.info("  覆盖率        : %.3f%%", t["coverage_pct"])
    log.info("")
    log.info("  %-46s %8s %8s %7s  %s", "分类", "总页", "已下载", "覆盖", "缺口")
    log.info("  " + "-" * 100)

    has_gap = t["pages_downloaded"] < t["pages_total"] or bool((index or {}).get("skipped"))
    for c in rep["categories"]:
        if c["downloaded"] == 0 and not verbose:
            continue
        gaps = c["gaps"]
        if gaps:
            has_gap = True
        gap_s = "-" if not gaps else (", ".join(str(g) for g in gaps[:8])
                                      + (" …" if len(gaps) > 8 else ""))
        log.info("  %-46s %8d %8d %6.2f%%  %s",
                 c["name"], c["total_pages"], c["downloaded"],
                 c["coverage_pct"], gap_s)

    log.info("")
    if t["pages_downloaded"] == 0:
        log.warning("  ⚠ 尚无下载记录（cache/manifest.json 为空）。"
                    "跑一次抓取后本报告才会有数据。")
        return EXIT_INSUFFICIENT
    if has_gap:
        log.warning("  ⚠ 存在缺口。补齐方式：--order sequential 会按页码升序补齐未抓页。")
        return EXIT_INSUFFICIENT
    log.info("  ✓ 已下载页面在区间内连续，无缺口")
    return EXIT_OK


def cmd_doctor(delay: float = 1.0, timeout: int = 20, ua: str = UA,
               skip_net: bool = False, jitter: float = 0.0) -> int:
    """环境自检（无人值守定时任务的前置体检）。

    :return: 退出码
    """
    log.info("[doctor] 环境自检")
    ok_all = True

    def chk(name: str, ok: bool, detail: str = "") -> bool:
        nonlocal ok_all
        log.info("  %s %-26s %s", "PASS" if ok else "FAIL", name, detail)
        ok_all = ok_all and ok
        return ok

    v = sys.version_info
    chk("Python 版本", v >= (3, 8), "%d.%d.%d" % (v[0], v[1], v[2]))

    for name, d in (("cache", CACHE), ("logs", LOGDIR), ("data", DATADIR)):
        try:
            os.makedirs(d, exist_ok=True)
            probe = os.path.join(d, ".write_test")
            with open(probe, "w") as fh:
                fh.write("x")
            os.remove(probe)
            chk("目录可写 %s" % name, True, d)
        except Exception as e:
            chk("目录可写 %s" % name, False, str(e))

    try:
        _, _, free = shutil.disk_usage(HERE)
        chk("磁盘剩余空间", free > 100 * 1024 * 1024, "%.1f GB 可用" % (free / 1024 ** 3))
    except Exception as e:
        chk("磁盘剩余空间", False, str(e))

    lk = file_lock(LOCK_PATH + ".probe")
    if lk:
        lk.close()
        try:
            os.remove(LOCK_PATH + ".probe")
        except Exception:
            pass
        chk("互斥锁可用", True, "OS 级文件锁")
    else:
        chk("互斥锁可用", False, "无法获取锁，可能已有实例在跑")

    if skip_net:
        log.info("  SKIP 网络连通 / robots.txt / 选择器自检（--skip-net）")
        log.info("[doctor] 结论：%s", "全部通过" if ok_all else "存在失败项，请先修复")
        return EXIT_OK if ok_all else EXIT_ENV

    try:
        t0 = time.time()
        req = urllib.request.Request(BASE + "/", headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            size = len(r.read())
        chk("网络连通 %s" % BASE, size >= MIN_PAGE_BYTES,
            "%.2fs / %dB" % (time.time() - t0, size))
    except Exception as e:
        chk("网络连通 %s" % BASE, False, str(e))

    allowed, detail, raw = check_robots(ua, timeout)
    if allowed is None:
        chk("robots.txt", False, detail)
    else:
        chk("robots.txt 允许本 UA", bool(allowed), detail)
        ai_bots = [b for b in ("gptbot", "claudebot", "google-extended",
                               "ccbot", "meta-externalagent") if b in raw.lower()]
        if ai_bots:
            log.info("  INFO 站点 Disallow 的训练型 AI 爬虫: %s", ", ".join(ai_bots))

    idx = load_index()
    test_url = idx["categories"][0]["url"] if (idx and idx.get("categories")) \
        else BASE + "/cat/automotive/"
    try:
        body, cached = fetch(test_url, delay, use_cache=False, timeout=timeout,
                             ua=ua, jitter=jitter)
        rows = parse_rows(body)
        chk("选择器自检 ROW_RE", len(rows) > 0,
            "%s → 解析 %d 条%s" % (test_url, len(rows), " (缓存)" if cached else ""))
        if rows:
            mob = sum(1 for r in rows if MOBILE_RE.fullmatch(r[2]))
            log.info("  INFO 该页手机号 %d / %d 条", mob, len(rows))
    except Exception as e:
        chk("选择器自检 ROW_RE", False, str(e))

    log.info("[doctor] 结论：%s", "全部通过" if ok_all else "存在失败项，请先修复")
    return EXIT_OK if ok_all else EXIT_ENV


# ==============================================================================
# 14·B. 限流探针 —— 实测「软限流上限」与「冷却恢复曲线」
# ==============================================================================
def _raw_get(url: str, timeout: int, ua: str) -> Dict[str, Any]:
    """发一次**原始 GET，不做任何重试** —— 专供限流探针测量。

    为什么不能复用 fetch()：fetch() 内置退避重试，会把「第几次触发限流」这个
    关键信号抹掉。探针要看到原始的每一次响应，所以自己发。

    :return: {status, bytes, elapsed, error, marker}
    """
    t0 = time.time()
    req = urllib.request.Request(url, headers={
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-MY,en;q=0.9",
        "Connection": "close",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            status = resp.status
        low = body[:4000].decode("utf-8", "replace").lower()
        marker = next((m for m in BLOCK_MARKERS if m in low), None)
        return {"status": status, "bytes": len(body),
                "elapsed": round(time.time() - t0, 3), "error": None, "marker": marker}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "bytes": 0, "elapsed": round(time.time() - t0, 3),
                "error": "HTTP %d" % e.code, "marker": None}
    except Exception as e:
        return {"status": None, "bytes": 0, "elapsed": round(time.time() - t0, 3),
                "error": type(e).__name__, "marker": None}


def _classify_probe(r: Dict[str, Any]) -> str:
    """把一次探测结果归类。

    ok       正常（200 且 >= MIN_PAGE_BYTES）
    soft     **软限流**：200 但响应过短/为空 —— 本项目的核心观察对象
    blocked  硬封禁：401/403/451 或 Cloudflare 挑战指纹
    notfound 404（页码越界，与限流无关）
    error    其他异常
    """
    if r["marker"]:
        return "blocked"
    if r["status"] in (401, 403, 451):
        return "blocked"
    if r["status"] == 404:
        return "notfound"
    if r["status"] != 200:
        return "error"
    return "ok" if r["bytes"] >= MIN_PAGE_BYTES else "soft"


def _probe_urls(index: Optional[Dict[str, Any]], count: int) -> List[str]:
    """挑一批**深页** URL 做探测（深页几乎不会被缓存命中，必须走网络）。"""
    urls: List[str] = []
    for c in (index or {}).get("categories", []):
        if c["pages"] >= 8:
            urls.append("%spage/%d/" % (c["url"], min(c["pages"], 60)))
    if not urls:                                   # 索引不可用时的兜底
        urls = [BASE + "cat/%s/page/30/" % n for n in
                ("automotive", "hotels", "legal", "plastics", "property")]
    while len(urls) < count:                       # 不够就循环复用
        urls = urls + urls
    return urls[:count]


def cmd_stress_test(index: Optional[Dict[str, Any]], burst: int, burst_delay: float,
                    cooldown_max: int, rate_intervals: Sequence[float],
                    rate_n: int, timeout: int, ua: str,
                    max_requests: int = 400, rate_gap: int = 30,
                    backoff: Sequence[int] = (6, 12, 24),
                    backoff_rounds: int = 4,
                    recover_streak: int = 3) -> int:
    """实测站点的限流上限与恢复曲线，并把结论写成 JSON 报告。

    四个阶段：
      A. 突发测试   —— 以固定小间隔连发，看软限流**何时开始、以什么形态出现**
      B. 冷却曲线   —— 撞墙后按递增间隔重探，测「多久**稳定**恢复正常」
                       （必须连续 N 次成功才算恢复；单次成功只是运气）
      C. 稳态速率   —— 每个候选间隔之间插入固定冷却，测各间隔的软限流比例
      D. 退避修复   —— 复现脚本内置的退避重试（默认 6s→12s→24s），
                       实测**这套修复方案能把多少软限流吸收掉** —— 这是关键结论

    :param burst: 阶段 A 的连发次数
    :param burst_delay: 阶段 A 的请求间隔（秒）
    :param cooldown_max: 阶段 B 最长冷却观察时间（秒）
    :param rate_intervals: 阶段 C 要测的请求间隔列表
    :param rate_n: 阶段 C 每个间隔发多少次
    :param max_requests: 总请求硬上限（安全阀，防跑飞）
    :param rate_gap: 阶段 C 各间隔之间的冷却秒数（消除「先测的占便宜」的顺序效应）
    :param backoff: 阶段 D 复现的退避表（应与 fetch() 内置的一致）
    :param backoff_rounds: 阶段 D 的轮数
    :param recover_streak: 阶段 B 判定「稳定恢复」所需的连续成功次数
    :return: 退出码
    """
    sent = 0

    def _guard() -> bool:
        if sent >= max_requests:
            log.error("[stress] 已达总请求硬上限 %d，停止探测", max_requests)
            return False
        return True

    log.info("[stress] 限流探针启动")
    log.info("         阶段 A 突发：%d 次 @ %.2fs 间隔", burst, burst_delay)
    log.info("         阶段 B 冷却：最长观察 %ds，需连续 %d 次成功才算恢复",
             cooldown_max, recover_streak)
    log.info("         阶段 C 稳态：间隔 %s，各 %d 次（间隔间冷却 %ds）",
             ", ".join("%.1fs" % v for v in rate_intervals), rate_n, rate_gap)
    log.info("         阶段 D 退避：复现 %s，%d 轮",
             "→".join("%ds" % b for b in backoff), backoff_rounds)
    log.info("         总请求硬上限：%d\n", max_requests)

    # ---- 基线：先等到站点「干净」再开始，否则测到的是上一轮的余温 ----
    # 用真实分类深页做基线（不用首页）—— 首页可能走 CDN 缓存，掩盖限流。
    urls = _probe_urls(index, max(burst, 5))
    base_url = urls[0]
    log.info("[stress] 基线 URL：%s", base_url)
    log.info("[stress] 等待基线恢复（需连续 %d 次成功）…", recover_streak)
    baseline_ok = False
    waited = 0
    streak = 0
    while waited <= 90 and _guard():
        r = _raw_get(base_url, timeout, ua)
        sent += 1
        if _classify_probe(r) == "ok":
            streak += 1
            if streak >= recover_streak:
                baseline_ok = True
                log.info("        基线正常：连续 %d 次成功（已等待 %ds）", streak, waited)
                break
        else:
            streak = 0
            log.info("        基线仍被限流（%dB），等 15s 再试…", r["bytes"])
            time.sleep(15)
            waited += 15
    if not baseline_ok:
        log.warning("[stress] ⚠ 90s 内基线未稳定恢复，测量结果会偏悲观（继续，但请留意）")

    report: Dict[str, Any] = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "base": BASE, "ua": ua,
        "params": {"burst": burst, "burst_delay": burst_delay,
                   "cooldown_max": cooldown_max, "rate_gap": rate_gap,
                   "rate_intervals": list(rate_intervals), "rate_n": rate_n,
                   "backoff": list(backoff), "backoff_rounds": backoff_rounds,
                   "recover_streak": recover_streak},
        "baseline_ok": baseline_ok,
    }

    # ================= 阶段 A：突发测试 =================
    log.info("\n[stress] ── 阶段 A：突发测试（找软限流触发点与形态）──")
    seq: List[Dict[str, Any]] = []
    first_soft: Optional[int] = None
    for i in range(burst):
        if not _guard():
            break
        u = urls[i % len(urls)]
        r = _raw_get(u, timeout, ua)
        sent += 1
        kind = _classify_probe(r)
        seq.append({"i": i + 1, "kind": kind, "url": u, **r})
        if kind == "soft" and first_soft is None:
            first_soft = i + 1
        log.info("  #%-3d %-8s %6dB %5.2fs  %s", i + 1, kind, r["bytes"], r["elapsed"],
                 r["error"] or u.split("/cat/")[-1][:40])
        if kind == "blocked":
            log.error("  ✗ 出现硬封禁指纹，立即停止阶段 A（这是真封禁，不是软限流）")
            break
        time.sleep(burst_delay + random.uniform(0, burst_delay * 0.3))

    ok_a = sum(1 for x in seq if x["kind"] == "ok")
    soft_a = sum(1 for x in seq if x["kind"] == "soft")
    # 最长连续软限流 —— 用来区分「硬阈值撞墙」与「概率性丢弃」
    run = best_run = 0
    for x in seq:
        run = run + 1 if x["kind"] == "soft" else 0
        best_run = max(best_run, run)
    soft_ratio = round(100.0 * soft_a / len(seq), 1) if seq else 0.0
    pattern = ("scattered（概率性丢弃：限流随机穿插在正常响应之间）"
               if first_soft and best_run <= max(3, len(seq) // 6)
               else "contiguous（连续撞墙：更像硬阈值）" if first_soft
               else "none")
    report["phase_a"] = {
        "requests": len(seq), "ok": ok_a, "soft": soft_a,
        "blocked": sum(1 for x in seq if x["kind"] == "blocked"),
        "soft_ratio_pct": soft_ratio,
        "first_soft_at": first_soft,
        "longest_soft_run": best_run,
        "pattern": pattern,
        "sequence": seq,
    }
    if first_soft:
        log.info("  → 软限流首次出现在第 %d 次；共 %d/%d 次被限流（%.1f%%）",
                 first_soft, soft_a, len(seq), soft_ratio)
        log.info("  → 最长连续软限流 %d 次 → 形态：%s", best_run, pattern)
        if best_run <= 3:
            log.info("     ★ 注意：不是「跑满 N 次就封」，而是**随机丢弃**。"
                     "这类限流靠「重试」就能穿过，不该中止。")
    else:
        log.info("  → %d 次连发内未触发软限流（%.2fs 间隔可承受）", len(seq), burst_delay)

    # ================= 阶段 B：冷却恢复曲线 =================
    log.info("\n[stress] ── 阶段 B：冷却恢复曲线（需连续 %d 次成功才算真恢复）──",
             recover_streak)
    cooldown: List[Dict[str, Any]] = []
    recover_at: Optional[int] = None
    if first_soft is None:
        log.info("  未触发限流，跳过阶段 B")
        report["phase_b"] = {"skipped": True, "reason": "阶段 A 未触发软限流"}
        recover_at = 0
    else:
        t_start = time.time()
        wait = 5
        while (time.time() - t_start) <= cooldown_max and _guard():
            time.sleep(wait)
            streak = 0
            first_ok_at = None
            for _ in range(recover_streak):
                if not _guard():
                    break
                r = _raw_get(base_url, timeout, ua)
                sent += 1
                k = _classify_probe(r)
                if k == "ok":
                    streak += 1
                    if first_ok_at is None:
                        first_ok_at = int(time.time() - t_start)
                else:
                    break
                time.sleep(1.0)
            elapsed_wait = int(time.time() - t_start)
            cooldown.append({"waited_s": elapsed_wait, "streak": streak,
                             "first_ok_at_s": first_ok_at, "target": recover_streak})
            log.info("  +%-4ds → 连续成功 %d/%d", elapsed_wait, streak, recover_streak)
            if streak >= recover_streak:
                recover_at = elapsed_wait
                break
            wait = min(wait * 2, 30)
        if recover_at is None:
            log.warning("  → %ds 内未稳定恢复，冷却窗口比观察窗更长", cooldown_max)
        else:
            log.info("  → 约 %ds 后**稳定**恢复正常", recover_at)
        report["phase_b"] = {"skipped": False, "recover_after_s": recover_at,
                             "observed_max_s": int(time.time() - t_start),
                             "curve": cooldown}

    # ================= 阶段 C：稳态速率 =================
    log.info("\n[stress] ── 阶段 C：稳态速率（各间隔之间冷却 %ds 以消除顺序效应）──",
             rate_gap)
    rate_res: List[Dict[str, Any]] = []
    for idx_iv, iv in enumerate(rate_intervals):
        if not _guard():
            break
        if idx_iv > 0:                              # 消除「先测的占便宜」
            log.info("  …冷却 %ds 后测下一个间隔", rate_gap)
            time.sleep(rate_gap)
        got = {"interval": iv, "ok": 0, "soft": 0, "n": 0}
        for i in range(rate_n):
            if not _guard():
                break
            r = _raw_get(urls[(i * 3 + 1) % len(urls)], timeout, ua)
            sent += 1
            kind = _classify_probe(r)
            got["n"] += 1
            if kind == "ok":
                got["ok"] += 1
            elif kind == "soft":
                got["soft"] += 1
            if kind == "blocked":
                log.error("  ✗ 出现硬封禁，停止阶段 C")
                break
            time.sleep(iv)
        rate = round(100.0 * got["ok"] / got["n"], 1) if got["n"] else 0.0
        got["ok_pct"] = rate
        got["verdict"] = ("安全" if rate >= 95 else
                          "勉强（会间歇限流，靠重试补）" if rate >= 60 else "不可用")
        rate_res.append(got)
        log.info("  间隔 %.1fs → %d/%d 成功（%.1f%%）→ %s",
                 iv, got["ok"], got["n"], rate, got["verdict"])
    report["phase_c"] = rate_res

    # ================= 阶段 D：退避修复验证 =================
    log.info("\n[stress] ── 阶段 D：退避修复验证（复现 %s）──",
             "→".join("%ds" % b for b in backoff))
    d_res: List[Dict[str, Any]] = []
    for rd in range(backoff_rounds):
        if not _guard():
            break
        attempts = 0
        waited_s = 0
        final = "error"
        for k in range(len(backoff) + 1):
            if not _guard():
                break
            r = _raw_get(base_url, timeout, ua)
            sent += 1
            attempts += 1
            final = _classify_probe(r)
            if final == "ok":
                break
            if k < len(backoff):
                waited_s += backoff[k]
                time.sleep(backoff[k])
        d_res.append({"round": rd + 1, "attempts": attempts,
                      "waited_s": waited_s, "final": final})
        log.info("  第 %d 轮：尝试 %d 次 / 额外等待 %ds → %s",
                 rd + 1, attempts, waited_s, final)
    absorbed = sum(1 for x in d_res if x["final"] == "ok")
    d_rate = round(100.0 * absorbed / len(d_res), 1) if d_res else 0.0
    report["phase_d"] = {"rounds": d_res, "absorbed": absorbed,
                         "absorbed_pct": d_rate,
                         "avg_attempts": (round(sum(x["attempts"] for x in d_res)
                                                / len(d_res), 2) if d_res else 0)}
    log.info("  → 退避策略吸收率：%d/%d（%.1f%%），平均尝试 %.2f 次",
             absorbed, len(d_res), d_rate, report["phase_d"]["avg_attempts"])
    if d_rate >= 95:
        log.info("     ★ 结论：退避重试能可靠吸收该站的软限流 —— 不需要并发/代理。")
    elif d_rate >= 60:
        log.info("     ⚠ 结论：退避能吸收大部分，但仍会漏。建议加大 --delay 并提高 --retries。")
    else:
        log.info("     ✗ 结论：退避不足以吸收，需要显著加大 --delay（并考虑错峰运行）。")

    report["total_requests"] = sent

    # ================= 结论 =================
    safe = [x for x in rate_res if x["ok_pct"] >= 95]
    near = [x for x in rate_res if 60 <= x["ok_pct"] < 95]
    log.info("\n[stress] ══ 结论 ══")
    log.info("  总请求数            : %d", sent)
    log.info("  阶段 A 软限流形态   : %s（%d/%d 次，最长连续 %d）",
             "分散概率性" if "scattered" in pattern else
             ("连续撞墙" if first_soft else "未触发"),
             soft_a, len(seq), best_run)
    log.info("  阶段 B 稳定恢复     : %s",
             "%ds" % recover_at if recover_at is not None else "未在观察窗内恢复")
    log.info("  阶段 C 各间隔成功率 : %s",
             "  ".join("%.1fs=%.0f%%" % (x["interval"], x["ok_pct"]) for x in rate_res)
             or "(无)")
    log.info("  阶段 D 退避吸收率   : %.1f%%（平均尝试 %.2f 次）",
             d_rate, report["phase_d"]["avg_attempts"])
    if safe:
        log.info("  生产建议            : --delay %.1f（已足够，保留 --jitter）",
                 min(x["interval"] for x in safe))
    elif near:
        log.info("  生产建议            : --delay %.1f + 保留退避重试（--retries 3）",
                 min(x["interval"] for x in near) + 1.0)
    else:
        log.info("  生产建议            : --delay 5.0 起步，并务必保留退避重试")
    log.info("  一句话              : 该站限流是「200+0B 的随机丢弃」，"
             "退避重试可吸收 %.0f%%；不要把它误判成封禁。", d_rate)

    rep_path = os.path.join(DATADIR, "ratelimit-report.json")
    try:
        atomic_write(rep_path, json.dumps(report, ensure_ascii=False, indent=2))
        log.info("\n[stress] 报告已写入 -> %s", rep_path)
    except Exception as e:
        log.warning("[stress] 报告写入失败：%s", e)

    # 判定：出现硬封禁 → 4；基线一直不恢复 → 6；否则 0
    if any(x["kind"] == "blocked" for x in seq):
        return EXIT_BLOCKED
    if not baseline_ok:
        return EXIT_INSUFFICIENT
    return EXIT_OK


def cmd_self_test() -> int:
    """离线自检：对纯函数做回归测试，零网络、零副作用。

    为什么必须有：本项目曾因 `--per-cat` 被误实现成「每页上限」而非「每分类上限」，
    导致顺序模式下 14 页全花在 agricultural 一个分类上、产出 109 条只覆盖 1 个分类。
    那种 bug 跑 `--doctor`（查环境）和 `--verify`（查数据格式）都发现不了 ——
    只有对**调度语义**本身做断言才能拦住。改完代码先跑这个，再联网抓。

    :return: EXIT_OK 全通过；EXIT_STRUCTURE 有断言失败
    """
    import tempfile

    passed = failed = 0
    failures: List[str] = []

    def check(name: str, cond: bool, extra: str = "") -> None:
        nonlocal passed, failed
        if cond:
            passed += 1
            log.info("  ✓ %s", name)
        else:
            failed += 1
            failures.append(name + ((" — " + extra) if extra else ""))
            log.error("  ✗ %s %s", name, extra)

    log.info("[self-test] 离线回归测试（纯函数，零网络）\n")
    # ---------- 1. 文本清洗 ----------
    log.info("[1/10] 文本清洗 clean_text")
    raw = "  Foo &amp; Bar\ufffd  \n Baz <script>  "
    got_txt = clean_text(raw)
    check("去实体 + 去 U+FFFD + 折叠空白",
          got_txt == "Foo & Bar Baz <script>", "实际=%r" % got_txt)
    check("空串安全", clean_text("") == "")

    # ---------- 2. 手机号正则 ----------
    log.info("[2/10] 手机号正则 MOBILE_RE（10 位 01X + 11 位 011，两种都要）")
    for good, why in (("0123956969", "10 位 012"), ("0198887777", "10 位 019"),
                      ("01112345678", "11 位 011（曾漏抓）"),
                      ("01111873521", "11 位 011 真实样本"),
                      ("0164705455", "10 位 016")):
        check("接受 %s（%s）" % (good, why), bool(MOBILE_RE.fullmatch(good)))
    for bad, why in (("0322334455", "座机 03"), ("082412345", "座机 08"),
                     ("60123956969", "带国码 60"), ("1234567890", "非 01 开头"),
                     ("012395696", "9 位不完整"), ("011123456", "9 位不完整")):
        check("拒绝 %s（%s）" % (bad, why), not MOBILE_RE.fullmatch(bad))

    # ---------- 3. 行解析（ROW_RE 捕获组顺序）----------
    log.info("[3/10] 行解析 parse_rows（捕获组顺序不能错）")
    fixture = (
        '<li class="row-item"><h3><a href="/item/alpha-sdn-bhd">'
        'Alpha Sdn Bhd</a></h3>'
        '<span class="row-meta">12 Jalan Satu, 50000 KL</span>'
        '<a class="row-phone" href="tel:0123456789">012-345 6789</a></li>'
        '<li class="row-item"><h3><a href="/item/beta-enterprise">'
        'Beta Enterprise</a></h3>'
        '<span class="row-meta">9 Jalan Dua, 40000 PJ</span>'
        '<a class="row-phone" href="tel:0398765432">03-9876 5432</a></li>'
    )
    rows = parse_rows(fixture)
    check("解析出 2 条", len(rows) == 2, "实际=%d" % len(rows))
    if len(rows) == 2:
        n0, a0, t0, d0, l0 = rows[0]
        check("第 1 条公司名正确", n0 == "Alpha Sdn Bhd", "实际=%r" % n0)
        check("第 1 条地址正确", a0 == "12 Jalan Satu, 50000 KL", "实际=%r" % a0)
        check("第 1 条电话取自 tel: href", t0 == "0123456789", "实际=%r" % t0)
        check("第 1 条显示文本正确", d0 == "012-345 6789", "实际=%r" % d0)
        check("第 1 条详情链接正确", l0 == "/item/alpha-sdn-bhd", "实际=%r" % l0)
        check("第 2 条是座机（应被手机号过滤挡掉）",
              not MOBILE_RE.fullmatch(rows[1][2]))
    check("乱码页解析出 0 条而非抛异常", parse_rows("<html>nothing</html>") == [])

    # ---------- 4. 调度：顺序 + 配额（本次 bug 的回归测试）----------
    log.info("[4/10] 调度 iter_plan —— 顺序模式 + 每分类配额")
    idx = {"categories": [
        {"name": "cat-a", "url": BASE + "cat/cat-a/", "pages": 5},
        {"name": "cat-b", "url": BASE + "cat/cat-b/", "pages": 5},
        {"name": "cat-c", "url": BASE + "cat/cat-c/", "pages": 5},
    ]}
    # 4a. 无配额（per_cat=0）→ 全部 15 页都要排出
    full = [c["name"] for c, _, _ in iter_plan(idx, "sequential", 1, None, 1, None, 0, {})]
    check("per_cat=0（不限）排出全部 15 页", len(full) == 15, "实际=%d" % len(full))
    check("顺序为 a→b→c 且页码升序",
          full == ["cat-a"] * 5 + ["cat-b"] * 5 + ["cat-c"] * 5, "实际=%s" % full)

    # 4b. per_cat=2，且每页就把配额吃满 → 必须跨 3 个分类，绝不能全吃 cat-a
    counts: Dict[str, int] = {}
    consumed: List[Tuple[str, int]] = []
    for cat, page_no, _url in iter_plan(idx, "sequential", 1, None, 1, None, 2, counts):
        consumed.append((cat["name"], page_no))
        counts[cat["name"]] = counts.get(cat["name"], 0) + 2     # 一页即达标
    names_hit = {n for n, _ in consumed}
    check("配额跨页生效：不再只吃第 1 个分类", len(names_hit) == 3,
          "实际覆盖 %s" % sorted(names_hit))
    check("配额吃满后每分类只排 1 页", len(consumed) == 3, "实际=%d 页" % len(consumed))
    check("分类顺序未被破坏", [n for n, _ in consumed] == ["cat-a", "cat-b", "cat-c"],
          "实际=%s" % consumed)

    # 4c. 配额未满 → 继续排同类下一页
    counts2: Dict[str, int] = {}
    seq: List[Tuple[str, int]] = []
    for cat, page_no, _url in iter_plan(idx, "sequential", 1, None, 1, None, 5, counts2):
        seq.append((cat["name"], page_no))
        counts2[cat["name"]] = counts2.get(cat["name"], 0) + 1    # 每页只吃 1 条
        if len(seq) >= 7:
            break
    check("配额未满时同类继续翻页",
          seq[:2] == [("cat-a", 1), ("cat-a", 2)], "实际=%s" % seq[:2])
    check("cat-a 累计到 5 条后跳到 cat-b",
          ("cat-b", 1) in seq and seq.count(("cat-a", 1)) == 1, "实际=%s" % seq)

    # 4d. 分类过滤 + 页码范围
    only_b = [c["name"] for c, _, _ in iter_plan(idx, "sequential", 1, ["cat-b"],
                                                 2, 3, 0, {})]
    check("--categories 过滤 + --from-page/--to-page 生效",
          only_b == ["cat-b", "cat-b"], "实际=%s" % only_b)

    # 4e. 随机模式确定性（同 seed 同结果）
    r1 = [(c["name"], p) for c, p, _ in iter_plan(idx, "random", 42, None, 1, None, 0, {})]
    r2 = [(c["name"], p) for c, p, _ in iter_plan(idx, "random", 42, None, 1, None, 0, {})]
    check("随机模式同 seed 结果可复现", r1 == r2, "%s vs %s" % (r1, r2))
    check("随机模式每分类只取 1 页", len(r1) == 3, "实际=%d" % len(r1))

    # ---------- 5. 输出保护 guard_output ----------
    log.info("[5/10] 输出保护 guard_output")
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "t.csv")

        check("文件不存在 → 放行", guard_output(p, False, False, 10) is None)

        with open(p, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=CSV_COLS)
            w.writeheader()
            for i in range(100):
                w.writerow({k: (i if k == "no" else "x") for k in CSV_COLS})

        r = guard_output(p, False, False, 100)
        check("已存在且未 --force → 拒绝", r is not None, "实际=%r" % r)
        check("拒绝理由提到 --force", bool(r and "--force" in r), "实际=%r" % r)
        check("--force → 放行", guard_output(p, True, False, 100) is None)
        r2 = guard_output(p, False, False, 10)
        check("缩水守卫：10 行 << 100 行 → 拒绝", r2 is not None, "实际=%r" % r2)
        check("缩水理由提到「缩水」", bool(r2 and "缩水" in r2), "实际=%r" % r2)
        check("--append 空结果 → 拒绝", guard_output(p, False, True, 0) is not None)

    # ---------- 6. 增量合并 append_merge + 追加安全 ----------
    log.info("[6/10] 增量合并 append_merge（按 phone 去重）+ 追加安全")
    old = [{"phone": "0121111111", "company": "A"}]
    new = [{"phone": "0121111111", "company": "A-dup"},
           {"phone": "0122222222", "company": "B"}]
    merged, added = append_merge(old, new)
    check("重复号码不被追加", len(merged) == 2, "实际=%d" % len(merged))
    check("新增计数正确", added == 1, "实际=%d" % added)
    check("旧记录被保留（不被新值覆盖）", merged[0]["company"] == "A")
    check("旧记录排在前面（顺序不变）", [r["phone"] for r in merged] ==
          ["0121111111", "0122222222"], "实际=%s" % [r["phone"] for r in merged])
    check("全部重复时新增为 0", append_merge(old, [dict(old[0])])[1] == 0)

    with tempfile.TemporaryDirectory() as td:
        # 6a. 文件不存在 → 返回空，不报错
        p0 = os.path.join(td, "none.csv")
        check("旧文件不存在时返回空表", read_existing_rows(p0, strict=True) == [])

        # 6b. 坏编码 → strict 必须抛错（绝不能当空表，否则追加会变成覆盖）
        pbad = os.path.join(td, "bad.csv")
        with open(pbad, "wb") as fh:
            fh.write(b"\xff\xfe\x00not-a-valid-utf8-header\n")
        try:
            read_existing_rows(pbad, strict=True)
            check("坏编码 + strict → 必须抛错", False, "没有抛错")
        except IOError:
            check("坏编码 + strict → 必须抛错", True)
        except Exception as e:
            check("坏编码 + strict → 必须抛错", False, "抛了 %r" % e)
        check("坏编码 + 非 strict → 降级为空表",
              read_existing_rows(pbad, strict=False) == [])

        # 6c. 列与 schema 不符 → strict 必须抛错
        psch = os.path.join(td, "schema.csv")
        with open(psch, "w", encoding="utf-8-sig", newline="") as fh:
            fh.write("no,nama,telefon\n1,Ali,0123456789\n")
        try:
            read_existing_rows(psch, strict=True)
            check("列不符 + strict → 必须抛错", False, "没有抛错")
        except IOError:
            check("列不符 + strict → 必须抛错", True)
        except Exception as e:
            check("列不符 + strict → 必须抛错", False, "抛了 %r" % e)

        # 6d. 端到端：旧 3 行 + 新 2 行（含 1 重复）→ 合并写盘后旧行必须完好
        pe = os.path.join(td, "e2e.csv")
        old_rows = [{"company": "Old%d" % i, "phone": "012000000%d" % i,
                     "display": "012-000 000%d" % i, "category": "cat%d" % i,
                     "address": "Addr %d" % i, "detail_url": "u%d" % i,
                     "source_page": "s%d" % i} for i in range(3)]
        write_csv(old_rows, pe)
        before = read_existing_rows(pe, strict=True)
        check("写盘后能原样读回 3 行", len(before) == 3, "实际=%d" % len(before))
        new_rows = [{"company": "New1", "phone": "0120000001",       # 与旧数据重复
                     "display": "012-000 0001", "category": "cx",
                     "address": "ax", "detail_url": "ux", "source_page": "sx"},
                    {"company": "New2", "phone": "0129999999",
                     "display": "012-999 9999", "category": "cy",
                     "address": "ay", "detail_url": "uy", "source_page": "sy"}]
        merged_rows, added_rows = append_merge(before, new_rows)
        write_csv(merged_rows, pe)
        after = read_existing_rows(pe, strict=True)
        check("合并写盘后共 4 行（3 旧 + 1 新）", len(after) == 4, "实际=%d" % len(after))
        check("旧 3 行内容完好", [r["company"] for r in after[:3]] ==
              ["Old0", "Old1", "Old2"], "实际=%s" % [r["company"] for r in after[:3]])
        check("旧行全部字段未丢", all(
            after[i]["address"] == "Addr %d" % i and after[i]["detail_url"] == "u%d" % i
            for i in range(3)))
        check("no 列被重新编号为 1..4",
              [r["no"] for r in after] == ["1", "2", "3", "4"],
              "实际=%s" % [r["no"] for r in after])
        check("重复号码未被重复写入",
              sum(1 for r in after if r["phone"] == "0120000001") == 1)

        # 6e. --verify --against 基线对比：旧号码一条没丢 → 通过
        #     （cmd_verify 会打很多行日志，这里临时静音，只看退出码）
        base_csv = os.path.join(td, "base.csv")
        write_csv(old_rows, base_csv)                       # 基线 = 旧 3 行
        logging.disable(logging.CRITICAL)
        try:
            rc_ok = cmd_verify(pe, 0, 5, UA, base_csv)      # pe = 合并后 4 行
            # 6f. 反例：故意造「追加退化成覆盖」的文件 → 必须被抓住
            lost_csv = os.path.join(td, "lost.csv")
            write_csv([new_rows[1]], lost_csv)              # 只剩 1 条新数据
            rc_bad = cmd_verify(lost_csv, 0, 5, UA, base_csv)
            # 6g. 反例：基线文件不存在 → 必须报错，而不是静默通过
            rc_missing = cmd_verify(pe, 0, 5, UA, os.path.join(td, "nope.csv"))
        finally:
            logging.disable(logging.NOTSET)
        check("基线号码全保留 → --against 校验通过", rc_ok == EXIT_OK,
              "退出码=%d" % rc_ok)
        check("旧号码丢失 → --against 必须报错", rc_bad == EXIT_INSUFFICIENT,
              "退出码=%d" % rc_bad)
        check("基线不存在 → 必须报错", rc_missing == EXIT_INSUFFICIENT,
              "退出码=%d" % rc_missing)

    # ---------- 7. 覆盖率缺口计算 ----------
    log.info("[7/10] 覆盖率 coverage_report（顺序检验的核心）")
    idx_x = {"categories": [{"name": "x", "url": BASE + "cat/x/", "pages": 10}]}
    fake_manifest = {"pages": {}}
    for pg in (1, 2, 3, 5):                     # 缺 4，且 6-10 未抓
        fake_manifest["pages"]["%scat/x/page/%d/" % (BASE, pg)] = {
            "cat": "x", "page": pg, "bytes": 1, "rows": 1, "mobiles": 1}
    rep = coverage_report(idx_x, fake_manifest)
    xc = [c for c in rep["categories"] if c["name"] == "x"]
    check("识别出分类 x", len(xc) == 1)
    if xc:
        check("下载页数 = 4", xc[0]["downloaded"] == 4, "实际=%d" % xc[0]["downloaded"])
        check("缺口命中第 4 页", 4 in xc[0]["gaps"], "实际=%s" % xc[0]["gaps"])
        check("未抓区间被标注", any(isinstance(g, str) for g in xc[0]["gaps"]),
              "实际=%s" % xc[0]["gaps"])
        check("覆盖率 = 40%", abs(xc[0]["coverage_pct"] - 40.0) < 0.01,
              "实际=%s" % xc[0]["coverage_pct"])
    check("无清单时返回 0 页而非报错",
          coverage_report(idx, {"pages": {}})["totals"]["pages_downloaded"] == 0)

    # ---------- 8. 退出码表完整性 ----------
    log.info("[8/10] 退出码表与常量一致性")
    for code in (EXIT_OK, EXIT_USAGE, EXIT_ENV, EXIT_BLOCKED, EXIT_STRUCTURE,
                 EXIT_INSUFFICIENT, EXIT_OUTPUT, EXIT_LOCKED, EXIT_INTERRUPTED):
        check("EXIT_DOC 覆盖退出码 %d" % code, code in EXIT_DOC)
    check("退出码互不重复", len(set(EXIT_DOC)) == len(EXIT_DOC))

    # ---------- 9. 内置文档完整性 ----------
    log.info("[9/10] 内置文档（--manual / --examples / --print-api）")
    # 手册正文含正则花括号（如 01[0-9]{7,8}）。若误用 .format() 渲染会抛 KeyError，
    # 表现是「--manual 直接崩、退出码 1」。这里复现 main() 的渲染路径做断言。
    try:
        rendered = MANUAL.replace("{ver}", __version__)
        check("MANUAL 渲染不抛异常", True)
        check("MANUAL 已注入版本号", __version__ in rendered, "版本 %s 未出现" % __version__)
        check("MANUAL 无残留占位符", "{ver}" not in rendered)
        check("MANUAL 含关键章节",
              all(k in rendered for k in ("退出码", "内置手册", "合规红线")))
    except Exception as e:
        check("MANUAL 渲染不抛异常", False, repr(e))
    for name, doc in (("EXAMPLES", EXAMPLES), ("API_DOC", API_DOC)):
        check("%s 非空且含分隔线" % name, len(doc) > 500 and "====" in doc,
              "长度=%d" % len(doc))
    check("EXAMPLES 提到 --self-test", "--self-test" in EXAMPLES)
    check("API_DOC 提到 cmd_self_test", "cmd_self_test" in API_DOC)

    # 文件头 banner 的版本号必须与 __version__ 一致（防止两处漂移）
    try:
        with open(__file__, encoding="utf-8") as fh:
            head = fh.read(2000)
        check("文件头 banner 版本 == __version__",
              "v%s" % __version__ in head,
              "banner 未出现 v%s" % __version__)
    except Exception as e:
        check("文件头 banner 版本 == __version__", False, repr(e))

    # ---------- 10. 限流探针的分类逻辑 ----------
    log.info("[10/10] 限流探针 _classify_probe（软限流 ≠ 封禁，必须分清）")

    def _pr(status, nbytes, marker=None, error=None):
        return {"status": status, "bytes": nbytes, "elapsed": 0.1,
                "error": error, "marker": marker}

    check("200 + 40KB → ok", _classify_probe(_pr(200, 40000)) == "ok")
    check("200 + 0B → soft（软限流，不是封禁）",
          _classify_probe(_pr(200, 0)) == "soft")
    check("200 + 100B → soft（过短也算）",
          _classify_probe(_pr(200, 100)) == "soft")
    check("200 + 2999B → soft（边界）",
          _classify_probe(_pr(200, MIN_PAGE_BYTES - 1)) == "soft")
    check("200 + 3000B → ok（边界）",
          _classify_probe(_pr(200, MIN_PAGE_BYTES)) == "ok")
    for code in (401, 403, 451):
        check("%d → blocked（真封禁）" % code,
              _classify_probe(_pr(code, 0)) == "blocked")
    check("200 但含挑战指纹 → blocked",
          _classify_probe(_pr(200, 40000, marker="just a moment")) == "blocked")
    check("404 → notfound（页码越界，与限流无关）",
          _classify_probe(_pr(404, 0)) == "notfound")
    check("500 → error", _classify_probe(_pr(500, 0)) == "error")
    check("连接异常 → error", _classify_probe(_pr(None, 0, error="URLError")) == "error")

    purls = _probe_urls({"categories": [
        {"name": "a", "url": BASE + "cat/a/", "pages": 100},
        {"name": "b", "url": BASE + "cat/b/", "pages": 3},      # 太浅，应被排除
    ]}, 4)
    check("探针 URL 数量正确", len(purls) == 4, "实际=%d" % len(purls))
    check("探针优先取深页", all("/page/" in u for u in purls), "实际=%s" % purls)
    check("浅分类被排除", not any("/cat/b/" in u for u in purls))
    check("无索引时回退到内置 URL", len(_probe_urls(None, 3)) == 3)

    log.info("\n[self-test] 结果：通过 %d 项，失败 %d 项", passed, failed)
    if failures:
        log.error("[self-test] 失败清单：")
        for f in failures:
            log.error("   - %s", f)
        log.error("[self-test] 结论：有断言失败 —— 请勿联网抓取，先修复上列问题")
        return EXIT_STRUCTURE
    log.info("[self-test] 结论：全部通过，调度语义与输出保护行为符合预期")
    return EXIT_OK


def cmd_check_robots(ua: str = UA, timeout: int = 15) -> int:
    """检查 robots.txt 并打印原文。"""
    allowed, detail, raw = check_robots(ua, timeout)
    log.info("[robots] %s", detail)
    if raw:
        log.info("---- robots.txt 原文 ----\n%s", raw.strip())
    return EXIT_OK if allowed else EXIT_ENV


# ==============================================================================
# 15. 内置手册 —— 脚本内可查询
# ==============================================================================
MANUAL = """
================================================================================
 scrape_malaysiayp.py  v{ver}   —   内置手册
================================================================================

一、这是什么
    从 malaysiayp.com 按站点结构抓取「公司名 + 01X 手机号」，输出 CSV。
    HTMLParser逐列表项确定性解析，零 LLM/第三方依赖；可独立分段运行。

二、三种运行方式（都不需要 LLM）
    A. Windows 双击 / 计划任务 :  run.cmd --n 100
    B. Linux / macOS          :  ./run.sh --n 100
    C. 直接调解释器            :  python scrape_malaysiayp.py --n 100 --seed 42

三、模式（互斥，一次只用一个）
    （默认）        抓取
    --doctor        环境自检（10 项）—— 出问题先跑这个
    --verify CSV    校验已有产出质量
    --against CSV   配合 --verify：对比基线（追加前的 .bak），证明旧号码一条没丢
    --coverage      报告下载覆盖情况与缺口（顺序检验）
    --self-test     离线自检（纯函数回归，零网络）—— 改代码后先跑这个
    --stress-test   限流探针：实测「软限流上限 + 冷却恢复曲线 + 安全速率」
    --check-robots  只看 robots.txt
    --manual        打印本手册
    --examples      只看示例
    --print-api     只看函数接口速查

四、常用参数
    --n N               显式抽样目标条数（不传则默认全量）
    --preset NAME       tiny / small / medium / large 规模预设
    --order MODE        sequential（按分类顺序+页码升序）| random（默认）
    --categories A,B    只抓指定分类
    --from-page / --to-page   页码范围
    --max-pages N       最多抓多少页（安全阀，默认 30）
    --per-cat N         单分类上限，强制跨类型（默认 10；0 = 不限，配顺序全量抓用）
    --delay S           请求间隔秒（默认 2.0）—— 被限流就调大
    --jitter S          间隔随机抖动上限（默认 0.5），避免固定间隔被识别
    --max-minutes M     时间预算，超时停止并保存断点
    --seed N            随机种子，同 seed 同结果
    --out PATH          输出 CSV 路径
    --force             已存在时允许覆盖（默认拒绝）
    --append            增量追加到已有 CSV（按 phone 去重）
    --no-backup         覆盖前不备份
    --resume            从断点续跑
    --self-test         离线自检（纯函数回归，零网络）★ 改代码后先跑这个
    --stress-test       限流探针（会主动连发请求，用于定 --delay）
    --stress-burst N / --stress-burst-delay S    阶段 A 连发次数与间隔
    --stress-cooldown S / --stress-rates "1,2,3" / --stress-rate-n N
    --stress-max-requests N                     总请求硬上限（默认 400）
    --reindex           强制重建站点索引
    --no-cache          忽略缓存全部重抓
    --dry-run           只建索引，不抓条目页
    --no-lock           不获取互斥锁（默认会获取）
    --allow-low-yield   条数不足也算成功（退出码 0）
    --skip-robots-check 跳过 robots 检查（仅在已获授权时用）
    --retries / --timeout / --user-agent   网络参数
    -v                  调试日志

五、退出码（无人值守只看这个）
    0    成功且达标
    2    参数错误
    3    环境错误（目录不可写 / 网络不通 / robots.txt 不允许）
    4    被站点封禁或出现验证页
    5    站点结构变更 —— 需检查 DirectoryParser / _FullProbe
    6    抓取成功但条数不足目标（--coverage 有缺口时也返回 6）
    7    输出文件已存在且未给 --force / --append
    8    已有另一个实例在运行
    9    全量分段/预算暂停，原命令自动续跑
    130  被中断（全量重跑原命令；抽样 --resume）

六、七项核心机制
    1. 顺序下载      --order sequential + manifest 账本 + --coverage 校验
    2. 重复下载防护   URL 缓存(sha1) + seen_url + 电话级去重，三层
    3. 输出保护      默认拒绝覆盖；--force 才覆盖；覆盖前自动 .bak；
                     --append 增量合并；缩水守卫（新 < 旧 50% 时拒绝）
    4. 人类可维护     全函数类型注解 + 接口速查 + 分节横幅
    5. 内置手册       --manual / --examples / --print-api
    6. 任意数量       --n / --preset
    7. 序列防限流     单线程串行 + --delay + --jitter + 退避 + 时间预算

    额外：互斥锁（防计划任务重叠）、SIGTERM 优雅退出、脚本指纹、
          自愈（索引/缓存损坏自动重建）、覆盖率检查、离线自检（--self-test）、
          限流探针（--stress-test，实测上限与冷却曲线来定 --delay）

    额外 2（配额语义，2026-10-08 修正）：--per-cat 是「每分类累计条数」上限，
          跨页生效；顺序模式下某分类达标即整类跳过，把页预算让给下一个分类，
          从而保证「跨类型」与「页预算不被单分类吃光」。

    额外 3（号码形态，2026-10-08 修正）：MOBILE_RE 必须同时认 10 位（01X-XXXXXXX）
          与 11 位（011-XXXXXXXX）。曾写成 01[0-9]{7,8} 只认 9~10 位，
          导致 011 段手机号被静默丢弃（缓存实测 12 条 11 位全漏）。
          --verify 现在会打印「号段分布 / 位数分布 / 分类集中度」以便发现这类整段缺失。

七、输出文件
    data/<名>.csv              产出数据（8 列）
    data/<名>.meta.json        本次运行的参数/条数/退出码/脚本指纹
    cache/index.json           站点结构索引（分类 + 每类页数）
    cache/manifest.json        抓取账本（每个已抓页的记录）
    cache/state.json           断点（达标后自动删除）
    cache/html/<sha1>.html     页面缓存
    logs/run-<时间戳>.log      完整日志（排错唯一依据）

八、站点改版了怎么办（退出码 5）
    1. 抓一页存本地看现在的结构：
         curl -sL -A "Mozilla/5.0 ... Chrome/120" \\
           "https://malaysiayp.com/cat/automotive/" -o probe.html
    2. 检查 DirectoryParser 的 row-item / row-meta / /item/ / tel: 字段映射；
       检查 _FullProbe 的同分类分页链接、canonical与页码文字。ROW_RE仅保留供旧工具兼容。
    3. 改完立刻验证：  python scrape_malaysiayp.py --doctor
       （选择器自检会直接告诉你改对没）
    4. 若分类结构也变了，检查 CAT_RE / PAGES_RE 后跑 --reindex

九、合规红线
    * 该站 robots.txt 把 AI 爬虫分两组：训练型（GPTBot/ClaudeBot/CCBot 等）Disallow，
      检索型（OAI-SearchBot/PerplexityBot 等）Allow；通用 UA 组 Allow: /。
    * 全站规模大：逐页落盘、每段冷却；遇限流退避，遇封禁停止，不绕过验证。
    * 产出是「公司名 + 手机号」聚合，受 PDPA 2010(2024) 约束：
      仅限目录检索/研究，禁止群发、推销、骚扰、转售。

十、完整排错手册见 TROUBLESHOOTING.md
================================================================================
"""

EXAMPLES = """
================================================================================
 使用示例
================================================================================

# —— 环境体检（出问题先跑这个）——
python scrape_malaysiayp.py --doctor
python scrape_malaysiayp.py --doctor --skip-net      # 断网环境也能跑

# —— 离线自检（零网络；改过 ROW_RE / iter_plan / scrape 后必须先跑）——
python scrape_malaysiayp.py --self-test
#   通过 → 退出码 0；有断言失败 → 退出码 5（不要联网抓，先修）
#   覆盖：文本清洗 / 手机号正则(10位01X+11位011) / 行解析捕获组顺序 /
#         调度配额语义(顺序+跨分类) / 输出保护 / 增量合并+追加安全 /
#         覆盖率缺口 / 退出码表 / 内置文档 / 限流探针分类逻辑

# —— 限流探针（实测站点能承受多快，用来定 --delay）——
python scrape_malaysiayp.py --stress-test
#   默认：突发 30 次 @0.3s → 冷却最长 120s → 稳态测 1/2/3s 各 10 次
#   保守跑法（请求更少）：
python scrape_malaysiayp.py --stress-test --stress-burst 15 --stress-rates 2,5 --stress-rate-n 8
#   结论会打印「建议 --delay X」，并写入 data/ratelimit-report.json

# —— 抓取：按数量 ——
python scrape_malaysiayp.py --preset tiny            # 20 条
python scrape_malaysiayp.py --preset medium          # 100 条（默认）
python scrape_malaysiayp.py --n 250                  # 任意数量

# —— 抓取：顺序模式（按站点结构，可校验完整性）——
python scrape_malaysiayp.py --order sequential --n 200 --max-pages 60
python scrape_malaysiayp.py --coverage               # 看已抓了哪些页、缺哪些

# —— 抓取：限定范围 ——
python scrape_malaysiayp.py --categories hotels,eating-places --n 60
python scrape_malaysiayp.py --order sequential --from-page 1 --to-page 5

# —— 防限流 ——
python scrape_malaysiayp.py --delay 5 --jitter 1.5 --max-minutes 30

# —— 输出保护 ——
python scrape_malaysiayp.py --n 100 --out data/run1.csv      # 首次写入
python scrape_malaysiayp.py --n 100 --out data/run1.csv      # 第二次 → 退出码 7（拒绝）
python scrape_malaysiayp.py --n 100 --out data/run1.csv --force    # 显式覆盖（自动备份）
python scrape_malaysiayp.py --n 100 --out data/run1.csv --append   # 增量合并去重

# —— 中断与续跑 ——
python scrape_malaysiayp.py --n 500 --max-pages 120
#   ... Ctrl-C 或计划任务 kill ...
python scrape_malaysiayp.py --resume --n 500 --max-pages 120

# —— 校验产出 ——
python scrape_malaysiayp.py --verify data/run1.csv
python scrape_malaysiayp.py --verify data/run1.csv --probe 3    # 抽样探测来源页

# —— 追加后自证：证明旧数据一条没丢（强烈建议每次都跑）——
#   先找到追加前的备份，再把它当基线对比：
python scrape_malaysiayp.py --verify data/run1.csv --against data/run1.20261008-104218.bak
#   判定：基线每个手机号都必须仍在新文件里；少一个即退出码 6。

# —— 合规检查 ——
python scrape_malaysiayp.py --check-robots

# —— 自查说明 ——
python scrape_malaysiayp.py --manual
python scrape_malaysiayp.py --print-api
================================================================================
"""

API_DOC = """
================================================================================
 函数接口速查
================================================================================

【异常】
  Fatal(Exception)              不可重试（被封/验证页）→ 立即中止
  Unavailable(Exception)        单页不可用（404/越界）→ 只跳过该页
  StructureChanged(Exception)   站点结构变更 → 需人工更新 ROW_RE
  OutputProtected(Exception)    输出保护触发（已存在/缩水）
  Locked(Exception)             已有实例在运行

【基础设施】
  atomic_write(path, text, encoding="utf-8") -> None
      原子写：先写 .tmp 再 os.replace
  file_lock(path) -> file|None
      OS 级排他锁（非阻塞）。进程死自动释放，不留死锁
  source_fingerprint() -> {script, version, sha256, schema}
      脚本指纹，写入 meta 供追溯

【日志】
  setup_logging(verbose=False, log_dir=LOGDIR) -> (logger, log_path)
      同时输出控制台 + 文件；日志目录不可写时降级不崩

【缓存 / 抓取】
  cache_path(url) -> str
      URL → cache/html/<sha1[:16]>.html（天然去重）
  fetch(url, delay, use_cache=True, retries=3, timeout=30, ua=UA, jitter=0.0)
        -> (html_text, from_cache)
      命中缓存直接返回；否则请求。带拦截检测 + 退避 + 软限流重试

【合规】
  parse_robots(text) -> [{uas, rules}]
  robots_allowed(text, ua, path="/") -> (allowed, detail)
  check_robots(ua=UA, timeout=15) -> (allowed|None, detail, raw)

【索引】
  build_index(delay, use_cache=True, retries=3, timeout=30, ua=UA, jitter=0.0)
        -> index dict
  load_index() -> index|None     损坏时自动备份 .corrupt 并返回 None

【清单 / 覆盖】
  load_manifest() -> manifest
  save_manifest(manifest) -> None
  record_page(manifest, url, cat, page, body, rows, mobiles, from_cache) -> None
      把一次抓取记入账本 —— 顺序检验的数据来源
  coverage_report(index, manifest=None) -> {categories, totals}
      按分类统计已下载页、缺口、覆盖率

【断点】
  save_state(state) / load_state() -> state|None / clear_state()

【解析】
  clean_text(s) -> str            反转义 + 去 U+FFFD/控制字符 + 折叠空白
  parse_rows(body) -> [(公司, 地址, 电话数字, 电话显示, 详情链接)]

【调度】
  iter_plan(index, order, seed, cats_filter=None, from_page=1, to_page=None,
            per_cat=0, cat_counts=None)
        -> 迭代 (分类, 页码, URL)   确定性；同 seed 同顺序
    说明：per_cat 是「每分类累计条数」配额（<=0 = 不限）；cat_counts 是调用方持有的
          实时计数字典。生成器每次恢复执行时读取 cat_counts 的最新值，故抓取中某分类
          一旦达标，其后续页会被自动跳过 —— 这是「配额跨页生效、页预算不被单分类吃光」
          的实现方式。顺序模式下分类顺序与页码升序始终不变。
  scrape(index, target, max_pages, per_cat, delay, seed, order="random", ...)
        -> (rows, stats)
    说明：target 为硬上限，达标即停（不会因单页多出条目而超发）。

【输出】
  guard_output(path, force, append, new_rows) -> 拒绝原因|None
      防误覆盖 + 缩水守卫
  backup_existing(path) -> 备份路径|None
  read_existing_rows(path) -> [dict]
  append_merge(old, new) -> (merged, added)     按 phone 去重
  write_csv(rows, path) -> 实际路径             原子写；被占用降级 *_new.csv
  write_meta(csv_path, rows, params, exit_code, index, extra=None) -> None

【模式】
  cmd_doctor(delay=1.0, timeout=20, ua=UA, skip_net=False, jitter=0.0) -> 退出码
  cmd_verify(path, probe=0, timeout=15, ua=UA) -> 退出码
  cmd_coverage(index=None, verbose=False) -> 退出码
  cmd_self_test() -> 退出码
      离线纯函数回归（零网络）：文本清洗 / 手机号正则 / 行解析捕获组顺序 /
      调度配额语义 / 输出保护 / 增量合并+追加安全 / 覆盖率缺口 / 退出码表完整性 /
      内置文档可渲染 / 限流探针分类逻辑。
      ★ 改动 ROW_RE 或 iter_plan / scrape 后，先跑它再联网。
  cmd_stress_test(index, burst, burst_delay, cooldown_max, rate_intervals,
                  rate_n, timeout, ua, max_requests=400, rate_gap=30,
                  backoff=(6,12,24), backoff_rounds=4, recover_streak=3) -> 退出码
      限流探针四阶段：
        A 突发   —— 软限流何时出现 + 形态（分散随机丢弃 / 连续撞墙）
        B 冷却   —— 需连续 recover_streak 次成功才算「稳定恢复」（单次成功不算）
        C 稳态   —— 各候选间隔的成功率，间隔间插入 rate_gap 冷却以消除顺序效应
        D 退避   —— 复现 backoff 退避表，测「修复方案的吸收率」
      报告写入 data/ratelimit-report.json。总请求受 max_requests 硬限制。
  _raw_get(url, timeout, ua) -> {status, bytes, elapsed, error, marker}
      单次原始 GET，**不做重试** —— 探针必须看到每一次原始响应。
  _classify_probe(r) -> "ok" | "soft" | "blocked" | "notfound" | "error"
      soft = 200 但响应过短/为空（软限流）；blocked = 401/403/451 或挑战指纹。
  _probe_urls(index, count) -> [url]
      挑深页 URL 做探测（深页不会被缓存命中，必须走网络）。
  cmd_check_robots(ua=UA, timeout=15) -> 退出码

【入口】
  build_parser() -> ArgumentParser
  main(argv=None) -> 退出码
================================================================================
"""


# ==============================================================================
# 16. 命令行入口
# ==============================================================================
# ==============================================================================
# SQLite 全量任务：只以提交后的数据库和导出账本作为断点真源
# ==============================================================================
import sqlite3
import unicodedata

FULL_MANUAL = r"""
【全量、分段与自动续跑】
  python scrape_malaysiayp.py --all --out data/all-mobile.csv
  python scrape_malaysiayp.py --all --out data/all-mobile.csv --max-chunks 1
  python scrape_malaysiayp.py --all --out data/all-mobile.csv --full-verify
  python scrape_malaysiayp.py --all --out data/all-mobile.csv --export

--all 不受 --n / --per-cat / --max-pages 的抽样上限约束。默认每段最多25次页面
尝试、段间30秒，单线程；每页单独提交SQLite事务。首页发现分类，各分类第一页
发现分页，后续同分类分页链接会扩大任务。分类首探失败也留在队列，不会漏算。
--categories 可指定逗号分隔分类slug，此时完成仅指所选分类范围；不接受分页裁剪。
--phone-scope mobile 仅导出有效01X手机号；all 导出全部企业，包括座机和无号码。
无论导出范围如何，所有解析的企业都留在SQLite，按(detail_url, phone)去重；
不同企业共用同一个号码不会被合并。原8列CSV格式不变，危险公式文本加单引号。

断点是 OUT.sqlite3；段文件是 OUT去扩展名.parts/part-000001.csv；运行摘要是
OUT.job.json。每段文件都有行数、SHA256和数据库范围账本。已写文件但事务未提交
时重跑会重新生成同一内容并校验，绝不覆盖内容不匹配的旧文件。只有页覆盖完整、
索引完整、CSV与数据库验收通过后才发布最终OUT。不要删除/修改断点或parts。
重跑相同命令自动续跑，不需要 --resume。已有其他任务CSV或不匹配scope的DB会
拒绝使用；--force / --append / --no-lock 不会绕过全量保护。SQLite损坏不重建。

--page-attempts 默认4次（跨进程持久计数），失败指数退避；连续3次失败冷却。
403/验证页立即返回4；解析结构损坏返回5，已成功页不丢。耗尽重试的页面需要
人工诊断修复任务，不能通过重跑无限请求。每段刷新robots（无法确认也停止）；
仅已明确取得授权时使用 --skip-robots-check。全量不读取/写入旧HTTP缓存。
--min-free-mb 默认512，每段检查磁盘余量。--max-minutes 为本次运行时间预算；
--max-chunks 限制本次段数；达到限制返回9，可用原命令续跑。处理中断返回130。
--export 不访问网络，只从当前DB生成段快照；未完整仍返回9，不冒充全量最终CSV。
--full-verify 不访问网络，检查SQLite integrity、索引/页缺口、业务键、parts哈希、
序号/字段/公式安全和最终CSV与DB逐行对应；未完整或验收失败返回6。
退出0仅表示声明的分类范围完成并验收通过；3=环境/DB/磁盘错误，7=输出保护，
8=同输出任务已运行，9=可续的分段暂停。SQLite缓存固定8MiB、临时表落盘，导出
流式进行，每个段CSV最多5000行；单页面及单字段也设上限，不载入全站记录。
"""

_FULL_DB_VERSION = 2
_FULL_PART_ROWS = 5000
_FULL_FIELD_LIMIT = 65536
_FULL_PAGE_LIMIT = 1000000
_FULL_PHONE_ALL = re.compile(r"0\d{7,10}|1[38]00\d{6,8}")
_FULL_DANGEROUS = "=+-@"


class _FullProbe(HTMLParser):
    def __init__(self, category_url: str):
        super().__init__(convert_charrefs=True)
        self.category_url = category_url
        self.items = 0
        self.pages = 1
        self.text = []
        self.categories = set()
        self.canonical = None
        self.page_number = None
        self._ignore = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._ignore += 1
            return
        if self._ignore:
            return
        attr = dict(attrs)
        if tag == "link" and "canonical" in (attr.get("rel") or "").split():
            self.canonical = urllib.parse.urljoin(BASE + "/", attr.get("href") or "")
        if tag == "li" and "row-item" in attr.get("class", "").split():
            self.items += 1
        if tag != "a" or not attr.get("href"):
            return
        url = urllib.parse.urljoin(BASE + "/", attr["href"])
        parsed = urllib.parse.urlsplit(url)
        origin = urllib.parse.urlsplit(BASE)
        if (parsed.scheme, parsed.netloc) != (origin.scheme, origin.netloc):
            return
        if re.fullmatch(r"/cat/[a-z0-9-]+/", parsed.path, re.I):
            self.categories.add(BASE + parsed.path)
        if self.category_url:
            cat_path = urllib.parse.urlsplit(self.category_url).path
            match = re.fullmatch(re.escape(cat_path) + r"page/(\d+)/?", parsed.path)
            if match:
                page = int(match.group(1))
                if not 1 <= page <= _FULL_PAGE_LIMIT:
                    raise StructureChanged("分页数超出安全上限")
                self.pages = max(self.pages, page)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._ignore = max(0, self._ignore - 1)

    def handle_data(self, data):
        if not self._ignore:
            self.text.append(data)

    def summary(self):
        text = " ".join(self.text)
        pagination = re.search(r"Page\s+(\d+)\s+of\s+([\d,]+)", text, re.I)
        if pagination:
            self.page_number = int(pagination.group(1))
            self.pages = max(self.pages, int(pagination.group(2).replace(",", "")))
            if self.pages > _FULL_PAGE_LIMIT:
                raise StructureChanged("Page total exceeds safety bound")
        total = None
        patterns = (
            r"(?:found|total(?:\s+(?:of|listings|companies|businesses))?)\s*:?\s*([\d,]+)\s*(?:listings|companies|businesses|results)?",
            r"([\d,]+)\s+(?:listings|companies|businesses|results)\s+(?:found|in|available)",
            r"showing\s+\d+\s*(?:-|to|–)\s*\d+\s+(?:of|out of)\s+([\d,]+)",
        )
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                total = int(match.group(1).replace(",", ""))
                break
        empty = bool(re.search(
            r"(?:no\s+(?:listings|companies|businesses|results)\s+(?:found|available)|"
            r"(?:found|total)\s*:?\s*0\s+(?:listings|companies|businesses|results))",
            text, re.I))
        return total, empty


def _full_get(db, key, default=None):
    row = db.execute("SELECT value FROM job_meta WHERE key=?", (key,)).fetchone()
    return json.loads(row[0]) if row else default


def _full_set(db, key, value):
    db.execute("INSERT OR REPLACE INTO job_meta(key,value) VALUES(?,?)",
               (key, json.dumps(value, ensure_ascii=False, sort_keys=True)))


def _full_inc(db, key, amount):
    _full_set(db, "count_" + key, _full_get(db, "count_" + key, 0) + amount)


def _full_filter(scope):
    if scope == "all":
        return "1=1"
    return "(phone GLOB '01[0-9]*' AND length(phone)=10) OR (phone GLOB '011[0-9]*' AND length(phone)=11)"


def _full_config(args):
    supplied = getattr(args, "categories", None)
    if isinstance(supplied, str):
        supplied = supplied.split(",")
    selected = sorted(set(str(x).strip() for x in (supplied or []) if str(x).strip()))
    if any(not re.fullmatch(r"[a-z0-9-]+", x, re.I) for x in selected):
        raise ValueError("--categories 必须为分类slug，逗号分隔")
    return {"base": BASE, "schema": _FULL_DB_VERSION,
            "csv_columns": CSV_COLS, "selected_categories": selected,
            "phone_scope": getattr(args, "phone_scope", "mobile"),
            "page_attempts": getattr(args, "page_attempts", 4)}


def _full_open(out, config=None, create=False):
    path = out + ".sqlite3"
    exists = os.path.exists(path)
    if not exists and not create:
        raise OSError("全量SQLite断点不存在：" + path)
    if not exists and (os.path.exists(out) or os.path.exists(out + ".job.json") or
                       os.path.exists(os.path.splitext(out)[0] + ".parts")):
        raise OutputProtected("已有输出但无匹配SQLite，拒绝覆盖/导入")
    db = sqlite3.connect(path, timeout=30)
    try:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=30000")
        db.execute("PRAGMA cache_size=-8192")
        db.execute("PRAGMA temp_store=FILE")
        integrity = db.execute("PRAGMA integrity_check")
        if any(row[0] != "ok" for row in integrity):
            raise sqlite3.DatabaseError("SQLite完整性检查失败；保留原文件，不重建")
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA synchronous=FULL")
        db.execute("PRAGMA foreign_keys=ON")
        if not exists:
            db.executescript("""
                CREATE TABLE job_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE categories(
                    url TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE,
                    pages INTEGER NOT NULL DEFAULT 1, total INTEGER,
                    index_state TEXT NOT NULL DEFAULT 'pending');
                CREATE TABLE pages(
                    url TEXT PRIMARY KEY, category TEXT NOT NULL, number INTEGER NOT NULL,
                    kind TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
                    attempts INTEGER NOT NULL DEFAULT 0, not_before REAL NOT NULL DEFAULT 0,
                    error TEXT NOT NULL DEFAULT '', rows INTEGER NOT NULL DEFAULT 0,
                    item_count INTEGER NOT NULL DEFAULT 0, body_sha TEXT, updated REAL,
                    UNIQUE(category,number,kind));
                CREATE INDEX page_queue ON pages(status,not_before,category,number);
                CREATE INDEX page_category ON pages(category,kind,number,status);
                CREATE TABLE entries(
                    id INTEGER PRIMARY KEY, company TEXT NOT NULL, phone TEXT NOT NULL,
                    display TEXT NOT NULL, category TEXT NOT NULL, address TEXT NOT NULL,
                    detail_url TEXT NOT NULL, source_page TEXT NOT NULL,
                    raw_phone TEXT NOT NULL DEFAULT '', phone_status TEXT NOT NULL DEFAULT 'valid',
                    exported INTEGER NOT NULL DEFAULT 0, UNIQUE(detail_url,phone));
                CREATE INDEX entries_export ON entries(exported,id);
                CREATE INDEX entries_mobile_pending ON entries(id) WHERE exported=0 AND
                    ((phone GLOB '01[0-9]*' AND length(phone)=10) OR (phone GLOB '011[0-9]*' AND length(phone)=11));
                CREATE TABLE page_entries(
                    page_url TEXT NOT NULL REFERENCES pages(url),
                    entry_id INTEGER NOT NULL REFERENCES entries(id),
                    PRIMARY KEY(page_url,entry_id));
                CREATE TABLE parts(
                    seq INTEGER PRIMARY KEY, path TEXT NOT NULL UNIQUE,
                    lo INTEGER NOT NULL, hi INTEGER NOT NULL, count INTEGER NOT NULL,
                    status TEXT NOT NULL, sha256 TEXT, schema_json TEXT NOT NULL);
            """)
            with db:
                _full_set(db, "config", config)
                _full_set(db, "created", time.time())
                _full_set(db, "fingerprints", [source_fingerprint()])
                _full_set(db, "completion", False)
                db.execute("INSERT INTO pages(url,category,number,kind) VALUES(?,?,?,?)",
                           (BASE + "/", "", 0, "home"))
        else:
            actual = _full_get(db, "config")
            if (not isinstance(actual, dict) or actual.get("schema") != _FULL_DB_VERSION
                    or actual.get("phone_scope") not in ("mobile", "all")
                    or not isinstance(actual.get("selected_categories"), list)
                    or not isinstance(actual.get("page_attempts"), int)):
                raise sqlite3.DatabaseError("SQLite不是受支持的全量任务；不自动重建")
            if config is not None and actual != config:
                raise OutputProtected("已有SQLite分类/号码scope配置不同，请使用新的--out")
            if actual.get("base") != BASE or actual.get("csv_columns") != CSV_COLS:
                raise OutputProtected("已有SQLite站点或CSV schema不匹配")
            history = _full_get(db, "fingerprints", [])
            current = source_fingerprint()
            if not history or history[-1] != current:
                # 只保留有限次版本历史；原始指纹独立保留。
                with db:
                    _full_set(db, "fingerprints", (history[:1] + history[-14:] + [current]))
        return db
    except BaseException:
        db.close()
        raise


def _full_origin(url, prefix):
    parsed = urllib.parse.urlsplit(url)
    origin = urllib.parse.urlsplit(BASE)
    return ((parsed.scheme, parsed.netloc) == (origin.scheme, origin.netloc)
            and parsed.path.startswith(prefix) and len(parsed.path) > len(prefix) and not parsed.username
            and not parsed.password and not parsed.query and not parsed.fragment)


def _full_text(value):
    if not isinstance(value, str) or len(value) > _FULL_FIELD_LIMIT:
        raise ValueError("CSV字段不是字符串或超过64Ki字符")
    for ch in value:
        if unicodedata.category(ch) in ("Cc", "Cs") or ch == "\ufffd" or ch in "\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069":
            raise ValueError("字段含控制字符、无效Unicode或双向覆盖字符")


def _full_check_row(row, scope, csv_input=False):
    for column in CSV_COLS[1:]:
        _full_text(row[column])
        if csv_input and row[column].lstrip().startswith(tuple(_FULL_DANGEROUS)):
            raise ValueError("CSV存在未保护的公式字段：" + column)
    if not row["company"].strip():
        raise ValueError("公司名缺失")
    phone = row["phone"]
    if phone and not _FULL_PHONE_ALL.fullmatch(phone):
        raise ValueError("号码不是归一化马来西亚电话号码：" + phone[:32])
    if scope == "mobile" and not MOBILE_RE.fullmatch(phone):
        raise ValueError("mobile导出中存在非01X手机号")
    if not row["category"] or not _full_origin(row["detail_url"], "/item/") or not _full_origin(row["source_page"], "/cat/"):
        raise ValueError("分类缺失或详情/来源URL不是同源目录地址")


def _full_csv_row(row, number):
    result = {"no": str(number)}
    for column in CSV_COLS[1:]:
        value = row[column]
        if value.lstrip().startswith(tuple(_FULL_DANGEROUS)):
            value = "'" + value
        result[column] = value
    return result


def _full_sha(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _full_rows(db, scope, lo=None, hi=None):
    query = "SELECT * FROM entries WHERE (" + _full_filter(scope) + ")"
    params = ()
    if lo is not None:
        query += " AND id BETWEEN ? AND ?"
        params = (lo, hi)
    return db.execute(query + " ORDER BY id", params)


def _full_publish(db, scope, path, lo=None, hi=None):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    count = 0
    with open(tmp, "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLS)
        writer.writeheader()
        for count, row in enumerate(_full_rows(db, scope, lo, hi), 1):
            _full_check_row(row, scope)
            writer.writerow(_full_csv_row(row, count))
        fh.flush()
        os.fsync(fh.fileno())
    digest = _full_sha(tmp)
    if os.path.exists(path):
        if _full_sha(path) != digest:
            raise OutputProtected("旧CSV内容与数据库账本不匹配，保留原文件：" + path)
        os.remove(tmp)
    else:
        os.replace(tmp, path)
    return count, digest


def _full_check_csv(db, scope, path, lo=None, hi=None):
    csv.field_size_limit(_FULL_FIELD_LIMIT * 2)
    expected = iter(_full_rows(db, scope, lo, hi))
    count = 0
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != CSV_COLS:
            raise ValueError("CSV列schema不一致：" + path)
        for count, actual in enumerate(reader, 1):
            if None in actual or any(value is None for value in actual.values()):
                raise ValueError("CSV行列数错误")
            _full_check_row(actual, scope, csv_input=True)
            row = next(expected, None)
            if row is None or actual != _full_csv_row(row, count):
                raise ValueError("CSV与SQLite记录/顺序/序号不一致：" + path)
        if next(expected, None) is not None:
            raise ValueError("CSV缺失SQLite记录：" + path)
    return count


def _full_commit_part(db, scope, part):
    count, digest = _full_publish(db, scope, part["path"], part["lo"], part["hi"])
    if count != part["count"]:
        raise ValueError("待发布段的数据库行数发生变化")
    if _full_check_csv(db, scope, part["path"], part["lo"], part["hi"]) != count:
        raise ValueError("段CSV验收失败")
    with db:
        changed = db.execute(
            "UPDATE entries SET exported=? WHERE exported=0 AND id BETWEEN ? AND ? AND (" + _full_filter(scope) + ")",
            (part["seq"], part["lo"], part["hi"])).rowcount
        if changed != count:
            raise ValueError("段CSV导出状态与账本冲突")
        db.execute("UPDATE parts SET status='done',sha256=? WHERE seq=?", (digest, part["seq"]))
        _full_inc(db, "exported", count)
        _full_inc(db, "parts", 1)


def _full_export_parts(db, out, scope):
    for part in db.execute("SELECT * FROM parts WHERE status='prepared' ORDER BY seq"):
        _full_commit_part(db, scope, part)
    while True:
        bounds = db.execute(
            "SELECT min(id),max(id),count(*) FROM (SELECT id FROM entries WHERE exported=0 AND (" +
            _full_filter(scope) + ") ORDER BY id LIMIT ?)", (_FULL_PART_ROWS,)).fetchone()
        if not bounds[2]:
            break
        seq = db.execute("SELECT coalesce(max(seq),0)+1 FROM parts").fetchone()[0]
        path = os.path.join(os.path.splitext(out)[0] + ".parts", "part-%06d.csv" % seq)
        with db:
            db.execute("INSERT INTO parts(seq,path,lo,hi,count,status,schema_json) VALUES(?,?,?,?,?,'prepared',?)",
                       (seq, path, bounds[0], bounds[1], bounds[2], json.dumps(CSV_COLS)))
        part = db.execute("SELECT * FROM parts WHERE seq=?", (seq,)).fetchone()
        _full_commit_part(db, scope, part)


def _full_coverage(db):
    pages = {row[0]: row[1] for row in db.execute("SELECT status,count(*) FROM pages GROUP BY status")}
    cat = db.execute("SELECT count(*),coalesce(sum(pages),0),sum(index_state!='done') FROM categories").fetchone()
    home = db.execute("SELECT status FROM pages WHERE kind='home'").fetchone()
    catalog = db.execute("SELECT status FROM pages WHERE kind='catalog'").fetchone()
    expected = cat[1] + 2
    actual = db.execute("SELECT count(*) FROM pages").fetchone()[0]
    # 既检查数量也检查连续边界，不能用重复页填补缺口。
    gaps = db.execute("""SELECT count(*) FROM categories c WHERE
        (SELECT count(*) FROM pages p WHERE p.category=c.name AND p.kind='category') != c.pages
        OR (SELECT coalesce(min(number),0) FROM pages p WHERE p.category=c.name AND p.kind='category') != 1
        OR (SELECT coalesce(max(number),0) FROM pages p WHERE p.category=c.name AND p.kind='category') != c.pages""").fetchone()[0]
    total_mismatch = db.execute("""SELECT count(*) FROM categories c WHERE c.total IS NOT NULL
        AND c.index_state='done'
        AND NOT EXISTS(SELECT 1 FROM pages p WHERE p.category=c.name AND p.status!='done')
        AND (SELECT coalesce(sum(rows),0) FROM pages p WHERE p.category=c.name AND p.kind='category') != c.total""").fetchone()[0]
    complete = bool(home and home[0] == "done" and catalog and catalog[0] == "done"
                    and cat[0] > 0 and not cat[2]
                    and not gaps and actual == expected and pages.get("done", 0) == expected
                    and not total_mismatch)
    return {"categories": cat[0], "index_failed_or_pending": cat[2] or 0,
            "expected_pages": expected, "known_pages": actual,
            "page_states": pages, "category_page_gaps": gaps,
            "header_total_mismatches": total_mismatch,
            "complete": complete}


def _full_verify_db(db, out, require_final=True):
    if any(row[0] != "ok" for row in db.execute("PRAGMA integrity_check")):
        raise sqlite3.DatabaseError("SQLite完整性检查失败")
    if db.execute("PRAGMA foreign_key_check").fetchone() is not None:
        raise ValueError("SQLite关联完整性失败")
    config = _full_get(db, "config")
    scope = config["phone_scope"]
    if db.execute("SELECT 1 FROM entries GROUP BY detail_url,phone HAVING count(*)>1 LIMIT 1").fetchone():
        raise ValueError("数据库业务键重复")
    for row in db.execute("SELECT * FROM entries ORDER BY id"):
        _full_check_row(row, "all")
    if db.execute("""SELECT 1 FROM pages p WHERE p.status='done' AND p.kind='category'
        AND (p.rows!=p.item_count OR p.rows!=(SELECT count(*) FROM page_entries e WHERE e.page_url=p.url)) LIMIT 1""").fetchone():
        raise ValueError("已提交页面的实体数量不匹配")
    for part in db.execute("SELECT * FROM parts ORDER BY seq"):
        if part["status"] != "done" or json.loads(part["schema_json"]) != CSV_COLS:
            raise ValueError("段CSV账本尚未提交或schema错误")
        if _full_sha(part["path"]) != part["sha256"]:
            raise ValueError("段CSV SHA256不一致：" + part["path"])
        if _full_check_csv(db, scope, part["path"], part["lo"], part["hi"]) != part["count"]:
            raise ValueError("段CSV行数不匹配")
        assigned = db.execute("SELECT count(*) FROM entries WHERE exported=? AND id BETWEEN ? AND ?",
                              (part["seq"], part["lo"], part["hi"])).fetchone()[0]
        if assigned != part["count"]:
            raise ValueError("段CSV与exported标记数量不一致")
    if db.execute("""SELECT 1 FROM entries e LEFT JOIN parts p ON e.exported=p.seq
        WHERE e.exported>0 AND (p.seq IS NULL OR p.status!='done' OR e.id<p.lo OR e.id>p.hi) LIMIT 1""").fetchone():
        raise ValueError("导出标记缺少对应段账本")
    parts_dir = os.path.splitext(out)[0] + ".parts"
    if os.path.isdir(parts_dir):
        for item in os.scandir(parts_dir):
            if item.is_file() and item.name.endswith(".csv"):
                if db.execute("SELECT 1 FROM parts WHERE path=?", (item.path,)).fetchone() is None:
                    raise ValueError("parts目录存在没有账本的CSV：" + item.path)
    coverage = _full_coverage(db)
    if require_final:
        if not coverage["complete"] or not _full_get(db, "completion", False):
            raise ValueError("任务索引/页覆盖未全量完成")
        if db.execute("SELECT 1 FROM entries WHERE exported=0 AND (" + _full_filter(scope) + ") LIMIT 1").fetchone():
            raise ValueError("有未提交段的导出记录")
        final = _full_get(db, "final")
        if not final or _full_sha(out) != final["sha256"]:
            raise ValueError("最终CSV哈希不匹配或缺失")
        if _full_check_csv(db, scope, out) != final["count"]:
            raise ValueError("最终CSV行数与账本不匹配")
    return coverage


def _full_metadata(db, out, phase, code, error=""):
    scope = _full_get(db, "config")["phone_scope"]
    totals = (_full_get(db, "count_stored", 0),
              _full_get(db, "count_missing", 0), _full_get(db, "count_exported", 0))
    attempts = db.execute("SELECT coalesce(sum(attempts),0),coalesce(sum(attempts-(status='done')),0) FROM pages").fetchone()
    summary = {"schema": _FULL_DB_VERSION, "script": source_fingerprint(),
               "config": _full_get(db, "config"), "created": _full_get(db, "created"),
               "updated": time.time(), "phase": phase, "exit_code": code, "last_error": error[:2000],
               "completion": bool(_full_get(db, "completion", False)),
               "database": out + ".sqlite3", "parts_dir": os.path.splitext(out)[0] + ".parts",
               "attempts": {"total": attempts[0], "failed_or_interrupted": attempts[1]},
               "page_coverage": _full_coverage(db),
               "csv_quality": {"stored_entities": totals[0], "missing_phone": totals[1] or 0,
                               "exported_rows": totals[2] or 0,
                               "scope_rows": totals[0] if scope == "all" else _full_get(db, "count_mobile", 0),
                               "invalid_phone_quarantined": _full_get(db, "count_invalid", 0),
                               "phone_policy": "invalid URI retained in raw_phone; CSV phone blank; mobile export excludes it",
                               "parts": _full_get(db, "count_parts", 0),
                               "formula_protection": "leading apostrophe", "final": _full_get(db, "final")}}
    with db:
        _full_set(db, "phase", phase)
        _full_set(db, "last_exit", code)
        _full_set(db, "last_error", error[:2000])
    atomic_write(out + ".job.json", json.dumps(summary, ensure_ascii=False, indent=2))


def _full_disk(out, minimum):
    free = shutil.disk_usage(os.path.dirname(out) or ".").free
    if free < minimum * 1024 * 1024:
        raise OSError("剩余磁盘空间不足--min-free-mb：%.1f MiB" % (free / 1024 / 1024))


def _full_robots(db, args):
    if getattr(args, "skip_robots_check", False):
        log.warning("[全量 robots] 使用用户明确授权的跳过选项")
        return ""
    allowed, detail, body = check_robots(args.user_agent, args.timeout)
    if allowed is not True:
        raise OSError("robots不允许或无法确认：" + detail)
    if body:
        for row in db.execute("SELECT url FROM categories"):
            ok, reason = robots_allowed(body, args.user_agent, urllib.parse.urlsplit(row[0]).path)
            if not ok:
                raise OSError("robots禁止分类：%s (%s)" % (row[0], reason))
    return body


def _full_seed(db, name, url, start, end):
    db.executemany("INSERT OR IGNORE INTO pages(url,category,number,kind) VALUES(?,?,?,'category')",
                   ((url if number == 1 else url + "page/%d/" % number, name, number)
                    for number in range(start, end + 1)))


def _full_parse_commit(db, task, body, args):
    if not isinstance(body, str) or len(body.encode("utf-8")) > 8 * 1024 * 1024:
        raise StructureChanged("页面超过8MiB或不是文本")
    category = (db.execute("SELECT * FROM categories WHERE name=?", (task["category"],)).fetchone()
                if task["kind"] == "category" else None)
    probe = _FullProbe(category["url"] if category is not None else "")
    probe.feed(body)
    probe.close()
    now = time.time()
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    if task["kind"] in ("home", "catalog"):
        urls = probe.categories
        # 兼容仅在非a节点模板中出现的标准CAT_RE分类引用。
        for match in CAT_RE.findall(body):
            path = match[0] if isinstance(match, tuple) else match
            url = urllib.parse.urljoin(BASE + "/", path)
            if _full_origin(url, "/cat/") and re.fullmatch(r"/cat/[a-z0-9-]+/", urllib.parse.urlsplit(url).path, re.I):
                urls.add(url)
        selected = _full_get(db, "config")["selected_categories"]
        discovered = {urllib.parse.urlsplit(url).path.strip("/").split("/")[-1] for url in urls}
        if (not urls or (task["kind"] == "catalog" and selected and not set(selected).issubset(discovered))):
            raise StructureChanged("首页分类为空或指定分类未发现，索引不能标完成")
        with db:
            if task["kind"] == "home":
                db.execute("INSERT OR IGNORE INTO pages(url,category,number,kind) VALUES(?,?,?,?)",
                           (BASE + "/categories/", "", 1, "catalog"))
            for url in sorted(urls):
                name = urllib.parse.urlsplit(url).path.strip("/").split("/")[-1]
                if not selected or name in selected:
                    db.execute("INSERT OR IGNORE INTO categories(url,name) VALUES(?,?)", (url, name))
                    _full_seed(db, name, url, 1, 1)
            db.execute("UPDATE pages SET status='done',error='',rows=0,item_count=0,body_sha=?,updated=? WHERE url=?",
                       (digest, now, task["url"]))
            _full_set(db, "discovered_category_count", len(discovered))
            _full_set(db, "consecutive_failures", 0)
        return
    parsed = parse_rows(body)
    total, empty = probe.summary()
    if probe.canonical and urllib.parse.urlsplit(probe.canonical).path.rstrip("/") != urllib.parse.urlsplit(task["url"]).path.rstrip("/"):
        raise StructureChanged("Canonical URL does not match requested category page")
    if probe.page_number is not None and probe.page_number != task["number"]:
        raise StructureChanged("Reported current page does not match requested page")
    if db.execute("SELECT 1 FROM pages WHERE category=? AND number!=? AND status='done' AND body_sha=? LIMIT 1",
                  (task["category"], task["number"], digest)).fetchone():
        raise StructureChanged("Different category pages returned identical HTML")
    if len(parsed) != probe.items or (not parsed and not empty):
        raise StructureChanged("页面观测%d个列表项，但解析%d条；没有明确空列表标记" % (probe.items, len(parsed)))
    if not parsed and total not in (None, 0):
        raise StructureChanged("空列表与页面总条数不一致")
    if parsed and db.execute("SELECT 1 FROM pages WHERE category=? AND status='done' AND url!=? AND body_sha=? LIMIT 1",
                             (task["category"], task["url"], digest)).fetchone():
        raise StructureChanged("不同分页返回完全相同的非空HTML，疑似重定向/分页结构损坏")
    category = db.execute("SELECT * FROM categories WHERE name=?", (task["category"],)).fetchone()
    new_pages = max(category["pages"], probe.pages, task["number"])
    if total is not None and total < len(parsed):
        raise StructureChanged("页面总条数小于实际列表数")
    # 页面实体、任务扩展、分类索引和done标志在同一事务内提交。
    try:
        with db:
            for company, address, phone, display, detail in parsed:
                raw_phone = phone or ""
                phone_status = "missing" if not raw_phone else ("valid" if _FULL_PHONE_ALL.fullmatch(raw_phone) else "invalid")
                row = {"company": company, "address": address,
                       "phone": raw_phone if phone_status == "valid" else "",
                       "raw_phone": raw_phone, "phone_status": phone_status,
                       "display": display, "detail_url": urllib.parse.urljoin(task["url"], detail),
                       "source_page": task["url"], "category": task["category"]}
                _full_check_row(row, "all")
                inserted_entry = db.execute("""INSERT OR IGNORE INTO entries(company,phone,display,category,address,detail_url,source_page,raw_phone,phone_status)
                    VALUES(:company,:phone,:display,:category,:address,:detail_url,:source_page,:raw_phone,:phone_status)""", row).rowcount
                if inserted_entry:
                    _full_inc(db, "stored", 1)
                    _full_inc(db, phone_status, 1)
                    if MOBILE_RE.fullmatch(row["phone"]):
                        _full_inc(db, "mobile", 1)
                entry = db.execute("SELECT id FROM entries WHERE detail_url=? AND phone=?",
                                   (row["detail_url"], row["phone"])).fetchone()[0]
                inserted = db.execute("INSERT OR IGNORE INTO page_entries(page_url,entry_id) VALUES(?,?)",
                                      (task["url"], entry)).rowcount
                if not inserted:
                    raise ValueError("同页出现重复业务实体，不能伪造解析条数")
            _full_seed(db, category["name"], category["url"], category["pages"] + 1, new_pages)
            db.execute("UPDATE categories SET pages=?,index_state='done',total=coalesce(?,total) WHERE name=?",
                       (new_pages, total, category["name"]))
            db.execute("UPDATE pages SET status='done',error='',rows=?,item_count=?,body_sha=?,updated=? WHERE url=?",
                       (len(parsed), probe.items, digest, now, task["url"]))
            _full_set(db, "consecutive_failures", 0)
    except ValueError as exc:
        raise StructureChanged("列表字段/业务键校验失败：" + str(exc)) from exc


def _full_failure(db, task, error, limit, pause):
    attempts = db.execute("SELECT attempts FROM pages WHERE url=?", (task["url"],)).fetchone()[0]
    wait = max(min(3600, 30 * (2 ** min(attempts - 1, 7))), getattr(error, "retry_after", 0))
    streak = _full_get(db, "consecutive_failures", 0) + 1
    with db:
        db.execute("UPDATE pages SET status=?,not_before=?,error=?,updated=? WHERE url=?",
                   ("failed" if attempts >= limit else "pending", time.time() + wait,
                    str(error)[:2000], time.time(), task["url"]))
        if task["kind"] == "category" and task["number"] == 1:
            db.execute("UPDATE categories SET index_state=? WHERE name=?",
                       ("failed" if attempts >= limit else "pending", task["category"]))
        _full_set(db, "consecutive_failures", streak)
        if streak >= 3:
            _full_set(db, "cooldown_until", time.time() + max(60, pause))
            _full_set(db, "consecutive_failures", 0)
    log.warning("[全量失败 %d/%d] %s：%s", attempts, limit, task["url"], error)
    return streak >= 3


def _full_wait(seconds, deadline):
    until = time.monotonic() + max(0, seconds)
    while time.monotonic() < until:
        if _INTERRUPTED:
            raise KeyboardInterrupt()
        if deadline is not None and time.monotonic() >= deadline:
            return False
        remaining = until - time.monotonic()
        if deadline is not None:
            remaining = min(remaining, deadline - time.monotonic())
        time.sleep(max(0, min(1, remaining)))
    return True


def full_verify(args_or_path, phone_scope=None):
    """离线验收全量任务；接受Namespace或最终CSV路径，缺口返回6。"""
    out = os.path.abspath(os.fspath(args_or_path) if isinstance(args_or_path, (str, bytes, os.PathLike)) else args_or_path.out)
    lock = None
    db = None
    try:
        lock = file_lock(out + ".lock")
        if lock is None:
            return EXIT_LOCKED
        expected_config = None if isinstance(args_or_path, (str, bytes, os.PathLike)) else _full_config(args_or_path)
        db = _full_open(out, config=expected_config)
        if phone_scope is not None and _full_get(db, "config")["phone_scope"] != phone_scope:
            raise ValueError("验收号码scope与数据库不一致")
        coverage = _full_verify_db(db, out, require_final=True)
        _full_metadata(db, out, "verified", EXIT_OK)
        log.info("[全量验收] 成功：%d页，最终CSV与SQLite一致", coverage["expected_pages"])
        return EXIT_OK
    except (ValueError, OutputProtected, FileNotFoundError, csv.Error) as exc:
        log.error("[全量验收] %s", exc)
        return EXIT_INSUFFICIENT
    except (OSError, sqlite3.Error) as exc:
        log.error("[全量验收环境] %s", exc)
        return EXIT_ENV
    except KeyboardInterrupt:
        return EXIT_INTERRUPTED
    finally:
        if db is not None:
            db.close()
        if lock is not None:
            lock.close()


def fullrun(args):
    """有界内存全量抓取/自动续跑；不依赖旧缓存、清单、索引或resume。"""
    global STORE_HTTP_CACHE
    if getattr(args, "full_verify", False):
        return full_verify(args)
    started = time.monotonic()
    budget = getattr(args, "max_minutes", None)
    deadline = started + budget * 60 if budget is not None else None
    out = os.path.abspath(args.out)
    db = None
    lock = None
    site_lock = None
    previous_cache = globals().get("STORE_HTTP_CACHE", True)
    STORE_HTTP_CACHE = False
    scope = getattr(args, "phone_scope", "mobile")
    code = EXIT_ENV
    error = ""
    phase = "starting"
    try:
        if getattr(args, "from_page", 1) not in (None, 1) or getattr(args, "to_page", None) is not None:
            raise ValueError("--all不接受--from-page/--to-page裁剪；使用--categories声明范围")
        chunk_pages = getattr(args, "chunk_pages", 25)
        pause = getattr(args, "chunk_pause", 30)
        limit = getattr(args, "page_attempts", 4)
        chunks_limit = getattr(args, "max_chunks", None)
        minimum = getattr(args, "min_free_mb", 512)
        if (scope not in ("mobile", "all") or chunk_pages < 1 or pause < 0 or limit < 1
                or minimum < 0 or (chunks_limit is not None and chunks_limit < 1)
                or (budget is not None and budget <= 0)):
            raise ValueError("全量参数范围无效")
        parent = os.path.dirname(out) or "."
        os.makedirs(parent, exist_ok=True)
        if not getattr(args, "export", False):
            site_lock = file_lock(LOCK_PATH)
            if site_lock is None:
                return EXIT_LOCKED
        lock = file_lock(out + ".lock")
        if lock is None:
            return EXIT_LOCKED
        _full_disk(out, minimum)
        db = _full_open(out, _full_config(args), create=not getattr(args, "export", False))
        _full_export_parts(db, out, scope)
        _full_verify_db(db, out, require_final=False)
        with db:
            # 被强杀的最后一次尝试已经计入上限，不能靠反复重跑突破预算。
            db.execute("UPDATE pages SET status='failed',error=CASE WHEN error='' THEN '尝试上限耗尽或前次被中断' ELSE error END WHERE status='pending' AND attempts>=?", (limit,))
            db.execute("UPDATE categories SET index_state='failed' WHERE EXISTS(SELECT 1 FROM pages p WHERE p.category=categories.name AND p.number=1 AND p.status='failed')")
        if getattr(args, "export", False):
            _full_verify_db(db, out, require_final=False)
            if _full_coverage(db)["complete"]:
                count, digest = _full_publish(db, scope, out)
                with db:
                    _full_set(db, "final", {"count": count, "sha256": digest, "schema": CSV_COLS})
                    _full_set(db, "completion", True)
                _full_verify_db(db, out, require_final=True)
                code, phase = EXIT_OK, "completed"
            else:
                code, phase = EXIT_PARTIAL, "snapshot_partial"
        chunks = 0
        while not getattr(args, "export", False):
            if _INTERRUPTED:
                raise KeyboardInterrupt()
            coverage = _full_coverage(db)
            if coverage["complete"]:
                phase = "finalizing"
                _full_export_parts(db, out, scope)
                _full_verify_db(db, out, require_final=False)
                count, digest = _full_publish(db, scope, out)
                with db:
                    _full_set(db, "final", {"count": count, "sha256": digest, "schema": CSV_COLS})
                    _full_set(db, "completion", True)
                _full_verify_db(db, out, require_final=True)
                code, phase = EXIT_OK, "completed"
                break
            if deadline is not None and time.monotonic() >= deadline:
                code, phase = EXIT_PARTIAL, "budget_paused"
                break
            if chunks_limit is not None and chunks >= chunks_limit:
                code, phase = EXIT_PARTIAL, "chunk_paused"
                break
            pending = db.execute("SELECT min(not_before) FROM pages WHERE status='pending' AND attempts<?", (limit,)).fetchone()[0]
            if pending is None:
                code, phase = EXIT_INSUFFICIENT, "incomplete"
                error = "存在失败页、索引失败或页面总数/实体总数缺口，需要人工诊断修复"
                break
            wait = max(0, pending - time.time(), _full_get(db, "cooldown_until", 0) - time.time())
            if wait and not _full_wait(wait, deadline):
                code, phase = EXIT_PARTIAL, "budget_paused"
                break
            _full_disk(out, minimum)
            robots_body = _full_robots(db, args)
            phase = "collecting"
            chunks += 1
            attempts_this_chunk = 0
            while attempts_this_chunk < chunk_pages:
                if _INTERRUPTED:
                    raise KeyboardInterrupt()
                if deadline is not None and time.monotonic() >= deadline:
                    break
                task = db.execute("""SELECT * FROM pages WHERE status='pending' AND attempts<? AND not_before<=?
                    ORDER BY not_before,category,number LIMIT 1""",
                                  (limit, time.time())).fetchone()
                if task is None:
                    break
                if robots_body:
                    allowed, reason = robots_allowed(robots_body, args.user_agent, urllib.parse.urlsplit(task["url"]).path)
                    if not allowed:
                        raise OSError("robots禁止任务页面：%s (%s)" % (task["url"], reason))
                with db:
                    db.execute("UPDATE pages SET attempts=attempts+1,updated=? WHERE url=?", (time.time(), task["url"]))
                attempts_this_chunk += 1
                timeout = args.timeout
                if deadline is not None:
                    timeout = max(0.1, min(timeout, deadline - time.monotonic()))
                log.info("[全量段%d 页%d/%d] %s", chunks, attempts_this_chunk, chunk_pages, task["url"])
                try:
                    body, _ = fetch(task["url"], args.delay, False, 1, timeout, args.user_agent, args.jitter)
                    _full_parse_commit(db, task, body, args)
                except (Fatal, StructureChanged) as exc:
                    _full_failure(db, task, exc, limit, pause)
                    raise
                except (Unavailable, RuntimeError, urllib.error.URLError, TimeoutError, OSError) as exc:
                    if _full_failure(db, task, exc, limit, pause):
                        break
            # 每个新段在导出提交前已逐行验收；避免每段重扫全部历史CSV。
            _full_export_parts(db, out, scope)
            _full_metadata(db, out, "chunk_committed", EXIT_PARTIAL)
            if _full_coverage(db)["complete"]:
                continue
            if deadline is not None and time.monotonic() >= deadline:
                code, phase = EXIT_PARTIAL, "budget_paused"
                break
            if chunks_limit is not None and chunks >= chunks_limit:
                code, phase = EXIT_PARTIAL, "chunk_paused"
                break
            if not _full_wait(pause, deadline):
                code, phase = EXIT_PARTIAL, "budget_paused"
                break
        _full_metadata(db, out, phase, code, error)
        log.info("[全量任务] %s；退出码%d；断点%s.sqlite3", phase, code, out)
    except Fatal as exc:
        code, phase, error = EXIT_BLOCKED, "blocked", str(exc)
    except StructureChanged as exc:
        code, phase, error = EXIT_STRUCTURE, "structure_changed", str(exc)
    except OutputProtected as exc:
        code, phase, error = EXIT_OUTPUT, "output_protected", str(exc)
    except KeyboardInterrupt:
        code, phase, error = EXIT_INTERRUPTED, "interrupted", "被中断，已提交页面保留"
    except ValueError as exc:
        code, phase, error = (EXIT_INSUFFICIENT if db is not None else EXIT_USAGE), "validation_failed", str(exc)
    except (OSError, sqlite3.Error, csv.Error) as exc:
        code, phase, error = EXIT_ENV, "environment_error", str(exc)
    finally:
        if db is not None:
            try:
                if code != EXIT_OK and phase != "output_protected":
                    if code != EXIT_PARTIAL:
                        with db:
                            _full_set(db, "completion", False)
                    _full_export_parts(db, out, scope)
                    _full_metadata(db, out, phase, code, error)
            except (OSError, sqlite3.Error, ValueError, OutputProtected, csv.Error) as exc:
                log.error("[全量保存失败] %s", exc)
                code = EXIT_OUTPUT if isinstance(exc, OutputProtected) else EXIT_ENV
                error = str(exc)
            db.close()
        if lock is not None:
            lock.close()
        if site_lock is not None:
            site_lock.close()
        STORE_HTTP_CACHE = previous_cache
    if code not in (EXIT_OK, EXIT_PARTIAL):
        log.error("[全量任务] %s：%s；退出码%d", phase, error, code)
    return code


def build_parser() -> argparse.ArgumentParser:
    """构建参数解析器。"""
    ap = argparse.ArgumentParser(
        prog="scrape_malaysiayp.py",
        description="malaysiayp.com 按站点结构抓取「公司名 + 01X 手机号」"
                    "（确定性解析，可脱离 LLM 运维）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="退出码: " + " | ".join("%d=%s" % (k, v) for k, v in sorted(EXIT_DOC.items()))
               + "\n更多说明: --manual | --examples | --print-api")

    g_mode = ap.add_argument_group("模式（互斥，默认=抓取）")
    g_mode.add_argument("--doctor", action="store_true", help="环境自检后退出")
    g_mode.add_argument("--verify", metavar="CSV", help="校验已有 CSV 后退出")
    g_mode.add_argument("--against", metavar="CSV",
                        help="配合 --verify：对比基线（如追加前的 .bak），"
                             "证明旧号码一条没丢")
    g_mode.add_argument("--coverage", action="store_true", help="报告下载覆盖与缺口后退出")
    g_mode.add_argument("--stress-test", action="store_true",
                        help="实测限流上限与冷却恢复曲线后退出（会主动连发请求）")
    g_mode.add_argument("--self-test", action="store_true",
                        help="离线自检：纯函数回归测试后退出（零网络）")
    g_mode.add_argument("--check-robots", action="store_true", help="只检查 robots.txt 后退出")
    g_mode.add_argument("--manual", action="store_true", help="打印完整手册后退出")
    g_mode.add_argument("--examples", action="store_true", help="打印示例后退出")
    g_mode.add_argument("--print-api", action="store_true", help="打印函数接口速查后退出")

    g_size = ap.add_argument_group("数量 / 范围")
    g_size.add_argument("--all", action="store_true", help="无总条数限制；分段全量采集（无 --n/--preset 时默认启用）")
    g_size.add_argument("--chunk-pages", type=int, default=25, help="每段最多页面尝试数（默认25）")
    g_size.add_argument("--chunk-pause", type=float, default=30.0, help="段间冷却秒数（默认30）")
    g_size.add_argument("--max-chunks", type=int, default=None, help="本次最多段数；暂停后原命令自动续跑")
    g_size.add_argument("--page-attempts", type=int, default=4, help="跨段单页尝试上限（默认4）")
    g_size.add_argument("--min-free-mb", type=int, default=512, help="磁盘空间安全阈值MiB（默认512）")
    g_size.add_argument("--phone-scope", choices=["mobile", "all"], default="mobile", help="导出手机号或全部目录记录；原始记录均入库")
    g_size.add_argument("--export", action="store_true", help="从全量SQLite流式导出当前快照")
    g_size.add_argument("--full-verify", action="store_true", help="验收全量作业页覆盖、分段哈希与最终CSV")
    g_size.add_argument("--n", type=int, default=None, help="显式选择抽样模式的目标条数（无最大100条限制）")
    g_size.add_argument("--preset", choices=sorted(PRESETS),
                        help="规模预设 tiny/small/medium/large")
    g_size.add_argument("--max-pages", type=int, default=None, help="最多抓多少页（默认 30）")
    g_size.add_argument("--per-cat", type=int, default=None,
                        help="单分类上限（默认 10；0 = 不限）")
    g_size.add_argument("--order", choices=["random", "sequential"], default="random",
                        help="遍历顺序：sequential 按分类顺序+页码升序（默认 random）")
    g_size.add_argument("--categories", default=None,
                        help="只抓这些分类，逗号分隔（如 hotels,eating-places）")
    g_size.add_argument("--from-page", type=int, default=1, help="起始页码（含，默认 1）")
    g_size.add_argument("--to-page", type=int, default=None, help="结束页码（含，默认到末页）")

    g_net = ap.add_argument_group("网络 / 限流")
    g_net.add_argument("--delay", type=float, default=DEFAULT_DELAY,
                       help="请求间隔秒（默认 2.0）")
    g_net.add_argument("--jitter", type=float, default=DEFAULT_JITTER,
                       help="间隔随机抖动上限秒（默认 0.5）")
    g_net.add_argument("--retries", type=int, default=3, help="单页重试次数（默认 3）")
    g_net.add_argument("--timeout", type=int, default=30, help="单请求超时秒（默认 30）")
    g_net.add_argument("--max-minutes", type=float, default=None, help="时间预算（分钟）")
    g_net.add_argument("--user-agent", default=UA, help="覆盖 User-Agent")
    g_net.add_argument("--seed", type=int, default=20261007, help="随机种子（默认 20261007）")

    g_out = ap.add_argument_group("输出保护")
    g_out.add_argument("--out", default=None,
                       help="CSV 输出路径")
    g_out.add_argument("--force", action="store_true", help="已存在时允许覆盖（默认拒绝）")
    g_out.add_argument("--append", action="store_true",
                       help="增量追加到已有 CSV（按 phone 去重）")
    g_out.add_argument("--no-backup", action="store_true", help="覆盖前不备份 .bak")

    g_sw = ap.add_argument_group("开关")
    g_sw.add_argument("--reindex", action="store_true", help="强制重建索引")
    g_sw.add_argument("--no-cache", action="store_true", help="忽略缓存，全部重新抓")
    g_sw.add_argument("--dry-run", action="store_true", help="只索引，不抓条目页")
    g_sw.add_argument("--resume", action="store_true", help="从 cache/state.json 断点续跑")
    g_sw.add_argument("--no-lock", action="store_true", help="不获取互斥锁（默认会获取）")
    g_sw.add_argument("--allow-low-yield", action="store_true", help="条数不足时仍返回 0")
    g_sw.add_argument("--skip-robots-check", action="store_true",
                      help="跳过 robots.txt 检查（仅在已获授权时使用）")
    g_sw.add_argument("--skip-net", action="store_true", help="配合 --doctor：跳过联网检查")
    g_sw.add_argument("--probe", type=int, default=0,
                      help="配合 --verify：抽样探测来源页条数")
    g_sw.add_argument("-v", "--verbose", action="store_true", help="调试日志")

    g_st = ap.add_argument_group("限流探针（配合 --stress-test）")
    g_st.add_argument("--stress-burst", type=int, default=30,
                      help="阶段 A 连发次数（默认 30）")
    g_st.add_argument("--stress-burst-delay", type=float, default=0.3,
                      help="阶段 A 连发间隔秒（默认 0.3，越小越快撞墙）")
    g_st.add_argument("--stress-cooldown", type=int, default=120,
                      help="阶段 B 最长冷却观察秒数（默认 120）")
    g_st.add_argument("--stress-rates", default="1,2,3",
                      help="阶段 C 要测的请求间隔，逗号分隔（默认 1,2,3）")
    g_st.add_argument("--stress-rate-n", type=int, default=10,
                      help="阶段 C 每个间隔发多少次（默认 10）")
    g_st.add_argument("--stress-rate-gap", type=int, default=30,
                      help="阶段 C 各间隔之间的冷却秒数（默认 30，消除顺序效应）")
    g_st.add_argument("--stress-backoff", default="6,12,24",
                      help="阶段 D 复现的退避表，逗号分隔秒（默认 6,12,24）")
    g_st.add_argument("--stress-backoff-rounds", type=int, default=4,
                      help="阶段 D 轮数（默认 4）")
    g_st.add_argument("--stress-recover-streak", type=int, default=3,
                      help="阶段 B 判定「稳定恢复」所需连续成功次数（默认 3）")
    g_st.add_argument("--stress-max-requests", type=int, default=400,
                      help="总请求硬上限（默认 400，防跑飞）")
    return ap


def main(argv: Optional[Sequence[str]] = None) -> int:
    """程序入口。

    :return: 退出码（见 EXIT_DOC）
    """
    ap = build_parser()
    a = ap.parse_args(argv)

    # ---- 只读模式：不需要日志文件，直接打印后返回 ----
    # 注意：用 .replace() 而不是 .format()。手册正文里会出现正则花括号（如 01[0-9]{7,8}），
    # .format() 会把 {7,8} 当成格式字段并抛 KeyError —— 曾因此把 --manual 打成崩溃。
    if a.manual:
        print(FULL_MANUAL)
        print(MANUAL.replace("{ver}", __version__))
        return EXIT_OK
    if a.examples:
        print(EXAMPLES)
        return EXIT_OK
    if a.print_api:
        print(API_DOC)
        return EXIT_OK

    a.all = a.all or a.export or a.full_verify or (a.n is None and a.preset is None and not a.dry_run)
    if a.all and a.dry_run:
        ap.error("--all 与 --dry-run 不混用；--dry-run 单独使用只索引")
    if a.out is None:
        a.out = os.path.join(DATADIR, "malaysiayp_full.csv" if a.all else "malaysiayp_sample.csv")
    if a.all and (a.n is not None or a.preset or a.max_pages is not None or a.per_cat is not None):
        ap.error("全量模式不能与 --n/--preset/--max-pages/--per-cat 混用")
    if (a.timeout <= 0 or (a.max_minutes is not None and (not math.isfinite(a.max_minutes) or a.max_minutes <= 0))
            or a.chunk_pages <= 0 or a.chunk_pages > 1000 or a.chunk_pause < 0
            or not math.isfinite(a.chunk_pause) or a.page_attempts <= 0 or a.min_free_mb < 0
            or (a.max_chunks is not None and a.max_chunks <= 0)
            or not math.isfinite(a.delay) or not math.isfinite(a.jitter)
            or (a.to_page is not None and a.to_page < a.from_page)):
        ap.error("超时/预算/段数/页尝试必须为正；每段1-1000页；浮点数须有限；页范围须有效")
    if a.export and a.full_verify:
        ap.error("--export 与 --full-verify 互斥")
    # ---- 预设展开（仅显式抽样模式使用） ----
    preset = PRESETS.get(a.preset or "medium", PRESETS["medium"])
    n = a.n if a.n is not None else preset["n"]
    max_pages = a.max_pages if a.max_pages is not None else preset["max_pages"]
    per_cat = a.per_cat if a.per_cat is not None else preset["per_cat"]

    # ---- 参数合法性（尽早失败，退出码 2）----
    # 注意：--per-cat 允许 0（= 不限单分类配额），故不参与「必须为正」的判定。
    if (n <= 0 or max_pages <= 0 or per_cat < 0 or a.retries <= 0
            or a.delay < 0 or a.jitter < 0 or a.from_page < 1):
        ap.error("--n/--max-pages/--retries/--from-page 必须为正；"
                 "--per-cat 必须 >= 0（0 = 不限单分类配额）；"
                 "--delay/--jitter 不能为负")
        return EXIT_USAGE
    if a.force and a.append:
        ap.error("--force 与 --append 不能同时使用")
        return EXIT_USAGE

    _, log_path = setup_logging(a.verbose)
    _install_signal_handlers()
    log.info(BANNER)
    log.info("脚本 v%s | 指纹 %s | 日志 %s\n", __version__,
             source_fingerprint()["sha256"], log_path or "(不可用)")

    # ============ 只读模式 ============
    if a.self_test:
        return cmd_self_test()
    if a.stress_test:
        try:
            rates = [float(x) for x in str(a.stress_rates).split(",") if x.strip()]
            backoff = [int(x) for x in str(a.stress_backoff).split(",") if x.strip()]
        except ValueError:
            ap.error("--stress-rates / --stress-backoff 必须是逗号分隔的数字")
            return EXIT_USAGE
        if not rates or any(v <= 0 for v in rates):
            ap.error("--stress-rates 必须全为正数")
            return EXIT_USAGE
        if any(v <= 0 for v in backoff):
            ap.error("--stress-backoff 必须全为正整数秒")
            return EXIT_USAGE
        allowed, detail, _ = check_robots(a.user_agent, a.timeout)
        if allowed is False:
            log.error("[robots] 当前 UA 不被允许：%s，退出码 %d", detail, EXIT_ENV)
            return EXIT_ENV
        return cmd_stress_test(load_index(), a.stress_burst, a.stress_burst_delay,
                               a.stress_cooldown, rates, a.stress_rate_n,
                               a.timeout, a.user_agent, a.stress_max_requests,
                               a.stress_rate_gap, backoff,
                               a.stress_backoff_rounds, a.stress_recover_streak)
    if a.check_robots:
        return cmd_check_robots(a.user_agent, a.timeout)
    if a.doctor:
        return cmd_doctor(a.delay, a.timeout, a.user_agent, a.skip_net, a.jitter)
    if a.verify:
        return cmd_verify(a.verify, a.probe, a.timeout, a.user_agent, a.against)
    if a.coverage:
        return cmd_coverage(load_index(), a.verbose)

    if a.full_verify:
        return full_verify(a)
    if a.all:
        return fullrun(a)

    # ============ 显式抽样模式 ============
    # --- 互斥锁：防止计划任务重叠运行（会双倍限流）---
    lock = None
    if not a.no_lock:
        lock = file_lock(LOCK_PATH)
        if lock is None:
            log.error("[锁] 已有另一个实例在运行（%s）。退出码 %d。", LOCK_PATH, EXIT_LOCKED)
            log.error("     如确认没有，可加 --no-lock 强制运行。")
            return EXIT_LOCKED

    try:
        if not a.skip_robots_check:
            allowed, detail, _ = check_robots(a.user_agent, a.timeout)
            if allowed is None:
                log.warning("[robots] %s → 无法确认，继续（建议先跑 --check-robots）", detail)
            elif not allowed:
                log.error("[robots] 当前 UA 不被允许：%s", detail)
                log.error("        如你已获站点授权，可加 --skip-robots-check。退出码 %d。",
                          EXIT_ENV)
                return EXIT_ENV
            else:
                log.info("[robots] %s\n", detail)

        use_cache = not a.no_cache
        try:
            index = None if a.reindex else load_index()
            if index:
                log.info("[阶段 1] 复用已有索引（%s，%d 个分类）",
                         index.get("fetched_at"), len(index["categories"]))
            else:
                index = build_index(a.delay, use_cache, a.retries, a.timeout,
                                    a.user_agent, a.jitter)
        except Fatal as e:
            log.error("[阶段 1] 被封禁：%s，退出码 %d", e, EXIT_BLOCKED)
            return EXIT_BLOCKED
        except Exception as e:
            log.error("[阶段 1] 环境错误：%s，退出码 %d", e, EXIT_ENV)
            return EXIT_ENV

        if a.dry_run:
            log.info("\n[dry-run] 只索引，不抓条目页。退出码 %d", EXIT_OK)
            return EXIT_OK

        cats_filter = a.categories.split(",") if a.categories else None

        try:
            rows, stats = scrape(
                index, n, max_pages, per_cat, a.delay, a.seed, a.order,
                cats_filter, a.from_page, a.to_page, use_cache, a.retries,
                a.timeout, a.user_agent, a.jitter, a.resume, a.max_minutes)
        except Fatal:
            return EXIT_BLOCKED
        except StructureChanged as e:
            log.error("[阶段 3] %s 退出码 %d", e, EXIT_STRUCTURE)
            return EXIT_STRUCTURE
        except KeyboardInterrupt:
            log.warning("\n[中断] 已保存断点，可用 --resume 续跑。退出码 %d", EXIT_INTERRUPTED)
            return EXIT_INTERRUPTED
        except Exception as e:
            log.error("[阶段 3] 未预期错误：%s，退出码 %d", e, EXIT_ENV)
            return EXIT_ENV

        if not rows:
            log.error("[阶段 3] 没有抓到任何记录。退出码 %d", EXIT_INSUFFICIENT)
            return EXIT_INSUFFICIENT

        # ---- 输出保护（防误覆盖）----
        try:
            reason = guard_output(a.out, a.force, a.append, len(rows))
            if reason:
                log.error("[输出] ✗ %s", reason)
                log.error("        退出码 %d（未写入任何文件）", EXIT_OUTPUT)
                return EXIT_OUTPUT
        except OutputProtected as e:
            log.error("[输出] ✗ %s，退出码 %d", e, EXIT_OUTPUT)
            return EXIT_OUTPUT

        # ---- 追加模式：先「严格」读取旧数据，读不到就中止 ----
        # 绝不把「读不到旧文件」当成「没有旧数据」—— 那会让追加静默变成覆盖。
        old_n = 0
        added = len(rows)
        if a.append:
            try:
                old = read_existing_rows(a.out, strict=True)
            except IOError as e:
                log.error("[输出] ✗ %s", e)
                log.error("        为避免把「追加」变成「覆盖」，本次未写入任何文件。退出码 %d",
                          EXIT_OUTPUT)
                return EXIT_OUTPUT
            old_n = len(old)
            rows, added = append_merge(old, rows)
            log.info("[输出] 追加模式：旧 %d 行 + 新增 %d 行 = %d 行",
                     old_n, added, len(rows))
            if added == 0:
                log.error("[输出] ✗ 追加模式下新增 0 条（抓到的号码全部与旧数据重复），"
                          "未写入任何文件。退出码 %d", EXIT_OUTPUT)
                log.error("        可换分类 / 调大 --n / 换 --seed 后再试。")
                return EXIT_OUTPUT

        # 追加前也备份：append 仍是「整文件重写」，备份是最后一道保险
        if not a.no_backup:
            try:
                backup_existing(a.out)
            except OutputProtected as e:
                log.error("[输出] %s", e)
                return EXIT_OUTPUT

        # ---- 条数判定：追加模式看「本次新增」，覆盖模式看「本次产出」----
        # （原实现用合并后的总数比 n，在追加模式下这个检查形同虚设）
        yield_n = added if a.append else len(rows)
        exit_code = EXIT_OK
        if yield_n < n:
            log.warning("[阶段 3] ⚠ 条数不足：目标 %d 条，实得 %d 条%s",
                        n, yield_n, "（本次新增）" if a.append else "")
            exit_code = EXIT_OK if a.allow_low_yield else EXIT_INSUFFICIENT

        out = write_csv(rows, a.out)
        params = {"n": n, "max_pages": max_pages, "per_cat": per_cat, "seed": a.seed,
                  "delay": a.delay, "jitter": a.jitter, "retries": a.retries,
                  "timeout": a.timeout, "order": a.order, "categories": cats_filter,
                  "from_page": a.from_page, "to_page": a.to_page,
                  "resume": a.resume, "append": a.append, "cache": use_cache,
                  "max_minutes": a.max_minutes}
        extra = dict(stats)
        if a.append:                       # 追加的账要记清：旧多少、新多少、合多少
            extra.update({"old_rows": old_n, "appended": added, "total_rows": len(rows)})
        write_meta(out, rows, params, exit_code, index, extra=extra)

        cats = sorted({r["category"] for r in rows})
        log.info("覆盖分类 %d 个: %s%s", len(cats), ", ".join(cats[:12]),
                 " ..." if len(cats) > 12 else "")
        log.info("产出文件: %s", out)
        log.info("下一步建议: --verify \"%s\" 校验质量；--coverage 看下载缺口", out)

        if exit_code == EXIT_OK:
            clear_state()
        log.info("退出码: %d (%s)", exit_code, EXIT_DOC.get(exit_code, ""))
        return exit_code
    finally:
        if lock is not None:
            try:
                lock.close()
            except Exception:
                pass


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(EXIT_INTERRUPTED)
