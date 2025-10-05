# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['zoom_auto_leaver_macos.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('README_macOS.md', '.'),
    ],
    hiddenimports=[
        'PyObjC',
        'AppKit',
        'Cocoa',
        'pyautogui',
        'pyobjc-core',
        'pyobjc-framework-Cocoa',
        'pyobjc-framework-Quartz',
        'pyobjc-framework-ApplicationServices'
    ],
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
    name='Zoom Auto Leaver',
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
)

app = BUNDLE(
    exe,
    name='Zoom Auto Leaver.app',
    icon=None,
    bundle_identifier='com.achibukz.zoomautoleaver',
    info_plist={
        'CFBundleName': 'Zoom Auto Leaver',
        'CFBundleDisplayName': 'Zoom Auto Leaver',
        'CFBundleIdentifier': 'com.achibukz.zoomautoleaver',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleExecutable': 'Zoom Auto Leaver',
        'CFBundlePackageType': 'APPL',
        'CFBundleIconFile': 'app_icon',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.12.0',
        'NSAppleEventsUsageDescription': 'This app needs to send Apple Events to control Zoom.',
        'NSSystemAdministrationUsageDescription': 'This app needs system access to monitor and control applications.',
        'NSAccessibilityUsageDescription': 'This app needs Accessibility access to read window information and send keystrokes to leave Zoom meetings automatically.',
    },
)