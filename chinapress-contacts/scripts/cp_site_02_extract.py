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
        r"副校长|警监|助理警监|警曹长|警曹|警长|警探|警官|警员|警員|总编辑|主编|干事长|总会长|署理会长|"
        r"院长|院長|园长|園長|院长|副校长|院长)")
# 姓名尾部会粘连职务，剥离后回填 role（如「艾达警长」→ 艾达 / 警长）
ROLE_TAIL = re.compile(r"(" + ROLE + r")$")
CJK_FULL = re.compile(r"^[\u4e00-\u9fa5]+$")
# 人名里几乎不会出现的虚词/连接字
FUNC = set("的或也都就是为為对對从從到把被让讓给給这這那此其该該每些很又再及与與了而且并並将將已曾由据據说說称稱")
TITLE_PREFIX = ("投诉局主任|执行秘书|总执行长|执行董事|副主席|副秘书|副主任|副财政|副团长|"
                "总策划|总协调|总干事|负责老师|票务组组长|查案官|大会主席|工委会主席|筹委会主席|"
                "拿督斯里|拿督威拉|准拿督|太平局绅|拿督|丹斯里|董事长|署理主席|执行长|销售经理|销售执行员|"
                "行政助理|活動執行官|活动执行官|執行官|执行官|財政|财政|大姐|二姐|助理|总领队|领队|总团长|团长|"
                "活动统筹|活動統籌|统筹|統籌|选区助理|選區助理|行政|行政处|" 
                "业务发展部|業務發展部|发展部|市場部|市场部|廣告部|广告部|票务|会务|财务|总务|教务|医务|筹募|"
                "商会会长|家协主席|校友会主席|主席|主任|营长|团长|林长|秘书|会长|理事|总务|财政|"
                "校长|住持|组长|班长|队长|顾问|干事|协调员|辅导员|村长|市议员|州议员|发言人|经理|总监|律师|医生|"
                "事务处|事務處|文教组|文教組|福利组|福利組|利组|利組|警官|警曹|"
                # 单字机构/警区前缀（「警区伍宗崇」被切剩「区伍宗崇」）
                "区|區|团|團|组|組|馆|館|处|處")
NAME_TAIL = re.compile(
    r"(?:" + TITLE_PREFIX + r")?([\u4e00-\u9fa5]{2,4})(?:" + ROLE + r")?\s*[（(]?\s*[：:]?\s*[，,、]?\s*$"
)
# 行尾锚定的版本，用于逐起点回溯
NAME_TAIL_A = re.compile(
    r"^(?:" + TITLE_PREFIX + r")?([\u4e00-\u9fa5]{2,4})(?:" + ROLE + r")?\s*[（(]?\s*[：:]?\s*[，,、]?\s*$"
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
              "办公室", "辦公室", "道北", "志愿", "志願", "行", "署", "廳", "厅", "主任", "线", "線",
              "Hotline", "HOTLINE", "hotline")
BAD_HEAD = set("的了和与及或请在於于为对从到向往把被让给这那此其该各个每些有是无不很就都也还又再处办座坊"
               "可情话络系划联请欲想要打拨致询查而且并将已曾正由经据指说称表透他她它我你们本另同以若如因所"
               "地之乎者太最更非没未别勿莫垂谘洽电手号预报名订购买卖供求需舍线进票务会教医总财"
               "提部院人乐工系繫络絡督拿丹准太园关长讯销通员")

