#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一名单解析器：把各商会/社团的「理事名表」转成同一份人员 schema。

【复用方式】下面的 SRC 是一张**配置表**，换项目时只改 SRC 即可，
五种版式的解析函数不用动。每行 = (txt 文件名, 机构正式名, 版式, 起始标记, 结束标记[, 第几次出现])

版式：
  role_first        职务行 → 1..N 个姓名（可「、」分隔）→ 可选所属团体
  name_first        姓名 → 职务
  en_pair           英文职务 → 中文职务 → 英文名 → 中文名
  en_role           英文职务 → 英文名（可多行）
  en_pairs          姓名行 + 公司行交替（FMM / REHDA 那种）
  name_job_company  姓名 → 本职 → 公司

注意：职务判定必须早于姓名判定，否则「主席/财政/董事」这类两字职务会被当成人名。
详见 references/pitfalls.md 第 25–32 条。

覆盖五种版式：
  role_first        职务行 → 1..N 个姓名（可含「、」分隔）→ 可选所属团体
  name_first        姓名 → 职务
  en_pair           英文职务 → 中文职务 → 英文名 → 中文名
  en_role           英文职务 → 英文名（可多行）
  name_job_company  姓名 → 本职 → 公司

输出：_raw/cc/lists2_people.jsonl
"""
import io
import json
import re

OUT = '_raw/cc/lists2_people.jsonl'

HONOR = re.compile(r'^(拿督斯里|拿督威拉|拿督巴杜卡|拿督|丹斯里|敦|准拿督|太平局绅)')
SUFFIX = re.compile(r'(先生|女士|小姐|局绅|博士|硕士|教授|副教授|医生|医师|律师|工程师|建筑师|'
                    r'会计师|特许税务员|上议员|太平绅士)$')
CJK_NAME = re.compile(r'^[\u4e00-\u9fff]{2,6}$')

# 职务：以职务词结尾即算（容许「商务/数字经济及中小企业组主任」这类长职务）
ROLE = re.compile(r'(会长|副会长|署理会长|秘书|副秘书长|副总秘书|总秘书|财政|副财政|'
                  r'总务|副总务|主席|署理主席|副主席|团长|署理团长|副团长|总团长|署理总团长|'
                  r'副总团长|董事|常务董事|查账|稽查员|顾问|执行顾问|委员|常务委员|'
                  r'主任|副主任|组长|正组长|主委|总执行长)$')

ROLE_EN = re.compile(r'(President|Advisor|Secretary|Treasurer|Officer|Member|Chairman|'
                     r'Director|Auditor|Council|Committee)', re.I)
PREFIX_EN = re.compile(r'^(Adjunct Prof|Prof\.?|Dr\.?|Ir\.?|Ts\.?|Mr\.?|Ms\.?|Mrs\.?|'
                       r"Dato'? Sri|Dato'? Seri|Dato'?|Datuk|Tan Sri|YB|Senator)$", re.I)

ORG = re.compile(r'(会馆|公会|协会|商会|校友会|基金会|理事会|联宗会|书院|同乡会|总会|堂$|团$|'
                 r'联合会|联谊会|宗亲会|俱乐部|学会|社$|阁$|庙$|寺$|委员会|公所|互助会|'
                 r'体育会|华团|联会|董联|华堂|大会堂|校友联|商会|公司|Sdn|Bhd|'
                 r'中学|小学|独中|华小|校友|公会|商会)')

GROUP = re.compile(r'(组|委员会|部|局|团)$')


def is_role(s):
    """职务行判定必须早于姓名判定：「主席」「财政」「董事」都是两字，会被误当人名"""
    return bool(s) and len(s) <= 40 and bool(ROLE.search(s)) and s not in ('主席团',)

NOT_NAME = set('''会长 副会长 署理会长 秘书 财政 总务 董事 查账 顾问 委员 主任 副主任
主席 副主席 团长 副团长 青商团 妇女组 理事会 董事会 常务委员会 工作委员会 会务组
财务策划组 国际贸易组 商务组 中小型企业组 人力资源组 法律组 国民团结组 青商团活动'''.split())


def clean(s):
    return re.sub(r'\s+', ' ', (s or '').replace('\xa0', ' ')).strip()


HONOR_CODE = re.compile(r'\s+(?:[A-Z]{2,6}\s*,?\s*)+$|\s*[A-Z]{2,6}\s*$|县议员$|州议员$|上议员$')


def split_name(s):
    """→ (honor, name) ；剥两次勋衔 + 一次学位/称谓后缀 + 尾部勋衔代码"""
    p = HONOR_CODE.sub('', clean(s)).strip()
    hon = ''
    for _ in range(2):
        m = HONOR.match(p)
        if not m:
            break
        hon = (hon + ' ' + m.group(1)).strip()
        p = p[m.end():].strip()
    p = SUFFIX.sub('', p).strip()
    p = HONOR.sub('', p).strip()
    return hon, p


def is_name(s):
    if not s or s in NOT_NAME:
        return False
    _, n = split_name(s)
    return bool(CJK_NAME.match(n))


def split_multi(s):
    """「甲、乙、丙」→ ['甲','乙','丙']"""
    parts = re.split(r'[、，,；;/]', clean(s))
    return [p.strip() for p in parts if p.strip()]


def rec(org, role, honor='', name_cn='', name_en='', member_org='', job='', company='',
        source='', layer='L1'):
    return dict(org=org, role=role, honor=honor, name_cn=name_cn, name_en=name_en,
                member_org=member_org, job=job, company=company,
                address='', mobile='', tel='', home='', fax='', email='', website='',
                source=source, layer=layer)


def load(slug):
    return [clean(x) for x in
            io.open('_raw/cc/txt/%s.txt' % slug, encoding='utf-8', errors='ignore')
            .read().split('\n')]


def region(L, start, end, occ=1):
    a, n = 0, 0
    for i, x in enumerate(L):
        if start in x:
            n += 1
            if n == occ:
                a = i
                break
    b = next((i for i in range(a + 1, len(L)) if end and end in L[i]), len(L))
    return L[a:b]


def p_role_first(L, org, src):
    rows, role, group, i = [], '', '', 0
    while i < len(L):
        s = re.sub(r'[\s:：]+$', '', L[i])
        if s in ('：', ':', ''):
            i += 1
            continue
        # 「主任     ： 蔡常辉」职务与姓名同行
        if '：' in s or ':' in s:
            head, tail = re.split(r'[：:]', s, 1)
            head = head.strip()
            if is_role(head):
                role = (group + ' ' + head) if (group and re.search(r'(主任|委员|组长)$', head)
                                                and not group.endswith(head)) else head
                for x in split_multi(tail):
                    if is_name(x):
                        hon, nm = split_name(x)
                        rows.append(rec(org, role, hon, nm, source=src))
                i += 1
                continue
        if is_role(s):
            # 只有小组职务才带分组前缀；会长/董事/顾问之类不加
            sub = re.search(r'(主任|委员|组长)$', s)
            role = (group + ' ' + s) if (group and sub and not group.endswith(s)) else s
            i += 1
            continue
        # 分组标题（会务组 / 财务、资产投资与管理委员会 / 青商团）
        if GROUP.search(s) and 2 < len(s) <= 24 and not is_name(s):
            group = s
            i += 1
            continue
        # 姓名行（可能多人）
        names = split_multi(s)
        if role and names and all(is_name(x) for x in names):
            for x in names:
                hon, nm = split_name(x)
                rows.append(rec(org, role, hon, nm, source=src))
            i += 1
            # 紧随的所属团体行
            if i < len(L) and ORG.search(L[i]) and not is_name(L[i]) and not is_role(L[i]):
                for r in rows[-len(names):]:
                    r['member_org'] = L[i]
                i += 1
            continue
        i += 1
    return rows


def p_name_first(L, org, src):
    rows = []
    for i in range(len(L) - 1):
        s = re.sub(r'[\s:：]+$', '', L[i])
        nxt = re.sub(r'[\s:：]+$', '', L[i + 1])
        if is_role(nxt) and is_name(s):
            hon, nm = split_name(s)
            rows.append(rec(org, nxt, hon, nm, source=src))
    return rows


def p_en_pair(L, org, src):
    rows, role_en, role_cn, pend = [], '', '', []
    for s in L:
        if not s:
            continue
        if is_role(s):
            role_cn = s
            pend = []
            continue
        if ROLE_EN.search(s) and len(s) <= 60 and not re.search(r"^(Mr|Ms|Dato|Datuk|Tan Sri)", s, re.I):
            role_en = s
            pend = []
            continue
        if CJK_NAME.match(split_name(s)[1]):
            hon, nm = split_name(s)
            en = ' '.join(pend).strip()
            pend = []
            rows.append(rec(org, (role_cn or role_en), hon, nm, en, source=src))
            continue
        if re.match(r"^[A-Za-z][A-Za-z'\.\,\s\-\u2019\u2018]{1,60}$", s) and not ORG.search(s):
            pend.append(s)
    return rows


def p_en_role(L, org, src):
    rows, role, pend, comp = [], '', [], ''
    for s in L:
        if not s:
            continue
        if ROLE_EN.search(s) and len(s) <= 60:
            role = s
            pend = []
            continue
        if PREFIX_EN.match(s):
            pend.append(s)
            continue
        if re.match(r"^[A-Z][A-Za-z'\.\,\s\-\u2019\u2018]{2,60}$", s) and not ORG.search(s):
            name = ' '.join(pend + [s]).strip()
            pend = []
            rows.append(rec(org, role, name_en=name, source=src))
            continue
        if ORG.search(s) and rows and not rows[-1]['company']:
            rows[-1]['company'] = s
            continue
        pend = []
    return rows


def p_name_job_company(L, org, src):
    """姓名 → 本职 → 公司，三行一组"""
    rows, i = [], 0
    while i < len(L) - 2:
        if is_name(L[i]) and not is_name(L[i + 1]) and ORG.search(L[i + 2] or ''):
            hon, nm = split_name(L[i])
            r = rec(org, '', hon, nm, source=src)
            r['job'] = L[i + 1]
            r['company'] = L[i + 2]
            rows.append(r)
            i += 3
        else:
            i += 1
    return rows


# ---------- 英文名 / 公司成对（FMM、REHDA） ----------
TITLE_EN = re.compile(r"^(Mr|Ms|Mrs|Mdm|Dr|Dato'?|Dato'? Sri|Dato'? Seri|Datuk|Tan Sri|"
                      r"Y Bhg|Encik|En\b|Puan|Tuan|Professor|Prof|Ir|Ts|Capt|Hj|Hjh|"
                      r"Datin|Puan Sri|Senator|YB|Adjunct)", re.I)
CO_SUF = re.compile(r'(Sdn\.?\s*Bhd|Berhad|Bhd|Sendirian|Enterprise|Holdings|Group|'
                    r'Corporation|Company|S/B|&\s*Associates|University|Bank|'
                    r'Sdn|Pte|Ltd)', re.I)
ROLE_HEAD = re.compile(r'(Members?|Chairperson|Chairman|Representative|President|'
                       r'Committee|Council|Officer|Secretary|Treasurer|Advisor|'
                       r'Ex-?Officio|Deputy|Vice)', re.I)


def p_en_pairs(L, org, src):
    """姓名行 + 公司行交替出现；职务取自最近的标题行"""
    rows, role, i = [], '', 0
    while i < len(L) - 1:
        a, b = L[i], L[i + 1]
        if ROLE_HEAD.search(a) and len(a) <= 70 and not CO_SUF.search(a) \
                and not TITLE_EN.match(a):
            role = a
            i += 1
            continue
        if TITLE_EN.match(a) and CO_SUF.search(b or ''):
            rows.append(rec(org, role, name_en=a.strip(), company=b.strip(), source=src))
            i += 2
            continue
        # 无称谓前缀的英文姓名：2~5 个首字母大写单词，且下一行是公司
        if re.fullmatch(r"[A-Z][A-Za-z'\.\-]+(\s+[A-Z][A-Za-z'\.\-]*){1,4}", a or '') \
                and CO_SUF.search(b or '') and not TITLE_EN.match(a):
            rows.append(rec(org, role, name_en=a.strip(), company=b.strip(), source=src))
            i += 2
            continue
        i += 1
    return rows


SRC = [
    ('cccbp_board', '峇株巴辖中华总商会 CCCBP', 'role_first', '现任董事名录', '当前活动'),
    ('cccbp_youth', '峇株巴辖中华总商会 青商团', 'role_first', '青商团现任理事', '当前活动', 2),
    ('cccbp_honor', '峇株巴辖中华总商会 名誉董事', 'role_first', '名誉会长、名誉董事名录', '当前活动', 2),
    ('dz_central', '马来西亚华校董事联合会总会 董总 中央委员会', 'role_first', '第33届', 'Facebook'),
    ('dz_exco', '马来西亚华校董事联合会总会 董总 中央常务委员会', 'role_first', '第33届', 'Facebook'),
    ('dz_work', '马来西亚华校董事联合会总会 董总 工作委员会', 'role_first', '各工作委员会', 'Facebook'),
    ('acccim_comm', '马来西亚中华总商会 ACCCIM 工作组', 'role_first', '会务组', 'Copyright'),
    ('acccim_honor', '马来西亚中华总商会 ACCCIM 名誉会长', 'name_job_company', '中总名誉会长', 'Privacy'),
    ('ns_board1', '森美兰中华总商会 NSCCCI', 'name_first', '第38届', '下一页'),
    ('ns_board2', '森美兰中华总商会 NSCCCI 各组主任', 'name_first', '第38届', '上一页'),
    ('ns_youth2', '森美兰中华总商会 青商团', 'name_first', '第6届', '下一页'),
    ('tccci_board', '登嘉楼中华总商会 TCCCI', 'en_pair', '第37届', '中总和各基本会员'),
    ('pg_committee', '槟城中华总商会 PCCC', 'en_role', 'GENERAL COMMITTEE 2024', 'About Us', 2),
    ('mrca_council', '马来西亚连锁协会 MRCA', 'en_role', 'MRCA Council Members', 'CONTACT'),
    ('klscah_list', '吉隆坡暨雪兰莪中华大会堂 隆雪华堂', 'role_first', '董事', '历任会长'),
    ('kt_board', '柔佛州中华总商会 哥打丁宜属会', 'role_first', '名誉会长', 'COPYRIGHT'),
    ('pcth_comm', '槟州华人大会堂 PCTH 其他委员会', 'role_first', '其他委员会', 'Copyright', 2),
    ('tccci_div', '登嘉楼中华总商会 TCCCI 小组名表', 'role_first', '第36届', '中总和各基本会员'),
    ('dz_micss_all', '董教总华文独中工委会', 'role_first', '全体委员会', 'Facebook'),
    ('dz_micss_exco', '董教总华文独中工委会 常务委员会', 'role_first', '第', 'Facebook'),
    ('fmm_council', '马来西亚厂商联合会 FMM', 'en_pairs', 'FMM Council for', ''),
    ('fmm_advisory', '马来西亚厂商联合会 FMM 顾问会', 'en_role', 'FMM Advisory Council', ''),
    ('rehda_about', 'REHDA 马来西亚房地产发展商会', 'en_pairs', 'Branch Chairperson', ''),
]

FUNC = dict(role_first=p_role_first, name_first=p_name_first, en_pair=p_en_pair,
            en_role=p_en_role, name_job_company=p_name_job_company,
            en_pairs=p_en_pairs)


def main():
    all_rows = []
    for cfg in SRC:
        slug, org, layout, s, e = cfg[:5]
        occ = cfg[5] if len(cfg) > 5 else 1
        L = region(load(slug), s, e, occ)
        rows = FUNC[layout](L, org, '%s.txt' % slug)
        all_rows += rows
        print('%-16s %-4s %3d' % (slug, layout[:4], len(rows)))

    # 同一组织内去重（同名同职务）
    seen, out = set(), []
    for r in all_rows:
        k = (r['org'], r['name_cn'] or r['name_en'], r['role'])
        if k in seen:
            continue
        seen.add(k)
        out.append(r)

    with open(OUT, 'w', encoding='utf-8') as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    print('\n合计 %d 人（去重前 %d）' % (len(out), len(all_rows)))
    print('  有英文名 %d' % sum(1 for r in out if r['name_en']))
    print('  有职务   %d' % sum(1 for r in out if r['role']))
    from collections import Counter
    for o, c in Counter(r['org'] for r in out).most_common():
        print('   %-40s %d' % (o, c))


if __name__ == '__main__':
    main()
