# Truecaller 非官方 OTP 登录 —— 本机实测报告（失败，路径已死）

> 实测日期：2026-10-02 · 目标号码 `+60102261791` · 方式：`truecallerpy` v1.0.3（Python 版 `truecallerjs`）
> **一句话结论：OTP 根本没发出去。这不是配置问题，是 Truecaller 服务端已封堵该自动化路径，项目已被官方标记为 broken/deprecated。**

---

## 一、先回答你最关心的：手机收到短信了吗？

**没有。请不要等了。**

服务端返回的是：

```json
{
  "status_code": 200,
  "data": {
    "status": 20003,
    "message": "Verification failed",
    "domain": "noneu",
    "requestId": "bfad2fb2-897a-46b3-9cbb-d52f27117c52"
  }
}
```

**判读依据**：正常发出的响应必须带 `method`（发送渠道，如 `sms`）和 `tokenTtl`（有效期秒数）。
本次响应**两个字段都不存在** → 服务端在「选定发送渠道」这一步就中止了，**短信从未进入投递队列**。

---

## 二、四组实验，逐条排除可能性

### 实验 1：是不是伪造的客户端版本太老？

库里写死的是 `Truecaller/11.75.5 (Android;10)`，而 Google Play 实测当前版本是 **14.43.8 / 15.3.10** —— 差 3–4 个大版本。

**换 4 组指纹重试**（含最新版）：

| 组 | UA | app 版本 | Android | 结果 |
|---|---|---|---|---|
| A | `Truecaller/11.75.5 (Android;10)` | 11.7.5 | 10 | **20003** |
| B | `Truecaller/14.43.8 (Android;13)` | 14.43.8 | 13 | **20003** |
| C | `Truecaller/15.3.10 (Android;14)` | 15.3.10 | 14 | **20003** |
| D | `okhttp/4.9.2`（不伪装） | 14.43.8 | 13 | **20003** |

→ **不是版本号问题。**

### 实验 2：是不是号码本身的问题？

| 号码 | 类型 | HTTP | status / message |
|---|---|---|---|
| `+60312345678` | 马来西亚**固话**（不可能收短信） | **400** | `40003` / **Invalid phone number** |
| `+601999999999` | 无效手机前缀 `199` | **200** | `20003` / Verification failed |
| `+60102261791` | **你的号码** | **200** | `20003` / Verification failed |

→ 两个关键推论：
1. **请求被正常解析了** —— 固话被正确识别并单独报 `Invalid phone number`，说明 `clientsecret`、body 结构、JSON 格式**全部通过校验**。
2. **无效前缀与你的真实号码结果完全相同** → **20003 与号码无关**，是针对**客户端身份**的拒绝。

### 实验 3：社区是否也这样？

- `sumithemmadi/truecallerjs`（881★）：**34 条** "Verification failed" issue，多条标题直接写着 **"NOT Sending OTP"**
  - `#165`（2026-07-27 开）："VERIFICATION FAILED, not sending OTP" → 到 **2026-09-17 仍有人跟帖**
  - `#162` 评论区：**"This repo is no longer maintained."**
- `sumithemmadi/truecallerpy`（153★）：`#42` "Verification failed"、`#43`、`#30` "It's stop working"
- 仓库活跃度：`truecallerpy` 最后实质提交 **2023-09-07**；`truecallerjs` 停在 **2023-11-29**

### 实验 4：跨国对照（截图证据）

`truecallerpy#42` 报告者用**印度号码 `+91 9…`**，得到的是：

```json
{"status":20003,"message":"Verification failed","domain":"noneu","requestId":"ecac4231-daa8-4f9e-aac0-f48e2ecf19bf"}
```

**与我的马来西亚号码响应逐字段一致**（仅 requestId 不同）→ 跨国、跨号码，行为完全统一。

---

## 三、权威判定（来自项目贡献者的 PR）

`sumithemmadi/truecallerjs` **PR #157**（2026-02-07）正文与 README diff 原文：

> ### Known Limitations
> Despite these fixes ensuring the client sends technically correct requests (**receiving `20003 Success` from the API**), Truecaller's backend appears to be **silently blocking SMS delivery for requests originating from this library**. The documentation has been updated to reflect this reality and mark **the automated login feature as deprecated/non-functional**.

> ### CRITICAL NOTICE (2025): Project Currently Non-Functional
> Truecaller has implemented **strict server-side restrictions** that block the API endpoints used by this library.
> **Status:**
> - `truecallerjs login`: Request succeeds (**Status 20003**), but **OTP is never delivered**.
> - Workarounds: Previously fetching `installationId` from web sessions was possible, but **recent reports suggest this method is also unreliable** or no longer compatible with the specific API endpoints this library uses.
> **Conclusion:**
> As of Feb 2026, this library should be considered **broken/deprecated** until a new method for unofficial access is discovered. **Use official Truecaller Business SDKs for reliable service.**

