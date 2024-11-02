#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import tkinter as tk
from tkinter.messagebox import showinfo

import pypowsybl

import yagat


class HelpMenu(tk.Menu):
    def __init__(self, parent, *args, **kwargs):
        tk.Menu.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        parent.add_cascade(label="Help", menu=self)
        self.add_command(label='About...', command=lambda: showinfo('About YAGAT',
                                                                    'YAGAT v' + yagat.__version__ +
                                                                    '\nBased on PyPowSyBl v' + pypowsybl.__version__))
