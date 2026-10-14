# DB1 CallerID 验证汇总 —— 三批共 22 个号码

> 实测日期：2026-10-02 · 全部号码与名字由用户提供
> 目的：量化 `phone-number-lookup` 的 DB1（aunumber.com / CallerID）在真实号码上的表现

---

## 一、三批测试集

| 批次 | 号码数 | 名字来源 | 有返回率 |
|---|---|---|---|
| 第一批 | 4 | 用户自有联系人（来源未标注） | 2/4 = 50% |
| 第二批 | 9 | **Truecaller**（用户明确说明） | 9/9 = 100% |
| 第三批 | 9 | 格式同 Truecaller（`MS`/`MR` + 全大写），来源未明确 | 7/9 = 78% |
| **合计** | **22** | — | **18/22 = 82%** |

---

## 二、总表（22 个号码）

### 第一批（4）

| 号码 | 已知名字 | DB1 返回 | 判定 |
|---|---|---|---|
| `0123355873` | roland leong | （空） | ✗ 无数据 |
| `0122071768` | dato ricky lim | `Dato Dr Ricky` | ◐ `ricky`（`dato` 是头衔，剥离后不计） |
| `0123013006` | martin lim | （空） | ✗ 无数据 |
| `0192385938` | marvin lee | `Mr Malvin` | ◐ `marvin` |

### 第二批（9，名字来自 Truecaller）

| 号码 | Truecaller | DB1 返回 | 判定 |
|---|---|---|---|
| `0122860106` | LOW CHI CHENG | `Loh lawyer` | ✅ `Loh`≈`Low` + **职业标签** |
| `0123883460` | NEW CHOY WAH | `AH WAH-MAY` | ◐ `wah` |
| `0122133606` | LIZA YAP SURBANA | `Liza Yap` | ✅ **子串** |
| `0122901021` | E MAHIDIN | `abe emy` | ✗ |
| `0123878872` | LINDA LIM VG | `Linda Lim` | ✅ **子串** |
| `0122958331` | ROSLI NORDIN | `rosli smvb` | ◐ `rosli` |
| `0162084648` | EDDIE LIM | `Mr Eddie PA` | ◐ `eddie` |
| `0169160123` | R PJ FIVESTONES MARCH | `Hahn V8 SCM/M` | ✗ |
| `0172706676` | BOON HONDA CITY | `boon han lim` | ◐ `boon`（两库完全不同） |

### 第三批（9）

| 号码 | 已知名字 | DB1 返回 | 判定 |
|---|---|---|---|
| `60124753903` | MS YONG LAI SUN | （空） | ✗ 无数据 |
| `122022913` | MR POH WEI YIN | `Nova Saujana-S/L Christ` | ✗ |
| `0128590583` | WONG YI JUN | （空） | ✗ 无数据 |
| **`60165014911`** | GABERIAL NG CHEE HUI | **`智辉`** | ✅ **拼音命中 `hui`**（跨语言） |
| `0182002095` | LEE KAR YEN | `amanda samsung` | ✗ |
| `0136666165` | LIM | `daniel lim @pll9202` | ✅ `lim` |
| `0103990894` | TAN YING FEN | `ah ying` | ◐ `ying` |
| `193879412` | MS NG YOKE LAN | `Lotus Power : Angie Ng` | ◐ `ng` |
| **`60197527397`** | MR ENG JING HAO | **`Eng Jing Hao`** | ✅✅ **token 全中** |

---

## 三、准确率统计（22 个号码）

| 指标 | 数量 | 比例 |
|---|---|---|
| **有返回（`name` 非空）** | **18 / 22** | **82%** |
| token 命中 ≥1 个 | 14 / 22 | 64% |
| 子串包含（DB1 是已知名的子串） | 4 / 22 | 18% |
| **token 全中** | **2 / 22** | 9.1% |
| 完全一致（归一化相等） | 0 / 22 | 0% |
| 重查可复现 | 22 / 22 | **100%** |

---

## 四、★ 本次新增的两个关键发现

### 1. 「token 全中」案例 —— DB1 确实会给完整准确的全名

```
DB1:  Eng Jing Hao
已知: MR ENG JING HAO     →  剥离 MR 称谓后完全一致
```

22 个号码里有 **2 个 token 全中**：

- `Eng Jing Hao` = `MR ENG JING HAO`（剥掉 `MR` 称谓）
- `daniel lim @pll9202` ⊃ `LIM`（已知名字只有 1 个 token，命中即全中）

**这推翻了"DB1 只给名不给姓"的过度概括。** 更准确的表述是：
DB1 的记录**完整度参差** —— 有的给全名（`Eng Jing Hao`），有的只给简称（`Liza Yap`），有的给别名（`ah ying`）。

