---
name: rimworld-workshop-download
description: RimWorld（环世界）模组全能工具箱——① 不装 Steam 客户端下载创意工坊 mod（RimSort + SteamCMD、目录前缀结构、匿名登录、排错）；② 把 ModsConfig 的 packageId 反查成工坊 ID（RMK ModList.tsv / 工坊中文包索引 / 定向检索 / 排除官方 DLC）；③ **用户问任何 RimWorld 模组问题（机制、数值、兼容性、报错、某 Def 在哪、某类叫什么）时，先用 search-mod.py 查本地 mod 源码与 Def 索引，不要凭记忆或先联网**。当用户说「不用 Steam 客户端下 mod」「RimSort 安装/配置/调试」「steamcmd 下载创意工坊失败」「GOG/Epic 版 RimWorld 怎么装工坊 mod」「检查某 mod 的源码」「本地 mod 在哪」「有些 mod 找不到工坊 ID」「把 packageId 映射成工坊 ID」「汉化包找不到」「这个 mod 是怎么实现的」「这个 Def/类在哪定义」「XX 和 YY 兼不兼容」「这个报错哪来的」时使用。
agent_created: true
---

# RimWorld 创意工坊 mod 免客户端下载（RimSort + SteamCMD）

## ★★ 最高优先规则：用户问任何 RimWorld 模组的事，先查本地源码（用户 2026-10-08 明确要求）

**不要凭记忆或联网回答 RimWorld 模组问题。** 本机存着 **417 个 mod / 3.1 万个 Def XML / 5,302 个 .cs 文件 / 52,883 个 defName**，
权威答案就在本地。流程固定为：

```
用户问 RimWorld mod 相关
  ├─ 问「某机制怎么实现的 / 数值是多少 / 兼容不兼容 / 这个报错哪来的」
  │    → search-mod.py --grep <关键词> --cs        # 找实现代码
  │    → search-mod.py --grep <关键词> --xml       # 找 Def / Patch
  ├─ 问「某 Def 在哪定义 / 有没有这个 Def」
  │    → search-mod.py --def <defName>             # 秒级，走索引
  ├─ 问「某类叫什么 / 谁 patch 了这个方法」
  │    → search-mod.py --cls <类名>
  ├─ 问「这个 mod 是什么 / 装了没 / 支持哪些版本」
  │    → find-mod.py <关键词>
  └─ 本地确实查不到（mod 未下载 / 纯 DLL 需反编译 / 版本太旧）
       → 才联网（工坊页 / GitHub raw / Ludeon 论坛），并说明「本地无源码」
```

```bash
cd C:\SteamCMDData
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"

"$PY" search-mod.py --def <defName>          # 精确查 Def（走索引，秒级）
"$PY" search-mod.py --def-like <片段>         # 模糊查 Def
"$PY" search-mod.py --cls <类名>              # 查 C# 类
"$PY" search-mod.py --types [片段]            # 列 Def 类型统计
"$PY" search-mod.py --grep <词> --cs          # 实时全文搜源码
"$PY" search-mod.py --grep <词> --xml --mod <工坊ID>   # 限单个 mod
"$PY" search-mod.py --list                    # 列出全部 mod + 是否带源码
"$PY" find-mod.py <关键词>                     # 定位 mod 目录 + 源码路径
"$PY" make-def-index.py                       # 下载新 mod 后重建索引
```

**回答时的硬要求**：
- 给出结论必须附 **工坊ID + 文件相对路径 + 行号**，让用户能自己复核。
- 区分「从源码读到的」/「从 Def XML 读到的」/「只有 DLL 未反编译，属推断」。
- 索引是快照（`def-index.json` 的 `meta.built`）；若用户刚下了新 mod，先 `make-def-index.py` 再查。

---

## ★ 本地 mod 库位置（用户已确认，最先读这一节）

