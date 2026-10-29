"""马来西亚电话归一/校验 + 州属推断（可 import，也可当 CLI 自测）

用法:
  python my_phone.py +60378049154 0182555867 "089-123 456"
  python my_phone.py --state "No.9, Jalan SS25/24, 47301 Petaling Jaya, Selangor"

被 build 脚本 import 的常用组合:
  from my_phone import phones, split_phones, state_from_addr, valid
"""
import re
import sys

# ---------------------------------------------------------------- 电话
PH = re.compile(r'(?:\+?60|0)[\s\-()]?\d{1,2}[\s\-()]?\d{3,4}[\s\-]?\d{3,4}')
MOB_PREFIX = {'10', '11', '12', '13', '14', '15', '16', '17', '18', '19'}


def fmt(raw):
    """任意写法 -> '+60 A-XXXX XXXX'；无法识别返回 ''"""
    d = re.sub(r'\D', '', raw or '')
    if d.startswith('0'):
        d = '60' + d[1:]
    if not d.startswith('60'):
        return ''
    s = d[2:]
    if len(s) < 8:
        return ''
    if s.startswith('1'):
        area, rest = s[:2], s[2:]          # 01x 手机
    elif s[0] == '8':
        area, rest = s[:2], s[2:]          # 08x 东马（082–089）
    elif s[0] == '3':
        area, rest = '3', s[1:]            # 03 吉隆坡/布城
    else:
        area, rest = s[0], s[1:]           # 04/05/06/07/09
    if len(rest) == 8:
        body = rest[:4] + ' ' + rest[4:]
    elif len(rest) in (6, 7):
        body = rest[:3] + ' ' + rest[3:]
    else:
        body = rest
    return '+60 %s-%s' % (area, body)


def valid(f):
    """按区号位数规则校验。8 位座机 / 9 位 03 / 9–10 位手机"""
    s = re.sub(r'\D', '', f or '')
    if not s.startswith('60'):
        return False
    n = s[2:]
    if n.startswith('1'):
        return len(n) in (9, 10) and n[:2] in MOB_PREFIX
    if n[:1] == '3':
        return len(n) == 9
    if n[:1] in '45679':
        return len(n) == 8
    if n[:2] in ('82', '83', '84', '85', '86', '87', '88', '89'):
        return len(n) == 8
    return False


def phones(text):
    """从一段文本抽出所有合法号码，去重保序"""
    out = []
    for m in PH.findall(text or ''):
        f = fmt(m)
        if f and valid(f) and f not in out:
            out.append(f)
    return out


def split_phones(ps):
    """[(手机...)], [(座机...)]  —— 用于把「联络电话」一栏拆成两列"""
    mob, land = [], []
    for p in ps or []:
        d = re.sub(r'\D', '', p or '')
        if not d:
            continue
        n = d[2:] if d.startswith('60') else d
        (mob if n.startswith('1') else land).append(p)
    return mob, land


# ---------------------------------------------------------------- 州属
# 顺序要紧：先匹配长名，避免 'Kuala Lumpur' 被 'Kuala' 抢先
STATE_EN = [
    ('WILAYAH PERSEKUTUAN KUALA LUMPUR', '吉隆坡'), ('KUALA LUMPUR', '吉隆坡'),
    ('WILAYAH PERSEKUTUAN PUTRAJAYA', '布城'), ('PUTRAJAYA', '布城'),
    ('WILAYAH PERSEKUTUAN LABUAN', '纳闽'), ('LABUAN', '纳闽'),
    ('PULAU PINANG', '槟城'), ('PENANG', '槟城'),
    ('NEGERI SEMBILAN', '森美兰'),
    ('JOHOR', '柔佛'), ('KEDAH', '吉打'), ('KELANTAN', '吉兰丹'),
    ('MELAKA', '马六甲'), ('MALACCA', '马六甲'),
    ('PAHANG', '彭亨'), ('PERAK', '霹雳'), ('PERLIS', '玻璃市'),
    ('SABAH', '沙巴'), ('SARAWAK', '砂拉越'), ('SELANGOR', '雪兰莪'),
    ('TERENGGANU', '登嘉楼'),
]

# 邮编区间（已修正：78000 淡边属森美兰，不属马六甲）
PC_RANGE = [
    (2000, 2999, '玻璃市'),
    (5000, 9999, '吉打'),
    (10000, 14999, '槟城'),
    (15000, 18999, '吉兰丹'),
    (20000, 24999, '登嘉楼'),
    (25000, 28999, '彭亨'),
    (39000, 39999, '彭亨'),
    (49000, 49999, '彭亨'),
    (30000, 36999, '霹雳'),
    (40000, 48999, '雪兰莪'),
    (50000, 60999, '吉隆坡'),
    (62000, 62999, '布城'),
    (63000, 64999, '雪兰莪'),
    (65000, 68999, '雪兰莪'),
    (70000, 73999, '森美兰'),
    (75000, 77999, '马六甲'),
    (78000, 78999, '森美兰'),
    (79000, 86999, '柔佛'),
    (87000, 87999, '纳闽'),
    (88000, 92999, '沙巴'),
    (93000, 98999, '砂拉越'),
]

