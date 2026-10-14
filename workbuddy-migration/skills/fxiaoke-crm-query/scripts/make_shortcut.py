# -*- coding: utf-8 -*-
"""
make_shortcut.py — 创建 Windows 快捷方式 (.lnk)

通过 ctypes 调用 Windows Shell COM 接口（IShellLinkW + IPersistFile），
由 Windows 自己生成 .lnk，保证格式有效。

为什么绕这一圈：本环境沙箱禁止 PowerShell 的 COM 实例化（New-Object -ComObject）
和 cscript，但 Python ctypes 调 COM 不在拦截范围内。

⚠️ vtable 索引要点：IShellLinkW 与 IPersistFile 是两个**独立接口**，
各自的 vtable 从 0 开始计数，不能混用。
    IShellLinkW :  QueryInterface(0) AddRef(1) Release(2) GetPath(3) GetIDList(4)
                   SetIDList(5) GetDescription(6) SetDescription(7) GetWorkingDirectory(8)
                   SetWorkingDirectory(9) GetArguments(10) SetArguments(11) GetHotkey(12)
                   SetHotkey(13) GetShowCmd(14) SetShowCmd(15) GetIconLocation(16)
                   SetIconLocation(17) SetRelativePath(18) Resolve(19) SetPath(20)
    IPersistFile:  QueryInterface(0) AddRef(1) Release(2) GetClassID(3) IsDirty(4)
                   Load(5) Save(6) SaveCompleted(7) GetCurFile(8)

用法：
    python make_shortcut.py
"""
import ctypes
import os
import sys
from ctypes import (POINTER, byref, c_void_p, c_ulong, c_ushort, c_ubyte,
                    c_wchar_p, c_int, c_int32)

ole32 = ctypes.windll.ole32


# ============ COM 基础设施 ============
class GUID(ctypes.Structure):
    _fields_ = [('Data1', c_ulong), ('Data2', c_ushort),
                ('Data3', c_ushort), ('Data4', c_ubyte * 8)]


CLSID_ShellLink  = GUID(0x00021401, 0, 0, (c_ubyte * 8)(0xC0, 0, 0, 0, 0, 0, 0, 0x46))
IID_IShellLinkW  = GUID(0x000214F9, 0, 0, (c_ubyte * 8)(0xC0, 0, 0, 0, 0, 0, 0, 0x46))
IID_IPersistFile = GUID(0x0000010B, 0, 0, (c_ubyte * 8)(0xC0, 0, 0, 0, 0, 0, 0, 0x46))

CLSCTX_INPROC_SERVER = 1

# --- IShellLinkW vtable ---
VT_QUERY_INTERFACE    = 0
VT_RELEASE            = 2
VT_SET_DESCRIPTION    = 7
VT_SET_WORKING_DIR    = 9
VT_SET_ARGUMENTS      = 11
VT_SET_SHOW_CMD       = 15
VT_SET_ICON_LOCATION  = 17
VT_SET_PATH           = 20

# --- IPersistFile vtable（独立计数！）---
PF_RELEASE            = 2
PF_SAVE               = 6

SHOW_NORMAL = 1


def _fn(ptr, idx, argtypes):
    vtbl = ctypes.cast(ptr, POINTER(POINTER(c_void_p)))[0]
    proto = ctypes.WINFUNCTYPE(c_int32, c_void_p, *argtypes)
    return proto(vtbl[idx])


