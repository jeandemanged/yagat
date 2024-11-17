#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import logging
import os
import tkinter as tk
from typing import List, Optional

import pypowsybl.network as pn

import yagat.widgets as pw
from yagat.app_context import AppContext
from yagat.frames.impl.vertical_scrolled_frame import VerticalScrolledFrame
from yagat.networkstructure import Substation, VoltageLevel, BusView, Connection


class DiagramViewBus(VerticalScrolledFrame):
    def __init__(self, parent, context: AppContext, tab_name: str, bus_view: 'BusView', *args, **kwargs):
        VerticalScrolledFrame.__init__(self, parent, *args, **kwargs)
        self.context = context
        self._tab_name = tab_name
        self.bus_view = bus_view
        self.widgets = []
        self.context.add_selection_changed_listener(self.on_selection_changed)
        self.context.add_tab_changed_listener(lambda _: self.on_selection_changed(self.context.selection))

        def navigate(connection: Connection):
            logging.info(f'Navigating to {connection.equipment_id} side {connection.side}')
            selection_type, _, _ = self.context.selection
            if selection_type == 'substation' and connection.substation is not None:
                new_selection_type = 'substation'
                new_selection_id = connection.substation.substation_id
            else:
                new_selection_type = 'voltage_level'
                new_selection_id = connection.voltage_level.voltage_level_id
            self.context.selection = (new_selection_type, new_selection_id, connection)

        self.navigate_command = navigate

    @property
    def tab_name(self) -> str:
        return self._tab_name

    @property
    def tab_group_name(self) -> str:
        return 'Buses Diagram'

    def on_selection_changed(self, selection: tuple[Optional[str], Optional[str], Optional[Connection]]):
        selection_type, selection_id, selection_connection = selection
        selected_connection_y = 0
        if self.context.selected_tab != self.tab_name:
            return
        logging.info('Start drawing bus view')
        for w in self.widgets:
            w.destroy()
        self.widgets = []
        if selection_type not in ['substation', 'voltage_level']:
            return
        if not selection_id:
            return
        if self.context.selected_tab != self.tab_name:
            return
        network_structure = self.context.network_structure
        what = network_structure.get_substation_or_voltage_level(selection_id)
        substation: Substation
        voltage_levels: List[VoltageLevel]
        if isinstance(what, Substation):
            substation = what
            voltage_levels = substation.voltage_levels
        elif isinstance(what, VoltageLevel):
            voltage_levels = [what]
            substation = what.substation
        else:
            raise RuntimeError(f'Selection {selection} not found')
        if substation:
            s = pw.Substation(self.interior, substation)
            self.widgets.append(s)
            s.pack(anchor=tk.NW, padx=(0, 0))
        pady_vl = 0
        for voltage_level in voltage_levels:
            vl = pw.VoltageLevel(self.interior, voltage_level)
            self.widgets.append(vl)
            vl.pack(anchor=tk.NW, padx=(20, 0), pady=(pady_vl, 0))
            pady_vl = 20

            buses = voltage_level.get_buses(self.bus_view)
            pady_bus = 0
            for bus_idx, bus_s in buses.iterrows():
                bus_id = str(bus_idx)
                b = pw.Bus(self.interior, bus_id, bus_s)
                self.widgets.append(b)
                b.pack(anchor=tk.NW, padx=(40, 0), pady=(pady_bus, 0))
                pady_bus = 20
                connections = voltage_level.get_bus_connections(self.bus_view, bus_id)
                for connection in connections:
                    c = pw.Connection(self.interior, connection, self.navigate_command)
                    self.widgets.append(c)
                    c.pack(anchor=tk.NW, padx=(60, 0))
                    if connection == selection_connection:
                        c.update()
                        logging.info(f'{connection.equipment_id} is selected connection. {c.winfo_geometry()}')
                        selected_connection_y = c.winfo_y()
                        c.highlight()
        self.interior.update()
        self.canvas.update()
        logging.info(f'interior geometry {self.interior.winfo_geometry()}')
        logging.info(f'canvas geometry {self.canvas.winfo_geometry()}')
        interior_height = self.interior.winfo_height()
        canvas_height = self.canvas.winfo_height()

        logging.info(
            f'interior_height={interior_height}, canvas_height={canvas_height},'
            f' selected_connection_y={selected_connection_y}, ')
        if selection_connection and selected_connection_y > (canvas_height / 2) and interior_height:
            # the selection is below visible range, scroll to it
            y_move_to = (selected_connection_y - canvas_height / 2) / interior_height
            logging.info(f'y_move_to={y_move_to}')
            self.canvas.yview_moveto(y_move_to)
        else:
            self.canvas.yview_moveto(0)
        logging.info("end drawing")
        self.context.reset_selected_connection()


if __name__ == "__main__":

    if os.name == 'nt':
        # Fixing the blur UI on Windows
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(2)
    root = tk.Tk()
    ctx = AppContext(root)
    bw = DiagramViewBus(root, ctx, 'Bus-Branch View', BusView.BUS_BRANCH)
    bw.pack(fill="both", expand=True)
    ctx.network = pn.create_ieee9()
    ctx.selection = 'S1'
    ctx.selected_tab = bw.tab_name
    root.mainloop()