| 用途 | 路径 |
|---|---|
| **mod 本体根目录** | `C:\SteamCMDData\steam\steamapps\workshop\content\294100\` |
| 单个 mod | `…\294100\<工坊ID>\`（文件夹名 = Steam 工坊数字 ID） |
| **Def / 类名索引** | `C:\SteamCMDData\def-index.json`（`make-def-index.py` 产出，速查主力） |
| 源码索引 | `C:\SteamCMDData\source-index.json`、`outputs\mod源码索引.csv` |
| SteamCMD | `C:\SteamCMDData\steamcmd\steamcmd.exe`（下载日志 `logs\console_log.txt`） |
| RimSort | `C:\RimSort\RimSort.exe` |
| 用户 mod 清单 | `C:\Users\Admin\Downloads\Medieval.xml`、`ce0906.xml` |

**规模（2026-10-08）**：417 个 mod。索引收录 **31,020 个 Def XML / 5,302 个 .cs / 52,883 个 defName / 5,543 个类**。
**66+ 个带 `Source/` C# 源码**、218 个带 DLL、其余纯 XML+贴图。

⚠️ **索引构建的性能关键**（第一次跑 10 分钟没跑完，改完 8 分钟出结果）：
1. **必须跳过 `Languages/` 目录** —— 全库 6.7 万 XML 里 1.4 万+ 是翻译文件，跳过后待读文件降到 3.1 万。
2. **二进制读 + 字节预筛**：`data = open(f,'rb').read()` → `if b"defName" not in data: continue` → 再 decode，比文本读快 3-5 倍；单文件限 ≤ 2MB。
3. ⚠️ `search-mod.py --grep` 全库实时扫描会被沙箱 SIGTERM 杀掉（>2 分钟）→ **先建索引，再查**；`--grep` 只用于限定单个 mod 或小范围。

### 「检查某 mod 的源码」标准动作

```bash
cd C:\SteamCMDData
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"
"$PY" find-mod.py --src <关键词>   # 按 工坊ID / packageId / 名称 模糊匹配
"$PY" find-mod.py --list           # 列出全部 316 个
"$PY" make-source-index.py         # 下载新 mod 后重建索引
```

`find-mod.py` 直接输出：mod 目录绝对路径、**源码目录绝对路径 + .cs 文件数**、DLL 路径、支持版本。

⚠️ **源码常在 `<mod>\<版本>\Source\`**（如 `1578693166\1.5\Source`，198 个 .cs），不一定在 mod 根下。
⚠️ 本机**未装 ILSpy / dnSpy / ilspycmd**。要反编译 DLL 需先 `dotnet tool install -g ilspycmd`；能走 `Source/` 就走源码。
⚠️ 读 `About.xml` 取 packageId **必须先剔除 `<modDependencies>` / `<modDependenciesByVersion>` / `<loadAfter>` 等块**——块内也有 `<packageId>`（那是依赖），否则误判。共用库见 `modlib.py`。
⚠️ packageId **不区分大小写**，比对前一律 `.lower()`。

### 配套脚本（本 skill 自带 `scripts/`，也部署在 `C:\SteamCMDData\`）

| 脚本 | 用途 |
|---|---|
| `search-mod.py` | **★ 本地速查主力**：`--def` / `--cls` / `--def-like` / `--types`（走索引，秒级）；`--grep --cs/--xml [--mod ID]` 实时全文 |
| `make-def-index.py` | **★ 建 Def / 类名索引** → `def-index.json`（下载新 mod 后重跑） |
| `modlib.py` | 共用解析库：剔除依赖块取 mod 自身 packageId、读名称/大小 |
| `find-mod.py` | **按关键词定位 mod + 源码路径** |
| `make-source-index.py` | 重建源码索引（`source-index.json`） |
| `true-verify.py` | 校验命中率（最严口径：剔依赖 + 忽略大小写 + 只看顶层 About.xml） |
| `make-manifest.py` | 生成已下载 mod 清单 CSV |
| `make-gap-list.py` | 生成未解析清单 + 建议检索词 |
| `api-check.py` | 批量查 Steam API（result / 可见性 / 大小） |
| `rmk-match.py` | **反查通道 1**：拉 RMK `ModList.tsv` 做 packageId 精确对账 |
| `crawl-zh.py` | **反查通道 2**：工坊全站中文检索（9 个词 × 20 页）→ `zh-packs.json` |
| `get-collection.py` | **反查通道 2**：抓工坊汉化合集子项 → JSON（`<合集ID>...`） |
| `match5.py` | **反查通道 2**：token 级匹配（含停用词表 + 汉化包优先级）→ `zh-match5.json` |
| `lookup.py` | 按关键词查汉化包池（`lookup.py "Vanilla Genetics Expanded"`） |
| `ws1.py` | **反查通道 3**：工坊定向检索（`ws1.py "Medieval Overhaul 汉化"`） |
| `consolidate.py` | 四通道整合 → `outputs\未解析-网络检索结果.csv` |
| `dl-loop.cmd` | 逐 ID 独立会话下载（配合 WMI 启动，见 6e） |

⚠️ 脚本里 `C = r"C:\SteamCMDData\steam\steamapps\workshop\content\294100"` 与用户 XML 路径是**硬编码**的；换机器需改 `modlib.py` 顶部常量。

## 核心事实（已实测，勿再猜）

| 事实 | 值 |
|---|---|
| RimWorld AppID | `294100` |
| 匿名下载是否可行 | ✅ 可行，`login anonymous` 即可，**不需要 Steam 账号** |
| 少数锁匿名的 mod | 回车后**立刻**报 `failed (Failure)`；RimSort 无法处理（它写死 anonymous） |
| 超时误报 | **等一会儿**才报错 = SteamCMD 超时，重跑同一命令会**续传** |
| 在线工坊下载站 | 基本全部关停，别推荐 |

**判据**：立即失败 = 权限问题；延迟失败 = 网络/超时问题。

## RimSort 的目录约定（读 v1.15.0 源码 `app/utils/steam/steamcmd/wrapper.py` 确认）

「SteamCMD installation location」设置项填的是**前缀目录**，不是 steamcmd.exe 所在目录：

```
<前缀>\steamcmd\steamcmd.exe
<前缀>\steam\steamapps\workshop\content\294100\<工坊ID>\
<前缀>\steam\steamapps\workshop\appworkshop_294100.acf   ← 更新检测靠它，别删
```

RimSort 写死的下载脚本（落在 `%TEMP%\steamcmd_script.txt`）：

```
force_install_dir "<前缀>\steam"
login anonymous
workshop_download_item 294100 <工坊ID> [validate]
quit
```

下载完成后 RimSort 建 junction：`<前缀>\steam\steamapps\workshop\content\294100` → 游戏 `Mods` 目录。

**推荐前缀**：`C:\SteamCMDData`（纯 ASCII、无空格）。

## 步骤 1：装 SteamCMD（按前缀结构摆放）

```bash
# 下载（约 775KB 引导器）
curl -sL --max-time 180 "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip" -o /tmp/steamcmd.zip
```

```powershell
# 解压到 <前缀>\steamcmd\
New-Item -ItemType Directory -Force -Path "C:\SteamCMDData\steamcmd" | Out-Null
Expand-Archive -Path "C:\Users\<user>\AppData\Local\Temp\steamcmd.zip" -DestinationPath "C:\SteamCMDData\steamcmd" -Force
```

**首次运行会自更新（约 43MB，1~2 分钟），然后 exit code 7 并退出**——这是正常的，必须**再跑一次**真正的下载命令。

## 步骤 2：实测匿名通道（关键验证，务必做）

```bash
cd /c/SteamCMDData/steamcmd && ./steamcmd.exe \
  +force_install_dir "C:\SteamCMDData\steam" \
  +login anonymous +workshop_download_item 294100 2009463077 +quit
