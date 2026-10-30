---
name: org-directory-harvest
description: 从协会/总会/教区官网的名录页与 Facebook 登录态中批量采集团体（寺庙、德教会、宗教团体、青年组织、文化体育团体）的联络方式，产出多表 xlsx 通讯录 + 海报取证包。触发词：通讯录、联系方式汇总、批量抓电话、会员团体名录、海报 OCR 取手机号、FB 登录态采集、directory harvest、org contacts。适用于「按州属分页的会员名录」「职位-姓名表格 + 通讯处」这类站点结构。
agent_created: true
---

# 团体通讯录批量采集

## 这个技能解决什么

给定一个领域（寺庙、德教会、基督教会、青年团体、舞狮团……）和一个国家/地区，
批量产出「机构名 + 州属 + 地址 + 座机 + 手机 + 电邮 + 官网/FB + 负责人姓名职务」的
多表 xlsx，并对「电话只印在海报图片里」的情况做 OCR 取证。

已验证场景：马来西亚华人社团体系（佛总 288 会员团体 / 青运 280 支会 / 青团运 153 理事 /
基督教会 / 德教会 / 龙狮武术团体），单轮可稳定产出 200–450 条可用记录。

## 核心原则：四层数据模型

**不要一上来就抓 Facebook。** 按可靠性分四层，先拿稳的，再补漏的，每条记录标 `layer`。

| 层 | 来源 | 可得字段 | 命中率 | 备注 |
|---|---|---|---|---|
| L1 | 协会官网名录页 | 全字段 + 负责人 | 最高 | 一次拿几百条，优先榨干 |
| L2 | 目录站 / 维基 / 黄页 | 名称、地址、座机 | 中 | 常有错行、过期 |
| L3 | Facebook 主页 + 海报 OCR | 手机、电邮、活动联系人 | 中低但**不可替代** | 唯一能拿到手机的层 |
| L4 | 只有名称/地址 | 待补全 | — | 明确标注，不要伪造 |

**关键判断：座机大面积停用，手机才是实际联络方式。** 但手机几乎只出现在
Facebook 帖子配图里，所以 L3 + OCR 不是锦上添花，而是整个任务的价值所在。

## 标准流程

### 第 1 步 摸清站点结构（30 分钟，决定后面 8 小时）

按顺序试这四个入口，命中即停：

```bash
# 1) WordPress REST：能直接列出所有内容类型和条目数
curl -s https://<domain>/wp-json/wp/v2/types
#    看到 tribe_organizer / tribe_venue / post_grid 说明是 The Events Calendar

# 2) sitemap：列出所有页面，从中反推目录页 URL 规律
curl -s https://<domain>/wp-sitemap-posts-page-1.xml | grep -o '<loc>[^<]*</loc>'
curl -s https://<domain>/sitemap_index.xml

# 3) 首页导航里的「组织 / 会员 / 分会 / 属会 / 委员会」
# 4) 直接搜 site:<domain> 会员团体
```

从 sitemap 拿到 151 个页面 URL 后，**看 URL 规律而不是看内容**——
`/关于/组织/会员团体/雪兰莪/` 这种就是分页目录，把州名替换成 12 个州批量拉。

### 第 2 步 写 L1 采集器

参照 `scripts/` 下同类实现，套用固定骨架：

```python
def rec(**kw): ...        # 统一字段，缺省空串
def save(rows, name): ... # 同时写 jsonl + csv(utf-8-sig)
```

**名录页两种典型结构，解析方式完全不同：**

- **块状列表**（会员团体名录）：整页 `innerText` 按行切，用
  `会员号码/地址/联络电话/传真/电子邮箱/网站` 这些标签定位每条的起止。
  陷阱见 `references/pitfalls.md` 的「块尾串到下一条」。
- **表格**（理事/委员会名单）：`职位` 后跟 `姓名`，常配 `通讯处 / 联络人 / 电子邮箱 / 面子书`。
  必须先剥掉导航区，从第一个职位词开始切。

### 第 3 步 电话号码归一化（务必用脚本，不要手写正则）

```bash
python scripts/my_phone.py            # 自测，全绿再往下走
```

规则：手机 `01x` 9–10 位；座机 `3` 开头 9 位、`4/5/6/7/9` 开头 8 位、`082–089` 8 位。
统一输出 `+60 3-7804 9154` / `+60 18-255 5867`。**号码不合法就丢弃**，宁可少一条也不要错号。

### 第 4 步 Facebook 登录态采集（拿手机的唯一途径）

**必须先有登录 cookie。** 登出态只有 590px 缩略图，改写 CDN 的 `stp/ctp` 参数会返回
22 字节 `URL signature mismatch`——这条路走不通，别浪费时间。

```bash
# 1) 搜索：多查询 -> 去重 -> 规则过滤
node scripts/fb_search.js queries.txt fb_found.csv rules.json _raw/fb_cookies.json

# 2) 采集：正文 + 手机/电邮 + 帖子大图（按图片 ID 去重取最大尺寸）
node scripts/fb_harvest.js urls.txt _raw/fb_out 8 26 _raw/fb_cookies.json
```

`rules.json` 三档：`keep`（命中才留）/ `drop`（命中即剔）/ `exclude`（硬排除，
例如 `伊斯兰|清真|masjid|surau`）。**中文关键词污染极重**——
搜「基督教会」会大量返回台湾/香港/新加坡/巴黎/美国页面，必须加地理闸门。

### 第 5 步 海报 OCR（本地离线，不上传）

```bash
python scripts/ocr_inc.py _raw/fb_out --cache _raw/ocr_cache.jsonl
python scripts/curate_posters.py --slugmap _raw/slug_map.json --out 海报证据 \
    --exclude "伊斯兰|清真|masjid"
```

