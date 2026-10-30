#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""中国报雪隆版 · 从文章正文提取联系人姓名 + 电话号码"""
import json, os, re, csv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.environ.get("SITE", "kl")
IN = os.path.join(ROOT, f"{SITE}_articles.jsonl")
OUT = os.path.join(ROOT, f"chinapress_{SITE}_contacts.csv")

# ---------- 电话（马来西亚） ----------
PHONE = re.compile(
    r"(?<![\d/.\-])"
    r"(?:\+?60[\s\-]?|0)"
    r"(?:1[0-9]|[2-9])"
    r"(?:[\s\-]?\d{3,4}){1,2}[\s\-]?\d{3,4}"
    r"(?![\d])"
)

# ---------- 姓名 ----------
ROLE = (r"(?:先生|女士|小姐|居士|法师|法師|师父|师兄|师姐|老师|校長|校长|秘书|会长|主席|理事|主任|"
        r"总务|财政|团长|营长|村长|州议员|国会议员|市议员|行政议员|部长|副部长|医生|医师|博士|"
        r"教授|工程师|律师|代表|发言人|经理|总监|执行长|总执行长|创办人|负责人|投诉主任|协调员|"
        r"副校长|警监|助理警监|警曹长|警长|警探|总编辑|主编|干事长|总会长|署理会长)")
TITLE_PREFIX = ("投诉局主任|执行秘书|总执行长|执行董事|副主席|副秘书|副主任|副财政|副团长|"
                "总策划|总协调|总干事|负责老师|票务组组长|查案官|大会主席|工委会主席|筹委会主席|"
                "拿督斯里|拿督威拉|准拿督|太平局绅|拿督|丹斯里|董事长|署理主席|执行长|销售经理|销售执行员|"
                "行政助理|活動執行官|活动执行官|執行官|执行官|財政|财政|大姐|二姐|助理|总领队|领队|总团长|团长|"
                "活动统筹|活動統籌|统筹|統籌|选区助理|選區助理|行政|行政处|" 
                "业务发展部|業務發展部|发展部|市場部|市场部|廣告部|广告部|票务|会务|财务|总务|教务|医务|筹募|"
                "商会会长|家协主席|校友会主席|主席|主任|营长|团长|林长|秘书|会长|理事|总务|财政|"
                "校长|住持|组长|班长|队长|顾问|干事|协调员|辅导员|村长|市议员|州议员|发言人|经理|总监|律师|医生")
NAME_TAIL = re.compile(
    r"(?:" + TITLE_PREFIX + r")?([\u4e00-\u9fa5]{2,4})(?:" + ROLE + r")?\s*[（(]?\s*[：:]?\s*[，,、]?\s*$"
)
# 尾部动作/连接词剥离（新闻文本里姓名常直接跟在动词后）
TAIL_STRIP = re.compile(
    r"(?:可|请|欲|如|欢迎|任何|详情请|详情|查询|询问|洽询|垂询|咨询|谘询|联络|联系|致电|拨打|拨电|"
    r"来电|电话|手机|号码|预约|报名|预订|订购|洽|电|或|及|和|与|至|往|向|对|给|是|为|在|的|了|"
    r"聯繫|聯絡|連絡|連繫|致電|撥打|撥電|查詢|詢問|詳情|報名|預約|電話|號碼|歡迎|任何|請|可|予)"
    r"[：:，,、\s]*$")
NAME_EN_TAIL = re.compile(
    r"([A-Z][A-Za-z\.']{1,15}(?:\s+(?:bin|binti|a/l|a/p)\s+[A-Za-z\.']+|\s+[A-Z][A-Za-z\.']+){0,3})"
    r"\s*[（(]?\s*[：:]?\s*[，,、]?\s*$"
)

STOP_WORD = set("""电话 手机 联络 联系 洽询 询问 报名 详情 查询 致电 传真 地址 日期 时间 地点
活动 主办 联办 承办 协办 主讲 主法 费用 报名费 备注 网址 电邮 邮址 面子书 短讯 报名处 秘书处
负责人 联络人 联系人 询问处 详情请 有意 欢迎 敬请 人数 名额 截止 表格 网站 办公 上午 下午
晚上 星期 农历 每日 每逢 通讯 热线 专线 号码 拨电 来电 咨询 谘询 读者 民众 市民 公众 当局
警方 消拯 医院 政府 部门 单位 公司 商家 居民 业主 家长 学生 老师 校方 董事 家协 校友
任何 欢迎 详情 询问 联络 电话 热线 单位 团队 讯息
""".split())
BAD_SUFFIX = ("会", "寺", "堂", "中心", "协会", "学会", "学院", "团", "组", "处", "部", "社",
              "宫", "庙", "庵", "精舍", "委员", "公司", "基金", "苑", "舍", "院", "校", "局", "馆",
              "居", "轩", "楼", "殿", "坊", "座办", "办事处", "询问处", "报名处", "委员会",
              "公会", "商会", "总会", "分会", "支会", "理事会", "发展华小工委会", "人士", "事件", "警监", "警曹长", "行政",
              "细则", "学生", "通知", "表格", "简章", "详情", "报名", "询问", "联络", "热线", "号码",
              "情报", "行动室", "太平间", "入场", "工作天", "秘書處", "秘书处", "可以", "人士", "者",
              "单位", "团队", "熱線", "热线", "讯息", "第期", "各造", "民众", "公众", "商家", "业者",
              "活动", "活動", "索求", "詳情", "详情", "查询", "查詢", "电话", "電話",
              "监狱", "監獄", "投报", "投報", "分行", "分会", "分局", "疑问", "疑問", "部门", "部門", "母亲", "母親",
              "办公室", "辦公室", "道北", "志愿", "志願",
              "Hotline", "HOTLINE", "hotline")
