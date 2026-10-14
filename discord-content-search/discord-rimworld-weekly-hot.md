# RimWorld Discord 一周热门讨论 Digest（2026-10-07 → 10-14）

> 采集方式：CDP 附着本人已登录 Chrome → 对 8 个活跃频道做「时间锚点采样」（每频道每天 ±50 条 around 固定时刻），77 次请求得 **2,707 条**近 7 天消息（去重、去 bot）。热度 = emoji reactions 总数（Discord 最接近社区投票的信号）。样本约占服务器周流量的 5–10%，结论为趋势性而非全量。生成时间：2026-10-14 12:50 (GMT+8)。

## 一、本周三大话题

### 1. 1.7 版本兼容焦虑（技术区最热）
- **CE（Combat Extended）是否支持 1.7** 引发最多担忧：*"does CE seriously not work with 1.7"*（voidtacos）、*"Kinda afraid if 1.7 comes out ce I'll wait for ce to be updated"*（star_fulminage）
- 官方口径：*"1.7 breaks a few big things like prepatcher but overall list should be fine according to the devs"*（alkye）——Prepatcher 被点名将失效
- 手感反馈：*"is it just me or does 1.7's camera feel.... floaty? slow?"*（nattly，1.7 已开放测试）
- Prepatcher vs Harmony 之争再起：*"prepatcher is meant to be a harmony alternative... what is the point of it over harmony?"*（iamtheconor）
- 历史阴影：*"like how 1.6 killed off almost all pathfinding mods"*（aelanna）——每代大版本都伴随模组生态清洗

### 2. 「AI vibecode 下一代 DLC」争议（#general 爆点）
- *"yeah the next DLC is actually being vibe coded"*（oog6638）
- *"If they *did* vibecode it for 1.7, they will need to disclose it once it goes live"*（v_atheron）——社区要求官方披露是否使用 AI 生成代码，若坐实将是本周最大公关事件

### 3. Anomaly DLC 口碑回暖 + 仪式 bug
- *"Who ever said anomaly is bad is wrong"*（star_fulminage，❤️×2）——Anomaly 评价从首发争议转向正面
- Ideology 联动推荐：*"alpha memes is the obvious answer, but there's also Mort's Ideology and the specialist roles for every meme collection"*（waterore）
- 待修 bug：Anomaly 仪式报错 *"the required item is unavailable"*（faintinggoat）

## 二、热议原帖 Top（非图片频道，按 reactions）

| 反应 | 频道 | 时间 | 作者 | 内容 |
|---|---|---|---|---|
| 13 | #colony-sharing | 10-07 | caekdaemon | "逃兵刺杀国王…这辈子头一次"——跑团式殖民地叙事连载 |
| 8 | #colony-sharing | 10-10 | caekdaemon | 王太子册封典礼的全王室描写（家族叙事） |
| 5 | #colony-sharing | 10-11 | moh_de_casio3 | "operation monolith awakening"——核弹就绪、准备撤离星球 |
| 5 | #colony-sharing | 10-07 | jeanulynn | 内环上圈施工进度 |
| 4 | #colony-sharing | 10-09 | adeninebliss | "poverty blimp" |
| 3 | #colony-sharing | 10-07 | seanman06 | "房子围着路修还是路围着房子修？" 城市设计讨论 |
| 3 | #colony-sharing | 10-09 | caekdaemon | 0 电力 comms table 皮肤 + 轨道商人清库存 hack |

→ **#colony-sharing 事实上是本周 reactions 之王**：叙事型殖民日志（而非截图）最受欢迎，caekdaemon 是本周 MVP 讲述者。

## 三、图片频道热度榜（#art / #mod-art，纯 reactions）

1. nguyenanh2132（17 ❤️×8 🔥×5 💖×3）
2. dauntless1942 "Post Apocalypse"（16）
3. cryosphore（16）
4. refrigerator4771 "Doodling a character that totally hasn't been appearing everywhere online"（14，梗图）
5. veanilla 本周多帖上榜（14/10/9×2）
6. redmattis "Rigged up the important stuff for my game"（9）
7. operator_exeles "The Tower of Babel"（9）
8. mod-art: star.echo "i think this looks pretty good in game"（9）

## 四、频道活跃度（样本口径）

| 频道 | 样本消息数 |
|---|---|
| #rimworld | 350 |
| #mod-development | 350 |
| #colony-sharing | 350 |
| #mod-art | 350 |
| #mod-general | 349 |
| #vanilla | 349 |
| #general | 348 |
| #art | 261 |

每日样本量：10-08 起稳定在 ~390 条/日，10-11（周日）峰值 430；10-14 为当天未完整数据。

## 五、模组开发实用信息（#mod-development 沉淀）

- **.NET 版本坑**：krypt_lynx 实测——*.NET Standard 有的方法在 Framework 4.7.2/4.8 缺失*，多模组编译踩坑；kasodus 建议新模组直接迁 .NET 10 并确认 *.net4.8 模组仍可用*
- **学习路径**（qwertaii 推荐）：rimworldwiki.com/wiki/Modding_Tutorials → 反编译游戏/模组源码 → 再上 Harmony v2（harmony.pardeike.net）
- **启动参数机制**（memegoddess）：游戏读 `-mod` 参数的 packageId（`;` 或 `,` 分隔）→ 加入活动列表 → 自动排序
- 全服 "harmony" 提及量 36,023（官方搜索接口实测）——RimWorld 模组生态第一依赖无争议

## 六、复跑方式

```bash
node tools/cdp-discord-weekly.mjs 7 RimWorld          # 默认 7 天、RimWorld 服
node tools/cdp-discord-weekly.mjs 14 RimWorld rimworld,mod-development  # 14 天、指定频道
```
原始数据：`discord-week-raw.json`（2,707 条消息，含 reactions/时间/作者/链接）。

## 局限性

- 采样为每日单时间锚点 ±50 条，若某讨论爆发在未覆盖时段可能漏采（可加密锚点提升覆盖率）
- #moderators 返回 403（无权限），归档频道（mod-updates/ideas-archive）内容稀疏
- reactions 偏向图片帖与老帖沉淀时间差；文本讨论热度可能被低估
