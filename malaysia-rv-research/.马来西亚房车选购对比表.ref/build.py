# -*- coding: utf-8 -*-
"""马来西亚房车选购对比表 — openpyxl 直写"""

try:
    import openpyxl
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "openpyxl>=3.1.0"])
    import openpyxl

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.chart import BarChart, Reference


def xl_color(css_hex: str) -> str:
    value = css_hex.removeprefix("#").upper()
    if len(value) != 6:
        raise ValueError(f"Expected #RRGGBB, got: {css_hex}")
    return "FF" + value


XL_HEAD = xl_color("#4472C4")
XL_HEAD_TXT = xl_color("#FFFFFF")
XL_INPUT = xl_color("#D9E2F3")
XL_CALC = xl_color("#F2F2F2")
XL_SUM = xl_color("#2F5597")
XL_BORDER = xl_color("#BFBFBF")
XL_OK_BG = xl_color("#C6EFCE"); XL_OK_TX = xl_color("#006100")
XL_BAD_BG = xl_color("#FFC7CE"); XL_BAD_TX = xl_color("#9C0006")
XL_WARN_BG = xl_color("#FFEB9C"); XL_WARN_TX = xl_color("#9C6500")

thin = Side(style="thin", color=XL_BORDER)
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

wb = Workbook()

# ============ Sheet 1: 选购对比 ============
ws = wb.active
ws.title = "选购对比"

HEADERS = [
    "序号", "车型", "类型", "卖家/渠道", "年份", "底盘/平台",
    "报价(RM)", "额外费用(RM)", "落地总价(RM)",
    "厕所", "铺位数", "整备质量(kg)", "排量(cc)", "所需驾照",
    "车龄(年)", "年路税(RM)", "年保险(RM)", "年持有成本(RM)", "5年总成本(RM)",
    "推荐度", "备注",
]

# 锚点：第1行表头，数据 2..21 行，第22行合计
HDR_ROW = 1
DATA_START = 2
DATA_END = 21
TOTAL_ROW = 22

for c, name in enumerate(HEADERS, start=1):
    cell = ws.cell(row=HDR_ROW, column=c, value=name)
    cell.font = Font(bold=True, color=XL_HEAD_TXT, size=10)
    cell.fill = PatternFill("solid", fgColor=XL_HEAD)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = BORDER
ws.row_dimensions[HDR_ROW].height = 32

