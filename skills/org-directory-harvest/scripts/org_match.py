#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""org_match.py —— 机构名归一 / 相似度 / 去重（可直接 import）

用途：把「官网名录里的机构名」和「Facebook 专页名」判成同一个机构，
以及把同一机构的中英文两种写法收敛成一条记录。

设计原则（血的教训，见 references/pitfalls.md 第 16–24 条）：
  1. 搜索关键词只能用来发现页面，绝不能用来判定身份。
  2. 缩写相同 ≠ 同一机构（吉打 / 吉兰丹中总都叫 KCCCI）。
  3. 母会与分会 / 属会 / 青商团 / 妇女组 一律独立成条，不合并。
  4. 境外同名机构极多，必须先按域名 TLD 与国名剔除。
  5. 繁体先转简体，再做任何比较。

用法：
    from org_match import simp, norm, toks, jac, similar, tidy, same_org, dedup
    if similar(page_name, official_name):
        ...
    orgs = dedup(orgs, key='org')

自测：python org_match.py
"""
import re

# ---------------------------------------------------------------- 繁简
TRAD = {
    '華': '华', '總': '总', '會': '会', '業': '业', '團': '团', '聯': '联', '經': '经',
    '貿': '贸', '東': '东', '馬': '马', '來': '来', '龍': '龙', '獅': '狮', '機': '机',
    '構': '构', '協': '协', '進': '进', '車': '车', '電': '电', '產': '产', '醫': '医',
    '藥': '药', '術': '术', '藝': '艺', '學': '学', '國': '国', '際': '际', '銀': '银',
    '鐵': '铁', '廠': '厂', '號': '号', '豐': '丰', '興': '兴', '賢': '贤', '僑': '侨',
    '灣': '湾', '縣': '县', '鄉': '乡', '館': '馆', '師': '师', '範': '范', '園': '园',
    '運': '运', '動': '动', '樂': '乐', '書': '书', '畫': '画', '報': '报', '聞': '闻',
    '網': '网', '絡': '络', '訊': '讯', '資': '资', '創': '创', '發': '发', '務': '务',
    '區': '区', '單': '单', '個': '个', '們': '们', '這': '这', '說': '说', '點': '点',
    '與': '与', '為': '为', '於': '于', '後': '后', '時': '时', '間': '间', '開': '开',
    '關': '关', '長': '长', '門': '门', '問': '问', '題': '题', '實': '实', '現': '现',
    '場': '场', '樣': '样', '種': '种', '稱': '称', '級': '级', '給': '给', '統': '统',
    '計': '计', '認': '认', '證': '证', '據': '据', '處': '处', '備': '备', '從': '从',
    '內': '内', '兩': '两', '並': '并', '萬': '万', '環': '环', '節': '节', '濟': '济',
    '職': '职', '轉': '转', '辦': '办', '雙': '双', '亞': '亚',
}

# 仅靠这些词相同不能判定为同一机构
COMMON = {
    'chinese', 'chamber', 'commerce', 'industry', 'industries', 'association',
    'associations', 'federation', 'council', 'society', 'the', 'and', 'of', 'for',
    'malaysia', 'malaysian', 'persatuan', 'gabungan', 'tionghua', 'trading',
    'business', 'enterprise', 'enterprises', 'corporation', 'company', 'group',
}

# 分支标记：出现即视为母会之外的下级组织，不并入母会
BRANCH = re.compile(r'分会|屬會|属会|支部|联委会|聯委會|branch|chapter', re.I)
# 青年 / 妇女组织：独立成条
SUB = re.compile(r'青商团|青年团|青商|妇女组|妇女組|女青|青年组|youth|yec', re.I)

ACRONYM = re.compile(r'\b[A-Z]{3,6}\b')

# 跨语言同义对，自动规则覆盖不到，只能手工补
MANUAL_PAIRS = [
    ('茶业商会', 'tea trade association'),
    ('茶业商会', 'tea association'),
]

# 境外 / 范围外关键词（按需增删）
FOREIGN = re.compile(
    r'华盛顿|关岛|毛里求斯|北欧|马耳他|秘鲁|乌克兰|柬埔寨|刚果|西班牙|葡萄牙|欧盟|'
    r'俄罗斯|爱尔兰|硅谷|株式会社|土耳其|印度尼西亚|孟加拉国|巴基斯坦|斯里兰卡|'
    r'澳大利亚|新西兰|加拿大|墨西哥|巴西|阿根廷|南非|埃及|尼日利亚|台湾|臺灣|香港|澳门|'
    r'Guam|Mauritius|Maltese|Nordic|Washington|WNY|Tampa|Cincinnati|Columbus|'
    r'Silicon ?Valley|Swiss-Chinese', re.I)

FOREIGN_TLD = re.compile(
    r'\.(tw|hk|mo|cn|jp|kr|id|th|vn|ph|in|au|uk|us|ca|de|fr|bd|ch|sg)$', re.I)


def simp(s):
    """繁体 → 简体"""
    return ''.join(TRAD.get(c, c) for c in (s or ''))


def norm(s):
    """去空格标点 + 小写，用于精确比对"""
    s = re.sub(r'[\s\(\)（）【】\[\]「」、,，.。·\-_/|&]+', '', simp(s))
    return s.lower()


def toks(s):
    """切成中文词块 + 英文词（≥3 字母），用于相似度"""
    s = simp(s)
    t = set(re.findall(r'[\u4e00-\u9fff]{2,}', s))
    t |= {x.lower() for x in re.findall(r'[A-Za-z]{3,}', s)}
    return t


def flat_cjk(s):
    return re.sub(r'[^\u4e00-\u9fff]', '', simp(s))


def acronym(s):
    return {a.lower() for a in ACRONYM.findall(s or '')} - COMMON


def _latin(s):
    return ' '.join(w.lower() for w in re.findall(r'[A-Za-z]{3,}', s or '')
                    if w.lower() not in COMMON)


def jac(a, b):
    """有效 token 的 Jaccard（剔除通用词与缩写）"""
    drop = COMMON | acronym(a) | acronym(b)
    ta, tb = toks(a) - drop, toks(b) - drop
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def similar(a, b, thr=0.7, ratio=0.9):
    """两个名字是否指同一机构（用于「页面名 → 官网名录名」的匹配）"""
    fa, fb = flat_cjk(a), flat_cjk(b)
    if acronym(a) & acronym(b):
        if not fa or not fb:
            return True                     # 一侧纯英文，缩写相同即同一家
        if fa == fb:
            return True
        if len(fa) >= 4 and len(fb) >= 4 and (fa in fb or fb in fa) \
                and min(len(fa), len(fb)) / max(len(fa), len(fb)) >= 0.6:
            return True                     # 如「…中华总商会 KLSCCCI (隆雪中总）」
    if jac(a, b) >= thr:
        return True
    # 中文很密，包含关系必须几乎等长才算同一机构；
    # 0.9 这个阈值是为了挡住「北霹雳中华总商会」被「霹雳中华总商会」吞掉
    if len(fa) >= 5 and len(fb) >= 5 and (fa in fb or fb in fa):
        if min(len(fa), len(fb)) / max(len(fa), len(fb)) >= ratio:
            return True
        # 全称后多挂一个 3–4 字俗称（如「…中华总商会」+「隆雪中总」）
        if len(fa) >= 8 and len(fb) >= 8 and abs(len(fa) - len(fb)) <= 4:
            return True
    return False


def tidy(nm):
    """英文为主、中文为辅的页名收敛成中文主名"""
    runs = re.findall(r'[\u4e00-\u9fff]{2,}', nm or '')
    if not runs or not re.findall(r'[A-Za-z]{3,}', nm or ''):
        return nm
    cjk = ''.join(runs)
    return simp(cjk) if len(cjk) >= 4 else nm


def is_foreign(name='', emails=(), websites=()):
    """按国名 / 邮箱域名 / 官网 TLD 判是否为境外机构"""
    if name and FOREIGN.search(simp(name)):
        return True
    doms = list(websites) + [e.split('@')[-1] for e in emails if '@' in e]
    return any(FOREIGN_TLD.search(d.strip()) for d in doms if d)


def same_org(a, b):
    """去重判定：比 similar 更严，额外处理分支、缩写、跨语言对"""
    if bool(SUB.search(a)) != bool(SUB.search(b)):
        return False
    fa, fb = flat_cjk(a), flat_cjk(b)
    if BRANCH.search(a) and BRANCH.search(b):
        return norm(a) == norm(b) or (
            len(fa) >= 4 and len(fb) >= 4 and (fa in fb or fb in fa)
            and min(len(fa), len(fb)) / max(len(fa), len(fb)) >= 0.95
            and _latin(a) == _latin(b))
    if BRANCH.search(a) or BRANCH.search(b):
        return False
    na, nb = simp(a).lower(), simp(b).lower()
    for x, y in MANUAL_PAIRS:
        if (x in na and y in nb) or (y in na and x in nb):
            return True
    if acronym(a) & acronym(b):
        if not fa or not fb:
            return True
        return fa == fb
    if jac(a, b) >= 0.75:
        return True
    if len(fa) >= 4 and len(fb) >= 4 and (fa in fb or fb in fa) \
            and min(len(fa), len(fb)) / max(len(fa), len(fb)) >= 0.95:
        return True
    return False


CONTACT_FIELDS = ('tel', 'mobile', 'email')
OTHER_FIELDS = ('fax', 'website', 'address', 'note', 'state', 'fb')


def dedup(orgs, key='org', prefer_l1=True):
    """按名称去重，合并时保留各条独有的号码（不丢手机号）"""
    out = []
    for o in orgs:
        tgt = next((m for m in out if same_org(o.get(key, ''), m.get(key, ''))), None)
        if tgt is None:
            out.append(o)
            continue
        for f in CONTACT_FIELDS:
            if not o.get(f):
                continue
            if not tgt.get(f):
                tgt[f] = o[f]
                continue
            parts = str(tgt[f]).split(' / ')
            for p in str(o[f]).split(' / '):
                if p and p not in parts:
                    parts.append(p)
            tgt[f] = ' / '.join(parts[:4])
        for f in OTHER_FIELDS:
            if not tgt.get(f) and o.get(f):
                tgt[f] = o[f]
        if prefer_l1 and o.get('layer') == 'L1' and tgt.get('layer') != 'L1':
            tgt['layer'] = 'L1'
            tgt[key] = o[key]
        elif not re.search(r'[\u4e00-\u9fff]', tgt.get(key, '')) \
                and re.search(r'[\u4e00-\u9fff]', o.get(key, '')):
            tgt[key] = o[key]
    return out


PLACE_PARENT = re.compile(
    r'^(.{4,}?(?:中华总商会|中华商会|商会))\s*(\S{2,6}?)(属会|分会|支会)$')


def merge_place_branches(orgs, key='org'):
    """把「柔佛州中华总商会 笨珍属会」与「笨珍中华总商会」归并成一条"""
    parents = []
    for o in orgs:
        m = PLACE_PARENT.match((o.get(key) or '').strip())
        if m:
            parents.append((m.group(2), o))
    attached = set()
    for o in orgs:
        if any(o is p for _, p in parents):
            continue
        nm = simp(o.get(key) or '')
        if '商会' not in nm:
            continue
        for place, par in parents:
            if place in nm and o[key] != par[key] and id(o) not in attached:
                for f in CONTACT_FIELDS:
                    if o.get(f):
                        par[f] = (par[f] + ' / ' + o[f]) if par.get(f) else o[f]
                for f in OTHER_FIELDS:
                    if not par.get(f) and o.get(f):
                        par[f] = o[f]
                if not BRANCH.search(o[key]):
                    par['note'] = ((par.get('note') + '；') if par.get('note') else '') \
                        + '亦称 ' + o[key]
                attached.add(id(o))
                break
    return [o for o in orgs if id(o) not in attached]


# ---------------------------------------------------------------- 自测
if __name__ == '__main__':
    ok = True

    def check(label, cond):
        global ok
        print(('  PASS  ' if cond else '  FAIL  ') + label)
        ok = ok and bool(cond)

    print('simp / norm / tidy')
    check('繁体转简体', simp('馬來西亞華商經貿總會') == '马来西亚华商经贸总会')
    check('norm 去标点', norm('KLSCCCI (隆雪中总）') == 'klsccci隆雪中总')
    check('tidy 取中文主名', tidy('BCCCI 民都鲁中华总商会') == '民都鲁中华总商会')
    check('tidy 纯英文不动', tidy('Malaysia Tea Trade Association')
          == 'Malaysia Tea Trade Association')

    print('similar —— 该合并的')
    check('同一机构中英顺序不同',
          similar('KLSCCCI 吉隆坡暨雪兰莪中华总商会', '吉隆坡暨雪兰莪中华总商会 KLSCCCI'))
    check('分会空格差异',
          similar('霹雳中华总商会曼绒分会-Pccci Manjung', '霹雳中华总商会 曼绒分会'))
    check('全称后挂俗称',
          similar('吉隆坡暨雪兰莪中华总商会 (隆雪中总）', '吉隆坡暨雪兰莪中华总商会 KLSCCCI'))

    print('similar —— 不该合并的')
    check('地方商会 vs 全国总会',
          not similar('关丹中华总商会', '马来西亚中华总商会 ACCCIM'))
    check('北霹雳 vs 霹雳', not similar('北霹雳中华总商会', '霹雳中华总商会'))
    check('关岛 vs 毛里求斯',
          not similar('Chinese Chamber of Commerce of Guam',
                      'Chinese Chamber of Commerce Mauritius'))

    print('same_org —— 分支与缩写')
    check('母会 vs 分会不合并',
          not same_org('REHDA 马来西亚房地产发展商会 Johor分会',
                       'REHDA 马来西亚房地产发展商会'))
    check('两个分会不互相吞并',
          not same_org('REHDA 马来西亚房地产发展商会 Johor分会',
                       'REHDA 马来西亚房地产发展商会 Penang分会'))
    check('KCCCI 撞车不合并',
          not same_org('吉打中华总商会 KCCCI', '吉兰丹中华总商会 KCCCI'))
    check('缩写补全后合并',
          same_org('Federation of Malaysian Manufacturing - FMM', '马来西亚厂商联合会 FMM'))
    check('跨语言手工对',
          same_org('Malaysia Tea Trade Association', '马来西亚茶业商会'))

    print('is_foreign')
    check('国名命中', is_foreign('柬埔寨中国商会'))
    check('TLD 命中', is_foreign('XX Chamber', emails=['a@b.org.tw']))
    check('马来西亚正常', not is_foreign('马来西亚中华总商会 ACCCIM',
                                        emails=['acccim@acccim.org.my'],
                                        websites=['https://acccim.org.my']))

    print('merge_place_branches + dedup')
    orgs = [
        dict(org='柔佛州中华总商会 笨珍属会', layer='L1'),
        dict(org='笨珍中华总商会', layer='L3', mobile='+60 19-702 2678'),
        dict(org='Federation of Malaysian Manufacturing - FMM', layer='L3',
             email='webmaster@fmm.org.my'),
        dict(org='马来西亚厂商联合会 FMM', layer='L1', email='info@fmm.org.my'),
    ]
    orgs = merge_place_branches(orgs)
    check('属会按地名归并', len(orgs) == 3 and orgs[0].get('mobile') == '+60 19-702 2678')
    check('归并后保留别名', '亦称 笨珍中华总商会' in orgs[0].get('note', ''))
    orgs = dedup(orgs)
    fmm = [o for o in orgs if 'FMM' in o['org']]
    check('FMM 合并成一条', len(fmm) == 1 and fmm[0]['layer'] == 'L1')
    check('合并后号码不丢', 'webmaster@fmm.org.my' in fmm[0]['email'])

    print()
    print('ALL PASS' if ok else 'SOME FAILED')
    raise SystemExit(0 if ok else 1)
