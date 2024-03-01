#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import tkinter as tk
from tkinter import font
from tkinter import ttk
from typing import Optional


class LabelValue(tk.Frame):
    BOLD_FONT = None

    def __init__(self, parent, label: str, value: tk.StringVar, unit: Optional[str] = None, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        if not LabelValue.BOLD_FONT:
            font_copy = font.nametofont('TkDefaultFont').copy()
            font_copy.config(weight='bold')
            LabelValue.BOLD_FONT = font_copy

        self._label = ttk.Label(self, text=label)
        self._label.pack(side=tk.LEFT)

        self._value_var = value
        self._value = ttk.Label(self, textvariable=self._value_var, font=LabelValue.BOLD_FONT)
        self._value.pack(side=tk.LEFT)

        if unit:
            self._unit = ttk.Label(self, text=unit)
            self._unit.pack(side=tk.LEFT)


if __name__ == "__main__":
    root = tk.Tk()
    LabelValue(root, 'label1:', tk.StringVar(value='value1')).pack(side=tk.LEFT)
    LabelValue(root, 'label2:', tk.StringVar(value='value2'), 'kV').pack(side=tk.LEFT, padx=10)
    root.mainloop()
