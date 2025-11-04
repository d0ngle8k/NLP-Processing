# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# Dynamically include underthesea model data if present
_datas = []
_home_models = Path.home() / ".underthesea"
if _home_models.exists():
    # (source_path, target_relative_dir)
    _datas.append((str(_home_models), ".underthesea"))
    
# Include schema.sql for runtime DB initialization
_datas.append((str(Path('database') / 'schema.sql'), 'database'))

_hiddenimports = [
    "babel.numbers",  # tkcalendar/babel hidden import to avoid packaging issues
]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=_datas,
    hiddenimports=_hiddenimports,
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TrinhLyAo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # windowed app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Put dist into ./app and work files into ./build
distpath = 'app'
workpath = 'build'

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TrinhLyAo',
)
