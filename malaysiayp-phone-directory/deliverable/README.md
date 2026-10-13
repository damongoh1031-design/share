# malaysiayp 电话号码目录 · 交付物

导出时间：2026-10-13 15:32:59
数据源：`data/malaysiayp_full.csv.sqlite3`（采集脚本 v3.0.0）

## 一、文件清单

| 文件 | 行数 | 说明 |
|---|---:|---|
| `malaysiayp_all.csv` | 25685 | **主交付**。全部有效记录，含座机与手机 |
| `malaysiayp_mobile.csv` | 4977 | 仅马来西亚手机号（`01X-XXXXXXX` / `011-XXXXXXXX`） |
| `malaysiayp_all_extended.csv` | 25685 | 11 列诊断版，含 `raw_phone` / `phone_status` / `entry_id` |
| `malaysiayp_quarantine.csv` | 1006 | 号码无效或缺失的记录，供人工排查 |
| `meta.json` | — | 行数 / 字节数 / SHA256 / 覆盖度 |

## 二、列定义

| 列 | 说明 |
|---|---|
| `no` | 全局连续序号（1..N），按 `category, company, id` 排序后重编 |
| `company` | 商家名称 |
| `phone` | 归一化号码（纯数字，无分隔符）。手机号 10 或 11 位，座机 8–9 位 |
| `display` | 站点原始展示格式（含空格/连字符），便于人工核对 |
| `category` | 来源分类 slug |
| `address` | 地址（可能为空） |
| `detail_url` | 商家详情页 |
| `source_page` | 抓取该记录的分类列表页 |

## 三、覆盖度（重要）

| 指标 | 值 |
|---|---:|
| 已完成页 / 已入队页 | 1991 / 34347（5.8%） |
| 分类总数 | 1243 |
| 已索引分类 | 1181 |
| 未索引分类 | 62 |
| 估计真实总页数 | 34345 – 37079（中值 35681） |
| **估计真实覆盖率** | **≈ 5.58%** |

> 当前为**阶段快照**，不是终版。采集仍在进行，覆盖率会持续上升。
> 未索引分类尚未展开页数，因此 `pages_queued_known` 会低估总量。

## 四、数据质量

- 号码校验：`_FULL_PHONE_ALL` 正则（`0\d{7,10}` / `1[38]00\d{6,8}`）全量校验，不合格入 `quarantine`
- 去重：DB 层 `UNIQUE(detail_url, phone)`，同公司多号码保留多行
- 公式注入防护：以 `= + - @` 开头的字段加前导撇号（Excel/Sheets 不会执行）
- 编码：UTF-8 **带 BOM**，CRLF 换行，Excel 双击即正常显示中文
- 完整性：每行均含 `company` / `category` / `detail_url` / `source_page`

## 五、使用注意

1. **合规**：数据来源为公开商业目录，含个人数据（公司名+手机号），受马来西亚 PDPA 2010 约束。
   仅限目录检索 / 研究用途；**禁止群发、推销、骚扰、转售**。
2. **手机号列可能为空**：`malaysiayp_all.csv` 保留号码缺失的记录（`phone` 为空），
   需要纯号码清单请用 `malaysiayp_mobile.csv`。
3. **重跑**：数据更新后重新执行 `python export_deliverable.py` 即可覆盖产出。

## 六、更新方式

```bash
# 查看采集进度
python supervise.py --status

# 重新导出最新交付物
python export_deliverable.py
```