BAD_HEAD = set("的了和与及或请在於于为对从到向往把被让给这那此其该各个每些有是无不很就都也还又再处办座坊"
               "可情话络系划联请欲想要打拨致询查而且并将已曾正由经据指说称表透他她它我你们本另同以若如因所"
               "地之乎者太最更非没未别勿莫垂谘洽电手号预报名订购买卖供求需舍线进票务会教医总财"
               "提部院人乐工系繫络絡督拿丹准太园关长讯销通员")

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
    if n[-1] in BAD_SUFFIX or n[-2:] in BAD_SUFFIX or n[-3:] in BAD_SUFFIX:
        return False
    if any(w in n for w in ("电话", "联络", "洽询", "报名", "询问", "详情", "查询", "热线", "投诉")):
        return False
    if any(ch.isdigit() for ch in n):
        return False
    return True

def ok_name_en(n):
    n = (n or "").strip(" .'")
    if len(n) < 3:
        return False
    if n.upper() in ("TEL", "CALL", "FAX", "EMAIL", "WHATSAPP", "PBB", "MBB", "RHB", "CIMB",
                     "PUBLIC", "BANK", "HONG", "LEONG", "THE", "AND", "FOR", "YOU", "MAY",
                     "HOTLINE", "OFFICE", "TEAM", "GROUP", "SALES", "INFO", "MALAYSIA", "MELAKA",
                     "SDN", "BHD", "JOHOR", "PENANG", "SINGAPORE"):
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
        win = body[max(0, start - 45):start]
        cut = max(win.rfind("；"), win.rfind(";"), win.rfind("。"), win.rfind("\n"),
                  win.rfind("/"), win.rfind("|"), win.rfind("｜"))
        if cut >= 0:
            win = win[cut + 1:]
        # 反复剥离尾部的动词/连接词，露出真正的姓名
        for _ in range(3):
            new = TAIL_STRIP.sub("", win)
            if new == win:
                break
            win = new
        name, role, src = "", "", ""
        mm = NAME_TAIL.search(win)
        if mm and ok_name(mm.group(1)):
            name = mm.group(1)
            r = re.match(r"\s*(" + ROLE + r")", win[mm.end(1):])
            role = r.group(1) if r else ""
            src = "adjacent"
        else:
            me = NAME_EN_TAIL.search(win)
            if me and ok_name_en(me.group(1)):
                name = me.group(1).strip()
                src = "adjacent"
        if not name:
            mt = re.match(r"\s*[（(]?\s*([\u4e00-\u9fa5]{2,4})(?:" + ROLE + r")?\s*[)）]?(?=[\s，,、；;。]|$)",
                          body[m.end():m.end() + 20])
            if mt and ok_name(mt.group(1)):
                name, src = mt.group(1), "after"
        if not name and same_clause and last_name:
            name, src = last_name, "inherited"
        if name:
            last_name = name
        last_pos = m.end()
        key = (np_, name)
        if key in seen:
            continue
        seen.add(key)
        ctx = body[max(0, start - 70):m.end() + 70].replace("\n", " ").strip()
        res.append((name, role, praw, np_, ctx, src))
    return res

rows, n_art = [], 0
for line in open(IN, encoding="utf-8"):
    try:
        a = json.loads(line)
    except Exception:
        continue
    n_art += 1
    body = a.get("post_content") or ""
    if not body:
        continue
    date = (a.get("post_date") or "")[:10]
    tax = a.get("tax") or []
    if isinstance(tax, str):
        try:
            tax = json.loads(tax)
        except Exception:
            tax = [tax]
    for name, role, praw, pnorm, ctx, src in extract(body):
        rows.append({
            "article_title": a.get("post_title", ""),
            "publish_date": date,
            "category": " / ".join(tax[:3]) if tax else "",
            "contact_name": name,
            "contact_role": role,
            "phone": praw,
            "phone_normalized": pnorm,
            "name_source": src,
            "context": ctx,
            "post_id": a.get("post_id", ""),
            "url": f"https://{SITE}.chinapress.com.my/?p={a.get('post_id','')}",
        })

best = {}
for r in rows:
    k = (r["post_id"], r["phone_normalized"])
    if k not in best or (not best[k]["contact_name"] and r["contact_name"]):
        best[k] = r
rows = list(best.values())
rows.sort(key=lambda r: (r["publish_date"] or "", str(r["post_id"])), reverse=True)

cols = ["article_title", "publish_date", "category", "contact_name", "contact_role",
        "phone", "phone_normalized", "name_source", "context", "post_id", "url"]
with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

named = sum(1 for r in rows if r["contact_name"])
print(f"文章 {n_art} 篇；记录 {len(rows)} 条；有姓名 {named}；无姓名 {len(rows)-named}")
print("CSV:", OUT)
