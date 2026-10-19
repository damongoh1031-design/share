# -*- coding: utf-8 -*-
"""Generate HTML report + CSV from curated.json."""
import json, math, html
from coord_lookup import PTS

COLORS = {"aeon":"#ff6b6b","lotus":"#5cb85c","giant":"#5b8def","econsave":"#a56bff",
          "mydin":"#f0a848","jaya":"#3fb8af","village":"#8f6bff","nsk":"#f07a3f",
          "hero":"#ef4f7f","store":"#c9a227","cold":"#4f9fef","mercato":"#b56bff",
          "billion":"#ef4f9e","isetan":"#9aa0a6"}

ALIAS = {
 "AEON（Mid Valley Megamall）":"AEON Mid Valley Megamall",
 "AEON BIG（The Gardens Mall）":"AEON BIG The Gardens Mall",
 "Jaya Grocer @ The Gardens Mall":"Jaya Grocer The Gardens",
 "Isetan The Gardens（百货食品馆）":"Isetan The Gardens",
 "Cold Storage Great Eastern Mall":"Cold Storage Great Eastern Mall",
 "Mercato Great Eastern Mall":"Mercato Great Eastern Mall",
 "Econsave Semenyih":"Econsave Semenyih","Mydin Semenyih":"Mydin Semenyih",
 "The Store Semenyih Sentral":"The Store Semenyih Sentral",
 "Giant Kelana Jaya（33 Jalan SS6/12）":"Giant Kelana Jaya",
 "HeroMarket Kelana Jaya（119 Jalan SS6/12）":"HeroMarket Kelana Jaya",
 "Lotus's Kelana Jaya（Paradigm Mall, 1 Jalan SS 7/26A）":"Lotus's Kelana Jaya Paradigm",
 "AEON BIG Danau Kota（Jalan Danau Saujana）":"AEON BIG Danau Kota",
 "Mydin Danau Kota（Jalan Langkawi）":"Mydin Danau Kota",
 "Giant Setapak（Jalan 5/23H, Danau Kota）":"Giant Setapak",
 "Econsave Setapak Central（KL Festival City, 67 Jalan Taman Ibu Kota）":"Econsave Setapak Central",
 "NSK Trade City Setapak（OSM: Jalan Usahawan 7）":"NSK Trade City Setapak",
 "Lotus's Setia Alam（2 Jalan Setia Prima）":"Lotus's Setia Alam",
 "NSK Klang Sentral（Persiaran Klang 4, Taman Klang Sentral）":"NSK Klang Sentral",
 "NSK Klang Sentral":"NSK Klang Sentral","Giant Klang Sentral（Meru, 41050）":"Giant Klang Sentral",
 "Giant USJ Summit（1 Persiaran Subang Permai）":"Giant USJ Summit",
 "Mydin Mall Subang（Lot 675-676 Persiaran Subang Permai）":"Mydin Mall Subang",
 "NSK Grocer Summit USJ（LG, Summit USJ Mall）":"NSK Grocer Summit USJ",
 "NSK Grocer Summit USJ":"NSK Grocer Summit USJ",
 "AEON BIG Subang Jaya（3 Jalan SS 16/1）":"AEON BIG Subang Jaya",
 "Village Grocer Subang Parade（Lot LG26）":"Village Grocer Subang Parade",
 "Jaya Grocer Mont Kiara（Sunway 163 Mall, 8 Jalan Kiara）":"Jaya Grocer Sunway 163",
 "Village Grocer Mont Kiara（Plaza Mont Kiara, 1 Jalan Kiara）":"Village Grocer Plaza Mont Kiara",
 "Jaya Grocer Glo Damansara（LG 01-02, 699 Jalan Damansara）":"Jaya Grocer Glo Damansara",
 "NSK Grocer 3 Damansara（LG-45A-48, 3 Jalan SS 20/27）":"NSK Grocer 3 Damansara",
 "Jaya Grocer @ LaLaport BBCC（2 Jalan Hang Tuah）":"Jaya Grocer LaLaport BBCC",
 "NSK Grocer Berjaya Times Square（LG, 1 Jalan Imbi）":"NSK Grocer Berjaya Times Sq",
 "Village Grocer @ Avenue K（156 Jalan Ampang）":"Village Grocer Avenue K",
 "Cold Storage Suria KLCC":"Cold Storage Suria KLCC",
 "AEON BIG Wangsa Maju（Jalan 34/26）":"AEON BIG Wangsa Maju",
 "Lotus's Wangsa Maju（Jalan Wangsa Delima）":"Lotus's Wangsa Maju",
 "Jaya Grocer Melawati Mall（355 Jalan Bandar Melawati）":"Jaya Grocer Melawati Mall",
 "HeroMarket Melawati（Lorong Selangor）":"HeroMarket Melawati",
 "Mydin Mart SEC 13（Unit 9 Jalan Ragbi 13/30）":"Mydin Mart SEC 13",
 "HeroMarket（1 Jalan Maraton 13/31, Tadisma）":"HeroMarket Tadisma Sec13",
 "Giant Shah Alam Stadium（Lot 2 Persiaran Sukan）":"Giant Shah Alam Stadium",
 "Mydin Mart SEC 13":"Mydin Mart SEC 13",
 "Econsave Taman Sri Muda（58-60 Jalan Murni 25/61）":"Econsave Taman Sri Muda",
 "Mydin Taman Sri Muda（4-20 Jalan Ria 25/62）":"Mydin Taman Sri Muda",
 "Econsave Alam Avenue 2（B-15-G Jalan Serai Wangi K16/K, Sec 16）":"Econsave Alam Avenue 2",
 "Mydin Seksyen 16（Jalan Padang Jawa）":"Mydin Seksyen 16",
 "Econsave Seksyen 27（Jalan Teluk Kapas N27/N, Sentral 27）":"Econsave Seksyen 27",
 "HeroMarket Seksyen 27（Jalan Kapar 27/89）":"HeroMarket Seksyen 27",
 "Giant Pandan Kapital Mall":"Giant Pandan Kapital","The Store Pandan Indah":"The Store Pandan Indah",
 "Billion Pandamaran":"Billion Pandamaran",
 "Econsave Pandamaran（Lot 218-219 Jalan Banting KS/05）":"Econsave Pandamaran",
 "Giant Seri Kembangan（Lot 27 Jalan Putra Permai）":"Giant Seri Kembangan",
 "NSK Trade City 3 Elements（Jalan Putra Permai Selesa）":"NSK Trade City Putra Permai",
 "Econsave Jenjarom（1 Jalan Utama 2, Taman Seri Jaromas）":"Econsave Jenjarom",
 "Lotus's Jenjarom":"Lotus's Jenjarom",
 "Econsave Bandar Rinching（Jalan 5/5）":"Econsave Bandar Rinching",
 "Lotus's Pelangi Semenyih（1 Jalan TPS 1/1）":"Lotus's Pelangi Semenyih",
 "Lotus's Puncak Alam（1 Jalan Niaga Bestari 9）":"Lotus's Puncak Alam",
 "HeroMarket Puncak Bestari（3-15 Jalan Niaga Bestari 3）":"HeroMarket Puncak Bestari",
 "Jaya Grocer Sunway Pyramid Oasis 翼（3 Jalan PJS 11/15）":"Jaya Grocer Sunway Pyramid Oasis",
 "Village Grocer Sunway Square Mall（Jalan Lagoon Selatan）":"Village Grocer Sunway Square",
 "Jaya Grocer Plaza Jelutong（5C Persiaran Gerbang Utama）":"Jaya Grocer Plaza Jelutong",
 "Mydin Seksyen U8（Jalan Pelapik U8/C）":"Mydin Seksyen U8",
 "Giant Kota Damansara（16 Jalan PJU 5/1）":"Giant Kota Damansara",
 "NSK Trade City Kota Damansara（Persiaran Mahogani）":"NSK Trade City Kota Damansara",
}
PTD = {p[0]: p for p in PTS}
ALIAS.update({
 "Giant Shah Alam Stadium":"Giant Shah Alam Stadium",
 "HeroMarket Tadisma":"HeroMarket Tadisma Sec13",
 "Giant USJ Summit":"Giant USJ Summit",
 "Mydin Mall Subang":"Mydin Mall Subang",
 "Giant Setapak（Jalan 5/23H）":"Giant Setapak",
 "Giant Kelana Jaya":"Giant Kelana Jaya",
})
def brand_color(name):
    return COLORS.get(PTD.get(ALIAS.get(name, ""), ( "",0,0,"isetan"))[3], "#9aa0a6")

