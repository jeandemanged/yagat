#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import tkinter as tk

from .file import FileMenu
from .help import HelpMenu
from .run import RunMenu
from .view import ViewMenu


class MenuBar(tk.Menu):
    def __init__(self, parent, context, *args, **kwargs):
        tk.Menu.__init__(self, parent, *args, **kwargs)
        self.file_menu = FileMenu(self, context)
        self.run_menu = RunMenu(self, context)
        self.view_menu = ViewMenu(self, context)
        self.help_menu = HelpMenu(self)
