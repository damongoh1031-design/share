"""持续检测可见的控制台类顶层窗口，测量其可见时长。

用法:
    python detect_window.py <输出文件> [持续秒数]

配合方式（触发侧与检测侧分离，因为沙箱不允许 Python 调 schtasks）:
    1. Bash 后台:  python detect_window.py out.txt 90
    2. PowerShell: Start-Sleep -Seconds 15; Start-ScheduledTask -TaskName '<任务名>'
    3. 读取 out.txt

窗口类名对照:
    ConsoleWindowClass             传统 conhost 窗口
    CASCADIA_HOSTING_WINDOW_CLASS  Windows Terminal 主窗口
    PseudoConsoleWindow            Windows Terminal 伪控制台
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

CONSOLE_CLASSES = ('ConsoleWindowClass', 'CASCADIA', 'PseudoConsole')


def scan():
    """返回 (可见顶层窗口总数, [控制台类可见窗口])。总数用于健全性检查。"""
    total = [0]
    consoles = []

    def cb(hwnd, _lparam):
        if user32.IsWindowVisible(hwnd):
            total[0] += 1
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            buf = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, buf, 256)
            cls = buf.value
            if any(k in cls for k in CONSOLE_CLASSES):
                consoles.append((pid.value, cls))
        return True

    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return total[0], consoles


def main():
    out_path = sys.argv[1]
    duration = float(sys.argv[2]) if len(sys.argv) > 2 else 90.0

    with open(out_path, 'w', encoding='utf-8') as f:
        t0 = time.time()
        total0, _ = scan()
        f.write(f"健全性检查: 当前可见顶层窗口数 = {total0}\n")
        f.flush()

        first, last = {}, {}
        while time.time() - t0 < duration:
            t = time.time() - t0
            _, consoles = scan()
            for item in consoles:
                if item not in first:
                    first[item] = t
                last[item] = t
            time.sleep(0.003)

        if first:
            f.write("检测到的可见控制台窗口：\n")
            for item in first:
                f.write(f"  pid={item[0]:<8} class={item[1]:<34} "
                        f"首次={first[item]:7.3f}s  末次={last[item]:7.3f}s  "
                        f"可见时长≈{last[item] - first[item]:6.3f}s\n")
        else:
            f.write("（未检测到任何可见控制台窗口）\n")
        f.write("DETECT-END\n")
        f.flush()


if __name__ == '__main__':
    main()
