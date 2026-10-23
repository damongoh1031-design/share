# Pixel 9 + Eden 游戏运行调研报告

**日期**：2026-10-23  
**设备**：Google Pixel 9（Tensor G4 / Mali-G715 MP7 / 12GB RAM / 无均热板）  
**模拟器**：Eden 0.2.1 稳定版；2026-10 nightly  
**范围**：不限于第一方；重点回答“哪些游戏顺畅”“是否建议 2D”“Atlus 行不行”“Galgame 行不行”  
**合规提醒**：仅使用自己合法 dump 的游戏、固件与 prod.keys；不要下载来路不明的 ROM、APK 或“Mali 驱动包”。

---

## 0. 速览结论

| 问题 | 结论 |
|---|---|
| Pixel 9 能顺畅跑 Eden 吗？ | 能跑，但主要是轻量 2D/独立游戏 + 少量上世代 3D；本世代 3D 大作不要期待顺畅 |
| 建议 2D 游戏吗？ | 建议，而且是最推荐的方向；但要选轻量 2D，避开 HD-2D/重特效 2D |
| Atlus 的游戏可以吗？ | P4G、13 Sentinels 优先试；P5R 勉强；SMT V/Vengeance、Catherine、P5T、P5S 不建议 |
| Galgame 呢？ | 纯 2D 文字冒险大多可行；Fate/Stay Night Remastered 存档崩溃要避开；优先原生 PC/手机版 |

**一句话**：Pixel 9 是一台“2D/独立游戏掌机”，不是“3D 大作模拟器”。

---

## 1. 硬件与软件前提

### 1.1 Pixel 9 的定位

- Tensor G4：1×Cortex-X4 + 3×Cortex-A720 + 4×Cortex-A520。
- GPU：Mali-G715 MP7。
- RAM：12GB；屏幕 6.3" 120Hz。
- 散热：基础版 Pixel 9 **没有均热板**；Pixel 9 Pro / Pro XL 才有。
- Tensor G4 在高负载下可损失约 50% 性能（即使是 Pixel 9 Pro XL 也会明显降频）。

### 1.2 Eden 官方档位

Eden 官方 Android 要求：

- 最低：Snapdragon 865 / Tensor G1 / Exynos 2200 / Dimensity 8200；Adreno 650 / Mali-G78；8GB。
- 推荐：Snapdragon 8 Gen 1 / **Tensor G4** / Exynos 2400 / Dimensity 8400；Adreno 740 / **Mali-G715**；12GB。
- 最佳：Snapdragon 8 Gen 3 / Tensor G5 / Exynos 2400-12 / Dimensity 9400；Adreno 750 / Immortalis-G925 / Xclipse 950 等；16GB。

Pixel 9 正好落在“推荐”档，但“推荐”只代表能跑，不代表所有游戏顺畅。

### 1.3 Mali 的现实

- Android 端 Eden 只支持 Vulkan（无 OpenGL），GPU 需 Vulkan 1.1+。
- Mali **没有 Turnip 这类成熟的社区驱动**；基本只能用系统自带驱动，不能像 Adreno 那样刷驱动。
- 因此 Mali 上常见的纹理闪烁、2D 花屏、黑屏、内存泄漏等问题，很多不是设置能完全解决的。
- 网上流传的第三方“Mali 驱动包”来源不明，不建议安装。

### 1.4 “顺畅”的定义

- **顺畅**：接近 60fps，或稳定在游戏原生上限（如 30fps 游戏稳 30）。
- **可玩**：30fps 左右、偶有掉帧/小瑕疵，但不影响通关。
- **不建议**：低于 30fps、严重花屏、频繁崩溃、存档风险。

---

## 2. 顺畅游戏清单

### 2.1 A 级：优先玩（Pixel 9 系实测接近满帧）

