#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import math
import tkinter as tk

import pandas as pd
import pypowsybl.network as pn

import yagat.networkstructure as ns
import yagat.widgets as pw
from yagat.utils import format_v_mag, format_v_angle, format_power


class Substation(tk.Frame):
    def __init__(self, parent, substation: 'ns.Substation', *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self._name_var = tk.StringVar(value=substation.name)
        self._name_label = pw.LabelValue(self, 'Substation:', self._name_var)
        self._name_label.pack(side=tk.LEFT)

        self._id_var = tk.StringVar(value=substation.substation_id)
        self._id_label = pw.LabelValue(self, 'id:', self._id_var)
        self._id_label.pack(side=tk.LEFT, padx=(10, 0))


class VoltageLevel(tk.Frame):
    def __init__(self, parent, voltage_level: 'ns.VoltageLevel', *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self._name_var = tk.StringVar(value=voltage_level.name)
        self._name_label = pw.LabelValue(self, 'VoltageLevel:', self._name_var)
        self._name_label.pack(side=tk.LEFT)

        self._nominal_v_var = tk.StringVar(value=format_v_mag(voltage_level.get_data().nominal_v))
        self._nominal_v_label = pw.LabelValue(self, 'Nominal voltage:', self._nominal_v_var, 'kV')
        self._nominal_v_label.pack(side=tk.LEFT, padx=(10, 0))

        self._id_var = tk.StringVar(value=voltage_level.voltage_level_id)
        self._id_label = pw.LabelValue(self, 'id:', self._id_var)
        self._id_label.pack(side=tk.LEFT, padx=(10, 0))


class Bus(tk.Frame):
    def __init__(self, parent, bus_id: str, bus_data: pd.Series, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self._name_var = tk.StringVar(value=str(bus_data['name']))
        self._name_label = pw.LabelValue(self, 'Bus:', self._name_var)
        self._name_label.pack(side=tk.LEFT)

        self._v_mag_var = tk.StringVar(value=format_v_mag(bus_data.v_mag))
        self._v_mag_label = pw.LabelValue(self, 'Vmag:', self._v_mag_var, 'kV')
        self._v_mag_label.pack(side=tk.LEFT, padx=(10, 0))

        self._v_angle_var = tk.StringVar(value=format_v_angle(bus_data.v_angle))
        self._v_angle_label = pw.LabelValue(self, 'Vangle:', self._v_angle_var, '°')
        self._v_angle_label.pack(side=tk.LEFT, padx=(10, 0))

        cc = self.clean_component(bus_data.connected_component)
        sc = self.clean_component(bus_data.synchronous_component)
        self._component_var = tk.StringVar(value=f'CC{cc} SC{sc}')
        self._component_var = pw.LabelValue(self, 'Island:', self._component_var)
        self._component_var.pack(side=tk.LEFT, padx=(10, 0))

        self._id_var = tk.StringVar(value=bus_id)
        self._id_label = pw.LabelValue(self, 'id:', self._id_var)
        self._id_label.pack(side=tk.LEFT, padx=(10, 0))

    @staticmethod
    def clean_component(component_num):
        if math.isnan(component_num):
            component_num = '-'
        else:
            component_num = int(component_num)
        return component_num


class Connection(tk.Frame):
    def __init__(self, parent, connection: 'ns.Connection', navigate_command, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.canvas = tk.Canvas(self, width=550, height=60, highlightthickness=0)
        self.canvas.create_line(0, 0, 0, 60, fill="black", width=15)
        self.canvas.create_line(0, 30, 30, 30, fill="black", width=2)
        self.connection = connection
        self.navigate_command = navigate_command
        if connection.equipment_type == ns.EquipmentType.SWITCH:
            self.canvas.create_line(30, 30, 50, 30, fill="black", width=2)
        else:
            if connection.get_connected():
                self.canvas.create_line(30, 30, 50, 30, fill="black", width=3)
            else:
                self.canvas.create_line(30, 40, 50, 30, fill="black", width=3)

        match connection.equipment_type:
            case ns.EquipmentType.LOAD:
                self.draw_load()
            case ns.EquipmentType.GENERATOR:
                self.draw_generator()
            case ns.EquipmentType.SHUNT_COMPENSATOR | ns.EquipmentType.STATIC_VAR_COMPENSATOR:
                self.draw_shunt()
            case ns.EquipmentType.LINE | ns.EquipmentType.DANGLING_LINE:
                self.canvas.create_line(50, 30, 500, 30, fill="black", width=2)
                self.draw_other_side_button()
            case ns.EquipmentType.SWITCH:
                self.draw_switch()
                self.draw_other_side_button()
            case ns.EquipmentType.TWO_WINDINGS_TRANSFORMER:
                self.draw_2wt()
                self.draw_other_side_button()
            case ns.EquipmentType.THREE_WINDINGS_TRANSFORMER:
                self.draw_3wt()
                other_sides = self.connection.network_structure.get_other_sides(self.connection)
                other_side1 = other_sides[0]
                other_side2 = other_sides[1]
                btn1 = tk.Button(self.canvas, text='>>', command=lambda: navigate_command(other_side1))
                self.canvas.create_window(510, 15, width=30, height=20, anchor=tk.W, window=btn1)
                btn2 = tk.Button(self.canvas, text='>>', command=lambda: navigate_command(other_side2))
                self.canvas.create_window(510, 40, width=30, height=20, anchor=tk.W, window=btn2)
            case ns.EquipmentType.LCC_CONVERTER_STATION | ns.EquipmentType.VSC_CONVERTER_STATION:
                self.draw_dc_converter()
                self.draw_other_side_button()
            case _:
                self.canvas.create_line(50, 30, 500, 30, fill="black", width=2)

        self.canvas.pack(side=tk.LEFT, pady=(0, 0), ipady=0)

        self._name_var = tk.StringVar(value=connection.name)
        self._name_label = pw.LabelValue(self, '', self._name_var)
        self._name_label.place(x=30, y=5)

        if connection.equipment_type != ns.EquipmentType.SWITCH:
            self._p = tk.StringVar(value=format_power(connection.get_p()))
            self._p_label = pw.LabelValue(self, '', self._p, 'MW')
            self._p_label.place(x=80, y=33)

            self._q = tk.StringVar(value=format_power(connection.get_q()))
            self._q_label = pw.LabelValue(self, '', self._q, 'Mvar')
            self._q_label.place(x=180, y=33)

    def draw_other_side_button(self):
        other_sides = self.connection.network_structure.get_other_sides(self.connection)
        if len(other_sides) == 1:
            other_side = other_sides[0]
            btn = tk.Button(self.canvas, text='>>', command=lambda: self.navigate_command(other_side))
            self.canvas.create_window(510, 30, width=30, height=20, anchor=tk.W, window=btn)

    def draw_dc_converter(self):
        self.canvas.create_line(50, 30, 300, 30, fill="black", width=2)
        self.canvas.create_rectangle(300, 15, 330, 45, width=2)
        self.canvas.create_line(300, 45, 330, 15, fill="black", width=2)
        # ac
        self.canvas.create_arc(304, 20, 309, 25, start=0, extent=180, width=2, style=tk.ARC)
        self.canvas.create_arc(309, 20, 314, 25, start=180, extent=180, width=2, style=tk.ARC)
        # dc
        self.canvas.create_line(318, 35, 325, 35, fill="black", width=2)
        self.canvas.create_line(318, 38, 325, 38, fill="black", width=2)
        self.canvas.create_line(330, 30, 500, 30, fill="black", width=2)

    def draw_3wt(self):
        self.canvas.create_line(50, 30, 300, 30, fill="black", width=2)
        self.canvas.create_oval(300, 20, 320, 40, width=2)
        self.canvas.create_oval(310, 15, 330, 35, width=2)
        self.canvas.create_oval(310, 25, 330, 45, width=2)
        self.canvas.create_line(330, 23, 500, 23, fill="black", width=2)
        self.canvas.create_line(330, 37, 500, 37, fill="black", width=2)

    def draw_2wt(self):
        self.canvas.create_line(50, 30, 300, 30, fill="black", width=2)
        self.canvas.create_oval(300, 20, 320, 40, width=2)
        self.canvas.create_oval(310, 20, 330, 40, width=2)
        self.canvas.create_line(330, 30, 500, 30, fill="black", width=2)

    def draw_switch(self):
        self.canvas.create_line(50, 30, 305, 30, fill="black", width=2)
        self.canvas.create_rectangle(305, 20, 325, 40, width=2)
        if self.connection.network_structure.is_open(self.connection):
            self.canvas.create_line(315, 25, 315, 35, fill="black", width=2)
        else:
            self.canvas.create_line(310, 30, 320, 30, fill="black", width=2)
        self.canvas.create_line(325, 30, 500, 30, fill="black", width=2)

    def draw_shunt(self):
        self.canvas.create_line(50, 30, 300, 30, fill="black", width=2)
        if self.connection.equipment_type == ns.EquipmentType.SHUNT_COMPENSATOR:
            sc_type = self.connection.network_structure.get_shunt_compensator_type(self.connection)
            if sc_type == ns.ShuntCompensatorType.CAPACITOR:
                self.canvas.create_line(300, 30, 310, 30, fill="black", width=2)
                self.canvas.create_line(310, 20, 310, 40, fill="black", width=2)
                self.canvas.create_line(320, 20, 320, 40, fill="black", width=2)
                self.canvas.create_line(320, 30, 330, 30, fill="black", width=2)
            else:
                for i in range(3):
                    self.canvas.create_arc(300 + 10 * i, 20, 300 + 10 * (i + 1), 40, start=0, extent=180,
                                           width=2, style=tk.ARC)
        elif self.connection.equipment_type == ns.EquipmentType.STATIC_VAR_COMPENSATOR:
            self.canvas.create_rectangle(300, 20, 330, 40, width=2)
            self.canvas.create_text(315, 30, text='SVC')
        self.canvas.create_line(330, 30, 350, 30, fill="black", width=2)
        # ground
        self.canvas.create_line(350, 20, 350, 40, fill="black", width=2)
        for i in range(6):
            self.canvas.create_line(350, 20 + i * 4, 350 + 6, 20 + i * 4 + 6, fill="black", width=1)

    def draw_generator(self):
        self.canvas.create_line(50, 30, 300, 30, fill="black", width=2)
        self.canvas.create_oval(300, 15, 330, 45, width=2)
        self.canvas.create_arc(305, 25, 315, 35, start=0, extent=180, width=1, style=tk.ARC)
        self.canvas.create_arc(315, 25, 325, 35, start=180, extent=180, width=1, style=tk.ARC)

    def draw_load(self):
        self.canvas.create_line(50, 30, 300, 30, fill="black", width=2)
        self.canvas.create_rectangle(300, 20, 330, 40, width=2)
        self.canvas.create_line(300, 20, 330, 40, fill="black", width=1)
        self.canvas.create_line(330, 20, 300, 40, fill="black", width=1)

    def highlight(self):
        # self.canvas.configure(background='light blue')
        self.canvas.configure(highlightthickness=2, highlightbackground='blue')


if __name__ == "__main__":
    root = tk.Tk()
    net = pn.create_micro_grid_be_network()
    structure = ns.NetworkStructure(net)
    sub = structure.get_substation('37e14a0f-5e34-4647-a062-8bfd9305fa9d')
    vl = structure.get_voltage_level('469df5f7-058f-4451-a998-57a48e8a56fe')
    bus = vl.get_buses(ns.BusView.BUS_BRANCH).loc['469df5f7-058f-4451-a998-57a48e8a56fe_0']
    Substation(root, sub).pack(anchor=tk.NW)
    VoltageLevel(root, vl).pack(anchor=tk.NW, padx=20)
    Bus(root, '469df5f7-058f-4451-a998-57a48e8a56fe_0', bus).pack(anchor=tk.NW, padx=40)
    cn = vl.get_connection('78736387-5f60-4832-b3fe-d50daf81b0a6')
    Connection(root, cn, lambda *args: None).pack(anchor=tk.NW, padx=60, pady=(0, 0), ipady=0)
    Connection(root, cn, lambda *args: None).pack(anchor=tk.NW, padx=60, pady=(0, 0), ipady=0)
    Connection(root, cn, lambda *args: None).pack(anchor=tk.NW, padx=60, pady=(0, 0), ipady=0)
    root.mainloop()