- 用 `rapidocr-onnxruntime`，中英混排远好于 tesseract。
- 以 **sha1** 做缓存键，跨项目复用；`org_slug` = 相对路径第一段，
  所以图片必须按 `<slug>/<img>.jpg` 组织。
- 增量：图片还没采完就先跑一遍，采完再跑，缓存会自动补齐。
- 取证包只收「识别出合法号码 + 有联络字样或 01x 手机 + slug 已在通讯录里」的图。

### 第 6 步 合并去重 + 分类

**这一步最容易做错，做错了整份名录就废了。** 直接用 `scripts/org_match.py`，
不要自己写名称匹配：

```python
from org_match import simp, similar, same_org, dedup, merge_place_branches, is_foreign

orgs = [o for o in orgs if not is_foreign(o['org'], emails, websites)]  # 先剔境外
orgs = merge_place_branches(orgs)     # 「…笨珍属会」↔「笨珍中华总商会」
orgs = dedup(orgs)                    # 中英文重复条目合并，号码不丢
```

铁律（详见 `references/pitfalls.md` 第 16–24 条）：

1. **搜索关键词只能用来发现页面，绝不能用来判定身份。**
   `qmap[slug] = idx[query]` 会把用宽泛词搜到的地方商会全部并进全国总会。
2. **缩写相同 ≠ 同一机构**（吉打 / 吉兰丹中总都叫 KCCCI）。
3. **母会与分会 / 属会 / 青商团 / 妇女组 一律独立成条。**
4. **境外同名机构极多**（Guam、Mauritius、Tampa Bay 的中国商会），
   优先按邮箱域名与官网 TLD 剔除，比按名字可靠。
5. **繁体先转简体**再分类、再比对。

其余规则：

- 分类用**带否定的正则**，见 `references/pitfalls.md` 的分类陷阱表。
  注意「中华总商会」里含「华总」二字，商会判定必须排在华总之前。
- 州属推断顺序：地址里的英文州名 → 城市/地名提示 → **最后一个** 5 位邮编；
  最后再把 `Johor/Penang/…` 之类的英文写法统一成中文州名。
- 每条记录标 `layer`（L1/L2/L3/L4）和 `source`，方便回溯。

### 第 7 步 出 xlsx

至少 8 个表：`说明` / `总表` / 按类别分表 / `按州统计` / `负责人名录` /
`待补全` / `海报命中` / `手机联络`。用 `openpyxl`，冻结首行、自动列宽、说明页写清
数据来源与免责声明。

### 第 8 步 同步 GitHub

**只用逐文件模式，禁止目录模式。** 见 `references/pitfalls.md` 的
「github-sync 目录模式会删远端文件」。

```bash
# 先 dry-run 确认 deletions=0
python <github-sync>/sync.py --repo <repo> --src <f> --dest <path>/<f> --dry-run
```

## 脚本清单

| 文件 | 作用 | 关键参数 |
|---|---|---|
| `scripts/my_phone.py` | 马来西亚号码归一化/校验 + 州属推断 | 直接运行即自测 |
| `scripts/org_match.py` | **机构名归一 / 相似度 / 去重 / 分支归并** | `python org_match.py` 自测；也可 `import` |
| `scripts/fb_search.js` | 登录态搜主页，按规则过滤 | `queries.txt out.csv rules.json cookies.json` |
| `scripts/fb_harvest.js` | 登录态采正文/电话/大图 | `urls.txt outdir [scroll] [maxImg] [cookies]` |
| `scripts/ocr_inc.py` | 增量离线 OCR | `<imgdir> --cache --max` |
| `scripts/curate_posters.py` | 海报证据包 + CSV | `--slugmap --out --exclude` |

依赖：`playwright`（用系统 Chrome）、`rapidocr-onnxruntime`、`openpyxl`、`requests`。

现成规则文件（直接传给 `fb_search.js` 第 3 个参数，按需增删）：

| 文件 | 适用 |
|---|---|
| `assets/rules-temple.json` | 寺庙 / 德教会 / 佛教团体 |
| `assets/rules-christian.json` | 基督 / 天主 / 福音 / 恩典 |
| `assets/rules-youth.json` | 青年团体（佛道+基督，排除伊斯兰，含文化/兴趣） |

`cookies.json` 格式（Chrome 登录 facebook.com → F12 → Application → Cookies →
右键 Copy all as JSON，确保每条有 `name` / `value` / `domain=".facebook.com"` / `path="/"`）：

```json
[{"name":"c_user","value":"1000...","domain":".facebook.com","path":"/","secure":true},
 {"name":"xs","value":"...","domain":".facebook.com","path":"/","secure":true},
 {"name":"datr","value":"...","domain":".facebook.com","path":"/","secure":true}]
```

## 交付前自检

- [ ] 号码全部过 `my_phone.py`，无 8 位以下、无 `+60 0` 开头
- [ ] 每条记录有 `layer` 和 `source`
- [ ] 州属无「雪隆」「沙闽」这类非标准写法（映射到雪兰莪/沙巴）
- [ ] 分类抽查 20 条，重点看「柔佛」「布道处」「狮子会」有没有错分
- [ ] 排除项（如伊斯兰团体）在搜索层和合并层**双重**拦截
- [ ] xlsx 说明页写明采集日期、来源层级、未核实项
- [ ] GitHub 同步 `deletions=0`

## 参考

- `references/pitfalls.md` — 十几个真实踩坑与修法（**动手前必读**）
- `references/site-patterns.md` — 站点结构识别与解析套路
