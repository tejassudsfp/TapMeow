# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['tap_meow_app.py'],
    pathex=[],
    binaries=[],
    datas=[('meow.wav', '.')],
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
    [],
    exclude_binaries=True,
    name='TapMeow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TapMeow',
)
app = BUNDLE(
    coll,
    name='TapMeow.app',
    icon='icon.icns',
    bundle_identifier='com.fandesk.tapmeow',
    info_plist={
        'LSUIElement': True,
        'NSMicrophoneUsageDescription': 'TapMeow needs microphone access to detect taps on your MacBook.',
    },
)
