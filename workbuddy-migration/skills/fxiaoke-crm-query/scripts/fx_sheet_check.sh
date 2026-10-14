#!/usr/bin/env bash
# fx_sheet_check.sh — 端到端：Google Sheets 号码列 → 纷享销客 CRM 查重 → 标记列回填
#
# 一条命令跑完「读表 → 校验 → 查询 → 行对齐映射 → 写回 → 读回验证」。
#
# 用法：
#   bash fx_sheet_check.sh --id <spreadsheetId> --sheet "01/10"
#   bash fx_sheet_check.sh --id <id> --sheet "01/10" --phone-col B --mark-col C --mark X
#   bash fx_sheet_check.sh --id <id> --sheet "01/10" --dry-run      # 只读表+体检，不查询不写回
#   bash fx_sheet_check.sh --id <id> --sheet "01/10" --resume       # 查询中断后续跑
#   bash fx_sheet_check.sh --id <id> --sheet "01/10" --reuse result.csv   # 复用已有结果，跳过查询
#
# 为什么用 shell 而不是 Node：
#   沙箱内 Node 进程无法 spawn 子进程（连调 node.exe 自身都报 EBUSY），
#   而 shell 可以正常串联 gog / node / python。故端到端编排放在 shell 层。
#
# 行对齐：按「行位置」映射；号码列中间的空行会写空标记，不会错位。
# 退出码：0 成功 / 1 参数或校验失败 / 2 CDP 连接失败 / 3 登录失效 / 4 遇鉴权或风控
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GOG="${GOG_CLI:-C:/Users/Admin/.workbuddy-ai/bin/gog/gog.exe}"
NODE="${NODE_BIN:-C:/Users/Admin/.workbuddy-ai/binaries/node/versions/22.22.2-3/node.exe}"
TMPBASE="${FX_TMP:-C:/Users/Admin/AppData/Local/Temp}"

ID=""; SHEET=""; PHONE_COL="B"; MARK_COL="C"; MARK="X"; DELAY="300"; OUT=""; REUSE=""
RESUME=0; DRY=0; FORCE=0; QUIET=0

usage() {
  cat <<'EOF'
用法: bash fx_sheet_check.sh --id <spreadsheetId> --sheet "<表名>" [选项]

  --id           spreadsheetId（必需，URL 里 /d/<这一段>/ 就是）
  --sheet        工作表名（必需，含 / 等字符会自动加单引号）
  --phone-col    号码所在列，默认 B
  --mark-col     标记写入列，默认 C
  --mark         命中标记，默认 X
  --out          结果 CSV 路径（固定路径才能 --resume），默认 ./fxsheet_<sheet>_result.csv
  --reuse <csv>  复用已有结果 CSV，跳过 CRM 查询
  --delay        查询间隔 ms，默认 300
  --resume       从上次进度续跑
  --dry-run      只读表 + 体检，不查询不写回
  --force        标记列已有非空值时仍强制写入（默认拒绝，防覆盖）
  --quiet        静默
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --id)          ID="${2:-}";          shift 2 2>/dev/null || shift;;
    --sheet)       SHEET="${2:-}";       shift 2 2>/dev/null || shift;;
    --phone-col)   PHONE_COL="${2:-B}";  shift 2 2>/dev/null || shift;;
    --mark-col)    MARK_COL="${2:-C}";   shift 2 2>/dev/null || shift;;
    --mark)        MARK="${2:-X}";       shift 2 2>/dev/null || shift;;
    --delay)       DELAY="${2:-300}";    shift 2 2>/dev/null || shift;;
    --out)         OUT="${2:-}";         shift 2 2>/dev/null || shift;;
    --reuse)       REUSE="${2:-}";       shift 2 2>/dev/null || shift;;
    --resume)      RESUME=1; shift;;
    --dry-run)     DRY=1; shift;;
    --force)       FORCE=1; shift;;
    --quiet)       QUIET=1; shift;;
    -h|--help)     usage; exit 0;;
    *)             echo "未知参数: $1" >&2; usage; exit 1;;
  esac
done

if [[ -z "$ID" || -z "$SHEET" ]]; then usage; exit 1; fi

log()  { [[ $QUIET -eq 1 ]] || echo "$@"; }
elog() { echo "$@" >&2; }

