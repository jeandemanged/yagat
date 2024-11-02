#
# Copyright (c) 2024, Damien Jeandemange (https://github.com/jeandemanged)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
#
import logging
import threading
import tkinter as tk
from tkinter import ttk
from typing import Dict, Union, Optional

import pypowsybl.network as pn

import yagat.networkstructure as ns
from yagat.app_context import AppContext


class TreeView(tk.Frame):
    def __init__(self, parent, context: AppContext, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.context = context

        self.search_var = tk.StringVar()
        self.search_var.trace_add(mode='write', callback=lambda _1, _2, _3: self.on_search())
        self.search = ttk.Entry(self, textvariable=self.search_var)
        self.search.pack(side=tk.TOP, fill=tk.X)

        # show='tree' => will not show header
        # selectmode='browse' => single item
        self.tree = ttk.Treeview(self, show='tree', selectmode='browse')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_parent = None
        self.nodes_mapping: Dict[Union['ns.Substation', 'ns.VoltageLevel'], str] = {}
        self.selection_mapping: Dict[str, str] = {}

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        context.add_network_changed_listener(self.on_network_changed)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.search_thread = None
        self.search_pending = False
        self.context.add_selection_changed_listener(self.on_selection_changed)

    def on_selection_changed(self, selection: tuple[Optional[str], Optional[str], Optional[ns.Connection]]):
        _, selection_id, _ = selection
        if not selection_id:
            return

        existing_selection = None
        tree_selection = [self.tree.item(item)["values"] for item in self.tree.selection()]
        if tree_selection and tree_selection[0] != '':
            existing_selection = tree_selection[0][1]
        if selection_id != existing_selection:
            node = self.selection_mapping[selection_id]
            self.tree.focus(node)
            self.tree.selection_set(node)
            self.tree.see(node)

    def on_search(self):
        if self.search_thread is not None:
            self.search_pending = True
            return
        to_reattach = []
        self.search_thread = threading.Thread(target=self.on_search_background, args=(to_reattach,))
        self.search_thread.start()

        def schedule_check(t):
            self.after(200, check_if_done, t)

        def check_if_done(t):
            if not t.is_alive():
                logging.info("Updating tree view...")
                self._detach_all()
                for item, parent, index in to_reattach:
                    self.tree.reattach(item, parent, index)
                logging.info("Done updating tree view")
                self.search_thread = None
                if self.search_pending:
                    self.search_pending = False
                    self.on_search()
            else:
                schedule_check(t)

        schedule_check(self.search_thread)

    def on_search_background(self, to_reattach):
        if not self.tree_parent:
            return
        to_search = self.search_var.get().lower()

        included_substations, included_voltage_levels = self._get_included(to_search)

        index = -1
        for substation in self.context.network_structure.substations:
            if substation in included_substations:
                index += 1
                to_reattach.append((self.nodes_mapping[substation], self.tree_parent, index))

        for voltage_level in self.context.network_structure.voltage_levels:
            if voltage_level in included_voltage_levels:
                voltage_level_node = self.nodes_mapping[voltage_level]
                parent_node = self.tree_parent
                if voltage_level.substation:
                    parent_node = self.nodes_mapping[voltage_level.substation]
                index += 1
                to_reattach.append((voltage_level_node, parent_node, index))

    def _get_included(self, to_search):
        logging.info(f'Searching {to_search}...')
        included_substations = set()
        for substation in self.context.network_structure.substations:
            if to_search in substation.substation_id.lower() or to_search in substation.name.lower():
                included_substations.add(substation)
        included_voltage_levels = set()
        for voltage_level in self.context.network_structure.voltage_levels:
            if to_search in voltage_level.voltage_level_id.lower() or to_search in voltage_level.name.lower():
                included_voltage_levels.add(voltage_level)
                if voltage_level.substation:
                    included_substations.add(voltage_level.substation)
        logging.info(
            f'Searching {to_search}: {len(included_substations)} substations, '
            f'{len(included_voltage_levels)} voltage levels')
        return included_substations, included_voltage_levels

    def _detach_all(self):
        for level_1_item in self.tree.get_children(self.tree_parent):
            for level_2_item in self.tree.get_children(level_1_item):
                self.tree.detach(level_2_item)
            self.tree.detach(level_1_item)

    def on_network_changed(self, network: pn.Network):
        self.tree.delete(*self.tree.get_children())
        self.tree_parent = None
        if not network:
            return
        self.tree_parent = self.tree.insert('', 'end', text=network.name, open=True)

        for substation in self.context.network_structure.substations:
            node = self.tree.insert(self.tree_parent, "end", text=f"{substation.name} ({substation.substation_id})",
                                    values=['substation', substation.substation_id], open=True)
            self.nodes_mapping[substation] = node
            self.selection_mapping[substation.substation_id] = node

        for voltage_level in self.context.network_structure.voltage_levels:
            parent_node = self.tree_parent
            if voltage_level.substation:
                parent_node = self.nodes_mapping[voltage_level.substation]
            node = self.tree.insert(parent_node, "end", text=f"{voltage_level.name} ({voltage_level.voltage_level_id})",
                                    values=['voltage_level', voltage_level.voltage_level_id])
            self.nodes_mapping[voltage_level] = node
            self.selection_mapping[voltage_level.voltage_level_id] = node

    def on_tree_select(self, event):
        tree = event.widget
        selection = [tree.item(item)["values"] for item in tree.selection()]
        if selection and selection[0] != '' and selection[0][1] != self.context.selection[1]:
            self.context.selection = (selection[0][0], selection[0][1], None)


if __name__ == "__main__":
    root = tk.Tk()
    ctx = AppContext(root)
    TreeView(root, ctx).pack(fill="both", expand=True)
    ctx.network = pn.create_ieee9()
    root.mainloop()
