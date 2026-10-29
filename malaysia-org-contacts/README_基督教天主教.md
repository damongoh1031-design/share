# 马来西亚 基督教 / 天主教 团体通讯录 — 数据说明

## 一句话

用采集佛教/德教会那套三层管线做的教会版：**天主教九个教区的堂区**（官网逐条解析，含本堂神父姓名）+ **新教宗派总部与堂会** + **Facebook 上的华人独立教会（含「恩典」系列）**。每条记录带 `source_url`，电话统一 `+60` 格式。

## 规模

- **216 条记录**：天主教堂 134 / 基督教堂 67 / 天主教团体 9 / 基督教团体 6
- 有座机 113、有手机 18、有电邮 112、有官网或 FB 80、**有本堂神父/牧者姓名 80**
- 州属前三：雪兰莪 36、沙巴 35、砂拉越 26
- FB 层：78 个专页 / 399 张图 / OCR 命中 17 张海报（含手机 8 张）/ 20 个去重号码

## 交付物

| 文件 | 内容 |
|---|---|
| `马来西亚基督教天主教团体通讯录_2026-10-29.xlsx` | 主交付，9 个工作表 |
| `contacts_chr.csv` | 同总表，UTF-8-BOM |
| `contacts_chr.jsonl` | 一行一记录 |
| `poster_hits_chr.csv` | 海报图命中索引（教会版） |
| `海报证据_基督.zip` | 命中海报原图，按教会分目录 |
| `基督教天主教采集报告_2026-10-29.md` | 做法、结果、限制 |
| `seed_chr.json` | 手工核对的全国性机构（宗派总部） |

### 工作表

说明 / 总表 / 天主教堂 / 天主教团体 / 基督教堂 / 基督教团体 / 按州统计 / 待补全 / 海报命中 / 手机联络

## 数据来源

### 天主教（L1，质量最好）

| 教区 | 入口 | 拿到的字段 |
|---|---|---|
| 槟城教区 | `pgdiocese.org/parish/<slug>` | 堂区名、地址、电话、电邮、官网、**本堂神父姓名与职务** |
| 马六甲-柔佛教区 | `mjdiocese.my/parish-data.json` | 同上 + 圣堂照片、主保年、牧民议会主席 |
| 吉隆坡总教区 | `archkl.org/<区>-district`（8 个区） | 堂区名、地址、电话、电邮 |
| 山打根教区 | `dioceseofsandakan.org/parish/` | 堂区名、地址、电话、传真、电邮、**主任司铎** |
| 亚庇总教区 | `catholicadkk.org/directory/parish-communities/` | 堂区名 + 神父名单（**无电话**） |
| 古晋总教区 | `kuchingcatholic.org/directories/parishes/` | 堂区名（**无电话**） |
| 诗巫 / 美里 / 根地咬 | 官网无结构化名录 | 只收教区总部条目 |

### 新教（L1 总部 + L3 堂会）

- 神召会总议会 `ag.org.my`、救世军 `salvationarmy.org.my`、巴色会 `bccm.org.my`、卫理公会华人年议会 `methodist.org.my`
- 卫理公会 TRAC `trac.org.my` 的「Find a Church」→ 31 间堂会（州属 + 崇拜语言，**详情页无电话**）
- 真耶稣教会、浸信会、长老会、安息日会、圣公会的马来西亚官网**从本机不可达**（连接超时/502，Chrome 直连同样失败），这些宗派只能靠 FB 层补

### Facebook（L3）

63 条中文查询 × 登录态 `/search/pages/` → 145 个专页 → 剔除德教会/佛教会/殡葬/书店/电视台 + 台湾香港新加坡日本菲律宾的教会 → 78 个进采集。教会海报（布道会、圣诞晚会、儿童营、主日学招生）底部常印「报名：01x-xxxx xxx」，是手机号的主要来源。

## 字段口径

- `category`：天主教堂 / 天主教团体 / 基督教堂 / 基督教团体
- `tradition`：天主教 / 卫理公会 / 神召会 / 信义会(巴色会) / 救世军 / 跨宗派
- `leader_name` / `leader_title`：官网公开列出的本堂神父、主任牧师、教区长；FB 专页不写牧者姓名，留空不推断
- `phone_mobile_src`：`FB专页资料栏` / `海报图OCR`
- `confidence`：已核实(官网) > 已核实(FB专页) > 仅地址/名录

## 边界

1. 只收组织自己公布的联络方式（官网、专页资料栏、海报），不抓个人档案、不推断身份。
2. 号码一律过区号校验：手机 01x 且 9–10 位；座机 3→9 位、4/5/6/7/9→8 位、082–089→8 位。
3. 州属先按地址里的州名判，再按邮编区间兜底（78000 Tampin 属森美兰而非马六甲，这类边界已修正）。

## 已知缺口

| 缺口 | 影响 | 补法 |
|---|---|---|
| 亚庇 23 / 古晋 18 个堂区无电话 | 东马天主教联系不上 | 查《Catholic Directory of Malaysia》纸本 |
| 卫理公会堂会只到名字级 | CAC/TRAC 的堂会电话拿不到 | 年议会 Yearbook |
| 真耶稣教会/浸信会/长老会/安息日会/圣公会 官网不可达 | 这些宗派覆盖低 | 换网络环境重试，或走 FB 层 |
| 「恩典」系列独立教会覆盖不全 | FB 搜索被台湾香港结果稀释 | 按州逐个确认，或用地名+教会名组合搜 |

## 复跑

```bash
cd _tools
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"
NODE="C:/Users/Admin/.workbuddy-ai/binaries/node/versions/22.22.2-6/node.exe"
export NODE_PATH="C:/Users/Admin/.workbuddy-ai/binaries/node/workspace/node_modules"

"$PY" chr_crawl.py all
"$NODE" fb_search_chr.js ../_raw/chr_queries.txt ../_raw/fb_chr_found.csv
"$NODE" fb_harvest3.js ../_raw/chr_pages_todo.txt ../_raw/fb_chr 5 10
"$PY" ocr_inc.py ../_raw/fb_chr
"$PY" ocr_pass2.py
"$PY" chr_curate.py
"$PY" chr_build.py
"$PY" chr_xlsx.py
```
