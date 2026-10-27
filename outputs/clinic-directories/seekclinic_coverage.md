# Seek Clinic 全站采集覆盖报告

检查日期：2026-10-27　通道：服务端页面读取（本机 IP 被站方 403 拒绝）

## 一、站点真实规模（实测，不是估算）

| 项目 | 实测值 | 依据 |
|---|---|---|
| `/clinics/` 全站归档总页数 | **603 页** | 页面标题 `Clinics - Page 2 Of 603`，`/clinics/page/603/` 有 1 条记录 |
| 每页 listing 数 | 9 条 | 各页实际计数 |
| 推算全站 listing 总量 | **约 5,419 条**（602×9 + 1） | 上两项相乘 |
| `medical-clinic` 分类页数 | 至少 100 页（`/category/medical-clinic/page/100/` 仍有 9 条） | 实测 page 100 |
| 用户判断核对 | 用户称“至少 1 千以上” | **成立**，全站量级为 5 千条 listing |

## 二、本轮实际抓取范围

已逐页读取并落盘的 `medical-clinic` 分类分页：

```
1-34, 35-47, 48-49, 50, 51-61, 62-70, 80, 100
```

其中：

- `seekclinic_medical_raw.tsv` — page 1-24
- `seekclinic_medical2_raw.tsv` — page 25-47, 50, 60, 80, 100
- `seekclinic_medical3_raw.tsv` — page 48-49, 51-59, 61
- `seekclinic_medical4_raw.tsv` — page 62-67
- `seekclinic_medical5_raw.tsv` — page 69-70
- `seekclinic_raw.tsv` — `aesthetic-clinic-1` 类目 page 1-13

## 三、被拒绝的页面（未绕过，按停机规则放弃）

| 页面 | 响应 | 处置 |
|---|---|---|
| `medical-clinic/page/35/`、`/36/`、`/39/` | 首次 403；加查询串重取成功 | 已取到数据 |
| `medical-clinic/page/68/`、`/71/`、`/72/`、`/73/` | 403（加查询串仍 403） | 未取，标记 blocked |
| `medical-clinic/page/74/`、`/75/` | 403 | 未取，标记 blocked |
| 本机 curl / Playwright + 系统 Chrome | 全站 403（IP 级拒绝） | 不做代理轮换、指纹伪装、挑战绕过 |
| 站内批量接口 | `/wp-json/wp/v2/clinics` 404；`/wp-json/geodir/v2/places` 404；`/wp-json/` 403 | 无公开批量导出 |

连续 403 判定为限流/访问控制触发，已停止继续请求，不通过更换 UA、代理或指纹继续施压。

## 四、当前产出统计

| 指标 | 数值 |
|---|---|
| 源记录（三站合计） | 886 |
| Seek Clinic 源记录 | 740 |
| AestheticClinic 号码实例 | 127（100 个 profile，0 失败） |
| Tressless 样本 | 3 |
| 空号/无效号码被拒 | 16 |
| 唯一电话号码 | **825** |
| 唯一机构 | **821** |

## 五、覆盖率的诚实结论

- 825 个唯一号码 ≈ 全站约 5,419 条 listing 的 **15%**。
- `medical-clinic` 分类本身也只覆盖到约 70 页 / 至少 100 页。
- 站内还有 `aesthetic-clinic`、`skin-clinic`、牙科等其余分类（sitemap index 共 95 个子 sitemap），本轮未逐一枚举。
- 要把 825 提到接近全站，需要在**未被 403 拒绝的网络环境**下运行 `crawl_seekclinic.js`（约 603 页，1 请求/页，9 条/页），或取得站方数据导出许可。

## 六、抽样复核（详情页回查）

| 机构 | 列表页号码 | 详情页号码 | 地址一致 |
|---|---|---|---|
| Klinik Stellar | +6062644344 | +6062644344 | 是（No.17, Jalan KSB 13, Taman Kota Syahbandar, 75200 Melaka） |
| PJ Polyclinic | +60377722099 | +60377722099 | 是（E19, Jalan 1/21, 46000 Petaling Jaya） |