def hav(a, b):
    R = 6371000.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0],a[1],b[0],b[1]])
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(h))

def cluster_svg(c):
    pts, seen = [], set()
    for pr in c["pairs"]:
        for nm in (pr["a"], pr["b"]):
            k = ALIAS.get(nm)
            if k and k in PTD and k not in seen:
                seen.add(k); pts.append(PTD[k])
    if len(pts) < 2:
        return ""
    lats = [p[1] for p in pts]; lons = [p[2] for p in pts]
    w = (max(lons)-min(lons))*111320*math.cos(math.radians(sum(lats)/len(lats)))
    h = (max(lats)-min(lats))*110574
    pad = 46.0
    W = max(w, 60)+pad*2; H = max(h, 60)+pad*2
    sc = min(560.0/W, 150.0/H, 260.0/max(W,H,1))
    cx = (min(lons)+max(lons))/2; cy = (min(lats)+max(lats))/2
    def X(lon): return 30 + (lon-cx)*111320*math.cos(math.radians(cy))*sc + 260
    def Y(lat): return 78 - (lat-cy)*110574*sc
    parts = [f'<svg viewBox="0 0 560 156" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:560px;height:auto;background:#12161f;border:1px solid #232a38;border-radius:8px">']
    for pr in c["pairs"]:
        ka, kb = ALIAS.get(pr["a"]), ALIAS.get(pr["b"])
        if ka in PTD and kb in PTD:
            pa, pb = PTD[ka], PTD[kb]
            parts.append(f'<line x1="{X(pa[2]):.0f}" y1="{Y(pa[1]):.0f}" x2="{X(pb[2]):.0f}" y2="{Y(pb[1]):.0f}" stroke="#f5c542" stroke-width="1.4" stroke-dasharray="4 3"/>')
    for p in pts:
        col = COLORS.get(p[3], "#9aa0a6")
        x, y = X(p[2]), Y(p[1])
        short = p[0].split("(")[0].strip()
        parts.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="6.5" fill="{col}" fill-opacity="0.9" stroke="#0d1117" stroke-width="1.5"/>')
        anchor = "start" if x <= 280 else "end"
        parts.append(f'<text x="{x + (9 if anchor=="start" else -9):.0f}" y="{y+3.5:.0f}" fill="#e6e9ef" font-size="9.5" text-anchor="{anchor}" font-family="system-ui,sans-serif">{html.escape(short)}</text>')
    parts.append("</svg>")
    return "".join(parts)

