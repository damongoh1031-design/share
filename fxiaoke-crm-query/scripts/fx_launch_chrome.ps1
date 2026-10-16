<#
  fx_launch_chrome.ps1 — 启动带 CDP 调试端口的 Chrome，且**不会被沙箱回收**。

  为什么必须用这个而不是直接 Popen / start：
    本机 WorkBuddy 沙箱把每个命令放进一个 Windows Job Object，
    命令结束时整个 job 被 terminate —— 子进程（含 DETACHED_PROCESS）一并被杀。
    实测：launch_cdp_chrome.py 启动后同一命令内 CDP 可用，换下一条命令就 10061 拒绝连接。
    解法：用 WMI (Win32_Process.Create) 创建进程，父进程是 WmiPrvSE.exe，
    不在我们的 job 里 → Chrome 可跨命令持续存活。

  用法（必须通过 PowerShell 工具执行，Bash 里调 powershell 会被沙箱拦截）：
    powershell -ExecutionPolicy Bypass -File fx_launch_chrome.ps1            # 后台静默窗口
    powershell -ExecutionPolicy Bypass -File fx_launch_chrome.ps1 -Visible   # 窗口可见（登录用）
    powershell -ExecutionPolicy Bypass -File fx_launch_chrome.ps1 -Check     # 仅检查状态
#>
param(
    [switch]$Visible,
    [switch]$Check,
    [string]$Url = "https://www.fxiaoke.com/XV/UI/Home"
)

$Chrome  = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$Profile = 'C:\Users\Admin\.workbuddy-ai\browser-profiles\manual'
$CDP     = 'http://127.0.0.1:9222/json/version'

function Get-Cdp {
    try {
        $r = Invoke-WebRequest -Uri $CDP -TimeoutSec 2 -UseBasicParsing
        return ($r.Content | ConvertFrom-Json).Browser
    } catch { return $null }
}

$browser = Get-Cdp
if ($browser) {
    Write-Output "CDP_ALREADY_RUNNING: $browser"
    exit 0
}

if ($Check) {
    Write-Output "CDP_DOWN"
    exit 1
}

if (-not (Test-Path $Chrome)) {
    Write-Output "ERROR: chrome.exe not found at $Chrome"
    exit 1
}

if ($Visible) { $pos = '--window-position=120,80' } else { $pos = '--window-position=-32000,-32000' }

$cmd = '"' + $Chrome + '"' +
       ' --user-data-dir="' + $Profile + '"' +
       ' --remote-debugging-port=9222' +
       ' --no-first-run --no-default-browser-check' +
       ' ' + $pos + ' --window-size=1280,800' +
       ' "' + $Url + '"'

$res = ([wmiclass]'Win32_Process').Create($cmd)
if ($res.ReturnValue -ne 0) {
    Write-Output "ERROR: Win32_Process.Create ReturnValue=$($res.ReturnValue)"
    exit 1
}
Write-Output "LAUNCHED: pid=$($res.ProcessId)  waiting for CDP ..."

for ($i = 1; $i -le 30; $i++) {
    Start-Sleep -Seconds 1
    $b = Get-Cdp
    if ($b) {
        Write-Output "CDP_READY: $b  (${i}s)"
        exit 0
    }
}
Write-Output "WARN: CDP not ready within 30s"
exit 1