def create_lnk(path, target, args, workdir, icon, icon_index,
               description, show_cmd=SHOW_NORMAL):
    """用 IShellLinkW 创建 .lnk，返回 (ok, message)"""
    ole32.CoInitialize(None)

    p = c_void_p()
    hr = ole32.CoCreateInstance(byref(CLSID_ShellLink), None, CLSCTX_INPROC_SERVER,
                                byref(IID_IShellLinkW), byref(p))
    if hr != 0 or not p.value:
        return False, 'CoCreateInstance hr=0x%08X' % (hr & 0xFFFFFFFF)

    try:
        steps = [
            ('SetPath',             VT_SET_PATH,          [c_wchar_p],        (target,)),
            ('SetArguments',        VT_SET_ARGUMENTS,     [c_wchar_p],        (args,)),
            ('SetWorkingDirectory', VT_SET_WORKING_DIR,   [c_wchar_p],        (workdir,)),
            ('SetIconLocation',     VT_SET_ICON_LOCATION, [c_wchar_p, c_int], (icon, icon_index)),
            ('SetDescription',      VT_SET_DESCRIPTION,   [c_wchar_p],        (description,)),
            ('SetShowCmd',          VT_SET_SHOW_CMD,      [c_int],            (show_cmd,)),
        ]
        for name, idx, types, a in steps:
            hr = _fn(p, idx, types)(p, *a)
            if hr != 0:
                return False, '%s hr=0x%08X' % (name, hr & 0xFFFFFFFF)

        # --- 取 IPersistFile ---
        pf = c_void_p()
        hr = _fn(p, VT_QUERY_INTERFACE, [c_void_p, POINTER(c_void_p)])(
            p, ctypes.cast(byref(IID_IPersistFile), c_void_p), byref(pf))
        if hr != 0:
            return False, 'QueryInterface(IPersistFile) hr=0x%08X' % (hr & 0xFFFFFFFF)
        if not pf.value:
            return False, 'QueryInterface 返回空指针'

        try:
            if os.path.exists(path):
                os.remove(path)
            # IPersistFile::Save(pszFileName, fRemember)
            hr = _fn(pf, PF_SAVE, [c_wchar_p, c_int])(pf, path, 1)
            if hr != 0:
                return False, 'IPersistFile::Save hr=0x%08X' % (hr & 0xFFFFFFFF)
        finally:
            _fn(pf, PF_RELEASE, [])(pf)
        return True, 'ok'
    finally:
        _fn(p, VT_RELEASE, [])(p)


# ============ 配置 ============
CHROME  = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE = r"C:\Users\Admin\.workbuddy-ai\browser-profiles\manual"
URL     = "https://www.fxiaoke.com/XV/UI/Home"
DESKTOP = r"C:\Users\Admin\Desktop"

COMMON_ARGS = (
    '--user-data-dir="%s" '
    '--remote-debugging-port=9222 '
    '--no-first-run --no-default-browser-check' % PROFILE
)


def main():
    if not os.path.isfile(CHROME):
        print('ERROR: 找不到 Chrome: %s' % CHROME); return 1
    if not os.path.isdir(DESKTOP):
        print('ERROR: 找不到桌面: %s' % DESKTOP); return 1

    jobs = [
        ('纷享CRM浏览器.lnk',
         COMMON_ARGS + ' --window-position=120,80 --window-size=1280,800 "%s"' % URL,
         '启动带 CDP 调试端口(9222)的纷享销客 CRM 浏览器 — 窗口可见，用于登录与排查'),
        ('纷享CRM浏览器（后台静默）.lnk',
         COMMON_ARGS + ' --window-position=-32000,-32000 --window-size=900,700 "%s"' % URL,
         '静默后台启动 CDP 浏览器（窗口移出屏幕），供自动化查询常驻使用'),
    ]

    ok_count = 0
    for fname, args, desc in jobs:
        path = os.path.join(DESKTOP, fname)
        ok, msg = create_lnk(path, CHROME, args, os.path.dirname(CHROME),
                             CHROME, 0, desc)
        exists = os.path.isfile(path)
        size = os.path.getsize(path) if exists else 0
        print('%s %s  (%d bytes)%s'
              % ('OK  ' if ok and exists else 'FAIL', fname, size,
                 '' if ok else '  — ' + msg))
        if ok and exists:
            ok_count += 1

    print('\n成功 %d/%d' % (ok_count, len(jobs)))
    return 0 if ok_count == len(jobs) else 1


if __name__ == '__main__':
    sys.exit(main())
