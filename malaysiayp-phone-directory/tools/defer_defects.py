# -*- coding: utf-8 -*-
"""缺陷页处置：可逆「软剔除」——分层延期重试，而非删除。

2026-10-08 实测把「坏响应」分成两类，恢复时间差两个数量级：

  A 型（短时限流）  200 + 0 字节。实测 automotive 首页被密集请求打到 0 字节，
                    静默 4 分钟后重测恢复 42990 B ⇒ 恢复是分钟级。
  B 型（坏缓存）    Content-Length: 32768(=2**15) 截断，或持续 0 字节，
                    X-Nextjs-Cache: HIT，Etag 恒定；?cb= / no-cache / no-store /
                    identity / gzip / br / RSC 等绕过手段全部失效
                    ⇒ 恢复周期 ≥ s-maxage=86400（24 小时）。

抽样复测（probe_recover.py，30 页 × 10s 间隔）：深层页恢复率 0.0%
⇒ 深层分页以 B 型为主；分类首页以 A 型为主。

因此延期时长按 attempts 阶梯上升，用最小时间代价同时覆盖两类：
  attempts 1   → +30 分钟   （等 A 型限流窗口过去）
  attempts 2   → +6 小时
  attempts ≥3  → +25 小时   （跨过 s-maxage=86400）

动作：只把 not_before 推到未来。不改 status / attempts / error，
      不破坏 _full_coverage 与 _full_verify_db 语义。可一键回滚（备份 JSON）。
"""
import sqlite3, json, os, time, sys

BASE = r"C:\Users\Admin\WorkBuddy AI\2026-10-07-16-32-42\phone-directory"
DB = os.path.join(BASE, "data", "malaysiayp_full.csv.sqlite3")
LADDER = [(1, 1, 1800.0), (2, 2, 6 * 3600.0), (3, 10 ** 9, 25 * 3600.0)]
DEFER = 6 * 3600           # 兼容旧字段：备份元数据里记录的基准值
STAMP = time.strftime("%Y%m%d-%H%M%S")
BK = os.path.join(BASE, "data", "malaysiayp_full.defer-backup-%s.json" % STAMP)
LIST = os.path.join(BASE, "logs", "DEFECT-PAGES.json")

apply = "--apply" in sys.argv
rollback = "--rollback" in sys.argv

c = sqlite3.connect(DB, timeout=60)
c.row_factory = sqlite3.Row


def latest_backup():
    files = [f for f in os.listdir(os.path.join(BASE, "data"))
             if f.startswith("malaysiayp_full.defer-backup-") and f.endswith(".json")]
    if not files:
        return None
    files.sort()
    return os.path.join(BASE, "data", files[-1])


if rollback:
    bk = sys.argv[sys.argv.index("--rollback") + 1] if len(sys.argv) > sys.argv.index("--rollback") + 1 else latest_backup()
    if not bk or not os.path.exists(bk):
        print("找不到备份文件")
        sys.exit(2)
    with open(bk, encoding="utf-8") as fh:
        data = json.load(fh)
    print("=" * 76)
    print(" 回滚：%s" % os.path.basename(bk))
    print("=" * 76)
    print("  备份创建于 %s，含 %d 页" % (data.get("created"), data.get("count", 0)))
    n = 0
    with c:
        for r in data["pages"]:
            c.execute("UPDATE pages SET not_before=? WHERE url=? AND status='pending'",
                      (r["not_before"], r["url"]))
            n += 1
    ready = c.execute("""SELECT count(*) FROM pages
                         WHERE status='pending' AND attempts<30 AND not_before<=?""",
                      (time.time(),)).fetchone()[0]
    print("  已恢复 %d 页的 not_before" % n)
    print("  验证：当前可抓取页数 = %d" % ready)
    c.close()
    sys.exit(0)


rows = [dict(r) for r in c.execute(
    """SELECT url,category,number,kind,status,attempts,not_before,error
       FROM pages WHERE status='pending' AND error<>'' ORDER BY category,number""")]

