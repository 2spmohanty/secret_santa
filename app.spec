import sys
import os
from PyInstaller.utils.hooks import collect_dynamic_libs

pygame_libs = collect_dynamic_libs('pygame')



# -*- mode: python ; coding: utf-8 -*-

pygame_libs = collect_dynamic_libs('pygame')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=pygame_libs,
    datas=[('images', 'images'), ('music', 'music')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,

)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,
)

a.datas += [('images/logo.png', '/Users/smruti/Dev/secret_santa/images/logo.png', 'DATA')]
