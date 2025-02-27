#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import logging
import os
import textwrap
import tkinter as tk

import pypowsybl.loadflow as lf
import tksheet as tks
from pypowsybl.loadflow import BalanceType, VoltageInitMode, ConnectedComponentMode

from yagat.app_context import AppContext


class LoadFlowParametersView(tk.Frame):

    def sheet_modified(self, event):
        # FIXME: handling of invalid values
        if event.eventname == 'edit_table':
            row = event.selected.row
            column = event.selected.column
            new_value = self.sheet[row, column].data
            param = self.sheet.get_index_data(row)
            lf_parameters = self.context.lf_parameters
            if param == 'distributedSlack':
                lf_parameters.distributed_slack = new_value
            elif param == 'balanceType':
                lf_parameters.balance_type = BalanceType.__members__[new_value]
            elif param == 'countriesToBalance':
                lf_parameters.countries_to_balance = str(new_value).split(',')
            elif param == 'voltageInitMode':
                lf_parameters.voltage_init_mode = VoltageInitMode.__members__[new_value]
            elif param == 'readSlackBus':
                lf_parameters.read_slack_bus = new_value
            elif param == 'writeSlackBus':
                lf_parameters.write_slack_bus = new_value
            elif param == 'useReactiveLimits':
                lf_parameters.use_reactive_limits = new_value
            elif param == 'phaseShifterRegulationOn':
                lf_parameters.phase_shifter_regulation_on = new_value
            elif param == 'transformerVoltageControlOn':
                lf_parameters.transformer_voltage_control_on = new_value
            elif param == 'shuntCompensatorVoltageControlOn':
                lf_parameters.shunt_compensator_voltage_control_on = new_value
            elif param == 'connectedComponentMode':
                lf_parameters.connected_component_mode = ConnectedComponentMode.__members__[new_value]
            elif param == 'twtSplitShuntAdmittance':
                lf_parameters.twt_split_shunt_admittance = new_value
            elif param == 'dcUseTransformerRatio':
                lf_parameters.dc_use_transformer_ratio = new_value
            elif param == 'dcPowerFactor':
                lf_parameters.dc_power_factor = new_value
            else:
                new_value = str(new_value)
                lf_parameters.provider_parameters[param] = str(new_value)
            logging.info(f'Load Flow Parameter "{param}" set to {new_value}')
            logging.info(f'Load Flow Parameters: {lf_parameters}')

    def __init__(self, parent, context: AppContext, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.sheet = tks.Sheet(self, index_align='left')
        self.sheet.enable_bindings('edit_cell',
                                   'single_select',
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
        self.context = context

        balance_types = [BalanceType.PROPORTIONAL_TO_GENERATION_P.name,
                         BalanceType.PROPORTIONAL_TO_GENERATION_P_MAX.name,
                         BalanceType.PROPORTIONAL_TO_GENERATION_PARTICIPATION_FACTOR.name,
                         BalanceType.PROPORTIONAL_TO_GENERATION_REMAINING_MARGIN.name,
                         BalanceType.PROPORTIONAL_TO_LOAD.name,
                         BalanceType.PROPORTIONAL_TO_CONFORM_LOAD.name]

        voltage_init_modes = [VoltageInitMode.UNIFORM_VALUES.name,
                              VoltageInitMode.DC_VALUES.name,
                              VoltageInitMode.PREVIOUS_VALUES.name]
        connected_component_modes = [ConnectedComponentMode.MAIN.name,
                                     ConnectedComponentMode.ALL.name]

        parameters = lf.get_provider_parameters()
        lf_parameters = self.context.lf_parameters
        parameters.loc['distributedSlack'] = ['SlackDistribution', 'Enable distributed slack', 'BOOLEAN', str(lf_parameters.distributed_slack), '']
        parameters.loc['balanceType'] = ['SlackDistribution', 'Slack distribution balance type', 'STRING', lf_parameters.balance_type.name, f'[{', '.join(balance_types)}]']
        parameters.loc['countriesToBalance'] = ['SlackDistribution', 'Countries to balance', 'STRING', ','.join(lf_parameters.countries_to_balance), '']
        parameters.loc['voltageInitMode'] = ['VoltageInit', 'Voltage Initialization Mode', 'STRING', lf_parameters.voltage_init_mode.name, f'[{', '.join(voltage_init_modes)}]']
        parameters.loc['readSlackBus'] = ['SlackDistribution', 'Read slack bus', 'BOOLEAN', str(lf_parameters.read_slack_bus), '']
        parameters.loc['writeSlackBus'] = ['SlackDistribution', 'Write slack bus', 'BOOLEAN', str(lf_parameters.write_slack_bus), '']
        parameters.loc['useReactiveLimits'] = ['VoltageControls', 'Use reactive limits', 'BOOLEAN', str(lf_parameters.use_reactive_limits), '']
        parameters.loc['phaseShifterRegulationOn'] = ['PhaseControl', 'Enable Phase Shifter control', 'BOOLEAN', str(lf_parameters.phase_shifter_regulation_on), '']
        parameters.loc['transformerVoltageControlOn'] = ['TransformerVoltageControl', 'Enable Transformer Voltage control', 'BOOLEAN', str(lf_parameters.transformer_voltage_control_on), '']
        parameters.loc['shuntCompensatorVoltageControlOn'] = ['ShuntVoltageControl', 'Enable Shunt Compensator Voltage control', 'BOOLEAN', str(lf_parameters.shunt_compensator_voltage_control_on), '']
        parameters.loc['connectedComponentMode'] = ['Performance', 'Connected component mode', 'STRING', lf_parameters.connected_component_mode.name, f'[{', '.join(connected_component_modes)}]']
        parameters.loc['twtSplitShuntAdmittance'] = ['Model', 'Split transformers shunt admittance', 'BOOLEAN', str(lf_parameters.twt_split_shunt_admittance), '']
        parameters.loc['dcUseTransformerRatio'] = ['DC', 'Ratio of transformers should be used in the flow equations in a DC power flow', 'BOOLEAN', str(lf_parameters.dc_use_transformer_ratio), '']
        parameters.loc['dcPowerFactor'] = ['DC', 'Power factor used to convert current limits into active power limits in DC calculations', 'BOOLEAN', str(lf_parameters.dc_power_factor), '']

        i_row = -1

        for param_idx, param_s in parameters.sort_values(by=['category_key', 'name']).iterrows():
            i_col = -1
            i_row += 1
            param_name = str(param_idx)
            param_category_key = param_s.category_key
            param_description = param_s.description
            param_type = param_s.type
            param_default = param_s.default
            if param_default == '[]':
                param_default = ''
            param_possible_values = None
            if param_s.possible_values and param_s.possible_values != '[]':
                param_possible_values = param_s.possible_values[1:-1].split(', ')

            i_col += 1
            if param_type == 'BOOLEAN':
                self.sheet[i_row, i_col].checkbox(checked=param_default.lower() == 'true')
            elif param_type == 'STRING':
                if param_possible_values:
                    self.sheet[i_row, i_col].dropdown(
                        values=param_possible_values,
                        set_value=param_default,
                    )
                else:
                    self.sheet[i_row, i_col].data = param_default
            elif param_type == 'STRING_LIST':
                # FIXME: make use of param_possible_values.
                #  tksheet does not support multiple selection in dropdown.
                #  also careful of OLF param where order is significant such as voltageTargetPriorities.
                if param_default.startswith('[') and param_default.endswith(']'):
                    # clean it, we should fix this in OLF
                    param_default = param_default[1:-1]
                self.sheet[i_row, i_col].data = param_default
            elif param_type == 'INTEGER':
                self.sheet[i_row, i_col].data = param_default
                self.sheet.format_cell(i_row, i_col, formatter_options=tks.int_formatter())
            elif param_type == 'DOUBLE':
                self.sheet[i_row, i_col].data = param_default
                self.sheet.format_cell(i_row, i_col, formatter_options=tks.float_formatter(decimals=5))

            i_col += 1
            self.sheet[i_row, i_col].data = param_category_key
            i_col += 1
            self.sheet[i_row, i_col].data = '\n'.join(textwrap.wrap(param_description))
            self.sheet.set_index_data(r=i_row, value=param_name)

        self.sheet.set_header_data(c=0, value="Value")
        self.sheet.set_header_data(c=1, value="Category")
        self.sheet["B"].readonly(readonly=True)
        self.sheet.set_header_data(c=2, value="Description")
        self.sheet["C"].readonly(readonly=True)
        self.sheet.set_all_cell_sizes_to_text()
        self.sheet.set_index_width(300)
        self.sheet.pack(fill="both", expand=True)


if __name__ == "__main__":
    if os.name == 'nt':
        # Fixing the blur UI on Windows
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(2)
    root = tk.Tk()
    # Windows & OSX
    root.unbind_class("TCombobox", "<MouseWheel>")

    # Linux and other *nix systems:
    root.unbind_class("TCombobox", "<ButtonPress-4>")
    root.unbind_class("TCombobox", "<ButtonPress-5>")
    ctx = AppContext(root)
    lfpv = LoadFlowParametersView(root, ctx)
    lfpv.pack(fill="both", expand=True)
    root.mainloop()