# 数据：(车型, 类型, 卖家, 年份, 底盘, 报价, 额外费用, 厕所, 铺位, 整备kg, 排量cc, 年保险, 推荐度, 备注)
ROWS = [
    ("Hobby Beachy 420", "拖挂", "AsiaRV Malaysia（KL）", 2022, "Hobby 单轴", 86500, 5000, "有", 3, 808, None, 0, "推荐",
     "全场最便宜的带厕所方案；内置空调；808kg 好拖；但仅 1 个座位区，无燃气灶"),
    ("Hobby Ontour 390 SF", "拖挂", "AsiaRV Malaysia（KL）", 2022, "Hobby 单轴", 120000, 5000, "有", 4, 1063, None, 0, "强烈推荐",
     "4 铺位 + 车载厕所 + DOMETIC FreshJet 2200 空调 + Truma 燃气暖风 + 3 头燃气灶 + 98L 冰箱；2 人用最均衡"),
    ("Knaus Sport 500 QDK", "拖挂", "AsiaRV Malaysia（KL）", 2022, "Knaus 单轴", 127200, 5000, "有", 6, 1166, None, 0, "可考虑",
     "已自带注册与车牌；可增载至 1,400/1,800kg；142L 冰箱；但车长 7.32m，2 人用偏大"),
    ("Knaus Südwind 450 FU 60周年", "拖挂", "AsiaRV Malaysia（KL）", 2022, "Knaus 单轴", 141300, 5000, "有", 4, 1201, None, 0, "强烈推荐",
     "2 人最佳：前床 200x138 + 后床 198x127；Thetford 坐便 + 淋浴 + 洗手盆；燃气加热"),
    ("Knaus Südwind 450 FU", "拖挂", "AsiaRV Malaysia（KL）", 2024, "Knaus 单轴", 215200, 5000, "有", 4, 1193, None, 0, "推荐",
     "同上布局但 2024 新款；注意：Gas-free 设计，炉灶与空调全靠 230V；最大载重仅 73kg"),
    ("Knaus Südwind 500 EU", "拖挂", "AsiaRV Malaysia（KL）", 2024, "Knaus 单轴", 224000, 5000, "有", 4, 1311, None, 0, "推荐",
     "双单人床布局，适合不习惯拼床的两人"),
    ("Knaus Südwind 540 FDK", "拖挂", "AsiaRV Malaysia（KL）", 2024, "Knaus 单轴", 230000, 5000, "有", 6, 1341, None, 0, "可考虑",
     "带独立儿童区与上下铺；2 人用偏大"),
    ("Maxus V80 改装 campervan（2015）", "自行式", "二手（Kuala Lumpur）", 2015, "Maxus V80", 78800, 0, "待确认", 2, 2500, 2499, 1200, "推荐",
     "最便宜的自行式带厕所候选；D 照可开；看车必须确认是盒式还是便携桶"),
    ("New Build Campervan Maxus V80（2017）", "自行式", "二手（Selangor）", 2017, "Maxus V80", 198000, 0, "待确认", 2, 2500, 1995, 1500, "可考虑",
     "整车新改装；价格已接近日本进口 Camper Lorry，性价比需现场比"),
    ("2020 Maxus V80 Turbo Diesel Campervan", "自行式", "二手（Selangor）", 2020, "Maxus V80", 168000, 0, "待确认", 2, 2500, 2499, 1500, "可考虑",
     "车龄新、里程低；适合不愿折腾的买家"),
    ("Toyota Camroad Motorhome", "自行式", "二手（Selangor / Sarawak）", 2003, "Toyota Dyna 货车", 90000, 0, "有", 3, 3200, 3000, 1300, "强烈推荐",
     "货车底盘 → 进口时免消费税；空间大；3,200kg 仍在 D 照范围；马来西亚最主流的入门 motorhome"),
    ("CAM Caravan 4WD（2018）", "自行式", "Karysma / CAM（Shah Alam）", 2018, "Plutus 皮卡 4WD", 175000, 0, "有", 2, 2900, 2771, 1600, "推荐",
     "完整卫浴 + 吊顶双人床 + 折叠沙发床 + 70L 水箱 + 40L 污水箱 + 空调 + 电磁炉 + Fiamma 遮阳篷；4WD 可进偏远地"),
    ("CAM Caravan 2WD（2014）", "自行式", "Karysma / CAM（Shah Alam）", 2014, "Plutus 皮卡 2WD", 138000, 0, "有", 2, 2800, 2771, 1500, "可考虑",
     "同上但 2WD、车龄 12 年；已超 10 年，无法办银行贷款"),
    ("CAM Caravan 全新", "自行式", "CAM Malaysia", 2026, "Plutus 皮卡", 207000, 0, "有", 2, 2900, 2771, 1800, "推荐",
     "唯一可确认能办银行贷款的自行式新车；落地即用，无进口手续"),
    ("Knaus Boxdrive 600 XL 4WD", "自行式", "AsiaRV Malaysia（KL）", 2024, "MAN TGE 4WD", 699000, 5000, "有", 4, 3160, 1968, 4000, "可考虑",
     "顶配：旋转浴室 + Thetford 坐便 + 户外淋浴 + Truma Combi 4D 柴油暖风 + 双头电磁炉；3,160kg 仍可用 D 照；价格是最大门槛"),
    ("Toyota Campervan（Hiace 改装）", "自行式", "二手（Selangor）", 2006, "Toyota Hiace", 75000, 0, "待确认", 2, 2000, 1998, 900, "可考虑",
     "Hiace 平台维修网络最好；但 2006 年车、车龄 20 年，需仔细验车"),
    ("Nissan Serena Pop-up Roof", "自行式", "二手（Kedah）", 2001, "Nissan Serena", 48500, 0, "大概率无", 2, 1700, 1998, 800, "不推荐",
     "pop-top 车型几乎肯定没有独立厕所，不满足硬性条件；仅作价格参照"),
    ("1999 Toyota Camroad Campervan 2.8", "自行式", "二手（Selangor）", 1999, "Toyota Dyna", 68888, 0, "有", 3, 3200, 2980, 1000, "推荐",
     "最便宜的日系原厂 motorhome 样本；车龄 27 年，只能私人注册（不能商用出租）"),
    ("1995 VW Kombi Westfalia", "自行式", "二手（Kedah）", 1995, "VW Kombi", 125000, 0, "有", 2, 1800, 1600, 1200, "不推荐",
     "车龄 31 年，维修零件是长期负担；价格与实用性不匹配"),
    ("MRC Motorhome cab-over", "自行式", "MRC Motorhome（Klang）", 2026, "货车底盘", 360000, 0, "有", 4, 4000, 3000, 2500, "可考虑",
     "4,000kg 超过 3,500kg → 需 E 级驾照，这是主要门槛"),
]