SAFE_SHEET="$(printf '%s' "$SHEET" | tr -c 'A-Za-z0-9._-' '_')"
[[ -n "$OUT" ]] || OUT="./fxsheet_${SAFE_SHEET}_result.csv"

TMP="$TMPBASE/fxsheet_$$"
mkdir -p "$TMP" || { elog "❌ 无法创建临时目录 $TMP"; exit 1; }
trap 'rm -rf "$TMP" 2>/dev/null || true' EXIT

log "📄 表 \"$SHEET\"  号码列 $PHONE_COL → 标记列 $MARK_COL（标记 \"$MARK\"）"

# ---------- 1. 读号码列 ----------
if ! "$GOG" sheets get -p "$ID" "'${SHEET}'!${PHONE_COL}1:${PHONE_COL}" > "$TMP/phones.tsv" 2>"$TMP/err.txt"; then
  elog "❌ 读取失败：$(cat "$TMP/err.txt" 2>/dev/null)"
  elog "   检查：spreadsheetId 是否正确 / gog 是否已授权（gog auth status）"
  exit 1
fi

N=$(awk 'NF{last=NR} END{print last+0}' "$TMP/phones.tsv")
if [[ "${N:-0}" -eq 0 ]]; then elog "❌ ${PHONE_COL} 列没有数据"; exit 1; fi
log "   号码列 $N 行"

EMPTY=$(awk -v N="$N" 'NR<=N && !NF{c++} END{print c+0}' "$TMP/phones.tsv")
[[ "$EMPTY" -gt 0 ]] && log "   ⚠️  ${EMPTY} 个空行 → 这些行写空标记"

awk -v N="$N" 'NR<=N && NF{print NR"\t"$0}' "$TMP/phones.tsv" > "$TMP/idx_nums.tsv"
awk -F'\t' '{print $2}' "$TMP/idx_nums.tsv" > "$TMP/nums.txt"
NUM_COUNT=$(wc -l < "$TMP/nums.txt" | tr -d ' ')
log "   待查号码 $NUM_COUNT 个（跳过 $((N - NUM_COUNT)) 个空行）"

# ---------- 2. 校验标记列原本为空 ----------
"$GOG" sheets get -p "$ID" "'${SHEET}'!${MARK_COL}1:${MARK_COL}" > "$TMP/marks.tsv" 2>/dev/null || : > "$TMP/marks.tsv"
OCC=$(awk -v N="$N" 'NR<=N && NF{c++} END{print c+0}' "$TMP/marks.tsv")
if [[ "$OCC" -gt 0 ]]; then
  if [[ $FORCE -eq 0 ]]; then
    elog "❌ 标记列 $MARK_COL 前 $N 行已有 $OCC 个非空值，写入会覆盖。确认要覆盖请加 --force。"
    exit 1
  fi
  log "   ⚠️  标记列已有 $OCC 个非空值（--force 强制继续，将被覆盖）"
else
  log "   标记列原本为空 ✓"
fi

if [[ $DRY -eq 1 ]]; then log "--dry-run：仅体检，未查询、未写回。"; exit 0; fi

# ---------- 2.5 确保 CDP 在线 ----------
# 沙箱下 Bash 启动的 Chrome 跨命令会被回收，但本脚本是一条命令跑完，自启动是安全的。
# 若用户已双击桌面快捷方式（或 Agent 用 WMI 启过），则直接复用，不重复启动。
if [[ -z "$REUSE" ]]; then
  if ! curl -s --max-time 3 "http://127.0.0.1:9222/json/version" >/dev/null 2>&1; then
    log "   🌐 CDP 未在线 → 自动启动 Chrome（仅本命令期间存活）"
    PY="${PY_BIN:-C:/Users/Admin/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe}"
    "$PY" "$SCRIPT_DIR/launch_cdp_chrome.py" >"$TMP/launch.log" 2>&1 || true
    if ! curl -s --max-time 3 "http://127.0.0.1:9222/json/version" >/dev/null 2>&1; then
      elog "❌ Chrome 启动失败，详见 $TMP/launch.log"
      elog "   建议：双击桌面「纷享CRM浏览器」快捷方式后重跑本脚本。"
      exit 2
    fi
  else
    log "   ♻️  复用已在线的 CDP"
  fi
fi