```

成功标志：

```
Connecting anonymously to Steam Public...OK
Success. Downloaded item 2009463077 to
  "c:\steamcmddata\steam\steamapps\workshop\content\294100\2009463077" (5729526 bytes)
```

**验证要点**：字节数应与 Steam WebAPI 报的 `file_size` 完全一致。

查 mod 元数据（校验工坊 ID 是否有效、拿准确大小）：

```bash
curl -s -X POST "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/" \
  -d "itemcount=1&publishedfileids[0]=2009463077" | grep -o '"title":"[^"]*"\|"file_size":"[^"]*"'
```

常用参照 mod：Harmony `2009463077`(5.7MB)、HugsLib `818773962`(2.5MB)、Vanilla Expanded Framework `2023507013`(12MB)。

## 步骤 3：装 RimSort

```bash
# 查最新版与资产
curl -sL "https://api.github.com/repos/RimSort/RimSort/releases/latest" -o /tmp/rel.json
python -c "import json;d=json.load(open('/tmp/rel.json'));[print(a['name'],a['size']) for a in d['assets'] if 'Windows_x86_64.zip' in a['name']]"
```

- Windows 便携版 zip 约 **200MB** → 必须后台下载（前台会撞 120s 超时被 SIGTERM）。
- **zip 内含顶层 `RimSort/` 目录**，解压后需扁平化：

```powershell
Get-ChildItem "C:\RimSort\RimSort" -Force | Move-Item -Destination "C:\RimSort" -Force
Remove-Item "C:\RimSort\RimSort" -Force -Recurse -ErrorAction SilentlyContinue
```

- 扁平化后可能残留一个**空的** `C:\RimSort\RimSort`，被系统占用删不掉 → 无害，忽略。

**无 GUI 验证二进制是否正常**（无需显示器）：

```bash
cd /c/RimSort && ./RimSort.exe build-db --help   # 应打印 usage 并 exit 0
```

**开调试日志**：在 RimSort 数据目录建一个空的 `DEBUG` 文件。

```powershell
New-Item -ItemType Directory -Force -Path "$env:LOCALAPPDATA\RimSort" | Out-Null
New-Item -ItemType File -Force -Path "$env:LOCALAPPDATA\RimSort\DEBUG" | Out-Null
```

日志位置：`%LOCALAPPDATA%\RimSort\Logs\RimSort.log`

## 步骤 4：配置 RimSort

设置 → **位置（Locations）** 填三项：

| 项 | 值 |
|---|---|
| 游戏安装目录 | RimWorld 根目录（含 `RimWorldWin64.exe`） |
| 本地 Mods 目录 | RimWorld 的 `Mods` 文件夹 |
| 配置目录 | `...\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config` |

设置 → **SteamCMD**：安装位置填 `<前缀>`（如 `C:\SteamCMDData`）。
点 `Setup SteamCMD` 若提示已存在并要求重装 → **选「否」**。

⚠️ **不要勾选** `Enable Steam client integration`（没有 Steam 客户端时勾了会出错）。

下载入口：`Download` → `Add workshop mods` → `Add to list` → 选 **`Download mod(s) (SteamCMD)`**。
**别选 `(Steam app)`**，那个需要 Steam 客户端。

⚠️ **`build-db` 子命令不要用**：官方要求 Steam WebAPI key，且「需在 Steam 拥有 RimWorld，可能还需消费 ≥5 美元」。非 Steam 用户保持默认社区数据库源。

## 附：不依赖 RimSort 的批量下载脚本

写到 `<前缀>\workshop-dl.cmd`（**纯 ASCII 内容**，中文会乱码）：

```cmd
@echo off
setlocal
set "STEAMCMD=C:\SteamCMDData\steamcmd\steamcmd.exe"
set "PREFIX=C:\SteamCMDData\steam"
set "SCRIPT=%TEMP%\workshop-dl.txt"
if "%~1"=="" ( echo Usage: workshop-dl.cmd ^<workshopID^> [workshopID ...] & exit /b 1 )
> "%SCRIPT%" echo force_install_dir "%PREFIX%"
>>"%SCRIPT%" echo login anonymous
for %%A in (%*) do >>"%SCRIPT%" echo workshop_download_item 294100 %%A
>>"%SCRIPT%" echo quit
"%STEAMCMD%" +runscript "%SCRIPT%"
```

用法：`workshop-dl.cmd 2009463077 818773962`
工坊 ID 从链接取：`steamcommunity.com/sharedfiles/filedetails/?id=XXXXXXXXXX`

## 从 ModsConfig.xml 批量下载整套 mod 列表

用户给一份 `ModsConfig.xml`（或它的导出）想「把这套 mod 全下下来」时走这条。**核心难点：ModsConfig 里存的是 packageId，不是工坊 ID，必须先映射。**

### 1. 抽 packageId

```bash
grep -o '<li>[^<]*</li>' ModsConfig.xml | sed 's/<[^>]*>//g' > pkgids.txt
```

### 2. 拿社区工坊数据库做映射

RimSort 默认源（源码 `app/models/settings.py` 里的 `external_steam_metadata_url`）：

```
https://raw.githubusercontent.com/RimSort/Steam-Workshop-Database/main/steamDB.json
```

约 **49MB**。结构：`{"version":..., "database": {"<publishedFileId>": {"packageId":..., "name":..., "dependencies":{...}}}}`

### 3. 映射（关键坑）

**57,679 条工坊条目里只有 18,645 条带 `packageId`**——数据库靠「下载 mod 后解析 About.xml」补全，收录很不全。
实测一份 **490 个 mod** 的清单：映射出 286 个，四轮搜索后扩到 **322 个**，最终**下载并回读 packageId 校验通过 311 个 = 63%**。剩下 179 个映射不到。
→ **63% 是这类清单的自动化可靠上限**，剩下的必须人工在 RimSort 工坊浏览器里手搜。

字段名两种写法都要读：`packageId` 和 `packageid`。

```python
idx = {}
for pfid, info in db.items():
    v = info.get("packageId") or info.get("packageid")
    if v: idx.setdefault(v.lower(), pfid)   # 小写归一