for i, r in enumerate(ROWS):
    row = DATA_START + i
    (model, typ, seller, year, chassis, price, extra, toilet, beds,
     weight, cc, ins, rating, note) = r

    ws.cell(row=row, column=1, value=i + 1)
    ws.cell(row=row, column=2, value=model)
    ws.cell(row=row, column=3, value=typ)
    ws.cell(row=row, column=4, value=seller)
    ws.cell(row=row, column=5, value=year)
    ws.cell(row=row, column=6, value=chassis)
    ws.cell(row=row, column=7, value=price)
    ws.cell(row=row, column=8, value=extra)
    ws.cell(row=row, column=9, value=f'=IF($G{row}="","",$G{row}+IF($H{row}="",0,$H{row}))')
    ws.cell(row=row, column=10, value=toilet)
    ws.cell(row=row, column=11, value=beds)
    ws.cell(row=row, column=12, value=weight)
    if cc is not None:
        ws.cell(row=row, column=13, value=cc)
    ws.cell(row=row, column=14, value=(
        f'=IF($C{row}="","",IF($C{row}="拖挂","DT/DAT（未开放）",'
        f'IF($L{row}<=3500,"D/DA","E")))'
    ))
    ws.cell(row=row, column=15, value=f'=IF($E{row}="","",YEAR(TODAY())-$E{row})')
    ws.cell(row=row, column=16, value=(
        f'=IF($C{row}="拖挂",50,IF($M{row}="","",'
        f'IF($M{row}<=1000,20,IF($M{row}<=1200,55,IF($M{row}<=1400,70,IF($M{row}<=1600,90,'
        f'IF($M{row}<=1800,200+0.4*($M{row}-1600),'
        f'IF($M{row}<=2000,280+0.5*($M{row}-1800),'
        f'IF($M{row}<=2500,440+0.8*($M{row}-2000),'
        f'IF($M{row}<=3000,840+1.6*($M{row}-2500),1640+1.6*($M{row}-3000)))))))))))'
    ))
    ws.cell(row=row, column=17, value=ins)
    ws.cell(row=row, column=18, value=f'=IF($P{row}="","",$P{row}+IF($Q{row}="",0,$Q{row}))')
    ws.cell(row=row, column=19, value=f'=IF($R{row}="","",$I{row}+5*$R{row})')
    ws.cell(row=row, column=20, value=rating)
    ws.cell(row=row, column=21, value=note)

# 合计行（第22行）
ws.cell(row=TOTAL_ROW, column=2, value="合计 / 平均")
ws.cell(row=TOTAL_ROW, column=9, value=f'=SUM(I{DATA_START}:I{DATA_END})')
ws.cell(row=TOTAL_ROW, column=16, value=f'=AVERAGE(P{DATA_START}:P{DATA_END})')
ws.cell(row=TOTAL_ROW, column=18, value=f'=AVERAGE(R{DATA_START}:R{DATA_END})')
ws.cell(row=TOTAL_ROW, column=19, value=f'=AVERAGE(S{DATA_START}:S{DATA_END})')

# 样式
MONEY = '#,##0'
for row in range(DATA_START, TOTAL_ROW + 1):
    for c in range(1, len(HEADERS) + 1):
        cell = ws.cell(row=row, column=c)
        cell.border = BORDER
        cell.font = Font(size=10)
        if c in (7, 8, 9, 16, 17, 18, 19):
            cell.number_format = MONEY
            cell.alignment = Alignment(horizontal="right", vertical="top")
        elif c in (1, 3, 5, 10, 11, 12, 13, 14, 15, 20):
            cell.alignment = Alignment(horizontal="center", vertical="top")
        else:
            cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        # 输入区浅底
        if c in (7, 8, 17):
            cell.fill = PatternFill("solid", fgColor=XL_INPUT)
        # 计算区浅灰底
        if c in (9, 14, 15, 16, 18, 19):
            cell.fill = PatternFill("solid", fgColor=XL_CALC)

for c in range(1, len(HEADERS) + 1):
    cell = ws.cell(row=TOTAL_ROW, column=c)
    cell.font = Font(bold=True, size=10, color=XL_HEAD_TXT)
    cell.fill = PatternFill("solid", fgColor=XL_SUM)

# 列宽
WIDTHS = {"A": 5, "B": 30, "C": 8, "D": 24, "E": 7, "F": 17, "G": 11, "H": 12, "I": 13,
          "J": 9, "K": 8, "L": 12, "M": 9, "N": 15, "O": 9, "P": 11, "Q": 11, "R": 13,
          "S": 14, "T": 11, "U": 52}
for col, w in WIDTHS.items():
    ws.column_dimensions[col].width = w

# 冻结 + 筛选
ws.freeze_panes = "C2"
ws.auto_filter.ref = f"A{HDR_ROW}:U{DATA_END}"

# 条件格式
ws.conditional_formatting.add(
    f"N{DATA_START}:N{DATA_END}",
    CellIsRule(operator="equal", formula=['"E"'], fill=PatternFill("solid", fgColor=XL_WARN_BG), font=Font(color=XL_WARN_TX, size=10)))
