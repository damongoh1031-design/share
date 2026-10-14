#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MalaysianOSINT 的 Python 移植版（Windows 可用）

原项目 ctkqiang/MalaysianOSINT 是 C + libmicrohttpd + cJSON 的常驻 HTTP 服务，
需要 gcc/cmake/libmicrohttpd，Windows 上编译成本高。本脚本把它的全部上游接口
原样搬到 Python，变成一次性 CLI，无需编译、无需起服务。

原项目的上游接口（已从源码逐一提取）+ 本机实测状态：
  PDRM Semak Mule  POST https://semakmule.rmp.gov.my/api/mule/get_search_data.php   ✅ 可用
                   headers: apikey: j3j389#nklala2（源码 pdrm.c 里写死的）
                   body:    {"data":{"category":..,"bankAccount":..,"telNo":..,"companyName":..,"captcha":""}}
  SSPI 移民局       POST https://sspi.imi.gov.my/sspi/index.php?page=sspi/bm           ✅ 可用
                   body: txtIcNo=<IC>&btnSemak=Semak
  PDRM 通缉名单     GET  https://www.rmp.gov.my/orang-dikehendaki                    ⚠️ 可抓但关键词匹配命中大量导航文字
  BNM 警示名单      GET  https://www.bnm.gov.my/financial-consumer-alert-list         ❌ WAF 403（Chrome 可开，需浏览器）
  SPRM 贪污名单     GET  https://www.sprm.gov.my/index.php?page_id=96                 ⚠️ 偶发代理 502
  公司搜索          GET  https://malaysiayp.com/?s=<kw>&location-address=&a=true      ✅ 可用（返回真实商家+电话）
  e-Court 判决      POST https://efs.kehakiman.gov.my/EJudgmentWeb/Search             ❌ 域名+路径均 404，
                   实际域名已迁到 ejudgment.kehakiman.gov.my，且旧 JSON 端点已不存在（改成 ASP.NET WebForms，需浏览器）
  MyKad / SSM 解码  本地计算，无网络请求                                              ✅ 可用

用法:
    python malaysian_osint.py phone 0102261791
    python malaysian_osint.py bank 1234567890123
    python malaysian_osint.py company "ABC SDN BHD"      # Semak Mule 公司名
    python malaysian_osint.py biz "ABC SDN BHD"          # malaysiayp 商家搜索
    python malaysian_osint.py bnm "ABC"
    python malaysian_osint.py mykad 900101011234
    python malaysian_osint.py ssm 202001012345
    python malaysian_osint.py ecourt "TAN AH KOW"
    python malaysian_osint.py sspi 900101011234
    python malaysian_osint.py wanted
    python malaysian_osint.py sprm 900101011234
    python malaysian_osint.py all 0102261791      # 电话全量（Semak Mule + BNM 无关，仅做示例）