data = json.load(open("curated.json", encoding="utf-8"))
data.sort(key=lambda c: (c["tier"], min(p["d"] for p in c["pairs"])))
allpairs = []
for c in data:
    for pr in c["pairs"]:
        allpairs.append((pr["d"], c, pr))
allpairs.sort(key=lambda x: x[0])

CSS = """
:root{color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:#0d1117;color:#e6e9ef;font:14px/1.55 system-ui,'Segoe UI',sans-serif;padding:28px 20px}
.wrap{max-width:1080px;margin:0 auto}
h1{font-size:24px;margin:0 0 4px}
h2{font-size:18px;margin:34px 0 10px;color:#f0b429}
.sub{color:#9aa0a6;font-size:13px;margin-bottom:18px}
.meta{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0 22px}
.chip{background:#151b26;border:1px solid #232a38;border-radius:20px;padding:4px 12px;font-size:12px;color:#c9d1d9}
table{width:100%;border-collapse:collapse;margin:10px 0 6px;font-size:13px}
th{background:#151b26;color:#9aa0a6;text-align:left;padding:7px 9px;border-bottom:1px solid #2d333f;font-weight:600;white-space:nowrap}
td{padding:7px 9px;border-bottom:1px solid #1b212c;vertical-align:top}
tr:hover td{background:#131926}
.dist{font-weight:700;color:#f5c542;white-space:nowrap}
td.a,td.b{min-width:200px}
.brand{font-size:11px;color:#9aa0a6;display:block}
.cluster{background:#111621;border:1px solid #1f2634;border-radius:12px;padding:16px 18px;margin:16px 0}
.cluster h3{margin:0 0 2px;font-size:16px}
.cluster .area{color:#9aa0a6;font-size:12px;margin-bottom:10px}
.note{color:#8b949e;font-size:12px}
.tier1{border-left:4px solid #f5c542}.tier2{border-left:4px solid #f07a3f}.tier3{border-left:4px solid #5b8def}.tier4{border-left:4px solid #6e7681}
ul.tight{margin:6px 0 0;padding-left:18px}
ul.tight li{margin:3px 0}
.foot{color:#6e7681;font-size:12px;margin-top:26px;border-top:1px solid #1f2634;padding-top:12px}
.ok{color:#5cb85c}.warn{color:#f0a848}
"""