| 游戏 | 类型 | 实测证据 | 备注 |
|---|---|---|---|
| Hades | 动作 Roguelike | Pixel 9a / Citron 0.6.1：60fps | 极适合 |
| Hades 2 | 动作 Roguelike | Pixel 9 Pro XL / Eden 0.0.3：60fps | 用户称“buttery smooth” |
| Hollow Knight | 2D 银河城 | 9a/Citron 60fps；Pro XL/Eden 良好 | 2D 标杆 |
| Metroid Dread | 2D 动作 | Pro XL/Eden 良好 | 偶有掉帧 |
| Cuphead | 2D 跑射 | 9a/Citron 60fps | 其他 Mali 设备有崩溃报告 |
| Rayman Legends | 2D 平台 | 9a/Citron 60fps | 很稳 |
| Shovel Knight | 2D 平台 | 9a/Citron 60fps | 很稳 |
| Hyper Light Drifter | 2D 动作 | 9a/Citron 60fps | 很稳 |
| Katana ZERO | 2D 动作 | 9a/Citron 60fps | 很稳 |
| Balatro | 卡牌 | 9a/Citron 60fps | 很稳 |
| Undertale | RPG | 9a/Citron 30fps | 游戏上限 30 |
| Stardew Valley | 模拟经营 | Pro XL/Eden 良好 | 很稳 |
| Salt and Sacrifice | 2D 魂类 | 9a/Citron 60fps | 很稳 |
| Boomerang Fu | 派对 | 9a/Citron 60fps | 小瑕疵 |
| TowerFall / SpeedRunners / Duck Game / Pool Party / Rogue Heroes / Bread and Fred | 派对/轻量 | 9a/Citron 60fps | 很稳 |

### 2.2 B 级：可玩但不满帧/有瑕疵

| 游戏 | 实测证据 | 注意事项 |
|---|---|---|
| Hollow Knight: Silksong | Pro XL/Eden 良好；Mali-G720 有人锁 30fps | 有存档损坏报告，勤备份 |
| Super Mario Bros. Wonder | 9a/Citron 30fps；9 Pro 用户称“plays well” | 不是 60fps |
| Smash Ultimate | 9a/Citron 约 50fps，小瑕疵 | 早期启动崩溃已在 0.1.x 修复 |
| Mario Kart 8 Deluxe | 9a/Citron 30–60fps + 菜单图形错误；Pixel Tablet 60fps | 设备/版本差异大 |
| Super Mario 3D World | 9a/Citron 60fps 但 major glitches；Pro XL 用户称良好 | 版本差异大，先试 |
| Dark Souls Remastered | 基础版 Pixel 9/Eden Nightly 20–30fps | 部分人地图切换崩溃 |
| Pokemon Diamond | Pro XL/Eden 可玩 | 偶发 10fps 掉帧 |
| 13 Sentinels: Aegis Rim | SD 6 Gen 4 + 0.75x 可玩 | Mali 未直测；战棋/AVG 节奏 |
| Octopath Traveler 1 | 社区轻量推荐 | Pixel 9 未直测 |
| Animal Well / Nine Sols / Monster Sanctuary / Peglin / Cassette Beasts | 社区轻量清单 | Pixel 9 无直测，先试 15 分钟 |
| GRIS / Hotline Miami / To the Moon / The Artful Escape | 社区轻量清单 | 同上 |
| Ori and the Blind Forest | 轻量推荐 | 续作 Will of the Wisps 在 9a 崩溃 |
| Dead Cells | A56/Exynos 60fps | 非 Pixel 9 直测，但负载很低 |

### 2.3 C 级：不建议/避开

