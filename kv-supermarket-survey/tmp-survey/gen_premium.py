# -*- coding: utf-8 -*-
import json, math, html
data = json.load(open("premium_curated.json", encoding="utf-8"))
C = {"Jaya Grocer":"#3fb8af","Village Grocer":"#8f6bff","Mercato":"#b56bff","Cold Storage":"#4f9fef",
     "Isetan":"#9aa0a6","Don Don Donki":"#ff9f43","AEON MaxValu":"#ff6b6b"}
def col(n):
    for k,v in C.items():
        if n.startswith(k): return v
    return "#9aa0a6"
def dc(d):
    c = "#ff6b6b" if d<100 else "#f07a3f" if d<250 else "#f5c542" if d<500 else "#8b949e"
    return f'<span style="color:{c};font-weight:700">{d} m</span>'
CSS = open("css.txt", encoding="utf-8").read() if False else """
:root{color-scheme:dark}*{box-sizing:border-box}
body{margin:0;background:#0d1117;color:#e6e9ef;font:14px/1.55 system-ui,'Segoe UI',sans-serif;padding:28px 20px}
.wrap{max-width:1080px;margin:0 auto}
h1{font-size:23px;margin:0 0 4px}h2{font-size:17px;margin:32px 0 10px;color:#f0b429}
h2s{font-size:15px;color:#c9d1d9}
.sub{color:#9aa0a6;font-size:13px;margin-bottom:16px}
.chip{background:#151b26;border:1px solid #232a38;border-radius:20px;padding:4px 12px;font-size:12px;color:#c9d1d9;display:inline-block;margin:3px 4px 3px 0}
table{width:100%;border-collapse:collapse;margin:10px 0 4px;font-size:13px}
th{background:#151b26;color:#9aa0a6;text-align:left;padding:7px 9px;border-bottom:1px solid #2d333f;font-weight:600}
td{padding:7px 9px;border-bottom:1px solid #1b212c;vertical-align:top}
tr:hover td{background:#131926}
.note{color:#8b949e;font-size:12px}
.cluster{background:#111621;border:1px solid #1f2634;border-left:4px solid #3fb8af;border-radius:12px;padding:14px 16px;margin:14px 0}
.cluster h3{margin:0 0 2px;font-size:15px}
.cluster .area{color:#9aa0a6;font-size:12px;margin-bottom:8px}
ul.tight{margin:6px 0 0;padding-left:18px}ul.tight li{margin:3px 0}
.foot{color:#6e7681;font-size:12px;margin-top:24px;border-top:1px solid #1f2634;padding-top:12px}
"""
allp=[]
for c in data:
    for pr in c["pairs"]: allp.append((pr["d"],c,pr))