# 姓名内部只要出现这些机构/动作碎片，就不是人名（整条丢弃）
BAD_CONTAINS = (
    "警方", "交警", "警区", "警區", "警查", "案官", "院方", "官员", "官員", "警署", "警局",
    "县", "縣", "州", "市", "花园", "花園", "商店", "银行", "銀行", "对面", "對面", "诊所", "診所",
    "饭店", "飯店", "眼镜", "眼鏡", "脚车", "腳車", "花店", "店铺", "店鋪", "職員", "职员",
    "校友", "家协", "家協", "团体", "團體", "华团", "華團", "文教", "秘书", "秘書", "执行", "執行",
    "筹委", "籌委", "会所", "會所", "泊車", "泊车", "小组", "小組", "专线", "專線", "直线", "直線",
    "行动室", "行動室", "协助", "協助", "寻求", "尋求", "民防", "部队", "部隊", "义卖", "義賣",
    "行列", "布施", "领取", "領取", "索取", "提供", "给予", "給予", "做为", "做為", "有事", "欲知",
    "自行", "面书", "面書", "局绅", "局紳", "上门", "上門", "合会", "合會", "教務", "教务",
    "執法", "执法", "伤队", "傷隊", "庙祝", "廟祝", "马华", "馬華", "市民", "学生", "學生",
    "事务处", "事務處", "電話", "电话", "號碼", "号码", "詳情", "详情",
    "反映", "情况", "情況", "调查", "調查", "固定线", "固定線", "负责", "負責", "作出", "透过", "透過",
    "即日起", "酒店", "车店", "車店", "镜店", "鏡店", "协调", "協調", "协理", "協理", "成员", "成員",
    "警察", "服务", "服務", "兴趣", "興趣", "直接", "更多", "时间", "時間", "会员", "會員",
    "议会", "議會", "执照", "執照", "社区", "社區", "书记", "書記", "灾情", "災情", "机构", "機構",
    "公共", "工程", "卫生", "衛生", "人大", "政府", "村委", "天灾", "天災", "施工", "行动", "行動",
    "区部", "區部", "区会", "區會", "马江", "馬江", "江区", "江區", "劳勿区", "勞勿區", "关丹区", "關丹區",
    "相关", "相關", "海事", "公司", "客户", "客戶", "佛教", "中华", "中華", "商会", "商會",
    "包括", "高原", "法雨", "法會", "法会", "园丘", "園丘", "弘法", "尽快", "盡快",
    "糕点", "糕點", "或",
)

# 地名（东海岸/全国常见），避免「云冰警方」被砍成「云冰」后当成姓名
PLACE = (
    "云冰", "雲冰", "劳勿", "勞勿", "文冬", "关丹", "關丹", "而连突", "而連突", "淡马鲁", "淡馬魯",
    "百乐", "百樂", "北根", "话望生", "話望生", "哥打峇鲁", "哥打峇魯", "道北", "瓜拉吉赖", "瓜拉吉賴",
    "丹那美拉", "马樟", "馬樟", "巴西富地", "龙运", "龍運", "甘马挽", "甘馬挽", "勿述", "士兆",
    "瓜拉登嘉楼", "瓜拉登嘉樓", "彭亨", "吉兰丹", "吉蘭丹", "登嘉楼", "登嘉樓", "直凉", "直涼",
    "明加叻", "加叻", "地里望", "文德甲", "金马扬", "金馬揚", "姆阿占沙", "瓜拉冼都",
    "云顶", "雲頂", "澹马鲁", "澹馬魯", "士满慕", "士滿慕", "武吉丁宜", "贞德灵", "貞德靈",
    "马兰", "馬蘭", "文积", "文積", "文达", "文達", "双溪", "雙溪", "甘孟", "斯里", "德里",
)

# 尾部机构词/地名整块剥离，防止「行动室」被回溯切成「动室」
BAD_TAIL = re.compile(
    r"(?:" + "|".join(map(re.escape, sorted(set(list(BAD_CONTAINS) + list(BAD_SUFFIX) + list(PLACE)),
                                          key=len, reverse=True))) + r")"
    r"\s*[（(]?\s*[：:]?\s*[，,、]?\s*$")

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
    if n[0] not in SURNAME:
        return False
    if n[-1] in BAD_SUFFIX or n[-2:] in BAD_SUFFIX or n[-3:] in BAD_SUFFIX:
        return False
    if any(w in n for w in BAD_CONTAINS):
        return False
    # 姓名里带地名 → 是「劳勿中华/云顶高原/彭亨佛教」这类机构名，不是人
    if any(p in n for p in PLACE):
        return False
    # 含虚词的绝不可能是人名（花或糕点 / 须尽快…）
    if any(ch in n for ch in FUNC):
        return False
    if any(w in n for w in ("电话", "联络", "洽询", "报名", "询问", "详情", "查询", "热线", "投诉")):
        return False
    # 4 字且第 2 字是「区/區」→ 几乎必然是「警区+姓名」被切坏
    if len(n) == 4 and n[1] in "区區":
        return False
    if any(ch.isdigit() for ch in n):
        return False
    return True