| 游戏 | 问题 |
|---|---|
| SMT V / Vengeance | Pixel 9 实测：开场动画后黑屏，只剩 UI/HUD |
| Persona 5 Royal | Mali-G720 约 20–34fps，G715 更低；纹理闪烁；部分设备 30–40 分钟内存泄漏崩溃 |
| Persona 5 Tactica | SD 8 Elite Gen 5 最新 nightly 也随机冻结 |
| Catherine: Full Body | 每几分钟崩溃，且没有自动存档 |
| Persona 5 Strikers | 图形故障，无双负载高 |
| FFT: The Ivalice Chronicles | Pixel 9 Pro 战斗 10–25fps，画面错误 |
| Octopath Traveler II | Pixel 9 实测渲染错位/破碎，调高精度也没修好 |
| DKC: Tropical Freeze | 9a 60fps 但 major graphics glitches |
| TUNIC | 9a 30fps + major glitches |
| Death's Door | 9a 18fps + major glitches |
| Untitled Goose Game | 9a 60fps 但 major glitches |
| BOTW / TOTK | BOTW 9a 15fps、Pro 发热崩溃；TOTK 基础版 9 30fps 但亮度 bug，9a 崩溃 |
| Super Mario Odyssey | 9a 40fps + major glitches |
| Mario Party Superstars / Mario Tennis Aces / Super Mario Party Jamboree | 9a 直接崩溃 |
| Super Mario Galaxy | 启动 RSS 约 8.3GB，Android LMK 随时杀进程，12GB 也不稳 |
| Pokemon Scarlet/Violet / Legends Z-A | 9a / Pro XL 用户报告黑屏 |
| Sword/Shield | 9a 30fps 但 20–30 分钟崩溃、发热严重 |
| New Super Mario Bros. U Deluxe | Pixel 8 / Eden 0.0.4-rc1 起崩溃，0.2.0-rc2 仍有人报告 |
| Fate/Stay Night Remastered | Android 上存档时卡死/崩溃 |

---

## 3. 2D 游戏：建议，而且是最推荐的方向

### 3.1 为什么 2D 适合 Pixel 9

- GPU 负载低，着色器编译少，发热低。
- Mali 的驱动/纹理短板不容易被触发。
- 多数 2D 游戏是 60fps 或 30fps 上限，帧数目标低。
- 很多 2D 游戏有安卓原生版，模拟只是备选。

### 3.2 但“2D ≠ 稳”

- HD-2D / 重特效 2D 反而更吃 GPU：Octopath Traveler II 在 Pixel 9 渲染破碎；FFT 在 Pixel 9 Pro 战斗 10–25fps。
- 2D 也可能引擎瓶颈：Unity 2D、复杂光照、粒子、后处理。
- 2D 也会崩：Cuphead、Sonic Mania、A Short Hike 在部分 Mali 设备有崩溃报告；Hollow Knight 安装更新后掉帧；SD865/Adreno 650 上甚至有“2D 小游戏黑屏、3D 反而能跑”的案例。
- 2D 动作游戏也有存档风险：Silksong 有存档损坏报告。

### 3.3 2D 选游原则

- 优先：像素风、轻量、原生 60fps、无复杂后处理、无大量视频。
- 避开：HD-2D、重特效、Unity 3D 伪 2D、大量 FMV 的“2D”游戏。
- 优先原生安卓版：Hades、Dead Cells、Stardew Valley、GRIS、Balatro 等。
- 先试 15–30 分钟，确认无花屏/崩溃再投入。

### 3.4 2D 推荐清单

- **最稳**：Hades、Hollow Knight、Cuphead、Rayman Legends、Shovel Knight、Hyper Light Drifter、Katana ZERO、Balatro、Undertale、Salt and Sacrifice、Boomerang Fu、TowerFall、SpeedRunners、Duck Game、Pool Party、Rogue Heroes、Bread and Fred。
- **可试**：Animal Well、Nine Sols、Monster Sanctuary、Peglin、Cassette Beasts、GRIS、Hotline Miami、To the Moon、The Artful Escape、Dead Cells、Ori and the Blind Forest、13 Sentinels。
- **慎选**：Octopath Traveler II、FFT、DKC Tropical Freeze、TUNIC、Death's Door、Untitled Goose Game、Ori and the Will of the Wisps。

---

## 4. Atlus 专题