ws.conditional_formatting.add(
    f"N{DATA_START}:N{DATA_END}",
    FormulaRule(formula=[f'ISNUMBER(SEARCH("DT/DAT",$N{DATA_START}))'],
                fill=PatternFill("solid", fgColor=XL_BAD_BG), font=Font(color=XL_BAD_TX, size=10)))
ws.conditional_formatting.add(
    f"J{DATA_START}:J{DATA_END}",
    FormulaRule(formula=[f'OR($J{DATA_START}="大概率无",$J{DATA_START}="无")'],
                fill=PatternFill("solid", fgColor=XL_BAD_BG), font=Font(color=XL_BAD_TX, size=10)))
ws.conditional_formatting.add(
    f"T{DATA_START}:T{DATA_END}",
    CellIsRule(operator="equal", formula=['"强烈推荐"'], fill=PatternFill("solid", fgColor=XL_OK_BG), font=Font(color=XL_OK_TX, size=10)))
ws.conditional_formatting.add(
    f"T{DATA_START}:T{DATA_END}",
    CellIsRule(operator="equal", formula=['"不推荐"'], fill=PatternFill("solid", fgColor=XL_BAD_BG), font=Font(color=XL_BAD_TX, size=10)))

# 推荐度下拉
dv = DataValidation(type="list", formula1='"强烈推荐,推荐,可考虑,不推荐"', allow_blank=True, showDropDown=False)
ws.add_data_validation(dv)
dv.add(f"T{DATA_START}:T{DATA_END}")

# 图表：落地总价横向条形图（20 类 > 7，用条形图）
chart = BarChart()
chart.type = "bar"
chart.style = 10
chart.title = "各候选车型落地总价（RM）"
chart.y_axis.title = "车型"
chart.x_axis.title = "RM"
data = Reference(ws, min_col=9, min_row=HDR_ROW, max_row=DATA_END)
cats = Reference(ws, min_col=2, min_row=DATA_START, max_row=DATA_END)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.legend = None
chart.height = 20
chart.width = 24
ws.add_chart(chart, "W2")

# ============ Sheet 2: 用车成本测算 ============
ws_cost = wb.create_sheet("用车成本测算")

# 锚点：第1行标题；第4行参数表头，5..16 行输入；第19行结果表头，20..27 行结果；第30行结论
C_TITLE, C_HDR1, C_IN_START, C_IN_END = 1, 4, 5, 16
C_HDR2, C_OUT_START, C_OUT_END = 19, 20, 27
C_CONC = 30

t = ws_cost.cell(row=C_TITLE, column=1, value="年度用车成本测算 — 自行式 Campervan vs 拖挂 Caravan")
t.font = Font(bold=True, size=13, color=XL_HEAD)
ws_cost.merge_cells(start_row=C_TITLE, start_column=1, end_row=C_TITLE, end_column=4)
ws_cost.row_dimensions[C_TITLE].height = 24

for col, name in zip("ABCD", ["参数", "方案A 自行式 Campervan", "方案B 拖挂 Caravan", "口径说明"]):
    cell = ws_cost[f"{col}{C_HDR1}"]
    cell.value = name
    cell.font = Font(bold=True, color=XL_HEAD_TXT, size=10)
    cell.fill = PatternFill("solid", fgColor=XL_HEAD)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = BORDER

# 输入假设（浅蓝底，不放公式，除路税两格为派生值）
INPUTS = [
    ("落地总价(RM)", 90000, 91500, "来自「选购对比」表中同类车型的落地总价，可自行替换"),
    ("排量(cc)", 3000, None, "拖挂房车无排量，路税为固定 RM 50/年"),
    ("年路税(RM)", None, 50, "自行式按 JPJ 私家车分档公式自动计算；拖挂固定 50"),
    ("年保险(RM)", 1300, 0, "拖挂的保险通常挂在牵引车保单下，此处按 0 计"),
    ("年行驶里程(km)", 12000, 12000, "马来西亚房车车主典型年里程 8,000–15,000 km"),
    ("油耗(L/100km)", 12, 14, "自行式为货车底盘柴油 3.0L；拖挂为牵引皮卡带挂车油耗"),
    ("柴油单价(RM/L)", 3.0, 3.0, "马来西亚柴油补贴价区间，请按最新油价更新"),
    ("年营地夜数(晚)", 40, 40, "每月约 3–4 晚；营地费按具名营地均价估"),
    ("营地均价(RM/晚)", 60, 60, "参考 Payung Getaway 插电 RM 50/天、Station2 RM 60–120"),
    ("年保养维修(RM)", 1500, 1200, "自行式含发动机保养；拖挂仅轮轴与刹车保养"),
    ("年停车存放(RM)", 1200, 2400, "拖挂需更长停放位，多数住宅区不允许，故更高"),
    ("年折旧率(%)", 0.08, 0.08, "房车折旧率高于普通乘用车，8% 为保守估计"),
]
for i, (label, a, b, note) in enumerate(INPUTS):
    r = C_IN_START + i
    ws_cost.cell(row=r, column=1, value=label)
    if label == "年路税(RM)":
        ws_cost.cell(row=r, column=2, value=(
            f'=IF($B$6="",0,IF($B$6<=1000,20,IF($B$6<=1200,55,IF($B$6<=1400,70,IF($B$6<=1600,90,'
            f'IF($B$6<=1800,200+0.4*($B$6-1600),IF($B$6<=2000,280+0.5*($B$6-1800),'
            f'IF($B$6<=2500,440+0.8*($B$6-2000),IF($B$6<=3000,840+1.6*($B$6-2500),'
            f'1640+1.6*($B$6-3000))))))))))'
        ))
        ws_cost.cell(row=r, column=3, value=b)
    else:
        if a is not None:
            ws_cost.cell(row=r, column=2, value=a)
        if b is not None:
            ws_cost.cell(row=r, column=3, value=b)
    ws_cost.cell(row=r, column=4, value=note)

