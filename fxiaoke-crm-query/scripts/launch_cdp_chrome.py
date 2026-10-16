# -*- coding: utf-8 -*-
"""
launch_cdp_chrome.py — 以「完全分离进程」方式启动带 CDP 调试端口的 Chrome。

为什么需要这个：用 Bash 的 run_in_background 启动 GUI 进程时，
后台任务结束会连带回收整个进程组，Chrome 跟着退出。
用 DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP 可让 Chrome 完全脱离父进程，
父进程退出后仍持续运行。

用法：
    python launch_cdp_chrome.py            # 静默后台（窗口移出屏幕）
    python launch_cdp_chrome.py --visible  # 窗口可见（用于登录）
"""
import subprocess
import sys
import time
import urllib.request

CHROME  = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE = r"C:\Users\Admin\.workbuddy-ai\browser-profiles\manual"
URL     = "https://www.fxiaoke.com/XV/UI/Home"
CDP     = "http://127.0.0.1:9222/json/version"

DETACHED_PROCESS        = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200


def cdp_alive(timeout=2):
    try:
        with urllib.request.urlopen(CDP, timeout=timeout) as r:
            import json
            d = json.loads(r.read().decode())
            return d.get("Browser", "?")
    except Exception:
        return None


def main():
    visible = "--visible" in sys.argv

    # 已在运行则直接返回
    browser = cdp_alive()
    if browser:
        print("CDP 已在运行: %s" % browser)
        return 0

    args = [
        CHROME,
        '--user-data-dir=%s' % PROFILE,
        '--remote-debugging-port=9222',
        '--no-first-run',
        '--no-default-browser-check',
    ]
    if visible:
        args += ['--window-position=120,80', '--window-size=1280,800']
    else:
        args += ['--window-position=-32000,-32000', '--window-size=1280,800']
    args.append(URL)

    p = subprocess.Popen(
        args,
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        close_fds=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("已启动 Chrome (pid=%d)，等待 CDP 就绪…" % p.pid)

    for i in range(30):
        time.sleep(1)
        b = cdp_alive()
        if b:
            print("✅ CDP 就绪: %s  (耗时 %ds)" % (b, i + 1))
            return 0
    print("⚠️ 30 秒内 CDP 未就绪，请检查 Chrome 是否正常启动")
    return 1


if __name__ == "__main__":
    sys.exit(main())
