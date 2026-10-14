"""实时记录「可见控制台窗口」的出现 / 消失事件，逐条落盘。

与 detect_window.py 的区别：
    detect_window.py   —— 统计「可见时长」，适合抓 < 2 秒的闪烁，结果最后一次性输出。
    viswatch.py        —— 逐条写事件（+VISIBLE / -GONE），适合抓「常驻窗口」和
                          「什么时候冒出来的」，中途随时可以读文件看进度。

用法:
    python viswatch.py <输出文件> [持续秒数]

输出示例:
    watch start 17:39:22 dur=900.0s
      0.00s +VISIBLE hwnd=57411606 pid=40508 class=CASCADIA_HOSTING_WINDOW_CLASS title='C:\\WINDOWS\\system32\\cmd.exe'
    557.40s -GONE    hwnd=57411606 pid=40508 class=CASCADIA_HOSTING_WINDOW_CLASS

注意: IsWindowVisible() 对「最小化」窗口也返回 True。要判断「用户是否真的看得见」，
      必须再查 IsIconic() 和 GetWindowRect()（见 winstate.py 思路）。
"""
import ctypes
import sys
import time
from ctypes import wintypes

user32 = ctypes.WinDLL('user32', use_last_error=True)
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]

KEYS = ('ConsoleWindowClass', 'CASCADIA', 'PseudoConsole')


def scan():
    found = []

    def cb(hwnd, _lp):
        if user32.IsWindowVisible(hwnd):
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            cls = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, cls, 256)
            if any(k in cls.value for k in KEYS):
                ttl = ctypes.create_unicode_buffer(256)
                user32.GetWindowTextW(hwnd, ttl, 256)
                found.append((int(hwnd), pid.value, cls.value, ttl.value))
        return True

    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return found


def main():
    out = sys.argv[1]
    dur = float(sys.argv[2]) if len(sys.argv) > 2 else 600.0
    f = open(out, 'w', encoding='utf-8')
    t0 = time.time()
    prev = {}
    f.write("watch start %s dur=%ss\n" % (time.strftime('%H:%M:%S'), dur))
    f.flush()
    while time.time() - t0 < dur:
        t = time.time() - t0
        cur = {w[0]: w for w in scan()}
        for h in cur:
            if h not in prev:
                w = cur[h]
                f.write("%6.2fs +VISIBLE hwnd=%s pid=%s class=%s title=%r\n"
                        % (t, w[0], w[1], w[2], w[3]))
                f.flush()
        for h in prev:
            if h not in cur:
                w = prev[h]
                f.write("%6.2fs -GONE    hwnd=%s pid=%s class=%s\n" % (t, w[0], w[1], w[2]))
                f.flush()
        prev = cur
        time.sleep(0.01)
    f.write("watch end\n")
    f.close()


if __name__ == '__main__':
    main()