| 游戏 | 结论 | 关键证据 |
|---|---|---|
| Persona 4 Golden | 优先试 | PS2 时代轻量 3D；Eden 可跑；RP6 8 小时后 TV Room 崩溃、相机裁剪、第二屏问题；勤备份 |
| 13 Sentinels: Aegis Rim | 优先试 | Atlus 发行/香草社开发；SD 6 Gen 4 + 0.75x 可玩；Mali 未直测 |
| Persona 5 Royal | 勉强 | Switch 版本身 30fps 目标；Mali-G720 20–34fps，G715 更低；纹理闪烁；部分设备 30–40 分钟内存泄漏崩溃；有 178 小时通关报告（设备未明，不能当作 Mali 证据） |
| Persona 5 Tactica | 观望 | SD 8 Elite Gen 5 最新 nightly 也随机冻结 |
| Persona 5 Strikers | 不建议 | 图形故障，无双负载高 |
| Persona 5 Scramble | 不建议 | PC 兼容表显示 boots/deadlock |
| SMT V / Vengeance | 不建议 | UE4；Pixel 9 实测开场动画后黑屏 |
| SMT III Nocturne HD | 谨慎 | PC 端 Ryubing playable / yuzu Bad；Android/Mali 无实测 |
| Catherine: Full Body | 不建议 | 每几分钟崩溃、无自动存档；Rin 白发纹理 bug |
| Unicorn Overlord | 谨慎 | Odin 2 上 playable；POCO F7 每 10–60 分钟 malloc 崩溃；音频爆音/红黑花屏 |
| Etrian Odyssey HD | 理论适合 | 纯 2D DRPG，负载低；无 Mali 实测，先试 30 分钟 |
| Tokyo Mirage Sessions #FE Encore | 谨慎 | 32-bit + nvdec；PC playable；Android 无实测 |
| Persona 3 Portable | 用 PPSSPP | PSP 移植，PPSSPP 比 Switch 模拟更轻、更稳 |

**Atlus 一句话**：真正适合 Pixel 9 的是 P4G 和 13 Sentinels；P5R 能玩但别指望顺；SMT V、Catherine、P5T、P5S 直接避开。

---

## 5. Galgame 专题

| 作品 | 结论 | 证据/备注 |
|---|---|---|
| Tsukihime Remake | 可试 | S20 FE SD865/Citron “stable-ish”；D8300 Ultra 12GB（Mali-G615）Eden/Yuzu 可跑；约 28–30GB；手机 40°C+ |
| Witch on the Holy Night | 优先 PC | D8300 Ultra 可跑；Steam 有 PC 版 |
| Fate/Stay Night Remastered | 避开 Android 模拟 | Eden/Citron/Ryujinx Android 都有存档卡死/崩溃、文字抖动；Steam 有 PC 版 |
| 13 Sentinels | 可试 | 见 Atlus 表 |
| Ace Attorney Trilogy | 优先原生 | 2D VN；有手机版；Eden 可试 |
| Steins;Gate Elite | 优先原生/PC | nvdec；系列有手机版；注意视频播放 |
| CLANNAD | 优先原生 | 有手机版/可用 Winlator；yuzu 评价 Great，但 Side Stories 是 Bad |
| Danganronpa | 优先原生/PSP | 有 Android/PSP/Vita；Switch 模拟不是最佳路线 |
| Nekopara | 优先原生 | yuzu Vol.1/2 Perfect；Vol.4 有 crash；有手机版 |
| Higurashi / Umineko | 优先 PC | 有 audout/audio 标签；PC 原生更稳 |
| Emio / Famicom Detective Club | 可试 | Switch-only 2D VN；无实测，理论适合；先试 30 分钟 |

### 5.1 Galgame 的 6 个风险

1. **存档崩溃**：FSN Remastered 是明确案例；Silksong 也有存档损坏报告。多用游戏内多槽位，定期复制 Eden 存档目录。
2. **文字/字体**：有乱码、文字抖动、非英文字体卡顿的 issue；中文汉化补丁尤其要先测。遇到文字问题，先关“异步 GPU 模拟”。
3. **视频播放**：部分游戏 FMV 有白屏/暗 overlay 报告；开场动画先看一遍。
4. **音频**：NXOpus/audout 有个案；语音、BGM 先测试。
5. **触屏/切后台**：有触摸控制失效、切后台黑屏的报告；建议用手柄，切换应用前先存档。
6. **存储与版本**：VN 常见 10–30GB；Switch 版不少是全年龄/删减版，内容和 PC 版可能不同，买之前确认。

### 5.2 原生版优先

FSN、Witch on the Holy Night、Steins;Gate、CLANNAD、Ace Attorney、Danganronpa、Nekopara 都有 PC 或手机版。真正值得用 Eden 模拟的，是 **Tsukihime Remake、Emio、Famicom Detective Club** 这类没有 PC/手机版的 Switch 独占 VN。

### 5.3 值得模拟的 Switch 独占 VN

