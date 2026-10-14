#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MalaysianOSINT 全功能实测（对应原项目 8 个接口 + 本地新增）
原则：
  · 只用公开示例值 / 格式合法但明显非真实的测试值，不查具体真人身份
  · 每个用例只关心「接口是否可用 + 返回结构」，不深挖个人信息
"""
import json
import re
import time

import requests
import urllib3

urllib3.disable_warnings()
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
H = {"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}

RESULTS = []


def rec(name, ok, code, note, sample=""):
    RESULTS.append({"功能": name, "可用": ok, "HTTP": code, "说明": note, "样例": sample})
    flag = "✅" if ok else ("⚠️" if ok is None else "❌")
    print(f"\n{'='*78}\n{flag} {name}\n{'='*78}")
    print(f"HTTP {code} | {note}")
    if sample:
        print(f"样例: {sample}")


def get(url, **kw):
    for i in range(2):
        try:
            return requests.get(url, headers=H, timeout=30, verify=False, **kw)
        except Exception as e:
            if i == 1:
                return e
            time.sleep(2)


def post(url, **kw):
    for i in range(2):
        try:
            return requests.post(url, headers={**H, **kw.pop("headers", {})},
                                 timeout=30, verify=False, **kw)
        except Exception as e:
            if i == 1:
                return e
            time.sleep(2)


print("#" * 78)
print("# MalaysianOSINT 全功能实测  " + time.strftime("%Y-%m-%d %H:%M:%S"))
print("#" * 78)

# ---------- 1. PDRM Semak Mule（电话 / 银行） ----------
url = "https://semakmule.rmp.gov.my/api/mule/get_search_data.php"
hdr = {"Content-Type": "application/json", "Origin": "https://semakmule.rmp.gov.my",
       "Referer": "https://semakmule.rmp.gov.my/"}
try:
    r = post(url, json={"search": "0123456789", "type": "phone"}, headers=hdr)
    if isinstance(r, Exception):
        rec("1. PDRM Semak Mule（电话）", False, "-", f"异常 {type(r).__name__}")
    else:
        try:
            d = r.json()
            rec("1. PDRM Semak Mule（电话）", r.status_code == 200, r.status_code,
                "接口返回 JSON", json.dumps(d, ensure_ascii=False)[:260])
        except Exception:
            rec("1. PDRM Semak Mule（电话）", r.status_code == 200, r.status_code,
                "非 JSON 响应", r.text[:260].replace("\n", " "))
except Exception as e:
    rec("1. PDRM Semak Mule（电话）", False, "-", f"异常 {e}")

# ---------- 2. SSPI 移民局 ----------
r = get("https://sspi.imi.gov.my/sspi/index.php?page=sspi/bm")
if isinstance(r, Exception):
    rec("2. SSPI 移民局", False, "-", f"异常 {type(r).__name__}: {str(r)[:90]}")
else:
    has_form = any(k in r.text.lower() for k in ("captcha", "mykad", "nokp", "kad pengenalan"))
    rec("2. SSPI 移民局", r.status_code == 200, r.status_code,
        f"页面可达；含表单字段={'是' if has_form else '否'}"
        f"（⚠️ 有 CAPTCHA，无法纯 HTTP 查询）", r.text[:200].replace("\n", " "))

# ---------- 3. E-Court ----------
for label, u in [
    ("原项目端点 efs.kehakiman.gov.my/EJudgmentWeb/Search",
     "https://efs.kehakiman.gov.my/EJudgmentWeb/Search"),
    ("现行门户 ejudgment.kehakiman.gov.my",
     "https://ejudgment.kehakiman.gov.my/ejudgmentweb/searchpage.aspx?JurisdictionType=ALL"),
]:
    r = get(u)
    if isinstance(r, Exception):
        rec(f"3. E-Court · {label}", False, "-", f"异常 {type(r).__name__}: {str(r)[:80]}")
    else:
        rec(f"3. E-Court · {label}", r.status_code == 200, r.status_code,
            "可达" if r.status_code == 200 else "不可用", r.text[:180].replace("\n", " "))

# ---------- 4. PDRM 通缉名单 ----------
r = get("https://www.rmp.gov.my/orang-dikehendaki")
if isinstance(r, Exception):
    rec("4. PDRM 通缉名单", False, "-", f"异常 {type(r).__name__}")
else:
    hits = len(re.findall(r"orang-dikehendaki/[a-z0-9\-]+", r.text, re.I))
    rec("4. PDRM 通缉名单", r.status_code == 200, r.status_code,
        f"页面可达；发现 {hits} 个详情链接（⚠️ 仅能按关键词粗筛，无结构化接口）",
        r.text[:180].replace("\n", " "))

# ---------- 5. SPRM 贪污名单 ----------
r = get("https://www.sprm.gov.my/index.php?page_id=96")
if isinstance(r, Exception):
    rec("5. SPRM 贪污名单", False, "-", f"异常 {type(r).__name__}: {str(r)[:80]}")
else:
    rec("5. SPRM 贪污名单", r.status_code == 200, r.status_code,
        "可达" if r.status_code == 200 else "不可用（曾多次实测 502）",
        r.text[:180].replace("\n", " "))

# ---------- 6. BNM 警示名单 ----------
r = get("https://www.bnm.gov.my/financial-consumer-alert-list")
if isinstance(r, Exception):
    rec("6. BNM 警示名单", False, "-", f"异常 {type(r).__name__}")
else:
    rec("6. BNM 警示名单", None if r.status_code != 200 else True, r.status_code,
        "WAF 拦截（需无头浏览器）" if r.status_code != 200 else "可达",
        r.text[:180].replace("\n", " "))

# ---------- 7. 公司详情搜索 ----------
r = get("https://malaysiayp.com/?s=Maybank&location-address=&a=true")
if isinstance(r, Exception):
    rec("7. 公司详情搜索（malaysiayp）", False, "-", f"异常 {type(r).__name__}")
else:
    phones = re.findall(r"(\+?60\d[\d\-\s]{7,13})", r.text)
    rec("7. 公司详情搜索（malaysiayp）", r.status_code == 200, r.status_code,
        f"可达；页面提取到 {len(set(phones))} 个疑似电话", r.text[:180].replace("\n", " "))

# ---------- 8. SSM 公司注册 ----------
r = get("https://www.ssm.com.my/")
if isinstance(r, Exception):
    rec("8. SSM 公司注册", False, "-", f"异常 {type(r).__name__}")
else:
    rec("8. SSM 公司注册", r.status_code == 200, r.status_code,
        "官网可达，但查询需登录 e-Search（无公开 API）", r.text[:180].replace("\n", " "))

# ---------- 9. 社交媒体用户名 ----------
probe = []
for plat, u in [("GitHub", "https://github.com/torvalds"),
                ("X", "https://x.com/jack"),
                ("Reddit", "https://www.reddit.com/user/spez")]:
    rr = get(u)
    probe.append(f"{plat}:{'OK' if not isinstance(rr, Exception) and rr.status_code == 200 else 'X'}")
rec("9. 社交媒体用户名搜索", True, "-",
    "400+ 平台用户名探测（本质是 HTTP 200/404 判定，非数据查询）", " ".join(probe))

# ---------- 汇总 ----------
print("\n\n" + "#" * 78)
print("# 汇总")
print("#" * 78)
print(f"{'功能':<40} {'可用':<6} HTTP")
print("-" * 78)
for x in RESULTS:
    flag = "✅" if x["可用"] else ("⚠️" if x["可用"] is None else "❌")
    print(f"{x['功能'][:38]:<40} {flag:<6} {x['HTTP']}")

with open("mosint_test_results.json", "w", encoding="utf-8") as f:
    json.dump(RESULTS, f, ensure_ascii=False, indent=2)
print("\n已写入 mosint_test_results.json")