```

排除官方：`p == "ludeon.rimworld"` 或 `p.startswith("ludeon.rimworld.")`（官方 DLC 不在工坊）。

⚠️ **别用 `raw.count(pkgid)` 判断是否存在**——短 ID 会命中长 ID 的子串（`al9000.highmedieval` 会命中 `serzhuk.al9000.highmedieval`），造成误判。

### 3b. 验收：回读 About.xml 时必须剔除依赖块（最容易踩的坑）

**`About.xml` 里 `<modDependencies>` / `<modDependenciesByVersion>` / `<loadAfter>` / `<loadBefore>` / `<incompatibleWith>` 块内也含 `<packageId>`**——那是**依赖**，不是本 mod 的 ID。
用裸正则 `re.findall(r"<packageId>(.*?)</packageId>", xml)` 会把 `brrainz.harmony` 之类当成 mod 自身 ID，导致**命中数虚高**（实测 330 → 真实 311）。

```python
DEP_BLOCKS = ["modDependencies", "modDependenciesByVersion", "loadAfter", "loadBefore",
              "forceLoadAfter", "forceLoadBefore", "incompatibleWith",
              "modOptionalDependencies", "modOptionalDependenciesByVersion", "modRequirements"]
DEP_RE = re.compile(r"<(%s)\b[^>]*>.*?</\1>" % "|".join(DEP_BLOCKS), re.S | re.I)

def self_pid(about_path):
    t = open(about_path, encoding="utf-8", errors="ignore").read()
    t = DEP_RE.sub("", t)                 # 先剥离依赖块
    m = re.search(r"<packageId>\s*([^<\s]+)\s*</packageId>", t, re.I)
    return m.group(1).strip() if m else None
