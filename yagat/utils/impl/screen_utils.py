#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import os
import tkinter as tk


def get_screen_infos(root: tk.Tk) -> tuple[int, int]:
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    scale = 1.0

    if os.name == 'nt':
        # Fix Tk's winfo not accounting windows scaling
        from ctypes import windll

        scale = windll.shcore.GetScaleFactorForDevice(0) / 100

    return scale * screen_width, scale * screen_height


def get_centered_geometry(root: tk.Tk, width: int, height: int) -> str:
    screen_width, screen_height = get_screen_infos(root)
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    return f'{width}x{height}+{x}+{y}'
