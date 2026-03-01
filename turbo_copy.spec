# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for TurboCopy
# Build: pyinstaller turbo_copy.spec
# Output: dist/TurboCopy/ (folder) or dist/TurboCopy.exe (onefile)

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
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TurboCopy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,   # No terminal window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,  # Set True on Mac for .app bundle behavior
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
