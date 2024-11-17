#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import tkinter as tk

from yagat.app_context import AppContext
from yagat.frames.impl.tabs_view import TabsView
from yagat.frames.impl.tree_view import TreeView


class TreeAndTabs(tk.Frame):
    def __init__(self, parent, context, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.context = context

        self.paned_window = tk.PanedWindow(self.parent, orient=tk.HORIZONTAL, showhandle=False, sashrelief=tk.RAISED,
                                           sashpad=4, sashwidth=8)

        self.tree_view = TreeView(self.paned_window, self.context)
        self.right_frame = TabsView(self.paned_window, self.context)

        self.paned_window.add(self.tree_view)
        self.paned_window.add(self.right_frame)


if __name__ == "__main__":
    root = tk.Tk()
    ctx = AppContext(root)
    v = TreeAndTabs(root, ctx)
    v.paned_window.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