for col, name in zip("ABCD", ["指标", "方案A 自行式 Campervan", "方案B 拖挂 Caravan", "公式说明"]):
    cell = ws_cost[f"{col}{C_HDR2}"]
    cell.value = name
    cell.font = Font(bold=True, color=XL_HEAD_TXT, size=10)
    cell.fill = PatternFill("solid", fgColor=XL_HEAD)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = BORDER

OUT_FORMULAS = [
    ("年燃油费(RM)", "=IF({c}9=\"\",0,{c}9/100*{c}10*{c}11)", "行驶里程 ÷ 100 × 油耗 × 柴油单价"),
    ("年营地费(RM)", "=IF({c}12=\"\",0,{c}12*{c}13)", "营地夜数 × 营地均价"),
    ("年固定成本(RM)", "=IF({c}7=\"\",0,{c}7)+IF({c}8=\"\",0,{c}8)+IF({c}14=\"\",0,{c}14)+IF({c}15=\"\",0,{c}15)",
     "年路税 + 年保险 + 年保养维修 + 年停车存放"),
    ("年总成本(RM)", "={c}20+{c}21+{c}22", "燃油 + 营地 + 固定成本（不含折旧）"),
    ("每公里成本(RM/km)", "=IF(OR({c}9=\"\",{c}9=0),\"\",{c}23/{c}9)", "年总成本 ÷ 年行驶里程（已含分母空值与 0 保护）"),
    ("年折旧金额(RM)", "=IF({c}5=\"\",0,{c}5*{c}16)", "落地总价 × 年折旧率"),
    ("年真实持有成本(RM)", "={c}23+{c}25", "年总成本 + 年折旧金额"),
    ("5年总支出(RM)", "=IF({c}5=\"\",\"\",{c}5+{c}26*5)", "落地总价 + 5 × 年真实持有成本"),
]
for i, (label, f, note) in enumerate(OUT_FORMULAS):
    r = C_OUT_START + i
    ws_cost.cell(row=r, column=1, value=label)
    ws_cost.cell(row=r, column=2, value=f.format(c="B"))
    ws_cost.cell(row=r, column=3, value=f.format(c="C"))
    ws_cost.cell(row=r, column=4, value=note)

ws_cost.cell(row=C_CONC, column=1, value="结论：5 年总支出差额（方案B − 方案A）")
ws_cost.cell(row=C_CONC, column=2, value='=IF(OR($B$27="",$C$27=""),"",$C$27-$B$27)')
ws_cost.cell(row=C_CONC, column=4, value="正数 = 拖挂更贵；负数 = 拖挂更省")
ws_cost.cell(row=C_CONC + 1, column=1, value="结论：每公里成本差额（方案B − 方案A）")
ws_cost.cell(row=C_CONC + 1, column=2, value='=IF(OR($B$24="",$C$24=""),"",$C$24-$B$24)')
ws_cost.cell(row=C_CONC + 1, column=4, value="正数 = 拖挂每公里更贵")

for r in range(C_IN_START, C_IN_END + 1):
    for c in range(1, 5):
        cell = ws_cost.cell(row=r, column=c)
        cell.border = BORDER
        cell.font = Font(size=10)
        if c in (2, 3):
            cell.fill = PatternFill("solid", fgColor=XL_INPUT)
            cell.alignment = Alignment(horizontal="right")
            cell.number_format = '0.00' if r == C_IN_START + 11 else '#,##0'
        elif c == 4:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.font = Font(size=9, color=xl_color("#767676"))

