# 三站采集故障恢复矩阵（仅适用于已获准的公开数据采集）

| 故障 | 可识别证据 | 自动动作 | 禁止动作 | 恢复条件 |
|---|---|---|---|---|
| DNS/连接超时 | socket/DNS exception，无 HTTP 状态码 | 最多重试 2 次，指数退避；记录失败 URL；最终停止当前站 | 循环无上限 | DNS/网络恢复后从 checkpoint 续跑 |
| 408/425/5xx | HTTP 临时错误 | 最多 2 次，1s/3s 退避；再失败记录 | 多线程重试风暴 | 服务恢复后续跑 |
| 429 | Rate limit + 可选 Retry-After | 尊重 Retry-After；暂停该 host；超出运行窗口停止 | 加并发、换代理 | 冷却期结束或取得站点速率说明 |
| 401/403 | 拒绝访问；nginx/Cloudflare 页面 | 立即停止该 host，记录状态和响应摘要 | UA/指纹伪装、代理轮换、重放 token | 站点授权、官方 API/导出或管理员解除阻止 |
| HTTP 200 challenge 壳 | title/body 有 One moment / challenge 等标记，目标字段缺失 | 标注 challenge_page，停止后续枚举 | 把 200 当成功；自动解题 | 正常公开通道或书面授权 |
| CAPTCHA / 登录墙 | 页面出现验证码/登录要求 | 停止并人工申请权限 | CAPTCHA solver、cookie 盗取/复用 | 获得账号/书面授权的官方访问方式 |
| robots Disallow | robots 明确禁止目标路径 | 跳过该路径；写入 blocked_by_robots | 改 UA 假装其他 crawler | robots 变更或明确许可（按许可范围） |
| ToS 不明 | 条款缺失、模板页或无法读取 | 标记 `terms_unverified`；限制为少量人工研究 | 擅自宣称已获授权 | 网站书面同意或正式许可 |
| Sitemap 缺失/陈旧 | sitemap 404/内容少于目录明显范围 | 用官方可见索引核对；记录差异；若访问受限则停止 | 猜 URL slug 扫描目录 | 官方索引/API/许可清单 |
| 分页异常/循环 | 页码重复、无新 URL、指向同一页 | 连续两页无新增停止；保留最后有效页 | 无限翻页 | 人工核对分页边界 |
| 页面字段缺失/脏电话 | required fields 缺失/电话占位/长度异常 | 保留原文，质量标记 `missing/invalid`，不造值 | 从其他网站猜测填充 | 官方诊所联系方式交叉验证 |
| 程序中断 | checkpoint 有已处理记录 | 原子写 checkpoint；重启跳过成功记录；失败单独队列 | 清空状态重抓全部 | 人工恢复后续跑 |
| 重复记录 | 同 URL/电话/分店多次出现 | 保留原始行，生成去重视图；品牌共享号标共享 | 把同品牌号码当各门店专线 | 确认分店关系后更新 |

## 本轮实际站点结果（2026-10-27 16:14）

- **AestheticClinic.my**：标准 Chrome UA 下 `robots.txt`、WP sitemap、clinic index 和详情页都返回 HTTP 200 但约 12 KB 的 JS challenge 壳。结果类型识别为 challenge_page；不能按 HTTP 200 判成功。
- **Seek Clinic**：robots、sitemap index、category page 1/2/13/14 全部返回 HTTP 403、548 字节 nginx 页面。是硬拒绝，不重试、不绕过。前序 WebFetch 能读取分页内容，但本地脚本通道不能。
- **Tressless**：robots.txt 公开返回 200、565 字节；sitemap、clinic index、Clinic RX profile 返回 Cloudflare HTTP 403（约 4.9–6 KB）。robots 注释明示 profile challenge gate / archive crawler 阻挡。
- 三站目前都不具备本地普通 HTTP 全站自动采集的可用条件。浏览器 JS 包安装成功但 Chromium 配套下载失败；headless Chrome 在沙箱被终止。更换浏览器执行环境不代表有权绕过 WAF。

## 本地诊断工具

- `check_sites.py`：15 个有界健康检查，每域请求间隔 1 秒；不枚举全站、不解挑战、不重试 403。
- `sitecheck_results.csv`：本轮诊断结果，含 HTTP 状态、页面类型、body hash、耗时、标题。
- `collector_config.json`：已授权采集的保守限频/重试/停机配置。

## 正常状态下的实际全量方案

1. 先拿网站书面许可/API/导出。确认域名、路径、字段、速率、保存和再发布范围。
2. 对获准入口读取 sitemap/category index，保存一份 URL manifest（URL、modified、discovered_at）。
3. 单 host 2 秒一个请求；串行或很低并发；每 25 条 checkpoint；记录响应状态和失败队列。
4. 仅对 408/425/429/5xx 做有限退避；403/401/challenge/CAPTCHA 立刻停该 host。
5. HTML 解析与字段校验分开；保存原始电话、规范化值、来源 URL、抓取时间、质量状态。
6. 对账：manifest 总 URL = 成功 + 失败 + 明确排除；不隐去漏项。
7. 先小样本验收，再扩大范围；公开前再核对条款和仓库可见性。