# ---------- 3. 取得结果（查询 or 复用）----------
RESULT_CSV="$OUT"
if [[ -n "$REUSE" ]]; then
  [[ -f "$REUSE" ]] || { elog "❌ --reuse 文件不存在: $REUSE"; exit 1; }
  RESULT_CSV="$REUSE"
  log "   ♻️  复用已有结果：$REUSE（跳过 CRM 查询）"
else
  QARGS=(--file "$TMP/nums.txt" --out "$OUT" --delay "$DELAY")
  [[ $RESUME -eq 1 ]] && QARGS+=(--resume)
  [[ $QUIET -eq 1 ]]  && QARGS+=(--quiet)

  log "   ⏳ CRM 查询中（$NUM_COUNT 个，间隔 ${DELAY}ms）..."
  "$NODE" "$SCRIPT_DIR/fx_phone_query.mjs" "${QARGS[@]}"
  RC=$?
  case $RC in
    0|1) ;;
    2) elog "❌ CDP 连接失败：请先用桌面快捷方式启动带调试端口的 Chrome。"; exit 2;;
    3) elog "❌ 登录失效：请在 Chrome 窗口重新扫码登录。"; exit 3;;
    4) elog "❌ 遇鉴权/风控：已保存进度，修复后用 --resume 重跑。"; exit 4;;
    *) elog "❌ 查询异常退出（code=$RC）"; exit 1;;
  esac
fi

# ---------- 4. 结果映射回原行位置 ----------
awk -F',' 'NR>1 && $1!="" {c=$3; gsub(/\r/,"",c); print $1"\t"c}' "$RESULT_CSV" > "$TMP/res.tsv"
awk -F'\t' '$2!="" && $2!="无数据" && $2!="ERROR" && $2!="SKIP" {print $1}' "$TMP/res.tsv" > "$TMP/hit.txt"

awk -v N="$N" -v mark="$MARK" '
  NR==FNR { hit[$1]=1; next }
  { if ($2 in hit) out[$1]=1 }
  END {
    printf "["
    for (i=1;i<=N;i++) printf "[%s]%s", (i in out ? "\""mark"\"" : "\"\""), (i<N ? "," : "")
    printf "]"
  }
' "$TMP/hit.txt" "$TMP/idx_nums.tsv" > "$TMP/col.json"

HIT=$(wc -l < "$TMP/hit.txt" | tr -d ' ')
log "   命中 $HIT / 其余 $((N - HIT))"

# ---------- 5. 写回 ----------
log "   ⬆️  写回 ${MARK_COL}1:${MARK_COL}${N} ..."
if ! "$GOG" sheets update "$ID" "'${SHEET}'!${MARK_COL}1:${MARK_COL}${N}" --values-json=@"$TMP/col.json" 2>"$TMP/err2.txt"; then
  elog "❌ 写入失败：$(cat "$TMP/err2.txt" 2>/dev/null)"; exit 1
fi

# ---------- 6. 读回验证 ----------
# 注意：gog 读取会**截断尾部空行**，读回行数可能 < N（写入范围尾部全空时）。
# 故验证三条：① 非空值必须全部是 MARK；② MARK 数 == 命中数；③ 读回行数不得超过 N。
"$GOG" sheets get -p "$ID" "'${SHEET}'!${MARK_COL}1:${MARK_COL}${N}" > "$TMP/verify.tsv"
VX=$(awk -v m="$MARK" '$0==m' "$TMP/verify.tsv" | wc -l | tr -d ' ')
VNON=$(awk 'NF' "$TMP/verify.tsv" | wc -l | tr -d ' ')
VRANGE=$(awk 'END{print NR+0}' "$TMP/verify.tsv")
log "✅ 读回验证：${MARK}=${VX}  非空=${VNON}  空=$((N - VX))  合计=${N}"
log "📄 查询明细：$RESULT_CSV"

if [[ "$VX" -ne "$HIT" || "$VNON" -ne "$VX" || "$VRANGE" -gt "$N" ]]; then
  elog "⚠️ 验证不一致（期望 ${MARK}=${HIT} / 非空=${HIT} / 读回行数<=${N}；实际 ${MARK}=${VX} / 非空=${VNON} / 读回行数=${VRANGE}）"
  exit 1
fi
log "🎉 完成"