> ⚠️ **比对前必须剥离称谓词**（`MR`/`MS`/`MRS`/`DR`/`DATO`/`PUAN`/`ENCIK` 等）。
> Truecaller 常带前缀（`MR ENG JING HAO`），DB1 常不带（`Eng Jing Hao`），
> 不剥离会把「实质全中」误判成「缺一个 token」。
> **但 `Tan`/`Lim`/`Ng` 这类同时是姓氏的词不能剥离。**

### 2. 首个「跨语言命中」案例 —— DB1 库里存中文备注

```
DB1:  智辉                  →  拼音 zhihui
已知: GABERIAL NG CHEE HUI  →  token `HUI` 命中拼音串 `zhihui` 的 `hui`
```

`Chee Hui` 的中文写法就是「智辉」。**DB1 库里同时存在中文字符和罗马拼音两种备注**，
而 Truecaller 只有罗马拼音。

**工程含义**：跨库比对**必须过拼音**，否则这条会被判为"不匹配"。
本项目的 `verify_callerid.py` 已集成 `pypinyin` 做这一步（未装时自动降级，不报错）。

---

## 五、DB1 备注的格式规律

把 18 条有返回的记录归类：

| 类型 | 例子 | 占比（约） |
|---|---|---|
| **纯人名** | `Eng Jing Hao`、`Liza Yap`、`Linda Lim`、`Dato Dr Ricky` | ~40% |
| **简称/别名** | `ah ying`、`rosli smvb`、`abe emy`（abe = 马来语"大哥"） | ~25% |
| **人名 + 职业/关系** | `Loh lawyer`、`Mr Eddie PA`、`Mr Malvin` | ~20% |
| **组织/商家 + 人名** | `Lotus Power : Angie Ng`、`Nova Saujana-S/L Christ` | ~10% |
| **中文名** | `智辉` | ~5% |
| **脏数据** | `rswelth. id : rs122867 / pword : rosdi74` | 极少数 |

**结论：DB1 存的是「来电者在这位用户的通讯录里是什么身份」**，不是身份档案。
所以会出现"公司名 : 人名"、"职业标签"、"马来语昵称"这类形态。

---

## 六、修正此前的一个过度概括

上一批（9/9 有返回）之后曾写：

> ❌ "Truecaller 有名字的号码 → DB1 **必然**有返回"

**第三批推翻了"必然"**：7/9。三批合并后：

> ✅ **修正为：DB1 的覆盖率与 Truecaller **高度相关但非必然**（22 个号码中 18 个有返回 = 82%）。
> Truecaller 无名字时，DB1 基本也不会有 —— 因为两库都是「被存进过通讯录」的号码。**

**实用流程仍然成立**：先在 Truecaller 查；没有名字，就不必再跑 DB1。

---

## 七、最终结论

| 问题 | 答案 |
|---|---|
| DB1 能查到名字吗？ | **能，82% 的号码有返回** |
| 返回的名字准吗？ | **是真实的众包备注**（64% 有 token 命中、100% 可复现），但**不是实名** |
| 会缺东西吗？ | **会** —— 有的只给简称（`Liza Yap`）、有的带职业标签（`Loh lawyer`）、有的存中文（`智辉`） |
| 能给出全名吗？ | **能**（`Eng Jing Hao` = `ENG JING HAO`），但不是每条都完整 |
| 能和 Truecaller 互补吗？ | **能** —— DB1 偏口语化备注/职业线索，TC 偏规范全名 |
| 是实名吗？ | ❌ **不是**。要实名只能报警（PDRM / NSRC **997**）或法院披露令（Norwich Pharmacal order） |

---

## 八、复现方式

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
R="C:/Users/Admin/AppData/Local/Temp/osintrepos/phone-number-lookup"

"$PY" verify_callerid.py --repo "$R" --recheck \
  "60197527397|MR ENG JING HAO" \
  "60165014911|GABERIAL NG CHEE HUI" \
  "0122133606|LIZA YAP SURBANA"
```

**依赖**：`pypinyin`（已装入 osint venv）—— 未安装时中文匹配自动降级，不影响其他功能。

**匹配规则**（三级 + 拼音 + 称谓剥离）：
1. 全串精确匹配
2. 子串包含
3. **token 级模糊匹配** —— 编辑距离 ≤1，**≥3 字母**（华语姓名罗马化有变体：`Loh`/`Low`、`Tan`/`Tang`）
4. **中文拼音匹配** —— 中文备注转拼音后与罗马拼音 token 比对（`智辉` → `zhihui` ⊃ `hui`）
5. **剥离称谓词** —— `MR`/`MS`/`MRS`/`DR`/`DATO`/`PUAN`/`ENCIK` 等不参与比对
   （`Tan`/`Lim`/`Ng` 这类**同时是姓氏**的词不能剥）
