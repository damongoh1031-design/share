# 站点结构识别与解析套路

## A. 先判断站点类型

| 特征 | 站点类型 | 首选打法 |
|---|---|---|
| `/wp-json/wp/v2/types` 返回 JSON | WordPress | REST API 直接列条目 |
| `wp-sitemap-posts-page-1.xml` 有内容 | WordPress 5.5+ | sitemap 反推目录页规律 |
| `/sitemap_index.xml` 有 `tribe_` 前缀 | The Events Calendar | `/wp-json/tribe/events/v1/organizers` |
| 页面 URL 含 `?page_id=` / `?p=` | 老 WordPress | 只能按 sitemap 抓 |
| 表格 `<table>` 里是机构名 | 传统 CMS | 直接 `pd.read_html` |
| 内容要滚动才出现 | SPA / 无限滚动 | Playwright + 等选择器 |

## B. 三个必试的发现入口

```bash
# 1. 内容类型与条目数（最快的摸底）
curl -s https://<domain>/wp-json/wp/v2/types | python -m json.tool | head -60

# 2. 所有页面 URL（看规律，不看内容）
curl -s https://<domain>/wp-sitemap-posts-page-1.xml \
  | grep -o '<loc>[^<]*</loc>' | sed 's/<[^>]*>//g' | head -60

# 3. 分类法（州属/类别常做成 taxonomy）
curl -s https://<domain>/wp-json/wp/v2/categories?per_page=100
```

**核心技巧**：拿到 100+ 个 URL 后，用肉眼找重复片段。
`/关于/组织/会员团体/雪兰莪/`、`/关于/组织/会员团体/槟城/` … 说明有 12 个州的分页，
把州名换成列表批量拉，一次拿到几百条。**这比写通用爬虫快一个数量级。**

## C. 名录页的两种结构

### C-1 块状列表（会员名录）

```
A001 | 某某佛教会
地址：No.9, Jalan ..., 47301 Petaling Jaya, Selangor
联络电话：03-7804 9154
传真：03-7804 9155
电子邮箱：info@xxx.org.my
网站：https://xxx.org.my
B002 | 另一家佛教会
...
```

解析步骤：

1. `body = page.inner_text('body')`，`lines = [l.strip() for l in body.split('\n') if l.strip()]`
2. 找出所有「会员号码」行（`^[A-Z]\d{3}\s*\|`）作为块起点
3. 每块内按标签 `地址 / 联络电话 / 传真 / 电子邮箱 / 网站` 二次切分
4. **块尾回退一行**（见 pitfalls #3）

### C-2 职位-姓名表格（理事会）

```
职位        姓名
主席        释某某
副主席      陈某某
秘书        林某某
...
通讯处：No.9, Jalan ...
联络人：陈某某
电子邮箱：xxx@xxx.org.my
面子书：https://facebook.com/xxx
```

解析步骤：

1. 找到第一个职位词的下标，**从这里开始切**（前面全是导航）
2. 两两成对：`(职位, 姓名)`，用 ROLE 正则校验职位
3. 姓名二次过滤，剔除含职务词的假人（`卸任主席`、`名誉顾问`）
4. 表格之后的 `标签：值` 段落是机构级联系方式，单独存

## D. 常见字段别名

| 想要 | 站点上可能写成 |
|---|---|
| 机构名 | 名称 / 团体名称 / 属会 / 会员团体 / 分会 / 支会 / 单位 |
| 电话 | 联络电话 / 电话 / 联络号码 / Tel / No. Tel / 电话号码 |
| 手机 | 手提 / 手机 / HP / H/P / 行动电话 / WhatsApp |
| 传真 | 传真 / Fax / No. Fax |
| 电邮 | 电子邮箱 / 电邮 / Email / E-mail / 邮箱 |
| 网站 | 网站 / 网址 / Website / Web / 官方网页 |
| 面子书 | 面子书 / 脸书 / Facebook / FB / 粉丝专页 |
| 负责人 | 主席 / 会长 / 理事长 / 团长 / 主任 / 负责人 / 联络人 / 主持人 |
| 地址 | 地址 / 通讯处 / 会址 / 所在地 / Alamat |

写解析器时把别名做成 `dict[str, tuple[str, ...]]`，一个字段一次扫完，别写十几个 if。

## E. 编码与格式

- 中文站点常见 `charset=gb2312` 但实际是 `utf-8`：`r.encoding = r.apparent_encoding`。
- CSV 一律 `utf-8-sig`（带 BOM），否则 Windows Excel 打开是乱码。
- JSONL 一行一条、`ensure_ascii=False`，便于 `grep` 和增量追加。
- 时间戳统一 ISO 8601，别用本地化格式。

## F. 并发与礼貌

- 同一域名并发 ≤ 3，间隔 ≥ 0.6s。
- 带 `User-Agent`，不要伪装成浏览器去撞 Cloudflare——被拦就换 sitemap 或 REST。
- 单轮最多 200 个请求/域名，超了分批，中间隔 10 分钟。
- 返回 502/503 连续 3 次就放弃该域名，记录到「不可达」清单。

## G. 结果落盘约定

```
_raw/
  <source>_pages.jsonl     # 每页一条原始记录
  <source>/                # 附件（图片/PDF）
  ocr_cache.jsonl          # 全局 OCR 缓存（sha1 键）
  slug_map.json            # slug -> 机构名，供取证包回溯
<最终>_contacts.jsonl      # 合并后
<最终>_contacts.csv        # 合并后（utf-8-sig）
<最终>.xlsx                # 交付物
```

**永远保留 `_raw/`。** 分类规则改了、去重逻辑改了，都要能一键重跑，
而不是重新抓一遍。