```

另外两条验收规则：
- **packageId 不区分大小写**，比对前一律 `.lower()`（否则 `Aoba.Fortress.Neolithic` vs `aoba.fortress.neolithic` 会漏判）。
- 只看**顶层** About.xml（`<mod>/About/` 或 `<mod>/<版本>/About/`，相对深度 ≤ 2），别递归到嵌套的捆绑 mod。

### 3c. 同名碰撞：score 100 也不代表是对的 mod

搜索「查询词 == 标题」拿到 100 分**只说明标题一样，不说明是同一个 mod**。实测踩到 3 次：

| 用户要的 | 误下 | 正确 |
|---|---|---|
| `bbbbilly.smokedmeat` | `dismarzero.VGP.Smokedmeat`（同名 "Smoked meat"） | `BBBBilly.SmokedMeat` |
| `mlie.apothecary` | `pelador.apothecary`（原作者版 vs Mlie 接手版） | 需手搜 |
| `diyshanliu.zh.rimpedia` | `yrtwof.Rimpedia`（汉化包 vs 英文本体） | 需手搜 |

**唯一可靠确认手段：下载后回读 `About.xml` 的 `<packageId>` 比对。** 映射表本身不可信。

### 4. 先算体积再下载

`GetPublishedFileDetails` 一次可提交多个 ID（50 个一批安全），拿 `file_size` 求和。
实测 286 个 mod ≈ **2.95 GB**，先报给用户。

### 5. 生成 runscript 并下载

```
force_install_dir "<前缀>\steam"
login anonymous
workshop_download_item 294100 <ID1>
...
quit
```

```bash
steamcmd.exe +runscript "C:\SteamCMDData\download-all.txt"
```

**重跑安全**：已下好的会跳过，超时中断的会续传。

### 6. 提高映射准确率（实测数据）

| 层 | 方法 | 覆盖 | 实测精度 |
|---|---|---|---|
| L1 | 社区库 packageId 精确索引 | 286/484 = 59% | **~100%**（真值校验 0 误报） |
| L2 | 社区库 `steamName` 归一化后**精确相等** | +36 | **86%**（14 个真值抽样） |
| L3 | `steamName` 包含匹配 | +45 | 未测，多为「汉化包→本体」 |
| L4 | 工坊搜索 + **降级查询** | +23 | **低，系统性误判** |

**可靠上限 ≈ 67%。** 再往上加自动化只会引入错误。

**① 连写 token 切分（关键技巧）**
packageId 常连写（`medievaltotalrim` / `fireandsteel`）。用社区库 57k 条 `steamName` 抽出的词表做 DP 切分：

```python
def best_split(tok, vocab):        # medievaltotalrim -> medieval total rim
    n = len(tok); best = [None]*(n+1); best[0] = []
    for i in range(n):
        if best[i] is None: continue
        for j in range(i+2, min(n, i+15)+1):
            if tok[i:j] in vocab:
                cand = best[i] + [tok[i:j]]
                if best[j] is None or len(cand) > len(best[j]): best[j] = cand
    return best[n] or [tok]
```

**② 打分规则（方向搞反就会系统性误判）**

```python
query in title  → 85+   # 查询是标题的一部分，可靠
title in query  → ≤60   # 标题是查询的前缀，八成是「通用前缀命中框架 mod」兜底
归一化后相等     → 100
```

反例（实测踩过）：
- `vanillaexpanded.vnutriente` → 错配到 `Vanilla Expanded Framework`
- `athelas.medievaltotalrim.byzantium` → 错配到 `Medieval Total Rim: **Core**`
- `zruic.expand.relation` → 错配到 `Vanilla Races Expanded - Android`

**降级查询（去掉末词再搜）是陷阱**——为了让子模块能搜到而降级，结果子模块全被错配到本体。
宁可漏，不可错。

**③ 模糊子串匹配必须加长度比门槛**
不加约束时 `athelas.medievaltotalrim.core` 会匹配到「起来不准死」这种无关条目。
要求 `min(len(q),len(nm))/max(len(q),len(nm)) >= 0.7`。

**④ 真值校验是唯一可靠的验收**
下载后读 `About/About.xml` 的 `<packageId>`，和清单里的期望值比对：

```python
for p in [d/"About"/"About.xml", *d.glob("*/About/About.xml")]:   # 注意版本文件夹
    m = re.search(r"<packageId>\s*([^<\s]+)\s*</packageId>", p.read_text("utf-8","ignore"), re.I)