注意: 全部为公开数据源，返回的是「是否被举报/是否在名单中」，不包含机主实名信息。
"""
import argparse
import json
import re
import sys

import time

import requests

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"
)
HEADERS = {"User-Agent": UA, "Accept": "*/*"}
TIMEOUT = 30

# 本机沙箱走 TLS 中间人代理，Python 的 certifi 根证书链校验会失败
# （curl 走 Windows 证书存储所以正常）。这些目标都是公开数据源，默认关闭校验；
# 需要严格校验时加 --verify。
VERIFY = False

MULE_URL = "https://semakmule.rmp.gov.my/api/mule/get_search_data.php"
MULE_KEY = "j3j389#nklala2"  # 原项目 src/pdrm.c 中硬编码

MYKAD_STATES = {
    "01": "Johor", "02": "Kedah", "03": "Kelantan", "04": "Malacca",
    "05": "Negeri Sembilan", "06": "Pahang", "07": "Penang", "08": "Perak",
    "09": "Perlis", "10": "Selangor", "11": "Terengganu", "12": "Sabah",
    "13": "Sarawak", "14": "Kuala Lumpur FT", "15": "Labuan FT", "16": "Putrajaya FT",
}

SSM_ENTITY = {
    "01": "Local Company",
    "02": "Foreign Company",
    "03": "Business Entity",
    "04": "Local LLP",
    "05": "Foreign LLP",
    "06": "Local LLP for Professional Practice",
}


def _text(html: str) -> str:
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    html = html.replace("&amp;", "&").replace("&nbsp;", " ").replace("&#39;", "'")
    return re.sub(r"[ \t\r\f\v]+", " ", html)


def _request(method: str, url: str, tries: int = 3, **kw):
    """带指数退避的请求。本机沙箱代理偶发 502，必须重试。"""
    kw.setdefault("timeout", TIMEOUT)
    kw.setdefault("verify", VERIFY)
    last = None
    for i in range(tries):
        try:
            return requests.request(method, url, **kw)
        except Exception as e:  # ProxyError / SSLError / Timeout ...
            last = e
            if i < tries - 1:
                time.sleep(1.5 * (i + 1))
    raise last


# ---------------------------------------------------------------- Semak Mule
def semak_mule(category: str, value: str) -> dict:
    """category: telefon | bank | namasyarikat"""
    field = {"telefon": "telNo", "bank": "bankAccount", "namasyarikat": "companyName"}[category]
    payload = {"data": {"category": category, field: value,
                        "bankAccount": "", "telNo": "", "companyName": "", "captcha": ""}}
    payload["data"][field] = value
    try:
        r = _request("POST",
            MULE_URL,
            json=payload,
            headers={**HEADERS, "Content-Type": "application/json",
                     "Origin": "https://semakmule.rmp.gov.my",
                     "Referer": "https://semakmule.rmp.gov.my/",
                     "apikey": MULE_KEY},
            timeout=TIMEOUT, verify=VERIFY,
        )
        body = r.json()
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    rows = body.get("table_data") or []
    return {
        "ok": True,
        "headers": body.get("table_header") or [],
        "rows": rows,
        "reported": bool(rows),
        # 注意: count 是该关键词被查询的次数计数器, 不是命中数（原项目把它读成"被查了几次"，是对的）
        "search_counter": body.get("count"),
    }


# ---------------------------------------------------------------- MyKad / SSM
def mykad_decode(ic: str) -> dict:
    ic = re.sub(r"\D", "", ic)
    if len(ic) < 12:
        return {"ok": False, "error": "IC 不足 12 位"}
    return {
        "ok": True,
        "birthday": f"19{ic[0:2]}-{ic[2:4]}-{ic[4:6]}",
        "birth_state": MYKAD_STATES.get(ic[6:8], "Unknown"),
        "gender": "Male" if int(ic[-1]) % 2 == 1 else "Female",
        "identifier": ic[8:12],
    }


def ssm_decode(num: str) -> dict:
    num = re.sub(r"\D", "", num)
    if len(num) != 12:
        return {"ok": False, "error": "SSM 编号应为 12 位"}
    return {"ok": True, "entity_code": num[4:6],
            "entity_type": SSM_ENTITY.get(num[4:6], "Unknown Entity")}


# ---------------------------------------------------------------- 官方名单
def bnm_alert_list(keyword: str | None = None) -> dict:
    """BNM 金融消费者警示名单

    ⚠️ 2026-10-02 实测：BNM 走 Cloudflare WAF，**随机拦截**（3 次中 1 次 403
       「Just a moment...」、2 次 200 正常返回 ~352KB）→ 必须重试。
    """
    url = "https://www.bnm.gov.my/financial-consumer-alert-list"
    r = None
    last_code = None
    for i in range(4):                      # Cloudflare 随机放行，多试几次
        try:
            r = _request("GET", url, headers=HEADERS, tries=1)
            last_code = r.status_code
            body = r.text
            blocked = (r.status_code != 200
                       or "Just a moment" in body
                       or "cf-chl" in body.lower()
                       or "Enable JavaScript and cookies" in body)
            if not blocked:
                break
        except Exception as e:
            last_code = f"{type(e).__name__}"
        r = None
        time.sleep(2.5 * (i + 1))

    if r is None:
        return {
            "ok": False,
            "error": f"HTTP {last_code}（BNM 的 Cloudflare WAF 拦截，重试 4 次仍失败）",
            "url": url,
            "hint": "改用无头浏览器（实测 352KB 正常渲染）: "
                    f'chrome --headless=new --dump-dom "{url}"',
        }
    text = _text(r.text)
    if not keyword:
        return {"ok": True, "url": url, "text_length": len(text),
                "hint": "加关键词参数可搜索，如: bnm \"ABC\""}
    hits = [m.start() for m in re.finditer(re.escape(keyword), text, re.I)]
    snippets = [re.sub(r"\s+", " ", text[max(0, i - 90):i + 120]) for i in hits[:10]]
    return {"ok": True, "url": url, "keyword": keyword, "hits": len(hits), "snippets": snippets}


def pdrm_wanted_list(keyword: str | None = None) -> dict:
    """PDRM 通缉名单（原项目 src/rmp_wanted.c）

    ⚠️ 2026-10-02 实测修正：
      1. **必须用词边界 `\\b` 匹配** —— 否则 "TAN" 会命中 CSS 的 `!important`
         和马来语导航词 `Keselamatan`（两者都含 "tan"），实测噪声率 41/41 = 100%
      2. 该页面为 Sitefinity 门户，通缉条目**没有独立详情页链接**（实测仅 1 个
         链接指向自身）→ 当页面无条目时，任何关键词都会返回 0 个有效命中
      3. 页面含大量站点导航（Jabatan / Keselamatan 等），无法纯 HTML 区分
         「人名」与「导航词」→ **结果只应作为线索，不能作为结论**
    """
    url = "https://www.rmp.gov.my/orang-dikehendaki"
    try:
        r = _request("GET", url, headers=HEADERS)
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
    if r.status_code != 200:
        return {"ok": False, "error": f"HTTP {r.status_code}"}

    # 先剥 script/style/标签，再去掉站点导航区，最后用词边界匹配
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", r.text, flags=re.S | re.I)
    # 去掉 <nav>/<ul class=*nav*>/面包屑等导航容器
    html = re.sub(r"<nav[^>]*>.*?</nav>", " ", html, flags=re.S | re.I)
    html = re.sub(r'<(ul|div)[^>]*class="[^"]*(?:nav|menu|breadcrumb|sitemap)[^"]*"[^>]*>.*?</\1>',
                  " ", html, flags=re.S | re.I)
    text = _text(html)

    if not keyword:
        return {"ok": True, "url": url, "text_length": len(text),
                "hint": '加关键词可搜索，如: wanted "TAN"（用词边界匹配，已过滤导航噪声）'}

    pat = re.compile(r"\b" + re.escape(keyword) + r"\b", re.I)
    hits = [m.start() for m in pat.finditer(text)]
    snippets = [re.sub(r"\s+", " ", text[max(0, i - 90):i + 160]) for i in hits[:10]]
    return {"ok": True, "url": url, "keyword": keyword, "hits": len(hits),
            "snippets": snippets,
            "caveat": "该页无结构化接口，命中可能仍含导航词；仅作线索"}


def sprm_list(keyword: str) -> dict:
    url = "https://www.sprm.gov.my/index.php?page_id=96"
    try:
        r = _request("GET", url, headers=HEADERS)
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
    if r.status_code != 200:
        return {"ok": False, "error": f"HTTP {r.status_code}"}
    text = _text(r.text)
    hits = [m.start() for m in re.finditer(re.escape(keyword), text, re.I)]
    return {"ok": True, "url": url, "keyword": keyword, "hits": len(hits),
            "snippets": [re.sub(r"\s+", " ", text[max(0, i - 90):i + 160]) for i in hits[:10]]}


# ---------------------------------------------------------------- 其他
def company_search(keyword: str) -> dict:
    """malaysiayp.com 商家搜索（原项目 src/company.c）"""
    url = f"https://malaysiayp.com/?s={requests.utils.quote(keyword)}&location-address=&a=true"
    try:
        r = _request("GET", url, headers=HEADERS)
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
    if r.status_code != 200:
        return {"ok": False, "error": f"HTTP {r.status_code}"}
    text = _text(r.text)
    hits = [m.start() for m in re.finditer(re.escape(keyword), text, re.I)]
    return {"ok": True, "url": url, "hits": len(hits),
            "snippets": [re.sub(r"\s+", " ", text[max(0, i - 120):i + 200]) for i in hits[:8]]}


def ecourt_search(name: str) -> dict:
    """e-Court 判决检索。

    ⚠️ 原项目 (ctkqiang/MalaysianOSINT) 用的是 https://efs.kehakiman.gov.my/EJudgmentWeb/Search，
    本机实测该主机+路径均为 404 —— 门户已迁到 ejudgment.kehakiman.gov.my，
    且旧 JSON 端点不复存在（现在是 ASP.NET WebForms，需 ViewState/Session）。
    因此本函数改为探测现状并给出可用的替代入口。
    """
    portal = "https://ejudgment.kehakiman.gov.my/ejudgmentweb/searchpage.aspx?JurisdictionType=ALL"
    try:
        r = _request("GET", portal, headers=HEADERS)
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
    return {
        "ok": True,
        "status": "旧 JSON 端点已失效，改用手动门户",
        "old_endpoint": "https://efs.kehakiman.gov.my/EJudgmentWeb/Search",
        "old_endpoint_result": "404",
        "portal": portal,
        "portal_http": r.status_code,
        "hint": f"用浏览器打开门户，在 Search 框输入 “{name}”，"
                "或对该页做浏览器自动化抓渲染结果。",
    }


def sspi_check(ic: str) -> dict:
    """移民局 SSPI 出入境限制查询（原项目 src/sspi.c）

    ⚠️ 2026-10-02 实测修正两处：
      1. **必须先 GET 拿 PHPSESSID**，无 cookie 直接 POST 会返回
         "Sila masukkan nombor kad pengenalan"（服务端不处理）
      2. 结果在 `<span id="lblStatuscode">` 里，格式为
         `Keputusan semakan: Tiada halangan` / `Masukan No. Kad Pengenalan 12 Digit`
         —— 用宽泛正则会在「提示区」误匹配，造成假阳性
    局限：服务端只校验 12 位数字格式，`000000000000` 也返回「Tiada halangan」，
         因此结果只能作**线索**，不能证明「此人可自由出境」。
    """
    url = "https://sspi.imi.gov.my/sspi/index.php?page=sspi/bm"
    try:
        with requests.Session() as s:
            s.headers.update(HEADERS)
            s.get(url, timeout=TIMEOUT, verify=VERIFY)          # ← 拿 PHPSESSID
            r = s.post(url, data={"txtIcNo": ic, "btnSemak": "Semak"},
                       headers={**HEADERS,
                                "Content-Type": "application/x-www-form-urlencoded"},
                       timeout=TIMEOUT, verify=VERIFY)
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    # 精确取结果区（避免匹配到提示区）
    m = re.search(r'id="lblStatuscode"[^>]*>(.*?)</span>', r.text, re.S | re.I)
    raw = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).strip() if m else ""

    if "Tiada halangan" in raw:
        verdict, note = "Tiada halangan", "无出入境禁止记录"
    elif "Ada halangan" in raw:
        verdict, note = "Ada halangan", "有出入境禁止记录"
    elif "12 Digit" in raw or "Masukan" in raw:
        verdict, note = "(格式不符)", "需 12 位纯数字身份证号"
    else:
        verdict, note = (raw or "(未解析到)"), "响应结构与预期不符，可能已改版"

    return {"ok": True, "url": url, "http": r.status_code, "ic": ic,
            "verdict": verdict, "note": note,
            "raw_result": raw[:120],
            "caveat": "服务端仅校验格式；结果为线索，非身份或权利证明"}


# ---------------------------------------------------------------- CLI
def show(title: str, obj: dict) -> None:
    print("\n" + "=" * 68)
    print(f"### {title}")
    print("=" * 68)
    if not obj.get("ok", True):
        print("  ✗", obj.get("error"))
        return
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def main() -> int:
    ap = argparse.ArgumentParser(description="MalaysianOSINT Python 移植版")
    ap.add_argument("action", choices=["phone", "bank", "company", "biz", "bnm", "mykad",
                                       "ssm", "ecourt", "sspi", "wanted", "sprm"])
    ap.add_argument("value", nargs="?", default=None)
    ap.add_argument("--json", action="store_true", help="只输出 JSON")
    ap.add_argument("--verify", action="store_true", help="启用严格 TLS 证书校验（默认关闭，见文件头注释）")
    args = ap.parse_args()

    global VERIFY
    if args.verify:
        VERIFY = True

    v = args.value
    out = {}

    if args.action == "phone":
        out["semak_mule"] = semak_mule("telefon", v)
        out["mykad_if_ic"] = mykad_decode(v) if re.fullmatch(r"\d{12}", v or "") else {"skipped": True}
    elif args.action == "bank":
        out["semak_mule"] = semak_mule("bank", v)
    elif args.action == "company":
        out["semak_mule"] = semak_mule("namasyarikat", v)
    elif args.action == "biz":
        out["malaysiayp"] = company_search(v)
    elif args.action == "bnm":
        out["bnm_alert_list"] = bnm_alert_list(v)
    elif args.action == "mykad":
        out["mykad"] = mykad_decode(v)
    elif args.action == "ssm":
        out["ssm"] = ssm_decode(v)
    elif args.action == "ecourt":
        out["ecourt"] = ecourt_search(v)
    elif args.action == "sspi":
        out["sspi"] = sspi_check(v)
    elif args.action == "wanted":
        out["pdrm_wanted"] = pdrm_wanted_list(v)
    elif args.action == "sprm":
        out["sprm"] = sprm_list(v)

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for k, o in out.items():
            show(k, o)
        print("\n" + "-" * 68)
        print("数据来源均为公开渠道，返回「是否被举报 / 是否在名单中」，不含机主实名信息。")
        print("-" * 68)
    return 0


if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    sys.exit(main())