for r in range(C_OUT_START, C_OUT_END + 1):
    for c in range(1, 5):
        cell = ws_cost.cell(row=r, column=c)
        cell.border = BORDER
        cell.font = Font(size=10)
        if c in (2, 3):
            cell.fill = PatternFill("solid", fgColor=XL_CALC)
            cell.alignment = Alignment(horizontal="right")
            cell.number_format = '0.00' if r == C_OUT_START + 4 else '#,##0'
        elif c == 4:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.font = Font(size=9, color=xl_color("#767676"))

for r in (C_CONC, C_CONC + 1):
    for c in range(1, 5):
        cell = ws_cost.cell(row=r, column=c)
        cell.border = BORDER
        cell.font = Font(size=10, bold=(c in (1, 2)))
        if c == 2:
            cell.fill = PatternFill("solid", fgColor=XL_SUM)
            cell.font = Font(size=10, bold=True, color=XL_HEAD_TXT)
            cell.alignment = Alignment(horizontal="right")
            cell.number_format = '#,##0.00'
        elif c == 4:
            cell.font = Font(size=9, color=xl_color("#767676"))

ws_cost.conditional_formatting.add(
    f"B{C_CONC}:B{C_CONC+1}",
    CellIsRule(operator="lessThan", formula=["0"], fill=PatternFill("solid", fgColor=XL_OK_BG), font=Font(color=XL_OK_TX, size=10, bold=True)))

for col, w in {"A": 24, "B": 22, "C": 22, "D": 58}.items():
    ws_cost.column_dimensions[col].width = w

# ============ Sheet 3: 二手实盘 ============
ws_used = wb.create_sheet("二手实盘")

U_HEADERS = ["序号", "挂牌车型", "年份", "挂牌价(RM)", "地区", "里程(km)", "状态", "厕所", "挂牌编号"]
U_ROWS = [
    ("Nissan Serena Pop-up Roof Campervan", 2001, 48500, "Kedah", "150,000–159,999", "Recon", "大概率无", "115606192"),
    ("Campervan（未注明车型）", None, 50000, "Selangor", "未注明", "Used", "待确认", "115753932"),
    ("1999 Toyota Camroad Campervan 2.8 Auto", 1999, 68888, "Selangor", "95,000–99,999", "Used", "有", "115502500"),
    ("Toyota Campervan（Hiace 改装）", 2006, 75000, "Selangor", "170,000–179,999", "Used", "待确认", "115167208"),
    ("2015 Maxus V80 2.5(M) Campervan 全改", 2015, 78800, "Kuala Lumpur", "100,000–109,999", "Used", "待确认", "114879670"),
    ("Motorhome / Caravan / Campervan（未注明）", None, 80000, "Negeri Sembilan", "未注明", "Used", "待确认", "111032071"),
    ("Campervan Status Persendirian", None, 90000, "Kuala Lumpur", "未注明", "Used", "待确认", "115772533"),
    ("Toyota Camroad Motorhome / Campervan", None, 90000, "Sarawak", "未注明", "Used", "有", "115727297"),
    ("Toyota Camroad King Bunks Bed Motorhome", None, 119000, "未注明", "未注明", "Used", "有", "114976944"),
    ("Volkswagen Kombi Westfalia Campervan", 1995, 125000, "Kedah", "5,000–9,999", "Recon", "有", "113295774"),
    ("1996 Nissan Caravan 2.5 CBU", 1996, 160000, "Selangor", "350,000–399,999", "Used", "待确认", "115284388"),
    ("2020 Maxus V80 2.5 Turbo Diesel Campervan", 2020, 168000, "Selangor", "未注明", "Used", "待确认", "115796517"),
    ("New Build Campervan Motorhome Maxus V80", 2017, 198000, "Selangor", "85,000–89,999", "Used", "待确认", "114374602"),
]
for c, name in enumerate(U_HEADERS, start=1):
    cell = ws_used.cell(row=1, column=c, value=name)
    cell.font = Font(bold=True, color=XL_HEAD_TXT, size=10)
    cell.fill = PatternFill("solid", fgColor=XL_HEAD)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = BORDER
ws_used.row_dimensions[1].height = 28

for i, (model, year, price, area, mileage, cond, toilet, pid) in enumerate(U_ROWS):
    r = 2 + i
    ws_used.cell(row=r, column=1, value=i + 1)
    ws_used.cell(row=r, column=2, value=model)
    if year is not None:
        ws_used.cell(row=r, column=3, value=year)
    ws_used.cell(row=r, column=4, value=price)
    ws_used.cell(row=r, column=5, value=area)
    ws_used.cell(row=r, column=6, value=mileage)
    ws_used.cell(row=r, column=7, value=cond)
    ws_used.cell(row=r, column=8, value=toilet)
    ws_used.cell(row=r, column=9, value=f"https://www.mudah.my/-{pid}.htm")

