#!/usr/bin/env bash
# gog_reauth.sh — gog（Google Workspace CLI）OAuth 重新授权，全自动
#
# 为什么需要这个脚本：
#   gog 的 refresh token 会过期（实测约 6–7 天）。过期后所有 sheets/docs 命令报
#   "refresh token expired or revoked: invalid_grant"。重新授权要过 Google OAuth，
#   而沙箱环境有两个坑：
#     ① 沙箱把每条命令的进程放进 Job Object，命令结束即回收 → gog 的本地回调监听活不过一条命令
#     ② Windows 下 gog --manual 读 stdin 会报 "read /dev/stdin: The handle is invalid"（FIFO 不兼容）
#
# 解法（关键三点）：
#   1) 用 `--remote --step 1/2` 而不是 `--manual`：state 会落盘到
#      %APPDATA%\gogcli\oauth-manual-state-<state>.json，跨命令不丢 PKCE verifier
#   2) 用 CDP 接管已登录的 Chrome 走完同意流程（选账号 → warning → id → consent）
#   3) 对「授权标签本身」开 Network.enable 监听，从
#      Network.requestWillBeSent / Page.frameRequestedNavigation 抓
#      http://127.0.0.1:<port>/oauth2/callback?code=... （browser 级监听会漏）
#      注意：回调页因监听不在会显示 ERR_CONNECTION_REFUSED（chrome-error://），
#      原始 URL 会被吞掉 —— 所以必须在导航发生前就挂好监听，不能事后从页面读。
#
# 用法:
#   bash gog_reauth.sh [email]
set -uo pipefail

GOG="C:/Users/Admin/.workbuddy-ai/bin/gog/gog.exe"
NODE="C:/Users/Admin/.workbuddy-ai/binaries/node/versions/22.22.2-6/node.exe"
WS="C:/Users/Admin/WorkBuddy AI/2026-09-29-12-21-44"
TMPD="${TEMP:-C:/Users/Admin/AppData/Local/Temp}"
EMAIL="${1:-jsng0819@gmail.com}"
SERVICES="drive,sheets"

OUT="$TMPD/gog_auth_out.txt"
REDIR="$TMPD/gog_redirect_url.txt"
rm -f "$REDIR" "$OUT"

# --- 1) 生成授权 URL（state 落盘）---
"$GOG" auth add "$EMAIL" --remote --step 1 --services="$SERVICES" --force-consent > "$OUT" 2>&1
URL="$(grep -o 'https://accounts\.google\.com/o/oauth2/auth[^[:space:]]*' "$OUT" | head -1)"
[[ -n "$URL" ]] || { echo "❌ 未生成授权 URL"; cat "$OUT"; exit 1; }
echo "✅ 授权 URL 已生成"

# --- 2) 在 Chrome 里打开（先清掉旧授权标签）---
"$NODE" -e "
const CDP='http://127.0.0.1:9222';
(async()=>{
  const l=await (await fetch(CDP+'/json/list')).json();
  for(const t of l){ if(t.type==='page'&&/accounts\.google\.com|chrome-error/.test(t.url||'')) await fetch(CDP+'/json/close/'+t.id).catch(()=>{}); }
  const r=await fetch(CDP+'/json/new?'+encodeURIComponent(process.argv[1]),{method:'PUT'});
  console.log('已打开授权页:', (await r.json()).id);
})();
" "$URL"
sleep 4

# --- 3) 挂标签级网络监听 + 驱动同意流程 ---
"$NODE" "$WS/fx_g_tab.mjs" "$EMAIL" 2>&1 | tail -20

# --- 4) step 2 交换 token ---
if [[ -s "$REDIR" ]]; then
  REDIRECT_URL="$(tr -d '\r\n' < "$REDIR")"
  "$GOG" auth add "$EMAIL" --remote --step 2 --auth-url "$REDIRECT_URL" --services="$SERVICES" --force-consent 2>&1 | tail -6
  echo "--- 验证 ---"
  "$GOG" auth status 2>&1 | grep -E "^account|^client" || true
else
  echo "⚠️ 未捕获回调 URL（同意流程可能未完成）"
fi