def split_role(name):
    """把粘连在姓名尾部的职务剥离出来：艾达警长 → (艾达, 警长)"""
    m = ROLE_TAIL.search(name)
    if m and len(name) - len(m.group(1)) >= 2:
        return name[: -len(m.group(1))], m.group(1)
    return name, ""

LEAD_STRIP = set("组組团團馆館处處")

# 姓氏表（简繁双写）：中文姓名首字必须命中，否则「客户服务/兴趣/直接」这类短语会被当成人名。
# 复姓（欧阳/司马/诸葛…）首字已单列，命中首字即可。
_SURNAME_RAW = (
    "赵錢孙李周吴吳郑鄭王冯馮陈陳褚卫衛蒋蔣沈韩韓杨楊朱秦尤许許何吕呂施张張孔曹严嚴华華金魏陶姜"
    "戚谢謝邹鄒喻柏水窦竇章云雲苏蘇潘葛奚范彭郎鲁魯韦韋昌马馬苗凤鳳花方俞任袁柳酆鲍鮑史唐费費廉岑薛雷贺賀"
    "倪汤湯滕殷罗羅毕畢郝邬鄔安常乐樂于於时時傅皮卞齐齊康伍余元卜顾顧孟平黄黃和穆萧蕭尹姚邵湛汪祁毛禹狄米"
    "贝貝明臧计計伏成戴谈談宋茅庞龐熊纪紀舒屈项項祝董梁杜阮蓝藍闵閔席季麻强強贾賈路娄婁危江童颜顏郭梅盛林"
    "刁钟鐘鍾徐邱骆駱高夏蔡田樊胡凌霍虞万萬支柯昝管卢盧莫经經房裘缪繆干解应應宗丁宣贲賁邓鄧郁单單杭洪包诸諸"
    "左石崔吉钮鈕龚龔程嵇邢滑裴陆陸荣榮翁荀羊惠甄曲家封芮羿储儲靳汲邴糜松井段富巫乌烏焦巴弓牧隗山谷车車侯"
    "蓬全郗班仰秋仲伊宫宮宁寧仇栾欒暴甘厉厲戎祖武符刘劉景詹束龙龍叶葉幸司韶郜黎蓟薊薄印宿白怀懷蒲邰鄂索咸"
    "籍赖賴卓蔺藺屠蒙池乔喬阴陰胥能苍蒼双雙闻聞莘党黨翟谭譚贡貢劳勞逄姬申扶堵冉宰郦酈雍璩桑桂濮牛寿壽通边邊"
    "扈燕冀郏郟浦尚农農温溫别別庄莊晏柴瞿阎閻充慕连連茹习習宦艾鱼魚容向古易慎戈廖庾终終暨居衡步都耿满滿弘"
    "匡国國文寇广廣禄祿阙闕东東欧歐殳沃利蔚越夔隆师師巩鞏聂聶晁勾敖融冷訾辛阚闞那简簡饶饒空曾毋沙养養鞠须須"
    "丰豐巢关關蒯相查后後荆荊红紅游竺权權逯盖蓋益桓公"
    "丘冼练練麦麥锺澹粱昙曇佘禤綦"
    "邝鄺岑覃涂塗游遊辜蓝藍纪紀官甘韦韋欧阳歐陽司马司馬上官诸葛諸葛司徒"
    # 音译姓名首字（马来/印度裔中文译名）
    "阿哈慕莫沙莎赛賽伊依拉卡迪奥奧法菲娜峇玛瑪曼米达達布嘉芝诺諾威维維尼妮雅山查淡斯士里"
)
SURNAME = set(ch for ch in _SURNAME_RAW if "\u4e00" <= ch <= "\u9fa5")
# 姓氏优先：BAD_HEAD 里与真姓氏冲突的字（莫/曾/于/关/乐/查/向/那/通…）让位，
# 否则「莫哈敏」「曾庆瑞」这类正确姓名会被当成动词开头而丢弃。
# 只给「既常见姓氏、又几乎不作虚词」的字让路（莫/曾/乐）。
# 于於通和向关關那查同 虽然也是姓氏，但作虚词/动词的频率远高于作姓，继续拦。
RELEASE = set("莫曾乐樂")
BAD_HEAD -= RELEASE
FUNC -= RELEASE
def strip_lead(name):
    """剥掉被切坏的机构首字：组黄宝燕 → 黄宝燕（区/區 是姓氏，不剥）"""
    while len(name) > 2 and name[0] in LEAD_STRIP:
        name = name[1:]
    return name

