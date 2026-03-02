# -*- mode: python ; coding: utf-8 -*-
# Mac-only spec: creates TurboCopy.app (double-clickable app bundle)
# Build on Mac: pyinstaller turbo_copy_mac.spec

block_cipher = None

a = Analysis(
    ['turbo_copy.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,   # onedir: binaries go to COLLECT
    name='TurboCopy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TurboCopy',
)

app = BUNDLE(
    coll,
    name='TurboCopy.app',
    icon=None,
    bundle_identifier='com.turbocopy.app',
    info_plist={'NSPrincipalClass': 'NSApplication'},
)
