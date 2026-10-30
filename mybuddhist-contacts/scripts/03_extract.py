#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段3: 从正文提取联系人姓名 + 电话号码，输出 CSV（v2: 就近配对）"""
import json, os, re, csv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
IN = os.path.join(ROOT, "articles.jsonl")
OUT = os.path.join(ROOT, "mybuddhist_contacts.csv")

# ---------- 电话 ----------
PHONE = re.compile(
    r"(?<![\d/.\-])"
    r"(?:\+?60[\s\-]?|0)"
    r"(?:1[0-9]|[2-9])"
    r"(?:[\s\-]?\d{3,4}){1,2}[\s\-]?\d{3,4}"
    r"(?![\d])"
)

# ---------- 姓名 ----------
ROLE = r"(?:先生|女士|小姐|居士|法师|法師|师兄|师姐|师兄姐|老师|校長|校长|秘书|会长|主席|理事|主任|师父|医师|医生|博士|同学|住持|执行长|总干事|团长|林长|营长|辅导员|讲师)"
TITLE_PREFIX = ("秘书处|办事处|询问处|报名处|联络处|总务处|教务处|筹委主席|工委会主席|执行秘书|弘法组主任|副主席|副营长|副主任|主席|主任|营长|团长|林长|"
                "秘书|会长|理事|总务|财政|校长|住持|组长|班长|队长|顾问|干事|协调员|辅导员|"
                "筹委会主席|工委主席|副会长|副秘书|副财政|副团长|副理事")
NAME_TAIL = re.compile(
    r"(?:" + TITLE_PREFIX + r")?([\u4e00-\u9fa5]{2,4})(?:" + ROLE + r")?\s*[（(]?\s*[：:]?\s*[，,、]?\s*$"
)
NAME_EN_TAIL = re.compile(
    r"([A-Z][A-Za-z\.]{1,14}(?:\s+[A-Z][A-Za-z\.]+){0,2})\s*[（(]?\s*[：:]?\s*[，,、]?\s*$"
)

STOP_WORD = set("""电话 手机 联络 联系 洽询 询问 报名 详情 查询 致电 传真 地址 日期 时间 地点
活动 主办 联办 承办 协办 主讲 主法 费用 报名费 备注 网址 电邮 邮址 面子书 短讯 报名处 秘书处
负责人 联络人 联系人 询问处 详情请 有意 欢迎 敬请 佛光 佛教 寺院 佛堂 中心 会馆 协会 学会 学院
人数 名额 截止 表格 网站 办公 上午 下午 晚上 星期 农历 每日 每逢 报名 洽询 询问 联络 通讯
法师 居士 老师 师兄 师姐 先生 女士 小姐 长老 和尚 上人 仁波切 堪布 喇嘛 校长 会长 主席 理事 主任
欢迎 公众 大众 各界 佛友 信众 电话 传真 电邮 短讯 面子书 书记 财政 副主 总务 查账 委员 组员
以及 或者 如有 任何 疑问 请洽 请联络 请电 请致电 办公时间 早上 中午 傍晚 凌晨 每日 时间 收费
""".split())
BAD_SUFFIX = ("会", "寺", "堂", "中心", "协会", "学会", "学院", "团", "组", "处", "部", "社",
              "宫", "庙", "庵", "精舍", "委员", "公司", "基金", "苑", "舍", "院", "校", "局", "馆",
              "居", "轩", "楼", "殿", "堂", "旅游", "旅行社", "企业", "机构", "单位", "坊", "座办", "办事处", "询问处", "报名处")
BAD_HEAD = set("的了和与及或请在於于为对从到向往把被让给这那此其该各个每些有是无不很就都也还又再处办座坊")

def norm_phone(p):
    d = re.sub(r"[^\d+]", "", p)
    if d.startswith("+60"):
        d = "0" + d[3:]
    elif d.startswith("60"):
        d = "0" + d[2:]
    if not d.startswith("0"):
        d = "0" + d
    return d

def valid_phone(p):
    d = re.sub(r"\D", "", p)
    if d.startswith("60"):
        d = d[2:]
    if not d.startswith("0"):
        return False
    if len(d) < 8 or len(d) > 11:
        return False
    # 排除日期串 dd-mm-yyyy / yyyy-mm-dd
    if len(d) == 8 and re.search(r"(19|20)\d{2}$", d):
        return False
    if re.match(r"^0(19|20)\d", d) and len(d) == 8:
        return False
    if re.match(r"^01[0-9]", d):
        return 9 <= len(d) <= 11
    if re.match(r"^0[2-9]", d):
        return 8 <= len(d) <= 10
    return False

