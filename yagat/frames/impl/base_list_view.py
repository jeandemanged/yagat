#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import logging
import tkinter as tk
from abc import ABC, abstractmethod
from typing import Optional, Any

import pandas as pd
import tksheet as tks
from tksheet import num2alpha, float_formatter, int_formatter

from yagat.app_context import AppContext
from yagat.networkstructure import Connection


class BaseColumnFormat(ABC):

    def __init__(self, column_name: str, editable: bool = False):
        self._column_name: str = column_name
        self._editable: bool = editable

    @property
    def column_name(self) -> str:
        return self._column_name

    @property
    def editable(self) -> bool:
        return self._editable


class StringColumnFormat(BaseColumnFormat):

    def __init__(self, column_name: str, editable: bool = False, possible_values=None):
        BaseColumnFormat.__init__(self, column_name, editable)
        if possible_values is None:
            possible_values = list()
        self._possible_values: list[str] = possible_values

    @property
    def possible_values(self) -> list[str]:
        return self._possible_values


class IntegerColumnFormat(BaseColumnFormat):

    def __init__(self, column_name: str, editable: bool = False):
        BaseColumnFormat.__init__(self, column_name, editable)


class DoubleColumnFormat(BaseColumnFormat):

    def __init__(self, column_name: str, editable: bool = False, precision: int = 0):
        BaseColumnFormat.__init__(self, column_name, editable)
        self._precision: int = precision

    @property
    def precision(self) -> int:
        return self._precision


class BooleanColumnFormat(BaseColumnFormat):

    def __init__(self, column_name: str, editable: bool = False):
        BaseColumnFormat.__init__(self, column_name, editable)


PRECISION_POWER = 1
PRECISION_CURRENT = 1
PRECISION_VOLTAGE = 2
PRECISION_VOLTAGE_DEADBAND = PRECISION_VOLTAGE + 1
PRECISION_ANGLE = 5
COLUMN_FORMATS = {
    'name': StringColumnFormat('name', editable=True),
    'v_mag': DoubleColumnFormat('v_mag', precision=PRECISION_VOLTAGE),
    'v_angle': DoubleColumnFormat('v_angle', precision=PRECISION_ANGLE),
    'connected_component': IntegerColumnFormat('connected_component'),
    'synchronous_component': IntegerColumnFormat('synchronous_component'),
    'voltage_level_id': StringColumnFormat('voltage_level_id'),
    'voltage_level_name': StringColumnFormat('voltage_level_name'),
    'country': StringColumnFormat('country'),
    'substation_id': StringColumnFormat('substation_id'),
    'substation_name': StringColumnFormat('substation_name'),
    'nominal_v': DoubleColumnFormat('nominal_v', precision=PRECISION_VOLTAGE),
    'low_voltage_limit': DoubleColumnFormat('low_voltage_limit', precision=PRECISION_VOLTAGE),
    'high_voltage_limit': DoubleColumnFormat('high_voltage_limit', precision=PRECISION_VOLTAGE),
    'target_p': DoubleColumnFormat('target_p', precision=PRECISION_POWER, editable=True),
    'target_v': DoubleColumnFormat('target_v', precision=PRECISION_VOLTAGE, editable=True),
    'target_deadband': DoubleColumnFormat('target_deadband', precision=PRECISION_VOLTAGE_DEADBAND, editable=True),
    'target_q': DoubleColumnFormat('target_q', precision=PRECISION_POWER, editable=True),
    'min_p': DoubleColumnFormat('min_p', precision=PRECISION_POWER, editable=True),
    'max_p': DoubleColumnFormat('max_p', precision=PRECISION_POWER, editable=True),
    'min_q': DoubleColumnFormat('min_q', precision=PRECISION_POWER),
    'max_q': DoubleColumnFormat('max_q', precision=PRECISION_POWER),
    'boundary_p': DoubleColumnFormat('boundary_p', precision=PRECISION_POWER),
    'boundary_q': DoubleColumnFormat('boundary_q', precision=PRECISION_POWER),
    'boundary_v_mag': DoubleColumnFormat('boundary_v_mag', precision=PRECISION_VOLTAGE),
    'boundary_v_angle': DoubleColumnFormat('boundary_v_angle', precision=PRECISION_ANGLE),
    'p0': DoubleColumnFormat('p0', precision=PRECISION_POWER, editable=True),
    'q0': DoubleColumnFormat('q0', precision=PRECISION_POWER, editable=True),
    'p': DoubleColumnFormat('p', precision=PRECISION_POWER),
    'q': DoubleColumnFormat('q', precision=PRECISION_POWER),
    'i': DoubleColumnFormat('i', precision=PRECISION_CURRENT),
    'p1': DoubleColumnFormat('p1', precision=PRECISION_POWER),
    'q1': DoubleColumnFormat('q1', precision=PRECISION_POWER),
    'i1': DoubleColumnFormat('i1', precision=PRECISION_CURRENT),
    'p2': DoubleColumnFormat('p2', precision=PRECISION_POWER),
    'q2': DoubleColumnFormat('q2', precision=PRECISION_POWER),
    'i2': DoubleColumnFormat('i2', precision=PRECISION_CURRENT),
    'p3': DoubleColumnFormat('p3', precision=PRECISION_POWER),
    'q3': DoubleColumnFormat('q3', precision=PRECISION_POWER),
    'i3': DoubleColumnFormat('i3', precision=PRECISION_CURRENT),
    'paired': BooleanColumnFormat('paired'),
    'fictitious': BooleanColumnFormat('fictitious', editable=True),
    'connected': BooleanColumnFormat('connected'),
    'connected1': BooleanColumnFormat('connected1'),
    'connected2': BooleanColumnFormat('connected2'),
    'connected3': BooleanColumnFormat('connected3'),
    'open': BooleanColumnFormat('open'),
    'retained': BooleanColumnFormat('retained'),
    'voltage_regulator_on': BooleanColumnFormat('voltage_regulator_on', editable=True),
    'voltage_regulation_on': BooleanColumnFormat('voltage_regulation_on', editable=True),
    'section_count': IntegerColumnFormat('section_count', editable=True),
    'interchange_target': DoubleColumnFormat('interchange_target', precision=PRECISION_POWER, editable=True),
    'interchange': DoubleColumnFormat('interchange', precision=PRECISION_POWER),
    'ac_interchange': DoubleColumnFormat('ac_interchange', precision=PRECISION_POWER),
    'dc_interchange': DoubleColumnFormat('dc_interchange', precision=PRECISION_POWER),
    'ac': BooleanColumnFormat('ac'),
    'iteration_count': IntegerColumnFormat('iteration_count'),
    'active_power_mismatch': DoubleColumnFormat('active_power_mismatch', precision=PRECISION_POWER),
    'distributed_active_power': DoubleColumnFormat('distributed_active_power', precision=PRECISION_POWER),
}