- **Tsukihime Remake**：无 PC 版，移动端只能模拟/串流。
- **Emio – The Smiling Man**：Switch 独占。
- **Famicom Detective Club** 重制版：Switch 独占。
- 其他 galgame 先查 PC/手机版；有原生版就别折腾模拟。

---

## 6. 设置与避坑

### 6.1 版本与驱动

- 优先 Eden 0.2.1 稳定版或 2026-10 nightly；某游戏失败再试 Eden Legacy。
- 不要用来路不明的 APK。
- 驱动：Vulkan + 系统 Mali 驱动；不要安装第三方“Mali 驱动包”。

### 6.2 图形设置

- 掌机模式，0.75x 起步；重载游戏 0.5x；1x 只在确认稳定后开。
- GPU 精度：Fast/Balanced 起步；画面错误再改 Accurate/High（会降帧）。
- Vulkan 优化：Eden Veil 里的 Vulkan 优化项可以试，Mali 用户反馈提升明显；但个别游戏会崩，逐个开。
- 异步 GPU：3D 动作游戏可开；VN/文字游戏出现乱码/抖动就关。

### 6.3 CPU/后台

- 默认 NCE；随机崩溃/音频异常时试 JIT。
- 关后台、关省电模式；12GB 比 9a 的 8GB 稳，但 Android LMK 仍可能杀进程。

### 6.4 散热

- 基础版 Pixel 9 无均热板；取壳、别边充电边玩、可用半导体散热器。
- 长时间玩必降频；建议每 30–60 分钟休息/重启游戏。

### 6.5 存档

- 多槽位 + 定期备份；不要只靠即时存档/切后台。
- 长游戏定期重启 Eden，降低内存泄漏风险。

### 6.6 更新

- 有些游戏更新后反而变慢/崩溃（Hollow Knight、Sonic Mania）；保留 base 版本测试。
- 新 nightly 可能修复旧问题，也可能引入回归；保留一个稳定版备用。

---

## 7. 证据强度与局限

没有“基础版 Pixel 9 + Eden 全游戏库”的完整测试。现有数据是三条线：

1. **Pixel 9a / Tensor G4 / 8GB / Citron 0.6.1 / 默认设置 / 每游戏几分钟**：保守下限；Citron ≠ Eden。
2. **Pixel 9 Pro XL / 16GB / Eden 0.0.3**：乐观上限；有均热板、RAM 更大。
3. **基础版 Pixel 9 / 12GB / Eden Nightly**：零散实测（SMT V、FFT、Octopath II、Dark Souls、TOTK）。

基础版 Pixel 9 的 12GB 比 9a 好，但没有均热板，长时间性能更接近 9a，而不是 Pro XL。社区样本小、版本差异大；PC 兼容表（Ryubing/yuzu）只能说明“模拟器能跑”，不能证明 Pixel 9 顺畅。

**结论**：这份清单是“优先级建议”，不是“保证列表”。每个游戏先试 15–30 分钟，确认无崩溃/花屏/存档问题再投入。

---

## 8. 快速决策：按需求选游戏

| 你想要 | 推荐 |
|---|---|
| 最稳的 2D 动作/银河城 | Hollow Knight、Metroid Dread、Hades、Dead Cells、Katana ZERO |
| 2D 平台/派对 | Rayman Legends、Shovel Knight、Boomerang Fu、TowerFall、Duck Game |
| 轻量 RPG/经营 | Stardew Valley、Undertale、Balatro、Monster Sanctuary、Cassette Beasts |
| 2D 魂类 | Salt and Sacrifice、Hollow Knight、Nine Sols（先试） |
| Atlus | Persona 4 Golden、13 Sentinels；P5R 只在你接受 20–30fps 时考虑 |
| Galgame | Tsukihime Remake、Emio、Famicom Detective Club；其他优先原生版 |
| 3D 大作 | 不建议：BOTW/TOTK、Odyssey、SMT V、P5R、Pokemon SV/ZA |

---

## 9. 此前调研结论索引（摘要）

> 以下是本系列此前调研的高层结论，详细表格与证据见对应报告。

### 9.1 四款 Switch 模拟器对比（yuzu / Eden / Ryujinx / Ryubing）