# 城市/地名 -> 州（页面名、地址都可能出现）
CITY_HINT = [
    ('乔治市', '槟城'), ('George Town', '槟城'), ('北海', '槟城'), ('Butterworth', '槟城'),
    ('大山脚', '槟城'), ('Bukit Mertajam', '槟城'), ('北赖', '槟城'), ('Prai', '槟城'),
    ('新山', '柔佛'), ('Johor Bahru', '柔佛'), ('麻坡', '柔佛'), ('Muar', '柔佛'),
    ('峇株巴辖', '柔佛'), ('Batu Pahat', '柔佛'), ('居銮', '柔佛'), ('Kluang', '柔佛'),
    ('古来', '柔佛'), ('Kulai', '柔佛'), ('昔加末', '柔佛'), ('Segamat', '柔佛'),
    ('笨珍', '柔佛'), ('Pontian', '柔佛'), ('哥打丁宜', '柔佛'), ('Kota Tinggi', '柔佛'),
    ('马六甲', '马六甲'), ('Melaka', '马六甲'), ('Malacca', '马六甲'),
    ('芙蓉', '森美兰'), ('Seremban', '森美兰'), ('波德申', '森美兰'), ('马口', '森美兰'),
    ('淡边', '森美兰'), ('Tampin', '森美兰'),
    ('怡保', '霹雳'), ('Ipoh', '霹雳'), ('太平', '霹雳'), ('Taiping', '霹雳'),
    ('安顺', '霹雳'), ('Teluk Intan', '霹雳'), ('金宝', '霹雳'), ('Kampar', '霹雳'),
    ('实兆远', '霹雳'), ('Sitiawan', '霹雳'),
    ('亚罗士打', '吉打'), ('Alor Setar', '吉打'), ('双溪大年', '吉打'), ('Sungai Petani', '吉打'),
    ('居林', '吉打'), ('Kulim', '吉打'),
    ('哥打巴鲁', '吉兰丹'), ('Kota Bharu', '吉兰丹'),
    ('瓜拉登嘉楼', '登嘉楼'), ('Kuala Terengganu', '登嘉楼'),
    ('关丹', '彭亨'), ('Kuantan', '彭亨'), ('文冬', '彭亨'), ('Bentong', '彭亨'),
    ('劳勿', '彭亨'), ('Raub', '彭亨'),
    ('加央', '玻璃市'), ('Kangar', '玻璃市'),
    ('莎阿南', '雪兰莪'), ('Shah Alam', '雪兰莪'), ('八打灵', '雪兰莪'), ('Petaling', '雪兰莪'),
    ('巴生', '雪兰莪'), ('Klang', '雪兰莪'), ('蒲种', '雪兰莪'), ('Puchong', '雪兰莪'),
    ('加影', '雪兰莪'), ('Kajang', '雪兰莪'), ('万挠', '雪兰莪'), ('Rawang', '雪兰莪'),
    ('古晋', '砂拉越'), ('Kuching', '砂拉越'), ('诗巫', '砂拉越'), ('Sibu', '砂拉越'),
    ('美里', '砂拉越'), ('Miri', '砂拉越'), ('民都鲁', '砂拉越'), ('Bintulu', '砂拉越'),
    ('亚庇', '沙巴'), ('Kota Kinabalu', '沙巴'), ('山打根', '沙巴'), ('Sandakan', '沙巴'),
    ('斗湖', '沙巴'), ('Tawau', '沙巴'), ('根地咬', '沙巴'), ('Keningau', '沙巴'),
    ('拿笃', '沙巴'), ('Lahad Datu', '沙巴'), ('仙本那', '沙巴'), ('Semporna', '沙巴'),
    ('吉隆坡', '吉隆坡'), ('Kuala Lumpur', '吉隆坡'),
    ('布城', '布城'), ('Putrajaya', '布城'), ('纳闽', '纳闽'), ('Labuan', '纳闽'),
]


def state_from_addr(addr, name='', default=''):
    """州属推断三步：地址里的英文州名 -> 地名 -> 邮编（取最后一个，从右往左）"""
    a = addr or ''
    for en, zh in STATE_EN:
        if re.search(r'\b%s\b' % en.replace(' ', r'\s+'), a, re.I):
            return zh
    t = a + ' ' + (name or '')
    for k, v in CITY_HINT:
        if k and k in t:
            return v
    for p in reversed(re.findall(r'\b(\d{5})\b', a)):
        n = int(p)
        for lo, hi, s in PC_RANGE:
            if lo <= n <= hi:
                return s
    return default


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--state':
        print(state_from_addr(' '.join(sys.argv[2:])))
    elif len(sys.argv) > 1:
        for a in sys.argv[1:]:
            f = fmt(a)
            print('%-22s -> %-20s %s' % (a, f or '(无法识别)', 'OK' if valid(f) else 'INVALID'))
    else:
        # 自测
        cases = ['+60378049154', '0182555867', '089-123 456', '07-8650206',
                 '011-1035 1346', '082-257634', '012-328 3457']
        for c in cases:
            f = fmt(c)
            print('%-18s -> %-18s %s' % (c, f, 'OK' if valid(f) else 'INVALID'))
        print()
        for a in ['78000 Tampin, Negeri Sembilan', 'No.9, Jalan SS25/24, 47301 Petaling Jaya, Selangor',
                  'Lot 1957, Batu 8, Jalan Batu Pahat, 86000 Kluang, Johor', 'P.O. Box 123, 93700 Kuching']:
            print('%-62s -> %s' % (a[:62], state_from_addr(a)))