class BaseListView(tk.Frame, ABC):

    def sheet_selected(self, event):
        logging.info(event)
        if event.eventname == 'select' and event.selected and event.selected.type_ == 'rows' and event.selected.box.from_r == event.selected.box.upto_r - 1:
            logging.info('single row')
            x = self.winfo_pointerx()
            y = self.winfo_pointery()
            abs_coord_x = self.winfo_pointerx() - self.winfo_vrootx()
            abs_coord_y = self.winfo_pointery() - self.winfo_vrooty()
            self.popup_menu.tk_popup(abs_coord_x, abs_coord_y, 0)
        else:
            logging.info('other')

    def sheet_modified(self, event):
        if event.eventname == 'edit_table':
            row = event.selected.row
            column = event.selected.column
            new_value = self.sheet[row, column].data
            ident = self.sheet.get_index_data(row)
            column_name = self.sheet.get_header_data(column)
            logging.info(f'updating "{ident}": {column_name} set to {new_value}')
            self.on_entry(ident=ident, column_name=column_name, new_value=new_value)

    def __init__(self, parent, context: AppContext, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.popup_menu = tk.Menu(self, tearoff=False)
        self.popup_menu.add_command(label="To Bus View")
        self.popup_menu.add_command(label="To Bus/Breaker View")
        self.sheet = tks.Sheet(self, index_align='left')
        self.sheet.enable_bindings('edit_cell', 'single_select',
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
        self.sheet.bind("<<SheetModified>>", self.sheet_modified)
        self.sheet.bind("<<SheetSelect>>", self.sheet_selected)
        self.context = context
        self.context.add_selection_changed_listener(self.on_selection_changed)
        self.context.add_tab_changed_listener(lambda _: self.on_selection_changed(self.context.selection))

        self.sheet.set_index_width(300)
        self.sheet.pack(fill="both", expand=True)

    @property
    @abstractmethod
    def tab_name(self) -> str:
        return 'tab name'

    @property
    @abstractmethod
    def tab_group_name(self) -> str:
        return 'tab group name'

    @abstractmethod
    def get_data_frame(self) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def filter_data_frame(self, df: pd.DataFrame, voltage_levels: list[str]) -> pd.DataFrame:
        return df

    @abstractmethod
    def get_column_formats(self) -> dict[str, BaseColumnFormat]:
        return COLUMN_FORMATS

    @abstractmethod
    def on_entry(self, ident: str, column_name: str, new_value: Any):
        logging.warning('Update not implemented for this change')

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
        self._format_columns(df)

    def _format_columns(self, df):
        column_formats = self.get_column_formats()
        for idx, column_name in enumerate(df.columns):
            col = self.sheet[num2alpha(idx)]
            if column_name not in column_formats:
                col.readonly(readonly=True)
                continue
            col_format = column_formats[column_name]
            col.readonly(readonly=not col_format.editable)
            if isinstance(col_format, StringColumnFormat):
                if col_format.possible_values:
                    col.dropdown(values=col_format.possible_values, set_values=dict(
                        zip([(i, idx) for i in range(len(df.index))],
                            df.reset_index()[col_format.column_name].to_list())))
            elif isinstance(col_format, IntegerColumnFormat):
                col.format(int_formatter())
            elif isinstance(col_format, DoubleColumnFormat):
                col.format(float_formatter(decimals=col_format.precision))
            elif isinstance(col_format, BooleanColumnFormat):
                state = 'normal' if col_format.editable else 'disabled'
                col.checkbox(state=state)

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
