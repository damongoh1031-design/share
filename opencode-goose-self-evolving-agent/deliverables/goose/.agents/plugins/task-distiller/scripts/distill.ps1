# task-distiller / distill.ps1
# 轴1：会话结束时把「本轮是否值得沉淀」入队，交由 agent 或人工处理。
# 设计原则：本脚本**不做任何自动写入技能的动作**，只收集与排队。
#   —— 自动写入 + 无闸门 = 注入面自我放大（见报告 §风险）。
# 触发：goose SessionEnd hook（事件 payload 从 stdin 传入 JSON）

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$PluginRoot = Split-Path -Parent $PSScriptRoot          # …/task-distiller
$StateDir   = Join-Path $PluginRoot 'state'
$QueueFile  = Join-Path $StateDir  'distill_queue.md'
$LogFile    = Join-Path $StateDir  'last-event.log'
New-Item -ItemType Directory -Force -Path $StateDir | Out-Null

# 读 goose 传入的事件 JSON（缺 stdin 时不报错，便于手动测试）
$raw = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($raw)) { $raw = '{}' }
($raw) | Add-Content -Path $LogFile -Encoding utf8

try { $ev = $raw | ConvertFrom-Json } catch { $ev = $null }

$sessionId = if ($ev -and $ev.session_id) { $ev.session_id } else { 'unknown' }
$cwd       = if ($ev -and $ev.working_dir) { $ev.working_dir } else { (Get-Location).Path }
$ts        = (Get-Date).ToString('s')

# 只排队，不写技能。真正沉淀由下一次会话里的 agent（或人工）挑一条来做。
$entry = @"
- [ ] $ts | session=$sessionId | cwd=$cwd
      待判定：本轮是否产生可复用流程？若是 → 写 `$HOME/.agents/skills/<name>/SKILL.md
"@
Add-Content -Path $QueueFile -Value $entry -Encoding utf8

# 顺带把「共享技能根」的现状打进日志，便于观察沉淀是否真的发生了
$skillsDir = Join-Path $HOME '.agents/skills'
if (Test-Path $skillsDir) {
  $names = (Get-ChildItem $skillsDir -Directory | Select-Object -ExpandProperty Name) -join ', '
  Add-Content -Path $LogFile -Value "skills[$((Get-ChildItem $skillsDir -Directory).Count)]: $names" -Encoding utf8
}

exit 0
