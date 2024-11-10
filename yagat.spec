# -*- mode: python ; coding: utf-8 -*-
#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import platform
import shutil
import sys

sys.path.append('./')
from yagat import __version__

from PyInstaller.utils.hooks import collect_dynamic_libs

datas = [('yagat/images', 'yagat/images')]
binaries = []
hiddenimports = ['PIL._tkinter_finder']
binaries += collect_dynamic_libs('pypowsybl')

a = Analysis(
    ['yagat/app.py'],
    pathex=['yagat'],
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
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YAGAT',
    icon='yagat/images/logo.png',
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
)
release_name=f'yagat_{__version__}_{platform.system()}'
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=release_name,
)
print(f'Zipping release into {release_name}.zip')
shutil.make_archive(f'{release_name}', 'zip', f'dist/{release_name}')