```

**⑤ packageId 碰撞（必查，15.1% 命中）**
社区库 18,645 条带 packageId 的条目里，**2,814 条（15.1%）与其他条目共享 packageId**。
用 `setdefault` / 取第一个会取到废弃版。实测用户 484 个清单里 8 个碰撞、**3 个取错**：

| packageId | 错取 | 正确 |
|---|---|---|
| `brrainz.harmony` | `[Deprecated] Harmony for Apple Silicon` | `Harmony` |
| `vanillaexpanded.vfesecurity` | `[1.6 Hack][DEPRECATED]`（已删） | `Vanilla Furniture Expanded - Security` |
| `cj.rimtalk.expandmemory` | `(Abandoned) ... temporary`（已删） | `RimTalk - Expand Memory` |

修正策略：
1. 收集该 packageId 的**所有**候选 ID；
2. 批量查 Steam API，**剔除 `result != 1` 的**（`result=9` = 工坊已删除/隐藏）；
3. 按标题与 packageId 的 token 匹配度打分，对 `[DEPRECATED]` / `[Hack]` / 语言后缀（`[RUS]`/`[THAI]`）**降权**。

**⑥ 下载报错的三种含义（别混）**

| 报错 | 含义 | 处理 |
|---|---|---|
| `failed (Failure)`（立即） | 该 mod 锁匿名 | 换源 |
| `Insufficient Privilege` | **匿名被拒**（实测约占 2%） | 只能登录拥有 RimWorld 的账号 |
| `failed (File Not Found)` / API `result=9` | **工坊条目已删除** | 无法下载，找替代条目 |
| `I/O Operation Failed` | 并发跑了两个 steamcmd | 串行重跑 |

**⑦ 硬天花板**：mod 若来自 GitHub / 贴吧整合包 / 作者群，**根本没有工坊 ID**，任何方法都映射不到。
剩下映射不到的，老实报给用户人工处理，别硬凑。

### 6b. 验证下载内容是否完整（别把源码误判成可用 mod）

判据必须**递归查找并排除 `Source/obj/bin/References`**——很多 mod 用版本文件夹
（`1.6/Assemblies/x.dll`），只看根目录 `Assemblies/` 会误判成「只有源码」。

```python
dlls = [f for f in d.rglob("*.dll")
        if not any(p.lower() in ("source","obj","bin","references","packages")
                   for p in f.relative_to(d).parts)]
```

同时检查：有 `About/About.xml`、文件夹非空。
实测 66 个里 12 个「附带 .cs 源码但同时有程序集」= 作者顺手打包，**不影响使用**。

### 6c. 未映射到的怎么办

按优先级报给用户：
1. RimSort 工坊浏览器 → `Add Mods by Workshop ID` 手动补
2. 浏览器搜 mod 名，URL 里 `?id=` 即工坊 ID
3. GitHub Releases / Ludeon 论坛直链

### 6d. ★ 反查「packageId → 工坊ID」的四条通道（2026-10-08 实测，别重新摸索）

本地库 + steamDB.json 只能覆盖 ~63%。剩下的大头是**汉化包**，必须走下面四条。实测 179 个未解析项 → 169 个拿到工坊 ID（94.4%）。

#### 通道 1：RMK 韩化组 `ModList.tsv`（最高价值，零误报）

```bash
curl -sL "https://raw.githubusercontent.com/RimWorldKorea/RMK/main/ModList.tsv" \
     -o "C:/SteamCMDData/rmk-modlist.tsv"
```

格式：`工坊ID \t mod名 \t 翻译数据目录 \t 原mod packageId`，**3068 行 / 3040 条唯一映射**。
packageId 是**原 mod 的**（不是汉化包的），所以 `pid.lower() in table` 直接命中、无需回读验证。
实测对 179 个未解析项一次命中 **27 个**。脚本：`C:\SteamCMDData\rmk-match.py`。

> 推广：任何「翻译组仓库」都可能有这种 `ModList.tsv` / 映射表。**先找表，再做模糊匹配。**

#### 通道 2：工坊中文包索引（覆盖最大）

工坊 `browse` 接口支持中文 `searchtext`，且**匿名可访问**：

```
https://steamcommunity.com/workshop/browse/?appid=294100
  &searchtext=<关键词>&browsesort=textsearch&section=readytouseitems&numperpage=30&p=<页>
```

内嵌 JSON 的键被转义成 `\"`，正则要写成：

```python
re.finditer(r'\\"publishedfileid\\":\\"(\d+)\\"(.*?)\\"title\\":\\"(.*?)\\"', html)
```

**两个数据源合并成池（实测 2951 条去重）**：

| 来源 | 方法 | 量 |
|---|---|---|
| 工坊全站中文检索 | 9 个词（汉化/简中/简繁/汉化包/汉化补丁/中文化/中文/汉化组/翻译）× 最多 20 页 | 2094 条 |
| 汉化合集子项 | 抓 `sharedfiles/filedetails/?id=<合集ID>`，解析 `class="collectionItemDetails"` 下 `<a href="...id=(\d+)">标题</a>` | 1220 项 |

已验证的合集 ID：`1781246546` 边缘汉化组 中文Mod合集（822 项）、`2533638240` 简繁汉化合集（399 项）。
其他可抓：`2063188240`、`1718190143`、`3395775893`、`3558991062`。

**匹配算法（token 级 + 停用词表，这是关键）**：