print("=" * 76)
print(" 缺陷页统计")
print("=" * 76)
print("  待处置（pending 且有错误）: %d 页" % len(rows))
by_cat = {}
for r in rows:
    e = by_cat.setdefault(r["category"], {"n": 0, "zero": 0, "trunc": 0, "other": 0})
    e["n"] += 1
    if "响应过短(0B)" in r["error"]:
        e["zero"] += 1
    elif "响应过短" in r["error"]:
        e["trunc"] += 1
    else:
        e["other"] += 1
for k, v in sorted(by_cat.items(), key=lambda kv: -kv[1]["n"]):
    print("    %-38s %4d 页  (0B %d / 截断 %d / 其他 %d)" % (k, v["n"], v["zero"], v["trunc"], v["other"]))

# 备份
payload = {"created": time.strftime("%Y-%m-%d %H:%M:%S"), "defer_ladder": LADDER,
           "reason": "缺陷页分层延期重试（A型限流/B型坏缓存，可逆）",
           "count": len(rows), "pages": rows}
with open(BK, "w", encoding="utf-8") as fh:
    json.dump(payload, fh, ensure_ascii=False, indent=1)
print("\n  备份已写入: %s (%d 条)" % (os.path.basename(BK), len(rows)))

# 人类可读清单
with open(LIST, "w", encoding="utf-8") as fh:
    json.dump({"generated": payload["created"],
               "defer_ladder": [{"attempts_max": hi, "hours": round(wait / 3600.0, 2)}
                                for lo, hi, wait in LADDER],
               "count": len(rows), "by_category": by_cat,
               "pages": [{"category": r["category"], "number": r["number"],
                          "attempts": r["attempts"], "error": r["error"][:120]}
                         for r in rows]}, fh, ensure_ascii=False, indent=1)
print("  清单已写入: %s" % os.path.basename(LIST))

if not apply:
    print("\n  [干跑] 未修改数据库。加 --apply 执行。")
    c.close()
    sys.exit(0)

now = time.time()
tiers = []
with c:
    # 只延期「已经到期」的缺陷页（not_before <= now）。
    # 这样已延期到未来的页不会被重复推后 —— 否则定时执行会让它们永远回不来。
    for lo, hi, wait in LADDER:
        n = c.execute(
            """UPDATE pages SET not_before=?
               WHERE status='pending' AND error<>'' AND not_before<=?
                 AND attempts>=? AND attempts<=?""",
            (now + wait, now, lo, hi)).rowcount
        tiers.append((lo, hi, wait, n))
n = sum(t[3] for t in tiers)
print("\n  分层延期：")
for lo, hi, wait, cnt in tiers:
    tag = ("attempts>=%d" % lo) if hi > 1000 else (
        "attempts=%d" % lo if lo == hi else "attempts %d-%d" % (lo, hi))
    span = ("%.0f 分钟" % (wait / 60.0)) if wait < 3600 else ("%.0f 小时" % (wait / 3600.0))
    print("    %-16s → +%-9s %4d 页" % (tag, span, cnt))
print("    合计延期 %d 页" % n)

# 验证
left = c.execute("""SELECT count(*) FROM pages
                    WHERE status='pending' AND error<>'' AND not_before<=?""",
                 (now,)).fetchone()[0]
ready = c.execute("""SELECT count(*) FROM pages
                     WHERE status='pending' AND attempts<30 AND not_before<=?""",
                  (now,)).fetchone()[0]
still = c.execute("""SELECT count(*) FROM pages
                     WHERE status='pending' AND attempts<30 AND not_before>?""",
                  (now,)).fetchone()[0]
print("  验证：仍在当前队列的缺陷页 = %d（应为 0）" % left)
print("  验证：当前可抓取页数 = %d，仍在延期中 = %d" % (ready, still))
c.close()

# 备份文件清理：只保留最近 12 个
bks = sorted(f for f in os.listdir(os.path.join(BASE, "data"))
             if f.startswith("malaysiayp_full.defer-backup-") and f.endswith(".json"))
for old in bks[:-12]:
    try:
        os.remove(os.path.join(BASE, "data", old))
    except OSError:
        pass
print("  备份文件保留 %d 个（已清理更旧的）" % min(len(bks), 12))
