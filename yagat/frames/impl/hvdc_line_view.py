#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import os
import tkinter as tk

import pandas as pd
import pypowsybl.network as pn

from yagat.app_context import AppContext
from yagat.frames.impl.base_list_view import BaseListView


class HvdcLineView(BaseListView):

    def __init__(self, parent, context: AppContext, *args, **kwargs):
        BaseListView.__init__(self, parent, context, *args, **kwargs)

    @property
    def tab_name(self) -> str:
        return 'HVDC Lines'

    def get_data_frame(self) -> pd.DataFrame:
        return self.context.network_structure.hvdc_lines

    def filter_data_frame(self, df: pd.DataFrame, voltage_levels: list[str]) -> pd.DataFrame:
        return df  #TODO


if __name__ == "__main__":

    if os.name == 'nt':
        # Fixing the blur UI on Windows
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(2)
    root = tk.Tk()
    ctx = AppContext(root)
    bw = HvdcLineView(root, ctx)
    bw.pack(fill="both", expand=True)
    ctx.network = pn.create_four_substations_node_breaker_network()
    ctx.selection = ('network', '', None)
    ctx.selected_tab = bw.tab_name
    root.mainloop()