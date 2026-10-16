# task-distiller / outcome.ps1
# 轴4：reward signal —— 记录技能的使用与失败次数，是「可测量的进化」的地基。
# 没有这个文件，所谓自我改进只是采集，不是进化。
# 触发：goose PostToolUse hook（stdin 传事件 JSON）

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$PluginRoot = Split-Path -Parent $PSScriptRoot
$StateDir   = Join-Path $PluginRoot 'state'
$Outcomes   = Join-Path $StateDir  'skill_outcomes.json'
New-Item -ItemType Directory -Force -Path $StateDir | Out-Null

$raw = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }
try { $ev = $raw | ConvertFrom-Json } catch { exit 0 }

$tool = [string]$ev.tool_name
# 技能加载事件：不同版本字段名可能不同，逐一兜底（TODO verify 对照 skill_slash_command.rs）
$skill = ''
foreach ($k in @('skill_name','name','argument')) {
  if ($ev.tool_input -and $ev.tool_input.$k) { $skill = [string]$ev.tool_input.$k; break }
}
if (-not $skill -and $tool -notmatch 'skill') { exit 0 }
if (-not $skill) { exit 0 }

# 失败判定：PostToolUseFailure 事件走到这里时视为失败（由 matcher 分流；此处按 error 字段再兜一层）
$failed = $false
if ($ev.PSObject.Properties.Name -contains 'error' -and $ev.error) { $failed = $true }
if ($ev.PSObject.Properties.Name -contains 'is_error' -and $ev.is_error) { $failed = $true }

if (Test-Path $Outcomes) {
  try { $data = Get-Content $Outcomes -Raw -Encoding utf8 | ConvertFrom-Json } catch { $data = [pscustomobject]@{} }
} else {
  $data = [pscustomobject]@{}
}

$cur = if ($data.PSObject.Properties.Name -contains $skill) { $data.$skill } else { [pscustomobject]@{ use = 0; fail = 0; last = '' } }
$cur.use  = [int]$cur.use + 1
if ($failed) { $cur.fail = [int]$cur.fail + 1 }
$cur.last = (Get-Date).ToString('s')

if ($data.PSObject.Properties.Name -contains $skill) { $data.$skill = $cur }
else { $data | Add-Member -NotePropertyName $skill -NotePropertyValue $cur }

$data | ConvertTo-Json -Depth 6 | Set-Content -Path $Outcomes -Encoding utf8
exit 0