U_END = 1 + len(U_ROWS)
for r in range(2, U_END + 1):
    for c in range(1, 10):
        cell = ws_used.cell(row=r, column=c)
        cell.border = BORDER
        cell.font = Font(size=10)
        if c == 4:
            cell.number_format = '#,##0'
            cell.alignment = Alignment(horizontal="right")
        elif c in (1, 3, 7, 8):
            cell.alignment = Alignment(horizontal="center")
        elif c == 9:
            cell.font = Font(size=9, color=xl_color("#185FA5"), underline="single")
        else:
            cell.alignment = Alignment(horizontal="left")

ws_used.conditional_formatting.add(
    f"H2:H{U_END}",
    FormulaRule(formula=['OR($H2="大概率无",$H2="无")'],
                fill=PatternFill("solid", fgColor=XL_BAD_BG), font=Font(color=XL_BAD_TX, size=10)))

dv2 = DataValidation(type="list", formula1='"有,待确认,大概率无,无"', allow_blank=True, showDropDown=False)
ws_used.add_data_validation(dv2)
dv2.add(f"H2:H{U_END}")

for col, w in {"A": 5, "B": 42, "C": 8, "D": 12, "E": 18, "F": 17, "G": 8, "H": 11, "I": 52}.items():
    ws_used.column_dimensions[col].width = w
ws_used.freeze_panes = "C2"
ws_used.auto_filter.ref = f"A1:I{U_END}"

# ============ Sheet 4: 口径与来源 ============
ws2 = wb.create_sheet("口径与来源")
ws2.column_dimensions["A"].width = 4
ws2.column_dimensions["B"].width = 26
ws2.column_dimensions["C"].width = 96

