#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import logging
import tkinter as tk
import traceback
from tkinter.messagebox import showerror

import yagat
from yagat.app_context import AppContext
from yagat.frames.impl.load_flow_parameters import LoadFlowParametersView
from yagat.frames.impl.logs_view import LogsView
from yagat.frames.impl.status_bar import StatusBar
from yagat.frames.impl.tree_and_tabs import TreeAndTabs
from yagat.menus import MenuBar
from yagat.utils import get_centered_geometry


class MainApplication(tk.Frame):

    @staticmethod
    def show_error(*args):
        logging.exception('Exception occurred')
        err = traceback.format_exception(*args)
        showerror(type(args[1]).__name__ + ' 😢: ' + str(args[1]), ''.join(err))

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.report_callback_exception = self.show_error
        # disable tear-off menus
        self.parent.option_add('*tearOff', False)
        self.parent.title('YAGAT v' + yagat.__version__)
        self.parent.geometry(get_centered_geometry(parent, 1000, 600))
        self.context = AppContext(parent)

        self.context.add_view_changed_listener(self.on_view_changed)

        self.menubar = MenuBar(self, self.context)
        self.parent.config(menu=self.menubar)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        self.container = container = tk.Frame(self.parent)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        self.tree_and_diagram = TreeAndTabs(container, self.context)
        self.tree_and_diagram.paned_window.grid(row=0, column=0, sticky="nsew")

        self.lfp = LoadFlowParametersView(container, self.context)
        self.lfp.grid(row=0, column=0, sticky="nsew")

        self.logs = LogsView(container)
        self.logs.grid(row=0, column=0, sticky="nsew")

        self.tree_and_diagram.paned_window.tkraise()

        self.statusbar = StatusBar(self.parent, self.context)
        self.statusbar.pack(fill=tk.X)

    def on_view_changed(self, new_view):
        if new_view == 'TreeAndTabs':
            self.tree_and_diagram.paned_window.tkraise()
        elif new_view == 'LoadFlowParameters':
            self.lfp.tkraise()
        elif new_view == 'Logs':
            self.logs.tkraise()
        else:
            raise ValueError(f'Unknown view {new_view}')


if __name__ == "__main__":
    root = tk.Tk()
    # disable tear-off menus
    root.option_add('*tearOff', False)
    MainApplication(root)
    root.mainloop()