def pick_name(win):
    """取姓名：先试最左整体匹配；失败则逐起点回溯，取第一个通过校验的候选。
    解决「可联络麦子康（」把动词末字『络』吃进姓名（络麦子康）导致整条丢弃的问题。"""
    m = NAME_TAIL.search(win)
    if m and ok_name(m.group(1)):
        return m.group(1), m
    n = len(win)
    for i in range(1, n):
        m = NAME_TAIL_A.match(win[i:])
        if m and ok_name(m.group(1)):
            return m.group(1), m
    return "", None

def ok_name_en(n):
    n = (n or "").strip(" .'")
    if len(n) < 3:
        return False
    if n.upper() in ("TEL", "CALL", "FAX", "EMAIL", "WHATSAPP", "PBB", "MBB", "RHB", "CIMB",
                     "PUBLIC", "BANK", "HONG", "LEONG", "THE", "AND", "FOR", "YOU", "MAY",
                     "HOTLINE", "OFFICE", "TEAM", "GROUP", "SALES", "INFO", "MALAYSIA", "MELAKA",
                     "SDN", "BHD", "JOHOR", "PENANG", "SINGAPORE",
                     "PAHANG", "KEMAMAN", "KUANTAN", "TERENGGANU", "KELANTAN", "SELANGOR",
                     "PERAK", "SABAH", "SARAWAK", "PUTRAJAYA", "ADU", "EZ"):
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
        # 先去掉尾部的括号/标点，否则剥离规则会被「（」卡住
        win = win.rstrip(" \t\u3000（(【[「『：:，,、；;。")
        # 交替剥离「尾部动词」与「尾部机构词/地名」，直到稳定
        for _ in range(4):
            new = TAIL_STRIP.sub("", win)
            new = BAD_TAIL.sub("", new)
            if new == win:
                break
            win = new
        name, role, src = "", "", ""
        mm = None
        cand, mm = pick_name(win)
        if cand:
            name = strip_lead(cand)
            r = re.match(r"\s*(" + ROLE + r")", mm.string[mm.end(1):])
            role = r.group(1) if r else ""
            src = "adjacent"
        else:
            me = NAME_EN_TAIL.search(win)
            if me and ok_name_en(me.group(1)):
                name = me.group(1).strip()
                src = "adjacent"
        # 姓名尾部粘连的职务剥离（艾达警长 → 艾达 / 警长）；仅对纯中文姓名生效
        if name and CJK_FULL.match(name):
            name, r2 = split_role(name)
            role = role or r2
            if not ok_name(name):
                name, role = "", ""
        if not name:
            tail = body[m.end():m.end() + 20]
            # 先吃掉职务前缀，避免「主任志文」整体被当姓名
            mp = re.match(r"\s*[（(]?\s*(?:" + TITLE_PREFIX + r")", tail)
            if mp:
                tail = tail[mp.end():]
            mt = re.match(r"\s*[（(]?\s*([\u4e00-\u9fa5]{2,4})(?:" + ROLE + r")?\s*[)）]?(?=[\s，,、；;。]|$)",
                          tail)
            if mt and ok_name(mt.group(1)):
                name, src = strip_lead(mt.group(1)), "after"
                name, r3 = split_role(name)
                role = role or r3
                if not ok_name(name):
                    name = ""
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
