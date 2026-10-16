# task-distiller / guard.ps1
# 轴5：护栏 —— 对应 Hermes 的「改 SOUL.md/AGENTS.md/CLAUDE.md 即使 --yolo 也须人工批准」。
# 触发：goose PreToolUse hook。PreToolUse 可返回 Deny 阻断工具调用并回传 reason。
#
# ⚠ TODO(verify)：goose 期望的 stdout 决策 JSON 结构需对照
#   crates/goose/src/hooks/mod.rs 的 PreToolUseResultPayload（allow/deny + reason + blocked_by）
#   确认后再启用 deny；当前默认输出 allow，属于「只观测不拦截」的安全起步。

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$PluginRoot = Split-Path -Parent $PSScriptRoot
$StateDir   = Join-Path $PluginRoot 'state'
New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
$LogFile = Join-Path $StateDir 'guard.log'

$raw = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($raw)) { '{"decision":"allow"}'; exit 0 }
try { $ev = $raw | ConvertFrom-Json } catch { '{"decision":"allow"}'; exit 0 }

$tool = [string]$ev.tool_name
$target = ''
foreach ($k in @('path','file_path','command','filePath')) {
  if ($ev.tool_input -and $ev.tool_input.$k) { $target = [string]$ev.tool_input.$k; break }
}
if (-not $target) { $target = [string]$ev.tool_input }

Add-Content -Path $LogFile -Value "$((Get-Date).ToString('s')) tool=$tool target=$target" -Encoding utf8

# 受保护清单：agent 不得自行改写自身指令文件与自进化脚本本体
$protected = @(
  'AGENTS.md', 'CLAUDE.md', 'SOUL.md',
  '\.agents[\\/]plugins[\\/]task-distiller'
)
$hit = $false
foreach ($p in $protected) { if ($target -match $p) { $hit = $true; break } }

if ($hit) {
  # 默认只记录、不拦截。确认决策 JSON schema 后，把下面两行换成 Deny：
  # '{"decision":"deny","reason":"受保护文件：自我指令/自进化脚本须人工修改"}'; exit 0
  Add-Content -Path $LogFile -Value "  → 命中受保护清单（当前策略：仅记录）" -Encoding utf8
}

'{"decision":"allow"}'
exit 0
