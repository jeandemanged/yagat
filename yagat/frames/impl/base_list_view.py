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
from tksheet import num2alpha, float_formatter, int_formatter

from yagat.app_context import AppContext
from yagat.networkstructure import Connection


class BaseColumnFormat(ABC):

    def __init__(self, column_name: str):
        self._column_name: str = column_name

    @property
    def column_name(self) -> str:
        return self._column_name


class StringColumnFormat(BaseColumnFormat):

    def __init__(self, column_name: str):
        BaseColumnFormat.__init__(self, column_name)


class IntegerColumnFormat(BaseColumnFormat):

    def __init__(self, column_name: str):
        BaseColumnFormat.__init__(self, column_name)


class DoubleColumnFormat(BaseColumnFormat):

    def __init__(self, column_name: str, precision: int):
        BaseColumnFormat.__init__(self, column_name)
        self._precision: int = precision

    @property
    def precision(self) -> int:
        return self._precision


class BooleanColumnFormat(BaseColumnFormat):

    def __init__(self, column_name: str):
        BaseColumnFormat.__init__(self, column_name)


COLUMN_FORMATS = {
    'name': StringColumnFormat('name'),
    'v_mag': DoubleColumnFormat('v_mag', 2),
    'v_angle': DoubleColumnFormat('v_angle', 5),
    'connected_component': IntegerColumnFormat('connected_component'),
    'synchronous_component': IntegerColumnFormat('synchronous_component'),
    'voltage_level_id': StringColumnFormat('voltage_level_id'),
    'voltage_level_name': StringColumnFormat('voltage_level_name'),
    'country': StringColumnFormat('country'),
    'substation_id': StringColumnFormat('substation_id'),
    'substation_name': StringColumnFormat('substation_name'),
    'nominal_v': DoubleColumnFormat('nominal_v', 2),
    'low_voltage_limit': DoubleColumnFormat('low_voltage_limit', 2),
    'high_voltage_limit': DoubleColumnFormat('high_voltage_limit', 2),
    'target_p': DoubleColumnFormat('target_p', 1),
    'target_v': DoubleColumnFormat('target_v', 2),
    'target_q': DoubleColumnFormat('target_q', 1),
    'min_p': DoubleColumnFormat('min_p', 1),
    'max_p': DoubleColumnFormat('max_p', 1),
    'min_q': DoubleColumnFormat('min_q', 1),
    'max_q': DoubleColumnFormat('max_q', 1),
    'boundary_p': DoubleColumnFormat('boundary_p', 1),
    'boundary_q': DoubleColumnFormat('boundary_q', 1),
    'boundary_v_mag': DoubleColumnFormat('boundary_v_mag', 2),
    'boundary_v_angle': DoubleColumnFormat('boundary_v_angle', 5),
    'p0': DoubleColumnFormat('p0', 1),
    'q0': DoubleColumnFormat('q0', 1),
    'p': DoubleColumnFormat('p', 1),
    'q': DoubleColumnFormat('q', 1),
    'i': DoubleColumnFormat('i', 1),
    'p1': DoubleColumnFormat('p1', 1),
    'q1': DoubleColumnFormat('q1', 1),
    'i1': DoubleColumnFormat('i1', 1),
    'p2': DoubleColumnFormat('p2', 1),
    'q2': DoubleColumnFormat('q2', 1),
    'i2': DoubleColumnFormat('i2', 1),
    'p3': DoubleColumnFormat('p3', 1),
    'q3': DoubleColumnFormat('q3', 1),
    'i3': DoubleColumnFormat('i3', 1),
    'paired': BooleanColumnFormat('paired'),
    'fictitious': BooleanColumnFormat('fictitious'),
    'connected': BooleanColumnFormat('connected'),
    'connected1': BooleanColumnFormat('connected1'),
    'connected2': BooleanColumnFormat('connected2'),
    'connected3': BooleanColumnFormat('connected3'),
    'open': BooleanColumnFormat('open'),
    'retained': BooleanColumnFormat('retained'),
    'voltage_regulator_on': BooleanColumnFormat('open'),
}


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
        self.context.add_tab_changed_listener(lambda _: self.on_selection_changed(self.context.selection))

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
        if self.context.selected_tab != self.tab_name:
            return
        self.sheet.reset()
        if not self.context.network_structure:
            return
        df = self.get_data_frame()
        voltage_levels = self.filtered_voltage_levels(selection)
        if voltage_levels:
            df = self.filter_data_frame(df, voltage_levels)
        self.sheet.data = [l.tolist() for l in df.to_numpy()]
        self.sheet.set_index_data(df.index.tolist())
        self.sheet.set_header_data(df.columns)
        for idx, column_name in enumerate(df.columns):
            if column_name not in COLUMN_FORMATS:
                continue
            col_format = COLUMN_FORMATS[column_name]
            col = self.sheet[num2alpha(idx)]
            if isinstance(col_format, StringColumnFormat):
                continue
            elif isinstance(col_format, IntegerColumnFormat):
                col.format(int_formatter())
            elif isinstance(col_format, DoubleColumnFormat):
                col.format(float_formatter(decimals=col_format.precision))
            elif isinstance(col_format, BooleanColumnFormat):
                col.checkbox(state='disabled')

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
