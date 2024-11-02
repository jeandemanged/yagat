#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import tkinter as tk

from yagat.app_context import AppContext


class ViewMenu(tk.Menu):
    def __init__(self, parent, context: AppContext, *args, **kwargs):
        tk.Menu.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.context = context
        parent.add_cascade(label="View", menu=self)
        self.add_command(label='Diagram', command=self.view_diagram)
        self.add_separator()
        self.add_command(label='Load Flow Parameters', command=self.view_load_flow_parameters)

    def view_diagram(self):
        self.context.selected_view = 'Diagram'

    def view_load_flow_parameters(self):
        self.context.selected_view = 'LoadFlowParameters'