blocks = [
    ("TITLE", "马来西亚房车选购对比表 — 口径与数据来源", ""),
    ("H", "数据截止", "2026-09-24"),
    ("H", "硬性筛选条件", "车内必须有厕所 + 可供 2 人睡觉的空间。不满足的车型保留在表中但标注为「不推荐」，仅作价格参照。"),
    ("H", "报价口径", "「报价」为商家公开挂牌价或报价；「额外费用」为运输、上牌、注册、改装等预估追加成本；落地总价 = 报价 + 额外费用。均为 RM。"),
    ("H", "年路税计算口径", "私人 RV 按私家车（Motokar）以排量计税，分档估算：≤1,000cc=20；1,001–1,200=55；1,201–1,400=70；1,401–1,600=90；1,601–1,800=200+0.40/cc；1,801–2,000=280+0.50/cc；2,001–2,500=440+0.80/cc；2,501–3,000=840+1.60/cc；>3,000=1,640+1.60/cc（均以超出该档下限的 cc 数计）。"),
    ("H", "拖挂房车路税", "JPJ 车辆发牌费率表中私人拖车（代码 AF）为固定 RM 50/年，与尺寸无关。表中拖挂车型一律按 50 计算。"),
    ("H", "路税口径验证", "按上述公式：2.8L≈1,320、3.0L≈1,640、3.4L≈2,280。车主实测口径为 2.8L≈1,300、3.0L≈1,800、3.4L≈2,200，同一量级。非轿车（SUV/MPV/van）部分费率表会上浮约 20%，最终以 MyJPJ 实算为准。"),
    ("H", "保险口径", "自行式按车主实测口径 RM 600–2,000/年取值；拖挂房车的保险通常挂在牵引车保单下，本表按 0 计。高价值进口车（如 Boxdrive 600 XL）保费显著更高。"),
    ("H", "驾照判定规则", "依据 JPJ 2026 版《房车注册与发牌指南》LAMPIRAN D：整备质量 BTM ≤3,500kg → D/DA 级；>3,500kg → E 级。拖挂房车：牵引车 ≤3,500kg 且拖挂 >750kg → 需全新的 DT/DAT 等级，该等级 JPJ 文本写明「将开发」，2026 年尚未开放考取。"),
    ("H", "检验口径", "私人注册 RV 无强制年检（按普通私家车规则）；商用 RV 须做 PPKM 初次检验并每 6 个月定期检验。表中未计入检验费用。"),
    ("H", "5 年总成本口径", "计算方式：落地总价 + 5 × 年持有成本（年路税 + 年保险）。不含燃油、营地费、维修保养、折旧与停放成本。"),
    ("H", "进口税制关键差异", "货车（HS 8704）与客车（HS 8702）底盘完全豁免消费税，有效总税负约 40%；van/MPV 底盘（HS 8703）按排量交 60–105% 消费税，有效总税负 150%+。这是 Camper Lorry / Camper Bus 在马来西亚占主流的原因。"),
    ("H", "拖挂房车税制（已核实）", "HS 8716.10.0000 最惠国进口关税 25% + 销售税 10%，有效税负约 37.5%（对 FOB 价）；不属机动车辆，免征消费税。对比 van 底盘 campervan 的 172%，差约 4.6 倍。ACFTA / RCEP / CPTPP 项下可降至 0%，需提供有效原产地证书。"),
    ("H", "落地成本反推验证", "Hobby Beachy 420（欧洲价约 €20,000 ≈ RM 93,600）→ 关税 25% + SST 10% 后 RM 128,700，加海运、VTA、工程师图纸、清关后约 RM 152,000–162,000，与 AsiaRV 标注的「原价」RM 158,888.88 高度吻合。说明清库价 RM 86,500 是真实的亏本清货。"),
    ("H", "AP 资格（已核实）", "RV 属 SPV，进口走 Other Vehicle AP，该类 AP 只发给公司且需预先批准。Individual AP 仅限海外工作/留学公民、REP、议员、使馆人员、外籍人士、MM2H 参与者 —— 普通居民不符合资格。"),
    ("H", "驾照 DT/DAT（已核实）", "JPJ 公布的完整驾照等级为 A、A1、B、B1、B2、C、D、DA、E、E1、E2、F、G、H、I —— 其中没有 DT 或 DAT。与指南「akan dibangunkan（将开发）」措辞一致，即目前无法申请。"),
    ("H", "用车成本测算口径", "年总成本 = 燃油 + 营地 + （路税 + 保险 + 保养 + 停车），不含折旧；年真实持有成本 = 年总成本 + 年折旧金额；5 年总支出 = 落地总价 + 5 × 年真实持有成本。全部为可调假设，改「用车成本测算」表的浅蓝格即可联动。"),
    ("H", "二手实盘口径", "取自 Mudah.my 公开挂牌（2026-09-24 抓取），为卖家挂牌要价而非成交价；「厕所」列中「待确认」表示挂牌信息未注明，必须现场核实。"),
    ("H", "未核实事项", "① Südwind 500 EU / 540 FDK / 450 FU 60 周年版沿用同一 KNAUS 卫浴模块，但未取得单独实拍确认；② 各二手车挂牌的实际厕所类型（盒式 vs 便携桶）；③ DT/DAT 的预计开放时间表。以上均需向卖家或 JPJ 书面确认。"),
    ("H", "主要来源", "JPJ《GARIS PANDUAN PENDAFTARAN DAN PELESENAN KENDERAAN REKREASI (RV)》(2026)：https://www.jpj.gov.my/wp-content/uploads/2026/04/GARIS-PANDUAN-PENDAFTARAN-DAN-PELESENAN-KENDERAAN-REKREASI-RV.pdf"),
    ("H", "", "AsiaRV 清库车型与价格：https://asiarv.my/demo-caravans/ · https://mobilehome.my/"),
    ("H", "", "Karysma Motorhome 价格指南：https://motorhomes.my/harga-motorhome-dan-campervan/"),
    ("H", "", "Karysma 日本进口教程：https://motorhomes.my/cara-import-motorhome-dan-campervan-japan/"),
    ("H", "", "马来西亚 8716.10.0000 关税税率（MFN 25% + SST 10%）：https://treayo.cn/en/hs/malaysia/h/8716"),
    ("H", "", "MITI 车辆 AP 分类与资格：https://www.miti.gov.my/ap"),
    ("H", "", "马来西亚整车进口税制结构：https://grokipedia.com/page/Malaysian_motor_vehicle_import_duties"),
    ("H", "", "交通部：全国 1,450+ 台 RV 已注册（2026-07）：https://nazznco.my/2026/07/15/kenderaan-rv-sah-di-sisi-undang-undang/"),
    ("H", "", "二手挂牌价格：https://www.mudah.my/malaysia/all?q=campervan"),
    ("H", "", "完整调研报告：马来西亚房车购买与使用调研报告.html（同目录）"),
]

r = 1
for kind, b, c in blocks:
    if kind == "TITLE":
        cell = ws2.cell(row=r, column=2, value=b)
        cell.font = Font(bold=True, size=14, color=XL_HEAD)
        ws2.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
        ws2.row_dimensions[r].height = 24
    else:
        k = ws2.cell(row=r, column=2, value=b)
        k.font = Font(bold=True, size=10)
        k.alignment = Alignment(vertical="top", wrap_text=True)
        v = ws2.cell(row=r, column=3, value=c)
        v.font = Font(size=10)
        v.alignment = Alignment(vertical="top", wrap_text=True)
        if b and c:
            k.border = BORDER
            v.border = BORDER
        ws2.row_dimensions[r].height = max(15, min(75, (len(c) // 90 + 1) * 15 + 4))
    r += 1

wb.properties.title = "马来西亚房车选购对比表"

OUT = r"C:\Users\Admin\WorkBuddy AI\2026-09-24-11-51-16\rv-research\马来西亚房车选购对比表.xlsx"
wb.save(OUT)
print("SAVED:", OUT)