allp.sort(key=lambda x:x[0])
H=[f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>雪隆区近距离高级超市盘点</title><style>{CSS}</style></head><body><div class="wrap">
<h1>雪隆区「距离非常近」的<b>中高端超市</b>盘点</h1>
<div class="sub">已剔除 Mydin / NSK / Giant / Econsave / AEON BIG / HeroMarket / The Store / Billion 等平价大卖场，只保留高端与精品线 · 直线距离</div>
<div>
<span class="chip">纳入：Jaya Grocer / Village Grocer / Mercato / Cold Storage / Isetan 食品馆 / Don Don Donki / AEON MaxValu Prime</span>
<span class="chip">67 个高端门店点（OSM 2026-10-19）+ Don Don Donki 手工补点</span>
<span class="chip">对照版（全品牌 39 对）：klang-valley-nearby-supermarkets.html</span>
</div>
<h2>高端品牌全名单（雪隆，2026-10）</h2>
<table><tr><th>品牌</th><th>定位</th><th>雪隆门店（OSM 点）</th><th>备注</th></tr>
<tr><td><b>Jaya Grocer</b></td><td>本地高端连锁</td><td>36 点 / 已识别 18+ 家</td><td class="note">母公司 Aventure? 不——Avenue 集团；旗舰：The Gardens LG-229、Sunway Pyramid Oasis 翼（2024-11 重开）</td></tr>
<tr><td><b>Village Grocer</b></td><td>高端</td><td>20 点 / 已识别 11 家</td><td class="note">Subang Parade、Plaza Mont Kiara、Avenue K、Sunway Square、Bangsar Village、Sri Hartamas、Kota Damansara、Desa ParkCity</td></tr>
<tr><td><b>Mercato</b></td><td>Gourmet 精品</td><td>5 点</td><td class="note">Great Eastern Mall、Raintree Plaza TRX、Solaris Mont Kiara、Jalan Raja Chulan（待核）</td></tr>
<tr><td><b>Cold Storage</b></td><td>DFI 高端</td><td>OSM 仅 2 点（覆盖不全）</td><td class="note">Suria KLCC、Great Eastern Mall；实际雪隆门店更多，OSM 漏标</td></tr>
<tr><td><b>Isetan（食品馆）</b></td><td>日系百货食品</td><td>3 点</td><td class="note">The Gardens、Suria KLCC、The Japan Store（址待核）</td></tr>
<tr><td><b>Don Don Donki</b></td><td>日系折扣网红</td><td>OSM 无点（手工补 4 点）</td><td class="note">在营：Fahrenheit 88、Sunway Pyramid（2024-12）；Nu Sentral 2025-05 已关；Tropicana Gardens / MyTown 待核</td></tr>
<tr><td><b>AEON MaxValu Prime</b></td><td>AEON 精品线</td><td>1 点（Kerinchi）</td><td class="note">普通 AEON 属中端，不计入本名单</td></tr>
</table>
<h2>高端近距离对（{len(allp)} 组，按距离排序）</h2>
<table><tr><th>#</th><th>距离</th><th>超市 A</th><th>超市 B</th><th>关系</th><th>核实</th></tr>"""]
for i,(d,c,pr) in enumerate(allp,1):
    H.append(f'<tr><td>{i}</td><td>{dc(d)}</td><td><span style="color:{col(pr["a"])}">●</span> {html.escape(pr["a"])}</td>'
             f'<td><span style="color:{col(pr["b"])}">●</span> {html.escape(pr["b"])}</td>'
             f'<td>{html.escape(pr["rel"])}</td><td class="note">{html.escape(pr["st"])}</td></tr>')
H.append('</table><h2>按商圈分组</h2>')
for c in data:
    H.append(f'<div class="cluster"><h3>{html.escape(c["cluster"])}</h3><div class="area">{html.escape(c["area"])}</div><table><tr><th>距离</th><th>超市 A</th><th>超市 B</th><th>关系</th><th>备注</th></tr>')
    for pr in sorted(c["pairs"], key=lambda x:x["d"]):
        H.append(f'<tr><td>{dc(pr["d"])}</td><td><span style="color:{col(pr["a"])}">●</span> {html.escape(pr["a"])}</td>'
                 f'<td><span style="color:{col(pr["b"])}">●</span> {html.escape(pr["b"])}</td><td>{html.escape(pr["rel"])}</td>'
                 f'<td class="note">{html.escape(pr.get("note",""))}</td></tr>')
    H.append('</table></div>')
H.append("""
<h2>平价 vs 高端：密度对比</h2>
<table><tr><th>片区</th><th>平价带（剔除前）</th><th>高端带（本报告）</th></tr>
<tr><td>Mont Kiara</td><td class="note">—</td><td><b>3 家高端挤 400m</b>：Jaya Grocer Sunway 163 + Village Grocer Plaza Mont Kiara（176m）+ Village Grocer Sri Hartamas</td></tr>
<tr><td>Danau Kota 翠湖园</td><td>5 家大卖场 1km 圈（AEON BIG+Mydin+Econsave+Giant+NSK）</td><td class="note">无高端店</td></tr>
<tr><td>KLCC 段</td><td>—</td><td>Cold Storage KLCC + Isetan KLCC + Village Grocer Avenue K，370m 三角</td></tr>
<tr><td>USJ 1 Summit</td><td>Giant + Mydin Mall + NSK，182–358m</td><td class="note">无高端店</td></tr>
<tr><td>Sunway City</td><td>—</td><td>Jaya Grocer Oasis 翼 + Don Don Donki Sunway Pyramid（2024-12）+ Village Grocer Sunway Square</td></tr>
<tr><td>Bukit Bintang</td><td>NSK（BTS，平价）</td><td>Don Don Donki Fahrenheit88 + Mercato Jalan Raja Chulan + Isetan The Japan Store</td></tr>
</table>
<h2>结论</h2>
<ul class="tight">
<li><b>雪隆高端超市的「近距离对」明显少于平价带</b>：平价带 39 对 vs 高端带 12 对（≤550m）。高端超市讲分区覆盖，刻意错开；平价带讲扎堆抢客。</li>
<li>最强高端组合：<b>Great Eastern Mall 内 Cold Storage+Mercato（34m 同商场）</b>；<b>The Gardens 内 Jaya Grocer+Isetan 食品馆（55m）</b>；<b>Mont Kiara 双高端 176m</b>；<b>Avenue K ↔ KLCC 隔马路 247–370m</b>。</li>
<li>新趋势：Jaya Grocer（2024-11 Sunway Pyramid Oasis）与 Don Don Donki（2024-12 Sunway Pyramid）把 Sunway City 变成新高端点，替代已撤的 AEON。</li>
<li>Mydin/NSK/Giant/Econsave 扎堆区（Danau Kota、USJ Summit、Setia Alam）都没有高端店——「平价双超市」和「高端双超市」在雪隆基本是两张不重叠的地图。</li>
</ul>
<div class="foot">数据：OSM Overpass 2026-10-19 + Nominatim 反向编码 + Jaya Grocer/Village Grocer 官网/商场官网 + 中文新店报道（Don Don Donki Sunway Pyramid 2024-12、Nu Sentral 2025-05 结业）。Don Don Donki 坐标为商场估算，铺位精度待核。生成于 2026-10-19。</div>
</div></body></html>""")
out="".join(H)
open("../klang-valley-nearby-premium-supermarkets.html","w",encoding="utf-8").write(out)
with open("../klang-valley-nearby-premium-supermarkets.csv","w",encoding="utf-8-sig") as f:
    f.write("distance_m,supermarket_a,supermarket_b,relation,status,note,cluster,area\n")
    for d,c,pr in allp:
        f.write(f'{d},"{pr["a"]}","{pr["b"]}","{pr["rel"]}","{pr["st"]}","{pr.get("note","")}","{c["cluster"]}","{c["area"]}"\n')
print("premium HTML bytes:", len(out.encode()), "pairs:", len(allp))