```python
# 1) 标题去掉汉化标记，取出英文主体
ZH_MARK = r"(zh[-_ ]?pack|_zh\b|\bzh\b|汉化包|汉化补丁|汉化|中文汉化|简&?繁中文|简繁中文|中文翻譯|中文翻译|中文化|中文|chinese|translation|补丁)"
base = ZH_MARK.split(title)[0]
# 2) packageId 去前缀/后缀
PREFIX = r"^(zh|rwzh|chinesepackage|chinesetranslation|cn|chs|zhongwen)[.\-_]"
SUFFIX = r"[.\-_](zh|zht|zhtc|chs|cn|zhpatch|zhpack|hc|xt|93|chinese)([.\-_].*)?$"
# 3) 打分
#    全等 100 ｜ token 全等 90 ｜ 标题token∈包名 80 ｜ 包名token∈标题 78 ｜ 相似度>=0.62 → 68
```

⚠️ **停用词表必须有**：`rimworld framework core expanded vanilla faction factions translation chinese patch mod pack continued series medieval overhaul`。
否则 `ludeon.rimworld` 会匹配到「A RimWorld of Magic」，`zh.vanillaexpanded.vgeneticse` 会被「vanilla」带偏。

脚本：`crawl-zh.py`（全站检索）、`get-collection.py`（合集）、`match5.py`（匹配）、`consolidate.py`（整合）。

#### 通道 3：工坊定向检索（补漏，命中率最高）

对剩余项直接按「原 mod 英文名」搜工坊，例：

| 查询 | 命中 |
|---|---|
| `Medieval Overhaul 汉化` | `2567264503 Medieval Overhaul 汉化包` |
| `Tasty Armory Shining Armor` | `3482266407 Tasty Armory - In Shining Armor` |
| `Medieval Total Rim` | `3806242927 Core` / `3806251054 The Kingdom of Poland` … |

脚本：`ws1.py <查询1> <查询2> ...`。

#### 通道 4：Ludeon 官方（识别「不是 mod」的条目）

`ludeon.rimworld` / `.royalty` / `.ideology` / `.biotech` / `.anomaly` / `.odyssey` = **官方本体 + 5 个 DLC**，
永远不可能在工坊找到。统计命中率时要先把这 6 个排除，否则会低估。

#### ❌ GitHub / 代码搜索：本机全部不可用（已实测，别浪费时间）

| 通道 | 结果 |
|---|---|
| GitHub Code Search API | 需登录，匿名 401 |
| `github.com/search?type=code` HTML | 页面写 "Sign in to search code"，无结果 |
| Sourcegraph 公开 SSE API | 可达（`sourcegraph.com/.api/search/stream?q=...&v=V3&t=literal`），但**对小体量 RimWorld 仓库索引覆盖率≈0**，逐 packageId 检索全 0 命中 |
| grep.app | Vercel 人机校验，429 challenge |
| searchcode.com | API 404 |
| DuckDuckGo HTML | 限流 |

✅ **唯一有效路径：已知仓库 → 直取 `raw.githubusercontent.com`**（通道 1 就是这么拿到的）。
✅ 内置 **WebSearch 工具**有效：搜 `"<packageId>" rimworld` 能直接命中 GitHub issue 里 `工坊ID + 包名 + packageId` 三件套（如 RimWorldKorea/RMK 的 issue）。

#### 实测的命名规律（能省一半工作量）

- 汉化包 packageId 与工坊标题**不同构**：`zh.mzmgow.ods.tavern` ↔「Tavern - 简&繁中文汉化包」
- `rwzh.chinesepack.X` → 工坊上的「`X zh-pack`」系列（边缘汉化组同一作者）
- `athelas.medievaltotalrim.*` 有**新旧两套命名**：旧「Medieval Kingdoms」→ 新「Medieval Total Rim」，订阅要按游戏版本二选一
- `shavius.vce.zh` / `.vbe.zh` / `.vbookse.zh` → Vanilla Cooking / Brewing / Books Expanded 的汉化
- `zh.vanillaexpanded.vchemfuele` → Vanilla **Chemfuel** Expanded（`v` 前缀 + 缩写 + `e` 后缀 = `v<name>e`）

### 6e. ★ Steam CDN 匿名下载的不稳定规律（2026-10-08 实测）

- 单条 **5 分钟硬超时**（时间戳精确到 5m01s），`ERROR! Timeout downloading item <id>`。
- **同一 steamcmd 会话内，第 2 条起必超时**；第 1 条常能成功。
  → **必须每个 ID 一个独立 steamcmd 会话**，不能用一个 runscript 跑几十个。