- **yuzu**：已停止官方开发；兼容性基线仍在，但没有新修复。
- **Eden**：活跃的 yuzu 分支，Android 支持最好；Mali 仍是短板；版本回归和存档风险存在。
- **Ryujinx**：已停止官方开发；PC 端兼容面广。
- **Ryubing**：活跃的 Ryujinx 分支，PC 端继续更新；不适合作为 Android 方案。
- **共同结论**：没有“全能模拟器”；兼容性、崩溃、存档安全、性能都要分游戏、分版本、分设备看。

### 9.2 任天堂第一方“完美兼容”清单

- 此前已按“完美兼容/回归/社区反馈/注意事项”整理。
- 核心结论：**“完美兼容”高度依赖版本、设备和游戏更新，不能跨设备照搬**；第一方大作在 Android/Mali 上尤其容易遇到图形/性能问题。

### 9.3 Switch 独占（Windows/Steam 玩不到）

- 任天堂第一方主机游戏没有官方 PC/Steam 版。
- 典型独占：Zelda BOTW/TOTK、Mario Odyssey、Smash Ultimate、Animal Crossing、MK8D、Splatoon 3、Pokemon、Mario Wonder、Metroid Dread/Prime 4、Fire Emblem、Xenoblade 3、Kirby 等。
- 部分第三方“伪独占”已有 PC 版（如 Monster Hunter Rise、SMT V: Vengeance、Octopath、Persona 5 Royal 等）。
- Switch 2 独占另列（Mario Kart World、DK Bananza、Hyrule Warriors: Age of Imprisonment 等）。

---

## 10. 主要来源

### 官方/硬件

