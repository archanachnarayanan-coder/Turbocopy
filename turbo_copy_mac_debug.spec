# Mac debug spec: console=True shows errors in Terminal
# Build: pyinstaller turbo_copy_mac_debug.spec
# Run from Terminal to see crash: ./dist/TurboCopy.app/Contents/MacOS/TurboCopy

block_cipher = None

a = Analysis(
    ['turbo_copy.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['tkinter'],
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
    exclude_binaries=True,
    name='TurboCopy',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,   # Disable UPX for easier debugging
    console=True,   # Opens Terminal - errors will be visible
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
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