- `Insufficient Privilege` 与 `Timeout` **都是瞬态的，直接重试即可**。真正无解的是 `File Not Found` / API `result=9`。
- ⚠️ **Bash 工具现在会瞬时杀掉 steamcmd**（`exit 127`，只来得及打印 `Redirecting stderr to ...`）。
  → ✅ 用 **PowerShell 工具 + WMI 启动 cmd 批处理**（脱离沙箱 Job Object）：
  ```powershell
  ([wmiclass]'Win32_Process').Create('cmd.exe /c C:\SteamCMDData\dl-loop.cmd')
  ```
  `dl-loop.cmd` 内 `for /f` 遍历 ID 列表，每个 ID 重写 `dl-one.txt` 后独立调用一次 steamcmd，结果 `echo %%i OK >> dl-cmd-result.txt`。
  进度**只能靠文件内容判断**（PowerShell 工具输出常被吞）。


### 7. 拷到别的电脑

`<前缀>\steam\steamapps\workshop\content\294100\<工坊ID>\` 里每个文件夹就是标准 mod 结构（含 `About\About.xml`），
**整个文件夹直接复制进 `RimWorld\Mods\` 即可**，文件夹名保持数字 ID 不影响识别。

## 排错速查

| 现象 | 原因 | 处理 |
|---|---|---|
| `ERROR! Download item xxx failed (Failure)`（立即） | 该 mod 锁匿名 | 换 mod；RimSort 无解（写死 anonymous） |
| `ERROR! ... failed (Insufficient Privilege)` | **瞬态**，不是「锁匿名」 | **直接重试**。实测 3/3 重试成功 |
| `ERROR! Timeout downloading item xxx` | 瞬态（CDN 卡住，约 5 分钟一项） | **直接重试**。实测 3/3 重试成功 |
| `File Not Found` / API `result=9` | 工坊已删 | 找替代，无解 |
| `SteamCMD not found` | 前缀填错（填到了 `steamcmd` 子目录） | 前缀填 `<前缀>` 本身 |
| 下载成功但游戏里看不到 | junction 没建 / Mods 路径错 | 查 `<前缀>\steam\steamapps\workshop\content\294100` 是否为链接 |
| RimSort 被 Defender 删 | Nuitka 未签名误报 | 加白名单，官方 FAQ 确认非恶意 |
| 更新检测失灵 | `.acf` 被清空 | 重下任一 mod 重建 |
| 首次跑 steamcmd 后没下载 | 自更新完就退出了（exit 7） | 再跑一次 |
| `failed (I/O Operation Failed)` | **并发跑了两个 steamcmd 实例**（争抢 depotcache/appcache） | 串行执行；要并行必须用**完全独立的 steamcmd 安装目录**，不只是独立前缀 |
| 批量下载中途出错漏项 | — | 直接重跑同一 runscript，幂等，会跳过已下好的 |
| **steamcmd 秒退：只打印 `Redirecting stderr to ...`，exit 127 / 被 SIGTERM** | **输出走了管道或被前台捕获**（`\| tail`、`\| grep`、直接跑不重定向）。沙箱会把 steamcmd 的子进程回收 | **永远重定向到文件**：`./steamcmd.exe +runscript X.txt > out.txt 2>&1`。绝不用管道，绝不裸跑。这是最高频的假故障 |
| 想统计下载结果时 grep 到 0 条 `Success` | steamcmd 把正文写进 `<steamcmd>\logs\console_log.txt`，stdout 只有一行 `Redirecting stderr` | 统计要看 `logs\console_log.txt`（或重定向文件），不是 stdout |

## 环境探测清单（判断用户处境）

```bash
# 游戏在哪 / 有没有 Steam
ls -d "/c/Program Files (x86)/Steam/steamapps/common/RimWorld" /c/GOG*/RimWorld /c/Program\ Files/Epic\ Games/RimWorld 2>/dev/null
ls -d /c/Users/*/AppData/LocalLow/"Ludeon Studios" 2>/dev/null   # 存在=跑过游戏
ls -d /c/Users/*/AppData/LocalLow/*RimWorld* 2>/dev/null
```

- 没有 `LocalLow\Ludeon Studios` → 本机从未启动过 RimWorld，RimSort 的位置设置填不了，必须先确认游戏路径。
- 用户 mod 列表常在 `Downloads\*.xml`（ModsConfig 导出）——注意那是 **packageId**，不是工坊 ID，不能直接用于 steamcmd。

## 平台操作注意（本机已验证的坑）

- 从 Bash 调 `powershell.exe` / `cmd` / `wmic` 会被沙箱拦 → 用 PowerShell 工具。
- PowerShell 工具的 stdout 常被吞 → 靠 exit code + Bash 验证副作用。
- `Expand-Archive` 的进度条会把输出刷成几百 KB 垃圾 → 不要在 PowerShell 里读它的输出。
- 下载二进制到 Windows 路径用 PowerShell `Invoke-WebRequest`；`curl -o` 写 Windows 路径会 `(23) client returned ERROR`。curl 到 `/tmp` 可用。
- Git Bash 的 `/tmp` = `C:\Users\<user>\AppData\Local\Temp`，但 `Read`/`Write` 把 `/tmp/x` 解析成 `C:\tmp\x` → 跨工具读写一律用真实 Windows 路径。
