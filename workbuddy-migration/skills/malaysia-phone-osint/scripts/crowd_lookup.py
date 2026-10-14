#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 层：众包来电识别查询（无需安装 App、无需 API Key、纯 HTTP）

实测结论（2026-10-02）：
  ✅ busuk.my      —— 静态 HTML，可直接 GET 解析
  ✅ junk-call.com —— 静态 HTML，可直接 GET 解析（数据薄）
  ❌ Truecaller    —— 网页版无头浏览器真渲染后 DOM 里没有任何号码数据，强制登录
  ❌ Whoscall      —— /en/number/<号码> 渲染后为空，netlog 里无任何 API XHR，数据只在 App 内
  ❌ tellows.my / shouldianswer —— 无马来西亚覆盖

用法:
    python crowd_lookup.py 0102261791
    python crowd_lookup.py 010-2261791 0123456789
"""
import re
import sys

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"
    )
}
TIMEOUT = 25


def digits_only(raw: str) -> str:
    return re.sub(r"\D", "", raw)


def strip_tags(html: str) -> str:
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    html = html.replace("&amp;", "&").replace("&nbsp;", " ").replace("&#39;", "'")
    return re.sub(r"[ \t\r\f\v]+", " ", html)


def busuk_my(number: str) -> dict:
    """busuk.my：马来西亚本地公共参考站，页面为静态 HTML。"""
    url = f"https://busuk.my/semak/nombor-telefon/{number}/"
    try:
        r = requests.get(url, headers=UA, timeout=TIMEOUT)
    except Exception as e:
        return {"source": "busuk.my", "ok": False, "error": str(e)}
    if r.status_code != 200:
        return {"source": "busuk.my", "ok": False, "error": f"HTTP {r.status_code}"}

    text = strip_tags(r.text)
    out = {"source": "busuk.my", "ok": True, "url": url}

    def grab(label: str) -> str:
        m = re.search(re.escape(label) + r"\s+(.{1,60}?)\s+(?:Nombor Telefon|Jenis|Carrier|Tahap Risiko|Laporan Komuniti|Semak Nombor Lain|$)", text)
        return m.group(1).strip() if m else ""

    out["line_type"] = grab("Jenis")
    out["carrier"] = grab("Carrier")
    out["risk"] = grab("Tahap Risiko")

    m = re.search(r"Laporan Komuniti\s+(.{0,200}?)(?:Semak Nombor Lain|$)", text, re.S)
    out["community"] = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
    return out


def junkcall(number: str) -> dict:
    """junk-call.com：可抓，但马来西亚数据很薄。"""
    url = f"https://www.junk-call.com/my/{number}"
    try:
        r = requests.get(url, headers=UA, timeout=TIMEOUT)
    except Exception as e:
        return {"source": "junk-call.com", "ok": False, "error": str(e)}
    if r.status_code != 200:
        return {"source": "junk-call.com", "ok": False, "error": f"HTTP {r.status_code}"}

    text = strip_tags(r.text)
    # 页面固定文案: "Comment on「 <number> 」 remind more people? Add Comment"
    m = re.search(r"Comment on[^\u300c]*\u300c(.{1,30}?)\u300d\s*(.{0,120}?)Add Comment", text, re.S)
    has_comment = bool(m and m.group(2).strip() and "remind more people" not in m.group(2))
    return {
        "source": "junk-call.com",
        "ok": True,
        "url": url,
        "has_comments": has_comment,
        "snippet": re.sub(r"\s+", " ", m.group(2)).strip()[:120] if m else "",
    }


def truecaller_whoscall_note() -> str:
    return (
        "Truecaller / Whoscall：网页版经无头浏览器实测不返回任何号码数据"
        "（Truecaller 强制登录；Whoscall 页面渲染后为空且无 API 请求），只能装 App 查。"
    )


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    for raw in sys.argv[1:]:
        num = digits_only(raw)
        # busuk.my 用无前导 0 的本地格式（0123456789 → 123456789 也可，先用原样）
        print("=" * 66)
        print(f"号码: {raw}  (规范化: {num})")
        print("=" * 66)

        b = busuk_my(num)
        print("\n[busuk.my]")
        if not b["ok"]:
            print("  ✗", b["error"])
        else:
            print(f"  线路类型   : {b['line_type'] or '(未解析)'}")
            print(f"  运营商     : {b['carrier'] or '(未解析)'}")
            print(f"  风险等级   : {b['risk'] or '(未解析)'}")
            print(f"  社区报告   : {b['community'] or '(无)'}")
            print(f"  来源       : {b['url']}")

        j = junkcall(num)
        print("\n[junk-call.com]")
        if not j["ok"]:
            print("  ✗", j["error"])
        else:
            print(f"  有评论     : {'是' if j['has_comments'] else '否'}")
            if j["snippet"]:
                print(f"  摘要       : {j['snippet']}")
            print(f"  来源       : {j['url']}")

    print("\n" + "-" * 66)
    print(truecaller_whoscall_note())
    print("-" * 66)
    return 0


if __name__ == "__main__":
    sys.exit(main())