PR 里还试过这些「修复」（都**没能解决**投递问题，只是让请求更「正确」）：
- 端点从 `account-asia-south1` 改为 `account-noneu`
- UA 改为 `Truecaller/12.0.0 Android`
- 用真实 Xiaomi 设备 profile 替代随机字符串
- CLI 把 `20003` 当作「成功」接受

→ **`20003` 现在的语义 = 「请求已受理，但静默不投递短信」**。

---

## 四、为什么封得住？（技术推断）

服务端无法区分「真实 App」与「伪造 HTTP 客户端」时，最可能的判别点是 **Play Integrity / SafetyNet attestation**：

| 校验项 | 纯 HTTP 伪造能否满足 |
|---|---|
| `clientsecret` | ✅ 能（硬编码，已验证仍有效） |
| UA / app 版本 / 设备型号 | ✅ 能（已试 4 组） |
| body 结构 / JSON 字段 | ✅ 能（固话对照证明被正常解析） |
| **Play Integrity token** | ❌ **不能** —— 需要 Google 签名的设备证明，必须在真机 + 已上架应用内生成 |
| **应用签名证书指纹** | ❌ **不能** —— 需 Truecaller 官方 APK 的签名 |

这解释了为什么「请求技术上完全正确」却拿不到短信：**缺的是密码学层面的设备证明，不是参数。**

---

## 五、替代路径（按可行性排序）

| # | 路径 | 可行性 | 说明 |
|---|---|---|---|
| **1** | **DB1 / aunumber 众包库** | ✅ **立即可用** | 已实测 22 个号码，**82% 有返回**、token 命中 64%、重查可复现 100%。**这是目前唯一实际有数据的源** |
| 2 | 从**真机**提取 `installationId` | ⚠️ 需设备权限 | 装 Truecaller App 登录后，用 `adb backup` 或 root 提取 App 私有存储里的 `installationId`。拿到后 `search5` 端点仍可用（已测：假 token→401，端点正常）。**违反 ToS** |
| 3 | Truecaller Web 版抓包 | ❌ **本机不可行** | `web.truecaller.com` 在本机 **DNS 不存在**（Non-existent domain，走 Maxis DNS），curl 走代理 `CONNECT tunnel failed 502`。且 PR#157 已称此法「unreliable」 |
| 4 | 官方 Business SDK | ❌ **不适用** | 只能验证**你自己 App 的用户**，返回登录者本人资料，**不能查任意号码**（见 `Truecaller登录方式对比-OAuth-SDK-vs-OTP.md`） |
| 5 | omkarcloud / Twilio 等商业 API | ❌ | omkarcloud 只给运营商不给姓名；Twilio Caller Name 仅美国 |
| 6 | **报警 / 法院令** | ✅ **唯一合法拿实名** | PDRM / NSRC **997**，或 Norwich Pharmacal order |

---

## 六、我的建议

**放弃 Truecaller 这条线。** 它已经不是「配置没调对」，而是**服务端从架构上封死了非官方客户端**——除非你愿意在真机上装 App 并提取凭据（违反 ToS，且账号有封禁风险）。

**要做号码反查，用 DB1（aunumber）**。它虽然覆盖不如 Truecaller，但：
- 已实测可用，22 个号码 82% 有返回
- 覆盖率与 Truecaller **高度相关**（TC 有名字的，DB1 大概率也有）
- 不需要任何账号、不违反任何条款

⚠️ 但请记住边界：**DB1 返回的是「某人通讯录里的备注名」，性质是线索，不是实名身份。** 任何合法渠道都拿不到「号码 → 机主实名」，要实名只能走报警。

---

## 七、复现命令

```bash
PY="C:/Users/Admin/.workbuddy-ai/binaries/python/envs/osint/Scripts/python.exe"
cd "C:/Users/Admin/WorkBuddy AI/2026-10-02-12-08-02"

"$PY" tc_inspect.py            # 库版本 + clientsecret + 端点常量
"$PY" tc_login.py              # ★ 发 OTP（会真发短信；本次返回 20003 未发出）
"$PY" tc_retry_fingerprint.py  # 实验1：4 组客户端指纹对照
"$PY" tc_control_number.py     # 实验2：固话 / 无效前缀 / 真实号码 对照
"$PY" tc_diag_20003.py         # 实验3：仓库活跃度 + issue 检索
"$PY" tc_read_issues.py        # 实验3：读关键 issue 正文与评论
"$PY" tc_chase_fix.py          # 实验4：PR#157 + 下载 issue 截图
"$PY" tc_check_web.py          # 替代路径：Web 版可达性
```

> ⚠️ `tc_login.py` / `tc_retry_fingerprint.py` 会向 Truecaller 发真实请求。**本次已证明不会真发短信**，但重跑请自行判断。

### 附：本机网络环境的一个发现

`nslookup web.truecaller.com` 返回的 DNS 服务器是 **`ns8.maxis.net.my`**（马来西亚 Maxis）。
→ 本机 DNS 解析走马来西亚 ISP。这修正了我在 `Tellows-Truecaller-API可用性实测.md` 里「本机是中国 IP」的假设。
（不影响 451 归因结论 —— 那是由「假 token→401」这组对照独立证明的。）
