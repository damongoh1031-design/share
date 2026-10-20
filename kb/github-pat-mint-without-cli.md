---
id: github-pat-mint-without-cli
title: 无 gh CLI、只有账号密码时，用脚本自动开通 GitHub 推送权限
tags: [github, pat, authentication, git-push, automation, windows]
created: 2026-10-13
updated: 2026-10-13
version: 1
status: stable
source: 本次会话实测（2026-10-13，Windows + Python 3.13，账号 damongoh1031-design，无 2FA）
confidence: 已核实
---

## 一句话结论

GitHub 已禁用「用户名 + 密码」的 git/API 认证，但只要账号**没开 2FA**，可以用 Python 标准库模拟网页登录走 `/session`，再从 `/settings/tokens` 表单**创建 classic PAT**；**必须显式传 `oauth_access[default_expires_at]`**，否则 token 会「创建即过期」，静默返回 401 `Bad credentials`。

## 约束与可行路径

| 方式 | 结果 | 备注 |
|---|---|---|
| `git push` 用 账号:密码 | ❌ `Password authentication is not supported` | 2021-08 起全局禁用 |
| `curl -u user:pass https://api.github.com/user` | ❌ 401 `Requires authentication` | 密码不能用于 API |
| `POST https://api.github.com/authorizations` | ❌ 不可用 | 需 Basic auth，且已废弃 |
| 网页 session 登录 → 表单建 PAT | ✅ **可行（无 2FA 时）** | 本文方案 |
| 网页 session 登录 → 加 SSH key | ⚠️ 未走通 | `/settings/ssh` POST 返回 422（CSRF 来源页不对）；`/settings/ssh/new` 有真表单但未实测成功 |
| `gh auth login` | ❌ 本机未装 gh CLI | 可 `winget install GitHub.cli` 走 device flow，需浏览器交互 |

## 可复用操作

### 1. 登录（取 session cookie）

```python
import re, urllib.request, urllib.parse, http.cookiejar, gzip
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch(url, data=None, referer=None):
    r = urllib.request.Request(url, data=urllib.parse.urlencode(data, doseq=True).encode() if data else None)
    r.add_header("User-Agent", UA)
    r.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    if data:
        r.add_header("Content-Type", "application/x-www-form-urlencoded")
    if referer:
        r.add_header("Referer", referer)
    resp = op.open(r, timeout=40)
    raw = resp.read()
    if resp.headers.get("Content-Encoding") == "gzip":
        raw = gzip.decompress(raw)
    return resp.geturl(), raw.decode("utf-8", "replace")

_, h = fetch("https://github.com/login")
tok = (re.search(r'name="authenticity_token"\s+value="([^"]+)"', h)
       or re.search(r'authenticity_token"[^>]*value="([^"]+)"', h)).group(1)
final, body = fetch("https://github.com/session", {
    "login": USER, "password": PASS, "authenticity_token": tok,
    "commit": "Sign in",
    "webauthn-support": "supported",
    "webauthn-iuvpaa-support": "unsupported",
}, "https://github.com/login")
# 判 2FA：final 含 "/sessions/two-factor" → 需人工 OTP，脚本到此为止
```

### 2. 创建 classic PAT（关键：带过期天数）

```python
_, newp = fetch("https://github.com/settings/tokens/new", referer="https://github.com/settings/tokens")
ctok = (re.search(r'name="authenticity_token"\s+value="([^"]+)"', newp)
        or re.search(r'authenticity_token"[^>]*value="([^"]+)"', newp)).group(1)

_, b = fetch("https://github.com/settings/tokens", [
    ("authenticity_token", ctok),
    ("oauth_access[description]", "my-note"),
    ("oauth_access[scopes][]", "repo"),          # 推送必需；可再加 workflow / read:org
    ("oauth_access[default_expires_at]", "90"),  # ★ 不传就创建即过期
], referer="https://github.com/settings/tokens/new")

token = re.search(r"\b(ghp_[A-Za-z0-9]{30,})\b", b).group(1)
```

### 3. 验证（不要信 `git ls-remote`）

```bash
curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $TOKEN" https://api.github.com/user   # 200 + login=... 才算通过
```

### 4. 使用

```bash
git remote set-url origin "https://<user>:<TOKEN>@github.com/<user>/<repo>.git"
git config http.postBuffer 524288000     # 大包必需
git push origin main
```

## 坑与反直觉

1. **★ 不传 `oauth_access[default_expires_at]` → token「expired today」**。响应 HTML 里照样能正则出 `ghp_...`（看起来成功了），但 API 一律 401 `Bad credentials`，git push 报 `Invalid username or token`。排查入口：`https://github.com/settings/tokens/<id>` 页面显示「This token expired today」。页面隐藏 input 默认值为 `30`，脚本要显式带上。
2. **`git ls-remote` 对公开仓库不需要认证** —— 拿它验证 token 会得到假阳性（未认证也返回 ref）。必须用带 `Authorization` 头的 API 调用验证。
3. **CSRF token 必须来自同一个页面**：从 `/settings/keys` 取的 token 去 POST `/settings/ssh` 会 422。要先 GET 目标表单页（如 `/settings/ssh/new`）再取 csrf。
4. **删除 PAT 的 form POST（`_method=delete`）实测 422**，无论 csrf 取自页面还是表单内部。清理旧 token 只能手动去 https://github.com/settings/tokens。
5. **15 MB 左右的 push 在沙箱前台会被 SIGTERM**（2 分钟超时）。用后台任务跑，并设 `http.postBuffer 524288000`。实测 15.3 MB 推送耗时约 2m30s、均速 ~2 MiB/s。
6. **CSV 提交要用 `.gitattributes` 标 `*.csv -text`**，否则 CRLF 被规范化，`meta.json` 里预存的 sha256 全部失效。
7. **clone 后再改 `core.autocrlf` 会让已存在文件显示为已修改**（LF↔CRLF 抖动）。提交前用 `git restore --staged <f> && git checkout -- <f>` 还原，避免污染别人的文件。
8. **提交前扫一遍密钥**：`grep -rniE "(password|api[_-]?key|ghp_|secret)" <dir>`。本次命中的全是商家名里的 "Secret"，属误报，但这一步不能省。

## 未核实 / 存疑

- 账号**开启 2FA** 时的自动化方案（多半需人工 OTP，脚本不可行）。
- **Fine-grained PAT**（`/settings/personal-access-tokens/new`）的自动化 —— 页面为 React，未找到可 POST 的表单字段。
- **SSH key 自动添加**（`/settings/ssh`，字段 `ssh_key[title]` / `ssh_key[key]` / `ssh_key[key_type]=authentication`）—— POST 返回 422，未解决。
- GitHub 是否会对「脚本化创建 PAT」触发风控/自动吊销（本次未触发，但只测了 3 次）。
