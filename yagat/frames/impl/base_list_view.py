#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import tkinter as tk
from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import tksheet as tks

from yagat.app_context import AppContext
from yagat.networkstructure import Connection


class BaseListView(tk.Frame, ABC):

    def __init__(self, parent, context: AppContext, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.sheet = tks.Sheet(self, index_align='left')
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

        self.sheet.set_index_width(300)
        self.sheet.pack(fill="both", expand=True)

    @property
    @abstractmethod
    def tab_name(self) -> str:
        pass

    @abstractmethod
    def get_data_frame(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def filter_data_frame(self, df: pd.DataFrame, voltage_levels: list[str]) -> pd.DataFrame:
        pass

    def on_selection_changed(self, selection: tuple[Optional[str], Optional[str], Optional[Connection]]):
        if not self.context.network_structure:
            self.sheet.data = []
            return
        df = self.get_data_frame()
        voltage_levels = self.filtered_voltage_levels(selection)
        if voltage_levels:
            df = self.filter_data_frame(df, voltage_levels)
        self.sheet.data = [l.tolist() for l in df.to_numpy()]
        self.sheet.set_index_data(df.index.tolist())
        self.sheet.set_header_data(df.columns)
        self.sheet.set_all_cell_sizes_to_text()

    def filtered_voltage_levels(self,
                                selection: tuple[Optional[str], Optional[str], Optional[Connection]]) -> list[str]:
        voltage_levels: list[str] = []
        if selection[0] == 'network' or not selection[0] or not selection[1]:
            return voltage_levels
        elif selection[0] == 'voltage_level':
            voltage_levels = [selection[1]]
        elif selection[0] == 'substation':
            voltage_levels = [vl.voltage_level_id for vl in
                              self.context.network_structure.get_substation(selection[1]).voltage_levels]
        return voltage_levels
