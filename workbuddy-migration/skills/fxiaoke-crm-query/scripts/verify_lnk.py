# -*- coding: utf-8 -*-
"""
verify_lnk.py — 用 Windows Shell COM 接口验证 .lnk 是否有效。

加载 .lnk → GetPath()/GetArguments() → 若返回我们写入的内容，说明快捷方式有效。

⚠️ 两个关键点：
1. IPersistFile 是独立接口，vtable 从 0 计数（Load=5, Save=6）
2. 输出缓冲区必须用 c_void_p 显式传地址；用 c_wchar_p 会被 ctypes 复制成临时副本，
   导致函数写入的内容丢失（表现为 GetPath 返回空串）
"""
import ctypes
import sys
from ctypes import (POINTER, byref, c_void_p, c_ulong, c_ushort, c_ubyte,
                    c_wchar_p, c_int, c_int32)

ole32 = ctypes.windll.ole32


class GUID(ctypes.Structure):
    _fields_ = [('Data1', c_ulong), ('Data2', c_ushort),
                ('Data3', c_ushort), ('Data4', c_ubyte * 8)]


CLSID_ShellLink   = GUID(0x00021401, 0, 0, (c_ubyte * 8)(0xC0, 0, 0, 0, 0, 0, 0, 0x46))
IID_IShellLinkW   = GUID(0x000214F9, 0, 0, (c_ubyte * 8)(0xC0, 0, 0, 0, 0, 0, 0, 0x46))
IID_IPersistFile  = GUID(0x0000010B, 0, 0, (c_ubyte * 8)(0xC0, 0, 0, 0, 0, 0, 0, 0x46))

CLSCTX_INPROC_SERVER = 1
STGM_READ = 0
SLGP_RAWPATH = 4

# --- IShellLinkW vtable ---
VT_QUERY_INTERFACE = 0
VT_RELEASE         = 2
VT_GET_PATH        = 3
VT_GET_DESCRIPTION = 6
VT_GET_WORKING_DIR = 8
VT_GET_ARGUMENTS   = 10
VT_GET_ICON        = 16
# --- IPersistFile vtable（独立计数！）---
PF_RELEASE         = 2
PF_LOAD            = 5


def vcall(ptr, idx, argtypes, *args):
    vtbl = ctypes.cast(ptr, POINTER(POINTER(c_void_p)))[0]
    fn = ctypes.cast(vtbl[idx], ctypes.WINFUNCTYPE(c_int32, c_void_p, *argtypes))
    return fn(ptr, *args)


def probe(path):
    p = c_void_p()
    hr = ole32.CoCreateInstance(byref(CLSID_ShellLink), None, CLSCTX_INPROC_SERVER,
                                byref(IID_IShellLinkW), byref(p))
    if hr != 0:
        return dict(ok=False, err='CoCreateInstance hr=0x%08X' % (hr & 0xFFFFFFFF))

    try:
        # 必须先 QueryInterface 取 IPersistFile —— Load/Save 是它的方法，
        # 不能在 IShellLinkW 指针上直接按索引调（那会调到 SetIDList）
        pf = c_void_p()
        hr = vcall(p, VT_QUERY_INTERFACE, [POINTER(GUID), POINTER(c_void_p)],
                   byref(IID_IPersistFile), byref(pf))
        if hr != 0 or not pf.value:
            return dict(ok=False, err='QueryInterface(IPersistFile) hr=0x%08X' % (hr & 0xFFFFFFFF))

        try:
            # IPersistFile::Load(path, STGM_READ)
            hr = vcall(pf, PF_LOAD, [c_wchar_p, c_ulong], path, STGM_READ)
            if hr != 0:
                return dict(ok=False, err='IPersistFile::Load hr=0x%08X' % (hr & 0xFFFFFFFF))
        finally:
            try:
                vcall(pf, PF_RELEASE, [])
            except Exception:
                pass

        out = dict(ok=True)

        # GetPath(buf, cch, pfd, fFlags) —— 用 c_void_p 传缓冲区地址
        buf = ctypes.create_unicode_buffer(1024)
        hr = vcall(p, VT_GET_PATH, [c_void_p, c_int, c_void_p, c_ulong],
                   ctypes.cast(buf, c_void_p), 1024, None, SLGP_RAWPATH)
        out['getpath_hr'] = '0x%08X' % (hr & 0xFFFFFFFF)
        out['target'] = buf.value

        abuf = ctypes.create_unicode_buffer(2048)
        vcall(p, VT_GET_ARGUMENTS, [c_void_p, c_int],
              ctypes.cast(abuf, c_void_p), 2048)
        out['args'] = abuf.value

        wbuf = ctypes.create_unicode_buffer(1024)
        vcall(p, VT_GET_WORKING_DIR, [c_void_p, c_int],
              ctypes.cast(wbuf, c_void_p), 1024)
        out['workdir'] = wbuf.value

        dbuf = ctypes.create_unicode_buffer(1024)
        vcall(p, VT_GET_DESCRIPTION, [c_void_p, c_int],
              ctypes.cast(dbuf, c_void_p), 1024)
        out['description'] = dbuf.value

        ibuf = ctypes.create_unicode_buffer(1024)
        idx = c_int(0)
        vcall(p, VT_GET_ICON, [c_void_p, c_int, POINTER(c_int)],
              ctypes.cast(ibuf, c_void_p), 1024, byref(idx))
        out['icon'] = '%s,%d' % (ibuf.value, idx.value)

        return out
    finally:
        try:
            vcall(p, VT_RELEASE, [])
        except Exception:
            pass


def main():
    paths = sys.argv[1:]
    if not paths:
        print('用法: python verify_lnk.py <a.lnk> [b.lnk ...]')
        return 2

    allok = True
    for path in paths:
        r = probe(path)
        print('=' * 70)
        print('文件: %s' % path)
        if not r['ok']:
            print('  状态: 无效 — %s' % r['err'])
            allok = False
            continue

        print('  状态    : 有效快捷方式（Windows 可解析）')
        print('  目标    : %s' % r['target'])
        print('  参数    : %s' % r['args'])
        print('  工作目录: %s' % r['workdir'])
        print('  描述    : %s' % r['description'])
        print('  图标    : %s' % r['icon'])

        checks = {
            '目标 = chrome.exe': r['target'].lower().endswith('chrome.exe'),
            '含调试端口 9222': 'remote-debugging-port=9222' in r['args'],
            '含 profile 目录': 'browser-profiles' in r['args'],
            '含 CRM 地址': 'fxiaoke.com' in r['args'],
            '工作目录正确': 'Chrome' in r['workdir'],
        }
        for k, v in checks.items():
            print('    %s %s' % ('OK  ' if v else 'FAIL', k))
            if not v:
                allok = False

    print('=' * 70)
    print('总体: %s' % ('全部有效' if allok else '存在无效项'))
    return 0 if allok else 1


if __name__ == '__main__':
    sys.exit(main())