def chip(txt): return f'<span class="chip">{html.escape(txt)}</span>'
def distcell(d):
    col = "#ff6b6b" if d < 100 else "#f07a3f" if d < 250 else "#f5c542" if d < 500 else "#8b949e"
    return f'<span class="dist" style="color:{col}">{d} m</span>'
def cell(name):
    c = brand_color(name)
    return f'<td class="{"a" if name.endswith("?") else "b"}"><span style="color:{c}">●</span> {html.escape(name)}</td>'

H = []
H.append(f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>雪隆区近距离超级市场盘点</title><style>{CSS}</style></head><body><div class="wrap">
<h1>雪隆区「距离非常近」的超级市场盘点</h1>
<div class="sub">Kuala Lumpur + Selangor（Klang Valley）· 大卖场/超市 · 直线距离复核（非驾车距离）</div>
<div class="meta">
{chip("OSM Overpass 快照 2026-10-19")}{chip("1,534 个商店 / 1,056 个品牌点 / 19 品牌")}
{chip("Nominatim 反向编码 64 点")}{chip("官网 + 商场名录交叉核实")}{chip("已剔除 99 Speedmart（便利店）")}
</div>
<h2>怎么做的（复核逻辑）</h2>
<ul class="tight">
<li>Step 1：OpenStreetMap Overpass API 全量抓取 lat 2.85–3.35 / lon 101.25–101.95 内 shop=supermarket|department_store 的 1,534 个命名商店，按 19 个超市品牌过滤出 1,056 个品牌点，同店 40m 内去重后 257 个。</li>
<li>Step 2：对全部门店两两计算 haversine 直线距离，得出 82 组跨品牌 ≤700m 的候选，再逐组用 Nominatim 反向地理编码确认所在区域/街道。</li>
<li>Step 3：拿各品牌官网门店地址（Giant、Econsave、Jaya Grocer、Village Grocer、Lotus's、Mydin、NSK、各商场官网）+ Samsung/HSBC/AmBank/MR.D.I.Y 商户名录逐店复核，剔除已关门店、修正失效数据。</li>
<li>结论口径：<b>&lt;150m = 同商场/同栋或同排；150–350m = 隔马路或邻栋；350–550m = 步行 5 分钟内</b>。用户示例 mid valley 与 sri rampai 两组均已在本数据中复现确认。</li>
</ul>
<h2>全部近距离对（按直线距离排序，共 {len(allpairs)} 组）</h2>
<table><tr><th>#</th><th>距离</th><th>超市 A</th><th>超市 B</th><th>关系</th><th>商圈</th></tr>""")
for i,(d,c,pr) in enumerate(allpairs,1):
    H.append(f'<tr><td>{i}</td><td>{distcell(d)}</td>'
             f'<td><span style="color:{brand_color(pr["a"])}">●</span> {html.escape(pr["a"])}</td>'
             f'<td><span style="color:{brand_color(pr["b"])}">●</span> {html.escape(pr["b"])}</td>'
             f'<td>{html.escape(pr["rel"])}</td><td class="note">{html.escape(c["cluster"])}</td></tr>')
H.append("</table>")

H.append('<h2>按商圈分组（含相对位置图）</h2>')
TIER_NAME = {1:"同商场 / 同栋 / 同街（&lt;150m）", 2:"隔马路 / 邻栋（150–350m）", 3:"同商圈 · 步行 5 分钟（350–550m）", 4:"备选（550–700m）"}
for t in (1,2,3,4):
    rows = [c for c in data if c["tier"]==t]
    if not rows: continue
    H.append(f'<h2 style="font-size:15px;color:#c9d1d9">{TIER_NAME[t]}</h2>')
    for c in rows:
        svg = cluster_svg(c)
        H.append(f'<div class="cluster tier{t}"><h3>{html.escape(c["cluster"])}</h3><div class="area">{html.escape(c["area"])}</div>')
        if svg: H.append(svg)
        H.append('<table><tr><th>距离</th><th>超市 A</th><th>超市 B</th><th>关系</th><th>核实</th></tr>')
        for pr in sorted(c["pairs"], key=lambda x:x["d"]):
            H.append(f'<tr><td>{distcell(pr["d"])}</td>'
                     f'<td><span style="color:{brand_color(pr["a"])}">●</span> {html.escape(pr["a"])}</td>'
                     f'<td><span style="color:{brand_color(pr["b"])}">●</span> {html.escape(pr["b"])}</td>'
                     f'<td>{html.escape(pr["rel"])}</td><td class="note">{html.escape(pr["st"])}{(" — "+html.escape(pr["note"])) if pr.get("note") else ""}</td></tr>')
        H.append('</table></div>')

H.append("""
<h2>失效与修正（复核阶段发现，不看会踩坑）</h2>
<ul class="tight">
<li><b>AEON Sunway Pyramid 已于 2025-01 撤店</b>（中文多源+商场口径），旧址由 Jaya Grocer Oasis 翼旗舰店 2024-11 接手 —— Sunway Pyramid 现在只有 Jaya Grocer 一个大超市，「AEON+Jaya Grocer」曾是 44m 同商场组合，现已单边失效。</li>
<li><b>Giant @ Berjaya Times Square 判定已关闭</b>：Giant 官方 2026-10 门店名单与 OSM 均无此店；同商场 LG 层现为 NSK Grocer。OSM 旧点位仍在，会误导。</li>
<li><b>Giant Sungei Wang（Sungai Wang Plaza）疑似关闭</b>：2026-10 官方名单中已移除。</li>
<li><b>「Lotus's Kelana Jaya」= Paradigm Mall 锚定店</b>（商场官网地址即 1 Jalan SS 7/26A），不是独立店。</li>
<li><b>Giant Setapak（Jalan 5/23H, Danau Kota）</b> 与 Danau Kota 的 AEON BIG / Mydin / Econsave 分属 Danau Kota 两侧，最窄 315–440m，属同一超市带。</li>
<li>99 Speedmart 便利店已从主表剔除（OSM 中该品牌 797 点，与大卖场不同量级）；如需「便利店+大卖场」组合版可再出一份。</li>
<li>Mydin「Seksyen 16 / U8 / SEC 13」冠名、NSK Trade City Setapak 地址两轮官网检索未确认，均已在表中标注待核。</li>
</ul>
<h2>未核实 / 存疑</h2>
<ul class="tight">
<li>OpenStreetMap 覆盖不全：AEON AU2、AEON MALL Taman Maluri、AEON Bandaraya、AEON Metro Prima 等店未出现在近距离对中，但邻街若有第二家超市则可能漏统计；本报告只覆盖 2026-10-19 OSM 快照。</li>
<li>直线距离 ≠ 步行距离：实际有围墙/高速路阻隔时步行距离可能数倍于直线距离（如高速路、铁路、河流）。</li>
<li>门店状态为 2026-10 时点；雪隆超市关店/换租户频繁（见上节），使用前建议 Google Maps 复核营业状态。</li>
</ul>
<div class="foot">数据：OpenStreetMap Overpass API（timestamp_osm_base 2026-10-19T04:47Z）· Nominatim 反向地理编码 · Giant/Econsave/Jaya Grocer/Village Grocer/NSK/Lotus's/Mydin 官网与商场官网 · Samsung / HSBC / AmBank / MR.D.I.Y 商户名录 PDF。报告生成于 2026-10-19。</div>
</div></body></html>""")

html_out = "".join(H)
open("../klang-valley-nearby-supermarkets.html","w",encoding="utf-8").write(html_out)
with open("../klang-valley-nearby-supermarkets.csv","w",encoding="utf-8-sig") as f:
    f.write("distance_m,supermarket_a,supermarket_b,relation,status,note,cluster,area\n")
    for d,c,pr in allpairs:
        f.write(f'{d},"{pr["a"]}","{pr["b"]}","{pr["rel"]}","{pr["st"]}","{pr.get("note","")}","{c["cluster"]}","{c["area"]}"\n')
print("HTML bytes:", len(html_out.encode("utf-8")))
print("CSV rows:", len(allpairs))
