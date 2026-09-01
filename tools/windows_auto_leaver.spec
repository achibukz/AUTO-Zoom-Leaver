# -*- mode: python ; coding: utf-8 -*-

import os

from PyInstaller.utils.hooks import collect_submodules


build_mode = os.environ.get("AUTO_ZOOM_LEAVER_BUILD_MODE", "onefile").casefold()
if build_mode not in {"onedir", "onefile"}:
    raise ValueError("AUTO_ZOOM_LEAVER_BUILD_MODE must be 'onedir' or 'onefile'")


hidden_imports = [
    "psutil",
    "pyautogui",
    *collect_submodules("pywinauto"),
]

a = Analysis(
    ["../zoom_auto_leaver.py"],
    pathex=[".."],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

if build_mode == "onedir":
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name="AutoZoomLeaver",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True,
    )
    COLLECT(
        exe,
        a.binaries,
        a.datas,
        a.zipfiles,
        name="AutoZoomLeaver",
    )
else:
    EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        a.zipfiles,
        name="AutoZoomLeaver",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True,
    )
