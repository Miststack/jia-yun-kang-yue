# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all, collect_submodules

datas = [('app', 'app')]
binaries = []
hiddenimports = [
    'webview',
    'webview.platforms.edgechromium',
    'webview.platforms.winforms',
    'serial',
    'serial.tools',
    'serial.tools.list_ports',
    'pythonnet',
    'clr_loader',
    'clr',
    'bottle',
    'proxy_tools',
]
tmp_ret = collect_all('webview')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]
hiddenimports += collect_submodules('webview')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# Windows 10/11 自带这些系统 DLL。打进安装包后，对方电脑常会在覆盖时提示“拒绝访问”。
_SKIP_DLLS = {
    'ucrtbase.dll',
    'ucrtbased.dll',
}


def _keep_binary(item):
    name = item[0].replace('\\', '/').split('/')[-1].lower()
    if name in _SKIP_DLLS:
        return False
    if name.startswith('api-ms-win-'):
        return False
    return True


a.binaries = [b for b in a.binaries if _keep_binary(b)]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='甲韵康跃监测系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='甲韵康跃监测系统',
)
