#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import tkinter as tk
from tkinter import ttk

import pypowsybl.network as pn

from yagat.app_context import AppContext
from yagat.frames.impl.area_boundaries_list_view import AreaBoundariesListView
from yagat.frames.impl.area_list_view import AreaListView
from yagat.frames.impl.diagram_view_bus import DiagramViewBus
from yagat.frames.impl.buses_bus_view_list_view import BusesListView
from yagat.frames.impl.buses_bus_breaker_view_list_view import BusesBusBreakerViewListView
from yagat.frames.impl.generator_list_view import GeneratorListView
from yagat.frames.impl.load_list_view import LoadListView
from yagat.frames.impl.line_list_view import LineListView
from yagat.frames.impl.two_windings_transformer_list_view import TwoWindingsTransformerListView
from yagat.frames.impl.three_windings_transformer_list_view import ThreeWindingsTransformerListView
from yagat.frames.impl.dangling_line_list_view import DanglingLineListView
from yagat.frames.impl.shunt_compensator_list_view import ShuntCompensatorListView
from yagat.frames.impl.static_var_compensator_list_view import StaticVarCompensatorListView
from yagat.frames.impl.lcc_list_view import LccListView
from yagat.frames.impl.vsc_list_view import VscListView
from yagat.frames.impl.switch_list_view import SwitchListView
from yagat.frames.impl.tie_line_view import TieLineView
from yagat.frames.impl.hvdc_line_view import HvdcLineView
from yagat.networkstructure import BusView


class TabsView(tk.Frame):
    def __init__(self, parent, context: AppContext, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.context = context
        self.context.add_tab_group_changed_listener(self.on_tab_group_changed)
        self.tab_control = ttk.Notebook(self)
        self._all_tabs = []
        self.tab_control.bind('<<NotebookTabChanged>>', lambda _: self.on_tab_changed())

        self._add_tab(DiagramViewBus(self.tab_control, context, 'Bus/Breaker View', BusView.BUS_BREAKER), hide=False)
        self._add_tab(DiagramViewBus(self.tab_control, context, 'Bus View', BusView.BUS_BRANCH), hide=False)
        self._add_tab(BusesListView(self.tab_control, self.context))
        self._add_tab(BusesBusBreakerViewListView(self.tab_control, self.context))
        self._add_tab(GeneratorListView(self.tab_control, self.context))
        self._add_tab(LoadListView(self.tab_control, self.context))
        self._add_tab(LineListView(self.tab_control, self.context))
        self._add_tab(TwoWindingsTransformerListView(self.tab_control, self.context))
        self._add_tab(ThreeWindingsTransformerListView(self.tab_control, self.context))
        self._add_tab(DanglingLineListView(self.tab_control, self.context))
        self._add_tab(ShuntCompensatorListView(self.tab_control, self.context))
        self._add_tab(StaticVarCompensatorListView(self.tab_control, self.context))
        self._add_tab(LccListView(self.tab_control, self.context))
        self._add_tab(VscListView(self.tab_control, self.context))
        self._add_tab(SwitchListView(self.tab_control, self.context))
        self._add_tab(TieLineView(self.tab_control, self.context))
        self._add_tab(HvdcLineView(self.tab_control, self.context))
        self._add_tab(AreaListView(self.tab_control, self.context))
        self._add_tab(AreaBoundariesListView(self.tab_control, self.context))

        self.tab_control.pack(expand=True, fill=tk.BOTH)

    def _add_tab(self, tab, hide=True):
        self.tab_control.add(tab, text=tab.tab_name)
        if hide:
            self.tab_control.hide(tab)
        self._all_tabs.insert(0, tab)

    def on_tab_group_changed(self, tab_group: str) -> None:
        for t in self._all_tabs:
            if t.tab_group_name == tab_group:
                self.tab_control.select(t)
            else:
                self.tab_control.hide(t)

    def on_tab_changed(self):
        self.context.selected_tab = self.tab_control.tab(self.tab_control.select(), 'text')


if __name__ == "__main__":
    root = tk.Tk()
    ctx = AppContext(root)
    TabsView(root, ctx).pack(fill="both", expand=True)
    ctx.network = pn.create_ieee9()
    ctx.selection = ('substation', 'S1', None)
    root.mainloop()