def ok_name(n):
    if not n or not (2 <= len(n) <= 4):
        return False
    if n in STOP_WORD or n[0] in BAD_HEAD:
        return False
    if n[-1] in BAD_SUFFIX or n[-2:] in BAD_SUFFIX:
        return False
    if any(w in n for w in ("电话", "联络", "洽询", "报名", "询问", "详情", "查询")):
        return False
    if any(ch.isdigit() for ch in n):
        return False
    return True

def ok_name_en(n):
    if not n:
        return False
    n = n.strip(" .")
    if len(n) < 3:
        return False
    if n.upper() in ("TEL", "CALL", "FAX", "EMAIL", "WHATSAPP", "PBB", "MBB", "RHB", "CIMB", "PUBLIC", "BANK", "HONG", "LEONG"):
        return False
    return True

def extract(body):
    res, seen = [], set()
    last_name, last_pos = "", -1
    for m in PHONE.finditer(body):
        praw = m.group(0).strip(" -，,、；;：:")
        if not valid_phone(praw):
            continue
        np_ = norm_phone(praw)
        start = m.start()
        between = body[last_pos:start] if last_pos >= 0 else ""
        same_clause = not re.search(r"[；;。\n！!？?]", between)
        win = body[max(0, start - 40):start]
        # 窗口截断到最近的分句符，避免跨句取名字
        cut = max(win.rfind("；"), win.rfind(";"), win.rfind("。"), win.rfind("\n"),
                  win.rfind("/"), win.rfind("|"), win.rfind("｜"))
        if cut >= 0:
            win = win[cut + 1:]
        name, role, src = "", "", ""
        mm = NAME_TAIL.search(win)
        if mm and ok_name(mm.group(1)):
            name = mm.group(1)
            tail_win = win[mm.end(1):]
            r = re.match(r"\s*(" + ROLE + r")", tail_win)
            role = r.group(1) if r else ""
            src = "adjacent"
        else:
            me = NAME_EN_TAIL.search(win)
            if me and ok_name_en(me.group(1)):
                name = me.group(1).strip()
                src = "adjacent"
        # 电话后紧跟姓名（无括号）
        if not name:
            mt = re.match(r"\s*[（(]?\s*([\u4e00-\u9fa5]{2,4})(?:" + ROLE + r")?\s*[)）]?(?=[\s，,、；;。]|$)",
                          body[m.end():m.end() + 20])
            if mt and ok_name(mt.group(1)):
                name = mt.group(1)
                src = "after"
        # 同句继承前一联系人
        if not name and same_clause and last_name:
            name, src = last_name, "inherited"
        if name:
            last_name = name
        last_pos = m.end()
        key = (np_, name)
        if key in seen:
            continue
        seen.add(key)
        ctx = body[max(0, start - 60):m.end() + 60].replace("\n", " ").strip()
        res.append((name, role, praw, np_, ctx, src))
    return res

rows, n_art = [], 0
for line in open(IN, encoding="utf-8"):
    try:
        a = json.loads(line)
    except Exception:
        continue
    n_art += 1
    body = a.get("body") or ""
    if not body:
        continue
    for name, role, praw, pnorm, ctx, src in extract(body):
        rows.append({
            "article_title": a.get("title", ""),
            "publish_date": a.get("date", ""),
            "organization": a.get("source", ""),
            "contact_name": name,
            "contact_role": role,
            "phone": praw,
            "phone_normalized": pnorm,
            "name_source": src,
            "context": ctx,
            "category": a.get("from_cat", ""),
            "url": a.get("url", ""),
        })

best = {}
for r in rows:
    k = (r["url"], r["phone_normalized"])
    if k not in best or (not best[k]["contact_name"] and r["contact_name"]):
        best[k] = r
rows = list(best.values())
rows.sort(key=lambda r: (r["publish_date"] or "", r["url"]), reverse=True)

cols = ["article_title", "publish_date", "organization", "contact_name", "contact_role",
        "phone", "phone_normalized", "name_source", "context", "category", "url"]
with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

named = sum(1 for r in rows if r["contact_name"])
print(f"文章 {n_art} 篇；记录 {len(rows)} 条；有姓名 {named}；无姓名 {len(rows)-named}")
print("CSV:", OUT)
