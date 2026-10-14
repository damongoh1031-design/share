# CallerID（DB1）准确率验证 —— 4 个已知答案号码

> 实测日期：2026-10-02 · 测试集由用户提供（号码 + 真实名字），非自造样本
> 目的：用 ground truth 量化 `phone-number-lookup` 的 DB1（aunumber.com）到底准不准

---

## 一、测试集与总表

| 号码 | 已知真实名字 | **DB1 返回** | token 命中 | libphonenumber | busuk.my | Semak Mule | CallApp |
|---|---|---|---|---|---|---|---|
| `0123355873` | roland leong | **（空）** | — | Maxis | Maxis · 无报告 | 无记录 | No Data |
| `0122071768` | dato ricky lim | **`Dato Dr Ricky`** | ✅ `dato` `ricky` | Maxis | Maxis · 无报告 | 无记录 | No Data |
| `0123013006` | martin lim | **（空）** | — | Maxis | Maxis · 无报告 | 无记录 | No Data |
| `0192385938` | marvin lee | **`Mr Malvin`** | ≈ `marvin`（Malvin 编辑距离 1） | Celcom | Celcom · 无报告 | 无记录 | No Data |

**重查可复现：4/4** —— 每个号码连查两次，返回完全一致。说明空返回是**稳定的"无数据"**，不是接口抖动。

---

## 二、准确率统计（诚实口径）

| 指标 | 结果 |
|---|---|
| 有返回（`name` 非空） | **2 / 4 = 50%** |
| 名字**部分**命中（≥1 个 token 对上） | **2 / 4 = 50%** |
| 名字**完全**正确（含姓氏） | **0 / 4 = 0%** |
| token 全中 | 0 / 4 |
| 结果可复现 | 4 / 4 = 100% |
| 其他库（CallApp/Eyecon）有返回 | 0 / 4 |

**一句话结论：DB1 能命中一半号码，但命中的记录都只给了"名"、没给"姓"。**

---

## 三、逐条分析

### ① `0123355873` → 空
库里没有该号码的 `name`。同号码重查仍为空。

### ② `0122071768` → `Dato Dr Ricky` ／ 已知 `dato ricky lim`
- **命中**：`Dato`、`Ricky` 两个 token 完全一致。
- **缺失**：姓氏 `Lim`。
- **多余**：`Dr` —— 库里存的是 **`Dato Dr Ricky`**，比用户给的还多一个头衔。
  → 说明这不是"部分乱码"，而是一条**语义完整但版本不同**的通讯录备注。

### ③ `0123013006` → 空
库里没有该号码的 `name`。同号码重查仍为空。

### ④ `0192385938` → `Mr Malvin` ／ 已知 `marvin lee`
- **近似命中**：`Malvin` 与 `Marvin` **编辑距离 = 1**（第 3 位 `l` ↔ `r`）。
  - 两种可能：① 库里存的就是另一个拼法（Malvin 也是真实英文名）② 存的人记错/拼错。
- **缺失**：姓氏 `Lee`。
- 与 ② 一样，只有"名"没有"姓"。

---

## 四、★ 关键发现：为什么总是缺姓氏？

4 个样本里，**2 条有数据的记录全部缺姓氏**。结合此前 `Diana/1`、`Prof Lee` 两个样本，规律很清楚：

> **这个库存的是「来电方在用户通讯录里被存成什么」，而现实中大量人存联系人只存名不存姓。**

旁证：
- `Diana/1` 的 `/1` —— 不是兜底值，而是通讯录里的**编号**（"Diana 的第 1 个号码"），是常见的备注写法。
- `Kedai Makan Pak Chik`（完整商家名 + `Scam` 标签 + 329 次举报）—— 商家类记录反而完整，因为没人会给商家起简称。

**实践含义**：
- 该库对**"名"（given name）的覆盖明显好于"姓"（surname）**。
- 用它对**已有的假设做交叉确认**很有效（"这个 Ricky 是不是叫 Ricky Lim？"）；
- 用它**从零推出完整姓名**不可靠（永远可能只有名）。

---

## 五、★ 字段语义更正（推翻此前的解读）

拉出全部 6 个样本的原始 JSON 后，几个字段的真实含义与最初判断不同：

| 字段 | 此前的解读 | **实际语义（已验证）** |
|---|---|---|
| `old_tel_number` | "旧号码" | ❌ **就是查询号码本身的回显**。6/6 个样本全部等于输入号码（`+60123355873` 等），无信息量 |
| `belong_area` | "归属区域" | ⚠️ **默认值 `"Malaysia"`**。只有记录真有地址时才变具体（如 `"Tumpat, Malaysia"`）→ 值等于 `Malaysia` 时应视为"无区域信息" |
| `type_label` | 号码类型 | ⚠️ 是**社区标签**（如 `Scam`），不是线路类型。空 = 无标签 |
| `report_count` | — | 被举报次数。空 = 无举报记录 |
| `address` | — | 地址。空 = 无 |
| `name` | 机主姓名 | ⚠️ **众包备注名**，非实名（本次 2/4 有值） |
| `avater` | 头像 | 头像 URL（本次样本均为空） |

**只有 `0123456789` 是"完整记录"**：`Kedai Makan Pak Chik` + `Scam` + `329` 次举报 + 完整地址 `Chabang Empat, Tumpat, Malaysia`。
其余样本只有 `name` 和默认 `belong_area`，说明**大多数记录在库里是很稀薄的**。

---

## 六、结论与使用建议

| 判断 | 结论 |
|---|---|
| DB1 能不能查到名字？ | **能，但只有 50% 命中率，且通常只有名没有姓** |
| 返回的名字可信吗？ | **是真实的众包备注名**（2/4 部分命中、4/4 可复现），但**不是实名** |
| 能用它做什么？ | ✅ **验证假设**（已知可能是谁 → 交叉确认）；❌ 不能从零推出完整身份 |
| 其他库能补吗？ | ❌ CallApp（DB3）4/4 `No Data Found`；Eyecon 无图片；Sync.ME / Truecaller 已废 |
| 想拿完整实名？ | 只能走报警（PDRM / NSRC **997**）或法院披露令（Norwich Pharmacal order） |

**给这批号码的最终画像**（4 个号码）：
- 运营商：3 个 Maxis、1 个 Celcom（libphonenumber 与 busuk.my **完全一致**）
- **全部未被 PDRM Semak Mule 举报**（≠ 安全，只表示无公开投诉记录）
- **全部无社区风险报告**（busuk.my 风险等级 `Tidak Diketahui`）
- 众包库里：2 个有备注名、2 个无记录

---

## 七、复现方式

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
R="C:/Users/Admin/AppData/Local/Temp/osintrepos/phone-number-lookup"

"$PY" verify_callerid.py --repo "$R" --recheck \
  "0123355873|roland leong" \
  "0122071768|dato ricky lim" \
  "0123013006|martin lim" \
  "0192385938|marvin lee"

# 看完整原始字段
"$PY" verify_callerid.py --repo "$R" --json "0122071768|dato ricky lim"
```

`verify_callerid.py` 做三级对比：全串精确 → 子串包含 → **token 级模糊匹配**（编辑距离 ≤1）。
**加更多号码即可扩充测试集** —— 样本越多，这个准确率结论越可靠。
