#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import os
import tkinter as tk
from typing import Any

import pandas as pd
import pypowsybl.network as pn

from yagat.app_context import AppContext
from yagat.frames.impl.base_list_view import BaseListView, BaseColumnFormat, StringColumnFormat


class StaticVarCompensatorListView(BaseListView):

    def __init__(self, parent, context: AppContext, *args, **kwargs):
        BaseListView.__init__(self, parent, context, *args, **kwargs)

    @property
    def tab_name(self) -> str:
        return 'Static VAR Compensators'

    @property
    def tab_group_name(self) -> str:
        return 'Static VAR Compensators List'

    def get_data_frame(self) -> pd.DataFrame:
        return self.context.network_structure.static_var_compensators

    def get_column_formats(self) -> dict[str, BaseColumnFormat]:
        formats = super().get_column_formats().copy()
        formats['regulation_mode'] = StringColumnFormat('regulation_mode', editable=True,
                                                        possible_values=['VOLTAGE', 'REACTIVE_POWER', 'OFF'])
        return formats

    def on_entry(self, ident: str, column_name: str, new_value: Any):
        self.context.network.update_static_var_compensators(**{'id': ident, column_name: new_value})
        self.context.network_structure.static_var_compensators.loc[ident, column_name] = new_value

    def filter_data_frame(self, df: pd.DataFrame, voltage_levels: list[str]) -> pd.DataFrame:
        return df.loc[df['voltage_level_id'].isin(voltage_levels)]


if __name__ == "__main__":

    if os.name == 'nt':
        # Fixing the blur UI on Windows
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(2)
    root = tk.Tk()
    ctx = AppContext(root)
    bw = StaticVarCompensatorListView(root, ctx)
    bw.pack(fill="both", expand=True)
    ctx.network = pn.create_four_substations_node_breaker_network()
    ctx.selection = ('network', '', None)
    ctx.selected_tab = bw.tab_name
    root.mainloop()
