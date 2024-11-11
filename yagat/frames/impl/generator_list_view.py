#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import os
import tkinter as tk
from typing import Optional

import pypowsybl.network as pn
import tksheet as tks

from yagat.app_context import AppContext
from yagat.networkstructure import Connection


class GeneratorListView(tk.Frame):

    def __init__(self, parent, context: AppContext, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.sheet = tks.Sheet(self, index_align='left', data=[[1, 2], [3, 4]])
        self.sheet.enable_bindings('single_select',
                                   'drag_select',
                                   'row_select',
                                   'column_select',
                                   'copy',
                                   'column_width_resize',
                                   'double_click_column_resize',
                                   'double_click_row_resize',
                                   'row_width_resize',
                                   'column_height_resize',
                                   'arrowkeys',
                                   )
        self.context = context
        self.context.add_selection_changed_listener(self.on_selection_changed)
        self.variables = []

        self.sheet.set_index_width(300)
        self.sheet.pack(fill="both", expand=True)

    def on_selection_changed(self, selection: tuple[Optional[str], Optional[str], Optional[Connection]]):
        generators = self.context.network_structure.generators
        voltage_levels = []
        if selection[0] == 'voltage_level':
            voltage_levels = [selection[1]]
        elif selection[0] == 'substation':
            voltage_levels = [vl.voltage_level_id for vl in self.context.network_structure.get_substation(selection[1]).voltage_levels]
        if voltage_levels:
            generators = generators.loc[generators['voltage_level_id'].isin(voltage_levels)]
        self.sheet.data = [l.tolist() for l in generators.to_numpy()]
        self.sheet.set_index_data(generators.index.tolist())
        self.sheet.set_header_data(generators.columns)
        self.sheet.set_all_cell_sizes_to_text()

    @property
    def tab_name(self) -> str:
        return 'Generator list'


if __name__ == "__main__":

    if os.name == 'nt':
        # Fixing the blur UI on Windows
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(2)
    root = tk.Tk()
    ctx = AppContext(root)
    bw = GeneratorListView(root, ctx)
    bw.pack(fill="both", expand=True)
    ctx.network = pn.create_ieee9()
    ctx.selection = 'S1'
    ctx.selected_tab = bw.tab_name
    root.mainloop()
