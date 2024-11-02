#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import tkinter as tk
from tkinter import ttk

from yagat.app_context import AppContext


class StatusBar(tk.Frame):
    def __init__(self, parent, context: AppContext, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.context = context
        self.sizegrip = ttk.Sizegrip(self)
        self.sizegrip.pack(side=tk.LEFT)
        self.statusbar = ttk.Label(parent, text='Ready', borderwidth=1, relief=tk.SUNKEN)
        self.statusbar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.context.add_status_text_listener(lambda value: self.statusbar.config(text=value))


if __name__ == "__main__":
    root = tk.Tk()
    # disable tear-off menus
    root.option_add('*tearOff', False)
    ctx = AppContext(root)
    label = ttk.Label(root, text='app goes here')
    label.pack(expand=True, fill=tk.BOTH)
    StatusBar(root, ctx).pack(fill=tk.X)
    root.mainloop()
