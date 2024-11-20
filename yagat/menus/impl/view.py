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
        self.add_command(label='Buses Diagram',
                         command=lambda: self.update_view_and_tab_group('TreeAndTabs', 'Buses Diagram'))
        self.add_separator()
        self.add_command(label='Buses',
                         command=lambda: self.update_view_and_tab_group('TreeAndTabs', 'Buses List'))
        self.add_command(label='Generators',
                         command=lambda: self.update_view_and_tab_group('TreeAndTabs', 'Generators List'))
        self.add_command(label='Loads',
                         command=lambda: self.update_view_and_tab_group('TreeAndTabs', 'Loads List'))
        self.add_command(label='Lines',
                         command=lambda: self.update_view_and_tab_group('TreeAndTabs', 'Lines List'))
        self.add_command(label='Transformers',
                         command=lambda: self.update_view_and_tab_group('TreeAndTabs', 'Transformers List'))
        self.add_command(label='Shunt Compensators',
                         command=lambda: self.update_view_and_tab_group('TreeAndTabs', 'Shunt Compensators List'))
        self.add_command(label='Static VAR Compensators',
                         command=lambda: self.update_view_and_tab_group('TreeAndTabs', 'Static VAR Compensators List'))
        self.add_command(label='HVDC Lines and Converters',
                         command=lambda: self.update_view_and_tab_group('TreeAndTabs', 'HVDC List'))
        self.add_command(label='Switches',
                         command=lambda: self.update_view_and_tab_group('TreeAndTabs', 'Switches List'))
        self.add_command(label='Areas',
                         command=lambda: self.update_view_and_tab_group('TreeAndTabs', 'Areas List'))
        self.add_separator()
        self.add_command(label='Load Flow Parameters', command=self.view_load_flow_parameters)
        self.add_separator()
        self.add_command(label='Logs', command=self.view_logs)

    def update_view_and_tab_group(self, view: str, tab_group: str) -> None:
        self.context.selected_view = view
        self.context.selected_tab_group = tab_group

    def view_load_flow_parameters(self):
        self.context.selected_view = 'LoadFlowParameters'

    def view_logs(self):
        self.context.selected_view = 'Logs'
