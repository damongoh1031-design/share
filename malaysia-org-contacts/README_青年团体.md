# 马来西亚青年团体通讯录

覆盖宗教（佛道 / 基督，**不含伊斯兰**）、文化（读书会、龙狮、武术、节令鼓、华乐）与兴趣（青运、青团运、运动娱乐）三类青年团体。

## 文件

| 文件 | 内容 |
|---|---|
| `马来西亚青年团体通讯录_2026-10-29.xlsx` | 主交付物，10 个工作表 |
| `contacts_youth.csv` | 全量数据（UTF-8 BOM，Excel 可直接打开） |
| `poster_hits_youth.csv` | 海报取证清单：一图一行，含识别号码与原图路径 |
| `海报证据_青年.zip` | 海报原图，按机构分文件夹 |
| `青年团体采集报告_2026-10-29.md` | 统计与方法说明 |
| `seed_youth.json` | 已人工核实的全国性团体种子数据 |

## 工作簿结构

| 工作表 | 内容 |
|---|---|
| 说明 | 口径、字段、注意事项 |
| 总表 | 全部 442 条 |
| 佛教青年 | 312 条 |
| 基督宗教青年 | 20 条 |
| 文化青年 | 51 条 |
| 兴趣青年 | 57 条 |
| 按州统计 | 州属 × 类别交叉表 |
| 负责人名录 | 346 位理事/负责人的姓名与职务 |
| 青运支会 | 280 个支会名录 |
| 待补全 | 无电话无电邮者 |
| 海报命中 | Facebook 海报取证 |
| 手机联络 | 可用手机直接联络者 |

## 重新生成

```bash
python _tools/youth_crawl.py all      # 官网层
node   _tools/fb_search_youth.js _raw/youth_queries.txt _raw/fb_youth_found.csv
node   _tools/fb_harvest3.js _raw/youth_pages_todo.txt _raw/fb_youth 8 26
python _tools/ocr_inc.py _raw/fb_youth
python _tools/youth_curate.py         # 海报证据包
python _tools/youth_build.py          # 合并
python _tools/youth_xlsx.py           # 工作簿
python _tools/youth_report.py         # 报告
```

## 注意

- 手机号均来自组织自行公布的海报/专页，属对外联络方式；未收录未公开的私人资料。
- OCR 号码有误读风险，重要联络请对照 `海报证据_青年` 原图。
- 伊斯兰相关团体已按要求全部排除。