- [Eden 官方系统要求](https://eden-emu.dev/system-requirements/)
- [Eden Releases](https://git.eden-emu.dev/eden-emu/eden/releases)
- [Pixel 9 规格（Notebookcheck）](https://www.notebookcheck.biz/Google-Pixel-9.888599.0.html)
- [Pixel 9 无均热板（WCCFTech）](https://wccftech.com/pixel-9-only-model-in-series-without-vapor-chamber/)
- [Tensor G4 高负载降频约 50%（WCCFTech）](https://wccftech.com/tensor-g4-in-pixel-9-pro-xl-poor-thermal-performance-throttles-easily/)
- [Pixel 9 Pro 均热板（9to5Google）](https://9to5google.com/2024/09/10/pixel-9-pro-vapor-chamber/)

### Pixel 9 系实测

- [Pixel 9a 40 款 Switch 游戏测试（Citron 0.6.1）](https://www.reddit.com/r/EmulationOnAndroid/comments/1kbpaao/pixel_9a_40_switch_games_tested/)
- [Hades 2 在 Pixel 9 Pro XL 上 60fps](https://www.reddit.com/r/EdenEmulator/comments/1nu6ao6/hades_2_running_on_pixel_9_mali/)
- [Pixel 9 上 SMT V Vengeance 黑屏](https://www.reddit.com/r/EdenEmulator/comments/1ua77lv/issue_with_shin_megami_tensei_v_vengeance/)
- [Pixel 9 Pro 上 FFT 战斗 10–25fps](https://www.reddit.com/r/EdenEmulator/comments/1r2xwb9/fftivc_on_pixel_mali_running_slow_during_battles/)
- [Pixel 9 上 Octopath Traveler II 渲染异常](https://www.reddit.com/r/EdenEmulator/comments/1nj0vyc/help_needed_weird_screen_issue_on_pixel_9_with/)
- [Pixel 9 上 Dark Souls Remastered](https://www.reddit.com/r/EdenEmulator/comments/1v0wadm/dark_souls_remastered_pixel_9_eden_nightly/)
- [Pixel 9 上 TOTK 亮度 bug](https://www.reddit.com/r/EdenEmulator/comments/1np03tz/totk_on_pixel_9_graphics_get_bright/)
- [Pixel 9 Pro XL 用户反馈与设置](https://www.reddit.com/r/EdenEmulator/comments/1ohscli/pixel_9_pro_xl_how_can_i_play_better/)
- [Pixel 9 Pro 用户 Mario 游戏反馈](https://www.reddit.com/r/EmulationOnAndroid/comments/1kyz6fl/pixel_9_pro_and_mali_for_emulation/)

### Atlus

- [P5R 在 Mali GPU 上的讨论](https://www.reddit.com/r/EmulationOnAndroid/comments/1ss09la/has_anyone_managed_to_run_persona_5_royal_on_a/)
- [P5R 在天玑 8400 Ultra 上 20–34fps](https://www.reddit.com/r/EmulationOnAndroid/comments/1r547q0/persona_5_royal_running_30-45_fps_on_dimensity/)
- [P5R 在天玑 8400 Ultra 上纹理闪烁](https://www.reddit.com/r/EdenEmulator/comments/1ww6a8x/flickering_problema_on_dimensity_8400-ultrw/)
- [P5T 随机冻结](https://www.reddit.com/r/EdenEmulator/comments/1vnawgk/persona_5_tactica_game_freeze_randomly/)
- [Catherine Full Body 频繁崩溃](https://www.reddit.com/r/EdenEmulator/comments/1o4o72l/catherine_full_body_crashes_every_few_minutes/)
- [P4G 8 小时后崩溃](https://www.reddit.com/r/EdenEmulator/comments/1ue8m0y/persona_4_golden_crashing_after_8_hours_of_game/)
- [13 Sentinels 在 Eden 上的推荐](https://www.reddit.com/r/EmulationOnAndroid/comments/1uf1n51/game_recommendations_13_sentinels_aegis_rim_on/)
- [Unicorn Overlord 随机 malloc 崩溃 #582](https://github.com/eden-emulator/Issue-Reports/issues/582)

### Galgame

- [月姬重制在 Android 上运行](https://www.reddit.com/r/Tsukihime/comments/1r3ck07/managed_to_get_tsukihime_remake_running_on_android/)
- [Fate/Stay Night Remastered 存档崩溃 #626](https://github.com/eden-emulator/Issue-Reports/issues/626)
- [FSN Android 存档崩溃讨论](https://www.reddit.com/r/fatestaynight/comments/1jwegma/fate_stay_night_switch_not_working_on_android/)
- [Eden 文字乱码 #326](https://github.com/eden-emulator/Issue-Reports/issues/326)
- [Eden 触摸控制问题 #551](https://github.com/eden-emulator/Issue-Reports/issues/551)
- [Witch on the Holy Night Steam](https://store.steampowered.com/app/2052410/WITCH_ON_THE_HOLY_NIGHT/)
- [Tsukihime 官方页面](http://www.tsukihime-en.com/)

### 2D/兼容性

- [Mali 轻量游戏清单](https://www.reddit.com/r/EmulationMediatekMali/comments/1p2ih8b/eden_emulatorswitch_games_on_mali_gpu/)
- [SD865/Adreno 650 上 2D 游戏黑屏](https://www.reddit.com/r/EdenEmulator/comments/1wcdr7m/samsung_tab_s7_plus_sd_865_adreno_650_2d_low_end/)
- [Silksong 存档损坏报告](https://www.reddit.com/r/EdenEmulator/comments/1oouk86/help_for_some_reason_my_hollow_knight_silkson/)
- [Hollow Knight 更新后掉帧 #212](https://github.com/eden-emulator/Issue-Reports/issues/212)
- [Sonic Mania 新版本崩溃 #480](https://github.com/eden-emulator/Issue-Reports/issues/480)
- [DQ I&II HD-2D 白视频 #153](https://github.com/eden-emulator/Issue-Reports/issues/153)
- [Skyward Sword FMV 暗 overlay #501](https://github.com/eden-emulator/Issue-Reports/issues/501)
- [Mali 上 Eden 设置讨论](https://www.reddit.com/r/EmulationOnAndroid/comments/1ney31h/best_switch_emulation_on_mali_gpu_so_far_eden/)

---

**文档结束**  
**最后更新**：2026-10-23  
**适用设备**：Google Pixel 9 系列（Tensor G4 / Mali-G715）；其他 Mali 设备可参考，但需按实际散热与驱动调整。  
**免责声明**：模拟器、ROM、固件与密钥的合法性因地区而异；请遵守当地法律与任天堂服务条款。
