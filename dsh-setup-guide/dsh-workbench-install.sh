#!/usr/bin/env bash
# ============================================================
# 把 DSH 打造成通用工作台 —— 插件安装脚本
# 对标 Goose / OpenWork / Open WebUI / WorkBuddy
# 生成日期: 2026-10-14
#
# 用法:
#   bash dsh-workbench-install.sh              # 安装「最小可用组合」(7 个)
#   bash dsh-workbench-install.sh --team       # 追加团队协作组
#   bash dsh-workbench-install.sh --knowledge  # 追加知识工作者组
#   bash dsh-workbench-install.sh --remote     # 追加远程+安全组
#   bash dsh-workbench-install.sh --all        # 全部安装
#   bash dsh-workbench-install.sh --dry-run    # 只打印不执行
#
# 注意:
#   1. 装完需重启 `dsh web` 并刷新页面才生效
#   2. 建议装一个验证一个，避免版本不兼容导致 dsh web 起不来
#   3. 安装前先确认 dsh 版本: dsh --version
# ============================================================

set -u
PROFILE="web"
DRY=0
GROUPS=()

for a in "$@"; do
  case "$a" in
    --team|--knowledge|--remote) GROUPS+=("$a") ;;
    --all) GROUPS=(--team --knowledge --remote) ;;
    --dry-run) DRY=1 ;;
    --profile=*) PROFILE="${a#--profile=}" ;;
    *) echo "未知参数: $a" >&2 ;;
  esac
done

install() {
  local pkg="$1"
  if [ "$DRY" -eq 1 ]; then
    echo "  [dry-run] dsh plugin --profile $PROFILE add $pkg"
  else
    echo "  --> $pkg"
    dsh plugin --profile "$PROFILE" add "$pkg" || echo "     !! 安装失败: $pkg （可稍后重试或检查版本要求）"
  fi
}

echo "=============================================="
echo " DSH 工作台插件安装  (profile=$PROFILE)"
[ "$DRY" -eq 1 ] && echo " 模式: DRY-RUN（不实际安装）"
echo "=============================================="

# ---------- 组 1: 最小可用组合（默认安装）----------
echo
echo "[1/4] 最小可用组合 —— 覆盖 80% 日常场景"
install dsh-config-manager              # 配置备份/迁移，先装它再折腾别的
install dock-base                       # VSCode 风格工作台布局外壳
install dsh-better-sidebar              # 侧边栏工作台（文件/终端/Git/子代理）
install @michengai/dsh-archive-manager  # 会话归档管理
install dsh-mcp-connector               # MCP/连接器管理面板（企查查团队维护）
install billion-context                 # 上下文压缩（生态第一，省 5 倍 token）
install dsh-context                     # 上下文可视化仪表盘

# ---------- 组 2: 团队协作 ----------
if printf '%s\n' "${GROUPS[@]:-}" | grep -q -- '--team'; then
  echo
  echo "[2/4] 团队协作组 —— 专家体系 + 自动化"
  install "github:Asher-2000/dsh-expert-mode"        # 首席协调官 + 17 位领域专家
  install @nanmicoder/dsh-agent-teams                # 持久化多智能体团队
  install dsh-scheduler                              # Cron 定时任务
  install @linxin666/dsh-client-ui-task-board        # 任务看板（含 cron）
fi

# ---------- 组 3: 知识工作者 ----------
if printf '%s\n' "${GROUPS[@]:-}" | grep -q -- '--knowledge'; then
  echo
  echo "[3/4] 知识工作者组 —— 知识库 + 办公 + 多模态"
  install dsh-kb-rag                                 # 本地文献知识库 RAG（10 个工具）
  install dsh-univer-office                          # 表格/文档/幻灯片一体化办公环境
  install @liustack/modlens                          # 纯文本模型补视觉（结构化 JSON 证据）
  install @xmanrui/dsh-im                            # IM 接入（9 种渠道）
  install dsh-pocket                                 # 手机远程访问（扫码即用）
fi

# ---------- 组 4: 远程 + 安全 ----------
if printf '%s\n' "${GROUPS[@]:-}" | grep -q -- '--remote'; then
  echo
  echo "[4/4] 远程 + 安全组 —— 暴露公网前必装"
  echo "  提示: 顺序很重要 —— 先有认证门禁，再开远程访问"
  install dsh-ui-auth                                # Web UI 登录门禁（PBKDF2 + 会话 Cookie）
  install @mrweicodes/dsh-permgate                   # 细粒度权限网关
  install "github:a23842/dsh-notifier"               # 多渠道通知
fi

echo
echo "=============================================="
echo " 完成。下一步:"
echo "   1) dsh plugin --profile $PROFILE list    # 确认已装"
echo "   2) dsh web                               # 重启服务"
echo "   3) 浏览器刷新 → 左下角「设置」确认新插件配置项出现"
echo
echo " 若插件启动失败（多为上次异常退出的锁文件残留）:"
echo "   删除 %USERPROFILE%\\.dsh\\**\\*.lock 后重启"
echo "=============================================="
